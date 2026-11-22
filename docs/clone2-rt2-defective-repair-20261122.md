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
(08:01:47 +07), 48 minutes BEFORE the batch 11 assignment
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

## Verdict: 15/15 proof tests pass

- The 5 repaired tests: Ran 5, OK at 65a2df6 (0.205 s).
- Full RT2 suite (tests/test_click3_redteam2.py): Ran 51 tests in
  1.199 s, OK. 51 = 49 + 1 F3 split test
  (test_stale_window_origin_refused_at_ground_time) + 1 maxlength
  test (test_set_value_maxlength_uses_sanitized_length, TESTREPAIR-C8).
  All 15 proof tests pass by name (listed in the per-test section),
  plus the 2 controls, the F3 sibling, the maxlength test, and the 32
  harness tests.
- Full discover at 65a2df6: Ran 1974 tests in 182.514 s, FAILED
  (failures=1, errors=5, skipped=17). The only failure and 1 of the
  5 errors are the tc02 tesseract pair (environmental: "tesseract is
  unavailable" on this VM, identical to every earlier run). The other
  4 errors are the pre-existing laptop-only ones (test_a11y_skeleton
  import, test_cursor_file setUpClass, test_perf_evidence x2). Zero
  RT2 problems remain. Zero test_code_exec / test_codemode problems:
  Ran 81 tests, OK (13.277 s), so the 8 Y1b problems seen at 17fdb9b
  are gone at this tip; which commit cleared them is batch 11 task
  3's question, not this task's.
- The discover count grew 1920 (at 0668327/29083cd) to 1974 at
  65a2df6 because the tip moved (S0-IMPL, ITEM8-MICROGAP,
  TESTREPAIR-C7/C8/C12/D, Y1B-RPC-LAND landings added tests). The
  failure count fell 5 to 1 and the error count 6 to 5 over the same
  move, entirely from the 5 repaired RT2 tests.

## Per-test evidence

### F2 test_region_fallback_readmits_raw_mozinner

- Failing-first (ed2d559): ERROR. ground_input returns a ground
  whose viewport_origin is the raw mozInner pair [240, 8]; the test
  asserts it is not [240, 8] and that the point is within 10 px of
  the true point, so correct refusal behavior errors the test, which
  has no assertRaises. Log: ~/workspace/tools/rt2-repair/preB-five.log.
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
  --dom-selector, so after this repair NO RT2 test exercises the
  unwired path behaviorally; only the source-level pin test
  test_codeexec_and_cli_act_paths_never_supply_x_ranges remains.
  The fail-closed vs best-effort choice is still open and left to
  adjudication. The coordinator's parallel council lane (commit
  a14223d) records F4/F5/F6 divergence decisions in an addendum;
  I did not read it and do not copy it.

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

## The 15 proof tests, all passing at 65a2df6

F1 test_set_value_newline_text_fails_verification, F2
test_region_fallback_readmits_raw_mozinner, F3
test_stale_window_origin_accepted_silently, F4
test_band_stacked_fields_low_click_with_x_range_must_not_verify,
F5-source test_codeexec_and_cli_act_paths_never_supply_x_ranges,
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

## What this task did NOT do, stated plainly

- No test file was edited by this task. The repair is the
  coordinator's TESTREPAIR-B (43b27a1), not mine. The assignment
  (495cfc6, 08:50) was written after TESTREPAIR-B landed (08:01);
  the coordinator's TESTREPAIR log (77c72be, "complete repair log
  (A, A2, B, C8, C12, C7, D, final verification)") records the same
  15/15 result from its own final verification (RT set Ran 51, OK
  at HEAD 29083cd). My numbers are an independent re-run at a later
  tip (65a2df6), not a copy of that log.
- No production code was touched. No other test was weakened: the
  only test-file change on this branch since ed2d559 is
  TESTREPAIR-B itself (verified: git show 43b27a1 --stat, 1 file).
- The two open notes from the TESTREPAIR log are repeated, not
  resolved here: (1) the F5 DOM-gate finding (through the full wired
  path the pixel band is never the decider; the DOM type_check
  decides either way, cu.py:2280 / cu.py:2110-2117 / cu.py:2279);
  (2) the item 7 pre-locked-property residual (outside the R10
  attacker model), now hardened by TESTREPAIR-C7 with a per-arm
  unpredictable property name.

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
  ~/workspace/tools/rt2-repair/codeexec-codemode.log (Ran 81, OK).
- Sources: TESTREPAIR-B diff (git show 43b27a1), TESTREPAIR log
  (improvements/worker-click3-testrepair-log.md, 77c72be), DOT 9
  task 1 review (docs/clone2-council-round3-amend4-20261122.md).
