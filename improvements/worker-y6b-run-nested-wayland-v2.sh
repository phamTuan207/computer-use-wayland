#!/bin/bash
# Y6b Wayland-nested reproduction run, v2 + Y6d v3 fixes.
# v2 fixes U1-U21 from improvements/worker-y6b-adjudication.md (council 1/2/3 + redteam).
# v3 (Y6d): F0 socket discovery (no --socket; the nest auto-names its socket,
# discovered after launch); U5b Wayland-backend gate greps the per-instance
# log, not the stdout log.
# Y6C5 (2026-11-22, Y6r A1-A10): the staged conf is now the y6e conf
# (rebuilt hyprglass 1.1.1-cu.1, worktree 03a57c4); the backup-1 dead ABI is
# kept only as the rollback copy. U6 replaced by the positive profile gate
# (A2); AMEND4/AMEND5 ported (A5); G4 configerrors gate + G6 stats (A6); no
# manual reload (A7, R2); Y6_STOP_AFTER_GATES=1 stops after the gates for
# the A8 load-only trial (no pill, no arms).
# v3 adjudication fixes (council 1/2/3 + redteam, 21:02-21:08 +07): backend
# gate retry loop, ldd pre-flight ABI check, socket connect probe, nest()
# guard pre-check, pill liveness re-check, dangling-symlink cleanup.
# Runs a nested Hyprland as a Wayland client of the live compositor, loads backup 1
# hyprglass, and tests the 20/11 idle-pill flicker (hypothesis H-E, animated backdrop).
#
# Preconditions (all enforced below, none assumed):
#  - runner-quiet window: flock on zen_dom.lock PLUS a live process check for
#    runner scripts and geckodriver. The flock alone does not cover every runner
#    (A1 pilot arms use Chromium/CDP + broker and never touch the lock), so Muse
#    must also confirm in writing that no A1 arm is scheduled in this window.
#  - handover re-confirmed at run time: rerun with Y6_HANDOVER_CONFIRMED=1 only
#    after Muse confirms the owner is still away. A handover is time-bound.
#  - owner away: the nested window appears on the live screen. Do not click it.
#
# Duration estimate: launch ~10s + shader up to 60s + controls ~10s +
# pill start ~45s + 2 arms x ~40s + teardown ~10s = about 4 minutes.
# Overall deadline: 25 minutes from script start, checked before each arm.
# Window: 30 minutes, covering launch through teardown.
#
# Exit codes: 0 = run completed, verdict lines printed. 1 = NO-GO / abort (see log).
# Teardown always runs (trap on EXIT, TERM, INT, HUP): nest killed by process
# group, runtime dir removed after the nested log is copied out, live session
# re-verified (live PID resolved at runtime, hyprctl responds, live plugin
# list compared before/after for identity; the list contents are recorded,
# never assumed).
# Y6C5-A7 (Y6r R2, adjudicated): DO NOT add a manual `nest hyprctl reload`
# anywhere in this runner. Parse 2 already applies the profile
# deterministically (redteam section 1.2: STAGE_LATE loads the plugin
# synchronously and calls reload(), so parse 2 sees count=1 and dofiles
# optics.lua), so a reload buys nothing and risks a parse-3 duplicate
# layer() registration (open item O1, overwrite vs error unresolved) plus
# live-touch surface (a wrong-target reload would hit the live session).
# One application path only: the automatic parse-2 path (R8). If the
# positive gate ever shows the applied marker absent, the reload becomes
# the next hypothesis to test, not a preemptive addition. Enforced by
# tests/test_y6c5_positive_gate.py (no non-comment `hyprctl reload` line).
set -u
NEST=/tmp/y6-nested
RUN_DIR=$NEST/run
CONF=$NEST/conf/hyprland-wayland.lua
HOOK=$NEST/conf/nested-visuals-hook.lua
OPTICS=$NEST/conf/optics.lua
BACKDROP=$NEST/backdrop.mp4
BACKDROP_STATIC=$NEST/backdrop-static.mp4
PILL=$NEST/run-nested-pill.py
LOG=$NEST/hyprland-wayland.log
LOCK=$HOME/.cache/agent-computer-use/zen_dom.lock
LIVE_SOCK=/run/user/1000/wayland-1
# Live identity resolved at runtime (U15). Values verified at fix time, kept
# here only as a comment: LIVE_SIG=11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795249046_1138556825, LIVE_PID=1515.
START_TS=$(date +%Y%m%d-%H%M%S)
START_MONO=$(date +%s)
RUN_LOG=$NEST/run-$START_TS.log
FRAMES=$NEST/frames-$START_TS
NESTED_PID=""
NEST_HYPRLAND_PID=""
PILL_PID=""
MPV_PID=""
SIG=""
LIVE_SIG=""
LIVE_PID=""
NEST_STARTED=0
NEST_OUTPUT="WAYLAND-1"
NEST_DISPLAY=""

# Tee stdout to the run log (U20). The tee process is created before the flock
# fd exists, so it cannot inherit the lock.
exec > >(tee -a "$RUN_LOG") 2>&1

fail() { echo "Y6-WAYLAND: FAIL: $1"; exit 1; }

check_deadline() {
  local now elapsed
  now=$(date +%s); elapsed=$((now - START_MONO))
  if [ "$elapsed" -gt 1500 ]; then fail "overall deadline exceeded (${elapsed}s > 1500s) at $1"; fi
  echo "Y6-WAYLAND: deadline check OK (${elapsed}s elapsed) at $1"
}

# Owner-return detection (U19): loginctl IdleHint is PROVEN UNUSABLE on this
# machine (all 8 james sessions report IdleHint=no while the owner is away,
# including the graphical seat0/tty1 session). This check is WARN-ONLY and
# never aborts. The real protection is the explicit Muse go at run time plus
# the 25-minute deadline plus the short run duration.
check_idle() {
  local sess hint
  sess=$(loginctl --no-legend 2>/dev/null | awk '$3 == "james" && $4 == "seat0" {print $1; exit}')
  if [ -z "$sess" ]; then echo "Y6-WAYLAND: WARN: graphical loginctl session not found, skipping idle check at $1"; return 0; fi
  hint=$(loginctl show-session "$sess" -p IdleHint 2>/dev/null | cut -d= -f2)
  echo "Y6-WAYLAND: idle check at $1: session $sess IdleHint=${hint:-unknown} (warn-only, IdleHint is unreliable on this machine)"
}

# Nested-env helper: every nested hyprctl/grim/mpv call goes through nest().
# The trailing 9>&- keeps the flock fd out of every child (U7d).
# NEST_DISPLAY is the socket name discovered after launch (F0, v3); calling
# nest() before discovery is a fail-closed error, never a silent empty display.
nest() { [ -n "$NEST_DISPLAY" ] || fail "nest() called before socket discovery"; env XDG_RUNTIME_DIR="$RUN_DIR" WAYLAND_DISPLAY="$NEST_DISPLAY" HYPRLAND_INSTANCE_SIGNATURE="$SIG" "$@" 9>&-; }
live() { env XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-1 HYPRLAND_INSTANCE_SIGNATURE="$LIVE_SIG" "$@" 9>&-; }

# Randomized inter-frame delay, 0.6-1.4s (U13): a periodic about 10 Hz flicker
# cannot hide by phase lock with a fixed 1s cadence.
rand_sleep() { sleep "$(awk -v r="$RANDOM" 'BEGIN{srand(r); printf "%.2f", 0.6+rand()*0.8}')"; }

teardown() {
  echo "Y6-WAYLAND: teardown start $(date +%H:%M:%S)"
  # Copy the nested per-instance log out before removing the runtime dir (U7a).
  if [ "$NEST_STARTED" = "1" ] && [ -n "$SIG" ] && [ -d "$RUN_DIR/hypr/$SIG" ]; then
    cp -r "$RUN_DIR/hypr/$SIG" "$NEST/hypr-saved-$START_TS-$SIG" 2>/dev/null && echo "Y6-WAYLAND: nested log saved to $NEST/hypr-saved-$START_TS-$SIG" || echo "Y6-WAYLAND: WARN: nested log copy failed"
  fi
  if [ -n "$PILL_PID" ]; then kill "$PILL_PID" 2>/dev/null; sleep 1; kill -9 "$PILL_PID" 2>/dev/null; fi
  if [ -n "$MPV_PID" ]; then kill "$MPV_PID" 2>/dev/null; sleep 1; kill -9 "$MPV_PID" 2>/dev/null; fi
  if [ "$NEST_STARTED" = "1" ] && [ -n "$NESTED_PID" ]; then
    # Kill the whole nested session process group (U7c). setsid made
    # NESTED_PID the session leader, so the group is -$NESTED_PID.
    kill -- -$NESTED_PID 2>/dev/null; sleep 2; kill -9 -- -$NESTED_PID 2>/dev/null
  fi
  # Remove the runtime dir only if the nest was actually started (U7b).
  if [ "$NEST_STARTED" = "1" ]; then rm -rf "$RUN_DIR"; fi
  echo "Y6-WAYLAND: live check:"
  if [ -n "$LIVE_PID" ]; then ps -o pid,lstart,cmd -p "$LIVE_PID" || echo "Y6-WAYLAND: LIVE PID $LIVE_PID MISSING"; else echo "Y6-WAYLAND: LIVE PID never resolved"; fi
  if [ -n "$LIVE_SIG" ]; then
    if live hyprctl version > /tmp/y6-live-version.txt 2>&1; then head -4 /tmp/y6-live-version.txt; else echo "Y6-WAYLAND: live hyprctl FAILED"; fi
    # Y6C5-A5 (AMEND5, live plugin list AFTER identity): the before/after
    # lists must be identical; any change means the run touched live.
    # A failed after-read warns instead of misreporting a change.
    if [ -f "$NEST/live-plugin-list-before.json" ]; then
      if live hyprctl -j plugin list > "$NEST/live-plugin-list-after.json" 2>&1; then
        grep -o '"name": "[^"]*"' "$NEST/live-plugin-list-after.json" || echo "Y6-WAYLAND: (no plugins listed after)"
        if cmp -s "$NEST/live-plugin-list-before.json" "$NEST/live-plugin-list-after.json"; then
          echo "Y6-WAYLAND: live plugin list unchanged (before == after)"
        else
          echo "Y6-WAYLAND: FAIL: live plugin list CHANGED during run (before vs after):"
          diff "$NEST/live-plugin-list-before.json" "$NEST/live-plugin-list-after.json" || true
          echo "Y6-WAYLAND: FAIL: live plugin list changed during run"
          exit 1
        fi
      else
        echo "Y6-WAYLAND: WARN: live plugin list (after) could not be read in teardown"
      fi
    else
      live hyprctl -j plugin list 2>&1 | grep -o '"name": "[^"]*"' || echo "Y6-WAYLAND: live plugin list FAILED"
    fi
  else
    echo "Y6-WAYLAND: live signature never resolved"
  fi
  # Stray process check (U21). The live Hyprland (LIVE_PID) is expected;
  # anything else is a leftover to record.
  echo "Y6-WAYLAND: stray check (live Hyprland pid $LIVE_PID expected):"
  pgrep -a -x Hyprland || true
  pgrep -a -x mpv || true
  pgrep -a -x foot || true
  pgrep -af "native/indicator" || true
  # Lock free check (U7f). Close our own fd 9 first, or the test measures
  # our own hold: flock locks are per open file description.
  exec 9>&- 2>/dev/null || true
  if flock -n "$LOCK" -c true 2>/dev/null; then echo "Y6-WAYLAND: lock free after teardown"; else echo "Y6-WAYLAND: WARN: lock still held after teardown"; fi
  echo "Y6-WAYLAND: teardown done $(date +%H:%M:%S)"
}
trap teardown EXIT
trap 'exit 143' TERM
trap 'exit 130' INT
trap 'exit 129' HUP

echo "Y6-WAYLAND: start $(date +%H:%M:%S)"
[ "${Y6_HANDOVER_CONFIRMED:-0}" = "1" ] || fail "handover not re-confirmed at run time; confirm with Muse, then rerun with Y6_HANDOVER_CONFIRMED=1"
test -S "$LIVE_SOCK" || fail "live socket $LIVE_SOCK missing"
for f in "$CONF" "$HOOK" "$OPTICS" "$BACKDROP" "$BACKDROP_STATIC" "$PILL"; do test -f "$f" || fail "missing file $f"; done
command -v Hyprland >/dev/null || fail "Hyprland not found"
command -v grim >/dev/null || fail "grim not found"
command -v mpv >/dev/null || fail "mpv not found"
command -v ffmpeg >/dev/null || fail "ffmpeg not found"

# Y6C5-A5 (AMEND4, ported verbatim in shape from the Y6e load test): the
# skip var must be unset in the ambient env at launch, or the version gate
# is bypassed.
if env | grep -q "^HYPRGLASS_SKIP_VERSION_CHECK="; then fail "HYPRGLASS_SKIP_VERSION_CHECK is set in the ambient env; refusing to run (the version gate would be bypassed)"; fi
echo "Y6-WAYLAND: AMEND4 OK: HYPRGLASS_SKIP_VERSION_CHECK unset (env | grep HYPRGLASS empty)"
unset HYPRGLASS_SKIP_VERSION_CHECK

# Pre-flight ABI check (redteam A3): the conf's plugin .so must be loadable
# on this machine, or the run fails here in under a second with the cause
# instead of launching a nest and failing at the plugin-list gate with a
# misleading message. The config-time hl.plugin.load() logs nothing on a
# dead ABI, so ldd is the only diagnosis. The path is extracted from the
# conf, so it follows the rebuilt plugin once the conf is switched.
command -v ldd >/dev/null || fail "ldd not found, cannot verify plugin ABI"
GLASS_SO=$(grep -o '/[^"]*hyprglass[^"]*\.so' "$CONF" | head -1)
[ -n "$GLASS_SO" ] || fail "no hyprglass.so path in conf $CONF"
[ -f "$GLASS_SO" ] || fail "hyprglass path in conf missing on disk: $GLASS_SO"
LDD_OUT=$(ldd "$GLASS_SO" 2>&1) || fail "ldd failed on $GLASS_SO: $LDD_OUT"
MISSING_LIBS=$(printf '%s\n' "$LDD_OUT" | grep "not found" || true)
[ -z "$MISSING_LIBS" ] || fail "hyprglass $GLASS_SO cannot load (dead ABI): $MISSING_LIBS"
echo "Y6-WAYLAND: plugin ABI OK: $GLASS_SO"

# Y6C5-A5 (AMEND5-before, ported verbatim in shape from the Y6e load test):
# the LIVE config chain must contain no hyprglass LOAD PATH, so the live
# session can never load the rebuilt plugin. The load vector is a plugin.load
# call or a .so filesystem path naming hyprglass. Guarded API refs are INERT
# when the plugin is not loaded and do NOT fail the check: visuals-login.lua
# only dofiles the optics file when exactly one hyprglass 1.1.1-cu.1 is
# already loaded, and the optics file is itself guarded by
# `if hl.plugin.hyprglass then`. The live plugin list (hyprbars only, checked
# before and after) is the backstop for anything this walker misses,
# including the Omarchy bootstrap file, which is a distro default and is not
# followed here.
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
echo "Y6-WAYLAND: AMEND5-BEFORE OK: no hyprglass load path in live config chain (hyprland.lua + hyprland.conf + sourced files)"

# Resolve live identity at runtime (U15).
LIVE_SIG=$(ls -t /run/user/1000/hypr/ 2>/dev/null | head -1)
[ -n "$LIVE_SIG" ] || fail "no live Hyprland signature found"
[ "$(ls /run/user/1000/hypr/ | wc -l)" = "1" ] || fail "ambiguous live signatures, refusing to guess"
LIVE_PID=$(pgrep -x Hyprland)
[ -n "$LIVE_PID" ] || fail "no live Hyprland process found"
[ "$(echo "$LIVE_PID" | wc -l)" = "1" ] || fail "ambiguous live Hyprland PIDs, refusing to guess"
echo "Y6-WAYLAND: live sig $LIVE_SIG pid $LIVE_PID"

# Y6C5-A5 (AMEND5, live plugin list BEFORE): recorded, compared in teardown.
live hyprctl -j plugin list > "$NEST/live-plugin-list-before.json" 2>&1 || fail "live hyprctl plugin list (before) failed"
echo "Y6-WAYLAND: live plugin list BEFORE:"
grep -o '"name": "[^"]*"' "$NEST/live-plugin-list-before.json" || echo "Y6-WAYLAND: (no plugins listed)"

# Runner-quiet process check (U8). The flock is a tripwire, not a guarantee:
# several runners never touch the lock, and the A1 pilot arms use Chromium/CDP
# plus the broker. The bracket trick ([.] instead of .) keeps pgrep -f from
# matching its own command line.
if pgrep -af "run_agyq2[.]py|run_live[.]py|run_agyq[.]py|run_agy_y2[.]py|run_fcck[.]py" 2>/dev/null | grep -v "pgrep -af"; then
  fail "live runner process found; abort, do not run"
fi
if pgrep -x geckodriver >/dev/null; then
  fail "geckodriver running; a live runner is active, abort"
fi
# Pre-launch guard (C3-4): no mpv or foot may already be running, or the
# PID-scoped mpv tracking below is ambiguous.
if pgrep -x mpv >/dev/null || pgrep -x foot >/dev/null; then
  fail "mpv or foot already running; abort, do not run"
fi
echo "Y6-WAYLAND: runner-quiet process check OK (no runner scripts, no geckodriver, no mpv/foot)"

# Hold the runner lock for the whole run. flock -n fails if any runner holds it.
exec 9>"$LOCK" || fail "cannot open lock $LOCK"
flock -n 9 || fail "zen_dom.lock held by a runner; abort, do not run"
echo "Y6-WAYLAND: flock held, runner-quiet window open"

# Clear stale nest runtime state (F0, v3): the socket name is discovered at
# launch, so remove any wayland-* socket/lock left by a previous run.
rm -rf "$RUN_DIR/hypr"
for stale in "$RUN_DIR"/wayland-*; do if [ -e "$stale" ] || [ -L "$stale" ]; then rm -rf "$stale"; fi; done
mkdir -p "$RUN_DIR" "$FRAMES" "$NEST/cache"

# Parent connection: absolute live socket path, so XDG_RUNTIME_DIR is irrelevant
# for the parent connection (Council C change 1). No --socket flag (F0, v3):
# in 0.57.2 passing --socket without --wayland-fd is a hard startup error, so
# the nest auto-names its socket and the launcher discovers it below.
# setsid may fork (it is a process group leader when run under job control), so
# the timeout PID is captured via a pidfile, not via $! (a dead parent's PID).
export XDG_RUNTIME_DIR="$RUN_DIR"
export WAYLAND_DISPLAY="$LIVE_SOCK"
unset HYPRLAND_INSTANCE_SIGNATURE
rm -f "$NEST/nest-timeout.pid"
setsid bash -c "echo \$\$ > \"$NEST/nest-timeout.pid\"; exec timeout 600 Hyprland --config \"$CONF\"" > "$LOG" 2>&1 < /dev/null 9>&- &
for i in $(seq 1 10); do sleep 1; [ -s "$NEST/nest-timeout.pid" ] && break; done
NESTED_PID=$(cat "$NEST/nest-timeout.pid" 2>/dev/null || echo "")
[ -n "$NESTED_PID" ] || fail "nested launcher did not write its pidfile"
NEST_STARTED=1
echo "Y6-WAYLAND: nested pid $NESTED_PID (timeout wrapper, session leader)"

for i in $(seq 1 15); do sleep 1; SIG=$(ls -t "$RUN_DIR/hypr/" 2>/dev/null | head -1); [ -n "$SIG" ] && break; done
[ -n "$SIG" ] || fail "no nested instance signature after 15s"
echo "Y6-WAYLAND: nested sig $SIG"
export Y6_NEST_SIG="$SIG"
# Per-instance log path (U5b, v3): defined here, used by the backend gate below
# and the hook-marker check later. The stdout log alone is NOT enough: after
# postConfigReload disables stdout logging, the backend line lands only here.
NEST_LOG="$RUN_DIR/hypr/$SIG/hyprland.log"

# Record the real nested Hyprland PID (child of the timeout wrapper).
NEST_HYPRLAND_PID=$(pgrep -P "$NESTED_PID" -x Hyprland | head -1)
echo "Y6-WAYLAND: nested Hyprland pid ${NEST_HYPRLAND_PID:-unknown}"

# Post-launch: the nested log must show the Wayland backend started (U5).
# The grep is now gating, not display-only. It greps the PER-INSTANCE log
# (U5b, v3): on a healthy start the line goes only there, never to stdout.
sleep 5
[ -f "$NEST_LOG" ] || fail "nested per-instance log $NEST_LOG missing"
# Retry the gate for up to 10s (redteam A1): the backend line can lag the
# signature on a loaded machine, and a single-shot grep false-fails a
# healthy slow start. Exact line: no failure line contains it.
BACKEND_OK=""
for i in $(seq 1 10); do
  if grep -a -q "Starting the Wayland backend!" "$NEST_LOG" 2>/dev/null; then BACKEND_OK=1; break; fi
  sleep 1
done
if [ -n "$BACKEND_OK" ]; then grep -a "Starting the Wayland backend!" "$NEST_LOG" | head -3;
else tail -20 "$LOG"; fail "Wayland backend did not start in nested log $NEST_LOG (stdout tail above)"; fi
# The nest must still be alive after the gate (redteam B3): a nest that
# logs the line then dies would otherwise fail later with a misleading message.
[ -n "$NEST_HYPRLAND_PID" ] && kill -0 "$NEST_HYPRLAND_PID" 2>/dev/null || fail "nested Hyprland died after backend start (pid ${NEST_HYPRLAND_PID:-unknown})"

# Discover the nested Wayland socket name (F0, v3): without --socket the nest
# auto-names its socket (probe-proven: wayland-1). Exactly one non-lock
# wayland-* socket must exist; zero is missing, two or more is ambiguous.
# The scan re-runs for up to 10s because the socket may lag the signature.
for i in $(seq 1 10); do
  NEST_DISPLAY=""
  for s in "$RUN_DIR"/wayland-*; do
    case "$s" in *.lock) continue;; esac
    [ -S "$s" ] || continue
    # Skip a dead socket (redteam B1): a socket file survives its process,
    # so a nest that dies after binding would otherwise be picked and fail
    # later at hyprctl with a misleading message. A refused candidate is
    # skipped, not fatal: the retry loop keeps waiting for the live socket.
    python3 -c "import socket,sys; s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); sys.exit(0 if s.connect_ex(sys.argv[1])==0 else 1)" "$s" 2>/dev/null || continue
    if [ -n "$NEST_DISPLAY" ]; then fail "ambiguous nested Wayland sockets in $RUN_DIR"; fi
    NEST_DISPLAY=$(basename "$s")
  done
  [ -n "$NEST_DISPLAY" ] && break
  sleep 1
done
[ -n "$NEST_DISPLAY" ] || fail "no nested Wayland socket in $RUN_DIR after 10s"
echo "Y6-WAYLAND: nested socket $NEST_DISPLAY"

# Record the actual nest output name (U16) and use it for the control frames.
# Fail-closed pre-check (council 1 A1): the nest() guard cannot kill the
# parent from inside this command substitution, so check directly here.
[ -n "$NEST_DISPLAY" ] || fail "nest() called before socket discovery"
NEST_OUTPUT=$(nest hyprctl -j monitors 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d[0]['name'])" 2>/dev/null || echo "WAYLAND-1")
echo "Y6-WAYLAND: nest output $NEST_OUTPUT"

nest hyprctl -j plugin list > "$NEST/nest-plugin-list.json" 2> "$NEST/nest-plugin-list.err" || fail "nested hyprctl plugin list failed"
grep -q hyprglass "$NEST/nest-plugin-list.json" || { grep -a -h "Y6-NEST-HOOK" "$LOG" "$NEST_LOG" 2>/dev/null; fail "hyprglass not in nested plugin list (hook marker above, if any)"; }
nest hyprctl -j hyprglass status > "$NEST/nest-glass-status.json" 2> "$NEST/nest-glass-status.err" || fail "nested hyprglass status failed"
cat "$NEST/nest-glass-status.json"

# Parse the status JSON explicitly (U6): fail fast on version mismatch with
# the observed version recorded, instead of burning the 60s liquid gate.
python3 - "$NEST/nest-glass-status.json" << 'PYEOF' || fail "hyprglass version mismatch or status unreadable (observed version recorded above)"
import json, sys
d = json.load(open(sys.argv[1]))
ver = d.get("version")
vc = d.get("versionCheck")
print("Y6-WAYLAND: hyprglass version=" + str(ver) + " versionCheck=" + str(vc))
if ver != "1.1.1-cu.1" or vc != "match":
    print("Y6-WAYLAND: NO-GO version mismatch: observed version=" + str(ver) + " versionCheck=" + str(vc))
    sys.exit(1)
PYEOF

# BEGIN Y6C5-A2 positive profile gate (Y6r A2, R3; replaces the old U6 block)
# The parse-1 "not ready" marker is EXPECTED on every successful startup
# (parse 1 runs before the plugin system exists; the profile is applied on
# parse 2). It must NEVER fail the run. This gate is positive: it requires
# the applied marker printed AFTER optics.lua returns, plus a second signal,
# features.layers.enabled == true, read from the status JSON fetched above.
# The marker proves config()+layer() returned; layers.enabled proves the
# config effect (optics.lua is the only setter; the plugin default is false).
# Y6C5-A10: this greps the LIVE per-instance log ($NEST_LOG) during the run
# (plus the stdout log $LOG). Saved-log marker counts are NOT parse evidence
# (ofstream buffering; saved logs are flushed prefixes, tail lost on SIGKILL
# teardown). No gate here reads a hypr-saved directory.
# Poll timeout/interval are overridable for tests (Y6C5_GATE_TIMEOUT_S,
# Y6C5_GATE_INTERVAL_S); production defaults are 15 s / 1 s. By the time
# this gate runs (about 10 s after launch) parse 2 has already applied the
# profile, so the poll is a margin for log flush lag, not for the load.
echo "Y6-WAYLAND: profile gate: parse-1 not-ready marker is expected, waiting for applied marker"
if grep -a -q "Y6-NEST-HOOK: hyprglass not ready" "$LOG" "$NEST_LOG" 2>/dev/null; then
  echo "Y6-WAYLAND: profile gate: parse-1 not-ready marker present (expected, not a failure)"
fi
GATE_TIMEOUT="${Y6C5_GATE_TIMEOUT_S:-15}"
GATE_INTERVAL="${Y6C5_GATE_INTERVAL_S:-1}"
GATE_DEADLINE=$(( $(date +%s) + GATE_TIMEOUT ))
GATE_OK=""
while [ "$(date +%s)" -le "$GATE_DEADLINE" ]; do
  if grep -a -q "Y6-NEST-OPTICS: applied" "$LOG" "$NEST_LOG" 2>/dev/null; then GATE_OK=1; break; fi
  sleep "$GATE_INTERVAL"
done
if [ -z "$GATE_OK" ]; then
  echo "Y6-WAYLAND: profile gate: applied marker absent after ${GATE_TIMEOUT}s (tail of nested log):"
  tail -30 "$NEST_LOG" 2>/dev/null || tail -30 "$LOG"
  fail "profile not applied: Y6-NEST-OPTICS applied marker absent after ${GATE_TIMEOUT}s; see nested log tail above"
fi
grep -a -h "Y6-NEST-OPTICS: applied" "$LOG" "$NEST_LOG" 2>/dev/null | head -3
HOOK_APPLIED=$(grep -a -h "Y6-NEST-HOOK: profile applied" "$LOG" "$NEST_LOG" 2>/dev/null | head -3 || true)
if [ -n "$HOOK_APPLIED" ]; then printf '%s\n' "$HOOK_APPLIED"; else echo "Y6-WAYLAND: profile gate: hook applied marker not seen in logs (optics marker present, continuing)"; fi
# Second positive signal: layers.enabled must be true in the status JSON
# fetched above (optics.lua is the only setter; the plugin default is false).
# NOTE: this is an early read of the same field the liquid gate already
# requires (scripts/indicator.py _valid_liquid needs layers.enabled True);
# its value is failing fast here instead of after a 60 s liquid wait.
python3 - "$NEST/nest-glass-status.json" << 'PYEOF' || fail "profile not applied: features.layers.enabled is not true in hyprglass status (see status JSON above)"
import json, sys
d = json.load(open(sys.argv[1]))
layers = (d.get("features") or {}).get("layers") or {}
print("Y6-WAYLAND: profile gate: features.layers.enabled=" + str(layers.get("enabled")))
if layers.get("enabled") is not True:
    sys.exit(1)
PYEOF
# Re-run the plugin-list and version checks after the marker: the profile
# must still be loaded when the gate passes, not only at the earlier check.
nest hyprctl -j plugin list > "$NEST/nest-plugin-list-after-gate.json" 2> "$NEST/nest-plugin-list-after-gate.err" || fail "nested hyprctl plugin list re-check failed after profile gate"
grep -q hyprglass "$NEST/nest-plugin-list-after-gate.json" || fail "hyprglass missing from nested plugin list on re-check after profile gate"
nest hyprctl -j hyprglass status > "$NEST/nest-glass-status-after-gate.json" 2> "$NEST/nest-glass-status-after-gate.err" || fail "nested hyprglass status re-check failed after profile gate"
python3 - "$NEST/nest-glass-status-after-gate.json" << 'PYEOF' || fail "hyprglass version mismatch on re-check after profile gate"
import json, sys
d = json.load(open(sys.argv[1]))
ver = d.get("version"); vc = d.get("versionCheck")
print("Y6-WAYLAND: profile gate re-check: hyprglass version=" + str(ver) + " versionCheck=" + str(vc))
if ver != "1.1.1-cu.1" or vc != "match":
    sys.exit(1)
PYEOF
echo "Y6-WAYLAND: profile gate OK: applied marker present, layers.enabled true, plugin list and version re-checked"
# END Y6C5-A2 positive profile gate

# BEGIN Y6C5-A6-G4 configerrors gate
# Y6C5-A6 (Council 3 G4, supporting gate): nest configerrors must be empty
# after profile application. A throwing optics.lua surfaces as a config
# error, not as a missing marker, so this is the only gate catching that
# case. Pattern follows scripts/activation_checks.py wait_for_profile
# (stripped output must be empty). A failed configerrors call fails closed.
# KNOWN TENSION (open item O1): if parse-3 duplicate layer() registration
# errors, configerrors is non-empty while the parse-2 profile stands, and
# this gate would false-fail a healthy profile. The A8 load-only trial
# observes the exact configerrors content; if the trial shows a parse-3
# duplicate-layer error with marker present and layers.enabled true, G4
# must be narrowed to allow that specific error.
CONFIG_ERRORS=$(nest hyprctl configerrors 2>&1) || fail "nest hyprctl configerrors failed (see above)"
if [ -n "$(printf '%s' "$CONFIG_ERRORS" | tr -d '[:space:]')" ]; then
  printf '%s\n' "$CONFIG_ERRORS"
  fail "nest config errors present after profile application (see above)"
fi
echo "Y6-WAYLAND: configerrors empty after profile application (G4 OK)"
# END Y6C5-A6-G4 configerrors gate

# Liquid gate: liquid_available(ready=True) semantics exactly (indicator.py).
# Shaders up to 60s: 30s LIQUID_READY_TIMEOUT + one 30s extension (Council C).
# Version mismatch is NO-GO with the observed version recorded; do NOT substitute
# the backup 2 .so and do NOT proceed with a mismatched profile.
nest python3 - << "PYEOF" || fail "liquid gate failed (see above; version mismatch or shader error is NO-GO)"
import sys
import time
sys.path.insert(0, "/home/james/workspace/computer-use-wayland/scripts")
import indicator
env = dict(__import__("os").environ)
deadline = time.monotonic() + 60
while True:
    ok = indicator.liquid_available(env, ready=True)
    print("Y6-WAYLAND: liquid ready=" + str(ok), flush=True)
    if ok:
        break
    if time.monotonic() > deadline:
        print("Y6-WAYLAND: liquid never ready in 60s", flush=True)
        sys.exit(1)
    time.sleep(2)
PYEOF

# Y6C5-A8 (load-only trial support): stop after the gates, before any
# backdrop, pill, or arm. The A8 trial runs the amended runner with
# Y6_STOP_AFTER_GATES=1 and proves the fix itself; the EXIT trap still runs
# teardown and re-verifies live. Production runs leave this unset.
if [ "${Y6_STOP_AFTER_GATES:-0}" = "1" ]; then
  echo "Y6-WAYLAND: stop-after-gates requested (A8 load-only trial): gates passed, stopping before backdrop/pill/arms"
  exit 0
fi

# Nest renderer lines (U17): the asymmetry clause needs a known rendering path.
echo "Y6-WAYLAND: nest renderer lines:"
grep -a -i -E "renderer|gles|opengl|egl" "$NEST_LOG" 2>/dev/null | head -10 || echo "Y6-WAYLAND: no renderer lines found in nested log"

# Backdrop client, launched from the launcher with explicit nest env (U3).
# No autostart mpv/foot in the nest config: config-time exec children may
# inherit the parent display instead of the nest socket (unverified), and foot
# serves no measurement purpose. mpv is tracked by PID, never by pkill -x.
env XDG_RUNTIME_DIR="$RUN_DIR" WAYLAND_DISPLAY="$NEST_DISPLAY" HYPRLAND_INSTANCE_SIGNATURE="$SIG" mpv --loop=inf --no-audio --fullscreen "$BACKDROP" > "$NEST/nest-mpv.log" 2>&1 < /dev/null 9>&- &
MPV_PID=$!
sleep 2
kill -0 "$MPV_PID" 2>/dev/null || fail "mpv backdrop client did not start"
[ "$(ps -o comm= -p "$MPV_PID" 2>/dev/null)" = "mpv" ] || fail "MPV_PID $MPV_PID is not mpv"
echo "Y6-WAYLAND: animated mpv pid $MPV_PID"

# Positive control (Council C change 3): the backdrop must move BEFORE the pill
# starts. Two full-output frames 1s apart must differ, or the animation source
# is broken and the run stops here.
nest grim -o "$NEST_OUTPUT" "$FRAMES/control-1.png" || fail "grim control frame 1 failed"
sleep 1
nest grim -o "$NEST_OUTPUT" "$FRAMES/control-2.png" || fail "grim control frame 2 failed"
if cmp -s "$FRAMES/control-1.png" "$FRAMES/control-2.png"; then
  fail "positive control FAILED: backdrop frames identical, animation source is not moving"
fi
echo "Y6-WAYLAND: positive control OK: backdrop moves"

check_deadline "before pill"
check_idle "before pill"

# Start the pill (separate state dir; see run-nested-pill.py). Wait for ready.
# The pill prints ready only after show succeeds (U9), so ready means visible.
env XDG_RUNTIME_DIR="$RUN_DIR" WAYLAND_DISPLAY="$NEST_DISPLAY" HYPRLAND_INSTANCE_SIGNATURE="$SIG" Y6_NEST_SIG="$SIG" python3 "$PILL" > "$NEST/nest-pill.log" 2>&1 < /dev/null 9>&- &
PILL_PID=$!
sleep 1
kill -0 "$PILL_PID" 2>/dev/null || fail "pill process died immediately (see $NEST/nest-pill.log)"
READY=""
for i in $(seq 1 45); do sleep 1; kill -0 "$PILL_PID" 2>/dev/null || fail "pill died during ready wait (see $NEST/nest-pill.log)"; grep -q "Y6-NEST-PILL: ready" "$NEST/nest-pill.log" 2>/dev/null && READY=1 && break; done
[ -n "$READY" ] || fail "pill did not become ready in 45s (see $NEST/nest-pill.log)"
echo "Y6-WAYLAND: pill ready, pid $PILL_PID"
sleep 2

# Read pill geometry from the nested layer list (namespace computer-use-indicator).
# Prints "X,Y WxH" in grim form (U1, U2). The layers JSON has a "levels" wrapper.
read_pill_geom() {
  nest hyprctl -j layers > "$NEST/nest-layers.json" 2>&1 || return 1
  python3 - "$NEST/nest-layers.json" << 'PYEOF' || return 1
import json
import sys
data = json.load(open(sys.argv[1]))
for monitor, mdata in data.items():
    for level, entries in mdata.get("levels", {}).items():
        for e in entries:
            if e.get("namespace") == "computer-use-indicator":
                print(str(e["x"]) + "," + str(e["y"]) + " " + str(e["w"]) + "x" + str(e["h"]))
                sys.exit(0)
sys.exit(1)
PYEOF
}

# Pick a 200x200 backdrop corner with zero intersection with the pill rect (U12).
# Args: pill x y w h. Prints "X,Y 200x200" or nothing.
compute_backdrop_geom() {
  python3 - "$1" "$2" "$3" "$4" << 'PYEOF' || return 1
import sys
px, py, pw, ph = (int(v) for v in sys.argv[1:5])
cands = [(0, 0), (760, 0), (0, 340), (760, 340)]
for cx, cy in cands:
    if cx + 200 <= px or cx >= px + pw or cy + 200 <= py or cy >= py + ph:
        print(str(cx) + "," + str(cy) + " 200x200")
        sys.exit(0)
sys.exit(1)
PYEOF
}

PILL_GEOM=$(read_pill_geom) || fail "pill surface not found in nested layers (pill not visible)"
echo "Y6-WAYLAND: pill geometry $PILL_GEOM"
PILL_X=$(echo "$PILL_GEOM" | cut -d, -f1)
PILL_Y=$(echo "$PILL_GEOM" | cut -d, -f2 | cut -d' ' -f1)
PILL_W=$(echo "$PILL_GEOM" | cut -d' ' -f2 | cut -dx -f1)
PILL_H=$(echo "$PILL_GEOM" | cut -dx -f2)
# Bounds check: the pill rect must lie inside the 960x540 nest output (U12).
if [ "$PILL_X" -lt 0 ] || [ "$PILL_Y" -lt 0 ] || [ $((PILL_X + PILL_W)) -gt 960 ] || [ $((PILL_Y + PILL_H)) -gt 540 ]; then
  fail "pill rect $PILL_GEOM outside the 960x540 nest output"
fi
BACKDROP_GEOM=$(compute_backdrop_geom "$PILL_X" "$PILL_Y" "$PILL_W" "$PILL_H") || fail "no backdrop corner clear of the pill rect"
echo "Y6-WAYLAND: backdrop sample geometry $BACKDROP_GEOM"

# Frame capture helper: capture PREFIX INDEX GEOMETRY.
# Geometry is grim form "X,Y WxH" (U2). No -o: -g alone selects the output it
# intersects, and -g plus -o are mutually exclusive in grim.
capture() { nest grim -g "$3" "$FRAMES/$1-$2.png" || fail "grim $1-$2 failed"; }

# Kill the tracked mpv by PID and confirm death. Never pkill -x mpv.
kill_mpv() {
  [ -n "$MPV_PID" ] || return 0
  kill "$MPV_PID" 2>/dev/null; sleep 1; kill -9 "$MPV_PID" 2>/dev/null; sleep 1
  if kill -0 "$MPV_PID" 2>/dev/null; then fail "mpv pid $MPV_PID did not die for $1"; fi
  MPV_PID=""
}

# Start an mpv instance with explicit nest env and record its PID.
# Args: FILE LOGFILE. The caller checks the PID with kill -0 afterwards.
start_mpv() {
  env XDG_RUNTIME_DIR="$RUN_DIR" WAYLAND_DISPLAY="$NEST_DISPLAY" HYPRLAND_INSTANCE_SIGNATURE="$SIG" mpv --loop=inf --no-audio --fullscreen "$1" > "$2" 2>&1 < /dev/null 9>&- &
  MPV_PID=$!
  sleep 2
  kill -0 "$MPV_PID" 2>/dev/null || fail "mpv did not start for $1"
  [ "$(ps -o comm= -p "$MPV_PID" 2>/dev/null)" = "mpv" ] || fail "MPV_PID $MPV_PID is not mpv"
  echo "Y6-WAYLAND: mpv pid $MPV_PID playing $1"
}

# Arm A (STATIC backdrop, pill idle): decisive. Any pill-region change = flicker.
# The backdrop is a frozen frame of the video (U4), and a backdrop sample is
# captured at the same cadence; the arm is VOID if the backdrop moves (U11).
# Globals set: ARM_A_PILL_DIFF, ARM_A_BG_DIFF.
run_arm_A() {
  local pass_label="$1" i j pill_diff bg_diff
  pill_diff=0; bg_diff=0
  for i in $(seq -w 1 32); do
    capture "armA-${pass_label}" "$i" "$PILL_GEOM"
    capture "armA-bg-${pass_label}" "$i" "$BACKDROP_GEOM"
    rand_sleep
  done
  for i in $(seq -w 1 31); do
    j=$(printf "%02d" $((10#$i + 1)))
    cmp -s "$FRAMES/armA-${pass_label}-$i.png" "$FRAMES/armA-${pass_label}-$j.png" || pill_diff=$((pill_diff + 1))
    cmp -s "$FRAMES/armA-bg-${pass_label}-$i.png" "$FRAMES/armA-bg-${pass_label}-$j.png" || bg_diff=$((bg_diff + 1))
  done
  echo "Y6-WAYLAND: ARM A ($pass_label): pill pairs differ $pill_diff/31; backdrop pairs differ $bg_diff/31"
  ARM_A_PILL_DIFF=$pill_diff
  ARM_A_BG_DIFF=$bg_diff
}

# Y6C5-A6 (Council 3 G6, corroboration only, never a gate): record hyprglass
# stats at a named point. The JSON key is contourRebuilds (the table column
# is contour_build). No baseline exists yet, so no threshold and no fail on
# missing stats (warn only).
record_glass_stats() {
  if nest hyprctl hyprglass stats > "$NEST/nest-glass-stats-$1.json" 2> "$NEST/nest-glass-stats-$1.err"; then
    echo "Y6-WAYLAND: glass stats ($1):"
    cat "$NEST/nest-glass-stats-$1.json"
  else
    echo "Y6-WAYLAND: glass stats ($1) unavailable (see $NEST/nest-glass-stats-$1.err)"
  fi
}

check_deadline "before arm A"
check_idle "before arm A"
record_glass_stats before-arms
echo "Y6-WAYLAND: arm A start $(date +%H:%M:%S)"
# Switch the backdrop to the static image (U4).
kill_mpv "static arm"
start_mpv "$BACKDROP_STATIC" "$NEST/nest-mpv-static.log"
run_arm_A "pass1"
A_DIFF=$ARM_A_PILL_DIFF; A_BG_DIFF=$ARM_A_BG_DIFF
A_OUTCOME="negative"
if [ "$A_BG_DIFF" -gt 0 ]; then A_OUTCOME="void";
elif [ "$A_DIFF" -ge 3 ]; then A_OUTCOME="reproduced";
elif [ "$A_DIFF" -ge 1 ]; then
  echo "Y6-WAYLAND: arm A pass1 inconclusive ($A_DIFF/31), rerunning arm A once"
  run_arm_A "pass2"
  A_DIFF=$ARM_A_PILL_DIFF; A_BG_DIFF=$ARM_A_BG_DIFF
  if [ "$A_BG_DIFF" -gt 0 ]; then A_OUTCOME="void";
  elif [ "$A_DIFF" -ge 3 ]; then A_OUTCOME="reproduced";
  elif [ "$A_DIFF" -ge 1 ]; then A_OUTCOME="inconclusive";
  else A_OUTCOME="negative"; fi
fi
echo "Y6-WAYLAND: ARM A outcome $A_OUTCOME (pill diff $A_DIFF/31, backdrop diff $A_BG_DIFF/31)"

check_deadline "before arm B"
check_idle "before arm B"
echo "Y6-WAYLAND: arm B start $(date +%H:%M:%S)"
# Restart the animated backdrop (U11).
kill_mpv "animated arm"
start_mpv "$BACKDROP" "$NEST/nest-mpv-armB.log"
# Motion re-validation: two consecutive full-output frames must differ
# (bounded 10s) before starting arm B captures.
MOTION_OK=0
for i in 1 2 3 4 5; do
  nest grim -o "$NEST_OUTPUT" "$FRAMES/armB-motion-1.png" || fail "grim armB motion frame 1 failed"
  sleep 1
  nest grim -o "$NEST_OUTPUT" "$FRAMES/armB-motion-2.png" || fail "grim armB motion frame 2 failed"
  if ! cmp -s "$FRAMES/armB-motion-1.png" "$FRAMES/armB-motion-2.png"; then MOTION_OK=1; break; fi
  sleep 1
done
[ "$MOTION_OK" = "1" ] || fail "arm B motion re-validation failed: animated backdrop not moving"
echo "Y6-WAYLAND: arm B motion re-validated, backdrop moves"
# Re-read pill geometry before arm B (U12). Re-baseline if it moved, and
# recompute the backdrop corner from the new rect.
PILL_GEOM_NEW=$(read_pill_geom) || fail "pill surface not found before arm B"
if [ "$PILL_GEOM_NEW" != "$PILL_GEOM" ]; then
  echo "Y6-WAYLAND: WARN: pill geometry moved ($PILL_GEOM -> $PILL_GEOM_NEW), re-baselining"
  PILL_GEOM=$PILL_GEOM_NEW
  PILL_X=$(echo "$PILL_GEOM" | cut -d, -f1)
  PILL_Y=$(echo "$PILL_GEOM" | cut -d, -f2 | cut -d' ' -f1)
  PILL_W=$(echo "$PILL_GEOM" | cut -d' ' -f2 | cut -dx -f1)
  PILL_H=$(echo "$PILL_GEOM" | cut -dx -f2)
  BACKDROP_GEOM=$(compute_backdrop_geom "$PILL_X" "$PILL_Y" "$PILL_W" "$PILL_H") || fail "no backdrop corner clear of the moved pill rect"
  echo "Y6-WAYLAND: backdrop sample geometry now $BACKDROP_GEOM"
fi

# Arm B (ANIMATED backdrop, pill idle): incident condition. Per-pair readout:
# pill_diff? + backdrop_diff? A pair where the pill differs but the backdrop is
# identical is flicker evidence. Both differing is expected motion.
B_PILL_DIFF=0; B_BG_DIFF=0; B_PILL_ONLY=0
for i in $(seq -w 1 32); do
  capture armB "$i" "$PILL_GEOM"
  capture armB-bg "$i" "$BACKDROP_GEOM"
  rand_sleep
done
for i in $(seq -w 1 31); do
  j=$(printf "%02d" $((10#$i + 1)))
  pd=0; bd=0
  cmp -s "$FRAMES/armB-$i.png" "$FRAMES/armB-$j.png" || pd=1
  cmp -s "$FRAMES/armB-bg-$i.png" "$FRAMES/armB-bg-$j.png" || bd=1
  B_PILL_DIFF=$((B_PILL_DIFF + pd)); B_BG_DIFF=$((B_BG_DIFF + bd))
  if [ "$pd" = "1" ] && [ "$bd" = "0" ]; then B_PILL_ONLY=$((B_PILL_ONLY + 1)); fi
done
echo "Y6-WAYLAND: ARM B (animated): pill pairs differ $B_PILL_DIFF/31; backdrop pairs differ $B_BG_DIFF/31; pill-only differs $B_PILL_ONLY/31"
B_OUTCOME="negative"
if [ "$B_BG_DIFF" -lt 15 ]; then B_OUTCOME="void";
elif [ "$B_PILL_ONLY" -ge 3 ]; then B_OUTCOME="reproduced";
elif [ "$B_PILL_ONLY" -ge 1 ]; then B_OUTCOME="inconclusive";
else B_OUTCOME="negative"; fi
echo "Y6-WAYLAND: ARM B outcome $B_OUTCOME"

# Verdict lines (U10, U11, U14). Only B_PILL_ONLY is flicker evidence in the
# animated arm: the pill-surface region differs under pure expected motion
# (it shows the moving backdrop through its transparent margins).
echo "Y6-WAYLAND: SUMMARY armA_outcome=$A_OUTCOME armA_diff=$A_DIFF/31 armA_bg_diff=$A_BG_DIFF/31 armB_outcome=$B_OUTCOME armB_pill_diff=$B_PILL_DIFF/31 armB_bg_diff=$B_BG_DIFF/31 armB_pill_only=$B_PILL_ONLY/31"
echo "Y6-WAYLAND: NOTE: only armB_pill_only is flicker evidence in the animated arm; armB_pill_diff is high under pure expected motion."
if [ "$A_OUTCOME" = "reproduced" ]; then
  echo "Y6-WAYLAND: VERDICT: REPRODUCED (static arm: pill region changed with a static backdrop)"
elif [ "$B_OUTCOME" = "reproduced" ]; then
  echo "Y6-WAYLAND: VERDICT: REPRODUCED in animated arm only (pill changed while its backdrop sample was identical)"
elif [ "$A_OUTCOME" = "inconclusive" ] || [ "$B_OUTCOME" = "inconclusive" ]; then
  echo "Y6-WAYLAND: VERDICT: INCONCLUSIVE (arm A $A_OUTCOME, arm B $B_OUTCOME; counts in SUMMARY)"
elif [ "$A_OUTCOME" = "void" ] && [ "$B_OUTCOME" = "void" ]; then
  echo "Y6-WAYLAND: VERDICT: VOID (both arms invalid; no verdict)"
elif [ "$A_OUTCOME" = "negative" ] && [ "$B_OUTCOME" = "negative" ]; then
  echo "Y6-WAYLAND: VERDICT: NOT reproduced in the nest (see asymmetry clause in the report: a nest negative does not exonerate the live backdrop)"
elif [ "$A_OUTCOME" = "negative" ] && [ "$B_OUTCOME" = "void" ]; then
  echo "Y6-WAYLAND: VERDICT: NOT reproduced in the nest (static arm negative; animated arm void)"
elif [ "$A_OUTCOME" = "void" ] && [ "$B_OUTCOME" = "negative" ]; then
  echo "Y6-WAYLAND: VERDICT: NOT reproduced in the nest (animated arm negative; static arm void)"
else
  echo "Y6-WAYLAND: VERDICT: VOID (uncovered outcome combination: arm A $A_OUTCOME, arm B $B_OUTCOME)"
fi
record_glass_stats after-arms
echo "Y6-WAYLAND: done $(date +%H:%M:%S)"
exit 0
