#!/usr/bin/env python3
"""Rung 3 ledger schema validation.

Validates rung3-run-log/R3-L1-grades.jsonl against
rung3-ci/ledger-schema.json using only the standard library.
Checks: one JSON object per line, required fields and types,
verdict enums, task ID shape, run code shape, scorer sessions
differ from the runner session, and grade consistency:
  - if scorer 1 and scorer 2 agree, final_grade equals that verdict;
  - if they disagree, scorer 3 must be present and final_grade
    equals the scorer 3 verdict;
  - an INVALID final grade needs both scorers INVALID (or a
    scorer 3 INVALID verdict on disagreement).
Rows with test_row=true skip the session and consistency checks
(they are schema-proof rows, never grades).

Usage:
  python3 rung3-ci/validate-ledger.py [LEDGER-FILE]
Exit 0 when every row is valid, else 1 with the bad rows listed.
No personal info in this file.
"""
import json
import os
import re
import sys

VERDICTS = ("PASS", "FAIL", "INVALID")
TASK_RE = re.compile(r"^(R3-[0-9]{3}|DP-0[1235]|R3-TEST)$")
RUN_RE = re.compile(r"^R3-L[0-9]+$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")


def check_str(row, field, errors):
    if not isinstance(row.get(field), str) or not row.get(field):
        errors.append("%s must be a non-empty string" % field)


def validate_row(row, lineno):
    errors = []
    if not isinstance(row, dict):
        return ["line %d: not a JSON object" % lineno]
    test_row = row.get("test_row", False)
    for field in ("task_id", "run_code", "runner_session", "scorer1",
                  "scorer2", "final_grade", "evidence_manifest_hash",
                  "timestamps", "invalid"):
        if field not in row:
            errors.append("missing %s" % field)
    if errors:
        return ["line %d: %s" % (lineno, "; ".join(errors))]
    if not TASK_RE.match(row["task_id"]):
        errors.append("bad task_id %s" % row["task_id"])
    if not RUN_RE.match(row["run_code"]):
        errors.append("bad run_code %s" % row["run_code"])
    check_str(row, "runner_session", errors)
    if row["final_grade"] not in ("PASS", "FAIL", "INVALID", "TEST"):
        errors.append("bad final_grade %s" % row["final_grade"])
    if test_row:
        if row["final_grade"] != "TEST":
            errors.append("test row must have final_grade TEST")
        if row["evidence_manifest_hash"] != "TEST":
            errors.append("test row must have evidence_manifest_hash TEST")
        return ["line %d: %s" % (lineno, "; ".join(errors))] if errors else []
    if not HEX64_RE.match(row["evidence_manifest_hash"] or ""):
        errors.append("evidence_manifest_hash must be a 64-char hex sha256")
    for who in ("scorer1", "scorer2"):
        sc = row[who]
        if not isinstance(sc, dict):
            errors.append("%s must be an object" % who)
            continue
        if sc.get("verdict") not in VERDICTS:
            errors.append("%s bad verdict %s" % (who, sc.get("verdict")))
        check_str(sc, "session", errors)
        if sc.get("session") == row["runner_session"]:
            errors.append("%s session equals runner session" % who)
    s1 = row["scorer1"]
    if isinstance(s1, dict):
        if not isinstance(s1.get("files_read"), list) or \
                not all(isinstance(x, str) for x in s1.get("files_read", [])):
            errors.append("scorer1 files_read must be a list of strings")
        if not HEX64_RE.match(s1.get("key_hash") or ""):
            errors.append("scorer1 key_hash must be a 64-char hex sha256")
    ts = row["timestamps"]
    if not isinstance(ts, dict):
        errors.append("timestamps must be an object")
    else:
        for field in ("task_start", "task_end", "scored1_at",
                      "scored2_at", "recorded_at"):
            if not isinstance(ts.get(field), str) or not ts.get(field):
                errors.append("timestamps.%s must be a non-empty string"
                              % field)
    inv = row["invalid"]
    if not isinstance(inv, dict) or "is_invalid" not in inv or \
            "reason" not in inv or "backup_task" not in inv:
        errors.append("invalid must have is_invalid, reason, backup_task")
    elif not isinstance(inv["is_invalid"], bool):
        errors.append("invalid.is_invalid must be boolean")
    # Grade consistency.
    v1 = row["scorer1"].get("verdict") if isinstance(row["scorer1"], dict) else None
    v2 = row["scorer2"].get("verdict") if isinstance(row["scorer2"], dict) else None
    if v1 and v2:
        if v1 == v2:
            if row["final_grade"] != v1:
                errors.append("final_grade %s != agreed verdict %s"
                              % (row["final_grade"], v1))
        else:
            s3 = row.get("scorer3")
            if not isinstance(s3, dict) or s3.get("verdict") not in VERDICTS:
                errors.append("scorers disagree; scorer3 verdict required")
            elif row["final_grade"] != s3["verdict"]:
                errors.append("final_grade %s != scorer3 verdict %s"
                              % (row["final_grade"], s3["verdict"]))
            elif s3.get("session") == row["runner_session"]:
                errors.append("scorer3 session equals runner session")
    if row["final_grade"] == "INVALID" and not (
            row.get("invalid") or {}).get("is_invalid"):
        errors.append("final_grade INVALID needs invalid.is_invalid true")
    return ["line %d: %s" % (lineno, "; ".join(errors))] if errors else []


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        root, "rung3-run-log", "R3-L1-grades.jsonl")
    if not os.path.isfile(path):
        print("FAIL: ledger file missing: %s" % path)
        return 1
    rows, errors = [], []
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append("line %d: invalid JSON: %s" % (lineno, e))
                continue
            rows.append(row)
            errors.extend(validate_row(row, lineno))
    seen = [r.get("task_id") for r in rows if isinstance(r, dict)]
    dupes = sorted(set(t for t in seen if seen.count(t) > 1
                       and t != "R3-TEST"))
    if dupes:
        errors.append("duplicate task rows (append-only, one row per task): %s"
                      % dupes)
    if errors:
        for e in errors:
            print("FAIL: %s" % e)
        print("RESULT: %d row(s), %d error(s)" % (len(rows), len(errors)))
        return 1
    print("PASS: ledger valid: %d row(s), 0 errors" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
