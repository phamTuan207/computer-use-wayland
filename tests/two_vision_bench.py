#!/usr/bin/env python3
"""2-vision benchmark script, batch 8 task 1. BUILD ONLY, no live run yet.

Implements the combined design from improvements/worker-coord-click2-log.md
("The combined design"): VISION 1 builds an inventory with a one-shot
bulk DOM harvest for both clone windows (one evaluate per window, returning
ref, role, name, rect, center, visibility, focused for every input +
button), formatted as numbered compact text (Mantis pattern). A plan-once
program then runs the send chain for both clones (click input, type,
Enter, per clone) with an HCU-style live guard, stop-at-first-failure,
exactly-once intents, and a V12 sent-bubble gate after each message.
Scoring is by OUTCOME (message in the thread DOM or not, M1), never by
point-in-box. Total: exactly 2 visions (VISION 1 inventory, VISION 2
outcome check); everything between them is cheap DOM reads, zero extra
observes.

VISION 1 here is a DOM harvest, NOT a screenshot (gap D5, stated
explicitly). The agent's two vision calls are: (1) read the numbered
inventory text to pick the two message inputs, (2) look at the two
threads once at the end to confirm both bubbles. The script itself
never reads a screenshot to locate anything.

SAFETY. This is an acceptance test. It runs live ONLY after the
improved method is approved and the coordinator says run. The script
refuses live mode unless BOTH --live and --confirm-live are given,
AND the gate is on the plan URLs, not the flag: any plan URL outside
the local fixture file refuses without both flags, so a custom --plan
cannot smuggle a live run past the gate. It never touches a real
thread in fixture mode (default). Dry-test it only against
tests/two_vision_fixture.html in headless Firefox.

Transport: Marionette (Selenium) only. Firefox 160 allows exactly one
active remote session per browser instance, so no BiDi session is
opened while the Marionette session is active (gap D1).

Every step prints one JSON line: wall clock (UTC) and elapsed seconds
from a monotonic clock. Run with the repo venv python.
"""

import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

FF = str(Path.home() / "workspace/tools/firefox/firefox")
GD = str(Path.home() / "workspace/tools/geckodriver")
FIXTURE = (Path(__file__).resolve().parent / "two_vision_fixture.html").as_uri()
FIXTURE_DIR = Path(__file__).resolve().parent.as_uri() + "/"
DEFAULT_WORKDIR = "/tmp/two_vision_bench"

# TODO (step-6 loop hygiene): prompt caching, diff-gated
# re-observation, downscale to token tier, context editing, low
# effort, adaptive waiting are unowned agent-harness concerns, not
# built here. TODO (D5): nothing open; VISION 1 is a DOM harvest,
# stated explicitly in the docstring above, never a screenshot.

# TODO (F5, bulk harvest): this script implements the one-shot bulk
# harvest as a single evaluate per window, which is the harvest the
# combined design needs. Still open: Brave CDP DOM.getBoxModel and
# Accessibility.getFullAXTree in scripts/cdp.mjs (Chromium path only).
# V11 (batch 12 task 2, BUILT): send_one arms a real
# MutationObserver before typing (OBSERVER_JS) and records the
# mutation delta per send; the fixture counter window.__inputEvents
# is kept alongside it.
# TODO (D1): no BiDi/Marionette handover protocol exists under the
# one-session constraint; sequencing for a live run that needs both
# protocols is unspecified.
HARVEST_JS = """
return (function(){
  // Unique, valid CSS selector for an element: '#id' when it has one,
  // else a full css path (tag:nth-of-type(k) segments up the tree).
  // The old form tag + '[' + i + ']' (for example 'input[0]') is NOT
  // a valid selector and crashed every downstream querySelector call.
  function cssPath(e) {
    const parts = [];
    let n = e;
    while (n && n.nodeType === 1) {
      if (n.id) { parts.unshift('#' + CSS.escape(n.id)); break; }
      let k = 1, sib = n;
      while ((sib = sib.previousElementSibling)) {
        if (sib.tagName === n.tagName) k++;
      }
      parts.unshift(n.tagName.toLowerCase() + ':nth-of-type(' + k + ')');
      n = n.parentElement;
    }
    return parts.join(' > ');
  }
  // Native controls plus ARIA controls: div[role=button], links with
  // role button, [role=textbox] without contenteditable. Plain links
  // and role-less divs are NOT inventoried (documented limit).
  const els = [...document.querySelectorAll(
    'input, textarea, button, [contenteditable="true"], '
    + '[role="button"], [role="textbox"]')];
  return els.map((e, i) => {
    const r = e.getBoundingClientRect();
    const cs = getComputedStyle(e);
    const tag = e.tagName.toLowerCase();
    const role = e.getAttribute('role') ||
      (tag === 'input' ? (e.type === 'button' || e.type === 'submit' ? 'button' : 'textbox') :
       tag === 'textarea' ? 'textbox' :
       tag === 'button' ? 'button' :
       e.isContentEditable ? 'textbox' : tag);
    const name = (e.getAttribute('aria-label') || e.placeholder ||
      (e.textContent || '').trim().slice(0, 40) || e.value || '');
    return {ref: cssPath(e),
            tag: tag, role: role, name: name,
            aria_label: e.getAttribute('aria-label') || '',
            placeholder: e.placeholder || '',
            x: r.x, y: r.y, w: r.width, h: r.height,
            cx: r.x + r.width / 2, cy: r.y + r.height / 2,
            visible: r.width > 0 && r.height > 0 &&
              cs.display !== 'none' && cs.visibility !== 'hidden',
            focused: document.activeElement === e};
  });
})()
"""

# One evaluate per step: V1 field value, V2 contenteditable innerText,
# V3 activeElement focus, V4 caret offset, V11 input-event flag,
# V5 elementFromPoint hit test, plus the live rect for the HCU guard.
# TODO (F5): V11 here reads the fixture counter window.__inputEvents.
# A production page needs a MutationObserver armed before typing.
VERIFY_JS = """
return (function(sel){
  const e = document.querySelector(sel);
  if (!e) return {found: false};
  const r = e.getBoundingClientRect();
  const x = r.left + r.width / 2, y = r.top + r.height / 2;
  const hit = document.elementFromPoint(x, y);
  return {found: true,
    value: ('value' in e) ? e.value : null,
    innerText: e.isContentEditable ? e.innerText : null,
    active: document.activeElement === e,
    caret: (typeof e.selectionStart === 'number') ? e.selectionStart : null,
    inputEvents: (typeof window.__inputEvents === 'number') ? window.__inputEvents : null,
    hit: !!hit && (e === hit || e.contains(hit)),
    rect: {x: r.x, y: r.y, w: r.width, h: r.height, cx: x, cy: y},
    visible: r.width > 0 && r.height > 0};
})(arguments[0])
"""

# V12 finish gate: the exact message text as a bubble in the thread DOM.
# Deliberately no __bubblePresent shortcut: the gate must honor the
# plan's thread selector, so a wrong selector fails loudly instead of
# passing through a fixture helper. bubble_selector comes from the
# plan window entry (default matches the fixture's .bubble and any
# [data-sender] element); a live Messenger plan overrides it.
# Known limit: the gate requires exact textContent === text, and the
# default bubble selector is fixture-shaped. A Messenger bubble's
# textContent may not equal the message exactly, so the default would
# fail closed live; a live plan MUST override bubble_selector.
GATE_JS = """
return (function(threadSel, bubbleSel, text){
  const t = document.querySelector(threadSel);
  if (!t) return false;
  return [...t.querySelectorAll(bubbleSel)]
    .some(b => b.textContent === text);
})(arguments[0], arguments[1], arguments[2])
"""

# textNew count (batch 12 task 2): how many bubbles in the thread
# carry exactly this text. The V12 gate is a textNew gate: it passes
# only when the count grows past the pre-Enter gate_baseline measured
# in send_one right before the Enter keypress, so a stale bubble from
# an earlier run cannot pass a new send (design doc section 4.2,
# Turbo textNew). before_count, the batch-start snapshot taken in
# main, is recorded evidence only and is NEVER consulted by the gate:
# a bubble arriving after batch start but before Enter is inside the
# baseline and cannot pass it. Returns -1 when the thread container
# is missing, so a wrong thread selector is distinguishable from
# zero bubbles; callers must not collapse -1 to 0 (fix pass: a -1
# collapsed to 0 let a recorded "sent" intent re-send).
COUNT_JS = """
return (function(threadSel, bubbleSel, text){
  const t = document.querySelector(threadSel);
  if (!t) return -1;
  let n = 0;
  for (const b of t.querySelectorAll(bubbleSel)) {
    if (b.textContent === text) n++;
  }
  return n;
})(arguments[0], arguments[1], arguments[2])
"""

# V11 MutationObserver flag (batch 12 task 2, BUILT; fix pass:
# thread-scoped, record-counted). A real observer armed before
# typing. It observes the thread container (childList, characterData,
# subtree) so the delta counts records appended to the thread, not
# page-wide noise: typing into a contenteditable input mutates the
# input, not the thread, and no longer moves the count. When the
# thread container is missing it falls back to document.body and
# records scope "body-fallback". The callback adds list.length, so
# the count is a mutation-record count, not a callback-batch count
# (one callback can carry many records). Armed once per page; later
# calls return the running count. The delta is recorded evidence
# only: it is entailed by gate success (a bubble append is a
# mutation) and can be true on gate failure (an incoming message),
# so it is NOT a pass criterion (runbook section 14.3).
OBSERVER_JS = """
return (function(threadSel){
  if (window.__v11Observer) {
    return {armed: true, count: window.__v11Mutations || 0,
            scope: window.__v11Scope || 'unknown'};
  }
  window.__v11Mutations = 0;
  const target = threadSel ? document.querySelector(threadSel) : null;
  const scopeEl = target || document.body;
  window.__v11Scope = target ? 'thread' : 'body-fallback';
  window.__v11Observer = new MutationObserver(function(list){
    window.__v11Mutations += list.length;
  });
  window.__v11Observer.observe(scopeEl, {
    childList: true, characterData: true, subtree: true});
  return {armed: true, count: 0, scope: window.__v11Scope};
})(arguments[0])
"""

# Frames census (batch 12 task 2, gap 10): HARVEST_JS evaluates in
# the top frame only, so an input or thread inside an iframe is
# invisible to it. List every iframe with its origin and whether
# its document is reachable from the top frame. A cross-origin frame
# reports accessible false; same-origin policy blocks any DOM read
# into it, so the live run must stop and record it if the message
# input or thread could live inside one.
FRAMES_JS = """
return [...document.querySelectorAll('iframe')].map(f => {
  let accessible = false;
  try { accessible = !!f.contentDocument; } catch (e) { accessible = false; }
  let origin = null;
  try { origin = new URL(f.src || '', location.href).origin; }
  catch (e) { origin = null; }
  return {src: f.src || '', origin: origin, accessible: accessible};
});
"""

# D3 ref-stability check (batch 12 task 2): re-resolve the harvested
# ref against the live DOM and compare tag, role and name with the
# harvested item. A ref whose element was renamed or replaced since
# the harvest fails fast here, before any click. Returns the current
# element plus up to 3 nearest visible textboxes, so the operator
# can see what the input became. The name derivation matches
# HARVEST_JS exactly (aria-label, else placeholder, else textContent
# slice, else value).
REF_CHECK_JS = """
return (function(sel){
  function cssPath(e) {
    const parts = [];
    let n = e;
    while (n && n.nodeType === 1) {
      if (n.id) { parts.unshift('#' + CSS.escape(n.id)); break; }
      let k = 1, sib = n;
      while ((sib = sib.previousElementSibling)) {
        if (sib.tagName === n.tagName) k++;
      }
      parts.unshift(n.tagName.toLowerCase() + ':nth-of-type(' + k + ')');
      n = n.parentElement;
    }
    return parts.join(' > ');
  }
  function nameOf(el) {
    return (el.getAttribute('aria-label') || el.placeholder ||
      (el.textContent || '').trim().slice(0, 40) || el.value || '');
  }
  function roleOf(el) {
    const tag = el.tagName.toLowerCase();
    return el.getAttribute('role') ||
      (tag === 'input' ? (el.type === 'button' || el.type === 'submit' ? 'button' : 'textbox') :
       tag === 'textarea' ? 'textbox' :
       tag === 'button' ? 'button' :
       el.isContentEditable ? 'textbox' : tag);
  }
  const e = document.querySelector(sel);
  const nearest = [...document.querySelectorAll(
    'input, textarea, [contenteditable="true"], [role="textbox"]')]
    .filter(x => { const r = x.getBoundingClientRect();
      return r.width > 0 && r.height > 0; })
    .slice(0, 3)
    .map(x => ({ref: cssPath(x), tag: x.tagName.toLowerCase(),
      name: nameOf(x), role: roleOf(x),
      aria_label: x.getAttribute('aria-label') || '',
      placeholder: x.placeholder || ''}));
  if (!e) return {found: false, nearest: nearest};
  const r = e.getBoundingClientRect();
  return {found: true, tag: e.tagName.toLowerCase(),
    role: roleOf(e), name: nameOf(e),
    aria_label: e.getAttribute('aria-label') || '',
    placeholder: e.placeholder || '',
    rect: {x: r.x, y: r.y, w: r.width, h: r.height},
    nearest: nearest};
})(arguments[0])
"""


def log(name, t0, **kw):
    rec = {"step": name, "wall": datetime.now(timezone.utc).isoformat(),
           "elapsed_s": round(time.monotonic() - t0, 4)}
    rec.update(kw)
    print(json.dumps(rec), flush=True)
    return rec


def port_open(port):
    import socket
    s = socket.socket()
    s.settimeout(0.5)
    try:
        s.connect(("127.0.0.1", port))
        return True
    except OSError:
        return False
    finally:
        s.close()


class Ledger:
    """Exactly-once send ledger (gap D4, mechanized here, needs review).

    TODO (D4): exactly-once needs review-round approval. What the
    mechanism honestly guarantees: within one session, a retry never
    re-sends a message the V12 pre-check can see in the thread. It
    does NOT guarantee it when the thread/bubble selectors cannot see
    the bubble: after a v12-timeout the intent is marked
    failed-unverified and a later run with the same intent REFUSES to
    re-send it, because the message may have landed unseen. To retry,
    fix the selectors and use a new run_id after manually checking
    the thread.

    Run registry (fix pass, redteam F3): a run_id is bound to the
    ledger path of its first run in a shared registry outside the
    workdir (~/.cache/two_vision_bench/run_registry.json). A later
    run with the same run_id but a different ledger path (fresh
    workdir, empty ledger) is refused before the browser starts:
    its pre-check is blind and it would re-send. Same ledger path
    is a same-workdir retry, allowed; the outcome rule still
    requires fresh sends this run for PASS unless --allow-resume.
    Harvest mode never touches the registry (fix pass 2, redteam
    round 2 finding 1): a harvest sends nothing, so binding the
    run_id there would make the rung 2 step-2 run in its own
    workdir REFUSED; the registry binds only in run mode.

    Pre-send reservation (batch 12 task 2, BUILT): send_one writes
    the intent as "sending" after the V1 readback passes and before
    the Enter keypress, then reconciles it to "sent" or
    "failed-unverified" after the V12 gate. A later run that finds
    status "sending" refuses to re-send (retry-blocked-reservation):
    the process died between Enter and the ledger mark, the message
    may have landed, and only a hand check of the thread can tell.
    This closes the process-death gap only when the same ledger is
    reused (same workdir or --ledger); a fresh workdir has an empty
    ledger, so the run registry above refuses that case outright and
    the run_id freshness check in the runbook still stands as the
    human backstop.

    Intent binding (fix pass 2, redteam round 2 findings 2 and 3):
    every mark records the message text, thread URL, thread
    selector and bubble selector it was written for. A later run
    whose plan disagrees with the recorded intent (different text,
    URL or selectors) refuses with retry-blocked-intent-changed
    instead of sending a different message under the same intent.
    A recorded "sent" intent whose bubble is absent (count 0)
    refuses with retry-blocked-sent-bubble-absent instead of
    re-sending: the bubble may be unloaded rather than genuinely
    absent, and a fresh page load empties the fixture thread, so
    the old "re-send once, by design" behavior is gone. To send
    again after a genuine loss, use a new run_id after manually
    checking the thread. Records written before binding existed
    carry no message field and skip the binding check.

    Status state machine (fix pass 2): "sent" is terminal and is
    never overwritten by any later mark; "sending" reconciles only
    to "sent", "failed-unverified" or "failed"; "failed-unverified"
    is never overwritten by a plain "failed"; "failed" is the only
    retryable terminal status (a new run may reserve it again).
    mark() returns False when a transition is refused, True when
    applied, and merges new fields into the existing record instead
    of replacing it, so a reconciliation never loses the bound
    message, URL and selectors.

    A JSON file keyed by intent id (run_id + window label). An intent
    is marked sent only after its V12 gate passed. Before any send the
    chain runs the V12 pre-check first: a recorded intent whose bubble
    is present is skipped, never re-sent; a failed gate whose message
    actually landed is also caught by the same pre-check, so a retry
    cannot double-send. Since batch 12 task 2 the pre-check skips
    only when the ledger says this intent was already sent (status
    "sent") and the bubble is visible: a stale bubble with no ledger
    record does NOT skip, the send proceeds and the textNew gate
    requires a NEW bubble (count past the pre-Enter gate_baseline),
    so a stale bubble from an earlier run cannot pass a new send.

    Ledger writes are locked (fcntl flock on <path>.lock) and the
    file is re-read inside the lock, so two processes sharing one
    ledger file cannot lose each other's marks (redteam F12).
    """

    def __init__(self, path):
        self.path = path
        parent = os.path.dirname(os.path.abspath(path))
        os.makedirs(parent, exist_ok=True)
        self.data = {"intents": {}}
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    self.data = json.load(f)
            except json.JSONDecodeError as exc:
                # A corrupt ledger cannot be trusted: fail loudly
                # instead of treating every intent as unsent and
                # re-sending (fix pass 2, council 1 finding 10a).
                raise ValueError(
                    f"corrupt ledger file {path}: {exc}; fix or "
                    "remove it by hand after checking the threads, "
                    "never delete it blindly") from exc

    def _load(self):
        """Re-read the ledger file from disk. mark() writes with
        os.replace, so a plain read always sees a whole record;
        status() must not trust the in-memory copy loaded at
        __init__ time, or two processes sharing one ledger both
        see None and both send (fix pass 2, redteam round 2
        finding 15)."""
        if os.path.exists(self.path):
            with open(self.path, encoding="utf-8") as f:
                self.data = json.load(f)
        return self.data

    def status(self, intent_id):
        self._load()
        return self.data["intents"].get(intent_id, {}).get("status")

    def record(self, intent_id):
        """Full stored record for one intent ({} when absent)."""
        self._load()
        return dict(self.data["intents"].get(intent_id, {}))

    # Allowed status transitions (fix pass 2 state machine):
    # "sent" is terminal, never overwritten; "sending" reconciles
    # only to "sent", "failed-unverified" or "failed";
    # "failed-unverified" never becomes a plain "failed"; "failed"
    # is the only retryable status.
    _ALLOWED = {
        None: ("sending", "sent", "failed-unverified", "failed"),
        "failed": ("sending", "sent", "failed-unverified", "failed"),
        "sending": ("sent", "failed-unverified", "failed"),
        "failed-unverified": ("failed-unverified",),
        "sent": ("sent",),
    }

    def mark(self, intent_id, status, **kw):
        import fcntl
        lock_path = self.path + ".lock"
        with open(lock_path, "w", encoding="utf-8") as lock_f:
            fcntl.flock(lock_f, fcntl.LOCK_EX)
            try:
                # Re-read inside the lock: another process may have
                # written since this object loaded the file.
                if os.path.exists(self.path):
                    with open(self.path, encoding="utf-8") as f:
                        self.data = json.load(f)
                current = self.data["intents"].get(
                    intent_id, {}).get("status")
                if status not in self._ALLOWED.get(current, ()):
                    # Refused transition (e.g. a gate-failure mark
                    # trying to overwrite a "sent" record): keep
                    # the protective record and report the refusal.
                    return False
                # Merge into the existing record: a reconciliation
                # must never lose the bound message, URL and
                # selectors written by the reservation.
                rec = dict(self.data["intents"].get(intent_id, {}))
                rec["status"] = status
                rec["wall"] = datetime.now(timezone.utc).isoformat()
                rec.update(kw)
                self.data["intents"][intent_id] = rec
                tmp_path = self.path + ".tmp"
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, indent=2, sort_keys=True)
                os.replace(tmp_path, self.path)
                return True
            finally:
                fcntl.flock(lock_f, fcntl.LOCK_UN)

    def reserve(self, intent_id, **kw):
        """Atomic check-and-reserve under one lock: mark "sending"
        only when the intent is fresh (None) or retryable
        ("failed"). Returns True when the reservation was written,
        False when another process or a previous run already holds
        the intent. send_one must call this instead of a separate
        status check plus mark, or two processes can both see None
        and both send (fix pass 2, redteam round 2 finding 15)."""
        return self.mark(intent_id, "sending", **kw)


def format_inventory(label, items, frames=None):
    """Numbered compact text (Mantis pattern) for the agent's VISION 1.

    D3 (batch 12 task 2, ref check BUILT): refs are derived from the
    live DOM of this run only (id when present, else tag index); they
    must not transfer between runs or vendors. send_one re-resolves
    the ref before input and fails fast with ref-stale when the
    element's tag, role, name, aria-label or placeholder changed
    since this harvest (aria-label and placeholder are compared
    separately, not only through the derived name).
    """
    lines = [f"Window {label}: {len(items)} inputs+buttons"]
    for i, it in enumerate(items, 1):
        lines.append(
            f"[{i}] {it['role']} {it['name']!r} ref={it['ref']} "
            f"rect=({it['x']:.0f},{it['y']:.0f},{it['w']:.0f}x{it['h']:.0f}) "
            f"center=({it['cx']:.0f},{it['cy']:.0f}) "
            f"visible={it['visible']} focused={it['focused']}")
    if frames is not None:
        lines.append(
            f"Frames in {label}: {len(frames)} " +
            ", ".join(
                f"{f['src'] or '(no src)'} origin={f['origin']} "
                f"accessible={f['accessible']}" for f in frames))
    return "\n".join(lines)


def find_input(items, name_hint="Message"):
    """Pick the message input from a harvest: a visible textbox whose
    name matches the hint, else the first visible textbox."""
    boxes = [it for it in items
             if it["role"] == "textbox" and it["visible"]]
    for it in boxes:
        if name_hint.lower() in it["name"].lower():
            return it
    return boxes[0] if boxes else None


def launch_browser(profile, bidi_port=9223):
    """Launch headless Firefox by hand with Marionette + BiDi port flags,
    the same shape as the batch 7 task 2 bench. Returns the Popen proc.
    The BiDi port is opened by the flag only; no BiDi session is ever
    created while the Marionette session is active (one-session rule).
    Refuses when the ports are already held: the old check only waited
    for the ports to answer, so a stale browser holding them would get
    attached to instead of the process just launched."""
    os.makedirs(profile, exist_ok=True)
    if port_open(2828) or port_open(bidi_port):
        raise RuntimeError(
            "Marionette/BiDi ports already in use; a stale browser "
            "may be running. Kill it first, do not attach to it.")
    t0 = time.monotonic()
    proc = subprocess.Popen(
        [FF, "-headless", "-marionette",
         f"--remote-debugging-port={bidi_port}",
         "-profile", profile, "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.time() + 30
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(
                f"browser exited early with code {proc.returncode}")
        if port_open(2828) and port_open(bidi_port):
            break
        time.sleep(0.25)
    if not (port_open(2828) and port_open(bidi_port)):
        proc.kill()
        raise RuntimeError("browser ports did not open in 30 s")
    log("browser_launch_manual", t0, pid=proc.pid)
    return proc


def attach_driver():
    from selenium import webdriver
    from selenium.webdriver.firefox.service import Service
    # Create the Selenium session AFTER the browser is up: creating it
    # first and polling after can fail the attach when Marionette is
    # not yet ready. Retry a few times; a not-yet-ready Marionette
    # raises instead of answering.
    last_exc = None
    for attempt in range(3):
        try:
            service = Service(
                GD, log_output="/tmp/two_vision_geckodriver.log",
                service_args=["--connect-existing",
                              "--marionette-port", "2828"])
            t0 = time.monotonic()
            driver = webdriver.Firefox(service=service)
            break
        except Exception as exc:  # noqa: BLE001 - retry, then raise
            last_exc = exc
            time.sleep(1)
    else:
        raise last_exc
    # Readiness poll: the Marionette port can answer before the
    # session is fully usable; wait until a trivial eval succeeds.
    deadline = time.monotonic() + 15
    while True:
        try:
            driver.execute_script("return 1")
            break
        except Exception:
            if time.monotonic() > deadline:
                raise
            time.sleep(0.5)
    driver.set_window_size(1280, 900)
    log("marionette_attach_session", t0)
    return driver


def click_at(driver, cx, cy):
    """One real pointer click at viewport coordinates, W3C actions."""
    from selenium.webdriver.common.actions.action_builder import ActionBuilder
    from selenium.webdriver.common.actions.pointer_input import PointerInput
    from selenium.webdriver.common.actions import interaction
    pointer = PointerInput(interaction.POINTER_MOUSE, "mouse")
    builder = ActionBuilder(driver, mouse=pointer)
    pointer.create_pointer_move(x=int(cx), y=int(cy))
    pointer.create_pointer_down(button=0)
    pointer.create_pointer_up(button=0)
    builder.perform()


def ensure_visible(driver, ref):
    """Scroll the target into view when its center is below the fold,
    then re-read only its rect (one cheap call, not a full snapshot).
    Returns {cx, cy, scrolled} or None when the ref resolves to
    nothing. The scrolled flag tells the caller whether the live rect
    legitimately moved from the harvest snapshot: after a scroll the
    HCU guard must compare against post-scroll geometry, otherwise
    against the harvested center (fix pass, redteam F7)."""
    vh = driver.execute_script("return window.innerHeight")
    r = driver.execute_script(
        "const e=document.querySelector(arguments[0]);"
        " if(!e) return null; const b=e.getBoundingClientRect();"
        " return {cx: b.x+b.width/2, cy: b.y+b.height/2};", ref)
    if r is None:
        return None
    scrolled = False
    if r["cy"] < 0 or r["cy"] > vh:
        driver.execute_script(
            "document.querySelector(arguments[0])"
            ".scrollIntoView({block:'center'});", ref)
        r = driver.execute_script(
            "const e=document.querySelector(arguments[0]);"
            " if(!e) return null; const b=e.getBoundingClientRect();"
            " return {cx: b.x+b.width/2, cy: b.y+b.height/2};", ref)
        if r is None:
            return None
        scrolled = True
    return {"cx": r["cx"], "cy": r["cy"], "scrolled": scrolled}


def hcu_guard(driver, item, t0, expect=None):
    """HCU-style live guard. Re-checks the target's live geometry +
    visibility + hit test right before input. Returns (ok, reason,
    verify_evidence). Geometry moved more than 2 px from the expected
    center fails the guard: the inventory is stale.

    TODO (D2): no production component owns the guard yet; it lives
    here, in this script only.

    expect is the center to compare against: the VISION 1 snapshot
    center by default, or the fresh center from ensure_visible when
    the page was just scrolled (a scroll legitimately moves every
    rect, so the guard must compare against post-scroll geometry,
    not the stale snapshot). The call site must pass the harvested
    center when nothing scrolled: passing the fresh center always
    made the 2 px check vacuous, comparing the live rect against
    itself milliseconds later (fix pass, redteam F7)."""
    v = driver.execute_script(VERIFY_JS, item["ref"])
    if not v.get("found"):
        return False, "target-gone", v
    if not v.get("visible"):
        return False, "not-visible", v
    if not v.get("hit"):
        return False, "covered", v
    ex, ey = expect if expect is not None else (item["cx"], item["cy"])
    dx = abs(v["rect"]["cx"] - ex)
    dy = abs(v["rect"]["cy"] - ey)
    if dx > 2 or dy > 2:
        return False, f"geometry-moved dx={dx:.1f} dy={dy:.1f}", v
    return True, None, v


def send_one(driver, window, item, message, intent_id, ledger,
             plan, t_start, step_no, before_count=0):
    """One guarded send: click, type, Enter, V12 gate. Returns a step
    record. On any failure the caller stops the chain (Anthropic batch
    loop contract: stop at first failure, rest not-executed).

    textNew (batch 12 task 2): the V12 gate is a count gate, not a
    presence gate. before_count is the number of bubbles carrying
    this exact text in the thread when the run started (snapshot in
    main, before any send); it is recorded evidence only and the
    gate NEVER consults it. The gate passes only when the count
    grows to exactly gate_baseline + 1, where gate_baseline is
    measured right before Enter, so a stale bubble from an earlier
    run cannot pass a new send, and a double append (count jumping
    past baseline + 1) fails as duplicate-bubble instead of passing
    silently. The gate is appearance-based, not causal: it proves a
    bubble with this exact text appeared after the baseline, not
    that our Enter caused it (an echo or incoming message with
    identical text would pass it; mitigation is unique message text
    plus a free live lane, see the runbook). The pre-check skips
    only when the ledger says this intent was already sent and the
    bubble is visible; a stale bubble with no ledger record does NOT
    skip, the send proceeds and the gate requires a NEW bubble.
    """
    t0 = time.monotonic()
    step = {"step": step_no, "window": window["label"],
            "intent_id": intent_id, "status": "failed",
            "elapsed_s": 0.0, "before_count": before_count}
    thread_sel = window.get("thread_selector", "#thread")
    bubble_sel = window.get("bubble_selector", ".bubble, [data-sender]")
    v12_timeout = plan.get("timeouts", {}).get("v12_gate_s", 5)

    def bubble_count():
        """COUNT_JS, with -1 preserved: -1 means the thread
        container is missing, and it must stay distinguishable from
        0 (fix pass, council 1 issue 2: collapsing -1 to 0 let a
        recorded "sent" intent re-send through a broken thread
        selector). Callers fail fast on -1 (thread-missing) instead
        of typing; the gate times out loudly on it instead of
        passing. None (JS returned nothing) reads as -1."""
        n = driver.execute_script(
            COUNT_JS, thread_sel, bubble_sel, message)
        return n if isinstance(n, int) else -1

    # Exactly-once pre-check (D4): before any send, count the bubbles
    # already carrying this text. A previous attempt ended in a
    # v12-timeout: the message may have landed unseen (wrong
    # thread/bubble selectors make the pre-check blind), so this
    # intent is never re-attempted with the same selectors. Fix the
    # selectors and use a new run_id after manually checking the
    # thread. The pre-check above runs first so a fixed selector that
    # CAN see the bubble still skips correctly.
    count_now = bubble_count()
    step["count_at_precheck"] = count_now
    # A missing thread container (-1) is a blocking error, not a
    # zero count: with a broken thread selector the script can no
    # longer tell "thread missing" from "bubble genuinely absent",
    # so it must not type or press Enter (fix pass, council 1
    # issue 2). This runs before the ledger blocks below.
    if count_now < 0:
        step["error"] = "thread-missing"
        step["elapsed_s"] = round(time.monotonic() - t0, 4)
        log("thread_missing", t0, window=window["label"],
            intent_id=intent_id, thread_selector=thread_sel,
            note="thread container matched nothing; refusing to "
            "type, fix the thread selector")
        return step
    if ledger.status(intent_id) == "failed-unverified":
        step["error"] = "retry-blocked-unverified"
        step["elapsed_s"] = round(time.monotonic() - t0, 4)
        log("send_retry_blocked", t0, window=window["label"],
            intent_id=intent_id,
            note="previous v12-timeout; message may have landed unseen")
        return step
    # A previous attempt left a pre-send reservation (status
    # "sending"): the process died between Enter and the ledger mark,
    # so the message may have landed and no later run may re-send it
    # until an operator checks the thread by hand. Fail closed even
    # when the bubble is visible: a visible bubble may be the crashed
    # attempt's message, or a stale bubble from an earlier run with
    # the same run_id, and the ledger cannot tell them apart.
    if ledger.status(intent_id) == "sending":
        step["error"] = "retry-blocked-reservation"
        step["elapsed_s"] = round(time.monotonic() - t0, 4)
        log("send_retry_blocked_reservation", t0,
            window=window["label"], intent_id=intent_id,
            note="previous attempt reserved but never reconciled; "
            "message may have landed, check the thread by hand")
        return step
    # Intent binding (fix pass 2, redteam round 2 finding 3): a
    # recorded intent binds its message text, thread URL and
    # selectors. This runs BEFORE the sent-skip below: a changed
    # plan whose new text happens to have a visible stale bubble
    # must refuse, not skip on a message this intent never sent.
    # A later run whose plan disagrees (edited message, different
    # thread) refuses instead of sending a different message under
    # the same intent and overwriting the record. Records written
    # before binding existed carry no message field and skip this
    # check.
    if ledger.status(intent_id) == "sent":
        rec = ledger.record(intent_id)
        if rec.get("message") is not None and (
                rec.get("message") != message
                or rec.get("url") != window.get("url")
                or rec.get("thread_selector") != thread_sel
                or rec.get("bubble_selector") != bubble_sel):
            step["error"] = "retry-blocked-intent-changed"
            step["evidence"] = {
                "recorded": {"message": rec.get("message"),
                             "url": rec.get("url"),
                             "thread_selector":
                                 rec.get("thread_selector"),
                             "bubble_selector":
                                 rec.get("bubble_selector")},
                "current": {"message": message,
                            "url": window.get("url"),
                            "thread_selector": thread_sel,
                            "bubble_selector": bubble_sel}}
            step["elapsed_s"] = round(time.monotonic() - t0, 4)
            log("send_retry_blocked_intent_changed", t0,
                window=window["label"], intent_id=intent_id,
                note="recorded intent binds a different message, "
                "URL or selectors; use a new run_id")
            return step
    if ledger.status(intent_id) == "sent" and count_now > 0:
        ledger.mark(intent_id, "sent", window=window["label"],
                    message=message, url=window.get("url"),
                    thread_selector=thread_sel,
                    bubble_selector=bubble_sel,
                    note="bubble-already-present")
        step["status"] = "skipped-already-sent"
        step["elapsed_s"] = round(time.monotonic() - t0, 4)
        log("send_skipped_already_sent", t0, window=window["label"],
            intent_id=intent_id)
        return step
    if ledger.status(intent_id) == "sent":
        # A recorded "sent" intent whose bubble is absent refuses
        # instead of re-sending (fix pass 2, redteam round 2
        # finding 2 and redteam 4/4 finding 1): the bubble may be
        # unloaded rather than genuinely absent, a wrong bubble
        # selector reads 0 the same way, and a fresh page load
        # empties the fixture thread. Only a hand check of the
        # thread can tell, then a new run_id if a re-send is
        # really wanted.
        step["error"] = "retry-blocked-sent-bubble-absent"
        step["elapsed_s"] = round(time.monotonic() - t0, 4)
        log("ledger_sent_bubble_absent", t0, window=window["label"],
            intent_id=intent_id,
            note="ledger says sent but no bubble carrying the text "
            "is visible; refusing to re-send, check the thread "
            "by hand")
        return step

    # D3 ref-stability check FIRST, before any scroll: re-resolve
    # the harvested ref against the live DOM. A renamed or replaced
    # input fails fast here, before any click and before
    # ensure_visible scrolls anything (fix pass: scrolling first
    # moved a possibly-wrong element into view before D3 failed).
    # Compares tag, role and name, plus aria-label and placeholder
    # separately, not only through the derived name (fix pass,
    # council 1 issue 3 and redteam F6/F8: tag was returned but
    # never compared, and a placeholder-only rename passed when an
    # aria-label was present). aria-label and placeholder are
    # compared only when the harvest recorded them, so inventories
    # from older script versions do not false-fail. The HCU guard
    # below re-checks geometry; this check catches identity changes
    # the guard cannot see (same rect, different element).
    ref_now = driver.execute_script(REF_CHECK_JS, item["ref"])
    if not ref_now.get("found"):
        step["error"] = "target-gone"
        step["elapsed_s"] = round(time.monotonic() - t0, 4)
        return step
    aria_mismatch = (item.get("aria_label") is not None
                     and (ref_now.get("aria_label") or "")
                     != (item.get("aria_label") or ""))
    placeholder_mismatch = (item.get("placeholder") is not None
                            and (ref_now.get("placeholder") or "")
                            != (item.get("placeholder") or ""))
    if (ref_now.get("tag") != item.get("tag")
            or ref_now.get("role") != item.get("role")
            or ref_now.get("name") != item.get("name")
            or aria_mismatch or placeholder_mismatch):
        step["error"] = "ref-stale"
        step["evidence"] = {
            "expected": {"tag": item.get("tag"),
                         "role": item.get("role"),
                         "name": item.get("name"),
                         "aria_label": item.get("aria_label"),
                         "placeholder": item.get("placeholder")},
            "current": {"tag": ref_now.get("tag"),
                        "role": ref_now.get("role"),
                        "name": ref_now.get("name"),
                        "aria_label": ref_now.get("aria_label"),
                        "placeholder": ref_now.get("placeholder")},
            "nearest": ref_now.get("nearest", [])}
        step["elapsed_s"] = round(time.monotonic() - t0, 4)
        log("ref_stale", t0, window=window["label"],
            expected_name=item.get("name"),
            current_name=ref_now.get("name"))
        return step
    # Scroll, then guard: a below-fold target fails the hit test
    # before ensure_visible ever runs, so the guard must run on
    # post-scroll geometry. The click uses the guard-verified center,
    # not the pre-scroll position.
    pos = ensure_visible(driver, item["ref"])
    if pos is None:
        step["error"] = "target-gone"
        step["elapsed_s"] = round(time.monotonic() - t0, 4)
        return step
    # V5 hit test + HCU guard, from the live DOM, before any input.
    # Expect the harvested center when nothing scrolled (the 2 px
    # check then catches a moved input); after a scroll, expect the
    # post-scroll center (fix pass, redteam F7).
    expect = ((item["cx"], item["cy"]) if not pos.get("scrolled")
              else (pos["cx"], pos["cy"]))
    ok, reason, v = hcu_guard(driver, item, t0, expect=expect)
    if not ok:
        step["error"] = reason
        step["elapsed_s"] = round(time.monotonic() - t0, 4)
        log("guard_failed", t0, window=window["label"], reason=reason)
        return step

    # Real pointer click at the guard-verified center, then focus
    # check (V3) before any keystroke: a missed click must never type.
    click_at(driver, v["rect"]["cx"], v["rect"]["cy"])
    v = driver.execute_script(VERIFY_JS, item["ref"])
    if not v.get("active"):
        step["error"] = "focus-failed"
        step["evidence"] = v
        step["elapsed_s"] = round(time.monotonic() - t0, 4)
        log("focus_check_failed", t0, window=window["label"])
        return step

    # V11: arm the real MutationObserver before typing, so the
    # mutation delta covers the type and the bubble append. The
    # observer is scoped to the thread container (falling back to
    # document.body when the thread is missing), and counts mutation
    # records, not callbacks. The fixture counter
    # window.__inputEvents is kept alongside it.
    obs = driver.execute_script(OBSERVER_JS, thread_sel)
    mutations_before = obs.get("count", 0) if obs else 0
    step["v11_scope"] = obs.get("scope") if obs else None

    # Type with real keys, then V1 value readback before Enter.
    # Inputs and textareas hold the text in value; contenteditable
    # elements (Messenger's message input) hold it in innerText and
    # report value null, so check innerText for them.
    events_before = v.get("inputEvents")
    driver.find_element("css selector", item["ref"]).send_keys(message)
    v = driver.execute_script(VERIFY_JS, item["ref"])
    typed = (v.get("innerText") if v.get("innerText") is not None
             else v.get("value"))
    if typed != message:
        step["error"] = "value-mismatch"
        step["evidence"] = v
        step["elapsed_s"] = round(time.monotonic() - t0, 4)
        log("value_check_failed", t0, window=window["label"],
            value=v.get("value"), innerText=v.get("innerText"))
        return step
    step["v1_value_ok"] = True
    step["v11_input_events"] = (
        None if events_before is None or v.get("inputEvents") is None
        else v["inputEvents"] - events_before)

    # Pre-send reservation: write the intent as "sending" after the
    # V1 readback passes and before the Enter keypress, then
    # reconcile it after the V12 gate. A crash between Enter and the
    # mark leaves "sending" in the ledger, and a later run refuses
    # to re-send it (see the retry-blocked-reservation block above).
    # gate_baseline is the bubble count right before Enter: the
    # textNew gate passes only on a bubble that appears after it.
    gate_baseline = bubble_count()
    step["gate_baseline"] = gate_baseline
    if gate_baseline < 0:
        step["error"] = "thread-missing"
        step["elapsed_s"] = round(time.monotonic() - t0, 4)
        log("thread_missing", t0, window=window["label"],
            intent_id=intent_id, thread_selector=thread_sel,
            note="thread container vanished after the V1 readback; "
            "no reservation written, nothing sent")
        return step
    # Atomic reservation: reserve() marks "sending" only when the
    # intent is fresh or retryable, under one lock, so two processes
    # cannot both see None and both send (fix pass 2, redteam
    # round 2 finding 15). The reservation binds the message text,
    # thread URL and selectors (fix pass 2, redteam round 2
    # finding 3): a later run compares its plan against them.
    if not ledger.reserve(intent_id, window=window["label"],
                          message=message, url=window.get("url"),
                          thread_selector=thread_sel,
                          bubble_selector=bubble_sel):
        step["error"] = "retry-blocked-reservation"
        step["elapsed_s"] = round(time.monotonic() - t0, 4)
        log("send_retry_blocked_reservation", t0,
            window=window["label"], intent_id=intent_id,
            note="reservation refused: the intent is already held "
            "by another run or a previous attempt; check the "
            "thread by hand")
        return step
    step["reservation"] = "sending"

    def v11_delta():
        """MutationObserver delta since the observer was armed."""
        n = driver.execute_script(
            "return (typeof window.__v11Mutations === 'number') "
            "? window.__v11Mutations : null")
        if n is None:
            return None, None
        return n - mutations_before, n

    # Everything after the reservation runs inside try/except: an
    # exception here (Enter failed, driver died mid-gate) must
    # reconcile the intent to failed-unverified, never leave
    # "sending" sticky forever, and never let the exception erase
    # the ledger record (fix pass, council 1 note 5). The handler
    # only touches the ledger while the status is still "sending",
    # so a "sent" mark made before the exception is never
    # overwritten (fix pass, council 1 issue 1).
    try:
        from selenium.webdriver.common.keys import Keys
        driver.find_element("css selector", item["ref"]).send_keys(
            Keys.ENTER)
        # Causal tie, recorded evidence only: did the input clear
        # on Enter? A send that clears the input and appends exactly
        # one bubble is tied to our Enter; the gate itself stays
        # appearance-based (see the send_one docstring).
        v_after = driver.execute_script(VERIFY_JS, item["ref"])
        if v_after.get("found"):
            cleared = (v_after.get("innerText")
                       if v_after.get("innerText") is not None
                       else v_after.get("value"))
            step["input_cleared_after_enter"] = (cleared == "")
        else:
            step["input_cleared_after_enter"] = None

        # V12 finish gate, textNew: exactly ONE new bubble carrying
        # the exact text must appear in the thread DOM, counted past
        # the pre-Enter baseline. A stale bubble from an earlier run
        # cannot pass it. A count jumping past baseline + 1 is a
        # double append, not a pass (fix pass, redteam F5). The
        # gate settles (fix pass 2, redteam round 2 finding 4):
        # once the count first reaches baseline + 1 it keeps
        # polling for a full second, because an asynchronous
        # second append (optimistic bubble plus server echo, a
        # retried handler) landing 700 ms later used to score
        # "sent" with two identical bubbles. The deadline extends
        # past a late first sighting so a bubble arriving just
        # before the timeout still gets its settle second.
        deadline = time.monotonic() + v12_timeout
        gate_count = gate_baseline
        duplicate = False
        settled_at = None
        step["gate_settle_s"] = 1.0
        while time.monotonic() < deadline:
            gate_count = bubble_count()
            if gate_count > gate_baseline + 1:
                duplicate = True
                break
            if gate_count == gate_baseline + 1:
                if settled_at is None:
                    settled_at = time.monotonic()
                    deadline = max(deadline, settled_at + 1.0)
                elif time.monotonic() - settled_at >= 1.0:
                    break
            else:
                settled_at = None
            time.sleep(0.2)
        if duplicate:
            step["error"] = "duplicate-bubble"
            step["gate_count"] = gate_count
            delta, total = v11_delta()
            step["v11_mutations"] = delta
            step["v11_mutation_flag"] = bool(delta and delta > 0)
            step["elapsed_s"] = round(time.monotonic() - t0, 4)
            # Two identical bubbles landed; the message was sent
            # (twice), so no later run may re-send it.
            ledger.mark(intent_id, "failed-unverified",
                        window=window["label"], message=message,
                        error="duplicate-bubble",
                        note="two identical bubbles appeared after "
                        "one Enter; message sent, check the thread "
                        "by hand before any new run_id")
            log("duplicate_bubble", t0, window=window["label"],
                gate_baseline=gate_baseline, gate_count=gate_count)
            return step
        if gate_count != gate_baseline + 1:
            step["error"] = "v12-timeout"
            step["gate_count"] = gate_count
            delta, total = v11_delta()
            step["v11_mutations"] = delta
            step["v11_mutation_flag"] = bool(delta and delta > 0)
            step["elapsed_s"] = round(time.monotonic() - t0, 4)
            # The message may have landed unseen (the selectors are
            # the only witness and they just failed to see it). Mark
            # the intent failed-unverified so no later run re-sends
            # it with the same selectors; see the block at the top
            # of send_one.
            ledger.mark(intent_id, "failed-unverified",
                        window=window["label"], message=message,
                        error="v12-timeout",
                        note="message may have landed unseen; fix "
                        "selectors and use a new run_id after "
                        "manually checking the thread")
            log("v12_gate_timeout", t0, window=window["label"],
                timeout_s=v12_timeout)
            return step
        step["v12_gate_ok"] = True
        step["gate_count"] = gate_count
        delta, total = v11_delta()
        step["v11_mutations"] = delta
        step["v11_mutation_flag"] = bool(delta and delta > 0)
        ledger.mark(intent_id, "sent", window=window["label"],
                    message=message)
        step["status"] = "sent"
        step["elapsed_s"] = round(time.monotonic() - t0, 4)
        log("send_ok_v12", t0, window=window["label"],
            intent_id=intent_id)
        return step
    except Exception as exc:  # noqa: BLE001 - reconcile, then report
        if step.get("status") == "sent":
            # The send already completed and was marked sent; the
            # exception came after (e.g. logging). Keep the record.
            log("harness_error_after_sent", t0,
                window=window["label"], error=str(exc))
            return step
        if ledger.status(intent_id) == "sending":
            try:
                ledger.mark(intent_id, "failed-unverified",
                            window=window["label"], message=message,
                            error="harness-error-after-reservation",
                            note="exception after the reservation "
                            "was written; the message may have "
                            "landed, check the thread by hand")
            except Exception:
                pass
        step["error"] = "harness-error-after-reservation"
        step["evidence"] = {
            "exception": f"{type(exc).__name__}: {exc}"}
        step["elapsed_s"] = round(time.monotonic() - t0, 4)
        log("harness_error_after_reservation", t0,
            window=window["label"], error=str(exc))
        return step


def harvest_window(driver, label, t_start):
    """VISION 1 for one window: one evaluate, all inputs + buttons."""
    t0 = time.monotonic()
    items = driver.execute_script(HARVEST_JS)
    log("vision1_harvest_one_shot", t0, window=label,
        elements=len(items))
    return items


def frames_census(driver, label, t_start):
    """Gap 10: list the iframes in this window with origin and
    reachability. HARVEST_JS evaluates in the top frame only, so an
    input or thread inside an iframe is invisible to it; a
    cross-origin frame reports accessible false. Returns the list
    (empty when the page has no iframes)."""
    t0 = time.monotonic()
    frames = driver.execute_script(FRAMES_JS)
    log("vision1_frames", t0, window=label, frames=len(frames),
        cross_origin=sum(1 for f in frames
                         if not f.get("accessible")))
    return frames


# Thread bubble texts (fix pass, redteam F10): the exact-text
# COUNT_JS gate cannot see a foreign bubble rendered with a sender
# name or timestamp prefix ("Alice: <message>"), so the
# cross-window check also reads the raw bubble texts and matches by
# containment. Returns null when the thread container is missing.
TEXTS_JS = """
return (function(threadSel, bubbleSel){
  const t = document.querySelector(threadSel);
  if (!t) return null;
  return [...t.querySelectorAll(bubbleSel)]
    .map(b => b.textContent);
})(arguments[0], arguments[1], arguments[2])
"""


def thread_texts(driver, window):
    """Raw bubble texts in one window's thread, or None when the
    thread container is missing."""
    thread_sel = window.get("thread_selector", "#thread")
    bubble_sel = window.get("bubble_selector", ".bubble, [data-sender]")
    return driver.execute_script(TEXTS_JS, thread_sel, bubble_sel)


def bubble_count_for(driver, window, message):
    """COUNT_JS for one window: how many bubbles carry exactly this
    text. -1 (thread container missing) is preserved, never collapsed
    to 0 (fix pass, council 1 issue 2); callers treat -1 as
    thread-missing. None (JS returned nothing) reads as -1."""
    thread_sel = window.get("thread_selector", "#thread")
    bubble_sel = window.get("bubble_selector", ".bubble, [data-sender]")
    n = driver.execute_script(COUNT_JS, thread_sel, bubble_sel, message)
    return n if isinstance(n, int) else -1


def cross_window_check(driver, handles, plan, t_start):
    """Cross-window check (design doc section 4.2): after both sends,
    each thread must contain only its own message. A thread holding
    the other window's message means a send landed in the wrong
    thread. Foreign matching is by containment on the raw bubble
    texts (fix pass, redteam F10): a foreign bubble rendered with a
    sender name or timestamp prefix ("Alice: <message>") still
    counts, and the matching texts are recorded so near-misses are
    visible. Bubbles whose text exactly equals this window's own
    message are excluded from the foreign count. Returns
    {label: {own_count, foreign: {label: count},
    foreign_texts: {label: [texts]}, thread_missing: bool}}.
    The caller fails the run on any foreign count above 0."""
    result = {}
    for w in plan["windows"]:
        driver.switch_to.window(handles[w["label"]])
        own = bubble_count_for(driver, w, plan["messages"][w["label"]])
        texts = thread_texts(driver, w)
        foreign = {}
        foreign_texts = {}
        for o in plan["windows"]:
            if o["label"] == w["label"]:
                continue
            other_msg = plan["messages"][o["label"]]
            if texts is None:
                foreign[o["label"]] = 0
                foreign_texts[o["label"]] = []
                continue
            hits = [t for t in texts
                    if t != plan["messages"][w["label"]]
                    and other_msg in t]
            foreign[o["label"]] = len(hits)
            foreign_texts[o["label"]] = [t[:120] for t in hits[:3]]
        result[w["label"]] = {"own_count": own, "foreign": foreign,
                              "foreign_texts": foreign_texts,
                              "thread_missing": texts is None}
    log("cross_window_check", t_start, result=result)
    return result


def default_plan(workdir):
    """Fixture plan: two windows of the local chat fixture, unique
    test messages so the V12 gate can tell this run's bubbles apart."""
    run_id = "bench-" + datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:6]
    return {
        "run_id": run_id,
        "windows": [
            {"label": "clone1", "url": FIXTURE + "?clone=1",
             "input_name": "Message", "thread_selector": "#thread"},
            {"label": "clone2", "url": FIXTURE + "?clone=2",
             "input_name": "Message", "thread_selector": "#thread"},
        ],
        "messages": {
            "clone1": "BENCH-TEST clone1 " + run_id,
            "clone2": "BENCH-TEST clone2 " + run_id,
        },
        "timeouts": {"v12_gate_s": 5},
    }


def open_windows(driver, plan, t_start):
    """Open one window per plan entry in a single browser instance.

    TODO (D6): one vs two Zen instances for the two clone windows is
    unspecified. This script uses ONE instance with two windows (the
    shape the live run needs if both clones live in one Zen); two
    instances would need a second Marionette attach, which the
    one-session rule forbids on one browser but allows across two
    browser processes. --instances two is REFUSED until that exists:
    it is never recorded in results as if it ran.
    """
    handles = {}
    first = True
    for w in plan["windows"]:
        if first:
            driver.get(w["url"])
            first = False
        else:
            driver.switch_to.new_window("window")
            driver.get(w["url"])
        handles[w["label"]] = driver.current_window_handle
        log("window_opened", t_start, window=w["label"],
            url=w["url"])
    return handles


def normalize_file_url(url):
    """Normalize a file:// plan URL so the live gate cannot be
    bypassed by a path that starts with the fixture dir textually
    but points outside it (redteam batch 9 task 2 finding 5:
    tests/../../tmp/rt-bypass.html passed startswith(FIXTURE_DIR)
    and ran the full send chain against a file outside tests/).
    os.path.normpath resolves '..' segments; non-file URLs pass
    through unchanged and fail the fixture gate on their own."""
    if not url.startswith("file://"):
        return url
    return "file://" + os.path.normpath(url[len("file://"):])


def validate_plan(plan):
    """Plan validation, before any browser starts (redteam batch 9
    task 2 findings 1, 2, 3, 5). The benchmark is defined as exactly
    two windows, two distinct threads, two messages. Before this
    check an empty plan reported PASS (0 sent == 0 windows), a
    one-window plan PASSED with one message, and two windows on the
    same URL PASSED with both messages in one thread. All four now
    refuse with exit 2 before the browser starts. Returns the plan
    with its URLs normalized in place. Raises ValueError on any
    defect; the caller prints REFUSED and returns 2."""
    if not isinstance(plan, dict):
        raise ValueError("plan must be a JSON object")
    run_id = plan.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        raise ValueError("plan needs a non-empty run_id string")
    windows = plan.get("windows")
    if not isinstance(windows, list) or len(windows) != 2:
        n = (len(windows) if isinstance(windows, list)
             else "not a list")
        raise ValueError(
            "plan needs exactly 2 windows (got "
            f"{n}); the benchmark is two clones, two threads, "
            "two messages")
    urls = []
    for w in windows:
        if not isinstance(w, dict):
            raise ValueError("each plan window must be an object")
        label = w.get("label")
        if not isinstance(label, str) or not label:
            raise ValueError("each plan window needs a label string")
        url = w.get("url")
        if not isinstance(url, str) or not url:
            raise ValueError("each plan window needs a url string")
        url = normalize_file_url(url)
        w["url"] = url
        urls.append(url)
    if urls[0] == urls[1]:
        raise ValueError(
            "the two plan windows must point at different URLs; "
            "two windows on the same thread would report PASS "
            "with both messages in one thread")
    messages = plan.get("messages")
    if not isinstance(messages, dict):
        raise ValueError("plan needs a messages object")
    for w in windows:
        if w["label"] not in messages:
            raise ValueError(
                "plan messages has no entry for window "
                f"{w['label']!r}")
        msg = messages[w["label"]]
        if not isinstance(msg, str) or not msg:
            raise ValueError(
                "plan messages must be non-empty strings "
                f"(window {w['label']!r})")
    # Distinct messages (fix pass, redteam F11): identical messages
    # make a correct run FAIL the cross-window check, because the
    # check identifies messages by text alone. Distinct thread
    # selectors are NOT required across windows: the fixture uses
    # "#thread" in both windows, and the windows are different
    # documents, so the same selector string points at different
    # threads; distinct URLs (checked above) already enforce
    # distinct threads.
    msgs = [messages[w["label"]] for w in windows]
    if len(set(msgs)) != len(msgs):
        raise ValueError(
            "plan messages must be distinct per window; identical "
            "messages make the cross-window check fail a correct "
            "run, because it identifies messages by text alone")
    # Substring-free (fix pass 2, redteam round 2 finding 15):
    # the cross-window check matches foreign bubbles by
    # containment, so if one message is a substring of the other,
    # a correct run fails contamination on its own bubbles.
    if msgs[0] in msgs[1] or msgs[1] in msgs[0]:
        raise ValueError(
            "plan messages must not be substrings of each other; "
            "the cross-window check matches by containment and "
            "would flag a correct run as contaminated")
    return plan


REGISTRY_DEFAULT = os.path.expanduser(
    "~/.cache/two_vision_bench/run_registry.json")


def registry_check_and_record(run_id, ledger_path, registry_path):
    """Shared run registry (fix pass, redteam F3): bind a run_id to
    the ledger path of its first run. Returns (ok, previous_path).
    A later run with the same run_id but a different ledger path
    (fresh workdir, empty ledger) is refused by the caller: its
    exactly-once pre-check is blind and it would re-send. The same
    ledger path is a same-workdir retry and is allowed. Writes are
    locked (fcntl flock) and atomic (temp file + os.replace)."""
    import fcntl
    os.makedirs(os.path.dirname(os.path.abspath(registry_path)),
                exist_ok=True)
    ledger_abs = os.path.abspath(ledger_path)
    lock_path = registry_path + ".lock"
    with open(lock_path, "w", encoding="utf-8") as lock_f:
        fcntl.flock(lock_f, fcntl.LOCK_EX)
        try:
            reg = {}
            if os.path.exists(registry_path):
                try:
                    with open(registry_path, encoding="utf-8") as f:
                        reg = json.load(f)
                except json.JSONDecodeError as exc:
                    # A corrupt registry cannot be trusted: refuse
                    # instead of treating every run_id as fresh and
                    # re-sending (fix pass 2, council 1 finding
                    # 10a). The caller turns this into REFUSED.
                    raise ValueError(
                        f"corrupt run registry {registry_path}: "
                        f"{exc}; fix or remove it by hand after "
                        "checking the threads, never delete it "
                        "blindly") from exc
            prev = reg.get(run_id)
            if prev is not None and prev != ledger_abs:
                return False, prev
            reg[run_id] = ledger_abs
            tmp_path = registry_path + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(reg, f, indent=2, sort_keys=True)
            os.replace(tmp_path, registry_path)
            return True, None
        finally:
            fcntl.flock(lock_f, fcntl.LOCK_UN)


def main():
    ap = argparse.ArgumentParser(
        description="2-vision benchmark: build only, no live run yet.")
    ap.add_argument("--mode", choices=["harvest", "run"],
                    default="run", help="harvest: VISION 1 only; "
                    "run: full send chain with V12 gates")
    ap.add_argument("--fixture", action="store_true",
                    help="dry-test against the local chat fixture "
                    "(default plan, two windows, no real thread)")
    ap.add_argument("--live", action="store_true",
                    help="live mode: plan URLs are real threads. "
                    "Requires --confirm-live and coordinator approval.")
    ap.add_argument("--confirm-live", action="store_true",
                    help="confirm a live run was approved. Never pass "
                    "this without the coordinator saying run.")
    ap.add_argument("--instances", choices=["one", "two"], default="one",
                    help="one browser instance with two windows "
                    "(default, D6 open) or two instances")
    ap.add_argument("--strict-input-name", action="store_true",
                    help="fail closed when the picked input's name does "
                    "not contain the plan's input_name (rung 2: the "
                    "step-2 run invocation reads no inventory, so "
                    "the script itself must refuse to type into a "
                    "wrongly named textbox, e.g. a login email "
                    "field; in harvest mode it checks the harvested "
                    "names the same way, so no operator read of "
                    "inventory.json is needed for the check).")
    ap.add_argument("--visions-used", type=int, default=2,
                    help="visions to record in results.json (default "
                    "2; rung 2 passes 0: the step-2 run invocation "
                    "uses no vision, the step-1 harvest read is "
                    "pre-run preparation outside the budget).")
    ap.add_argument("--allow-resume", action="store_true",
                    help="score a resume run as PASS when "
                    "skipped-already-sent steps cover the rest. "
                    "Without it a run with zero fresh sends never "
                    "scores PASS, even when both steps skip.")
    ap.add_argument("--run-registry",
                    help="shared run_id registry path (default "
                    "~/.cache/two_vision_bench/run_registry.json)")
    ap.add_argument("--no-run-registry", action="store_true",
                    help="disable the run_id registry (test harnesses "
                    "only; a reused run_id in a fresh workdir then "
                    "re-sends, because its ledger is empty).")
    ap.add_argument("--plan", help="plan JSON (default: fixture plan)")
    ap.add_argument("--inventory", help="inventory JSON to write "
                    "(VISION 1 output) or read with --inventory-in")
    ap.add_argument("--inventory-in", help="read a saved inventory "
                    "instead of harvesting (VISION 1 already done)")
    ap.add_argument("--ledger", help="exactly-once ledger JSON "
                    "(default: <workdir>/ledger.json)")
    ap.add_argument("--workdir", default=DEFAULT_WORKDIR,
                    help="workdir for ledger/results (default "
                    "/tmp/two_vision_bench)")
    ap.add_argument("--out", help="results JSON path "
                    "(default: <workdir>/results.json)")
    ap.add_argument("--print-inventory", action="store_true",
                    help="print the numbered compact inventory text "
                    "(the agent-visible VISION 1 format)")
    args = ap.parse_args()

    if args.visions_used < 0:
        print("REFUSED: --visions-used cannot be negative.",
              file=sys.stderr)
        return 2
    if args.live and not args.confirm_live:
        print("REFUSED: live mode needs --confirm-live, which only the "
              "coordinator gives after approving the run.",
              file=sys.stderr)
        return 2
    if args.live and args.fixture:
        print("REFUSED: --live and --fixture together make no sense.",
              file=sys.stderr)
        return 2
    if args.instances == "two":
        print("REFUSED: --instances two is not implemented: the run "
              "always uses one browser instance with two windows, and "
              "recording 'two' in results would lie about what ran.",
              file=sys.stderr)
        return 2

    os.makedirs(args.workdir, exist_ok=True)
    # Disk-space guard (fix pass, redteam note): a full disk made
    # finish() raise while writing results.json, leaving a 0-byte
    # file even though both sends had succeeded. Refuse early
    # instead of losing the run record late.
    import shutil
    free_b = shutil.disk_usage(args.workdir).free
    if free_b < 100 * 1024 * 1024:
        print(f"REFUSED: only {free_b // (1024 * 1024)} MB free in "
              f"{args.workdir}; free space before running, the run "
              "record would not survive a full disk.",
              file=sys.stderr)
        return 2
    t_start = time.monotonic()
    wall_start = datetime.now(timezone.utc).isoformat()

    if args.plan:
        with open(args.plan, encoding="utf-8") as f:
            plan = json.load(f)
    elif args.fixture or not args.live:
        plan = default_plan(args.workdir)
    else:
        print("REFUSED: live mode needs --plan with thread URLs.",
              file=sys.stderr)
        return 2
    # Plan validation first, before any browser starts: exactly 2
    # windows, distinct URLs, non-empty run_id. See validate_plan.
    try:
        plan = validate_plan(plan)
    except ValueError as exc:
        print(f"REFUSED: invalid plan: {exc}", file=sys.stderr)
        return 2
    # Live gate, on the plan URLs, not the flag: a custom --plan with
    # real thread URLs and no --live flag used to run the full send
    # chain against those threads. Any URL outside the local fixture
    # files now requires BOTH --live and --confirm-live, before any
    # browser starts. Fixture mode is the default plan and any plan
    # whose windows all point at local fixture files under tests/.
    # Plan URLs were normalized by validate_plan above, so a '..'
    # path cannot pass this gate textually while pointing outside
    # tests/.
    fixture_urls = all(
        w.get("url", "").startswith(FIXTURE_DIR)
        for w in plan["windows"])
    if not fixture_urls and not (args.live and args.confirm_live):
        print("REFUSED: plan URLs are not the local fixture. A live "
              "run needs --live and --confirm-live; without them the "
              "script sends nothing.", file=sys.stderr)
        return 2
    run_id = plan["run_id"]
    ledger_path = args.ledger or os.path.join(args.workdir, "ledger.json")
    # Run registry (fix pass, redteam F3): refuse a reused run_id
    # bound to a different ledger path before the browser starts.
    # Harvest mode never touches it (fix pass 2, redteam round 2
    # finding 1): a harvest sends nothing, so binding the run_id
    # there would make the rung 2 step-2 run in its own workdir
    # REFUSED. The registry binds only in run mode. The registry
    # path and the enabled flag are recorded in results.json (fix
    # pass 2, redteam round 2 finding 5), so a run that bypassed
    # the registry with --no-run-registry or --run-registry is
    # visible in its own record instead of indistinguishable from
    # a protected run. Live runs must use the default registry
    # path; the runbook forbids both override flags live.
    registry_path = None
    registry_enabled = False
    if args.mode == "run" and args.no_run_registry:
        print("WARNING: run_id registry disabled; a reused run_id "
              "in a fresh workdir re-sends, because its ledger is "
              "empty.", file=sys.stderr)
    elif args.mode == "run":
        registry_path = args.run_registry or REGISTRY_DEFAULT
        registry_enabled = True
        try:
            ok, prev = registry_check_and_record(
                run_id, ledger_path, registry_path)
        except ValueError as exc:
            print(f"REFUSED: {exc}", file=sys.stderr)
            return 2
        if not ok:
            print(f"REFUSED: run_id {run_id!r} already ran with "
                  f"ledger {prev}; this run would use {ledger_path}, "
                  "whose ledger is empty, so its exactly-once "
                  "pre-check is blind and it would re-send. Use a "
                  "new run_id, or reuse the original workdir/ledger.",
                  file=sys.stderr)
            return 2
    results = {"run_id": run_id, "mode": args.mode,
               "live": bool(args.live), "instances": args.instances,
               "wall_start": wall_start,
               "visions_used": args.visions_used,
               "registry_enabled": registry_enabled,
               "registry_path": registry_path,
               "steps": [], "outcome": "FAIL"}

    proc = None
    driver = None
    try:
        proc = launch_browser(os.path.join(args.workdir, "profile"))
        driver = attach_driver()
        handles = open_windows(driver, plan, t_start)

        # VISION 1: one-shot harvest per window.
        inventory = {}
        if args.inventory_in:
            with open(args.inventory_in, encoding="utf-8") as f:
                inventory = json.load(f)
            log("vision1_inventory_loaded", t_start,
                path=args.inventory_in)
        else:
            for w in plan["windows"]:
                driver.switch_to.window(handles[w["label"]])
                items = harvest_window(driver, w["label"], t_start)
                inventory[w["label"]] = items
            inv_path = args.inventory or os.path.join(
                args.workdir, "inventory.json")
            # Atomic write (fix pass 2, council 1 finding 10c):
            # the same full-disk failure that left a 0-byte
            # results.json would leave a 0-byte inventory.json.
            inv_tmp = inv_path + ".tmp"
            with open(inv_tmp, "w", encoding="utf-8") as f:
                json.dump(inventory, f, indent=2)
            os.replace(inv_tmp, inv_path)
            log("vision1_inventory_written", t_start, path=inv_path)
        # Gap 10 frames census: one evaluate per window, top frame
        # only. A cross-origin iframe reports accessible false; the
        # runbook's harvest-first step stops on one.
        results["frames"] = {}
        for w in plan["windows"]:
            driver.switch_to.window(handles[w["label"]])
            results["frames"][w["label"]] = frames_census(
                driver, w["label"], t_start)
        if args.print_inventory:
            for w in plan["windows"]:
                print(format_inventory(w["label"],
                                       inventory[w["label"]],
                                       results["frames"].get(w["label"])))
        if args.mode == "harvest":
            # Mechanized name check (fix pass, redteam F13): with
            # --strict-input-name the script itself refuses to
            # accept a wrongly named input, so rung 2 step 1 needs
            # no operator read of inventory.json for the check. The
            # picked name, aria-label and placeholder per window are
            # logged and recorded in results["harvest_inputs"].
            results["harvest_inputs"] = {}
            if args.strict_input_name:
                for w in plan["windows"]:
                    hint = w.get("input_name", "Message")
                    item = find_input(inventory[w["label"]], hint)
                    if item is None:
                        results["steps"].append(
                            {"step": len(results["steps"]) + 1,
                             "window": w["label"], "status": "failed",
                             "error": "no-message-input-in-inventory"})
                        return finish(results, args, t_start, 1)
                    results["harvest_inputs"][w["label"]] = {
                        "name": item["name"],
                        "aria_label": item.get("aria_label"),
                        "placeholder": item.get("placeholder"),
                        "ref": item["ref"]}
                    log("harvest_input_picked", t_start,
                        window=w["label"], input_name=item["name"],
                        aria_label=item.get("aria_label"),
                        placeholder=item.get("placeholder"),
                        ref=item["ref"])
                    if hint.lower() not in item["name"].lower():
                        results["steps"].append(
                            {"step": len(results["steps"]) + 1,
                             "window": w["label"], "status": "failed",
                             "error": "input-name-mismatch",
                             "evidence": {
                                 "expected_name_contains": hint,
                                 "actual_name": item["name"],
                                 "ref": item["ref"]}})
                        log("input_name_mismatch", t_start,
                            window=w["label"], expected=hint,
                            actual=item["name"])
                        return finish(results, args, t_start, 1)
            results["outcome"] = "HARVEST-ONLY"
            results["steps"] = [
                {"step": i + 1, "window": w["label"],
                 "status": "harvested",
                 "elements": len(inventory[w["label"]])}
                for i, w in enumerate(plan["windows"])]
            return finish(results, args, t_start, 0)

        # Plan-once: pick the message input per window from inventory.
        targets = {}
        for w in plan["windows"]:
            item = find_input(inventory[w["label"]],
                              w.get("input_name", "Message"))
            if item is None:
                results["steps"].append(
                    {"step": len(results["steps"]) + 1,
                     "window": w["label"], "status": "failed",
                     "error": "no-message-input-in-inventory"})
                return finish(results, args, t_start, 1)
            targets[w["label"]] = item

        # Rung 2 strict input name: with no operator reading the
        # inventory, the script itself must refuse to type into a
        # textbox whose name does not contain the plan's input_name.
        # Without this flag the old behavior stands: find_input falls
        # back to the first visible textbox, which on a login page is
        # the email field (runbook section 0 item 1).
        if args.strict_input_name:
            for w in plan["windows"]:
                hint = w.get("input_name", "Message")
                picked = targets[w["label"]]
                if hint.lower() not in picked["name"].lower():
                    results["steps"].append(
                        {"step": len(results["steps"]) + 1,
                         "window": w["label"], "status": "failed",
                         "error": "input-name-mismatch",
                         "evidence": {
                             "expected_name_contains": hint,
                             "actual_name": picked["name"],
                             "ref": picked["ref"]}})
                    log("input_name_mismatch", t_start,
                        window=w["label"], expected=hint,
                        actual=picked["name"])
                    return finish(results, args, t_start, 1)

        # Batch-start before-snapshot: count the bubbles carrying
        # each message before any send. Recorded as evidence in
        # results["before_counts"] and each step's before_count
        # only: the V12 gate does NOT use this count, it passes
        # only on a NEW bubble past the pre-Enter gate_baseline
        # measured inside send_one (fix pass, redteam correction 2
        # and council 1 note 4: the old comment claimed the gate
        # used this count, which was never true in code).
        results["before_counts"] = {}
        for w in plan["windows"]:
            driver.switch_to.window(handles[w["label"]])
            results["before_counts"][w["label"]] = bubble_count_for(
                driver, w, plan["messages"][w["label"]])
        # A missing thread container (-1) fails fast here, before
        # any send is attempted (fix pass, council 1 issue 2).
        for w in plan["windows"]:
            if results["before_counts"][w["label"]] < 0:
                results["steps"].append(
                    {"step": len(results["steps"]) + 1,
                     "window": w["label"], "status": "failed",
                     "error": "thread-missing",
                     "evidence": {"thread_selector": w.get(
                         "thread_selector", "#thread")}})
                log("thread_missing", t_start, window=w["label"],
                    thread_selector=w.get("thread_selector", "#thread"),
                    note="thread container matched nothing before "
                    "any send; fix the thread selector")
                return finish(results, args, t_start, 1)

        # Guarded send chain, stop at first failure, rest not-executed.
        # The ledger is constructed here, in run mode only: harvest
        # mode never sends, so it needs no ledger and must not fail
        # on a corrupt one (fix pass 2). A corrupt ledger raises
        # ValueError, caught by the outer handler as a harness
        # error with exit 2.
        ledger = Ledger(ledger_path)
        step_no = 0
        failed = False
        for w in plan["windows"]:
            step_no += 1
            if failed:
                results["steps"].append(
                    {"step": step_no, "window": w["label"],
                     "status": "not-executed"})
                continue
            driver.switch_to.window(handles[w["label"]])
            intent_id = run_id + ":" + w["label"]
            try:
                step = send_one(driver, w, targets[w["label"]],
                                plan["messages"][w["label"]], intent_id,
                                ledger, plan, t_start, step_no,
                                before_count=results["before_counts"][
                                    w["label"]])
            except Exception as exc:  # noqa: BLE001 - record, not lose
                # Pre-reservation exceptions escape send_one (its
                # try block starts at the reservation): record the
                # failed step instead of losing it from
                # results["steps"], and reconcile a reservation if
                # one was written (fix pass 2, council 1 finding
                # 10d). The ledger is correctly left unmarked when
                # no reservation exists.
                if ledger.status(intent_id) == "sending":
                    try:
                        ledger.mark(intent_id, "failed-unverified",
                                    window=w["label"],
                                    message=plan["messages"][w["label"]],
                                    error="harness-error-before-"
                                    "reservation",
                                    note="exception after the "
                                    "reservation was written; the "
                                    "message may have landed, check "
                                    "the thread by hand")
                    except Exception:
                        pass
                step = {"step": step_no, "window": w["label"],
                        "intent_id": intent_id, "status": "failed",
                        "error": "harness-error-before-reservation",
                        "evidence": {"exception":
                                     f"{type(exc).__name__}: {exc}"},
                        "before_count": results["before_counts"][
                            w["label"]],
                        "elapsed_s": 0.0}
                log("harness_error_before_reservation", t_start,
                    window=w["label"], error=str(exc))
            results["steps"].append(step)
            if step["status"] not in ("sent", "skipped-already-sent"):
                failed = True
                # Never overwrite a protective ledger record with a
                # plain "failed": "failed-unverified" blocks the
                # retry, "sent" is the proof a message landed, and
                # "sending" means a crashed attempt may have landed.
                # Overwriting any of them unblocks a re-send (fix
                # pass, council 1 issue 1 and redteam F1: a failed
                # retry erased a "sent" record, then the script
                # re-sent despite a visible identical bubble).
                if ledger.status(intent_id) not in (
                        "failed-unverified", "sent", "sending"):
                    ledger.mark(intent_id, "failed",
                                error=step.get("error"))

        sent = [s for s in results["steps"]
                if s["status"] in ("sent", "skipped-already-sent")]
        # Fresh sends this invocation only (fix pass, redteam F2):
        # a run in which no send happened (both steps skipped on a
        # recorded "sent" ledger) must not score PASS, or a retry
        # scores PASS with zero new sends and results.json itself
        # says PASS. --allow-resume explicitly scores a resume run.
        sent_now = [s for s in results["steps"]
                    if s["status"] == "sent"]
        results["sends_this_run"] = len(sent_now)
        results["allow_resume"] = bool(args.allow_resume)
        effective = sent_now if not args.allow_resume else sent
        # Cross-window check: each thread must hold only its own
        # message. A thread holding the other window's message
        # fails the run even when both sends report sent.
        results["cross_window_check"] = cross_window_check(
            driver, handles, plan, t_start)
        contaminated = any(
            c > 0
            for rec in results["cross_window_check"].values()
            for c in rec["foreign"].values())
        # A thread that vanished after the gates still scores FAIL
        # (fix pass 2, council 1 finding 3 and redteam round 2
        # finding 6): the cross-window check reports thread_missing
        # and own_count -1/0 in that case, and the outcome rule used
        # to consult neither, so contamination on a thread it could
        # not read passed silently. own_count below 1 fails even
        # without contamination: the sent bubble is gone.
        thread_gone = any(
            rec.get("thread_missing")
            for rec in results["cross_window_check"].values())
        own_missing = any(
            rec.get("own_count", -1) < 1
            for rec in results["cross_window_check"].values())
        if contaminated:
            results["outcome_note"] = (
                "cross-window-contamination: a thread holds the "
                "other window's message")
        elif thread_gone or own_missing:
            results["outcome_note"] = (
                "cross-window-check-incomplete: a thread vanished "
                "after the gates or holds no bubble with its own "
                "message; the run cannot be scored PASS on gates "
                "alone")
        elif len(sent_now) == 0:
            # The note must describe the actual failure (fix pass 2,
            # council 1 finding 2 and redteam 4/4 finding 6): the
            # old text claimed both steps skipped even when clone1
            # failed v12-timeout and clone2 never executed.
            if all(s.get("status") == "skipped-already-sent"
                   for s in results["steps"]):
                results["outcome_note"] = (
                    "no sends this run: both steps skipped on "
                    "recorded sent intents; a retry that only skips "
                    "does not score PASS (pass --allow-resume to "
                    "score a resume run)")
            else:
                errors = "; ".join(
                    f"{s.get('window')}:{s.get('error')}"
                    for s in results["steps"] if s.get("error"))
                results["outcome_note"] = (
                    "no sends this run: "
                    + (errors or "no step error recorded"))
        # Outcome scoring (M1): PASS iff both messages are in their
        # threads. VISION 2 is the agent looking at both threads once;
        # the script's V12 gates are the same check by DOM read.
        # The rule requires exactly 2 sent AND exactly 2 windows:
        # validate_plan already refuses any other window count, but
        # the outcome must not pass on 0 == 0 if that ever changes.
        results["outcome"] = ("PASS" if len(effective) == 2
                              and len(plan["windows"]) == 2
                              and not contaminated
                              and not thread_gone
                              and not own_missing
                              else "FAIL")
        return finish(results, args, t_start,
                      0 if results["outcome"] == "PASS" else 1)
    except Exception as exc:
        results["error"] = f"{type(exc).__name__}: {exc}"
        log("harness_error", t_start, error=results["error"])
        return finish(results, args, t_start, 2)
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass
        if proc is not None:
            try:
                proc.terminate()
                proc.wait(timeout=10)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass


def finish(results, args, t_start, code):
    results["wall_s"] = round(time.monotonic() - t_start, 4)
    out_path = args.out or os.path.join(args.workdir, "results.json")
    # Atomic write (fix pass, redteam note): a full disk mid-write
    # used to leave a 0-byte results.json; write a temp file and
    # replace, so the previous record survives a failed write.
    # Never raise out of finish() (fix pass 2, council 1 finding
    # 10b): if the disk fills mid-write, the first finish() used to
    # raise inside the try and the except block called finish()
    # again, which raised again uncaught and no results.json was
    # written at all. Log the loss to stderr and return the
    # original exit code, so the outcome is still reported.
    try:
        tmp_path = out_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        os.replace(tmp_path, out_path)
    except Exception as exc:  # noqa: BLE001 - report, do not raise
        print(f"WARNING: could not write results to {out_path}: "
              f"{exc}; the run record is lost, the exit code still "
              "reports the outcome.", file=sys.stderr)
    log("benchmark_finished", t_start, outcome=results["outcome"],
        wall_s=results["wall_s"], out=out_path)
    return code


if __name__ == "__main__":
    sys.exit(main())
