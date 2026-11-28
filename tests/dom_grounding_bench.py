#!/usr/bin/env python3
"""DOM/a11y grounding benchmark, batch 7 task 2.

Measures, on real headless Firefox 160.0.1, how fast exact element
rects come out of the DOM (one observation, many elements) over
Marionette (Selenium) and over raw WebDriver BiDi, how much a
screenshot costs in comparison, and whether one rect snapshot can
drive several real pointer clicks verified by a cheap DOM read.
It also times Selenium 4.53 accessibility snapshots (whole page
and one element) and a warm BiDi session.new, and it handles a
BiDi rect item without an "id" defensively instead of crashing
(run 1 crashed on exactly that, KeyError 'id', flaky).

Every step prints one JSON line: wall clock (UTC) and elapsed seconds
from a monotonic clock. Run with the repo venv python.
"""
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone

FF = os.path.expanduser("~/workspace/tools/firefox/firefox")
GD = os.path.expanduser("~/workspace/tools/geckodriver")
FIXTURE = "file://" + os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "dom_grounding_fixture.html")
BIDI_PORT = 9223

RECT_JS = """
const els = [...document.querySelectorAll('button, input, select, a')];
return els.map(e => {
  const r = e.getBoundingClientRect();
  return {id: e.id, tag: e.tagName, x: r.x, y: r.y, w: r.width, h: r.height,
          cx: r.x + r.width / 2, cy: r.y + r.height / 2,
          visible: r.width > 0 && r.height > 0};
});
"""

# Same read, but the result is a JSON string, because BiDi RemoteValue
# serializes objects as [key, value] pairs instead of plain objects.
BIDI_RECT_JS = """
(function(){
  const els = [...document.querySelectorAll('button, input, select, a')];
  return JSON.stringify(els.map(e => {
    const r = e.getBoundingClientRect();
    return {id: e.id, tag: e.tagName, x: r.x, y: r.y, w: r.width, h: r.height,
            cx: r.x + r.width / 2, cy: r.y + r.height / 2,
            visible: r.width > 0 && r.height > 0};
  }));
})()
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


def main():
    from selenium import webdriver
    from selenium.webdriver.firefox.service import Service
    from selenium.webdriver.common.by import By

    t_start = time.monotonic()
    # Launch Firefox by hand: -marionette plus --remote-debugging-port
    # on the command line (the port flag is rejected via capabilities),
    # then attach Selenium with geckodriver --connect-existing.
    profile = "/tmp/dom_grounding_profile"
    import os
    os.makedirs(profile, exist_ok=True)
    t0 = time.monotonic()
    proc = subprocess.Popen(
        [FF, "-headless", "-marionette",
         f"--remote-debugging-port={BIDI_PORT}",
         "-profile", profile, "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.time() + 30
    while time.time() < deadline:
        if port_open(2828) and port_open(BIDI_PORT):
            break
        time.sleep(0.25)
    if not (port_open(2828) and port_open(BIDI_PORT)):
        proc.kill()
        raise RuntimeError("browser ports did not open in 30 s")
    log("browser_launch_manual", t0, pid=proc.pid)
    service = Service(GD, log_output="/tmp/dom_grounding_geckodriver.log",
                      service_args=["--connect-existing", "--marionette-port", "2828"])
    t0 = time.monotonic()
    driver = webdriver.Firefox(service=service)
    driver.set_window_size(1280, 900)
    log("marionette_attach_session", t0)
    try:
        t0 = time.monotonic()
        driver.get(FIXTURE)
        log("navigate_fixture", t0)
        n = driver.execute_script("return document.querySelectorAll('button, input, select, a').length")
        log("count_interactive", t0, count=n)

        # 1. Marionette: one observation, all rects, 3 runs.
        times = []
        for i in range(3):
            t0 = time.monotonic()
            rects = driver.execute_script(RECT_JS)
            times.append(time.monotonic() - t0)
        log("marionette_one_shot_all_rects", t_start, runs=[round(x, 4) for x in times],
            median_s=round(median(times), 4), elements=len(rects))
        marionette_rects = {r["id"]: r for r in rects}

        # 2. Marionette: per-element rect calls, 66 round trips, 1 run (slow).
        t0 = time.monotonic()
        per = {}
        els = driver.find_elements(By.CSS_SELECTOR, "button, input, select, a")
        for e in els:
            r = e.rect
            per[e.get_attribute("id")] = {"x": r["x"], "y": r["y"], "w": r["width"], "h": r["height"]}
        t_per = time.monotonic() - t0
        log("marionette_per_element_rects", t_start, elapsed_s=round(t_per, 4),
            elements=len(per), per_element_ms=round(t_per / max(len(per), 1) * 1000, 2))

        # 3. Rect agreement: one-shot vs per-element, max delta.
        worst = 0.0
        worst_id = None
        for k, v in per.items():
            m = marionette_rects.get(k)
            if not m:
                continue
            d = max(abs(v["x"] - m["x"]), abs(v["y"] - m["y"]),
                    abs(v["w"] - m["w"]), abs(v["h"] - m["h"]))
            if d > worst:
                worst, worst_id = d, k
        log("rect_agreement_one_shot_vs_per_element", t_start,
            max_delta_px=worst, worst_id=worst_id)

        # 4. Screenshot cost, 3 runs.
        times = []
        sizes = []
        for i in range(3):
            t0 = time.monotonic()
            png = driver.get_screenshot_as_png()
            times.append(time.monotonic() - t0)
            sizes.append(len(png))
        log("screenshot_png", t_start, runs=[round(x, 4) for x in times],
            median_s=round(median(times), 4), bytes=sizes[0])

        # 4b. Accessibility snapshot (Selenium 4.53): whole page and
        # one element, timed. The snapshot is computed from the DOM
        # following WAI-ARIA, html-aam and accname; it is not the
        # browser's own accessibility tree. Node count counts the
        # returned tree recursively. json_chars is the length of
        # json.dumps of a compact recursive projection
        # {role, name, children} of the whole-page tree.
        def count_nodes(node):
            return 1 + sum(count_nodes(c) for c in (node.children or []))

        def compact(node):
            return {"role": node.role, "name": node.name,
                    "children": [compact(c) for c in (node.children or [])]}

        times = []
        nodes = None
        json_chars = None
        to_text_chars = None
        for i in range(3):
            t0 = time.monotonic()
            tree = driver.accessibility_snapshot()
            times.append(time.monotonic() - t0)
            if i == 0:
                nodes = count_nodes(tree)
                json_chars = len(json.dumps(compact(tree)))
                to_text_chars = len(tree.to_text())
        log("a11y_snapshot_page", t_start, runs=[round(x, 4) for x in times],
            median_s=round(median(times), 4), nodes=nodes,
            json_chars=json_chars, to_text_chars=to_text_chars)
        t0 = time.monotonic()
        el = driver.find_element(By.ID, "btn-42")
        one = el.accessibility_snapshot()
        one_t = time.monotonic() - t0
        log("a11y_snapshot_one_element", t_start, elapsed_s=round(one_t, 4),
            role=one.role, node_name=one.name,
            has_element_handle=one.element is not None)

        # 5. BiDi while a Marionette session is active on the same
        # browser: Firefox 160 allows one active session in total.
        import websocket
        ws = websocket.create_connection(f"ws://127.0.0.1:{BIDI_PORT}/session",
                                         timeout=10, suppress_origin=True)
        try:
            _mid = [0]

            def bidi(method, params):
                _mid[0] += 1
                mid = _mid[0]
                ws.send(json.dumps({"id": mid, "method": method, "params": params}))
                while True:
                    msg = json.loads(ws.recv())
                    if msg.get("id") == mid:
                        return msg
            t0 = time.monotonic()
            r = bidi("session.new", {"capabilities": {}})
            log("bidi_session_new_while_marionette_active", t0,
                ok="result" in r,
                error=r.get("error"), message=(r.get("message") or "")[:200])
        finally:
            ws.close()

        # 6. One observation drives many actions: rect snapshot once,
        # then 5 real pointer clicks at rect centers, verified by one
        # cheap DOM read (no re-observation of the page).
        targets = ["btn-3", "btn-17", "btn-42", "moved", "scroll-btn"]
        t0 = time.monotonic()
        snap = driver.execute_script(RECT_JS)
        snap_t = time.monotonic() - t0
        by_id = {r["id"]: r for r in snap}
        # Click at absolute viewport coordinates taken ONLY from the
        # snapshot, using the W3C pointer action (move_to_location).
        # scroll-btn is below the fold, so scroll it into view first and
        # re-read only its rect (one cheap call, not a full snapshot).
        from selenium.webdriver.common.actions.action_builder import ActionBuilder
        from selenium.webdriver.common.actions.pointer_input import PointerInput
        from selenium.webdriver.common.actions import interaction
        t0 = time.monotonic()
        vh = driver.execute_script("return window.innerHeight")
        for tid in targets:
            r = by_id[tid]
            # Any target below the fold must be scrolled into view first,
            # then only its own rect is re-read (one cheap call).
            if r["cy"] < 0 or r["cy"] > vh:
                driver.execute_script(
                    f"document.getElementById('{tid}').scrollIntoView({{block:'center'}})")
                r = driver.execute_script(
                    f"const e=document.getElementById('{tid}'); const b=e.getBoundingClientRect();"
                    " return {cx: b.x+b.width/2, cy: b.y+b.height/2};")
            pointer = PointerInput(interaction.POINTER_MOUSE, "mouse")
            builder = ActionBuilder(driver, mouse=pointer)
            pointer.create_pointer_move(x=int(r["cx"]), y=int(r["cy"]))
            pointer.create_pointer_down(button=0)
            pointer.create_pointer_up(button=0)
            builder.perform()
        click_t = time.monotonic() - t0
        t0 = time.monotonic()
        clicked = driver.execute_script("return window.__clickedIds()")
        counter = driver.execute_script("return document.getElementById('counter').textContent")
        verify_t = time.monotonic() - t0
        log("one_snapshot_five_clicks", t_start, snapshot_s=round(snap_t, 4),
            clicks_s=round(click_t, 4), verify_read_s=round(verify_t, 4),
            targets=targets, clicked_log=clicked, counter=counter,
            all_five_landed=all(t in clicked for t in targets))

        # 7. DOM click (no pointer) on 5 more, verify by one DOM read.
        t0 = time.monotonic()
        driver.execute_script(
            "['btn-0','btn-1','btn-2','btn-4','btn-5'].forEach(id => document.getElementById(id).click())")
        dom_t = time.monotonic() - t0
        t0 = time.monotonic()
        clicked2 = driver.execute_script("return window.__clickedIds()")
        verify2_t = time.monotonic() - t0
        log("dom_clicks_five_verify_one_read", t_start, clicks_s=round(dom_t, 4),
            verify_read_s=round(verify2_t, 4), total_clicks_logged=len(clicked2.split(";")) - 1)
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

    # 8. BiDi in its own browser instance (no Marionette session):
    # same fixture, same 1280x900 viewport, one-shot rect read x3.
    bidi_port = 9224
    profile2 = "/tmp/dom_grounding_profile2"
    import os
    os.makedirs(profile2, exist_ok=True)
    t0 = time.monotonic()
    proc2 = subprocess.Popen(
        [FF, "-headless", f"--remote-debugging-port={bidi_port}",
         "-profile", profile2, "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.time() + 30
    while time.time() < deadline:
        if port_open(bidi_port):
            break
        time.sleep(0.25)
    if not port_open(bidi_port):
        proc2.kill()
        raise RuntimeError("bidi port did not open in 30 s")
    log("browser_launch_bidi_only", t0, pid=proc2.pid)
    import websocket
    ws = websocket.create_connection(f"ws://127.0.0.1:{bidi_port}/session",
                                     timeout=10, suppress_origin=True)
    try:
        _mid = [0]

        def bidi(method, params):
            _mid[0] += 1
            mid = _mid[0]
            ws.send(json.dumps({"id": mid, "method": method, "params": params}))
            while True:
                msg = json.loads(ws.recv())
                if msg.get("id") == mid:
                    return msg
        t0 = time.monotonic()
        r = bidi("session.new", {"capabilities": {}})
        log("bidi_session_new_alone", t0, ok="result" in r)
        r = bidi("browsingContext.getTree", {})
        ctx = r["result"]["contexts"][0]["context"]
        r = bidi("browsingContext.setViewport",
                 {"context": ctx, "viewport": {"width": 1280, "height": 900}})
        log("bidi_set_viewport", t0, ok="result" in r)
        t0 = time.monotonic()
        r = bidi("browsingContext.navigate",
                 {"context": ctx, "url": FIXTURE, "wait": "complete"})
        log("bidi_navigate_fixture", t0, ok="result" in r)
        times = []
        bidi_rects = None
        for i in range(3):
            t0 = time.monotonic()
            r = bidi("script.evaluate", {
                # Return a JSON string: BiDi RemoteValue serializes
                # objects as [key, value] pairs, so a plain object
                # round trip is awkward; a string avoids that.
                "expression": BIDI_RECT_JS,
                "target": {"context": ctx},
                "awaitPromise": False,
                "resultOwnership": "none",
            })
            times.append(time.monotonic() - t0)
            if "result" in r:
                raw = r["result"]["result"].get("value")
                if isinstance(raw, str):
                    bidi_rects = json.loads(raw)
        log("bidi_one_shot_all_rects", t_start, runs=[round(x, 4) for x in times],
            median_s=round(median(times), 4),
            elements=len(bidi_rects) if isinstance(bidi_rects, list) else None,
            error=r.get("error"))
        if isinstance(bidi_rects, list):
            # Defensive: a BiDi evaluate result item is expected to
            # carry "id", but run 1 of this bench crashed here with
            # KeyError 'id' (flaky, not reproduced since). Skip items
            # without an id and record how many were skipped instead
            # of crashing the whole run.
            skipped = sum(1 for x in bidi_rects
                          if not (isinstance(x, dict) and "id" in x))
            bm = {x["id"]: x for x in bidi_rects
                  if isinstance(x, dict) and "id" in x}
            log("bidi_rects_without_id", t_start, skipped=skipped,
                total=len(bidi_rects))
            worst = 0.0
            worst_id = None
            for k, v in bm.items():
                m = marionette_rects.get(k)
                if not m:
                    continue
                d = max(abs(v["x"] - m["x"]), abs(v["y"] - m["y"]),
                        abs(v["w"] - m["w"]), abs(v["h"] - m["h"]))
                if d > worst:
                    worst, worst_id = d, k
            log("rect_agreement_bidi_vs_marionette", t_start,
                max_delta_px=worst, worst_id=worst_id)
        # BiDi DOM click on 3 buttons, verify by one evaluate read.
        t0 = time.monotonic()
        r = bidi("script.evaluate", {
            "expression": "['btn-10','btn-11','btn-12'].forEach(id => document.getElementById(id).click()); document.getElementById('counter').textContent",
            "target": {"context": ctx},
            "awaitPromise": False,
            "resultOwnership": "none",
        })
        log("bidi_dom_clicks_three_verify_one_read", t_start,
            elapsed_s=round(time.monotonic() - t0, 4),
            counter=r.get("result", {}).get("result", {}).get("value"))
    finally:
        ws.close()
        proc2.terminate()
        try:
            proc2.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc2.kill()
    # 9. Warm BiDi session.new: same fresh browser launch, but wait
    # 5 s after the remote-debugging port opens before connecting,
    # so the remote agent is already warm. This separates the
    # first-session cost (measured in step 8) from the steady-state
    # session.new cost.
    bidi_port3 = 9225
    profile3 = "/tmp/dom_grounding_profile3"
    import os
    os.makedirs(profile3, exist_ok=True)
    proc3 = subprocess.Popen(
        [FF, "-headless", f"--remote-debugging-port={bidi_port3}",
         "-profile", profile3, "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        deadline = time.time() + 30
        while time.time() < deadline:
            if port_open(bidi_port3):
                break
            time.sleep(0.25)
        if not port_open(bidi_port3):
            raise RuntimeError("warm bidi port did not open in 30 s")
        time.sleep(5)
        ws3 = websocket.create_connection(f"ws://127.0.0.1:{bidi_port3}/session",
                                          timeout=10, suppress_origin=True)
        try:
            t0 = time.monotonic()
            ws3.send(json.dumps({"id": 1, "method": "session.new",
                                 "params": {"capabilities": {}}}))
            msg = json.loads(ws3.recv())
            log("bidi_session_new_warm", t_start,
                elapsed_s=round(time.monotonic() - t0, 4),
                ok="result" in msg)
        finally:
            ws3.close()
    finally:
        proc3.terminate()
        try:
            proc3.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc3.kill()
    log("run_total", t_start)


if __name__ == "__main__":
    main()
