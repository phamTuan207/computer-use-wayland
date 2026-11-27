#!/usr/bin/env python3
"""M7 stall and latency detector (flag only, never triggers anything).

Reads run activity signals and flags silence gaps for human judgement:
  - heartbeat log (JSONL, field "ts");
  - per-task reports (pipe lines starting with an ISO timestamp);
  - grades ledger (JSONL timestamps.task_end / recorded_at) for the
    post-run latency table;
  - git commits touching rung3-run-log/ (coordinator ledger activity).

A stall flag is a gap in the UNION of all activity timestamps longer
than the threshold. A single-signal gap (for example git silence while
the coordinator drives on the laptop and heartbeats continue) does not
flag. This corroboration rule is the M7 backtest condition: fire on
the 2026-11-27 stall window, stay silent across the 2026-11-25 window
the owner later corrected.

Exit code is always 0 when inputs parse; flags are printed, never
acted on. No personal info in this file.

Usage:
  python3 rung3-ci/stall-detector.py [--threshold-min 30]
      [--heartbeat FILE] [--reports FILE] [--grades FILE]
      [--repo DIR] [--no-git] [--json-out FILE]
Defaults point at the repo rung3-run-log files.
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys

ISO_HEAD = re.compile(r"^(\d{4}-\d\d-\d\dT[\d:.]+[+\-]\d\d:\d\d)\s*\|")


def parse_ts(text):
    try:
        return datetime.datetime.fromisoformat(text)
    except (TypeError, ValueError):
        return None


def heartbeat_times(path):
    out = []
    if not path or not os.path.exists(path):
        return out
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            ts = parse_ts(rec.get("ts"))
            if ts:
                out.append(ts)
    return out


def report_times(path):
    out = []
    if not path or not os.path.exists(path):
        return out
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = ISO_HEAD.match(line)
            if m:
                ts = parse_ts(m.group(1))
                if ts:
                    out.append(ts)
    return out


def grade_latencies(path):
    """Return (recorded_times, [(task_id, latency_minutes)])."""
    times, lat = [], []
    if not path or not os.path.exists(path):
        return times, lat
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if rec.get("test_row"):
                continue
            stamps = rec.get("timestamps") or {}
            end = parse_ts(stamps.get("task_end"))
            rec_at = parse_ts(stamps.get("recorded_at"))
            if rec_at:
                times.append(rec_at)
            if end and rec_at:
                lat.append((rec.get("task_id", "?"),
                            (rec_at - end).total_seconds() / 60.0))
    return times, lat


def git_ledger_times(repo):
    try:
        out = subprocess.run(
            ["git", "-C", repo, "log", "--all", "--format=%cI",
             "--", "rung3-run-log/"],
            capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired):
        return []
    times = []
    for line in out.stdout.splitlines():
        ts = parse_ts(line.strip())
        if ts:
            times.append(ts)
    return times


def gaps_over(times, threshold_min):
    ordered = sorted(times)
    found = []
    for i in range(1, len(ordered)):
        minutes = (ordered[i] - ordered[i - 1]).total_seconds() / 60.0
        if minutes > threshold_min:
            found.append((ordered[i - 1], ordered[i], minutes))
    return found


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logdir = os.path.join(root, "rung3-run-log")
    ap = argparse.ArgumentParser()
    ap.add_argument("--threshold-min", type=float, default=30.0)
    ap.add_argument("--heartbeat",
                    default=os.path.join(logdir, "r3-l3-heartbeat.log"))
    ap.add_argument("--reports",
                    default=os.path.join(logdir,
                                         "r3-l3-per-task-reports.log"))
    ap.add_argument("--grades",
                    default=os.path.join(logdir, "R3-L3-grades.jsonl"))
    ap.add_argument("--repo", default=root)
    ap.add_argument("--no-git", action="store_true")
    ap.add_argument("--since", default=None,
                    help="ISO timestamp; ignore activity before it")
    ap.add_argument("--until", default=None,
                    help="ISO timestamp; ignore activity after it")
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args()
    since = parse_ts(args.since) if args.since else None
    until = parse_ts(args.until) if args.until else None

    def in_window(times):
        return [t for t in times
                if (since is None or t >= since)
                and (until is None or t <= until)]

    beats = heartbeat_times(args.heartbeat)
    reports = report_times(args.reports)
    grade_times, latencies = grade_latencies(args.grades)
    ledger = [] if args.no_git else git_ledger_times(args.repo)

    signals = {"heartbeat": in_window(beats),
               "reports": in_window(reports),
               "grades": in_window(grade_times),
               "git_ledger": in_window(ledger)}
    beats, reports, grade_times, ledger = (
        signals["heartbeat"], signals["reports"], signals["grades"],
        signals["git_ledger"])
    union = sorted(set(beats + reports + grade_times + ledger))
    flags = gaps_over(union, args.threshold_min)

    result = {
        "threshold_min": args.threshold_min,
        "counts": {k: len(v) for k, v in signals.items()},
        "union_events": len(union),
        "flags": [{"start": a.isoformat(), "end": b.isoformat(),
                   "minutes": round(m, 1)} for a, b, m in flags],
        "per_signal_gaps": {
            k: len(gaps_over(v, args.threshold_min))
            for k, v in signals.items()},
        "latency": {
            "tasks": len(latencies),
            "total_min": round(sum(m for _, m in latencies), 1),
            "max_min": round(max((m for _, m in latencies), default=0), 1),
        },
    }
    print("signals: " + ", ".join(
        "%s=%d" % kv for kv in result["counts"].items()))
    print("union events: %d, threshold: %.0f min"
          % (len(union), args.threshold_min))
    print("per-signal gaps over threshold: " + ", ".join(
        "%s=%d" % kv for kv in result["per_signal_gaps"].items()))
    print("latency: %d tasks, total %.1f min, max %.1f min"
          % (result["latency"]["tasks"], result["latency"]["total_min"],
             result["latency"]["max_min"]))
    ict = datetime.timezone(datetime.timedelta(hours=7))
    if flags:
        print("STALL FLAGS (union silence, for human judgement):")
        for a, b, m in flags:
            print("  %.1f min  %s -> %s"
                  % (m, a.astimezone(ict).isoformat(),
                     b.astimezone(ict).isoformat()))
    else:
        print("no stall flags")
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
