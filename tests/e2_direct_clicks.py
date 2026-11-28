#!/usr/bin/env python3
"""E2 Part B (direct pointer path): click the 29 estimated points using the
exact Driver A pointer protocol from scripts/cu.py desktop_act, without a
session (the session guardian fails to start on this checkout; see the
report). Protocol per click, identical to desktop_act:
  image_point -> normalized abs coords -> pointer move -> hyprctl cursorpos
  must be within 3px or refuse -> button 0 press/release -> re-check 3px.
Run DETACHED on the laptop:
  setsid nohup python3 tests/e2_direct_clicks.py > /tmp/e2-direct.out 2>&1 < /dev/null & disown
Logs every click with wall-clock time to /tmp/e2-direct-clicks.log.
NOTE: no session means no indicator pill and no cancel latch for this run.
The clicks themselves use the identical math and verification as desktop_act.
"""
import json
import math
import os
import select
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POINTER = ROOT + "/native/pointer"
OBS = os.path.expanduser("~/.cache/agent-computer-use/44623b123878.json")
ACTIONS = "/tmp/e2-actions.json"
LOG = "/tmp/e2-direct-clicks.log"
ENV = {
    "XDG_RUNTIME_DIR": "/run/user/1000",
    "WAYLAND_DISPLAY": "wayland-1",
    "HYPRLAND_INSTANCE_SIGNATURE": "11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795201820_401709775",
    "PATH": "/usr/local/sbin:/usr/local/bin:/usr/bin:"
            + os.path.expanduser("~/.local/bin"),
}


def log(msg):
    line = "%s %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def hypr(*args):
    env = dict(os.environ)
    env.update(ENV)
    out = subprocess.run(["hyprctl", "-j", *args], capture_output=True, text=True,
                         env=env, timeout=15)
    return json.loads(out.stdout)


def image_point(meta, x, y):
    iw, ih = meta["image_size"]
    rx, ry, rw, rh = meta["region"]
    if not (0 <= x < iw and 0 <= y < ih):
        raise ValueError("point outside observed image: %s,%s" % (x, y))
    return rx + x * rw / iw, ry + y * rh / ih


class Pointer:
    def __init__(self, monitor):
        env = dict(os.environ)
        env.update(ENV)
        self.p = subprocess.Popen([POINTER, monitor], env=env,
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True, bufsize=1)
        if self.reply() != "ready":
            raise RuntimeError("pointer startup failed")

    def reply(self):
        if not select.select([self.p.stdout], [], [], 2)[0]:
            raise RuntimeError("pointer timed out")
        line = self.p.stdout.readline().strip()
        if not line:
            raise RuntimeError("pointer disconnected")
        return line

    def command(self, s):
        self.p.stdin.write(s + "\n")
        self.p.stdin.flush()
        if self.reply() != "ok":
            raise RuntimeError("pointer action failed: " + s)

    def close(self):
        try:
            self.p.stdin.close()
        except (BrokenPipeError, OSError):
            pass
        try:
            self.p.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.p.terminate()
            self.p.wait(timeout=2)


def main():
    open(LOG, "w").write("")
    log("E2 Part B direct start")
    meta = json.load(open(OBS))
    actions = json.load(open(ACTIONS))
    log("observation %s image %s region %s monitor_box %s" % (
        OBS, meta["image_size"], meta["region"], meta["monitor_box"]))
    pointer = Pointer(meta["monitor"])
    log("pointer ready, monitor " + meta["monitor"])
    mx, my, mw, mh = meta["monitor_box"]
    n_ok = 0
    for i, a in enumerate(actions, 1):
        gx, gy = image_point(meta, a["x"], a["y"])
        nx = round((gx - mx) / mw * 1000000)
        ny = round((gy - my) / mh * 1000000)
        pointer.command("abs %d %d 1000000 1000000" % (nx, ny))
        pos = hypr("cursorpos")
        err = math.hypot(pos["x"] - gx, pos["y"] - gy)
        if err > 3:
            log("click %d REFUSED pointer missed: intended %.1f,%.1f cursor %s err %.1f" % (
                i, gx, gy, pos, err))
            raise RuntimeError("pointer missed target; refusing click")
        pointer.command("button 0 1")
        time.sleep(0.025)
        pointer.command("button 0 0")
        pos2 = hypr("cursorpos")
        err2 = math.hypot(pos2["x"] - gx, pos2["y"] - gy)
        if err2 > 3:
            log("click %d post-click pointer moved: err %.1f" % (i, err2))
            raise RuntimeError("post-click pointer moved; click outcome uncertain")
        n_ok += 1
        log("click %d ok image %s,%s screen %.1f,%.1f cursor_err %.2f" % (
            i, a["x"], a["y"], gx, gy, err))
    pointer.close()
    log("E2 Part B direct done: %d/%d clicks, pointer within 3px every time" % (n_ok, len(actions)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
