"""Task chains, stuck-agent killing, detached launch, and stop gates.

Fixes all of Phase 2.5:
- 2.5.1 (A4/I28): promised problem 3 when the problem 2 fix finished,
  did not check until the user asked at 00:46. TaskChainMonitor polls
  the dependency and starts the next task immediately when it finishes,
  then notifies. No waiting for the user to ask.
- 2.5.2 (A5/I27): covered by StepWatchdog in step_watchdog.py (3.5 min
  step report, 15 min worker stall). This module owns the kill side.
- 2.5.3 (A6): clean-env test agent stuck from 13/11, silent 73 hours.
  A stuck agent is KILLED IMMEDIATELY, no asking first, and the user is
  told. kill_stuck_agent does exactly that for registered agents.
- 2.5.4 (G16): the watchdog reports DIRECTLY to Muse. DirectReporter in
  step_watchdog.py is the sink; this module uses it, never a coordinator
  intermediary, so a stuck coordinator cannot swallow a stall flag.
- 2.5.5 (G17): watch_until_done in step_watchdog.py polls every 5 min
  and reports completion at once.
- 2.5.6 (G15): a subagent that launches a long-running process attached
  never completes. launch_detached uses setsid semantics
  (start_new_session) with output to a log file, stdin from /dev/null,
  and never waits: the launcher verifies the process is alive, then
  ends its turn. Every worker brief that launches a long-running process
  must use this.
- 2.5.7 (G18): Track 2 ran 35+ hours with no council decision. Track 2
  is PAUSED. Track2Gate refuses to run it until the gate file records a
  unanimous council + redteam GO. No self-judged stop, no silent resume.
- I29: a pause order must stop agents already dispatched. AgentRegistry
  records every dispatched agent, and pause_all kills or stops each one
  and reports which ones could not be stopped (the I29 failure was a
  redo handed to another agent seconds before the pause, unstoppable
  because nobody had a handle on it).
- I30: overnight results were not reported until the user asked.
  PendingReport queues results produced while the user sleeps; the
  morning check delivers the whole queue instead of waiting to be asked.
"""
import json
import os
import signal
import subprocess
import time
from datetime import datetime
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Asia/Ho_Chi_Minh")
except Exception:  # pragma: no cover
    from datetime import timezone
    TZ = timezone.utc

# A6: 73 hours silent. The kill threshold is 15 minutes of no progress,
# not 73 hours. Stuck means no progress, not dead: a live process that
# has not progressed is stuck (I16 proved alive != progressing).
KILL_IDLE_S = 900.0
KILL_GRACE_S = 5.0


def wall_text(now=None):
    moment = now or datetime.now(TZ)
    return moment.strftime("%Y-%m-%d %H:%M:%S %Z")


def _read_json(path):
    if not Path(path).exists():
        return None
    with open(path, encoding="utf-8") as stream:
        return json.load(stream)


def _write_json(path, value):
    path = Path(path)
    if path.parent and not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    os.replace(tmp, path)


class AgentRegistry:
    """Every dispatched agent gets a handle before it starts.

    I29 happened because a redo was handed to another agent with no
    handle: when the pause order came seconds later, there was nothing
    to stop. No agent is dispatched without a registry entry (pid or
    session id, command, start time). The registry is the thing pause_all
    and kill_stuck_agent act on.
    """

    def __init__(self, path):
        self.path = Path(path)
        self.agents = _read_json(self.path) or {}

    def _save(self):
        _write_json(self.path, self.agents)

    def register(self, agent_id, *, pid=None, session=None, command=""):
        self.agents[agent_id] = {
            "pid": pid, "session": session, "command": command,
            "started_wall": wall_text(), "last_progress_wall": wall_text(),
            "last_progress_mono": time.monotonic(), "status": "running"}
        self._save()
        return self.agents[agent_id]

    def progress(self, agent_id):
        entry = self.agents.get(agent_id)
        if entry is None:
            return False
        entry["last_progress_wall"] = wall_text()
        entry["last_progress_mono"] = time.monotonic()
        self._save()
        return True

    def idle_s(self, agent_id, *, now=None):
        entry = self.agents.get(agent_id)
        if entry is None:
            return None
        return (now if now is not None else time.monotonic()) - \
            entry["last_progress_mono"]

    def mark(self, agent_id, status):
        if agent_id in self.agents:
            self.agents[agent_id]["status"] = status
            self._save()


def _pid_dead(pid):
    """True when the pid no longer exists.

    A plain kill(pid, 0) is not enough: an unreaped child is a zombie and
    still answers signal 0 even though it is dead. Reap first with
    waitpid when the pid is our child; fall back to signal 0 otherwise.
    """
    try:
        done, _ = os.waitpid(pid, os.WNOHANG)
        if done == pid:
            return True
    except ChildProcessError:
        pass
    except OSError:
        pass
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    except PermissionError:
        return False
    return False


def _pid_alive(pid):
    return not _pid_dead(pid)


def kill_agent_pid(pid, *, grace=KILL_GRACE_S):
    """SIGTERM, brief grace, then SIGKILL. Returns True if it is dead."""
    if _pid_dead(pid):
        return True
    os.kill(pid, signal.SIGTERM)
    deadline = time.monotonic() + grace
    while time.monotonic() < deadline:
        if _pid_dead(pid):
            return True
        time.sleep(0.2)
    if _pid_alive(pid):
        os.kill(pid, signal.SIGKILL)
        time.sleep(0.2)
    return _pid_dead(pid)


def kill_stuck_agent(registry, agent_id, *, reporter=None,
                     idle_after=KILL_IDLE_S):
    """Kill a stuck agent immediately, do not ask first, then report.

    A6 rule: stuck (no progress past the threshold) means kill now and
    tell the user. Asking first is how a 73-hour silence happened.
    Returns a dict describing the outcome; the caller must surface it.
    """
    idle = registry.idle_s(agent_id)
    if idle is None:
        return {"ok": False, "agent": agent_id,
                "message": "agent not in registry; nothing to kill"}
    if idle <= idle_after:
        return {"ok": False, "agent": agent_id, "idle_s": round(idle, 1),
                "message": "agent is not stuck yet; no kill"}
    entry = registry.agents[agent_id]
    killed = False
    if entry.get("pid"):
        killed = kill_agent_pid(entry["pid"])
    registry.mark(agent_id, "killed" if killed else "kill-failed")
    outcome = {"ok": killed, "agent": agent_id, "idle_s": round(idle, 1),
               "message": (f"agent {agent_id} stuck {idle:.0f}s with no "
                           f"progress; killed immediately, no asking "
                           f"first (A6 rule)")}
    if reporter is not None:
        reporter.report("KILL-STUCK", outcome["message"], agent=agent_id,
                        idle_s=round(idle, 1))
    return outcome


def pause_all(registry, *, reporter=None):
    """I29: a pause order stops every dispatched agent, and says which
    ones could not be stopped. Returns the per-agent outcomes; a pause
    is not complete while any outcome is unresolved."""
    outcomes = []
    for agent_id, entry in list(registry.agents.items()):
        if entry.get("status") != "running":
            continue
        killed = False
        if entry.get("pid"):
            killed = kill_agent_pid(entry["pid"])
        registry.mark(agent_id, "paused" if killed else "pause-failed")
        outcomes.append({"agent": agent_id, "stopped": killed,
                         "command": entry.get("command", "")})
    if reporter is not None:
        stopped = [o["agent"] for o in outcomes if o["stopped"]]
        failed = [o["agent"] for o in outcomes if not o["stopped"]]
        reporter.report("PAUSE", "pause applied to dispatched agents",
                        stopped=stopped, failed=failed)
    return outcomes


def launch_detached(argv, log_path):
    """Launch a long-running process FULLY DETACHED (G15 fix).

    setsid semantics via start_new_session, stdin from /dev/null, output
    to the log file. The caller must NOT wait on the returned process:
    verify it is alive with poll(), then end the turn. An attached
    launch never completes and its final report never arrives; that is
    the whole G15 failure.
    """
    log_path = Path(log_path)
    if log_path.parent and not log_path.parent.exists():
        log_path.parent.mkdir(parents=True, exist_ok=True)
    log = open(log_path, "ab")
    try:
        proc = subprocess.Popen(
            argv, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
            start_new_session=True, close_fds=True)
    finally:
        log.close()
    alive = proc.poll() is None
    return {"proc": proc, "pid": proc.pid, "alive": alive,
            "log": str(log_path)}


class TaskChainMonitor:
    """Start the next task the moment its dependency finishes (A4/I28).

    A chain is a list of {"task": name, "depends_on": name-or-None}.
    ``status_fn(task)`` returns "done", "running", "failed", or "new".
    ``start_fn(task)`` starts a task. ``check()`` starts every task whose
    dependency is done and which has not started, and notifies via the
    reporter immediately. The monitor is polled on a schedule (every 5
    min, same cadence as the watcher); the point is that the check
    happens without the user asking.
    """

    def __init__(self, state_path, *, reporter=None):
        self.state_path = Path(state_path)
        self.reporter = reporter
        self.chain = _read_json(self.state_path) or {"tasks": []}
        if "tasks" not in self.chain:
            self.chain = {"tasks": []}

    def _save(self):
        _write_json(self.state_path, self.chain)

    def add(self, task, depends_on=None):
        self.chain["tasks"].append(
            {"task": task, "depends_on": depends_on, "status": "new"})
        self._save()

    def set_status(self, task, status):
        for item in self.chain["tasks"]:
            if item["task"] == task:
                item["status"] = status
                self._save()
                return True
        return False

    def check(self, status_fn, start_fn):
        started = []
        for item in self.chain["tasks"]:
            if item["status"] != "new":
                continue
            dep = item["depends_on"]
            if dep is not None and status_fn(dep) != "done":
                continue
            start_fn(item["task"])
            item["status"] = "running"
            started.append(item["task"])
            if self.reporter is not None:
                self.reporter.report(
                    "CHAIN-START",
                    f"dependency {dep or '-'} done; started next task "
                    f"'{item['task']}' immediately, no waiting to be asked",
                    task=item["task"], depends_on=dep)
        if started:
            self._save()
        return started


class PendingReport:
    """Overnight results queued for the morning, never left unreported.

    I30: results produced overnight were not reported until the user
    asked. Queue them here; the morning check delivers the whole queue.
    The queue is a file, not memory: a restart must not lose the report.
    """

    def __init__(self, path):
        self.path = Path(path)
        if self.path.parent and not self.path.parent.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def queue(self, title, body):
        rows = _read_json(self.path) or []
        rows.append({"wall": wall_text(), "title": title, "body": body})
        _write_json(self.path, rows)

    def pending(self):
        return _read_json(self.path) or []

    def deliver(self):
        """Return all queued reports and clear the queue. The caller
        sends them to the user; an empty return means nothing is owed."""
        rows = self.pending()
        if rows:
            _write_json(self.path, [])
        return rows


class Track2Gate:
    """Track 2 is PAUSED until council + redteam unanimously agree GO.

    G18: the loop ran 35+ hours past its stop gate because nobody
    convened the council. The gate file is the single source of truth:
    status is PAUSED unless the file records status GO with a unanimous
    council decision AND a unanimous redteam decision, each with a date.
    The loop checks the gate before every iteration; a missing or
    PAUSED gate refuses to run. Nobody self-judges the stop.
    """

    def __init__(self, path):
        self.path = Path(path)

    def status(self):
        data = _read_json(self.path)
        if not data:
            return {"status": "PAUSED",
                    "reason": "no gate file; default is PAUSED"}
        if data.get("status") != "GO":
            return {"status": "PAUSED",
                    "reason": data.get("reason", "gate is not GO")}
        council = data.get("council_unanimous")
        redteam = data.get("redteam_unanimous")
        if council is not True or redteam is not True:
            return {"status": "PAUSED",
                    "reason": "GO requires unanimous council AND redteam"}
        return {"status": "GO", "council_date": data.get("council_date"),
                "redteam_date": data.get("redteam_date")}

    def may_run(self):
        return self.status()["status"] == "GO"

    def record_pause(self, reason):
        _write_json(self.path, {"status": "PAUSED", "reason": reason,
                                "wall": wall_text()})

    def record_go(self, *, council_date, redteam_date):
        _write_json(self.path, {
            "status": "GO", "council_unanimous": True,
            "redteam_unanimous": True, "council_date": council_date,
            "redteam_date": redteam_date, "wall": wall_text()})
