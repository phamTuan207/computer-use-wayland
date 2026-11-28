#!/bin/bash
# Y8 E1 infra start (FROZEN v2): driver (hand_drive_e1.py on WD port 4451)
# + fixture HTTP server (port 8767). Records exact PIDs to /tmp/e1/*.pid
# files with cmdline snapshots. No pkill anywhere. Fails closed.
# Run ONLY when no other executor is on Zen (Y4d complete, handover in force).
# Usage: worker-y8-start-infra.sh
set -u

fail() { echo "START_FAIL: $1" >&2; exit 1; }

# I2: fail closed on stale infra. Never start over a live old driver.
for port in 4451 8767; do
  if ss -ltn 2>/dev/null | grep -q ":$port "; then fail "port $port already bound"; fi
done
for f in /tmp/e1/holder.pid /tmp/e1/driver.pid /tmp/e1/http.pid; do
  if [ -f "$f" ]; then
    p=$(cat "$f" 2>/dev/null)
    if [ -n "$p" ] && kill -0 "$p" 2>/dev/null; then fail "stale pidfile $f still live (pid $p); run stop-infra.sh first"; fi
  fi
done
if pgrep -x geckodriver >/dev/null 2>&1; then fail "a geckodriver is already running; run stop-infra.sh / check other workers first"; fi
[ -x /tmp/geckodriver ] || fail "/tmp/geckodriver missing"

cd ~/workspace/computer-use-wayland
sed 's/WD_PORT = 4450/WD_PORT = 4451/' tests/realistic/hand_drive.py > /tmp/e1/hand_drive_e1.py
python3 -m py_compile /tmp/e1/hand_drive_e1.py || fail "py_compile failed"
# I1: verify the sed replacement actually took.
grep -q "WD_PORT = 4451" /tmp/e1/hand_drive_e1.py || fail "sed did not set WD_PORT = 4451"

rm -f /tmp/e1/fifo /tmp/e1/holder.pid /tmp/e1/driver.pid /tmp/e1/http.pid
mkfifo /tmp/e1/fifo
# Archive the previous driver log instead of destroying it.
if [ -s /tmp/e1/out.log ]; then
  mv /tmp/e1/out.log "/tmp/e1/out-archived-$(date +%Y%m%d-%H%M%S).log"
fi
: > /tmp/e1/out.log
# Holder with an identifiable cmdline marker (e1-fifo-holder) so the stop
# script can verify its identity before killing it. The exec -a marker is
# the process name; the open of the FIFO blocks until the driver reads it.
setsid bash -c 'exec 9>/tmp/e1/fifo; exec -a e1-fifo-holder sleep 7200' &
echo $! > /tmp/e1/holder.pid
setsid nohup python3 /tmp/e1/hand_drive_e1.py < /tmp/e1/fifo >> /tmp/e1/out.log 2>&1 &
echo $! > /tmp/e1/driver.pid
setsid nohup python3 -m http.server 8767 --bind 127.0.0.1 --directory tests/realistic/agy-q2/fixtures > /tmp/e1/http-8767.log 2>&1 &
echo $! > /tmp/e1/http.pid
# Cmdline snapshots next to the PIDs (PID reuse guard for the stop script).
rm -f /tmp/e1/pids.txt
for role in holder driver http; do
  p=$(cat /tmp/e1/$role.pid)
  echo "$p $(tr '\0' ' ' < /proc/$p/cmdline 2>/dev/null)" >> /tmp/e1/pids.txt
done
sleep 3
# I1: verify BOTH ports listening, fail closed.
for port in 4451 8767; do
  ss -ltn 2>/dev/null | grep -q ":$port " || fail "port $port not listening after start"
done
curl -s --max-time 5 -o /dev/null -w "fixture http %{http_code}\n" http://127.0.0.1:8767/test-05-contact-book.html | grep -q "200" || fail "fixture HTTP not 200"
ps -eo pid,etime,cmd | grep "[h]and_drive_e1" | head -2
date "+INFRA_UP %F %T %Z"
