#!/usr/bin/env python3
"""Live Zen runner for the 20 realistic tests (Worker P, 21/11/2026).

Runs the clone1 (t01-t10) and fcc-k (test-01..10) realistic tests against
the LIVE Zen on the laptop via geckodriver --connect-existing (Marionette
2828). Stdlib only, no selenium module (the laptop has no pip).

Rules:
- One WebDriver session per test, ALWAYS deleted in a finally block
  (BiDi and Marionette share a single session slot; a leak blocks all
  remote control until Zen restarts).
- A NEW tab per test; user tabs are never navigated, typed into, or
  clicked. Test tabs are closed at the end of each test.
- Fixtures are served from a loopback HTTP server started by this script
  (same origin, so localStorage and multi-tab/popup sharing work).
- End states are verified by reading the DOM directly. The fcc-k
  __fcckVerify() functions are NEVER used as oracles: they self-simulate
  the intended flow and always pass, so they prove nothing about an
  agent run. See the run report for the full finding.
- Per-step wall time is the DOM-driver time (machine time). It is the
  floor under any agent run, not agent think time. Agent think time is
  measured separately by hand-driving a sample test.

Usage (on the laptop, from the repo root):
  python3 tests/realistic/run_live.py t01
  python3 tests/realistic/run_live.py all
  python3 tests/realistic/run_live.py f01 f02
Output: one JSON summary line per test on stdout, plus a JSONL step log
at tests/realistic/live-run-20261121.jsonl (relative to the server root
copy) and /tmp/worker-p-live.jsonl.
"""
import datetime
import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

GECKO = "/tmp/geckodriver"
WD_PORT = int(os.environ.get("WD_PORT", "4445"))
MARIONETTE_PORT = int(os.environ.get("MARIONETTE_PORT", "2828"))
SERVER_ROOT = Path(os.environ.get("LIVE_SERVER_ROOT", "/tmp/worker-p-server"))
SERVER_PORT = int(os.environ.get("LIVE_SERVER_PORT", "8765"))
UPLOADS = Path("/tmp/worker-p-uploads")
DOWNLOADS = Path.home() / "Downloads"
LOG_PATH = Path(os.environ.get("LIVE_LOG", "/tmp/worker-p-live.jsonl"))
EL_KEY = "element-6066-11e4-a52e-4f735466cecf"


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def checksum(buf):
    h = 0
    for b in buf:
        h = ((h * 31) + b) & 0xFFFFFFFF
    return format(h, "08x")


def log_step(test, step, op, elapsed_ms, ok, detail=None, error=None):
    rec = {"ts": now_iso(), "test": test, "step": step, "op": op,
           "elapsed_ms": round(elapsed_ms, 1), "ok": ok,
           "detail": detail, "error": error}
    with open(LOG_PATH, "a") as f:
        # default=str: details may hold Path objects (downloads).
        f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
    return rec


class WD:
    """Minimal WebDriver client over geckodriver --connect-existing."""

    def __init__(self):
        self.proc = None
        self.session = None
        self.opened_tabs = []

    def __enter__(self):
        self.proc = subprocess.Popen(
            [GECKO, "--connect-existing", "--marionette-host", "127.0.0.1",
             "--marionette-port", str(MARIONETTE_PORT),
             "--port", str(WD_PORT), "--log", "warn"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.perf_counter() + 30
        while time.perf_counter() < deadline:
            try:
                with urllib.request.urlopen(
                        f"http://127.0.0.1:{WD_PORT}/status", timeout=2) as r:
                    if r.status == 200:
                        break
            except Exception:
                time.sleep(0.1)
        else:
            self._cleanup()
            raise RuntimeError("geckodriver status endpoint did not answer")
        resp = self._wd("POST", "/session", {"capabilities": {
            "alwaysMatch": {"browserName": "firefox"}}})
        self.session = resp["value"]["sessionId"]
        # No maximize here: the live Zen is already 1863x1176, and
        # maximize is an unneeded variable (its effect was never
        # isolated; probe v3's failure is fully explained by the
        # missing settle delay, see goto()).
        return self

    def __exit__(self, *exc):
        self._cleanup()
        return False

    def _cleanup(self):
        if self.session is not None:
            # Close tabs this session opened (test tabs only; user tabs
            # are never in opened_tabs). Best effort; a tab with an open
            # alert may refuse, and the session delete below still runs.
            for handle in list(self.opened_tabs):
                try:
                    self.switch(handle)
                    self._wd("DELETE", self._s("/window"), {})
                except Exception:
                    pass
            self.opened_tabs = []
            try:
                self._wd("DELETE", f"/session/{self.session}", {})
            except Exception:
                pass
            self.session = None
        if self.proc is not None and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=10)
            except Exception:
                self.proc.kill()
            self.proc = None

    def _wd(self, method, path, body=None):
        url = f"http://127.0.0.1:{WD_PORT}{path}"
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            raise RuntimeError(
                f"HTTP {e.code} on {method} {path}: "
                f"{e.read().decode(errors='replace')[:300]}")

    def _s(self, path):
        return f"/session/{self.session}{path}"

    def eval(self, script, args=None):
        return self._wd("POST", self._s("/execute/sync"),
                        {"script": script, "args": args or []})["value"]

    def handles(self):
        return self._wd("GET", self._s("/window/handles"))["value"]

    def switch(self, handle):
        self._wd("POST", self._s("/window"), {"handle": handle})
        # Settle: a freshly selected tab needs a beat before Marionette's
        # interactability check passes (probe v2 vs v4, 21/11).
        time.sleep(0.5)

    def new_tab(self, url):
        resp = self._wd("POST", self._s("/window/new"), {"type": "tab"})
        handle = resp["value"]["handle"]
        self.opened_tabs.append(handle)
        # CRITICAL: geckodriver --connect-existing does NOT switch the
        # current window to the new tab (proven 21/11: current handle
        # stays on the old tab after window/new). Without this switch,
        # goto/type/click all land in the PREVIOUSLY current tab (a user
        # tab), and close_tab would close that user tab. Always switch.
        self.switch(handle)
        current = self._wd("GET", self._s("/window"))["value"]
        if current != handle:
            raise RuntimeError(
                f"window switch failed: current {current[:8]} != new {handle[:8]}")
        self.goto(url)
        return handle

    def scroll_into_view(self, css):
        self.eval("const el = document.querySelector(arguments[0]);"
                  " if (el) el.scrollIntoView({block: 'center'});", [css])

    def close_tab(self):
        self._wd("DELETE", self._s("/window"), {})

    def goto(self, url):
        self._wd("POST", self._s("/url"), {"url": url})
        self.wait_ready()
        # Settle: readyState == complete is NOT enough. Probe v2 (1s sleep
        # after goto) passes element clear/type; probe v4 (no sleep) fails
        # with "could not be scrolled into view" although the element has
        # a valid rect and the tab reports visible + focused. The tab needs
        # a paint before Marionette's interactability check passes.
        time.sleep(1.0)

    def refresh(self):
        self._wd("POST", self._s("/refresh"), {})
        self.wait_ready()
        # Same settle as goto(): after a reload, JS listeners / init
        # scripts lag behind readyState. Without this, the first element
        # interaction fails ("could not be scrolled into view") and
        # select/change handlers appear not to fire (t04, t05, t08, 21/11).
        time.sleep(1.0)

    def wait_ready(self, timeout=10):
        deadline = time.perf_counter() + timeout
        while time.perf_counter() < deadline:
            try:
                if self.eval("return document.readyState") == "complete":
                    return True
            except Exception:
                pass
            time.sleep(0.1)
        raise RuntimeError("page did not reach readyState complete")

    def wait_for(self, js_cond, timeout=10, desc="condition"):
        deadline = time.perf_counter() + timeout
        while time.perf_counter() < deadline:
            try:
                if self.eval(f"return !!({js_cond})"):
                    return True
            except Exception:
                pass
            time.sleep(0.1)
        raise RuntimeError(f"timeout waiting for {desc}: {js_cond}")

    def find(self, css):
        resp = self._wd("POST", self._s("/element"),
                        {"using": "css selector", "value": css})
        return resp["value"][EL_KEY]

    def click(self, css):
        self.scroll_into_view(css)
        el = self.find(css)
        self._wd("POST", self._s(f"/element/{el}/click"), {})

    def click_js(self, js_expr):
        """Click an element located by arbitrary JS (returns the element)."""
        self.eval(f"({js_expr}).click()")

    def type_text(self, css, text):
        self.scroll_into_view(css)
        el = self.find(css)
        self._wd("POST", self._s(f"/element/{el}/clear"), {})
        self._wd("POST", self._s(f"/element/{el}/value"), {"text": text})

    def set_file(self, css, path):
        self.scroll_into_view(css)
        el = self.find(css)
        self._wd("POST", self._s(f"/element/{el}/value"),
                 {"text": str(path)})

    def text(self, css):
        el = self.find(css)
        return self._wd("GET", self._s(f"/element/{el}/text"))["value"]

    def value(self, css):
        el = self.find(css)
        return self._wd("GET",
                        self._s(f"/element/{el}/property/value"))["value"]

    def visible(self, css):
        return self.eval(
            "const el = document.querySelector(arguments[0]);"
            " if (!el) return false;"
            " const r = el.getBoundingClientRect();"
            " const cs = getComputedStyle(el);"
            " return r.width > 0 && r.height > 0 && cs.display !== 'none'"
            " && cs.visibility !== 'hidden';", [css])

    def alert_text(self):
        return self._wd("GET", self._s("/alert/text"))["value"]

    def alert_accept(self):
        self._wd("POST", self._s("/alert/accept"), {})

    def alert_dismiss(self):
        self._wd("POST", self._s("/alert/dismiss"), {})

    def alert_send(self, text):
        self._wd("POST", self._s("/alert/text"), {"text": text})


class Runner:
    def __init__(self, test_id, base_url):
        self.test = test_id
        self.base = base_url
        self.failures = []
        self.details = {}
        self.t0 = time.perf_counter()
        self.wall_start = now_iso()

    def step(self, name, op, fn):
        start = time.perf_counter()
        try:
            detail = fn()
            ok, error = True, None
        except Exception as exc:
            detail, ok, error = None, False, f"{type(exc).__name__}: {exc}"
        ms = (time.perf_counter() - start) * 1000
        log_step(self.test, name, op, ms, ok, detail, error)
        print(f"[{self.test}] {name} {'ok' if ok else 'FAIL'} "
              f"{ms:.0f}ms detail={detail} error={error}", flush=True)
        if not ok:
            self.failures.append(f"{name}: {error}")
            raise RuntimeError(f"step failed: {name}: {error}")
        return detail

    def check(self, name, cond, detail=""):
        if not cond:
            self.failures.append(f"{name}: {detail}")
            print(f"[{self.test}] CHECK FAIL {name}: {detail}", flush=True)
        else:
            print(f"[{self.test}] CHECK ok {name}: {detail}", flush=True)
        return cond

    def summary(self):
        return {"test": self.test, "pass": len(self.failures) == 0,
                "failures": self.failures, "details": self.details,
                "started_at": self.wall_start, "finished_at": now_iso(),
                "elapsed_ms": round((time.perf_counter() - self.t0) * 1000)}


def start_server():
    # Reuse an already-listening server on the port (e.g. the persistent
    # python3 -m http.server started for probing). Otherwise start one.
    try:
        with urllib.request.urlopen(
                f"http://127.0.0.1:{SERVER_PORT}/clone1/t01-upload-single/fixture.html",
                timeout=2) as resp:
            if resp.status == 200:
                print(f"reusing live server at http://127.0.0.1:{SERVER_PORT}",
                      flush=True)
                return None, f"http://127.0.0.1:{SERVER_PORT}"
    except Exception:
        pass
    handler = partial(SimpleHTTPRequestHandler, directory=str(SERVER_ROOT))
    httpd = ThreadingHTTPServer(("127.0.0.1", SERVER_PORT), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd, f"http://127.0.0.1:{SERVER_PORT}"


def wait_download(name, timeout=15):
    deadline = time.perf_counter() + timeout
    target = DOWNLOADS / name
    while time.perf_counter() < deadline:
        if target.exists() and target.stat().st_size > 0:
            time.sleep(0.3)
            return target
        time.sleep(0.2)
    raise RuntimeError(f"download {name} did not appear in {DOWNLOADS}")


def clear_download(name):
    target = DOWNLOADS / name
    if target.exists():
        target.unlink()
    for p in DOWNLOADS.glob(name + " *"):
        p.unlink()


# ---------------- clone1 tests (t01-t10) ----------------

def run_t01(r, d):
    url = r.base + "/clone1/t01-upload-single/fixture.html"
    content = b"polygon statement\nline two\nline three\n"
    f = UPLOADS / "t01-statement.txt"
    f.write_bytes(content)
    exp_sum, exp_size = checksum(content), len(content)
    r.details.update({"file": f.name, "size": exp_size, "checksum": exp_sum})
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    r.step("fill title", "type", lambda: d.type_text("#title", "Sample Problem"))
    r.step("choose file", "set_file", lambda: d.set_file("#file", f))
    r.step("click upload", "click", lambda: d.click("#upload"))
    r.step("wait confirmation", "wait",
           lambda: d.wait_for(
               "document.querySelector('#result') && "
               "document.querySelector('#result').textContent !== ''",
               10, "#result non-empty"))
    text = r.step("read confirmation", "text", lambda: d.text("#result"))
    r.details["confirmation"] = text
    r.check("name in confirmation", f.name in text, text)
    r.check("size in confirmation", f"{exp_size} bytes" in text, text)
    r.check("checksum in confirmation", exp_sum in text, text)
    r.check("title in confirmation", "Sample Problem" in text, text)


def run_t02(r, d):
    url = r.base + "/clone1/t02-upload-multi-error/fixture.html"
    a, b, big = UPLOADS / "t02-a.txt", UPLOADS / "t02-b.txt", UPLOADS / "t02-big.txt"
    a.write_bytes(b"test one\n")
    b.write_bytes(b"test two\n")
    big.write_bytes(b"x" * (100 * 1024))
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    r.step("choose 3 files", "set_file",
           lambda: d.set_file("#files", f"{a}\n{b}\n{big}"))
    r.step("click upload all", "click", lambda: d.click("#upload"))
    r.step("wait one error row", "wait",
           lambda: d.wait_for(
               "document.querySelectorAll('#rows .err').length === 1",
               10, "exactly 1 .err row"))
    rows = r.step("read rows", "text", lambda: d.text("#rows"))
    r.details["rowsAfterFirstUpload"] = " ".join(rows.split())
    r.check("large row mentions 64 KB limit", "64 KB limit" in rows, rows)
    r.check("exactly two ok rows", rows.count("ok") == 2, rows)
    r.step("remove failed", "click", lambda: d.click("#remove-failed"))
    r.step("retry remaining", "click", lambda: d.click("#retry"))
    r.step("wait final confirmation", "wait",
           lambda: d.wait_for(
               "document.querySelector('#result') && "
               "document.querySelector('#result').textContent !== ''",
               10, "#result non-empty"))
    res = r.step("read final result", "text", lambda: d.text("#result"))
    r.details["finalResult"] = res
    r.check("final lists t02-a.txt", "t02-a.txt" in res, res)
    r.check("final lists t02-b.txt", "t02-b.txt" in res, res)
    r.check("final omits t02-big.txt", "t02-big.txt" not in res, res)


def run_t03(r, d):
    url = r.base + "/clone1/t03-long-form/fixture.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    r.step("submit empty", "click", lambda: d.click("#submit"))
    r.step("wait errors", "wait",
           lambda: d.wait_for(
               "document.querySelector('#errors') && "
               "document.querySelector('#errors').textContent !== ''",
               10, "#errors non-empty"))
    errors = r.step("read errors", "text", lambda: d.text("#errors"))
    r.details["emptySubmitErrors"] = errors
    for word in ["Title", "Statement", "Sample input", "Sample output"]:
        r.check(f"empty error names {word}", word in errors, errors)
    values = {"#title": "Long Form Problem", "#short": "lfp", "#time": "2",
              "#memory": "256", "#tags": "graphs, shortest path",
              "#statement": "Find the shortest path.",
              "#inputfmt": "First line has n and m.",
              "#outputfmt": "One integer, the distance.",
              "#samplein": "3 2\n1 2\n2 3", "#sampleout": "2",
              "#notes": "Draft for review."}
    for sel, val in values.items():
        r.step(f"fill {sel}", "type", lambda s=sel, v=val: d.type_text(s, v))
    r.step("select difficulty medium", "select",
           lambda: d.eval("document.querySelector('#difficulty').value='medium';"
                          "document.querySelector('#difficulty').dispatchEvent(new Event('change'));"))
    r.step("select checker token", "select",
           lambda: d.eval("document.querySelector('#checker').value='token';"
                          "document.querySelector('#checker').dispatchEvent(new Event('change'));"))
    r.step("submit filled", "click", lambda: d.click("#submit"))
    r.step("wait summary", "wait",
           lambda: d.wait_for(
               "document.querySelector('#summary') && "
               "document.querySelector('#summary').textContent !== ''",
               10, "#summary non-empty"))
    summary = r.step("read summary", "text", lambda: d.text("#summary"))
    r.details["summary"] = summary
    r.check("summary has title", "Long Form Problem" in summary, summary)
    r.check("summary confirms 14 fields", "14 fields" in summary, summary)
    leftover = r.step("read leftover errors", "text", lambda: d.text("#errors"))
    r.check("no errors after success", leftover.strip() == "", leftover)


def run_t04(r, d):
    url = r.base + "/clone1/t04-long-form-draft/fixture.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    r.step("clear storage + reload", "eval",
           lambda: (d.eval("localStorage.clear()"), d.refresh()))
    vis = r.step("batch hides interactive fields", "visible",
                 lambda: d.visible("#interactive-fields"))
    r.details["batchExtraVisible"] = vis
    r.check("interactive fields hidden for batch", not vis, str(vis))
    r.step("select interactive type", "select",
           lambda: d.eval("document.querySelector('#ptype').value='interactive';"
                          "document.querySelector('#ptype').dispatchEvent(new Event('change'));"))
    vis2 = r.step("interactive shows extra fields", "visible",
                  lambda: d.visible("#interactive-fields"))
    r.details["interactiveExtraVisible"] = vis2
    r.check("interactive fields visible", vis2, str(vis2))
    for sel, val in [("#title", "Interactive Guessing Problem"),
                     ("#interactor", "Judge answers each query."),
                     ("#qlimit", "30"),
                     ("#statement", "Guess the hidden number.")]:
        r.step(f"fill {sel}", "type", lambda s=sel, v=val: d.type_text(s, v))
    r.step("save draft", "click", lambda: d.click("#save-draft"))
    r.step("wait draft msg", "wait",
           lambda: d.wait_for(
               "document.querySelector('#draft-msg') && "
               "document.querySelector('#draft-msg').textContent !== ''",
               10, "#draft-msg non-empty"))
    r.step("reload page", "eval", lambda: d.refresh())
    restored = r.step("read restored values", "eval",
                      lambda: d.eval("return {title: document.querySelector('#title').value,"
                                     "interactor: document.querySelector('#interactor').value,"
                                     "qlimit: document.querySelector('#qlimit').value,"
                                     "statement: document.querySelector('#statement').value}"))
    r.details["restored"] = restored
    r.check("draft title restored",
            restored["title"] == "Interactive Guessing Problem", str(restored))
    r.check("draft interactor restored",
            restored["interactor"] == "Judge answers each query.", str(restored))
    r.check("draft qlimit restored", restored["qlimit"] == "30", str(restored))
    r.check("draft statement restored",
            restored["statement"] == "Guess the hidden number.", str(restored))
    r.step("submit", "click", lambda: d.click("#submit"))
    r.step("wait result", "wait",
           lambda: d.wait_for(
               "document.querySelector('#result') && "
               "document.querySelector('#result').textContent !== ''",
               10, "#result non-empty"))
    res = r.step("read result", "text", lambda: d.text("#result"))
    r.details["result"] = res
    r.check("success mentions title", "Interactive Guessing Problem" in res, res)


def run_t05(r, d):
    url = r.base + "/clone1/t05-multi-tab/fixture.html"
    list_tab = r.step("open list", "goto", lambda: d.new_tab(url))
    r.step("clear storage + reload", "eval",
           lambda: (d.eval("localStorage.clear()"), d.refresh()))
    count = r.step("count rows", "eval",
                   lambda: d.eval("return document.querySelectorAll('#rows tr').length"))
    r.details["initialRowCount"] = count
    r.check("5 rows at start", count == 5, str(count))
    before = r.step("read titles before", "eval",
                    lambda: d.eval("return [...document.querySelectorAll('#rows tr .title')].map(e => e.textContent)"))
    r.details["titlesBefore"] = before
    handles_before = d.handles()
    r.step("open problem 2 in new tab", "click",
           lambda: d.click("#rows tr:nth-child(2) a"))
    r.step("wait for detail tab", "wait",
           lambda: _wait_handles(d, len(handles_before) + 1))
    detail_tab = [h for h in d.handles() if h not in handles_before][0]
    r.step("switch to detail tab", "switch",
           lambda: d.switch(detail_tab))
    # The detail tab navigated AFTER the click, so it needs the full
    # post-navigation settle (switch()'s 0.5s is not enough for a tab
    # that is still painting its first load; t05 failed here 21/11).
    r.step("settle detail tab", "wait",
           lambda: (d.wait_ready(), time.sleep(1.0)))
    title0 = r.step("read detail title", "value", lambda: d.value("#title"))
    r.details["detailInitialTitle"] = title0
    r.check("detail opens Problem Two", title0 == "Problem Two", str(title0))
    r.step("edit title", "type",
           lambda: d.type_text("#title", "Edited Title Two"))
    r.step("save", "click", lambda: d.click("#save"))
    r.step("wait saved msg", "wait",
           lambda: d.wait_for(
               "document.querySelector('#saved') && "
               "document.querySelector('#saved').textContent !== ''",
               10, "#saved non-empty"))
    r.step("close detail tab", "close", lambda: d.close_tab())
    r.step("switch back to list", "switch",
           lambda: d.switch(list_tab))
    r.step("refresh list", "click", lambda: d.click("#refresh"))
    after = r.step("read titles after", "eval",
                   lambda: d.eval("return [...document.querySelectorAll('#rows tr .title')].map(e => e.textContent)"))
    r.details["titlesAfter"] = after
    r.check("row 2 shows edited title", after[1] == "Edited Title Two", str(after))
    for i in [0, 2, 3, 4]:
        r.check(f"row {i + 1} unchanged", after[i] == before[i],
                f"before={before[i]} after={after[i]}")


def _wait_handles(d, n, timeout=10):
    deadline = time.perf_counter() + timeout
    while time.perf_counter() < deadline:
        if len(d.handles()) >= n:
            return True
        time.sleep(0.1)
    raise RuntimeError(f"only {len(d.handles())} handles, expected >= {n}")


def run_t06(r, d):
    url = r.base + "/clone1/t06-popup-dialog/fixture.html"
    main_tab = r.step("open fixture", "goto", lambda: d.new_tab(url))
    r.step("click show alert", "click", lambda: d.click("#alert-btn"))
    r.step("accept alert", "alert_accept", lambda: d.alert_accept())
    r.step("wait alert outcome", "wait",
           lambda: d.wait_for(
               "document.getElementById('out-alert').textContent !== ''",
               10, "#out-alert non-empty"))
    a = r.step("read alert outcome", "text", lambda: d.text("#out-alert"))
    r.details["alert"] = a
    r.check("alert recorded accepted", a == "alert accepted", a)
    r.step("click confirm (accept)", "click", lambda: d.click("#confirm-btn"))
    r.step("accept confirm", "alert_accept", lambda: d.alert_accept())
    r.step("wait confirmed", "wait",
           lambda: d.wait_for(
               "document.getElementById('out-confirm').textContent === 'confirmed'",
               10, "out-confirm confirmed"))
    r.step("click confirm (dismiss)", "click", lambda: d.click("#confirm-btn"))
    r.step("dismiss confirm", "alert_dismiss", lambda: d.alert_dismiss())
    r.step("wait cancelled", "wait",
           lambda: d.wait_for(
               "document.getElementById('out-confirm').textContent === 'cancelled'",
               10, "out-confirm cancelled"))
    cd = r.step("read confirm outcome", "text", lambda: d.text("#out-confirm"))
    r.details["confirmDismissed"] = cd
    r.check("second confirm recorded cancelled", cd == "cancelled", cd)
    r.step("click ask name", "click", lambda: d.click("#prompt-btn"))
    r.step("answer prompt Reviewer", "alert_send",
           lambda: (d.alert_send("Reviewer"), d.alert_accept()))
    r.step("wait prompt outcome", "wait",
           lambda: d.wait_for(
               "document.getElementById('out-prompt').textContent !== ''",
               10, "#out-prompt non-empty"))
    p = r.step("read prompt outcome", "text", lambda: d.text("#out-prompt"))
    r.details["prompt"] = p
    r.check("prompt recorded Reviewer", p == "name: Reviewer", p)
    r.step("open modal", "click", lambda: d.click("#modal-btn"))
    r.step("fill note", "type",
           lambda: d.type_text("#note", "Looks good, publish it."))
    r.step("save modal", "click", lambda: d.click("#modal-save"))
    r.step("wait modal outcome", "wait",
           lambda: d.wait_for(
               "document.getElementById('out-modal').textContent !== ''",
               10, "#out-modal non-empty"))
    m = r.step("read modal outcome", "text", lambda: d.text("#out-modal"))
    r.details["modal"] = m
    r.check("modal recorded note", "Looks good, publish it." in m, m)
    handles_before = d.handles()
    r.step("open popup", "click", lambda: d.click("#popup-btn"))
    r.step("wait popup handle", "wait",
           lambda: _wait_handles(d, len(handles_before) + 1))
    popup_tab = [h for h in d.handles() if h not in handles_before][0]
    r.step("switch to popup", "switch", lambda: d.switch(popup_tab))
    # The popup navigated after the click, so it needs the full
    # post-navigation settle (switch()'s 0.5s is flaky here: t06 passed
    # in batch 1 and failed in the final run at this exact step, 21/11).
    r.step("settle popup", "wait",
           lambda: (d.wait_ready(), time.sleep(1.0)))
    r.step("fill popup name", "type",
           lambda: d.type_text("#pname", "Popup Tester"))
    r.step("submit popup", "click", lambda: d.click("#send"))
    r.step("switch back to main", "switch", lambda: d.switch(main_tab))
    r.step("wait popup value back", "wait",
           lambda: d.wait_for(
               "document.getElementById('out-popup').textContent !== ''",
               10, "#out-popup non-empty"))
    pv = r.step("read popup value", "text", lambda: d.text("#out-popup"))
    r.details["popup"] = pv
    r.check("popup returned name", pv == "popup name: Popup Tester", pv)


def run_t07(r, d):
    url = r.base + "/clone1/t07-download-check/fixture.html"
    clear_download("t07-test-data.csv")
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    info = r.step("read page info", "text", lambda: d.text("#info"))
    r.details["pageInfo"] = info
    m = re.search(r"checksum ([0-9a-f]{8})", info or "")
    exp_sum = m.group(1) if m else None
    r.check("page shows a checksum", exp_sum is not None, info)
    r.step("click download", "click", lambda: d.click("#download"))
    path = r.step("wait for downloaded file", "poll",
                  lambda: wait_download("t07-test-data.csv"))
    data = path.read_bytes()
    text = data.decode("utf8")
    lines = [l for l in text.split("\n") if l]
    r.details.update({"lines": len(lines), "firstLine": lines[0] if lines else "",
                      "checksum": checksum(data)})
    r.check("header is id,input,expected",
            lines and lines[0] == "id,input,expected", lines[0] if lines else "")
    r.check("6 lines total", len(lines) == 6, str(len(lines)))
    r.check("checksum matches page",
            exp_sum is not None and checksum(data) == exp_sum,
            f"file {checksum(data)} page {exp_sum}")


def run_t08(r, d):
    url = r.base + "/clone1/t08-login-auth/fixture.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    r.step("type short code", "type", lambda: d.type_text("#code", "abc"))
    r.step("click login", "click", lambda: d.click("#login-btn"))
    r.step("wait error", "wait",
           lambda: d.wait_for(
               "document.querySelector('#error') && "
               "document.querySelector('#error').textContent !== ''",
               10, "#error non-empty"))
    err = r.step("read short code error", "text", lambda: d.text("#error"))
    r.details["shortCodeError"] = err
    vis = r.step("protected hidden after short code", "visible",
                 lambda: d.visible("#protected"))
    r.details["protectedVisibleAfterShortCode"] = vis
    r.check("short code does not log in", not vis, str(vis))
    r.step("type valid code", "type",
           lambda: d.type_text("#code", "CODE-2026-ABCD"))
    r.step("click login", "click", lambda: d.click("#login-btn"))
    r.step("wait protected visible", "wait",
           lambda: d.wait_for(
               "document.querySelector('#protected') && "
               "document.querySelector('#protected').offsetParent !== null",
               10, "#protected visible"))
    w = r.step("read welcome", "text", lambda: d.text("#welcome"))
    r.details["welcome"] = w
    r.step("click mark reviewed", "click", lambda: d.click("#review"))
    r.step("wait review result", "wait",
           lambda: d.wait_for(
               "document.querySelector('#review-result') && "
               "document.querySelector('#review-result').textContent !== ''",
               10, "#review-result non-empty"))
    rr = r.step("read review result", "text", lambda: d.text("#review-result"))
    r.details["reviewResult"] = rr
    r.check("review reports problem 42",
            rr == "Problem 42 marked reviewed.", rr)
    r.step("reload page", "eval", lambda: d.refresh())
    vis2 = r.step("protected visible after reload", "visible",
                  lambda: d.visible("#protected"))
    r.details["protectedVisibleAfterReload"] = vis2
    r.check("session survives reload", vis2, str(vis2))
    r.step("click log out", "click", lambda: d.click("#logout"))
    r.step("wait login visible", "wait",
           lambda: d.wait_for(
               "document.querySelector('#login') && "
               "document.querySelector('#login').offsetParent !== null",
               10, "#login visible"))
    vis3 = r.step("protected hidden after logout", "visible",
                  lambda: d.visible("#protected"))
    r.details["protectedVisibleAfterLogout"] = vis3
    r.check("protected hidden after logout", not vis3, str(vis3))


def run_t09(r, d):
    url = r.base + "/clone1/t09-upload-metadata/fixture.html"
    txt, png = UPLOADS / "t09-statement.txt", UPLOADS / "t09-statement.png"
    txt.write_bytes(b"Statement text.\n")
    png.write_bytes(b"not really an image")
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    r.step("submit empty", "click", lambda: d.click("#submit"))
    r.step("wait error", "wait",
           lambda: d.wait_for(
               "document.querySelector('#error') && "
               "document.querySelector('#error').textContent !== ''",
               10, "#error non-empty"))
    err = r.step("read empty error", "text", lambda: d.text("#error"))
    r.details["emptyError"] = err
    r.check("empty error names title", "Title is required." in err, err)
    r.check("empty error names file", "Statement file is required." in err, err)
    r.step("fill title", "type",
           lambda: d.type_text("#title", "Metadata Problem"))
    r.step("choose png file", "set_file", lambda: d.set_file("#file", png))
    r.step("submit png", "click", lambda: d.click("#submit"))
    r.step("wait png error", "wait",
           lambda: d.wait_for(
               "document.getElementById('error').textContent.includes('Only .txt files')",
               10, "error mentions Only .txt files"))
    perr = r.step("read png error", "text", lambda: d.text("#error"))
    r.details["pngError"] = perr
    r.step("choose txt file", "set_file", lambda: d.set_file("#file", txt))
    r.step("submit txt", "click", lambda: d.click("#submit"))
    r.step("wait result", "wait",
           lambda: d.wait_for(
               "document.querySelector('#result') && "
               "document.querySelector('#result').textContent !== ''",
               10, "#result non-empty"))
    res = r.step("read result", "text", lambda: d.text("#result"))
    r.details["result"] = res
    r.check("success has problem ID P-1042", "P-1042" in res, res)
    r.check("success has title", "Metadata Problem" in res, res)
    r.check("success has file name", "t09-statement.txt" in res, res)


def run_t10(r, d):
    url = r.base + "/clone1/t10-login-upload-download/fixture.html"
    f = UPLOADS / "t10-data.txt"
    f.write_bytes(b"case one\ncase two\ncase three\ncase four\n")
    clear_download("t10-report.txt")
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    r.step("type access code", "type",
           lambda: d.type_text("#code", "CODE-2026-ABCD"))
    r.step("click login", "click", lambda: d.click("#login-btn"))
    r.step("wait work section visible", "wait",
           lambda: d.wait_for(
               "document.querySelector('#work') && "
               "document.querySelector('#work').offsetParent !== null",
               10, "#work visible"))
    r.step("choose data file", "set_file", lambda: d.set_file("#file", f))
    r.step("click judge", "click", lambda: d.click("#judge"))
    r.step("wait verdict", "wait",
           lambda: d.wait_for(
               "document.querySelector('#verdict') && "
               "document.querySelector('#verdict').textContent !== ''",
               10, "#verdict non-empty"))
    v = r.step("read verdict", "text", lambda: d.text("#verdict"))
    r.details["verdict"] = v
    r.check("verdict is 4 cases PASS", v == "Judged: 4 cases, PASS.", v)
    r.step("click download report", "click", lambda: d.click("#download"))
    path = r.step("wait for report file", "poll",
                  lambda: wait_download("t10-report.txt"))
    report = path.read_text(encoding="utf8")
    r.details["report"] = report
    r.check("report names uploaded file", "t10-data.txt" in report, report)
    r.check("report states 4 cases", "Cases: 4" in report, report)
    r.check("report states PASS", "Verdict: PASS" in report, report)


# ---------------- fcc-k tests (f01-f10) ----------------
# NOTE: the fcc-k fixtures only implement a fraction of their specs, and
# their __fcckVerify() checkers self-simulate. These functions run the
# RUNNABLE core of each spec through the real UI and verify the end state
# by reading the DOM. Steps with no UI are recorded as fixture gaps, not
# faked. See RUN-REPORT-20261121.md.

def _fcc_cell_btn(cell_id):
    # The spreadsheet fixture selects a cell ONLY via the buttons below
    # the table (onclick=clickCell('a2')). Clicking the <td> does nothing.
    return f"button[onclick=\"clickCell('{cell_id}')\"]"


def run_f01(r, d):
    url = r.base + "/fcc-k/test-01-spreadsheet.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    headers = r.step("read headers", "eval",
                     lambda: d.eval("return [...document.querySelectorAll('#sheet th')].map(e => e.textContent).join(',')"))
    r.check("headers Date Item Units Price Total",
            headers == ",Date,Item,Units,Price,Total", headers)
    # Trap check: clicking the <td> cell itself must NOT select it.
    r.step("TRAP: click td#a2 directly", "click_js",
           lambda: d.click_js("document.querySelector('#a2')"))
    sel = r.step("check td click selected nothing", "eval",
                 lambda: d.eval("return document.querySelector('#a2').classList.contains('sel')"))
    r.details["tdClickSelects"] = sel
    r.check("td click does NOT select (fixture trap)", sel is False, str(sel))
    rows = [("a2", "2026-11-16"), ("b2", "Widget"), ("c2", "12"),
            ("d2", "45000"), ("e2", "=C2*D2"),
            ("a3", "2026-11-17"), ("b3", "Gadget"), ("c3", "7"),
            ("d3", "82000"), ("e3", "=C3*D3"),
            ("a4", "2026-11-18"), ("b4", "Tool"), ("c4", "5"),
            ("d4", "150000"), ("e4", "=C4*D4"),
            ("e5", "=SUM(E2:E4)"), ("e6", "=AVERAGE(E2:E4)"),
            ("e7", "=COUNT(E2:E4)")]
    for cell, val in rows:
        r.step(f"select {cell.upper()}", "click",
               lambda c=cell: d.click(_fcc_cell_btn(c)))
        r.step(f"type {val} into {cell.upper()}", "type",
               lambda v=val: d.type_text("#typed", v))
        r.step(f"press type for {cell.upper()}", "click",
               lambda: d.eval("return [...document.querySelectorAll('button')].find(b => b.textContent === 'type').click()"))
        if val.startswith("="):
            r.step(f"press Enter for {cell.upper()}", "click",
                   lambda: d.eval("return [...document.querySelectorAll('button')].find(b => b.textContent === 'Enter').click()"))
    e7 = r.step("read E7 after wrong formula", "text", lambda: d.text("#e7"))
    r.details["e7AfterCount"] = e7
    r.check("E7 shows COUNT text after wrong formula", e7 == "COUNT text", e7)
    r.step("select E7", "click", lambda: d.click(_fcc_cell_btn("e7")))
    r.step("type corrected formula", "type",
           lambda: d.type_text("#typed", "=COUNTA(E2:E4)"))
    r.step("press type for correction", "click",
           lambda: d.eval("return [...document.querySelectorAll('button')].find(b => b.textContent === 'type').click()"))
    r.step("press Enter for correction", "click",
           lambda: d.eval("return [...document.querySelectorAll('button')].find(b => b.textContent === 'Enter').click()"))
    vals = r.step("read all result cells", "eval",
                  lambda: d.eval("return {e2: document.querySelector('#e2').textContent,"
                                 "e3: document.querySelector('#e3').textContent,"
                                 "e4: document.querySelector('#e4').textContent,"
                                 "e5: document.querySelector('#e5').textContent,"
                                 "e6: document.querySelector('#e6').textContent,"
                                 "e7: document.querySelector('#e7').textContent,"
                                 "c2: document.querySelector('#c2').textContent,"
                                 "c3: document.querySelector('#c3').textContent,"
                                 "c4: document.querySelector('#c4').textContent}"))
    r.details["endState"] = vals
    for k, v in [("e2", "540000"), ("e3", "574000"), ("e4", "750000"),
                 ("e5", "1864000"), ("e6", "621333"), ("e7", "3")]:
        r.check(f"{k.upper()} == {v}", vals[k] == v, f"{k}={vals[k]}")


def run_f02(r, d):
    # PARTIAL: fixture has no read toggle, flag, archive, compose, or send UI.
    url = r.base + "/fcc-k/test-02-email.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    count = r.step("count inbox rows", "eval",
                   lambda: d.eval("return document.querySelectorAll('#inbox li').length"))
    r.details["inboxCount"] = count
    r.check("inbox shows 6 messages", count == 6, str(count))
    for i in range(1, 7):
        r.step(f"open message {i}", "click", lambda n=i: d.click(f"#msg{n}"))
        body = r.step(f"read message {i} body", "text", lambda: d.text("#msg"))
        r.details[f"msg{i}"] = body
    r.step("open Sent folder", "click", lambda: d.click("#sentBtn"))
    sent = r.step("read Sent folder", "text", lambda: d.text("#msg"))
    r.details["sentFolder"] = sent
    r.check("Sent folder shows empty", "empty" in sent, sent)
    r.check("no triage UI exists (fixture gap)",
            d.eval("return !document.querySelector('[id*=archive i], [id*=flag i], [id*=compose i], [id*=send i]')"),
            "no archive/flag/compose/send controls in DOM")
    r.failures.append("FIXTURE GAP: spec steps 4,6,8,10,12,13,14-18 "
                      "(mark read, flag, archive, compose, send) have no UI "
                      "in the fixture; only reading messages is runnable.")


def run_f03(r, d):
    # PARTIAL: no event dialog; clicking a free slot creates a hardcoded
    # event in JS state; the event is NOT rendered in the grid.
    url = r.base + "/fcc-k/test-03-calendar.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    days = r.step("read day headers", "eval",
                  lambda: d.eval("return Array.from(document.querySelector('#grid').children).slice(1, 6).map(e => e.textContent.trim()).join(',')"))
    r.details["days"] = days
    r.check("week shows Tue-Sat", days == "Tue,Wed,Thu,Fri,Sat", days)
    busy = r.step("read Tue busy hours", "eval",
                  lambda: d.eval("return [...document.querySelectorAll('#grid .slot.busy')].map(e => e.textContent)"))
    r.details["busySlots"] = busy
    # Tue 10:00 slot: grid children = corner + 5 headers, then per hour
    # (label + 5 day slots). Hour 10 is the 2nd hour row, Tue 1st column.
    r.step("click Tue 10:00 free slot", "click_js",
           lambda: d.click_js("document.querySelector('#grid').children[6 + 1*6 + 1]"))
    # NOTE: the created event lives in a top-level `let events` binding,
    # which Marionette execute/sync CANNOT read (ReferenceError, 21/11).
    # The event is also never rendered in the grid. So the click itself
    # (no error) is the only observable outcome; event existence is not
    # DOM-verifiable. That is a fixture limitation, not a pass.
    r.failures.append("FIXTURE LIMIT: the clicked slot creates the event in "
                      "a top-level `let events` binding that Marionette "
                      "cannot read, and the event is never rendered in the "
                      "grid; event creation is unverifiable from the DOM.")


def run_f04(r, d):
    # PARTIAL: no typing UI for notes; clicking a source card adds one
    # fact (name + price). 2 clicks per source give 6 facts. Summary
    # textarea + Save work.
    url = r.base + "/fcc-k/test-04-research.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    n0 = r.step("verify notes empty", "text", lambda: d.text("#notes"))
    r.check("notes start empty", n0.strip() == "", n0)
    for src in range(3):
        for _ in range(2):
            r.step(f"click source card {chr(65 + src)}", "click_js",
                   lambda i=src: d.click_js(f"document.querySelectorAll('#sources .card')[{i}]"))
    notes = r.step("read notes", "text", lambda: d.text("#notes"))
    r.details["notes"] = notes
    lines = [l for l in notes.split("\n") if l.strip()]
    r.check("6 fact lines present", len(lines) == 6, f"{len(lines)} lines")
    for label in ["A:", "B:", "C:"]:
        r.check(f"2 facts with label {label}",
                sum(1 for l in lines if l.startswith(label)) == 2, notes)
    r.check("fact2 is price not support (fixture behavior)",
            "support" not in notes and "price=" in notes, notes)
    r.step("type summary", "type",
           lambda: d.type_text("#summary",
                               "Alpha $12/mo vs Beta $19/mo vs Gamma $9/mo, all differ."))
    r.step("save notes", "click", lambda: d.click("#saveBtn"))
    # NOTE: `saved` is a top-level `let` binding; Marionette execute/sync
    # cannot read it (ReferenceError). Verify the DOM-visible effect
    # instead: the summary textarea keeps the typed text after Save.
    summary_after = r.step("read summary after save", "eval",
                           lambda: d.eval("return document.querySelector('#summary').value"))
    r.details["summaryAfterSave"] = summary_after
    r.check("summary survives save",
            summary_after == "Alpha $12/mo vs Beta $19/mo vs Gamma $9/mo, all differ.",
            summary_after)
    notes2 = r.step("re-read notes after save", "text", lambda: d.text("#notes"))
    r.check("notes survive save", notes2 == notes, notes2)
    r.failures.append("FIXTURE GAP: spec steps 4,5,7,8,10,11 (type each fact "
                      "with source label) have no typing UI; facts come only "
                      "from clicking cards, and fact2 is always the price, "
                      "never the support channel the spec asks for.")


def run_f05(r, d):
    # PARTIAL: clicking a file moves it to Organized. No folder creation,
    # no rename, no index.txt UI. Spec step 9 also has a wrong extension
    # (trip-03.png; the file is photo from web.jpg, so trip-03.jpg).
    url = r.base + "/fcc-k/test-05-image.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    dl0 = r.step("list downloads", "eval",
                 lambda: d.eval("return [...document.querySelectorAll('#dl .file')].map(e => e.textContent)"))
    r.details["downloadsStart"] = dl0
    r.check("8 files in downloads", len(dl0) == 8, str(dl0))
    for i in range(8):
        r.step(f"move file {i + 1} to Organized", "click_js",
               lambda: d.click_js("document.querySelector('#dl .file')"))
    org = r.step("list Organized", "eval",
                 lambda: d.eval("return [...document.querySelectorAll('#org .file')].map(e => e.textContent)"))
    r.details["organized"] = org
    dl1 = r.step("list downloads after move", "eval",
                 lambda: d.eval("return [...document.querySelectorAll('#dl .file')].map(e => e.textContent)"))
    r.details["downloadsEnd"] = dl1
    r.check("Organized has 8 files", len(org) == 8, str(org))
    r.check("downloads empty after move", len(dl1) == 0, str(dl1))
    r.check("files keep ORIGINAL names (no rename UI)",
            org == ["img_01.jpg", "screenshot.png", "photo from web.jpg",
                    "img_04.jpg", "img_05.jpg", "img_06.png", "img_07.jpg",
                    "img_08.jpg"], str(org))
    r.failures.append("FIXTURE GAP: spec steps 3 (create Organized folder), "
                      "5,7,9,11,13,15,17,19 (rename to trip-01..08) and 21-23 "
                      "(write index.txt) have no UI. Spec step 9 also names "
                      "trip-03.png but the file is photo from web.jpg.")


def run_f06(r, d):
    # BLOCKED: no settings controls at all; both Open buttons are dead.
    url = r.base + "/fcc-k/test-06-settings.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    font = r.step("read notes font", "text", lambda: d.text("#notesSettings"))
    zoom = r.step("read reader zoom", "text", lambda: d.text("#readerSettings"))
    r.details.update({"notesFont": font, "readerZoom": zoom})
    r.check("notes font starts 14", "14" in font, font)
    r.check("reader zoom starts 100", "100" in zoom, zoom)
    r.step("click Open Notes", "click", lambda: d.click("#notesOpen"))
    r.step("click Open Reader", "click", lambda: d.click("#readerOpen"))
    font2 = r.step("re-read notes font", "text", lambda: d.text("#notesSettings"))
    zoom2 = r.step("re-read reader zoom", "text", lambda: d.text("#readerSettings"))
    r.check("Open buttons change nothing (dead buttons)",
            font2 == font and zoom2 == zoom, f"{font2} / {zoom2}")
    r.failures.append("BLOCKED: fixture has no font-size input, no zoom "
                      "input, no Apply button, no sample document. The spec "
                      "steps 3-18 cannot run; nothing in the fixture is "
                      "configurable.")


def run_f07(r, d):
    # BLOCKED: toggle and save buttons have no handlers; note save is dead.
    url = r.base + "/fcc-k/test-07-bug.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    before = r.step("read setting before", "text", lambda: d.text("#settingVal"))
    r.details["before"] = before
    r.check("setting starts enabled", before == "enabled", before)
    r.step("click toggle", "click", lambda: d.click("#toggle"))
    r.step("click save immediately", "click", lambda: d.click("#save"))
    after = r.step("read setting after", "text", lambda: d.text("#settingVal"))
    r.details["after"] = after
    r.check("toggle does nothing (dead button)", after == "enabled", after)
    r.step("click save again", "click", lambda: d.click("#save"))
    after2 = r.step("read setting after2", "text", lambda: d.text("#settingVal"))
    r.details["after2"] = after2
    r.step("type bug note", "type",
           lambda: d.type_text("#bugNote",
                               "Bug: setting reverts. Before enabled After enabled After2 enabled. Conclusion: not reproduced"))
    r.step("click save note", "click", lambda: d.click("#saveNote"))
    # NOTE: `noteSaved` is a top-level `let` binding; Marionette cannot
    # read it. Verify the DOM-visible effect instead: the note textarea
    # keeps the typed text (the button is dead, so nothing else changes).
    note_after = r.step("read note after save", "eval",
                        lambda: d.eval("return document.querySelector('#bugNote').value"))
    r.details["noteAfterSave"] = note_after
    r.check("note text stays in textarea after save click",
            note_after.startswith("Bug: setting reverts."), note_after)
    r.failures.append("BLOCKED: #toggle, #save, #saveNote have no click "
                      "handlers in the fixture. The toggle-save-revert bug "
                      "cannot be observed and no note can be saved.")


def run_f08(r, d):
    # BLOCKED: the form has no validation logic; submit does nothing.
    url = r.base + "/fcc-k/test-08-form.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    r.step("type name", "type", lambda: d.type_text("#fullName", "Pham Tuan"))
    r.step("type short password", "type", lambda: d.type_text("#pw", "abcd"))
    r.step("type mismatched confirm", "type", lambda: d.type_text("#pw2", "wxyz"))
    r.step("submit (expect errors)", "click", lambda: d.click("#submit"))
    err = r.step("read errors after submit", "text", lambda: d.text("#errors"))
    r.details["errorsAfterSubmit"] = err
    r.check("submit produces no errors (no validation logic)",
            err.strip() == "", err)
    ok_vis = r.step("success shown after bad submit", "visible",
                    lambda: d.visible("#ok"))
    r.check("no success shown either", ok_vis is False, str(ok_vis))
    r.step("fill valid values", "eval",
           lambda: d.eval("document.querySelector('#email').value='pham@example.com';"
                          "document.querySelector('#pw').value='longenough1';"
                          "document.querySelector('#pw2').value='longenough1';"))
    r.step("submit valid", "click", lambda: d.click("#submit"))
    ok2 = r.step("success shown after valid submit", "visible",
                 lambda: d.visible("#ok"))
    r.check("valid submit shows nothing (no success logic)",
            ok2 is False, str(ok2))
    r.failures.append("BLOCKED: #submit has no click handler and there is no "
                      "validation code in the fixture. No error can appear, "
                      "no success can appear; the spec error-fix loop cannot run.")


def run_f09(r, d):
    # PARTIAL: source has 3 rows, not 4; Convert copies src to tgt; no
    # typing UI for converted lines.
    url = r.base + "/fcc-k/test-09-convert.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    src = r.step("read App A source", "text", lambda: d.text("#src"))
    r.details["source"] = src
    rows = [l for l in src.split("\n") if l.strip()]
    r.check("source has 3 rows, not 4 as specced",
            len(rows) == 3, f"{len(rows)} rows")
    r.step("click Convert / Apply", "click", lambda: d.click("#convert"))
    tgt = r.step("read App B output", "text", lambda: d.text("#tgt"))
    r.details["converted"] = tgt
    r.check("converted output equals source (3 lines)",
            tgt.strip() == src.strip(), tgt)
    r.check("no typing UI exists (fixture gap)",
            d.eval("return !document.querySelector('#tgt input, #tgt textarea, #tgt [contenteditable]')"),
            "tgt is a plain div")
    r.failures.append("FIXTURE GAP: spec says a 4-row source table and "
                      "typing 4 converted lines into App B; the fixture has "
                      "3 rows already in target format and #tgt is a plain "
                      "div with no input. Only read + Convert + compare runs.")


def run_f10(r, d):
    # BLOCKED: all five buttons have no handlers; doc is static text.
    url = r.base + "/fcc-k/test-10-document.html"
    r.step("open fixture", "goto", lambda: d.new_tab(url))
    doc0 = r.step("read document", "text", lambda: d.text("#doc"))
    r.details["docStart"] = doc0
    r.check("doc has old vendor twice", doc0.count("old vendor") == 2, doc0)
    r.step("click Replace all", "click", lambda: d.click("#replaceAll"))
    doc1 = r.step("read doc after replace", "text", lambda: d.text("#doc"))
    r.check("replace does nothing (dead button)",
            doc1.count("old vendor") == 2, doc1)
    r.step("click Add table", "click", lambda: d.click("#addTable"))
    r.step("click Save", "click", lambda: d.click("#save"))
    r.step("click Export", "click", lambda: d.click("#export"))
    doc2 = r.step("read doc after all buttons", "text", lambda: d.text("#doc"))
    r.check("doc unchanged after all buttons", doc2 == doc0, doc2)
    r.failures.append("BLOCKED: #find, #replaceAll, #addTable, #save, #export "
                      "have no click handlers and #doc is static text. No "
                      "find/replace, no table insert, no TOC, no export can run.")


TESTS = {
    "t01": run_t01, "t02": run_t02, "t03": run_t03, "t04": run_t04,
    "t05": run_t05, "t06": run_t06, "t07": run_t07, "t08": run_t08,
    "t09": run_t09, "t10": run_t10,
    "f01": run_f01, "f02": run_f02, "f03": run_f03, "f04": run_f04,
    "f05": run_f05, "f06": run_f06, "f07": run_f07, "f08": run_f08,
    "f09": run_f09, "f10": run_f10,
}


def run_one(test_id, base_url):
    fn = TESTS[test_id]
    r = Runner(test_id, base_url)
    UPLOADS.mkdir(parents=True, exist_ok=True)
    try:
        with WD() as d:
            fn(r, d)
    except Exception as exc:
        r.failures.append(f"RUNNER ERROR: {type(exc).__name__}: {exc}")
        print(f"[{test_id}] RUNNER ERROR {exc}", flush=True)
    finally:
        # Make sure the test tab is gone even if the session died: the
        # session close in WD.__exit__ handles it; nothing else to do.
        pass
    s = r.summary()
    print("RESULT " + json.dumps(s, ensure_ascii=False), flush=True)
    return s


def main():
    args = sys.argv[1:]
    if not args:
        print("usage: run_live.py <t01..t10 f01..f10 | all>", flush=True)
        return 2
    wanted = list(TESTS) if args == ["all"] else args
    for t in wanted:
        if t not in TESTS:
            print(f"unknown test {t}", flush=True)
            return 2
    httpd, base_url = start_server()
    print(f"serving {SERVER_ROOT} at {base_url}", flush=True)
    results = []
    try:
        for t in wanted:
            results.append(run_one(t, base_url))
    finally:
        if httpd is not None:
            httpd.shutdown()
    passed = sum(1 for x in results if x["pass"])
    print(f"SUMMARY {passed}/{len(results)} passed, "
          f"total_ms={sum(x['elapsed_ms'] for x in results)}", flush=True)
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
