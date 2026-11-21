# CLICK-AMEND independent verification, 2026-11-22

Verifier: batch 8 task 2, independent second opinion. Read-only work in two
worktrees, `~/workspace/b8t2/amend` at `4b7d6ac` and `~/workspace/b8t2/base`
at `e4082ff`. No checkout of `todolist-push` into the working tree, no merge,
no commit, no push. No `coord/clone1.md` or `coord/clone2.md` edit.

## 1. Diff range and what it contains

Range: `e4082ff..4b7d6ac` on branch `todolist-push`.

The CLICK-AMEND work inside the range is 8 commits:

- `e704187` cu.py type verification band, focus and type hooks, terminal None marker
- `e10fef4` first_action widen G28 refusal to pointer-only, envelope fields, window-only remedy
- `7d37d60` zen_dom raw-exception conversion, restore surfacing, scan budget, switch verify, DOM helpers
- `8e52ba9` DOM-first grounding, rect center to image point, dom_act orchestrator
- `eb9066a` tests: type verification band and hooks, preflight harness, item 1 fake fix
- `90b7026` tests: first_action refusal flip, zen_dom R5-R8 and DOM helpers, rect mapping, dom_act
- `96a9e46` logs: fix-log Stage A correction (RT R1) and amend run log
- `4b7d6ac` log: push verified at `96a9e46`

Code and test files changed by those commits, 12 files, 1632 insertions,
116 deletions:

- `scripts/cu.py` 256 lines, `scripts/dom_act.py` 129 (new), `scripts/fastpath.py` 81
- `scripts/first_action.py` 75, `scripts/zen_dom.py` 250
- `tests/test_dom_act.py` 282 (new), `tests/test_first_action.py` 111
- `tests/test_keyboard_preflight.py` 23, `tests/test_pick4_fastpath.py` 124
- `tests/test_session_continuation.py` 8, `tests/test_type_verification.py` 132
- `tests/test_zen_dom.py` 277

The range also contains other workers' commits that are NOT part of
CLICK-AMEND and were NOT verified here: batch 7 corrections `748cc35`,
`219720c`, `05ee34d`, `16c4196`; ZT-C `c19c227`, `7437384`, `0b92542`,
`646cf71`; crawls `50343fe`, `c450f5d`, `8fd87e2`, `f5ac63f`, `43b7c42`,
`7b85472`, `96f49ac`; reviews `846cf0d`, `9d5ae86`,
`59acd36`, `6cdebda`; ZT-B `f2999c7`, `88d3d0a`; CODEX comparisons
`238b528`, `9350db7`; Y13g `ab0b62c`, `167a2e9`; coord logs `ce2b4d7`,
`7d3db26`, `07dcb0b`, `9a1be5c`, `0db32fc`, `96ce916`, `5dacdeb`,
`9e6c80c`. That is all 33 non-amend commits in the range (41 total).
Scope claims below cover only the
CLICK-AMEND code and test files.

Scope check, by `git diff e4082ff..4b7d6ac`: 15 changed lines mention
`image_point` (new calls, the new `dom_rect_to_image_point` function,
docstrings), but zero diff lines touch the `image_point`, `move`, or
`_check_entry_pyc` definitions, so the
calibration-proven coordinate conversion and the entry check are untouched.
Zero em dashes and zero en dashes in the code and test diff.

## 2. Test suites re-run on this machine

Method: `python3 -m unittest <suite>` in the amend worktree `tests/`
directory. Run 2026-11-21 21:44 UTC and re-runs 22:01 UTC (run times
unlogged, no artifact on disk). The suites use
fakes, no live browser. Only `native/wtype` was built from vendored source;
the full `scripts/build.py` fails here on missing gtk4 dev packages (no
build log on disk; `pkg-config --exists gtk4` fails), which
does not affect these suites.

| Suite | Tests | Result | Time |
|---|---|---|---|
| test_first_action | 61 | OK | 0.629s |
| test_type_verification | 47 | OK | 0.424s |
| test_zen_dom | 25 | OK | 0.005s |
| test_dom_act | 10 | OK | 0.001s |
| test_pick4_fastpath | 28 | OK | 0.074s |
| test_session_continuation | 10 | OK | 0.242s |
| Total 6 suites | 181 | OK | 1.375s |

Extra runs, same worktree:

- 13-suite set (the 6 above plus test_keyboard_preflight,
  test_fast_observe, test_act_diagnostics, test_guard_boundaries,
  test_pointer_safety, test_focus, test_observation_contract): 315 tests
  OK in 2.239s, wall 2.81s. Matches the amend log claim of 315 tests OK.
- 12-module neighbor set (test_core, test_codemode, test_session_driver,
  test_session_policy, test_session_continuation, test_phase3_c1,
  test_phase3_c2, test_phase3_cleanup, test_json_limits,
  test_observation_contract, test_act_diagnostics, test_fast_observe):
  209 tests in 8.037s, FAILED with exactly 2 failures, both
  `test_core.SecureObservationFiles.test_private_mode_under_any_umask_in_isolated_child`
  (umask `0` and `0o777`). The same 2 failures occur on the base worktree
  at `e4082ff` (209 tests in 7.690s), so they are pre-existing environment
  failures, not a regression from this diff.

## 3. The 12 fix items, file and line at 4b7d6ac

All 12 confirmed present. Line numbers verified by reading the files at
`4b7d6ac`, not from the amend log.

1. Session-continuation regression test: `tests/test_session_continuation.py:252`,
   `post = dict(after, pixel_sha256='1111')`. PASS.
2. G28 widening: `scripts/first_action.py:474-498`. The refusal covers EVERY
   batch, not only key/type batches; docstring says "for any batch";
   `has_keyboard` is now computed only to pick the message text. Flipped
   test `tests/test_first_action.py:620`
   `test_stale_given_observation_pointer_only_refused` expects code 1,
   path `refused`, session not called. PASS.
3. `type_verified=None` on the other after-skipped path:
   `scripts/cu.py:2005`, terminal address None. PASS.
4. R1: `_input_line_changed` `scripts/cu.py:1018` (band anchor_y plus or
   minus 12px, threshold 50); `type_anchor` `:1711`; focus gate `:1849`;
   type_check hook `:1913`; DOM-value basis `:2050`. Fix-log Stage A claim
   corrected in `improvements/worker-click-fix-log.md`. PASS.
5. R2, subsumed by item 2: no proceed path remains. `rejected is not None`
   always refuses with `fallback_reason` set (`scripts/first_action.py:474-498`).
   `_fresh_observation` has exactly one production caller in the repo, `run()` at
   `scripts/first_action.py:470` (plus 8 direct test calls in
   `tests/test_first_action.py:809, 823, 843, 856, 868, 878, 892, 904`). PASS.
6. R3: envelope `type_verified` and `error_code` init
   `scripts/first_action.py:427-428`; copied from session `:543-544` and
   from the fallback `:597-599`. PASS.
7. R4: `loud_substitution_refusal(rejected, has_keyboard)`
   `scripts/first_action.py:357`; screen remedy only when `not has_keyboard`
   `:378`. PASS.
8. R5: `_wd` `scripts/zen_dom.py:197` catches TimeoutError, OSError,
   URLError, HTTPException, ValueError (JSONDecodeError is a ValueError);
   missing `value` raises ZenDomError `:191`. HTTPError is caught first
   (it is a URLError subclass), so the order is correct. PASS.
9. R6: `_try_restore` `scripts/zen_dom.py:227`; restore failures are raised,
   never swallowed (`:304-314` and `:331-337`). PASS.
10. R7: scan stops after the first hang, wedge `:317-332`. The transport
    failure sets `wedge` and breaks the loop; restore runs in `finally`.
    PASS.
11. R8: `_verify_selected` `scripts/zen_dom.py:240`; docstring downgraded to
    "handle-LIST index, not a verified visual tab order" `:257-258`. PASS.
12. DOM-first grounding: `viewport_origin` `scripts/zen_dom.py:367`
    (`window.mozInnerScreenX/Y`); `locate_point` `:384`; `hit_check` `:405`;
    `focus_check` `:423`; `field_value` `:436`; `verify_typed` `:444`;
    `scripts/fastpath.py` `dom_rect_to_screen_point` `:152`,
    `dom_rect_to_image_point` `:169`, `point_in_rect` `:206`;
    `scripts/dom_act.py` `ground_input` `:38`, `ground_many` `:64`,
    `focus_type` `:78`. Test coverage: rect center
    (`tests/test_dom_act.py:123`), covered-refusal before any click
    (`:132`), miss never types (`:233`), no extra observes
    (`tests/test_dom_act.py:227-228`
    assert `observes_added` 0 and `act_observes` 0;
    `tests/test_type_verification.py:195` asserts the observe call
    sequence `['fresh', 'persist', 'persist']`), 7-case accuracy
    (`tests/test_pick4_fastpath.py:488-541`). PASS.

Bonus, not demanded by any review: R10 third bullet is fixed. In
`list_tabs` the range check now runs before `current_handle()`
(`scripts/zen_dom.py:288-294`): handles are fetched, the index is range
checked, then `current = self.current_handle()`. R10 bullets 1 and 2
remain as noted, no change demanded: (1) verification is skipped, not
failed, when after_capture is False or terminal_address is None; (2) the
age check uses the max session deadline, not actual attempt time.

## 4. Fail-before evidence at e4082ff

Method: copied the 7 changed test files and the new `scripts/dom_act.py`
from the amend worktree into the base worktree at `e4082ff`, then ran the
suites there. The counts reproduce the amend log exactly.

| Suite | Base result |
|---|---|
| test_first_action | 61 tests, FAILED, failures 3, errors 2, 0.604s |
| test_type_verification | 47 tests, FAILED, failures 1, errors 7, 0.313s |
| test_zen_dom | 25 tests, FAILED, failures 6, errors 9, 0.017s |
| test_dom_act | 10 tests, FAILED, errors 9, 0.004s |
| test_pick4_fastpath | 28 tests, FAILED, errors 5, 0.078s |
| test_session_continuation | 10 tests, OK, 0.265s (expected, item 1 passes on old code too) |
| test_keyboard_preflight | 32 tests, OK, 0.112s (expected) |

Key failures, each proving the test catches the bug it guards:

- `test_click_type_frame_changed_by_click_only_fails`
  (test_type_verification): FAIL on old code, the R1 demo. The old
  whole-frame check passes on a click-only frame change.
- `test_stale_given_observation_pointer_only_refused`
  (test_first_action): FAIL on old code, the item 2 flip.
- `test_stale_given_observation_refusal_key_type_offers_window_only`
  (test_first_action): FAIL on old code, item 7.
- `test_session_type_verified_and_error_code_surfaced_in_envelope` and
  `test_fallback_type_verified_and_error_code_surfaced_in_envelope`
  (test_first_action): ERROR on old code, item 6, fields missing.
- `test_non_json_response_becomes_zen_dom_error` and
  `test_response_without_value_becomes_zen_dom_error` (test_zen_dom):
  ERROR and FAIL on old code, item 8.
- `test_failed_restore_is_raised_not_swallowed` and
  `test_failed_restore_after_scan_is_raised` (test_zen_dom): FAIL on old
  code, item 9.
- `test_hung_handle_stops_scan_and_raises_wedge` and
  `test_raw_timeout_per_handle_stops_scan` (test_zen_dom): FAIL on old
  code, item 10.
- `test_switch_not_taking_effect_raises` (test_zen_dom): FAIL on old code,
  item 11.
- `test_viewport_origin_returns_moz_inner_screen`,
  `test_locate_point_is_rect_center_in_image`,
  `test_hit_check_passes_uncovered_fails_covered`,
  `test_focus_check_reads_active_element`, `test_field_value_and_verify_typed`,
  `test_grounding_accuracy_across_cases`,
  `test_g30_dom_point_hits_and_old_eye_point_misses` (test_zen_dom,
  test_pick4_fastpath, test_dom_act): ERROR on old code, item 12.

## 5. C12 evaluation: is viewport_origin correct

C12 is the coordinate conversion layer from the crawl log
(`improvements/worker-click-crawl-doma11y-log.md:209`): CSS viewport px
to screen px, covering window screen position, devicePixelRatio and
scaling, viewport offset inside the window (chrome height, sidebar
width), and scroll offset.

Verdict: CORRECT on the evidence available. The deciding lines:

- `scripts/zen_dom.py:367-383`. `viewport_origin()` returns
  `[window.mozInnerScreenX, window.mozInnerScreenY]` and validates both
  are non-bool numbers, else raises ZenDomError. mozInnerScreenX/Y is the
  viewport origin on the screen, so it already includes the chrome height
  and sidebar width. No per-layout calibration is needed, which is better
  than the crawl proposal of measuring URL bar and sidebar heights.
- `scripts/fastpath.py:152-167`. `dom_rect_to_screen_point` returns
  `origin + rect center`. Scroll offset is already inside
  getBoundingClientRect by definition, so nothing else is needed.
- `scripts/fastpath.py:169-184`. `dom_rect_to_image_point` is the exact
  algebraic inverse of `cu.image_point`: screen equals origin plus rect
  center, then image equals (screen minus region origin) times image size
  over region size. The forward map `cu.image_point` was proven live on
  the laptop (calibration_e2, P1 0px, P2 1px), and the same formula is
  stated as truth in `scripts/calibration_e2.py`: "Truth screen =
  (mozInnerScreenX + rect.cx, mozInnerScreenY + rect.cy)".
- The 7-case G30 suite (`tests/test_pick4_fastpath.py:488-541`) passes
  7/7, above the 90% bar. Case 1 reproduces the incident: Brave window
  [2533,914,901,1176], field x 86..526, y 1101..1164, center (306,1132.5);
  the DOM point hits and the old eye point (250,1037) misses 64px above.
  Case 6 models a 100px chrome offset with a viewport-relative rect and
  still hits. Case 7 models a scale-2 capture (image 1802x2352, region
  901x1176).

Two limits, both owed live work, not code errors in this diff:

- No devicePixelRatio factor. None is needed on the laptop: the incident
  numbers show the observation pipeline at 1:1 (window 901x1176, image
  901x1176), and the calibration_e2 live proof validates the formula
  without a DPR factor. Adding one without live measurement would break
  the proven chain. If the laptop display scale ever changes, the
  calibration must be re-proven live.
- No AT-SPI cross-check at runtime. The crawl demanded it as the cheapest
  accuracy proof before trusting any DOM click point. That proof is the
  job of the separate 2-vision benchmark worker on the laptop, not of this
  diff, and it is still owed. See section 7.

## 6. Verdict: GO

No errors to fix. All 12 items are in the code at the stated lines, all 6
suites pass on the amend code, fail-before reproduces exactly on the base
code, the 12-module neighbor set shows no regression (only the 2
pre-existing umask failures, identical on base), and C12 viewport_origin
matches the live-proven calibration_e2 truth formula.

## 7. What could not be checked

- Live browser proof. These suites use fakes; no Zen or Brave ran on this
  VM. The live accuracy proof (DOM point versus eye point, accuracy at
  least 90% on real clicks) is owed by the 2-vision benchmark worker on
  the laptop. Nothing in this diff substitutes for it.
- Full test discover. The amend log claims 1752 tests with 2 failures, 4
  errors and 17 skipped, all pre-existing or environment. I did not re-run
  full discover. The 13-suite run (315 tests OK) and the 12-module
  neighbor set (209 tests, only the 2 pre-existing umask failures) cover
  the regression surface the councils flagged.
- The other commits in the range (batch 7 corrections, ZT-C, crawls,
  reviews, coord logs) were not verified here; they are not CLICK-AMEND
  work.

## Corrections after the batch 8 council and redteam review

Applied to this report by the batch 8 fix agent, each number recomputed
first-hand from the code and the diff at `4b7d6ac` / `e4082ff..4b7d6ac`.
No code change; the GO verdict is unaffected.

- W1 (redteam): 6-suite total "1.385s" was wrong; the listed per-suite
  times sum to 1.375s (0.629+0.424+0.005+0.001+0.074+0.242). Fixed in the
  section 2 table.
- Item 5 (council 2, redteam W2): "_fresh_observation has exactly one
  caller in the repo" was wrong; there are 9 call sites: 1 production
  caller (`run()` at `scripts/first_action.py:470`) plus 8 direct test
  calls (`tests/test_first_action.py:809, 823, 843, 856, 868, 878, 892,
  904`). Fixed to "exactly one production caller". The R2 subsumption
  stands.
- Item 2 (council 2): refusal range was "478-498"; `if rejected is not
  None:` is at line 474 and `return 1` at 498. Fixed to 474-498, here and
  in item 5.
- Item 12 (council 2): the parenthetical wrongly attributed the counter
  asserts to `tests/test_type_verification.py:195`. Only
  `tests/test_dom_act.py:227-228` asserts `observes_added` 0 and
  `act_observes` 0; the 195 test asserts the observe call sequence
  `['fresh', 'persist', 'persist']`. Fixed. The "no extra observes" claim
  stands.
- R10 bonus (redteam W3): bullets 1 and 2 were misstated as "(session
  creation failure type, 200-char error truncation)". Actual R10
  (`improvements/worker-click-rt-log.md:94-100`): (1) verification is
  skipped, not failed, when after_capture is False or terminal_address is
  None; (2) the age check uses the max session deadline, not actual
  attempt time. Fixed.
- Non-amend enumeration (redteam M2): the range has 41 commits (8 amend
  + 33 others); the report named 14 and covered 8 as "coord logs", leaving
  11 unlisted. Completed: ZT-C `7437384`, `0b92542`, `646cf71`; crawls
  `7b85472`, `96f49ac`; ZT-B `f2999c7`, `88d3d0a`; CODEX comparisons
  `238b528`, `9350db7`; Y13g `ab0b62c`, `167a2e9`; the 8 coord logs are
  `ce2b4d7`, `7d3db26`, `07dcb0b`, `9a1be5c`, `0db32fc`, `96ce916`,
  `5dacdeb`, `9e6c80c` (all verified with `git log`).
- Scope sentence (redteam M4): clarified. 15 changed lines mention
  `image_point` (new calls, the new `dom_rect_to_image_point` function,
  docstrings), but zero diff lines touch the `image_point`, `move`, or
  `_check_entry_pyc` definitions.
- Run times and build failure (redteam U1/U2): marked as unlogged. The
  "21:44 UTC and re-runs 22:01 UTC" times have no artifact on disk, and
  there is no build log on disk; `pkg-config --exists gtk4` fails, which
  confirms the cause but not the build failure itself.

NOT applied, because first-hand verification showed the report was already
correct and the council 2 correction was wrong:

- Council 2 item 6: the session copy is at lines 543-544
  (`type_verified` at 543, `error_code` at 544), exactly as the report
  said. Council 2 claimed 543-545; `grep -n` in the amend worktree shows
  the `error_code` assignment at 544.
- Council 2 item 9: `def _try_restore` is at line 227, exactly as the
  report said. Council 2 claimed 226; `grep -n` in the amend worktree
  shows the def at 227 and the first docstring line at 228.
