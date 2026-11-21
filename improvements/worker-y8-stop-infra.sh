#!/bin/bash
# Y8 E1 infra stop: kills ONLY E1's own PIDs (driver 4451, HTTP 8767).
# No pkill -f anywhere: PIDs come from /tmp/e1/*.pid files, leftovers are
# found by scanning /proc cmdlines locally and killed by exact PID number.
# Closing the FIFO holder FIRST lets the driver's finally block delete the
# session and terminate geckodriver cleanly (SIGTERM would skip finally).
# Usage: worker-y8-stop-infra.sh
kill_pidfile() { # $1 = pidfile, $2 = label
  if [ -f "$1" ]; then
    p=$(cat "$1" 2>/dev/null)
    if [ -n "$p" ] && kill -0 "$p" 2>/dev/null; then
      kill -TERM "$p" 2>/dev/null && echo "TERM $2 pid $p"
    fi
  fi
}
kill_pidfile /tmp/e1/holder.pid holder
sleep 3
kill_pidfile /tmp/e1/driver.pid driver
kill_pidfile /tmp/e1/http.pid http
sleep 2
# Leftovers by /proc scan (exact PID kill only, never pattern kill)
for p in $(ls /proc 2>/dev/null | grep -E '^[0-9]+$'); do
  c=$(tr '\0' ' ' < /proc/$p/cmdline 2>/dev/null)
  case "$c" in
    *hand_drive_e1.py*|*"http.server 8767"*)
      echo "leftover pid $p: $c"
      kill -TERM "$p" 2>/dev/null
      ;;
  esac
done
sleep 2
# E1 geckodriver only: its cmdline carries --port 4451
for p in $(pgrep -x geckodriver 2>/dev/null); do
  c=$(tr '\0' ' ' < /proc/$p/cmdline 2>/dev/null)
  case "$c" in
    *"--port 4451"*)
      echo "leftover geckodriver pid $p"
      kill -TERM "$p" 2>/dev/null
      ;;
  esac
done
sleep 1
ps -eo pid,cmd | grep -E "[h]and_drive_e1|[h]ttp.server 8767" | head
ss -ltn 2>/dev/null | grep -E "4451|8767" || echo "ports 4451 and 8767 free"
pgrep -x geckodriver || echo "no geckodriver running"
date "+INFRA_DOWN %F %T %Z"
