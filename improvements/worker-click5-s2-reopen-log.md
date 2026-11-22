# Worker C5-S2-REOPEN log: S2 flip re-open, two-browser 5-run measurement (Brave fill, Chromium b1 set_value)

Owner: Pham Tuan. Coordinator: COORD-CLICK-5. Repo
~/workspace/computer-use-wayland, branch todolist-push. This worker
did NOT do the original flip or the input fix, so this is
independent verification work. No em dash or en dash anywhere in
this file. No personal info. Wall-clock Asia/Ho_Chi_Minh plus
elapsed time on every entry.

## 0. Task and starting point

- Task received 12:56 +07, Sun 2026-11-22 (T+0m). VM HEAD 6805e10
  at start (coord log; includes 030c227, the INPUT-FIX head named
  in the brief). Origin todolist-push fast-forwarded to 6805e10
  before work (docs-only coord log commit, no code change).
- Final direction: improvements/worker-click3-final-direction-log.md
  (commit e05fc58). Plateau gate (COORD-CLICK-4, from the flip
  log section 0): median wall over 5 runs above 60s = plateau
  reached. Per-run completeness: both sends verified in a run.
- Original flip (improvements/worker-click4-s2-flip-log.md):
  median wall 33.2s, Brave 5/5 SENT with fill, Chromium 0/5,
  CDP timeout Input.dispatchMouseEvent, 0 model calls, per-send
  5/10. Verdict DO NOT EXPAND.
- C5-INPUT-FIX (improvements/worker-click5-input-fix-log.md,
  commit 4bd6292): (a1) CDP tab activation FAILED 0/5 live
  (median wall 32.9s; activation ok true all 5, run 1 even
  changed focus False to True and the mouse dispatch still timed
  out; one-off probe success 14ms did not reproduce). Stall is
  MOUSE-specific: Input.dispatchKeyEvent answers in 2ms on the
  stuck tab. (b1) set_value + focus + CDP key Enter WORKS 5/5
  on Chromium (median wall 18.8s; program ok True completed 2,
  elapsed 91.6-106.6ms; V12 attempt 1 all 5; CB-1 all three True
  all 5; pre-send count 0, delayed count exactly 1, all 5;
  0 model calls). Run 1 passed under the strict routing gate;
  runs 2-5 under a DISCLOSED relaxed gate (live thread grew past
  the 80-element snapshot cap; proceed when truncated but the
  composer is in the snapshot, recorded per run). P9 reviewed:
  R1 bubble in run 1 shot, R2-R5 bubbles in run 5 shot, composer
  empty, DOM and render agree.
- This re-open: full two-browser flip, 5 runs, same shape as the
  original flip. Brave with FILL (it already sends 5/5 with
  fill; do NOT change what works), Chromium with (b1) set_value
  + focus + CDP Enter. Keep the relaxed routing gate with
  per-run recording (do NOT raise the 80-element cap). Record per
  run: wall, per-browser outcome, program ok/completed/elapsed,
  V12 found/attempt, CB-1 all three, pre-send count, delayed
  count, model calls (must be 0), routing reason. Run JSONs:
  improvements/s2-flip-reopen-runs/run-1..5.json. P9: one final
  screenshot per run, reviewed before scoring (B1 condition: any
  DOM-vs-render mismatch FAILS the run).
- Focus rule (C5-FOCUS-INCIDENT, commit 2d198c4, section 7, read
  in full before acting): this task is CDP-only, no keystrokes
  at all. No hyprctl focus or workspace command is used anywhere
  in this task. Clone2-watch holds run :11:56, :26:56, :41:56,
  :56:56 (hold about start+1m to start+2m40s); the Brave fill
  uses mouse Input and Brave sits on ws1, so a run whose Brave
  send lands inside a hold risks the occlusion stall; runs are
  timed so each Brave send lands outside the holds, and every
  run records its own timestamps so a hold overlap would be
  visible. The Chromium set_value path uses zero mouse events
  and is hold-insensitive.
- Endpoints: Chromium 127.0.0.1:9223, live tab
  D1374C7C994D3DA72678E20C7FD099A0 ("Chat - clone2"); Brave
  [::1]:9223, tab 06074E282C000A95EF89CC9EBB8F9713. Never assume
  port 9223 is Brave.
- Test messages go into the clone1 and clone2 threads only,
  same as the flip runs did. Clone2 is capped until Nov 25
  02:38 (its account cannot work), but receiving test messages
  in its thread needs no clone2 activity. No other thread, no
  other tab.
- OPEN ITEM (do NOT do it in this task, recorded here): durable
  landing of the (b1) shape in cdp.mjs (a focus action, or
  set_value focusing the field) with tests. The measurement uses
  /tmp helpers plus harness flags; landing is follow-up work
  for step 8/9.

## 1. Time log

- 12:56 +07, T+0m: task received. Read the final direction, the
  flip log in full, the INPUT-FIX log in full, the P3 probe log
  in full, the FOCUS-INCIDENT section 7, scripts/cdp.mjs
  (set_value present) and scripts/s2_flip_live.py.
- 12:58 +07, T+2m: laptop pre-state via ssh-laptop.sh. Brave PID
  1003210, no debug flag, window 0x55705383d420 on ws1, active
  window Brave. Chromium PID 8059 with --remote-debugging-port
  =9223, exactly one page tab D1374C7C994D3DA72678E20C7FD099A0
  ("Chat - clone2"). [::1]:9223 closed. /tmp helpers present:
  s2-v12.mjs, s2-p9.mjs, s2-seed.mjs, c5-focusenter.mjs,
  c5-count.mjs, c5-activate.mjs. Relay PID 983809 alive, broker
  state finished, owner s2-flip-run5, guardian clean, laptop
  HEAD e68e578. Laptop cdp.mjs carries set_value (6 mentions).
  The (b1) runs at 12:44-12:51 already proved this relay plus
  laptop tree works with the current harness, so no relay
  restart and no laptop sync is needed.
- 12:59 +07, T+3m: clone1 state checked before the Brave
  relaunch. Coord log section 25: clone1 batch 11 DONE
  (summary 8020e31), task 4 dispatched 12:38 (a47a15b, close-out
  summary of clone2 batch 12). Watch runs 55 (12:41) and 56
  (12:56) observed ws1: Brave tiled, no cursor activity, no
  sign of active use. No clone1 commit since the 12:38/12:39
  watchdog notes. Batch 11 is done, so no open batch; the
  single dispatched task-4 agent works via git/CLI on its own
  machine, and the Brave chat tab restores from session files
  on relaunch (proven twice: P3 probe 08:50, flip 10:00).
  Relaunch proceeds per the task order, SIGTERM graceful so
  session files flush.
- 13:01 +07, T+5m: harness gap found and fixed. The harness
  carried ONE global program_variant, so --set-value would
  have forced set_value onto Brave too, changing what already
  works. Added --chromium-set-value (Brave fill, Chromium
  set_value), variant_for(browser), per-browser program_variant
  in the run JSON, delayed-count recount only for set_value
  browsers. New wiring test
  test_chromium_set_value_splits_variants_per_browser. Wiring
  tests 12/12 pass (was 11/11). Committed d90d1b9, push
  verified with git ls-remote (d90d1b917cc9e615158307e90315982bae86e796).

## 2. Brave relaunch with --remote-debugging-port=9223 (P3 procedure)

- 13:02:45 +07, T+6m: SIGTERM to Brave main PID 1003210.
  Graceful exit in 1s; no brave process remains. Chromium PID
  8059 untouched.
- 13:03:06 +07, T+7m: relaunched detached (setsid nohup, same
  as-found flags plus --remote-debugging-port=9223, log
  /tmp/s2-reopen-brave-debug.log), donor env from zen-bin PID
  496121 verified from /proc/496121/environ: WAYLAND_DISPLAY
  =wayland-1, XDG_RUNTIME_DIR=/run/user/1000,
  DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus. New
  main PID 1112207, cmdline carries the flag.
- 13:03:14 +07: [::1]:9223 serves exactly one page tab,
  FED133417A338D5B1596D60490746672, "Chat - clone1",
  https://muse.ai/?__pwa=1. Login intact (authenticated chat
  page, not a login redirect). NOTE: the tab id differs from
  the brief's 06074E282C000A95EF89CC9EBB8F9713 because tab ids
  are per-session and Brave restarted; the P3 probe likewise
  saw a different id (1563355BC...) after its relaunch. The
  harness looks the tab up by URL prefix, so the new id is
  fine. What is stable: one page tab, same title, same URL,
  same login.
- 13:03:32 +07: version split confirms no misattribution:
  [::1]:9223 reports Chrome/157.0.8103.79 (Brave),
  127.0.0.1:9223 reports Chrome/157.0.8103.38 (Chromium). ss
  shows 127.0.0.1:9223 owned by chromium PID 8059 and [::1]:9223
  owned by brave PID 1112207. hyprctl: Brave window back at
  the same address 0x55705383d420, ws1, PID 1112207; Chromium
  window unchanged 0x5570538ed160, ws2, PID 8059.
- The flag stays on for the 5 runs; the P3 rollback (relaunch
  without the flag) runs after run 5, section 7.

## 3. Dry run 0 (scratch tabs, both browsers)

- Command (13:03:51 +07):
  python3 scripts/s2_flip_live.py --run 0 --dry-run
  --chromium-set-value --message-prefix S2-REOPEN-DRY --workdir
  /tmp/s2-reopen-dry
- Result: PASS, 13:03:51-13:04:38 +07. Wall 30123.9ms (dry run
  seeds, not comparable). Both browsers sent on scratch tabs.
  Brave: variant fill, program ok True, completed 3, elapsed
  92.5ms, CB-1 all three True, V12 found attempt 1, items 2.
  Chromium: variant set_value, program ok True, completed 2,
  elapsed 85.8ms, CB-1 all three True, V12 found attempt 1,
  items 2, pre_count 0, delayed_count chromium 1 (Brave not
  recounted, as designed: only set_value browsers are
  recounted). P9 ok True both. Routing dom-chromium both
  (complete coverage, 1 element, scratch shape). Scratch tabs
  closed by the harness afterwards. The split-variant wiring
  (fill on Brave, set_value on Chromium) is proven end to end
  before any live send.

- Runs start 13:04 +07, back-to-back, one command per run:
  python3 scripts/s2_flip_live.py --run N --chromium-set-value
  --message-prefix S2-REOPEN --workdir
  improvements/s2-flip-reopen-runs
  Each run takes about 40s (scored wall plus 10s delayed-count
  sleep plus P9 captures). All 5 runs are timed to finish
  before the 13:11:56 clone2-watch hold; each run's own
  timestamps are in its JSON, so any hold overlap would be
  visible.

### Run table (from improvements/s2-flip-reopen-runs/run-1..5.json)

| run | time (+07) | wall ms | Brave (fill) | Chromium (set_value) |
|-----|-----------|---------|--------------|----------------------|
| 1 | 13:05:09-13:05:57 | 29020.4 | sent, strict 72 el, program ok True completed 3, dom_act 51ms, elapsed 140.5ms, V12 attempt 1 items 43, CB-1 all True | sent, RELAXED 80 el trunc, program ok True completed 2, dom_act 12ms, elapsed 113.0ms, focus_enter ok, V12 attempt 1 items 54, CB-1 all True, pre 0, delayed 1 |
| 2 | 13:06:02-13:06:46 | 27799.1 | sent, strict 73 el, completed 3, dom_act 46ms, elapsed 137.5ms, V12 attempt 1 items 45, CB-1 all True | sent, RELAXED 80 el trunc, completed 2, dom_act 9ms, elapsed 106.6ms, focus_enter ok, V12 attempt 1 items 56, CB-1 all True, pre 0, delayed 1 |
| 3 | 13:06:50-13:07:34 | 28112.6 | sent, strict 75 el, completed 3, dom_act 46ms, elapsed 144.9ms, V12 attempt 1 items 47, CB-1 all True | sent, RELAXED 80 el trunc, completed 2, dom_act 9ms, elapsed 107.1ms, focus_enter ok, V12 attempt 1 items 58, CB-1 all True, pre 0, delayed 1 |
| 4 | 13:07:39-13:08:24 | 28898.1 | sent, strict 77 el, completed 3, dom_act 43ms, elapsed 140.8ms, V12 attempt 1 items 49, CB-1 all True | sent, RELAXED 80 el trunc, completed 2, dom_act 8ms, elapsed 99.4ms, focus_enter ok, V12 attempt 1 items 60, CB-1 all True, pre 0, delayed 1 |
| 5 | 13:08:27-13:09:12 | 28560.9 | sent, strict 79 el, completed 3, dom_act 43ms, elapsed 141.2ms, V12 attempt 1 items 51, CB-1 all True | sent, RELAXED 80 el trunc, completed 2, dom_act 10ms, elapsed 104.2ms, focus_enter ok, V12 attempt 1 items 62, CB-1 all True, pre 0, delayed 1 |

- Median wall: 28560.9ms (28.6s). Sorted walls: 27799.1,
  28112.6, 28560.9, 28898.1, 29020.4.
- Per-send: 10/10 verified (Brave 5/5, Chromium 5/5). Per-run
  (both sends verified): 5/5. Model calls 0 in all runs.
- Brave half, median: per-browser wall 3699.4ms, program
  elapsed 140.8ms (dom_act 43-51ms), V12 attempt 1 every run,
  routing strict every run (72 to 79 elements, not truncated;
  the Brave thread grows by one user bubble plus clone1's
  reply per run and stays under the 80 cap).
- Chromium half, median: per-browser wall 6243.9ms, program
  elapsed 106.6ms (dom_act 8-12ms), V12 attempt 1 every run,
  routing RELAXED every run (80 elements, truncated, composer
  present in the snapshot; the live thread is past the cap
  since the (b1) runs). Pre-send count 0 and delayed count
  exactly 1 in every run: no double-send. Zero
  Input.dispatchMouseEvent calls in the Chromium path.
- Phase split, median across runs (ms): ssh transport 21942.2,
  broker 761.1, observe 2274.6, act 245.4, verify 375.9, setup
  227.3, residual 2750.1. Transport is about 77 percent of the
  wall. The residual is accounted for, not a hole: the pre-send
  count-check SSH call (874.7-1383.7ms, inside the scored wall)
  appends no span by design, and the mux baseline (about
  1.0-1.2s) underestimates the actual per-call SSH cost
  (1.3-1.8s), so each span undercounts transport by about
  0.1-0.6s. The sends themselves are fully timed (program
  elapsed above, V12 about 1.4s per browser).
- No run overlapped a clone2-watch hold (runs 13:05-13:09;
  holds are :11:56, :26:56). No keystrokes sent anywhere in
  this task. No workspace switch. No Zen tab touched.

## 5. P9 review

- All 10 P9 screenshots (5 runs x 2 browsers) reviewed by
  reading the PNGs before scoring. DOM and render agree in
  every shot; no DOM-vs-render mismatch, so no run fails on
  the B1 condition. Each run message appears exactly once;
  no duplicate send in any shot.
- Run 1 Brave: blue bubble "S2-REOPEN-R1-BRAVE-IGNORE-TEST"
  visible, composer empty. PASS.
- Run 1 Chromium: blue bubble
  "S2-REOPEN-R1-CHROMIUM-IGNORE-TEST" visible at the bottom,
  composer empty; older C5-B1-R3/R4/R5 bubbles above with cap
  banners between. PASS.
- Run 2 Brave: R1 and R2 bubbles visible, composer empty,
  clone1 reply between them. PASS.
- Run 2 Chromium: R1 and R2 bubbles visible, composer empty.
  PASS.
- Run 3 Brave: R1, R2, R3 bubbles visible, composer empty,
  clone1 replies. PASS.
- Run 3 Chromium: R1, R2, R3 bubbles visible, composer empty.
  PASS.
- Run 4 Brave: R1-R4 bubbles visible, composer empty, clone1
  replies. PASS.
- Run 4 Chromium: R1-R4 bubbles visible, composer empty. PASS.
- Run 5 Brave: R1-R5 bubbles visible, composer empty, clone1
  replies including the R5 receipt. PASS.
- Run 5 Chromium: R2-R5 bubbles visible (R1 scrolled off the
  top), composer empty. PASS.
- P9 PASS 10/10. Incidental, recorded not judged: clone1's
  task-4 agent followed the runs live in its thread, replying
  to each test message ("Da nhan ma reopen R1...") and
  recording them in its Today panel; the Brave relaunch did
  not disrupt it. Clone2's thread shows its cap banners
  between the test bubbles, as in the (b1) runs; that is
  clone2's account state, not this task's.

## 6. Verdict: the class NOW completes end to end. Recommend EXPAND.

- (a) Can the class now complete end to end? YES. 5/5 runs
  both sends verified (was 0/5 in the original flip),
  per-send 10/10, V12 attempt 1 in all 10 sends, CB-1 all
  three True in all 10 sends, 0 model calls. The Chromium
  half went from 0/5 (fill, mouse stall) to 5/5 (set_value,
  input-free); the Brave half stayed 5/5 with fill, unchanged.
- (b) Median wall: 28560.9ms (28.6s), down from 33.2s in the
  original flip (which failed half its sends) and up from
  the 18.8s Chromium-only (b1) figure (which covered one
  browser only). The two-browser wall is the honest class
  figure.
- (c) Does the flip EXPAND to more classes or stay limited
  to this class? EXPAND. The plateau gate (coordinator-set,
  flip log section 0) is: median wall above 60s over 5 runs
  equals plateau reached; below 60s the class expands. The
  median is 28.6s, below 60s, AND the class completes (5/5
  runs, not fast failures). The gate's spirit is met as
  well as its letter: the mechanism is no longer the
  bottleneck for this class (program elapsed about 0.11s
  Chromium plus about 0.14s Brave; the wall is transport).
  Per the task, I do NOT expand the flip myself; I report
  the numbers and recommend: the coordinator may expand the
  flip to the next class.
- Caveats, stated plainly:
  1. The Chromium half ran under the DISCLOSED relaxed
     routing gate in all 5 runs (truncated inventory, composer
     covered). The send mechanism is identical to run 1 of
     the (b1) measurement, which passed under the strict gate;
     the relaxation touches only the routing gate, not the
     send path. The 80-element snapshot cap will keep biting
     live threads as they grow; raising the cap is a cdp.mjs
     change plus laptop sync for the coordinator to weigh.
  2. The mouse stall itself is UNSOLVED. Chromium still
     cannot answer Input.dispatchMouseEvent on the occluded
     tab; (b1) routes around it for this class only. Any
     future task class that genuinely needs synthetic mouse
     input on an occluded tab will hit the same wall, and
     that stays the step 9 prototype's natural first target.
  3. Transport dominates the wall (ssh median 21.9s of
     28.6s). Further speed gains for this class must come
     from transport (S0/S1), not from the send mechanism,
     which is already about 0.25s of program time per run.
  4. The durable landing is still open (section 0 open
     item): the (b1) shape lives in /tmp helpers plus
     harness flags. Landing it in cdp.mjs with tests is
     follow-up work for step 8/9.

## 7. Rollback: Brave back to no-flag

- 13:10:36 +07, T+14m: SIGTERM to the debug-port Brave main
  PID 1112207. Graceful exit in 1s; no brave process remains.
  [::1]:9223 closed.
- 13:10:52 +07, T+15m: relaunched WITHOUT the flag (same
  as-found flags, donor env prefix, log
  /tmp/s2-reopen-brave-rollback.log). New main PID 1119832.
- 13:11:00 +07: verified. Brave window back at the same
  address 0x55705383d420, ws1, PID 1119832. [::1]:9223 stays
  closed. Chromium (clone2, PID 8059) never restarted or
  touched; its tab D1374C7C994D3DA72678E20C7FD099A0 still
  serving on 127.0.0.1:9223.
- 13:11:18 +07: full cmdline check: 0 matches for
  remote-debugging-port on PID 1119832. The CDP exposure is
  closed; the machine is back to its as-found state (Brave
  no-flag, Chromium on 127.0.0.1:9223, relay PID 983809
  untouched). The rollback finished before the 13:11:56
  clone2-watch hold; the 13:11:18 verification call was
  read-only (ps plus curl), no keystrokes.

## 8. Commit record

- Harness + test (--chromium-set-value split variant):
  d90d1b9 (scripts/s2_flip_live.py,
  tests/test_s2_flip_wiring.py), wiring tests 12/12 pass,
  push verified with git ls-remote
  (d90d1b917cc9e615158307e90315982bae86e796).
- Re-open run JSONs + P9 PNGs:
  improvements/s2-flip-reopen-runs/run-1..5.json plus
  p9-runN-brave.png and p9-runN-chromium.png (to be committed
  with this log).
- This log: improvements/worker-click5-s2-reopen-log.md
  (commit hash to be recorded here after the commit lands).
- Laptop helpers (not in the repo, reused from the (b1)
  measurement): /tmp/c5-focusenter.mjs, /tmp/c5-count.mjs,
  /tmp/s2-v12.mjs, /tmp/s2-p9.mjs, /tmp/s2-seed.mjs.
  Laptop logs: /tmp/s2-reopen-brave-debug.log,
  /tmp/s2-reopen-brave-rollback.log.
- No keystrokes sent anywhere in this task. No workspace
  switch. No Zen tab touched. Clone1 window untouched except
  the P3-style relaunch and rollback, both verified.
