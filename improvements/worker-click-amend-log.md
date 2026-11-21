# Worker CLICK-AMEND log

Branch: todolist-push. Task: implement all consolidated required fixes on top of
e4082ff (CLICK-FIX), per C1 (846cf0d), C2 (9d5ae86), C3 (59acd36), RT (6cdebda),
CODEX-CMP (238b528), plus the owner corrections of 02:00, 02:02, 02:05-02:07.
Work on the VM only (code + tests). No live laptop driving, no browser work,
never ydotool. No em dash (U+2014) or en dash (U+2013) anywhere in any file
written by this worker. All times wall-clock Asia/Ho_Chi_Minh, elapsed from
task start 01:54:35 +07 (brief) / work start 02:08 +07.

## 2026-11-22 02:08 +07 (t+0m)
Start. Repo at ~/workspace/computer-use-wayland, branch todolist-push, HEAD
646cf71 (fetched fresh; equals origin/todolist-push). Background logs read:
fix e4082ff, C1, C2, C3, RT, CODEX-CMP, SRC 050272d. Root cause of G30 is
PROVEN vision grounding, not conversion: Muse clicked (250,1037), 64px above
the real input (field y 1101-1164, center (306,1132)); Codex re-grounded,
clicked (300,1132), saw the caret, typed, Enter sent 01:37. Conversion
(image_point cu.py:995, move cu.py:1602) is PROVEN correct and stays
untouched. Y13g _check_entry_pyc stays untouched. No message re-sent to
clone1.

## Design decision (02:08, before any code)
Owner corrections 02:00/02:02 replace item 12 and set the acceptance bar:
faster AND accurate together, DOM/a11y rects first-time-right, cheap
verification, no slow observe cycles, one vision drives max actions,
accuracy >= 90%. The 02:02 authorization allows a wholesale rewrite, but
judged by the bar, not by diff size. Decision: INCREMENTAL patch for items
1-11 (all small, specified fixes) PLUS a real new DOM-first grounding path
for item 12 (replaced), NOT a wholesale rewrite of desktop_act. Reason:
the bar is met without rewriting the act loop, because the new path adds
ZERO observes (grounding from DOM rects, verification from cheap JS evals
and from images already in memory), one observation already drives the
whole click+type+Enter batch in desktop_act, and the measured numbers
below are the judge. If the numbers fail the bar, the rewrite option
stays open and will be stated plainly instead of claimed.
Key design points, all cheap by construction:
- R1 fix (item 4): verify the INPUT LINE BAND (full width, anchor y
  plus/minus 12px) between the pre-batch image and the after-capture
  image, both already in memory. No mid-batch capture, no new observe.
  The band catches text anywhere on the caret line, including text at
  the left edge of an empty field far from the click point. The click
  confound is narrowed, not fully removed: a caret/focus ring alone
  also changes the band, so the band is necessary, not sufficient.
  The DOM value check (type_check hook) is the sufficient check.
- Focus check (item 12): a cheap hook in desktop_act, called before
  the first type group. The caller passes a DOM closure
  (document.activeElement check via zen_dom evaluate, no screenshot).
  No hook means no gate; the after-capture band check stays the loud
  backstop. No fresh observe is ever taken to buy accuracy.
- DOM grounding (item 12): fastpath gains dom_rect_to_image_point,
  reusing the calibration_e2 proven chain (screen = viewport origin +
  rect center; image = inverse of image_point). zen_dom gains
  viewport_origin, focus_check, field_value, verify_typed, hit_check,
  all cheap evaluate calls. dom_act.py orchestrates: locate + origin
  + hit check, one desktop_act batch (click + type + Enter) with the
  hooks, DOM value verify. Grounding and verification use 0 observes.
- Acceptance numbers are measured in tests/test_dom_act.py and in the
  run log below: observes per task, actions per observation, wall
  time of the test runs, grounding accuracy across synthetic cases.
  Live wall time (beat Codex 2.5 min) and live accuracy can only be
  proven by the later 2-vision benchmark worker; that is stated as
  owed, not claimed here.

## 2026-11-22 02:24 +07 (t+16m)
All code and tests written. zen_dom test suite finished: 25 tests OK in
0.029s (R5 3 new, R6 2 new, R7 3 rewritten + 1 new, R8 1 new, DOM helpers
7 new). fastpath DomRectMappingTests: 5 tests OK in 0.001s, including the
G30 exact case (DOM point (306,1132.5) hits, old eye point (250,1037)
misses by 64px) and the 7-case accuracy suite at 7/7. dom_act tests: 10
tests OK in 0.002s (ground_many grounds 2 clone inputs from 1 meta in 6
DOM calls, focus miss types nothing, happy path 3 actions from 1
observation). One fix found by the tests: dom_act.focus_type now also
surfaces error_code (not only error), so the miss test can assert
focus_unverified directly instead of a vacuous fallback. Fix-log
correction appended (item 4 / RT R1): the Stage A claim at line 29 was
unproven and false under e4082ff whole-frame check; the amend replaces
it with band + focus gate + DOM value check.

## 2026-11-22 02:26 +07 (t+18m)
Required suites, all on the amend code. 13-suite run (10 named suites
plus test_session_continuation, test_dom_act, test_pick4_fastpath):
315 tests OK in 5.173s wall (5.997s real). 12-module neighbor set:
209 tests, 2 failures, both the pre-existing test_core umask
environment failures
(test_private_mode_under_any_umask_in_isolated_child, umask 0 and
0o777, isolated child cannot import cu), no other failure. Full
discover run started 02:26, still running at log time; result appended
below when it lands.

## 2026-11-22 02:28 +07 (t+20m)
Fail-before proof, worktree /tmp/click-amend-failbefore at e4082ff,
new/changed test files + scripts/dom_act.py + native/wtype copied in,
old source untouched. First run without native/wtype gave 9 failures +
100 errors, most of them the missing wtype binary, so the wtype copy
was added and the run repeated for true numbers. True fail-before on
e4082ff: test_type_verification 1 failure + 7 errors (all 8 new tests;
the 1 failure is the R1 demo itself, old whole-frame check passes on a
click-only frame change), test_first_action 3 failures + 2 errors
(flipped pointer-only test + 4 new), test_zen_dom 6 failures + 9
errors (R5/R6/R7/R8 rewrites + DOM helpers), test_dom_act 9 errors of
10 (the 10th, missing-element, passes on old code because it raises
before touching fastpath), test_pick4_fastpath 5 errors (all 5 new
mapping tests), test_keyboard_preflight OK, test_session_continuation
OK (item 1 fake fix passes on old code too, as expected; the fake was
wrong, the code was right). On the amend code all of these pass.

## Bar numbers (measured in tests, 2026-11-22 02:26 +07)
- Observes per task: click+type+Enter batch uses 3 observes
  (1 preflight fresh + 1 after-capture + 1 settle re-capture for the
  nav-candidate click), identical to the pre-fix path, proven by
  test_click_type_enter_uses_no_extra_observes. The amend adds zero
  observes. DOM grounding + verification add 0 observes (5 cheap JS
  evals per focus_type: 3 grounding + 1 focus + 1 type).
- Actions per observation: 3 actions (click, type, Enter) driven by
  1 observation in the batch; ground_many grounds 2 inputs (6 actions
  across the 2-vision benchmark shape) from 1 observation meta.
- Total wall time: 13-suite run 315 tests in 5.173s; the discriminator
  path is unchanged in step count, so no new latency is added. Live
  wall time vs Codex 2.5 min is OWED by the later 2-vision benchmark
  worker, not claimed here.
- Measured accuracy: grounding accuracy 7/7 = 100% across the 7
  synthetic cases (fastpath suite) and 7/7 = 100% through the
  dom_act orchestrator, bar is >= 90%. Both suites assert >= 0.9.
- Verdict on the bar: the amend diff meets the bar on every measured
  number (observes unchanged, actions per observation 3, accuracy
  100%). The live proof (2-vision benchmark, total wall time beating
  2.5 min, both messages sent) is the remaining acceptance step and
  belongs to the benchmark worker.
- Scope check: no changed line touches image_point (cu.py:995),
  move (cu.py:1724), or _check_entry_pyc. No em/en dash in any file
  written by this worker (grep clean); one pre-existing en dash at
  tests/test_session_continuation.py:456 (comment from b737639, not in
  my diff) left untouched. No ydotool anywhere.

## 2026-11-22 02:32 +07 (t+24m)
Full discover, first run: 1752 tests in 281.550s, FAILED (failures=2,
errors=4, skipped=17). The tail -6 pipe swallowed the failure names,
so a second run wrote the full output to /tmp/click-amend-discover.log:
1752 tests in 278.334s, same 2 failures + 4 errors + 17 skipped.
The 6 are: test_core umask x2 (known), test_a11y_skeleton import
error (No module named tests), test_cursor_file setUpClass (g++
rejects -std=c++26), test_perf_evidence x2 (FileNotFoundError
docs/benchmarks/r5_cdp_aggregate.json). None touches a file this
diff changes. Proven pre-existing: the same 4 modules run in the
e4082ff worktree fail identically (test_core 2 failures,
test_cursor_file 1 error, test_perf_evidence 2 errors,
test_a11y_skeleton 1 error). C2 baseline at HEAD was 1718 tests, 2
failures + 2 errors + 17 skipped; the amend adds 34 tests (1752
total) and no new failure.

## 2026-11-22 02:33 +07 (t+25m)
Commits (explicit pathspec, local HEAD 2080a6f at commit time):
c66aff6 cu.py, 7755e5b first_action.py, 98d8e98 zen_dom.py, c47e2a7
fastpath.py + dom_act.py, 4964f2f type-verification/preflight/
session-continuation tests, 1525a04 first_action/zen_dom/fastpath/
dom_act tests. Note: local HEAD had moved under me (shared branch;
origin/todolist-push c19c227 vs local 2080a6f, same messages, different
hashes, common ancestor 7b85472). Rebase onto origin follows after
this log entry is committed.
