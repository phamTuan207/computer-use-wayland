#!/bin/bash
# Y6d redteam proofs. Extracts blocks VERBATIM from the v3 runner and runs
# them against controlled fixtures. No nest launched, no Zen, no live session.
# All output is timed. Run: bash /tmp/y6d-redteam/proofs.sh
RUNNER="$HOME/workspace/computer-use-wayland/improvements/worker-y6b-run-nested-wayland-v2.sh"
T0=$(date +%s)
ts() { echo "[T+$(( $(date +%s) - T0 ))s] $*"; }
fail() { echo "Y6-WAYLAND: FAIL: $1"; exit 1; }

ts "=== P1 (H1): discovery picks a DEAD socket (bound, then process gone) ==="
D1=$(mktemp -d /tmp/y6d-rt-dead-XXXXXX)
python3 - "$D1" <<'PYEOF'
import socket, os, sys
d = sys.argv[1]
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.bind(os.path.join(d, "wayland-1"))
s.close()  # dead socket file remains, nothing listening
open(os.path.join(d, "wayland-1.lock"), "w").write("x")
c = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
try:
    c.connect(os.path.join(d, "wayland-1"))
    print("P1-CONNECT: OK (unexpected)")
except Exception as e:
    print("P1-CONNECT: refused as expected:", e)
PYEOF
awk '/^# Discover the nested Wayland socket name/,/nested socket \$NEST_DISPLAY"/' "$RUNNER" > /tmp/y6d-redteam/p1-disc.sh
RUN_DIR="$D1" bash -c 'fail() { echo "FAIL: $1"; exit 1; }; RUN_DIR="'"$D1"'"; '"$(cat /tmp/y6d-redteam/p1-disc.sh)"'; echo "P1-RESULT rc=$? NEST_DISPLAY=$NEST_DISPLAY"'
echo "P1-OUTER-RC=$?"
ls -la "$D1"

ts "=== P2 (H1): foreign socket in RUN_DIR -> ambiguous false-fail ==="
D2=$(mktemp -d /tmp/y6d-rt-foreign-XXXXXX)
python3 - "$D2" <<'PYEOF' &
import socket, os, sys, time
d = sys.argv[1]
a = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); a.bind(os.path.join(d, "wayland-1"))
b = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); b.bind(os.path.join(d, "wayland-9"))
time.sleep(20)  # hold both sockets while the discovery block runs
PYEOF
HOLDPID=$!
sleep 1
RUN_DIR="$D2" bash -c 'fail() { echo "FAIL: $1"; exit 1; }; RUN_DIR="'"$D2"'"; '"$(cat /tmp/y6d-redteam/p1-disc.sh)"'; echo "P2-RESULT rc=$? NEST_DISPLAY=$NEST_DISPLAY"'
echo "P2-OUTER-RC=$? (fail() exits the inner shell, so the RESULT line above never prints; the outer rc is the proof)"
kill $HOLDPID 2>/dev/null

ts "=== P2b (H1): cleanup block removes stale socket/lock/file; dangling symlink survives ==="
D2b=$(mktemp -d /tmp/y6d-rt-clean-XXXXXX)
python3 - "$D2b" <<'PYEOF'
import socket, os, sys
d = sys.argv[1]
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); s.bind(os.path.join(d, "wayland-1")); s.close()
open(os.path.join(d, "wayland-1.lock"), "w").write("x")
open(os.path.join(d, "wayland-old"), "w").write("x")
PYEOF
RUN_DIR="$D2b" bash -c 'RUN_DIR="'"$D2b"'"; rm -rf "$RUN_DIR/hypr"; for stale in "$RUN_DIR"/wayland-*; do [ -e "$stale" ] && rm -rf "$stale"; done; echo "P2b-AFTER-CLEANUP:"; ls -A "$RUN_DIR" | sed "s/^/  /"; echo "(empty above = all stale entries removed)"'
ln -s /nonexistent-target "$D2b/wayland-1"
RUN_DIR="$D2b" bash -c 'RUN_DIR="'"$D2b"'"; for stale in "$RUN_DIR"/wayland-*; do [ -e "$stale" ] && rm -rf "$stale"; done; echo "P2b-SYMLINK-AFTER-CLEANUP:"; ls -A "$RUN_DIR" | sed "s/^/  /"; [ -L "$RUN_DIR/wayland-1" ] && echo "P2b: dangling symlink SURVIVED cleanup ([ -e ] is false for dangling links)"; [ -S "$RUN_DIR/wayland-1" ] || echo "P2b: ...but discovery skips it too ([ -S ] false), so it cannot be picked"'

ts "=== P3 (H2/H3): backend gate is single-shot, discovery retries ==="
D3=$(mktemp -d /tmp/y6d-rt-gate-XXXXXX)
GATELOG="$D3/hyprland.log"; touch "$GATELOG"
( sleep 6; echo "DEBUG from aquamarine ]: Starting the Wayland backend!" >> "$GATELOG" ) &
S3=$(date +%s)
NEST_LOG="$GATELOG" bash -c 'fail() { echo "FAIL: $1"; exit 1; }; NEST_LOG="'"$GATELOG"'"; sleep 5; [ -f "$NEST_LOG" ] || fail "nested per-instance log $NEST_LOG missing"; grep -a "Wayland backend" "$NEST_LOG" | head -3; grep -a -q "Wayland backend" "$NEST_LOG" || fail "Wayland backend did not start in nested log $NEST_LOG"; echo "P3-GATE: passed"'
echo "P3-GATE-RC=$? (rc=1 proves the single-shot gate fails although the line arrives 1s later at t=6s)"
echo "P3-GATE-ELAPSED: $(( $(date +%s) - S3 ))s (sleep 5 included, as in the runner; line arrived at t=6s, 1s too late)"
wait 2>/dev/null
grep -c "Wayland backend" "$GATELOG"
D3b=$(mktemp -d /tmp/y6d-rt-disc-late-XXXXXX)
( sleep 6; python3 -c "import socket,os,sys,time; s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); s.bind(os.path.join(sys.argv[1],'wayland-1')); time.sleep(15)" "$D3b" ) &
S3b=$(date +%s)
RUN_DIR="$D3b" bash -c 'fail() { echo "FAIL: $1"; exit 1; }; RUN_DIR="'"$D3b"'"; '"$(cat /tmp/y6d-redteam/p1-disc.sh)"'; echo "P3-DISC-LATE rc=$? NEST_DISPLAY=$NEST_DISPLAY"'
echo "P3-DISC-LATE-RC=$?"
echo "P3-DISC-LATE-ELAPSED: $(( $(date +%s) - S3b ))s (socket appeared at t=6s, inside the 10s loop)"
wait 2>/dev/null

ts "=== P5 (H7): nest() guard inside command substitution is masked ==="
S5=$(date +%s)
grep '^nest() {' "$RUNNER" > /tmp/y6d-redteam/nest-def.sh
awk '/^read_pill_geom\(\) \{/{f=1} f{print} /^}$/ && f{exit}' "$RUNNER" > /tmp/y6d-redteam/read-pill-geom.sh
cat > /tmp/y6d-redteam/p5.sh <<'P5EOF'
fail() { echo "Y6-WAYLAND: FAIL: $1"; exit 1; }
RUN_DIR="/tmp"; SIG="sig"; NEST_DISPLAY=""; NEST="/tmp"
. /tmp/y6d-redteam/nest-def.sh
NEST_OUTPUT=$(nest hyprctl -j monitors 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d[0]['name'])" 2>/dev/null || echo "WAYLAND-1")
echo "P5-NEST_OUTPUT rc=$? NEST_OUTPUT=$NEST_OUTPUT"
echo "P5: SCRIPT CONTINUED past the guard (no exit, no FAIL visible to operator)"
P5EOF
bash /tmp/y6d-redteam/p5.sh
echo "P5-ELAPSED: $(( $(date +%s) - S5 ))s"
cat > /tmp/y6d-redteam/p5b.sh <<'P5EOF'
fail() { echo "Y6-WAYLAND: FAIL: $1"; exit 1; }
RUN_DIR="/tmp"; SIG="sig"; NEST_DISPLAY=""; NEST="/tmp"
. /tmp/y6d-redteam/nest-def.sh
. /tmp/y6d-redteam/read-pill-geom.sh
PILL_GEOM=$(read_pill_geom) || echo "P5b-OUTER-FAIL: pill surface not found in nested layers (pill not visible)"
echo "P5b: outer message above replaced the guard message; the guard text never reached the operator"
P5EOF
bash /tmp/y6d-redteam/p5b.sh

ts "=== P6 (H5): plugin-list gate fails fast, but with no ABI diagnosis ==="
echo '[]' > /tmp/y6d-redteam/nest-plugin-list.json
bash -c 'fail() { echo "FAIL: $1"; exit 1; }; grep -q hyprglass /tmp/y6d-redteam/nest-plugin-list.json || fail "hyprglass not in nested plugin list"'
echo "P6-RC=$? (fail-fast at the plugin-list gate, no ldd/load-error evidence collected)"
echo "P6: conf plugin line:"; grep -n "plugin.load" "$HOME/workspace/computer-use-wayland/improvements/worker-y6b-hyprland-wayland-v2.lua"
echo "P6: runner ldd/backup guard lines (expect none):"; grep -n "ldd\|backup" "$RUNNER" | grep -v "^.*#" | head; grep -c "ldd" "$RUNNER" || true

ts "=== P7 (H8): C2 coverage gaps ==="
echo "P7: C2-vm mentions of stale/cleanup (expect none):"
grep -n -i "stale\|cleanup" /tmp/y6d-c2-vm.py || echo "  (none found)"
echo "P7: C2-vm mentions of mpv/pill env propagation (expect none):"
grep -n "mpv\|PILL" /tmp/y6d-c2-vm.py | grep -v "^\s*#" || echo "  (none found)"
echo "P7: C2-vm mentions of a socket appearing mid-loop or a dead socket (expect none):"
grep -n -i "mid-loop\|dead socket\|appear" /tmp/y6d-c2-vm.py || echo "  (none found)"
echo "P7: C2-laptop mentions of NEST_DISPLAY/pill-env/mpv-env:"
grep -n "NEST_DISPLAY" /tmp/y6d-c2-laptop.sh || echo "  (none found)"
echo "P7: GRIM-A in c2-laptop.log (expected file, got no file, no FAIL recorded):"
grep -n -A1 "grim space form" "$HOME/workspace/computer-use-wayland/improvements/y6d-evidence/c2-laptop.log"
grep -n "GRIM-A OK" "$HOME/workspace/computer-use-wayland/improvements/y6d-evidence/c2-laptop.log" || echo "  (no GRIM-A OK line anywhere in the log)"
echo "P7: c2-laptop.sh GRIM-A has no assertion (only && echo OK):"
grep -n "y6d-grim-a.png" /tmp/y6d-c2-laptop.sh

ts "=== P4 (H6): pill dies at t=2s, wait loop burns the full 45s (runs last, ~46s) ==="
D4=$(mktemp -d /tmp/y6d-rt-pill-XXXXXX)
NEST="$D4"
python3 -c "import time,sys; time.sleep(2); print('Traceback (most recent call last):', file=sys.stderr); print('  File \"run-nested-pill.py\", line 22, in <module>', file=sys.stderr); print('KeyError: '"'"'WAYLAND_DISPLAY'"'"'', file=sys.stderr); sys.exit(1)" > "$NEST/nest-pill.log" 2>&1 &
PILL_PID=$!
cat > /tmp/y6d-redteam/p4.sh <<'P4EOF'
fail() { echo "Y6-WAYLAND: FAIL: $1"; exit 1; }
sleep 1
kill -0 "$PILL_PID" 2>/dev/null || fail "pill process died immediately (see $NEST/nest-pill.log)"
READY=""
for i in $(seq 1 45); do sleep 1; grep -q "Y6-NEST-PILL: ready" "$NEST/nest-pill.log" 2>/dev/null && READY=1 && break; done
[ -n "$READY" ] || fail "pill did not become ready in 45s (see $NEST/nest-pill.log)"
echo "P4: pill became ready (unexpected)"
P4EOF
S4=$(date +%s)
NEST="$NEST" PILL_PID="$PILL_PID" bash /tmp/y6d-redteam/p4.sh
echo "P4-RC=$? ELAPSED=$(( $(date +%s) - S4 ))s (pill died at t=2s; the log below holds the real cause the message hides)"
cat "$NEST/nest-pill.log"
wait 2>/dev/null
ts "=== ALL PROOFS DONE ==="
