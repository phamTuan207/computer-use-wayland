# Batch 13 redteam task 1: attack on the P2-AMEND-FIX verification

## Verdict: SURVIVES

The task 1 report (docs/batch13-task1-p2-amend-fix-verify-20261122.md,
commit e018ae0, verdict PASS) survives the attack. Every substantive
claim was re-checked first-hand against the real code on branch
todolist-push at HEAD 3167c76 and by re-running the key checks. The P2
suite passes with 97 tests, the failing-first run gives exactly the 7
predicted failures, the pointer guard exists at both _dispatch call
sites, the A1/A2 pins reproduce exactly, and both discover totals
reproduce with every error and failure traced to a named cause. No
breaking finding. Five minor findings follow, all citation,
attribution, or presentation issues. None changes the PASS verdict.

## Breaking findings

None.

## Minor findings

### M1. Three line-range citations in Check 2 are off by a few lines

The code claims are all true, only the cited ranges are wrong:

- Wait: the report cites "(lines 515-522)". input_sent False and
  target_received False are at lines 520-521, but the 'ok': True line
  is line 524, outside the cited range. Correct range: 515-524.
- Assert sent/received: the report cites "(lines 611-614)". The
  `if action_type == 'assert':` line is 613 and
  `sent = received = False` is line 618. Correct range: 613-618.
- Assert ok: the report cites "640-641". `ok = verified` is line 639;
  line 640 is `else:`. Correct: line 639.

### M2. Check 4 misattributes two evidence items to the worker log

The report says: "The worker log records tesseract present at
/usr/bin/tesseract at 12:58 +07 and Firefox re-downloaded for batch 6."

- The worker log (improvements/worker-click5-p2-amend-fix-log.md,
  commit 03d99bc, 529 lines) states tesseract is installed in the
  13:12:00 +07 entry, not at 12:58. The 12:58 entry is about
  native/wtype existing, not tesseract. The timestamp is attached to
  the wrong log entry.
- "Firefox re-downloaded for batch 6" does not appear in the worker
  log at all. The log mentions Firefox only twice: "/usr/bin/firefox
  does NOT exist" and "no firefox string in the test file at all".
  The conclusion itself still stands: test_bench_manifest passed at
  worker time, and it hashes
  /home/hatch/workspace/tools/firefox/firefox unconditionally
  (scripts/bench_manifest.py line 177), so that binary existed at
  worker time. But the cited evidence is not in the cited source.

### M3. Check 1 is not reproducible from a bare checkout as written

In a fresh worktree the exact Check 1 command fails: Ran 97 tests,
FAILED (errors=21), all "RuntimeError: private wtype helper is
missing". The OK result needs the docs/testing.md wtype build first.
The report does disclose the build in "Scope and method", and
docs/testing.md documents the 21-error precondition, but Check 1
presents the command as directly yielding OK. A reader following
Check 1 alone gets a failure. After building wtype (35984 bytes,
same size the report states), the suite passes, so this is a
presentation gap, not a wrong result.

### M4. The root discover failure count is boot-time dependent

My root discover gave failures=2, not the report's 1. The extra
failure is test_act_diagnostics.ActDiagnostics.
test_preflight_refusal_raises_before_any_diagnostics_query, which
fails only when the VM was booted less than 121 seconds before the
test runs: the test subtracts OBSERVATION_MAX_AGE + 1 (121) from
capture_started_monotonic, which is time.monotonic() at fixture
build, so on a fresh boot the value goes negative and the code
raises "capture_started_monotonic is invalid" instead of the
expected "observation older than 120s" refusal. It passes on
re-run once the monotonic clock is past 121 (verified at monotonic
431.2s). The 507a50b cu.py diff touches only the wtype error
message, so this cannot be a P2-fix regression. The report's
failures=1 was correct for its run. A future verifier on a fresh
boot should expect this flake and not mistake it for a regression.

### M5. The report's cited evidence logs are gone

The report cites /tmp/batch13-t1-discover-root.log,
/tmp/batch13-t1-discover-tests.log, and
/tmp/batch13-t1-discover-root-v.log. /tmp was swept during this
session and those files no longer exist. This is a record-keeping
note only. My own logs are kept under the goal hidden_files
directory (see Evidence index).

## What survived (confirmed first-hand)

### Check 1: P2 suite, 97 tests OK

- Loader count: 97 tests across 9 classes, exactly the report's
  breakdown (ElementRefTests 21, ScreenScopeLegalityTests 18,
  ZenBackendTests 14, ScreenPointFormTests 11, ValidatorFixTests 11,
  CodeExecPlanValidationTests 9, NoPointerDelegateTests 8,
  ValidatorLimitationTests 3, BackendRangeTests 2). The 18 for
  ScreenScopeLegalityTests is 2 defined in the file plus 16 inherited
  from test_keyboard_preflight.DesktopPreflight.
- After the wtype build: Ran 97 tests, OK, twice (0.787s, 0.671s).
- Failing-first at ce399c7: Ran 11 tests, FAILED (failures=7). The 7
  failure names match the report exactly: test_main_path_type,
  test_main_path_move, test_reground_click, test_reground_fill,
  test_wait_reports_no_input_sent, test_assert_reports_no_input_sent,
  test_assert_mismatch_still_fails_without_input_sent. The 4
  pre-fix passers are test_main_path_click plus A1, A2, A3, as the
  report states. Full pre-fix suite: 97 tests, failures=7, errors=21
  (the 21 are the missing-wtype errors). Post-fix: Ran 11 tests, OK.
- ce399c7 changes exactly 1 file (tests/test_p2_element_ref.py, 212
  insertions), so the 11 tests are the only addition. 507a50b changes
  3 files (docs/testing.md, scripts/cu.py, scripts/zen_backend.py),
  so no validator change is in either fix commit.

### Check 2: pointer guard at both _dispatch call sites

- Exactly two `self._dispatch(` call sites in scripts/zen_backend.py
  at HEAD 3167c76: line 569 (re-ground) and line 635 (main path).
  The only other `_dispatch` matches in scripts/ are
  tc02_controller._dispatch_hyprland and first_action._dispatch_ms,
  neither of which sends pointer input.
- Guards immediately before each call: line 559 (re-ground, with the
  re_ground plan_rect/live_rect pair and error code
  no_pointer_delegate) and line 625 (main path). _dispatch itself
  returns (False, False) when the pointer is None (line 387).
- The old 8-type allowlist is confirmed in the 507a50b diff:
  ('click', 'double_click', 'confirm_click', 'hover_click', 'fill',
  'set_value', 'key', 'scroll'), removed and replaced by a check for
  all types. The only remaining double_click/confirm_click/
  hover_click mention is lines 429-430 inside _verify, a
  postcondition classifier, not a dispatch guard.
- The 507a50b diff also confirms the wait fix (input_sent and
  target_received True changed to False) and the assert fix
  (sent = received = True changed to False, plus `ok = verified`).
- No other input-sending path exists in zen_backend.py: _revalidate
  and _note_typed contain no pointer, _dispatch, wtype, or send
  call; _note_typed only reads session.field_value. No wtype,
  subprocess, or os.system call exists in zen_backend.py, and no
  shell-out to any external pointer tool exists there.
- cu.py builds ZenDomBackend without a pointer argument and comments
  that the delegate is NOT wired and needs the step-9 prototype, so
  the CLI path always refuses input. This matches the report's
  limitation section, which does not claim a live re-run.

### Check 3: A1/A2 pin the validator limit

- check_viewport_geometry is at scripts/zen_dom.py line 107. The
  verified-origin branch runs only inside
  `if right_gap < 0 or bottom_gap < 0:`, and the normal branch
  returns `absolute` after the exactness check, never reading
  verified_moz_inner. Confirmed by code read.
- Direct calls reproduced exactly (factor 1, window [2509, 914],
  size [925, 1176], monitor [2464, 902, 1920, 1200], inner
  [667, 1150]): gaps 8 and 8; A1 returns [2759, 932]; A2 with
  verified_moz_inner [240, 8] still returns [2759, 932]; A3 returns
  [2749, 922]; control case (moz [274, 66], gaps -16 and -40) with
  verified [240, 8] returns [2749, 922].

### Check 4: discover totals and error attribution

- Root discover, my re-run: Ran 2131 tests in 317.762s, FAILED
  (failures=2, errors=5, skipped=17). The 5 errors are exactly the
  report's 5: test_bench_manifest x3 (FileNotFoundError
  '/home/hatch/workspace/tools/firefox/firefox'), test_cursor_file
  setUpClass (g++ rejects -std=c++26), test_tc02_controller x1
  (tesseract unavailable). The 1st failure is the tc02
  fragment-absent test expecting '20:30' in the reason. The 2nd
  failure is the fresh-boot flake in M4, not a code difference.
- Tests/ discover (verbose), my re-run: Ran 2124 tests in 249.291s,
  FAILED (failures=1, errors=8, skipped=17), exactly the report's
  numbers. The 8 errors are the worker 4 (test_a11y_skeleton
  ModuleNotFoundError: No module named 'tests'; test_cursor_file
  g++ C++26; test_perf_evidence x2, FileNotFoundError
  'docs/benchmarks/r5_cdp_aggregate.json') plus bench_manifest x3
  plus tc02 x1. The 1 failure is the tc02 fragment-absent test.
- Skip breakdown from the verbose log: 10 "cursor renderer missing"
  plus 2 "optional cursor renderer missing" (12 cursor), 2 "Lua
  interpreter missing" plus 1 "Lua interpreter is unavailable"
  (3 Lua), 1 hyprglass source, 1 tesseract. Same 12 + 3 + 1 + 1 = 17
  as the report, with the same grouping.
- Skip swap confirmed in the verbose log:
  test_menu_bar_ocr_requires_file_and_edit_on_fixture_images now
  skips ("tesseract is required by the menu-bar check") while
  test_missing_tesseract_is_unverifiable now runs and passes ("ok").
- Related 7 suites: Ran 294 tests, OK. Previously unrun 3 suites:
  Ran 131 tests, OK. Both match the report exactly.
- wtype build reproduced: native/wtype 35984 bytes, twice (two
  worktrees). `pkg-config gtk4-layer-shell-0 gtk4 wayland-client`
  fails with exit 1, as the report states.
- Git claims: ce399c7, 507a50b, 03d99bc, and 292753f all resolve and
  are ancestors of 3167c76. No commit between 507a50b and 3167c76
  touched scripts/bench_manifest.py, scripts/tc02_controller.py,
  tests/test_bench_manifest.py, or tests/test_tc02_controller.py.
  No commit between 292753f and 3167c76 touched
  test_cursor_file.py, test_perf_evidence.py, test_a11y_skeleton.py,
  test_tc02_controller.py, or test_bench_manifest.py.
  `git show 292753f --stat` confirms 17 files.
- Worker log numbers confirmed in the log at 03d99bc: P2 Ran 97 OK;
  tests/ discover Ran 2124, errors=4, skipped=17, failures=0;
  root discover Ran 2131, errors=1, skipped=17, failures=0;
  related suites 294 OK; unrun suites 131 OK. The live claims the
  report lists as not re-run are in the log as stated (Zen live run
  PASSED 13:22:29 +07; CLI act WITH/WITHOUT binding PASSED
  13:38:38 +07).
- Em dash check: 0 em dashes in the added lines of docs/testing.md
  in 507a50b, 0 in the zen_backend.py and cu.py diff, 0 in the
  ce399c7 test diff. The single em dash in the full 507a50b diff is
  a pre-existing hunk-header context line, not an added line.
  docs/testing.md at 3167c76 has 9 em dashes, as the report notes.
  The task 1 report itself has 0 em dashes, 0 en dashes, and 0
  at-signs.
- Binaries still missing at check time (14:52 +07): 
  /home/hatch/workspace/tools/firefox/firefox does not exist and
  /usr/bin/tesseract does not exist (`which tesseract` finds
  nothing). Same state the report recorded at 14:26 +07.

## Scope and method

- Report branch: main. Code read read-only from branch todolist-push
  at HEAD 3167c76, in clean git worktrees. todolist-push was never
  modified. No live Zen run was attempted, per the brief.
- Worktrees: first pair under /tmp was deleted by a /tmp sweep
  mid-session (it killed the first root discover at about 101s);
  recreated under ~/workspace/batch13-redteam-wt (3167c76) and
  ~/workspace/batch13-redteam-wt-ce (ce399c7) and all runs repeated
  there. The wtype helper was built inside the worktree only
  (gitignored build artifact, 35984 bytes). Worktree status after
  all runs: clean.
- Times are Asia/Ho_Chi_Minh (+07) on 2026-11-22, unless marked UTC.
- No personal information in this report. No long dashes anywhere
  in it.

## Evidence index

- P2 suite fresh worktree without wtype: Ran 97, FAILED (errors=21).
- P2 suite after wtype build: Ran 97, OK, twice (0.787s, 0.671s).
- Failing-first at ce399c7: Ran 11, FAILED (failures=7), 7 failure
  names listed in Check 1 above; full pre-fix suite: 97 tests,
  failures=7, errors=21.
- Post-fix 11 tests at 3167c76: Ran 11, OK.
- Pointer guard: scripts/zen_backend.py lines 559-569 (re-ground)
  and 625-635 (main), _dispatch fail-closed at line 387, _verify
  lines 429-430. Correct wait/assert lines: wait 515-524,
  assert 613-618 and 639.
- Validator: scripts/zen_dom.py line 107; direct A1/A2/A3 calls in
  Check 3 above.
- Root discover: Ran 2131 in 317.762s, FAILED (failures=2, errors=5,
  skipped=17). Log: goal hidden_files
  batch13-redteam-task1/discover-root.log.
- Tests/ verbose discover: Ran 2124 in 249.291s, FAILED (failures=1,
  errors=8, skipped=17). Log: goal hidden_files
  batch13-redteam-task1/discover-tests-v.log.
- Related suites: 294 OK; unrun suites: 131 OK.
- Fresh-boot flake: test_act_diagnostics fails while VM uptime is
  under 121s, passes at monotonic 431.2s.
- Commits verified: ce399c7, 507a50b, 03d99bc, 292753f, all
  ancestors of todolist-push HEAD 3167c76.
