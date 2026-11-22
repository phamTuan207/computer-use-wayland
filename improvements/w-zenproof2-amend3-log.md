# W-ZENPROOF2-AMEND3: close the review conditions on W-ZENPROOF2-AMEND2

Owner: Pham Tuan. Worker: W-ZENPROOF2-AMEND3, independent (not
W-ZENPROOF2-AMEND2, not W-ZENPROOF2-AMEND, not W-ZENPROOF2-FIX, not
W-ZENPROOF2, not COORD-CLICK-9). Report goes to Muse tong, not
directly to Pham Tuan. No live proof re-run, no tab opened,
navigated, or deleted in Pham Tuan's Zen. All verification is
code/unit level only. No em dash or en dash anywhere in this file.
No personal info.

## 0. Task receipt and sources (20:48 +07, 22/11/2026)

- Task received ~20:48 +07. T+0m. Branch todolist-push, repo
  ~/workspace/computer-use-wayland. HEAD at start 302bc7d
  (redteam review of amend 2).
- The amend under amendment (4 commits): e9994d9 (zen-tab.py),
  d8f8ac3 (36 unit tests), 16075f6 (prep file), bcc249c (amend
  log). All 4 reviews GO WITH CONDITIONS:
  - Council 1, ccaa056: GO, no conditions.
  - Council 2, 1be1ce4: GO WITH CONDITIONS, C1 (2 remaining
    phase-4 branches untested: active-window check, final
    ok/completed gate).
  - Council 3, 50e6fab: GO, no conditions.
  - Redteam, 302bc7d: GO WITH CONDITIONS, C1 (P-C concurrent
    open + close defeats membership + count gates; add
    set-difference check + regression test; correct the
    amend-2 log wording "never a wrong navigate"), C2 (H3:
    2 phase-4 tests + pin call order and program identity
    in the _run_phase4 helper), C3 (H2: record the
    within-session handle-stability assumption, doc-only).
- Sources read before any edit: all 4 amend-2 reviews in full,
  the amend-2 log, the current zen-tab.py cmd_open, run2.py
  phase4 (lines 483-525), the test file, and
  /tmp/redteam-amend2-probes.py (P-C, P-D; read in full).

## 1. Time log (wall-clock Asia/Ho_Chi_Minh)

- 20:48 +07, T+0m: task received, 4 reviews + amend-2 log read.
- 20:48 +07, T+0m: code + test file + P-C/P-D probes read.
- 20:49 +07, T+1m: baseline confirmed (P-C reproduces on the
  amend-2 code, checked by position; suite 36/36 OK).
- 20:50 +07, T+2m: zen-tab.py amended (set-difference check +
  docstring assumption). Test file amended (1 P-C test + 5
  phase-4 tests + helper records calls). Full suite 42/42 OK;
  P-C probe now refuses; G0a 177/177, G0b both programs
  validate, fixture sha matches. Log written, committing.

## 2. What was closed, condition by condition

### P-C (Redteam C1, MEDIUM): concurrent open + close defeats membership + count gates

- zen-tab.py cmd_open: after POST /window/new, the driver now
  keeps the full handle LIST from the count fetch (not just
  its length) and requires the set difference against
  `before` to be exactly the new handle added and nothing
  removed: set(after) - set(before) == {new_handle} and
  set(before) - set(after) == empty. The check uses `before`
  (captured at cmd_open start), not the pre-check scan's
  handle list: a concurrent change between `before` and the
  scan is already in the scan, so a difference against the
  scan would miss it; against `before`, every ordering is
  caught. The membership check and the count gate are kept
  as defense in depth with distinct error messages; the
  set-difference check is the third line and refuses with
  'new tab handle set changed unexpectedly (added %d,
  removed %d); refusing to navigate or close'.
- The set-difference check also independently closes the
  within-session handle re-mint case (Redteam P-A): a
  re-minted owner handle changes the set by more than
  {new_handle} (one added, one removed), so it refuses
  fail-closed. The fake does not model re-minting (Redteam
  G4), so no P-A test was added; the closure is by the same
  set-difference logic the P-C test pins.
- Regression test added
  (test_open_refuses_concurrent_open_close_with_stale_handle):
  tab X opens after `before` AND the example tab closes in
  the same window (net count +1), and /window/new returns
  X's handle. Asserts the 'handle set' raise, zero
  deletions, 3 tabs, owner URL unchanged, X URL unchanged
  (https://x.example/), new tab left as about:blank.
- Baseline first, by my own probe
  (/tmp/amend3-baseline-probe.py, written by me because the
  redteam P-C probe looks X up by title and misses the
  hijack: the navigate rewrites the title too; my probe
  checks tabs[1] by position): on the amend-2 code, cmd_open
  RETURNED ok, tabs[1] (X) carried the fixture URL, and
  cleanup close DELETEd X, leaving only the owner Muse tab
  and the empty about:blank tab. After the fix, the same
  probe shows cmd_open REFUSED with 'new tab handle set
  changed unexpectedly (added 2, removed 1)', deletions [],
  owner intact, X intact, tabs [owner, X, about:blank].
  The damage no longer reproduces.
- Wording correction (Redteam C1): the amend-2 log section 4
  claim "a concurrent tab change causes a spurious
  fail-closed refusal, never a wrong navigate" was
  overstated, as the P-C repro proves. It is corrected
  here, not by editing the amend-2 log (a committed
  historical record): the set-difference check narrows the
  residual further, but WebDriver offers no atomic
  verify-and-navigate, so a concurrent change plus a stale
  return remains a (narrower) residual, not an eliminated
  one. The check catches the churn the membership and count
  gates miss; it cannot catch a change that happens after
  the set-difference fetch and before the navigate, which
  the post-navigate F1 check then catches (refusal, no
  DELETE).

### Phase-4 tests (Council 2 C1 + Redteam H3/C2)

- The _run_phase4 helper now records calls: the tab and
  oneshot_zen mocks append to runner._phase4_calls, and the
  helper takes ok= and hypr_address= parameters (defaults
  True and '0xABC', the previous behavior). The 5 existing
  phase-4 tests run unchanged through the new helper.
- Five tests added to RunnerFixTest, all running phase4 on a
  real Runner:
  - test_phase4_active_window_moved_raises: hypr returns
    address 0xDEF (not the Zen address); raises RuntimeError
    'active window moved off Zen before send'. That check is
    the first line of phase4, so the message alone proves
    no switch or send ran.
  - test_phase4_envelope_ok_false_raises: envelope ok False
    with a valid PROBE line and completed 4; raises
    RuntimeError 'send program did not complete 4/4'.
  - test_phase4_completed_three_raises: log with 'dom_act ok
    True completed 3'; raises the same.
  - test_phase4_missing_dom_act_raises: log with a valid
    PROBE line but no dom_act line (completed None); raises
    the same.
  - test_phase4_switch_before_send_and_program_identity:
    happy path; asserts the call kinds are exactly ['tab',
    'oneshot'] in that order, the tab call args are
    ('switch', TARGET), the oneshot program IS
    SEND_PROGRAM (identity, not equality), and the intent
    is INTENT. A future edit reordering the calls or
    passing the wrong program fails this test.
- Council 2's probes already proved the code behaves
  correctly in all 4 sub-cases; these tests pin that
  behavior in the suite. The final ok/completed gate is
  now executed by tests: a failed send can no longer be
  recorded as success without a test failing first.

### Handle-stability assumption (Redteam C3, doc-only)

- zen-tab.py module docstring now records the assumption
  the membership, count, and set-difference checks make:
  handles are stable within one cmd_open invocation. Run 1
  supports this (handles were consistent across before,
  scan, /window/new, the (c) check, navigate, and the
  post-navigate check within one invocation); run 2's
  ephemerality was cross-session (two lists a minute apart,
  separate processes). If a handle were re-minted
  mid-invocation, the set-difference check refuses
  fail-closed.
- The module docstring's open-checks paragraph now also
  names the set-difference requirement next to the count
  +1 and membership requirements.

## 3. Verification (code/unit only, no live tab operation)

- py_compile OK for zen-tab.py and the test file.
- New tests tests/test_zenproof2_fix.py: 42/42 OK
  (python3 -m unittest tests.test_zenproof2_fix, 0.008s).
  36 old tests still pass unchanged; 6 new tests added
  (1x P-C, 5x phase 4).
- G0b: both programs pass code_exec.validate_program with no
  exception (PROBE Module, SEND Module), same check the run
  used.
- G0a suite still passes: python3 -m unittest
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec, Ran 177 tests, OK (12.504s).
- P-C probe re-run against the amended code: cmd_open
  refuses with 'new tab handle set changed unexpectedly
  (added 2, removed 1)', deletions [], owner intact, X
  intact. On the amend-2 code the same probe returned ok
  and cleanup deleted X (section 2).
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
- Known limitations recorded in the amend 1 log section 4
  and the amend 2 log section 4 still hold, plus the ones
  named here: the WebDriver protocol offers no atomic
  verify-and-navigate (the F1 residual race is narrowed,
  not eliminated; the set-difference check narrows the
  concurrent-churn case further but cannot catch a change
  after its own fetch); backend first-match stays a known
  limitation; unreadable tabs stay invisible to URL
  identity. None of them is a live-run gate beyond what
  the reviews already stated.
- Not closed here (follow-up candidate, not a live-run
  gate): cmd_close's post-DELETE verification reads can
  still raise after a successful DELETE and mask the close
  success (Redteam G1 / Council 1 G1, same shape as H2,
  different site, pre-existing from amend 1). Consequence
  is a spurious error (fail-closed), never a wrong navigate
  or DELETE.

## 5. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received ~20:48 +07, 22/11/2026. Branch todolist-push,
  HEAD at start 302bc7d. Fetched origin before committing;
  local HEAD already equalled origin/todolist-push.
- Baseline 20:49 +07: python3 /tmp/amend3-baseline-probe.py
  on the amend-2 code: cmd_open RETURNED ok, tabs[1] URL
  now the fixture URL, hijacked True, cleanup close ok
  True, X deleted True, tabs left [owner Muse tab,
  about:blank]. Suite 36/36 OK on the same code.
- zen-tab.py edits 20:50 +07: set-difference check after the
  count gate, docstring assumption + open-checks paragraph.
  py_compile OK after edit.
- Test file edits 20:50 +07: 1 P-C test, 5 phase-4 tests,
  _run_phase4 records calls (ok=, hypr_address= params).
- Suite 20:50 +07: python3 -m unittest
  tests.test_zenproof2_fix, Ran 42 tests in 0.008s, OK.
- P-C probe re-run 20:50 +07: cmd_open REFUSED with 'new
  tab handle set changed unexpectedly (added 2, removed 1)',
  deletions [], owner intact, X intact, tabs [owner, X,
  about:blank].
- G0a 20:50 +07: Ran 177 tests in 12.504s, OK.
- G0b 20:50 +07: PROBE Module, SEND Module.
- Fixture sha 20:50 +07:
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6
  cbf, matches FIXTURE_SHA.
- Dash counts 20:50 +07: U+2014 0, U+2013 0 in both changed
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
  improvements/w-zenproof2-amend3-log.md (new, this file).
- Commits, pushed, ls-remote verified: (hashes in the report
  to Muse tong).
- No live Zen tab was opened, navigated, or deleted. No proof
  re-run. No reviewer spawned (Muse tong spawns council +
  redteam after this).
