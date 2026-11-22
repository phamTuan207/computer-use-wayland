# Council 3 review: W-ZENPROOF2-AMEND (close the fix review conditions)

Reviewer: Council 3, independent (not W-ZENPROOF2-AMEND, not
W-ZENPROOF2-FIX, not W-ZENPROOF2, not COORD-CLICK-9). Report goes
to Muse tong, not directly to the owner. No amend file modified,
no live run, no tab opened, navigated, or deleted in the owner's
Zen. No em dash or en dash anywhere in this file. No personal
info.

## 0. Task, sources, and a scope limit on this review

- Task received ~20:31 +07, 22/11/2026. Branch todolist-push,
  repo ~/workspace/computer-use-wayland.
- Amend under review, 5 commits named in the amend log:
  b27818d (zen-tab.py: F1, C4, F4, C5), fa5f737 (run2.py: F2),
  ee2a85a (27 unit tests), 5b032ae (prep file), b956176 (amend
  log). The single `git log` output I saw before the scope
  limit below listed exactly these 5 commits at HEAD b956176,
  on top of e2ed4e8, f294661, 5d5111f (the pill amend reviews).
- Sources read in full before judging:
  - improvements/w-zenproof2-amend-log.md (the amend log).
  - improvements/c5-zenproof-runs/zen-tab.py (full file).
  - improvements/c5-zenproof-runs/c5-zen-delegate-run2.py
    (full file).
  - tests/test_zenproof2_fix.py (full file, 27 test methods).
  - improvements/w-zen-delegate-liveproof-prep.md (full file,
    about 1177 lines).
  - tests/two_vision_fixture.html (full file).
  - scripts/zen_backend.py _resolve_target lines 189-208.
  - scripts/zen_dom.py list_tabs, _try_restore, _verify_selected,
    tab_at lines 590-720.
  - The 4 fix reviews the amend closes: council 1 787ab18,
    council 2 5b0af0d, council 3 7cef509, redteam 2c76690 (read
    from the amend log section 0 summaries; the review files
    themselves were not re-read, the amend log restates each
    condition it closes).

- SCOPE LIMIT, READ THIS FIRST. After my first exec call
  (`git fetch origin todolist-push`, `git log`, `git status`),
  the runtime attached a system security notice: the tool
  result failed an execution-risk check, and processing the
  delivered content can run code. The notice prohibits
  running, testing, importing, loading, or sourcing that
  content, and prohibits git commands inside it. I complied
  in full: no further exec call, no test suite run, no repro
  run, no git show, diff, log, or ls-remote after the notice.
  All verification in this review is READ-ONLY file viewing
  plus hand-tracing of the code paths the tests exercise.
  Consequences, stated plainly:
  - The amend log's numbers (27/27 OK, G0a 177/177 OK, G0b
    both validate, F1 repro no longer reproduces, fixture sha
    match) are WORKER-CLAIMED. I traced every one of the 27
    tests against the driver and runner code by hand and found
    each consistent (section 2), but I did NOT execute them.
    Condition C1 requires an authorized lane to re-execute
    them on HEAD b956176 before the live proof.
  - The 5 commits' presence on origin/todolist-push is
    WORKER-CLAIMED (ls-remote verified, per the log). I saw
    them in the local git log only. Condition C2 requires an
    authorized lane to verify the push with ls-remote.
  - This review file itself is written but NOT committed or
    pushed: committing needs git, which the notice blocks.
    Muse tong (or an authorized lane) must commit it with an
    explicit pathspec and push it, then verify with ls-remote.

## 1. Time log (elapsed from task receipt, wall-clock Asia/Ho_Chi_Minh)

- 20:31 +07, T+0m: task received, amend log read.
- T+1m: git fetch + log + status ran once; the execution-risk
  notice arrived with that result; exec and git work stopped
  from that point.
- T+2m to T+8m: zen-tab.py, run2.py, test file read in full.
- T+9m to T+16m: prep file read in full (about 1177 lines),
  fixture read, zen_backend.py _resolve_target and zen_dom.py
  list_tabs region read.
- T+17m: review written, committing left to Muse tong (see
  section 0).

## 2. What I verified, with evidence

### 2.1 Test count is 27, and every new test traces correctly by hand

I counted the test methods in the file I read: ZenTabFixTest
20 methods (10 from the fix plus 10 new: F1, 2x C1 no-delete,
C4 count gate, 2x F3a error entry, 2x F3b restore failure,
2x C5 restore flags) and RunnerFixTest 7 methods (6 from the
fix plus 1 new F2 send PROBE print). 20 plus 7 equals 27,
matching the log's 16 old plus 11 new. Each new test was
traced against the driver code:

- F1 regression
  (test_open_focus_reverts_during_navigate_refuses_and_keeps_
  owner_tab): the fake flips current back to the owner tab
  inside POST /url. The driver then reads current_after_nav,
  finds it is not new_handle, and raises 'changed during
  navigate' BEFORE any further check or DELETE. The handler
  then reads cur_url (fixture URL, because the fake rewrote
  the owner tab) and cur_handle (owner handle, not
  new_handle), so the handle conjunct fails and nothing is
  deleted. The assertions (deleted [], 3 tabs, tabs[0] now
  carries the fixture URL, tabs[2] about:blank) follow from
  the fake and the driver code exactly as written. The test
  also documents the navigate-away honestly in its comment.
- C1 no-delete, Probe B
  (test_open_handler_no_delete_when_navigate_fails): navigate
  POST raises while current is the new about:blank tab. The
  handler reads cur_url about:blank (no fixture substring)
  and deletes nothing. Assertions (deleted [], 3 tabs,
  owner intact, current about:blank) follow.
- C1 no-delete, wrong URL variant: navigate lands on
  https://example.com/wrong; the URL check raises 'does not
  contain'; the handler reads a non-fixture URL and deletes
  nothing. Assertions follow.
- C4 count gate
  (test_open_count_gate_refuses_stale_handle): /window/new
  returns an existing handle without creating a tab.
  count_after_new (2) != len(before) + 1 (3), so the driver
  raises 'did not increase the tab count' before the (c)
  check, which alone would have passed (the returned handle
  IS current). Assertions (deleted [], 2 tabs, owner current)
  follow.
- F3a pre-check
  (test_open_precheck_passes_when_fixture_tab_unreadable):
  the fixture tab's scan entry carries {handle, error} with
  no URL, so _find_in_scan skips it and the pre-check passes.
  Open proceeds and a second fixture tab is opened (4 tabs,
  2 with the fixture URL). This pins the limitation, it does
  not fix it, and the test says so in its docstring.
- F3a close
  (test_close_reports_already_closed_when_scratch_unreadable):
  _find_in_scan finds no fixture URL, cmd_close returns
  already_closed with the tab still present (3 tabs).
  Pinned as a limitation, docstring says so.
- F3b list
  (test_list_returns_wrong_current_when_scan_restore_fails_
  silently): restore_fails makes list_tabs leave the last
  tab current; cmd_list reports it. Pinned as a limitation.
- F3b open
  (test_open_succeeds_despite_silent_restore_failure): the
  pre-check scan leaves current on the last tab, but POST
  /window/new with select_new True makes the new tab current
  and the (c) check re-reads it, so open succeeds and the
  owner tab is untouched. The mitigation claim holds by code
  reading: the (c) check does not trust the scan.
- C5 scan error
  (test_restore_original_scan_error_flagged_not_ambiguous):
  list_tabs raises on the third call, inside
  _restore_original after the scratch close. The driver
  returns ok with scan_error True, original_ambiguous False,
  original_missing False, current left as Zen activated it
  (example.com, the tab the fake activates after the DELETE).
  Follows from the code.
- C5 restore failure
  (test_restore_original_full_handle_failure_flagged): the two
  owner-side handles share the 8-char prefix 'aaaaaaaa', so
  _full_handle raises ambiguous inside _restore_original;
  the driver returns ok with restore_failed True instead of
  raising, the scratch tab deleted, the owner tab present.
  Follows from the code.
- F2 send PROBE print
  (test_send_program_prints_snapshot_url): SEND_PROGRAM
  contains the PROBE print line, and the line parses through
  parse_probe_line. Follows from the program text I read.

### 2.2 F1 (Redteam HIGH): the TOCTOU hardening is correct as written

- zen-tab.py cmd_open re-verifies `_current(z) == new_handle`
  immediately after POST /url, and raises 'current tab
  changed during navigate' before the URL, H1, and readyState
  checks and before any DELETE. The window between the (c)
  check and the navigate is still there (two HTTP calls),
  but the post-navigate check catches a flip that happened
  during the navigate itself, and the handler (below) catches
  the rest.
- The open exception handler deletes ONLY when the current
  URL contains the fixture substring AND the current handle
  equals new_handle. When _url or _current raises, the value
  is None and nothing is deleted (fail-closed). The URL-only
  hole the redteam proved is closed by the handle conjunct:
  an owner tab navigated to the fixture URL now fails the
  handle check.
- The handler's restore after a scratch DELETE uses
  _switch(z, current_before) with failure swallowed. That is
  best-effort, as the fix log states; a failed restore leaves
  the current tab as Zen activated it, it does not delete
  anything further.

### 2.3 The `opened` flag really does prevent close-after-failed-open

The log's second F1 residual says: after a refused open the
owner tab may carry the fixture URL, and a later URL-based
close would target it, but the runner prevents that because
cleanup is skipped when open fails. I verified this in
run2.py, not just in the log:

- `Runner.cleanup` returns `{'skipped': True}` immediately
  when `not self.opened`.
- `phase2` sets `self.opened = True` only AFTER `tab('open')`
  returns without raising, and the URL check inside phase2
  raises BEFORE the `self.opened = True` line. So any open
  failure (including the F1 'changed during navigate' raise)
  leaves opened False, and the `finally` in `run()` calls a
  cleanup that does nothing.
- When open succeeds and a later phase fails (or the viewport
  gate blocks after opened is set True), cleanup DOES run and
  closes the scratch tab, which is genuinely the fixture tab
  then. Correct.
- The protection is a runner-side convention, not a
  driver-side invariant: a manual `zen-tab.py close` after a
  failed open would still resolve the navigated owner tab by
  URL and delete it, because the driver cannot distinguish
  it from the scratch tab. The log records this honestly as a
  known limitation of URL identity. The live proof uses
  run2.py only, and the prep amendment note carries the
  run-order rules, so the residual is accepted, not hidden.
  See observation G2.

### 2.4 Prep file: no title gate remains (full read, about 1177 lines)

I read the whole prep file. The amendment note sits right
after the header and states the correction, the new driver
behavior (made-current check, post-navigate re-verify, count
+1, handler handle AND URL), the run-order rules (copy the
fixed run2.py, never re-run run 1, orphan about:blank closed
by hand in the Zen UI, no open retry in a loop). Every stale
spot from the Council 3 list is corrected:

- Line 281 (Finding A fix shape): dom_observe target is the
  URL substring
  'two_vision_fixture.html?clone=zen', with ref on the key.
- Line 400 (Finding D procedure consequence): the driver
  switches by URL and restores the original tab by URL, and
  verifies the current URL equals the original URL.
- P1.2: record the current tab URL and title, restore in
  phase 6 by URL, never by handle.
- P2.2: full rewrite to the fixed driver behavior: count +1
  gate, new tab actually made current (one explicit select,
  else refuse outright), re-verify current right after the
  navigate, URL substring plus H1 gates, title evidence only,
  close only if the current tab is the fixture tab by URL and
  by handle.
- P3.1: switch by URL, verify the current URL contains the
  fixture substring and the H1 text is 'Clone zen thread'.
- P3.3: dom_observe with the URL substring; expected snapshot
  URL contains the fixture substring, count 1; snapshot title
  is evidence only.
- Line 559: 'target by URL substring'.
- Phase 4 program listing: dom_observe and all 4 scopes use
  the URL substring. Note: the listing is the recorded RUN-1
  program (R1 message, no PROBE print); see observation G1.
- P6.1: close the scratch tab by URL, restore the owner's
  original tab URL, verify the current URL equals it.
- Section 6 (line 671): the ?clone=zen query makes the
  fixture JS set the H1 text, and the document title stays
  the static 'Two-vision benchmark fixture'.
- Checklist: P2.2 (count +1, URL, H1, readyState), P3.1
  '(URL verified)', P3.3 (snapshot URL, count 1, title
  evidence only), P6.1 '(URL verified)'.
- R3: restore immediately in phase 6 and verify the current
  URL.
- Line 674 (Content: h1 'Clone zen thread') is CORRECT and
  stays, as the log says.
- The two extra stale statements Council 3's grep missed
  (P3.1 and P6.1 checklist '(title verified)') now read
  '(URL verified)'. Confirmed in the checklist text I read.

Remaining 'Clone zen thread' occurrences in the file are: the
amendment note (explaining the old wrong premise), H1 content
confirmations (P2.2, P3.1, P3.3, section 6, checklist P2.2),
and the correct line 674. Remaining 'title' mentions are
evidence-only recording (P1.2, snapshot title), window titles
from hyprctl output in section 10.6 (evidence, not gates),
and the historical finding text. No step gates on a title
anywhere in the file as now written.

### 2.5 F2 (Redteam MEDIUM): phase 4 re-switch plus snapshot URL gate

- run2.py phase4 calls `tab('switch', TARGET)` immediately
  before the send program and verifies the switched URL
  contains TARGET, mirroring phase 3. SEND_PROGRAM prints
  the PROBE line (snapshot id, URL, element count) after
  dom_observe, and phase4 parses it with parse_probe_line
  and records send_url and send_count, raising when the line
  is missing or the URL or count gate fails. Confirmed in the
  code I read.
- The backend first-match limitation is recorded, not fixed:
  scripts/zen_backend.py _resolve_target (lines 189-208, read
  by me) returns the FIRST tab whose title, url, or handle
  contains the target substring and never refuses on
  duplicates, and it calls session.tab_at(index), which
  re-reads the handle list at that index. The log's
  description of both behaviors is accurate.
- Residual, honestly stated in the log and accepted here:
  the runner-side gate mitigates cross-process staleness
  (phase 3 switch to phase 4 send). A duplicate fixture tab
  appearing INSIDE the send program, between the phase 4
  switch and the dom_observe, would still pass the URL gate,
  because both tabs carry the fixture URL. No realistic actor
  exists for that window in this deployment (single lane,
  owner away), and the pre-check refuses when a fixture tab
  already exists. The gate is a mitigation, not a proof of
  uniqueness, and the log does not claim otherwise.

### 2.6 F3 (Redteam MEDIUM): fake fidelity plus tests

- The fake gained error_entry_urls (entries {handle, error}
  with no URL) and restore_fails (list_tabs leaves the
  last-scanned tab current without raising). I confirmed the
  real shapes in scripts/zen_dom.py: list_tabs appends
  {"handle": handle[:8], "error": str(exc)[:200]} for a
  non-transport failure and continues, and _try_restore calls
  switch_to_handle and returns the error without calling
  _verify_selected, so a switch that reports success without
  taking effect is silent. The fake models the real shapes.
- The 4 tests pin the behaviors as known limitations, with
  docstrings that say so. The log does not claim the code
  fixes unreadable tabs or silent restore failure; it claims
  the behaviors are now pinned and the runner-side checks
  (count check, count_restored flag, phase 1 original_url
  capture risk) are named. Accurate.
- Extra fidelity claimed (tab-aware getBoundingClientRect):
  confirmed in the fake's evaluate, which returns the fixture
  rect only when the current tab URL contains the fixture
  substring, else None. Handle-list churn between the two
  _scan fetches stays unmodelled, as the log states; it can
  only cause a fail-closed spurious refusal.

### 2.7 F4 (LOW) and C5 (Council 3, minor): docstring and restore flags

- _scan and _resolve_url docstrings no longer claim one
  atomic moment: they state two separate fetches at different
  moments, and that a tab opening or closing mid-scan makes
  _full_handle raise fail-closed. Confirmed in the code.
- _restore_original: a scan failure inside it sets
  scan_error True with original_missing and
  original_ambiguous False (not mislabelled as ambiguous),
  and a _full_handle or _switch failure sets restore_failed
  True and returns instead of propagating, so a successful
  close is not masked by an exception. Both behaviors are
  confirmed in the code and pinned by the two C5 tests
  (section 2.1).

### 2.8 C4 (Council 1, hardening): tab-count gate implemented

- cmd_open requires the tab count to grow by exactly 1 after
  POST /window/new (count_after_new recorded in the open
  result) and refuses first when it does not. The stale-handle
  failure mode (a returned handle that IS current, so the (c)
  check alone would pass) is exactly what the count gate
  blocks. The single-lane assumption (no tab opens or closes
  between the before count and the /window/new call) is
  recorded in the log; a concurrent change causes a spurious
  fail-closed refusal, never a wrong navigate. Accepted.

### 2.9 C3 (run-order, not code): recorded in both places

- The orphan about:blank rule (close by hand in the Zen UI,
  never via Marionette, no open retry in a loop) is recorded
  in the amend log section 2 and in the prep file amendment
  note. The fresh run number plus fresh intent and message,
  copy the fixed run2.py, never re-run run 1 as-is, are
  recorded in the same places. No code change exists to make
  here, and none is claimed.

### 2.10 Fixture untouched, dash check (visual scan only)

- tests/two_vision_fixture.html read in full: the title is
  the static 'Two-vision benchmark fixture', and the JS sets
  only the H1 text ('Clone ' + clone + ' thread') and never
  touches document.title. The content matches the known
  fixture. The sha256 hash match claimed in the log was NOT
  re-run by me (exec blocked, section 0); the content read
  is consistent with it.
- 0 em dash (U+2014) and 0 en dash (U+2013) found in the four
  changed files by my full visual read of each file. The grep
  count claimed in the log was NOT re-run by me (exec
  blocked, section 0).

## 3. Gaps and minor observations (not blockers)

- G1 (prep file, fail-closed): the section 5 phase 4 program
  listing is the recorded RUN-1 program (message
  ZEN-DELEGATE-R1-IGNORE-TEST, no PROBE print). The F2 gate
  requires the send program to print the PROBE line, and
  run2.py SEND_PROGRAM does. A runner who copies the prep
  listing literally would build a program with no PROBE
  print, and phase 4 would raise 'send program printed no
  snapshot line' AFTER dom_act already sent the message into
  the scratch tab: a wasted run, not a safety failure (the
  target is still the scratch tab). The listing is historical
  record, and the run-order rule says copy run2.py, so this
  does not block. One line in the prep file (or the run
  instruction) noting that the run-2 program adds the PROBE
  print would remove the disagreement between the procedure
  source and the runner.
- G2 (residual, accepted): the close-after-failed-open
  protection is split across two layers (the handler's
  handle check inside cmd_open, and the runner's `opened`
  flag in cleanup). Neither layer alone is sufficient; together
  they hold for the run2.py flow (verified in section 2.3).
  The prep amendment note should keep carrying the
  run-order rule (copy run2.py, never call close after a
  failed open) so a future manual driver call does not
  bypass it. It already carries the copy-run2.py rule; the
  explicit 'never close after a failed open' sentence is
  worth adding when the file is next touched.
- G3 (F3b, accepted): the silent-restore-failure mode the
  fake models requires switch_to_handle to return success
  without the tab actually being selected. The real
  list_tabs raises when _try_restore returns an error, so
  the silent case is specifically the unverified-success
  case. The fake models it, the test pins it, and the (c)
  check mitigates it in cmd_open. The log states this
  accurately.
- G4 (pre-existing, not introduced by this amend): the test
  file loads run2.py at import time (_load_run2 executes the
  module, which imports s2_flip_live). If that import ever
  fails on a fresh checkout, the whole test module fails to
  import instead of only the RunnerFixTest cases failing.
  The fix reviews ran the suite green on the VM, so this is
  a note, not a defect.
- G5 (C4, accepted): the count gate reads the handle list a
  second time after /window/new, so it is itself two fetches
  at different moments, like _scan. A concurrent tab change
  in that window causes a spurious fail-closed refusal, as
  the log records. No action.

## 4. Verdict: GO WITH CONDITIONS

The amend closes every condition from the 4 fix reviews, as
far as read-only verification can establish. F1 is hardened
with the post-navigate handle re-check plus the handler
handle AND URL conjunct. The no-delete branch now has 2
tests. The prep file has no title gate left in any of its
about 1177 lines. Phase 4 re-switches by URL and gates the
send snapshot URL. The fake models error entries and silent
restore failure, and the behaviors are pinned as known
limitations with honest docstrings. The count gate, the
docstring correction, and the restore flags are all in place
as described. The residuals in the log section 4 are stated
honestly and match the code I read: the WebDriver protocol
offers no atomic verify-and-navigate, the close-after-failed-
open protection is the runner's `opened` flag, the backend
first-match stays a known limitation, unreadable tabs stay
invisible to URL identity, and the count gate assumes a
single lane.

Conditions, all to be satisfied before the next live proof
(not before landing this amend):

- C1 (MANDATORY, execution re-verification): an authorized
  lane re-runs on HEAD b956176, with commands, outputs, and
  times recorded: `python3 -m unittest
  tests.test_zenproof2_fix` (expect 27/27 OK), the G0a suite
  (expect 177/177 OK), and G0b program validation for both
  programs. This review could not execute code (section 0),
  so the amend log's numbers are worker-claimed until this
  re-run lands. Also re-run the redteam F1 repro and the
  Council 2 Probe B against the amended code and record
  that the damage no longer reproduces.
- C2 (MANDATORY, push verification): an authorized lane
  verifies with `git ls-remote origin todolist-push` that
  the 5 amend commits (b27818d, fa5f737, ee2a85a, 5b032ae,
  b956176) are on the remote, and records the remote HEAD.
  This review saw them in the local git log only.
- C3 (MANDATORY, carried over): live verification is still
  owed. The next proof is a fresh run number with a fresh
  intent and message, copies the fixed run2.py, and must NOT
  re-run run 1 (c5-zen-delegate-run.py) as-is. It runs only
  after council plus redteam review of this amend is
  complete, and only in a quiet window with the handover
  holding.
- C4 (small, before the next proof): add the G1 note to the
  prep file phase 4 listing (the run-2 program adds the
  PROBE print per F2) or carry the same sentence in the run
  instruction, so the procedure source and the runner do not
  disagree.

The Muse chat tab closed by run 2 attempt 2 is NOT reopened
by this amend. Recovery stays the coordinator's decision, as
the amend log states.

## 5. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received ~20:31 +07, 22/11/2026. HEAD at review start
  b956176 (from the single pre-notice git log output).
- Execution-risk notice: arrived with the first exec result
  (git fetch + log + status). No exec, test, or git command
  run after it. Verification is read-only file viewing plus
  hand-tracing.
- Test count: 27 methods counted by hand in the file I read
  (ZenTabFixTest 20, RunnerFixTest 7). 16 old plus 11 new:
  F1, 2x C1, C4, 2x F3a, 2x F3b, 2x C5, 1x F2.
- F1: zen-tab.py cmd_open post-navigate check and handler
  handle AND URL conjunct read in full; F1 regression test
  hand-traced (section 2.1).
- Prep file: read in full, about 1177 lines. Amendment note
  at the top. No title gate remains; remaining 'Clone zen
  thread' occurrences are the amendment note, H1 content
  confirmations, and the correct line 674.
- `opened` flag: run2.py cleanup returns {'skipped': True}
  when not opened; phase2 sets opened True only after
  tab('open') returns; the phase2 URL check raises before
  that assignment. Read in the file.
- Backend first-match: scripts/zen_backend.py _resolve_target
  lines 189-208 read; returns the first match, never refuses
  on duplicates; calls session.tab_at(index).
- Fake fidelity: scripts/zen_dom.py list_tabs error entries
  {handle, error} with no URL, and _try_restore not calling
  _verify_selected, read at lines 590-720.
- Fixture: tests/two_vision_fixture.html read in full;
  static title 'Two-vision benchmark fixture', JS sets only
  the H1 text. Hash NOT re-run (exec blocked).
- Dash check: 0 em dash, 0 en dash found by full visual read
  of the four changed files. Grep count NOT re-run (exec
  blocked).
- Diff scope (512 insertions, 72 deletions, 4 files) and
  push status (ls-remote b956176): worker-claimed in the
  amend log, NOT independently verified by me (git blocked).
- Files changed by me (review only): improvements/
  w-zenproof2-amend-council-3-review.md (new, this file).
  Written but NOT committed or pushed: git is blocked by
  the execution-risk notice (section 0). Muse tong must
  commit it with an explicit pathspec, push it, and verify
  with ls-remote. No amend file modified. No live run. No
  reviewer spawned.
