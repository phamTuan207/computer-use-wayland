#!/bin/bash
# E1 infra stop: kill the E1 driver, its holder, its geckodriver, and the
# E1 HTTP server. Only kills OUR pids/ports (4451, 8767). Never pkill -f.
# Usage: stop-infra.sh
pkill -f "hand_drive_e1.py" 2>/dev/null
pkill -f "http.server 8767" 2>/dev/null
sleep 1
ps -eo pid,cmd | grep -E "[h]and_drive_e1|[h]ttp.server 8767" | head
ss -ltn 2>/dev/null | grep -E "4451|8767" || echo "ports 4451 and 8767 free"
pgrep -x geckodriver || echo "no geckodriver running"
date "+INFRA_DOWN %F %T %Z"
