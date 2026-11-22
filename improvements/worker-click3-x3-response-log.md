# Worker CLICK3-X3: cross-response for the D3 reviewer position

Role: cross-response worker holding the D3 reviewer position. The original D3 reviewer completed and cannot receive follow-ups, so this response speaks from D3's log: improvements/worker-click3-d3-review-log.md, commit 14fc139. Owner: the owner. Repo: ~/workspace/computer-use-wayland, branch todolist-push. Task start: 2026-11-22 06:15:14 +07. All times wall-clock Asia/Ho_Chi_Minh plus elapsed from task start.
Decision criterion (owner standing rule 06:07): judge every proposal by the accuracy and speed of its FINAL RESULT, never by rewrite size or cost. Cost is IRRELEVANT.
Rules honored: no em dash (U+2014) or en dash (U+2013) anywhere in this file; no personal info; evidence with every claim; commit with an explicit pathspec immediately after staging, never plain git commit, never git add -A; verify every push with git ls-remote; never ydotool. This is a review response, not my own work, so no self-healing question arises.

## 0. Bottom line

D3's direction stands. D3's sequencing and gating change in ten places. The pattern of the changes is one-sided: every change moves D3 toward RTD's gates, and none moves D3 toward a faster or less gated version. That is because RTD brought four new facts D3 did not have (Y1b BLOCK, unrun bench, zero Broker references in the live path, AMEND4 items 2-4 collision), and I spot-checked all four and they confirm. D1's independent mux re-measurement corroborates D3's headline correction and kills the 460x figure outright. D2's positions are mostly consistent with D3's, except its "order of hundreds" hedge on 460x, which the two re-measurements supersede.

Verdict-letter changes (D3 original to this response):

| Item | D3 original | X3 response | Nature |
|------|-------------|-------------|--------|
| A1 | ADOPT, staged | MODIFY, prototype gate | Letter change, section 2.7 |
| A5 | ADOPT, fallback kept | MODIFY, persistent default with fallback | Letter only, substance unchanged, section 2.6 |
| A10 | ADOPT, staged behind fixture | MODIFY, ladder | Letter change, section 2.3 |
| S1 | ADOPT | MODIFY, prove one live batch first | Letter change, section 3.1 |
| S2 | ADOPT, gated on bench | MODIFY, bench plus Y1b fixes plus one task class | Letter change, section 2.4 |
| P2 | ADOPT | MODIFY, after AMEND4 items 2-4 plus stale-ref protocol | Letter change, section 2.5 |
| P5 | ADOPT | MODIFY, per action type as its assert lands | Letter change, section 3.3 |
| P7 | ADOPT | MODIFY, Marionette-only question first | Letter change, section 3.4 |
| A8 | ADOPT | MODIFY, behind the assert set | Letter change, section 3.2 |
| SPEED del 3 | ADOPT | MODIFY, same as S1 | Letter change, section 3.1 |
| A4 | MODIFY | MODIFY, strengthened | Sequence gains a session-level pill step, section 2.6 |
| S3 | MODIFY, fold into A1 | MODIFY, fold into A1 plus numerical plateau | Addition, no letter change, section 2.9 |
| AMEND4 | CONTINUE slower, surviving items first | CONTINUE slower, D1 order plus item 4 qualification | Refinement, no direction change, section 2.8 |
| S0 | ADOPT, corrected numbers | ADOPT | No change, section 2.1 |
| A3 | MODIFY | MODIFY | No change, section 2.6 |

No proposal flips from adopt to reject or from reject to adopt. D3 rejected nothing in full originally, and this response still rejects nothing in full. The changes are all gating, sequencing, and labeling.

## 1. What I read and spot-checked

### 1.1 Read in full

- D1: improvements/worker-click3-d1-review-log.md, commit 37f457e.
- D2: improvements/worker-click3-d2-review-log.md, commit 6d1bf04.
- D3: improvements/worker-click3-d3-review-log.md, commit 14fc139 (my own position).
- RTD: improvements/worker-click3-rtd-review-log.md, commit e96b2ff.
- All four commits are present in git log on this branch. HEAD at task start was f4dcfa3.

### 1.2 Spot-checks run in this session (06:16-06:17 +07)

- Y1b BLOCK: `git log -1 --format=%B 9d9bd63` returns the subject "Y1b verdict council 3: OVERALL Phase A BLOCK on 84b88bb (14/20, 3 real fails, 2 probe artifacts)". RTD's B2 factual premise is CONFIRMED from git. D3's log never mentions Y1b; D3 did not have this fact.
- Broker references: `grep -c 'session_remote\|Broker' scripts/first_action.py scripts/cu.py` returns 0 and 0. RTD's S1 premise (the client primitive exists in session_remote.py but nothing in the live path references it) is CONFIRMED. D3's S1 ADOPT treated the relay socket being alive as the live path being ready; that inference was wrong.
- Bench status: `git show origin/main:tests/two_vision_bench.py` docstring line 1 reads "2-vision benchmark script, batch 8 task 1. BUILD ONLY, no live run yet." RTD's B1 premise (the benchmark has never run, even in fixture mode) is CONFIRMED. D3's log called the fixture bench the smoke gate without checking whether it had ever run.
- AMEND4 items 2-4: read ~/workspace/codex-amend4-prompt.md in full. Item 2 is gate traversal (focus_check, hit_check, arm_typed_flag, harvest, sent_bubble_contains through frame plus shadow traversal). Item 3 is band anchoring. Item 4 is wiring type_x_ranges through the CLI act path, CodeExecBackend.act, and BrowserAdapter.act. RTD's B5 collision premise is CONFIRMED: P2's element-ref rewrite touches the same functions item 4 is threading ranges through, and the same check functions item 2 is rewriting. D3's log saw only item 12 of AMEND4 and judged the other 11 by lineage.
- V11 observer: grep finds MutationObserver code in scripts/zen_dom.py line 983 ("const obs=new MutationObserver(function(){") and arm_typed_flag at line 948. RTD's phrasing ("the production V11 MutationObserver flag is an open TODO") is NOT adopted as phrased by D3, because observer code exists in zen_dom.py. D3 did not read enough surrounding code to say whether it is wired into the production code-exec path, so D3 rests its P5/A8 sequencing change on the narrower verified ground instead: focus_check and type_check are still optional hooks (D1 V13, first_action.py lines 597-613 wire DOM hooks only when a selector is given). See section 3.2 and 3.3.

### 1.3 Not re-measured

- Multiplexed SSH: D3's 8 samples stand as D3's measurement; D1's independent 3 samples corroborate them. No new SSH probe was needed.
- DOM bench timings (66 rects, Marionette median 0.030s, 5 clicks, verify 0.002-0.015s): still single-source (clone2 batch 7 via docs/clone2-dom-grounding-20261122.md on origin/main). D3, D1, D2, and RTD all cite the same measurement. See section 3.10 (C1).

## 2. The nine disagreements

### 2.1 SPEED 460x: dead, corrected S0 expectation

Positions. D3: 8 samples, 0.914-1.455s, mean about 1.25s mux vs 4.447s fresh, about 3.5x; saving about 3.2s per connection; per act-now about 16s to about 6s. D1: independent, mux 0.94/1.18/1.29s (n=3, rc=0, master verified alive), real command 0.91s, about 5x; plus the failed-fast trap, a mux call with the master down returned in 0.01s with rc=255. D2: verified only the fresh side (5.06s) and treated 460x as "order of hundreds" until the soak test runs. RTD: incorporated the correction, verified the fresh leg itself at 4.61s, and adopted D1's failed-fast diagnosis.

D3 response: AGREE with D1 and RTD. DISAGREE with D2's hedge. 460x is dead. D1's failed-fast trap is the likely explanation for SPEED's figure: SPEED's log reports 0.01s x3 with no return codes and no master-liveness check, and D1 reproduced exactly 0.01s with rc=255 when the master had not come up. Two independent re-measurements with rc=0 and a verified-alive master (D1 n=3, D3 n=8) against one uninstrumented measurement settle it. D2's "order of hundreds until the soak test runs" is superseded: the soak test answers master survival over hours, not the per-call cost, and the per-call cost is now measured twice over. D2's own log flags its 460x as trusted, not re-measured, so D2's hedge carries no counter-evidence.

Corrected S0 expectation, converged across all four reviewers. Fresh leg: D3 4.447s, RTD 4.61s, D2 5.06s, D1 5.29s, range 4.447-5.29s. Mux leg: D1 0.91-1.29s, D3 0.91-1.46s, range 0.91-1.46s. Saving per connection about 3.2-3.5s, about 3.5-5x, not 460x. Per act-now (3 connects) about 16s to about 5-6s (D1 says about 5s, D3 said about 6s, RTD says 5-6s), not to about 2s. Per observe (2 connects) the saving is about 6-7s. D1's revision of SPEED's 1.6x per-task estimate down to roughly 1.3-1.4x on a CL2-MSG-class task is accepted; D3 did not quote the 1.6x figure, so no D3 number changes on that point. The residual about 1.1-1.2s per call is per-session sshd and shell setup on the laptop, which multiplexing does not remove; D3 already drew this consequence (it strengthens S1 and A1), and RTD agrees. D1's open probe R2 (what exactly costs the 1s: shell startup, PAM, systemd user session setup) is endorsed; it bounds every transport design, including the Broker.

Verdict change: none. S0 stays ADOPT. The magnitude claim was already corrected in D3's log; this response only records that D1 and RTD now agree with the correction and D2's hedge is closed.

### 2.2 Ordering: P1/P5 before S2 held, P2 moved after S2, S2 gated harder

Positions. D1: S0+P6, P3+P8, A7/P4, then S2 switch-on gated on the 2-vision bench, then P1+P2+P5+A9, then S1+A6, then A1/S3, then A3/A4, then A10. D2: S0+P6, item 12, P3, then P1+P2+P5, then S1 then S2 gated on the fixture bench, then staged acceptance, then A1, then A3/A4. D3: S0+P6, P3, then one step bundling S2+P1+P5+P2 (with dependency order inside the step: P1 and P5 rewiring first, P2 interface rewrite second, S2 switch-on last), then S1, then A1 absorbing S3, then A10. RTD: S0, AMEND4 in parallel, P3, fixture bench run, Y1b fixes then S2 flip for one task class, then P1+P5 and P2 after AMEND4 items 2-4, then S1 proof, then A1/S3 decision, then acceptance ladder.

D3 response: SPLIT. Three separate order questions are tangled here, and D3 answers each on its own evidence.

(a) P1/P5 vs S2: D3 HOLDS P1/P5 before S2, disagreeing with D1 and with RTD's numbered order (RTD step 4 flips S2 before step 5 does P1/P5). Reason: S2 is DOM-first plus code-exec plus checkpoint verification, and the checkpoint verification part IS P5. Flipping S2 without P5 means flipping code-exec while DOM verification is still optional hooks (D1 V13, first_action.py:597-613). The rewiring is cheap because the hooks exist; the cost of doing it first is one small step, and the cost of doing it after is a window in which the live loop runs code-exec with pixel-band verification only. D1's order (S2 at step 3, P1/P2/P5 at step 4) and RTD's order both accept that window. D3 does not. Note D3's original bundle already had this dependency inside step 2 ("P1 and P5 are rewiring of existing code, P2 is the interface rewrite, S2 is the switch-on"), so this is a hold, not a change.

(b) P2 vs S2: D3 MOVES P2 to after S2, agreeing with RTD and disagreeing with D2 and with D3's own original bundle. Reason: B5, confirmed by spot-check in section 1.2. P2 rewrites the same functions AMEND4 item 4 is threading type_x_ranges through and item 2 is rewriting for traversal. Running P2 in parallel with items 2-4 guarantees merge collisions on the same functions. D2's order (P1+P2+P5, then S1 then S2) does not address the collision at all. D3's original bundle put P2 before S2 without addressing it either. RTD's sequence (P2 after AMEND4 items 2-4 land, stale-ref protocol specified first) is the correct one. D3 accepts it in full, including the stale-ref protocol precondition: D3's P2 verdict never specified what happens when a live rect re-read disagrees with the plan (refuse, re-plan, or click stale), and RTD is right that this must be specified before P2 starts.

(c) S2 gating: D3 ACCEPTS RTD's harder gate and moves S2 later (see section 2.4). D3's original gate (bench, then live benchmark) is replaced by: fixture bench run, then Y1b 3 real fails fixed, then flip for one task class with fallback. D1's gate (bench only) and D2's gate (fixture bench only) are both insufficient on the Y1b evidence, which neither of them had.

Revised order is given in section 5. Net effect on D3's order: step 2 splits into P1/P5, then fixture bench plus Y1b fixes, then S2 for one task class, then P2. P3 stays early (all four agree). A7/P4 (item 12) stays first among code changes (D1 step 2, D2 step 2, RTD defers to AMEND4; D3 agrees).

### 2.3 A10 acceptance: ladder accepted, final gate unchanged

Positions. D1: ADOPT 0-vision live as final gate, staged behind fixture; 2-vision bench is the interim gate. D2: ADOPT live as final gate, staged fixture first then live. D3: ADOPT, conditional on sequencing; fixture 2-vision is the smoke gate, live 0-vision is the acceptance gate, one final screenshot kept as unscored human evidence (P9). RTD: MODIFY, BLOCK straight-to-0-vision (B1); ladder is fixture 2-vision, live 2-vision, then 0-vision, keeping one final screenshot as human evidence.

D3 response: AGREE with RTD on the ladder, AGREE with D1/D2 on the final gate. D3's verdict changes from ADOPT to MODIFY. RTD's B1 has five limbs, and D3 assesses each:

(1) The 2-vision benchmark is BUILD ONLY and has never run even in fixture mode. CONFIRMED by spot-check (section 1.2). D3, D1, and D2 all treated the bench as built and ready to gate on. None of the three checked whether it had run. This limb alone justifies inserting a fixture rung that must actually pass, not merely exist.
(2) A10 as stated removes the human outcome check, contradicting P9. PARTLY agreed. ARCH's A10 as stated does remove it, but D3's A10 did not: D3's row kept "an optional final screenshot as unscored human evidence (P9)". RTD's ladder step 3 keeps the same screenshot. So on D3's version there is no P9 contradiction; the disagreement is only about the missing middle rung, not about the screenshot.
(3) Depends on untested P3 and an open V11 TODO. AGREED on P3 (all four agree P3 is untested; D3's log says so). On V11, D3 does not adopt RTD's exact wording (see section 1.2: observer code exists in zen_dom.py:983), but the sequencing conclusion stands on the opt-in-hooks ground.
(4) No live accuracy number exists for DOM on real Messenger; 5/5 fixture clicks do not transfer. AGREED. D3's log never claimed a live number; the live 2-vision rung is exactly the measurement that produces one.
(5) ws2 clone chats are live agent workspaces with clone1 mid-batch; a benchmark there disrupts in-flight work. AGREED. D3's log already required a quiet window and clone coordination for the live run; the ladder does not remove that requirement, it adds a fixture pass before the disruption is incurred.

Cost of the added rung under the 06:07 criterion: one extra run, about 0.25s plus one model read for VISION 2. It protects accuracy (DOM can report a bubble present while the rendered thread shows something else, wrong thread or hidden render) for negligible speed. D3 accepts the ladder: fixture 2-vision, live 2-vision, then live 0-vision with the P9 screenshot kept. The final gate stays 0-vision live, as D1, D2, and D3 all held.

Verdict change: A10 ADOPT to MODIFY (ladder). D3's section 4 in the original log ("0-vision live benchmark, not 2-vision") is superseded by the ladder; the fixture 2-vision run is now a rung, not just a smoke gate, and the live 2-vision run is a rung, not skipped.

### 2.4 S2 blanket flip: blocked as stated, D3 concedes to RTD

Positions. D1: ADOPT, gated on the 2-vision bench (bench must be brought onto todolist-push first). D2: ADOPT, gated on the fixture bench pass. D3: ADOPT, gated with the 2-vision benchmark then the live 0-vision benchmark. RTD: MODIFY, BLOCK the blanket flag flip (B2): Y1b council 3 BLOCKED Phase A on 84b88bb with 14/20 probes passing, 3 real fails, 2 probe artifacts (commit 9d9bd63), unmentioned by SPEED, and the named gate (2-vision benchmark) has never run.

D3 response: AGREE with RTD. D3's verdict changes from ADOPT to MODIFY. The Y1b BLOCK is confirmed from git (section 1.2), and it is the single most important fact SPEED omits, exactly as RTD says. D3 did not have it: D3's log took AMEND4 items on trust by lineage and never cited Y1b. D1 and D2 did not have it either; their bench-only gates are insufficient for the same reason D3's was. A bench gate alone does not fix an executor that a council already blocked on 3 real fails. RTD's sequence is adopted in full: run the benchmark in fixture mode, fix the 3 Y1b real fails on code-exec, flip the flag for ONE live task class (clone chat sends) with act-now as fallback, measure, then expand. RTD's honest-limit note is also accepted: the "10x path" label overclaims, since SPEED's own limit puts the end to end at 30-60s on unmeasured model inference, which is 3-5x, not 10x. D3's log already flagged that the 10s target depends on unmeasured model inference time; the S2 flip must not be sold as a 10x win before P6 measures it.

Verdict change: S2 ADOPT to MODIFY (bench green plus Y1b fixes plus one task class with fallback). D3's S2 row in section 4 is updated accordingly. D1/D2's "gated on bench" is not wrong as a gate, it is incomplete as a gate, and D3 now holds the complete gate.

### 2.5 P2 immediate rewrite: blocked as immediate, direction kept

Positions. D1: ADOPT, highest-leverage code change after P3. D2: ADOPT, the central fix. D3: ADOPT, highest-leverage code change with P3. RTD: MODIFY, BLOCK immediate execution (B5): collides with AMEND4 items 2-4 on the same functions, and the stale-ref and mid-plan-mutation protocol is missing.

D3 response: AGREE with RTD on timing, DISAGREE with any reading that B5 kills the direction. D3's verdict changes from ADOPT to MODIFY (sequenced). The collision is confirmed by spot-check (section 1.2): item 4 threads type_x_ranges through the CLI act path, CodeExecBackend.act, and BrowserAdapter.act, which are the paths P2 rewrites, and item 2 rewrites the check functions P2's interface touches. D1, D2, and D3 all adopted P2 without checking AMEND4 item 4's scope; all three missed the collision. RTD is right that running P2 in parallel with items 2-4 guarantees merge collisions and wasted work on the same functions. D3 also accepts the second limb: D3's P2 verdict never specified the stale-ref protocol (live rect re-read disagrees with the plan, then refuse, re-plan, or click stale; refs carry a 90s plus URL staleness guard in cdp.mjs, lifecycle across a multi-action plan unspecified). That protocol must be specified before P2 starts. The direction is untouched: the image-frame round trip is proven wasteful from source (D3 verified dom_act.py 147/159/312 and fastpath.py 195-243; D1 V5 and D2 section 1a agree), and AMEND3 step 2 already deleted the fallback (commit e5c1c47, cited in D3's log). B5 lifts when AMEND4 items 2-4 land and the stale-ref protocol is written; D3 adopts RTD's lift condition verbatim.

Verdict change: P2 ADOPT to MODIFY (after AMEND4 items 2-4, stale-ref protocol first). This also moves P2 after S2 in D3's revised order (see section 2.2b), which disagrees with D2's order (P1+P2+P5, then S1 then S2) on P2 specifically.

### 2.6 A3/A4/A5 deletions: A3 agreed, A4 strengthened, A5 relabeled

Positions. A3: D1 MODIFY (delete only when the driver demonstrably holds lock plus cancel plus scope). D2 MODIFY (same, delete only after replacement passes acceptance). D3 MODIFY (delete only after the driver holds task scope plus cancel file plus driver-owned pill, proven live). RTD MODIFY, BLOCK the delete-first ordering (B4). A4: D1 MODIFY (delete only when a driver-owned pill is proven live by raw grim). D2 MODIFY (same, session-level pill first). D3 MODIFY (delete the server only when a driver-owned pill is proven to show and to clear, including when the driver dies mid-task). RTD REJECT as stated, BLOCK (B3: pill safety-critical, replacements unbuilt, compositor-plugin route is in the hardest area of the repo). A5: D1 MODIFY (persistent-first, fresh SSH retained as fallback; "only" is the rejected word). D2 ADOPT with fallback. D3 ADOPT (keep one-shot SSH as a documented emergency fallback; "only" applies to the default path). RTD MODIFY, BLOCK the "only transport" absolutism (B4).

D3 response: A3, AGREE with RTD and with D1/D2. No material disagreement exists. RTD's B4 restates D3's own condition: the supervisor's real jobs are a named killable scope, cancel/stop, and the session pill label, plus the single-runner lock. Deleting before the driver provides all three removes the cancel/stop path. D3's verdict is unchanged (MODIFY). RTD's added point is accepted: the F1 failure cluster is partly environment faults, not supervisor-design faults, so deleting the tree does not delete those failure modes.

A4, AGREE with RTD on substance, verdict stays MODIFY with a strengthened sequence. RTD's REJECT targets ARCH's proposal as stated (delete the server, replacements unbuilt). D3 never adopted ARCH as stated; D3's MODIFY already gated deletion on the replacement proven, including the driver-death case ("including when the driver dies mid-task" is in D3's A4 row). Where D3 moves: RTD's intermediate step is adopted. Before any driver-owned pill is considered, the session-level pill comes first (acquire once per task, keep the server), which removes the 315-349ms per-batch overlay tax without touching visibility. D2 said the same ("session-level pill first for A4"), and D3's original log noted the session-level pill shape in its S1 row but did not put it into the A4 sequence. The revised A4 sequence is: (a) session-level pill with the server kept, measured; (b) driver-owned pill only with proof that a crash leaves no stale or missing pill; (c) delete the server only then. B3 lifts on (a) measured plus (b) proven, which is RTD's lift condition. D3 disagrees with RTD only on the label applied to D3's own row: D3's conditional MODIFY is not the "as stated" deletion RTD rejects.

A5, AGREE with RTD and D1 on the label; substance was already agreed. D3 called A5 ADOPT with the fallback kept; D1 and RTD call the same substance MODIFY. The difference is labeling, and D3 concedes the label to avoid confusion: the word "only" in ARCH's proposal is rejected, the fallback is not a footnote but a requirement (broker recovery path: if the broker dies, one-shot SSH is how the relay gets restarted). D3's verdict changes from ADOPT to MODIFY in letter only; the substance (persistent default, one-shot SSH kept as documented fallback and recovery path) is unchanged from D3's original row.

Verdict changes: A3 none, A4 strengthened within MODIFY, A5 ADOPT to MODIFY (letter only).

### 2.7 A1: no existence proof, D3 concedes to RTD

Positions. D1: ADOPT, staged; built AFTER S2 is measured, not as a day-1 big bang; holds the single-runner lock as a task lock, owns pill visibility, respects the one-session constraint. D2: ADOPT, staged; stage 1 make S2 the live default through existing parts, stage 2 consolidate into the daemon; do not big-bang while live tasks still fail on screenshots. D3: ADOPT; "the parts exist (code_exec, session_driver, Broker, dom_act, cdp.mjs)"; single-runner lock must move into the driver as a task lock. RTD: MODIFY, with a block on full replacement (B6); no prototype exists, "mostly assembly" fails C2 (session_driver.py runs cu.main() per command, code_exec.py is not a daemon, dom_act.py still grounds through image points); new failure surface undesigned (daemon crash kills all tasks, stale state compounds silently, daemon holding the single Firefox session blocks every other tool for the task duration, lifecycle across sleep/reboot unspecified).

D3 response: AGREE with RTD. D3's verdict changes from ADOPT to MODIFY. D3's "the parts exist" overstated readiness in exactly the way RTD's C2 names: "exists" in D3's log meant a file exists, not that the composition works. These parts were never composed into one running loop, and D3 did not verify any composition. RTD's failure-surface list is accepted in full, including the two D3 had not priced: daemon stale state compounding silently across actions where one-shot calls fail fast, and the daemon holding the single Firefox session blocking every other tool for the task duration (C5). D1's and D2's "adopt staged" is close to RTD's MODIFY, and D3 now aligns with RTD's form: the deliverable is a staged prototype that must prove snapshot/execute/verify end to end on one live ws2 clone chat before anything is deleted. B6 lifts on that proof, which is RTD's lift condition. D3 disagrees with RTD on nothing material here; D3's original conditions (task lock in the driver, pill ownership, one-session constraint) survive as prototype requirements, with two additions from RTD: the prototype must specify lock behavior and session-holding scope (C5), and daemon lifecycle across laptop sleep and reboot must be specified.

Verdict change: A1 ADOPT to MODIFY (staged prototype gate). This also answers D2's open question in its section 8: D3's answer to "if the other reviewers say big-bang daemon first, what does the live loop run on" is that none of the four reviewers says big-bang first; D1, D2, and RTD all stage it, and D3 now stages it with RTD's prototype gate.

### 2.8 AMEND4 triage: D1's order adopted, item 4 qualified, B2/B5 fed into round-3

Positions. D1: items 1, 2, 5, 6, 7, 8, 12 first; items 3, 4, 9, 10 after; item 11 doc fix any time; items 3-4 drop in priority because the pixel band becomes a diagnostic. D3: prioritize items that survive any outcome (item 12 and the DOM-verification items); deprioritize pixel-path-only patches, especially pixel-band verification work; kill an item at reconciliation if the adopted rewrite deletes its target. RTD: AMEND4 is the foundation the rewrite builds on; items 1-6 fix the geometry and traversal the rewrite needs; B2 and B5 fed into round-3; narrow redirect only, per item record patch vs redesign, defer any item the rewrite track will replace wholesale (P2 supersedes item 4's wiring if P2 lands first, so item 4 must not be gold-plated). D2: continue slower; items 1-11 are fixes the rewrite also needs; item 1 already landed and is a prerequisite for A9.

D3 response: AGREE with all three, with two refinements that reconcile them. First, D1's explicit order is adopted as the operational form of D3's triage: D3's "surviving items first" and D1's "1, 2, 5, 6, 7, 8, 12 first" name the same set, and D1 is more explicit, so D3 takes D1's list. There is no material disagreement between D1 and D3 here; D1's deprioritization of items 3-4 matches D3's pixel-band deprioritization. Second, RTD's item 4 qualification is accepted and it refines the deprioritization: item 3 (band anchoring) stays deprioritized, because under A8 the pixel band is a diagnostic, not a success criterion, so perfecting its anchoring is low value under any outcome. But item 4 (wiring type_x_ranges through the three paths) is not merely pixel-band work: it is the wiring P2 will replace, so it must be sequenced with the P2 decision, not just deprioritized. D3's revised triage: items 1, 2, 5, 6, 7, 8, 12 first; item 4 minimal, not gold-plated, sequenced with P2 (if P2 lands first, item 4 is re-verified against the new code rather than finished as written); item 3 deprioritized; items 9, 10 after; item 11 doc fix any time. RTD's point that items 1-6 are foundation is agreed: item 1 is already landed and is a prerequisite for A9's one-system conversion, and items 5-6 fix the origin staleness A9 depends on. D2's "items 1-11 are fixes the rewrite also needs" is agreed with the item 4 qualification above. B2 and B5 are fed into the round-3 council, per RTD; D3's original log did not have B2 or B5 to feed, and now does.

Verdict change: none in direction. AMEND4 CONTINUES, slower, per the owner's 06:09 TWO TRACKS rule, which all four reviewers cite. The triage is refined as above.

### 2.9 S3: merge agreed, plateau must be defined numerically first

Positions. D1: conditional adopt; A1's Layer 0 daemon in task-runner form; do not build before S2 is measured; trigger is a measured plateau above target after S2. D2: merge into A1, decide after S2 measured. D3: MODIFY, fold into A1; plateau condition stays; A1 built as the driver, not as a second runner. RTD: MODIFY, correctly gated but undefined; "plateau" has no threshold, no measurement window, and no decision owner, so it will either never trigger or trigger on one bad run; define the plateau criterion numerically BEFORE Step 2 starts; merge S3 with A1.

D3 response: AGREE with RTD and D2. D3's verdict stays MODIFY (fold into A1). RTD's addition is accepted in full: D3's "plateau condition stays" was empty in exactly the way RTD names (no threshold, no window, no owner). The plateau criterion must be defined numerically before the S2 flip starts, for example Step 2 live median wall time above a stated threshold for a stated number of runs after the flag flip, with a named decision owner, so the trigger is not argued later. D1's "conditional adopt" is the same substance under a different label; D3 notes no material disagreement with D1 either, only that D1's condition now needs RTD's numerical form. D2's merge and D3's fold are the same change.

Verdict change: none in letter. The MODIFY gains the numerical plateau definition as a precondition.

## 3. Other disagreements found

### 3.1 S1 and SPEED deletion 3: a build, not a switch

Positions. D1: S1 ADOPT; relay verified alive. D2: S1 ADOPT. D3: S1 ADOPT; relay socket confirmed alive. RTD: MODIFY, BLOCK the deletion half; the client primitive exists in session_remote.py but nothing in first_action.py or cu.py references the Broker, so S1 needs an SSH-tunneled broker client, which is a build; single-owner socket semantics under concurrent VM workers unexamined; overlay 0.35s per batch remains the largest item after S1.

D3 response: AGREE with RTD. D3's verdict changes from ADOPT to MODIFY for S1 and for SPEED deletion 3 (per-batch session spawn). The zero-reference premise is confirmed by spot-check (section 1.2: grep returns 0 hits in both files). D3's original ADOPT rested on the relay socket being alive, which proves the relay exists, not that the VM live path can use it. RTD's sequence is adopted: prove one live batch end to end over the broker from the VM first, then delete the per-batch spawn; keep the spawn as fallback until proven. D1's MODIFY on deletion 3 (delete only after S1 is live) is the same shape and is agreed. RTD's unexamined points are recorded as open: single-owner socket semantics under concurrent VM workers (serialize or refuse), and the overlay 0.35s per batch remaining the largest item after S1, which is why the session-level pill lands in the same step (section 5, step 8).

### 3.2 A8: sequenced behind the assert set

Positions. D1: ADOPT (band stays as diagnostic only). D2: ADOPT, merged with P5. D3: ADOPT (code admits insufficiency; DOM value check is sufficient and 100-1000x cheaper). RTD: MODIFY, sequenced behind P5; deletion before the DOM assert set exists leaves actions with NO verification, which is worse than weak verification.

D3 response: AGREE with RTD. D3's verdict changes from ADOPT to MODIFY. The direction is unchanged (the band is necessary, not sufficient, per cu.py lines 1023-1076, verified by all four), but the timing was wrong: deleting band-as-pass-signal before the per-action DOM assert exists and is mandatory leaves a verification gap. D3's original row assumed the DOM value check already covers every action; it does not cover every action type yet. A8 deletes band-as-pass-signal only when the per-action DOM assert exists and is mandatory; until then the band stays as a diagnostic. D1's ADOPT and D2's ADOPT missed the same sequencing; D3 moves with RTD here. Note on evidence: D3 does not rest this change on RTD's V11 TODO wording (see section 1.2); it rests on the verified opt-in status of focus_check and type_check.

### 3.3 P5: mandatory per action type, not blanket

Positions. D1: MODIFY, scoped; mandatory for any batch with a DOM session, NOT universal (native apps and pixel fallback keep the band as diagnostic). D2: ADOPT, merged with A8. D3: ADOPT (focus_check and type_check become required for any batch with a type action). RTD: MODIFY, BLOCK the blanket mandate; the assert set does not exist for every action type, and the rule needs an explicit per-action exception list (scroll position, hover state) where DOM assert is impossible and pixel is the only signal.

D3 response: AGREE with RTD and D1, DISAGREE with D2's blanket adopt. D3's verdict changes from ADOPT to MODIFY. D3's original row ("required for any batch with a type action") is close to blanket for type batches and does not name the exception list. The corrected rule: DOM verification becomes mandatory per action type as its assert lands; an explicit per-action exception list names the actions where DOM assert is impossible (scroll position, hover state) and pixel stays the only signal; the band stays as a diagnostic until then. D1's scoping (DOM sessions only, not universal) is the same shape and is agreed.

### 3.4 P7: Marionette-only question first

Positions. D1: ADOPT, write it before the first live task needs both protocols. D2: ADOPT as a design doc, do not let it block other work. D3: ADOPT, write the protocol before the first live task needs both. RTD: MODIFY, and possibly dissolve; first answer whether Marionette-only suffices, since the benchmark already runs Marionette-only (harvest plus input) and zen_dom harvest IS Marionette; a handover costs 4-7s per switch (BiDi new 1.51-2.77s fresh, Marionette attach 2.65-4.12s), comparable to the SSH tax being deleted.

D3 response: AGREE with RTD. D3's verdict changes from ADOPT to MODIFY. None of the three council reviewers justified needing two protocols; all three assumed a task will need both. RTD's question is the right first step: answer whether Marionette-only suffices. Write the handover protocol only if a task genuinely needs BiDi for grounding plus Marionette for input. D2's "do not let it block other work" is consistent with this and is agreed.

### 3.5 A2: adopt with RTD's sequencing constraint

Positions. D1, D2, D3: ADOPT. RTD: ADOPT, with a sequencing constraint: demote only after the router (P1) and its fallback trigger are proven; Zen chrome UI stays pixel-primary until P8 proves a structured path, because today pixels are its only perception.

D3 response: AGREE. Verdict stays ADOPT, with the constraint added. D3's original row did not state the router-proven condition; it is now part of the row. Without it, A2 strands Zen chrome tasks.

### 3.6 A6: adopt, audit trail kept

Positions. D1: ADOPT for transport; files stay as the audit and evidence trail. D2: ADOPT for transport, keep files as record. D3: ADOPT; keep file IPC only as the fallback transport when no Broker is reachable. RTD: MODIFY; replace JSON file transfer with same-channel transfer, keep persisted observation artifacts (JSON plus JPEG) written by the driver as the audit trail; the JPEG still travels for the human VISION 2 check.

D3 response: AGREE with RTD, D1, and D2 on the substance. Verdict stays ADOPT. D3's original row already kept file IPC as fallback transport; RTD's audit-trail condition is added explicitly: persisted observation artifacts stay as the audit trail the no-self-healing rule depends on for independent investigation, and the JPEG still travels for the human check until S1's channel carries bytes. The difference between D3's ADOPT and RTD's MODIFY is labeling of the same change (JSON transfer moves, artifacts stay); D3 keeps ADOPT because the row already carried the fallback condition and now carries the audit condition too.

### 3.7 A7: no disagreement in substance

Positions. D1, D2, D3: ADOPT, both-fields shape (after scope-matching and chainable, after_screen verification only, documented non-chainable), merged with P4 and SPEED deletion 4. RTD: ADOPT the demote half, MODIFY the delete half; implement P4's shape, do not delete the after image entirely.

D3 response: AGREE with RTD. Verdict stays ADOPT. RTD's MODIFY targets ARCH's delete half ("delete act-now after image as chainable observation"); D3's row already IS the both-fields shape, not the deletion. There is no disagreement between D3's row and RTD's row. Deleting the after image entirely would lose the human-visible evidence and the frame-change signal for a saving of about 0.25s, which is noise; D3 agrees. AMEND4 item 12 owns the implementation; the rewrite track consumes it (all four agree).

### 3.8 A9, P1, P3, P6, P9, D6: adopt with RTD's additions

A9: all four ADOPT for structured targets. RTD adds two caveats, both accepted: the one conversion still needs a correct absolute viewport origin and scale factors re-read per ground (C12 proved window-relative vs absolute origin is a live trap, absolute origin (2749, 922)), and A9 depends on AMEND4 items 5-6 landing, since those fix origin staleness. Verdict stays ADOPT with the dependency added.

P1: D1, D2, D3 ADOPT. RTD ADOPTS as design, MODIFY to require fail-closed behavior with a per-target routing table proven per target, a defined fallback, and a log line on every routing decision. D3's row already required fail-closed to the screenshot fallback with the fallback labeled. RTD's per-target table and log line are added. Verdict stays ADOPT. RTD's note that the a11y branch is thin (AT-SPI cannot see Zen) is accepted; the a11y branch mostly covers native apps that are not the live workload.

P3: all four ADOPT as a controlled experiment. RTD's attacks are accepted as experiment-design requirements: the window must be a real quiet window owned by the coordinator, never mid-batch; the "login persists" claim is the thing to prove; CDP on port 9223 exposes the logged-in browser to any local process, a security consideration none of the three council reviews mentioned; the fallback (move clone chats to agent-managed Chromium) is a migration with re-login and clone reconfiguration, not a fallback, and needs its own login-persistence check (D1 R3 says the same). Verdict stays ADOPT. BLOCK on any live-task migration until the experiment passes with login intact plus one fill plus assert on a scratch input, per RTD.

P6: all four ADOPT. RTD's specification fix is accepted: the model call happens in the calling agent's loop, outside cu.py, so the proposal must specify the timestamp points (observation delivered to the agent vs located target returned) and the owner of the logging (the harness, not cu.py), or it will be recorded as done when only capture timing is logged again. Verdict stays ADOPT with the spec added. D3's original row already said P6 must land before anyone claims the 10s target; that stands.

P9: all four ADOPT. RTD's wording correction is accepted: VISION 2 is the agent looking at the threads and reporting to the human, not the owner looking directly, so it is the agent's final sanity check reported to the human. Substance unchanged. Verdict stays ADOPT.

D6 (120s freshness window): D1 ADOPT for the DOM path, D2 ADOPT for the DOM path only, D3 MODIFY scoped (keep the window for pixel work). RTD ADOPTS for DOM work with a correction: the refusal at cu.py:773 also guards against future-clock observations, and a blanket delete removes the clock-skew guard. D3 accepts the correction: keep the future-clock refusal, drop only the age refusal for DOM paths. Verdict stays MODIFY (scoped).

### 3.9 SPEED deletions D1, D2, D4, D5

D1 (fresh SSH per call): all four ADOPT (merged with S0/A5). No disagreement. D2 (scp for JSON): all four ADOPT for JSON transfer, with the A6 audit caveat (section 3.6). No disagreement. D4 (screen-scope after-capture): all four ADOPT the shape, DEFER to AMEND4 item 12. No disagreement. D5 (per-action model call as default): D1 ADOPT, D2 ADOPT merged with S2, D3 ADOPT merged with S2. RTD MODIFY, BLOCK the blanket flip, same as S2 (depends on S2's gating: Y1b fails plus unrun benchmark). D3 AGREES with RTD: D5 changes to MODIFY with S2 (code-exec becomes the default for the proven task class first, expand on measurement). This follows from section 2.4; it is not a separate disagreement.

### 3.10 C1, C4, C5: RTD's cross-cutting attacks

C1 (agreement is not independent confirmation): AGREED. ARCH, GROUNDING, and SPEED all read the same failure record (E2, G30/G31, F2b, clone2 batch 7) and reach the same direction. That is one evidence base read three times, not three independent measurements. D3's log cited the DOM bench numbers as verified in source (the docs file exists and states them) but did not re-run them; neither did D1, D2, or RTD. D3's verdicts rest on structural code verification, which D3 did independently (cu.py, first_action.py, fastpath.py, dom_act.py line refs in D3 section 1.1), plus the single DOM bench measurement. The DOM timing claims stay single-source until re-run. No verdict changes on C1 alone; it lowers the confidence D3 claims for the timing-dependent rows (P2, S2, A1) and is one reason the prototype and bench gates in this response are load-bearing.

C4 (the unmeasured model call dominates everything): AGREED. D3's log section 6 already flagged it: "The 10s target for a tc02-class task depends on model inference time, which nobody in this round measured. P6 must land before anyone claims the target is met." D1 shares the honest limit (30-60s if vision reading dominates). No verdict change; C4 is the reason S2's "10x path" label is corrected to 3-5x in section 2.4.

C5 (single-runner lock and one-session constraint unexamined): AGREED. D3's A1 condition said the lock moves into the driver as a task lock but never specified lock behavior or session-holding scope, and never priced the lock-in risk (a daemon holding the single Firefox session blocks every other tool for the task duration). Added to the A1 prototype requirements in section 2.7. No separate verdict change.

### 3.11 D2's "order of hundreds" and D1's R2

D2's 460x hedge is addressed in section 2.1 (disagreed, superseded). D1's R2 (the per-connection laptop-side cost of about 1s even over the master is unexplained; worth one probe) is AGREED and recorded as an open probe; D3's log offered the same explanation (per-session sshd and shell setup) without proving it. D1's R3 (P3 fallback needs its own login-persistence check) is agreed and folded into section 3.8. D1's R4 (live benchmark traffic needs agreed threads and owner approval per run) is agreed; D3's log already required owner approval per run with the bench's --live --confirm-live gates. D2's open questions in its section 8 (A3/A4 replacement, A1 staging, S0 soak ownership, P3 window ownership, CODEX-BREAKTHROUGH round) are answered by this response where they overlap D3's rows: A3/A4 in section 2.6, A1 in section 2.7, S0 soak in section 2.1 (advisory, runs in parallel, fallback makes it non-blocking), P3 window in section 3.8 (coordinator owns the window). CODEX-BREAKTHROUGH stays PENDING in all four reviews; RTD's caution is accepted (section 3.12).

### 3.12 CODEX-BREAKTHROUGH: still pending, arrival is not a tie-breaker

Positions. D1, D2, D3, RTD: PENDING. Only a launch log exists (Codex PID 781223 launched 06:04 on the laptop). RTD adds: do not treat its arrival as a tie-breaker by default, because a fourth reading of the same evidence base is still the same evidence base (C1).

D3 response: AGREE. Verdict stays PENDING. D3's log already said the cross-response round and the joint adjudication must leave room to integrate its proposals when they land and must not treat this review as complete on that axis. RTD's caution is added: when the report lands it gets a full verdict round against the same criterion, judged also against this response's blocking findings, especially whether it independently re-measures anything or cites clone2, F2b, and E2 second-hand.

## 4. Updated D3 verdict table

Legend: ADOPT means do it as proposed. MODIFY means do it with the stated change. REJECT means do not do it. PENDING means the input has not landed. Rows marked CHANGED differ from D3's original table (commit 14fc139); rows marked STRENGTHENED keep their letter with an added condition.

### 4.1 ARCH

| ID | Proposal | Verdict | Evidence and reasoning |
|----|----------|---------|------------------------|
| A1 | Layer 0 persistent driver daemon | MODIFY, CHANGED from ADOPT | Direction right; composition unproven (RTD C2, B6). Staged prototype must prove snapshot/execute/verify end to end on one live ws2 clone chat before anything is deleted. Prototype must specify lock behavior, session-holding scope (C5), and lifecycle across sleep/reboot. |
| A2 | Layer 1 pixels demoted to fallback-only | ADOPT, STRENGTHENED | Demote only after the router (P1) and its fallback trigger are proven; Zen chrome UI stays pixel-primary until P8 proves a structured path (RTD constraint, agreed). |
| A3 | Delete session supervisor tree | MODIFY | Unchanged. Delete only after the driver holds task scope plus cancel file plus driver-owned pill and they are proven live. RTD B4 restates this condition. |
| A4 | Delete overlay daemon server | MODIFY, STRENGTHENED | Unchanged in letter. Sequence now: (a) session-level pill with the server kept, measured; (b) driver-owned pill only with proof no stale or missing pill on crash; (c) delete the server only then. RTD B3 substance agreed; RTD REJECT targets ARCH as stated, not this conditional row. |
| A5 | Delete one-shot SSH loop | MODIFY, CHANGED from ADOPT | Letter only. Persistent default, one-shot SSH kept as documented fallback and recovery path (broker restart). "Only" is rejected as a word, per D1 and RTD B4. |
| A6 | Delete file-based observation/action IPC | ADOPT, STRENGTHENED | JSON transfer moves to the same channel; persisted observation artifacts (JSON plus JPEG) stay as the audit trail; JPEG still travels for the human VISION 2 check. |
| A7 | Delete act-now after image as chainable observation | ADOPT | Unchanged. Both-fields shape (after scope-matching and chainable, after_screen verification only). This IS P4's shape; RTD's MODIFY targets ARCH's delete half, not this row. AMEND4 item 12 owns it. |
| A8 | Delete pixel-band verification for structured targets | MODIFY, CHANGED from ADOPT | Delete band-as-pass-signal only when the per-action DOM assert exists and is mandatory; until then the band stays as a diagnostic. RTD sequencing agreed. |
| A9 | Coordinate model to one system | ADOPT, STRENGTHENED | For structured targets. Depends on AMEND4 items 5-6 landing (origin staleness); pixel fallback keeps its own frame internally. |
| A10 | Acceptance test becomes 0-vision live benchmark | MODIFY, CHANGED from ADOPT | Ladder: fixture 2-vision, live 2-vision, then live 0-vision with the P9 screenshot kept. Final gate stays 0-vision live. RTD B1 agreed. |

### 4.2 GROUNDING P1-P9

| ID | Proposal | Verdict | Evidence and reasoning |
|----|----------|---------|------------------------|
| P1 | DOM/a11y default router | ADOPT, STRENGTHENED | Encode in code; fail closed to the screenshot fallback with the fallback labeled; per-target routing table proven per target; log line on every routing decision (RTD additions agreed). |
| P2 | Element-ref action interface rewrite | MODIFY, CHANGED from ADOPT | Direction right, round trip proven wasteful from source. Sequence AFTER AMEND4 items 2-4 land, stale-ref protocol specified first. RTD B5 agreed. |
| P3 | Brave relaunch with debugging port | ADOPT, STRENGTHENED | Controlled experiment, quiet window, never mid-batch; verify /json/list shows the tab and login intact, one fill plus assert on a scratch input. Added: CDP port 9223 local-exposure note; fallback is a migration, needs its own login-persistence check; no live-task migration until it passes. |
| P4 | After-image scope fix | ADOPT with MODIFY | Unchanged. Both-fields fix plus regression test (merged with A7). Scope-rule deletion only as part of P2. Execution deferred to AMEND4 item 12. |
| P5 | DOM verification mandatory | MODIFY, CHANGED from ADOPT | Mandatory per action type as its assert lands; explicit per-action exception list (scroll position, hover state) where DOM assert is impossible; band stays diagnostic until then. RTD and D1 scoping agreed. |
| P6 | Measure the vision call | ADOPT, STRENGTHENED | Log vision-call latency in the harness. Added spec: timestamp points are observation delivered vs located target returned; owner of logging is the harness, not cu.py (RTD fix agreed). |
| P7 | Session handover protocol | MODIFY, CHANGED from ADOPT | Answer whether Marionette-only suffices first; write the protocol only if a task genuinely needs BiDi plus Marionette. RTD agreed. |
| P8 | Zen chrome Marionette context test | ADOPT | Unchanged. Bounded probe, low priority; if blocked without a restart, keep screenshots ONLY for chrome UI and record the boundary. |
| P9 | Keep one screenshot for the human | ADOPT | Unchanged. VISION 2 stays as unscored human evidence; wording corrected per RTD (agent's final sanity check reported to the human). |

### 4.3 SPEED S0-S3 plus six deletions

| ID | Proposal | Verdict | Evidence and reasoning |
|----|----------|---------|------------------------|
| S0 | Step 0 persistent SSH multiplexing | ADOPT | Unchanged. Corrected numbers: mux 0.91-1.46s vs fresh 4.447-5.29s, about 3.5-5x, saving about 3.2-3.5s per connection; per act-now about 16s to about 5-6s. 460x dead (D1 corroboration plus failed-fast trap). Soak test runs in parallel, advisory, fallback explicit; watchdog per-socket, not global. |
| S1 | Step 1 act-now over persistent relay broker | MODIFY, CHANGED from ADOPT | Prove one live batch end to end over the broker from the VM first, then delete the per-batch spawn; keep the spawn as fallback until proven. Zero Broker references in first_action.py and cu.py confirmed by grep (section 1.2). |
| S2 | Step 2 DOM-first plus code-exec plus checkpoint verification | MODIFY, CHANGED from ADOPT | Fixture bench green, plus 3 Y1b real fails fixed, plus flip for ONE live task class with act-now fallback, then measure and expand. RTD B2 agreed; Y1b BLOCK confirmed (commit 9d9bd63). "10x path" corrected to 3-5x on unmeasured inference. |
| S3 | Step 3 laptop-side task runner | MODIFY, STRENGTHENED | Fold into A1, do not build a separate runner. Plateau criterion defined numerically BEFORE the S2 flip starts (threshold, run count, decision owner). RTD addition agreed. |
| D1 | Delete fresh SSH per call | ADOPT | Unchanged, merged with A5/S0. |
| D2 | Delete scp for JSON files | ADOPT | Unchanged, merged with A6; audit caveat in section 3.6. |
| D3 | Delete per-batch session spawn | MODIFY, CHANGED from ADOPT | Same as S1: delete only after the broker path proves on the VM path. |
| D4 | Delete screen-scope after-capture | ADOPT | Unchanged, merged with A7/P4; deferred to AMEND4 item 12. |
| D5 | Delete per-action model call as default | MODIFY, CHANGED from ADOPT | Same as S2: code-exec becomes the default for the proven task class first, expand on measurement. |
| D6 | Delete 120s freshness window as gate on DOM work | MODIFY | Unchanged in letter. Scoped deletion for DOM work; keep the window for pixel work; keep the future-clock refusal at cu.py:773 (RTD correction agreed). |

### 4.4 CODEX-BREAKTHROUGH

| ID | Proposal | Verdict | Evidence and reasoning |
|----|----------|---------|------------------------|
| CB | All proposals | PENDING | Unchanged. Report not landed. Arrival is not a tie-breaker by default (RTD C1 caution agreed). |

Verdict count in this response: ADOPT 14 rows (A2, A6, A7, A9, P1, P3, P4, P6, P8, P9, S0, D1, D2, D4), MODIFY 15 rows (A1, A3, A4, A5, A8, A10, P2, P5, P7, S1, S2, S3, D3, D5, D6), REJECT 0, PENDING 1 track (CODEX-BREAKTHROUGH). Total 30 rows counted.

## 5. Revised order of work

This replaces D3's section 3 order. It adopts RTD's numbered order with two D3 holds (P1/P5 before S2, and the P8 probe alongside P3) and D3's A7/P4-first placement.

0. S0 plus P6, now. Both cheap, both reversible; P6 makes every later speed claim honest. S0 with explicit fallback, master-death logging, per-socket watchdog, and the 1-day soak test running in parallel (advisory, not a gate). Plateau criterion for S3/A1 defined numerically before step 6 starts.
1. AMEND4 continues in parallel, slower, per the owner's 06:09 TWO TRACKS rule. Item 12 (A7/P4) lands via the in-flight run; verify the regression test. No parallel edits to the same functions from the rewrite track (see section 6).
2. P3 Brave relaunch experiment plus P8 Zen chrome test, in a real quiet window between clone batches, coordinator-owned. P3 first: it unlocks every live task. No live-task migration until P3 passes with login intact plus one fill plus assert on a scratch input.
3. Fixture 2-vision bench run. It has never run at all; the whole program's gate cannot be an unrun script. This run does not depend on P3 (headless Firefox, local fixture) and can run as soon as step 0 lands.
4. Fix the 3 Y1b real fails on code-exec (84b88bb).
5. P1 router plus P5 asserts per action type. Rewiring of existing hooks; this is the D3 hold against D1 and RTD's numbered order, for the reason in section 2.2a (S2's checkpoint verification IS P5).
6. S2 flip for ONE live task class (clone chat sends) with act-now as fallback. Measure. Expand only on measurement.
7. P2 interface rewrite, after AMEND4 items 2-4 land, with the stale-ref protocol specified first.
8. S1 broker path proof from the VM on one live batch, then delete the per-batch spawn. Session-level pill (keep the overlay server) in the same step.
9. A1/S3 merged daemon/runner design decision, only after steps 0-8 are measured. A1 prototype must prove snapshot/execute/verify end to end on one live ws2 clone chat.
10. A3/A4/A5 deletions last, each gated on its replacement proving (A4: session-level pill first, driver-owned pill only with crash proof).
11. Acceptance ladder: fixture 2-vision (step 3), live 2-vision, then live 0-vision with the P9 screenshot kept as human evidence.

What this order buys, unchanged from D3's original claim: every step is independently verifiable, every step lands a measured win before the next step starts, and no step depends on a bet (P3, P8, S2 measurement) that has not yet paid off. What changed: S2 no longer rides on a bench gate alone, P2 no longer rides before AMEND4, and A10 no longer jumps from fixture to live 0-vision.

## 6. AMEND4 triage, revised

CONTINUE, slower, per the owner's 06:09 TWO TRACKS rule. Do not pause, redirect, or stop. D3's original reasons stand (the current loop is the only working loop, item 12 fixes a defect that bites live tasks today, the rewrite is not adjudicated yet). The triage is refined as follows, adopting D1's explicit order and RTD's item 4 qualification:

- First: items 1, 2, 5, 6, 7, 8, 12. Item 1 already landed and is a prerequisite for A9; items 5-6 fix the origin staleness A9 depends on; item 12 IS the A7/P4 fix.
- Item 4: minimal, not gold-plated, sequenced with the P2 decision. If P2 lands first, item 4 is re-verified against the new code rather than finished as written (RTD section 7).
- Item 3: deprioritized. Under A8 the pixel band is a diagnostic, not a success criterion.
- After: items 9, 10. Item 11 (doc fix) can land any time.
- B2 (Y1b fails) and B5 (P2 collision) are fed into the round-3 council, per RTD. The council records per item whether the fix is a patch on a defective design or a real redesign, and defers any item the rewrite track will replace wholesale.
- The two tracks run in sequence per item on shared files, not in parallel on the same functions, or the merge will collide (RTD section 6). The rewrite track's work while AMEND4 runs is S0, the P3 experiment, the fixture benchmark run, the Y1b fail fixes, P6 instrumentation, and P7's Marionette-only question. None of these touch AMEND4's files except P6's harness logging, which stays out of cu.py's hot paths.

## 7. What would change these responses

- The S2 MODIFY reverts toward ADOPT when the 3 Y1b real fails are fixed and the fixture benchmark runs green; then the one-task-class flip is the next step, not a further debate. This is RTD's B2 lift condition, adopted here.
- The P2 MODIFY reverts toward ADOPT when AMEND4 items 2-4 land and the stale-ref protocol is written. This is RTD's B5 lift condition, adopted here.
- The A1 MODIFY reverts toward ADOPT when a daemon prototype runs snapshot/execute/verify end to end on one live ws2 clone chat. This is RTD's B6 lift condition, adopted here.
- The A10 ladder collapses to D3's original two-rung form (fixture, then live 0-vision) only if the live 2-vision run passes at 90 percent or better DOM-scored accuracy AND the P5 assert set is complete; until then the middle rung stays. This is RTD's B1 lift condition, adopted here.
- The A4 MODIFY becomes a deletion only when a session-level pill is measured and a driver-owned pill proves no stale or missing pill on crash. This is RTD's B3 lift condition, adopted here.
- If P3 fails (Brave refuses the debugging port on its default profile and the Chromium migration is too disruptive), the DOM-first live path loses its highest-leverage unlock, and the whole program re-plans around Zen Marionette only. That outcome must be reported plainly, not worked around silently (RTD section 7, agreed).
- If CODEX-BREAKTHROUGH lands with an independent re-measurement that contradicts the DOM bench timings or the mux numbers, the affected rows (P2, S2, A1, S0) are re-judged on the new measurement. A fourth citation of the same numbers changes nothing (C1).

## 8. Log

- 06:15:14 +07 (T+0m): task received. Repo on todolist-push, HEAD f4dcfa3 at start. Branch had moved since D3's commit 14fc139; the four review commits (37f457e, 6d1bf04, 14fc139, e96b2ff) are all present in git log.
- 06:15:25-06:16:30 +07 (T+0-1m): read all four review logs in full (D1, D2, D3, RTD).
- 06:16:57 +07 (T+2m): spot-checks. Y1b commit 9d9bd63 subject confirmed from git. Broker grep 0 hits in first_action.py and cu.py. Bench docstring "BUILD ONLY, no live run yet" confirmed on origin/main.
- 06:17:06 +07 (T+2m): AMEND4 prompt read in full (items 2, 3, 4 scope confirmed); V11 grep (MutationObserver at zen_dom.py:983, arm_typed_flag at :948).
- 06:17-06:25 +07 (T+2-10m): wrote this log. Next: fetch plus rebase first if the branch moved, commit this file only with an explicit pathspec, verify with git ls-remote, report to COORD-CLICK-3.
