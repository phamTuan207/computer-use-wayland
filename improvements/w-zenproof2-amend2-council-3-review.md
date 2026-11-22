# Council 3 review: W-ZENPROOF2-AMEND2 (prep file + residuals)

Reviewer: Council 3, independent (not W-ZENPROOF2-AMEND2, not
W-ZENPROOF2-AMEND, not W-ZENPROOF2-FIX, not W-ZENPROOF2, not
COORD-CLICK-9). Report goes to Muse tong, not directly to Pham
Tuan. No amend modified, no live run, no tab opened, navigated,
or deleted in Pham Tuan's Zen. All verification is code/unit
level only, plus my own re-runs of the unit and G0a suites and
the redteam H1 repro. No em dash or en dash anywhere in this
file. No personal info.

## 0. Task and sources (20:40 +07, 22/11/2026)

- Task received ~20:40 +07. Branch todolist-push, repo
  ~/workspace/computer-use-wayland, HEAD bcc249c at review
  start (verified equal to origin/todolist-push, section 5).
- Amend under review, 4 commits, each exactly 1 file:
  - e9994d9 zen-tab.py: H1 membership check + H2 guarded
    restore reads.
  - d8f8ac3 tests/test_zenproof2_fix.py: 36 tests (9 new).
  - 16075f6 prep file: recovery line + G1 note.
  - bcc249c improvements/w-zenproof2-amend2-log.md: amend log.
  run2.py was NOT changed by this amend (the phase-4 tests
  execute its existing code). Diff stat ee6b487..bcc249c also
  contains 1f28b3f, the Council 2 pillfix review from another
  lane; it is not part of this amend.
- Sources read before judging:
  - improvements/w-zenproof2-amend2-log.md (the amend log,
    304 lines, read in full).
  - Full diff of e9994d9 and 16075f6 (read line by line).
  - The 9 new tests in tests/test_zenproof2_fix.py (read in
    full), plus the updated C4 test.
  - improvements/w-zen-delegate-liveproof-prep.md: amendment
    note (lines 1-45), phase-4 section (lines 595-670),
    section 6 scratch target (lines 720-740), and greps for
    every remaining 'Clone zen thread' and title-gate phrase.
  - improvements/c5-zenproof-runs/c5-zen-delegate-run2.py:
    ev() (line 281), phase5 (line 527), cleanup (opened flag).
  - scripts/zen_backend.py _resolve_target (lines 189-208,
    re-read for the H3 wording check).
  - All 4 amend 1 reviews (7c6e80d, ddea95a, 4f8825d,
    ee6b487) for the condition list in section 4.

## 1. Time log (wall-clock Asia/Ho_Chi_Minh)

- 20:40 +07, T+0m: task received, amend log + diff stat read.
- 20:40 +07, T+0m: full diff of e9994d9 and 16075f6 read;
  36 unit tests re-run by me, 36/36 OK.
- 20:41 +07, T+1m: _handles/_current/_full_handle and the
  open exception handler read; _restore_original grep for
  bare _title/_url calls; prep file greps; ev()/phase5 read;
  redteam H1 repro re-run by me; G0a, G0b, fixture sha,
  dash counts, ls-remote.
- 20:41 +07, T+1m: review written, committing.

## 2. What I verified, with evidence

### 2.1 Diff scope is exactly the amend, nothing else

- git log ee6b487..bcc249c: 4 amend commits plus 1f28b3f
  (another lane). git show --stat per amend commit: each
  touches exactly 1 file (zen-tab.py 47+/11-, test file
  205+/4-, prep file 14+/1-, log 304+). No shared library
  touched. The pre-existing dirty
  tests/realistic/clone1-batch3/results.json is not in these
  commits.
- 0 em dash (U+2014) and 0 en dash (U+2013) in all 4 changed
  files, counted by me with grep -c (0 in each file).
  Fixture untouched: sha256 of tests/two_vision_fixture.html
  is 147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72
  fba6cbf, identical to FIXTURE_SHA.

### 2.2 The 36 tests pass on my own run, and the new tests are real

- Command: python3 -m unittest tests.test_zenproof2_fix.
  Output: Ran 36 tests in 0.006s, OK. Exit 0. I ran it
  myself, not trusting the log's 36/36.
- G0a, re-run by me: python3 -m unittest
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec, Ran 177 tests in 12.455s, OK.
- G0b, re-run by me: code_exec.validate_program passes for
  both PROBE_PROGRAM and SEND_PROGRAM (both return AST
  Module objects, no exception).
- I read all 9 new tests in full. They are behavioral, not
  string-presence assertions:
  - 2x H1: _StaleHandleWithTab returns the owner handle AND
    creates a tab, in both select modes. Both assert the
    'existing handle' raise, zero deletions, 3 tabs, owner
    tab URL unchanged, new tab left as unnavigated
    about:blank. The select_new=False variant is the run 2
    mode (owner tab already current, so the (c) check would
    pass with no select at all).
  - 1x H2: scan fails on the 3rd list_tabs call AND the
    GET /title and GET /url reads raise. cmd_close returns
    ok with scan_error True, current_title None,
    current_url None, scratch tab deleted, owner tab present.
  - 1x count gate: a genuinely new handle that creates no
    tab is refused by the count gate ('did not increase the
    tab count'), 0 deletions, owner tab intact. The old C4
    test was updated to expect the membership message
    instead, which is correct: the membership check now
    refuses the stale-handle case first and subsumes it.
  - 5x phase 4: _run_phase4 builds a real Runner, mocks
    hypr/tab/oneshot_zen, and executes runner.phase4().
    Happy path records send_url/send_count/completed 4;
    wrong URL and wrong count raise ValueError from
    parse_probe_line; missing PROBE line raises RuntimeError
    ('send program printed no snapshot line'); switch
    landing on the wrong tab raises RuntimeError before the
    send program runs.
- Redteam H1 repro, re-run by me against the amended code
  (/tmp/redteam-amend-repro-h1.py, still existed): cmd_open
  REFUSED with 'new tab returned an existing handle
  b061eff7; refusing to navigate or close', owner tab URL
  still https://muse.ai/thread/750c8dae-58fb-4a65-82ac-753e
  78d6ce93, deletions []. The damage no longer reproduces.

### 2.3 H1 membership check is correct as written

- `before` is the raw list from GET /window/handles,
  captured at the start of cmd_open before POST /window/new.
  `new_handle` is the full handle from the POST response.
  `if new_handle in before` is therefore a full-string
  membership test, not a prefix match. Correct.
- Placement is correct: immediately after POST /window/new,
  before the count gate, before the (c) check, before any
  /url navigate or DELETE. It closes the redteam H1 path at
  its first step: a stale handle that also creates a tab
  (count +1, so the count gate passes) is refused before
  anything can select or navigate to the owner tab.
- The module docstring now states the returned handle must
  not be one that already existed before the open, next to
  the count +1 requirement.

### 2.4 H2 restore reads are all guarded

- Grep for bare _title(z)/_url(z) calls inside
  _restore_original: none remain. All 4 branches (scan_error,
  missing/ambiguous, restore_failed, success path) assign
  through _safe_title_url(z), which catches per-read and
  returns (None, None) on failure. The docstring states the
  guard.
- The remaining bare _title/_url calls in zen-tab.py are
  outside _restore_original and are fail-closed by design:
  cmd_open pre-check reads (raise before opening anything),
  post-navigate checks (raise, no DELETE), the open exception
  handler (guarded by try/except to None, already verified in
  amend 1), and switch/eval return values (raise, command
  errors). None of them can mask a successful close.

### 2.5 Prep file: both doc items present and correct

- Recovery line (Council 1 C1, adopted by Redteam C4):
  present in the amendment note, lines 31-34. Wording is
  exactly what was ordered: when the owner tab carries the
  fixture URL after a refused open, the coordinator navigates
  it back to the Muse thread by hand in the Zen UI, never via
  a Marionette navigate or DELETE, and verifies the pre-check
  passes before the next run. It also records the reason
  (the leftover after a refused open is not always an empty
  about:blank tab). Correct placement: in the amendment note,
  directly after the orphan about:blank rule it extends.
- G1 note (Council 3 C4): present at line 622, immediately
  after the phase-4 program listing and before P4.1. Wording
  is correct: the program above is the recorded RUN-1 program
  (message ZEN-DELEGATE-R1-IGNORE-TEST, no PROBE print); the
  run-2 program in c5-zen-delegate-run2.py adds the PROBE
  print after dom_observe (Redteam F2), which phase 4 gates
  on; copy run2.py, never copy this listing into a run, or the
  run fails phase 4 after the send ('send program printed no
  snapshot line').
- No title gate remains anywhere in the file. Grep for
  'title verified', 'verify the current title', 'sets the
  title': 0 matches. 'Clone zen thread' occurs only 5 times:
  line 12 (amendment note history: the wrong premise, stated
  as the cause of the incident), line 540 (H1 content
  confirmation), line 727 (section 6: the fixture JS sets the
  H1 text, the document title stays the static 'Two-vision
  benchmark fixture'), line 731 (content list, h1), line 773
  (checklist P2.2: URL substring + H1 + readyState, no title
  gate). All 5 are correct uses.

### 2.6 Residuals in log section 4 are honest and complete

- "WebDriver protocol offers no atomic verify-and-navigate
  (the F1 residual race is narrowed, not eliminated)":
  honest. The post-navigate check is a separate HTTP call
  after the navigate; a focus change between navigate and
  check is caught (raise, no DELETE), but the navigate
  itself already happened, so the wrong tab's content can
  still be changed. What the fix guarantees is no DELETE
  follows and the run errors, and the recovery line now
  covers restoring the navigated tab. Narrowed to
  content-change-only is exactly what the log says.
- "The count gate assumes a single lane (a concurrent tab
  change causes a spurious fail-closed refusal, never a wrong
  navigate)": honest. With the H1 membership check, a
  concurrent tab creation makes the count grow by 2, so the
  count gate refuses. The outcome is a spurious refusal,
  never a wrong navigate. Correct.
- "Backend first-match stays a known limitation": honest.
  _resolve_target (zen_backend.py 189-208) still returns the
  first match and does not refuse on duplicates; tab_at
  re-reads the list by index. The mitigation is real: the
  phase-4 switch refuses on ambiguity (_find_in_scan
  raises), and phase-5 ev() goes through tab('eval', TARGET)
  which resolves fresh and raises on ambiguity, so a
  duplicate makes the run error, never a false PASS. I
  traced both paths in run2.py (ev line 281, phase5 line
  527), not just trusting the log.
- "Unreadable tabs stay invisible to URL identity": honest
  (Redteam F3a known limitation, pinned by tests).
- The log incorporates the amend 1 section-4 residuals by
  reference ("Known limitations recorded in the amend 1 log
  section 4 still hold, plus the ones named here"), which
  includes the opened-flag runner-side convention. That is
  acceptable: the residuals are named in the amend 1 log and
  this log does not claim to close them.
- H3 (Redteam LOW) wording correction is done in this log,
  not by editing the amend 1 log (a committed historical
  record). The correction is accurate: the PROBE gate is
  detection-only, the input follows the current tab, and the
  real guards are the switch refusing on ambiguity and
  phase-5 ev() raising on ambiguity. Worst case is a send to
  a duplicate fixture tab (harmless test content) with the
  run recorded as error. No owner-tab impact. Correct.

### 2.7 No doc item from amend 1 remains unclosed

Checked against all 4 amend 1 reviews:

- Council 1 C1 (recovery line): CLOSED, section 2.5.
- Council 2 C1 (phase-4 behavioral tests): CLOSED, 5 tests,
  section 2.2.
- Council 3 C1 (re-execution): SATISFIED. Council 3 could
  not execute code in the amend 1 review; the re-execution
  was done independently by Council 1, Council 2, and
  Redteam for amend 1, by this worker for amend 2, and by
  me for this review (36/36, G0a 177/177, G0b, H1 repro,
  fixture sha).
- Council 3 C2 (push verification): SATISFIED. git
  ls-remote origin todolist-push returns
  bcc249ce0b075cb61395844f2480aed14865ee9b, equal to local
  HEAD. The 4 amend commits are on remote. (The amend 1
  push verification was satisfied when Muse tong committed
  and pushed the Council 3 review itself, 4f8825d.)
- Council 3 C3 (live verification owed): CARRIED OVER by
  design, not closed here. The amend 2 log section 4 states
  this explicitly. The next proof is a fresh run number with
  a fresh intent/message, copying the fixed run2.py, after
  council + redteam review of this amend. Correct.
- Council 3 C4 (G1 note): CLOSED, section 2.5.
- Redteam C1 (H1): CLOSED, sections 2.2 and 2.3.
- Redteam C2 (H2): CLOSED, sections 2.2 and 2.4.
- Redteam C3 (adopt Council 2): CLOSED.
- Redteam C4 (adopt Council 1): CLOSED.
- Redteam C5 (re-execution): SATISFIED, same evidence as
  Council 3 C1.

## 3. Gaps and minor observations (not blockers)

- G1 (minor, doc hygiene): P4.1 still carries the run-1
  intent string 'c5-zen-delegate-r1', and the phase-4
  listing still carries the run-1 message
  ZEN-DELEGATE-R1-IGNORE-TEST. The amendment note and the
  checklist G0d already require a fresh run number with a
  fresh intent/message, so a careful runner does not reuse
  them, and a reused intent would fail-closed at the ledger
  anyway. Not a live-run hazard. A 1-line clarification in
  P4.1 (pointing at the amendment note for the intent) would
  remove the last verbatim-copyable run-1 string; not a
  condition for GO.
- G2 (minor): the recovery line's "verifies the pre-check
  passes before the next run" is verified by the next run's
  own phase 1/2 pre-check (or a manual list call). The line
  as written is a correct instruction; no change needed.
- G3 (minor): the H1 error message truncates the handle to
  8 characters (new_handle[:8]), consistent with the file's
  display convention everywhere else. Fine.
- G4 (minor): the H1 membership check compares against
  `before`, captured before the pre-check scan. A tab
  opening or closing between _handles and POST /window/new
  would make `before` stale, but every resulting mismatch
  refuses fail-closed (membership or count gate). Not a gap.

## 4. Verdict: GO

The amend closes every condition from the amend 1 reviews
that can be closed without a live run. The two doc items in
my scope are present, correctly worded, and correctly placed
in the prep file; no title gate remains anywhere in the file;
no doc item from amend 1 remains unclosed except the live
verification, which is carried over by design and stated as
such. The H1 membership check and H2 guarded reads are
correct as written and covered by real tests that I re-ran
myself, including the redteam H1 repro. The residuals in log
section 4 are honest, complete, and traced against the code.
The live proof is the next step, on a fresh run number with a
fresh intent/message, copying the fixed run2.py, in a quiet
window, after redteam review of this amend.

No conditions. The Muse chat tab closed by run 2 attempt 2
is NOT reopened by this amend. Recovery stays the
coordinator's decision.

## 5. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received ~20:40 +07, 22/11/2026. HEAD at review
  start bcc249c.
- 36 unit tests, re-run by me 20:40 +07: python3 -m
  unittest tests.test_zenproof2_fix, Ran 36 tests in 0.006s,
  OK, exit 0.
- G0a, re-run by me 20:41 +07: python3 -m unittest
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec, Ran 177 tests in 12.455s, OK.
- G0b, re-run by me 20:41 +07: code_exec.validate_program
  passes for PROBE_PROGRAM and SEND_PROGRAM.
- Redteam H1 repro, re-run by me 20:41 +07: python3
  /tmp/redteam-amend-repro-h1.py, cmd_open REFUSED with
  'new tab returned an existing handle b061eff7; refusing
  to navigate or close', owner tab URL still the Muse thread,
  deletions [].
- Diff scope 20:40 +07: git show --stat per commit, each
  amend commit touches exactly 1 file; run2.py unchanged.
- Fixture 20:41 +07: sha256
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72
  fba6cbf, matches FIXTURE_SHA.
- Dash counts 20:41 +07: U+2014 0, U+2013 0 in all 4 changed
  files, counted by me.
- Prep file 20:41 +07: 'Clone zen thread' 5 occurrences
  (lines 12, 540, 727, 731, 773), all correct uses;
  'title verified' / 'verify the current title' / 'sets the
  title' 0 matches; recovery line lines 31-34; G1 note
  line 622.
- _restore_original 20:41 +07: grep for bare _title(z) /
  _url(z) calls inside the function, 0 remain; all 4 branches
  use _safe_title_url.
- _handles 20:40 +07: returns the raw list from GET
  /window/handles (full handle strings); new_handle is the
  full handle from the POST response.
- ls-remote 20:41 +07: origin/todolist-push =
  bcc249ce0b075cb61395844f2480aed14865ee9b, equal to local
  HEAD.
- Files changed by me (review only): improvements/
  w-zenproof2-amend2-council-3-review.md (new, this file).
  No amend file modified. No live run. No reviewer spawned.
