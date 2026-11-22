#!/bin/bash
# Y6e nested LOAD test ONLY (todolist 2.2.3 I11): prove the rebuilt hyprglass
# loads in a nested Hyprland. NOT the pill measurement run (that is a separate
# worker after a fresh re-review). Reuses the v3 runner's verified blocks
# (launch, discovery, backend gate, plugin checks, teardown) and stops after
# the plugin status check. No mpv, no grim, no pill, no arms, no liquid gate.
#
# Preconditions enforced below: handover re-confirmed (Y6_HANDOVER_CONFIRMED=1),
# runner-quiet (process check + flock), live socket present, new conf present,
# ldd pre-flight passes on the rebuilt .so, HYPRGLASS_SKIP_VERSION_CHECK unset
# (redteam AMEND 4), live config contains no hyprglass path + live plugin list
# recorded BEFORE (redteam AMEND 5 / Council 3 check 2).
#
# Exit codes: 0 = LOADED (plugin listed + version 1.1.1-cu.1 + versionCheck match).
# 1 = NO-GO / abort (see log). Teardown always runs (trap on EXIT/TERM/INT/HUP).
set -u
NEST=/tmp/y6-nested
RUN_DIR=$NEST/run
CONF=$NEST/conf/hyprland-wayland-y6e.lua
LOG=$NEST/hyprland-wayland.log
LOCK=$HOME/.cache/agent-computer-use/zen_dom.lock
LIVE_SOCK=/run/user/1000/wayland-1
START_TS=$(date +%Y%m%d-%H%M%S)
START_MONO=$(date +%s)
RUN_LOG=$NEST/y6e-load-$START_TS.log
NESTED_PID=""
NEST_HYPRLAND_PID=""
SIG=""
LIVE_SIG=""
LIVE_PID=""
NEST_STARTED=0
NEST_OUTPUT="WAYLAND-1"
NEST_DISPLAY=""

# Tee stdout to the run log. The tee process is created before the flock
# fd exists, so it cannot inherit the lock.
exec > >(tee -a "$RUN_LOG") 2>&1

fail() { echo "Y6E-LOAD: FAIL: $1"; exit 1; }

# Nested-env helper: every nested hyprctl call goes through nest().
# The trailing 9>&- keeps the flock fd out of every child.
# NEST_DISPLAY is the socket name discovered after launch; calling nest()
# before discovery is a fail-closed error, never a silent empty display.
nest() { [ -n "$NEST_DISPLAY" ] || fail "nest() called before socket discovery"; env XDG_RUNTIME_DIR="$RUN_DIR" WAYLAND_DISPLAY="$NEST_DISPLAY" HYPRLAND_INSTANCE_SIGNATURE="$SIG" "$@" 9>&-; }
live() { env XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-1 HYPRLAND_INSTANCE_SIGNATURE="$LIVE_SIG" "$@" 9>&-; }

teardown() {
  echo "Y6E-LOAD: teardown start $(date +%H:%M:%S)"
  # Copy the nested per-instance log out before removing the runtime dir.
  if [ "$NEST_STARTED" = "1" ] && [ -n "$SIG" ] && [ -d "$RUN_DIR/hypr/$SIG" ]; then
    cp -r "$RUN_DIR/hypr/$SIG" "$NEST/hypr-saved-y6e-$START_TS-$SIG" 2>/dev/null && echo "Y6E-LOAD: nested log saved to $NEST/hypr-saved-y6e-$START_TS-$SIG" || echo "Y6E-LOAD: WARN: nested log copy failed"
  fi
  if [ "$NEST_STARTED" = "1" ] && [ -n "$NESTED_PID" ]; then
    # Kill the whole nested session process group. setsid made NESTED_PID
    # the session leader, so the group is -$NESTED_PID.
    kill -- -$NESTED_PID 2>/dev/null; sleep 2; kill -9 -- -$NESTED_PID 2>/dev/null
  fi
  # Remove the runtime dir only if the nest was actually started.
  if [ "$NEST_STARTED" = "1" ]; then rm -rf "$RUN_DIR"; fi
  echo "Y6E-LOAD: live check:"
  if [ -n "$LIVE_PID" ]; then ps -o pid,lstart,cmd -p "$LIVE_PID" || echo "Y6E-LOAD: LIVE PID $LIVE_PID MISSING"; else echo "Y6E-LOAD: LIVE PID never resolved"; fi
  if [ -n "$LIVE_SIG" ]; then
    if live hyprctl version > /tmp/y6e-live-version.txt 2>&1; then head -4 /tmp/y6e-live-version.txt; else echo "Y6E-LOAD: live hyprctl FAILED"; fi
    live hyprctl -j plugin list > "$NEST/y6e-live-plugin-list-after.json" 2>&1 && grep -o '"name": "[^"]*"' "$NEST/y6e-live-plugin-list-after.json" || echo "Y6E-LOAD: live plugin list FAILED"
  else
    echo "Y6E-LOAD: live signature never resolved"
  fi
  # Stray process check. The live Hyprland (LIVE_PID) is expected.
  echo "Y6E-LOAD: stray check (live Hyprland pid $LIVE_PID expected):"
  pgrep -a -x Hyprland || true
  pgrep -a -x mpv || true
  pgrep -a -x foot || true
  # Lock free check. Close our own fd 9 first, or the test measures our own hold.
  exec 9>&- 2>/dev/null || true
  if flock -n "$LOCK" -c true 2>/dev/null; then echo "Y6E-LOAD: lock free after teardown"; else echo "Y6E-LOAD: WARN: lock still held after teardown"; fi
  echo "Y6E-LOAD: teardown done $(date +%H:%M:%S)"
}
trap teardown EXIT
trap 'exit 143' TERM
trap 'exit 130' INT
trap 'exit 129' HUP

echo "Y6E-LOAD: start $(date +%H:%M:%S)"
[ "${Y6_HANDOVER_CONFIRMED:-0}" = "1" ] || fail "handover not re-confirmed at run time; confirm with Muse, then rerun with Y6_HANDOVER_CONFIRMED=1"
test -S "$LIVE_SOCK" || fail "live socket $LIVE_SOCK missing"
test -f "$CONF" || fail "missing conf $CONF"
command -v Hyprland >/dev/null || fail "Hyprland not found"
command -v ldd >/dev/null || fail "ldd not found"

# Redteam AMEND 4: the skip var must be unset in the ambient env at launch.
if env | grep -q "^HYPRGLASS_SKIP_VERSION_CHECK="; then fail "HYPRGLASS_SKIP_VERSION_CHECK is set in the ambient env; refusing to run (the version gate would be bypassed)"; fi
echo "Y6E-LOAD: AMEND4 OK: HYPRGLASS_SKIP_VERSION_CHECK unset (env | grep HYPRGLASS empty)"
unset HYPRGLASS_SKIP_VERSION_CHECK

# Redteam AMEND 5 (before half): the LIVE config chain must contain no
# hyprglass LOAD PATH, so the live session can never load the rebuilt plugin.
# The load vector is a plugin.load call or a .so filesystem path naming
# hyprglass. Guarded API refs are INERT when the plugin is not loaded and
# do NOT fail the check: visuals-login.lua only dofiles the optics file when
# exactly one hyprglass 1.1.1-cu.1 is already loaded, and the optics file is
# itself guarded by `if hl.plugin.hyprglass then`. The live plugin list
# (hyprbars only, checked before and after) is the backstop for anything
# this walker misses, including the Omarchy bootstrap file, which is a
# distro default and is not followed here.
# False-positive history, both fail-closed aborts, both recorded:
# - 21:52: whole-directory grep hit agent_computer_use_glass.lua
#   .before-final-20261011 (a 2026-10-11 snapshot, referenced nowhere).
# - 21:54: any-"hyprglass"-string check hit the guarded API refs in
#   visuals-login.lua (plugin.name check, dofile of the optics file) and
#   hyprglass-local-optics.lua (config/layer calls). A grep for plugin.load
#   over the same chain returns EMPTY: the live session never loads
#   hyprglass from config. Noted interaction: visuals-login.lua:10 gates
#   the optics profile on glass_version == "1.1.1-cu.1", so it WOULD apply
#   the profile if hyprglass 1.1.1-cu.1 were ever loaded live, which is
#   exactly why the no-load-path check below matters.
LIVE_HG=$(python3 - "$HOME/.config/hypr" << 'PYEOF'
import os, re, sys
root = sys.argv[1]
main = [os.path.join(root, "hyprland.lua"), os.path.join(root, "hyprland.conf")]
seen, queue = set(), [p for p in main if os.path.isfile(p)]
hits = []
while queue:
    p = queue.pop(0)
    if p in seen:
        continue
    seen.add(p)
    try:
        txt = open(p, errors="replace").read()
    except OSError:
        continue
    for i, line in enumerate(txt.splitlines(), 1):
        if re.search(r'plugin\.load\s*\(.*hyprglass', line) or re.search(r'hyprglass[^"\']*\.so', line):
            hits.append("%s:%d:%s" % (p, i, line.strip()))
    for m in re.finditer(r'(?:source|dofile)\s*\(?\s*["\']([^"\']+)["\']', txt):
        s = m.group(1)
        if not os.path.isabs(s):
            s = os.path.join(root, s)
        if os.path.isfile(s):
            queue.append(s)
print("\n".join(hits))
PYEOF
)
if [ -n "$LIVE_HG" ]; then echo "$LIVE_HG"; fail "live config contains a hyprglass load path; refusing to run"; fi
echo "Y6E-LOAD: AMEND5-BEFORE OK: no hyprglass load path in live config chain (hyprland.lua + hyprland.conf + sourced files)"

# ldd pre-flight (v3 block, verbatim shape): the conf's plugin .so must load.
GLASS_SO=$(grep -o '/[^"]*hyprglass[^"]*\.so' "$CONF" | head -1)
[ -n "$GLASS_SO" ] || fail "no hyprglass.so path in conf $CONF"
[ -f "$GLASS_SO" ] || fail "hyprglass path in conf missing on disk: $GLASS_SO"
LDD_OUT=$(ldd "$GLASS_SO" 2>&1) || fail "ldd failed on $GLASS_SO: $LDD_OUT"
MISSING_LIBS=$(printf '%s\n' "$LDD_OUT" | grep "not found" || true)
[ -z "$MISSING_LIBS" ] || fail "hyprglass $GLASS_SO cannot load (dead ABI): $MISSING_LIBS"
echo "Y6E-LOAD: plugin ABI OK: $GLASS_SO"

# Resolve live identity at runtime.
LIVE_SIG=$(ls -t /run/user/1000/hypr/ 2>/dev/null | head -1)
[ -n "$LIVE_SIG" ] || fail "no live Hyprland signature found"
[ "$(ls /run/user/1000/hypr/ | wc -l)" = "1" ] || fail "ambiguous live signatures, refusing to guess"
LIVE_PID=$(pgrep -x Hyprland)
[ -n "$LIVE_PID" ] || fail "no live Hyprland process found"
[ "$(echo "$LIVE_PID" | wc -l)" = "1" ] || fail "ambiguous live Hyprland PIDs, refusing to guess"
echo "Y6E-LOAD: live sig $LIVE_SIG pid $LIVE_PID"

# Live plugin list BEFORE (AMEND 5 / Council 3 check 2): recorded, compared after.
live hyprctl -j plugin list > "$NEST/y6e-live-plugin-list-before.json" 2>&1 || fail "live hyprctl plugin list (before) failed"
echo "Y6E-LOAD: live plugin list BEFORE:"
grep -o '"name": "[^"]*"' "$NEST/y6e-live-plugin-list-before.json" || echo "Y6E-LOAD: (no plugins listed)"

# Runner-quiet process check (v3, verbatim patterns).
if pgrep -af "run_agyq2[.]py|run_live[.]py|run_agyq[.]py|run_agy_y2[.]py|run_fcck[.]py" 2>/dev/null | grep -v "pgrep -af"; then
  fail "live runner process found; abort, do not run"
fi
if pgrep -x geckodriver >/dev/null; then
  fail "geckodriver running; a live runner is active, abort"
fi
if pgrep -x mpv >/dev/null || pgrep -x foot >/dev/null; then
  fail "mpv or foot already running; abort, do not run"
fi
echo "Y6E-LOAD: runner-quiet process check OK"

# Hold the runner lock for the whole run.
exec 9>"$LOCK" || fail "cannot open lock $LOCK"
flock -n 9 || fail "zen_dom.lock held by a runner; abort, do not run"
echo "Y6E-LOAD: flock held, runner-quiet window open"

# Clear stale nest runtime state: the socket name is discovered at launch,
# so remove any wayland-* socket/lock left by a previous run.
rm -rf "$RUN_DIR/hypr"
for stale in "$RUN_DIR"/wayland-*; do if [ -e "$stale" ] || [ -L "$stale" ]; then rm -rf "$stale"; fi; done
mkdir -p "$RUN_DIR"

# Parent connection: absolute live socket path. No --socket flag: in 0.57.2
# passing --socket without --wayland-fd is a hard startup error, so the nest
# auto-names its socket and the launcher discovers it below (F0, v3).
export XDG_RUNTIME_DIR="$RUN_DIR"
export WAYLAND_DISPLAY="$LIVE_SOCK"
unset HYPRLAND_INSTANCE_SIGNATURE
unset HYPRGLASS_SKIP_VERSION_CHECK
rm -f "$NEST/nest-timeout.pid"
setsid bash -c "echo \$\$ > \"$NEST/nest-timeout.pid\"; exec timeout 600 Hyprland --config \"$CONF\"" > "$LOG" 2>&1 < /dev/null 9>&- &
for i in $(seq 1 10); do sleep 1; [ -s "$NEST/nest-timeout.pid" ] && break; done
NESTED_PID=$(cat "$NEST/nest-timeout.pid" 2>/dev/null || echo "")
[ -n "$NESTED_PID" ] || fail "nested launcher did not write its pidfile"
NEST_STARTED=1
echo "Y6E-LOAD: nested pid $NESTED_PID (timeout wrapper, session leader)"

for i in $(seq 1 15); do sleep 1; SIG=$(ls -t "$RUN_DIR/hypr/" 2>/dev/null | head -1); [ -n "$SIG" ] && break; done
[ -n "$SIG" ] || fail "no nested instance signature after 15s"
echo "Y6E-LOAD: nested sig $SIG"
# Per-instance log path (U5b, v3): the backend line lands only here.
NEST_LOG="$RUN_DIR/hypr/$SIG/hyprland.log"

# Record the real nested Hyprland PID (child of the timeout wrapper).
NEST_HYPRLAND_PID=$(pgrep -P "$NESTED_PID" -x Hyprland | head -1)
echo "Y6E-LOAD: nested Hyprland pid ${NEST_HYPRLAND_PID:-unknown}"

# Post-launch: the nested log must show the Wayland backend started.
# Retry the gate for up to 10s (redteam A1): the backend line can lag the
# signature on a loaded machine. Exact line: no failure line contains it.
sleep 5
[ -f "$NEST_LOG" ] || fail "nested per-instance log $NEST_LOG missing"
BACKEND_OK=""
for i in $(seq 1 10); do
  if grep -a -q "Starting the Wayland backend!" "$NEST_LOG" 2>/dev/null; then BACKEND_OK=1; break; fi
  sleep 1
done
if [ -n "$BACKEND_OK" ]; then grep -a "Starting the Wayland backend!" "$NEST_LOG" | head -3;
else tail -20 "$LOG"; fail "Wayland backend did not start in nested log $NEST_LOG (stdout tail above)"; fi
# The nest must still be alive after the gate (redteam B3).
[ -n "$NEST_HYPRLAND_PID" ] && kill -0 "$NEST_HYPRLAND_PID" 2>/dev/null || fail "nested Hyprland died after backend start (pid ${NEST_HYPRLAND_PID:-unknown})"

# Discover the nested Wayland socket name (F0, v3): without --socket the nest
# auto-names its socket. Exactly one non-lock wayland-* socket must exist.
# The scan re-runs for up to 10s because the socket may lag the signature.
for i in $(seq 1 10); do
  NEST_DISPLAY=""
  for s in "$RUN_DIR"/wayland-*; do
    case "$s" in *.lock) continue;; esac
    [ -S "$s" ] || continue
    # Skip a dead socket (redteam B1): a socket file survives its process.
    python3 -c "import socket,sys; s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); sys.exit(0 if s.connect_ex(sys.argv[1])==0 else 1)" "$s" 2>/dev/null || continue
    if [ -n "$NEST_DISPLAY" ]; then fail "ambiguous nested Wayland sockets in $RUN_DIR"; fi
    NEST_DISPLAY=$(basename "$s")
  done
  [ -n "$NEST_DISPLAY" ] && break
  sleep 1
done
[ -n "$NEST_DISPLAY" ] || fail "no nested Wayland socket in $RUN_DIR after 10s"
echo "Y6E-LOAD: nested socket $NEST_DISPLAY"

# Record the actual nest output name and use it for control calls.
[ -n "$NEST_DISPLAY" ] || fail "nest() called before socket discovery"
NEST_OUTPUT=$(nest hyprctl -j monitors 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d[0]['name'])" 2>/dev/null || echo "WAYLAND-1")
echo "Y6E-LOAD: nest output $NEST_OUTPUT"

nest hyprctl -j plugin list > "$NEST/y6e-nest-plugin-list.json" 2> "$NEST/y6e-nest-plugin-list.err" || fail "nested hyprctl plugin list failed"
grep -q hyprglass "$NEST/y6e-nest-plugin-list.json" || { grep -a -h "Y6-NEST-HOOK" "$LOG" "$NEST_LOG" 2>/dev/null; fail "hyprglass not in nested plugin list (hook marker above, if any)"; }
echo "Y6E-LOAD: hyprglass IS in the nested plugin list:"
grep -o '"name": "[^"]*"' "$NEST/y6e-nest-plugin-list.json"
nest hyprctl -j hyprglass status > "$NEST/y6e-nest-glass-status.json" 2> "$NEST/y6e-nest-glass-status.err" || fail "nested hyprglass status failed"
cat "$NEST/y6e-nest-glass-status.json"

# Parse the status JSON explicitly: fail fast on version mismatch with the
# observed version recorded. Council 3: if versionCheck is "unknown", the
# identity half of the guard is inert in that build; stop and report.
python3 - "$NEST/y6e-nest-glass-status.json" << 'PYEOF' || fail "hyprglass version mismatch or status unreadable (observed version recorded above)"
import json, sys
d = json.load(open(sys.argv[1]))
ver = d.get("version")
vc = d.get("versionCheck")
print("Y6E-LOAD: hyprglass version=" + str(ver) + " versionCheck=" + str(vc))
if ver != "1.1.1-cu.1" or vc != "match":
    print("Y6E-LOAD: NO-GO version mismatch: observed version=" + str(ver) + " versionCheck=" + str(vc))
    sys.exit(1)
PYEOF

# Y6C5-A4 (Y6r R1): the parse-1 "not ready" marker is EXPECTED on every
# successful startup and does NOT mean the profile is missing; the profile
# is applied on parse 2 (layers.enabled true against a default of false,
# optics.lua the only setter). This note only records the marker, it is not
# a profile verdict. The positive proof is the Y6-NEST-OPTICS applied marker.
if grep -a -q "Y6-NEST-HOOK: hyprglass not ready" "$LOG" "$NEST_LOG" 2>/dev/null; then
  echo "Y6E-LOAD: NOTE: parse-1 not-ready marker present (expected; profile applied on parse 2, load verdict unaffected)"
else
  echo "Y6E-LOAD: NOTE: parse-1 not-ready marker absent"
fi

echo "Y6E-LOAD: VERDICT: LOADED (rebuilt hyprglass 1.1.1-cu.1 listed in nested plugin list, versionCheck=match)"
echo "Y6E-LOAD: done $(date +%H:%M:%S)"
exit 0
