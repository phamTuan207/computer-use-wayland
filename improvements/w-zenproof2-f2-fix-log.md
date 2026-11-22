# W-ZENPROOF2-F2-FIX log: settle the viewport-origin read after tab activation

Worker: W-ZENPROOF2-F2-FIX (independent). Report to Muse tong only.
Repo ~/workspace/computer-use-wayland, branch todolist-push.
No em dash (U+2014) or en dash (U+2013) anywhere in this file.
No personal info. Commit with explicit pathspec only, never bare
commit, never add -A. Verify every push with ls-remote.
No live proof run in this task. No self-spawned reviewer.

## 0. Task receipt and sources read

- Task received 21:37:09 +07, 22/11/2026. Fix F2 of ZT-B run 3:
  phase 4 send refused by the dimension-closure gate before any
  desktop act. mozInner [274, 66] + inner [677, 1160] exceeds
  window size [925, 1176] (gaps -26, -50). Reported mozInner
  displaced from the true viewport origin (pixel proof a42ef12:
  true origin (240, 8) on the live narrowed window). Zen narrowed
  to 925 wide (bounds [2509, 914, 925, 1176]), OmaCal tiled beside
  it on ws1. mozInner moved +21/+36 between the open harvest
  [253, 30] and the send snapshot [274, 66], displaced (+34, +58)
  from the true origin (240, 8).
- Sources read before any code change:
  - improvements/c5-zenproof-runs/run-3.json (attempt 2 result:
    open ok 18 to 19, probe ok, program ok false with the
    dimension-closure error, outcome error, cleanup ok false with
    the discarded-context error, pill_release ok, wall 38811.6ms,
    fixture sha matches).
  - improvements/c5-zenproof-runs/c5-zen-delegate-run3-log.md
    (418 lines: attempt 1 F1 transient scan read, attempt 2
    phases 1-3 PASS, phase 4 refused, no input sent anywhere).
  - improvements/coord-click-10-log.md (sequence STOPPED at step
    1, decisions needed: F2 fork, F1, whether steps 2-4 proceed).
  - improvements/worker-click5-moz-growth-log.md (commit
    a42ef12: the pixel proof, the toggle table, the verdict that
    NO UI element accounts for moz +34/+58).
  - improvements/worker-click5-validator-proof-log.md (v1-v4:
    the stale-read finding, the verified-origin wiring proof).
  - scripts/zen_dom.py check_viewport_geometry (lines 131-340)
    and ZenSession.viewport_origin (lines 830-920), display
    metrics, harvest; scripts/dom_act.py ground_input (lines
    260-310); scripts/zen_backend.py _screen_point (lines
    319-340); tests/test_zen_dom.py fake + viewport_origin
    tests; tests/test_p2_element_ref.py live-state tests.
- Hard rules restated: the fix must be safe, never allow an act
  when the geometry does not close; no live proof; no self-fix
  of anything else (F1 is a separate fix, not touched here);
  no ydotool; no personal info; log continuously with
  wall-clock Asia/Ho_Chi_Minh plus elapsed.

## 1. Time log (wall-clock Asia/Ho_Chi_Minh, elapsed from 21:37:09)

- 21:37:09 +07, T+0m: task received. Sources read (section 0).
- 21:37-21:44 +07, T+0m to T+7m: investigation (section 2),
  implementation (section 3), targeted verification (section 5).
  Intermediate steps are ordered, not minute-stamped: I did not
  record a wall-clock line per step as I went, so no per-step
  times are invented here. Verified anchors: the diff stat and
  dash check below ran at 21:44:17 +07.
- 21:44:17 +07, T+7m: diff stat (2 files, 231 insertions, 17
  deletions), 0 em dash, 0 en dash in both changed files.
- 21:46 +07, T+9m: full suite started detached, log
  /tmp/w-zenproof2-f2-fix-fullsuite.log.
- 21:50:25 +07, T+13m: full suite finished (Ran 2381 in
  231.603s, failures=1, errors=2, skipped=17, the same 3 known
  environment errors, 0 new regressions).
- 21:52 +07, T+15m: log written, commits (section 7). No stall
  over 15 minutes at any point in this task.

## 2. Root cause: mozInnerScreen is a stale transient after tab activation

The reported mozInner is not wrong because the viewport moved.
The viewport never moved. Firefox's REPORTED mozInnerScreenX/Y
is displaced from where the viewport actually renders, and the
displacement is transient: it is stale for ~0.5s after a tab
activation (switch), then settles to the true origin.

Evidence chain (all pre-existing, re-verified by reading the
logs, not re-measured live in this task):

- Pixel proof (moz-growth log a42ef12, section 5): a white
  scratch host div at viewport (8, 8), photographed with grim.
  Expanded narrowed window: the host renders at window (248, 16)
  to (675, 119), so the true origin is (248 - 8, 16 - 8) =
  (240, 8). Firefox reports moz (274, 66). Offset (+34, +58).
  Cross-check: (240, 8) + inner (677, 1160) closes with gaps
  +8/+8, exactly the C12 gaps. The viewport SIZE matches the old
  chrome; only the REPORTED position is offset.
- No UI element accounts for it (moz-growth verdict): sidebar
  Ctrl+S moves moz x between 274 and 53 but the true origin
  barely moves (240 to 236), and moz y never leaves 66;
  bookmarks toolbar and compact-mode shortcut do not move moz
  at all; the +58 in y is untouched by every toggle, and there
  is no visible top chrome beyond the 8px window border.
- The stale-window finding (validator-proof log, NEW FINDING 1,
  run v2): an 8-read stability series (250ms apart, right after
  scratch creation) read (274, 66) at t=0.047s and t=0.299s,
  then (240, 8) from t=0.552s onward (6 reads). The (274, 66)
  value is a STALE read in the first ~300ms after the scratch
  tab is activated; it then settles to the true (240, 8) and
  stays. Every earlier probe (ITEMS56, MOZ-GROWTH) did ONE read
  per fresh session within ~100ms of the switch, so it always
  sampled the stale value. Run v4 reproduced it: first moz read
  0.002s after the switch (274, 66) after a 5min idle gap, and
  the stale state recurs after an idle gap, not on every switch
  (v3 session 2, 1s gap, read settled).
- Run 3 fits the same model: the open harvest read (253, 30)
  and the send snapshot read (274, 66). Neither is the true
  (240, 8); both are samples of the settling curve taken inside
  the stale window (the send runs right after send_switch, a tab
  activation). The intermediate values (264, 50) seen once in
  the moz-growth log and (253, 30) in run 3 show the value drifts
  through intermediates toward (240, 8); it does not jump.
- Why the send read it and the probe did not: each phase uses a
  fresh Marionette session (handles are ephemeral per session:
  open 73ae0c84, probe switch d2e473fb, send_switch 9b629a71),
  so each phase SWITCHES to the fixture tab anew, and each
  switch re-opens the ~0.5s stale window. The send program's
  snapshot read runs ~10ms after send_switch, inside the window.

What the fix must do, and must not do:

- Must: make the origin computation use the TRUE origin on the
  narrowed window, i.e. not trust a single moz read taken right
  after a switch. The read must be allowed to settle.
- Must not: hardcode (240, 8) as the origin. The value lives
  only in probe logs and runtime calls, never in repo code
  (validator-proof section 9: no production code path returns
  or defaults to it). A hardcoded origin would be wrong the
  moment the sidebar state changes (collapsed sidebar moves the
  true origin), and it would hide a genuinely displaced read.
- Must not: weaken the closure gate. The gate correctly refused
  run 3 (the reported moz would have grounded clicks 34px right
  and 58px down). The fix changes the READ, not the CHECK:
  check_viewport_geometry is untouched, and no act is ever
  allowed on geometry that does not close.

## 3. The fix: settle the read in viewport_origin (scripts/zen_dom.py)

Design: poll the 9-number origin read until the moz pair is
unchanged across VIEWPORT_SETTLE_STABLE_READS consecutive reads
AND the geometry closes (check_viewport_geometry passes on that
read's own numbers), within VIEWPORT_SETTLE_BUDGET_S; otherwise
refuse fail-closed. Only the unverified path settles; the
verified path takes one read as before (v4-proven behavior).

Changes (diff 163 lines in scripts/zen_dom.py, 231 insertions
and 17 deletions across both files):

- Module constants (new, after ELEMENT_KEY):
  VIEWPORT_SETTLE_BUDGET_S = 2.0, VIEWPORT_SETTLE_POLL_S = 0.1,
  VIEWPORT_SETTLE_STABLE_READS = 3. Budget 2.0s is 4x the
  observed ~0.5s settle; poll 0.1s gives ~5 samples across the
  settle; 3 stable reads span 200ms of no movement.
- `_read_viewport_origin_raw()` (new helper): one 9-number
  evaluate plus the shape validation, extracted verbatim from
  viewport_origin. A malformed read raises at once: it is a
  transport/protocol failure, never a stale value, so the
  settle loop does not retry it.
- `_read_viewport_origin_settled()` (new): the poll loop. Each
  iteration reads the raw array, tracks moz stability (equal to
  the previous read or not), computes the factor and the
  absolute origin for that read, and runs
  check_viewport_geometry on that read's own numbers inside
  try/except. It accepts only when the check passes AND the
  moz has been unchanged for settle_stable_reads consecutive
  reads. A stable-but-non-closing value is NOT an early exit:
  the stale value itself holds steady for ~300ms (validator
  v2: equal reads at t=0.047s and t=0.299s) and only then
  moves, so only the budget bounds the wait. On expiry it
  raises ZenDomError fail-closed, carrying the last closure
  error (so the refusal message still names the closure
  failure, preserving the existing test contract that matches
  on 'closure'). None arguments resolve to the module constants
  at call time, so tests can monkeypatch the constants. The
  settle is recorded on self.last_viewport_settle (reads,
  settled moz, elapsed ms).
- `viewport_origin()` signature gains keyword params
  settle_budget_s=None, settle_poll_s=None,
  settle_stable_reads=None (defaults resolve to the constants).
  Verified path (verified_moz_inner is not None): one raw read,
  unchanged behavior. Unverified path: the settle loop.
  self.last_viewport_settle is reset to None at the start of
  every call, so a verified-path call never leaves a stale
  settle record. The rest of the function (factor, absolute,
  size, the check call, the warnings recording) is unchanged
  and still runs on the settled read. Docstring records the
  settle behavior and the F2 mechanism with the v2/v4 evidence.

Safety argument (why 3 stable closing reads, not just closure):

- Closure alone is not enough: the drift passes through the
  closure boundary, so a closing-but-wrong intermediate (e.g.
  (245, 12), gaps (3, 4)) could be sampled once. The observed
  drift jumps (253, 30) to (240, 8), a step of (13, 22), and
  the stale plateau that DOES hold steady ((274, 66) for
  ~300ms) never closes, so stability plus closure together
  admit only the settled value: a value must hold still for
  200ms AND close. A false accept would need the drift to pause
  inside the narrow closing-but-wrong band ((248, 16) to
  (240, 8)) for 200ms; no such pause is observed.
- The check itself is untouched: exactness, containment, the
  fit invariant, and the factor requirement still run on the
  accepted read (F9/F10 still refused, verified by the existing
  tests, which all still pass).
- The verified-origin override path is untouched and remains
  the escape hatch for a geometry that genuinely never
  settles (e.g. a persistently displaced moz in some future
  window state): after the 2s budget the call refuses with the
  closure error and the message names the verified override.

What was NOT changed, deliberately:

- check_viewport_geometry: untouched (the validator is the
  spec; the bug was in the read).
- display_metrics and harvest: untouched. They also read moz
  once, and the run-3 open harvest did sample the stale window
  ((253, 30)), but their moz is evidence only, never a gate:
  no click point is computed from the harvest moz (the send
  gate is viewport_origin, which now settles; the backend
  _screen_point and dom_act ground_input both call it). A
  harvest that settles would break its one-shot contract for
  no safety gain. Noted here so a reviewer does not mistake
  the harvest moz for a grounding input.
- F1 (transient empty scan read of the current tab): not
  touched. Separate fix, separate review.
- No live proof run in this task, per the brief. The live
  verification of the settle is the re-run (run 4), which
  needs the coordinator's call.

## 4. Regression tests (tests/test_zen_dom.py, 85 lines, 4 tests)

Added to TestDomHelpers, using a `_sequenced_session` helper
that wraps evaluate to serve moz pairs in order for the
zen_viewport_origin script (repeating the last pair once
exhausted, so a runaway loop is deterministic) and counts the
origin reads. Live run-3 numbers throughout: window (2509,
914) size (925, 1176), inner (677, 1160), outer (925, 1176),
factor 1, true origin (2749, 922).

- test_viewport_origin_settles_after_stale_reads: sequence
  [(274, 66), (274, 66), (253, 30), (240, 8), (240, 8),
  (240, 8)] (the run-3 drift). Expects origin (2749, 922),
  exactly 6 reads, settled moz (240, 8). Poll 0, budget 5s
  (speed; the loop logic is what is pinned).
- test_viewport_origin_refuses_when_never_settles: sequence
  all (274, 66), budget 0.05s, poll 0. Expects ZenDomError
  matching 'closure', and more than 1 read (it polled, then
  refused; it did not refuse on the first sample).
- test_viewport_origin_accepts_settled_first_read: already
  settled (240, 8) on the C12 geometry (inner 1615x1160,
  outer 1863x1176). Expects origin (2749, 922) and exactly 3
  reads: one sample cannot prove the value is not mid-drift,
  so the settle requirement applies on every unverified call.
- test_viewport_origin_verified_path_skips_settle: reported
  moz stale (274, 66), verified (240, 8). Expects origin
  (2749, 922), exactly 1 read, last_viewport_settle None.

## 5. Verification (VM, no live touch)

- py_compile scripts/zen_dom.py OK.
- 4 new tests, self-run: Ran 4 tests in 0.070s, OK.
- Targeted suites, self-run: python3 -m unittest
  tests.test_zenproof2_fix tests.test_zen_dom
  tests.test_p2_element_ref tests.test_dom_act
  tests.test_zen_pointer tests.test_code_exec: Ran 296 tests
  in 20.497s, OK. (296 = 44 zenproof2 + 49 zen_dom incl. 4 new
  + 177 G0a + 26 dom_act.)
- G0a, inside the targeted run: test_zen_pointer +
  test_p2_element_ref + test_code_exec, 177 tests, OK.
- G0b, self-run: PROBE_PROGRAM and SEND_PROGRAM of
  c5-zen-delegate-run3.py both pass code_exec.validate_program
  (Module), same check the run used.
- Full suite, detached, log
  /tmp/w-zenproof2-f2-fix-fullsuite.log: Ran 2381 tests in
  231.603s, FAILED (failures=1, errors=2, skipped=17). The 3
  errors are exactly the known environment errors, 0 new
  regressions:
  - ERROR: setUpClass (test_cursor_file.CursorFileTests), g++
    C++26.
  - ERROR: test_typed_text_check_passes_when_fragment_is_visible
    (test_tc02_controller), tesseract.
  - FAIL: test_typed_text_check_fails_when_fragment_is_absent
    (test_tc02_controller), tesseract.
  Ran 2381 is 2370 (amend3) + 4 new tests here + 7 from other
  lanes in the shared checkout; the invariant that matters is
  identical: failures=1, errors=2, skipped=17, same 3 names.
- Timing note: the settle adds ~0.2s per already-settled
  viewport_origin call (3 reads, 2 polls) and up to 2s per
  refusal. test_zen_dom standalone went from 0.014s (baseline)
  to 5.269s, all of it the two refusal tests burning the 2s
  budget plus the settled calls. Acceptable: the full suite is
  231s, and a send takes seconds.
- Pre-existing quirk, not mine: test_zen_dom standalone shows
  4 errors (ModuleNotFoundError: No module named
  'test_click3_redteam2'), identical on the pristine baseline
  (same 4 errors, Ran 45 in 0.014s). They vanish in the
  combined run (the module is imported by another suite
  first). Not touched, not fixed here.

## 6. Baseline check (new tests bite on old code)

Worktree /tmp/f2-baseline at HEAD (clean, no other lanes'
uncommitted changes), new test file copied in:

- The 4 new tests on old code: Ran 4 tests, FAILED (errors=4).
  The old viewport_origin has no settle parameters, so the
  tests error on the unknown kwargs. That proves they exercise
  the new API, but it is a signature failure, not a behavioral
  one, so I also probed the behavior directly.
- Behavioral probe on old code (same drift sequence, plain
  viewport_origin call, no new params): refused with exactly
  the F2 error, "dimension closure fails: mozInner [274, 66] +
  inner [677, 1160] exceeds window size [925, 1176] (gaps -26,
  -50)". On the fixed code the same sequence returns the
  settled origin (2749, 922). The fix changes the behavior,
  not just the signature.
- Baseline worktree removed after the check (git worktree
  remove /tmp/f2-baseline, verify no leftover in the repo).

## 7. Commits (todolist-push, ls-remote verified)

- Code + tests: 2 files, 231 insertions, 17 deletions.
- Log: this file.
- Hash record: this section, updated after the push.
- Other workers' dirty files left untouched and uncommitted:
  improvements/c5-zenproof-runs/zen-tab.py,
  tests/realistic/clone1-batch3/results.json,
  tests/test_zenproof2_fix.py, and the untracked improvement
  files. None of them are mine; none were staged.
- 0 em dash and 0 en dash in both changed files plus this log
  (grep count 0 each, 21:44:17 +07).

## 8. Residuals and open items (for the coordinator)

- Live verification is still owed by design: the settle must
  be proven on the real narrowed window (run 4, fresh run
  number, fresh intent/message). The settle loop is unit-proven
  here, not live-proven. If run 4's send still refuses, the
  next hypothesis is that the stale window is longer than 2s
  on the live window (raise the budget) or that the value
  never settles in the send context (then the verified-origin
  path, measured live by pixel proof, is the way out).
- The settle budget (2.0s) is 4x the observed ~0.5s settle.
  If a future Zen is slower to settle, the budget is the knob,
  not the check.
- The harvest moz remains a single-read evidence value and can
  sample the stale window (run 3 open harvest (253, 30)); it
  is not a gate, so no fix was made there.
- F1 (transient empty scan read) and the cmd_close
  spurious-error open item are separate fixes, not touched.
- The verified-origin override is unchanged and remains the
  escape hatch for a geometry that genuinely never settles.
