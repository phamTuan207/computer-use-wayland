#!/usr/bin/env python3
"""Probe v5: t04 select + t08 sessionStorage across refresh (Worker P).
Tests the exact eval sequences the runner uses, with state reads."""
import json
import subprocess
import time
import urllib.request

WD_PORT = 4448


def wd(method, path, body=None):
    url = f"http://127.0.0.1:{WD_PORT}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def main():
    p = subprocess.Popen(
        ["/tmp/geckodriver", "--connect-existing",
         "--marionette-host", "127.0.0.1", "--marionette-port", "2828",
         "--port", str(WD_PORT), "--log", "warn"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    sid = None
    try:
        sid = wd("POST", "/session", {"capabilities": {
            "alwaysMatch": {"browserName": "firefox"}}})["value"]["sessionId"]
        S = f"/session/{sid}"

        def ev(js):
            return wd("POST", S + "/execute/sync",
                      {"script": js, "args": []})["value"]

        def goto(url):
            wd("POST", S + "/url", {"url": url})
            deadline = time.perf_counter() + 10
            while time.perf_counter() < deadline:
                if ev("return document.readyState") == "complete":
                    return
                time.sleep(0.1)
            raise RuntimeError("not complete")

        # --- t04 select test ---
        h = wd("POST", S + "/window/new", {"type": "tab"})["value"]["handle"]
        wd("POST", S + "/window", {"handle": h})
        goto("http://127.0.0.1:8765/clone1/t04-long-form-draft/fixture.html")
        time.sleep(1)
        print("t04 ptype before:", ev("return document.querySelector('#ptype').value"))
        print("t04 display before:", ev("return getComputedStyle(document.querySelector('#interactive-fields')).display"))
        ev("document.querySelector('#ptype').value='interactive';"
           "document.querySelector('#ptype').dispatchEvent(new Event('change'));")
        print("t04 ptype after eval:", ev("return document.querySelector('#ptype').value"))
        print("t04 display after eval:", ev("return getComputedStyle(document.querySelector('#interactive-fields')).display"))
        # Try the option-click path instead.
        ev("document.querySelector('#ptype').value='batch';"
           "document.querySelector('#ptype').dispatchEvent(new Event('change'));")
        print("t04 display after reset to batch:", ev("return getComputedStyle(document.querySelector('#interactive-fields')).display"))
        el = wd("POST", S + "/element", {"using": "css selector", "value": "#ptype option[value='interactive']"})["value"]["element-6066-11e4-a52e-4f735466cecf"]
        wd("POST", S + f"/element/{el}/click", {})
        print("t04 ptype after option click:", ev("return document.querySelector('#ptype').value"))
        print("t04 display after option click:", ev("return getComputedStyle(document.querySelector('#interactive-fields')).display"))
        wd("DELETE", S + "/window", {})

        # --- t08 sessionStorage across refresh ---
        h = wd("POST", S + "/window/new", {"type": "tab"})["value"]["handle"]
        wd("POST", S + "/window", {"handle": h})
        goto("http://127.0.0.1:8765/clone1/t08-login-auth/fixture.html")
        time.sleep(1)
        print("t08 sessionStorage keys before login:", ev("return Object.keys(sessionStorage)"))
        print("t08 localStorage keys before login:", ev("return Object.keys(localStorage)"))
        wd("DELETE", S + "/window", {})
        wd("DELETE", "/session/" + sid, {})
        print("SESSION_DELETED")
    except Exception as e:
        print("FAIL:", type(e).__name__, str(e)[:300])
    finally:
        if sid is not None:
            try:
                wd("DELETE", "/session/" + sid, {})
            except Exception:
                pass
        p.terminate()


if __name__ == "__main__":
    main()
