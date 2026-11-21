#!/usr/bin/env python3
"""Probe v2: does explicit window switch fix interactability? (Worker P)
Creates a session, opens a new tab, EXPLICITLY switches to it, loads the
t01 fixture, and tries the exact failing op (element clear on #title).
Closes only its own new tab. Never navigates/clicks user tabs."""
import json
import subprocess
import time
import urllib.request

WD_PORT = 4447


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
        orig = wd("GET", S + "/window")["value"]
        print("orig current:", orig[:8],
              wd("GET", S + "/title")["value"][:40])
        new_h = wd("POST", S + "/window/new",
                   {"type": "tab"})["value"]["handle"]
        print("new handle:", new_h[:8])
        print("current right after new (no switch):",
              wd("GET", S + "/window")["value"][:8])
        wd("POST", S + "/window", {"handle": new_h})
        print("current after explicit switch:",
              wd("GET", S + "/window")["value"][:8])
        wd("POST", S + "/url",
           {"url": "http://127.0.0.1:8765/clone1/t01-upload-single/fixture.html"})
        time.sleep(1)

        def ev(js):
            return wd("POST", S + "/execute/sync",
                      {"script": js, "args": []})["value"]
        print("title:", ev("return document.title"))
        print("visibility:", ev("return document.visibilityState"))
        print("hasFocus:", ev("return document.hasFocus()"))
        print("inner:", ev("return [window.innerWidth, window.innerHeight]"))
        print("rect #title:", ev("const r=document.querySelector('#title').getBoundingClientRect(); return [r.x,r.y,r.width,r.height]"))
        el = wd("POST", S + "/element",
                {"using": "css selector", "value": "#title"})["value"]["element-6066-11e4-a52e-4f735466cecf"]
        print("found #title el:", el[:8])
        try:
            wd("POST", S + f"/element/{el}/clear", {})
            print("CLEAR OK")
        except Exception as e:
            print("CLEAR FAILED:", str(e)[:200])
        try:
            wd("POST", S + f"/element/{el}/value", {"text": "Sample Problem"})
            print("TYPE OK")
            print("value readback:",
                  wd("GET", S + f"/element/{el}/property/value")["value"])
        except Exception as e:
            print("TYPE FAILED:", str(e)[:200])
        wd("DELETE", S + "/window", {})
        print("probe tab closed")
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
