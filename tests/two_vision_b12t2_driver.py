#!/usr/bin/env python3
"""Batch 12 task 2 driver test for tests/two_vision_bench.py.

Tests the three features that cannot be reached through the plain
CLI happy path, against the local fixture only (never --live, never
a real thread):

1. D3 ref-stale: harvest, rename the message input in the live DOM,
   then send_one must fail fast with ref-stale and send nothing.
2. Cross-window check: inject clone1's message bubble into clone2's
   thread, then cross_window_check must report foreign count 1.
3. Pre-send reservation: seed the ledger with status "sending" for
   an intent, then send_one must refuse with
   retry-blocked-reservation, with and without a visible bubble.

Writes results.json into --workdir and prints JSONL log lines to
stdout; redirect stdout to a log file to preserve the run.

Run with the repo venv python:
  ~/workspace/tools/venv/bin/python tests/two_vision_b12t2_driver.py \
    --workdir /tmp/two_vision_bench/b12t2 \
    > /tmp/two_vision_bench/b12t2.log 2>&1
"""
import argparse
import importlib.util
import json
import os
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = importlib.util.spec_from_file_location(
    "two_vision_bench", os.path.join(HERE, "two_vision_bench.py"))
bench = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bench)


def make_plan(run_id, fixture_name, messages, v12_s=5):
    base = "file://" + os.path.join(
        os.path.dirname(os.path.abspath(__file__)), fixture_name)
    return {
        "run_id": run_id,
        "windows": [
            {"label": "clone1", "url": base + "?clone=1",
             "input_name": "Message", "thread_selector": "#thread"},
            {"label": "clone2", "url": base + "?clone=2",
             "input_name": "Message", "thread_selector": "#thread"},
        ],
        "messages": messages,
        "timeouts": {"v12_gate_s": v12_s},
    }


def main():
    ap = argparse.ArgumentParser(description="batch 12 task 2 driver")
    ap.add_argument("--workdir", default="/tmp/two_vision_bench/b12t2")
    args = ap.parse_args()
    os.makedirs(args.workdir, exist_ok=True)
    t_start = time.monotonic()
    results = {"test": "batch12-task2-features",
               "wall_start": datetime.now(timezone.utc).isoformat(),
               "tests": {}, "outcome": "FAIL"}
    proc = None
    driver = None
    try:
        proc = bench.launch_browser(os.path.join(args.workdir, "profile"))
        driver = bench.attach_driver()

        # Test 1: D3 ref-stale.
        run_id = "bench-b12t2-d3"
        plan = make_plan(run_id, "two_vision_fixture.html", {
            "clone1": "BENCH-TEST clone1 " + run_id,
            "clone2": "BENCH-TEST clone2 " + run_id})
        handles = bench.open_windows(driver, plan, t_start)
        driver.switch_to.window(handles["clone1"])
        items = bench.harvest_window(driver, "clone1", t_start)
        item = bench.find_input(items, "Message")
        driver.execute_script(
            "document.getElementById('msg-input')"
            ".setAttribute('aria-label', 'Renamed');"
            "document.getElementById('msg-input')"
            ".setAttribute('placeholder', 'Renamed');")
        ledger = bench.Ledger(os.path.join(args.workdir, "ledger.json"))
        step = bench.send_one(
            driver, plan["windows"][0], item,
            plan["messages"]["clone1"], run_id + ":clone1",
            ledger, plan, t_start, 1, before_count=0)
        bubbles = driver.execute_script(
            "return window.__sentBubbles().length")
        results["tests"]["d3_ref_stale"] = {
            "error": step.get("error"),
            "expected_name": step.get("evidence", {}).get(
                "expected", {}).get("name"),
            "current_name": step.get("evidence", {}).get(
                "current", {}).get("name"),
            "nearest_count": len(step.get("evidence", {}).get(
                "nearest", [])),
            "bubbles_after": bubbles,
            "pass": step.get("error") == "ref-stale"
            and bubbles == 0
            and len(step.get("evidence", {}).get("nearest", [])) > 0}

        # Test 2: cross-window check.
        run_id2 = "bench-b12t2-xwin"
        plan2 = make_plan(run_id2, "two_vision_fixture.html", {
            "clone1": "BENCH-TEST clone1 " + run_id2,
            "clone2": "BENCH-TEST clone2 " + run_id2})
        handles2 = bench.open_windows(driver, plan2, t_start)
        driver.switch_to.window(handles2["clone2"])
        driver.execute_script(
            "const b = document.createElement('div');"
            "b.className = 'bubble'; b.dataset.sender = 'me';"
            "b.textContent = arguments[0];"
            "document.getElementById('thread').appendChild(b);",
            plan2["messages"]["clone1"])
        check = bench.cross_window_check(
            driver, handles2, plan2, t_start)
        results["tests"]["cross_window"] = {
            "check": check,
            "pass": check["clone2"]["foreign"].get("clone1") == 1
            and check["clone1"]["foreign"].get("clone2") == 0
            and check["clone1"]["own_count"] == 0
            and check["clone2"]["own_count"] == 0}

        # Test 3: pre-send reservation block, bubble absent then
        # present. Same ledger, same intent, fresh page load.
        run_id3 = "bench-b12t2-res"
        plan3 = make_plan(run_id3, "two_vision_fixture.html", {
            "clone1": "BENCH-TEST clone1 " + run_id3,
            "clone2": "BENCH-TEST clone2 " + run_id3})
        handles3 = bench.open_windows(driver, plan3, t_start)
        driver.switch_to.window(handles3["clone1"])
        items3 = bench.harvest_window(driver, "clone1", t_start)
        item3 = bench.find_input(items3, "Message")
        ledger3 = bench.Ledger(
            os.path.join(args.workdir, "ledger-res.json"))
        intent3 = run_id3 + ":clone1"
        ledger3.mark(intent3, "sending", window="clone1",
                     message=plan3["messages"]["clone1"])
        step3a = bench.send_one(
            driver, plan3["windows"][0], item3,
            plan3["messages"]["clone1"], intent3,
            ledger3, plan3, t_start, 1, before_count=0)
        bubbles3a = driver.execute_script(
            "return window.__sentBubbles().length")
        driver.execute_script(
            "const b = document.createElement('div');"
            "b.className = 'bubble'; b.dataset.sender = 'me';"
            "b.textContent = arguments[0];"
            "document.getElementById('thread').appendChild(b);",
            plan3["messages"]["clone1"])
        step3b = bench.send_one(
            driver, plan3["windows"][0], item3,
            plan3["messages"]["clone1"], intent3,
            ledger3, plan3, t_start, 2, before_count=1)
        bubbles3b = driver.execute_script(
            "return window.__sentBubbles().length")
        results["tests"]["reservation_block"] = {
            "absent_error": step3a.get("error"),
            "absent_bubbles": bubbles3a,
            "present_error": step3b.get("error"),
            "present_bubbles": bubbles3b,
            "pass": step3a.get("error") == "retry-blocked-reservation"
            and bubbles3a == 0
            and step3b.get("error") == "retry-blocked-reservation"
            and bubbles3b == 1}

        results["outcome"] = (
            "PASS" if all(t.get("pass")
                          for t in results["tests"].values())
            else "FAIL")
        results["wall_s"] = round(time.monotonic() - t_start, 4)
        out = os.path.join(args.workdir, "results.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        bench.log("b12t2_driver_finished", t_start,
                  outcome=results["outcome"], out=out)
        return 0 if results["outcome"] == "PASS" else 1
    except Exception as exc:
        results["error"] = f"{type(exc).__name__}: {exc}"
        bench.log("harness_error", t_start, error=results["error"])
        out = os.path.join(args.workdir, "results.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        return 2
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


if __name__ == "__main__":
    sys.exit(main())
