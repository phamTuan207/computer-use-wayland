#!/bin/bash
# E1 step driver: send one JSON command to the running hand_drive_e1.py
# via FIFO, wait for the result line, print it.
# Usage: step.sh '<json>'
# Prints one JSON line: {"ok": true, "result": ..., "ms": N}
# or {"ok": false, "error": ...}. Exit 0 on ok, 1 on error/timeout.
FIFO=/tmp/e1/fifo
LOG=/tmp/e1/out.log
if [ ! -p "$FIFO" ]; then
  echo '{"ok":false,"error":"fifo missing, driver not running"}'
  exit 1
fi
before=$(wc -l < "$LOG" 2>/dev/null || echo 0)
if ! timeout 10 bash -c 'printf "%s\n" "$1" > "$2"' _ "$1" "$FIFO"; then
  echo '{"ok":false,"error":"timeout writing to fifo, driver may be dead"}'
  exit 1
fi
for _ in $(seq 1 60); do
  after=$(wc -l < "$LOG" 2>/dev/null || echo 0)
  if [ "$after" -gt "$before" ]; then
    tail -n +"$((before+1))" "$LOG"
    exit 0
  fi
  sleep 0.5
done
echo '{"ok":false,"error":"timeout waiting for driver output (30s)"}'
exit 1
