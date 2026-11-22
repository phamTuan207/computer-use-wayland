# Council 1 review: W-ZENPROOF2-AMEND (F1 TOCTOU close, C4 count gate, prep file)

Reviewer: Council 1, independent (not W-ZENPROOF2-AMEND, not
W-ZENPROOF2-FIX, not W-ZENPROOF2, not COORD-CLICK-9). Report goes
to Muse tong, not directly to the owner. No amend file modified,
no live run, no tab opened, navigated, or deleted in the owner's
Zen. All verification is code/unit level only, plus my own
re-runs of the unit and G0a suites and my own probes. No em dash
or en dash anywhere in this file. No personal info.

## 0. Task and sources (20:31 +07, 22/11/2026)

- Task received ~20:31 +07. Branch todolist-push, repo
  ~/workspace/computer-use-wayland, HEAD b956176 at review
  start. The 5 amend files are committed, not dirty (git status
  on the 5 paths is empty; the pre-existing dirty
  tests/realistic/clone1-batch3/results.json belongs to another
  worker and is not in these commits).
- Amend under review, 5 commits:
  - b27818d zen-tab.py: F1 post-navigate handle check, C4 count
    gate, F4 docstring, C5 restore flags (+91/-15).
  - fa5f737 run2.py: F2 phase 4 re-switch plus send snapshot URL
    gate (+27).
  - ee2a85a tests/test_zenproof2_fix.py: 11 new tests, fake
    extensions (+299/-6).
  - 5b032ae prep file: title premise corrected to URL-substring
    target (+95/-51).
  - b956176 improvements/w-zenproof2-amend-log.md: amend log
    (+381).
- Sources read before judging:
  - improvements/w-zenproof2-amend-log.md (the amend log, full).
  - Full diff of b27818d, fa5f737, ee2a85a, 5b032ae (read line
    by line, not skimmed).
  - The current zen-tab.py cmd_open (lines 175-345), cmd_close,
    _restore_original, _current, _handles, _scan, _resolve_url.
  - run2.py cleanup (lines 566-600), phase 2 open (lines
    424-435), phase 4 (lines 485-525), parse_probe_line.
  - The 4 reviews of the fix (Council 1 787ab18, Council 2
    5b0af0d, Council 3 7cef509, Redteam 2c76690) for the
    conditions this amend claims to close.
  - /tmp/redteam-repro-f1.py, /tmp/zenproof2_council2_probe.py
    (repro templates, re-run, not trusted blindly).
  - My own probe /tmp/c1-amend-probe-f1-variant.py (flip after
    the post-navigate check, before the URL check).

## 1. Time log (wall-clock Asia/Ho_Chi_Minh)

- 20:31 +07, T+0m: task received, amend log + diff stat read.
- 20:32 +07, T+1m: full zen-tab.py diff read; cmd_open read in
  full; handler scope checked (try starts after new_handle is
  assigned).
- 20:33 +07, T+2m: run2.py F2 diff read; parse_probe_line and
  cleanup/opened flag read; prep file diff read.
- 20:34 +07, T+3m: test file diff read in full (11 new tests).
- 20:35 +07, T+4m: 27 unit tests re-run by me, 27/27 OK.
- 20:36 +07, T+5m: G0a 177/177 re-run by me, OK; G0b both
  programs validate; fixture sha and dash counts checked.
- 20:37 +07, T+6m: redteam F1 repro re-run by me (dies at
  cmd_open line 241); Council 2 Probe B re-run by me; my own
  F1-variant probe written and run (fail-closed, 0 deletions).
- 20:38 +07, T+7m: prep file greps (Clone zen thread, title
  gates, R3); review written, committing.

## 2. What I verified, with evidence

### 2.1 Diff scope is exactly the amend, nothing else

- Each amend commit touches exactly 1 file: b27818d zen-tab.py
  only, fa5f737 run2.py only, ee2a85a test file only, 5b032ae
  prep file only, b956176 amend log only. No shared library
  touched, so no regression outside the Zen proof flow.
- 0 em dash (U+2014) and 0 en dash (U+2013) in all 5 files,
  counted by me with grep -c. Fixture untouched (sha256
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6cbf,
  matches FIXTURE_SHA).

### 2.2 The 27 unit tests pass on my own run

- Command: python3 -m unittest tests.test_zenproof2_fix -v.
  Output: Ran 27 tests in 0.003s, OK. Exit 0. I ran it myself,
  not trusting the log's 27/27.
- The 11 new tests are the ones the amend claims: F1
  regression, 2x no-delete branch, C4 count gate, 2x F3a error
  entry, 2x F3b restore failure, 2x C5 restore flags, 1x F2
  send PROBE print. All 16 old tests still pass unchanged.

### 2.3 F1: the TOCTOU is closed, and I proved it three ways

- Code read: cmd_open re-verifies `_current(z) ==
  new_handle` immediately after POST /url, raising 'current
  tab changed during navigate' before any further check or
  DELETE. The handler deletes only when the current handle ==
  new_handle AND the current URL contains the fixture
  substring. `_current` returns the full handle (GET
  /session/{id}/window), so the comparison is against the same
  handle the open returned, not a truncated prefix.
- Scope check: the try block starts AFTER new_handle is
  assigned, so the handler's `new_handle` reference can never
  raise NameError. The count gate and the (c) check raise
  BEFORE the try block, so no handler runs for them, which is
  correct: nothing was navigated yet and nothing should be
  deleted.
- Repro 1 (redteam F1, re-run by me): the fake flips current
  back to the owner tab inside POST /url. The repro now dies
  at cmd_open line 241 with 'current tab changed during
  navigate (current 4f3c3f60 != new a4fc4ab0); refusing' and
  never reaches cmd_close. The damage no longer reproduces.
  On the unamended code this same repro deleted the owner tab
  (redteam review, confirmed by the amend log baseline).
- Repro 2 (my own probe, /tmp/c1-amend-probe-f1-variant.py):
  the flip happens AFTER the post-navigate check passes but
  BEFORE the URL check reads. The URL check then reads the
  owner tab's URL and raises 'does not contain'; the handler
  deletes nothing; 3 tabs, 0 deletions, owner tab current.
  This covers the flip window the suite's F1 test does not.
- The suite F1 test itself
  (test_open_focus_reverts_during_navigate_refuses_and_keeps_
  owner_tab) asserts the documented residual honestly: the
  owner tab survives but its URL was rewritten to the fixture
  page (navigate-away, not delete). The handler's handle check
  is what saves it: the owner tab now carries the fixture URL,
  so a URL-only check would delete it.

### 2.4 C4: the count gate really blocks a stale handle

- Code read: `count_after_new = len(_handles(z))` right after
  POST /window/new; refuses unless it equals len(before) + 1.
  The gate runs before the (c) check, so a stale returned
  handle cannot pass the (c) check on the wrong tab.
- Test re-run by me (test_open_count_gate_refuses_stale_handle):
  /window/new returns an existing handle without creating a
  tab; open raises 'did not increase the tab count', 0
  deletions, 2 tabs, owner tab still current.
- Assumption is recorded in the log and the code: no tab opens
  or closes between the `before` count and the /window/new
  call (single lane, owner away). A concurrent tab change
  causes a spurious fail-closed refusal, never a wrong
  navigate. That is the correct direction of failure.

### 2.5 C1 (Council 2): the no-delete branch is now tested

- Two tests added and passing on my run:
  test_open_handler_no_delete_when_navigate_fails (Probe B
  template: navigate POST raises, current is the new
  about:blank tab) and
  test_open_handler_no_delete_when_navigate_lands_wrong_url
  (navigate lands on https://example.com/wrong, URL check
  raises). Both assert 0 deletions, 3 tabs, owner tab intact.
- Council 2 Probe B re-run by me: still confirms the branch
  works, and it is now covered by a suite test (the probe's
  own closing line predates the amend; the branch is no longer
  untested).

### 2.6 F2: phase 4 re-switch plus snapshot URL gate

- Code read: SEND_PROGRAM prints the PROBE line in the same
  shape as PROBE_PROGRAM; phase 4 calls tab('switch', TARGET)
  immediately before the send and verifies the switched URL
  contains TARGET; it then parses the send PROBE line with
  parse_probe_line and records send_url / send_count, raising
  when the line is missing or the gate fails.
- The gate runs after the send, so it is detection, not
  prevention; the prevention is the re-switch. That is the
  design, and the log is honest about it (section 2, F2).
  A wrong-tab send would be detected and the run would fail
  rather than false-PASS.
- Backend first-match is recorded as a known limitation, not
  changed. Correct scoping: the runner-side gate is the
  mitigation, the backend change stays a future option.

### 2.7 F3, F4, C5: fake fidelity and restore flags

- F3: FakeSession models error_entry_urls (entries {handle,
  error} with no URL, matching the real list_tabs shape) and
  restore_fails (restore leaves the last-scanned tab current
  without raising). Four tests pin the behavior as known
  limitations (pre-check blind to an unreadable fixture tab,
  close reports already_closed while the tab exists, cmd_list
  returns the wrong current, (c) check mitigates the silent
  restore failure in open). The fake's getBoundingClientRect
  is now tab-aware (fixture rect only when the current tab URL
  contains the fixture substring). All four tests pass on my
  run.
- F4: _scan and _resolve_url docstrings no longer claim one
  atomic moment; they state two fetches at different moments
  and fail-closed on mid-scan change. Read in the diff.
- C5: _restore_original separates scan_error from
  original_ambiguous, and _full_handle/_switch failures inside
  it record restore_failed and return instead of raising.
  Both tests pass on my run. The close success is no longer
  masked by a restore exception.

### 2.8 Prep file: the stale title premise is fully corrected

- Grep after the edit: 'Clone zen thread' occurs only in the
  amendment note, H1 content confirmations, and the correct
  line 674. No title gate remains: grep for 'title verified',
  'verify the current title', and "title 'Clone" returns
  nothing. The remaining 'title' mentions are evidence-only
  recording (P1.2, snapshot title) or hyprctl window titles,
  never gates.
- The corrected steps match the fixed driver: P2.2 (count +1,
  made-current, re-verify after navigate, URL + H1, close
  only by URL and handle), P3.1 (URL verified), P3.3
  (snapshot URL, count 1, title evidence only), P6.1 (tab
  count back, URL verified), section 6 line 671 (the query
  makes the fixture JS set the H1; the document title stays
  static), R3 (restore and verify the current URL), checklist
  P2.2/P3.1/P3.3/P6.1. The two further stale statements the
  Council 3 grep missed ('(title verified)' in the P3.1 and
  P6.1 checklists) are fixed to '(URL verified)'.
- The amendment note at the top states the incident, the new
  target, the driver guarantees, the run-order rules (fresh
  run number, fixed run2.py only, run 1 forbidden), and the
  orphan about:blank rule (close by hand in the Zen UI, never
  via Marionette, no open retry in a loop).

### 2.9 The F1 residual claim holds in the runner code

- The amend log's second residual: after a refused open the
  owner tab may carry the fixture URL, and what prevents a
  later URL-based close from targeting it is the runner's
  `opened` flag. Verified in run2.py: cleanup returns
  {'skipped': True} when `self.opened` is False (line 575),
  and `self.opened` is set True only after the phase 2 open
  returns with the fixture URL (line 431). A failed open never
  calls close. The pre-check also refuses any later open while
  a tab carries the fixture URL, so the run fails closed
  instead of proceeding.

### 2.10 G0b and G0a, re-run by me

- G0b: code_exec.validate_program passes for PROBE_PROGRAM
  and SEND_PROGRAM (both returned AST modules, no exception).
- G0a: python3 -m unittest tests.test_zen_pointer
  tests.test_p2_element_ref tests.test_code_exec, Ran 177
  tests in 12.800s, OK. Exit 0. No regression.

## 3. Gaps and minor observations (not blockers)

- G1 (same structural class as F1, in cmd_close, not a
  condition): cmd_close's DELETE has the same
  verify-then-delete shape: _switch verifies the current
  handle is the scratch tab, then DELETE closes the current
  window in a separate HTTP call. A focus change in between
  would delete the wrong tab. No observed mechanism for it
  (the observed failure was Marionette failing to select, not
  spontaneously switching), no realistic actor in this
  deployment (owner away, one lane, no other Marionette
  session), and the post-DELETE scan detects a wrong delete
  (scratch still listed raises 'scratch tab still listed
  after close'). Detection, not prevention, same assessment
  as the redteam's F1 actor analysis. A re-verify immediately
  before DELETE would close it the same way F1 was closed;
  leave it for a later hardening pass.
- G2 (minor, in the function C5 just fixed): in
  _restore_original's scan_error branch, _title(z) and _url(z)
  are called unguarded. If the scan failed because the session
  is dead, those reads raise too and the exception masks the
  close success, the same masking class C5 observation 2
  fixed for _full_handle/_switch. The runner's cleanup catches
  the exception and records it, so nothing is lost, only the
  scan_error flag. The suite test uses a fake where _title and
  _url still work after the scan failure, so this path is
  untested. Worth guarding in a later pass, not a live gate.
- G3 (design, not a defect): the F2 phase-4 PROBE gate runs
  after the send. If the send went to a wrong fixture tab,
  the message was already sent there; the gate fails the run
  instead of false-PASSing. The re-switch is the prevention.
  Understood and accepted.

## 4. Verdict: GO WITH CONDITIONS

The amend closes every condition it was given. F1 is proven
closed by three independent runs (redteam repro, my own
variant probe, the suite regression test). C4 blocks a stale
handle. The no-delete branch is now tested. F2, F3, F4, C5
are implemented as specified and pass on my own runs. The
prep file carries no title gate. G0a/G0b pass on my own runs.
The F1 residual is honestly recorded and its load-bearing
claim (runner never closes after a failed open) is verified
in the runner code.

Conditions, all to be satisfied before the next live proof
(not before landing this amend):

- C1 (doc-only, one line). The navigated-away owner tab has
  no written recovery. After a refused open, the owner tab
  may carry the fixture URL; the next run's pre-check refuses,
  but the prep file amendment note does not say what the
  coordinator does then. Add one line to the amendment note:
  when the owner tab carries the fixture URL after a refused
  open, the coordinator navigates it back to the Muse thread
  by hand in the Zen UI, never via a Marionette navigate or
  DELETE, and verifies the pre-check passes before the next
  run. Without the written step, the coordinator faces an
  unwritten recovery, and this campaign's history is that
  unwritten recoveries get improvised dangerously.

The Muse chat tab closed by run 2 attempt 2 is NOT reopened
by this amend. Recovery stays the coordinator's decision, as
the amend log states.

## 5. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received ~20:31 +07, 22/11/2026. HEAD at review start
  b956176.
- 27 unit tests, re-run by me 20:35 +07: python3 -m unittest
  tests.test_zenproof2_fix -v, Ran 27 tests in 0.003s, OK,
  exit 0.
- G0a, re-run by me 20:36 +07: python3 -m unittest
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec, Ran 177 tests in 12.800s, OK.
- G0b, re-run by me 20:36 +07: code_exec.validate_program
  passes for PROBE_PROGRAM and SEND_PROGRAM.
- Fixture sha 20:36 +07: 147494cda4c6ae24a51ced03ccdfb3fc5a79a1
  bbab56dcdfc5afb4f72fba6cbf, matches FIXTURE_SHA.
- Dash counts 20:36 +07: U+2014 0, U+2013 0 in all 5 files.
- F1 repro, re-run by me 20:37 +07: python3
  /tmp/redteam-repro-f1.py, dies at cmd_open zen-tab.py:241
  with 'current tab changed during navigate (current 4f3c3f60
  != new a4fc4ab0); refusing', never reaches cmd_close.
- Council 2 Probe B, re-run by me 20:37 +07: raised
  'simulated navigate failure', tabs=3, deleted=[], current
  about:blank; branch confirmed, now suite-covered.
- My F1-variant probe, run by me 20:37 +07:
  /tmp/c1-amend-probe-f1-variant.py, flip after the
  post-navigate check: raised 'navigated tab URL ... does not
  contain two_vision_fixture.html?clone=zen', tabs=3,
  deleted=[], current owner URL. Fail-closed confirmed.
- Prep file greps 20:38 +07: 'Clone zen thread' only in the
  amendment note, H1 content confirmations, line 674; no
  'title verified' or 'verify the current title' remains.
- Runner opened flag 20:33 +07: run2.py cleanup line 575
  returns {'skipped': True} when not opened; opened set True
  at line 431 only after a successful open.
- Diff scope 20:32 +07: each amend commit touches exactly 1
  file (b27818d zen-tab.py, fa5f737 run2.py, ee2a85a test
  file, 5b032ae prep file, b956176 amend log).
- Files changed by me (review only): improvements/
  w-zenproof2-amend-council-1-review.md (new, this file). No
  amend file modified. No live run. No reviewer spawned.
