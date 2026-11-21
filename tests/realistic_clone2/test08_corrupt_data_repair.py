#!/usr/bin/env python3
"""Test 08, error handling: repair a corrupt dataset with an audit.

Context: an orders CSV arrives with corrupt rows mixed into good
ones: a negative quantity, a date in the wrong format, a truncated
row with missing fields, a duplicate order id, and a non numeric
price. The task is to produce a clean CSV that satisfies the schema,
a rejects file that keeps every bad row with a reason, and counts
that add up. Nothing may be silently dropped.

Pass: clean CSV holds exactly the good rows in original order,
rejects hold exactly the bad rows each with a correct reason, and
good plus bad equals the input row count.
Fail: a good row lost, a bad row passed through, or a missing reason.
"""

import csv
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import Case

HEADER = ["order_id", "date", "item", "qty", "price"]
ROWS = [
    ["1001", "2026-11-01", "cable", "2", "9.50"],
    ["1002", "2026-11-02", "mouse", "-1", "25.00"],
    ["1003", "02/11/2026", "keyboard", "1", "49.00"],
    ["1004", "2026-11-03", "stand", "1", "19.99"],
    ["1005", "2026-11-04", "hub"],
    ["1004", "2026-11-05", "stand", "2", "19.99"],
    ["1006", "2026-11-06", "lamp", "1", "free"],
    ["1007", "2026-11-07", "desk", "1", "199.00"],
]
EXPECTED_GOOD = ["1001", "1004", "1007"]
EXPECTED_REJECTS = [
    ("1002", "negative qty"),
    ("1003", "bad date format"),
    ("1005", "wrong field count"),
    ("1004", "duplicate order_id"),
    ("1006", "non numeric price"),
]


def validate(row, seen_ids):
    if len(row) != 5:
        return "wrong field count"
    oid, date, _item, qty, price = row
    if oid in seen_ids:
        return "duplicate order_id"
    parts = date.split("-")
    if len(parts) != 3 or len(parts[0]) != 4:
        return "bad date format"
    if int(qty) < 0:
        return "negative qty"
    try:
        float(price)
    except ValueError:
        return "non numeric price"
    return None


def main():
    case = Case("test08", "repair a corrupt dataset with an audit",
                "error handling")
    ws = case.ws
    with case.phase("setup_fixture"):
        with open(ws / "orders.csv", "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(HEADER)
            writer.writerows(ROWS)

    with case.phase("repair_and_quarantine"):
        good, rejects = [], []
        seen_ids = set()
        with open(ws / "orders.csv", newline="", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            next(reader)
            for row in reader:
                reason = validate(row, seen_ids)
                if reason is None:
                    seen_ids.add(row[0])
                    good.append(row)
                else:
                    rejects.append((row, reason))
        with open(ws / "clean.csv", "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(HEADER)
            writer.writerows(good)
        with open(ws / "rejects.csv", "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(HEADER + ["reason"])
            for row, reason in rejects:
                padded = row + [""] * (5 - len(row))
                writer.writerow(padded + [reason])

    with case.phase("verify_against_ground_truth"):
        clean_rows = list(csv.reader(io.StringIO(
            (ws / "clean.csv").read_text(encoding="utf-8"))))[1:]
        clean_ids = [r[0] for r in clean_rows]
        case.check("clean_ids_exact", clean_ids == EXPECTED_GOOD,
                   f"clean={clean_ids}")
        reject_rows = list(csv.reader(io.StringIO(
            (ws / "rejects.csv").read_text(encoding="utf-8"))))[1:]
        got_rejects = [(r[0], r[-1]) for r in reject_rows]
        case.check("reject_reasons_exact", got_rejects == EXPECTED_REJECTS,
                   f"got={got_rejects}")
        case.check("nothing_silently_dropped",
                   len(clean_rows) + len(reject_rows) == len(ROWS),
                   f"{len(clean_rows)}+{len(reject_rows)} vs {len(ROWS)}")

    return case.finish()


if __name__ == "__main__":
    sys.exit(main())
