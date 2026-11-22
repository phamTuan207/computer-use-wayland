#!/usr/bin/env python3
"""Fix-pass driver test for tests/two_vision_bench.py (batch 12 task 2
council + redteam fix pass).

Reproduces, against the local fixture only (never --live, never a
real thread), the exact scenarios the council and redteam broke:

T1 (redteam F1 / council 1 issue 1, CLI): a failed retry must not
  erase a "sent" ledger record. Run A sends, run B fails with
  target-gone on a tampered inventory, run C (stale fixture, same
  run_id, same workdir, bubble visible) must skip, not re-send.
T2 (redteam F2, CLI): a retry run with zero fresh sends must not
  score PASS; with --allow-resume it may.
T3 (redteam F3, CLI): the same run_id in a fresh workdir must be
  REFUSED by the run registry before the browser starts.
T4 (redteam F5): one Enter appending two identical bubbles must
  fail as duplicate-bubble, not pass.
T5 (redteam F6 / council 1 issue 3): an input replaced by a
  textarea with the same role and name must fail D3 as ref-stale.
T6 (redteam F7): an input moved after the harvest must fail the
  HCU guard as geometry-moved.
T7 (redteam F11, unit): a plan with identical messages must be
  refused by validate_plan.
T8 (council 1 issue 2): a "sent" intent with a broken thread
  selector must fail as thread-missing, never re-send.
T9 (redteam F8): a placeholder-only rename (aria-label unchanged)
  must fail D3 as ref-stale.
T10 (redteam F10): a foreign bubble rendered with a sender prefix
  ("Alice: <message>") must count as cross-window contamination.
T11 (redteam F9): typing into a contenteditable input that never
  sends must time out with v11_mutations 0 (thread-scoped
  observer), not 1.

Writes results.json into --workdir and prints JSONL log lines to
stdout; redirect stdout to a log file to preserve the run.

Run with the repo venv python:
  ~/workspace/tools/venv/bin/python tests/two_vision_fixpass_driver.py \
    --workdir /tmp/two_vision_bench/fixpass \
    > /tmp/two_vision_bench/fixpass.log 2>&1
"""
import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = importlib.util.spec_from_file_location(
    "two_vision_bench", os.path.join(HERE, "two_vision_bench.py"))
bench = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bench)
FIXTURE_DIR = ("file:///home/hatch/workspace/computer-use-wayland/"
               "tests/")


def make_plan(run_id, fixture_name, messages, v12_s=5,
              thread_sel="#thread"):
    return {
        "run_id": run_id,
        "windows": [
            {"label": "clone1", "url": FIXTURE_DIR + fixture_name
             + "?clone=1", "input_name": "Message",
             "thread_selector": thread_sel},
            {"label": "clone2", "url": FIXTURE_DIR + fixture_name
             + "?clone=2", "input_name": "Message",
             "thread_selector": thread_sel},
        ],
        "messages": messages,
        "timeouts": {"v12_gate_s": v12_s},
    }


def run_cli(plan_path, workdir, extra=None):
    """Run the bench CLI once; return (exit_code, stderr_text)."""
    cmd = [sys.executable, os.path.join(HERE, "two_vision_bench.py"),
           "--plan", plan_path, "--workdir", workdir]
    cmd += extra or []
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          timeout=180)
    return proc.returncode, proc.stderr


def write_plan(path, plan):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)


def ledger_status(workdir, intent_id, name="ledger.json"):
    path = os.path.join(workdir, name)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data["intents"].get(intent_id, {}).get("status")


def main():
    ap = argparse.ArgumentParser(description="fix-pass driver test")
    ap.add_argument("--workdir", default="/tmp/two_vision_bench/fixpass")
    args = ap.parse_args()
    os.makedirs(args.workdir, exist_ok=True)
    t_start = time.monotonic()
    results = {"test": "batch12-task2-fixpass",
               "wall_start": datetime.now(timezone.utc).isoformat(),
               "tests": {}, "outcome": "FAIL"}
    proc = None
    driver = None
    try:
        # T1: F1, CLI, three runs.
        run_id1 = "bench-fixpass-f1"
        msgs1 = {"clone1": "BENCH-TEST clone1 bench-stale-001",
                 "clone2": "BENCH-TEST clone2 bench-stale-001"}
        plan1 = make_plan(run_id1, "two_vision_fixture.html", msgs1)
        plan1_path = os.path.join(args.workdir, "plan-f1.json")
        write_plan(plan1_path, plan1)
        wd1 = os.path.join(args.workdir, "f1")
        code_a, _ = run_cli(plan1_path, wd1)
        led_a = ledger_status(wd1, run_id1 + ":clone1")
        # Run B: tampered inventory, clone1 ref does not exist.
        inv = json.load(open(os.path.join(wd1, "inventory.json")))
        for it in inv["clone1"]:
            if it["name"] == "Message":
                it["ref"] = "#does-not-exist"
        tampered = os.path.join(args.workdir, "inventory-f1-bad.json")
        with open(tampered, "w", encoding="utf-8") as f:
            json.dump(inv, f, indent=2)
        code_b, _ = run_cli(plan1_path, wd1,
                            ["--inventory-in", tampered])
        res_b = json.load(open(os.path.join(wd1, "results.json")))
        led_b = ledger_status(wd1, run_id1 + ":clone1")
        # Run C: stale fixture, same run_id/messages/workdir: the
        # seeded bubble is visible, so the preserved "sent" record
        # must skip instead of re-sending.
        plan1c = make_plan(run_id1, "two_vision_fixture_stale.html",
                           msgs1)
        plan1c_path = os.path.join(args.workdir, "plan-f1c.json")
        write_plan(plan1c_path, plan1c)
        code_c, _ = run_cli(plan1c_path, wd1)
        res_c = json.load(open(os.path.join(wd1, "results.json")))
        bubbles_c = res_c["cross_window_check"]["clone1"]["own_count"]
        results["tests"]["f1_guard_sent"] = {
            "run_a_exit": code_a, "ledger_after_a": led_a,
            "run_b_exit": code_b,
            "run_b_step1": res_b["steps"][0].get("status"),
            "run_b_step1_error": res_b["steps"][0].get("error"),
            "ledger_after_b": led_b,
            "run_c_exit": code_c, "run_c_outcome": res_c["outcome"],
            "run_c_steps": [s["status"] for s in res_c["steps"]],
            "run_c_sends_this_run": res_c.get("sends_this_run"),
            "run_c_clone1_own": bubbles_c,
            "pass": code_a == 0 and led_a == "sent"
            and code_b == 1
            and res_b["steps"][0].get("error") == "target-gone"
            and led_b == "sent"
            and res_c["outcome"] == "FAIL"
            and res_c["steps"][0]["status"] == "skipped-already-sent"
            and res_c.get("sends_this_run") == 0
            and bubbles_c == 1}

        # T2: F2, CLI, stale plan twice, then --allow-resume.
        run_id2 = "bench-fixpass-f2"
        plan2 = make_plan(run_id2, "two_vision_fixture_stale.html",
                          msgs1)
        plan2_path = os.path.join(args.workdir, "plan-f2.json")
        write_plan(plan2_path, plan2)
        wd2 = os.path.join(args.workdir, "f2")
        code_2a, _ = run_cli(plan2_path, wd2)
        code_2b, _ = run_cli(plan2_path, wd2)
        res_2b = json.load(open(os.path.join(wd2, "results.json")))
        code_2c, _ = run_cli(plan2_path, wd2, ["--allow-resume"])
        res_2c = json.load(open(os.path.join(wd2, "results.json")))
        results["tests"]["f2_zero_send_no_pass"] = {
            "run1_exit": code_2a,
            "run2_exit": code_2b, "run2_outcome": res_2b["outcome"],
            "run2_steps": [s["status"] for s in res_2b["steps"]],
            "run2_sends_this_run": res_2b.get("sends_this_run"),
            "resume_exit": code_2c,
            "resume_outcome": res_2c["outcome"],
            "pass": code_2a == 0 and code_2b == 1
            and res_2b["outcome"] == "FAIL"
            and res_2b.get("sends_this_run") == 0
            and all(s["status"] == "skipped-already-sent"
                    for s in res_2b["steps"])
            and code_2c == 0 and res_2c["outcome"] == "PASS"}

        # T3: F3, CLI, same run_id in a fresh workdir is refused.
        run_id3 = "bench-fixpass-f3"
        plan3 = make_plan(run_id3, "two_vision_fixture_stale.html",
                          msgs1)
        plan3_path = os.path.join(args.workdir, "plan-f3.json")
        write_plan(plan3_path, plan3)
        wd3a = os.path.join(args.workdir, "f3a")
        wd3b = os.path.join(args.workdir, "f3b")
        code_3a, _ = run_cli(plan3_path, wd3a)
        code_3b, err_3b = run_cli(plan3_path, wd3b)
        results["tests"]["f3_fresh_workdir_refused"] = {
            "run_a_exit": code_3a,
            "run_b_exit": code_3b,
            "run_b_refused": "REFUSED" in err_3b
            and "run_id" in err_3b,
            "run_b_no_results": not os.path.exists(
                os.path.join(wd3b, "results.json")),
            "run_b_no_ledger": not os.path.exists(
                os.path.join(wd3b, "ledger.json")),
            "pass": code_3a == 0 and code_3b == 2
            and "REFUSED" in err_3b
            and not os.path.exists(os.path.join(wd3b, "results.json"))
            and not os.path.exists(os.path.join(wd3b, "ledger.json"))}

        # Shared browser for T4-T6 and T8-T11.
        proc = bench.launch_browser(
            os.path.join(args.workdir, "profile"))
        driver = bench.attach_driver()

        # T4: F5, double append.
        run_id4 = "bench-fixpass-f5"
        plan4 = make_plan(run_id4, "two_vision_fixture_double.html", {
            "clone1": "BENCH-TEST clone1 " + run_id4,
            "clone2": "BENCH-TEST clone2 " + run_id4})
        handles4 = bench.open_windows(driver, plan4, t_start)
        driver.switch_to.window(handles4["clone1"])
        items4 = bench.harvest_window(driver, "clone1", t_start)
        item4 = bench.find_input(items4, "Message")
        ledger4 = bench.Ledger(
            os.path.join(args.workdir, "ledger-f5.json"))
        step4 = bench.send_one(
            driver, plan4["windows"][0], item4,
            plan4["messages"]["clone1"], run_id4 + ":clone1",
            ledger4, plan4, t_start, 1, before_count=0)
        bubbles4 = driver.execute_script(
            "return window.__sentBubbles().length")
        results["tests"]["f5_duplicate_bubble"] = {
            "error": step4.get("error"),
            "gate_baseline": step4.get("gate_baseline"),
            "gate_count": step4.get("gate_count"),
            "bubbles_after": bubbles4,
            "ledger": ledger4.status(run_id4 + ":clone1"),
            "pass": step4.get("error") == "duplicate-bubble"
            and step4.get("gate_count") == 2
            and bubbles4 == 2
            and ledger4.status(run_id4 + ":clone1")
            == "failed-unverified"}

        # T5: F6, tag swap input -> textarea, same role and name.
        run_id5 = "bench-fixpass-f6"
        plan5 = make_plan(run_id5, "two_vision_fixture.html", {
            "clone1": "BENCH-TEST clone1 " + run_id5,
            "clone2": "BENCH-TEST clone2 " + run_id5})
        handles5 = bench.open_windows(driver, plan5, t_start)
        driver.switch_to.window(handles5["clone1"])
        items5 = bench.harvest_window(driver, "clone1", t_start)
        item5 = bench.find_input(items5, "Message")
        driver.execute_script(
            "const old = document.getElementById('msg-input');"
            "const ta = document.createElement('textarea');"
            "ta.id = 'msg-input';"
            "ta.setAttribute('aria-label', 'Message');"
            "ta.setAttribute('placeholder', 'Message');"
            "old.replaceWith(ta);")
        ledger5 = bench.Ledger(
            os.path.join(args.workdir, "ledger-f6.json"))
        step5 = bench.send_one(
            driver, plan5["windows"][0], item5,
            plan5["messages"]["clone1"], run_id5 + ":clone1",
            ledger5, plan5, t_start, 1, before_count=0)
        bubbles5 = driver.execute_script(
            "return [...document.querySelectorAll('#thread .bubble')]"
            ".length")
        ev5 = step5.get("evidence", {})
        results["tests"]["f6_tag_swap"] = {
            "error": step5.get("error"),
            "expected_tag": ev5.get("expected", {}).get("tag"),
            "current_tag": ev5.get("current", {}).get("tag"),
            "bubbles_after": bubbles5,
            "pass": step5.get("error") == "ref-stale"
            and ev5.get("current", {}).get("tag") == "textarea"
            and bubbles5 == 0}

        # T6: F7, input moved 50 px after the harvest.
        run_id6 = "bench-fixpass-f7"
        plan6 = make_plan(run_id6, "two_vision_fixture.html", {
            "clone1": "BENCH-TEST clone1 " + run_id6,
            "clone2": "BENCH-TEST clone2 " + run_id6})
        handles6 = bench.open_windows(driver, plan6, t_start)
        driver.switch_to.window(handles6["clone1"])
        items6 = bench.harvest_window(driver, "clone1", t_start)
        item6 = bench.find_input(items6, "Message")
        driver.execute_script(
            "document.getElementById('msg-input').style.marginTop"
            " = '50px';")
        ledger6 = bench.Ledger(
            os.path.join(args.workdir, "ledger-f7.json"))
        step6 = bench.send_one(
            driver, plan6["windows"][0], item6,
            plan6["messages"]["clone1"], run_id6 + ":clone1",
            ledger6, plan6, t_start, 1, before_count=0)
        bubbles6 = driver.execute_script(
            "return window.__sentBubbles().length")
        results["tests"]["f7_moved_input"] = {
            "error": step6.get("error"),
            "bubbles_after": bubbles6,
            "pass": step6.get("error", "").startswith(
                "geometry-moved") and bubbles6 == 0}

        # T7: F11, unit-level, no browser.
        bad_plan = make_plan("bench-fixpass-f11",
                             "two_vision_fixture.html", {
                                 "clone1": "same message",
                                 "clone2": "same message"})
        try:
            bench.validate_plan(bad_plan)
            f11_raised = None
        except ValueError as exc:
            f11_raised = str(exc)
        results["tests"]["f11_identical_messages"] = {
            "raised": f11_raised,
            "pass": f11_raised is not None
            and "distinct" in f11_raised}

        # T8: council 1 issue 2, broken thread selector + "sent".
        run_id8 = "bench-fixpass-c12"
        plan8 = make_plan(run_id8, "two_vision_fixture.html", {
            "clone1": "BENCH-TEST clone1 " + run_id8,
            "clone2": "BENCH-TEST clone2 " + run_id8},
            thread_sel="#no-such-thread")
        handles8 = bench.open_windows(driver, plan8, t_start)
        driver.switch_to.window(handles8["clone1"])
        items8 = bench.harvest_window(driver, "clone1", t_start)
        item8 = bench.find_input(items8, "Message")
        ledger8 = bench.Ledger(
            os.path.join(args.workdir, "ledger-c12.json"))
        intent8 = run_id8 + ":clone1"
        ledger8.mark(intent8, "sent", window="clone1",
                     message=plan8["messages"]["clone1"])
        step8 = bench.send_one(
            driver, plan8["windows"][0], item8,
            plan8["messages"]["clone1"], intent8,
            ledger8, plan8, t_start, 1, before_count=0)
        bubbles8 = driver.execute_script(
            "return window.__sentBubbles().length")
        results["tests"]["c12_thread_missing"] = {
            "error": step8.get("error"),
            "count_at_precheck": step8.get("count_at_precheck"),
            "bubbles_after": bubbles8,
            "ledger": ledger8.status(intent8),
            "pass": step8.get("error") == "thread-missing"
            and step8.get("count_at_precheck") == -1
            and bubbles8 == 0
            and ledger8.status(intent8) == "sent"}

        # T9: F8, placeholder-only rename, aria-label unchanged.
        run_id9 = "bench-fixpass-f8"
        plan9 = make_plan(run_id9, "two_vision_fixture.html", {
            "clone1": "BENCH-TEST clone1 " + run_id9,
            "clone2": "BENCH-TEST clone2 " + run_id9})
        handles9 = bench.open_windows(driver, plan9, t_start)
        driver.switch_to.window(handles9["clone1"])
        items9 = bench.harvest_window(driver, "clone1", t_start)
        item9 = bench.find_input(items9, "Message")
        driver.execute_script(
            "document.getElementById('msg-input')"
            ".setAttribute('placeholder', 'Renamed');")
        ledger9 = bench.Ledger(
            os.path.join(args.workdir, "ledger-f8.json"))
        step9 = bench.send_one(
            driver, plan9["windows"][0], item9,
            plan9["messages"]["clone1"], run_id9 + ":clone1",
            ledger9, plan9, t_start, 1, before_count=0)
        bubbles9 = driver.execute_script(
            "return window.__sentBubbles().length")
        results["tests"]["f8_placeholder_rename"] = {
            "error": step9.get("error"),
            "bubbles_after": bubbles9,
            "pass": step9.get("error") == "ref-stale"
            and bubbles9 == 0}

        # T10: F10, foreign bubble with a sender prefix.
        run_id10 = "bench-fixpass-f10"
        plan10 = make_plan(run_id10, "two_vision_fixture.html", {
            "clone1": "BENCH-TEST clone1 " + run_id10,
            "clone2": "BENCH-TEST clone2 " + run_id10})
        handles10 = bench.open_windows(driver, plan10, t_start)
        driver.switch_to.window(handles10["clone2"])
        driver.execute_script(
            "const b = document.createElement('div');"
            "b.className = 'bubble'; b.dataset.sender = 'me';"
            "b.textContent = 'Alice: ' + arguments[0];"
            "document.getElementById('thread').appendChild(b);",
            plan10["messages"]["clone1"])
        check10 = bench.cross_window_check(
            driver, handles10, plan10, t_start)
        results["tests"]["f10_prefixed_foreign"] = {
            "check": check10,
            "pass": check10["clone2"]["foreign"].get("clone1") == 1
            and check10["clone2"]["foreign_texts"].get("clone1")
            == ["Alice: " + plan10["messages"]["clone1"]]
            and check10["clone1"]["foreign"].get("clone2") == 0}

        # T11: F9, contenteditable typing with a no-op Enter.
        run_id11 = "bench-fixpass-f9"
        plan11 = make_plan(
            run_id11, "two_vision_fixture_ce_nosend.html", {
                "clone1": "BENCH-TEST clone1 " + run_id11,
                "clone2": "BENCH-TEST clone2 " + run_id11},
            v12_s=2)
        handles11 = bench.open_windows(driver, plan11, t_start)
        driver.switch_to.window(handles11["clone1"])
        items11 = bench.harvest_window(driver, "clone1", t_start)
        item11 = bench.find_input(items11, "Message")
        ledger11 = bench.Ledger(
            os.path.join(args.workdir, "ledger-f9.json"))
        step11 = bench.send_one(
            driver, plan11["windows"][0], item11,
            plan11["messages"]["clone1"], run_id11 + ":clone1",
            ledger11, plan11, t_start, 1, before_count=0)
        results["tests"]["f9_ce_typing_no_mutation"] = {
            "error": step11.get("error"),
            "v11_mutations": step11.get("v11_mutations"),
            "v11_mutation_flag": step11.get("v11_mutation_flag"),
            "v11_scope": step11.get("v11_scope"),
            "v1_value_ok": step11.get("v1_value_ok"),
            "pass": step11.get("error") == "v12-timeout"
            and step11.get("v11_mutations") == 0
            and step11.get("v11_mutation_flag") is False
            and step11.get("v11_scope") == "thread"
            and step11.get("v1_value_ok") is True}

        results["outcome"] = (
            "PASS" if all(t.get("pass")
                          for t in results["tests"].values())
            else "FAIL")
        results["wall_s"] = round(time.monotonic() - t_start, 4)
        out = os.path.join(args.workdir, "results.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        bench.log("fixpass_driver_finished", t_start,
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
