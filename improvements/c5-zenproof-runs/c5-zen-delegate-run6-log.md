# W-ZT-B: Zen pointer delegate live proof, run 6 (F4 verification)

Owner: the owner. Coordinator: COORD-CLICK-14. Worker: W-ZT-B.
Repo ~/workspace/computer-use-wayland, branch todolist-push.
No em dash or en dash anywhere in this file. No personal info.
Report goes to COORD-CLICK-14, not directly to the owner.

## 0. Task receipt and sources read (before any live touch)

- Task received 01:52:22 +07, 23/11/2026. T+0m. Single lane,
  quiet machine, owner confirmed at 23:58 the user is not touching
  the machine and every machine-activity alarm is a false alarm,
  live work authorized.
- Sources read before running:
  - improvements/w-zen-delegate-liveproof-prep.md (procedure
    phases 0-7, scratch target
    tests/two_vision_fixture.html?clone=zen, viewport gate P2.4,
    send program phase 4, pass only when dom_act ok True,
    completed 4, error None, post-checks P5.1, retry already-sent
    P5.2, delayed count 1 P5.3, P9 screenshot reviewed by sight
    P5.4, cleanup P6).
  - improvements/c5-zenproof-runs/c5-zen-delegate-run5-log.md
    (run 5: phases 1-3 PASS, phase 4 refused by the NEW error
    F4 "action_failed, dom-value", completed 0, no input sent;
    F3 point error gone, F2 partial pass).
  - improvements/c5-zenproof-runs/run-5.json (run 5 result:
    program error "action_failed, dom-value", wall 40963.3ms,
    tabs_before 19).
  - improvements/f4-reviews/ (F4 review evidence, commit
    0031449: fix commits 71ad538, ccb0f1e, 66c34f8, 9858d9a,
    f1cb4d5; council LAND 423/423; redteam LAND 24/24; tests
    425/425 PASS; live f4diag runs 11, 12, 13 all 4/4; bubble
    sent correctly; cleanup clean).
- Hard rules restated: never close or navigate any tab of the
  owner; do NOT reopen the Muse chat tab (the owner reopened
  it, it is the current tab and the run restores to
  it); pill must show on any agent control (gate 4.29); on a
  'not made current' refusal, STOP at once, no retry open in
  a loop, no DELETE via Marionette, report to the
  coordinator; if any owner tab is closed or navigated wrong,
  or the pill is not visible during control, STOP at once and
  report; no em dash; no ydotool; no personal info on GitHub;
  log continuously with wall-clock Asia/Ho_Chi_Minh plus
  elapsed; commit with an explicit pathspec, never bare
  commit, never add -A; if run 6 still refuses, record the
  error, STOP, report, do NOT self-fix.
- This run is run 6, NEW run number, NEW intent
  c5-zen-delegate-r6, NEW message ZEN-DELEGATE-R6-IGNORE-TEST.
  It verifies the fix landed after run 5: F4 (four layers:
  mid-transition batch meta, fcitx5 Telex doubling, stale
  batch meta after type, assert on a bubble that never
  passes; fix commits 71ad538, ccb0f1e, 66c34f8, 9858d9a,
  f1cb4d5), on top of the F3, F1, and F2 fixes already
  proven in runs 4 and 5.

## 1. Time log (wall-clock Asia/Ho_Chi_Minh, elapsed from 01:52:22 +07 23/11)

- 01:52:22 +07 23/11, T+0m: task received. VM HEAD 0031449,
  branch todolist-push, origin equal. Sources read (section 0).
- 01:52 +07, T+0m: run6.py created by copying run5.py,
  diff limited to the briefed renames (docstring run 6 plus
  coordinator COORD-CLICK-14 plus the F4 fix note, RUN_NO 6,
  MESSAGE/INTENT R6, WORKDIR /tmp/c5-zenproof-6, run-6.json,
  p9-zen-r6.png, pill-during-r6.png, usage line). py_compile
  OK, 0 em dash, 0 en dash. Fixture sha on the VM matches.
- 01:53 +07, T+1m: phase 0 gates (section 2): G0a 194 OK in
  17.709s, G0b both programs validate, G0c fixture sha matches,
  G0d fresh intent and message.
- 01:53 +07, T+1m: runner commit dd9ed0f created. Push
  succeeded, ls-remote
  dd9ed0f592ae9ea94627cf812deb902edffe3525.
- 01:53 +07, T+1m: laptop as-found read-only checks
  (section 2): Zen 0x56307e2771d0 on ws1, bounds [2509, 914,
  1863, 1176], FULL WIDTH 1863; active window Zen (Chat -
  Muse); 19 tabs (same as run 5; the owner reopened the
  Chat - Muse tab and has other tabs); laptop repo at
  0031449, equal to the VM HEAD; all 5 F4 fix commits
  present; fixture sha matches; geckodriver present; pill
  OFF (holders {}, visible false); fixture server root
  HTTP 200 (PID 45976, serves /tmp/a1fix-20261122/fixtures;
  the /tests path 404s because that is not its root, the
  runner uses a file:// URL so the server is not used).
- 01:54:05 +07, T+2m: pill acquire (section 3). Holder
  S2-flip:373168, visible true, label "Computer use active"
  (the new plain label, commit 163e90c, live on the laptop).
- 01:54 +07, T+2m: pre-run grim reviewed by sight: pill
  VISIBLE top center, label "Computer use active", green
  dot. The screen shows the owner's Chat - Muse thread
  (this side chat) in Zen, untouched.
- 01:54 +07, T+2m: run 6 launched detached,
  PILL_SLEEP_PID=373168.
- 01:56 +07, T+4m: run 6 finished, wall 87387.9ms,
  outcome sent, program ok True, completed 4, error None.
  Bubble sent correctly. Pill released ok.
- 01:56 +07, T+4m: end-state verification (section 6):
  independent fresh list, count 19, exact original URL set,
  current restored to Chat - Muse, no fixture tab. Pill
  holders {}, visible false; no live session-driver.
- 01:57 +07, T+5m: evidence copied to the repo, log
  written, report to COORD-CLICK-14. ZT-B done. No stall
  over 15 minutes at any point in this task.

## 2. Phase 0 gates (VM, no live touch) and the run6.py runner

- G0a PASS, 01:53 +07: `python3 -m unittest
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec` returned Ran 194 tests in 17.709s,
  OK. (180 in run 5 + 14 new F4 regression tests.)
- G0b PASS, 01:53 +07: probe program and send program
  (run 6 text, message ZEN-DELEGATE-R6-IGNORE-TEST) both
  pass code_exec.validate_program with no exception.
- G0c PASS, 01:53 +07: `sha256sum
  tests/two_vision_fixture.html` on the VM =
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6cbf,
  matching the manifest. Same hash on the laptop.
- G0d PASS: fresh intent c5-zen-delegate-r6, fresh message
  ZEN-DELEGATE-R6-IGNORE-TEST for run 6.
- Runner run 6: improvements/c5-zenproof-runs/
  c5-zen-delegate-run6.py, copied from the run 5 runner
  (c5-zen-delegate-run5.py, which itself was copied from the
  run 4 runner). Diff run5 to run6 limited to the briefed
  renames plus the docstring (run 6, COORD-CLICK-14, F4 fix
  note). Everything else (transport, phases, programs,
  gates, pill handling, grim Wayland-env prefix) is
  byte-identical to run5.py. py_compile OK. 0 em dash, 0 en
  dash in run6.py. Commit dd9ed0f pushed and ls-remote
  verified before the run.
- Laptop sync: not needed. The laptop checkout was already
  at 0031449, equal to the VM HEAD. All 5 F4 fix commits
  present (71ad538, ccb0f1e, 66c34f8, 9858d9a, f1cb4d5).
  The laptop working tree had only the 2 pre-existing
  untracked files (improvements/cf26-polygon-upload-lessons-
  20261120.md, improvements/latency-probe-20261120-results.csv),
  no tracked modifications, left alone.

## 3. Pill verification (gate 4.29)

- Pill started OFF for this run (holders {}, owner none,
  visible false), confirmed by read-only status check at
  01:53 +07.
- Acquire 01:54:05 +07: holder S2-flip:373168, method CDP,
  acquired 2026-11-23T01:54:05+07:00. Status reports visible
  true and the exact holder key alive.
- Pre-run grim /tmp/c5-zenproof-6/pill-pre-r6.png, 710432
  bytes, sha256
  24b17378314349e4ff493e4387d0db74410fa62f0e570376ee789ee0673cbef9:
  reviewed by sight, pill VISIBLE top center, label
  "Computer use active", green dot. Zen shows the owner's
  Chat - Muse thread. No tab navigated or closed, only the
  grim read.
- Runner re-verified the holder at start (from_env true)
  and re-checked it immediately before the phase 4 send.
- Pill-during grim /tmp/c5-zenproof-6/pill-during-r6.png
  captured while the hold was up, ok true.
- Release after cleanup: ok true, pid 373168. End status
  holders {}, visible false.

## 4. Run 6 result, phase by phase

- Outcome: sent. Wall 87387.9ms (longer than run 5's
  40963.3ms; the F4 fix adds settle steps, expected).
- Phase 1 PASS: Zen 0x56307e2771d0 ws1, bounds [2509, 914,
  1863, 1176] (full width). tabs_before 19, current Chat -
  Muse. Liveness live false (relay finished, owner
  s2-flip-run6, guardian clean, recovery none, 11 stale
  lease files recorded as evidence only).
- Phase 2 PASS: open ok, count 19 up to 20, selected_by
  explicit-select, URL fixture, H1 'Clone zen thread',
  viewport_ok true, innerWidth 1615, innerHeight 1160,
  rect x 20 y 228.87 w 340 h 36, element_at_point
  'msg-input', harvest moz_inner [261, 23].
- Phase 3 PASS: switch ok, probe ok (PROBE zen-1, fixture
  URL, 1 element, wall 2080.9ms, envelope 652.935ms),
  pre-checks clean (H1 correct, bubble false, input empty,
  input_events 0).
- Phase 4 PASS: send_switch ok, dom_act ok True,
  completed 4, error None, elapsed_ms 5745.525, wall
  7172.5ms. Send URL and count gates pass (fixture URL,
  1 element). F4 is GONE: set_value on #msg-input
  succeeded, no dom-value error. No F1 fallback needed
  (scan read the current tab fine). No F2 dimension-closure
  error. No F3 point-outside-image error.
- Phase 5 PASS: post bubble_present true, bubbles ==
  [ZEN-DELEGATE-R6-IGNORE-TEST], input_value '', input_events
  27. Retry already-sent, bubbles_after_refusal ==
  [MESSAGE]. Delayed count 1. P9 ok (p9-zen-r6.png, wall
  1571.0ms), reviewed by sight: bubble
  ZEN-DELEGATE-R6-IGNORE-TEST visible at the top of the
  thread, "sent: ZEN-DELEGATE-R6-IGNORE-TEST" below the
  input, input empty, pill "Computer use active" visible
  top center. Pill-during ok.
- Phase 6 cleanup PASS: close ok (count 20 down to 19),
  current restored to Chat - Muse
  (https://muse.ai/thread/[THREAD-ID]),
  original_restored true, count_restored true, zen_alive
  true, same address true. This time cleanup ok is TRUE,
  not the spurious "Browsing context has been discarded"
  error seen in runs 3, 4, and 5; the F4 bonus fix f1cb4d5
  (cmd_close fallback window after DELETE) fixed it.

## 5. F1/F2/F3/F4 status after run 6

- F1: NOT EXERCISED in run 6 (no fallback needed, scan
  read the current tab normally). F1 was proven live in
  run 4.
- F2: PARTIAL PASS, as in runs 4 and 5. The
  dimension-closure error is gone. The settle numbers are
  still not surfaced in the envelope (known open
  follow-up, not a gate).
- F3: PASS. The "point outside observed image" error is
  gone in runs 5 and 6. The screen-point to image-point
  fix (c3954e3) holds.
- F4: PASS, proven live in run 6. The dom-value error is
  gone; set_value completed 4/4 with error None. All 4
  layers of the fix are live on the laptop (71ad538,
  ccb0f1e, 66c34f8, 9858d9a, f1cb4d5).
- ZT-B is DONE. No new error in run 6.

## 6. End-state verification and evidence

- Independent fresh list after the run: count 19, current
  Chat - Muse
  (https://muse.ai/thread/[THREAD-ID]),
  no fixture tab. URL sets before and after are identical
  (verified programmatically: only before [], only after []).
- No owner tab closed or navigated. Only the scratch
  fixture tab was opened and closed. The Chat - Muse tab
  was NOT reopened; it was already open and the run
  restored to it.
- No input sent anywhere except the fixture. Pill covered
  every control, released ok, holders {} visible false
  after. No live session-driver. Relay back to serve idle.
- Evidence:
  - run-6.json sha256
    bd5e7f140ac900f8a448c3e9a0703ad1ba361a5d66f9bc9b8908f66b364107e9
  - improvements/c5-zenproof-runs/run-6.json
  - improvements/c5-zenproof-runs/c5-zen-delegate-run6-log.md
    (this file)
  - improvements/coord-click-14-log.md
  - improvements/c5-zenproof-runs/list-after-r6.txt
  - /tmp/c5-zenproof-6/pill-pre-r6.png (710432 bytes, sha256
    24b17378314349e4ff493e4387d0db74410fa62f0e570376ee789ee0673cbef9)
  - /tmp/c5-zenproof-6/p9-zen-r6.png (1605151 bytes, sha256
    d19c5b89eb323ae42b471405a08864c8a714e609f5c0bdb98e45d8890f067b6e)
  - /tmp/c5-zenproof-6/pill-during-r6.png
- Runner commit dd9ed0f, ls-remote verified. Evidence
  commit to follow in the coord log.
- Next: A1 resume is unblocked. Muse tong issues the A1
  resume order (single-lane, ZT-B now done). Rung 3 is
  unblocked on the ZT-B side.
