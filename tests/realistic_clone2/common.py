#!/usr/bin/env python3
"""Shared helpers for the clone2 realistic test suite.

Every test builds its own fixture in a fresh temp workspace, performs
a realistic agent task with real file and process operations, then
checks the outcome with an independent checker. Timing is wall clock
plus monotonic elapsed, per phase and in total, and every test prints
one RESULT json line that run_all.py aggregates.
"""

import datetime
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def wall_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def run_cmd(args, cwd=None, timeout=60):
    """Run a command, return dict with exit code, output, elapsed."""
    start = time.perf_counter()
    proc = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                          timeout=timeout)
    return {"args": [str(a) for a in args], "exit": proc.returncode,
            "stdout": proc.stdout, "stderr": proc.stderr,
            "elapsed_s": round(time.perf_counter() - start, 4)}


class Case:
    def __init__(self, test_id, title, topic):
        self.test_id = test_id
        self.title = title
        self.topic = topic
        self.wall_start = wall_now()
        self._t0 = time.perf_counter()
        self.checks = []
        self.phases = []
        self.ws = Path(tempfile.mkdtemp(prefix=f"clone2_{test_id}_"))
        print(f"[{self.wall_start}] {test_id} {title} ws={self.ws}",
              flush=True)

    def phase(self, name):
        case = self

        class _Phase:
            def __enter__(self):
                self.wall_start = wall_now()
                self.t0 = time.perf_counter()
                return self

            def __exit__(self, *exc):
                entry = {"phase": name, "wall_start": self.wall_start,
                         "wall_end": wall_now(),
                         "elapsed_s": round(time.perf_counter() - self.t0, 4)}
                case.phases.append(entry)
                print(f"  phase {name} elapsed_s={entry['elapsed_s']}",
                      flush=True)
                return False

        return _Phase()

    def check(self, name, condition, detail=""):
        ok = bool(condition)
        self.checks.append({"check": name, "ok": ok, "detail": str(detail)})
        print(f"  check {name} {'ok' if ok else 'FAIL'} {detail}", flush=True)
        return ok

    def finish(self, keep_ws=False):
        ok = all(c["ok"] for c in self.checks) and len(self.checks) > 0
        result = {"id": self.test_id, "title": self.title,
                  "topic": self.topic, "ok": ok,
                  "wall_start": self.wall_start, "wall_end": wall_now(),
                  "elapsed_s": round(time.perf_counter() - self._t0, 4),
                  "phases": self.phases, "checks": self.checks,
                  "workspace": str(self.ws)}
        print("RESULT " + json.dumps(result, ensure_ascii=False), flush=True)
        if not keep_ws:
            shutil.rmtree(self.ws, ignore_errors=True)
        return 0 if ok else 1
