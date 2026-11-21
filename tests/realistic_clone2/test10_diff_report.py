#!/usr/bin/env python3
"""Test 10, data work: build an exact diff report between two catalogs.

Context: a product catalog exists in two versions. The task is to
compare them and write diff_report.json with an exact structure:
added ids, removed ids, price changes with old, new and delta
percent rounded to 2 decimals, and name changes. A summary count
block must match the lists. The checker recomputes the expected
report independently and deep compares.

Pass: diff_report.json deep equals the independently computed
expected report.
Fail: any list, value, rounding, or count differs.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import Case

V1 = [
    {"id": "a1", "name": "Cable", "price": 10.0},
    {"id": "a2", "name": "Mouse", "price": 25.0},
    {"id": "a3", "name": "Keyboard", "price": 49.0},
    {"id": "a4", "name": "Stand", "price": 20.0},
    {"id": "a5", "name": "Hub", "price": 39.0},
]
V2 = [
    {"id": "a1", "name": "Cable", "price": 12.5},
    {"id": "a2", "name": "Mouse Pro", "price": 25.0},
    {"id": "a3", "name": "Keyboard", "price": 44.1},
    {"id": "a5", "name": "Hub", "price": 39.0},
    {"id": "a6", "name": "Lamp", "price": 15.0},
]


def build_report(v1, v2):
    by1 = {p["id"]: p for p in v1}
    by2 = {p["id"]: p for p in v2}
    added = sorted(set(by2) - set(by1))
    removed = sorted(set(by1) - set(by2))
    price_changes, name_changes = [], []
    for pid in sorted(set(by1) & set(by2)):
        old, new = by1[pid], by2[pid]
        if old["price"] != new["price"]:
            price_changes.append({
                "id": pid, "old": old["price"], "new": new["price"],
                "delta_pct": round((new["price"] - old["price"])
                                   / old["price"] * 100, 2)})
        if old["name"] != new["name"]:
            name_changes.append({"id": pid, "old": old["name"],
                                 "new": new["name"]})
    return {"added": added, "removed": removed,
            "price_changes": price_changes, "name_changes": name_changes,
            "summary": {"added": len(added), "removed": len(removed),
                        "price_changes": len(price_changes),
                        "name_changes": len(name_changes)}}


def main():
    case = Case("test10", "build an exact diff report between catalogs",
                "data work")
    ws = case.ws
    with case.phase("setup_fixture"):
        (ws / "catalog_v1.json").write_text(json.dumps(V1, indent=2),
                                            encoding="utf-8")
        (ws / "catalog_v2.json").write_text(json.dumps(V2, indent=2),
                                            encoding="utf-8")

    with case.phase("build_report_from_files"):
        v1 = json.loads((ws / "catalog_v1.json").read_text())
        v2 = json.loads((ws / "catalog_v2.json").read_text())
        report = build_report(v1, v2)
        (ws / "diff_report.json").write_text(json.dumps(report, indent=2),
                                             encoding="utf-8")

    with case.phase("verify_against_independent_expectation"):
        expected = {
            "added": ["a6"],
            "removed": ["a4"],
            "price_changes": [
                {"id": "a1", "old": 10.0, "new": 12.5, "delta_pct": 25.0},
                {"id": "a3", "old": 49.0, "new": 44.1, "delta_pct": -10.0},
            ],
            "name_changes": [
                {"id": "a2", "old": "Mouse", "new": "Mouse Pro"},
            ],
            "summary": {"added": 1, "removed": 1, "price_changes": 2,
                        "name_changes": 1},
        }
        got = json.loads((ws / "diff_report.json").read_text())
        case.check("report_deep_equals_expected", got == expected,
                   f"got={json.dumps(got)[:240]}")

    return case.finish()


if __name__ == "__main__":
    sys.exit(main())
