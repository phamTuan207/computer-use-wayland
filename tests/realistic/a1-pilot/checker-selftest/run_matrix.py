#!/usr/bin/env python3
"""Run the A1 checker self-test matrix T1-T16 (Council 3 section 6.3).

One command runs the whole matrix. Each case is compared against its
frozen expected output exactly, not approximately. The checker must
match every expected value.

Checks per case (except T11/T12, see below):
- Stage 1 output equals expected-stage1.json (ignoring run_dir).
- Stage 2 output equals expected-stage2.json (ignoring run_dir).
- Join verdict (Stage 1 pass AND Stage 2 with no problems) equals
  expected-join.json run_verdict.
T11: Stage 1 outputs of T11a and T11b identical; Stage 2 outputs
identical except program_calls, program_chars, think_per_call_ms,
total_composition_think_ms.
T12: the checker run twice on T01 gives byte-identical stdout, Stage 1
and Stage 2.
Also: check_run.py contains no reference to the manifest path.

Usage: python3 run_matrix.py
Exit 0 only if every case passes.
No em dash or en dash in this file.
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKER = os.path.join(HERE, "..", "check_run.py")
CASES = os.path.join(HERE, "cases")
ARM_REVEALING_STAGE2 = {
    "program_calls", "program_chars",
    "think_per_call_ms", "total_composition_think_ms",
}


def run_checker(case_dir, metrics=False):
    cmd = [sys.executable, CHECKER]
    if metrics:
        cmd.append("--metrics")
    cmd.append(case_dir)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return proc.returncode, json.loads(proc.stdout)
    except json.JSONDecodeError:
        return proc.returncode, {"_unparseable_stdout": proc.stdout,
                                 "_stderr": proc.stderr}


def load_expected(case_dir, name):
    with open(os.path.join(case_dir, name), "r") as h:
        return json.load(h)


def without_run_dir(d):
    d = dict(d)
    d.pop("run_dir", None)
    return d


def check_case(name):
    case_dir = os.path.join(CASES, name)
    failures = []
    _, s1 = run_checker(case_dir, metrics=False)
    _, s2 = run_checker(case_dir, metrics=True)
    e1 = load_expected(case_dir, "expected-stage1.json")
    e2 = load_expected(case_dir, "expected-stage2.json")
    ej = load_expected(case_dir, "expected-join.json")
    if without_run_dir(s1) != without_run_dir(e1):
        failures.append("stage1 mismatch: got %s, expected %s"
                        % (json.dumps(without_run_dir(s1), sort_keys=True),
                           json.dumps(without_run_dir(e1), sort_keys=True)))
    if without_run_dir(s2) != without_run_dir(e2):
        failures.append("stage2 mismatch: got %s, expected %s"
                        % (json.dumps(without_run_dir(s2), sort_keys=True),
                           json.dumps(without_run_dir(e2), sort_keys=True)))
    join = "PASS" if (s1.get("pass") and not s2.get("problems")) else "FAIL"
    if join != ej["run_verdict"]:
        failures.append("join verdict mismatch: got %s, expected %s"
                        % (join, ej["run_verdict"]))
    return failures


def main():
    failures = {}
    cases = sorted(
        d for d in os.listdir(CASES)
        if os.path.isdir(os.path.join(CASES, d)) and d.startswith("T"))
    for name in cases:
        if name in ("T11a", "T11b"):
            continue
        bad = check_case(name)
        if bad:
            failures[name] = bad

    # T11 arm-leak test.
    _, s1a = run_checker(os.path.join(CASES, "T11a"), metrics=False)
    _, s1b = run_checker(os.path.join(CASES, "T11b"), metrics=False)
    _, s2a = run_checker(os.path.join(CASES, "T11a"), metrics=True)
    _, s2b = run_checker(os.path.join(CASES, "T11b"), metrics=True)
    t11_bad = []
    if without_run_dir(s1a) != without_run_dir(s1b):
        t11_bad.append("stage1 differs between T11a and T11b")
    a2 = {k: v for k, v in without_run_dir(s2a).items()
          if k not in ARM_REVEALING_STAGE2}
    b2 = {k: v for k, v in without_run_dir(s2b).items()
          if k not in ARM_REVEALING_STAGE2}
    if a2 != b2:
        t11_bad.append("stage2 differs beyond arm-revealing fields: %s"
                       % json.dumps(
                           {k: (a2.get(k), b2.get(k)) for k in a2
                            if a2.get(k) != b2.get(k)}, sort_keys=True))
    if s2a.get("program_calls") == s2b.get("program_calls"):
        t11_bad.append("program_calls does not differ (leak test is void)")
    if t11_bad:
        failures["T11"] = t11_bad

    # T12 determinism: byte-identical stdout on repeat runs.
    t12_bad = []
    for metrics in (False, True):
        cmd = [sys.executable, CHECKER]
        if metrics:
            cmd.append("--metrics")
        cmd.append(os.path.join(CASES, "T01"))
        r1 = subprocess.run(cmd, capture_output=True, text=True)
        r2 = subprocess.run(cmd, capture_output=True, text=True)
        if r1.stdout != r2.stdout:
            t12_bad.append(
                "non-deterministic stdout (metrics=%s)" % metrics)
    if t12_bad:
        failures["T12"] = t12_bad

    # Checker must not reference the manifest path.
    with open(CHECKER, "r") as h:
        checker_src = h.read()
    if "manifest" in checker_src:
        failures["manifest-grep"] = [
            "check_run.py contains the string 'manifest'"]

    for name in sorted(failures):
        print("FAIL %s" % name)
        for f in failures[name]:
            print("  - %s" % f)
    # 15 regular cases + T11 (arm leak) + T12 (determinism) = 17 checks.
    total = 17
    passed = total - len(failures)
    print("matrix: %d/%d passed" % (passed, total))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
