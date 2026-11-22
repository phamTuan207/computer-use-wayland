# Council 1 review: W-ZENPROOF2-AMEND3 (set-difference check + phase-4 tests)

Reviewer: Council 1, independent (not W-ZENPROOF2-AMEND3, not
W-ZENPROOF2-AMEND2, not W-ZENPROOF2-AMEND, not W-ZENPROOF2-FIX,
not W-ZENPROOF2, not COORD-CLICK-9). Report goes to Muse tong,
not directly to the owner. No amend modified, no live run, no
tab opened, navigated, or deleted in the owner's Zen. All
verification is code/unit level only, plus my own re-runs of
the unit and G0a suites and my own probes (written by me, in
/tmp/c1-amend3-probe.py). No em dash or en dash anywhere in
this file. No personal info.

## 0. Task and sources (20:52 +07, 22/11/2026)

- Task received ~20:52 +07. Branch todolist-push, repo
  ~/workspace/computer-use-wayland, HEAD 24050c1 at review
  start.
- Amend under review, 3 commits:
  - 09802c3 zen-tab.py: set-difference check after
    /window/new + handle-stability docstring.
  - 58df67d tests/test_zenproof2_fix.py: P-C regression test
    + 5 phase-4 tests, helper pins call order and program
    identity (42 tests).
  - 24050c1 improvements/w-zenproof2-amend3-log.md: amend log.
- Sources read before judging:
  - improvements/w-zenproof2-amend3-log.md (the amend log,
    260 lines, read in full).
  - Full diff of 09802c3 and 58df67d (read line by line, not
    skimmed).
  - The current zen-tab.py cmd_open in full (lines 180-380),
    including the handler and cmd_close.
  - improvements/c5-zenproof-runs/c5-zen-delegate-run2.py
    phase4 (lines 483-525), the real code the phase-4 tests
    pin.
  - improvements/w-zenproof2-log.md sections on run 1 and
    run 2 (lines 18, 31, 58, 99, 109, 160, 300-320, 455-475).
  - improvements/c5-zenproof-runs/run-1.json (outcome, error).
  - git show a355002:improvements/c5-zenproof-runs/zen-tab.py
    (the driver run 1 actually used).
  - The test file FakeSession, _owner_tabs, _run_cmd
    (lines 93-260).

## 1. Time log (wall-clock Asia/Ho_Chi_Minh)

- 20:52 +07, T+0m: task received, amend log + diff stat read.
- 20:52 +07, T+1m: full diff of 09802c3 and 58df67d read;
  cmd_open read in full.
- 20:53 +07, T+1m: 42 unit tests re-run by me, 42/42 OK;
  G0a 177/177 re-run by me; G0b both programs validated by
  me; fixture sha and dash counts checked by me.
- 20:53 +07, T+2m: my own probes written
  (/tmp/c1-amend3-probe.py), run against the amend-3 driver
  and against the amend-2 driver (302bc7d, checked out to
  /tmp/c1-amend2-zen-tab.py): P-C both select modes, both
  re-mint variants, happy-path control.
- 20:55 +07, T+3m: run-1 evidence checked (run-1.json,
  a355002 driver, w-zenproof2-log.md): docstring citation
  found false, see section 3.
- 20:56 +07, T+4m: phase4 real code cross-checked against
  the 5 new tests; residual window traced; review written,
  committing.

## 2. What I verified, with evidence

### 2.1 Diff scope is exactly the amend, nothing else

- git diff --stat 09802c3^..24050c1: 3 files, 432 insertions,
  13 deletions. Only zen-tab.py (+40/-4), the test file, and
  the amend log (260 lines, new). run2.py was NOT changed by
  this amend (the phase-4 tests execute its existing code).
  No other file touched by these commits. The pre-existing
  dirty tests/realistic/clone1-batch3/results.json and the
  untracked prompt files from other lanes are not in these
  commits.
- 0 em dash (U+2014) and 0 en dash (U+2013) in all 3 files,
  counted by me with Python. Fixture untouched: sha256 of
  tests/two_vision_fixture.html is
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6
  cbf, identical to FIXTURE_SHA.

### 2.2 The 42 tests and G0a/G0b pass on my own runs

- Command: python3 -m unittest tests.test_zenproof2_fix.
  Output: Ran 42 tests in 0.008s, OK. Exit 0. I ran it
  myself, not trusting the log's 42/42.
- G0a: python3 -m unittest tests.test_zen_pointer
  tests.test_p2_element_ref tests.test_code_exec. Ran 177
  tests in 12.511s, OK. Exit 0. Re-run by me.
- G0b: code_exec.validate_program (scripts/code_exec.py
  line 588) on run2.PROBE_PROGRAM and run2.SEND_PROGRAM,
  loaded by me from c5-zen-delegate-run2.py: both return an
  ast.Module, no exception. Re-run by me. (My first attempt
  used the wrong import path and failed with ImportError;
  the correct module is scripts/code_exec, not
  tests.test_code_exec.)
- The 6 new tests are real: 1 P-C regression test and 5
  phase-4 tests. The 36 old tests still pass unchanged.

### 2.3 The set-difference check really catches P-C (my own probes, both directions)

I wrote my own probe (/tmp/c1-amend3-probe.py, scenario
code written by me, not copied from the worker's probe or
the suite test). It reuses the suite's FakeSession harness
only, which I read and verified models POST /window/new,
select, /url, DELETE, and list_tabs faithfully. The
scenario: X opens after `before` AND the example tab closes
in the /window/new window, /window/new returns X's handle,
current set to the about:blank handle; after cmd_open, the
runner cleanup close by URL is modeled too. Results:

- Amend-3 driver, select_new=True: cmd_open REFUSED with
  'new tab handle set changed unexpectedly (added 2,
  removed 1); refusing to navigate or close'. Deletions [],
  tabs [owner Muse, X https://x.example/, about:blank],
  owner intact.
- Amend-3 driver, select_new=False: identical refusal
  (added 2, removed 1), 0 deletions. The check fires before
  the (c) check, so the select mode does not matter; both
  modes are covered by experiment, not just by reasoning.
- Amend-2 driver (302bc7d, same scenario): cmd_open
  RETURNED ok with selected_by 'explicit-select' (the (c)
  check selected X, believing it was the new tab), and the
  cleanup close DELETEd the fixture URL, which was X's tab
  (x_intact False). Tabs left: owner Muse + about:blank.
  The full P-C hijack reproduces on amend-2 code and is
  blocked on amend-3 code. This matches the worker's
  baseline claim exactly, verified independently.
- Happy-path control: cmd_open ok ('window/new'), 0
  deletions, on both drivers. No regression.

### 2.4 The set-difference check also catches handle re-minting (the claimed side effect)

The log claims the check "independently closes" the
within-session re-mint case (Redteam P-A). The fake does
not model re-minting, so no P-A test was added. I modeled
it myself with two probe variants on the amend-3 driver:

- Owner re-mint: /window/new replaces the owner tab's
  handle with a fresh uuid (URL unchanged) and returns the
  new tab's real handle. Amend-3: REFUSED 'handle set
  (added 2, removed 1)', 0 deletions. Amend-2 (same
  scenario): cmd_open returned ok ('window/new'), 0
  deletions, no damage, but it proceeded on a handle set
  that no longer matches `before`. So the set-difference
  check is what catches this case, and it catches it
  before any select or navigate.
- New-tab re-mint: /window/new appends the new tab, then
  re-mints its handle and returns the stale one.
  Amend-3: REFUSED 'handle set (added 1, removed 0)'.
  Amend-2: REFUSED 'new tab was not made current', at the
  (c) check, later. Amend-3 catches it earlier, at the
  set-difference check.
- The side effect is real and verified by experiment, not
  just by the log's logic. Note G1: a re-mint in a healthy
  session now refuses a run that would otherwise succeed
  (the amend-2 owner re-mint opened ok). That is the
  intended fail-closed cost, and the docstring says so;
  it is unmeasured either way, because no live run has
  exercised the fixed driver's open sequence yet.

### 2.5 Membership check and count gate are intact as defense in depth

- Read cmd_open in full. Order: membership check
  (`if new_handle in before`, distinct message 'new tab
  returned an existing handle'), then count gate
  (`count_after_new != len(before) + 1`, distinct message),
  then set-difference check (distinct message 'new tab
  handle set changed unexpectedly'). All three run before
  the (c) check and before any navigate or DELETE.
- The count gate and the set-difference check share one
  fetch (`handles_after_new` from `_handles(z)`; the count
  is derived from the same list), so they cannot disagree
  with each other. Good construction, no TOCTOU between
  them.
- The baseline is `before` (captured at cmd_open start),
  not the pre-check scan's handle list. That is the right
  choice, and the log's reasoning for it is correct: a
  concurrent change between `before` and the scan is
  already in the scan, so diffing against the scan would
  miss it; diffing against `before` catches every ordering.
  I traced the orderings: churn before the scan, churn
  between scan and /window/new, churn inside /window/new,
  all refuse at the set-difference check.
- Honest note: for refusal outcome, the membership and
  count checks are logically subsumed by the set-difference
  check (any case they refuse, the set-difference check
  would refuse too, because added != {new_handle} or
  removed is non-empty). Their value is as early exits with
  clearer diagnostics, which is what the log claims
  ("they diagnose their own cases most clearly"). That is
  genuine defense in depth, not a redundant gate.
- The error message reports counts only (added %d,
  removed %d), no handle values. Good.

### 2.6 The 5 phase-4 tests pin real behavior (cross-checked against run2.py)

- Read run2.py phase4 (lines 483-525). The active-window
  check IS the first line, then tab('switch', TARGET),
  then oneshot_zen(SEND_PROGRAM, INTENT), then the PROBE
  snapshot gate, then the final ok/completed gate. So the
  active-window test's claim holds: the message alone
  proves no switch or send ran, because nothing precedes
  that check.
- The identity test asserts the call kinds are exactly
  ['tab', 'oneshot'] in that order, the tab call args are
  ('switch', TARGET), the oneshot program IS SEND_PROGRAM
  (identity, not equality), and the intent is INTENT. A
  future edit reordering the calls or passing the wrong
  program fails this test. The helper records calls on
  runner._phase4_calls; the 5 existing phase-4 tests run
  unchanged through the new helper (defaults ok=True,
  hypr_address='0xABC'), confirmed by the green suite.
- The 4 gate tests (active-window moved, envelope ok
  False, completed 3, missing dom_act) each raise
  RuntimeError 'send program did not complete 4/4' or
  'active window moved off Zen before send', as asserted.
  The final ok/completed gate is now executed by tests:
  a failed send can no longer be recorded as success
  without a test failing first. Council 2 C1 and Redteam
  H3/C2 are both closed.

### 2.7 The wording correction is done right

- The amend-2 log section 4 claim "a concurrent tab
  change causes a spurious fail-closed refusal, never a
  wrong navigate" was overstated, as the P-C repro proves
  (my probe reproduces the wrong navigate + DELETE on
  amend-2 code). The amend-3 log corrects it in its own
  section 2 and does NOT edit the amend-2 log (a committed
  historical record). Correct handling.
- The phrase "never a wrong navigate" no longer appears as
  a claim in zen-tab.py or the test file (grep: 0 matches
  in both). Its 3 occurrences in the amend-3 log are the
  Redteam C1 citation, the quoted amend-2 claim being
  corrected, and the cmd_close post-DELETE site, where the
  statement is justified in context (the raise happens
  after a correct DELETE, so it cannot cause a wrong
  navigate or DELETE there).
- The residual statement is honest: WebDriver offers no
  atomic verify-and-navigate; the set-difference check
  cannot catch a change after its own fetch; the F1
  post-navigate check then catches that as refusal, no
  DELETE. I traced the remaining window: a post-fetch churn
  that leaves current == new_handle and does not touch the
  new tab is harmless (unrelated tabs opening/closing);
  any churn that changes current or the new tab's handle is
  caught by the (c) check or the F1 post-navigate check as
  refusal. The residual is genuinely narrow.

### 2.8 The P-C suite test is faithful

- Read the test (test_open_refuses_concurrent_open_close_
  with_stale_handle). The fake override appends X, deletes
  tabs[1], appends about:blank, returns X's handle, sets
  current to the about:blank handle when select_new. With
  _owner_tabs() = [owner Muse, example], tabs[1] is the
  example tab, so the churn is exactly the P-C scenario.
  It asserts the 'handle set' raise, 0 deletions, 3 tabs,
  owner URL unchanged, X URL unchanged, new tab left as
  about:blank. All true, and my independent probe
  reproduces the same outcome plus the amend-2 damage.

## 3. Finding: the docstring falsely cites run 1 as support (condition C1)

The new module docstring paragraph (09802c3) says:

"The membership, count, and set-difference checks in
cmd_open assume handles are stable within one cmd_open
invocation: run 1 supports this (handles were consistent
across before, scan, /window/new, the (c) check, navigate,
and the post-navigate check within one invocation); run
2's ephemerality was cross-session (two lists a minute
apart, separate processes)."

The second half is true (w-zenproof2-log.md: list A and B
one minute apart, 15 of 15 comparable URLs with different
handles; each list is its own session). The first half is
false, and I verified it three ways:

- run-1.json: outcome 'error', error "active window is
  not Zen (0x56307e202df0); aborting", wall_ms 3473.8,
  cleanup skipped. Run 1 aborted in phase 1 and never
  reached phase 2. It never ran /window/new, never opened
  a tab. w-zenproof2-log.md line 109 states it plainly:
  "run 1 never reached phase 2".
- The driver run 1 used (a355002, read by me): its
  cmd_open had no scan, no (c) check, and no post-navigate
  check. It did before, current_before, title_before, POST
  /window/new, then an immediate POST /url navigate. So
  run 1 could not have demonstrated consistency "across
  the (c) check and the post-navigate check", because those
  checks did not exist yet.
- No live run has exercised the fixed driver's open
  sequence at all (live verification is still owed, as the
  amend log itself states in section 4). So within-
  invocation handle stability has NO live evidence yet,
  from any run.

The assumption itself is reasonable, and the design is
fail-closed if it breaks (the set-difference check
refuses, as my re-mint probes prove). The defect is only
the false evidence citation in the procedure source. But
this campaign's original incident came from exactly this
class of error: a wrong premise written into the procedure
source (the title premise in the prep file). A docstring
that invents run-1 support for a load-bearing assumption
must not stand.

Condition C1 (doc-only, before the next live proof):
rewrite the paragraph to state the assumption honestly,
for example: the checks assume handles are stable within
one cmd_open invocation; this is unproven by live
evidence (run 1 aborted in phase 1 before any open, and
no live run has exercised the fixed driver's open
sequence); if a handle were re-minted mid-invocation, the
set-difference check refuses fail-closed. Keep the true
run-2 cross-session sentence. Do not cite run 1.

## 4. Minor observations (not blockers)

- G1: re-mint fail-closed cost (section 2.4). A re-mint in
  a healthy session now refuses a run that would otherwise
  succeed. Intended, documented, unmeasured. Not a defect.
- G2: the residual window after the set-difference fetch
  is covered by the F1 post-navigate check as refusal
  (section 2.7). No test models a churn in that window,
  but the only harmful churn there changes current or the
  new handle, which the (c) and F1 checks catch. No test
  gap worth a condition.
- G3: the P-C suite test uses select_new=True only. My
  probes show select_new=False refuses identically, because
  the set-difference check fires before the mode-dependent
  (c) check. One mode suffices; no second test needed.
- G4: cmd_close's post-DELETE verification reads can
  still raise after a successful DELETE and mask the close
  success (amend-3 log section 4, follow-up candidate,
  pre-existing from amend 1). Consequence is a spurious
  error, fail-closed, never a wrong navigate or DELETE.
  Not a live-run gate, as the log states.

## 5. Verdict: GO WITH CONDITIONS

The amend is correct and complete for its scope. The
set-difference check catches the P-C concurrent
open+close+stale-handle case (proven both directions by
my own probes), it also catches within-session handle
re-minting (proven by my own probes), the membership
check and count gate stand intact as defense in depth
with distinct diagnostics, the 5 phase-4 tests pin real
behavior in the real runner code, the wording correction
is done right, and the residual is stated honestly. The
42-test suite, G0a, and G0b all pass on my own runs.

Conditions, to be satisfied before the next live proof
(not before landing this amend):

- C1. Correct the docstring's handle-stability paragraph
  (section 3): remove the false run-1 citation and state
  the assumption as unproven by live evidence, with the
  fail-closed consequence. A one-paragraph doc edit; no
  code change, no re-review needed for this item alone.

The Muse chat tab closed by run 2 attempt 2 is NOT
reopened by this amend. Recovery stays the coordinator's
decision, as the amend log states.

## 6. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received ~20:52 +07, 22/11/2026. HEAD at review
  start 24050c1.
- Diff scope 20:52 +07: git diff --stat 09802c3^..24050c1,
  3 files, 432 insertions, 13 deletions.
- 42 unit tests, re-run by me 20:53 +07: python3 -m
  unittest tests.test_zenproof2_fix, Ran 42 tests in
  0.008s, OK, exit 0.
- G0a, re-run by me 20:53 +07: python3 -m unittest
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec, Ran 177 tests in 12.511s, OK.
- G0b, re-run by me 20:53 +07: scripts/code_exec.
  validate_program on run2.PROBE_PROGRAM and
  run2.SEND_PROGRAM, both return ast.Module, no exception.
- Fixture sha, checked by me 20:53 +07: sha256sum
  tests/two_vision_fixture.html =
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6
  cbf, matches FIXTURE_SHA.
- Dash counts, counted by me 20:53 +07: U+2014 0, U+2013 0
  in zen-tab.py, the test file, and the amend log.
- My probes 20:53 +07: python3 /tmp/c1-amend3-probe.py
  <driver> <scenario>. Amend-3 P-C (both modes): REFUSED
  'handle set (added 2, removed 1)', 0 deletions. Amend-2
  P-C (both modes): cmd_open ok 'explicit-select', cleanup
  close deleted the fixture URL, X gone (x_intact False).
  Amend-3 re-mint owner: REFUSED 'handle set (added 2,
  removed 1)'. Amend-3 re-mint new tab: REFUSED 'handle
  set (added 1, removed 0)'. Amend-2 re-mint owner: ok.
  Amend-2 re-mint new tab: REFUSED 'not made current'.
  Happy path: ok on both drivers.
- Baseline driver 20:53 +07: git show
  302bc7d:improvements/c5-zenproof-runs/zen-tab.py >
  /tmp/c1-amend2-zen-tab.py; grep set-difference 0 matches.
- Run-1 evidence 20:55 +07: run-1.json outcome 'error',
  "active window is not Zen (0x56307e202df0); aborting",
  wall_ms 3473.8, cleanup skipped; w-zenproof2-log.md
  line 109 "run 1 never reached phase 2"; a355002 cmd_open
  has no scan, no (c) check, no post-navigate check.
- Run-2 ephemerality 20:55 +07: w-zenproof2-log.md lines
  308 and 464, 15 of 15 comparable URLs with different
  handles between list A and B one minute apart.
- Phase4 real code 20:56 +07: run2.py lines 483-525 read;
  active-window check is the first line, then switch,
  then oneshot_zen(SEND_PROGRAM, INTENT), then PROBE gate,
  then final ok/completed gate.
- Files changed by me (review only): improvements/
  w-zenproof2-amend3-council-1-review.md (new, this file).
  My probe lives at /tmp/c1-amend3-probe.py (not committed,
  scratch). No amend file modified. No live run. No
  reviewer spawned.
