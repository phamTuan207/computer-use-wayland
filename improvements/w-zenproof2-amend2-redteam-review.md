# Redteam review: W-ZENPROOF2-AMEND2 (H1 membership check + H2 guarded restore reads)

Reviewer: Redteam, independent (not W-ZENPROOF2-AMEND2, not
W-ZENPROOF2-AMEND, not W-ZENPROOF2-FIX, not W-ZENPROOF2, not
COORD-CLICK-9). Report goes to Muse tong, not directly to Pham
Tuan. No amend modified, no live run, no tab opened, navigated,
or deleted in Pham Tuan's Zen. All verification is code/unit
level only, plus my own re-runs and my own attack probes against
fake sessions. No em dash or en dash anywhere in this file. No
personal info.

## 0. Task and sources (20:39 +07, 22/11/2026)

- Task received ~20:39 +07. Branch todolist-push, repo
  ~/workspace/computer-use-wayland. The 4 amend commits:
  - e9994d9 zen-tab.py: H1 membership check, H2 _safe_title_url.
  - d8f8ac3 tests/test_zenproof2_fix.py: 36 tests (9 new).
  - 16075f6 prep file: recovery line + G1 note.
  - bcc249c improvements/w-zenproof2-amend2-log.md: amend log.
- Sources read before judging:
  - improvements/w-zenproof2-amend2-log.md (the amend log,
    in full).
  - Full diff of e9994d9, d8f8ac3, and 16075f6 (read line by
    line, not skimmed), and the current zen-tab.py cmd_open,
    cmd_close, _restore_original, _safe_title_url.
  - improvements/c5-zenproof-runs/c5-zen-delegate-run2.py
    phase4 (lines 483-525) and cleanup (lines 560-600).
  - scripts/zen_dom.py _wd (lines 537-567) and list_tabs
    (lines 647-720).
  - improvements/w-zenproof2-log.md section 6 (the run 2
    incident and the handle ephemerality finding).
  - improvements/w-zenproof2-amend2-council-1-review.md
    (commit ccaa056, read in full before writing this
    review).
  - /tmp/redteam-amend-repro-h1.py (read in full).
  - My own attack probes, /tmp/redteam-amend2-probes.py
    (written by me from the review descriptions, run by me).

## 1. Time log (wall-clock Asia/Ho_Chi_Minh)

- 20:39 +07, T+0m: task received, log + diff stat read.
- 20:40 +07, T+1m: zen-tab.py diff + test diff read in full.
- 20:41 +07, T+2m: suite 36/36 re-run by me; G0a 177/177
  re-run by me; G0b re-run by me; fixture sha; dash counts.
- 20:42 +07, T+3m: zen_dom _wd and list_tabs read; run-2 log
  section 6 re-read; attack probes written and run (P-A to
  P-E); P-C corrected and re-run.
- 20:44 +07, T+5m: Council 1 amend-2 review read in full;
  convergence checked.
- 20:46 +07, T+7m: review written, committing.

## 2. What I verified independently (not trusting the log)

- Diff scope: 4 files, 570 insertions, 16 deletions
  (e9994d9 zen-tab.py 47+/11-, d8f8ac3 test file 205+/4-,
  16075f6 prep file 14+/1-, bcc249c log 304+). run2.py was
  NOT changed by this amend. No shared library touched.
  The 4 amend commits are on origin (ancestors of remote
  HEAD ccaa056, verified by merge-base).
- Suite, re-run by me 20:41 +07: python3 -m unittest
  tests.test_zenproof2_fix, Ran 36 tests in 0.006s, OK.
- G0a, re-run by me 20:41 +07: Ran 177 tests in 12.628s, OK.
- G0b, re-run by me 20:41 +07: code_exec.validate_program
  passes for PROBE_PROGRAM and SEND_PROGRAM (returns an
  ast.Module, no exception).
- Fixture untouched: sha256
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6
  cbf, matches FIXTURE_SHA.
- 0 em dash (U+2014) and 0 en dash (U+2013) in all 4 files,
  counted by me.
- H1 single-lane case: the amend-1 H1 repro no longer
  reproduces (the two new suite tests pass in my run:
  test_open_refuses_stale_handle_that_creates_tab, line 534,
  and test_open_refuses_stale_handle_that_creates_tab_no_
  select, line 554; both assert the raise, zero deletions,
  3 tabs, owner tab URL unchanged).
- H2: I verified all FOUR _restore_original branches with
  failed reads (my probes B2, B3, B4), not just the
  scan_error branch the amend's own test covers. All four
  call sites (lines 457, 470, 480, 482) go through
  _safe_title_url (lines 417-435). B2 (original missing +
  reads fail): ok True, original_missing True, reads None.
  B3 (restore_failed via ambiguous prefix + reads fail):
  ok True, restore_failed True, reads None, scratch gone,
  owner present. B4 (success path + reads fail): ok True,
  reads None, current_handle recorded. H2 is complete.
- _wd converts every transport failure to ZenDomError
  (scripts/zen_dom.py lines 537-567: HTTPError,
  TimeoutError, OSError, URLError, HTTPException,
  ValueError, malformed responses), and list_tabs raises
  ZenDomError only (lines 647-720: per-handle failures
  become error entries or a wedge ZenDomError, restore
  failure becomes ZenDomError). So the except
  ZenDomError guards around _scan and _switch inside
  _restore_original are complete for realistic failures,
  and the reads are guarded more broadly anyway.
- The other _title(z) / _url(z) calls in zen-tab.py are
  outside _restore_original and cannot mask a close:
  lines 182-183 (pre-check, nothing deleted yet),
  272 and 286 (navigate checks), 344 (open handler,
  already wrapped in try/except), 369-370 and 378
  (cmd_switch / cmd_eval returns, no DELETE in those
  paths). Verified by grep + reading.
- The old C4 test update is legitimate, not
  test-cheating: the membership check subsumes the
  stale-handle case, so the old test now expects the
  'existing handle' message, and a dedicated count-gate
  test covers the genuinely-new-handle-no-tab case.
  Coverage is preserved, not removed.
- Prep file: the recovery line (Council 1 C1) and the G1
  note (phase-4 listing is the run-1 program) are present
  as described, verified in the diff.
- H3 wording: the amend-2 log corrects the F2 gate to
  detection-only and names the real guards. The amend-1
  log is untouched as a committed historical record.
  Correct handling.

## 3. Holes I found

### H1 (MEDIUM): concurrent open + close defeats the membership check and the count gate

- The membership check (zen-tab.py line 206) compares
  new_handle against `before`, captured at cmd_open start.
  The count gate (lines 216-217) requires the count to
  grow by exactly 1. A tab X opening after `before` AND
  another tab closing in the same window gives net +1,
  and if POST /window/new returns X's handle (the H1 bug),
  both gates pass. The (c) check then explicitly selects
  X, the navigate rewrites X to the fixture URL, the F1
  post-navigate check passes (current == new_handle, both
  X), URL and H1 pass, cmd_open returns ok, and cleanup
  close by URL DELETEs X.
- Repro: /tmp/redteam-amend2-probes.py P-C, corrected
  re-run by me. Output: cmd_open ok True; the X tab URL
  is now the fixture URL, title 'Two-vision benchmark
  fixture', current True; cleanup close ok True; tabs left
  are the owner Muse tab and the empty about:blank scratch
  tab (X deleted). The first version of the probe looked
  the X tab up by title and missed it, because the
  navigate rewrites the title too; the corrected version
  checks by position and confirms the hijack.
- Trigger: needs concurrent tab churn (forbidden by the
  run rules: single lane, quiet window, owner away) AND
  the H1 bug (unobserved, hypothetical). So practical
  exposure in the actual deployment is low. But the
  bypass is real, and the amend-2 log section 4 claim is
  overstated: "a concurrent tab change causes a spurious
  fail-closed refusal, never a wrong navigate". The
  open+close pair plus a stale-handle return CAN wrongly
  navigate. The wording must be corrected.
- Fix (small, fail-closed): after POST /window/new, keep
  the handle LIST from the count fetch (not just its
  length) and require the set difference against `before`
  to be exactly {new_handle} added and nothing removed:
  set(after) - set(before) == {new_handle} and
  set(before) - set(after) == empty. Use `before`, not
  the pre-check scan's handle list: if the concurrent
  change happens between `before` and the scan, the
  scan already contains X, so a difference against the
  scan would miss it; against `before`, every ordering
  is caught. This check also independently catches the
  H1 stale-handle case (new = {scratch} != {new_handle})
  and turns the P-A re-mint case below into a fail-closed
  refusal. Keep the membership check and the count gate
  as defense in depth with distinct error messages; they
  give the clearest diagnosis for their own cases. Add
  a P-C regression test (concurrent open+close plus
  stale-handle return refuses, owner tab intact, zero
  deletions). Or the coordinator records written risk
  acceptance. The check assumes handles are stable
  within one cmd_open invocation, the same assumption
  the membership check already makes; tab loading
  changes title and URL, not the window handle, so it
  should not cause false refusals, and any false refusal
  is fail-closed (safe).

### H2 (LOW): within-session handle re-mint bypasses the membership check

- The membership check is the only check comparing
  fresh-vs-stale (new_handle vs `before`). The (c)
  check (lines 230, 235), the F1 post-navigate check
  (line 256), and the handler handle check all compare
  fresh-vs-fresh (current vs new_handle). If the owner
  tab's handle were re-minted between the `before`
  fetch and the /window/new response, and /window/new
  returned the owner tab's NEW handle, the membership
  check would pass (new handle not in `before`), the
  (c) check would pass (current == new_handle, both the
  owner tab), the navigate would rewrite the owner tab,
  the F1 check would pass, and cleanup would delete the
  owner tab.
- Repro: /tmp/redteam-amend2-probes.py P-A, both modes.
  Output: select_new=True and select_new=False both
  cmd_open RETURNED ok, owner tab URL now the fixture
  URL, hijacked True, cleanup close deleted owner tab
  True.
- Judgment: the triggering condition has NO supporting
  evidence and contradicts run-1 evidence. Within one
  cmd_open invocation, handles were consistent across
  before, scan, /window/new, (c) check, navigate, and
  F1 check; run 1 passed all of them. Run 2's
  ephemerality was CROSS-session (two lists one minute
  apart, separate processes), and Gecko handles are
  per-window UUIDs. So this is a residual assumption,
  not a live hole. Note the set-difference check in C1
  turns this case into a fail-closed refusal too, so C1
  closes H2 as a side effect. Condition: record the
  assumption explicitly (one line in the zen-tab.py
  docstring): the membership check assumes handles are
  stable within one cmd_open invocation; run 1 supports
  this; run 2's ephemerality was cross-session. Doc-only.

### H3 (test completeness): phase-4 tests leave branches unpinned

- The 5 new phase-4 tests execute phase4, but 4
  behaviors are not pinned by the suite. My probes
  (P-D in /tmp/redteam-amend2-probes.py) confirm the
  code is correct in all 4 cases, so these are test
  gaps, not code bugs:
  - D1: the completed != 4 branch is untested. Probe:
    log with good PROBE URL/count and 'dom_act ok True
    completed 3' raises RuntimeError 'send program did
    not complete 4/4'. Branch works, untested.
  - D2: the envelope ok False branch is untested.
    Probe: ok=False with good URL/count/completed 4
    raises RuntimeError 'send program did not complete
    4/4'. Branch works, untested.
  - D3: call order is not pinned. Probe: the order is
    ['tab', 'oneshot'] (switch before send, correct),
    but the test helper uses return_value mocks with no
    call recording, so a future edit reordering them
    would not be caught.
  - D4: program identity is not pinned. Probe: the
    program passed to oneshot_zen IS SEND_PROGRAM, but
    the mock ignores the program argument, so a future
    edit passing the wrong program would not be caught.
- Condition: add 2 tests (completed != 4, ok False)
  and pin call order plus program identity in the
  _run_phase4 helper (record calls, assert tab('switch')
  precedes oneshot_zen and the program passed is
  SEND_PROGRAM).

## 4. What I could not break

- H1 single-lane case (amend-1 H1): refuses in both
  modes, owner tab intact, zero deletions. The
  membership check is in the right place (line 206,
  immediately after POST /window/new, before the count
  gate and before any navigate or DELETE), and `before`
  is full handles (GET /window/handles), the same form
  as new_handle, so there is no truncation mismatch.
- H2: complete across all four branches (my probes B2,
  B3, B4 above). The amend's own test covered only the
  scan_error branch; I verified the other three.
- Count gate: the genuinely-new-handle-no-tab test
  passes; the gate still refuses when no tab is created.
- Phase-4 happy path, wrong URL, wrong count, missing
  PROBE, wrong switch landing: all 5 tests pass in my
  run, and my probes confirm the underlying behavior.
- Prep file: no title gate left; recovery line and G1
  note present.
- Fixture: sha matches FIXTURE_SHA. Diff scope is
  exactly the amend, 4 files, 570 insertions, 16
  deletions.

## 5. Convergence with Council 1 (ccaa056, GO, no conditions)

- Council 1 G1 is the same finding as my P-E below:
  cmd_close's post-DELETE verification reads can mask
  a successful close. Independent convergence.
- Council 1 G3 covers concurrent open-only (count +2,
  refuse) and concurrent close-only (stale handle in
  `before`, unrealistic return). My H1 goes one step
  further: the open+close PAIR nets +1 and defeats the
  count gate, which G3 does not cover. Genuinely new.
- Council 1 did not mention the phase-4 test gaps
  (H3) or the re-mint assumption (H2). Both are mine.
- Council 1 verified the H1 repro, the H2 probe, the
  suite, G0a, G0b, the fixture sha, and the dash counts
  independently. My numbers match theirs exactly
  (36/36, 177/177, fixture sha, 0 dashes).

## 6. Gaps and minor observations (not blockers)

- G1 (converges with Council 1 G1): cmd_close's
  post-DELETE verification reads (_handles and _scan
  after the DELETE, lines 402-406, before
  _restore_original) can still raise after a successful
  DELETE and mask the close success. My probe P-E:
  cmd_close RAISED 'simulated scan failure after
  DELETE' although the scratch tab was actually gone.
  Same shape as H2, different site, pre-existing from
  amend 1. Consequence is a spurious error
  (fail-closed), never a wrong navigate or DELETE.
  Follow-up candidate, not a live-run gate.
- G2 (adopt Council 1 G2): the amend-2 log says the
  H1 repro was re-run "in both modes", but the repro
  script itself is single-mode (select_new=True). The
  no-select mode was covered by the worker's own probe
  file and the new suite test. Log wording only.
- G3: the set-difference check in C1 subsumes the
  count gate and the membership check as independent
  detections (both still catch H1 on their own); keep
  all three as defense in depth with distinct error
  messages.
- G4: the fake does not model within-session handle
  re-minting; if the coordinator ever wants to test
  the P-A condition, the fake needs a re-mint mode.
  Informational.
- G5: the membership check's false-positive side is
  fail-closed only: if /window/new returned a handle
  in `before` belonging to a tab that has since closed,
  the run refuses spuriously. No safety impact.

## 7. Verdict: GO WITH CONDITIONS

Conditions, all to be satisfied before the next live
proof (not before landing this amend):

- C1 (MEDIUM, H1): add the handle-set difference
  check after POST /window/new (new handles ==
  {new_handle}, none removed, against `before`),
  plus a P-C regression test (concurrent open+close
  plus stale-handle return refuses, owner tab intact,
  zero deletions). Correct the amend-2 log wording
  ("never a wrong navigate") in the follow-up log.
  Or the coordinator records written risk acceptance
  of the P-C conjunction instead of the fix.
- C2 (small, H3): add the 2 phase-4 tests
  (completed != 4, ok False) and pin call order plus
  program identity in the _run_phase4 helper.
- C3 (doc-only, H2): record the within-session
  handle-stability assumption in the zen-tab.py
  docstring (one line).

The live proof still waits for the remaining amend-2
reviews (Council 2, Council 3) per the standing
process; that is a process gate, not a condition on
this amend. The next proof is a fresh run number with
a fresh intent/message, copying the fixed run2.py;
run 1 must not be re-run as-is. The Muse chat tab
closed by run 2 is NOT reopened by this amend.

## 8. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received ~20:39 +07, 22/11/2026. HEAD at review
  start bcc249c (remote HEAD moved to ccaa056 during
  the review when Council 1 landed).
- Suite, re-run by me 20:41 +07: python3 -m unittest
  tests.test_zenproof2_fix, Ran 36 tests in 0.006s, OK.
- G0a, re-run by me 20:41 +07: Ran 177 tests in
  12.628s, OK.
- G0b, re-run by me 20:41 +07: code_exec.validate_
  program passes for PROBE_PROGRAM and SEND_PROGRAM.
- Fixture, 20:41 +07: sha256 147494cda4c6ae24a51ced
  03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6cbf, matches
  FIXTURE_SHA.
- Dash counts, 20:41 +07: U+2014 0, U+2013 0 in all 4
  files.
- Diff scope, 20:40 +07: git diff --stat
  e9994d9^..bcc249c, 4 files, 570 insertions, 16
  deletions. Per commit: e9994d9 zen-tab.py 47+/11-,
  d8f8ac3 test file 205+/4-, 16075f6 prep file 14+/1-,
  bcc249c log 304+.
- Amend commits on origin, 20:46 +07: git merge-base
  --is-ancestor bcc249c ccaa056 passes; ls-remote
  origin/todolist-push = ccaa05669f03cbe7a9cfe76db
  45f35faa469bea2.
- Probes, 20:42 +07: python3 /tmp/redteam-amend2-
  probes.py. P-A both modes cmd_open RETURNED ok,
  owner tab hijacked True, cleanup deleted owner tab
  True. P-B B2/B3/B4 all ok True with reads None.
  P-C first run missed the hijack (title lookup);
  corrected re-run: cmd_open ok True, X tab URL is
  the fixture URL, cleanup deleted X, tabs left are
  the owner Muse tab and the empty about:blank tab.
  P-D D1/D2 raise RuntimeError 'send program did not
  complete 4/4'; D3 order ['tab', 'oneshot']; D4
  program IS SEND_PROGRAM. P-E cmd_close RAISED
  'simulated scan failure after DELETE' although the
  scratch tab was gone.
- _wd, 20:42 +07: scripts/zen_dom.py lines 537-567,
  every transport failure becomes ZenDomError.
- list_tabs, 20:42 +07: scripts/zen_dom.py lines
  647-720, raises ZenDomError only.
- Council 1 amend-2 review, read 20:44 +07: commit
  ccaa056, verdict GO, no conditions. Convergence
  noted in section 5.
- Files changed by me (review only): improvements/
  w-zenproof2-amend2-redteam-review.md (new, this
  file). No amend file modified. No live run. No
  reviewer spawned.
