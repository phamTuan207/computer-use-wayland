# W-ZENPROOF2-AMEND: close the review conditions on W-ZENPROOF2-FIX

Owner: Pham Tuan. Worker: W-ZENPROOF2-AMEND, independent (not
W-ZENPROOF2-FIX, not W-ZENPROOF2, not COORD-CLICK-9). Report goes
to Muse tong, not directly to Pham Tuan. No live proof re-run, no
tab opened, navigated, or deleted in Pham Tuan's Zen. All
verification is code/unit level only. No em dash or en dash
anywhere in this file. No personal info.

## 0. Task receipt and sources (20:24 +07, 22/11/2026)

- Task received ~20:24 +07. T+0m. Branch todolist-push, repo
  ~/workspace/computer-use-wayland. HEAD at start 2c76690
  (redteam review of the fix).
- The fix under amendment (4 commits): 6d751b9 (zen-tab.py),
  f0dd5ec (run2.py), 014938b (16 unit tests), 4dafe17 (fix log).
  All 4 reviews GO WITH CONDITIONS:
  - Council 1, 787ab18: 4 conditions (C1 prep file, C2 fresh
    run number after redteam review, C3 orphan about:blank
    closed by hand in the Zen UI, C4 tab-count gate hardening).
  - Council 2, 5b0af0d: 2 conditions (1: no-delete branch test,
    2: prep file per the Council 3 list).
  - Council 3, 7cef509: 5 conditions (C1 prep file per the full
    stale list, C2 run order names the fixed run2.py and forbids
    run 1, C3 orphan about:blank rule in the run instruction,
    C4 live verification owed, C5 two _restore_original
    observations).
  - Redteam, 2c76690: 3 conditions (C1 F1 TOCTOU hardening plus
    regression test, C2 F2 phase 4 re-switch plus snapshot URL
    gate, C3 F3 fake fidelity plus tests).
- Sources read before any edit: all 4 reviews in full, the fix
  log, the current zen-tab.py, run2.py, and test file, the prep
  file (grep for 'Clone zen thread' plus the full 'title' grep),
  scripts/zen_dom.py list_tabs/_try_restore/_verify_selected/
  tab_at (lines 590-720), scripts/zen_backend.py
  _resolve_target (lines 189-208, read for the known-limitation
  note only, not changed).
- Probe templates reused (read, not trusted blindly):
  /tmp/redteam-repro-f1.py, /tmp/redteam-repro-f2.py,
  /tmp/zenproof2_council2_probe.py. All three still existed.

## 1. Time log (wall-clock Asia/Ho_Chi_Minh)

- 20:24 +07, T+0m: task received, 4 reviews + fix log read.
- 20:26 +07, T+2m: code + prep file + zen_dom.py read; baseline
  confirmed (16/16 OK; F1 repro still deletes the owner tab on
  the unamended code; Council 2 Probe B confirms the no-delete
  branch works but is untested).
- 20:28 +07, T+4m: zen-tab.py amended (F1, C4, F4, C5).
- 20:29 +07, T+5m: run2.py amended (F2).
- 20:30 +07, T+6m: test file amended (fake extensions + 11 new
  tests). Full suite 27/27 OK; F1 repro no longer reproduces
  the damage; G0a 177/177 OK; G0b both programs validate.
- 20:31 +07, T+7m: prep file corrected (amendment note + all
  stale title-gated steps). Log written, committing.

## 2. What was closed, condition by condition

### F1 (Redteam HIGH, mandatory before live proof): TOCTOU closed

- zen-tab.py cmd_open: after POST /url, the current tab is
  re-verified against new_handle. A focus change between the
  (c) check and the navigate now raises 'current tab changed
  during navigate (current %s != new %s); refusing' BEFORE any
  further check or DELETE.
- zen-tab.py open exception handler: DELETE now requires the
  current handle == new_handle AND the current URL containing
  the fixture substring. A URL-only check would delete an owner
  tab navigated to the fixture URL (it IS the fixture tab by
  URL); the handle check is what saves it. When _url or
  _current raises, the corresponding value is None and nothing
  is deleted (fail-closed).
- Regression test added (test_open_focus_reverts_during_navigate_
  refuses_and_keeps_owner_tab, adapted from
  /tmp/redteam-repro-f1.py): the fake flips current back to the
  owner tab inside POST /url. Open raises 'changed during
  navigate', zero deletions, 3 tabs, the owner tab survives,
  the new tab is left as an un-navigated about:blank.
- The redteam repro itself was re-run against the amended code:
  it now dies at cmd_open with 'current tab changed during
  navigate (current c5e20798 != new 98677310); refusing' and
  never reaches cmd_close. The damage no longer reproduces.
- Residual risk, recorded honestly: the WebDriver protocol
  offers no atomic verify-and-navigate, so a focus change
  AFTER the post-navigate check could still in principle land
  a later check on the wrong tab. The hardening narrows the
  window to detection plus damage limitation (navigate-away at
  worst, never a delete through the handler). There is no
  realistic actor for the race in this deployment (owner away,
  one lane, no other Marionette session), same assessment as
  the redteam review.
- Second residual, recorded: after a refused open, the owner
  tab may carry the fixture URL (navigate-away). A later
  URL-based close would then target it, because URL identity
  cannot distinguish it from the scratch tab. The runner is
  what prevents that: cleanup is skipped when open fails
  (opened stays False in run2.py), so close is never called
  after a failed open. This is a known limitation of URL
  identity, not a hole in the handler.

### C1 (Council 2 condition 1): no-delete branch tested

- Two tests added. test_open_handler_no_delete_when_navigate_
  fails (Probe B template): the navigate POST raises while the
  current tab is the new about:blank tab; zero deletions, 3
  tabs, owner tab intact, current is about:blank.
- test_open_handler_no_delete_when_navigate_lands_wrong_url
  (the URL-gate variant Council 2 named): the navigate lands
  on https://example.com/wrong; the URL check raises 'does not
  contain'; zero deletions, 3 tabs, owner tab intact.

### Prep file (Council 1 C1, Council 2 condition 2, Council 3 C1): corrected

- improvements/w-zen-delegate-liveproof-prep.md: an amendment
  note was added after the file header (date, worker, what
  changed, why, and the run-order rules). Every stale
  title-gated step was corrected to the URL-substring target:
  - Line 281 (Finding A proposed fix shape): dom_observe target
    is now the URL substring.
  - Line 400 (procedure consequence): the driver verifies the
    current URL, and restores the original tab by URL.
  - P1.2: record the current tab URL and title (restore in
    phase 6 by URL, never by handle: handles are ephemeral per
    session).
  - P2.2: full rewrite to the fixed driver behavior: count +1
    gate, new tab actually made current (one explicit select,
    else refuse outright), re-verify current right after the
    navigate, URL substring + H1 gates, title evidence only,
    close only if the current tab is the fixture tab by URL and
    by handle.
  - P3.1: switch by URL, verify the current URL contains the
    fixture substring and the H1 text is 'Clone zen thread'.
  - P3.3: dom_observe with the URL substring; expected snapshot
    URL contains the fixture substring, count 1; snapshot title
    is evidence only.
  - Line 559: 'target by title substring' is now 'target by URL
    substring'.
  - Phase 4 program listing (lines 565-570): dom_observe and all
    4 scopes now use the URL substring. The R1 message text is
    unchanged (it is the recorded run 1 program).
  - P6.1: close the scratch tab by URL, restore the owner's
    original tab URL, verify the current URL equals it.
  - Section 6 (line 671): the ?clone=zen query makes the
    fixture JS set the H1 text (the document title stays the
    static 'Two-vision benchmark fixture').
  - Checklist: P2.2 (count +1, URL, H1, readyState), P3.1 (URL
    verified), P3.3 (snapshot URL, count 1, title evidence
    only), P6.1 (tab count back, URL verified).
  - R3: restore and verify the current URL.
  - Line 674 (Content: h1 'Clone zen thread') is CORRECT and
    stays. The remaining 'Clone zen thread' occurrences in the
    file are all H1 content confirmations or the amendment note.
- Two further stale title statements the Council 3 grep missed
  (they carry no 'Clone zen thread' literal) were fixed in the
  same pass: P3.1 checklist '(title verified)' and P6.1
  checklist '(title verified)' are now '(URL verified)'.
- Verified after the edit: grep for 'Clone zen thread' returns
  only the amendment note, H1 content confirmations, and the
  correct line 674. The remaining 'title' mentions are
  evidence-only recording (P1.2, snapshot title) or window
  titles from hyprctl output, never gates.

### F2 (Redteam MEDIUM): phase 4 re-switch plus snapshot URL gate

- run2.py SEND_PROGRAM now prints the PROBE line (snapshot id,
  URL, element count) after dom_observe, same shape as the
  probe program.
- run2.py phase4 now calls tab('switch', TARGET) immediately
  before the send program and verifies the switched URL
  contains TARGET (mirror of phase 3). It then parses the
  send program's PROBE line with parse_probe_line and records
  send_url / send_count in the run results, raising when the
  line is missing or the URL/count gate fails.
- Test added (test_send_program_prints_snapshot_url): the PROBE
  print is present in SEND_PROGRAM and parses through
  parse_probe_line.
- Backend first-match recorded as a known limitation (no backend
  change, by design): scripts/zen_backend.py _resolve_target
  returns the FIRST tab whose title, url, or handle contains
  the target substring and never refuses on duplicates, and
  tab_at re-reads the list at the resolved index, so a tab
  closing between the two scans shifts the index and returns
  the wrong tab without re-checking (redteam repro F2 parts A
  and B, both confirmed by the redteam review). The runner-side
  gate (phase 4 re-switch plus snapshot URL gate) is the
  mitigation: a send can only go to the tab the switch just
  selected and the snapshot just confirmed. The backend change
  (refuse on ambiguity) stays a future option, not this amend.

### F3 (Redteam MEDIUM): fake fidelity plus tests

- FakeSession gained error_entry_urls (tabs whose list_tabs
  entries carry {handle, error} with no URL, exactly like the
  real list_tabs in scripts/zen_dom.py) and restore_fails (a
  list_tabs whose restore leaves the last-scanned tab current
  without raising, because _try_restore does not verify the
  switch took effect).
- Four tests added, all pinning behavior as known limitations
  where the code cannot do better:
  - test_open_precheck_passes_when_fixture_tab_unreadable: the
    pre-check cannot see an unreadable fixture tab, so open
    proceeds and a second fixture tab is opened (two tabs with
    the fixture URL, one unreadable). Only the runner's count
    check would notice the extra tab.
  - test_close_reports_already_closed_when_scratch_unreadable:
    cmd_close cannot find the scratch tab by URL and reports
    already_closed while the tab still exists. The runner's
    count_restored flag is what detects the mismatch.
  - test_list_returns_wrong_current_when_scan_restore_fails_
    silently: cmd_list reports the last-scanned tab as current.
    The runner's phase 1 original_url capture would take the
    wrong tab's URL in that state.
  - test_open_succeeds_despite_silent_restore_failure: the (c)
    check mitigates the silent restore failure in cmd_open (it
    re-reads current after /window/new), so open succeeds and
    the owner tab is untouched.
- Extra fidelity, not a condition: the fake's
  getBoundingClientRect is now tab-aware (returns the fixture
  rect only when the current tab URL contains the fixture
  substring, else None). The H1 read already was. readyState
  and metrics stay canned (real pages are complete and have
  viewports; the rect is the discriminating read). Handle-list
  churn between the two _scan fetches stays unmodelled (F3d);
  it can only cause a fail-closed spurious refusal.

### F4 (Redteam LOW): _scan docstring corrected

- zen-tab.py _scan docstring no longer claims the entries and
  the handle list come from one moment: they are two separate
  fetches at different moments (list_tabs fetches handles at
  its own start, switches through tabs, restores; _handles
  fetches the list again after). A tab opening or closing
  mid-scan makes _full_handle raise (fail-closed). The same
  correction was applied to the _resolve_url docstring.

### C5 (Council 3, minor): _restore_original observations fixed

- Observation 1: a scan failure inside _restore_original is
  now reported as scan_error, not original_ambiguous. Test
  added (test_restore_original_scan_error_flagged_not_
  ambiguous): the scan fails on the third list_tabs call
  (inside _restore_original, after the scratch close
  succeeded); cmd_close returns ok with scan_error True,
  original_ambiguous False, original_missing False, current
  left as Zen activated it (example.com).
- Observation 2: a _full_handle or _switch failure inside
  _restore_original is now reported as restore_failed and
  returns, instead of propagating out of cmd_close. Test added
  (test_restore_original_full_handle_failure_flagged): the
  original tab's handle prefix is ambiguous in the full handle
  list; cmd_close returns ok with restore_failed True, the
  scratch tab deleted, the owner tab present. The runner
  records the outcome (original_restored False) instead of the
  close success being masked by an exception.

### C4 (Council 1, hardening): tab-count gate implemented

- zen-tab.py cmd_open now requires the tab count to grow by
  exactly 1 after POST /window/new (count_after_new recorded
  in the open result). If /window/new ever returned a stale or
  existing handle, the (c) check alone would pass on the wrong
  tab; the count gate refuses first.
- Test added (test_open_count_gate_refuses_stale_handle): POST
  /window/new returns an existing handle without creating a
  tab; open raises 'did not increase the tab count', zero
  deletions, 2 tabs, owner tab still current.
- Assumption recorded: no tab opens or closes between the
  `before` count and the /window/new call (single lane, owner
  away). A concurrent tab change would cause a spurious
  fail-closed refusal, never a wrong navigate.

### C3 (Council 1 + Council 3, run-order, not code): recorded

- No code change (there is none to make: the select that would
  let the driver close the leftover tab is exactly what
  failed). Recorded here and in the prep file amendment note:
  after any run that hits the 'not made current' refusal, the
  coordinator closes the leftover empty about:blank tab by hand
  in the Zen UI, never via Marionette, and does not retry the
  open in a loop. The pre-check refuses only on a fixture URL
  tab, not on an about:blank tab, so leftovers would otherwise
  accumulate across refused runs.
- Run-order rules recorded in the same place: the next proof is
  a fresh run number with a fresh intent/message, copies the
  fixed run2.py, and must NOT re-run run 1 (c5-zen-delegate-
  run.py) as-is. Run 1 is now doubly dead: old title premise
  AND old handle-based driver calls the fixed driver refuses.

## 3. Verification (code/unit only, no live tab operation)

- py_compile OK for zen-tab.py, run2.py, and the test file.
- New tests tests/test_zenproof2_fix.py: 27/27 OK
  (python3 -m unittest tests.test_zenproof2_fix, 0.003s).
  16 old tests still pass unchanged; 11 new tests added (F1,
  2x C1 no-delete, C4 count gate, 2x F3a error entry, 2x F3b
  restore failure, 2x C5 restore flags, 1x F2 send PROBE
  print).
- G0b: both programs pass code_exec.validate_program with no
  exception (PROBE validates, SEND validates), same check the
  run used.
- G0a suite still passes: python3 -m unittest
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec, Ran 177 tests, OK (12.569s).
- Redteam F1 repro re-run against the amended code: cmd_open
  raises 'current tab changed during navigate (current
  c5e20798 != new 98677310); refusing' at zen-tab.py:241, the
  repro dies before cmd_close, no owner-tab delete. The damage
  no longer reproduces.
- Council 2 Probe B re-run (read-only, /tmp): still confirms
  the no-delete branch works; it is now also covered by a
  suite test.
- 0 em dash (U+2014) and 0 en dash (U+2013) in all four
  changed files (zen-tab.py, run2.py, test file, prep file),
  counted by grep.
- Fixture untouched: sha256 of tests/two_vision_fixture.html
  is 147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6
  cbf, identical to FIXTURE_SHA.
- NOT verified (needs a live run, out of scope for this
  worker): the amended runner against real Zen. The next proof
  is a fresh run number with a fresh intent/message, after
  council + redteam review of this amend.

## 4. Open items for the coordinator (not fixed here)

- Live verification is still owed by design (code/unit only
  here). The next proof is a fresh run number with a fresh
  intent/message, after council + redteam review of this amend.
  It copies the fixed run2.py; run 1 must not be re-run as-is.
- The Muse chat tab closed by run 2 attempt 2
  (https://muse.ai/thread/750c8dae-58fb-4a65-82ac-753e78d6ce93)
  is NOT reopened by this amend. Recovery is the coordinator's
  decision (w-zenproof2-log.md section 11, item 1).
- Known limitations recorded in section 2 (F1 residual race,
  F1 close-after-failed-open, F2 backend first-match, F3a
  unreadable tabs, F3b cmd_list current, C4 single-lane
  assumption). None of them is a live-run gate beyond what the
  reviews already stated, but the coordinator should carry
  them into the run instruction where noted (C3 orphan-tab
  rule, fresh run number, fixed run2.py only).

## 5. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received ~20:24 +07, 22/11/2026. Branch todolist-push,
  HEAD at start 2c76690. Fetched origin before committing;
  local HEAD already equalled origin/todolist-push.
- Baseline 20:26 +07: 16/16 OK; F1 repro on unamended code
  deleted the owner tab (owner tab still present False);
  Council 2 Probe B confirmed the no-delete branch works.
- zen-tab.py edits 20:28 +07: py_compile OK after edit.
- run2.py edits 20:29 +07: py_compile OK after edit.
- Tests 20:30 +07: python3 -m unittest
  tests.test_zenproof2_fix, Ran 27 tests in 0.003s, OK.
- G0a 20:30 +07: Ran 177 tests in 12.569s, OK.
- G0b 20:30 +07: PROBE validates, SEND validates.
- F1 repro re-run 20:30 +07: raises 'current tab changed
  during navigate (current c5e20798 != new 98677310);
  refusing' at zen-tab.py:241; no cmd_close reached.
- Fixture sha 20:30 +07:
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6
  cbf, matches FIXTURE_SHA.
- Dash counts 20:30 +07: U+2014 0, U+2013 0 in all four
  changed files.
- Prep file grep after edit: 'Clone zen thread' only as H1
  content confirmations, the amendment note, and the correct
  line 674; no title gate remains.
- Diff scope: 4 files, 512 insertions, 72 deletions
  (zen-tab.py +106, run2.py +27, test file +305, prep file
  +146 net of rewrites). The pre-existing dirty
  tests/realistic/clone1-batch3/results.json was never touched
  and is never committed by me.
- Files changed (mine only, explicit pathspecs):
  improvements/c5-zenproof-runs/zen-tab.py,
  improvements/c5-zenproof-runs/c5-zen-delegate-run2.py,
  tests/test_zenproof2_fix.py,
  improvements/w-zen-delegate-liveproof-prep.md,
  improvements/w-zenproof2-amend-log.md (new, this file).
- Commits, pushed, ls-remote verified: (hashes in the report
  to Muse tong).
- No live Zen tab was opened, navigated, or deleted. No proof
  re-run. No reviewer spawned (Muse tong spawns council +
  redteam after this).
