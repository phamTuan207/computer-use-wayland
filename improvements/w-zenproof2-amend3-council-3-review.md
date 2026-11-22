# Council 3 review: W-ZENPROOF2-AMEND3 (set-difference check + handle-stability docstring + phase-4 tests)

Reviewer: Council 3, independent (not W-ZENPROOF2-AMEND3, not
W-ZENPROOF2-AMEND2, not W-ZENPROOF2-AMEND, not W-ZENPROOF2-FIX,
not W-ZENPROOF2, not COORD-CLICK-9). Report goes to Muse tong,
not directly to the owner. No amend modified, no live run, no tab
opened, navigated, or deleted in the owner's Zen. All verification
is code/unit level only, plus my own re-runs of the unit and G0a
suites and my own re-runs of the baseline probe in both directions.
No em dash or en dash anywhere in this file. No personal info.

## 0. Task and sources (20:52 +07, 22/11/2026)

- Task received ~20:52 +07. Branch todolist-push, repo
  ~/workspace/computer-use-wayland. HEAD at review start 86d6f89
  (Council 2's amend-3 review, already pushed); the 3 amend
  commits under review are 09802c3, 58df67d, 24050c1.
- Amend under review, 3 commits:
  - 09802c3 zen-tab.py: set-difference check + handle-stability
    docstring (40 insertions, 4 deletions).
  - 58df67d tests/test_zenproof2_fix.py: P-C regression test + 5
    phase-4 tests + helper pins call order and program identity
    (132 insertions, 9 deletions).
  - 24050c1 improvements/w-zenproof2-amend3-log.md: amend log
    (new, 260 lines).
- Sources read before judging:
  - improvements/w-zenproof2-amend3-log.md (the amend log, read
    in full).
  - Full diff of 09802c3 and 58df67d (read line by line, not
    skimmed), the current zen-tab.py module docstring and
    cmd_open, and run2.py phase4 lines 483-525.
  - improvements/w-zenproof2-amend2-redteam-review.md sections
    P-C, H2, H3, G4 (the conditions this amend closes).
  - improvements/w-zenproof2-amend2-log.md section 4 (the
    overstated claim being corrected).
  - improvements/w-zenproof2-log.md sections 0, 1, 6 and evidence
    appendix (run 1 abort, run 2 attempt 1 and 2, 15/15 handle
    ephemerality).
  - Pre-fix cmd_open at a355002 (what run 1 and run 2 attempt 2
    actually ran).
  - /tmp/redteam-amend2-probes.py (P-C, P-D, P-E, read in full)
    and /tmp/amend3-baseline-probe.py (read in full, re-run by
    me in both directions).

## 1. Time log (wall-clock Asia/Ho_Chi_Minh)

- 20:52 +07, T+0m: task received, amend log + diffs read.
- 20:53 +07, T+1m: 42 unit tests re-run by me, 42/42 OK; G0a
  177/177 re-run by me, OK; G0b both programs validate OK;
  fixture sha checked; dash counts checked.
- 20:54 +07, T+2m: P-C test run against amend-2 code in a temp
  worktree (fails, as it must); 5 new phase-4 tests run against
  amend-2 code (pass, as the log says); baseline probe re-run
  by me on amend-2 code and on amend-3 code.
- 20:55 +07, T+3m: docstring and log wording checked against
  the run-2 log and the pre-fix driver; the run-1 attribution
  found false (section 2).
- 20:56 +07, T+4m: cmd_close residual checked against code
  and the P-E probe; residual list checked; review written.
- 20:57 +07, T+5m: committing.

## 2. What I verified, with evidence

### 2.1 Diff scope is exactly the amend, nothing else

- The 3 amend commits touch exactly 3 files: zen-tab.py,
  test_zenproof2_fix.py, and the amend log. No other file.
  (The wider range 302bc7d..24050c1 also shows
  scripts/overlay.py, scripts/s2_flip_live.py and their tests;
  those belong to the pill lane commit 14cf4dc, not this
  amend.)
- 0 em dash (U+2014) and 0 en dash (U+2013) in all 3 files,
  counted by me. Fixture untouched (sha256
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6
  cbf, matches FIXTURE_SHA).

### 2.2 The 42 tests pass on my own run, and the P-C test is a genuine regression test

- Command: python3 -m unittest tests.test_zenproof2_fix.
  Output: Ran 42 tests in 0.008s, OK. Exit 0. I ran it
  myself, not trusting the log's 42/42.
- G0a, re-run by me: python3 -m unittest
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec. Ran 177 tests in 13.782s, OK.
- G0b, re-run by me: code_exec.validate_program passes for
  PROBE_PROGRAM and SEND_PROGRAM.
- The P-C test pins the new check, proven by the baseline:
  I copied the new test file into a temp worktree at
  302bc7d (amend-2 code, worktree removed afterwards) and
  ran the P-C test there: FAILED, "_FakeZenDomError not
  raised". On amend-3 code the same test passes. A test
  that fails on the old code and passes on the new code is
  a genuine regression test.
- The 5 new phase-4 tests pass on amend-2 code too (Ran 5,
  OK in the same worktree). That is expected and the log
  is honest about it: run2.py was NOT changed by this
  amend, and Council 2's probes already proved the code
  behaves correctly; these tests pin that behavior in the
  suite. They are pins, not fixes.

### 2.3 The P-C baseline damage is real, and the fix closes it

- I re-ran the worker's baseline probe
  (/tmp/amend3-baseline-probe.py) in both directions:
  - On amend-2 code (ROOT pointed at the temp worktree):
    cmd_open RETURNED ok, tabs[1] (X) now carried the
    fixture URL (hijacked True), cleanup close ok True, X
    deleted True, tabs left [owner Muse tab, about:blank].
    Exactly the damage the log's baseline section records.
  - On amend-3 code: cmd_open REFUSED with 'new tab handle
    set changed unexpectedly (added 2, removed 1)',
    deletions [], owner intact, X intact, tabs [owner, X,
    about:blank]. Exactly the log's re-run section.
- The worker's claim about the redteam P-C probe is also
  true, verified in the fake: the base FakeSession POST
  /url handler rewrites the tab title to 'Two-vision
  benchmark fixture' when the URL contains the fixture
  substring. The redteam probe looks X up by title 'X'
  after cmd_open, so after the hijack it finds nothing
  (x_url []), hijacked False, and misses the damage. The
  worker's position-based check (tabs[1]) and the suite
  test (which asserts by position) are the correct fix
  for the probe, not just a different style.

### 2.4 The set-difference check is implemented as the log describes

- `before = _handles(z)` is the first line of cmd_open's
  session block, captured at cmd_open start. The
  set-difference check diffs against `before`, not against
  the pre-check scan's handle list. The log's reasoning
  for that choice is correct: a concurrent change between
  `before` and the scan is already in the scan, so a
  difference against the scan would miss it; against
  `before`, every ordering is caught.
- Order in code: membership check (new_handle in before),
  count gate (+1), set-difference check (added ==
  {new_handle} and removed empty), (c) check, navigate,
  F1 post-navigate re-verify. The membership check and the
  count gate are kept with distinct error messages, as the
  log says.
- The re-mint closure claim is true at the code level: a
  re-minted owner handle changes the set by one added and
  one removed, so added != {new_handle} or removed
  non-empty, and the check refuses. The fake does not
  model re-minting (Redteam G4), so no P-A test exists;
  the log states that honestly instead of claiming a
  test covers it.

### 2.5 The docstring states the set-difference requirement correctly

- The open-checks paragraph now names the set-difference
  requirement next to the count +1 and membership
  requirements: "the handle set after the open must differ
  from before by exactly the new handle added and nothing
  removed". That matches the code exactly. The assumption
  paragraph correctly states the fail-closed property:
  "If a handle were re-minted mid-invocation, the
  set-difference check refuses fail-closed." Both are
  correct. The error is only in the EVIDENCE cited for
  the assumption, see section 3.

### 2.6 The phase-4 tests pin what the log says they pin

- The active-window test asserts only the RuntimeError
  message, and that is sufficient: I read run2.py
  phase4, and the active-window check is the first lines
  of phase4 (hypr activewindow, raise 'active window
  moved off Zen before send'), before the switch and the
  send. The message alone proves nothing after it ran.
- The final gate tests cover ok False, completed 3, and
  missing dom_act (completed None), all raising 'did not
  complete 4/4'. The gate code reads `if
  envelope.get('ok') is not True or completed != 4`, so
  all three paths raise at the same gate.
- The identity test asserts the call kinds are exactly
  ['tab', 'oneshot'], the tab call args are ('switch',
  TARGET), the oneshot program IS SEND_PROGRAM
  (identity, not equality), and the intent is INTENT.
  The helper records calls on runner._phase4_calls. The
  5 older phase-4 tests run unchanged through the new
  helper (they pass in the 42/42 run).

### 2.7 The log wording correction is honest and correctly placed

- The amend-2 log section 4 claim was, verbatim:
  "a concurrent tab change causes a spurious fail-closed
  refusal, never a wrong navigate". I read it at line 252
  of improvements/w-zenproof2-amend2-log.md. The P-C
  repro proves it overstated: a concurrent open plus
  close plus a stale-handle return caused a wrong
  navigate (X hijacked) and then a wrong DELETE (X
  deleted by cleanup), as my own baseline re-run shows.
- The amend-3 log corrects it in its own section 2 and
  does NOT edit the amend-2 log. That is the right
  treatment: the amend-2 log is a committed historical
  record. The correction sentence is honest: "the
  set-difference check narrows the residual further, but
  WebDriver offers no atomic verify-and-navigate, so a
  concurrent change plus a stale return remains a
  (narrower) residual, not an eliminated one."
- The amend-3 log section 2 also states the remaining
  hole correctly: the check "cannot catch a change that
  happens after the set-difference fetch and before the
  navigate, which the post-navigate F1 check then catches
  (refusal, no DELETE)". The F1 check compares current
  against new_handle after the navigate, so a current-tab
  change in that window is caught as a refusal with no
  DELETE. True.

### 2.8 The residuals in log section 4 are honest and complete

- "WebDriver offers no atomic verify-and-navigate" and
  "the set-difference check ... cannot catch a change
  after its own fetch": true, and the F1 check is the
  stated backstop. "Backend first-match stays a known
  limitation": true, I read _resolve_target in
  zen_backend.py lines 189-208 in the fix review; it
  returns the first match and does not refuse on
  duplicates. "Unreadable tabs stay invisible to URL
  identity": true, _find_in_scan skips entries with no
  URL.
- The "not closed here" item is real and described
  accurately: in cmd_close, after a successful DELETE,
  `after = _handles(z)` and `_scan(z)` run unguarded, so
  a read failure there raises and masks the close
  success. I verified it in the code and in the redteam
  P-E probe (/tmp/redteam-amend2-probes.py): a scan
  failing after DELETE makes cmd_close RAISE while the
  scratch tab is actually gone. The stated consequence
  is correct: a spurious error (fail-closed), never a
  wrong navigate or DELETE, because no further navigate
  or DELETE follows the raise inside cmd_close.
- The section 4 reference "limitations recorded in the
  amend 1 log section 4 and the amend 2 log section 4
  still hold" is true for the limitations themselves.
  See G4 for the one wrinkle (the corrected wording).

## 3. The finding: the run-1 evidence citation is false (F1)

- The docstring's assumption paragraph says: "run 1
  supports this (handles were consistent across before,
  scan, /window/new, the (c) check, navigate, and the
  post-navigate check within one invocation)". That
  sentence is false, and the amend-3 log section 2
  repeats it verbatim. Three independent facts prove it:
  - (a) Run 1 never ran cmd_open at all. The run-2 log
    section 0 records run 1 aborted in phase 1 because
    the active window was mochi Chromium on ws2, and
    section 1 states it plainly: "run 1 never reached
    phase 2 (it aborted at the activewindow gate), so
    the driver was never on the laptop." A run that
    never opened a tab cannot support any claim about
    handle consistency across an open sequence.
  - (b) The checks named in the parenthetical did not
    exist in run 1's driver. I read the pre-fix cmd_open
    at a355002: it fetches `before`, posts /window/new,
    then navigates directly, then checks the title. It
    has no scan (_scan), no (c) check, and no
    post-navigate (F1) check. The (c) check and the scan
    were added by the fix (6d751b9); the F1
    post-navigate check was added by amend 1. Run 1
    could not have "passed" checks that did not exist.
  - (c) No live invocation has ever run the fixed
    driver's cmd_open. Live runs stopped after the
    20:06 incident; the G-PILL retry and ZT-B never ran.
    The only executions of the (c) check, the count
    gate, the membership check, the set-difference
    check, and the post-navigate check are unit tests
    against FakeSession, which models handles as stable
    by construction and therefore cannot evidence
    real-world stability.
- What IS true, and what the sentence should say:
  run 2's ephemerality was cross-session (two lists one
  minute apart, separate processes, 15 of 15 comparable
  URLs with different handles; run-2 log section 6 and
  evidence appendix), and Gecko handles are per-window
  UUIDs. That is indirect support for the assumption,
  not proof of it. Within-invocation stability is an
  UNTESTED assumption, and the safety net is the
  fail-closed refusal, which IS tested.
- How this happened: the sentence comes from the
  redteam amend-2 review H2, which states the same
  run-1 claim. The amend-3 worker copied it into the
  docstring faithfully, as Redteam C3 instructed ("record
  the assumption explicitly ... run 1 supports this").
  The worker followed the brief; the error is in the
  source claim, not in the worker's compliance. My
  condition corrects the record, it does not blame the
  worker.
- Why this matters enough to be a condition: the
  docstring is the live procedure record the next live
  proof's coordinator will read. A false "run 1
  supports this" turns an untested assumption into a
  cited fact. If the coordinator believes handle
  stability is proven, they may treat a re-mint refusal
  as a surprise rather than as the designed fail-closed
  path. The code is safe either way, but the record
  must be honest, and this campaign corrects
  overstated claims as a matter of standard (this
  amend itself exists to correct one).

## 4. Minor observations (not blockers)

- G1: log section 4 says "(the F1 residual race is
  narrowed, not eliminated; the set-difference check
  narrows the concurrent-churn case further ...)".
  Strictly, amend 3 does not narrow the F1 race itself
  (the TOCTOU between the (c) check and the navigate);
  it narrows the concurrent-churn case. The F1 race was
  narrowed by amend 1's post-navigate check. The second
  clause of the same sentence says the right thing, so
  a reader gets the correct picture; the first clause is
  loose, not wrong in substance. Record the precise
  wording in the follow-up log.
- G2: log section 4 dates the cmd_close residual as
  "pre-existing from amend 1". The post-DELETE scan
  ("scratch tab still listed after close") dates from
  the original run kit (2d1dc82) and is present in the
  fix (6d751b9), so it predates amend 1. The operative
  point (it predates amend 2 and 3 and was not
  introduced by them) is true; only the origin label is
  off by one generation. Record the precise origin in
  the follow-up log.
- G3: the test-file module docstring bullet says the
  handle set must differ "by more than exactly the new
  handle added". The check also refuses when the added
  set is a different singleton or empty (added !=
  {new_handle}), not only when it is larger. Loose
  wording in a docstring bullet, not a code error.
- G4: section 4's reference "limitations recorded in
  the amend 2 log section 4 still hold" sits next to
  the section 2 correction of that same section's
  "never a wrong navigate" wording. The limitations
  themselves still hold and the correction is explicit
  in section 2, so there is no contradiction, but a
  reader could trip on it. The follow-up log should
  state once that the reference excepts the corrected
  wording.

## 5. Verdict: GO WITH CONDITIONS

The code is correct and the tests are genuine. The P-C
check closes the concurrent open-plus-close hole, proven
in both directions by my own re-runs. The phase-4 tests
pin behavior the code already had. The log wording
correction is honest and correctly placed. The residuals
are honest and complete. The single defect is the false
run-1 evidence citation in the docstring (and repeated
in the amend-3 log section 2), in the exact area this
review was asked to verify.

Conditions, to be closed before the next live proof:

- C1 (mandatory, doc-only): correct the docstring's
  handle-stability paragraph. Remove the false
  attribution "run 1 supports this (handles were
  consistent across before, scan, /window/new, the (c)
  check, navigate, and the post-navigate check within
  one invocation)". Replace it with the honest
  statement: no live invocation has yet run these
  checks (they were added after the last live run,
  attempt 2; run 1 aborted in phase 1 and never ran
  cmd_open); the only support is indirect (run 2's
  ephemerality was cross-session, two lists a minute
  apart, separate processes; Gecko handles are
  per-window UUIDs); if a handle were re-minted
  mid-invocation, the set-difference check refuses
  fail-closed. Record the correction with its evidence
  (run-2 log sections 0, 1, 6; pre-fix cmd_open at
  a355002) in the follow-up worker's log. Do NOT
  silently edit the amend-3 log: leave it as committed
  history, exactly as amend 3 did for the amend-2 log.
  No re-review needed for this doc fix; a follow-up
  commit plus the correction in its log is enough.

The Muse chat tab closed by run 2 attempt 2 is NOT
reopened by this amend. Recovery stays the
coordinator's decision, as the amend log states.

## 6. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received ~20:52 +07, 22/11/2026. Branch
  todolist-push. HEAD at review start 86d6f89 (Council
  2's amend-3 review, already pushed). Amend commits
  09802c3, 58df67d, 24050c1, all on origin (HEAD equals
  origin/todolist-push, ls-remote verified 86d6f89).
- 42 unit tests, re-run by me 20:53 +07: python3 -m
  unittest tests.test_zenproof2_fix, Ran 42 tests in
  0.008s, OK, exit 0.
- G0a, re-run by me 20:53 +07: Ran 177 tests in
  13.782s, OK. G0b, re-run by me 20:53 +07:
  code_exec.validate_program passes for PROBE_PROGRAM
  and SEND_PROGRAM.
- Fixture sha, checked by me 20:53 +07:
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6
  cbf, matches FIXTURE_SHA. Em dash 0, en dash 0 in all
  3 amend files, counted by me.
- P-C test on amend-2 code, run by me 20:54 +07 in a
  temp worktree at 302bc7d (test file copied in):
  FAILED, "_FakeZenDomError not raised". On amend-3
  code the same test passes. Worktree removed
  afterwards.
- 5 new phase-4 tests on amend-2 code, run by me
  20:54 +07 in the same worktree: Ran 5, OK.
- Baseline probe, re-run by me 20:54 +07 in both
  directions: on amend-2 code, cmd_open RETURNED ok,
  tabs[1] now the fixture URL, hijacked True, cleanup
  close ok True, X deleted True, tabs left [owner Muse
  tab, about:blank]; on amend-3 code, cmd_open REFUSED
  'new tab handle set changed unexpectedly (added 2,
  removed 1)', deletions [], owner intact, X intact,
  tabs [owner, X, about:blank].
- Fake POST /url handler, read by me 20:54 +07: it
  rewrites the current tab title to 'Two-vision
  benchmark fixture' on navigate, so the redteam P-C
  probe's lookup by title 'X' finds nothing and misses
  the hijack, as the amend log claims.
- Amend-2 log claim, read by me 20:55 +07 at line 252:
  "a concurrent tab change causes a spurious
  fail-closed refusal, never a wrong navigate".
- Run 1 abort, read by me 20:55 +07 in
  w-zenproof2-log.md sections 0 and 1: run 1 aborted
  in phase 1 (active window was mochi), "run 1 never
  reached phase 2 (it aborted at the activewindow
  gate), so the driver was never on the laptop."
- Pre-fix cmd_open, read by me 20:55 +07 at a355002:
  fetches `before`, posts /window/new, navigates
  directly, checks title. No scan, no (c) check, no
  post-navigate check.
- 15/15 ephemerality, read by me 20:55 +07 in
  w-zenproof2-log.md section 6: two lists one minute
  apart (list A and B, 20:04 +07), both count 18,
  identical URL sets, 15 of 15 comparable URLs with
  different handles.
- cmd_close post-DELETE reads, read by me 20:56 +07:
  after DELETE, `after = _handles(z)` and `_scan(z)`
  run unguarded; the P-E probe in
  /tmp/redteam-amend2-probes.py makes cmd_close RAISE
  while the scratch tab is actually gone. The
  "scratch tab still listed after close" check dates
  from 2d1dc82 (original run kit).
- Diff scope, checked by me 20:57 +07: the 3 amend
  commits touch exactly 3 files (zen-tab.py +40/-4,
  test file +132/-9, amend log new 260 lines). The
  other files in the range 302bc7d..24050c1 belong to
  the pill lane commit 14cf4dc.
- Files changed by me (review only):
  improvements/w-zenproof2-amend3-council-3-review.md
  (new, this file). No amend file modified. No live
  run. No reviewer spawned.
