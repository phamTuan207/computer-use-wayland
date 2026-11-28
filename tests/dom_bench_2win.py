#!/usr/bin/env python3
"""DOM bench, 2-window shape, batch 8 task 2.

Extends batch 7 task 2 (docs/clone2-dom-grounding-20261122.md) to the
2-vision benchmark shape: two headless Firefox windows in ONE
Marionette session, the same fixture in both, one one-shot harvest
per window, pointer clicks in both windows from those snapshots,
verify by one DOM read per window, and the benchmark-shaped flow
(click input window 1, type, Enter, click input window 2, type,
Enter).

It also compares the amend's ground_many (scripts/dom_act.py on
todolist-push: 3 evaluates per selector, locate + viewport_origin +
hit_check, so 3N evals for N selectors) against the one-shot harvest
(1 evaluate for all N) on the same fixture, for the benchmark-shaped
selector set (6 above-fold buttons per window) and for the full
visible inventory (65 per window, hidden-btn excluded, it has no
rect). Two findings from the first run are built into the bench:
ground_many as written FAILS on below-fold elements (the hit check
fails off-viewport), so below-fold selectors are measured with a
scroll-first variant (3 evals above the fold, 5 below it), and a
scroll-first full harvest leaves early rects stale after later
scrolls, which the bench records.

Every step prints one JSON line: wall clock (UTC) and elapsed seconds
from a monotonic clock. One script invocation is one full run; run it
twice and keep both logs. Run with the repo venv python.
"""
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

FF = os.path.expanduser("~/workspace/tools/firefox/firefox")
GD = os.path.expanduser("~/workspace/tools/geckodriver")
FIXTURE = "file://" + os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "dom_grounding_fixture.html")

RECT_JS = """
const els = [...document.querySelectorAll('button, input, select, a')];
return els.map(e => {
  const r = e.getBoundingClientRect();
  return {id: e.id, tag: e.tagName, x: r.x, y: r.y, w: r.width, h: r.height,
          cx: r.x + r.width / 2, cy: r.y + r.height / 2,
          visible: r.width > 0 && r.height > 0};
});
"""

LOCATE_JS = """
const el = document.querySelector(arguments[0]);
if (!el) return null;
const r = el.getBoundingClientRect();
return {x: r.x, y: r.y, width: r.width, height: r.height,
        center_x: r.x + r.width / 2, center_y: r.y + r.height / 2};
"""

ORIGIN_JS = "return [window.mozInnerScreenX, window.mozInnerScreenY];"

HIT_JS = """
const el = document.querySelector(arguments[0]);
if (!el) return false;
const r = el.getBoundingClientRect();
if (!r.width || !r.height) return false;
const cx = r.x + r.width / 2, cy = r.y + r.height / 2;
const hit = document.elementFromPoint(cx, cy);
return hit === el || el.contains(hit);
"""

# Benchmark-shaped selector set for the strict comparison: 6
# above-fold buttons per window. The benchmark's input/select/link
# sit below the fold in this fixture, and ground_many as written
# fails on them (see step 2b), so they are measured separately.
SET_A = ["btn-3", "btn-17", "btn-42", "btn-0", "btn-1", "btn-2"]
# Below-fold benchmark selectors, measured with scroll-first.
SET_B = ["name-input", "pick", "plain-link"]
CLICK_TARGETS = ["btn-3", "btn-17", "btn-42", "moved", "scroll-btn"]


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


def ground_many(driver, selectors):
    """Mirror scripts/dom_act.py ground_many: 3 evals per selector.

    Returns (points, evals): points maps selector to its rect dict,
    evals is the count of JS evaluates performed (3 per selector).
    Raises on the first ungroundable selector, like the original.
    """
    points = {}
    evals = 0
    for sel in selectors:
        rect = driver.execute_script(LOCATE_JS, "#" + sel)
        evals += 1
        if rect is None:
            raise RuntimeError("no element matches #%s" % sel)
        origin = driver.execute_script(ORIGIN_JS)
        evals += 1
        if not (isinstance(origin, list) and len(origin) == 2):
            raise RuntimeError("viewport origin is not two numbers")
        hit = driver.execute_script(HIT_JS, "#" + sel)
        evals += 1
        if not hit:
            raise RuntimeError("hit check failed for #%s" % sel)
        points[sel] = rect
    return points, evals


def ground_many_scroll(driver, selectors):
    """ground_many plus scroll-into-view for below-fold selectors.

    Per selector: locate (1 eval); when the rect center is outside
    the viewport, scrollIntoView (1 eval) and re-locate (1 eval);
    then viewport origin (1 eval) and hit check (1 eval). So 3
    evals above the fold, 5 below it. Returns (points, evals).
    Raises on the first ungroundable selector, like the original.
    """
    vh = driver.execute_script("return window.innerHeight")
    evals = 1
    points = {}
    for sel in selectors:
        rect = driver.execute_script(LOCATE_JS, "#" + sel)
        evals += 1
        if rect is None:
            raise RuntimeError("no element matches #%s" % sel)
        if rect["center_y"] < 0 or rect["center_y"] > vh:
            driver.execute_script(
                "document.querySelector(arguments[0]).scrollIntoView({block:'center'})",
                "#" + sel)
            evals += 1
            rect = driver.execute_script(LOCATE_JS, "#" + sel)
            evals += 1
        origin = driver.execute_script(ORIGIN_JS)
        evals += 1
        if not (isinstance(origin, list) and len(origin) == 2):
            raise RuntimeError("viewport origin is not two numbers")
        hit = driver.execute_script(HIT_JS, "#" + sel)
        evals += 1
        if not hit:
            raise RuntimeError("hit check failed for #%s" % sel)
        points[sel] = rect
    return points, evals


def main():
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.firefox.service import Service

    run_tag = sys.argv[1] if len(sys.argv) > 1 else "run1"
    profile = "/tmp/dom_2win_profile_" + run_tag
    shutil.rmtree(profile, ignore_errors=True)
    os.makedirs(profile, exist_ok=True)
    t_start = time.monotonic()

    proc = subprocess.Popen(
        [FF, "-headless", "-marionette",
         "-profile", profile, "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.time() + 30
    while time.time() < deadline:
        if port_open(2828):
            break
        time.sleep(0.25)
    if not port_open(2828):
        proc.kill()
        raise RuntimeError("marionette port did not open in 30 s")
    log("browser_launch_manual", t_start, pid=proc.pid)
    service = Service(GD, log_output="/tmp/dom_2win_geckodriver.log",
                      service_args=["--connect-existing", "--marionette-port", "2828"])
    t0 = time.monotonic()
    driver = webdriver.Firefox(service=service)
    log("marionette_attach_session", t0)
    try:
        driver.set_window_size(1280, 900)
        t0 = time.monotonic()
        driver.get(FIXTURE)
        log("navigate_fixture_window1", t0)
        win1 = driver.current_window_handle
        t0 = time.monotonic()
        driver.switch_to.new_window("window")
        win2 = driver.current_window_handle
        driver.set_window_size(1280, 900)
        driver.get(FIXTURE)
        log("open_window2_navigate_fixture", t0, handles=len(driver.window_handles))

        # Window switch cost, 3 round trips.
        switch_times = []
        for i in range(3):
            t0 = time.monotonic()
            driver.switch_to.window(win1)
            driver.switch_to.window(win2)
            switch_times.append(time.monotonic() - t0)
        log("window_switch_roundtrip", t_start,
            runs=[round(x, 4) for x in switch_times],
            median_s=round(median(switch_times), 4))

        # Counts in both windows.
        counts = {}
        for name, h in (("win1", win1), ("win2", win2)):
            driver.switch_to.window(h)
            t0 = time.monotonic()
            n = driver.execute_script(
                "return document.querySelectorAll('button, input, select, a').length")
            counts[name] = n
            log("count_interactive_" + name, t0, count=n)

        # 1. One-shot harvest per window, 3 runs each.
        harvests = {}
        for name, h in (("win1", win1), ("win2", win2)):
            driver.switch_to.window(h)
            times = []
            rects = None
            for i in range(3):
                t0 = time.monotonic()
                rects = driver.execute_script(RECT_JS)
                times.append(time.monotonic() - t0)
            harvests[name] = {r["id"]: r for r in rects}
            log("one_shot_harvest_" + name, t_start,
                runs=[round(x, 4) for x in times],
                median_s=round(median(times), 4), elements=len(rects),
                visible=sum(1 for r in rects if r["visible"]))

        # 2. ground_many vs one-shot on the benchmark-shaped set A
        # (6 selectors per window, 12 total, 36 evals vs 2 evals).
        for name, h in (("win1", win1), ("win2", win2)):
            driver.switch_to.window(h)
            t0 = time.monotonic()
            points, evals = ground_many(driver, SET_A)
            gm_t = time.monotonic() - t0
            worst = 0.0
            worst_id = None
            for sel, rect in points.items():
                m = harvests[name].get(sel)
                if not m:
                    continue
                d = max(abs(rect["x"] - m["x"]), abs(rect["y"] - m["y"]),
                        abs(rect["width"] - m["w"]),
                        abs(rect["height"] - m["h"]))
                if d > worst:
                    worst, worst_id = d, sel
            log("ground_many_setA_" + name, t_start,
                elapsed_s=round(gm_t, 4), selectors=len(SET_A),
                evals=evals, per_selector_ms=round(gm_t / len(SET_A) * 1000, 2),
                max_delta_vs_oneshot_px=worst, worst_id=worst_id)

        # 2b. Below the fold: ground_many as written fails. Measure
        # the strict failure on name-input, then the scroll-first
        # variant on the 3 below-fold benchmark selectors.
        for name, h in (("win1", win1), ("win2", win2)):
            driver.switch_to.window(h)
            vh = driver.execute_script("return window.innerHeight")
            rect = driver.execute_script(LOCATE_JS, "#name-input")
            origin = driver.execute_script(ORIGIN_JS)
            hit = driver.execute_script(HIT_JS, "#name-input")
            log("ground_many_strict_below_fold_" + name, t_start,
                selector="name-input", rect=rect, viewport_height=vh,
                hit=hit, groundable=bool(hit),
                note="strict ground_many fails here, rect center is off-viewport")
            t0 = time.monotonic()
            points, evals = ground_many_scroll(driver, SET_B)
            gm_t = time.monotonic() - t0
            log("ground_many_scroll_setB_" + name, t_start,
                elapsed_s=round(gm_t, 4), selectors=len(SET_B),
                evals=evals, per_selector_ms=round(gm_t / len(SET_B) * 1000, 2))

        # 3. ground_many on the full visible inventory (65 per window,
        # hidden-btn excluded: it has no rect and fails the hit check,
        # which is ground_many's fail-fast behaviour). Scroll-first,
        # because 5 of the 65 sit below the fold. No agreement check
        # against the step 1 harvest here: scrolling moves every rect,
        # so a rect grounded before a scroll is stale after it. The
        # hit check at grounding time is the per-element proof.
        full_ids = [r["id"] for r in harvests["win1"].values()
                    if r["visible"]]
        for name, h in (("win1", win1), ("win2", win2)):
            driver.switch_to.window(h)
            t0 = time.monotonic()
            points, evals = ground_many_scroll(driver, full_ids)
            gm_t = time.monotonic() - t0
            log("ground_many_full_" + name, t_start,
                elapsed_s=round(gm_t, 4), selectors=len(full_ids),
                evals=evals, per_selector_ms=round(gm_t / len(full_ids) * 1000, 2))

        # 3b. Fail-fast proof: hidden-btn is ungroundable.
        driver.switch_to.window(win1)
        t0 = time.monotonic()
        hidden_rect = driver.execute_script(LOCATE_JS, "#hidden-btn")
        hidden_hit = driver.execute_script(HIT_JS, "#hidden-btn")
        log("ground_many_hidden_btn_fails", t_start,
            rect=hidden_rect, hit=hidden_hit,
            groundable=bool(hidden_hit))

        # 4. One snapshot per window for inventory, then 5 real
        # pointer clicks in that window, verified by one DOM read per
        # window. The first version of this step clicked straight
        # from the snapshot and FAILED in both windows (clicked log
        # "btn-3;btn-17;btn-42;tall;tall;", run log
        # /tmp/dom_2win_run1_stale_rect.log): a scroll for an earlier
        # target invalidates the snapshot rects of the later targets,
        # so the "moved" and "scroll-btn" clicks landed on the tall
        # spacer at stale coordinates. The fix, measured here: re-read
        # each target's rect immediately before its click (one cheap
        # evaluate each, plus one more when a scroll intervenes).
        from selenium.webdriver.common.actions.action_builder import ActionBuilder
        from selenium.webdriver.common.actions.pointer_input import PointerInput
        from selenium.webdriver.common.actions import interaction
        for name, h in (("win1", win1), ("win2", win2)):
            driver.switch_to.window(h)
            t0 = time.monotonic()
            snap = driver.execute_script(RECT_JS)
            snap_t = time.monotonic() - t0
            t0 = time.monotonic()
            vh = driver.execute_script("return window.innerHeight")
            re_reads = 0
            for tid in CLICK_TARGETS:
                r = driver.execute_script(
                    "const e=document.getElementById('%s'); const b=e.getBoundingClientRect();"
                    " return {cx: b.x+b.width/2, cy: b.y+b.height/2};" % tid)
                re_reads += 1
                if r["cy"] < 0 or r["cy"] > vh:
                    driver.execute_script(
                        "document.getElementById('%s').scrollIntoView({block:'center'})" % tid)
                    r = driver.execute_script(
                        "const e=document.getElementById('%s'); const b=e.getBoundingClientRect();"
                        " return {cx: b.x+b.width/2, cy: b.y+b.height/2};" % tid)
                    re_reads += 1
                pointer = PointerInput(interaction.POINTER_MOUSE, "mouse")
                builder = ActionBuilder(driver, mouse=pointer)
                pointer.create_pointer_move(x=int(r["cx"]), y=int(r["cy"]))
                pointer.create_pointer_down(button=0)
                pointer.create_pointer_up(button=0)
                builder.perform()
            click_t = time.monotonic() - t0
            t0 = time.monotonic()
            clicked = driver.execute_script("return window.__clickedIds()")
            counter = driver.execute_script(
                "return document.getElementById('counter').textContent")
            verify_t = time.monotonic() - t0
            landed = clicked.split(";")
            log("snapshot_five_clicks_fresh_rects_" + name, t_start,
                snapshot_s=round(snap_t, 4), clicks_s=round(click_t, 4),
                verify_read_s=round(verify_t, 4), targets=CLICK_TARGETS,
                re_read_evals=re_reads,
                clicked_log=clicked, counter=counter,
                all_five_landed=all(t in landed for t in CLICK_TARGETS))

        # 5. Benchmark-shaped flow: click input in window 1, type,
        # Enter, then the same in window 2, verify both with one DOM
        # read per window.
        flow_text = {"win1": "hello win1", "win2": "hello win2"}
        t0 = time.monotonic()
        for name, h in (("win1", win1), ("win2", win2)):
            driver.switch_to.window(h)
            snap = driver.execute_script(RECT_JS)
            by_id = {r["id"]: r for r in snap}
            r = by_id["name-input"]
            # name-input sits below the fold: scroll it into view
            # first, then re-read only its rect (one cheap call).
            vh = driver.execute_script("return window.innerHeight")
            if r["cy"] < 0 or r["cy"] > vh:
                driver.execute_script(
                    "document.getElementById('name-input').scrollIntoView({block:'center'})")
                r = driver.execute_script(
                    "const e=document.getElementById('name-input'); const b=e.getBoundingClientRect();"
                    " return {cx: b.x+b.width/2, cy: b.y+b.height/2};")
            pointer = PointerInput(interaction.POINTER_MOUSE, "mouse")
            builder = ActionBuilder(driver, mouse=pointer)
            pointer.create_pointer_move(x=int(r["cx"]), y=int(r["cy"]))
            pointer.create_pointer_down(button=0)
            pointer.create_pointer_up(button=0)
            builder.perform()
            el = driver.find_element(By.ID, "name-input")
            el.send_keys(flow_text[name])
            el.send_keys(Keys.ENTER)
        flow_t = time.monotonic() - t0
        verify = {}
        for name, h in (("win1", win1), ("win2", win2)):
            driver.switch_to.window(h)
            t0 = time.monotonic()
            res = driver.execute_script(
                "return JSON.stringify({value: document.getElementById('name-input').value,"
                " focused: document.activeElement.id,"
                " counter: document.getElementById('counter').textContent,"
                " clicked: window.__clickedIds()})")
            verify[name] = {"verify_read_s": round(time.monotonic() - t0, 4),
                            "data": json.loads(res)}
        log("benchmark_flow_both_windows", t_start,
            flow_s=round(flow_t, 4), texts=flow_text, verify=verify)
    finally:
        try:
            driver.quit()
        except Exception:
            pass
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
    log("run_total", t_start)


if __name__ == "__main__":
    main()
