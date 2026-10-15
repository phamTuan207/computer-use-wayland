"""Recompute published benchmark evidence from the sanitized aggregates.

Checks the MUSE2 aggregate (24 blocks, 1440 measured rows, 48 warmups),
all 12 workload cells x both variants (medians/p95 + byte medians), the
embedded summary, the exact doc table rows keyed by cell, the MUSE1
historical aggregate (180 live rows + 4 warmups verified per-row with
tasks/cleanup, 11 unit modules totalling 98 with sanitized log hashes),
and the R4 isolation aggregate (66 blocks: 360 desktop + 0 warmup,
480 + 48 CDP normal, 30 + 6 CDP image; recomputed summaries, per-round
gains, seeded paired-block CI and fixed gates), plus both R5 CDP comparisons
with Git-verified runtime sources and recomputed gates; R5 a11y/paint
correctness, timing/byte summaries and retained failure PNGs; and ordered
sample hashes across all aggregates.

Stdlib only. Read-only local Git blob verification; no shell, eval or network. Bounded output.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import math
import re
import statistics
import struct
import zlib
import sys


def require(condition, detail=None):
    if not condition:
        raise ValueError(detail if detail is not None else "check failed")


def median_p95(vals):
    require(len(vals) > 0)
    ordered = sorted(vals)
    count = len(ordered)
    return statistics.median(ordered), ordered[math.ceil(0.95 * count) - 1]


def fmt(value):
    return "%.3f" % value


HEX64 = re.compile(r"^[0-9a-f]{64}$")
DOC_ROW = re.compile(
    r"^\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([a-z\-]+)\s*\|"
    r"\s*([\d.]+)\s*/\s*([\d.]+)\s*\|"
    r"\s*([\d.]+)\s*/\s*([\d.]+)\s*\|"
    r"\s*([\d.]+)%\s*\(([\d.]+)\s*ms\)\s*\|"
    r"\s*(\d+)\s*(?:\u2192|->)\s*(\d+)\s*\|"
)


def samples_sha256(samples):
    """Ordered samples: sorted-key compact JSON, UTF-8, no newline or NaN.

    Detects edits without a matching hash update, not independent attestation;
    this does not verify raw_sha256 without the original raw file.
    """
    require(isinstance(samples, list), "samples must be a list")
    return hashlib.sha256(json.dumps(samples, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def check_samples_hash(block):
    require(block.get("samples_sha256") == samples_sha256(block["samples"]),
            "samples_sha256 mismatch: " + block.get("file", "live group"))


def main(muse2_path, muse1_path, doc_path, r4_path, r5_path,
         a11y_path="docs/benchmarks/r5_a11y_aggregate.json",
         paint_path="docs/benchmarks/r5_paint_aggregate.json"):
    # Tiny stdlib self-check of the helpers used below.
    require(statistics.median([1, 2, 3]) == 2)
    require(median_p95([1, 2, 3, 4, 5]) == (3, 5))
    require(DOC_ROW.match(
        "| 0 | 0 | task-scoped | 63.742 / 67.811 | 30.502 / 32.577 |"
        " 52.15% (33.240 ms) | 381 \u2192 381 |"
    ), "row regex self-check")

    muse2 = json.load(open(muse2_path))
    blocks = muse2["blocks"]
    require(len(blocks) == 24, len(blocks))
    totals = muse2["totals"]
    measured = sum(b["n_measured"] for b in blocks)
    warmups = sum(b["n_warmup"] for b in blocks)
    ok = sum(b["n_ok"] for b in blocks)
    require((measured, warmups, ok) == (1440, 48, 1440), (measured, warmups, ok))
    require(totals == {"measured": 1440, "warmups": 48, "ok": 1440}, totals)
    rows = 0
    for block in blocks:
        check_samples_hash(block)
        require(block["n_measured"] == 60 and block["n_ok"] == 60, block["file"])
        require(block["n_warmup"] == 2, block["file"])
        require(block["tasks_ok"] and block["cleanup_ok"], block["file"])
        require(block["variant"] in ("baseline", "candidate"), block["file"])
        require(len(block["samples"]) == 60, block["file"])
        require(isinstance(block["runtime_cdp_sha256"], str))
        require(HEX64.match(block["runtime_cdp_sha256"]), block["file"])
        rows += len(block["samples"])
        for sample in block["samples"]:
            require(sample["ok"] is True, block["file"])
            require(sample["mode"] in ("task-scoped", "task-after-scoped"))
            require(isinstance(sample["whole_task_ms"], (int, float)))
            require(isinstance(sample["total_ms"], (int, float)))
            require(isinstance(sample["result_bytes"], int))
    require(rows == 1440, rows)

    groups = {}
    byte_groups = {}
    for block in blocks:
        for sample in block["samples"]:
            key = (block["controls"], block["delay_ms"],
                   sample["mode"], block["variant"])
            groups.setdefault(key, []).append(sample["whole_task_ms"])
            byte_groups.setdefault(key, []).append(sample["result_bytes"])
    require(len(groups) == 24, len(groups))
    for key, vals in groups.items():
        require(len(vals) == 60, (key, len(vals)))
    summary = {(s["controls"], s["delay_ms"], s["route"], s["variant"]): s
               for s in muse2["summary"]}
    require(len(summary) == 24, len(summary))
    for key, vals in sorted(groups.items()):
        med, p95 = median_p95(vals)
        cell = summary[key]
        require(cell["n"] == 60, key)
        require(abs(cell["whole_task_ms_median"] - med) < 1e-9, key)
        require(abs(cell["whole_task_ms_p95"] - p95) < 1e-9, key)
        require(abs(cell["result_bytes_median"]
                   - statistics.median(sorted(byte_groups[key]))) < 1e-9, key)

    doc = open(doc_path).read()
    doc_rows = {}
    for line in doc.splitlines():
        match = DOC_ROW.match(line.strip())
        if match:
            delay, controls, route = (int(match.group(1)),
                                      int(match.group(2)), match.group(3))
            doc_rows[(controls, delay, route)] = match.groups()
    require(len(doc_rows) == 4, len(doc_rows))
    for (controls, delay, route) in sorted(doc_rows):
        require(delay == 0, (controls, delay, route))
        base = summary[(controls, delay, route, "baseline")]
        cand = summary[(controls, delay, route, "candidate")]
        base_med, base_p95 = median_p95(groups[(controls, delay, route,
                                                "baseline")])
        cand_med, cand_p95 = median_p95(groups[(controls, delay, route,
                                                "candidate")])
        groups_match = doc_rows[(controls, delay, route)]
        require(groups_match[3] == fmt(base_med), (route, groups_match[3]))
        require(groups_match[4] == fmt(base_p95), (route, groups_match[4]))
        require(groups_match[5] == fmt(cand_med), (route, groups_match[5]))
        require(groups_match[6] == fmt(cand_p95), (route, groups_match[6]))
        red_pct = (base_med - cand_med) / base_med * 100
        red_ms = base_med - cand_med
        require(groups_match[7] == ("%.2f" % red_pct), (route, groups_match[7]))
        require(groups_match[8] == fmt(red_ms), (route, groups_match[8]))
        require(int(groups_match[9]) == int(base["result_bytes_median"]), route)
        require(int(groups_match[10]) == int(cand["result_bytes_median"]), route)

    muse1 = json.load(open(muse1_path))
    live = muse1["live"]
    for group in live.values():
        check_samples_hash(group)
    browser = live["browser"]
    require(browser["tasks_ok"] and browser["cleanup_ok"], "browser cleanup")
    require((browser["n_measured"], browser["n_warmup"],
            browser["n_ok"]) == (120, 4, 120), browser["n_measured"])
    for sample in browser["samples"]:
        require(sample["ok"] is True)
        require(isinstance(sample["whole_task_ms"], (int, float)))
        require(isinstance(sample["result_bytes"], int))
    for name in ("desktop_full", "desktop_crop"):
        group = live[name]
        require(group["tasks_ok"], name)
        cleanup = group.get("cleanup", {})
        require(cleanup.get("children_reaped") is True, name)
        require((group["n_measured"], group["n_ok"]) == (30, 30), name)
        for sample in group["samples"]:
            require(sample["ok"] is True, name)
            require(isinstance(sample["whole_task_ms"], (int, float)))
            require(isinstance(sample["result_bytes"], int))
    live_rows = (len(browser["samples"])
                 + len(live["desktop_full"]["samples"])
                 + len(live["desktop_crop"]["samples"]))
    require((live_rows, browser["n_warmup"]) == (180, 4), live_rows)
    require(muse1["totals"]["live_measured"] == 180)
    require(muse1["totals"]["live_ok"] == 180)
    modules = muse1["installed_unittests"]["modules"]
    require(len(modules) == 11, len(modules))
    ran = 0
    seen_logs = set()
    for module in modules:
        require(module["ok"] and module["exit_code"] == 0, module["module"])
        require(module["failed"] == 0, module["module"])
        require(module.get("skipped", 0) == 0, module["module"])
        for field in ("stderr_sha256", "exit_sha256"):
            require(HEX64.match(module[field]), (module["module"], field))
            require(module[field] not in seen_logs, module["module"])
            seen_logs.add(module[field])
        ran += module["ran"]
    require(ran == 98, ran)
    require(muse1["totals"]["installed_ran"] == 98)
    raw_hashes = muse1["provenance"]["raw_file_sha256"]
    require(len(raw_hashes) >= 25, len(raw_hashes))
    for module in modules:
        require(module["stderr_sha256"] in raw_hashes.values(), module["module"])
        require(module["exit_sha256"] in raw_hashes.values(), module["module"])

    print("muse2: 24 blocks, 1440 measured, 48 warmups, all ok/cleanup true")
    print("muse2: 24 pooled groups x 60 match embedded summary + byte medians; "
          "4 exact doc rows keyed by cell match")
    print("muse1: 180 live rows (every row ok, tasks/cleanup true) + 4 warmups; "
          "11 modules, 98 ran, 0 failed, log hashes present")
    check_r4(r4_path, doc_path)
    check_r5(r5_path)
    check_r5_a11y(a11y_path)
    check_r5_paint(paint_path)
    print("OK: public evidence recomputed")


def paired_ci95(diffs, seed=0):
    import random
    rng = random.Random(seed)
    draws = sorted(median_p95(rng.choices(diffs, k=len(diffs)))[0]
                   for _ in range(10000))
    return [draws[250], draws[9750]]


def png_bytes(row):
    if "png_before" in row:
        return row["png_before"]["png_bytes"] + row["png_after"]["png_bytes"]
    if row.get("png_bytes") is None:
        return None
    return row["png_bytes"] + (row.get("after_png_bytes") or 0)


def byte_summary(rows):
    js = [r["result_bytes"] for r in rows]
    png = [png_bytes(r) for r in rows]
    require(all(x is None for x in png) or all(type(x) is int and x > 0 for x in png))
    return {"json_total": sum(js), "json_median": statistics.median(js),
            "png_total": None if png[0] is None else sum(png),
            "png_median": None if png[0] is None else statistics.median(png)}


def check_r4(r4_path, doc_path):
    r4 = json.load(open(r4_path))
    require(r4["artifact"] == "r4_isolation_aggregate", r4_path)
    totals = r4["totals"]
    require(totals == {"desktop_measured": 360, "desktop_warmups": 0,
        "desktop_ok": 360, "cdp_normal_measured": 480,
        "cdp_normal_warmups": 48, "cdp_normal_ok": 480,
        "cdp_image_measured": 30, "cdp_image_warmups": 6,
        "cdp_image_ok": 30}, totals)
    dblocks = r4["desktop_blocks"]
    cblocks = r4["cdp_blocks"]
    require(len(dblocks) == 36 and len(cblocks) == 30, (len(dblocks), len(cblocks)))
    require(sum(b["n_measured"] for b in dblocks) == 360)
    require(sum(b["n_warmup"] for b in dblocks) == 0)
    norm = [b for b in cblocks if b["workload"] != "IMG"]
    img = [b for b in cblocks if b["workload"] == "IMG"]
    require(len(norm) == 24 and len(img) == 6)
    require(sum(b["n_measured"] for b in norm) == 480)
    require(sum(b["n_warmup"] for b in norm) == 48)
    require(sum(b["n_measured"] for b in img) == 30)
    require(sum(b["n_warmup"] for b in img) == 6)

    seen_files, seen_slots = set(), set()
    manifest = r4["provenance"]["raw_file_sha256"]
    for b in dblocks + cblocks:
        check_samples_hash(b)
        require(b["file"] not in seen_files, b["file"])
        seen_files.add(b["file"])
        require(HEX64.match(b["sha256"]), b["file"])
        require(manifest[b["file"]] == b["sha256"], b["file"])
        require(b["ok"] and b["sidecar_returncode"] == 0, b["file"])
    require(len(manifest) == 66, len(manifest))

    dcells = {("exp1", "guard-crop-noafter-click"),
              ("exp2", "crop-after"), ("exp2", "crop-noafter")}
    for b in dblocks:
        require(tuple(b["cell"]) in dcells, b["cell"])
        require(b["variant"] in ("A", "B") and b["round"] in (1, 2, 3), b["file"])
        require(b["n_measured"] == 10 and b["n_warmup"] == 0, b["file"])
        require(b["tasks_ok"] and b["cleanup"] == {"children_reaped": True,
            "focus_preserved": True}, b["file"])
        require(HEX64.match(b["engine_sha256"]), b["file"])
        slot = (tuple(b["cell"]), b["round"], b["pos"])
        require(slot not in seen_slots, slot)
        seen_slots.add(slot)
        require(len(b["samples"]) == 10, b["file"])
        require(sorted(s["index"] for s in b["samples"]) == list(range(10)), b["file"])
        for s in b["samples"]:
            require(s["ok"] is True, b["file"])
            require(isinstance(s["whole_task_ms"], (int, float)), b["file"])
            require(isinstance(s["result_bytes"], int), b["file"])
            require(isinstance(s["png_bytes"], int), b["file"])
            require(isinstance(s["image_size"], list) and len(s["image_size"]) == 2, b["file"])
    # desktop schedule: R1 ABBA, R2 BAAB, R3 ABBA at pos 0..3
    sched = {1: "ABBA", 2: "BAAB", 3: "ABBA"}
    for cell in dcells:
        for rnd in (1, 2, 3):
            got = "".join(b["variant"] for b in sorted(
                (x for x in dblocks if tuple(x["cell"]) == cell and x["round"] == rnd),
                key=lambda x: x["pos"]))
            require(got == sched[rnd], (cell, rnd, got))

    for b in cblocks:
        require(b["variant"] in ("A", "B") and b["round"] in (1, 2, 3), b["file"])
        require(b["tasks_ok"] and b["cleanup_ok"], b["file"])
        for h in b["runtime_sha256"].values():
            require(HEX64.match(h), b["file"])
        modes = ["task-after-scoped"] if b["workload"] == "IMG" else ["task-scoped", "task-after-scoped"]
        require(b["modes"] == modes and b["delay_ms"] == 0, b["file"])
        require(set(b["runtime_sha256"]) == {"cu.py", "cdp.mjs", "browser_worker.py"})
        n = 5 if b["workload"] == "IMG" else 10
        require(len(b["samples"]) == n * len(modes) and len(b["warmup"]) == len(modes))
        for mode in modes:
            require(sorted(s["index"] for s in b["samples"] if s["mode"] == mode) == list(range(n)))
        require(sorted((s["mode"], s["index"]) for s in b["warmup"]) == sorted((m, -1) for m in modes))
        for s in b["samples"] + b["warmup"]:
            require(s["ok"] is True, b["file"])
            require(isinstance(s["whole_task_ms"], (int, float)), b["file"])
            require(isinstance(s["result_bytes"], int), b["file"])
            if b["workload"] == "IMG":
                require(s["png_present"] is True, b["file"])
                for side in ("png_before", "png_after"):
                    require(isinstance(s[side]["png_bytes"], int), b["file"])
                    require(isinstance(s[side]["width"], int), b["file"])
                    require(isinstance(s[side]["height"], int), b["file"])
            else:
                require(s["png_present"] is False and s["png_bytes"] is None, b["file"])
        if b["workload"] == "IMG":
            require(b["n_measured"] == 5 and b["n_warmup"] == 1, b["file"])
        else:
            require(b["n_measured"] == 20 and b["n_warmup"] == 2, b["file"])
            require(b["cell_family"] == "cdp" and b["workload"] in ("C0", "C1000"), b["file"])
    for cell, rnd in ((c, r) for c in ("C0", "C1000") for r in (1, 2, 3)):
        got = "".join(b["variant"] for b in sorted(
            (x for x in norm if x["workload"] == cell and x["round"] == rnd),
            key=lambda x: x["pos"]))
        require(got == sched[rnd], (cell, rnd, got))

    for b in dblocks + cblocks:
        for row in b["samples"] + b.get("warmup", []):
            require(type(row["whole_task_ms"]) in (int, float) and math.isfinite(row["whole_task_ms"]) and row["whole_task_ms"] >= 0)
            require(type(row["result_bytes"]) is int and row["result_bytes"] > 0)
    for rnd, order in ((1, "AB"), (2, "BA"), (3, "AB")):
        require("".join(b["variant"] for b in sorted((b for b in img if b["round"] == rnd), key=lambda b:b["pos"])) == order)

    def key_of(group, b, s):
        if group == "desktop":
            return tuple(b["cell"])
        if b["workload"] == "IMG":
            return ("cdp", "IMG", s["mode"])
        return ("cdp", b["workload"], s["mode"])

    def check_group(blocks, group, expect_pairs):
        pooled = {}
        for b in blocks:
            for s in b["samples"]:
                pooled.setdefault((key_of(group, b, s), b["variant"]), []).append(s)
        cells = sorted(set(c for c, _ in pooled))
        summary = r4["summary"][group]
        require(len(summary) == len(cells), (group, len(summary)))
        seen = set()
        for entry in summary:
            cell = tuple(entry["cell"])
            require(cell in cells and cell not in seen, cell)
            seen.add(cell)
            variants = entry["variants"]
            require(set(variants) == {"A", "B"}, cell)
            for var in ("A", "B"):
                whole = [s["whole_task_ms"] for s in pooled[(cell, var)]]
                require(variants[var]["n"] == len(whole), (cell, var))
                med, p95 = median_p95(whole)
                require(abs(variants[var]["whole_median"] - med) < 1e-9, (cell, var))
                require(abs(variants[var]["whole_p95"] - p95) < 1e-9, (cell, var))
                js = sorted(s["result_bytes"] for s in pooled[(cell, var)])
                require(abs(variants[var]["json_median"] - statistics.median(js)) < 1e-9, cell)
                require(variants[var]["json_p95"] == median_p95(js)[1], cell)
                png = [png_bytes(s) for s in pooled[(cell, var)]]
                expected_png = (None, None) if png[0] is None else median_p95(png)
                require((variants[var]["png_median"], variants[var]["png_p95"]) == expected_png, cell)
            rounds = entry["rounds"]
            require([r["round"] for r in rounds] == [1, 2, 3], cell)
            diffs = []
            for r in rounds:
                bs = sorted((b for b in blocks
                             if any(key_of(group, b, s) == cell for s in b["samples"])
                             and b["round"] == r["round"]),
                            key=lambda b: b["pos"])
                require(len(bs) in (2, 4), (cell, r["round"]))
                for i in range(0, len(bs), 2):
                    pair = (bs[i], bs[i + 1])
                    a = next(x for x in pair if x["variant"] == "A")
                    bb = next(x for x in pair if x["variant"] == "B")
                    ma = statistics.median(s["whole_task_ms"] for s in a["samples"]
                                           if key_of(group, a, s) == cell)
                    mb = statistics.median(s["whole_task_ms"] for s in bb["samples"]
                                           if key_of(group, bb, s) == cell)
                    diffs.append(ma - mb)
                av = [s["whole_task_ms"] for b in bs if b["variant"] == "A"
                      for s in b["samples"] if key_of(group, b, s) == cell]
                bv = [s["whole_task_ms"] for b in bs if b["variant"] == "B"
                      for s in b["samples"] if key_of(group, b, s) == cell]
                am, ap = median_p95(av)
                bm, bp = median_p95(bv)
                require(abs(r["A_median"] - am) < 1e-9, (cell, r["round"]))
                require(abs(r["B_median"] - bm) < 1e-9, (cell, r["round"]))
                require(abs(r["gain_ms"] - (am - bm)) < 1e-9, (cell, r["round"]))
                require(abs(r["A_p95"] - ap) < 1e-9 and abs(r["B_p95"] - bp) < 1e-9, cell)
                require(abs(r["p95_regression_percent"] - 100 * (bp / ap - 1)) < 1e-9, cell)
                want_bytes = {v: byte_summary([s for b in bs if b["variant"] == v for s in b["samples"] if key_of(group, b, s) == cell]) for v in ("A", "B")}
                require(r["bytes"] == want_bytes, cell)
            require(len(diffs) == expect_pairs, (cell, len(diffs)))
            require(entry["seed"] == 0, cell)
            bounds = paired_ci95(diffs)
            require(all(abs(a - b) < 1e-9 for a, b in
                       zip(entry["block_ci95_ms"], bounds)), cell)
            require(all(abs(a - b) < 1e-9 for a, b in
                       zip(entry["paired_block_differences_ms"], diffs)), cell)
            gate = entry["gate"]
            if group == "cdp_image":
                require(gate == {"applies": False, "pass": None}, cell)
            else:
                gain = variants["A"]["whole_median"] - variants["B"]["whole_median"]
                pct = 100 * gain / variants["A"]["whole_median"]
                want = (all(rr["gain_ms"] > 0 and rr["p95_regression_percent"] <= 5
                            for rr in rounds)
                        and entry["block_ci95_ms"][0] > 0
                        and variants["B"]["whole_p95"] <= variants["A"]["whole_p95"] * 1.05)
                if group == "cdp_normal":
                    want = want and gain >= 1 and pct >= 3
                require(gate == {"applies": True, "pass": bool(want)}, cell)
                require(abs(entry["gain_ms"] - gain) < 1e-9, cell)
        return cells

    dc = check_group(dblocks, "desktop", 6)
    nc = check_group(norm, "cdp_normal", 6)
    ic = check_group(img, "cdp_image", 3)
    require(len(dc) == 3 and len(nc) == 4 and len(ic) == 1, (dc, nc, ic))

    doc = open(doc_path).read()
    require("R4 FINAL" in doc, "R4 final section missing")
    for token in ("guard-crop-noafter-click", "crop-after", "crop-noafter",
                  "C0", "C1000", "image cell", "NOT LANDED"):
        require(token in doc, token)

    print("r4: 66 blocks, 870 measured +54 warmups; row/round times, PNG/JSON bytes and gates recomputed")



def check_r5(path):
    data = json.load(open(path))
    require(data["artifact"] == "r5_cdp_aggregate", "R5 artifact")
    require(data["totals"] == {"blocks_per_comparison": 24, "comparisons": 2, "measured_per_comparison": 480, "measured_total": 960, "warmups_per_comparison": 48, "warmups_total": 96}, "R5 totals")
    sources = data["sources"]
    require(set(sources) == {"before", "shipped-r4", "final-r5"}, "R5 source set")
    runtime_files = {"cu.py", "browser_worker.py", "cdp.mjs"}
    repo = Path(__file__).resolve().parents[1]
    for source in sources.values():
        commit = source["source_git_commit"]
        require(isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{40}", commit), "R5 source commit format")
        require(set(source["runtime_sha256"]) == runtime_files, "R5 runtime file set")
        for name in sorted(runtime_files):
            declared = source["runtime_sha256"][name]
            require(isinstance(declared, str) and HEX64.fullmatch(declared), "R5 source hash format")
            # Fixed file allowlist and full hex object ID; never shell or remote Git.
            blob = subprocess.run(["git", "show", commit + ":scripts/" + name],
                                  cwd=repo, capture_output=True, timeout=10)
            require(blob.returncode == 0, "R5 source commit/blob unavailable")
            require(hashlib.sha256(blob.stdout).hexdigest() == declared, "R5 source Git hash mismatch")
    comparisons = data["comparisons"]
    require(len(comparisons) == 2 and {c["name"] for c in comparisons} == {"shipped-r4", "final-r5"}, "R5 comparison set")
    modes = {"task-scoped", "task-after-scoped"}
    schedule = {1: "ABBA", 2: "BAAB", 3: "ABBA"}
    for comparison in comparisons:
        seen_files = set()
        blocks = comparison["blocks"]
        require(len(blocks) == 24, "R5 block count")
        slots = set()
        for block in blocks:
            check_samples_hash(block)
            require(block["file"] not in seen_files, "R5 duplicate raw file")
            seen_files.add(block["file"])
            require(isinstance(block["raw_sha256"], str) and HEX64.fullmatch(block["raw_sha256"]), "R5 raw hash")
            rnd, controls, pos, variant = (block[k] for k in ("round", "controls", "position", "variant"))
            require(type(rnd) is int and rnd in schedule and type(controls) is int and controls in (0, 1000) and type(pos) is int and 1 <= pos <= 4, "R5 block slot")
            require(variant == schedule[rnd][pos - 1], "R5 schedule")
            require((rnd, controls, pos) not in slots, "R5 duplicate block slot")
            slots.add((rnd, controls, pos))
            source = "before" if variant == "A" else comparison["name"]
            require(block["source"] == source and block["runtime_sha256"] == sources[source]["runtime_sha256"], "R5 block/source hash mismatch")
            require(block["ok"] is True and block["cleanup"] == {"cleanup_ok": True, "tasks_ok": True, "cleanup_errors": []}, "R5 block correctness/cleanup")
            require(len(block["samples"]) == 20 and len(block["warmup"]) == 2, "R5 row count")
            require(sorted((r["mode"], r["index"]) for r in block["samples"]) == sorted((m, i) for m in modes for i in range(10)), "R5 measured row slots")
            require(sorted((r["mode"], r["index"]) for r in block["warmup"]) == sorted((m, -1) for m in modes), "R5 warmup slots")
            for row in block["samples"] + block["warmup"]:
                require(row["ok"] is True and row["calls"] == 2, "R5 task correctness/calls")
                require(type(row["whole_task_ms"]) in (int, float) and math.isfinite(row["whole_task_ms"]) and row["whole_task_ms"] > 0, "R5 task time")
                require(type(row["result_bytes"]) is int and row["result_bytes"] > 0, "R5 JSON bytes")
                require(png_bytes(row) is None, "R5 unmeasured PNG must be absent/null")
        summary = comparison["summary"]
        require(len(summary) == 4, "R5 summary cell count")
        seen_cells = set()
        for entry in summary:
            cell = (entry["controls"], entry["mode"])
            require(cell in {(c, m) for c in (0, 1000) for m in modes} and cell not in seen_cells, "R5 summary cell")
            seen_cells.add(cell)
            selected = [b for b in blocks if b["controls"] == cell[0]]
            def rows(bs, variant):
                return [r for b in bs if b["variant"] == variant for r in b["samples"] if r["mode"] == cell[1]]
            stats = {}
            for variant in ("A", "B"):
                rs = rows(selected, variant)
                med, p95 = median_p95([r["whole_task_ms"] for r in rs])
                stats[variant] = {"whole_median": med, "whole_p95": p95, "json_median": statistics.median(r["result_bytes"] for r in rs)}
                require(entry[variant]["n"] == len(rs) == 60, "R5 pooled row count")
                require(all(abs(entry[variant][k] - value) < 1e-9 for k, value in stats[variant].items()), "R5 pooled summary mismatch")
            gain = stats["A"]["whole_median"] - stats["B"]["whole_median"]
            percent = 100 * gain / stats["A"]["whole_median"]
            require(abs(entry["gain_ms"] - gain) < 1e-9 and abs(entry["gain_percent"] - percent) < 1e-9, "R5 gain mismatch")
            require([r["round"] for r in entry["rounds"]] == [1, 2, 3], "R5 summary rounds")
            diffs = []
            round_gate = True
            for rr in entry["rounds"]:
                bs = sorted((b for b in selected if b["round"] == rr["round"]), key=lambda b: b["position"])
                for offset in (0, 2):
                    pair = bs[offset:offset + 2]
                    diffs.append(statistics.median(r["whole_task_ms"] for r in rows(pair, "A")) - statistics.median(r["whole_task_ms"] for r in rows(pair, "B")))
                am, ap = median_p95([r["whole_task_ms"] for r in rows(bs, "A")])
                bm, bp = median_p95([r["whole_task_ms"] for r in rows(bs, "B")])
                expected = {"A_median": am, "B_median": bm, "A_p95": ap, "B_p95": bp, "gain_ms": am - bm, "p95_regression_percent": 100 * (bp / ap - 1)}
                require(all(abs(rr[k] - v) < 1e-9 for k, v in expected.items()), "R5 per-round summary mismatch")
                require(rr["bytes"] == {v: byte_summary(rows(bs, v)) for v in ("A", "B")}, "R5 per-round byte summary mismatch")
                round_gate = round_gate and am > bm and bp <= ap * 1.05
            bounds = paired_ci95(diffs)
            require(entry["paired_block_differences_ms"] == diffs and entry["block_ci95_ms"] == bounds, "R5 seeded block CI mismatch")
            gate = gain >= 1 and percent >= 3 and round_gate and bounds[0] > 0 and stats["B"]["whole_p95"] <= stats["A"]["whole_p95"] * 1.05
            require(type(entry["gate_pass"]) is bool and entry["gate_pass"] == gate, "R5 gate mismatch")
    print("r5: Git-verified sources; 2 comparisons x24 blocks, 960 measured +96 warmups; times/bytes/CI/gates recomputed")


def metric_summary(rows, fields):
    result = {}
    for field in fields:
        values = [r[field] for r in rows]
        require(all(type(v) in (int, float) and math.isfinite(v) and v >= 0
                    for v in values), "invalid metric: " + field)
        med, p95 = median_p95(values)
        result[field] = {"median": med, "p95": p95, "total": sum(values)}
    return result


def check_r5_a11y(path):
    data = json.load(open(path))
    require(data["artifact"] == "r5_a11y_aggregate", "R5 a11y artifact")
    require(data["totals"] == {"blocks": 6, "measured": 30, "ok": 30, "warmups": 0}, "R5 a11y totals")
    blocks = data["blocks"]
    require(len(blocks) == 6, "R5 a11y block count")
    slots, files = set(), set()
    pooled = {route: [] for route in ("screenshot", "semantic")}
    fields = ("whole_task_ms", "json_bytes", "png_bytes", "png_count", "calls", "drill_calls")
    for b in blocks:
        check_samples_hash(b)
        slot = (b["round"], b["route"])
        require(slot in {(r, route) for r in (1, 2, 3) for route in pooled} and slot not in slots, "R5 a11y block slot")
        slots.add(slot)
        require(b["file"] not in files, "R5 a11y duplicate file")
        files.add(b["file"])
        require(HEX64.fullmatch(b["raw_sha256"]) and b["engine_sha256"] == data["engine_sha256"] and HEX64.fullmatch(b["engine_sha256"]), "R5 a11y hashes")
        require(b["ok"] is True and b["tasks_ok"] is True and b["sidecar_returncode"] == 0 and b["cleanup"] == {"children_reaped": True, "focus_preserved": True}, "R5 a11y cleanup/correctness")
        rows = b["samples"]
        require(len(rows) == 5 and [s["index"] for s in rows] == list(range(5)) and not b.get("warmup"), "R5 a11y rows/warmups")
        for row in rows:
            require(row["ok"] is True and row["pid_ok"] is True and row["clicks"] == 1 and type(row["whole_task_ms"]) in (int, float) and row["whole_task_ms"] > 0, "R5 a11y row correctness")
            require(all(type(row[k]) is int and row[k] >= 0 for k in fields[1:]) and row["json_bytes"] > 0, "R5 a11y bytes/counts")
            if b["route"] == "semantic":
                require(row["calls"] == 4 and row["drill_calls"] == 2 and row["redrill"] is True and 0 < row["skeleton_elements"] <= 80 and row["png_count"] == row["png_bytes"] == 0, "R5 a11y semantic correctness")
            else:
                require(row["calls"] == 2 and row["drill_calls"] == 0 and row["png_count"] == 2 and row["png_bytes"] > 0, "R5 a11y screenshot correctness")
        metrics = metric_summary(rows, fields)
        require((b["whole_median_ms"], b["whole_p95_ms"]) == (metrics["whole_task_ms"]["median"], metrics["whole_task_ms"]["p95"]), "R5 a11y block timing summary")
        require(b["json_bytes_median"] == metrics["json_bytes"]["median"] and b["png_bytes_total"] == metrics["png_bytes"]["total"], "R5 a11y block byte summary")
        pooled[b["route"]].extend(rows)
    expected = {route: {"n": len(rows), **metric_summary(rows, fields)} for route, rows in pooled.items()}
    require(all(len(rows) == 15 for rows in pooled.values()) and data["pooled_by_route"] == expected, "R5 a11y pooled summary")
    shot, sem = expected["screenshot"], expected["semantic"]
    require(sem["json_bytes"]["median"] > shot["json_bytes"]["median"], "R5 a11y semantic JSON increases")
    gain = shot["whole_task_ms"]["median"] - sem["whole_task_ms"]["median"]
    require(data["comparison"] == {"cpu": "UNVERIFIED - unmeasured", "median_json_wire_bytes_increase": sem["json_bytes"]["median"] - shot["json_bytes"]["median"], "median_png_bytes_saved": shot["png_bytes"]["median"] - sem["png_bytes"]["median"], "png_captures_skipped": shot["png_count"]["total"] - sem["png_count"]["total"], "semantic_tasks": 15, "semantic_vs_screenshot_median_gain_pct": 100 * gain / shot["whole_task_ms"]["median"], "semantic_vs_screenshot_median_ms_saved": gain}, "R5 a11y comparison summary")
    failed = data["failed_attempt01"]
    require(failed["ok"] is False and failed["n_samples"] == 1 and failed["sample0"]["ok"] is False and failed["sample0"]["png_count"] == 0 and HEX64.fullmatch(failed["raw_sha256"]), "R5 a11y retained failed attempt")
    print("r5 a11y: 6 blocks, 30 measured, no warmups; correctness/times/PNG/JSON summaries recomputed")


def png_rgb_at(blob, xy):
    """Decode the retained non-interlaced 8-bit RGB PNGs using stdlib only."""
    require(blob[:8] == b"\x89PNG\r\n\x1a\n", "PNG signature")
    offset, compressed, header = 8, bytearray(), None
    while offset < len(blob):
        require(offset + 12 <= len(blob), "PNG chunk truncated")
        size = struct.unpack(">I", blob[offset:offset + 4])[0]
        kind = blob[offset + 4:offset + 8]
        payload = blob[offset + 8:offset + 8 + size]
        require(offset + size + 12 <= len(blob), "PNG chunk length")
        crc = struct.unpack(">I", blob[offset + size + 8:offset + size + 12])[0]
        require(zlib.crc32(kind + payload) == crc, "PNG chunk CRC")
        if kind == b"IHDR":
            header = struct.unpack(">IIBBBBB", payload)
        elif kind == b"IDAT":
            compressed.extend(payload)
        elif kind == b"IEND":
            break
        offset += size + 12
    require(header is not None, "PNG header missing")
    width, height, depth, color, compression, filtering, interlace = header
    require((depth, color, compression, filtering, interlace) == (8, 2, 0, 0, 0) and 0 < width <= 4096 and 0 < height <= 4096, "PNG format/size")
    x, y = xy
    require(type(x) is int and type(y) is int and 0 <= x < width and 0 <= y < height, "PNG pixel position")
    stride = width * 3
    decoder = zlib.decompressobj()
    raw = decoder.decompress(compressed, (stride + 1) * height + 1)
    require(decoder.eof and not decoder.unused_data and len(raw) == (stride + 1) * height, "PNG decompressed size")
    previous = bytearray(stride)
    for row_index in range(y + 1):
        start = row_index * (stride + 1)
        mode = raw[start]
        require(mode in range(5), "PNG filter")
        row = bytearray(raw[start + 1:start + 1 + stride])
        for i in range(stride):
            a, b, c = (row[i - 3] if i >= 3 else 0), previous[i], (previous[i - 3] if i >= 3 else 0)
            if mode == 4:
                p = a + b - c
                distances = (abs(p - a), abs(p - b), abs(p - c))
                predictor = (a, b, c)[distances.index(min(distances))]
            else:
                predictor = (0, a, b, (a + b) // 2)[mode]
            row[i] = (row[i] + predictor) & 255
        previous = row
    return list(previous[x * 3:x * 3 + 3])


def check_r5_paint(path):
    data = json.load(open(path))
    require(data["artifact"] == "r5_paint_aggregate", "R5 paint artifact")
    require(data["totals"] == {"blocks": 6, "failed_rows": 1, "measured": 41, "planned": 144, "successful_blocks": 5, "successful_rows": 40}, "R5 paint totals (planned is not measured)")
    blocks = data["blocks"]
    require(len(blocks) == 6, "R5 paint block count")
    fields = ("whole_task_ms", "response_ms", "total_ms", "validation_probe_ms", "core_png_bytes", "core_request_json_bytes", "core_reply_json_bytes", "probe_png_bytes", "probe_request_json_bytes", "probe_reply_json_bytes")
    slots, files, expected, failures = set(), set(), [], []
    for b in blocks:
        check_samples_hash(b)
        slot = (b["sleep_ms"], b["delay_ms"])
        require(slot in {(s, d) for s in (80, 40) for d in (0, 30, 60)} and slot not in slots and b["round"] == 1 and b["arm"] == "cand-%dms" % slot[0], "R5 paint block slot")
        slots.add(slot)
        require(b["file"] not in files and HEX64.fullmatch(b["raw_sha256"]) and HEX64.fullmatch(b["engine_sha256"]) and b["engine_sha256"] == b["source_cu_sha256"], "R5 paint file/hashes")
        files.add(b["file"])
        require(b["cleanup"] == {"children_reaped": True, "focus_preserved": True} and not b.get("warmup"), "R5 paint cleanup/warmups")
        failed = slot == (40, 60)
        count = 1 if failed else 8
        rows = b["samples"]
        require(len(rows) == b["n_measured"] == count and b["ok"] is (not failed) and b["ok_count"] == (0 if failed else count) and [r["index"] for r in rows] == list(range(count)), "R5 paint row count/status")
        for r in rows:
            require(r["ok"] is (not failed) and r["after_png_correct"] is (not failed) and r["click_count"] == r["core_tool_completed"] == 1, "R5 paint row correctness")
            require(r["before_rgb"] == [251, 0, 0] and r["reference_rgb"] == [0, 251, 0] and r["after_rgb"] == ([251, 0, 0] if failed else [0, 251, 0]), "R5 paint pixel correctness")
            require(r["failure"] == ("pilot gate: after PNG not proven correct" if failed else None), "R5 paint failure retained")
            require(all(type(r[k]) is int and r[k] > 0 for k in fields[4:]), "R5 paint separate core/probe bytes")
            require(0 < r["response_ms"] <= r["total_ms"] <= r["whole_task_ms"] and r["validation_probe_ms"] > 0, "R5 paint separate core/probe timers")
        expected.append({"arm": b["arm"], "delay_ms": b["delay_ms"], "n": count, **metric_summary(rows, fields)})
        if failed:
            failures.extend(rows)
    require(data["summary"] == expected, "R5 paint timing/byte summary")
    require(len(failures) == 1, "R5 paint failed rows")
    require(data["outcome"] == {"delay60_sleep40": "0/1 gate failure: after RGB red [251,0,0] vs late reference green [0,251,0]; click_count 1, core_tool_completed 1; no performance claim from failed candidate", "delay60_sleep80": "8/8 green (correctness pass, no performance success claim from this pilot alone)", "sleep80_retained": True}, "R5 paint outcome summary")
    images = data["failure_images"]
    require(set(images) == {"before", "after", "reference"}, "R5 paint failure image set")
    for name, image in images.items():
        require(image["file"] == "r5_paint_images/" + name + ".png", "R5 paint image path")
        # Public retained PNGs are anchored to this repository, even for /tmp aggregates.
        blob = (Path(__file__).resolve().parents[1] / "docs/benchmarks" / image["file"]).read_bytes()
        require(len(blob) == image["png_bytes"] and hashlib.sha256(blob).hexdigest() == image["sha256"], "R5 paint failure PNG bytes/hash")
        require(png_rgb_at(blob, image["pixel_xy"]) == image["rgb"] == failures[0][name + "_rgb"], "R5 paint failure PNG pixel")
    require(images["before"]["png_bytes"] + images["after"]["png_bytes"] == failures[0]["core_png_bytes"] and images["reference"]["png_bytes"] == failures[0]["probe_png_bytes"], "R5 paint failure image byte accounting")
    print("r5 paint: 41 measured (40 pass, 1 failure), planned 144 stopped; core/probe times/bytes separate; PNG hashes/pixels verified")


if __name__ == "__main__":
    args = sys.argv[1:]
    base = args[0] if len(args) > 0 else "docs/benchmarks/muse2_assertion_poll_aggregate.json"
    hist = args[1] if len(args) > 1 else "docs/benchmarks/muse1_historical_aggregate.json"
    doc = args[2] if len(args) > 2 else "docs/optimization-experiments.md"
    r4_path = args[3] if len(args) > 3 else "docs/benchmarks/r4_isolation_aggregate.json"
    r5_path = args[4] if len(args) > 4 else "docs/benchmarks/r5_cdp_aggregate.json"
    a11y_path = args[5] if len(args) > 5 else "docs/benchmarks/r5_a11y_aggregate.json"
    paint_path = args[6] if len(args) > 6 else "docs/benchmarks/r5_paint_aggregate.json"
    require(len(args) <= 7, "at most seven evidence paths")
    main(base, hist, doc, r4_path, r5_path, a11y_path, paint_path)
