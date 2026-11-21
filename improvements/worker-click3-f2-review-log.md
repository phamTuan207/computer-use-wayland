# Worker CLICK3-F2: final council reviewer 2 position for the FINAL DECISION round

Owner: Pham Tuan. Role: independent final council reviewer 2. I did not
coordinate with any other final participant in this round, I question
everything, including the adjudication draft. Decision criterion (owner
standing rule 06:07): the final result must be the MOST ACCURATE and the
FASTEST; cost is IRRELEVANT (tokens, time, rewrite effort). A bigger
rewrite that wins on accuracy and speed beats a smaller patch that does
not. Evidence standard (owner 06:34, Lauren Tan standard): every claim
carries real measured numbers (test command, output, commit hash, time
log). A proposal with no measured evidence behind it does not count as
feasible. Rules honored: no em dash (U+2014) or en dash (U+2013) anywhere
in this file. No personal info. Evidence with every claim. Wall-clock
Asia/Ho_Chi_Minh plus elapsed time. Commit with an explicit pathspec
immediately after staging, never plain git commit, never git add -A.
Verify every push with git ls-remote. Never ydotool. This is a review,
not my own work, so no self-healing question arises.

## 0. Log and what I verified myself

- 06:37 +07 (T+0s): task received. Repo ~/workspace/computer-use-wayland,
  branch todolist-push, local HEAD 7b1006a at start. Fetched first.
- 06:37-06:40 (T+0-3m): read all 12 inputs in full: ARCH-REVIEW
  (improvements/worker-arch-review-log.md, 074c1d7), GROUNDING-REVIEW
  (improvements/worker-grounding-review-log.md, d1fc4e9), SPEED-REVIEW
  (improvements/worker-speed-review-log.md, a4ecb49), CODEX-BREAKTHROUGH
  (improvements/codex-breakthrough-report.md, 2596287, 138 lines),
  adjudication DRAFT (improvements/worker-click3-adjudication-log.md,
  9d23834), D1 (37f457e), D2 (6d1bf04), D3 (14fc139), RTD (e96b2ff), X1
  (0cf601c), X2 (d5b205d), X3 (2b0c73c), XRT (6cb3f95).
- 06:40-06:44 (T+3-7m): spot checks of my own (section 0.1). The branch
  moved during this work: PROBE-P8 log landed as 3790901, HEAD now
  2864be4. Probe results that landed during this review are incorporated
  in section 0.2, not ignored.
- 06:44 +07 (T+7m): wrote this log.

### 0.1 Spot checks run by me in this session (new verification, not trust)

- V-F1. CODEX-BREAKTHROUGH HAS LANDED. The draft (9d23834) marked it
  PENDING on a 17-line launch stub. The report is now in the tree:
  improvements/codex-breakthrough-report.md, commit 2596287, 138 lines,
  Vietnamese, with 11 proposals (CB-1 to CB-10 plus CB-EXEC). I judge
  all 11 in section 1.4. The draft's PENDING row is therefore closed
  by this review, not by the finalizer.
- V-F2. Y1b BLOCK is real and current. Commit 9d9bd63 exists: "Y1b
  verdict council 3: OVERALL Phase A BLOCK on 84b88bb (14/20, 3 real
  fails, 2 probe artifacts)". PROBE-S2's code check (section 0.2)
  confirms the 3 fails are still open at code level.
- V-F3. Broker wiring gap is real. `grep -c 'session_remote\|Broker'
  scripts/first_action.py scripts/cu.py` returns 0 and 0 in this
  session. S1 is a build, not a switch. Verified again, independently.
- V-F4. Bench is now ON this branch. tests/two_vision_bench.py exists
  in the working tree (brought in by PROBE-S2, commit c5311ce, 868
  lines, blob 80b00469) plus tests/two_vision_fixture.html (7f3a70b,
  48 lines). The draft's V-A3 (bench absent from todolist-push) is
  overtaken: the files are here, unedited. What is still missing is
  the RUNTIME (PROBE-S2: no .venv, no selenium, no Firefox or
  geckodriver at the hardcoded paths) and any run at all.
- V-F5. CB-4 math verified by me, computed live: 0.9 to the power 20
  is 0.1216 (12.2 percent), 0.9 to the power 32 is 0.0343 (3.4
  percent). Codex's figures are exact under the stated assumption
  (independent errors, 90 percent per click). The assumption is
  illustrative (real errors correlate), the arithmetic is correct.
- V-F6. CB-EXEC benchmark bar verified by me, computed live: Wilson
  95 percent lower bound for 96 passes out of 100 is 0.9016. Codex's
  "about 96 of 100 for 95 percent confidence" of at least 90 percent
  task success is correct.
- V-F7. Y1b fail 1e still open at code level, checked by me: grep for
  chr in scripts/code_exec.py returns one hit, line 100, which is
  DOM_WINDOW_CLASS, not a builtin. "chr" is in neither SAFE_BUILTINS
  list (codemode.py line 37, code_exec.py line 107, per PROBE-S2).
  This corroborates PROBE-S2's code check independently.
- V-F8. CB-9 premise partly moved. Codex's checkout 4500a18 did NOT
  contain scripts/first_action.py: `git ls-tree 4500a18 --
  scripts/first_action.py` returns nothing, so Codex's claim was
  correct for its checkout. At current HEAD 2864be4 the file IS
  tracked (`git ls-files` lists it; commit 72120aa threads ranges
  through the first_action fallback). The installed-vs-repo drift
  (installed cu.py carries two extra act-now branches vs repo
  scripts/cu.py) is still unverified from this VM and is exactly what
  the CB-9 manifest would settle. The manifest stays ADOPT; one of
  its premises has moved, the need has not.
- V-F9. AMEND4 landed state at HEAD 2864be4: items 1-4 landed
  (cc964b2, c1ea773, 62b740e, 72120aa, per draft V-A2), items 5-6
  landed (b44a5ea), item 7 landed (49081aa), item 8 landed (af0fa87).
  Items 1-8 are done. Items 9, 10, 12 remain; item 12 is in flight
  on two lanes (Codex amend4-codex, VM CLICK3-AMEND4).
- V-F10. The S0 numbers are settled and I take no new probe: fresh SSH
  4.43 to 5.29s (7 samples across SPEED, D1, D2, D3, RTD), multiplexed
  0.91 to 1.46s (11 samples, rc=0, master verified alive). SPEED's
  0.01s and 460x are dead; D1's failed-fast diagnosis (0.01s with
  rc=255, master not up) is the accepted explanation. Corrected saving
  about 3.2 to 3.5s per connection, about 3.5 to 5x.

### 0.2 Probe results that landed during this review (evidence, not trust)

- PROBE-P8 (3790901): ANSWERED. Marionette chrome context is BLOCKED
  without a Zen restart: HTTP 500, error "unsupported operation",
  message "System access is required. Start Zen with the
  MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 environment variable set to enable
  it." Session acquire 0.01s, content sanity eval 0.00s (title
  Welcome, url zen-browser.app/welcome, mozInnerScreenX 240,
  mozInnerScreenY 8, matching C12 exactly, third confirmation of that
  geometry), context switch refused in 0.00s. MOZ_REMOTE_ALLOW_SYSTEM_ACCESS
  absent from /proc/496121/environ. C12 reproduced live (03:27:26
  +07 run 2, same 500, same message). Consequence: P8 closes as a
  probe; screenshots stay ONLY for Zen chrome UI; the only path
  forward is a Zen restart with the env var, an owner decision, not a
  probe. No further time on this path.
- PROBE-P3 (7b1006a): NOT-RUN. Clone1 batch 9 open since 06:01 +07
  (assigned commit 422f4b0, 2 tasks, zero completion signal at
  06:36-06:40, zero clone1-authored commits since assignment). Brave
  running, PID 7356, untouched. P3 feasibility UNDECIDED: no measured
  evidence for or against. Re-run only when batch 9 is complete with a
  final report commit, no new clone1 batch assigned, Brave confirmed
  idle.
- PROBE-S2 (untracked log, commits c5311ce, 7f3a70b): PARTIAL. Bench
  plus fixture brought onto todolist-push unedited. Runtime missing on
  this VM (no .venv, no selenium, no Firefox or geckodriver at the
  hardcoded paths). Y1b 3 real fails STILL OPEN (1e chr NameError;
  2a codemode wall preemption, elapsed 7.20s, error raised only after
  the C loop finished, probe needs at most 4.0s; 2b code_exec wall
  preemption, elapsed 6.20s, ok=True with NO error, silent success).
  No bench run yet. S2 gate (a) fixture green and gate (b) Y1b fixes
  are both NOT met.
- PROBE-S0, PROBE-S1, PROBE-DOMZEN: no logs in the tree yet. Still
  pending; section 6 states per proposal what their results would
  change.

### 0.3 Facts all inputs now agree on (the settled base)

- Vision is the proven error source (E2 17/29 first-try, 58.6 percent;
  G30 64px and 75px misses; G31 45px eyeball error), never a
  coordinate failure (pointer error 0.5-0.9px, 29/29 clicks executed).
  DOM grounding is single-source (clone2 batch 7: 66 rects, Marionette
  median 0.030s; C1 applies: three reviews citing one measurement is
  one measurement, not three).
- The after-image scope trap is proven from source (first_action.py:656
  hardcodes cu.observe_screen, overwriting desktop_act's scope-matching
  after-capture at cu.py:2083-2091). All four reviewers, both
  cross-response rounds, and the draft agree.
- SPEED 460x is dead; S0 stays ADOPT on corrected numbers. Y1b BLOCK
  is real; S2 needs the fixture bench run plus the 3 Y1b real fails
  fixed before any live flag flip. The 2-vision bench has never run,
  even in fixture mode. The Broker exists but nothing in
  first_action.py or cu.py references it; S1 is a build, not a switch.
- The P2/AMEND4 collision is closed by landing (items 2-4 landed);
  the stale-ref protocol is the single outstanding P2 gate.
- AMEND4 CONTINUES, slower, per the owner 06:09 TWO TRACKS rule. All
  inputs agree; no reviewer proposes pause, redirect, or stop.
- False success is the worst failure mode in the record: G30 (3
  act-now batches ok/completed, message never sent) and Y1b 2b
  (ok=True with NO error past the wall budget) are the same class.
  Codex CB-1 names it precisely; no earlier review named it as a
  contract problem.

## 1. Per-proposal verdict table (every row covered, none skipped)

Legend: ADOPT means do it as proposed. MODIFY means do it with the
stated change; the gating conditions attached to each MODIFY are what
must be proven before it proceeds. REJECT means do not do it (no
proposal is rejected in full; rejected parts inside rows are named).
Exact duplicates are merged into one row citing every source.
Coverage: 34 rows covering 41 proposals: ARCH A1-A10 (10 rows),
GROUNDING P1-P9 (8 rows, P4 merged into A7), SPEED S0-S3 plus six
deletions (5 rows, D1 merged into S0, D2 into A6, D3 into S1, D4 into
A7, D5 into S2), CODEX-BREAKTHROUGH CB-1 to CB-10 plus CB-EXEC
(11 rows).

Tally: ADOPT 19 (A2, A6, A7, A9, A10, P1, P3, P6, P8, P9, S0, CB-1,
CB-2, CB-3, CB-4, CB-7, CB-8, CB-9, CB-10), MODIFY 15 (A1, A3, A4, A5,
A8, P2, P5, P7, S1, S2, S3, D6, CB-5, CB-6, CB-EXEC), REJECT 0 in full,
PENDING 0. The draft's PENDING row is closed by V-F1.

### 1.1 ARCH (worker-arch-review-log.md, 074c1d7)

| ID | Proposal | Verdict | Evidence, reasoning, and gating conditions |
|----|----------|---------|---------------------------------------------|
| A1 | Layer 0 persistent driver daemon (snapshot/execute/verify, structured-first) | MODIFY | Direction right: structured state is exact and cheap, and a state-holding driver is the only shape that stops paying setup per action. But the full-replacement claim has no existence proof (RTD C2, accepted by X1/X2/X3 and by me): session_driver.py runs cu.main() per command, code_exec.py is an in-process program model not a daemon, dom_act.py still grounds through image points, cdp.mjs drives agent-managed Chromium only, the bench is unrun. "Exists" means a file exists, not that the composition works. Gating condition: a staged prototype must prove snapshot/execute/verify end to end on one live ws2 clone chat before anything is deleted (B6 lift). The prototype design must cover the single-runner lock as a task lock, pill visibility, the one-session-per-browser constraint (RTD C5: holding the single Firefox session blocks every other tool for the task duration), daemon crash and stale-state behavior, session-holding scope, and lifecycle across laptop sleep and reboot. No deletions until then. Design basis for the prototype is CB-EXEC (section 1.4): the semantic contract is the sharpest spec of the daemon's execution core. I keep MODIFY, not XRT's ADOPT-staged: same substance, but the full-replacement claim as stated is not adopted as stated. |
| A2 | Layer 1 pixels demoted to fallback-only, pixel-band labeled weak | ADOPT, with sequencing constraint | Proven by vision 58.6 percent first-try (E2) and by the code itself admitting the band is necessary, not sufficient (cu.py:1023-1076). Constraint, from RTD and accepted by all inputs: demote only after the router (P1) and its fallback trigger are proven; Zen chrome UI stays pixel-primary until a structured path exists, because today pixels are its only perception (AT-SPI cannot see Zen, C12 probe; PROBE-P8 3790901 now proves chrome context is BLOCKED without a restart). Fallback stays for canvas, games, video, Zen chrome UI. |
| A3 | Delete session supervisor tree | MODIFY | Direction right, timing conditional. The tree's real jobs are a named killable scope, cancel/stop, the session pill label, and the single-runner lock. Gating condition: delete only when the driver demonstrably holds scope plus cancel latch plus lock on a live run (B4 lift). Until then the supervisor is the lock holder, and deleting it risks two live runners and loses the cancel/stop path. The F1 failure cluster is partly environment faults, not supervisor-design faults; deleting the tree does not delete those modes. All inputs agree. |
| A4 | Delete overlay daemon server (keep pill visibility) | MODIFY | The server is real (overlay.py 613 lines, Unix-socket server with holder accounting) and per-batch overlay acquire (315-349ms) is a genuine tax, so the end state (delete the server) is right. But the pill is the owner's only visibility into live runs and both replacements are unbuilt. Gating conditions, in sequence: (a) session-level pill first, acquire once per task, server KEPT, measured (this removes the per-batch tax without touching visibility); (b) driver-owned pill (or compositor-plugin indicator) only with proof it shows and clears, including no stale or missing pill when the driver dies mid-task; (c) delete the server only then (B3 lift). RTD originally REJECTED as stated; XRT softens to MODIFY conditional. The REJECT targeted ARCH's stated form (delete with unbuilt replacements); no input defends that form, so MODIFY is the converged label. |
| A5 | Delete one-shot SSH loop (persistent Broker only) | MODIFY | Persistent-first is right (fresh SSH 4.43-5.29s per connect, corrected S0 numbers). The word "only" is REJECTED: the VM reaches the relay only through SSH, so this is not deletion of SSH but deletion of one-shot SSH in favor of multiplexed SSH plus broker RPC; and if the broker dies, one-shot SSH is how the relay gets restarted. Gating condition: fresh SSH stays as the documented fallback AND the recovery path. "Only" applies to the default path, never to the recovery path (B4 lift). |
| A6 + D2 | Delete file-based observation/action IPC (A6) / delete scp for JSON files (D2) | ADOPT for transport | JSON over the persistent channel (or in-process calls) replaces scp per step; each scp costs a fresh about 5s SSH. Scope condition, recorded by all inputs: files stay as the audit and evidence trail (persisted observation artifacts, JSON plus JPEG, written by the driver); what dies is files as the transport, not files as the record. The JPEG still travels for the human VISION 2 check until the persistent channel carries bytes. Keep file IPC only as the fallback transport when no Broker is reachable. |
| A7 + P4 + D4 | Act-now after-image scope fix (A7) / after-image scope fix, both fields (P4) / delete screen-scope after-capture as produced today (D4) | ADOPT the both-fields shape; the delete-entirely half is REJECTED | Proven defective by construction (first_action.py:656). The adopted shape, triple-sourced plus AMEND4 item 12: return BOTH after (scope-matching, chainable) and after_screen (full monitor, verification only, documented non-chainable); move the scope check before the overlay attempt; add a regression test. Execution is DEFERRED to AMEND4 item 12, already in flight on two lanes; the rewrite track consumes it and does not duplicate it. REJECTED part: deleting the envelope after image entirely (ARCH's delete half, and D2's withdrawn alternative). It loses the human-visible evidence and the frame-change signal for a saving of about 0.25s, which is noise; that trade fails the 06:07 criterion on accuracy. Timing note, from D3 and accepted by X1/X2/X3/XRT: the scope-as-capability refusal deletion (cu.py:1648/1649, screen observations refuse key/type) is sequenced WITH P2, not with this fix. While actions are still pixel-addressed, the refusal protects typing against a screen observation; once actions are element-ref addressed, scope is irrelevant and the refusal can go. |
| A8 | Delete pixel-band verification for structured targets | MODIFY, sequenced behind P5 | Direction right: the band is admitted necessary-not-sufficient and the DOM value check is sufficient and 100-1000x cheaper (0.002-0.015s). Gating condition: delete band-as-pass-signal only where the per-action DOM assert exists and is mandatory; until then the band stays as a diagnostic. Deleting before the assert set exists leaves actions with NO verification, which is worse than weak verification. This is RTD's sequencing, accepted by X2/X3 and by X1 in substance. The P5/A8 change rests on the verified opt-in-hooks ground (focus_check and type_check are still optional hooks, D1 V13), not on RTD's V11 TODO wording; the draft's V-A5 verified arm_typed_flag exists in zen_dom.py and is called from dom_act.py:433-434, and X3 verified the MutationObserver at zen_dom.py:983. The remaining open question is narrow: whether the production code-exec path reaches that call for every type action. That confirmation belongs to the P5 implementer; it is not load-bearing for the P5/A8 verdicts or for benchmark scoring. |
| A9 | Coordinate model to one system (CSS px element rects, converted once at the driver edge) | ADOPT for structured targets | The five-frame tower has five proven bug sites (F2b-1, C12, amend3 step 5, G28, after-scope trap); the one-conversion path already exists (fastpath.dom_rect_to_screen_point, verified). Dependency, accepted by all inputs: A9 depends on AMEND4 items 5-6 landing (SATISFIED: b44a5ea) and item 1 (SATISFIED: cc964b2), and the one conversion still needs a correct absolute viewport origin and scale factors re-read per ground (C12 proved window-relative vs absolute origin is a live trap). The pixel fallback keeps its own frame internally; the router decides. |
| A10 | Acceptance test becomes 0-vision live benchmark on real ws2 clone chats | ADOPT as staged | Final gate: live 0-vision on real ws2 clone chats (clone1 Brave plus clone2 Chrome), DOM harvest, plan, execute, DOM verify, zero screenshots in the machine loop, accuracy at least 90 percent scored by DOM outcome (V12 sent-bubble gate), total wall time end to end including transport, one final screenshot kept as unscored human evidence (P9), owner approval per run. Staging: fixture 2-vision first (it has never run), P3 first (the live run needs the CDP path). My addition to the draft (section 3): the P9 screenshot must actually be reviewed before the run scores as passed, and any DOM-vs-render mismatch in it FAILS the run; otherwise the human check is decorative. The live-2-vision intermediate rung GOES as a hard gate and is kept only as a diagnostic; see section 3 for the full reasoning. B1 is LIFTED (draft section 5, XRT section 3); I adopt the lift. |

### 1.2 GROUNDING P1-P9 (worker-grounding-review-log.md, d1fc4e9)

| ID | Proposal | Verdict | Evidence, reasoning, and gating conditions |
|----|----------|---------|---------------------------------------------|
| P1 | DOM/a11y default router (Zen Marionette/BiDi, Chromium CDP, AT-SPI, screenshot last; encoded in code, not convention) | ADOPT | Two perception stacks with no routing rule drift to the worse one (works everywhere) instead of the better one (needs setup). Implementation requirements, accepted by all inputs: encode the router in code as one function returning the perception source; fail closed to the labeled screenshot fallback; a per-target routing table proven per target before the default flips; a log line on every routing decision, so drift back to screenshots is visible instead of silent. Note: the a11y branch is thin for the apps in play (AT-SPI cannot see Zen; AT-SPI numbers unverified on this VM), so it mostly covers native apps that are not the live workload. Interim honest state: Brave tasks still route to screenshots until P3 lands. |
| P2 | Element-ref action interface rewrite (live rect re-read at execution, screen-point action form, delete dom_rect_to_image_point from the live path) | MODIFY | Direction right and highest-leverage code change after P3: the round trip exact DOM rect to exact screen point to lossy image point and back is proven wasteful from source (fastpath.py:195-243, dom_act.py:312, cu.py:1000-1005), and it deletes the F2b-1, C12, amend3-step-5 bug class. Gating conditions (B5): (a) the stale-ref disagreement protocol is specified first (what happens when a live rect re-read disagrees with the plan: refuse, re-plan, or click stale, per case; lifecycle across a multi-action plan); AND (b) AMEND4 items 2-4 have landed (SATISFIED at HEAD 2864be4: item 2 c1ea773, item 3 62b740e, item 4 72120aa). P2 starts only when (a) is met; the landing limb is already satisfied, so the protocol is now the single outstanding gate. My addition: the protocol writer also specifies CB-2 (scope mandatory in action data; scope change stops the batch), since scope-disagreement and rect-disagreement are the same protocol family. Running P2 in parallel with AMEND4 items 2-4 would have guaranteed merge collisions on the same functions; that risk is closed by the landing, not by the protocol. Delete dom_rect_to_image_point from the live path (keep for tests and legacy). The scope-as-capability refusal deletion lands in this step (see A7 row). |
| P3 | Brave relaunch with debugging port (controlled experiment, quiet window, never mid-batch; fallback agent-managed Chromium) | ADOPT as a controlled experiment | Single highest-leverage unblocker: the clone chats live in Brave, Brave holds no debugging port on its default profile (cdp.mjs comment verified verbatim), so the CDP path cannot reach them today. Status: NOT-RUN (PROBE-P3 7b1006a; clone1 batch 9 open since 06:01, Brave untouched). Conditions, accepted by all inputs: quiet window owned by the coordinator, never mid-batch; verify /json/list shows the Muse tab and login intact; run observe plus harvest plus one fill plus assert on a scratch input. Recorded additions: CDP on port 9223 exposes the logged-in browser to any local process (security consideration, never mentioned by GROUNDING); the Chromium fallback is a migration with re-login and clone reconfiguration, not a fallback, and needs its own login-persistence check before it is relied on; cdp.mjs notes shadow-DOM elements have null box_model, and Messenger's DOM shape against that gap is unexamined. BLOCK on any live-task migration until the experiment passes. If P3 fails (Brave refuses the port and the Chromium migration is too disruptive), the DOM-first live path loses its highest-leverage unlock and the whole program re-plans around Zen Marionette only; report that plainly, not worked around silently. |
| P5 | DOM verification mandatory (focus_check and type_check required, not optional hooks; CDP fill read-back and assert polling the model) | MODIFY | Direction right; the code admits the band is insufficient. The blanket mandate is BLOCKED as stated: the assert set does not exist for every action type (focus_check/type_check are still optional hooks, D1 V13), and no per-action exception list exists. Gating conditions: DOM verification becomes mandatory PER ACTION TYPE as its assert lands; an explicit per-action exception list names the actions where DOM assert is impossible (scroll position, hover state) and pixel stays the only signal; the band stays as a diagnostic until then. A blanket mandate now means false refusals on working flows or vacuous asserts (false confidence). The V12 sent-bubble gate in the benchmark is the pattern. This MODIFY is converged across all inputs (X1/X2/X3 MODIFY; XRT MODIFY with BLOCK on the blanket version). My addition: the CB-1 result contract (input_sent vs verified) lands in this step for the flipped task class, because Y1b fail 2b (silent success past the wall budget) is the CB-1 false-success class on the code-exec path; fixing 2b and adopting CB-1 are the same work there. |
| P6 | Measure the vision call | ADOPT, with specification fix | Cheapest item on the list and a precondition for honest speed claims: capture is 15-30ms and DOM rects 0.030s, but the model read that locates the target is seconds and timed nowhere. Bundle with S0 and CB-7. Specification fix, from RTD and accepted by all inputs: the model call happens in the calling agent's loop, outside cu.py, so the proposal must specify the timestamp points (observation delivered to the agent vs located target returned) and the owner of the logging (the harness, not cu.py), or it will be recorded as done when only capture timing is logged again. Until that number is in the logs, every speed claim about the screenshot path is incomplete, and nobody may claim the 10s target is met. |
| P7 | Session handover protocol (one protocol per browser per task phase, BiDi ground then Marionette input or stay on one) | MODIFY | The one-session constraint is proven (4 runs, Firefox allows exactly one remote session per instance), so a protocol is needed IF a task genuinely needs two protocols. Gating condition: first answer whether Marionette-only suffices (the benchmark already runs Marionette-only, harvest plus input, and zen_dom harvest IS Marionette). Write the handover protocol only if a task genuinely needs BiDi for grounding plus Marionette for input. Price noted: a handover costs 4-7s per switch (BiDi new 1.51-2.77s fresh, Marionette attach 2.65-4.12s), comparable to the SSH tax being deleted. Small and non-blocking either way. All inputs converge on MODIFY. |
| P8 | Zen chrome Marionette context test (set_context chrome) | ADOPT, CLOSED as BLOCKED by probe | Premise verified (no chrome-context support in zen_cli.py today). PROBE-P8 (3790901) has now answered it: BLOCKED, HTTP 500, MOZ_REMOTE_ALLOW_SYSTEM_ACCESS required, C12 reproduced live (section 0.2). Consequence: keep screenshots ONLY for Zen chrome UI and record that boundary explicitly. AT-SPI cannot see Zen, so that path is closed; do not spend more time on it. The only path forward is a Zen restart with the env var set, which kills owner tabs and the session: an owner decision, not a probe. No further probe unless the owner approves that restart experiment. |
| P9 | Keep one screenshot for the human (VISION 2 stays, machine scores by DOM) | ADOPT | Correct division: screenshots are a human evidence channel, not a machine perception channel. VISION 2 stays as unscored human evidence; the machine scores by DOM outcome. Wording correction, from RTD and accepted by all inputs: VISION 2 is the agent looking at the threads and reporting to the human, not the owner looking directly, so it is the agent's final sanity check reported to the human. Cost is about 0.25s plus one vision read, noise against the total. Attached to A10. My addition (section 3): the P9 screenshot is load-bearing, not decorative: it must be reviewed before the run scores as passed. |

### 1.3 SPEED S0-S3 plus six deletions (worker-speed-review-log.md, a4ecb49)

| ID | Proposal | Verdict | Evidence, reasoning, and gating conditions |
|----|----------|---------|---------------------------------------------|
| S0 + D1 | Step 0 persistent SSH multiplexing, do now (S0) / delete fresh SSH per call (D1) | ADOPT on CORRECTED numbers | Fresh SSH 4.43-5.29s (7 samples, confirmed five ways); multiplexed 0.91-1.46s (11 samples, rc=0, master verified alive). Saving about 3.2-3.5s per connection, about 3.5-5x, NOT 460x and NOT 0.01s. SPEED's 0.01s figure matches a failed-fast connection (master not up, rc=255, D1's diagnosis, accepted by RTD and D3). Corrected expectation: per act-now (3 connects) about 16s becomes about 5-6s, not about 2s; per observe (2 connects) about 6-8s saved. SPEED's 1.6x per-task estimate was built on 0.01s and must NOT be quoted; D1's revised roughly 1.3-1.4x on a CL2-MSG-class task is the working figure until a recompute on the corrected numbers. Conditions: implement the fallback explicitly (any multiplex failure falls back to a fresh connect, slow but correct); log master death; per-socket watchdog, not global (a half-dead master can hang rather than fail cleanly; ControlPersist=600 can leave a stale master holding a dead Tailscale route); the 1-day soak test runs IN PARALLEL, advisory, not a gate. The residual about 1.1-1.2s per call (per-session sshd and shell setup, which multiplexing does not remove) is itself an argument for S1 and A1. Do it now: no agent-logic code change, fallback safe. |
| S1 + D3 | Step 1 act-now over the persistent relay broker (S1) / delete per-batch session spawn (D3) | MODIFY, proof-first | Direction right: the per-batch session spawn is a real tax (0.4-2.1s) plus a real failure mode (20s deadline, timeout never falls back, council 1 B1), and JSON over the same channel kills the scp round trips. But S1 is a BUILD, not a switch: the relay is alive (PID 1821, socket exists, verified) yet zero references to session_remote or Broker exist in first_action.py or cu.py (grep 0 hits, verified by me again this session, V-F3), so the broker path from the VM is unproven end to end, and the single-owner socket semantics under concurrent VM workers are unexamined (serialize or refuse). Gating conditions: prove one live batch end to end over the broker from the VM first, then delete the per-batch spawn; keep the spawn as fallback until proven. Session-level pill (keep the overlay server) lands in the same step. Expected per-batch mechanism about 0.5s plus the overlay item after S1. All inputs converge on MODIFY. |
| S2 + D5 | Step 2 DOM-first plus code-exec plus checkpoint verification, CU_CODE_EXEC=1 on (S2) / delete per-action model call as the default (D5) | MODIFY, gated | The 10x path, already built and merged (code_exec.py 880 lines, Pick 1 winner, commits 714e4f9, 84b88bb, 2e2aeff, merge 453adc4), and the flag is OFF in the live path (verified live: CU_CODE_EXEC unset on the laptop). But the blanket flip is BLOCKED (B2): Y1b council 3 BLOCKED Phase A on 84b88bb with 14/20 probes passing and 3 real fails (1e f-string chr NameError; 2a codemode wall preemption, error raised only after the C loop finished; 2b code_exec wall preemption, elapsed 6.20s, ok=True with NO error, silent success), and the named gate (2-vision benchmark) has never run. A fixture bench pass alone does not fix the 3 real fails. Gating conditions, in order: (a) run the fixture 2-vision bench green; (b) fix the 3 Y1b real fails; (c) flip the flag for ONE live task class (clone chat sends) with act-now as fallback, measure, then expand. Status from PROBE-S2: (a) not run (bench files now on branch, runtime missing), (b) NOT met (no preemption mechanism in codemode.py or code_exec.py; chr in neither SAFE_BUILTINS list; V-F7 corroborates). The "10x path" label is corrected to 3-5x on unmeasured model inference time (SPEED's own honest limit: 30-60s if vision reading dominates); the mechanism can be about 1s, the model is the remaining unknown, and P6 must measure it before anyone claims the 10s target. Code-exec becomes the default for the proven task class first; the stepwise loop stays the fallback for unknown shapes only. |
| S3 | Step 3 laptop-side task runner, only if Step 2 plateaus | MODIFY, fold into A1; plateau defined numerically first | S3 substantially overlaps A1: a laptop-side runner that grounds, acts, and verifies locally and streams back compact state IS the A1 driver daemon approached from the other side. One design decision, not two builds; do not build a separate runner alongside A1. CB-EXEC is the third approach to the same destination (section 1.4); all three fold into one merged build. Gating condition: the plateau criterion must be defined NUMERICALLY BEFORE the S2 flip starts (threshold, run count, decision owner), so the trigger is not argued later. An undefined plateau either never triggers or triggers on one bad run. The decision itself happens only after steps 0-8 of section 2 are measured. The numbers themselves are set from the fixture bench plus first live runs baseline, not invented here. |
| D6 | Delete 120s freshness window as a gate on DOM work | MODIFY, scoped | For DOM-grounded work, re-read the DOM (0.030s) instead of refusing for staleness; the window is a patch for vision coordinates, not a law. Correction, from RTD and accepted by all inputs: the refusal at cu.py:773 also guards against future-clock observations, and a blanket delete removes the clock-skew guard. Gating condition: keep the future-clock refusal, drop only the age refusal for DOM paths. Keep the window for pixel-addressed work, where staleness is real and the refusal protects against acting on a dead frame. |

### 1.4 CODEX-BREAKTHROUGH (codex-breakthrough-report.md, 2596287, 138 lines)

Codex worked independently: read the todolist, the full error file, cu.py, browser and accessibility adapters, broker and session driver, and installed act-now code on the laptop; ran no browser, no clicks; its only new measurement is an aggregation of the existing act-now JSONL (199 lines). Its proposals therefore rest on code reading plus the same evidence base as the other three reviews (C1 applies: a fourth reading of the same base is still the same base), EXCEPT where it cites laptop-installed code and logs the other reviews did not read. I judge each proposal on its own evidence, not on Codex's authority.

| ID | Proposal | Verdict | Evidence, reasoning, and gating conditions |
|----|----------|---------|---------------------------------------------|
| CB-1 | Three-part result contract (input_sent / verified=true only with postcondition) | ADOPT, top priority contract change | The most important accuracy fix in this round. Evidence: G30 (3 act-now batches ok/completed, message never sent; clicks 64-75px above the real field); Codex 2.1 (cu.py:1541-1549: the desktop check only knows pointer position, not which UI element received the event; cu.py:1806-1809: pixel hash change does not confirm success; a11y.py:204-219: do_action true is treated as click complete with no post-state check; installed first_action.py:422-439 turns cu.py ok into envelope ok=true). So a click into empty space can report success today. The fix: every result separates input sent, correct target received the input, and post-state confirmed; verified=true only when a postcondition holds. This kills the false-success class, which is worse than slow success: a slow failure is retried, a false success is believed. Gating: none on the contract itself; it lands with P5 in section 2 step 5. Note: fixing Y1b fail 2b (ok=True, NO error, past the wall budget) IS adopting CB-1 on the code-exec path; one fix, not two. |
| CB-2 | Scope mandatory in action data, scope change stops the batch | ADOPT | Evidence: J40 (points taken from a window observation used on a full-screen image, missed the button by about +45,+12 px, command still returned ok); J35 (window observation 1863x1176 vs after full screen 1920x1200); first_action.py:289-315 (_fresh_observation substitutes a full-screen capture without converting coordinates and still hands the whole action list to the executor). Scope is a mandatory part of action data (window or tab, DOM or image frame, observation ID). An observation with a different scope stops the batch; it must never silently reframe and continue. This strengthens A7/P4: the both-fields fix addresses the after-image; CB-2 addresses the input side. Specified together with the P2 stale-ref protocol (section 1.2, P2 row): same protocol family. |
| CB-3 | Vision error taxonomy plus image uniformity plus J37 codec false refusal | ADOPT | Evidence: E2 Wilson 95 percent interval for 17/29 is 40.7-74.5 percent (Codex computed; n=29 is small and not a held-out set, so the rate itself is weak evidence, the failure MODE is the strong evidence); image inputs are not uniform (observe caps at 960px width, cu.py:2303; act-now captures at max_width 1920, first_action.py:313; JPEG q90, cu.py:807-863), so the model sees different resolution and detail by path; J37 (error file lines 832-837): preflight patch around the pointer differs by 6.627 against threshold 6 (cu.py:979-1000), a measured codec false refusal, unstable by construction. Fix: one capture width, lossless crop (PNG) for vision fallback, separate the codec comparison from real screen change, and record a vision error taxonomy (wrong target vs wrong frame vs codec refusal) so P6 numbers are interpretable. Cheap; lands with P6/CB-7. |
| CB-4 | Batch growth by proven validity (90 percent per-click math: 20 clicks 12.2 percent, 32 clicks 3.4 percent) | ADOPT | Math verified by me (V-F5): 0.9 to the power 20 is 12.2 percent, 0.9 to the power 32 is 3.4 percent, exact under the stated assumption. The point stands even though real errors correlate (Codex says so itself): 90 percent per-click does not mean 90 percent task success, and a batch that grows by capacity bets the whole task on one stale image. Replacement rule: the batch grows only when the executor proves the next steps still valid (preconditions re-checked, postconditions met). This KILLS the "max actions per vision" goal as a target and reframes S2/D5: code-exec programs grow steps by proven validity, not by capacity. No code gate beyond the CB-EXEC prototype; the rule is enforced by the executor contract (CB-1) and the stale-ref protocol (P2). |
| CB-5 | Common executor routing plus Zen adapter plus locate confirms visible/interactive/uncovered/stable/unique plus remove unrestricted zen_dom eval from default interface plus AT-SPI coverage reporting | MODIFY | The parts: routing web targets to DOM, desktop controls to AT-SPI, canvas and image content to screenshot-crop, under one contract, is P1's router with teeth; ADOPT the routing as part of P1. The Zen adapter with locate confirms (visible, interactive, uncovered, stable, unique, plus iframe offsets, transforms, moving elements, non-unique targets) is the precondition set CB-EXEC needs; ADOPT the confirms as requirements on the prototype. Remove unrestricted zen_dom eval from the default agent interface (zen_dom.py:151-155, 221-245: arbitrary JS in the current tab as a normal primitive); ADOPT as a standalone change, keep eval only in an intentional debug mode. AT-SPI coverage reporting (a11y.py:83-104: at most 500 nodes or 2s, at most 80 items, truncated flag; query locked after the fastpath flag at lines 118-139); ADOPT: report coverage, then fall back to DOM or image when the tree is insufficient. MODIFY overall because the "common executor" as a separate build is REJECTED: it folds into the A1/S3/CB-EXEC merged build (one design decision, not three builds). Caveat from Codex itself, which I adopt as a prototype constraint: BiDi pointer click FAILED, Marionette has viewport limits, DOM click is not equivalent to a real mouse (zen-dom-control-comparison.md:67-120). The Zen adapter must use real mouse and keyboard input when the control needs hover or trusted events; DOM click is not a universal substitute. The Browse hover case proves real input is sometimes required. |
| CB-6 | act-now uses the long-lived session driver, one owner, sequential queue | ADOPT direction, MODIFY sequencing | Evidence: session_remote.py Broker (lines 460-520) and session_driver.py (lines 59-75) exist; act-now builds a cu.py session per invocation (first_action.py:172-178, 403-405) instead of using them; zen_dom also opens and closes a session per command. The shape is right: one owner of the pointer, overlay, and Firefox session, with a sequential queue; no competing BiDi and Marionette clients, since the record shows two protocols share one Zen slot. Sequencing is the S1 gate (proof-first): prove one live batch end to end over the broker from the VM, then delete the per-batch spawn (S1 row). The one-owner requirement also answers RTD C5 (session-holding scope): the owner holds the single Firefox session for the task duration, and the prototype design must state that scope. |
| CB-7 | Latency measurement fixes plus measure VM-to-laptop dispatch separately | ADOPT | Evidence: first_action.py records order_to_overlay_ms from wrapper start, not from the user command on the VM (lines 339-400); no timestamp for the first pointer action; target_breached compares the whole batch duration against the 30s threshold (lines 495-498), so it does not measure first-action latency; the file header (lines 40-48) admits model decision time and pre-call observation time are excluded. Codex's JSONL aggregation (199 lines, p50 order-to-overlay 337.5ms, max 368.4ms; p50 total wrapper 2.288s, max 6.95s; 195 session, 4 fallback, 0 timeout; 167 ok=true, 32 ok=false; 5 source=captured) measures executor time and state, not click hit rate or task success. Codex could NOT verify the F2b 11.6s of 12.26s SSH share from laptop logs (logs start after the command arrives); a separate record (service 11.611s, gap 1208.942s) neither proves nor refutes it. SPEED's fresh-SSH numbers (4.43-5.29s) plus mux (0.91-1.46s) partially answer the transport share but do not measure dispatch for a real act-now workload. Fix: measure VM-to-laptop dispatch separately with the same workload, fresh SSH vs connection reuse; fix the latency metrics to measure first-action latency, not batch totals. Lands with S0/P6 in step 0. Until then, no dispatch-share claim (95 percent or otherwise) is quoted as fact. |
| CB-8 | Evidence discipline (DONE is a state of specific evidence) | ADOPT | Process-level, no code change. Evidence: the todolist marks many items DONE for a direction decided or a fixture passed, but those do not prove the real-app case (Codex 2.8: fixture form 0.64s and 15 steps is a Polygon-process simulation, not a Polygon upload; no same-task baseline; 13/13 verified actions cannot become a 90 percent commitment for another app; held-out new app and independent agent are PARTIAL, todolist line 38; J10 real think-time still OPEN, error file line 717). Rule: DONE means a named piece of evidence exists (command, output, commit hash, time log), not that a direction was decided. This is the Lauren Tan standard applied to the todolist itself. I apply it to this review: every verdict above cites its evidence or states plainly where evidence is missing. |
| CB-9 | Deployment manifest (lock source commit plus installed artifact plus log) | ADOPT | Evidence: Codex's checkout was branch todolist-push HEAD 4500a18 with the remote-tracking ref 622 commits behind; scripts/first_action.py was not in ITS tree (verified by me, V-F8: git ls-tree 4500a18 returns nothing for it); the installed cu.py has two extra act-now branches vs repo scripts/cu.py. A running behavior that depends on a wrapper absent from the source checkout cannot be reviewed, tested, or deployed reproducibly. Fix: before any benchmark is used as a release bar, lock source commit, installed artifact, and log of the same build into one manifest. Cheap, do early (step 0). Note the premise has moved (the file is tracked at HEAD 2864be4); the installed-vs-repo drift is still unverified from this VM and is exactly what the manifest settles. |
| CB-10 | Overlay flicker vs think-time separate, per-phase measurements | ADOPT, low priority, non-gating | Evidence: the todolist records overlay idle at 0 repaint and 0 events, but the LIQUID background test never ran because the plugin was not loaded (todolist:42-45), so there is no evidence the initial flicker was reproduced or fixed; think-time is unmeasured by act-now and J10 marks H2 OPEN. Two different questions, two different measurements. Do not attribute either to SSH or screenshots without per-phase numbers. Low priority: it gates no build, only claims about flicker and think-time. Lands with P6/CB-7 measurement work. |
| CB-EXEC | The semantic transaction executor itself (semantic targets, preconditions, real mouse/keyboard, postconditions, retry only when surely unsent; one local broker; DOM/BiDi plus AT-SPI plus screenshot-crop backends under one contract; vision as fallback; 100 held-out tasks benchmark, 90 percent defined as task success, about 96/100 for 95 percent confidence) | MODIFY | This is the sharpest specification of the A1/S3 destination in this round, and it folds into A1/S3 as ONE merged build, not a separate executor. What it adds over A1: the semantic contract (targets by role and name or snapshot ref; scope; preconditions: unique, visible, enabled, right window, geometry and focus unchanged; real mouse and keyboard or a confirmed-fitting DOM action; postconditions: dialog closed, URL changed, field holds the value, checked state changed, new text appeared; retry ONLY when the executor knows surely the input was not sent, checking state before replaying an action that can send or delete data). A form may run many steps in one call, but Submit or any side-effect click gets its own precondition and postcondition. Model decides targets and hard branches; the executor does stable steps (find, fill, wait for ready, re-read the field, check the result). MODIFY because: (a) the prototype gate (B6) still applies: snapshot/execute/verify end to end on one live ws2 clone chat before anything is deleted; (b) the 100-task benchmark is the general acceptance expansion (section 3), built alongside, run after live 0-vision; (c) Codex's effort estimates (2-3 day prototype on a fixture plus low-risk web tasks, 1-2 weeks to unify the broker plus desktop AT-SPI plus Firefox limits, a few days for the benchmark) are ESTIMATES, not measurements; I record them as estimates and commit to nothing on them. Risks Codex names and I adopt as prototype constraints: one Zen remote-session slot, a hung session blocks every client; some controls need real mouse events; iframe, shadow DOM, canvas, native file picker, and Wayland extents may lack data; DOM fill may not equal real typing; UI can change between read and click. Mitigations: one session owner, no retry of uncertain input, re-read the target close to click time, vision and native input as fallback. The benchmark bar is verified by me (V-F6): Wilson 95 percent lower bound for 96/100 is 0.9016, so about 96 passes is the right bar for 90 percent task success at 95 percent confidence. |

## 2. Order of work (numbered sequence with explicit gates)

Every step is independently verifiable, every step lands a measured win
before the next step starts, and no step depends on a bet (P3, P8, S2
measurement) that has not yet paid off. Cost is irrelevant by the
criterion, but sequencing by dependency is not cost, it is correctness:
a daemon built from unproven parts inherits their failure modes. This
order adopts the draft's 12 steps in substance and inserts the CB work
where it belongs.

0. S0 plus P6 plus CB-7 plus CB-9, now. Persistent SSH multiplexing
   with explicit fallback, master-death logging, per-socket watchdog;
   P6 vision-call measurement with the timestamp points and harness
   owner specified; CB-7 latency metric fixes plus a separate
   VM-to-laptop dispatch measurement with the same workload (fresh SSH
   vs connection reuse); CB-9 deployment manifest locking source
   commit plus installed artifact plus log. Gate to step 1: fallback
   explicit and watchdog in place. The 1-day soak test starts the same
   day and runs IN PARALLEL, advisory, not a gate (a master death falls
   back to fresh SSH, slow but correct). The numerical plateau
   definition (S3/A1) is due before step 6, set from the fixture bench
   plus first live runs baseline by the coordinator; I invent no numbers.
1. AMEND4 continues in parallel, slower, per the owner 06:09 TWO TRACKS
   rule (section 5). Item 12 (A7/P4) lands via the in-flight run; verify
   the regression test. Gate: the rewrite track makes no parallel edits
   to the same functions AMEND4 is working on (the two tracks run in
   sequence per item on shared files, not in parallel on the same
   functions, or the merge will collide).
2. P3 Brave relaunch experiment, in a real quiet window between clone
   batches, coordinator-owned, never mid-batch. Re-run conditions per
   PROBE-P3: batch 9 complete with a final report commit, no new clone1
   batch assigned, no clone1 commits in flight, Brave confirmed idle.
   Gate to any live DOM work: P3 passes (login intact, /json/list shows
   the Muse tab, one fill plus assert on a scratch input) or the Chromium
   fallback is proven with its own login-persistence check. No live-task
   migration until then. If P3 fails, re-plan around Zen Marionette only
   and report it plainly. P8 is CLOSED (BLOCKED, 3790901); the only
   remaining chrome-UI path is a Zen restart with
   MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1, an owner decision, not a probe.
3. Fixture 2-vision bench run. The bench is now on todolist-push
   (c5311ce, 7f3a70b); the runtime (selenium plus Firefox plus
   geckodriver at the hardcoded paths) is environment setup, not a
   bench edit. This step does not depend on P3 (headless Firefox, local
   fixture) and may run in parallel with step 2. Gate to step 6: the
   fixture run passes. The program's gate cannot be an unrun script.
4. Fix the 3 Y1b real fails on code-exec (1e, 2a, 2b). Gate to step 6:
   the fails are fixed (B2 lift, part 1). Fixing 2b IS adopting the
   CB-1 contract on the code-exec path; one fix, not two.
5. P1 router plus P5 asserts per action type, plus CB-1 contract, CB-2
   scope in action data, CB-3 taxonomy. Rewiring of existing hooks;
   P5 per action type as its assert lands, plus the explicit exception
   list. This step precedes the S2 flip because S2's checkpoint
   verification IS P5: flipping S2 without P5 means flipping code-exec
   while DOM verification is still optional hooks (D1 V13), a window
   in which the live loop runs code-exec with pixel-band verification
   only. Gate to step 6: the router logs its routing decisions, and the
   P5 assert set covers the S2 task class (clone chat sends).
6. Define the numerical plateau (coordinator, before the flip), then the
   S2 flip for ONE live task class (clone chat sends) with act-now as
   fallback. Measure model-call count and wall time. Gate to expansion:
   measured on one class; expand only on measurement.
7. P2 element-ref interface rewrite, after B5 lifts (stale-ref protocol
   specified, including CB-2 scope; items 2-4 landed limb satisfied at
   HEAD 2864be4). A9 one-system coordinates land in this step (depends
   on AMEND4 items 5-6, satisfied: b44a5ea). The scope-as-capability
   refusal deletion lands in this step, not with A7. CB-5 locate
   confirms (visible, interactive, uncovered, stable, unique) land in
   this step, and unrestricted zen_dom eval leaves the default agent
   interface here (kept for intentional debug mode only). Gate to step
   8: P2 proven on the S2 task class with DOM verification mandatory.
8. S1 broker path proof from the VM on one live batch, then delete the
   per-batch spawn. Session-level pill (server kept) in the same step.
   P7's Marionette-only question is answered before any handover protocol
   is written. Gate to step 9: one live batch proven end to end over the
   broker from the VM.
9. A1/S3/CB-EXEC merged prototype: the semantic transaction executor on
   the persistent driver (snapshot/execute/verify plus CB-1 contract
   plus CB-2 scope plus one owner CB-6). The prototype must prove
   snapshot/execute/verify end to end on one live ws2 clone chat (B6
   lift). Backends under one contract (DOM/BiDi plus AT-SPI plus
   screenshot-crop; vision as fallback). Gate to step 10: prototype
   proven.
10. A3/A4/A5 deletions last, each gated on its replacement proving (A3:
    driver holds scope plus cancel latch plus lock; A4: session-level
    pill measured, then driver-owned pill crash proof, then delete the
    server; A5: broker proven on the VM path with one-shot SSH kept as
    recovery).
11. Acceptance: fixture 2-vision (step 3), then live 0-vision on real ws2
    clone chats as the final gate (section 3), after P3 and P2. Live
    2-vision is a diagnostic only if the live 0-vision run fails. Then
    the 100-task held-out benchmark (section 3) as the general gate for
    the CB-EXEC build.

## 3. Acceptance test decision

Decision: the acceptance test is a LADDER with two required rungs, one
diagnostic option, and one general gate. The final live gate is the
live 0-vision benchmark on real ws2 clone chats. The general gate is
the 100-task held-out benchmark (CB-EXEC).

- Rung 1 (required, first): fixture 2-vision benchmark. Headless Firefox,
  local fixture. It has never run at all (BUILD ONLY); the whole
  program's gate cannot be an unrun script. The bench is now on
  todolist-push (c5311ce, 7f3a70b); the runtime setup is environment
  work, not a bench edit. Pass criteria: the script's own gates (V12
  sent-bubble gate after each message, scoring by OUTCOME in the thread
  DOM, never point-in-box). This rung does not depend on P3 and may run
  as soon as S0 lands.
- Final gate (required, last for live): live 0-vision benchmark on the
  REAL ws2 clone chats (clone1 Brave plus clone2 Chrome). DOM harvest,
  plan, execute, DOM verify, zero screenshots in the machine loop. Pass
  criteria: accuracy at least 90 percent, scored by DOM outcome (V12
  sent-bubble gate, message in the thread DOM, never point-in-box);
  total wall time measured end to end including transport. One final
  screenshot is kept as unscored human evidence (P9). Conditions on the
  live run: P3 closed first (otherwise it falls back to screenshots and
  proves nothing); quiet window with clone coordination; owner approval
  per run (the bench's --live plus --confirm-live gates plus plan-URL
  gate); agreed test messages so the clones' working threads are not
  polluted.
- P9 load-bearing condition (my addition to the draft): the final
  screenshot must actually be reviewed before the run scores as passed,
  and any DOM-vs-render mismatch in it (bubble in the DOM but not
  rendered, wrong thread, hidden render) FAILS the run. Without this,
  the human check is decorative and RTD's B1 limb (2) stands
  unanswered. With it, the live 2-vision rung adds nothing the P9
  review does not already supply, which is why B1 stays lifted.
- Diagnostic option (not a rung): live 2-vision. If the live 0-vision run
  fails, the team may run live 2-vision to localize (script vs DOM path).
  It is not required before the final gate, for the reasons in section
  3.1: the machine behavior is identical in both forms, and the P9
  screenshot supplies the human outcome check. If live 2-vision passes
  and live 0-vision fails on the same tasks, that indicates flakiness in
  the 0-vision change, not a systematic gap, and the failure must be
  investigated, not papered over.
- General gate (required for the CB-EXEC build, after live 0-vision):
  100-task held-out benchmark (CB-EXEC). Browser plus desktop apps,
  new content and layouts, independent agent, interleaved order across
  four arms (screenshot-only, DOM plus real mouse, AT-SPI plus real
  mouse, proposed executor). Pass criteria: at least 96 of 100 task
  successes (Wilson 95 percent lower bound 0.9016, verified by me,
  V-F6, for at least 90 percent task success at 95 percent confidence);
  90 percent is defined as TASK success, not per-click hit rate.
  Recorded per task: first-try target-hit rate, end-to-end success,
  wrong side effects, recovery actions, P50/P90 per-phase times
  (model, SSH, broker, observe, act, verify), model calls, full
  screenshots, crops, DOM/a11y queries, retries, postcondition
  accuracy, and false successes. False successes count as FAILURES in
  the 96/100 (a task that falsely reports success is a wrong result,
  not a pass). The benchmark itself needs building (a few days per
  Codex's estimate, uncommitted); it must not gate the live 0-vision
  run, which is the live proof the fixture cannot give.

### 3.1 Why the live 2-vision rung goes (B1 lift, adopted with the P9 condition)

X1/X2/X3 keep the ladder (fixture 2-vision, live 2-vision, then
0-vision); XRT lifts B1 and the draft adopts the lift. I side with
XRT and the draft, on the evidence, not on vote count (C1: agreement
is not independent confirmation). In the bench design VISION 1 is a DOM
harvest, not a screenshot, and VISION 2 is a human look at the threads;
the machine never locates from pixels in either form. Live 2-vision
and live 0-vision-with-P9-screenshot are the same machine behavior;
they differ only in whether the human looks at live threads or at a
screenshot, and the P9 screenshot IS the human outcome check in the
0-vision run. The councils' stated purpose for the rung ("the live
2-vision run is the proof that DOM works on real Messenger pages") is
served equally by the live 0-vision run itself, which also runs DOM on
real Messenger pages and scores by DOM outcome. The extra run buys
replication and localization, not a distinct proof, and under the 06:07
criterion a gate must protect accuracy or speed measurably. The V11
limb of B1 is conceded as non-load-bearing for benchmark scoring: the
bench scores by the V12 sent-bubble gate, not through the production
V11 flag. The disruption limb is addressed by all inputs (quiet window,
agreed test messages, owner approval per run). The rung is retained as
a diagnostic. The one place I strengthen the draft: the P9 review is
made load-bearing (section 3), so the human check that replaces the
rung is a real check, not a formality.

## 4. What STOPS (killed, deleted, or never built)

Killed now, by evidence in this round:
- SPEED's 460x and 0.01s multiplexing figures, and the 1.6x per-task
  estimate built on them. Never quoted again. Working figure is D1's
  roughly 1.3-1.4x on a CL2-MSG-class task, pending a recompute on the
  corrected numbers.
- The "10x path" label for S2. On unmeasured model inference time it is
  3-5x (SPEED's own honest limit: 30-60s if vision reading dominates).
  The 10s target is unclaimed until P6 measures inference time.
- The "mostly assembly" claim for A1. A file existing is not the
  composition working (RTD C2). The composition is the work, and it is
  unproven until the B6 prototype proof.
- The blanket CU_CODE_EXEC=1 flip (B2), the immediate P2 rewrite (B5),
  delete-first A3/A4/A5 (B3/B4), the straight-to-0-vision-live jump
  (B1 as originally stated), and the big-bang daemon-first build (B6).
  All five stay blocked as stated; each has a stated lift condition in
  section 7.
- The delete-entirely half of A7 (after image deleted entirely). It
  loses the human-visible evidence and the frame-change signal for
  about 0.25s.
- Generic x/y as the model's everyday action input (CB-EXEC, CB-5).
  Coordinates become an internal adapter detail; the model addresses
  semantic targets. This is a direction kill, enforced by the P2
  interface and the CB-EXEC contract, not a flag flip.
- "Max actions per vision" as a target (CB-4). Replaced by growth by
  proven validity.
- DONE claims without specific evidence (CB-8). A todolist DONE needs a
  named piece of evidence (command, output, commit hash, time log).
- Unrestricted zen_dom eval from the default agent interface (CB-5).
  Kept for intentional debug mode only.
- Further P8 probing without an owner-approved Zen restart (PROBE-P8
  3790901: BLOCKED, C12 reproduced). The probe is closed.

Never built:
- A separate S3 runner alongside A1, or a separate CB-EXEC executor
  alongside A1. One merged build (A1 plus S3 plus CB-EXEC), one design
  decision, one prototype gate.
- A BiDi plus Marionette handover protocol unless Marionette-only is
  proven insufficient (P7 MODIFY). A handover costs 4-7s per switch,
  comparable to the SSH tax being deleted.
- A compositor-plugin pill as the first A4 replacement. Session-level
  pill first (server kept); driver-owned pill only with crash proof.

## 5. AMEND4 sequencing

CONTINUE, slower, per the owner 06:09 TWO TRACKS rule. Do not pause,
redirect, or stop. All inputs agree, and the owner rule answers the
question directly: the team debates directions while the fix and
improve-current track keeps going, but slower and more carefully to
save tokens, because no direction is confirmed best yet.

- Why continue: items 1-8 have landed and fix the geometry and
  traversal the rewrite builds on (item 1 is the prerequisite for A9;
  items 5-6 fix the origin staleness A9 depends on); item 12 IS the
  A7/P4 fix all inputs agree is proven-needed; stopping wastes the
  in-flight Codex run and leaves known-broken behavior (after-image
  scope) in the live loop the clones use today; the rewrite is not
  adjudicated final yet, so there is no adopted direction to redirect
  into.
- Triage going forward: first items 9, 10; item 11 (doc fix) any time;
  item 12 lands via the in-flight run, verify the regression test.
  Items 1-8 are done (V-F9). Item 3's deprioritization and item 4's
  minimal cap are now moot in fact (both landed during adjudication);
  their landed work stands subject to the kill rule below.
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
- Pace per TWO TRACKS: fewer parallel workers, smaller batches,
  per-item verification, no new scope. The two tracks run in sequence
  per item on shared files, not in parallel on the same functions.

## 6. Where my verdicts depend on probe evidence not yet in

Each pending probe, what it would change, and what it would not change.
PROBE-P8 is already answered (section 0.2) and PROBE-S2 is partial;
the rest are still pending at writing time.

- PROBE-S0 (SSH soak, no log yet): if the master survives 24h with no
  hangs, S0 is DONE. If the master dies or hangs repeatedly (half-dead
  master hangs rather than failing cleanly), S0 stays ADOPT (the
  fallback is safe) but the per-socket watchdog design changes and S0
  "done" waits; S1 reliance on the master gets gated until the watchdog
  proves. No other verdict changes: the per-connection saving is
  already measured (V-F10) and does not depend on the soak.
- PROBE-P3 (Brave relaunch, NOT-RUN 7b1006a): if it passes (login
  intact, /json/list shows the Muse tab, one fill plus assert on a
  scratch input), the A10 live gate proceeds and the P1 Chromium branch
  goes live. If it fails (Brave refuses the port on its default profile
  AND the Chromium migration loses login or is too disruptive), P3
  ADOPT becomes FAILED-as-tested; the DOM-first live path loses its
  highest-leverage unlock and the whole program re-plans around Zen
  Marionette only; the A10 live gate moves to Zen-hosted chats or
  waits; PROBE-DOMZEN becomes the critical path. Either outcome is
  reported plainly, not worked around silently.
- PROBE-DOMZEN (DOM-first on real Zen, no log yet): if DOM harvest plus
  real input plus DOM verify works on real Zen chats at 90 percent or
  better first-try, it corroborates P2 and S2 and Zen becomes the live
  fallback if P3 fails. If it fails (Marionette viewport limits or
  BiDi click failures bite, or DOM click proves unequal to real mouse
  on the live controls), the S2 Zen leg and the CB-EXEC Zen adapter
  need redesign; P3/CDP becomes the only live DOM path; the P7
  Marionette-only question gets a negative answer in part (BiDi
  grounding may be needed after all). The A1/CB-EXEC prototype gate
  (B6) does not change; its proof chat is a ws2 clone chat either way.
- PROBE-S1 (broker batch, no log yet): if one live batch proves end to
  end over the broker from the VM, S1/D3 lift to ADOPT (delete the
  per-batch spawn). If the broker path fails (single-owner socket
  semantics under concurrent VM workers, or the SSH-tunneled client
  does not work), S1 stays MODIFY, the per-batch spawn stays as the
  live mechanism, and the A1/CB-EXEC prototype must carry its own
  transport design; CB-6's one-owner queue still applies to the
  session driver. A5's fallback condition does not change either way.
- PROBE-S2 (fixture bench plus one-class flag flip, PARTIAL): bench
  files are on the branch (c5311ce, 7f3a70b), runtime missing, Y1b 3
  fails still open, no run yet. If the fixture bench runs green AND
  the one-class flip (with Y1b fixes) measures well, S2/D5 lift toward
  ADOPT-expand. If the fixture bench fails or silent successes persist
  after the flip, S2 stays gated and the CB-1 contract becomes the
  fix, not a further debate. If P6 shows model inference dominates
  (30-60s floor), the 10s target is unreachable by any mechanism
  change; the plateau definition must reflect that, and S2's value is
  accuracy plus 3-5x, not 10x. If the bench cannot run on this VM at
  all (runtime uninstallable), the bench moves to the laptop and the
  gate moves with it; the gate itself does not drop.
- PROBE-P8 (DONE, BLOCKED 3790901): already answered. Only a future
  owner-approved restart-with-env-var experiment could change it. If
  that experiment passes, Zen chrome UI leaves pixel-primary and A2's
  constraint lifts for chrome. If it fails or is never approved, no
  verdict changes; screenshots stay ONLY for chrome UI, which is
  already the plan.

## 7. Blocking findings, final status, and disagreements with the draft

- B1 (A10 straight to 0-vision live): LIFTED. Adopted from XRT and the
  draft, with my P9 load-bearing condition added (section 3). The
  live-2-vision intermediate step is a diagnostic, not a gate.
- B2 (S2/D5 blanket CU_CODE_EXEC=1 flip): STANDS. No input mentions a
  fix for the Y1b BLOCK; PROBE-S2 confirms the 3 fails are still open
  at code level. Lift condition: fix the 3 Y1b real fails (1e, 2a, 2b),
  fixture benchmark green, then flip the flag for ONE live task class
  (clone chat sends) with act-now as fallback, measure, then expand.
  My addition: fixing 2b is adopting CB-1 on the code-exec path.
- B3 (A4 overlay daemon deletion without a replacement): STANDS as a
  gate, confirmed by all inputs. Lift condition: a session-level pill
  (acquire once per task, server kept) is measured, and a driver-owned
  pill proves no stale or missing pill on crash.
- B4 (A3/A5 delete-first ordering): STANDS as a gate, confirmed by all
  inputs. Lift condition: the driver proves scope plus cancel latch
  plus lock, and the broker proves on the VM path with one-shot SSH
  kept as recovery.
- B5 (P2 immediate interface rewrite): STANDS, narrowed. Collision limb
  closed by landing (items 2-4 landed). Stale-ref protocol limb still
  open. Lift condition: the stale-ref disagreement protocol is
  specified (now including CB-2 scope) AND items 2-4 have landed
  (satisfied). The protocol is now the single outstanding gate.
- B6 (A1 full replacement claim): STANDS as a gate, complied with by
  all inputs' sequencing. Lift condition: a daemon prototype runs
  snapshot/execute/verify end to end on one live ws2 clone chat. The
  prototype's design basis is now CB-EXEC (section 1.4), which the
  draft could not name because CB was PENDING then.

Disagreements with the draft (9d23834), stated plainly:
1. CB track: the draft marked it PENDING; the report HAS landed
   (2596287). I judge all 11 CB rows now and fold CB-EXEC into A1/S3.
   This is the largest delta from the draft, and it is new evidence,
   not a re-read.
2. P8: the draft has P8 as a bounded probe; PROBE-P8 has now answered
   it (BLOCKED, 3790901). P8 closes; the boundary is recorded.
3. A10: I agree with the draft's B1 lift, but I strengthen P9 (the
   final screenshot must be reviewed before the run scores as passed;
   any DOM-vs-render mismatch fails the run). Without this, RTD's B1
   limb (2) stands unanswered.
4. S2 gate: I agree, and I add that fixing Y1b 2b IS adopting CB-1's
   contract on the code-exec path (same work, one fix).
5. P2 gate: I agree, and I add CB-2 scope-mandatory to the stale-ref
   protocol writer's brief (same protocol family).
6. Order: I agree with the draft's 12 steps in substance; I insert
   CB-7 and CB-9 into step 0, CB-1/CB-2/CB-3 into step 5, CB-5
   locate-confirms plus eval removal into step 7, CB-EXEC as the step 9
   design basis, and the 100-task benchmark as the post-live-0-vision
   general gate.
7. A1 label: I keep the draft's MODIFY, not XRT's ADOPT-staged. Same
   substance; MODIFY is the honest label while the full-replacement
   claim is unproven.
8. S0 per-task figure: I keep D1's roughly 1.3-1.4x working figure,
   pending a recompute; 1.6x is never quoted.
9. Where the draft and I agree outright: B1 lift, B2/B3/B4/B5/B6 stand,
   S0 corrected numbers, A7 both-fields shape deferred to AMEND4 item
   12, P1/P5 before the S2 flip (X3's dependency hold), AMEND4
   continues slower with the kill rule at reconciliation, and the
   numerical plateau defined before the S2 flip with numbers set from
   measured baselines, not invented.

## 8. Evidence index

- ARCH log: improvements/worker-arch-review-log.md (074c1d7).
- GROUNDING log: improvements/worker-grounding-review-log.md (d1fc4e9).
- SPEED log: improvements/worker-speed-review-log.md (a4ecb49).
- CODEX-BREAKTHROUGH report: improvements/codex-breakthrough-report.md
  (2596287, 138 lines).
- Draft: improvements/worker-click3-adjudication-log.md (9d23834).
- D1: improvements/worker-click3-d1-review-log.md (37f457e).
- D2: improvements/worker-click3-d2-review-log.md (6d1bf04).
- D3: improvements/worker-click3-d3-review-log.md (14fc139).
- RTD: improvements/worker-click3-rtd-review-log.md (e96b2ff).
- X1: improvements/worker-click3-x1-response-log.md (0cf601c).
- X2: improvements/worker-click3-x2-response-log.md (d5b205d).
- X3: improvements/worker-click3-x3-response-log.md (2b0c73c).
- XRT: improvements/worker-click3-xrt-response-log.md (6cb3f95).
- Probes: PROBE-P8 improvements/worker-probe-p8-log.md (3790901,
  BLOCKED); PROBE-P3 improvements/worker-probe-p3-log.md (7b1006a,
  NOT-RUN); PROBE-S2 improvements/worker-probe-s2-log.md (untracked,
  bench c5311ce, fixture 7f3a70b, Y1b still open, no run yet).
- Y1b BLOCK: commit 9d9bd63 (14/20, 3 real fails 1e/2a/2b).
- Bench: tests/two_vision_bench.py on todolist-push (c5311ce, 868
  lines, BUILD ONLY, VISION 1 is a DOM harvest); fixture
  tests/two_vision_fixture.html (7f3a70b, 48 lines).
- AMEND4 landed state at HEAD 2864be4: items 1-4 (cc964b2, c1ea773,
  62b740e, 72120aa), items 5-6 (b44a5ea), item 7 (49081aa), item 8
  (af0fa87). Items 9, 10, 12 remain; item 12 in flight.
- Numbers verified by me this session: CB-4 math (0.9^20 0.1216,
  0.9^32 0.0343); Wilson lower bound 96/100 0.9016; Broker grep 0 hits
  in first_action.py and cu.py; git ls-tree 4500a18 has no
  scripts/first_action.py (CB-9 premise moved); chr absent from both
  SAFE_BUILTINS lists (Y1b 1e still open).
- Numbers used: fresh SSH 4.43-5.29s, mux 0.91-1.46s, saving about
  3.2-3.5s per connection, about 3.5-5x (460x dead); per act-now about
  16s to about 5-6s; per-task about 1.3-1.4x working figure (1.6x not
  to be quoted); vision 17/29 first-try 58.6 percent, pointer error
  0.5-0.9px; DOM 66 rects median 0.030s, 5 clicks all landed, verify
  0.002-0.015s (single-source, clone2 batch 7, C1 applies); F2b
  order-to-overlay 12.262s (dispatch 11.620s, 95 percent, disputed by
  CB-7: unverifiable from laptop logs); overlay acquire 315-349ms;
  tc02-t1 gap 722.955s (87.8 percent) measured with a local helper,
  no SSH hop in it; act-now JSONL 199 lines, p50 order-to-overlay
  337.5ms, max 368.4ms, 167 ok=true, 32 ok=false (Codex aggregation,
  not re-verified by me).

## 9. Addendum: evidence that landed after this log was written (06:44-06:52 +07, 22/11/2026)

This log was written at 06:44 +07. Between 06:44 and 06:52 the branch moved again (HEAD now 5f30908) and four position responses plus three probe logs landed. I read the four responses and the three probe logs in full and re-verified the load-bearing new facts from source myself (section 9.1). This addendum records what changes, what does not, and which statements in the body above are superseded. Nothing in the body above is silently edited; where a statement is corrected, section 9.7 names it exactly.

Read in full for this addendum: FARCH (improvements/worker-click3-farch-response-log.md, c3bf5e0, 697 lines), FSPEED (improvements/worker-click3-fspeed-response-log.md, e7562ca, 853 lines), FCODEX (improvements/worker-click3-fcodex-response-log.md, 09c6b3f, 411 lines), FGROUND (improvements/worker-click3-fground-response-log.md, 8d0e38a, 890 lines), PROBE-S0 interim (improvements/worker-probe-s0-log.md, 90eb8be, 254 lines), PROBE-S1 interim (improvements/worker-probe-s1-log.md, untracked, 9181 bytes), PROBE-S2 committed log (improvements/worker-probe-s2-log.md, f1952a5, bench pass a1a672d).

NOT read, deliberately: F1 (improvements/worker-click3-f1-review-log.md, 7124f1e), F3 (improvements/worker-click3-f3-review-log.md, 433a6e6), FRT (improvements/worker-click3-frt-review-log.md, 5f30908). F1 and F3 are the fellow final council reviewers; FRT is the final redteam review. Reading any of them would break the independence this round requires. They are left to the finalizer.

### 9.1 New spot checks run by me in this session (V-F11 to V-F16)

- V-F11. FCODEX V-F3 confirmed from source: the G28 loud refusal IS enforced in the repo copy. scripts/first_action.py:478-498: when a given observation was rejected and a screen capture was substituted, the run returns 1 with path='refused' before any session attempt and before any action runs, naming the given observation, its age, and why it was rejected, for EVERY batch including pointer-only batches. The _fresh_observation docstring (lines 328-350) states the same rule. So CB-2's limb 2 (silent substitution of a screen capture for a rejected window observation) is CLOSED in the current tree. This refutes FARCH's premise that the silent substitution is still live, and it refutes FGROUND's framing that the substitution defect is unaddressed (FGROUND cited installed first_action.py:289-315, the installed copy, not the repo copy). Limb 1 (after-image scope) is still OPEN: first_action.py:661-665 shows after_meta = cu.observe_screen(...) unconditional, screen-scoped, no scope check. So A7/P4 item 12 remains open. The remaining gap beyond both limbs is the planned-action case: actions planned on a window observation and executed after a screen observation arrived. Neither limb covers it; CB-2's scope-plus-observation-ID rule does. That is the CB-2 MODIFY substance (section 9.2).
- V-F12. FGROUND V-F5/V-F6 confirmed from source: scripts/zen_dom.py locate() lines 567-588 returns getBoundingClientRect only, no visibility check, no interactive/enabled check, no uncovered/hit check, no stability check, no uniqueness check (find() returns the first match). hit_check() lines 820-851 exists (elementFromPoint, returns True only when the rect center hits the element itself or a contained non-interactive descendant). The eval CLI primitive exists: main() line 1144, sub.add_parser("eval") line 1153, handled line 1171. So P2's re-confirm expansion and the eval-removal item are verified from source, not just CB-claimed.
- V-F13. FGROUND's correction of CB-7 confirmed from the F2b log: improvements/worker-f2b-live-session-log.md lines 34-35 read "ORDER-TO-OVERLAY = 12.262s. Breakdown: dispatch 11.620s (T_order to T_LAPTOP_START: scp script + SSH connect + shell startup), fresh observe 0.233s, Python startup 0.060s, overlay acquire 0.349s." The 11.620s dispatch IS measured (VM-side record, D1 V10 verified). CB-7's "no record supports 11.6s of 12.26s is SSH dispatch" is WRONG in the broad form. FARCH's precise form stands: 11.620s is dispatch, not proven SSH alone (it includes scp plus SSH connect plus shell startup). The "SSH is 95 percent" slogan dies; the dispatch figure does not. S0's arithmetic survives on direct fresh-SSH probes (PROBE-S0 interim, V-F15).
- V-F14. Bench pass and AMEND4 items 9/10/11 confirmed from git log: a1a672d "probe-s2: fixture 2-vision bench PASS 10.86s, Y1b 3 fails still open, flag NOT flipped (gate b unmet)"; 44c15bb (item 9), e912ad4 (item 10), 8d75135 (item 11). Item 12 is the only outstanding AMEND4 item.
- V-F15. PROBE-S0 interim (90eb8be) numbers: fresh SSH mean 4.667s (n=10, 06:36 +07); healthy mux mean 1.339s (n=18 accepted samples); saving 3.328s per connection, 3.49x. Confirms the corrected S0 numbers in my V-F10. FINDING F1 (measured, reproduced 2/2): an explicitly started ssh -M -f -N master does NOT multiplex on this path (sessions refused "Master refused session request: Permission denied", client falls back to fresh cost about 4.5s, rc=0, master dies on its own within about 1-2 minutes). Any S0 implementation starting its master with ssh -f delivers zero saving. FINDING F2: setsid/nohup master WITHOUT -f accepts mux sessions reliably. FINDING F3: residual about 1.2-1.3s is a PER-SESSION cost, not per-command and not shell startup (mux -O check only about 0.058s; 3 commands in one session cost the same as one, about 1.206s vs about 1.382s; explicit extra shell adds nothing). It sits in server-side session setup per new channel (sshd fork plus session negotiation plus Tailscale proxy round trips). This answers D1's open probe R2. Consequence: code opening a session per action still pays about 1.3s per action, strengthening S1 and A1. FINDING F4: master death costs one slow (about 4.269s) but correct fallback, then ControlMaster=auto self-heals with a fresh auto-master (new pid 13517). No manual recovery needed IF clients use ControlMaster=auto. Soak test: 60 minutes, samples every 10 min, keepalive every 5 min, IN PROGRESS at interim commit; soak master pid 13662 started 06:41:20 +07; ends about 07:41 +07. Soak verdict stays pending. Soak harness bug noted: master pid recorded empty for setsid masters (grep pattern only matches auto-created masters); timing/rc values unaffected.
- V-F16. PROBE-S1 interim (untracked log, sections 5-7 TODO, broker arm and one-shot arm NOT RUN): relay verified alive (PID 1821, service active since 2026-11-21 15:17:30 +07, socket /run/user/1000/computer-use-wayland/relay.sock, mode 0600). Socket path correction: the brief named /run/user/1000/agent-computer-use/cursor-guard.sock; that path is the CURSOR GUARD socket, not the relay. Any S1 client must use relay.sock. Broker status 06:36 +07: ok, idle, broker_generation ee8e59d3db191dd1e817ba8b658a2ee6, loaded_code_sha256 84f65d16ad3dd26b23c1ef75d8614cbb8c1e6539d0512cce65c8c8111d65d4a5, started_git_head 56f5af4e521e1c20b26b56dc31d662e34f1c2668, no retained session, no live run active. Broker-client gap re-confirmed: 0 references to session_remote/Broker in first_action.py and cu.py; the broker IS referenced in tc02_controller.py:411 and det_finish.py. S1 is a build, not a switch. Transport baselines: fresh SSH 4.459s and 4.528s; mux 0.98-1.35s. SPEED's 0.01s mux figure dead again. MASTER LIVENESS FINDING (measured twice): a ControlMaster started with ControlPersist=600 DIES after about 1-2 minutes idle on this path, socket unlinked on exit. Master 1 (pid 11815): alive 23:39Z, dead by 23:40:45Z. Master 2 (pid 13600, detached setsid nohup): served 6 mux calls through 23:42:10Z, dead by 23:43:31Z (about 80s after last use). Consequence: the persistent channel needs a per-use liveness check plus restart-on-death (fresh SSH about 4.5s) as the normal path, not an exception. A restart test is running: master 3 (pid 14865) adds -o ServerAliveInterval=15 -o ServerAliveCountMax=3; survival past 2 minutes idle to be checked before the broker arm. chromium_cli.py default endpoint is NOT 9223 in practice: status reported http://127.0.0.1:9222 (Zen BiDi, unreachable for CDP); always pass --endpoint http://127.0.0.1:9223 explicitly. Test target set up (scratch fixture on 8931, tab C299A7D9D48478C9453566876D60A13F in agent Chromium, window 0x557053b4a930 at [3448,914], size [924,1176]); setup observation 1.104s mux round trip. NOTE on PROBE-S0's concurrency worry: PROBE-S0's interim note claimed sibling PROBE-S1 was running with the broken -fN master form (pid 13600). PROBE-S1's own log states pid 13600 was detached setsid nohup and served 6 mux calls at 0.98-1.35s. A master in the broken -f state does not multiplex at all (S0 F1), so S1's timings stand and S0's worry about S1's evidence does not hold.

### 9.2 Verdict changes

Corrected tally: ADOPT 19, MODIFY 14, CLOSED 1 (P8), REJECT 0 in full, PENDING 0. The ADOPT count is coincidentally unchanged from section 1 (19), but the composition changed: P8 and CB-2 leave ADOPT, CB-5 and CB-6 enter it. The section 1 tally line is superseded by this tally.

- CB-2: ADOPT becomes MODIFY. Reason: V-F11 closes limb 2 (G28 loud refusal enforced at first_action.py:478-498); limb 1 (after-image) stays open via A7/P4 item 12; what remains of CB-2 as new work is the planned-action rule (scope plus observation ID mandatory in action data, refuse on mismatch). The rule itself is adopted as stated; the MODIFY label records that half of CB-2 as stated is already done in the repo. This matches FCODEX's tally for CB (ADOPT 9, MODIFY 2).
- CB-5: MODIFY becomes ADOPT (content). Reason: FCODEX and FGROUND both adopt CB-5's content as stated (routing, Zen adapter, locate confirms, eval removal, AT-SPI coverage). My MODIFY rested on the "common executor as a separate build" rejection; that is a build statement, and it belongs under CB-EXEC MODIFY (which I keep), not on the CB-5 content row. The fold into the A1/S3/CB-EXEC merged build is unchanged. Real-input default adopted (section 9.3): real Pointer/keyboard input is the DEFAULT at DOM-located coordinates; DOM .click() only where equivalence is proven per control type (FARCH actuation concession, FGROUND section 2 CB-5).
- CB-6: "ADOPT direction, MODIFY sequencing" becomes ADOPT. Reason: label hygiene. The sequencing gate lives in the S1 row (proof-first), exactly as CB-1's landing condition lives in the P5 row. FCODEX adopts CB-6 as stated with the same fold; FGROUND adopts CB 2.6 (single owner) into P7. Substance unchanged: one owner, sequential queue, broker proof first.
- P8: ADOPT-as-probe becomes CLOSED. Reason: PROBE-P8 answered (3790901, BLOCKED). FGROUND's formulation adopted: P8 is CLOSED, the boundary (screenshots ONLY for Zen chrome UI) is recorded in P1, and the only reopen is an owner-approved Zen restart with MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1. No further time on this path.

No other verdict changes. The B1 lift, B2/B3/B4/B5/B6 stand, AMEND4 continues slower, and the acceptance ladder are all unchanged in direction; sections 9.3-9.5 add content and correct gates inside them.

### 9.3 Row additions (content tightenings, no verdict change unless stated)

- P1: add T1a (FGROUND): the router routes on COVERAGE, not just target type. A backend that returns an empty harvest or a truncated a11y tree (a11y.py truncated flag, FGROUND V-F7) falls through to the next backend; it does not fail and does not proceed on a partial inventory. Add T1b: Zen chrome UI routes to screenshots, a DECIDED boundary (P8 CLOSED), recorded in the router. Add CX1 (FCODEX/FGROUND): the fallback branch uses a lossless PNG crop of the target region, not a full-screen JPEG.
- P2: content expanded per CB-5 (FGROUND, V-F12 verified). Live RE-CONFIRM, not just re-read: visible, interactive/enabled, uncovered (hit_check, zen_dom.py:820-851), stable (two rect reads agree), unique (querySelectorAll count is 1, or the ref disambiguates). The pieces exist (hit_check, harvest hit/focused flags); P2 composes them into locate. Add the Zen adapter under the same contract (snapshot id, refs, confirmations); code_exec.py DOM is Chromium-only (FGROUND V-F8, DOM_WINDOW_CLASS='chromium'), the Zen adapter is genuinely missing work, not just unwiring. Add caller enumeration: enumerate the live callers of dom_rect_to_image_point (desktop_act, first_action, code_exec backends, tests) BEFORE deleting it from the live path. Add the eval removal as verified (zen_dom.py:1153/1171; boundary: internal evaluate() stays, it is the transport for harvest, locate, and hit_check). Add EX2 retry policy and EX3 ref binding to the stale-ref protocol (FCODEX/FGROUND): retry only when the executor knows input was not sent; check state before replaying any action that can send or delete data; every target ref is bound to a snapshot ID and a scope; an expired observation or a changed scope refuses, never substitutes. Add FARCH's stale-ref protocol core as the B5 lift content: re-validate each ref immediately before acting; on disagreement refuse and re-plan by default; click stale only when the executor proves the same element (same ref, same snapshot id, still unique, visible, enabled, geometry delta within tolerance); never click a stale point on a destructive or message-sending action.
- P3: add the shadow-DOM check item (FGROUND): cdp.mjs notes shadow-DOM elements have null box_model; Messenger's DOM shape against that gap is unexamined. zen_dom locate() pierces open shadow roots (docstring, V-F12 read); the CDP harvest must be checked against the same composer. PARTIAL outcome defined: if the Messenger composer sits in shadow DOM and CDP returns null box_model for it, P3 narrows to "CDP works except shadow-DOM elements" and P2 carries a shadow-DOM fallback.
- P4: add the CB-2 substitution rule (FGROUND section 1 P4, FCODEX): a scope change stops the batch, never silently substitutes (J40 +45,+12 px, ok returned). Note V-F11: for the given-observation case the G28 loud refusal already enforces this halt in the repo; the remaining gap is the planned-action case, covered by CB-2 binding.
- P5: add EX1 preconditions (unique, visible, enabled, right window, geometry and focus unchanged since grounding) alongside the postcondition set. Add the three-way result contract as P5's deliverable shape (FGROUND section 1 P5): every action returns input sent, right target received it, postcondition confirmed; desktop_act's ok becomes input_sent; verified=true only on postcondition. The draft's (f) settlement stands (arm_typed_flag exists; FGROUND accepts it in full).
- P6: add P6a (FGROUND): measure model INFERENCE time separately from vision-call latency; record a first-pointer-action timestamp; measure order-to-overlay from the user command, not from the wrapper start. Add P6b: log the ERROR CLASS per miss (wrong target in the image vs orchestration fed the wrong frame or scope; G30 is class (a), J40 and the after-image trap are class (b)). Add P6c: pin and log the capture parameters with every measurement (observe default 960, act-now 1920, JPEG q90 always, FGROUND V-F9); without them the latency numbers are not comparable across paths.
- P7: add the single session owner (CB 2.6, FGROUND section 1 P7): one owner for pointer, overlay, and the Firefox session, with a serialized queue, no competing BiDi plus Marionette clients. The one-session constraint is proven in 4 runs; the owner is the missing piece, not the sequence.
- P9: pin the P9 capture parameters (fixed size and compression, FGROUND section 1 P9). The human evidence channel must not vary by path the way machine perception does today.
- CB-1: add FCODEX's gate form: CB-1 is an ADDITIONAL gate on S2 alongside B2. The verified/input_sent split lands for a task class BEFORE the S2 flip for that class, judged by postcondition pass rate, not envelope ok rate. My step 5 already lands CB-1 for the flipped class; this makes it an explicit S2 gate (section 9.4 step 6).
- CB-7: CORRECTED per V-F13. The 11.620s dispatch IS measured (F2b log lines 34-35, D1 V10); attributing it wholly to SSH is inference. The "SSH is 95 percent" slogan dies (FARCH); the dispatch figure does not. S0's arithmetic survives on direct fresh-SSH probes (V-F15). The CB-7 fix stands: measure VM-to-laptop dispatch separately with the same workload, and fix the latency metrics to measure first-action latency, not batch totals.
- CB-9: premise updated per FCODEX V-F7 and FGROUND V-F10. The file-presence limb is STALE (first_action.py is tracked on todolist-push). The divergence limb is CONFIRMED LIVE by FCODEX (read-only SSH call 06:40 +07): installed first_action.py is 23442 bytes and DIFFERS from the repo copy (33893 bytes); installed cu.py also DIFFERS; laptop HEAD 3790901. The "behind 622 commits" count was per remote-tracking ref without a fetch; the material fact is installed != repo. The manifest stays ADOPT, and it is now OVERDUE: the fixture bench pass (a1a672d) is already being quoted, so the manifest must be locked before that pass is cited as a gate.
- CB-10: tightened per FCODEX. The overlay limb is NOT handled by the draft (0 hits for LIQUID). The pill change alters overlay acquisition, so flicker status interacts with A4. The LIQUID flicker probe (load the plugin, reproduce the flicker, count repaints) or an explicit recorded deferral with an owner PRECEDES the A4 session-level pill judgment. CB-10 stays ADOPT but is no longer fully non-gating: it gates A4 step (a). The draft does not handle the LIQUID flicker probe, the 622/behind count, the manifest, or the first-pointer timestamp (FCODEX draft grep: 0 hits for "liquid", "622", "manifest", "first_pointer").
- A10: add the per-phase timing split to the live 0-vision pass criteria (FARCH A10 amendment): per-phase times (model, SSH, broker, observe, act, verify) recorded in the live run log, as in the 100-task gate. 90 percent stays defined as end-to-end TASK SUCCESS. NOTE a disagreement with FARCH: FARCH folds the 96/100 bar into the live gate itself. I keep them separate (live 0-vision gate, then the 100-task general gate). Reason: the 100-task set does not exist yet (Codex: a few days to build, uncommitted estimate); folding an unbuilt benchmark into the live gate would block the live proof on a build. FCODEX agrees the 100-task set SUPPLEMENTS the ladder, it does not replace it. The live gate's 90 percent is task success on the clone chats; the 96/100 bar is the general claim after it.

### 9.4 Order of work amendments (section 2)

- Step 0: add the P6a/P6b/P6c spec (section 9.3 P6). Add S0 hard requirements from V-F15/V-F16: (a) start the master with setsid/nohup WITHOUT -f (or let ControlMaster=auto create it), never with ssh -M -f -N; (b) ControlMaster=auto on clients so master death self-heals; (c) per-use liveness check plus restart-on-death (fresh SSH about 4.5s) as the normal path, not an exception (PROBE-S1 master liveness finding). Add the CB-9 manifest overdue note: lock it before the fixture bench pass (a1a672d) is cited as a gate.
- Step 1: triage corrected per V-F14: only AMEND4 item 12 remains (items 9, 10, 11 landed: 44c15bb, e912ad4, 8d75135). Item 12 lands via the in-flight run; the CB-2 substitution rule is its addition. NOTE a stale line in FSPEED: it states AMEND4 items 5 and 6 are "still in flight", but git log shows commit b44a5ea "amend4 items 5-6: refuse without window_bounds..." in the ancestry. My V-F9 stands; FSPEED's line is stale. It does not change any verdict.
- Step 2: P3 gate NARROWED per FGROUND C-O2. P3 gates ONLY the clone-chat live acceptance run (step 11), NOT steps 3-6. This corrects my step 2's "Gate to any live DOM work: P3 passes" and the draft's same gate. Reason: the stall risk is real (PROBE-P3 already NOT-RUN once because clone1 batch 9 has been open since 06:01); gating everything on P3 stalls the program on one open clone batch. P8 leaves this step (CLOSED). Add the P3 shadow-DOM check item (section 9.3 P3). Add C-O3: if P3 is still NOT-RUN at step 6, RE-SCOPE the S2 flip class to a Zen-reachable task class (Marionette path, no Brave needed) rather than stalling; the flip still measures the same thing (DOM-first plus code-exec plus checkpoint verification, one class, act-now fallback), only the venue changes.
- Step 2, new sub-step (FARCH): write the Layer 0 + CB-EXEC merged contract NOW, in parallel with AMEND4, while prototype PROOF stays late (step 9). The contract covers snapshot/execute/verify, the CB-1 result contract, CB-2 scope binding, CB-6 one owner, and the stale-ref protocol core (section 9.3 P2). Purpose: stops P2/S1/P5 from inventing three ad-hoc interfaces. FARCH also asks the final adjudication to attach DATES to the deletion gates; I cannot invent dates, so that is recorded here as an open condition for the finalizer/coordinator, not decided by me.
- Step 3: DONE. The fixture 2-vision bench PASSED in 10.86s (a1a672d). S2 gate (a) is MET. The runtime is no longer the blocker; the run happened. Pending: the CB-9 manifest before the pass is quoted as a gate.
- Step 6: add CB-1 as an explicit additional S2 gate (FCODEX, section 9.3 CB-1): the verified/input_sent split lands for the flipped class BEFORE the flip, judged by postcondition pass rate, not envelope ok rate. Add the C-O3 re-scope (Zen-reachable class if P3 is still NOT-RUN).
- Step 7: P2 content expanded per section 9.3 (re-confirm, Zen adapter, eval removal, caller enumeration, EX2/EX3, FARCH protocol core). Scope-refusal deletion SETTLED (FGROUND reconciliation plus V-F11): the rule to DELETE with P2 is the refusal to act on a correctly-addressed action because the OBSERVATION's scope is screen. The rule to KEEP is the halt on a scope CHANGE mid-batch, now enforced by the G28 loud refusal for the given-observation case and by CB-2 binding for the planned-action case. FARCH's overturn is NOT adopted as stated (its premise, live silent substitution, is refuted by V-F11), but its substance (the check must exist in binding form, never simply vanish) is adopted through this reconciliation. FSPEED agrees with the draft's P2 timing here; the disagreement is now resolved on evidence, not vote.
- Step 8: add the CB-10 precondition to the session-level pill (overlay probe or explicit owner deferral before A4 step (a) is judged). Add the relay socket correction (relay.sock, V-F16) to the S1 proof. Add the S1 master-liveness requirement (per-use liveness check plus restart-on-death).
- Step 9: unchanged (prototype proof late). FARCH's daemon-contract writing moves to step 2 (above); proof stays here.
- Step 11 / acceptance: add the per-phase timing split to the live 0-vision pass criteria (section 9.3 A10). Add FGROUND A-L1: the live run's log carries CB's three-way result contract per action (sent, target, verified); never pool the 13/13 fixture with real-task numbers.

### 9.5 Section 6 probe dependencies, updated

- PROBE-S0: INTERIM in (90eb8be). Corrected numbers hold (fresh 4.667s n=10, mux 1.339s n=18, 3.49x, saving 3.328s). Hard requirements added (V-F15). Soak (60 min, ends about 07:41 +07) still pending; the soak verdict stays pending. PROBE-S1's master-liveness finding (masters die after 1-2 min idle even with ControlPersist=600) is consistent with S0 F4 (death self-heals with ControlMaster=auto) and strengthens the per-use liveness requirement. No verdict changes: the per-connection saving is measured and does not depend on the soak.
- PROBE-S1: INTERIM in (untracked log). Relay/broker verified alive and idle; socket path corrected (relay.sock); broker-client gap re-confirmed; transport baselines match S0; master-liveness finding recorded (V-F16). Broker batch proof NOT RUN (sections 5-7 TODO: broker arm types PROBE-S1-OK, one-shot arm types ONE-SHOT-OK, verdict TODO). S1 stays MODIFY, proof-first. What changes it: the broker arm plus one-shot arm results. If the broker arm proves end to end, S1/D3 lift to ADOPT. If it fails, S1 stays MODIFY and the A1/CB-EXEC prototype carries its own transport design.
- PROBE-S2: fixture rung PASSED (a1a672d, 10.86s). Gate (a) MET; gate (b) Y1b fixes NOT met. The bench run serves as the grounding-path re-proof before P2 lands (FCODEX section 5 gap: no separate DOM-bench re-run is needed unless the fixture bench's coverage is challenged). The 100-task benchmark still needs building. What changes S2 now: only the Y1b fixes (gate b) and the CB-1 additional gate (section 9.4 step 6).
- PROBE-P3: still NOT-RUN. Add the shadow-DOM partial outcome and the C-O3 re-scope (section 9.4 step 2). Re-run conditions unchanged (batch 9 complete with a final report commit, no new clone1 batch, Brave confirmed idle).
- PROBE-DOMZEN: still no log. Unchanged. FGROUND V-F11 confirms it has not landed.
- PROBE-P8: CLOSED (3790901). Unchanged.

### 9.6 Disagreements with the draft, updated (items 10-14, added to section 7)

10. P3 gate narrowed (FGROUND C-O2/C-O3, adopted): the draft's "P3 gates any live DOM work" stalls steps 3-6 on one open clone batch. P3 gates only the clone-chat live run; if P3 is still NOT-RUN at step 6, the S2 flip class re-scopes to a Zen-reachable class.
11. Scope-refusal settlement (FGROUND reconciliation plus my V-F11): FARCH's overturn is not adopted as stated (premise refuted: the G28 loud refusal enforces the substitution halt in the repo); its substance is adopted through the binding form. The deletion proceeds with P2, conditioned on CB-2 binding being live in the same step.
12. Contract written early at step 2 (FARCH, adopted): the draft has no contract-writing step before the prototype. The Layer 0 + CB-EXEC merged contract is written at step 2; prototype proof stays late (step 9).
13. CB-1 as an explicit additional S2 gate (FCODEX, adopted): the verified/input_sent split lands for the flipped class before the flip, judged by postcondition pass rate.
14. CB-10 overlay probe (or explicit owner deferral) before A4 step (a) (FCODEX, adopted): the draft does not handle the LIQUID flicker probe at all.

### 9.7 Statements in the body above that this addendum supersedes

Do not quote these without the correction. The body text is left as written at 06:44 +07 as the audit trail; this addendum is the current position.

- Section 0.1 V-F9: "Items 9, 10, 12 remain" is superseded. Corrected: items 9, 10, 11 landed (44c15bb, e912ad4, 8d75135); item 12 is the only outstanding item (V-F14).
- Section 0.2 PROBE-S2: "No bench run yet. S2 gate (a) fixture green and gate (b) Y1b fixes are both NOT met." is superseded. Corrected: the fixture bench ran and PASSED in 10.86s (a1a672d); gate (a) is MET; gate (b) is still NOT met.
- Section 0.2: "PROBE-S0, PROBE-S1, PROBE-DOMZEN: no logs in the tree yet." is superseded. Corrected: PROBE-S0 interim (90eb8be) and PROBE-S1 interim (untracked) are in; PROBE-DOMZEN still has no log.
- Section 0.3: "The 2-vision bench has never run, even in fixture mode." is superseded. Corrected: it ran and PASSED in fixture mode (a1a672d, 10.86s).
- Section 1 tally line: "Tally: ADOPT 19 ..., MODIFY 15 ..., REJECT 0 in full, PENDING 0." is superseded by section 9.2: ADOPT 19 (different composition: P8 and CB-2 out, CB-5 and CB-6 in), MODIFY 14, CLOSED 1 (P8), REJECT 0 in full, PENDING 0.
- Section 1.2 P8 row ("ADOPT, CLOSED as BLOCKED by probe") verdict label is superseded: P8 is CLOSED (section 9.2).
- Section 1.4 CB-2 row (ADOPT), CB-5 row (MODIFY), CB-6 row ("ADOPT direction, MODIFY sequencing") verdict labels are superseded by section 9.2: CB-2 MODIFY, CB-5 ADOPT, CB-6 ADOPT.
- Section 1.4 CB-7 row: "Codex could NOT verify the F2b 11.6s of 12.26s SSH share from laptop logs" and the implication that the dispatch figure is unmeasured are superseded by V-F13: the 11.620s dispatch IS measured (F2b log, D1 V10); only the SSH-only attribution is inference.
- Section 2 step 2: "Gate to any live DOM work: P3 passes" is superseded by section 9.4: P3 gates only the clone-chat live run (step 11).
- Section 2 step 3: "Gate to step 6: the fixture run passes." is superseded: the fixture run has passed (a1a672d); step 3 is done, pending the CB-9 manifest.
- Section 3 rung 1: "It has never run at all (BUILD ONLY)" is superseded: it ran and passed (a1a672d, 10.86s); the rung is passed, pending the manifest before it is quoted as a gate.
- Section 5 triage: "first items 9, 10; item 11 (doc fix) any time" is superseded: only item 12 remains.
- Section 6 PROBE-S0, PROBE-S1, PROBE-S2 entries are superseded by section 9.5.
- Section 7 B2 lift condition ("fix the 3 Y1b real fails, fixture benchmark green, then flip") is partly superseded: the fixture benchmark green limb is now SATISFIED (a1a672d); only the 3 Y1b fixes remain before the flip, plus the CB-1 additional gate (section 9.4 step 6).
- Section 8 evidence index, AMEND4 line ("Items 9, 10, 12 remain; item 12 in flight") is superseded: items 1-11 landed; item 12 only outstanding. Section 8 numbers line ("F2b order-to-overlay 12.262s (dispatch 11.620s, 95 percent, disputed by CB-7: unverifiable from laptop logs)") is superseded by V-F13: dispatch 11.620s measured; SSH-alone attribution unproven; S0 arithmetic survives on direct probes (fresh 4.667s, mux 1.339s, 3.49x, PROBE-S0 interim).

### 9.8 Evidence index additions

- FARCH: improvements/worker-click3-farch-response-log.md (c3bf5e0, 697 lines). ADOPT 15, MODIFY 14, REJECT 0 in full. Scope-refusal dissent, daemon contract early, stale-ref protocol core, real-input default, "SSH is 95 percent" slogan dies, dates on deletion gates (open condition for the finalizer).
- FSPEED: improvements/worker-click3-fspeed-response-log.md (e7562ca, 853 lines). 460x conceded, S1/S2/D6 gated, CB-4/CB-6/CB-7/CB-8 answered. NOTE: its AMEND4 "items 5, 6 still in flight" line is stale against git log b44a5ea (section 9.4 step 1).
- FCODEX: improvements/worker-click3-fcodex-response-log.md (09c6b3f, 411 lines). CB tally ADOPT 9, MODIFY 2, REJECT 0. Fixture bench pass, AMEND4 9/10/11 landed, CB-2 limb 2 closed, deployment drift confirmed live, CB-1 as additional S2 gate, CB-9 manifest gate, CB-10 overlay probe.
- FGROUND: improvements/worker-click3-fground-response-log.md (8d0e38a, 890 lines). P8 CLOSED, P2 expanded per CB-5, P3 gates Brave only, P6a/P6b/P6c, F2b correction of CB-7.
- PROBE-S0 interim: improvements/worker-probe-s0-log.md (90eb8be, 254 lines). Fresh 4.667s (n=10), mux 1.339s (n=18), 3.49x; ssh -f master refuses mux; setsid/nohup master works; residual about 1.2-1.3s per session; master death self-heals with ControlMaster=auto; soak in progress, ends about 07:41 +07, 22/11/2026.
- PROBE-S1 interim: improvements/worker-probe-s1-log.md (untracked, 9181 bytes). Relay alive PID 1821, socket relay.sock; broker idle; broker-client gap re-confirmed; fresh 4.459/4.528s, mux 0.98-1.35s; masters die after 1-2 min idle even with ControlPersist=600; broker arm and one-shot arm NOT RUN (sections 5-7 TODO).
- PROBE-S2 committed: improvements/worker-probe-s2-log.md (f1952a5; bench pass a1a672d, 10.86s; Y1b 3 fails still open, flag NOT flipped).
- NOT read (independence): F1 (7124f1e), F3 (433a6e6), FRT (5f30908). Left to the finalizer.
- New numbers verified by me this session: G28 loud refusal at first_action.py:478-498 plus docstring 328-350 (V-F11); after-image still open at first_action.py:661-665 (V-F11); zen_dom.py locate 567-588 rect-only, hit_check 820-851, eval subparser 1153/1171 (V-F12); F2b log lines 34-35 dispatch 11.620s measured (V-F13); bench pass a1a672d 10.86s and AMEND4 44c15bb/e912ad4/8d75135 (V-F14).

### 9.9 Late landing during the commit step (06:52-06:55 +07, 22/11/2026)

While this addendum was being committed, AMEND4 item 12 LANDED as cbab398 ("AMEND4 item 12: act-now envelope carries a scope-matching after (CL1-SWEEP)", 2026-11-21 23:46:57 +0000). I verified the shape from the diff myself (V-F17): scripts/first_action.py gains _scope_after (line 328: prefers the action result's after when its scope matches the input observation's scope, else a fresh capture in the input scope, screen-scope input reuses the screen capture) and an 'after_screen' envelope field (line 462, set line 737, documented verification-only, non-chainable); the scope check moves before the overlay attempt (refuse before overlay and session, saving the 998ms CL1-SWEEP waste); four regression tests added in tests/test_first_action.py (124 lines). Two files changed, 212 insertions, 6 deletions. This is exactly the both-fields shape my A7/P4 row adopted. Consequences: (a) ALL 12 AMEND4 items are now landed; section 5's triage is complete and section 9.4 step 1's "only item 12 remains" is superseded at commit time; what remains of AMEND4 is confirming the four regression tests PASS on the new code (the commit states they were failing-first on the old code; I verified the shape from the diff, I did not run the tests) and the kill rule at reconciliation. (b) A7/P4 limb 1 (after-image scope) is now CLOSED at code level, not in flight; the A7/P4 row's "execution DEFERRED to AMEND4 item 12" is satisfied by landing. The remaining A7/P4 work is the CB-2 planned-action binding (section 9.2) and the test-pass evidence. (c) B5 is unaffected: items 2-4 limb was already satisfied; the stale-ref protocol is still the single outstanding P2 gate. NOTE for the finalizer: FRT landed as 5f30908 and its commit message mentions a B1 lift reversal. I did NOT read FRT (independence, section 9 intro); I neither adopt nor contest it here. It is left to the finalizer.
