# Council Member B verdict: Fix 3 (input watchdog) and Fix 5 (stall monitor)
# Worker V, 21/11/2026. All times wall-clock Asia/Ho_Chi_Minh.
# Scope: ONLY Fix 3 and Fix 5 from Worker T's diagnosis (commit 029cb9b).
# Fix 1 is already applied and was not revisited.
# Rules followed: full access, no fabrication, no em dash or en dash,
# never ydotool, nothing edited/restarted/killed on the laptop.

## Evidence collected live (laptop user, 192.0.2.1, via ssh-laptop.sh)

### E1. Existing timers and cron, 17:24:25
- `crontab` is NOT installed on the laptop (command not found).
- `systemctl --user list-timers` shows exactly ONE user timer:
  opencode-telegram-watchdog.timer, OnUnitActiveSec=4min, AccuracySec=30s.
- No existing input-method probe, watchdog, or stall monitor exists.
- `~/.local/bin` has no fcitx/input/stall/probe script (only
  opencode-telegram-watchdog.sh and unrelated watchdog/pulumi-watch).
- Precedent exists for a systemd user timer running a watchdog script, but
  note its AccuracySec=30s: a 30s probe interval under a timer with 30s
  accuracy is imprecise by design. A 30s probe wants AccuracySec=1s or a
  long-running daemon with its own sleep loop instead of a timer.

### E2. fcitx5 healthy baseline, 17:24:25 and 17:26:13
- omarchy-fcitx5.service active running since 15:17:30, PID 1828, no restart.
- `fcitx5-remote -n` = ngosen, timed at 2ms; 10 samples 17:25:xx:
  1.3-1.9ms, rc 0 every time. Healthy read latency is ~2ms, rock stable.
- fcitx5 journal since 15:17:30: ZERO lines matching error/fail/critical.
  The daemon is clean and has not crashed or been restarted all session.
- Load average 1.39 at 17:24:39 (was 1.78 at 16:49 per T). System is loaded
  but not thrashing.

### E3. fcitx5 restart time, from the 15:17:30 boot journal
- 15:17:30 systemd "Starting..."; 15:17:30.369 "Starting fcitx5 5.1.23";
  15:17:30.500 dbus addon loaded; 15:17:30.491-30.574 all addons loaded;
  systemd "Started" in the same second.
- Daemon start-to-dbus-ready is UNDER 1s (about 0.5s to the dbus addon).
  A `systemctl --user restart` therefore costs roughly 1-3s of no input
  (stop + start), not the ~1s T estimated, but the same order.
- The unit is Type=dbus with Restart=always, RestartSec=2. systemd ALREADY
  restarts fcitx5 2s after any crash. A watchdog fcitx5 restart only adds
  value for the hung-but-alive case, which has been seen exactly once and
  whose trigger is still unknown.
- User manager environment HAS both vars a timer probe needs:
  WAYLAND_DISPLAY=wayland-1 and OMARCHY_PATH=/usr/share/omarchy.

### E4. indicator.py source, read 17:24-17:25 (read-only)
- `call()` uses a 1000ms dbus timeout (line 17-20).
- `refresh()` in `watch()`: on ANY GLib.Error it sets
  `indicator.pending = ""` AND `indicator.last = ""`, then keeps polling.
  T's claim is confirmed in source: one >1000ms dbus hiccup silently eats
  the user's Super I press. Same in `command()`: any exception in
  select_next clears pending.
- `pending` and `last` are in-memory attributes only. Killing indicator.py
  destroys them. A fresh instance re-snapshots the current IM from fcitx5.
- Poll cadence: 50ms while pending, 500ms while switchable, 2000ms after
  a failed read. The "50ms pending poll" is real.

### E5. Quickshell restart behavior, InputMethodState.qml, read 17:25
- Process `running: true`; `onExited: { root.state = ({}); restart.restart() }`;
  Timer interval 5000. The 5s auto-restart claim is confirmed in source.
- `cycle(back)`: `if (!watcher.running) return false`. While the reader is
  dead or restarting, cycle fails, and `omarchy-input-method cycle` exits 1
  with "The shell's input reader is not running" (script source read).
- Consequence: for 5s after ANY indicator kill, the probe's own cycle
  fails with exit 1. A watchdog that reads that as "still stalled" and
  escalates to an fcitx5 restart is misreading its own damage.

### E6. What a restart does to state (architecture + profile, not a live test)
- No restart was performed (forbidden by the brief). The following is
  grounded in the files, not a live restart:
- The profile `~/.config/fcitx5/profile` contains NO current-IM field,
  only DefaultIM=ngosen. On a fresh start fcitx5 starts at DefaultIM.
  MEDIUM CONFIDENCE: a restart while the user is on keyboard-us silently
  resets them to ngosen. Needs one live test before Fix 3 ships.
- In-progress Telex composition lives in the daemon's per-context state
  (ngosen addon, in-process). Process exit destroys every input context;
  clients get a fresh input-method connection with empty state. HIGH
  CONFIDENCE: an uncommitted syllable is LOST on fcitx5 restart, not
  committed, not preserved. This is the direct cost of step 2 of Fix 3.

### E7. The sensitivity problem (from T's timeline, re-checked, not re-run)
- During the 16:42-16:45 stall, T's scripts kept READING the IM fine:
  values reported at 16:44:08, 16:44:35, 16:45:00 with no read timeout,
  and the cycle command itself returned in 7ms at 16:45:00. What froze
  was the APPLICATION of the switch (21s late) and wtype key delivery.
- Therefore a `fcitx5-remote -n`-only probe would very likely have shown
  HEALTHY through the entire stall. The read half of the probe is
  non-invasive and almost certainly INSENSITIVE to this stall signature.
- The cycle round trip is the only sensitive half, and it is the invasive
  half. Any probe design that logs one combined "probe OK/slow" number
  learns nothing; the two halves must be timed and logged separately.

## Answers to the brief's questions

### Q1. Existing timer/cron setup?
None for input. One precedent timer exists (opencode-telegram-watchdog,
4min interval). No crontab binary. A user timer is feasible, but see E1
on AccuracySec.

### Q2. Actual restart time of omarchy-fcitx5.service?
Daemon start-to-dbus-ready under 1s (E3); full restart interruption
about 1-3s. Cheap in seconds, expensive in lost composition (E6).

### Q3. In-progress Telex composition on fcitx5 restart?
Lost (E6, high confidence). Plus a probable silent IM reset to ngosen
(medium confidence, untested).

### Q4. Probe running during an agent-driven typing session?
- The `-n` read half: harmless, 1.6ms dbus read, different path from wtype.
  wtype contention does NOT slow `-n`.
- The cycle round-trip half: HARMFUL during typing. Healthy timings per T:
  first cycle lands in ~200ms, cycle back in ~1s. So every probe leaves
  the user in the WRONG input method for roughly 0.2-1s, twice per probe
  window. Any keystroke in that window composes as plain US, or splits a
  Telex syllable across two methods. T's own garbled string
  "chaof banjhào bạn xin chaoào" is exactly this failure mode, caused by
  delayed keys. Agent typing via wtype is equally exposed: a flip
  mid-string corrupts agent-typed text too, and agent sessions are the
  main "AI-optimized Zen" context this fix is meant to protect.

### Q5. Can the watchdog's cycle round trip FLIP the IM and leave it wrong?
Yes, and the failure mode is specific. In a 2-method group two cycles net
to identity ONLY if both land. If either SetCurrentIM hits the 1000ms
timeout, indicator.py clears pending silently (E4) and one flip is lost,
netting exactly one flip: the user is left in the wrong IM with no error.
During a stall, the cycle-back is the most likely half to be lost, which
is precisely the condition the watchdog is detecting. The probe can also
absorb a user's own Super I press: select_next computes from
`pending or current`, so a user press interleaved with the probe's two
cycles has a timing-dependent outcome, not a deterministic one.

### Q6. Can killing indicator.py during its 50ms pending poll lose a switch?
Yes, confirmed by source (E4). Pending is in-memory only; kill destroys
it; the restarted instance snapshots whatever fcitx5 currently reports.
A Super I press the user made a fraction of a second before the kill is
silently dropped, and Super I is dead for the 5s restart window (E5).
Fix 3 step 1 as specified fires exactly when the user is most likely to
have just pressed Super I (during a stall, mashing the key).

### Q7. False STALL from wtype contention vs real stall?
- `-n` half: no false positives from wtype contention (different path),
  but also likely no true positives (E7).
- Cycle half: real risk. Healthy cycle-back already took 1s once (T,
  16:49). Under load 1.4-1.8 a single 2s threshold is tight against a 1s
  healthy worst case. A single-sample 2s rule WILL eventually false-fire
  on load spikes. Require confirmation (see thresholds below).

### Q8. Blast radius if the watchdog misfires repeatedly?
Per misfire: 5s of dead Super I (step 1), 1-3s of no input plus a lost
composition plus a possible silent IM reset to ngosen (step 2), and two
probe-induced IM flips every 30s regardless. Loop scenario: the probe
reads failure while fcitx5 is still activating (or while the reader is
in its 5s restart window), treats its own restart as "still stalled",
and restarts again. Without a cooldown and a cap, the user gets typing
interrupted every 30s, compositions dropped, and the IM flapping between
methods, which is strictly worse than the original symptom (a rare
3-minute stall that self-clears). Also note Fix 3 step 1 does not match
the observed stall at all: indicator.py PID 3444 was ALIVE through the
whole 16:42-16:45 window, and wtype froze too, and wtype does not go
through indicator.py. Killing the reader cannot unfreeze wtype.

## Sequencing: Fix 5 first, Fix 3 later
The stall trigger is UNKNOWN (T open item 4). Fix 3's restarts are aimed
at components that were observed healthy during the stall (reader alive,
daemon journal clean, no crash), and the only restart with a plausible
mechanism (fcitx5, hung-but-alive) is unproven. You cannot write a
correct recovery for a fault you have not located. Fix 5 is what locates
it. Fix 3 before Fix 5 is shooting in the dark with live ammunition
pointed at the user's typing.

## Thresholds (recommended, to be validated against Fix 5 logs)
- `-n` read: healthy 1.3-1.9ms; STALL only if >2s (1000x healthy).
  A slow `-n` is strong evidence; a fast `-n` proves nothing (E7).
- Cycle round trip: healthy land ~200ms, back ~1s worst seen; STALL only
  if the flip has not landed after 2s AND a second consecutive probe
  30s later also fails. Never judge on one sample.
- Never judge STALL while omarchy-fcitx5.service is activating, within
  10s of an indicator kill, or within 10s of an fcitx5 restart.
- Cap restarts: max 3 per hour, then fall back to log-only and stop
  touching the input stack. Log every restart with before/after IM.

## VERDICT: Fix 5 (logging-only stall monitor)
IMPLEMENT NOW. Confidence: HIGH.
- It is the only way to close T's open item 4 with evidence instead of
  guessing, and it costs the user nothing except probe disturbance.
- Design correction to T's proposal: do NOT run the cycle round trip
  every 30s. Run `-n` every 30s (cheap, non-invasive) and the cycle round
  trip every 2 minutes. A ~3-minute stall is still very likely caught by
  at least one cycle probe, while wrong-IM exposure drops about 4x.
  Log the two halves SEPARATELY with timestamps, plus load average and
  the IM before and after each probe (to catch probe-induced flips).
- Run for 7 days or until 2 stalls are captured, whichever comes first.
  Then stop and correlate with journalctl (fcitx5, Hyprland, Chromium
  launches, CPU spikes) before any restart logic is armed.
- Verification test: on the next stall, the log must show exact
  start/end timestamps AND which half went slow (read vs cycle vs both).
  Success is a captured stall with a correlatable journal window, or 7
  clean days with a measured zero false-positive rate for the cycle half.
  If 7 days pass with zero stalls, extend, do not declare victory.
- Strongest 3 reasons:
  1. The trigger is unknown and the read half likely cannot see this
     stall at all (E7); only a logging monitor with separated halves can
     identify which component stalls, and no restart design is correct
     until that is known.
  2. It is safe: logging-only, no restarts, no kills, no lost
     compositions; the only cost is a 2-minute cycle probe, which is
     disclosed and bounded.
  3. It directly produces the evidence Fix 3 needs (thresholds, false
     positive rate, stall location, whether restarts clear it), so it
     unblocks the later decision instead of duplicating it.

## VERDICT: Fix 3 (input watchdog with restarts)
IMPLEMENT LATER (with conditions). Confidence: MEDIUM-HIGH that it must
not ship as specified.
- As specified (30s cycle round trip, kill indicator on any STALL, then
  restart fcitx5), it should NOT go live. Step 1 does not match the
  observed stall (reader was alive, wtype also froze). Step 2 duplicates
  systemd Restart=always for crashes and is unproven for hung-alive.
  The detector itself flips the IM every 30s and can leave it wrong
  (Q5), lose a pending user switch (Q6), and loop on its own restarts
  (Q8). The cure is worse than the disease at current evidence.
- Conditions for implementation, in order:
  1. Fix 5 captures at least one stall and identifies WHICH component
     stalls (fcitx5 vs indicator vs compositor), with timestamps.
  2. A MANUAL restart of the identified component during a captured
     stall is shown to clear it faster than the ~3min self-clear.
     If no restart clears it, Fix 3 is rejected outright.
  3. Thresholds and the 2-consecutive-failure rule are validated against
     Fix 5 logs with a measured false-positive rate (target: zero false
     restarts in the logging period).
  4. Redesign: kill indicator.py ONLY when the reader is provably dead
     (cycle exits 1 / watcher not running), never on a generic STALL.
     Suppress STALL judgment during activating/restart windows. Cap 3
     restarts per hour, then log-only. Record IM before/after every
     restart and restore it if the restart reset it to ngosen.
- Verification test: a forced drill on a captured stall (restart clears
  it, composition loss is disclosed, IM is restored), PLUS a 7-day
  dry-run of the full watchdog in log-only mode showing zero false
  restarts, before the restart paths are armed.
- Strongest 3 reasons:
  1. The mechanism does not match the evidence: the reader was alive
     through the stall and wtype froze independently, so killing the
     reader cannot fix the observed fault, and fcitx5 restart is
     unproven for a hung-but-alive daemon with a clean journal.
  2. The detector is itself a disturber: a 30s cycle round trip puts
     the user in the wrong IM for ~0.2-1s per probe and can leave the
     IM flipped when the cycle-back is lost to the 1000ms timeout,
     exactly during a stall.
  3. The blast radius of a misfire loop (dead Super I, lost Telex
     compositions, IM reset to ngosen, restart-on-restart) exceeds the
     cost of the rare self-clearing stall it is meant to fix.

## What I did NOT do
- No file edited, no service restarted, no process killed on the laptop.
  indicator.py PID 3444 and fcitx5 PID 1828 are the same PIDs T saw.
  IM left at ngosen, as found. All checks were reads.
- Fix 1 was not revisited (already applied, per brief).
- Fix 2 and Fix 4 are out of scope for this verdict and were not judged.
- Open item carried forward: whether fcitx5 restart resets the current
  IM to DefaultIM (medium confidence, profile has no current-IM field).
  One live test (restart while on keyboard-us, read `-n` after) settles
  it; do it during Fix 5 setup, not as a surprise to the user.
