# Worker CLICK3-D3: council review 3 of the breakthrough discussion

Role: independent council reviewer 3. No coordination with other reviewers in this round.
Owner: Pham Tuan. Repo: ~/workspace/computer-use-wayland, branch todolist-push, HEAD a4ecb49.
Start: 2026-11-22 06:08 +07. All times wall-clock Asia/Ho_Chi_Minh plus elapsed from task start.
Decision criterion (owner standing rule 06:07): judge every proposal by the accuracy and speed of
its FINAL RESULT, never by rewrite size or cost. Cost (tokens, time, rewrite effort) is IRRELEVANT.

## 0. Verdict in one paragraph

The three reviews agree on the diagnosis and I agree with them: the screenshot is the wrong
sensor for structured targets, the transport tax is real, and the code-exec plus DOM parts that
would fix both already exist but are not the live path. I ADOPT the direction in full: DOM/a11y
first, element-ref actions, persistent transport, code-exec on, and a live 0-vision benchmark as
the acceptance gate. I MODIFY four items (A3, A4, P4 scope-rule deletion, S3) and one deletion
(D6, scoped not global), all on sequencing and replacement grounds, not on direction. My one
material correction to the evidence is SPEED's multiplexing number: I re-measured it live and
got about 1.2s per multiplexed call, not 0.01s. S0 still goes first, it just saves about 3.3s
per connection, not 4.6s, and the residual 1.2s per call is itself an argument for S1 and A1.
AMEND4 CONTINUES, but SLOWER, per the owner's 06:09 TWO TRACKS rule received during this review.

## 1. What I verified independently vs what I took on trust

### 1.1 Verified by me from source (file and line, this session)

- scripts/cu.py is 3063 lines. observe line 920, observe_screen line 974, image_point line 1000,
  _input_line_changed line 1023 (docstring admits the band check is necessary, not sufficient),
  desktop_act line 1619, guard line 1691 (fetches monitors list plus activewindow per call),
  move line 1770, scope refusal line 1648 (reviewers cited 1649, off by one, immaterial),
  after-capture scope-matching lines 2083-2091, pre-batch re-observe plus settle retry lines
  1733-1749. ARCH F4 (up to 5 captures per batch) is confirmed in structure.
- scripts/first_action.py is 719 lines. attempt_session line 183, session_cmd line 175,
  envelope after-capture cu.observe_screen line 656 with max_width 1920, scope docstring lines
  343-353, OBSERVATION_MAX_AGE_S = 120 line 80. The after-image defect (A7/P4/SPEED 2d) is
  confirmed from source: the envelope capture is unconditional and screen-scoped.
- scripts/fastpath.py: dom_rect_to_screen_point line 152, dom_rect_to_image_point line 195.
  scripts/dom_act.py: ground_many_one_shot line 240, focus_type line 425, and lines 147, 159,
  312 call dom_rect_to_image_point. The image-frame round trip (exact rect to screen point to
  image point and back) is confirmed from source.
- scripts/zen_dom.py harvest line 905. scripts/cdp.mjs lines 237-239: the comment states Brave
  holds no debugging port on its default profile. scripts/code_exec.py line 134 gates on
  CU_CODE_EXEC, cu.py lines 2770-2793 refuse code-exec when the flag is off. scripts/overlay.py
  is 613 lines with holders.json accounting (lines 38, 86-102). scripts/cursor_session.py
  supervise line 228. scripts/session_remote.py 1601 lines, session_driver.py 180 lines.
- tests/two_vision_bench.py on origin/main: docstring states VISION 1 is a DOM harvest, NOT a
  screenshot, and scoring is by OUTCOME (message in thread DOM), never point-in-box. Confirmed.
- docs/clone2-dom-grounding-20261122.md on origin/main exists and states the cited numbers
  (66 rects, Marionette median 0.030s, 5 clicks all landed, verify 0.002-0.015s).
- G30 in ~/workspace/cf26-upload/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md lines 302-310: confirmed.
  Muse clicked (250,1037), 64px above the real field (y 1101-1164, center (306,1132)); CL1-MSG2
  clicked (300,1026), 75px too high; Codex re-grounded, clicked (300,1132), message sent 01:37.
  Root cause vision-grounding, not coordinates, not typing.

### 1.2 Verified by me live (probes this session)

- Fresh SSH via ssh-laptop.sh: 4.447s for one call (env check plus socket listing). Reproduces
  SPEED's 4.43/4.93/4.48s.
- Multiplexed SSH: 8 samples, two methods (wrapper script and plain ssh, same master): 0.987s,
  1.328s, 1.234s, 0.914s, 1.298s, 1.455s, 1.207s, 1.352s. Mean about 1.25s. This does NOT
  reproduce SPEED's 0.01s x3. The saving per connection is about 3.2s (4.45 to about 1.25s),
  roughly 3.5x, not 460x. Likely explanation: the residual about 1.2s is per-session sshd and
  shell setup on the laptop, which multiplexing does not remove. Consequence: per act-now
  (3 connects) S0 saves about 10s, taking 16s to about 6s, not to about 2s. S0 stays first,
  the magnitude claim is corrected, and the residual strengthens S1 (the Broker avoids
  per-call sshd sessions entirely). The 1-day soak test SPEED flagged is still owed.
- CU_CODE_EXEC is OFF in the live path: `env | grep CU_CODE_EXEC` on the laptop returned
  nothing (probe 06:12). Confirms SPEED section 2e.
- Relay socket exists: /run/user/1000/agent-computer-use/cursor-guard.sock present (probe 06:12).

### 1.3 Taken on trust, with source (not re-measured by me)

- DOM bench numbers (clone2 batch 7): clone2's report, council and redteam corrected. Not
  re-run here: no venv, no pytest, no Firefox/geckodriver tooling in this session.
- Vision 58.6% first-try hit rate (E2 calibration): memory files and the error file. The G30
  record I did verify independently, and it shows the same failure mode.
- Brave accepts --remote-debugging-port at launch on the existing profile with login intact:
  standard Chromium behavior, stated by GROUNDING, not tested here. Testing it would kill
  clone1's Brave window mid-batch-8. Treated as a hypothesis for the P3 experiment, not a fact.
- The 87.8% think-observe-think gap (10x review): measured with a local helper, known hole
  (no SSH hop measured). SPEED's correction stands: it does not transfer to the remote path.
- Code-exec Pick 1 win and merge (commits cited by SPEED): not re-verified commit by commit.
- AMEND4 full 12-item list: only item 12 is visible in this working tree (driver log,
  improvements/worker-codex-amend4-driver-log.md line 38). The other 11 items I judge by
  their known lineage (AMEND3 steps and the redteam findings), and I say so where it matters.
- CODEX-BREAKTHROUGH proposals: not landed. Only a launch log exists (untracked file
  improvements/worker-codex-breakthrough-log.md, Codex PID 781223 launched 06:04). Marked
  PENDING below. I invent nothing for it.

## 2. Verdict table (every proposal, none skipped)

Legend: ADOPT means do it as proposed. MODIFY means do it with the stated change. REJECT means
do not do it. PENDING means the input has not landed.

### 2.1 ARCH (worker-arch-review-log.md, commit 074c1d7)

| ID | Proposal | Verdict | Evidence and reasoning |
|----|----------|---------|------------------------|
| A1 | Layer 0 persistent driver daemon (snapshot/execute/verify, structured-first) | ADOPT | DOM numbers verified in source (0.030s for 66 rects, 5/5 clicks, verify 0.005-0.015s) vs vision 58.6% first-try and G30/G31 45-75px eyeball errors. The parts exist (code_exec, session_driver, Broker, dom_act, cdp.mjs). Cost is irrelevant by the decision criterion. The single-runner lock must move into the driver as a task lock. |
| A2 | Layer 1 pixels demoted to fallback-only, pixel-band labeled weak | ADOPT | The code itself admits the band is necessary, not sufficient (cu.py 1023-1076). Canvas, games, video, and Zen chrome UI have no structured path, so the fallback stays. Honest labeling costs nothing and stops the band being read as verification. |
| A3 | Delete session supervisor tree | MODIFY | Direction right, timing wrong. The tree's real jobs are a named killable scope, cancel/stop, and the pill label. Delete only after the driver holds all three (task scope plus cancel file plus driver-owned pill) and they are proven live. Deleting first loses cancel/stop. End state ADOPT, sequence after A1. |
| A4 | Delete overlay daemon server (keep pill visibility) | MODIFY | Same logic as A3. 613 lines plus holder accounting for a boolean plus a label is the right thing to delete, but the pill is the owner's visibility into a run, and the current acquire path works (315-349ms). Delete the server only when a driver-owned pill (or compositor-plugin indicator) is proven to show and to clear, including when the driver dies mid-task. End state ADOPT, sequence after the replacement is proven. |
| A5 | Delete one-shot SSH loop (persistent Broker only) | ADOPT | My live probes: fresh 4.45s, mux about 1.25s, so even multiplexing leaves a per-call tax the Broker avoids. Relay socket confirmed alive. Keep one-shot SSH as a documented emergency fallback when the Broker is down, not in the live loop. The word "only" applies to the default path. |
| A6 | Delete file-based observation/action IPC | ADOPT | Same evidence as A5. JSON-lines over the persistent channel (session_driver shape exists). Keep file IPC only as the fallback transport when no Broker is reachable. The 120s window, G28 refusal class, and path confusion all trace to state moving as files. |
| A7 | Delete act-now after image as chainable observation | ADOPT | Proven defective by construction from source (first_action.py:656 overwrites the scope-matching after-capture). Adopt the both-fields shape: after (scope-matching, chainable) plus after_screen (verification only, documented non-chainable), plus a regression test. Same row as P4 and SPEED deletion 4; merged. |
| A8 | Delete pixel-band verification for structured targets | ADOPT | Code admits insufficiency; DOM value check is sufficient and 100-1000x cheaper (0.002-0.015s vs re-screenshot plus model read). Keep the band as a diagnostic only, never as a pass signal. |
| A9 | Coordinate model to one system (CSS px element rects, converted once at driver edge) | ADOPT | For structured targets. The four-system tower has five proven bug sites (F2b-1 region vs monitor_box, C12 window-relative origin, 1.10x vision scale, G28, after-scope). The pixel fallback keeps its own frame internally; it is not the shared model. |
| A10 | Acceptance test becomes 0-vision live benchmark on real ws2 clone chats | ADOPT | Conditional on sequencing (see section 4). The fixture 2-vision benchmark already is DOM-first; its VISION 1 is a harvest, not a screenshot. The live part is the upgrade: fixture proof is not live proof. Score by DOM outcome only, accuracy at least 90%, wall time end to end including transport. Keep an optional final screenshot as unscored human evidence (P9). Needs a quiet window and clone coordination, since it touches real threads. |

### 2.2 GROUNDING P1-P9 (worker-grounding-review-log.md, commit d1fc4e9)

| ID | Proposal | Verdict | Evidence and reasoning |
|----|----------|---------|------------------------|
| P1 | DOM/a11y default router | ADOPT | Encode the router in code, not convention. Order as proposed: Zen Marionette/BiDi, Chromium CDP, AT-SPI, then screenshot. Must fail closed to the screenshot fallback when no structured path is available, with the fallback labeled. Without a router the system drifts to the worse path because the worse path works everywhere. |
| P2 | Element-ref action interface rewrite | ADOPT | Highest-leverage code change with P3. The round trip exact rect to screen point to image point and back is confirmed in source (dom_act.py 147/159/312, fastpath.py 195-243, cu.py 1000-1005) and buys nothing: the Pointer takes screen coordinates. Delete dom_rect_to_image_point from the live path (keep for tests and legacy). Note AMEND3 step 2 already deleted its fallback (commit e5c1c47), so this completes a direction already landed. |
| P3 | Brave relaunch with debugging port | ADOPT | Controlled experiment, highest leverage for live tasks. Conditions: quiet window, never mid-batch (clone1 is mid-batch-8 now), verify /json/list shows the Muse tab and login intact, one fill plus assert on a scratch input first. If Brave refuses the port on its default profile, fall back to the agent-managed Chromium with the clones' chats. The flag working on the existing profile is a hypothesis until run, not a fact. |
| P4 | After-image scope fix (both after + after_screen) | ADOPT with MODIFY | ADOPT the both-fields fix plus regression test (merged with A7). MODIFY the scope-rule deletion: delete the cu.py:1648 scope refusal only as part of P2. While actions are still pixel-addressed, the refusal protects typing against a screen observation. Once actions are element-ref addressed, scope is irrelevant and the refusal can go. |
| P5 | DOM verification mandatory | ADOPT | focus_check and type_check become required for any batch with a type action; CDP fill read-back and assert polling are the model. AMEND3 steps 3 and 4 already moved this way (grounded band x-range, V11 typed flag). Pixel band becomes diagnostic only. |
| P6 | Measure the vision call | ADOPT | Cheapest item on the list and a precondition for honest speed claims. Capture is 26.5ms and DOM rects 0.030s, but the model read that locates the target is seconds and timed nowhere. The 10x loop cannot optimize what it does not measure. |
| P7 | Session handover protocol | ADOPT | One active remote session per Firefox instance is a proven hard constraint. Any live task needing grounding on BiDi and real input on Marionette has no defined sequence today (bench TODO D1). Write the protocol before the first live task needs both. Small doc plus enforcement. |
| P8 | Zen chrome Marionette context test | ADOPT | Bounded probe, low priority. If set_context("chrome") works, the last screenshot-only surface falls. If blocked without a restart, keep screenshots ONLY for chrome UI and record the boundary explicitly. Do not spend more than a bounded probe on it; AT-SPI cannot see Zen, so that path is closed. |
| P9 | Keep one screenshot for the human | ADOPT | VISION 2 in the benchmark stays as unscored human evidence. The machine scores by DOM; the screenshot is evidence for the human, not perception for the machine. |

### 2.3 SPEED S0-S3 plus six deletions (worker-speed-review-log.md, commit a4ecb49)

| ID | Proposal | Verdict | Evidence and reasoning |
|----|----------|---------|------------------------|
| S0 | Step 0 persistent SSH multiplexing (do now) | ADOPT | Corrected numbers: my 8 live samples give mux about 0.91-1.46s, mean about 1.25s, vs fresh 4.45s. Saving about 3.2s per connection, about 3.5x, not 460x and not 0.01s. Per act-now (3 connects) that is about 16s to about 6s, not about 2s. Still the cheapest win available, do it first, with fallback to fresh SSH. Soak test still owed (does the master survive the historical about-30s SSH death over hours). |
| S1 | Step 1 act-now over persistent relay broker | ADOPT | Relay socket confirmed alive by my probe. Session start 0.4-2.1s per batch plus per-call sshd sessions disappear. Build S1 as the first slice of A1, not as a separate system. Flag for council: the 315-349ms overlay acquire per batch becomes the largest remaining item, and a session-level pill (acquire once per task) is the first-principles shape, but the pill is owner visibility, so that change needs a council decision, not a unilateral one. |
| S2 | Step 2 DOM-first + code-exec + checkpoint verification (CU_CODE_EXEC=1 on) | ADOPT | Flag confirmed OFF in the live path by my probe. The implementation is built, merged, and already won Pick 1; the live loop never switched on. This is the single biggest free win. Gate with the 2-vision benchmark, then the live 0-vision benchmark. |
| S3 | Step 3 laptop-side task runner (only if Step 2 plateaus) | MODIFY | Do not build a separate runner. S3 substantially overlaps A1: a laptop-side runner that grounds, acts, and verifies locally and streams back compact state IS the A1 driver daemon approached from the other side. Fold S3 into A1. The plateau condition stays: A1's full form is justified by S2's measured plateau, but S0-S2 plus the P3 experiment should come first, and A1 should be built as the driver, not as a second runner. |
| D1 | Delete fresh SSH per call | ADOPT | Merged with A5. Same evidence. |
| D2 | Delete scp for JSON files | ADOPT | Merged with A6. Same evidence. |
| D3 | Delete per-batch session spawn | ADOPT | Merged with S1 and the A3 end state. Session becomes a per-task lease through the relay. |
| D4 | Delete screen-scope after-capture | ADOPT | Merged with A7 and P4. Same evidence. |
| D5 | Delete per-action model call as default | ADOPT | Merged with S2. Code-exec programs with checkpoint verification become the default; the stepwise loop is the fallback for unknown shapes only. |
| D6 | Delete 120s freshness window as gate on DOM work | MODIFY | Scoped deletion, not global. For DOM-grounded work, re-read the DOM (0.030s) instead of refusing for staleness. Keep the window for pixel-addressed work, where staleness is real and the refusal protects against acting on a dead frame. |

### 2.4 CODEX-BREAKTHROUGH

| ID | Proposal | Verdict | Evidence and reasoning |
|----|----------|---------|------------------------|
| CB | All proposals | PENDING | Report not landed. Only a launch log exists (untracked improvements/worker-codex-breakthrough-log.md, Codex PID 781223 launched 06:04 on the laptop). I invent nothing. The cross-response round and the joint adjudication must leave room to integrate its proposals when they land, and must not treat this review as complete on that axis. |

## 3. Order of work

0. S0 plus P6, now. Both are cheap, both are reversible, and P6 makes every later speed claim
   honest. S0: ControlMaster in ssh-laptop.sh plus a watchdog that restarts the master, fallback
   to fresh SSH on any multiplex failure. P6: log vision-call latency (observation to located
   target, seconds) in the harness. Also start the S0 soak test the same day.
1. P3 Brave relaunch experiment, in the next quiet window between clone batches. This unlocks
   the live CDP path, and the live benchmark (A10) cannot run on real clone chats without it
   or its Chromium fallback. One experiment, one fill plus assert on a scratch input, then decide.
2. S2 (flip CU_CODE_EXEC=1 in the live path) plus P1 (router in code) plus P5 (mandatory DOM
   verification) plus P2 (element-ref interface). Dependency order inside this step: P1 and P5
   are rewiring of existing code, P2 is the interface rewrite, S2 is the switch-on. Run the
   fixture 2-vision benchmark as the smoke gate at the end of this step.
3. S1, built as the first slice of A1 (act-now over the Broker, JSON over the channel, no scp,
   scope-matched after-capture). P7 (handover protocol) lands before any live task needs both
   BiDi and Marionette. P8 (Zen chrome context probe) runs in parallel at low priority.
4. A1 full driver daemon (snapshot/execute/verify), absorbing S3. A3 and A4 deletions land
   only when their replacement functions are proven live (driver task scope, cancel file,
   driver-owned pill that shows and clears, including on driver death).
5. Acceptance: the live 0-vision benchmark on real ws2 clone chats (A10). Fixture 2-vision is
   the smoke gate, not the acceptance gate.

What I would NOT do: do not build S3 as a separate runner alongside A1 (duplicate systems);
do not delete the supervisor tree or the overlay daemon before their replacements are proven
(a run with no cancel and no pill is worse than a run with a slow pill); do not run the live
benchmark against the fixture and call it live proof.

## 4. Acceptance test: 0-vision live benchmark, not 2-vision

The planned 2-vision benchmark stays, but as the fixture smoke gate, not the acceptance gate.
Its VISION 1 is already a DOM harvest, not a screenshot, so the "2-vision" name already
overstates the machine's dependence on vision: the machine never locates from pixels in that
design. The acceptance gate becomes A10: same shape, against the REAL clone chats on ws2,
DOM harvest, plan, execute, DOM verify, zero screenshots in the machine loop, accuracy at
least 90%, total wall time measured end to end including transport. One final screenshot may
be kept as unscored human evidence (P9); it must not feed the score. Two conditions: the
live run needs P3 (or its Chromium fallback) to reach the chats, and it needs a quiet window
with clone coordination, since it touches real threads. If the live benchmark cannot run yet
for coordination reasons, the fixture 2-vision is the interim gate, and the gap must be
recorded as a gap, not papered over.

## 5. AMEND4 sequencing: CONTINUE, but SLOWER

During this review the owner added a standing rule (06:09, TWO TRACKS, received via a MEMORY.md
update mid-session): the team debates directions, while the fix and improve-current track keeps
going, but SLOWER and more gradually to save tokens, since no direction is confirmed best yet
and the current work continues meanwhile. My recommendation follows it exactly:

- CONTINUE. Do not pause and do not stop AMEND4. Stopping would leave known-broken behavior
  live in the loop the clones use today, notably the after-image trap (item 12), and the
  rewrite is not adjudicated yet, so there is no adopted direction to redirect into.
- SLOWER. Run AMEND4 at the reduced pace the owner ordered, to save tokens while the
  breakthrough direction is debated and adjudicated.
- TRIAGE inside the slow track. Prioritize items that survive any outcome: item 12
  (after-image scope, identical to A7/P4/D4) and the DOM-verification items. Deprioritize
  pixel-path-only patches, especially pixel-band verification work: A2 and P1 demote that
  path to fallback-only, so polishing its verification is low value under any outcome.
  For each of the 12 items, Codex already records patch vs remove vs redesign; keep that
  discipline, and kill an item at reconciliation if the adopted rewrite deletes its target.
- REDIRECT, not yet. No wholesale redirect of AMEND4 into the rewrite before adjudication.
  After adjudication, re-triage the remaining AMEND4 items against the adopted direction in
  one pass, and kill the ones the rewrite deletes rather than finishing them.
- Why not pause: the current loop is the only working loop, the clones depend on it, and
  AMEND4 item 12 fixes a defect that bites live tasks today. Why not full speed: the owner
  ordered the slower pace, and several AMEND4 items patch code the rewrite may delete.

## 6. Dissent and open questions for the cross-response round

- SPEED's 0.01s multiplexing figure does not reproduce in my session (8 samples, 0.91-1.46s).
  I want SPEED's method checked: what exactly was timed, and was the master warm in a way mine
  was not. If 0.01s is real under some setup, I want that setup named so it can be reproduced.
  Either way S0 stands; only the magnitude changes.
- ARCH deletes the supervisor tree and the overlay daemon. I agree on the end state but I
  require the replacements proven first. If ARCH holds that the driver can own the pill from
  day one, I want the failure mode named: what clears the pill when the driver dies mid-task.
- GROUNDING's P3 is the highest-leverage experiment, but it is also the only proposal in this
  round whose core claim (flag works on the existing Brave profile, login intact) is untested
  by anyone. The experiment design must include the rollback: if the relaunch loses the
  session, the cost is a re-login, and that must be stated before the window, not after.
- The 10s target for a tc02-class task depends on model inference time, which nobody in this
  round measured. P6 must land before anyone claims the target is met.

## 7. Log

- 06:08 +07 (T+0m): task received. Repo on todolist-push HEAD a4ecb49, confirmed by git log.
  Read all three review logs in full.
- 06:10 +07 (T+2m): spot-checked line references in scripts/cu.py, scripts/first_action.py,
  scripts/fastpath.py, scripts/dom_act.py, scripts/zen_dom.py, scripts/cdp.mjs,
  scripts/code_exec.py, scripts/overlay.py, scripts/cursor_session.py. All cited lines
  confirmed except the cu.py scope refusal at 1648 not 1649 (immaterial).
- 06:12 +07 (T+4m): live probes. Fresh SSH 4.447s. CU_CODE_EXEC unset on laptop. Relay
  socket present. G30 error-file lines verified.
- 06:13-06:15 +07 (T+5-7m): multiplexed SSH probes, 8 samples across two methods,
  0.91-1.46s. Does not reproduce SPEED 0.01s. Recorded as the headline correction.
- 06:15 +07 (T+7m): checked AMEND4 driver logs (only item 12 visible in this tree),
  two_vision_bench.py docstring on origin/main, clone2 DOM report on origin/main.
  Received the owner's 06:09 TWO TRACKS rule via a MEMORY.md update mid-session.
- 06:17 +07 (T+9m): wrote this log. Next: commit with explicit pathspec, verify with
  git ls-remote, report to COORD-CLICK-3.
