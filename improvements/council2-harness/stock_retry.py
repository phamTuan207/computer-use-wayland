#!/usr/bin/env python3
"""Council-2 stock 0b retry: pre-create the profile dir (mkdir) so Zen does
not show Profile Missing, launch with NO automation flags, observe the new
window, record. Holds the pill. Stdlib only (ponytail)."""
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path.home() / "computer-use-wayland" / "scripts"))
from first_action import acquire_overlay, overlay_visible, release_overlay  # noqa: E402

OUT = Path("/tmp/council2-evidence")
LOG = OUT / "run6-stock.log"
AGENT = "Council-2"
METHOD = "BiDi test"


def log(obj):
    line = json.dumps({"wall": datetime.now().astimezone().isoformat(timespec="seconds"), **obj})
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def zen_env():
    pid = subprocess.run(["pgrep", "-f", "zen-bin --remote-debugging-port"],
                         capture_output=True, text=True).stdout.split()[0]
    env = {}
    for kv in Path(f"/proc/{pid}/environ").read_bytes().split(b"\x00"):
        if b"=" in kv:
            k, v = kv.decode(errors="replace").split("=", 1)
            env[k] = v
    keep = {k: env[k] for k in ("WAYLAND_DISPLAY", "XDG_RUNTIME_DIR", "DBUS_SESSION_BUS_ADDRESS", "HYPRLAND_INSTANCE_SIGNATURE", "DISPLAY") if k in env}
    log({"step": "zen_env", "pid": pid, "keys": sorted(keep.keys())})
    return keep


def stock_observe(url, tag, env, wait_s=25):
    profile = Path(f"/tmp/zen-stock6-{tag}")
    subprocess.run(["rm", "-rf", str(profile)])
    profile.mkdir(parents=True, exist_ok=True)
    full_env = dict(os.environ)
    full_env.update(env)
    before = subprocess.run(["computer-use", "windows"], capture_output=True, text=True, timeout=60, env=full_env).stdout
    before_addrs = {w["address"] for w in json.loads(before)}
    log({"step": "stock_launch", "tag": tag, "url": url[:80]})
    proc = subprocess.Popen(["/opt/zen-browser-bin/zen-bin", "--profile", str(profile), "--no-remote", url],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=full_env)
    time.sleep(wait_s)
    after = subprocess.run(["computer-use", "windows"], capture_output=True, text=True, timeout=60, env=full_env).stdout
    new_wins = [w for w in json.loads(after) if w["address"] not in before_addrs]
    log({"step": "stock_windows", "tag": tag, "new": [(w["class"], w["title"][:60], w["address"]) for w in new_wins]})
    for w in new_wins:
        if w["class"] == "zen":
            p = subprocess.run(["computer-use", "observe", "--window", w["address"], "--focus"],
                               capture_output=True, text=True, timeout=120, env=full_env)
            log({"step": "stock_observe", "tag": tag, "rc": p.returncode, "out": p.stdout[:600], "err": p.stderr[:200]})
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=10)
    subprocess.run(["rm", "-rf", str(profile)])
    log({"step": "stock_done", "tag": tag, "profile_deleted": True})


def main():
    log({"step": "runner6_start"})
    reply = acquire_overlay(AGENT, METHOD)
    log({"step": "pill_acquired", "visible": overlay_visible(AGENT), "label": reply.get("label")})
    try:
        env = zen_env()
        probe = "data:text/html,<title>wdprobe</title><body><h1 id=w>?</h1><script>document.getElementById('w').textContent='webdriver='+navigator.webdriver</script></body>"
        stock_observe(probe, "probe", env, 15)
        stock_observe("https://coolors.co", "coolors", env, 30)
        stock_observe("https://chatgpt.com", "chatgpt", env, 30)
    finally:
        err = release_overlay(AGENT)
        log({"step": "pill_released", "error": err, "visible_after": overlay_visible(AGENT)})
    log({"step": "runner6_done"})


if __name__ == "__main__":
    main()
