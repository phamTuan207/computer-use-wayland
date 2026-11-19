#!/bin/bash
# Scripted prefetch adoption re-measure (coordinator-run, zero model calls).
# Branch harness-prefetch 7c840d7, CU_PRECAPTURE=0.
# Question: does open https://example.com/ adopt a prefetch of https://example.com
# after the _normalize_prefetch_url fix (commit 7c840d7)?
# TEST BASELINE: fresh open https://example.com, NO prefetch (load_ms, prefetched flag, tab id, TTFI).
# TEST METHOD: prefetch https://example.com, sleep 3, open https://example.com/
# (prefetched flag, same tab id as prefetch?, load_ms near adopted ~13ms vs fresh ~50ms, TTFI).
source /home/james/backups/cu-final-0.57.2-20261114-225131/env.sh
refresh_gui >/dev/null 2>&1 || true
live_dir=$(find /run/user/1000/hypr -mindepth 1 -maxdepth 1 -type d -exec test -f '{}/hyprland.lock' \; -print | head -1)
export HYPRLAND_INSTANCE_SIGNATURE="$(basename "$live_dir")"
RUN=/tmp/live-pf3-20261120/pf3-probe
LOG=$RUN/probe-driver.log
mkdir -p "$RUN" ~/.cache/agent-computer-use/leases/pf3-probe
chmod 700 ~/.cache/agent-computer-use/leases/pf3-probe
exec > "$LOG" 2>&1
CLI="python3 /home/james/computer-use-wayland/scripts/chromium_cli.py"
date '+START %H:%M:%S.%3N'
python3 "$RUN/timed.py" --log "$RUN/records.jsonl" start --owner pf3-probe --lease-file ~/.cache/agent-computer-use/leases/pf3-probe/probe.lease --label probe-start
ls -l ~/.cache/agent-computer-use/session.json
python3 -c 'import json; json.dump({"args": ["browser", "start"]}, open("'$RUN'/probe-req-browser-start.json", "w"))'
chmod 600 "$RUN/probe-req-browser-start.json"
python3 "$RUN/timed.py" --log "$RUN/records.jsonl" req --lease-file ~/.cache/agent-computer-use/leases/pf3-probe/probe.lease --seq 1 --request "$RUN/probe-req-browser-start.json" --label probe-browser-start
echo '=== TEST BASELINE: open https://example.com, NO prefetch ==='
date '+BASE-OPEN-SUBMIT %H:%M:%S.%3N'
$CLI open https://example.com | tee "$RUN/base-open.result"
BASE_TAB=$(python3 -c 'import json; d=json.load(open("'$RUN'/base-open.result")); t=d.get("tab") or {}; print(t.get("id") or d.get("tab_id") or "")')
echo "BASE_TAB=$BASE_TAB"
date '+BASE-OBSERVE-SUBMIT %H:%M:%S.%3N'
python3 -c 'import json; json.dump({"args": ["browser", "observe", "--target", "'"$BASE_TAB"'", "--image"]}, open("'$RUN'/probe-req-base-observe.json", "w"))'
chmod 600 "$RUN/probe-req-base-observe.json"
python3 "$RUN/timed.py" --log "$RUN/records.jsonl" req --lease-file ~/.cache/agent-computer-use/leases/pf3-probe/probe.lease --seq 2 --request "$RUN/probe-req-base-observe.json" --label probe-base-observe
$CLI close "$BASE_TAB" | tee "$RUN/base-close.result"
sleep 1
echo '=== TEST METHOD: prefetch https://example.com, sleep 3, open https://example.com/ ==='
date '+METH-PREFETCH-SUBMIT %H:%M:%S.%3N'
$CLI prefetch https://example.com | tee "$RUN/meth-prefetch.result"
echo '--- tabs after method prefetch ---'
$CLI tabs | tee "$RUN/meth-tabs-after-prefetch.json"
sleep 3
date '+METH-OPEN-SUBMIT %H:%M:%S.%3N'
$CLI open https://example.com/ | tee "$RUN/meth-open.result"
METH_TAB=$(python3 -c 'import json; d=json.load(open("'$RUN'/meth-open.result")); t=d.get("tab") or {}; print(t.get("id") or d.get("tab_id") or "")')
echo "METH_TAB=$METH_TAB"
date '+METH-OBSERVE-SUBMIT %H:%M:%S.%3N'
python3 -c 'import json; json.dump({"args": ["browser", "observe", "--target", "'"$METH_TAB"'", "--image"]}, open("'$RUN'/probe-req-meth-observe.json", "w"))'
chmod 600 "$RUN/probe-req-meth-observe.json"
python3 "$RUN/timed.py" --log "$RUN/records.jsonl" req --lease-file ~/.cache/agent-computer-use/leases/pf3-probe/probe.lease --seq 3 --request "$RUN/probe-req-meth-observe.json" --label probe-meth-observe
echo '--- tabs at end ---'
$CLI tabs | tee "$RUN/tabs-end.json"
echo '=== TEARDOWN: close method tab ==='
$CLI close "$METH_TAB" | tee "$RUN/meth-close.result"
python3 "$RUN/timed.py" --log "$RUN/records.jsonl" finish --lease-file ~/.cache/agent-computer-use/leases/pf3-probe/probe.lease --label probe-finish
sleep 2
hyprctl clients -j | python3 -c 'import json,sys; ws=json.load(sys.stdin); xs=[w for w in ws if w.get("class")=="chromium"]; print(json.dumps({"chromium_windows_remaining":len(xs),"titles":[w.get("title") for w in xs]}))'
date '+END %H:%M:%S.%3N'
echo PROBE-DRIVER-DONE
