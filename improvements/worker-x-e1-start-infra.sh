#!/bin/bash
# E1 infra start: driver (hand_drive_e1.py on WD port 4451) + fixture
# HTTP server (port 8767). Run ONLY when no other executor is on Zen.
# Usage: start-infra.sh
set -u
cd ~/workspace/computer-use-wayland
sed 's/WD_PORT = 4450/WD_PORT = 4451/' tests/realistic/hand_drive.py > /tmp/e1/hand_drive_e1.py
python3 -m py_compile /tmp/e1/hand_drive_e1.py || exit 1
rm -f /tmp/e1/fifo
mkfifo /tmp/e1/fifo
: > /tmp/e1/out.log
( exec 9>/tmp/e1/fifo; sleep 7200 ) &
echo "holder pid $!"
setsid nohup python3 /tmp/e1/hand_drive_e1.py < /tmp/e1/fifo >> /tmp/e1/out.log 2>&1 &
echo "driver pid $!"
setsid nohup python3 -m http.server 8767 --bind 127.0.0.1 --directory tests/realistic/agy-q2/fixtures > /tmp/e1/http-8767.log 2>&1 &
echo "http pid $!"
sleep 3
ss -ltn 2>/dev/null | grep -E "4451|8767" || netstat -ltn 2>/dev/null | grep -E "4451|8767"
curl -s --max-time 5 -o /dev/null -w "fixture http %{http_code}\n" http://127.0.0.1:8767/test-05-contact-book.html
ps -eo pid,etime,cmd | grep "[h]and_drive_e1" | head -2
date "+INFRA_UP %F %T %Z"
