# Worker CLICK3-FARCH: ARCH position response to the joint adjudication DRAFT

Owner: the owner. Role: final discussion participant holding the ARCH-REVIEW
position from its log (improvements/worker-arch-review-log.md, commit
074c1d7). The original ARCH-REVIEW worker completed and cannot receive
follow-ups, so I answer the draft and the other reports from ARCH's
position, with ARCH's verdicts as my starting point. Decision criterion
(owner standing rule 06:07): the final result must be the MOST ACCURATE
and the FASTEST; cost is IRRELEVANT. Evidence standard (owner 06:34,
Lauren Tan standard): every claim carries real measured numbers; where
evidence is missing I say so plainly.
Rules honored: no em dash (U+2014) or en dash (U+2013) anywhere in this
file. No personal info. Evidence with every claim. Wall-clock
Asia/Ho_Chi_Minh + elapsed time. Commit with an explicit pathspec
immediately after staging, never plain git commit, never git add -A.
Verify every push with git ls-remote. Never ydotool. This is a review
response, not my own work, so no self-healing question arises.

## 0. Log and what I verified myself

- 06:37 +07 (T+0s): task received. Repo ~/workspace/computer-use-wayland,
  branch todolist-push, HEAD 2864be4 at start (fetched first).
- 06:37-06:41 (T+0-4m): read in full: ARCH-REVIEW (074c1d7),
  GROUNDING-REVIEW (d1fc4e9), SPEED-REVIEW (a4ecb49),
  CODEX-BREAKTHROUGH (2596287, 138 lines), the joint adjudication DRAFT
  (9d23834), D1 (37f457e), D2 (6d1bf04), D3 (14fc139), RTD (e96b2ff),
  X1 (0cf601c), X2 (d5b205d), X3 (2b0c73c), XRT (6cb3f95).
- 06:41-06:43 (T+4-6m): spot checks in section 0.1. Branch state and
  probe results in section 0.2.
- 06:43-06:55 (T+6-18m): wrote this log.

### 0.1 Spot checks run by me in this session (new verification, not trust)

- V-F1. CODEX-BREAKTHROUGH has LANDED since the draft: commit 2596287,
  report improvements/codex-breakthrough-report.md, 138 lines, in
  Vietnamese. The draft's section 1.4 PENDING row is now decidable, and
  section 2 of this log judges it in full. No proposal is invented.
- V-F2. Scope refusal verified in the repo checkout at cu.py:1665-1666
  (screen observations refuse key/type). Reviewers cited 1648/1649; the
  line moved with AMEND4 edits, substance identical. This matters for
  section 2.3, where I dissent from the draft's deletion timing.
- V-F3. Y1b fails still open, confirmed from code, not just from the
  verdict file: no setitimer, SIGALRM, or child-process preemption
  mechanism in scripts/codemode.py or scripts/code_exec.py, and "chr"
  appears in NEITHER SAFE_BUILTINS list (code_exec.py:107,
  codemode.py:37). PROBE-S2 records the same finding independently.
  B2's fix limb is not met.
- V-F4. AMEND4 landed state at HEAD 2864be4: item 1 (cc964b2, plus
  ddf5673 on amend4-codex), item 2 (c1ea773), item 3 (62b740e), item 4
  (72120aa), items 5-6 (b44a5ea), item 7 (49081aa), item 8 (af0fa87).
  Items 1-8 are landed. Item 12 is in flight on two lanes. Consequence
  for B5: the AMEND4-items-2-4 limb is SATISFIED, so the stale-ref
  protocol is now the single outstanding gate for P2.
- V-F5. Bench is now ON todolist-push: tests/two_vision_bench.py
  (c5311ce, 868 lines, blob 80b00469, unedited from origin/main) and
  tests/two_vision_fixture.html (7f3a70b, 48 lines). The draft's V-A3
  (bench absent) is overtaken. The bench still has never run anywhere.
- V-F6. CB's code line numbers refer to the INSTALLED laptop copy and
  to a checkout at HEAD 4500a18 (behind 622 commits at CB's read time),
  so its cu.py/first_action.py line cites are NOT verifiable against
  this checkout. Its substance is corroborated where reviewers read the
  same code on this branch (first_action.py:656 after-image capture,
  cu.py:1665-1666 scope refusal). I judge CB on substance, not on its
  line numbers.
- V-F7. ssh-laptop.sh contains no ControlMaster flags (grep, this
  session). S0 is not implemented. PROBE-S0 has no log yet.

### 0.2 Probe state at writing (what is decided, what is not)

- PROBE-P8: LANDED, BLOCKED (3790901, log 2864be4). Marionette chrome
  context refused live: HTTP 500, "unsupported operation", "System
  access is required. Start Zen with the
  MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 environment variable set to enable
  it." Session acquire 0.01s, content eval works (title 'Welcome!',
  mozInnerScreenX=240, mozInnerScreenY=8, matching C12 exactly, third
  confirmation of that geometry). No restart performed. Consequence is
  settled: screenshots stay ONLY for Zen chrome UI, boundary recorded.
  P8 is CLOSED as a probe.
- PROBE-P3: NOT-RUN (7b1006a). Clone1 batch 9 open since 06:01, zero
  completion signal, Brave PID 7356 untouched. P3 feasibility is
  UNDECIDED: no measured evidence for or against.
- PROBE-S2: IN PROGRESS (untracked log improvements/worker-probe-s2-log.md).
  Bench files brought onto the branch (V-F5). Runtime missing on this VM
  (no .venv, no selenium, no Firefox/Chromium binary, bench hardcodes
  FF/GD paths under ~/workspace/tools/). Y1b 3 fails still open (V-F3).
- PROBE-S0, PROBE-S1, PROBE-DOMZEN: no logs, no results yet.

## 1. The draft's verdicts on A1-A10: where ARCH agrees, and where the draft is too gated or too loose

ARCH's original verdict was: architecture inverted, rewrite not patch;
Layer 0 persistent driver daemon; Layer 1 pixels demoted to fallback;
7 deletions; coordinate model to one system; acceptance test becomes
0-vision live benchmark on real ws2 clone chats. The draft adopts the
direction on every row and gates the deletions and the daemon on proof.
ARCH accepts that shape. The disagreements below are about placement,
one deletion timing, and scheduling, not about direction.

- A1 (Layer 0 daemon, draft MODIFY): AGREE with the gate, DISAGREE with
  the placement. The draft puts the daemon at step 9, after S2 measured
  and the plateau defined, with no design work before then. That is too
  gated on timing and too loose on scheduling at once: too gated, because
  P2 (element-ref interface), S1 (broker client), and P5 (assert set) are
  all slices of the daemon's contract, and building them first without
  the contract means building them twice; too loose, because a step 9
  with no date attached is a patch track with a new name. ARCH's
  amendment (section 4, step 2): the daemon CONTRACT is written early,
  in parallel with AMEND4, while the prototype PROOF stays late at step
  8 under B6. The contract specifies snapshot/execute/verify, the CB-1
  three-part result, snapshot-bound refs, per-step preconditions, the
  serialized queue, the task lock, pill ownership, crash/stale/sleep
  lifecycle, and the allowlisted API. Writing a contract is not building
  a daemon; it costs a design document and it stops P2/S1/P5 from
  inventing three ad-hoc interfaces. B6's lift condition (prototype
  proves snapshot/execute/verify end to end on one live ws2 clone chat)
  is accepted unchanged.
- A2 (pixels demoted, draft ADOPT with sequencing constraint): AGREE.
  The constraint (demote only after the router P1 and its fallback
  trigger are proven; Zen chrome UI stays pixel-primary until P8 proves
  a structured path) is right, and PROBE-P8 now settles the second half
  as a measured boundary rather than a hypothesis: chrome context is
  BLOCKED without a restart (HTTP 500, section 0.2), so Zen chrome UI
  stays pixel-primary and the boundary is recorded, not revisited. ARCH
  adds two CB measurements that strengthen A2: image inputs are not
  even self-consistent (observe caps width at 960px, act-now captures
  at max_width 1920, JPEG q90 throughout, CB 2.3), and the pixel-band
  preflight has a codec false-refusal mode (J37 patch diff 6.627 around
  the cursor, CB 2.3). The pixel path fails on its own terms, not only
  against DOM.
- A3 (delete supervisor tree, draft MODIFY): AGREE. ARCH concedes the
  draft's correction: the F1 failure cluster (JSONDecodeError, guard
  plugin, loader failure, stale repo) is partly environment faults, not
  supervisor-design faults, so deleting the tree does not delete those
  modes. ARCH's original F5 overstated that. The gate stands: delete
  only when the driver demonstrably holds scope plus cancel latch plus
  lock on a live run. ARCH adds that the replacement (driver task scope
  plus cancel file) is small and should be proven as part of the
  prototype proof, not as a separate late step.
- A4 (delete overlay server, draft MODIFY): AGREE. ARCH concedes the
  delete-first form was wrong: the pill is the owner's only visibility
  into live runs and both replacements were unbuilt. The draft's
  sequence is accepted in full: (a) session-level pill first, acquire
  once per task, server KEPT, measured (this removes the 315-349ms
  per-batch overlay tax without touching visibility); (b) driver-owned
  pill only with proof it shows and clears, including no stale or
  missing pill when the driver dies mid-task; (c) delete the server
  only then.
- A5 (delete one-shot SSH, draft MODIFY): AGREE. ARCH concedes the word
  "only" is rejected: the VM reaches the relay only through SSH, so this
  is deletion of one-shot SSH in favor of multiplexed SSH plus broker
  RPC, with fresh SSH kept as the documented fallback AND the recovery
  path (if the broker dies, one-shot SSH is how the relay gets
  restarted). Substance unchanged: one-shot SSH dies as the DEFAULT
  transport.
- A6 (delete file IPC, draft ADOPT for transport): AGREE. The scope
  condition is accepted: files stay as the audit and evidence trail
  (persisted observation artifacts written by the driver), the JPEG
  still travels for the human VISION 2 check until the persistent
  channel carries bytes, and file IPC stays as the fallback transport
  when no Broker is reachable. What dies is files as the transport.
- A7 (after-image scope fix, draft ADOPT both-fields, delete-entirely
  REJECTED): AGREE on the fix, DISSENT on one timing point. ARCH
  concedes the delete half: deleting the envelope after-image entirely
  loses the human-visible evidence and the frame-change signal for a
  saving of about 0.25s, which is noise against accuracy under 06:07.
  The both-fields shape (after scope-matching and chainable,
  after_screen verification only and documented non-chainable, plus a
  regression test, via AMEND4 item 12) is adopted. The dissent is the
  scope-as-capability refusal deletion, which the draft sequences WITH
  P2 (D3's timing, draft section 1 A7 row). ARCH says that deletion is
  WRONG, not just mistimed, for a reason the draft did not have: CB 2.2
  proves a second scope failure mode ARCH missed. When the observation
  is missing, stale, or errored, _fresh_observation substitutes a
  screen capture and hands the original action list to the executor
  without reframing coordinates; J40 records exactly that outcome (a
  window-frame point used on a screen frame, missing the button by
  about (+45,+12)px, while the call still returned ok). Deleting the
  refusal once actions are element-ref addressed does not fix that
  mode, because the failure is a silent scope substitution, not a
  pixel-addressing problem. ARCH's corrected rule: refs are bound to
  (snapshot id, scope); a scope change HALTS the batch, it never
  silently reframes and never silently substitutes. The refusal changes
  form (scope-mismatch becomes snapshot-mismatch), it is not deleted.
  This is ARCH's sharpest dissent from the draft, and it is decided in
  section 2.3.
- A8 (delete pixel-band verification, draft MODIFY sequenced behind P5):
  AGREE. Deleting band-as-pass-signal before the per-action DOM assert
  exists leaves actions with NO verification, which is worse than weak
  verification. The band stays as a diagnostic until the assert set is
  mandatory per action type.
- A9 (one coordinate system, draft ADOPT): AGREE. The dependency the
  draft records (AMEND4 items 5-6 landing, origin staleness) is now
  SATISFIED: items 5-6 landed as b44a5ea (refuse without window_bounds,
  live Hyprland re-read at ground time, refuse on mismatch), and item 1
  landed as cc964b2. The pixel fallback keeps its own frame internally;
  the router decides.
- A10 (0-vision live benchmark, draft ADOPT as staged, B1 LIFTED):
  AGREE with the draft against the X1/X2/X3 ladder. The draft's
  reasoning is correct on the machine side: in the bench design VISION
  1 is a DOM harvest, not a screenshot, and VISION 2 is a human look at
  the threads, so live 2-vision and live 0-vision-with-P9-screenshot are
  the same machine behavior and differ only in whether the human looks
  at live threads or at a screenshot. The extra live run on real clone
  chats (quiet window, owner approval, agreed test messages, disruption
  to in-flight work) buys replication and localization, not a distinct
  proof, and under 06:07 a gate must protect accuracy or speed
  measurably. The draft keeps live 2-vision as a diagnostic if the live
  0-vision run fails; ARCH accepts that. ARCH adds two amendments to
  A10 from CB (section 5): define 90 percent as end-to-end TASK
  SUCCESS on a held-out set with the sample size stated, and require the
  source/artifact/log manifest before the benchmark gates anything.

## 2. ARCH vs CODEX-BREAKTHROUGH's semantic transaction executor (CB-EXEC)

CB-EXEC (2596287) proposes a local semantic transaction executor: the
agent sends a target (role and name, or selector/ref from a fresh
snapshot) with scope, preconditions, real mouse/keyboard or confirmed
DOM input, and a postcondition; the executor resolves the target on the
laptop through DOM/BiDi, AT-SPI, or screenshot-crop backends under one
contract, with retry only when it knows input was not sent. Its named
pieces: CB-1 three-part result contract, CB-6 long-lived session driver,
one local broker owning session/overlay/browser.

### 2.1 Same direction (no conflict)

Both ARCH and CB-EXEC say the agent must stop sending raw x/y as the
primary action form, the local executor must own target resolution and
verification, screenshots demote to fallback, and one local component
must own the session, the overlay, and the browser. The evidence base
is the same and the direction is the same: vision 17/29 first-try
58.6% with pointer error 0.5-0.9px (E2), G30 64px and 75px misses,
G31 45px eyeball error, DOM 66 rects median 0.030s with 5/5 clicks
landing and verify 0.002-0.015s (clone2 batch 7, single-source, C1
applies). CB independently re-derives the same verdict from the same
record and adds its own measurement: the Wilson 95% interval for 17/29
is 40.7%-74.5%, so the 58.6% point estimate is a small sample, not a
tight bound (CB 2.3). That widens the uncertainty, it does not change
the direction.

### 2.2 Overlapping (merge, do not build twice)

- CB-EXEC IS the design of ARCH Layer 0's execute path. ARCH Layer 0
  specified snapshot/execute/verify as three calls; CB-EXEC specifies
  what execute must do (resolve by backend, check preconditions, act,
  check postcondition, return a three-part result). They are one
  component, not two proposals. The draft's A1/S3 merge (one design
  decision, not two builds) extends to CB-EXEC: one daemon, one
  executor, one contract.
- CB-6 (long-lived session driver) IS ARCH A1 plus SPEED S1: route
  act-now through the session driver instead of spawning a session per
  batch, one owner of pointer, overlay, and the Firefox session, with a
  serialized queue. ARCH accepts the queue requirement, which ARCH's
  original Layer 0 lacked and which answers the draft's open S1
  question (single-owner socket semantics under concurrent VM workers:
  serialize or refuse, never interleave).
- CB-1 (three-part result contract: input sent, correct target received
  input, post-state verified) IS ARCH's execute/verify split made
  precise. ARCH adopts it as the Layer 0 contract: desktop_act's ok
  becomes input_sent, and verified=true only when a postcondition
  holds. CB-1 subsumes P5/A8: for structured targets the DOM assert IS
  the postcondition. Evidence for the need: CB 2.1, cu.py admits the
  desktop check knows only cursor position, not which element received
  the event, and the installed act-now wrapper maps cu.py ok (or enough
  actions completed) to envelope ok=true, so a click on empty space at
  the right pixel can report success; G30 is exactly that case (3
  batches ok/completed, message never entered the thread).
- CB's per-phase measurement demand (CB 2.7, 2.10) merges with P6: P6
  must measure think time as well as the vision call, and the
  acceptance test must split wall time into model, SSH, broker,
  observe, act, and verify phases.

### 2.3 Competing or different (resolved, with ARCH conceding where CB is right)

- (a) Actuation: CB keeps REAL mouse/keyboard input as the default
  execution primitive (semantic locate plus real input when trusted
  events are needed), and notes DOM clicks are not equivalent to real
  input (BiDi pointer click failed, Marionette has viewport limits,
  DOM fill may not equal real typing, CB 2.5; the Browse-button hover
  case in the record proves some controls need real hover). ARCH's
  original text leaned toward DOM/.click() execution (citing DOM clicks
  at 0.0022-0.0053s). ARCH CONCEDES this point: the daemon locates via
  DOM rects (exact, 0.030s) and actuates via real Pointer/keyboard input
  at those coordinates by default; DOM/.click() is an optimization for
  controls where equivalence is proven, not the default actuation.
  This refines A1/P2; it does not kill them. The accuracy claim
  (location exact) survives; the actuation claim is corrected.
- (b) Batch maximization: CB 2.4 shows maximizing actions per image is
  the wrong goal. At 90% per-click hit rate, 20 clicks all correct
  first try is about 12.2% and 32 clicks about 3.4% under independence
  (illustrative, real errors correlate, but the direction holds). A
  batch should grow only when the executor proves subsequent steps are
  still valid. ARCH ACCEPTS: Layer 0 execute takes a plan of refs WITH
  preconditions, re-validates each ref immediately before acting (live
  rect re-read, which is P2), and halts on the first failed
  precondition. This also supplies the core of the stale-ref protocol
  B5 is missing: on live-rect disagreement, refuse and re-plan by
  default; click stale only when the executor proves the same element
  (same ref, same snapshot id, still unique, visible, enabled, geometry
  delta within tolerance). Never click a stale point on a
  destructive or message-sending action.
- (c) Scope: CB 2.2 (scope is part of the action data; a scope change
  must HALT the batch, never silently reframe) against ARCH A7 and the
  draft's P2-timed scope-refusal deletion. ARCH SIDES WITH CB against
  the draft. The refusal is reframed as snapshot binding, not deleted
  (section 1, A7). This is the one place ARCH asks the final
  adjudication to OVERTURN the draft.
- (d) "Mostly assembly": CB prices the composition independently (Zen
  prototype 2-3 days on a private fixture plus low-risk web tasks,
  broker merge plus AT-SPI plus Firefox limits 1-2 weeks for one
  engineer, plus days for an independent benchmark). That supports
  RTD's C2 and the draft's MODIFY on A1: "exists" meant a file exists,
  not that the composition works. ARCH CONCEDES the overclaim. The
  composition is the work, and it is unproven.
- (e) The 95% SSH figure: CB 2.7 shows no record supports exactly that
  11.6s of F2b's 12.26s is SSH dispatch. The laptop-side act-now logs
  start after the command arrives, so they cannot measure VM-to-laptop
  dispatch, and the cited 11.611s service figure is a different
  measurement. ARCH CONCEDES: F2b's 11.620s is dispatch time (SSH plus
  scp plus spawn), not proven SSH alone. The "SSH is 95%" slogan dies.
  No verdict changes, because S0 is already judged on the corrected
  mux numbers (fresh 4.43-5.29s over 7 samples, mux 0.91-1.46s over 11
  samples, saving about 3.2-3.5s per connection, about 3.5-5x, 460x
  dead; per act-now about 16s to about 5-6s), not on the 95% slogan.
- (f) CB 2.9 (installed code not reproducible from checkout):
  first_action.py not tracked in CB's checkout, installed cu.py has
  extra act-now branches, remote-tracking ref behind 622 commits.
  ARCH ACCEPTS as a precondition on A10: before the benchmark gates
  anything, lock the source commit, the installed artifact, and the log
  of the same build into one manifest. A gate that cannot name its
  build is not a gate. Note V-F6: CB read HEAD 4500a18; on todolist-push
  at HEAD 2864be4 first_action.py IS tracked, so the manifest point is
  about installed-vs-checkout divergence, not about that one file.
- (g) CB 2.10 (overlay flicker and think time): the LIQUID flicker test
  never ran because the plugin was not loaded, and think time is
  unmeasured (J10 open). ARCH ACCEPTS: do not attribute flicker or
  think time to SSH or screenshots without per-phase measurement. P6
  must cover think time.
- (h) CB eval restriction: unrestricted zen_dom eval (arbitrary JS in
  the current tab) must leave the default agent API and stay in a
  deliberate debug mode. ARCH ACCEPTS as an A1 API constraint: the
  daemon exposes an allowlisted snapshot/execute surface, not arbitrary
  eval. The snapshot API returns rects, roles, names, values, and
  states; it does not run agent-supplied scripts.
- (i) CB 2.8 (fixture numbers do not transfer): the 0.64s 15-step
  fixture run is a Polygon-process simulation, not a Polygon upload,
  with no same-task baseline, and 13/13 verified actions on a fixture
  cannot become a 90% commitment on other apps. ARCH ACCEPTS, and it
  strengthens A10: 90% must be defined as end-to-end TASK SUCCESS on
  held-out tasks, and CB's statistics give the form (100 held-out tasks
  need about 96 pass for 90% task success at 95% confidence by Wilson).
  The draft's "accuracy at least 90%" is adopted with this definition
  attached.

Net on CB-EXEC: same direction, overlapping to the point of merger, and
the differences resolve in CB's favor on actuation, batching, scope,
composition cost, and measurement discipline, and in ARCH's favor on
nothing contested. CB-EXEC is not a rival direction; it is the
executor design ARCH Layer 0 was missing. ARCH's position going forward
is Layer 0 built to the CB-EXEC contract.

## 3. Per-proposal verdict table (ARCH's final position)

Legend: ADOPT means do it as proposed. MODIFY means do it with the
stated change. REJECT means do not do it (one part inside A7, and one
timing deletion, are rejected and named). Rows: 10 ARCH, 8 GROUNDING
(P4 merged into A7), 5 SPEED (S0+D1, S1+D3, S2+D5, S3, D6), 7 CB.
Tally: ADOPT 15, MODIFY 14, REJECT 0 in full (2 parts rejected inside
merged rows), PENDING 0. CB-EXEC is now judged, not pending.

### 3.1 ARCH A1-A10

| ID | Proposal | Verdict | Evidence and reasoning |
|----|----------|---------|------------------------|
| A1 | Layer 0 persistent driver daemon (snapshot/execute/verify, structured-first) | MODIFY | Direction right and now consensus. Gate accepted (B6): staged prototype must prove snapshot/execute/verify end to end on one live ws2 clone chat before anything is deleted. Amendment vs draft: the daemon CONTRACT is written early (section 4 step 2) so P2/S1/P5 build to it; only the proof stays late. Composition unproven (RTD C2, CB 2-3 day prototype plus 1-2 week merge estimate). Prototype design must cover the task lock, pill visibility, one-session-per-browser constraint, session-holding scope (C5), daemon crash and stale-state behavior, and lifecycle across sleep and reboot. |
| A2 | Layer 1 pixels demoted to fallback-only, pixel-band labeled weak | ADOPT | Vision 58.6% first-try (E2) vs DOM rects exact at 0.030s; G30/G31 are vision errors, never coordinate errors. Constraint accepted: demote only after P1 and its fallback trigger are proven; Zen chrome UI stays pixel-primary, now a MEASURED boundary (PROBE-P8 HTTP 500, section 0.2). Fallback stays for canvas, games, video, Zen chrome UI. |
| A3 | Delete session supervisor tree | MODIFY | Direction right, timing conditional. Delete only when the driver demonstrably holds scope plus cancel latch plus lock on a live run. Until then the supervisor is the lock holder. Concession: the F1 cluster is partly environment faults, so deletion does not delete those modes. |
| A4 | Delete overlay daemon server (keep pill visibility) | MODIFY | End state right, sequence gated. Session-level pill first (acquire once per task, server kept, measured, removes the 315-349ms per-batch tax); driver-owned pill only with proof it shows and clears, including no stale or missing pill when the driver dies mid-task; delete the server only then (B3). |
| A5 | Delete one-shot SSH loop (persistent Broker only) | MODIFY | Persistent-first is right (fresh SSH 4.43-5.29s, mux 0.91-1.46s, saving about 3.2-3.5s per connection). The word "only" is REJECTED: the VM reaches the relay only through SSH, and one-shot SSH is the recovery path when the broker dies. "Only" applies to the default path, never to recovery. |
| A6 + D2 | Delete file-based observation/action IPC (A6) / delete scp for JSON files (D2) | ADOPT for transport | JSON over the persistent channel replaces scp per step. Scope condition: files stay as the audit and evidence trail; the JPEG still travels for the human VISION 2 check; file IPC stays as the fallback transport when no Broker is reachable. |
| A7 + P4 + D4 | Act-now after-image scope fix, both-fields shape | MODIFY | Both-fields shape ADOPTED (after scope-matching chainable, after_screen verification only and documented non-chainable, regression test, via AMEND4 item 12). The delete-entirely half is REJECTED (loses human evidence and frame-change signal for about 0.25s). The scope-refusal deletion is REJECTED as a deletion: refs are bound to (snapshot id, scope); a scope change HALTS the batch (CB 2.2, J40 +45/+12px miss on silent substitution). The refusal changes form to snapshot binding, it is not deleted with P2. This overturns the draft's P2 timing for that deletion. |
| A8 | Delete pixel-band verification for structured targets | MODIFY, sequenced behind P5 | Direction right: the band is admitted necessary-not-sufficient (cu.py:1023-1076) and the DOM value check is sufficient at 0.002-0.015s. Delete band-as-pass-signal only where the per-action DOM assert exists and is mandatory; until then the band stays as a diagnostic. |
| A9 | Coordinate model to one system (CSS px element rects, converted once at the driver edge) | ADOPT for structured targets | Five-frame tower has five proven bug sites (F2b-1, C12, amend3 step 5, G28, after-scope trap); the one-conversion path exists (fastpath.dom_rect_to_screen_point). Dependency SATISFIED: AMEND4 items 1, 5-6 landed (cc964b2, b44a5ea). Pixel fallback keeps its own frame internally. |
| A10 | Acceptance test becomes 0-vision live benchmark on real ws2 clone chats | ADOPT as staged | Final gate: live 0-vision on real ws2 clone chats, DOM harvest, plan, execute, DOM verify, zero screenshots in the machine loop, total wall time end to end including transport, owner approval per run. Staging: fixture 2-vision first (it has never run), P3 first. Live 2-vision is a diagnostic only, not a gate (draft's B1 lift accepted). AMENDMENTS from CB: 90% means end-to-end TASK SUCCESS on a held-out set (100 tasks need about 96 pass for 95% confidence by Wilson); per-phase timing split required; source/artifact/log manifest required before the benchmark gates anything (CB 2.9). |

### 3.2 GROUNDING P1-P9 (P4 merged into A7 above)

| ID | Proposal | Verdict | Evidence and reasoning |
|----|----------|---------|------------------------|
| P1 | DOM/a11y default router (encoded in code, not convention) | ADOPT | Two perception stacks with no routing rule drift to the worse one. Requirements: one function returning the perception source; fail closed to the labeled screenshot fallback; per-target routing table proven per target before the default flips; a log line on every routing decision. Interim honest state: Brave tasks still route to screenshots until P3 lands. |
| P2 | Element-ref action interface rewrite (live rect re-read at execution, screen-point action form) | MODIFY | Direction right and highest-leverage code change after P3: the exact-rect to lossy-image-point round trip is proven wasteful from source (fastpath.py:195-243, dom_act.py:312, cu.py:1000-1005). Gate narrowed by V-F4: AMEND4 items 2-4 have LANDED, so the stale-ref disagreement protocol is now the SINGLE outstanding gate. ARCH supplies the protocol core (section 2.3b): re-validate each ref immediately before acting; on disagreement refuse and re-plan by default; click stale only when the executor proves the same element. Delete dom_rect_to_image_point from the live path (keep for tests and legacy). Actuation per CB-3: real Pointer/keyboard input at DOM-located coordinates by default; DOM/.click() only where equivalence is proven. |
| P3 | Brave relaunch with debugging port (controlled experiment) | ADOPT as a controlled experiment | Single highest-leverage unblocker: clone chats live in Brave, Brave holds no debugging port on its default profile (cdp.mjs comment verified verbatim). Status: NOT-RUN (clone1 batch 9 open since 06:01). Conditions: quiet window owned by the coordinator, never mid-batch; verify /json/list shows the Muse tab and login intact; one fill plus assert on a scratch input. Additions accepted: CDP port 9223 local exposure noted; Chromium fallback is a migration with re-login and clone reconfiguration, needs its own login-persistence check. No live-task migration until it passes. If P3 fails, re-plan around Zen Marionette only and report it plainly. |
| P5 | DOM verification mandatory | MODIFY | Direction right; the code admits the band is insufficient. Blanket mandate BLOCKED as stated: the assert set does not exist for every action type (focus_check/type_check are still optional hooks, D1 V13). Mandatory PER ACTION TYPE as its assert lands, plus an explicit per-action exception list (scroll position, hover state) where DOM assert is impossible and pixel stays the only signal. The band stays as a diagnostic until then. |
| P6 | Measure the vision call | ADOPT, with specification fix | Cheapest item and a precondition for honest speed claims: capture is 15-30ms and DOM rects 0.030s, but the model read that locates the target is seconds and timed nowhere. Specification fix (RTD, accepted): timestamp points are observation delivered to the agent vs located target returned; logging owner is the harness, not cu.py. ARCH addition (CB 2.10): measure think time too; until both numbers are logged, nobody may claim the 10s target is met. Bundle with S0. |
| P7 | Session handover protocol | MODIFY | One remote session per Firefox instance is proven (4 runs), so a protocol is needed IF a task genuinely needs two protocols. First answer whether Marionette-only suffices (the benchmark already runs Marionette-only, harvest plus input, and zen_dom harvest IS Marionette). Write the handover protocol only if a task genuinely needs BiDi plus Marionette. Price noted: a handover costs 4-7s per switch (BiDi new 1.51-2.77s fresh, Marionette attach 2.65-4.12s), comparable to the SSH tax being deleted. |
| P8 | Zen chrome Marionette context test | ADOPT as a probe, now CLOSED | Premise verified, result BLOCKED (PROBE-P8 3790901, HTTP 500, MOZ_REMOTE_ALLOW_SYSTEM_ACCESS required, C12 reproduced). Consequence settled: keep screenshots ONLY for Zen chrome UI and record that boundary explicitly. The only path to chrome context is an owner-approved Zen restart with the env var set, which no probe does. No further time on this path. |
| P9 | Keep one screenshot for the human (VISION 2 stays, machine scores by DOM) | ADOPT | Correct division: screenshots are a human evidence channel, not a machine perception channel. Wording correction accepted: VISION 2 is the agent looking at the threads and reporting to the human, not the owner looking directly. Cost about 0.25s plus one vision read, noise against the total. Attached to A10. |

### 3.3 SPEED S0-S3 plus six deletions

| ID | Proposal | Verdict | Evidence and reasoning |
|----|----------|---------|------------------------|
| S0 + D1 | Step 0 persistent SSH multiplexing, do now / delete fresh SSH per call | ADOPT on CORRECTED numbers | Fresh SSH 4.43-5.29s (7 samples), mux 0.91-1.46s (11 samples, rc=0, master verified alive). Saving about 3.2-3.5s per connection, about 3.5-5x, NOT 460x and NOT 0.01s. Per act-now about 16s becomes about 5-6s. SPEED's 1.6x per-task estimate must NOT be quoted; D1's roughly 1.3-1.4x on a CL2-MSG-class task is the working figure until a recompute. Conditions: explicit fallback to fresh SSH, master-death logging, per-socket watchdog (a half-dead master can hang; ControlPersist=600 can leave a stale master on a dead Tailscale route). Soak test runs IN PARALLEL, advisory, not a gate. Status: not implemented (V-F7, no ControlMaster flags in ssh-laptop.sh). |
| S1 + D3 | Step 1 act-now over the persistent relay broker / delete per-batch session spawn | MODIFY, proof-first | Direction right: per-batch spawn is a real tax (0.4-2.1s) plus a real failure mode (20s deadline, timeout never falls back). But S1 is a BUILD, not a switch: the relay is alive (PID 1821) yet zero references to session_remote or Broker exist in first_action.py or cu.py (grep 0 hits), so the broker path from the VM is unproven end to end, and single-owner socket semantics under concurrent VM workers are unexamined. Gating: prove one live batch end to end over the broker from the VM first, then delete the per-batch spawn; keep the spawn as fallback until proven. CB-5 addition: the daemon owns a serialized queue (serialize or refuse, never interleave). Session-level pill (server kept) lands in the same step. |
| S2 + D5 | Step 2 DOM-first plus code-exec plus checkpoint verification, CU_CODE_EXEC=1 on / delete per-action model call as default | MODIFY, gated | The 10x path, already built and merged (code_exec.py 880 lines, Pick 1 winner, merge 453adc4), flag OFF in the live path (verified live, CU_CODE_EXEC unset). Blanket flip BLOCKED (B2): Y1b council 3 BLOCKED Phase A on 84b88bb with 14/20 passing and 3 real fails (1e chr NameError; 2a codemode wall preemption 7.20s, error only after the C loop; 2b code_exec wall preemption 6.20s, ok=True with NO error, silent success), and the named gate (2-vision bench) has never run. Gating in order: fixture bench green, fix the 3 Y1b real fails, flip for ONE live task class (clone chat sends) with act-now as fallback, measure, then expand. "10x path" corrected to 3-5x on unmeasured model inference time (SPEED's own honest limit: 30-60s if vision reading dominates). |
| S3 | Step 3 laptop-side task runner, only if Step 2 plateaus | MODIFY, fold into A1 | S3 substantially overlaps A1: a laptop-side runner that grounds, acts, and verifies locally IS the A1 driver daemon approached from the other side. One design decision, not two builds. Gating: the plateau criterion must be defined NUMERICALLY BEFORE the S2 flip starts (threshold, run count, decision owner), so the trigger is not argued later. The numbers are set from the fixture bench plus first live runs baseline, not invented here. |
| D6 | Delete 120s freshness window as a gate on DOM work | MODIFY, scoped | For DOM-grounded work, re-read the DOM (0.030s) instead of refusing for staleness. Correction accepted (RTD): the refusal at cu.py:773 also guards against future-clock observations, so keep the future-clock refusal and drop only the age refusal for DOM paths. Keep the window for pixel-addressed work, where staleness is real. |

### 3.4 CODEX-BREAKTHROUGH CB-EXEC (2596287, judged here, no longer pending)

| ID | Proposal | Verdict | Evidence and reasoning |
|----|----------|---------|------------------------|
| CB-A | CB-1 three-part result contract (input sent, correct target received input, post-state verified) | ADOPT | The verification hole is proven (CB 2.1, G30): desktop checks know cursor position, not which element received the event, and ok=true can mean a click on empty space. Adopt as the Layer 0 execute/verify contract: ok becomes input_sent, verified=true only on postcondition. Subsumes P5/A8 for structured targets. |
| CB-B | Scope as action data, halt on scope change (CB 2.2) | ADOPT | Proven from the record: _fresh_observation substitutes a screen capture without reframing coordinates; J40 missed by about (+45,+12)px while returning ok. Refs bind to (snapshot id, scope); a scope change halts the batch. This overturns the draft's P2-timed scope-refusal deletion (section 1, A7). |
| CB-C | Real-input actuation, DOM locate (CB 2.5) | ADOPT | DOM clicks are not equivalent to real input (BiDi pointer click failed, Marionette viewport limits, DOM fill may not equal real typing; Browse hover case). Default actuation is real Pointer/keyboard input at DOM-located coordinates; DOM/.click() only where equivalence is proven. Refines ARCH's execute. |
| CB-D | Per-step preconditions, no blind batch maximization (CB 2.4) | ADOPT | At 90% per-click, 20 clicks all correct first try is about 12.2% and 32 clicks about 3.4% under independence. Plan steps carry preconditions; the daemon re-validates each ref immediately before acting and halts on the first failure. Supplies the stale-ref protocol core (section 3.1 P2). |
| CB-E | One local broker owning session/overlay/browser, serialized queue, long-lived session driver (CB 2.6, CB-6) | ADOPT, merged into A1/S1 | Act-now does not use the session driver today (first_action.py builds a session per invocation); zen_dom opens and closes a session per command. One owner, one queue, serialize or refuse, never interleave; no competing BiDi and Marionette clients on one Zen (one session slot). This IS Layer 0; merge with A1/S1, do not build twice. |
| CB-F | Measurement discipline (CB 2.3, 2.7, 2.8, 2.10) plus manifest (CB 2.9) | ADOPT as requirements | No "SSH is 95%" slogan (dispatch, not proven SSH); no fixture-to-real transfer (0.64s fixture run, 13/13 fixture passes do not commit 90% on other apps); flicker and think time unattributed without per-phase measurement (P6 measures think time too); manifest locks source commit plus installed artifact plus log of the same build before A10 gates anything. |
| CB-G | Held-out benchmark statistics (CB section 3) | ADOPT as A10 amendment | Define 90% as end-to-end TASK SUCCESS, not click hit rate, on held-out browser plus desktop tasks with new content and layout. 100 tasks need about 96 pass for 90% at 95% confidence by Wilson. Report per-phase p50/p90 (model, SSH, broker, observe, act, verify), model-call count, full-screen vs crop vs DOM/a11y query counts, retries, postcondition accuracy, and false successes. Compare screenshot-only, DOM plus real input, AT-SPI plus real input, and the proposed executor on the same set, order interleaved. |

## 4. Order of work (ARCH's revised order)

ARCH accepts the draft's order with three amendments: the daemon
contract moves early (step 2), the P8 probe is closed (step 2), and the
scope refusal is reframed rather than deleted (step 6).

0. S0 plus P6, now. Persistent SSH multiplexing with explicit fallback,
   master-death logging, per-socket watchdog; P6 vision-call
   measurement with timestamp points and harness owner specified, plus
   think-time measurement (CB 2.10). Gate to step 1: fallback explicit
   and watchdog in place. Soak test runs IN PARALLEL, advisory, not a
   gate.
1. AMEND4 continues in parallel, slower, per the owner 06:09 TWO TRACKS
   rule. Items 1-8 landed; item 12 (A7/P4) lands via the in-flight run;
   verify the regression test. Kill rule at reconciliation: items the
   rewrite deletes get killed (items 3-4 already landed, so the rule is
   moot for them and applies to items 9-10 if the rewrite subsumes
   them). The two tracks run in sequence per item on shared files, not
   in parallel on the same functions.
2. Daemon CONTRACT written (Layer 0 plus CB-EXEC merged spec), in
   parallel with AMEND4, no code deleted: snapshot/execute/verify,
   CB-1 three-part result, snapshot-bound refs, per-step
   preconditions, serialized queue, task lock, pill ownership,
   crash/stale/sleep lifecycle, allowlisted API with no arbitrary eval.
   P3 Brave relaunch experiment in a real quiet window between clone
   batches, coordinator-owned, never mid-batch. P8 is DONE (BLOCKED,
   boundary recorded, section 0.2). Fixture bench run may start as soon
   as step 0 lands (it needs no quiet window; its runtime must first be
   installed, PROBE-S2).
3. Fixture 2-vision bench run green (it has never run; the program's
   gate cannot be an unrun script). Fix the 3 Y1b real fails on
   code-exec (1e, 2a, 2b). Both are B2 limbs; both must land before
   step 5.
4. P1 router plus P5 asserts per action type, built as the contract's
   router and assert set, not as separate patches to the old loop.
   This is the X3/D3 hold ARCH keeps: S2's checkpoint verification IS
   P5, so flipping code-exec while DOM verification is still optional
   hooks leaves a window with pixel-band-only verification.
5. Define the numerical plateau (coordinator, before the flip), then
   the S2 flip for ONE live task class (clone chat sends) with act-now
   as fallback. Measure model-call count and wall time. Expand only on
   measurement.
6. P2 element-ref interface rewrite. Gate narrowed to the stale-ref
   protocol only (items 2-4 landed, V-F4); protocol core is in section
   3.1. A9 one-system coordinates land in this step. The scope refusal
   is REFRAMED as snapshot binding here, NOT deleted.
7. S1 broker path proof from the VM on one live batch (proves the
   daemon's transport plus queue), then delete the per-batch spawn.
   Session-level pill (server kept) in the same step. P7's
   Marionette-only question is answered before any handover protocol is
   written.
8. A1/S3 merged daemon prototype, gated on one live ws2 clone chat
   proof (B6 lift). The prototype proves snapshot/execute/verify end to
   end; the S1 proof in step 7 and this proof may share one live run to
   save a live cycle.
9. A3/A4/A5 deletions last, each gated on its replacement proving
   (A3: driver holds scope plus cancel latch plus lock; A4: session-level
   pill measured, then driver-owned pill crash proof, then delete the
   server; A5: broker proven on the VM path with one-shot SSH kept as
   recovery). ARCH asks the final adjudication to attach DATES to these
   gates, not leave them open-ended: a staged plan that never schedules
   its deletions is a patch track with a new name.
10. Acceptance ladder (section 5).

## 5. Acceptance test

Ladder with two required rungs and one diagnostic option, as the draft
settles it, plus CB's statistical and manifest amendments.

- Rung 1 (required, first): fixture 2-vision benchmark. Headless
  Firefox, local fixture. It has never run at all; bring the runtime up
  (PROBE-S2: selenium plus Firefox plus geckodriver at the hardcoded
  paths) and run it. Pass criteria: the script's own gates (V12
  sent-bubble gate after each message, scoring by OUTCOME in the thread
  DOM, never point-in-box).
- Final gate (required, last): live 0-vision benchmark on the REAL ws2
  clone chats (clone1 Brave plus clone2 Chrome). DOM harvest, plan,
  execute, DOM verify, zero screenshots in the machine loop. Pass
  criteria: end-to-end TASK SUCCESS at least 90% on a held-out set (100
  tasks need about 96 pass for 90% at 95% confidence by Wilson),
  scored by DOM outcome (V12 sent-bubble gate, message in the thread
  DOM, never point-in-box); total wall time measured end to end
  including transport, split per phase (model, SSH, broker, observe,
  act, verify); model-call count and retry count reported. One final
  screenshot is kept as unscored human evidence (P9); it must not feed
  the score. Conditions: P3 closed first; quiet window with clone
  coordination; owner approval per run; agreed test messages so the
  clones' working threads are not polluted.
- Precondition (CB 2.9): the manifest locks the source commit, the
  installed artifact, and the log of the same build before the
  benchmark gates anything. A gate that cannot name its build is not a
  gate.
- Diagnostic option (not a rung): live 2-vision. If the live 0-vision
  run fails, the team may run live 2-vision to localize (script vs DOM
  path). It is not required before the final gate.

What the fixture run does NOT prove, recorded as a gap not papered
over: a fixture pass alone repeats the F1a/F2b pattern (pass on the
exercise, unproven on the real task). The live run is the proof the
fixture cannot give, because the real tasks fail on Brave on ws2, where
the DOM path does not reach yet (P3).

## 6. What STOPS (blocking findings, ARCH's final list)

- B1 (A10 straight to 0-vision live): LIFTED, agreed with the draft.
  The councils' staged A10 satisfies the ladder's substance, and the
  live 2-vision intermediate adds nothing measurable as a gate.
- B2 (S2/D5 blanket CU_CODE_EXEC=1 flip): STANDS. Lift: fix the 3 Y1b
  real fails (1e, 2a, 2b), fixture benchmark green, then flip for ONE
  live task class with act-now as fallback, measure, then expand.
  PROBE-S2 confirms both limbs are unmet (bench never run, fails still
  open in code).
- B3 (A4 overlay daemon deletion without a replacement): STANDS as a
  gate. Lift: session-level pill measured, driver-owned pill proves no
  stale or missing pill on crash.
- B4 (A3/A5 delete-first ordering): STANDS as a gate. Lift: the driver
  proves scope plus cancel latch plus lock, and the broker proves on
  the VM path with one-shot SSH kept as recovery.
- B5 (P2 immediate interface rewrite): STANDS, narrowed to the protocol
  limb only. Lift: the stale-ref disagreement protocol is specified
  (core supplied in section 3.1 P2). The AMEND4-items-2-4 limb is
  SATISFIED (items 1-8 landed, V-F4).
- B6 (A1 full replacement claim): STANDS as a gate. Lift: a daemon
  prototype runs snapshot/execute/verify end to end on one live ws2
  clone chat.
- ARCH additional stop 1: no scope-refusal deletion. The refusal is
  reframed as snapshot binding (section 1, A7; section 2.3c). Any plan
  that deletes it without the binding rule is blocked.
- ARCH additional stop 2: no A10 gate without the manifest (CB 2.9).
  The benchmark cannot gate a release until it names its build.
- ARCH additional stop 3: no deletion without its replacement proof
  (B3/B4/B6), and the final adjudication must attach dates to the
  deletion gates (section 4 step 9).
- What does NOT stop: S0 plus P6 now, AMEND4 continuing slower, the P3
  experiment in a quiet window, the fixture bench run, and the daemon
  contract writing in step 2.

## 7. What probe evidence would change ARCH's verdicts

PROBE-S0, PROBE-S1, PROBE-DOMZEN, and PROBE-P3 have no results yet;
PROBE-P8 has landed BLOCKED; PROBE-S2 is mid-run with two findings
already in (bench on branch, Y1b fails still open). What each result
would do:

- PROBE-S0 (mux soak and residual cost): if the master dies or hangs
  over hours, the soak becomes a gate (not advisory) and the fallback
  handling hardens; S0 stays ADOPT either way. If the residual about
  1.1-1.2s per call is confirmed as per-session sshd and shell setup,
  it strengthens S1 and A1 (the Broker and the daemon avoid per-call
  sshd sessions entirely). If mux reproducibly hit 0.01s under some
  named setup, S0's value rises and S1's urgency falls slightly; ARCH's
  daemon case does not change, because it rests on model-call count and
  verification, not on transport.
- PROBE-S1 (broker VM path): if the broker path proves end to end from
  the VM with serialize-or-refuse semantics, the B4 broker limb lifts
  and the S1 delete-half unlocks; the A1 prototype gains its transport.
  If it fails (the single-owner socket cannot serialize concurrent VM
  workers), S1 stays MODIFY and the daemon must specify its own queue;
  the CB-5 queue requirement is already in ARCH's contract, so no
  verdict flips, only the build order.
- PROBE-DOMZEN (Zen DOM harvest and input): if Marionette-only suffices
  for harvest plus input, P7 dissolves (no handover protocol written).
  If DOM clicks prove non-equivalent to real input on Messenger
  controls, CB-3 governs (real Pointer input at DOM coordinates, DOM
  clicks only where equivalence is proven); P2's execution side narrows
  to locate-only and no verdict flips.
- PROBE-P3 (Brave relaunch): NOT-RUN now. If it passes (login intact,
  /json/list shows the Muse tab, one fill plus assert on a scratch
  input), A10 unlocks and P1's Chromium branch is proven. If it fails
  (Brave refuses the port on its default profile and the Chromium
  migration is too disruptive), the DOM-first live path loses its
  highest-leverage unlock and the whole program re-plans around Zen
  Marionette only; ARCH Layer 0 stands for Zen, the Brave/CDP backend
  drops, and the A10 live benchmark moves to Zen chats or waits. That
  outcome must be reported plainly, not worked around silently.
- PROBE-P8 (Zen chrome context): LANDED BLOCKED, verdicts already
  updated. Screenshots stay ONLY for Zen chrome UI; A2's exception is a
  measured boundary. If a future owner-approved restart with
  MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 ever enables chrome context, the
  boundary moves, but that is an owner decision, not a probe.
- PROBE-S2 (fixture bench plus Y1b): bench files are on the branch
  (c5311ce, 7f3a70b) but the runtime is missing on this VM and the Y1b
  fails are still open in code. If the fixture bench passes AND the
  Y1b fails are fixed, the S2 one-class flip proceeds (B2 lifts). If
  the bench fails, the bench itself is the blocker: B2's bench limb
  fails and S2 stays blocked until the bench is fixed, because a gate
  that cannot run cannot gate anything. If the bench passes but the
  Y1b fails remain, S2 stays blocked; both B2 limbs are needed.

## 8. What ARCH concedes and what ARCH holds (honest record)

Concessions (ARCH was wrong or overstated, and the record proves it):

- "Mostly assembly" overstated the daemon's readiness (RTD C2, CB's
  2-3 day prototype plus 1-2 week merge estimate). The composition is
  the work.
- Big-bang rewrite rejected. The live loop must keep running; the
  rewrite stages behind measured wins.
- A7 delete-entirely wrong (about 0.25s saving vs lost evidence).
  A4 delete-first wrong (pill visibility is safety-critical). A5
  "only" wrong (VM reaches the relay only through SSH).
- The F1 failure cluster is partly environment faults, not
  supervisor-design faults.
- "SSH is 95%" unproven as SSH (CB 2.7). F2b's 11.620s is dispatch,
  not proven SSH alone.
- The DOM bench numbers are single-source (clone2 batch 7, C1).
  ARCH's original log cited them as if settled.
- ARCH's execute leaned toward DOM/.click(); CB-3 corrects it to real
  input at DOM-located coordinates.

What ARCH holds (unchanged from 074c1d7, now consensus or amended):

- The architecture is inverted: structured-first, pixels-last. Every
  failure in the record is a vision failure, never a coordinate
  failure (E2 17/29, pointer 0.5-0.9px, 29/29 executed).
- Rewrite, not patch: the deletions are the point, and they need dates
  attached at final adjudication, not open-ended "last".
- The daemon contract is written early (section 4 step 2), so P2/S1/P5
  build to one contract instead of three ad-hoc interfaces.
- The scope refusal is reframed as snapshot binding, not deleted
  (the one overturn ARCH asks of the draft).
- The acceptance test is the 0-vision live benchmark with 90% defined
  as task success on a held-out set, per-phase timing, and a
  source/artifact/log manifest.

## 9. Evidence index

- ARCH log: improvements/worker-arch-review-log.md (074c1d7).
- GROUNDING log: improvements/worker-grounding-review-log.md (d1fc4e9).
- SPEED log: improvements/worker-speed-review-log.md (a4ecb49).
- CODEX-BREAKTHROUGH report: improvements/codex-breakthrough-report.md
  (2596287, 138 lines).
- Draft adjudication: improvements/worker-click3-adjudication-log.md
  (9d23834).
- D1: improvements/worker-click3-d1-review-log.md (37f457e).
- D2: improvements/worker-click3-d2-review-log.md (6d1bf04).
- D3: improvements/worker-click3-d3-review-log.md (14fc139).
- RTD: improvements/worker-click3-rtd-review-log.md (e96b2ff).
- X1: improvements/worker-click3-x1-response-log.md (0cf601c).
- X2: improvements/worker-click3-x2-response-log.md (d5b205d).
- X3: improvements/worker-click3-x3-response-log.md (2b0c73c).
- XRT: improvements/worker-click3-xrt-response-log.md (6cb3f95).
- PROBE-P8: improvements/worker-probe-p8-log.md (3790901).
- PROBE-P3: improvements/worker-probe-p3-log.md (7b1006a, NOT-RUN).
- PROBE-S2: improvements/worker-probe-s2-log.md (untracked at writing;
  bench commits c5311ce, 7f3a70b).
- AMEND4 landed at HEAD 2864be4: items 1 (cc964b2), 2 (c1ea773), 3
  (62b740e), 4 (72120aa), 5-6 (b44a5ea), 7 (49081aa), 8 (af0fa87).
- Numbers used: vision 17/29 = 58.6% first-try, Wilson 95% 40.7%-74.5%,
  pointer error 0.5-0.9px, 29/29 executed; G30 64px and 75px, G31 45px,
  J40 about (+45,+12)px, J37 patch diff 6.627; DOM 66 rects median
  0.030s, 5 clicks all hit, verify 0.002-0.015s (single-source); fresh
  SSH 4.43-5.29s (7 samples), mux 0.91-1.46s (11 samples), saving about
  3.2-3.5s per connection, about 3.5-5x, 460x dead; per act-now about
  16s to about 5-6s; per-task about 1.3-1.4x working figure (SPEED's
  1.6x not to be quoted); F2b order-to-overlay 12.262s (dispatch
  11.620s, observe 0.233s, Python 0.060s, overlay 0.349s); overlay
  acquire 315-349ms per batch; CB JSONL 199 lines, p50
  order-to-overlay 337.5ms, max 368.4ms, p50 wrapper 2.288s, max 6.95s,
  167 ok=true, 32 ok=false, 195 session, 4 fallback, 0 timeout, 5
  source=captured; Y1b 14/20, 3 real fails (1e chr NameError, 2a 7.20s,
  2b 6.20s ok=True silent success); handover 4-7s per switch (BiDi new
  1.51-2.77s, Marionette attach 2.65-4.12s); 90% per-click gives 20
  clicks about 12.2% and 32 clicks about 3.4% all-correct; 100 held-out
  tasks need about 96 pass for 90% task success at 95% confidence.
- Code refs verified by me this session: cu.py:1665-1666 scope refusal,
  code_exec.py:107 SAFE_BUILTINS, codemode.py:37 SAFE_BUILTINS,
  ssh-laptop.sh (no ControlMaster flags).

## 10. Log of this response

- 06:37 +07 (T+0s): task received. Repo on todolist-push HEAD 2864be4,
  fetched first.
- 06:37-06:41 +07 (T+0-4m): read all 13 inputs in full (section 0).
- 06:41-06:43 +07 (T+4-6m): spot checks V-F1 to V-F7, probe state
  section 0.2.
- 06:43-06:55 +07 (T+6-18m): wrote this log. Next: fetch plus rebase
  first if the branch moved, commit this file only with an explicit
  pathspec, verify with git ls-remote, report to COORD-CLICK-3.
