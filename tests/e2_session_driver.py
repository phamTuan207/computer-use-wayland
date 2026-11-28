#!/usr/bin/env python3
"""E2 Part B session driver: observe the grid tab, click the 29 estimated
points with the Driver A pointer, then finish. Run DETACHED on the laptop:

  setsid nohup python3 tests/e2_session_driver.py > /tmp/e2-session-driver.out 2>&1 < /dev/null & disown

Logs every send/recv with wall-clock time to /tmp/e2-session-driver.log.
No em dashes. Never ydotool. The session shows the computer-use indicator
while it runs, which is the required visible signal.
"""
import json
import os
import subprocess
import sys
import time

CU = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "scripts", "cu.py")
WINDOW = "0x559f8d5adda0"
ACTIONS = "/tmp/e2-actions.json"
LOG = "/tmp/e2-session-driver.log"
ENV_EXTRA = {
    "XDG_RUNTIME_DIR": "/run/user/1000",
    "WAYLAND_DISPLAY": "wayland-1",
    "HYPRLAND_INSTANCE_SIGNATURE": "11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795201820_401709775",
}


def log(msg):
    line = "%s %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def main():
    open(LOG, "w").write("")
    log("E2 Part B start")
    env = dict(os.environ)
    env.update(ENV_EXTRA)
    proc = subprocess.Popen(
        [sys.executable, CU, "session", "--", sys.executable, CU, "session-driver"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1, env=env)

    def send(obj):
        line = json.dumps(obj)
        log("SEND " + line[:400])
        proc.stdin.write(line + "\n")
        proc.stdin.flush()

    def recv():
        line = proc.stdout.readline()
        if not line:
            raise RuntimeError("driver stdout closed")
        log("RECV " + line[:600])
        return json.loads(line)

    ready = recv()
    assert ready.get("driver") == "ready", ready
    log("driver ready, observing")
    send({"args": ["observe", "--window", WINDOW, "--max-width", "1200"]})
    obs = recv()
    result = obs.get("result", {})
    if obs.get("returncode") != 0 or not result.get("observation"):
        raise RuntimeError("observe failed: " + json.dumps(obs)[:500])
    obs_path = result["observation"]
    log("observation path: " + obs_path)
    send({"args": ["act", "--observation", obs_path, "--actions", ACTIONS]})
    act = recv()
    log("act returncode: " + str(act.get("returncode")))
    after = (act.get("result") or {}).get("after") or {}
    log("after image: " + str(after.get("image")))
    log("after observation: " + str(after.get("observation")))
    send({"args": ["finish"]})
    fin = recv()
    log("finish: " + json.dumps(fin)[:200])
    proc.stdin.close()
    code = proc.wait(timeout=120)
    log("session exit code: " + str(code))
    log("E2 Part B done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
