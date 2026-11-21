# Independent review: F1 guardian fix, F2 act-now, F3b slot heal (todolist-push)

Reviewer: clone2, batch 6 task 2. Independent, no code written by this reviewer.
Review window: 00:51 to about 01:05 +07, 22/11/2026.
Branches: origin/todolist-push tip at worktree creation 8bdd5aa (Y13g round 2).
Method: read every code commit in the three streams, read the final code end
to end, ran the affected test suites in a clean worktree at /tmp/fteam/wt
(venv python + system dist-packages, the same command batch 5 used), ran the
full suite once in that worktree, checked every cited line number and
commit hash, and read the F1/F2/F3b logs plus their council and redteam files.
Nothing was committed or pushed by this review. No personal information.
No em dash or en dash in this file.

Naming warning: "F1" and "F2" here are the F-team workstream names
(F1 guardian fix, F2 act-now). They are NOT the batch 5 crawl findings
(crawl F1 = frozen A1 pilot, crawl F2 = full suite failures). The coverage
section at the end keeps the two uses apart.

## Summary table

| Item | Verdict | One line |
|---|---|---|
| F1 guardian fix (12 code commits) | SOUND, minor issues | Error naming, hyprglass gate, drain settle, wrapper; all its tests pass here |
| F2 act-now (first_action.py + overlay.py + cu.py wiring) | SOUND, minor issues | Session/fallback split is correct, D1 BLOCK fixed and re-reviewed GO |
| F2b live session-path proof | SOUND | Session path proven live, 12.262 s order-to-overlay, 5/5, envelope path session |
| F3b slot heal (log + evidence scripts, no production code) | SOUND, evidence only | Arm E reproduces the wedge, restart is the only fix; no council/redteam of its own |
| Batch 5 evidence bug 1 (SyntaxError) | FIXED on todolist-push and on main | F1 a152f31 ExitStack rewrite; fixed on main by 9171773 after this review (see dated note in Coverage) |
| Batch 5 evidence bug 2 (cu.py run shadowing) | FIXED on both branches | 22b0fa3, not an F-stream commit |
| Crawl F1 HIGH (frozen A1 pilot) | OPEN, untouched | No unblinder/A1 commit in the window |
| Crawl F2 HIGH (suite failures) | PARTIALLY ADDRESSED | Failures 14-16 down to 4 on todolist-push; wtype gap untouched |

No item is BROKEN. Nothing in these diffs needs to be reverted.

## F1 guardian fix: SOUND, minor issues

### What it changed (12 code commits, 5033c9d to 0246a69)

- scripts/cursor_session.py: supervise pipes the guardian stderr, drains it
  on a daemon thread into a deque (32, then 200), tees every line to our
  stderr, includes the tail (4000 chars, errors=replace) in startup and
  registration failures; settles the drain thread before reading the tail;
  mid-session guard death now terminates the driver and prints the cause;
  gates the session on hyprglass (liquid_available ready=False then
  ready=True) BEFORE creating the indicator, so a down or warming-up
  backend fails fast with a named cause instead of hanging in
  wait_for_profile; owner_lock message names plugin activation too.
- scripts/cursor_theme.py: guard_reply catches JSONDecodeError and
  UnicodeDecodeError, distinguishes truncated/corrupt JSON (starts with
  { or [) from a missing backend, redacts 32-hex tokens, strips control
  characters; missing socket directory or socket now raises a named
  RuntimeError instead of a raw FileNotFoundError.
- scripts/session_remote.py: BrokerError carries the guard cause.
- scripts/activate-session-backend.py (new, ab67173): lock-holding wrapper
  holding one owner lock across glass + guard activation, with verify.
- Tests: ExitStack rewrite of test_cleanup_exceptions_cannot_skip_restore
  (a152f31), FAKE hyprglass/configerrors answers, R3 gate test,
  missing-socket test, envelope assertion on stdout JSON, sync manifest
  regression test (0246a69).

### Verification done by this reviewer

- py_compile passes on all F1 files on todolist-push.
- Ran in the worktree via `unittest discover -s tests`:
  test_cursor_theme 35 tests OK (0.158 s); test_cursor_session 36 tests OK,
  skipped 1, 50.102 s; test_activate_session_backend 3 tests OK;
  test_sync_installed 9 tests OK. All match the F1 log's counts.
- Verified the call sites the wrapper depends on: activate-glass.py
  activate(library, abi, profile_sha256, env) and activate-cursor-guard.py
  activate(library, abi, env) match the wrapper's calls; indicator
  .liquid_available(env, *, ready=...) exists; plugin_inventory
  .setup_snapshot exists.
- Verified the start-failure raise sites first_action.py relies on:
  cursor_session.py:281 raises 'session guardian startup failed' before
  the driver is spawned, :293 raises 'driver registration failed' before
  the 'go' byte is written, and the driver only execs when
  os.read(gate,2)==b'go' (:337).
- Live evidence is log-only (cannot be reproduced from this VM):
  F1 live negative test 23:35 shows the new message in the envelope;
  F1a live activation verdict PASS (session 3b click, 0px error by
  cursorpos, clean teardown). The F1a log itself records that F1's
  negative test passed inline JSON to --actions, which the act CLI
  rejects (file paths only), so the negative test proves the guardian
  message, not the full command path. Disclosed in the F1a log, not hidden.
- F1's own council was AMEND x3 and redteam AMEND; round 2 addressed the
  required items (A3/R4 guard_reply rewrite, R5/R7 drain, A1/A2/R6/R8
  settle, R8/R11 mid-session death, R3 gate, D1/D2, E1/E2/E3). The F1 log
  records the two remaining durability follow-ups as tracked, not blocking.

### Issues (minor, none blocking)

1. Wrapper manifest handling is raw. read_manifest does
   json.loads(Path(manifest).read_text()) with no error handling: a
   missing manifest raises a bare FileNotFoundError and a malformed one a
   bare JSON error or KeyError. This matters because native/visuals.json
   is gitignored and generated at login (scripts/visuals.py), so it does
   not exist in a fresh checkout; the wrapper's default --manifest path
   fails there with an unhelpful traceback. The wrapper's own tests all
   pass a temp manifest, so the gap is untested.
2. BrokenPipeError acceptance weakens a test. b3fac91 accepts
   BrokenPipeError in the Guard close-race test, described as a
   pre-existing flake (about 5/95 runs). The comment discloses it, but
   the test now passes when the guard fails with a broken pipe instead
   of a clean failure. Test-only, disclosed, minor.
3. Durability follow-ups still open (recorded in the F1 log, not hidden):
   the login loader still fails silently (visuals-login.lua fires
   visuals.py to /dev/null, exit code never recorded), and the drift
   repair was a manual copy, not via refresh-visuals-manifest.py, so the
   next optics edit without a re-pin repeats the incident. The F1 log
   says plainly "the root cause is not durably fixed until that lands".
   The R3 gate fix (e7913d5) is in; the loader and re-pin workflow are not.
4. The F1 log's own note: test_cursor_session.py cannot compile on VM
   Python 3.12 was fixed on todolist-push by the ExitStack rewrite, but
   the F1 log text at that point still says it "does not compile".
   Stale log wording only; the code is fixed.

## F2 act-now: SOUND, minor issues

### What it changed

- scripts/first_action.py (new, a576e69, then council 1 BLOCK fix bb8f4e3
  and redteam fixes 268fcbf): overlay acquire first, session attempt with
  a 20 s hard deadline, fallback to the direct Pointer path ONLY on a
  proven session-start failure (parsed stdout JSON error starting with
  'session guardian startup failed' or 'driver registration failed');
  timeout never falls back; rc 0 alone never proves success (requires
  ok true or the completed-capture-error shape); overlay re-checked
  before the fallback; every path prints exactly one JSON envelope and
  one JSONL record; target_breached recorded when total exceeds 30 s.
- scripts/overlay.py (91895b3, 1c6344e, 4c32fc4): holders keyed by
  (agent, pid), per-run release, show returns a real ack (apply_holders
  returns visible False with 'pill show failed' on a failed show),
  prune_dead_holders called by _ensure_daemon and apply_holders,
  cmd_acquire removes the just-added holder on failure (D1 fix, with the
  label assignment inside the try).
- scripts/cu.py (8d1f775): act-now subcommand wired in. Verified here:
  `cu.py act-now --help` prints the parser.
- Tests: 46 tests in test_first_action.py, 12 function tests in
  test_overlay.py.

### Verification done by this reviewer

- py_compile passes on first_action.py, overlay.py, cu.py.
- Ran via `unittest discover -s tests`: test_first_action 46 tests OK
  (0.564 s); test_overlay 12 tests OK (0.010 s). Both counts reproduce
  the F2 log exactly. Note: `python -m unittest tests.test_overlay`
  (module form) fails to load on Python 3.12 because load_tests imports
  _function_test_support, a repo file under tests/ that is only on
  sys.path under discovery; under the repo's standard discovery command
  it works. I also ran all 12 overlay functions directly: 12 passed.
- D1 BLOCK (re-review, worker-f2-rereview.md): cmd_acquire leaked a
  holder with pid None on daemon/socket failure, unprunable. Fixed by
  1c6344e (remove on failure) and hardened by 4c32fc4 (label assignment
  inside the try), with tests 526919d and 1c08f8a. The D1 re-review
  (worker-f2-rereview-d1.md) verdict is GO. I re-ran the D1 test
  (test_cmd_acquire_failure_leaks_nothing) here: passes.
- The F2 log's cited numbers check out: improvements
  /worker-f2-silence-fix-log.md lines 25 and 29-45 contain the direct
  Pointer click "SUCCEEDS in 0.31 s" and the about 5.5 min breakdown,
  matching the evidence-check fix pass (the file exists at 2495382).
- The F2 re-review's per-item table checks out against the final code:
  B1 (timeout never falls back, first_action.py is_session_start_failure
  returns False on timeout), B2 (prefix classifier, raise sites verified
  above), B3 (no session_live probe on the fallback decision), A1
  (acquire failure removes the holder), A3 (envelope required for
  success), A5 (overlay re-checked before fallback, release failure
  recorded as release_error). Council 1 BLOCK, council 2 AMEND, council
  3 AMEND, redteam BLOCK were all addressed by bb8f4e3, 268fcbf, 91895b3
  and the D1 fix pass.
- F2b live session-path proof (worker-f2b-live-session-log.md,
  commit 115ae4d): pre-registered protocol, envelope path='session',
  ok=true, completed 5/5, order-to-overlay 12.262 s, under 30 s. This
  closes F2's open item (session path untested in rehearsal). The log
  honestly reports spawn-to-overlay 6m 56.4 s (setup/think time) as
  exceeding 30 s, and states the verdict number is the order-to-overlay
  from the act-now invocation, per protocol.

### Issues (minor, none blocking)

1. A-M2 (re-review amend, still present): 'status' reports holders, not
   the pill. overlay.py cmd_status (line 541) and the daemon 'status'
   handler (line 400) report 'visible': bool(holders). A stale holder
   makes status claim visible True with no pill. Act-now does not use
   status as a gate (it uses the sync round trip), so this is amend only.
2. A-M3 (re-review amend, still present): prune_dead_holders treats
   PermissionError as dead (overlay.py:163). A pid owned by another user
   exists but cannot be signalled, and would be pruned while live.
   Same-user in practice on this machine.
3. A-M4 (re-review amend, still present): the pill is re-checked
   immediately before the fallback acts, but not during desktop_act
   itself. If the daemon dies mid-batch, the tail acts with no pill.
   Needs a check inside desktop_act, outside act-now scope; recorded
   as a follow-up.
4. A-M5 (re-review amend, still present): a non-RuntimeError acquire
   failure returns exit 1 while a RuntimeError acquire failure returns
   2. Same refusal, inconsistent code. Cosmetic.
5. Stale line references in first_action.py: the docstring (D3) and the
   START_FAILURE_PREFIXES comment cite cursor_session.py:275 and :290,
   but the raise sites in the final file are :281 and :293. The
   re-review cited :281/:293 correctly. Doc nit only.
6. run() never-escapes contract has a narrow hole. The docstring says
   run() never lets an exception escape (council 1, A2), but _load_cu()
   and `import overlay` run BEFORE the try block, so an import failure
   escapes with no envelope. Narrow (both modules exist in the repo),
   but the contract as stated is not total.
7. The 30 s rule is still not demonstrated end to end from a user
   order including agent decision and observation time. first_action.py
   docstring D4 discloses this plainly (timings start at command start;
   the under-30 s rule is not yet demonstrated end to end), as council
   2 required. Disclosed, not a hidden gap.

## F3b slot heal: SOUND, evidence only

### What it changed

No production code. 7 commits, all log
(improvements/worker-f3b-restart-log.md) plus evidence scripts
(improvements/f3-evidence/arm_a.py, arm_b.py, arm_d.py, arm_e.py,
parse_sessionstore.py, probe_session.py, rclick.py). All 7 scripts pass
py_compile here.

### What the log shows

- Baseline 23:15: slot wedged since 22:56:12 (newSession HTTP 500
  'browserElement is null', 5th failure); Example Domain tab LIVE via
  BiDi (serves real DOM text), refuting the zombie-as-Example theory.
- Step 2: right-click Close Tab on the Example row (grounded coords,
  after one miss on the disabled row) closed Example; slot still wedged
  (7th failure). Step 2 exhausted.
- Step 3: restart #3 was NOT needed yet at this point. First restart
  (step 3 in the log's own numbering, 23:25:45): pkill -TERM on Zen PID
  426338, clean exit in 3 s. Relaunch attempt 1 failed ("no DISPLAY
  environment variable specified"); attempt 2 with the desktop env
  (XDG_RUNTIME_DIR, WAYLAND_DISPLAY, DBUS_SESSION_BUS_ADDRESS,
  HYPRLAND_INSTANCE_SIGNATURE) succeeded, new PID 479395, BiDi 9222 +
  Marionette 2828 LISTEN. Slot healed 23:26:40: session created, list
  returned 16 tabs. Re-list after 30 s still 16/16, stable; the 9
  about:blank entries in the first list resolved to the real tabs (they
  were still restoring). Website-open test PASS (example.com opened as a
  new tab, Welcome intact). Lesson recorded in the log: a bare SSH
  relaunch of a GUI app fails without the desktop env.
- Step 4, arms A to D: every atomic step from close3's sequence passes
  alone. Arm A (session DELETE with a BiDi-navigated tab current) PASS
  23:35:31 after two aborted runs (run 1 lost to an SSH break, run 2 died
  on a handle-scan hang at the 30 s timeout). Arm B (DELETE with a
  window/new blank tab current, no BiDi) PASS 23:36:16. Arm C (UI
  right-click Close Tab on the BiDi-navigated Example row, grounded
  coords) PASS 23:38:24. Arm D (close the BiDi-navigated Example tab via
  Marionette switch + DELETE /window, then session DELETE) PASS 23:41:01
  on attempt 2 (attempt 1 died on the same handle-scan hang, 10 s
  timeout, raw TimeoutError escaping zen_dom.py's ZenDomError-only
  handling). Probe after every arm: PROBE1 + PROBE2 CREATE OK.
- Step 4, Arm E: the full close3 reproduction FAILS, wedge reproduced
  23:42:12. Session 6304b1d8, sacrificial tab via window/new, closed
  Example + 3 blanks via switch + DELETE /window (DOOMED 4, AFTER 15),
  DELETE with the sacrificial current, exit 0. Probe: PROBE1 CREATE FAIL
  + PROBE2 CREATE FAIL, both HTTP 500 'browserElement is null', exit 1.
  This is the 3rd wedge (22:06, 22:56, about 23:42). Refined suspects
  inside E: (1) multiple DELETE /window closes in one session (D did
  one), (2) closing about:blank tabs via DELETE /window (never done in
  A-D), (3) the sacrificial tab surviving the session DELETE. The exact
  minimal combination is NOT yet isolated; a follow-up Arm F (one blank
  close via DELETE /window, then probe) would settle it, but each wedge
  costs a restart, so it is deferred to the cleanup-procedure owner.
- Non-restart fixes tried and failed: right-click Close Tab on the
  Example row (step 2, slot still wedged after 7th failure), BiDi
  browsingContext.close on the sacrificial tab 23:43:01 (closed ok, probe
  23:43:29 still wedged). Ctrl+W on a zombie row was NOT tried: no dead
  row was identified and the owner was active on the other workspace, so
  the log records it as not worth the disruption. RESTART IS THE ONLY FIX
  (3/3 times).
- Step 5, restart #3 (23:44:11, authorized, same procedure): pkill -TERM
  on PID 479395, relaunch with desktop env, new PID 496121. Probe 23:44:35:
  PROBE1 CREATE OK + PROBE2 CREATE OK, exit 0. Slot healed for the 3rd
  time by restart. Final verify 23:48:44: Marionette lists 17 tabs, all
  14 real tabs present by URL, 0 fixtures, no Example, no sacrificial.
  The 3 remaining blanks are the owner's pre-existing store blanks, left
  deliberately (BiDi cannot address lazy tabs, and Marionette DELETE
  /window risks re-wedging). Sessionstore after restart #3: 69 tabs,
  closedTabs 0, all 14 real tabs present, nothing lost. Final check
  23:51:12: probe again, both CREATEs OK, slot healed and stable at
  handover.

### Verdict detail

- SLOT HEALED: yes, by restart #3 (PID 496121). All 14 real tabs
  present, 0 fixtures, verified at 23:48:44 and again 23:51:12.
- TRIGGER: the full close3 sequence (Arm E) reproduces the wedge; every
  atomic step alone does not. Arms A/B/C/D PASS, Arm E FAILS. The trigger
  is the COMBINATION, with the three refined suspects above. The exact
  minimal combination is not isolated (Arm F deferred).
- ZOMBIE-AS-EXAMPLE: REFUTED. The Example tab was live and served DOM
  text at baseline; the dead element is invisible to BiDi in all three
  wedges.
- PROCEDURE RULE (from the log, for all future tab cleanup): NEVER close
  tabs via Marionette DELETE /window in bulk, and NEVER close about:blank
  tabs via Marionette at all. Close via BiDi browsingContext.close only
  (Council 2), or via UI right-click Close Tab (grounded coords, proven
  in Arm C). A session DELETE with any tab current is safe on its own
  (Arms A/B PASS).
- F1 SIGN-OFF: the slot is healed and stable, so F1's live activation
  test is unblocked (recorded in the log 23:41:28).

### Issues (minor, none blocking)

1. No council/redteam of its own for F3b. The F3 council files
   (worker-f3-council-1/2/3.md, worker-f3-redteam.md) review the F3
   Marionette slot log, not the F3b restart log
   (worker-f3b-restart-log.md). The F3b verdicts above therefore rest on
   this review and the log itself, with no independent F3b review. The
   F3b log's own council references are to F3's council, not a fresh
   round on F3b.
2. The minimal combination is not isolated. Arm F (one blank close via
   DELETE /window, then probe) is deferred because each wedge costs a
   restart. Until it runs, the rule "never close blanks via Marionette"
   is precautionary, not proven minimal.
3. New finding, separate from the wedge: Marionette tab-switch
   intermittently HANGS (Arm A run 2 at the 30 s timeout, Arm D attempt 1
   at the 10 s timeout; raw TimeoutError escapes zen_dom.py's
   ZenDomError-only handling). The log's own mitigation is to target
   handles by known index instead of scanning, and to catch TimeoutError
   per call. This is a Marionette reliability issue in its own right,
   not yet fixed.
4. Ctrl+W on a zombie row was not tried (no target identified, owner
   active on the other workspace). The "restart is the only fix" claim
   therefore covers the options actually tried, not every conceivable
   close path. Disclosed in the log, not hidden.

## Coverage: batch 5 cross-check

This section keeps the two uses of "F1" and "F2" apart, as the naming
warning at the top says: F1/F2/F3b above are the F-team workstreams;
crawl F1/F2 and evidence bugs 1/2 below are the batch 5 findings.

### Batch 5 evidence bug 1 (SyntaxError in test_cursor_session.py)

- FIXED on todolist-push by F1 commit a152f31 (ExitStack rewrite of
  test_cleanup_exceptions_cannot_skip_restore). Verified here:
  tests/test_cursor_session.py compiles on todolist-push at 8bdd5aa and
  the module runs 36 tests OK (skipped 1).
- Dated note, added during this fix pass (01:12 22/11): the summary
  table originally said "still broken on main". That was true during the
  review window (00:51 to about 01:05 +07 22/11), but batch 6 task 1
  fixed tests/test_cursor_session.py on main in commit 9171773 during
  the same window, and PR 1 has since merged (d322cd7). Verified now:
  `git merge-base --is-ancestor 9171773 origin/main` is yes, and
  `python3 -m py_compile tests/test_cursor_session.py` passes on
  current main. Bug 1 is now fixed on both branches. The table row above
  was corrected to match.

### Batch 5 evidence bug 2 (cu.py run shadowing)

- FIXED on both branches by 22b0fa3 ("fix: keep doctor probe runner
  callable"), not an F-stream commit. Verified in batch 6 task 1 with a
  before/after run of DoctorCliTests: 5 failures before the fix with the
  exact "'ArgumentParser' object is not callable" error, 13/13 pass
  after. Closed.

### Crawl F1 HIGH (frozen A1 pilot)

- OPEN, untouched. No unblinder or A1-pilot commit on todolist-push
  since 16:00 UTC 21/11 (checked by git log grep for unblinder and
  "A1 pilot" over that range, both empty). The frozen pilot's 3 blockers,
  13 major and 12 minor holes from the batch 5 crawl stand unaddressed
  by the F-team work.

### Crawl F2 HIGH (full suite failures)

- PARTIALLY ADDRESSED. Full suite run by this reviewer in the clean
  worktree at todolist-push tip 8bdd5aa, preserved log
  /tmp/fteam/full_suite_todolist.log: "Ran 1634 tests in 191.906s,
  FAILED (failures=4, errors=68, skipped=17)". Failures fell from 14-16
  on main (batch 5) to 4 on todolist-push, and the test count grew from
  1494 to 1634 as the F-team added tests. Error breakdown, read from
  the log itself:
  - 2 setUpClass errors: test_cursor_file.CursorFileTests (g++ 13.3.0
    does not recognize '-std=c++26', log line 90) and
    test_wtype_native.WtypeNativeTests (log line 1223).
  - The bulk of the 68 errors are the missing wtype binary: "wtype"
    appears 267 times in the log, and the two envelope failures report
    "private wtype helper is missing: /tmp/fteam/wt/native/wtype".
    The wtype setup gap is untouched: native/wtype was never built in
    the worktree.
  - 1 failure in test_tc02_controller (tesseract unavailable, "tesseract
    is unavailable; refusing to assume text presence").
  - 1 failure in test_cli_exit_codes (leftover session guardian in the
    full run). Verified during this fix pass: the same test passes in
    isolation (discovery form, 5 tests OK including test_cli_exit_codes
    in 0.111 s), so it is order-dependent, not a deterministic code bug.
  - The 2 remaining failures are the two envelope tests in
    test_session_driver (primary and restore failure), both failing
    only because the wtype helper is missing, so they are the same
    wtype gap, not separate defects.
- Conclusion: the suite is healthier on todolist-push (4 failures vs
  14-16), but the dominant remaining cause is the same unbuilt wtype
  binary the batch 5 evidence check already proved, plus the
  test_cursor_file g++ flag and the tesseract gap. None of those three
  was addressed by the F-team work.

## Conclusion

F1 SOUND, F2 SOUND, F2b SOUND, F3b SOUND (evidence only). No item is
BROKEN and nothing needs to be reverted. The minor issues listed under
each stream are follow-ups, not blockers. On the batch 5 cross-check:
both evidence bugs are now fixed on both branches (bug 1 by a152f31 on
todolist-push and by 9171773 on main), crawl F1 HIGH is untouched and
still open, and crawl F2 HIGH is partially addressed (failures 14-16
down to 4) with the wtype binary gap still dominant.
