# Council OPT-M1, Voice 2: EVIDENCE
# Classes (A) session/guardian startup failure, (B) silence / slow first action,
# (C) overlay never shows / flicker. Evidence contract: what proof each candidate
# method needs, what observation would falsify it, what is still unmeasured.
# No em/en dashes in this file.

## Method of this voice
For each candidate method, state the claim, the proof it needs, the falsifier
(one observation that kills it), and the unmeasured gap. A method with no
falsifier is not a method, it is a hope. A claim with no named proof is not
evidence, it is an opinion. Sources are cited as file:line where read here,
or LOG where they come from a worker log.

## Class A: session/guardian startup failure

### A candidate 1: load the plugins live (F1 plan B) and the session starts
- Claim: the session dies only because glass + guard are unloaded; loading them
  restores sessions. LOG: improvements/worker-f1-guardian-fix-log.md, fix plan B.
- Proof needed, all of it, in order: (1) same-minute pre-flight (F1 council 2
  preconditions 1-8: ABI match, plugin list exactly hyprbars 1.0, configerrors
  empty, no session/token/socket dir, .so shas match filenames and manifest,
  ldd 0 not found on both); (2) run installed-tree activate-glass.py then
  activate-cursor-guard.py with manifest abi and profile-sha256 9a151634;
  (3) plugin list shows hyprglass + computer-use-cursor + hyprbars;
  (4) `hyprctl cu-cursor status` returns JSON; (5) socket exists;
  (6) a session starts, `ready` prints, pill appears in a fresh observe;
  (7) one planned click lands, verified by cursorpos plus a second fresh
  observe; (8) clean stop, pill gone, desktop clean.
- Falsifier: after a correct glass-then-guard load with all pre-flight checks
  green, the session still dies, or `cu-cursor status` still answers
  `unknown request`, or the pill never appears in a fresh observe. Any one of
  those kills the "only unloaded plugins" claim and forces the investigation
  back to the guardian code (supervise, Guard.__init__, indicator listen).
- Status: NOT YET RUN. Live activation is gated on council 1, council 2,
  council 3 and redteam verdicts plus preconditions 1-8. The negative test
  (22:39, LOG F1) proves only that the error message now names the cause; it
  does not prove sessions work.

### A candidate 2: the JSON guard alone (diagnostic fix) is enough
- Claim: naming the error in guard_reply + supervise is the fix.
- Proof needed: a session that fails must print the named cause in the envelope,
  and a session that succeeds must start. The first half is proven (22:39 live
  negative test: error now reads "session guardian startup failed: cursor guard
  reply is not valid JSON (got: unknown request)..."). The second half is not.
- Falsifier: any session failure after this fix that still prints a bare error,
  or any session that succeeds in the error text but never shows a pill. Also:
  council 1 A1 (drain race) predicts a fast death can still produce a bare
  envelope; one observed bare envelope after the fix falsifies "the diagnostic
  fix is complete" and proves A1 real.
- Status: HALF PROVEN. Council 1 bottom line, LOG: "the root-cause chain is
  proven live, the fix is correct in design, but it must not be presented as
  restoring sessions. Until plan B live activation runs, sessions still fail,
  only with a clearer error now." This council agrees.

### A candidate 3: the drift repair makes the next login load the plugins
- Claim: copying installed optics + manifest over the laptop-repo copies makes
  the login loader pass manifest_validation at the next login.
- Proof needed: (1) laptop optics sha256 = 9a151634 and manifest diff empty
  (done 22:37, LOG F1); (2) the loader run mid-session now fails at
  fresh_login_gate, NOT manifest_validation (done 22:37, loader log record time
  1795275379, LOG F1); (3) at the next real login, the loader log shows stage
  complete with glass 199153ae and guard 06712eaf, and the plugin list shows
  both loaded without manual activation.
- Falsifier: at the next login the loader log still shows stage
  manifest_validation, or shows stage complete but the plugin list lacks one
  plugin. Either kills the "drift was the only loader defect" claim and points
  at the loader itself (30s single-shot gate, redteam R10; silent failure,
  redteam R1).
- Status: PARTS 1-2 PROVEN, part 3 UNMEASURED (no login has happened since the
  repair). The repair is also not durable: it is an uncommitted change in a
  repo at detached HEAD 56f5af4 on gitignored files (redteam R2). Any checkout,
  reset, clean, or fresh clone wipes it. Durability proof needed: a re-pin
  check in sync-installed/setup that fails loudly when installed and repo
  manifests disagree, plus a test that exercises it.

### A candidate 4: session gate on hyprglass active (redteam R3)
- Claim: sessions must refuse to start when glass is down, so a live session
  always has a pill.
- Proof needed: (1) with glass paused or crashed and guard loaded, a session
  attempt refuses with a named error instead of starting pill-less; (2) with
  glass active, the session starts normally; (3) the require-liquid marker
  state is published (present or absent) in the installed tree, not left
  gitignored and unverifiable.
- Falsifier: a session starts and completes actions while the pill is absent
  in a fresh observe. That single observation falsifies the gate and proves
  class C1 is still open.
- Status: UNMEASURED, not implemented. This is the largest open evidence gap
  in class A/C1: the R3 gate does not exist in code today.

### A unmeasured list (what nobody has measured yet)
- A5: the old pin 674441ea claimed to match commit d27ad0a (blur 0.10). This
  council did NOT verify the sha. Until F1 runs the git show + sha256sum on
  the laptop repo, the Layer 4 story has two versions and the log is wrong in
  one of them. Cost of checking: one command. Cost of not checking: the
  redteam attacks the wrong drift story.
- Drain race A1/R6: council 1 predicts a bare envelope on a fast death; redteam
  simulation found 0 empty in 300 trials on the exact pattern, 1 partial in 200
  on a variant. The window is small but real. Proof needed: a fast-death test
  that asserts the exact envelope string (council 1 A4), not just that the
  text appears somewhere via the tee.
- UnicodeDecodeError A3/R5: verified live on the VM by council 1, but the fix
  (catch alongside JSONDecodeError, errors='replace' on the drain) is not
  implemented and has no test.
- Truncated JSON R4: verified on the VM, fix not implemented, no test.
- The VM `re` deletion (22:25:39 +07, LOG F1/F2/VMFIX): cause UNKNOWN. One file
  missing, dpkg -V clean after restore, observe 22:38 ok. No agent has proven
  which process deleted it. This is not class A evidence, but any future
  "file vanished" claim must be checked against it, and the deletion window
  (mtime 15:25 UTC vs last good SSH ~22:24 +07) is still unexplained.
- test_cursor_session.py does not compile on VM Python 3.12 (SyntaxError, too
  many statically nested blocks, line 570, pre-existing). All session-test
  evidence is laptop-only (Python 3.14.10). An independent re-run on the VM is
  impossible until R12 is fixed.

## Class B: silence / slow first action

### B candidate 1: act-now as the default path (F2 first_action.py)
- Claim: overlay-first + 20s session deadline + fallback only on session-start
  failure gets the first visible action under 30s from the order.
- Proof needed, on a live run: (1) order timestamp recorded; (2) overlay-on
  timestamp and a fresh observe showing the pill; (3) first move timestamp;
  (4) first click timestamp and a fresh observe showing the click landed;
  (5) the JSON envelope with path taken (session or fallback), timings
  (order -> overlay-on, order -> first move, order -> first click), pill_shown
  flag, and bypass reason if any; (6) the JSONL timing log entry;
  (7) no gap over 60s between visible actions while the task runs.
- Falsifier: a rehearsal where order-to-first-visible-action exceeds 30s with
  the overlay on, or a run where the pill is absent from the after-capture, or
  a fallback that replays an act failure (is_session_start_failure returning
  True when actions partially ran). Any one kills "act-now is fast enough" or
  "act-now is safe" and the bottleneck must be re-measured (observe capture,
  agent think, session deadline) before any further claim.
- Status: CODE-PROVEN ONLY. tests/test_first_action.py 21/21 on the VM; deployed
  to the laptop (md5s verified, `act-now --help` works, `import first_action`
  OK). The live rehearsal has NOT run. It is gated on F3 Zen restore and the
  ZT-00 gate. ZT-00 gates 0-3 passed 22:44 (67 tabs listed, Zen PID 426338
  alive, 9222 returns 200, Marionette session created), but the rehearsal step
  itself (one act-now batch) is still pending, and the 22:45:15 fresh observe
  showed two Muse chat windows, not Zen, so Zen workspace location was still
  unresolved at last log.

### B candidate 2: the 30s target is the right target
- Claim: under 30s order-to-first-visible-action is achievable and is what the
  owner asked for.
- Proof needed: the owner order 22:21 sets the target (<30s) and the priorities
  (FAST, CONTINUOUS, OVERLAY VISIBLE). The number itself needs a baseline: the
  only measured order-to-click is ~5 minutes (22:11:30 to 22:17), of which the
  click was 0.31s. A 30s target is a 10x cut on the measured 5 minutes, which
  matches the standing 10x mindset but is not derived from a tool limit.
- Falsifier: if the rehearsal shows a floor above 30s that no path beats (for
  example observe capture + agent think alone exceed 30s on a cold start), the
  target is wrong and must be re-set from the measured floor, not defended.
  Conversely, if the rehearsal lands well under 30s, the target may be too
  loose and the next target comes from the measured distribution.
- Status: TARGET SET BY OWNER, floor UNMEASURED. No order-to-overlay timing
  exists yet for any path.

### B candidate 3: narration is unnecessary (owner 22:21 correction)
- Claim: dropping pre-action narration does not slow the run or hide progress,
  because the overlay itself reports what is happening.
- Proof needed: a rehearsal run with no narration where the overlay is visible
  in every after-capture and the owner (or the log) can read progress from the
  pill + cursor + screen alone. The F2 rule doc states this; the rehearsal must
  show it.
- Falsifier: a rehearsal where the overlay is on but the visible state does not
  show what step is running (for example a long think with no cursor move and
  no label change), so the owner cannot tell progress from the screen. That
  observation reopens the narration question, narrowed to label updates rather
  than spoken narration.
- Status: UNMEASURED. The label mechanism exists (overlay.py label routing),
  but no live run has shown whether the pill label tracks the step.

### B unmeasured list
- No order-to-first-visible-action timing exists for ANY path (session, direct
  Pointer, or act-now). The 5-minute figure is order-to-click, not
  order-to-overlay, and the overlay was never on in that run.
- The fallback safety predicate (is_session_start_failure, first_action.py
  lines 153-176) is unit-tested with fakes but has never been exercised live
  against a real guardian failure. A live session-start failure with a
  partially-run action would be the dangerous case; the predicate claims to
  exclude it, but the exclusion is unproven live.
- The 20s session deadline is a chosen constant, not a measured one. If the
  guardian normally takes 21s on a cold start, the deadline converts successes
  into fallbacks. Proof needed: a distribution of successful session start
  times, which does not exist because sessions have not started since 03:05.
- Think time (H2) is still unmeasured on an agent-driven run. Todolist 2.3.1
  is ticked but only scripted (Y11b, think null). G-H2 folds instrumentation
  into Y13/Y14/A1. Until then, any claim that "think is the bottleneck" or
  "think is not the bottleneck" is unproven for class B.

## Class C: overlay never shows / flicker

### C1 candidate 1: watchdog respawn fixes overlay loss (todolist 2.2.4)
- Claim: Daemon._ensure_native() respawns a dead native indicator while holders
  remain, so the pill comes back without the worker noticing.
- Proof needed: (1) unit tests pass (done: test_daemon_respawns_dead_native +
  test_daemon_keeps_live_native); (2) LIVE proof: kill the indicator during a
  hold, show the pill returns in a fresh observe, with timestamps. The live
  proof is explicitly still owed (todolist 2.2.4).
- Falsifier: killing the indicator during a hold and the pill does NOT return,
  or returns only after the holder releases and re-acquires. Either kills the
  "watchdog fixes overlay loss" claim.
- Status: UNIT-PROVEN, LIVE-UNPROVEN.

### C1 candidate 2: the R3 hyprglass gate (same as A candidate 4)
- See A candidate 4. One observation (a session completing actions with no pill
  in a fresh observe) falsifies it. Not implemented, unmeasured.

### C2 candidate 1: compositor/plugin repaint loop under animated LIQUID backdrop
- Claim: the ~10Hz flicker is a compositor/plugin repaint loop triggered by an
  animated backdrop in LIQUID mode, not an indicator bug.
- Proof needed, in the nested Hyprland only (owner choice C, 18:24): (1) load
  hyprglass in the nested compositor (Y6e nested LOAD TEST PASS 21:57 is the
  loader proof, not the flicker proof); (2) animated backdrop on, LIQUID mode,
  E1 per-event logging running; (3) count repaints/commits per second over at
  least 60s idle and 60s driving-equivalent; (4) repeat with animated backdrop
  off and with LIQUID off, same counts. The hypothesis predicts high repaint
  rate only in the animated + LIQUID cell.
- Falsifier: 0 repaints in the animated + LIQUID cell, or equal repaint rates
  across all four cells. Either kills the compositor-loop hypothesis and the
  investigation restarts from the E1 logs, with the indicator re-opened as a
  suspect only if the E1 logs show indicator events during a flicker.
- Status: UNMEASURED. Todolist 2.2.3 BLOCKED for the live compositor (loading a
  backup plugin risks crashing Hyprland while the owner works). The nested path
  is the only approved measurement route. Y6r AMEND requires fix A1-A10 + fresh
  re-review before any retry, and the pill measurement is still unproven (Y6e).

### C2 candidate 2: the indicator repaints at idle (already falsified)
- Claim: the indicator itself repaints and causes the flicker.
- Proof against it, LOG (todolist 2.2.1): 0 idle paints in 122 one-second
  windows, 32/32 frames pill pixel-identical, 60s idle with no events; no
  in-repo 10Hz driver exists (exactly 2 visibility toggles per observe, 0
  while idle). This candidate is DEAD. Any verdict that re-opens it without new
  E1 log evidence is re-litigating a settled measurement.
- Caveat, recorded honestly: the flicker work log file was NOT found in this VM
  repo (find for *flicker* returned nothing at 22:51 +07). The numbers above
  are cited as todolist-recorded. The redteam should re-verify them from the
  laptop copy or the E2 run before treating them as settled.

### C2 candidate 3: screenshots cause the flicker (already falsified)
- Claim: Muse screenshotting too often causes the flicker.
- Proof against it, LOG (todolist 2.2.5, I20 retraction): Muse observed every
  10-30s, which cannot cause ~10Hz flicker; disproven by code and by live E2
  measurement. DEAD. Do not revive.

### C unmeasured list
- The flicker rate (~10Hz, I10) was a user estimate, never measured. No log,
  no timestamp series, no frequency count exists for the 20/11 evening event.
  The owner ordered full time-stamped logging from 22:47 precisely because this
  event was never logged. Any future flicker claim without a timestamped E1 log
  is an estimate, not evidence.
- The 20/11 flicker happened when Muse drove directly; Codex driving was normal
  (I9). No controlled comparison exists (same screen, same backdrop, same mode,
  Muse vs Codex, repaint counts). The difference between the two drivers is
  unmeasured: it could be observe cadence, cursor movement, or compositor state,
  and the current evidence cannot distinguish them.
- The pill blur increase (0.0 to 0.15, todolist 4.1) is deployed in code but its
  effect on the live pill is unmeasured (no fresh observe of the new blur on the
  live compositor exists in the logs read here). It must not be cited as a
  flicker fix.
- The 22:44 stray click that opened the Omarchy menu is unattributed (F2/F3 logs
  do not record it; F2 denies it, F3 log notes a second menu-opening miss at
  22:45:38 by wtype Logo+1). Attribution is open, not evidence for any class,
  but the redteam should note that two different workers touched the workspace
  controls within minutes, which is a process gap, not a code gap.

## Evidence rules this council applies to the verdict
- No class is declared fixed on code review alone. Each class needs its named
  live proof, listed in the verdict with its falsifier.
- A VM unit test proves the code path, never the live behavior. Tests cited in
  the verdict are labeled VM or laptop, and laptop-only evidence is labeled as
  such (test_cursor_session.py cannot compile on VM Python 3.12).
- A user estimate (10Hz, "nearly 5 minutes") is a lead, not a measurement. The
  verdict replaces each estimate with the measured number where one exists, and
  marks the rest unmeasured.
- Where this council could not verify a claim (A5 d27ad0a sha, flicker work log
  file, OPT-SRC crawl), the verdict says so plainly instead of repeating the
  claim as fact.
