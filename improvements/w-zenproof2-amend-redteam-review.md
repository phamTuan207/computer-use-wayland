# Redteam review: W-ZENPROOF2-AMEND (close the fix-review conditions)

Reviewer: Redteam, independent (not W-ZENPROOF2-AMEND, not
W-ZENPROOF2-FIX, not W-ZENPROOF2, not COORD-CLICK-9). Report goes
to Muse tong, not directly to the owner. No amend file modified,
no live run, no tab opened, navigated, or deleted in the owner's
Zen. All verification is code/unit level only, plus my own
repro scripts in /tmp. No em dash or en dash anywhere in this
file. No personal info.

## 0. Task and sources (20:31 +07, 22/11/2026)

- Task received ~20:31 +07. Branch todolist-push, repo
  ~/workspace/computer-use-wayland, HEAD at review start
  b956176 (the amend log commit), equal to origin/todolist-push
  after fetch. The 3 council reviews of this amend had already
  landed (7c6e80d Council 1, ddea95a Council 2, 4f8825d
  Council 3); I read all three before judging, to converge
  rather than duplicate. Where a finding is theirs, I say so
  and adopt it; the findings below marked MINE are new.
- Amend under review, 5 commits:
  - b27818d zen-tab.py: F1 post-navigate handle check, C4 count
    gate, F4 docstring, C5 restore flags.
  - fa5f737 run2.py: F2 phase 4 re-switch plus send snapshot
    URL gate.
  - ee2a85a tests/test_zenproof2_fix.py: 27 unit tests (16 old
    + 11 new), fake models error entries and silent restore
    failure.
  - 5b032ae improvements/w-zen-delegate-liveproof-prep.md:
    title premise corrected to URL-substring target.
  - b956176 improvements/w-zenproof2-amend-log.md: amend log.
- Sources read before judging:
  - improvements/w-zenproof2-amend-log.md (the amend log, 381
    lines, read in full).
  - Full diff of b27818d and fa5f737 (read line by line), the
    test file (read in full), the prep file amendment note and
    the corrected steps.
  - scripts/zen_backend.py _resolve_target (lines 189-208) and
    dom_observe (lines 232-310): how the snapshot URL and the
    harvested elements are produced.
  - scripts/zen_dom.py list_tabs (lines 641-720), _try_restore
    (597-608), _verify_selected (610-622), tab_at (624-639),
    switch_to_handle (576-581), locate_confirmed (1070+),
    harvest (1349+).
  - The 4 fix reviews (787ab18, 5b0af0d, 7cef509, 2c76690) and
    the 3 amend council reviews (7c6e80d, ddea95a, 4f8825d).
  - Repro templates read, not trusted blindly:
    /tmp/redteam-repro-f1.py, /tmp/redteam-repro-f2.py,
    /tmp/zenproof2_council2_probe.py.

## 1. Time log (wall-clock Asia/Ho_Chi_Minh)

- 20:31 +07, T+0m: task received, amend log + diffs read.
- 20:33 +07, T+2m: suite 27/27 and G0a 177/177 re-run by me.
- 20:34 +07, T+3m: F1 repro re-run against amended code (dies
  at line 241); F2 repro re-run (backend first-match
  confirmed, unchanged by design).
- 20:35 +07, T+4m: backend dom_observe + zen_dom.py read;
  H1 attack constructed and run (stale handle + tab created).
- 20:37 +07, T+6m: H1 variant (select_new=False) run; C5
  probe run (scan fails + reads fail); G0b re-run; fixture
  sha checked; prep file greps; council reviews read.
- 20:39 +07, T+8m: review written, committing.

## 2. What I verified, with evidence

### 2.1 Suite, G0a, G0b, fixture, scope: all re-run by me

- 27 unit tests: python3 -m unittest tests.test_zenproof2_fix,
  Ran 27 tests in 0.003s, OK, exit 0. I ran it myself.
- G0a: python3 -m unittest tests.test_zen_pointer
  tests.test_p2_element_ref tests.test_code_exec, Ran 177
  tests in 12.554s, OK. I ran it myself.
- G0b: code_exec.validate_program passes for PROBE_PROGRAM
  and SEND_PROGRAM. I ran it myself.
- Fixture untouched: sha256 of
  tests/two_vision_fixture.html is
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6
  cbf, identical to FIXTURE_SHA.
- Diff scope: git diff 2c76690..b956176 --shortstat over the
  amend's 4 files is 512 insertions, 72 deletions. (The
  3 pillfix review files in the same range are other lanes'
  commits, not the amend.)
- 0 em dash (U+2014) and 0 en dash (U+2013) in all 5 amend
  files, counted by me.
- Run 1 runner still old (TARGET 'Clone zen thread' line 36,
  title checks 357/377): confirmed, must not be re-run as-is;
  the run-order rule covers it.

### 2.2 F1 is closed for the case it was built for

- Redteam F1 repro re-run by me against the amended code:
  dies at cmd_open zen-tab.py:241 with 'current tab changed
  during navigate (current c743a48f != new aa52510e);
  refusing', never reaches cmd_close. The damage no longer
  reproduces. The regression test
  test_open_focus_reverts_during_navigate_refuses_and_keeps_
  owner_tab proves the same in-suite (0 deletions, owner tab
  survives as a navigate-away, new tab left about:blank).
- The handler handle check is correct as far as it goes:
  DELETE requires current handle == new_handle AND current
  URL containing the fixture substring. A URL-only check
  would delete a navigated owner tab; the handle check is
  what saves it in the F1 repro. The two no-delete tests
  (Council 2 condition 1) cover the navigate-failure and
  wrong-URL branches. Verified in the suite run.

### 2.3 The prep file is clean

- grep for 'Clone zen thread' in
  improvements/w-zen-delegate-liveproof-prep.md returns only
  the amendment note (which describes the old wrong premise),
  H1 content confirmations, and the correct line 674. No
  'title verified' or title gate remains. The two further
  stale statements Council 3's grep missed ('(title
  verified)' in the P3.1/P6.1 checklists) are now
  '(URL verified)'. Verified by me.

### 2.4 F3 fake fidelity is faithful to the real code

- The silent restore failure the fake models is real:
  scripts/zen_dom.py _try_restore (lines 597-608) calls
  switch_to_handle without _verify_selected, so a POST
  /window select that returns success without taking effect
  (the exact run-2 misfire mode) returns None and list_tabs
  returns normally with the wrong tab current. The fake's
  restore_fails models exactly that. The error-entry shape
  ({handle, error}, no URL) matches list_tabs lines 641-720.
- The four F3 tests pin the behaviors as known limitations,
  and the rect tab-awareness in the fake is a genuine
  fidelity improvement (a rect from the wrong tab used to
  be canned).

## 3. Holes found (MINE unless stated)

### H1 (HIGH, MINE): the C4 count gate does not block a stale handle when a tab IS created

Council 1 section 2.4 judged "C4 blocks a stale handle" on
the suite test alone. That test only covers the case where
POST /window/new returns an existing handle WITHOUT creating
a tab (count stays, gate refuses). The gate is a count
comparison: it refuses only when the count did NOT grow by
exactly 1. It never checks whether the returned handle is
actually new. If /window/new returns an EXISTING handle
(the owner tab's) AND creates a tab, the count grows by 1,
the gate passes, and every later check passes on the wrong
tab:

- The (c) check compares current to the returned handle.
  With select_new=True, current is the new tab, so the (c)
  check tries one explicit select to the stale handle. The
  handle exists, the select takes effect, current becomes
  the owner tab, and the (c) check passes. With
  select_new=False (the run-2 mode), current is already the
  owner tab, so the (c) check passes immediately with no
  select at all.
- POST /url then navigates the OWNER tab to the fixture URL.
- The F1 post-navigate check passes: current (owner
  handle) == new_handle (owner handle, stale).
- The URL gate passes (the owner tab now IS the fixture
  page) and the H1 gate passes (the fixture JS ran in it).
- cmd_open returns ok. The owner tab is navigated away and
  the new tab is left as an un-navigated about:blank.
- The runner then proceeds, and cleanup closes by URL: the
  only tab carrying the fixture URL is the owner tab, so
  cmd_close switches to it and DELETEs it.

That is the run-2 incident replayed end to end through
the amended code, defeating the count gate, the (c) check,
the F1 post-navigate check, and the handler handle check.
The explicit-select fallback in the (c) check is the pivot
in the select_new=True mode: it moves current onto the
owner tab. The fallback itself is fine once the handle is
proven new; the missing proof is the hole.

Repro (mine, /tmp/redteam-amend-repro-h1.py, run by me):
a fake whose POST /window/new creates a tab but returns
tabs[0]['handle'] (the owner tab). Output on the amended
code, select_new=True:

- cmd_open RETURNED OK: True
- owner tab url now: file:///.../two_vision_fixture.html
  ?clone=zen (the fixture page)
- new tab url: about:blank
- cmd_close by URL: ok True, count 3 to 2,
  original_missing True
- owner tab still present: False
- deleted: [file:///.../two_vision_fixture.html?clone=zen]

Variant select_new=False, run by me: cmd_open also
RETURNED OK, owner tab navigated to the fixture URL,
deletions [] at open. Same hole, no select needed.

Trigger assessment: /window/new returning an existing
handle has never been observed; the C4 condition itself
was premised on "in case the returned handle is stale",
and the amend implemented only the no-tab half of that
premise. The consequence is the exact incident this whole
track exists to prevent, and the fix is one line (see
condition C1). Same bar as F1, which was mandatory before
live proof despite having no realistic actor: H1 is a
mandatory condition before live proof.

### H2 (MEDIUM, MINE): C5's "not raised" promise is broken by the flag-setting reads

Council 3 C5 asked that a scan failure be reported as
scan_error and a _full_handle/_switch failure as
restore_failed, "not raised: the close already succeeded,
and the runner records the outcome instead of masking it
with an exception". The amend guards the _scan and
_full_handle/_switch calls, but the _title(z) and _url(z)
reads in the same branches are unguarded. When the scan
failed, the transport is the likeliest cause, so those
reads are the likeliest to fail too, and the exception
then propagates out of _restore_original, out of
cmd_close, and masks the successful close anyway.

Probe (mine, run by me): a fake whose list_tabs fails on
the 3rd call (inside _restore_original) AND whose GET
/title and GET /url raise. Output on the amended code:

- cmd_close RAISED: 'simulated read failure'
- scratch tab deleted: True

The close succeeded and the run records an error instead
of ok with scan_error. The suite's C5 tests do not catch
this because the fake's _title/_url never fail. Fix: wrap
the _title/_url reads in _restore_original in
try/except and record None on failure (see condition C2).

### H3 (LOW, MINE): the F2 PROBE gate cannot tell a duplicate fixture tab from the scratch tab

The amend log claims the phase-4 gate means "a send can
only go to the tab the switch just selected and the
snapshot just confirmed". That overstates what the gate
proves. parse_probe_line checks the snapshot URL contains
the target substring and the element count is 1. Two
fixture tabs have the identical URL and one #msg-input
each, so the gate passes on either. And the snapshot URL
is metadata from the resolved tab, while the input
follows the CURRENT tab: dom_observe resolves via
_resolve_target (first match, backend), then harvest and
locate_confirmed evaluate on the current tab (the one
phase 4 switched to). So the gate confirms the URL
substring, not which tab receives the input.

What actually protects the send: the phase-4 switch
refuses on ambiguity (two fixture tabs at switch time),
and phase 5 ev() resolves by URL and raises on ambiguity,
so a duplicate appearing after the send makes the run
error, never a false PASS. The worst case is a send to a
duplicate fixture tab (harmless content, it is a test
fixture) with the run recorded as error. No owner-tab
impact. The compound case (duplicate appearing between
switch and program AND a silent restore failure inside
tab_at leaving current on the duplicate) is the only
wrong-tab path, and it still fails safe at phase 5.
Verdict on F2: the mitigation is real defense in depth,
but the log's claim should be corrected to detection-only
(see note G1). Not a live-run gate beyond the phase-4
test condition Council 2 already set.

### What I could NOT break

- The F1 regression test and the handler after a navigate
  on the right tab: the F1 repro dies at line 241, and the
  handler deletes only when handle AND URL agree.
- The no-delete branches (Council 2 condition 1): both
  suite tests pass on my run.
- The pre-check, _find_in_scan ambiguity refusal, _switch
  verification, _restore_original flagging (for the cases
  the fake models), the count gate for the no-tab case.
- The prep file: no title gate remains.
- The fake's error-entry and silent-restore models: both
  faithful to scripts/zen_dom.py as read in section 2.4.

## 4. Verdict: GO WITH CONDITIONS

The amend is correct in what it does. F1 is proven closed
for its case, the no-delete branches are tested, the prep
file carries no title gate, F3/F4/C5 are implemented as
specified for the cases the fake models, and the suite,
G0a, G0b, and fixture sha all pass on my own re-runs.
One hole is real and must be closed before the next live
proof: H1, the stale handle that creates a tab. It
replays the run-2 incident through every check the amend
added, and its fix is one line plus a regression test.

Conditions, all to be satisfied before the next live
proof (not before landing this amend):

- C1 (MANDATORY, MINE, H1): in cmd_open, refuse when the
  returned handle is already in `before` (the handle list
  captured before POST /window/new), checked immediately
  after /window/new and before the count gate. Add a
  regression test adapted from
  /tmp/redteam-amend-repro-h1.py, in both select modes
  (select_new=True and select_new=False): open must raise,
  zero deletions, owner tab URL unchanged. Land as a
  follow-up commit, re-run the suite, G0a, G0b.
- C2 (MANDATORY, MINE, H2): guard the _title(z) and
  _url(z) reads inside _restore_original (scan_error,
  restore_failed, and missing/ambiguous branches) with
  try/except, recording None on failure, so a failed read
  can never raise out of cmd_close and mask a successful
  close. Add a test on the probe shape (scan fails AND
  the reads fail): cmd_close returns ok with scan_error
  True and the scratch tab deleted. Land as a follow-up
  commit, re-run the suite.
- C3 (MANDATORY, ADOPTED from Council 2 ddea95a): add
  behavioral unit tests for the new phase-4 runner logic
  in run2.py, using a Runner with mocked hypr/tab/
  oneshot_zen (Council 2's /tmp/phase4-probe.py proves
  this works): happy path records send_url and
  send_count; a wrong-URL or wrong-count send snapshot
  raises (ValueError from parse_probe_line, not
  RuntimeError); a missing PROBE line raises; a switch
  landing on a non-fixture URL raises. The F2 mitigation
  must not be executed for the first time in a live run.
- C4 (MANDATORY, ADOPTED from Council 1 7c6e80d): add one
  line to the prep file amendment note. When the owner tab
  carries the fixture URL after a refused open, the
  coordinator navigates it back to the Muse thread by hand
  in the Zen UI, never via a Marionette navigate or DELETE,
  and verifies the pre-check passes before the next run.
  (This also covers the navigated-fixture-tab leftover,
  which the C3 orphan-tab note does not mention: the
  leftover after a refused open is not always an empty
  about:blank tab.)
- C5 (EXECUTION, ADOPTED from Council 3 4f8825d): Council
  3 could not execute code (execution-risk block) and
  required re-execution by an authorized lane. Satisfied
  by this review plus Council 1 and Council 2: the suite
  (27/27), G0a (177/177), G0b, the F1 repro, the H1
  repro, and the C5 probe were all executed independently
  by me (section 5), and Council 1 and Council 2 ran
  the same suites and repros independently. No separate
  re-execution lane is needed.

Notes, not conditions:

- G1 (H3 wording): correct the amend log's F2 claim ("a
  send can only go to the tab the switch just selected")
  to detection-only: the PROBE gate confirms the URL
  substring and count, which a duplicate fixture tab
  satisfies identically; the input follows the current
  tab, and the real guards are the switch ambiguity
  refusal and the phase-5 ev() ambiguity raise.
- G2 (TOCTOU, same class as the admitted F1 residual):
  the handler's cur_url/cur_handle reads and the DELETE
  are separate calls; a focus flip in that microsecond
  window could still delete the wrong tab. No realistic
  actor; the WebDriver protocol offers no atomic
  check-and-delete. Recorded, not gated.
- G3: a focus flip to a duplicate fixture tab after the
  post-navigate check passes all cmd_open gates (URL and
  H1 identical); phase 3 then refuses on ambiguity, the
  run errors, tabs leak. No deletion, no wrong send.
  Requires a duplicate appearing mid-open with no actor.
- G4: the explicit-select fallback in the (c) check is
  the pivot of H1 in select_new=True mode. The membership
  check in C1 removes the danger; the fallback itself
  stays, since it is the correct recovery when the handle
  is proven new.

The Muse chat tab closed by run 2 attempt 2 is NOT
reopened by this amend. Recovery stays the coordinator's
decision, as the amend log states.

## 5. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received ~20:31 +07, 22/11/2026. HEAD at review
  start b956176, equal to origin/todolist-push after fetch.
- 27 unit tests, re-run by me 20:33 +07: python3 -m
  unittest tests.test_zenproof2_fix, Ran 27 tests in
  0.003s, OK, exit 0.
- G0a, re-run by me 20:33 +07: python3 -m unittest
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec, Ran 177 tests in 12.554s, OK.
- G0b, re-run by me 20:34 +07: code_exec.validate_program
  passes for PROBE_PROGRAM and SEND_PROGRAM.
- Fixture sha, re-run by me 20:37 +07:
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6
  cbf, matches FIXTURE_SHA.
- Dash counts, re-run by me 20:37 +07: U+2014 0, U+2013 0
  in all 5 amend files.
- F1 repro, re-run by me 20:34 +07: python3
  /tmp/redteam-repro-f1.py, dies at cmd_open
  zen-tab.py:241 with 'current tab changed during navigate
  (current c743a48f != new aa52510e); refusing', never
  reaches cmd_close.
- F2 repro, re-run by me 20:34 +07: python3
  /tmp/redteam-repro-f2.py, part A _resolve_target returns
  the stale ?clone=zen2 tab, part B returns example.com;
  backend unchanged by design, recorded as known
  limitation.
- H1 repro, run by me 20:35 +07:
  /tmp/redteam-amend-repro-h1.py, select_new=True:
  cmd_open RETURNED OK, owner tab URL now the fixture
  URL, new tab about:blank; cmd_close by URL DELETEs the
  owner tab (owner tab still present False, deleted =
  [fixture URL], original_missing True).
- H1 variant, run by me 20:36 +07: select_new=False:
  cmd_open RETURNED OK, owner tab navigated to the
  fixture URL, deletions [] at open.
- C5 probe, run by me 20:37 +07: list_tabs fails on the
  3rd call AND GET /title and GET /url raise: cmd_close
  RAISED 'simulated read failure' although the scratch
  tab was deleted (True).
- Prep file greps, re-run by me 20:37 +07: 'Clone zen
  thread' only in the amendment note, H1 content
  confirmations, and line 674; no title gate remains.
- Run 1 runner, checked by me 20:37 +07: TARGET 'Clone
  zen thread' line 36, title checks 357/377; must not be
  re-run as-is.
- Backend reads, 20:36 +07: zen_backend.py _resolve_target
  lines 189-208 (first match, no ambiguity refusal),
  dom_observe lines 232-310 (snapshot URL from the
  resolved tab, elements from harvest on the current
  tab); zen_dom.py _try_restore lines 597-608 (no
  _verify_selected, silent restore failure is real),
  locate_confirmed line 1070 (evaluate, current tab).
- Council reviews read 20:37 +07: 7c6e80d Council 1 (GO
  WITH CONDITIONS, 1 doc condition), ddea95a Council 2
  (GO WITH CONDITIONS, phase-4 runner code untested),
  4f8825d Council 3 (GO WITH CONDITIONS, read-only,
  exec blocked, re-execution required).
- Diff scope 20:37 +07: git diff 2c76690..b956176
  --shortstat over the amend's 4 files: 512 insertions,
  72 deletions.
- Files changed by me (review only): improvements/
  w-zenproof2-amend-redteam-review.md (new, this file).
  Repro scripts in /tmp only
  (/tmp/redteam-amend-repro-h1.py). No amend file
  modified. No live run. No reviewer spawned.
