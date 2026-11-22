# Worker CLICK3-X2 log: cross-response for the D2 reviewer position

Owner: the owner. Role: cross-response worker holding D2's position in the
breakthrough discussion. The original D2 reviewer completed and cannot
receive follow-ups, so this log answers the other three reviews from D2's
position, using D2's log (improvements/worker-click3-d2-review-log.md,
commit 6d1bf04, 387 lines) as the base. Decision criterion (owner standing
rule 06:07): judge every proposal by the accuracy and speed of its FINAL
RESULT, never by rewrite size or cost. Cost is IRRELEVANT.
Standing rules honored: no em dash (U+2014) or en dash (U+2013) anywhere,
no personal info, evidence with every claim, wall-clock + elapsed time,
commit with an explicit pathspec immediately after staging, never plain
git commit, never git add -A, verify every push with git ls-remote,
never ydotool. This is a review response, not my own work, so no
self-healing question arises.

## 0. Log and what I verified this session

- 06:15:14 +07 (T+0s): task received. Repo ~/workspace/computer-use-wayland,
  branch todolist-push, HEAD f4dcfa3, in sync with origin/todolist-push
  (fetch showed no new todolist-push commits; origin/main moved only).
- 06:15-06:17 (T+0-2m): read all four review logs in full: D1
  (improvements/worker-click3-d1-review-log.md, commit 37f457e, 538 lines),
  D2 (commit 6d1bf04, 387 lines), D3
  (improvements/worker-click3-d3-review-log.md, commit 14fc139, 242 lines),
  RTD (improvements/worker-click3-rtd-review-log.md, commit e96b2ff,
  209 lines).
- 06:15:45 +07 (T+1m): spot checks, all recorded in section 1. No live
  task touched, no GUI driven, no browser work.

## 1. Spot checks this session (new verification, not trust)

- V-X1. Y1b BLOCK is real. Commit 9d9bd63 exists: "Y1b verdict council 3:
  OVERALL Phase A BLOCK on 84b88bb (14/20, 3 real fails, 2 probe
  artifacts)". The verdict file lists the 3 real fails as 1e (f-string
  `chr` NameError, code_exec fails the same way), 2a (codemode wall
  preemption, error raised only after the C loop finished), 2b (code_exec
  wall preemption, elapsed 6.20s, ok=True with NO error, silent success).
  All three touch code_exec/codemode directly, so they bear on the S2
  flag flip. 2e is an allowed exception, 4a/4b are probe artifacts. RTD's
  B2 citation is VERIFIED. D2's original log never mentioned Y1b; neither
  did D1's or D3's (no Y1b reference in either log). The correction
  applies to all three council reviewers equally, not only to SPEED.
- V-X2. Broker wiring gap is real. `grep -c "session_remote|Broker"
  scripts/first_action.py scripts/cu.py` returns 0 and 0. Nothing in
  first_action.py or cu.py references the Broker. RTD's claim that S1 is
  a wiring/build job, not a switch, is VERIFIED. D2's original S1 ADOPT
  rested on the relay being alive (PID 1821, socket exists, verified by
  D2/D1/D3 live probes); liveness is not a client path.
- V-X3. Bench BUILD ONLY is real. `git show origin/main:tests/two_vision_bench.py`
  docstring line 1: "2-vision benchmark script, batch 8 task 1. BUILD ONLY,
  no live run yet." VISION 1 is a DOM harvest, NOT a screenshot. Live mode
  refuses unless BOTH --live and --confirm-live are given plus a plan-URL
  gate. Transport Marionette only, one session per Firefox instance. RTD's
  description is VERIFIED. D2's original log verified the same docstring
  but did not weigh the "never run, even in fixture mode" consequence.
- V-X4. CODEX-BREAKTHROUGH still PENDING. improvements/worker-codex-
  breakthrough-log.md is still 1465 bytes, unchanged since 23:04, launch
  stub only (Codex PID 781223 launched 06:04). No report has landed. I
  invent none of its proposals.
- V-X5. AMEND4 state unchanged since D2. Driver log
  improvements/worker-codex-amend4-driver-log.md still shows item 1
  GEOMETRY landed as ddf5673 at 06:08:51, items 2-12 in flight, no new
  commits visible in this tree. The 06:09 TWO TRACKS rule and the 06:01
  first-principles follow-up (patch vs remove vs redesign per item,
  round-3 council judges) are as D2 recorded them.
- V-X6. Fresh SSH leg, four-way agreement. D2 5.06s, D1 5.29s, D3 4.447s,
  RTD 4.61s. All inside SPEED's 4.43/4.93/4.48s range. The fresh side is
  confirmed four times over. The multiplexed side is now measured twice
  against SPEED's 0.01s (section 2.1).

## 2. The nine disagreements

### 2.1 (1) SPEED 460x: AGREE with D1/D3/RTD, D2's verdict CHANGES on numbers

- D2's original position: fresh side verified by D2's own probe (5.06s),
  multiplexed 0.01s TRUSTED from SPEED, 460x treated as "order of
  hundreds, not a precise ratio, until the soak test runs".
- New evidence, two independent live re-measurements: D1, master verified
  alive with `ssh -O check`, `true` over the master 0.94s, 1.18s, 1.29s
  (n=3, all rc=0), real command 0.91s. D3, 8 samples across two methods,
  0.987s, 1.328s, 1.234s, 0.914s, 1.298s, 1.455s, 1.207s, 1.352s, mean
  about 1.25s. RTD re-measured the fresh leg at 4.61s and incorporated
  the correction. SPEED's log reports 0.01s x3 with no return codes and
  no master-liveness check.
- D2 AGREES the 460x figure does NOT reproduce and WITHDRAWS "order of
  hundreds". The corrected figure is about 3.5-5x per connection (fresh
  about 4.4-5.3s, mux about 0.94-1.46s), saving about 3.2-3.5s per
  connection. Per act-now (3 connects) S0 takes about 16s to about 5-6s,
  not to about 2s. SPEED's 1.6x per-task estimate was computed on the
  0.01s figure and must be recomputed downward before anyone quotes it
  (D1 revises it to roughly 1.3-1.4x on a CL2-MSG-class task; D2 accepts
  that direction, the exact number is for the re-measurement to state).
- D2 ACCEPTS D1's failed-fast trap as the likely explanation for SPEED's
  figure: in D1's own first attempt, when the master had NOT come up,
  the mux call returned in 0.01s with rc=255, a failed-fast connection,
  not a fast one. A 0.01s reading with an unchecked return code is a
  failure, not a speed. D2 notes its own original log already flagged
  the ratio as depending on the unreproduced 0.01s side; the flag is now
  resolved against SPEED.
- Verdict change: S0 stays ADOPT, do now, on CORRECTED numbers. The win
  is still large and still free, but the arithmetic changes, and the
  residual about 1.1-1.25s per call (per-session sshd and shell setup,
  which multiplexing does not remove) is itself an argument for S1 and
  A1, which avoid per-call sshd sessions entirely. D2 also accepts RTD's
  soak handling: the 1-day soak test runs IN PARALLEL, not as a gate,
  because the fallback (fresh SSH) makes it advisory; and RTD's
  per-socket watchdog detail (a half-dead master can hang rather than
  fail cleanly; ControlPersist=600 can leave a stale master holding a
  dead Tailscale route; the watchdog must be per-socket, not global).
  D2 had not considered the per-socket point; it is recorded as an
  implementation requirement for S0.

### 2.2 (2) Ordering: PARTIAL AGREE with D1/D3, AGREE with RTD's gates, D2's order CHANGES

- The orders: D1: S0+P6, P3+P8, A7/P4, S2 switch-on, P1/P2/P5/A9, S1/A6,
  A1/S3 on plateau, A3/A4 last, A10 final. D2: S0+P6, item 12, P3,
  P1/P2/P5, S1/S2, acceptance, A1, A3/A4. D3: S0+P6, P3, S2+P1+P5+P2,
  S1, A1, A10. RTD: S0, AMEND4 parallel, P3, fixture bench run, Y1b
  fixes plus S2 one class, P1/P5 then P2 after AMEND4 items 2-4, S1
  proof, A1/S3 decision, acceptance ladder.
- D2 AGREES with D1 that the S2 switch-on belongs BEFORE P1/P2/P5, and
  moves it earlier. D2's original order (rewrite core first) assumed the
  P2 interface rewrite was the accuracy win; D1 is right that the S2
  flip is a config change on already-built code, that it proves the
  shape before the bigger rewrite, and that it measures the real
  bottleneck (model inference time, P6) before committing to the P2
  rewrite. Under the 06:07 criterion, banking a measured win before the
  riskiest build beats building first and measuring later.
- D2 AGREES with RTD that the S2 flip needs two gates D2 did not have:
  the fixture bench run (the bench has never run at all, V-X3) and the
  Y1b 3 real fails fixed (V-X1). D2's original single gate (fixture
  bench pass) does not cover the Y1b fails, because the bench exercises
  Marionette grounding plus the send chain, not code-exec wall
  preemption or f-string builtins. See 2.4.
- D2 AGREES with RTD's B5 sequencing for P2 (see 2.5): P2 moves AFTER
  AMEND4 items 2-4 land and after the S2 one-class flip.
- D2's REVISED order (section 5): 0. S0+P6 now, soak in parallel. 1. Run
  the fixture 2-vision bench (never run; the baseline). 2. P3 experiment
  in a quiet window. 3. Fix the Y1b 3 real fails. 4. S2 one-class flip
  (clone chat sends) with act-now fallback; plateau defined numerically
  BEFORE this flip. 5. P1 router plus P5 asserts per action type, then
  P2 after AMEND4 items 2-4. 6. S1 broker proof from the VM, session-level
  pill in the same step. 7. A1/S3 merged decision after steps 0-6 are
  measured. 8. A3/A4/A5 deletions last, each gated on its replacement.
  9. Acceptance ladder. This converges with D1 on S2-before-P2, with D3
  on S2-plus-P1/P5 grouped, and with RTD on the gates and the ladder.
  The remaining difference from RTD is only that D2 runs the fixture
  bench (step 1) before the P3 experiment (step 2), because the fixture
  run needs no quiet window and no live coordination, while P3 does.

### 2.3 (3) A10 acceptance: AGREE with RTD's ladder, D2's verdict CHANGES in staging only

- D2's original position: ADOPT 0-vision live as the FINAL gate, MODIFY
  staging: fixture bench first, then live once P3 is proven. D1 and D3
  hold the same staged form. RTD: MODIFY, BLOCKS straight-to-0-vision
  (B1), ladder required: fixture 2-vision, live 2-vision, then 0-vision.
- D2 AGREES with RTD's ladder and adopts the middle rung. Reasons D2
  accepts: (a) the 2-vision benchmark is BUILD ONLY and has never run
  even in fixture mode (V-X3), so jumping to a 0-vision LIVE benchmark
  skips the fixture proof entirely; (b) VISION 2 is the only independent
  check that the DOM outcome matches what a human sees, and removing it
  before DOM is proven on real Messenger pages trades accuracy for about
  0.25s plus one model read, which fails the 06:07 criterion; (c) the
  live run depends on untested P3 and on the open V11 observer TODO.
- Verdict change: A10 stays ADOPT as the FINAL gate, but the staging
  becomes the 3-rung ladder (fixture 2-vision, live 2-vision at accuracy
  at least 90% scored by DOM outcome, then 0-vision keeping one final
  screenshot as unscored human evidence per P9). D2's destination does
  not change; the path gains one rung. D2 keeps D1's conditions: the
  live run needs P3 closed first, needs owner approval per run with the
  bench's --live and --confirm-live gates, and needs agreed test messages
  so it does not pollute the clones' working threads.

### 2.4 (4) S2 blanket flip: AGREE with RTD (B2), D2's verdict CHANGES

- D2's original position: ADOPT, gated on the fixture bench pass. D1 and
  D3 hold the same gated adopt. RTD: MODIFY, BLOCKS the blanket flip
  (B2: Y1b council 3 BLOCKED Phase A on 84b88bb, 3 real fails, unmentioned
  by SPEED).
- D2 AGREES with RTD. V-X1 verifies the BLOCK from source: commit
  9d9bd63, 14/20 PASS, 3 real fails (1e, 2a, 2b), all three in
  code_exec/codemode. The most damning for a live flip is 2b: code_exec
  wall preemption returns ok=True with NO error after 6.20s, a silent
  success past the wall budget. Flipping CU_CODE_EXEC=1 on the live path
  before that is fixed ships a known-broken executor to live tasks.
  D2's original gate (fixture bench pass) does not cover these fails.
- Verdict change: S2 becomes ADOPT gated on TWO conditions: (a) the
  fixture 2-vision bench runs green, and (b) the 3 Y1b real fails are
  fixed. The flip itself narrows to ONE live task class (clone chat
  sends) with act-now as fallback, measured, then expanded. This is
  RTD's B2 sequence, adopted in full. D2 notes the honest limit stands:
  SPEED's own "30-60s, 3-5x not 10x" applies until P6 measures model
  inference time.

### 2.5 (5) P2 immediate rewrite: AGREE with RTD (B5), D2's verdict CHANGES

- D2's original position: ADOPT, "the central fix", "the rewrite the
  owner authorized 06:01". D1 and D3 adopt immediately. RTD: MODIFY,
  BLOCKS immediate execution (B5: collides with AMEND4 items 2-4, stale-ref
  protocol missing).
- D2 AGREES with RTD. Two grounds. First, collision: AMEND4 item 4 is
  already threading type_x_ranges through the exact paths P2 rewrites
  (CLI act path, CodeExecBackend.act, BrowserAdapter.act, per D1 V11 and
  RTD). Running P2 in parallel with AMEND4 items 2-4 guarantees merge
  collisions and wasted work on the same functions. D2's original log
  recorded AMEND4 item 12's overlap with A7/P4 and said "do not duplicate
  the work"; the same rule applies here, and D2 missed it for P2.
  Second, the stale-ref protocol is missing: a live rect re-read can
  disagree with the plan, and the lifecycle (refuse, re-plan, or click
  stale) is unspecified. D2's own P7 note (one session per Firefox) shows
  the session lifecycle is already the fragile part; P2 adds a second
  unspecified lifecycle on top of it.
- Verdict change: P2 becomes ADOPT, SEQUENCED after AMEND4 items 2-4
  land, with the stale-ref/mid-plan-mutation protocol specified first.
  The direction is unchanged; the timing moves. D2 also accepts RTD's
  narrow redirect for AMEND4 item 4: it must not be gold-plated, since
  P2 supersedes its wiring work if P2 lands first.

### 2.6 (6) A3/A4/A5 deletions: AGREE with RTD on B3/B4 in substance, D2's verdicts CHANGE in shape

- D2's original position: A3 MODIFY (delete only after the replacement
  passes the acceptance test), A4 MODIFY (delete only once the
  driver-owned pill is proven live; session-level pill first), A5 ADOPT
  with fallback. D1 and D3 hold the same MODIFY conditional form. RTD:
  REJECTS A4 as stated (B3: pill safety-critical) and B4 delete-first
  ordering for A3/A5.
- A4: D2 AGREES with RTD and strengthens its MODIFY to RTD's two-step
  shape. Step one is the session-level pill, acquire once per task, with
  the overlay server KEPT, which removes the 315-349ms per-batch overlay
  tax without touching visibility. Step two, deleting the server, needs a
  crash proof: a driver-owned pill must prove no stale or missing pill
  when the driver dies mid-task. D2 accepts RTD's reasons: the
  compositor-plugin replacement is in the hardest area of this repo
  (the hyprglass plugin saga shows plugin work is slow and fragile),
  and a driver-owned pill dies with the driver, which is exactly the
  failure mode the daemon's holder accounting exists to prevent. D2
  notes the gap between D2/D1/D3 MODIFY and RTD REJECT is smaller than
  it looks: all four agree deletion is not the first act. RTD's REJECT
  is of the deletion as the stated first act, which D2 also rejects. D2
  adopts RTD's framing for A4 because the end-state wording (delete
  after replacement proven) hid the fact that the first step is a
  different change (session-level pill, server kept).
- A3: D2 keeps MODIFY, and records that all four reviewers now agree in
  substance: delete only when the driver implements scope plus cancel
  latch plus lock with proof (RTD B4). D2's original condition (replacement
  passes the acceptance test) is the same bar in different words. No
  verdict change, wording aligned to RTD's three-part list.
- A5: D2 AGREES with D1/RTD on the wording correction. D2's "ADOPT with
  fallback" becomes MODIFY: persistent-first, fresh SSH kept as the
  documented fallback AND the recovery path (if the broker dies, one-shot
  SSH is how the relay gets restarted). RTD's point that the VM reaches
  the relay only through SSH, so this is not deletion of SSH but deletion
  of one-shot SSH in favor of multiplexed SSH plus broker RPC, is
  accepted. Substance unchanged (D2 already kept the fallback); the
  "only" is rejected, matching D1.

### 2.7 (7) A1: AGREE with RTD (B6) in substance, D2's verdict CHANGES from ADOPT staged to MODIFY

- D2's original position: ADOPT, staged (stage 1 make S2 the live default
  through existing parts, stage 2 consolidate into the daemon; do not
  big-bang while live tasks fail). D1 and D3 adopt staged. RTD: MODIFY,
  BLOCK the full-replacement claim (B6: no existence proof; "mostly
  assembly" conflates five uncomposed parts).
- D2 AGREES with RTD's B6. Evidence checked this session: V-X2 (zero
  Broker references in first_action.py/cu.py, so the S1 client path does
  not exist yet) and V-X3 (the bench is BUILD ONLY, never run). D2's
  original log already said A1 is "mostly assembly of parts that already
  exist, not invention from scratch"; RTD's C2 sharpens that into the
  correct test: session_driver.py runs cu.main() per command, code_exec.py
  is not a daemon, dom_act.py still grounds through image points, cdp.mjs
  drives agent-managed Chromium only, and the benchmark is unrun. "Exists"
  means a file exists, not that the composition works. The composition is
  the work, and it is unproven.
- Verdict change: A1 becomes MODIFY, staged prototype. The deliverable is
  a prototype that must prove snapshot/execute/verify end to end on one
  live ws2 clone chat before anything is deleted. The destination is
  unchanged (a state-holding driver wins on final accuracy and speed IF
  proven), the staging is unchanged (after S2 measured), but the ADOPT
  label for the full-replacement claim is withdrawn. D2 also accepts
  RTD's C5 as an undesigned risk to record: the daemon holding the single
  Firefox session blocks every other tool for the task duration, and
  daemon lifecycle across laptop sleep/reboot is unspecified. The
  prototype must answer both.

### 2.8 (8) AMEND4 triage: AGREE with D1, D3, and RTD, D2's position CHANGES in detail

- D2's original position: CONTINUE, slower, items 1-11 are fixes the
  rewrite also needs, no pause/redirect/stop. D1: items 1, 2, 5, 6, 7, 8,
  12 first; items 3-4 deprioritized; items 9, 10 after; item 11 any time.
  D3: surviving items first; pixel-band work deprioritized; kill an item
  at reconciliation if the rewrite deletes its target. RTD: foundation,
  continue, B2/B5 fed into round-3.
- D2 AGREES with all three and adopts D1's triage, which is sharper than
  D2's flat "items 1-11". Items 3-4 (band anchoring and band wiring) drop
  in priority because A8/P5 demote the pixel band to a diagnostic, not a
  success criterion; perfecting its anchoring is lower value than the
  DOM-verification items. Items 1, 2, 5, 6, 7, 8, 12 go first. D2 accepts
  D3's reconciliation discipline (kill an item if the adopted rewrite
  deletes its target) and RTD's foundation argument (items 1-6 fix the
  geometry and traversal the rewrite builds on; A9's one-system conversion
  needs items 5-6 origin staleness fixed; P2 needs items 2-4 landed first
  per B5).
- D2's verdict stays CONTINUE SLOWER, triage refined. D2 also accepts
  RTD's feed-in: B2 (Y1b 3 fails) and B5 (P2 sequencing) go to the AMEND4
  round-3 council, which judges patch vs rewrite per item under the 06:07
  criterion. D2's "not redirect" stands: no wholesale redirect before
  adjudication, and the 06:01 first-principles follow-up already queues
  patch-vs-remove-vs-redesign per item into the AMEND4 Codex session.

### 2.9 (9) S3: AGREE with RTD/D3, D2's verdict UNCHANGED in substance, STRENGTHENED

- D2's original position: MERGE into A1, decide after S2 measured. D1:
  conditional adopt. D3: fold into A1. RTD: merge with A1, define the
  plateau numerically first.
- D2 AGREES with RTD/D3. The merge stands: a laptop-side runner that
  grounds, acts, and verifies locally and streams back compact state IS
  the A1 driver daemon approached from the other side; building both is
  duplicate work. One design decision, not two builds. D1's conditional
  adopt is the same destination kept as its own row; D2 holds the merge
  because two rows for one build invite two builds.
- Strengthening, adopted from RTD: the plateau criterion must be defined
  numerically BEFORE Step 2 starts (for example, Step 2 live median wall
  time above a stated threshold for a stated number of runs after the
  flag flip), so the trigger is not argued later. D2's original "decide
  after S2 measured" left the trigger empty; RTD's point that an
  undefined plateau either never triggers or triggers on one bad run is
  accepted. D2 adds the definition to its revised order (section 5,
  step 4).

## 3. Other disagreements found (beyond the nine)

### 3.1 A7/P4 delete-vs-both-fields: AGREE with RTD, D2 WITHDRAWS the delete-entirely alternative

- D2's original position: ADOPT the both-fields shape (after plus
  after_screen), OR delete the envelope after entirely since the next
  step re-observes anyway. D1 and D3 adopt both-fields. RTD: ADOPT the
  demote half, MODIFY the delete half (do not delete the after image
  entirely; it loses the human-visible evidence and the frame-change
  signal for a saving of about 0.25s, which is noise).
- D2 AGREES with RTD and WITHDRAWS the delete-entirely alternative. The
  both-fields shape is triple-sourced (ARCH A7, GROUNDING P4, SPEED 2d,
  plus AMEND4 item 12) and proven defective-by-construction from source
  (first_action.py:656, verified by D2/D1/D3). Deleting the after image
  to save about 0.25s while losing the frame-change signal fails the
  06:07 criterion on accuracy. D2 also agrees with RTD's deferral:
  execution belongs to AMEND4 item 12, already in flight on two lanes;
  the rewrite track consumes it and does not duplicate it. D2's original
  log already said "let AMEND4 land it", so the deferral is a
  confirmation, not a change.
- One further refinement, from D3, accepted by D2: the scope-rule deletion
  (cu.py:1648/1649 scope refusal for key/type) is sequenced WITH P2, not
  with A7/P4. While actions are still pixel-addressed, the refusal
  protects typing against a screen observation; once actions are
  element-ref addressed, scope is irrelevant and the refusal can go. D1
  said delete the rule as part of A7/P4; D2 accepts D3's sequencing over
  D1's.

### 3.2 P5 blanket mandate: AGREE with RTD/D1, D2's verdict CHANGES from ADOPT to MODIFY

- D2's original position: ADOPT, focus_check and type_check required for
  any batch with a type action. D1: MODIFY, scoped to batches with a DOM
  session. D3: ADOPT. RTD: MODIFY, BLOCKS the blanket mandate (the assert
  set does not exist for every action type; the production V11
  MutationObserver flag is an open TODO; the rule needs an explicit
  per-action exception list).
- D2 AGREES with RTD/D1. D2's own review verified the hooks exist as
  opt-in (first_action.py lines 597-613 per D1 V13); opt-in hooks are not
  a mandatory assert set. A blanket mandate now means every action
  without an assert either fails (false refusals on currently-working
  flows) or gets a vacuous assert (false confidence). Verdict change: P5
  becomes MODIFY, DOM verification mandatory PER ACTION TYPE as its
  assert lands, with an explicit per-action exception list (scroll
  position, hover state) where DOM assert is impossible and pixel is the
  only signal. The pixel band stays as a diagnostic until then.

### 3.3 A8 follows P5: AGREE with RTD, D2's verdict CHANGES from ADOPT to MODIFY

- D2 adopted A8 outright (delete pixel-band verification for structured
  targets). RTD sequences A8 behind P5: delete band-as-pass-signal only
  when the per-action DOM assert exists and is mandatory; until then keep
  the band as a diagnostic. D2 AGREES. Deleting before the DOM assert set
  exists leaves actions with NO verification, which is worse than weak
  verification. Verdict change: A8 becomes MODIFY, sequenced behind the
  P5 assert set. D1's ADOPT and D3's ADOPT on A8 are noted; D2's change
  is driven by RTD's sequencing argument, which D2 accepts as correct.

### 3.4 D6 120s window: AGREE with RTD's correction, D2's verdict CHANGES slightly

- D2: ADOPT for the DOM path only, keep the window for pixel work. D1:
  same. D3: MODIFY, scoped. RTD: ADOPT for DOM-grounded work, with a
  correction: the refusal at cu.py:773 also guards against future-clock
  observations, and a blanket delete removes the clock-skew guard.
- D2 AGREES. D2 verified OBSERVATION_MAX_AGE=120 at cu.py:58 and the
  refusal at line 773 in its own review, but did not separate the two
  guards. Verdict change: D6 stays ADOPT for DOM paths, with the
  future-clock refusal KEPT and only the age refusal dropped for DOM
  paths.

### 3.5 P7 handover protocol: PARTIAL AGREE with RTD, D2's verdict CHANGES from ADOPT to MODIFY

- D2: ADOPT as a design doc. D1: ADOPT. D3: ADOPT. RTD: MODIFY, possibly
  dissolve (answer first whether Marionette-only suffices; a handover
  costs 4-7s per switch, comparable to the SSH tax being deleted).
- D2 ACCEPTS RTD's question as a precondition. The benchmark already runs
  Marionette-only (harvest plus input), and zen_dom harvest IS Marionette.
  Verdict change: P7 becomes MODIFY, write the protocol only if a task
  genuinely needs BiDi for grounding plus Marionette for input; first
  record the Marionette-only answer. The doc stays small and non-blocking
  either way.

### 3.6 S1 proof-first: AGREE with RTD in part, D2's verdict CHANGES

- D2: ADOPT (relay verified alive). D1: ADOPT. D3: ADOPT, build S1 as the
  first slice of A1. RTD: MODIFY, BLOCKS the delete-first version (no
  Broker refs in first_action.py/cu.py, V-X2; VM path unproven; single-owner
  socket semantics under concurrent VM workers unexamined; overlay 0.35s
  per batch remains the largest item after S1).
- D2 AGREES. Relay liveness is not a client path, and D2's original ADOPT
  did not distinguish the two. Verdict change: S1 becomes ADOPT the
  build, MODIFY the deletion: prove one live batch end to end over the
  broker from the VM first, then delete the per-batch spawn; keep the
  spawn as fallback until proven. D2 accepts RTD's point that the overlay
  0.35s per batch remains the largest item after S1, which supports doing
  the session-level pill (A4 first step) in the same step as the S1 proof.
  D1/D3 also treated S1 as near-ready; the wiring gap applies to all
  three council reviews, not only to D2.

### 3.7 A6, A2, A9, P1, P3, P6, P8, P9: AGREE, no verdict change in substance

- A6 (delete file IPC as transport): D2 ADOPT for transport, keep files
  as record. RTD MODIFY adds only a clarification D2 already held: the
  JPEG still travels for the human VISION 2 check, and file transfer is
  moved onto the persistent channel, not deleted. No change.
- A2 (pixels demoted): D2 ADOPT. RTD's sequencing constraint is accepted
  and recorded: demote only after the router (P1) and its fallback
  trigger are proven; Zen chrome UI stays pixel-primary until P8 proves
  a structured path. D2 already scoped A2 to structured targets with the
  fallback kept, so this is a recorded constraint, not a change.
- A9 (one coordinate system): D2 ADOPT. RTD's two caveats are accepted:
  the one conversion still needs a correct absolute viewport origin and
  scale factors re-read per ground (AMEND4 items 5-6 exist precisely for
  origin staleness), and the pixel system remains for fallback targets
  with the router deciding. D2 already scoped A9 to structured targets
  and recorded item 1 GEOMETRY as a prerequisite. No change.
- P1 (router): D2 ADOPT. RTD's fail-closed requirement (per-target routing
  table proven per target, defined fallback, a log line on every routing
  decision) is accepted as an implementation requirement. No change.
- P3 (Brave relaunch experiment): D2 ADOPT. RTD's experiment-design
  additions are accepted: the rollback and re-login cost must be stated
  BEFORE the window (relaunch without the flag, Brave session restore),
  the CDP port 9223 local-exposure note must be recorded, and the
  shadow-DOM null box_model gap for Messenger's DOM shape is unexamined.
  The experiment itself is unchanged. No verdict change.
- P6 (measure the vision call): D2 ADOPT, do early. RTD's specification
  fix is accepted: timestamp points must be named (observation delivered
  to the agent vs located target returned) and the logging owner is the
  harness, not cu.py, because the model call happens in the calling
  agent's loop outside cu.py. Without that, P6 will be recorded done when
  only capture timing is logged again. No verdict change in direction.
- P8 (Zen chrome context test): D2 ADOPT, time-boxed probe. RTD's
  conditions (quiet window with owner-approved Zen restart, one-session
  constraint in the test design) are accepted. No change.
- P9 (keep one screenshot for the human): D2 ADOPT. RTD's correction is
  accepted: VISION 2 is the agent looking at the threads and reporting to
  the human, not the owner looking directly. Substance stands. No change.

### 3.8 RTD cross-cutting attacks C1 and C4: AGREE, confidence note, no verdict change by themselves

- C1 (agreement is not independent confirmation): D2 AGREES. D2's own
  review already noted the three reviews cite the same sources (E2 17/29,
  clone2 batch 7, F2b) and D2 took the DOM bench numbers and vision rates
  on trust from single measurements. Three reviewers citing the same
  single measurement is one measurement, not three. This lowers D2's
  confidence on absolute timings and is why D2 accepts the live
  re-measurements (D1/D3 mux, V-X1/V-X2/V-X3) over trusted figures.
- C4 (the unmeasured model call dominates everything): D2 AGREES. D2's
  S2/S3 reasoning already flagged model inference time as unmeasured and
  P6 as the fix. Every speed projection stays conditional on that number.
  No verdict change.

### 3.9 SPEED deletions D1-D5: follow their parents, no separate disagreements

- D1 (fresh SSH): ADOPT, follows S0 with corrected numbers. D2 (scp for
  JSON): ADOPT, follows A6. D3 (per-batch session spawn): follows S1,
  now MODIFY proof-first (section 3.6). D4 (screen-scope after-capture):
  follows A7/P4, execution deferred to AMEND4 item 12 (section 3.1).
  D5 (per-action model call): follows S2, now gated on fixture bench plus
  Y1b fixes, one task class first (section 2.4).

## 4. D2's open questions from the original log: status after the other reviews

- A3/A4 replacements: ANSWERED. D1/D3 agree with D2 (MODIFY conditional).
  RTD strengthens A4 to REJECT-as-stated with the session-level pill
  first (section 2.6), which D2 accepts. A3: all four agree on MODIFY
  conditional on the driver holding scope plus cancel latch plus lock
  with proof. No replacement exists yet anywhere D2 read; the
  session-level pill is the first A4 step.
- A1 big-bang, what the live loop runs on: ANSWERED. D1 rejects the
  big-bang (staged rewrite); D3 builds A1 after S2 measured; RTD blocks
  full replacement and demands a staged prototype. All three answer the
  same way: the live loop runs on the current code plus S0 plus the S2
  one-class switch-on while the daemon is built. No big-bang. D2's staged
  ADOPT becomes MODIFY per B6 (section 2.7).
- S0 soak test owner: ANSWERED in part. D1 says the soak is owed before
  calling S0 done, plus the watchdog. D3 says start the soak the same day.
  RTD says run it in parallel, not as a gate, with a per-socket watchdog.
  D2 AGREES with RTD (soak in parallel, fallback makes it advisory) and
  adopts the per-socket watchdog detail. D2's view stands that the
  coordinator owns the soak because it spans workers; the open part is
  only who implements the per-socket watchdog, which is for the S0
  implementer to name.
- P3 quiet window coordinator: ANSWERED. D1/D3/RTD all say the coordinator
  owns the quiet window, never mid-batch. RTD adds the rollback must be
  stated before the window. D2 agrees. Rollback: relaunch without the
  flag, Brave session restore, re-login cost stated up front.
- CODEX-BREAKTHROUGH verdict round: ANSWERED in form, still PENDING in
  fact. D1: judged in the cross-response round when it lands. D3: the
  cross-response and adjudication must leave room to integrate it. RTD:
  judge by the same criterion against the blocking findings, and do not
  treat its arrival as a tie-breaker by default. D2 AGREES with all three
  and adopts RTD's caution (a fourth reading of the same evidence base is
  still the same evidence base, C1). D2's original view (full round, same
  criterion) stands. Status this session: still PENDING, launch stub
  unchanged at 1465 bytes (V-X4).

## 5. D2's updated verdict table (rows that change; unchanged rows confirmed)

Legend: ADOPT means do it as proposed. MODIFY means do it with the stated
change. MERGE means one change proposed twice, one verdict, both sources
cited. PENDING means the input has not landed.

| ID | Old D2 verdict | New D2 verdict | What changed and why |
|----|---------------|---------------|----------------------|
| S0 | ADOPT, do now (460x as order-of-hundreds) | ADOPT, do now, CORRECTED numbers | Mux measured twice at about 0.94-1.46s, about 3.5-5x, per act-now about 16s to about 5-6s. 460x and "order of hundreds" withdrawn. Soak in parallel, not a gate; per-socket watchdog. Section 2.1. |
| S1 | ADOPT | ADOPT the build, MODIFY the deletion | Prove one live batch over the broker from the VM first, then delete the per-batch spawn. Zero Broker refs in first_action.py/cu.py (V-X2). Section 3.6. |
| S2 | ADOPT, gated on fixture bench | ADOPT, gated on fixture bench PLUS Y1b 3 fails fixed, one task class first | B2 verified (V-X1): 1e, 2a, 2b are real code_exec fails, 2b is silent success past the wall budget. Section 2.4. |
| D5 | ADOPT, merge with S2 | Follows S2 (gated, one class first) | Inheritance from S2. Section 3.9. |
| D3 | ADOPT, merge with S1 | Follows S1 (proof-first) | Inheritance from S1. Section 3.9. |
| P2 | ADOPT | ADOPT, sequenced after AMEND4 items 2-4 plus stale-ref protocol | B5: collision on the same functions, protocol missing. Section 2.5. |
| P5 | ADOPT | MODIFY, per action type as asserts land, plus exception list | Blanket mandate would cause false refusals or vacuous asserts; V11 observer is an open TODO. Section 3.2. |
| A8 | ADOPT | MODIFY, sequenced behind the P5 assert set | Deleting before the assert set exists leaves NO verification. Section 3.3. |
| A1 | ADOPT, staged | MODIFY, staged prototype | B6: no existence proof; composition unproven (V-X2, V-X3). Prototype must prove snapshot/execute/verify on one live ws2 clone chat. Section 2.7. |
| S3 | MERGE into A1, decide after S2 measured | MERGE into A1, plateau defined numerically BEFORE S2 starts | RTD: an undefined plateau never triggers or triggers on one bad run. Section 2.9. |
| A4 | MODIFY (delete after driver pill proven) | MODIFY, RTD two-step (session-level pill first, server kept; deletion only with crash proof) | B3: pill is safety-critical, replacements unbuilt. Section 2.6. |
| A5 | ADOPT with fallback | MODIFY, persistent-first, fresh SSH kept as fallback and recovery | "Only" rejected; VM reaches the relay only through SSH. Section 2.6. |
| A3 | MODIFY | MODIFY (unchanged) | All four agree: delete only when the driver holds scope plus cancel latch plus lock with proof. Section 2.6. |
| A7/P4 | ADOPT both-fields, or delete envelope after entirely | ADOPT both-fields only; delete-entirely alternative WITHDRAWN; execution deferred to AMEND4 item 12; scope-rule deletion sequenced with P2 | RTD: deletion loses the frame-change signal for about 0.25s. D3: scope rule goes with P2. Section 3.1. |
| D4 | ADOPT, merge with A7/P4 | Follows A7/P4 (defer to AMEND4 item 12) | Inheritance. Section 3.9. |
| A10 | ADOPT as final gate, staged behind fixture | ADOPT as final gate, staging is the 3-rung ladder (fixture 2-vision, live 2-vision, 0-vision) | B1: bench never run, VISION 2 is the only independent check, P3 untested. Section 2.3. |
| D6 | ADOPT for DOM path only | ADOPT for DOM path only, future-clock refusal KEPT | RTD: cu.py:773 guards future-clock observations too. Section 3.4. |
| P7 | ADOPT as design doc | MODIFY, Marionette-only question first | RTD: write the protocol only if a task genuinely needs two protocols; handover costs 4-7s per switch. Section 3.5. |
| A2 | ADOPT | ADOPT (unchanged) + router-proven constraint recorded | Demote only after P1 and its fallback trigger are proven. Section 3.7. |
| A6 | ADOPT for transport, keep files as record | ADOPT (unchanged) + RTD clarification recorded | File transfer moves onto the channel; JPEG still travels for VISION 2. Section 3.7. |
| A9 | ADOPT | ADOPT (unchanged) + items 5-6 dependency recorded | One conversion needs the absolute origin re-read per ground. Section 3.7. |
| P1 | ADOPT | ADOPT (unchanged) + fail-closed requirement recorded | Per-target routing table, defined fallback, log line per decision. Section 3.7. |
| P3 | ADOPT, controlled experiment | ADOPT (unchanged) + experiment-design additions recorded | Rollback and re-login cost stated before the window; CDP exposure noted. Section 3.7. |
| P6 | ADOPT, do early | ADOPT (unchanged) + specification fix recorded | Timestamp points named; harness owns the logging. Section 3.7. |
| P8 | ADOPT, time-boxed probe | ADOPT (unchanged) | RTD conditions accepted. Section 3.7. |
| P9 | ADOPT | ADOPT (unchanged) | VISION 2 is the agent's final sanity check reported to the human. Section 3.7. |
| CB | PENDING | PENDING (unchanged) | Launch stub only, 1465 bytes (V-X4). Full round, same criterion, when it lands; not a tie-breaker by default. Section 4. |

Tally of changes: 17 rows touched (S0, S1, S2, D5, D3, D4, P2, P5, A8,
A1, S3, A4, A5, A7/P4, A10, D6, P7); the substantive verdict changes are
12 of those (S0 numbers, S2 gating, P2 sequencing, P5, A8, A1, A4 shape,
A5 wording, A7/P4 withdrawal, A10 ladder, D6 guard split, P7
precondition), the rest are inheritances (D3, D4, D5) or strengthened
wording (S1, S3).
Unchanged in substance: A2, A3, A6, A9, P1, P3, P6, P8, P9, D1, D2, CB.
No proposal flips from ADOPT to REJECT or the reverse. The pattern of
the changes is uniform: every change ADDS a gate, a sequence, or a proof
requirement to a direction D2 already adopted. RTD did not reverse D2's
direction anywhere; it proved D2's gates were incomplete.

## 6. D2's revised order of work

0. S0 now plus P6 (with RTD's timestamp/owner specification), soak test
   running in parallel, per-socket watchdog. No agent-logic change,
   fallback safe, corrected saving about 3.2-3.5s per connection.
1. Run the 2-vision benchmark in fixture mode. It has never run at all;
   the whole program's gate cannot be an unrun script. This is the
   baseline everything else is measured against.
2. P3 Brave relaunch experiment, in a quiet window owned by the
   coordinator, never mid-batch, rollback and re-login cost stated
   before the window. This unlocks the live CDP path.
3. Fix the 3 Y1b real fails on code-exec (1e, 2a, 2b).
4. Define the S3/A1 plateau numerically BEFORE the S2 flip, then S2 flag
   flip for ONE live task class (clone chat sends) with act-now as
   fallback. Measure.
5. P1 router plus P5 asserts per action type, then P2 interface rewrite
   after AMEND4 items 2-4 land, with the stale-ref protocol specified
   first. P7's Marionette-only question answered before any handover
   protocol is written. P8 time-boxed probe any time it fits.
6. S1 broker path proof from the VM on one live batch, session-level pill
   (keep the overlay server) in the same step, then delete the per-batch
   spawn.
7. A1/S3 merged daemon/runner design decision, only after steps 0-6 are
   measured. A3/A4/A5 deletions last, each gated on its replacement
   proving (A4 needs the crash proof).
8. Acceptance ladder: fixture 2-vision, live 2-vision at accuracy at
   least 90% scored by DOM outcome, then 0-vision keeping one final
   screenshot as unscored human evidence (P9).
9. AMEND4 continues in parallel at the slower TWO TRACKS pace with D1's
   triage (items 1, 2, 5, 6, 7, 8, 12 first; items 3-4 deprioritized;
   items 9, 10 after; item 11 any time), D3's reconciliation discipline
   (kill an item if the rewrite deletes its target), and RTD's B2/B5
   fed into the round-3 council. Item 12 (A7/P4) is consumed from AMEND4,
   not duplicated.

## 7. Log of this cross-response

- 06:15:14 +07 (T+0s): task received. Repo on todolist-push HEAD f4dcfa3,
  in sync with origin/todolist-push. Read D1 (37f457e), D2 (6d1bf04), D3
  (14fc139), RTD (e96b2ff) in full.
- 06:15:45 +07 (T+1m): spot checks V-X1 to V-X6. Y1b BLOCK commit 9d9bd63
  verified with the 3 real fails (1e, 2a, 2b) from the verdict file.
  Broker grep 0 hits in first_action.py and cu.py. Bench docstring
  "BUILD ONLY, no live run yet" verified on origin/main. CODEX-BREAKTHROUGH
  still 1465 bytes, launch stub only. AMEND4 driver log unchanged (item 1
  ddf5673 landed, items 2-12 in flight).
- 06:17-06:18 +07 (T+2-3m): wrote this log. Next: commit with explicit
  pathspec, verify with git ls-remote, report to COORD-CLICK-3.
