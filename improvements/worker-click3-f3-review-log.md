# Worker CLICK3-F3: final council reviewer 3 position, FINAL DECISION round

Owner: Pham Tuan. Role: final council reviewer 3 (Worker CLICK3-F3). I am
independent: I did not coordinate with other final participants in this
round, and I question everything, including the joint adjudication DRAFT.
This round finalizes the direction once and for all.

Decision criterion (owner standing rule 06:07): the final result must be
the MOST ACCURATE and the FASTEST; cost is IRRELEVANT (tokens, time,
rewrite effort). A bigger rewrite that wins on accuracy and speed beats a
smaller patch that does not. I apply the same criterion to blocking
findings: a block must protect accuracy or speed of the final result, not
caution alone.
Evidence standard (owner 06:34, Lauren Tan standard): every claim carries
real measured numbers (test command, output, commit hash, time log). A
proposal with no measured evidence behind it does not count as feasible.

Rules honored: no em dash (U+2014) or en dash (U+2013) anywhere in this
file. No personal info. Evidence with every claim. Wall-clock
Asia/Ho_Chi_Minh + elapsed time. Commit with an explicit pathspec
immediately after staging, never plain git commit, never git add -A.
Verify every push with git ls-remote. Never ydotool. First principles
(06:01): question whether each piece should exist at all. No self-healing
(05:56): this is a review, not my own work.

## 0. Log and what I verified myself

- 06:38 +07 (T+0s): task received. Repo ~/workspace/computer-use-wayland,
  branch todolist-push. Fetched first; local HEAD 7b1006a at start.
- 06:38-06:41 (T+0-3m): read all 13 inputs in full: ARCH-REVIEW
  (improvements/worker-arch-review-log.md, 074c1d7), GROUNDING-REVIEW
  (improvements/worker-grounding-review-log.md, d1fc4e9), SPEED-REVIEW
  (improvements/worker-speed-review-log.md, a4ecb49), CODEX-BREAKTHROUGH
  (improvements/codex-breakthrough-report.md, 2596287, 138 lines,
  Vietnamese, LANDED, no longer PENDING), joint adjudication DRAFT
  (improvements/worker-click3-adjudication-log.md, 9d23834), D1
  (improvements/worker-click3-d1-review-log.md, 37f457e), D2
  (improvements/worker-click3-d2-review-log.md, 6d1bf04), D3
  (improvements/worker-click3-d3-review-log.md, 14fc139), RTD
  (improvements/worker-click3-rtd-review-log.md, e96b2ff), X1
  (improvements/worker-click3-x1-response-log.md, 0cf601c), X2
  (improvements/worker-click3-x2-response-log.md, d5b205d), X3
  (improvements/worker-click3-x3-response-log.md, 2b0c73c), XRT
  (improvements/worker-click3-xrt-response-log.md, 6cb3f95).
- 06:40-06:42 (T+2-4m): spot checks of my own (section 0.1). The branch
  moved during this work: HEAD at writing is 2864be4 (PROBE-P8 log
  commit). I fetched again before writing.
- 06:42-06:55 +07 (T+4-17m): wrote this log.

### 0.1 Spot checks run by me in this session (new verification, not trust)

- V-F1. Y1b BLOCK is real and current: commit 9d9bd63 exists, "Y1b
  verdict council 3: OVERALL Phase A BLOCK on 84b88bb (14/20, 3 real
  fails, 2 probe artifacts)". PROBE-S2 re-checked at 06:37 +07: the 3
  real fails 1e/2a/2b are STILL OPEN (no setitimer, SIGALRM, or
  child-process preemption in scripts/codemode.py or scripts/code_exec.py;
  chr in NEITHER SAFE_BUILTINS list, codemode.py line 37,
  code_exec.py line 107; no commit after 84b88bb touches the executors
  for these gaps). B2 stands.
- V-F2. Broker wiring gap is real: grep for session_remote|Broker in
  scripts/first_action.py and scripts/cu.py returns 0 and 0. S1 is a
  build, not a switch. Verified by me, same result as X1/X2/X3.
- V-F3. 32-action cap is real: scripts/code_exec.py _validate_dom_actions
  requires 1..32 actions. scripts/cu.py lines 1010-1020 show the
  patch-diff threshold 6 code CB cites for J37 (sum of patch mean over
  3 channels above 6 returns True). Line numbers moved with AMEND4 edits
  since CB's checkout; the mechanisms CB cites are present.
- V-F4. J37 codec false refusal is real in substance: error file
  ~/workspace/cf26-upload/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md line 832
  records the preflight "screen changed" tripping on the patch around
  the parked cursor on photographic backgrounds, and line 871 records
  reveal-path refusals of the same class. The exact 6.627 figure is
  CB-cited from lines 832-837; I verified the entry and the mechanism,
  not the decimal.
- V-F5. Unrestricted zen_dom eval exists on the agent CLI:
  scripts/zen_dom.py line 1153 has an eval subparser ("run JS in the
  current tab") and line 441 has the evaluate method. CB's line numbers
  (151-155) are from its older checkout; the primitive exists at HEAD.
- V-F6. The after-image defect is STILL PRESENT in the working tree:
  scripts/first_action.py line 661 still hardcodes cu.observe_screen
  for the envelope after-capture, and line 353 uses observe_screen on
  the substitute path. AMEND4 item 12 has NOT landed yet. A7/P4 is
  still an open fix, not a done fix.
- V-F7. zen_cli.py has zero hits for chrome or set_context, confirming
  the P8 premise. PROBE-P8 has now answered the question live (section
  0.2): chrome context is BLOCKED without a Zen restart.
- V-F8. tests/two_vision_bench.py (868 lines) and
  tests/two_vision_fixture.html (48 lines) are NOW on todolist-push
  (commits c5311ce, 7f3a70b). The draft's V-A3 (bench absent from the
  branch) is outdated; the fixture run is no longer blocked on branch
  state.
- V-F9. CB-9 correction: scripts/first_action.py IS tracked on
  todolist-push at HEAD 2864be4 (git ls-files returns it). CB's
  "not tracked" was true on its checkout (HEAD 4500a18, behind 622 per
  its remote-tracking ref) and is stale on this branch. The manifest gap
  stands in its load-bearing part: the installed laptop cu.py has two
  extra act-now branches not in the repo checkout, so installed artifact
  vs source commit still diverges. CB-9 is judged on the live gap, not
  on the stale part.
- V-F10. AMEND4 landed state at HEAD 2864be4: items 1 (cc964b2), 2
  (c1ea773), 3 (62b740e), 4 (72120aa), 5-6 (b44a5ea), 7 (49081aa), 8
  (af0fa87) have all landed. Remaining: 9, 10, 11, 12. The draft's
  triage ("first 5, 6, 7, 8, 12") is therefore half done; only item 12
  of that first set remains. Item 12 delivery is UNCONFIRMED on the
  Codex lane (driver log queue-check 06:19: grep for ADDENDUM / FIRST
  PRINCIPLES / PRAGMATIC / ITEM 12 in /tmp/codex-amend4.log returned 0;
  the three queued follow-up messages have not surfaced in the exec
  log).

### 0.2 Probe results that landed during this round (new facts, not in the draft)

- PROBE-P8 LANDED (commit 3790901, log commit recorded 2864be4):
  Marionette chrome context BLOCKED without Zen restart (HTTP 500,
  MOZ_REMOTE_ALLOW_SYSTEM_ACCESS required); C12 reproduced live. Zen
  PID 496121, Marionette on 127.0.0.1:2828, MOZ_REMOTE_ALLOW_SYSTEM_ACCESS
  absent from Zen environ. P8 is ANSWERED, not pending: the chrome-context
  path is closed without a restart. Consequence: Zen chrome UI stays
  screenshot-only, and the boundary is now recorded fact, not a pending
  question. No re-probe without an owner-approved Zen restart.
- PROBE-P3 NOT-RUN (commit 7b1006a): clone1 batch 9 open since 06:01,
  Brave untouched. P3 is still the gating experiment, still unrun.
- PROBE-S2 RUNNING (untracked log improvements/worker-probe-s2-log.md):
  bench runtime installed 06:41 +07 (venv /tmp/probe-s2-venv, selenium
  4.53.0, Firefox 160.0.1, geckodriver 0.36.0 at the bench's hardcoded
  paths); fixture bench run started 06:42 +07; result NOT in yet. Y1b
  3 fails confirmed STILL OPEN (V-F1).
- PROBE-S0, PROBE-DOMZEN, PROBE-S1: no results in the record at writing.
  Section 7 states, per proposal, what each would change.

### 0.3 What CODEX-BREAKTHROUGH adds that the draft never judged

The draft treated CODEX-BREAKTHROUGH as PENDING (launch stub only). The
report landed as 2596287 and I read it in full. It is independent in the
sense that matters: it read the code directly on its own checkout, did
its own read-only JSONL synthesis of the act-now log (199 lines: p50
order-to-overlay 337.5 ms, max 368.4 ms; p50 total wrapper 2.288 s, max
6.95 s; 195 session path, 4 fallback, 0 timeout; 167 envelope ok=true,
32 ok=false; 5 source=captured), and it computed its own Wilson 95%
interval for 17/29 (40.7%-74.5%). It also states its limits honestly: it
could NOT verify the 66-element / 5-of-5 sweep claim from local evidence,
could NOT verify the SSH 95% claim, did NOT test browser, BiDi,
Marionette, AT-SPI, overlay, or compositor, did NOT run the test suite,
and did NOT fetch origin. Under RTD C1 (agreement is not independent
confirmation), CB's citations of E2, G30, F2b, and clone2 batch 7 are the
same evidence base read a fourth time and add no new weight to those
numbers. What is NEW in CB, and what I judge on its own evidence, is:
the three-part result contract (CB-1), scope as mandatory action data
with stop-on-change (CB-2), image non-uniformity plus J37 codec false
refusal (CB-3), batch-growth-by-proven-validity (CB-4), locate
confirmations plus eval removal plus AT-SPI coverage reporting (CB-5),
act-now via the session driver (CB-6), latency measurement fixes plus
separate VM-to-laptop dispatch measurement (CB-7), evidence discipline
(CB-8), the deployment manifest (CB-9), overlay flicker vs think-time
separation (CB-10), and the semantic transaction executor itself
(CB-EXEC). CB's time estimates (prototype 2-3 days, broker merge plus
AT-SPI 1-2 weeks, benchmark a few more days) are estimates, not
measurements, and I do not count them as evidence for feasibility; the
prototype gate (B6) is what converts them into proof.

## 1. Per-proposal verdict table (every row covered, none skipped)

Legend: ADOPT means do it as proposed. MODIFY means do it with the stated
change; the gating conditions attached to each MODIFY are what must be
proven, by whom, before it proceeds. REJECT means do not do it (no
proposal is rejected in full; three parts inside merged rows are rejected
and are named). Exact duplicates are merged into one row citing every
source. Coverage: 32 rows covering all 40 proposals: ARCH A1-A10 (10
rows), GROUNDING P1-P9 (8 rows, P4 merged into A7), SPEED S0-S3 plus six
deletions (5 rows, D1 merged into S0, D2 into A6, D3 into S1, D4 into A7,
D5 into S2), CODEX-BREAKTHROUGH CB-1..CB-10 plus CB-EXEC (9 rows, CB-6
merged into S1, CB-7 merged into P6).

Tally in proposal terms: ADOPT 25 (A2, A6, D2, A7, P4, D4, A9, A10, P1,
P3, P6, P8, P9, S0, D1, CB-1, CB-2, CB-3, CB-4, CB-5, CB-7, CB-8, CB-9,
CB-10, CB-EXEC), MODIFY 15 (A1, A3, A4, A5, A8, P2, P5, P7, S1, D3, CB-6,
S2, D5, S3, D6), REJECT 0 in full, PENDING 0. The draft's tally was ADOPT
15, MODIFY 14, REJECT 0, PENDING 1 track over 30 proposals; the 10 new
ADOPTs and 1 new MODIFY are all CB proposals judged here for the first
time. No draft verdict changes letter in this round except where section
2 says so explicitly.

### 1.1 ARCH (worker-arch-review-log.md, 074c1d7)

| ID | Proposal | Verdict | Evidence, reasoning, and gating conditions |
|----|----------|---------|---------------------------------------------|
| A1 | Layer 0 persistent driver daemon (snapshot/execute/verify, structured-first) | MODIFY | Direction right: structured state is exact and cheap, and a state-holding driver is the only shape that stops paying setup per action. But the full-replacement claim has no existence proof (RTD C2, accepted by X1/X2/X3 and by the draft): session_driver.py runs cu.main() per command, code_exec.py is an in-process program model not a daemon, dom_act.py still grounds through image points, cdp.mjs drives agent-managed Chromium only, the bench was unrun at draft time. CB-EXEC now supplies the missing design specification (section 1.4): the prototype to be built is the semantic transaction executor, not a vague daemon. Gating conditions: a staged prototype must prove snapshot/execute/verify end to end on one live ws2 clone chat before anything is deleted (B6 lift, section 5). The prototype design must cover the single-runner lock as a task lock, pill visibility, the one-session-per-browser constraint, daemon crash and stale-state behavior, session-holding scope (RTD C5), and lifecycle across laptop sleep and reboot. No deletions until then. |
| A2 | Layer 1 pixels demoted to fallback-only, pixel-band labeled weak | ADOPT, with sequencing constraint | Proven by V1 (vision 58.6% first-try, Wilson 40.7%-74.5% per CB) and V3 (the code itself admits the band is necessary, not sufficient, cu.py:1023-1076). Constraint, from RTD and accepted by all four cross-responses and the draft: demote only after the router (P1) and its fallback trigger are proven; Zen chrome UI stays pixel-primary until P8 proves a structured path. P8 has now ANSWERED (section 0.2): chrome context is BLOCKED without a Zen restart, so the Zen-chrome constraint is now a recorded permanent-until-restart boundary, not a pending question. Fallback stays for canvas, games, video, Zen chrome UI. |
| A3 | Delete session supervisor tree | MODIFY | Direction right, timing conditional. The tree's real jobs are a named killable scope, cancel/stop, the session pill label, and the single-runner lock. Gating condition: delete only when the driver demonstrably holds scope plus cancel latch plus lock on a live run (B4 lift, section 5). Until then the supervisor is the lock holder, and deleting it risks two live runners and loses the cancel/stop path. The F1 failure cluster is partly environment faults, not supervisor-design faults; deleting the tree does not delete those modes. All four cross-responses and the draft agree. |
| A4 | Delete overlay daemon server (keep pill visibility) | MODIFY | The server is real (overlay.py 613 lines, Unix-socket server with holder accounting) and per-batch overlay acquire (315-349ms) is a genuine tax, so the end state (delete the server) is right. But the pill is the owner's only visibility into live runs and both replacements are unbuilt. Gating conditions, in sequence: (a) session-level pill first, acquire once per task, server KEPT, measured (this removes the per-batch tax without touching visibility); (b) driver-owned pill (or compositor-plugin indicator) only with proof it shows and clears, including no stale or missing pill when the driver dies mid-task; (c) delete the server only then (B3 lift, section 5). CB-10 adds a measurement condition to step (a): flicker and think-time are measured separately per phase, so a session-level pill is not credited or blamed for either without per-phase numbers. |
| A5 | Delete one-shot SSH loop (persistent Broker only) | MODIFY | Persistent-first is right (fresh SSH 4.43-5.29s per connect, corrected S0 numbers). The word "only" is REJECTED: the VM reaches the relay only through SSH, so this is not deletion of SSH but deletion of one-shot SSH in favor of multiplexed SSH plus broker RPC; and if the broker dies, one-shot SSH is how the relay gets restarted. Gating condition: fresh SSH stays as the documented fallback AND the recovery path. "Only" applies to the default path, never to the recovery path (B4 lift, section 5). |
| A6 + D2 | Delete file-based observation/action IPC (A6) / delete scp for JSON files (D2) | ADOPT for transport | JSON over the persistent channel (or in-process calls) replaces scp per step; each scp costs a fresh about 5s SSH. Scope condition, recorded by all four cross-responses and the draft: files stay as the audit and evidence trail (persisted observation artifacts, JSON plus JPEG, written by the driver); what dies is files as the transport, not files as the record. The JPEG still travels for the human VISION 2 check until the persistent channel carries bytes. Keep file IPC only as the fallback transport when no Broker is reachable. |
| A7 + P4 + D4 | Act-now after-image scope fix (A7) / after-image scope fix, both fields (P4) / delete screen-scope after-capture as produced today (D4) | ADOPT the both-fields shape; the delete-entirely half is REJECTED | Proven defective by construction (V-F6: first_action.py:661 still hardcodes observe_screen; draft V-A7: first_action.py:656 overwrote desktop_act's scope-matching after-capture, cu.py:2083-2091). The adopted shape, triple-sourced plus AMEND4 item 12: return BOTH after (scope-matching, chainable) and after_screen (full monitor, verification only, documented non-chainable); move the scope check before the overlay attempt; add a regression test. Execution is DEFERRED to AMEND4 item 12, already in flight on two lanes; the rewrite track consumes it and does not duplicate it. Item 12 has NOT landed yet (V-F6, V-F10) and its Codex-lane delivery is unconfirmed (V-F10); the deferral stands but the finalizer must confirm item 12 lands and the regression test passes. REJECTED part: deleting the envelope after image entirely (ARCH's delete half, and D2's withdrawn alternative). It loses the human-visible evidence and the frame-change signal for a saving of about 0.25s, which is noise; that trade fails the 06:07 criterion on accuracy. Timing note, from D3 and accepted by X1/X2/X3/XRT and the draft: the scope-as-capability refusal deletion (cu.py:1648/1649, screen observations refuse key/type) is sequenced WITH P2, not with this fix. While actions are still pixel-addressed, the refusal protects typing against a screen observation; once actions are element-ref addressed, scope is irrelevant and the refusal can go. |
| A8 | Delete pixel-band verification for structured targets | MODIFY, sequenced behind P5 | Direction right: the band is admitted necessary-not-sufficient and the DOM value check is sufficient and 100-1000x cheaper (0.002-0.015s). Gating condition: delete band-as-pass-signal only where the per-action DOM assert exists and is mandatory; until then the band stays as a diagnostic. Deleting before the assert set exists leaves actions with NO verification, which is worse than weak verification. This is RTD's sequencing, accepted by X2/X3 and by X1 in substance and by the draft. CB-1 is the contract this sequencing serves: verified=true requires a postcondition, and the P5 assert set is what supplies it. |
| A9 | Coordinate model to one system (CSS px element rects, converted once at the driver edge) | ADOPT for structured targets | The five-frame tower has five proven bug sites (F2b-1, C12, amend3 step 5, G28, after-scope trap); the one-conversion path already exists (fastpath.dom_rect_to_screen_point, verified). Dependency, accepted by all four cross-responses and the draft: A9 depends on AMEND4 items 5-6 landing (origin staleness). That dependency is now SATISFIED: items 5-6 landed as b44a5ea (refuse without window_bounds, live Hyprland re-read at ground time, refuse on mismatch). Item 1 (geometry, one unit system) already landed (cc964b2) and is the prerequisite. The one conversion still needs a correct absolute viewport origin and scale factors re-read per ground (C12 proved window-relative vs absolute origin is a live trap). The pixel fallback keeps its own frame internally; the router decides. |
| A10 | Acceptance test becomes 0-vision live benchmark on real ws2 clone chats | ADOPT as staged | Final gate: live 0-vision on real ws2 clone chats (clone1 Brave plus clone2 Chrome), DOM harvest, plan, execute, DOM verify, zero screenshots in the machine loop, accuracy at least 90% scored by DOM outcome (V12 sent-bubble gate), total wall time end to end including transport, one final screenshot kept as unscored human evidence (P9), owner approval per run. Staging: fixture 2-vision first (bench now on the branch, V-F8; PROBE-S2 running), P3 first (the live run needs the CDP path). The live-2-vision intermediate rung GOES as a hard gate and is kept only as a diagnostic; see section 2 item (a) for the full reasoning, where I side with XRT and the draft against X1/X2/X3. B1 is LIFTED (section 5). |

### 1.2 GROUNDING P1-P9 (worker-grounding-review-log.md, d1fc4e9)

| ID | Proposal | Verdict | Evidence, reasoning, and gating conditions |
|----|----------|---------|---------------------------------------------|
| P1 | DOM/a11y default router (Zen Marionette/BiDi, Chromium CDP, AT-SPI, screenshot last; encoded in code, not convention) | ADOPT | Two perception stacks with no routing rule drift to the worse one (works everywhere) instead of the better one (needs setup). Implementation requirements, accepted by all four cross-responses and the draft: encode the router in code as one function returning the perception source; fail closed to the labeled screenshot fallback; a per-target routing table proven per target before the default flips; a log line on every routing decision, so drift back to screenshots is visible instead of silent. Note: the a11y branch is thin for the apps in play (AT-SPI cannot see Zen; AT-SPI numbers unverified on this VM), so it mostly covers native apps that are not the live workload. Interim honest state: Brave tasks still route to screenshots until P3 lands. CB-5's routing (one contract across DOM/BiDi, AT-SPI, screenshot-crop backends) is the router's destination inside CB-EXEC; P1 is the router, CB-EXEC is the executor it routes into. |
| P2 | Element-ref action interface rewrite (live rect re-read at execution, screen-point action form, delete dom_rect_to_image_point from the live path) | MODIFY | Direction right and highest-leverage code change after P3: the round trip exact DOM rect to exact screen point to lossy image point and back is proven wasteful from source (fastpath.py:195-243, dom_act.py:312, cu.py:1000-1005), and it deletes the F2b-1, C12, amend3-step-5 bug class. Gating conditions (B5, section 5): (a) the stale-ref disagreement protocol is specified first (what happens when a live rect re-read disagrees with the plan: refuse, re-plan, or click stale, per case; lifecycle across a multi-action plan); AND (b) AMEND4 items 2-4 have landed. The landing limb is now SATISFIED at HEAD 2864be4: item 2 c1ea773, item 3 62b740e, item 4 72120aa (whose message records BrowserAdapter does not exist, narrowing the collision surface to the CLI act path, CodeExecBackend.act, and the first_action fallback). The protocol is now the single outstanding gate for B5. Running P2 in parallel with AMEND4 items 2-4 would have guaranteed merge collisions on the same functions; that risk is closed by the landing, not by the protocol. Delete dom_rect_to_image_point from the live path (keep for tests and legacy). The scope-as-capability refusal deletion lands in this step (see A7 row). CB-2's scope-in-action-data lands in this step with P2. |
| P3 | Brave relaunch with debugging port (controlled experiment, quiet window, never mid-batch; fallback agent-managed Chromium) | ADOPT as a controlled experiment | Single highest-leverage unblocker: the clone chats live in Brave, Brave holds no debugging port on its default profile (cdp.mjs comment verified verbatim), so the CDP path cannot reach them today. Conditions, accepted by all four cross-responses and the draft: quiet window owned by the coordinator, never mid-batch (clone1 is mid-batch-9 now; PROBE-P3 reported NOT-RUN at 7b1006a for exactly this reason); verify /json/list shows the Muse tab and login intact; run observe plus harvest plus one fill plus assert on a scratch input. Recorded additions: CDP on port 9223 exposes the logged-in browser to any local process (security consideration, never mentioned by GROUNDING); the Chromium fallback is a migration with re-login and clone reconfiguration, not a fallback, and needs its own login-persistence check before it is relied on; cdp.mjs notes shadow-DOM elements have null box_model, and Messenger's DOM shape against that gap is unexamined. BLOCK on any live-task migration until the experiment passes. If P3 fails (Brave refuses the port and the Chromium migration is too disruptive), the DOM-first live path loses its highest-leverage unlock and the whole program re-plans around Zen Marionette only; report that plainly, not worked around silently. |
| P5 | DOM verification mandatory (focus_check and type_check required, not optional hooks; CDP fill read-back and assert polling the model) | MODIFY | Direction right; the code admits the band is insufficient. The blanket mandate is BLOCKED as stated: the assert set does not exist for every action type (focus_check/type_check are still optional hooks, D1 V13), and no per-action exception list exists. Gating conditions: DOM verification becomes mandatory PER ACTION TYPE as its assert lands; an explicit per-action exception list names the actions where DOM assert is impossible (scroll position, hover state) and pixel stays the only signal; the band stays as a diagnostic until then. A blanket mandate now means false refusals on working flows or vacuous asserts (false confidence). CB-1 is the contract P5 implements: verified=true only when a postcondition holds, and the P5 assert set is the postcondition machinery per action type. This MODIFY is converged across all four cross-responses and the draft. |
| P6 + CB-7 | Measure the vision call (P6) / latency measurement fixes plus separate VM-to-laptop dispatch measurement (CB-7) | ADOPT, with specification fix | Cheapest items on the list and preconditions for honest speed claims: capture is 15-30ms and DOM rects 0.030s, but the model read that locates the target is seconds and timed nowhere. Bundle with S0. Specification fix, from RTD and accepted by all four cross-responses and the draft: the model call happens in the calling agent's loop, outside cu.py, so the proposal must specify the timestamp points (observation delivered to the agent vs located target returned) and the owner of the logging (the harness, not cu.py), or it will be recorded as done when only capture timing is logged again. CB-7 adds three concrete fixes, all ADOPTED: timestamp the first pointer action (act-now currently logs order_to_overlay from wrapper start, not from the VM command, and target_breached compares the whole batch against the 30s threshold instead of first-action latency); measure VM-to-laptop dispatch separately with the same workload under fresh SSH and connection reuse (CB proves no record supports the 11.6s of 12.26s as SSH dispatch, so the 95% claim is suspended as a decision input until this measurement exists); and stop quoting order-to-overlay as user-perceived latency until the VM-side start is timestamped. Until these numbers are in the logs, every speed claim about the screenshot path is incomplete, and nobody may claim the 10s target is met. |
| P7 | Session handover protocol (one protocol per browser per task phase, BiDi ground then Marionette input or stay on one) | MODIFY | The one-session constraint is proven (4 runs, Firefox allows exactly one remote session per instance), so a protocol is needed IF a task genuinely needs two protocols. Gating condition: first answer whether Marionette-only suffices (the benchmark already runs Marionette-only, harvest plus input, and zen_dom harvest IS Marionette). Write the handover protocol only if a task genuinely needs BiDi for grounding plus Marionette for input. Price noted: a handover costs 4-7s per switch (BiDi new 1.51-2.77s fresh, Marionette attach 2.65-4.12s), comparable to the SSH tax being deleted. Small and non-blocking either way. All four cross-responses converge on MODIFY, as does the draft. |
| P8 | Zen chrome Marionette context test (set_context chrome) | ADOPT as a bounded probe, now ANSWERED | Premise verified (V-F7: no chrome-context support in zen_cli.py today). The probe has now RUN and ANSWERED (section 0.2, commit 3790901): chrome context is BLOCKED without a Zen restart (HTTP 500, MOZ_REMOTE_ALLOW_SYSTEM_ACCESS required); C12 reproduced live. If it works, the last screenshot-only surface falls; it does not work without a restart, so keep screenshots ONLY for chrome UI and record that boundary explicitly. Conditions now closed: no re-probe without an owner-approved Zen restart; the one-session constraint was respected in the test design; do not gate anything on it; do not let it become a rabbit hole. AT-SPI cannot see Zen, so that path is closed; do not spend more time on it. The verdict stays ADOPT because the probe was the proposal and it ran; its RESULT is negative, and the negative result is itself the deliverable (the boundary is now measured fact). |
| P9 | Keep one screenshot for the human (VISION 2 stays, machine scores by DOM) | ADOPT | Correct division: screenshots are a human evidence channel, not a machine perception channel. VISION 2 stays as unscored human evidence; the machine scores by DOM outcome. Wording correction, from RTD and accepted by all four cross-responses and the draft: VISION 2 is the agent looking at the threads and reporting to the human, not the owner looking directly, so it is the agent's final sanity check reported to the human. Cost is about 0.25s plus one vision read, noise against the total. Attached to A10. |

### 1.3 SPEED S0-S3 plus six deletions (worker-speed-review-log.md, a4ecb49)

| ID | Proposal | Verdict | Evidence, reasoning, and gating conditions |
|----|----------|---------|---------------------------------------------|
| S0 + D1 | Step 0 persistent SSH multiplexing, do now (S0) / delete fresh SSH per call (D1) | ADOPT on CORRECTED numbers | Fresh SSH 4.43-5.29s (7 samples, confirmed four ways); multiplexed 0.91-1.46s (11 samples, rc=0, master verified alive). Saving about 3.2-3.5s per connection, about 3.5-5x, NOT 460x and NOT 0.01s. SPEED's 0.01s figure matches a failed-fast connection (master not up, rc=255, D1's diagnosis, accepted by RTD and D3); SPEED's log records no return codes and no master-liveness check. Corrected expectation: per act-now (3 connects) about 16s becomes about 5-6s, not about 2s; per observe (2 connects) about 6-8s saved. SPEED's 1.6x per-task estimate was built on 0.01s and must NOT be quoted; D1's revised roughly 1.3-1.4x on a CL2-MSG-class task is the working figure until a recompute on the corrected numbers. The 460x and 1.6x figures are DEAD and are never quoted again. Conditions: implement the fallback explicitly (any multiplex failure falls back to a fresh connect, slow but correct); log master death; per-socket watchdog, not global (a half-dead master can hang rather than fail cleanly; ControlPersist=600 can leave a stale master holding a dead Tailscale route); the 1-day soak test runs IN PARALLEL, advisory, not a gate (section 7, PROBE-S0). The residual about 1.1-1.2s per call (per-session sshd and shell setup, which multiplexing does not remove) is itself an argument for S1 and A1. Do it now: no agent-logic code change, fallback safe. |
| S1 + D3 + CB-6 | Step 1 act-now over the persistent relay broker (S1) / delete per-batch session spawn (D3) / act-now uses the long-lived session driver, one owner, sequential queue (CB-6) | MODIFY, proof-first | Direction right: the per-batch session spawn is a real tax (0.4-2.1s) plus a real failure mode (20s deadline, timeout never falls back, council 1 B1), and JSON over the same channel kills the scp round trips. CB-6 sharpens the design: act-now routes through the session driver instead of spawning a cu.py session per batch, with one owner of pointer, overlay, and the Firefox session and a sequential queue, which also answers RTD C5 (single-owner socket semantics under concurrent VM workers: serialize, do not compete). But S1 is a BUILD, not a switch: the relay is alive (PID 1821, socket exists, verified) yet zero references to session_remote or Broker exist in first_action.py or cu.py (V-F2, verified by me and by X1/X2/X3), so the broker path from the VM is unproven end to end, and the single-owner socket semantics under concurrent VM workers are unexamined until the proof run examines them. Gating conditions: prove one live batch end to end over the broker from the VM first, then delete the per-batch spawn; keep the spawn as fallback until proven. Session-level pill (keep the overlay server) lands in the same step. Expected per-batch mechanism about 0.5s plus the overlay item after S1. All four cross-responses converge on MODIFY, as does the draft. |
| S2 + D5 | Step 2 DOM-first plus code-exec plus checkpoint verification, CU_CODE_EXEC=1 on (S2) / delete per-action model call as the default (D5) | MODIFY, gated | The 10x path, already built and merged (code_exec.py 880 lines, Pick 1 winner, commits 714e4f9, 84b88bb, 2e2aeff, merge 453adc4), and the flag is OFF in the live path (verified live: CU_CODE_EXEC unset on the laptop). But the blanket flip is BLOCKED (B2, section 5): Y1b council 3 BLOCKED Phase A on 84b88bb with 14/20 probes passing and 3 real fails (1e f-string chr NameError; 2a codemode wall preemption, error raised only after the C loop finished; 2b code_exec wall preemption, elapsed 6.20s, ok=True with NO error, silent success), and the named gate (2-vision benchmark) has never run. PROBE-S2 confirms at 06:37 +07 that the 3 fails are STILL OPEN (V-F1). A fixture bench pass alone does not fix the 3 real fails. Gating conditions, in order: (a) run the fixture 2-vision bench green (bench now on the branch, V-F8; PROBE-S2 running); (b) fix the 3 Y1b real fails; (c) flip the flag for ONE live task class (clone chat sends) with act-now as fallback, measure, then expand. The "10x path" label is corrected to 3-5x on unmeasured model inference time (SPEED's own honest limit: 30-60s if vision reading dominates); the mechanism can be about 1s, the model is the remaining unknown, and P6 must measure it before anyone claims the 10s target. CB-4 constrains the flip: code-exec programs re-validate per risky step (live rect re-read, DOM assert) and batch size grows only on proven validity; the 32-action cap stays a cap, never a target. Code-exec becomes the default for the proven task class first; the stepwise loop stays the fallback for unknown shapes only. |
| S3 | Step 3 laptop-side task runner, only if Step 2 plateaus | MODIFY, fold into A1; plateau defined numerically first | S3 substantially overlaps A1: a laptop-side runner that grounds, acts, and verifies locally and streams back compact state IS the A1 driver daemon approached from the other side. One design decision, not two builds; do not build a separate runner alongside A1. CB-EXEC is the merged design specification for this one build (section 1.4). Gating condition: the plateau criterion must be defined NUMERICALLY BEFORE the S2 flip starts (threshold, run count, decision owner), so the trigger is not argued later. An undefined plateau either never triggers or triggers on one bad run. The decision itself happens only after steps 0-8 of section 3 are measured. Open condition with owner: section 6. All four cross-responses agree on the merge and on the numerical definition; none of the councils supplied the numbers, so this position specifies the form, the owner, and the deadline, not invented numbers. |
| D6 | Delete 120s freshness window as a gate on DOM work | MODIFY, scoped | For DOM-grounded work, re-read the DOM (0.030s) instead of refusing for staleness; the window is a patch for vision coordinates, not a law. Correction, from RTD and accepted by X1/X2/X3 and the draft: the refusal at cu.py:773 also guards against future-clock observations, and a blanket delete removes the clock-skew guard. Gating condition: keep the future-clock refusal, drop only the age refusal for DOM paths. Keep the window for pixel-addressed work, where staleness is real and the refusal protects against acting on a dead frame. |

### 1.4 CODEX-BREAKTHROUGH CB-1..CB-10 + CB-EXEC (codex-breakthrough-report.md, 2596287)

| ID | Proposal | Verdict | Evidence, reasoning, and gating conditions |
|----|----------|---------|---------------------------------------------|
| CB-1 | Three-part result contract (input_sent / verified=true only with postcondition) | ADOPT | The strongest single finding in CB, proven from source: cu.py:1541-1549 admits the desktop check knows only pointer position, not which UI element received the event; cu.py:1580-1592 refuses only on pointer deviation over 3px, which checks mouse movement, not target receipt; cu.py:1806-1809 compares pixel hashes, and a changed image (including animation) does not confirm action success; a11y.py:204-219 treats do_action returning true as a completed click with no post-state check; installed first_action.py:422-439 turns cu.py ok or enough completed actions into envelope ok=true, so a click on empty pixels at the right coordinates reports success. G30 is the live instance: batches reported ok/completed, message never sent, clicks 64-75px above the real field. The contract change: every result separates input_sent (input was dispatched) from verified (postcondition holds); verified=true requires a postcondition, never a pointer position or a pixel hash. Sequencing: lands WITH P5 (P5's per-action-type assert set is the postcondition machinery that makes the contract enforceable); the contract is stated now, enforced per action type as its assert lands. A result of ok=true with no postcondition is a false success and counts as a failure in every benchmark (section 4). |
| CB-2 | Scope mandatory in action data, scope change stops the batch | ADOPT | Proven from source and record: desktop_act allows key/type only on window observations (cu.py:1473-1475), but first_action.py always captures after with observe_screen (V-F6) and _fresh_observation captures full screen when the observation is missing, stale, or errored, then runs the whole action list anyway (first_action.py:289-315 per CB on the installed copy; repo copy lines 353 and 661 show the same observe_screen paths, V-F6). J40 is the live instance: a point from a window image used on a full-screen image missed the button by about (+45,+12) px while the command still returned ok; J35 records a window observation 1863x1176 against a full-screen after 1920x1200. The rule: scope is a mandatory part of action data (window or tab, frame, observation ID); a new observation with a different scope stops the batch instead of silently swapping frames and continuing. Sequencing, split: the stop-on-scope-change guard lands with AMEND4 item 12 / A7 (same file, first_action.py, same defect family); scope carried in action data lands with P2 (the interface rewrite). The both-fields A7 fix does not by itself stop a batch on scope change; CB-2 adds the stop rule, and I adopt it as the missing half. |
| CB-3 | Vision error taxonomy plus image uniformity plus J37 codec false refusal | ADOPT | Three cheap, evidence-backed fixes bundled as one row. (a) Image uniformity: observe caps width at 960px (cu.py:2303) and saves JPEG q90 (cu.py:807-863), while act-now captures fresh at max_width=1920 (first_action.py:313 per CB; repo copy line 661 shows the same 1920), so the model sees different resolution and detail by path. Fix: one capture size and quality path for model-visible images; the mapping code can compensate arithmetic scale, but the model still has to recognize the target from images of different detail. (b) J37: preflight compares decoded JPEG against a fresh uncompressed capture with a patch threshold of 6 (cu.py:979-1000 per CB; repo copy lines 1010-1020 show the same threshold-6 patch code, V-F3); J37 reports a patch around the cursor differing by 6.627 and causing an unstable refusal (error file lines 832-837; entry verified by me, V-F4). Fix: separate codec false refusal from real screen change (compare on the same encoding, or use lossless PNG for preflight). (c) Vision error taxonomy: classify misses (wrong target vs frame error vs scale) instead of one "vision missed" bucket, so the next fix targets the right cause; E2's 58.6% (Wilson 40.7%-74.5% per CB) is too small and too narrow to support a single-cause story, and CB shows scale alone does not explain it (screen 1920x1200 scale 1, cu.py:973-977 maps through the capture region). Bundle with P6/S0 work; no gate beyond the P6 timestamp specification. |
| CB-4 | Batch growth by proven validity (90% per-click math: 20 clicks 12.2%, 32 clicks 3.4%) | ADOPT as policy | The math is arithmetic illustration, not measurement: at 90% per-click success with independent errors, 20 clicks all correct first try is 12.2% and 32 clicks is 3.4%; CB states plainly that real errors correlate, so I do not quote these as measured rates. The policy is right and I adopt it: batch size grows only when the executor proves the next steps are still valid, not because more coordinates fit in one image. Desktop and code-exec both accept up to 32 actions per batch today (V-F3), and their guards check focus, window, geometry, and screen before acting but never check that the first click opened the right page, focused the right field, or did not stale the later coordinates; after-capture happens only at batch end. Consequence for S2/D5: a code-exec program is not a blind 32-action batch; it re-validates per risky step (live rect re-read, DOM assert, postcondition), and steps that can change page or focus carry their own precondition and postcondition. The 32-action cap stays a cap, never a target. This policy is a constraint on the S2 flip and on CB-EXEC design, not a separate build. |
| CB-5 | Common executor routing plus Zen adapter plus locate confirms visible/interactive/uncovered/stable/unique plus remove unrestricted zen_dom eval from default interface plus AT-SPI coverage reporting | ADOPT, split sequencing | (a) Locate confirms: zen_dom locate only runs querySelector and reads getBoundingClientRect (lines 172-185 per CB); it does not confirm the element is visible, interactive, uncovered, stable, or uniquely selected. An exact CSS rect is not the right target or a clickable point. ADOPT: locate must confirm all five before returning a target, landing with P1/P2 work. (b) Remove unrestricted zen_dom eval from the default agent interface: the CLI exposes eval ("run JS in the current tab", V-F5) and the agent interface should expose only bounded read/query APIs, keeping eval for an explicit debug mode. ADOPT, landing with P2 (the interface rewrite is the moment the default interface is redefined). (c) AT-SPI coverage reporting: a11y.py:83-104 caps traversal at 500 nodes or 2s, returns at most 80 items, and sets a truncated flag; query locks after a fastpath flag (lines 118-139 per CB). ADOPT: the backend must report its coverage and the router must fall through to DOM or image when the tree is insufficient. (d) Common executor routing plus Zen adapter under one contract: this is CB-EXEC's routing, ADOPTED as part of CB-EXEC (same B6 prototype gate, section 1.4). Caveat, per C1: CB could not verify the 66-element / 5-of-5 sweep claim from local evidence, and it did not test BiDi, Marionette, or AT-SPI live, so the Zen-adapter claims rest on code reading plus clone2's single measurement until the prototype gate proves them. |
| CB-6 | Act-now uses the long-lived session driver, one owner, sequential queue | MODIFY, merged into S1 | Merged with S1+D3 (section 1.3): same change, CB's framing. The repo has the session_remote broker and the JSON-lines session driver (session_remote.py:460-520, session_driver.py:59-75 per CB), but act-now builds a cu.py session per invocation (first_action.py:172-178, 403-405 per CB) and zen_dom opens and closes a session per command, so the new wrapper does not use the durable session path that exists. CB-6 adds the missing design answers: one owner of pointer, overlay, and the Firefox session, with a sequential queue, and no competing BiDi plus Marionette clients because the record shows two protocols share one Zen slot. ADOPT the design; MODIFY the sequencing exactly as S1: prove one live batch end to end over the broker from the VM first, then delete the per-batch spawn; keep the spawn as fallback until proven. |
| CB-7 | Latency measurement fixes plus measure VM-to-laptop dispatch separately | ADOPT, merged into P6 | Merged with P6 (section 1.2): same measurement work, CB's specifics. CB's act-now JSONL synthesis (199 lines, p50 order-to-overlay 337.5 ms, max 368.4 ms; p50 total wrapper 2.288 s, max 6.95 s; 195 session, 4 fallback, 0 timeout; 167 ok=true, 32 ok=false) measures executor time and status, not click hit rate or task success, and the log has no target element or postcondition to tell whether ok=true hit the target. The 95% SSH claim is UNSUPPORTED: the act-now log starts after the command reaches the laptop, so it cannot measure SSH, and the other cited number (service 11.611 s, gap 1208.942 s) is a different measurement that neither proves nor refutes it. ADOPT: timestamp first pointer action, fix target_breached to measure first-action latency not whole-batch time, and measure VM-to-laptop dispatch separately with the same workload under fresh SSH and reuse. Until then the SSH 95% figure is suspended as a decision input. |
| CB-8 | Evidence discipline (DONE is a state of specific evidence) | ADOPT as process rule | CB shows the todolist marks items DONE on direction or fixture evidence that does not prove the real-app claim: the fixture form ran 0.64s and 15 steps in real Zen, but the page is a Polygon-process simulation, not the Polygon upload task, and the report itself records no same-task baseline; 13/13 verified actions cannot become a 90% commitment for another app; held-out new app plus independent agent is PARTIAL; J10 real think-time is OPEN. The rule: DONE means a specific named evidence exists (command, output, commit, time log), not that a direction was decided or a fixture passed. No code, no gate, immediate effect. I adopt it as the standing rule for every claim in this program, including my own verdicts: where I cite a number, its source is named; where evidence is missing, I say so (sections 0.1, 0.3, 7). |
| CB-9 | Deployment manifest (lock source commit plus installed artifact plus log) | ADOPT, precondition to acceptance runs | CB proves the gap from its own checkout: HEAD 4500a18, remote-tracking ref behind 622, first_action.py untracked there, installed cu.py carrying two extra act-now branches not in the repo checkout. My V-F9 corrects one part (first_action.py IS tracked on todolist-push now), but the load-bearing gap stands: the running laptop artifacts diverge from the source checkout, which blocks repeatable review, test, and deploy. The fix is cheap: before any benchmark is used as a release gate, record a manifest locking the source commit, the installed artifact, and the log of the same build. I adopt CB-9 as a PRECONDITION to acceptance runs (fixture bench, 100-task benchmark, live 0-vision), not as a gate on S0 or P6. Without a manifest, a pass cannot be attributed to a build. |
| CB-10 | Overlay flicker vs think-time separate, per-phase measurements | ADOPT | CB shows the two questions were conflated: the todolist records 0 repaints and 0 events for idle overlay, but the LIQUID background test never ran because the plugin was not loaded, so there is no evidence the original flicker was reproduced or fixed; and think-time is unmeasured with J10 OPEN. Do not attribute either to SSH or screenshots without per-phase numbers. ADOPT: measure overlay flicker and model think-time as separate phases with their own numbers, feeding A4 (the session-level pill measurement must show flicker separately) and P6 (think-time is part of the vision-call measurement). No gate beyond the P6 timestamp specification. |
| CB-EXEC | The semantic transaction executor itself (semantic targets, preconditions, real mouse/keyboard, postconditions, retry only when surely unsent; one local broker; DOM/BiDi plus AT-SPI plus screenshot-crop backends under one contract; vision as fallback; 100 held-out tasks benchmark, 90% defined as task success, about 96/100 for 95% confidence) | ADOPT as the design specification for the A1/S3 merged build, B6 prototype gate unchanged | This is the breakthrough design, and it is the correct one under the 06:07 criterion: it is the only proposal in the whole round that names the actual defect (the contract reports input dispatch as success) and fixes it at the contract level instead of at the sensor level. The executor resolves a semantic target (role and name, or selector/ref from a fresh snapshot) on the laptop with the fitting backend, checks preconditions (unique, visible, enabled, right window, geometry and focus unchanged), acts with real mouse/keyboard or a confirmed-fitting DOM/API action, checks a postcondition (dialog closed, URL changed, field holds the value, checked state flipped, new text appeared), and retries only when it knows for sure no input was sent, checking state before replaying any action that could send or delete. Scope rides in the action data (CB-2). Batch size follows proven validity (CB-4). Backends (DOM/BiDi, AT-SPI, screenshot crop) sit under one contract with vision as fallback, not as parallel paths. One local broker owns session, overlay, desktop input, and browser session (CB-6). Where CB-EXEC differs from A1 as ARCH stated it: A1 is a shape (persistent driver, snapshot/execute/verify); CB-EXEC is the contract that shape must implement. I adopt CB-EXEC as the design specification for the A1/S3 merged build, not as a second build. The B6 prototype gate is UNCHANGED: the prototype must prove the contract end to end on one live ws2 clone chat before anything is deleted, and the full acceptance is the 100-task held-out benchmark plus the live 0-vision ws2 run (section 4). CB's time estimates (2-3 days prototype, 1-2 weeks broker merge plus AT-SPI, a few more days benchmark) are estimates, not measurements; they do not move the gate. Risks CB names and I accept as prototype requirements: one Zen remote session slot with a hung session blocking every client; controls needing real mouse events; iframe, shadow DOM, canvas, native file picker, and Wayland extent gaps; DOM fill not equal to real typing; UI changing between read and click (answered by live rect re-read at execution, P2). |

## 2. Settled residual disagreements (my positions as final reviewer)

(a) A10 live-2-vision rung stays or goes. GOES as a hard gate; kept only
as a diagnostic. I side with XRT and the draft AGAINST X1/X2/X3, who
keep the ladder. My reasoning, on the evidence, not on vote count (C1:
agreement is not independent confirmation). In the bench design VISION 1
is a DOM harvest, not a screenshot, and VISION 2 is a human look at the
threads; the machine never locates from pixels in either form. Live
2-vision and live 0-vision-with-P9-screenshot are the same machine
behavior; they differ only in whether the human looks at live threads or
at a screenshot, and the P9 screenshot IS the human outcome check in the
0-vision run. RTD's strongest limb, that DOM can report a bubble present
while the rendered thread shows something else (wrong thread, hidden
render), is answered by the P9 screenshot itself: a screenshot of the
right thread shows the bubble present or absent, and a bubble in the
wrong thread shows absent in the right thread's screenshot. The live
look adds scrolling and multi-thread inspection, which one screenshot per
thread also supplies. The councils' stated purpose for the rung ("the live
2-vision run is the proof that DOM works on real Messenger pages") is
served equally by the live 0-vision run itself, which also runs DOM on
real Messenger pages and scores by DOM outcome. The extra run buys
replication and localization, not a distinct proof, and it costs a second
live run on real clone chats (disruption, coordination, owner approval)
for that replication. Under the 06:07 criterion a gate must protect
accuracy or speed measurably, and this rung protects neither beyond what
the 0-vision run plus P9 already protects. CB-EXEC reinforces the point
from the other side: its acceptance is outcome-scored on held-out tasks,
not vision-count-scored, so the gate that matters is the outcome, not how
many vision calls the machine made. The rung is retained as a diagnostic:
if the live 0-vision run fails, the team may run live 2-vision to
localize (script vs DOM path), but it is not a required rung. A10 verdict:
ADOPT as staged (section 1.1).

(b) Ordering: S2 before vs after P1/P5. P1/P5 go BEFORE the S2 flip. I
side with X3 and the draft against D1 and RTD's numbered order. S2 is
"DOM-first plus code-exec plus checkpoint verification", and the
checkpoint verification part IS P5. Flipping S2 without P5 means flipping
code-exec while DOM verification is still optional hooks (D1 V13,
first_action.py:597-613), a window in which the live loop runs code-exec
with pixel-band verification only. P1 (router) and P5 (mandatory DOM
verification per action type as asserts land) are rewiring of existing
code with no collision, so doing them first costs one small step and
removes that window. I refine the draft's position in one respect: what
must precede the flip is P1/P5 FOR THE S2 TASK CLASS (clone chat sends),
not the general router for every target; the general per-target routing
table is proven per target as it lands. CB-1 sharpens the same point: the
flip must not ship a loop whose ok=true cannot mean verified, and P5 for
the class is what makes ok=true mean verified for that class. X2's "S2
before P1/P2/P5" is rejected for P1/P5 but accepted for P2: the S2
one-class flip does not depend on P2, and P2 is collision-blocked until
B5 lifts, so S2 precedes P2. Full order: fixture bench run plus Y1b
fixes, then P1/P5 for the class, then the S2 one-class flip, then P2.

(c) AMEND4 items 3-4 priority. MOOT in fact, and the draft's split
reasoning stands as history. Items 3 and 4 LANDED during the
adjudication (62b740e, 72120aa). The deprioritization debate is over;
their landed work serves the diagnostic band, and the kill rule at
reconciliation (section 6) still applies if the rewrite deletes its
target. The live triage question is now items 9, 10, 11, 12 (section 6).

(d) Numerical-plateau definition for A1/S3. OPEN condition, with owner,
form, and deadline settled and numbers explicitly NOT invented here. All
four cross-responses and the draft agree it must be defined numerically
BEFORE the S2 flip; none of them supplied the numbers. Settled: the
definition is owned by the coordinator (COORD-CLICK-3), is set before the
S2 flip (section 3 step 6), and has the form RTD specified (Step 2 live
median wall time above a stated threshold for a stated number of runs
after the flag flip), with the coordinator as decision owner. The numbers
themselves are the open item: they are set from the fixture bench plus
first live runs baseline, not guessed in this position. Until the
definition exists, the A1/S3 decision cannot trigger; an undefined
plateau either never triggers or triggers on one bad run.

(e) Stale-ref disagreement protocol. OPEN, with the B5 narrowed lift
condition settled. The protocol is the missing piece GROUNDING P2 never
specifies (V-X5, XRT): the guard mechanism exists (cdp.mjs 90s plus URL
check, GroundPoints live re-validation) but no decision protocol exists
for the case the live rect re-read disagrees with the plan. Settled lift
condition for B5 (XRT's narrowed form, accepted by X1/X2/X3 and the
draft): the stale-ref disagreement protocol is specified (refuse,
re-plan, or click stale, per case, plus the lifecycle across a
multi-action plan), AND (AMEND4 items 2-4 have landed OR items 3-4 are
deprioritized per the D1/D3 triage with item 2 landed). At HEAD 2864be4
items 2, 3, and 4 have all landed (c1ea773, 62b740e, 72120aa), so the
second limb is SATISFIED and the protocol is now the single outstanding
gate for B5. The protocol writer is named in section 6; it is due before
P2 starts.

(f) V11 TODO wording. RTD's phrasing is NOT adopted as phrased. X3
verified MutationObserver code exists at zen_dom.py:983 (arm_typed_flag
at :948 in the file X3 read); the draft verified it again at HEAD
62b740e (arm_typed_flag defined in zen_dom.py, MutationObserver JS
string inside it, called from production code at dom_act.py:433-434).
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

(g) CB-EXEC vs A1/S3: one build, not two. ARCH's A1, SPEED's S3, and
CB-EXEC converge on one destination (a local executor that grounds,
acts, and verifies on the laptop and streams back compact state). I
settle this as ONE build with ONE design specification (CB-EXEC) and ONE
gate (B6 prototype plus section 4 acceptance). Any lane that builds a
second runner, a second daemon, or a second executor alongside it is
stopped (section 5). The draft's A1/S3 merge is confirmed and extended
to CB-EXEC.

(h) The draft's B1 lift vs the councils' ladder. Addressed in (a) above.
I confirm the draft. The three cross-responses that keep the ladder
(X1/X2/X3) all concede the machine behavior is identical in both forms;
their remaining argument is localization value, which the diagnostic
retention already supplies without making it a gate.

## 3. Order of work (numbered sequence with explicit gates)

Every step is independently verifiable, every step lands a measured win
before the next step starts, and no step depends on a bet (P3, P8, S2
measurement) that has not yet paid off. Cost is irrelevant by the
criterion, but sequencing by dependency is not cost, it is correctness:
a daemon built from unproven parts inherits their failure modes.

0. S0 plus P6 plus CB-7 plus CB-3, now. Persistent SSH multiplexing with
   explicit fallback, master-death logging, per-socket watchdog; P6
   vision-call measurement with the timestamp points and harness owner
   specified in section 1.2; CB-7 latency fixes (first-pointer timestamp,
   target_breached fixed, VM-to-laptop dispatch measured separately);
   CB-3 image uniformity plus J37 codec separation. Gate to step 1:
   fallback explicit and watchdog in place. The 1-day soak test starts
   the same day and runs IN PARALLEL, advisory, not a gate (a master
   death falls back to fresh SSH, slow but correct). CB-8 evidence
   discipline takes effect immediately as a process rule.
1. AMEND4 continues in parallel, slower, per the owner 06:09 TWO TRACKS
   rule (section 6). Item 12 (A7/P4 plus CB-2 stop-guard) lands via the
   in-flight run; verify the regression test and confirm the Codex-lane
   delivery (V-F10). Gate: the rewrite track makes no parallel edits to
   the same functions AMEND4 is working on (the two tracks run in
   sequence per item on shared files, not in parallel on the same
   functions, or the merge will collide).
2. P3 Brave relaunch experiment, in a real quiet window between clone
   batches, coordinator-owned, never mid-batch (PROBE-P3 NOT-RUN at
   7b1006a because clone1 batch 9 is open). P8 is answered and needs no
   further work. Gate to any live DOM work: P3 passes (login intact,
   /json/list shows the Muse tab, one fill plus assert on a scratch
   input) or the Chromium fallback is proven with its own
   login-persistence check. No live-task migration until then. If P3
   fails, re-plan around Zen Marionette only and report it plainly.
3. Fixture 2-vision bench run. Bench and fixture are on todolist-push
   now (V-F8); PROBE-S2 is running the fixture run. This step does not
   depend on P3 (headless Firefox, local fixture) and may run in parallel
   with step 2. Gate to step 6: the fixture run passes. The program's
   gate cannot be an unrun script. CB-9 manifest is recorded for the
   exact build under test.
4. Fix the 3 Y1b real fails on code-exec (1e, 2a, 2b). Gate to step 6:
   the fails are fixed (B2 lift, part 1). PROBE-S2 confirms they are
   STILL OPEN at 06:37 +07 (V-F1). Owner: section 6.
5. P1 router plus P5 asserts per action type FOR THE S2 TASK CLASS, plus
   CB-1 contract stated, plus CB-5 locate confirmations and eval removal.
   Rewiring of existing hooks; P5 per action type as its assert lands,
   plus the explicit exception list. Gate to step 6: the router logs its
   routing decisions, and the P5 assert set covers the S2 task class
   (clone chat sends). See item (b) above for why this step precedes the
   S2 flip.
6. Define the numerical plateau (coordinator, before the flip; section
   6), then the S2 flip for ONE live task class (clone chat sends) with
   act-now as fallback. CB-4 batch-validity constraint applies to
   code-exec programs (re-validate per risky step). Measure model-call
   count and wall time. Gate to expansion: measured on one class; expand
   only on measurement.
7. P2 element-ref interface rewrite, after B5 lifts (stale-ref protocol
   specified; items 2-4 landed limb satisfied at HEAD 2864be4). A9
   one-system coordinates land in this step (depends on AMEND4 items 5-6,
   satisfied by b44a5ea). The scope-as-capability refusal deletion lands
   in this step, not with A7. CB-2 scope-in-action-data lands in this
   step. Gate to step 8: P2 proven on the S2 task class with DOM
   verification mandatory.
8. S1/CB-6 broker path proof from the VM on one live batch, then delete
   the per-batch spawn. Session-level pill (server kept) in the same
   step, measured per CB-10 (flicker separate from think-time). P7's
   Marionette-only question is answered before any handover protocol is
   written. Gate to step 9: one live batch proven end to end over the
   broker from the VM.
9. A1/S3/CB-EXEC merged prototype: the semantic transaction executor per
   the CB-EXEC contract (semantic target, preconditions, real input,
   postcondition, retry only when surely unsent, one local broker, backends
   under one contract, vision fallback). Gate to step 10: prototype proven
   snapshot/execute/verify end to end on one live ws2 clone chat (B6
   lift).
10. A3/A4/A5 deletions last, each gated on its replacement proving (A3:
    driver holds scope plus cancel latch plus lock; A4: session-level
    pill measured, then driver-owned pill crash proof, then delete the
    server; A5: broker proven on the VM path with one-shot SSH kept as
    recovery).
11. Acceptance: fixture 2-vision (step 3), then the 100-task held-out
    benchmark (section 4), then live 0-vision on real ws2 clone chats as
    the final gate (section 4), after P3 and P2. Live 2-vision is a
    diagnostic only if the live 0-vision run fails.

## 4. Acceptance test decision

Decision: the acceptance test is a LADDER with three required rungs and
one diagnostic option, plus a manifest precondition. The final gate is
the live 0-vision benchmark on real ws2 clone chats. The live 2-vision
run is NOT a required rung. The 100-task held-out benchmark is REQUIRED,
not optional: it is the only rung that tests generality (new apps, new
content, new layout) instead of the two tasks the team already knows.

- Precondition (required before any rung scores): CB-9 deployment
  manifest. The source commit, the installed artifact, and the log of
  the same build are recorded for the exact build under test. Without a
  manifest, a pass cannot be attributed to a build, and the rung does
  not count.
- Rung 1 (required, first): fixture 2-vision benchmark. Headless Firefox,
  local fixture. It has never run at all (BUILD ONLY); the whole
  program's gate cannot be an unrun script. Bench and fixture are on
  todolist-push now (V-F8); PROBE-S2 is running it. Pass criteria: the
  script's own gates (V12 sent-bubble gate after each message, scoring
  by OUTCOME in the thread DOM, never point-in-box). This rung does not
  depend on P3 and may run as soon as S0 lands.
- Rung 2 (required, second): 100-task held-out benchmark for CB-EXEC
  (browser plus desktop tasks, new content and layout, run by an
  independent agent, arms interleaved to cut time and UI-change effects:
  screenshot-only, DOM plus real mouse, AT-SPI plus real mouse, proposed
  executor). Recorded separately per task: first-try target hit rate
  (retry does not count as pass), end-to-end task success, wrong side
  effects, recovery actions needed, P50/P90 times for model, SSH, broker,
  observe, act, and verify phases separately, model calls, full-screen
  images, crops, DOM/a11y queries, retries, postcondition accuracy, and
  false successes. Pass criteria: task success at least 96 of 100 (90%
  at 95% confidence per Wilson, CB's bar), AND zero false successes (a
  run reported verified=true with the wrong outcome counts as a fail,
  not a pass; CB-1 makes this load-bearing). "90%" is defined UP FRONT
  as task success, never as click hit rate; the two are reported
  separately and never substituted for each other. Do not merge 13/13 on
  a fixture with 90% on real tasks (CB-8).
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
does not reach yet (P3). What the 100-task benchmark does NOT prove: it
does not prove the live clone chats, which is why the live 0-vision run
stays the final gate; and it does not prove Zen chrome UI, which stays
screenshot-only per P8 (section 0.2).

## 5. What STOPS (killed, deleted, or never built)

NEVER BUILT:
- A second S3 runner alongside the A1 daemon (merged into one build,
  section 2 item (g)). Any lane building a parallel runner is stopped.
- A second executor alongside CB-EXEC (same merge; CB-EXEC is the design
  specification for the one build).
- A big-bang daemon build before the B6 prototype gate. The prototype
  proves first; the replacement follows.
- Unrestricted zen_dom eval in the default agent interface (CB-5(b)):
  removed from the default interface, kept in an explicit debug mode
  only.
- The live 2-vision run as a hard gate (diagnostic only, section 2 (a)).
- Any new AMEND4 scope beyond the 12 items (TWO TRACKS pace, section 6).

KILLED OR DELETED, each gated on its replacement proving:
- One-shot SSH as the default transport (kept as fallback and recovery
  only, A5). Fresh SSH per call dies with S0.
- scp for JSON files as transport (audit files stay, A6/D2).
- Per-batch session spawn (after the S1/CB-6 VM proof, step 8).
- Pixel-band verification as a pass signal for structured targets (after
  the P5 assert set exists per action type, A8). The band stays as a
  diagnostic.
- dom_rect_to_image_point from the live path (after P2, step 7; kept for
  tests and legacy).
- Screen-scope after-capture as produced today (replaced by the
  both-fields shape via AMEND4 item 12, A7/P4/D4).
- The 120s age refusal for DOM paths (future-clock refusal kept, D6).
- The scope-as-capability refusal (with P2, not with A7, section 1.1).
- The overlay daemon server (after session-level pill measured plus
  driver-owned pill crash proof, A4, step 10).
- The session supervisor tree (after the driver holds scope plus cancel
  latch plus lock, A3, step 10).

NEVER QUOTED OR USED AS A DECISION INPUT AGAIN:
- SPEED's 460x and 0.01s multiplexing figures (dead; corrected numbers
  are 3.5-5x, about 3.2-3.5s per connection). SPEED's 1.6x per-task
  estimate (built on 0.01s; working figure is D1's roughly 1.3-1.4x until
  a recompute on corrected numbers).
- The "SSH is 95% of 12.26s" claim (CB-7 proves no record supports it;
  suspended until the separate dispatch measurement exists).
- The "10x path" label for S2 (corrected to 3-5x on unmeasured model
  inference time until P6 measures it).
- The "mostly assembly" claim for A1 (RTD C2: a file existing is not the
  composition working; the B6 prototype is the proof).
- The 66-element / 5-of-5 sweep claim as a proven fact (CB could not
  verify it from local evidence; it is a single measurement from clone2
  batch 7 until re-run).
- Any DONE label without a named specific evidence (CB-8).
- A blanket CU_CODE_EXEC=1 flip (never; one task class at a time with
  act-now fallback, B2). A blanket P5 mandate (per action type only).
  A blanket D6 delete (scoped, future-clock refusal kept).

## 6. AMEND4 sequencing and open conditions with owners

CONTINUE, slower, per the owner 06:09 TWO TRACKS rule. Do not pause,
redirect, or stop. All four cross-responses and the draft agree, and the
owner rule answers the question directly: the team debates directions
while the fix/improve-current track keeps going, but slower and more
carefully to save tokens, because no direction is confirmed best yet.

- Why continue: items 1-8 fix the geometry and traversal the rewrite
  builds on (item 1 is the prerequisite for A9; items 5-6 fix the origin
  staleness A9 depends on; item 2 is the traversal P2 builds on); item
  12 IS the A7/P4 fix all three reviews plus CB agree is proven-needed;
  stopping wastes the in-flight runs and leaves known-broken behavior
  (after-image scope, V-F6) in the live loop the clones use today; the
  rewrite is not adjudicated final yet, so there is no adopted direction
  to redirect into.
- Landed state at HEAD 2864be4: items 1-8 done (cc964b2, c1ea773,
  62b740e, 72120aa, b44a5ea, 49081aa, af0fa87). Remaining: 9, 10, 11, 12.
- Agreed triage order, updated for the landed state: first item 12
  (after-image scope plus CB-2 stop-guard, in flight on two lanes;
  confirm the Codex-lane delivery per V-F10 and verify the regression
  test); then items 9, 10; item 11 (doc fix) any time. The split-3/4
  settlement in section 2 item (c) is moot in fact because items 3 and
  4 landed during the adjudication.
- Kill rule at reconciliation: items the rewrite deletes get killed.
  The round-3 council records per item whether the fix is a patch on a
  defective design or a real redesign, and defers or kills any item the
  adopted rewrite replaces wholesale, rather than finishing it. An item
  the rewrite subsumes is verified against the new code, not assumed
  gone. (D3's reconciliation discipline, accepted by X1/X2/XRT and the
  draft.)
- B2/B5 findings go into the round-3 review: the Y1b 3 real fails (B2)
  and the P2 collision plus stale-ref protocol (B5) are fed into the
  AMEND4 round-3 council, which judges patch vs rewrite per item under
  the 06:07 criterion. (RTD's feed-in, accepted by X1/X2/X3 and the
  draft.)
- Pace per TWO TRACKS: fewer parallel workers, smaller batches,
  per-item verification, no new scope. The two tracks run in sequence
  per item on shared files, not in parallel on the same functions.

Open conditions and owners:
- S0 soak test: owner COORD-CLICK-3 (the coordinator owns the soak
  because it spans workers; X2). The S0 implementer names the per-socket
  watchdog. The soak runs in parallel, advisory, not a gate; a master
  death falls back to fresh SSH.
- P3 quiet window plus rollback: owner COORD-CLICK-3. The window is a
  real quiet window between clone batches, never mid-batch. The rollback
  (relaunch without the flag, Brave session restore, re-login cost)
  is stated BEFORE the window, not after.
- Numerical plateau (A1/S3/CB-EXEC): owner COORD-CLICK-3. Form: Step 2
  live median wall time above a stated threshold for a stated number of
  runs after the flag flip, decision owner the coordinator. Deadline:
  defined before the S2 flip. The numbers are set from the fixture bench
  plus first live runs baseline; this position does not invent them.
- Stale-ref disagreement protocol: writer is the P2 implementer, to be
  named by COORD-CLICK-3 when P2 is staffed. Due before P2 starts; it
  is B5 lift condition (a). Content: refuse, re-plan, or click stale,
  per case, plus the lifecycle across a multi-action plan.
- Y1b fixes (1e, 2a, 2b): owner COORD-CLICK-3 to commission; the fix
  lane is to be named in the follow-up round. No input names an owner
  for this work, so I record it as open rather than inventing one. Due
  before the S2 flip; it is B2 lift condition, part 1.
- P6 specification: timestamp points are named in this position
  (observation delivered to the agent vs located target returned);
  logging owner is the harness, not cu.py. The P6 implementer lands it
  bundled with S0. CB-7 fixes (first-pointer timestamp, target_breached,
  separate dispatch measurement) land in the same bundle.
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
- Item 12 Codex-lane delivery: the driver log queue-check at 06:19 +07
  found 0 hits for the queued item-12 follow-up messages in the exec
  log. The finalizer confirms whether item 12 landed on either lane and
  whether the regression test passes; if neither lane delivered it, it
  is re-commissioned, not assumed done (CB-8).

## 7. Where my verdicts depend on probe evidence not yet in

The feasibility probes run in parallel; their results are NOT in yet
except where section 0.2 records them. For each pending probe, what
would change my verdicts:

- PROBE-S0 (SSH soak, 1-day master survival): S0 stays ADOPT whatever
  the soak shows, because the fallback is the current behavior and the
  win is already measured (3.5-5x, 11 samples rc=0). What changes: if
  the master dies repeatedly or hangs instead of failing clean, the
  per-socket watchdog design changes and the soak stops being advisory
  (calling S0 done then requires a stated master-lifetime number); if
  the master survives the day clean, the soak closes and S0 is done. It
  does not flip any other row, but its residual-cost finding (D1 R2)
  bounds S1 and A1: if the residual is per-session sshd setup the Broker
  cannot avoid either, the S1/A1 speed case weakens and the accuracy
  case must carry them alone.
- PROBE-P3 (Brave relaunch): P3 is the highest-leverage pending fact. If
  it passes (login intact, /json/list shows the Muse tab, one fill plus
  assert on a scratch input), P3, P1, S2, and A10 proceed as written. If
  Brave refuses the port on its default profile AND the Chromium
  migration proves too disruptive (re-login fails or clone
  reconfiguration breaks sessions), P3 flips from ADOPT-as-experiment to
  REJECT-as-live-path, A10's live gate re-plans to Zen Marionette only
  (the final gate venue changes, the 90% DOM-scored bar does not), P1's
  Chromium branch drops to fallback-only, and the S2 one-class flip
  narrows to Zen tasks. That outcome is reported plainly, not worked
  around silently. If the Chromium migration passes with login intact,
  P3 stays ADOPT and the live path moves to agent-managed Chromium; the
  migration cost is recorded, not hidden.
- PROBE-DOMZEN (DOM-first on real Zen): affects P1, P2, S2, A10, and
  CB-5. If DOM harvest on real Zen Messenger pages returns rects that
  disagree with rendered positions, or the harvest fails on real pages,
  P2 and S2 stay MODIFY with a narrower task class, A10's live gate
  cannot be DOM-scored until the disagreement is fixed, and CB-5's
  locate confirmations gain a failing case to fix first. If it passes
  (rects exact, clicks land, DOM verify reads back), it strengthens the
  P1/P2 ADOPTs, de-risks the S2 one-class flip, and is the first
  independent re-measurement of the clone2 batch 7 numbers (C1).
- PROBE-S1 (broker batch): affects S1/D3/CB-6. If one live batch over
  the broker from the VM fails, S1 stays MODIFY and the per-batch spawn
  is NOT deleted; the failure mode is named and the broker path is
  re-proved, not worked around by deleting the spawn anyway. If the
  single-owner socket semantics force serialization with a timeout under
  concurrent VM workers, that becomes a recorded condition on S1, not a
  surprise. If it passes, S1's deletion half lifts to ADOPT and the
  session-level pill lands in the same step as written.
- PROBE-S2 (fixture bench plus one-class flag flip): affects S2/D5, A10
  rung 1, and CB-4. If the fixture bench fails, S2 stays MODIFY and the
  flip waits; the failing case is named. If the bench passes but the Y1b
  fails are still open, B2 still stands and there is no flip (the bench
  does not cover 1e/2a/2b). If both go green, the S2 one-class flip
  proceeds as written. If the one-class flip measures model inference
  dominating at 30-60s end to end, the 10s target is restated, not the
  flip reversed: the flip is judged on measured task success and model
  calls, and the plateau definition (section 6) is what decides the
  A1/S3/CB-EXEC build, not the 10s wish.
- PROBE-P8: LANDED (section 0.2). No longer pending. If a future
  owner-approved Zen restart re-probe passes, A2's Zen-chrome constraint
  lifts and P8's boundary note is removed; until then no verdict
  changes, and no re-probe runs without restart approval.

## 8. Blocking findings, final status

- B1 (A10 straight to 0-vision live on ws2 clone chats): LIFTED. I
  confirm the draft and XRT against X1/X2/X3 (section 2 item (a)).
  What B1 attacked was A10 as a straight jump: fixture proof skipped,
  human outcome check removed, P3 untested, live clone workspaces
  disrupted. None of the three councils proposes that version; all three
  stage fixture first, condition on P3, require owner approval per run,
  and keep VISION 2 as a human look (P9). The remaining RTD-only step
  (live 2-vision intermediate) adds nothing measurable, and the V11 limb
  is conceded as non-load-bearing for benchmark scoring. B1's remaining
  note (live 2-vision as a diagnostic) is recorded in section 4, not as
  a gate.
- B2 (S2/D5 blanket CU_CODE_EXEC=1 flip): STANDS. No council mentions
  the Y1b BLOCK; the fixture-bench gate does not cover the 3 known real
  fails. PROBE-S2 confirms at 06:37 +07 the fails are STILL OPEN (V-F1).
  Lift condition: fix the 3 Y1b real fails (1e, 2a, 2b), fixture
  benchmark green, then flip the flag for ONE live task class (clone
  chat sends) with act-now as fallback, measure, then expand.
- B3 (A4 overlay daemon deletion without a replacement): STANDS as a
  gate, confirmed by all three councils. Lift condition: a session-level
  pill (acquire once per task, server kept) is measured, and a
  driver-owned pill proves no stale or missing pill on crash.
- B4 (A3/A5 delete-first ordering): STANDS as a gate, confirmed by all
  three councils. Lift condition: the driver proves scope plus cancel
  latch plus lock, and the broker proves on the VM path with one-shot
  SSH kept as recovery.
- B5 (P2 immediate interface rewrite): STANDS, narrowed. The landing
  limb is now SATISFIED (items 2-4 landed: c1ea773, 62b740e, 72120aa),
  and item 4's commit message records BrowserAdapter does not exist, so
  the collision surface was narrower than B5 stated (CLI act path,
  CodeExecBackend.act, first_action fallback). The stale-ref protocol
  limb is unanswered by all three councils and still open. Lift
  condition (settled, section 2 item (e)): the stale-ref disagreement
  protocol is specified AND (AMEND4 items 2-4 have landed OR items 3-4
  are deprioritized per the D1/D3 triage with item 2 landed). At HEAD
  2864be4 the second limb is SATISFIED, so the protocol is now the
  single outstanding gate.
- B6 (A1 full replacement claim): STANDS as a gate, complied with by
  all three councils' sequencing. CB-EXEC now supplies the design
  specification the prototype must implement, which narrows but does not
  lift the gate: a specification is not a running composition. Lift
  condition: a daemon prototype implementing the CB-EXEC contract runs
  snapshot/execute/verify end to end on one live ws2 clone chat.

## 9. Evidence index

- ARCH log: improvements/worker-arch-review-log.md (074c1d7).
- GROUNDING log: improvements/worker-grounding-review-log.md (d1fc4e9).
- SPEED log: improvements/worker-speed-review-log.md (a4ecb49).
- CODEX-BREAKTHROUGH report: improvements/codex-breakthrough-report.md
  (2596287, 138 lines, Vietnamese).
- D1: improvements/worker-click3-d1-review-log.md (37f457e).
- D2: improvements/worker-click3-d2-review-log.md (6d1bf04).
- D3: improvements/worker-click3-d3-review-log.md (14fc139).
- RTD: improvements/worker-click3-rtd-review-log.md (e96b2ff).
- X1: improvements/worker-click3-x1-response-log.md (0cf601c).
- X2: improvements/worker-click3-x2-response-log.md (d5b205d).
- X3: improvements/worker-click3-x3-response-log.md (2b0c73c).
- XRT: improvements/worker-click3-xrt-response-log.md (6cb3f95).
- Draft adjudication: improvements/worker-click3-adjudication-log.md
  (9d23834, 24 rows covering 30 proposals, ADOPT 15, MODIFY 14, REJECT
  0, PENDING 1 track).
- My spot checks this session (section 0.1, V-F1 to V-F10), 06:40-06:42
  +07, HEAD 2864be4 at writing.
- Probe results landed during this round: PROBE-P8 commit 3790901
  (chrome context BLOCKED, HTTP 500, MOZ_REMOTE_ALLOW_SYSTEM_ACCESS
  required); PROBE-P3 commit 7b1006a (NOT-RUN, clone1 batch 9 open);
  PROBE-S2 untracked log (bench runtime installed 06:41 +07, fixture
  run started 06:42 +07, Y1b 3 fails STILL OPEN at 06:37 +07).
- AMEND4 landed state at HEAD 2864be4: item 1 cc964b2, item 2 c1ea773,
  item 3 62b740e, item 4 72120aa, items 5-6 b44a5ea, item 7 49081aa,
  item 8 af0fa87; remaining 9, 10, 11, 12.
- Bench on todolist-push: tests/two_vision_bench.py c5311ce (868 lines,
  blob 80b00469), tests/two_vision_fixture.html 7f3a70b (48 lines).
- Y1b BLOCK: commit 9d9bd63 (14/20, 3 real fails 1e/2a/2b).
- Code refs verified by the reviewers and accepted here, plus my own
  V-F2/V-F3/V-F5/V-F6: scripts/cu.py (observe 920, observe_screen 974,
  image_point 1000-1005, _input_line_changed 1023-1076, desktop_act
  1619-2199, scope refusal 1648/1649, after-capture 2083-2091,
  OBSERVATION_MAX_AGE 120 at line 58, refusal 773, --dom-selector 2717,
  code-exec subparser 2733, CU_CODE_EXEC gate 2770/2793), scripts/
  first_action.py (attempt_session 183, envelope after-capture 661 at
  HEAD 2864be4, substitute observe_screen 353), scripts/fastpath.py
  (152, 195-243), scripts/dom_act.py (ground_many_one_shot 240-331,
  focus_type 425-491, arm_typed_flag call 433-434), scripts/zen_dom.py
  (harvest 905, arm_typed_flag with MutationObserver, eval subparser
  1153, evaluate 441), scripts/cdp.mjs (616 lines, Brave
  debugging-port comment 227-243), scripts/cursor_session.py (supervise
  228), scripts/overlay.py (613 lines), scripts/session_remote.py
  (1601 lines, Broker 463), scripts/session_driver.py (180 lines),
  scripts/code_exec.py (880 lines, gate 134, 1..32 action cap).
- Numbers used: fresh SSH 4.43-5.29s, mux 0.91-1.46s, saving about
  3.2-3.5s per connection, about 3.5-5x (460x dead); per act-now about
  16s to about 5-6s; per-task about 1.3-1.4x working figure (SPEED's 1.6x
  not to be quoted); vision 17/29 first-try 58.6%, Wilson 95%
  40.7%-74.5% (CB), pointer error 0.5-0.9px; DOM 66 rects median 0.030s,
  5 clicks all landed, verify 0.002-0.015s (single-source, clone2 batch
  7, C1 applies; CB could not verify the 66/5 claim from local
  evidence); F2b order-to-overlay 12.262s (dispatch 11.620s, 95%,
  unproven as SSH by CB-7); overlay acquire 315-349ms; tc02-t1 gap
  722.955s (87.8%) measured with a local helper, no SSH hop in it;
  CB act-now JSONL 199 lines (p50 order-to-overlay 337.5 ms, max
  368.4 ms; p50 total wrapper 2.288 s, max 6.95 s; 195 session, 4
  fallback, 0 timeout; 167 ok=true, 32 ok=false; 5 source=captured);
  J37 patch diff 6.627 vs threshold 6 (CB-cited); 90% per-click math
  20 clicks 12.2%, 32 clicks 3.4% (arithmetic illustration only, CB's
  own caveat); 100-task benchmark bar about 96/100 for 90% at 95%
  confidence per Wilson (CB).
