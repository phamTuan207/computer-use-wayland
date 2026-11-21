#!/usr/bin/env python3
"""Shared driver for experiment 3.4.1 E1, planning vs execution.

One Session wraps a headless Firefox driven by Selenium and counts:
- observations: full DOM state reads used to decide the next action
  (the final checker read is NOT counted, it is identical for both arms)
- actions: WebDriver interactions (click, one field fill, select, key use)
- retries: times the script had to redo work after a failed check
Timing: wall clock and monotonic elapsed for the whole run, plus the
browser start portion separately.
"""

import datetime
import json
import os
import time
from pathlib import Path

ROOT = Path(__file__).parent
FIXTURES = ROOT / "fixtures"
FIREFOX = os.environ.get("FIREFOX_BINARY", str(Path.home() / "workspace/tools/firefox/firefox"))
GECKODRIVER = os.environ.get("GECKODRIVER", str(Path.home() / "workspace/tools/geckodriver"))


def wall_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def fixture_uri(name):
    return (FIXTURES / name).as_uri()


class Session:
    def __init__(self, task_id):
        self.task_id = task_id
        self.driver = None
        self.observations = 0
        self.actions = 0
        self.retries = 0
        self.browser_start_s = 0.0
        self.wall_start = None
        self._t0 = None

    def start(self, fixture):
        from selenium import webdriver
        from selenium.webdriver.firefox.options import Options
        from selenium.webdriver.firefox.service import Service

        self.wall_start = wall_now()
        self._t0 = time.perf_counter()
        t = time.perf_counter()
        opts = Options()
        opts.add_argument("-headless")
        opts.binary_location = FIREFOX
        service = Service(executable_path=GECKODRIVER, port=0)
        self.driver = webdriver.Firefox(options=opts, service=service)
        self.browser_start_s = round(time.perf_counter() - t, 4)
        self.driver.get(fixture_uri(fixture))
        return self.driver

    # --- observation: one full state read, the unit arm A pays per step ---
    def observe(self):
        self.observations += 1
        return self.driver.execute_script(
            "return {title: document.title,"
            " text: document.body ? document.body.innerText.slice(0, 2000) : '',"
            " inputs: Array.prototype.map.call(document.querySelectorAll('input,select,textarea'),"
            "   function (e) { return {id: e.id, value: e.value, checked: e.checked}; })};")

    # --- action primitives, each counts as one action ---
    def click(self, element_id):
        self.actions += 1
        self.driver.find_element("id", element_id).click()

    def click_css(self, selector):
        self.actions += 1
        self.driver.find_element("css selector", selector).click()

    def type_into(self, element_id, text, clear_first=True):
        self.actions += 1
        el = self.driver.find_element("id", element_id)
        if clear_first:
            el.clear()
        el.send_keys(text)

    def select_value(self, element_id, value):
        self.actions += 1
        from selenium.webdriver.support.ui import Select
        Select(self.driver.find_element("id", element_id)).select_by_value(value)

    def set_range(self, element_id, target):
        """Focus the range input and arrow-key to the target value."""
        self.actions += 1
        from selenium.webdriver.common.keys import Keys
        el = self.driver.find_element("id", element_id)
        el.click()
        current = int(el.get_attribute("value"))
        key = Keys.ARROW_RIGHT if target > current else Keys.ARROW_LEFT
        for _ in range(abs(target - current)):
            el.send_keys(key)
        assert int(el.get_attribute("value")) == target

    def read(self, script):
        """A targeted read that is not a decision observation (checker use)."""
        return self.driver.execute_script(script)

    def text_of(self, element_id):
        return self.driver.find_element("id", element_id).text

    def finish(self, ok, detail=""):
        elapsed = round(time.perf_counter() - self._t0, 4)
        result = {
            "task": self.task_id,
            "ok": bool(ok),
            "wall_start": self.wall_start,
            "wall_end": wall_now(),
            "elapsed_s": elapsed,
            "steps_only_s": round(elapsed - self.browser_start_s, 4),
            "browser_start_s": self.browser_start_s,
            "observations": self.observations,
            "actions": self.actions,
            "retries": self.retries,
            "detail": detail,
        }
        try:
            if self.driver is not None:
                self.driver.quit()
        except Exception:
            pass
        print("RESULT " + json.dumps(result), flush=True)
        return result
