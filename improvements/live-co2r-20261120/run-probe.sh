#!/bin/bash
# Scripted diff-delivery probe (coordinator-run, zero model calls).
# Branch change-only-obs 37f7c63, CU_CODE_EXEC=1. Terminal co2r-probe-term.
source /home/james/backups/cu-final-0.57.2-20261114-225131/env.sh
refresh_gui >/dev/null 2>&1 || true
live_dir=$(find /run/user/1000/hypr -mindepth 1 -maxdepth 1 -type d -exec test -f '{}/hyprland.lock' \; -print | head -1)
export HYPRLAND_INSTANCE_SIGNATURE="$(basename "$live_dir")"
RUN=/tmp/live-co2r-20261120/probe
LOG=$RUN/probe-driver2.log
exec > "$LOG" 2>&1
date '+START %H:%M:%S.%3N'
setsid -f kitty --single-instance=no --title co2r-probe-term
sleep 3
hyprctl clients -j | python3 -c 'import json,sys; ws=json.load(sys.stdin); xs=[w for w in ws if w.get("title")=="co2r-probe-term"]; print(json.dumps({"count":len(xs),"windows":[{"address":w["address"]} for w in xs]})); assert len(xs)==1'
mkdir -p ~/.cache/agent-computer-use/leases/co2r-probe2
chmod 700 ~/.cache/agent-computer-use/leases/co2r-probe2
python3 "$RUN/timed.py" --log "$RUN/records2.jsonl" start --owner co2r-probe2 --lease-file ~/.cache/agent-computer-use/leases/co2r-probe2/probe.lease --label probe2-start
python3 -c 'import json; json.dump({"args": ["code-exec", "--program", "/tmp/live-co2r-20261120/probe/probe1.py", "--intent", "diff delivery probe: type x, observe diff"]}, open("/tmp/live-co2r-20261120/probe/probe-req2.json", "w"))'
chmod 600 "$RUN/probe-req2.json"
python3 "$RUN/timed.py" --log "$RUN/records2.jsonl" req --lease-file ~/.cache/agent-computer-use/leases/co2r-probe2/probe.lease --seq 1 --request "$RUN/probe-req2.json" --label probe2-codeexec
python3 "$RUN/timed.py" --log "$RUN/records2.jsonl" finish --lease-file ~/.cache/agent-computer-use/leases/co2r-probe2/probe.lease --label probe2-finish
hyprctl eval 'local matches = {}; for _, w in ipairs(hl.get_windows()) do if w.title == "co2r-probe-term" then table.insert(matches, w) end end; assert(#matches == 1, "expected exactly one test terminal"); hl.dispatch(hl.dsp.window.close({ window = matches[1] }))'
sleep 2
hyprctl clients -j | python3 -c 'import json,sys; ws=json.load(sys.stdin); xs=[w for w in ws if w.get("title")=="co2r-probe-term"]; print(json.dumps({"test_window_count_after_close":len(xs)}))'
if hyprctl clients -j | python3 -c 'import json,sys; ws=json.load(sys.stdin); xs=[w for w in ws if w.get("title")=="co2r-probe-term"]; sys.exit(0 if len(xs)==0 else 1)'; then
  echo CLOSE-OK
else
  echo CLOSE-RETRY
  hyprctl eval 'local matches = {}; for _, w in ipairs(hl.get_windows()) do if w.title == "co2r-probe-term" then table.insert(matches, w) end end; assert(#matches == 1, "expected exactly one test terminal"); hl.dispatch(hl.dsp.window.close({ window = matches[1] }))'
  sleep 2
  hyprctl clients -j | python3 -c 'import json,sys; ws=json.load(sys.stdin); xs=[w for w in ws if w.get("title")=="co2r-probe-term"]; print(json.dumps({"test_window_count_after_retry":len(xs)})); assert len(xs)==0'
fi
date '+END %H:%M:%S.%3N'
echo PROBE-DRIVER-DONE
