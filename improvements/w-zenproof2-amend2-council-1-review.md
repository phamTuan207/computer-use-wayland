# Council 1 review: W-ZENPROOF2-AMEND2 (H1 membership check + H2 guarded restore reads)

Reviewer: Council 1, independent (not W-ZENPROOF2-AMEND2, not
W-ZENPROOF2-AMEND, not W-ZENPROOF2-FIX, not W-ZENPROOF2, not
COORD-CLICK-9). Report goes to Muse tong, not directly to Pham
Tuan. No amend modified, no live run, no tab opened, navigated,
or deleted in Pham Tuan's Zen. All verification is code/unit
level only, plus my own re-runs of the unit and G0a suites and
the two repro/probe scripts. No em dash or en dash anywhere in
this file. No personal info.

## 0. Task and sources (20:39 +07, 22/11/2026)

- Task received ~20:39 +07. Branch todolist-push, repo
  ~/workspace/computer-use-wayland, HEAD bcc249c at review
  start. The 4 amend commits:
  - e9994d9 zen-tab.py: H1 membership check, H2 _safe_title_url.
  - d8f8ac3 tests/test_zenproof2_fix.py: 36 tests (9 new).
  - 16075f6 prep file: recovery line + G1 note.
  - bcc249c improvements/w-zenproof2-amend2-log.md: amend log.
- Sources read before judging:
  - improvements/w-zenproof2-amend2-log.md (the amend log,
    in full).
  - Full diff of e9994d9, d8f8ac3, and 16075f6 (read line by
    line, not skimmed).
  - Current zen-tab.py cmd_open, cmd_close, _restore_original,
    _handles, _current, _scan, _full_handle.
  - improvements/c5-zenproof-runs/c5-zen-delegate-run2.py
    phase4 (lines 483-525).
  - scripts/zen_dom.py _wd (lines 537-567) and list_tabs
    docstring.
  - /tmp/redteam-amend-repro-h1.py (read in full, re-run).
  - /tmp/amend2-baseline-probes.py (re-run).
  - /tmp/phase4-probe.py (existence only; the suite tests
    cover the same shape).

## 1. Time log (wall-clock Asia/Ho_Chi_Minh)

- 20:39 +07, T+0m: task received, log + diff stat read.
- 20:40 +07, T+1m: zen-tab.py diff + _handles/_current read;
  test diff read.
- 20:41 +07, T+2m: phase4 + zen_dom read; H1 repro and H2
  probe re-run; suite 36/36 re-run by me.
- 20:42 +07, T+3m: G0a + G0b re-run by me; fixture sha; dash
  counts; ls-remote check.
- 20:43 +07, T+4m: review written, committing.

## 2. What I verified, with evidence

### 2.1 Diff scope is exactly the amend, nothing else

- git diff --stat e9994d9^..bcc249c: 4 files, 570 insertions,
  16 deletions. Only zen-tab.py (58), test_zenproof2_fix.py
  (209), the prep file (15), and the amend log (304).
  run2.py was NOT changed by this amend (the phase-4 tests
  execute its existing code). No shared library touched.
- 0 em dash (U+2014) and 0 en dash (U+2013) in all 4 files,
  counted by me. Fixture untouched (sha256
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6
  cbf, matches FIXTURE_SHA).
- Remote HEAD is bcc249c (ls-remote, checked by me). The 4
  amend files are clean (git status on those paths is empty);
  the dirty tests/realistic/clone1-batch3/results.json and the
  untracked prompt files belong to other lanes, not this amend.

### 2.2 H1: the membership check closes the hole, in the right place

- `before = _handles(z)` is captured at cmd_open start, and
  `_handles` returns the raw GET /window/handles value (full
  handles), the same form as `new_handle` from POST
  /window/new. The check `new_handle in before` is therefore
  a full-handle membership comparison with no truncation
  mismatch. Verified in the code, not assumed.
- The check sits immediately after POST /window/new, before
  the count gate and before any navigate or DELETE (read in
  the diff and in the current file).
- Redteam H1 repro re-run by me (select_new=True): cmd_open
  REFUSED with 'new tab returned an existing handle ...;
  refusing to navigate or close', owner tab URL unchanged,
  deletions [].
- No-select mode (select_new=False, the run 2 mode): the
  worker probe file re-run by me refuses the same way, owner
  tab URL unchanged, deletions []. The new suite test for
  that mode also passes in my run (section 2.7).
- The open exception handler cannot delete on the membership
  raise anyway: the navigate never ran, so cur_url does not
  contain the fixture substring, and the handler requires
  URL AND handle (cur_handle == new_handle). Both H1 tests
  assert deleted == [].
- The count gate still has its own coverage: the new test
  with a genuinely new handle that creates no tab refuses
  via the count gate ('did not increase the tab count').

### 2.3 The C4 test fix is legitimate, not test-cheating

- The worker's first suite run was 35/36: the old C4 test
  expected the count-gate message for a stale-handle fake
  (existing handle, no tab created). Since amend 2 the
  membership check refuses that case first with 'existing
  handle'. That is the intended behavior change, not a
  regression: the membership check subsumes the stale-handle
  case, and the count gate remains the second line of
  defense for a genuinely new handle that creates no tab.
- The worker updated the test to expect the new message and
  rewrote its docstring to say so, and added a dedicated
  count-gate test for the new-handle case. Both tests pass
  in my run. The test change tracks the behavior change;
  coverage of the count gate is preserved, not removed.

### 2.4 H2: _safe_title_url covers every read in _restore_original

- `_safe_title_url` catches bare Exception on each read
  separately and returns (None, None) on failure. All 4
  call sites inside `_restore_original` use it: the
  scan_error branch, the missing/ambiguous branch, the
  restore_failed branch, and the success path. Verified by
  grep (4 sites) and by reading the whole function.
- `_wd` converts every transport failure to ZenDomError
  (zen_dom.py docstring + except clauses: HTTPError,
  TimeoutError, OSError, URLError, HTTPException, ValueError,
  malformed responses), so the `except zen_dom.ZenDomError`
  guards around `_scan` and `_switch` inside
  `_restore_original` are complete for realistic failures;
  the reads are guarded more broadly anyway.
- H2 test and worker probe re-run by me: cmd_close returns
  ok with scan_error True, current_title None, current_url
  None, scratch tab deleted True.
- The other `_title(z)` / `_url(z)` calls in the file are
  outside `_restore_original` and cannot mask a close: the
  cmd_open pre-check and navigate checks (nothing deleted
  yet, raising is correct), the open handler (already wrapped
  in try/except, cur_url None on failure), and the
  cmd_switch / cmd_eval returns (no DELETE in those paths).
  Verified by grep + reading.

### 2.5 C3: the phase-4 tests genuinely execute phase4

- The 5 tests run real phase4 on a Runner with hypr/tab/
  oneshot_zen mocked (Council 2's probe shape). I read
  phase4: the re-switch URL check (lines 493-496) runs
  BEFORE oneshot_zen (line 498), and the PROBE gate runs
  after. Tests: happy path records send_url, send_count '1',
  completed 4; wrong URL/count raise ValueError from
  parse_probe_line; missing PROBE raises RuntimeError ('send
  program printed no snapshot line'); wrong switch landing
  raises RuntimeError ('send switch landed on ...') before
  the send program runs. All 5 pass in my run.
- The switch ambiguity refusal itself lives in cmd_switch
  (zen-tab domain, covered by the zen-tab tests), not in
  phase4. Correctly out of scope here.

### 2.6 Docs (C4) and H3 wording

- Recovery line in the prep file amendment note: matches
  Council 1 C1 from the amend-1 review. When the owner tab
  carries the fixture URL after a refused open, the
  coordinator navigates it back to the Muse thread by hand
  in the Zen UI, never via a Marionette navigate or DELETE,
  and verifies the pre-check passes before the next run.
  Verified in the diff.
- G1 note: the phase-4 listing is the recorded RUN-1
  program (no PROBE print); copy run2.py, never copy the
  listing. Verified in the diff.
- H3: the amend-2 log corrects the F2 wording to
  detection-only and names the real guards (the phase-4
  switch refusing on ambiguity, the phase-5 ev() raising on
  ambiguity). The amend-1 log is untouched as a committed
  historical record. Correct handling.

### 2.7 G0a and G0b, re-run by me

- Suite: python3 -m unittest tests.test_zenproof2_fix -v,
  Ran 36 tests in 0.007s, OK. Exit 0.
- G0a: python3 -m unittest tests.test_zen_pointer
  tests.test_p2_element_ref tests.test_code_exec, Ran 177
  tests in 12.534s, OK.
- G0b: code_exec.validate_program passes for PROBE_PROGRAM
  and SEND_PROGRAM (returns an ast.Module, no exception).
  Loaded run2.py via importlib the same way the test file
  does (the filename has dashes, so it is not a plain
  import).

## 3. Gaps and minor observations (not blockers)

- G1: cmd_close's post-DELETE verification reads (`_handles`
  and `_scan` after the DELETE, before `_restore_original`)
  can still raise after a successful DELETE and mask the
  close success. Same shape as H2, different site,
  pre-existing from amend 1, flagged by no prior review.
  Consequence is a spurious error (fail-closed), never a
  wrong navigate or DELETE. Follow-up candidate, not a
  live-run gate.
- G2: log wording nit. The amend-2 log says the Redteam H1
  repro was re-run "in both modes", but the repro script
  itself is single-mode (select_new=True). The no-select
  mode was covered by the worker's own probe file and the
  new suite test, both of which I re-ran and confirmed.
  Log wording only, not a code gap.
- G3: the membership check relies on `before` captured at
  cmd_open start. A tab opening between `before` and
  /window/new makes the count gate refuse fail-closed
  (count +2). A tab closing in between leaves a stale handle
  in `before`, but /window/new returning a closed tab's
  handle is not realistic Marionette behavior. No action.

## 4. Verdict: GO

No conditions from me. H1, H2, C3, the C4 doc items, and H3
are all closed and independently verified. The live proof
still waits for the remaining amend-2 reviews (Council 2,
Council 3, Redteam) per the standing process; that is a
process gate, not a condition on this amend. The next proof
is a fresh run number with a fresh intent/message, copying
the fixed run2.py; run 1 must not be re-run as-is. The Muse
chat tab closed by run 2 is NOT reopened by this amend.

## 5. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received ~20:39 +07, 22/11/2026. HEAD at review
  start bcc249c.
- Suite, re-run by me 20:41 +07: python3 -m unittest
  tests.test_zenproof2_fix -v, Ran 36 tests in 0.007s, OK.
- G0a, re-run by me 20:42 +07: python3 -m unittest
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec, Ran 177 tests in 12.534s, OK.
- G0b, re-run by me 20:42 +07: code_exec.validate_program
  passes for PROBE_PROGRAM and SEND_PROGRAM.
- H1 repro, re-run by me 20:41 +07: python3
  /tmp/redteam-amend-repro-h1.py, cmd_open REFUSED with
  'new tab returned an existing handle ...', owner tab URL
  unchanged, deletions [].
- H1 no-select + H2 probe, re-run by me 20:41 +07:
  python3 /tmp/amend2-baseline-probes.py, H1 refused, owner
  URL unchanged, deletions []; H2 cmd_close ok, scan_error
  True, current_title None, current_url None, scratch
  deleted True.
- Fixture 20:42 +07: sha256 147494cda4c6ae24a51ced03ccdfb3fc
  5a79a1bbab56dcdfc5afb4f72fba6cbf, matches FIXTURE_SHA.
- Dash counts 20:42 +07: U+2014 0, U+2013 0 in all 4 files.
- Diff scope 20:40 +07: git diff --stat e9994d9^..bcc249c,
  4 files, 570 insertions, 16 deletions.
- ls-remote 20:42 +07: origin/todolist-push = bcc249c,
  verified by me. The 4 amend files clean.
- `_handles` 20:40 +07: returns the raw GET
  /window/handles value (full handles), same form as the
  POST /window/new returned handle.
- `_wd` 20:41 +07: every transport failure becomes a
  ZenDomError (scripts/zen_dom.py lines 537-567).
- Files changed by me (review only): improvements/
  w-zenproof2-amend2-council-1-review.md (new, this file).
  No amend file modified. No live run. No reviewer spawned.
