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
  9. The 7 synthesis-owned values (DP-02 keywords, DP-03 exact N,
     R3-003/R3-004 full keys, R3-007 input values, Tier C rubrics
     for R3-067/R3-083, R3-085 reference frame) are checked against
     the frozen key files docs/rung3-answer-keys.json/.md when those
     files exist. While a key file is absent the item stays PENDING;
     once frozen, a missing or wrong value is a FAIL.

Exit 0 only if zero FAIL checks. PENDING items are synthesis-owned
keys not yet frozen; they are listed, not hidden, and do not block
exit 0.

Usage:
  python3 rung3-ci/verify-list.py [--list PATH] [--frozen PATH]
      [--key-json PATH] [--key-md PATH]
No personal info in this file.
"""
import argparse
import hashlib
import json
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
    ("R3-013 sample text", 8, "hoa@example.com"),
    ("R3-013 pattern counts", 8, "2.750.000"),
    ("R3-021 query order", 8, "Giuong 600, Tu 400, Ghe 250, Ban 150"),
    ("R3-021 total", 8, "tong gia tri buoc 5: 6750"),
    ("R3-072 fixture sizes", 8, "d72-anh-1.png 800x600"),
    ("R3-082 calculations", 8, "(14 + 6) * 4 - 9 = 71"),
    ("R3-082 calculations (5th)", 8, "(11 + 9) * 5 / 4 = 25"),
    ("R3-014 RGB values", 6, "#FF0000 la RGB(255, 0, 0)"),
    ("R3-009 URLs", 8, "https://www.bbc.com/"),
    ("R3-009 URLs (2nd)", 8, "https://en.wikipedia.org/wiki/Main_Page"),
    ("R3-019 flight dates rule", 8, "ngay chay cong 30 ngay"),
    ("DP-05 tables", 8, "SP01 Ban 150"),
    ("DP-05 JOIN results", 8, "DH01 Ban 10"),
    ("DP-02 fixture rule", 8, "12 file van ban trong ~/rung3/dp02-code"),
]

# Synthesis-owned values, now frozen in the key files. Used only as
# PENDING messages while a key file is absent; when the key files
# exist the values below are checked against them (see main()).
PENDING_KEYS = [
    "DP-02 keywords: frozen key JSON not present yet.",
    "DP-03 exact port count N: frozen key file not present yet.",
    "R3-003 full key: frozen key file not present yet.",
    "R3-004 full key: frozen key file not present yet.",
    "R3-007 input values: frozen key JSON not present yet.",
    "Tier C rubrics R3-067/R3-083: frozen key file not present yet.",
    "R3-085 reference frame: frozen key file not present yet.",
]

# Expected frozen values (must match docs/rung3-answer-keys.json/.md).
EXPECTED_DP02 = [
    ("alpha7", 12, "dp02-01.txt", 4),
    ("bravo21", 9, "dp02-02.txt", 3),
    ("charlie9", 15, "dp02-03.txt", 5),
    ("delta42", 7, "dp02-06.txt", 3),
    ("echo13", 11, "dp02-04.txt", 4),
]
EXPECTED_DP02_GRAND_TOTAL = 54
EXPECTED_DP02_FILES_WITH_KEYWORD = 12
EXPECTED_R3007_INPUTS = [
    [12, "km", "miles", "miles"],
    [8, "miles", "km", "km"],
    [7, "kg", "lb", "lb"],
    [30, "C", "F", "F"],
    [5, "L", "gal", "US gallons"],
]
EXPECTED_R3007_EXPECTED = [7.4565, 12.8748, 15.4324, 86.0, 1.3209]
R3003_NEEDLES = ["Navanethem", "9 October 2026", "Oslo",
                 "12 trieu crown", "KHONG co mau thuan"]
R3004_NEEDLES = ["rm -rf /usr/local/go",
                 "export PATH=$PATH:/usr/local/go/bin",
                 "go version", "https://go.dev/doc/install"]
R3067_NEEDLES = ["hinh chu nhat, vung x 50-350, y 50-250, to mau do",
                 "hinh tron, vung x 300-500, y 200-400, to mau xanh duong",
                 "hinh tam giac", "800x600", "nen trang"]
R3083_NEEDLES = ["Chao mung", "#1E88E5", "#43A047", "1200x628",
                 "co chu 72"]
R3085_NEEDLES = ["r3-085-khung-tham-chieu.png",
                 "de410f94b2192e553f4a78ff42df8bcfd84e29e5908c3f02775125cfa4c759c2",
                 "ffmpeg -ss 00:10", "RGB (118.2, 139.7, 121.3)"]


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
    ap.add_argument("--key-json", default=None)
    ap.add_argument("--key-md", default=None)
    args = ap.parse_args()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    list_path = args.list or os.path.join(root, "docs", "rung3-list-100-tasks.md")
    frozen_path = args.frozen or os.path.join(root, "rung3-ci", "frozen-heads.txt")
    key_json_path = args.key_json or os.path.join(
        root, "docs", "rung3-answer-keys.json")
    key_md_path = args.key_md or os.path.join(
        root, "docs", "rung3-answer-keys.md")

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

    # Frozen key checks: the 7 synthesis-owned values. When a key file
    # exists, verify each value against it (PASS/FAIL); while a key
    # file is absent, the item stays PENDING (non-blocking).
    def md_section(text, heading, hashes="##"):
        parts = re.split(r"\n" + hashes + r" " + re.escape(heading) + r"\b",
                         text)
        if len(parts) < 2:
            return ""
        rest = parts[1]
        nxt = re.search(r"\n#{1,4} ", rest)
        return rest[:nxt.start()] if nxt else rest

    key_json = None
    if os.path.isfile(key_json_path):
        try:
            key_json = json.load(open(key_json_path, encoding="utf-8"))
        except ValueError as e:
            fails.append("frozen key JSON unreadable: %s: %s"
                         % (key_json_path, e))
    key_md = ""
    if os.path.isfile(key_md_path):
        key_md = open(key_md_path, encoding="utf-8").read()

    if key_json is None:
        pendings.append(PENDING_KEYS[0])
        pendings.append(PENDING_KEYS[4])
    else:
        tasks = key_json.get("tasks", {})
        dp02 = tasks.get("DP-02") or {}
        got_dp02 = sorted(
            (k["keyword"], k["total"], k["top_file"], k["top_count"])
            for k in dp02.get("keywords", []))
        check("frozen key: DP-02 keywords match key JSON",
              dp02.get("type") == "keyword-counts"
              and got_dp02 == sorted(EXPECTED_DP02)
              and dp02.get("grand_total") == EXPECTED_DP02_GRAND_TOTAL
              and dp02.get("files_with_keyword")
              == EXPECTED_DP02_FILES_WITH_KEYWORD,
              "keywords=%s grand=%s files=%s"
              % (got_dp02, dp02.get("grand_total"),
                 dp02.get("files_with_keyword")))
        r3007 = tasks.get("R3-007") or {}
        check("frozen key: R3-007 inputs match key JSON",
              r3007.get("type") == "unit-conversion"
              and r3007.get("inputs") == EXPECTED_R3007_INPUTS
              and r3007.get("expected") == EXPECTED_R3007_EXPECTED,
              "inputs=%s expected=%s"
              % (r3007.get("inputs"), r3007.get("expected")))

    if not key_md:
        pendings.extend(PENDING_KEYS[1:4] + PENDING_KEYS[5:])
    else:
        dp03_sec = md_section(key_md, "DP-03")
        check("frozen key: DP-03 N=5 in key file",
              "- DP-03: N = 5." in key_md and "N = 5" in dp03_sec,
              "ruling line present: %s; DP-03 section has N=5: %s"
              % ("- DP-03: N = 5." in key_md, "N = 5" in dp03_sec))
        r3003_sec = md_section(key_md, "R3-003")
        missing = [n for n in R3003_NEEDLES if n not in r3003_sec]
        check("frozen key: R3-003 full key in key file", not missing,
              "missing from R3-003 section: %s" % missing)
        r3004_sec = md_section(key_md, "R3-004")
        missing = [n for n in R3004_NEEDLES if n not in r3004_sec]
        steps = len(re.findall(r"^\s*\d+\. ", r3004_sec, re.M))
        check("frozen key: R3-004 full key in key file",
              not missing and steps == 5,
              "missing: %s; numbered steps: %d" % (missing, steps))
        r3067_sec = md_section(key_md, "R3-067", hashes="###")
        missing = [n for n in R3067_NEEDLES if n not in r3067_sec]
        check("frozen key: Tier C rubric R3-067 in key file", not missing,
              "missing from R3-067 rubric: %s" % missing)
        r3083_sec = md_section(key_md, "R3-083", hashes="###")
        missing = [n for n in R3083_NEEDLES if n not in r3083_sec]
        check("frozen key: Tier C rubric R3-083 in key file", not missing,
              "missing from R3-083 rubric: %s" % missing)
        missing = [n for n in R3085_NEEDLES if n not in key_md]
        check("frozen key: R3-085 reference frame in key file",
              not missing, "missing: %s" % missing)

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
