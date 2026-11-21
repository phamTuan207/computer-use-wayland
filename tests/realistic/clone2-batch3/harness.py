#!/usr/bin/env python3
"""Shared harness for the clone2 batch 3 hard realistic tests.

Every test drives a real browser through Selenium against a fully
offline local HTML fixture, and the checker verifies real DOM state
after every action. No simulated DOM, no mock elements.

Environment:
  FIREFOX_BINARY  browser binary, Firefox or Zen
                  default ~/workspace/tools/firefox/firefox when it
                  exists, else "firefox" from PATH
  GECKODRIVER     geckodriver binary
                  default ~/workspace/tools/geckodriver when it
                  exists, else "geckodriver" from PATH
  BATCH3_HEADED   set to 1 to run headed, default headless

Each test records steps with wall clock and monotonic elapsed,
checks with pass or fail, and prints one RESULT json line at the
end, the same contract as the earlier clone2 suites.
"""

import datetime
import json
import os
import sys
import time
from pathlib import Path

SUITE_ROOT = Path(__file__).parent
FIXTURES = SUITE_ROOT / "fixtures"


def wall_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _default_binary(env_name, tools_path, fallback):
    value = os.environ.get(env_name)
    if value:
        return value
    if Path(tools_path).exists():
        return tools_path
    return fallback


def browser_binary():
    return _default_binary("FIREFOX_BINARY",
                           str(Path.home() / "workspace/tools/firefox/firefox"),
                           "firefox")


def geckodriver_binary():
    return _default_binary("GECKODRIVER",
                           str(Path.home() / "workspace/tools/geckodriver"),
                           "geckodriver")


def fixture_uri(name):
    return (FIXTURES / name).as_uri()


class BrowserCase:
    def __init__(self, test_id, title):
        self.test_id = test_id
        self.title = title
        self.wall_start = wall_now()
        self._t0 = time.perf_counter()
        self.steps = []
        self.checks = []
        self.driver = None
        print(f"[{self.wall_start}] {test_id} {title}", flush=True)

    def start_browser(self):
        from selenium import webdriver
        from selenium.webdriver.firefox.options import Options
        from selenium.webdriver.firefox.service import Service
        options = Options()
        options.binary_location = browser_binary()
        if os.environ.get("BATCH3_HEADED") != "1":
            options.add_argument("--headless")
        service = Service(executable_path=geckodriver_binary(), port=0)
        t0 = time.perf_counter()
        self.driver = webdriver.Firefox(service=service, options=options)
        self.driver.set_window_size(1280, 900)
        self.steps.append({"step": "browser_start", "ok": True,
                           "elapsed_s": round(time.perf_counter() - t0, 4),
                           "detail": {"binary": options.binary_location}})
        print(f"  step browser_start ok elapsed_s={self.steps[-1]['elapsed_s']}",
              flush=True)
        return self.driver

    def step(self, name, func):
        wall_start = wall_now()
        t0 = time.perf_counter()
        try:
            detail = func()
            ok, error = True, None
        except Exception as exc:
            detail, ok, error = None, False, f"{type(exc).__name__}: {exc}"
        entry = {"step": name, "ok": ok, "wall_start": wall_start,
                 "elapsed_s": round(time.perf_counter() - t0, 4),
                 "detail": detail, "error": error}
        self.steps.append(entry)
        print(f"  step {name} {'ok' if ok else 'FAIL'} "
              f"elapsed_s={entry['elapsed_s']} detail={detail} "
              f"error={error}", flush=True)
        if not ok:
            raise RuntimeError(f"step failed: {name}: {error}")
        return detail

    def check(self, name, condition, detail=""):
        ok = bool(condition)
        self.checks.append({"check": name, "ok": ok, "detail": str(detail)})
        print(f"  check {name} {'ok' if ok else 'FAIL'} {detail}", flush=True)
        return ok

    def finish(self):
        if self.driver is not None:
            try:
                self.driver.quit()
            except Exception:
                pass
        ok = (all(s["ok"] for s in self.steps)
              and all(c["ok"] for c in self.checks)
              and len(self.checks) > 0)
        result = {"id": self.test_id, "title": self.title, "ok": ok,
                  "wall_start": self.wall_start, "wall_end": wall_now(),
                  "elapsed_s": round(time.perf_counter() - self._t0, 4),
                  "step_count": len(self.steps),
                  "steps": self.steps, "checks": self.checks}
        print("RESULT " + json.dumps(result, ensure_ascii=False), flush=True)
        return 0 if ok else 1
