# Council 2 review: W-ZENPROOF2-AMEND2 (phase-4 tests + H1/H2 close-out)

Reviewer: Council 2, independent (not W-ZENPROOF2-AMEND2, not
W-ZENPROOF2-AMEND, not W-ZENPROOF2-FIX, not W-ZENPROOF2, not
COORD-CLICK-9). Report goes to Muse tong, not directly to the owner. No amend modified, no live run, no tab opened, navigated,
or deleted in the owner's Zen. All verification is code/unit
level only, plus my own re-runs of the unit and G0a suites and
my own probes. No em dash or en dash anywhere in this file. No
personal info.

## 0. Task and sources (20:40 +07, 22/11/2026)

- Task received ~20:40 +07. Branch todolist-push, repo
  ~/workspace/computer-use-wayland, HEAD at review start
  bcc249c (the amend-2 log commit).
- Amend under review, 4 commits:
  - e9994d9 zen-tab.py: H1 membership check + H2 guarded
    restore reads.
  - d8f8ac3 tests/test_zenproof2_fix.py: 36 tests (9 new).
  - 16075f6 prep file: recovery line + G1 note.
  - bcc249c improvements/w-zenproof2-amend2-log.md: amend log.
- My condition from the amend-1 review (ddea95a) was C1:
  behavioral tests for the phase-4 runner code (happy path,
  wrong URL, wrong count, missing PROBE, switch landing on the
  wrong tab). This review checks whether that condition is
  closed, and whether any phase-4 branch is still untested.
- Sources read before judging:
  - improvements/w-zenproof2-amend2-log.md (the amend-2 log,
    304 lines, read in full).
  - Full diff of e9994d9, d8f8ac3, 16075f6 (read line by line,
    not skimmed).
  - improvements/c5-zenproof-runs/c5-zen-delegate-run2.py
    phase4 (lines 483-525) and tab() (lines 270-279).
  - improvements/c5-zenproof-runs/zen-tab.py cmd_open head,
    _scan, _handles, _switch, cmd_close, _restore_original.
  - /tmp/redteam-amend-repro-h1.py (re-run, not trusted
    blindly). /tmp/phase4-probe.py still exists (read only;
    the amend-2 tests supersede it).

## 1. Time log (wall-clock Asia/Ho_Chi_Minh)

- 20:40 +07, T+0m: task received, amend-2 log read in full,
  4 commits confirmed on todolist-push.
- 20:40 +07, T+0m: full diff of e9994d9, d8f8ac3, 16075f6
  read; phase4 code and tab() read.
- 20:41 +07, T+1m: 36 unit tests re-run by me, 36/36 OK;
  G0a 177/177 re-run by me, OK; G0b both programs validated
  by me; fixture sha and dash counts checked by me.
- 20:41 +07, T+1m: redteam H1 repro re-run by me against
  the amended code; 4 own probes for the uncovered phase-4
  branches; H2 call-count traced; `before` capture verified.
- 20:41 +07, T+1m: review written, committing.

## 2. What I verified, with evidence

### 2.1 My C1 condition from the amend-1 review: CLOSED

The amend adds exactly the 5 behavioral tests I required,
all in RunnerFixTest, all running phase4 on a real Runner
with hypr/tab/oneshot_zen mocked (the shape of my
/tmp/phase4-probe.py, now landed in the suite):

- test_phase4_happy_path_records_send_url_and_count: runs
  phase4, asserts send_url is the fixture URL, send_count
  '1', completed 4, send_switch URL contains the fixture
  URL.
- test_phase4_wrong_url_snapshot_raises: send snapshot URL
  https://example.com/ raises ValueError from
  parse_probe_line.
- test_phase4_wrong_count_snapshot_raises: count 0 raises
  ValueError.
- test_phase4_missing_probe_line_raises: no PROBE line
  raises RuntimeError ('send program printed no snapshot
  line').
- test_phase4_switch_landing_wrong_tab_raises: re-switch
  landing on https://example.com/ raises RuntimeError
  ('send switch landed on ...') before the send runs.

These are behavioral, not string assertions. I verified
this by reading phase4 (lines 483-525) and tracing each
test through it: _run_phase4 builds a real Runner, calls
runner.phase4(), and the assertions read
runner.results['program'] and runner.results['send_switch'],
which only exist after the real code ran lines 493-522.
The old string-only F2 test (asserting 'PROBE' in
SEND_PROGRAM) is still in the suite, but it is no longer
the only F2 test. The F2 mitigation has now been executed
outside a live run, in all 5 required shapes.

### 2.2 The 9 new tests: all real, none weak, none duplicative

- 2x H1 (select_new=True and select_new=False): different
  modes, different trigger paths. True mode: the (c) check
  would otherwise select the owner tab. False mode (the run
  2 mode): the owner tab is already current, so the (c)
  check would pass with no select at all. Both assert the
  raise ('existing handle'), zero deletions, 3 tabs, owner
  URL unchanged. Redteam required a regression test in both
  modes; both are present.
- 1x H2: the scan fails inside _restore_original AND the
  _title/_url reads fail, cmd_close still returns ok with
  scan_error True and current_title/current_url None. I
  traced the call count by hand to confirm the test
  exercises the real H2 path: _handles does not call
  list_tabs (it GETs /window/handles), so one _scan is
  exactly one list_tabs call; cmd_close calls _scan twice
  before _restore_original (pre-DELETE scan, post-DELETE
  verification scan), so the fake's threshold (>= 3) fires
  exactly inside _restore_original. The fake's _wd raises
  on GET /title and GET /url, which is exactly what
  _title/_url call, so the _safe_title_url guard is
  exercised, not bypassed.
- 1x count gate (new handle, no tab): the membership check
  passes (the handle was not in `before`), the count gate
  refuses with 'did not increase the tab count'. This is
  distinct from the updated old C4 test, which now expects
  the membership refusal ('existing handle') for a stale
  handle that creates no tab. The log is honest about the
  first run being 35/36 and the old test being updated with
  a reason, not silently reworded to pass.
- 5x phase-4: see 2.1. Each has a distinct trigger and a
  distinct expected exception or result. None of the 9
  overlaps another.

### 2.3 H1 membership check: correct, and I re-ran the repro

- `before = _handles(z)` is captured before POST
  /window/new (cmd_open head, verified by reading). _handles
  returns full handles (GET /window/handles);
  new_handle is the full handle from the response. The
  check `new_handle in before` is a full-to-full
  membership test, placed immediately after the response
  and before the count gate and before any navigate or
  DELETE. The module docstring states the requirement.
- I re-ran /tmp/redteam-amend-repro-h1.py against the
  amended code myself: cmd_open REFUSED with 'new tab
  returned an existing handle 855efa98; refusing to
  navigate or close', owner tab URL unchanged
  (https://muse.ai/thread/750c8dae-58fb-4a65-82ac-753e78d6ce93),
  deletions []. The damage no longer reproduces.
- The side effect the log reports is real and correctly
  handled: the old C4 test's fake returns an existing
  handle without creating a tab, so the membership check
  now refuses it first. That is the correct behavior (the
  membership check subsumes that case), and the count gate
  keeps its own dedicated test for a genuinely new handle.

### 2.4 H2 guarded reads: correct, and the guard is complete in _restore_original

- _safe_title_url(z) wraps _title and _url in separate
  try/except blocks and returns (None, None) on failure.
  All four _title/_url call sites inside _restore_original
  now go through it: the scan_error branch, the
  missing/ambiguous branch, the restore_failed branch, and
  the success path. I checked all four in the diff; no
  bare _title/_url call remains in _restore_original.
- The docstring states the guard. The H2 test (2.2) proves
  the behavior.

### 2.5 Prep file and H3: both doc items landed as specified

- Recovery line (Council 1 C1): added to the amendment
  note after the orphan about:blank rule. It says the
  coordinator navigates the owner tab back to the Muse
  thread by hand in the Zen UI, never via a Marionette
  navigate or DELETE, and verifies the pre-check passes
  before the next run, with the reason (the leftover after
  a refused open is not always an empty about:blank tab).
- G1 note (Council 3 C4): added after the phase-4 listing.
  It says the listing is the recorded RUN-1 program (no
  PROBE print) and to copy run2.py, never the listing, or
  phase 4 fails after the send ('send program printed no
  snapshot line').
- H3 (Redteam LOW): the amend-2 log corrects the amend-1
  wording in its own log (section 2, H3): the PROBE gate
  is detection-only, the real guards are the phase-4
  switch refusing on ambiguity and the phase-5 ev() raising
  on ambiguity. It does not edit the committed amend-1
  log, which is correct: a committed historical record is
  not rewritten.

### 2.6 Suite, G0a, G0b, fixture, dashes: re-run by me

- 36 unit tests, re-run by me 20:41 +07: python3 -m
  unittest tests.test_zenproof2_fix, Ran 36 tests in
  0.009s, OK, exit 0. 27 old tests pass (one updated for
  the new refusal message, see 2.2); 9 new tests pass.
- G0a, re-run by me 20:41 +07: python3 -m unittest
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec, Ran 177 tests in 12.442s, OK.
- G0b, validated by me 20:41 +07:
  code_exec.validate_program passes for PROBE_PROGRAM and
  SEND_PROGRAM (both returned AST Module objects, no
  exception).
- Fixture untouched: sha256 of
  tests/two_vision_fixture.html is
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6cbf,
  identical to FIXTURE_SHA.
- 0 em dash (U+2014) and 0 en dash (U+2013) in all 4
  changed files (zen-tab.py, test file, prep file, amend-2
  log), counted by grep.
- Diff scope: 4 files, 570 insertions, 16 deletions
  (e9994d9^..bcc249c), matching the log. run2.py was not
  changed by this amend; the phase-4 tests execute its
  existing code, which is the correct scope for a test
  condition.

## 3. The one remaining gap: 2 phase-4 branches still untested

My C1 is closed, but phase 4 is not yet fully covered.
I probed the 2 remaining branches myself (same
_run_phase4 helper shape, own probe script, not the
suite). The code behaves correctly in all 4 sub-cases,
so this is a test-coverage gap, not a code bug:

- Active-window check (run2.py lines 484-487): my probe
  with hypr returning address 0xDEF (not the Zen address)
  raises RuntimeError 'active window moved off Zen before
  send'. Correct, but no suite test exercises it.
- Final ok/completed gate (run2.py lines 523-525): my
  probes prove it fires in all 3 sub-cases: envelope ok
  False with a valid PROBE line raises 'send program did
  not complete 4/4'; completed 3 raises the same; a log
  with a valid PROBE line but no dom_act line (completed
  None) raises the same. Correct, but no suite test
  exercises it.

This matters because the final gate is the last line of
defense against recording a failed send as success: if
it were ever broken, phase4 would return success on a
failed send and the run would record a false PASS. The
whole point of C1 was that phase-4 must be executed by
tests before it runs live; leaving its last gate
unexecuted repeats the same mistake one branch later.
See condition C1.

## 4. Small notes (not blockers)

- G1: the 5 phase-4 tests mock oneshot_zen to return the
  envelope regardless of arguments, so they do not assert
  it was called with SEND_PROGRAM and INTENT. phase4
  passes those as literals (line 498-499), so there is no
  variable to get wrong; the important execution (switch
  check, PROBE gate, completed parsing, final gate) is
  exercised. Not a condition.
- G2: _safe_title_url is only tested with both reads
  failing. A partial failure (title fails, URL succeeds,
  or the reverse) is not tested. The two try/except blocks
  are independent and symmetric, and the both-fail test
  exercises the guard mechanism; a partial-failure test
  would be nice but is not required.
- G3: tab() raises RuntimeError when the driver returns
  ok False (lines 276-278), so a switch that fails at the
  driver never reaches phase4's URL check. The switch test
  (wrong URL with ok True) therefore covers the realistic
  failure path. No gap.
- G4: the H1 fake's select_new=True mode sets the fake
  current to the new tab while returning the owner handle.
  That is slightly inconsistent with real Marionette
  semantics (the returned handle identifies the current
  window), but the membership check fires before any
  current-based logic, so the test outcome does not depend
  on it. Not a defect.

## 5. Verdict: GO WITH CONDITIONS

The amend closes every condition it was given. H1 is
fixed at its first step with a regression test in both
select modes (repro re-run by me, hole closed). H2 is
fixed with the guard in all four _restore_original
branches (call count traced by hand, test exercises the
real path). My C1 is closed with 5 real behavioral
phase-4 tests (all execute Runner.phase4, distinct
triggers, no string-only test among them). The prep file
doc items and the H3 wording correction landed as
specified. Suite 36/36, G0a 177/177, G0b pass, fixture
unchanged, 0 dashes, all on my own re-runs.

Condition, before the next live proof (small follow-up,
same file, same helper; code unchanged, no re-review of
this amend needed beyond verifying the follow-up commit):

- C1. Add behavioral tests for the 2 remaining phase-4
  branches, using the same _run_phase4 helper: (a) the
  active-window check raises when hypr returns an address
  other than the Zen address; (b) the final ok/completed
  gate raises when the envelope says ok False, when
  completed is 3, and when the log has a valid PROBE line
  but no dom_act line. Land a follow-up commit, re-run
  the suite + G0a + G0b. My probes prove the code already
  behaves correctly in all 4 sub-cases, so this is purely
  pinning tested behavior, not fixing code.

Live verification is still owed by design (code/unit
only here). The next proof is a fresh run number with a
fresh intent/message, copying the fixed run2.py, after
council + redteam review of this amend is done. The Muse
chat tab closed by run 2 attempt 2 is NOT reopened by
this amend.

## 6. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received ~20:40 +07, 22/11/2026. HEAD at review
  start bcc249c.
- Amend-2 log read in full 20:40 +07 (304 lines).
- Diff read in full 20:40 +07: e9994d9 (zen-tab.py, H1 +
  H2), d8f8ac3 (test file, 205 insertions), 16075f6 (prep
  file, recovery line + G1 note).
- 36 unit tests, re-run by me 20:41 +07: python3 -m
  unittest tests.test_zenproof2_fix, Ran 36 tests in
  0.009s, OK, exit 0.
- G0a, re-run by me 20:41 +07: python3 -m unittest
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec, Ran 177 tests in 12.442s, OK.
- G0b, validated by me 20:41 +07:
  code_exec.validate_program returns AST Module for both
  PROBE_PROGRAM and SEND_PROGRAM.
- Fixture sha, checked by me 20:41 +07: sha256sum
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6cbf,
  matches FIXTURE_SHA.
- Dash counts, checked by me 20:41 +07: U+2014 0, U+2013 0
  in all 4 changed files.
- Diff scope 20:40 +07: git diff --stat
  e9994d9^..bcc249c, 4 files, 570 insertions, 16
  deletions.
- Redteam H1 repro, re-run by me 20:41 +07: python3
  /tmp/redteam-amend-repro-h1.py, cmd_open REFUSED with
  'new tab returned an existing handle 855efa98;
  refusing to navigate or close', owner tab URL unchanged,
  deletions [].
- Own phase-4 probes, run by me 20:41 +07 (not in the
  suite): active-window-moved raises RuntimeError;
  envelope ok False raises 'send program did not complete
  4/4'; completed 3 raises the same; missing dom_act line
  raises the same.
- H2 call-count trace 20:41 +07: _handles GETs
  /window/handles (no list_tabs call), one _scan is
  exactly one list_tabs call, cmd_close calls _scan twice
  before _restore_original, so the fake's >= 3 threshold
  fires exactly inside _restore_original.
- `before` capture 20:41 +07: `before = _handles(z)` is
  set before POST /window/new in cmd_open; full handles
  compared to the full new_handle.
- Files changed by me (review only): improvements/
  w-zenproof2-amend2-council-2-review.md (new, this file).
  No amend file modified. No live run. No reviewer
  spawned.
