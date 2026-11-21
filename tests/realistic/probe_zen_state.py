#!/usr/bin/env python3
"""Probe live Zen tab/window state (Worker P diagnostic, 21/11/2026).
Stdlib only. Creates one session, reports state, deletes session.
Does not navigate or click any user tab. Closes ONLY tabs whose URL
starts with http://127.0.0.1:8765 (Worker P test tabs)."""
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request

WD_PORT = 4446


def wd(method, path, body=None):
    url = f"http://127.0.0.1:{WD_PORT}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def main():
    close_leftovers = "--close-leftovers" in sys.argv
    quick = "--quick" in sys.argv
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
        cur = wd("GET", S + "/window")["value"]
        print("current handle:", cur[:8])
        print("current title:", wd("GET", S + "/title")["value"][:80])
        print("current url:", wd("GET", S + "/url")["value"][:120])
        handles = wd("GET", S + "/window/handles")["value"]
        print("tab count:", len(handles))
        leftovers = []
        if quick:
            print("quick mode: skipping per-tab enumeration")
        else:
            for h in handles:
                wd("POST", S + "/window", {"handle": h})
                t = wd("GET", S + "/title")["value"]
                u = wd("GET", S + "/url")["value"]
                if u.startswith("http://127.0.0.1:8765"):
                    leftovers.append((h, t, u))
        print("leftover test tabs:", len(leftovers))
        for h, t, u in leftovers:
            print("  leftover:", h[:8], t[:50], u[:100])
        if close_leftovers:
            for h, t, u in leftovers:
                wd("POST", S + "/window", {"handle": h})
                wd("DELETE", S + "/window", {})
                print("  closed:", h[:8])
            # The session's original tab may have been a leftover we just
            # closed. Re-pick the current tab from the survivors.
            cur = wd("GET", S + "/window")["value"]
            print("current handle after cleanup:", cur[:8])
            print("tab count after cleanup:",
                  len(wd("GET", S + "/window/handles")["value"]))
        # Back to the original tab, then probe a NEW tab state.
        wd("POST", S + "/window", {"handle": cur})
        try:
            new_h = wd("POST", S + "/window/new",
                       {"type": "tab"})["value"]["handle"]
            print("new tab handle:", new_h[:8])
            wd("POST", S + "/url",
               {"url": "http://127.0.0.1:8765/clone1/t01-upload-single/fixture.html"})
            time.sleep(1)
            def ev(js):
                return wd("POST", S + "/execute/sync",
                          {"script": js, "args": []})["value"]
            print("new tab title:", ev("return document.title"))
            print("visibility:", ev("return document.visibilityState"))
            print("hasFocus:", ev("return document.hasFocus()"))
            print("inner:", ev("return [window.innerWidth, window.innerHeight]"))
            print("rect #title:", ev("const r=document.querySelector('#title').getBoundingClientRect(); return [r.x,r.y,r.width,r.height]"))
            print("current handle now:", wd("GET", S + "/window")["value"][:8])
            wd("DELETE", S + "/window", {})
            print("probe tab closed")
        except Exception as e:
            print("NEW TAB PROBE FAILED:", type(e).__name__, str(e)[:300])
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
