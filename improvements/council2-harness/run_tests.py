#!/usr/bin/env python3
"""Council-2 live test runner. Holds the pill for the whole run, then:
 1. baseline BiDi (run Zen, no preload)
 2. private user-context BiDi
 3. preload BiDi (candidate 3a)
 4. stock launch temp profile, no flags (decisive check 0b), grim screenshots
Writes /tmp/council2-evidence/run.log plus screenshots. Ponytail: stdlib only,
reuse overlay + first_action acquire pattern from computer-use-wayland.
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path.home() / "computer-use-wayland" / "scripts"))
import overlay as overlay_mod  # noqa: E402
from first_action import acquire_overlay, overlay_visible, release_overlay  # noqa: E402

OUT = Path("/tmp/council2-evidence")
OUT.mkdir(parents=True, exist_ok=True)
LOG = OUT / "run.log"
AGENT = "Council-2"
METHOD = "BiDi test"


def log(obj):
    line = json.dumps({"wall": datetime.now().astimezone().isoformat(timespec="seconds"), **obj})
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def run_cmd(cmd, timeout_s, tag):
    start = time.monotonic()
    log({"step": "cmd_start", "tag": tag, "cmd": cmd[:3]})
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s)
        elapsed = round(time.monotonic() - start, 1)
        for line in p.stdout.splitlines():
            log({"step": "cmd_out", "tag": tag, "line": line[:2000]})
        if p.stderr.strip():
            log({"step": "cmd_err", "tag": tag, "stderr": p.stderr[:1000]})
        log({"step": "cmd_done", "tag": tag, "rc": p.returncode, "elapsed_s": elapsed})
        return p.returncode
    except subprocess.TimeoutExpired:
        log({"step": "cmd_timeout", "tag": tag, "timeout_s": timeout_s})
        return -1


def stock_test(url, tag, wait_s=25):
    profile = f"/tmp/zen-stock-{tag}"
    subprocess.run(["rm", "-rf", profile])
    cmd = ["/opt/zen-browser-bin/zen-bin", "-P", profile, "--no-remote", url]
    log({"step": "stock_launch", "tag": tag, "url": url, "profile": profile})
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(wait_s)
    shot = OUT / f"stock-{tag}.png"
    r = subprocess.run(["grim", str(shot)], capture_output=True, text=True, timeout=30)
    size = shot.stat().st_size if shot.exists() else 0
    log({"step": "stock_screenshot", "tag": tag, "file": str(shot), "bytes": size, "grim_rc": r.returncode})
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=10)
    subprocess.run(["rm", "-rf", profile])
    log({"step": "stock_done", "tag": tag, "pid": proc.pid, "profile_deleted": True})


def main():
    log({"step": "runner_start", "agent": AGENT})
    reply = acquire_overlay(AGENT, METHOD)
    log({"step": "pill_acquired", "reply": reply, "visible": overlay_visible(AGENT)})
    try:
        node = ["node", "/tmp/council2-harness/bidi_test.mjs"]
        run_cmd(node + ["baseline", str(OUT)], 300, "baseline")
        log({"step": "pill_check_after_baseline", "visible": overlay_visible(AGENT)})
        run_cmd(node + ["private", str(OUT)], 300, "private")
        run_cmd(node + ["preload", str(OUT)], 300, "preload")
        log({"step": "pill_check_after_preload", "visible": overlay_visible(AGENT)})
        probe = "data:text/html,<title>wdprobe</title><body><h1 id=w>?</h1><script>document.getElementById('w').textContent='webdriver='+navigator.webdriver</script></body>"
        stock_test(probe, "probe", 15)
        stock_test("https://coolors.co", "coolors", 30)
        stock_test("https://chatgpt.com", "chatgpt", 30)
    finally:
        err = release_overlay(AGENT)
        log({"step": "pill_released", "error": err, "visible_after": overlay_visible(AGENT)})
    log({"step": "runner_done"})


if __name__ == "__main__":
    main()
