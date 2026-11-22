# W-ZENPROOF2-FIX: URL tab identity + new-tab current check (close R13 blocker)

Owner: Pham Tuan. Worker: W-ZENPROOF2-FIX, independent (not
W-ZENPROOF2, not COORD-CLICK-9). Report goes to Muse tong, not
directly to Pham Tuan. No live proof re-run, no tab opened,
navigated, or deleted in Pham Tuan's Zen. All verification is
code/unit level only. No em dash or en dash anywhere in this
file. No personal info.

## 0. Task receipt and sources (20:08 +07, 22/11/2026)

- Task received ~20:08 +07. T+0m. Branch todolist-push, repo
  ~/workspace/computer-use-wayland.
- Sources read before any edit:
  - improvements/w-zenproof2-log.md (run 2 FAIL, section 5 title
    premise wrong, section 6 Muse tab closed by attempt 2).
  - improvements/c5-zenproof-runs/run-2.json (attempt 2, wall
    20.4s, error title mismatch, tabs_before 18, current
    ef90cb33 'Chat - Muse').
  - improvements/c5-zenproof-runs/c5-zen-delegate-run2.py (run 2
    runner: TARGET 'Clone zen thread', probe/send programs,
    phase 3 title check, phase 6 close by stored handles).
  - improvements/c5-zenproof-runs/zen-tab.py (driver: title gate
    in cmd_open, blind DELETE in the exception handler,
    switch/eval/close by stored handle).
  - tests/two_vision_fixture.html (verified by reading: static
    <title>Two-vision benchmark fixture</title> line 3; JS sets
    H1 textContent to 'Clone ' + clone + ' thread' and never
    touches document.title; git log confirms the fixture was
    brought unedited by 7f3a70b).
  - scripts/zen_backend.py _resolve_target lines 189-208 (matches
    target as a substring over title, url, or handle, so a URL
    substring target resolves the scratch tab with no backend
    change) and dom_observe/dom_act scope binding
    (code_exec.py _api_dom_act: every action scope must equal
    the dom_observe target; the stored binding target is what
    dom_act re-validates against).
  - scripts/zen_dom.py list_tabs lines 641+ (entries carry
    truncated handles, titles, URLs; the scan restores the
    original tab) and _read_current_tab (GET /title and GET /url
    for the current tab).

## 1. Time log (wall-clock Asia/Ho_Chi_Minh)

- 20:08 +07, T+0m: task received, sources read.
- 20:10 +07, T+2m: fixture + backend + scope binding confirmed
  (see section 0). Design fixed (section 2).
- 20:11 +07, T+3m: zen-tab.py rewritten (docstring, URL
  constants, helpers, cmd_open, cmd_switch, cmd_eval,
  cmd_close, _restore_original). py_compile OK, 0 em/en dash,
  0 SCRATCH_TITLE refs.
- 20:13 +07, T+5m: run2.py rewritten (TARGET URL substring,
  programs, parse_probe_line, Runner URL identity, phase 2/3/6).
  py_compile OK, programs validate (G0b), parse checks pass.
- 20:14 +07, T+6m: tests/test_zenproof2_fix.py written (16
  tests, FakeZenSession modelling the run 2 misfire).
  First run 15/16: the incident regression test expected the
  tab count to stay 2, but /window/new creates the about:blank
  tab even when it never makes it current, so the count is 3
  with zero deletions. The test expectation was wrong, not the
  code: leaving the empty tab is the fail-closed outcome (the
  select that would let us close it is exactly what failed,
  and deleting the current window would close the owner's
  tab). Test corrected to assert the empty tab exists,
  un-navigated, with zero deletions.
- 20:15 +07, T+7m: full suite 16/16 OK; G0a suite 177/177 OK.
  Log written, committing.

## 2. What was fixed (3 items from the brief)

### (a) Target the scratch tab by URL substring or H1, never by document.title

- zen-tab.py: SCRATCH_TITLE deleted. New constants
  SCRATCH_URL_SUBSTR = 'two_vision_fixture.html?clone=zen'
  and SCRATCH_H1 = 'Clone zen thread'. cmd_open gates on the
  navigated tab URL containing the substring, then on the H1
  text being 'Clone zen thread' (content confirmation that the
  clone JS ran), then on readyState complete. The document
  title is only recorded as evidence, never gated on.
- run2.py: TARGET is now the URL substring. PROBE_PROGRAM and
  SEND_PROGRAM call dom_observe with it, and all 4 SEND
  actions carry it as scope (scope must equal the dom_observe
  target, enforced by _validate_dom_actions and
  validate_action_binding). No backend change: _resolve_target
  already matches on URL substring.
- Runner probe check: PROBE_PROGRAM prints 'PROBE <snapshot>
  <url> <count>' (the URL has no spaces) plus a separate
  'SNAP-TITLE <title>' line for evidence only. New module
  function parse_probe_line(line, target) parses the PROBE
  line and gates on the URL containing the substring and the
  count being 1; it rejects the old title format, a wrong URL,
  a wrong count, and a wrong shape. Phase 3 uses it, and also
  gates on the switched tab URL and on the H1 text read by
  ev() (recorded in results['pre']['h1']).
- The fixture file is untouched (still 7f3a70b content).

### (b) Identify tabs by URL, never by stored Marionette handles across sessions

- zen-tab.py: new helpers _scan (one list_tabs scan: entries
  plus full handle list from the same moment), _full_handle
  (one full handle per prefix, refuses on zero or ambiguous),
  _find_in_scan (entry by URL substring, refuses on more
  than one match), _resolve_url (fresh resolve inside this
  session). cmd_switch and cmd_eval take a URL substring.
  cmd_close takes (scratch URL substring, original URL):
  the scratch close is precise by URL, the original restore
  re-resolves by URL after the DELETE, and the restore never
  guesses (missing or ambiguous original URL is reported with
  original_missing / original_ambiguous flags, the current tab
  left as Zen activated it). When the scratch tab is already
  gone, close returns already_closed and only restores.
- cmd_open pre-check: refuses before opening anything when a
  tab already carries the fixture URL, so URL identity can
  never be ambiguous between a stale and a fresh scratch tab.
- run2.py: Runner keeps no handle. self.opened records
  whether the open succeeded (so cleanup knows a scratch tab
  exists). self.original_url / self.original_title are
  captured from tabs_before (the current handle is only valid
  inside that one list response; the URL is kept, the handle
  is dropped). ev() evaluates by TARGET URL. cleanup closes
  by (TARGET, original_url) and verifies the current tab URL
  afterwards (original_restored flag) plus the count.

### (c) Check POST /window/new really made the new tab current

- zen-tab.py cmd_open: after POST /window/new, the current
  handle is read back. When it is not the new handle, one
  explicit POST /window select is tried and the current handle
  is read again. When the new tab still is not current, the
  driver raises 'new tab was not made current ...; refusing
  to navigate or close' BEFORE any /url navigate or DELETE.
  The successful path records selected_by ('window/new' or
  'explicit-select') in the open result.
- The open exception handler now deletes ONLY when the
  current tab is the fixture tab by URL (read fresh with GET
  /url). When the current tab is anything else, it deletes
  nothing and leaves every tab untouched. After a scratch
  DELETE it best-effort restores the tab that was current
  before the open.

## 3. Verification (code/unit only, no live tab operation)

- py_compile OK for zen-tab.py, run2.py, and the test file.
- New tests tests/test_zenproof2_fix.py: 16/16 OK
  (python3 -m unittest tests.test_zenproof2_fix, 0.001s).
  FakeZenSession models the run 2 misfire with flags
  select_new and select_works. The incident regression test
  (new tab never current + explicit select fails) proves the
  owner's tab URL is unchanged, zero deletions, the owner tab
  still current, and the new tab left as an un-navigated
  about:blank. Other tests: happy path, explicit-select path,
  wrong H1 closes only the scratch tab, duplicate fixture tab
  refused, switch/eval/close by URL, close when scratch
  already gone, close with ambiguous or missing original URL,
  switch to an unknown URL refuses, runner programs use the
  URL target, parse_probe_line accepts the good line and
  rejects 4 bad lines.
- G0b: both programs pass code_exec.validate_program with no
  exception (same check the run used).
- G0a suite still passes: python3 -m unittest
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec, Ran 177 tests, OK (12.6s).
- 0 em dash (U+2014) and 0 en dash (U+2013) in all three
  changed/new files. Fixture sha unchanged (file untouched).
- NOT verified (needs a live run, out of scope for this
  worker): the fixed runner against real Zen. The next proof
  is a fresh run number with a fresh intent/message, after
  council + redteam review of this fix.

## 4. Open items for the coordinator (not fixed here)

- improvements/w-zen-delegate-liveproof-prep.md still states
  the wrong premise at line 671 ('The ?clone=zen query sets
  the title to Clone zen thread') and in the P2.2/P3.3
  checklist lines. The procedure doc should be corrected to
  the URL-substring target, or the next runner must be told
  the prep file is stale on this point. I did not edit the
  prep file: it is the procedure source, owned by the
  coordinator.
- improvements/c5-zenproof-runs/c5-zen-delegate-run.py (run 1,
  historical) still carries TARGET 'Clone zen thread' and the
  old title check. It must not be re-run as-is; the next proof
  copies the fixed run 2 runner.
- The run 2 incident left one question open: whether Zen's
  tab management selects a Marionette opened tab at all. The
  (c) check plus the explicit-select fallback handle both
  cases (selected by /window/new, or selected by explicit
  POST /window). If a future live run hits the 'not made
  current' refusal, the fallback is to select the tab through
  Zen's own UI or to refuse the run, not to navigate blind.
- The Muse chat tab closed by run 2 attempt 2
  (https://muse.ai/thread/750c8dae-58fb-4a65-82ac-753e78d6ce93)
  is NOT reopened by this fix. Recovery is the coordinator's
  decision (w-zenproof2-log.md section 11, item 1).

## 5. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received ~20:08 +07, 22/11/2026. VM HEAD at start
  a355002 (docs: record amend commit hash 5a272ae in
  w-pillfix-amend-log.md).
- Fixture read 20:10 +07: <title>Two-vision benchmark
  fixture</title>, H1 set by JS to 'Clone ' + clone +
  ' thread', document.title never set.
- zen-tab.py edits 20:11 +07: py_compile OK; U+2014 0,
  U+2013 0, SCRATCH_TITLE refs 0.
- run2.py edits 20:13 +07: py_compile OK; TARGET
  'two_vision_fixture.html?clone=zen'; SEND scopes 5 (1
  dom_observe + 4 actions); programs contain no 'Clone zen
  thread'; parse_probe_line good line returns the fixture URL
  and '1', 4 bad lines rejected with ValueError.
- G0b 20:13 +07: code_exec.validate_program passes for both
  programs.
- Tests 20:14 +07: first run 15/16 (test expectation wrong,
  see section 1); corrected test, then 16/16 OK.
- G0a 20:15 +07: Ran 177 tests, OK.
- Files changed (mine only, explicit pathspecs):
  improvements/c5-zenproof-runs/zen-tab.py,
  improvements/c5-zenproof-runs/c5-zen-delegate-run2.py,
  tests/test_zenproof2_fix.py (new),
  improvements/w-zenproof2-fix-log.md (new, this file).
- Commits, pushed, ls-remote verified:
  6d751b9 zen-tab fix,
  f0dd5ec run2 fix,
  014938b 16 unit tests,
  (this log, fourth commit, hash in the report to Muse tong).
  Pre-existing dirty tests/realistic/clone1-batch3/results.json
  and the untracked improvements files from other workers
  were never touched and are never committed by me.
- No live Zen tab was opened, navigated, or deleted. No
  proof re-run. No reviewer spawned (Muse tong spawns
  council + redteam after this).
