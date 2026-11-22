# COORD-CLICK-14: ZT-B run 6 - PASS, F4 fix verified live

## Result

**Run 6 PASS.** Outcome sent, wall 87387.9ms. All phases 1-6
PASS. F4 (dom-value) is GONE. ZT-B is DONE. A1 resume is
unblocked.

## Phase by phase

- **Phase 1 PASS:** Zen 0x56307e2771d0 ws1, bounds [2509, 914,
  1863, 1176] (full width, OmaCal closed 22:03). tabs_before
  19 (same as run 5; the owner reopened the Chat - Muse tab),
  current Chat - Muse. Liveness live false (relay finished,
  owner s2-flip-run6, guardian clean, recovery none, 11 stale
  lease files evidence only).
- **Phase 2 PASS:** open ok, count 19 up to 20, selected_by
  explicit-select, URL fixture, H1 'Clone zen thread',
  viewport_ok true, innerWidth 1615, innerHeight 1160, rect
  x 20 y 228.87 w 340 h 36, element_at_point 'msg-input',
  harvest moz_inner [261, 23].
- **Phase 3 PASS:** switch ok, probe ok (PROBE zen-1,
  fixture URL, 1 element, wall 2080.9ms, envelope
  652.935ms), pre-checks clean (H1 correct, bubble false,
  input empty, input_events 0).
- **Phase 4 PASS:** send_switch ok, dom_act ok True,
  completed 4, error None, elapsed_ms 5745.525. Send URL
  and count gates pass (fixture URL, 1 element). F4 is
  GONE: set_value on #msg-input succeeded.
- **Phase 5 PASS:** post bubble_present true, bubbles ==
  [ZEN-DELEGATE-R6-IGNORE-TEST], input_value '',
  input_events 27. Retry already-sent, bubbles_after_refusal
  == [MESSAGE]. Delayed count 1. P9 ok, reviewed by sight:
  bubble ZEN-DELEGATE-R6-IGNORE-TEST visible, "sent:
  ZEN-DELEGATE-R6-IGNORE-TEST" below the input, input
  empty, pill "Computer use active" visible top center.
  Pill-during ok.
- **Phase 6 cleanup PASS:** close ok (count 20 down to 19),
  current restored to Chat - Muse
  (https://muse.ai/thread/[THREAD-ID]),
  original_restored true, count_restored true, zen_alive
  true, same address true. Cleanup ok is TRUE this time,
  not the spurious "Browsing context has been discarded"
  error from runs 3, 4, and 5; the F4 bonus fix f1cb4d5
  fixed it.

## F1/F2/F3/F4

- **F1: NOT EXERCISED** (no fallback needed, scan read the
  current tab normally). F1 was proven live in run 4.
- **F2: PARTIAL PASS, as in runs 4 and 5.** The
  dimension-closure error is gone. The settle numbers are
  still not surfaced in the envelope (known open follow-up,
  not a gate).
- **F3: PASS.** The "point outside observed image" error is
  gone in runs 5 and 6. The screen-point to image-point fix
  (c3954e3) holds.
- **F4: PASS, proven live in run 6.** The dom-value error
  is gone; set_value completed 4/4 with error None. All 4
  layers of the fix are live on the laptop (71ad538, ccb0f1e,
  66c34f8, 9858d9a, f1cb4d5). Council LAND 423/423, redteam
  LAND 24/24, tests 425/425 PASS, f4diag runs 11, 12, 13 all
  4/4. No new error in run 6.

## Safety

- No owner tab closed or navigated: 19 tabs before, 19
  tabs after, URL sets identical (only before [], only
  after []), current restored to Chat - Muse. Only the
  scratch fixture tab was opened and closed. The Chat -
  Muse tab was NOT reopened; it was already open and the
  run restored to it.
- No input sent anywhere except the fixture (the single
  test message into the local file fixture).
- Pill covered every control: acquire 01:54:05 +07, holder
  S2-flip:373168, visible true, label "Computer use
  active" (the new plain label, commit 163e90c, live on
  the laptop), pre-run grim reviewed by sight (pill VISIBLE
  top center), holder re-check before send, release ok,
  end holders {} visible false.

## Evidence (Lauren Tan)

- Runner: commit dd9ed0f, ls-remote
  dd9ed0f592ae9ea94627cf812deb902edffe3525. G0a 194 tests OK
  in 17.709s, G0b both programs validate, G0c fixture sha
  matches, G0d fresh intent and message.
- Run 6: launch 01:54 +07, wall 87387.9ms, outcome sent.
  JSON improvements/c5-zenproof-runs/run-6.json, sha256
  bd5e7f140ac900f8a448c3e9a0703ad1ba361a5d66f9bc9b8908f66b364107e9.
- Run log:
  improvements/c5-zenproof-runs/c5-zen-delegate-run6-log.md.
- Coord log: improvements/coord-click-14-log.md (this file).
- End-state list
  improvements/c5-zenproof-runs/list-after-r6.txt: count 19,
  URL sets identical to tabs_before, current restored to
  Chat - Muse.
- Pre-run grim /tmp/c5-zenproof-6/pill-pre-r6.png, 710432
  bytes, sha256
  24b17378314349e4ff493e4387d0db74410fa62f0e570376ee789ee0673cbef9.
- P9 /tmp/c5-zenproof-6/p9-zen-r6.png, 1605151 bytes,
  sha256
  d19c5b89eb323ae42b471405a08864c8a714e609f5c0bdb98e45d8890f067b6e.
- Pill-during /tmp/c5-zenproof-6/pill-during-r6.png.
- Evidence commit to follow (4 files, same shape as run 5
  commit 0400e86).

## What is next

1. **ZT-B is DONE.** No further ZT-B run is needed. The
   live sequence step 1 is complete.
2. **A1 resume is UNBLOCKED.** Muse tong issues the A1
   resume order (single-lane, ZT-B now done). The draft
   order is in improvements/w-a1prep2-log.md section 4
   (commit f64ba70); at resume, re-verify the relay with a
   FRESH H2 (the recorded relay head 4eb5917 is stale,
   never use a recorded HEAD value), re-probe was 5/5 PASS
   21:47, fixture tabs disposition done 22:05, idle check
   must accept broker finished + driver stopped +
   active_sequence null and confirm the cleanup_failed
   marker clears after restart.
3. **Rung 3 is unblocked on the ZT-B side.** The remaining
   rung-2 items are the A1 resume, mochi B2-4/B2-6, and
   mei's F4 root-cause investigation (parallel, already
   assigned).
4. Open follow-ups (not gates): last_viewport_settle
   surfacing in the envelope; F1 fallback not exercised in
   runs 5 and 6 (proven live in run 4).
