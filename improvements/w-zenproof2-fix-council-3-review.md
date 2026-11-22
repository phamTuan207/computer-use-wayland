# Council 3 review: W-ZENPROOF2-FIX (URL tab identity + new-tab current check)

Reviewer: Council 3, independent (not W-ZENPROOF2-FIX, not
W-ZENPROOF2, not COORD-CLICK-9). Report to Muse tong, not
directly to Pham Tuan. No fix modified, no live proof run, no
tab opened, navigated, or deleted in Pham Tuan's Zen. All
verification is code/unit level plus reading, done on the VM.
No em dash or en dash anywhere in this file. No personal info.

## 0. Task and sources

- Task received 20:17 +07, 22/11/2026. Branch todolist-push,
  repo ~/workspace/computer-use-wayland.
- Sources read before judging:
  - improvements/w-zenproof2-fix-log.md (worker log, sections
    0-5).
  - Diffs of 6d751b9 (zen-tab.py), f0dd5ec (run2.py), 014938b
    (tests), 4dafe17 (log).
  - improvements/w-zenproof2-log.md section 6 (the incident:
    run 2 attempt 2 closed the Muse tab).
  - improvements/w-zen-delegate-liveproof-prep.md (full grep
    for 'Clone zen thread'; lines 281, 497-538, 560-580,
    665-680, 710-730 read in full).
  - tests/two_vision_fixture.html (title line 3, H1 line 13,
    JS line 24).
  - scripts/zen_backend.py _resolve_target lines 189-208.
  - improvements/c5-zenproof-runs/c5-zen-delegate-run.py
    (run 1, old literal) and c5-zen-delegate-run2.py phase 1
    (driver transfer, lines 330-360).

## 1. Time log (wall-clock Asia/Ho_Chi_Minh)

- 20:17 +07, T+0m: task received, log and all 3 diffs read.
- 20:18 +07, T+1m: tests run independently, 16/16 OK; grep
  confirms no title gate left in the fixed files; 0 em/en
  dash in all 4 files.
- 20:18 +07, T+1m: G0a suite run independently, 177/177 OK.
- 20:19 +07, T+2m: prep file, run 1, driver transfer, fixture
  verified by reading and grep; review written, committing.

## 2. Verdict: GO WITH CONDITIONS

The fix code is correct and complete for its 3 brief items,
and the test numbers check out by my own runs. The risk that
remains is not in the code, it is in the procedure doc the
coordinator follows: the prep file still instructs the exact
title-gated verify/close pattern that caused the incident,
and the worker under-reported how many places carry it. The
conditions below gate the next live run, not the fix. None of
them asks the fix worker to rework the code.

## 3. What I verified independently (evidence)

- Test numbers, my own runs: `python3 -m unittest
  tests.test_zenproof2_fix`, Ran 16 tests, OK, 0.002s.
  G0a: `python3 -m unittest tests.test_zen_pointer
  tests.test_p2_element_ref tests.test_code_exec`, Ran 177
  tests, OK, 14.201s. The worker reported 0.001s and 12.6s;
  same counts, the time difference is machine load only.
- No title gate left: grep for SCRATCH_TITLE and for
  `title != TARGET` in zen-tab.py and run2.py returns
  nothing. The remaining 'Clone zen thread' occurrences are
  SCRATCH_H1 (content confirmation) and one docstring line.
- 0 em dash (U+2014) and 0 en dash (U+2013) in all 4 files,
  counted.
- Fixture untouched: `git diff` and `git status` on
  tests/two_vision_fixture.html are empty. Title is the
  static 'Two-vision benchmark fixture' (line 3); the JS
  (line 24) only sets the H1 textContent, never
  document.title.
- Backend needs no change: _resolve_target matches a target
  as a substring over title, url, or handle (lines 189-208),
  so a URL substring target resolves through the url key.
- Commits pushed: `git ls-remote origin todolist-push` =
  4dafe17e5c14f17fe62805de9f6084e8f1f6f85b, matches local
  HEAD. The 4 commits touch exactly 4 files (zen-tab.py,
  run2.py, test file, log). Clean scope; the pre-existing
  dirty tests/realistic/clone1-batch3/results.json was not
  touched by any of the 4 commits.
- Driver transfer closes the stale-driver risk: run2.py
  phase 1 copies the fixed zen-tab.py to the laptop and
  verifies sha256, raising on mismatch (lines 349-353). The
  live run uses the fixed driver.

## 4. Fix assessment per item

### (a) Target by URL substring or H1, never by document.title: CORRECT

- cmd_open gates on the navigated tab URL containing
  SCRATCH_URL_SUBSTR, then on the H1 text, then on
  readyState complete. The title is only recorded as
  evidence. Confirmed in the diff.
- run2.py TARGET is the URL substring; all 4 SEND scopes
  carry it; parse_probe_line gates on the URL and the count
  and rejects the old title format plus 3 other bad lines.
  Confirmed in the diff and by the RunnerFixTest tests.

### (b) Identify tabs by URL, never by stored handles: CORRECT

- The runner keeps no handle (self.opened flag plus
  self.original_url; the current handle is dropped right
  where it is read). zen-tab.py resolves fresh per session
  via _scan / _find_in_scan / _full_handle and refuses on
  zero or ambiguous matches. cmd_close re-resolves the
  original tab by URL after the DELETE instead of trusting
  a pre-DELETE handle. Confirmed in the diff and by the
  switch/eval/close tests.
- The premise is proven by the incident log itself: 15 of
  15 comparable URLs had a different handle between two
  list scans a minute apart, so handles are ephemeral per
  session on this Zen.

### (c) Check POST /window/new really made the new tab current: CORRECT

- cmd_open reads the current handle back after POST
  /window/new, tries one explicit select when it is not the
  new handle, and raises before any navigate or DELETE when
  the new tab still is not current. The open exception
  handler deletes ONLY when the current tab is the fixture
  tab by URL (read fresh with GET /url). Confirmed in the
  diff.
- The incident regression test models the exact misfire
  (select_new=False, select_works=False) and proves zero
  deletions, the owner tab URL unchanged, the owner tab
  still current. Confirmed by my own test run.

## 5. Restore mechanism: never guesses (confirmed, 2 minor observations)

- _restore_original: when the original URL is missing or
  matches more than one tab, it sets original_missing /
  original_ambiguous, records the current title and URL,
  and leaves the current tab as Zen activated it. cmd_close
  still closes the scratch tab by URL in that case, and
  returns already_closed plus restore when the scratch tab
  is already gone. Tests cover ambiguous, missing, and
  already-gone. Confirmed.
- Minor observation 1 (not a blocker): when _scan itself
  raises inside _restore_original, the except labels it
  original_ambiguous. A scan failure is an error, not
  ambiguity. The outcome is identical (no guess, current
  left alone), only the flag mislabels. Fix at convenience.
- Minor observation 2 (not a blocker): _full_handle
  raising inside _restore_original propagates out of
  cmd_close instead of being recorded in the result flags.
  Safe (the scratch tab is already deleted, the error is
  reported by the runner cleanup), but the flags are not
  set on that path. Fix at convenience.

## 6. Open items: assessment (this is where the risk lives)

### 6.1 Prep file wrong premise: WORKER UNDER-REPORTED, must resolve before next live run

- The worker listed line 671 plus the P2.2/P3.3 checklist
  lines. My grep finds 'Clone zen thread' at 10 further
  places. Full stale list: lines 281, 504, 526, 536, 565,
  567, 568, 569, 570, 671, 716, 724. Line 674 is CORRECT
  (the H1 text really is 'Clone zen thread') and stays.
- The dangerous ones are live procedure steps, not just
  the premise:
  - P2.2 procedure (line 504): "Expected: new handle
    recorded, title 'Clone zen thread', readyState
    complete... On timeout or wrong title: close the new
    tab if one was opened, delete the session, ABORT."
    This instructs title-gated close. It is the exact
    incident pattern. Following it would false-ABORT (the
    real title is 'Two-vision benchmark fixture') or push
    the operator to "fix" the driver back to the title
    gate.
  - P3.1 procedure (line 526): "switch the Marionette
    current tab to the scratch handle (finding D), verify
    the current title is 'Clone zen thread'". Title gate
    plus handle identity, both removed by the fix.
  - P3.3 procedure (line 536) plus the SEND program
    example (lines 565-570): dom_observe and scopes with
    'Clone zen thread'. A runner copying the example
    reintroduces the title target.
  - Line 281: a proposed fix shape using the title
    target. Lower risk (proposal text, not a step), but
    stale.
- Condition C1 below. Do NOT use the worker's shorter
  list; use this list. The worker was right not to edit
  the coordinator-owned procedure file, but the record of
  what is stale was incomplete, and the coordinator must
  work from the complete list.

### 6.2 Run 1 runner: confirmed dead, must not be re-run

- c5-zen-delegate-run.py still has TARGET 'Clone zen
  thread' (line 36), title dom_observe (lines 57, 64),
  title scopes (lines 67, 70, 72, 76), title switch check
  (line 357), title probe parse (line 377). Confirmed by
  grep.
- It is now doubly dead: old title premise AND old
  handle-based driver calls (tab('switch', scratch_handle),
  tab('close', scratch_handle, original_handle)) that the
  fixed driver will refuse, because a handle string is
  not a URL substring. The refusal is safe (raises, never
  guesses), but the file cannot run. Condition C2 below.

### 6.3 Orphan about:blank tab on refusal: fail-closed by design, needs a rule

- When cmd_open hits 'not made current', the new
  about:blank tab is left open (the test asserts 3 tabs,
  zero deletions). That is the correct fail-closed
  outcome: the select that would let us close it is
  exactly what just failed, and deleting the current
  window would close the owner's tab.
- But it leaves residue in the owner's Zen, and each
  retried open leaves another one. Condition C3 below:
  the run instruction must state the cleanup rule.

### 6.4 Live verification and the Muse tab: as expected, no action on the fix

- Live verification is still owed by design (code/unit
  only here). The next proof is a fresh run number with a
  fresh intent/message, after redteam review. Acceptable.
- The Muse tab closed by run 2 attempt 2 is NOT
  reopened by this fix. Correct, per the brief. Recovery
  is the coordinator's decision. No action for this fix.

## 7. Conditions (numbered, for the coordinator)

- C1 (MUST, before the next live run): the prep file is
  corrected per the full stale list in section 6.1
  (lines 281, 504, 526, 536, 565, 567, 568, 569, 570,
  671, 716, 724; line 674 stays). Acceptable alternative
  when the file cannot be corrected in the window: the
  next run instruction carries an explicit stale-premise
  notice naming every stale line and stating the
  URL-substring target governs. The file correction is
  preferred, because the prep file is the durable
  procedure source.
- C2 (MUST, before the next live run): the run
  instruction names the fixed c5-zen-delegate-run2.py
  (6d751b9/f0dd5ec) as the base and forbids re-running
  c5-zen-delegate-run.py (run 1) as-is.
- C3 (MUST, in the next run instruction): on a 'not made
  current' refusal, the leftover about:blank tab is
  closed via Zen UI, never via Marionette, and the open
  is not retried in a loop.
- C4 (owed, not a gate on the code): live verification
  on a fresh run number with a fresh intent/message,
  after redteam review.
- C5 (minor, at convenience): the two _restore_original
  observations in section 5.

## 8. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received 20:17 +07, 22/11/2026. Branch
  todolist-push, HEAD at start 4dafe17.
- Tests, my runs: 16/16 OK in 0.002s; G0a 177/177 OK in
  14.201s.
- Grep, fixed files: no SCRATCH_TITLE and no `title !=
  TARGET`; 'Clone zen thread' only as SCRATCH_H1 plus one
  docstring line.
- Em/en dash: 0 in all 4 files.
- Fixture: git diff/status empty; title static line 3; JS
  line 24 sets H1 only.
- Backend: _resolve_target lines 189-208, substring over
  title/url/handle.
- Prep file grep: 'Clone zen thread' at lines 281, 504,
  526, 536, 565, 567, 568, 569, 570, 671, 674 (correct),
  716, 724.
- Run 1 grep: TARGET line 36; title uses lines 57, 64,
  67, 70, 72, 76, 357, 377.
- Driver transfer: run2.py lines 349-353, scp plus sha256
  verify.
- Push: ls-remote origin todolist-push =
  4dafe17e5c14f17fe62805de9f6084e8f1f6f85b, matches local
  HEAD.
- Review file: improvements/w-zenproof2-fix-council-3-review.md
  (this file), committed and pushed, ls-remote verified.
- No fix modified. No live run. No reviewer spawned. No
  tab opened, navigated, or deleted.
