# Batch 10 task 2: AMEND4 independent re-verification

Date: 2026-11-22. All times UTC. Work done on this machine (clone2 VM).
Code under test: origin/todolist-push tip 48c6aee, in a scratch worktree
(~/workspace/tools/amend4/wt). The AMEND4 code is not on main, so the
verification ran against the todolist-push tip, not main. Baseline:
origin/todolist-push 9bcfb04 (AMEND3 tip), worktree ~/workspace/tools/amend4/wt-amend3.

Command, every run: `PYTHONPATH=/usr/lib/python3/dist-packages
~/workspace/tools/venv/bin/python -m unittest discover -s tests -p 'test_*.py'`
(venv python plus system dist-packages, the established suite command).

## Verdict

AMEND4 as landed does NOT pass the full suite on this machine: 1927 tests,
20 failures, 5 errors, 17 skipped. But 17 of the 25 problem tests share one
cause that is not a production regression: stale test doubles. With that
single cause fixed in a diagnostic probe, the suite is 1927 tests,
5 failures, 3 errors. The 5 remaining failures and 1 remaining error are
the 5 RT2 proof tests F2, F3, F4, F5, F6. Of those, F6 is openly admitted
left failing in the item 7 commit body, F2 and F3 are defective or obsolete
as written (judged independently below), F4 tests the helper fallback
rather than the fixed production path, and F5 is a TRUE negative: the
unwired path still verifies wrong-field text. Item 12 is VERIFIED:
the 4 new after-scope regression tests exist, pass, and fail first on
the old code.

## Numbers, all runs on this machine

| Run | Code | Tests | Failures | Errors | Skipped | Suite time |
| --- | --- | --- | --- | --- | --- | --- |
| Baseline A | amend3 tip 9bcfb04, incomplete checkout (no build artifacts) | 1839 | 1 | 3 | 17 | 172.476 s |
| Baseline B | amend3 tip 9bcfb04, complete checkout | 1862 | 2 | 2 | 17 | 189.229 s |
| AMEND4 run 1 | tip 48c6aee, no build artifacts | 1904 | 21 | 240 | 17 | 169.371 s |
| AMEND4 run 2 | tip 48c6aee, wtype binary restored | 1904 | 20 | 6 | 17 | 170.065 s |
| AMEND4 run 3 | tip 48c6aee, diagnostic probe (test doubles patched) | 1904 | 5 | 4 | 17 | 172.712 s |
| AMEND4 run 4 | tip 48c6aee, complete checkout + probe | 1927 | 5 | 3 | 17 | 176.973 s |
| AMEND4 run 5 | tip 48c6aee, complete checkout, as landed | 1927 | 20 | 5 | 17 | 211.925 s |

Wall windows: baseline A 2026-11-21T23:58:15Z to 2026-11-22T00:01:09Z;
baseline B 00:17:01Z to 00:20:11Z; run 2 23:55:02Z to 23:57:53Z; run 4
00:09:58Z to 00:12:56Z; run 5 00:13:09Z to 00:16:43Z. Elapsed times vary
with VM contention (run 5 took 211.9 s against run 4 at 177.0 s on the
same code except the probe patch); wall times are as measured.

Run 1 is INVALID and is reported only to show the trap: a fresh worktree
lacks the gitignored build artifacts (native/wtype binary and the
wayland-scanner generated native/keyboard-protocol.c/.h), so 240 errors
were the missing binary, not the code. Runs 2 to 5 use the artifacts a
normal checkout has (binary copied from the main checkout, protocol
files generated with wayland-scanner exactly as scripts/build.py does).

Count check: 1862 baseline + 49 (RT2 module as loaded) + 16 (AMEND4 new
test methods, counted per item commit: item 2: 2, item 3: 3, items 5-6: 3,
item 7: 1, item 9: 3, item 12: 4) = 1927. Exact.

## The AMEND4 log has no full-suite numbers

There is no AMEND4 work log file on todolist-push. The "log" is the 12
item commits themselves. Items 3, 4 and 5-6 have empty bodies (subject
only). The subjects and bodies that say "proof in log", "symmetry proof
in log" and "see the AMEND4 log" point to a log file that does not exist
in the repo (grep over the branch finds only the driver log and the
probe-p3 log mentioning "AMEND4 log"). So there is no AMEND4-claimed
full-suite number to compare against, and the "RT2 test defective"
proofs for F2, F3, F4 and F5 are not verifiable from any repo artifact.
I judged each test myself below, from the test source and the code.

The nearest claimed numbers are AMEND3's, from
improvements/worker-click3-amend3-log.md: 1855 tests, 0 failures,
errors=4, skipped=17. That claim does NOT reproduce on this machine:
baseline B at the same commit gives 1862 tests, 2 failures, 2 errors,
17 skipped. The 7-test count gap is unattributed (the laptop collected
fewer tests than this machine at the same commit, cause unknown from
the artifacts). The failure set is stable except one flaky test, see
below.

## Baseline problems (pre-existing, also at the AMEND3 tip)

- test_tc02_controller: 1 failure
  (test_typed_text_check_fails_when_fragment_is_absent) and 1 error
  (test_typed_text_check_passes_when_fragment_is_visible), in both
  baseline runs and in every AMEND4 run. Pre-existing on this machine.
- test_cursor_file setUpClass error: g++ 13.3.0 does not recognize
  -std=c++26. Pre-existing environment limit, also on main.
- test_cli_exit_codes (test_phase3_cleanup.py): FAILED in baseline B
  ("session guardian still running: pid 46454") but PASSED in baseline
  A and in all four AMEND4-tip runs. Flaky: a test leaves a session
  guardian running and the cleanup check trips on it. Order and timing
  dependent, not an AMEND4 regression.
- test_wtype_native setUpClass error in the incomplete-checkout runs:
  the harness compile needs native/keyboard-protocol.c, a build
  artifact. Gone once the artifacts are present (23 tests, all pass).

## The 17 session failures: one cause, stale test doubles

As landed, 17 problem tests sit in test_session_continuation.py and
test_session_policy.py (15 failures, 2 errors). All 17 share one root
cause. AMEND4 item 4 changed the CLI act call site (scripts/cu.py:2986)
and CodeExecBackend.act (scripts/cu.py:2649) to ALWAYS pass
type_x_ranges= and type_y_ranges= to desktop_act. The tests patch
cu.desktop_act with a fake, act_boundary, defined in
test_session_continuation.py:110 and test_session_policy.py:101, whose
signature is frozen at the old call contract: it accepts only
after_capture, observation_path and expected_terminal_window, and
forwards only those three to the real desktop_act. Every relay test
that reaches the CLI act path now raises TypeError inside the fake:
"live.<locals>.act_boundary() got an unexpected keyword argument
'type_x_ranges'". The session driver catches that as a fatal error,
so the tests fail with exit code 1 or with the TypeError text where
they expected a domain error.

Proof, by a diagnostic probe only (not committed): I patched both
act_boundary fakes in the scratch worktree to accept type_x_ranges
and type_y_ranges and forward them to the real desktop_act. All 28
tests in the two modules then pass, and the full discover (run 4)
goes to 1927 tests, 5 failures, 3 errors. The probe was reverted
afterward; the worktree is back to the landed code.

Production desktop_act DOES accept the kwargs (added by item 3,
scripts/cu.py:1635), so in the real unpatched system the calls work.
This is a test-double staleness, not a production regression. But the
suite as landed is red because of it, and the AMEND4 fix pass did not
update its own test doubles. The fix is a small test-only change
(accept and forward the two kwargs in both fakes); it is not committed
here, it belongs to the AMEND4 owner or a follow-up.

## RT proof tests: 10 of 15 pass, 5 do not

tests/test_click3_redteam2.py has 17 own test methods: 15 failing
proofs plus 2 passing controls, per improvements/worker-click3-rtr2-log.md
lines 113 and 426 (the assignment's "15 RT proof tests" are the 15
proofs). As loaded the module runs 49 tests in 0.941 s (the 17 own
tests plus 32 inherited from DesktopPreflight, because
R3aUnwiredPathTests subclasses it). Standalone run at the AMEND4 tip:
49 tests, 4 failures, 1 error. The 2 controls pass. Of the 15 proofs,
10 pass and 5 do not: F2, F3, F4, F5, F6.

- F1 (set_value newline, item 8): PASS.
  test_set_value_newline_text_fails_verification passes. (F1 was also
  confirmed live separately by fcc on Chromium 130 headless.)
- F2 (stale window origin, items 5-6): FAIL.
  test_stale_window_origin_accepted_silently. My judgment: the test is
  self-contradictory as written and can never pass under any fix. It
  asserts the returned stale origin equals [340, 108] AND that the
  point derived from it is within 10 px of the true point (it is
  1271 px away). If viewport_origin raised, the test would error at
  the call; if it returned the true origin [2749, 922], the first
  assert would fail. The test needs a rewrite (assert refusal, or
  assert the true origin). AMEND4's "defective" claim stands on my
  reading. The "proof in log" for it is not in the repo.
- F3 (region fallback, items 5-6): ERROR. test_region_fallback_readmits_raw_mozinner
  calls dom_act.ground_input with a meta that has no window_bounds.
  Items 5-6 made ground_input refuse without window_bounds, so the
  test now errors with DomActError ("meta needs window_bounds for the
  window origin"). The test asserts the old fallback contract; under
  the new refuse rule it cannot pass as written. It is obsolete and
  needs a rewrite to assert refusal. Whether refusal is the right fix
  is the adjudication's call, not this test's.
- F4 (band stacked fields, item 3): FAIL.
  test_band_stacked_fields_low_click_with_x_range_must_not_verify calls
  cu._input_line_changed directly with x_range but no y_range, and the
  helper's documented fallback with no y_range is click-anchored, so
  the lower field's text still verifies the upper field. Item 3 wired
  y_range through the production path (desktop_act, dom_act
  grounded_y_range, first_action fallback, CLI act), so in production
  the band is field-anchored when grounding succeeds. The test does
  not exercise the production path, so its failure does not refute
  item 3. But the fallback is real and still reachable when grounding
  fails (y_range None), and the helper's docstring says so. The test
  is misleading as a proof of a production flaw; it needs a
  y_range-passing variant to test the fix. The "symmetry proof" for
  calling it defective is not in any repo file.
- F5 (unwired path, item 4): FAIL, and this one is a TRUE negative.
  test_band_wrong_field_unwired_path_reports_ok runs a click+type
  batch with no DOM session and expects the wrong-field pixels not to
  verify. Item 4 threads the ranges only when a DOM session and
  selector exist; without them the batch keeps the full-width band
  by design ("best-effort"), and the result is ok True with
  type_verified True on the input-line-band basis. The test demands
  fail-closed on the unwired path; the implementation chose
  best-effort. That is a design dispute, not a test defect, and the
  test failure is real evidence the fail-closed requirement is unmet
  on this path. Whether best-effort is acceptable is for the
  adjudication round to decide. The "proof in log" for calling it
  defective is not in the repo.
- F6 (typed flag forgeable, item 7): FAIL, openly admitted.
  test_typed_flag_forgeable_by_page_script. Item 7's commit body says:
  "F6 is left failing for adjudication (its forge line assumes the
  removed window property and its value assertion conflates the field
  value with the verify outcome, see the AMEND4 log)". The new design
  has no window property to forge (closure plus locked getter), so the
  test's node harness errors (window.__agentCuTyped is undefined) and
  the test fails. The test is obsolete for the new design and needs a
  rewrite. The admission is in the commit body; the cited AMEND4 log
  does not exist in the repo.
- F7 (typed flag sticky, item 7): PASS. Both the node and the python
  sticky tests pass.
- F8, F11, F12, F13 (gate traversal and iframe reads, item 2): PASS.
  All three iframe tests pass (nested iframe, shadow root, harvest).
- F9, F10 (geometry, item 1): PASS. Both geometry tests pass.
- Item 9 (supply-chain range wiring, C2 A3): PASS. The three new
  tests pass as part of the suite (no failures in test_dom_act or
  test_first_action outside item 12, which is covered below).
- Item 10 (snapshot test, C1 G4): PASS. No failures in the snapshot
  path; cdp_snapshot.mjs passes per the item commit.
- Item 11 (design-doc fixes, C3 G3/G4): docs only, no code. The doc
  change is in improvements/worker-coord-click2-log.md, 4 insertions.

## Item 12: VERIFIED

The fix matches the assignment description, checked against the code
(scripts/first_action.py at cbab398):

- _scope_after (new helper): prefers the action result's after when
  it is a dict whose scope matches the input observation's scope
  (desktop_act already captures in the input scope, on the session
  path from the session stdout and on the fallback path from the
  direct result); otherwise, for a window-scope input, a fresh
  capture in the input scope via cu.observe; a screen-scope input
  reuses the screen capture, which IS its scope-matching after.
- The envelope carries BOTH captures: 'after' is the scope-matching
  capture (chainable) and 'after_screen' is the full-monitor capture,
  for verification only, documented non-chainable in the code comment.
- The scope check runs BEFORE the overlay attempt: a key or type
  batch given a screen-scope observation is refused before the
  overlay acquire and the session attempt (the 998 ms CL1-SWEEP
  waste), with the session never attempted.

The new regression test for after-scope matching EXISTS and PASSES:
four tests in tests/test_first_action.py, class TestRun, all pass at
the tip (run in 0.008 s):

- test_session_after_is_scope_matching_not_screen
- test_fallback_after_is_scope_matching_not_screen
- test_after_without_result_after_captures_fresh_window
- test_screen_observation_key_batch_refused_before_overlay

Failing-first verified: the same four tests, run against the
pre-item-12 code (worktree at cbab398^, which is 5f30908, with only
the new test file copied in), all four FAIL. The first three fail
because env['after']['id'] is 'a1b2c3d4e5f6' (the screen capture)
instead of the scope-matching ids ('sess-after-1', 'after-1',
'win-after-1'). The fourth fails because attempt_session WAS called
on the old code (the scope check did not exist yet). The claim "all
failing-first on the old code" in the item 12 commit body holds.

## What remains, for the coordinator

1. Update the two act_boundary test doubles (test_session_continuation.py:110,
   test_session_policy.py:101) to accept and forward type_x_ranges and
   type_y_ranges. Test-only change, verified by probe to clear all 17
   session problems. Uncommitted here.
2. Decide F5: fail-closed on the unwired path (the test's requirement)
   or best-effort (item 4's choice). This is the one remaining true
   negative in the RT proofs.
3. Rewrite the obsolete RT2 proof tests F2, F3, F6 (and add a
   y_range-passing variant for F4) to match the landed contracts, or
   rule them defective in the adjudication. F6 is already flagged for
   adjudication in the item 7 commit body.
4. The AMEND4 "proof in log" references point to a log file that does
   not exist in the repo. If the proofs exist elsewhere, they need to
   be put in the repo, or the "defective" verdicts rest on the
   independent judgments above, not on the cited log.
5. Pre-existing, not AMEND4: the tc02 typed-text-check pair
   (1 failure, 1 error on this machine), the g++ -std=c++26 limit in
   test_cursor_file, and the flaky test_cli_exit_codes guardian
   leftover. None of these is an AMEND4 regression.

## Logs preserved

~/workspace/tools/amend4/: discover.log (run 1, invalid), discover2.log
(run 2), discover3.log (run 3, probe), discover4.log (run 4),
discover5.log (run 5, as landed), discover-amend3.log (baseline A),
discover-amend3b.log (baseline B), rt2.log (RT2 standalone).
Worktrees: ~/workspace/tools/amend4/wt (tip 48c6aee, reverted to landed
code after the probe), ~/workspace/tools/amend4/wt-amend3 (9bcfb04),
~/workspace/tools/amend4/wt-pre12 (5f30908, failing-first check).
