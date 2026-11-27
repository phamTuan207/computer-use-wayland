#!/usr/bin/env python3
"""R10 seamless RDP client with tool-enforced tab scoping (RT-20, stdlib only).

Base: W4 production-shaped client (connect, listTabs, getTarget,
evaluateJSAsync, navigateTo, port-owner guard, fail-loud webdriver probe,
navigate-to-load polling, latency bench).

RT-20 additions (enforced IN the tool, not in briefs):
- Scope set at attach: allowed tab descriptor ids and/or URL glob patterns.
  evaluate/navigate/getTarget on an out-of-scope tab raises RDPError.
  No scope = legacy behavior, but a loud UNSCOPED warning is printed.
- Credential-tab denylist: URL patterns from --scope-config (JSON) or the
  generic defaults below (opt-in via --use-default-denylist; default off).
  A denylisted tab is refused even when in scope, unless an explicit
  approval (--allow-credential-tab + --approval-note) covers that tab id;
  approvals used are recorded in the drive report.
- Drive report (JSON): webdriver probe, tab list before/after with diff,
  scope used, denylist hits, scope refusals, approvals used, action counts.
  Written to --drive-report on session end, or on demand via `report`.

Runs on the laptop next to the browser. No geckodriver, no DevTools
frontend. ydotool is banned (not used here; this client sends no OS input).
Generic defaults only: no machine-specific values in this file. Real
patterns belong in a machine-layer config file passed via --scope-config.

Landed fixes (R10 landing integration):
- Tab-pinned re-attach: closing DevTools swaps the tab target and kills
  the held consoleActor once with noSuchActor (RT-06). evaluate/navigate
  catch that error, re-attach pinned to the same tab (canonical
  descriptor id, URL fallback, never selected-pick), and retry once.
- Fail-closed port-owner guard: an explicit profile marker is required
  before attach. The only escape is the test-only
  --allow-unmarked-test-attach flag, which warns loudly.
"""
import argparse
import fnmatch
import json
import re
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone

# Generic credential-tab URL fragments (opt-in; denylist is OFF unless a
# config file supplies patterns or --use-default-denylist is passed).
DEFAULT_CREDENTIAL_DENYLIST = [
    "login", "signin", "sign-in", "account", "auth", "oauth",
    "password", "checkout", "payment",
]

UNSCOPED_WARNING = (
    "WARNING: RDP session is UNSCOPED - no tab scope was given, so this "
    "session may act on ANY tab, including credential tabs. Pass "
    "--scope-tab-id / --scope-url-pattern (or a --scope-config) to "
    "restrict it. Unscoped mode is for throwaway/test use only."
)


def median(xs):
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def ms(sec):
    return round(sec * 1000, 1)


def _now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _url_matches(url, pattern):
    """Glob match if pattern has * or ?, else case-insensitive substring."""
    if not url:
        return False
    u, p = url.lower(), pattern.lower()
    if "*" in p or "?" in p:
        return fnmatch.fnmatchcase(u, p)
    return p in u


def _canon_tab_id(actor):
    """Canonical tab key: RDP descriptor actors are per-connection
    (server1.conn1.tabDescriptor2 vs server1.conn2.tabDescriptor2 for the
    same tab; verified live, L3 probe 27/11). Strip the connection prefix
    so scope/approval ids match across connections. URL patterns remain
    the robust cross-connection scope; ids are exact within a session."""
    if not actor:
        return actor
    m = re.match(r"^[^.]+\.conn\d+\.(tabDescriptor\d+)$", actor)
    return m.group(1) if m else actor


class RDPError(Exception):
    pass


class Scope:
    """Allowed tabs for one attached session.

    A tab is in scope when its descriptor id is listed OR its URL matches
    any URL glob pattern. An empty Scope means unscoped (legacy behavior).
    """

    def __init__(self, tab_ids=None, url_patterns=None):
        self.tab_ids = set(tab_ids or [])
        self.url_patterns = list(url_patterns or [])

    @property
    def scoped(self):
        return bool(self.tab_ids or self.url_patterns)

    def matches(self, tab_id, url):
        if not self.scoped:
            return True
        if tab_id is not None and _canon_tab_id(tab_id) in \
                {_canon_tab_id(t) for t in self.tab_ids}:
            return True
        return any(_url_matches(url, p) for p in self.url_patterns)

    def to_dict(self):
        return {"scoped": self.scoped, "tab_ids": sorted(self.tab_ids),
                "url_patterns": list(self.url_patterns)}


def load_scope_config(path):
    """Load a JSON scope config. Recognized keys (all optional):
    scope_tab_ids [str], scope_url_patterns [str],
    credential_denylist_patterns [str] (aliases: denylist_patterns,
    credential_denylist). Returns a normalized dict."""
    try:
        with open(path) as f:
            raw = json.load(f)
    except OSError as e:
        raise RDPError(f"cannot read scope config {path!r}: {e}")
    except json.JSONDecodeError as e:
        raise RDPError(f"scope config {path!r} is not valid JSON: {e}")
    if not isinstance(raw, dict):
        raise RDPError(f"scope config {path!r} must be a JSON object")
    deny = raw.get("credential_denylist_patterns")
    if deny is None:
        deny = raw.get("denylist_patterns", raw.get("credential_denylist"))
    return {
        "scope_tab_ids": list(raw.get("scope_tab_ids") or []),
        "scope_url_patterns": list(raw.get("scope_url_patterns") or []),
        "credential_denylist_patterns": list(deny) if deny else None,
    }


def _is_no_such_actor(text):
    """True when an RDP error text reports a dead actor (target swap)."""
    return "noSuchActor" in (text or "")


def check_port_owner(port, marker):
    """Refuse unless the process listening on `port` looks like the expected
    throwaway browser (cmdline contains `marker`). Returns (pid, cmdline).
    Fail-closed: an empty marker is refused, never skipped."""
    if not marker:
        raise RDPError(
            "profile marker is required (fail-closed): pass "
            "--profile-marker <substring> so the port owner can be "
            "verified before attach")
    try:
        out = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True,
                             timeout=10).stdout
    except Exception as e:
        raise RDPError(f"port-owner check failed to run ss: {e}")
    pid = None
    for line in out.splitlines():
        if re.search(rf":{port}\s", line):
            m = re.search(r"pid=(\d+)", line)
            if m:
                pid = int(m.group(1))
                break
    if pid is None:
        raise RDPError(
            f"port {port}: no listening pid found via ss -tlnp "
            f"(browser not running, or port owned by another process)")
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            cmd = f.read().replace(b"\0", b" ").decode(errors="replace")
    except OSError as e:
        raise RDPError(f"port {port}: cannot read cmdline of pid {pid}: {e}")
    if marker not in cmd:
        raise RDPError(
            f"port {port} is bound by pid {pid} whose cmdline does not contain "
            f"expected marker {marker!r}; refusing to attach. cmdline: {cmd[:300]}")
    return pid, cmd


def _tab_snapshot(tabs):
    return [{"actor": t.get("actor"), "tab_id": _canon_tab_id(t.get("actor")),
             "url": t.get("url", ""), "title": t.get("title", ""),
             "selected": bool(t.get("selected"))} for t in tabs]


def _tab_diff(before, after):
    b = {t.get("tab_id") or t["actor"]: t for t in before}
    a = {t.get("tab_id") or t["actor"]: t for t in after}
    added = [a[k] for k in a if k not in b]
    removed = [b[k] for k in b if k not in a]
    navigated = [{"tab_id": k, "from_url": b[k]["url"], "to_url": a[k]["url"]}
                 for k in a if k in b and a[k]["url"] != b[k]["url"]]
    return {"added": added, "removed": removed, "navigated": navigated}


class RDPClient:
    def __init__(self, port, host="127.0.0.1", timeout=15, scope=None,
                 denylist_patterns=None, credential_approvals=None,
                 drive_report_path=None, transport=None, warn_unscoped=True):
        self.port = port
        self.scope = scope if scope is not None else Scope()
        self.denylist_patterns = list(denylist_patterns or [])
        self.credential_approvals = dict(credential_approvals or {})
        self.drive_report_path = drive_report_path
        if warn_unscoped and not self.scope.scoped:
            print(UNSCOPED_WARNING, file=sys.stderr)
        if transport is not None:
            self.sock = transport
        else:
            self.sock = socket.create_connection((host, port), timeout=timeout)
        self.buf = b""
        self.greeting = self._recv()
        self.desc_actor = None
        self.target_actor = None
        self.console_actor = None
        self._tabs = []
        self._current_tab = None
        self._tabs_before = None
        self._probe_result = None
        self._pinned_tab_id = None
        self._pinned_url = ""
        self._retries = 0
        self._actions = {"evaluate": 0, "navigate": 0, "get_target": 0}
        self._denylist_hits = []
        self._scope_refusals = []
        self._approvals_used = []
        self._started_at = _now_iso()

    # -- scope / denylist guards -------------------------------------------
    def _guard(self, tab_id, url, op):
        """Raise RDPError when (tab_id, url) is out of scope or denylisted
        without approval. Records hits/refusals/approvals for the report."""
        if not self.scope.matches(tab_id, url):
            self._scope_refusals.append(
                {"op": op, "tab_id": tab_id, "url": url, "at": _now_iso()})
            raise RDPError(
                f"SCOPE REFUSED: {op} on tab {tab_id!r} url={url!r} is out "
                f"of scope (allowed tab ids: {sorted(self.scope.tab_ids)}, "
                f"url patterns: {self.scope.url_patterns})")
        if self.denylist_patterns:
            hit = next((p for p in self.denylist_patterns
                        if _url_matches(url, p)), None)
            if hit is not None:
                note = self._approval_note(tab_id)
                if note is not None:
                    self._approvals_used.append(
                        {"op": op, "tab_id": tab_id, "url": url,
                         "pattern": hit, "note": note, "at": _now_iso()})
                else:
                    self._denylist_hits.append(
                        {"op": op, "tab_id": tab_id, "url": url,
                         "pattern": hit, "at": _now_iso()})
                    raise RDPError(
                        f"CREDENTIAL TAB REFUSED: {op} on tab {tab_id!r} "
                        f"url={url!r} matches denylist pattern {hit!r}. "
                        f"Pass --allow-credential-tab {tab_id} together "
                        f"with --approval-note <text> to approve explicitly.")

    def _approval_note(self, tab_id):
        """Approval note for tab_id (canonical match), or None."""
        canon = _canon_tab_id(tab_id)
        for k, v in self.credential_approvals.items():
            if _canon_tab_id(k) == canon:
                return v
        return None

    def _guard_current(self, op):
        tab = self._current_tab or {}
        self._guard(self.desc_actor, tab.get("url", ""), op)

    # -- transport ----------------------------------------------------------
    def _fill(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise RDPError("RDP socket closed by server")
            self.buf += chunk

    def _recv(self):
        self._fill(1)
        colon = self.buf.find(b":")
        while colon == -1:
            self._fill(len(self.buf) + 1)
            colon = self.buf.find(b":")
        length = int(self.buf[:colon])
        self._fill(colon + 1 + length)
        raw = self.buf[colon + 1: colon + 1 + length]
        self.buf = self.buf[colon + 1 + length:]
        return json.loads(raw.decode())

    def _send(self, obj):
        data = json.dumps(obj).encode()
        self.sock.sendall(f"{len(data)}:".encode() + data)

    def request(self, obj, expect_from=None, timeout=15, expect_key=None):
        self.sock.settimeout(timeout)
        self._send(obj)
        while True:
            msg = self._recv()
            if expect_from is not None and msg.get("from") != expect_from:
                continue
            # Unsolicited root events (e.g. tabListChanged) also carry
            # from=root; require the response key when asked.
            if expect_key is not None and expect_key not in msg \
                    and not msg.get("error"):
                continue
            if msg.get("error"):
                raise RDPError(f"RDP error for {obj.get('type')}: {msg}")
            return msg

    # -- tabs / attach --------------------------------------------------------
    def list_tabs(self):
        """Read-only inventory; always allowed (needed to discover tabs).
        Acting on a tab (getTarget/evaluate/navigate) is what scope gates."""
        msg = self.request({"to": "root", "type": "listTabs"},
                           expect_from="root", expect_key="tabs")
        tabs = msg.get("tabs", [])
        if not tabs:
            raise RDPError(f"listTabs returned no tabs: {msg}")
        # Zen fresh profiles have 2 tabs; the VISIBLE one carries
        # selected=true (msg["selected"] is null on this build). Picking
        # index 0 attaches to a background tab (W4 smoke finding).
        sel = None
        for i, t in enumerate(tabs):
            if t.get("selected") is True:
                sel = i
                break
        if sel is None:
            s = msg.get("selected", 0)
            sel = s if isinstance(s, int) and 0 <= s < len(tabs) else 0
        self._tabs = tabs
        if self._tabs_before is None:
            self._tabs_before = _tab_snapshot(tabs)
        # Keep the current-tab pointer on the attached descriptor when one
        # is attached; otherwise track the selected tab.
        cur = next((t for t in tabs if t.get("actor") == self.desc_actor),
                   None)
        self._current_tab = cur if cur is not None else tabs[sel]
        if self.desc_actor is None:
            self.desc_actor = tabs[sel]["actor"]
        # Keep the pinned URL fresh (the pinned tab may have navigated).
        if self._pinned_tab_id:
            pinned = next(
                (t for t in tabs
                 if _canon_tab_id(t.get("actor")) == self._pinned_tab_id),
                None)
            if pinned is not None:
                self._pinned_url = pinned.get("url", "")
        return tabs, sel

    def refresh_target(self):
        """Re-list tabs and re-get the target (after navigation the
        windowGlobalTarget is replaced; the visible tab stays selected)."""
        self.list_tabs()
        self.get_target()
        return self

    def _find_tab(self, tab_actor=None, tab_url=None):
        if not self._tabs:
            self.list_tabs()
        for _ in range(2):
            if tab_actor is not None:
                canon = _canon_tab_id(tab_actor)
                tab = next((t for t in self._tabs
                            if t.get("actor") == tab_actor
                            or _canon_tab_id(t.get("actor")) == canon), None)
            else:
                tab = next((t for t in self._tabs
                            if tab_url in (t.get("url") or "")), None)
            if tab is not None:
                return tab
            self.list_tabs()
        return None

    def get_target(self, tab_actor=None, tab_url=None):
        if tab_actor is not None or tab_url is not None:
            tab = self._find_tab(tab_actor, tab_url)
            if tab is None:
                raise RDPError(
                    f"tab {tab_actor or tab_url!r} not found in tab list")
            self._guard(tab.get("actor"), tab.get("url", ""), "getTarget")
            self.desc_actor = tab.get("actor")
            self._current_tab = tab
        else:
            if not self.desc_actor:
                self.list_tabs()
            self._guard_current("getTarget")
        msg = self.request({"to": self.desc_actor, "type": "getTarget"},
                           expect_from=self.desc_actor)
        frame = msg.get("frame") or msg.get("target") or {}
        self.target_actor = frame.get("actor") or msg.get("actor")
        self.console_actor = frame.get("consoleActor")
        if not self.console_actor and self.target_actor:
            # Fallback: attach on the target and read consoleActor from reply.
            try:
                self._send({"to": self.target_actor, "type": "attach"})
                for _ in range(8):
                    m = self._recv()
                    if m.get("from") != self.target_actor:
                        continue
                    if m.get("consoleActor"):
                        self.console_actor = m["consoleActor"]
                        break
                    if m.get("error"):
                        break
            except Exception:
                pass
        if not self.console_actor:
            raise RDPError(f"getTarget gave no consoleActor: {str(msg)[:500]}")
        self._actions["get_target"] += 1
        # Pin this tab: a later target swap (DevTools close) kills the
        # consoleActor, and recovery must land back on THIS tab.
        self._pinned_tab_id = _canon_tab_id(self.desc_actor)
        self._pinned_url = (self._current_tab or {}).get("url", "")
        return frame

    def _reattach_pinned(self):
        """Re-attach to the SAME tab after a target swap (RT-06: closing
        DevTools kills the held consoleActor once with noSuchActor).
        Pinned by canonical tab id, URL fallback. Never falls back to
        the selected tab: selected-pick can land on the wrong tab."""
        pin_id, pin_url = self._pinned_tab_id, self._pinned_url
        if not pin_id and not pin_url:
            raise RDPError("no pinned tab to re-attach to")
        self.list_tabs()
        tab = None
        if pin_id:
            tab = next((t for t in self._tabs
                        if _canon_tab_id(t.get("actor")) == pin_id), None)
        if tab is None and pin_url:
            tab = next((t for t in self._tabs
                        if (t.get("url") or "") == pin_url), None)
        if tab is None:
            raise RDPError(
                f"pinned tab {pin_id!r} url={pin_url!r} not found after "
                f"target swap; refusing selected-tab fallback")
        self.get_target(tab_actor=tab.get("actor"))

    def attach(self, tab_actor=None, tab_url=None):
        """connect already done in __init__; listTabs + getTarget.
        With tab_actor/tab_url, attach to that specific tab (scope-gated).
        tab_url (substring) resolves robustly across connections."""
        self.list_tabs()
        self.get_target(tab_actor, tab_url)
        return self

    # -- evaluate / navigate --------------------------------------------------
    @staticmethod
    def _unwrap(grip):
        if isinstance(grip, dict) and "type" in grip:
            t = grip["type"]
            if t in ("boolean", "number", "string"):
                return grip.get("value")
            if t == "null":
                return None
            if t == "undefined":
                return None
            return grip
        return grip

    def evaluate(self, expr, timeout=20):
        if not self.console_actor:
            raise RDPError("evaluate before attach (no console actor)")
        self._guard_current("evaluate")
        try:
            return self._evaluate_once(expr, timeout)
        except RDPError as e:
            if not _is_no_such_actor(str(e)):
                raise
            # Target swap killed the held consoleActor (RT-06): re-attach
            # pinned to the same tab and retry the evaluate once.
            self._reattach_pinned()
            self._retries += 1
            return self._evaluate_once(expr, timeout)

    def _evaluate_once(self, expr, timeout=20):
        self.sock.settimeout(timeout)
        self._send({"to": self.console_actor, "type": "evaluateJSAsync",
                    "text": expr})
        while True:
            m = self._recv()
            if m.get("type") == "evaluationResult":
                if m.get("exception"):
                    raise RDPError(f"evaluate exception: {str(m)[:400]}")
                self._actions["evaluate"] += 1
                return self._unwrap(m.get("result"))
            if m.get("error"):
                raise RDPError(f"evaluate error: {str(m)[:400]}")

    def _navigate_send(self, url):
        """Send navigateTo via target actor, fallback descriptor actor."""
        last = None
        for actor in (self.target_actor, self.desc_actor):
            if not actor:
                continue
            try:
                self.request({"to": actor, "type": "navigateTo",
                              "url": url}, expect_from=actor)
                return
            except Exception as e:
                last = e
        raise RDPError(f"navigateTo failed for {url}: {last}")

    def navigate(self, url):
        """navigateTo via target actor, fallback to descriptor actor.
        Navigation may replace the windowGlobalTarget, so re-attach after.
        Scope-gated on the current tab; denylist-gated on both the current
        URL and the destination URL."""
        self._guard_current("navigate")
        # Destination check: navigating INTO a credential URL is refused
        # the same way (approval keyed by the tab being navigated).
        if self.denylist_patterns:
            hit = next((p for p in self.denylist_patterns
                        if _url_matches(url, p)), None)
            if hit is not None:
                note = self._approval_note(self.desc_actor)
                if note is not None:
                    self._approvals_used.append(
                        {"op": "navigate-destination",
                         "tab_id": self.desc_actor, "url": url,
                         "pattern": hit, "note": note, "at": _now_iso()})
                else:
                    self._denylist_hits.append(
                        {"op": "navigate-destination",
                         "tab_id": self.desc_actor, "url": url,
                         "pattern": hit, "at": _now_iso()})
                    raise RDPError(
                        f"CREDENTIAL TAB REFUSED: navigate destination "
                        f"{url!r} matches denylist pattern {hit!r}. Pass "
                        f"--allow-credential-tab {self.desc_actor} together "
                        f"with --approval-note <text> to approve explicitly.")
        try:
            self._navigate_send(url)
        except RDPError as e:
            if not _is_no_such_actor(str(e)):
                raise
            # Target swap killed the held actor (RT-06): re-attach
            # pinned to the same tab and retry the navigate once.
            self._reattach_pinned()
            self._retries += 1
            self._navigate_send(url)
        self._actions["navigate"] += 1
        time.sleep(0.05)
        try:
            self.list_tabs()
            self.get_target()
        except Exception:
            pass  # wait_load re-attaches as needed

    def wait_load(self, url_substr, timeout=30):
        deadline = time.monotonic() + timeout
        last_reattach = 0.0
        while time.monotonic() < deadline:
            try:
                v = self.evaluate(
                    "document.readyState + '|' + location.href", timeout=5)
            except Exception:
                v = None
            if isinstance(v, str) and v.startswith("complete|") \
                    and url_substr in v:
                return v
            # Stale target after navigation: refresh actors periodically.
            # Pinned re-attach when a tab is pinned (never selected-pick).
            if time.monotonic() - last_reattach > 1.0:
                last_reattach = time.monotonic()
                try:
                    if self._pinned_tab_id:
                        self._reattach_pinned()
                    else:
                        self.list_tabs()
                        self.get_target()
                except Exception:
                    pass
            time.sleep(0.05)
        raise RDPError(f"wait_load timeout for {url_substr!r}")

    def probe_webdriver(self):
        """Small evaluates (short grips). Raises RDPError unless native false."""
        wd = self.evaluate("navigator.webdriver")
        typ = self.evaluate("typeof navigator.webdriver")
        getter = self.evaluate(
            "Object.getOwnPropertyDescriptor("
            "Object.getPrototypeOf(navigator),'webdriver').get.toString()")
        doc_attr = self.evaluate(
            "document.documentElement ? "
            "String(document.documentElement.getAttribute('webdriver')) : 'none'")
        plugins = self.evaluate("navigator.plugins ? navigator.plugins.length : -1")
        globals_found = self.evaluate(
            "['cdc_adoQpoasnfa76pfcZLmcfl_Array','__webdriver_evaluate',"
            "'__driver_evaluate','__webdriver_script_fn']"
            ".filter(k => k in window).join(',')")
        probe = {
            "webdriver": wd, "webdriver_type": typ, "getter_tostring": getter,
            "doc_webdriver_attr": doc_attr, "plugins_length": plugins,
            "automation_globals": globals_found,
        }
        native = isinstance(getter, str) and getter.startswith(
            "function webdriver()")
        if wd is not False or typ != "boolean" or not native:
            self._probe_result = {**probe, "verdict": "NOT_CLEAN"}
            raise RDPError(
                f"webdriver probe NOT clean (fail-loud): {json.dumps(probe)}")
        probe["verdict"] = "CLEAN"
        self._probe_result = probe
        return probe

    # -- drive report ---------------------------------------------------------
    def drive_report(self):
        """Build the RT-20 drive report dict (probe, tab diff, scope,
        denylist hits, approvals, action counts). Best-effort: probe and
        final tab list failures are recorded, not raised."""
        try:
            self.list_tabs()
        except Exception:
            pass
        # The attached target may be stale after a keyboard navigation;
        # refresh before probing (best-effort; scope refusals are recorded
        # by the probe error below, not raised here).
        try:
            self.get_target()
        except Exception:
            pass
        tabs_after = _tab_snapshot(self._tabs)
        tabs_before = self._tabs_before or []
        probe = self._probe_result
        if probe is None:
            try:
                probe = self.probe_webdriver()
            except Exception as e:
                probe = self._probe_result or {"error": str(e)}
        return {
            "generated_at": _now_iso(),
            "session_started_at": self._started_at,
            "port": self.port,
            "scope": self.scope.to_dict(),
            "denylist": {"enabled": bool(self.denylist_patterns),
                         "patterns": list(self.denylist_patterns)},
            "probe": probe,
            "tabs_before": tabs_before,
            "tabs_after": tabs_after,
            "tab_diff": _tab_diff(tabs_before, tabs_after),
            "denylist_hits": list(self._denylist_hits),
            "scope_refusals": list(self._scope_refusals),
            "approvals_used": list(self._approvals_used),
            "approvals_configured": dict(self.credential_approvals),
            "actions": dict(self._actions),
            "retries": self._retries,
        }

    def write_drive_report(self, path=None):
        path = path or self.drive_report_path
        if not path:
            raise RDPError("no drive report path given")
        report = self.drive_report()
        with open(path, "w") as f:
            json.dump(report, f, indent=1)
        return report

    def close(self):
        if self.drive_report_path:
            try:
                self.write_drive_report()
            except Exception as e:
                print(f"WARNING: drive report write failed: {e}",
                      file=sys.stderr)
        try:
            self.sock.close()
        except Exception:
            pass


def bench(port, marker, local_url, real_url, runs, scope=None,
          denylist_patterns=None, credential_approvals=None,
          allow_unmarked_test_attach=False):
    if marker:
        check_port_owner(port, marker)
    elif not allow_unmarked_test_attach:
        raise RDPError(
            "profile marker is required (fail-closed): pass "
            "--profile-marker <substring> so the port owner can be "
            "verified before attach")
    kw = {"scope": scope, "denylist_patterns": denylist_patterns,
          "credential_approvals": credential_approvals}
    out = {"port": port, "runs": runs,
           "scoped": bool(scope and scope.scoped)}
    # attach-to-first-evaluate: fresh connection each run
    xs = []
    for _ in range(runs):
        t0 = time.monotonic()
        c = RDPClient(port, **kw)
        c.attach()
        v = c.evaluate("1+1")
        xs.append(time.monotonic() - t0)
        assert v == 2, f"1+1 gave {v!r}"
        c.close()
    out["attach_to_first_evaluate"] = {
        "median_ms": ms(median(xs)), "runs_ms": [ms(x) for x in xs]}
    # held connection for the rest
    c = RDPClient(port, **kw)
    c.attach()
    out["probe"] = c.probe_webdriver()
    xs = []
    for _ in range(max(runs, 20)):
        t0 = time.monotonic()
        c.evaluate("1+1")
        xs.append(time.monotonic() - t0)
    out["evaluate_trivial"] = {
        "median_ms": ms(median(xs)), "runs_ms": [ms(x) for x in xs]}
    xs = []
    for _ in range(max(runs, 20)):
        t0 = time.monotonic()
        c.evaluate("document.querySelectorAll('*').length")
        xs.append(time.monotonic() - t0)
    out["evaluate_dom_read"] = {
        "median_ms": ms(median(xs)), "runs_ms": [ms(x) for x in xs]}
    # navigate-to-load, local then real, alternating with about:blank
    for label, url, substr in (("navigate_local", local_url, "slice"),
                               ("navigate_real", real_url, "example")):
        xs = []
        for _ in range(runs):
            c.navigate("about:blank")
            c.wait_load("about:blank", timeout=15)
            t0 = time.monotonic()
            c.navigate(url)
            c.wait_load(substr, timeout=30)
            xs.append(time.monotonic() - t0)
        out[label] = {"url": url, "median_ms": ms(median(xs)),
                      "runs_ms": [ms(x) for x in xs]}
    c.close()
    return out


def _build_scope(args):
    """Merge --scope-config + CLI flags into (Scope, denylist, approvals)."""
    tab_ids, patterns, deny = [], [], None
    if args.scope_config:
        cfg = load_scope_config(args.scope_config)
        tab_ids += cfg["scope_tab_ids"]
        patterns += cfg["scope_url_patterns"]
        deny = cfg["credential_denylist_patterns"]
    tab_ids += list(args.scope_tab_id or [])
    patterns += list(args.scope_url_pattern or [])
    if args.use_default_denylist and not deny:
        deny = list(DEFAULT_CREDENTIAL_DENYLIST)
    approvals = {}
    if args.allow_credential_tab or args.approval_note:
        if not args.allow_credential_tab or not args.approval_note:
            raise RDPError(
                "--allow-credential-tab and --approval-note must be passed "
                "together (approval without a note is not an approval)")
        approvals = {t: args.approval_note for t in args.allow_credential_tab}
    return Scope(tab_ids, patterns), deny, approvals


def main():
    ap = argparse.ArgumentParser(
        description="RDP client with RT-20 tab scoping")
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--profile-marker", default=None,
                    help="substring required in the listening pid cmdline "
                         "(required for attach; fail-closed)")
    ap.add_argument("--allow-unmarked-test-attach", action="store_true",
                    help="TEST ONLY: skip the port-owner marker check "
                         "(throwaway/test use; never for a real session)")
    ap.add_argument("--scope-tab-id", action="append", default=[],
                    help="allowed tab descriptor id (repeatable)")
    ap.add_argument("--scope-url-pattern", action="append", default=[],
                    help="allowed URL glob pattern (repeatable)")
    ap.add_argument("--scope-config", default=None,
                    help="JSON file: scope_tab_ids, scope_url_patterns, "
                         "credential_denylist_patterns")
    ap.add_argument("--use-default-denylist", action="store_true",
                    help="enable the generic credential denylist patterns")
    ap.add_argument("--allow-credential-tab", action="append", default=[],
                    help="tab id approved past the denylist (repeatable; "
                         "requires --approval-note)")
    ap.add_argument("--approval-note", default=None,
                    help="reason recorded for credential-tab approvals")
    ap.add_argument("--drive-report", default=None,
                    help="write the JSON drive report to this path")
    ap.add_argument("--tab-id", default=None,
                    help="attach to this tab descriptor id (full actor or "
                         "canonical tabDescriptorN; default: selected tab)")
    ap.add_argument("--tab-url", default=None,
                    help="attach to the tab whose URL contains this "
                         "substring (robust across connections)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("probe")
    sub.add_parser("tabs")
    sub.add_parser("report")
    e = sub.add_parser("eval")
    e.add_argument("expr")
    n = sub.add_parser("navigate")
    n.add_argument("url")
    b = sub.add_parser("bench")
    b.add_argument("--local-url", required=True)
    b.add_argument("--real-url", default="https://example.com/")
    b.add_argument("--runs", type=int, default=12)
    args = ap.parse_args()
    try:
        scope, deny, approvals = _build_scope(args)
        if not scope.scoped:
            print(UNSCOPED_WARNING, file=sys.stderr)
        if not args.profile_marker and not args.allow_unmarked_test_attach:
            print("ERROR: profile marker is required (fail-closed): pass "
                  "--profile-marker <substring> so the port owner can be "
                  "verified before attach", file=sys.stderr)
            return 2
        if args.allow_unmarked_test_attach and not args.profile_marker:
            print("WARNING: TEST-ONLY unmarked attach: port-owner marker "
                  "check skipped. Never use this against a real session.",
                  file=sys.stderr)
        kw = {"scope": scope, "denylist_patterns": deny,
              "credential_approvals": approvals,
              "drive_report_path": args.drive_report,
              "warn_unscoped": False}  # main() already warned loudly
        if args.cmd == "bench":
            print(json.dumps(bench(args.port, args.profile_marker,
                                   args.local_url, args.real_url,
                                   args.runs, scope=scope,
                                   denylist_patterns=deny,
                                   credential_approvals=approvals,
                                   allow_unmarked_test_attach=
                                   args.allow_unmarked_test_attach), indent=1))
            return 0
        if args.profile_marker:
            pid, _ = check_port_owner(args.port, args.profile_marker)
            print(json.dumps({"port_owner_pid": pid}), file=sys.stderr)
        c = RDPClient(args.port, **kw)
        try:
            if args.cmd == "tabs":
                tabs, sel = c.list_tabs()
                print(json.dumps({"tabs": _tab_snapshot(tabs),
                                  "selected_index": sel}, indent=1))
                if args.drive_report:
                    c.write_drive_report()
                return 0
            c.attach(args.tab_id, args.tab_url)
            if args.cmd == "probe":
                print(json.dumps(c.probe_webdriver(), indent=1))
            elif args.cmd == "eval":
                print(json.dumps({"result": c.evaluate(args.expr)}, indent=1))
            elif args.cmd == "navigate":
                c.navigate(args.url)
                print(json.dumps({"navigated": args.url}))
            elif args.cmd == "report":
                report = c.drive_report()
                if args.drive_report:
                    with open(args.drive_report, "w") as f:
                        json.dump(report, f, indent=1)
                print(json.dumps(report, indent=1))
                c.drive_report_path = None  # already written; avoid rewrite
            return 0
        finally:
            c.close()
    except RDPError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"ERROR: unexpected {type(e).__name__}: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
