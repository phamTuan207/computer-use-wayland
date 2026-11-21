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
Stage 2 reports metrics from whatever files exist: a run that FAILS
still gets its metrics reported (a missing file or a bad line is a
problem in the problems list, not a reason to drop the numbers).
A run counts as a pass only if Stage 1 says pass AND Stage 2 reports
no log-structure problem; the unblinding step enforces that join.

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

Metric names (frozen): observation_service_cost_ms_by_type,
vcr_service, silence_minutes, vcr_wall (UNMEASURED unless verify lines
are present), total_composition_think_ms, gap_ms (wall minus summed
service ms, the STEP total-think proxy), run_end_reason,
misclick_lines (count) and misclicks ("none detected" when the count
is 0, else the count). Recovery steps equal retry lines plus recovery
lines.

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
FROZEN_FIXTURE_MD5 = {
    "pick4": "91b2f92945c167306a13ae32977a9bf3",
    "f01": "2b6eda97036af51510b7eefe6d36dd93",
}
# Ops that carry no metric information and are excluded from the
# metric input chain (framing lines and unknown ops). Unknown ops are
# ignored for metrics and never counted as steps.
METRIC_EXCLUDED_OPS = {"program_submit", "think_before_program"}


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


def _read_log_lines(log_path, problems):
    """Parse run-log.jsonl. Malformed lines are problems, not crashes;
    parseable lines are kept so metrics are still computed."""
    lines = []
    with open(log_path, "r", encoding="utf-8") as handle:
        for number, raw in enumerate(handle, start=1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                lines.append(json.loads(raw))
            except json.JSONDecodeError:
                problems.append(
                    "run-log.jsonl line %d is not JSON" % number)
    return lines


def stage2_metrics(run_dir):
    """Unblinded metrics from the timed log. Run only after Stage 1
    verdicts for all runs are committed. Metrics are computed from
    whatever files exist; problems are listed, never a reason to
    drop the numbers."""
    problems = []
    metrics = {"run_dir": run_dir, "problems": problems}
    log_path = os.path.join(run_dir, "run-log.jsonl")
    if not os.path.isfile(log_path):
        problems.append("missing run-log.jsonl")
        return metrics
    lines = _read_log_lines(log_path, problems)
    if not lines:
        problems.append("run-log.jsonl has no parseable lines")
        return metrics
    if lines[0].get("op") != "run_start":
        problems.append("log does not start with run_start")
    if lines[-1].get("op") != "run_end":
        problems.append("log does not end with run_end")

    # ts must be non-decreasing down the file. A backward ts makes
    # wall unreliable, so wall is UNMEASURED instead of negative.
    ts_bad = None
    prev_ts = None
    for index, line in enumerate(lines):
        try:
            cur_ts = _parse_ts(line["ts"])
        except (KeyError, ValueError, TypeError):
            problems.append(
                "line %d has an unparseable ts" % (index + 1))
            ts_bad = index + 1
            break
        if prev_ts is not None and cur_ts < prev_ts:
            ts_bad = index + 1
            break
        prev_ts = cur_ts
    if ts_bad is not None:
        problems.append(
            "ts not non-decreasing at line %d" % ts_bad)

    start_lines = [l for l in lines if l.get("op") == "run_start"]
    end_lines = [l for l in lines if l.get("op") == "run_end"]
    if ts_bad is None and start_lines and end_lines:
        try:
            start = _parse_ts(start_lines[0]["ts"])
            end = _parse_ts(end_lines[-1]["ts"])
            wall_ms = int((end - start).total_seconds() * 1000)
        except (KeyError, ValueError, TypeError):
            wall_ms = "UNMEASURED"
    else:
        wall_ms = "UNMEASURED"

    # Metric input chain: framing lines and unknown ops are excluded,
    # so the two arms' logs differ in counts, not in kinds.
    known_ops = {
        "run_start", "run_end", "observe", "act", "think",
        "tokens", "verify_start", "verify_end", "assert",
        "refusal", "retry", "recovery", "misclick",
        "session_death", "tool_call",
    }
    metric_lines = [
        l for l in lines
        if l.get("op") in known_ops
    ]
    unknown_ops = sorted({
        str(l.get("op")) for l in lines
        if l.get("op") not in known_ops
        and l.get("op") not in METRIC_EXCLUDED_OPS
    })
    notes = []
    for op in unknown_ops:
        notes.append("unknown op %r ignored for metrics" % op)

    tool_calls = sum(
        1 for line in lines if line.get("op") == "tool_call")
    act_lines = [l for l in lines if l.get("op") == "act"]
    if act_lines and tool_calls == 0:
        problems.append(
            "tool_call lines missing: act lines present but zero "
            "tool_call lines")

    tokens_in = None
    tokens_out = None
    for line in lines:
        if line.get("op") == "tokens":
            tokens_in = line.get("detail", {}).get("in")
            tokens_out = line.get("detail", {}).get("out")

    # Observation service cost, split by (kind, image), with
    # gap-before ms (think plus idle before that observation).
    observe_groups = {}
    prev_metric_ts = None
    for line in metric_lines:
        try:
            cur_ts = _parse_ts(line["ts"])
        except (KeyError, ValueError, TypeError):
            continue
        if line.get("op") == "observe":
            kind = line.get("detail", {}).get("kind", "unknown")
            image = line.get("detail", {}).get("image", False)
            key = "%s:%s" % (kind, "image" if image else "noimage")
            group = observe_groups.setdefault(
                key, {"service": [], "gap_before": []})
            group["service"].append(line.get("elapsed_ms", 0))
            if prev_metric_ts is not None:
                gap_ms = int(
                    (cur_ts - prev_metric_ts).total_seconds() * 1000)
                gap_ms -= line.get("elapsed_ms", 0)
                group["gap_before"].append(max(gap_ms, 0))
        prev_metric_ts = cur_ts
    if observe_groups:
        observation_cost = {
            key: {
                "service_ms": round(
                    sum(v["service"]) / len(v["service"]), 3),
                "gap_before_ms": (
                    round(
                        sum(v["gap_before"]) / len(v["gap_before"]), 3)
                    if v["gap_before"] else "UNMEASURED"),
            }
            for key, v in sorted(observe_groups.items())
        }
    else:
        observation_cost = "UNMEASURED"

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
    vcr_service = (
        round(verify_ms / production_ms, 3)
        if production_ms else "UNMEASURED")

    verify_starts = [
        l for l in lines if l.get("op") == "verify_start"]
    verify_ends = [
        l for l in lines if l.get("op") == "verify_end"]
    if verify_starts and verify_ends and wall_ms != "UNMEASURED":
        try:
            v_start = _parse_ts(verify_starts[0]["ts"])
            v_end = _parse_ts(verify_ends[-1]["ts"])
            verify_wall_ms = int(
                (v_end - v_start).total_seconds() * 1000)
            prod_wall_ms = wall_ms - verify_wall_ms
            vcr_wall = (
                round(verify_wall_ms / prod_wall_ms, 3)
                if prod_wall_ms > 0 else "UNMEASURED")
        except (KeyError, ValueError, TypeError):
            vcr_wall = "UNMEASURED"
    else:
        vcr_wall = "UNMEASURED"

    gaps = []
    prev_ts = None
    for line in lines:
        try:
            cur_ts = _parse_ts(line["ts"])
        except (KeyError, ValueError, TypeError):
            continue
        if prev_ts is not None:
            gaps.append((cur_ts - prev_ts).total_seconds())
        prev_ts = cur_ts
    silence_minutes = round(sum(g for g in gaps if g > 900) / 60, 3)

    program_calls = 0
    program_chars = 0
    for line in lines:
        if line.get("op") == "program_submit":
            program_calls = max(
                program_calls, line.get("detail", {}).get("calls_so_far", 0))
            program_chars += line.get("detail", {}).get("chars", 0)
    think_per_call = [
        line.get("detail", {}).get("ms")
        for line in lines
        if line.get("op") == "think_before_program"
        and isinstance(line.get("detail", {}).get("ms"), (int, float))
    ]
    total_think = (
        sum(think_per_call) if think_per_call else "UNMEASURED")
    run_sequence = (
        start_lines[0].get("detail", {}).get("run_sequence")
        if start_lines else None)
    run_end_reason = (
        end_lines[-1].get("detail", {}).get("reason")
        if end_lines else None)
    # Gap ms: wall minus summed harness service time. The gap is think
    # plus idle. It is the STEP arm's total think proxy for GO
    # condition 4 (CODE total composition think vs STEP median gap).
    if wall_ms != "UNMEASURED":
        service_ms = sum(
            line.get("elapsed_ms", 0) for line in lines
            if isinstance(line.get("elapsed_ms"), (int, float)))
        gap_ms = wall_ms - service_ms
    else:
        gap_ms = "UNMEASURED"

    # commands.txt: program text must match the logged char counts.
    commands_path = os.path.join(run_dir, "commands.txt")
    if os.path.isfile(commands_path):
        submitted_texts = []
        with open(commands_path, "r", encoding="utf-8") as handle:
            for number, raw in enumerate(handle, start=1):
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    entry = json.loads(raw)
                except json.JSONDecodeError:
                    problems.append(
                        "commands.txt line %d is not JSON" % number)
                    continue
                if entry.get("kind") == "program_submit":
                    submitted_texts.append(entry.get("text", ""))
        logged_chars = [
            line.get("detail", {}).get("chars")
            for line in lines
            if line.get("op") == "program_submit"
        ]
        if len(submitted_texts) != len(logged_chars):
            problems.append(
                "commands.txt has %d program texts but the log has %d "
                "program_submit lines"
                % (len(submitted_texts), len(logged_chars)))
        else:
            for index, (text, chars) in enumerate(
                    zip(submitted_texts, logged_chars)):
                if len(text) != chars:
                    problems.append(
                        "program_submit %d chars mismatch: log says %s, "
                        "commands.txt text is %d chars"
                        % (index + 1, chars, len(text)))
    else:
        problems.append("missing commands.txt")

    # setup.json: fixture md5 must match the frozen values.
    setup_path = os.path.join(run_dir, "setup.json")
    fixture_md5 = None
    if os.path.isfile(setup_path):
        try:
            with open(setup_path, "r", encoding="utf-8") as handle:
                setup = json.load(handle)
            fixture_md5 = setup.get("fixture_md5", {})
            for name, expected in FROZEN_FIXTURE_MD5.items():
                got = fixture_md5.get(name)
                if got is not None and got != expected:
                    problems.append(
                        "fixture md5 mismatch for %s: got %s, frozen %s "
                        "(INVALID)" % (name, got, expected))
        except (json.JSONDecodeError, AttributeError):
            problems.append("setup.json is not JSON")
    else:
        problems.append("missing setup.json")

    misclick_lines = sum(
        1 for line in lines if line.get("op") == "misclick")
    metrics.update({
        "wall_ms": wall_ms,
        "tool_calls": tool_calls,
        "tokens_in": tokens_in if tokens_in is not None else "UNMEASURED",
        "tokens_out": tokens_out if tokens_out is not None else "UNMEASURED",
        "observation_service_cost_ms_by_type": observation_cost,
        "vcr_service": vcr_service,
        "vcr_wall": vcr_wall,
        "silence_minutes": silence_minutes,
        "recovery_steps": sum(
            1 for line in lines
            if line.get("op") in ("recovery", "retry")),
        "refusals": sum(
            1 for line in lines if line.get("op") == "refusal"),
        "misclick_lines": misclick_lines,
        "misclicks": (
            "none detected" if misclick_lines == 0 else misclick_lines),
        "session_deaths": sum(
            1 for line in lines if line.get("op") == "session_death"),
        "retries": sum(
            1 for line in lines if line.get("op") == "retry"),
        "program_calls": program_calls,
        "program_chars": program_chars,
        "think_per_call_ms": (
            think_per_call if think_per_call else "UNMEASURED"),
        "total_composition_think_ms": total_think,
        "gap_ms": gap_ms,
        "run_end_reason": run_end_reason,
        "case_task": (
            start_lines[0].get("detail", {}).get("case_task")
            if start_lines else None),
        "run_id": start_lines[0].get("run_id") if start_lines else None,
        "run_sequence": run_sequence,
        "fixture_md5": fixture_md5,
        "notes": notes,
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
