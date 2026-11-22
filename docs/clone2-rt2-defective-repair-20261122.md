# Batch 11 task 1: RT2 defective-test repair, independent verification

Agent: clone2. Work window 2026-11-22 08:51-09:00 +07 (01:51-02:00 UTC).
Tip verified: origin/todolist-push 65a2df6 ("docs: COORD-CLICK-4 log
start, batch 11 + 3 workers spawned, Codex launch deferred to after P3").
Worktrees under ~/workspace/tools/rt2-repair (wt at 65a2df6, wt-preB at
ed2d559). Runner everywhere: system python3 from tests/,
PYTHONPATH=../scripts:. python3 -m unittest. No em dash or en dash.
No personal information.

## Headline: the assignment's premise is stale, the repair already landed

The 5 defective RT2 proof tests (F2, F3, F4, F5-behavior, F6) were
already repaired on todolist-push by the coordinator's own TESTREPAIR
lane, commit 43b27a1 ("TESTREPAIR-B: repair the 5 defective RT2 proof
tests (F2 assertRaises, F3 split, F4 y_range, F5 wired-path rewrite,
F6 guarded forge + value fix)"), landed 2026-11-22 01:01:47 UTC
(08:01:47 +07), about 46 minutes before the batch 11 assignment
by commit timestamps (01:01:54 UTC to 01:47:32 UTC; 48 minutes
against the stated 08:50 assignment time in coord/clone2.md)
(08:50 +07, commit 495cfc6). The repair diff touches only
tests/test_click3_redteam2.py (110 insertions, 24 deletions, 1 file).

I did NOT re-edit the tests. Re-editing an already-correct repair
just to have a change would be manufacturing work. What I did instead,
independently, from primary sources:

1. Failing-first: ran the 5 tests on the parent commit ed2d559
   ("docs: Y1B-RPC-LAND log, landing record + 81-test verification"),
   the tree immediately before TESTREPAIR-B. All 5 fail there.
2. Diff check: read the full TESTREPAIR-B diff and checked each hunk
   against the exact repairs documented in the DOT 9 task 1 review
   (docs/clone2-council-round3-amend4-20261122.md, 7aeea01 + fix
   9427eeb). Every repair matches the documented one.
3. Post-fix runs at the current tip 65a2df6: the 5 tests, the full
   RT2 suite, and a full discover. All pass.

## Verdict: 14/14 behavioral proof tests pass, plus 1 source-presence pin

- The 5 repaired tests: Ran 5, OK at 65a2df6 (0.205 s).
- Full RT2 suite (tests/test_click3_redteam2.py): Ran 51 tests in
  1.199 s, OK. 51 = 49 + 1 F3 split test
  (test_stale_window_origin_refused_at_ground_time) + 1 maxlength
  test (test_set_value_maxlength_uses_sanitized_length, TESTREPAIR-C8).
  All 14 behavioral proof tests pass by name (listed in the
  per-test section), plus the source-presence pin test, the 2
  controls, the F3 sibling, the maxlength test, and the 32
  harness tests.
- Full discover at 65a2df6: Ran 1974 tests in 182.514 s, FAILED
  (failures=1, errors=5, skipped=17). The only failure and 1 of the
  5 errors are the tc02 tesseract pair (environmental: "tesseract is
  unavailable" on this VM, identical to every earlier run). The other
  4 errors are the pre-existing laptop-only ones (test_a11y_skeleton
  import, test_cursor_file setUpClass, test_perf_evidence x2). Zero
  RT2 problems remain. Full discover failure count is load-sensitive:
  an independent re-run under load gave failures=3 (the same tc02
  failure plus 2 test_ime_cleanup timeout failures that pass 14/14
  in isolation); zero RT2 problems in either run. I verified the
  isolation half myself: test_ime_cleanup Ran 14, OK in my own
  worktree at 65a2df6. My own 29083cd re-run under load likewise
  flaked one ime test (the SIGHUP case) for failures=4. Zero
  test_code_exec / test_codemode problems:
  Ran 81 tests, OK (13.277 s), so the 8 Y1b problems seen at 17fdb9b
  are gone at this tip; which commit cleared them is batch 11 task
  3's question, not this task's.
- The discover count grew 1920 (at 0668327) to 1974 at 29083cd,
  where it already stood (my full discover at 29083cd: Ran 1974
  in 440.595 s, failures=4, errors=5, skipped=17; the 2 non-tc02
  failures are test_browser_image, fixed by e83b72d; the 4th
  failure is a load-flaky test_ime_cleanup SIGHUP case, and
  council 1's run at the same commit gave failures=3, errors=6,
  the same total of 9 problem tests, none RT2). At 65a2df6 it is
  still 1974, with failures=1 and errors=5. Against the 0668327
  baseline the failure count fell 5 to 1 and the error count 6 to
  5, entirely from the 5 repaired RT2 tests.

## Per-test evidence

### F2 test_region_fallback_readmits_raw_mozinner

- Failing-first (ed2d559): ERROR. ground_input raises DomActError
  (meta needs window_bounds..., scripts/dom_act.py:67, via
  ground_input at line 182) because the meta has no window_bounds,
  so the test, which has no assertRaises, errors before its
  assertions run. Log: ~/workspace/tools/rt2-repair/preB-five.log,
  lines 11-19.
- Repair in 43b27a1: the old ground + two assertions are replaced by
  `with self.assertRaises(dom_act.DomActError):
  dom_act.ground_input(session, meta, '#msg-input')`, with a comment
  stating the fix refuses a bounds-less meta and the true origin
  [2749, 922] is not derivable from this meta. This is exactly the
  documented repair ("assert the refusal").
- Post-fix (65a2df6): ok.

### F3 test_stale_window_origin_accepted_silently

- Failing-first (ed2d559): FAIL. The test asserts stale == [340, 108]
  AND the mapped point within 10 px of the true point; the mapped
  point is (323.0, 620.25), the true point (1527.5, 1027.25), 1271.4
  px apart, so no return value satisfies both.
- Repair in 43b27a1: split in two. The original test now documents
  the stale value only: it keeps stale == [340, 108] and asserts
  dist > 1000 (the 1271 px gap as evidence the direct call cannot
  know the window moved). The new sibling test
  test_stale_window_origin_refused_at_ground_time tests the
  ground-time refusal: FakeDomSession with live_origin [2600, 914]
  against G30_META origin [2533, 914], assertRaises DomActError
  containing 'moved'. This is the documented repair ("rewrite to
  test the ground-time refusal via ground_input"), with the
  documentation half kept as a separate test instead of deleted.
  Implemented as a split: the refusal half is the new sibling test
  test_stale_window_origin_refused_at_ground_time, the original is
  retained as characterization documenting the direct-call
  limitation. Caveat: the retained original test now pins current
  direct-call behavior (asserts dist > 1000, i.e. the stale mapping
  stays 1271 px off), so it would fail/error if viewport_origin
  were ever fixed to refuse or re-read at that layer, and its
  assertion message at tests/test_click3_redteam2.py:311-313 ("a
  stale window origin must be refused, not returned as if true")
  contradicts its assertion, since the test passes precisely because
  the stale origin IS returned. OPEN follow-up for the
  coordinator's lane: fix that assertion message; the test file is
  not edited in this fix pass.
- Post-fix (65a2df6): both tests ok.

### F4 test_band_stacked_fields_low_click_with_x_range_must_not_verify

- Failing-first (ed2d559): FAIL. Pixels at y=126 verify through the
  symmetric anchor +- 12 band around anchor 118, the same band that
  must include y=110.
- Repair in 43b27a1: y_range=(100, 120) added to the
  _input_line_changed call, exactly the documented repair, with a
  comment explaining the symmetry.
- Post-fix (65a2df6): ok. The positive control
  test_band_text_inside_target_field_still_verifies still passes,
  so the band is not blinded.

### F5-behavior test_band_wrong_field_unwired_path_reports_ok

- Failing-first (ed2d559): FAIL. Direct desktop_act call with no
  ranges verifies wrong-field pixels at x 0..11, as documented.
- Repair in 43b27a1: rewritten in two halves, exactly as the
  documented repair prescribes ("rewrite to exercise a wired
  path"). Half 1 proves the wiring: a desktop_act spy records that
  CodeExecBackend.act threads the grounded ranges of the target
  field ([12.0, 20.0] x [8.0, 12.0]) to desktop_act, asserted
  exactly. Half 2 proves the behavior: a direct desktop_act call
  with THOSE ranges (taken from the spy, not hardcoded) and no
  type_check hook must not verify wrong-field pixels at x 0..11,
  while right-field pixels at x 12..17 still verify, so the ranges
  narrow the band instead of blinding it. The test name is kept so
  the round-2/3 review references still resolve.
- The "or" branch (band-only unverified without ranges) is NOT
  adopted, as instructed: the TESTREPAIR-B comment states this
  explicitly, and the control test
  test_click_type_text_in_input_line_verifies
  (tests/test_type_verification.py:120) still passes at this tip
  (verified: Ran 1 test, OK).
- Post-fix (65a2df6): ok.
- Dissent, carried forward: the batch 10 task 2 re-verification
  judged this test a TRUE negative (a design dispute, fail-closed
  vs best-effort); the DOT 9 task 1 review judged it defective at
  the desktop_act layer. This verification agrees with the DOT 9
  judgment at the desktop_act layer and confirms the repair
  implements it. The unwired-path residual stands unchanged: the
  CodeExec path remains unwired by construction (allowlist exposes
  no ZenSession) and the CLI path remains unwired without
  --dom-selector, so after this repair no RT2 test asserts the
  wrong-field outcome on the unwired path; only the source-level
  pin test test_codeexec_and_cli_act_paths_never_supply_x_ranges
  remains for that. (That pin test is source-presence only and
  vacuous, see the proof-test count note below; it is not counted
  as a behavioral proof.) The fail-closed vs best-effort choice is
  still open and left to adjudication. The coordinator's parallel
  council lane (commit a14223d) records F4/F5/F6 divergence
  decisions in an addendum; I did not read it and do not copy it.

### F6 test_typed_flag_forgeable_by_page_script

- Failing-first (ed2d559): FAIL. The forge line
  `window.__agentCuTyped['#msg-input'] = true;` throws TypeError
  (Cannot set properties of undefined, setting '#msg-input')
  because the arm no longer creates window.__agentCuTyped, so the
  test dies in _run_node before its assertions run. The node stderr
  is in ~/workspace/tools/rt2-repair/preB-five.log.
- Repair in 43b27a1: the forge line is guarded in try/catch, and
  the value assertion is replaced: assertNotEqual(value, 'hello')
  becomes assertEqual(value, 'hello'), with a comment stating the
  field's value IS 'hello' (the page script set it) and the flag is
  the discriminator, not the value. This is exactly the documented
  repair ("guard the forge line and drop or replace the value
  assertion"). The flag assertion (assertFalse) is unchanged.
- Post-fix (65a2df6): ok. The guarded-run result is
  {"armed":true,"flag":false,"value":"hello"}, matching the DOT 9
  review's own guarded node run exactly.

## The 14 behavioral proof tests, all passing at 65a2df6

F1 test_set_value_newline_text_fails_verification, F2
test_region_fallback_readmits_raw_mozinner, F3
test_stale_window_origin_accepted_silently, F4
test_band_stacked_fields_low_click_with_x_range_must_not_verify,
F5-behavior test_band_wrong_field_unwired_path_reports_ok, F6
test_typed_flag_forgeable_by_page_script, F7-node
test_typed_flag_sticky_across_js_set_value, F7-python
test_typed_flag_sticky_python_level, F8
test_arm_typed_flag_misses_iframe_targets, F9
test_viewport_origin_factor2_small_window_false_refusal, F10
test_geometry_check_accepts_factor_forgotten_origin, F11
test_field_value_misses_iframe_in_shadow_root, F12
test_harvest_misses_iframe_targets, F13
test_field_value_misses_nested_iframe. Each confirmed ok in
~/workspace/tools/rt2-repair/rt2-verbose.log; the full suite is
Ran 51, OK.

Plus 1 source-presence pin, not counted as a behavioral proof:
F5-source test_codeexec_and_cli_act_paths_never_supply_x_ranges.
It only asserts the string 'type_x_ranges' appears in the
CodeExecBackend.act source slice and in the CLI act line, so it is
vacuous. I verified this by mutation in my own worktree at 65a2df6:
setting type_ranges = [[0.0, 20.0]] unconditionally in
CodeExecBackend.act (scripts/cu.py:2748, the exact behavior the
test name says must never happen) still passes the test (Ran 1,
OK); I then reverted the mutation and verified the tree clean.
The test's own comment ("CodeExecBackend.act builds no
type_x_ranges at all") is also false at this tip: act builds
type_ranges in the wired branch and passes
type_x_ranges=type_ranges on every call (scripts/cu.py:2771-2782),
and the CLI likewise (scripts/cu.py:3119). Rewriting the pin test
is the coordinator's lane's decision, not this task's; the
disclosed unwired-path residual stands as is.

## What this task did NOT do, stated plainly

- No test file was edited by this task. The repair is the
  coordinator's TESTREPAIR-B (43b27a1), not mine. The assignment
  (495cfc6, 08:50) was written after TESTREPAIR-B landed (08:01);
  the coordinator's TESTREPAIR log (77c72be, "complete repair log
  (A, A2, B, C8, C12, C7, D, final verification)") records its own
  final verification as "RT set Ran 51, OK at HEAD 29083cd" (the
  log never writes the literal string "15/15"; the 51 entails 14
  behavioral proofs + 1 pin passing). My numbers are an
  independent re-run at a later tip (65a2df6), not a copy of that
  log.
- TESTREPAIR-B itself touches only tests/test_click3_redteam2.py
  (git show 43b27a1 --stat, 1 file, 110 insertions, 24 deletions)
  and no production code, and weakens no other test. The branch
  ed2d559..65a2df6 also contains TESTREPAIR-C7, C8, C12 and D test
  changes, including C7 edits to the F6/F7/F8 tests in the same
  file, and production-code changes by C7 (zen_dom.py per-arm
  property name), C8 (cdp.mjs), C12 (first_action.py _scope_after
  restore), ITEM8 and S0-J37. The F6 test as it passes at tip
  65a2df6 is a B+C7 composite, not B alone; credit C7 for the
  session-pairing edit that keeps those tests green under the
  random property name. No production code was touched by this
  task. No-weakening check extended to C7 and C8, verified from
  their diffs in this fix pass: C7 changes only the _capture_js
  session pairing in the test file, with assertions unchanged;
  C8 purely adds the maxlength test (+92/-0 in the test file).
- The two open notes from the TESTREPAIR log are repeated, not
  resolved here: (1) the F5 DOM-gate finding (through the full wired
  path the pixel band is never the decider; the DOM type_check
  decides either way, cu.py:2280 / cu.py:2110-2117 / cu.py:2279);
  (2) the item 7 pre-locked-property residual (outside the R10
  attacker model), now hardened by TESTREPAIR-C7 with a per-arm
  unpredictable property name. One further open follow-up from
  this fix pass, for the coordinator's lane: (3) the F3 retained
  test's assertion message at tests/test_click3_redteam2.py:311-313
  contradicts its assertion (see the F3 section); the test file is
  not edited here.

## Evidence locations

- Worktrees: ~/workspace/tools/rt2-repair/wt (65a2df6),
  ~/workspace/tools/rt2-repair/wt-preB (ed2d559).
- Logs: ~/workspace/tools/rt2-repair/preB-five.log (5 tests,
  failures=4, errors=1, at ed2d559),
  ~/workspace/tools/rt2-repair/post-five.log (5 tests, OK, at
  65a2df6), ~/workspace/tools/rt2-repair/rt2-full.log (Ran 51,
  OK), ~/workspace/tools/rt2-repair/rt2-verbose.log (per-test ok
  list), ~/workspace/tools/rt2-repair/discover-current.log (Ran
  1974, failures=1, errors=5, skipped=17, 182.514 s),
  ~/workspace/tools/rt2-repair/discover-29083cd.log (Ran 1974,
  failures=4, errors=5, skipped=17, 440.595 s, fix-pass re-run at
  29083cd; council 1's run at the same commit gave failures=3,
  errors=6, the same total of 9 problem tests),
  ~/workspace/tools/rt2-repair/codeexec-codemode.log (Ran 81, OK).
  Fix-pass worktree: ~/workspace/tools/rt2-repair/wt-29083cd.
- Sources: TESTREPAIR-B diff (git show 43b27a1), TESTREPAIR log
  (improvements/worker-click3-testrepair-log.md, 77c72be), DOT 9
  task 1 review (docs/clone2-council-round3-amend4-20261122.md).
