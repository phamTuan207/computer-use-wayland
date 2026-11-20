"""Always-on timing log for computer-use runs.

Fixes 2.3.1 (H2/I13: Muse thinks longer than Codex, no per-step think-time
log), 2.3.4 (G22: 3-6 ops taking 5 min is WAY too slow, timing/logging
ALWAYS ON), and 2.3.5 (I16: worker 9 min for 6 model calls, same slow-think
pattern, few clicks).

Design, from the failures:
- Think time is measured separately from action time. A step is
  `think` (decision, from observation received to first action issued) plus
  `act` (execution, from first action issued to result observed). The 20/11
  failures were think-dominated: repeated wrong clicks forced re-observe,
  re-aim, re-click loops. If think and act are not split, the loop hides.
- The log is JSONL, one row per step, with wall clock (Asia/Ho_Chi_Minh)
  and elapsed seconds from run start. Appends are trailing-newline safe:
  a JSONL file whose last line lacks ``\\n`` glues two objects into one
  invalid line (G24 lesson, same guard as the run-log fix).
- The logger is on by default. There is no flag to turn timing off; a run
  without timing is a run without evidence, and evidence is what the
  before/after comparison needs.
- Pace check (I16): count model calls vs actions issued. Fewer than one
  action per model call over a 5-minute window, or a step whose think time
  exceeds 60 s, is flagged SLOW_THINK. The flag is data, not a verdict:
  a genuinely hard decision can be slow, but it must be visible.

Usage:
    from timing import TimingLogger
    log = TimingLogger(Path("run-timing.jsonl"), run_id="tc02-20261121")
    with log.think_step("find-add-to-contest"):
        ...decide...
        log.note_action("click", x=837, y=850)
    log.summary()  # dict with totals, medians, slow-step list
"""
import json
import os
import time
from datetime import datetime
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Asia/Ho_Chi_Minh")
except Exception:  # pragma: no cover - minimal env without tzdata
    from datetime import timezone
    TZ = timezone.utc

# A single decision that takes longer than this is slow, full stop.
# H2/I13: decisions stretched past minutes with no record. 60 s is the
# line where a decision must justify itself in the log.
SLOW_THINK_S = 60.0
# G22: a 3-6 operation task has a 5-minute wall budget. Past it, the run
# is over budget and the summary must say so.
SMALL_TASK_BUDGET_S = 300.0
# I16: 6 model calls in 9 minutes with almost no clicks. Fewer than one
# action per model call across a window means thinking, not doing.
MIN_ACTIONS_PER_CALL = 1.0


def wall_text(now=None):
    moment = now or datetime.now(TZ)
    return moment.strftime("%Y-%m-%d %H:%M:%S %Z")


def _ensure_trailing_newline(path):
    """Make sure an existing JSONL file ends with ``\\n`` before appending.

    G24: appending to a JSONL file whose last line has no trailing newline
    glues two JSON objects into one invalid line and the whole file fails
    to parse. Check first, fix first, then append.
    """
    if not path.exists() or path.stat().st_size == 0:
        return
    with open(path, "rb") as stream:
        stream.seek(-1, os.SEEK_END)
        if stream.read(1) != b"\n":
            with open(path, "ab") as out:
                out.write(b"\n")


class TimingLogger:
    """Per-step think/act timing, always on, JSONL."""

    def __init__(self, path, run_id, *, clock=time.monotonic):
        self.path = Path(path)
        self.run_id = run_id
        self._clock = clock
        self.t0 = self._clock()
        self.steps = []
        self.model_calls = 0
        self.actions = 0
        if self.path.parent and not self.path.parent.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
        _ensure_trailing_newline(self.path)

    def elapsed(self):
        return self._clock() - self.t0

    def _write(self, row):
        with open(self.path, "a", encoding="utf-8") as stream:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")

    def think_step(self, name):
        """Context manager timing one decision: think, then actions."""
        return _ThinkStep(self, name)

    def note_model_call(self):
        self.model_calls += 1

    def note_action(self, kind, **detail):
        self.actions += 1
        row = {"run": self.run_id, "wall": wall_text(),
               "elapsed_s": round(self.elapsed(), 3), "event": "action",
               "kind": kind, **detail}
        self._write(row)

    def _finish_step(self, name, think_s, act_s, actions_in_step):
        slow = think_s > SLOW_THINK_S
        row = {"run": self.run_id, "wall": wall_text(),
               "elapsed_s": round(self.elapsed(), 3), "event": "step",
               "step": name, "think_s": round(think_s, 3),
               "act_s": round(act_s, 3),
               "total_s": round(think_s + act_s, 3),
               "actions": actions_in_step,
               "slow_think": slow}
        self.steps.append(row)
        self._write(row)
        return row

    def pace(self):
        """I16 pace check: actions per model call, and slow-step count."""
        calls = self.model_calls or 1
        ratio = self.actions / calls
        slow_steps = [s for s in self.steps if s["slow_think"]]
        return {"model_calls": self.model_calls, "actions": self.actions,
                "actions_per_call": round(ratio, 3),
                "slow_think": ratio < MIN_ACTIONS_PER_CALL,
                "slow_steps": len(slow_steps),
                "slow_step_names": [s["step"] for s in slow_steps]}

    def summary(self):
        """Totals plus the G22 budget verdict, for before/after comparison."""
        totals = {"run": self.run_id, "wall": wall_text(),
                  "elapsed_s": round(self.elapsed(), 3),
                  "steps": len(self.steps)}
        if self.steps:
            think = sorted(s["think_s"] for s in self.steps)
            total = sorted(s["total_s"] for s in self.steps)
            mid = len(think) // 2
            totals["think_median_s"] = think[mid]
            totals["think_max_s"] = think[-1]
            totals["total_median_s"] = total[mid]
            totals["total_max_s"] = total[-1]
        totals.update(self.pace())
        totals["over_small_task_budget"] = (
            self.elapsed() > SMALL_TASK_BUDGET_S and len(self.steps) <= 6)
        self._write({"event": "summary", **totals})
        return totals


class _ThinkStep:
    def __init__(self, logger, name):
        self.logger = logger
        self.name = name
        self._think_start = None
        self._act_start = None
        self._actions_at_start = 0

    def __enter__(self):
        self.logger.note_model_call()
        self._think_start = self.logger._clock()
        self._actions_at_start = self.logger.actions
        return self

    def act(self):
        """Call when the decision is made and execution starts.

        Think time ends here; everything after is act time. If never
        called, the whole step counts as think time, which is honest:
        a step that never acts was all thinking.
        """
        self._act_start = self.logger._clock()

    def __exit__(self, *exc):
        now = self.logger._clock()
        split = self._act_start if self._act_start is not None else now
        think_s = split - self._think_start
        act_s = now - split
        self.logger._finish_step(
            self.name, think_s, act_s,
            self.logger.actions - self._actions_at_start)
        return False
