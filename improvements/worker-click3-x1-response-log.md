# Worker CLICK3-X1: D1 cross-response to D2, D3, and RTD

Owner: the owner. Role: I hold the D1 reviewer position from its log
(improvements/worker-click3-d1-review-log.md, commit 37f457e, 538 lines).
The original D1 reviewer completed and cannot receive follow-ups, so I
answer the other three reviews from D1's position, with D1's verdicts as
my starting point. Decision criterion (owner standing rule 06:07): judge
every proposal by the accuracy and speed of its FINAL RESULT, never by
rewrite size or cost. Cost is IRRELEVANT. No em dash or en dash anywhere
in this file. No personal info. Evidence with every claim. Never ydotool.
This is a review response, not my own work, so no self-healing question
arises.

## 0. Log (wall-clock Asia/Ho_Chi_Minh + elapsed from task start)

- 06:15:25 +07 (T+0s): task received. Repo ~/workspace/computer-use-wayland,
  branch todolist-push, HEAD f4dcfa3 at start (fetched first; branch had
  moved past D1's commit 37f457e).
- 06:15-06:20 (T+0-5m): read all four review logs in full: D1 (37f457e,
  538 lines), D2 (improvements/worker-click3-d2-review-log.md, 6d1bf04,
  387 lines), D3 (improvements/worker-click3-d3-review-log.md, 14fc139,
  242 lines), RTD (improvements/worker-click3-rtd-review-log.md, e96b2ff,
  209 lines).
- 06:20-06:22 (T+5-7m): spot-checked RTD's new evidence (section 1).
  I did not re-run SSH probes: fresh and mux legs are now measured four
  ways (SPEED, D1, D2, D3, RTD); a fifth measurement adds nothing.
- 06:22-06:38 (T+7-23m): wrote this log.

## 1. What I spot-checked new in this round

- X1. Y1b BLOCK is real. Commit 9d9bd63 exists in git log: "Y1b verdict
  council 3: OVERALL Phase A BLOCK on 84b88bb (14/20, 3 real fails,
  2 probe artifacts)". Commit 84b88bb ("fix: harden code execution
  envelopes") also exists. SPEED never mentions this block, and D1
  missed it too (D1's log has no mention of 9d9bd63; D1 checked the
  code-exec gate lines but never checked git log for a verdict on the
  executor). RTD's B2 rests on a real record.
- X2. Broker client unproven from the VM. `grep -c 'session_remote\|Broker'
  scripts/first_action.py scripts/cu.py` returns 0 and 0. RTD's S1
  claim is verified: the Broker exists in session_remote.py but nothing
  in the live act-now path references it, so S1 is a build, not a switch.
- X3. P2/AMEND4 collision is real. AMEND4 prompt
  (~/workspace/codex-amend4-prompt.md) item 4: "thread type_x_ranges
  through the CLI act path, CodeExecBackend.act, and BrowserAdapter.act
  (mirror first_action.py:599-613)". Those are exactly the paths P2's
  element-ref interface rewrite touches. RTD's B5 rests on a real
  collision. Neither D2 nor D3 mentions AMEND4 items 2-4 in its P2 row.
- X4. Bench status. tests/two_vision_bench.py docstring on origin/main:
  "BUILD ONLY, no live run yet", VISION 1 is a DOM harvest not a
  screenshot, Marionette only, live mode refuses unless both --live and
  --confirm-live are given plus a plan-URL gate. RTD's stronger claim
  ("never run, even in fixture mode") I did NOT independently verify
  (no run record checked); the BUILD ONLY docstring is consistent with
  it, so I treat fixture-unrun as RTD-claimed, not as my own verification.
  It does not change any verdict below, since D1 already staged fixture
  first.
- X5. D1's own tally error. D1's log claims "ADOPT 20 rows" but then
  lists 21 entries. Corrected count in section 4: 26 rows total
  (10 ARCH, 8 GROUNDING with P4 merged into A7, 4 SPEED steps, 4 SPEED
  deletions). This response counts precisely.

## 2. The nine disagreements

### (1) SPEED 460x: dead, and the corrected S0 expectation

Positions: D1 measured mux 0.94/1.18/1.29s (n=3, rc=0, master verified
alive) plus a real command 0.91s, about 5x, and caught the 0.01s
failed-fast trap (rc=255, master not up). D3 measured 8 samples
0.91-1.46s, mean about 1.25s, about 3.5x. D2 verified only the fresh
side (5.06s) and trusted SPEED's 0.01s as "order of hundreds". RTD
incorporated the D1/D3 correction and added the failed-fast diagnosis.

AGREE with RTD and D3. 460x is DEAD. Corrected S0 expectation, now
measured four ways: fresh 4.43-5.29s (SPEED 4.43/4.93/4.48, D1 5.29,
D2 5.06, D3 4.447, RTD 4.61); mux 0.91-1.46s (D1 and D3). Saving about
3.2-3.5s per connection, about 3.5-5x, not 460x. Per act-now (3 connects)
about 16s becomes about 5-6s (D1 said about 5s, D3 about 6s, RTD 5-6s;
I converge on 5-6s), not about 2s. Per observe (2 connects) about 8s
saved (D1's figure, unchanged). D1's failed-fast diagnosis is now the
accepted explanation for SPEED's 0.01s, adopted by RTD. D2's "order of
hundreds" is superseded: D2 trusted without re-measuring, and two
independent re-measurements refute it; D2's S0 verdict stands, its
magnitude note does not. SPEED's 1.6x per-task estimate was built on
0.01s and must be recomputed before anyone quotes it (RTD); D1's
corrected 1.3-1.4x on a CL2-MSG-class task stands as the working figure
until that recompute. The residual about 1.1-1.2s per call (per-session
sshd and shell setup, which multiplexing does not remove) is itself an
argument for S1 and A1, as D3 and RTD both note.

D1 verdict: UNCHANGED. S0 stays ADOPT with corrected numbers. One
change inside it: the 1-day soak test moves from a gate to advisory.
D1's log said soak "before calling it done"; RTD and D2 both say the
fresh-SSH fallback makes the soak advisory, and D1 accepts that. The
soak runs in parallel; a master death falls back to fresh SSH, slow
but correct.

### (2) Ordering: S2 before P1/P2/P5 (D1) vs P1/P2/P5 before S2 (D2/D3) vs fixture + Y1b fixes before S2, P2 after AMEND4 items 2-4 (RTD)

Positions: D1 order was S0, P3/P8, A7, S2, P1/P2/P5/A9, S1, A1/S3,
A3/A4, A10. D2: S0/P6, item 12, P3, P1/P2/P5, S1 then S2 gated on
fixture, A10 staged, A1, A3/A4. D3: S0/P6, P3, S2+P1+P5+P2 in one step,
S1, A1, A10. RTD: S0, AMEND4, P3, fixture bench, Y1b fixes, S2 for one
task class, P1/P5 then P2 after AMEND4 items 2-4, S1 proof, A1/S3
decision, A10 ladder.

D1 CONCEDES the two load-bearing parts of RTD's order and does not
concede the rest. First, D1's S2-before-P1/P2/P5 assumed S2 is a flag
flip on built code. RTD's B2 (verified by me, X1) kills the blanket
flip D1 adopted: Y1b BLOCKED Phase A on 84b88bb with 3 real fails, and
the named gate (2-vision bench) has never run. S2 cannot precede the
fixture bench run and the Y1b fixes. D1's S2 moves to after those two
steps and becomes a one-task-class flip with act-now fallback (RTD's
shape). Second, P2 cannot precede AMEND4 items 2-4: the collision is
verified from the AMEND4 prompt (X3), and D1's ADOPT never checked it.
P2 moves to after items 2-4 land, with the stale-ref protocol specified
first. D2/D3's P1/P2/P5-before-S2 is therefore half right: P1 and P5
are rewiring of existing code with no collision, so they can proceed
alongside the gated S2; only P2 is collision-blocked. D1 does not
accept D2/D3's ordering as a block (P1/P2/P5 all before S2), because
it delays the S2 measurement behind a rewrite that is itself blocked.
D1 keeps S0 first and P3 early (all four agree on those), and keeps A7
early via AMEND4 item 12 (all four agree). Revised D1 order is in
section 5. Net: D1 moves from its own order toward RTD's, and past
D2/D3 on the two points where RTD has new evidence.

### (3) A10 acceptance: 0-vision live as final gate staged behind fixture (D1/D2/D3) vs ladder, BLOCK straight-to-0-vision (RTD, B1)

Positions: D1, D2, D3 all adopt 0-vision live on ws2 clone chats as the
final gate, staged behind the fixture 2-vision bench. RTD says ladder:
fixture 2-vision, live 2-vision, then 0-vision, and BLOCKS the jump.

AGREE with RTD's ladder, with one correction to RTD's objection. D1
CONCEDES the missing rung: D1 staged fixture 2-vision then live
0-vision, skipping the live 2-vision proof. The bench has never run
even in fixture mode (BUILD ONLY, X4), so D1's jump skips two proofs,
not one, and the live 2-vision run is the proof that DOM works on real
Messenger pages. D1 accepts the ladder: fixture 2-vision, live
2-vision at 90 percent or better DOM-scored accuracy, then 0-vision.
But RTD's B1 point (2), that A10 "removes the human's only look at the
outcome", does NOT apply to D1's form: D1's A10 row and section 6 both
keep VISION 2 as a human look (P9), scored by DOM, and D2/D3 say the
same. RTD's objection hits a straw form of A10 that drops the
screenshot, not D1's form. D1's final gate remains 0-vision live; only
the path gains a rung.

D1 verdict change: A10 ADOPT to MODIFY (ladder: fixture 2-vision, live
2-vision, then 0-vision; 0-vision only after live 2-vision passes and
the P5 assert set is complete).

### (4) S2 blanket flip: ADOPT (D1/D2/D3) vs BLOCK blanket flip (RTD, B2)

AGREE with RTD. D1 CONCEDES. D1's ADOPT did not know of the Y1b BLOCK
(D1's log never mentions 9d9bd63; SPEED omitted it, and D1 checked the
gate lines but not the verdict record). Verified by me (X1): 14/20
probes passing, 3 real fails, 2 probe artifacts, Phase A BLOCKED on
84b88bb. Flipping CU_CODE_EXEC=1 on the live path before those 3 real
fails are fixed ships a known-broken executor to live tasks. D2/D3's
"gated on the fixture bench" is necessary but NOT sufficient: a fixture
bench pass does not fix the 3 real fails, so the gate must name both
the bench run and the Y1b fixes. D1 moves past D2/D3 toward RTD. The
"10x" label: D1 already recorded the honest limit (30-60s if vision
reading dominates, 3-5x better than about 100s), so RTD's 3-5x
correction changes no D1 number, only the label D1 never used for the
flip itself.

D1 verdict change: S2 ADOPT to MODIFY. Sequence: run the fixture bench,
fix the 3 Y1b real fails, flip the flag for ONE live task class (clone
chat sends) with act-now as fallback, measure, then expand.

### (5) P2 immediate rewrite: ADOPT (D1/D2/D3) vs BLOCK immediate (RTD, B5)

AGREE with RTD. D1 CONCEDES. The collision is verified from source
(X3): AMEND4 item 4 threads type_x_ranges through the CLI act path,
CodeExecBackend.act, and BrowserAdapter.act, exactly the functions P2
rewrites. Running P2 in parallel with AMEND4 item 4 guarantees merge
collisions and wasted work on the same functions. D2/D3 never checked
this (neither mentions items 2-4 in its P2 row; D2 mentions only item
12, D3 cites AMEND3 step 2). RTD's second point also stands: the
stale-ref and mid-plan-mutation protocol is unspecified (live rect
re-read can disagree with the plan; refuse, re-plan, or click stale is
unanswered), and it must be specified before P2 starts. P2 remains the
highest-leverage code change after P3 in D1's judgment; only its timing
changes.

D1 verdict change: P2 ADOPT to MODIFY. Sequence after AMEND4 items 2-4
land, with the stale-ref protocol specified first.

### (6) A3/A4/A5 deletions: MODIFY conditional (D1/D2/D3) vs REJECT A4 as stated, BLOCK delete-first ordering (RTD, B3/B4)

A3: AGREE with RTD, no change. D1 already MODIFY: delete only when the
driver demonstrably holds the lock plus cancel plus scope on a live run.
RTD's B4 adds nothing D1 did not already require; D2/D3 say the same.

A5: AGREE with RTD, no change. D1 already MODIFY: persistent-first,
fresh SSH retained as fallback, and D1 explicitly rejected the word
"only". RTD's B4 (keep one-shot SSH as recovery when the broker dies)
is D1's condition in other words. D2's "ADOPT with fallback" and D3's
"only applies to the default path" are the same substance.

A4: AGREE with RTD's substance, KEEP MODIFY rather than REJECT. The
difference is wording, not substance: RTD rejects A4 "as stated", and
ARCH's stated form deletes the server with unbuilt replacements. D1
never adopted ARCH's stated form; D1's MODIFY already conditions
deletion on a driver-owned pill proven live by raw grim. But D1 accepts
two RTD additions that strengthen the condition. First, the intermediate
step: session-level pill (acquire once per task, keep the server),
which kills the 315-349ms per-batch overlay tax without touching
visibility. D1's condition jumped straight to the driver-owned pill and
named no intermediate step. Second, the crash case: the replacement
must prove no stale or missing pill when the driver dies mid-task. D1's
raw-grim proof covered the pill showing, not the driver dying. Both
additions are accepted into D1's A4 condition.

D1 verdict: A3, A4, A5 all stay MODIFY. A4's conditions are
strengthened as above.

### (7) A1: ADOPT staged (D1/D2/D3) vs MODIFY, no existence proof (RTD, B6)

PARTIALLY CONCEDE. D1's staged ADOPT required S2 measured first, but
it did not require a prototype existence proof before treating the
daemon as the destination, and D1's section 3 repeated ARCH's "mostly
assembly" claim. RTD's C2 attack on that claim is valid, and it is
valid against D1's own verified readings: session_driver.py runs
cu.main() in-process per command (D1 V7), code_exec.py is an
in-process program model not a daemon, and dom_act.py still grounds
through image points (D1 V5). "Exists" means a file exists, not that
the composition works. The composition is the work, and it is unproven.
D2/D3's staged ADOPT has the same gap; D1 now sides with RTD on the
gate while keeping D1's staging (S2 measured first) as the order.

D1 verdict change: A1 ADOPT to MODIFY. Staged prototype must prove
snapshot/execute/verify end to end on one live ws2 clone chat before
the daemon becomes the replacement; no deletions until then. RTD's C5
is also accepted as a design requirement for the prototype: the daemon
holding the single Firefox session blocks every other tool for the task
duration, and daemon lifecycle across laptop sleep and reboot, plus
stale-state compounding across actions, must be in the prototype design,
not discovered after adoption.

### (8) AMEND4 triage: D1 vs D3 vs RTD

Positions: D1 (items 1, 2, 5, 6, 7, 8, 12 first; 3-4 deprioritized;
9, 10 after; 11 anytime). D3 (surviving items first; pixel-band work
deprioritized; kill an item at reconciliation if the rewrite deletes
its target). RTD (foundation, continue, B2/B5 fed into round-3; items
1-6 fix the geometry and traversal the rewrite builds on; item 4 must
not be gold-plated).

AGREE with RTD's foundation framing and with D3's surviving-items
framing. All four agree AMEND4 CONTINUES, slower, per the 06:09 TWO
TRACKS rule. D1 PARTIALLY CONCEDES on items 3-4. D1 deprioritized them
because under A8/P5 the pixel band becomes a diagnostic, not a success
criterion. That reasoning is still sound for the band's value, but RTD
shows two reasons 3-4 cannot be deprioritized the way D1 wrote it.
First, item 4 is the collision surface P2 must wait for (X3), so items
2-4 are the P2 precondition, and P2's timing depends on them landing.
Second, RTD's point that A9 depends on items 5-6 (origin staleness)
is right, and D1's order already puts 5, 6 first, so that part is
consistent. D1 also accepts D3's kill rule, which D1's section 7 did
not state explicitly, and RTD's per-item patch vs remove vs redesign
recording plus feeding B2/B5 into the round-3 council.

D1 verdict: AMEND4 stays CONTINUE, slower. Triage revised: first
1, 2, 5, 6, 7, 8, 12 (unchanged); then 3, 4 as the P2 precondition,
landed but not gold-plated (RTD's wording); then 9, 10; 11 anytime.
Items 3-4 are no longer "deprioritized" in D1's order; they are
sequenced second, as a precondition, with a cap on polish.

### (9) S3: conditional adopt (D1) vs merge into A1 (D2/D3) vs merge with A1, define plateau numerically first (RTD)

AGREE with all three. There is no real disagreement on the merge: D1's
own S3 row already says "This is A1's Layer 0 daemon in task-runner
form; the two proposals converge on the same destination", and D2/D3
say the same. D1 accepts RTD's one addition: define the plateau
numerically BEFORE S2 starts (threshold, number of runs, decision
owner), so the trigger is not argued later. D1's row had only "a
measured plateau above target", which RTD correctly calls empty in
content: it will either never trigger or trigger on one bad run.

D1 verdict: S3 stays conditional adopt, merged into A1, with the
numerical plateau definition added as a precondition to be set before
the S2 flip, owned by the coordinator.

## 3. Other disagreements I found

- S1: D1 ADOPT, D2 ADOPT, D3 ADOPT (first slice of A1), RTD MODIFY and
  BLOCK the deletion half. D1 SIDES WITH RTD. Verified by me (X2):
  zero references to session_remote or Broker in first_action.py or
  cu.py, so the broker path from the VM is unproven end to end, and the
  single-owner socket semantics under concurrent VM workers are
  unexamined. D1's ADOPT treated "relay alive" as "path proven"; that
  inference is wrong. Verdict change: S1 ADOPT to MODIFY. Prove one
  live batch end to end over the broker from the VM first, then delete
  the per-batch spawn. D1's SPEED deletion 3 row already said "delete
  only after S1 is live", so that row is unchanged and now consistent.
  D2/D3's ADOPT is now the outlier on S1.
- SPEED deletion 5 (per-action model call as default): D1 ADOPT, D2
  ADOPT merged into S2, D3 ADOPT merged into S2, RTD MODIFY and BLOCK
  the blanket flip (same gating as S2). D1 SIDES WITH RTD, for the same
  B2 reason as S2. Verdict change: deletion 5 ADOPT to MODIFY. Code-exec
  becomes the default for the proven task class first, expands on
  measurement.
- P7: D1 ADOPT, D2 ADOPT as a design doc, D3 ADOPT, RTD MODIFY and
  possibly dissolve (Marionette-only may suffice; a handover costs
  4-7s per switch, comparable to the SSH tax being deleted). D1
  PARTIALLY CONCEDES. D1's ADOPT was a low-cost doc written before the
  first live task needs both protocols. RTD's prior question is valid
  and cheap: the benchmark already runs Marionette-only (harvest plus
  input), and zen_dom harvest IS Marionette. Verdict change: P7 ADOPT
  to MODIFY. First answer whether Marionette-only suffices; write the
  handover protocol only if a task genuinely needs two protocols.
- A8: D1 ADOPT, D2 ADOPT merged with P5, D3 ADOPT, RTD MODIFY sequenced
  behind P5 (the assert set must exist first; the V11 observer is an
  open TODO and type_check/focus_check are still optional hooks).
  D1 AGREES in substance, verdict STANDS, condition added: delete
  band-as-pass-signal only where the per-action DOM assert exists and
  is mandatory; where it does not, the band stays as a diagnostic, which
  is what D1's row already said. The disagreement is thin: D1's A8
  assumed the DOM check exists for structured targets, RTD names the
  cases where it does not yet.
- P5: D1 MODIFY (scoped to batches with a DOM session), D2 ADOPT merged
  with A8, D3 ADOPT, RTD MODIFY and BLOCK the blanket mandate (assert
  set incomplete per action type, plus an explicit exception list for
  scroll position and hover state where DOM assert is impossible).
  D1 AGREES with RTD over D2/D3. D1's scoping already blocks the
  blanket version; RTD's per-action-type condition and exception list
  are accepted as additions. Verdict stays MODIFY, conditions extended.
- A2: D1 ADOPT, D2 ADOPT, D3 ADOPT, RTD ADOPT with a sequencing
  constraint (demote only after the router P1 and its fallback trigger
  are proven; Zen chrome UI stays pixel-primary until P8 proves a
  structured path). D1 AGREES, verdict STANDS, constraint added.
- A9: D1 ADOPT, D2 ADOPT, D3 ADOPT, RTD ADOPT with two caveats (needs a
  correct absolute viewport origin re-read per ground; depends on
  AMEND4 items 5-6). D1 AGREES, verdict STANDS, dependency added: A9
  depends on AMEND4 items 5-6 landing.
- SPEED deletion 6: D1 ADOPT for the DOM path, D2 ADOPT for DOM only,
  D3 MODIFY scoped, RTD ADOPT for DOM with a correction (keep the
  future-clock refusal at cu.py:773; a blanket delete removes the
  clock-skew guard). D1 AGREES, verdict STANDS, correction added: keep
  the future-clock refusal, drop only the age refusal for DOM paths.
- P3: all four ADOPT as a controlled experiment. D1 accepts RTD's two
  additions with no verdict change: the CDP security consideration
  (port 9223 exposes the logged-in browser to any local process, never
  mentioned by GROUNDING), and the fallback correction (moving clone
  chats to agent-managed Chromium is a migration with re-login and
  clone reconfiguration, not a fallback).
- A7/P4 scope-rule deletion timing: D1 merged the refusal deletion into
  the A7 fix; D2 ADOPT merged; D3 MODIFY (delete the cu.py:1648 scope
  refusal only as part of P2, because while actions are still
  pixel-addressed the refusal protects typing against a screen
  observation); RTD ADOPT the shape, defer execution to AMEND4 item 12.
  D1 SIDES WITH D3 on the timing. The both-fields fix itself proceeds
  via AMEND4 item 12 (all four agree); the scope-as-capability refusal
  deletion is sequenced with P2, not with the fix. The A7/P4 row stays
  ADOPT for the fix shape, with the refusal deletion moved to the P2
  step.
- A6: D1 ADOPT for transport with files kept as audit, D2 ADOPT same,
  D3 ADOPT, RTD MODIFY (keep persisted observation artifacts; the JPEG
  still travels for the human check). No material disagreement: D1's row
  already says files stay as the audit and evidence trail. Verdict
  STANDS.
- RTD's cross-cutting attacks: C1 (agreement is not independent
  confirmation; all three reviews read the same evidence base, so a
  claim in all three still rests on one measurement) is accepted and
  applies to D1 too. C2 (composition unproven) is accepted, see A1.
  C4 (the unmeasured model call dominates everything; every speed
  projection is conditional on an unmeasured number) is accepted and
  strengthens D1's own S2 honest limit. No verdict changes from C1/C4
  alone; they bound what D1's speed claims can promise.
- D2's open questions, answered from D1's revised position: A3/A4
  replacement does not exist anywhere D1 read (RTD confirms); the live
  loop runs on S0 plus P3 plus A7 plus the gated S2 while the daemon
  prototypes, so nothing is left without a loop; S0 soak is advisory
  (section 2.1); the P3 quiet window is owned by the coordinator with
  rollback to relaunch without the flag; CODEX-BREAKTHROUGH stays
  PENDING in all four logs and gets its own verdict round when it lands.

## 4. Updated D1 verdict table (changes marked)

26 rows. ADOPT 14, MODIFY 12, REJECT 0. Changes from D1's original
table: A1, A10, S1, S2, P2, P7, deletion 5 move ADOPT to MODIFY (7
changes). A8, P5, A2, A9, deletion 6, P3, A7/P4 keep their verdict with
conditions added or moved (section 3). A3, A4, A5 keep MODIFY, with A4
conditions strengthened.

- A1 Layer 0 driver daemon: MODIFY (was ADOPT). Staged prototype must
  prove snapshot/execute/verify end to end on one live ws2 clone chat
  before it becomes the replacement; no deletions until then. Prototype
  design must cover the single-runner lock as a task lock, pill
  visibility, the one-session-per-browser constraint, daemon crash and
  stale-state behavior, and lifecycle across sleep and reboot.
- A2 Pixels fallback-only: ADOPT, with RTD's sequencing constraint
  (demote only after P1 and its fallback trigger are proven; Zen chrome
  stays pixel-primary until P8).
- A3 Delete supervisor tree: MODIFY, unchanged. Delete only when the
  driver demonstrably holds lock plus cancel plus scope on a live run.
- A4 Delete overlay server: MODIFY, conditions strengthened. Session-level
  pill first (acquire once per task, keep the server); driver-owned pill
  only with proof it shows and clears, including no stale or missing
  pill when the driver dies mid-task.
- A5 Delete one-shot SSH: MODIFY, unchanged. Persistent-first, fresh SSH
  retained as fallback and recovery path. "Only" still rejected.
- A6 Delete file IPC: ADOPT for transport, unchanged. Files stay as the
  audit trail; JSON moves to the persistent channel.
- A7/P4 after-image fix: ADOPT for the fix shape, unchanged. Both-fields
  shape (after scope-matching chainable, after_screen verification only),
  regression test, via AMEND4 item 12. The scope-as-capability refusal
  deletion moves to the P2 step (D3's timing).
- A8 Delete pixel-band verification for structured targets: ADOPT,
  condition added. Delete band-as-pass-signal only where the per-action
  DOM assert exists and is mandatory.
- A9 One coordinate system: ADOPT, dependency added. Depends on AMEND4
  items 5-6 (origin staleness) landing.
- A10 0-vision live benchmark: MODIFY (was ADOPT). Ladder: fixture
  2-vision, live 2-vision at 90 percent or better DOM-scored accuracy,
  then 0-vision. One final screenshot stays as human evidence (P9).
- P1 DOM/a11y router: ADOPT, unchanged. Encode in code, log every
  routing decision, fail closed to the labeled screenshot fallback.
- P2 Element-ref interface: MODIFY (was ADOPT). After AMEND4 items 2-4
  land, stale-ref protocol specified first.
- P3 Brave relaunch experiment: ADOPT, conditions added. Quiet window,
  verify login intact plus /json/list plus one fill and assert on a
  scratch input; CDP port exposure noted; Chromium fallback named as a
  migration, not a fallback.
- P5 DOM verification mandatory: MODIFY, conditions extended. Mandatory
  per action type as its assert lands; explicit exception list where DOM
  assert is impossible; band stays diagnostic.
- P6 Measure the vision call: ADOPT, unchanged. Bundle with S0.
- P7 Session handover protocol: MODIFY (was ADOPT). First answer
  whether Marionette-only suffices; write the protocol only if a task
  genuinely needs two protocols.
- P8 Zen chrome context test: ADOPT, unchanged. Bounded probe, low
  priority, quiet window with owner-approved Zen restart.
- P9 Keep one screenshot for the human: ADOPT, unchanged.
- S0 Persistent SSH multiplexing: ADOPT, corrected numbers (section
  2.1). About 3.5-5x per connect, act-now about 16s to about 5-6s.
  Soak test advisory, run in parallel.
- S1 Act-now over broker: MODIFY (was ADOPT). Prove one live batch end
  to end over the broker from the VM first, then delete the per-batch
  spawn.
- S2 DOM-first plus code-exec: MODIFY (was ADOPT). Fixture bench run,
  fix the 3 Y1b real fails, flip for one task class with act-now
  fallback, measure, then expand.
- S3 Laptop-side task runner: conditional ADOPT merged into A1,
  precondition added. Numerical plateau definition (threshold, run
  count, decision owner) set before the S2 flip.
- Deletion 2 (scp for JSON): ADOPT, unchanged.
- Deletion 3 (per-batch session spawn): MODIFY, unchanged. Delete only
  after S1 is proven live.
- Deletion 5 (per-action model call as default): MODIFY (was ADOPT).
  Same gating as S2: proven task class first, expand on measurement.
- Deletion 6 (120s window on DOM work): ADOPT for the DOM path,
  correction added. Keep the future-clock refusal at cu.py:773.

CODEX-BREAKTHROUGH: PENDING in all four logs. No report landed. I
invent none of its proposals. Full verdict round when it lands.

## 5. Revised D1 order of work (replaces D1 section 5)

0. S0 plus P6 now. Corrected numbers, explicit fallback, soak advisory
   and running in parallel.
1. P3 Brave relaunch experiment plus P8 Zen chrome probe, in a quiet
   window. These decide the shape of the live path.
2. A7/P4 after-image fix via AMEND4 item 12 (both-fields shape, regression
   test). Focused fix, unanimous across all reviews plus AMEND4.
3. Run the 2-vision benchmark in fixture mode (it has never run), and fix
   the 3 Y1b real fails on code-exec. The program's gate cannot be an
   unrun script, and the flag flip cannot precede the fixes.
4. S2 flip for ONE live task class (clone chat sends) with act-now as
   fallback. Measure model-call count and wall time.
5. P1 router plus P5 asserts per action type. Rewiring, no collision.
6. P2 element-ref interface, after AMEND4 items 2-4 land and the
   stale-ref protocol is specified. A9 one-system coordinates land in
   this step (depends on AMEND4 items 5-6).
7. S1 broker path proof from the VM on one live batch, then delete the
   per-batch spawn. Session-level pill (keep the overlay server) in the
   same step.
8. A1/S3 merged driver daemon prototype, gated on one live ws2 clone chat
   proof. A3/A4/A5 deletions last, each gated on its replacement proving.
9. Acceptance ladder: fixture 2-vision, live 2-vision, then 0-vision
   (A10 MODIFY).

What changed from D1's original order: steps 3 and 4 are new (fixture
bench run plus Y1b fixes before any flag flip); P2 moves from step 4 to
step 6 (after AMEND4 items 2-4); S1 moves after P2 (it was step 5, now
step 7, and its deletion half is gated on a VM proof); A10 gains the
live 2-vision rung. What did not change: S0 first, P3 early, A7 early,
AMEND4 continues slower in parallel, deletions last.

## 6. What D1 got wrong (record, for the adjudication)

- Missed the Y1b BLOCK (9d9bd63). D1 verified the code-exec gate lines
  but never checked git log for a verdict on the executor, so D1 adopted
  a blanket S2 flip on a known-blocked executor. SPEED omitted it; D1
  should have caught the omission independently.
- Repeated "mostly assembly" for A1 without checking composition.
  session_driver.py runs cu.main() per command and dom_act.py still
  grounds through image points (D1's own verified readings), so the
  composition, not the parts, is the unproven work.
- Tally arithmetic: "ADOPT 20 rows" against 21 listed entries. Corrected
  here: 26 rows, 14 ADOPT, 12 MODIFY, 0 REJECT.
- S0 per-task estimate: D1's 1.3-1.4x stands as the working figure, but
  RTD's recompute requirement is accepted; nobody should quote 1.6x.

## 7. Evidence index

- D1 log: improvements/worker-click3-d1-review-log.md (37f457e).
- D2 log: improvements/worker-click3-d2-review-log.md (6d1bf04).
- D3 log: improvements/worker-click3-d3-review-log.md (14fc139).
- RTD log: improvements/worker-click3-rtd-review-log.md (e96b2ff).
- Spot checks this round: git log 9d9bd63 and 84b88bb (both present);
  grep session_remote/Broker in scripts/first_action.py and scripts/cu.py
  (0 hits each); AMEND4 prompt item 4
  (~/workspace/codex-amend4-prompt.md, line 34); two_vision_bench.py
  docstring on origin/main (BUILD ONLY, VISION 1 DOM harvest, Marionette
  only, live gate --live plus --confirm-live plus plan-URL gate).
- Standing rules honored: no em dash or en dash, no personal info,
  evidence with every claim, wall-clock plus elapsed time, explicit
  pathspec commit, verify push with git ls-remote, never ydotool.
