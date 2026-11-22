# Council 1 review: W-ZENPROOF2-FIX (URL tab identity + new-tab current check)

Reviewer: Council 1, independent (not W-ZENPROOF2-FIX, not
W-ZENPROOF2, not COORD-CLICK-9). Report goes to Muse tong, not
directly to Pham Tuan. No fix modified, no live run, no tab
opened, navigated, or deleted in Pham Tuan's Zen. All
verification is code/unit level only, plus my own re-runs of
the unit and G0a suites. No em dash or en dash anywhere in this
file. No personal info.

## 0. Task and sources (20:16 +07, 22/11/2026)

- Task received ~20:16 +07. Branch todolist-push, repo
  ~/workspace/computer-use-wayland, HEAD 4dafe17 at review
  start. The 4 fix files are committed, not dirty (git status
  on the 4 paths is empty).
- Fix under review, 4 commits:
  - 6d751b9 zen-tab.py: URL identity, (c) current check,
    guarded DELETE.
  - f0dd5ec run2.py: URL target, probe gate, close by URL.
  - 014938b tests/test_zenproof2_fix.py: 16 unit tests.
  - 4dafe17 improvements/w-zenproof2-fix-log.md: fix log.
- Sources read before judging:
  - improvements/w-zenproof2-fix-log.md (the fix log, 231
    lines).
  - Full diff of 6d751b9 and f0dd5ec (read line by line, not
    skimmed), the test file (390 lines, read in full), and
    the current zen-tab.py _switch and main().
  - improvements/w-zenproof2-log.md sections 5 and 6 (the
    run 2 incident, the mechanism the fix must block).
  - tests/two_vision_fixture.html (title line, no
    document.title).
  - scripts/zen_dom.py list_tabs lines 641+ (restore
    behavior) and scripts/zen_backend.py _resolve_target
    lines 189-208 (URL substring matching).
  - improvements/w-zen-delegate-liveproof-prep.md lines 281,
    493-536, 565-570, 665-675, 716, 724 (open item 1).
  - improvements/c5-zenproof-runs/c5-zen-delegate-run.py
    lines 36, 57-76, 357, 377 (open item 2, run 1).

## 1. Time log (wall-clock Asia/Ho_Chi_Minh)

- 20:16 +07, T+0m: task received, log + diff stat read.
- 20:17 +07, T+1m: full diff of 6d751b9 and f0dd5ec read.
- 20:18 +07, T+2m: test file read in full; 16 unit tests
  re-run by me, 16/16 OK.
- 20:19 +07, T+3m: _switch verification, DELETE/navigate
  sites, SCRATCH_TITLE refs, fixture title, G0a 177/177
  re-run by me, G0b validate re-run by me, open items
  checked against the prep file and run 1.
- 20:20 +07, T+4m: run 2 log sections 5 and 6 re-read,
  list_tabs restore and _resolve_target confirmed.
- 20:21 +07, T+5m: review written, committing.

## 2. What I verified, with evidence

### 2.1 Diff scope is exactly the fix, nothing else

- git diff --stat a355002..4dafe17: 4 files, 955 insertions,
  88 deletions. Only zen-tab.py, run2.py,
  test_zenproof2_fix.py, and the fix log. No other file
  touched by these commits. The pre-existing dirty
  tests/realistic/clone1-batch3/results.json and the
  untracked prompt files from other workers are not in
  these commits.
- 0 em dash (U+2014) and 0 en dash (U+2013) in all 4 files,
  counted by me. Fixture untouched (still the 7f3a70b
  content; <title>Two-vision benchmark fixture</title>,
  no document.title anywhere in the file).

### 2.2 The 16 unit tests pass on my own run, and the regression test is faithful

- Command: python3 -m unittest tests.test_zenproof2_fix -v.
  Output: Ran 16 tests in 0.003s, OK. Exit 0. I ran it
  myself, not trusting the log's 16/16.
- The regression test
  test_open_new_tab_never_current_refuses_without_touch
  models the run 2 misfire exactly as the run 2 log states
  it: FakeSession with select_new=False (POST /window/new
  does not make the new tab current) and select_works=False
  (the explicit POST /window select does not take effect).
  That is the worst case of the inferred mechanism in
  w-zenproof2-log.md section 6.
- It proves fail-closed, not just "raises": the exception
  message contains 'not made current'; the tab count is 3
  (owner + example + the new about:blank tab); fake.deleted
  is [] (zero deletions); the current tab URL is still the
  owner URL; the owner tab URL is unchanged (so no /url
  navigate ran, because the fake's POST /url rewrites the
  current tab's URL); the new tab is left as an un-navigated
  about:blank. The test's comment states this honestly:
  leaving the empty tab is the fail-closed outcome, because
  the select that would let the driver close it is exactly
  what just failed, and deleting the current window would
  close the owner's tab.
- The other 15 tests cover the rest of the fix: happy path
  (selected_by 'window/new', owner tab kept, URL + H1 in
  the result), explicit-select path, wrong H1 closes only
  the scratch tab (deleted == [FIXTURE_URL], owner tab
  current), duplicate fixture tab refused (zero deletions),
  switch/eval/close by URL, close when scratch already gone
  (already_closed, owner restored), close with ambiguous or
  missing original URL (no guessing, flags set), switch to
  an unknown URL refuses, programs target by URL with 4
  scopes, parse_probe_line accepts the good line and
  rejects the old title format, wrong URL, wrong count, and
  wrong shape.

### 2.3 Fix (a): URL identity, H1 only as content confirmation

- SCRATCH_TITLE is deleted; 0 refs in the 3 code files
  (grep, counted by me). New constants
  SCRATCH_URL_SUBSTR = 'two_vision_fixture.html?clone=zen'
  and SCRATCH_H1 = 'Clone zen thread'. The only remaining
  'Clone zen thread' strings are the SCRATCH_H1 constant
  and one docstring line.
- cmd_open gates post-navigate on the URL containing the
  substring, then on the H1 text, then on readyState
  complete. The document title is read only for the result
  record, never gated on. This matches the fixture: the
  title is static, the JS only sets the H1.
- run2.py TARGET is the URL substring. PROBE_PROGRAM and
  SEND_PROGRAM call dom_observe with it, and all 4 SEND
  actions carry it as scope. The test
  test_programs_target_by_url_not_title asserts the 4
  scopes and that 'Clone zen thread' appears in neither
  program.
- parse_probe_line gates on the snapshot URL containing
  the target and the count being '1', and rejects the old
  title format. Phase 3 uses it, and also gates on the
  switched tab URL and on the H1 read by ev(). The title
  is kept on a separate SNAP-TITLE line for evidence only.
- No backend change was needed, and the log's claim for
  that is true: scripts/zen_backend.py _resolve_target
  lines 189-208 matches a target as a substring over
  title, url, or handle, so a URL substring resolves the
  scratch tab. (It returns the first match in list order;
  the driver's pre-check guarantees the fixture URL is
  unique, so the first match is the scratch tab.)

### 2.4 Fix (b): URL identity, no stored handles across sessions

- Runner keeps no handle: self.opened (bool) and
  self.original_url replace self.scratch_handle and
  self.original_handle. The current handle from
  tabs_before is used only inside that one list response;
  the URL is kept, the handle is dropped. The code
  comments say this, and the diff shows it.
- cmd_switch and cmd_eval take a URL substring and resolve
  it fresh inside the call via _resolve_url (one scan, so
  the entry and the handle list come from the same
  moment). _find_in_scan refuses on more than one match;
  _full_handle refuses on zero or ambiguous prefixes.
  Entries with no URL are skipped, never matched.
- cmd_close takes (scratch URL substring, original URL).
  The scratch close is precise by URL; the original
  restore re-resolves by URL after the DELETE, and never
  guesses: missing or ambiguous original URL is reported
  with original_missing / original_ambiguous flags and
  the current tab is left as Zen activated it. When the
  scratch tab is already gone, close returns
  already_closed and only restores.
- cmd_open pre-check refuses before opening anything when
  a tab already carries the fixture URL, so URL identity
  can never be ambiguous between a stale and a fresh
  scratch tab. (When 2+ fixture tabs exist, _find_in_scan
  raises on ambiguity, which also refuses; the message
  differs, the outcome is the same.)
- This maps to the run 2 log's proven finding: handles
  are ephemeral per session (15 of 15 comparable URLs had
  a different handle between two back-to-back lists), so
  stored handles cannot identify tabs across sessions.

### 2.5 Fix (c): the new tab must be current before any navigate or DELETE

- cmd_open reads the current handle back after POST
  /window/new. When it is not the new handle, one explicit
  POST /window select is tried and the current handle is
  read again. When the new tab still is not current, the
  driver raises 'new tab was not made current ...;
  refusing to navigate or close' BEFORE any /url navigate
  or DELETE. The successful path records selected_by
  ('window/new' or 'explicit-select').
- The open exception handler deletes ONLY when the current
  tab is the fixture tab by URL, read fresh with GET /url.
  When the current tab is anything else, it deletes
  nothing. When _url itself raises, cur_url is None and
  nothing is deleted. After a scratch DELETE it
  best-effort restores the tab that was current before the
  open (same-session handle, _switch verifies, failure is
  swallowed).
- This blocks the run 2 mechanism at its first step. The
  run 2 log states the mechanism as the best explanation,
  not a proven fact; the fix handles both cases (selected
  by /window/new, or selected by explicit POST /window, or
  refused outright). The log's open item 3 is honest about
  the remaining question (whether Zen selects a
  Marionette-opened tab at all) and names the fallback
  (select through Zen's own UI, or refuse the run).

### 2.6 No tab operation can touch Pham Tuan's tabs

- I enumerated every DELETE and /url navigate in the fixed
  zen-tab.py (grep): exactly 2 DELETE sites and 1
  navigate site.
  - Navigate (line 202): only after the (c) check proved
    the new tab is current.
  - DELETE in the open exception handler (line 286): only
    when the current tab URL contains the fixture
    substring, read fresh.
  - DELETE in cmd_close (line 333): only after _switch to
    the scratch tab, and _switch verifies the switch took
    effect (raises 'switch did not take effect' when the
    current handle is not the target). So the DELETE runs
    only with the scratch tab current.
- cmd_switch and cmd_eval only switch and read; they
  navigate and delete nothing. The runner never issues a
  DELETE directly; it goes through zen-tab.py close by
  URL. The runner's hypr calls (activewindow, clients)
  are read-only. kill-hung is untouched by this fix
  (pre-existing recovery tool, not a tab operation).
- _scan depends on list_tabs restoring the original tab.
  Confirmed in scripts/zen_dom.py lines 641-652: the
  originally selected tab is restored afterwards, and a
  failed restore is raised, never swallowed. So _scan does
  not disturb the current tab.
- The fake session's DELETE semantics match real
  Marionette (DELETE closes the current window; Zen
  activates an adjacent tab), and its POST /url rewrites
  the current tab's URL, so the regression test's
  assertions (owner URL unchanged, zero deletions) are
  meaningful, not vacuous.

### 2.7 G0b and G0a, re-run by me

- G0b: I validated both programs with
  code_exec.validate_program (same check the run used).
  PROBE_PROGRAM validate OK, SEND_PROGRAM validate OK.
- G0a: python3 -m unittest tests.test_zen_pointer
  tests.test_p2_element_ref tests.test_code_exec. Ran 177
  tests in 14.116s, OK. Exit 0. No regression.

### 2.8 The 3 open items are real and correctly recorded

- Open item 1 (prep file still wrong): confirmed, and the
  spread is wider than the worker listed. Line 671 states
  'The ?clone=zen query sets the title to Clone zen
  thread'. The checklist lines 716 (P2.2) and 724 (P3.3)
  still demand the title. The procedure body also still
  carries the title premise at lines 281, 504, 526, 536,
  and the run-1 program listing at lines 565-570. The
  fix must not be judged on the prep file, but the next
  proof must not follow it as written. See condition C1.
- Open item 2 (run 1 runner still old): confirmed.
  c5-zen-delegate-run.py line 36 TARGET = 'Clone zen
  thread', title checks at lines 357 and 377. It must not
  be re-run as-is. The next proof copies the fixed run 2
  runner. See condition C1.
- Open item 3 (not verified live): confirmed. No live
  proof re-run was done or is claimed. The next proof is
  a fresh run number with a fresh intent/message, after
  council + redteam review. See condition C2.

## 3. Gaps and minor observations (not blockers)

- G1 (hardening, not required): the (c) check verifies
  the current handle equals the new handle, but does not
  verify the tab count increased by 1 after POST
  /window/new. If /window/new ever returned a stale or
  existing handle, the check would pass and the navigate
  would rewrite the wrong tab. That failure mode was not
  observed in run 2 (the tab was created, count went
  18 to 19), and the fake models the observed misfire.
  Consider adding a count check in a later hardening
  pass; it is not a condition for GO.
- G2 (known fail-closed leak): when the (c) check
  refuses, the empty about:blank tab is left behind, and
  the runner's cleanup skips it because opened is False.
  That is the correct fail-closed outcome (the select
  that would let the driver close it is exactly what
  failed), but the tab does not clean itself up. The
  pre-check refuses only on a fixture URL tab, not on an
  about:blank tab, so leftovers would accumulate across
  refused runs if nobody closes them. See condition C3.
- G3 (minor limitation): phase 1 refuses with 'could not
  identify the current tab' when the current tab has no
  URL (for example an about:blank tab is current). That
  is fail-closed and correct, but it means a run cannot
  start while an empty tab is current. Not a defect.
- G4 (minor): in cmd_close, the post-DELETE verification
  scan calls _scan, and a list_tabs hang would raise
  after the scratch tab is already deleted, so the runner
  would record a close failure even though the tab is
  gone. Pre-existing list_tabs behavior, not introduced
  by this fix, and the runner's cleanup records the
  error rather than masking it. Not a defect.
- G5 (minor): the fake's list_tabs does not model the
  switch-through side effect of the real list_tabs (it
  returns entries without switching). The restore
  behavior is confirmed in the real code (section 2.6),
  so this is a test-fidelity note, not a gap in the fix.

## 4. Verdict: GO WITH CONDITIONS

The fix is correct and complete for its scope. All three
items (a), (b), (c) are implemented as specified, the
regression test faithfully models the run 2 misfire and
proves fail-closed behavior, no tab operation can touch
Pham Tuan's tabs, and G0a/G0b pass on my own re-runs.
The 3 open items are real but are correctly scoped out
of this fix, not hidden.

Conditions, all to be satisfied before the next live
proof (not before landing this fix):

- C1. Correct the prep file, or mark it stale in writing.
  Fix the wrong title premise at line 671, checklist
  lines 716 (P2.2) and 724 (P3.3), and the procedure body
  lines 281, 504, 526, 536, to the URL-substring target
  (or the coordinator tells the next runner in writing
  that the prep file is stale on this point). The next
  proof copies the fixed run 2 runner; run 1
  (c5-zen-delegate-run.py) must not be re-run as-is.
- C2. The next proof is a fresh run number with a fresh
  intent/message, after redteam review of this fix
  (council 1 is done here; redteam is still owed). No
  live re-run of run 2, and no live run of this fix
  until redteam has reviewed it.
- C3. After any run that hits the (c) refusal, the
  coordinator closes the leftover empty about:blank tab
  by hand in the Zen UI (the driver cannot close it,
  because the select that would let it is exactly what
  failed). Do not leave refused-run empty tabs to
  accumulate.
- C4 (non-blocking, hardening): consider gating the (c)
  check on the tab count increasing by 1 after POST
  /window/new, so a stale returned handle cannot pass
  the check. May be done in a later pass; not required
  for GO.

The Muse chat tab closed by run 2 is NOT reopened by
this fix. Recovery stays the coordinator's decision, as
the fix log states.

## 5. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received ~20:16 +07, 22/11/2026. HEAD at review
  start 4dafe17.
- 16 unit tests, re-run by me 20:18 +07: python3 -m
  unittest tests.test_zenproof2_fix -v, Ran 16 tests in
  0.003s, OK, exit 0.
- G0a, re-run by me 20:19 +07: python3 -m unittest
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec, Ran 177 tests in 14.116s, OK.
- G0b, re-run by me 20:19 +07:
  code_exec.validate_program passes for PROBE_PROGRAM
  and SEND_PROGRAM.
- Diff scope 20:19 +07: git diff --stat
  a355002..4dafe17, 4 files, 955 insertions, 88
  deletions.
- SCRATCH_TITLE refs 20:19 +07: 0 in the 3 code files.
  Em dash 0, en dash 0 in all 4 files, counted by me.
- Fixture 20:19 +07: <title>Two-vision benchmark
  fixture</title>, no document.title in the file.
- DELETE sites 20:19 +07: exactly 2 in zen-tab.py
  (lines 286 and 333), both guarded; 1 navigate site
  (line 202), after the (c) check.
- Prep file 20:19 +07: wrong premise at line 671,
  checklist 716 and 724, procedure body 281, 504, 526,
  536, program listing 565-570.
- Run 1 runner 20:19 +07: TARGET 'Clone zen thread'
  line 36, title checks lines 357 and 377.
- Run 2 log 20:20 +07: sections 5 and 6 re-read; the
  only DELETE in attempt 2 was the open exception
  handler; handles ephemeral (15 of 15 URLs changed
  between back-to-back lists).
- list_tabs restore 20:20 +07: scripts/zen_dom.py lines
  641-652, original tab restored, failed restore raised.
- _resolve_target 20:20 +07: scripts/zen_backend.py
  lines 189-208, substring match over title, url, handle.
- Files changed by me (review only): improvements/
  w-zenproof2-fix-council-1-review.md (new, this file).
  No fix file modified. No live run. No reviewer
  spawned.
