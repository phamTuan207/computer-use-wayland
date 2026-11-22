# Worker C5-B5-VERIFY log: B5 limb (ii), defective RT2 proof tests for AMEND4 items 3, 4, 5-6

Worker: C5-B5-VERIFY, for COORD-CLICK-5. Reports to the coordinator only.
Branch: todolist-push. Repo: ~/workspace/computer-use-wayland.
Start: 2026-11-22 10:42 +07 (Asia/Ho_Chi_Minh). Head at start: fccf367.
Finish: 2026-11-22 10:51 +07. Head at finish: 5127ce5. Elapsed about 9 minutes.
No live laptop work; repo plus test-run work only. No em dash or en dash
anywhere in this file. No personal information. Never ydotool.

## Headline verdict

B5 limb (ii) is MET on todolist-push, NOT MET on main.

- All 5 defective RT2 proof tests (F2, F3, F4, F5-behavior, F6) are
  repaired by TESTREPAIR-B, commit 43b27a1, which is an ancestor of
  todolist-push. I re-ran them failing-first at the pre-repair parent
  ed2d559 (Ran 5, FAILED, failures=4, errors=1) and post-repair at the
  current tip 5127ce5 (Ran 6 tests including the new F3 sibling, OK).
  Full RT2 suite at tip: Ran 51, OK. Full discover at tip: Ran 2024,
  0 failures, 4 pre-existing errors, 17 skipped.
- The repairs are ABSENT from main. Main does not contain the RT2 test
  file at all, and does not contain the AMEND4 production code either.
  This is a port problem, not a repair problem. I did not cherry-pick
  or port anything; the coordinator decides the port after this verdict.
- Two open follow-ups do not change the verdict (neither affects
  pass/fail or the behavioral coverage of the 5 tests): (1) the retained
  F3 test carries an assertion message that contradicts its assertion;
  (2) the F5-source pin test is vacuous by my own mutation test, and
  the unwired-path residual stands by design, awaiting adjudication.

## 1. Sources read in full

- Clone2 batch 11 task 1 report: docs/clone2-rt2-defective-repair-20261122.md,
  commit 3c805a7 (fix pass) building on 49a6e4c (first verification).
  Tip it verified: origin/todolist-push 65a2df6. Its headline: the
  assignment premise was stale, the repair had already landed as
  TESTREPAIR-B 43b27a1 about 46 minutes before the batch 11 assignment
  (495cfc6, 08:50 +07). Verdict there: 14/14 behavioral proof tests
  pass plus 1 source-presence pin.
- DOT 9 task 1 review: docs/clone2-council-round3-amend4-20261122.md,
  7aeea01 plus fix pass 9427eeb. It proves each of the 5 tests defective
  with its own runs and prescribes the exact test-side repair for each.
  Overall verdict there: AMEND on the acceptance gate only, 12/12 GO
  per item, repairs test-side only, no code change required.
- TESTREPAIR-B diff: git show 43b27a1, read in full (228 lines, 1 file,
  tests/test_click3_redteam2.py, 110 insertions, 24 deletions).
- Defective landing commits: 62b740e (item 3, F4 test defective),
  72120aa (item 4, F5 behavior test defective), b44a5ea (items 5-6,
  F2/F3 RT2 tests defective). All three are ancestors of todolist-push
  and none is an ancestor of origin/main.
- Prior logs: improvements/worker-click4-step1-closeout-log.md (discover
  at 36364b1: Ran 1974, 0 failures, 4 errors) and
  improvements/worker-click3-reconcile-amend4-log.md (Ran 1974,
  failures=2, errors=4 at 77c72be).

## 2. The 5 defective tests: defect named, repair claimed

Mapping note: limb (ii) names AMEND4 items 3, 4, 5-6, which cover F4
(item 3), F5-behavior (item 4), F2 and F3 (items 5-6). F6 belongs to
item 7 (R10 flag redesign), but it was named defective in the same
DOT 9 review and repaired in the same commit 43b27a1, so it is
verified here too. All 5 are listed.

| Test | Item | Defect named (DOT 9, own proof) | Repair in 43b27a1 |
| --- | --- | --- | --- |
| F2 test_region_fallback_readmits_raw_mozinner | 5-6 | Calls ground_input with a meta that has no window_bounds and asserts a ground return plus a point within 10 px of the true point. The specified fix is to REFUSE, so correct behavior errors the test, which has no assertRaises. The true origin [2749, 922] is not derivable from the meta. | Old ground plus two assertions replaced by with self.assertRaises(dom_act.DomActError): dom_act.ground_input(session, meta, '#msg-input'). |
| F3 test_stale_window_origin_accepted_silently | 5-6 | Asserts stale == [340, 108] AND the mapped point within 10 px of the true point. Mapped point (323.0, 620.25), true point (1527.5, 1027.25), 1271.4 px apart. No return value satisfies both. Direct viewport_origin call cannot detect staleness. | Split in two. Original retained as characterization: keeps stale == [340, 108], asserts dist > 1000. New sibling test_stale_window_origin_refused_at_ground_time asserts the ground-time refusal via ground_input with a live origin mismatch, assertRaises DomActError containing 'moved'. |
| F4 test_band_stacked_fields_low_click_with_x_range_must_not_verify | 3 | Calls _input_line_changed with pixels at y=126 and no y_range, while its control requires pixels at y=110 to verify. Both are 8 px from anchor 118 and the band without y_range is symmetric anchor +- 12. No half value satisfies both assertions. | y_range=(100, 120) added to the _input_line_changed call, with a comment explaining the symmetry. |
| F5-behavior test_band_wrong_field_unwired_path_reports_ok | 4 | Calls cu.desktop_act DIRECTLY with no ranges and expects ok False. Range threading through CLI, CodeExec and first_action cannot affect a direct call. The "or" branch (band-only unverified without ranges) would break the control test_click_type_text_in_input_line_verifies. | Rewritten in two halves. Half 1 proves wiring: a desktop_act spy records CodeExecBackend.act threading the grounded ranges of the target field ([12.0, 20.0] x [8.0, 12.0]) to desktop_act, asserted exactly. Half 2 proves behavior: a direct desktop_act call with THOSE ranges (taken from the spy, not hardcoded) and no type_check hook must not verify wrong-field pixels at x 0..11, while right-field pixels at x 12..17 still verify. |
| F6 test_typed_flag_forgeable_by_page_script | 7 | Two defects, both proven by DOT 9 with its own node run. (1) The forge line window.__agentCuTyped['#msg-input'] = true; throws TypeError because the arm no longer creates window.__agentCuTyped, so the test dies before its assertions. (2) assertNotEqual(value, 'hello') can never pass: the page script set the field value to 'hello'. | Forge line guarded in try/catch; value assertion replaced with assertEqual(value, 'hello'). Flag assertion assertFalse unchanged. Comment states the flag is the discriminator, not the value. |

## 3. Branch placement: repairs on todolist-push only

Evidence, all run 2026-11-22 10:42-10:43 +07:

- git merge-base --is-ancestor 43b27a1 todolist-push: YES.
  git merge-base --is-ancestor 43b27a1 origin/main: NO.
- git branch --contains 43b27a1 lists todolist-push (plus
  item8-microgap, which branched from todolist-push) and does NOT
  list main.
- git log origin/main --grep="TESTREPAIR": no code or test repair
  commit. The only hits are docs mentions (49a6e4c, 66689aa,
  d437510). Clone2's batch 11 task 1 verification docs ARE on main
  (49a6e4c, 3c805a7), but the repair commit they verify is not.
- The RT2 test file does not exist on main at all:
  git rev-parse origin/main:tests/test_click3_redteam2.py fails
  ("path exists on disk, but not in origin/main"). git grep for the
  test names on origin/main finds them only in docs files
  (clone2-amend4-reverify, clone2-batch11-discover-y1b,
  clone2-council-round3-amend4, clone2-rt2-defective-repair).
  git diff origin/main todolist-push -- tests/test_click3_redteam2.py
  shows the file as new on todolist-push (843 insertions).
- Main also lacks the AMEND4 production code: git grep type_x_ranges
  on origin/main scripts/cu.py returns nothing; on todolist-push it
  returns 6 matches. The defective landing commits 62b740e, 72120aa,
  b44a5ea are ancestors of todolist-push and not of main.
- Blob hashes of the test file: tip dddbddc
  7c4c3d1d122b9ddcb724a5c01fab2c2edda70cfc; at 43b27a1
  994b7b1f946801c0cef23cfafb6d94c14c091686; at ed2d559
  f012cda861296c4b66e622bbc317605fda17569a. No blob comparison with
  main is possible because the file is absent there.
- Tip movement during this verification: HEAD was fccf367 at start,
  moved to dddbddc (docs-only COORD-CLICK-5 log commit, 10:43 +07),
  then to 5127ce5 by the finish. git diff dddbddc HEAD -- tests/
  scripts/ is empty, so all test and production code is identical
  between dddbddc and 5127ce5. My runs below were done at dddbddc
  and re-run at the final tip 5127ce5.

## 4. My test runs (independent, own worktrees and own commands)

Runner everywhere, unless noted: from tests/,
PYTHONPATH=../scripts:. python3 -m unittest. System python3.

### 4a. Failing-first at the pre-repair parent ed2d559

Worktree /tmp/wt-preB, detached HEAD ed2d559 (parent of 43b27a1).
Correction, recorded honestly: my first run showed F5-behavior as
ERROR, not FAIL, because the fresh worktree lacked the built binary
native/wtype (present in the main checkout, 35984 bytes, not tracked
by git), and desktop_act raised RuntimeError 'private wtype helper
is missing'. I copied native/wtype into the worktree and re-ran.
Second run, 2026-11-22 10:45:17 +07:

```
test_region_fallback_readmits_raw_mozinner ... ERROR
test_stale_window_origin_accepted_silently ... FAIL
test_band_stacked_fields_low_click_with_x_range_must_not_verify ... FAIL
test_band_wrong_field_unwired_path_reports_ok ... FAIL
test_typed_flag_forgeable_by_page_script ... FAIL
Ran 5 tests in 0.387s
FAILED (failures=4, errors=1)
```

This matches the DOT 9 post-fix numbers (F2 error, F3/F4/F5-behavior/
F6 failures) and clone2's preB-five.log. All 5 defective tests fail
or error before the repair, exactly as documented. The F6 node stderr
in my run is the same TypeError (Cannot set properties of undefined,
setting '#msg-input') DOT 9 recorded.

### 4b. Post-repair at the todolist-push tip

Run 1 at dddbddc, 2026-11-22 10:43:47 +07, 6 tests (5 repaired plus
the new F3 sibling):

```
test_region_fallback_readmits_raw_mozinner ... ok
test_stale_window_origin_accepted_silently ... ok
test_stale_window_origin_refused_at_ground_time ... ok
test_band_stacked_fields_low_click_with_x_range_must_not_verify ... ok
test_band_wrong_field_unwired_path_reports_ok ... ok
test_typed_flag_forgeable_by_page_script ... ok
Ran 6 tests in 0.449s
OK
```

Run 2, final re-run at tip 5127ce5, 2026-11-22 10:50:03 +07:
Ran 6 tests in 0.427s, OK. Same 6 tests, all ok.

### 4c. Full RT2 suite at tip

2026-11-22 10:43:57 +07 at dddbddc: Ran 51 tests in 1.617s, OK.
Re-run at 5127ce5, 10:50:03 +07: Ran 51 tests in 1.731s, OK.
Verbose per-test list confirms all 14 behavioral proof tests pass
by name (F1, F2, F3, F4, F5-behavior, F6, F7-node, F7-python, F8,
F9, F10, F11, F12, F13) plus the F5-source pin, the F3 sibling,
the maxlength test, the 2 controls, and the 32 harness tests.
51 = 14 + 1 pin + 1 sibling + 1 maxlength + 2 controls + 32 harness.

### 4d. Controls: the "or" branch was correctly not adopted, the band is not blinded

2026-11-22 10:45 +07 at tip, Ran 2 tests, OK:

- test_click_type_text_in_input_line_verifies
  (test_type_verification.TypeVerification): ok. Direct desktop_act
  with no ranges still verifies via the band, so the "or" branch
  would have broken it and was rightly refused.
- test_band_text_inside_target_field_still_verifies
  (R3aStackedFieldTests): ok. F4's y_range narrows the band instead
  of blinding it.

### 4e. Full discover at tip

Launched 2026-11-22 10:44:36 +07, detached, log /tmp/c5-discover.log.
Finished 10:48:44 +07. Command: from tests/,
PYTHONPATH=../scripts:. python3 -m unittest discover -s . -p "test_*.py".
Result:

```
Ran 2024 tests in 212.433s
FAILED (errors=4, skipped=17)
```

Failures: 0. Errors: 4, all pre-existing baseline, identical to the
closeout log: test_a11y_skeleton import (No module named 'tests'),
test_cursor_file setUpClass (g++ -std=c++26 unrecognized),
test_perf_evidence x2 (missing docs/benchmarks/r5_cdp_aggregate.json).
No FAIL lines, no RT2 problems, no test_code_exec or test_codemode
problems. Zero tc02 problems (see section 7).

### 4f. F5-source pin vacuity, confirmed by my own mutation

In a separate tip worktree /tmp/wt-tip (dddbddc), I set
type_ranges = [[0.0, 20.0]] unconditionally in CodeExecBackend.act
(scripts/cu.py, right after type_ranges = None), the exact behavior
the pin test name says must never happen. Run 2026-11-22 10:47:10 +07:

```
test_codeexec_and_cli_act_paths_never_supply_x_ranges ... ok
Ran 1 test in 0.074s
OK
```

The pin still passes under the forbidden mutation, so it is vacuous:
it only asserts the string 'type_x_ranges' appears in the
CodeExecBackend.act source slice and in the CLI act line. I reverted
the mutation with git checkout and verified the worktree clean
(0 dirty files). Note the pin's own comment ("CodeExecBackend.act
builds no type_x_ranges at all") is false at this tip: act builds
type_ranges in the wired branch and passes type_x_ranges=type_ranges
on every call (cu.py:2872), and the CLI likewise (cu.py:3223).
This reproduces clone2's mutation result independently.

## 5. Per-test weakening analysis: does the repair fix the defect, or merely relax the assertion?

I read the full 43b27a1 diff and the current test bodies at tip.
Verdict per test:

- F2: FIXES the defect, does not relax. The old assertions are
  unsatisfiable under the specified fix (refuse a bounds-less meta).
  assertRaises(DomActError) asserts the specified behavior strictly:
  the code must refuse. The test asserts more about the required
  behavior, not less. Minor note: it does not assert the error
  message; the refusal itself is what the item specifies.
- F3: FIXES the defect, does not relax. The pair asserts strictly
  more about the specified behavior than the old test could: the
  sibling asserts the ground-time refusal (assertRaises plus
  'moved' in the message), and the retained original pins the
  direct-call limitation (dist > 1000, the documented 1271 px gap).
  The old dist < 10 assertion was impossible for any implementation.
  Open quality issue, see section 6 item 1: the retained test's
  assertion message contradicts its assertion.
- F4: FIXES the defect, does not relax. Adding y_range=(100, 120)
  supplies the distinguishing input the production fix provides;
  the test exercises the field-anchored band the item implements.
  The positive control still passes, so the band is not blinded.
  Nothing about the no-y_range path is asserted, but that path is
  symmetric by design and out of scope for item 3.
- F5-behavior: FIXES the defect as a test, does not relax. Half 1
  asserts the exact threaded ranges ([[12.0, 20.0]], [[8.0, 12.0]]);
  half 2 asserts wrong-field pixels do not verify AND right-field
  pixels do verify with those ranges. That is a strict two-sided
  behavioral check of the wired path. What it does NOT do is test
  the unwired path: after this repair no RT2 test asserts the
  wrong-field outcome on the unwired path, only the vacuous
  source pin (section 4f). That residual is a design adjudication
  (fail-closed vs best-effort), not a test-weakening trick: the
  DOT 9 review prescribes exactly this rewrite and records the
  dissent (batch 10 task 2 judged it a true negative).
- F6: FIXES the defect, does not relax. The substantive flag
  assertion assertFalse is unchanged, and assertTrue(armed) is
  unchanged. The flipped value assertion (assertNotEqual to
  assertEqual 'hello') pins a true fact: the page script did set
  the value to 'hello', and the flag is the discriminator. The
  try/catch guard keeps the test alive when the forgery attempt
  itself throws, which is evidence the attack surface is gone.
- Later edits do not weaken the 5: git diff 43b27a1 dddbddc --
  tests/test_click3_redteam2.py is only TESTREPAIR-C7 session
  pairing (ee883bc, _capture_js session parameter plus arm/flag
  call sites in F6/F7/F8, assertions unchanged) and TESTREPAIR-C8
  (7372ddd, purely additive maxlength test, +92/-0 in the test
  file). No production code was touched by 43b27a1 (1 file, test
  only). The F6 test as it passes at tip is a B plus C7 composite;
  credit C7 for the session pairing that keeps it green under the
  per-arm property name.

## 6. Open follow-ups (do not block the limb, tracked for the coordinator)

1. F3 retained test assertion message contradicts its assertion.
   At tip, tests/test_click3_redteam2.py, the assertEqual(stale,
   [340, 108]) carries the message 'a stale window origin must be
   refused, not returned as if true', but the test passes precisely
   because the stale origin IS returned. The message states the
   opposite of what the test pins. Message-only: it does not change
   pass/fail. Fix: reword the message to state the characterization
   (the direct call returns the stale value; refusal happens only
   at ground time). Clone2 flagged this first; I confirm it is
   still present at tip 5127ce5. One-line test-message fix, in the
   coordinator's lane.
2. F5-source pin test is vacuous (section 4f) and its comment is
   false at tip. Rewriting the pin is the coordinator's lane's
   decision. It is not one of the 5 defective tests, so it does not
   block limb (ii).
3. Unwired-path residual stands unchanged: the CodeExec path remains
   unwired by construction (allowlist exposes no ZenSession) and the
   CLI path remains unwired without --dom-selector, so after this
   repair no RT2 test asserts the wrong-field outcome on the
   unwired path. The fail-closed vs best-effort choice is still open
   and left to adjudication. Not a repair problem; a design decision.
4. F5 DOM-gate finding (from the TESTREPAIR log, repeated, not
   resolved here): through the full wired path the pixel band is
   never the decider; the DOM type_check decides either way.
5. Item 7 pre-locked-property residual (outside the R10 attacker
   model), hardened by TESTREPAIR-C7 with a per-arm unpredictable
   property name.

## 7. Discover-count discrepancy note

Three discovers are on record:

- Step 1 closeout at 36364b1: Ran 1974 in 248.397s, 0 failures,
  4 errors, 17 skipped. The 2 failures at the earlier 77c72be
  baseline were test_browser_image (S0 J37 jpeg keys), fixed by
  e83b72d; the closeout log records failures 2 to 0.
- Clone2 batch 11 task 3 at 65a2df6: Ran 1974, failures=1, errors=5,
  skipped=17. The 1 failure and 1 of the 5 errors were the tc02
  tesseract pair ("tesseract is unavailable" on that run).
- Mine at dddbddc (section 4e): Ran 2024 in 212.433s, 0 failures,
  4 errors, 17 skipped.

Resolution, from my own runs: the 1 failure does NOT reproduce at
the current tip. /usr/bin/tesseract exists on this VM now, and the
tc02 module passes in full: from repo root,
PYTHONPATH=scripts:. python3 -m unittest tests.test_tc02_controller
gives Ran 46 tests in 1.034s, OK (2026-11-22 10:49:22 +07). The gap
between the closeout (0 failures) and clone2 task 3 (1 failure) is
the tc02 pair failing only when tesseract is unavailable in that
run's environment; clone2 itself noted the discover failure count
is load-sensitive. No RT2 problem in any of the three runs.
The count growth 1974 to 2024 is tip movement (S2 flip work and
coord logs added tests between 65a2df6 and dddbddc), not a
collection error: same runner, same start directory, same pattern.

Note on my own wrong invocation, for the record: running
test_tc02_controller from tests/ with PYTHONPATH=../scripts:.
gives Ran 1 test, errors=1 (ModuleNotFoundError: No module named
'scripts', test_tc02_controller.py line 9). That is my runner
mistake, not a test problem; the module must run from the repo
root as tests.test_tc02_controller, which passes 46/46.

## 8. B5 limb (ii) judgment

MET on todolist-push. Evidence:

- The 5 defective proof tests are repaired by 43b27a1 on
  todolist-push, each repair matching the DOT 9 documented repair
  exactly (section 2), and each repair fixes its named defect
  rather than relaxing the assertion (section 5).
- The repairs are re-verified twice independently: clone2 batch 11
  task 1 at 65a2df6 (Ran 5 OK, full RT2 Ran 51 OK, discover
  1974/1/5/17 with the 1 failure environmental) and this worker at
  dddbddc and 5127ce5 (Ran 6 OK, full RT2 Ran 51 OK, discover
  2024/0/4/17).
- Failing-first is established by my own runs: all 5 fail or error
  at ed2d559 and all 5 pass at tip.

NOT MET on main, as a port problem only: the repair commit 43b27a1,
the RT2 test file, and the AMEND4 production code are all absent
from main (section 3). If B5 is meant to gate main, the port is the
remaining work. I did not port anything; the coordinator decides.

What remains, per test: nothing, on todolist-push, except the
message-only F3 follow-up (section 6 item 1). No repair problem, no
verification problem on todolist-push. One port problem, main only.

## Evidence locations

- Worktrees (ephemeral, /tmp): /tmp/wt-preB (ed2d559, failing-first),
  /tmp/wt-tip (ddbddc, pin mutation, reverted clean).
- Logs: /tmp/c5-discover.log (Ran 2024, 0 failures, 4 errors,
  212.433s). All other run outputs are quoted verbatim in this log.
- Sources: git show 43b27a1, git show 49a6e4c, git show 3c805a7,
  docs/clone2-rt2-defective-repair-20261122.md,
  docs/clone2-council-round3-amend4-20261122.md.
