#!/usr/bin/env python3
"""Direct Pointer right-click (no session) - image coords (1920x1200 eDP-2) to global."""
import importlib.util, json, math, os, subprocess, sys, time
IMG_W, IMG_H = 1920, 1200
MX, MY, MW, MH = 2464, 902, 1920, 1200
spec = importlib.util.spec_from_file_location("cu", "/home/james/.local/share/agent-computer-use/scripts/cu.py")
cu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cu)
def getenv():
    env = dict(os.environ)
    env.update({"XDG_RUNTIME_DIR": "/run/user/1000", "WAYLAND_DISPLAY": "wayland-1",
                "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/1000/bus"})
    import glob
    dirs = [d for d in glob.glob("/run/user/1000/hypr/*") if "_" in d]
    sig = ""
    for d in dirs:
        base = d.rsplit("/", 1)[-1]
        if "_" in base and len(base) > 20:
            sig = base
            break
    if sig:
        env["HYPRLAND_INSTANCE_SIGNATURE"] = sig
    return env
def cursorpos(env):
    return cu.hypr(env, "cursorpos")
def main():
    ix, iy, label = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else "rclick"
    t0 = time.time()
    gx, gy = MX + ix, MY + iy
    env = getenv()
    ptr = cu.Pointer(env, "eDP-2")
    try:
        before = cursorpos(env)
        ptr.command("abs %d %d 1000000 1000000" % (round(ix/IMG_W*1000000), round(iy/IMG_H*1000000)))
        pos = cursorpos(env)
        miss = math.hypot(pos["x"]-gx, pos["y"]-gy)
        print("%s: move img=(%d,%d) global=(%d,%d) cursor=(%d,%d) miss=%.1fpx before=(%d,%d)" % (label, ix, iy, gx, gy, pos["x"], pos["y"], miss, before["x"], before["y"]), flush=True)
        if miss > 3:
            print("MISS - refusing click"); return 1
        ptr.command("button 1 1"); time.sleep(0.025); ptr.command("button 1 0")
        after = cursorpos(env)
        print("%s: RIGHT-CLICKED in %.0fms, cursor after=(%d,%d)" % (label, (time.time()-t0)*1000, after["x"], after["y"]), flush=True)
    finally:
        ptr.close()
    return 0
sys.exit(main())
