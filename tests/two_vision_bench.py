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
refuses live mode unless BOTH --live and --confirm-live are given, and
it never touches a real thread in fixture mode (default). Dry-test it
only against tests/two_vision_fixture.html in headless Firefox.

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

FF = "/home/hatch/workspace/tools/firefox/firefox"
GD = "/home/hatch/workspace/tools/geckodriver"
FIXTURE = "file:///home/hatch/workspace/computer-use-wayland/tests/two_vision_fixture.html"
DEFAULT_WORKDIR = "/tmp/two_vision_bench"

# TODO (F5, bulk harvest): this script implements the one-shot bulk
# harvest as a single evaluate per window, which is the harvest the
# combined design needs. Still open: Brave CDP DOM.getBoxModel and
# Accessibility.getFullAXTree in scripts/cdp.mjs (Chromium path only);
# a production V11 MutationObserver flag (here the fixture counts input
# events in window.__inputEvents, a Messenger page needs a real
# observer armed before typing); the BiDi/Marionette handover protocol
# under the one-session constraint (D1); step-6 loop hygiene is
# unowned (prompt caching, diff-gated re-observation, downscale to
# token tier, context editing, low effort, adaptive waiting).
HARVEST_JS = """
return (function(){
  const els = [...document.querySelectorAll(
    'input, textarea, button, [contenteditable="true"]')];
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
    return {ref: e.id ? ('#' + e.id) : (tag + '[' + i + ']'),
            tag: tag, role: role, name: name,
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
GATE_JS = """
return (function(threadSel, bubbleSel, text){
  const t = document.querySelector(threadSel);
  if (!t) return false;
  return [...t.querySelectorAll(bubbleSel)]
    .some(b => b.textContent === text);
})(arguments[0], arguments[1], arguments[2])
"""


def log(name, t0, **kw):
    rec = {"step": name, "wall": datetime.now(timezone.utc).isoformat(),
           "elapsed_s": round(time.monotonic() - t0, 4)}
    rec.update(kw)
    print(json.dumps(rec), flush=True)
    return rec


def median(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2]


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

    A JSON file keyed by intent id (run_id + window label). An intent
    is marked sent only after its V12 gate passed. Before any send the
    chain runs the V12 gate first, regardless of ledger status: a
    recorded intent whose bubble is present is skipped, never re-sent;
    a failed gate whose message actually landed is also caught by the
    same pre-check, so a retry cannot double-send. A recorded intent
    whose bubble is absent is treated as stale and re-sent once,
    because the earlier V12 may have failed on a slow render rather
    than on a lost message.
    """

    def __init__(self, path):
        self.path = path
        parent = os.path.dirname(os.path.abspath(path))
        os.makedirs(parent, exist_ok=True)
        self.data = {"intents": {}}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                self.data = json.load(f)

    def status(self, intent_id):
        return self.data["intents"].get(intent_id, {}).get("status")

    def mark(self, intent_id, status, **kw):
        rec = {"status": status,
               "wall": datetime.now(timezone.utc).isoformat()}
        rec.update(kw)
        self.data["intents"][intent_id] = rec
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, sort_keys=True)


def format_inventory(label, items):
    """Numbered compact text (Mantis pattern) for the agent's VISION 1.

    TODO (D3): Mantis numbering is Chromium-only and ref stability on
    a mutating Messenger page is unaddressed. Refs here are derived
    from the live DOM of this run only (id when present, else tag
    index); they must not transfer between runs or vendors.
    """
    lines = [f"Window {label}: {len(items)} inputs+buttons"]
    for i, it in enumerate(items, 1):
        lines.append(
            f"[{i}] {it['role']} {it['name']!r} ref={it['ref']} "
            f"rect=({it['x']:.0f},{it['y']:.0f},{it['w']:.0f}x{it['h']:.0f}) "
            f"center=({it['cx']:.0f},{it['cy']:.0f}) "
            f"visible={it['visible']} focused={it['focused']}")
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
    created while the Marionette session is active (one-session rule)."""
    os.makedirs(profile, exist_ok=True)
    t0 = time.monotonic()
    proc = subprocess.Popen(
        [FF, "-headless", "-marionette",
         f"--remote-debugging-port={bidi_port}",
         "-profile", profile, "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.time() + 30
    while time.time() < deadline:
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
    service = Service(GD, log_output="/tmp/two_vision_geckodriver.log",
                      service_args=["--connect-existing",
                                    "--marionette-port", "2828"])
    t0 = time.monotonic()
    driver = webdriver.Firefox(service=service)
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
    then re-read only its rect (one cheap call, not a full snapshot)."""
    vh = driver.execute_script("return window.innerHeight")
    r = driver.execute_script(
        "const e=document.querySelector(arguments[0]);"
        " if(!e) return null; const b=e.getBoundingClientRect();"
        " return {cx: b.x+b.width/2, cy: b.y+b.height/2};", ref)
    if r is None:
        return None
    if r["cy"] < 0 or r["cy"] > vh:
        driver.execute_script(
            "document.querySelector(arguments[0])"
            ".scrollIntoView({block:'center'});", ref)
        r = driver.execute_script(
            "const e=document.querySelector(arguments[0]);"
            " if(!e) return null; const b=e.getBoundingClientRect();"
            " return {cx: b.x+b.width/2, cy: b.y+b.height/2};", ref)
    return r


def hcu_guard(driver, item, t0):
    """HCU-style live guard (gap D2: the guard lives here; no
    production component owns it yet). Re-checks the target's live
    geometry + visibility + hit test right before input. Returns
    (ok, reason, verify_evidence). Geometry moved more than 2 px from
    the VISION 1 snapshot fails the guard: the inventory is stale."""
    v = driver.execute_script(VERIFY_JS, item["ref"])
    if not v.get("found"):
        return False, "target-gone", v
    if not v.get("visible"):
        return False, "not-visible", v
    if not v.get("hit"):
        return False, "covered", v
    dx = abs(v["rect"]["cx"] - item["cx"])
    dy = abs(v["rect"]["cy"] - item["cy"])
    if dx > 2 or dy > 2:
        return False, f"geometry-moved dx={dx:.1f} dy={dy:.1f}", v
    return True, None, v


def send_one(driver, window, item, message, intent_id, ledger,
             plan, t_start, step_no):
    """One guarded send: click, type, Enter, V12 gate. Returns a step
    record. On any failure the caller stops the chain (Anthropic batch
    loop contract: stop at first failure, rest not-executed)."""
    t0 = time.monotonic()
    step = {"step": step_no, "window": window["label"],
            "intent_id": intent_id, "status": "failed",
            "elapsed_s": 0.0}
    thread_sel = window.get("thread_selector", "#thread")
    bubble_sel = window.get("bubble_selector", ".bubble, [data-sender]")
    v12_timeout = plan.get("timeouts", {}).get("v12_gate_s", 5)

    # Exactly-once pre-check (D4): before any send, check whether the
    # bubble is already in the thread DOM. If it is, the message was
    # already sent (by an earlier attempt whose V12 gate timed out, or
    # by a previous run with the same intent), so mark sent and skip.
    # This runs regardless of ledger status: a failed gate must not
    # double-send on retry. Cost is one cheap evaluate per send.
    present = driver.execute_script(
        GATE_JS, thread_sel, bubble_sel, message)
    if present:
        ledger.mark(intent_id, "sent", window=window["label"],
                    message=message, note="bubble-already-present")
        step["status"] = "skipped-already-sent"
        step["elapsed_s"] = round(time.monotonic() - t0, 4)
        log("send_skipped_already_sent", t0, window=window["label"],
            intent_id=intent_id)
        return step
    if ledger.status(intent_id) == "sent":
        log("ledger_stale_bubble_absent", t0, window=window["label"],
            intent_id=intent_id)

    # V5 hit test + HCU guard, from the live DOM, before any input.
    ok, reason, v = hcu_guard(driver, item, t0)
    if not ok:
        step["error"] = reason
        step["elapsed_s"] = round(time.monotonic() - t0, 4)
        log("guard_failed", t0, window=window["label"], reason=reason)
        return step

    # Real pointer click at the snapshot center, then focus check (V3)
    # before any keystroke: a missed click must never type.
    pos = ensure_visible(driver, item["ref"])
    if pos is None:
        step["error"] = "target-gone"
        step["elapsed_s"] = round(time.monotonic() - t0, 4)
        return step
    click_at(driver, pos["cx"], pos["cy"])
    v = driver.execute_script(VERIFY_JS, item["ref"])
    if not v.get("active"):
        step["error"] = "focus-failed"
        step["evidence"] = v
        step["elapsed_s"] = round(time.monotonic() - t0, 4)
        log("focus_check_failed", t0, window=window["label"])
        return step

    # Type with real keys, then V1 value readback before Enter.
    events_before = v.get("inputEvents")
    driver.find_element("css selector", item["ref"]).send_keys(message)
    v = driver.execute_script(VERIFY_JS, item["ref"])
    if v.get("value") != message:
        step["error"] = "value-mismatch"
        step["evidence"] = v
        step["elapsed_s"] = round(time.monotonic() - t0, 4)
        log("value_check_failed", t0, window=window["label"],
            value=v.get("value"))
        return step
    step["v1_value_ok"] = True
    step["v11_input_events"] = (
        None if events_before is None or v.get("inputEvents") is None
        else v["inputEvents"] - events_before)

    from selenium.webdriver.common.keys import Keys
    driver.find_element("css selector", item["ref"]).send_keys(Keys.ENTER)

    # V12 finish gate: the sent bubble must appear in the thread DOM.
    deadline = time.monotonic() + v12_timeout
    while time.monotonic() < deadline:
        if driver.execute_script(GATE_JS, thread_sel, bubble_sel,
                                 message):
            break
        time.sleep(0.2)
    else:
        step["error"] = "v12-timeout"
        step["elapsed_s"] = round(time.monotonic() - t0, 4)
        log("v12_gate_timeout", t0, window=window["label"],
            timeout_s=v12_timeout)
        return step
    step["v12_gate_ok"] = True
    ledger.mark(intent_id, "sent", window=window["label"],
                message=message)
    step["status"] = "sent"
    step["elapsed_s"] = round(time.monotonic() - t0, 4)
    log("send_ok_v12", t0, window=window["label"], intent_id=intent_id)
    return step


def harvest_window(driver, label, t_start):
    """VISION 1 for one window: one evaluate, all inputs + buttons."""
    t0 = time.monotonic()
    items = driver.execute_script(HARVEST_JS)
    log("vision1_harvest_one_shot", t0, window=label,
        elements=len(items))
    return items


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
    shape the live run needs if both clones live in one Zen), and the
    --instances flag records the choice for the live run; two
    instances would need a second Marionette attach, which the
    one-session rule forbids on one browser but allows across two
    browser processes.
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

    if args.live and not args.confirm_live:
        print("REFUSED: live mode needs --confirm-live, which only the "
              "coordinator gives after approving the run.",
              file=sys.stderr)
        return 2
    if args.live and args.fixture:
        print("REFUSED: --live and --fixture together make no sense.",
              file=sys.stderr)
        return 2
    if args.instances == "two" and not args.live:
        print("NOTE: two instances is a live-run shape; fixture mode "
              "uses one instance with two windows.", file=sys.stderr)

    os.makedirs(args.workdir, exist_ok=True)
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
    run_id = plan["run_id"]
    ledger_path = args.ledger or os.path.join(args.workdir, "ledger.json")
    ledger = Ledger(ledger_path)
    results = {"run_id": run_id, "mode": args.mode,
               "live": bool(args.live), "instances": args.instances,
               "wall_start": wall_start, "visions_used": 2,
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
            with open(inv_path, "w", encoding="utf-8") as f:
                json.dump(inventory, f, indent=2)
            log("vision1_inventory_written", t_start, path=inv_path)
        if args.print_inventory:
            for w in plan["windows"]:
                print(format_inventory(w["label"],
                                       inventory[w["label"]]))
        if args.mode == "harvest":
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

        # Guarded send chain, stop at first failure, rest not-executed.
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
            step = send_one(driver, w, targets[w["label"]],
                            plan["messages"][w["label"]], intent_id,
                            ledger, plan, t_start, step_no)
            results["steps"].append(step)
            if step["status"] not in ("sent", "skipped-already-sent"):
                failed = True
                ledger.mark(intent_id, "failed",
                            error=step.get("error"))

        sent = [s for s in results["steps"]
                if s["status"] in ("sent", "skipped-already-sent")]
        # Outcome scoring (M1): PASS iff both messages are in their
        # threads. VISION 2 is the agent looking at both threads once;
        # the script's V12 gates are the same check by DOM read.
        results["outcome"] = ("PASS" if len(sent) == len(plan["windows"])
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
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    log("benchmark_finished", t_start, outcome=results["outcome"],
        wall_s=results["wall_s"], out=out_path)
    return code


if __name__ == "__main__":
    sys.exit(main())
