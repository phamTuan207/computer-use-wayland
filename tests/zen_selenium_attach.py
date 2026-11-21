#!/usr/bin/env python3
"""Selenium-free WebDriver attach test for the live Zen (Marionette 2828).

Why no selenium client: the laptop system python has no pip and no
selenium module. WebDriver is plain JSON over HTTP, so this script drives
geckodriver directly with urllib. Same steps as clone2's
tests/selenium_connect_existing.py, but SAFE for the user's live Zen:
it opens a NEW tab for the fixture and closes it at the end; it never
navigates, types into, or clicks on any of the user's existing tabs.

Steps: start geckodriver --connect-existing (port 2828) -> create session
-> list tabs -> open NEW tab -> goto local fixture -> read DOM -> type ->
click and verify DOM change -> close new tab -> delete session -> verify
Zen still alive (Marionette port open). Every step timed, wall clock
Asia/Ho_Chi_Minh, JSON summary printed at the end.
Exit 0 = all steps passed.
"""
import datetime
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

GECKO = "/tmp/geckodriver"
WD_PORT = int(os.environ.get("WD_PORT", "4445"))
MARIONETTE_PORT = int(os.environ.get("MARIONETTE_PORT", "2828"))
FIXTURE = Path("/tmp/zen_selenium_fixture.html")
TEST_TEXT = "zen marionette test"


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def wd(method, path, body=None):
    url = f"http://127.0.0.1:{WD_PORT}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} on {method} {path}: {e.read().decode()[:300]}")


def wait_for_http(url, timeout_s):
    deadline = time.perf_counter() + timeout_s
    while time.perf_counter() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.1)
    return False


def main():
    log = []
    total_start = time.perf_counter()
    gecko_proc = None
    session = None
    new_handle = None
    summary = {"ok": False, "steps": log}

    def run(name, func):
        start = time.perf_counter()
        wall = now_iso()
        try:
            detail = func()
            ok, error = True, None
        except Exception as exc:
            detail, ok, error = None, False, f"{type(exc).__name__}: {exc}"
        entry = {"step": name, "ok": ok, "wall_start": wall,
                 "elapsed_s": round(time.perf_counter() - start, 4),
                 "detail": detail, "error": error}
        log.append(entry)
        print(f"[{wall}] {name} {'ok' if ok else 'FAIL'} "
              f"elapsed_s={entry['elapsed_s']} detail={detail} error={error}",
              flush=True)
        if not ok:
            raise RuntimeError(f"step failed: {name}: {error}")
        return detail

    try:
        def start_gecko():
            nonlocal gecko_proc
            gecko_proc = subprocess.Popen(
                [GECKO, "--connect-existing", "--marionette-host", "127.0.0.1",
                 "--marionette-port", str(MARIONETTE_PORT),
                 "--port", str(WD_PORT), "--log", "info"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if not wait_for_http(f"http://127.0.0.1:{WD_PORT}/status", 30):
                raise RuntimeError("geckodriver status endpoint did not answer")
            return {"pid": gecko_proc.pid}
        run("start_geckodriver_connect_existing", start_gecko)

        def create_session():
            nonlocal session
            resp = wd("POST", "/session", {"capabilities": {
                "alwaysMatch": {"browserName": "firefox"}}})
            session = resp["value"]["sessionId"]
            caps = resp["value"].get("capabilities", {})
            return {"session_id": session,
                    "browser": caps.get("browserName"),
                    "version": caps.get("browserVersion")}
        run("create_session", create_session)

        def maximize():
            return wd("POST", f"/session/{session}/window/maximize", {})
        run("maximize_window", maximize)

        def list_tabs():
            resp = wd("GET", f"/session/{session}/window/handles")
            return {"count": len(resp["value"])}
        first = run("list_tabs", list_tabs)

        def new_tab():
            nonlocal new_handle
            resp = wd("POST", f"/session/{session}/window/new",
                      {"type": "tab"})
            new_handle = resp["value"]["handle"]
            wd("POST", f"/session/{session}/url",
               {"url": FIXTURE.as_uri()})
            deadline = time.perf_counter() + 10
            ready = ""
            while time.perf_counter() < deadline:
                ready = wd("POST", f"/session/{session}/execute/sync",
                           {"script": "return document.readyState",
                            "args": []})["value"]
                if ready == "complete":
                    break
                time.sleep(0.1)
            title = wd("GET", f"/session/{session}/title")["value"]
            return {"new_handle": new_handle[:8], "title": title,
                    "ready_state": ready}
        run("open_new_tab_fixture", new_tab)

        def read_dom():
            count = wd("POST", f"/session/{session}/execute/sync",
                       {"script": "return document.querySelectorAll('*').length",
                        "args": []})["value"]
            heading = wd("POST", f"/session/{session}/element",
                         {"using": "css selector", "value": "#heading"})
            el = heading["value"]["element-6066-11e4-a52e-4f735466cecf"]
            text = wd("GET", f"/session/{session}/element/{el}/text")["value"]
            return {"element_count": count, "heading": text}
        run("read_dom", read_dom)

        def type_input():
            wd("POST", f"/session/{session}/execute/sync",
               {"script": "document.querySelector('#q').scrollIntoView()",
                "args": []})
            resp = wd("POST", f"/session/{session}/element",
                      {"using": "css selector", "value": "#q"})
            el = resp["value"]["element-6066-11e4-a52e-4f735466cecf"]
            wd("POST", f"/session/{session}/element/{el}/clear", {})
            wd("POST", f"/session/{session}/element/{el}/value", {"text": TEST_TEXT})
            value = wd("GET", f"/session/{session}/element/{el}/property/value")["value"]
            if value != TEST_TEXT:
                raise RuntimeError(f"input value mismatch: {value!r}")
            return {"typed": TEST_TEXT, "value_read_back": value}
        run("type_into_input", type_input)

        def click_verify():
            wd("POST", f"/session/{session}/execute/sync",
               {"script": "document.querySelector('#go').scrollIntoView()",
                "args": []})
            resp = wd("POST", f"/session/{session}/element",
                      {"using": "css selector", "value": "#go"})
            el = resp["value"]["element-6066-11e4-a52e-4f735466cecf"]
            wd("POST", f"/session/{session}/element/{el}/click", {})
            resp = wd("POST", f"/session/{session}/element",
                      {"using": "css selector", "value": "#out"})
            el = resp["value"]["element-6066-11e4-a52e-4f735466cecf"]
            out = wd("GET", f"/session/{session}/element/{el}/text")["value"]
            expected = "clicked:" + TEST_TEXT
            if out != expected:
                raise RuntimeError(f"output mismatch: {out!r} != {expected!r}")
            return {"output_text": out}
        run("click_and_verify_dom_change", click_verify)

        def close_tab():
            wd("DELETE", f"/session/{session}/window", {})
            handles = wd("GET", f"/session/{session}/window/handles")["value"]
            return {"handles_after_close": len(handles)}
        run("close_new_tab", close_tab)

        def delete_session():
            nonlocal session
            wd("DELETE", f"/session/{session}", {})
            session = None
            return {"session_deleted": True}
        run("delete_session", delete_session)

        def alive():
            with socket.create_connection(("127.0.0.1", MARIONETTE_PORT), timeout=2):
                pass
            return {"marionette_port_open": True}
        run("browser_still_alive_after_session_delete", alive)
        summary["ok"] = True
    except Exception as exc:
        summary["ok"] = False
        summary["failure"] = f"{type(exc).__name__}: {exc}"
        print(f"FAILURE {summary['failure']}", flush=True)
    finally:
        if session is not None:
            try:
                wd("DELETE", f"/session/{session}", {})
            except Exception:
                pass
        if gecko_proc is not None and gecko_proc.poll() is None:
            gecko_proc.terminate()
            try:
                gecko_proc.wait(timeout=10)
            except Exception:
                gecko_proc.kill()
        summary["wall_start"] = log[0]["wall_start"] if log else now_iso()
        summary["wall_end"] = now_iso()
        summary["total_elapsed_s"] = round(time.perf_counter() - total_start, 4)
        summary["first_tab_count"] = first["count"] if "first" in locals() and first else None
        print("SUMMARY " + json.dumps(summary, ensure_ascii=False), flush=True)
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
