#!/usr/bin/env python3
"""Client for the speed daemon (Unix socket, JSON lines).

  python3 send.py --ping
  python3 send.py --status
  python3 send.py --recipient mei --run 9 --message "Test toc do gui tin, lan 9, khong can lam gi. (daemon)"
Prints a human summary + the full response JSON. Exit 0 iff outcome == sent.
"""
import argparse
import json
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Asia/Ho_Chi_Minh")
except Exception:
    TZ = timezone.utc

SOCK = Path(__file__).resolve().parent / "daemon.sock"


def hcm_now():
    return datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S %Z")


def call(req, timeout=150):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect(str(SOCK))
    s.sendall((json.dumps(req, ensure_ascii=False) + "\n").encode("utf-8"))
    buf = b""
    while not buf.endswith(b"\n"):
        chunk = s.recv(65536)
        if not chunk:
            break
        buf += chunk
    s.close()
    return json.loads(buf.decode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ping", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--recipient", choices=["mei", "mochi"])
    ap.add_argument("--run", type=int)
    ap.add_argument("--message")
    args = ap.parse_args()
    if args.ping:
        print(json.dumps(call({"cmd": "ping"}), ensure_ascii=False))
        return 0
    if args.status:
        print(json.dumps(call({"cmd": "status"}), ensure_ascii=False, indent=2))
        return 0
    if not args.recipient or args.run is None or not args.message:
        ap.error("--recipient, --run and --message are required for a send")
    t0 = time.monotonic()
    wall_start = hcm_now()
    resp = call({"cmd": "send", "recipient": args.recipient,
                 "message": args.message, "run": args.run})
    wall_end = hcm_now()
    client_elapsed = time.monotonic() - t0
    node = resp.get("node") or {}
    v12 = node.get("v12") or {}
    print("daemon send: recipient=%s run=%d outcome=%s verified=%s" % (
        args.recipient, args.run, resp.get("outcome"), v12.get("found")))
    print("  wall: %s -> %s (+07), client elapsed %.2fs, daemon elapsed %ss" % (
        wall_start, wall_end, client_elapsed, resp.get("elapsed_s")))
    print("  breakdown: ipc_ms=%s ssh_ms=%s node_ms_total=%s "
          "node timings=%s" % (
              resp.get("ipc_ms"), resp.get("ssh_ms"), node.get("ms_total"),
              json.dumps(node.get("timings"), ensure_ascii=False)))
    print("  pill: %s" % json.dumps(resp.get("pill"), ensure_ascii=False))
    if resp.get("error"):
        print("  error: %s" % resp["error"])
    print(json.dumps(resp, ensure_ascii=False))
    return 0 if resp.get("outcome") == "sent" else 1


if __name__ == "__main__":
    sys.exit(main())
