#!/usr/bin/env python3
"""Live Zen runner: clone1-batch3 FIXED suite, 10 tests (Worker Y14, 21/11/2026).

Runs the merged fixed suite (main commit 1d23532, Y15 D1 fix on top of
Y10's reconciled best of both: t05 clone1 fixture + Y10 checker, t09
clone1 polling checker + Y10 cancel dwell, t10 Y15 exact-zero + clock
liveness checks + sampler as second witness) against the LIVE
Zen on the laptop via geckodriver --connect-existing (Marionette 2828).
Stdlib only. Reuses the proven driver from tests/realistic/run_live.py
(Worker P: explicit tab switch after window/new, 1s settle after
navigation, 0.5s after switch, no maximize, one WebDriver session per
test, always deleted in a finally block) and the diagnose-first ladder
from tests/realistic/run_agyq2.py (Worker Y4d: ensure_visible verbatim).

Rules:
- One WebDriver session per test, ALWAYS deleted in a finally block.
- A NEW tab per test; user tabs are never navigated, typed into, or
  clicked. Test tabs are closed at the end of each test.
- Fixtures are served from a loopback HTTP server started by this script
  (same origin, so localStorage and multi-tab/popup sharing work).
- End states are verified by reading the DOM directly. No fixture verify
  hook is ever used as an oracle.
- Every test starts with new_tab(fixture URL), localStorage.clear() +
  sessionStorage.clear(), refresh() (fresh-profile equivalence; t07/t08/
  t09 persist in localStorage).
- Preflight step 0 proves the /actions input path live on a scratch tab
  before t01. If it fails, the run stops before t01.
- A POST /actions that hits the 30 s _wd timeout is INFRA: close the
  session, record the test INFRA, next test starts a fresh session.
- Circuit breaker: abort the suite after 2 consecutive INFRA failures.
- One retry per failed test at most, only if the failure is INFRA.

Usage (on the laptop, from /tmp/y14-server):
  LIVE_SERVER_ROOT=/tmp/y14-server LIVE_SERVER_PORT=8771 \
  LIVE_LOG=/tmp/worker-y14-live.jsonl LIVE_RUN_ID=y14-batch3 \
  WD_PORT=4452 python3 run_batch3.py all
  python3 run_batch3.py b3-t01 b3-t05
"""
import json
import os
import sys
import time
import urllib.error
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_live import WD, Runner, start_server  # noqa: E402
from run_agyq2 import ensure_visible, rebootstrap_tab  # noqa: E402
# (Y4d ladder, verbatim; rebootstrap_tab for the final fresh tab, H3)

# --- select_option / clear_search / append_text, copied verbatim from
# run_fcck.py (Worker U), attributed here. select_option sets a <select>
# value and fires change. clear_search clears an input and fires input
# so the filter re-renders (used for empty steps: whether Marionette
# /clear fires an input event is UNVERIFIED, and every empty step in
# this suite depends on an input listener). append_text types without
# clearing: focus, caret to end, send keys (the key fallback path,
# never type_text, which would clear first and erase the typed text).


def select_option(d, css, value):
    """Set a <select> value and fire change."""
    return d.eval(
        "const el=document.querySelector(arguments[0]);"
        "el.value=arguments[1];"
        "el.dispatchEvent(new Event('change',{bubbles:true}));"
        "return el.value;", [css, value])


def clear_search(d, css):
    """Clear an input and fire input so the filter re-renders."""
    return d.eval(
        "const el=document.querySelector(arguments[0]); el.value='';"
        "el.dispatchEvent(new Event('input',{bubbles:true})); return 'cleared';",
        [css])


def append_text(d, css, text):
    """Type without clearing: focus, caret to end, send keys."""
    d.eval(
        "const el=document.querySelector(arguments[0]); el.focus();"
        "el.setSelectionRange(el.value.length, el.value.length);",
        [css])
    el = d.find(css)
    d._wd("POST", d._s(f"/element/{el}/value"), {"text": text})
    return "appended"


# WebDriver PUA key codes (W3C Actions mapping). Note: the legacy
# Firefox Marionette Keys doc maps ENTER to 0xE006, not E007; that is
# the old mapping, not the W3C Actions mapping, which is why preflight
# asserts the recorded e.key string, not just that a keydown fired.
KEY_ENTER = "\uE007"
KEY_HOME = "\uE011"
KEY_ARROW_LEFT = "\uE012"
KEY_ARROW_UP = "\uE013"
KEY_ARROW_RIGHT = "\uE014"
KEY_ARROW_DOWN = "\uE015"

# Preflight result: set by run_preflight, read by type_empty.
# True when Marionette /clear was proven to fire the input event live.
CLEAR_FIRES_INPUT = None

# Preflight result: set by run_preflight. True when POST /actions was
# proven live; False routes the helpers to their specified fallbacks.
ACTIONS_OK = True


def _actions_post(d, payload):
    """POST /session/:id/actions. A 30 s _wd timeout raises
    RuntimeError("INFRA: ...") so run_one records it as INFRA with one
    retry and a breaker count (redteam 2 H2). WD._wd raises
    TimeoutError/URLError on a urlopen timeout (run_live.py L570-581).
    """
    try:
        return d._wd("POST", d._s("/actions"), payload)
    except (TimeoutError, urllib.error.URLError) as exc:
        raise RuntimeError(f"INFRA: /actions POST timed out: {exc}")


def _actions_release(d):
    """DELETE /session/:id/actions, best effort, never raises. Try the
    {} body first; if geckodriver rejects it, retry with body None."""
    try:
        d._wd("DELETE", d._s("/actions"), {})
        return "delete-body-{}"
    except Exception:
        pass
    try:
        d._wd("DELETE", d._s("/actions"), None)
        return "delete-body-none"
    except Exception as exc:
        print(f"[actions] release failed (harmless): {exc}", flush=True)
        return "delete-failed"


def send_key_raw(d, css, key):
    """Fallback key send: no-clear raw element/value with a PUA key
    code (append_text pattern). Used only when /actions is down."""
    el = d.find(css)
    d._wd("POST", d._s(f"/element/{el}/value"), {"text": key})
    return "raw-key"


def press_keys(d, keys, css=None):
    """Send keyDown+keyUp per key via the Actions API, batched max 10
    pairs per call. Payload shape is W3C Perform Actions, all fields
    explicit. Returns the release form used, for the log. When preflight
    proved /actions down (ACTIONS_OK False), routes to the raw
    element/value fallback, which needs css."""
    if not ACTIONS_OK:
        if css is None:
            raise RuntimeError("press_keys fallback needs css")
        for k in keys:
            send_key_raw(d, css, k)
        print("[fallback] press_keys used raw element/value", flush=True)
        return "fallback-raw"
    release_form = None
    for i in range(0, len(keys), 10):
        batch = keys[i:i + 10]
        acts = []
        for k in batch:
            acts.append({"type": "keyDown", "value": k})
            acts.append({"type": "keyUp", "value": k})
        payload = {"actions": [{
            "type": "key", "id": "keyboard", "actions": acts}]}
        _actions_post(d, payload)
        release_form = _actions_release(d)
    return release_form


def _rect_of(d, js_expr):
    """Bounding rect of the element located by JS, as ints."""
    r = d.eval(
        "const el=(" + js_expr + ");"
        "if (!el) return null;"
        "const b = el.getBoundingClientRect();"
        "return {x: b.x, y: b.y, w: b.width, h: b.height};")
    if not isinstance(r, dict):
        raise RuntimeError(f"rect: element not found: {js_expr[:80]}")
    return r


def _probe_point(d, x, y):
    """elementFromPoint check at viewport coords. Returns the top
    element's identity string, or raises when nothing is there."""
    top = d.eval(
        "const el = document.elementFromPoint(arguments[0], arguments[1]);"
        "if (!el) return null;"
        "return (el.tagName || '') + '#' + (el.id || '') + '.' + "
        "((el.className || '') + '').split(' ')[0];", [x, y])
    if top is None:
        raise RuntimeError(f"elementFromPoint found nothing at {x},{y}")
    return top


def pointer_click_at(d, x, y, fallback_css=None):
    """Real pointer click at viewport coords via the Actions API.
    Fallback (only when /actions is down): d.click on fallback_css."""
    if not ACTIONS_OK:
        if fallback_css is None:
            raise RuntimeError("pointer_click_at fallback needs css")
        d.click(fallback_css)
        print("[fallback] pointer_click_at used d.click", flush=True)
        return ("fallback-click", fallback_css)
    xi, yi = int(round(x)), int(round(y))
    payload = {"actions": [{
        "type": "pointer", "id": "mouse",
        "parameters": {"pointerType": "mouse"},
        "actions": [
            {"type": "pointerMove", "duration": 0, "x": xi, "y": yi,
             "origin": "viewport"},
            {"type": "pointerDown", "button": 0},
            {"type": "pointerUp", "button": 0},
        ]}]}
    _actions_post(d, payload)
    _actions_release(d)
    return (xi, yi)


def click_nth(d, js_expr):
    """Click the element located by JS index at its rect center.
    Scrolls into view first, re-reads the rect after scrolling, checks
    elementFromPoint at the center before moving the pointer."""
    if not ACTIONS_OK:
        d.eval("(" + js_expr + ").click(); return 'fallback-js-click';")
        print("[fallback] click_nth used JS el.click (degraded, not a "
              "real pointer click)", flush=True)
        return {"fallback": "js-click"}
    d.eval("const el=(" + js_expr + ");"
           "if (el) el.scrollIntoView({block: 'center'});")
    r = _rect_of(d, js_expr)
    cx = int(round(r["x"] + r["w"] / 2))
    cy = int(round(r["y"] + r["h"] / 2))
    top = _probe_point(d, cx, cy)
    pointer_click_at(d, cx, cy)
    return {"center": [cx, cy], "top": top}


def dblclick_el(d, js_expr, fallback_css=None):
    """Real double-click at the element's rect center, one Actions call:
    move, down, up, pause 50 ms, down, up. Scrolls into view first,
    re-reads the rect after scrolling, checks elementFromPoint.
    Fallback (only when /actions is down): two Marionette element
    clicks via dblclick_fallback."""
    if not ACTIONS_OK:
        if fallback_css is None:
            raise RuntimeError("dblclick_el fallback needs css")
        return dblclick_fallback(d, fallback_css)
    d.eval("const el=(" + js_expr + ");"
           "if (el) el.scrollIntoView({block: 'center'});")
    r = _rect_of(d, js_expr)
    cx = int(round(r["x"] + r["w"] / 2))
    cy = int(round(r["y"] + r["h"] / 2))
    top = _probe_point(d, cx, cy)
    payload = {"actions": [{
        "type": "pointer", "id": "mouse",
        "parameters": {"pointerType": "mouse"},
        "actions": [
            {"type": "pointerMove", "duration": 0, "x": cx, "y": cy,
             "origin": "viewport"},
            {"type": "pointerDown", "button": 0},
            {"type": "pointerUp", "button": 0},
            {"type": "pause", "duration": 50},
            {"type": "pointerDown", "button": 0},
            {"type": "pointerUp", "button": 0},
        ]}]}
    _actions_post(d, payload)
    _actions_release(d)
    return {"center": [cx, cy], "top": top}


def dblclick_fallback(d, css):
    """Fallback when /actions is unavailable: two Marionette element
    clicks back to back. NOT a proven dblclick: if the fixture's
    dblclick handler does not fire, the test fails and the failure is
    recorded as input-path degradation, never as a fixture failure."""
    d.click(css)
    d.click(css)
    return "dblclick-fallback-two-clicks"


def poll_effect(d, js_cond, timeout=5.0):
    """Poll a JS condition every 50 ms up to timeout seconds (mirror of
    clone1 t09 verify polling). Returns True when seen."""
    deadline = time.perf_counter() + timeout
    while time.perf_counter() < deadline:
        try:
            if d.eval(f"return !!({js_cond})"):
                return True
        except Exception:
            pass
        time.sleep(0.05)
    return False


def type_empty(d, css):
    """Empty a text input the way the empty steps need: if preflight
    proved Marionette /clear fires input, type_text('') is faithful;
    otherwise clear_search (JS set + input event)."""
    if CLEAR_FIRES_INPUT:
        d.type_text(css, "")
    else:
        clear_search(d, css)
    return "emptied"


def _wait_handles(d, n, timeout=10):
    deadline = time.perf_counter() + timeout
    while time.perf_counter() < deadline:
        if len(d.handles()) >= n:
            return True
        time.sleep(0.1)
    raise RuntimeError(f"only {len(d.handles())} handles, expected >= {n}")


def _wait_handles_gone(d, handle, timeout=10):
    deadline = time.perf_counter() + timeout
    while time.perf_counter() < deadline:
        if handle not in d.handles():
            return True
        time.sleep(0.1)
    raise RuntimeError(f"handle {handle[:8]} still present after close")


def open_test(r, d, url):
    """Open a fixture with the Y4d ladder. Order pinned: new_tab(url),
    clear local+session storage, refresh(), ensure_visible. On a swap,
    reload the fixture on the new tab and ensure again (one final fresh
    tab before finalising INFRA), mirroring open_fixture. The swapped
    tab is appended to opened_tabs so session cleanup closes it."""
    tab = r.step("open fixture", "goto",
                 lambda: d.new_tab(url, allow_hidden=True))
    r.step("clear storage + reload", "eval",
           lambda: (d.eval("localStorage.clear(); sessionStorage.clear();"
                           "return 'cleared';"),
                    d.refresh(allow_hidden=True)))
    ok, swapped = r.step("ensure visible", "diagnose",
                         lambda: ensure_visible(d, r))
    if swapped:
        if r.tab not in d.opened_tabs:
            d.opened_tabs.append(r.tab)
        d.switch(r.tab)
        r.step("open fixture on rebootstrap tab", "goto",
               lambda: d.goto(url, allow_hidden=True))
        r.step("clear storage + reload on rebootstrap tab", "eval",
               lambda: (d.eval("localStorage.clear(); "
                               "sessionStorage.clear(); return 'cleared';"),
                        d.refresh(allow_hidden=True)))
        ok, swapped2 = r.step("ensure visible on rebootstrap tab",
                              "diagnose",
                              lambda: ensure_visible(d, r))
        if swapped2 or not ok:
            # One more fresh tab before finalising INFRA (open_fixture
            # pattern, run_agyq2.py L525-551): a stall that hides the
            # rebootstrap fixture load is not a final verdict until one
            # more fresh tab has been tried (redteam 2 H3).
            try:
                r.tab = rebootstrap_tab(
                    d, r.base, deadline=time.perf_counter() + 8.0)
            except Exception as exc:
                raise RuntimeError(
                    f"INFRA: hidden-body, final fresh tab failed: {exc}")
            if r.tab not in d.opened_tabs:
                d.opened_tabs.append(r.tab)
            d.switch(r.tab)
            r.step("open fixture on final tab", "goto",
                   lambda: d.goto(url, allow_hidden=True))
            r.step("clear storage + reload on final tab", "eval",
                   lambda: (d.eval("localStorage.clear(); "
                                   "sessionStorage.clear();"
                                   "return 'cleared';"),
                            d.refresh(allow_hidden=True)))
            ok, _swapped3 = r.step("ensure visible on final tab",
                                   "diagnose",
                                   lambda: ensure_visible(d, r,
                                                          allow_swap=False))
            if not ok:
                raise RuntimeError(
                    "INFRA: hidden-body after final fresh tab; cannot "
                    "drive")
    if not ok:
        raise RuntimeError(
            "INFRA: hidden-body on test tab after recovery ladder")
    vis = r.step("check body visible", "eval", lambda: d.visible("body"))
    r.check("body renders visible", vis is True, str(vis))
    # Redteam 2 H1: on a swap ensure_visible sets r.tab to the new tab;
    # returning the old handle would send every later switch in t09 to
    # the old hidden tab. Return the live handle.
    return r.tab if swapped else tab


def reload_visible(r, d, url):
    """Reload the fixture mid-test (t07/t08 reload steps) with the
    ladder. On a swap, the fixture is reloaded on the new tab; all
    state at a reload step is persisted in localStorage, so the
    reloaded fixture is equivalent. Returns no handle (redteam 2 H1
    audit): the current tab is always r.tab after ensure_visible, and
    no caller holds a handle across this call."""
    r.step("reload", "eval", lambda: d.refresh(allow_hidden=True))
    ok, swapped = r.step("ensure visible after reload", "diagnose",
                         lambda: ensure_visible(d, r))
    if swapped:
        if r.tab not in d.opened_tabs:
            d.opened_tabs.append(r.tab)
        d.switch(r.tab)
        r.step("open fixture on rebootstrap tab after reload", "goto",
               lambda: d.goto(url, allow_hidden=True))
        ok, _ = r.step("ensure visible on rebootstrap tab",
                       "diagnose",
                       lambda: ensure_visible(d, r, allow_swap=False))
    if not ok:
        raise RuntimeError("INFRA: hidden-body after reload")
    return True

# ---------------- clone1-batch3 tests (b3-t01..b3-t10) ----------------

def _items(d):
    return d.eval("return [...document.querySelectorAll('#list .item')]"
                  ".map(e => e.dataset.name)")


def run_b3_t01(r, d):
    url = r.base + "/clone1-batch3/t01-terminal/fixture.html"
    open_test(r, d, url)

    def run_cmd(text):
        d.click("#cmd")
        d.type_text("#cmd", text)
        active = d.eval("return document.activeElement.id")
        if active != "cmd":
            raise RuntimeError(f"focus lost before Enter: {active}")
        press_keys(d, [KEY_ENTER], css="#cmd")

    out = lambda: d.text("#output")  # noqa: E731
    prompt = lambda: d.text("#prompt")  # noqa: E731
    r.check("initial prompt", prompt() == "/home/demo $", prompt())
    r.step("run help", "type", lambda: run_cmd("help"))
    r.check("help output", "Available commands" in out(), out()[:80])
    r.step("run echo", "type", lambda: run_cmd("echo hello world"))
    r.check("echo output", "hello world" in out(), out()[:80])
    r.step("run ls", "type", lambda: run_cmd("ls"))
    ls_out = out()
    for item in ["readme.txt", "notes.txt", "docs"]:
        r.check(f"ls has {item}", item in ls_out, ls_out[:120])
    r.step("run pwd", "type", lambda: run_cmd("pwd"))
    r.check("pwd output", "/home/demo" in out(), out()[:80])
    r.step("run cd docs", "type", lambda: run_cmd("cd docs"))
    r.check("prompt after cd docs", prompt() == "/home/demo/docs $",
            prompt())
    r.step("run ls in docs", "type", lambda: run_cmd("ls"))
    r.check("ls in docs has guide.txt", "guide.txt" in out(), out()[:80])
    r.step("run cat guide", "type", lambda: run_cmd("cat guide.txt"))
    r.check("cat guide", "Welcome to the docs" in out(), out()[:80])
    r.step("run cat missing", "type", lambda: run_cmd("cat missing.txt"))
    r.check("cat missing error",
            "cat: No such file: missing.txt" in out(), out()[:120])
    r.step("run cd ..", "type", lambda: run_cmd("cd .."))
    r.check("prompt after cd ..", prompt() == "/home/demo $", prompt())
    r.step("run cd nowhere", "type", lambda: run_cmd("cd nowhere"))
    r.check("cd bad dir error",
            "cd: No such directory: nowhere" in out(), out()[:120])
    r.step("run cat docs", "type", lambda: run_cmd("cat docs"))
    r.check("cat directory error", "cat: docs is a directory" in out(),
            out()[:120])
    r.step("run history", "type", lambda: run_cmd("history"))
    hist_out = out()
    for item in ["echo hello world", "cd docs", "cat docs"]:
        r.check(f"history has {item}", item in hist_out, hist_out[:200])
    r.details["historyLines"] = len(
        [l for l in hist_out.split("\n") if l.strip()])
    r.step("click cmd + ArrowUp", "key",
           lambda: (d.click("#cmd"),
                    press_keys(d, [KEY_ARROW_UP], css="#cmd"))[1])
    recalled = r.step("read recalled", "value", lambda: d.value("#cmd"))
    r.check("ArrowUp recalled history", recalled == "history", recalled)
    r.step("run recalled history", "key",
           lambda: press_keys(d, [KEY_ENTER], css="#cmd"))
    r.check("recalled history ran", "history" in out(), out()[:80])
    r.step("run frobnicate", "type", lambda: run_cmd("frobnicate"))
    r.check("unknown command error",
            "command not found: frobnicate" in out(), out()[:120])
    r.step("run clear", "type", lambda: run_cmd("clear"))
    r.check("clear emptied output", out().strip() == "", out()[:80])
    r.step("run pwd after clear", "type", lambda: run_cmd("pwd"))
    r.check("pwd after clear", "/home/demo" in out(), out()[:80])
    r.check("prompt after clear", prompt() == "/home/demo $", prompt())
    r.step("run echo final", "type", lambda: run_cmd("echo final check"))
    r.check("echo after clear", "final check" in out(), out()[:80])
    r.details["finalOutputLines"] = r.step(
        "count output lines", "eval",
        lambda: d.eval(
            "return document.querySelectorAll('#output .line').length"))


def run_b3_t02(r, d):
    url = r.base + "/clone1-batch3/t02-spreadsheet/fixture.html"
    open_test(r, d, url)
    val = lambda cell: d.value("#cell-" + cell)  # noqa: E731

    def expect(cell, wanted, what):
        got = val(cell)
        r.check(what, got == wanted, f"{cell} is {got!r}, want {wanted!r}")
        if got == wanted:
            r.details[cell] = got

    r.step("set A1 10", "type", lambda: d.type_text("#cell-A1", "10"))
    r.step("set A2 20", "type", lambda: d.type_text("#cell-A2", "20"))
    r.step("set A3 30", "type", lambda: d.type_text("#cell-A3", "30"))
    r.step("set C1 SUM", "type",
           lambda: d.type_text("#cell-C1", "=SUM(A1:A3)"))
    expect("C1", "60", "SUM after first fill")
    r.step("set C2 AVERAGE", "type",
           lambda: d.type_text("#cell-C2", "=AVERAGE(A1:A3)"))
    expect("C2", "20", "AVERAGE after first fill")
    r.step("set B1 2", "type", lambda: d.type_text("#cell-B1", "2"))
    r.step("set D1 multiply", "type",
           lambda: d.type_text("#cell-D1", "=A1*B1"))
    expect("D1", "20", "multiply after B1 set")
    r.step("set A1 40", "type", lambda: d.type_text("#cell-A1", "40"))
    expect("C1", "90", "SUM after A1 edit")
    expect("C2", "30", "AVERAGE after A1 edit")
    expect("D1", "80", "multiply after A1 edit")
    r.step("set B2 add", "type",
           lambda: d.type_text("#cell-B2", "=A1+A2"))
    expect("B2", "60", "addition formula")
    r.step("set D4 chained", "type",
           lambda: d.type_text("#cell-D4", "=C1/2"))
    expect("D4", "45", "chained formula over C1")
    r.step("set D2 unknown fn", "type",
           lambda: d.type_text("#cell-D2", "=FOO(1)"))
    expect("D2", "#ERR", "unknown function")
    r.step("set D3 out of grid", "type",
           lambda: d.type_text("#cell-D3", "=A9"))
    expect("D3", "#ERR", "reference outside the grid")
    r.step("set A5 hello", "type", lambda: d.type_text("#cell-A5", "hello"))
    r.step("set C3 SUM text", "type",
           lambda: d.type_text("#cell-C3", "=SUM(A1:A5)"))
    expect("C3", "90", "SUM ignores text cell")
    r.step("set A4 5", "type", lambda: d.type_text("#cell-A4", "5"))
    expect("C3", "95", "SUM after A4 added")
    expect("C1", "90", "SUM range still correct after A4")
    r.step("clear B1", "type", lambda: type_empty(d, "#cell-B1"))
    expect("D1", "0", "multiply by cleared cell is 0")
    r.step("set A6 2.5", "type", lambda: d.type_text("#cell-A6", "2.5"))
    r.step("set C4 decimal", "type",
           lambda: d.type_text("#cell-C4", "=A6*2"))
    expect("C4", "5", "decimal multiply")
    r.step("set D5 division", "type",
           lambda: d.type_text("#cell-D5", "=A3/A2"))
    expect("D5", "1.5", "division")
    r.step("set D6 div zero", "type",
           lambda: d.type_text("#cell-D6", "=A3/0"))
    expect("D6", "#ERR", "division by zero")
    r.step("set A3 10", "type", lambda: d.type_text("#cell-A3", "10"))
    expect("C1", "70", "SUM after A3 edit")
    expect("D5", "0.5", "division after A3 edit")
    status = r.step("read status", "text", lambda: d.text("#status"))
    r.check("status", status == "Recalculated.", status)


def run_b3_t03(r, d):
    url = r.base + "/clone1-batch3/t03-video-call/fixture.html"
    open_test(r, d, url)

    def expect_text(sel, wanted, what):
        got = (d.text(sel) or "").strip()
        r.check(what, got == wanted, f"got {got!r}, want {wanted!r}")

    expect_text("#status", "Not in a call.", "initial status")
    r.check("lobby visible", d.visible("#lobby") is True, "")
    r.check("call hidden before join", d.visible("#call") is False, "")
    r.step("click join", "click", lambda: d.click("#join-btn"))
    expect_text("#status", "In call: Weekly sync", "status after join")
    r.check("call visible after join", d.visible("#call") is True, "")
    expect_text("#participant-count", "Participants: 3",
                "initial participants")
    r.step("click mute", "click", lambda: d.click("#mute-btn"))
    expect_text("#tile-you .mic-state", "Muted", "mic after mute")
    expect_text("#mute-btn", "Unmute", "mute button after mute")
    r.step("click unmute", "click", lambda: d.click("#mute-btn"))
    expect_text("#tile-you .mic-state", "Live", "mic after unmute")
    expect_text("#mute-btn", "Mute", "mute button after unmute")
    r.step("click cam off", "click", lambda: d.click("#cam-btn"))
    expect_text("#tile-you .cam-state", "Camera off", "camera after off")
    cam_class = r.step("read tile class", "eval",
                       lambda: d.eval(
                           "return document.querySelector('#tile-you')"
                           ".getAttribute('class')"))
    r.check("tile has camera-off class", "camera-off" in (cam_class or ""),
            cam_class)
    r.step("click cam on", "click", lambda: d.click("#cam-btn"))
    expect_text("#tile-you .cam-state", "Camera on", "camera after on")
    r.step("click raise hand", "click", lambda: d.click("#hand-btn"))
    expect_text("#hand-count", "Hands raised: 1", "hand count after raise")
    expect_text("#hand-btn", "Lower hand", "hand button after raise")
    r.step("click lower hand", "click", lambda: d.click("#hand-btn"))
    expect_text("#hand-count", "Hands raised: 0", "hand count after lower")
    r.step("type chat 1", "type",
           lambda: d.type_text("#chat-input", "Hello team"))
    r.step("send chat 1", "click", lambda: d.click("#chat-send"))
    r.step("type chat 2", "type",
           lambda: d.type_text("#chat-input",
                               "Can we start with item one?"))
    r.step("send chat 2", "click", lambda: d.click("#chat-send"))
    chat = r.step("read chat log", "text", lambda: d.text("#chat-log"))
    r.check("first chat message", "You: Hello team" in chat, chat[:120])
    r.check("second chat message",
            "You: Can we start with item one?" in chat, chat[:160])
    r.details["chatMessages"] = r.step(
        "count chat messages", "eval",
        lambda: d.eval(
            "return document.querySelectorAll('#chat-log .chat-msg').length"))
    r.step("click share", "click", lambda: d.click("#share-btn"))
    expect_text("#share-state", "Sharing screen.", "share after start")
    r.check("screen tile present", d.visible("#tile-screen") is True, "")
    expect_text("#participant-count", "Participants: 4",
                "participants while sharing")
    r.step("click stop share", "click", lambda: d.click("#share-btn"))
    expect_text("#share-state", "Not sharing.", "share after stop")
    gone = r.step("check screen tile gone", "eval",
                  lambda: d.eval(
                      "return document.querySelector('#tile-screen')"))
    r.check("screen tile absent after stop", gone is None, str(gone))
    r.step("click invite", "click", lambda: d.click("#invite-btn"))
    expect_text("#participant-count", "Participants: 4",
                "participants after invite")
    r.check("Cara tile present", d.visible("#tile-cara") is True, "")
    r.step("remove Cara", "click",
           lambda: d.click("#tile-cara .remove-btn"))
    expect_text("#participant-count", "Participants: 3",
                "participants after remove")
    gone = r.step("check Cara gone", "eval",
                  lambda: d.eval(
                      "return document.querySelector('#tile-cara')"))
    r.check("Cara tile absent", gone is None, str(gone))
    r.step("click leave", "click", lambda: d.click("#leave-btn"))
    expect_text("#status", "Left the call.", "status after leave")
    r.check("lobby visible after leave", d.visible("#lobby") is True, "")
    expect_text("#join-btn", "Rejoin call", "join label after leave")
    r.step("click rejoin", "click", lambda: d.click("#join-btn"))
    expect_text("#status", "In call: Weekly sync", "status after rejoin")
    expect_text("#participant-count", "Participants: 3",
                "participants after rejoin")
    r.step("click leave again", "click", lambda: d.click("#leave-btn"))
    expect_text("#status", "Left the call.", "status after second leave")


def run_b3_t04(r, d):
    url = r.base + "/clone1-batch3/t04-email-client/fixture.html"
    open_test(r, d, url)

    def expect_text(sel, wanted, what):
        got = (d.text(sel) or "").strip()
        r.check(what, got == wanted, f"got {got!r}, want {wanted!r}")

    def count(sel):
        return d.eval(
            f"return document.querySelectorAll('{sel}').length")

    expect_text("#inbox-count", "3", "initial inbox count")
    expect_text("#unread-count", "2", "initial unread count")
    r.step("search invoice", "type",
           lambda: d.type_text("#search", "invoice"))
    n = r.step("count search invoice", "eval",
               lambda: count("#list .msg"))
    r.check("search invoice shows 1", n == 1, str(n))
    lst = r.step("read list", "text", lambda: d.text("#list"))
    r.check("search shows invoice", "Your invoice for June" in lst,
            lst[:120])
    r.step("clear search", "type", lambda: type_empty(d, "#search"))
    n = r.step("count after clear", "eval", lambda: count("#list .msg"))
    r.check("clearing search shows 3", n == 3, str(n))
    r.step("open first message", "click",
           lambda: click_nth(
               d, "document.querySelectorAll('#list .msg')[0]"))
    expect_text("#reader-subject", "Your invoice for June",
                "reader subject")
    expect_text("#reader-body",
                "Invoice INV-1001 is attached. Total 42.00.", "reader body")
    expect_text("#unread-count", "1", "unread after opening one")
    r.step("click reader back", "click", lambda: d.click("#reader-back"))
    r.step("star second message", "click",
           lambda: click_nth(
               d, "document.querySelectorAll('#list .msg')[1]"
                  ".querySelector('.star')"))
    expect_text("#starred-count", "1", "starred after starring")
    r.step("click compose", "click", lambda: d.click("#compose-btn"))
    r.step("fill to", "type",
           lambda: d.type_text("#to", "team@example.org"))
    r.step("fill subject", "type",
           lambda: d.type_text("#subject", "Demo report"))
    r.step("fill body", "type",
           lambda: d.type_text("#body", "Hello, here is the demo report."))
    r.step("click send", "click", lambda: d.click("#send-btn"))
    expect_text("#toast", "Message sent.", "toast after send")
    expect_text("#sent-count", "1", "sent count after send")
    r.step("open sent folder", "click", lambda: d.click("#folder-sent"))
    expect_text("#folder-title", "Sent", "folder title Sent")
    n = r.step("count sent", "eval", lambda: count("#list .msg"))
    r.check("sent folder shows 1", n == 1, str(n))
    lst = r.step("read sent list", "text", lambda: d.text("#list"))
    r.check("sent subject present", "Demo report" in lst, lst[:120])
    r.step("open inbox folder", "click", lambda: d.click("#folder-inbox"))
    r.step("open third message", "click",
           lambda: click_nth(
               d, "document.querySelectorAll('#list .msg')[2]"))
    expect_text("#reader-subject", "System maintenance Sunday",
                "reader subject third message")
    r.step("click reader delete", "click",
           lambda: d.click("#reader-delete"))
    expect_text("#inbox-count", "2", "inbox after delete")
    expect_text("#trash-count", "1", "trash after delete")
    r.step("open trash folder", "click", lambda: d.click("#folder-trash"))
    lst = r.step("read trash list", "text", lambda: d.text("#list"))
    r.check("deleted message in trash",
            "System maintenance Sunday" in lst, lst[:120])
    r.step("open inbox folder again", "click",
           lambda: d.click("#folder-inbox"))
    r.step("click mark all read", "click",
           lambda: d.click("#mark-all-read"))
    expect_text("#unread-count", "0", "unread after mark all read")
    r.step("search nomatch", "type",
           lambda: d.type_text("#search", "nomatch"))
    n = r.step("count nomatch", "eval", lambda: count("#list .msg"))
    r.check("search nomatch shows 0", n == 0, str(n))
    r.check("empty state visible", d.visible("#empty") is True, "")
    r.step("clear search again", "type", lambda: type_empty(d, "#search"))
    r.step("open starred folder", "click",
           lambda: d.click("#folder-starred"))
    n = r.step("count starred", "eval", lambda: count("#list .msg"))
    r.check("starred folder shows 1", n == 1, str(n))
    lst = r.step("read starred list", "text", lambda: d.text("#list"))
    r.check("starred message present", "Weekly sync notes" in lst,
            lst[:120])
    r.step("unstar the message", "click",
           lambda: click_nth(
               d, "document.querySelectorAll('#list .msg')[0]"
                  ".querySelector('.star')"))
    expect_text("#starred-count", "0", "starred after unstarring")
    r.step("open inbox folder final", "click",
           lambda: d.click("#folder-inbox"))
    expect_text("#folder-title", "Inbox", "folder title Inbox")
    r.details["finalInbox"] = r.step("read inbox count", "text",
                                     lambda: d.text("#inbox-count"))


def run_b3_t05(r, d):
    url = r.base + "/clone1-batch3/t05-file-manager/fixture.html"
    open_test(r, d, url)

    def expect_items(wanted, what):
        got = _items(d)
        r.check(what, got == wanted,
                f"got {got}, want {wanted}")

    def expect_text(sel, wanted, what):
        got = (d.text(sel) or "").strip()
        r.check(what, got == wanted, f"got {got!r}, want {wanted!r}")

    def dialog_open(prefill, what):
        vis = d.visible("#rename-dialog")
        pre = d.value("#rename-input")
        r.check(what + " dialog visible", vis is True, str(vis))
        r.check(what + " prefill", pre == prefill,
                f"prefill is {pre!r}, want {prefill!r}")

    def dialog_hidden(what):
        vis = d.visible("#rename-dialog")
        r.check(what + " dialog hidden", vis is False, str(vis))

    expect_items(["budget.csv", "notes.txt", "photo.jpg", "video.mp4"],
                 "initial Home order")
    expect_text("#status", "Home: 4 items", "initial status")
    r.step("sort size-desc", "select",
           lambda: select_option(d, "#sort", "size-desc"))
    first = r.step("read first after size-desc", "eval",
                   lambda: _items(d)[0])
    r.check("size-desc first is video.mp4", first == "video.mp4", first)
    r.step("sort name", "select",
           lambda: select_option(d, "#sort", "name"))
    first = r.step("read first after name", "eval", lambda: _items(d)[0])
    r.check("name first is budget.csv", first == "budget.csv", first)
    r.step("sort size-asc", "select",
           lambda: select_option(d, "#sort", "size-asc"))
    first = r.step("read first after size-asc", "eval",
                   lambda: _items(d)[0])
    r.check("size-asc first is notes.txt", first == "notes.txt", first)
    r.step("sort name again", "select",
           lambda: select_option(d, "#sort", "name"))
    r.step("search photo", "type",
           lambda: d.type_text("#search", "photo"))
    expect_items(["photo.jpg"], "search photo")
    r.step("clear search", "type", lambda: type_empty(d, "#search"))
    expect_items(["budget.csv", "notes.txt", "photo.jpg", "video.mp4"],
                 "after clearing search")
    r.step("click new folder", "click", lambda: d.click("#new-folder-btn"))
    expect_items(["Archive", "budget.csv", "notes.txt", "photo.jpg",
                  "video.mp4"], "after new folder")
    tree = r.step("check tree Archive", "eval",
                  lambda: d.eval(
                      "return document.querySelector('#tree-archive')"))
    r.check("tree button for Archive present", tree is not None, str(tree))
    r.step("dblclick Archive", "click",
           lambda: dblclick_el(
               d, "document.querySelector('#list .item[data-name=\"Archive\"]')",
               fallback_css='#list .item[data-name="Archive"]'))
    expect_text("#crumbs", "Archive", "crumbs inside Archive")
    r.check("empty state in Archive", d.visible("#empty") is True, "")
    expect_text("#status", "Archive: 0 items", "Archive status")
    r.step("click tree home", "click", lambda: d.click("#tree-home"))
    expect_text("#crumbs", "Home", "crumbs back in Home")
    r.step("select budget.csv", "click",
           lambda: d.click('#list .item[data-name="budget.csv"]'))
    r.step("click rename", "click", lambda: d.click("#rename-btn"))
    r.step("check dialog for cancel", "eval",
           lambda: dialog_open("budget.csv", "rename dialog for cancel"))
    items = _items(d)
    r.check("budget.csv present while dialog open",
            "budget.csv" in items, str(items))
    r.check("budget2.csv absent before rename",
            "budget2.csv" not in items, str(items))
    r.step("type budget2.csv", "type",
           lambda: d.type_text("#rename-input", "budget2.csv"))
    r.step("click rename cancel", "click",
           lambda: d.click("#rename-cancel"))
    r.step("check dialog hidden after cancel", "eval",
           lambda: dialog_hidden("after rename cancel"))
    items = _items(d)
    r.check("budget.csv present after cancel", "budget.csv" in items,
            str(items))
    r.check("budget2.csv absent after cancel", "budget2.csv" not in items,
            str(items))
    r.step("click rename again", "click", lambda: d.click("#rename-btn"))
    r.step("check dialog for empty", "eval",
           lambda: dialog_open("budget.csv", "rename dialog for empty"))
    r.step("type empty name", "type",
           lambda: type_empty(d, "#rename-input"))
    r.step("click rename save empty", "click",
           lambda: d.click("#rename-save"))
    items = _items(d)
    r.check("budget.csv present after empty rename",
            "budget.csv" in items, str(items))
    r.check("dialog open on empty name",
            d.visible("#rename-dialog") is True, "")
    r.check("empty error shown",
            d.visible("#rename-error") is True, "")
    r.step("click rename cancel after empty", "click",
           lambda: d.click("#rename-cancel"))
    r.step("check dialog hidden after empty cancel", "eval",
           lambda: dialog_hidden("after cancelling the empty rename"))
    r.step("select notes.txt", "click",
           lambda: d.click('#list .item[data-name="notes.txt"]'))
    r.step("click rename notes", "click", lambda: d.click("#rename-btn"))
    r.step("check dialog for notes", "eval",
           lambda: dialog_open("notes.txt", "rename dialog for notes.txt"))
    items = _items(d)
    r.check("notes.txt present while dialog open", "notes.txt" in items,
            str(items))
    r.check("field-notes-7.txt absent before rename",
            "field-notes-7.txt" not in items, str(items))
    r.step("type field-notes-7.txt", "type",
           lambda: d.type_text("#rename-input", "field-notes-7.txt"))
    r.step("click rename save", "click", lambda: d.click("#rename-save"))
    r.step("check dialog hidden after rename", "eval",
           lambda: dialog_hidden("after file rename"))
    items = _items(d)
    r.check("notes.txt gone after rename", "notes.txt" not in items,
            str(items))
    r.check("field-notes-7.txt present after rename",
            "field-notes-7.txt" in items, str(items))
    r.step("select photo.jpg", "click",
           lambda: d.click('#list .item[data-name="photo.jpg"]'))
    r.step("click delete", "click", lambda: d.click("#delete-btn"))
    r.check("delete confirm shown", d.visible("#confirm") is True, "")
    confirm = r.step("read confirm text", "text",
                     lambda: d.text("#confirm-text"))
    r.check("confirm text", "Delete photo.jpg?" in confirm, confirm)
    r.step("click confirm no", "click", lambda: d.click("#confirm-no"))
    n = r.step("count after cancelled delete", "eval",
               lambda: d.eval(
                   "return document.querySelectorAll('#list .item').length"))
    r.check("cancelled delete kept 5 items", n == 5, str(n))
    r.step("select photo.jpg again", "click",
           lambda: d.click('#list .item[data-name="photo.jpg"]'))
    r.step("click delete again", "click", lambda: d.click("#delete-btn"))
    r.step("click confirm yes", "click", lambda: d.click("#confirm-yes"))
    expect_items(["Archive", "budget.csv", "field-notes-7.txt",
                  "video.mp4"], "after delete")
    r.step("select video.mp4", "click",
           lambda: d.click('#list .item[data-name="video.mp4"]'))
    r.step("click move", "click", lambda: d.click("#move-btn"))
    r.step("select move target Archive", "select",
           lambda: select_option(d, "#move-target", "Archive"))
    r.step("click move ok", "click", lambda: d.click("#move-ok"))
    expect_items(["Archive", "budget.csv", "field-notes-7.txt"],
                 "Home after moving video out")
    r.step("click tree archive", "click", lambda: d.click("#tree-archive"))
    expect_items(["video.mp4"], "Archive after moving video in")
    r.step("click tree home", "click", lambda: d.click("#tree-home"))
    r.step("select Archive", "click",
           lambda: d.click('#list .item[data-name="Archive"]'))
    r.step("click rename folder", "click", lambda: d.click("#rename-btn"))
    r.step("check dialog for folder", "eval",
           lambda: dialog_open("Archive", "rename dialog for folder"))
    items = _items(d)
    r.check("Archive present while dialog open", "Archive" in items,
            str(items))
    r.check("Old Files 2026 absent before rename",
            "Old Files 2026" not in items, str(items))
    r.step("type Old Files 2026 padded", "type",
           lambda: d.type_text("#rename-input", "  Old Files 2026  "))
    r.step("click rename save folder", "click",
           lambda: d.click("#rename-save"))
    r.step("check dialog hidden after folder rename", "eval",
           lambda: dialog_hidden("after folder rename"))
    items = _items(d)
    r.check("Old Files 2026 present after rename",
            "Old Files 2026" in items, str(items))
    r.check("Archive gone after rename", "Archive" not in items,
            str(items))
    tree = r.step("check tree Old Files 2026", "eval",
                  lambda: d.eval(
                      "return document.querySelector('#tree-old-files-2026')"))
    r.check("tree button for Old Files 2026 present", tree is not None,
            str(tree))
    tree_text = r.step("read tree button text", "text",
                       lambda: d.text("#tree-old-files-2026"))
    r.check("tree button text", tree_text.strip() == "Old Files 2026",
            tree_text)
    r.step("click tree Old Files 2026", "click",
           lambda: d.click("#tree-old-files-2026"))
    expect_text("#crumbs", "Old Files 2026",
                "crumbs inside Old Files 2026")
    expect_items(["video.mp4"],
                 "Old Files 2026 still holds video.mp4 after rename")
    r.step("select video.mp4 in folder", "click",
           lambda: d.click('#list .item[data-name="video.mp4"]'))
    r.step("click move back", "click", lambda: d.click("#move-btn"))
    r.step("select move target Home", "select",
           lambda: select_option(d, "#move-target", "Home"))
    r.step("click move ok back", "click", lambda: d.click("#move-ok"))
    n = r.step("count in folder after move back", "eval",
               lambda: d.eval(
                   "return document.querySelectorAll('#list .item').length"))
    r.check("Old Files 2026 empty after moving video back", n == 0, str(n))
    r.step("click tree home final", "click", lambda: d.click("#tree-home"))
    expect_items(["budget.csv", "field-notes-7.txt", "Old Files 2026",
                  "video.mp4"], "Home after moving video back")
    r.step("search 2026", "type",
           lambda: d.type_text("#search", "2026"))
    expect_items(["Old Files 2026"], "search 2026")
    r.step("clear search final", "type", lambda: type_empty(d, "#search"))
    r.step("dblclick Old Files 2026", "click",
           lambda: dblclick_el(
               d, "document.querySelector('#list .item[data-name=\"Old Files 2026\"]')",
               fallback_css='#list .item[data-name="Old Files 2026"]'))
    expect_text("#crumbs", "Old Files 2026",
                "crumbs inside Old Files 2026 final")
    r.check("empty state in Old Files 2026",
            d.visible("#empty") is True, "")
    r.step("click tree home end", "click", lambda: d.click("#tree-home"))
    r.details["finalHome"] = _items(d)

def run_b3_t06(r, d):
    url = r.base + "/clone1-batch3/t06-calendar/fixture.html"
    open_test(r, d, url)

    def expect_text(sel, wanted, what):
        got = (d.text(sel) or "").strip()
        r.check(what, got == wanted, f"got {got!r}, want {wanted!r}")

    def chips_on(day):
        return d.eval(
            f"return [...document.querySelectorAll('.day[data-day=\"{day}\"] .chip')]"
            ".map(e => e.textContent)")

    def add_event(day, title, time):
        d.click(f'.day[data-day="{day}"] .day-num')
        d.type_text("#event-title", title)
        d.type_text("#event-time", time)
        d.click("#save-event")

    expect_text("#month-title", "June 2026", "initial month")
    today_class = r.step("read day 15 class", "eval",
                         lambda: d.eval(
                             "return document.querySelector('.day[data-day=\"15\"]')"
                             ".getAttribute('class')"))
    r.check("day 15 has today highlight", "today" in (today_class or ""),
            today_class)
    r.step("click day 12", "click",
           lambda: d.click('.day[data-day="12"] .day-num'))
    r.check("event form shown", d.visible("#form") is True, "")
    expect_text("#form-day", "June 12, 2026", "form day label")
    r.step("fill Team sync", "type",
           lambda: d.type_text("#event-title", "Team sync"))
    r.step("fill 10:00", "type",
           lambda: d.type_text("#event-time", "10:00"))
    r.step("save first event", "click", lambda: d.click("#save-event"))
    chips = r.step("read day 12 chips", "eval", lambda: chips_on(12))
    r.check("day 12 chips after first event", chips == ["10:00 Team sync"],
            str(chips))
    r.step("add Lunch", "eval", lambda: add_event(12, "Lunch", "12:30"))
    chips = r.step("read day 12 chips again", "eval", lambda: chips_on(12))
    r.check("day 12 chips after second event",
            len(chips) == 2 and "12:30 Lunch" in chips, str(chips))
    r.step("add Deadline", "eval", lambda: add_event(20, "Deadline", "09:00"))
    chips = r.step("read day 20 chips", "eval", lambda: chips_on(20))
    r.check("day 20 chips", chips == ["09:00 Deadline"], str(chips))
    expect_text("#status", "Events: 3", "status after 3 events")
    r.step("open first chip", "click",
           lambda: click_nth(
               d, "document.querySelectorAll('.day[data-day=\"12\"] .chip')[0]"))
    expect_text("#details-title", "Team sync", "details title")
    meta = r.step("read details meta", "text",
                  lambda: d.text("#details-meta"))
    r.check("details meta", "June 12, 2026 at 10:00" in meta, meta)
    r.step("edit time to 11:00", "type",
           lambda: d.type_text("#edit-time", "11:00"))
    r.step("click update", "click", lambda: d.click("#update-event"))
    meta = r.step("read details meta again", "text",
                  lambda: d.text("#details-meta"))
    r.check("details meta updated to 11:00", "at 11:00" in meta, meta)
    chips = r.step("read day 12 chips after edit", "eval",
                   lambda: chips_on(12))
    r.check("chip updated to 11:00", "11:00 Team sync" in chips, str(chips))
    r.step("open second chip", "click",
           lambda: click_nth(
               d, "document.querySelectorAll('.day[data-day=\"12\"] .chip')[1]"))
    expect_text("#details-title", "Lunch", "details title for Lunch")
    r.step("click delete event", "click",
           lambda: d.click("#delete-event"))
    chips = r.step("read day 12 chips after delete", "eval",
                   lambda: chips_on(12))
    r.check("day 12 chips after delete", chips == ["11:00 Team sync"],
            str(chips))
    expect_text("#status", "Events: 2", "status after delete")
    r.step("click next month", "click", lambda: d.click("#next-btn"))
    expect_text("#month-title", "July 2026", "month after next")
    n = r.step("count July chips", "eval",
               lambda: d.eval(
                   "return document.querySelectorAll('.chip').length"))
    r.check("July has no chips", n == 0, str(n))
    r.step("click prev month", "click", lambda: d.click("#prev-btn"))
    expect_text("#month-title", "June 2026", "month after prev")
    n = r.step("count June chips", "eval",
               lambda: d.eval(
                   "return document.querySelectorAll('.chip').length"))
    r.check("June has 2 chips again", n == 2, str(n))
    r.step("click day 5", "click",
           lambda: d.click('.day[data-day="5"] .day-num'))
    r.step("click cancel event", "click",
           lambda: d.click("#cancel-event"))
    chips = r.step("read day 5 chips", "eval", lambda: chips_on(5))
    r.check("day 5 gained no chip after cancel", len(chips) == 0,
            str(chips))
    expect_text("#status", "Events: 2", "status after cancel")
    r.step("add Demo", "eval", lambda: add_event(15, "Demo", "14:00"))
    chips = r.step("read day 15 chips", "eval", lambda: chips_on(15))
    r.check("day 15 chips", chips == ["14:00 Demo"], str(chips))
    expect_text("#status", "Events: 3", "status after Demo")
    r.step("click next twice 1", "click", lambda: d.click("#next-btn"))
    r.step("click next twice 2", "click", lambda: d.click("#next-btn"))
    expect_text("#month-title", "August 2026", "month after two nexts")
    r.step("click today", "click", lambda: d.click("#today-btn"))
    expect_text("#month-title", "June 2026", "month after Today")
    expect_text("#status", "Events: 3", "status after Today")
    r.details["chips"] = r.step(
        "read all chips", "eval",
        lambda: d.eval(
            "return [...document.querySelectorAll('.chip')]"
            ".map(e => e.textContent)"))


def run_b3_t07(r, d):
    url = r.base + "/clone1-batch3/t07-code-editor/fixture.html"
    open_test(r, d, url)

    def expect_text(sel, wanted, what):
        got = (d.text(sel) or "").strip()
        r.check(what, got == wanted, f"got {got!r}, want {wanted!r}")

    def expect_editor(wanted, what):
        got = d.value("#editor")
        r.check(what, got == wanted,
                f"editor is {got!r}, want {wanted!r}")

    def tab_class(f):
        return d.eval(
            f"return document.querySelector('#tabs button[data-file=\"{f}\"]')"
            ".getAttribute('class')")

    expect_editor("2 + 3", "initial main.js content")
    r.step("click run", "click", lambda: d.click("#run-btn"))
    expect_text("#output", "Result: 5", "run 2 + 3")
    r.step("fill 10 * 4", "type", lambda: d.type_text("#editor", "10 * 4"))
    r.step("click run again", "click", lambda: d.click("#run-btn"))
    expect_text("#output", "Result: 40", "run 10 * 4")
    cls = r.step("read main.js tab class", "eval",
                 lambda: tab_class("main.js"))
    r.check("main.js tab dirty after edit", "dirty" in (cls or ""), cls)
    r.step("click save", "click", lambda: d.click("#save-btn"))
    expect_text("#status", "Saved main.js.", "status after save")
    cls = r.step("read main.js tab class after save", "eval",
                 lambda: tab_class("main.js"))
    r.check("main.js tab clean after save", "dirty" not in (cls or ""), cls)
    r.step("reload", "eval", lambda: reload_visible(r, d, url))
    expect_editor("10 * 4", "main.js content after reload")
    r.step("switch to utils.js", "click",
           lambda: d.click('#tabs button[data-file="utils.js"]'))
    expect_editor("7 - 2", "utils.js content")
    r.step("run utils.js", "click", lambda: d.click("#run-btn"))
    expect_text("#output", "Result: 5", "run utils.js")
    r.step("fill 7 - 2 + 100", "type",
           lambda: d.type_text("#editor", "7 - 2 + 100"))
    cls = r.step("read utils.js tab class", "eval",
                 lambda: tab_class("utils.js"))
    r.check("utils.js tab dirty after edit", "dirty" in (cls or ""), cls)
    r.step("switch to main.js", "click",
           lambda: d.click('#tabs button[data-file="main.js"]'))
    expect_editor("10 * 4", "main.js content after tab switch")
    r.step("switch back to utils.js", "click",
           lambda: d.click('#tabs button[data-file="utils.js"]'))
    expect_editor("7 - 2 + 100", "utils.js unsaved edit kept")
    r.step("save utils.js", "click", lambda: d.click("#save-btn"))
    expect_text("#status", "Saved utils.js.", "status after saving utils.js")
    r.step("reload 2", "eval", lambda: reload_visible(r, d, url))
    r.step("switch to utils.js after reload", "click",
           lambda: d.click('#tabs button[data-file="utils.js"]'))
    expect_editor("7 - 2 + 100", "utils.js content after reload")
    r.step("switch to main.js for find", "click",
           lambda: d.click('#tabs button[data-file="main.js"]'))
    r.step("fill find 10", "type",
           lambda: d.type_text("#find-input", "10"))
    r.step("click find", "click", lambda: d.click("#find-btn"))
    expect_text("#find-result", "1 match", "find 10")
    r.step("fill replace 20", "type",
           lambda: d.type_text("#replace-input", "20"))
    r.step("click replace", "click", lambda: d.click("#replace-btn"))
    expect_text("#find-result", "Replaced.", "replace result")
    expect_editor("20 * 4", "editor after replace")
    r.step("run after replace", "click", lambda: d.click("#run-btn"))
    expect_text("#output", "Result: 80", "run after replace")
    r.step("fill find zzz", "type",
           lambda: d.type_text("#find-input", "zzz"))
    r.step("click find zzz", "click", lambda: d.click("#find-btn"))
    expect_text("#find-result", "0 matches", "find missing text")
    r.step("switch to notes.md", "click",
           lambda: d.click('#tabs button[data-file="notes.md"]'))
    r.step("run markdown", "click", lambda: d.click("#run-btn"))
    expect_text("#output", "Error: cannot run a markdown file.",
                "run markdown")
    r.step("fill notes.md", "type",
           lambda: d.type_text(
               "#editor", "# Notes\nRemember to ship the demo.\nShip on Friday."))
    r.step("save notes.md", "click", lambda: d.click("#save-btn"))
    r.step("reload 3", "eval", lambda: reload_visible(r, d, url))
    r.step("switch to notes.md after reload", "click",
           lambda: d.click('#tabs button[data-file="notes.md"]'))
    val = r.step("read notes.md", "value", lambda: d.value("#editor"))
    r.check("notes.md persisted", "Ship on Friday." in (val or ""), val)
    r.step("switch to main.js for error", "click",
           lambda: d.click('#tabs button[data-file="main.js"]'))
    r.step("fill invalid code", "type",
           lambda: d.type_text("#editor", "2 +"))
    r.step("run invalid code", "click", lambda: d.click("#run-btn"))
    err = r.step("read run error", "text", lambda: d.text("#output"))
    r.check("invalid code errors", err.startswith("Error:"), err)
    r.step("fill empty code", "type", lambda: type_empty(d, "#editor"))
    r.step("run empty code", "click", lambda: d.click("#run-btn"))
    err = r.step("read empty error", "text", lambda: d.text("#output"))
    r.check("empty code errors", err.startswith("Error:"), err)
    r.details["lines"] = r.step("read lines", "text",
                                lambda: d.text("#lines"))


def run_b3_t08(r, d):
    url = r.base + "/clone1-batch3/t08-settings-panel/fixture.html"
    open_test(r, d, url)

    def expect_text(sel, wanted, what):
        got = (d.text(sel) or "").strip()
        r.check(what, got == wanted, f"got {got!r}, want {wanted!r}")

    def visible_sections():
        return d.eval(
            "return [...document.querySelectorAll('section')]"
            ".filter(e => e.style.display !== 'none').map(e => e.id)")

    expect_text("#preview-theme", "Light", "initial preview theme")
    expect_text("#volume-value", "50", "initial volume")
    expect_text("#notif-state", "On", "initial notifications state")
    r.step("select dark theme", "select",
           lambda: select_option(d, "#theme", "dark"))
    expect_text("#preview-theme", "Dark", "preview after dark theme")
    body_class = r.step("read body class", "eval",
                        lambda: d.eval(
                            "return document.body.getAttribute('class')"))
    r.check("body has dark class", "dark" in (body_class or ""), body_class)
    r.step("check blue accent", "click",
           lambda: d.click('input[name="accent"][value="blue"]'))
    swatch = r.step("read swatch", "eval",
                    lambda: d.eval(
                        "return document.querySelector('#swatch')"
                        ".style.background"))
    r.check("swatch blue after blue accent", swatch == "blue", swatch)
    r.step("uncheck notif", "click", lambda: d.click("#notif-toggle"))
    expect_text("#notif-state", "Off", "notifications after toggle off")
    r.step("check digest", "click", lambda: d.click("#digest-toggle"))
    expect_text("#digest-state", "On", "digest after toggle on")
    r.step("uncheck privacy", "click", lambda: d.click("#privacy-toggle"))
    expect_text("#privacy-state", "Off", "privacy after toggle off")
    r.step("fill display name", "type",
           lambda: d.type_text("#display-name", "Demo User"))
    r.step("click volume", "click", lambda: d.click("#volume"))
    vol = r.step("read volume after click", "value",
                 lambda: d.value("#volume"))
    r.check("volume 50 after click", vol == "50", str(vol))
    r.step("press Home on volume", "key",
           lambda: press_keys(d, [KEY_HOME], css="#volume"))
    vol = r.step("read volume after Home", "value",
                 lambda: d.value("#volume"))
    r.check("volume 0 after Home", vol == "0", str(vol))
    r.step("press ArrowRight x70", "key",
           lambda: press_keys(d, [KEY_ARROW_RIGHT] * 70, css="#volume"))
    vol = r.step("read volume after arrows", "value",
                 lambda: d.value("#volume"))
    r.check("volume 70 after arrows", vol == "70", str(vol))
    expect_text("#volume-value", "70", "volume value after slider")
    r.step("click save", "click", lambda: d.click("#save-btn"))
    expect_text("#toast", "Settings saved.", "toast after save")
    r.step("reload", "eval", lambda: reload_visible(r, d, url))
    expect_text("#preview-theme", "Dark", "preview theme after reload")
    expect_text("#volume-value", "70", "volume after reload")
    name = r.step("read display name after reload", "value",
                  lambda: d.value("#display-name"))
    r.check("display name persisted", name == "Demo User", name)
    expect_text("#notif-state", "Off", "notifications after reload")
    expect_text("#digest-state", "On", "digest after reload")
    expect_text("#privacy-state", "Off", "privacy after reload")
    blue = r.step("read blue checked", "eval",
                  lambda: d.eval(
                      "return document.querySelector"
                      "('input[name=\"accent\"][value=\"blue\"]'"
                      ").checked"))
    r.check("blue accent persisted", blue is True, str(blue))
    r.step("search theme", "type",
           lambda: d.type_text("#search", "theme"))
    shown = r.step("read visible sections", "eval",
                   lambda: visible_sections())
    r.check("search theme shows appearance only",
            shown == ["section-appearance"], str(shown))
    r.step("clear search", "type", lambda: type_empty(d, "#search"))
    shown = r.step("read visible sections after clear", "eval",
                   lambda: visible_sections())
    r.check("clearing search shows 4 sections", len(shown) == 4, str(shown))
    r.step("search xyz", "type", lambda: d.type_text("#search", "xyz"))
    r.check("no-match visible", d.visible("#no-match") is True, "")
    r.step("clear search again", "type", lambda: type_empty(d, "#search"))
    r.step("click reset", "click", lambda: d.click("#reset-btn"))
    expect_text("#toast", "Settings reset.", "toast after reset")
    expect_text("#preview-theme", "Light", "preview theme after reset")
    expect_text("#volume-value", "50", "volume after reset")
    expect_text("#notif-state", "On", "notifications after reset")
    name = r.step("read display name after reset", "value",
                  lambda: d.value("#display-name"))
    r.check("display name cleared after reset", name == "", name)
    r.step("reload after reset", "eval", lambda: reload_visible(r, d, url))
    expect_text("#preview-theme", "Light", "preview after reload post reset")
    expect_text("#volume-value", "50", "volume after reload post reset")
    notif = r.step("read notif checked", "eval",
                   lambda: d.eval(
                       "return document.querySelector('#notif-toggle')"
                       ".checked"))
    if notif is not True:
        r.step("check notif toggle", "click",
               lambda: d.click("#notif-toggle"))
    r.step("click save again", "click", lambda: d.click("#save-btn"))
    expect_text("#toast", "Settings saved.", "toast after second save")
    r.details["finalTheme"] = r.step("read final theme", "text",
                                     lambda: d.text("#preview-theme"))

def run_b3_t09(r, d):
    url = r.base + "/clone1-batch3/t09-multi-window/fixture.html"
    main_tab = open_test(r, d, url)
    # Live handles() returns EVERY tab/window in the attached Zen, so
    # counts are relative to a baseline captured here, never absolute
    # (redteam D2: check.mjs counts 3/1 run in a fresh Playwright
    # context with only test pages; live there are user tabs too).
    handles_before = r.step("record handle baseline", "eval",
                            lambda: len(d.handles()))

    def title_of(pid):
        return d.eval(
            f"return document.querySelector('.project[data-id=\"{pid}\"] .title')"
            ".textContent")

    def expect_title(pid, wanted, what):
        got = (title_of(pid) or "").strip()
        r.check(what, got == wanted,
                f"project {pid} is {got!r}, want {wanted!r}")

    def open_popup(click_sel):
        before = d.handles()
        d.click(click_sel)
        _wait_handles(d, len(before) + 1)
        popup = [h for h in d.handles() if h not in before][0]
        d.switch(popup)
        d.wait_ready()
        time.sleep(1.0)
        ok, swapped = ensure_visible(d, r, "popup", allow_swap=False)
        if not ok:
            raise RuntimeError("INFRA: hidden-body on popup tab")
        return popup

    def click_and_close(popup, click_sel, verify_js, what):
        # Tolerate a click that raises only when the popup really
        # closed within 2 s (check.mjs clickAndClose tolerance); the
        # verify poll below is the arbiter.
        try:
            d.click(click_sel)
        except Exception as exc:
            if "has been closed" not in str(exc):
                try:
                    _wait_handles_gone(d, popup, 2)
                except Exception:
                    raise exc
        _wait_handles_gone(d, popup, 10)
        d.switch(main_tab)
        ok, _ = ensure_visible(d, r, "main after popup close",
                               allow_swap=False)
        if not ok:
            raise RuntimeError(
                "INFRA: hidden-body on main tab after popup close")
        if verify_js:
            seen = poll_effect(d, verify_js, 5.0)
            r.check(what + " effect seen after popup closed", seen is True,
                    "expected effect not seen after popup closed, "
                    "click may not have landed")

    def title_is(pid, wanted):
        return (f"document.querySelector('.project[data-id=\"{pid}\"] .title')"
                f".textContent.trim() === '{wanted}'")

    def body_is_dark():
        return "document.body.classList.contains('dark')"

    def body_is_light():
        return "!document.body.classList.contains('dark')"

    expect_title("alpha", "Alpha", "initial Alpha title")
    expect_title("beta", "Beta", "initial Beta title")
    expect_title("gamma", "Gamma", "initial Gamma title")
    popup = r.step("open Alpha detail", "click",
                   lambda: open_popup('.project[data-id="alpha"] .detail-btn'))
    pre = r.step("read detail prefill", "value",
                 lambda: d.value("#title-input"))
    r.check("detail prefilled Alpha", pre == "Alpha", pre)
    r.step("fill Alpha v2", "type",
           lambda: d.type_text("#title-input", "Alpha v2"))
    r.step("save Alpha v2", "click",
           lambda: click_and_close(popup, "#save-btn",
                                   title_is("alpha", "Alpha v2"),
                                   "Alpha title after first rename"))
    expect_title("alpha", "Alpha v2", "Alpha title after first rename")
    status = r.step("read status", "text", lambda: d.text("#status"))
    r.check("status after first rename",
            "Renamed alpha to Alpha v2." in status, status)
    popup = r.step("open Alpha detail again", "click",
                   lambda: open_popup('.project[data-id="alpha"] .detail-btn'))
    pre = r.step("read detail prefill again", "value",
                 lambda: d.value("#title-input"))
    r.check("detail prefilled Alpha v2", pre == "Alpha v2", pre)
    r.step("fill Alpha Final", "type",
           lambda: d.type_text("#title-input", "Alpha Final"))
    r.step("save Alpha Final", "click",
           lambda: click_and_close(popup, "#save-btn",
                                   title_is("alpha", "Alpha Final"),
                                   "Alpha title after second rename"))
    expect_title("alpha", "Alpha Final", "Alpha title after second rename")
    popup = r.step("open prefs", "click",
                   lambda: open_popup("#prefs-btn"))
    r.step("select dark theme", "select",
           lambda: select_option(d, "#theme-select", "dark"))
    r.step("apply dark", "click",
           lambda: click_and_close(popup, "#apply-btn", body_is_dark(),
                                   "main window dark class after prefs dark"))
    dark = r.step("read body dark", "eval",
                  lambda: d.eval("return " + body_is_dark()))
    r.check("main window dark after prefs dark", dark is True, str(dark))
    popup = r.step("open prefs again", "click",
                   lambda: open_popup("#prefs-btn"))
    r.step("select light theme", "select",
           lambda: select_option(d, "#theme-select", "light"))
    r.step("apply light", "click",
           lambda: click_and_close(popup, "#apply-btn", body_is_light(),
                                   "main window light class after prefs light"))
    dark = r.step("read body dark again", "eval",
                  lambda: d.eval("return " + body_is_dark()))
    r.check("main window light after prefs light", dark is False, str(dark))
    popup = r.step("open Beta detail", "click",
                   lambda: open_popup('.project[data-id="beta"] .detail-btn'))
    r.step("fill Beta Changed", "type",
           lambda: d.type_text("#title-input", "Beta Changed"))
    r.step("cancel Beta rename", "click",
           lambda: click_and_close(popup, "#cancel-btn", None,
                                   "Beta cancel"))
    # No verify: the title is already Beta, so waiting for it would
    # return instantly and prove nothing. Dwell, then read immediately.
    time.sleep(0.5)
    expect_title("beta", "Beta", "Beta title after cancelled rename")
    detail_popup = r.step(
        "open Gamma detail", "click",
        lambda: open_popup('.project[data-id="gamma"] .detail-btn'))
    d.switch(main_tab)
    ok, _ = ensure_visible(d, r, "main before second prefs",
                           allow_swap=False)
    if not ok:
        raise RuntimeError(
            "INFRA: hidden-body on main tab at two-popups step")
    prefs_popup = r.step(
        "open prefs while detail open", "click",
        lambda: open_popup("#prefs-btn"))
    n = r.step("count handles with two popups", "eval",
               lambda: len(d.handles()))
    r.check("two more handles with two popups open",
            n == handles_before + 2, f"got {n}, baseline {handles_before}")
    r.step("select dark in second prefs", "select",
           lambda: select_option(d, "#theme-select", "dark"))
    r.step("apply dark in second prefs", "click",
           lambda: click_and_close(prefs_popup, "#apply-btn",
                                   body_is_dark(),
                                   "main window dark class after second prefs popup"))
    dark = r.step("read body dark after second prefs", "eval",
                  lambda: d.eval("return " + body_is_dark()))
    r.check("main window dark after second prefs", dark is True, str(dark))
    d.switch(detail_popup)
    ok, _ = ensure_visible(d, r, "detail popup after switch",
                           allow_swap=False)
    if not ok:
        raise RuntimeError(
            "INFRA: hidden-body on detail popup after switch")
    r.step("fill Gamma v2", "type",
           lambda: d.type_text("#title-input", "Gamma v2"))
    r.step("save Gamma v2", "click",
           lambda: click_and_close(detail_popup, "#save-btn",
                                   title_is("gamma", "Gamma v2"),
                                   "Gamma title after rename with two popups"))
    expect_title("gamma", "Gamma v2",
                 "Gamma title after rename with two popups")
    expect_title("alpha", "Alpha Final", "Alpha title at the end")
    expect_title("beta", "Beta", "Beta title at the end")
    n = r.step("count handles at end", "eval", lambda: len(d.handles()))
    r.check("handles back to baseline after all popups closed",
            n == handles_before, f"got {n}, baseline {handles_before}")
    r.details["finalTitles"] = {
        "alpha": title_of("alpha"),
        "beta": title_of("beta"),
        "gamma": title_of("gamma"),
    }


def run_b3_t10(r, d):
    url = r.base + "/clone1-batch3/t10-music-player/fixture.html"
    open_test(r, d, url)

    def expect_text(sel, wanted, what):
        got = (d.text(sel) or "").strip()
        r.check(what, got == wanted, f"got {got!r}, want {wanted!r}")

    def position():
        # Raw Number, no int() truncation (redteam L1): a
        # fractional read must not truncate to 0 and false-pass
        # exact-zero. The fixture position is always an integer,
        # so this changes no live value, only the failure mode.
        return d.eval(
            "return Number(document.getElementById('position')"
            ".dataset.seconds)")

    def tracks():
        return d.eval(
            "return [...document.querySelectorAll('#playlist .track')]"
            ".map(e => e.textContent)")

    def sample_position_min():
        # Top-level return is REQUIRED (Y4d lesson: Marionette runs the
        # script as a function body). The sampler starts the moment this
        # eval runs, right after the Next click, exactly as check.mjs
        # starts its sampler promise before the now-playing assert.
        # /execute/sync awaits the returned promise (W3C Execute Script
        # 13.2.1; Marionette bug 1398095, Firefox 67), so this call
        # blocks about 500 ms and returns the minimum observed.
        # Fail-closed (redteam D3): a None or non-numeric result raises
        # here, never defaults to 0 and never skips the assert.
        result = d.eval(
            "return new Promise((resolve) => {"
            "let min = Infinity;"
            "const t0 = Date.now();"
            "const sample = () => {"
            "const v = Number(document.getElementById('position')"
            ".dataset.seconds);"
            "if (v < min) min = v;"
            "if (Date.now() - t0 >= 500) resolve(min);"
            "else setTimeout(sample, 10);"
            "}; sample(); })")
        if not isinstance(result, (int, float)):
            raise RuntimeError(
                f"sampler returned non-numeric: {result!r}")
        return result

    def exact_zero_next():
        # Same-task click+read (Y15, check.mjs 1d23532): the
        # next-btn click and the position read run in one in-page
        # task, so no timer tick can land between them. Fail-closed
        # (redteam D3): a None or non-numeric result raises here,
        # never defaults to 0 and never skips the assert.
        result = d.eval(
            "document.getElementById('next-btn').click();"
            " return Number(document.getElementById('position')"
            ".dataset.seconds)")
        if not isinstance(result, (int, float)):
            raise RuntimeError(
                f"exact-zero read returned non-numeric: {result!r}")
        # Raw Number, no int() truncation (redteam L1): a
        # fractional read must not truncate to 0 and false-pass.
        return result

    listed = r.step("read playlist", "eval", lambda: tracks())
    r.check("playlist lists 5 tracks", len(listed) == 5, str(listed))
    r.check("first track is Morning Light",
            listed and listed[0].startswith("Morning Light"), str(listed[:1]))
    r.step("click play", "click", lambda: d.click("#play-btn"))
    expect_text("#status", "Playing", "status after play")
    expect_text("#now-playing", "Morning Light - The Demos",
                "now playing after play")
    time.sleep(0.7)
    pos = r.step("read position after 700ms", "eval", lambda: position())
    r.check("position advanced while playing", pos >= 5, str(pos))
    r.details["positionAfter700ms"] = pos
    r.step("click pause", "click", lambda: d.click("#pause-btn"))
    expect_text("#status", "Paused", "status after pause")
    frozen1 = r.step("read frozen position 1", "eval", lambda: position())
    time.sleep(0.4)
    frozen2 = r.step("read frozen position 2", "eval", lambda: position())
    r.check("position frozen while paused", frozen1 == frozen2,
            f"{frozen1} to {frozen2}")
    r.step("click play resume", "click", lambda: d.click("#play-btn"))
    time.sleep(0.5)
    resumed = r.step("read resumed position", "eval", lambda: position())
    r.check("position advanced after resume", resumed > frozen2,
            str(resumed))
    # Exact-zero read on the playing path (Y15, check.mjs 1d23532).
    # The click and the read run in the same in-page task, so no
    # 100 ms timer tick can land between the reset and the read:
    # page JavaScript is single-threaded, and the click handler runs
    # synchronously inside the task. A plain d.click followed by a
    # read cannot guarantee that.
    pos_after_next = r.step(
        "exact-zero read after next while playing", "eval",
        lambda: exact_zero_next())
    r.check("position exactly 0 after next while playing",
            pos_after_next == 0, str(pos_after_next))
    r.details["positionAfterPlayingNext"] = pos_after_next
    # Second witness: sample the position for 500 ms right after the
    # click and take the minimum. Start sampling before the
    # now-playing assert so the first sample lands as close to the
    # click as possible (plan Council 2 A5).
    pos_before = resumed
    min_after = r.step("sample position min after next", "eval",
                       lambda: sample_position_min())
    r.check("position reset after next",
            min_after <= 2 and min_after < pos_before,
            f"min observed {min_after} after {pos_before}")
    r.details["positionMinAfterNext"] = min_after
    # Three-point advancing check: a Next that stops the timer
    # part-way through would still pass an absolute read, so read
    # when the sampler window ends and again after two 350 ms
    # sleeps, requiring a gain of at least 2 ticks across each
    # sleep. The absolute 2-11 bound on the middle read still
    # catches a clock that runs fast.
    after_sampler = r.step("read position at sampler end", "eval",
                           lambda: position())
    r.details["positionAtSamplerEnd"] = after_sampler
    time.sleep(0.35)
    advancing = r.step("read advancing position", "eval",
                       lambda: position())
    r.details["positionAdvancingAfterNext"] = advancing
    r.check("position gained after next while playing",
            advancing - after_sampler >= 2,
            f"{after_sampler} to {advancing}")
    r.check("position after next while playing in range 2-11",
            2 <= advancing <= 11, str(advancing))
    time.sleep(0.35)
    advancing_later = r.step("read advancing position again", "eval",
                             lambda: position())
    r.details["positionAdvancingLaterAfterNext"] = advancing_later
    r.check("position gained again after next while playing",
            advancing_later - advancing >= 2,
            f"{advancing} to {advancing_later}")
    # Now-playing assert moved here (redteam H4 alternative (c)):
    # it used to sit between the sampler and the min check, so its
    # 2 Marionette round trips (find + text) sat in the
    # sampler-to-advancing path and ate the 2..11 bound's margin.
    # The track name is stable across the advancing window, so the
    # assert proves the same thing here; the assert SET is
    # identical to check.mjs, only the order of these two
    # independent asserts is swapped. The frozen Nexts keep their
    # now-playing asserts in place (no timing bound there).
    expect_text("#now-playing", "River Road - The Demos",
                "now playing after next")
    # Exact-zero check on a clock-frozen path. Pause first (the
    # timer stops, so no tick can land between the click and the
    # read) and require exactly 0 after Next. This runs as a second
    # Next on purpose: pausing before the first Next and resuming
    # with Play would restart the timer and hide a nextTrack that
    # stops the clock, and the advancing check above is the only
    # witness for that defect.
    r.step("click pause before frozen next", "click",
           lambda: d.click("#pause-btn"))
    expect_text("#status", "Paused", "status before frozen next")
    r.step("click next while paused", "click",
           lambda: d.click("#next-btn"))
    frozen_after_next = r.step("read position after frozen next",
                               "eval", lambda: position())
    r.check("position exactly 0 after next while paused",
            frozen_after_next == 0, str(frozen_after_next))
    r.details["positionAfterFrozenNext"] = frozen_after_next
    expect_text("#now-playing", "Night Drive - The Demos",
                "now playing after frozen next")
    r.step("click play resume from frozen next", "click",
           lambda: d.click("#play-btn"))
    expect_text("#status", "Playing",
                "status after resume from frozen next")
    # The frozen value was exactly 0, so this read is a gain check:
    # a Play that does not restart the timer fails here, before the
    # Previous clicks (which reset position themselves) can mask it.
    time.sleep(0.35)
    after_frozen_resume = r.step(
        "read position after resume from frozen next", "eval",
        lambda: position())
    r.details["positionAfterFrozenNextResume"] = after_frozen_resume
    r.check("position advanced after resume from frozen next",
            2 <= after_frozen_resume <= 11, str(after_frozen_resume))
    time.sleep(0.35)
    after_frozen_resume_later = r.step(
        "read position after resume from frozen next again", "eval",
        lambda: position())
    r.details["positionAfterFrozenNextResumeLater"] = \
        after_frozen_resume_later
    r.check("position gained again after resume from frozen next",
            after_frozen_resume_later - after_frozen_resume >= 2,
            f"{after_frozen_resume} to {after_frozen_resume_later}")
    r.check("position after resume from frozen next in range 2-11",
            2 <= after_frozen_resume_later <= 11,
            str(after_frozen_resume_later))
    r.step("click prev", "click", lambda: d.click("#prev-btn"))
    expect_text("#now-playing", "River Road - The Demos",
                "now playing after prev from frozen next")
    r.step("click prev again", "click", lambda: d.click("#prev-btn"))
    expect_text("#now-playing", "Morning Light - The Demos",
                "now playing after prev")
    r.step("click volume", "click", lambda: d.click("#volume"))
    vol = r.step("read volume after click", "value",
                 lambda: d.value("#volume"))
    r.check("volume 50 after click", vol == "50", str(vol))
    r.step("press Home on volume", "key",
           lambda: press_keys(d, [KEY_HOME], css="#volume"))
    vol = r.step("read volume after Home", "value",
                 lambda: d.value("#volume"))
    r.check("volume 0 after Home", vol == "0", str(vol))
    r.step("press ArrowRight x30", "key",
           lambda: press_keys(d, [KEY_ARROW_RIGHT] * 30, css="#volume"))
    vol = r.step("read volume after arrows", "value",
                 lambda: d.value("#volume"))
    r.check("volume 30 after arrows", vol == "30", str(vol))
    expect_text("#volume-value", "30", "volume value after slider")
    bar = r.step("read progress rect", "eval",
                 lambda: _rect_of(
                     d, "document.querySelector('#progress')"))
    r.step("click progress at 50%", "click",
           lambda: pointer_click_at(bar["x"] + bar["w"] * 0.5,
                                    bar["y"] + bar["h"] / 2,
                                    fallback_css="#progress"))
    pos = r.step("read position right after seek", "eval",
                 lambda: position())
    r.check("position after 50% seek in range", 85 <= pos <= 100, str(pos))
    r.details["positionAfterSeek"] = pos
    r.step("click shuffle on", "click", lambda: d.click("#shuffle-btn"))
    expect_text("#shuffle-btn", "Shuffle: On", "shuffle button after on")
    listed = r.step("read playlist after shuffle", "eval",
                    lambda: tracks())
    r.check("second track after shuffle is Mountain Air",
            len(listed) > 1 and listed[1].startswith("Mountain Air"),
            str(listed))
    expect_text("#now-playing", "Morning Light - The Demos",
                "now playing unchanged by shuffle")
    # Same sampler read as the first Next: the shuffle Next must
    # reset the position too, and the track-name assert alone cannot
    # see a Next that skips the reset while shuffle is on.
    pos_before_shuffle = r.step("read position before shuffle next",
                                "eval", lambda: position())
    pos_after_shuffle = r.step(
        "exact-zero read after shuffle next while playing", "eval",
        lambda: exact_zero_next())
    r.check("position exactly 0 after shuffle next while playing",
            pos_after_shuffle == 0, str(pos_after_shuffle))
    r.details["positionAfterPlayingShuffleNext"] = pos_after_shuffle
    min_after_shuffle = r.step(
        "sample position min after shuffle next", "eval",
        lambda: sample_position_min())
    r.check("position reset after shuffle next",
            min_after_shuffle <= 2
            and min_after_shuffle < pos_before_shuffle,
            f"min observed {min_after_shuffle} "
            f"after {pos_before_shuffle}")
    r.details["positionMinAfterShuffleNext"] = min_after_shuffle
    # Three-point advancing check, as after the first Next: a
    # shuffle Next that stops the timer would also show min 0, and
    # the step 14 playlist click restarts the timer, so this is the
    # only witness for it.
    after_shuffle_sampler = r.step(
        "read position at shuffle sampler end", "eval",
        lambda: position())
    r.details["positionAtShuffleSamplerEnd"] = after_shuffle_sampler
    time.sleep(0.35)
    advancing_shuffle = r.step(
        "read advancing position after shuffle next", "eval",
        lambda: position())
    r.details["positionAdvancingAfterShuffleNext"] = advancing_shuffle
    r.check("position gained after shuffle next while playing",
            advancing_shuffle - after_shuffle_sampler >= 2,
            f"{after_shuffle_sampler} to {advancing_shuffle}")
    r.check("position after shuffle next while playing in range 2-11",
            2 <= advancing_shuffle <= 11, str(advancing_shuffle))
    time.sleep(0.35)
    advancing_shuffle_later = r.step(
        "read advancing position after shuffle next again", "eval",
        lambda: position())
    r.details["positionAdvancingLaterAfterShuffleNext"] = \
        advancing_shuffle_later
    r.check("position gained again after shuffle next while playing",
            advancing_shuffle_later - advancing_shuffle >= 2,
            f"{advancing_shuffle} to {advancing_shuffle_later}")
    # Now-playing assert moved here, same reason as the plain Next
    # (redteam H4 alternative (c)): its 2 round trips no longer sit
    # in the sampler-to-advancing path. Assert set identical to
    # check.mjs, order of independent asserts swapped.
    expect_text("#now-playing", "Mountain Air - The Demos",
                "now playing after next in shuffle order")
    # Paused shuffle Next, mirroring step 7: the sampler above
    # proves the reset happens, this exact-zero read proves the
    # reset value in shuffle order. Previous returns to Mountain
    # Air so the shuffle-off step still checks the track it started
    # from.
    r.step("click pause before frozen shuffle next", "click",
           lambda: d.click("#pause-btn"))
    expect_text("#status", "Paused",
                "status before frozen shuffle next")
    r.step("click next while paused in shuffle", "click",
           lambda: d.click("#next-btn"))
    frozen_after_shuffle = r.step(
        "read position after frozen shuffle next", "eval",
        lambda: position())
    r.check("position exactly 0 after shuffle next while paused",
            frozen_after_shuffle == 0, str(frozen_after_shuffle))
    r.details["positionAfterFrozenShuffleNext"] = frozen_after_shuffle
    expect_text("#now-playing", "City Rain - The Demos",
                "now playing after frozen shuffle next")
    r.step("click play resume from frozen shuffle next", "click",
           lambda: d.click("#play-btn"))
    expect_text("#status", "Playing",
                "status after resume from frozen shuffle next")
    time.sleep(0.35)
    after_frozen_shuffle_resume = r.step(
        "read position after resume from frozen shuffle next", "eval",
        lambda: position())
    r.details["positionAfterFrozenShuffleResume"] = \
        after_frozen_shuffle_resume
    r.check("position advanced after resume from frozen shuffle next",
            2 <= after_frozen_shuffle_resume <= 11,
            str(after_frozen_shuffle_resume))
    time.sleep(0.35)
    after_frozen_shuffle_resume_later = r.step(
        "read position after resume from frozen shuffle next again",
        "eval", lambda: position())
    r.details["positionAfterFrozenShuffleResumeLater"] = \
        after_frozen_shuffle_resume_later
    r.check("position gained again after resume from frozen shuffle",
            after_frozen_shuffle_resume_later
            - after_frozen_shuffle_resume >= 2,
            f"{after_frozen_shuffle_resume} to "
            f"{after_frozen_shuffle_resume_later}")
    r.check("position after resume from frozen shuffle in range 2-11",
            2 <= after_frozen_shuffle_resume_later <= 11,
            str(after_frozen_shuffle_resume_later))
    r.step("click prev from frozen shuffle next", "click",
           lambda: d.click("#prev-btn"))
    expect_text("#now-playing", "Mountain Air - The Demos",
                "now playing after prev from frozen shuffle next")
    r.step("click shuffle off", "click", lambda: d.click("#shuffle-btn"))
    expect_text("#shuffle-btn", "Shuffle: Off", "shuffle button after off")
    listed = r.step("read playlist after shuffle off", "eval",
                    lambda: tracks())
    r.check("first track after shuffle off is Morning Light",
            listed and listed[0].startswith("Morning Light"),
            str(listed[:1]))
    expect_text("#now-playing", "Mountain Air - The Demos",
                "now playing unchanged by shuffle off")
    r.step("click repeat 1", "click", lambda: d.click("#repeat-btn"))
    expect_text("#repeat-btn", "Repeat: All", "repeat after first click")
    r.step("click repeat 2", "click", lambda: d.click("#repeat-btn"))
    expect_text("#repeat-btn", "Repeat: One", "repeat after second click")
    r.step("click repeat 3", "click", lambda: d.click("#repeat-btn"))
    expect_text("#repeat-btn", "Repeat: Off", "repeat after third click")
    r.step("click Mountain Air track", "click",
           lambda: d.click('#playlist .track[data-track="4"]'))
    expect_text("#now-playing", "Mountain Air - The Demos",
                "now playing after clicking Mountain Air")
    # Let the track play so the position is clearly past 0 before
    # the wrap Nexts: a wrap that fails to reset is only observable
    # when the pre-click position is nonzero (a fresh playlist click
    # leaves it at 0, which a broken wrap would also read as 0).
    time.sleep(0.7)
    pos_before_wrap = r.step("read position before playing wrap",
                             "eval", lambda: position())
    r.details["positionBeforePlayingWrap"] = pos_before_wrap
    r.check("position advanced before playing wrap next",
            pos_before_wrap >= 2, str(pos_before_wrap))
    r.step("click repeat All", "click", lambda: d.click("#repeat-btn"))
    expect_text("#repeat-btn", "Repeat: All", "repeat All before wrap")
    # Playing wrap first: the wrap while playing must reset the
    # position too. The sampler catches a wrap that resets only when
    # paused (or never resets); the frozen check below catches a wrap
    # that resets to the wrong value. Neither alone covers both.
    pos_after_wrap = r.step(
        "exact-zero read after playing wrap next", "eval",
        lambda: exact_zero_next())
    r.check("position exactly 0 after playing wrap next",
            pos_after_wrap == 0, str(pos_after_wrap))
    r.details["positionAfterPlayingWrap"] = pos_after_wrap
    min_after_wrap = r.step("sample position min after playing wrap",
                            "eval", lambda: sample_position_min())
    expect_text("#now-playing", "Morning Light - The Demos",
                "repeat All wraps to first track (playing)")
    r.check("position reset after playing wrap next",
            min_after_wrap <= 2 and min_after_wrap < pos_before_wrap,
            f"min observed {min_after_wrap} after {pos_before_wrap}")
    r.details["positionMinAfterPlayingWrap"] = min_after_wrap
    # Frozen wrap second: go back to the last track and wrap again,
    # this time paused, so the reset value can be read exactly.
    r.step("click Mountain Air track again", "click",
           lambda: d.click('#playlist .track[data-track="4"]'))
    expect_text("#now-playing", "Mountain Air - The Demos",
                "now playing after clicking Mountain Air again")
    time.sleep(0.7)
    pos_before_frozen_wrap = r.step(
        "read position before frozen wrap", "eval", lambda: position())
    r.details["positionBeforeFrozenWrap"] = pos_before_frozen_wrap
    r.check("position advanced before frozen wrap next",
            pos_before_frozen_wrap >= 2, str(pos_before_frozen_wrap))
    # Same frozen exact-zero check as the mid-list Next above, for
    # the repeat-All wrap branch: the wrap path resets position too,
    # and the track-name assert alone cannot see a wrap that leaves
    # the old position behind. Pausing here masks nothing: no
    # advancing check follows the wrap Next.
    r.step("click pause before frozen wrap next", "click",
           lambda: d.click("#pause-btn"))
    expect_text("#status", "Paused", "status before frozen wrap next")
    r.step("click next for frozen wrap", "click",
           lambda: d.click("#next-btn"))
    frozen_after_wrap = r.step("read position after frozen wrap",
                               "eval", lambda: position())
    r.check("position exactly 0 after wrap next while paused",
            frozen_after_wrap == 0, str(frozen_after_wrap))
    r.details["positionAfterFrozenWrap"] = frozen_after_wrap
    expect_text("#now-playing", "Morning Light - The Demos",
                "repeat All wraps to first track (paused)")
    r.step("click play resume from frozen wrap next", "click",
           lambda: d.click("#play-btn"))
    expect_text("#status", "Playing",
                "status after resume from frozen wrap next")
    time.sleep(0.35)
    after_frozen_wrap_resume = r.step(
        "read position after resume from frozen wrap next", "eval",
        lambda: position())
    r.details["positionAfterFrozenWrapResume"] = \
        after_frozen_wrap_resume
    r.check("position advanced after resume from frozen wrap next",
            2 <= after_frozen_wrap_resume <= 11,
            str(after_frozen_wrap_resume))
    time.sleep(0.35)
    after_frozen_wrap_resume_later = r.step(
        "read position after resume from frozen wrap next again",
        "eval", lambda: position())
    r.details["positionAfterFrozenWrapResumeLater"] = \
        after_frozen_wrap_resume_later
    r.check("position gained again after resume from frozen wrap",
            after_frozen_wrap_resume_later
            - after_frozen_wrap_resume >= 2,
            f"{after_frozen_wrap_resume} to "
            f"{after_frozen_wrap_resume_later}")
    r.check("position after resume from frozen wrap in range 2-11",
            2 <= after_frozen_wrap_resume_later <= 11,
            str(after_frozen_wrap_resume_later))
    r.step("click repeat One", "click", lambda: d.click("#repeat-btn"))
    expect_text("#repeat-btn", "Repeat: One", "repeat One after wrap")
    r.step("click repeat Off", "click", lambda: d.click("#repeat-btn"))
    expect_text("#repeat-btn", "Repeat: Off", "repeat Off after wrap")
    r.step("search river", "type",
           lambda: d.type_text("#search", "river"))
    listed = r.step("read playlist after search", "eval",
                    lambda: tracks())
    r.check("search river shows only River Road",
            len(listed) == 1 and listed[0].startswith("River Road"),
            str(listed))
    r.step("clear search", "type", lambda: type_empty(d, "#search"))
    listed = r.step("read playlist after clear", "eval",
                    lambda: tracks())
    r.check("clearing search shows 5 tracks", len(listed) == 5,
            str(listed))
    r.step("click Night Drive track", "click",
           lambda: d.click('#playlist .track[data-track="2"]'))
    expect_text("#now-playing", "Night Drive - The Demos",
                "now playing after clicking Night Drive")
    r.step("click pause final", "click", lambda: d.click("#pause-btn"))
    expect_text("#status", "Paused", "status after final pause")
    # NOTE (Y14b re-stage): the old supplementary D1 diagnostic probe
    # (Next while paused, details-only) is REMOVED. Y15's checker now
    # carries the real frozen-Next exact-zero steps above, so the
    # probe is superseded; keeping it would double-drive Next after
    # the suite's final pause and could mask nothing but would add
    # an un-speced step.

# ---------------- preflight step 0 ----------------

def run_preflight(r, d):
    """Prove the /actions input path live on a scratch tab before t01.
    FAIL on any miss blocks t01. Sets the module globals ACTIONS_OK and
    CLEAR_FIRES_INPUT. The run proceeds only if a working key path
    exists for every required case: /actions, or raw element/value on
    both a text input and a range input."""
    global CLEAR_FIRES_INPUT, ACTIONS_OK
    # Runner-quiet re-check (Y13f H2, defense in depth behind the
    # launch gate: a runner could have started between the gate and
    # this preflight). Runs BEFORE any tab opens; a hit raises
    # PREFLIGHT FAIL and blocks t01.
    for _rpid, _flat in _scan_other_runners():
        raise RuntimeError(
            f"PREFLIGHT FAIL: live slot busy, runner process "
            f"running: pid {_rpid}: {_flat}")
    url = r.base + "/run_batch3_probe.html"
    tab = open_test(r, d, url)
    probe = lambda: d.eval("return window.__probe")  # noqa: E731

    # (i) Keys on a text input: exact e.key strings, focus verified.
    r.step("preflight click probe input", "click",
           lambda: d.click("#probe-input"))
    r.step("preflight type ab", "type",
           lambda: d.type_text("#probe-input", "ab"))
    active = r.step("preflight check focus", "eval",
                    lambda: d.eval("return document.activeElement.id"))
    r.check("preflight focus is probe-input", active == "probe-input",
            active)
    actions_ok = True

    def _keys_attempt():
        global ACTIONS_OK
        try:
            press_keys(d, [KEY_ENTER, KEY_ARROW_UP], css="#probe-input")
            return "actions"
        except Exception as exc:
            print(f"[preflight] /actions key press failed: {exc}",
                  flush=True)
            ACTIONS_OK = False
            send_key_raw(d, "#probe-input", KEY_ENTER)
            send_key_raw(d, "#probe-input", KEY_ARROW_UP)
            return "fallback-raw"

    path_used = r.step("preflight press Enter+ArrowUp", "key",
                       _keys_attempt)
    actions_ok = (path_used == "actions")
    r.details["keyPath"] = path_used
    keys = r.step("preflight read keys", "eval",
                  lambda: probe()["keys"])
    r.check("preflight keys are Enter, ArrowUp",
            len(keys) >= 2 and keys[-2:] == ["Enter", "ArrowUp"],
            str(keys))
    # D1 fix: assert the arrow e.key strings directly, so a future
    # Right/Down PUA swap is named here instead of surfacing as a
    # wrong volume number.
    r.step("preflight press ArrowRight+ArrowDown", "key",
           lambda: press_keys(d, [KEY_ARROW_RIGHT, KEY_ARROW_DOWN],
                              css="#probe-input"))
    keys = r.step("preflight read keys after arrows", "eval",
                  lambda: probe()["keys"])
    r.check("preflight keys are ArrowRight, ArrowDown",
            len(keys) >= 2 and keys[-2:] == ["ArrowRight", "ArrowDown"],
            str(keys))

    # (ii) Range input: click leaves 50, Home sets 0, ArrowRight x70
    # sets 70. Proves the full 70-key batch and focus across batches.
    r.step("preflight click range", "click", lambda: d.click("#probe-range"))
    vol = r.step("preflight range after click", "value",
                 lambda: d.value("#probe-range"))
    r.check("preflight range 50 after click", vol == "50", str(vol))
    r.step("preflight Home on range", "key",
           lambda: press_keys(d, [KEY_HOME], css="#probe-range"))
    vol = r.step("preflight range after Home", "value",
                 lambda: d.value("#probe-range"))
    r.check("preflight range 0 after Home", vol == "0", str(vol))
    r.step("preflight ArrowRight x70 on range", "key",
           lambda: press_keys(d, [KEY_ARROW_RIGHT] * 70,
                              css="#probe-range"))
    vol = r.step("preflight range after arrows", "value",
                 lambda: d.value("#probe-range"))
    r.check("preflight range 70 after arrows", vol == "70", str(vol))

    # (iii) Pointer click at a known point after scrolling.
    r.step("preflight scroll pad into view", "eval",
           lambda: d.eval(
               "document.querySelector('#probe-pad')"
               ".scrollIntoView({block: 'center'}); return 'scrolled';"))
    pad = r.step("preflight read pad rect", "eval",
                 lambda: _rect_of(d, "document.querySelector('#probe-pad')"))
    tx, ty = int(round(pad["x"] + pad["w"] / 2)), int(round(pad["y"] + 10))
    if actions_ok:
        r.step("preflight pointer click pad", "click",
               lambda: pointer_click_at(d, tx, ty))
        clicks = r.step("preflight read clicks", "eval",
                        lambda: probe()["clicks"])
        ok = bool(clicks) and abs(clicks[-1][0] - tx) <= 3 and \
            abs(clicks[-1][1] - ty) <= 3
        r.check("preflight pointer coords match", ok,
                f"target {tx},{ty} got {clicks}")
    else:
        r.details["pointerProbe"] = "skipped, /actions down"
        print("[preflight] pointer probe skipped, /actions down",
              flush=True)

    # (iv) Dblclick on the re-rendering list.
    r.step("preflight dblclick re-render list", "click",
           lambda: dblclick_el(
               d, "document.querySelectorAll('#probe-list li')[0]",
               fallback_css="#probe-list li:nth-of-type(1)"))
    dbl = r.step("preflight read dblclicks", "eval",
                 lambda: probe()["dblclicks"])
    r.check("preflight dblclick fired on re-render list", dbl == 1,
            str(dbl))

    # (v) Empty clear probe: does Marionette /clear fire input?
    r.step("preflight type filter ap", "type",
           lambda: d.type_text("#probe-filter", "ap"))
    n = r.step("preflight read filtered", "eval",
               lambda: probe()["filtered"])
    r.check("preflight filter ap shows 2", n == 2, str(n))
    r.step("preflight type_text empty", "type",
           lambda: d.type_text("#probe-filter", ""))
    n = r.step("preflight read filtered after empty", "eval",
               lambda: probe()["filtered"])
    CLEAR_FIRES_INPUT = (n == 4)
    r.details["clearFiresInput"] = CLEAR_FIRES_INPUT
    print(f"[preflight] CLEAR_FIRES_INPUT={CLEAR_FIRES_INPUT}", flush=True)
    r.step("preflight type_empty", "type",
           lambda: type_empty(d, "#probe-filter"))
    n = r.step("preflight read filtered after type_empty", "eval",
               lambda: probe()["filtered"])
    r.check("preflight type_empty restores 4", n == 4, str(n))

    # (vi) Fallback path proof: raw element/value keys on a text input
    # and on a range input. Required when /actions is down; recorded
    # when /actions works.
    r.step("preflight click probe input for raw", "click",
           lambda: d.click("#probe-input"))
    r.step("preflight raw Enter on text", "key",
           lambda: send_key_raw(d, "#probe-input", KEY_ENTER))
    keys = r.step("preflight read keys after raw", "eval",
                  lambda: probe()["keys"])
    raw_text_ok = keys and keys[-1] == "Enter"
    r.check("preflight raw Enter recorded", raw_text_ok is True,
            str(keys))
    r.step("preflight click range for raw", "click",
           lambda: d.click("#probe-range"))
    r.step("preflight raw Home on range", "key",
           lambda: send_key_raw(d, "#probe-range", KEY_HOME))
    vol = r.step("preflight range after raw Home", "value",
                 lambda: d.value("#probe-range"))
    raw_range_ok = (vol == "0")
    r.check("preflight raw Home resets range", raw_range_ok is True,
            str(vol))
    r.details["rawFallback"] = {"text": raw_text_ok, "range": raw_range_ok}
    if not actions_ok and not (raw_text_ok and raw_range_ok):
        raise RuntimeError(
            "PREFLIGHT FAIL: neither /actions nor raw element/value "
            "provides a working key path for all required cases")
    # (vii) Promise proof (redteam D3): /execute/sync must await a
    # returned Promise. Plus a control showing a bare IIFE returns
    # null (the Y4d lesson: no top-level return discards the value).
    promise_result = r.step("preflight promise eval", "eval",
                            lambda: d.eval(
                                "return new Promise(r => setTimeout("
                                "() => r(42), 100))"))
    r.check("preflight promise eval returns 42", promise_result == 42,
            str(promise_result))
    iife_result = r.step("preflight bare IIFE control", "eval",
                         lambda: d.eval("(function(){ return 42; })()"))
    r.check("preflight bare IIFE returns null (control)",
            iife_result is None, str(iife_result))

    # (viii) window.open popup proof (redteam D5): t09 popups are
    # window.open with width/height features, which Firefox opens as
    # separate windows, not tabs (unlike the <a target=_blank> tabs in
    # run_t05/run_t06). Open one from a real click, switch to it,
    # assert visible, close it, switch back, assert the handle count
    # returns to baseline.
    before_handles = r.step("preflight record handles", "eval",
                            lambda: d.handles())
    r.step("preflight open window.open popup", "click",
           lambda: d.click("#probe-popup-btn"))
    _wait_handles(d, len(before_handles) + 1)
    popup = [h for h in d.handles() if h not in before_handles][0]
    r.step("preflight switch to popup", "switch",
           lambda: d.switch(popup))
    r.step("preflight settle popup", "wait",
           lambda: (d.wait_ready(), time.sleep(1.0)))
    ok, _sw = r.step("preflight ensure popup visible", "diagnose",
                     lambda: ensure_visible(d, r, "probe popup",
                                            allow_swap=False))
    if not ok:
        raise RuntimeError("PREFLIGHT FAIL: window.open popup tab hidden")
    title = r.step("preflight read popup title", "text",
                   lambda: d.text("#popup-title"))
    r.check("preflight popup title", title.strip() == "probe popup",
            title)
    r.step("preflight close popup", "close", lambda: d.close_tab())
    r.step("preflight switch back", "switch",
           lambda: d.switch(tab))
    ok, _ = r.step("preflight ensure probe visible after popup",
                   "diagnose",
                   lambda: ensure_visible(d, r, "probe after popup",
                                          allow_swap=False))
    if not ok:
        raise RuntimeError(
            "PREFLIGHT FAIL: hidden-body on probe tab after popup "
            "close")
    n = r.step("preflight count handles after popup", "eval",
               lambda: len(d.handles()))
    r.check("preflight handles back to baseline",
            n == len(before_handles), f"got {n}, baseline {len(before_handles)}")

    if actions_ok:
        ACTIONS_OK = True
    r.details["actionsOk"] = actions_ok
    print(f"[preflight] ACTIONS_OK={actions_ok} "
          f"raw_text={raw_text_ok} raw_range={raw_range_ok}", flush=True)
    return True


# ---------------- main ----------------

TESTS = {
    "b3-t01": run_b3_t01, "b3-t02": run_b3_t02, "b3-t03": run_b3_t03,
    "b3-t04": run_b3_t04, "b3-t05": run_b3_t05, "b3-t06": run_b3_t06,
    "b3-t07": run_b3_t07, "b3-t08": run_b3_t08, "b3-t09": run_b3_t09,
    "b3-t10": run_b3_t10,
}


def _is_infra(summary):
    return any("INFRA" in f or "PREFLIGHT FAIL" in f
               for f in summary["failures"])


def run_one(test_id, base_url, metrics=None):
    fn = TESTS[test_id]
    r = Runner(test_id, base_url, metrics=metrics)
    # Redteam M2: re-scan at the top of each test, so a runner that
    # starts after the preflight is caught before this test drives
    # Zen. A hit is recorded as INFRA (one retry + breaker count),
    # not as a fixture failure; the test is not driven at all.
    # Note (redteam F7): a runner starting MID-TEST, after this
    # re-scan and during the test's WD session, is not caught until
    # the next test's re-scan. The window is one test's duration;
    # the other runner's own gate is the backstop for documented
    # launch forms.
    hits = _scan_other_runners()
    if hits:
        r.failures.append(
            "INFRA: live slot busy, runner process running: " +
            "; ".join(f"pid {p}: {c}" for p, c in hits))
        s = r.summary()
        print("RESULT " + json.dumps(s, ensure_ascii=False), flush=True)
        return s
    try:
        with WD() as d:
            d.metrics = metrics
            fn(r, d)
    except Exception as exc:
        msg = f"RUNNER ERROR: {type(exc).__name__}: {exc}"
        # Redteam 2 H2: classify transport/session errors as INFRA so
        # the one retry and the breaker count apply. A hung session
        # cannot wedge the suite (each test gets a fresh session), but
        # without this a transient infra event costs the test its pass
        # instead of a retry.
        infra_markers = ("TimeoutError", "URLError",
                         "invalid session id", "no such window",
                         "FIXTURE-UNAVAILABLE")
        if any(m in msg for m in infra_markers):
            msg = "INFRA: " + msg
        r.failures.append(msg)
        print(f"[{test_id}] RUNNER ERROR {exc}", flush=True)
    s = r.summary()
    print("RESULT " + json.dumps(s, ensure_ascii=False), flush=True)
    return s


def _script_basename_is_runner(name):
    """True if a cmdline token's basename is a test-runner script
    (Y13f H2/H3). run_*.py covers Y9/Y13/Y14/Y4d; run-nested*
    covers Y6c's nested run (run-nested-pill.py, run-nested-wayland
    [.sh]: a hyphen, not run_, so the old run_ pattern was blind
    to it); hand_drive_e1.py is E1's driver. No real runner name
    contains "(" or ")", so a basename carrying one is a literal
    filename, never a runner (fix pass 8, Council 2 C7-1: the
    fix7 paren drop re-exposed the fix5 false positive for
    mid-name parens, `run_foo(a).py` and `run_(foo).py`, which
    the fix6 cut was accidentally suppressing; the rejection
    here closes them without touching the separator cut)."""
    if "(" in name or ")" in name:
        return False
    if name == "hand_drive_e1.py":
        return True
    if name.startswith("run-nested"):
        return True
    return name.startswith("run_") and name.endswith(".py")


def _is_python_token(tok):
    base = tok.rsplit("/", 1)[-1]
    return (base in ("python", "python3")
            or base.startswith("python3.") or base.startswith("python2."))


# CPython short options, for bundle expansion (fix pass 3,
# redteam F1). No-value options can be bundled ("-u" "-s"); a
# value-taking option (c, m, W, X) takes the rest of the token as
# its value, or the next argv element when it ends the token.
_PY_NO_VALUE_OPTS = frozenset("bBdEhiIOqsSuv")
_PY_VALUE_OPTS = frozenset("cmWX")


def _expand_bundle(tok):
    """Expand one bundled short-option token, or return None when
    it is not a bundle of known CPython options. "-umrun_batch3"
    becomes ["-u", "-m", "run_batch3"]; "-uc" becomes ["-u", "-c"]
    (the value is the next argv element); "-Wignore" becomes
    ["-W", "ignore"]. A token whose first unknown letter appears
    before any value option is not a bundle (e.g. grep "-rn")."""
    if len(tok) < 3 or not tok.startswith("-") or tok.startswith("--"):
        return None
    out = []
    j = 1
    while j < len(tok):
        ch = tok[j]
        if ch in _PY_NO_VALUE_OPTS:
            out.append("-" + ch)
            j += 1
            continue
        if ch in _PY_VALUE_OPTS:
            out.append("-" + ch)
            if j + 1 < len(tok):
                out.append(tok[j + 1:])
            return out
        return None
    return out


def _expand_bundles(tokens):
    """Expand bundled short flags in a token list, but only after
    the first python interpreter token (a non-python command's own
    bundled flags, e.g. grep "-rn", must not be rewritten). Tokens
    before any python token pass through untouched."""
    out = []
    seen_python = False
    for tok in tokens:
        if _is_python_token(tok):
            seen_python = True
        if seen_python:
            expanded = _expand_bundle(tok)
            if expanded is not None:
                out.extend(expanded)
                continue
        out.append(tok)
    return out


def _c_arg_flat_end(cmdline, c_idx):
    """Flat-token index just past the -c argument for the "-c" at
    flat index c_idx (fix pass 6, redteam B12). The -c argument
    is a single argv element; tokens after it are separate argv
    elements, not part of the -c code, so an import in a later
    argv element must not match. Re-simulates _argv_tokens to
    find where the -c argument's words end. Only valid when the
    -c is a top-level (part-level) "-c", i.e. the DIRECT case;
    a -c nested inside a shell -c string is a word inside that
    string's split, not a part, so this helper does not apply
    to it (the nested case is bounded by the separator stop
    instead). Returns the flat token count when the -c has no
    argument or is not found (fail-open for the span, the
    caller's other checks still apply)."""
    parts = _expand_bundles([t for t in cmdline.split("\x00") if t])
    flat = 0
    i = 0
    while i < len(parts):
        if parts[i] == "-c" and i + 1 < len(parts):
            arg_words = _expand_bundles(parts[i + 1].split())
            if flat == c_idx:
                return flat + 1 + len(arg_words)
            flat += 1 + len(arg_words)
            i += 2
        else:
            flat += 1
            i += 1
    return flat


def _argv_tokens(cmdline):
    """Split a /proc cmdline (NUL-separated) into argv tokens, and
    split any shell -c / flock -c argument on whitespace, so a
    bare-relative or wrapped launch is visible (Y13f H2). The -c
    argument itself is replaced by its words: the first word of a
    -c string is the command being run. Bundled short flags after
    a python token are expanded first ("-umrun_batch3" becomes
    "-u" "-m" "run_batch3"), so a bundled -m/-c is visible to the
    matcher (fix pass 3, redteam F1)."""
    parts = _expand_bundles([t for t in cmdline.split("\x00") if t])
    tokens = []
    i = 0
    while i < len(parts):
        if parts[i] == "-c" and i + 1 < len(parts):
            tokens.append("-c")
            tokens.extend(_expand_bundles(parts[i + 1].split()))
            i += 2
        else:
            tokens.append(parts[i])
            i += 1
    return tokens


def _is_cmd_separator(tok):
    """True if the token is (or contains) a shell command separator
    (fix pass 4, redteam F7; fix pass 5, Council 2 C2-2). A glued
    ";" ("--help;echo") separates commands just as a standalone
    ";" does; "&&" and "||" likewise. A lone "|" inside a token is
    left alone (it is more often a literal, e.g. in a regex, than a
    pipeline). A bare "&" is a separator (background operator);
    "&" inside a token is left alone (it is more often a literal,
    e.g. in a URL, than an operator)."""
    return tok in (";", "&&", "||", "|", "&") or ";" in tok or \
        "&&" in tok or "||" in tok


def _is_var_assignment(tok):
    """True if the token is a VAR=value assignment (fix pass 5,
    redteam R2). The name before "=" must be a valid shell
    identifier (letters, digits, underscore, not starting with a
    digit)."""
    if "=" not in tok:
        return False
    name = tok.split("=", 1)[0]
    return name.isidentifier()


_KNOWN_COMMANDS = ("bash", "sh", "dash", "flock", "env", "sudo",
                   "timeout", "nice", "python3", "python", "codex")


def _owning_command(tokens, c_idx):
    """Basename of the command owning the "-c" token at c_idx
    (fix pass 5, redteam R2/U1; fix pass 6, Council 1 C5-2 /
    redteam R5-2). Walks back from the -c, skipping flags (start
    with "-"), VAR=value assignments, path arguments (contain "/"
    with a basename not in _KNOWN_COMMANDS), and a bare word that
    follows a flag UNLESS its basename is a known command (a
    flag's VALUE, e.g. "pipefail" after "-o" in "bash -o pipefail
    -c"; the "unless known" clause matters because "bash" after
    "-i" in "env -i bash -c" IS the command), and returns the
    first remaining token's basename. A bare word is always a
    command; a path whose basename is a known command is a
    command; a path whose basename is unknown (e.g. flock's
    lockfile /tmp/lock) is an argument and is skipped. Returns
    None when no command token is found before the -c. Residual
    (fix pass 6, Council 1 C5-2): a flag value whose basename is
    exactly a known command (e.g. an init file literally named
    "python3") would still be returned as the owner; that form
    is contrived and the redteam's own path rule has the same
    shape, so it is a record, not a fix. Residual (fix pass 6,
    redteam R5-8 / Council 2 C2-5, NEW false positive,
    fix5-introduced): the walk-back returns ANY bare word as
    the owner without checking whether that word is actually a
    command, so `echo bash -c run_batch3.py`, `ssh host bash -c
    run_batch3.py`, `cat bash -c run_batch3.py` and `grep -r
    bash -c run_batch3.py` all flag True (fix4 False), although
    no shell -c runs (echo prints the words; the ssh client is
    not running the runner locally). Fail-closed, narrow shape
    (needs a literal shell name as a bare word immediately
    before a -c in a non-shell command); fixing it properly
    would require command-position tracking (accept a bare word
    as the owner only when it sits in command position: argv[0],
    or after a separator, a -c, or a wrapper chain). Recorded,
    not fixed; the leaf process is still caught live in every
    case."""
    j = c_idx - 1
    while j >= 0:
        tok = tokens[j]
        if tok.startswith("-"):
            j -= 1
            continue
        if _is_var_assignment(tok):
            j -= 1
            continue
        base = tok.rsplit("/", 1)[-1]
        if j > 0 and tokens[j - 1].startswith("-") and \
                base not in _KNOWN_COMMANDS:
            # C5-2 (fix pass 6): a bare word after a flag is the
            # flag's VALUE, not a command (e.g. "pipefail" after
            # "-o"). Skip it, unless its basename is a known
            # command (then it IS the command, e.g. "bash" after
            # "-i" in "env -i bash -c").
            j -= 1
            continue
        if "/" in tok and base not in _KNOWN_COMMANDS:
            j -= 1
            continue
        return base
    return None


def _quote_states(tokens):
    """Quote state BEFORE each token index, scanning forward from
    tokens[0] (fix pass 6, redteam R5-1 / Council 1 C5-1 /
    Council 2 C2-3). Returns a list of (in_single, in_double)
    tuples, one per token. A ' toggles in_single unless inside
    double quotes; a " toggles in_double unless inside single
    quotes. Backslash escapes follow the shell rule (fix pass 7,
    redteam R6-1): a backslash escapes the next character when
    outside single quotes (outside quotes and inside double
    quotes) and is literal inside single quotes, so an escaped
    quote does not toggle the state. Proven forms: a codex
    prompt carrying 'a \"b; marionette', python -c code carrying
    'x=\"a\\\"b\"; import run_batch3', and the shell apostrophe
    idiom 'don'\''t stop; marionette'. A token is inside quotes
    when either flag is True before it. Caveat: an apostrophe in
    a prompt ("don't") unbalances the tracker, so everything
    after it reads as inside quotes; that errs fail-closed (a
    later real separator would be missed and the marker scope
    would extend too far), which is the safe direction and the
    same class of over-approximation the guard already carries.
    (A bare "don't" inside a single-quoted -c string is a shell
    syntax error and never reaches a live scan; the reachable
    apostrophe form is the '\'' idiom, which the escape rule
    handles.)"""
    states = []
    in_single = False
    in_double = False
    for tok in tokens:
        states.append((in_single, in_double))
        i = 0
        while i < len(tok):
            ch = tok[i]
            if ch == "\\" and not in_single:
                i += 2
                continue
            if ch == "'" and not in_double:
                in_single = not in_single
            elif ch == '"' and not in_single:
                in_double = not in_double
            i += 1
    return states


def _top_level_sep_index(tok, in_single=False, in_double=False):
    """Index of the first top-level shell separator (; / && / ||)
    in tok, or -1 (fix pass 5, redteam R3/R4; fix pass 6, redteam
    R5-1 / Council 1 C5-1 / Council 2 C2-3: rewritten from the
    "after the last quote" heuristic to a char-by-char scan from
    the quote state BEFORE tok; fix pass 7, redteam R6-1: a
    backslash escapes the next character when outside single
    quotes, so an escaped quote does not toggle the state).
    in_single/in_double is the quote state before tok (from
    _quote_states). A separator is top-level only when it
    appears while outside quotes. A token that OPENS a quoted
    region (starts with a quote and holds only one quote of
    that kind, e.g. "'x=1;") has no top-level separator: its
    ";" is inside the opened region (this subsumes Council 1's
    C5-1 sketch). A token with no quotes (e.g. "time;" inside a
    codex -c snippet, or "1;" inside a python -c string) has no
    top-level separator when the state before it is inside
    quotes; when outside, its ";" is a real separator. A
    standalone separator token returns 0 when outside quotes,
    -1 when inside. Limitation: a token with a top-level
    separator BEFORE its last quote (e.g.
    "'a';'b;marionette'") returns the FIRST such separator, so
    a marker after it in the same token is missed (redteam R5-5
    / B13, pre-existing, documented); that form is contrived
    and not in the fleet's launchers. Note the d4 instance
    (redteam addendum): a glued ";" after an OPENING quote
    ("'a=1;") is NOT top-level (the old heuristic called it
    top-level). The direct leaf form ("a=1;") has no quotes;
    this helper DOES return a top-level index for it (3, not
    -1), and the direct case is safe only because its caller
    applies no separator stop there (the separator is Python
    code by the direct-vs-nested rule, not by this helper)
    (fix pass 7, Council 2 C6-2)."""
    if tok in (";", "&&", "||", "&", "|"):
        return 0 if not (in_single or in_double) else -1
    i = 0
    while i < len(tok):
        ch = tok[i]
        if ch == "\\" and not in_single:
            i += 2
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
            i += 1
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            i += 1
            continue
        if not in_single and not in_double:
            if tok.startswith("&&", i) or tok.startswith("||", i):
                return i
            if ch == ";":
                return i
        i += 1
    return -1


def _runner_basename_head(base):
    """The runner basename before the first shell separator char
    (fix pass 6, Council 2 C2-4 / redteam R5-3; fix pass 7,
    Council 2 C6-3 / redteam R6-2: "(" and ")" dropped from the
    cut set). A glued separator with no space ("run_foo.py&&echo",
    "run_foo.py;echo", "run_foo.py|cat") still leaves the runner
    basename as the head; rstrip only strips a separator at the
    END of the token and misses mid-token glue. Returns base up
    to (not including) the first of ";", "&", "|". "(" and ")"
    are not shell separators in argument position: a direct argv
    like "run_foo.py(x" is a literal filename (never executes
    run_foo.py), and in a shell -c string it is a syntax error,
    so cutting at them only adds a literal-filename false
    positive. The ")" cut was pre-existing fix5 behaviour (the
    rstrip stripped a trailing ")"). The paren drop re-exposed
    the fix5 false positive for MID-NAME parens (`run_foo(a).py`,
    `run_(foo).py`, fix pass 8, Council 2 C7-1); those are now
    rejected in _script_basename_is_runner, so the drop plus
    that rejection together close all four paren shapes."""
    cut = len(base)
    for sep in (";", "&", "|"):
        idx = base.find(sep)
        if 0 <= idx < cut:
            cut = idx
    return base[:cut]


def _c_is_shell(tokens, c_idx):
    """True if the "-c" token at c_idx is a shell -c (owned by
    bash, sh, dash or flock). A python/codex -c argument is code
    or a prompt, not a command line, so its first word is not a
    command (fix pass 4, redteam F1/F6). Finds the command owning
    the -c via _owning_command (fix pass 5, redteam R2: the old
    walk-back to argv[0] misclassified wrapper-prefixed shell -c,
    e.g. "env bash -c" and "sudo bash -c", as non-shell)."""
    owner = _owning_command(tokens, c_idx)
    return owner in ("bash", "sh", "dash", "flock")


def _python_executes(tokens, i):
    """True if the token at i is executed BY a python interpreter,
    not merely mentioned after one (fix pass 3, redteam F3; fix
    pass 4, redteam F4/F5). Finds the nearest python token before
    i within the same shell command (the search stops at a shell
    separator or a -c, so "python3 --version; pytest -W ignore
    run_batch3.py" does not count the python3 of the first
    command); returns False when there is none, or when a script
    token sits between it and i, because then the token at i is an
    argument to that script, not to python. A script token is a
    .py basename, -m, -c, or an extensionless run_* token
    ("python3 run_other -W ignore run_batch3.py" returns False,
    the FP is fixed). Residual (fix pass 5, Council 3 C3-2 /
    Council 1 C1-R2): the barrier covers run_* only, so a
    non-run_* extensionless script still false-positives
    ("python3 other -W ignore run_batch3.py" returns True).
    Extending the barrier to any extensionless script token would
    need flag-value tracking (skip -W/-X/-c/-m values to find the
    script position) and is a future improvement, not attempted
    here.
    Callers pass the index of the flag introducing the runner
    token (the -m index, or the -c index for an import), so the
    introducing flag itself is never counted as a barrier."""
    s = i
    while s > 0 and tokens[s - 1] != "-c" and \
            not _is_cmd_separator(tokens[s - 1]):
        s -= 1
    py_idx = -1
    for j in range(s, i):
        if _is_python_token(tokens[j]):
            py_idx = j
    if py_idx < 0:
        return False
    for k in range(py_idx + 1, i):
        base = tokens[k].rsplit("/", 1)[-1]
        if base.endswith(".py") or tokens[k] in ("-m", "-c") or \
                (base.startswith("run_") and
                 not tokens[k].startswith("-")):
            return False
    return True


def _is_runner_cmdline(cmdline):
    """True if the cmdline EXECUTES a runner script (Y13f H2).

    The old regex r"(^|/)run_[^/\\s]*\\.py" matched raw cmdline
    text and missed every bare-relative launch (the token sits
    after a NUL, not after "/" or string start) and every flock -c
    / shell -c form. It also false-positived on a mere path
    mention (md5sum /abs/run_foo.py). This version tokenizes argv
    and requires the script token to be argv[0] (shebang exec), to
    follow a python interpreter token (bare-relative, absolute,
    -u/-m flags, flock -c, shell -c), to be the first word of a -c
    string, or (for non-.py run-nested scripts only) to follow
    bash/sh. A path mention after md5sum/cat/git never matches.
    Module form (Council 2 Fix 1, redteam H1, fix pass 2): "python3
    -m run_batch3" has no .py suffix, so it is accepted as a bare
    run_* / hand_drive_e1 token after -m; the joined form
    "python3 -mrun_batch3" and dotted paths "python3 -m
    foo.run_batch3" are also accepted (dotted only for exact runner
    module names, so foo.run_tests does not flag). Combined short
    flags (fix pass 3, redteam F1) are expanded by _argv_tokens
    ("-umrun_batch3" becomes "-u" "-m" "run_batch3", "-uc" becomes
    "-u" "-c"), so they are caught by the same branches. A
    trailing ".py" on a -m module name is stripped before
    matching: "python3 -m run_batch3.py" DOES execute the file
    (verified live, exit 124 on the sleeping stub), so it must
    match (fix pass 4, redteam R1 regression). A spaced
    -W/-X value ("python3 -W ignore run_batch3.py") is accepted
    via the token two back, as is the long option
    "--check-hash-based-pycs always" (fix pass 3, redteam F2; the
    only CPython long option that takes a value; the joined
    "--check-hash-based-pycs=always" form is rejected by CPython
    as an unknown option, so the flag branch returning True for it
    is a fail-closed over-approximation, not an execution). The
    flag branch and the two-back rule both require the token to be
    executed BY python (_python_executes), so "pytest -W ignore
    run_batch3.py" and "python3 run_other.py -W ignore
    run_batch3.py" no longer false-positive (fix pass 3, redteam
    F3); the guard respects shell command boundaries (fix pass 4,
    redteam F4) and treats an extensionless run_* token as a
    script barrier (fix pass 4, redteam F5). The -m branch is
    guarded the same way (the -m index itself is the guard
    endpoint, so the -m token is never its own barrier), and the
    import branch requires the import to sit inside a python -c
    string (fix pass 4, redteam F3: "pytest -m run_batch3",
    "echo -m run_batch3" and "echo import run_batch3" all miss
    now; fix pass 6, redteam R5-1 / Council 1 C5-1: the
    import guard is now quote-state aware and direct-vs-nested
    aware, so a ";" in direct python -c code no longer blocks
    while a ";" after a nested python -c argument's closing
    quote still does). The first word of a -c string is a command only when
    the -c is a shell -c (fix pass 4, redteam F1: "python3
    -crun_batch3.py" is a NameError, the file never runs). -c
    import form
    (redteam H1): "python3 -c 'import run_batch3; ...'" is accepted
    when a bare runner module name follows "import" or "from" in
    the -c words. Known residual limitations, recorded not hidden:
    runpy.run_path inside -c; "import os, run_foo" (runner second
    in a comma list) misses; dynamic imports (__import__,
    importlib.import_module, exec(open(...).read())) evade the
    static check; a -c string that only imports the runner module
    (no main() call) is flagged although it does not execute it
    (fail-closed over-approximation); extensionless script tokens
    and direct .pyc execution miss for run_*/hand_drive_e1 names
    only ("python3 run-nested-pill" returns True via the run-nested
    prefix rule); a non-run_* extensionless script still
    false-positives ("python3 other -W ignore run_batch3.py"
    returns True, fix pass 5, Council 3 C3-2 / Council 1 C1-R2);
    a glued ";codex" misses ("bash -c 'echo foo;codex
    marionette'", fix pass 5, Council 1 C1-R3, pre-existing);
    a bare word before a -c is always taken as the owning
    command, so `echo bash -c run_batch3.py`, `ssh host bash -c
    run_batch3.py`, `cat bash -c run_batch3.py` and `grep -r bash
    -c run_batch3.py` false-positive (fix pass 6, redteam R5-8 /
    Council 2 C2-5, fail-closed, recorded not fixed; fix pass 7,
    Council 2 C6-3 note: the grep -r form was missing from this
    list); the nearest--c search in _in_shell_c_string crosses
    a shell separator (fix pass 6, redteam R5-4, FIXED: a
    non-shell -c in an earlier command is skipped, so a marker
    in a later command after a codex -c no longer counts); a
    python -c in a later top-level command after a shell -c is
    treated as nested (fix pass 6, import-branch heuristic,
    synthetic-only, recorded not fixed: a single /proc cmdline
    cannot hold two top-level commands from a real shell launch,
    so no live runner is missed) (fix pass 7, Council 3 U-C3-1 /
    Council 1 INFO-1: the old "(fail-closed)" label was the
    wrong direction; a real runner missed would be fail-open,
    and the combined argv cannot occur from a real launch);
    renamed copies, shebang renamed copies, and
    spoofed argv[0] all miss. None is a launch form in use, and
    the renamed/spoofed forms are adversarial, outside this gate's
    accidental-collision threat model. (Correction to the fix-pass-1
    record, redteam F8: double-nested -c quoting is NOT a residual;
    the leaf python process is caught live.) A flock lock held for
    the whole run would close those shapes too, but only fleet-wide
    (every runner must take the same lock; run_live.py does not
    today), so that is a Muse-level fleet decision, not a change
    for this runner. Sync note: this copy has the fix-pass-1, -2,
    -3, -4, -5 and -6 additions; the sibling copies in launch_y13.py and
    run_codex_y5.py do NOT yet have them, so the "identical logic"
    claim is currently FALSE. Re-diff the copies before treating
    them as in sync; the sync itself belongs to Y13f's fix pass."""
    tokens = _argv_tokens(cmdline)
    for i, tok in enumerate(tokens):
        base = tok.rsplit("/", 1)[-1]
        # -m branch FIRST (fix pass 4, redteam R1): a .py-suffixed
        # module name ("run_batch3.py") IS a runner basename, so
        # it would hit the `continue` in the basename block below
        # before reaching this check. The guard endpoint is the
        # -m index itself, so the -m token is never its own
        # barrier.
        if i > 0 and tokens[i - 1] == "-m" and \
                _is_runner_module(base) and \
                _python_executes(tokens, i - 1):
            return True
        if _script_basename_is_runner(_runner_basename_head(base)):
            # C2-1 (fix pass 5, Council 2) + C2-4/R5-3 (fix pass
            # 6): a glued separator on the runner token
            # ("run_foo.py;", "run_foo.py&&", "run_foo.py||",
            # and the no-space forms "run_foo.py&&echo",
            # "run_foo.py;echo", "run_foo.py|cat") must still
            # match. The head before the first separator char is
            # used only for the basename check; `base` itself is
            # used for the .py / bash-sh checks below.
            if i == 0:
                return True
            prev = tokens[i - 1]
            prev_base = prev.rsplit("/", 1)[-1]
            if _is_python_token(prev):
                return True
            # First word of a -c string (bash -c "run_batch3.py").
            # Only when no script token precedes the -c itself
            # ("python3 run_other.py -c 'run_batch3.py'" passes the
            # runner name as an argument to run_other.py, it does
            # not execute it, fix pass 3, redteam F3 class) AND
            # the -c is a shell -c (fix pass 4, redteam F1: a
            # python -c string is code, so "python3
            # -crun_batch3.py" is a NameError, the file never
            # runs; a codex -c string is a prompt, not a command).
            if prev == "-c" and _c_is_shell(tokens, i - 1) and not any(
                    tokens[k].rsplit("/", 1)[-1].endswith(".py")
                    or tokens[k] in ("-m", "-c")
                    for k in range(i - 1)):
                return True
            if prev.startswith("-") and _python_executes(tokens, i):
                return True
            # Spaced flag-with-value form (redteam F2, fix pass 3):
            # "python3 -W ignore run_batch3.py" (the flag's value
            # sits between the python token and the script). The
            # long option --check-hash-based-pycs is the only
            # CPython long option that takes a value.
            if i >= 2 and tokens[i - 2] in (
                    "-W", "-X", "--check-hash-based-pycs") and \
                    _python_executes(tokens, i):
                return True
            if not base.endswith(".py") and prev_base in ("bash", "sh"):
                return True
            continue
        if i > 0 and tokens[i - 1] in ("import", "from") and (
                base.rstrip(";,()").startswith("run_")
                or base.rstrip(";,()") == "hand_drive_e1"):
            # Guard (fix pass 4, redteam F3; fix pass 5, redteam
            # R4 / Council 3 C3-3 / Council 1 C1-R1; fix pass 6,
            # redteam R5-1 / Council 1 C5-1): the import must be
            # inside a python -c string in the SAME shell
            # command. Find the nearest "-c" before the import
            # token (NO separator stop on the way back; the stop
            # is applied forward, below). The -c itself must be
            # owned by python. A DIRECT python -c (no shell -c
            # before it) has its argument's outer quotes consumed
            # by the shell, so a ";" between the -c and the
            # import is Python code (B1/B2/B8 direct standalone
            # ";", B10 direct glued ";") and must not block: a
            # single /proc cmdline never contains a top-level
            # shell ";" separating two top-level commands (the
            # shell splits those into separate processes), so a
            # ";" in a direct python -c cmdline is always code.
            # A NESTED python -c (inside a shell -c string,
            # detected by a shell -c at some index j < c_idx)
            # has its argument quoted in the tokens, so a
            # top-level separator between the -c and the import
            # (a ";" after the argument's closing quote, B12/R4)
            # means the import is in a later shell command and
            # blocks; a ";" inside the argument's opened quote
            # region (d4 "'a=1;", C5-1 B5 "'x=1;") is code and
            # does not block. The stop uses
            # _top_level_sep_index with the quote state before
            # each token (from _quote_states). Limitation: a
            # python -c in a later top-level command after a
            # shell -c (e.g. `bash -c "echo hi"; python3 -c
            # 'import os; import run_batch3'`) is wrongly
            # treated as nested; that form is synthetic-only
            # (a single /proc cmdline cannot hold two top-level
            # commands from a real shell launch, so no live
            # runner is missed) (fix pass 7, Council 3 U-C3-1 /
            # Council 1 INFO-1: the old "(fail-closed)" label
            # was the wrong direction).
            c_idx = -1
            for j in range(i - 1, -1, -1):
                if tokens[j] == "-c":
                    c_idx = j
                    break
            if c_idx >= 0 and _python_executes(tokens, c_idx):
                nested = any(tokens[j] == "-c" and
                             _c_is_shell(tokens, j)
                             for j in range(c_idx))
                blocked = False
                if nested:
                    states = _quote_states(tokens)
                    blocked = any(
                        _top_level_sep_index(tokens[k], *states[k]) >= 0
                        for k in range(c_idx + 1, i))
                else:
                    # DIRECT python -c: the -c argument is a single
                    # argv element, so the import must lie within
                    # it. An import in a LATER argv element (e.g.
                    # `python3 -c "import os" echo import
                    # run_batch3`, redteam B12: the no-separator
                    # later argv, True in fix5 and False in fix6;
                    # fix pass 7, Council 2 C6-4: the earlier
                    # cited form with a glued ";" after the
                    # closing quote returned False in both
                    # fix5 and fix6 and did not demonstrate the
                    # gap) is a command-line argument, not
                    # executed code, and must not match.
                    # _c_arg_flat_end bounds the -c argument's
                    # flat-token span.
                    if i >= _c_arg_flat_end(cmdline, c_idx):
                        blocked = True
                if not blocked:
                    return True
    return False


_RUNNER_MODULES = ("run_batch3", "run_live", "run_agyq2", "run_agyq",
                   "run_fcck", "run_codex_y5", "hand_drive_e1")


def _is_runner_module(mod):
    """True if a -m module name executes a runner (fix pass 2, fix
    pass 4). A bare name matches the run_* prefix rule (same as the
    spaced -m branch); a dotted name matches only when its last
    component is an exact runner module, so foo.run_tests does not
    flag. A trailing ".py" is stripped first: "python3 -m
    run_batch3.py" DOES execute the file (verified live, exit 124
    on the sleeping stub), so it must match (fix pass 4, redteam
    R1 regression)."""
    if mod.endswith(".py"):
        mod = mod[:-3]
    last = mod.rsplit(".", 1)[-1]
    if "." in mod:
        return last in _RUNNER_MODULES
    return last.startswith("run_") or last == "hand_drive_e1"


# Codex executor processes that must REFUSE, not just warn (Y13f,
# council 3 fix 2): a codex CLI whose cmdline mentions the E1
# driver, a geckodriver, a browser profile path, or Marionette is
# driving (or about to drive) a browser. A plain "codex" match with
# none of these is warning-only (a Codex CLI may be doing
# unrelated work). The MARKER tuple below is still in sync with
# launch_y13.py; the predicate using it (_is_codex_executor) is
# NOT identical across copies since fix pass 2 (executable-position
# anchor lives only in this copy so far).
CODEX_REFUSE_MARKERS = ("hand_drive_e1", "geckodriver", ".config/zen",
                        "zen-bin", ".mozilla", "remote-debugging",
                        "marionette")


def _ppid_of(pid):
    """Parent pid from /proc/<pid>/stat, parsed after the last ")",
    because the comm field (in parentheses) may contain spaces and
    shift every index of a blind split (C3 F7). Returns None when
    unreadable."""
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
        rest = stat[stat.rfind(")") + 2:]
        return int(rest.split()[1])
    except Exception:
        return None


def _codex_at_command(tokens, i):
    """True if the "codex" token at i is the command of its command
    (fix pass 3, redteam F4/F5). The command starts at argv[0] or
    right after a "-c" token. From there, only an env wrapper chain
    may precede codex: "env" (basename, so /usr/bin/env counts),
    then flags ("-i", "-u VAR") and VAR=value assignments, then
    codex. Anything else before codex (echo, grep, cat, another
    command) means codex is an argument or a printed word, not the
    command, so "echo env codex marionette" no longer flags. Known
    gaps, recorded: nohup, setsid, timeout, flock-direct, time,
    nice and sudo wrappers each need their own argument parser
    (flock takes a lockfile, timeout a duration); no fleet launcher
    uses them for codex, so they are recorded, not parsed. A "-c"
    bounds the command only when it is a shell -c: "python3 -c
    'codex marionette'" is Python code, not a command (fix pass 4,
    redteam F6)."""
    s = i
    while s > 0 and tokens[s - 1] != "-c" and \
            not _is_cmd_separator(tokens[s - 1]):
        s -= 1
    # A "-c" bounds the command only when it is a shell -c (fix
    # pass 4, redteam F6): "python3 -c 'codex marionette'" is
    # Python code, not a command, so codex there is not the
    # command of anything.
    if s > 0 and tokens[s - 1] == "-c" and \
            not _c_is_shell(tokens, s - 1):
        return False
    if s == i:
        return True
    if tokens[s].rsplit("/", 1)[-1] != "env":
        return False
    j = s + 1
    while j < i:
        if tokens[j].startswith("-"):
            if tokens[j] in ("-u", "--unset"):
                j += 2
            else:
                j += 1
            continue
        if "=" in tokens[j]:
            j += 1
            continue
        return False
    return j == i


def _in_shell_c_string(tokens, i):
    """True if the token at i sits inside a SHELL -c string (fix
    pass 3). Only there does ";" separate shell commands. A codex
    or python -c argument is a prompt/snippet, not a shell command,
    so its ";" must not truncate the marker scope (the H2 live
    case is "codex -c 'import time; ... # marionette'"). Finds the
    "-c" containing i and checks whether the command owning it
    is a shell (bash, sh, dash or flock), via _owning_command
    (fix pass 5, redteam R2: same walk-back fix as _c_is_shell).
    Fix pass 6, redteam R5-4: a non-shell -c in an EARLIER
    command does not contain i. When the nearest "-c" is a
    python/codex -c and a top-level shell separator (quote-state
    aware) lies between it and i, the token is in a later command
    within the enclosing shell -c string, so that -c is skipped
    and the search continues backward to the shell -c that does
    contain i. `bash -c "python3 -c 'x'; codex exec foo; echo
    marionette"` now returns True (the bash -c contains the
    codex), so _same_command_tokens bounds the marker scope and
    the echo's marker does not count. A shell -c is returned
    immediately (a separator inside its string separates
    commands within the string, it does not end the string).
    Bound (fix pass 7, redteam R6-4, pre-existing, fail-closed,
    narrow, recorded not fixed): the R5-4 skip only fires when
    a top-level separator lies between the non-shell -c and the
    token. With no separator before codex (`bash -c "python3 -c
    'x=1;__import__(\"time\").sleep(60)' codex --help; echo
    marionette"`), the wrapper flags True although no codex
    process exists at all (live-proven)."""
    states = _quote_states(tokens)
    for j in range(i - 1, -1, -1):
        if tokens[j] == "-c":
            if _owning_command(tokens, j) in ("bash", "sh", "dash",
                                              "flock"):
                return True
            # Non-shell -c (python/codex). If a top-level
            # separator lies between it and i, the token is in a
            # later command, not inside this -c's argument; skip
            # it and keep searching. Otherwise the token is
            # inside this -c's argument, so it is not in a shell
            # -c string.
            if any(_top_level_sep_index(tokens[k], *states[k]) >= 0
                   for k in range(j + 1, i)):
                continue
            return False
    return False


def _same_command_tokens(tokens, i):
    """Tokens of the same shell command as the token at i (fix pass
    3, redteam F5; fix pass 5, redteam R3; fix pass 6, redteam
    R5-1 / Council 1 C5-1 / Council 2 C2-3: the bound after a
    codex -c is now quote-state aware). Stops at command
    separators (";", "&&", "||", "|", "&"), so "codex --help; echo
    marionette" does not let the marker from the later command
    count against codex. After a codex -c flag, tokens are
    included until a TOP-LEVEL separator (a ";" after a closing
    quote); a ";" inside the snippet's opened quote region is
    code, not a separator, so the F2 case ("time;" inside the
    snippet) and the C5-1/R5-1 cases ("'x=1;", "'a=1;", a SPACED
    separator inside the prompt, e.g. "&&", "|", "&") still count
    their marker. Returns the tokens before and after i within
    that command, lowercased joined text is the caller's job.
    Residual (fix pass 6, redteam R5-7 / Council 2 C2-9/C2-10):
    the direct-form codex "&" (a bare "&" as a separate argv
    element, e.g. `codex --help & echo marionette`) still
    returns True; a bare "&" CAN occur in /proc via direct exec
    (redteam L4), so the old "cannot occur in /proc" claim is
    corrected, but the behaviour is fail-closed and the form is
    contrived."""
    lo = i
    while lo > 0 and tokens[lo - 1] != "-c" and \
            not _is_cmd_separator(tokens[lo - 1]):
        lo -= 1
    parts = list(tokens[lo:i])
    j = i + 1
    while j < len(tokens):
        tok = tokens[j]
        if tok in (";", "&&", "||", "|", "&"):
            break
        if tok == "-c":
            # Codex's own -c flag: everything after it is codex's
            # snippet (a prompt, not shell words), so no ";" after
            # it can be a shell separator (fix pass 4, redteam F2).
            # But a TOP-LEVEL separator (a ";" after a closing
            # quote, fix pass 5, redteam R3) ends the snippet and
            # starts a later shell command, whose marker must not
            # count. A ";" inside the snippet's opened quote
            # region (e.g. "time;", "'x=1;") is code, not a
            # separator, so the scan continues past it (fix pass
            # 6, redteam R5-1 / Council 1 C5-1 / Council 2 C2-3:
            # the bound now uses _quote_states, so a token that
            # OPENS a quoted region has no top-level separator).
            j += 1
            states = _quote_states(tokens)
            while j < len(tokens):
                tok2 = tokens[j]
                in_single, in_double = states[j]
                sep_idx = _top_level_sep_index(tok2, in_single,
                                               in_double)
                if sep_idx >= 0:
                    if sep_idx > 0:
                        parts.append(tok2[:sep_idx])
                    break
                parts.append(tok2)
                j += 1
            break
        if ";" in tok or "&&" in tok or "||" in tok:
            # A glued separator ("--help;echo", "marionette;echo"):
            # the part before the first separator belongs to this
            # command, the rest does not (fix pass 4, redteam F7).
            first = tok.replace("&&", ";").replace("||", ";") \
                .split(";", 1)[0]
            if first:
                parts.append(first)
            break
        parts.append(tok)
        j += 1
    return parts


def _is_codex_executor(cmdline):
    """True if the cmdline is a codex CLI driving (or about to
    drive) a browser (redteam M3, fix pass 3). "codex" must sit in
    an executable position: argv[0] (direct launch, possibly a
    full path), the first word after a -c (shell/flock -c string),
    or the command after an env wrapper chain (env, env -i, env
    FOO=bar, /usr/bin/env). A bare "codex" elsewhere (a grep
    pattern, a cat file argument, an echo string, a word after
    "env" that echo prints) is not an executor and no longer
    flags. A refuse marker is required in a DIFFERENT token than
    the codex token, and only within the same shell command (a
    ";" separates commands). Known gaps: nohup, setsid, timeout,
    flock-direct, time and nice wrappers miss (see
    _codex_at_command); no fleet launcher uses them for codex."""
    tokens = _argv_tokens(cmdline)
    for i, tok in enumerate(tokens):
        if tok.rsplit("/", 1)[-1] != "codex":
            continue
        if not _codex_at_command(tokens, i):
            continue
        # ";" separates shell commands only inside a shell -c
        # string; a codex/python -c argument is a prompt/snippet,
        # so its ";" does not bound the marker scope.
        if _in_shell_c_string(tokens, i):
            rest = " ".join(_same_command_tokens(tokens, i)).lower()
        else:
            rest = " ".join(tokens[:i] + tokens[i + 1:]).lower()
        if any(m in rest for m in CODEX_REFUSE_MARKERS):
            return True
    return False


def _scan_other_runners():
    """Scan /proc for other live runner processes (Y13f H2 fix).
    Returns a list of (pid, flat cmdline) for processes that EXECUTE
    a runner script or are codex executors driving a browser,
    excluding this process's own ancestry (the launching shell's -c
    string names the runner, and flock -c names it too; without the
    exclusion the gate would false-refuse its own launch). Empty
    list means the slot is quiet. Used by launch_gate() and, as a
    re-check, at the top of run_preflight()."""
    own = {os.getpid()}
    pid = os.getpid()
    while pid > 1:
        ppid = _ppid_of(pid)
        if ppid is None or ppid in own:
            break
        pid = ppid
        own.add(pid)
    hits = []
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        rpid = int(name)
        if rpid in own:
            continue
        try:
            with open(f"/proc/{rpid}/cmdline", "rb") as f:
                cmd = f.read().decode("utf-8", "replace")
        except OSError:
            continue
        flat = cmd.replace(chr(0), " ").strip()
        if _is_runner_cmdline(cmd):
            hits.append((rpid, flat))
        elif _is_codex_executor(cmd):
            hits.append((rpid, flat))
    return hits


def _plain_codex_processes():
    """Processes whose executable token is a codex CLI, with no
    refuse marker (warning-only, redteam M3): a plain codex CLI
    may be doing unrelated work, so it never refuses the gate,
    but launch_gate() prints a warning for it."""
    found = []
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        rpid = int(name)
        try:
            with open(f"/proc/{rpid}/cmdline", "rb") as f:
                cmd = f.read().decode("utf-8", "replace")
        except OSError:
            continue
        tokens = _argv_tokens(cmd)
        if tokens and tokens[0].rsplit("/", 1)[-1] == "codex":
            found.append((rpid, cmd.replace(chr(0), " ").strip()))
    return found


def launch_gate():
    """Fail-closed launch gate (plan A4). Runs on the laptop before any
    Zen driving. Checks: LIVE_SLOT_OK=1 is set (I set it only after Y13
    DONE is posted and the Muse go-order is in force); Zen alive;
    Marionette 2828 accepts a TCP connection; server port 8771 and WD
    port 4452 are free; no geckodriver process and no other runner
    process is live. Any failure aborts with exit 2. Never pkill -f."""
    import socket
    import subprocess
    if os.environ.get("LIVE_SLOT_OK") != "1":
        print("LAUNCH GATE: LIVE_SLOT_OK != 1 (slot + go-order not "
              "confirmed), refusing to drive Zen", flush=True)
        return False
    try:
        out = subprocess.run(["pgrep", "-x", "zen-bin"],
                             capture_output=True, text=True,
                             timeout=10).stdout.strip()
    except Exception as exc:
        print(f"LAUNCH GATE: zen check failed: {exc}", flush=True)
        return False
    if not out:
        print("LAUNCH GATE: no zen-bin process, Zen is not alive",
              flush=True)
        return False
    print(f"LAUNCH GATE: Zen alive (PID {out.split()[0]})", flush=True)
    try:
        sock = socket.create_connection(("127.0.0.1", 2828), timeout=3)
        sock.close()
    except Exception as exc:
        print(f"LAUNCH GATE: Marionette 2828 not responsive: {exc}",
              flush=True)
        return False
    print("LAUNCH GATE: Marionette 2828 responsive", flush=True)
    for port, name in ((8771, "server"), (4452, "WD")):
        s = socket.socket()
        try:
            s.bind(("127.0.0.1", port))
        except Exception as exc:
            print(f"LAUNCH GATE: {name} port {port} not free: {exc}",
                  flush=True)
            return False
        finally:
            s.close()
    print("LAUNCH GATE: ports 8771/4452 free", flush=True)
    # Redteam 2 H5: predecessor ports must be free (a live runner on
    # another port would also trip the /proc tokenizer scan below,
    # but the port check fails closed directly).
    for port in (8767, 8768, 8769, 8770, 4448, 4449, 4450, 4451):
        s = socket.socket()
        try:
            s.bind(("127.0.0.1", port))
        except Exception as exc:
            print(f"LAUNCH GATE: predecessor port {port} not free: "
                  f"{exc}", flush=True)
            return False
        finally:
            s.close()
    print("LAUNCH GATE: predecessor ports 8767-8770/4448-4451 free",
          flush=True)
    root = os.environ.get("LIVE_SERVER_ROOT", "")
    fixture = os.path.join(root, "clone1-batch3", "t01-terminal",
                           "fixture.html")
    if not root or not os.path.isdir(root) or \
            not os.path.isfile(fixture):
        print(f"LAUNCH GATE: LIVE_SERVER_ROOT {root!r} missing or does "
              "not hold the suite", flush=True)
        return False
    print(f"LAUNCH GATE: server root holds the suite ({root})",
          flush=True)
    try:
        gecko = subprocess.run(["pgrep", "-x", "geckodriver"],
                               capture_output=True, text=True,
                               timeout=10).stdout.strip()
    except Exception:
        gecko = ""
    if gecko:
        print(f"LAUNCH GATE: geckodriver already running: {gecko} "
              "(another runner live or a stale orphan; kill by PID "
              "only, then re-run)", flush=True)
        return False
    # Y13f H2 (Y14b re-stage): the old pgrep -f sweep matched raw
    # cmdline text, so it missed every bare-relative launch (the
    # token sits after a NUL, not after "/" or string start) and
    # every flock -c / shell -c form, and it false-positived on a
    # mere path mention (md5sum /abs/run_foo.py) and on the
    # launching shell's own -c string. The /proc tokenizer scan
    # below replaces it; it matches only a cmdline that EXECUTES a
    # runner script, and excludes this process's own ancestry.
    hits = _scan_other_runners()
    if hits:
        for rpid, flat in hits:
            print(f"LAUNCH GATE: runner process live: "
                  f"pid {rpid}: {flat}", flush=True)
        return False
    print("LAUNCH GATE: no other runner live", flush=True)
    # Redteam M3: a plain codex CLI (no refuse marker) is
    # warning-only, never a refusal, but it is not silently
    # ignored either.
    for rpid, flat in _plain_codex_processes():
        print(f"LAUNCH GATE: warning: plain codex process live: "
              f"pid {rpid}: {flat}", flush=True)
    return True


def _verify_served_fixture(base_url):
    """Fetch every browser-served suite file over HTTP and compare
    its md5 to the on-disk file under LIVE_SERVER_ROOT (redteam M1,
    fix pass 2: all 12 files, not just the t10 fixture). The 10
    fixture.html files plus the t09 detail.html and prefs.html the
    t09 fixture opens via window.open. start_server() reuses any
    listening server on port 8771, so the gate's disk check alone
    cannot prove the served bytes are the staged suite. Returns
    True only if every file matches; False on any mismatch or
    fetch failure (a foreign server without a path 404s, which
    also refuses). Known limits, recorded: a server that redirects
    or serves different bytes per User-Agent could still fool this
    check (the md5 is the check, not the URL or headers); that is
    adversarial server behavior, outside this gate's threat model
    (the server is started by this runner or reused from a
    previous Y14 run on the same loopback). The check is
    point-in-time (fix pass 3, redteam F7): it verifies the bytes
    once before driving, with no re-check during the run, so a
    server swapped after the check would serve foreign bytes
    unchecked. A slow server refuses fail-closed after the 5 s
    timeout. Content-Type is not checked (bytes only)."""
    import hashlib
    import urllib.request
    root = os.environ.get("LIVE_SERVER_ROOT", "")
    served = (
        "clone1-batch3/t01-terminal/fixture.html",
        "clone1-batch3/t02-spreadsheet/fixture.html",
        "clone1-batch3/t03-video-call/fixture.html",
        "clone1-batch3/t04-email-client/fixture.html",
        "clone1-batch3/t05-file-manager/fixture.html",
        "clone1-batch3/t06-calendar/fixture.html",
        "clone1-batch3/t07-code-editor/fixture.html",
        "clone1-batch3/t08-settings-panel/fixture.html",
        "clone1-batch3/t09-multi-window/fixture.html",
        "clone1-batch3/t09-multi-window/detail.html",
        "clone1-batch3/t09-multi-window/prefs.html",
        "clone1-batch3/t10-music-player/fixture.html",
    )
    for rel in served:
        try:
            with open(os.path.join(root, rel), "rb") as f:
                want = hashlib.md5(f.read()).hexdigest()
            with urllib.request.urlopen(base_url + "/" + rel,
                                       timeout=5) as resp:
                got = hashlib.md5(resp.read()).hexdigest()
        except Exception as exc:
            print(f"SERVED FIXTURE CHECK: fetch failed for {rel}: "
                  f"{exc}", flush=True)
            return False
        if got != want:
            print(f"SERVED FIXTURE CHECK: served md5 {got} != on-disk "
                  f"md5 {want} for {rel} (foreign root reuse), "
                  "refusing", flush=True)
            return False
    print("SERVED FIXTURE CHECK: all 12 served files match the "
          "on-disk root", flush=True)
    return True


def main():
    args = sys.argv[1:]
    if not args:
        print("usage: run_batch3.py <b3-t01..b3-t10 | all>", flush=True)
        return 2
    if not launch_gate():
        return 2
    wanted = list(TESTS) if args == ["all"] else args
    for t in wanted:
        if t not in TESTS:
            print(f"unknown test {t}", flush=True)
            return 2
    # Live metrics, constructed exactly as run_live.main() does: one
    # LiveMetrics per main() invocation, run_id from LIVE_RUN_ID.
    from run_live import live_metrics as lm_mod
    metrics = None
    if lm_mod is not None and os.environ.get("LIVE_METRICS") != "off":
        try:
            from run_live import LOG_PATH as _LOG_PATH
            metrics_path = os.environ.get("LIVE_METRICS") or \
                lm_mod.default_metrics_path(_LOG_PATH)
            run_id = lm_mod.make_run_id(os.environ.get("LIVE_RUN_ID"))
            metrics = lm_mod.LiveMetrics(metrics_path, run_id)
            metrics.live_log = str(_LOG_PATH)
        except Exception as exc:
            print(f"[metrics] disabled: {exc}", file=sys.stderr)
            metrics = None
    elif os.environ.get("LIVE_METRICS") == "off":
        print("[metrics] OFF (LIVE_METRICS=off)", file=sys.stderr)
    httpd, base_url = start_server()
    print(f"serving {os.environ.get('LIVE_SERVER_ROOT', '')} at {base_url}",
          flush=True)
    # Redteam M1: verify the SERVED bytes match the on-disk suite
    # root before driving anything (start_server() reuses any
    # listening server on the port). Refuse (exit 2) on mismatch.
    if not _verify_served_fixture(base_url):
        return 2
    results = []
    infra_streak = 0
    try:
        # Preflight first, in its own session. A preflight failure
        # aborts the run before t01.
        pr = Runner("preflight", base_url, metrics=metrics)
        try:
            with WD() as d:
                d.metrics = metrics
                run_preflight(pr, d)
        except Exception as exc:
            pr.failures.append(
                f"PREFLIGHT FAIL: {type(exc).__name__}: {exc}")
            print(f"[preflight] PREFLIGHT FAIL {exc}", flush=True)
        ps = pr.summary()
        print("RESULT " + json.dumps(ps, ensure_ascii=False), flush=True)
        if ps["failures"]:
            print("SUMMARY preflight FAILED, aborting before t01",
                  flush=True)
            return 1
        # Verify the -metrics.jsonl sibling exists after preflight.
        if metrics is not None:
            import pathlib
            mp = pathlib.Path(metrics.path) \
                if hasattr(metrics, "path") else None
            print(f"[metrics] file: {mp} exists={mp.exists() if mp else '?'}",
                  flush=True)
        for t in wanted:
            s = run_one(t, base_url, metrics=metrics)
            if _is_infra(s):
                infra_streak += 1
                # One retry, only for INFRA.
                print(f"[{t}] INFRA failure, one retry", flush=True)
                s2 = run_one(t, base_url, metrics=metrics)
                results.append(s2)
                infra_streak = 0 if not _is_infra(s2) else infra_streak + 1
            else:
                results.append(s)
                infra_streak = 0
            if infra_streak >= 2:
                print("SUMMARY circuit breaker: 2 consecutive INFRA, "
                      "aborting suite", flush=True)
                break
    finally:
        if httpd is not None:
            httpd.shutdown()
        if metrics is not None:
            try:
                detail = [{"test": x["test"], "pass": x["pass"],
                           "elapsed_s": x["elapsed_ms"] / 1000.0}
                          for x in results]
                metrics.summary(detail)
            except Exception as exc:
                print(f"[metrics] summary failed: {exc}", file=sys.stderr)
    passed = sum(1 for x in results if x["pass"])
    print(f"SUMMARY {passed}/{len(results)} passed, "
          f"total_ms={sum(x['elapsed_ms'] for x in results)}", flush=True)
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
