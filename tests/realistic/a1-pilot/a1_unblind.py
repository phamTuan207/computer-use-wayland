#!/usr/bin/env python3
"""Unblind the A1 pilot and compute the verdict (run by Muse only).

Run ONLY after all 12 Stage 1 verdicts are committed. Verifies the
sealed manifest, joins run-id to arm, loads the sealed Stage 1 verdicts
and Stage 2 metrics, and evaluates the frozen GO bar (plan section 5).

A run counts as a pass only if Stage 1 says pass AND Stage 2 reports no
problems. Wall medians, pass rates, recovery totals, composition think,
the 2-of-3 rule, the dispersion rule, the flagged-run rule, the
robustness label, and the INCONCLUSIVE outcome are all computed here
from the sealed outputs, with no executor memory.

Flagged runs are detected from the metrics: session_deaths above 0 or
refusals above 0. Extra verification acts not in the runbook and broker
contention that does not surface as a refusal must be checked by Muse
from the logs before the verdict is finalized; this script prints a
reminder and accepts an optional --flags file mapping run-id to a
reason for such manual flags.

Usage:
  python3 a1_unblind.py --manifest /path/outside/repo/a1-manifest.jsonl \
    --runs /tmp/a1-pilot-20261121/runs \
    --stage1 <dir of <run-id>.json Stage 1 verdicts> \
    --stage2 <dir of <run-id>.json Stage 2 metrics> \
    [--flags flags.json]
Stdout prints the verdict table as JSON. Exit 0 only if the manifest
verifies and the verdict is GO or NO-GO; exit 2 on a manifest or
evidence failure; exit 3 on INCONCLUSIVE.
No em dash or en dash in this file.
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime


def median(values):
    s = sorted(values)
    return s[len(s) // 2]


def parse_ts(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_json(path):
    with open(path, "r") as h:
        return json.load(h)


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--runs", required=True)
    parser.add_argument("--stage1", required=True)
    parser.add_argument("--stage2", required=True)
    parser.add_argument("--flags", default=None,
                        help="optional JSON {run_id: reason} manual flags")
    args = parser.parse_args(argv)

    digest = hashlib.sha256(open(args.manifest, "rb").read()).hexdigest()
    print("manifest sha256 %s" % digest, file=sys.stderr)
    manifest = []
    with open(args.manifest, "r") as h:
        for number, raw in enumerate(h, start=1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                manifest.append(json.loads(raw))
            except json.JSONDecodeError:
                print("manifest line %d is not JSON" % number,
                      file=sys.stderr)
                return 2
    errors = []
    if len(manifest) != 12:
        errors.append("manifest has %d lines, expected 12" % len(manifest))
    seen_ids = set()
    for line in manifest:
        rid = line.get("run_id")
        if rid in seen_ids:
            errors.append("duplicate run_id %s" % rid)
        seen_ids.add(rid)
    for case in ("pick4", "f01"):
        for arm in ("STEP", "CODE"):
            nums = sorted(
                line.get("run_number") for line in manifest
                if line.get("case") == case and line.get("arm") == arm)
            if nums != [1, 2, 3]:
                errors.append(
                    "run numbers for %s %s are %s, expected [1, 2, 3]"
                    % (case, arm, nums))
    run_dirs = {
        d for d in os.listdir(args.runs)
        if os.path.isdir(os.path.join(args.runs, d))
    }
    if seen_ids != run_dirs:
        errors.append(
            "manifest run-ids do not match run dirs: only in manifest %s, "
            "only in runs %s"
            % (sorted(seen_ids - run_dirs), sorted(run_dirs - seen_ids)))
    if errors:
        for e in errors:
            print("manifest error: %s" % e, file=sys.stderr)
        return 2

    manual_flags = {}
    if args.flags:
        manual_flags = load_json(args.flags)

    # Load per-run evidence in manifest (run_sequence) order.
    ordered = sorted(manifest, key=lambda l: l.get("run_sequence", 0))
    prev_start = None
    runs = {}
    for line in ordered:
        rid = line["run_id"]
        s1 = load_json(os.path.join(args.stage1, rid + ".json"))
        s2 = load_json(os.path.join(args.stage2, rid + ".json"))
        log_path = os.path.join(args.runs, rid, "run-log.jsonl")
        start_ts = None
        with open(log_path, "r") as h:
            first = h.readline()
            if first.strip():
                start_ts = parse_ts(json.loads(first)["ts"])
        if prev_start is not None and start_ts is not None \
                and start_ts < prev_start:
            errors.append(
                "run_start ts goes backward at run %s" % rid)
        if start_ts is not None:
            prev_start = start_ts
        run_pass = bool(s1.get("pass")) and not s2.get("problems")
        flagged = (
            (s2.get("session_deaths") or 0) > 0
            or (s2.get("refusals") or 0) > 0
            or rid in manual_flags)
        runs[rid] = {
            "case": line["case"], "arm": line["arm"],
            "run_number": line["run_number"],
            "run_sequence": line["run_sequence"],
            "stage1_pass": bool(s1.get("pass")),
            "stage2_problems": s2.get("problems", []),
            "pass": run_pass,
            "wall_ms": s2.get("wall_ms"),
            "recovery_steps": s2.get("recovery_steps"),
            "misclicks": s2.get("misclicks"),
            "total_composition_think_ms": s2.get(
                "total_composition_think_ms"),
            "gap_ms": s2.get("gap_ms"),
            "run_end_reason": s2.get("run_end_reason"),
            "flagged": flagged,
            "flag_reason": manual_flags.get(rid, ""),
        }
    if errors:
        for e in errors:
            print("evidence error: %s" % e, file=sys.stderr)
        return 2

    def cell(case, arm):
        return [runs[l["run_id"]] for l in ordered
                if l["case"] == case and l["arm"] == arm]

    verdict = {"cases": {}, "overall": None, "notes": []}
    case_verdicts = {}
    for case in ("pick4", "f01"):
        code = cell(case, "CODE")
        step = cell(case, "STEP")
        c = {"code_runs": code, "step_runs": step}
        code_walls = [r["wall_ms"] for r in code]
        step_walls = [r["wall_ms"] for r in step]
        c["code_walls"] = code_walls
        c["step_walls"] = step_walls
        inconclusive = []
        if any(w == "UNMEASURED" or w is None for w in code_walls + step_walls):
            inconclusive.append("a gate wall is UNMEASURED")
        code_timeout_median = False
        step_timeout_median = False
        if all(isinstance(w, (int, float)) for w in code_walls):
            code_med = median(code_walls)
            code_timeout_median = any(
                r["wall_ms"] == code_med and r["run_end_reason"] == "timeout"
                for r in code)
        if all(isinstance(w, (int, float)) for w in step_walls):
            step_med = median(step_walls)
            step_timeout_median = any(
                r["wall_ms"] == step_med and r["run_end_reason"] == "timeout"
                for r in step)
        if code_timeout_median or step_timeout_median:
            inconclusive.append("an arm median is a timed-out run (lower bound)")
        # Dispersion per cell.
        for name, walls in (("CODE", code_walls), ("STEP", step_walls)):
            if all(isinstance(w, (int, float)) for w in walls):
                med = median(walls)
                disp = (max(walls) - min(walls)) / med if med else 0
                c["dispersion_%s" % name] = round(disp, 3)
                if disp > 0.5:
                    inconclusive.append(
                        "dispersion in %s cell is %s, above 0.5" % (name, round(disp, 3)))
        # Flagged runs per cell.
        for name, rs in (("CODE", code), ("STEP", step)):
            n_flag = sum(1 for r in rs if r["flagged"])
            c["flagged_%s" % name] = n_flag
            if n_flag >= 2:
                inconclusive.append(
                    "%d flagged runs in the %s cell" % (n_flag, name))
        code_pass = sum(1 for r in code if r["pass"])
        step_pass = sum(1 for r in step if r["pass"])
        code_rec = sum(r["recovery_steps"] or 0 for r in code)
        step_rec = sum(r["recovery_steps"] or 0 for r in step)
        c["pass_rate"] = {"CODE": code_pass, "STEP": step_pass}
        c["recovery_total"] = {"CODE": code_rec, "STEP": step_rec}
        # Composition think: CODE median total vs STEP median gap.
        code_thinks = [r["total_composition_think_ms"] for r in code
                       if isinstance(r["total_composition_think_ms"], (int, float))]
        step_gaps = [r["gap_ms"] for r in step
                     if isinstance(r["gap_ms"], (int, float))]
        if len(code_thinks) == 3 and len(step_gaps) == 3:
            code_think_med = median(code_thinks)
            step_gap_med = median(step_gaps)
            c["composition_think_median_CODE"] = code_think_med
            c["gap_median_STEP"] = step_gap_med
            c["think_condition"] = code_think_med < step_gap_med
            code_wall_med = median(code_walls)
            c["think_flag_50pct_wall"] = (
                code_think_med > 0.5 * code_wall_med)
        else:
            c["think_condition"] = None
            inconclusive.append(
                "composition think or STEP gap UNMEASURED on a run")
        # Robustness label (reporting, not a gate).
        if all(isinstance(w, (int, float)) for w in code_walls + step_walls):
            step_med = median(step_walls)
            robust = all(w <= step_med for w in code_walls)
            c["robustness"] = "PASS" if robust else "FAIL"
            c["code_median_wall"] = median(code_walls)
            c["step_median_wall"] = step_med
        else:
            c["robustness"] = "UNMEASURED"
        if inconclusive:
            c["verdict"] = "INCONCLUSIVE"
            c["inconclusive_reasons"] = inconclusive
            case_verdicts[case] = "INCONCLUSIVE"
            verdict["cases"][case] = c
            continue
        # Gated conditions.
        cond = {}
        if case == "f01":
            cond["wall_30pct"] = (
                median(code_walls) <= 0.70 * median(step_walls))
            below = sum(
                1 for w in code_walls
                if w <= 0.80 * median(step_walls))
            cond["two_of_three"] = below >= 2
            c["two_of_three_count"] = below
        cond["pass_rate"] = code_pass >= step_pass
        cond["recovery"] = code_rec <= step_rec
        cond["think"] = bool(c.get("think_condition"))
        c["conditions"] = cond
        c["verdict"] = "GO" if all(cond.values()) else "NO-GO"
        case_verdicts[case] = c["verdict"]
        verdict["cases"][case] = c

    if any(v == "INCONCLUSIVE" for v in case_verdicts.values()):
        verdict["overall"] = "INCONCLUSIVE"
    elif all(v == "GO" for v in case_verdicts.values()):
        verdict["overall"] = "GO"
    else:
        verdict["overall"] = "NO-GO"
    verdict["notes"].append(
        "Manual flag check: extra verification acts not in the runbook and "
        "broker contention that did not surface as a refusal must be "
        "checked by Muse from the logs before this verdict is finalized.")
    print(json.dumps(verdict, indent=2, sort_keys=True))
    if verdict["overall"] == "GO" or verdict["overall"] == "NO-GO":
        return 0
    return 3


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
