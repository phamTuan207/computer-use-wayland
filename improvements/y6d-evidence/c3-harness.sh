#!/bin/bash
# Council 3 (safety) independent harness for Y6d v3 launcher fixes.
# VM-only. No live session contact, no nest launch, no hyprglass.
# Each test prints PASS/FAIL with evidence. Run: bash /tmp/y6d-c3-harness.sh
set -u
RUNNER="$HOME/workspace/computer-use-wayland/improvements/worker-y6b-run-nested-wayland-v2.sh"
FAILURES=0
check() { # check NAME OK DETAIL
  if [ "$2" = "1" ]; then echo "PASS $1 | $3"; else echo "FAIL $1 | $3"; FAILURES=$((FAILURES+1)); fi
}
echo "=== C3 harness start $(date +%H:%M:%S) ==="

# --- A1. nest() guard inside command substitution (line 240 pattern) ---
# Verbatim nest() def from the v3 file, empty display, line-240 shape.
NESTDEF=$(grep '^nest() {' "$RUNNER")
OUT_A=$(bash -c '
set -u
fail() { echo "Y6-WAYLAND: FAIL: $1"; exit 1; }
RUN_DIR="/tmp"; SIG="sig"; NEST_DISPLAY=""
'"$NESTDEF"'
NEST_OUTPUT=$(nest hyprctl -j monitors 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d[0][\"name\"])" 2>/dev/null || echo "WAYLAND-1")
echo "outer-survived NEST_OUTPUT=$NEST_OUTPUT"
' 2>&1)
echo "A1 raw: $OUT_A"
case "$OUT_A" in *"outer-survived NEST_OUTPUT=WAYLAND-1"*) check "A1 nest() guard in \$() is masked by the WAYLAND-1 fallback (outer survives)" 1 "$OUT_A" ;;
  *) check "A1 nest() guard in \$() is masked by the WAYLAND-1 fallback (outer survives)" 0 "$OUT_A" ;; esac

# --- A2. Guard unreachability: discovery (221-237) precedes line 240 and fails closed ---
DISC_START=$(grep -n '# Discover the nested Wayland socket name' "$RUNNER" | cut -d: -f1)
LINE240=$(grep -n 'NEST_OUTPUT=$(nest' "$RUNNER" | cut -d: -f1)
ASSIGNS=$(grep -n 'NEST_DISPLAY=' "$RUNNER" | tr '\n' ';')
echo "A2 discovery starts line $DISC_START, NEST_OUTPUT line $LINE240, assignments: $ASSIGNS"
[ "$DISC_START" -lt "$LINE240" ] && check "A2 discovery block precedes the only \$(nest ...) call" 1 "disc=$DISC_START nest-output=$LINE240" || check "A2 discovery block precedes the only \$(nest ...) call" 0 "disc=$DISC_START nest-output=$LINE240"
case "$ASSIGNS" in *"NEST_DISPLAY=\"\""*"NEST_DISPLAY=\$(basename"*) check "A2 NEST_DISPLAY assigned only at init and in discovery" 1 "$ASSIGNS" ;;
  *) check "A2 NEST_DISPLAY assigned only at init and in discovery" 0 "$ASSIGNS" ;; esac

# --- B1. Stale-cleanup glob: fixture with socket, lock, regular file, dir, broken symlink ---
FIX=$(mktemp -d /tmp/y6d-c3-clean-XXXXXX)
mkdir -p "$FIX/hypr" "$FIX/wayland-dir"
python3 -c "import socket; s=socket.socket(socket.AF_UNIX); s.bind('$FIX/wayland-1'); import time; time.sleep(0.2)" &
sleep 1
echo x > "$FIX/wayland-1.lock"
echo x > "$FIX/wayland-foo"
echo x > "$FIX/wayland-dir/inner.txt"
ln -s "$FIX/nonexistent-target" "$FIX/wayland-broken"
echo keep > "$FIX/keep.txt"
# Verbatim cleanup block (lines 179-180 of v3 file), RUN_DIR=$FIX
RUN_DIR="$FIX"
rm -rf "$RUN_DIR/hypr"
for stale in "$RUN_DIR"/wayland-*; do [ -e "$stale" ] && rm -rf "$stale"; done
SURVIVORS=$(ls -A "$FIX" | tr '\n' ' ')
echo "B1 survivors after cleanup: [$SURVIVORS]"
[ -e "$FIX/wayland-1" ] && B1SOCK=0 || B1SOCK=1
[ -e "$FIX/wayland-1.lock" ] && B1LOCK=0 || B1LOCK=1
[ -e "$FIX/wayland-foo" ] && B1REG=0 || B1REG=1
[ -d "$FIX/wayland-dir" ] && B1DIR=0 || B1DIR=1
[ -d "$FIX/hypr" ] && B1HYPR=0 || B1HYPR=1
[ -L "$FIX/wayland-broken" ] && B1LINK=1 || B1LINK=0
[ -f "$FIX/keep.txt" ] && B1KEEP=1 || B1KEEP=0
check "B1 cleanup removes socket+lock+regular file+dir+hypr, keeps unrelated file" "$([ "$B1SOCK" = 1 ] && [ "$B1LOCK" = 1 ] && [ "$B1REG" = 1 ] && [ "$B1DIR" = 1 ] && [ "$B1HYPR" = 1 ] && [ "$B1KEEP" = 1 ] && echo 1 || echo 0)" "survivors=[$SURVIVORS]"
check "B1 broken symlink wayland-broken SURVIVES cleanup ([ -e ] false for dangling link)" "$B1LINK" "survivors=[$SURVIVORS]"

# --- B2. Discovery skips the surviving broken symlink, fails missing after 10s ---
DISC=$(awk '/# Discover the nested Wayland socket name/,/echo "Y6-WAYLAND: nested socket \$NEST_DISPLAY"/' "$RUNNER")
OUT_B2=$(bash -c 'fail() { echo "FAIL: $1"; exit 1; }; RUN_DIR="'"$FIX"'"; '"$DISC" 2>&1)
echo "B2 raw: $OUT_B2"
case "$OUT_B2" in *"no nested Wayland socket"*) check "B2 discovery ignores dangling symlink, fails missing (10s)" 1 "$OUT_B2" ;;
  *) check "B2 discovery ignores dangling symlink, fails missing (10s)" 0 "$OUT_B2" ;; esac

# --- B3. Cleanup with zero matches is a no-op (glob stays literal, [ -e ] false) ---
FIX3=$(mktemp -d /tmp/y6d-c3-empty-XXXXXX)
RUN_DIR="$FIX3"
rm -rf "$RUN_DIR/hypr"
for stale in "$RUN_DIR"/wayland-*; do [ -e "$stale" ] && rm -rf "$stale"; done
RC3=$?
check "B3 cleanup with no matches is a no-op, rc=0" "$([ "$RC3" = 0 ] && echo 1 || echo 0)" "rc=$RC3 dir still exists: $(test -d "$FIX3" && echo yes || echo no)"
rm -rf "$FIX" "$FIX3"

# --- B4. RUN_DIR unset under set -u aborts BEFORE any rm ---
OUT_B4=$(bash -c 'set -u; RUN_DIR_UNSET_TEST=1; unset RUN_DIR; rm -rf "$RUN_DIR/hypr"; echo REACHED-RM' 2>&1)
echo "B4 raw: $OUT_B4"
case "$OUT_B4" in *"unbound variable"*|*"REACHED-RM"*) : ;; esac
if echo "$OUT_B4" | grep -q "REACHED-RM"; then check "B4 unset RUN_DIR under set -u aborts before rm" 0 "$OUT_B4"; else check "B4 unset RUN_DIR under set -u aborts before rm" 1 "$OUT_B4"; fi

# --- C. Teardown dry harness against the v3-extracted function (VM, fake live values) ---
TD=/tmp/y6d-c3-teardown
rm -rf "$TD"; mkdir -p "$TD/run/hypr/FAKESIG"
printf 'fake-line-1\nfake-line-2\n' > "$TD/run/hypr/FAKESIG/hyprland.log"
awk '/^teardown\(\) \{/{f=1} f{print} /^}$/ && f{exit}' "$RUNNER" > "$TD/teardown.sh"
cat > "$TD/run-teardown.sh" << 'EOF'
#!/bin/bash
set -u
NEST=/tmp/y6d-c3-teardown
RUN_DIR=/tmp/y6d-c3-teardown/run
LOCK=/tmp/y6d-c3-teardown.lock
START_TS=test
SIG=FAKESIG
NEST_STARTED=1
NESTED_PID=""
PILL_PID=""
MPV_PID=""
LIVE_PID=999999
LIVE_SIG=FAKELIVESIG
export XDG_RUNTIME_DIR=/tmp WAYLAND_DISPLAY=wayland-1
live() { env XDG_RUNTIME_DIR=/tmp WAYLAND_DISPLAY=wayland-1 HYPRLAND_INSTANCE_SIGNATURE="$LIVE_SIG" "$@" 9>&-; }
exec 9>"$LOCK"
. /tmp/y6d-c3-teardown/teardown.sh
teardown
echo "C-ASSERT1: $(test -f /tmp/y6d-c3-teardown/hypr-saved-test-FAKESIG/hyprland.log && grep -c fake-line /tmp/y6d-c3-teardown/hypr-saved-test-FAKESIG/hyprland.log || echo MISSING)"
echo "C-ASSERT2: $(test ! -d /tmp/y6d-c3-teardown/run && echo RUN-DIR-REMOVED || echo RUN-DIR-STILL-THERE)"
if flock -n "$LOCK" -c true 2>/dev/null; then echo "C-ASSERT3: LOCK-FREE"; else echo "C-ASSERT3: LOCK-HELD"; fi
EOF
OUT_C=$(bash "$TD/run-teardown.sh" 2>&1)
echo "$OUT_C" | grep -E "C-ASSERT|teardown (start|done)"
case "$OUT_C" in *"C-ASSERT1: 2"*) check "C1 teardown copies nested log (2 lines) from v3-extracted function" 1 "assert1=2" ;; *) check "C1 teardown copies nested log (2 lines) from v3-extracted function" 0 "$OUT_C" ;; esac
case "$OUT_C" in *"C-ASSERT2: RUN-DIR-REMOVED"*) check "C2 teardown removes run dir" 1 "removed" ;; *) check "C2 teardown removes run dir" 0 "$OUT_C" ;; esac
case "$OUT_C" in *"C-ASSERT3: LOCK-FREE"*) check "C3 teardown releases lock" 1 "free" ;; *) check "C3 teardown releases lock" 0 "$OUT_C" ;; esac
rm -rf "$TD"

# --- D1. Pill KeyError: exact line, WAYLAND_DISPLAY unset ---
OUT_D1=$(env -u WAYLAND_DISPLAY python3 -c 'import os; env = dict(os.environ); env["WAYLAND_DISPLAY"] = os.environ["WAYLAND_DISPLAY"]' 2>&1; echo "rc=$?")
echo "D1 raw: $OUT_D1"
case "$OUT_D1" in *"KeyError: 'WAYLAND_DISPLAY'"*"rc=1"*) check "D1 pill missing WAYLAND_DISPLAY raises loud KeyError, rc=1" 1 "KeyError rc=1" ;; *) check "D1 pill missing WAYLAND_DISPLAY raises loud KeyError, rc=1" 0 "$OUT_D1" ;; esac

# --- D2. Launcher 45s pill-ready wait vs a log holding only the KeyError traceback ---
PILLLOG=$(mktemp /tmp/y6d-c3-pilllog-XXXXXX)
printf 'Traceback (most recent call last):\n  File "run-nested-pill.py", line 22, in <module>\n    env["WAYLAND_DISPLAY"] = os.environ["WAYLAND_DISPLAY"]\nKeyError: %s\n' "'WAYLAND_DISPLAY'" > "$PILLLOG"
OUT_D2=$(bash -c 'fail() { echo "Y6-WAYLAND: FAIL: $1"; exit 1; }; NEST="'"$(dirname "$PILLLOG")"'"; READY=""; for i in $(seq 1 45); do sleep 1; grep -q "Y6-NEST-PILL: ready" "'"$PILLLOG"'" 2>/dev/null && READY=1 && break; done; [ -n "$READY" ] || fail "pill did not become ready in 45s (see '"$PILLLOG"')"' 2>&1)
echo "D2 raw: $OUT_D2"
case "$OUT_D2" in *"pill did not become ready in 45s"*) check "D2 pill-ready wait fails cleanly in 45s, names the pill log" 1 "$OUT_D2" ;; *) check "D2 pill-ready wait fails cleanly in 45s, names the pill log" 0 "$OUT_D2" ;; esac
rm -f "$PILLLOG"

# --- E. Failure-order trace with backup-1 conf: gate line numbers ---
PL=$(grep -n 'hyprglass not in nested plugin list' "$RUNNER" | cut -d: -f1)
LG=$(grep -n 'liquid gate failed' "$RUNNER" | cut -d: -f1)
echo "E plugin-list fail line $PL, liquid-gate fail line $LG"
[ "$PL" -lt "$LG" ] && check "E plugin-list check precedes the 60s liquid gate" 1 "plugin-list=$PL liquid-gate=$LG" || check "E plugin-list check precedes the 60s liquid gate" 0 "plugin-list=$PL liquid-gate=$LG"

echo "=== C3 harness done $(date +%H:%M:%S): failures=$FAILURES ==="
exit "$FAILURES"
