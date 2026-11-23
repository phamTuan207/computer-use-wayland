#!/usr/bin/env python3
"""Rung 3 Tier A deterministic checker driver.

Compares evidence values to the frozen key JSON and exits 0 for PASS
or 1 for FAIL with machine-readable reasons. Exit 2 means SKIP: the
task has no Tier A key yet (for example DP-02 keywords are allocated
by synthesis before the freeze) or the evidence folder is missing a
file the check needs.

Usage:
  python3 rung3-ci/tier-a-check.py --key <key.json> --evidence <dir> --task <ID>

  --key defaults to docs/rung3-answer-keys.json (the frozen key file).
  Until that file exists, pass --key rung3-ci/test-keys.json, which is
  a TEST key built only from values already in the list (section 8
  plus the R3-014 Pass line) and from the preserved trial inputs for
  R3-007. Never grade a real run against the test key.

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
    found = [(int(l), int(c)) for l, c in
             re.findall(r"dong loi\s+(\d+)\s*,\s*cot loi\s+(\d+)", text)]
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
        if len(lines) - 1 != len(order):
            reasons.append("CSV has %d data rows, expected %d"
                           % (len(lines) - 1, len(order)))


def check_image_sizes(text, key, reasons):
    found = {}
    for name, w, h in re.findall(r"(\S+\.png)\s+(\d+)\s*x\s*(\d+)", text):
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
    m = re.search(r"Dia con trong:\s*(\S+)", bao)
    if not m or m.group(1) not in texts["d42-lenh-dia.txt"]:
        reasons.append("disk free value in bao-cao not found in lenh-dia")
    m = re.search(r"RAM con trong:\s*(\S+)", bao)
    if not m or m.group(1) not in texts["d42-lenh-ram.txt"]:
        reasons.append("RAM free value in bao-cao not found in lenh-ram")
    proc_lines = [l for l in bao.splitlines()
                  if re.match(r"\S+\s+\d+\s+[\d.]+\s+[\d.]+", l.strip())]
    if len(proc_lines) < 5:
        reasons.append("bao-cao has %d process rows, need 5"
                       % len(proc_lines))
    for line in proc_lines:
        name, pid = line.split()[:2]
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
