"""Shared driver helpers for the G14 held-out validation run.

Every state-changing action (click, type, select) goes through
Metrics.act(), which:
  - finds the target element fresh from the live DOM on every attempt
    (locators are callables, never cached element handles),
  - performs the action,
  - polls a caller-supplied DOM verification until it holds or a
    timeout expires,
  - counts the attempt, and counts a MISS when the verification does
    not hold after the action. A miss triggers a retry, up to
    max_attempts tries for one logical action.

Pure DOM reads used for task logic (reading a price, a list of names)
are not actions and are not counted. No pixel coordinates are used
anywhere. Locators use only semantics the application itself exposes
in its live DOM: visible text, placeholders, and the app's own class
and data-test attributes, discovered by inspecting the running page.
"""

import os
import time
import urllib.parse

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

FIREFOX = os.path.expanduser("~/workspace/tools/firefox/firefox")
GECKODRIVER = os.path.expanduser("~/workspace/tools/geckodriver")


class TaskFail(Exception):
    pass


class Metrics:
    def __init__(self):
        self.attempts = 0
        self.misses = 0
        self.retries = 0
        self.log = []

    def act(self, driver, kind, desc, find, do, verify,
            timeout=3.0, max_attempts=3):
        """Run one logical action with verified retries.

        find(driver) -> element (fresh lookup each attempt)
        do(element) -> performs the raw WebDriver action
        verify(driver) -> bool, the intended effect read from the DOM
        """
        last_err = None
        for attempt in range(1, max_attempts + 1):
            self.attempts += 1
            if attempt > 1:
                self.retries += 1
            try:
                el = find(driver)
                do(el)
            except Exception as exc:  # stale element, not clickable, ...
                last_err = exc
                self.misses += 1
                self.log.append(
                    f"MISS {kind} '{desc}' attempt {attempt}: "
                    f"action raised {type(exc).__name__}: {exc}")
                time.sleep(0.3)
                continue
            if self._poll(driver, verify, timeout):
                return
            self.misses += 1
            self.log.append(
                f"MISS {kind} '{desc}' attempt {attempt}: "
                f"effect not verified in DOM within {timeout}s")
            time.sleep(0.3)
        raise TaskFail(
            f"action '{desc}' failed after {max_attempts} attempts; "
            f"last error: {last_err}")

    @staticmethod
    def _poll(driver, verify, timeout):
        deadline = time.time() + timeout
        while True:
            try:
                if verify(driver):
                    return True
            except Exception:
                pass
            if time.time() >= deadline:
                return False
            time.sleep(0.1)


def make_driver():
    """Headless Firefox with the sandbox egress proxy, if configured."""
    opts = Options()
    opts.binary_location = FIREFOX
    opts.add_argument("-headless")
    opts.add_argument("--width=1280")
    opts.add_argument("--height=900")
    proxy = (os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY")
             or os.environ.get("http_proxy") or os.environ.get("HTTP_PROXY"))
    if proxy:
        u = urllib.parse.urlparse(proxy)
        if u.hostname and u.port:
            opts.set_preference("network.proxy.type", 1)
            opts.set_preference("network.proxy.http", u.hostname)
            opts.set_preference("network.proxy.http_port", u.port)
            opts.set_preference("network.proxy.ssl", u.hostname)
            opts.set_preference("network.proxy.ssl_port", u.port)
            opts.set_preference("network.proxy.no_proxies_on",
                                "localhost, 127.0.0.1")
            opts.set_preference("signon.autologin.proxy", True)
            if u.username:
                opts.set_preference("network.proxy.username", u.username)
            if u.password:
                opts.set_preference("network.proxy.password", u.password)
    driver = webdriver.Firefox(service=Service(GECKODRIVER), options=opts)
    driver.set_window_size(1280, 900)
    driver.set_page_load_timeout(60)
    return driver


def wait_for(driver, verify, timeout=15.0):
    """Poll a DOM condition; return True if it held before timeout."""
    return Metrics._poll(driver, verify, timeout)
