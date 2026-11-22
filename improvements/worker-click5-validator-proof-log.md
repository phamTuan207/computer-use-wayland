# Worker C5-VALIDATOR-PROOF log: live proof of the fixed validator (step 7 P2 gate)

Worker C5-VALIDATOR-PROOF for coordinator COORD-CLICK-5. Report to the
coordinator only. Repo `~/workspace/computer-use-wayland`, branch
`todolist-push`. Owner asleep since 06:52 on 2026-11-22 with a headache;
Muse holds full authority. Wall-clock is Asia/Ho_Chi_Minh; elapsed is
from task receipt 2026-11-22 11:57:59 +07.

Standing rules: wall-clock Asia/Ho_Chi_Minh plus elapsed time on every
log entry. No em dash (U+2014) or en dash (U+2013) anywhere. No personal
info on GitHub. Commit with explicit pathspec only, immediately after
staging, never plain git commit, never git add -A. Verify every push
with git ls-remote. Never ydotool.

## 0. Primary sources read (T+0m to T+5m)

- P2 implementation log, read in full:
  improvements/worker-click5-p2-impl-log.md (commit 292753f). The
  validator fix: scripts/zen_dom.py check_viewport_geometry accepts
  verified_moz_inner; when closure fails it refuses unless a verified
  moz is supplied, and the verified numbers must close; F9/F10 still
  refused. scripts/zen_backend.py accepts verified_moz_inner and
  threads it through. The value is NEVER hardcoded in the repo.
- ITEMS56 log, read in full:
  improvements/worker-click5-items56-log.md (commit 2942f68). Origin
  stage shape (locate, _check_window_not_moved, viewport_origin,
  dom_rect_to_screen_point) and the closure failure on the reported
  moz (274, 66), inner (677, 1160), gaps -26/-50.
- MOZ-GROWTH log, read in full:
  improvements/worker-click5-moz-growth-log.md (commit a42ef12).
  Pixel-proof method (white fixed scratch host + grim screenshot)
  and the true origin (240, 8), giving verified origin (2749, 922).
- FOCUS-INCIDENT log, read in full, procedure-fix section first:
  improvements/worker-click5-focus-incident-log.md (commit 2d198c4).
  Rule applied throughout: verify hyprctl -j activewindow in the
  SAME SSH call immediately before any keystroke batch; use only
  hl.dsp.focus({ window = "address:0x..." }); never the string form;
  if the focus command errors or the active window is wrong, STOP
  and do not send the key. This task sent NO keystrokes at all:
  every read was CDP/Marionette or hyprctl, and the grim shots
  waited for ws1 to become active on its own. No focus change was
  made by this worker at any point.

## 1. Pre-state (T+1m, 2026-11-22 11:58:49 +07)

Live check via ~/workspace/ssh-laptop.sh (hyprctl -j clients,
hyprctl -j activewindow, ps):

- Zen 0x557052b62dd0, origin [2509, 914], size [925, 1176], ws1,
  PID 496121, /opt/zen-browser-bin/zen-bin --remote-debugging-port=9222
  --marionette. Same address, origin, and size as the 11:25 state.
- Active window then: clone2 Chrome 0x5570538ed160 on ws2 (the
  clone2-watch run started 11:56:56 was holding ws2).
- Laptop worktree /tmp/click4-live-confirm was at b57f499 (the Codex
  log commit, pre-P2 code). Fetched origin/todolist-push, checked out
  e68e578 (origin tip at the time; docs-only delta over f1b85ee, code
  identical to 292753f). Verified SHA-256 of the four stage scripts
  on the laptop against the VM copy at 292753f: zen_dom
  7a44a1fd8cdec7df709d4390d62c25ecdc0333ea66bd8fee2198c31bcbae88ad,
  zen_backend
  3694fc9880f92bb393fafaf4c7931efb331a3f003f7b98c13e5f3153cc8263db,
  dom_act ab89f2932d675888b4c78658f8ef797e80f41ee6168fedeb91e9d898ebbabfb9,
  fastpath c76a9b10c3a78ae64eefe58eab46a862aaec75cb171ac22d59a2e5788513eac1.
  All four match exactly. Clean tree.

## 2. Unit evidence (VM, T+2m, about 12:00 +07)

Test command: `cd tests && PYTHONPATH=../scripts:. python3 -m unittest
test_p2_element_ref test_zen_dom`. Result: Ran 128 tests, OK
(0.488s). The F9/F10 tests are in test_p2_element_ref.py:
test_factor_forgotten_origin_still_refused (F10, factor 2),
test_missing_factor_still_refused (F10), the factor-2 small-window
test (F9, fit invariant). Live F9/F10 checks are in section 7.

## 3. Run v1 (2026-11-22 12:01:24-12:01:25 +07, elapsed 1.19s, FAIL)

Script: ~/workspace/c5-validator-proof.py, SHA-256
63217395fc2674bdf0d263b0f496594a0617400fcb3881434f0bf8e464c66a8a,
laptop copy /tmp/c5-validator-proof.py, SHA verified identical.
Output: /tmp/c5-validator-proof.json (11232 bytes). Exit 1.

- Phase A re-measure: window [2509, 914] [925, 1176], monitor
  [2464, 902, 1920, 1200]. locate('#c5-text') OK, 4.0ms, rect
  {x: 12, y: 12, width: 420, height: 28, center: (222, 26)}.
  _check_window_not_moved OK, 4.7ms. viewport_origin UNVERIFIED
  FAILS, 3.1ms, ZenDomError: "dimension closure fails: mozInner
  [274, 66] + inner [677, 1160] exceeds window size [925, 1176]
  (gaps -26, -50)". Reported moz (274, 66), inner (677, 1160),
  outer (925, 1176), DPR 1, screenPixelsPerCSSPixel null, zoom 1,
  factor 1. Closure FAILS on the reported moz, reproduced.
- Phase B pixel proof: grim of the Zen window region. Whole-window
  bbox left 15 (polluted, see below); page-area bbox (x >= 240)
  left 248, top 16, right 675, bottom 119, giving verified moz
  (240, 8). BUT the dense-block method took min/max x over ALL
  white pixels in dense rows, so sparse bright sidebar glyphs (a
  10px run at x 17-26, visible while Zen is unfocused) dragged its
  left edge to 15, giving a WRONG verified moz [7, 8]. The script
  used the dense value. pixel_methods_agree False.
- Phase C: viewport_origin with verified [7, 8] returned
  (2516, 922) (correct behavior for the wrong input; the validator
  itself is not at fault). backend _screen_point [2971.0, 948.0]
  matched the direct fastpath point. Cross-check patch was white
  (255) at the computed point, but computed origin (2516, 922) did
  NOT equal the pixel origin (2749, 922). F9/F10 all refused;
  verified control passed (for the wrong verified value).
- Verdict FAIL. Cause: the probe's pixel method, not the validator.
  The page-area method in the same run gave the correct (240, 8).
- Cleanup: scratch removed true, original tab restored true,
  session closed true. Window unchanged after.

## 4. Run v2 (2026-11-22 12:04:56-12:04:59 +07, elapsed 3.11s, FAIL)

Script: ~/workspace/c5-validator-proof2.py, SHA-256
2d061cd636f6bc1659b040be74443a0a09fe278c03b748914e4ac0d9e99d1599,
laptop copy /tmp/c5-validator-proof2.py, SHA verified identical.
Output: /tmp/c5-validator-proof2.json (11207 bytes). Exit 1.

- NEW FINDING 1, decisive: mozInnerScreen is NOT stable. The
  8-read stability series (250ms apart, right after scratch
  creation) read (274, 66) at t=0.047s and t=0.299s, then (240, 8)
  from t=0.552s onward (6 reads). The (274, 66) value is a STALE
  read in the first ~300ms after the scratch tab is activated; it
  then settles to the true (240, 8) and stays. That is why v1
  phase A (t=0.064s) read (274, 66) but phase C (t=1.13s) read
  (240, 8): v1's phase C viewport_origin returned (2749, 922) with
  last_geometry_warnings EMPTY, i.e. it took the NORMAL path, not
  the verified path. Every earlier probe (ITEMS56, MOZ-GROWTH) did
  ONE read per fresh session within ~100ms of the switch, so it
  always sampled the stale value. The stale value is real and
  reproducible, but it is transient, not the stable state.
- Phase A: by the time the unverified call ran, moz had settled,
  so viewport_origin UNVERIFIED PASSED with (2749, 922) (2.0ms).
  The closure failure was NOT reproduced in this run.
- Phase B pixel proof: page-area bbox (248, 16)-(675, 119),
  verified (240, 8). Row 18 longest run (248, len 428) agreed on
  x. BUT the longest-run column method was wrong for y: the 1px
  input/textarea borders split column x=400 into runs, and the
  LONGEST run is the textarea (start 53, len 62), not the host top
  (16). So verified_moz_longest_run was [240, 45] and
  pixel_methods_agree_1px False. Row 60 diagnostic runs confirm
  the geometry: [17, 26, 10] (sidebar glyph), [248, 251, 4] (host
  padding), [253, 670, 418] (input), [672, 675, 4] (host padding).
- Phase C: viewport_origin verified (240, 8) returned (2749, 922),
  1.1ms; warnings empty (moz settled, normal path). Backend point
  [2971.0, 948.0] matched direct. Cross-check: computed origin
  equals pixel origin true, patch white (255). F9/F10: factor
  forgotten at factor 2 refused with exactness ("absolute viewport
  origin [2749, 922] is not window origin [2509, 914] plus mozInner
  [240, 8] times factor 2 (expected [2989, 930])"); missing factor
  refused; factor-2 small window refused via the fit invariant;
  raw moz as absolute refused via exactness; verified control
  passed with (2749, 922).
- Verdict FAIL, on two counts only: the unverified call passed
  (moz settled before it ran) and the pixel y-method disagreed.
  The origin itself was proven in this run (computed == pixel),
  but the verified path was not exercised.
- Cleanup: scratch removed true, original tab restored true,
  session closed true. Window unchanged after.

## 5. Run v3 (2026-11-22 12:07:05-12:07:07 +07, elapsed 1.20s, PARTIAL)

Script: ~/workspace/c5-validator-proof3.py, SHA-256
cbf05964e7ecbc86d79e2a5a083781b2afef1157d610c5438d9b88df9d657a5e,
laptop copy /tmp/c5-validator-proof3.py, SHA verified identical.
Output: /tmp/c5-validator-proof3.json (10107 bytes). Exit 1.

- Structure: two sessions. Session 1 measured the verified moz by
  pixel proof; session 2 opened a FRESH session, switched to the
  scratch tab, and ran the origin stage immediately (~10ms after
  the switch) to catch the stale window.
- Session 1 pixel proof: page-area bbox (248, 16)-(675, 119) and
  runs method (row 18 longest run start 248 len 428; column 400
  FIRST run start 16 len 4) AGREED: verified moz (240, 8), verified
  origin (2749, 922). pixel_methods_agree_1px True. Row 60 runs
  identical to v2. Window unchanged after session 1.
- Session 2 origin stage: switch 0.002s, host still present true,
  locate OK 1.0ms, _check_window_not_moved OK 4.3ms,
  viewport_origin verified (240, 8) returned (2749, 922), 1.9ms,
  verified call 0.010s after the switch. Backend _screen_point
  [2971.0, 948.0] matched the direct fastpath point. Unverified
  call after the stage also passed (2749, 922). Cross-check:
  computed origin equals pixel origin true, patch white (255).
  F9/F10 all refused with the same messages as v2; verified
  control passed.
- BUT verified_path_exercised False: the verified call's own moz
  read was (240, 8), already settled, warnings empty. Session 1
  had activated the scratch tab 1s earlier, so the stale value did
  not recur on session 2's switch. The stale state recurs only
  after an idle gap, not on every switch: v1 (36min gap) and v2
  (3min gap) both read stale first; v3 session 2 (1s gap) read
  settled. The refresh is triggered by tab activation, not by the
  moz read (session 1 never read moz, session 2 still got the
  settled value).
- Verdict PARTIAL: the origin is proven end to end, but the
  verified path was not exercised live.
- Cleanup defect (mine, recorded): original_tab_restored False.
  The restore used session 1's original handle inside session 2,
  and window handles are per-Marionette-session, so the switch
  failed silently. The visible tab was left on the blank scratch
  tab (scratch removed true, so an empty about:blank tab).

## 6. Restore incident and remediation (T+11m to T+12m, 12:08:02-12:09:01 +07)

- First restore attempt (12:08:02 +07, script /tmp/c5-restore-tab.py):
  scanned the 18 tab handles in order, reading each URL. It died
  on the 5th handle with ZenDomError: HTTP 500 "unexpected alert
  open", "Unexpected alert dialog detected. Performed handler
  dismiss". The alert was on the 5th tab in handle order (YouTube,
  Reddit, Todoist, Gmail, then the 5th). By elimination from the
  second scan's order, the 5th tab is Google Calendar
  (https://calendar.google.com/calendar/u/1/r/week), and the first
  attempt left the Calendar tab selected, which matches. The alert
  TEXT is unknown: the driver's unexpected-alert handler dismissed
  it before its text could be read. Nothing else was touched; the
  script died immediately (no further tab switches, no clicks, no
  keys). This worker did not create the alert deliberately; it was
  open on a pre-existing tab (or raised on switching to it) and was
  dismissed by the driver's default handler, not by a choice of
  mine. Recorded here because it is a real side effect on the
  owner's browser state, even though its content is unknown.
- Second restore attempt (12:09:01 +07, script
  /tmp/c5-restore-tab2.py, per-tab try/except): all 18 tabs read
  fine, no alert, no failures. Tab list: YouTube, Reddit, Todoist,
  Gmail, Google Calendar, Muse thread, Google Sheets, 127.0.0.1:8082
  admin/model_config, Welcome (zen-browser.app/welcome),
  about:blank (scratch tab), BytePlus Coding Plan, example.com,
  about:blank, about:blank, Polygon login, Codeforces, Chunkbase
  Biome Finder, duck.ai. Welcome tab handle 5f2413a7 selected,
  restored_to_welcome True. Active window still Brave on ws1 (no
  focus change by this worker). The blank scratch tab is empty
  again (scratch removed in v3). Post-state restored except for the
  dismissed Calendar alert, whose content cannot be recovered.
- The tab restore also starts the idle gap the v4 experiment needs:
  the scratch blank tab has been inactive since 12:09:01 +07.

## 7. Run v4 (2026-11-22 12:14:14 +07, elapsed 0.12s, PASS)

Script: ~/workspace/c5-validator-proof4.py, SHA-256
95c593a6cb735661756c40919e0ca6c67bcd9ee6518e68251a43e78b41e802dc,
laptop copy /tmp/c5-validator-proof4.py, SHA verified identical.
Output: /tmp/c5-validator-proof4.json (11247 bytes). Exit 0.

- Idle gap: no Zen touch from the 12:09:01 +07 tab restore to the
  v4 run at 12:14:14 +07 (5min 13s). The clone2-watch run started
  12:11:56 held ws2 across the run (active window before and after
  was clone2 Chrome on ws2); v4 needs no ws1, so the hold did not
  matter, and v4 changed no focus.
- Window re-checked before the stage: 0x557052b62dd0, [2509, 914]
  [925, 1176], monitor [2464, 902, 1920, 1200]. window_matches_v3
  True.
- First moz read, 0.002s after the switch: (274, 66), inner
  (677, 1160), outer (925, 1176), DPR 1. first_read_is_stale True.
  The 5-minute idle gap reproduced the stale state, confirming the
  v2/v3 model: the stale (274, 66) recurs after an idle gap and
  settles to (240, 8) within ~0.5s of tab activation.
- Origin stage, all inside the stale window (verified call 0.022s
  after the switch):
  - locate('#c5-text') OK, 8.0ms, rect {x: 12, y: 12, width: 420,
    height: 28, center: (222, 26)}.
  - dom_act._check_window_not_moved OK, 4.3ms (live origin equals
    meta origin).
  - viewport_origin UNVERIFIED: FAILS, 3.1ms, ZenDomError:
    "dimension closure fails: mozInner [274, 66] + inner [677, 1160]
    exceeds window size [925, 1176] (gaps -26, -50); the reported
    mozInner is displaced from the true viewport origin (pixel proof
    a42ef12: true origin (240, 8) on the live narrowed window);
    supply a verified mozInner (independent screenshot/click
    cross-check) to override". Metrics after the call still moz
    (274, 66). The ITEMS56/Codex failure is reproduced exactly,
    with the message preserved (procedure defect P1 closed).
  - viewport_origin VERIFIED with the measured (240, 8): OK, 1.7ms,
    returns (2749, 922). Metrics after the call still moz (274, 66).
    last_geometry_warnings: ["dimension closure overflow: reported
    mozInner [274, 66] + inner [677, 1160] exceeds window size
    [925, 1176] (gaps -26, -50); using verified mozInner [240, 8],
    verified origin [2749, 922]"]. The verified path fired, and the
    warning names the override. verified_path_exercised True.
  - ZenDomBackend._screen_point with verified_moz_inner (240, 8):
    OK, 1.4ms, [2971.0, 948.0]. Direct fastpath
    dom_rect_to_screen_point: OK, 0.0ms, [2971.0, 948.0].
    backend_point_matches_direct True. (The backend call took the
    verified path too: stderr shows the same closure-overflow
    warning three times in the run: the verified viewport_origin
    call, the backend _screen_point call, and the verified-control
    validator call.)
  - Computed origin (2749, 922) equals window origin [2509, 914]
    plus verified moz (240, 8), and equals the v3 pixel origin
    (2749, 922). Cross-check: screen point (2971.0, 948.0), window
    coords (462.0, 34.0), 5x5 patch around it pure white (mean 255,
    min 255), point_inside_white_input True (checked against the
    v3 screenshot /tmp/c5-validator-pixel3.png, same window state).
- F9/F10 (live numbers, moz (274, 66), inner (677, 1160)): factor
  forgotten at factor 2 refused via exactness; missing factor
  refused; factor-2 small window refused via the fit invariant;
  raw moz as absolute refused via exactness; verified control
  passed, (2749, 922). Messages are the same as in v2/v3 (section 8).
- Cleanup: scratch removed true, original tab restored true (the
  v3 cross-session handle bug is fixed: v4 records and restores the
  CURRENT session's own original handle), session closed true.
  Window unchanged after: [2509, 914] [925, 1176].
- Verdict PASS. Every gate in the task is met: the stage completes,
  the computed origin equals window origin + verified moz, the
  independent pixel cross-check agrees, F9/F10 are still refused,
  and the wiring works through the backend interface.

## 8. F9/F10 refusal evidence (live, all runs)

Live validator calls on the live geometry (window [2509, 914]
[925, 1176], inner [677, 1160], monitor [2464, 902, 1920, 1200]):

- F10 factor-forgotten at factor 2 (verified moz (240, 8),
  absolute (2749, 922), factor 2): REFUSED, exactness:
  "absolute viewport origin [2749, 922] is not window origin
  [2509, 914] plus mozInner [240, 8] times factor 2 (expected
  [2989, 930]); the origin was computed without the factor"
  (v2, v3).
- F10 missing factor (factor None): REFUSED: "viewport factor is
  required: pass the CSS-to-screen factor explicitly; a validator
  that silently assumes factor 1 accepts a factor-forgotten origin
  at factor != 1 (F10)" (v1, v2, v3).
- F9 factor-2 small window (window [462, 588], inner [677, 1160],
  factor 2): REFUSED, fit invariant: "viewport larger than window:
  inner [677, 1160] exceeds window size [462, 588]" (v1, v2, v3).
- Raw moz as absolute (absolute (240, 8), factor 1): REFUSED,
  exactness: "absolute viewport origin [240, 8] is not window
  origin [2509, 914] plus mozInner [240, 8] times factor 1
  (expected [2749, 922])" (v2, v3).
- Verified control (reported moz, verified (240, 8), factor 1):
  PASSES, returns (2749, 922) (v1 with the wrong [7, 8] input
  returned (2516, 922), correct behavior for that input; v2/v3
  return (2749, 922)).
- Unit evidence (VM, section 2): Ran 128, OK, including the F9/F10
  tests in test_p2_element_ref.py.

## 9. Wiring demonstration

- The measured verified moz (240, 8) passes through
  ZenDomBackend(verified_moz_inner=(240, 8)) into
  _screen_point, which calls session.viewport_origin with
  verified_moz_inner and then fastpath.dom_rect_to_screen_point.
  In v2 and v3 the backend point [2971.0, 948.0] exactly matched
  the direct fastpath point, and both equal the verified origin
  (2749, 922) plus the rect center (222, 26). backend_point_matches_direct
  True in v2 and v3 (and v1, with the wrong verified input).
- The value (240, 8) lives only in the probe logs and the runtime
  calls on the laptop (/tmp/c5-validator-proof*.json, /tmp/*.py).
  It is NOT supplied by any repo code path: verified_moz_inner
  defaults to None in scripts/zen_dom.py (check_viewport_geometry
  and viewport_origin) and in scripts/zen_backend.py
  (ZenDomBackend), and must be passed in by the caller. Precision
  note (grep, 2026-11-22 12:11 +07): the literal (240, 8) DOES
  appear in the repo as cited evidence in docstrings/comments
  (zen_dom.py:48, :115, :141, :206, :213, :772; fastpath.py:250)
  and as test-fixture input in tests/test_p2_element_ref.py and
  tests/test_pick4_fastpath.py. That is documentation and test
  data, not a hardcoded operational value: no production code path
  returns or defaults to it. The live value in this proof came only
  from the probe's own runtime pixel measurement.

## 10. Verdict

PASS. The step 7 P2 gate's live validator proof is proven on the real
Zen window 0x557052b62dd0 at [2509, 914] [925, 1176]:

- Re-measured geometry (v4, 12:14:14 +07): reported moz (274, 66),
  inner (677, 1160), outer (925, 1176), gaps -26/-50, closure FAILS
  on the reported moz (ITEMS56 failure reproduced with the message
  preserved).
- Measured verified moz (240, 8), re-measured live by pixel proof
  in v3 (two glyph-robust methods agreeing within 1px) on the same
  unmoved window; NOT assumed from the old logs (v1/v2 showed what
  happens with a wrong pixel method, and were reported as FAIL, not
  papered over).
- Origin stage live (v4): _check_window_not_moved OK (4.3ms),
  viewport_origin with the measured verified moz OK (1.7ms) returning
  (2749, 922), dom_rect_to_screen_point OK ([2971.0, 948.0]).
  Computed origin equals window origin + verified moz and equals the
  pixel-inferred origin; the 5x5 patch at the screen point is pure
  white (255). The backend wiring works: ZenDomBackend with
  verified_moz_inner (240, 8) returns the same point.
- F9/F10 still refused live (factor-forgotten at factor 2, missing
  factor, factor-2 small window, raw moz as absolute), and in unit
  tests (Ran 128, OK).
- New finding for the coordinator (not in the brief): mozInnerScreen
  is a TRANSIENT stale read, not a stable state. It reads (274, 66)
  on the first activation after an idle gap (v1 36min gap, v2 3min
  gap, v4 5min gap all read stale first) and settles to the true
  (240, 8) within ~0.5s of activation (v2 stability series flipped
  between 0.299s and 0.552s). Any future live probe that reads moz
  more than ~0.5s after tab activation will see the settled value
  and must NOT expect the closure failure; the verified path is
  exercised only inside the stale window. The P2 fix is still the
  correct shape: in the stale window the unverified call refuses
  and the verified call returns the true origin.
- Machine restored: Zen window unchanged, selected tab Welcome
  (verified 12:14:45 +07), scratch removed, no tab opened or
  closed, no window resized, no keystroke sent at any point. Final
  post-state check 12:17:16 +07: ws1 active, Brave
  0x55705383d420 active (the last-focused ws1 window, same as the
  11:58 pre-state), Zen 0x557052b62dd0 unchanged at [2509, 914]
  [925, 1176] ws1.
  defects of mine are recorded, not hidden: the v3 cross-session
  tab-restore miss (remediated 12:09:01 +07, fix verified in v4)
  and the Google Calendar alert dismissed by the driver's default
  handler during the first restore scan (section 6, text unknown).

## 11. Evidence index

- Probe scripts (VM and laptop copies, SHAs verified identical
  before each run): c5-validator-proof.py
  63217395fc2674bdf0d263b0f496594a0617400fcb3881434f0bf8e464c66a8a,
  c5-validator-proof2.py
  2d061cd636f6bc1659b040be74443a0a09fe278c03b748914e4ac0d9e99d1599,
  c5-validator-proof3.py
  cbf05964e7ecbc86d79e2a5a083781b2afef1157d610c5438d9b88df9d657a5e,
  c5-validator-proof4.py
  95c593a6cb735661756c40919e0ca6c67bcd9ee6518e68251a43e78b41e802dc.
  Laptop scripts at /tmp/c5-validator-proof.py,
  /tmp/c5-validator-proof2.py, /tmp/c5-validator-proof3.py,
  /tmp/c5-validator-proof4.py.
- Probe JSONs on the laptop: /tmp/c5-validator-proof.json (v1),
  /tmp/c5-validator-proof2.json (v2), /tmp/c5-validator-proof3.json
  (v3), /tmp/c5-validator-proof4.json (v4). Screenshots:
  /tmp/c5-validator-pixel.png (v1), /tmp/c5-validator-pixel2.png
  (v2), /tmp/c5-validator-pixel3.png (v3, reused by v4).
- Code executed on the laptop: /tmp/click4-live-confirm at
  e68e578, scripts SHAs listed in section 1, matching the VM copy
  at 292753f exactly.
- Repo state for this log: branch todolist-push. No code changed.
  No keystroke sent by this worker at any point. No tab opened or
  closed, no window resized, no chat thread, Brave, or Chromium
  endpoint touched, except the Calendar alert dismissal recorded
  in section 6 (driver default handler during the tab restore
  scan) and the v3 cross-session tab-restore miss (remediated
  12:09:01 +07).
- No stall over 15 minutes at any point; the v4 idle gap
  (12:09:01 to the v4 run) is a deliberate experiment, logged
  here, not a stall.
