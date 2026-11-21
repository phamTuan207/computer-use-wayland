# Worker CLICK3-FRT: final redteam review of the FINAL DECISION round

Owner: Pham Tuan. Role: final redteam reviewer, independent and adversarial.
Repo: ~/workspace/computer-use-wayland, branch todolist-push.
Task start: 2026-11-22 06:37 +07. All times wall-clock Asia/Ho_Chi_Minh + elapsed.
Rules honored: no em dash (U+2014) or en dash (U+2013) anywhere in this file.
No personal info. Evidence with every claim. Commit with an explicit pathspec
immediately after staging, never plain git commit, never git add -A. Verify
every push with git ls-remote. Never ydotool. This is a review, not my own
work, so no self-healing question arises.

Decision criterion (owner standing rule 06:07): the final result must be the
MOST ACCURATE and the FASTEST; cost is IRRELEVANT. This cuts both ways: a
proposal must ALSO prove its accuracy/speed win with evidence, not just
assert it. A proposal with no measured evidence behind it does not count
as feasible (owner 06:34, Lauren Tan standard: every claim carries real
measured numbers, test command, output, commit hash, time log).

## 0. What I read and what I verified myself

### 0.1 Inputs read in full before attacking

- ARCH-REVIEW: improvements/worker-arch-review-log.md (074c1d7).
- GROUNDING-REVIEW: improvements/worker-grounding-review-log.md (d1fc4e9).
- SPEED-REVIEW: improvements/worker-speed-review-log.md (a4ecb49).
- CODEX-BREAKTHROUGH: improvements/codex-breakthrough-report.md (2596287,
  138 lines, Vietnamese).
- Joint adjudication DRAFT: improvements/worker-click3-adjudication-log.md
  (9d23834, 24 rows covering 30 proposals).
- Reviews: D1 (37f457e), D2 (6d1bf04), D3 (14fc139), RTD (e96b2ff).
- Cross-responses: X1 (0cf601c), X2 (d5b205d), X3 (2b0c73c), XRT (6cb3f95).
- Probe logs in tree: worker-probe-s2-log.md (uncommitted),
  worker-probe-p3-log.md (7b1006a), worker-probe-p8-log.md (3790901).

### 0.2 My own spot checks this session (new verification, not trust)

- V-F1. CODEX-BREAKTHROUGH has LANDED: commit 2596287,
  improvements/codex-breakthrough-report.md, 138 lines. The draft's
  PENDING row (V-A1) is overtaken. Its proposals get full verdicts in
  section 1.4 below; they are not rubber-stamped in.
- V-F2. first_action.py IS in the repo on todolist-push at HEAD af0fa87.
  The after-image trap is STILL in the code: line 661 hardcodes
  cu.observe_screen(env, args.screen, max_width=1920) for the envelope
  after-image. AMEND4 item 12 has NOT landed on this branch. Envelope
  ok logic, lines 552-563: envelope ok=True when the session result says
  ok, or when the completed-capture shape holds, with no postcondition
  anywhere in the path. CB-2.1's substance (ok reported on input sent,
  not on target reached) is VERIFIED from source. The comment at line
  550 even cites "Council 1, A3: the exit code alone never proves
  success", then propagates session ok anyway.
- V-F3. Broker wiring gap re-verified this session: grep for
  session_remote|Broker in scripts/first_action.py and scripts/cu.py
  returns 0 and 0. S1 is still a build, not a switch.
- V-F4. Bench files are now ON todolist-push (c5311ce bench, 7f3a70b
  fixture), but PROBE-S2's log (uncommitted, in tree, 06:36-06:38 +07)
  records the bench runtime is ABSENT on this VM: no .venv, no selenium
  in system python3, no Firefox/Chromium binary, no tools dir, while the
  bench hardcodes FF and GD under ~/workspace/tools. The fixture run is
  NOT runnable as written. Same log, 06:36 code-level re-check: the 3
  Y1b real fails are STILL OPEN (chr in neither SAFE_BUILTINS list,
  codemode.py line 37, code_exec.py line 107; no setitimer, SIGALRM, or
  child-process preemption in either executor).
- V-F5. PROBE-P8 LANDED: commit 3790901, Marionette chrome context
  BLOCKED without Zen restart (HTTP 500, MOZ_REMOTE_ALLOW_SYSTEM_ACCESS
  required), C12 reproduced live. P8 is a CLOSED negative, not an open
  probe. PROBE-P3 NOT-RUN: commit 7b1006a, clone1 batch 9 open since
  06:01, Brave untouched. At 06:41 +07 there is NO committed log for
  PROBE-S0, PROBE-S1, or PROBE-DOMZEN in this tree (git log --all
  --grep probe- shows only P3, P8, S2). Their results are not in, and
  their absence is recorded, not assumed.
- V-F6. AMEND4 landed state moved since the draft (draft HEAD 72120aa,
  items 1-4 landed). Now landed: items 5-6 (b44a5ea), item 7 (49081aa),
  item 8 (af0fa87, current HEAD). Items 9, 10, 12 NOT landed on
  todolist-push. Caveat, from the landing commits' own messages:
  62b740e records "F4 RT2 test defective", 72120aa records "F5 behavior
  test defective", b44a5ea records "F2/F3 RT2 tests defective". Landing
  with a defective proof test is not proof-grade landing. Any verdict
  that leans on items 2-6 as proven must carry this caveat until the
  round-3 council repairs or re-verifies those tests.
- V-F7. Arithmetic re-verified by me: 0.9^20 = 12.2%, 0.9^32 = 3.4%
  (CB-4 math correct); Wilson 95% interval for 17/29 is 40.7%-74.5%
  (matches Codex CB-3); Wilson lower bound for 96/100 is about 90.2%
  (matches Codex's 96/100 claim for the 100-task benchmark). Code facts
  re-verified at HEAD af0fa87: 32-action cap at scripts/cu.py:1182 and
  scripts/code_exec.py:187-192; pixel-patch threshold >6 at
  scripts/cu.py:1015 (J37's 6.627 vs 6 is consistent with this code);
  observe default max_width=960 at scripts/cu.py:920/974 vs act-now
  1920 at scripts/first_action.py:353/661 (CB-3 image non-uniformity
  verified); zen_dom unrestricted JS eval capability exists as
  evaluate() at scripts/zen_dom.py:441 (Codex cited older line numbers);
  arm_typed_flag IS called from production code at
  scripts/dom_act.py:483-484 (draft V-A5 cited 433-434, lines moved by
  AMEND4 edits, substance stands); MutationObserver string at
  scripts/zen_dom.py:993.
- V-F8. Codex's first-action JSONL aggregate (199 lines, p50
  order-to-overlay 337.5 ms, max 368.4 ms, p50 wrapper 2.288 s, max
  6.95 s, 167 ok=true, 32 ok=false, 195 session, 4 fallback, 0 timeout,
  5 source=captured) is Codex-reported from the laptop log, NOT
  re-verified by me. I take it as reported. Note what it means: 167
  ok=true with no postcondition data anywhere in the log means the ok
  rate (84%) is NOT a success rate. G30 proves false ok exists in this
  exact population. Nobody may quote 167/199 as a success rate.

## 1. Verdict table (every proposal, none skipped)

Legend: ADOPT means do it as proposed. MODIFY means do it with the stated
change; the gating conditions are what must be proven before it proceeds.
REJECT means do not do it as stated. Exact duplicates are merged into one
row citing every source. Coverage: 34 rows covering all 40 proposals:
ARCH A1-A10 (10 rows), GROUNDING P1-P9 (8 rows, P4 merged into A7),
SPEED S0-S3 plus six deletions (5 rows, D1 into S0, D2 into A6, D3 into
S1, D4 into A7, D5 into S2), CODEX-BREAKTHROUGH CB-1..CB-10 plus
CB-EXEC (11 rows).

Tally in proposal terms: ADOPT 16 (A2, A6, D2, A7, P4, D4, A9, P1, P3,
P6, P9, S0, D1, CB-7, CB-8, CB-9), MODIFY 21 (A1, A3, A5, A8, A10, P2,
P5, P7, S1, D3, S2, D5, S3, D6, CB-1, CB-2, CB-3, CB-4, CB-5, CB-6,
CB-10), REJECT 3 as stated (A4, P8 probe spend, CB-EXEC).

### 1.1 ARCH (worker-arch-review-log.md, 074c1d7)

| ID | Proposal | Verdict | Evidence, reasoning, and blocking finding |
|----|----------|---------|--------------------------------------------|
| A1 | Layer 0 persistent driver daemon (snapshot/execute/verify, structured-first) | MODIFY, prototype gate | Direction right: structured state is exact and cheap (66 rects median 0.030s, single-source clone2 batch 7, C1 applies). But the composition is unproven (RTD C2, accepted by X1/X2/X3/XRT and the draft): session_driver.py runs cu.main() per command, code_exec.py is an in-process program model not a daemon, dom_act.py still grounds through image points. BLOCK full replacement (B6 STANDS). Gate: staged prototype proves snapshot/execute/verify end to end on one live ws2 clone chat. Prototype design must cover the single-runner lock as a task lock, pill visibility, the one-session-per-browser constraint (daemon holding the single Firefox session blocks every other tool for the task duration, C5), daemon crash and stale-state behavior, and lifecycle across laptop sleep and reboot. NEW: A1 and CB-EXEC are the SAME destination approached from two sides (see CB-EXEC row). Exactly ONE prototype is authorized, with one design owner. Two daemon designs is duplicate work and a merge collision waiting to happen. |
| A2 | Layer 1 pixels demoted to fallback-only, pixel-band labeled weak | ADOPT, with sequencing constraint | Proven by V1 (vision 58.6% first-try, Wilson 40.7-74.5%, V-F7) and V3 (code admits the band is necessary, not sufficient, cu.py:1023-1076). Constraint, from RTD and the draft: demote only after the router (P1) and its fallback trigger are proven; Zen chrome UI stays pixel-primary. Strengthened by V-F5: PROBE-P8 PROVED chrome context is blocked without a Zen restart, so Zen chrome UI is now PROVEN pixel-only, not merely unproven structured. The fallback must name it explicitly and permanently unless the owner approves a restart. |
| A3 | Delete session supervisor tree | MODIFY | Direction right, timing conditional. The tree's real jobs are a named killable scope, cancel/stop, the session pill label, and the single-runner lock. Gate: delete only when the driver demonstrably holds scope plus cancel latch plus lock on a live run (B4 lift). Until then the supervisor is the lock holder; deleting it risks two live runners and loses the cancel/stop path. The F1 failure cluster is partly environment faults, not supervisor-design faults; deleting the tree does not delete those modes. |
| A4 | Delete overlay daemon server (keep pill visibility) | REJECT as stated; MODIFY to session-level pill first | BLOCK. This is the one place I restore RTD's original REJECT, which the draft softened to MODIFY by label negotiation. The substance has not changed: the pill is the owner's only visibility into live runs, and BOTH replacements are unbuilt (compositor plugin in the hardest area of this repo; driver-owned pill dies with the driver, leaving a stale or missing pill, exactly the failure the daemon's holder accounting exists to prevent). The draft's MODIFY label hides that the deletion as stated is still rejected by every reviewer; relabeling a rejection as a conditional adopt is how a final decision smuggles a bad deletion through. What is ADOPTED: the session-level pill first (acquire once per task, server KEPT, measured), which removes the 315-349 ms per-batch overlay tax without touching visibility. Server deletion only after a driver-owned pill proves no stale or missing pill on crash (B3 lift). |
| A5 | Delete one-shot SSH loop (persistent Broker only) | MODIFY | Persistent-first is right (fresh SSH 4.43-5.29 s, 7 samples; mux 0.91-1.46 s, 11 samples; saving about 3.2-3.5 s per connection). The word "only" is REJECTED: the VM reaches the relay only through SSH, so this is deletion of one-shot SSH in favor of multiplexed SSH plus broker RPC, and if the broker dies, one-shot SSH is how the relay gets restarted. Gate: fresh SSH stays as the documented fallback AND the recovery path. "Only" applies to the default path, never to recovery (B4 lift). |
| A6 + D2 | Delete file-based observation/action IPC (A6) / delete scp for JSON files (D2) | ADOPT for transport | JSON over the persistent channel (or in-process calls) replaces scp per step; each scp costs a fresh about 5 s SSH. Scope condition: files stay as the audit and evidence trail (persisted observation artifacts, JSON plus JPEG, written by the driver); what dies is files as the transport, not files as the record. The JPEG still travels for the human VISION 2 check until the persistent channel carries bytes. Keep file IPC only as fallback transport when no Broker is reachable. |
| A7 + P4 + D4 | Act-now after-image scope fix (A7) / both-fields fix (P4) / delete screen-scope after-capture (D4) | ADOPT the both-fields shape; the delete-entirely half is REJECTED | Proven defective by construction (V-F2: first_action.py:661 hardcodes cu.observe_screen, overwriting desktop_act's scope-matching after-capture). Adopted shape: return BOTH after (scope-matching, chainable) and after_screen (full monitor, verification only, documented non-chainable); move the scope check before the overlay attempt; add a regression test. Execution DEFERRED to AMEND4 item 12, in flight on two lanes, NOT landed on todolist-push at HEAD af0fa87 (V-F2). REJECTED part: deleting the envelope after image entirely. It loses the human-visible evidence and the frame-change signal for a saving of about 0.25 s, which is noise; that trade fails the 06:07 criterion on accuracy. Timing, from D3 and the draft: the scope-as-capability refusal deletion (cu.py:1648/1649) is sequenced WITH P2, not with this fix. While actions are still pixel-addressed, the refusal protects typing against a screen observation. |
| A8 | Delete pixel-band verification for structured targets | MODIFY, sequenced behind P5 | Direction right: the band is admitted necessary-not-sufficient and the DOM value check is sufficient and 100-1000x cheaper (0.002-0.015 s). Gate: delete band-as-pass-signal only where the per-action DOM assert exists and is mandatory; until then the band stays as a diagnostic. Deleting before the assert set exists leaves actions with NO verification, which is worse than weak verification. The change rests on the verified opt-in-hooks ground (focus_check and type_check are still optional hooks, D1 V13), not on RTD's V11 TODO wording, which the draft correctly did not adopt as phrased (V-F7: arm_typed_flag exists and is called from dom_act.py:483-484). |
| A9 | Coordinate model to one system (CSS px element rects, converted once at the driver edge) | ADOPT for structured targets, with a proof-grade caveat | The five-frame tower has five proven bug sites (F2b-1, C12, amend3 step 5, G28, after-scope trap); the one-conversion path already exists (fastpath.dom_rect_to_screen_point, verified). Dependency, from the draft: A9 depends on AMEND4 items 5-6 landing. That dependency is NOW SATISFIED in form (b44a5ea, V-F6). CAVEAT, new: b44a5ea's own message records "F2/F3 RT2 tests defective", and items 3 and 4 landed with the same defect note. A9 may proceed on the landed code, but the round-3 council must repair or re-verify those proof tests before P2 leans on the landings as proven. The pixel fallback keeps its own frame internally; the router decides. |
| A10 | Acceptance test becomes 0-vision live benchmark on real ws2 clone chats | MODIFY, ladder with the live 2-vision rung REINSTATED | Final gate: live 0-vision on real ws2 clone chats, DOM harvest, plan, execute, DOM verify, zero screenshots in the machine loop, accuracy at least 90% scored by DOM outcome (V12 sent-bubble gate), total wall time end to end including transport, one final screenshot kept as unscored human evidence (P9), owner approval per run. Staging: fixture 2-vision first, then LIVE 2-vision, then live 0-vision. I REVERSE the draft's B1 lift (see FRT-B2, section 2). The draft's claim that live 2-vision "adds nothing measurable" is wrong: the P9 screenshot is read by the same fallible vision (58.6% first-try, Wilson 40.7-74.5%) it is supposed to check, while the live-thread look is a direct check of the rendered outcome. DOM can report a bubble present while the render shows the wrong thread or a hidden render; only the live look catches that. One extra run costs about 0.25 s plus one model read and protects accuracy; removing it trades accuracy for negligible speed, which fails the 06:07 criterion. BLOCK finalizing A10 as a two-rung ladder. |

### 1.2 GROUNDING P1-P9 (worker-grounding-review-log.md, d1fc4e9)

| ID | Proposal | Verdict | Evidence, reasoning, and gating conditions |
|----|----------|---------|---------------------------------------------|
| P1 | DOM/a11y default router (Zen Marionette/BiDi, Chromium CDP, AT-SPI, screenshot last; encoded in code, not convention) | ADOPT | Two perception stacks with no routing rule drift to the worse one (works everywhere) instead of the better one (needs setup). Requirements: encode the router in code as one function returning the perception source; fail closed to the labeled screenshot fallback; a per-target routing table proven per target before the default flips; a log line on every routing decision, so drift back to screenshots is visible instead of silent. Note: the a11y branch is thin for the apps in play (AT-SPI cannot see Zen; AT-SPI numbers unverified on this VM), so it mostly covers native apps that are not the live workload. Interim honest state: Brave tasks still route to screenshots until P3 lands. |
| P2 | Element-ref action interface rewrite (live rect re-read at execution, screen-point action form, delete dom_rect_to_image_point from the live path) | MODIFY | Direction right and highest-leverage code change after P3: the round trip exact DOM rect to exact screen point to lossy image point and back is proven wasteful from source (fastpath.py:195-243, dom_act.py:312, cu.py:1000-1005), and it deletes the F2b-1, C12, amend3-step-5 bug class. Gating conditions (B5, narrowed): (a) the stale-ref disagreement protocol is specified first (what happens when a live rect re-read disagrees with the plan: refuse, re-plan, or click stale, per case; lifecycle across a multi-action plan); AND (b) AMEND4 items 2-4 have landed. Limb (b) is SATISFIED at HEAD af0fa87 (c1ea773, 62b740e, 72120aa), so the protocol is now the single outstanding gate. CAVEAT (V-F6): item 4 landed with "F5 behavior test defective" in its own message, so the landing is form-satisfied, not proof-grade; the protocol writer must re-verify item 4's landed wiring against P2's target functions. CB-2's stricter "scope change stops the batch" must be decided inside this ONE protocol (see CB-2 row): my position is re-ground-and-continue when a DOM re-read is cheap (0.030 s) and the target is unambiguous, stop only on ambiguity or a scope change re-grounding cannot resolve. Two protocols for the same decision is a defect. Delete dom_rect_to_image_point from the live path (keep for tests and legacy). The scope-as-capability refusal deletion lands in this step (see A7 row). |
| P3 | Brave relaunch with debugging port (controlled experiment, quiet window, never mid-batch; fallback agent-managed Chromium) | ADOPT as a controlled experiment | Single highest-leverage unblocker: the clone chats live in Brave, Brave holds no debugging port on its default profile (cdp.mjs comment verified verbatim), so the CDP path cannot reach them today. Conditions: quiet window owned by the coordinator, never mid-batch; verify /json/list shows the Muse tab and login intact; run observe plus harvest plus one fill plus assert on a scratch input. Recorded additions: CDP on port 9223 exposes the logged-in browser to any local process (security consideration); the Chromium fallback is a migration with re-login and clone reconfiguration, not a fallback, and needs its own login-persistence check; cdp.mjs notes shadow-DOM elements have null box_model, and Messenger's DOM shape against that gap is unexamined. BLOCK on any live-task migration until the experiment passes. NEW STATUS (V-F5): PROBE-P3 is NOT-RUN, clone1 batch 9 open since 06:01 (7b1006a). The quiet window does not exist yet; the experiment is gated on batch 9 completing, not on a vague "quiet window". If P3 fails (Brave refuses the port and the Chromium migration is too disruptive), the DOM-first live path loses its highest-leverage unlock and the whole program re-plans around Zen Marionette only; report that plainly, not worked around silently. |
| P5 | DOM verification mandatory (focus_check and type_check required, not optional hooks; CDP fill read-back and assert polling the model) | MODIFY | Direction right; the code admits the band is insufficient. The blanket mandate is BLOCKED as stated: the assert set does not exist for every action type (focus_check/type_check are still optional hooks, D1 V13), and no per-action exception list exists. Gate: DOM verification becomes mandatory PER ACTION TYPE as its assert lands; an explicit per-action exception list names the actions where DOM assert is impossible (scroll position, hover state) and pixel stays the only signal; the band stays as a diagnostic until then. A blanket mandate now means false refusals on working flows or vacuous asserts (false confidence). The V12 sent-bubble gate in the benchmark is the pattern. CB-1's three-part contract folds into this row (see CB-1). |
| P6 | Measure the vision call | ADOPT, with specification fix | Cheapest item on the list and a precondition for honest speed claims: capture is 15-30 ms and DOM rects 0.030 s, but the model read that locates the target is seconds and timed nowhere. Bundle with S0. Specification fix, from RTD and the draft: the model call happens in the calling agent's loop, outside cu.py, so the proposal must specify the timestamp points (observation delivered to the agent vs located target returned) and the owner of the logging (the harness, not cu.py), or it will be recorded as done when only capture timing is logged again. CB-7 and CB-10 fold into this ONE measurement workstream (see CB-7, CB-10 rows). Until that number is in the logs, every speed claim about the screenshot path is incomplete, and nobody may claim the 10s target is met. |
| P7 | Session handover protocol (one protocol per browser per task phase, BiDi ground then Marionette input or stay on one) | MODIFY | The one-session constraint is proven (4 runs, Firefox allows exactly one remote session per instance), so a protocol is needed IF a task genuinely needs two protocols. Gate: first answer whether Marionette-only suffices (the benchmark already runs Marionette-only, harvest plus input, and zen_dom harvest IS Marionette). Write the handover protocol only if a task genuinely needs BiDi for grounding plus Marionette for input. Price noted: a handover costs 4-7 s per switch (BiDi new 1.51-2.77 s fresh, Marionette attach 2.65-4.12 s), comparable to the SSH tax being deleted; a protocol that costs more than the tax it enables is not a win. If CB-EXEC's single-owner broker is adopted, P7 dissolves into that design (the broker owns the one session); do not write a standalone protocol and a broker session design for the same slot. |
| P8 | Zen chrome Marionette context test (set_context chrome) | REJECT further spend; boundary record ADOPTED | CLOSED, by probe evidence (V-F5). PROBE-P8 landed as commit 3790901: chrome context BLOCKED without Zen restart (HTTP 500, MOZ_REMOTE_ALLOW_SYSTEM_ACCESS required), C12 reproduced live. The only path to chrome context is a Zen restart with MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1, which kills owner tabs and the session and is a decision for the owner, not for a probe. Verdict: keep screenshots ONLY for Zen chrome UI and record that boundary explicitly; AT-SPI remains closed too (C12: Zen never registered accessibility). The draft's "ADOPT as a bounded, time-boxed, low-priority probe" is STALE and must NOT be finalized as an open probe. Any further spend needs an owner-approved Zen restart, stated up front. |
| P9 | Keep one screenshot for the human (VISION 2 stays, machine scores by DOM) | ADOPT | Correct division: screenshots are a human evidence channel, not a machine perception channel. VISION 2 stays as unscored human evidence; the machine scores by DOM outcome. Wording correction, from RTD: VISION 2 is the agent looking at the threads and reporting to the human, not the owner looking directly, so it is the agent's final sanity check reported to the human. Cost is about 0.25 s plus one vision read, noise against the total. Attached to A10. Note: P9's screenshot is human evidence, NOT an independent accuracy check, which is why it cannot substitute for the live 2-vision rung (see A10, FRT-B2). |

### 1.3 SPEED S0-S3 plus six deletions (worker-speed-review-log.md, a4ecb49)

| ID | Proposal | Verdict | Evidence, reasoning, and gating conditions |
|----|----------|---------|---------------------------------------------|
| S0 + D1 | Step 0 persistent SSH multiplexing, do now (S0) / delete fresh SSH per call (D1) | ADOPT on CORRECTED numbers | Fresh SSH 4.43-5.29 s (7 samples, confirmed four ways); multiplexed 0.91-1.46 s (11 samples, rc=0, master verified alive). Saving about 3.2-3.5 s per connection, about 3.5-5x, NOT 460x and NOT 0.01 s. SPEED's 0.01 s figure matches a failed-fast connection (master not up, rc=255, D1's diagnosis); SPEED's log records no return codes and no master-liveness check. Corrected expectation: per act-now (3 connects) about 16 s becomes about 5-6 s, not about 2 s; per observe (2 connects) about 6-8 s saved. SPEED's 1.6x per-task estimate was built on 0.01 s and must NOT be quoted; D1's revised roughly 1.3-1.4x on a CL2-MSG-class task is the working figure until a recompute on the corrected numbers. Conditions: implement the fallback explicitly (any multiplex failure falls back to a fresh connect, slow but correct); log master death; per-socket watchdog, not global (a half-dead master can hang rather than fail cleanly; ControlPersist=600 can leave a stale master holding a dead Tailscale route). The 1-day soak test runs IN PARALLEL, advisory, not a gate. PROBE-S0 has no committed log yet (V-F5); S0 is safe to authorize NOW on the existing 7 fresh plus 11 mux samples, and the soak can only refine the watchdog design, not reverse the verdict. What would change it: if PROBE-S0 shows the master dies within minutes under real idle patterns AND the fallback path itself hangs (half-dead master hang), the watchdog design must change, but the ADOPT stands because the fallback is the current behavior. |
| S1 + D3 | Step 1 act-now over the persistent relay broker (S1) / delete per-batch session spawn (D3) | MODIFY, proof-first | Direction right: the per-batch session spawn is a real tax (0.4-2.1 s) plus a real failure mode (20s deadline, timeout never falls back, council 1 B1), and JSON over the same channel kills the scp round trips. But S1 is a BUILD, not a switch: the relay is alive (PID 1821, socket exists, verified) yet zero references to session_remote or Broker exist in first_action.py or cu.py (V-F3, re-verified this session), so the broker path from the VM is unproven end to end, and the single-owner socket semantics under concurrent VM workers are unexamined (serialize or refuse). Gate: prove one live batch end to end over the broker from the VM first, then delete the per-batch spawn; keep the spawn as fallback until proven. Session-level pill (keep the overlay server) lands in the same step. PROBE-S1 has no committed log yet (V-F5); if its proof fails (broker unreachable from the VM, or single-owner semantics refuse concurrent workers), the delete half dies permanently and act-now keeps the per-batch spawn, and A1's transport assumption weakens with it. |
| S2 + D5 | Step 2 DOM-first plus code-exec plus checkpoint verification, CU_CODE_EXEC=1 on (S2) / delete per-action model call as the default (D5) | MODIFY, gated | The 10x path, already built and merged (code_exec.py 880 lines, Pick 1 winner, commits 714e4f9, 84b88bb, 2e2aeff, merge 453adc4), and the flag is OFF in the live path (verified live: CU_CODE_EXEC unset on the laptop). But the blanket flip is BLOCKED (B2, STANDS, strengthened): Y1b council 3 BLOCKED Phase A on 84b88bb with 14/20 probes passing and 3 real fails (1e f-string chr NameError; 2a codemode wall preemption, error raised only after the C loop finished; 2b code_exec wall preemption, elapsed 6.20 s, ok=True with NO error, silent success), and the named gate (2-vision benchmark) has never run. PROBE-S2's 06:36 check reconfirms the 3 fails are STILL OPEN (V-F4). NEW BLOCKER, from PROBE-S2: the fixture bench itself cannot run on this VM (no selenium, no Firefox, no geckodriver at the bench's hardcoded paths). The draft's step 3 (fixture bench run) is not runnable as written; a bench-runtime install step must precede it. Gates, in order: (a) bench runtime installed so the fixture run is possible; (b) fixture 2-vision bench green; (c) fix the 3 Y1b real fails; (d) flip the flag for ONE live task class (clone chat sends) with act-now as fallback, measure, then expand. The "10x path" label is corrected to 3-5x on unmeasured model inference time (SPEED's own honest limit: 30-60 s if vision reading dominates); the mechanism can be about 1 s, the model is the remaining unknown, and P6 must measure it before anyone claims the 10s target. |
| S3 | Step 3 laptop-side task runner, only if Step 2 plateaus | MODIFY, fold into A1; plateau defined numerically first | S3 substantially overlaps A1: a laptop-side runner that grounds, acts, and verifies locally and streams back compact state IS the A1 driver daemon approached from the other side. One design decision, not two builds; do not build a separate runner alongside A1. Gate: the plateau criterion must be defined NUMERICALLY BEFORE the S2 flip starts (threshold, run count, decision owner), so the trigger is not argued later. An undefined plateau either never triggers or triggers on one bad run. NEW HARDENING (FRT-B7): the plateau numbers are a HARD GATE on the flip step, not an open condition with a deadline. Until the numbers exist, the flip step is not authorized, because the flip is what the plateau is measured against and a plateau defined after the flip can be gamed. The decision itself happens only after steps 0-8 of section 3 are measured. |
| D6 | Delete 120s freshness window as a gate on DOM work | MODIFY, scoped | For DOM-grounded work, re-read the DOM (0.030 s) instead of refusing for staleness; the window is a patch for vision coordinates, not a law. Correction, from RTD: the refusal at cu.py:773 also guards against future-clock observations, and a blanket delete removes the clock-skew guard. Gate: keep the future-clock refusal, drop only the age refusal for DOM paths. Keep the window for pixel-addressed work, where staleness is real and the refusal protects against acting on a dead frame. |

### 1.4 CODEX-BREAKTHROUGH CB-1..CB-10 + CB-EXEC (codex-breakthrough-report.md, 2596287)

Codex's report is a genuine fourth reading with NEW evidence, not only a
fourth citation of the same base (C1). New material it brings: the
first-action JSONL aggregate (199 lines, V-F8); the J40 scope-substitution
record (+45,+12 px miss, ok returned); the J37 codec false refusal
(patch diff 6.627 vs threshold 6, consistent with cu.py:1015, V-F7); the
Wilson 95% interval for 17/29 (40.7-74.5%, arithmetic verified, V-F7);
the 90% per-click math (0.9^20 = 12.2%, 0.9^32 = 3.4%, verified, V-F7);
the CB-7 challenge to the 95% SSH attribution; and the deployment-drift
finding (installed first_action.py not in the repo at Codex's HEAD,
installed cu.py with two extra act-now branches). Its limits are also
real: it ran no live browser, BiDi, Marionette, AT-SPI, overlay, or
compositor test; it did not re-run the DOM bench; it could not verify
the 66-rect/5-click claim from local evidence; its SSH challenge and its
"behind 622 commits" note are both partly self-qualified. I judge each
proposal on its own evidence, not on Codex's authority.

| ID | Proposal | Verdict | Evidence, reasoning, and gating conditions |
|----|----------|---------|---------------------------------------------|
| CB-1 | Three-part result contract (input_sent / verified=true only with postcondition) | MODIFY, merge into P5/A8 | The failure mode is proven: G30 (click into empty space reported ok) and V-F2 (envelope ok=True on session ok with no postcondition anywhere in the path). The contract is the right shape: split input sent, correct target received input, and post-state confirmed. BLOCKED as a standalone contract for two reasons. First, the rename breaks callers unless migrated in the same commit: first_action.py:552-563 propagates session ok into envelope ok today, so renaming ok to input_sent without migrating the envelope logic creates a silent compatibility break (envelope ok disappears or is misread downstream). Second, "verified=true only with postcondition" presumes postconditions exist for every action; for scroll, hover, and focus-only moves there is no cheap postcondition, so the contract needs the SAME per-action exception list as P5, or it mandates false refusals or vacuous postconditions. Gate: fold CB-1 into P5/A8 as the contract for DOM-verifiable actions, with the exception list, and migrate the envelope logic in the same commit. |
| CB-2 | Scope mandatory in action data, scope change stops the batch | MODIFY; blanket stop REJECTED | The defect class is real: J40 (window-scope point used on a full-screen image, miss about (+45,+12) px, command still returned ok) and the _fresh_observation substitution path (missing/stale/old observation replaced by a full-screen capture while the action list is passed through unchanged, no frame conversion, no stop). Scope must be a mandatory part of action data. The PRESCRIPTION overcorrects: a blanket stop on every scope change throws away cheap recovery. A DOM re-read costs 0.030 s; when the target is unambiguous after re-grounding, re-ground-and-continue is strictly better than stopping the batch, on both accuracy and speed. My position: scope change triggers re-grounding first; stop only on ambiguity or a scope change re-grounding cannot resolve. CB-2's stop rule and P2's stale-ref protocol must be ONE protocol, not two (see P2 row). Gate: decide the protocol inside the P2 step, with CB-2's J40 evidence as a test case (the protocol must refuse or re-ground the J40 shape, never silently convert frames). |
| CB-3 | Vision error taxonomy + image uniformity + J37 codec false refusal | MODIFY (uniformity ADOPT, taxonomy gated on P6) | Three parts, three verdicts. (a) Image uniformity: ADOPT. Verified from source (V-F7): observe defaults to max_width=960 (cu.py:920/974) while act-now captures at 1920 (first_action.py:353/661), so the model's input resolution and detail change by path. One max_width for all captures is trivial and right. Condition: re-run an E2-style calibration after the change, because the model's input distribution changes and the old 58.6% number no longer applies. (b) J37 codec false refusal: ADOPT the fix. The preflight compares a decoded JPEG against a fresh uncompressed capture with a patch threshold of 6 (cu.py:1015, verified); J37's patch diff of 6.627 tripped it. A codec artifact is not a screen change; separate the two or the refusal stays flaky. (c) Vision error taxonomy: MODIFY. A taxonomy is classification, not a fix; without P6's measurement it is paperwork with no numbers to classify. Gate: taxonomy is populated from P6-measured vision calls, not written from the armchair. Also noted: the Wilson interval (40.7-74.5%) widens the uncertainty on every vision-dependent claim; vision could be as bad as 40.7% first-try, which strengthens A2/P1 but also means no vision-dependent number in this round is tight. |
| CB-4 | Batch growth by proven validity (90% per-click math: 20 clicks 12.2%, 32 clicks 3.4%) | MODIFY, fold into P5/CB-EXEC postconditions; math must not be quoted as measured | The arithmetic is correct (V-F7) and the conclusion is right: 90% per-click does not mean 90% task success, and a batch should grow only when the executor proves the next steps are still valid, not because coordinates can be stuffed into one image. But the math ASSUMES independent errors, and Codex itself says it is only an illustration. Real errors correlate through the shared frame: one wrong frame poisons every coordinate taken from it, so the true all-correct rate is likely WORSE than 12.2% when the frame is wrong. Do not quote 12.2%/3.4% as measured rates; no measured per-click rate on held-out tasks exists, and the 90% figure is hypothetical. As a standalone proposal CB-4 duplicates P5's assert set and CB-EXEC's postconditions; fold its rule (grow the batch only on proven validity) into the P5 assert set and the CB-EXEC prototype's postcondition design. BLOCK using CB-4's math as a gate threshold. |
| CB-5 | Common executor routing + Zen adapter + locate confirms visible/interactive/uncovered/stable/unique + remove unrestricted zen_dom eval from default interface + AT-SPI coverage reporting | MODIFY; routing half merged into CB-EXEC, eval removal ADOPTED | Split verdict. (a) Remove unrestricted zen_dom eval from the default agent interface: ADOPT, with a debug-mode carve-out. The capability exists (evaluate() at zen_dom.py:441, V-F7): arbitrary JavaScript in the current tab as a default primitive is a correctness and safety hole (it can silently rewrite the page the agent is supposed to read). Keep it in an intentional debug mode only, as Codex itself concedes. (b) Locate confirmations (visible, interactive, uncovered, stable, unique): ADOPTED as requirements, with definitions owed. "Stable" and "unique" are unmeasurable as stated (stable for how long? unique by selector or by visible set?). They become acceptance criteria only with operational definitions. (c) AT-SPI coverage reporting: ADOPT. The a11y tree is partial by design (500 nodes or 2 s cap, max 80 items, truncated flag, a11y.py:83-104); a backend that silently returns a partial tree is a false-confidence source. Report coverage, then fall through to DOM or image when the tree is insufficient. (d) Common executor routing: BLOCKED as a standalone build. It IS CB-EXEC's routing layer; do not build routing twice (once in CB-5, once in CB-EXEC). Fold into the CB-EXEC prototype decision. |
| CB-6 | act-now uses the long-lived session driver, one owner, sequential queue | MODIFY, merge into S1 | This duplicates S1 exactly except for "sequential queue": act-now today spawns a session per call (first_action.py attempt_session, verified), the Broker and session driver already exist, and the fix is to route act-now through the session driver with one owner. The new content is the queue, and its discipline is unspecified: what happens to the second queued batch (wait? refuse? timeout?), and how does a sequential queue behave under concurrent VM workers (the same single-owner socket question RTD raised for S1)? Gate: fold CB-6 into S1; the queue discipline (wait/refuse/timeout plus the concurrent-worker semantics) must be specified before the merge lands. BLOCK CB-6 as a separate track. |
| CB-7 | Latency measurement fixes + measure VM-to-laptop dispatch separately | ADOPT | The strongest measurement item in the Codex report, and the one place Codex corrects the record. Its methodological point is real: the act-now JSONL starts after the command reaches the laptop, so it cannot support a dispatch share, and the "11.6 s of 12.26 s is SSH dispatch" figure (95%) rests on one F2b run's accounting, not on the laptop log. What CB-7 does NOT do: it does not kill the SSH tax. SPEED's fresh-SSH measurements (4.43-5.29 s, 7 samples, four-way confirmed) are independent of the laptop JSONL, and F2b's VM-side dispatch accounting is consistent with 2-3 fresh connects. The precise "95%" share stays single-source and must not be quoted as a law. Adopted: redefine order_to_overlay from the user command on the VM (not from Python wrapper start); fix target_breached to compare first-pointer-action time against the 30 s threshold, not whole-batch time; measure VM-to-laptop dispatch separately per phase (VM send, SSH connect, laptop work, return). Fold into P6 as ONE measurement workstream, not a second one. |
| CB-8 | Evidence discipline (DONE is a state of specific evidence) | ADOPT as a standing rule, scoped | Correct and overdue: the todolist marks items DONE for "direction determined" or "fixture proven", which is not the same as proven on a real app (Codex 2.8: 13/13 on a fixture cannot become a 90% commitment on another app; held-out new app is PARTIAL; J10 real think-time is OPEN). Its teeth: any proposal whose DONE basis is a fixture-only proof gets its DONE revoked until live evidence exists. SCOPE, to keep it from becoming an unbounded audit: apply it only to the DONE items that gate this final direction (S2's Pick 1 DONE, the bench DONE, the DOM-grounding DONE claims), not a full-history re-audit. CB-8 has no build and no measurement; it must not consume a build slot or delay the order of work. It is a rule the finalizer enforces when judging gates, not a workstream. |
| CB-9 | Deployment manifest (lock source commit + installed artifact + log) | ADOPT, ranked below accuracy/speed work | Cheap and obviously right. The drift is real in kind: at Codex's HEAD the installed first_action.py was not in the repo and the installed cu.py had two extra act-now branches vs the checkout, and the remote-tracking ref was stale (Codex admits it could not confirm the "behind 622" state). Premise partly overtaken (V-F2: first_action.py IS in the repo now), but the manifest idea stands: the deploy step itself must record source commit plus installed artifact hash plus log, as one manifest per deploy. Rank: under the 06:07 criterion it changes auditability, not the accuracy or speed of the final result, so it lands after the accuracy/speed work, not before it. It must be produced by the deploy step, not as a separate audit project. |
| CB-10 | Overlay flicker vs think-time separate, per-phase measurements | MODIFY, fold into P6/CB-7 | The separation is right: the todolist records 0 repaint and 0 event for overlay idle, but the LIQUID background test never ran because the plugin was not loaded, so there is no evidence the original flicker was reproduced or fixed; and think-time (J10, H2) is OPEN and unmeasured by act-now. Two problems as a standalone track. First, it duplicates P6/CB-7 measurement work; fold it into the ONE measurement workstream. Second, the flicker itself is unproven on the current build (plugin not loaded means the flicker may not even exist now). Gate: first establish the flicker reproduces on the current build; if it does not reproduce, CB-10 dissolves. Do not measure the phases of a phenomenon that may not exist. |
| CB-EXEC | The semantic transaction executor itself (semantic targets, preconditions, real mouse/keyboard, postconditions, retry only when surely unsent; one local broker; DOM/BiDi + AT-SPI + screenshot-crop backends under one contract; vision as fallback; 100 held-out tasks benchmark, 90% defined as task success, about 96/100 for 95% confidence) | REJECT as stated; MODIFY to prototype-only | BLOCK. This is the biggest build in the round (2-3 day Zen prototype, 1-2 weeks to merge, plus days of benchmark) and the least proven. Six findings. (1) No existence proof whatsoever: zero lines built, zero measurements. It fails RTD's C2 harder than A1 does: A1 at least has parts that individually run (code_exec, session_driver, Broker); CB-EXEC's semantic transaction executor with preconditions, postconditions, and retry-only-when-surely-unsent exists in no form at all. Under the 06:07 criterion a 1-2 week build cannot be authorized on zero running evidence when the much smaller S2 flip is BLOCKED on 3 known fails. (2) Single-session-slot risk, concentrated: Zen allows exactly one remote session per instance (proven in 4 runs). CB-EXEC's "one local broker, one owner" concentrates ALL execution through one session holder; a hung session blocks every client, and Codex names this risk itself without specifying recovery. Who kills a wedged session, on what timeout, with what watchdog? The current architecture fails per batch; CB-EXEC fails totally, with no designed recovery. (3) Retry-only-when-surely-unsent is circular: it assumes the delivery knowledge it exists to provide. For a click that may have submitted a form, "surely unsent" is unknowable from DOM alone if the page navigated. The safe default (never retry a possibly-sent action) means real failures become unrecoverable without model intervention, which pushes model calls back up, the opposite of the speed goal. (4) The 100-task benchmark is disproportionate: 100 held-out tasks across browser and desktop apps, authored by one person, run across 4 variants (screenshot-only, DOM+mouse, AT-SPI+mouse, executor) with interleaved ordering, is 400 task runs plus days of task authoring, to inform a decision the A10 ladder already answers at 90%. The Wilson math is correct (96/100 gives a lower bound of about 90.2%, V-F7) but its independence assumption does not hold: 100 tasks authored by one person on a handful of apps are NOT independent samples (shared app quirks correlate), so the 95% confidence claim is statistically decorative. (5) It absorbs A1/S3/P2/P5/S1/CB-1/CB-2/CB-5/CB-6. Adopting it as stated makes the draft's staged order incoherent: there is no point flipping CU_CODE_EXEC=1 for one task class and rewriting P2's interface if both are about to be replaced by a new executor. Conversely, if the staged order proceeds, CB-EXEC's prototype duplicates S2+P2 work. The finalizer must choose ONE destination, not fund both. (6) The schedule (2-3 days prototype, 1-2 weeks merge) is an estimate with no prototype behind it; under 06:07 cost is irrelevant, but an unproven estimate is not evidence. PROTOTYPE GATE (the MODIFY): authorize ONLY the 2-3 day Zen prototype (semantic targets, real mouse, preconditions, postconditions) on a handful of held-out tasks, proven on live tasks, with CB's own metric list (first-try target accuracy, end-to-end task success, wrong side effects, recovery actions, per-phase p50/p90, model calls, retry count, postcondition accuracy, false successes). THEN decide merge vs A1, on measured evidence. If the prototype fails or stalls, CB-EXEC dies and A1/S3 remains the destination. The 100-task benchmark is NOT authorized before the prototype proves; a smaller held-out set (same metric list) decides the prototype, and the 100-task run, if ever needed, is a release gate, not a design gate. |

## 2. Blocking findings, final status

- FRT-B1 (NEW). CB-EXEC as stated is REJECTED. Only the prototype is
  authorized (see CB-EXEC row). Lift condition for the merge: the Zen
  prototype proves semantic targets plus real input plus postconditions
  on held-out live tasks, with the recovery protocol for a wedged
  session specified and proven, and the A1-vs-CB-EXEC choice made on
  measured evidence. The 100-task benchmark is not a lift condition for
  the prototype; it is a release gate after the merge decision, if ever.
- FRT-B2 (NEW). The draft's B1 lift is REVERSED. The live 2-vision rung
  is REINSTATED as a required rung in the acceptance ladder. The draft
  lifted B1 on XRT's argument that live 2-vision and live 0-vision-with-
  P9 are "the same machine behavior". They are the same machine behavior
  and NOT the same evidence: the P9 screenshot is read by the same
  fallible vision (58.6% first-try, Wilson 40.7-74.5%) it is supposed to
  check, while the live-thread look is a direct human check of the
  rendered outcome. The draft also lifted by counting council agreement
  (three councils staged A10), which violates C1: agreement is not
  independent confirmation. The lift is a vote, not evidence. BLOCK
  finalizing A10 as a two-rung ladder.
- FRT-B3 (NEW). A4 deletion as stated is REJECTED (restores RTD's
  original REJECT). The draft's softening to MODIFY was label
  negotiation, not a substance change. Lift condition: session-level
  pill measured (server kept), then driver-owned pill proves no stale
  or missing pill on crash. B3 STANDS as a gate.
- FRT-B4 (NEW, strengthens B2). The S2 flip is blocked on THREE
  conditions, not two: (a) bench runtime installed so the fixture run
  is possible (PROBE-S2: runtime absent on the VM, V-F4); (b) fixture
  2-vision bench green; (c) the 3 Y1b real fails fixed (still open at
  the 06:36 check, V-F4). B2 STANDS.
- FRT-B5 (NEW). P8 is CLOSED. No further spend on Zen chrome context
  without an owner-approved Zen restart (PROBE-P8 landed 3790901,
  V-F5). The draft's P8 ADOPT-as-probe is stale and must not be
  finalized as an open probe.
- FRT-B6 (NEW, narrows B5). B5 is NOT lifted. Its second limb (AMEND4
  items 2-4 landed) is satisfied in FORM at HEAD af0fa87, but items 3,
  4, and 5-6 landed with defective proof tests noted in their own
  commit messages (V-F6), and the stale-ref disagreement protocol is
  still missing (unanswered by all four cross-responses, draft section
  2 item (e)). P2 stays MODIFY. Lift condition: the protocol is
  specified AND the defective proof tests for items 3, 4, 5-6 are
  repaired or re-verified.
- FRT-B7 (NEW, hardens S3). The numerical plateau definition is a HARD
  GATE on the S2 flip step, not an open condition with a deadline. Until
  the numbers exist, the flip is not authorized.
- Carried, unchanged: B2 (S2/D5 blanket flip, strengthened by FRT-B4),
  B3 (A4, as a gate, strengthened by FRT-B3), B4 (A3/A5 delete-first
  ordering, as a gate), B6 (A1 full replacement, as a gate). B1: LIFTED
  by the draft, REVERSED by FRT-B2, reinstated as a required rung.

## 3. Order of work (numbered, gated)

Every step is independently verifiable, every step lands a measured win
before the next step starts, and no step depends on a bet that has not
yet paid off.

0. S0 plus P6 plus CB-7 plus CB-10 (folded into the ONE measurement
   workstream), now. Persistent SSH multiplexing with explicit fallback,
   master-death logging, per-socket watchdog; P6 vision-call measurement
   with the timestamp points and harness owner specified; CB-7 dispatch
   measurement per phase; CB-10 flicker reproduction check first (if the
   flicker does not reproduce, CB-10 dissolves). CB-8 evidence discipline
   adopted as a standing rule (scoped audit of gate-relevant DONE items
   only). CB-9 manifest produced by the deploy step. Gate to step 1:
   fallback explicit and watchdog in place. The 1-day soak test starts
   the same day and runs IN PARALLEL, advisory, not a gate.
1. AMEND4 continues in parallel, slower, per the owner 06:09 TWO TRACKS
   rule (section 6). Item 12 (A7/P4) lands via the in-flight run; verify
   the regression test. Repair or re-verify the defective proof tests
   for items 3, 4, 5-6 before P2/A9 lean on those landings. Gate: the
   rewrite track makes no parallel edits to the same functions AMEND4
   is working on.
2. Bench runtime install on the VM (selenium plus Firefox plus
   geckodriver at the bench's hardcoded paths) or run the bench on the
   laptop where Firefox exists. NEW step the draft lacks: PROBE-S2
   proved the fixture run is not runnable as written (V-F4). Gate to
   step 4: the bench runs at all.
3. P3 Brave relaunch experiment, gated on clone1 batch 9 completing
   (PROBE-P3 NOT-RUN, batch 9 open since 06:01, V-F5). Real quiet
   window between clone batches, coordinator-owned, never mid-batch,
   rollback stated BEFORE the window (relaunch without the flag, Brave
   session restore, re-login cost). Gate to any live DOM work: P3 passes
   (login intact, /json/list shows the Muse tab, one fill plus assert
   on a scratch input) or the Chromium fallback is proven with its own
   login-persistence check. No live-task migration until then. If P3
   fails, re-plan around Zen Marionette only and report it plainly.
   P8 does NOT ride in this step: it is closed (FRT-B5).
4. Fixture 2-vision bench run (gate: passes), fix the 3 Y1b real fails
   (gate: fixed), and define the plateau numbers NUMERICALLY (gate:
   defined before step 5, FRT-B7). This step does not depend on P3
   (headless Firefox, local fixture) and may run in parallel with
   step 3 once step 2 is done.
5. P1 router plus P5 asserts per action type (plus CB-1 contract for
   DOM-verifiable actions, CB-4 batch-growth rule folded into the
   assert set, CB-2 scope rule folded into the stale-ref protocol
   decision). Rewiring of existing hooks; P5 per action type as its
   assert lands, plus the explicit exception list. Gate to step 6: the
   router logs its routing decisions, and the P5 assert set covers the
   S2 task class (clone chat sends). This step precedes the S2 flip
   because S2's checkpoint verification IS P5; flipping without it
   leaves a window where the live loop runs code-exec with pixel-band
   verification only.
6. S2 flip for ONE live task class (clone chat sends) with act-now as
   fallback. Measure model-call count, wall time, and P6 vision-call
   latency. Gate to expansion: measured on one class; expand only on
   measurement.
7. P2 element-ref interface rewrite, after the stale-ref protocol is
   specified (items 2-4 landed limb satisfied, protocol the single
   gate, FRT-B6). A9 one-system coordinates land in this step (items
   5-6 landed, proof tests repaired per step 1). The scope-as-capability
   refusal deletion lands in this step, not with A7. CB-5's eval
   removal lands in this step (default interface only, debug-mode
   carve-out kept). Gate to step 8: P2 proven on the S2 task class with
   DOM verification mandatory.
8. S1/CB-6 broker path proof from the VM on one live batch (queue
   discipline specified first: wait/refuse/timeout plus
   concurrent-worker semantics), then delete the per-batch spawn.
   Session-level pill (server kept) in the same step. P7's
   Marionette-only question is answered before any handover protocol
   is written. Gate to step 9: one live batch proven end to end over
   the broker from the VM.
9. ONE prototype decision: CB-EXEC prototype (2-3 day Zen prototype,
   semantic targets plus real input plus postconditions, with the
   wedged-session recovery protocol) OR the A1 daemon prototype
   (snapshot/execute/verify). Exactly one is built, with one design
   owner. The prototype must prove end to end on one live ws2 clone
   chat, on held-out tasks, with CB's metric list (first-try target
   accuracy, end-to-end task success, wrong side effects, recovery
   actions, per-phase p50/p90, model calls, retry count, postcondition
   accuracy, false successes). Gate to step 10: prototype proven and
   the A1-vs-CB-EXEC choice made on measured evidence. If the CB-EXEC
   prototype fails or stalls, CB-EXEC dies and A1/S3 remains the
   destination.
10. A3/A4/A5 deletions last, each gated on its replacement proving (A3:
    driver holds scope plus cancel latch plus lock; A4: session-level
    pill measured, then driver-owned pill crash proof, then delete the
    server; A5: broker proven on the VM path with one-shot SSH kept as
    recovery).
11. Acceptance ladder (section 4): fixture 2-vision (step 4), live
    2-vision, then live 0-vision with the P9 screenshot kept as human
    evidence.

What this order changes vs the draft: step 2 (bench runtime) is new;
step 3 gates P3 on batch 9 completion and drops P8 (closed); step 4
adds the bench-runtime gate and hardens the plateau to a hard gate;
step 5 folds CB-1/CB-2/CB-4 into P5/P2; step 9 replaces the draft's
A1/S3 decision with ONE prototype decision (CB-EXEC vs A1); step 11
restores the live 2-vision rung.

## 4. Acceptance test (and what in the draft's ladder I block or change)

Decision: the acceptance test is a LADDER with THREE required rungs.
I BLOCK the draft's two-rung ladder (FRT-B2).

- Rung 1 (required, first): fixture 2-vision benchmark. Headless
  Firefox, local fixture. It has never run at all (BUILD ONLY); the
  whole program's gate cannot be an unrun script. Bring the bench
  runtime onto the VM first (step 2); the bench files are already on
  todolist-push (c5311ce, 7f3a70b). Pass criteria: the script's own
  gates (V12 sent-bubble gate after each message, scoring by OUTCOME
  in the thread DOM, never point-in-box). This rung does not depend on
  P3 and may run as soon as step 2 lands.
- Rung 2 (required, second): LIVE 2-vision benchmark on the REAL ws2
  clone chats (clone1 Brave plus clone2 Chrome). DOM harvest, plan,
  execute, DOM verify, accuracy at least 90% scored by DOM outcome,
  total wall time measured end to end including transport. Conditions:
  P3 closed first (otherwise it falls back to screenshots and proves
  nothing); quiet window with clone coordination; owner approval per
  run (the bench's --live plus --confirm-live gates plus plan-URL
  gate); agreed test messages so the clones' working threads are not
  polluted. This rung is the proof that DOM works on real Messenger
  pages, and the live-thread look is the only independent check that
  the DOM outcome matches what a human sees. The draft's claim that it
  adds nothing measurable is rejected (FRT-B2).
- Final gate (required, last): LIVE 0-vision benchmark on the REAL ws2
  clone chats. Same shape as rung 2, zero screenshots in the machine
  loop. Pass criteria: accuracy at least 90%, scored by DOM outcome;
  total wall time measured end to end including transport. One final
  screenshot is kept as unscored human evidence (P9); it must not feed
  the score.

What the fixture run does NOT prove, recorded as a gap not papered
over: a fixture pass alone repeats the F1a/F2b pattern (pass on the
exercise, unproven on the real task). The live runs are the proof the
fixture cannot give, because the real tasks fail on Brave on ws2,
where the DOM path does not reach yet (P3).

CHANGED vs the draft's ladder: the live 2-vision rung is restored as
required (draft: diagnostic only). The P9 screenshot is human evidence,
not an accuracy check, and cannot substitute for the live-thread look.
No rung may be skipped on the ground that the bench "already embodies"
the design; the bench never ran.

## 5. What STOPS (killed, deleted, or never built)

1. A4 overlay server deletion as stated: REJECTED. Session-level pill
   first, server kept (FRT-B3).
2. A3 supervisor tree deletion until the driver proves scope plus
   cancel latch plus lock (B4).
3. A5 "only": one-shot SSH kept as fallback AND recovery (B4).
4. S2/D5 blanket CU_CODE_EXEC=1 flip until bench runtime plus fixture
   green plus Y1b 3 fails fixed plus one-class flip (FRT-B4).
5. P2 immediate rewrite until the stale-ref protocol is specified and
   the defective proof tests for items 3, 4, 5-6 are repaired or
   re-verified (FRT-B6).
6. CB-EXEC 1-2 week merge plus 100-task benchmark as stated: REJECTED.
   Prototype-only (FRT-B1).
7. S3 as a separate runner build: folded into A1, never built alone.
8. P7 as a standalone deliverable unless Marionette-only fails; it
   dissolves into the broker design if CB-EXEC/A1 owns the session.
9. Further spend on P8 chrome context without an owner-approved Zen
   restart: CLOSED (FRT-B5).
10. Delete-entirely for the act-now after image (A7/D4 delete half):
    REJECTED. Both-fields shape only.
11. The dead numbers, never quoted again: 460x, 0.01 s mux, 1.6x
    per-task, "10x path" for S2 (corrected: about 3.5-5x, about
    1.3-1.4x, 3-5x), "95% of 12.262 s is SSH" as a law (single-source,
    one F2b run; the SSH tax itself stands on independent measurements).
12. Any DONE marking without specific evidence (CB-8 rule, scoped to
    gate-relevant DONE items). Fixture-only DONE is revoked until live
    evidence exists.
13. Big-bang A1 (B6): no deletions until the prototype proves.
14. CB-2 blanket stop, CB-4 math as a gate threshold, CB-5 routing as
    a standalone build, CB-6 as a separate track, CB-10 as a standalone
    track: all folded or rejected as stated, per section 1.4.
15. Quoting clone2 batch 7 DOM numbers as three independent
    confirmations (C1): one measurement, cited three times, not three
    measurements. Every timing-dependent row carries that discount
    until the bench is re-run.

## 6. AMEND4 sequencing

CONTINUE, slower, per the owner 06:09 TWO TRACKS rule. Do not pause,
redirect, or stop. All four cross-responses agree, and the owner rule
answers the question directly.

- Landed state at HEAD af0fa87 (V-F6): items 1-8 landed (cc964b2,
  c1ea773, 62b740e, 72120aa, b44a5ea, 49081aa, af0fa87). Remaining:
  items 9, 10, 11, 12. Item 12 is in flight on two lanes (Codex
  amend4-codex, VM CLICK3-AMEND4); the rewrite track consumes it and
  does not duplicate it.
- Triage going forward: item 12 FIRST among remaining (it IS the
  A7/P4 fix all reviews agree is proven-needed, and it is verified
  still unlanded, V-F2); then items 9, 10; item 11 (doc fix) any time.
  The draft's split-3/4 settlement is now MOOT in fact: items 3 and 4
  have both landed, so their deprioritization no longer applies. The
  draft's triage list (first 5, 6, 7, 8, 12, then 9, 10) is overtaken
  the same way: 5, 6, 7, 8 are done.
- NEW (V-F6): items 3, 4, 5-6 landed with defective proof tests noted
  in their own commit messages. The round-3 council repairs or
  re-verifies those tests before P2/A9 lean on the landings as proven.
  Landing with a defective test is not proof-grade landing.
- Kill rule at reconciliation: items the rewrite deletes get killed.
  The round-3 council records per item whether the fix is a patch on a
  defective design or a real redesign, and defers or kills any item
  the adopted rewrite replaces wholesale, rather than finishing it.
  An item the rewrite subsumes is verified against the new code, not
  assumed gone.
- B2/B5 findings go into the round-3 review: the Y1b 3 real fails (B2,
  still open per PROBE-S2 06:36) and the P2 collision plus stale-ref
  protocol (B5, narrowed: items 2-4 landed, protocol outstanding) are
  fed into the AMEND4 round-3 council, which judges patch vs rewrite
  per item under the 06:07 criterion.
- Pace per TWO TRACKS: fewer parallel workers, smaller batches,
  per-item verification, no new scope. The two tracks run in sequence
  per item on shared files, not in parallel on the same functions.

## 7. Probe dependence: what would change my verdicts, and which draft verdicts must NOT be finalized before the probes land

At 06:41 +07, PROBE-P8 has landed (3790901, CLOSED negative), PROBE-P3
is NOT-RUN (7b1006a), PROBE-S2 is in progress with an uncommitted log
(bench runtime absent, Y1b fails still open), and PROBE-S0, PROBE-S1,
PROBE-DOMZEN have NO committed log in this tree (V-F5). Per proposal:

- PROBE-S0 (SSH soak). Affects S0/D1 only. My ADOPT is safe to finalize
  NOW on the existing 7 fresh plus 11 mux samples. What would change
  it: soak showing the master dies within minutes under real idle
  patterns AND the fallback path itself hangs (half-dead master hang).
  That changes the watchdog design, not the verdict, because the
  fallback is the current behavior.
- PROBE-P3 (Brave relaunch). Affects P3, P1 (live), P2 (live value),
  S2 (live expansion), A10 (live rungs). UNSAFE TO FINALIZE before it
  lands: the draft's A10 ADOPT-as-staged assumes the CDP path exists,
  and the draft's P3 ADOPT is safe only as an experiment design, not
  as a live-path assumption. What would change my verdicts: if Brave
  refuses the port AND the Chromium migration breaks login, P3 flips
  to REJECT and the program re-plans around Zen Marionette only; P1's
  live value and A10's live rungs are then re-scoped to Zen only, and
  the Brave clone chats stay on screenshots indefinitely.
- PROBE-DOMZEN (DOM-first on real Zen). Affects P1, P2, S2, A10. UNSAFE
  TO FINALIZE before it lands: the draft's P2 MODIFY and S2 MODIFY
  assume DOM grounding works on real Zen Messenger pages, but every
  DOM timing in the round is single-source fixture data (clone2 batch
  7, headless Firefox fixture, C1). What would change my verdicts: if
  DOM-first on real Zen fails or diverges from fixture (rects wrong on
  real Messenger pages, session slot conflicts on live Zen), P2's value
  collapses, S2's live expansion narrows to Chromium only, and the
  program falls back to the screenshot path for Zen tasks.
- PROBE-S1 (broker batch). Affects S1/D3, CB-6, A1 (transport
  assumption). My MODIFY is safe as a gated verdict; UNSAFE to
  strengthen before it lands. What would change my verdicts: if the
  broker proof fails (unreachable from the VM, or single-owner
  semantics refuse concurrent workers), the delete half dies
  permanently, act-now keeps the per-batch spawn, CB-6 dies with it,
  and A1's transport assumption weakens.
- PROBE-S2 (fixture bench + one-class flip). Affects S2/D5, A10 rung 1,
  B2. UNSAFE TO FINALIZE before it lands: the draft's step 3 (fixture
  bench run) is not runnable as written (bench runtime absent, V-F4),
  and the one-class flip test has not run. What would change my
  verdicts: if the flip test fails on the one class, S2 stays MODIFY
  indefinitely and code-exec does not become the default for any class;
  if the fixture bench fails, rung 1 fails and the whole ladder stalls
  at the first rung, which is the correct outcome (a gate that cannot
  pass must not be skipped).
- PROBE-P8 (Zen chrome context). LANDED. The draft's P8 ADOPT-as-probe
  MUST NOT be finalized as written; it is stale. Finalize as CLOSED
  (FRT-B5). Nothing further would change it short of an owner-approved
  Zen restart, which is a new decision, not probe evidence.

Draft verdicts that must NOT be finalized before the probes land (list):
A10 ADOPT-as-staged (needs P3, DOMZEN, bench run); P3 as a live-path
assumption (needs PROBE-P3); S2 flip timeline (needs PROBE-S2 bench
runtime plus flip test); S1 stronger than MODIFY (needs PROBE-S1);
P2 live value (needs PROBE-DOMZEN); P8 as an open probe (already
overtaken by PROBE-P8); A9 as proof-grade (needs the defective-test
repair, V-F6); B5 lift (needs the stale-ref protocol, FRT-B6); the
plateau as anything but a hard gate (needs numbers, FRT-B7).

## 8. Attacks on the draft itself (why this review differs)

1. Zero rejects. The draft covers 30 proposals with ADOPT 15, MODIFY
   14, REJECT 0, PENDING 1. A final decision round that rejects nothing
   has not actually decided; it deferred everything into MODIFY gates.
   I restore three REJECTs as stated (A4, P8 probe spend, CB-EXEC),
   because each of those as stated would damage accuracy or speed if
   executed. A finalizer that cannot say no is not finalizing.
2. The B1 lift was a vote, not evidence. XRT lifted B1 because the
   councils staged A10; the draft adopted the lift on that agreement.
   C1 says agreement is not independent confirmation. The councils all
   read the same bench docstring and reached the same staging; that is
   one reading, not proof that the middle rung adds nothing. The
   substantive argument (live 2-vision equals live 0-vision-with-P9)
   is wrong on the evidence: the P9 screenshot is vision-read, and
   vision is the proven error source (FRT-B2).
3. The draft is stale on P8 and on AMEND4. P8 landed as a closed
   negative after the draft was written, and AMEND4 items 5-8 landed
   with defective-test notes. A final decision that finalizes the
   draft's P8 row or its AMEND4 triage as written finalizes stale
   facts. Section 6 corrects both.
4. The draft never saw Codex. Its CB row is PENDING with a follow-up
   round promised. That round is this review. CB-EXEC is the largest
   build in the round and it arrived after the draft; finalizing
   without judging it would leave the biggest decision unjudged. I
   judge it REJECT as stated, prototype-only (FRT-B1).
5. The draft's step 3 (fixture bench run) assumes a runnable bench.
   PROBE-S2 proves the bench is not runnable on the VM as written.
   The finalizer must add the bench-runtime step (my step 2) or the
   order of work starts with a step that cannot execute.
6. The draft's B5 lift condition is half-overtaken and half-weakened.
   Its second limb (items 2-4 landed) is now satisfied in form, but
   the landings carry defective-test notes (V-F6), and its first limb
   (protocol) is still entirely open. The draft's presentation ("the
   protocol is now the single outstanding gate") is right about the
   protocol and silent about the test quality; I add the repair
   requirement (FRT-B6).

## 9. Evidence index

- Inputs: ARCH 074c1d7, GROUNDING d1fc4e9, SPEED a4ecb49,
  CODEX-BREAKTHROUGH 2596287, draft adjudication 9d23834, D1 37f457e,
  D2 6d1bf04, D3 14fc139, RTD e96b2ff, X1 0cf601c, X2 d5b205d,
  X3 2b0c73c, XRT 6cb3f95.
- My spot checks: V-F1 to V-F8, section 0.2.
- Probes: PROBE-P8 3790901 (landed, CLOSED negative), PROBE-P3
  7b1006a (NOT-RUN, clone1 batch 9 open since 06:01), PROBE-S2 log
  uncommitted (bench runtime absent, Y1b fails still open 06:36),
  PROBE-S0/S1/DOMZEN no committed log at 06:41 +07.
- AMEND4 landed at HEAD af0fa87: item 1 cc964b2, item 2 c1ea773,
  item 3 62b740e (F4 RT2 test defective), item 4 72120aa (F5 behavior
  test defective, BrowserAdapter does not exist), items 5-6 b44a5ea
  (F2/F3 RT2 tests defective), item 7 49081aa, item 8 af0fa87.
  Items 9, 10, 12 not landed on todolist-push.
- Y1b BLOCK: commit 9d9bd63 (14/20, 3 real fails 1e/2a/2b).
- Numbers used: fresh SSH 4.43-5.29 s (7 samples), mux 0.91-1.46 s
  (11 samples), saving about 3.2-3.5 s per connection, about 3.5-5x
  (460x dead); per act-now about 16 s to about 5-6 s; per-task about
  1.3-1.4x working figure (1.6x dead); vision 17/29 first-try 58.6%,
  Wilson 95% 40.7-74.5%; pointer error 0.5-0.9 px; DOM 66 rects median
  0.030 s, 5 clicks all landed, verify 0.002-0.015 s (single-source,
  clone2 batch 7, C1 applies); F2b order-to-overlay 12.262 s
  (dispatch 11.620 s, single-source, 95% share not quotable as law);
  overlay acquire 315-349 ms; tc02-t1 gap 722.955 s (87.8%) measured
  with a local helper, no SSH hop in it; 0.9^20 = 12.2%, 0.9^32 =
  3.4%; Wilson lower bound for 96/100 about 90.2%; first-action
  JSONL aggregate 199 lines, p50 order-to-overlay 337.5 ms, p50
  wrapper 2.288 s, 167 ok=true, 32 ok=false (Codex-reported, V-F8;
  ok rate is not a success rate).
- Code refs verified this session at HEAD af0fa87: scripts/cu.py
  (OBSERVATION_MAX_AGE 120 line 58, refusal 773, observe 920,
  observe_screen 974, max_width default 960, patch threshold >6
  line 1015, 32-action cap 1182, _input_line_changed 1023-1076,
  scope refusal 1648/1649, desktop_act 1633+, after-capture
  2083-2091), scripts/first_action.py (attempt_session 183,
  envelope ok 552-563, observe_screen 353 and 661),
  scripts/fastpath.py (152, 195-243), scripts/dom_act.py
  (ground_many_one_shot 240-331, focus_type 425-491, arm_typed_flag
  call 483-484), scripts/zen_dom.py (harvest 905, evaluate 441,
  MutationObserver string 993), scripts/code_exec.py (gate 134,
  32-action cap 187-192, SAFE_BUILTINS 107), scripts/codemode.py
  (SAFE_BUILTINS 37), scripts/cdp.mjs (616 lines, Brave
  debugging-port comment), scripts/overlay.py (613 lines),
  scripts/cursor_session.py (supervise 228),
  scripts/session_remote.py (1601 lines, Broker 463),
  scripts/session_driver.py (180 lines).

## 10. Log

- 06:37 +07 (T+0m): task received. Repo ~/workspace/computer-use-wayland,
  branch todolist-push. Fetched first; HEAD af0fa87, in sync with
  origin/todolist-push.
- 06:37-06:41 (T+0-4m): read all 12 inputs in full (4 breakthrough
  reports, draft adjudication, 4 reviews, 4 cross-responses).
- 06:41-06:44 (T+4-7m): spot checks V-F1 to V-F8. Verified CB report
  landed (2596287); after-image trap still in code (first_action.py
  :661); Broker grep 0 hits; bench on branch but runtime absent
  (PROBE-S2 log); P8 landed closed negative (3790901); P3 NOT-RUN
  (7b1006a); no PROBE-S0/S1/DOMZEN logs; AMEND4 items 5-8 landed
  with defective-test notes; arithmetic re-verified (CB-4 math,
  Wilson intervals, 32-action caps, patch threshold, max_width
  split, zen_dom evaluate, arm_typed_flag call site).
- 06:44-07:05 (T+7-28m): wrote this log. Verdicts: ADOPT 16, MODIFY 21,
  REJECT 3 as stated, in proposal terms across 40 proposals. Blocking
  findings: FRT-B1 to FRT-B7 (CB-EXEC prototype-only, B1 lift reversed,
  A4 rejected as stated, B2 strengthened with bench-runtime gate, P8
  closed, B5 not lifted, plateau a hard gate).
- Next: fetch plus rebase first if the branch moved, commit this file
  only with an explicit pathspec, verify with git ls-remote, report
  to COORD-CLICK-3.
