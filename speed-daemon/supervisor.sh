#!/bin/bash
# supervisor.sh - keep the speed daemon alive without cron/systemd.
# This VM has NO cron daemon (no crontab/crond binaries, no cron.service)
# and no user systemd bus, so the watchdog runs as a detached supervisor
# loop instead: every 60s it runs watchdog.py, which pings the daemon
# socket and restarts the daemon if it does not answer.
#
#   ~/workspace/speed-daemon/supervisor.sh start|stop|status
#
# The supervisor is a separate process from the daemon, so killing the
# daemon does NOT kill the supervisor: it revives the daemon within ~60s.
# CAVEAT: a VM replacement kills both. After a replacement, run
#   ~/workspace/speed-daemon/daemon.sh start
#   ~/workspace/speed-daemon/supervisor.sh start
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$DIR/supervisor.pid"
LOG="$DIR/supervisor.log"

case "${1:-}" in
  start)
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
      echo "supervisor already running (pid $(cat "$PID_FILE"))"; exit 0; fi
    setsid nohup bash -c "while true; do python3 $DIR/watchdog.py >> $DIR/watchdog.log 2>&1; sleep 60; done" >> "$LOG" 2>&1 < /dev/null &
    echo $! > "$PID_FILE"
    echo "$(TZ=Asia/Ho_Chi_Minh date '+%Y-%m-%d %H:%M:%S %Z') supervisor_start pid=$(cat "$PID_FILE")" >> "$LOG"
    echo "supervisor started (pid $(cat "$PID_FILE"))"
    ;;
  stop)
    [ -f "$PID_FILE" ] && kill "$(cat "$PID_FILE")" 2>/dev/null
    pkill -f "watchdog.py" 2>/dev/null
    echo "$(TZ=Asia/Ho_Chi_Minh date '+%Y-%m-%d %H:%M:%S %Z') supervisor_stop pid=$(cat "$PID_FILE" 2>/dev/null)" >> "$LOG"
    rm -f "$PID_FILE"
    echo "supervisor stopped"
    ;;
  status)
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
      echo "supervisor running (pid $(cat "$PID_FILE"))"
      tail -n 3 "$DIR/watchdog.log" 2>/dev/null
    else
      echo "supervisor NOT running"; exit 1
    fi
    ;;
  *)
    echo "usage: $0 start|stop|status"; exit 2
    ;;
esac
