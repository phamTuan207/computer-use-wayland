# Council 2 review: W-ZENPROOF2-AMEND3 (phase-4 tests + P-C set-difference)

Reviewer: Council 2, independent (not W-ZENPROOF2-AMEND3, not
W-ZENPROOF2-AMEND2, not W-ZENPROOF2-FIX, not W-ZENPROOF2, not
COORD-CLICK-9). Report goes to Muse tong, not directly to Pham
Tuan. No amend modified, no live run, no tab opened, navigated,
or deleted in Pham Tuan's Zen. All verification is code/unit
level only, plus my own re-runs, a baseline worktree, and
mutation probes. No em dash or en dash anywhere in this file.
No personal info.

## 0. Task and sources (20:52 +07, 22/11/2026)

- Task received ~20:52 +07. Branch todolist-push, repo
  ~/workspace/computer-use-wayland, HEAD 24050c1 at review
  start.
- Amend under review, 3 commits: 09802c3 (zen-tab.py:
  set-difference check + handle-stability docstring), 58df67d
  (test file: P-C regression test + 5 phase-4 tests + helper
  records calls), 24050c1 (amend log).
- My condition from the amend-2 review (C1): add behavior
  tests for the 2 remaining phase-4 branches (active-window
  check, final ok/completed gate). Redteam H3/C2: pin call
  order and program identity in the _run_phase4 helper.
- Sources read before judging: improvements/
  w-zenproof2-amend3-log.md in full; the full diff of 09802c3
  and 58df67d; run2.py phase4 lines 483-525; the test file
  header, FakeSession, _owner_tabs, the _run_phase4 helper,
  all 10 phase-4 tests; zen-tab.py cmd_open lines 188-275.

## 1. Time log (wall-clock Asia/Ho_Chi_Minh)

- 20:52 +07, T+0m: task received, log + diff stat read.
- 20:53 +07, T+1m: full diff of both code commits read;
  phase4 code and cmd_open read.
- 20:53 +07, T+1m: suite 42/42 re-run by me; G0a 177/177
  re-run; G0b validate re-run; fixture sha + dash counts
  checked.
- 20:54 +07, T+2m: baseline worktree at 302bc7d (amend-2
  code) + new test file: exactly 1 failure (P-C test, not
  raised). Mutation probes in /tmp (order swap, PROBE_PROGRAM
  swap, intent swap): identity test fails on all 3, with the
  pin assertion as the failure.
- 20:55 +07, T+3m: phase-4 branch enumeration against the
  real code; message-uniqueness check; review written,
  committing.

## 2. What I verified, with evidence

### 2.1 Diff scope is exactly the amend, nothing else

- git show --stat: 09802c3 touches only zen-tab.py (1 file);
  58df67d touches only tests/test_zenproof2_fix.py (1 file);
  24050c1 is the log (1 file). 3 files total, +432/-13 across
  the 3 commits (zen-tab.py +44, test file +141, log +260).
  run2.py was NOT changed: the phase-4 tests execute its
  existing code, which is the point (behavior that already
  existed, now pinned).
- 0 em dash (U+2014) and 0 en dash (U+2013) in all 3 files,
  counted by me. Fixture untouched: sha256
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6
  cbf matches FIXTURE_SHA in run2.py line 52 and the bench
  manifest.

### 2.2 Suite, G0a, G0b, re-run by me

- python3 -m unittest tests.test_zenproof2_fix: Ran 42 tests
  in 0.008s, OK. Exit 0.
- G0a: python3 -m unittest tests.test_zen_pointer
  tests.test_p2_element_ref tests.test_code_exec: Ran 177
  tests in 12.889s, OK.
- G0b: code_exec.validate_program passes for PROBE_PROGRAM
  and SEND_PROGRAM (both return Module, no exception).
- The 5 old phase-4 tests run unchanged through the new
  helper (defaults ok=True, hypr_address='0xABC' reproduce
  the previous behavior: envelope ok True, hypr returns
  '0xABC'; the mocks return the same shapes as before).

### 2.3 My C1 from the amend-2 review: CLOSED

- The 2 untested branches now have tests, and the final gate
  has all 3 sub-cases:
  - Active-window check:
    test_phase4_active_window_moved_raises
    (hypr_address='0xDEF' vs zen_address '0xabc') raises
    RuntimeError 'active window moved off Zen before send'.
  - Final gate, ok False:
    test_phase4_envelope_ok_false_raises (valid PROBE line
    + completed 4, envelope ok False) raises 'did not
    complete 4/4'.
  - Final gate, completed 3:
    test_phase4_completed_three_raises raises the same.
  - Final gate, completed None:
    test_phase4_missing_dom_act_raises (PROBE line only, no
    dom_act line) raises the same.
- The message 'active window moved off Zen before send' is
  unique inside phase4 (the only other occurrence is phase3's
  '...before probe' at line 447, which a phase4() call cannot
  reach), and the check is the first statement of phase4
  after the hypr read, so the raise proves no switch or send
  ran. The test asserts the message, which is sufficient
  here.

### 2.4 The 5 new tests really run real phase-4 code

- _run_phase4 builds a real Runner and calls
  runner.phase4(). Only the I/O boundaries are mocked: hypr
  (read), tab (switch), oneshot_zen (program execution).
  Every branch of phase4 (lines 483-525) runs for real: the
  active-window comparison, the switch URL check, the PROBE
  parse, the completed regex scan, the final gate.
- The mocks are faithful: _tab returns {'ok': True, 'url':
  switch_url} (same shape as before); _oneshot returns (12.3,
  envelope) (same as before); the real call sites pass
  timeout=60 (tab) and timeout=90 (oneshot) as before.

### 2.5 The order/identity pin bites: 3 mutation probes, all fail on the pin

- Order mutation (moved the oneshot_zen call + program
  recording before the tab switch in a /tmp copy of
  run2.py): the identity test fails with `Lists differ:
  ['oneshot', 'tab'] != ['tab', 'oneshot']` on the kinds
  assertion.
- Program mutation (passed PROBE_PROGRAM instead of
  SEND_PROGRAM): the identity test fails on
  `assertIs(oneshot_call[1], run2.SEND_PROGRAM)` (identity,
  not equality: PROBE_PROGRAM is a different object).
- Intent mutation (passed INTENT + '-probe'): the identity
  test fails with `'c5-zen-delegate-r2-probe' !=
  'c5-zen-delegate-r2'`.
- The kinds assertion is exact list equality, so any extra,
  missing, or reordered call fails it. The tab-call assertion
  pins ('switch', TARGET) as the call args.
- First run of the probes failed on import: run2.py imports
  s2_flip_live, which needs scripts/ on PYTHONPATH. Reran
  with PYTHONPATH set to the repo scripts/ dir; the import
  error was my harness, not the code.

### 2.6 The P-C test is a genuine regression test

- Baseline worktree at 302bc7d (amend-2 code) with the new
  test file copied in: Ran 42 tests, FAILED (failures=1),
  and the single failure is
  test_open_refuses_concurrent_open_close_with_stale_handle
  with `_FakeZenDomError not raised`. All 5 new phase-4
  tests pass on amend-2 code (run2.py unchanged, as
  expected).
- On amend-3 code the P-C test passes: the set-difference
  check raises 'new tab handle set changed unexpectedly
  (added 2, removed 1)' before any select or navigate, with
  zero deletions and the X tab intact.
- I read cmd_open (lines 188-275) and confirmed the check
  order in code: `before` is captured at cmd_open start
  (before the pre-check scan, so a change between `before`
  and the scan is caught too); the membership check runs
  first with its own message; the count gate runs second on
  the full handle list (not just its length); the
  set-difference check runs third, requiring added ==
  {new_handle} and removed empty; then the (c) check. The
  log's description of the check order matches the code.

### 2.7 Phase-4 branch enumeration: nothing left

- Every raise site in phase4 (lines 483-525) is executed by
  a suite test: active-window (new), switch-landed
  (existing), no-snapshot-line (existing), parse_probe_line
  ValueError for wrong URL and wrong count (existing),
  final gate 4/4 for ok False / completed 3 / completed None
  (new). The happy path records send_url, send_count,
  completed 4 (existing).
- The helper's new ok= and hypr_address= parameters default
  to the previous behavior, and the call recording does not
  change what the mocks return.

## 3. Gaps and minor observations (not blockers)

- G1: the dom_act regex's `ok` group is ignored (only
  `completed` is read). A log line 'dom_act ok False
  completed 4' with envelope ok True would pass the gate.
  Unreachable in practice: SEND_PROGRAM ends with
  `assert_state(res.get("ok") is True, "dom_act failed")`,
  so a failed dom_act fails the program and the envelope ok
  is False. Defense in depth only; not a condition.
- G2: three None-variants hit tested raise branches but
  have no distinct test: envelope log None/missing (same
  branch as the missing-PROBE test), switch url None (same
  branch as the switch-landed test), hypr dict without
  'address' (same branch as the active-window test). Same
  branch, no new behavior; no separate test needed.
- G3: the active-window test proves no switch/send ran only
  through the message (the helper does not return the runner
  on raise, so the test cannot assert calls == []). The
  message is unique inside phase4 and the check is first, so
  the proof is sound as written. A future helper change could
  return the calls on raise for a direct assertion; not
  required.
- G4: the identity test pins the tab call args ('switch',
  TARGET) but not the timeout=60 kwarg. Dropping the timeout
  would not fail the test. Trivial; the timeout is not
  behavior-critical here.
- G5: the log's wording is honest about the residual (no
  atomic verify-and-navigate; the set-difference check
  narrows the concurrent-churn case but cannot catch a
  change after its own fetch, which the post-navigate F1
  check then catches as a refusal). The amend-2 log
  overstatement is corrected in the amend-3 log, not by
  editing the committed amend-2 log. Correct handling of a
  historical record.

## 4. Verdict: GO

- My C1 is closed: the active-window check and the final
  ok/completed gate (all 3 sub-cases) are executed by
  behavioral tests on a real Runner, and the helper pins
  call order (switch before send) and program identity
  (SEND_PROGRAM, identity not equality) plus intent. The
  pins bite: 3/3 mutation probes fail on the pin assertions.
- The P-C regression test is genuine: it fails on amend-2
  code and passes on amend-3 code, and the set-difference
  check is correctly ordered in cmd_open with `before`
  captured at invocation start.
- No conditions. The G notes above are observations, not
  gates: same-branch variants, an unreachable-in-practice
  regex case, and two possible-but-unneeded test
  strengthenings.

## 5. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received ~20:52 +07, 22/11/2026. HEAD at review start
  24050c1.
- Suite re-run by me 20:53 +07: python3 -m unittest
  tests.test_zenproof2_fix, Ran 42 tests in 0.008s, OK.
- G0a re-run by me 20:53 +07: Ran 177 tests in 12.889s, OK.
- G0b re-run by me 20:53 +07: validate_program returns
  Module for PROBE and SEND.
- Fixture sha 20:53 +07:
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6
  cbf, matches FIXTURE_SHA (run2.py line 52).
- Dash counts 20:53 +07: U+2014 0, U+2013 0 in zen-tab.py,
  test file, amend-3 log.
- Diff scope 20:52 +07: 3 files, +432/-13 (zen-tab.py +44,
  test file +141, log +260). run2.py unchanged.
- Baseline worktree 20:54 +07: git worktree at 302bc7d +
  new test file, Ran 42, FAILED (failures=1), single failure
  the P-C test (_FakeZenDomError not raised).
- Mutation probes 20:54 +07 (copies in /tmp/mut-order,
  /tmp/mut-prog, /tmp/mut-intent, PYTHONPATH set to repo
  scripts/): order swap fails `['oneshot', 'tab'] != ['tab',
  'oneshot']`; PROBE_PROGRAM swap fails assertIs;
  intent swap fails `'c5-zen-delegate-r2-probe' !=
  'c5-zen-delegate-r2'`.
- Branch enumeration 20:55 +07: all 5 raise sites in phase4
  lines 483-525 covered; message 'active window moved off
  Zen before send' unique in phase4 (other occurrence is
  phase3 line 447).
- Files changed by me (review only):
  improvements/w-zenproof2-amend3-council-2-review.md (new,
  this file). No amend file modified. No live run. No
  reviewer spawned.
