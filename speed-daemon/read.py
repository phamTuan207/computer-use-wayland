#!/usr/bin/env python3
"""Read-back client for the speed daemon (read-only).

  python3 read.py --recipient mei [--count 5]
  python3 read.py --recipient mochi [--count 5]

Fetches the most recent assistant replies from that recipient's Muse chat
tab (mei in Brave on 9224, mochi in Chromium on 9223) via the same CDP
path the daemon uses, and prints them verbatim. It does NOT send anything,
NOT type, NOT click, and NOT modify the tab. Read-only.

How it works (no daemon socket, no pill):
  - Uses the same mux SSH helper as the daemon (ssh-laptop-mux.sh,
    CU_LAPTOP_SSH defaults to james@100.70.92.52) to reach the laptop.
  - Ensures /tmp/daemon-read.mjs exists on the laptop (pushes it if
    missing, same pattern as daemon.py), then runs it with node.
  - daemon-read.mjs fetches /json/list, finds the tab by target id,
    opens a WebSocket, and runs a Runtime.evaluate that only READS the
    [data-message-item] bubbles. No pill is acquired: a read is not agent
    control, and the script never runs cu.py session-driver, so it cannot
    collide with the session guardian.

What it returns:
  - Human summary: recipient, total bubbles, assistant count, and each
    returned message (index, role, side, time if present, full text).
  - The full JSON from daemon-read.mjs (one line).
  - Exit 0 iff ok. A missing tab, a CDP failure, or an empty assistant
    list is reported as ok=false or returned=0, never faked.

Limits:
  - Returns the most recent N assistant messages (role !== 'user'),
    default 5, oldest-first. Use --count to change N.
  - Timestamps: the Muse UI shows group timestamps as separators between
    bubbles, not inside them, so per-message time is often null. When a
    bubble carries a <time> element, its text and datetime are returned.
  - Only messages currently in the DOM are visible. If the chat uses
    virtual scrolling, very old messages may not be present.
  - Text is the bubble's textContent verbatim (may include minor UI
    chrome such as a Copy button label).
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Asia/Ho_Chi_Minh")
except Exception:
    TZ = timezone.utc

HERE = Path(__file__).resolve().parent
REPO_SCRIPTS = Path.home() / "workspace" / "computer-use-wayland" / "scripts"
MUX_SSH = str(REPO_SCRIPTS / "ssh-laptop-mux.sh")
SSH_LAPTOP = str(Path.home() / "workspace" / "ssh-laptop.sh")
READ_MJS = HERE / "daemon-read.mjs"

RECIPIENTS = {
    "mei": {"endpoint": "http://127.0.0.1:9224", "target": "709E2AE0F1CE0F9C9B57536626782E2D"},
    "mochi": {"endpoint": "http://127.0.0.1:9223", "target": "A25AA6F0370A00A174BC5304A333417D"},
}
SSH_TIMEOUT = 90


def hcm_now():
    return datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S %Z")


def mux_env():
    env = dict(os.environ)
    env.setdefault("CU_LAPTOP_SSH", "james@100.70.92.52")
    return env


def ssh_mux(remote_cmd, timeout=SSH_TIMEOUT):
    p = subprocess.run([MUX_SSH, remote_cmd], capture_output=True,
                       text=True, timeout=timeout, env=mux_env())
    return p.returncode, p.stdout, p.stderr


def ensure_laptop_file():
    import hashlib
    local_md5 = hashlib.md5(READ_MJS.read_bytes()).hexdigest()
    rc, out, _err = ssh_mux("md5sum /tmp/daemon-read.mjs 2>&1")
    if rc == 0 and local_md5 in out:
        return True
    with open(READ_MJS, "rb") as f:
        data = f.read()
    p = subprocess.run([SSH_LAPTOP, "cat > /tmp/daemon-read.mjs"],
                       input=data, capture_output=True, timeout=60)
    return p.returncode == 0


def do_read(recipient, count):
    cfg = RECIPIENTS[recipient]
    t0 = time.monotonic()
    wall_start = hcm_now()
    if not ensure_laptop_file():
        return {"ok": False, "error": "could not push daemon-read.mjs to laptop"}
    remote = "node /tmp/daemon-read.mjs %s %s %d" % (
        cfg["endpoint"], cfg["target"], count)
    try:
        rc, out, err = ssh_mux(remote)
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "ssh timeout"}
    elapsed = time.monotonic() - t0
    result = None
    for line in reversed(out.strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                result = json.loads(line)
                break
            except ValueError:
                continue
    if result is None:
        return {"ok": False, "error": "no JSON from laptop read (rc=%d): %s" % (
            rc, (out + err).strip()[-300:])}
    result["wall_start_hcm"] = wall_start
    result["wall_end_hcm"] = hcm_now()
    result["elapsed_s"] = round(elapsed, 3)
    result["recipient"] = recipient
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--recipient", choices=["mei", "mochi"], required=True)
    ap.add_argument("--count", type=int, default=5)
    ap.add_argument("--raw", action="store_true",
                    help="print only the JSON, no human summary")
    args = ap.parse_args()
    resp = do_read(args.recipient, args.count)
    if args.raw:
        print(json.dumps(resp, ensure_ascii=False))
        return 0 if resp.get("ok") else 1
    print("daemon read: recipient=%s ok=%s total_items=%s assistant_count=%s returned=%s elapsed_s=%s" % (
        args.recipient, resp.get("ok"), resp.get("total_items"),
        resp.get("assistant_count"), resp.get("returned"), resp.get("elapsed_s")))
    if resp.get("error"):
        print("  error: %s" % resp["error"])
    for m in resp.get("messages") or []:
        print("--- message index=%s role=%s side=%s time=%s time_attr=%s ---" % (
            m.get("index"), m.get("role"), m.get("side"),
            m.get("time"), m.get("time_attr")))
        print(m.get("text") or "")
    print(json.dumps(resp, ensure_ascii=False))
    return 0 if resp.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
