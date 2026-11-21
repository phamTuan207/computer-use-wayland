# Batch 8 redteam: audit of the CLICK-AMEND verification report, 2026-11-22

Auditor: batch 8 redteam, independent of the task 2 agent. Report audited:
`docs/clone1-amend-verify-20261122.md` (254 lines by `wc -l`; the task 2
agent's completion message said 255, wrong by 1, see M1). Method: read the
report in full, then re-verified every checkable fact first-hand in the two
worktrees (`~/workspace/b8t2/amend` at `4b7d6ac`,
`~/workspace/b8t2/base` at `e4082ff`), re-running suites myself. I am
auditing the REPORT, not the diff itself.

## Verdict: GO SURVIVES

The GO conclusion survives. All 12 items are in the code at the stated
lines, all 6 suites pass on the amend code (counts reproduced exactly),
fail-before reproduces exactly on the base code (every failure/error count
and every named key failure reproduced), the 12-module neighbor set shows
no regression (exactly the same 2 pre-existing umask failures on both
trees), and C12 viewport_origin matches the live-proven calibration_e2
truth formula. The three wrong facts below are all in supporting details:
an arithmetic total, a caller count, and a bonus-paragraph description.
None of them touches the basis for GO.

## Wrong facts (3)

### W1. 6-suite total time "1.385s" is wrong; the listed times sum to 1.375s

The report's own table lists 0.629 + 0.424 + 0.005 + 0.001 + 0.074 +
0.242 seconds. That sums to 1.375s, not the 1.385s in the "Total 6
suites" row. Even allowing 3-decimal rounding, the true sum cannot exceed
1.378s (each listed value can hide at most +0.0005). The total is wrong
by 0.01s. My own re-runs gave 0.589 + 0.418 + 0.005 + 0.001 + 0.071 +
0.232 = 1.316s, so the per-suite times are plausible single
measurements under load variance; only the total row is arithmetically
inconsistent with its own table. Fix: change the total to 1.375s.

### W2. Item 5: "_fresh_observation has exactly one caller in the repo" is wrong

There are 9 call sites, not 1. One production caller,
`scripts/first_action.py:470` inside `run()`, which the report cites
correctly. Plus 8 direct test call sites in
`tests/test_first_action.py` at lines 809, 823, 843, 856, 868, 878, 892
and 904, each calling `first_action._fresh_observation(...)` directly.
(Grep hits in `test_observation_contract.py:78` and
`test_phase3_c1.py:39` are test names containing the substring, not
calls, and are not counted.) The true statement is "exactly one
production caller". The R2 subsumption conclusion itself still stands:
the refusal block at `scripts/first_action.py:478-498` fires whenever
`rejected is not None`, which I verified by reading the code, so no
proceed path remains regardless of the caller count. Fix: correct the
caller count to 9 (1 production + 8 test).

### W3. R10 bonus paragraph misstates R10 bullets 1 and 2

The report says: "R10 bullets 1 and 2 (session creation failure type,
200-char error truncation) remain as noted". That is not what R10 says.
R10 is defined in `improvements/worker-click-rt-log.md:94-100`
("minor, noted, no change demanded"). Its actual bullets are: (1)
verification is skipped, not failed, when after_capture is False (ok
True, type_verified None) and when terminal_address is None; (2) the age
check uses the max session deadline, not actual attempt time
(`first_action.py:292-325`). Neither bullet mentions session creation
failure type or 200-char error truncation; a repo-wide grep finds no
such wording attached to R10 anywhere. Bullet 3 is correctly identified
and correctly fixed (range check before `current_handle()` at
`scripts/zen_dom.py:288-294`, verified by reading the code). Fix: replace
the parenthetical with the real bullets 1 and 2.

## Unverified claims stated as done (2)

### U1. Run times "2026-11-21 21:44 UTC and re-runs 22:01 UTC" have no artifact

No run log, output file, or timestamped artifact is cited for these
times, and none was found on disk. The times are consistent with the
task 2 agent completing at 22:03:18 UTC, but they cannot be confirmed
from the worktrees. The suite results themselves were re-verified by my
own runs, so this affects only the stated run times, not the results.

### U2. "The full scripts/build.py fails here on missing gtk4 dev packages" has no build log

No build output or log is cited. I confirmed the stated cause:
`pkg-config --exists gtk4` fails on this machine, so the gtk4 dev
packages are indeed missing. But the build.py failure itself was not
observed by me and has no artifact. The claim is half corroborated
(cause confirmed, failure itself unlogged).

## What survived (verified first-hand)

- Commit range: the 8 CLICK-AMEND commits listed (e704187, e10fef4,
  7d37d60, 8e52ba9, eb9066a, 90b7026, 96a9e46, 4b7d6ac) are exactly the
  top 8 of the 41-commit range `e4082ff..4b7d6ac`, with matching
  subjects. The 4 batch 7 correction commits, ZT-C c19c227, the 5 crawl
  commits and the 4 review commits named in the report are all real and
  in the range.
- File counts: the 12 code/test files total 1632 insertions and 116
  deletions (`git diff --numstat` sums: insertions 236+129+81+48+216+282
  +97+20+124+7+132+260 = 1632; deletions 20+0+0+27+34+0+14+3+0+1+0+17
  = 116). Per-file changed-line numbers all match the numstat
  (insertions + deletions) for each file. No non-amend commit in the
  range touched any of the 12 files, so the whole-range numbers are the
  amend numbers.
- Scope: 0 changed lines in the scripts+tests diff touch `def
  image_point`, `def move`, or `_check_entry_pyc` (checked over all
  1748 changed lines). `image_point` (`scripts/cu.py:995-999`) sits
  before the first cu.py hunk (old line 1015), so its definition and
  body are untouched. `def move` (`scripts/cu.py:1724`) is a context
  line in its hunk, body untouched. 15 changed lines do mention
  `image_point`, but only as new calls to `cu.image_point`, the new
  function `dom_rect_to_image_point`, or docstrings (see M4). Zero em
  dashes and zero en dashes in the code and test diff.
- 6 suites re-run by me in the amend worktree, all OK with matching
  counts: test_first_action 61 in 0.589s, test_type_verification 47 in
  0.418s, test_zen_dom 25 in 0.005s, test_dom_act 10 in 0.001s,
  test_pick4_fastpath 28 in 0.071s, test_session_continuation 10 in
  0.232s. Total 181 tests.
- 13-suite set re-run by me: 315 tests OK (2.708s test time, 3.108s
  wall, against the report's 2.239s / 2.81s; times are load-dependent,
  the count is what matters and matches). The amend log
  (`improvements/worker-click-amend-log.md:82`) does claim "315 tests
  OK", so the match claim is correct.
- Neighbor set re-run by me on both trees: 209 tests, exactly 2
  failures on each, both
  `test_core.SecureObservationFiles.test_private_mode_under_any_umask_in_isolated_child`
  (umask '0' and '0o777'), identical on amend (8.019s) and base
  (7.502s). No regression.
- All 12 items' file+line citations checked by reading the code at
  `4b7d6ac`: item 1 (`tests/test_session_continuation.py:252`,
  `pixel_sha256='1111'`); item 2 (`scripts/first_action.py:478-498`,
  refusal covers every batch, `fallback_reason` set, path 'refused',
  return 1; docstring "for any batch" at line 59; flipped test at
  `tests/test_first_action.py:620` asserts code 1, path 'refused',
  session not called); item 3 (`scripts/cu.py:2005`,
  `type_verified=None`); item 4 (`scripts/cu.py:1018` band anchor_y
  plus or minus 12px threshold 50, `:1711` type_anchor, `:1849` focus
  gate, `:1913` type_check hook, `:2050` basis 'dom-value'); item 6
  (`:427-428` envelope init, `:543-544` from session, `:597-599`
  from fallback); item 7 (`:357` loud_substitution_refusal, `:378`
  remedy only when not has_keyboard); item 8 (`scripts/zen_dom.py:197`
  except tuple TimeoutError, OSError, URLError, HTTPException,
  ValueError, with `except urllib.error.HTTPError` first at `:194`;
  missing value raises ZenDomError at `:191`); item 9 (`:227`
  _try_restore, failures raised at `:304-314` and `:331-337`); item 10
  (`:317-332` wedge set and loop broken, restore in finally); item 11
  (`:240` _verify_selected, docstring "handle-LIST index, not a
  verified visual tab order" at `:257-258`); item 12 (all def lines:
  `zen_dom.py:367/384/405/423/436/444`,
  `fastpath.py:152/169/206`, `dom_act.py:38/64/78`; test lines
  `test_dom_act.py:123/132/233`,
  `test_type_verification.py:195`, `test_dom_act.py:227-228` asserting
  `observes_added` 0 and `act_observes` 0).
- Fail-before re-run by me in the base worktree (with the agent's
  copied test files still in place): test_first_action failures 3,
  errors 2; test_type_verification failures 1, errors 7; test_zen_dom
  failures 6, errors 9; test_dom_act errors 9; test_pick4_fastpath
  errors 5; test_session_continuation OK; test_keyboard_preflight OK.
  Every count matches the report exactly. Every named key failure was
  confirmed present in the base runs, including the R1 demo
  (`test_click_type_frame_changed_by_click_only_fails`, the single
  failure in test_type_verification), the item 2 flip, the item 6
  envelope errors, the item 8 conversion errors/failure, the item 9
  and 10 failures, the item 11 switch failure, and the item 12 DOM
  helper errors.
- C12: `scripts/zen_dom.py:367-383` returns
  `[window.mozInnerScreenX, window.mozInnerScreenY]` with non-bool
  number validation; `scripts/fastpath.py:152-167` returns origin +
  rect center; `scripts/fastpath.py:169-200` computes
  `ix = (sx - rx) * iw / rw`, `iy = (sy - ry) * ih / rh`, the exact
  algebraic inverse of `cu.image_point` (`rx + x*rw/iw`,
  `ry + y*rh/ih` at `scripts/cu.py:995-999`); the calibration_e2 truth
  formula is verbatim in `scripts/calibration_e2.py:16-17` ("Truth
  screen = (mozInnerScreenX + rect.cx, mozInnerScreenY + rect.cy)").
  The G30 test (`tests/test_pick4_fastpath.py:488-541`) has exactly 7
  cases with the stated numbers (case 1 Brave window [2533,914,901,1176],
  field x 86..526, y 1101..1164, center (306,1132.5); case 6 100px chrome
  offset with viewport origin [2533,1014]; case 7 scale-2 image
  1802x2352), asserts accuracy at least 0.9 and hits equal to 7, and
  passes as part of the 28 OK in test_pick4_fastpath. The eye point
  (250,1037) sitting 64px above the field top edge is stated at lines
  545-546 and asserted at 556-557.
- Amend log quotes: the "1752 tests with 2 failures, 4 errors and 17
  skipped" figure matches `improvements/worker-click-amend-log.md:139`
  ("1752 tests in 278.334s, same 2 failures + 4 errors + 17 skipped").
  The report honestly states it did not re-run full discover, so this
  is a quoted figure, not a verified one, and is presented that way.

## Minor issues (6)

- M1. The task 2 agent's completion message claimed the report is 255
  lines; `wc -l` says 254. The report itself makes no line-count
  claim, so nothing in the doc needs fixing. This is the same +1
  newline-counting error as prior batches, this time in the handoff
  rather than the doc.
- M2. The non-amend commit enumeration in section 1 is incomplete. The
  range has 41 commits: 8 amend + 33 others. The report names 14 others
  and covers 8 more as "coord logs", leaving 11 unlisted: 7b85472 and
  96f49ac (click-crawl-doma11y appendices), 7437384 (CLICK-BASELINE),
  0b92542 and 646cf71 (ZT-C), 238b528 and 9350db7 (CODEX-DEMO/CMP),
  f2999c7 and 88d3d0a (ZT-B), ab0b62c and 167a2e9 (Y13g). Every commit
  the report does name is real and in range; the list is just not
  exhaustive. It also presents "ZT-C c19c227" and the crawl list as if
  they covered those groups, while 0b92542, 646cf71, 7b85472 and 96f49ac
  belong to the same groups.
- M3. Suite times are load-dependent single measurements, not stable
  facts. My re-runs differed from the report's by up to 0.04s per suite
  (13-suite: 2.708s test time / 3.108s wall against the report's 2.239s
  / 2.81s; neighbor set: 8.019s / 7.502s against 8.037s / 7.690s). The
  counts all match exactly, which is what the verdict rests on. The
  report should not be quoted for exact timings beyond "about".
- M4. The scope sentence "zero diff lines touch image_point, move, or
  _check_entry_pyc definitions" is true for the definitions, but a
  reader grepping the diff for "image_point" will find 15 changed
  lines: new calls to `cu.image_point`, the new function
  `dom_rect_to_image_point`, and docstring references. The conclusion
  (the calibration-proven conversion is untouched) holds, because the
  definition and body of `image_point` are unchanged. A clarifying
  word ("definition" already does this work, but the sentence is easy
  to misread as "no diff line mentions image_point") would prevent
  confusion.
- M5. The report's method for fail-before (copying the 7 changed test
  files and the new `scripts/dom_act.py` from the amend worktree into
  the base worktree) is sound and reproduces the amend log, but the
  base worktree was left dirty with those copies in place (6 modified
  test files, 2 untracked new files). Anyone reusing
  `~/workspace/b8t2/base` must know the copies are there, or the
  worktree needs a `git checkout -- .` and removal of the untracked
  files before reuse.
- M6. The report's section 7 honestly flags what it did not check
  (live browser proof, full discover, non-amend commits). The two C12
  limits (no DPR factor, no runtime AT-SPI cross-check) are correctly
  presented as owed live work, not code errors. No correction needed;
  recorded here so the batch 8 final report does not upgrade them into
  verified claims.

## Corrections owed

Before the batch 8 final report repeats the task 2 numbers, the source
report `docs/clone1-amend-verify-20261122.md` must be corrected:

1. W1: 6-suite total time 1.385s to 1.375s (the sum of the listed
   per-suite times).
2. W2: item 5 caller count: `_fresh_observation` has 9 call sites (1
   production caller `run()` at `scripts/first_action.py:470`, plus 8
   direct test call sites in `tests/test_first_action.py:809, 823, 843,
   856, 868, 878, 892, 904`), not "exactly one caller in the repo".
3. W3: R10 bonus paragraph: bullets 1 and 2 are (1) verification
   skipped when after_capture is False / terminal_address is None, and
   (2) the age check uses the max session deadline instead of actual
   attempt time. Remove "(session creation failure type, 200-char
   error truncation)".
4. M2: complete the non-amend commit enumeration (add the 11 unlisted
   commits) or reword the list as examples ("including") rather than an
   exhaustive-seeming enumeration.
5. M4: clarify the scope sentence so it cannot be misread as "no diff
   line mentions image_point": 15 changed lines mention it as new calls
   and the new `dom_rect_to_image_point` function; only the
   `image_point` definition and body are untouched.
6. U1/U2: either cite the run-time and build-failure artifacts or mark
   the 21:44/22:01 run times and the build.py failure as unlogged
   (the gtk4-missing cause is confirmed by `pkg-config`).

No correction is owed to the GO verdict itself. It survives on the
verified evidence above.
