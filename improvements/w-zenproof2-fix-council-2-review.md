# Council 2 review: W-ZENPROOF2-FIX (6d751b9, f0dd5ec, 014938b, 4dafe17)

Reviewer: Council 2, independent (not W-ZENPROOF2-FIX, not
W-ZENPROOF2, not COORD-CLICK-9). Report goes to Muse tong.
No fix modified, no live proof re-run, no tab opened,
navigated, or deleted in Pham Tuan's Zen. All verification is
code/unit level only, plus two read-only probes in /tmp.
No em dash or en dash anywhere in this file. No personal info.

## 0. Verdict: GO WITH CONDITIONS

The fix is correct on all three items (a, b, c) and may land.
Two conditions must be met before the next live proof runs
(see section 4). The code is not the problem; one
safety-critical branch is untested, and the procedure doc still
states the wrong premise. Neither blocks landing the fix, but
both must close before any live tab operation.

## 1. Time log (wall-clock Asia/Ho_Chi_Minh, 22/11/2026)

- 20:17 +07: task received, read w-zenproof2-fix-log.md,
  the 4 commit diffs, zen-tab.py, run2.py, test file.
- 20:18 +07: ran 16 unit tests independently, 16/16 OK.
  Ran G0a suite, 177/177 OK. Ran G0b validate, both programs
  pass. Read old zen-tab.py and run2.py at a355002 to confirm
  the root cause.
- 20:19 +07: wrote and ran two read-only probes in
  /tmp/zenproof2_council2_probe.py (Probe A: first-run 15/16
  claim; Probe B: handler no-delete branch). Both confirmed.
- 20:20 +07: review written, committing.

## 2. What I verified independently (command, output, hash)

- 16 unit tests, run by me:
  `python3 -m unittest tests.test_zenproof2_fix` -> Ran 16
  tests in 0.003s, OK. All 16 pass, including the incident
  regression test.
- G0a suite, run by me: `python3 -m unittest
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec` -> Ran 177 tests in 14.379s, OK.
  No regression in the shared suites.
- G0b, run by me: code_exec.validate_program passes for
  both PROBE_PROGRAM and SEND_PROGRAM (printed 'PROBE
  validates', 'SEND validates').
- Fixture untouched: sha256 of
  tests/two_vision_fixture.html is
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6
  cbf, identical to FIXTURE_SHA in run2.py.
- 0 em dash (U+2014) and 0 en dash (U+2013) in all four
  changed/new files (zen-tab.py, run2.py, test file, log).
  0 SCRATCH_TITLE refs in the three code/test files.
- Scope check: the 4 commits touch only the 4 claimed files
  (zen-tab.py, run2.py, test file, log). No shared library
  (scripts/zen_backend.py, code_exec.py, zen_dom.py) is
  touched, so the regression surface is the Zen proof flow
  only.
- Root cause confirmed against the old code at a355002:
  old zen-tab.py line 35 had SCRATCH_TITLE =
  'Clone zen thread', line 90 gated on the document title
  (the wrong premise: the fixture title is the static
  'Two-vision benchmark fixture'), and lines 135-140 ran a
  blind DELETE in the exception handler with no check of
  which tab was current. Old run2.py line 39 had TARGET =
  'Clone zen thread' and parsed the probe line by title
  (lines 393-395). The fix removes all of it.

## 3. FakeZenSession fidelity: models the misfire correctly

- select_new=False reproduces the run 2 misfire exactly:
  POST /window/new creates the tab but leaves the owner tab
  current. select_works=False models the explicit POST
  /window select not taking effect. The regression test sets
  both False, which is the incident.
- The fake's DELETE closes the current window and activates
  a neighbour, matching Marionette semantics. Its /url
  navigate rewrites the current tab's URL and title, matching
  the incident (the navigate rewrote the owner's tab).
- Probe A (my own, /tmp) confirms the fake's outcome:
  tabs=3, deleted=[], current URL is the owner URL, tab
  list is [owner, example.com, about:blank]. That is the
  fail-closed outcome the fix claims.
- Fidelity limits (minor, noted not blocking):
  list_tabs in the fake does not switch through tabs (the
  real one switches and restores); the end state matches
  (current restored) but a failed restore is unmodelled.
  evaluate always returns readyState 'complete' and always
  returns a #msg-input rect, so the readyState timeout and
  missing-rect paths cannot fail in the fake.

## 4. Test completeness: what is covered, what is missing

Covered (verified by reading the tests and running them):
- Happy path (selected_by window/new), explicit-select path,
  wrong H1 closes only the scratch tab, duplicate fixture
  tab refused, switch/eval/close by URL, close when scratch
  already gone, close with ambiguous or missing original
  URL, switch to an unknown URL refuses, programs target by
  URL not title, parse_probe_line good plus 4 bad lines.

MISSING, the one gap that matters:
- The cmd_open exception handler's NO-DELETE branch is not
  covered by any suite test. The handler deletes only when
  the current tab is the fixture tab by URL; the delete
  branch is tested (wrong H1), but no test raises inside the
  try while the current tab is NOT the fixture tab. That is
  the exact branch that would have saved the owner's tab in
  run 2 if a navigate had landed on the wrong tab, and it is
  the second layer of defense behind the (c) check.
- Probe B (my own, /tmp) proves the code is correct here:
  a subclassed FakeSession whose /url POST raises, current
  tab the new about:blank, gives tabs=3, deleted=[],
  owner tab intact. The code works; the suite does not guard
  it. A future edit could break this branch silently.
- The same gap covers the URL-gate failure path (navigate
  lands on a non-fixture URL): it reaches the same no-delete
  branch and is likewise untested.

Other untested edges (minor, not conditions):
- POST /window/new itself raising (before the try block):
  safe by construction (no navigate, no DELETE), untested.
- cmd_close when the select to the scratch tab does not
  take effect: _switch raises, DELETE never runs, safe but
  the error propagates and cleanup would report failure.
- _restore_original calling _switch without a guard: if the
  switch to the original tab fails, cmd_close raises even
  though the close succeeded. Reporting issue, not a
  tab-safety issue.
- The handler's post-DELETE restore uses the pre-open handle
  (same session, best-effort, wrapped in try/except) rather
  than re-resolving url_before by URL. Safe as-is, but
  inconsistent with the fix's own URL-identity principle.
- URL identity is a substring, so a tab with
  ?clone=zen2 would match the ?clone=zen identity. This is
  pre-existing design (the backend _resolve_target is also
  substring based) and the proof flow only ever opens
  ?clone=zen, so it is theoretical, not a regression.

## 5. The first-run 15/16 claim: confirmed true

The log says the first run was 15/16 because the incident
regression test expected the tab count to stay 2, but
/window/new creates the about:blank tab even when it never
makes it current, so the count is 3 with zero deletions.
Probe A confirms this independently: the code leaves 3 tabs
and 0 deletions, owner tab current, third tab about:blank
un-navigated. Expecting 2 assumed /window/new would not
create the tab when selection fails, which is wrong:
Marionette creates the tab and only the current selection
fails. The test expectation was wrong, not the code. The
corrected expectation (3 tabs, about:blank, 0 deletions) is
the right fail-closed outcome.

## 6. Regression assessment

- No regression in the shared suites (G0a 177/177, G0b both
  programs validate). No shared library touched.
- The fix changes the runner's target from title to URL
  substring. That is the intended correction (the title
  premise was wrong), and the next live proof is the real
  validation. Nothing else in the repo depends on the old
  title target.
- The residual risk is live-only: whether Zen's tab
  management selects a Marionette opened tab at all. The
  (c) check plus the explicit-select fallback handle both
  cases, and a 'not made current' refusal is the safe
  outcome. That question is open for the live run, not for
  this review.

## 7. Conditions (must close before the next live proof)

1. Add one test for the cmd_open exception handler's
   no-delete branch: an in-try exception with the current
   tab NOT the fixture tab (navigate POST raises, or the
   navigate lands on a non-fixture URL). Assert zero
   deletions, the owner tab intact, and no tab closed.
   Template: /tmp/zenproof2_council2_probe.py Probe B
   (subclass FakeSession, raise on POST /url, run cmd_open,
   assert deleted == [] and len(tabs) == 3). Land it as a
   follow-up commit on todolist-push and re-run the suite.
2. Correct or mark stale the prep file
   improvements/w-zen-delegate-liveproof-prep.md line 671
   and the P2.2/P3.3 checklist, which still state the wrong
   title premise. The fix log already flags this as open
   item 1. Either the coordinator corrects the file, or the
   next runner is told in writing that the prep file is stale
   on this point. Do not let the next proof reintroduce the
   title target from the prep file.

## 8. Evidence appendix (Lauren Tan)

- Commits reviewed: 6d751b9 (zen-tab fix), f0dd5ec (run2
  fix), 014938b (16 tests), 4dafe17 (fix log), all on
  todolist-push, HEAD 4dafe17 at review start.
- 16 unit tests run by me 20:18 +07: Ran 16 tests in
  0.003s, OK.
- G0a run by me 20:18 +07: Ran 177 tests in 14.379s, OK.
- G0b run by me 20:18 +07: PROBE validates, SEND validates.
- Old code read at a355002 20:18 +07: SCRATCH_TITLE line
  35, title gate lines 90-92, blind DELETE lines 135-140;
  old run2.py TARGET line 39, title probe lines 393-395.
- Probe A run by me 20:19 +07 (/tmp, read-only): tabs=3,
  deleted=[], current owner URL, third tab about:blank.
- Probe B run by me 20:19 +07 (/tmp, read-only): navigate
  POST raises, tabs=3, deleted=[], owner tab intact.
- Fixture sha 20:18 +07:
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6
  cbf, matches FIXTURE_SHA.
- Dash counts 20:18 +07: U+2014 0, U+2013 0 in all four
  files; SCRATCH_TITLE refs 0 in code/test files.
- No live Zen tab was opened, navigated, or deleted. No
  proof re-run. No reviewer spawned. No fix file modified
  (only this review file is new).
