#!/usr/bin/env python3
"""Build the A1 checker self-test matrix T1-T16 (Council 3 section 6.3).

Each case is a synthetic run dir with hand-computed expected outputs
frozen alongside it. Expected values below are computed BY HAND from
the log lines defined here (see the arithmetic in comments); the runner
(run_matrix.py) compares the checker output against them exactly.
Synthetic dirs cover edge cases that cannot occur in a real run
(malformed JSON, missing files, out-of-order ts). The verdict-critical
cases (T1, T3 known-good; T2, T4 known-bad) are ALSO validated against
real runs via the Layer-2 preflight probe directories at resume
(Redteam C2).

Usage: python3 build_matrix.py   (writes cases/ and expected files)
No em dash or en dash in this file.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = os.path.join(HERE, "cases")

FROZEN_MD5 = {
    "pick4": "91b2f92945c167306a13ae32977a9bf3",
    "f01": "2b6eda97036af51510b7eefe6d36dd93",
}
# Minimal valid 1x1 PNG, non-empty is what the checker tests.
PNG_1X1 = bytes([
    0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
    0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
    0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
    0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
    0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,
    0x54, 0x08, 0xD7, 0x63, 0xF8, 0xCF, 0xC0, 0x00,
    0x00, 0x03, 0x01, 0x01, 0x00, 0x18, 0xDD, 0x8D,
    0xB4, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,
    0x44, 0xAE, 0x42, 0x60, 0x82,
])


def line(ts, step, op, elapsed, ok, progress, detail):
    return {
        "ts": ts, "run_id": "a1b2c3d4", "step_index": step,
        "op": op, "elapsed_ms": elapsed, "ok": ok,
        "progress_marker": progress, "detail": detail, "error": None,
    }


def write_case(name, log_lines, end_state, shot_bytes,
               program_texts, raw_log=None):
    """Write one case dir. log_lines is a list of dicts, or raw_log is
    the exact file text (for the malformed-JSON case)."""
    d = os.path.join(CASES, name)
    os.makedirs(d, exist_ok=True)
    if raw_log is not None:
        with open(os.path.join(d, "run-log.jsonl"), "w") as h:
            h.write(raw_log)
    elif log_lines is not None:
        with open(os.path.join(d, "run-log.jsonl"), "w") as h:
            for l in log_lines:
                h.write(json.dumps(l) + "\n")
    if end_state is not None:
        with open(os.path.join(d, "end-state.json"), "w") as h:
            json.dump(end_state, h, indent=2)
    if shot_bytes is not None:
        with open(os.path.join(d, "verify.png"), "wb") as h:
            h.write(shot_bytes)
    setup = {
        "repo_head": "freeze",
        "relay_head": "freeze",
        "cu_code_exec": "1",
        "cu_pick4_fastpath": "1",
        "broker_solo_proof": "solo",
        "fixture_md5": FROZEN_MD5,
        "checker_version": "freeze",
        "runbook_version": "freeze",
    }
    with open(os.path.join(d, "setup.json"), "w") as h:
        json.dump(setup, h, indent=2)
    with open(os.path.join(d, "commands.txt"), "w") as h:
        for text in program_texts:
            h.write(json.dumps({
                "ts": "2026-11-21T10:00:08.000Z",
                "kind": "program_submit",
                "chars": len(text),
                "text": text,
            }) + "\n")


def program_text(chars):
    base = "# case A program, composed live\nwins = windows()\n"
    assert chars >= len(base)
    return base + ("# pad\n" * ((chars - len(base)) // 6 + 1))[:chars - len(base)]


def expect(name, stage1, stage2, run_verdict):
    with open(os.path.join(CASES, name, "expected-stage1.json"), "w") as h:
        json.dump(stage1, h, indent=2, sort_keys=True)
    with open(os.path.join(CASES, name, "expected-stage2.json"), "w") as h:
        json.dump(stage2, h, indent=2, sort_keys=True)
    with open(os.path.join(CASES, name, "expected-join.json"), "w") as h:
        json.dump({"run_verdict": run_verdict}, h, indent=2, sort_keys=True)


def base_stage2(**over):
    """T1 Stage 2 metrics, hand-computed (see T1 comment)."""
    m = {
        "wall_ms": 11000,
        "tool_calls": 3,
        "tokens_in": "UNMEASURED",
        "tokens_out": "UNMEASURED",
        "observation_service_cost_ms_by_type": {
            "desktop:image": {"service_ms": 450.0, "gap_before_ms": 0.0},
        },
        "vcr_service": 0.25,
        "vcr_wall": 0.038,
        "silence_minutes": 0.0,
        "recovery_steps": 0,
        "refusals": 0,
        "misclick_lines": 0,
        "misclicks": "none detected",
        "session_deaths": 0,
        "retries": 0,
        "program_calls": 1,
        "program_chars": 900,
        "think_per_call_ms": [6000],
        "total_composition_think_ms": 6000,
        "gap_ms": 8400,
        "run_end_reason": "done",
        "case_task": "pick4",
        "run_id": "a1b2c3d4",
        "run_sequence": 1,
        "fixture_md5": FROZEN_MD5,
        "problems": [],
        "notes": [],
    }
    m.update(over)
    return m


# --- T1: known-good pick4 (CODE-shaped) ---
# Log, 14 lines. Wall: run_end 10:00:11.000 minus run_start 10:00:00.000
# = 11000 ms. tool_calls: 3 (steps 1, 3, 5). Observes: desktop/image
# 500 ms (gap: prev line 10:00:02.000, 500-500=0) and 400 ms (prev
# verify_start 10:00:08.500, 400-400=0); mean service 450.0.
# vcr_service: verify = assert 200 + last desktop observe 400 = 600;
# production = act 1200+300 + observe 500+400 = 2400; 600/2400 = 0.25.
# vcr_wall: verify phase 400 ms over prod wall 10600 ms = 0.038.
# Silence: no gap over 900 s, 0.0. Program: 1 call, 900 chars.
T1_LOG = [
    line("2026-11-21T10:00:00.000Z", 0, "run_start", 0, True, True,
         {"case_task": "pick4", "run_sequence": 1}),
    line("2026-11-21T10:00:02.000Z", 1, "tool_call", 0, True, False,
         {"tool": "windows"}),
    line("2026-11-21T10:00:02.500Z", 2, "observe", 500, True, True,
         {"kind": "desktop", "elements": 5, "image": True}),
    line("2026-11-21T10:00:04.000Z", 3, "tool_call", 0, True, False,
         {"tool": "act"}),
    line("2026-11-21T10:00:05.200Z", 4, "act", 1200, True, True,
         {"kind": "broker", "actions": 2, "completed": 2,
          "target_ref": None, "intended": "address bar"}),
    line("2026-11-21T10:00:07.000Z", 5, "tool_call", 0, True, False,
         {"tool": "code_exec"}),
    line("2026-11-21T10:00:08.000Z", 6, "program_submit", 0, True, True,
         {"chars": 900, "calls_so_far": 1, "planned": True}),
    line("2026-11-21T10:00:08.000Z", 7, "think_before_program", 0, True,
         False, {"ms": 6000, "call": 1}),
    line("2026-11-21T10:00:08.300Z", 8, "act", 300, True, True,
         {"kind": "dom", "actions": 1, "completed": 1,
          "target_ref": "e3", "intended": "Show result"}),
    line("2026-11-21T10:00:08.500Z", 9, "assert", 200, True, True,
         {"what": "#result", "expected": "pick4-ok",
          "got": "pick4-ok hello stranger"}),
    line("2026-11-21T10:00:08.500Z", 10, "verify_start", 0, True, False, {}),
    line("2026-11-21T10:00:08.900Z", 11, "observe", 400, True, True,
         {"kind": "desktop", "elements": 4, "image": True}),
    line("2026-11-21T10:00:08.900Z", 12, "verify_end", 0, True, False, {}),
    line("2026-11-21T10:00:11.000Z", 13, "run_end", 0, True, True,
         {"verdict": "done", "reason": "done"}),
]
T1_STATE = {"result_text": "pick4-ok hello stranger"}
write_case("T01", T1_LOG, T1_STATE, PNG_1X1, [program_text(900)])
expect("T01",
       {"pass": True, "problems": [], "case_task": "pick4",
        "checked": {"result_text": "pick4-ok hello stranger"}},
       base_stage2(), "PASS")

# --- T2: known-bad pick4 (same log, wrong end state) ---
T2_STATE = {"result_text": "not clicked yet"}
write_case("T02", T1_LOG, T2_STATE, PNG_1X1, [program_text(900)])
expect("T02",
       {"pass": False,
        "problems": ["pick4 result_text 'not clicked yet' does not "
                     "contain 'pick4-ok'"],
        "case_task": "pick4",
        "checked": {"result_text": "not clicked yet"}},
       base_stage2(), "FAIL")

# --- T3: known-good f01 (STEP-shaped) ---
# Wall: 10:01:00 minus 10:00:00 = 60000 ms. tool_calls 4.
# Observes: desktop/image 600 (gap 0) and 500 (gap 0), mean 550.0;
# dom/noimage 400 (gap 0). vcr_service: verify = assert 200 + last
# desktop 500 = 700; production = act 1500+800 + observe 600+400+500
# = 3800; 700/3800 = 0.184. vcr_wall: 500 over 59500 = 0.008.
# Silence 0.0. No program calls.
T3_LOG = [
    line("2026-11-21T10:00:00.000Z", 0, "run_start", 0, True, True,
         {"case_task": "f01", "run_sequence": 4}),
    line("2026-11-21T10:00:03.000Z", 1, "tool_call", 0, True, False,
         {"tool": "windows"}),
    line("2026-11-21T10:00:03.600Z", 2, "observe", 600, True, True,
         {"kind": "desktop", "elements": 5, "image": True}),
    line("2026-11-21T10:00:05.000Z", 3, "tool_call", 0, True, False,
         {"tool": "act"}),
    line("2026-11-21T10:00:06.500Z", 4, "act", 1500, True, True,
         {"kind": "broker", "actions": 2, "completed": 2,
          "target_ref": None, "intended": "address bar"}),
    line("2026-11-21T10:00:09.000Z", 5, "tool_call", 0, True, False,
         {"tool": "observe"}),
    line("2026-11-21T10:00:09.400Z", 6, "observe", 400, True, True,
         {"kind": "dom", "elements": 20, "image": False}),
    line("2026-11-21T10:00:12.000Z", 7, "tool_call", 0, True, False,
         {"tool": "act"}),
    line("2026-11-21T10:00:12.800Z", 8, "act", 800, True, True,
         {"kind": "dom", "actions": 4, "completed": 4,
          "target_ref": "e5", "intended": "A2"}),
    line("2026-11-21T10:00:13.000Z", 9, "assert", 200, True, True,
         {"what": "#e5", "expected": "1864000", "got": "1864000"}),
    line("2026-11-21T10:00:13.000Z", 10, "verify_start", 0, True, False, {}),
    line("2026-11-21T10:00:13.500Z", 11, "observe", 500, True, True,
         {"kind": "desktop", "elements": 4, "image": True}),
    line("2026-11-21T10:00:13.500Z", 12, "verify_end", 0, True, False, {}),
    line("2026-11-21T10:01:00.000Z", 13, "run_end", 0, True, True,
         {"verdict": "done", "reason": "done"}),
]
T3_STATE = {"C2": "12", "C3": "7", "C4": "5", "E2": 540000,
            "E3": 574000, "E4": 750000, "E5": 1864000,
            "E6": 621333, "E7": 3}
T3_STAGE2 = base_stage2(
    wall_ms=60000, tool_calls=4,
    observation_service_cost_ms_by_type={
        "desktop:image": {"service_ms": 550.0, "gap_before_ms": 0.0},
        "dom:noimage": {"service_ms": 400.0, "gap_before_ms": 0.0},
    },
    vcr_service=0.184, vcr_wall=0.008,
    program_calls=0, program_chars=0,
    think_per_call_ms="UNMEASURED",
    total_composition_think_ms="UNMEASURED",
    gap_ms=56000, run_end_reason="done",
    case_task="f01", run_sequence=4)
write_case("T03", T3_LOG, T3_STATE, PNG_1X1, [])
expect("T03",
       {"pass": True, "problems": [], "case_task": "f01",
        "checked": {"E2": 540000.0, "E3": 574000.0, "E4": 750000.0,
                    "E5": 1864000.0, "E6": 621333.0, "E7": 3.0}},
       T3_STAGE2, "PASS")

# --- T4: f01 with E7 wrong (same log, E7=2) ---
T4_STATE = dict(T3_STATE, E7=2)
write_case("T04", T3_LOG, T4_STATE, PNG_1X1, [])
expect("T04",
       {"pass": False,
        "problems": ["f01 E7 is 2, expected 3"],
        "case_task": "f01",
        "checked": {"E2": 540000.0, "E3": 574000.0, "E4": 750000.0,
                    "E5": 1864000.0, "E6": 621333.0, "E7": 2.0}},
       T3_STAGE2, "FAIL")

# --- T5: timeout run (wall at the 15 min Case A cap) ---
# Wall 900000 ms. tool_calls 1. vcr_service: verify = 0 assert + last
# desktop 500 = 500; production = observe 500; 1.0. vcr_wall UNMEASURED
# (no verify lines). Silence 0.0 (largest gap 897.5 s, under 900).
T5_LOG = [
    line("2026-11-21T10:00:00.000Z", 0, "run_start", 0, True, True,
         {"case_task": "pick4", "run_sequence": 2}),
    line("2026-11-21T10:00:02.000Z", 1, "tool_call", 0, True, False,
         {"tool": "windows"}),
    line("2026-11-21T10:00:02.500Z", 2, "observe", 500, True, True,
         {"kind": "desktop", "elements": 5, "image": True}),
    line("2026-11-21T10:15:00.000Z", 3, "run_end", 0, False, True,
         {"verdict": "failed", "reason": "timeout"}),
]
T5_STAGE2 = base_stage2(
    wall_ms=900000, tool_calls=1,
    observation_service_cost_ms_by_type={
        "desktop:image": {"service_ms": 500.0, "gap_before_ms": 0.0},
    },
    vcr_service=1.0, vcr_wall="UNMEASURED",
    program_calls=0, program_chars=0,
    think_per_call_ms="UNMEASURED",
    total_composition_think_ms="UNMEASURED",
    gap_ms=899500, run_end_reason="timeout",
    run_sequence=2)
write_case("T05", T5_LOG, T2_STATE, PNG_1X1, [])
expect("T05",
       {"pass": False,
        "problems": ["pick4 result_text 'not clicked yet' does not "
                     "contain 'pick4-ok'"],
        "case_task": "pick4",
        "checked": {"result_text": "not clicked yet"}},
       T5_STAGE2, "FAIL")

# --- T6: session death then FAIL ---
# Wall 9000 ms. tool_calls 2. Deaths 1. vcr_service: verify 500 over
# production 1500 = 0.333.
T6_LOG = [
    line("2026-11-21T10:00:00.000Z", 0, "run_start", 0, True, True,
         {"case_task": "pick4", "run_sequence": 3}),
    line("2026-11-21T10:00:02.000Z", 1, "tool_call", 0, True, False,
         {"tool": "windows"}),
    line("2026-11-21T10:00:02.500Z", 2, "observe", 500, True, True,
         {"kind": "desktop", "elements": 5, "image": True}),
    line("2026-11-21T10:00:05.000Z", 3, "session_death", 0, False, True,
         {"what": "broker", "error": "broker lost"}),
    line("2026-11-21T10:00:06.000Z", 4, "tool_call", 0, True, False,
         {"tool": "act"}),
    line("2026-11-21T10:00:07.000Z", 5, "act", 1000, True, True,
         {"kind": "broker", "actions": 1, "completed": 1,
          "target_ref": None, "intended": "address bar"}),
    line("2026-11-21T10:00:09.000Z", 6, "run_end", 0, False, True,
         {"verdict": "failed", "reason": "failed"}),
]
T6_STAGE2 = base_stage2(
    wall_ms=9000, tool_calls=2,
    observation_service_cost_ms_by_type={
        "desktop:image": {"service_ms": 500.0, "gap_before_ms": 0.0},
    },
    vcr_service=0.333, vcr_wall="UNMEASURED",
    program_calls=0, program_chars=0,
    think_per_call_ms="UNMEASURED",
    total_composition_think_ms="UNMEASURED",
    gap_ms=7500, run_end_reason="failed",
    session_deaths=1, run_sequence=3)
write_case("T06", T6_LOG, T2_STATE, PNG_1X1, [])
expect("T06",
       {"pass": False,
        "problems": ["pick4 result_text 'not clicked yet' does not "
                     "contain 'pick4-ok'"],
        "case_task": "pick4",
        "checked": {"result_text": "not clicked yet"}},
       T6_STAGE2, "FAIL")

# --- T7: missing run-log.jsonl (end state good) ---
# Stage 1 PASS (it never reads the log). Stage 2: metrics {} plus the
# missing-log problem. Join verdict FAIL.
d = os.path.join(CASES, "T07")
os.makedirs(d, exist_ok=True)
with open(os.path.join(d, "end-state.json"), "w") as h:
    json.dump(T1_STATE, h, indent=2)
with open(os.path.join(d, "verify.png"), "wb") as h:
    h.write(PNG_1X1)
with open(os.path.join(d, "setup.json"), "w") as h:
    json.dump({"fixture_md5": FROZEN_MD5}, h, indent=2)
with open(os.path.join(d, "commands.txt"), "w") as h:
    h.write("")
expect("T07",
       {"pass": True, "problems": [], "case_task": "pick4",
        "checked": {"result_text": "pick4-ok hello stranger"}},
       {"problems": ["missing run-log.jsonl"]}, "FAIL")

# --- T8: missing end-state.json with a complete log ---
# Stage 1 FAIL. Stage 2 metrics identical to T1.
write_case("T08", T1_LOG, None, PNG_1X1, [program_text(900)])
expect("T08",
       {"pass": False, "problems": ["missing end-state.json"]},
       base_stage2(), "FAIL")

# --- T9: empty verify.png ---
# Stage 1 FAIL (early return on the empty screenshot, so no case_task
# or checked values). Stage 2 metrics identical to T1.
write_case("T09", T1_LOG, T1_STATE, b"", [program_text(900)])
expect("T09",
       {"pass": False, "problems": ["verify.png is empty"]},
       base_stage2(), "FAIL")

# --- T10: malformed JSON line (line 5 is not JSON) ---
# Stage 1 PASS. Stage 2: problem naming line 5, metrics identical to
# T1 (the bad line carries no ts and no op, so nothing changes).
raw_lines = ["json.dumps placeholder"]
raw = ""
for i, l in enumerate(T1_LOG):
    if i == 4:
        raw += "THIS IS NOT JSON\n"
    raw += json.dumps(l) + "\n"
write_case("T10", None, T1_STATE, PNG_1X1, [program_text(900)],
           raw_log=raw)
expect("T10",
       {"pass": True, "problems": [], "case_task": "pick4",
        "checked": {"result_text": "pick4-ok hello stranger"}},
       base_stage2(
           problems=["run-log.jsonl line 5 is not JSON"]), "FAIL")

# --- T11: arm-leak test (T1 with and without program lines) ---
# T11a is T1 verbatim. T11b drops the program_submit and
# think_before_program lines and renumbers step_index. Stage 1 outputs
# must be identical; Stage 2 outputs must be identical except
# program_calls, program_chars, think_per_call_ms,
# total_composition_think_ms. The runner checks this directly (no
# frozen expected files for T11b beyond its own).
write_case("T11a", T1_LOG, T1_STATE, PNG_1X1, [program_text(900)])
expect("T11a",
       {"pass": True, "problems": [], "case_task": "pick4",
        "checked": {"result_text": "pick4-ok hello stranger"}},
       base_stage2(), "PASS")
T11B_LOG = []
step = 0
for l in T1_LOG:
    if l["op"] in ("program_submit", "think_before_program"):
        continue
    l2 = dict(l)
    l2["step_index"] = step
    step += 1
    T11B_LOG.append(l2)
write_case("T11b", T11B_LOG, T1_STATE, PNG_1X1, [])
expect("T11b",
       {"pass": True, "problems": [], "case_task": "pick4",
        "checked": {"result_text": "pick4-ok hello stranger"}},
       base_stage2(
           program_calls=0, program_chars=0,
           think_per_call_ms="UNMEASURED",
           total_composition_think_ms="UNMEASURED"), "PASS")

# --- T13: out-of-order ts (line 9 goes backward) ---
# L9 (act dom) ts moved from 10:00:08.300 to 10:00:06.000, before L8
# at 10:00:08.000. Problem at line 9. Wall UNMEASURED, vcr_wall
# UNMEASURED (it needs wall). Everything else identical to T1.
T13_LOG = []
for l in T1_LOG:
    l2 = dict(l)
    if l2["step_index"] == 8:
        l2["ts"] = "2026-11-21T10:00:06.000Z"
    T13_LOG.append(l2)
write_case("T13", T13_LOG, T1_STATE, PNG_1X1, [program_text(900)])
expect("T13",
       {"pass": True, "problems": [], "case_task": "pick4",
        "checked": {"result_text": "pick4-ok hello stranger"}},
       base_stage2(
           wall_ms="UNMEASURED", vcr_wall="UNMEASURED",
           gap_ms="UNMEASURED", run_end_reason="done",
           problems=["ts not non-decreasing at line 9"]), "FAIL")

# --- T14: zero observe lines ---
# Wall 4000 ms. tool_calls 1. Observation UNMEASURED. vcr_service:
# verify = assert 200 over production = act 1000, 0.2.
T14_LOG = [
    line("2026-11-21T10:00:00.000Z", 0, "run_start", 0, True, True,
         {"case_task": "pick4", "run_sequence": 5}),
    line("2026-11-21T10:00:02.000Z", 1, "tool_call", 0, True, False,
         {"tool": "act"}),
    line("2026-11-21T10:00:03.000Z", 2, "act", 1000, True, True,
         {"kind": "broker", "actions": 1, "completed": 1,
          "target_ref": None, "intended": "address bar"}),
    line("2026-11-21T10:00:03.500Z", 3, "assert", 200, True, True,
         {"what": "#result", "expected": "pick4-ok",
          "got": "pick4-ok hello stranger"}),
    line("2026-11-21T10:00:04.000Z", 4, "run_end", 0, True, True,
         {"verdict": "done", "reason": "done"}),
]
T14_STAGE2 = base_stage2(
    wall_ms=4000, tool_calls=1,
    observation_service_cost_ms_by_type="UNMEASURED",
    vcr_service=0.2, vcr_wall="UNMEASURED",
    program_calls=0, program_chars=0,
    think_per_call_ms="UNMEASURED",
    total_composition_think_ms="UNMEASURED",
    gap_ms=2800, run_end_reason="done",
    run_sequence=5)
write_case("T14", T14_LOG, T1_STATE, PNG_1X1, [])
expect("T14",
       {"pass": True, "problems": [], "case_task": "pick4",
        "checked": {"result_text": "pick4-ok hello stranger"}},
       T14_STAGE2, "PASS")

# --- T15: act lines with zero tool_call lines ---
# Same as T14 minus the tool_call line. Problem: tool_call lines
# missing. Everything else identical to T14 except tool_calls 0.
T15_LOG = [l for l in T14_LOG if l["op"] != "tool_call"]
for i, l in enumerate(T15_LOG):
    l["step_index"] = i
write_case("T15", T15_LOG, T1_STATE, PNG_1X1, [])
expect("T15",
       {"pass": True, "problems": [], "case_task": "pick4",
        "checked": {"result_text": "pick4-ok hello stranger"}},
       base_stage2(
           wall_ms=4000, tool_calls=0,
           observation_service_cost_ms_by_type="UNMEASURED",
           vcr_service=0.2, vcr_wall="UNMEASURED",
           program_calls=0, program_chars=0,
           think_per_call_ms="UNMEASURED",
           total_composition_think_ms="UNMEASURED",
           gap_ms=2800, run_end_reason="done",
           run_sequence=5,
           problems=["tool_call lines missing: act lines present but "
                     "zero tool_call lines"]), "FAIL")

# --- T16: unknown op value ---
# T1 log plus one "teleport" line after the assert (step 10, ts
# 10:00:08.500, equal to the assert ts so the ts order stays
# non-decreasing). Metrics identical to T1; notes carry the unknown-op
# entry; problems stay empty.
T16_LOG = []
step = 0
for l in T1_LOG:
    l2 = dict(l)
    l2["step_index"] = step
    step += 1
    T16_LOG.append(l2)
    if l["op"] == "assert":
        T16_LOG.append(line(
            "2026-11-21T10:00:08.500Z", step, "teleport", 0, True,
            False, {"where": "nowhere"}))
        step += 1
write_case("T16", T16_LOG, T1_STATE, PNG_1X1, [program_text(900)])
expect("T16",
       {"pass": True, "problems": [], "case_task": "pick4",
        "checked": {"result_text": "pick4-ok hello stranger"}},
       base_stage2(
           notes=["unknown op 'teleport' ignored for metrics"]), "PASS")

print("built %d cases under %s" % (len(os.listdir(CASES)), CASES))
