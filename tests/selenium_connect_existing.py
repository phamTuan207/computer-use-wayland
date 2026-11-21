#!/usr/bin/env python3
"""Selenium plus geckodriver, connect-existing attach test for Firefox and Zen.

Purpose
Attach to a Firefox or Zen instance that is already running with
Marionette enabled, then run a timed DOM task against it: list tabs,
read the DOM, type into an input, click a button and verify the DOM
changed, open a second tab, read it, close it, delete the session, and
confirm the browser process is still alive after the session ends.

How attach works here, and how it differs from Chrome
Chrome attach uses a DevTools debugging address. Firefox attach does
not. The browser is started first with Marionette enabled, geckodriver
is then started with the connect-existing flag and the Marionette
port, and Selenium talks WebDriver HTTP to that geckodriver. This
script uses that second pattern directly: it starts geckodriver
itself as a subprocess, waits for its status endpoint, then creates
the session with webdriver.Remote. The alternative pattern, letting
Selenium start geckodriver through a Service object with the same
flags in service_args, is shown in the module notes in
coord/clone2.md and reaches the same geckodriver process.

Browser launch recipe, run this yourself for a pure attach test
  firefox -marionette -no-remote -profile /path/to/test-profile URL
  zen -marionette -no-remote -profile /path/to/test-profile URL
Marionette listens on 127.0.0.1 port 2828 by default. If the profile
sets marionette.port to another value, pass that value with
--marionette-port. Keep both Marionette and geckodriver on loopback.

Self contained mode
With --launch-firefox the script launches the browser itself with a
temporary profile, waits for the Marionette port, attaches, runs the
task, and at the end terminates only the browser it launched. This is
the mode used for the recorded local run, because it proves the full
sequence on one machine with no manual steps.

Timing and logging
Every step is timed twice: wall clock, ISO 8601 UTC start and end,
and elapsed, time.perf_counter seconds. Each step prints one log line
and is also collected into a JSON summary printed at the end and,
with --log-json PATH, written to a file. Nothing in the log contains
personal data: URLs are the fixture page or the --second-url value,
titles, element counts and typed test text only.

Usage
  python3 tests/selenium_connect_existing.py \
      --geckodriver /path/to/geckodriver \
      --launch-firefox --firefox-binary /path/to/firefox \
      --headless \
      --log-json /tmp/selenium_attach_log.json

  Pure attach, browser already running with Marionette on 2828:
  python3 tests/selenium_connect_existing.py \
      --geckodriver /path/to/geckodriver

Requirements: Python 3, selenium 4, geckodriver matching the target
browser generation, see the support table in coord/clone2.md.
Exit code 0 means every step passed, 1 means at least one step failed.
The full exception text is printed for a failed step, never hidden.
"""

import argparse
import datetime
import json
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "selenium_attach_fixture.html"
TEST_TEXT = "clone2 dom test"


def wall_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class StepLog:
    def __init__(self):
        self.steps = []

    def run(self, name, func):
        wall_start = wall_now()
        start = time.perf_counter()
        try:
            detail = func()
            ok = True
            error = None
        except Exception as exc:  # recorded and re-raised as a failed step
            detail = None
            ok = False
            error = f"{type(exc).__name__}: {exc}"
        elapsed = time.perf_counter() - start
        entry = {
            "step": name,
            "ok": ok,
            "wall_start": wall_start,
            "wall_end": wall_now(),
            "elapsed_s": round(elapsed, 4),
            "detail": detail,
            "error": error,
        }
        self.steps.append(entry)
        status = "ok" if ok else "FAIL"
        print(f"[{entry['wall_start']}] {name} {status} elapsed_s={entry['elapsed_s']} "
              f"detail={detail} error={error}", flush=True)
        if not ok:
            raise RuntimeError(f"step failed: {name}: {error}")
        return detail


def wait_for_port(host, port, timeout_s):
    deadline = time.perf_counter() + timeout_s
    while time.perf_counter() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.1)
    return False


def wait_for_http(url, timeout_s):
    deadline = time.perf_counter() + timeout_s
    while time.perf_counter() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode("utf-8", "replace"))
        except Exception:
            time.sleep(0.1)
    return None


def main():
    parser = argparse.ArgumentParser(description="Selenium connect-existing attach test")
    parser.add_argument("--geckodriver", required=True, help="path to the geckodriver binary")
    parser.add_argument("--marionette-host", default="127.0.0.1")
    parser.add_argument("--marionette-port", type=int, default=2828)
    parser.add_argument("--webdriver-port", type=int, default=4444)
    parser.add_argument("--url", default=FIXTURE.as_uri(),
                        help="page the browser shows first, default the local fixture")
    parser.add_argument("--second-url", default="https://example.com/",
                        help="page opened in the second tab step")
    parser.add_argument("--launch-firefox", action="store_true",
                        help="launch the browser here, with a temporary profile")
    parser.add_argument("--firefox-binary", default="",
                        help="browser binary for --launch-firefox, firefox or zen")
    parser.add_argument("--profile", default="",
                        help="profile dir for --launch-firefox, default a temp dir")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--log-json", default="")
    parser.add_argument("--keep-browser", action="store_true",
                        help="do not terminate a browser launched by this script")
    args = parser.parse_args()

    if args.launch_firefox and not args.firefox_binary:
        print("error: --launch-firefox needs --firefox-binary", flush=True)
        return 2

    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.firefox.options import Options

    log = StepLog()
    wall_total_start = wall_now()
    total_start = time.perf_counter()
    firefox_proc = None
    gecko_proc = None
    driver = None
    profile_dir = args.profile
    summary = {"ok": False, "steps": log.steps}

    try:
        if args.launch_firefox:
            if not profile_dir:
                profile_dir = tempfile.mkdtemp(prefix="selenium-attach-profile-")

            def launch_browser():
                nonlocal firefox_proc
                cmd = [args.firefox_binary, "-marionette", "-no-remote",
                       "-profile", profile_dir]
                if args.headless:
                    cmd.append("-headless")
                cmd.append(args.url)
                firefox_proc = subprocess.Popen(
                    cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if not wait_for_port(args.marionette_host, args.marionette_port,
                                     args.timeout):
                    raise RuntimeError("Marionette port did not open in time")
                return {"pid": firefox_proc.pid, "profile": profile_dir,
                        "marionette": f"{args.marionette_host}:{args.marionette_port}"}

            log.run("launch_browser_with_marionette", launch_browser)

        def start_geckodriver():
            nonlocal gecko_proc
            cmd = [args.geckodriver, "--connect-existing",
                   "--marionette-host", args.marionette_host,
                   "--marionette-port", str(args.marionette_port),
                   "--port", str(args.webdriver_port), "--log", "info"]
            gecko_proc = subprocess.Popen(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            status = wait_for_http(
                f"http://127.0.0.1:{args.webdriver_port}/status", args.timeout)
            if status is None:
                raise RuntimeError("geckodriver status endpoint did not answer")
            return {"pid": gecko_proc.pid, "status": status}

        log.run("start_geckodriver_connect_existing", start_geckodriver)

        def create_session():
            nonlocal driver
            driver = webdriver.Remote(
                command_executor=f"http://127.0.0.1:{args.webdriver_port}",
                options=Options())
            return {"session_id": driver.session_id,
                    "capabilities_browser": driver.capabilities.get("browserName"),
                    "capabilities_version": driver.capabilities.get("browserVersion")}

        log.run("create_session", create_session)

        def list_tabs():
            handles = driver.window_handles
            tabs = []
            original = driver.current_window_handle
            for handle in handles:
                driver.switch_to.window(handle)
                tabs.append({"title": driver.title, "url": driver.current_url})
            driver.switch_to.window(original)
            return {"count": len(handles), "tabs": tabs}

        first_tabs = log.run("list_tabs", list_tabs)

        def read_dom():
            source = driver.page_source
            count = driver.execute_script("return document.querySelectorAll('*').length")
            ready = driver.execute_script("return document.readyState")
            return {"title": driver.title, "url": driver.current_url,
                    "page_source_chars": len(source), "element_count": count,
                    "ready_state": ready,
                    "heading": driver.find_element(By.ID, "heading").text}

        log.run("read_dom", read_dom)

        def type_into_input():
            box = driver.find_element(By.ID, "q")
            box.clear()
            box.send_keys(TEST_TEXT)
            value = box.get_attribute("value")
            if value != TEST_TEXT:
                raise RuntimeError(f"input value mismatch: {value!r}")
            return {"typed": TEST_TEXT, "value_read_back": value}

        log.run("type_into_input", type_into_input)

        def click_and_verify():
            driver.find_element(By.ID, "go").click()
            out = driver.find_element(By.ID, "out").text
            expected = "clicked:" + TEST_TEXT
            if out != expected:
                raise RuntimeError(f"output mismatch: {out!r} != {expected!r}")
            return {"output_text": out}

        log.run("click_and_verify_dom_change", click_and_verify)

        def second_tab():
            before = len(driver.window_handles)
            driver.switch_to.new_window("tab")
            driver.get(args.second_url)
            info = {"title": driver.title, "url": driver.current_url,
                    "handles_before": before,
                    "handles_now": len(driver.window_handles)}
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            info["handles_after_close"] = len(driver.window_handles)
            info["back_to_title"] = driver.title
            return info

        log.run("open_second_tab_read_and_close", second_tab)

        def delete_session():
            nonlocal driver
            driver.quit()
            driver = None
            return {"session_deleted": True}

        log.run("delete_session", delete_session)

        def browser_still_alive():
            alive = {}
            if firefox_proc is not None:
                alive["launched_browser_running"] = firefox_proc.poll() is None
            try:
                with socket.create_connection(
                        (args.marionette_host, args.marionette_port), timeout=2):
                    alive["marionette_port_open"] = True
            except OSError:
                alive["marionette_port_open"] = False
            if firefox_proc is not None and not alive["launched_browser_running"]:
                raise RuntimeError("browser exited when the session was deleted")
            return alive

        log.run("browser_still_alive_after_session_delete", browser_still_alive)
        summary["ok"] = True
    except Exception as exc:
        summary["ok"] = False
        summary["failure"] = f"{type(exc).__name__}: {exc}"
        print(f"FAILURE {summary['failure']}", flush=True)
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass
        if gecko_proc is not None and gecko_proc.poll() is None:
            gecko_proc.terminate()
            try:
                gecko_proc.wait(timeout=10)
            except Exception:
                gecko_proc.kill()
        if firefox_proc is not None and not args.keep_browser:
            if firefox_proc.poll() is None:
                firefox_proc.terminate()
                try:
                    firefox_proc.wait(timeout=10)
                except Exception:
                    firefox_proc.kill()
        summary["wall_start"] = wall_total_start
        summary["wall_end"] = wall_now()
        summary["total_elapsed_s"] = round(time.perf_counter() - total_start, 4)
        summary["first_tab_count"] = (
            first_tabs["count"] if "first_tabs" in locals() and first_tabs else None)
        print("SUMMARY " + json.dumps(summary, ensure_ascii=False), flush=True)
        if args.log_json:
            Path(args.log_json).write_text(
                json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
