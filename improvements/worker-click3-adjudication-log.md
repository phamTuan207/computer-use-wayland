# Worker CLICK3-ADJ: JOINT adjudication DRAFT of the breakthrough discussion

Owner: the owner. Role: joint adjudicator (Worker CLICK3-ADJ). I judge from
the evidence in the logs, not from any one reviewer's verdicts. This is a
DRAFT, not the final joint adjudication. See section 7 for what happens next.

Decision criterion (owner standing rule 06:07): judge every proposal by the
accuracy and speed of its FINAL RESULT, never by rewrite size or cost. Cost
(tokens, time, rewrite effort) is IRRELEVANT. A bigger rewrite that wins on
accuracy and speed beats a smaller patch that does not. I apply the same
criterion to the blocking findings themselves: a block must protect accuracy
or speed of the final result, not caution alone. One block fails that test
below (B1) and is lifted on that ground.

Rules honored: no em dash (U+2014) or en dash (U+2013) anywhere in this file.
No personal info. Evidence with every claim. Wall-clock Asia/Ho_Chi_Minh +
elapsed time. Commit with an explicit pathspec immediately after staging,
never plain git commit, never git add -A. Verify push with git ls-remote.
Never ydotool. This is an adjudication, not my own work, so no self-healing
question arises. I did not edit AMEND4's files and I did not touch other
workers' uncommitted changes (scripts/cu.py shows an uncommitted modification
by another worker in this shared tree; I left it alone).

## 0. Log and what I verified myself

- 06:21 +07 (T+0s): task received. Repo ~/workspace/computer-use-wayland,
  branch todolist-push. Fetched first; local HEAD was 2b0c73c at start.
- 06:21-06:23 (T+0-2m): read all 11 inputs in full: ARCH-REVIEW
  (improvements/worker-arch-review-log.md, 074c1d7), GROUNDING-REVIEW
  (improvements/worker-grounding-review-log.md, d1fc4e9), SPEED-REVIEW
  (improvements/worker-speed-review-log.md, a4ecb49), D1
  (improvements/worker-click3-d1-review-log.md, 37f457e), D2
  (improvements/worker-click3-d2-review-log.md, 6d1bf04), D3
  (improvements/worker-click3-d3-review-log.md, 14fc139), RTD
  (improvements/worker-click3-rtd-review-log.md, e96b2ff), X1
  (improvements/worker-click3-x1-response-log.md, 0cf601c), X2
  (improvements/worker-click3-x2-response-log.md, d5b205d), X3
  (improvements/worker-click3-x3-response-log.md, 2b0c73c), XRT
  (improvements/worker-click3-xrt-response-log.md, 6cb3f95).
- 06:23-06:24 (T+2-3m): spot checks of my own (section 0.1). The branch
  moved during this work: AMEND4 item 3 landed as 62b740e while I read.
  I fetched again before writing; HEAD at writing was 62b740e, then
  item 4 landed as 72120aa and I re-fetched before commit; HEAD at
  commit is 72120aa.
- 06:25 +07 (T+4m): wrote this log.
- 06:26 +07 (T+5m): re-fetched before commit; the branch had moved again
  (item 4 landed as 72120aa). Updated V-A2 and sections 2, 4, 5 for the
  new landed state.

### 0.1 Spot checks run by me in this session (new verification, not trust)

- V-A1. CODEX-BREAKTHROUGH is still PENDING. The file
  improvements/worker-codex-breakthrough-log.md is an untracked 17-line,
  1805-byte launch stub: Codex PID 781223 launched 06:04:15 on the laptop,
  monitoring check 1 at 06:19:50 (log 1065280 bytes, report file NOT yet
  written, Codex in write-up phase). No report, no proposals. I invent
  none of its proposals. It is PENDING in section 1 and its follow-up
  round is specified in section 7.
- V-A2. AMEND4 landed state on todolist-push at HEAD 72120aa: item 1
  landed (cc964b2, geometry, one unit system), item 2 landed (c1ea773,
  gate traversal, shared find() with frame + shadow recursion), item 3
  landed (62b740e, band y field-anchored via y_range + grounded_y_range
  + type_y_ranges), item 4 landed DURING this adjudication (72120aa,
  thread type_x_ranges + type_y_ranges through CLI act, CodeExecBackend.act,
  first_action fallback). Item 4's commit message records that
  BrowserAdapter does not exist, which narrows the P2 collision surface
  as B5 stated it: the real paths are the CLI act path,
  CodeExecBackend.act, and the first_action fallback, not a
  BrowserAdapter.act that does not exist. The collision was real for
  the paths that exist. Item 12 is in flight on two lanes (Codex
  amend4-codex + VM CLICK3-AMEND4). Items 2-4 landed satisfies the
  second limb of the B5 lift condition; see section 5.
- V-A3. The 2-vision benchmark is still absent from the local
  todolist-push working tree (ls tests/two_vision_bench.py: no such file).
  Any gate that runs it must first bring it onto this branch.
- V-A4. Y1b BLOCK is real and current: commit 9d9bd63, "Y1b verdict
  council 3: OVERALL Phase A BLOCK on 84b88bb (14/20, 3 real fails,
  2 probe artifacts)". No later commit unblocks Phase A in the record
  (XRT V-X2 confirms the same through the verdict file and later Y1b
  commits 7e6262f and e8fad29).
- V-A5. V11 MutationObserver wording (disagreement (f)): observer code
  EXISTS in scripts/zen_dom.py. arm_typed_flag is defined there and its
  body installs a trusted-input-event listener plus a MutationObserver
  (const obs=new MutationObserver, observing the field). It is also
  CALLED from production code: scripts/dom_act.py:433-434
  (if hasattr(session, 'arm_typed_flag'): session.arm_typed_flag(selector)).
  RTD's phrasing "the production V11 MutationObserver flag is an open
  TODO" is therefore NOT adopted as phrased. The remaining open question
  is narrow: whether the production code-exec path reaches that call for
  every type action. That confirmation belongs to the P5 implementer; it
  is not load-bearing for the P5/A8 verdicts or for benchmark scoring
  (section 2, item (f)).
- V-A6. The S0 numbers are settled and I take no new probe: fresh SSH
  4.43-5.29s (SPEED, D1, D2, D3, RTD, 7 samples), multiplexed 0.91-1.46s
  (D1 n=3 rc=0 with master verified alive, D3 n=8, 11 samples pooled,
  XRT V-X9). SPEED's 0.01s / 460x does NOT reproduce and is dead. The
  corrected saving is about 3.2-3.5s per connection, about 3.5-5x.
- V-A7. The after-image scope trap is proven from source by all four
  reviewers and I accept their concordant reading: first_action.py:656
  hardcodes cu.observe_screen for the envelope after-image, overwriting
  desktop_act's scope-matching after-capture (cu.py:2083-2091).

### 0.2 Facts all four cross-responses now agree on (the settled base)

- SPEED 460x is dead; S0 stays ADOPT on corrected numbers (section 1).
- Y1b BLOCK is real; S2 needs the fixture bench run plus the 3 Y1b real
  fails fixed before any live flag flip (B2 STANDS).
- The 2-vision bench has never run, even in fixture mode; the fixture run
  is a required first rung.
- The Broker exists but nothing in first_action.py or cu.py references it
  (grep 0 hits, verified by X1/X2/X3); S1 is a build, not a switch.
- The P2/AMEND4 collision is real (item 4 threads type_x_ranges through
  the CLI act path, CodeExecBackend.act, BrowserAdapter.act; item 2
  rewrites the same check functions); P2 waits (B5 STANDS, narrowed).
- Vision is the proven error source (E2 17/29 first-try, 58.6%; G30 64px
  and 75px misses; G31 45px eyeball error), never a coordinate failure
  (pointer error 0.5-0.9px, 29/29 clicks executed). DOM grounding is
  single-source (clone2 batch 7: 66 rects, Marionette median 0.030s;
  C1 applies: three reviews citing one measurement is one measurement,
  not three).
- AMEND4 CONTINUES, slower, per the owner 06:09 TWO TRACKS rule. All four
  cross-responses agree; no reviewer proposes pause, redirect, or stop.

## 1. Per-proposal verdict table (every row covered, none skipped)

Legend: ADOPT means do it as proposed. MODIFY means do it with the stated
change; the gating conditions attached to each MODIFY are what must be proven,
by whom, before it proceeds. REJECT means do not do it (no proposal is
rejected in full; two parts inside merged rows are rejected and are named).
PENDING means the input has not landed. Exact duplicates are merged into one
row citing every source. Coverage: 24 rows covering all 30 proposals:
ARCH A1-A10 (10 rows), GROUNDING P1-P9 (8 rows, P4 merged into A7),
SPEED S0-S3 plus six deletions (5 rows, D1 merged into S0, D2 into A6,
D3 into S1, D4 into A7, D5 into S2), CODEX-BREAKTHROUGH (1 row, PENDING).

Tally in proposal terms: ADOPT 15 (A2, A6, D2, A7, P4, D4, A9, A10, P1, P3,
P6, P8, P9, S0, D1), MODIFY 14 (A1, A3, A4, A5, A8, P2, P5, P7, S1, D3, S2,
D5, S3, D6), REJECT 0 in full, PENDING 1 track (CODEX-BREAKTHROUGH).

### 1.1 ARCH (worker-arch-review-log.md, 074c1d7)

| ID | Proposal | Verdict | Evidence, reasoning, and gating conditions |
|----|----------|---------|---------------------------------------------|
| A1 | Layer 0 persistent driver daemon (snapshot/execute/verify, structured-first) | MODIFY | Direction right: structured state is exact and cheap, and a state-holding driver is the only shape that stops paying setup per action. But the full-replacement claim has no existence proof (RTD C2, accepted by X1/X2/X3): session_driver.py runs cu.main() per command, code_exec.py is an in-process program model not a daemon, dom_act.py still grounds through image points, cdp.mjs drives agent-managed Chromium only, the bench is unrun. "Exists" means a file exists, not that the composition works. Gating conditions: a staged prototype must prove snapshot/execute/verify end to end on one live ws2 clone chat before anything is deleted (B6 lift, section 5). The prototype design must cover the single-runner lock as a task lock, pill visibility, the one-session-per-browser constraint, daemon crash and stale-state behavior, session-holding scope (RTD C5: holding the single Firefox session blocks every other tool for the task duration), and lifecycle across laptop sleep and reboot. No deletions until then. Note on labels: XRT softens RTD's MODIFY to ADOPT staged; X1/X2/X3 keep MODIFY. Substance is identical; I keep MODIFY because the proposal as stated (full replacement) is not adopted as stated. |
| A2 | Layer 1 pixels demoted to fallback-only, pixel-band labeled weak | ADOPT, with sequencing constraint | Proven by V1 (vision 58.6% first-try) and V3 (the code itself admits the band is necessary, not sufficient, cu.py:1023-1076). Constraint, from RTD and accepted by all four cross-responses: demote only after the router (P1) and its fallback trigger are proven; Zen chrome UI stays pixel-primary until P8 proves a structured path, because today pixels are its only perception (AT-SPI cannot see Zen, C12 probe). Without that constraint A2 strands Zen chrome tasks. Fallback stays for canvas, games, video, Zen chrome UI. |
| A3 | Delete session supervisor tree | MODIFY | Direction right, timing conditional. The tree's real jobs are a named killable scope, cancel/stop, the session pill label, and the single-runner lock. Gating condition: delete only when the driver demonstrably holds scope plus cancel latch plus lock on a live run (B4 lift, section 5). Until then the supervisor is the lock holder, and deleting it risks two live runners and loses the cancel/stop path. The F1 failure cluster is partly environment faults, not supervisor-design faults; deleting the tree does not delete those modes. All four cross-responses agree. |
| A4 | Delete overlay daemon server (keep pill visibility) | MODIFY | The server is real (overlay.py 613 lines, Unix-socket server with holder accounting) and per-batch overlay acquire (315-349ms) is a genuine tax, so the end state (delete the server) is right. But the pill is the owner's only visibility into live runs and both replacements are unbuilt. Gating conditions, in sequence: (a) session-level pill first, acquire once per task, server KEPT, measured (this removes the per-batch tax without touching visibility); (b) driver-owned pill (or compositor-plugin indicator) only with proof it shows and clears, including no stale or missing pill when the driver dies mid-task; (c) delete the server only then (B3 lift, section 5). Note on labels: RTD originally REJECTED as stated; XRT softens to MODIFY conditional and X1/X2/X3 are MODIFY. The REJECT targeted ARCH's stated form (delete with unbuilt replacements); no reviewer defends that form, so MODIFY is the converged label. |
| A5 | Delete one-shot SSH loop (persistent Broker only) | MODIFY | Persistent-first is right (fresh SSH 4.43-5.29s per connect, corrected S0 numbers). The word "only" is REJECTED: the VM reaches the relay only through SSH, so this is not deletion of SSH but deletion of one-shot SSH in favor of multiplexed SSH plus broker RPC; and if the broker dies, one-shot SSH is how the relay gets restarted. Gating condition: fresh SSH stays as the documented fallback AND the recovery path. "Only" applies to the default path, never to the recovery path (B4 lift, section 5). Note on labels: XRT softens to ADOPT with fallback retained; X1/X2/X3 keep MODIFY. I keep MODIFY because the proposal's operative word is rejected. Substance is identical across all four. |
| A6 + D2 | Delete file-based observation/action IPC (A6) / delete scp for JSON files (D2) | ADOPT for transport | JSON over the persistent channel (or in-process calls) replaces scp per step; each scp costs a fresh about 5s SSH. Scope condition, recorded by all four cross-responses: files stay as the audit and evidence trail (persisted observation artifacts, JSON plus JPEG, written by the driver); what dies is files as the transport, not files as the record. The JPEG still travels for the human VISION 2 check until the persistent channel carries bytes. Keep file IPC only as the fallback transport when no Broker is reachable. Note on labels: XRT calls A6 MODIFY on the same substance (claim as stated overbroad); D1/D2/D3 call it ADOPT with the audit condition. I record ADOPT with the scope condition, since the condition is a scoping note on the transport change, not a redesign. |
| A7 + P4 + D4 | Act-now after-image scope fix (A7) / after-image scope fix, both fields (P4) / delete screen-scope after-capture as produced today (D4) | ADOPT the both-fields shape; the delete-entirely half is REJECTED | Proven defective by construction (V-A7, first_action.py:656). The adopted shape, triple-sourced plus AMEND4 item 12: return BOTH after (scope-matching, chainable) and after_screen (full monitor, verification only, documented non-chainable); move the scope check before the overlay attempt; add a regression test. Execution is DEFERRED to AMEND4 item 12, already in flight on two lanes; the rewrite track consumes it and does not duplicate it. REJECTED part: deleting the envelope after image entirely (ARCH's delete half, and D2's withdrawn alternative). It loses the human-visible evidence and the frame-change signal for a saving of about 0.25s, which is noise; that trade fails the 06:07 criterion on accuracy. Timing note, from D3 and accepted by X1/X2/X3/XRT: the scope-as-capability refusal deletion (cu.py:1648/1649, screen observations refuse key/type) is sequenced WITH P2, not with this fix. While actions are still pixel-addressed, the refusal protects typing against a screen observation; once actions are element-ref addressed, scope is irrelevant and the refusal can go. |
| A8 | Delete pixel-band verification for structured targets | MODIFY, sequenced behind P5 | Direction right: the band is admitted necessary-not-sufficient and the DOM value check is sufficient and 100-1000x cheaper (0.002-0.015s). Gating condition: delete band-as-pass-signal only where the per-action DOM assert exists and is mandatory; until then the band stays as a diagnostic. Deleting before the assert set exists leaves actions with NO verification, which is worse than weak verification. This is RTD's sequencing, accepted by X2/X3 and by X1 in substance (X1 keeps ADOPT with the same condition added). The P5/A8 change rests on the verified opt-in-hooks ground (focus_check and type_check are still optional hooks, D1 V13), not on RTD's V11 TODO wording; see section 2 item (f). |
| A9 | Coordinate model to one system (CSS px element rects, converted once at the driver edge) | ADOPT for structured targets | The five-frame tower has five proven bug sites (F2b-1, C12, amend3 step 5, G28, after-scope trap); the one-conversion path already exists (fastpath.dom_rect_to_screen_point, verified). Dependency, accepted by all four cross-responses: A9 depends on AMEND4 items 5-6 landing (origin staleness), and the one conversion still needs a correct absolute viewport origin and scale factors re-read per ground (C12 proved window-relative vs absolute origin is a live trap). The pixel fallback keeps its own frame internally; the router decides. Item 1 (geometry, one unit system) already landed (cc964b2) and is the prerequisite. |
| A10 | Acceptance test becomes 0-vision live benchmark on real ws2 clone chats | ADOPT as staged | Final gate: live 0-vision on real ws2 clone chats (clone1 Brave plus clone2 Chrome), DOM harvest, plan, execute, DOM verify, zero screenshots in the machine loop, accuracy at least 90% scored by DOM outcome (V12 sent-bubble gate), total wall time end to end including transport, one final screenshot kept as unscored human evidence (P9), owner approval per run. Staging: fixture 2-vision first (it has never run), P3 first (the live run needs the CDP path). The live-2-vision intermediate rung GOES as a hard gate and is kept only as a diagnostic; see section 2 item (a) and section 3 for the full reasoning. B1 is LIFTED (section 5). |

### 1.2 GROUNDING P1-P9 (worker-grounding-review-log.md, d1fc4e9)

| ID | Proposal | Verdict | Evidence, reasoning, and gating conditions |
|----|----------|---------|---------------------------------------------|
| P1 | DOM/a11y default router (Zen Marionette/BiDi, Chromium CDP, AT-SPI, screenshot last; encoded in code, not convention) | ADOPT | Two perception stacks with no routing rule drift to the worse one (works everywhere) instead of the better one (needs setup). Implementation requirements, accepted by all four cross-responses: encode the router in code as one function returning the perception source; fail closed to the labeled screenshot fallback; a per-target routing table proven per target before the default flips; a log line on every routing decision, so drift back to screenshots is visible instead of silent. Note: the a11y branch is thin for the apps in play (AT-SPI cannot see Zen; AT-SPI numbers unverified on this VM), so it mostly covers native apps that are not the live workload. Interim honest state: Brave tasks still route to screenshots until P3 lands. |
| P2 | Element-ref action interface rewrite (live rect re-read at execution, screen-point action form, delete dom_rect_to_image_point from the live path) | MODIFY | Direction right and highest-leverage code change after P3: the round trip exact DOM rect to exact screen point to lossy image point and back is proven wasteful from source (fastpath.py:195-243, dom_act.py:312, cu.py:1000-1005), and it deletes the F2b-1, C12, amend3-step-5 bug class. Gating conditions (B5, section 5): (a) the stale-ref disagreement protocol is specified first (what happens when a live rect re-read disagrees with the plan: refuse, re-plan, or click stale, per case; lifecycle across a multi-action plan); AND (b) AMEND4 items 2-4 have landed (SATISFIED at HEAD 72120aa: item 2 c1ea773, item 3 62b740e, item 4 72120aa). P2 starts only when (a) is met; the landing limb is already satisfied, so the protocol is now the single outstanding gate. Running P2 in parallel with AMEND4 items 2-4 would have guaranteed merge collisions on the same functions; that risk is closed by the landing, not by the protocol. Delete dom_rect_to_image_point from the live path (keep for tests and legacy). The scope-as-capability refusal deletion lands in this step (see A7 row). |
| P3 | Brave relaunch with debugging port (controlled experiment, quiet window, never mid-batch; fallback agent-managed Chromium) | ADOPT as a controlled experiment | Single highest-leverage unblocker: the clone chats live in Brave, Brave holds no debugging port on its default profile (cdp.mjs comment verified verbatim), so the CDP path cannot reach them today. Conditions, accepted by all four cross-responses: quiet window owned by the coordinator, never mid-batch (clone1 is mid-batch-8 now); verify /json/list shows the Muse tab and login intact; run observe plus harvest plus one fill plus assert on a scratch input. Recorded additions: CDP on port 9223 exposes the logged-in browser to any local process (security consideration, never mentioned by GROUNDING); the Chromium fallback is a migration with re-login and clone reconfiguration, not a fallback, and needs its own login-persistence check before it is relied on; cdp.mjs notes shadow-DOM elements have null box_model, and Messenger's DOM shape against that gap is unexamined. BLOCK on any live-task migration until the experiment passes. If P3 fails (Brave refuses the port and the Chromium migration is too disruptive), the DOM-first live path loses its highest-leverage unlock and the whole program re-plans around Zen Marionette only; report that plainly, not worked around silently. |
| P5 | DOM verification mandatory (focus_check and type_check required, not optional hooks; CDP fill read-back and assert polling the model) | MODIFY | Direction right; the code admits the band is insufficient. The blanket mandate is BLOCKED as stated: the assert set does not exist for every action type (focus_check/type_check are still optional hooks, D1 V13), and no per-action exception list exists. Gating conditions: DOM verification becomes mandatory PER ACTION TYPE as its assert lands; an explicit per-action exception list names the actions where DOM assert is impossible (scroll position, hover state) and pixel stays the only signal; the band stays as a diagnostic until then. A blanket mandate now means false refusals on working flows or vacuous asserts (false confidence). The V12 sent-bubble gate in the benchmark is the pattern. This MODIFY is converged across all four cross-responses (X1/X2/X3 MODIFY; XRT MODIFY with BLOCK on the blanket version). |
| P6 | Measure the vision call | ADOPT, with specification fix | Cheapest item on the list and a precondition for honest speed claims: capture is 15-30ms and DOM rects 0.030s, but the model read that locates the target is seconds and timed nowhere. Bundle with S0. Specification fix, from RTD and accepted by all four cross-responses: the model call happens in the calling agent's loop, outside cu.py, so the proposal must specify the timestamp points (observation delivered to the agent vs located target returned) and the owner of the logging (the harness, not cu.py), or it will be recorded as done when only capture timing is logged again. Until that number is in the logs, every speed claim about the screenshot path is incomplete, and nobody may claim the 10s target is met. |
| P7 | Session handover protocol (one protocol per browser per task phase, BiDi ground then Marionette input or stay on one) | MODIFY | The one-session constraint is proven (4 runs, Firefox allows exactly one remote session per instance), so a protocol is needed IF a task genuinely needs two protocols. Gating condition: first answer whether Marionette-only suffices (the benchmark already runs Marionette-only, harvest plus input, and zen_dom harvest IS Marionette). Write the handover protocol only if a task genuinely needs BiDi for grounding plus Marionette for input. Price noted: a handover costs 4-7s per switch (BiDi new 1.51-2.77s fresh, Marionette attach 2.65-4.12s), comparable to the SSH tax being deleted. Small and non-blocking either way. All four cross-responses converge on MODIFY. |
| P8 | Zen chrome Marionette context test (set_context chrome) | ADOPT as a bounded, time-boxed, low-priority probe | Premise verified (V12: no chrome-context support in zen_cli.py today). If it works, the last screenshot-only surface falls; if blocked without a restart, keep screenshots ONLY for chrome UI and record that boundary explicitly. Conditions: quiet window with owner-approved Zen restart; the one-session constraint in the test design (chrome context plus content session cannot both be live); do not gate anything on it; do not let it become a rabbit hole. AT-SPI cannot see Zen, so that path is closed; do not spend more time on it. |
| P9 | Keep one screenshot for the human (VISION 2 stays, machine scores by DOM) | ADOPT | Correct division: screenshots are a human evidence channel, not a machine perception channel. VISION 2 stays as unscored human evidence; the machine scores by DOM outcome. Wording correction, from RTD and accepted by all four cross-responses: VISION 2 is the agent looking at the threads and reporting to the human, not the owner looking directly, so it is the agent's final sanity check reported to the human. Cost is about 0.25s plus one vision read, noise against the total. Attached to A10. |

### 1.3 SPEED S0-S3 plus six deletions (worker-speed-review-log.md, a4ecb49)

| ID | Proposal | Verdict | Evidence, reasoning, and gating conditions |
|----|----------|---------|---------------------------------------------|
| S0 + D1 | Step 0 persistent SSH multiplexing, do now (S0) / delete fresh SSH per call (D1) | ADOPT on CORRECTED numbers | Fresh SSH 4.43-5.29s (7 samples, confirmed four ways); multiplexed 0.91-1.46s (11 samples, rc=0, master verified alive). Saving about 3.2-3.5s per connection, about 3.5-5x, NOT 460x and NOT 0.01s. SPEED's 0.01s figure matches a failed-fast connection (master not up, rc=255, D1's diagnosis, accepted by RTD and D3); SPEED's log records no return codes and no master-liveness check. Corrected expectation: per act-now (3 connects) about 16s becomes about 5-6s, not about 2s; per observe (2 connects) about 6-8s saved. SPEED's 1.6x per-task estimate was built on 0.01s and must NOT be quoted; D1's revised roughly 1.3-1.4x on a CL2-MSG-class task is the working figure until a recompute on the corrected numbers. Conditions: implement the fallback explicitly (any multiplex failure falls back to a fresh connect, slow but correct); log master death; per-socket watchdog, not global (a half-dead master can hang rather than fail cleanly; ControlPersist=600 can leave a stale master holding a dead Tailscale route); the 1-day soak test runs IN PARALLEL, advisory, not a gate (section 6). The residual about 1.1-1.2s per call (per-session sshd and shell setup, which multiplexing does not remove) is itself an argument for S1 and A1. Do it now: no agent-logic code change, fallback safe. |
| S1 + D3 | Step 1 act-now over the persistent relay broker (S1) / delete per-batch session spawn (D3) | MODIFY, proof-first | Direction right: the per-batch session spawn is a real tax (0.4-2.1s) plus a real failure mode (20s deadline, timeout never falls back, council 1 B1), and JSON over the same channel kills the scp round trips. But S1 is a BUILD, not a switch: the relay is alive (PID 1821, socket exists, verified) yet zero references to session_remote or Broker exist in first_action.py or cu.py (grep 0 hits, verified by X1/X2/X3), so the broker path from the VM is unproven end to end, and the single-owner socket semantics under concurrent VM workers are unexamined (serialize or refuse). Gating conditions: prove one live batch end to end over the broker from the VM first, then delete the per-batch spawn; keep the spawn as fallback until proven. Session-level pill (keep the overlay server) lands in the same step. Expected per-batch mechanism about 0.5s plus the overlay item after S1. All four cross-responses converge on MODIFY. |
| S2 + D5 | Step 2 DOM-first plus code-exec plus checkpoint verification, CU_CODE_EXEC=1 on (S2) / delete per-action model call as the default (D5) | MODIFY, gated | The 10x path, already built and merged (code_exec.py 880 lines, Pick 1 winner, commits 714e4f9, 84b88bb, 2e2aeff, merge 453adc4), and the flag is OFF in the live path (verified live: CU_CODE_EXEC unset on the laptop). But the blanket flip is BLOCKED (B2, section 5): Y1b council 3 BLOCKED Phase A on 84b88bb with 14/20 probes passing and 3 real fails (1e f-string chr NameError; 2a codemode wall preemption, error raised only after the C loop finished; 2b code_exec wall preemption, elapsed 6.20s, ok=True with NO error, silent success), and the named gate (2-vision benchmark) has never run. A fixture bench pass alone does not fix the 3 real fails. Gating conditions, in order: (a) run the fixture 2-vision bench green; (b) fix the 3 Y1b real fails; (c) flip the flag for ONE live task class (clone chat sends) with act-now as fallback, measure, then expand. The "10x path" label is corrected to 3-5x on unmeasured model inference time (SPEED's own honest limit: 30-60s if vision reading dominates); the mechanism can be about 1s, the model is the remaining unknown, and P6 must measure it before anyone claims the 10s target. Code-exec becomes the default for the proven task class first; the stepwise loop stays the fallback for unknown shapes only. |
| S3 | Step 3 laptop-side task runner, only if Step 2 plateaus | MODIFY, fold into A1; plateau defined numerically first | S3 substantially overlaps A1: a laptop-side runner that grounds, acts, and verifies locally and streams back compact state IS the A1 driver daemon approached from the other side. One design decision, not two builds; do not build a separate runner alongside A1. Gating condition: the plateau criterion must be defined NUMERICALLY BEFORE the S2 flip starts (threshold, run count, decision owner), so the trigger is not argued later. An undefined plateau either never triggers or triggers on one bad run. The decision itself happens only after steps 0-8 of section 2 are measured. Open condition with owner: section 6. All four cross-responses agree on the merge and on the numerical definition; none of the councils supplied the numbers, so this draft specifies the form, the owner, and the deadline, not invented numbers. |
| D6 | Delete 120s freshness window as a gate on DOM work | MODIFY, scoped | For DOM-grounded work, re-read the DOM (0.030s) instead of refusing for staleness; the window is a patch for vision coordinates, not a law. Correction, from RTD and accepted by X1/X2/X3: the refusal at cu.py:773 also guards against future-clock observations, and a blanket delete removes the clock-skew guard. Gating condition: keep the future-clock refusal, drop only the age refusal for DOM paths. Keep the window for pixel-addressed work, where staleness is real and the refusal protects against acting on a dead frame. Note on labels: X1/X2/XRT say ADOPT for DOM paths with this correction recorded; X3 says MODIFY scoped. I keep MODIFY because the proposal as stated (blanket delete on DOM work) is changed by the correction. Substance is identical across all four. |

### 1.4 CODEX-BREAKTHROUGH

| ID | Proposal | Verdict | Evidence and reasoning |
|----|----------|---------|------------------------|
| CB | All proposals | PENDING | Report NOT landed at adjudication time (V-A1: untracked 17-line launch stub, 1805 bytes; Codex PID 781223 launched 06:04:15, monitoring check 1 at 06:19:50 records the report file NOT yet written, Codex in write-up phase). I invent none of its proposals. Follow-up round (section 7): when the report lands, its proposals get a full verdict round against the same criterion (06:07) and against this draft's blocking findings, especially whether it independently re-measures anything or also cites clone2 batch 7, F2b, and E2 second-hand. Its arrival is NOT a tie-breaker by default: a fourth reading of the same evidence base is still the same evidence base (RTD C1, accepted by X1/X2/X3/XRT). If it lands after the final joint adjudication, its proposals get their own verdict round; they are not rubber-stamped into the final. |

## 2. Order of work (numbered sequence with explicit gates)

Every step is independently verifiable, every step lands a measured win
before the next step starts, and no step depends on a bet (P3, P8, S2
measurement) that has not yet paid off. Cost is irrelevant by the
criterion, but sequencing by dependency is not cost, it is correctness:
a daemon built from unproven parts inherits their failure modes.

0. S0 plus P6, now. Persistent SSH multiplexing with explicit fallback,
   master-death logging, per-socket watchdog; P6 vision-call measurement
   with the timestamp points and harness owner specified in section 1.
   Gate to step 1: fallback explicit and watchdog in place. The 1-day
   soak test starts the same day and runs IN PARALLEL, advisory, not a
   gate (a master death falls back to fresh SSH, slow but correct).
1. AMEND4 continues in parallel, slower, per the owner 06:09 TWO TRACKS
   rule (section 4). Item 12 (A7/P4) lands via the in-flight run; verify
   the regression test. Gate: the rewrite track makes no parallel edits
   to the same functions AMEND4 is working on (the two tracks run in
   sequence per item on shared files, not in parallel on the same
   functions, or the merge will collide).
2. P3 Brave relaunch experiment plus P8 Zen chrome probe, in a real quiet
   window between clone batches, coordinator-owned, never mid-batch.
   Gate to any live DOM work: P3 passes (login intact, /json/list shows
   the Muse tab, one fill plus assert on a scratch input) or the Chromium
   fallback is proven with its own login-persistence check. No live-task
   migration until then. If P3 fails, re-plan around Zen Marionette only
   and report it plainly.
3. Fixture 2-vision bench run. Bring the bench onto todolist-push first
   (it is absent there today, V-A3). This step does not depend on P3
   (headless Firefox, local fixture) and may run in parallel with step 2.
   Gate to step 6: the fixture run passes. The program's gate cannot be
   an unrun script.
4. Fix the 3 Y1b real fails on code-exec (1e, 2a, 2b). Gate to step 6:
   the fails are fixed (B2 lift, part 1). Owner: section 6.
5. P1 router plus P5 asserts per action type. Rewiring of existing hooks;
   P5 per action type as its assert lands, plus the explicit exception
   list. Gate to step 6: the router logs its routing decisions, and the
   P5 assert set covers the S2 task class (clone chat sends). See item
   (b) below for why this step precedes the S2 flip.
6. Define the numerical plateau (coordinator, before the flip; section 6),
   then the S2 flip for ONE live task class (clone chat sends) with
   act-now as fallback. Measure model-call count and wall time.
   Gate to expansion: measured on one class; expand only on measurement.
7. P2 element-ref interface rewrite, after B5 lifts (stale-ref protocol
   specified; items 2-4 landed limb satisfied at HEAD 72120aa). A9 one-system coordinates land in this
   step (depends on AMEND4 items 5-6). The scope-as-capability refusal
   deletion lands in this step, not with A7. Gate to step 8: P2 proven on
   the S2 task class with DOM verification mandatory.
8. S1 broker path proof from the VM on one live batch, then delete the
   per-batch spawn. Session-level pill (server kept) in the same step.
   P7's Marionette-only question is answered before any handover protocol
   is written. P8 probe runs any time it fits. Gate to step 9: one live
   batch proven end to end over the broker from the VM.
9. A1/S3 merged daemon/runner decision, only after steps 0-8 are measured
   and the plateau definition is applied. The prototype must prove
   snapshot/execute/verify end to end on one live ws2 clone chat
   (B6 lift). Gate to step 10: prototype proven.
10. A3/A4/A5 deletions last, each gated on its replacement proving (A3:
    driver holds scope plus cancel latch plus lock; A4: session-level
    pill measured, then driver-owned pill crash proof, then delete the
    server; A5: broker proven on the VM path with one-shot SSH kept as
    recovery).
11. Acceptance: fixture 2-vision (step 3), then live 0-vision on real ws2
    clone chats as the final gate (section 3), after P3 and P2. Live
    2-vision is a diagnostic only if the live 0-vision run fails.

### 2.1 Settled residual disagreements

(a) A10 live-2-vision rung stays or goes. GOES as a hard gate; kept only
as a diagnostic. X1/X2/X3 include the rung in their ladder; XRT argues
it adds nothing measurable because VISION 1 is already a DOM harvest and
VISION 2 a human look. I settle with XRT, on the evidence, not on vote
count (C1: agreement is not independent confirmation). In the bench
design VISION 1 is a DOM harvest, not a screenshot, and VISION 2 is a
human look at the threads; the machine never locates from pixels in
either form. Live 2-vision and live 0-vision-with-P9-screenshot are the
same machine behavior; they differ only in whether the human looks at
live threads or at a screenshot, and the P9 screenshot IS the human
outcome check in the 0-vision run. The councils' stated purpose for the
rung ("the live 2-vision run is the proof that DOM works on real
Messenger pages") is served equally by the live 0-vision run itself,
which also runs DOM on real Messenger pages and scores by DOM outcome.
The extra run buys replication and localization, not a distinct proof,
and under the 06:07 criterion a gate must protect accuracy or speed
measurably. The V11-observer limb of B1 is also conceded as
non-load-bearing for benchmark scoring: the bench scores by the V12
sent-bubble gate, not through the production V11 flag (XRT section 3,
accepted). The rung is retained as a diagnostic: if the live 0-vision
run fails, the team may run live 2-vision to localize (script vs DOM
path), but it is not a required rung. A10 verdict: ADOPT as staged
(section 1).

(b) Ordering: S2 before vs after P1/P5. P1/P5 go BEFORE the S2 flip.
X1 puts P1/P5 alongside the gated S2; X2 puts S2 before P1/P2/P5; X3
puts P1/P5 before S2 because S2's checkpoint verification IS P5; RTD
puts the fixture bench plus Y1b fixes first. I settle with X3 on the
dependency, and with RTD on the gates. S2 is "DOM-first plus code-exec
plus checkpoint verification", and the checkpoint verification part IS
P5. Flipping S2 without P5 means flipping code-exec while DOM
verification is still optional hooks (D1 V13, first_action.py:597-613),
a window in which the live loop runs code-exec with pixel-band
verification only. P1 (router) and P5 (mandatory DOM verification per
action type as asserts land) are rewiring of existing code with no
collision, so doing them first costs one small step and removes that
window. X2's "S2 before P1/P2/P5" is rejected for P1/P5 but accepted
for P2: the S2 one-class flip does not depend on P2, and P2 is
collision-blocked until B5 lifts, so S2 precedes P2. X1's "alongside"
is compatible in outcome but I sequence P1/P5 strictly before the flip,
not alongside it, because the verification must exist before the flip
it verifies. Full order: fixture bench run plus Y1b fixes, then P1/P5,
then the S2 one-class flip, then P2.

(c) AMEND4 items 3-4 priority. SPLIT item 3 from item 4 (X3's
refinement). X1 moved both up to second position as the P2
precondition; X2/X3/XRT kept them deprioritized. Item 3 (band
anchoring) stays DEPRIORITIZED in principle: under A8/P5 the pixel band
is a diagnostic, not a success criterion, so perfecting its anchoring
is low value under any outcome. Note the fact has overtaken the
instruction: item 3 LANDED as 62b740e during this adjudication, so the
deprioritization is now moot for item 3; its landed work serves the
diagnostic band, and the kill rule at reconciliation (section 4) still
applies if the rewrite deletes its target. Item 4 (wiring type_x_ranges
through the three paths) is NOT merely pixel-band work: it is the wiring
P2 will replace AND the collision surface P2 must wait for, so it goes
MINIMAL, not gold-plated, sequenced with the P2 decision: if P2 lands
first, item 4 is re-verified against the new code rather than finished
as written. Note the facts have overtaken both instructions during this
adjudication: item 3 LANDED as 62b740e and item 4 LANDED as 72120aa
(whose message records BrowserAdapter does not exist, narrowing the
collision surface to the paths that exist). The deprioritization and the
minimal-cap are now moot in fact; their landed work stands subject to
the kill rule at reconciliation (section 4). The split-3/4 settlement
stands as the reasoning that got us here. Triage going forward: first
5, 6, 7, 8, 12 (items 1-4 done); then 9, 10; 11 anytime.

(d) Numerical-plateau definition for A1/S3. OPEN condition, with owner,
form, and deadline settled and numbers explicitly NOT invented here.
All four cross-responses agree it must be defined numerically BEFORE
the S2 flip; none of them supplied the numbers. Settled: the definition
is owned by the coordinator (COORD-CLICK-3), is set before the S2 flip
(step 6), and has the form RTD specified (Step 2 live median wall time
above a stated threshold for a stated number of runs after the flag
flip), with the coordinator as decision owner. The numbers themselves
are the open item: they are set from the fixture bench plus first live
runs baseline, not guessed in this draft. Until the definition exists,
the A1/S3 decision cannot trigger; an undefined plateau either never
triggers or triggers on one bad run.

(e) Stale-ref disagreement protocol. OPEN, with the B5 narrowed lift
condition settled. The protocol is the missing piece GROUNDING P2 never
specifies (V-X5, XRT): the guard mechanism exists (cdp.mjs 90s plus URL
check, GroundPoints live re-validation) but no decision protocol exists
for the case the live rect re-read disagrees with the plan. Settled lift
condition for B5 (XRT's narrowed form, accepted by X1/X2/X3): the
stale-ref disagreement protocol is specified (refuse, re-plan, or click
stale, per case, plus the lifecycle across a multi-action plan), AND
(AMEND4 items 2-4 have landed OR items 3-4 are deprioritized per the
D1/D3 triage with item 2 landed). Updated reading at HEAD 72120aa
(V-A2): items 2, 3, and 4 have all landed (c1ea773, 62b740e, 72120aa),
so the second limb is SATISFIED and the protocol is now the single
outstanding gate for B5. The protocol writer is named in section 6;
it is due before P2 starts.

(f) V11 TODO wording. RTD's phrasing is NOT adopted as phrased.
X3 verified MutationObserver code exists at zen_dom.py:983 (arm_typed_flag
at :948 in the file X3 read); I verified it again at HEAD 62b740e
(V-A5: arm_typed_flag defined in zen_dom.py, MutationObserver JS string
inside it, and it is CALLED from production code at dom_act.py:433-434).
RTD's "the production V11 MutationObserver flag is an open TODO" is
therefore not adopted as phrased. The P5/A8 change rests on the verified
opt-in-hooks ground instead: focus_check and type_check are still
optional hooks (D1 V13, first_action.py:597-613 wires DOM hooks only
when a selector is given). The remaining open question is narrow:
whether the production code-exec path reaches the arm_typed_flag call
for every type action; that confirmation belongs to the P5 implementer
(section 6) and is not load-bearing for the P5/A8 verdicts or for
benchmark scoring. Line numbers move with the in-flight AMEND4 edits;
cite the function and file, not a frozen line.

## 3. Acceptance test decision

Decision: the acceptance test is a LADDER with two required rungs and one
diagnostic option. The final gate is the live 0-vision benchmark on real
ws2 clone chats. The live 2-vision run is NOT a required rung.

- Rung 1 (required, first): fixture 2-vision benchmark. Headless Firefox,
  local fixture. It has never run at all (BUILD ONLY); the whole
  program's gate cannot be an unrun script. Bring the bench onto
  todolist-push first (absent there today, V-A3). Pass criteria: the
  script's own gates (V12 sent-bubble gate after each message, scoring
  by OUTCOME in the thread DOM, never point-in-box). This rung does not
  depend on P3 and may run as soon as S0 lands.
- Final gate (required, last): live 0-vision benchmark on the REAL ws2
  clone chats (clone1 Brave plus clone2 Chrome). DOM harvest, plan,
  execute, DOM verify, zero screenshots in the machine loop. Pass
  criteria: accuracy at least 90%, scored by DOM outcome (V12
  sent-bubble gate, message in the thread DOM, never point-in-box);
  total wall time measured end to end including transport. One final
  screenshot is kept as unscored human evidence (P9); it must not feed
  the score. Conditions on the live run: P3 closed first (otherwise it
  falls back to screenshots and proves nothing); quiet window with clone
  coordination; owner approval per run (the bench's --live plus
  --confirm-live gates plus plan-URL gate); agreed test messages so the
  clones' working threads are not polluted.
- Diagnostic option (not a rung): live 2-vision. If the live 0-vision run
  fails, the team may run live 2-vision to localize (script vs DOM path).
  It is not required before the final gate, for the reasons in section
  2 item (a): the machine behavior is identical in both forms, and the
  P9 screenshot supplies the human outcome check.

What the fixture run does NOT prove, recorded as a gap not papered over:
a fixture pass alone repeats the F1a/F2b pattern (pass on the exercise,
unproven on the real task). The live run is the proof the fixture cannot
give, because the real tasks fail on Brave on ws2, where the DOM path
does not reach yet (P3).

## 4. AMEND4 sequencing

CONTINUE, slower, per the owner 06:09 TWO TRACKS rule. Do not pause,
redirect, or stop. All four cross-responses agree, and the owner rule
answers the question directly: the team debates directions while the
fix/improve-current track keeps going, but slower and more carefully to
save tokens, because no direction is confirmed best yet.

- Why continue: items 1-6 fix the geometry and traversal the rewrite
  builds on (item 1 is the prerequisite for A9; items 5-6 fix the origin
  staleness A9 depends on); item 12 IS the A7/P4 fix all three reviews
  agree is proven-needed; stopping wastes the in-flight Codex run and
  leaves known-broken behavior (geometry units, after-image scope) in
  the live loop the clones use today; the rewrite is not adjudicated
  final yet, so there is no adopted direction to redirect into.
- Agreed triage order: first items 5, 6, 7, 8, 12 (items 1-4 done);
  then items 9, 10; item 11 (doc fix) any time. The split-3/4 settlement
  in section 2 item (c) is the reasoning that got us here; its
  instructions are now moot in fact because items 3 and 4 landed during
  this adjudication.
- Kill rule at reconciliation: items the rewrite deletes get killed.
  The round-3 council records per item whether the fix is a patch on a
  defective design or a real redesign, and defers or kills any item the
  adopted rewrite replaces wholesale, rather than finishing it. An item
  the rewrite subsumes is verified against the new code, not assumed
  gone. (D3's reconciliation discipline, accepted by X1/X2/XRT.)
- B2/B5 findings go into the round-3 review: the Y1b 3 real fails (B2)
  and the P2 collision plus stale-ref protocol (B5) are fed into the
  AMEND4 round-3 council, which judges patch vs rewrite per item under
  the 06:07 criterion. (RTD's feed-in, accepted by X1/X2/X3.)
- Landed state observed at HEAD 72120aa: item 1 landed (cc964b2),
  item 2 landed (c1ea773), item 3 landed (62b740e, during this
  adjudication), item 4 landed (72120aa, during this adjudication;
  its message records BrowserAdapter does not exist). Item 12 is in
  flight on two lanes (Codex amend4-codex, VM CLICK3-AMEND4); the
  rewrite track consumes it and does not duplicate it. Item 1 also
  landed on the amend4-codex branch as ddf5673 (per the driver log).
- Pace per TWO TRACKS: fewer parallel workers, smaller batches,
  per-item verification, no new scope. The two tracks run in sequence
  per item on shared files, not in parallel on the same functions.

## 5. Blocking findings, final status

- B1 (A10 straight to 0-vision live on ws2 clone chats): LIFTED by XRT,
  and I adopt the lift. What B1 attacked was A10 as a straight jump:
  fixture proof skipped, human outcome check removed, P3 untested, live
  clone workspaces disrupted. None of the three councils proposes that
  version; all three stage fixture first, condition on P3, require owner
  approval per run, and keep VISION 2 as a human look (P9). The
  remaining RTD-only step (live 2-vision intermediate) adds nothing
  measurable (section 2 item (a)), and the V11 limb is conceded as
  non-load-bearing for benchmark scoring. B1's remaining note (live
  2-vision as a diagnostic) is recorded in section 3, not as a gate.
- B2 (S2/D5 blanket CU_CODE_EXEC=1 flip): STANDS. No council mentions
  the Y1b BLOCK (XRT V-X1: 0 hits for Y1b or 84b88bb in D1, D2, D3);
  the fixture-bench gate does not cover the 3 known real fails. Lift
  condition: fix the 3 Y1b real fails (1e, 2a, 2b), fixture benchmark
  green, then flip the flag for ONE live task class (clone chat sends)
  with act-now as fallback, measure, then expand.
- B3 (A4 overlay daemon deletion without a replacement): STANDS as a
  gate, confirmed by all three councils. Lift condition: a session-level
  pill (acquire once per task, server kept) is measured, and a
  driver-owned pill proves no stale or missing pill on crash.
- B4 (A3/A5 delete-first ordering): STANDS as a gate, confirmed by all
  three councils. Lift condition: the driver proves scope plus cancel
  latch plus lock, and the broker proves on the VM path with one-shot
  SSH kept as recovery.
- B5 (P2 immediate interface rewrite): STANDS, narrowed. Collision limb
  closed by landing: items 2-4 have all landed (c1ea773, 62b740e,
  72120aa), and item 4's commit message records BrowserAdapter does not
  exist, so the collision surface was narrower than B5 stated (CLI act
  path, CodeExecBackend.act, first_action fallback). Stale-ref protocol
  limb unanswered by all three councils and still open. Lift condition
  (settled, section 2 item (e)): the stale-ref disagreement protocol is
  specified AND (AMEND4 items 2-4 have landed OR items 3-4 are
  deprioritized per the D1/D3 triage with item 2 landed). At HEAD
  72120aa the second limb is SATISFIED, so the protocol is now the single
  outstanding gate.
- B6 (A1 full replacement claim): STANDS as a gate, complied with by
  all three councils' sequencing. Lift condition: a daemon prototype
  runs snapshot/execute/verify end to end on one live ws2 clone chat.

## 6. Open conditions and owners

- S0 soak test: owner COORD-CLICK-3 (the coordinator owns the soak
  because it spans workers; X2). The S0 implementer names the per-socket
  watchdog. The soak runs in parallel, advisory, not a gate; a master
  death falls back to fresh SSH.
- P3 quiet window plus rollback: owner COORD-CLICK-3. The window is a
  real quiet window between clone batches, never mid-batch. The rollback
  (relaunch without the flag, Brave session restore, re-login cost)
  is stated BEFORE the window, not after.
- Numerical plateau (A1/S3): owner COORD-CLICK-3. Form: Step 2 live
  median wall time above a stated threshold for a stated number of runs
  after the flag flip, decision owner the coordinator. Deadline: defined
  before the S2 flip. The numbers are set from the fixture bench plus
  first live runs baseline; this draft does not invent them.
- Stale-ref disagreement protocol: writer is the P2 implementer, to be
  named by COORD-CLICK-3 when P2 is staffed. Due before P2 starts; it
  is B5 lift condition (a). Content: refuse, re-plan, or click stale,
  per case, plus the lifecycle across a multi-action plan.
- Y1b fixes (1e, 2a, 2b): owner COORD-CLICK-3 to commission; the fix
  lane is to be named in the follow-up round. No input names an owner
  for this work, so I record it as open rather than inventing one. Due
  before the S2 flip; it is B2 lift condition, part 1.
- P6 specification: timestamp points are named in this draft
  (observation delivered to the agent vs located target returned);
  logging owner is the harness, not cu.py. The P6 implementer lands it
  bundled with S0.
- Residual per-connection cost probe (D1 R2): what exactly costs the
  about 1.1-1.2s even over the master (shell startup, PAM, systemd user
  session setup). Owner: the S0 implementer. It bounds every transport
  design, including the Broker.
- V11 wiring confirmation: the P5 implementer confirms whether the
  production code-exec path reaches the arm_typed_flag call for every
  type action. Open, not load-bearing for the P5/A8 verdicts or for
  benchmark scoring.
- P3 failure re-plan: if Brave refuses the debugging port on its default
  profile and the Chromium migration is too disruptive, the DOM-first
  live path loses its highest-leverage unlock and the whole program
  re-plans around Zen Marionette only. That outcome must be reported
  plainly, not worked around silently.

## 7. What happens next

This is a DRAFT joint adjudication, not the final one. Stated plainly:

- Codex plus fcc discussion rounds follow, with this draft as input.
  Their positions are then incorporated by a finalizer into the final
  joint adjudication. No step in section 2 that depends on a still-open
  condition is authorized by this draft alone; the final adjudication is
  the document that settles the program.
- CODEX-BREAKTHROUGH, when its report lands, gets its own full verdict
  round against the same criterion (06:07) and against this draft's
  blocking findings (section 1.4). Its arrival is not a tie-breaker by
  default.
- The work that does not wait for the final adjudication is the work
  already gated as safe in section 2: S0 plus P6 now, AMEND4 continuing
  slower, the P3 experiment in a quiet window, and the fixture bench
  run. Everything else waits on its gate.

## 8. Evidence index

- ARCH log: improvements/worker-arch-review-log.md (074c1d7).
- GROUNDING log: improvements/worker-grounding-review-log.md (d1fc4e9).
- SPEED log: improvements/worker-speed-review-log.md (a4ecb49).
- D1: improvements/worker-click3-d1-review-log.md (37f457e).
- D2: improvements/worker-click3-d2-review-log.md (6d1bf04).
- D3: improvements/worker-click3-d3-review-log.md (14fc139).
- RTD: improvements/worker-click3-rtd-review-log.md (e96b2ff).
- X1: improvements/worker-click3-x1-response-log.md (0cf601c).
- X2: improvements/worker-click3-x2-response-log.md (d5b205d).
- X3: improvements/worker-click3-x3-response-log.md (2b0c73c).
- XRT: improvements/worker-click3-xrt-response-log.md (6cb3f95).
- CODEX-BREAKTHROUGH launch stub:
  improvements/worker-codex-breakthrough-log.md (untracked, 17 lines,
  1805 bytes; report not landed at adjudication time).
- AMEND4 landed state at HEAD 72120aa: item 1 cc964b2, item 2 c1ea773,
  item 3 62b740e, item 4 72120aa (BrowserAdapter does not exist, per its
  message); item 12 in flight.
- Y1b BLOCK: commit 9d9bd63 (14/20, 3 real fails 1e/2a/2b).
- Bench: tests/two_vision_bench.py on origin/main (868 lines, BUILD ONLY,
  VISION 1 is a DOM harvest); absent from the todolist-push working tree.
- Code refs verified by the reviewers and accepted here: scripts/cu.py
  (observe 920, observe_screen 974, image_point 1000-1005,
  _input_line_changed 1023-1076, desktop_act 1619-2199, scope refusal
  1648/1649, after-capture 2083-2091, OBSERVATION_MAX_AGE 120 at line 58,
  refusal 773, --dom-selector 2717, code-exec subparser 2733, CU_CODE_EXEC
  gate 2770/2793), scripts/first_action.py (attempt_session 183,
  envelope after-capture 656), scripts/fastpath.py (152, 195-243),
  scripts/dom_act.py (ground_many_one_shot 240-331, focus_type 425-491,
  arm_typed_flag call 433-434), scripts/zen_dom.py (harvest 905,
  arm_typed_flag with MutationObserver), scripts/cdp.mjs (616 lines,
  Brave debugging-port comment 227-243), scripts/cursor_session.py
  (supervise 228), scripts/overlay.py (613 lines), scripts/session_remote.py
  (1601 lines, Broker 463), scripts/session_driver.py (180 lines),
  scripts/code_exec.py (880 lines, gate 134).
- Numbers used: fresh SSH 4.43-5.29s, mux 0.91-1.46s, saving about
  3.2-3.5s per connection, about 3.5-5x (460x dead); per act-now about
  16s to about 5-6s; per-task about 1.3-1.4x working figure (SPEED's 1.6x
  not to be quoted); vision 17/29 first-try 58.6%, pointer error
  0.5-0.9px; DOM 66 rects median 0.030s, 5 clicks all landed, verify
  0.002-0.015s (single-source, clone2 batch 7, C1 applies); F2b
  order-to-overlay 12.262s (dispatch 11.620s, 95%); overlay acquire
  315-349ms; tc02-t1 gap 722.955s (87.8%) measured with a local helper,
  no SSH hop in it.
