#!/bin/bash
# R10 Stage 1 flag/pref matrix. Throwaway headless profiles ONLY.
# Never touches the live Zen (different profile, different ports,
# --no-remote). Kill step verifies the cmdline carries the throwaway
# profile path before killing anything.
# ydotool is banned. Restate the ban in every brief. Never assume it.
set -u
WORK=/tmp/r10-stage1
ZEN=/opt/zen-browser-bin/zen-bin
GECKO=$HOME/.local/bin/geckodriver
BIDI_PORT=9333
MAR_PORT=2838
GECKO_PORT=4445
LOG=$WORK/results.log
mkdir -p "$WORK"
: > "$LOG"

ts() { TZ=Asia/Ho_Chi_Minh date '+%Y-%m-%dT%H:%M:%S+07:00'; }
say() { echo "[$(ts)] $*" | tee -a "$LOG"; }

wait_port() {
  local port=$1 tries=0
  while [ $tries -lt 60 ]; do
    if ss -ltn 2>/dev/null | grep -q ":$port "; then return 0; fi
    sleep 0.5; tries=$((tries+1))
  done
  return 1
}

# start_instance <name> <prefs-lines-or-empty> <zen args...>
start_instance() {
  local name=$1 prefs=$2; shift 2
  local profile=$WORK/profile-$name
  rm -rf "$profile"; mkdir -p "$profile"
  if [ -n "$prefs" ]; then printf '%s\n' "$prefs" > "$profile/prefs.js"; fi
  setsid nohup "$ZEN" --headless --no-remote --profile "$profile" "$@" about:blank \
    > "$WORK/$name.out" 2>&1 < /dev/null &
  echo $! > "$WORK/$name.pid"
  say "started $name pid=$(cat "$WORK/$name.pid") args: $* prefs: ${prefs:-none}"
}

stop_instance() {
  local name=$1
  local profile=$WORK/profile-$name
  local pid
  pid=$(cat "$WORK/$name.pid" 2>/dev/null || true)
  if [ -n "${pid:-}" ] && [ -r "/proc/$pid/cmdline" ]; then
    if tr '\0' ' ' < "/proc/$pid/cmdline" | grep -q "$profile"; then
      kill "$pid" 2>/dev/null
      local tries=0
      while [ -d "/proc/$pid" ] && [ $tries -lt 20 ]; do sleep 0.5; tries=$((tries+1)); done
      [ -d "/proc/$pid" ] && kill -9 "$pid" 2>/dev/null
      say "stopped $name pid=$pid"
    else
      say "REFUSED to kill pid=$pid for $name: cmdline lacks throwaway profile"
    fi
  fi
  rm -rf "$profile"
}

start_gecko() {
  setsid nohup "$GECKO" --port $GECKO_PORT --connect-existing --marionette-port $MAR_PORT \
    > "$WORK/gecko.out" 2>&1 < /dev/null &
  echo $! > "$WORK/gecko.pid"
  wait_port $GECKO_PORT && say "geckodriver up pid=$(cat "$WORK/gecko.pid")" || say "geckodriver FAILED to listen on $GECKO_PORT"
}
stop_gecko() {
  local pid; pid=$(cat "$WORK/gecko.pid" 2>/dev/null || true)
  [ -n "${pid:-}" ] && kill "$pid" 2>/dev/null
  rm -f "$WORK/gecko.pid"
}

probe_bidi() { say "probe bidi ($1):"; node "$WORK/webdriver-probe.mjs" --transport bidi --port $BIDI_PORT --mode probe 2>&1 | tee -a "$LOG"; }
probe_wd()   { say "probe webdriver ($1):"; node "$WORK/webdriver-probe.mjs" --transport webdriver --port $GECKO_PORT --mode probe 2>&1 | tee -a "$LOG"; }

say "=== R10 Stage 1 matrix start ==="

# T2: BiDi only
say "--- T2 bidi-only (--remote-debugging-port=$BIDI_PORT) ---"
start_instance t2 "" --remote-debugging-port=$BIDI_PORT
if wait_port $BIDI_PORT; then probe_bidi t2; else say "T2: BiDi port never listened"; tail -5 "$WORK/t2.out" | tee -a "$LOG"; fi
ss -ltn | grep -q ":$MAR_PORT " && say "T2: marionette port $MAR_PORT LISTENING (unexpected)" || say "T2: marionette port $MAR_PORT not listening (expected)"
stop_instance t2

# T3: Marionette only
say "--- T3 marionette-only (--marionette, pref marionette.port=$MAR_PORT) ---"
start_instance t3 "user_pref(\"marionette.port\", $MAR_PORT);" --marionette
if wait_port $MAR_PORT; then start_gecko; probe_wd t3; stop_gecko; else say "T3: marionette port never listened"; tail -5 "$WORK/t3.out" | tee -a "$LOG"; fi
ss -ltn | grep -q ":$BIDI_PORT " && say "T3: BiDi port $BIDI_PORT LISTENING (unexpected)" || say "T3: BiDi port $BIDI_PORT not listening (expected)"
stop_instance t3

# T4: both (live-config replica on spare ports)
say "--- T4 both flags (live replica) ---"
start_instance t4 "user_pref(\"marionette.port\", $MAR_PORT);" --remote-debugging-port=$BIDI_PORT --marionette
wait_port $BIDI_PORT && probe_bidi t4 || say "T4: BiDi port never listened"
if wait_port $MAR_PORT; then start_gecko; probe_wd t4; stop_gecko; else say "T4: marionette port never listened"; fi
stop_instance t4

# T5: both + dom.webdriver.enabled=false
say "--- T5 both flags + dom.webdriver.enabled=false ---"
start_instance t5 "user_pref(\"marionette.port\", $MAR_PORT);
user_pref(\"dom.webdriver.enabled\", false);" --remote-debugging-port=$BIDI_PORT --marionette
wait_port $BIDI_PORT && probe_bidi t5 || say "T5: BiDi port never listened"
if wait_port $MAR_PORT; then start_gecko; probe_wd t5; stop_gecko; else say "T5: marionette port never listened"; fi
stop_instance t5

# T6: BiDi only + dom.webdriver.enabled=false
say "--- T6 bidi-only + dom.webdriver.enabled=false ---"
start_instance t6 "user_pref(\"dom.webdriver.enabled\", false);" --remote-debugging-port=$BIDI_PORT
wait_port $BIDI_PORT && probe_bidi t6 || say "T6: BiDi port never listened"
stop_instance t6

# T7: shim disagreement reproduction (both flags)
say "--- T7 shim disagreement (both flags, shimtest mode) ---"
start_instance t7 "user_pref(\"marionette.port\", $MAR_PORT);" --remote-debugging-port=$BIDI_PORT --marionette
if wait_port $BIDI_PORT; then
  node "$WORK/webdriver-probe.mjs" --transport bidi --port $BIDI_PORT --mode shimtest 2>&1 | tee -a "$LOG"
else say "T7: BiDi port never listened"; fi
stop_instance t7

say "=== R10 Stage 1 matrix done ==="
say "leftover check:"; ps -eo pid,args | grep "r10-stage1/profile" | grep -v grep | tee -a "$LOG" || true
say "MATRIX-COMPLETE"
