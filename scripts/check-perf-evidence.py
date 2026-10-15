"""Recompute published benchmark evidence from the sanitized aggregates.

Checks the MUSE2 aggregate (24 blocks, 1440 measured rows, 48 warmups),
all 12 workload cells x both variants (medians/p95 + byte medians), the
embedded summary, the exact doc table rows keyed by cell, the MUSE1
historical aggregate (180 live rows + 4 warmups verified per-row with
tasks/cleanup, 11 unit modules totalling 98 with sanitized log hashes),
and the R4 isolation aggregate (66 blocks: 360 desktop + 0 warmup,
480 + 48 CDP normal, 30 + 6 CDP image; recomputed summaries, per-round
gains, seeded paired-block CI and fixed gates; 4 mutation probes).

Stdlib only. No subprocess, no eval, no network. Bounded output.
"""
import json
import math
import re
import statistics
import sys


def median_p95(vals):
    assert len(vals) > 0
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


def main(muse2_path, muse1_path, doc_path, r4_path):
    # Tiny stdlib self-check of the helpers used below.
    assert statistics.median([1, 2, 3]) == 2
    assert median_p95([1, 2, 3, 4, 5]) == (3, 5)
    assert DOC_ROW.match(
        "| 0 | 0 | task-scoped | 63.742 / 67.811 | 30.502 / 32.577 |"
        " 52.15% (33.240 ms) | 381 \u2192 381 |"
    ), "row regex self-check"

    muse2 = json.load(open(muse2_path))
    blocks = muse2["blocks"]
    assert len(blocks) == 24, len(blocks)
    totals = muse2["totals"]
    measured = sum(b["n_measured"] for b in blocks)
    warmups = sum(b["n_warmup"] for b in blocks)
    ok = sum(b["n_ok"] for b in blocks)
    assert (measured, warmups, ok) == (1440, 48, 1440), (measured, warmups, ok)
    assert totals == {"measured": 1440, "warmups": 48, "ok": 1440}, totals
    rows = 0
    for block in blocks:
        assert block["n_measured"] == 60 and block["n_ok"] == 60, block["file"]
        assert block["n_warmup"] == 2, block["file"]
        assert block["tasks_ok"] and block["cleanup_ok"], block["file"]
        assert block["variant"] in ("baseline", "candidate"), block["file"]
        assert len(block["samples"]) == 60, block["file"]
        assert isinstance(block["runtime_cdp_sha256"], str)
        assert HEX64.match(block["runtime_cdp_sha256"]), block["file"]
        rows += len(block["samples"])
        for sample in block["samples"]:
            assert sample["ok"] is True, block["file"]
            assert sample["mode"] in ("task-scoped", "task-after-scoped")
            assert isinstance(sample["whole_task_ms"], (int, float))
            assert isinstance(sample["total_ms"], (int, float))
            assert isinstance(sample["result_bytes"], int)
    assert rows == 1440, rows

    groups = {}
    byte_groups = {}
    for block in blocks:
        for sample in block["samples"]:
            key = (block["controls"], block["delay_ms"],
                   sample["mode"], block["variant"])
            groups.setdefault(key, []).append(sample["whole_task_ms"])
            byte_groups.setdefault(key, []).append(sample["result_bytes"])
    assert len(groups) == 24, len(groups)
    for key, vals in groups.items():
        assert len(vals) == 60, (key, len(vals))
    summary = {(s["controls"], s["delay_ms"], s["route"], s["variant"]): s
               for s in muse2["summary"]}
    assert len(summary) == 24, len(summary)
    for key, vals in sorted(groups.items()):
        med, p95 = median_p95(vals)
        cell = summary[key]
        assert cell["n"] == 60, key
        assert abs(cell["whole_task_ms_median"] - med) < 1e-9, key
        assert abs(cell["whole_task_ms_p95"] - p95) < 1e-9, key
        assert abs(cell["result_bytes_median"]
                   - statistics.median(sorted(byte_groups[key]))) < 1e-9, key

    doc = open(doc_path).read()
    doc_rows = {}
    for line in doc.splitlines():
        match = DOC_ROW.match(line.strip())
        if match:
            delay, controls, route = (int(match.group(1)),
                                      int(match.group(2)), match.group(3))
            doc_rows[(controls, delay, route)] = match.groups()
    assert len(doc_rows) == 4, len(doc_rows)
    for (controls, delay, route) in sorted(doc_rows):
        assert delay == 0, (controls, delay, route)
        base = summary[(controls, delay, route, "baseline")]
        cand = summary[(controls, delay, route, "candidate")]
        base_med, base_p95 = median_p95(groups[(controls, delay, route,
                                                "baseline")])
        cand_med, cand_p95 = median_p95(groups[(controls, delay, route,
                                                "candidate")])
        groups_match = doc_rows[(controls, delay, route)]
        assert groups_match[3] == fmt(base_med), (route, groups_match[3])
        assert groups_match[4] == fmt(base_p95), (route, groups_match[4])
        assert groups_match[5] == fmt(cand_med), (route, groups_match[5])
        assert groups_match[6] == fmt(cand_p95), (route, groups_match[6])
        red_pct = (base_med - cand_med) / base_med * 100
        red_ms = base_med - cand_med
        assert groups_match[7] == ("%.2f" % red_pct), (route, groups_match[7])
        assert groups_match[8] == fmt(red_ms), (route, groups_match[8])
        assert int(groups_match[9]) == int(base["result_bytes_median"]), route
        assert int(groups_match[10]) == int(cand["result_bytes_median"]), route

    muse1 = json.load(open(muse1_path))
    live = muse1["live"]
    browser = live["browser"]
    assert browser["tasks_ok"] and browser["cleanup_ok"], "browser cleanup"
    assert (browser["n_measured"], browser["n_warmup"],
            browser["n_ok"]) == (120, 4, 120), browser["n_measured"]
    for sample in browser["samples"]:
        assert sample["ok"] is True
        assert isinstance(sample["whole_task_ms"], (int, float))
        assert isinstance(sample["result_bytes"], int)
    for name in ("desktop_full", "desktop_crop"):
        group = live[name]
        assert group["tasks_ok"], name
        cleanup = group.get("cleanup", {})
        assert cleanup.get("children_reaped") is True, name
        assert (group["n_measured"], group["n_ok"]) == (30, 30), name
        for sample in group["samples"]:
            assert sample["ok"] is True, name
            assert isinstance(sample["whole_task_ms"], (int, float))
            assert isinstance(sample["result_bytes"], int)
    live_rows = (len(browser["samples"])
                 + len(live["desktop_full"]["samples"])
                 + len(live["desktop_crop"]["samples"]))
    assert (live_rows, browser["n_warmup"]) == (180, 4), live_rows
    assert muse1["totals"]["live_measured"] == 180
    assert muse1["totals"]["live_ok"] == 180
    modules = muse1["installed_unittests"]["modules"]
    assert len(modules) == 11, len(modules)
    ran = 0
    seen_logs = set()
    for module in modules:
        assert module["ok"] and module["exit_code"] == 0, module["module"]
        assert module["failed"] == 0, module["module"]
        assert module.get("skipped", 0) == 0, module["module"]
        for field in ("stderr_sha256", "exit_sha256"):
            assert HEX64.match(module[field]), (module["module"], field)
            assert module[field] not in seen_logs, module["module"]
            seen_logs.add(module[field])
        ran += module["ran"]
    assert ran == 98, ran
    assert muse1["totals"]["installed_ran"] == 98
    raw_hashes = muse1["provenance"]["raw_file_sha256"]
    assert len(raw_hashes) >= 25, len(raw_hashes)
    for module in modules:
        assert module["stderr_sha256"] in raw_hashes.values(), module["module"]
        assert module["exit_sha256"] in raw_hashes.values(), module["module"]

    print("muse2: 24 blocks, 1440 measured, 48 warmups, all ok/cleanup true")
    print("muse2: 24 pooled groups x 60 match embedded summary + byte medians; "
          "4 exact doc rows keyed by cell match")
    print("muse1: 180 live rows (every row ok, tasks/cleanup true) + 4 warmups; "
          "11 modules, 98 ran, 0 failed, log hashes present")
    check_r4(r4_path, doc_path)
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
    assert all(x is None for x in png) or all(type(x) is int and x > 0 for x in png)
    return {"json_total": sum(js), "json_median": statistics.median(js),
            "png_total": None if png[0] is None else sum(png),
            "png_median": None if png[0] is None else statistics.median(png)}


def check_r4(r4_path, doc_path):
    r4 = json.load(open(r4_path))
    assert r4["artifact"] == "r4_isolation_aggregate", r4_path
    totals = r4["totals"]
    assert totals == {"desktop_measured": 360, "desktop_warmups": 0,
        "desktop_ok": 360, "cdp_normal_measured": 480,
        "cdp_normal_warmups": 48, "cdp_normal_ok": 480,
        "cdp_image_measured": 30, "cdp_image_warmups": 6,
        "cdp_image_ok": 30}, totals
    dblocks = r4["desktop_blocks"]
    cblocks = r4["cdp_blocks"]
    assert len(dblocks) == 36 and len(cblocks) == 30, (len(dblocks), len(cblocks))
    assert sum(b["n_measured"] for b in dblocks) == 360
    assert sum(b["n_warmup"] for b in dblocks) == 0
    norm = [b for b in cblocks if b["workload"] != "IMG"]
    img = [b for b in cblocks if b["workload"] == "IMG"]
    assert len(norm) == 24 and len(img) == 6
    assert sum(b["n_measured"] for b in norm) == 480
    assert sum(b["n_warmup"] for b in norm) == 48
    assert sum(b["n_measured"] for b in img) == 30
    assert sum(b["n_warmup"] for b in img) == 6

    seen_files, seen_slots = set(), set()
    manifest = r4["provenance"]["raw_file_sha256"]
    for b in dblocks + cblocks:
        assert b["file"] not in seen_files, b["file"]
        seen_files.add(b["file"])
        assert HEX64.match(b["sha256"]), b["file"]
        assert manifest[b["file"]] == b["sha256"], b["file"]
        assert b["ok"] and b["sidecar_returncode"] == 0, b["file"]
    assert len(manifest) == 66, len(manifest)

    dcells = {("exp1", "guard-crop-noafter-click"),
              ("exp2", "crop-after"), ("exp2", "crop-noafter")}
    for b in dblocks:
        assert tuple(b["cell"]) in dcells, b["cell"]
        assert b["variant"] in ("A", "B") and b["round"] in (1, 2, 3), b["file"]
        assert b["n_measured"] == 10 and b["n_warmup"] == 0, b["file"]
        assert b["tasks_ok"] and b["cleanup"] == {"children_reaped": True,
            "focus_preserved": True}, b["file"]
        assert HEX64.match(b["engine_sha256"]), b["file"]
        slot = (tuple(b["cell"]), b["round"], b["pos"])
        assert slot not in seen_slots, slot
        seen_slots.add(slot)
        assert len(b["samples"]) == 10, b["file"]
        assert sorted(s["index"] for s in b["samples"]) == list(range(10)), b["file"]
        for s in b["samples"]:
            assert s["ok"] is True, b["file"]
            assert isinstance(s["whole_task_ms"], (int, float)), b["file"]
            assert isinstance(s["result_bytes"], int), b["file"]
            assert isinstance(s["png_bytes"], int), b["file"]
            assert isinstance(s["image_size"], list) and len(s["image_size"]) == 2, b["file"]
    # desktop schedule: R1 ABBA, R2 BAAB, R3 ABBA at pos 0..3
    sched = {1: "ABBA", 2: "BAAB", 3: "ABBA"}
    for cell in dcells:
        for rnd in (1, 2, 3):
            got = "".join(b["variant"] for b in sorted(
                (x for x in dblocks if tuple(x["cell"]) == cell and x["round"] == rnd),
                key=lambda x: x["pos"]))
            assert got == sched[rnd], (cell, rnd, got)

    for b in cblocks:
        assert b["variant"] in ("A", "B") and b["round"] in (1, 2, 3), b["file"]
        assert b["tasks_ok"] and b["cleanup_ok"], b["file"]
        for h in b["runtime_sha256"].values():
            assert HEX64.match(h), b["file"]
        modes = ["task-after-scoped"] if b["workload"] == "IMG" else ["task-scoped", "task-after-scoped"]
        assert b["modes"] == modes and b["delay_ms"] == 0, b["file"]
        assert set(b["runtime_sha256"]) == {"cu.py", "cdp.mjs", "browser_worker.py"}
        n = 5 if b["workload"] == "IMG" else 10
        assert len(b["samples"]) == n * len(modes) and len(b["warmup"]) == len(modes)
        for mode in modes:
            assert sorted(s["index"] for s in b["samples"] if s["mode"] == mode) == list(range(n))
        assert sorted((s["mode"], s["index"]) for s in b["warmup"]) == sorted((m, -1) for m in modes)
        for s in b["samples"] + b["warmup"]:
            assert s["ok"] is True, b["file"]
            assert isinstance(s["whole_task_ms"], (int, float)), b["file"]
            assert isinstance(s["result_bytes"], int), b["file"]
            if b["workload"] == "IMG":
                assert s["png_present"] is True, b["file"]
                for side in ("png_before", "png_after"):
                    assert isinstance(s[side]["png_bytes"], int), b["file"]
                    assert isinstance(s[side]["width"], int), b["file"]
                    assert isinstance(s[side]["height"], int), b["file"]
            else:
                assert s["png_present"] is False and s["png_bytes"] is None, b["file"]
        if b["workload"] == "IMG":
            assert b["n_measured"] == 5 and b["n_warmup"] == 1, b["file"]
        else:
            assert b["n_measured"] == 20 and b["n_warmup"] == 2, b["file"]
            assert b["cell_family"] == "cdp" and b["workload"] in ("C0", "C1000"), b["file"]
    for cell, rnd in ((c, r) for c in ("C0", "C1000") for r in (1, 2, 3)):
        got = "".join(b["variant"] for b in sorted(
            (x for x in norm if x["workload"] == cell and x["round"] == rnd),
            key=lambda x: x["pos"]))
        assert got == sched[rnd], (cell, rnd, got)

    for b in dblocks + cblocks:
        for row in b["samples"] + b.get("warmup", []):
            assert type(row["whole_task_ms"]) in (int, float) and math.isfinite(row["whole_task_ms"]) and row["whole_task_ms"] >= 0
            assert type(row["result_bytes"]) is int and row["result_bytes"] > 0
    for rnd, order in ((1, "AB"), (2, "BA"), (3, "AB")):
        assert "".join(b["variant"] for b in sorted((b for b in img if b["round"] == rnd), key=lambda b:b["pos"])) == order

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
        assert len(summary) == len(cells), (group, len(summary))
        seen = set()
        for entry in summary:
            cell = tuple(entry["cell"])
            assert cell in cells and cell not in seen, cell
            seen.add(cell)
            variants = entry["variants"]
            assert set(variants) == {"A", "B"}, cell
            for var in ("A", "B"):
                whole = [s["whole_task_ms"] for s in pooled[(cell, var)]]
                assert variants[var]["n"] == len(whole), (cell, var)
                med, p95 = median_p95(whole)
                assert abs(variants[var]["whole_median"] - med) < 1e-9, (cell, var)
                assert abs(variants[var]["whole_p95"] - p95) < 1e-9, (cell, var)
                js = sorted(s["result_bytes"] for s in pooled[(cell, var)])
                assert abs(variants[var]["json_median"] - statistics.median(js)) < 1e-9, cell
                assert variants[var]["json_p95"] == median_p95(js)[1], cell
                png = [png_bytes(s) for s in pooled[(cell, var)]]
                expected_png = (None, None) if png[0] is None else median_p95(png)
                assert (variants[var]["png_median"], variants[var]["png_p95"]) == expected_png, cell
            rounds = entry["rounds"]
            assert [r["round"] for r in rounds] == [1, 2, 3], cell
            diffs = []
            for r in rounds:
                bs = sorted((b for b in blocks
                             if any(key_of(group, b, s) == cell for s in b["samples"])
                             and b["round"] == r["round"]),
                            key=lambda b: b["pos"])
                assert len(bs) in (2, 4), (cell, r["round"])
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
                assert abs(r["A_median"] - am) < 1e-9, (cell, r["round"])
                assert abs(r["B_median"] - bm) < 1e-9, (cell, r["round"])
                assert abs(r["gain_ms"] - (am - bm)) < 1e-9, (cell, r["round"])
                assert abs(r["A_p95"] - ap) < 1e-9 and abs(r["B_p95"] - bp) < 1e-9, cell
                assert abs(r["p95_regression_percent"] - 100 * (bp / ap - 1)) < 1e-9, cell
                want_bytes = {v: byte_summary([s for b in bs if b["variant"] == v for s in b["samples"] if key_of(group, b, s) == cell]) for v in ("A", "B")}
                assert r["bytes"] == want_bytes, cell
            assert len(diffs) == expect_pairs, (cell, len(diffs))
            assert entry["seed"] == 0, cell
            bounds = paired_ci95(diffs)
            assert all(abs(a - b) < 1e-9 for a, b in
                       zip(entry["block_ci95_ms"], bounds)), cell
            assert all(abs(a - b) < 1e-9 for a, b in
                       zip(entry["paired_block_differences_ms"], diffs)), cell
            gate = entry["gate"]
            if group == "cdp_image":
                assert gate == {"applies": False, "pass": None}, cell
            else:
                gain = variants["A"]["whole_median"] - variants["B"]["whole_median"]
                pct = 100 * gain / variants["A"]["whole_median"]
                want = (all(rr["gain_ms"] > 0 and rr["p95_regression_percent"] <= 5
                            for rr in rounds)
                        and entry["block_ci95_ms"][0] > 0
                        and variants["B"]["whole_p95"] <= variants["A"]["whole_p95"] * 1.05)
                if group == "cdp_normal":
                    want = want and gain >= 1 and pct >= 3
                assert gate == {"applies": True, "pass": bool(want)}, cell
                assert abs(entry["gain_ms"] - gain) < 1e-9, cell
        return cells

    dc = check_group(dblocks, "desktop", 6)
    nc = check_group(norm, "cdp_normal", 6)
    ic = check_group(img, "cdp_image", 3)
    assert len(dc) == 3 and len(nc) == 4 and len(ic) == 1, (dc, nc, ic)

    doc = open(doc_path).read()
    assert "R4 FINAL" in doc, "R4 final section missing"
    for token in ("guard-crop-noafter-click", "crop-after", "crop-noafter",
                  "C0", "C1000", "image cell", "NOT LANDED"):
        assert token in doc, token

    print("r4: 66 blocks, 870 measured +54 warmups; row/round times, PNG/JSON bytes and gates recomputed")


if __name__ == "__main__":
    args = sys.argv[1:]
    base = args[0] if len(args) > 0 else "docs/benchmarks/muse2_assertion_poll_aggregate.json"
    hist = args[1] if len(args) > 1 else "docs/benchmarks/muse1_historical_aggregate.json"
    doc = args[2] if len(args) > 2 else "docs/optimization-experiments.md"
    r4_path = args[3] if len(args) > 3 else "docs/benchmarks/r4_isolation_aggregate.json"
    assert len(args) <= 4, args
    main(base, hist, doc, r4_path)
