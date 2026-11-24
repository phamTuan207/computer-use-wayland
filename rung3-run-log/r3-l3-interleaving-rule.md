R3-L3 interleaving rule and session-free verification (precondition 19).
Written 2026-11-24 17:36 +07 by the Phase 0 coordinator.

SINGLE-DRIVER RULE: only one runner drives the laptop at a time. The laptop
session (the browser + the GUI) is a single-driver resource. Two runners must
never drive it simultaneously. The coordinator grants the session to one
runner per task and reclaims it before granting it to the next runner.

INTERLEAVING RULE (how the two runners share the session):
- The run order is fixed: FCC positions 1-28, then Codex positions 29-55.
  In practice the two lanes run sequentially by position, but the speedup
  council allows the lanes to interleave (one runner works while the other
  waits for scoring) as long as only one drives at a time.
- The coordinator is the ONLY agent that grants the session. A runner never
  takes the session on its own. The coordinator grants it by telling the
  runner "start task R3-xxx now" and reclaims it when the runner reports
  the task done and the evidence is snapshotted.
- A runner that is waiting for scoring (its task is done, grade pending)
  does NOT hold the session. The session is free once the evidence is
  snapshotted and the runner has stopped driving.
- The coordinator verifies the session is FREE (procedure below) before
  telling the next runner to start. It never tells a runner to start on the
  assumption the session is free; it verifies first.
- If a runner is found driving while another runner holds the session, the
  coordinator stops the intruding runner immediately and records the
  violation. This is a serious error (it can corrupt both tasks' evidence).

SESSION-FREE VERIFICATION (/proc fd scan, verbatim):
The broker status alone is NOT sufficient to prove the session is free.
The coordinator proves it with a /proc fd scan for the cursor.lock file.
Run this on the laptop (via ssh-laptop.sh):

  ls -la ~/.cache/agent-computer-use/cursor.lock
  for pid in $(ls /proc | grep -E '^[0-9]+$'); do
    if ls -l /proc/$pid/fd 2>/dev/null | grep -q cursor.lock; then
      echo "HOLDER: $pid $(cat /proc/$pid/cmdline 2>/dev/null | tr '\0' ' ')"
    fi
  done
  echo "scan done"

Expected output when the session is FREE:
  - The ls -la shows the cursor.lock file exists (0 bytes, dated Oct 9) or
    does not exist. Either is fine.
  - The for loop prints NO "HOLDER:" lines.
  - The final line is "scan done".
  If any "HOLDER:" line appears, the session is NOT free. The coordinator
  identifies the holding process, tells it to stop, waits, and re-runs the
  scan. Only when the scan shows no holder does the coordinator grant the
  session to the next runner.

VERIFIED AT PREP (2026-11-24 17:11 +07):
- The /proc fd scan found NO holder for cursor.lock. The session was FREE.
- The cursor.lock file exists (0 bytes, Oct 9) but no process holds it.
- The relay (PID 3360774) is running but does not hold the lock.
- FCC (PID 2046632) and Codex (PID 1235041) were alive but idle and did not
  hold the lock.
- This verification is recorded here and in the coordinator state file.

COORDINATOR NAMED: the Phase 0 coordinator (agent 68a84d25) is the
coordinator for Phase 0. The run coordinator (whoever coordinates the run)
inherits this rule. The deputy (named in the state file) is the backup
coordinator. Only the coordinator (or the deputy, if it takes over) grants
the session. No runner, scorer, or other agent grants it.
