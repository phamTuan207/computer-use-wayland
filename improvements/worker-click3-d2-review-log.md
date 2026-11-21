# Worker CLICK3-D2 review log: council reviewer 2, breakthrough discussion

Owner: Pham Tuan. Review start: 2026-11-22 06:08 Asia/Ho_Chi_Minh.
Repo: ~/workspace/computer-use-wayland, branch todolist-push, HEAD a4ecb49.
Role: independent council reviewer 2. No coordination with other reviewers
in this round. Did not follow the current method. Questioned everything.
Decision criterion (owner standing rule 06:07): judge every proposal by the
accuracy and speed of its FINAL RESULT, never by rewrite size or cost.
Cost (tokens, time, rewrite effort) is IRRELEVANT.
Standing rules honored: no em dash (U+2014) or en dash (U+2013) anywhere,
no personal info, evidence with every claim, wall-clock + elapsed time,
commit with explicit pathspec only, verify push with git ls-remote,
never ydotool. This is a review, not my own work, so no self-healing
question arises.

Note recorded mid-review: owner rule 06:09 TWO TRACKS landed in MEMORY.md
while I worked. The fix/improve-current track continues but SLOWER to save
tokens, since no direction is confirmed best yet, and the team keeps doing
the current work meanwhile. This rule shapes section 6 (AMEND4 sequencing).

## 1. What I verified myself (this session, 06:08-06:11 +07)

### 1a. Code references, spot-checked in the working tree

- cu.py observe() line 920, observe_screen() line 974, image_point() line
  1000, _input_line_changed() line 1023, desktop_act() line 1619,
  guard() line 1691, move() line 1770, OBSERVATION_MAX_AGE = 120 line 58,
  stale refusal line 773, browser() line 2207, --dom-selector line 2717,
  code-exec subparser line 2733, CU_CODE_EXEC gate lines 2770 and 2793.
  All match the line numbers cited by ARCH and GROUNDING.
- _input_line_changed docstring (lines 1023-1076) states plainly that a
  True there is necessary, not sufficient, proof the text landed, and
  "the DOM value check is the sufficient check". GROUNDING's claim that
  the code admits pixel verification is insufficient is VERIFIED verbatim.
- desktop_act head: screen-scope refusal of key/type present, plus the
  scope-matching after-capture at lines 2083-2091 (observe_screen when
  screen_scope else observe on the terminal address, plus settle retry).
  ARCH F9 / GROUNDING 1.6 / SPEED 2d all cite this block correctly.
- desktop_act guard(): calls window() (clients list), hypr monitors, and
  hypr activewindow. ARCH F3 substance VERIFIED. move(): cursorpos read
  twice per move (lines 1773, 1775), plus further cursorpos checks after
  clicks (lines 1817, 1846, 1886-1888). ARCH's "roughly 8-10 socket round
  trips per click" is an estimate, not a count I reproduced, but the
  per-action polling pattern is real.
- first_action.py line 656: envelope after-capture is unconditionally
  cu.observe_screen(env, args.screen, max_width=1920). Line 353: the
  substitute path also uses cu.observe_screen. attempt_session() line 183.
  The after-image scope trap (A7/P4, investigator 5f5a2fd) is VERIFIED
  from source: every act-now after-image is screen-scoped by construction.
- fastpath.py dom_rect_to_screen_point() line 152, dom_rect_to_image_point()
  line 195. dom_act.py GroundPoints line 208, ground_many_one_shot()
  lines 240-331, focus_type() lines 425-491. ground_many_one_shot returns
  IMAGE points: it calls fastpath.dom_rect_to_image_point (line ~312) and
  stores the result as 'point'. GROUNDING section 1.4 (exact DOM rect
  degraded back into the lossy image frame because desktop_act only speaks
  image coordinates) is VERIFIED from source.
- zen_dom.py harvest() line 905. cdp.mjs 616 lines; harvest comment lines
  227-243 states the Brave debugging-port open item verbatim ("Brave holds
  no debugging port on its default profile ... runs against the
  agent-managed Chromium, not Brave, until that is resolved"). GROUNDING
  1.5 VERIFIED verbatim.
- overlay.py 613 lines, Unix-socket server (line 350), add_holder line 111.
  cursor_session.py supervise() line 228: guard + driver subprocesses,
  pipes, token, gate, drain thread. session_remote.py 1601 lines, Broker
  class line 463. session_driver.py 180 lines, JSON-lines driver running
  cu.main() in-process. code_exec.py 880 lines, is_enabled() line 134
  (CU_CODE_EXEC=1/true/yes). ARCH line counts and structural claims
  VERIFIED.
- tests/two_vision_bench.py: 868 lines on origin/main, NOT present in the
  local todolist-push working tree. Docstring VERIFIED via git show: VISION
  1 is a DOM harvest, NOT a screenshot; scoring is by OUTCOME (message in
  the thread DOM), never point-in-box; transport Marionette only; BUILD
  ONLY, no live run yet. ARCH and GROUNDING both describe it correctly.
  The benchmark script already embodies the DOM-first design; that is a
  point in favor of both reviews, and it means "2-vision as planned" and
  "0-vision" differ mainly in venue (fixture vs live), not in machine
  perception (see section 5).

### 1b. Live probe I ran myself (one SSH call, 06:09:25 +07)

- Fresh ssh-laptop.sh call: 5.06s real time. SPEED reported 4.43/4.93/4.48s
  (mean 4.6s). My single sample confirms the magnitude: a fresh SSH
  connection costs about 5s on this path. I did NOT set up a ControlMaster
  myself, so SPEED's 0.01s multiplexed figure and the 460x ratio are
  TRUSTED from the SPEED log, not re-measured (see section 2).
- CU_CODE_EXEC on the laptop: unset. SPEED 2e (flag OFF in the live path)
  VERIFIED by direct probe.
- Relay socket /run/user/1000/agent-computer-use/cursor-guard.sock exists.
  Relay PID 1821 alive, elapsed 14:52:00. SPEED 1b (relay alive, reachable
  only through SSH) VERIFIED in substance.
- No GUI was driven, no browser work, no live task touched.

### 1c. Error-file facts

- G30 in ~/workspace/cf26-upload/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md lines
  302-310: 3 act-now batches ok/completed, message never entered the
  thread; 50px offset hypothesis refuted by a 3-point probe (clicks exact
  0-1px); root cause vision-grounding, Muse clicked (250,1037), 64px above
  the real field (y 1101-1164, center (306,1132)); CL1-MSG2 clicked
  (300,1026), 75px too high; Codex re-grounded, clicked (300,1132), typed,
  Enter sent 01:37. VERIFIED as written.
- G31: grep finds 0 hits in the error file (GROUNDING's "not yet in the
  error file" VERIFIED). The facts are in ~/workspace/cl2msg-direct-log.md
  line 23: eyeball read 45px too high, caught by the visual grounding tool.
  VERIFIED.

### 1d. CODEX-BREAKTHROUGH status

- Only an untracked launch stub exists:
  improvements/worker-codex-breakthrough-log.md (1465 bytes, 23:04).
  Codex PID 781223 launched 06:04 on the laptop, report to /tmp only, no
  repo writes yet. No report has landed. Its proposals are PENDING in my
  table below; I invent none of them.

### 1e. AMEND4 status (for section 6)

- 12-item patch track. Codex on the laptop (branch amend4-codex, base
  f0ddd41) landed its first commit ddf5673 "fix: keep viewport geometry
  units consistent" (item 1 GEOMETRY) at 06:08, per the driver log
  improvements/worker-codex-amend4-driver-log.md. Item 12 (after-image
  scope trap) was added 06:01 with the P4/A7 fix shape. The amend4-codex
  branch is not fetched on this VM, so the commit itself is TRUSTED from
  the driver log, not verified by git here.

## 2. What I took on trust, with its source

- Vision first-try hit rate 17/29 = 58.6%, pointer error 0.5-0.9px,
  29/29 clicks executed, 0 refusals (calibration E2). Source: memory
  files cited by ARCH and GROUNDING (proactivity hidden files
  1795237364036, 1795240963795, memory/people/luna-6.md). Not re-measured
  by me. It is the load-bearing number for A2/P1/P2, and both reviews
  cite the same source consistently.
- DOM bench numbers (clone2 batch 7): one-shot 66 rects Marionette median
  0.030s; 5 clicks from one snapshot 1.49s, all 5 hit; DOM clicks
  0.0022-0.0053s; verify by one DOM read 0.005-0.015s; BiDi/Marionette
  session start 1.5-4.1s fresh, 0.014s warm; one remote session per
  Firefox instance. Source: docs/clone2-dom-grounding-20261122.md on
  origin/main. Not re-run by me (no venv/pytest on this VM session).
  The structural claims built on them are proven from code (section 1a);
  the absolute timings are trusted.
- F2b order-to-overlay 12.262s (dispatch 11.620s, 95%) and the 6m56s
  spawn-to-overlay honesty number. Source: improvements/worker-f2b-live-session-log.md.
  Not re-derived.
- tc02-t1 gap 722.955s (87.8%) vs service 37.721s (4.6%). Source:
  live-test-log.md 10x review. SPEED itself flags the hole honestly
  (measured with a local helper, no SSH hop in it), and I agree with
  SPEED's correction: the 87.8% verdict does not transfer to the remote
  VM-agent path, where transport is a second unmeasured tax.
- ControlMaster 0.01s x3, 460x. Source: SPEED log section 1a. I verified
  only the fresh side (5.06s). The ratio claim depends on the 0.01s side,
  which I did not reproduce. Treat 460x as "order of hundreds", not as a
  precise ratio, until the soak test runs.
- zen-mcp 2-20ms, Selenium 11/11 steps in 0.278s, firefox-mcp click 33ms,
  real-task DOM-first 0.64s (Worker J), upload zip 11ms vs 70-minute
  blocker. Source: todolist and docs/zen-dom-control-comparison.md via
  ARCH/GROUNDING. Not re-measured.
- SPEED's CL2-MSG transport estimate (60-90s of 243s) and per-task 1.6x
  estimate for Step 0: computed estimates from the task shape, not
  measurements. Directionally sound (my 5.06s fresh sample supports the
  per-connection cost), but the task-level totals are estimates.
- "Chrome and Brave accept --remote-debugging-port at launch on the
  existing profile, login persists, tabs restore" (GROUNDING P3 premise):
  standard Chromium behavior, not proven live on this Brave profile.
  The P3 experiment itself is the proof; until it runs, P3's premise is
  an assumption, not a fact.

## 3. Corrections and cautions on the three reviews

- ARCH says desktop_act does "up to five screen captures" per batch
  (pre-batch re-observe plus settle retry, after-capture plus settle
  retry, act-now after). Verified structure: the pre-batch re-observe
  plus one settle retry (lines 1733-1749) and the after-capture plus one
  settle retry (lines 2083-2091) exist; the retries are conditional on
  detected change, not unconditional. "Up to five" is the worst case, not
  the typical case. The tax is real but the headline overstates the
  typical count. Does not change the verdict.
- ARCH F7 says "the observed practice is still one-shot SSH per command"
  while a persistent relay exists. VERIFIED in the sense that my probe
  shows the relay alive and the live loop still uses fresh SSH (SPEED's
  CL2-MSG/F2b accounting). The gap is a usage gap, not a capability gap.
  Agreed.
- GROUNDING says the five-frame tower has "five historical bugs" (F2b-1,
  C12, amend3 step 5, G28, after-image scope trap). I verified F2b-1's
  mechanism class, C12's origin note in fastpath.py, G28's refusal, and
  the after-image trap from source. Amend3 step 5 I did not re-check.
  Four of five verified directly is enough to sustain the claim.
- SPEED says "the flag is OFF in the live path" and calls flipping it
  "the single biggest free win". The flag-off part I VERIFIED (unset on
  the laptop). The "free win" part needs a qualifier: flipping the flag
  changes the live loop for every task at once, so it should be gated on
  the fixture bench pass first (see S2 verdict), not flipped blind.
- All three reviews agree with each other on the core diagnosis
  (screenshots are the wrong primary perception, transport tax is real,
  code-exec + DOM already exist and are not the default). No material
  contradiction between them. The differences are scope and sequencing,
  not direction.

## 4. Verdict table (every proposal, none skipped)

Legend: ADOPT = do it as proposed. REJECT = do not do it. MODIFY = do it
with the stated change. MERGE = same change proposed twice, one row,
verdict once, both sources cited. CODEX rows are PENDING.

### ARCH

| ID | Proposal | Verdict | Evidence and reason |
|----|----------|---------|---------------------|
| A1 | Layer 0 persistent driver daemon (snapshot/execute/verify, structured-first) | ADOPT, staged | Final result is best: one persistent channel, structured calls, no per-action SSH or screenshots. But it is mostly assembly of parts that already exist (code_exec.py, session_driver.py, Broker, dom harvest, cdp.mjs), not invention from scratch. Stage 1: make S2 the live default through the existing parts. Stage 2: consolidate into the daemon. Do not big-bang it while live tasks still fail on screenshots. S3 folds into A1 (see S3 row). |
| A2 | Layer 1 pixels demoted to fallback-only, pixel-band labeled weak | ADOPT | Vision 58.6% first-try vs DOM rects exact at 0.030s; G30/G31 are vision errors, never coordinate errors. Fallback stays for canvas, games, video, Zen chrome UI (P8). |
| A3 | Delete session supervisor tree | MODIFY | Direction is right, timing is wrong. The supervisor's real jobs are a named killable scope, cancel/stop, and the session pill label plus the single-runner lock. The driver task-scope + cancel file + state file replacement is not built or proven. Deleting before the replacement exists risks losing the ability to stop a runaway agent, which the owner sees directly. Delete only after the replacement passes the acceptance test. Until then, keep the supervisor and slim it. |
| A4 | Delete overlay daemon server (keep pill visibility) | MODIFY | Same shape as A3. The pill visibility must stay; the daemon also does holder accounting and leak pruning. The driver-owned pill or compositor-plugin indicator is unbuilt. Better first step, from SPEED: a session-level pill acquired once per task, which also kills the 315-349ms per-batch overlay tax. Delete the server only once the driver-owned pill is proven live. |
| A5 | Delete one-shot SSH loop (persistent Broker only) | ADOPT with fallback | Persistent as the ONLY default transport; keep one-shot SSH as the fallback when the master/broker dies (SPEED's own fail-safe). "Only" without a fallback is brittle on a path where SSH historically dies after about 30s idle. Relay verified alive (PID 1821, socket exists). |
| A6 | Delete file-based observation/action IPC | ADOPT for transport, keep files as record | JSON over the persistent channel / in-process calls replaces scp per step (each scp costs a fresh 5s SSH, verified). But keep the local observation JPEG+JSON files as the audit record: humans and redteams verify runs from them, and the F2b log relied on them. Delete files as the transport, not as the record. |
| A7 | Delete act-now after image as chainable observation | ADOPT, MERGE with P4 | Proven defective by construction (first_action.py:656, verified). The fix shape is P4: return BOTH after (scope-matching, chainable) and after_screen (verification only, non-chainable), or delete the envelope after entirely since the next step re-observes anyway. Same change as P4; one verdict, counted once. Note AMEND4 item 12 is exactly this and is already in flight. |
| A8 | Delete pixel-band verification for structured targets | ADOPT, MERGE with P5 | The code itself admits the band is necessary, not sufficient (cu.py:1023-1076, verified verbatim). DOM value read is the sufficient check and costs 0.002-0.015s. Pixel band stays as a diagnostic only, never as a pass signal. Same change as P5. |
| A9 | Coordinate model to one system (CSS px element rects, converted once at driver edge) | ADOPT | Five-frame tower has five historical bugs; DOM path needs one conversion, already implemented in fastpath.dom_rect_to_screen_point (verified). Scope: structured targets. The pixel fallback keeps its own conversion, isolated in the fallback, not in the main path. |
| A10 | Acceptance test becomes 0-vision live benchmark on real ws2 clone chats | ADOPT as final gate, MODIFY staging | The planned 2-vision bench already uses 0 screenshots for machine location (VISION 1 is a DOM harvest, verified). The real change is venue: fixture to live ws2 clone chats. ADOPT live as the final gate, but stage it: fixture bench first, then live once P3 (Brave CDP) is proven. Do not skip the fixture gate, and do not run live until P3 lands. Live run needs agreed test messages so it does not pollute the clones' working threads. Keep VISION 2 human look (P9). |

### GROUNDING P1-P9

| ID | Proposal | Verdict | Evidence and reason |
|----|----------|---------|---------------------|
| P1 | DOM/a11y default router | ADOPT | Two perception stacks with no routing rule drift to the worse one (works everywhere) instead of the better one (needs setup). Encode the rule in code as one function returning the perception source, not in convention or briefs. Cheap rewiring of existing code. |
| P2 | Element-ref action interface rewrite | ADOPT | The central fix. ground_many_one_shot returns image points (verified), so exact DOM rects are degraded through the lossy image frame before they can be clicked. A screen-point / element-ref action form deletes the five-frame tower for grounded actions and with it the F2b-1, C12, amend3-step-5 bug class. This is the rewrite the owner authorized 06:01. Delete dom_rect_to_image_point from the live path (keep for tests/legacy). |
| P3 | Brave relaunch with debugging port | ADOPT, controlled experiment | Single highest-leverage unblocker: clone chats live in Brave, Brave holds no debugging port, so the CDP path cannot reach them (cdp.mjs comment verified verbatim). Do it in a quiet window, never mid-batch (clone1 is mid-batch-8 now), verify /json/list shows the Muse tab and login intact, run observe + harvest + one fill + assert on a scratch input. Fallback if Brave refuses: agent-managed Chromium with the clones' chats. Either way the outcome is the same: no more screenshots for chat tasks. |
| P4 | After-image scope fix (both after + after_screen) | ADOPT, MERGE with A7 | Same change as A7, one verdict. AMEND4 item 12 already covers it; do not duplicate the work, let AMEND4 land it and verify the regression test. Move the scope check before the overlay attempt; delete the scope-as-capability rule. |
| P5 | DOM verification mandatory | ADOPT, MERGE with A8 | Same change as A8. focus_check and type_check become required for any batch with a type action; CDP fill read-back and assert polling are the model. V12 sent-bubble gate in the bench is the pattern. |
| P6 | Measure the vision call | ADOPT, do early | The dominant cost is unmeasured: capture is 15-30ms, the model read that locates the target is seconds and timed nowhere. The 10x loop cannot optimize what it does not measure. Harness change, cheap, do it with S0. |
| P7 | Session handover protocol | ADOPT, as a design doc | One remote session per Firefox instance is a proven hard constraint; no BiDi/Marionette handover protocol exists (bench TODO D1). Write the sequence down before the first live task needs both. Small; do not let it block other work, it only bites when a task needs both protocols. |
| P8 | Zen chrome Marionette context test | ADOPT, time-boxed probe | Last screenshot-only surface is Zen's own chrome UI (AT-SPI cannot see Zen, C12 probe). Test set_context("chrome"). If blocked without a restart, keep screenshots ONLY for chrome UI and record that boundary explicitly. Time-box it; do not let it become a rabbit hole. |
| P9 | Keep one screenshot, for the human | ADOPT | Screenshots are a human evidence channel, not a machine perception channel. VISION 2 (a look at the two threads at the end) stays because the owner wants to see the result. Machine scores by DOM. |

### SPEED S0-S3 and six deletions

| ID | Proposal | Verdict | Evidence and reason |
|----|----------|---------|---------------------|
| S0 | Step 0 persistent SSH multiplexing (do now) | ADOPT, do now | Fresh SSH verified at 5.06s by my probe; multiplexed 0.01s trusted from SPEED (460x, treat as order-of-hundreds). Config change plus watchdog, fail-safe fallback to fresh SSH. Nearly free, no reason to sit undeployed. Only open item: master survival over hours (historical 30s death); a 1-day soak test is owed before calling it done. |
| S1 | Step 1 act-now over persistent relay broker | ADOPT | Relay verified alive (PID 1821, socket exists). Kills the per-batch session spawn (0.4-2.1s) and the scp round trips. Expected per-batch mechanism about 0.5s. This is the 10x review's deferred item; the deferral reason (transport not the bottleneck locally) no longer holds for the remote path. Un-defer it. |
| S2 | Step 2 DOM-first + code-exec + checkpoint verification (CU_CODE_EXEC=1 on) | ADOPT, gated | The 10x path, already built and merged. Flag verified OFF in the live path (unset on laptop, my probe). One DOM snapshot grounds all coordinates, one code-exec program runs all actions, one DOM read verifies. But gate the live flag flip on the fixture bench pass: flipping changes the live loop for every task at once. Mechanism about 1s + 2-3 model calls; whether it lands near the 10s target depends on unmeasured model inference time (P6 will measure it). |
| S3 | Step 3 laptop-side task runner (only if Step 2 plateaus) | MERGE into A1, decide after S2 measured | Substantially the same destination as A1 (persistent driver daemon): VM sends a plan once, laptop-side runner executes locally, model intervenes only on deviation. One proposal, not two. Do not build it now. Decide after Step 2 is measured; if Step 2 plateaus above target, S3/A1 is the next step. |
| D1 | Delete fresh SSH per call | ADOPT, MERGE with S0/A5 | Same change as S0/A5. |
| D2 | Delete scp for JSON | ADOPT, MERGE with A6 | Same change as A6. |
| D3 | Delete per-batch session spawn | ADOPT, MERGE with S1 | Same change as S1. Session is a lease for the whole task, not per batch. |
| D4 | Delete screen-scope after-capture as produced today | ADOPT, MERGE with A7/P4 | Same change as A7/P4. |
| D5 | Delete per-action model call as default | ADOPT, MERGE with S2 | Same change as S2. Code-exec programs with checkpoint verification become the default; the stepwise loop is the fallback for unknown shapes only. |
| D6 | Delete 120s freshness window as gate on DOM work | ADOPT for DOM path only | DOM rects re-read in 0.030s; a DOM-grounded loop does not need a 120s window or a stale-refusal path (G28). Keep the window for pixel-grounded work, where staleness is real. The window is a patch for vision coordinates, not a law. |

### CODEX-BREAKTHROUGH

| ID | Proposal | Verdict | Evidence and reason |
|----|----------|---------|---------------------|
| CB | All proposals | PENDING | Report not landed. Only a launch stub exists (Codex PID 781223, launched 06:04, report to /tmp). I invent no proposals for it. Fold into the joint adjudication when it lands. If it lands after adjudication, its proposals get their own verdict round against the same criterion. |

### Tally

- ADOPT (including merges and staged adopts): A1, A2, A5, A6, A7/P4, A8/P5,
  A9, A10 (as final gate), P1, P2, P3, P6, P7, P8, P9, S0, S1, S2 (gated),
  D1-D6 (all merged into the above). That is every substantive proposal
  except the two MODIFY deletions and the one MERGE deferral below.
- MODIFY: A3, A4 (delete only after the replacement is built and proven;
  session-level pill first for A4). A10 staging (fixture first, live second).
- MERGE into A1: S3 (decide after S2 measured).
- REJECT: none. No proposal fails the criterion outright. The disagreements
  are about timing and staging, not direction.
- PENDING: CODEX-BREAKTHROUGH (all proposals).

## 5. Order of work

1. S0 + P6 now. Persistent SSH multiplexing plus vision-call measurement.
   Nearly free, no rewrite, fail-safe fallback. Fits even under the
   slower TWO TRACKS pace.
2. AMEND4 item 12 lands (A7/P4) via the in-flight Codex run. Verify the
   regression test. Do not duplicate this work on the breakthrough track.
3. P3 Brave relaunch experiment, in a quiet window between clone batches.
   This is the gate for all live DOM work on the clone chats. If Brave
   refuses the port, fall back to agent-managed Chromium.
4. P1 router + P2 element-ref interface + P5/A8 mandatory DOM verification.
   The rewrite core. This is where the accuracy win comes from.
5. S1 broker act-now, then S2 flag flip, gated on the fixture bench pass.
6. Acceptance, staged: fixture 2-vision bench pass, then live 0-vision
   benchmark on real ws2 clone chats (A10 final gate).
7. A1 daemon consolidation (S3 folded in), then A3/A4 deletions only after
   their replacements are proven live. P7 handover doc before the first
   dual-protocol live task. P8 time-boxed probe any time it fits.

Why this order: S0/P6 are free and unblock measurement; P3 unblocks live
DOM; P1/P2/P5 are the accuracy win; S1/S2 are the speed win; the daemon
(A1) consolidates proven parts instead of betting the run on a big-bang
rewrite; deletions (A3/A4) come last because they remove safety machinery
whose replacements must be proven first. Cost is irrelevant by the
criterion, but sequencing by dependency is not cost, it is correctness:
a daemon built from unproven parts inherits their failure modes.

## 6. Acceptance test: 2-vision as planned vs 0-vision live benchmark

Recommend the 0-vision live benchmark on real ws2 clone chats as the
FINAL gate, staged behind the fixture bench. Reasons:

- The planned 2-vision bench already is 0-vision for the machine: VISION 1
  is a DOM harvest, not a screenshot (verified in the docstring), and
  VISION 2 is a human look at the threads. Calling the acceptance test
  "0-vision" makes the real bar explicit (zero screenshots used by the
  machine to locate or verify) instead of hiding it behind the count 2.
- The fixture is not a live proof. The bench runs in headless Firefox
  against a local fixture; the real tasks fail on Brave on ws2, where the
  DOM path does not reach yet (P3). A fixture pass alone would repeat the
  F1a/F2b pattern: pass on the exercise, unproven on the real task.
- So: fixture 2-vision bench first (it is built, 868 lines, and it is the
  gate for the S2 flag flip), then the same script shape live on ws2 clone
  chats: DOM harvest, plan, execute, DOM verify, zero screenshots in the
  loop, accuracy at least 90%, total wall time measured end to end
  including transport. Keep VISION 2 human look (P9) as evidence, not as
  machine perception. Live run needs agreed test messages so it does not
  pollute the clones' working threads.

## 7. Sequencing with the AMEND4 fix pass (12-item patch track)

Verdict: AMEND4 CONTINUES, but SLOWER, per the owner rule 06:09 TWO
TRACKS. It does not pause, redirect, or stop. Reasons:

- Continue: items 1-11 are small correctness fixes the rewrite also
  needs. Item 1 GEOMETRY already landed (ddf5673, 06:08) and is a
  prerequisite for A9 (one coordinate system). Stopping would discard
  proven-needed fixes and waste the in-flight Codex run.
- Slower: the owner said so at 06:09, because no direction is confirmed
  best yet. The AMEND4 lanes should finish the 12 items at reduced pace
  and take on no new scope.
- Not pause: a full pause loses the Codex run mid-flight and the
  correctness fixes for no gain; the breakthrough track is still in
  review and adjudication, it has not decided anything yet.
- Not redirect: AMEND4's items are not in conflict with the breakthrough
  direction except item 12, which already matches it (P4/A7 fix shape).
  Redirecting the Codex run mid-flight to a rewrite would throw away a
  nearly-finishing fix pass for a design that is still being adjudicated.
- Not stop: same as pause, plus the live loop still runs on the current
  code today, and the current code's bugs (geometry units, after-image
  scope) bite live tasks now.
- Two reconciliations at adjudication: (a) item 12's fix shape must match
  the breakthrough decision (both after + after_screen, or delete the
  envelope after); (b) any AMEND4 item the rewrite subsumes is verified
  against the new code rather than assumed gone. The AMEND4 verification
  lane (fcc re-verification) stays as the checker for the 12 items.

## 8. Open questions for the cross-response round

- A3/A4 timing: if the other reviewers say delete the supervisor and the
  overlay server now, I want their answer to what replaces cancel/stop
  and the pill label in the same step. My MODIFY rests on the replacement
  not existing yet. If a replacement already exists somewhere I did not
  read, I will change to ADOPT.
- A1 staging: if the other reviewers say big-bang daemon first, I want
  their answer to what the live loop runs on while the daemon is being
  built. My staged ADOPT rests on live tasks failing on screenshots today.
- S0 soak: the 1-day soak test for ControlMaster survival is owed. Who
  owns it, and does it block calling S0 done, or does the fresh-SSH
  fallback make the soak advisory only? My view: fallback makes it
  advisory, the soak runs in the background.
- P3 window: who coordinates the quiet window with clone1 batch 8, and
  what is the rollback if the Brave relaunch loses login or tabs? My
  view: coordinator owns the window, rollback is relaunch without the
  flag and restore from Brave's own session restore.
- CODEX-BREAKTHROUGH: when its report lands, do its proposals get a
  full verdict round, or are they folded into the joint adjudication
  directly? My view: full round, same criterion, because a report that
  arrives after adjudication should not be rubber-stamped.

## 9. Log of this review

- 06:08:40 +07 (T+0s): task received. Repo on todolist-push HEAD a4ecb49.
  Read all three review logs in full (ARCH 074c1d7, GROUNDING d1fc4e9,
  SPEED a4ecb49).
- 06:09:25 +07 (T+1m): live SSH probe. Fresh ssh-laptop.sh 5.06s real;
  CU_CODE_EXEC unset; relay socket exists; relay PID 1821 elapsed
  14:52:00. Confirms SPEED 1a magnitude, 1b relay, 2e flag-off.
- 06:09-06:11 +07 (T+1-3m): spot-checked code refs. cu.py lines 58, 773,
  920, 974, 1000, 1023-1076, 1619, 1691, 1770-1775, 2083-2091, 2717,
  2733, 2770, 2793. first_action.py lines 183, 353, 656. fastpath.py
  lines 152, 195. dom_act.py lines 208, 240-331, 425. zen_dom.py line
  905. cdp.mjs lines 227-243, 616 lines total. overlay.py 613 lines,
  cursor_session.py line 228, session_remote.py 1601 lines, Broker 463,
  session_driver.py 180 lines, code_exec.py 880 lines. Bench 868 lines
  on origin/main, absent locally. G30 lines 302-310, G31 0 hits in error
  file, present in cl2msg-direct-log.md line 23.
- 06:10 +07: owner rule 06:09 TWO TRACKS landed in MEMORY.md during this
  review. Incorporated into section 6.
- 06:11-06:14 +07 (T+3-6m): wrote this log. Next: commit with explicit
  pathspec, verify with git ls-remote, report to COORD-CLICK-3.
