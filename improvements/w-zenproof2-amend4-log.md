# W-ZENPROOF2-AMEND4: close the review conditions on W-ZENPROOF2-AMEND3

Owner: Pham Tuan. Worker: W-ZENPROOF2-AMEND4, independent (not
W-ZENPROOF2-AMEND3, not W-ZENPROOF2-AMEND2, not W-ZENPROOF2-AMEND,
not W-ZENPROOF2-FIX, not W-ZENPROOF2, not COORD-CLICK-9). Report
goes to Muse tong, not directly to Pham Tuan. No live proof
re-run, no tab opened, navigated, or deleted in Pham Tuan's Zen.
All verification is code/unit level only. No em dash or en dash
anywhere in this file. No personal info.

## 0. Task receipt and sources (21:02 +07, 22/11/2026)

- Task received ~21:02 +07. T+0m. Branch todolist-push, repo
  ~/workspace/computer-use-wayland. HEAD at start e48578e
  (redteam review of amend 3).
- The amend under amendment (3 commits): 09802c3 (zen-tab.py),
  58df67d (42 unit tests), 24050c1 (amend log). All 4 reviews GO
  WITH CONDITIONS except Council 2:
  - Council 1, 3bb2bb5: GO WITH CONDITIONS, C1 (doc-only: the
    docstring falsely cites run 1 as support for
    within-invocation handle stability).
  - Council 2, 86d6f89: GO, no conditions.
  - Council 3, fb9b07f: GO WITH CONDITIONS, C1 (same false
    run-1 citation; mandatory, doc-only).
  - Redteam, e48578e: GO WITH CONDITIONS, C1 (H1 MEDIUM:
    concurrent open + stale return WITHOUT creation defeats the
    set-difference check; add a second baseline +
    regression tests Q-J1/Q-J2, or written risk acceptance),
    C2 (H2 LOW, doc-only: qualify the re-mint sentence to the
    pre-fetch timing, folded into the Councils 1 and 3
    docstring rewrite), C3 (H3 LOW, test-only: pin hypr-first
    ordering in the phase-4 helper), C4 (doc-only: record the
    during-POST residual in the follow-up log).
- Sources read before any edit: all 4 amend-3 reviews in full,
  the amend-3 log, the current zen-tab.py cmd_open, run2.py
  phase4 (lines 483-525), the test file, and the redteam
  probes /tmp/redteam-amend3-probes.py (Q-A to Q-D, Q-J) and
  /tmp/redteam-amend3-qe.py (Q-E), read in full.

## 1. Time log (wall-clock Asia/Ho_Chi_Minh)

- 21:02 +07, T+0m: task received, 4 reviews + amend-3 log read.
- 21:03 +07, T+1m: code + test file + Q-J/Q-E probes read.
- 21:03 +07, T+1m: baseline confirmed (suite 42/42 OK; Q-J1
  and Q-J2 both hijack + delete X on amend-3 code, both modes;
  Q-E: the 3 amend-3 phase-4 tests pass against reordered run2,
  0 failures; run-1 evidence spot-checked).
- 21:05 +07, T+3m: zen-tab.py amended (second baseline +
  docstring rewrite). Test file amended (Q-J2 test, Q-J1
  residual pin, helper records hypr calls + calls_out,
  active-window and identity tests pin hypr-first).
- 21:06 +07, T+4m: suite 44/44 OK; Q-J2 refuses on amended
  code, Q-J1 still hijacks (residual, pinned); Q-E now fails
  2 of 3 on reordered run2 (pin bites); G0a 177/177, G0b both
  programs validate, fixture sha matches. Log written,
  committing.

## 2. What was closed, condition by condition

### H1 (Redteam C1, MEDIUM): second baseline against the no-creation stale return

- zen-tab.py cmd_open now captures a second baseline
  `just_before = _handles(z)` immediately before POST
  /window/new (after the pre-check scan), and requires the
  set difference against BOTH baselines to be exactly
  {new_handle} added and nothing removed. The new check
  refuses with 'new tab handle set changed unexpectedly since
  just before the open (added %d, removed %d); refusing to
  navigate or close'. The membership check, the count gate,
  and the first set-difference check are kept unchanged, in
  the same order, as defense in depth with distinct error
  messages. The second baseline costs one extra GET; a
  transport error there raises ZenDomError, fail-closed, and
  adds no new failure mode.
- Regression test added
  (test_open_refuses_no_creation_stale_return_at_scan, Q-J2,
  both select modes): X opens during the pre-check scan, and
  /window/new returns X's handle WITHOUT creating a tab.
  Asserts the 'handle set' raise, zero deletions, 3 tabs,
  owner URL unchanged, example URL unchanged, X URL unchanged
  (https://x.example/). Adapted from the redteam Q-J2 probe.
- Baseline first, by the redteam probe itself
  (/tmp/redteam-amend3-probes.py, re-run by me): on the
  amend-3 code, Q-J2 RETURNED ok in both modes and cleanup
  close DELETEd X (tabs left 2). After the fix, the same
  probe shows Q-J2 REFUSED in both modes with 'new tab
  handle set changed unexpectedly since just before the open
  (added 0, removed 0)'. The damage no longer reproduces.
- The new test is a genuine regression test, proven by a
  baseline worktree: I checked out 24050c1 (amend-3 code)
  to a temp worktree, copied the new test file in, and ran
  the suite: Ran 44, FAILED (failures=1), and the single
  failure is the Q-J2 test ('_FakeZenDomError not raised').
  On the amended code it passes. Worktree removed
  afterwards.

### Q-J1 is NOT fixed by the second baseline (correction to the brief, recorded honestly)

- The task brief asked for regression tests for Q-J1 and Q-J2
  "asserting the refuse" after the fix. That expectation is
  wrong for Q-J1, and Redteam's own review says so in section
  6 G1: the second baseline does not catch churn DURING the
  /window/new round-trip itself, because X does not exist when
  either baseline is captured. I verified this directly: on
  the amended code, the redteam Q-J1 probe still RETURNED ok
  in both modes, X was navigated to the fixture URL, and
  cleanup close DELETEd X (tabs left 2), exactly as on
  amend-3 code.
- I did not write a Q-J1 test asserting a refuse that does
  not happen. Instead I pinned the residual as a known
  limitation, following the convention already used in this
  test file (the unreadable-fixture and silent-restore tests
  pin known limitations the same way):
  test_open_no_creation_stale_return_during_post_is_residual
  (both select modes) asserts cmd_open returns ok, the
  navigate rewrites X, and cleanup close deletes X. A future
  fix that closes Q-J1 must update this test, not pass
  silently. The residual is recorded in section 4 (C4) as
  narrowed, not eliminated.

### Doc-only (Council 1 C1 + Council 3 C1 + Redteam C2): the handle-stability paragraph rewritten honestly

- zen-tab.py module docstring: the false run-1 citation is
  removed. The paragraph now states the assumption is
  unproven by live evidence: no live invocation has run
  these checks (run 1 aborted in phase 1 before any open,
  and the checks were added after the last live run, attempt
  2). The only support is indirect: run 2's ephemerality was
  cross-session (two lists a minute apart, separate
  processes), and Gecko handles are per-window UUIDs.
- The re-mint sentence is qualified to the pre-fetch timing,
  per Redteam H2: a re-mint before the set-difference fetch
  is refused by that check fail-closed; a re-mint after the
  fetch is caught by the (c) check, the post-navigate check,
  and the handler's handle check, or is harmless (a re-minted
  owner handle leaves the run correct). Council 3's proposed
  replacement text kept the overbroad sentence verbatim; the
  redteam Q-A2/Q-A3 probes show why it needed the
  qualification, and this rewrite applies it.
- The open-checks paragraph in the same docstring now also
  names the second-baseline requirement next to the count +1,
  membership, and set-difference requirements.
- Evidence for the correction (spot-checked by me, not just
  copied from the councils): run-1.json outcome 'error',
  error "active window is not Zen (0x56307e202df0); aborting",
  wall_ms 3473.8; w-zenproof2-log.md line 109 "run 1 never
  reached phase 2"; the pre-fix cmd_open at a355002 fetches
  `before`, posts /window/new, navigates directly, then
  checks the title: no scan, no (c) check, no post-navigate
  check. Run 2 log sections 0, 1, 6 record the cross-session
  ephemerality (15 of 15 comparable URLs with different
  handles between two lists a minute apart).
- The amend-3 log is NOT edited: it keeps the false citation
  as a committed historical record, exactly as amend 3 did
  for the amend-2 log. The correction lives here, in this
  log, and in the docstring itself.
- No re-review is needed for this doc fix alone, per Council
  3 C1 (a follow-up commit plus the correction in its log is
  enough).

### H3 (Redteam C3, test-only): hypr-first ordering pinned in the phase-4 helper

- The _run_phase4 helper now records hypr calls too: the
  hypr mock is a recording side_effect, not a plain
  return_value. It also takes a calls_out= parameter: a
  caller that needs the calls on the raise path passes its
  own list, and the helper appends to it, so the list
  survives the raise (the runner is lost to the test when
  phase4 raises). The 5 existing phase-4 tests run unchanged
  through the new helper.
- test_phase4_active_window_moved_raises now asserts the
  only call before the raise was the hypr read itself
  (kinds == ['hypr'], hypr args ('activewindow',)), not
  just the RuntimeError message.
- test_phase4_switch_before_send_and_program_identity now
  asserts kinds == ['hypr', 'tab', 'oneshot'] in that order,
  the hypr call args are ('activewindow',), the tab call args
  are ('switch', TARGET), the oneshot program IS SEND_PROGRAM
  (identity), and the intent is INTENT.
- The pin bites, proven by the redteam Q-E probe
  (/tmp/redteam-amend3-qe.py, re-run by me against the new
  test module): on the reordered run2 (hypr check moved after
  the switch), the 3 tests now run 2 failures out of 3 (was
  0 failures before this fix). The active-window test fails
  because the switch ran before the raise, and the identity
  test fails because the kinds are ['tab', 'hypr',
  'oneshot'] instead of ['hypr', 'tab', 'oneshot']. The
  envelope-ok-false test still passes, as it should: it pins
  the final gate, not the order.

### C4 (Redteam): the during-POST residual recorded

- The during-POST residual remains: a tab opening inside the
  /window/new round-trip plus a stale return without creation
  (Q-J1) still defeats both baselines, because neither
  baseline can contain a tab that did not exist when it was
  captured. The second baseline narrows the vulnerable window
  from [cmd_open start, fetch] to the /window/new round-trip
  itself. It is narrowed, not eliminated: WebDriver offers no
  atomic verify-and-create, same class as the F1 race. The
  Q-J1 residual pin test records it in the suite.
- Wording precision notes from Council 3 (G1, G2, G4),
  recorded here as the follow-up log should:
  - G1: amend 3 does not narrow the F1 race itself (the
    TOCTOU between the (c) check and the navigate); it
    narrows the concurrent-churn case. The F1 race was
    narrowed by amend 1's post-navigate check. Amend 4
    likewise narrows the concurrent-churn case, not the F1
    race.
  - G2: the cmd_close post-DELETE scan dates from the
    original run kit (2d1dc82), not from amend 1. It
    predates amend 2 and 3 and was not introduced by them.
  - G4: the section 4 reference "limitations recorded in the
    amend 2 log section 4 still hold" (amend-3 log) excepts
    the corrected "never a wrong navigate" wording, which
    section 2 of that log corrects explicitly. The
    limitations themselves still hold.

### Drive-by (Council 3 G3, minor, same docstring area)

- The test-file module docstring bullet for the amend-3
  P-C check said the handle set must differ "by more than
  exactly the new handle added". The check also refuses when
  the added set is a different singleton or empty, not only
  when it is larger. Fixed to "by anything other than exactly
  the new handle added and nothing removed". Two amend-4
  bullets added to the same docstring (second baseline +
  Q-J1 residual pin; hypr-first pin).

### Considered and not taken

- A pre-navigate check that the new tab is still
  about:blank would catch the probe's Q-J1 X (its URL is
  https://x.example/), but it is a heuristic, not a proof:
  a concurrent about:blank open plus a stale return would
  still pass it, and it adds a new assumption (a real
  /window/new tab is about:blank at that moment) that could
  false-refuse a real run. No review asked for it. Left for
  the coordinator to consider, not implemented here.

## 3. Verification (code/unit only, no live tab operation)

- py_compile OK for zen-tab.py and the test file.
- New tests tests/test_zenproof2_fix.py: 44/44 OK
  (python3 -m unittest tests.test_zenproof2_fix, 0.034s).
  42 old tests still pass unchanged; 2 new tests added
  (1x Q-J2, 1x Q-J1 residual pin); 2 phase-4 tests
  strengthened (active-window, identity).
- Baseline worktree at 24050c1 (amend-3 code) + new test
  file: Ran 44, FAILED (failures=1), the single failure the
  Q-J2 test ('_FakeZenDomError not raised'). The Q-J1
  residual pin passes there too, as it must (it pins
  behavior present on both codes). Worktree removed
  afterwards.
- Q-J probe re-run against the amended code: Q-J2 REFUSED
  in both modes ('new tab handle set changed unexpectedly
  since just before the open (added 0, removed 0)'); Q-J1
  still RETURNED ok in both modes and cleanup deleted X
  (the pinned residual).
- Q-E probe re-run against the new test module: 3 tests, 2
  failures on reordered run2 (was 0 failures). The pin
  bites.
- G0b: both programs pass code_exec.validate_program with no
  exception (PROBE Module, SEND Module), same check the run
  used.
- G0a suite still passes: python3 -m unittest
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec, Ran 177 tests, OK (12.906s).
- 0 em dash (U+2014) and 0 en dash (U+2013) in both changed
  files (zen-tab.py, test file), counted by grep.
- Fixture untouched: sha256 of tests/two_vision_fixture.html
  is 147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6
  cbf, identical to FIXTURE_SHA.
- NOT verified (needs a live run, out of scope for this
  worker): the amended runner against real Zen. The next
  proof is a fresh run number with a fresh intent/message,
  after council + redteam review of this amend.

## 4. Open items for the coordinator (not fixed here)

- Live verification is still owed by design (code/unit only
  here). The next proof is a fresh run number with a fresh
  intent/message, after council + redteam review of this
  amend. It copies the fixed run2.py; run 1 must not be
  re-run as-is.
- The Muse chat tab closed by run 2 attempt 2
  (https://muse.ai/thread/750c8dae-58fb-4a65-82ac-753e78d6ce93)
  is NOT reopened by this amend. Recovery is the
  coordinator's decision (w-zenproof2-log.md section 11,
  item 1).
- Known limitations still hold, plus the ones named here:
  the WebDriver protocol offers no atomic
  verify-and-navigate and no atomic verify-and-create (the
  F1 residual race is narrowed, not eliminated; the
  set-difference checks narrow the concurrent-churn case
  further but cannot catch a change during the /window/new
  round-trip itself, Q-J1); backend first-match stays a known
  limitation; unreadable tabs stay invisible to URL identity.
  None of them is a live-run gate beyond what the reviews
  already stated. The section 4 reference to the amend-2
  log limitations excepts the corrected "never a wrong
  navigate" wording (Council 3 G4).
- Not closed here (follow-up candidate, not a live-run
  gate): cmd_close's post-DELETE verification reads can
  still raise after a successful DELETE and mask the close
  success (Redteam G1 / Council 1 G1, same shape as H2,
  different site, pre-existing from the original run kit
  2d1dc82, per Council 3 G2). Consequence is a spurious
  error (fail-closed), never a wrong navigate or DELETE.

## 5. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received ~21:02 +07, 22/11/2026. Branch todolist-push,
  HEAD at start e48578e. Fetched origin before committing;
  local HEAD already equalled origin/todolist-push.
- Baseline 21:03 +07: python3 -m unittest
  tests.test_zenproof2_fix, Ran 42 tests, OK. Q-J probe:
  Q-J1 and Q-J2 both RETURNED ok in both modes, cleanup
  deleted X, tabs left 2. Q-E probe: 3 tests, 0 failures on
  reordered run2.
- Run-1 evidence 21:03 +07: run-1.json outcome 'error',
  "active window is not Zen (0x56307e202df0); aborting",
  wall_ms 3473.8; w-zenproof2-log.md line 109 "run 1 never
  reached phase 2"; pre-fix cmd_open at a355002: before,
  /window/new, navigate, title check; no scan, no (c) check,
  no post-navigate check.
- zen-tab.py edits 21:05 +07: just_before capture + second
  set-difference check, docstring rewrite (assumption
  paragraph + open-checks paragraph), comment update.
  py_compile OK after edit.
- Test file edits 21:05 +07: Q-J2 test, Q-J1 residual pin
  test, _run_phase4 records hypr calls + calls_out param,
  active-window and identity tests pin hypr-first, module
  docstring bullets (amend-3 wording fixed, amend-4 added).
- Suite 21:06 +07: python3 -m unittest
  tests.test_zenproof2_fix, Ran 44 tests in 0.034s, OK.
- Baseline worktree 21:06 +07: git worktree add
  /tmp/amend3-base 24050c1, new test file copied in, Ran 44,
  FAILED (failures=1), single failure the Q-J2 test
  ('_FakeZenDomError not raised'). Worktree removed,
  worktree pruned.
- Q-J probe re-run 21:06 +07: Q-J2 REFUSED both modes
  ('new tab handle set changed unexpectedly since just
  before the open (added 0, removed 0)'); Q-J1 still
  RETURNED ok both modes, cleanup deleted X (pinned
  residual).
- Q-E probe re-run 21:06 +07: 3 tests, 2 failures on
  reordered run2 (was 0 failures).
- G0a 21:06 +07: Ran 177 tests in 12.906s, OK.
- G0b 21:06 +07: PROBE Module, SEND Module.
- Fixture sha 21:06 +07:
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6
  cbf, matches FIXTURE_SHA.
- Dash counts 21:06 +07: U+2014 0, U+2013 0 in both changed
  files.
- Diff scope: 2 code/test files plus this log (zen-tab.py,
  test file). run2.py was NOT changed by this amend (the
  phase-4 tests execute its existing code). The pre-existing
  dirty tests/realistic/clone1-batch3/results.json was never
  touched and is never committed by me. The untracked prompt
  files in improvements/ belong to other lanes and are not
  mine.
- Files changed (mine only, explicit pathspecs):
  improvements/c5-zenproof-runs/zen-tab.py,
  tests/test_zenproof2_fix.py,
  improvements/w-zenproof2-amend4-log.md (new, this file).
- Commits, pushed, ls-remote verified: (hashes in the report
  to Muse tong).
- No live Zen tab was opened, navigated, or deleted. No proof
  re-run. No reviewer spawned (Muse tong spawns council +
  redteam after this).
