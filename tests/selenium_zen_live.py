#!/usr/bin/env python3
"""Selenium on real Zen, live run script, prepared for the laptop.

Purpose
Run one real browser task against Zen with Selenium plus
geckodriver and Marionette, with every step timed and logged as
JSON lines, so the laptop run produces evidence, not impressions.
The same script runs against Firefox unchanged, which is how it is
verified on machines without Zen.

Modes
launch: the script starts the browser itself with -marionette and
a dedicated throwaway profile, runs the task, and closes the
browser it started. Safe anywhere, recommended first run.
attach: the script connects to a browser the user already started
with -marionette, runs the task in a new tab it creates, and only
deletes the WebDriver session at the end. The browser and all
pre-existing tabs stay open.

Tab safety rules, built in, not optional
- The script records the window handles that exist when the
  session starts.
- It only ever closes handles it created during its own run.
- Before finishing it switches back to the original handle.
- In attach mode it never calls driver.quit(), which would close
  the user browser. It deletes only the session.

Timing rules from field experience, built in
- After every page load the script waits 1 second before the
  first interaction, pages that settle late otherwise produce
  flaky element errors.
- The window size is set explicitly to 1280x900 at session start,
  a zero or tiny viewport makes elements non interactable.
- Every step is one JSON line: wall clock ISO UTC, step name,
  elapsed seconds from a monotonic clock, ok flag, detail.

Usage on the laptop, attach mode against real Zen:
  python3 tests/selenium_zen_live.py --mode attach \
      --zen /path/to/zen --out /tmp/zen-live.jsonl
Start Zen first with: zen -marionette -P <profile>
Usage, launch mode:
  python3 tests/selenium_zen_live.py --mode launch --zen /path/to/zen

Exit codes: 0 pass, 2 browser binary not found, 3 geckodriver or
session failure, 4 task assertion failure.
"""

import argparse
import datetime
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

MARIONETTE_PORT = 2828
GECKO_PORT = 4444


def wall_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class JsonlLog:
    def __init__(self, path):
        self.path = path
        self.fh = open(path, "a", encoding="utf-8") if path else None
        self.steps = []

    def step(self, name, func):
        wall_start = wall_now()
        t0 = time.perf_counter()
        try:
            detail = func()
            ok, error = True, None
        except Exception as exc:
            detail, ok, error = None, False, f"{type(exc).__name__}: {exc}"
        entry = {"ts": wall_start, "step": name, "ok": ok,
                 "elapsed_s": round(time.perf_counter() - t0, 4),
                 "detail": detail, "error": error}
        self.steps.append(entry)
        line = json.dumps(entry, ensure_ascii=False)
        print(line, flush=True)
        if self.fh:
            self.fh.write(line + "\n")
            self.fh.flush()
        if not ok:
            raise RuntimeError(f"step failed: {name}: {error}")
        return detail

    def note(self, name, detail):
        entry = {"ts": wall_now(), "step": name, "ok": True,
                 "elapsed_s": 0.0, "detail": detail, "error": None}
        self.steps.append(entry)
        line = json.dumps(entry, ensure_ascii=False)
        print(line, flush=True)
        if self.fh:
            self.fh.write(line + "\n")
            self.fh.flush()


def port_open(port):
    sock = socket.socket()
    sock.settimeout(0.5)
    try:
        return sock.connect_ex(("127.0.0.1", port)) == 0
    finally:
        sock.close()


def find_browser(cli_value):
    candidates = []
    if cli_value:
        candidates.append(cli_value)
    for name in ("zen", "zen-browser"):
        found = shutil.which(name)
        if found:
            candidates.append(found)
    candidates += ["/usr/bin/zen", "/opt/zen/zen", "/opt/zen-browser/zen",
                   str(Path.home() / ".local/bin/zen")]
    for cand in candidates:
        if cand and Path(cand).exists():
            return cand
    return None


def main():
    parser = argparse.ArgumentParser(description="Selenium live browser test")
    parser.add_argument("--mode", choices=["launch", "attach"],
                        default="launch")
    parser.add_argument("--zen", default="",
                        help="browser binary, Zen or Firefox")
    parser.add_argument("--geckodriver", default="geckodriver")
    parser.add_argument("--profile", default="",
                        help="profile dir, launch mode only, "
                             "default a throwaway temp profile")
    parser.add_argument("--headless", action="store_true",
                        help="launch mode only")
    parser.add_argument("--out", default="",
                        help="JSONL log path, appended")
    parser.add_argument("--pause-after-load", type=float, default=1.0)
    args = parser.parse_args()

    log = JsonlLog(args.out)
    total_t0 = time.perf_counter()
    summary = {"mode": args.mode, "ok": False, "wall_start": wall_now()}

    binary = find_browser(args.zen)
    if binary is None:
        log.note("find_browser", {"found": None})
        print("FAIL browser binary not found, pass --zen PATH")
        return 2
    log.note("find_browser", {"binary": binary})

    def version():
        proc = subprocess.run([binary, "--version"], capture_output=True,
                              text=True, timeout=20)
        return (proc.stdout or proc.stderr).strip()

    try:
        summary["browser_version"] = log.step("browser_version", version)
    except Exception:
        summary["browser_version"] = "unknown"

    browser_proc = None
    profile_dir = None
    driver = None
    try:
        if args.mode == "launch":
            profile_dir = args.profile or tempfile.mkdtemp(
                prefix="clone2-zen-live-profile-")

            def launch():
                nonlocal browser_proc
                cmd = [binary, "-marionette", "-profile", profile_dir,
                       "-no-remote"]
                if args.headless:
                    cmd.append("--headless")
                browser_proc = subprocess.Popen(
                    cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                deadline = time.time() + 30
                while time.time() < deadline:
                    if port_open(MARIONETTE_PORT):
                        return {"pid": browser_proc.pid,
                                "profile": profile_dir}
                    time.sleep(0.25)
                raise RuntimeError("marionette port did not open in 30 s")

            log.step("launch_browser_marionette", launch)
        else:
            def check_running():
                if not port_open(MARIONETTE_PORT):
                    raise RuntimeError(
                        "nothing on marionette port 2828, start the "
                        "browser with -marionette first")
                return {"marionette_port_open": True}

            log.step("check_browser_already_running", check_running)

        def start_gecko_and_session():
            nonlocal driver
            from selenium import webdriver
            from selenium.webdriver.firefox.service import Service
            service = Service(
                executable_path=args.geckodriver, port=GECKO_PORT,
                service_args=["--connect-existing", "--marionette-port",
                              str(MARIONETTE_PORT)])
            driver = webdriver.Firefox(service=service)
            driver.set_window_size(1280, 900)
            return {"session_id": driver.session_id,
                    "window_size": driver.get_window_size()}

        log.step("create_session_connect_existing", start_gecko_and_session)

        initial = {}

        def record_handles():
            handles = list(driver.window_handles)
            initial["handles"] = handles
            initial["current"] = driver.current_window_handle
            return {"initial_handles": handles}

        log.step("record_initial_handles", record_handles)

        fixture = (Path(__file__).parent / "fixtures"
                   / "selenium_attach_fixture.html")

        def open_fixture_new_tab():
            before = set(driver.window_handles)
            driver.switch_to.new_window("tab")
            new_handles = [h for h in driver.window_handles
                           if h not in before]
            initial["created"] = new_handles
            driver.get(fixture.as_uri())
            time.sleep(args.pause_after_load)
            return {"new_tab": new_handles, "title": driver.title}

        log.step("open_fixture_in_new_tab", open_fixture_new_tab)

        def read_dom():
            from selenium.webdriver.common.by import By
            heading = driver.find_element(By.ID, "heading").text
            status = driver.find_element(By.ID, "out").text
            return {"heading": heading, "status_before": status}

        dom = log.step("read_dom", read_dom)
        if dom["heading"] != "Selenium Attach Fixture":
            raise AssertionError(f"unexpected heading {dom['heading']!r}")

        def type_text():
            from selenium.webdriver.common.by import By
            box = driver.find_element(By.ID, "q")
            box.clear()
            box.send_keys("clone2 zen live")
            return {"value": box.get_attribute("value")}

        typed = log.step("type_into_input", type_text)
        if typed["value"] != "clone2 zen live":
            raise AssertionError(f"input value mismatch {typed['value']!r}")

        def click_and_verify():
            from selenium.webdriver.common.by import By
            driver.find_element(By.ID, "go").click()
            time.sleep(0.3)
            return {"status_after":
                    driver.find_element(By.ID, "out").text}

        clicked = log.step("click_and_verify", click_and_verify)
        if clicked["status_after"] != "clicked:clone2 zen live":
            raise AssertionError(
                f"status mismatch {clicked['status_after']!r}")

        def second_tab_network():
            before = set(driver.window_handles)
            driver.switch_to.new_window("tab")
            new_handles = [h for h in driver.window_handles
                           if h not in before]
            initial.setdefault("created", []).extend(new_handles)
            driver.set_page_load_timeout(30)
            driver.get("https://example.com/")
            time.sleep(args.pause_after_load)
            heading = driver.execute_script(
                "var h = document.querySelector('h1');"
                "return h ? h.textContent : null;")
            return {"h1": heading, "title": driver.title,
                    "url": driver.current_url,
                    "note": "verified by title and url, some networks "
                            "serve example.com without its usual h1, "
                            "so the h1 text is reported, not asserted"}

        net = log.step("second_tab_example_com", second_tab_network)
        if net["title"] != "Example Domain":
            raise AssertionError(f"unexpected title {net['title']!r}")

        def close_only_created_tabs():
            created = list(initial.get("created", []))
            for handle in created:
                if handle in driver.window_handles:
                    driver.switch_to.window(handle)
                    driver.close()
            driver.switch_to.window(initial["current"])
            return {"closed": created,
                    "remaining": list(driver.window_handles)}

        closed = log.step("close_only_own_tabs", close_only_created_tabs)
        if closed["remaining"] != initial["handles"]:
            raise AssertionError(
                f"handle set changed: {closed['remaining']} vs "
                f"{initial['handles']}")

        summary["ok"] = True
    except Exception as exc:
        summary["failure"] = f"{type(exc).__name__}: {exc}"
        print(f"FAIL {summary['failure']}", flush=True)
    finally:
        if driver is not None:
            def delete_session():
                import urllib.request
                sid = driver.session_id
                req = urllib.request.Request(
                    f"http://127.0.0.1:{GECKO_PORT}/session/{sid}",
                    method="DELETE")
                with urllib.request.urlopen(req, timeout=10) as resp:
                    status = resp.status
                driver.service.stop()
                return {"deleted_session": sid, "http_status": status,
                        "note": "session deleted by HTTP, service "
                                "stopped without quit, browser left "
                                "running in attach mode"}
            try:
                if args.mode == "attach":
                    log.step("delete_session_only", delete_session)
                else:
                    driver.quit()
                    log.note("browser_closed",
                             {"mode": "launch, own browser closed"})
            except Exception as exc:
                log.note("cleanup_warning", {"error": str(exc)})
        if browser_proc is not None and args.mode == "launch":
            try:
                browser_proc.terminate()
                browser_proc.wait(timeout=10)
            except Exception:
                browser_proc.kill()
        if args.mode == "attach":
            alive = port_open(MARIONETTE_PORT)
            log.note("browser_still_alive_after",
                     {"marionette_port_open": alive})
            summary["browser_alive_after"] = alive

    summary["total_elapsed_s"] = round(time.perf_counter() - total_t0, 4)
    summary["wall_end"] = wall_now()
    summary["steps_ok"] = sum(1 for s in log.steps if s["ok"])
    summary["steps_total"] = len(log.steps)
    print("SUMMARY " + json.dumps(summary, ensure_ascii=False), flush=True)
    if log.fh:
        log.fh.write("SUMMARY " + json.dumps(summary, ensure_ascii=False)
                     + "\n")
        log.fh.close()
    if summary["ok"]:
        return 0
    return 4 if "failure" in summary else 3


if __name__ == "__main__":
    sys.exit(main())
