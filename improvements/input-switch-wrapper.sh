#!/bin/sh
# omarchy-input-method-switch: Super I replacement (council decision 21/11/2026).
# Bypasses the Quickshell stdin queue that silently lost switches on dbus
# stalls, and switches fcitx5 directly by EXPLICIT TARGET (-s), never by
# toggle (-t). -t toggles Active/Inactive and can undo a switch that already
# landed; -s <target> is idempotent, so a redundant re-apply is a no-op.
# Usage: omarchy-input-method-switch next|back
#   With the 2-method group [keyboard-us, ngosen], next and back are the same
#   toggle to the other method. Bound from ~/.config/hypr/bindings.lua
#   (user config, survives Omarchy updates). See
#   improvements/worker-v-council-decision-20261121.md.
set -u

CACHE="$HOME/.cache/agent-computer-use"
LOCK="$CACHE/input-switch.lock"
LOG="$CACHE/input-switch.log"
MARKER="$CACHE/input-switch-last"
mkdir -p "$CACHE"

# Serialize presses: a duplicate press while one switch is in flight is
# dropped, never queued. Without this, mashing Super I during a stall
# leaves the final method to press-count parity.
exec 9>"$LOCK"
if ! flock -n 9; then
  exit 0
fi

log() { printf '%s %s\n' "$(date '+%F %T %z')" "$*" >> "$LOG"; }
now_ms() { date +%s%3N; }

direction="${1:-next}"
start=$(now_ms)

# Read current method. Every call has a timeout: during the exact stall
# this fix is meant to survive, fcitx5-remote can hang, and an unguarded
# call would block past the whole budget.
current=$(timeout 0.2 fcitx5-remote -n 2>/dev/null)
if [ -z "$current" ]; then
  # Cannot read state. Do NOT guess a target. Queue the switch through the
  # old path instead: indicator.py (Fix 2a) retains pending for 30s and
  # applies it when the stall clears.
  OMARCHY_PATH=/usr/share/omarchy timeout 2 omarchy-input-method cycle >/dev/null 2>&1
  log "read-failed direction=$direction queued-cycle"
  [ -x /usr/bin/notify-send ] && notify-send -a "Input method" -u normal -t 1500 "Switch queued, will land shortly"
  exit 0
fi

case "$current" in
  ngosen) target="keyboard-us" ;;
  *) target="ngosen" ;;
esac

if ! timeout 1 fcitx5-remote -s "$target" 2>/dev/null; then
  log "set-failed current=$current target=$target direction=$direction"
  exit 0
fi

# Verify the switch landed, up to 1s. The poll reads the same stalled bus,
# so a "not changed" reading does not prove the switch is lost; that is why
# the fallback below re-applies the SAME explicit target (harmless if the
# first call already landed) instead of toggling.
deadline=$((start + 1000))
landed=0
while [ "$(now_ms)" -lt "$deadline" ]; do
  seen=$(timeout 0.2 fcitx5-remote -n 2>/dev/null)
  if [ "$seen" = "$target" ]; then landed=1; break; fi
  sleep 0.1
done
if [ "$landed" -eq 0 ]; then
  timeout 1 fcitx5-remote -s "$target" 2>/dev/null
  sleep 0.2
  seen=$(timeout 0.2 fcitx5-remote -n 2>/dev/null)
  [ "$seen" = "$target" ] && landed=1
fi

elapsed=$(( $(now_ms) - start ))
date +%s > "$MARKER"
log "switch current=$current target=$target direction=$direction landed=$landed ms=$elapsed"
if [ "$landed" -eq 1 ]; then
  [ -x /usr/bin/notify-send ] && notify-send -a "Input method" -u low -t 1200 "$target"
else
  [ -x /usr/bin/notify-send ] && notify-send -a "Input method" -u normal -t 2000 "Switch to $target not confirmed, press Super I again"
fi
exit 0
