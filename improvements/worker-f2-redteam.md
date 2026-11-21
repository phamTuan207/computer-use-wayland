# Worker F2 redteam: silence-fix attack verdict

Redteam: independent attack on Worker F2's fix for the silence weakness.
Date: 2026-11-21, Asia/Ho_Chi_Minh. Repo branch todolist-push.
F2 commits reviewed: a576e69, afed06e, 8d1f775, 8979b30, 2495382, c2c0a8b,
e016cde, 62ad028, 82539bf.
Files attacked: scripts/first_action.py, scripts/cu.py (act-now wiring and
desktop_act), scripts/overlay.py, scripts/cursor_session.py,
scripts/cursor_theme.py, scripts/indicator.py, tests/test_first_action.py,
improvements/first-visible-action-rule-20261121.md,
improvements/worker-f2-silence-fix-log.md.
Method: read the code, traced every path by hand, constructed concrete
repros from the traced paths. No code modified, no live Zen driving, no
commits. No em or en dashes in this file, per owner rule.

## Verdict: BLOCK

The fix is fast and the genuine guardian-startup fallback works, but the
core safety claim ("an act failure is NEVER replayed") does not hold: the
replay classifier matches substrings with no evidence of WHEN the failure
happened, and two concrete mid-batch failure paths carry those substrings
(A1). The fallback refusal path crashes with a traceback instead of
refusing cleanly (A5), the overlay acquire can report visible while no
pill exists (A3), and holders are keyed by agent name so a concurrent
same-agent run loses its pill mid-action (A4). Those four break the
safety claim, the overlay claim, or the clean-refusal claim. The fix must
not be declared proven or used as the default live path until the
required fixes in section "Required fixes for GO" land with tests.

## What holds up (checked, not assumed)

- Overlay acquire is fast in rehearsal: 314-346 ms across runs 2-5.
  Genuine guardian startup failure falls back and completes (runs 2-5,
  4/4 fallback, session guardian fails, desktop_act completes).
- The double-print bug is really fixed: run() prints the envelope only
  in the finally block (first_action.py, end of run), and the tests parse
  stdout as a single JSON object, so a second print would fail
  json.loads. Regression-covered.
- Coordinate conversion for window observations is correct.
  image_point (cu.py:973) maps image coords through region, and for an
  uncropped window observation region equals the window bounds
  (observe, cu.py:893). Rehearsal cursorpos (2629,974) equals window
  [2509,914] plus (120,60) exactly. Click delivery is press 1, 25 ms
  wait, release 0, with post-release cursorpos re-verification
  (execute_group in desktop_act). A1 below does not dispute delivery.
- Stale SCREEN observations are mitigated: desktop_act re-observes in
  preflight and screen_changed returns a dict refusal, it does not act
  on stale pixels.
- Mid-batch RuntimeErrors inside desktop_act are caught by its execution
  try/except and returned as result dicts, they do not crash run().
  The crash class in A5 is the PREFLIGHT raises, not the execution ones.
- The timeout path is partly protected by cleanup ordering: the guardian
  cleanup list runs stop_group(driver) before server.close, and the
  supervisor finally runs terminate_driver before guard.wait. So the
  timeout replay in A2 is narrow, not wide open. A2 stays AMEND, not
  BLOCK, for that reason.
- The session-path screen-typing refusal is clean: cu.py main prints a
  JSON error and exits 1, and is_session_start_failure correctly returns
  False for it, so no replay on that path. Only the fallback path
  crashes (A5). The two paths are inconsistent.

## A1. REPLAY: substring matching with no phase evidence (BLOCK, safety)

Severity: breaks the core safety claim. An act failure CAN be replayed.

The classifier is scripts/first_action.py:153-175,
is_session_start_failure. It returns True when the combined session
stdout plus stderr contains any of: 'session guardian startup failed',
'Expecting value', 'cursor guard'. It never checks WHEN the failure
happened. Its docstring claims "True only when NO action can have run",
but the code has no phase evidence at all: it does not look for the
guardian 'ready' or 'registered' markers that supervise prints before
the driver runs (cursor_session.py supervise: 'ready' after the guardian
is up, 'registered' after the driver pid is received, then gate 'go').
A failure at any phase carrying a magic string is treated as a start
failure.

Concrete repro 1, 'Expecting value' mid-batch:

1. Session starts fine. Driver runs desktop_act on a batch, delivers the
   first click, then calls guard() before the next action group.
2. guard() calls hypr(env, 'activewindow') (cu.py, guard inside
   desktop_act). hypr (cu.py:493-524) does a bare json.loads(data) on the
   compositor reply, line 523-524, with no validation and no fallback.
   Any non-JSON reply (compositor hiccup, truncated socket read, an
   error string instead of JSON) raises
   json.decoder.JSONDecodeError: Expecting value: line 1 column 1
   (char 0). The same bare json.loads sits in move() via
   hypr(env, 'cursorpos'), called before every pointer action.
3. desktop_act catches the exception in its execution handler and
   returns {'ok': False, 'error': 'Expecting value: line 1 column 1
   (char 0)', 'completed': 1}. cu.py main prints that JSON to stdout
   and exits 1.
4. first_action.py run() reads the stdout, is_session_start_failure
   finds 'Expecting value' in the combined output (first_action.py:168)
   and returns True. run() falls back to desktop_act and REPLAYS the
   whole batch, including the click that already landed. Double click,
   double type, double navigation, depending on the batch.

Concrete repro 2, 'cursor guard' mid-session:

1. Session starts fine, driver is mid-batch, actions partially run.
2. The cursor-guard socket becomes ready (guard died, socket event).
   The guardian raises RuntimeError('session cursor guard lost')
   (cursor_session.py:178). The guardian is already known flaky on this
   machine: the guard plugin is not loaded in the live Hyprland
   (F2 log R2), so a mid-session guard event is the plausible failure,
   not an exotic one.
3. supervise sees the guardian die, prints 'session guardian died
   mid-session: ...' plus the drain tail containing 'session cursor
   guard lost', and terminates the driver mid-batch. Exit 1.
4. is_session_start_failure finds 'cursor guard' in the combined
   output (first_action.py:170) and returns True. Fallback replays the
   partially run batch.

Also note: the guardian drain tee forwards EVERY guardian stderr line
into the supervisor stderr (cursor_session.py supervise, _drain), so any
later guardian message containing a magic string lands in the matched
text. And _stdout_session_error (first_action.py:142) only parses stdout
as JSON; a JSON error printed to stdout by the session path is matched
the same way, with no phase check.

Exact fix required: make the classifier phase-aware. Fall back only
when the output proves the driver never started: require that the
guardian 'registered' marker (and the driver gate) is ABSENT, and match
anchored startup errors instead of substrings across combined output
(for example, the session JSON error equals 'session guardian startup
failed', or the stderr tail shows the guardian dying before 'ready').
A post-'registered' failure must never fall back, whatever strings it
contains. Add tests that feed a post-start stdout/stderr containing
'Expecting value' and 'cursor guard lost' and assert False.

## A2. SESSION DEADLINE: killpg misses the real tree, live check is a proxy (AMEND, safety)

Severity: weakens the safety claim and the speed claim; does not by
itself prove a replay, because cleanup ordering usually saves it (see
"What holds up"), but first_action never verifies the save happened.

Paths traced:

1. attempt_session (first_action.py:112-140) does Popen with
   start_new_session=True, then on timeout killpg(proc.pid, SIGTERM),
   3 s grace, killpg SIGKILL. But the session supervisor spawns BOTH
   the guard (cursor_session.py:238, start_new_session=True) and the
   driver (cursor_session.py:280, start_new_session=True) in their OWN
   sessions. killpg on the supervisor group kills the supervisor only.
   The guard and the driver survive the kill by design. Deadline
   enforcement therefore depends entirely on the supervisor finally
   (terminate_driver, then guard.wait up to 20 s) and the guardian
   cleanup chain, not on the kill itself.
2. The fallback decision uses session_live() (first_action.py:296),
   which probes the INDICATOR (overlay.py session_live, indicator
   request 'show'), not the driver process. It is a proxy for "no
   action can have run". Cleanup ordering (stop_group before
   server.close in the guardian finally) usually makes live go False
   only after the driver is dead, but first_action never waits for or
   checks driver death, and the decision is taken immediately after the
   supervisor exits, with no settle wait for the guardian cleanup.
3. desktop.lock serialises the fallback against a still-running driver
   (session act holds locked() around desktop_act, fallback takes the
   same lock), which prevents simultaneous execution, but the lock has
   no timeout: a surviving driver hangs the fallback forever, and the
   lock does not prevent a replay once the driver has finished and
   released it. A driver that completes the batch just after the
   supervisor was killed (its exit code is lost with the supervisor)
   is indistinguishable from a driver that never ran, and the live
   probe can read False for it.
4. The deadline covers only the session subprocess. Overlay acquire can
   take up to 15 s (_ensure_daemon deadline, overlay.py) plus 10 s
   socket timeouts, observation capture is unbounded, after-capture is
   unbounded, so order-to-first-action can exceed the 30 s target with
   no enforcement anywhere. --session-deadline-s is unvalidated:
   0 or negative makes communicate time out at once (instant
   SIGTERM/SIGKILL then fallback), a huge value defeats the deadline.
5. Test gap: test_timeout_kills_group uses `time.sleep(30)` in the
   SAME process group with default SIGTERM death. The production tree
   (guard and driver in separate sessions) is never tested, so the test
   passes while the real topology escapes the kill.

Exact fix required: after a timeout, explicitly verify the driver is
dead (poll the driver pid from the session snapshot, bounded wait)
before deciding fallback; never fall back on a live-probe alone.
Clamp --session-deadline-s to a sane range (for example 5 to 60 s).
Bound the whole run (overlay plus observe plus session) against the
30 s target and record a breach in the envelope. Give the fallback
lock acquisition a timeout. Add a test with a SIGTERM-ignoring child
that spawns a separate-session grandchild, asserting both are dead
after attempt_session returns.

## A3. OVERLAY ACQUIRE CAN REPORT VISIBLE WHILE NO PILL EXISTS (BLOCK, overlay claim)

Severity: breaks the overlay gate. act-now can act invisibly after a
successful acquire.

Paths traced:

1. Daemon._show_label (overlay.py:237-254), daemon path: if
   _ensure_native() fails it returns silently; if native.command('show')
   fails it retries once, then logs 'native_command_failed' and returns
   silently. No boolean is returned, no exception is raised.
2. Daemon.apply_holders (overlay.py:256-289) calls _show_label and then
   returns {'visible': True, 'owner': ..., 'holders': ...}
   unconditionally on that path. The session path is the same: it calls
   session_label(label) and session_live() and ignores both return
   values, then returns visible True. Only the initial native spawn
   failure returns visible False; a show failure AFTER a live native
   object exists (process died between the poll and the command, stdin
   broken, liquid backend refusing) is swallowed and reported as
   visible.
3. first_action.acquire_overlay (first_action.py:68-89) trusts
   reply.get('visible') is True and proceeds. It never re-verifies the
   pill between acquire and the fallback desktop_act, up to 20 s plus
   later. The daemon _monitor polls every 2 s and would respawn, but a
   respawn that keeps failing is silent, and first_action never checks.
4. Concrete trigger: the native indicator binary exits or refuses the
   show command (liquid profile not ready, Wayland socket gone, the
   process killed between poll and command). apply_holders still
   answers visible True, act-now acts, the user sees no pill. This is
   the exact failure mode R3 was supposed to close.

Exact fix required: _show_label must return bool, apply_holders must
return visible False when the show ack fails (on either owner path),
and acquire_overlay must treat that as a refusal. In addition,
first_action must re-verify overlay visibility immediately before the
fallback desktop_act call (a status or sync round trip that requires a
live show ack) and refuse if the pill is not confirmed visible at that
moment, not only at acquire time.

## A4. PILL LEAK AND CONCURRENT SAME-AGENT RELEASE (BLOCK, overlay claim)

Severity: breaks the overlay claim in both directions: stale pill with
no live run, and no pill during a live run.

Paths traced:

1. Leak on acquire failure. acquire_overlay (first_action.py:68-89)
   calls add_holder FIRST, then _ensure_daemon, then _send_socket
   acquire. If _ensure_daemon raises, run() catches the RuntimeError,
   sets envelope error, returns 2, with overlay_acquired still False,
   so the finally block never releases. The holder stays in
   holders.json with no daemon and no live run. The next daemon that
   spawns will show a pill for a dead run. The test
   test_daemon_start_failure_refuses uses a fake whose add_holder
   already recorded the holder and never asserts the holders are empty
   afterwards, so the leak is untested.
2. Leak on kill. If act-now is SIGKILLed or SIGTERMEd, the finally
   block never runs and the holder stays. prune_dead_holders
   (overlay.py:126) exists and drops holders whose pid is dead, but it
   is called ONLY by cmd_status. It is never called by _ensure_daemon,
   by acquire, or by the daemon _monitor. A dead holder therefore keeps
   the pill up indefinitely (the daemon only exits after 3 empty polls,
   which never come while a stale holder exists). It self-heals only
   when the same agent runs again and overwrites its own entry.
3. Concurrent same-agent release. Holders are keyed by agent name only:
   holders[agent] = {...} (overlay.py:107). Two concurrent act-now runs
   with the default agent 'Muse' share one entry; the second overwrites
   the first pid and method. The first run to finish calls
   release_overlay, which removes the 'Muse' entry entirely
   (overlay.py remove_holder, first_action.py release_overlay), so the
   pill hides while the second run is still acting. The parent runs
   parallel lanes and the default agent is 'Muse' for every run, so
   this is reachable, not theoretical. release_overlay has the same
   flaw in its socket-failure fallback (remove_holder by agent).

Exact fix required: key holders by (agent, pid, run id), one entry per
live run, and release only the caller's own entry. Call
prune_dead_holders in _ensure_daemon and at the start of acquire, and
remove the just-added holder when acquire fails after add_holder.
Add tests for: acquire failure leaves no holder, a killed run leaves
no live holder after prune, and two concurrent same-agent runs keep
the pill until BOTH release.

## A5. FALLBACK PREFIGHT REFUSALS CRASH WITH A TRACEBACK (BLOCK, refusal claim)

Severity: breaks the "refuses loudly with a clear error" claim for the
most common refusal. The envelope carries no error at all on this path.

Paths traced:

1. run() (first_action.py:299-310) calls cu.desktop_act in the fallback
   branch with NO try/except around it. The only except in run() is the
   RuntimeError handler around acquire_overlay.
2. desktop_act raises PreflightRefusal (a ValueError subclass,
   cu.py:1330) before any action for: screen observation with type/key
   actions (cu.py:1475, the rehearsal run 1 case), bad actions or bad
   coordinates, stale or future-dated observation (cu.py:745,
   monotonic age outside 0..120), missing scope or window fields
   (validate_coordinate_metadata, cu.py:674). It raises RuntimeError
   for window-moved or monitor-changed (guard, desktop_act pre-batch),
   focus dispatch rejected, and window gone (focus, cu.py:536,
   window, cu.py:527). All of these propagate out of desktop_act.
3. The exception skips the after-capture block, reaches the finally,
   which prints an envelope with path 'fallback', ok False, completed 0
   and NO 'error' key, then the traceback goes to stderr and the
   process exits 1 via uncaught exception. The caller parsing the JSON
   envelope sees ok False with no reason and must read the traceback.
   Rehearsal run 1 ("REFUSED in 638 ms") was this path, not a clean
   refusal.
4. The rule doc says "act-now refuses loudly (exit 2)". That is wrong:
   exit 2 is overlay-refusal only. This refusal exits 1 via traceback.
   The session path handles the same refusal cleanly (cu.py main
   prints a JSON error, exit 1, no replay), so the two paths are
   inconsistent.

Exact fix required: wrap the fallback desktop_act call in
try/except (PreflightRefusal, ValueError, RuntimeError), write
str(exc) plus a concrete next step into envelope['error'], keep path
'fallback', return 1 cleanly with no traceback, and still attempt the
after-capture. Add a run-level test where FakeCu.desktop_act raises
PreflightRefusal and assert the envelope carries the error text and
the process returns 1 without raising.

## A6. STALE OBSERVATION: AGE BUDGET AND WEAK GATE (AMEND, speed and safety)

Severity: wastes runs and feeds A5; does not by itself cause a replay.

Paths traced:

1. _fresh_observation (first_action.py:191-211) accepts a given
   observation when it has id, image, monitor_box, created, and wall
   age under 120 s. It does not check backend, scope, window or
   window_bounds, monitor identity versus args.screen, image existence
   or hash, or capture identity. desktop_act validation catches most
   of those later, but as PreflightRefusal, which in the fallback path
   is the A5 crash.
2. Age budget: a 119 s old observation passes _fresh_observation, then
   the session attempt takes up to 20 s, so the observation is 139 s
   old at act time. validate_desktop_observation rejects monotonic age
   over 120 s (cu.py:745). Session path: wasted 20 s, act refusal, no
   replay, safe but failed. Fallback path: A5 traceback.
3. Future-dated created (clock skew, negative wall age) passes the
   wall check and fails validation the same way.
4. Window moved between observation and click: guard() raises
   RuntimeError 'expected window geometry changed' instead of returning
   a clean re-observe refusal, so the fallback path crashes (A5) while
   the session path returns a JSON error. Screen observations are
   handled better (screen_changed preflight returns a dict refusal).
   Inconsistent handling of the same staleness.

Exact fix required: require age plus session_deadline_s under 120 s in
_fresh_observation, or re-observe after a session failure before the
fallback act; validate the given meta scope, backend and window fields
up front and replace it with a fresh capture when invalid; convert
guard geometry and monitor errors into result-dict refusals instead of
raised RuntimeErrors, on both paths.

## A7. THE URLBAR FINDING IS OVERSTATED, NOT PROVEN (AMEND, evidence claim)

Severity: breaks a "proven" claim in the rule doc. Does not break the
safety claim: act-now delivery itself is exonerated.

What is verified: conversion and delivery are correct (see "What holds
up"). image_point (cu.py:973) through region, cursorpos exactly on
target, press and release correctly paired.

What is NOT proven: the rule doc says "This is a Zen UI finding, not
an act-now defect (act-now delivered the click exactly)". The evidence
is 2 attempts with identical target, identical coords (120,60),
identical sequence shape (Ctrl+N, then click, then type, then Enter).
No variation separates act-now delivery from Zen behavior:

- No hover dwell before the click. desktop_act's own G21 comment
  (cu.py, hover handling) records that some buttons only register a
  click after the pointer has hovered long enough for the hover state
  to land. The click path here does move() then IMMEDIATELY button 1,
  zero dwell. Run 4 waited 500 ms after Ctrl+N but the click itself
  still had zero dwell.
- No control: no click on a known-focusable field to show clicks DO
  focus elsewhere, no double-click, no click without the preceding
  Ctrl+N (new-tab settle race), no click on the urlbar text area versus
  its icon.
- Field identity was read off a screenshot, not from DOM or a11y, so
  the (120,60) point being the urlbar versus the sidebar search field
  is itself unverified.
- Note the generic hazard the batch design does not guard: after a
  click that does not focus, the following blind type goes wherever
  focus happens to be. desktop_act verifies cursor position, not focus.
  Harmless in this rehearsal, dangerous in general.

Exact fix required: downgrade the rule doc claim from proven to
hypothesis, and run the discriminating probes before calling it proven:
hover 100 ms then click; click a control text field; click the urlbar
without a preceding Ctrl+N; double-click. Record which probe changes
the outcome.

## A8. SESSION-PATH completed IS ASSERTED, NOT MEASURED (AMEND, reporting)

Severity: a false-success report on the session path. The envelope can
claim full completion for a batch that did not fully run.

Path traced: run() (first_action.py, session branch) sets ok True and
completed equal to len(actions) on rc 0 alone, without parsing the
session subprocess stdout, even though cu.py act prints its result
JSON (cu.py main prints compact_result for act). A session that exits
0 without running the batch, or with a partial completed count, is
reported as full success. The after-capture is not a substitute: it
shows pixels changed, not actions completed. test_session_path bakes
this in: the fake session returns empty stdout and the test asserts
completed 1.

Exact fix required: parse the act result JSON out of the session
stdout and take ok and completed from it; when it is absent or
inconsistent with rc, report completed as unknown, not len(actions),
and do not claim full completion. Add a test where the session exits
0 with a result JSON claiming completed 0 and assert the envelope does
not report full completion.

## A9. TESTS: HAPPY PATH WITH FAKES, DANGEROUS PATHS UNCOVERED (AMEND)

21 tests, all VM-only with fakes. What they cover: the happy session
path, the genuine guardian-failure fallback, act-failure-no-replay for
a NON-magic error string, timeout with live versus dead session at the
unit level, overlay visible versus not-visible, log append, fresh
versus stale observation at the wall-age level, session command shape.
What they do NOT cover, each mapped to an attack above:

1. No test feeds a POST-START failure carrying 'Expecting value' or
   'cursor guard' and asserts no replay (A1). Worse, the unit tests
   for is_session_start_failure assert True for those bare strings,
   baking the vulnerable behavior in as correct.
2. No run-level test where fallback desktop_act RAISES PreflightRefusal
   (A5). FakeCu.desktop_act always returns an ok dict.
3. No test that an acquire failure leaves no holder (A4). No test for
   a killed run or for prune_dead_holders ever being called.
4. No concurrency test: two same-agent runs, first release must not
   hide the pill for the second (A4).
5. No test with a SIGTERM-ignoring child or a separate-session
   grandchild for attempt_session (A2). test_timeout_kills_group uses
   sleep in the same group.
6. No test for a stale session.json making session_live read True or
   False at the wrong time (A2).
7. No test for _fresh_observation accepting a meta missing scope,
   backend or window fields (A6). FakeCu always returns a full meta.
8. No test that session-path completed comes from parsed stdout
   (A8). test_session_path asserts completed 1 on empty stdout.
9. No test for --session-deadline-s validation (0, negative, huge)
   (A2).
10. No test that the overlay is re-verified before the fallback act
    (A3). FakeOverlay always answers visible True.
11. No test for the whole-run time budget versus the 30 s target (A2).

Credit where due: the double-print fix IS regression-covered (tests
parse stdout as one JSON object).

## Required fixes for GO

All of these, with tests, before the fix is declared proven or made the
default live path. Do not land a partial set and call it GO.

1. Phase-aware replay classifier (A1): fall back only when output
   proves the driver never started (no 'registered' marker, anchored
   startup error). Post-start magic strings must return False. Tests
   for both post-start magic-string cases.
2. Catch fallback desktop_act exceptions into the envelope (A5):
   PreflightRefusal, ValueError, RuntimeError become envelope['error']
   plus a concrete next step, clean exit 1, no traceback, after-capture
   still attempted.
3. Per-run holder identity plus pruning (A4): key holders by
   (agent, pid, run id), release only the caller entry, prune dead
   holders on acquire, remove the just-added holder on acquire failure.
   Tests for leak-on-failure, prune, and concurrent same-agent runs.
4. Overlay show ack must propagate (A3): _show_label returns bool,
   apply_holders returns visible False on show failure, and
   first_action re-verifies the pill immediately before the fallback
   act. Test with a failing show command.
5. Honest completion and bounded time (A8, A2): parse session stdout
   for ok and completed; clamp the session deadline; bound the whole
   run against the 30 s target and record breaches; verify driver death
   (bounded wait) after a timeout before deciding fallback; timeout on
   the fallback lock.
6. Stale observation budget and gate (A6): age plus deadline under
   120 s, up-front scope and backend validation of a given observation,
   guard geometry errors as dict refusals.
7. Downgrade the urlbar claim and run the discriminating probes (A7).
8. Tests for every item above (A9 list), run green on the VM.

## Out of scope, noted but not charged

- The guardian itself (F1 owns the cursor-guard loading) and the
  Marionette slot re-break (F3 owns it) are not F2 defects and are not
  counted against this verdict.
- The overlay daemon wayland_env hyprland versus hypr directory
  mismatch (rule doc limits section) is recorded but not charged: the
  pill still works because the indicator needs WAYLAND_DISPLAY, not the
  signature, and this redteam did not reproduce a failure from it.
- The R6 re/__init__.py deletion root cause is solved (Y13r2 shim,
  VMFIX c16dd4e) and is not part of this verdict.
