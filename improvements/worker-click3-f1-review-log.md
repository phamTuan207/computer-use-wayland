# Worker CLICK3-F1: final council reviewer 1 position for the FINAL DECISION round

Owner: the owner. Role: final council reviewer 1, independent. I did not
coordinate with any other participant in this round, I question everything,
including the adjudication draft. This is my position, not a summary of
others. Where I agree with the draft (9d23834) I say so and give my own
reason; where I differ I say so plainly.

Decision criterion (owner standing rule 06:07): the final result must be
the MOST ACCURATE and the FASTEST; cost is IRRELEVANT (tokens, time,
rewrite effort). A bigger rewrite that wins on accuracy and speed beats a
smaller patch that does not. I apply the same criterion to blocks: a block
must protect accuracy or speed of the final result, not caution alone.

Evidence standard (owner 06:34, Lauren Tan standard): every claim carries
real measured numbers (test command, output, commit hash, time log). A
proposal with no measured evidence behind it does not count as feasible.
Where evidence is missing I state it plainly instead of filling the gap.

Rules honored: no em dash (U+2014) or en dash (U+2013) anywhere in this
file. No personal info. Evidence with every claim. Wall-clock
Asia/Ho_Chi_Minh + elapsed time. Commit with an explicit pathspec
immediately after staging, never plain git commit, never git add -A.
Verify push with git ls-remote. Never ydotool. This is a review, not my
own work, so no self-healing question arises.

## 0. Log and what I verified myself

- 06:38 +07 (T+0s): task received. Repo ~/workspace/computer-use-wayland,
  branch todolist-push. Fetched first; local HEAD 2864be4, in sync with
  origin/todolist-push at start.
- 06:38-06:44 (T+0-6m): read all inputs in full: ARCH-REVIEW
  (improvements/worker-arch-review-log.md, 074c1d7), GROUNDING-REVIEW
  (improvements/worker-grounding-review-log.md, d1fc4e9), SPEED-REVIEW
  (improvements/worker-speed-review-log.md, a4ecb49), CODEX-BREAKTHROUGH
  (improvements/codex-breakthrough-report.md, 2596287, 138 lines),
  adjudication DRAFT (improvements/worker-click3-adjudication-log.md,
  9d23834), D1 (37f457e), D2 (6d1bf04), D3 (14fc139), RTD (e96b2ff),
  X1 (0cf601c), X2 (d5b205d), X3 (2b0c73c), XRT (6cb3f95). Then the probe
  logs PROBE-P3 (7b1006a), PROBE-S2 (uncommitted working-tree file at
  read time), PROBE-P8 (3790901, 2864be4).
- 06:44-06:46 (T+6-8m): spot checks of my own (section 0.1). The branch
  did not move during this work.
- 06:46-06:58 +07 (T+8-20m): wrote this log.
- Next: commit this file only with an explicit pathspec, verify with
  git ls-remote, report to COORD-CLICK-3.

### 0.1 Spot checks run by me in this session (new verification, not trust)

- V-F1-1. AMEND4 landed state on todolist-push at HEAD 2864be4, from
  git log: item 1 cc964b2, item 2 c1ea773, item 3 62b740e, item 4 72120aa,
  items 5-6 b44a5ea, item 7 49081aa, item 8 af0fa87. Items 1-8 LANDED.
  Remaining: items 9, 10, 11, item 12 in flight on two lanes. This
  changes the B5 picture from the draft: the collision limb is closed
  by landing, not by triage (section 5).
- V-F1-2. PROBE-P8 ANSWERED (3790901, 2864be4): Marionette chrome
  context BLOCKED without a Zen restart. Exact error HTTP 500,
  "unsupported operation", "System access is required. Start Zen with
  the MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 environment variable set to
  enable it." Session acquire 0.01s, content sanity eval 0.00s (title
  Welcome!, url https://zen-browser.app/welcome/, mozInnerScreenX 240,
  mozInnerScreenY 8, matching C12 exactly, third confirmation of that
  geometry). Env var absent from /proc/496121/environ. C12 reproduced
  live on the same still-running Zen (PID 496121). P8 is CLOSED as a
  probe; its outcome is negative, and the fallback (screenshots ONLY
  for Zen chrome UI, boundary recorded) is now the adopted state.
- V-F1-3. PROBE-S2 (working-tree log, 06:36-06:38 +07): the 3 Y1b real
  fails 1e/2a/2b are STILL OPEN at this HEAD. Code-level re-check: no
  setitimer, SIGALRM, or child-process preemption mechanism in
  scripts/codemode.py or scripts/code_exec.py; "chr" is in NEITHER
  SAFE_BUILTINS list (codemode.py line 37, code_exec.py line 107).
  Bench runtime ABSENT on this VM (no .venv, no selenium, no
  firefox/chromium binary, no tools dir), so the fixture bench cannot
  run as-is; environment setup is a prerequisite, not a bench edit.
  Bench + fixture ARE now on todolist-push (c5311ce, 7f3a70b), unedited
  from origin/main. B2 is therefore NOT lifted, and the fixture gate
  itself has a setup step (section 5).
- V-F1-4. PROBE-P3 NOT-RUN (7b1006a): clone1 batch 9 open since 06:01
  +07 22/11, zero completion evidence at 06:36-06:40, Brave PID 7356
  running and untouched. P3 feasibility is UNDECIDED: no measured
  evidence for or against, and it counts as neither feasible nor
  refuted.
- V-F1-5. F2b dispatch, from improvements/worker-f2b-live-session-log.md
  lines 30, 34-35, 49: ORDER-TO-OVERLAY 12.262s, breakdown dispatch
  11.620s (T_order at VM exec start to T_LAPTOP_START: scp script +
  SSH connect + shell startup), fresh observe 0.233s, Python startup
  0.060s, overlay acquire 0.349s. The 11.620s is a MEASURED lump, not
  an invention: it is dispatch as a whole (scp + SSH connect + shell),
  not SSH-connect alone. Codex (CB-7) is therefore right that no
  record splits the lump, and WRONG to say no record supports the
  dispatch-dominance claim at all. The lump is real evidence for
  dispatch dominance; the split is what is missing.
- V-F1-6. Codex's deployment-divergence claim, checked: scripts/
  first_action.py IS tracked on todolist-push now (git ls-files
  matches it). Codex's "not in the repo" was true at ITS checkout
  (HEAD 4500a18, behind 622 per a remote-tracking ref, unfetched by
  Codex, disclosed). F2b line 20 records md5 match VM vs installed
  for first_action.py (8caff365) and overlay.py (c7e815b5) at that
  time. The divergence Codex saw was checkout staleness, not proven
  installed-vs-repo divergence. CB-9 still stands, because this
  exact confusion (which commit is installed, which checkout was
  read) is what a manifest prevents.
- V-F1-7. CB-4 batch math, recomputed by me: 0.9^20 = 0.1216 (12.2%),
  0.9^32 = 0.0343 (3.4%). Correct. The independence assumption is
  disclosed by Codex as illustration, and the real errors are
  correlated, so the numbers are a bound on the shape of the problem,
  not a measured failure rate. The conclusion stands anyway: per-click
  90% does not mean task 90%.
- V-F1-8. CB-EXEC Wilson bar, recomputed by me: for 96 passes out of
  100, the Wilson 95% lower bound is about 90.2% (center about 0.943,
  half-width about 0.041). So 96/100 is the correct bar for a 90%
  task-success claim at 95% confidence. Codex's figure checks out.
- V-F1-9. Convergence pattern across the round, from the tallies:
  X1 ADOPT 14 MODIFY 12 (26 rows, 7 changes, all ADOPT to MODIFY);
  X2 12 substantive changes, all adding gates; X3 same direction;
  XRT updated tally ADOPT 15 MODIFY 14 REJECT 0 PENDING 1; draft the
  same tally. Every cross-response moved in ONE direction only: ADOPT
  to MODIFY, adding a gate, a sequence, or a proof requirement. No
  reviewer reversed a direction, and no proposal flipped ADOPT to
  REJECT or the reverse. RTD reversed nothing except lifting B1. That
  one-directional convergence is itself evidence: the direction is
  settled, the gates are what was missing.
- V-F1-10. Y1b BLOCK is current: commit 9d9bd63 (council 3, 14/20,
  3 real fails 1e/2a/2b), 7e6262f FINAL BLOCK, e8fad29 (10b/10f must be
  rewritten before Phase B). No later commit unblocks Phase A. D1, D2,
  D3 never mention it (XRT V-X1: 0 hits for Y1b or 84b88bb in all
  three). SPEED mentions 84b88bb once, as a Pick 1 merge commit only.

### 0.2 Facts the whole round now agrees on (the settled base)

- SPEED 460x is dead; S0 stays ADOPT on corrected numbers (fresh SSH
  4.43-5.29s, 7 samples; mux 0.91-1.46s, 11 samples, rc=0, master
  verified alive; saving about 3.2-3.5s per connection, about 3.5-5x).
- Vision is the proven error source (E2 17/29 first-try, 58.6%; G30
  64px and 75px misses; G31 45px eyeball error), never a coordinate
  failure (pointer error 0.5-0.9px, 29/29 clicks executed). DOM
  grounding is single-source (clone2 batch 7: 66 rects, Marionette
  median 0.030s; C1 applies: three reviews citing one measurement is
  one measurement, not three). The DOM bench has still never been
  re-run by any reviewer in this round.
- The after-image scope trap is proven from source by all four
  reviewers plus Codex (first_action.py:656 hardcodes
  cu.observe_screen, overwriting desktop_act's scope-matching
  after-capture at cu.py:2083-2091).
- Y1b BLOCK is real and current; S2 needs the fixture bench run plus
  the 3 Y1b real fails fixed before any live flag flip (B2 STANDS,
  strengthened by PROBE-S2).
- The 2-vision bench has never run, even in fixture mode; it is now
  on todolist-push (c5311ce, 7f3a70b) but its runtime is absent on
  this VM (PROBE-S2).
- The Broker exists but nothing in first_action.py or cu.py references
  it (grep 0 hits, verified by X1/X2/X3); S1 is a build, not a switch.
- AMEND4 CONTINUES, slower, per the owner 06:09 TWO TRACKS rule. No
  reviewer proposes pause, redirect, or stop.
- P8 is ANSWERED, not open: chrome context blocked without a Zen
  restart (3790901). Screenshots stay ONLY for Zen chrome UI.
- CODEX-BREAKTHROUGH has now LANDED (2596287). Its proposals were
  PENDING for D1/D2/D3/RTD and all four cross-responses, so NO
  council reviewer has cross-examined them. My CB verdicts below are
  the first full CB round and are single-reviewer, not
  council-converged. The finalizer must record that, and if time
  allows the CB rows should get a cross-response of their own.

### 0.3 Where I differ from the adjudication draft (summary, details in section 1)

- A10: MODIFY, not ADOPT as staged. The draft adopts live 0-vision as
  the acceptance test. I adopt it as rung 2 of a 3-rung ladder and add
  the CB-EXEC 100-task held-out benchmark as rung 3, the general proof.
  A 2-message chat-class pass cannot carry a 90% task-success claim
  for the whole system. Live 2-vision stays diagnostic only; I agree
  with the draft and XRT against X1/X3 on that point, for the draft's
  reason (VISION 1 is a DOM harvest, machine behavior identical).
- B5: collision limb CLOSED by landing (items 2-4, 5-6, 7, 8 all landed
  at HEAD 2864be4). Only the stale-ref protocol limb remains open.
  P2's gate is now protocol-only.
- B6: now shared with CB-EXEC. The prototype must prove the semantic
  executor (targets, preconditions, real input, postconditions), not
  just snapshot/execute/verify in the abstract. A1 and CB-EXEC are one
  design decision, not two builds.
- Order step 0 gains three cheap items the draft does not sequence
  there: CB-5 eval removal, CB-9 manifest habit, CB-7 dispatch-split
  measurement (bundled with S0/P6).
- P8: CLOSED by probe (BLOCKED). No further time on chrome context
  unless the owner approves a Zen restart with the env var.

## 1. Per-proposal verdict table (every row covered, none skipped)

Legend: ADOPT means do it as proposed. MODIFY means do it with the
stated change; the gating conditions attached are what must be proven
before it proceeds. REJECT means do not do it (no proposal is rejected
in full; rejected parts inside merged rows are named). Exact duplicates
are merged into one row citing every source. Coverage: 39 rows: ARCH
A1-A10 (10), GROUNDING P1-P9 (8 rows, P4 merged into A7), SPEED S0-S3
plus six deletions (10 rows), CODEX-BREAKTHROUGH CB-1 to CB-10 plus
CB-EXEC (11 rows).

Tally: ADOPT 21, MODIFY 18, REJECT 0 in full. ADOPT: A2, A6, A7, A9,
P1, P3, P6, P8, P9, S0, D1, D2, D4, CB-1, CB-2, CB-3, CB-4, CB-5, CB-8,
CB-9, CB-10. MODIFY: A1, A3, A4, A5, A8, A10, P2, P5, P7, S1, S2, S3,
D3, D5, D6, CB-6, CB-7, CB-EXEC.

### 1.1 ARCH (worker-arch-review-log.md, 074c1d7)

| ID | Proposal | Verdict | Evidence, reasoning, and gating conditions |
|----|----------|---------|---------------------------------------------|
| A1 | Layer 0 persistent driver daemon (snapshot/execute/verify, structured-first) | MODIFY | Direction right: structured state is exact and cheap (66 rects median 0.030s, clone2 batch 7, single-source), and a state-holding driver is the only shape that stops paying setup per action. But the full-replacement claim has no existence proof (RTD C2, accepted by X1/X2/X3): session_driver.py runs cu.main() per command, code_exec.py is an in-process program model not a daemon, dom_act.py still grounds through image points, cdp.mjs drives agent-managed Chromium only, the bench is unrun. "Exists" means a file exists, not that the composition works. Gating conditions: a staged prototype must prove snapshot/execute/verify end to end on one live ws2 clone chat before anything is deleted (B6 lift, section 5). The prototype design must cover the single-runner lock as a task lock, pill visibility, the one-session-per-browser constraint, daemon crash and stale-state behavior, session-holding scope (RTD C5: holding the single Firefox session blocks every other tool for the task duration), and lifecycle across laptop sleep and reboot. No deletions until then. MERGE with CB-EXEC (section 1.4): the prototype proves the semantic executor, not a bare snapshot/execute/verify shell. One design decision, not two builds. |
| A2 | Layer 1 pixels demoted to fallback-only, pixel-band labeled weak | ADOPT, with sequencing constraint | Proven by vision 58.6% first-try (E2 17/29) and by the code itself admitting the band is necessary, not sufficient (cu.py:1023-1076). Constraint, from RTD and accepted by all four cross-responses: demote only after the router (P1) and its fallback trigger are proven; Zen chrome UI stays pixel-primary because P8 is now ANSWERED BLOCKED (3790901, HTTP 500, MOZ_REMOTE_ALLOW_SYSTEM_ACCESS required), so today pixels are its only perception (AT-SPI cannot see Zen, C12 probe). Without that constraint A2 strands Zen chrome tasks. Fallback stays for canvas, games, video, Zen chrome UI. |
| A3 | Delete session supervisor tree | MODIFY | Direction right, timing conditional. The tree's real jobs are a named killable scope, cancel/stop, the session pill label, and the single-runner lock. Gating condition: delete only when the driver demonstrably holds scope plus cancel latch plus lock on a live run (B4 lift, section 5). Until then the supervisor is the lock holder, and deleting it risks two live runners and loses the cancel/stop path. The F1 failure cluster is partly environment faults, not supervisor-design faults; deleting the tree does not delete those modes. All four cross-responses agree. |
| A4 | Delete overlay daemon server (keep pill visibility) | MODIFY | The server is real (overlay.py 613 lines, Unix-socket server with holder accounting) and per-batch overlay acquire (315-349ms) is a genuine tax, so the end state (delete the server) is right. But the pill is the owner's only visibility into live runs and both replacements are unbuilt. Gating conditions, in sequence: (a) session-level pill first, acquire once per task, server KEPT, measured (this removes the per-batch tax without touching visibility); (b) driver-owned pill (or compositor-plugin indicator) only with proof it shows and clears, including no stale or missing pill when the driver dies mid-task; (c) delete the server only then (B3 lift, section 5). RTD originally REJECTED as stated; XRT softens to MODIFY conditional. No reviewer defends ARCH's stated form (delete with unbuilt replacements), so MODIFY is the converged label. |
| A5 | Delete one-shot SSH loop (persistent Broker only) | MODIFY | Persistent-first is right (fresh SSH 4.43-5.29s per connect, corrected S0 numbers). The word "only" is REJECTED: the VM reaches the relay only through SSH, so this is not deletion of SSH but deletion of one-shot SSH in favor of multiplexed SSH plus broker RPC; and if the broker dies, one-shot SSH is how the relay gets restarted. Gating condition: fresh SSH stays as the documented fallback AND the recovery path. "Only" applies to the default path, never to the recovery path (B4 lift, section 5). XRT softens to ADOPT with fallback retained; X1/X2/X3 keep MODIFY. I keep MODIFY because the proposal's operative word is rejected. Substance is identical across all four. |
| A6 + D2 | Delete file-based observation/action IPC (A6) / delete scp for JSON files (D2) | ADOPT for transport | JSON over the persistent channel (or in-process calls) replaces scp per step; each scp costs a fresh about 5s SSH. Scope condition, recorded by all four cross-responses: files stay as the audit and evidence trail (persisted observation artifacts, JSON plus JPEG, written by the driver); what dies is files as the transport, not files as the record. The JPEG still travels for the human VISION 2 check until the persistent channel carries bytes. Keep file IPC only as the fallback transport when no Broker is reachable. |
| A7 + P4 + D4 | Act-now after-image scope fix (A7) / after-image scope fix, both fields (P4) / delete screen-scope after-capture as produced today (D4) | ADOPT the both-fields shape; the delete-entirely half is REJECTED | Proven defective by construction (first_action.py:656 hardcodes cu.observe_screen, overwriting desktop_act's scope-matching after-capture at cu.py:2083-2091; confirmed by all four reviewers plus Codex). The adopted shape, triple-sourced plus AMEND4 item 12: return BOTH after (scope-matching, chainable) and after_screen (full monitor, verification only, documented non-chainable); move the scope check before the overlay attempt; add a regression test. Execution is DEFERRED to AMEND4 item 12, already in flight on two lanes; the rewrite track consumes it and does not duplicate it. REJECTED part: deleting the envelope after image entirely (ARCH's delete half). It loses the human-visible evidence and the frame-change signal for a saving of about 0.25s, which is noise; that trade fails the 06:07 criterion on accuracy. Timing note, from D3 and accepted by X1/X2/X3/XRT: the scope-as-capability refusal deletion (cu.py:1648/1649, screen observations refuse key/type) is sequenced WITH P2, not with this fix. While actions are still pixel-addressed, the refusal protects typing against a screen observation; once actions are element-ref addressed, scope is irrelevant and the refusal can go. |
| A8 | Delete pixel-band verification for structured targets | MODIFY, sequenced behind P5 | Direction right: the band is admitted necessary-not-sufficient and the DOM value check is sufficient and 100-1000x cheaper (0.002-0.015s). Gating condition: delete band-as-pass-signal only where the per-action DOM assert exists and is mandatory; until then the band stays as a diagnostic. Deleting before the assert set exists leaves actions with NO verification, which is worse than weak verification. This is RTD's sequencing, accepted by X2/X3 and by X1 in substance. The P5/A8 change rests on the verified opt-in-hooks ground (focus_check and type_check are still optional hooks, D1 V13), not on RTD's V11 TODO wording; the draft's V-A5 verified arm_typed_flag exists in zen_dom.py and is called from production code at dom_act.py:433-434, so RTD's phrasing "the production V11 MutationObserver flag is an open TODO" is NOT adopted as phrased. The remaining open question (whether the production code-exec path reaches that call for every type action) belongs to the P5 implementer and is not load-bearing for the P5/A8 verdicts or for benchmark scoring. |
| A9 | Coordinate model to one system (CSS px element rects, converted once at the driver edge) | ADOPT for structured targets | The five-frame tower has five proven bug sites (F2b-1, C12, amend3 step 5, G28, after-scope trap); the one-conversion path already exists (fastpath.dom_rect_to_screen_point, verified). Dependency, accepted by all four cross-responses: A9 depends on AMEND4 items 5-6 landing (origin staleness). That dependency is now SATISFIED (b44a5ea, items 5-6 landed; item 1 geometry landed cc964b2). The one conversion still needs a correct absolute viewport origin and scale factors re-read per ground (C12 proved window-relative vs absolute origin is a live trap). The pixel fallback keeps its own frame internally; the router decides. |
| A10 | Acceptance test becomes 0-vision live benchmark on real ws2 clone chats | MODIFY: adopt as rung 2 of a 3-rung ladder, not as the sole acceptance test | The live 0-vision run is the right final gate for the chat class: DOM harvest, plan, execute, DOM verify, zero screenshots in the machine loop, accuracy at least 90% scored by DOM outcome (V12 sent-bubble gate), total wall time end to end including transport, one final screenshot kept as unscored human evidence (P9), owner approval per run. Staging: fixture 2-vision first (it has never run), P3 first (the live run needs the CDP path). But as stated it cannot carry the general 90% claim: a 2-message chat-class pass proves one task class, not the system. The 100-task held-out benchmark (CB-EXEC, rung 3, section 3) is the general proof and is required before anyone claims 90% task success. Live 2-vision is a diagnostic only if the live 0-vision run fails, NOT a required rung: I agree with the draft and XRT against X1/X3 here, because VISION 1 is already a DOM harvest and VISION 2 a human look, so live 2-vision and live 0-vision-with-P9-screenshot are the same machine behavior and differ only in whether the human looks at live threads or at a screenshot. B1 is LIFTED (section 5). |

### 1.2 GROUNDING P1-P9 (worker-grounding-review-log.md, d1fc4e9)

| ID | Proposal | Verdict | Evidence, reasoning, and gating conditions |
|----|----------|---------|---------------------------------------------|
| P1 | DOM/a11y default router (Zen Marionette/BiDi, Chromium CDP, AT-SPI, screenshot last; encoded in code, not convention) | ADOPT | Two perception stacks with no routing rule drift to the worse one (works everywhere) instead of the better one (needs setup). Implementation requirements, accepted by all four cross-responses: encode the router in code as one function returning the perception source; fail closed to the labeled screenshot fallback; a per-target routing table proven per target before the default flips; a log line on every routing decision, so drift back to screenshots is visible instead of silent. Note: the a11y branch is thin for the apps in play (AT-SPI cannot see Zen; AT-SPI numbers unverified on this VM), so it mostly covers native apps that are not the live workload. Interim honest state: Brave tasks still route to screenshots until P3 lands. |
| P2 | Element-ref action interface rewrite (live rect re-read at execution, screen-point action form, delete dom_rect_to_image_point from the live path) | MODIFY | Direction right and highest-leverage code change after P3: the round trip exact DOM rect to exact screen point to lossy image point and back is proven wasteful from source (fastpath.py:195-243, dom_act.py:312, cu.py:1000-1005), and it deletes the F2b-1, C12, amend3-step-5 bug class. Gating conditions (B5, section 5): (a) the stale-ref disagreement protocol is specified first (what happens when a live rect re-read disagrees with the plan: refuse, re-plan, or click stale, per case; lifecycle across a multi-action plan); AND (b) AMEND4 items 2-4 have landed. Limb (b) is SATISFIED at HEAD 2864be4 (item 2 c1ea773, item 3 62b740e, item 4 72120aa; items 5-6 b44a5ea, item 7 49081aa, item 8 af0fa87 also landed). The collision limb is therefore CLOSED by landing, not by triage, and the protocol is now the single outstanding gate. P2 starts only when (a) is met. Delete dom_rect_to_image_point from the live path (keep for tests and legacy). The scope-as-capability refusal deletion lands in this step (see A7 row). |
| P3 | Brave relaunch with debugging port (controlled experiment, quiet window, never mid-batch; fallback agent-managed Chromium) | ADOPT as a controlled experiment | Single highest-leverage unblocker: the clone chats live in Brave, Brave holds no debugging port on its default profile (cdp.mjs comment verified verbatim), so the CDP path cannot reach them today. Conditions, accepted by all four cross-responses: quiet window owned by the coordinator, never mid-batch (clone1 is mid-batch-8/batch-9 now; PROBE-P3 7b1006a correctly did NOT run); verify /json/list shows the Muse tab and login intact; run observe plus harvest plus one fill plus assert on a scratch input. Recorded additions: CDP on port 9223 exposes the logged-in browser to any local process (security consideration, never mentioned by GROUNDING); the Chromium fallback is a migration with re-login and clone reconfiguration, not a fallback, and needs its own login-persistence check before it is relied on; cdp.mjs notes shadow-DOM elements have null box_model, and Messenger's DOM shape against that gap is unexamined. BLOCK on any live-task migration until the experiment passes. PROBE-P3 status: NOT-RUN, feasibility UNDECIDED (V-F1-4). If P3 fails (Brave refuses the port and the Chromium migration is too disruptive), the DOM-first live path loses its highest-leverage unlock and the whole program re-plans around Zen Marionette only; report that plainly, not worked around silently. |
| P5 | DOM verification mandatory (focus_check and type_check required, not optional hooks; CDP fill read-back and assert polling the model) | MODIFY | Direction right; the code admits the band is insufficient. The blanket mandate is BLOCKED as stated: the assert set does not exist for every action type (focus_check/type_check are still optional hooks, D1 V13), and no per-action exception list exists. Gating conditions: DOM verification becomes mandatory PER ACTION TYPE as its assert lands; an explicit per-action exception list names the actions where DOM assert is impossible (scroll position, hover state) and pixel stays the only signal; the band stays as a diagnostic until then. A blanket mandate now means false refusals on working flows or vacuous asserts (false confidence). The V12 sent-bubble gate in the benchmark is the pattern. CB-1 (section 1.4) is the result-contract form of this row: verified=true only with a postcondition. This MODIFY is converged across all four cross-responses. |
| P6 | Measure the vision call | ADOPT, with specification fix | Cheapest item on the list and a precondition for honest speed claims: capture is 15-30ms and DOM rects 0.030s, but the model read that locates the target is seconds and timed nowhere. Bundle with S0. Specification fix, from RTD and accepted by all four cross-responses: the model call happens in the calling agent's loop, outside cu.py, so the proposal must specify the timestamp points (observation delivered to the agent vs located target returned) and the owner of the logging (the harness, not cu.py), or it will be recorded as done when only capture timing is logged again. Until that number is in the logs, every speed claim about the screenshot path is incomplete, and nobody may claim the 10s target is met. |
| P7 | Session handover protocol (one protocol per browser per task phase, BiDi ground then Marionette input or stay on one) | MODIFY | The one-session constraint is proven (4 runs, Firefox allows exactly one remote session per instance), so a protocol is needed IF a task genuinely needs two protocols. Gating condition: first answer whether Marionette-only suffices (the benchmark already runs Marionette-only, harvest plus input, and zen_dom harvest IS Marionette). Write the handover protocol only if a task genuinely needs BiDi for grounding plus Marionette for input. Price noted: a handover costs 4-7s per switch (BiDi new 1.51-2.77s fresh, Marionette attach 2.65-4.12s), comparable to the SSH tax being deleted. Small and non-blocking either way. All four cross-responses converge on MODIFY. |
| P8 | Zen chrome Marionette context test (set_context chrome) | ADOPT as a probe; ANSWERED BLOCKED, fallback adopted, no further work | Premise verified (no chrome-context support in zen_cli.py today). The probe has now RUN and answered (3790901): chrome context BLOCKED without a Zen restart, HTTP 500, MOZ_REMOTE_ALLOW_SYSTEM_ACCESS required, C12 reproduced live, session acquire 0.01s, content eval fine (title Welcome!, mozInner 240, 8). Consequence, per the probe and GROUNDING's own fallback: keep screenshots ONLY for Zen chrome UI and record that boundary explicitly. AT-SPI cannot see Zen, so that path is closed; do not spend more time on it. The only path to chrome context is a Zen restart with MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1, which kills owner tabs and the session: that is a decision for the owner, not a probe, and is NOT scheduled by this verdict. |
| P9 | Keep one screenshot for the human (VISION 2 stays, machine scores by DOM) | ADOPT | Correct division: screenshots are a human evidence channel, not a machine perception channel. VISION 2 stays as unscored human evidence; the machine scores by DOM outcome. Wording correction, from RTD and accepted by all four cross-responses: VISION 2 is the agent looking at the threads and reporting to the human, not the owner looking directly, so it is the agent's final sanity check reported to the human. Cost is about 0.25s plus one vision read, noise against the total. Attached to A10. |

### 1.3 SPEED S0-S3 plus six deletions (worker-speed-review-log.md, a4ecb49)

| ID | Proposal | Verdict | Evidence, reasoning, and gating conditions |
|----|----------|---------|---------------------------------------------|
| S0 + D1 | Step 0 persistent SSH multiplexing, do now (S0) / delete fresh SSH per call (D1) | ADOPT on CORRECTED numbers | Fresh SSH 4.43-5.29s (7 samples, confirmed four ways); multiplexed 0.91-1.46s (11 samples, rc=0, master verified alive). Saving about 3.2-3.5s per connection, about 3.5-5x, NOT 460x and NOT 0.01s. SPEED's 0.01s figure matches a failed-fast connection (master not up, rc=255, D1's diagnosis, accepted by RTD and D3); SPEED's log records no return codes and no master-liveness check. Corrected expectation: per act-now (3 connects) about 16s becomes about 5-6s, not about 2s; per observe (2 connects) about 6-8s saved. SPEED's 1.6x per-task estimate was built on 0.01s and must NOT be quoted; D1's revised roughly 1.3-1.4x on a CL2-MSG-class task is the working figure until a recompute on the corrected numbers. Conditions: implement the fallback explicitly (any multiplex failure falls back to a fresh connect, slow but correct); log master death; per-socket watchdog, not global (a half-dead master can hang rather than fail cleanly; ControlPersist=600 can leave a stale master holding a dead Tailscale route); the 1-day soak test runs IN PARALLEL, advisory, not a gate (section 6). The residual about 1.1-1.2s per call (per-session sshd and shell setup, which multiplexing does not remove) is itself an argument for S1 and A1. Do it now: no agent-logic code change, fallback safe. |
| S1 + D3 | Step 1 act-now over the persistent relay broker (S1) / delete per-batch session spawn (D3) | MODIFY, proof-first | Direction right: the per-batch session spawn is a real tax (0.4-2.1s) plus a real failure mode (20s deadline, timeout never falls back, council 1 B1), and JSON over the same channel kills the scp round trips. But S1 is a BUILD, not a switch: the relay is alive (PID 1821, socket exists, verified) yet zero references to session_remote or Broker exist in first_action.py or cu.py (grep 0 hits, verified by X1/X2/X3), so the broker path from the VM is unproven end to end, and the single-owner socket semantics under concurrent VM workers are unexamined (serialize or refuse). Gating conditions: prove one live batch end to end over the broker from the VM first, then delete the per-batch spawn; keep the spawn as fallback until proven. Session-level pill (keep the overlay server) lands in the same step. Expected per-batch mechanism about 0.5s plus the overlay item after S1. All four cross-responses converge on MODIFY. |
| S2 + D5 | Step 2 DOM-first plus code-exec plus checkpoint verification, CU_CODE_EXEC=1 on (S2) / delete per-action model call as the default (D5) | MODIFY, gated | The 10x path, already built and merged (code_exec.py 880 lines, Pick 1 winner, commits 714e4f9, 84b88bb, 2e2aeff, merge 453adc4), and the flag is OFF in the live path (verified live: CU_CODE_EXEC unset on the laptop). But the blanket flip is BLOCKED (B2, section 5): Y1b council 3 BLOCKED Phase A on 84b88bb with 14/20 probes passing and 3 real fails (1e f-string chr NameError; 2a codemode wall preemption, error raised only after the C loop finished; 2b code_exec wall preemption, elapsed 6.20s, ok=True with NO error, silent success), and the named gate (2-vision benchmark) has never run. A fixture bench pass alone does not fix the 3 real fails. PROBE-S2 strengthens B2 (V-F1-3): the 3 fails are STILL OPEN at this HEAD, no preemption mechanism exists in codemode.py or code_exec.py, chr is in neither SAFE_BUILTINS list, and the bench runtime is absent on this VM. Gating conditions, in order: (a) bench runtime installed, fixture 2-vision bench green; (b) fix the 3 Y1b real fails; (c) flip the flag for ONE live task class (clone chat sends) with act-now as fallback, measure, then expand. The "10x path" label is corrected to 3-5x on unmeasured model inference time (SPEED's own honest limit: 30-60s if vision reading dominates); the mechanism can be about 1s, the model is the remaining unknown, and P6 must measure it before anyone claims the 10s target. Code-exec becomes the default for the proven task class first; the stepwise loop stays the fallback for unknown shapes only. |
| S3 | Step 3 laptop-side task runner, only if Step 2 plateaus | MODIFY, fold into A1/CB-EXEC; plateau defined numerically first | S3 substantially overlaps A1: a laptop-side runner that grounds, acts, and verifies locally and streams back compact state IS the A1 driver daemon approached from the other side, and CB-EXEC is the same destination stated as a semantic executor. One design decision, not two or three builds; do not build a separate runner alongside A1 or CB-EXEC. Gating condition: the plateau criterion must be defined NUMERICALLY BEFORE the S2 flip starts (threshold, run count, decision owner), so the trigger is not argued later. An undefined plateau either never triggers or triggers on one bad run. The decision itself happens only after steps 0-8 of section 2 are measured. Open condition with owner: section 6. All four cross-responses agree on the merge and on the numerical definition; none of the councils supplied the numbers, so this position specifies the form, the owner, and the deadline, not invented numbers. |
| D6 | Delete 120s freshness window as a gate on DOM work | MODIFY, scoped | For DOM-grounded work, re-read the DOM (0.030s) instead of refusing for staleness; the window is a patch for vision coordinates, not a law. Correction, from RTD and accepted by X1/X2/X3: the refusal at cu.py:773 also guards against future-clock observations, and a blanket delete removes the clock-skew guard. Gating condition: keep the future-clock refusal, drop only the age refusal for DOM paths. Keep the window for pixel-addressed work, where staleness is real and the refusal protects against acting on a dead frame. |

### 1.4 CODEX-BREAKTHROUGH (codex-breakthrough-report.md, 2596287, 138 lines)

Process note, load-bearing: Codex read the todolist, the full error file,
cu.py, the browser/accessibility adapters, the broker/session driver and
the installed act-now code, and ran one new read-only aggregation (the
act-now JSONL: 199 lines, p50 order-to-overlay 337.5ms, max 368.4ms;
p50 total wrapper 2.288s, max 6.95s; 195 session paths, 4 fallback,
0 timeout; 167 envelope ok=true, 32 ok=false; 5 uses of
source=captured). It opened no browser window, drove no tab, and ran no
test suite. Its evidence is therefore second-hand on the same base
(E2, G30/G31, F2b, clone2 batch 7) except for two first-hand items:
the installed-code read (first_action.py:422-439 ok=true mapping,
first_action.py:480-485 after-capture, first_action.py:289-315
_fresh_observation substitution) and the JSONL aggregation. Where
Codex re-derives a conclusion from the same base, C1 applies: a fourth
reading is still the same evidence base. Where Codex adds a first-hand
reading, I weight it higher. Its two independent contributions are
CB-1/CB-2 (the result contract and scope-as-data, from installed-code
reading) and CB-9 (the deployment manifest, from the checkout-vs-
installed gap). Its 100-task benchmark design (CB-EXEC) is the only
proposal in the whole round that defines what 90% means and how many
passes prove it; that alone makes CB-EXEC load-bearing for acceptance.

| ID | Proposal | Verdict | Evidence, reasoning, and gating conditions |
|----|----------|---------|---------------------------------------------|
| CB-1 | Three-part result contract (input_sent / verified=true only with postcondition) | ADOPT | First-hand evidence from installed code: cu.py:1541-1549 admits the desktop check knows only cursor position, not which UI element received the event; cu.py:1580-1592 refuses only on cursor drift over 3px; cu.py:1806-1809 pixel-hash change does not confirm success; a11y.py:204-219 treats do_action true as click complete with no post-state check; installed first_action.py:422-439 turns cu.py ok or enough completed actions into envelope ok=true. G30 is the live proof: batches reported ok/completed, message never sent, clicks 64-75px above the real field. The fix separates three facts the current contract conflates: input sent, correct target received it, post-state confirmed. This is the result-contract form of P5/A8 and the acceptance language for the whole program: from now on no result is reported verified without naming its postcondition. ADOPT as the standard; implementation lands with P5 (per-action asserts) and CB-EXEC (postconditions per step). No new measurement needed to adopt the contract itself; the postcondition set per action type is the P5 work. |
| CB-2 | Scope mandatory in action data, scope change stops the batch | ADOPT | First-hand evidence from installed code plus error file: cu.py:1473-1475 allows key/type only on window observations; first_action.py:480-485 always captures after with observe_screen; first_action.py:289-315 (_fresh_observation) substitutes a full-screen capture when the observation is missing, stale, or bad, and still hands the whole action list to the executor without converting coordinates to the new frame. J40 records the consequence: a point from a window image used on a full-screen image, missed the button by about (+45,+12)px, command still returned ok. J35 records window 1863x1176 vs after 1920x1200. This generalizes A7/P4 from the after-image to the whole batch: scope is part of the action data, and a scope change is a stop, not a silent frame swap. ADOPT; lands with A7/item 12 (scope-matching after-capture) plus P2 (element-ref actions carry their scope and observation id). |
| CB-3 | Vision error taxonomy + image uniformity + J37 codec false refusal | ADOPT, with the J37 threshold change gated on re-measurement | Evidence: E2 17/29 (58.6%), Wilson 95% interval 40.7%-74.5% computed by Codex (small sample, not a held-out set, correctly caveated); G30 as the stronger independent vision-reading example (64-75px); geometry 1920x1200 scale 1 (cu.py:973-977) refutes a single global scale factor as the sole cause; at least two error kinds exist (model picks the wrong target in the image, orchestration feeds a frame-mismatched image/coordinate pair). Image non-uniformity is first-hand from code: observe defaults to max_width 960 (cu.py:2303), save_observation JPEG q90 (cu.py:807-863), act-now captures at max_width 1920 (first_action.py:313), so the model sees different resolution and detail by path. J37: preflight compares decoded JPEG against a fresh uncompressed capture with patch threshold 6 (cu.py:979-1000); error file lines 832-837 report a patch diff 6.627 causing an unstable refusal, a plausible codec false refusal. ADOPT the taxonomy (classify E2/G30/G31/J37 into target-selection vs orchestration-frame vs codec errors) and the uniformity fix (one capture size/quality for the machine path, or record the size in the observation). The J37 threshold move itself is GATED on a re-measurement: one sample at 6.627 vs threshold 6 does not set a new threshold; measure the patch-diff distribution on unchanged screens first, then move the threshold or separate codec noise from real change. Bundled with P6 (measurement work). |
| CB-4 | Batch growth by proven validity (90% per-click math: 20 clicks 12.2%, 32 clicks 3.4%) | ADOPT as a design rule | Math verified by me (V-F1-7): 0.9^20 = 12.2%, 0.9^32 = 3.4%. The independence assumption is disclosed as illustration and the real errors are correlated, so these are not measured failure rates. The conclusion stands anyway and is the strongest form of the argument against maximizing actions per image: 90% per-click does not mean 90% task success, and the guards in desktop_act (focus, window, geometry, screen checks before actions, after-capture only at batch end) do not check that click 1 opened the right page, focused the right field, or that earlier steps invalidated later coordinates. ADOPT as the rule that governs batch size: a batch grows only when the executor proves the next steps are still valid (live re-read, postcondition per step), never because 32 slots exist (cu.py:1013-1019, code_exec.py:187-192 cap 32). Implementation is CB-EXEC's per-step postconditions plus S2 checkpoint verification. This rule also kills the "max actions per vision" framing as a goal: the goal is task success, not batch size. |
| CB-5 | Common executor routing + Zen adapter + locate confirms visible/interactive/uncovered/stable/unique + remove unrestricted zen_dom eval from default interface + AT-SPI coverage reporting | ADOPT | Evidence: act-now calls only desktop_act (first_action.py:403-405, 457-460), never routes web targets to DOM or AT-SPI; code_exec has DOM actions and assertions but its DOM window is chromium and it is gated by CU_CODE_EXEC=1 (code_exec.py:41-53, 69-77, 92-103); zen_dom.py:81-115 spawns a geckodriver session per invocation; locate does one querySelector plus getBoundingClientRect (lines 172-185) with no check that the element is visible, interactive, uncovered, stable, or unique; zen_dom eval runs unrestricted JavaScript in the current tab (lines 151-155, 221-245); a11y.py:83-104 caps at 500 nodes or 2s, returns at most 80 items, flags truncated (partial coverage, honestly reported as a flag, not a number). The locate-confirm list (visible, interactive, uncovered, stable, unique) is the precondition set CB-EXEC needs, and AT-SPI coverage reporting (how much of the tree was actually seen) is the honest form of a partial source. The eval removal is a security fix with zero accuracy cost: unrestricted eval must not be a default agent primitive; keep it in an explicit debug mode. This row is the executor-side statement of P1+P2 plus two new items (eval removal, coverage reporting). ADOPT; the eval removal can land immediately (step 0, small, safe, no dependency), the locate-confirm set lands with P2, coverage reporting lands with P1. |
| CB-6 | act-now uses the long-lived session driver, one owner, sequential queue | MODIFY, same gates as S1/A1 | Evidence: session_remote.py:460-520 broker plus session_driver.py:59-75 JSON-lines driver exist, but act-now builds a cu.py session command per invocation (first_action.py:172-178, 403-405); zen_dom opens and closes a session per command. One owner of pointer, overlay, and Firefox session, with a sequential queue, is the right shape, and it is the same destination as S1 (broker transport) and A1 (driver daemon). But it is stated as a use, not a proof: the VM-to-broker path is unproven (0 Broker refs in first_action.py/cu.py), the single-owner socket semantics under concurrent VM workers are unexamined, and two protocols share one Zen slot (no BiDi plus Marionette at once). MODIFY with the S1/A1 gates: prove one live batch end to end over the broker from the VM first (S1 gate), then move act-now onto the session driver; keep the per-batch session spawn as fallback until proven. |
| CB-7 | Latency measurement fixes + measure VM-to-laptop dispatch separately | MODIFY: adopt the measurement, correct Codex's overstatement | Codex is right on the measurement gap: first_action.py records order_to_overlay_ms from wrapper start, not from the user command on the VM (lines 339-400); no timestamp for first pointer action; target_breached compares the whole batch duration against the 30s threshold (lines 495-498), so it does not measure first-action latency; the header note (lines 40-48) admits model decision and pre-call observation time are excluded. The JSONL aggregation (199 lines, p50 order-to-overlay 337.5ms, max 368.4ms; p50 wrapper 2.288s, max 6.95s; 167 ok=true, 32 ok=false) measures executor time, not click hit rate or task success, and the log carries no target element or postcondition, so ok=true cannot be checked against the target. ADOPT the fix: timestamp first pointer action, measure VM-to-laptop dispatch separately with the same workload under fresh SSH and connection reuse. MODIFY because Codex overstates one claim: "no record supports 11.6s of 12.26s is SSH dispatch" is wrong as phrased (V-F1-5). F2b measured the dispatch LUMP (scp + SSH connect + shell startup, 11.620s, T_order to T_LAPTOP_START) and it is real evidence for dispatch dominance. What is missing is the SPLIT (scp vs connect vs shell), and SPEED's per-call composition (about 9.5s per observe, about 16s per act-now) assumed 4.6s per connect, which the mux correction (about 1.1-1.25s) has since changed. The dispatch-split probe is bundled with S0/P6 in step 0. Until it lands, nobody quotes a dispatch share more precise than the F2b lump. |
| CB-8 | Evidence discipline (DONE is a state of specific evidence) | ADOPT | Evidence: the todolist marks items DONE toward a determined direction or a fixture, which does not mean proven on a real app; held-out new app plus independent agent is PARTIAL (todolist line 38); J10 real think-time still OPEN (error file line 717); fixture form 0.64s and 15 steps in real Zen is a fixture simulating Polygon, not the Polygon upload task, with no same-task baseline (final-report lines 178-194); 13/13 verified actions on a fixture cannot become a 90% commitment for other apps. ADOPT as a process rule for the whole program: every DONE names its specific evidence (which task, which app, which run, which gate), and no DONE is inherited from a different task or a fixture. This rule governs the acceptance ladder in section 3: each rung passes only on its own evidence. No code change; the finalizer records it as a standing rule. |
| CB-9 | Deployment manifest (lock source commit + installed artifact + log) | ADOPT | Evidence: Codex's checkout was HEAD 4500a18 with the remote-tracking ref 622 behind, unfetched; scripts/first_action.py was not in that checkout (not git tracked there) and was read from /home/james/.local/share/agent-computer-use/scripts/first_action.py; the installed cu.py had two extra act-now branches vs that checkout; untracked files existed in the repo. My check (V-F1-6) shows the staleness explains part of this (first_action.py IS tracked on todolist-push now), but the underlying failure is real and already bit once: a reviewer could not tell which commit was installed, which checkout was read, or whether they matched. F2b line 20 shows the manual form of the fix (md5 match VM vs installed). ADOPT: every deploy writes a manifest (source commit, installed artifact hashes, log path, timestamp) and every benchmark cites it. Lands immediately in step 0 as a habit, no code dependency; the manifest file is written at deploy time by whoever deploys. |
| CB-10 | Overlay flicker vs think-time separate, per-phase measurements | ADOPT | Evidence: the todolist records overlay idle 0 repaint and 0 events in its measurements, but the LIQUID background test did not run because the plugin was not loaded (todolist lines 42-45), so there is no evidence the original flicker was reproduced or fixed; think-time is unmeasured by act-now and J10 marks H2 open. Two different unknowns (does the pill flicker, how long does the model think) must not be collapsed into one cause (SSH, screenshot) without per-phase numbers. ADOPT, bundled with P6/CB-7 in step 0: measure overlay behavior per phase (idle, acquire, during action, release) and model think time per phase, separately. Until those numbers exist, no flicker claim and no think-time claim is made. |
| CB-EXEC | The semantic transaction executor itself (semantic targets, preconditions, real mouse/keyboard, postconditions, retry only when surely unsent; one local broker; DOM/BiDi + AT-SPI + screenshot-crop backends under one contract; vision as fallback; 100 held-out tasks benchmark, 90% defined as task success, about 96/100 for 95% confidence) | MODIFY, staged: adopt as the destination design, prototype first, benchmark last | This is the strongest single proposal in the round and the only one that names the actual defect in one sentence: the current contract sends x/y and calls driver receipt success, without proving which control received the input or whether the app reached its goal. Its evidence base is the installed-code reading (CB-1/CB-2) plus the benchmark-design gap (CB-8): no live accuracy number exists for DOM on real Messenger, 13/13 on a fixture does not transfer, 17/29 is one small non-held-out sample. Its design answers the open questions the other reviews left open: semantic targets (role plus name, or selector/ref from a fresh snapshot) instead of pixels; scope (window/tab, frame, observation id) as data; preconditions (unique, visible, enabled, right window, geometry and focus unchanged); real input when hover/trusted events matter (the Browse-button lesson, the BiDi pointer-click failure, Marionette viewport limits, docs/zen-dom-control-comparison.md:67-120); postconditions per step (dialog closed, URL changed, field value, checked state, new text); retry only when the executor knows input was surely unsent, with a state check before replaying anything that can send or delete. One local broker holds the single owner, the sequential queue, the overlay, and the single Firefox session (no competing BiDi plus Marionette clients). Backends under one contract: DOM/BiDi, AT-SPI, screenshot-crop for canvas/image content, vision as fallback, PNG/lossless crop for vision fallback, lowest structure needed. Cost estimate is disclosed as an estimate, not a plan (prototype 2-3 days on a fixture plus low-risk web tasks; broker consolidation plus desktop AT-SPI plus Firefox limits 1-2 weeks for one engineer; independent benchmark a few more days). MODIFY, not ADOPT as a build order, for three reasons. First, the composition is unproven (C2): no prototype exists, and the same "parts exist" fallacy applies here as to A1. Second, building the full executor before S2 is measured repeats the big-bang error D1/Rtd reject: S2 (code-exec on, one task class) is the cheap proof of the program shape, and the executor is built on what S2 measures. Third, the 100-task benchmark needs its task set specified before counting (sampling, independence, representativeness, comparison arms), or 96/100 is a number without a denominator. Gating conditions: (a) prototype on the Zen fixture plus one clone-chat class, proving semantic target plus precondition plus real input plus postcondition on a live run, including a destructive-action test that proves no double-send on retry; (b) S2 measured first (step 5 of section 2); (c) benchmark task set and comparison arms (screenshot-only, DOM plus real mouse, AT-SPI plus real mouse, executor, same tasks, order interleaved) specified before rung 3 runs. A1 and S3 fold into CB-EXEC: one design decision, one prototype, one benchmark. |

### 1.5 Overlap map (same change proposed twice or more)

- Transport: A5 plus S1 plus D1/D2/D3 plus CB-6. One change, four framings. Implement once as S0 then S1/CB-6.
- After-image and scope: A7 plus P4 plus D4 plus AMEND4 item 12 plus CB-2. One fix plus one generalization. AMEND4 owns the fix; CB-2 generalizes scope to all action data.
- Pixel verification: A8 plus P5 plus CB-1. One change, three framings. CB-1 is the contract language.
- Coordinate model: A9 plus P2. P2 is the implementation of A9 for grounded actions.
- Daemon/runner/executor: A1 plus S3 plus CB-EXEC. One design decision, not three builds. CB-EXEC is the fullest statement; A1 is the transport shape; S3 is the runner shape.
- File IPC: A6 plus D2. One change, JSON transfer only.
- Measurement: P6 plus CB-7 plus CB-10. One instrumentation program, three framings. P6 is the vision-call timestamp, CB-7 the dispatch split and first-action timestamp, CB-10 the per-phase overlay/think split.
- Evidence discipline: CB-8 plus CB-9. One habit, two forms: name the evidence for every DONE, and lock the deployed build in a manifest.
- The reviews agree with each other because they read the same record (C1). Overlap is not corroboration. Codex is the partial exception: CB-1, CB-2, CB-9 rest on first-hand installed-code reading, not on the shared record.

## 2. Order of work (numbered sequence with explicit gates)

Every step is independently verifiable, every step lands a measured win
before the next step starts, and no step depends on a bet (P3, P8, S2
measurement) that has not yet paid off. Cost is irrelevant by the
criterion, but sequencing by dependency is not cost, it is correctness:
a daemon built from unproven parts inherits their failure modes.

0. S0 plus P6 plus CB-7 dispatch split plus CB-10 per-phase split plus
   CB-9 manifest habit plus CB-5 eval removal, now. Persistent SSH
   multiplexing with explicit fallback, master-death logging,
   per-socket watchdog; P6 vision-call measurement with the timestamp
   points and harness owner specified in section 1; CB-7 dispatch
   split (fresh SSH vs reuse, scp vs connect vs shell, same workload);
   CB-10 overlay/think per-phase measurement; CB-9 manifest written
   at every deploy from now on; CB-5 unrestricted zen_dom eval removed
   from the default agent interface (debug mode only). Gate to step 1:
   fallback explicit and watchdog in place; eval removal landed.
   The 1-day soak test starts the same day and runs IN PARALLEL,
   advisory, not a gate (a master death falls back to fresh SSH, slow
   but correct).
1. AMEND4 continues in parallel, slower, per the owner 06:09 TWO TRACKS
   rule (section 4). Items 9, 10 after; item 11 any time; item 12 lands
   via the in-flight lanes; verify the regression test. Gate: the
   rewrite track makes no parallel edits to the same functions AMEND4
   is working on (the two tracks run in sequence per item on shared
   files, not in parallel on the same functions, or the merge will
   collide).
2. P3 Brave relaunch experiment plus the P8 boundary record, in a real
   quiet window between clone batches, coordinator-owned, never
   mid-batch. P8 is already answered (BLOCKED); record its boundary
   (screenshots ONLY for Zen chrome UI) explicitly in the router and
   the docs, and do not spend further time on chrome context unless
   the owner approves a Zen restart with MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1.
   Gate to any live DOM work on Brave: P3 passes (login intact,
   /json/list shows the Muse tab, one fill plus assert on a scratch
   input) or the Chromium fallback is proven with its own
   login-persistence check. No live-task migration until then. If P3
   fails, re-plan around Zen Marionette only and report it plainly.
3. Fixture 2-vision bench run. Bench runtime setup first (venv,
   selenium, Firefox/geckodriver at the hardcoded paths, per PROBE-S2),
   then run. Bring nothing new onto the branch (bench and fixture are
   already there, c5311ce and 7f3a70b). This step does not depend on P3
   (headless Firefox, local fixture) and may run in parallel with step
   2. Gate to step 6: the fixture run passes. The program's gate cannot
   be an unrun script.
4. Fix the 3 Y1b real fails on code-exec (1e, 2a, 2b). Gate to step 6:
   the fails are fixed (B2 lift, part 1). Owner: section 6.
5. P1 router plus P5 asserts per action type plus CB-1 contract plus
   CB-3 taxonomy/uniformity. Rewiring of existing hooks; P5 per action
   type as its assert lands, plus the explicit exception list; CB-1
   result language (input_sent vs verified) adopted as the reporting
   standard from here on. Gate to step 6: the router logs its routing
   decisions, and the P5 assert set covers the S2 task class (clone
   chat sends). This step precedes the S2 flip because S2's checkpoint
   verification IS P5: flipping S2 without P5 means running code-exec
   with pixel-band verification only.
6. Define the numerical plateau (coordinator, before the flip; section
   6), then the S2 flip for ONE live task class (clone chat sends)
   with act-now as fallback. Measure model-call count, wall time, and
   P6 vision latency. CB-4 batch rule applies from here on: batch size
   grows only by proven validity, never to fill 32 slots. Gate to
   expansion: measured on one class; expand only on measurement.
7. P2 element-ref interface rewrite, after the stale-ref protocol is
   specified (the only remaining B5 gate; the AMEND4 landing limb is
   satisfied at HEAD 2864be4). A9 one-system coordinates land in this
   step (depends on AMEND4 items 5-6, satisfied). The
   scope-as-capability refusal deletion lands in this step, not with
   A7. CB-5 locate-confirm set (visible, interactive, uncovered,
   stable, unique) and AT-SPI coverage reporting land in this step.
   Gate to step 8: P2 proven on the S2 task class with DOM verification
   mandatory.
8. S1/CB-6 broker path proof from the VM on one live batch, then delete
   the per-batch spawn. Session-level pill (server kept) in the same
   step. P7's Marionette-only question is answered before any handover
   protocol is written. Gate to step 9: one live batch proven end to
   end over the broker from the VM.
9. A1/S3/CB-EXEC merged prototype decision, only after steps 0-8 are
   measured and the plateau definition is applied. The prototype must
   prove semantic target plus precondition plus real input plus
   postcondition end to end on one live ws2 clone chat, including a
   destructive-action test proving no double-send on retry (CB-EXEC
   gate). Gate to step 10: prototype proven.
10. A3/A4/A5 deletions last, each gated on its replacement proving (A3:
    driver holds scope plus cancel latch plus lock; A4: session-level
    pill measured, then driver-owned pill crash proof, then delete the
    server; A5: broker proven on the VM path with one-shot SSH kept as
    recovery).
11. Acceptance ladder (section 3): rung 1 fixture 2-vision (step 3),
    rung 2 live 0-vision on real ws2 clone chats, rung 3 100-task
    held-out benchmark. Live 2-vision is a diagnostic only if rung 2
    fails.

## 3. Acceptance test decision

Decision: the acceptance test is a LADDER with three required rungs and
one diagnostic option. No single rung carries the 90% claim on its own
(CB-8: DONE is a state of specific evidence; each rung passes only on
its own evidence).

- Rung 1 (required, first): fixture 2-vision benchmark. Headless
  Firefox, local fixture. It has never run at all (BUILD ONLY); the
  whole program's gate cannot be an unrun script. The bench and the
  fixture are on todolist-push now (c5311ce, 7f3a70b); the runtime
  (venv, selenium, Firefox/geckodriver) must be installed first, per
  PROBE-S2. Pass criteria: the script's own gates (V12 sent-bubble
  gate after each message, scoring by OUTCOME in the thread DOM, never
  point-in-box). This rung does not depend on P3 and may run as soon
  as S0 lands.
- Rung 2 (required, final gate for the chat class): live 0-vision
  benchmark on the REAL ws2 clone chats (clone1 Brave plus clone2
  Chrome). DOM harvest, plan, execute, DOM verify, zero screenshots
  in the machine loop. Pass criteria: accuracy at least 90%, scored by
  DOM outcome (V12 sent-bubble gate, message in the thread DOM, never
  point-in-box); total wall time measured end to end including
  transport (recorded; no time pass bar is set on the first run until
  P6 has baselined model inference time, and nobody may claim the 10s
  target until that baseline exists). One final screenshot is kept as
  unscored human evidence (P9); it must not feed the score. Conditions
  on the live run: P3 closed first (otherwise it falls back to
  screenshots and proves nothing); quiet window with clone
  coordination; owner approval per run (the bench's --live plus
  --confirm-live gates plus plan-URL gate); agreed test messages so
  the clones' working threads are not polluted.
- Rung 3 (required, the general proof): 100-task held-out benchmark
  (CB-EXEC design). Browser plus desktop tasks, new content and
  layout, run by an independent agent. Pass criteria: task success
  end to end at least 90%, defined as task success (not per-click hit
  rate); at least 96 passes out of 100 (Wilson 95% lower bound about
  90.2%, verified by me in V-F1-8); per-phase P50/P90 recorded
  separately (model, SSH, broker, observe, act, verify); model-call
  counts, full-screen images, crops, DOM/a11y queries, and retries
  counted; false-success count (ok=true without a postcondition)
  reported as its own metric with zero tolerance as a honesty gate
  (any false success fails the run's honesty gate even if the count
  passes); side effects and recovery actions counted. Comparison arms
  on the same task set, order interleaved: screenshot-only, DOM plus
  real mouse, AT-SPI plus real mouse, executor. The task set, sampling,
  and independence rules are specified BEFORE rung 3 runs, or 96/100
  is a number without a denominator.
- Diagnostic option (not a rung): live 2-vision. If the live 0-vision
  run fails, the team may run live 2-vision to localize (script vs DOM
  path). It is not required before the final gate, for the reasons in
  section 1 (A10 row): the machine behavior is identical in both
  forms, and the P9 screenshot supplies the human outcome check.

What the fixture run does NOT prove, recorded as a gap not papered
over: a fixture pass alone repeats the F1a/F2b pattern (pass on the
exercise, unproven on the real task). The live run is the proof the
fixture cannot give, because the real tasks fail on Brave on ws2, where
the DOM path does not reach yet (P3). And the chat-class live run does
not prove the general 90% claim either: that is what rung 3 is for.

## 4. AMEND4 sequencing

CONTINUE, slower, per the owner 06:09 TWO TRACKS rule. Do not pause,
redirect, or stop. All four cross-responses agree, and the owner rule
answers the question directly: the team debates directions while the
fix/improve-current track keeps going, but slower and more carefully to
save tokens, because no direction is confirmed best yet.

- Why continue: items 1-8 fix the geometry and traversal the rewrite
  builds on (item 1 is the prerequisite for A9; items 5-6 fix the
  origin staleness A9 depends on); item 12 IS the A7/P4 fix all three
  reviews plus Codex agree is proven-needed; stopping wastes the
  in-flight lanes and leaves known-broken behavior (geometry units,
  after-image scope) in the live loop the clones use today; the
  rewrite is not adjudicated final yet, so there is no adopted
  direction to redirect into.
- Landed state at HEAD 2864be4: items 1-8 landed (cc964b2, c1ea773,
  62b740e, 72120aa, b44a5ea, 49081aa, af0fa87). Item 12 is in flight on
  two lanes (Codex amend4-codex, VM CLICK3-AMEND4); the rewrite track
  consumes it and does not duplicate it. Remaining: items 9, 10, 11.
- Triage going forward: items 9, 10 after; item 11 (doc fix) any time;
  item 12 lands via the in-flight run. The draft's split-3/4 settlement
  is now moot in fact (items 3 and 4 landed during the adjudication);
  its reasoning stands (pixel-band work is low value under A8/P5, since
  the band becomes a diagnostic), and it is recorded here as the reason
  the remaining pixel-path-only work stays deprioritized.
- Kill rule at reconciliation: items the rewrite deletes get killed.
  The round-3 council records per item whether the fix is a patch on a
  defective design or a real redesign, and defers or kills any item the
  adopted rewrite replaces wholesale, rather than finishing it. An item
  the rewrite subsumes is verified against the new code, not assumed
  gone. (D3's reconciliation discipline, accepted by X1/X2/XRT.) This
  matters concretely now: item 4's wiring already landed, so P2 must
  re-verify against the new code rather than redo it.
- B2/B5 findings go into the round-3 review: the Y1b 3 real fails (B2)
  and the P2 stale-ref protocol (B5) are fed into the AMEND4 round-3
  council, which judges patch vs rewrite per item under the 06:07
  criterion. (RTD's feed-in, accepted by X1/X2/X3.)
- Pace per TWO TRACKS: fewer parallel workers, smaller batches,
  per-item verification, no new scope. The two tracks run in sequence
  per item on shared files, not in parallel on the same functions.

## 5. Blocking findings, final status

- B1 (A10 straight to 0-vision live on ws2 clone chats): LIFTED. I
  adopt the lift for the draft's reason: what B1 attacked was A10 as
  a straight jump (fixture proof skipped, human outcome check removed,
  P3 untested, live clone workspaces disrupted). None of the councils
  proposes that version; all stage fixture first, condition on P3,
  require owner approval per run, and keep VISION 2 as a human look
  (P9). The remaining RTD-only step (live 2-vision intermediate) adds
  nothing measurable (section 1, A10 row), and the V11 limb is conceded
  as non-load-bearing for benchmark scoring. B1's remaining note (live
  2-vision as a diagnostic) is recorded in section 3, not as a gate.
  My A10 MODIFY differs from the draft's ADOPT only in that acceptance
  is three rungs, not one; the B1 lift itself I accept.
- B2 (S2/D5 blanket CU_CODE_EXEC=1 flip): STANDS, strengthened. No
  council mentions the Y1b BLOCK (XRT V-X1: 0 hits for Y1b or 84b88bb
  in D1, D2, D3); the fixture-bench gate does not cover the 3 known
  real fails. PROBE-S2 adds two facts: the fails are STILL OPEN at
  this HEAD (no preemption mechanism, chr in neither SAFE_BUILTINS),
  and the bench runtime is absent on this VM. Lift condition: bench
  runtime installed, fixture benchmark green, fix the 3 Y1b real fails
  (1e, 2a, 2b), then flip the flag for ONE live task class (clone chat
  sends) with act-now as fallback, measure, then expand.
- B3 (A4 overlay daemon deletion without a replacement): STANDS as a
  gate, confirmed by all three councils. Lift condition: a
  session-level pill (acquire once per task, server kept) is measured,
  and a driver-owned pill proves no stale or missing pill on crash.
- B4 (A3/A5 delete-first ordering): STANDS as a gate, confirmed by all
  three councils. Lift condition: the driver proves scope plus cancel
  latch plus lock, and the broker proves on the VM path with one-shot
  SSH kept as recovery.
- B5 (P2 immediate interface rewrite): STANDS, narrowed to one limb.
  Collision limb CLOSED by landing: items 2-4 have all landed
  (c1ea773, 62b740e, 72120aa), and items 5-8 have landed since
  (b44a5ea, 49081aa, af0fa87); item 4's commit message records
  BrowserAdapter does not exist, so the collision surface was narrower
  than B5 stated (CLI act path, CodeExecBackend.act, first_action
  fallback). Stale-ref protocol limb still open and unanswered by all
  three councils. Lift condition: the stale-ref disagreement protocol
  is specified (refuse, re-plan, or click stale, per case, plus the
  lifecycle across a multi-action plan). That protocol is now the
  single outstanding gate for P2.
- B6 (A1 full replacement claim, now shared with CB-EXEC): STANDS as a
  gate, complied with by all three councils' sequencing. Lift
  condition: a daemon/executor prototype runs snapshot/execute/verify
  end to end on one live ws2 clone chat, in CB-EXEC form (semantic
  target plus precondition plus real input plus postcondition, with a
  destructive-action test proving no double-send on retry).

## 6. Open conditions and owners

- S0 soak test: owner COORD-CLICK-3 (the coordinator owns the soak
  because it spans workers; X2). The S0 implementer names the
  per-socket watchdog. The soak runs in parallel, advisory, not a
  gate; a master death falls back to fresh SSH.
- P3 quiet window plus rollback: owner COORD-CLICK-3. The window is a
  real quiet window between clone batches, never mid-batch. The
  rollback (relaunch without the flag, Brave session restore, re-login
  cost) is stated BEFORE the window, not after. PROBE-P3 re-runs only
  when batch 9 is complete, no new clone1 batch is assigned, and no
  clone1 commits are in flight.
- Numerical plateau (A1/S3/CB-EXEC): owner COORD-CLICK-3. Form: Step 2
  live median wall time above a stated threshold for a stated number
  of runs after the flag flip, decision owner the coordinator.
  Deadline: defined before the S2 flip. The numbers are set from the
  fixture bench plus first live runs baseline; this position does not
  invent them.
- Stale-ref disagreement protocol: writer is the P2 implementer, to be
  named by COORD-CLICK-3 when P2 is staffed. Due before P2 starts; it
  is B5 lift condition (a). Content: refuse, re-plan, or click stale,
  per case, plus the lifecycle across a multi-action plan.
- Y1b fixes (1e, 2a, 2b): owner COORD-CLICK-3 to commission; the fix
  lane is to be named in the final round. No input names an owner for
  this work, so I record it as open rather than inventing one. Due
  before the S2 flip; it is B2 lift condition, part 1.
- P6 specification: timestamp points are named in this position
  (observation delivered to the agent vs located target returned);
  logging owner is the harness, not cu.py. The P6 implementer lands it
  bundled with S0. CB-7 dispatch split and CB-10 per-phase split land
  in the same bundle.
- Residual per-connection cost probe (D1 R2): what exactly costs the
  about 1.1-1.2s even over the master (shell startup, PAM, systemd user
  session setup). Owner: the S0 implementer. It bounds every transport
  design, including the Broker. This is the same probe CB-7 asks for
  as the dispatch split; do it once, not twice.
- V11 wiring confirmation: the P5 implementer confirms whether the
  production code-exec path reaches the arm_typed_flag call for every
  type action. Open, not load-bearing for the P5/A8 verdicts or for
  benchmark scoring.
- CB-EXEC benchmark task set: owner COORD-CLICK-3 to commission, with
  the task set, sampling, independence rules, and comparison arms
  specified before rung 3 runs. No numbers are counted before the set
  exists.
- P3 failure re-plan: if Brave refuses the debugging port on its
  default profile and the Chromium migration is too disruptive, the
  DOM-first live path loses its highest-leverage unlock and the whole
  program re-plans around Zen Marionette only. That outcome must be
  reported plainly, not worked around silently.
- P8 restart decision: Zen restart with MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1
  is an owner decision, not scheduled. It kills owner tabs and the
  session. Until the owner approves it, screenshots stay ONLY for Zen
  chrome UI.

## 7. What would change my verdicts (falsifiable)

- B1 is already lifted (section 5). It re-opens only if a staged live
  run is proposed that skips the fixture rung, drops the human evidence,
  or runs without owner approval per run.
- B2 lifts when the 3 Y1b real fails are fixed, the bench runtime is
  installed, and the fixture benchmark runs green. Then the flag flip
  for one task class is safe.
- B3 lifts when a session-level pill (acquire once per task) is
  measured and a driver-owned pill proves no stale or missing pill on
  crash.
- B4 lifts when the driver proves scope plus cancel latch plus lock,
  and the broker proves on the VM path with one-shot SSH kept as
  recovery.
- B5 lifts when the stale-ref disagreement protocol is specified. The
  collision limb is already closed by landing (V-F1-1).
- B6 lifts when a daemon/executor prototype runs semantic
  target/precondition/real-input/postcondition end to end on one live
  ws2 clone chat, with the no-double-send test passing.
- S0 flips to REJECT only if a live measurement shows multiplexed
  connections slower than fresh ones, or a half-dead master hangs
  instead of failing cleanly with no fallback. Neither has been
  observed; the soak test is the check.
- P3 flips from experiment-ADOPT to REJECT-as-Brave-path if Brave
  refuses the debugging port on its default profile. The program then
  re-plans around Zen Marionette only, and the Chromium migration gets
  its own login-persistence proof before anyone relies on it.
- PROBE-DOMZEN (DOM-first on real Zen) would change P1/P2/S2
  confidence: if DOM harvest plus real input works on real Zen at
  at least 90% first-try target accuracy, the live path can start on
  the Zen side even if P3 fails; if DOM rects disagree with real input
  (Marionette click not equivalent to real mouse, hover/trusted events
  fail), CB-5's real-input requirement dominates and P2 must include
  the Pointer path, and the S2 flip narrows to DOM-verified classes.
- PROBE-S1 (broker batch) would change S1/CB-6: one live batch end to
  end over the broker from the VM lifts the proof gate and the
  per-batch spawn deletion proceeds; a failure (broker unreachable
  from the VM, single-owner socket blocking concurrent workers) keeps
  S1 MODIFY, keeps the spawn, and makes S0 the transport ceiling until
  the broker is fixed.
- PROBE-S2 (fixture bench plus one-class flag flip) would change S2:
  fixture green plus Y1b fixes lifts B2 and the one-class flip
  proceeds; fixture red keeps S2 blocked and the bench/executor gets
  fixed first; a one-class flip measured slower or less accurate than
  act-now stops expansion and triggers the plateau decision. Partial
  PROBE-S2 evidence is already in (V-F1-3): Y1b fails still open, bench
  runtime absent, so B2 is NOT lifted and the fixture gate has a setup
  prerequisite.
- PROBE-S0 (SSH soak) would change S0's done-state, not its verdict:
  a stable 24h master calls S0 done; repeated master deaths or hangs
  keep S0 ADOPT (the fallback covers) but raise S1/A1 priority. It
  cannot flip S0 to REJECT while the fallback exists.
- PROBE-P8 is CLOSED (V-F1-2): chrome context BLOCKED without a Zen
  restart. No further probe evidence can change P8 except an
  owner-approved restart with the env var set, which is a new
  experiment, not a re-run of this one.

## 8. What STOPS (what gets killed, deleted, or never built)

Never built:
- A second separate S3 runner alongside A1/CB-EXEC. One design
  decision, one prototype, one benchmark.
- Unrestricted zen_dom eval in the default agent interface. Remove now
  (step 0, CB-5); keep it in an explicit debug mode only.
- Generic x/y as the everyday model input. Coordinates become an
  adapter-internal detail; the model addresses semantic targets and
  element refs (CB-EXEC, P2).
- The screen-scope after-capture as produced today. Replaced by the
  both-fields shape via AMEND4 item 12 (A7/P4/D4); never ship a
  non-chainable artifact labeled as the batch result again.
- The per-action think-observe-think loop as the default. After the
  gated S2 flip, code-exec programs with checkpoint verification are
  the default; the stepwise loop is the fallback for unknown shapes
  only (S2/D5).
- The 120s age refusal on DOM paths (D6, scoped). The future-clock
  refusal stays.
- Fresh SSH per call and scp JSON transport as the live path (S0/S1).
  Fresh SSH stays only as fallback and recovery.
- The "10x path" label for S2 until P6 measures model inference time.
  Say 3-5x on the mechanism-measured parts, or say nothing about the
  multiple. The 10s target is unclaimed until P6 baselines it.
- The 460x claim. Dead, never quoted again (SPEED's 0.01s was a
  failed-fast connection, rc=255, no return-code check).
- Any live-task migration on P3 before the experiment passes.
- Any blanket CU_CODE_EXEC=1 flip before the Y1b fixes plus fixture
  green (B2).
- Any deletion (A3 supervisor, A4 overlay server, A5 one-shot SSH as
  recovery, A6 file transport) before its replacement proves (B3/B4).
- A big-bang daemon/executor build before S2 is measured. The
  prototype comes after steps 0-8, not before them.

Killed or deleted at reconciliation (section 4 kill rule):
- Any AMEND4 item the adopted rewrite subsumes, verified against the
  new code, not assumed gone. Item 4's wiring already landed, so P2
  re-verifies rather than redoes it.
- dom_rect_to_image_point from the live path (keep for tests and
  legacy). The exact-rect to lossy-image-point round trip dies with P2.
- The pixel band as a pass signal wherever a per-action DOM assert
  exists and is mandatory (A8/P5). It survives only as a diagnostic.
- The scope-as-capability refusal, but only with P2 (A7 row): while
  actions are pixel-addressed it protects typing, so it is not deleted
  early.
- The live 2-vision run as a required gate. It survives only as a
  diagnostic (section 3).

## 9. Evidence index

- ARCH log: improvements/worker-arch-review-log.md (074c1d7).
- GROUNDING log: improvements/worker-grounding-review-log.md (d1fc4e9).
- SPEED log: improvements/worker-speed-review-log.md (a4ecb49).
- CODEX-BREAKTHROUGH report: improvements/codex-breakthrough-report.md
  (2596287, 138 lines). First full CB verdict round is this log; D1/D2/
  D3/RTD and all four cross-responses predate it and mark CB PENDING.
- D1: improvements/worker-click3-d1-review-log.md (37f457e).
- D2: improvements/worker-click3-d2-review-log.md (6d1bf04).
- D3: improvements/worker-click3-d3-review-log.md (14fc139).
- RTD: improvements/worker-click3-rtd-review-log.md (e96b2ff).
- X1: improvements/worker-click3-x1-response-log.md (0cf601c).
- X2: improvements/worker-click3-x2-response-log.md (d5b205d).
- X3: improvements/worker-click3-x3-response-log.md (2b0c73c).
- XRT: improvements/worker-click3-xrt-response-log.md (6cb3f95).
- Adjudication DRAFT: improvements/worker-click3-adjudication-log.md
  (9d23834, 24 rows covering 30 proposals, ADOPT 15, MODIFY 14,
  REJECT 0, PENDING 1 track).
- Probes: PROBE-P3 improvements/worker-probe-p3-log.md (7b1006a,
  NOT-RUN, clone1 batch 9 open, Brave PID 7356 untouched); PROBE-S2
  improvements/worker-probe-s2-log.md (working-tree file at read time,
  Y1b fails still open, bench runtime absent); PROBE-P8
  improvements/worker-probe-p8-log.md (3790901, 2864be4, chrome
  context BLOCKED HTTP 500, MOZ_REMOTE_ALLOW_SYSTEM_ACCESS required,
  C12 reproduced).
- AMEND4 landed state at HEAD 2864be4: item 1 cc964b2, item 2 c1ea773,
  item 3 62b740e, item 4 72120aa, items 5-6 b44a5ea, item 7 49081aa,
  item 8 af0fa87; item 12 in flight on two lanes; items 9, 10, 11
  remaining.
- Y1b BLOCK: commit 9d9bd63 (14/20, 3 real fails 1e/2a/2b), 7e6262f
  FINAL BLOCK, e8fad29.
- Bench: tests/two_vision_bench.py on todolist-push (c5311ce, 868
  lines, BUILD ONLY, VISION 1 is a DOM harvest) plus
  tests/two_vision_fixture.html (7f3a70b, 48 lines); runtime absent
  on this VM per PROBE-S2.
- F2b: improvements/worker-f2b-live-session-log.md lines 30, 34-35,
  49 (order-to-overlay 12.262s, dispatch lump 11.620s scp plus SSH
  plus shell, observe 0.233s, Python 0.060s, overlay 0.349s;
  spawn-to-overlay honesty number 6m56s).
- Codex JSONL aggregation: /home/james/.cache/agent-computer-use/
  first-action-20261122.jsonl, 199 lines, p50 order-to-overlay
  337.5ms, max 368.4ms, p50 wrapper 2.288s, max 6.95s, 195 session
  paths, 4 fallback, 0 timeout, 167 ok=true, 32 ok=false.
- Code refs verified by the reviewers and accepted here: scripts/cu.py
  (observe 920, observe_screen 974, image_point 1000-1005,
  _input_line_changed 1023-1076, desktop_act 1619-2199, scope refusal
  1648/1649, after-capture 2083-2091, OBSERVATION_MAX_AGE 120 at line
  58, refusal 773, --dom-selector 2717, code-exec subparser 2733,
  CU_CODE_EXEC gate 2770/2793), scripts/first_action.py (attempt_session
  183, envelope after-capture 656, _fresh_observation 289-315,
  ok mapping 422-439, after-capture 480-485), scripts/fastpath.py
  (152, 195-243), scripts/dom_act.py (ground_many_one_shot 240-331,
  focus_type 425-491, arm_typed_flag call 433-434), scripts/zen_dom.py
  (harvest 905, eval 151-155, locate 172-185, session per invocation
  81-115), scripts/cdp.mjs (616 lines, Brave debugging-port comment
  227-243), scripts/cursor_session.py (supervise 228),
  scripts/overlay.py (613 lines), scripts/session_remote.py (1601
  lines, Broker 463), scripts/session_driver.py (180 lines),
  scripts/code_exec.py (880 lines, gate 134), scripts/a11y.py
  (cap 83-104, do_action 204-219).
- Numbers used: fresh SSH 4.43-5.29s (7 samples), mux 0.91-1.46s
  (11 samples), saving about 3.2-3.5s per connection, about 3.5-5x
  (460x dead); per act-now about 16s to about 5-6s; per-task about
  1.3-1.4x working figure (SPEED's 1.6x not to be quoted); vision
  17/29 first-try 58.6% (Wilson 95% 40.7%-74.5% per Codex), pointer
  error 0.5-0.9px; DOM 66 rects median 0.030s, 5 clicks all landed,
  verify 0.002-0.015s (single-source, clone2 batch 7, C1 applies);
  F2b order-to-overlay 12.262s (dispatch lump 11.620s, 95%); overlay
  acquire 315-349ms; tc02-t1 gap 722.955s (87.8%) measured with a local
  helper, no SSH hop in it; CB-4 math 0.9^20 12.2%, 0.9^32 3.4%
  (recomputed by me); Wilson 95% lower bound for 96/100 about 90.2%
  (recomputed by me); session start BiDi 1.51-2.77s fresh, Marionette
  attach 2.65-4.12s; handover cost 4-7s per switch.
