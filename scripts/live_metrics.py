"""Live metrics for the realistic harness (Worker Y11, 21/11/2026).

Wires the two headline instruments into live runs (Y3 gap audit H2/I8):
per-step think/act/wait/exec timing and per-click records, emitted as
timed JSONL next to the pass/fail record. Design frozen in
improvements/worker-y11-design.md (council C1/C2/C3 AMEND, redteam BLOCK
lifted by landing all 8 cheapest fixes in that doc before implementation).

Honesty rules baked into this module (read the design doc for the why):

- Scripted steps record think_s = null, think_source = "scripted". Never
  0.0. A scripted run has no model decisions; step wall time is machine
  act time, the floor under any agent run, not agent think time. H2 stays
  OPEN until an agent-driven run produces agent-source think rows.
- The click record is a SELECTOR-DELIVERY rate (pointer occlusion and
  intercept on selector-resolved clicks), not an agent grounding hit rate.
  Vision grounding error is not measured by this oracle; see calibration
  E2 for the vision hit rate. The summary says so in plain words.
- One writer: every row goes through jsonlutil.append_jsonl. TimingLogger
  and hit_rate.append_attempt/summarize are never called on the live
  path (TimingLogger.think_step would invent model calls; append_attempt
  rejects live selectors and summarize raises on the attempt collision).
- Fail-open: a metrics failure never fails a test. Construction failure
  degrades to disabled with one stderr line. First mid-run write failure
  disables further writes and counts dropped rows. Metrics warnings go to
  stderr only, prefixed "[metrics] ".
- No typed text, no file contents, no page titles in any row. Type
  actions log text length, never the text. Set-file actions log the
  basename, never the full path.

Schema version 1. Envelope on every row: schema, run, wall
(Asia/Ho_Chi_Minh, "%Y-%m-%d %H:%M:%S %Z"), elapsed_s (seconds from
LiveMetrics t0 via time.monotonic), event, test, attempt.
"""
import hashlib
import json
import os
import re
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from jsonlutil import append_jsonl, verify_jsonl  # noqa: E402
import hit_rate  # noqa: E402  (ISSUES and BACKENDS constants only)
from timing import SLOW_THINK_S, wall_text  # noqa: E402

SCHEMA = 1
SLOW_THINK_S = SLOW_THINK_S
MIN_ACTIONS_PER_CALL = 1.0
SMALL_TASK_BUDGET_S = 300.0
JS_SHARE_UNRELIABLE = 0.10

THINK_DISCLAIMER = (
    "think_s is null: the scripted DOM driver has no model decisions; "
    "step wall time is machine act time, the floor under any agent run, "
    "not agent think time.")
CLICKS_DISCLAIMER = (
    "Selector-delivery rate for DOM-selector clicks (pointer occlusion "
    "and intercept). Vision grounding error is not measured by this "
    "oracle; see calibration E2 for the vision hit rate.")
CLICKS_EXCLUDED_REASON = (
    "click_js calls .click() on the element directly and bypass hit "
    "testing, so they are counted here and excluded from hit rate.")
ACTION_DISCLOSURE = (
    "Click hit rate covers N pointer clicks only. It excludes M "
    "js-clicks and K eval-clicks and L type actions. It is not an "
    "overall action success rate.")

_SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
_RUN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
_CURRENT = object()

# One probe eval, run BEFORE the click, in the same eval that resolves
# the rect (C2 A2, redteam B4). There is no post-click elementFromPoint
# read: on navigation clicks it reads a different document, on
# destructive clicks it manufactures false misses. Top-level return is
# REQUIRED (Marionette /execute/sync runs the script as a function
# body; Y4d lesson). The selector arrives as arguments[0], captured
# outside the arrow IIFE because arrow functions have no arguments.
PROBE_JS = """
const sel = arguments[0];
return (() => {
  const el = document.querySelector(sel);
  if (!el) return {found: false};
  const r = el.getBoundingClientRect();
  const cx = r.x + r.width / 2;
  const cy = r.y + r.height / 2;
  const top = document.elementFromPoint(cx, cy);
  function domPath(node) {
    const parts = [];
    let n = node;
    while (n && n.nodeType === 1) {
      if (n.id) { parts.unshift('#' + n.id); break; }
      let idx = 1;
      let sib = n;
      while ((sib = sib.previousElementSibling)) {
        if (sib.tagName === n.tagName) idx++;
      }
      parts.unshift(n.tagName.toLowerCase() + ':nth-of-type(' + idx + ')');
      n = n.parentElement;
    }
    return parts.join('/');
  }
  function ident(node) {
    if (!node) return null;
    return {id: node.id || null, path: domPath(node),
            tag: node.tagName.toLowerCase()};
  }
  let relation = null;
  let clickableOnPath = false;
  if (top) {
    if (top === el) relation = 'exact';
    else if (el.contains(top)) {
      relation = 'contains';
      const CLICKABLE = ['a', 'button', 'input', 'select', 'textarea',
                         'label'];
      let n = top;
      while (n && n !== el) {
        const tag = n.tagName ? n.tagName.toLowerCase() : '';
        const role = (n.getAttribute && n.getAttribute('role') || '')
          .toLowerCase();
        if (CLICKABLE.indexOf(tag) >= 0
            || (n.hasAttribute && n.hasAttribute('onclick'))
            || role === 'button' || role === 'link') {
          clickableOnPath = true;
          break;
        }
        n = n.parentElement;
      }
    }
    else if (top.contains(el)) relation = 'ancestor';
    else relation = 'other';
  }
  const cs = getComputedStyle(el);
  return {
    found: true,
    rect: {x: r.x, y: r.y, w: r.width, h: r.height},
    point: {x: cx, y: cy},
    viewport: {w: window.innerWidth, h: window.innerHeight},
    intended: ident(el),
    top: ident(top),
    relation: relation,
    clickable_on_path: clickableOnPath,
    pointer_events_none: cs.pointerEvents === 'none'
  };
})()
"""


def slugify(text):
    """Lowercase dash-collapsing slug, max 63 chars (hit_rate._SAFE_ID)."""
    slug = re.sub(r"[^a-z0-9_-]+", "-", str(text).lower())
    slug = slug.strip("-")
    return slug[:63] or "el"


def make_run_id(env_value=None):
    """Run id, formed once per main() invocation.

    LIVE_RUN_ID env, when set and valid, is used verbatim. Otherwise
    YYYYMMDD-HHMMSS-<pid>-<6 hex> from wall clock Asia/Ho_Chi_Minh.
    """
    if env_value and _RUN_ID_RE.fullmatch(env_value):
        return env_value
    now = datetime.now()
    try:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
    except Exception:
        pass
    import secrets
    return (f"{now.strftime('%Y%m%d-%H%M%S')}-{os.getpid()}-"
            f"{secrets.token_hex(3)}")


def default_metrics_path(live_log):
    """Metrics path: the LIVE_LOG sibling with -metrics before .jsonl."""
    path = str(live_log)
    if path.endswith(".jsonl"):
        return path[:-len(".jsonl")] + "-metrics.jsonl"
    return path + "-metrics.jsonl"


def classify_probe(probe, click_error=None):
    """Map a pre-click probe plus the click outcome to hit/issue.

    Returns (hit, hit_basis, issue_group). The probe is authoritative
    for hit/miss; the click outcome only adds the unresponsive issue
    when the probe said hit but the driver failed. A probe miss with a
    succeeding click stays a miss: the driver clicking an element
    handle directly does not prove a pointer would have landed there.
    """
    if not isinstance(probe, dict) or not probe.get("found"):
        return False, "none", "unknown"
    rect = probe.get("rect") or {}
    if not rect.get("w") or not rect.get("h"):
        return False, "none", "coordinate_mapping"
    point = probe.get("point") or {}
    view = probe.get("viewport") or {}
    if ("x" in point and "y" in point and "w" in view and "h" in view
            and (point["x"] < 0 or point["y"] < 0
                 or point["x"] > view["w"] or point["y"] > view["h"])):
        return False, "none", "coordinate_mapping"
    relation = probe.get("relation")
    if probe.get("pointer_events_none") and relation != "exact":
        return False, "none", "wrong_target"
    if click_error is not None:
        if relation == "exact":
            return False, "none", "unresponsive"
        if relation == "contains" and not probe.get("clickable_on_path"):
            return False, "none", "unresponsive"
        if relation == "contains":
            return False, "none", "wrong_target"
        if relation == "ancestor":
            return False, "none", "wrong_target"
        if relation == "other":
            return False, "none", "occlusion"
        return False, "none", "unknown"
    if relation == "exact":
        return True, "exact", None
    if relation == "contains":
        if probe.get("clickable_on_path"):
            return False, "none", "wrong_target"
        return True, "contains", None
    if relation == "ancestor":
        return False, "none", "wrong_target"
    if relation == "other":
        return False, "none", "occlusion"
    return False, "none", "unknown"


class LiveMetrics:
    """Sole writer of one run's metrics JSONL file. Fail-open."""

    def __init__(self, path, run_id, *, clock=time.monotonic):
        self.path = Path(path)
        self.run_id = run_id
        self._clock = clock
        self.t0 = self._clock()
        self.disabled = False
        self.error = None
        self.dropped = 0
        self.test = None
        self.attempt = 1
        self.model_calls = 0
        self.actions_total = 0
        self._steps = []
        self._clicks = []
        self._types = []
        self._js_clicks = []
        self._eval_clicks = []
        self._slug_registry = {}
        self._click_n = 0
        self._type_n = 0
        self._run_wait_s = 0.0
        self._run_exec_s = 0.0
        self._step = None
        self.dom_to_js_retry = False
        self._step_failed_dom_click = False
        self.live_log = ""
        try:
            if self.path.parent:
                if not self.path.parent.exists():
                    self.path.parent.mkdir(parents=True, exist_ok=True)
                elif not self.path.parent.is_dir():
                    raise NotADirectoryError(
                        f"{self.path.parent} is not a directory")
            self._quarantine_torn_tail()
        except Exception as exc:
            self._disable(f"construction failed: {exc}")

    def _disable(self, reason):
        if not self.disabled:
            self.disabled = True
            self.error = reason
            print(f"[metrics] disabled: {reason}", file=sys.stderr)

    def _quarantine_torn_tail(self):
        """Move a torn trailing line aside; never repair it in place.

        A crash mid-write leaves a partial last line with no trailing
        newline. Appending a newline after it would preserve the corrupt
        line as its own bad line, and the file would fail verify_jsonl.
        Quarantine the bad tail instead, so the file stays parseable.
        """
        if not self.path.exists() or self.path.stat().st_size == 0:
            return
        data = self.path.read_bytes()
        if data.endswith(b"\n"):
            return
        cut = data.rfind(b"\n")
        good, torn = data[:cut + 1], data[cut + 1:]
        if not torn.strip():
            return
        try:
            json.loads(torn.decode("utf-8"))
            return
        except ValueError:
            pass
        torn_path = self.path.with_name(
            self.path.name + ".torn-" + self.run_id)
        torn_path.write_bytes(torn)
        self.path.write_bytes(good)
        print(f"[metrics] quarantined torn tail to {torn_path}",
              file=sys.stderr)

    def elapsed(self):
        return self._clock() - self.t0

    def _envelope(self, event, *, test=_CURRENT, attempt=_CURRENT):
        return {"schema": SCHEMA, "run": self.run_id,
                "wall": wall_text(), "elapsed_s": round(self.elapsed(), 3),
                "event": event,
                "test": self.test if test is _CURRENT else test,
                "attempt": self.attempt if attempt is _CURRENT else attempt}

    def _write(self, row):
        if self.disabled:
            self.dropped += 1
            return False
        try:
            append_jsonl(self.path, row)
            return True
        except Exception as exc:
            self.dropped += 1
            self._disable(f"write failed: {exc}")
            return False

    def _slug_for(self, source):
        """Slug with a per-run collision registry (6-hex sha1 suffix)."""
        base = slugify(source)
        owner = self._slug_registry.get(base)
        if owner is None:
            self._slug_registry[base] = source
            return base
        if owner == source:
            return base
        digest = hashlib.sha1(source.encode("utf-8")).hexdigest()[:6]
        suffixed = (base[:56] + "-" + digest)[:63]
        if suffixed in self._slug_registry:
            digest = hashlib.sha1(source.encode("utf-8")).hexdigest()[:12]
            suffixed = (base[:50] + "-" + digest)[:63]
        self._slug_registry[suffixed] = source
        return suffixed

    def _identity_slug(self, ident):
        """Element identity slug: id attribute, else DOM path."""
        if not isinstance(ident, dict):
            return None
        if ident.get("id"):
            return self._slug_for(ident["id"])
        if ident.get("path"):
            return self._slug_for(ident["path"])
        if ident.get("tag"):
            return self._slug_for(ident["tag"])
        return None

    def set_test(self, test_id):
        self.test = test_id
        self._click_n = 0
        self._type_n = 0

    def set_attempt(self, attempt):
        self.attempt = attempt

    def note_model_calls(self, count=1):
        try:
            count = int(count)
        except (TypeError, ValueError):
            return
        if count > 0:
            self.model_calls += count

    def note_wait(self, seconds):
        try:
            seconds = float(seconds)
        except (TypeError, ValueError):
            return
        if seconds <= 0:
            return
        self._run_wait_s += seconds
        if self._step is not None:
            self._step["wait_s"] += seconds

    def note_exec(self, seconds):
        try:
            seconds = float(seconds)
        except (TypeError, ValueError):
            return
        if seconds <= 0:
            return
        self._run_exec_s += seconds
        if self._step is not None:
            self._step["exec_s"] += seconds

    def begin_step(self, name, op):
        self._step = {"name": name, "op": op, "t0": self._clock(),
                      "wait_s": 0.0, "exec_s": 0.0, "actions": 0}
        self._step_failed_dom_click = False

    def note_action(self, kind, detail=None):
        if self.disabled:
            return
        row = self._envelope("action")
        row.update({"kind": kind,
                    "step": self._step["name"] if self._step else None,
                    "op": self._step["op"] if self._step else None,
                    "detail": detail or {}})
        if self._write(row):
            self.actions_total += 1
            if self._step is not None:
                self._step["actions"] += 1
            if kind == "click_js":
                self._js_clicks.append(
                    {"test": row["test"], "js": (detail or {}).get("js", "")})
                if self._step_failed_dom_click:
                    self.dom_to_js_retry = True
            elif kind == "eval" and (detail or {}).get("has_click"):
                self._eval_clicks.append(
                    {"test": row["test"],
                     "script_len": (detail or {}).get("script_len", 0)})
                if self._step_failed_dom_click:
                    self.dom_to_js_retry = True

    def record_click(self, selector, probe, error=None, probe_error=None):
        """One row per WD.click call, written after the click outcome."""
        self._click_n += 1
        eff_error = error or probe_error
        hit, basis, issue = classify_probe(probe, eff_error)
        intended = None
        actual = None
        intended_path = None
        actual_path = None
        point = None
        rect = None
        if isinstance(probe, dict) and probe.get("found"):
            intended = self._identity_slug(probe.get("intended"))
            actual = self._identity_slug(probe.get("top"))
            intended_path = (probe.get("intended") or {}).get("path")
            actual_path = (probe.get("top") or {}).get("path")
            point = probe.get("point")
            rect = probe.get("rect")
        row = self._envelope("click_attempt")
        row.update({"case_id": row["test"], "click_n": self._click_n,
                    "backend": "dom",
                    "intended_target": intended,
                    "selector": selector,
                    "point": point, "rect": rect,
                    "dom_path": intended_path,
                    "actual_target": actual,
                    "actual_dom_path": actual_path,
                    "hit": hit, "hit_basis": basis,
                    "issue_group": issue, "click_method": "dom",
                    "error": (eff_error[:300] if eff_error else None)})
        self._write(row)
        rec = {"test": row["test"], "hit": hit, "issue": issue,
               "backend": "dom"}
        self._clicks.append(rec)
        if not hit or eff_error:
            self._step_failed_dom_click = True
        return rec

    def record_type(self, selector, expected_text, readback, error=None):
        """One row per WD.type_text call; hit = read-back equals text."""
        self._type_n += 1
        if readback is None:
            hit = None
        else:
            hit = (readback == expected_text)
        row = self._envelope("type_attempt")
        row.update({"case_id": row["test"], "type_n": self._type_n,
                    "selector": selector,
                    "expected_len": len(expected_text) if expected_text else 0,
                    "readback_len": (len(readback)
                                     if readback is not None else None),
                    "hit": hit,
                    "error": (error[:300] if error else None)})
        self._write(row)
        self._types.append({"hit": hit})
        return {"hit": hit}

    def finish_step(self, ok, error=None, *, think_s=None,
                    think_source="scripted", extra=None):
        if self._step is None:
            return None
        step = self._step
        self._step = None
        act_s = self._clock() - step["t0"]
        total_s = (think_s or 0.0) + act_s
        slow = think_s is not None and think_s > SLOW_THINK_S
        row = self._envelope("step")
        row.update({"step": step["name"], "op": step["op"],
                    "think_s": (round(think_s, 3)
                                if think_s is not None else None),
                    "act_s": round(act_s, 3),
                    "wait_s": round(step["wait_s"], 3),
                    "exec_s": round(step["exec_s"], 3),
                    "total_s": round(total_s, 3),
                    "actions": step["actions"],
                    "slow_think": slow,
                    "think_source": think_source,
                    "ok": bool(ok),
                    "error": error})
        if extra:
            row.update(extra)
        self._write(row)
        self._steps.append(row)
        return row

    def _click_summary(self):
        attempts = len(self._clicks)
        hits = sum(1 for c in self._clicks if c["hit"])
        misses = attempts - hits
        by_backend = {}
        by_issue = {}
        for rec in self._clicks:
            backend = rec["backend"]
            slot = by_backend.setdefault(
                backend, {"attempts": 0, "hits": 0, "misses": 0})
            slot["attempts"] += 1
            if rec["hit"]:
                slot["hits"] += 1
            else:
                slot["misses"] += 1
                issue = rec["issue"] or "unknown"
                by_issue[issue] = by_issue.get(issue, 0) + 1
        return {"attempts": attempts, "hits": hits, "misses": misses,
                "hit_rate": (hits / attempts if attempts else None),
                "by_backend": by_backend,
                "misses_by_issue": dict(sorted(by_issue.items()))}

    def summary(self, tests_detail):
        """Exactly one summary row per LiveMetrics lifetime, written last.

        tests_detail: list of {test, pass} in run order. Per-test step
        and click counts are computed here from the in-memory rows.
        """
        think_vals = [s["think_s"] for s in self._steps
                      if s["think_s"] is not None]
        total_vals = [s["total_s"] for s in self._steps]
        clicks = self._click_summary()
        click_actions = clicks["attempts"] + len(self._js_clicks) \
            + len(self._eval_clicks)
        js_share = ((len(self._js_clicks) + len(self._eval_clicks))
                    / click_actions if click_actions else 0.0)
        unreliable = bool(js_share > JS_SHARE_UNRELIABLE
                          or self.dom_to_js_retry)
        if self.dom_to_js_retry:
            unreliable_reason = ("a step retried through JS after a "
                                 "failed DOM click")
        elif js_share > JS_SHARE_UNRELIABLE:
            unreliable_reason = (
                f"js+eval click share {js_share:.0%} exceeds "
                f"{JS_SHARE_UNRELIABLE:.0%}")
        else:
            unreliable_reason = None
        sources = {s["think_source"] for s in self._steps}
        think_source = ("scripted" if sources <= {"scripted"}
                        else "hand" if sources <= {"hand"} else "mixed")
        type_hits = sum(1 for t in self._types if t["hit"] is True)
        type_miss = sum(1 for t in self._types if t["hit"] is False)
        type_unk = sum(1 for t in self._types if t["hit"] is None)
        detail = []
        for item in tests_detail:
            tid = item["test"]
            tsteps = [s for s in self._steps if s["test"] == tid]
            tclicks = [c for c in self._clicks if c.get("test") == tid]
            thits = sum(1 for c in tclicks if c["hit"])
            detail.append({
                "test": tid, "pass": bool(item["pass"]),
                "steps": len(tsteps),
                "steps_ok": sum(1 for s in tsteps if s["ok"]),
                "total_s": round(sum(s["total_s"] for s in tsteps), 3),
                "over_small_task_budget": bool(
                    item.get("elapsed_s", 0) > SMALL_TASK_BUDGET_S
                    and len(tsteps) <= 6),
                "clicks_attempts": len(tclicks),
                "clicks_hits": thits,
                "hit_rate": (thits / len(tclicks) if tclicks else None),
                "js_clicks_excluded": sum(
                    1 for j in self._js_clicks if j["test"] == tid)})
        row = self._envelope("summary", test=None, attempt=None)
        row.update({
            "tests": [item["test"] for item in tests_detail],
            "tests_pass": sum(1 for item in tests_detail
                              if item["pass"]),
            "tests_fail": sum(1 for item in tests_detail
                              if not item["pass"]),
            "tests_total": len(tests_detail),
            "steps": len(self._steps),
            "steps_ok": sum(1 for s in self._steps if s["ok"]),
            "steps_fail": sum(1 for s in self._steps if not s["ok"]),
            "think_median_s": (round(statistics.median(think_vals), 3)
                               if think_vals else None),
            "think_max_s": (round(max(think_vals), 3)
                            if think_vals else None),
            "total_median_s": (round(statistics.median(total_vals), 3)
                               if total_vals else None),
            "total_max_s": (round(max(total_vals), 3)
                            if total_vals else None),
            "model_calls": self.model_calls,
            "actions": self.actions_total,
            "actions_per_call": (
                round(self.actions_total / self.model_calls, 3)
                if self.model_calls > 0 else None),
            "low_pace": ((self.actions_total / self.model_calls
                          < MIN_ACTIONS_PER_CALL)
                         if self.model_calls > 0 else None),
            "slow_steps": sum(1 for s in self._steps if s["slow_think"]),
            "slow_step_names": [s["step"] for s in self._steps
                                if s["slow_think"]],
            "slow_think": any(s["slow_think"] for s in self._steps),
            "clicks": clicks,
            "js_clicks_excluded": len(self._js_clicks),
            "js_clicks": self._js_clicks,
            "eval_clicks_excluded": len(self._eval_clicks),
            "eval_clicks": self._eval_clicks,
            "dom_to_js_retry": self.dom_to_js_retry,
            "unreliable": unreliable,
            "unreliable_reason": unreliable_reason,
            "type_attempts": {"attempts": len(self._types),
                              "hits": type_hits, "misses": type_miss,
                              "unknown": type_unk},
            "think_source": think_source,
            "think_disclaimer": THINK_DISCLAIMER,
            "clicks_disclaimer": CLICKS_DISCLAIMER,
            "clicks_excluded_reason": CLICKS_EXCLUDED_REASON,
            "action_disclosure": ACTION_DISCLOSURE,
            "metrics_dropped": self.dropped,
            "metrics_path": str(self.path),
            "live_log": self.live_log,
            "tests_detail": detail})
        self._write(row)
        try:
            fd = os.open(self.path, os.O_WRONLY | os.O_APPEND)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
        except Exception:
            pass
        return row


def verify_file(path):
    """Parse a metrics file; return the bad 1-based line numbers."""
    return verify_jsonl(path)
