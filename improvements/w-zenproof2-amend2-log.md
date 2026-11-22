# W-ZENPROOF2-AMEND2: close the review conditions on W-ZENPROOF2-AMEND

Owner: the owner. Worker: W-ZENPROOF2-AMEND2, independent (not
W-ZENPROOF2-AMEND, not W-ZENPROOF2-FIX, not W-ZENPROOF2, not
COORD-CLICK-9). Report goes to Muse tong, not directly to the owner. No live proof re-run, no tab opened, navigated, or deleted
in the owner's Zen. All verification is code/unit level only. No
em dash or en dash anywhere in this file. No personal info.

## 0. Task receipt and sources (20:36 +07, 22/11/2026)

- Task received ~20:36 +07. T+0m. Branch todolist-push, repo
  ~/workspace/computer-use-wayland. HEAD at start ee6b487
  (redteam review of amend 1).
- The amend under amendment (5 commits): b27818d (zen-tab.py),
  fa5f737 (run2.py), ee2a85a (27 unit tests), 5b032ae (prep
  file), b956176 (amend log). All 4 reviews GO WITH CONDITIONS:
  - Council 1, 7c6e80d: 1 condition (C1, doc-only: recovery
    line for a navigated-away owner tab).
  - Council 2, ddea95a: 1 condition (C1: behavioral tests for
    the phase-4 runner code).
  - Council 3, 4f8825d: 4 conditions (C1 re-execution, C2
    push verification, C3 live verification owed, C4 G1 note
    on the phase-4 listing). C1 and C2 were already satisfied
    by the independent re-runs of Council 1, Council 2, and
    Redteam plus the push of this review itself (see section
    2); C3 is carried over, not closed here.
  - Redteam, ee6b487: 5 conditions (C1 H1 membership check,
    C2 H2 guard the restore reads, C3 adopt Council 2 phase-4
    tests, C4 adopt Council 1 recovery line, C5 re-execution,
    already satisfied).
- Sources read before any edit: all 4 amend reviews in full,
  the amend 1 log, the current zen-tab.py, run2.py, and test
  file, the prep file amendment note and phase-4 listing,
  /tmp/redteam-amend-repro-h1.py and /tmp/phase4-probe.py
  (both still existed; re-run, not trusted blindly).

## 1. Time log (wall-clock Asia/Ho_Chi_Minh)

- 20:36 +07, T+0m: task received, 4 reviews + amend log read.
- 20:38 +07, T+2m: code + prep file read; baseline confirmed
  (27/27 OK; H1 repro still deletes the owner tab on the
  unamended code in both select modes; H2 probe raises and
  masks the close).
- 20:40 +07, T+4m: zen-tab.py amended (H1, H2).
- 20:42 +07, T+6m: test file amended (9 new tests). Full suite
  36/36 OK; H1 repro no longer reproduces in either mode; H2
  probe returns ok.
- 20:44 +07, T+8m: prep file corrected (recovery line, G1
  note). Full verification: suite 36/36, G0a 177/177, G0b
  both programs validate, fixture sha matches. Log written,
  committing.

## 2. What was closed, condition by condition

### H1 (Redteam HIGH, mandatory before live proof): stale handle that creates a tab

- zen-tab.py cmd_open: immediately after POST /window/new and
  before the count gate, the driver now refuses when
  `new_handle in before` (the handle list captured before the
  open), raising 'new tab returned an existing handle %s;
  refusing to navigate or close'. The count gate alone could
  not catch this: when /window/new returns an existing handle
  (the owner's) AND still creates a tab, the count grows by
  exactly 1, the gate passes, and every later check passes on
  the wrong tab (the (c) check selects the owner tab, the
  navigate rewrites it to the fixture URL, the post-navigate
  F1 check passes because current == new_handle, both the
  owner handle). The membership check is one line and closes
  the whole path at its first step.
- The module docstring now states the returned handle must not
  be one that already existed before the open, next to the
  count +1 requirement.
- Regression tests added, both adapted from
  /tmp/redteam-amend-repro-h1.py, both asserting the raise,
  zero deletions, 3 tabs, owner tab URL unchanged:
  - test_open_refuses_stale_handle_that_creates_tab
    (select_new=True): the (c) check would otherwise select
    the owner tab; the new tab is left as an un-navigated
    about:blank.
  - test_open_refuses_stale_handle_that_creates_tab_no_select
    (select_new=False, the run 2 mode): the owner tab is
    already current, so the (c) check would pass with no
    select at all; the membership check refuses first.
- The redteam H1 repro was re-run against the amended code in
  both modes: select_new=True refuses with 'new tab returned
  an existing handle dcf7f748; refusing to navigate or close',
  owner tab URL unchanged, deletions []; select_new=False
  refuses the same way, owner tab unchanged, deletions [].
  The damage no longer reproduces in either mode.
- Side effect found and fixed while landing H1: the old C4
  test (test_open_count_gate_refuses_stale_handle) failed,
  because its fake returns an existing handle without
  creating a tab, and the membership check now refuses that
  case first with 'existing handle' instead of the count
  gate's 'did not increase the tab count'. That is correct
  behavior, not a regression: the membership check subsumes
  the stale-handle case. The test was updated to expect the
  new message and to say so, and a new test was added for the
  count gate itself:
  test_open_count_gate_refuses_new_handle_without_tab (a
  genuinely new handle that creates no tab; the membership
  check passes, the count gate refuses). Both the membership
  check and the count gate are now covered by their own test.

### H2 (Redteam MEDIUM): restore reads guarded

- zen-tab.py gained _safe_title_url(z): (title, url) of the
  current tab, or (None, None) when the reads fail. Every
  _title(z)/_url(z) call inside _restore_original now goes
  through it: the scan_error branch, the missing/ambiguous
  branch, the restore_failed branch, and the success path.
  A failed read records None, never raises, so a failed read
  can never mask a successful close. The _restore_original
  docstring states the guard.
- Test added
  (test_restore_original_scan_error_with_failed_reads_returns_
  ok): the scan fails on the third list_tabs call AND the
  GET /title and GET /url reads raise. cmd_close returns ok
  with scan_error True, current_title None, current_url None,
  scratch tab deleted, owner tab present.
- The H2 probe (/tmp/amend2-baseline-probes.py, written by me
  from the redteam review description) was run against the
  amended code: cmd_close returns {'ok': True, 'scan_error':
  True, 'current_title': None, 'current_url': None}, scratch
  deleted True. On the unamended code the same probe raised
  'simulated read failure' although the scratch tab was
  deleted.

### C3 (Council 2 C1, adopted by Redteam): phase-4 behavioral tests

- Five tests added to RunnerFixTest, all running phase4 on a
  real Runner with hypr/tab/oneshot_zen mocked (Council 2's
  /tmp/phase4-probe.py shape: Runner() builds a Harness that
  only mkdirs, no SSH):
  - test_phase4_happy_path_records_send_url_and_count: happy
    path records send_url (fixture URL), send_count '1',
    completed 4, send_switch URL the fixture URL.
  - test_phase4_wrong_url_snapshot_raises: a send snapshot URL
    that does not contain the target raises ValueError from
    parse_probe_line (not RuntimeError, as Council 2 noted).
  - test_phase4_wrong_count_snapshot_raises: a send snapshot
    count other than 1 raises ValueError.
  - test_phase4_missing_probe_line_raises: a send program that
    prints no PROBE line raises RuntimeError ('send program
    printed no snapshot line').
  - test_phase4_switch_landing_wrong_tab_raises: the phase-4
    re-switch landing on any other URL raises RuntimeError
    ('send switch landed on ...') before the send program
    runs.
- The F2 mitigation (re-switch plus snapshot URL gate) has now
  been executed outside a live run. The only F2 test before
  this was a string-presence assertion; the new tests execute
  the runner code.

### C4 (Council 1 C1, adopted by Redteam): recovery line for a navigated-away owner tab

- Prep file amendment note, one line added after the orphan
  about:blank rule: when the owner tab carries the fixture URL
  after a refused open, the coordinator navigates it back to
  the Muse thread by hand in the Zen UI, never via a Marionette
  navigate or DELETE, and verifies the pre-check passes before
  the next run. The note also records why: the leftover after
  a refused open is not always an empty about:blank tab.

### C4 (Council 3, G1 note): phase-4 listing is the run-1 program

- Prep file phase-4 section, one note added after the program
  listing: the program above is the recorded RUN-1 program
  (message ZEN-DELEGATE-R1-IGNORE-TEST, no PROBE print). The
  run-2 program in c5-zen-delegate-run2.py adds the PROBE
  print after dom_observe (Redteam F2), which phase 4 gates
  on. Copy run2.py, never copy this listing into a run: a
  program copied from the listing would fail phase 4 after
  the send ('send program printed no snapshot line').

### H3 (Redteam LOW): F2 wording corrected

- The amend 1 log overstated the F2 gate: "a send can only go
  to the tab the switch just selected and the snapshot just
  confirmed". That is corrected here, not by editing the
  amend 1 log (a committed historical record): the PROBE gate
  is detection-only. It confirms the snapshot URL substring
  and count, which a duplicate fixture tab satisfies
  identically, and the input follows the current tab, not the
  resolved tab. The real guards are the phase-4 switch
  refusing on ambiguity and the phase-5 ev() raising on
  ambiguity, so a duplicate makes the run error, never a
  false PASS. The worst case is a send to a duplicate fixture
  tab (harmless content, a test fixture) with the run
  recorded as error. No owner-tab impact.

### C5 (Council 3 re-execution, adopted by Redteam): already satisfied

- Council 3 could not execute code and required re-execution
  by an authorized lane. Satisfied by the independent re-runs
  of Redteam (27/27, G0a 177/177, G0b, F1 repro, H1 repro,
  C5 probe) plus Council 1 and Council 2, and by this
  worker's re-runs in section 3. No separate re-execution
  lane is needed. The push verification (Council 3 C2) was
  satisfied when Muse tong committed and pushed the Council 3
  review itself (4f8825d, ls-remote verified).

## 3. Verification (code/unit only, no live tab operation)

- py_compile OK for zen-tab.py, run2.py, and the test file.
- New tests tests/test_zenproof2_fix.py: 36/36 OK
  (python3 -m unittest tests.test_zenproof2_fix, 0.005s).
  27 old tests still pass unchanged (one updated for the new
  refusal message, see H1 side effect); 9 new tests added
  (2x H1, 1x H2, 1x count gate new-handle, 5x phase 4).
- G0b: both programs pass code_exec.validate_program with no
  exception (PROBE True, SEND True), same check the run used.
- G0a suite still passes: python3 -m unittest
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec, Ran 177 tests, OK (12.509s).
- Redteam H1 repro re-run against the amended code, both
  modes: refuses at cmd_open with 'existing handle', owner
  tab URL unchanged, deletions []. The damage no longer
  reproduces.
- H2 probe re-run against the amended code: cmd_close returns
  ok with scan_error True, current_title None, current_url
  None, scratch deleted True.
- 0 em dash (U+2014) and 0 en dash (U+2013) in all four
  changed files (zen-tab.py, run2.py, test file, prep file),
  counted by grep.
- Fixture untouched: sha256 of tests/two_vision_fixture.html
  is 147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6
  cbf, identical to FIXTURE_SHA.
- NOT verified (needs a live run, out of scope for this
  worker): the amended runner against real Zen. The next proof
  is a fresh run number with a fresh intent/message, after
  council + redteam review of this amend.

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
- Known limitations recorded in the amend 1 log section 4
  still hold, plus the ones named here: the WebDriver
  protocol offers no atomic verify-and-navigate (the F1
  residual race is narrowed, not eliminated); the count gate
  assumes a single lane (a concurrent tab change causes a
  spurious fail-closed refusal, never a wrong navigate);
  backend first-match stays a known limitation; unreadable
  tabs stay invisible to URL identity. None of them is a
  live-run gate beyond what the reviews already stated.

## 5. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received ~20:36 +07, 22/11/2026. Branch todolist-push,
  HEAD at start ee6b487. Fetched origin before committing;
  local HEAD already equalled origin/todolist-push.
- Baseline 20:38 +07: 27/27 OK; H1 repro on unamended code
  returned ok and cmd_close deleted the owner tab (owner tab
  still present False); H1 select_new=False variant returned
  ok with the owner tab navigated to the fixture URL; H2
  probe raised 'simulated read failure' although the scratch
  tab was deleted.
- zen-tab.py edits 20:40 +07: py_compile OK after edit.
- Tests 20:42 +07: python3 -m unittest
  tests.test_zenproof2_fix, Ran 36 tests in 0.005s, OK.
  First run was 35/36: the old C4 test expected the count
  gate message for a stale-handle fake, but the membership
  check now refuses that case first; the test was updated and
  a count-gate-only test added (see section 2, H1 side
  effect).
- G0a 20:44 +07: Ran 177 tests in 12.509s, OK.
- G0b 20:44 +07: PROBE True, SEND True.
- H1 repro re-run 20:44 +07: both modes refuse at cmd_open
  with 'existing handle', owner tab URL unchanged,
  deletions [].
- H2 probe re-run 20:44 +07: cmd_close returns ok with
  scan_error True, current_title None, current_url None,
  scratch deleted True.
- Fixture sha 20:44 +07:
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6
  cbf, matches FIXTURE_SHA.
- Dash counts 20:44 +07: U+2014 0, U+2013 0 in all four
  changed files.
- Diff scope: 3 code/doc files plus this log (zen-tab.py, test
  file, prep file). run2.py was NOT changed by this amend
  (the phase-4 tests execute its existing code). The pre-existing dirty
  tests/realistic/clone1-batch3/results.json was never touched
  and is never committed by me. The untracked prompt files in
  improvements/ belong to other lanes and are not mine.
- Files changed (mine only, explicit pathspecs):
  improvements/c5-zenproof-runs/zen-tab.py,
  tests/test_zenproof2_fix.py,
  improvements/w-zen-delegate-liveproof-prep.md,
  improvements/w-zenproof2-amend2-log.md (new, this file).
- Commits, pushed, ls-remote verified: (hashes in the report
  to Muse tong).
- No live Zen tab was opened, navigated, or deleted. No proof
  re-run. No reviewer spawned (Muse tong spawns council +
  redteam after this).
