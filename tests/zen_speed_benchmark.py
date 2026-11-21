#!/usr/bin/env python3
"""Speed benchmark, Marionette against WebDriver BiDi, same tasks.

Purpose: fill the Zen control speed comparison with numbers that
were actually measured, on one machine, one browser, one day, with
both methods doing the same task against the same pages. The
browser here is Firefox as a stand-in for Zen, both speak both
protocols, and the script takes the binary path as an argument so
the identical benchmark runs against real Zen on the laptop.

Task per run, identical outcome for both methods:
session start, list tabs, navigate to the local fixture, read the
heading, put text into the input, click the button, read the
result text, navigate to example.com, read the title, end session.

Mechanism note, important for reading the results: Marionette
steps are WebDriver element commands through geckodriver. The
BiDi steps are protocol commands, with typing and clicking done as
DOM operations inside script.evaluate, set the value and dispatch
events, call click(). The outcomes are the same, the mechanisms
differ, and the comparison document says so wherever it quotes
these numbers.

Usage:
  python3 tests/zen_speed_benchmark.py \
      --browser /path/to/firefox-or-zen \
      --geckodriver /path/to/geckodriver \
      --runs 3 --out /tmp/benchmark.json

Exit code 0 when both methods complete every run.
"""

import argparse
import datetime
import importlib.util
import json
import socket
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

MARIONETTE_PORT = 2828
GECKO_PORT = 4444
BIDI_PORT = 9223
FIXTURE = (Path(__file__).parent / "fixtures"
           / "selenium_attach_fixture.html")


def wall_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def port_open(port):
    sock = socket.socket()
    sock.settimeout(0.5)
    try:
        return sock.connect_ex(("127.0.0.1", port)) == 0
    finally:
        sock.close()


def timed(steps, name, func):
    t0 = time.perf_counter()
    result = func()
    steps[name] = round(time.perf_counter() - t0, 4)
    return result


def load_zen_cli():
    path = Path(__file__).parent.parent / "scripts" / "zen_cli.py"
    spec = importlib.util.spec_from_file_location("zen_cli", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_marionette(geckodriver):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.firefox.service import Service
    steps = {}
    service = Service(executable_path=geckodriver, port=GECKO_PORT,
                      service_args=["--connect-existing",
                                    "--marionette-port",
                                    str(MARIONETTE_PORT)])
    driver = timed(steps, "session_start",
                   lambda: webdriver.Firefox(service=service))
    try:
        def list_tabs():
            handles = driver.window_handles
            return {"count": len(handles)}
        timed(steps, "list_tabs", list_tabs)
        timed(steps, "navigate_fixture",
              lambda: driver.get(FIXTURE.as_uri()))
        heading = timed(steps, "read_dom",
                        lambda: driver.find_element(By.ID, "heading").text)
        if heading != "Selenium Attach Fixture":
            raise RuntimeError(f"heading mismatch {heading!r}")

        def type_text():
            box = driver.find_element(By.ID, "q")
            box.clear()
            box.send_keys("clone2 bench")
            return box.get_attribute("value")
        timed(steps, "type", type_text)

        def click():
            driver.find_element(By.ID, "go").click()
            time.sleep(0.2)
            return driver.find_element(By.ID, "out").text
        out = timed(steps, "click_and_verify", click)
        if out != "clicked:clone2 bench":
            raise RuntimeError(f"out mismatch {out!r}")

        def navigate_web():
            driver.get("https://example.com/")
            return driver.title
        title = timed(steps, "navigate_example_com", navigate_web)
        if title != "Example Domain":
            raise RuntimeError(f"title mismatch {title!r}")
    finally:
        import urllib.request
        try:
            req = urllib.request.Request(
                f"http://127.0.0.1:{GECKO_PORT}/session/{driver.session_id}",
                method="DELETE")
            urllib.request.urlopen(req, timeout=10).read()
        except Exception:
            pass
        driver.service.stop()
    return steps


def run_bidi(zen_cli):
    steps = {}
    session = zen_cli.BidiSession(BIDI_PORT)
    timed(steps, "session_start", session.start)
    try:
        contexts = timed(steps, "list_tabs",
                         lambda: zen_cli.list_contexts(session))
        ctx = contexts[0]["context"]

        def nav(url):
            return session.call("browsingContext.navigate",
                                {"context": ctx, "url": url,
                                 "wait": "complete"})
        timed(steps, "navigate_fixture", lambda: nav(FIXTURE.as_uri()))

        def read(selector, prop="textContent"):
            result = zen_cli.evaluate(
                session, ctx,
                f"document.querySelector('{selector}').{prop}")
            return zen_cli.bidi_string(result)
        heading = timed(steps, "read_dom", lambda: read("#heading"))
        if heading != "Selenium Attach Fixture":
            raise RuntimeError(f"heading mismatch {heading!r}")

        def type_text():
            result = zen_cli.evaluate(
                session, ctx,
                "var b=document.querySelector('#q');"
                "b.value='clone2 bench';"
                "b.dispatchEvent(new Event('input',{bubbles:true}));"
                "b.value")
            return zen_cli.bidi_string(result)
        timed(steps, "type", type_text)

        def click():
            zen_cli.evaluate(session, ctx,
                             "document.querySelector('#go').click();'ok'")
            time.sleep(0.2)
            return read("#out")
        out = timed(steps, "click_and_verify", click)
        if out != "clicked:clone2 bench":
            raise RuntimeError(f"out mismatch {out!r}")

        timed(steps, "navigate_example_com",
              lambda: nav("https://example.com/"))
        title = zen_cli.bidi_string(
            zen_cli.evaluate(session, ctx, "document.title"))
        if title != "Example Domain":
            raise RuntimeError(f"title mismatch {title!r}")
    finally:
        session.end()
    return steps


def median_steps(runs):
    keys = runs[0].keys()
    return {k: round(statistics.median(r[k] for r in runs), 4)
            for k in keys}


def main():
    parser = argparse.ArgumentParser(description="Marionette vs BiDi speed")
    parser.add_argument("--browser", required=True)
    parser.add_argument("--geckodriver", default="geckodriver")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    profile = tempfile.mkdtemp(prefix="clone2-bench-profile-")
    proc = subprocess.Popen(
        [args.browser, "-marionette", "-profile", profile, "-no-remote",
         "--headless", "--remote-debugging-port", str(BIDI_PORT)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    report = {"wall_start": wall_now(), "browser": args.browser,
              "runs_per_method": args.runs, "ok": False}
    try:
        deadline = time.time() + 40
        while time.time() < deadline:
            if port_open(MARIONETTE_PORT) and port_open(BIDI_PORT):
                break
            time.sleep(0.25)
        else:
            raise RuntimeError("browser ports did not open in 40 s")

        zen_cli = load_zen_cli()
        marionette_runs, bidi_runs = [], []
        for i in range(args.runs):
            marionette_runs.append(run_marionette(args.geckodriver))
            print(f"marionette run {i + 1}: {marionette_runs[-1]}",
                  flush=True)
        for i in range(args.runs):
            bidi_runs.append(run_bidi(zen_cli))
            print(f"bidi run {i + 1}: {bidi_runs[-1]}", flush=True)
        report["marionette"] = {"runs": marionette_runs,
                                "median": median_steps(marionette_runs)}
        report["bidi"] = {"runs": bidi_runs,
                          "median": median_steps(bidi_runs)}
        report["ok"] = True
    except Exception as exc:
        report["failure"] = f"{type(exc).__name__}: {exc}"
        print(f"FAIL {report['failure']}", flush=True)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()
    report["wall_end"] = wall_now()
    print("MEDIAN marionette:", json.dumps(
        report.get("marionette", {}).get("median", {})), flush=True)
    print("MEDIAN bidi:", json.dumps(
        report.get("bidi", {}).get("median", {})), flush=True)
    if args.out:
        Path(args.out).write_text(json.dumps(report, indent=2),
                                  encoding="utf-8")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
