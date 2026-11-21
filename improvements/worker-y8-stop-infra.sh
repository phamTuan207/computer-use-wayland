#!/bin/bash
# Y8 E1 infra stop (FROZEN v2): kills ONLY E1's own PIDs (driver 4451,
# HTTP 8767). No pkill -f anywhere: PIDs come from /tmp/e1/*.pid files,
# each verified against /proc/<pid>/cmdline before TERM. Leftovers are
# found by scanning /proc cmdlines locally and killed by exact PID number.
# Closing the FIFO holder FIRST lets the driver's finally block delete the
# session and terminate geckodriver cleanly (SIGTERM would skip finally).
# Usage: worker-y8-stop-infra.sh

# I3: verify cmdline identity before killing a pidfile PID.
kill_pidfile() { # $1 = pidfile, $2 = label, $3 = expected cmdline substring
  if [ -f "$1" ]; then
    p=$(cat "$1" 2>/dev/null)
    if [ -n "$p" ] && kill -0 "$p" 2>/dev/null; then
      c=$(tr '\0' ' ' < /proc/$p/cmdline 2>/dev/null)
      case "$c" in
        *"$3"*) kill -TERM "$p" 2>/dev/null && echo "TERM $2 pid $p ($c)" ;;
        *) echo "SKIP $2 pid $p: cmdline mismatch ($c), not killing" ;;
      esac
    fi
  fi
}

kill_pidfile /tmp/e1/holder.pid holder "e1-fifo-holder"
sleep 3
# I4: verify the holder is actually dead before killing the driver.
# A non-interactive bash waiting on sleep may not exit promptly on TERM.
if [ -f /tmp/e1/holder.pid ]; then
  hp=$(cat /tmp/e1/holder.pid 2>/dev/null)
  if [ -n "$hp" ] && kill -0 "$hp" 2>/dev/null; then
    echo "holder pid $hp still alive after TERM; waiting up to 10 s more"
    for _ in $(seq 1 20); do sleep 0.5; kill -0 "$hp" 2>/dev/null || break; done
    if kill -0 "$hp" 2>/dev/null; then
      echo "holder still alive; killing its sleep child"
      for ch in $(pgrep -P "$hp" 2>/dev/null); do kill -TERM "$ch" 2>/dev/null; done
      sleep 2
    fi
    kill -0 "$hp" 2>/dev/null && echo "WARNING holder pid $hp still alive; driver kill proceeds anyway" || echo "holder confirmed dead"
  fi
fi
kill_pidfile /tmp/e1/driver.pid driver "hand_drive_e1.py"
kill_pidfile /tmp/e1/http.pid http "http.server 8767"
sleep 2
# Leftovers by /proc scan (exact PID kill only, never pattern kill)
for p in $(ls /proc 2>/dev/null | grep -E '^[0-9]+$'); do
  c=$(tr '\0' ' ' < /proc/$p/cmdline 2>/dev/null)
  case "$c" in
    *hand_drive_e1.py*|*"http.server 8767"*|*e1-fifo-holder*)
      echo "leftover pid $p: $c"
      kill -TERM "$p" 2>/dev/null
      ;;
  esac
done
sleep 2
# E1 geckodriver only: its cmdline carries --port 4451. A geckodriver on
# another port (for example Y4's 4448) is not E1's and is never touched.
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
# I8: final check filtered by port 4451; another port's geckodriver is not E1's.
e1gd=0
for p in $(pgrep -x geckodriver 2>/dev/null); do
  c=$(tr '\0' ' ' < /proc/$p/cmdline 2>/dev/null)
  case "$c" in *"--port 4451"*) e1gd=1; echo "E1 geckodriver STILL RUNNING pid $p";; esac
done
[ "$e1gd" = 0 ] && echo "no E1 geckodriver running"
date "+INFRA_DOWN %F %T %Z"
