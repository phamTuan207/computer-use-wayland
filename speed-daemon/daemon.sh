#!/bin/bash
# daemon.sh - start | stop | restart | status for the speed daemon.
# One-command (re)start after a VM replacement:
#   ~/workspace/speed-daemon/daemon.sh start
# (then re-install the cron watchdog, see README.md.)
set -u
export CU_LAPTOP_SSH="${CU_LAPTOP_SSH:-james@100.70.92.52}"
DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$DIR/daemon.pid"
SOCK="$DIR/daemon.sock"

is_up() {
  [ -S "$SOCK" ] && python3 "$DIR/send.py" --ping >/dev/null 2>&1
}

case "${1:-}" in
  start)
    if is_up; then echo "speed-daemon already running"; exit 0; fi
    [ -f "$PID_FILE" ] && kill "$(cat "$PID_FILE")" 2>/dev/null; sleep 1
    setsid nohup python3 "$DIR/daemon.py" >> "$DIR/daemon.out" 2>&1 < /dev/null &
    for _ in $(seq 1 20); do sleep 0.5; is_up && break; done
    if is_up; then echo "speed-daemon started (pid $(cat "$PID_FILE" 2>/dev/null))"; exit 0; else
      echo "speed-daemon FAILED to start; see $DIR/daemon.out"; exit 1; fi
    ;;
  stop)
    if [ -f "$PID_FILE" ]; then kill "$(cat "$PID_FILE")" 2>/dev/null; fi
    for _ in $(seq 1 10); do sleep 0.5; [ -S "$SOCK" ] || break; done
    rm -f "$SOCK" "$PID_FILE"
    echo "speed-daemon stopped"
    ;;
  restart)
    "$0" stop; "$0" start
    ;;
  status)
    if is_up; then python3 "$DIR/send.py" --status; else echo "speed-daemon NOT running"; exit 1; fi
    ;;
  *)
    echo "usage: $0 start|stop|restart|status"; exit 2
    ;;
esac
