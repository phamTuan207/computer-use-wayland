# Council decision: Vietnamese typing fixes (Worker V)
# Date: 21/11/2026. Decided by council, not by the owner (owner order 17:23:
# decide yourselves, do not wait for the user). All times Asia/Ho_Chi_Minh.
# Repo: computer-use-wayland, branch todolist-push.

## The council
- Council A: Fix 2 (indicator.py retry + wrapper). Verdict file:
  improvements/worker-v-council-a.md (commit 8b124df).
- Council B: Fix 3 (watchdog) + Fix 5 (monitor). Verdict file:
  improvements/worker-v-council-b.md (commit ebaa61b).
- Council C: Fix 4 (ActiveByDefault) + audit of T's diagnosis. Verdict file:
  improvements/worker-v-council-c.md (commit d5d8fb8).
- Redteam: attack on all proposals. Verdict file:
  improvements/worker-v-redteam.md (commit 7be2f1b).
- Diagnosis under review: Worker T, improvements/worker-t-vietnamese-typing-diagnosis.md
  (commit 029cb9b). Fix 1 (lotus-autostart.sh -s lotus to -s ngosen) was already
  applied by Muse before the council; the council reviewed it retroactively.

## Diagnosis judgment: SOUND WITH GAPS (Council C, ~85% confidence)
- Sound: the 16:42-16:45 stall is real (5 wtype hangs, 21s Super I lag vs 200ms
  healthy, garbled late keystrokes), re-verified from T's on-disk logs. The
  silent pending-clear mechanism is confirmed in indicator.py source.
- Gaps (G1-G5): G1 Marionette exoneration overstated (a Marionette session WAS
  active during both stall runs; only BiDi was absent). G2 pending-clear
  attribution imprecise (clearing happens in the two callers, not in refresh()
  itself; worse than T wrote, the code promises a retry but only re-reads).
  G3 missed suspects (Chromium scopes 16:42:41, 16:43:09; xkbcomp recompiles
  bracketing recovery at 16:45:19 AND 16:45:21). G4 load-spike candidate weak
  (load 1.78 on 12 CPUs is ~15%). G5 per-context H2 rests on an unverified
  ShareInputState default.
- Consequence recorded: Fix 5's monitor must also log Marionette session
  lifetimes, Chromium scope starts, xkbcomp events, and per-core load.
  (Implemented in the monitor's log fields where feasible; Marionette
  lifetimes are logged by the agent runners separately, not by the monitor.)

## Decisions (one per proposal)

### Fix 2a (indicator.py: retain pending instead of silently dropping it)
VERDICT: IMPLEMENT NOW, in redesigned form (unanimous direction, redteam included).
- What was WRONG with T's spec: a 2s retry budget does not cover the observed
  21s stall (A, redteam F2a-1). A synchronous retry loop inside refresh()
  lengthens the single-threaded GLib main-loop block that makes presses pile
  up (redteam F2a-2: one tick can already block ~7s). The patch target was
  wrong: pending is cleared in THREE places (watch.refresh() line 231,
  Indicator.refresh() line 112, command() line 302), not just refresh()
  (A, C G2, redteam C1).
- What was IMPLEMENTED (council synthesis):
  - No new sync retry loop. Pending is retained across transient dbus errors;
    the existing 50ms pending poll re-attempts refresh().
  - Pending TTL 30s (covers the observed 21s stall with margin; a newer press
    supersedes; on expiry the drop is LOGGED, never silent). Answers redteam
    F2a-7 staleness (a 5-minute-old press cannot flip a password field).
  - All three clear sites covered: watch.refresh() and command() no longer
    clear pending/last on error; Indicator.refresh() keeps only the legitimate
    clear (method genuinely absent from a successful snapshot) and no longer
    drops pending when the post-SetCurrentIM re-snapshot fails (it returns the
    pre-switch reading and lets the next poll confirm).
  - Poll backoff (A2): 50ms healthy, 2000ms after a failure, so a stalled bus
    is not hammered.
  - Rate-limited logging (once per 5s per message) to stderr AND to
    ~/.cache/agent-computer-use/indicator-errors.log, because the Quickshell
    stderr sink is unverified (redteam F2a-5).
  - Patch lives in-repo (improvements/fix2a-indicator.py.patch, original +
    patched copies) AND at ~/.config/agent-computer-use/patches/ on the
    laptop. A post-update hook
    (~/.config/omarchy/hooks/post-update.d/reapply-indicator-patch.hook)
    re-applies it after omarchy-settings upgrades (both files are owned by
    omarchy-settings 4.5.0-3). Hook always exits 0, never fails an update.
- Verification (live, 17:32-17:33): patched file compiles; installed with
  sudo; reader restarted (PID 159243); old path cycle test ngosen to
  keyboard-us to ngosen passes. No error log lines since install.
- Rollback: sudo cp the backup at
  ~/.config/agent-computer-use/patches/indicator-original-20261121.py over
  /usr/share/omarchy/default/input-methods/indicator.py, kill the reader
  (Quickshell restarts it in 5s). One command, no other component depends
  on the patch.

### Fix 2b (Super I wrapper: verify switch, fall back if not landed)
VERDICT: IMPLEMENT NOW, in redesigned form. REJECT as specified (unanimous).
- What was WRONG with T's spec: the `-t` fallback toggles Active/Inactive,
  not methods (proven by help text + live test: -t flips ngosen/2 to
  keyboard-us/1 and back). During a stall the 1s poll reads stale state, so
  the fallback false-triggers in exactly the case it is meant to fix, then
  the stalled SetCurrentIM lands 20s later and toggles back: user ends on
  the opposite method (A, redteam F2b-1/F2b-2). No serialization: mashing
  Super I runs concurrent wrappers and the final method is parity luck
  (redteam F2b-3). No timeout on the wrapper's own dbus calls (F2b-4).
  Editing the package-owned bind file is unnecessary (F2b-5).
- What was IMPLEMENTED:
  - Wrapper ~/.local/bin/omarchy-input-method-switch (copy in repo:
    improvements/input-switch-wrapper.sh). Switches by EXPLICIT TARGET
    (`fcitx5-remote -s <target>`): a redundant re-apply is a harmless no-op,
    so wrapper and indicator retry converge instead of fighting.
  - flock -n serializes presses (duplicate dropped, never queued).
  - `timeout` on every fcitx5-remote call (0.2s reads, 1s set).
  - Poll up to 1s for the landing, then ONE -s re-apply, then stop and log.
  - If the current method cannot be read at all, fall back to queuing via
    `omarchy-input-method cycle` (Fix 2a retains pending 30s, lands later).
  - After a confirmed switch, notify-send shows the method (redteam A3:
    visible feedback kills the "typed through the wrong method" symptom).
  - Writes a marker file on every switch so the monitor can skip its cycle
    probe for 10s after a real press.
  - Bound from USER config (~/.config/hypr/bindings.lua, hl.unbind + o.bind),
    never touching the package-owned bind file. Survives Omarchy updates.
- Verification (live, 17:33-17:39):
  - Direct wrapper runs: 20/20 flips, all landed=1, 8-10ms each, final ngosen.
  - Dead-reader drill: reader killed (PID 165470), wrapper flipped ngosen to
    keyboard-us in 8ms during the dead window, reader restarted (PID 165692),
    state consistent. (T's acceptance test 3 claimed Fix 2a covers this
    window; redteam C4 correctly showed only the direct path can. The
    wrapper is that path.)
  - Double-press drill: sequential double returns to the original method;
    concurrent double gives exactly ONE flip (flock works, log proves it).
  - Bind registered: hyprctl binds shows exactly one SUPER+I "Switch input
    language" and one SUPER+SHIFT+I, no duplicates, plus the F9 test bind
    registered the same way and was removed after the test.
- NOT YET VERIFIED (stated plainly): a live physical Super I press. wtype
  virtual-keyboard presses do NOT trigger Hyprland binds in this setup
  (proven: registered SUPER+F9 marker bind, wtype press, no marker). The
  bind is registered and the wrapper is proven; the owner tests it with one
  physical press when back. One unexplained single flip (ngosen to
  keyboard-us) occurred during the wtype testing and did not reproduce in
  3 later presses; recorded here as unexplained, not attributed.
- Rollback: remove the two hl.unbind/o.bind lines from bindings.lua,
  hyprctl reload; the default bind (omarchy-input-method cycle) returns.
  The patched indicator.py keeps working with the old bind.

### Fix 3 (input watchdog: probe every 30s, restart indicator.py then fcitx5)
VERDICT: IMPLEMENT LATER, with conditions (Council B; redteam: reject as specified).
- Why not now: the mechanism does not match the evidence (reader PID 3444 was
  alive through the stall, wtype froze independently, so killing the reader
  cannot fix the observed fault). The probe itself is a disturber (cycle round
  trip flips the live method twice per probe, ~3,800 flips/day, and can eat a
  user press or leave the IM wrong when the cycle-back is lost). No backoff or
  circuit breaker: one 3-minute stall means up to 6 fcitx5 restarts, each
  destroying input contexts and resetting the method to DefaultIM. Missing-env
  false positive: cycle exits 1 without OMARCHY_PATH, which the probe would
  read as "stall" and answer with a restart every 30s forever.
- Conditions to implement (in order): (1) Fix 5 captures a stall and identifies
  WHICH component stalls. (2) A MANUAL restart of that component during a
  captured stall is shown to clear it faster than the ~3min self-clear; if no
  restart clears it, Fix 3 is rejected outright. (3) Thresholds + 2-consecutive-
  failure rule validated against Fix 5 logs with zero false restarts. (4)
  Redesign: kill indicator.py ONLY when provably dead, suppress STALL judgment
  during activating/restart windows, cap 3 restarts/hour then log-only, record
  IM before/after every restart and restore it.

### Fix 4 (ActiveByDefault=True experiment)
VERDICT: REJECT (Council C ~80%, redteam agrees).
- Why: it treats a mechanism T himself refuted (new Zen tabs already keep
  ngosen active, proved live 16:44). Its acceptance test is
  non-discriminating (5 fresh tabs would already pass 5/5 with the fix off).
  The downside is documented and daily: terminal bleed (new terminal inherits
  the active IM), Telex corrupts everyday shell words (dd, git add, root,
  free, docker, bash, status), DdFreeStyle=True explicitly exempts dd from
  auto-restore, and terminal sudo passwords have no password-purpose
  protection, so they corrupt invisibly. The password-field safety claim rests
  on a code comment, never a test.
- Revisit ONLY if a distinct symptom is reported ("IM inactive in the first
  field after login"), as a bounded trial paired with ShareInputState=Program
  plus terminal and sudo-password regression checks.

### Fix 5 (stall monitor)
VERDICT: IMPLEMENT NOW, in redesigned form (Council B high confidence; redteam:
reject as specified, redesign as read-only).
- What was WRONG with T's spec: the proposed probe is not logging-only, it
  cycles the IM twice every 30s (redteam F5-1). One combined number cannot
  localize the trigger across three failure domains (F5-2). 30s cadence is too
  coarse to order events seconds apart (F5-3). No owner, stop rule, or alert
  (F5-4).
- What was IMPLEMENTED (B + redteam synthesis):
  - Script ~/.local/bin/input-stall-monitor.sh (copy in repo:
    improvements/input-stall-monitor.sh), run as a systemd user service
    (long-running loop, not a timer: a timer with AccuracySec=30s would make
    a 30s cadence imprecise by design).
  - Read half every 30s: `timeout 2 fcitx5-remote -n` latency + IM + load +
    fcitx5/indicator liveness. Non-invasive.
  - Cycle half every 2 min: round trip with IM before/after, flip latency,
    landed flag, logged SEPARATELY from the read half. Skipped if the user
    pressed Super I in the last 10s (marker file). Infra failures (reader
    dead, env missing) logged distinctly, never counted as stalls.
  - JSONL log: ~/.cache/agent-computer-use/input-monitor.log.
  - STOP RULE: 7 days, or 2 stalls captured, whichever comes first. Then
    correlate with journalctl before any restart logic is armed.
- Verification (live, 17:36-17:39): service active since 17:36:58, read probes
  3-4ms rc 0, first cycle probe 17:38:29 flip_ms 117 landed 1, im_before and
  im_after both ngosen (restored correctly). IM left ngosen.
- Rollback: systemctl --user disable --now input-stall-monitor.service.

### Fix 1 (lotus-autostart.sh, retroactive review)
VERDICT: SURVIVES as harmless, completed (redteam: applied fix was NOT what
was proposed; verification was vacuous).
- What was missing: only the word changed (lotus to ngosen); 2>/dev/null still
  on both lines, comments still said Lotus, and `-n` prints ngosen with or
  without the script (DefaultIM), so the check proved nothing. Whether -s does
  anything at login with no focused window is still untested (F1-4).
- What was DONE now: stale comments fixed in lotus-autostart.sh AND in
  ~/.config/hypr/autostart.lua ("Auto-switch to ngosen"); a marker line was
  added (timestamp + current IM to
  ~/.cache/agent-computer-use/lotus-autostart.log), so script execution at
  login is verifiable. The 2>/dev/null redirects were KEPT: the sink they
  would expose to is unknown (F1-2), and the marker makes execution provable
  without depending on it. Script run live 17:38: marker written, IM=ngosen.
- Note: the old line could never change anything; the new line forces ngosen
  at every login, so if the owner ever changes DefaultIM away from ngosen the
  script will override it (accepted risk, recorded).

## Redteam alternatives, decided
- A1 direct bind from user config: ADOPTED as Fix 2b (the wrapper).
- A2 backoff + TTL retention: ADOPTED inside Fix 2a (2000ms backoff after
  failure, 30s TTL).
- A3 visible method feedback: ADOPTED (notify-send after confirmed switch).
- A4 longer dbus timeout only: REJECTED (each poll tick blocks 5x longer,
  stdin pile-up gets worse).
- A5 disable the 50ms poll: REJECTED as a fix (cadence number is meaningless
  under stall; the problem is synchronous calls, not cadence).
- A6 proper fix (async dbus in indicator.py): IMPLEMENT LATER. It is the real
  fix for the mechanism (main loop never blocks, presses processed in order
  with a sequence number), but it is a bigger change to a package-owned file
  and needs the re-apply procedure with a hash check. A1-A3 ship now; A6 is
  the follow-up.

## Scope gap (stated plainly, per redteam)
NOTHING in this decision fixes the wtype (agent typing) stall itself: 5
consecutive hangs over ~3 minutes in the observed window. All five fixes
target Super I bookkeeping or stall detection. The shared-path stall that
froze both wtype and dbus has no fix proposed. Fix 5's monitor is the path
to one: when it captures the next stall with per-component timings, the
council reconvenes with the trigger identified.

## Files implemented (laptop + repo)
- Laptop: /usr/share/omarchy/default/input-methods/indicator.py (patched,
  backup at ~/.config/agent-computer-use/patches/indicator-original-20261121.py,
  patched copy at .../indicator-patched-20261121.py).
- Laptop: ~/.local/bin/omarchy-input-method-switch (wrapper).
- Laptop: ~/.config/hypr/bindings.lua (Super I / Super+Shift+I rebind).
- Laptop: ~/.local/bin/input-stall-monitor.sh + ~/.config/systemd/user/input-stall-monitor.service (running).
- Laptop: ~/.config/omarchy/hooks/post-update.d/reapply-indicator-patch.hook.
- Laptop: ~/.local/bin/lotus-autostart.sh (comments + marker), ~/.config/hypr/autostart.lua (comments).
- Repo (todolist-push): improvements/fix2a-indicator.py.patch,
  improvements/indicator-original-20261121.py,
  improvements/indicator-patched-20261121.py,
  improvements/input-switch-wrapper.sh, improvements/input-stall-monitor.sh,
  improvements/input-stall-monitor.service,
  improvements/reapply-indicator-patch.hook,
  improvements/lotus-autostart-fixed.sh,
  improvements/worker-v-council-a.md, improvements/worker-v-council-b.md,
  improvements/worker-v-council-c.md, improvements/worker-v-redteam.md,
  improvements/worker-v-council-decision-20261121.md (this file),
  improvements/worker-v-implementation-log.md.

## Rollback (whole decision, one list)
1. indicator.py: sudo cp the backup over /usr/share/.../indicator.py, kill
   the reader (restarts in 5s).
2. Wrapper/bind: remove the two hl.unbind/o.bind lines from bindings.lua,
   hyprctl reload; default Super I returns.
3. Monitor: systemctl --user disable --now input-stall-monitor.service.
4. Hook: delete reapply-indicator-patch.hook.
5. lotus-autostart.sh: restore ~/.local/bin/lotus-autostart.sh.bak-20261121.
6. IM state: fcitx5-remote -s ngosen. Left at ngosen on 21/11 17:39.
