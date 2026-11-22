# Council 2 review: W-ZENPROOF2-AMEND (close the fix-review conditions)

Reviewer: Council 2, independent (not W-ZENPROOF2-AMEND, not
W-ZENPROOF2-FIX, not W-ZENPROOF2, not COORD-CLICK-9). Report goes
to Muse tong, not directly to Pham Tuan. No amend modified, no
live run, no tab opened, navigated, or deleted in Pham Tuan's
Zen. All verification is code/unit level only, plus my own
re-runs of the unit and G0a suites and my own probes in /tmp.
No em dash or en dash anywhere in this file. No personal info.

## 0. Task and sources (20:31 +07, 22/11/2026)

- Task received ~20:31 +07. Branch todolist-push, repo
  ~/workspace/computer-use-wayland, HEAD b956176 at review
  start, equal to origin/todolist-push after fetch.
- Amend under review, 5 commits:
  - b27818d zen-tab.py: F1 post-navigate handle check, C4
    count gate, F4 docstring, C5 restore flags.
  - fa5f737 run2.py: F2 phase 4 re-switch plus send snapshot
    URL gate.
  - ee2a85a tests/test_zenproof2_fix.py: 27 unit tests.
  - 5b032ae prep file: title premise corrected to
    URL-substring target.
  - b956176 improvements/w-zenproof2-amend-log.md: amend log.
- My brief: verify independently, focus on test
  completeness. My own condition 1 from the fix review
  (5b0af0d) was the no-delete branch test; I check it first.
- Sources read before judging:
  - improvements/w-zenproof2-amend-log.md (the amend log,
    381 lines, read in full).
  - Full diff of b27818d and fa5f737 (read line by line),
    the test file (read in full), the current zen-tab.py
    cmd_open (lines 160-360, read in full), run2.py phase4
    (lines 483-530, read in full).
  - The 4 fix reviews (787ab18, 5b0af0d, 7cef509, 2c76690)
    for what each condition demanded.
  - improvements/w-zen-delegate-liveproof-prep.md amendment
    note plus grep for 'Clone zen thread' and 'title
    verified' (5 remaining occurrences, all checked).

## 1. Time log (wall-clock Asia/Ho_Chi_Minh)

- 20:31 +07, T+0m: task received, amend log read.
- 20:32 +07, T+1m: full diff of b27818d and fa5f737 read;
  test file read in full; 27 unit tests re-run by me,
  27/27 OK.
- 20:33 +07, T+2m: G0a 177/177 re-run by me, G0b both
  programs validate; baseline worktree at 2c76690 created,
  16/16 OK there; F1 repro run against amended code (dies
  at cmd_open) and against unamended code (owner tab
  deleted); worktree removed.
- 20:34 +07, T+3m: phase-4 probe written and run by me
  (/tmp/phase4-probe.py): real Runner with mocked
  hypr/tab/oneshot_zen, happy path plus wrong-URL plus
  missing-PROBE; prep file grep checked; fixture sha
  checked; dash counts checked.
- 20:35 +07, T+4m: review written, committing.

## 2. My condition 1 from the fix review: CLOSED

The fix review (5b0af0d) demanded one test for the handler
no-delete branch: raise in the try block while the current
tab is NOT the fixture tab, proving deleted == [], owner
tab intact, 3 tabs. The amend added TWO tests, and both
genuinely cover the branch through distinct triggers:

- test_open_handler_no_delete_when_navigate_fails (Probe B
  template): the navigate POST raises while the current tab
  is the new about:blank tab. The handler reads the URL
  (about:blank, no fixture substring) and deletes nothing.
  Asserts deleted == [], 3 tabs, owner URL present, current
  is about:blank. This is the exact branch I asked for.
- test_open_handler_no_delete_when_navigate_lands_wrong_url
  (the URL-gate variant I named): the navigate lands on
  https://example.com/wrong, the URL gate raises 'does not
  contain', the handler reads the wrong URL and deletes
  nothing. Asserts the exception message, deleted == [],
  3 tabs, owner URL present. A different trigger and a
  different current-tab state from the first test, not a
  duplicate: the first proves no-delete when the navigate
  never happened, the second when it landed on the wrong
  page.

The handler decision matrix is now covered on three of its
four no-delete sub-branches:

- URL does not contain the substring: tested twice (the
  two tests above).
- URL contains the substring but the handle differs from
  new_handle: tested by the F1 regression test
  (test_open_focus_reverts_during_navigate_refuses_and_
  keeps_owner_tab), which asserts deleted == [] while the
  owner tab carries the fixture URL. This is the
  highest-value sub-branch: it is the one that saves the
  owner tab after a navigate-away.
- URL read raises (cur_url None) and handle read raises
  (cur_handle None): NOT tested. See observation G1; both
  are fail-closed either way, so this is not a condition.

The delete branch itself is tested by
test_open_wrong_h1_closes_only_scratch (deleted ==
[FIXTURE_URL], owner current after restore). My condition
1 is closed, with one test more than I asked for.

## 3. What I verified, with evidence

### 3.1 Suites re-run by me, numbers match the log

- 27 unit tests, re-run by me 20:32 +07: python3 -m
  unittest tests.test_zenproof2_fix -v, Ran 27 tests in
  0.004s, OK. Exit 0. 16 old tests still pass unchanged;
  11 new tests added (F1, 2x C1 no-delete, C4 count gate,
  2x F3a error entry, 2x F3b restore failure, 2x C5
  restore flags, 1x F2 send PROBE print).
- G0a, re-run by me 20:33 +07: python3 -m unittest
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec, Ran 177 tests in 12.505s, OK.
- G0b, re-run by me 20:33 +07: code_exec.validate_program
  passes for PROBE_PROGRAM and SEND_PROGRAM.
- Baseline, checked by me in a temp worktree at 2c76690
  (pre-amend HEAD): 16/16 OK. The amend log's baseline
  claim is true. Worktree removed after the check.

### 3.2 F1 fix works, proven by the redteam repro on both codes

- Against the amended code, /tmp/redteam-repro-f1.py dies
  at cmd_open line 241 with 'current tab changed during
  navigate (current d5525e88 != new b3187ce2); refusing'
  and never reaches cmd_close. The damage no longer
  reproduces. Matches the amend log.
- Against the unamended code (same repro, paths pointed
  at the /tmp/wt-old worktree at 2c76690): cmd_open
  returns ok, the owner tab is navigated to the fixture
  URL, and cmd_close DELETEs it (owner tab still present
  False, deleted urls = [fixture URL]). The repro genuinely
  reproduces the hole on the old code and is closed by the
  amend. This is the strongest evidence in the amend:
  a before/after on the same repro, not just a new test.

### 3.3 The 11 new tests: 10 strong and distinct, 1 weak

Read the whole test file and judged each new test on
whether it executes new behavior or only pins text:

- F1 regression: strong. Executes the TOCTOU path end to
  end (flip inside POST /url, post-navigate check raises,
  handler handle-mismatch refuses the DELETE) and asserts
  0 deletions, owner tab survives, new tab left as
  about:blank. It also documents the navigate-away
  residual honestly in its comment.
- 2x C1 no-delete: strong, see section 2.
- C4 count gate: strong. The stale-handle fake returns
  an existing handle without creating a tab; open raises
  'did not increase the tab count', 0 deletions, 2 tabs,
  owner still current. The +2 growth case is not tested,
  but it hits the same `!=` comparison, so no separate
  test is needed. See G5.
- 2x F3a error entry: strong as limitation pins. The
  pre-check test proves an unreadable fixture tab is
  invisible to URL identity (a second fixture tab opens,
  count 4, two tabs carry the fixture URL). The close test
  proves cmd_close reports already_closed while the tab
  still exists. Both assert the exact wrong-looking
  outcome and name the runner-side detector (count check,
  count_restored flag) in their docstrings.
- 2x F3b restore failure: strong. The list test proves
  cmd_list reports the last-scanned tab as current after
  a silent restore failure. The open test proves the (c)
  check mitigates it in cmd_open (open succeeds, owner
  untouched). The pair covers both the hole and the
  mitigation.
- 2x C5 restore flags: strong. The scan-error test makes
  list_tabs fail on the third call (inside
  _restore_original, after the scratch close succeeded)
  and asserts scan_error True with original_ambiguous and
  original_missing both False. The full-handle test uses
  two handles sharing an 8-char prefix and asserts
  restore_failed True with the scratch deleted and the
  owner present. Both test the exact observations Council
  3 named.
- F2 send PROBE print: WEAK, and it is the only F2 test.
  It asserts a string is present in SEND_PROGRAM and that
  a hand-built PROBE line parses through parse_probe_line.
  It never executes the PROBE print, never runs phase4,
  and never touches the new runner code. See condition C1.

### 3.4 Prep file fix confirmed

- Grep for 'Clone zen thread' returns 5 occurrences:
  line 12 (the amendment note explaining the stale
  premise), line 535 (P2.2 H1 content confirmation),
  line 714 (section 6, the fixture JS sets the H1),
  line 718 (Content: h1 'Clone zen thread'), line 760
  (checklist P2.2 H1 confirmation). All are H1 content
  confirmations or the amendment note. No title gate
  remains.
- Grep for 'title verified' and 'sets the title' returns
  nothing. The two extra stale checklist lines Council 3
  missed (P3.1 and P6.1 '(title verified)') are now
  '(URL verified)', as the amend log claims.
- The amendment note at the file head states the run-order
  rules (fresh run number, fixed run2.py only, run 1
  forbidden, orphan about:blank closed by hand in the Zen
  UI). Council 1 C1, Council 2 condition 2, and Council 3
  C1 are closed.

### 3.5 Diff scope and hygiene match the log

- git diff --stat b27818d^..b956176: 5 files, 893
  insertions, 72 deletions. Excluding the log file
  itself (381 lines), that is 512 insertions, 72
  deletions, exactly what the amend log states
  (zen-tab.py +106, run2.py +27, test file +305, prep
  file +146 net of rewrites).
- 0 em dash (U+2014) and 0 en dash (U+2013) in all 4
  changed files, counted by me with grep.
- Fixture untouched: sha256 of
  tests/two_vision_fixture.html is
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72f
  ba6cbf, identical to FIXTURE_SHA.
- The pre-existing dirty
  tests/realistic/clone1-batch3/results.json was not
  touched by the amend and is not in these commits. I
  did not touch it either.

## 4. The gap: phase-4 runner code has zero behavioral coverage

This is the one test-completeness gap in the amend, and
it is the F2 mitigation itself. Redteam F2 demanded the
phase-4 re-switch plus snapshot URL gate; the amend
implemented both in run2.py phase4:

- re-switch by URL immediately before the send, raising
  'send switch landed on %r, not the scratch tab' when
  the switched URL does not contain TARGET;
- gate the send snapshot URL with parse_probe_line,
  raising 'send program printed no snapshot line' when
  no PROBE line exists, and raising through
  parse_probe_line on a wrong URL or wrong count;
- record send_url and send_count in the run results.

None of that code is executed by any test. The only F2
test (test_send_program_prints_snapshot_url) asserts a
string in SEND_PROGRAM. If the phase-4 code had a bug
(a wrong key, a wrong variable, a gate on the wrong
list), the suite would stay green and only a live run
would catch it. That is exactly what the suite exists
to prevent before a live proof.

I proved the test is writable, with my own probe
(/tmp/phase4-probe.py, read-only, not committed): a real
Runner() constructs cleanly (Harness.__init__ only
mkdirs, no SSH), and phase4 runs with hypr, tab, and
oneshot_zen mocked:

- happy path: send_url is the fixture URL, send_count
  is 1;
- wrong-URL envelope: raises ValueError from
  parse_probe_line ('probe snapshot URL ... does not
  contain ...');
- missing PROBE line: raises RuntimeError ('send
  program printed no snapshot line').

All three gates fire correctly on the current code. The
condition below only asks that this coverage land in the
suite, so the next live proof is not the first execution
of the F2 mitigation. Detail for the test author: the
wrong-URL gate raises ValueError (from parse_probe_line),
not RuntimeError, so assert accordingly; the switch
check raises RuntimeError.

## 5. Minor observations (not conditions)

- G1: handler read-failure branches untested. When _url
  raises inside the handler, cur_url is None and nothing
  is deleted; when _current raises, cur_handle is None
  and nothing is deleted. No suite test drives either.
  This is fail-closed either way: the DELETE is gated on
  the reads succeeding, so a read failure cannot cause a
  delete even if the try/except were absent (the handler
  would abort before the DELETE, only with a different
  exception surfacing). A test would only pin which
  exception propagates. Cheap to add with a
  call-counting fake, recommended, not gated.
- G2: the DELETE-raise swallow and the post-DELETE
  restore-failure swallow inside the open handler are
  untested (the fake's DELETE never raises). Both were
  in the fix, not introduced by the amend. Same
  fail-closed shape as G1.
- G3: the readyState != complete raise and the rect-None
  raise are unreachable in the fake (ready is always
  'complete'; the rect is fixture-tab-aware, so it is
  present whenever the URL gate passed). Pre-existing
  fake limitation from the fix, not introduced by the
  amend.
- G4: the count-gate test covers 0-growth only. +2
  growth hits the same `!=` comparison and the same
  raise, so no separate test is needed. Recorded here
  so nobody files it as a gap later.
- G5: the amend log is honest about the F1 residual
  (no atomic verify-and-navigate in WebDriver; the
  window is narrowed to navigate-away, never a delete
  through the handler) and about the close-after-failed-
  open residual (a later URL-based close would target
  a navigated owner tab; the runner's opened flag is
  what prevents it). Both residuals are stated, not
  hidden, and neither is a live-run gate beyond what
  the reviews already said.

## 6. Verdict: GO WITH CONDITIONS

The amend closes every condition it was given, and my
own condition 1 (the no-delete branch test) is closed
with two distinct tests, not one. The F1 fix is proven
by a before/after on the same redteam repro. The prep
file is fully corrected. 27/27, G0a 177/177, and G0b
pass on my own re-runs. The one gap is real but small
and cheap to close: the new phase-4 runner code has no
behavioral test, so the F2 mitigation has never been
executed outside a live run.

Condition, to be satisfied before the next live proof
(not before landing this amend):

- C1. Add behavioral unit tests for the new phase-4
  runner logic in run2.py, using a Runner with mocked
  hypr/tab/oneshot_zen (my /tmp/phase4-probe.py proves
  this works): happy path records send_url and
  send_count; a wrong-URL or wrong-count send snapshot
  raises (note: ValueError from parse_probe_line, not
  RuntimeError); a missing PROBE line raises; a switch
  landing on a non-fixture URL raises. Land as a
  follow-up commit, re-run the suite, G0a, and G0b.

The Muse chat tab closed by run 2 attempt 2 is NOT
reopened by this amend. Recovery stays the
coordinator's decision, as the amend log states.

## 7. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received ~20:31 +07, 22/11/2026. HEAD at review
  start b956176, equal to origin/todolist-push after
  fetch.
- 27 unit tests, re-run by me 20:32 +07: python3 -m
  unittest tests.test_zenproof2_fix -v, Ran 27 tests in
  0.004s, OK, exit 0.
- G0a, re-run by me 20:33 +07: python3 -m unittest
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec, Ran 177 tests in 12.505s, OK.
- G0b, re-run by me 20:33 +07: code_exec.validate_program
  passes for PROBE_PROGRAM and SEND_PROGRAM.
- Baseline, worktree at 2c76690, 20:33 +07: Ran 16
  tests in 0.002s, OK. Worktree removed after the check.
- F1 repro, amended code, 20:33 +07: dies at zen-tab.py
  line 241, 'current tab changed during navigate
  (current d5525e88 != new b3187ce2); refusing', never
  reaches cmd_close.
- F1 repro, unamended code (worktree 2c76690), 20:33
  +07: cmd_open ok, owner tab navigated to the fixture
  URL, cmd_close DELETEs it (owner tab still present
  False, deleted urls = [fixture URL]).
- Phase-4 probe, /tmp/phase4-probe.py, 20:34 +07: happy
  path send_url = fixture URL, send_count = 1;
  wrong-URL raises ValueError from parse_probe_line;
  missing-PROBE raises RuntimeError ('send program
  printed no snapshot line').
- Prep file grep, 20:34 +07: 'Clone zen thread' 5
  occurrences, all H1 content confirmations or the
  amendment note; 'title verified' 0; 'sets the title' 0.
- Diff scope, 20:33 +07: git diff --stat
  b27818d^..b956176, 5 files, 893 insertions, 72
  deletions (512/72 excluding the 381-line log file).
- Dash counts, 20:34 +07: U+2014 0, U+2013 0 in all 4
  changed files.
- Fixture sha, 20:34 +07: 147494cda4c6ae24a51ced03ccdfb3
  fc5a79a1bbab56dcdfc5afb4f72fba6cbf, matches FIXTURE_SHA.
- Files changed by me (review only): improvements/
  w-zenproof2-amend-council-2-review.md (new, this
  file). No amend file modified. No live run. No
  reviewer spawned.
