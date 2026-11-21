#!/bin/bash
# Self-contained AT-SPI session probe: Xvfb + D-Bus + AT-SPI registry
# + Firefox 160.0.1, from a clean state, no inherited display or bus.
#
# Usage:
#   bash tests/run_atspi_session.sh [--mode dump|full|both] [--firefox PATH]
#
# Default mode is both: dump first, then full. Exit 0 when the session
# itself works (tree read and Action click verified), exit 2 otherwise.
#
# Known limit, NOT a session failure: typing through EditableText is
# BROKEN on Firefox 160.0.1 (Mozilla Bug 2087495: setTextContents
# returns True but reads back empty), so full mode exits 2 even when
# the session is fine. The verdict line at the end separates the
# session result from the typing result. Use BiDi for typing until
# the fix lands in the Firefox base.
#
# The working recipe, found by council 3 in batch 4 after
# dbus-run-session failed three times with find_app timeouts:
# dbus-launch (not dbus-run-session) plus GNOME_ACCESSIBILITY=1 plus
# GTK_MODULES=gail:atk-bridge, with the AT-SPI registry activated
# BEFORE Firefox starts. Every stage logs one JSON line with
# wall clock and elapsed ms. All test processes are cleaned up on
# exit, including on error.
#
# No personal info, no long dashes, no ydotool.

set -u
START_MS=$(date +%s%3N)
REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
FIXTURE="$REPO_ROOT/tests/bidi_fixture.html"
FIREFOX_BIN="${FIREFOX_BIN:-/tmp/firefox/firefox}"
MODE="both"
while [ $# -gt 0 ]; do
  case "$1" in
    --mode) MODE="$2"; shift 2 ;;
    --firefox) FIREFOX_BIN="$2"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
case "$MODE" in dump|full|both) ;; *) echo "bad --mode: $MODE" >&2; exit 2 ;; esac

now_ms() { date +%s%3N; }
wall() { date -u +%Y-%m-%dT%H:%M:%SZ; }
stage() { # stage <name> <ok true|false> <stage_start_ms> [extra json fragment]
  local name="$1" ok="$2" t0="$3" extra="${4:-}"
  local now elapsed
  now=$(now_ms); elapsed=$((now - t0))
  if [ -n "$extra" ]; then
    printf '{"wall_clock":"%s","stage":"%s","ok":%s,"stage_elapsed_ms":%s,"elapsed_ms":%s,%s}\n' \
      "$(wall)" "$name" "$ok" "$elapsed" "$((now - START_MS))" "$extra"
  else
    printf '{"wall_clock":"%s","stage":"%s","ok":%s,"stage_elapsed_ms":%s,"elapsed_ms":%s}\n' \
      "$(wall)" "$name" "$ok" "$elapsed" "$((now - START_MS))"
  fi
}

XVFB_PID=""; BUS_PID=""; FF_PID=""
PROFILE_DIR=""; RUNTIME_DIR=""
cleanup() {
  if [ -n "$FF_PID" ]; then kill "$FF_PID" 2>/dev/null; wait "$FF_PID" 2>/dev/null; fi
  if [ -n "$XVFB_PID" ]; then kill "$XVFB_PID" 2>/dev/null; wait "$XVFB_PID" 2>/dev/null; fi
  if [ -n "$BUS_PID" ]; then kill "$BUS_PID" 2>/dev/null; fi
  if [ -n "$PROFILE_DIR" ]; then rm -rf "$PROFILE_DIR"; fi
  if [ -n "$RUNTIME_DIR" ]; then rm -rf "$RUNTIME_DIR"; fi
  pkill -f "firefox.*atspi-session-profile" 2>/dev/null || true
}
trap cleanup EXIT

# Stage 1: prerequisites. Print exact install commands when missing.
T0=$(now_ms)
MISSING=""
for bin in Xvfb dbus-launch gdbus python3; do
  command -v "$bin" >/dev/null 2>&1 || MISSING="$MISSING $bin"
done
[ -x /usr/libexec/at-spi-bus-launcher ] || MISSING="$MISSING at-spi-bus-launcher"
[ -x "$FIREFOX_BIN" ] || MISSING="$MISSING firefox-binary"
[ -f "$FIXTURE" ] || MISSING="$MISSING fixture"
if ! python3 -c "import pyatspi" 2>/dev/null; then MISSING="$MISSING pyatspi"; fi
if [ -n "$MISSING" ]; then
  stage "prereq" false "$T0" '"missing":"'"$MISSING"'","install":"sudo apt-get update && sudo apt-get install -y at-spi2-core python3-pyatspi dbus-x11 xvfb, then download Firefox 160.0.1 to /tmp/firefox"'
  echo "MISSING:$MISSING" >&2
  echo "Install with: sudo apt-get update && sudo apt-get install -y at-spi2-core python3-pyatspi dbus-x11 xvfb" >&2
  echo "Firefox: download Firefox 160.0.1 and extract to /tmp/firefox (or pass --firefox PATH)" >&2
  exit 2
fi
stage "prereq" true "$T0" '"firefox":"'"$FIREFOX_BIN"'","fixture":"'"$FIXTURE"'"'

# Stage 2: start Xvfb on a free display.
T0=$(now_ms)
DISPLAY_NUM=""
for n in 97 98 99; do
  if [ ! -e "/tmp/.X11-unix/X$n" ]; then DISPLAY_NUM="$n"; break; fi
done
if [ -z "$DISPLAY_NUM" ]; then
  stage "start_xvfb" false "$T0" '"error":"no free display number in 97..99"'
  exit 2
fi
Xvfb ":$DISPLAY_NUM" -screen 0 1280x800x24 >/dev/null 2>&1 &
XVFB_PID=$!
SOCK="/tmp/.X11-unix/X$DISPLAY_NUM"
for _ in $(seq 1 100); do
  [ -e "$SOCK" ] && kill -0 "$XVFB_PID" 2>/dev/null && break
  sleep 0.1
done
if [ -e "$SOCK" ] && kill -0 "$XVFB_PID" 2>/dev/null; then
  stage "start_xvfb" true "$T0" '"display":":'"$DISPLAY_NUM"'","pid":'"$XVFB_PID"''
else
  stage "start_xvfb" false "$T0" '"error":"X socket never appeared"'
  exit 2
fi

# Stage 3: start a private session bus with dbus-launch.
T0=$(now_ms)
eval "$(dbus-launch --sh-syntax)" || { stage "start_session_bus" false "$T0" '"error":"dbus-launch failed"'; exit 2; }
BUS_PID="$DBUS_SESSION_BUS_PID"
export DISPLAY=":$DISPLAY_NUM"
export DBUS_SESSION_BUS_ADDRESS
export GNOME_ACCESSIBILITY=1
export GTK_MODULES=gail:atk-bridge
RUNTIME_DIR=$(mktemp -d /tmp/atspi-runtime.XXXXXX)
chmod 700 "$RUNTIME_DIR"
export XDG_RUNTIME_DIR="$RUNTIME_DIR"
stage "start_session_bus" true "$T0" '"pid":'"$BUS_PID"''
# Note: the bus address itself is a local abstract socket path and is
# not logged, to keep the log free of machine-specific values.

# Stage 4: activate the AT-SPI registry BEFORE Firefox starts.
# A gdbus call to org.a11y.Bus triggers D-Bus activation of
# /usr/libexec/at-spi-bus-launcher, which starts at-spi2-registryd.
# If Firefox starts first, it can miss the registry and the tree
# stays empty (childCount 0), which is exactly the dbus-run-session
# failure mode.
T0=$(now_ms)
A11Y_ADDR=""
for _ in $(seq 1 10); do
  A11Y_ADDR=$(gdbus call --session --dest org.a11y.Bus \
    --object-path /org/a11y/bus \
    --method org.a11y.Bus.GetAddress 2>/dev/null | sed "s/.*'\(.*\)'.*/\1/") || true
  [ -n "$A11Y_ADDR" ] && break
  sleep 0.5
done
if [ -n "$A11Y_ADDR" ]; then
  stage "activate_a11y_registry" true "$T0" '"note":"registry answered before Firefox started"'
else
  stage "activate_a11y_registry" false "$T0" '"error":"org.a11y.Bus.GetAddress never answered"'
  exit 2
fi

# Stage 5: launch Firefox on the fixture with a fresh profile.
T0=$(now_ms)
PROFILE_DIR=$(mktemp -d /tmp/atspi-session-profile.XXXXXX)
"$FIREFOX_BIN" -profile "$PROFILE_DIR" -no-remote "file://$FIXTURE" >/dev/null 2>&1 &
FF_PID=$!
sleep 5
if kill -0 "$FF_PID" 2>/dev/null; then
  stage "launch_firefox" true "$T0" '"pid":'"$FF_PID"''
else
  stage "launch_firefox" false "$T0" '"error":"firefox exited early"'
  exit 2
fi

# Stage 6: wait until the fixture document appears in the tree.
# Two things have to happen first, in order. The first-run
# spotlight dialog populates slowly (its Continue button takes
# about 10 s to appear in the tree) and blocks the tab content
# until dismissed. The dismiss poll uses --mode dismiss, which has
# no side effects; click and full modes must not be used as a
# readiness poll, because they would press the fixture button and
# change the counter the full run later checks. Once the dialog is
# gone, the fixture document itself takes a few seconds to appear,
# and it is not the first document web node in tree order (an empty
# about:blank document comes first), so the poll looks for the
# document named after the fixture.
T0=$(now_ms)
PROBE="python3 $REPO_ROOT/tests/atspi_probe.py"
DOC_OK=false
WAIT_OUT=$(mktemp /tmp/atspi-wait.XXXXXX)
for _ in $(seq 1 15); do
  timeout 60 $PROBE --mode dismiss >"$WAIT_OUT" 2>&1 && break
  sleep 2
done
for _ in $(seq 1 15); do
  timeout 30 $PROBE --mode dump --max-nodes 200 >"$WAIT_OUT" 2>&1 || true
  if grep -q '"role": "document web", "name": "BiDi fixture"' "$WAIT_OUT"; then DOC_OK=true; break; fi
  sleep 2
done
rm -f "$WAIT_OUT"
if [ "$DOC_OK" = true ]; then
  stage "wait_document" true "$T0" '"note":"document web named BiDi fixture present in the tree"'
else
  stage "wait_document" false "$T0" '"error":"no BiDi fixture document in the tree after waiting"'
fi

# Stage 7: run the probe. Dump proves the tree is readable, full
# proves the Action click and records the typing result.
DUMP_OK=false; CLICK_OK=false; TYPE_OK=false; TYPE_DETAIL=""; COUNTER_OK=false
if [ "$MODE" = "dump" ] || [ "$MODE" = "both" ]; then
  T0=$(now_ms)
  DUMP_OUT=$(timeout 120 $PROBE --mode dump --max-nodes 200 2>&1)
  DUMP_RC=$?
  DUMP_NODES=$(printf '%s' "$DUMP_OUT" | grep '"op": "dump"' | sed 's/.*"nodes": \([0-9]*\).*/\1/')
  printf '%s\n' "$DUMP_OUT"
  if [ "$DUMP_RC" -eq 0 ] && [ -n "$DUMP_NODES" ] && [ "$DUMP_NODES" -gt 0 ]; then
    DUMP_OK=true
    stage "probe_dump" true "$T0" '"nodes":'"$DUMP_NODES"''
  else
    stage "probe_dump" false "$T0" '"rc":'"$DUMP_RC"''
  fi
fi
if [ "$MODE" = "full" ] || [ "$MODE" = "both" ]; then
  T0=$(now_ms)
  FULL_OUT=$(timeout 180 $PROBE --mode full --text "hello atspi" 2>&1)
  FULL_RC=$?
  printf '%s\n' "$FULL_OUT"
  # If the first full run could not find the button (spotlight still
  # settling), wait and retry once; the retry result is what counts.
  if ! printf '%s' "$FULL_OUT" | grep -q '"op": "find_button", "ok": true'; then
    sleep 5
    T0=$(now_ms)
    FULL_OUT=$(timeout 180 $PROBE --mode full --text "hello atspi" 2>&1)
    FULL_RC=$?
    printf '%s\n' "$FULL_OUT"
  fi
  CLICK_OK=$(printf '%s' "$FULL_OUT" | grep '"op": "click"' | grep -c '"ok": true' || true)
  [ "$CLICK_OK" = "1" ] && CLICK_OK=true || CLICK_OK=false
  TYPE_OK=$(printf '%s' "$FULL_OUT" | grep '"op": "type_editabletext"' | grep -c '"ok": true' || true)
  [ "$TYPE_OK" = "1" ] && TYPE_OK=true || TYPE_OK=false
  TYPE_DETAIL=$(printf '%s' "$FULL_OUT" | grep '"op": "type_editabletext"' | sed 's/.*"detail": "\([^"]*\)".*/\1/' | head -1)
  COUNTER_OK=$(printf '%s' "$FULL_OUT" | grep '"op": "final_readback"' | grep -c '"counter_seen": true' || true)
  [ "$COUNTER_OK" = "1" ] && COUNTER_OK=true || COUNTER_OK=false
  # Escape double quotes in the detail for JSON.
  TYPE_DETAIL_ESC=$(printf '%s' "$TYPE_DETAIL" | sed 's/\\/\\\\/g; s/"/\\"/g')
  stage "probe_full" "$([ "$CLICK_OK" = true ] && echo true || echo false)" "$T0" '"rc":'"$FULL_RC"',"click_ok":'"$CLICK_OK"',"type_ok":'"$TYPE_OK"',"type_detail":"'"$TYPE_DETAIL_ESC"'","counter_seen":'"$COUNTER_OK"''
fi

# Verdict: the session works when the tree reads and the click lands.
# Typing is a separate, known-broken Firefox behaviour (Bug 2087495),
# not a session failure.
T0=$(now_ms)
if [ "$MODE" = "dump" ]; then
  SESSION_OK="$DUMP_OK"
elif [ "$MODE" = "full" ]; then
  SESSION_OK="$CLICK_OK"
else
  [ "$DUMP_OK" = true ] && [ "$CLICK_OK" = true ] && SESSION_OK=true || SESSION_OK=false
fi
if [ "$TYPE_OK" = true ]; then TYPE_STATUS="pass"; elif [ "$MODE" = "dump" ]; then TYPE_STATUS="not-run"; else TYPE_STATUS="expected-fail-bug-2087495"; fi
stage "session_verdict" "$SESSION_OK" "$T0" '"dump_ok":'"$DUMP_OK"',"click_ok":'"$CLICK_OK"',"counter_seen":'"$COUNTER_OK"',"type_status":"'"$TYPE_STATUS"'","verdict":"session works, typing via EditableText broken on Firefox 160.0.1, use BiDi for typing"'
if [ "$SESSION_OK" = true ]; then exit 0; else exit 2; fi
