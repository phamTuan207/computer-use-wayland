"""Step watchdog: no silent stuck steps, no silent workers, no silent runs.

Fixes 2.3.2 (I14: froze ~5 min at the delete dialog), 2.3.3 (I15:
unresponsive until the user called out), 2.5.2 (A5/I27: file picker stuck
15:37-16:47, 70 min, no report), and 2.5.5 (G17: Gates2 done 14:41, not
reported until the user asked 1.5 h later).

The numbers are the user's own rules, not ours:
- STEP_TIMEOUT_S = 210 (3.5 min). A single step with no action and no
  progress past this is STUCK: report immediately, do not wait for 5 min.
  The user set this on 20/11 at 18:06: "ket qua 3 phut ruoi phai bao,
  ko de den 5p dau".
- HEARTBEAT_S = 300 (5 min). A run must report progress at least every
  5 minutes. Silence longer than that is itself the failure (I15).
- WORKER_STALL_S = 900 (15 min). A worker with no progress past this is
  reported as stalled (A5: worker stuck over 15 min, report).
- WATCH_INTERVAL_S = 300 (5 min). A dedicated watcher polls a
  long-running job every 5 minutes (G17 fix); completion is reported at
  the next poll, never 1.5 h later.

Reporting goes DIRECTLY to the report sink (a file the coordinator and
the user both read, plus stdout). It never goes through a coordinator
intermediary: G16 proved that when the watchdog reports to the
coordinator and the coordinator is the stuck part, the stall flag goes
silent with it. The watchdog reports to Muse, straight.
"""
import json
import time
from datetime import datetime
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Asia/Ho_Chi_Minh")
except Exception:  # pragma: no cover
    from datetime import timezone
    TZ = timezone.utc

STEP_TIMEOUT_S = 210.0
HEARTBEAT_S = 300.0
WORKER_STALL_S = 900.0
WATCH_INTERVAL_S = 300.0


def wall_text(now=None):
    moment = now or datetime.now(TZ)
    return moment.strftime("%Y-%m-%d %H:%M:%S %Z")


class DirectReporter:
    """Report sink that bypasses any coordinator.

    Every report is one JSON line in the report file AND one plain line on
    stdout, so a stuck coordinator can never swallow it: the file is
    readable by the parent agent directly.
    """

    def __init__(self, path):
        self.path = Path(path)
        if self.path.parent and not self.path.parent.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def report(self, kind, message, **detail):
        row = {"wall": wall_text(), "kind": kind, "message": message,
               **detail}
        with open(self.path, "a", encoding="utf-8") as stream:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"[{row['wall']}] {kind}: {message}", flush=True)
        return row


class StepWatchdog:
    """Per-step timeout + progress heartbeat for one run.

    Call ``progress(note)`` on every action, observation, or decision.
    ``check()`` returns a list of reports due right now: a STUCK report
    when the current step passed 3.5 min with no progress, and a
    HEARTBEAT report when 5 min passed since the last progress line.
    Callers must deliver the returned reports via DirectReporter
    immediately; returning them without sending is the I27 failure again.
    """

    def __init__(self, run_id, *, clock=time.monotonic,
                 step_timeout=STEP_TIMEOUT_S, heartbeat=HEARTBEAT_S):
        self.run_id = run_id
        self._clock = clock
        self.step_timeout = step_timeout
        self.heartbeat = heartbeat
        self._step_start = self._clock()
        self._step_name = "start"
        self._last_progress = self._clock()
        self._stuck_reported = False
        self._last_heartbeat = self._clock()

    def start_step(self, name):
        self._step_name = name
        self._step_start = self._clock()
        self._stuck_reported = False
        self._last_progress = self._clock()

    def progress(self, note=""):
        self._last_progress = self._clock()
        self._last_heartbeat = self._clock()
        self._stuck_reported = False
        return {"run": self.run_id, "wall": wall_text(),
                "elapsed_step_s": round(self._clock() - self._step_start, 1),
                "note": note}

    def check(self):
        now = self._clock()
        due = []
        step_age = now - self._step_start
        # Stuck is measured from the last progress, not from the step
        # start: a step that keeps progressing is working, even if it is
        # long. A step with no progress past 3.5 min is stuck (I14/A5).
        idle = now - self._last_progress
        if idle > self.step_timeout and not self._stuck_reported:
            self._stuck_reported = True
            due.append({"kind": "STUCK",
                        "message": (f"step '{self._step_name}' stuck "
                                    f"{idle:.0f}s with no progress "
                                    f"(limit {self.step_timeout:.0f}s); "
                                    f"reporting immediately, not retrying "
                                    f"silently"),
                        "run": self.run_id, "step": self._step_name,
                        "step_age_s": round(step_age, 1),
                        "idle_s": round(idle, 1)})
        if now - self._last_heartbeat > self.heartbeat:
            self._last_heartbeat = now
            due.append({"kind": "HEARTBEAT",
                        "message": (f"still working on step "
                                    f"'{self._step_name}' "
                                    f"({step_age:.0f}s in); next update "
                                    f"within {self.heartbeat:.0f}s"),
                        "run": self.run_id, "step": self._step_name,
                        "step_age_s": round(step_age, 1)})
        return due

    @property
    def step_age(self):
        return self._clock() - self._step_start


class WorkerStall:
    """15-minute stall rule for a delegated worker (A5).

    The worker's own log carries its last-progress timestamp. If the
    worker made no progress for WORKER_STALL_S, the coordinator reports
    it as stalled and stops waiting silently. The stall check reads the
    timestamp, never the worker's word that it is "still working": I16
    showed a worker alive 1 second ago and still 9 minutes into 6 calls.
    Alive is not progress.
    """

    def __init__(self, worker_id, *, clock=time.monotonic,
                 stall_after=WORKER_STALL_S):
        self.worker_id = worker_id
        self._clock = clock
        self.stall_after = stall_after
        self._last_progress = self._clock()

    def progress(self):
        self._last_progress = self._clock()

    def stalled(self):
        return self._clock() - self._last_progress > self.stall_after

    def idle_s(self):
        return self._clock() - self._last_progress


def watch_until_done(poll_fn, *, interval=WATCH_INTERVAL_S, clock=time.sleep,
                     reporter=None, job="job", timeout=None):
    """Dedicated watcher: poll every 5 min, report completion at once.

    Fixes G17: the watcher owns one job, polls ``poll_fn`` every
    ``interval`` seconds, and reports the moment ``poll_fn`` returns a
    non-None result. ``poll_fn`` returns None while the job runs, and a
    dict (or any non-None value) describing the outcome when it finishes.
    A None ``timeout`` watches forever; pass one for bounded waits.
    Returns the outcome, or None on timeout.
    """
    waited = 0.0
    while True:
        outcome = poll_fn()
        if outcome is not None:
            if reporter is not None:
                reporter.report("DONE", f"{job} finished", job=job,
                                outcome=outcome)
            return outcome
        if timeout is not None and waited >= timeout:
            return None
        clock(interval)
        waited += interval
