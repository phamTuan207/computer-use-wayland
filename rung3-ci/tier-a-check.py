#!/usr/bin/env python3
"""Rung 3 Tier A deterministic checker driver.

Compares evidence values to the frozen key JSON and exits 0 for PASS
or 1 for FAIL with machine-readable reasons. Exit 2 means SKIP: the
task has no Tier A key yet or the evidence folder is missing a
file the check needs.

Usage:
  python3 rung3-ci/tier-a-check.py --key <key.json> --evidence <dir> --task <ID>

  --key defaults to docs/rung3-answer-keys.json (the frozen key file).
  Until that file exists, pass --key rung3-ci/test-keys.json, which is
  a TEST key built only from values already in the list (section 8
  plus the R3-014 Pass line) and from the preserved trial inputs for
  R3-007. Never grade a real run against the test key.

  DP-02 (keyword-counts) reads its key from the frozen key JSON and
  checks the evidence two ways: when the 12 fixture files
  (dp02-01.txt to dp02-12.txt, at the evidence root or under
  dp02-code/) are present, it recounts every keyword with the same
  grep -o -F the key specifies and compares the per-file matrix,
  totals, top files, grand total and files-with-keyword count; it
  also parses bao-cao.txt (fallback names dp02-bao-cao.txt,
  ket-qua.txt) for the reported totals and top files and compares
  those. Both sources are required and both must PASS: a missing
  report FAILS and missing fixture files FAIL. The evidence
  requirement for DP-02 is bao-cao.txt plus the 12 fixture files
  dp02-01.txt to dp02-12.txt under dp02-code/.

Output: one JSON object on stdout:
  {"task": ..., "verdict": "PASS|FAIL|SKIP", "reasons": [...],
   "key_hash": ..., "evidence_files": [...]}
No human judgment inside this script. A human scorer still confirms
the required evidence files exist and screenshots are legible.
No personal info in this file.
"""
import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def norm_pattern(p):
    """Accept the escaped regex101 form: \\/ counts as /."""
    return p.replace("\\/", "/")


def safe_eval(expr):
    """Evaluate a numeric expression with + - * / and parentheses only."""
    tree = ast.parse(expr, mode="eval")
    allowed = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Add, ast.Sub,
               ast.Mult, ast.Div, ast.USub, ast.UAdd, ast.Constant,
               ast.Load)
    for node in ast.walk(tree):
        if not isinstance(node, allowed):
            raise ValueError("unsupported node %s" % type(node).__name__)
        if isinstance(node, ast.Constant) and not isinstance(
                node.value, (int, float)):
            raise ValueError("non-numeric constant")
    return eval(compile(tree, "<expr>", "eval"), {"__builtins__": {}})


def convert(value, from_unit, to_unit):
    if (from_unit, to_unit) == ("km", "miles"):
        return value / 1.609344
    if (from_unit, to_unit) == ("miles", "km"):
        return value * 1.609344
    if (from_unit, to_unit) == ("kg", "lb"):
        return value * 2.2046226218
    if (from_unit, to_unit) == ("C", "F"):
        return value * 9.0 / 5.0 + 32.0
    if (from_unit, to_unit) == ("L", "gal"):
        return value / 3.785411784
    raise ValueError("unknown conversion %s to %s" % (from_unit, to_unit))


def check_json_errors(text, key, reasons):
    # Bilingual (owner order 2026-11-25): accept the Vietnamese form
    # "dong loi N, cot loi M" AND English forms ("line N, col M",
    # "line N column M", "Error line N ... Error column M").
    # Union of all patterns: acceptance only broadens, a text that
    # matched before still matches. Already-graded results are
    # untouched; this applies to remaining tasks only.
    patterns = [
        r"dong loi\s+(\d+)\s*,\s*cot loi\s+(\d+)",
        r"line\s+(\d+)\s*,\s*col(?:umn)?\s+(\d+)",
        r"line\s+(\d+)\s+col(?:umn)?\s+(\d+)",
        r"error\s+line\s*:?\s*(\d+)[^\d]{0,30}?error\s+col(?:umn)?\s*:?\s*(\d+)",
    ]
    found = []
    for pat in patterns:
        for l, c in re.findall(pat, text, re.IGNORECASE):
            pair = (int(l), int(c))
            if pair not in found:
                found.append(pair)
    for want in key["rows"]:
        if (want["line"], want["col"]) not in found:
            reasons.append("missing JSON error at line %s col %s"
                           % (want["line"], want["col"]))
    if len(found) < len(key["rows"]):
        reasons.append("only %d error positions found, need %d"
                       % (len(found), len(key["rows"])))


def check_unit_conversion(text, key, reasons):
    rows = []
    for line in text.splitlines():
        m = re.match(r"\s*([\d.]+)\s*(\S+)\s*=\s*([\d.]+)\s*(.+?)\s*$", line)
        if m:
            rows.append((float(m.group(1)), m.group(2),
                         float(m.group(3)), m.group(4).strip()))
    inputs = key["inputs"]
    if len(rows) < len(inputs):
        reasons.append("only %d conversion rows, need %d"
                       % (len(rows), len(inputs)))
        return
    for i, (val, frm, to, to_unit) in enumerate(inputs):
        got = None
        for (v, fu, r, tu) in rows:
            if abs(v - val) < 1e-9 and fu == frm:
                got = (r, tu)
        if got is None:
            reasons.append("missing input %s %s" % (val, frm))
            continue
        if got[1] != to_unit:
            reasons.append("row %d: unit %s, expected %s"
                           % (i + 1, got[1], to_unit))
        expected = convert(val, frm, to)
        if abs(got[0] - expected) > 0.01:
            reasons.append("row %d: result %s, expected %.4f (tol 0.01)"
                           % (i + 1, got[0], expected))


def check_regex_counts(text, key, reasons):
    rows = {}
    for line in text.splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) == 3 and parts[1].isdigit():
            matches = [m.strip() for m in parts[2].split(",") if m.strip()]
            rows[norm_pattern(parts[0])] = (int(parts[1]), matches)
    for want in key["rows"]:
        pat = norm_pattern(want["pattern"])
        if pat not in rows:
            reasons.append("missing pattern %s" % want["pattern"])
            continue
        count, matches = rows[pat]
        if count != want["count"]:
            reasons.append("pattern %s: count %d, expected %d"
                           % (want["pattern"], count, want["count"]))
        if sorted(matches) != sorted(want["matches"]):
            reasons.append("pattern %s: matches %s, expected %s"
                           % (want["pattern"], matches, want["matches"]))


def check_color_rgb(text, key, reasons):
    pairs = re.findall(r"(#[0-9A-Fa-f]{6})\D{0,40}?RGB\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", text)
    found = {}
    for hx, r, g, b in pairs:
        found[hx.upper()] = (int(r), int(g), int(b))
    if not pairs:
        # Fallback: hex codes and RGB triples in file order.
        hexes = [h.upper() for h in re.findall(r"#[0-9A-Fa-f]{6}", text)]
        rgbs = [(int(r), int(g), int(b)) for r, g, b in
                re.findall(r"RGB\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", text)]
        found = dict(zip(hexes, rgbs))
    for want in key["rows"]:
        got = found.get(want["hex"].upper())
        if got is None:
            reasons.append("missing color %s" % want["hex"])
        elif list(got) != want["rgb"]:
            reasons.append("color %s: RGB %s, expected %s"
                           % (want["hex"], list(got), want["rgb"]))


def check_sql_order_total(text, key, reasons, ev_dir):
    order = key["order"]
    seq = []
    for name, _val in order:
        for m in re.finditer(re.escape(name) + r"\s+(\d+)", text):
            seq.append((name, int(m.group(1))))
    # Keep the first occurrence of each name in file order.
    seen = []
    for item in seq:
        if item[0] not in [s[0] for s in seen]:
            seen.append(item)
    if seen != [tuple(x) for x in order]:
        reasons.append("query order %s, expected %s" % (seen, order))
    m = re.search(r"6750", text)
    if str(key["total"]) not in text:
        reasons.append("total %s not found in ket-qua.txt" % key["total"])
    csv_path = os.path.join(ev_dir, "ket-qua-truy-van.csv")
    if not os.path.isfile(csv_path):
        reasons.append("missing ket-qua-truy-van.csv")
    else:
        lines = [l for l in read_text(csv_path).splitlines() if l.strip()]
        # Header row is optional (R3-021: headerless quoted CSV was
        # counted as if it had a header). The first line is a data
        # row when its last cell is an integer; otherwise it is a
        # header. Union-only: with-header files count as before.
        data_rows = len(lines)
        if lines:
            cells = [c.strip().strip('"')
                     for c in lines[0].split(",")]
            if not (len(cells) >= 2 and cells[-1].isdigit()):
                data_rows -= 1
        if data_rows != len(order):
            reasons.append("CSV has %d data rows, expected %d"
                           % (data_rows, len(order)))


def check_image_sizes(text, key, reasons):
    found = {}
    # Separators between file name and size may be whitespace, a
    # pipe (R3-072 table rows), a colon or a dash (numbered rows).
    # Union-only: plain "name.png 800x600" still matches.
    for name, w, h in re.findall(
            r"(\S+\.png)[\s|:\-\u2013\u2014]*(\d+)\s*x\s*(\d+)", text):
        found[name] = "%sx%s" % (w, h)
    for want in key["rows"]:
        got = found.get(want["file"])
        if got is None:
            reasons.append("missing image %s" % want["file"])
        elif got != want["size"]:
            reasons.append("image %s: size %s, expected %s"
                           % (want["file"], got, want["size"]))


def check_calculations(text, key, reasons):
    rows = []
    for line in text.splitlines():
        m = re.match(r"\s*(.+?)\s*=\s*(-?[\d.]+)\s*$", line)
        if m and re.search(r"[+\-*/()]", m.group(1)):
            rows.append((m.group(1).strip(), float(m.group(2))))
    for want in key["rows"]:
        hit = None
        for expr, result in rows:
            if expr.replace(" ", "") == want["expr"].replace(" ", ""):
                hit = result
        if hit is None:
            reasons.append("missing calculation %s" % want["expr"])
            continue
        if abs(hit - want["result"]) > 0.01:
            reasons.append("calculation %s: result %s, expected %s"
                           % (want["expr"], hit, want["result"]))
        try:
            computed = safe_eval(want["expr"])
            if abs(computed - want["result"]) > 0.01:
                reasons.append("key error: %s computes to %s, key says %s"
                               % (want["expr"], computed, want["result"]))
        except ValueError as e:
            reasons.append("cannot evaluate key expr %s: %s"
                           % (want["expr"], e))


def check_report_consistency(ev_dir, key, reasons):
    """R3-076: bao-cao values must match the saved command-output files."""
    need = ["d42-bao-cao.txt", "d42-lenh-dia.txt", "d42-lenh-ram.txt",
            "d42-lenh-tien-trinh.txt"]
    texts = {}
    for name in need:
        path = os.path.join(ev_dir, name)
        if not os.path.isfile(path):
            reasons.append("missing %s" % name)
            return
        texts[name] = read_text(path)
    bao = texts["d42-bao-cao.txt"]
    # Bilingual labels (owner order 2026-11-25): Vietnamese
    # "Dia con trong:" / "RAM con trong:" and English
    # "Disk free:" / "Free disk:" / "RAM free:" / "Free RAM:".
    # R3-076 adds the section forms "Free on /:" (disk) and
    # "Free (free column):" (RAM). Acceptance only broadens.
    m = re.search(r"(?:Dia con trong|Disk free|Free disk|Free on \S+)"
                  r"\s*:\s*(\S+)", bao, re.IGNORECASE)
    if not m or m.group(1) not in texts["d42-lenh-dia.txt"]:
        reasons.append("disk free value in bao-cao not found in lenh-dia")
    m = re.search(r"(?:RAM con trong|RAM free|Free RAM|"
                  r"Free \(free column\))\s*:\s*(\S+)",
                  bao, re.IGNORECASE)
    if not m or m.group(1) not in texts["d42-lenh-ram.txt"]:
        reasons.append("RAM free value in bao-cao not found in lenh-ram")
    # Process rows: whitespace form ("name PID cpu mem") or pipe
    # form ("name | PID | cpu | rss ...", R3-076). Union-only.
    procs = []
    for line in bao.splitlines():
        s = line.strip()
        if re.match(r"\S+\s+\d+\s+[\d.]+\s+[\d.]+", s):
            name, pid = s.split()[:2]
            procs.append((name, pid))
            continue
        cells = [c.strip() for c in s.split("|")]
        if len(cells) >= 4 and cells[1].isdigit() and \
                re.fullmatch(r"[\d.]+", cells[2]):
            procs.append((cells[0], cells[1]))
    if len(procs) < 5:
        reasons.append("bao-cao has %d process rows, need 5"
                       % len(procs))
    for name, pid in procs:
        if name not in texts["d42-lenh-tien-trinh.txt"] or \
                pid not in texts["d42-lenh-tien-trinh.txt"]:
            reasons.append("process %s PID %s not in lenh-tien-trinh"
                           % (name, pid))


def check_sql_join(text, key, reasons):
    for label, pairs in (("JOIN step 2", key["join_rows"]),
                         ("GROUP BY qty step 3", key["group_qty"]),
                         ("GROUP BY value step 4", key["group_value"])):
        for name, value in pairs:
            if not re.search(re.escape(name) + r"\s+" + str(value) + r"\b",
                             text):
                reasons.append("%s: missing %s %s" % (label, name, value))
    for label, want in (("step 2 rows", key["join_row_count"]),
                        ("step 3 rows", key["group_row_count"]),
                        ("step 4 rows", key["group_row_count"])):
        pass


def grep_count(path, keyword):
    """Count literal occurrences of keyword in one file.

    Same count as `grep -o -F <keyword> <file> | wc -l` (one line per
    match, exit 1 means no match). Falls back to a pure-Python
    literal count when grep is unavailable; the two agree for these
    keywords because none is a substring of another and none can
    overlap with itself.
    """
    try:
        proc = subprocess.run(["grep", "-o", "-F", keyword, path],
                              capture_output=True, text=True,
                              errors="replace")
        if proc.returncode == 0:
            return len(proc.stdout.splitlines())
        if proc.returncode == 1:
            return 0
    except OSError:
        pass
    return read_text(path).count(keyword)


def check_keyword_counts(ev_dir, key, reasons):
    """DP-02: compare keyword counts against the frozen key.

    Both evidence sources are required and both must PASS:
      - fixture files dp02-01.txt..dp02-12.txt (at the evidence root
        or under dp02-code/): recount every keyword with grep -o -F
        and compare the per-file matrix, totals, top files, grand
        total and files-with-keyword count. A fixture file present
        but unreadable FAILS with reason fixture file unreadable.
      - report bao-cao.txt (or dp02-bao-cao.txt, or ket-qua.txt):
        parse the reported totals and top files in the shape the key
        file shows ("alpha7: tong 12, file nhieu hit nhat
        dp02-01.txt (4 hit)") and compare them. The grand total
        line and the files-with-keyword line MUST be stated and
        MUST match the key. A missing line FAILS.
    """
    keywords = key.get("keywords", [])
    per_file_key = key.get("per_file", {})
    if not keywords:
        reasons.append("key has no keywords list for DP-02")
        return

    fixture_files = {}
    for cand_dir in (ev_dir, os.path.join(ev_dir, "dp02-code")):
        if os.path.isdir(cand_dir):
            for name in sorted(os.listdir(cand_dir)):
                if re.fullmatch(r"dp02-\d+\.txt", name):
                    fixture_files.setdefault(name, os.path.join(cand_dir, name))
    expected_names = sorted(per_file_key) or \
        ["dp02-%02d.txt" % n for n in range(1, 13)]

    missing = [n for n in expected_names if n not in fixture_files]
    if missing:
        reasons.append("fixture files missing: %s"
                       % ", ".join(missing))
    extra = [n for n in sorted(fixture_files)
             if n not in expected_names]
    if extra:
        reasons.append("unexpected fixture files: %s"
                       % ", ".join(extra))
    unreadable = []
    for name in sorted(fixture_files):
        path = fixture_files[name]
        try:
            if os.stat(path).st_mode & 0o444 == 0:
                unreadable.append(name)
                continue
            with open(path, "rb") as f:
                f.read(1)
        except OSError:
            unreadable.append(name)
    for name in unreadable:
        reasons.append("fixture file unreadable: %s" % name)
    readable_files = {n: p for n, p in fixture_files.items()
                      if n not in unreadable}
    if readable_files:
        grand = 0
        files_with = set()
        for entry in keywords:
            kw = entry["keyword"]
            counts = {}
            for name in sorted(readable_files):
                try:
                    counts[name] = grep_count(readable_files[name], kw)
                except OSError:
                    reasons.append("fixture file unreadable: %s" % name)
            total = sum(counts.values())
            grand += total
            for name, count in counts.items():
                if count:
                    files_with.add(name)
                want = per_file_key.get(name, {}).get(kw)
                if want is not None and count != want:
                    reasons.append("fixture recount %s in %s: %d, "
                                   "expected %d" % (kw, name, count, want))
            if total != entry["total"]:
                reasons.append("fixture recount %s: total %d, expected %d"
                               % (kw, total, entry["total"]))
            if counts:
                top_name, top_count = max(sorted(counts.items()),
                                          key=lambda kv: kv[1])
                if top_name != entry["top_file"]:
                    reasons.append("fixture recount %s: top file %s, "
                                   "expected %s" % (kw, top_name,
                                                    entry["top_file"]))
                if top_count != entry["top_count"]:
                    reasons.append("fixture recount %s: top count %d, "
                                   "expected %d" % (kw, top_count,
                                                    entry["top_count"]))
        if "grand_total" in key and grand != key["grand_total"]:
            reasons.append("fixture recount grand total %d, expected %d"
                           % (grand, key["grand_total"]))
        if "files_with_keyword" in key and \
                len(files_with) != key["files_with_keyword"]:
            reasons.append("fixture recount files with keyword %d, "
                           "expected %d"
                           % (len(files_with), key["files_with_keyword"]))

    report_path = None
    for name in ("bao-cao.txt", "dp02-bao-cao.txt", "ket-qua.txt"):
        cand = os.path.join(ev_dir, name)
        if os.path.isfile(cand):
            report_path = cand
            break
    if report_path is None:
        reasons.append("missing bao-cao.txt in evidence folder")
        return
    report_name = os.path.basename(report_path)
    lines = read_text(report_path).splitlines()
    # The "(N dong)" parenthetical is optional (DP-02).
    detail_re = re.compile(
        r"^(dp02-\d+\.txt)(?:\s*\(\d+\s*dong\))?\s*:\s*(.*)$")
    for entry in keywords:
        kw = entry["keyword"]
        strict_re = re.compile(
            r"^" + re.escape(kw) + r":\s*tong\s+(\d+),\s*"
            r"file nhieu hit nhat\s+(dp02-\d+\.txt)\s*"
            r"\(\s*(\d+)\s*hit\s*\)\s*$")
        m = None
        for line in lines:
            m = strict_re.match(line.strip())
            if m:
                break
        if m is None:
            reasons.append("keyword %s: line not in required format "
                           "in %s" % (kw, report_name))
            continue
        got_total = int(m.group(1))
        got_top = m.group(2)
        got_top_count = int(m.group(3))
        if got_total != entry["total"]:
            reasons.append("keyword %s: report total %d, expected %d"
                           % (kw, got_total, entry["total"]))
        if got_top != entry["top_file"]:
            reasons.append("keyword %s: report top file %s, expected %s"
                           % (kw, got_top, entry["top_file"]))
        if got_top_count != entry["top_count"]:
            reasons.append("keyword %s: report top count %d, expected %d"
                           % (kw, got_top_count, entry["top_count"]))
    grand_stated = None
    for line in lines:
        m = re.match(r"^\s*Tong chung\s*:\s*(\d+)\s*$", line)
        if m:
            grand_stated = int(m.group(1))
            break
    if grand_stated is None:
        reasons.append("report grand total not stated in %s"
                       % report_name)
    elif "grand_total" in key and \
            grand_stated != key["grand_total"]:
        reasons.append("report grand total %d, expected %d"
                       % (grand_stated, key["grand_total"]))
    files_stated = None
    for line in lines:
        m = re.match(r"^\s*So file chua it nhat 1 tu khoa\s*:\s*(\d+)\s*$",
                     line)
        if m:
            files_stated = int(m.group(1))
            break
    if files_stated is None:
        reasons.append("report files with keyword not stated in %s"
                       % report_name)
    elif "files_with_keyword" in key and \
            files_stated != key["files_with_keyword"]:
        reasons.append("report files with keyword %d, expected %d"
                       % (files_stated, key["files_with_keyword"]))
    detail_seen = set()
    for line in lines:
        dm = detail_re.match(line.strip())
        if not dm:
            continue
        detail_seen.add(dm.group(1))
        fname, rest = dm.group(1), dm.group(2)
        want = per_file_key.get(fname, {})
        for kw in [e["keyword"] for e in keywords]:
            m = re.search(re.escape(kw) + r"\s+(\d+)", rest)
            if m and kw in want and int(m.group(1)) != want[kw]:
                reasons.append("report %s in %s: %d, expected %d"
                               % (kw, fname, int(m.group(1)), want[kw]))
    # The DP-02 brief requires only the summary table, grand total
    # and files-with-keyword count; the per-file detail block is
    # optional as a whole because the fixture recount above already
    # verifies the per-file matrix. A partial detail block still
    # FAILS: once any detail line is present, all files are required.
    if detail_seen:
        for name in expected_names:
            if name not in detail_seen:
                reasons.append(
                    "report per-file detail missing for %s in %s"
                    % (name, report_name))


CHECKERS = {
    "json-errors": lambda t, k, r, d: check_json_errors(t, k, r),
    "unit-conversion": lambda t, k, r, d: check_unit_conversion(t, k, r),
    "regex-counts": lambda t, k, r, d: check_regex_counts(t, k, r),
    "color-rgb": lambda t, k, r, d: check_color_rgb(t, k, r),
    "sql-order-total": check_sql_order_total,
    "image-sizes": lambda t, k, r, d: check_image_sizes(t, k, r),
    "calculations": lambda t, k, r, d: check_calculations(t, k, r),
    "sql-join": lambda t, k, r, d: check_sql_join(t, k, r),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", default=None)
    ap.add_argument("--evidence", required=True)
    ap.add_argument("--task", required=True)
    args = ap.parse_args()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    key_path = args.key or os.path.join(root, "docs",
                                        "rung3-answer-keys.json")
    result = {"task": args.task, "verdict": "SKIP", "reasons": [],
              "key_hash": None, "evidence_files": []}
    if not os.path.isfile(key_path):
        result["reasons"] = ["key file missing: %s (frozen key not yet "
                             "written; pass --key rung3-ci/test-keys.json "
                             "for testing only)" % key_path]
        print(json.dumps(result, sort_keys=True))
        return 2
    result["key_hash"] = sha256_file(key_path)
    keys = json.load(open(key_path, encoding="utf-8"))
    entry = keys.get("tasks", {}).get(args.task)
    if entry is None:
        result["reasons"] = ["no Tier A key for %s in %s"
                             % (args.task, key_path)]
        print(json.dumps(result, sort_keys=True))
        return 2
    if not os.path.isdir(args.evidence):
        result["reasons"] = ["evidence folder missing: %s" % args.evidence]
        print(json.dumps(result, sort_keys=True))
        return 2
    result["evidence_files"] = sorted(os.listdir(args.evidence))
    ket_path = os.path.join(args.evidence, "ket-qua.txt")
    checker = CHECKERS.get(entry.get("type"))
    if entry.get("type") == "report-consistency":
        reasons = []
        check_report_consistency(args.evidence, entry, reasons)
        result["reasons"] = reasons
    elif entry.get("type") == "keyword-counts":
        reasons = []
        check_keyword_counts(args.evidence, entry, reasons)
        result["reasons"] = reasons
    elif checker is None:
        result["reasons"] = ["unknown checker type %s for %s"
                             % (entry.get("type"), args.task)]
        print(json.dumps(result, sort_keys=True))
        return 2
    else:
        if not os.path.isfile(ket_path):
            result["reasons"] = ["missing ket-qua.txt in evidence folder"]
            print(json.dumps(result, sort_keys=True))
            return 2
        reasons = []
        checker(read_text(ket_path), entry, reasons, args.evidence)
        result["reasons"] = reasons
    result["verdict"] = "PASS" if not result["reasons"] else "FAIL"
    print(json.dumps(result, sort_keys=True))
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
