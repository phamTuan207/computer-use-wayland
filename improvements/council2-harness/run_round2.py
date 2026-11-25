#!/usr/bin/env python3
"""Council-2 round 2: user-way BiDi tests (baseline + preload) and stock 0b
redo with display env exported from the live Zen process. Holds the pill.
Stdlib only, reuse overlay acquire pattern (ponytail)."""
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
LOG = OUT / "run2.log"
AGENT = "Council-2"
METHOD = "BiDi test"


def log(obj):
    line = json.dumps({"wall": datetime.now().astimezone().isoformat(timespec="seconds"), **obj})
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def run_cmd(cmd, timeout_s, tag):
    start = time.monotonic()
    log({"step": "cmd_start", "tag": tag})
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s)
        for line in p.stdout.splitlines():
            log({"step": "cmd_out", "tag": tag, "line": line[:2000]})
        if p.stderr.strip():
            log({"step": "cmd_err", "tag": tag, "stderr": p.stderr[:1000]})
        log({"step": "cmd_done", "tag": tag, "rc": p.returncode, "elapsed_s": round(time.monotonic() - start, 1)})
    except subprocess.TimeoutExpired:
        log({"step": "cmd_timeout", "tag": tag, "timeout_s": timeout_s})


def zen_env():
    """Display env from the live run Zen process (grim needs WAYLAND_DISPLAY)."""
    pid = subprocess.run(["pgrep", "-f", "zen-bin --remote-debugging-port"],
                         capture_output=True, text=True).stdout.split()[0]
    env = {}
    raw = Path(f"/proc/{pid}/environ").read_bytes().split(b"\x00")
    for kv in raw:
        if b"=" in kv:
            k, v = kv.decode(errors="replace").split("=", 1)
            env[k] = v
    keep = {k: env[k] for k in ("WAYLAND_DISPLAY", "XDG_RUNTIME_DIR", "DBUS_SESSION_BUS_ADDRESS", "HYPRLAND_INSTANCE_SIGNATURE", "DISPLAY") if k in env}
    log({"step": "zen_env", "pid": pid, "keys": sorted(keep.keys())})
    return keep


def stock_test(url, tag, env, wait_s=30):
    profile = f"/tmp/zen-stock2-{tag}"
    subprocess.run(["rm", "-rf", profile])
    full_env = dict(os.environ)
    full_env.update(env)
    log({"step": "stock_launch", "tag": tag, "url": url[:80]})
    proc = subprocess.Popen(["/opt/zen-browser-bin/zen-bin", "-P", profile, "--no-remote", url],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=full_env)
    time.sleep(wait_s)
    shot = OUT / f"stock2-{tag}.png"
    r = subprocess.run(["grim", str(shot)], capture_output=True, text=True, timeout=30, env=full_env)
    size = shot.stat().st_size if shot.exists() else 0
    log({"step": "stock_screenshot", "tag": tag, "file": str(shot), "bytes": size,
         "grim_rc": r.returncode, "grim_err": r.stderr[:200]})
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=10)
    subprocess.run(["rm", "-rf", profile])
    log({"step": "stock_done", "tag": tag, "profile_deleted": True})


def main():
    log({"step": "runner2_start"})
    reply = acquire_overlay(AGENT, METHOD)
    log({"step": "pill_acquired", "visible": overlay_visible(AGENT), "label": reply.get("label")})
    try:
        node = ["node", "/tmp/council2-harness/bidi_userway.mjs"]
        run_cmd(node + ["baseline", str(OUT)], 600, "uw-baseline")
        run_cmd(node + ["preload", str(OUT)], 600, "uw-preload")
        env = zen_env()
        probe = "data:text/html,<title>wdprobe</title><body><h1 id=w>?</h1><script>document.getElementById('w').textContent='webdriver='+navigator.webdriver</script></body>"
        stock_test(probe, "probe", env, 15)
        stock_test("https://coolors.co", "coolors", env, 30)
        stock_test("https://chatgpt.com", "chatgpt", env, 30)
    finally:
        err = release_overlay(AGENT)
        log({"step": "pill_released", "error": err, "visible_after": overlay_visible(AGENT)})
    log({"step": "runner2_done"})


if __name__ == "__main__":
    main()
