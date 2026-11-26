#!/usr/bin/env python3
"""One small test for clean-validate-ledger.py (R19).

Cases:
  1. Closed R3-L3 inputs: validate-ledger exits 0. ledger-cross-check
     exits 1 with exactly one error, naming R3-056: task 56 was added
     mid-run by owner amendment and has no run position in
     thu-tu-chay.txt (structural gap, not a data-integrity failure).
     This pins the honest final state; any NEW cross-check error
     fails this test. Skipped (with a printed note) when the VM-local
     verdict dir is absent.
  2. One mutated copied row (final_grade flipped against agreeing
     scorers): validate-ledger exits nonzero.
  3. Between-writes copy case: last ledger line truncated mid-JSON
     (a copy taken during an append): validate-ledger exits nonzero.
     A partial append fails loud, never silently passes; the snapshot
     discipline (verdict dir first, ledger last) keeps the window
     minimal.

Run from outside the flagged tree, e.g.:
  cp rung3-ci/clean-validate-ledger.py rung3-ci/test-clean-validate.py /tmp/
  python3 /tmp/test-clean-validate.py
Repo root resolution: $CLEAN_VALIDATE_REPO_ROOT, else the checkout
holding this file, else ~/workspace/r3l3-run-wt.
No personal info in this file.
"""
import importlib.util
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def load_module():
    spec = importlib.util.spec_from_file_location(
        "clean_validate_ledger",
        os.path.join(HERE, "clean-validate-ledger.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def find_repo_root():
    env = os.environ.get("CLEAN_VALIDATE_REPO_ROOT")
    if env:
        return os.path.expanduser(env)
    grand = os.path.dirname(HERE)
    if os.path.isfile(os.path.join(
            grand, "rung3-run-log", "R3-L3-grades.jsonl")):
        return grand
    return os.path.expanduser("~/workspace/r3l3-run-wt")


def main():
    mod = load_module()
    repo_root = find_repo_root()
    ledger = os.path.join(repo_root, "rung3-run-log", "R3-L3-grades.jsonl")
    verdict_dir = os.path.expanduser("~/workspace/rung3-verdicts")
    failures = []

    # Case 1: closed R3-L3 inputs.
    r = mod.run_clean_validation(repo_root)
    print("case1: validate_rc=%d cross_rc=%d rows=%d head=%s"
          % (r["validate_rc"], r["cross_rc"], r["rows"], r["head_sha"]))
    if r["validate_rc"] != 0:
        failures.append("case1: validate-ledger should exit 0 on the "
                        "closed ledger, got %d" % r["validate_rc"])
    if os.path.isdir(verdict_dir):
        err_lines = [ln for ln in r["cross_out"].splitlines()
                     if ln.strip().startswith("- ")]
        if r["cross_rc"] != 1 or len(err_lines) != 1 \
                or "R3-056" not in err_lines[0]:
            failures.append(
                "case1: cross-check should exit 1 with exactly the "
                "R3-056 structural error, got rc=%d errors=%r"
                % (r["cross_rc"], err_lines))
    else:
        print("case1: verdict dir absent, cross-check assertions skipped")

    with open(ledger, encoding="utf-8") as f:
        lines = [ln for ln in f.read().splitlines() if ln.strip()]

    # Case 2: one mutated copied row.
    mutated = []
    flipped = False
    for ln in lines:
        row = json.loads(ln)
        if not flipped and row.get("test_row") is not True \
                and row.get("final_grade") == "PASS" \
                and (row.get("scorer1") or {}).get("verdict") == "PASS" \
                and (row.get("scorer2") or {}).get("verdict") == "PASS":
            row["final_grade"] = "FAIL"
            flipped = True
        mutated.append(json.dumps(row))
    assert flipped, "no PASS row found to mutate"
    with tempfile.NamedTemporaryFile(
            "w", suffix=".jsonl", delete=False) as tf:
        tf.write("\n".join(mutated) + "\n")
        mut_path = tf.name
    r2 = mod.run_clean_validation(repo_root, ledger=mut_path)
    print("case2: validate_rc=%d (mutated row)" % r2["validate_rc"])
    if r2["validate_rc"] == 0:
        failures.append("case2: mutated row must fail validation")
    os.unlink(mut_path)

    # Case 3: between-writes copy (last line truncated mid-JSON).
    truncated = lines[:-1] + [lines[-1][: len(lines[-1]) // 2]]
    with tempfile.NamedTemporaryFile(
            "w", suffix=".jsonl", delete=False) as tf:
        tf.write("\n".join(truncated) + "\n")
        trunc_path = tf.name
    r3 = mod.run_clean_validation(repo_root, ledger=trunc_path)
    print("case3: validate_rc=%d (truncated last line)" % r3["validate_rc"])
    if r3["validate_rc"] == 0:
        failures.append("case3: truncated last line must fail validation")
    os.unlink(trunc_path)

    if failures:
        for msg in failures:
            print("FAIL: %s" % msg)
        print("RESULT: %d failure(s)" % len(failures))
        return 1
    print("PASS: all clean-validate cases pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
