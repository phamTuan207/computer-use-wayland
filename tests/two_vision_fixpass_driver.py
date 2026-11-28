#!/usr/bin/env python3
"""Fix-pass driver test for tests/two_vision_bench.py (batch 12 task 2
council + redteam fix pass).

Reproduces, against the local fixture only (never --live, never a
real thread), the exact scenarios the council and redteam broke:

T1 (redteam F1 / council 1 issue 1, CLI): a retry must not
  erase a "sent" ledger record. Run A sends on the stale
  fixture, run B (same run_id, same workdir, bubble visible)
  must skip, not re-send, and the ledger must stay "sent".
  Run B2 (fresh run_id, tampered inventory) must still fail
  with target-gone, proving D3 fires when no "sent" record
  blocks it. Unit check: the ledger state machine refuses to
  overwrite "sent" with "failed-unverified" or "failed".
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
T12 (redteam round 2 finding 1): harvest-then-run with the same
  run_id in different workdirs must succeed: the harvest binds
  no registry entry, the run binds it.
T13 (redteam round 2 finding 2): a "sent" intent whose bubble is
  absent (fresh page load, count 0) must refuse with
  retry-blocked-sent-bubble-absent, never re-send.
T14 (redteam round 2 finding 3): the same run_id with a changed
  message must refuse with retry-blocked-intent-changed, and the
  ledger record must keep the original message.
T15 (redteam round 2 finding 4): one Enter appending a second
  identical bubble 700 ms later must fail as duplicate-bubble;
  the gate settles a full second after first sighting. Runs on
  the shared browser before the CLI tests (T12 and later), which
  each launch their own Firefox.
T16 (redteam round 2 finding 5): results.json records the
  registry state: registry_enabled false with --no-run-registry,
  true with the default path otherwise.
T17 (redteam round 2 finding 15): validate_plan refuses
  messages where one is a substring of the other.
T18 (council 1 finding 2): a no-send run's outcome_note must
  name the actual failure, never claim both steps skipped.
T19 (fix pass 2 state machine, unit, inside T1): Ledger.mark
  refuses to overwrite "sent", and reserve() is atomic (second
  call False).
T20 (council 1 finding 10a): a corrupt registry or ledger file
  is REFUSED with exit 2, never treated as empty.

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
FIXTURE_DIR = ("file://" + os.path.dirname(os.path.abspath(__file__))
               + "/")


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
    # Settle delay (fix pass 2, redteam 4/4 finding 10f): a
    # just-exited Firefox can still hold the Marionette/BiDi ports
    # when the next CLI run starts, failing it spuriously.
    time.sleep(1.0)
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
        # T1: F1, CLI, three runs. Run A sends on the stale
        # fixture (seeded bubble + one new bubble past the gate).
        run_id1 = "bench-fixpass-f1"
        msgs1 = {"clone1": "BENCH-TEST clone1 bench-stale-001",
                 "clone2": "BENCH-TEST clone2 bench-stale-001"}
        plan1 = make_plan(run_id1, "two_vision_fixture_stale.html",
                          msgs1)
        plan1_path = os.path.join(args.workdir, "plan-f1.json")
        write_plan(plan1_path, plan1)
        wd1 = os.path.join(args.workdir, "f1")
        code_a, _ = run_cli(plan1_path, wd1)
        led_a = ledger_status(wd1, run_id1 + ":clone1")
        # Run B: same run_id, same workdir, stale fixture: the
        # seeded bubble is visible, so the preserved "sent" record
        # must skip instead of re-sending.
        code_b, _ = run_cli(plan1_path, wd1)
        res_b = json.load(open(os.path.join(wd1, "results.json")))
        led_b = ledger_status(wd1, run_id1 + ":clone1")
        bubbles_b = res_b["cross_window_check"]["clone1"]["own_count"]
        # Run B2: fresh run_id, tampered inventory, clone1 ref
        # does not exist: D3 must still fail with target-gone when
        # no "sent" record blocks it.
        inv = json.load(open(os.path.join(wd1, "inventory.json")))
        for it in inv["clone1"]:
            if it["name"] == "Message":
                it["ref"] = "#does-not-exist"
        tampered = os.path.join(args.workdir, "inventory-f1-bad.json")
        with open(tampered, "w", encoding="utf-8") as f:
            json.dump(inv, f, indent=2)
        run_id1b = "bench-fixpass-f1b"
        plan1b = make_plan(run_id1b, "two_vision_fixture.html", {
            "clone1": "BENCH-TEST clone1 " + run_id1b,
            "clone2": "BENCH-TEST clone2 " + run_id1b})
        plan1b_path = os.path.join(args.workdir, "plan-f1b.json")
        write_plan(plan1b_path, plan1b)
        code_b2, _ = run_cli(plan1b_path, wd1,
                             ["--inventory-in", tampered])
        res_b2 = json.load(open(os.path.join(wd1, "results.json")))
        led_b2 = ledger_status(wd1, run_id1b + ":clone1")
        # Unit: the ledger state machine refuses to overwrite
        # "sent" with "failed-unverified" or "failed", and a
        # second reserve() on one intent returns False.
        ledger_u = bench.Ledger(
            os.path.join(args.workdir, "ledger-f1-unit.json"))
        unit_ok = (ledger_u.mark("u:clone1", "sent", message="m")
                   is True
                   and ledger_u.mark("u:clone1", "failed-unverified")
                   is False
                   and ledger_u.mark("u:clone1", "failed") is False
                   and ledger_u.status("u:clone1") == "sent"
                   and ledger_u.reserve("v:clone1", message="m")
                   is True
                   and ledger_u.reserve("v:clone1", message="m")
                   is False)
        results["tests"]["f1_guard_sent"] = {
            "run_a_exit": code_a, "ledger_after_a": led_a,
            "run_b_exit": code_b,
            "run_b_steps": [s["status"] for s in res_b["steps"]],
            "run_b_sends_this_run": res_b.get("sends_this_run"),
            "run_b_clone1_own": bubbles_b,
            "ledger_after_b": led_b,
            "run_b2_exit": code_b2,
            "run_b2_step1_error": res_b2["steps"][0].get("error"),
            "ledger_after_b2": led_b2,
            "state_machine_unit": unit_ok,
            "pass": code_a == 0 and led_a == "sent"
            and code_b == 1
            and res_b["outcome"] == "FAIL"
            and all(s["status"] == "skipped-already-sent"
                    for s in res_b["steps"])
            and res_b.get("sends_this_run") == 0
            and bubbles_b == 1 and led_b == "sent"
            and code_b2 == 1
            and res_b2["steps"][0].get("error") == "target-gone"
            and led_b2 == "failed"
            and unit_ok}

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

        # T15: round 2 finding 4, delayed double append. Runs
        # here, on the shared browser, before the CLI tests: a
        # CLI run launches its own Firefox, and launch_browser
        # refuses while the shared browser holds the
        # Marionette/BiDi ports.
        run_id15 = "bench-fixpass-r2f4"
        plan15 = make_plan(
            run_id15, "two_vision_fixture_delayed_double.html", {
                "clone1": "BENCH-TEST clone1 " + run_id15,
                "clone2": "BENCH-TEST clone2 " + run_id15})
        handles15 = bench.open_windows(driver, plan15, t_start)
        driver.switch_to.window(handles15["clone1"])
        items15 = bench.harvest_window(driver, "clone1", t_start)
        item15 = bench.find_input(items15, "Message")
        ledger15 = bench.Ledger(
            os.path.join(args.workdir, "ledger-r2f4.json"))
        step15 = bench.send_one(
            driver, plan15["windows"][0], item15,
            plan15["messages"]["clone1"], run_id15 + ":clone1",
            ledger15, plan15, t_start, 1, before_count=0)
        bubbles15 = driver.execute_script(
            "return window.__sentBubbles().length")
        results["tests"]["r2f4_delayed_double"] = {
            "error": step15.get("error"),
            "gate_baseline": step15.get("gate_baseline"),
            "gate_count": step15.get("gate_count"),
            "gate_settle_s": step15.get("gate_settle_s"),
            "bubbles_after": bubbles15,
            "ledger": ledger15.status(run_id15 + ":clone1"),
            "pass": step15.get("error") == "duplicate-bubble"
            and step15.get("gate_count") == 2
            and step15.get("gate_settle_s") == 1.0
            and bubbles15 == 2
            and ledger15.status(run_id15 + ":clone1")
            == "failed-unverified"}

        # Quit the shared browser before the CLI tests below
        # (fix pass 2, redteam 4/4 finding 10f): each CLI run
        # launches its own Firefox, and launch_browser refuses
        # while the Marionette/BiDi ports are held.
        try:
            driver.quit()
        except Exception:
            pass
        driver = None
        try:
            proc.terminate()
            proc.wait(timeout=10)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        proc = None
        time.sleep(1.0)

        # T12: round 2 finding 1, CLI: harvest-then-run, same
        # run_id, different workdirs. The harvest must bind no
        # registry entry, so the run in its own workdir succeeds.
        run_id12 = "bench-fixpass-r2f1"
        plan12 = make_plan(run_id12, "two_vision_fixture_stale.html",
                           msgs1)
        plan12_path = os.path.join(args.workdir, "plan-r2f1.json")
        write_plan(plan12_path, plan12)
        wd12h = os.path.join(args.workdir, "r2f1-harvest")
        wd12r = os.path.join(args.workdir, "r2f1-run")
        code_12h, _ = run_cli(plan12_path, wd12h,
                              ["--mode", "harvest"])
        res_12h = json.load(open(os.path.join(wd12h, "results.json")))
        code_12r, _ = run_cli(plan12_path, wd12r)
        res_12r = json.load(open(os.path.join(wd12r, "results.json")))
        results["tests"]["r2f1_harvest_then_run"] = {
            "harvest_exit": code_12h,
            "harvest_outcome": res_12h.get("outcome"),
            "harvest_registry_enabled":
                res_12h.get("registry_enabled"),
            "run_exit": code_12r,
            "run_outcome": res_12r.get("outcome"),
            "run_registry_enabled": res_12r.get("registry_enabled"),
            "pass": code_12h == 0
            and res_12h.get("outcome") == "HARVEST-ONLY"
            and res_12h.get("registry_enabled") is False
            and code_12r == 0
            and res_12r.get("outcome") == "PASS"
            and res_12r.get("registry_enabled") is True}

        # T13: round 2 finding 2, CLI: a "sent" intent whose
        # bubble is absent (fresh page load, count 0) must refuse,
        # never re-send.
        run_id13 = "bench-fixpass-r2f2"
        msgs13 = {"clone1": "BENCH-TEST clone1 " + run_id13,
                  "clone2": "BENCH-TEST clone2 " + run_id13}
        plan13 = make_plan(run_id13, "two_vision_fixture.html", msgs13)
        plan13_path = os.path.join(args.workdir, "plan-r2f2.json")
        write_plan(plan13_path, plan13)
        wd13 = os.path.join(args.workdir, "r2f2")
        code_13a, _ = run_cli(plan13_path, wd13)
        code_13b, _ = run_cli(plan13_path, wd13)
        res_13b = json.load(open(os.path.join(wd13, "results.json")))
        results["tests"]["r2f2_sent_bubble_absent"] = {
            "run_a_exit": code_13a,
            "run_b_exit": code_13b,
            "run_b_step1_error": res_13b["steps"][0].get("error"),
            "run_b_sends_this_run": res_13b.get("sends_this_run"),
            "ledger": ledger_status(wd13, run_id13 + ":clone1"),
            "pass": code_13a == 0 and code_13b == 1
            and res_13b["steps"][0].get("error")
            == "retry-blocked-sent-bubble-absent"
            and res_13b.get("sends_this_run") == 0
            and ledger_status(wd13, run_id13 + ":clone1") == "sent"}

        # T14: round 2 finding 3, CLI: the same run_id with a
        # changed message must refuse, and the ledger record must
        # keep the original message.
        run_id14 = "bench-fixpass-r2f3"
        msgs14 = {"clone1": "BENCH-TEST clone1 " + run_id14,
                  "clone2": "BENCH-TEST clone2 " + run_id14}
        plan14 = make_plan(run_id14, "two_vision_fixture.html", msgs14)
        plan14_path = os.path.join(args.workdir, "plan-r2f3.json")
        write_plan(plan14_path, plan14)
        wd14 = os.path.join(args.workdir, "r2f3")
        code_14a, _ = run_cli(plan14_path, wd14)
        msgs14b = {"clone1": "BENCH-TEST clone1 " + run_id14
                   + "-DIFFERENT",
                   "clone2": "BENCH-TEST clone2 " + run_id14
                   + "-DIFFERENT"}
        plan14b = make_plan(run_id14, "two_vision_fixture.html",
                            msgs14b)
        plan14b_path = os.path.join(args.workdir, "plan-r2f3b.json")
        write_plan(plan14b_path, plan14b)
        code_14b, _ = run_cli(plan14b_path, wd14)
        res_14b = json.load(open(os.path.join(wd14, "results.json")))
        rec14 = json.load(open(os.path.join(wd14, "ledger.json")))[
            "intents"].get(run_id14 + ":clone1", {})
        results["tests"]["r2f3_intent_changed"] = {
            "run_a_exit": code_14a,
            "run_b_exit": code_14b,
            "run_b_step1_error": res_14b["steps"][0].get("error"),
            "run_b_sends_this_run": res_14b.get("sends_this_run"),
            "ledger_status": rec14.get("status"),
            "ledger_message": rec14.get("message"),
            "pass": code_14a == 0 and code_14b == 1
            and res_14b["steps"][0].get("error")
            == "retry-blocked-intent-changed"
            and res_14b.get("sends_this_run") == 0
            and rec14.get("status") == "sent"
            and rec14.get("message") == msgs14["clone1"]}

        # T16: round 2 finding 5, CLI: results.json records the
        # registry state.
        run_id16a = "bench-fixpass-r2f5a"
        plan16a = make_plan(run_id16a, "two_vision_fixture.html", {
            "clone1": "BENCH-TEST clone1 " + run_id16a,
            "clone2": "BENCH-TEST clone2 " + run_id16a})
        plan16a_path = os.path.join(args.workdir, "plan-r2f5a.json")
        write_plan(plan16a_path, plan16a)
        wd16a = os.path.join(args.workdir, "r2f5a")
        code_16a, _ = run_cli(plan16a_path, wd16a,
                              ["--no-run-registry"])
        res_16a = json.load(open(os.path.join(wd16a, "results.json")))
        run_id16b = "bench-fixpass-r2f5b"
        plan16b = make_plan(run_id16b, "two_vision_fixture.html", {
            "clone1": "BENCH-TEST clone1 " + run_id16b,
            "clone2": "BENCH-TEST clone2 " + run_id16b})
        plan16b_path = os.path.join(args.workdir, "plan-r2f5b.json")
        write_plan(plan16b_path, plan16b)
        wd16b = os.path.join(args.workdir, "r2f5b")
        code_16b, _ = run_cli(plan16b_path, wd16b)
        res_16b = json.load(open(os.path.join(wd16b, "results.json")))
        results["tests"]["r2f5_registry_recorded"] = {
            "noreg_exit": code_16a,
            "noreg_registry_enabled": res_16a.get("registry_enabled"),
            "noreg_registry_path": res_16a.get("registry_path"),
            "default_exit": code_16b,
            "default_registry_enabled":
                res_16b.get("registry_enabled"),
            "default_registry_path": res_16b.get("registry_path"),
            "pass": code_16a == 0
            and res_16a.get("registry_enabled") is False
            and res_16a.get("registry_path") is None
            and code_16b == 0
            and res_16b.get("registry_enabled") is True
            and str(res_16b.get("registry_path") or "").endswith(
                "run_registry.json")}

        # T17: round 2 finding 15, unit: substring messages refused.
        sub_plan = make_plan("bench-fixpass-r2f15",
                             "two_vision_fixture.html", {
                                 "clone1": "hello world",
                                 "clone2": "say hello world now"})
        try:
            bench.validate_plan(sub_plan)
            sub_raised = None
        except ValueError as exc:
            sub_raised = str(exc)
        results["tests"]["r2f15_substring_messages"] = {
            "raised": sub_raised,
            "pass": sub_raised is not None
            and "substring" in sub_raised}

        # T18: council 1 finding 2, CLI: a no-send run's
        # outcome_note names the failure, never claims skips.
        # Messages are the seeded bench-stale-001 texts, so the
        # stale bubbles match and the cross-window check sees
        # own_count 1 per thread (otherwise own_missing would
        # replace the note with the incomplete-check text).
        run_id18 = "bench-fixpass-r2f18"
        plan18 = make_plan(run_id18, "two_vision_fixture_nosend.html",
                           msgs1)
        plan18_path = os.path.join(args.workdir, "plan-r2f18.json")
        write_plan(plan18_path, plan18)
        wd18 = os.path.join(args.workdir, "r2f18")
        code_18, _ = run_cli(plan18_path, wd18)
        res_18 = json.load(open(os.path.join(wd18, "results.json")))
        note18 = res_18.get("outcome_note") or ""
        results["tests"]["r2f18_outcome_note"] = {
            "exit": code_18, "outcome": res_18.get("outcome"),
            "outcome_note": note18,
            "pass": code_18 == 1
            and res_18.get("outcome") == "FAIL"
            and "v12-timeout" in note18
            and "both steps skipped" not in note18}

        # T20: council 1 finding 10a, CLI: corrupt registry and
        # corrupt ledger files are REFUSED with exit 2.
        run_id20 = "bench-fixpass-r2f20"
        plan20 = make_plan(run_id20, "two_vision_fixture.html", {
            "clone1": "BENCH-TEST clone1 " + run_id20,
            "clone2": "BENCH-TEST clone2 " + run_id20})
        plan20_path = os.path.join(args.workdir, "plan-r2f20.json")
        write_plan(plan20_path, plan20)
        bad_reg = os.path.join(args.workdir, "registry-bad.json")
        with open(bad_reg, "w", encoding="utf-8") as f:
            f.write("{not json")
        wd20a = os.path.join(args.workdir, "r2f20a")
        code_20a, err_20a = run_cli(plan20_path, wd20a,
                                    ["--run-registry", bad_reg])
        wd20b = os.path.join(args.workdir, "r2f20b")
        os.makedirs(wd20b, exist_ok=True)
        with open(os.path.join(wd20b, "ledger.json"), "w",
                  encoding="utf-8") as f:
            f.write("{not json")
        code_20b, err_20b = run_cli(plan20_path, wd20b,
                                    ["--no-run-registry"])
        res_20b = None
        res_20b_path = os.path.join(wd20b, "results.json")
        if os.path.exists(res_20b_path):
            res_20b = json.load(open(res_20b_path))
        results["tests"]["r2f20_corrupt_files"] = {
            "bad_registry_exit": code_20a,
            "bad_registry_refused": "REFUSED" in err_20a,
            "bad_ledger_exit": code_20b,
            "bad_ledger_error": (res_20b or {}).get("error"),
            "pass": code_20a == 2 and "REFUSED" in err_20a
            and code_20b == 2
            and res_20b is not None
            and "corrupt ledger" in (res_20b.get("error") or "")}

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
