# Batch 8 fix: corrections to the task 2 (CLICK-AMEND) report

Fix agent, 2026-11-22. Source report `docs/clone1-amend-verify-20261122.md`
(254 lines before, 324 lines after, 0 em/en dashes). Every number below
was recomputed first-hand from the code and the diff in the worktrees
`~/workspace/b8t2/amend` at `4b7d6ac` and `~/workspace/b8t2/base` at
`e4082ff`. No code change; the GO verdict is unaffected. Nothing committed
or pushed; coord untouched, per instructions.

## Corrections applied

### Council 2

- **Item 5 (also redteam W2, applied once).** Old: "`_fresh_observation`
  has exactly one caller in the repo, `run()` at
  `scripts/first_action.py:470`". New: "exactly one production caller in
  the repo, `run()` at `scripts/first_action.py:470` (plus 8 direct test
  calls in `tests/test_first_action.py:809, 823, 843, 856, 868, 878, 892,
  904`)". Source: `grep -rn _fresh_observation scripts/ tests/` in the
  amend worktree returns 9 call sites: 1 production call at
  `scripts/first_action.py:470` and 8 test calls at the listed lines.
  (Two more grep hits are test function names containing the string, not
  calls.) The R2 subsumption stands.
- **Item 2.** Old: refusal range "478-498". New: "474-498". Source:
  `grep -n "if rejected is not None"` returns line 474, and `return 1`
  is at line 498. The same range was fixed in item 5, which cites it.
- **Item 12.** Old: parenthetical attributed the counter asserts to
  `tests/test_type_verification.py:195` as well as
  `tests/test_dom_act.py:227-228`. New: only `tests/test_dom_act.py:227-228`
  asserts `observes_added` 0 and `act_observes` 0; the 195 test
  (`test_click_type_enter_uses_no_extra_observes`) asserts the observe
  call sequence `['fresh', 'persist', 'persist']`. Source:
  `grep -c "observes_added\|act_observes" tests/test_type_verification.py`
  returns 0; `sed -n '195,230p'` of that file shows the sequence assert.
  The "no extra observes" claim stands. The `:132` covered-refusal and
  `:233` miss-never-types references were kept.

### Redteam

- **W1.** Old: 6-suite total "1.385s". New: "1.375s". Source: the listed
  per-suite times sum to 1.375s (0.629+0.424+0.005+0.001+0.074+0.242 =
  1.3749999999999998 in Python). Fixed in the section 2 table.
- **W3.** Old: R10 bullets 1 and 2 described as "(session creation
  failure type, 200-char error truncation)". New: (1) verification is
  skipped, not failed, when after_capture is False or terminal_address is
  None; (2) the age check uses the max session deadline, not actual
  attempt time. Source: `improvements/worker-click-rt-log.md:94-100`, read
  in the amend worktree. Bullet 3 (range check before `current_handle()`)
  was correct and is unchanged.
- **M2.** Old: non-amend enumeration named 14 commits and covered 8 as
  "coord logs", leaving 11 unlisted. New: full enumeration of all 33
  non-amend commits in the range (41 total). Source: `git rev-list --count
  e4082ff..4b7d6ac` returns 41; each of the 11 hashes was verified with
  `git log` (7b85472, 96f49ac, 7437384, 0b92542, 646cf71, 238b528, 9350db7,
  f2999c7, 88d3d0a, ab0b62c, 167a2e9) and the 8 coord logs were confirmed
  as COORD-CLICK log commits (ce2b4d7, 7d3db26, 07dcb0b, 9a1be5c, 0db32fc,
  96ce916, 5dacdeb, 9e6c80c).
- **M4.** Old: "zero diff lines touch `image_point`, `move`, or
  `_check_entry_pyc` definitions". New: "15 changed lines mention
  `image_point` (new calls, the new `dom_rect_to_image_point` function,
  docstrings), but zero diff lines touch the `image_point`, `move`, or
  `_check_entry_pyc` definitions". Source: `git diff e4082ff..4b7d6ac --
  scripts tests | grep "^[+-]" | grep -v "^[+-][+-]" | grep -c
  "image_point"` returns 15; a grep for added/removed `def image_point`,
  `def move`, or `def _check_entry_pyc` lines returns nothing.
- **U1/U2.** Old: run times "21:44 UTC and re-runs 22:01 UTC" and the
  "scripts/build.py fails here on missing gtk4 dev packages" claim were
  stated without qualification. New: both marked as unlogged in the
  report. Source: no run log or build log exists on disk
  (`~/workspace/b8t2/` holds only `amend/`, `base/`, `c3-logs/`; no
  `*build*.log` under `~/workspace`). `pkg-config --exists gtk4` fails,
  which confirms the cause for U2 but not the build failure itself.

## Corrections NOT applied

Two council 2 corrections were checked first-hand and found wrong; the
report was already correct, so they were not applied. Both are recorded
in the report's own corrections section.

- **Council 2 item 6.** Council 2 claimed the session copy spans
  543-545, with the `error_code` assignment at 545. Verified wrong:
  `grep -n` in the amend worktree shows `envelope['type_verified'] =
  session_result.get('type_verified')` at 543 and
  `envelope['error_code'] = session_result.get('error_code')` at 544.
  The report's "543-544" is correct.
- **Council 2 item 9.** Council 2 claimed `def _try_restore` is at 226,
  with 227 the first docstring line. Verified wrong: `grep -n "def
  _try_restore"` returns 227, and `sed -n '226,228p'` shows line 226
  blank, 227 the def, 228 the first docstring line. The report's "227"
  is correct.

## Worktree cleanup (redteam M5)

Base worktree `~/workspace/b8t2/base` was left dirty by the task 2 agent's
fail-before copies: 6 modified test files and 2 untracked new files
(`scripts/dom_act.py`, `tests/test_dom_act.py`). Restored with
`git checkout -- .` and removal of the 2 untracked files. Verified with
`git status --short`: empty, HEAD still `e4082ff`. The amend worktree was
not touched and is clean.

## Verification of the fixed report

- `wc -l docs/clone1-amend-verify-20261122.md`: 324 lines (was 254).
- 0 em dashes, 0 en dashes.
- No old wrong figure remains in the body outside the corrections
  section: a scan of the text before the "## Corrections after" heading
  finds no "1.385s", "478-498", "exactly one caller in the repo",
  "200-char error truncation", or the old incomplete enumeration.
- New figures present in the body: "1.375s", "474-498" (items 2 and 5),
  "exactly one production caller", "max session deadline", the full
  33-commit enumeration, the 15-line scope clarification, and the
  unlogged marks for U1/U2.

## Could not apply

Nothing. Every correction in the council 2 and redteam lists was either
applied or, for the two council 2 items above, refuted first-hand with
the evidence recorded. The task 2 agent's 255-line handoff claim (M1)
needs no doc change: the report itself makes no line-count claim, and
`wc -l` says 254 before the fix, 324 after.
