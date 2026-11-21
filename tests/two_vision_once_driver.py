#!/usr/bin/env python3
"""Exactly-once driver test for tests/two_vision_bench.py.

Calls send_one twice with the SAME intent id and message in ONE
browser session, against the local fixture only (never --live, never
a real thread). Proves the second call is skipped-already-sent and
the bubble count stays 1. Writes results.json into --workdir and
prints JSONL log lines to stdout; redirect stdout to a log file to
preserve the run.

Run with the repo venv python:
  ~/workspace/tools/venv/bin/python tests/two_vision_once_driver.py \
    --workdir /tmp/two_vision_bench/once2 \
    > /tmp/two_vision_bench/once2.log 2>&1
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


def main():
    ap = argparse.ArgumentParser(description="exactly-once driver test")
    ap.add_argument("--workdir", default="/tmp/two_vision_bench/once2")
    args = ap.parse_args()
    os.makedirs(args.workdir, exist_ok=True)
    t_start = time.monotonic()
    run_id = "bench-once-20261122"
    plan = {
        "run_id": run_id,
        "windows": [
            {"label": "clone1",
             "url": bench.FIXTURE + "?clone=1",
             "input_name": "Message", "thread_selector": "#thread"},
            {"label": "clone2",
             "url": bench.FIXTURE + "?clone=2",
             "input_name": "Message", "thread_selector": "#thread"},
        ],
        "messages": {
            "clone1": "BENCH-ONCE clone1 " + run_id,
            "clone2": "BENCH-ONCE clone2 " + run_id,
        },
        "timeouts": {"v12_gate_s": 5},
    }
    ledger = bench.Ledger(os.path.join(args.workdir, "ledger.json"))
    results = {"run_id": run_id, "test": "exactly-once-same-intent-twice",
               "wall_start": datetime.now(timezone.utc).isoformat(),
               "calls": [], "outcome": "FAIL"}
    proc = None
    driver = None
    try:
        proc = bench.launch_browser(os.path.join(args.workdir, "profile"))
        driver = bench.attach_driver()
        handles = bench.open_windows(driver, plan, t_start)
        driver.switch_to.window(handles["clone1"])
        items = bench.harvest_window(driver, "clone1", t_start)
        item = bench.find_input(items, "Message")
        if item is None:
            raise RuntimeError("no message input in harvest")
        window = plan["windows"][0]
        message = plan["messages"]["clone1"]
        intent_id = run_id + ":clone1"
        t1 = time.monotonic()
        first = bench.send_one(driver, window, item, message,
                               intent_id, ledger, plan, t_start, 1)
        first_s = round(time.monotonic() - t1, 4)
        bubbles1 = driver.execute_script(
            "return window.__sentBubbles().length")
        t2 = time.monotonic()
        second = bench.send_one(driver, window, item, message,
                                intent_id, ledger, plan, t_start, 2)
        second_s = round(time.monotonic() - t2, 4)
        bubbles2 = driver.execute_script(
            "return window.__sentBubbles().length")
        results["calls"] = [
            {"call": 1, "status": first["status"],
             "elapsed_s": first_s, "bubbles_after": bubbles1},
            {"call": 2, "status": second["status"],
             "elapsed_s": second_s, "bubbles_after": bubbles2},
        ]
        results["outcome"] = (
            "PASS" if first["status"] == "sent"
            and second["status"] == "skipped-already-sent"
            and bubbles1 == 1 and bubbles2 == 1 else "FAIL")
        results["wall_s"] = round(time.monotonic() - t_start, 4)
        out = os.path.join(args.workdir, "results.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        bench.log("once_driver_finished", t_start,
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
