# Worker CLICK3-D1: council reviewer 1 verdicts on the breakthrough discussion

Owner: the owner. Role: independent council reviewer 1. I did not coordinate
with other reviewers in this round, did not follow the current method, and
questioned everything. Decision criterion (owner standing rule 06:07):
judge every proposal by the accuracy and speed of its FINAL RESULT, never
by rewrite size or cost. Cost (tokens, time, rewrite effort) is IRRELEVANT.
No em dash or en dash anywhere in this file. No personal info. Evidence
with every claim. Never ydotool.

## 0. Log (wall-clock Asia/Ho_Chi_Minh + elapsed from task start)

- 06:08:40 +07 (T+0s): task received. Repo ~/workspace/computer-use-wayland,
  branch todolist-push, HEAD a4ecb49 at start.
- 06:08-06:10 (T+0-2m): read all three review logs in full: ARCH-REVIEW
  (improvements/worker-arch-review-log.md, 074c1d7), GROUNDING-REVIEW
  (improvements/worker-grounding-review-log.md, d1fc4e9), SPEED-REVIEW
  (improvements/worker-speed-review-log.md, a4ecb49). Read the CODEX-BREAKTHROUGH
  launch log (improvements/worker-codex-breakthrough-log.md): launch only,
  Codex PID 781223 started 06:04:15, report not landed.
- 06:09-06:11 (T+1-3m): spot-checked cited code refs (section 1) and ran my
  own SSH probes (section 2). Read the AMEND4 prompt
  (~/workspace/codex-amend4-prompt.md, 11 items + item 12 addendum) to answer
  the AMEND4 sequencing question from source, not from memory.
- 06:09 (during this review): owner rule TWO TRACKS landed in MEMORY.md:
  the team debates the old directions; fix/improve work on the current
  system continues, but SLOWER and more carefully to save tokens, because
  no direction is confirmed best yet, so keep doing the current work.
  This rule is applied in section 5.
- 06:12 (T+4m): fetched origin/todolist-push before writing; branch had
  moved (6d1bf04, reviewer 2 log). I did NOT read that log: independence
  in this round forbids it. I will rebase my commit onto it and push.
- 06:12-06:14 (T+4-6m): wrote this log.

## 1. What I verified independently (file, line, or live probe)

VERIFIED (I checked the source myself on todolist-push HEAD a4ecb49):

- V1. Vision 17/29 = 58.6% first-try hit rate: docs/calibration-e2-report.md
  lines 31 and 53. Pointer error 0.5-0.9 px, 29/29 clicks executed, 0
  refusals: same report, consistent with all three reviews.
- V2. cu.py observe() line 920, observe_screen() line 974, image_point()
  lines 1000-1005, desktop_act() lines 1619-2199 (580 lines), guard()
  line 1691, move() line 1770, hypr() line 520, _input_line_changed()
  lines 1023-1076, OBSERVATION_MAX_AGE = 120 line 58, stale refusal
  line 773, screen-scope refusal for key/type line 1649, scope-matching
  after-capture lines 2083-2091, --dom-selector line 2717, code-exec
  subparser line 2733, CU_CODE_EXEC gate lines 2770 and 2793, browser()
  line 2207. All ARCH/GROUNDING line numbers check out exactly.
- V3. The pixel-band docstring (cu.py lines 1023-1076) states in plain
  text that a True there is "necessary, not sufficient, proof the text
  landed" and "the DOM value check is the sufficient check". ARCH F10
  and GROUNDING W3 quote it accurately.
- V4. first_action.py line 656: envelope after-capture is hardcoded
  cu.observe_screen(env, args.screen, max_width=1920), regardless of
  input scope, overwriting desktop_act's scope-matching after-capture.
  The after-image scope trap (investigator 5f5a2fd) is proven from source.
  attempt_session() lines 183-210 spawns a fresh session subprocess per
  call with a hard deadline, exactly as SPEED 2c describes.
- V5. fastpath.py dom_rect_to_screen_point() lines 152-180 (exact screen
  point from DOM rect, one conversion) and dom_rect_to_image_point()
  lines 195-243 (maps the exact point BACK into image coordinates).
  dom_act.py ground_many_one_shot() lines 240-331 calls
  dom_rect_to_image_point at line 312; focus_type() lines 425-491.
  The image-frame round trip GROUNDING 1.4 describes is real and in the
  code: exact DOM rect -> exact screen point -> lossy image point ->
  back to screen point at click time.
- V6. zen_dom.py harvest() lines 905-976 (one-shot bulk harvest).
  cdp.mjs lines 237-240: the harvest comment states the Brave gap
  plainly (remote-debugging-port needs a custom profile/relaunch vs
  the already-logged-in Brave; runs against agent-managed Chromium,
  not Brave, until resolved). GROUNDING 1.5 quotes it accurately.
- V7. cursor_session.py supervise() line 228: guard + driver subprocesses,
  pipes, gate, UUID token, drain thread. Confirmed by reading lines
  228-260. overlay.py is a Unix-socket server: serve() line 344,
  AF_UNIX socket bind lines 350-353, holder accounting throughout
  (lines 38-165). Confirmed.
- V8. session_remote.py carries test scaffolding in production transport:
  _git_head_at_start() line 100, _envsteal_test_proof() line 110,
  started_git_head recorded line 492. Broker class line 463, serve()
  line 1253, 1601 lines total. ARCH F7 is accurate.
- V9. tests/two_vision_bench.py on origin/main is 868 lines; its
  docstring states VISION 1 is a DOM harvest, NOT a screenshot, scoring
  by OUTCOME (message in thread DOM, V12 sent-bubble gate), transport
  Marionette only, TODO D1 (no BiDi/Marionette handover protocol).
  It is NOT present in the todolist-push working tree (ls confirms
  both the bench and the fixture are absent locally). Any gate that
  runs it must first bring it onto this branch.
- V10. F2b numbers: improvements/worker-f2b-live-session-log.md lines
  33-35: order-to-overlay 12.262s, dispatch 11.620s, fresh observe
  0.233s, Python startup 0.060s, overlay acquire 0.349s; spawn-to-overlay
  honesty number 6m56s line 44. Confirmed as cited.
- V11. AMEND4 is a 12-item fix list (11 items in
  ~/workspace/codex-amend4-prompt.md plus item 12 addendum, the
  after-image scope investigation). Items 1-11 are DOM-grounding
  correctness fixes (geometry, gate traversal, band anchoring/wiring,
  region fallback, stale origin, flag redesign, set_value
  sanitization, supply-chain tests, snapshot event test, design-doc
  fixes). Item 12 is the same after-image fix as A7/P4. Two
  independent implementations run in parallel (Codex amend4-codex,
  VM CLICK3-AMEND4) for later reconciliation. Round-3 council exists
  (commit 422f4b0).
- V12. zen_cli.py contains zero hits for chrome or set_context (grep).
  P8's premise (no chrome-context support in the CLI today) holds.
- V13. first_action.py lines 597-613 already wires DOM hooks and
  type_x_ranges into the act-now path when a selector is given. The
  DOM verification hooks exist and are opt-in, exactly as GROUNDING
  1.3 claims.

TAKEN ON TRUST (cited with source, not re-measured by me):

- T1. Clone2 DOM bench numbers (66 rects, Marionette median 0.030s,
  5 DOM clicks 0.0022-0.0053s, verify 0.002-0.015s, one-session-per
  Firefox constraint): docs/clone2-dom-grounding-20261122.md on
  origin/main. I did not re-run the bench (no .venv, no Firefox
  tooling in this session). The structural claims built on them are
  proven from code (V5, V6); the timings are trusted.
- T2. G30/G31 eyeball errors (64 px, 75 px, 45 px above the real
  field): error file ~/workspace/cf26-upload/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md
  lines 302-310 for G30 (verified the heading exists); G31 from
  ~/workspace/cl2msg-direct-log.md and the parent brief, not yet in
  the error file (GROUNDING notes the same gap).
- T3. The 87.8% think-observe-think share (tc02-t1 gap 722.955s):
  live-test-log.md via SPEED 1c. I accept SPEED's correction that
  it was measured with a LOCAL helper and contains no SSH tax, so it
  does not transfer to the remote VM-agent path.
- T4. Brave accepts --remote-debugging-port at launch on its existing
  profile with login and tabs intact, and a second launch forwards to
  the existing instance with the flag ignored. General Chromium
  behavior, asserted by GROUNDING, not verified by me. P3's own
  verification step (check /json/list, login intact, one fill plus
  assert) must confirm it live; the experiment is designed to fail
  safe to the Chromium fallback.
- T5. AT-SPI numbers (linux-use 48 ms figure) and Zen chrome-context
  blocking without a restart (C12 note): author-reported, not
  re-probed here.

## 2. My own probes (re-derived numbers, 06:09-06:11 +07)

CORRECTION TO SPEED: the 460x multiplexing claim does NOT reproduce.

- Fresh SSH (ssh-laptop.sh true, n=1, timed in Python): 5.29s, rc=0.
  Confirms SPEED's fresh range (4.43/4.93/4.48s) in order of magnitude.
- Multiplexed SSH (ControlMaster, master started from the shell,
  confirmed alive with `ssh -S sock -O check`, rc=0, socket present):
  `true` over the master took 0.94s, 1.18s, 1.29s (n=3, all rc=0).
  A real command over the master (env grep + ls + pgrep) took 0.91s.
  That is about 5x cheaper than fresh, NOT 460x, and NOT 0.01s.
- Warning sign I caught in my own first attempt: when the master had
  NOT come up (my in-process start failed silently), the mux call
  returned in 0.01s with rc=255. A 0.01s reading with an unchecked
  return code is a failed-fast connection, not a fast one. SPEED
  reports 0.01s x3 with no return codes and no master-liveness check
  in its log, so its figure is suspect and must be re-measured with
  rc and master check recorded. My 0.94-1.29s readings are the
  trustworthy ones: master verified alive, rc=0, real work done.
- Consequence for S0: the win is still large and still free, but the
  arithmetic changes. Per act-now (3 connects) the saving is about
  12s, not 13.8s; per observe (2 connects) about 8s, not 9.2s.
  Act-now 16s becomes about 5s (3 x 1.1s mux + 1.7-2.9s laptop work),
  not about 2s. S0 stays ADOPT (section 4), with corrected numbers.
  The 1-day soak test SPEED itself demands is still owed: master
  survival over hours is unproven, and SSH historically dies after
  about 30s of idleness on this path.
- Live state confirmed in the same probe: CU_CODE_EXEC is UNSET on
  the laptop (env grep empty), relay PID 1821 alive
  (session_remote.py serve, socket
  /run/user/1000/agent-computer-use/cursor-guard.sock exists).
  SPEED's "flag OFF in the live path" is confirmed live, not just
  from logs. The master socket was closed cleanly afterwards
  (`-O exit` rc=0, socket gone, no proxy process left).

## 3. Judgments on the three reviews as wholes

- ARCH is right about the direction and overstates the readiness of
  the deletions. The inversion is proven (V1, V3, V5, V10): pixels
  primary, structured bolt-on, and every failure in the record is a
  vision failure, never a coordinate failure. But "rewrite, do not
  patch" as a big-bang sequence is REJECTED (see section 5): the
  rewrite is mostly assembly of parts that already exist (code_exec.py,
  session_driver.py, dom_act.py, zen_dom.py, cdp.mjs, the bench), and
  the cheap wins (S0, S2 switch-on, P3 experiment) land before any
  big-bang commitment is needed. The four deletions (A3, A4, A5, A6)
  are each correct as a destination and wrong as an immediate act:
  each one removes a load-bearing piece (runner lock, pill, fallback
  transport, audit trail) whose replacement is not yet proven. They
  are therefore MODIFY (conditional), not ADOPT.
- GROUNDING is the strongest of the three reviews: every structural
  claim traces to code I verified (V2-V6, V13), its honest limits are
  stated, and its one big bet (P3) is framed as an experiment with a
  fallback, not a claim. Its weakest point is T4 (Brave relaunch
  behavior unverified), which the experiment itself is designed to
  settle. No correction needed except the P5 scoping in section 4.
- SPEED is right about the shape of the latency problem and wrong
  about one number. The fresh-SSH tax, the code-exec flag being off,
  the 87.8% locality correction, and the Step 0/1/2 ordering are all
  sound. The 460x figure is not (section 2). The 1.6x per-task
  estimate for Step 0 should be revised down to roughly 1.3-1.4x on
  a CL2-MSG-class task with the corrected per-connect saving; the
  Step 2 claim stands because it rests on model-call count, not on
  the mux number.

## 4. Per-proposal verdict table (every row covered, none skipped)

Legend: ADOPT means do it as proposed. MODIFY means do it with the
stated change. REJECT means do not do it (none in this table is a
full reject of its direction; the two rejects are of a sequencing
claim and a number, recorded in section 3). Merged rows cite every
source. Overlaps are noted, not hidden.

ARCH:

- A1 Layer 0 persistent driver daemon (snapshot/execute/verify,
  structured-first): ADOPT. The daemon is the destination both ARCH
  and SPEED S3 describe from opposite sides. It wins on final
  accuracy (structured state, exact) and speed (one channel, state
  held, no per-action re-query). Conditions: it holds the
  single-runner lock as a task lock, it owns pill visibility, it
  respects the one-session-per-browser constraint (P7 protocol
  inside it), and it is built AFTER S2 is measured (S3 trigger),
  not as a day-1 big bang.
- A2 Layer 1 pixels demoted to fallback-only, pixel-band labeled
  weak: ADOPT. Proven by V1 and V3. The band stays only as a
  diagnostic for the pixel fallback, never as a pass signal.
- A3 Delete session supervisor tree: MODIFY. Direction right,
  timing conditional. The tree's real jobs (named killable scope,
  cancel/stop, pill label, single-live-runner lock) must be held by
  the Layer 0 driver first. Delete only when the driver
  demonstrably holds the lock plus cancel plus scope on a live run.
  Until then the supervisor is the lock holder, and deleting it
  risks two live runners. The F1 failure cluster (guard plugin,
  stale repo) is real but is fixable without deletion.
- A4 Delete overlay daemon server, keep pill visibility: MODIFY.
  Same conditional logic as A3. The server is real (V7: Unix-socket
  server with holder accounting), and per-batch overlay acquire
  (315-349ms) is a genuine tax, so a session-level pill acquired
  once per task is the right shape. But delete only when a
  driver-owned pill (or compositor-plugin indicator) is proven live
  by raw grim, the same proof F2b used. Never leave the owner blind
  during a run to save 350ms.
- A5 Delete one-shot SSH loop, persistent Broker only: MODIFY.
  Persistent-first, fresh SSH retained as fallback. "Only" is the
  rejected word: a dead relay with no fallback strands the agent
  mid-task, and keeping the fallback costs nothing at runtime.
  The Broker exists and is alive (section 2), so the default can
  move now (S1). Overlaps S1 and S0.
- A6 Delete file-based observation/action IPC: ADOPT for transport.
  JSON over the persistent channel or in-process calls replaces
  scp-per-step. Note: files stay as the audit and evidence trail
  (logs reference observation files); what dies is files as the
  transport, not files as the record. Overlaps SPEED deletion 2.
- A7 + P4 + SPEED deletion 4 (merged, one row, all sources agree):
  act-now after-image scope fix, best shape return BOTH after
  (scope-matching, chainable) and after_screen (full monitor,
  verification only, documented non-chainable); move the scope check
  before the overlay attempt; add a regression test: ADOPT. This is
  the only triple-sourced item in the whole inventory (ARCH A7,
  GROUNDING P4, SPEED 2d, plus AMEND4 item 12), proven from source
  (V4), and it is a focused fix in first_action.py, not a rewrite.
  Do it first among code changes. Also delete the scope-as-capability
  rule in its current form: the executor should not refuse key/type
  based on the observation's scope.
- A8 Delete pixel-band verification for structured targets: ADOPT.
  V3 is decisive: the code itself admits the band is necessary, not
  sufficient, while the DOM value check is sufficient and already
  exists. Keep the band as a diagnostic only (A2).
- A9 Coordinate model to one system (CSS px element rects, converted
  once at the driver edge): ADOPT. The five-frame tower has five
  historical bugs (F2b-1, C12, amend3 step 5, G28, after-scope
  trap); the one-conversion path already exists (V5,
  fastpath.dom_rect_to_screen_point). Applies to the structured
  path; the pixel fallback keeps its own conversion, honestly
  labeled as the fallback. Overlaps P2 (same conversion deleted
  from a different side); P2 is the interface change, A9 is the
  model rule.
- A10 Acceptance test becomes 0-vision live benchmark on real ws2
  clone chats: ADOPT, with P9 attached. The existing 2-vision bench
  already has VISION 1 as a DOM harvest (V9), so "2-vision" misnames
  the machine's perception; 0 machine visions is the honest name.
  Live ws2 clone chats (clone1 Brave plus clone2 Chrome, per AMEND4
  item 11) are the proof the fixture cannot give. Scoring by DOM
  outcome (V12 sent-bubble gate), accuracy at least 90%, total wall
  time end to end including transport. Conditions: the live run
  needs P3 closed first (otherwise it falls back to screenshots and
  proves nothing), needs owner approval per run with the bench's
  --live --confirm-live gates, and keeps VISION 2 as a human look
  (P9), scored by DOM, not by the machine.

GROUNDING P1-P9 (P4 merged into A7 above):

- P1 DOM/a11y default router (Zen Marionette/BiDi, Chromium CDP,
  AT-SPI, screenshot last; encoded in code, not convention): ADOPT.
  The router must log which branch each task took, so drift back to
  screenshots is visible instead of silent. Interim honest state:
  Brave tasks still route to screenshots until P3 lands.
- P2 Element-ref action interface rewrite (live rect re-read at
  execution, screen-point action form, delete dom_rect_to_image_point
  from the live path): ADOPT. Highest-leverage code change after P3.
  The round trip it deletes is proven wasteful from source (V5).
  Overlaps A9; keep both rows because P2 is the interface, A9 is
  the model.
- P3 Brave relaunch with debugging port (controlled experiment,
  quiet window, never mid-batch; fallback agent-managed Chromium):
  ADOPT. Single highest-leverage experiment: it moves the live
  messaging tasks off screenshots entirely. T4 must be verified
  inside the experiment (login intact, /json/list shows the tab,
  one fill plus assert). Do not run it while clone1 is mid-batch.
- P5 DOM verification mandatory: MODIFY (scope it). Mandatory for
  any batch with a DOM session (focus_check and type_check required,
  not optional hooks; CDP fill read-back and assert polling are the
  model). NOT universal: batches on native apps or the pixel
  fallback have no DOM session and keep the band as a diagnostic.
  The hooks exist (V13); this is rewiring, not invention.
- P6 Measure the vision call: ADOPT. Cheap harness logging
  (observation to located target, seconds). Until that number is in
  the logs, every speed claim about the screenshot path is
  incomplete. Bundle with S0.
- P7 Session handover protocol (one protocol per browser per task
  phase, BiDi ground then Marionette input or stay on one): ADOPT.
  Low cost, prevents a known bite (TODO D1, V9). Write it before the
  first live task needs both protocols.
- P8 Zen chrome Marionette context test (set_context chrome): ADOPT
  as a bounded experiment. Premise verified (V12: no chrome support
  in zen_cli.py today). If it works, the last screenshot-only surface
  falls; if blocked, record the boundary explicitly and keep
  screenshots ONLY for chrome UI.
- P9 Keep one screenshot for the human (VISION 2 stays, machine
  scores by DOM): ADOPT. This is the correct division: screenshots
  are a human evidence channel, not a machine perception channel.
  Attached to A10.

SPEED S0-S3 (plus six deletions):

- S0 + SPEED deletion 1 (merged, one row): Step 0 persistent SSH
  multiplexing, delete fresh SSH per call: ADOPT, with corrected
  numbers (section 2). About 5x per connect (5.29s fresh vs
  0.94-1.29s mux in my probe), NOT 460x. Per act-now about 12s
  saved, per observe about 8s; act-now 16s becomes about 5s, not
  about 2s. Do it now: no agent-logic code change, fallback to
  fresh SSH on any multiplex failure. The 1-day soak test is owed
  before calling it done, plus the watchdog SPEED proposes.
- S1 Step 1 act-now over the persistent relay broker: ADOPT. Relay
  verified alive (PID 1821, section 2). JSON over the same channel,
  no scp, after-capture scope-matched or dropped (merged A7/P4 row).
  Expected per-batch mechanism about 0.5s plus the overlay item.
  Overlaps A5 and A6.
- S2 Step 2 DOM-first + code-exec + checkpoint verification
  (CU_CODE_EXEC=1 on): ADOPT. The flag is OFF live (section 2),
  the code is built and merged (code_exec.py 880 lines, gate at
  cu.py:2770/2793), the DOM grounding is measured (T1). This is the
  main 10x lever: one DOM snapshot plus one program plus one DOM
  verify is 2-3 model calls. Honest limit shared with SPEED: the
  10s target depends on unmeasured model inference time; expect
  30-60s if vision reading dominates, still 3-5x better than the
  about 100s best. The 2-vision bench is the gate, and it must be
  brought onto todolist-push first (V9).
- S3 Step 3 laptop-side task runner, only if Step 2 plateaus: ADOPT
  as conditional. This is A1's Layer 0 daemon in task-runner form;
  the two proposals converge on the same destination. Do not build
  before S2 is measured; the trigger is a measured plateau above
  target after S2.
- SPEED deletion 2 (scp for JSON files): ADOPT. Same change as A6
  from the transport side; merged in substance with A6, kept as its
  own row here to show it was judged. JSON goes over the persistent
  channel.
- SPEED deletion 3 (per-batch session spawn): ADOPT in direction,
  MODIFY in sequencing: delete only after S1 is live, since the
  spawn is the current session mechanism. Deleting before the broker
  path is proven strands act-now. Overlaps A3 (narrower: per-batch
  spawn vs the whole supervisor tree).
- SPEED deletion 5 (per-action model call as default): ADOPT. One
  code-exec program per model call is the default; the stepwise
  loop is the fallback for unknown shapes only. This is the S2
  change from the deletion side.
- SPEED deletion 6 (120s freshness window as a gate on DOM work):
  ADOPT for the DOM path (OBSERVATION_MAX_AGE=120, cu.py:58, and
  the refusal at line 773, both verified). Re-read the DOM in 0.030s
  instead of refusing for staleness. Keep the window for the pixel
  path, where staleness is real.

CODEX-BREAKTHROUGH:

- PENDING. Report not landed at review time. The launch log records
  Codex PID 781223 started 06:04:15 on the laptop with its own
  prompt and output log; no report file was in front of me. I invent
  none of its proposals. They are judged in the cross-response round
  when the report lands.

Verdict count: ADOPT 20 rows (A1, A2, A6, A7/P4/2d merged, A8, A9,
A10, P1, P2, P3, P6, P7, P8, P9, S0/del-1 merged, S1, S2, S3, del-2,
del-5, del-6), MODIFY 5 rows (A3, A4, A5, P5, del-3), REJECT 0
proposals in full. The rejects in this review are of a sequencing
claim (big-bang rewrite) and a number (460x), recorded in section 3.

## 5. Order of work (staged rewrite, not big bang)

0. S0 now, plus P6 instrumentation alongside it. No agent-logic
   change, fallback safe, corrected saving about 12s per act-now.
   Soak-test the master for a day before calling it done.
1. P3 Brave relaunch experiment plus P8 Zen chrome test, in a quiet
   window. These are experiments, not builds, and they decide the
   shape of the live path. P3 first: it unlocks every live task.
2. A7/P4 after-image fix (both-fields shape). Focused fix, unanimous
   across all three reviews plus AMEND4 item 12. Do it first among
   code changes; it also unblocks the S2 gate, since the trap cannot
   fire inside the bench but still bites live act-now.
3. S2 switch-on: CU_CODE_EXEC=1 in the live path, drive the live loop
   through code-exec, gate on the 2-vision bench (bring the bench onto
   todolist-push first, fixture run, then live run). This proves the
   shape before the bigger rewrite and measures the model-call count.
4. P1 router plus P2 element-ref interface plus P5 mandatory DOM
   verification plus A9 one-system coordinates. This is the core
   DOM-default build. P7 handover protocol is written inside this
   step, before any live task needs both protocols.
5. S1 broker transport plus A6 file-IPC removal. Transport
   consolidation after the perception core is proven.
6. A1/S3 Layer 0 driver daemon, ONLY on a measured plateau after S2
   (Step 2 measured above target). If S2 hits target, the daemon is
   still the right destination but its urgency drops; if S2 plateaus,
   the daemon is the next lever and its design is already written.
7. A3/A4 deletions last, conditional on the driver demonstrably
   holding the runner lock (A3) and pill visibility proven by raw
   grim (A4). A5's "only" never applies: fresh SSH stays as fallback.
8. A10 0-vision live benchmark on real ws2 clone chats as the final
   acceptance, after P3 and P2. Interim gate remains the 2-vision
   bench (step 3 above).

What this order buys: every step is independently verifiable, every
step lands a measured win before the next step starts, and no step
depends on a bet (P3, P8, S2 measurement) that has not yet paid off.
The big-bang alternative (build the daemon first, delete the old
paths, then measure) risks a long unproven stretch with no fallback;
under the owner's criterion (final accuracy and speed) the staged
order wins because it banks the accuracy win (DOM grounding) and the
speed win (fewer model calls) before the riskiest build.

## 6. Acceptance test: 0-vision live benchmark (ADOPT A10)

The acceptance test becomes a 0-vision live benchmark on the REAL ws2
clone chats (clone1 Brave plus clone2 Chrome), not the 2-vision plan
as written. Reasons: the 2-vision bench's VISION 1 is already a DOM
harvest, so the machine never locates from pixels in that design; the
name is wrong and the fixture run proves nothing about the Brave CDP
gap, which is the live blocker. The 0-vision form is: DOM harvest,
plan, execute, DOM verify, zero screenshots in the loop, accuracy at
least 90%, total wall time measured end to end including transport,
scored by outcome in the thread DOM (V12 sent-bubble gate), with one
screenshot kept as a human look at the end (P9), scored by DOM, not by
the machine. The 2-vision bench stays as the interim gate (fixture
first, then live) because the 0-vision live run needs P3 and P2 built
first; it is a staging fact, not a competing acceptance test. The bench
script must be brought onto todolist-push (it is absent there today,
V9) before either gate runs.

## 7. AMEND4 sequencing: CONTINUE, slower and more carefully

CONTINUE. Do not pause, redirect, or stop. Three reasons, plus the
user's own rule.

- Owner rule TWO TRACKS (06:09, landed during this review): fix and
  improve work on the current system continues, but SLOWER and more
  carefully to save tokens, because no direction is confirmed best
  yet. AMEND4 is exactly that work. The rule answers the question
  directly, and I follow it.
- Nothing in AMEND4 contradicts the rewrite direction. Items 1, 2,
  5, 6, 7, 8, 9, 10 are DOM-grounding correctness fixes that stay
  valid, and become more valuable, under DOM-first: geometry in one
  unit system, gate traversal through frames and shadow roots, stale
  origin refusal, an unforgeable typed flag, sanitized set_value
  read-back. Item 12 IS the breakthrough's after-image fix (A7/P4).
  Item 11 (design-doc fix: benchmark target is clone1 Brave plus
  clone2 Chrome on ws2) is the target definition A10 uses.
- Stopping loses more than it saves: two independent implementations
  (Codex amend4-codex, VM CLICK3-AMEND4) mid-reconciliation, and the
  15 redteam proof tests as the regression net the rewrite itself
  will be judged against. A rewrite with no regression net is a
  blind rewrite.

One redirect inside CONTINUE: items 3-4 (band anchoring and band
wiring) drop in priority. Under A8/P5 the pixel band becomes a
diagnostic, not a success criterion, so perfecting its anchoring is
lower value than the DOM-verification items. Do items 1, 2, 5, 6, 7,
8, 12 first; items 3, 4, 9, 10 after; item 11 is a doc fix and can
land any time. Pace per the TWO TRACKS rule: fewer parallel workers,
smaller batches, per-item verification, no new scope. The AMEND4
round-3 council (422f4b0) already exists; the rewrite track does not
replace it, it runs as the second track.

## 8. Risks and open questions for the cross-response round

- R1. My mux re-measurement (0.94-1.29s) contradicts SPEED's 0.01s.
  SPEED should re-measure with return code and master-liveness
  check recorded, or concede the corrected figure. If the 0.01s
  figure came from a failed-fast connection (as my first attempt
  did), the same error may affect other SPEED timings taken through
  the same path. Ask SPEED to state its exact mux command and rc.
- R2. The per-connection laptop-side cost (about 1s even over the
  master) is unexplained. Is it shell startup, PAM, or systemd user
  session setup per connection? Worth one probe: it bounds every
  transport design, including the Broker.
- R3. P3's Brave relaunch has never been attempted. If Brave refuses
  the port on its default profile AND the agent-managed Chromium
  fallback breaks the clones' logged-in sessions, the live path stays
  on screenshots and A10 cannot run. The fallback needs its own
  login-persistence check before it is relied on.
- R4. The 0-vision live benchmark sends real messages into real clone
  chats. A scratch thread or a quiet-window run is preferable to
  test traffic in a shared channel; the coordinator should confirm
  the exact threads and the owner approval per run.
- R5. CODEX-BREAKTHROUGH is still PENDING. If its report proposes a
  direction that contradicts A1/S3 (for example a different driver
  shape), the order in section 5 must be revisited in the
  adjudication, not defended here.
- R6. I did not read reviewer 2's log (6d1bf04, landed during this
  review) to preserve independence. Any agreement or disagreement
  with it is for the cross-response round.

## 9. Evidence index

- ARCH log: improvements/worker-arch-review-log.md (074c1d7).
- GROUNDING log: improvements/worker-grounding-review-log.md (d1fc4e9).
- SPEED log: improvements/worker-speed-review-log.md (a4ecb49).
- CODEX-BREAKTHROUGH launch log:
  improvements/worker-codex-breakthrough-log.md (launch only).
- Code refs: scripts/cu.py (3063 lines), scripts/first_action.py
  (719), scripts/cdp.mjs (616), scripts/zen_dom.py (1046),
  scripts/dom_act.py (556), scripts/fastpath.py (272),
  scripts/code_exec.py (880), scripts/session_driver.py (180),
  scripts/cursor_session.py (344), scripts/overlay.py (613),
  scripts/session_remote.py (1601). Line numbers in section 1.
- Bench: tests/two_vision_bench.py on origin/main (868 lines).
- Calibration: docs/calibration-e2-report.md lines 31, 53.
- F2b: improvements/worker-f2b-live-session-log.md lines 33-35, 44.
- AMEND4 prompt: ~/workspace/codex-amend4-prompt.md plus
  ~/workspace/codex-amend4-item12.md (12 items total).
- My probes: fresh SSH 5.29s (n=1, rc=0); mux true 0.94/1.18/1.29s
  (n=3, rc=0, master verified alive); CU_CODE_UNSET live; relay
  PID 1821 alive; master closed cleanly, no leftover processes.
