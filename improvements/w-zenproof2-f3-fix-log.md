# W-ZENPROOF2-F3-FIX log - diagnose and fix the run-4 F3 refusal

Owner: the owner. Coordinator: Muse tong. Worker: W-ZENPROOF2-F3-FIX.
Repo ~/workspace/computer-use-wayland, branch todolist-push.
No em dash or en dash anywhere in this file. No personal info.
Code + unit tests only, on the VM. No live run, no tab opened,
navigated, or closed in Zen or any browser of the owner. No laptop
touch at all.

## 0. Task receipt and sources read

- Task received 22:08:59 +07, 22/11/2026.
- Sources read before any change:
  - improvements/c5-zenproof-runs/run-4.json (run 4 result)
  - improvements/c5-zenproof-runs/c5-zen-delegate-run4-log.md
  - improvements/coord-click-12-log.md
  - scripts/cu.py (validate_coordinate_metadata, image_point,
    desktop_act preflight, observe, save_observation,
    validate_actions, CodeExecBackend.act)
  - scripts/zen_backend.py (dom_act, _screen_point, _dispatch,
    dom_observe)
  - scripts/zen_pointer.py (ZenPointerDelegate, the step-9
    prototype)
  - scripts/fastpath.py (dom_rect_to_screen_point,
    screen_point_to_image_point, _image_point_for_screen)
  - scripts/dom_act.py (ground_input, ground_many_one_shot)
  - tests/test_zen_pointer.py (existing delegate tests)
  - tests/test_p2_element_ref.py (fake window/field geometry)

## 1. Diagnosis (root cause, proven, not guessed)

### 1.1 The failure, exactly as recorded

Run 4, phase 4 send: program ok False, elapsed 1123.553ms,
completed null, log only the PROBE line, error verbatim "point
outside observed image", error_type sandbox. No input sent, no
bubble. Phases 1-3 PASS (F1 fallback fired, F2 closure refusal
gone). The worker stopped per the brief and did not diagnose
beyond the raise site (scripts/cu.py:1030).

### 1.2 The chain from the send program to the raise

1. The send program calls dom_act(snap, [set_value, focus, key,
   assert]) on the Zen backend (scripts/zen_backend.py).
2. For the first action (set_value), the backend revalidates
   the ref, computes the screen point with _screen_point: the
   #msg-input rect center plus the settled absolute viewport
   origin (scripts/zen_backend.py _screen_point, via
   session.viewport_origin and fastpath.dom_rect_to_screen_point).
3. _dispatch hands (action, screen_point) to the pointer
   delegate, ZenPointerDelegate (scripts/zen_pointer.py).
4. The delegate translates set_value into desktop actions
   [click (x, y), type text] and calls CodeExecBackend.act(meta,
   desktop, observation_path), where meta is the batch window
   observation taken in begin_batch.
5. CodeExecBackend.act calls desktop_act, whose preflight
   validates every pointer action with cu.image_point(meta, x,
   y) (scripts/cu.py:1879). image_point requires 0 <= x < iw
   and 0 <= y < ih against the observation image_size, and
   raises ValueError('point outside observed image') otherwise
   (scripts/cu.py:1030). The refusal propagates through the
   delegate (no try/except there, by documented design: a
   CodeExecBackend.act refusal propagates), through _dispatch
   and dom_act, to the code-exec sandbox, which reports it as
   error_type sandbox.

### 1.3 The point, reconstructed from run-4.json

- Window bounds (Hyprland, probe snap window):
  [2509, 914, 925, 1176].
- #msg-input rect (open.harvest + probe snap): x 20,
  y 228.86666870117188, w 340, h 36, center
  (190, 246.86666870117188).
- Settled absolute viewport origin: (2749, 922), from the
  verified mozInner [240, 8] (F2 pixel proof a42ef12). Factor 1
  (device_pixel_ratio 1).
- Screen point = (2749 + 190, 922 + 246.86666870117188)
  = (2939.0, 1168.86666870117188). The delegate truncated it
  to ints: (2939, 1168).
- Batch window observation (begin_batch: observe_window with
  crop None, max_width 960): region = window bounds
  [2509, 914, 925, 1176]; the window is 925 wide, under
  max_width 960, so no downscale and image_size = [925, 1176].
- desktop_act preflight: image_point(meta, 2939, 1168) needs
  0 <= 2939 < 925. False. The x coordinate alone fails (the y,
  1168 < 1176, passes).

### 1.4 Root cause

The delegate hands the GLOBAL screen point straight through as
the desktop action's (x, y), but desktop_act consumes IMAGE
coordinates: image_point maps image px to global px and refuses
anything outside the image. The delegate never applies the
inverse map, even though fastpath.screen_point_to_image_point
exists for exactly this purpose and the delegate already holds
the batch observation meta (it stamps scope + observation_id
from it). The correct image point is (2939 - 2509, 1168 - 914)
= (430, 254), well inside [925, 1176].

The grounding itself was correct: rect, origin, and screen
point are all right, and the converted point round-trips to the
same global point (2939.0, 1168.87). Only the coordinate frame
of the action payload was wrong.

### 1.5 Why it surfaced only in run 4

Runs 1-3 never reached a dispatch through this delegate: run 1
aborted in phase 1, run 2 closed the tab before the send, run 3
was refused at the dimension-closure gate before the delegate
ran. The G-PILL retry used the CDP path (s2_flip_live.py), not
this delegate. Run 4 was the first live dispatch through
ZenPointerDelegate, so the latent frame bug fired for the first
time. The existing tests encoded the bug: test_zen_pointer
asserted the raw screen point (2949, 1137) reaching the fake
act, and the fake backend meta carried no image_size or region,
so nothing ever validated the frame.

### 1.6 Reproduction (VM, real functions, no live touch)

With the run-4 meta (image_size [925, 1176], region
[2509, 914, 925, 1176]) and the run-4 screen point
(2939.0, 1168.86666870117188):
- Old delegate point (2939, 1168): cu.image_point REFUSES,
  'point outside observed image' (the exact run-4 error).
- Converted image point (430.0, 254.86666870117188):
  cu.image_point ACCEPTS and returns global
  (2939.0, 1168.86666870117188), the same screen point.

## 2. Fix

File: scripts/zen_pointer.py (only production file changed).

- The delegate now converts every screen point to an image
  point against the batch observation meta with
  fastpath.screen_point_to_image_point (the inverse of
  cu.image_point) before building desktop actions. The
  conversion lives in a new _image_point helper, replacing the
  old _point helper that truncated the screen point to ints.
- Floats are kept, not truncated: validate_actions and
  image_point both accept finite floats, and truncating would
  shift the click by up to one image px.
- Fail closed: a point outside the observed image, or a meta
  without an image frame, maps to None, so _translate returns
  None and __call__ returns False with no dispatch. This matches
  the delegate's documented contract (returns False, never
  raises, when an action cannot be mapped). The key path needs
  no point and is unchanged.
- Module docstring records the frame conversion and the run-4
  numbers, so the next reader sees why the conversion exists.

What was NOT changed: no change to cu.py (the desktop_act
contract is image coordinates everywhere, and changing it would
be a far bigger, riskier change), no change to zen_backend.py,
zen_dom.py, fastpath.py, dom_act.py, or the run runners. The
fix is at the single place where the two frames meet.

## 3. Tests

File: tests/test_zen_pointer.py (only test file changed).

- FakeCodeBackend.observe_window now returns a realistic meta
  mirroring the run-4 window: region [2509, 914, 925, 1176],
  image_size [925, 1176], window_bounds the same, monitor_box
  [2464, 902, 1920, 1200].
- FakeCodeBackend.act now validates point actions against the
  image frame the way the real desktop_act preflight does
  (cu.image_point refuses a point outside the image). A
  delegate that hands through a raw screen point is refused
  here, exactly as run 4 was refused live.
- Updated tests use an in-region screen point (2700, 1000) and
  assert the converted image point (191.0, 86.0):
  test_click_maps_and_stamps, test_fill_maps_to_click_plus_type,
  test_focus_maps_to_click, test_second_batch_reobserves,
  test_failed_act_returns_false, test_completed_mismatch_returns_false,
  test_drag_refuses.
- test_backend_dispatches_a_click_through_the_delegate now
  expects the image point (440.0, 223.0) instead of the raw
  screen point (2949, 1137), with the frame conversion explained
  in the comment.
- test_backend_send_shape_through_the_delegate additionally
  asserts the set_value click is at (440.0, 223.0).
- Three new regression tests:
  - test_run4_screen_point_converts_to_image_point: the exact
    run-4 screen point (2939, 1168.86666870117188) reaches the
    desktop as (430.0, 254.86666870117188).
  - test_point_outside_window_image_returns_false: screen point
    (100, 200), outside the window region, returns False with
    no act call.
  - test_meta_without_image_frame_returns_false: a batch meta
    with id and scope but no image frame returns False with no
    act call.

## 4. Verification

- New suite on fixed code: python3 -m unittest
  tests.test_zen_pointer, Ran 20 tests, OK (17 old + 3 new).
- Baseline (new test file against the OLD zen_pointer.py from
  HEAD): Ran 20 tests, FAILED (failures=9). The 9 failures are
  exactly the F3-relevant tests, so the new tests bite:
  test_backend_dispatches_a_click_through_the_delegate,
  test_backend_send_shape_through_the_delegate,
  test_click_maps_and_stamps, test_fill_maps_to_click_plus_type,
  test_focus_maps_to_click, test_meta_without_image_frame_returns_false,
  test_point_outside_window_image_returns_false,
  test_run4_screen_point_converts_to_image_point,
  test_b1_program_completes_through_the_real_shape_session.
  The other 11 tests pass on both versions (they do not touch
  the frame). The fixed file was restored after the baseline
  (diff against the saved copy empty).
- test_zenproof2_fix: Ran 51 tests, OK.
- test_zen_dom standalone: Ran 49 tests, FAILED (errors=4).
  The 4 errors are the known pre-existing
  ModuleNotFoundError: No module named 'test_click3_redteam2',
  identical to baseline, unrelated to this change (this change
  touches only zen_pointer.py, which test_zen_dom does not
  import). They vanish when run grouped (see below).
- G0a: python3 -m unittest tests.test_zen_pointer
  tests.test_p2_element_ref tests.test_code_exec, Ran 180 tests,
  OK. (177 + 3 new tests in test_zen_pointer.)
- G0b: code_exec.validate_program on PROBE_PROGRAM and
  SEND_PROGRAM of c5-zen-delegate-run4.py, both validate OK.
- Grouped targeted run: python3 -m unittest
  tests.test_zenproof2_fix tests.test_zen_dom
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec tests.test_dom_act, Ran 299 tests, OK.
- Full suite: (result below, section 5).
- 0 em dash (U+2014) and 0 en dash (U+2013) in both changed
  files, counted by python.
- Fixture untouched: sha256 of tests/two_vision_fixture.html is
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6cbf,
  matching the manifest.

## 5. Full suite

- Detached, log /tmp/w-zenproof2-f3-fix-fullsuite.log: Ran 2384
  tests in 228.617s, FAILED (failures=1, errors=2, skipped=17).
  2384 = 2381 (F2 baseline) + 3 new tests. The 3 errors are
  exactly the known environment errors, 0 new regressions:
  - ERROR: setUpClass (test_cursor_file.CursorFileTests), g++
    C++26.
  - ERROR: test_typed_text_check_passes_when_fragment_is_visible
    (test_tc02_controller.Tc02MenuBarTests), tesseract
    unavailable.
  - FAIL: test_typed_text_check_fails_when_fragment_is_absent
    (test_tc02_controller.Tc02MenuBarTests), same tesseract
    cause ('tesseract is unavailable; refusing to assume text
    presence').

## 6. Residuals and open items (not fixed here)

- The delegate converts against the batch observation taken in
  begin_batch. If the window moves between begin_batch and a
  dispatch, the backend's live-origin check re-grounds first
  (zen_backend.dom_act window-move path); the delegate itself
  does not re-check the window position. That is the existing
  design, unchanged by this fix.
- A point that genuinely falls outside the observed image now
  refuses the action with input_sent False (fail closed) instead
  of raising. The backend records it as action_failed with the
  verify basis, not as a sandbox error. That is the intended
  fail-closed shape, but it changes the error surface for a
  genuinely off-image point: the envelope will carry
  action_failed rather than 'point outside observed image'.
- The last_viewport_settle surfacing limitation from run 4
  (coord-click-12-log section F2) is untouched: the settle
  reads/elapsed still live only on the ZenSession object and do
  not appear in the envelope. Not part of F3.
- The cmd_close spurious-error open item (post-DELETE
  verification read masking a successful close, reproduced in
  runs 3 and 4) is untouched. Not part of F3.
- Live verification is still owed by design: this fix is unit
  proven only. The next proof run (R5, new number, fresh
  intent/message) must run only when the owner hands the
  machine over again; the user is at the keyboard now, so no live
  run was attempted.

## 7. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received 22:08:59 +07, 22/11/2026.
- Reproduction, VM, real functions: old point (2939, 1168)
  REFUSED 'point outside observed image'; converted point
  (430.0, 254.86666870117188) ACCEPTED, global
  (2939.0, 1168.86666870117188).
- New suite fixed code: Ran 20 tests, OK.
- Baseline old code: Ran 20 tests, FAILED (failures=9).
- test_zenproof2_fix: Ran 51 tests, OK.
- test_zen_dom standalone: Ran 49 tests, errors=4
  (pre-existing test_click3_redteam2 import errors).
- G0a: Ran 180 tests, OK.
- G0b: PROBE_PROGRAM and SEND_PROGRAM of run4.py both
  validate OK.
- Grouped targeted: Ran 299 tests, OK.
- Full suite: Ran 2384 tests in 228.617s, FAILED (failures=1,
  errors=2, skipped=17), 3 known environment errors, 0 new
  regressions (see section 5).
- 0 em dash, 0 en dash in both changed files.
- Fixture sha 147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab
  56dcdfc5afb4f72fba6cbf, unchanged.
- Commits (todolist-push, ls-remote verified 1bc13ca):
  c3954e3 code + tests (scripts/zen_pointer.py,
  tests/test_zen_pointer.py); 1bc13ca this log.
