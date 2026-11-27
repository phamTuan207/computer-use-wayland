#!/usr/bin/env python3
"""Validate probes/ledger.jsonl: rows parse, carry the required
fields, and cited repo paths exist. Advisory only (no gate)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = Path(__file__).resolve().parent / "ledger.jsonl"
REQUIRED = ("date", "probe", "question", "result", "output", "verdict")


def main():
    bad = 0
    rows = 0
    for lineno, line in enumerate(LEDGER.read_text().splitlines(), 1):
        if not line.strip():
            continue
        rows += 1
        try:
            row = json.loads(line)
        except ValueError as exc:
            print("FAIL line %d: not JSON: %s" % (lineno, exc))
            bad += 1
            continue
        for field in REQUIRED:
            if not row.get(field):
                print("FAIL line %d: missing field %s" % (lineno, field))
                bad += 1
        for field in ("probe", "output"):
            value = row.get(field, "")
            if "/" in value and " " not in value and \
                    not (ROOT / value).exists():
                print("FAIL line %d: %s path not found: %s"
                      % (lineno, field, value))
                bad += 1
    if bad:
        print("LEDGER INVALID: %d problem(s) in %d rows" % (bad, rows))
        return 1
    print("LEDGER OK: %d rows" % rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
