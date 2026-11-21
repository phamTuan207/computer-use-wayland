#!/bin/sh
# input-stall-monitor: logging-only input-path monitor (council 21/11/2026).
# Catches the next stall with exact timestamps and per-component timings so
# the trigger can be identified with evidence (Worker T open item 4).
# Design (Council B + redteam): the -n read half runs every 30s (cheap,
# non-invasive); the cycle round-trip half runs every 2 min (the only half
# sensitive to this stall signature, since -n reads kept succeeding through
# the 16:42-16:45 stall). The two halves are timed and logged SEPARATELY.
# The cycle probe is skipped if the user pressed Super I in the last 10s
# (marker file written by omarchy-input-method-switch) so the probe never
# interleaves with a real press. A cycle-infra failure (reader dead, env
# missing) is logged distinctly and is NEVER treated as a stall.
# Run as a systemd user service (long-running loop, not a timer: a timer
# with AccuracySec=30s would make a 30s cadence imprecise by design).
# STOP RULE: 7 days, or 2 stalls captured, whichever comes first. Then
# correlate with journalctl (fcitx5, Hyprland, Chromium scopes, xkbcomp,
# Marionette sessions) before any restart logic is armed.
# Log: ~/.cache/agent-computer-use/input-monitor.log (JSONL, one line/probe).
set -u

CACHE="$HOME/.cache/agent-computer-use"
LOG="$CACHE/input-monitor.log"
MARKER="$CACHE/input-switch-last"
LOCK="$CACHE/input-monitor.lock"
mkdir -p "$CACHE"
export OMARCHY_PATH=/usr/share/omarchy

exec 9>"$LOCK"
if ! flock -n 9; then
  echo "input-stall-monitor: already running" >&2
  exit 1
fi

# Discover the Hyprland instance signature for hyprctl (same method as agy-hypr).
SIG=$(ls /run/user/1000/hypr/ 2>/dev/null | head -1)
if [ -n "$SIG" ]; then
  export HYPRLAND_INSTANCE_SIGNATURE="$SIG"
  export XDG_RUNTIME_DIR=/run/user/1000
  export WAYLAND_DISPLAY=wayland-1
fi

now_ms() { date +%s%3N; }
ts() { date '+%Y-%m-%dT%H:%M:%S%z'; }
loadavg() { cut -d' ' -f1-3 /proc/loadavg; }
alive() { [ -n "$(pgrep -x "$1" 2>/dev/null | head -1)" ] && echo 1 || echo 0; }
indicator_alive() { [ -n "$(pgrep -f "input-methods/indicator.py" 2>/dev/null | head -1)" ] && echo 1 || echo 0; }

read_half() {
  start=$(now_ms)
  im=$(timeout 2 fcitx5-remote -n 2>/dev/null)
  rc=$?
  ms=$(( $(now_ms) - start ))
  printf '{"t":"%s","half":"read","ms":%s,"rc":%s,"im":"%s","load":"%s","fcitx5":%s,"indicator":%s}\n' \
    "$(ts)" "$ms" "$rc" "$im" "$(loadavg)" "$(alive fcitx5)" "$(indicator_alive)" >> "$LOG"
}

cycle_half() {
  # Skip if the user pressed Super I recently: never interleave with a real press.
  if [ -f "$MARKER" ]; then
    age=$(( $(date +%s) - $(cat "$MARKER" 2>/dev/null || echo 0) ))
    if [ "$age" -lt 10 ]; then
      printf '{"t":"%s","half":"cycle","skipped":"user-pressed-super-i-%ss-ago"}\n' "$(ts)" "$age" >> "$LOG"
      return
    fi
  fi
  before=$(timeout 2 fcitx5-remote -n 2>/dev/null)
  start=$(now_ms)
  out=$(timeout 5 omarchy-input-method cycle 2>&1)
  rc=$?
  if [ $rc -ne 0 ]; then
    printf '{"t":"%s","half":"cycle","infra_failed":1,"rc":%s,"out":"%s","im_before":"%s"}\n' \
      "$(ts)" "$rc" "$(echo "$out" | head -c 120)" "$before" >> "$LOG"
    return
  fi
  # Wait up to 2s for the flip to land.
  landed=0
  deadline=$((start + 2000))
  while [ "$(now_ms)" -lt "$deadline" ]; do
    seen=$(timeout 0.5 fcitx5-remote -n 2>/dev/null)
    if [ -n "$seen" ] && [ "$seen" != "$before" ]; then landed=1; break; fi
    sleep 0.1
  done
  flip_ms=$(( $(now_ms) - start ))
  # Cycle back to restore the user's method.
  timeout 5 omarchy-input-method cycle >/dev/null 2>&1
  sleep 1
  after=$(timeout 2 fcitx5-remote -n 2>/dev/null)
  printf '{"t":"%s","half":"cycle","flip_ms":%s,"landed":%s,"im_before":"%s","im_after":"%s","load":"%s"}\n' \
    "$(ts)" "$flip_ms" "$landed" "$before" "$after" "$(loadavg)" >> "$LOG"
}

n=0
while true; do
  read_half
  n=$((n + 1))
  if [ $((n % 4)) -eq 0 ]; then
    cycle_half
  fi
  sleep 30
done
