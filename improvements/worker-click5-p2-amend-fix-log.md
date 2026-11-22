# Worker C5-P2-AMEND-FIX log: step 7 AMEND fix, 6 tracked items

Owner: Pham Tuan (asleep since 06:52, headache; Muse holds full
authority). Coordinator: COORD-CLICK-5. Repo
~/workspace/computer-use-wayland, branch todolist-push. This worker
did NOT do the step 7 implementation (commit 292753f), so this is
independent fix work. No em dash or en dash anywhere in this file.
No personal info. Wall-clock Asia/Ho_Chi_Minh plus elapsed time on
every entry.

## 0. Task and starting point

- Task received 12:56 +07, Sun 2026-11-22 (T+0m). VM HEAD 030c227
  at start.
- Source of truth: the independent verification report on main,
  docs/batch11-task1-step7-verify-20261122.md (commit on
  origin/main, fetched read-only; 107 lines, read in full).
  Verdict AMEND, not PASS. The 6 tracked fix items are quoted
  from its Verdict section.
- Final direction read first:
  improvements/worker-click3-final-direction-log.md (commit
  e05fc58).
- Focus rule (C5-FOCUS-INCIDENT, commit 2d198c4, section 7, read
  first): verify `hyprctl -j activewindow` in the SAME SSH call
  immediately before each keystroke batch; re-verify after any
  gap over 60 seconds or any intervening non-keystroke command;
  use only `hyprctl dispatch 'hl.dsp.focus({ window =
  "address:0x..."})'`; never the string dispatcher form; if the
  focus command errors or the active window is wrong, STOP and
  do not send the key. Prefer CDP-only work with NO keystrokes.
  Laptop SSH only via ~/workspace/ssh-laptop.sh; long jobs
  detached (setsid nohup ... & disown), short checks only.
  Clone2-watch holds run :11:56, :26:56, :41:56, :56:56 (hold
  about start+1m to start+2m40s); verify live, never rely on the
  schedule.
- Window map (re-listed each live run): ws1 Zen 0x557052b62dd0
  (PID 496121); ws2 clone1 Brave 0x55705383d420 (PID 1003210),
  clone2 Chrome 0x5570538ed160 (PID 8059, app window, no tab
  strip).

## 1. Time log

- 12:56 +07, T+0m: task received. Read the final direction log
  (e05fc58), the step 7 verification report in full (fetched
  from origin/main), scripts/zen_backend.py in full,
  scripts/zen_dom.py check_viewport_geometry, the FOCUS-INCIDENT
  section 7, docs/testing.md, scripts/build.py, and the P2 test
  file (ValidatorFixTests, FakeZenSession, FakeZenPointer,
  ZenBackendTests).
- 12:58 +07, T+2m: pre-checks. `native/wtype` EXISTS on this VM
  (35984 bytes, Nov 21 10:53), so the P2 suite runs here without
  a build. `pkg-config gtk4-layer-shell-0` MISSING on this VM;
  `wayland-scanner`, `cc`, `patch` present; wtype deps
  (`wayland-client`, `xkbcommon`) present.
- 12:59 +07, T+3m: failing-first tests written
  (tests/test_p2_element_ref.py, +212 lines): 8
  NoPointerDelegateTests + 3 ValidatorLimitationTests (A1/A2/A3).
- 13:00 +07, T+4m: failing-first run:
  `cd tests && PYTHONPATH=../scripts:. python3 -m unittest
  test_p2_element_ref.NoPointerDelegateTests
  test_p2_element_ref.ValidatorLimitationTests`
  Ran 11 tests, FAILED (failures=7). The 7 failures are exactly
  the predicted ones: main-path type, main-path move, re-ground
  click, re-ground fill, wait, assert, assert-mismatch.
  Main-path click already passed (the old 8-type allowlist guard
  covered it). A1/A2/A3 pin tests passed (they pin the known
  limitation, they do not fix it).
- 13:00 +07, T+4m: failing-first commit ce399c7 pushed, verified
  via `git ls-remote` (origin todolist-push at ce399c7).
- 13:01 +07, T+5m: fix implemented in scripts/zen_backend.py
  (items 1 and 3, section 2) and scripts/cu.py (item 4b,
  clearer missing-helper error).
- 13:01:49 +07, T+5m: wtype-only build run for the item 4 log:
  patch + cc, `wtype built`, `native/wtype` 35984 bytes (same
  size, timestamp updated). Full `python3 scripts/build.py`
  confirmed failing on this VM at the indicator step:
  `CalledProcessError: Command '['pkg-config', '--cflags',
  '--libs', 'gtk4-layer-shell-0', 'gtk4', 'wayland-client']'
  returned non-zero exit status 1`. No tracked file changed
  (`git status` clean apart from the two intended files).
- 13:02 +07, T+6m: docs/testing.md gained the "Building only
  the wtype helper" section (full commands + run log). Fix
  commit 507a50b pushed, verified via `git ls-remote` (origin
  todolist-push at 507a50b).
- 13:02 +07, T+6m: P2 suite after the fix: Ran 97 tests, OK
  (86 + 11 new).
- 13:03 +07, T+7m: full discover from tests/ started
  (backgrounded after 120s, session proc_f4da05f28594).
- 13:05:25 +07, T+9m: discover from tests/ finished: Ran 2124
  tests in 175.215s, FAILED (errors=4, skipped=17), failures=0
  (log /tmp/c5-amend-discover-tests.log).
- 13:05 +07, T+9m: full discover from repo root started
  (background, session proc_0fd8acacb747).
- 13:08:17 +07, T+12m: the three previously unrun suites:
  test_keyboard_preflight + test_click2_redteam +
  test_pick4_fastpath: Ran 131 tests, OK. The 7 related
  suites re-run: Ran 294 tests, OK (same count as the
  verifier).
- 13:08:46 +07, T+12m: discover from repo root finished: Ran
  2131 tests in 178.664s, FAILED (errors=1, skipped=17),
  failures=0 (log /tmp/c5-amend-discover-root.log).
- 13:12:00 +07, T+16m: verbose root discover finished, naming
  all 17 skips (log /tmp/c5-amend-discover-root-v.log).
  tesseract IS installed on this VM (/usr/bin/tesseract);
  /usr/bin/firefox does NOT exist. No commit between 292753f
  and HEAD touched test_tc02_controller.py,
  test_bench_manifest.py, test_perf_evidence.py,
  test_a11y_skeleton.py, or test_cursor_file.py.
- 13:13:23 +07, T+17m: laptop state check. Zen 0x557052b62dd0
  ws1 PID 496121 (matches the window map); clone2 Chrome
  0x5570538ed160 ws2 PID 8059; clone1 Brave 0x55705383d420 ws1
  PID 1119832 (address matches the map; PID changed since the
  brief, Brave restarted). Laptop repo HEAD e68e578, origin
  tip 1a3356d; installed tree has NO zen_backend.py (predates
  step 7), so live runs use the repo checkout, not the
  installed CLI. No full sync-installed.py: it rebuilds native
  components and touches the installed tree + relay, out of
  scope for this fix task.
- 13:13 +07, T+17m: origin tip moved (coordinator pushed
  C5-S2-REOPEN logs 1a3356d, 212e0ad); my 507a50b is an
  ancestor. VM checkout fast-forwarded by the coordinator's
  process to 212e0ad; my commits intact.
- 13:16:32 +07, T+20m: laptop repo fast-forwarded to
  origin/todolist-push 4305dcb (includes 507a50b);
  `_no_pointer_result` count 3 in scripts/zen_backend.py;
  file parses.
- 13:17:47 +07, T+21m: Zen probe 1 (direct Marionette,
  read-only): 18 tabs listed; current tab is Welcome!.
  locate_confirmed on the current tab: body unique=false
  (count 2), input uncovered=false, button not visible, a
  unique=false (count 36), [role=button] null. No selector
  passes on the Welcome tab.
- 13:18:52 +07, T+22m: Zen probe 2: switch_to_handle with the
  8-char listed handles FAILS (HTTP 404 "no such window":
  list_tabs truncates handles to 8 chars, Marionette wants the
  full handle). Lesson recorded: switch by full handle from
  window/handles, or by index via tab_at.
- 13:19:21 +07, T+23m: Zen probe 3 (full handles): Example
  Domain tab (index 11): body passes ALL checks (visible,
  interactive, uncovered, stable, unique, count 1); 'a' also
  passes all; input/button null. Welcome tab re-confirmed as
  unusable. Tab restored to the original afterwards
  (restored: true).
- 13:21:42 +07, T+25m: Marionette current tab switched to
  Example Domain (current_ok true, title "Example Domain").
  Note: dom_observe's tab_at restores the original tab, so the
  harvest reads the CURRENT tab; the program target must match
  the selected tab.
- 13:22:08 +07, T+26m: Zen live run attempt 1 FAILED fast
  (0.09s): program called dom_observe without dom_start():
  error "no Zen session is open; call dom_start() first".
  Program fixed (dom_start() first) and re-run.
- 13:22:29 +07, T+26m: Zen live run PASSED (section 8).
- 13:22:46 +07, T+26m: Marionette tab restored to Welcome!
  (current_ok true).
- 13:24 +07, T+28m: CDP helper /tmp/c5-amend-cdp.mjs written
  (composer rect/focus/read/clear on the clone2 tab); fixed a
  real bug in it before use (onmessage used undefined `mid`,
  must be `msg.id`; the sed then also wrongly changed the
  timeout closure, fixed back line by line, re-verified with
  node --check).
- 13:25 +07, T+29m: A/B driver /tmp/c5-amend-live.py written
  (87 lines). A/B run deferred past the 13:26:56 clone2-watch
  hold; runs after ~13:30.
- 13:25:27 +07, T+29m: A/B run launched detached on the laptop
  (setsid nohup sh /tmp/c5-amend-launch.sh: sleep 240, then
  `computer-use session -- python3 /tmp/c5-amend-live.py`,
  output to /tmp/c5-amend-live.log). Session starts ~13:29:27,
  just as the 13:26:56 hold ends (~13:29:36); the driver
  re-verifies Hyprland focus immediately before each act and
  aborts on mismatch, so any hold overlap fails safe.
  Detached launch chosen because laptop SSH sessions die after
  ~30s on long foreground runs (2026-11-13 lesson).
- 13:26 +07, T+30m: dash audit: my log, zen_backend.py, cu.py,
  and test_p2_element_ref.py contain 0 em/en dashes.
  docs/testing.md contains 9 em dashes, ALL pre-existing
  (lines 10, 11, 54, 56, 59, 61, 194, 204, 205); none is in my
  added "Building only the wtype helper" section. Left as is:
  reformatting the whole pre-existing file is out of scope.
- 13:25:27 +07, T+29m: A/B run attempt 1 launched detached
  (sleep 240, then session; output /tmp/c5-amend-live.log).
  FAILED to produce evidence: by 13:32:22 no log file existed,
  no session process was alive, and the three /tmp files
  (c5-amend-cdp.mjs, c5-amend-live.py, c5-amend-launch.sh) had
  vanished, although each had been confirmed present by a later
  SSH call (node --check passed, wc -l 87, "launched"). The
  13:30:45 "process alive" reading was a false positive: the
  `ps | grep -c "[c]5-amend-live"` count of 1 was my own check
  command's `bash -c` line, which contains the literal string
  (the [c] trick excludes only the grep itself). Root cause of
  the disappearance NOT established: /tmp still holds older
  c5-* files (validator-proof, click1/2, focus screenshots),
  so it was not a wholesale tmp cleanup; no relay journal
  entries 13:28-13:33; no OOM evidence sought. Workaround:
  reran from ~/c5-amend-run/ (persistent home dir) with
  self-logging launcher. Lesson recorded: do not trust /tmp
  persistence across minutes on the laptop for live-run
  drivers; keep them under ~ with a launcher log.
- 13:35:51 +07, T+39m: A/B run attempt 2 (persistent files)
  started the session but exited 1 in ~1s. The driver got
  through focus, CDP focus, and observe, then act-WITH failed
  fast with {"ok": false, "error": "desktop observation
  required"} and the driver died silently right after the next
  focus-check, with no traceback. Root cause found in code
  (scripts/cu.py:807-809): validate_desktop_observation
  requires meta['backend'] == 'desktop'; I passed the observe
  STDOUT result as --observation, but the stdout result has no
  'backend' field. The persisted STATE file
  (result['observation'], ~/.cache/agent-computer-use/<id>.json)
  carries it. The silent death is also explained in code: any
  uncaught exception in a cu.py invocation calls
  stop_session_on_error() (scripts/cu.py:3450-3463), which
  requests a session stop, and the supervisor kills the driver
  mid-run. Driver fixed to pass result['observation'] as
  --observation, plus an explicit traceback guard.
- 13:38:38 +07, T+42m: A/B run attempt 3 PASSED, session exit
  0, wall 1.3s (section 8). Composer read-back "C5-AMEND-A
  C5-AMEND-B ", then cleared to "".
- 13:40 +07, T+44m: all 6 items complete. Log finalized and
  committed (see section 9).

## 2. Item 1: pointer check before EVERY _dispatch (fix)

- File: scripts/zen_backend.py, commit 507a50b.
- Change: new helper `_no_pointer_result(index)` returning the
  structured refusal (input_sent False, target_received False,
  verified False, verified_basis 'no-pointer-delegate', ok
  False, error code no_pointer_delegate with the step-9
  prototype wiring reason). It is used at BOTH _dispatch call
  sites, checked BEFORE the call:
  - re-ground path (line 559): before the `_dispatch` at line
    569; the result also carries the `re_ground`
    {plan_rect, live_rect} pair, and the top-level error is
    no_pointer_delegate, never action_failed/focus_check.
  - main path (line 625): the old 8-type allowlist guard
    (click, double_click, confirm_click, hover_click, fill,
    set_value, key, scroll) is REPLACED by a plain
    `if self._pointer is None` check, so type/move and every
    other dispatching type get the same code.
- `_dispatch` itself (line 380) still returns (False, False)
  when pointer is None, as the second fail-closed layer; no
  input path bypasses the check (grep: only two _dispatch call
  sites, lines 569 and 635, both guarded).
- Evidence: the 7 previously failing tests now pass; P2 suite
  Ran 97, OK (section 6).

## 3. Item 3: wait/assert input_sent (fix)

- File: scripts/zen_backend.py, commit 507a50b.
- Wait: the result now records input_sent False,
  target_received False, ok True (time.sleep only, no dispatch).
- Assert: sent = received = False (it only reads state); ok now
  comes from the postcondition alone (`ok = verified` for
  assert) instead of `sent and received and (...)`, so a
  passing assert still passes and a mismatching assert still
  fails. A failing assert reports action_failed/dom-value with
  input_sent False.
- Evidence: test_wait_reports_no_input_sent,
  test_assert_reports_no_input_sent,
  test_assert_mismatch_still_fails_without_input_sent all pass
  (section 6).

## 4. Item 2: pointer=None tests + validator A1/A2 tests (fix)

- File: tests/test_p2_element_ref.py, commit ce399c7 (failing
  first) then 507a50b (green).
- NoPointerDelegateTests (8 tests): main-path click (already
  passed pre-fix, kept as the regression anchor), main-path
  type, main-path move, re-ground click, re-ground fill, wait,
  assert, assert-mismatch. All use pointer=None with the file's
  own FakeZenSession/FakeZenPointer fakes, so they prove the
  logic in zen_backend.py, not live Zen behavior (same scope
  caveat as the verifier's direct checks).
- ValidatorLimitationTests (3 tests): A1 self-consistent-but-
  wrong moz [250, 18], absolute [2759, 932], inner [667, 1150],
  gaps 8/8 is ACCEPTED with [2759, 932], 10px off the true
  origin [2749, 922]; A2 the same plus true verified_moz_inner
  [240, 8] is still ACCEPTED [2759, 932], verified ignored; A3
  true moz [240, 8] returns the true origin (sanity anchor).
  These PIN the limitation; they do not fix it.
- F9/F10 tests untouched and still passing (ValidatorFixTests
  green in the 97-test run).

## 5. Validator scope correction (record)

- The P2-IMPL log's model-correction-2 claim ("validator does
  not accept moz-computed origin") is WRONG in general form.
  It holds ONLY on the closure-overflow branch.
- Evidence (scripts/zen_dom.py, check_viewport_geometry, line
  107): the verified branch runs only when right_gap < 0 or
  bottom_gap < 0 (around line 204) and returns verified_absolute
  at line 267; on the normal passing branch the code continues
  past line 268, checks absolute against expected = window + moz
  * factor within 0.5px, and returns `absolute` at line 299,
  which IS the moz-computed origin. verified_moz_inner is never
  read on the normal branch.
- Live proof (redteam attack, verify report section 5): A1 moz
  [250, 18], absolute [2759, 932], inner [667, 1150], gaps 8/8,
  ACCEPTED [2759, 932], 10px off true [2749, 922]; A2 same plus
  verified [240, 8], still ACCEPTED [2759, 932]. Both are now
  pinned as tests (section 4), not fixed.
- Scope of the correction: the verified-origin path only rescues
  the closure-overflow case (displaced moz, gaps -26/-50, pixel
  proof a42ef12). A moz that is wrong but self-consistent with
  inner/window is accepted. The validator is NOT claimed fixed
  in general. The fix belongs to a later step (likely the step 9
  prototype, which should pass verified moz always or make the
  validator prefer it).

## 6. Item 4: wtype build guidance + clearer error (fix)

- docs/testing.md, new section "Building only the wtype
  helper": full commands (wayland-scanner keyboard protocol,
  patch with keyboard-correction.patch, cc with pkg-config
  wayland-client xkbcommon flags) plus the run log from this VM
  (13:01:49 +07: patching main.c, cc flags -lwayland-client
  -lxkbcommon, `wtype built`, 35984 bytes) plus the note that
  the full `scripts/build.py` stops at the indicator step
  (gtk4-layer-shell-0 missing, CalledProcessError exit 1,
  confirmed live on this VM 13:01 +07).
- scripts/cu.py, `_wtype_executable()`: the RuntimeError now
  names the cause (gitignored build artifact, not in the repo)
  and points at docs/testing.md "Building only the wtype
  helper" plus the gtk4-layer-shell-0 full-build failure. The
  original prefix 'private wtype helper is missing: ' is kept.
  No test pins the old exact message (grep: only scripts/cu.py
  carries it).
- Evidence: P2 suite Ran 97, OK after the rebuild; full discover
  below.

## 7. Item 5: full discover + the three unrun suites

- Discover from tests/ (`cd tests &&
  PYTHONPATH=../scripts:. python3 -m unittest discover -s .
  -p 'test_*.py'`), 13:05:25 +07: Ran 2124 tests in 175.215s,
  FAILED (errors=4, skipped=17), failures=0. Log
  /tmp/c5-amend-discover-tests.log.
  The 4 errors, all pre-existing and none a step 7 regression:
  1. test_a11y_skeleton (import): `from tests import test_a11y`
     fails with ModuleNotFoundError: No module named 'tests'
     when discovering from tests/ (the `tests` package only
     resolves from the repo root). Invocation artifact.
  2. test_cursor_file.CursorFileTests.setUpClass: g++ rejects
     -std=c++26 ("unrecognized command-line option; did you mean
     -std=c++20"). VM toolchain too old. Environmental.
  3. test_perf_evidence.EvidenceChecks.test_valid_normal:
     FileNotFoundError docs/benchmarks/r5_cdp_aggregate.json
     (relative path, resolved from tests/). Invocation artifact.
  4. test_perf_evidence.EvidenceChecks.test_valid_optimized:
     same missing r5 file.
- Discover from repo root (`PYTHONPATH=scripts:. python3 -m
  unittest discover -s tests -p 'test_*.py'`), 13:08:46 +07:
  Ran 2131 tests in 178.664s, FAILED (errors=1, skipped=17),
  failures=0. Log /tmp/c5-amend-discover-root.log. The single
  error is #2 above (cursor_file g++ C++26); #1, #3, #4 pass
  from the root, confirming they are invocation artifacts.
- The 17 skips (verbose root run, 13:12:00 +07, log
  /tmp/c5-amend-discover-root-v.log, every line matched
  "... skipped 'reason'"):
  - 12x "cursor renderer missing" / "optional cursor renderer
    missing": test_real_xcursor_decoder_accepts_each_size,
    test_rendered_silhouette_is_diagonally_symmetric,
    test_a_failed_render_publishes_nothing,
    test_digest_follows_a_directory_symlink_instead_of_skipping_it,
    test_digest_is_content_addressed_and_ignores_the_host_path,
    test_install_publishes_immutably_and_is_idempotent,
    test_install_refuses_a_different_tree_at_the_hash_path,
    test_install_refuses_a_symlink_at_the_target,
    test_missing_renameat2_publishes_nothing_and_fails_closed,
    test_publish_accepts_an_identical_tree_as_idempotent,
    test_publish_refuses_a_different_tree_at_the_same_path,
    test_publish_rejects_a_symlink_created_at_the_destination.
  - 3x "Lua interpreter is unavailable" / "Lua interpreter
    missing": test_lua_string_literals_roundtrip_utf8_controls_and_digits,
    test_hook_sources_profile_each_eval_only_for_the_accepted_glass,
    test_quotes_and_unicode_paths_execute_one_startup_command.
  - 1x "set CU_HYPRGLASS_SOURCE to a pinned hyprglass git repo
    to run this":
    test_patch_applies_to_fresh_pinned_upstream_when_source_is_supplied.
  - 1x "tesseract installed, skip missing-binary case":
    test_missing_tesseract_is_unverifiable.
  Total 12 + 3 + 1 + 1 = 17.
- The verifier redteam's remaining issues do NOT reproduce on
  this VM at this HEAD: test_tc02_controller tests pass
  (tesseract IS installed here, /usr/bin/tesseract; the
  redteam machine lacked it) and test_bench_manifest tests pass
  (4 ok in the verbose log; no "firefox" string in the test
  file at all). No commit between 292753f and HEAD touched
  test_tc02_controller.py, test_bench_manifest.py,
  test_perf_evidence.py, test_a11y_skeleton.py, or
  test_cursor_file.py, so the difference is environment, not
  code. The redteam's failures=1 (tests/ run) also does not
  reproduce: this run has failures=0 on both invocations.
- Step 7 regression check: the step 7 diff is 17 files
  (verified via `git show 292753f --stat`); NONE of the five
  error/skip modules above is in it (test_cursor_file,
  test_perf_evidence, test_a11y_skeleton, test_tc02_controller,
  test_bench_manifest are all untouched by step 7). Every suite
  step 7 did touch passes: P2 97 OK, related 7 suites 294 OK.
- The three previously unrun suites, 13:08:17 +07:
  `PYTHONPATH=../scripts:. python3 -m unittest
  test_keyboard_preflight test_click2_redteam
  test_pick4_fastpath` -> Ran 131 tests, OK.
- The 7 related suites re-run, 13:08:17 +07:
  test_zen_dom test_click3_redteam2 test_code_exec
  test_a1_preflight test_core test_first_action test_s0_bundle
  -> Ran 294 tests, OK.

## 8. Item 6: live CLI act + live Zen run

- Live Zen run (CU_DOM_BACKEND=zen), PASSED 13:22:29 +07.
  Command (on the laptop, inside `computer-use session`):
  `CU_CODE_EXEC=1 CU_DOM_BACKEND=zen python3
  /tmp/c5-amend-zen.py`, which writes the program file
  (mode 600) and runs repo `scripts/cu.py code-exec --program
  /tmp/c5-amend-zen-program.txt --intent 'C5-AMEND live Zen
  no-pointer check' --wall-seconds 45`.
  Program: dom_start(); dom_observe('Example Domain', 'body');
  dom_act with wait 2000ms (lets the transient stale moz
  settle per the VALIDATOR-PROOF note) then click on ref
  'body' with scope 'Example Domain' and the snapshot id.
  Result (wall 2.49s, api_calls 3, elapsed_ms 2399.8):
  envelope ok true; dom_act ok false, completed 1; wait
  result input_sent false, target_received false, ok true
  (item 3 live); click result input_sent false,
  target_received false, verified false, verified_basis
  'no-pointer-delegate', ok false, error code
  no_pointer_delegate; top-level error no_pointer_delegate.
  Snapshot: Example Domain, body rect {x: 98.5, y: 0, width:
  480, height: 884.8}, window [2509, 914, 925, 1176]. The
  closure check passed (no closure error), so the 2s wait did
  its job and the click reached the pointer check. This is the
  FIRST live Zen run of the CU_DOM_BACKEND=zen path: the
  verify report records none existed before. First attempt
  (13:22:08) failed in 0.09s with "no Zen session is open; call
  dom_start() first" (program lacked dom_start()); fixed and
  re-run. Marionette tab was switched to Example Domain before
  the run (13:21:42, current_ok true) because dom_observe's
  tab_at restores the original tab, so the harvest reads the
  CURRENT tab; the Welcome tab has no selector passing
  revalidation. Tab restored to Welcome! after the run
  (13:22:46, current_ok true). No input was dispatched at any
  point (pointer None, fail-closed); no keystrokes were sent.
- Live CLI act WITH / WITHOUT scope/observation_id (clone2
  Chrome tab D1374C7C994D3DA72678E20C7FD099A0, scratch
  composer, no send), PASSED 13:38:38-13:38:39 +07, session
  exit 0, wall 1.3s. Driver ~/c5-amend-run/live.py + CDP
  helper ~/c5-amend-run/cdp.mjs on the laptop; repo
  scripts/cu.py observe/act (laptop checkout at 4305dcb,
  includes 507a50b). Focus verified in-process immediately
  before each act (Hyprland activewindow 0x5570538ed160, ws2,
  ok true, 3x); CDP composer focus rect {x: 451.5, y: 1091,
  width: 622, height: 24}, focused true; baseline composer "".
  Observe id 16202e959211, scope window, window_bounds [2514,
  914, 1853, 1176].
  - WITH binding (action carries scope 'window' +
    observation_id 16202e959211): rc 0, ok true, completed 1,
    preflight 93ms, execution 80ms, type_verified true
    (input-line-band+frame-hash), input_sent true.
  - WITHOUT binding (action carries neither field): rc 0, ok
    true, completed 1, preflight 80ms, execution 79ms,
    type_verified true, input_sent true.
  - DOM read-back (the sufficient check): composer-after
    "C5-AMEND-A C5-AMEND-B ", proving both types landed in the
    composer. Composer cleared to "" (cleared true). No Enter
    pressed, no message sent, no submission.
  This is the first live run of `cu.py act` with and without
  binding, closing the verify report's gap ("no live run of
  cu.py act at all", section 4). It confirms the
  binding-when-present model live: a bound action validates
  against its observation and proceeds; an unbound action
  proceeds on the legacy pixel path instead of being refused.
  Two failed attempts precede the pass, both with recorded
  causes: attempt 1 (13:25:27, /tmp files) produced no
  evidence and its driver files vanished from /tmp for an
  unestablished reason (see section 1); attempt 2 (13:35:51)
  failed with "desktop observation required" because the
  driver passed the observe stdout result instead of the
  persisted STATE observation file, and the failing child
  requested a session stop (cu.py stop_session_on_error),
  which killed the driver silently. Both causes are fixed in
  the passing run (persistent home-dir files; --observation
  set to result['observation']).

## 9. Test evidence summary

- Failing-first: `cd tests && PYTHONPATH=../scripts:.
  python3 -m unittest test_p2_element_ref.NoPointerDelegateTests
  test_p2_element_ref.ValidatorLimitationTests` -> Ran 11,
  FAILED (failures=7), 13:00 +07.
- After fix: `cd tests && PYTHONPATH=../scripts:. python3 -m
  unittest test_p2_element_ref` -> Ran 97 tests in 0.175s, OK,
  13:02 +07.
- Three previously unrun suites: Ran 131 tests, OK, 13:08:17
  +07. Seven related suites re-run: Ran 294 tests, OK,
  13:08:17 +07.
- Full discover from tests/: Ran 2124 tests in 175.215s,
  FAILED (errors=4, skipped=17), failures=0, 13:05:25 +07.
  Full discover from repo root: Ran 2131 tests in 178.664s,
  FAILED (errors=1, skipped=17), failures=0, 13:08:46 +07.
  Verbose root discover names all 17 skips, 13:12:00 +07.
- Live Zen (CU_DOM_BACKEND=zen): PASSED 13:22:29 +07, wall
  2.49s; dom_act wait input_sent false + click
  no_pointer_delegate on the real Example Domain tab.
- Live CLI act WITH/WITHOUT binding: PASSED 13:38:38 +07,
  session exit 0, wall 1.3s; composer read-back "C5-AMEND-A
  C5-AMEND-B ", cleared to "".
- Commits: ce399c7 (failing-first tests), 507a50b (fix items
  1, 3, 4 + docs), 03d99bc (this log). All pushed to origin
  todolist-push and verified with `git ls-remote`.

## 10. Open questions / handoff to coordinator

- The installed tree (~/.local/share/agent-computer-use/) still
  has NO zen_backend.py: it predates step 7. The live runs
  above used the laptop repo checkout. A sync-installed.py run
  is still needed before the installed CLI carries this fix;
  I did not run it (it rebuilds native components and touches
  the installed tree + relay, out of scope for this fix task).
- The /tmp disappearance of the first A/B attempt's driver
  files is unexplained (section 1). No evidence it affects
  anything else; the rerun from ~/c5-amend-run/ worked.
  ~/c5-amend-run/ (cdp.mjs, live.py, launch.sh, live.log,
  obs.json, actions files) is left on the laptop as evidence.
- All 6 tracked items are done. Step 7 can be declared
  complete at live level on this evidence, subject to the
  coordinator's judgment on the validator A1/A2 limitation,
  which is pinned by tests, not fixed (section 5).
