#!/bin/bash
# Dry run of worker-y8-stop-infra.sh kill path with dummy processes ONLY.
# No real infra, no Zen driving, no geckodriver on real ports.
# Phase 1: correct pidfiles (happy path). Phase 2: driver pidfile points at
# a decoy with a non-matching cmdline (guard path).
# Expected: phase 1 kills holder/driver/http/gd-4451, spares gd-4448.
# Phase 2 spares the decoy (guard), kills the driver dummy via leftover scan.
set -u
D=/tmp/e1dry
mkdir -p $D
cp /usr/bin/python3 $D/geckodriver 2>/dev/null || cp "$(command -v python3)" $D/geckodriver
rm -f /tmp/e1/holder.pid /tmp/e1/driver.pid /tmp/e1/http.pid
: > $D/cleanup-pids.txt

setup_dummies() {
  rm -f $D/fifo; mkfifo $D/fifo
  # Reader first, or the holder's FIFO open blocks forever.
  ( exec 8<$D/fifo; sleep 300 ) &
  echo $! >> $D/cleanup-pids.txt
  setsid bash -c 'exec 9>'"$D"'/fifo; exec -a e1-fifo-holder sleep 7200' &
  echo $! > /tmp/e1/holder.pid
  setsid bash -c 'exec -a "hand_drive_e1.py dummy" sleep 300' &
  echo $! > /tmp/e1/driver.pid
  setsid bash -c 'exec -a "http.server 8767 dummy" sleep 300' &
  echo $! > /tmp/e1/http.pid
  $D/geckodriver -c "import time; time.sleep(300)" --port 4451 &
  GD1=$!
  $D/geckodriver -c "import time; time.sleep(300)" --port 4448 &
  GD2=$!
  echo "$GD2" >> $D/cleanup-pids.txt
  sleep 1
}
check() { # $1 = label, $2 = pid, $3 = expected ALIVE|DEAD
  if kill -0 "$2" 2>/dev/null; then got=ALIVE; else got=DEAD; fi
  if [ "$got" = "$3" ]; then echo "PASS $1: $got (expected $3)"; else echo "FAIL $1: $got (expected $3)"; fi
}

echo "=== PHASE 1: happy path ==="
setup_dummies
H1=$(cat /tmp/e1/holder.pid); D1=$(cat /tmp/e1/driver.pid); H2=$(cat /tmp/e1/http.pid)
bash /tmp/e1/worker-y8-stop-infra.sh > $D/phase1.out 2>&1
check "holder killed" $H1 DEAD
check "driver killed" $D1 DEAD
check "http killed" $H2 DEAD
check "gd-4451 killed" $GD1 DEAD
check "gd-4448 SPARED" $GD2 ALIVE

echo "=== PHASE 2: guard path (driver pidfile points at decoy) ==="
setup_dummies
H1=$(cat /tmp/e1/holder.pid); D1=$(cat /tmp/e1/driver.pid); H2=$(cat /tmp/e1/http.pid)
sleep 300 &
DECOY=$!
echo $DECOY > /tmp/e1/driver.pid
echo "$DECOY" >> $D/cleanup-pids.txt
bash /tmp/e1/worker-y8-stop-infra.sh > $D/phase2.out 2>&1
check "holder killed" $H1 DEAD
check "decoy SPARED (guard)" $DECOY ALIVE
check "driver dummy killed via leftover scan" $D1 DEAD
check "http killed" $H2 DEAD
check "gd-4451 killed" $GD1 DEAD
check "gd-4448 SPARED" $GD2 ALIVE

echo "=== CLEANUP ==="
while read -r p; do kill -TERM "$p" 2>/dev/null; done < $D/cleanup-pids.txt
rm -f /tmp/e1/holder.pid /tmp/e1/driver.pid /tmp/e1/http.pid
sleep 1
pgrep -x geckodriver >/dev/null 2>&1 && echo "WARNING: a geckodriver still alive" || echo "no geckodriver left"
rm -rf $D
echo DRYRUN_DONE
