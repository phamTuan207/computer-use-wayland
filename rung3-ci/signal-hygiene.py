#!/usr/bin/env python3
"""R3-L3 signal hygiene verdicts (fix-review R1, 2026-11-27).

Pure decision logic for the timeout watch and the coordinator liveness
watch, so both watches follow one deterministic rule instead of prose
interpretation. No killing, no alerting, no writes: this script only
reads the state file, the per-task report log and the grades ledger
and prints a verdict the watch bodies act on.

Rules (redteam 1.1-1.2):
- A task counts as RUNNING only when the state file shows it current
  with task_start set and no drive-end recorded, AND no completion
  evidence exists: a per-task report row or a grade row for the task
  timestamped AFTER task_start. A row older than task_start (written
  early or backfilled) does not spare a hung task.
- Timeout action depends on runner identity: an OS PID lane is killed
  by exact PID; the Muse lane has a subagent session id and no OS
  PID, so its timeout action is "coordinator closes the subagent".
- Liveness: while a task is driving and still inside its 30-min
  deadline, a stale heartbeat alone does not fire the liveness alert
  (long drives legitimately go quiet). The reporting-chain trigger
  still requires both signals.

Usage:
  python3 rung3-ci/signal-hygiene.py timeout  [--state F] [--reports F] [--grades F] [--now ISO]
  python3 rung3-ci/signal-hygiene.py liveness [--state F] [--reports F] [--heartbeat F] [--now ISO]

Output: one JSON object with the verdict. Exit 0 always on a verdict;
exit 2 on unreadable inputs.
No personal info in this file.
"""
import argparse
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUNLOG = os.path.join(HERE, "..", "rung3-run-log")
TASK_LIMIT_MIN = 30
WARN_MIN = 15
HEARTBEAT_STALE_MIN = 15
REPORT_STALE_MIN = 30


def parse_ts(value):
    if not value:
        return None
    try:
        return datetime.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def now_default():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))


def task_id_of(state):
    raw = state.get("current_task") or ""
    m = re.search(r"(R3-\d+|DP-\d+)", str(raw))
    return m.group(1) if m else None


def completion_evidence(task_id, task_start, reports_text, grades_rows):
    """Return a short string naming the evidence, or None."""
    if not task_id:
        return None
    for line in (reports_text or "").splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 2 and parts[1] == task_id:
            ts = parse_ts(parts[0])
            if ts and task_start and ts > task_start:
                return "per-task report row at " + parts[0]
    for row in grades_rows or []:
        if row.get("task_id") == task_id and not row.get("test_row"):
            ts = parse_ts((row.get("timestamps") or {}).get("recorded_at"))
            if ts and task_start and ts > task_start:
                return "grade row recorded_at " + str(
                    (row.get("timestamps") or {}).get("recorded_at"))
    return None


def running_state(state, reports_text, grades_rows):
    """Return (is_running, task_id, task_start, reason)."""
    if (state.get("status") or "").upper().startswith("RUN NOT STARTED"):
        return False, None, None, "run not started"
    task_start = parse_ts(state.get("task_start"))
    task_id = task_id_of(state)
    if not task_start:
        return False, task_id, None, "no task_start (no drive recorded as running)"
    if state.get("drive_end") or state.get("task_end"):
        return False, task_id, task_start, "drive-end recorded in state"
    evidence = completion_evidence(task_id, task_start, reports_text, grades_rows)
    if evidence:
        return False, task_id, task_start, "completed: " + evidence
    return True, task_id, task_start, "running"


def timeout_verdict(state, reports_text, grades_rows, now):
    running, task_id, task_start, reason = running_state(
        state, reports_text, grades_rows)
    if not running:
        return {"verdict": "NOT_RUNNING", "task": task_id, "reason": reason}
    elapsed = (now - task_start).total_seconds() / 60.0
    pid = state.get("runner_pid")
    sess = state.get("claude_runner_session")
    out = {"task": task_id, "elapsed_min": round(elapsed, 1),
           "runner_pid": pid, "runner_session": sess}
    if elapsed >= TASK_LIMIT_MIN:
        out["verdict"] = "TIMEOUT"
        out["action"] = ("kill exact PID " + str(pid)) if pid else (
            "coordinator closes the subagent (Muse lane, session "
            + str(sess) + "); no PID kill")
    elif elapsed >= WARN_MIN:
        out["verdict"] = "WARNING"
    else:
        out["verdict"] = "OK"
    return out


def liveness_verdict(state, reports_text, heartbeat_text, now):
    running, task_id, task_start, _reason = running_state(state, reports_text, [])
    last_hb = None
    for line in (heartbeat_text or "").splitlines():
        m = re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[^\s|]*", line)
        if m:
            last_hb = parse_ts(m.group(0)) or last_hb
    last_report = None
    for line in (reports_text or "").splitlines():
        ts = parse_ts(line.split("|")[0].strip()) if "|" in line else None
        if ts:
            last_report = ts
    hb_age = (now - last_hb).total_seconds() / 60.0 if last_hb else None
    rep_age = (now - last_report).total_seconds() / 60.0 if last_report else None
    inside_deadline = bool(
        running and task_start
        and (now - task_start).total_seconds() / 60.0 < TASK_LIMIT_MIN)
    out = {"task": task_id, "heartbeat_age_min": None if hb_age is None else round(hb_age, 1),
           "report_age_min": None if rep_age is None else round(rep_age, 1),
           "inside_task_deadline": inside_deadline}
    hb_stale = hb_age is None or hb_age >= HEARTBEAT_STALE_MIN
    rep_stale = rep_age is None or rep_age >= REPORT_STALE_MIN
    if hb_stale and rep_stale:
        out["verdict"] = "ALERT_REPORTING_CHAIN"
    elif hb_stale and not inside_deadline:
        out["verdict"] = "ALERT_LIVENESS"
    elif hb_stale and inside_deadline:
        out["verdict"] = "SUPPRESSED_INSIDE_DEADLINE"
    else:
        out["verdict"] = "OK"
    return out


def read(path, default=""):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return default


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=["timeout", "liveness"])
    ap.add_argument("--state", default=os.path.join(RUNLOG, "r3-l3-coordinator-state.json"))
    ap.add_argument("--reports", default=os.path.join(RUNLOG, "r3-l3-per-task-reports.log"))
    ap.add_argument("--grades", default=os.path.join(RUNLOG, "R3-L3-grades.jsonl"))
    ap.add_argument("--heartbeat", default=os.path.join(RUNLOG, "r3-l3-heartbeat.log"))
    ap.add_argument("--now", default=None, help="ISO timestamp override (tests)")
    args = ap.parse_args(argv)
    try:
        state = json.loads(read(args.state, "{}"))
    except json.JSONDecodeError as exc:
        print(json.dumps({"error": "state file unparsable: " + str(exc)}))
        return 2
    now = parse_ts(args.now) or now_default()
    reports = read(args.reports)
    if args.mode == "timeout":
        grades = []
        for line in read(args.grades).splitlines():
            line = line.strip()
            if line:
                try:
                    grades.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        verdict = timeout_verdict(state, reports, grades, now)
    else:
        verdict = liveness_verdict(state, reports, read(args.heartbeat), now)
    print(json.dumps(verdict, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
