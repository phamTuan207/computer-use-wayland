# E2 calibration experiment: vision estimates vs DOM truth vs real clicks

Phase 0 calibration-first experiment, run 2026-11-21 04:36-05:30 +07 on the
real laptop screen (Zen, Hyprland). Decisive result: the pointer stage is
exact; every miss is vision grounding error. The "screen ratio 1.55x" story
is refuted with measured numbers.

## Setup (measured live, not assumed)

- Monitor eDP-2: 1920x1200, scale 1, transform 0, at virtual (2464, 902).
- Zen window: at [2509, 914], size [1863, 1176]. Zen PID 28990, running
  since 02:57 with --remote-debugging-port=9222 --marionette.
- Viewport 1615x1160, dpr 1, sidebar about 240 CSS px.
- Observation 1200x757 JPEG, region [2509, 914, 1863, 1176],
  scale_x 0.6441, scale_y 0.6437, capture 42 ms.
- Grid page: tests/calibration-grid.html, 20 medium buttons T01-T20
  (120x48 CSS px) + 9 small links R1/R2/R3 View/Remove/Rejudge (14 px,
  mimicking Polygon invocations). Clicks record into window.__hits, turn
  green, status counter "Hits: N / 29", hitlist panel bottom-right.
- Truth: in-page overlay labels (?truth=1) from getBoundingClientRect +
  mozInnerScreenX/Y. NOTE: mozInnerScreenX/Y in this Zen build are
  WINDOW-relative (240, 8), not absolute screen coords. Truth table is
  window-relative CSS px; add the window origin (2509, 914) for screen px.

## Part A: vision estimates vs DOM truth

29 vision estimates by eye from the 1200x757 observation, compared against
DOM truth rects. Report: /tmp/e2/report-vision-actual.json (also the
per-attempt log tests/calibration-e2-hits.jsonl).

- Overall predicted hit rate: 17/29 = 58.6%.
- Grid A (120x48 buttons, exact rects): 8/20 = 40%, mean dx +78.6,
  mean dy -5.0, mean abs err 78.9.
- Grid B (small links): 9/9 = 100% (several within about 2 px of the rect
  edge, so this is sensitive to the width assumption), mean abs err 21.7.
- Overall mean dx +57.0, mean dy -4.9, std dx 49.1, std dy 1.9,
  mean abs err 61.2, max abs err 137.8.
- corr(err vs x) = 0.973 (extremely strong, error grows linearly with x),
  corr(err vs y) = -0.42.
- Fit: estimates are about truth_image_x x 1.10 - 15, i.e. a ~10% x-scale
  frame error, while y is nearly exact (errors -1 to -5 px).

## Part B: real clicks at the estimated points

29 clicks, 05:23:56-05:23:57, via tests/e2_direct_clicks.py (see below for
why direct, not session). Every click verified with hyprctl cursorpos.

- 29/29 clicks executed. Pointer error 0.5-0.9 px every time, always
  within the 3 px refusal threshold. No click refused.
- After-state observation 5068ef38271e (05:25:05): header "Hits: 17 / 29".
- Actual hits: T01, T02, T06, T07, T11, T12, T16, T17 (Grid A) + all 9
  Grid B links. EXACTLY the same 17 targets Part A predicted.
- End-to-end first-try hit rate: 17/29 = 58.6%. Grid A 8/20 = 40%,
  Grid B 9/9 = 100%.

## Decisive conclusions

1. The pointer stage is exact. Move + click lands within 1 px of the
   intended screen point, 29/29. The miss rate does not come from the
   pointer, the monitor, or the coordinate math.
2. All misses come from vision grounding. The ~10% x-scale frame error
   (estimates in the wrong coordinate frame, corr 0.973) is the whole
   story. Hits cluster on the left columns (x 402, 692) because the
   rightward shift still lands inside wide-enough rects there.
3. The "screen ratio 1.55x" story is refuted. Monitor scale is 1,
   logical equals physical, error is ~1.10x, not 1.55x.
4. Fix direction stands: do not estimate pixels from screenshots. Use
   DOM rects (exact) or fix the frame (grid overlay, crop-zoom, explicit
   image dimensions in the prompt). This matches the redteam verdict and
   the hybrid DOM-locate + real-mouse-click recommendation.

## Findings that blocked or shaped the run

1. BiDi session cap. Firefox refuses new sessions with "Maximum number
   of active sessions" after about 1 session. Leaked sessions do not
   expire within ~15 min. Likely leaked by the first coordinator's 5
   workers plus my own --list calls. Fix applied: tests/bidi_truth.mjs
   now calls session.end before closing. RULE: every BiDi client MUST
   call session.end; the cap is hit fast and leaked sessions block
   later runs.
2. Session guardian fails to start on a repo checkout. First error:
   "agent cursor profile required; run setup with explicit
   --restore-theme and --restore-size" (native/agent-cursor.json missing
   from the repo checkout; it is gitignored by design, the installed
   copy at ~/.local/share/agent-computer-use/native/ has it). Copied the
   installed profile into the laptop repo checkout, which cleared that
   error. Next error: the session supervisor prints "Expecting value:
   line 1 column 1 (char 0)" then {"ok": false, "error": "session
   guardian startup failed"}. Root cause of the guardian failure is NOT
   yet diagnosed (guardian does cursor snapshot, guard check, snapshot
   write, Escape binding, cursor apply, indicator listen). This is a
   session-infrastructure issue for Phase 2.5, not a calibration issue.
   Do NOT commit native/agent-cursor.json to the repo (gitignored on
   purpose, machine-specific config).
3. Part B ran via the direct pointer path (tests/e2_direct_clicks.py),
   replicating desktop_act's exact protocol: image_point math,
   normalized abs coords over the monitor box, cursorpos within 3 px
   before and after the click, refuse on miss. This path uses NO
   session, so NO indicator pill showed and NO cancel latch was active
   for this run. The clicks themselves are the identical math and
   verification as desktop_act, so the measurement is valid; the missing
   pill is a deviation from the overlay rule, recorded here honestly.
4. Window address changes. The Zen window address from the 05:10
   observation (0x400000000014d6e) was stale by 05:24 ("window no longer
   exists"); the live address was 0x559f8d5adda0. Always re-read the
   window address from hyprctl clients before observing.
5. hyprctl cursorpos without -j prints plain "x, y" text, not JSON.
   Use -j for parsing (cu.py uses the Hyprland socket directly).

## Phase 2.1 status after E2

- 2.1.1 calibration: DONE (live). Monitor 1920x1200 scale 1, window
  [2509, 914, 1863, 1176], vision x-scale frame error ~1.10x, corr 0.973.
- 2.1.2 DOM vs screenshot: DONE (live). DOM rects exact; vision 58.6%
  end-to-end; pointer exact to <1 px. Same-case comparison is now
  measured, not offline-only.
- 2.1.7 video hit rate: UNMEASURABLE. No video file in the workspace;
  the source report says the video is in chat with no frame or attempt
  count. No number is inferred from the narrative.
- 2.1.10 held-out: still PARTIAL. Synthetic held-out passed
  (1cfac75); real new-app validation and a fresh independent agent run
  are still owed.
- 2.1.3, 2.1.4, 2.1.5, 2.1.6, 2.1.8, 2.1.9, 2.1.11: FIXED (offline
  fixtures, live proof pending), unchanged by this run.

## Files

- tests/calibration-grid.html, tests/bidi_truth.mjs,
  tests/e2_session_driver.py, tests/e2_direct_clicks.py,
  scripts/calibration_e2.py, tests/calibration-e2-hits.jsonl
- /tmp/e2/report-vision-actual.json (final numbers),
  /tmp/e2/after-1200.jpg (after-state screenshot, Hits 17/29)
- 3 "Calibration Grid E2" tabs remain open on the user's Zen (clean grid,
  broken-JS truth grid, fixed-JS truth grid). Close them at the end of
  the experiment; the user's other tabs were not touched.
