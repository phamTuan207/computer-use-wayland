#!/usr/bin/env python3
"""Rung 3 list verify script (55-task safe-only list).

Checks docs/rung3-list-100-tasks.md on branch todolist-push:
  1. 55 tasks, IDs R3-001 to R3-100 minus the 45 removed, no gaps, no duplicates.
  2. Every task has Pass, Fail, and held-out evidence lines.
  3. Counts match section 7: 35 browser, 20 desktop, 37 trung binh,
     11 kho, 7 rat kho.
  4. Backups DP-01, DP-02, DP-03, DP-05 present, DP-04 absent as a task.
  5. Answer keys present in section 8 for the tasks named in the
     grading decision section 2.
  6. Section 1 pass table: 55 valid needs 53 pass; invalid caps
     5 total, 2 per difficulty group.
  7. Section 9 removal log lists exactly the 45 removed IDs.
  8. List file sha256 matches rung3-ci/frozen-heads.txt (freeze check).

Exit 0 only if zero FAIL checks. PENDING items are synthesis-owned
keys not yet frozen (DP-02 keywords, DP-03 exact N, R3-003/R3-004
full keys, R3-007 input values, Tier C rubrics for R3-067/R3-083);
they are listed, not hidden, and do not block exit 0. Once the
frozen key file exists, check-key-hash.py and the Tier A checkers
cover those values.

Usage:
  python3 rung3-ci/verify-list.py [--list PATH] [--frozen PATH]
No personal info in this file.
"""
import argparse
import hashlib
import os
import re
import sys

EXPECTED_TOTAL = 55
EXPECTED_BROWSER = 35
EXPECTED_DESKTOP = 20
EXPECTED_TRUNG_BINH = 37
EXPECTED_KHO = 11
EXPECTED_RAT_KHO = 7

REMOVED_OFFICE = [
    "R3-058", "R3-059", "R3-060", "R3-061", "R3-062", "R3-063",
    "R3-064", "R3-065", "R3-066", "R3-068", "R3-069", "R3-070",
    "R3-071", "R3-084", "R3-087", "R3-090", "R3-091", "R3-097",
]
REMOVED_DANGEROUS = [
    "R3-012", "R3-015", "R3-020", "R3-023", "R3-030", "R3-031",
    "R3-032", "R3-033", "R3-034", "R3-038", "R3-039", "R3-043",
    "R3-044", "R3-048", "R3-050", "R3-051", "R3-052", "R3-053",
    "R3-054", "R3-056", "R3-057", "R3-073", "R3-077", "R3-080",
    "R3-081", "R3-092", "R3-095",
]
REMOVED = sorted(set(REMOVED_OFFICE + REMOVED_DANGEROUS))
EXPECTED_IDS = sorted(
    "R3-%03d" % n for n in range(1, 101) if ("R3-%03d" % n) not in REMOVED
)

# (label, section, distinctive substring that proves the key is present)
KEY_CHECKS = [
    ("R3-002 JSON errors", 8, "dau phay thua truoc dau ngoac dong"),
    ("R3-002 JSON errors (jsonlint)", 8, "jsonlint.com"),
    ("R3-013 sample text", 8, "lan@example.com"),
    ("R3-013 pattern counts", 8, "1.250.000"),
    ("R3-021 query order", 8, "Giuong 600, Tu 400, Ghe 250, Ban 150"),
    ("R3-021 total", 8, "tong gia tri buoc 5: 6750"),
    ("R3-072 fixture sizes", 8, "d72-anh-1.png 800x600"),
    ("R3-082 calculations", 8, "(12 + 8) * 3 - 5 = 55"),
    ("R3-082 calculations (5th)", 8, "(9 + 6) * 4 / 2 = 30"),
    ("R3-014 RGB values", 6, "#FF0000 la RGB(255, 0, 0)"),
    ("R3-009 URLs", 8, "https://www.bbc.com/"),
    ("R3-009 URLs (2nd)", 8, "https://en.wikipedia.org/wiki/Main_Page"),
    ("R3-019 flight dates rule", 8, "ngay chay cong 30 ngay"),
    ("DP-05 tables", 8, "SP01 Ban 150"),
    ("DP-05 JOIN results", 8, "DH01 Ban 10"),
    ("DP-02 fixture rule", 8, "12 file van ban trong ~/rung3/dp02-code"),
]

# Synthesis-owned values not yet frozen in the list. Listed as PENDING.
PENDING_KEYS = [
    "DP-02 keywords: 5 keywords are allocated by the synthesis step "
    "into section 8 before the freeze; only the fixture rule is in the list now.",
    "DP-03 exact port count N: the rule (minimum 3, 5 rows when 5 named "
    "ports exist) is in section 8; the exact N is fixed pre-run by synthesis.",
    "R3-003 full key: the event and per-article values are chosen by "
    "synthesis before the freeze; section 8 only names the key to be fixed.",
    "R3-004 full key: the tool document and its 5 steps are chosen by "
    "synthesis before the freeze; section 8 only names the key to be fixed.",
    "R3-007 input values: the 5 conversion inputs are allocated by "
    "synthesis; the checker computes expected outputs with 0.01 tolerance.",
    "Tier C rubrics R3-067/R3-083: required shapes, counts, colors and "
    "text must be written and frozen in the key file before task 1.",
    "R3-085 reference frame: path ~/rung3/r3-085-khung-tham-chieu.png is "
    "named in section 8; the file itself is produced by synthesis.",
]


def section(text, num):
    """Return the text of '## <num>.' section, or '' if missing."""
    parts = re.split(r"\n## %d\." % num, text)
    if len(parts) < 2:
        return ""
    rest = parts[1]
    nxt = re.search(r"\n## \d+\.", rest)
    return rest[: nxt.start()] if nxt else rest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", default=None)
    ap.add_argument("--frozen", default=None)
    args = ap.parse_args()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    list_path = args.list or os.path.join(root, "docs", "rung3-list-100-tasks.md")
    frozen_path = args.frozen or os.path.join(root, "rung3-ci", "frozen-heads.txt")

    fails, passes, pendings = [], [], []

    def check(name, ok, detail=""):
        (passes if ok else fails).append(name + (" | " + detail if detail else ""))

    if not os.path.isfile(list_path):
        print("FAIL: list file missing: %s" % list_path)
        return 1
    text = open(list_path, encoding="utf-8").read()

    check("title states 55 tasks",
          text.startswith("# Danh sach 55 task rung 3"))

    sec6 = section(text, 6)
    sec7 = section(text, 7)
    sec8 = section(text, 8)
    sec9 = section(text, 9)
    sec1 = section(text, 1)
    check("section 6 present", bool(sec6))
    check("section 7 present", bool(sec7))
    check("section 8 present", bool(sec8))
    check("section 9 present", bool(sec9))
    check("section 1 present", bool(sec1))

    heads = re.findall(
        r"^### (R3-\d+), .*nhom: (.+?), do kho: (.+?)\)",
        sec6, re.M)
    ids = [h[0] for h in heads]
    check("55 task headers in section 6", len(ids) == EXPECTED_TOTAL,
          "found %d" % len(ids))
    check("no duplicate task IDs", len(ids) == len(set(ids)),
          "duplicates: %s" % sorted(set(i for i in ids if ids.count(i) > 1)))
    check("IDs match expected set (R3-001..R3-100 minus 45 removed)",
          sorted(ids) == EXPECTED_IDS,
          "missing: %s; extra: %s" % (
              sorted(set(EXPECTED_IDS) - set(ids)),
              sorted(set(ids) - set(EXPECTED_IDS))))
    check("no removed ID appears as a task",
          not (set(ids) & set(REMOVED)),
          "found removed: %s" % sorted(set(ids) & set(REMOVED)))

    groups = {}
    diffs = {}
    for _tid, group, diff in heads:
        groups[group] = groups.get(group, 0) + 1
        diffs[diff] = diffs.get(diff, 0) + 1
    check("browser count 35", groups.get("trinh duyet", 0) == EXPECTED_BROWSER,
          "found %d" % groups.get("trinh duyet", 0))
    check("desktop count 20", groups.get("desktop", 0) == EXPECTED_DESKTOP,
          "found %d" % groups.get("desktop", 0))
    check("trung binh count 37", diffs.get("trung binh", 0) == EXPECTED_TRUNG_BINH,
          "found %d" % diffs.get("trung binh", 0))
    check("kho count 11", diffs.get("kho", 0) == EXPECTED_KHO,
          "found %d" % diffs.get("kho", 0))
    check("rat kho count 7", diffs.get("rat kho", 0) == EXPECTED_RAT_KHO,
          "found %d" % diffs.get("rat kho", 0))

    # Section 7 states the same counts; cross-check the doc against itself.
    check("section 7 states 55 total", "Tong: 55 task" in sec7)
    check("section 7 states browser 35", "35 task" in sec7)
    check("section 7 states desktop 20", "20 task" in sec7)
    check("section 7 states trung binh 37", "Trung binh: 37 task" in sec7)
    check("section 7 states kho 11", "Kho: 11 task" in sec7)
    check("section 7 states rat kho 7", "Rat kho: 7 task" in sec7)

    # Every task body has Pass, Fail, held-out lines.
    bodies = re.split(r"\n### R3-\d+, ", sec6)[1:]
    missing = []
    for tid, body in zip(ids, bodies):
        if "- Pass:" not in body:
            missing.append(tid + ":Pass")
        if "- Fail:" not in body:
            missing.append(tid + ":Fail")
        if "Bang chung held-out" not in body:
            missing.append(tid + ":held-out")
    check("every task has Pass, Fail, held-out lines", not missing,
          "missing: %s" % missing)

    # Backups.
    for dp in ("DP-01", "DP-02", "DP-03", "DP-05"):
        check("backup %s present in section 8" % dp,
              ("  - %s," % dp) in sec8 or ("- %s," % dp) in sec8)
    check("DP-04 has no task definition",
          "### DP-04" not in text and "- DP-04," not in sec8)
    check("DP-04 removal is recorded",
          "DP-04" in text and "da loai" in text)

    # Answer keys.
    for label, secnum, needle in KEY_CHECKS:
        hay = {6: sec6, 8: sec8}[secnum]
        check("key present: %s" % label, needle in hay)

    # Section 1 pass table and invalid caps.
    check("pass bar 53/55 in section 1",
          "55 task hop le thi can 53 pass" in sec1)
    check("invalid cap 5 total in section 1",
          "So task vo hieu toi da la 5" in sec1)
    check("invalid cap 2 per difficulty group in section 1",
          "toi da 2 trong moi nhom do kho" in sec1)

    # Section 9 removal log lists every removed ID.
    missing_log = [i for i in REMOVED if i not in sec9]
    check("section 9 log lists all 45 removed IDs", not missing_log,
          "missing from log: %s" % missing_log)

    # Freeze check: sha256 of the list file matches frozen-heads.txt.
    if os.path.isfile(frozen_path):
        frozen = {}
        for line in open(frozen_path, encoding="utf-8"):
            parts = line.split()
            if len(parts) == 2:
                frozen[parts[0]] = parts[1]
        digest = hashlib.sha256(open(list_path, "rb").read()).hexdigest()
        check("list sha256 matches frozen-heads.txt",
              frozen.get("list_sha256") == digest,
              "file=%s frozen=%s" % (digest, frozen.get("list_sha256")))
        if frozen.get("list_commit"):
            print("INFO: frozen list commit recorded as %s"
                  % frozen["list_commit"])
    else:
        fails.append("frozen-heads.txt missing: %s" % frozen_path)

    pendings.extend(PENDING_KEYS)

    for name in passes:
        print("PASS: %s" % name)
    for name in pendings:
        print("PENDING: %s" % name)
    for name in fails:
        print("FAIL: %s" % name)
    print("RESULT: %d pass, %d pending, %d fail"
          % (len(passes), len(pendings), len(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
