#!/bin/bash
# daemon-one-send.sh - ONE batched laptop-side step for the speed daemon.
# Runs ON the laptop, invoked by the VM daemon over ONE mux SSH session:
#   bash /tmp/daemon-one-send.sh <endpoint> <targetId> <message>
#
# Inside this single session it does, in order:
#   1. start a laptop sleeper, acquire the overlay pill (agent speed-daemon,
#      method CDP, pid-keyed), verify visible=true + holder present.
#      FAIL CLOSED: if acquire or verification fails, NO send runs.
#   2. run node /tmp/daemon-send.mjs (pre-count guard + set_value + focus +
#      Enter + V12 poll) and capture its single JSON line.
#   3. release the pill, kill the sleeper, verify holders {} + visible false.
#   4. print EXACTLY ONE JSON line on stdout (the merged result).
# The pill is never left stuck: release runs even when the send fails, and
# the holder is pid-keyed by the sleeper, so the overlay daemon prunes it
# when the sleeper expires (600s) if this script dies mid-send.
set -u
ENDPOINT="$1"
TARGET="$2"
MSG="$3"
OVERLAY=/home/james/computer-use-wayland/scripts/overlay.py
SEND=/tmp/daemon-send.mjs

jstr() { python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$1"; }

# Laptop-side file check first (cheap, local): the /tmp helpers disappear
# between runs, so a missing send script must fail loudly, not silently.
if [ ! -f "$SEND" ]; then
  echo "{\"ok\": false, \"outcome\": \"error\", \"error\": \"daemon-send.mjs missing on laptop\", \"stage\": \"preflight\"}"
  exit 0
fi

nohup sleep 600 >/dev/null 2>&1 < /dev/null & SLEEP_PID=$!
ACQ_OUT=$(python3 "$OVERLAY" acquire --agent speed-daemon --method CDP --pid "$SLEEP_PID" 2>/dev/null)
ACQ_RC=$?
if [ "$ACQ_RC" -ne 0 ]; then
  kill "$SLEEP_PID" 2>/dev/null
  echo "{\"ok\": false, \"outcome\": \"error\", \"error\": $(jstr "pill acquire failed rc=$ACQ_RC: ${ACQ_OUT:0:200}"), \"stage\": \"pill-acquire\"}"
  exit 0
fi
ACQ_VISIBLE=$(echo "$ACQ_OUT" | python3 -c 'import json,sys; print("1" if json.load(sys.stdin).get("visible") is True else "0")' 2>/dev/null)
STATUS1=$(python3 "$OVERLAY" status 2>/dev/null)
HOLD_OK=$(echo "$STATUS1" | python3 -c 'import json,sys; d=json.load(sys.stdin); print("1" if d.get("visible") and ("speed-daemon:%d" % '"$SLEEP_PID"') in (d.get("holders") or {}) else "0")' 2>/dev/null)
if [ "$ACQ_VISIBLE" != "1" ] || [ "$HOLD_OK" != "1" ]; then
  python3 "$OVERLAY" release --agent speed-daemon --method CDP --pid "$SLEEP_PID" >/dev/null 2>&1
  kill "$SLEEP_PID" 2>/dev/null
  echo "{\"ok\": false, \"outcome\": \"aborted-pill-lost\", \"error\": $(jstr "pill not verified after acquire: $STATUS1"), \"stage\": \"pill-verify\"}"
  exit 0
fi

SEND_OUT=$(node "$SEND" "$ENDPOINT" "$TARGET" "$MSG" 10000 2>&1)

python3 "$OVERLAY" release --agent speed-daemon --method CDP --pid "$SLEEP_PID" >/dev/null 2>&1
kill "$SLEEP_PID" 2>/dev/null
STATUS2=$(python3 "$OVERLAY" status 2>/dev/null)
REL_OK=$(echo "$STATUS2" | python3 -c 'import json,sys; d=json.load(sys.stdin); print("1" if d.get("holders")=={} and d.get("visible") is False else "0")' 2>/dev/null)

# Merge: send JSON + pill facts. If node printed no JSON, report it raw.
python3 - "$SEND_OUT" "$REL_OK" "$SLEEP_PID" <<'PYEOF'
import json, sys
raw, rel_ok, pid = sys.argv[1], sys.argv[2] == "1", int(sys.argv[3])
try:
    send = json.loads(raw.strip().splitlines()[-1])
except Exception:
    send = {"ok": False, "outcome": "error", "error": "daemon-send.mjs bad output: " + raw.strip()[:300]}
send["pill"] = {"acquired": True, "verified": True, "sleep_pid": pid,
                "released": True, "release_verified": rel_ok}
print(json.dumps(send))
PYEOF
exit 0
