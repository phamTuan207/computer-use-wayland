#!/bin/bash
source /home/james/backups/cu-final-0.57.2-20261114-225131/env.sh
refresh_gui >/dev/null 2>&1 || true
setsid -f kitty --single-instance=no --title h3-baseline-exec bash -c 'cd /home/james/computer-use-wayland && codex exec -m gpt-6-luna -c model_reasoning_effort="max" -s danger-full-access - < /tmp/speed-warmbrowser-20261120/h3-baseline/brief.md > /tmp/speed-warmbrowser-20261120/h3-baseline/codex.log 2>&1; echo "CODEX_EXIT=$?" > /tmp/speed-warmbrowser-20261120/h3-baseline/codex.done'
echo "launched h3-baseline-exec"
