#!/usr/bin/env python3
"""Blinded checker for one A1 pilot run directory.

Two stages, split so the verdict can never be influenced by the log.

Stage 1, blind verdict (default): reads ONLY end-state.json and
verify.png in the run directory. It reads no timed log, no transcript,
no timestamps, no run number, and no directory listing across runs.
It outputs ONLY PASS/FAIL plus the end-state values it checked.
Stage 1 runs once per run directory, and its verdict files are
committed before unblinding.

Stage 2, unblinded metrics (--metrics): reads run-log.jsonl and
computes the six metrics plus per-run fields. Run ONLY after ALL 12
Stage 1 verdicts are committed. Stage 2 is explicitly unblinded.

Usage:
  python3 check_run.py <run-dir>            # Stage 1, blind verdict
  python3 check_run.py --metrics <run-dir>  # Stage 2, metrics

Pass/fail rules (same for every run, arm-independent):
- Case pick4: end-state.json result_text must contain "pick4-ok".
- Case f01: end-state.json must have E5=1864000, E6=621333, E7=3,
  E2=540000, E3=574000, E4=750000 (numbers or numeric strings).
- verify.png must exist and be non-empty.
- The case is inferred from the end-state keys (result_text means
  pick4, E5/E6/E7 cells mean f01). A state matching neither case is
  a FAIL.

No em dash or en dash in this file.
"""

import json
import os
import sys
from datetime import datetime

CASE_A_EXPECTED_TEXT = "pick4-ok"
CASE_B_EXPECTED = {
    "E5": 1864000, "E6": 621333, "E7": 3,
    "E2": 540000, "E3": 574000, "E4": 750000,
}


def _parse_ts(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _as_number(value):
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        return float(value.replace(",", "").strip())
    raise ValueError("not a number: %r" % (value,))


def stage1_verdict(run_dir):
    """Blind verdict from end state and screenshot only. No log read."""
    problems = []
    verdict = {"run_dir": run_dir, "pass": False, "problems": problems}

    state_path = os.path.join(run_dir, "end-state.json")
    shot_path = os.path.join(run_dir, "verify.png")
    if not os.path.isfile(state_path):
        problems.append("missing end-state.json")
    if not os.path.isfile(shot_path):
        problems.append("missing verify.png")
    elif os.path.getsize(shot_path) == 0:
        problems.append("verify.png is empty")
    if problems:
        return verdict

    with open(state_path, "r", encoding="utf-8") as handle:
        try:
            state = json.load(handle)
        except json.JSONDecodeError:
            problems.append("end-state.json is not JSON")
            return verdict

    checked = {}
    if "result_text" in state and "E5" not in state:
        case_task = "pick4"
        text = state.get("result_text", "")
        checked["result_text"] = text
        if CASE_A_EXPECTED_TEXT not in str(text):
            problems.append(
                "pick4 result_text %r does not contain %r"
                % (text, CASE_A_EXPECTED_TEXT))
    elif "E5" in state:
        case_task = "f01"
        for cell, expected in sorted(CASE_B_EXPECTED.items()):
            if cell not in state:
                problems.append("f01 end state missing %s" % cell)
                continue
            try:
                got = _as_number(state[cell])
            except ValueError:
                problems.append("f01 %s is not a number: %r"
                                % (cell, state[cell]))
                continue
            checked[cell] = got
            if got != expected:
                problems.append("f01 %s is %s, expected %s"
                                % (cell, got, expected))
    else:
        problems.append(
            "end-state.json matches neither pick4 nor f01 shape")
        return verdict

    verdict["case_task"] = case_task
    verdict["checked"] = checked
    verdict["pass"] = not problems
    return verdict


def stage2_metrics(run_dir):
    """Unblinded metrics from the timed log. Run only after Stage 1
    verdicts for all runs are committed."""
    problems = []
    metrics = {"run_dir": run_dir, "problems": problems}
    log_path = os.path.join(run_dir, "run-log.jsonl")
    if not os.path.isfile(log_path):
        problems.append("missing run-log.jsonl")
        return metrics
    lines = []
    with open(log_path, "r", encoding="utf-8") as handle:
        for number, raw in enumerate(handle, start=1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                lines.append(json.loads(raw))
            except json.JSONDecodeError:
                problems.append("run-log.jsonl line %d is not JSON" % number)
    if problems:
        return metrics
    if not lines or lines[0].get("op") != "run_start":
        problems.append("log does not start with run_start")
    if not lines or lines[-1].get("op") != "run_end":
        problems.append("log does not end with run_end")
    if problems:
        return metrics

    start = _parse_ts(lines[0]["ts"])
    end = _parse_ts(lines[-1]["ts"])
    wall_ms = int((end - start).total_seconds() * 1000)
    tool_calls = sum(1 for line in lines if line.get("op") == "tool_call")
    tokens_in = None
    tokens_out = None
    for line in lines:
        if line.get("op") == "tokens":
            tokens_in = line.get("detail", {}).get("in")
            tokens_out = line.get("detail", {}).get("out")
    observe_ms = {}
    for line in lines:
        if line.get("op") == "observe":
            kind = line.get("detail", {}).get("kind", "unknown")
            observe_ms.setdefault(kind, []).append(
                line.get("elapsed_ms", 0))
    observation_cost = {
        kind: sum(values) / len(values)
        for kind, values in observe_ms.items()
    } if observe_ms else "UNMEASURED"
    desktop_observes = [
        line for line in lines
        if line.get("op") == "observe"
        and line.get("detail", {}).get("kind") == "desktop"]
    verify_ms = sum(
        line.get("elapsed_ms", 0) for line in lines
        if line.get("op") == "assert")
    if desktop_observes:
        verify_ms += desktop_observes[-1].get("elapsed_ms", 0)
    production_ms = sum(
        line.get("elapsed_ms", 0) for line in lines
        if line.get("op") in ("act", "observe"))
    vcr = (verify_ms / production_ms) if production_ms else "UNMEASURED"
    gaps = []
    for prev, cur in zip(lines, lines[1:]):
        gap = (_parse_ts(cur["ts"]) - _parse_ts(prev["ts"])).total_seconds()
        gaps.append(gap)
    stall_minutes = round(sum(g for g in gaps if g > 900) / 60, 3)
    program_calls = 0
    program_chars = 0
    for line in lines:
        if line.get("op") == "program_submit":
            program_calls = max(
                program_calls, line.get("detail", {}).get("calls_so_far", 0))
            program_chars += line.get("detail", {}).get("chars", 0)
    think_before_program = None
    for line in lines:
        if line.get("op") == "think_before_program":
            think_before_program = line.get("detail", {}).get("ms")
    run_sequence = lines[0].get("detail", {}).get("run_sequence")

    metrics.update({
        "wall_ms": wall_ms,
        "tool_calls": tool_calls,
        "tokens_in": tokens_in if tokens_in is not None else "UNMEASURED",
        "tokens_out": tokens_out if tokens_out is not None else "UNMEASURED",
        "observation_cost_ms_by_type": observation_cost,
        "vcr": vcr,
        "stall_minutes": stall_minutes,
        "recovery_steps": sum(
            1 for line in lines if line.get("op") == "recovery"),
        "refusals": sum(
            1 for line in lines if line.get("op") == "refusal"),
        "misclicks": sum(
            1 for line in lines if line.get("op") == "misclick"),
        "session_deaths": sum(
            1 for line in lines if line.get("op") == "session_death"),
        "retries": sum(
            1 for line in lines if line.get("op") == "retry"),
        "program_calls": program_calls,
        "program_chars": program_chars,
        "think_before_program_ms": (
            think_before_program
            if think_before_program is not None else "UNMEASURED"),
        "case_task": lines[0].get("detail", {}).get("case_task"),
        "run_id": lines[0].get("run_id"),
        "run_sequence": run_sequence,
    })
    return metrics


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("-")]
    stage2 = "--metrics" in argv[1:]
    if len(args) != 1:
        print("usage: check_run.py [--metrics] <run-dir>", file=sys.stderr)
        return 2
    if stage2:
        result = stage2_metrics(args[0])
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if not result.get("problems") else 1
    result = stage1_verdict(args[0])
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
