#!/usr/bin/env python3
"""Single-session Zen DOM control manager.

Owns the ONE remote session a Zen instance allows (BiDi and Marionette
share a single session slot; a leaked session blocks ALL remote control
until Zen restarts, see docs/zen-dom-control-comparison.md section 7).

Rules enforced here, not by convention:
- One session at a time across all processes (file lock).
- The session is ALWAYS deleted in a finally block, even on error.
- geckodriver is started per session and terminated with it.
- DOM is used to LOCATE and READ. Clicks are NOT done through the DOM
  here: BiDi click failed to fire a handler (04:49 21/11) and Marionette
  click fails on windowed Zen (0x0 viewport quirk). locate() returns the
  exact rect; the caller does the REAL mouse click through cu.py and
  then calls verify() to confirm the DOM changed. That is the hybrid.

Stdlib only (urllib). No selenium module needed; the laptop has no pip.
Default ports are the live Zen's (Marionette 2828). For a temp Zen,
pass --marionette-port.

Usage:
  python3 scripts/zen_dom.py list
  python3 scripts/zen_dom.py tab 8
  python3 scripts/zen_dom.py eval "return document.title"
  python3 scripts/zen_dom.py locate "#count-btn"
  python3 scripts/zen_dom.py rect "#count-btn"
  python3 scripts/zen_dom.py tabs
Environment: ZEN_MARIONETTE_PORT, ZEN_GECKODRIVER, ZEN_WD_PORT.

Timeouts (F3b): every WebDriver call converts TimeoutError, OSError,
and URLError into ZenDomError, so a hung Marionette tab-switch never
escapes raw. tab_at / list_tabs(handle_index=N) targets one tab by its
known handle index instead of scanning; a full list_tabs scan records
a hung handle as an error entry and keeps going.
"""
import argparse
import fcntl
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_MARIONETTE_PORT = int(os.environ.get("ZEN_MARIONETTE_PORT", "2828"))
DEFAULT_WD_PORT = int(os.environ.get("ZEN_WD_PORT", "4444"))
GECKODRIVER = os.environ.get("ZEN_GECKODRIVER", "/tmp/geckodriver")
LOCK_PATH = Path(os.environ.get("ZEN_DOM_LOCK",
                               str(Path.home() / ".cache" / "agent-computer-use"
                                   / "zen_dom.lock")))
ELEMENT_KEY = "element-6066-11e4-a52e-4f735466cecf"


class ZenDomError(RuntimeError):
    pass


def _wait_http(url, timeout_s=30):
    deadline = time.perf_counter() + timeout_s
    while time.perf_counter() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.1)
    return False


class ZenSession:
    """One WebDriver session against one Zen, with guaranteed cleanup."""

    def __init__(self, marionette_port=DEFAULT_MARIONETTE_PORT,
                 wd_port=DEFAULT_WD_PORT, geckodriver=GECKODRIVER,
                 timeout_s=30):
        self.marionette_port = marionette_port
        self.wd_port = wd_port
        self.geckodriver = geckodriver
        self.timeout_s = timeout_s
        self.gecko_proc = None
        self.session = None
        self._lock_file = None

    def __enter__(self):
        LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._lock_file = open(LOCK_PATH, "w")
        try:
            fcntl.flock(self._lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self._lock_file.close()
            raise ZenDomError(
                "another process already holds the Zen remote session; "
                "only one remote session is allowed per Zen instance")
        self.gecko_proc = subprocess.Popen(
            [self.geckodriver, "--connect-existing",
             "--marionette-host", "127.0.0.1",
             "--marionette-port", str(self.marionette_port),
             "--port", str(self.wd_port), "--log", "warn"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not _wait_http(f"http://127.0.0.1:{self.wd_port}/status",
                          self.timeout_s):
            self._cleanup()
            raise ZenDomError("geckodriver status endpoint did not answer")
        try:
            resp = self._wd("POST", "/session", {"capabilities": {
                "alwaysMatch": {"browserName": "firefox"}}})
        except ZenDomError as exc:
            self._cleanup()
            raise ZenDomError(
                "could not create a remote session (is the single session "
                "slot leaked by a hung client? only a Zen restart clears "
                f"it): {exc}")
        self.session = resp["value"]["sessionId"]
        return self

    def __exit__(self, *exc):
        self._cleanup()
        return False

    def _cleanup(self):
        if self.session is not None:
            try:
                self._wd("DELETE", f"/session/{self.session}", {})
            except Exception:
                pass
            self.session = None
        if self.gecko_proc is not None and self.gecko_proc.poll() is None:
            self.gecko_proc.terminate()
            try:
                self.gecko_proc.wait(timeout=10)
            except Exception:
                self.gecko_proc.kill()
            self.gecko_proc = None
        if self._lock_file is not None:
            try:
                fcntl.flock(self._lock_file, fcntl.LOCK_UN)
                self._lock_file.close()
            except Exception:
                pass
            self._lock_file = None

    def _wd(self, method, path, body=None):
        """One WebDriver call. Every transport failure becomes a
        ZenDomError, never a raw exception (F3b): Marionette
        tab-switch intermittently HANGS past the timeout, and the raw
        TimeoutError used to escape the ZenDomError-only handling and
        kill the whole live lane. urllib wraps a socket timeout in a
        URLError whose reason is the TimeoutError, so URLError is
        caught too; HTTPError keeps its own branch first because it
        is a URLError subclass and carries the status code.
        """
        url = f"http://127.0.0.1:{self.wd_port}{path}"
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            raw = e.read().decode(errors="replace")[:400]
            raise ZenDomError(f"HTTP {e.code} on {method} {path}: {raw}")
        except (TimeoutError, OSError, urllib.error.URLError) as e:
            raise ZenDomError(
                f"transport failure on {method} {path} after "
                f"{self.timeout_s}s timeout: {e}") from e

    def current_handle(self):
        """The handle of the tab Marionette currently has selected."""
        return self._wd("GET", f"/session/{self.session}/window")["value"]

    def switch_to_handle(self, handle):
        """Select one tab by its known handle. Raises ZenDomError on a
        hang or transport failure (via _wd); the caller decides whether
        to skip that handle or abort."""
        self._wd("POST", f"/session/{self.session}/window",
                 {"handle": handle})

    def _read_current_tab(self, handle):
        """Title and URL of the currently selected tab."""
        return {
            "handle": handle[:8],
            "title": self._wd("GET", f"/session/{self.session}/title")["value"],
            "url": self._wd("GET", f"/session/{self.session}/url")["value"],
        }

    def evaluate(self, script, args=None):
        """Run JS in the current tab. The reliable read/write path."""
        resp = self._wd("POST", f"/session/{self.session}/execute/sync",
                        {"script": script, "args": args or []})
        return resp["value"]

    def tab_at(self, index):
        """One tab by known handle index, without scanning the rest.

        Handle order is tab order (proven in F3b Arm A run 3), so a
        caller that already knows the index targets that handle
        directly: one switch, one title read, one URL read, then the
        original tab is restored. A hang on that single switch raises
        ZenDomError (via _wd) instead of escaping raw. Raises
        ZenDomError when the index is out of range.
        """
        return self.list_tabs(handle_index=index)[0]

    def list_tabs(self, handle_index=None):
        """List tabs, or one tab when handle_index is given.

        Full scan: every handle is switched to in turn, and a hang or
        transport failure on ONE handle is recorded as an error entry
        for that handle and skipped (F3b Arm D v2 pattern), instead of
        killing the whole listing. The originally selected tab is
        always restored, even when a handle hangs. A tab entry is
        {handle, title, url}; a skipped handle is {handle, error}.
        """
        handles = self._wd("GET", f"/session/{self.session}/window/handles")["value"]
        current = self.current_handle()
        if handle_index is not None:
            if (not isinstance(handle_index, int) or isinstance(handle_index, bool)
                    or handle_index < 0 or handle_index >= len(handles)):
                raise ZenDomError(
                    f"tab index {handle_index!r} out of range: "
                    f"{len(handles)} tabs")
            try:
                self.switch_to_handle(handles[handle_index])
                return [self._read_current_tab(handles[handle_index])]
            finally:
                try:
                    self.switch_to_handle(current)
                except ZenDomError:
                    pass
        tabs = []
        try:
            for handle in handles:
                try:
                    self.switch_to_handle(handle)
                    tabs.append(self._read_current_tab(handle))
                except (ZenDomError, TimeoutError, OSError) as exc:
                    # F3b Arm D v2: catch per handle, record, keep going.
                    tabs.append({"handle": handle[:8],
                                 "error": str(exc)[:200]})
        finally:
            try:
                self.switch_to_handle(current)
            except (ZenDomError, TimeoutError, OSError):
                pass
        return tabs

    def locate(self, selector):
        """Exact rect of an element, via getBoundingClientRect (JS path).

        Returns {x, y, width, height, center_x, center_y} in CSS pixels,
        or None if the selector matches nothing. Use center_x/center_y
        for the REAL mouse click; never a DOM click.
        """
        js = ("const el = document.querySelector(arguments[0]);"
              " if (!el) return null;"
              " const r = el.getBoundingClientRect();"
              " return {x: r.x, y: r.y, width: r.width, height: r.height,"
              " center_x: r.x + r.width / 2, center_y: r.y + r.height / 2};")
        rect = self.evaluate(js, [selector])
        return rect

    def verify(self, script, expected):
        """Check a DOM condition after a real mouse click. Returns True
        when the JS expression equals the expected value."""
        return self.evaluate(script) == expected


def kill_hung_remote_clients(max_age_s=900):
    """Watchdog helper: kill node/python processes that look like hung
    remote-control clients (puppeteer_bidi, selenium attach tests).
    Returns the list of killed PIDs. Never kills the browser itself."""
    import re
    killed = []
    try:
        out = subprocess.run(["ps", "-eo", "pid,etimes,args"],
                             capture_output=True, text=True, timeout=10).stdout
    except Exception:
        return killed
    for line in out.splitlines():
        m = re.match(r"\s*(\d+)\s+(\d+)\s+(.*)$", line)
        if not m:
            continue
        pid, age, args = int(m.group(1)), int(m.group(2)), m.group(3)
        if age < max_age_s:
            continue
        if ("puppeteer_bidi" in args or "zen_selenium" in args
                or "selenium_connect_existing" in args):
            try:
                os.kill(pid, 15)
                killed.append(pid)
            except Exception:
                pass
    return killed


def main():
    parser = argparse.ArgumentParser(description="Zen DOM control, single session")
    parser.add_argument("--marionette-port", type=int, default=DEFAULT_MARIONETTE_PORT)
    parser.add_argument("--wd-port", type=int, default=DEFAULT_WD_PORT)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="list tabs")
    p_tab = sub.add_parser("tab", help="one tab by handle index, no scan")
    p_tab.add_argument("index", type=int,
                       help="handle index (handle order is tab order)")
    p_eval = sub.add_parser("eval", help="run JS in the current tab")
    p_eval.add_argument("script")
    p_loc = sub.add_parser("locate", help="exact rect of a selector")
    p_loc.add_argument("selector")
    sub.add_parser("kill-hung", help="kill hung remote-control clients")
    args = parser.parse_args()

    if args.cmd == "kill-hung":
        print(json.dumps({"killed": kill_hung_remote_clients()}, indent=1))
        return 0
    with ZenSession(marionette_port=args.marionette_port,
                    wd_port=args.wd_port) as z:
        if args.cmd == "list":
            print(json.dumps(z.list_tabs(), indent=1, ensure_ascii=False))
        elif args.cmd == "tab":
            print(json.dumps(z.tab_at(args.index), indent=1,
                             ensure_ascii=False))
        elif args.cmd == "eval":
            print(json.dumps(z.evaluate(args.script), indent=1, ensure_ascii=False))
        elif args.cmd == "locate":
            print(json.dumps(z.locate(args.selector), indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
