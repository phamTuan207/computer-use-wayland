#!/usr/bin/env python3
"""Hand-drive helper for Worker P agent-think-time samples (21/11/2026).
Reads one JSON command per line on stdin, executes it against live Zen
via geckodriver --connect-existing, prints one JSON result per line.
The AGENT types each command by hand and times its own thinking between
commands, so the wall time per step is real agent time, not script time.
Commands: {"cmd": "new_session"} | {"cmd": "new_tab", "url": ...}
| {"cmd": "find", "css": ...} | {"cmd": "clear", "el": ...}
| {"cmd": "type", "el": ..., "text": ...} | {"cmd": "click", "el": ...}
| {"cmd": "click_js", "js": ...} | {"cmd": "eval", "js": ...}
| {"cmd": "text", "css": ...} | {"cmd": "value", "css": ...}
| {"cmd": "close_tab"} | {"cmd": "delete_session"} | {"cmd": "quit"}
Element ids are returned by find and reused by clear/type/click.
set_file reads a local file, uploads it via the WebDriver /file
endpoint, and sets the file input's value to the remote path."""
import json
import subprocess
import sys
import time
import urllib.request

WD_PORT = 4450


def wd(method, path, body=None):
    url = f"http://127.0.0.1:{WD_PORT}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def main():
    g = subprocess.Popen(
        ["/tmp/geckodriver", "--connect-existing",
         "--marionette-host", "127.0.0.1", "--marionette-port", "2828",
         "--port", str(WD_PORT), "--log", "warn"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    sid = None
    opened = []
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                c = json.loads(line)
            except Exception as e:
                print(json.dumps({"ok": False, "error": f"bad json: {e}"}), flush=True)
                continue
            cmd = c.get("cmd")
            t0 = time.perf_counter()
            try:
                if cmd == "quit":
                    print(json.dumps({"ok": True, "result": "bye"}), flush=True)
                    break
                if cmd == "new_session":
                    sid = wd("POST", "/session", {"capabilities": {
                        "alwaysMatch": {"browserName": "firefox"}}})["value"]["sessionId"]
                    out = sid[:8]
                elif cmd == "new_tab":
                    S = f"/session/{sid}"
                    h = wd("POST", S + "/window/new", {"type": "tab"})["value"]["handle"]
                    opened.append(h)
                    wd("POST", S + "/window", {"handle": h})
                    wd("POST", S + "/url", {"url": c["url"]})
                    deadline = time.perf_counter() + 10
                    while time.perf_counter() < deadline:
                        if wd("POST", S + "/execute/sync",
                              {"script": "return document.readyState", "args": []})["value"] == "complete":
                            break
                        time.sleep(0.1)
                    time.sleep(1.0)
                    out = h[:8]
                elif cmd == "find":
                    S = f"/session/{sid}"
                    out = wd("POST", S + "/element",
                             {"using": "css selector", "value": c["css"]})["value"]["element-6066-11e4-a52e-4f735466cecf"]
                elif cmd == "clear":
                    S = f"/session/{sid}"
                    wd("POST", S + f"/element/{c['el']}/clear", {})
                    out = "cleared"
                elif cmd == "type":
                    S = f"/session/{sid}"
                    wd("POST", S + f"/element/{c['el']}/value", {"text": c["text"]})
                    out = "typed"
                elif cmd == "click":
                    S = f"/session/{sid}"
                    wd("POST", S + f"/element/{c['el']}/click", {})
                    out = "clicked"
                elif cmd == "click_js":
                    S = f"/session/{sid}"
                    wd("POST", S + "/execute/sync",
                       {"script": c["js"] + ".scrollIntoView({block:'center'}); " + c["js"] + ".click();", "args": []})
                    out = "clicked_js"
                elif cmd == "eval":
                    S = f"/session/{sid}"
                    out = wd("POST", S + "/execute/sync",
                             {"script": c["js"], "args": []})["value"]
                elif cmd == "text":
                    S = f"/session/{sid}"
                    out = wd("POST", S + "/execute/sync",
                             {"script": f"return document.querySelector({json.dumps(c['css'])}).textContent", "args": []})["value"]
                elif cmd == "value":
                    S = f"/session/{sid}"
                    out = wd("POST", S + "/execute/sync",
                             {"script": f"return document.querySelector({json.dumps(c['css'])}).value", "args": []})["value"]
                elif cmd == "set_file":
                    S = f"/session/{sid}"
                    # Geckodriver does NOT implement POST /session/:id/file
                    # (405). Setting the file input's value to a local path
                    # directly is the supported path: geckodriver uploads
                    # it internally.
                    wd("POST", S + f"/element/{c['el']}/value",
                       {"text": c["path"]})
                    out = f"set {c['path']}"
                elif cmd == "close_tab":
                    S = f"/session/{sid}"
                    wd("DELETE", S + "/window", {})
                    out = "closed"
                elif cmd == "delete_session":
                    wd("DELETE", "/session/" + sid, {})
                    out = "deleted"
                    sid = None
                else:
                    raise ValueError(f"unknown cmd {cmd}")
                print(json.dumps({"ok": True, "result": out,
                                  "ms": int((time.perf_counter() - t0) * 1000)}), flush=True)
            except Exception as e:
                print(json.dumps({"ok": False, "error": str(e)[:300],
                                  "ms": int((time.perf_counter() - t0) * 1000)}), flush=True)
    finally:
        if sid is not None:
            try:
                wd("DELETE", "/session/" + sid, {})
            except Exception:
                pass
        g.terminate()


if __name__ == "__main__":
    main()
