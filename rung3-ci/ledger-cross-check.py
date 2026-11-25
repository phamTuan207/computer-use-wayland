#!/usr/bin/env python3
"""R3-L3 ledger cross-check (gate G-49).

Diffs each ledger row against its verdict files (task ID, verdict, pair)
before each push, or the rows are generated from the verdict files instead
of typed. Test rows (test_row=true) are schema-proof rows, never grades,
and are skipped.

Verdict files live in ~/workspace/rung3-verdicts/ as R3-xxx-A1.json,
R3-xxx-A2.json, R3-xxx-B1.json, R3-xxx-B2.json, R3-xxx-TB.json
(VM-local, never committed). Each verdict file carries at least a task id,
a verdict (PASS/FAIL/INVALID), and the scorer/pair it belongs to.

Usage:
  python3 rung3-ci/ledger-cross-check.py [LEDGER-FILE] [VERDICT-DIR]
Defaults: rung3-run-log/R3-L3-grades.jsonl, ~/workspace/rung3-verdicts.
Exit 0 when every non-test row cross-checks clean (or all rows are test
rows), else 1 with the mismatches listed.
No personal info in this file.
"""
import json
import os
import sys

LEDGER_DEFAULT = "rung3-run-log/R3-L3-grades.jsonl"
VERDICT_DIR_DEFAULT = os.path.expanduser("~/workspace/rung3-verdicts")

# Ledger row fields (see rung3-ci/ledger-schema.json).
# scorer1/scorer2 carry verdicts; a tiebreaker verdict lives in scorer3
# when present. The pair is derived from the task's lane: positions 1-28
# are Pair A, positions 29-55 are Pair B (see thu-tu-chay.txt).
PAIR_A_POSITIONS = range(1, 29)
PAIR_B_POSITIONS = range(29, 56)


ORDER_FILE_DEFAULT = "rung3-run-log/thu-tu-chay.txt"

# Backup tasks used mid-run are NOT in the fixed order line; they inherit
# the position of the task they replaced (F-18). Record each mid-run
# replacement here when it happens (position = the replaced task's
# position). DP-03 is already in the order line (pre-run replacement for
# the dropped R3-047 at position 34), so it needs no entry here.
# DP-06 replaced R3-011 (INVALID, Cloudflare block on timeanddate.com)
# at position 11 on 2026-11-25 (coordinator epoch 8).
DP_REPLACEMENT_POSITION = {"DP-06": 11, "DP-02": 20, "DP-07": 21}


def load_order(order_path):
    """Return {task_id: position} from the fixed run-order line."""
    import re
    order = {}
    try:
        with open(order_path, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return order
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        tokens = line.split()
        if len(tokens) >= 10 and all(re.match(r"^(R3-\d{3}|DP-\d{2})$", t) for t in tokens):
            for i, t in enumerate(tokens, 1):
                order[t] = i
            return order
    return order


def task_position(task_id, order=None):
    """Return the run position (1-55) for a task id, or None.

    The position comes from the fixed run-order line in thu-tu-chay.txt,
    NOT from the task number: R3-029 is position 25 (Pair A), not 29.
    A DP task inherits the replaced task's position (F-18): DP-03 is
    position 34. Mid-run backups not in the order line use
    DP_REPLACEMENT_POSITION above.
    """
    if order is None:
        order = {}
    if task_id in order:
        return order[task_id]
    if task_id in DP_REPLACEMENT_POSITION:
        return DP_REPLACEMENT_POSITION[task_id]
    return None


def pair_for_position(pos):
    if pos in PAIR_A_POSITIONS:
        return "A"
    if pos in PAIR_B_POSITIONS:
        return "B"
    return None


def verdict_files_for(task_id, verdict_dir):
    """Return {suffix: path} for the verdict files that exist for a task."""
    found = {}
    for suffix in ("A1", "A2", "B1", "B2", "TB"):
        path = os.path.join(verdict_dir, "%s-%s.json" % (task_id, suffix))
        if os.path.exists(path):
            found[suffix] = path
    return found


def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    ledger_path = sys.argv[1] if len(sys.argv) > 1 else LEDGER_DEFAULT
    verdict_dir = sys.argv[2] if len(sys.argv) > 2 else VERDICT_DIR_DEFAULT
    order_path = sys.argv[3] if len(sys.argv) > 3 else ORDER_FILE_DEFAULT
    order = load_order(order_path)
    errors = []
    checked = 0
    skipped = 0
    if not os.path.exists(ledger_path):
        print("FAIL: ledger file not found: %s" % ledger_path)
        return 1
    with open(ledger_path, "r", encoding="utf-8") as f:
        lines = [ln for ln in f.read().splitlines() if ln.strip()]
    if not lines:
        print("OK: ledger empty, nothing to cross-check")
        return 0
    for i, line in enumerate(lines, 1):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as e:
            errors.append("line %d: not valid JSON: %s" % (i, e))
            continue
        if row.get("test_row") is True:
            skipped += 1
            continue
        task_id = row.get("task_id")
        if not task_id:
            errors.append("line %d: missing task_id" % i)
            continue
        final_grade = row.get("final_grade")
        pos = task_position(task_id, order)
        if pos is None:
            errors.append("%s: no run position found in %s (not in the order line and not in DP_REPLACEMENT_POSITION)" % (task_id, order_path))
            continue
        expected_pair = pair_for_position(pos)
        if expected_pair is None:
            errors.append("%s: position %s is outside 1-55" % (task_id, pos))
            continue
        files = verdict_files_for(task_id, verdict_dir)
        if not files:
            errors.append("%s: no verdict files found in %s" % (task_id, verdict_dir))
            continue
        for suffix, path in sorted(files.items()):
            try:
                v = read_json(path)
            except (json.JSONDecodeError, OSError) as e:
                errors.append("%s: verdict file %s unreadable: %s" % (task_id, path, e))
                continue
            v_task = v.get("task_id") or v.get("task") or v.get("id")
            if v_task and v_task != task_id:
                errors.append("%s: verdict file %s names task %s" % (task_id, path, v_task))
            v_verdict = v.get("verdict") or v.get("grade") or v.get("final_grade")
            if v_verdict and final_grade and v_verdict != final_grade:
                # A tiebreaker file may legitimately differ from a single
                # scorer; only the final grade must match the verdict the
                # ledger records as deciding. The TB file is the deciding
                # verdict when present, so a TB mismatch is an error, while
                # a single-scorer mismatch against the final grade is
                # expected on disagreement and is not an error by itself.
                if suffix == "TB":
                    errors.append("%s: tiebreaker verdict %s != ledger final %s" % (task_id, v_verdict, final_grade))
            # Pair check (was dead code before the final review 25/11):
            # the verdict file's pair must match the pair implied by the
            # task's run position (1-28 Pair A, 29-55 Pair B). The pair
            # comes from the verdict file's "pair" field when present, and
            # from its suffix (A1/A2 are Pair A, B1/B2 are Pair B) when
            # present. A TB file has no suffix pair; only its "pair" field
            # is checked.
            v_pair = v.get("pair")
            if v_pair and v_pair != expected_pair:
                errors.append("%s: verdict file %s pair %s != expected pair %s (position %s)" % (task_id, path, v_pair, expected_pair, pos))
            suffix_pair = {"A1": "A", "A2": "A", "B1": "B", "B2": "B"}.get(suffix)
            if suffix_pair and suffix_pair != expected_pair:
                errors.append("%s: verdict file %s suffix %s is Pair %s but position %s is Pair %s" % (task_id, path, suffix, suffix_pair, pos, expected_pair))
            checked += 1
    if errors:
        print("FAIL: %d cross-check error(s):" % len(errors))
        for e in errors:
            print("  - %s" % e)
        return 1
    print("OK: %d verdict file(s) cross-checked, %d test row(s) skipped, 0 errors" % (checked, skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())
