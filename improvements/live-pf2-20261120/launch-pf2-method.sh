#!/bin/bash
source /home/james/backups/cu-final-0.57.2-20261114-225131/env.sh
refresh_gui >/dev/null 2>&1 || true
setsid -f kitty --single-instance=no --title pf2-method-exec bash -c 'cd /home/james/computer-use-wayland && codex exec -m gpt-6-luna -c model_reasoning_effort="max" -s danger-full-access - < /tmp/live-pf2-20261120/pf2-method/brief.md > /tmp/live-pf2-20261120/pf2-method/codex.log 2>&1'
echo "launched pf2-method-exec"
