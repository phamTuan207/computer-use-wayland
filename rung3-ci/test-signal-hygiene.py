#!/usr/bin/env python3
"""Dry-run test for signal-hygiene.py (fix-review R1).

Fake state/report/grade fixtures in a temp dir; asserts the three
required verdicts plus the redteam early-row guard:
  (a) completed task, stale task_start 40 min old, per-task row after
      task_start -> NOT_RUNNING (no kill)
  (b) running task inside its 30-min deadline, stale heartbeat ->
      SUPPRESSED_INSIDE_DEADLINE (no liveness alert)
  (c) running task past deadline, no completion signals -> TIMEOUT,
      and the Muse lane action is subagent close, never a PID kill
  (d) per-task row written BEFORE task_start (early/backfilled) does
      not spare a hung task -> TIMEOUT still fires (redteam 1.1)
Run: python3 rung3-ci/test-signal-hygiene.py
No personal info in this file.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
HELPER = os.path.join(HERE, "signal-hygiene.py")
NOW = "2026-11-27T05:00:00+07:00"


def run(mode, state, reports="", grades="", heartbeat=""):
    with tempfile.TemporaryDirectory() as d:
        paths = {}
        for name, content in [("state", json.dumps(state)), ("reports", reports),
                              ("grades", grades), ("heartbeat", heartbeat)]:
            p = os.path.join(d, name)
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(content)
            paths[name] = p
        out = subprocess.run(
            [sys.executable, HELPER, mode, "--state", paths["state"],
             "--reports", paths["reports"], "--grades", paths["grades"],
             "--heartbeat", paths["heartbeat"], "--now", NOW],
            capture_output=True, text=True)
        assert out.returncode == 0, out.stderr
        return json.loads(out.stdout)


def check(name, got, want_verdict, want_in_action=None):
    ok = got.get("verdict") == want_verdict
    if want_in_action:
        ok = ok and want_in_action in str(got.get("action", ""))
    print(("PASS" if ok else "FAIL"), name, "->", json.dumps(got, sort_keys=True))
    assert ok, name


# (a) completed: task_start 40 min ago, report row after it
check("a completed-task guard", run("timeout",
      {"status": "RUNNING", "current_task": "R3-090 driving",
       "task_start": "2026-11-27T04:20:00+07:00", "runner_pid": 4242},
      reports="2026-11-27T04:45:00+07:00 | R3-090 | position 40 | PASS | done | Rule-A 1/0\n"),
      "NOT_RUNNING")

# (b) running inside deadline (10 min in), heartbeat 20 min stale
check("b deadline suppression", run("liveness",
      {"status": "RUNNING", "current_task": "R3-091 driving",
       "task_start": "2026-11-27T04:50:00+07:00", "runner_pid": 4242},
      reports="2026-11-27T04:35:00+07:00 | R3-090 | position 40 | PASS | done | Rule-A 1/0\n",
      heartbeat="2026-11-27T04:40:00+07:00 coordinator heartbeat\n"),
      "SUPPRESSED_INSIDE_DEADLINE")

# (c) past deadline (35 min), no completion signals, Muse lane (session, no PID)
check("c timeout Muse lane", run("timeout",
      {"status": "RUNNING", "current_task": "R3-092 driving",
       "task_start": "2026-11-27T04:25:00+07:00", "runner_pid": None,
       "claude_runner_session": "sess-0001"}),
      "TIMEOUT", want_in_action="coordinator closes the subagent")

# (c2) past deadline, PID lane -> exact-PID kill action
check("c2 timeout PID lane", run("timeout",
      {"status": "RUNNING", "current_task": "R3-093 driving",
       "task_start": "2026-11-27T04:25:00+07:00", "runner_pid": 7777}),
      "TIMEOUT", want_in_action="kill exact PID 7777")

# (d) early/backfilled row before task_start must not spare a hang
check("d early row does not spare", run("timeout",
      {"status": "RUNNING", "current_task": "R3-094 driving",
       "task_start": "2026-11-27T04:25:00+07:00", "runner_pid": 7777},
      reports="2026-11-27T04:10:00+07:00 | R3-094 | position 41 | PASS | backfill | Rule-A 1/0\n"),
      "TIMEOUT")

# (e) grade row after task_start also completes the task
check("e grade row completes", run("timeout",
      {"status": "RUNNING", "current_task": "R3-095 driving",
       "task_start": "2026-11-27T04:20:00+07:00", "runner_pid": 4242},
      grades=json.dumps({"task_id": "R3-095", "test_row": False,
                         "timestamps": {"recorded_at": "2026-11-27T04:50:00+07:00"}}) + "\n"),
      "NOT_RUNNING")

print("ALL PASS")
