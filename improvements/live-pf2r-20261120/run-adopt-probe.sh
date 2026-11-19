#!/bin/bash
# Scripted adoption probe (coordinator-run, zero model calls).
# Branch harness-prefetch ac3882b, CU_PRECAPTURE=0.
# Question: why did open NOT adopt the prefetched tab in the method arm
# (prefetch ok:true tab 6691BF08..., open prefetched:false fresh tab 86350AA5...)?
# Code hypothesis (scripts/chromium_cli.py _prefetched_target): the record URL is
# the raw string "https://example.com" (validate_url returns it unchanged) but
# Chromium reports the loaded tab URL and location.href as "https://example.com/"
# (trailing slash). The string comparison fails deterministically before the
# readyState check is ever reached.
# Test A replicates the method arm (no slash, 3s sleep).
# Test B uses the trailing-slash URL for both prefetch and open: if it adopts,
# the slash mismatch is proven as the root cause.
# Test C is the control for the readyState hypothesis (no slash, 12s sleep):
# if it still does not adopt, the wait time is not the cause.
source /home/james/backups/cu-final-0.57.2-20261114-225131/env.sh
refresh_gui >/dev/null 2>&1 || true
live_dir=$(find /run/user/1000/hypr -mindepth 1 -maxdepth 1 -type d -exec test -f '{}/hyprland.lock' \; -print | head -1)
export HYPRLAND_INSTANCE_SIGNATURE="$(basename "$live_dir")"
RUN=/tmp/live-pf2r-20261120/pf2r-adopt-probe
LOG=$RUN/probe-driver.log
mkdir -p "$RUN" ~/.cache/agent-computer-use/leases/pf2r-probe-adopt
chmod 700 ~/.cache/agent-computer-use/leases/pf2r-probe-adopt
exec > "$LOG" 2>&1
CLI="python3 /home/james/computer-use-wayland/scripts/chromium_cli.py"
date '+START %H:%M:%S.%3N'
python3 "$RUN/timed.py" --log "$RUN/records.jsonl" start --owner pf2r-probe-adopt --lease-file ~/.cache/agent-computer-use/leases/pf2r-probe-adopt/probe.lease --label probe-start
ls -l ~/.cache/agent-computer-use/session.json
python3 -c 'import json; json.dump({"args": ["browser", "start"]}, open("'$RUN'/probe-req-browser-start.json", "w"))'
chmod 600 "$RUN/probe-req-browser-start.json"
python3 "$RUN/timed.py" --log "$RUN/records.jsonl" req --lease-file ~/.cache/agent-computer-use/leases/pf2r-probe-adopt/probe.lease --seq 1 --request "$RUN/probe-req-browser-start.json" --label probe-browser-start
echo '=== TEST A: prefetch https://example.com, sleep 3, open https://example.com ==='
date '+A-PREFETCH-SUBMIT %H:%M:%S.%3N'
$CLI prefetch https://example.com | tee "$RUN/a-prefetch.result"
echo '--- tabs after A prefetch ---'
$CLI tabs | tee "$RUN/a-tabs-after-prefetch.json"
sleep 3
date '+A-OPEN-SUBMIT %H:%M:%S.%3N'
$CLI open https://example.com | tee "$RUN/a-open.result"
echo '=== TEST B: prefetch https://example.com/, sleep 3, open https://example.com/ ==='
date '+B-PREFETCH-SUBMIT %H:%M:%S.%3N'
$CLI prefetch https://example.com/ | tee "$RUN/b-prefetch.result"
echo '--- tabs after B prefetch ---'
$CLI tabs | tee "$RUN/b-tabs-after-prefetch.json"
sleep 3
date '+B-OPEN-SUBMIT %H:%M:%S.%3N'
$CLI open https://example.com/ | tee "$RUN/b-open.result"
echo '=== TEST C: prefetch https://example.com, sleep 12, open https://example.com ==='
date '+C-PREFETCH-SUBMIT %H:%M:%S.%3N'
$CLI prefetch https://example.com | tee "$RUN/c-prefetch.result"
sleep 12
date '+C-OPEN-SUBMIT %H:%M:%S.%3N'
$CLI open https://example.com | tee "$RUN/c-open.result"
echo '--- tabs at end ---'
$CLI tabs | tee "$RUN/tabs-end.json"
echo '=== TEARDOWN: close every tab id opened or prefetched ==='
python3 - "$RUN" <<'PYEOF'
import json, glob, subprocess, sys
ids = set()
for f in glob.glob(sys.argv[1] + "/*.result") + [sys.argv[1] + "/tabs-end.json"]:
    try:
        d = json.load(open(f))
    except Exception:
        continue
    if isinstance(d, dict):
        t = d.get("tab") or {}
        if isinstance(t, dict) and t.get("id"):
            ids.add(t["id"])
        if d.get("tab_id"):
            ids.add(d["tab_id"])
        for tab in d.get("tabs", []) or []:
            if isinstance(tab, dict) and tab.get("id"):
                ids.add(tab["id"])
for tid in sorted(ids):
    r = subprocess.run(["python3", "/home/james/computer-use-wayland/scripts/chromium_cli.py", "close", tid],
                       capture_output=True, text=True)
    print("close", tid[:8], r.returncode, (r.stdout or r.stderr).strip()[:200])
PYEOF
python3 "$RUN/timed.py" --log "$RUN/records.jsonl" finish --lease-file ~/.cache/agent-computer-use/leases/pf2r-probe-adopt/probe.lease --label probe-finish
sleep 2
hyprctl clients -j | python3 -c 'import json,sys; ws=json.load(sys.stdin); xs=[w for w in ws if w.get("class")=="chromium"]; print(json.dumps({"chromium_windows_remaining":len(xs),"titles":[w.get("title") for w in xs]}))'
date '+END %H:%M:%S.%3N'
echo PROBE-DRIVER-DONE
