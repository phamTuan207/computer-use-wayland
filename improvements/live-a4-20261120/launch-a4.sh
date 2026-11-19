#!/bin/bash
source /home/james/backups/cu-final-0.57.2-20261114-225131/env.sh
refresh_gui >/dev/null 2>&1 || true
setsid -f kitty --single-instance=no --title a4-exec bash -c 'cd /home/james/computer-use-wayland && codex exec -m gpt-6-luna -c model_reasoning_effort="max" -s danger-full-access - < /tmp/speed-a4-20261120/a4-measure/brief-a4.md > /tmp/speed-a4-20261120/a4-measure/codex.log 2>&1'
echo "launched a4-exec"
