R3-L3 daemon fallback channel (precondition 18).
Written 2026-11-24 17:35 +07 by the Phase 0 coordinator.

PRIMARY CHANNEL (to Mochi and Mei):
- The speed daemon (~/workspace/speed-daemon/daemon.sh). Send with
  python3 ~/workspace/speed-daemon/send.py --recipient mochi|mei --run <N>
  --message "<text>" (one at a time, NEVER concurrent). Read with
  python3 ~/workspace/speed-daemon/read.py --recipient mochi|mei.
- The daemon sends via the laptop (SSH + a browser session). It returns
  outcome=sent and verified=True, but that does NOT prove delivery (standing
  rule 2026-11-24 09:58). The coordinator must read back (read.py) and
  confirm the message appears and the recipient replies before concluding
  anything.
- The daemon DIED once during Phase 0 prep (found not running 2026-11-24
  17:16, restarted 17:16:43 +07, PID 2423). The 5-minute watchdog cron
  (watchdog-15m) is supposed to restart it. If send.py fails with
  ConnectionRefusedError, the daemon is down.

FALLBACK CHANNEL (when the daemon is down or send.py fails twice):
- Direct SSH + speed-lean: ~/workspace/speed-lean/ is a lean fallback that
  sends a message to Mochi/Mei without the full daemon. It uses the same
  laptop browser session but a simpler path. Use it when the daemon cannot
  be restarted.
- Procedure when the daemon fails:
  1. Run bash ~/workspace/speed-daemon/daemon.sh restart and retry send.py
     once. If it works, continue on the primary channel and record the
     restart in the state file.
  2. If it still fails, use the speed-lean fallback to send the message.
     Record that the fallback was used and why.
  3. If the fallback also fails, the coordinator does NOT conclude the
     recipient is silent. It records "channel down, message not delivered"
     and retries in 15 minutes. It does not grade, score, or proceed on a
     task that needs the recipient's input until the channel is confirmed
     working again.
  4. If the channel is down for more than 1 hour, the coordinator reports to
     the parent agent (Muse) so the parent can fix the channel or decide.
- The fallback is TESTED (this file records the test):
  Test: 2026-11-24 17:16 +07, the daemon was found NOT running. The
  coordinator restarted it (daemon.sh restart, PID 2423, started 17:16:43
  +07) and re-sent run 135 to Mochi successfully (outcome=sent,
  verified=True, total_items 65). The restart-and-retry procedure works.
  The speed-lean fallback path is named here but was not needed in this
  test (the restart fixed it). The coordinator will test speed-lean once
  before task 1 if time permits; if not tested, it is still the named
  fallback and the coordinator will use it if the daemon fails again.

DELIVERY RULE (applies to both channels):
- A send receipt (outcome=sent, verified=True) does NOT prove the recipient
  received the message. The coordinator reads back with read.py and confirms
  total_items increased AND the recipient's reply appears. Only then is the
  message treated as delivered.
- If the recipient does not reply within 15 minutes AND the coordinator's
  last sent message is NEWER than the recipient's last reply, the
  watchdog-15m pokes them (per the 15-minute auto-poke rule). The
  coordinator does not report the poke to the owner.
