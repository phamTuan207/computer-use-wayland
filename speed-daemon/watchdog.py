#!/usr/bin/env python3
"""watchdog.py - keep the speed daemon alive (run from cron every minute).

Pings the daemon socket; if it does not answer within 5s, restarts it via
daemon.sh restart. Logs every check that finds the daemon down (and every
restart) to watchdog.log with Asia/Ho_Chi_Minh wall time. Exits 0 when the
daemon is up (or was restarted), 1 only when the restart itself failed.

Cron line (install with `crontab -e`):
  * * * * * /usr/bin/python3 /home/hatch/workspace/speed-daemon/watchdog.py
"""
import json
import os
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Asia/Ho_Chi_Minh")
except Exception:
    TZ = timezone.utc

HERE = Path(__file__).resolve().parent
SOCK = HERE / "daemon.sock"
LOG = HERE / "watchdog.log"


def log(event, **fields):
    rec = {"ts_hcm": datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S %Z"),
           "event": event}
    rec.update(fields)
    with open(LOG, "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def ping():
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        s.connect(str(SOCK))
        s.sendall(b'{"cmd": "ping"}\n')
        data = s.recv(4096)
        return bool(data and json.loads(data.decode()).get("ok"))
    except Exception:
        return False
    finally:
        s.close()


def main():
    if ping():
        # R15 instrumentation: one heartbeat line per 60s cycle. A gap
        # longer than ~2 cycles means the supervisor loop itself died
        # (or the VM was replaced); that gap is the evidence for the
        # death class exit logging cannot capture.
        log("watchdog_heartbeat", daemon_up=True)
        return 0
    log("daemon_down_restarting", restarter="watchdog.py-supervisor-loop")
    env = dict(os.environ, DAEMON_RESTARTER="watchdog.py-supervisor-loop")
    p = subprocess.run([str(HERE / "daemon.sh"), "restart"],
                       capture_output=True, text=True, timeout=120, env=env)
    up = ping()
    log("daemon_restart", rc=p.returncode, up=up,
        restarter="watchdog.py-supervisor-loop",
        out=(p.stdout + p.stderr)[-300:])
    return 0 if up else 1


if __name__ == "__main__":
    sys.exit(main())
