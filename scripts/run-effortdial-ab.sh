#!/usr/bin/env bash
# Effort-dial A/B runner (Track 2, M1). Baseline arm vs dial arm on P1-P4.
#
# Baseline: one long `codex exec` at max effort with the Pick 2 baseline
# brief (v3 optimized discipline, no dial). Dial: the resume-per-turn
# driver (scripts/effort_dial_driver.py) with the dial brief + plan.
#
# Broker is SINGLE-OWNER. This script checks the broker is idle first
# and refuses to start when busy. It also refuses a dirty /tmp
# (P3/P4 end states already present). Run ONE arm at a time; the
# coordinator cleans /tmp between arms.
#
# Usage:
#   run-effortdial-ab.sh [--arm baseline|dial] [--run-root DIR]
#                        [--repo DIR] [--timed-py FILE]
# Defaults: arm=dial, run-root=/tmp/effortdial-runs, repo=this checkout.
# timed.py is looked up in: --timed-py, $RUN_DIR/timed.py (already
# copied by the coordinator), $REPO/improvements/timed.py. If missing,
# the script stops with BLOCKED-no-timed-py.
#
# MEASUREMENT VERDICT (2026-11-19): the dial arm is REFUSED while
# improvements/effort-dial-validation.md says the dial does not work.
# Resume-per-turn -c is accepted but does not move reasoning tokens,
# so the dial arm would measure a no-op. Set EFFORTDIAL_FORCE_DIAL=1
# to run it anyway (only after a working per-step mechanism is proven).
# No em dash or en dash in this file.
set -u
REPO="$(cd "$(dirname "$0")/.." && pwd)"
ARM="dial"
RUN_ROOT="/tmp/effortdial-runs"
TIMED_PY=""

while [ $# -gt 0 ]; do
  case "$1" in
    --arm) ARM="$2"; shift 2 ;;
    --run-root) RUN_ROOT="$2"; shift 2 ;;
    --repo) REPO="$2"; shift 2 ;;
    --timed-py) TIMED_PY="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

case "$ARM" in
  baseline|dial) ;;
  *) echo "arm must be baseline or dial" >&2; exit 2 ;;
esac

RUN_DIR="$RUN_ROOT/$ARM-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$RUN_DIR" || exit 1
echo "run dir: $RUN_DIR"

# --- gates: broker idle, /tmp clean -------------------------------------
echo "== broker idle check =="
if ! python3 "$REPO/scripts/session_remote.py" status >"$RUN_DIR/broker-status.txt" 2>&1; then
  echo "BLOCKED-busy: session_remote.py status failed (see broker-status.txt)" >&2
  exit 3
fi
# The broker daemon itself always reports "broker": "running". What
# matters is the task state: finished/failed means idle, anything else
# (starting, running, cleaning) or a live sequence means busy.
if ! python3 -c "
import json, sys
status = json.load(open('$RUN_DIR/broker-status.txt'))
state = status.get('state')
busy = state not in ('finished', 'failed') or status.get('active_sequence') is not None
sys.exit(0 if not busy else 1)
"; then
  echo "BLOCKED-busy: broker state is not finished/failed (see broker-status.txt):" >&2
  cat "$RUN_DIR/broker-status.txt" >&2
  exit 3
fi
echo "broker idle (status output in broker-status.txt)"

echo "== dirt check =="
DIRTY=""
[ -e /tmp/hoc-ky-2 ] && DIRTY="$DIRTY /tmp/hoc-ky-2"
[ -e /tmp/y-tuong.txt ] && DIRTY="$DIRTY /tmp/y-tuong.txt"
[ -e /tmp/lon-nhat.txt ] && DIRTY="$DIRTY /tmp/lon-nhat.txt"
if [ -n "$DIRTY" ]; then
  echo "BLOCKED-dirty: end states already present:$DIRTY (coordinator cleans between arms)" >&2
  exit 3
fi
echo "clean"

# --- timed.py ------------------------------------------------------------
if [ -z "$TIMED_PY" ]; then
  for cand in "$RUN_DIR/timed.py" "$REPO/improvements/timed.py"; do
    if [ -f "$cand" ]; then TIMED_PY="$cand"; break; fi
  done
fi
if [ -z "$TIMED_PY" ] || [ ! -f "$TIMED_PY" ]; then
  echo "BLOCKED-no-timed-py: pass --timed-py or copy timed.py into $RUN_DIR" >&2
  exit 3
fi
cp "$TIMED_PY" "$RUN_DIR/timed.py"
chmod 600 "$RUN_DIR/timed.py"
echo "timed.py: $TIMED_PY"

# --- arms ---------------------------------------------------------------
if [ "$ARM" = "baseline" ]; then
  BRIEF_SRC="$REPO/improvements/pick2-executor-brief.md"
  BRIEF="$RUN_DIR/brief-baseline.md"
  sed -e "s|__RUN_DIR__|$RUN_DIR|g" -e "s|__ARM__|effortdial-baseline|g" "$BRIEF_SRC" >"$BRIEF"
  echo "== baseline arm: single codex exec, max effort =="
  echo "start: $(date '+%F %T %Z')"
  /usr/bin/time -v codex exec --sandbox danger-full-access -m gpt-6-luna \
    -c model_reasoning_effort=\"max\" - <"$BRIEF" >"$RUN_DIR/executor.log" 2>"$RUN_DIR/executor.time"
  echo "exit: $?"
  echo "end: $(date '+%F %T %Z')"
  echo "log: $RUN_DIR/executor.log"
  exit 0
fi

echo "== dial arm: resume-per-turn driver =="
if [ "${EFFORTDIAL_FORCE_DIAL:-}" != "1" ] && grep -q 'VERDICT: DIAL NOT WORKING' "$REPO/improvements/effort-dial-validation.md" 2>/dev/null; then
  echo "BLOCKED-dial-unproven: effort-dial-validation.md verdict is DIAL NOT WORKING." >&2
  echo "The dial arm would run every turn at the bootstrap effort and measure a no-op." >&2
  echo "Set EFFORTDIAL_FORCE_DIAL=1 only after a working per-step mechanism is proven." >&2
  exit 3
fi
echo "start: $(date '+%F %T %Z')"
python3 "$REPO/scripts/effort_dial_driver.py" \
  --run-dir "$RUN_DIR" \
  --brief "$REPO/scripts/effort_dial_brief.md" \
  --plan "$REPO/improvements/effort-dial-plan-p1p4.json" \
  --repo "$REPO" --arm effortdial-dial
RC=$?
echo "exit: $RC"
echo "end: $(date '+%F %T %Z')"
echo "summary: $RUN_DIR/summary.md"
exit "$RC"
