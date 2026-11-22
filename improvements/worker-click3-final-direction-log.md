# Worker CLICK3-FINALIZER: FINAL direction for computer-use-wayland

Owner: the owner. Role: final adjudicator (Worker CLICK3-FINALIZER). This is
the FINAL direction, not a draft and not a set of options. One direction:
what to build, in what order, what the acceptance test is, and what stops.
The coordinator executes it from the plan in section 6. I do not execute
it myself.

Decision criterion (owner standing rule 06:07): the final result must be
the MOST ACCURATE and the FASTEST; cost is IRRELEVANT (tokens, time,
rewrite effort). A bigger rewrite that wins on accuracy and speed beats a
smaller patch that does not. Evidence standard (owner 06:34, Lauren Tan
standard): every claim carries real measured numbers (test command,
output, commit hash, time log where applicable). A proposal with no
measured evidence behind it does not count as feasible. Feasibility rule
(owner 06:32): no direction is finalized on theory alone; where a verdict
rests on probe evidence not yet in, it is marked CONDITIONAL and the probe
sits in the gated order of work. First principles (owner 06:01): question
whether each piece should exist at all; rewrite when the evidence
supports it.

Rules honored: no em dash (U+2014) or en dash (U+2013) anywhere in this
file. No personal info. Evidence with every claim. Wall-clock
Asia/Ho_Chi_Minh plus elapsed time. Commit with an explicit pathspec
immediately after staging, never plain git commit, never git add -A.
Verify push with git ls-remote. Never ydotool. This is an adjudication,
not my own work, so no self-healing question arises.

## 0. Log and what I verified myself

- 06:52 +07 (T+0m): task received. Repo ~/workspace/computer-use-wayland,
  branch todolist-push. Fetched first; local HEAD was 48c6aee at start.
- 06:52-07:00 (T+0-8m): read in full the adjudication DRAFT
  (improvements/worker-click3-adjudication-log.md, 9d23834, 585 lines),
  the Codex report (improvements/codex-breakthrough-report.md, 2596287,
  138 lines), ARCH-REVIEW (074c1d7, 280 lines), GROUNDING-REVIEW
  (d1fc4e9, 150 lines), SPEED-REVIEW (a4ecb49, 212 lines), and the probe
  logs PROBE-S0 (90eb8be), PROBE-S1 (1af7330), PROBE-S2 (f1952a5,
  bench pass a1a672d), PROBE-P3 (7b1006a), PROBE-P8 (3790901).
- 07:00-07:08 (T+8-16m): extracted and compared the verdict tables of
  all eight final positions (F1 7124f1e, F2 48c6aee, F3 433a6e6, FRT
  5f30908, FARCH c3bf5e0, FGROUND 8d0e38a, FSPEED e7562ca, FCODEX
  09c6b3f) and read their dissent, order, acceptance, stops, and open
  condition sections in full where they bear on a decision.
- 07:08-07:12 (T+16-20m): spot checks of my own (section 0.1). The
  branch moved during this work: PROBE-S1 landed as 1af7330 while I
  read. I fetched again before writing; HEAD at writing is 1af7330.
- Follow-up incorporated: PROBE-S1 landed since the task started
  (1af7330a232d96df5af35806b4eb1510d63e1cee). Its numbers are read from
  its own log, not from the brief alone (section 0.1 V-Z3).

### 0.1 Spot checks run by me in this session (new verification, not trust)

- V-Z1. Branch state at writing: HEAD 1af7330 (probe-s1). AMEND4 all 12
  items landed on todolist-push: items 1-8 (cc964b2, c1ea773, 62b740e,
  72120aa, b44a5ea, 49081aa, af0fa87), item 9 (44c15bb), item 10
  (e912ad4), item 11 (8d75135), item 12 (cbab398). Verified from git log
  this session. The VM lane of item 12 is cbab398; its shape was
  verified from the diff by F2 (V-F17): _scope_after at
  first_action.py:328, after_screen envelope field at line 462 set at
  line 737, scope check before the overlay attempt, four regression
  tests in tests/test_first_action.py (124 lines). The four tests were
  NOT run by F2 and NOT run by me; test-pass evidence is still open
  (section 7).
- V-Z2. Codex-lane item 12 is UNCONFIRMED. The driver log
  (improvements/worker-codex-amend4-driver-log.md) records a queue-check
  at 06:19 +07 with 0 hits for the queued item-12 follow-up messages
  (message 01a20058) and its Result section is still "(pending)" with
  branch, commits, and test counts unfilled. I do not assume it done.
  It is re-commissioned or confirmed per section 6 step 1, not assumed.
- V-Z3. PROBE-S1 numbers read from its log (1af7330) this session.
  Broker core batch 12.110s vs one-shot core batch 28.700s, delta
  16.590s, broker 2.37x faster. Broker core = observe req 3.270s plus
  act req 4.270s plus after-image fetch 4.570s. Laptop-side act through
  the broker about 258ms (preflight 71ms plus execution 109ms plus
  after-capture 78ms). Each request/result round trip costs the mux SSH
  price (mean 1.16s). Relay alive PID 1821, 15h uptime, socket
  /run/user/1000/computer-use-wayland/relay.sock (the brief's
  cursor-guard.sock path was the cursor-guard socket, not the relay).
  Type visibly landed in the scratch field (PROBE-S1-OK). Gating
  conditions measured: (1) laptop tree behind the VM (HEAD 56f5af4 vs
  48c6aee), no first_action.py/act-now on the laptop, laptop cu.py and
  session_driver.py default the browser endpoint to 9222 (Zen BiDi), so
  browser observe through the broker 404s and fatally ends the session;
  (2) scp costs about 4.6s even over a live multiplexed master
  (4.57-4.93s, n=4), fresh scp 8.1-9.4s, so S0 alone does not fix scp;
  (3) ControlMasters die after about 1-2 min idle without keepalive
  (measured twice); with ServerAliveInterval=15 the master survived the
  whole broker arm (about 4 min); per-use liveness check plus
  restart-on-death required, 1-day soak still owed; (4) a failed
  read-only browser observe is session-fatal by construction; (5)
  single-owner serialization under concurrent VM workers unexamined
  (second start gets busy). The delta is mostly transport, not the
  session spawn (one-shot spawn plus act plus teardown is only about
  0.9s inside the 5.375s invocation).
- V-Z4. PROBE-S0 interim (90eb8be) numbers confirmed from its log:
  fresh SSH mean 4.667s (n=10), healthy mux mean 1.339s (n=18 accepted
  samples), saving 3.328s per connection, 3.49x. ssh -M -f -N master
  refuses mux sessions (Permission denied, falls back to fresh cost)
  and dies in about 1-2 min; setsid/nohup master without -f accepts
  mux reliably; residual about 1.2-1.3s per session is server-side
  session setup, not shell startup (F2 V-F15). Soak (60 min, ends about
  07:41 +07) still in progress at finalization.
- V-Z5. PROBE-S2 fixture bench PASS confirmed from its log (a1a672d):
  bench wall 10.8596s, visions_used 2, outcome PASS, both sends V12
  gated, run_id bench-20261121T234030Z-86e8d8. Y1b 3 real fails still
  open (1e chr NameError; 2a codemode wall preemption absent, elapsed
  7.20s; 2b code_exec wall preemption absent, elapsed 6.20s, ok=True
  with NO error, silent success). Gate (a) MET, gate (b) NOT met, flag
  NOT flipped.
- V-Z6. PROBE-P8 CLOSED negative confirmed from its log (3790901):
  Marionette chrome context BLOCKED, HTTP 500, error "unsupported
  operation", MOZ_REMOTE_ALLOW_SYSTEM_ACCESS required, C12 reproduced
  live. PROBE-P3 NOT-RUN confirmed (7b1006a): clone1 batch 9 open since
  06:01, Brave untouched. PROBE-DOMZEN: no log, no commit anywhere in
  the tree at finalization; still not landed.
- V-Z7. Codex and FCC discussion positions: STILL PENDING at
  finalization. The Codex discuss driver log
  (improvements/worker-codex-discuss-driver-log.md) last records check 1
  at 06:48 +07 (Codex PID 813390 alive, position file not yet written).
  The FCC discuss driver log records run 1 finished 06:38 +07 (position
  file /tmp/fcc-discuss-position.md, 3008 bytes, verdicts row-for-row
  identical to the draft, CB PENDING, header finished-time defect noted)
  and run 2 launched 06:48 +07 (detached, follow-up for the Codex
  report, PID 824585). No Codex or FCC run-2 position file has landed
  on todolist-push at finalization. They are recorded as pending inputs
  in section 7 and do NOT block this decision.
- V-Z8. Clone states at finalization (origin/main log): clone1 batch 9
  open, STALL 48 min, nudged 06:45 (ae636a2), no reply yet (watchdog
  8e09e8e, 06:48). Clone2 batch 10 running, tasks 1, 3, 4 done as of
  06:43 (d41898b); task 2 waits on the AMEND4 log, which is now 12/12,
  so task 2 is unblocked by this landing.
- V-Z9. The defective-test caveat (FRT V-F6) verified from the landing
  commits' own messages as cited: 62b740e records "F4 RT2 test
  defective", 72120aa records "F5 behavior test defective", b44a5ea
  records "F2/F3 RT2 tests defective". Landing with a defective proof
  test is not proof-grade landing (CB-8). This bears on the B5 decision
  in section 2 item (d).

### 0.2 Facts all eight final positions now agree on (the settled base)

- SPEED 460x is dead; S0 stands ADOPT on corrected numbers (fresh
  4.667s n=10, mux 1.339s n=18, 3.49x, PROBE-S0 interim 90eb8be).
- Vision is the proven error source (E2 17/29 first-try, 58.6%, Wilson
  95% 40.7-74.5%; G30 64px and 75px misses; G31 45px eyeball error),
  never a coordinate failure (pointer error 0.5-0.9px, 29/29 clicks
  executed). DOM grounding is single-source (clone2 batch 7: 66 rects,
  Marionette median 0.030s; C1 applies).
- The 2-vision fixture bench has now RUN and PASSED (a1a672d, 10.86s);
  Y1b 3 real fails still open; flag NOT flipped.
- The Broker exists and now WORKS from the VM (PROBE-S1 1af7330,
  12.110s vs 28.700s, 2.37x); the per-batch spawn deletion is gated on
  the five measured conditions in V-Z3, not on a further proof run.
- P8 is CLOSED (3790901, BLOCKED); Zen chrome UI stays screenshot-only
  unless the owner approves a Zen restart with
  MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1.
- AMEND4 is COMPLETE (all 12 items landed); what remains is test-pass
  confirmation, the Codex-lane confirmation, the round-3
  patch-vs-rewrite judgment, and the kill rule at reconciliation.
- The P2/AMEND4 collision is closed by landing (items 2-4 landed:
  c1ea773, 62b740e, 72120aa); the stale-ref protocol is still open.
- CB-EXEC, A1, and S3 are ONE destination, not three builds (F1, F2,
  F3, FRT, FARCH, FCODEX agree on the merge; they disagree only on how
  much of CB-EXEC is authorized now, decided in section 2 item (a)).
- The scope-as-capability refusal deletion is NOT a simple deletion
  (FARCH overturn, FGROUND reconciliation, F2 V-F11); decided in
  section 2 item (f).
- No final position proposes pausing, redirecting, or stopping AMEND4;
  it is complete, and the TWO TRACKS pace rule no longer governs new
  work because the fix track has landed.

## 1. VERDICT TABLE (every proposal, none skipped)

Legend: ADOPT means do it as proposed. MODIFY means do it with the stated
change; the gating conditions attached are what must be proven before it
proceeds. REJECT means do not do it as stated (no proposal is rejected in
full; rejected parts inside merged rows are named). CLOSED means the probe
answered it and no further work is authorized. CONDITIONAL marks a verdict
whose finality depends on probe evidence not yet in; the exact evidence
that would make it final is stated in the row. Coverage: 34 rows covering
all 40 proposals: ARCH A1-A10 (10 rows, D2 merged into A6, P4 and D4
merged into A7), GROUNDING P1-P9 (8 rows), SPEED S0-S3 plus six deletions
(5 rows, D1 into S0, D3 into S1, D5 into S2), CODEX-BREAKTHROUGH CB-1 to
CB-10 plus CB-EXEC (11 rows).

Tally in proposal terms: ADOPT 19 (A2, A6, D2, A7, P4, D4, A9, P1, P3, P6,
P9, S0, D1, S1, D3, CB-6, CB-7, CB-8, CB-9), MODIFY 20 (A1, A3, A4, A5, A8,
A10, P2, P5, P7, S2, D5, S3, D6, CB-1, CB-2, CB-3, CB-4, CB-5, CB-10,
CB-EXEC), CLOSED 1 (P8), REJECT 0 in full. Final positions tallies for
comparison: draft ADOPT 15 MODIFY 14 PENDING 1; F1 ADOPT 21 MODIFY 18;
F2 ADOPT 19 MODIFY 14 CLOSED 1; F3 ADOPT 25 MODIFY 15; FRT ADOPT 16
MODIFY 21 REJECT 3 as stated.

### 1.1 ARCH (worker-arch-review-log.md, 074c1d7)

| ID | Proposal | Verdict | Evidence, reasoning, and gating conditions |
|----|----------|---------|---------------------------------------------|
| A1 | Layer 0 persistent driver daemon (snapshot/execute/verify, structured-first) | MODIFY | Direction right: structured state is exact and cheap (66 rects median 0.030s, clone2 batch 7, single-source, C1 applies), and a state-holding driver is the only shape that stops paying setup per action. But the full-replacement claim has no existence proof (RTD C2, accepted by all eight final positions): session_driver.py runs cu.main() per command, code_exec.py is an in-process program model not a daemon, dom_act.py still grounds through image points, cdp.mjs drives agent-managed Chromium only. "Exists" means a file exists, not that the composition works. MERGED with S3 and CB-EXEC into ONE build with ONE design spec (CB-EXEC contract, section 2 item (a)) and ONE prototype. Gating conditions: the contract is written at step 2; a staged prototype must prove snapshot/execute/verify end to end on one live ws2 clone chat plus held-out tasks before anything is deleted (B6 lift, section 5). The prototype design must cover the single-runner lock as a task lock, pill visibility, the one-session-per-browser constraint, daemon crash and stale-state behavior, session-holding scope (RTD C5: holding the single Firefox session blocks every other tool for the task duration), lifecycle across laptop sleep and reboot, and the wedged-session recovery protocol (FRT-B1: who kills a wedged session, on what timeout, with what watchdog). No deletions until then. |
| A2 | Layer 1 pixels demoted to fallback-only, pixel-band labeled weak | ADOPT, with sequencing constraint | Proven by vision 58.6% first-try (E2 17/29, Wilson 40.7-74.5%) and by the code itself admitting the band is necessary, not sufficient (cu.py:1023-1076). Constraint, from RTD and accepted by all eight final positions: demote only after the router (P1) and its fallback trigger are proven; Zen chrome UI stays pixel-primary because P8 is now CLOSED BLOCKED (3790901, HTTP 500, MOZ_REMOTE_ALLOW_SYSTEM_ACCESS required), so today pixels are its only perception (AT-SPI cannot see Zen, C12 probe). Without that constraint A2 strands Zen chrome tasks. Fallback stays for canvas, games, video, Zen chrome UI. |
| A3 | Delete session supervisor tree | MODIFY | Direction right, timing conditional. The tree's real jobs are a named killable scope, cancel/stop, the session pill label, and the single-runner lock. Gating condition: delete only when the driver demonstrably holds scope plus cancel latch plus lock on a live run (B4 lift, section 5). Until then the supervisor is the lock holder, and deleting it risks two live runners and loses the cancel/stop path. The F1 failure cluster is partly environment faults, not supervisor-design faults; deleting the tree does not delete those modes. All eight final positions agree. |
| A4 | Delete overlay daemon server (keep pill visibility) | MODIFY (staged sequence); the deletion AS STATED is REJECTED | The server is real (overlay.py 613 lines, Unix-socket server with holder accounting) and per-batch overlay acquire (315-349ms) is a genuine tax, so the end state (delete the server) is right. But the pill is the owner's only visibility into live runs and both replacements are unbuilt. FRT's REJECT-as-stated is adopted as the characterization of the as-stated form (section 2 item (c)); the staged sequence is what is adopted, and it is identical in substance across all eight positions. Gating conditions, in sequence: (a) session-level pill first, acquire once per task, server KEPT, measured, with the CB-10 precondition (LIQUID flicker probe run, or an explicit owner deferral recorded, before this step is judged; the pill change interacts with flicker status); (b) driver-owned pill (or compositor-plugin indicator) only with proof it shows and clears, including no stale or missing pill when the driver dies mid-task; (c) delete the server only then (B3 lift, section 5). |
| A5 | Delete one-shot SSH loop (persistent Broker only) | MODIFY | Persistent-first is right (fresh SSH 4.667s mean n=10, PROBE-S0 90eb8be; broker 2.37x faster than one-shot on a live batch, PROBE-S1 1af7330). The word "only" is REJECTED: the VM reaches the relay only through SSH, so this is not deletion of SSH but deletion of one-shot SSH in favor of multiplexed SSH plus broker RPC; and if the broker dies, one-shot SSH is how the relay gets restarted (PROBE-S1: the one-shot driver path, 5.375s for a whole batch, is the recovery path). Gating condition: fresh SSH stays as the documented fallback AND the recovery path. "Only" applies to the default path, never to the recovery path (B4 lift, section 5). All eight final positions agree in substance. |
| A6 + D2 | Delete file-based observation/action IPC (A6) / delete scp for JSON files (D2) | ADOPT for transport | JSON over the persistent channel (or in-process calls) replaces scp per step. Strengthened by PROBE-S1 (V-Z3): scp costs 4.57-4.93s EVEN over a live multiplexed master (n=4) and 8.1-9.4s fresh, so S0 multiplexing alone does NOT fix scp; only deleting scp as transport removes the about 4.6s transfer tax. Scope condition, recorded by all eight final positions: files stay as the audit and evidence trail (persisted observation artifacts, JSON plus JPEG, written by the driver); what dies is files as the transport, not files as the record. The JPEG still travels for the human VISION 2 check until the persistent channel carries bytes. Keep file IPC only as the fallback transport when no Broker is reachable. |
| A7 + P4 + D4 | Act-now after-image scope fix (A7) / after-image scope fix, both fields (P4) / delete screen-scope after-capture as produced today (D4) | ADOPT the both-fields shape; the delete-entirely half is REJECTED | Proven defective by construction (first_action.py:656 hardcodes cu.observe_screen for the envelope after-image, overwriting desktop_act's scope-matching after-capture, cu.py:2083-2091). The adopted shape, triple-sourced plus AMEND4 item 12: return BOTH after (scope-matching, chainable) and after_screen (full monitor, verification only, documented non-chainable); move the scope check before the overlay attempt; add a regression test. LANDED: AMEND4 item 12 cbab398 (shape verified from the diff by F2 V-F17). What remains is confirming the four regression tests PASS on the new code (not yet run by anyone) and the Codex-lane confirmation (V-Z2, open). REJECTED part: deleting the envelope after image entirely (ARCH's delete half, and D2's withdrawn alternative). It loses the human-visible evidence and the frame-change signal for a saving of about 0.25s, which is noise; that trade fails the 06:07 criterion on accuracy. The scope-as-capability refusal deletion is NOT part of this row; it lands reframed as snapshot binding with P2 (section 2 item (f)). |
| A8 | Delete pixel-band verification for structured targets | MODIFY, sequenced behind P5 | Direction right: the band is admitted necessary-not-sufficient and the DOM value check is sufficient and 100-1000x cheaper (0.002-0.015s). Gating condition: delete band-as-pass-signal only where the per-action DOM assert exists and is mandatory; until then the band stays as a diagnostic. Deleting before the assert set exists leaves actions with NO verification, which is worse than weak verification. This is RTD's sequencing, accepted by all eight final positions. The P5/A8 change rests on the verified opt-in-hooks ground (focus_check and type_check are still optional hooks, D1 V13), not on RTD's V11 TODO wording (section 2 of the draft, item (f), confirmed by F2 V-F11 and FGROUND). CB-1 folds into this row as the contract shape (section 1.4). |
| A9 | Coordinate model to one system (CSS px element rects, converted once at the driver edge) | ADOPT for structured targets | The five-frame tower has five proven bug sites (F2b-1, C12, amend3 step 5, G28, after-scope trap); the one-conversion path already exists (fastpath.dom_rect_to_screen_point, verified). Dependency satisfied: AMEND4 items 5-6 landed (b44a5ea, origin staleness fixed), item 1 landed (cc964b2, one unit system). The one conversion still needs a correct absolute viewport origin and scale factors re-read per ground (C12 proved window-relative vs absolute origin is a live trap). The pixel fallback keeps its own frame internally; the router decides. All eight final positions agree. CONDITIONAL on the defective-test repair for items 5-6 (b44a5ea records "F2/F3 RT2 tests defective", V-Z9): the wiring is re-verified against P2's target functions before A9 is relied on as proof-grade. |
| A10 | Acceptance test becomes 0-vision live benchmark on real ws2 clone chats | MODIFY (3-rung ladder; live 2-vision diagnostic only) | Final gate: live 0-vision on real ws2 clone chats (clone1 Brave plus clone2 Chrome), DOM harvest, plan, execute, DOM verify, zero screenshots in the machine loop, accuracy at least 90% scored by DOM outcome (V12 sent-bubble gate), total wall time end to end including transport, one final screenshot kept as unscored human evidence (P9), owner approval per run. MODIFY because the acceptance is a 3-rung ladder (section 4), not the single live gate as stated: rung 1 fixture 2-vision (PASSED a1a672d, 10.86s, pending the CB-9 manifest before it is quoted as a gate), rung 2 live 0-vision (final gate for the chat class), rung 3 100-task held-out benchmark (general gate, separate from the live gate, section 2 item (g)). B1 is LIFTED (section 5), with F2's P9 load-bearing condition as a HARD condition on scoring (section 2 item (b)): the final screenshot must be reviewed before a run scores as passed, and any DOM-vs-render mismatch FAILS the run. |

### 1.2 GROUNDING P1-P9 (worker-grounding-review-log.md, d1fc4e9)

| ID | Proposal | Verdict | Evidence, reasoning, and gating conditions |
|----|----------|---------|---------------------------------------------|
| P1 | DOM/a11y default router (Zen Marionette/BiDi, Chromium CDP, AT-SPI, screenshot last; encoded in code, not convention) | ADOPT | Two perception stacks with no routing rule drift to the worse one (works everywhere) instead of the better one (needs setup). Implementation requirements, accepted by all eight final positions: encode the router in code as one function returning the perception source; fail closed to the labeled screenshot fallback; a per-target routing table proven per target before the default flips; a log line on every routing decision, so drift back to screenshots is visible instead of silent. Tightenings adopted (F2 9.3, FGROUND): (T1a) the router routes on COVERAGE, not just target type: a backend returning an empty harvest or a truncated a11y tree (a11y.py truncated flag) falls through to the next backend, never proceeds on a partial inventory; (T1b) Zen chrome UI routes to screenshots, a DECIDED boundary (P8 CLOSED), recorded in the router. Note: the a11y branch is thin for the apps in play (AT-SPI cannot see Zen; AT-SPI numbers unverified on this VM), so it mostly covers native apps that are not the live workload. Interim honest state: Brave tasks still route to screenshots until P3 lands. |
| P2 | Element-ref action interface rewrite (live rect re-read at execution, screen-point action form, delete dom_rect_to_image_point from the live path) | MODIFY | Direction right and highest-leverage code change after P3: the round trip exact DOM rect to exact screen point to lossy image point and back is proven wasteful from source (fastpath.py:195-243, dom_act.py:312, cu.py:1000-1005), and it deletes the F2b-1, C12, amend3-step-5 bug class. Gating conditions (B5, section 5): (a) the stale-ref disagreement protocol is specified first (what happens when a live rect re-read disagrees with the plan: refuse, re-plan, or click stale, per case; lifecycle across a multi-action plan), with FARCH's protocol core adopted (section 2 item (f)) and CB-2's binding folded in (scope plus observation ID mandatory, re-ground first, stop on ambiguity); AND (b) AMEND4 items 2-4 have landed (SATISFIED: c1ea773, 62b740e, 72120aa) AND the defective proof tests for items 3, 4, 5-6 are repaired or re-verified (FRT-B6, V-Z9; section 2 item (d)). P2 starts only when (a) and the repair limb of (b) are met. Content expanded per CB-5 (F2 9.3, FGROUND V-F12 verified from source): live RE-CONFIRM, not just re-read (visible, interactive/enabled, uncovered via hit_check zen_dom.py:820-851, stable via two rect reads agreeing, unique via querySelectorAll count 1 or ref disambiguation); the Zen adapter under the same contract (code_exec.py DOM is Chromium-only, DOM_WINDOW_CLASS='chromium', so the Zen adapter is genuinely missing work); enumerate the live callers of dom_rect_to_image_point before deleting it from the live path; remove unrestricted zen_dom eval from the default agent interface (verified: subparser at zen_dom.py:1153, handled at 1171; internal evaluate() stays as the transport for harvest, locate, and hit_check). Delete dom_rect_to_image_point from the live path (keep for tests and legacy). The scope-as-capability refusal deletion lands reframed as snapshot binding in this step (section 2 item (f)). |
| P3 | Brave relaunch with debugging port (controlled experiment, quiet window, never mid-batch; fallback agent-managed Chromium) | ADOPT as a controlled experiment, CONDITIONAL as a live path | Single highest-leverage unblocker: the clone chats live in Brave, Brave holds no debugging port on its default profile (cdp.mjs comment verified verbatim), so the CDP path cannot reach them today. Conditions, accepted by all eight final positions: quiet window owned by the coordinator, never mid-batch (clone1 is mid-batch-9 now, stalled 48 min, nudged 06:45, V-Z8); verify /json/list shows the Muse tab and login intact; run observe plus harvest plus one fill plus assert on a scratch input. Recorded additions: CDP on port 9223 exposes the logged-in browser to any local process (security consideration); the Chromium fallback is a migration with re-login and clone reconfiguration, not a fallback, and needs its own login-persistence check before it is relied on; cdp.mjs notes shadow-DOM elements have null box_model, and Messenger's DOM shape against that gap is unexamined (PARTIAL outcome defined: if the Messenger composer sits in shadow DOM and CDP returns null box_model for it, P3 narrows to "CDP works except shadow-DOM elements" and P2 carries a shadow-DOM fallback). Gate narrowed per FGROUND C-O2 (adopted, F2 9.6 item 10): P3 gates ONLY the clone-chat live acceptance run (step 11), NOT steps 3-6. If P3 is still NOT-RUN at step 6, the S2 flip class RE-SCOPES to a Zen-reachable task class (C-O3). CONDITIONAL: PROBE-P3 is NOT-RUN (7b1006a, V-Z6); the live-path verdict becomes final only when the experiment passes or fails in a quiet window. If P3 fails (Brave refuses the port and the Chromium migration is too disruptive), the DOM-first live path loses its highest-leverage unlock and the whole program re-plans around Zen Marionette only; report that plainly, not worked around silently. |
| P5 | DOM verification mandatory (focus_check and type_check required, not optional hooks; CDP fill read-back and assert polling the model) | MODIFY | Direction right; the code admits the band is insufficient. The blanket mandate is BLOCKED as stated: the assert set does not exist for every action type (focus_check/type_check are still optional hooks, D1 V13), and no per-action exception list exists. Gating conditions: DOM verification becomes mandatory PER ACTION TYPE as its assert lands; an explicit per-action exception list names the actions where DOM assert is impossible (scroll position, hover state) and pixel stays the only signal; the band stays as a diagnostic until then. A blanket mandate now means false refusals on working flows or vacuous asserts (false confidence). The V12 sent-bubble gate in the benchmark is the pattern. CB-1 folds into this row as the contract shape (three-way result per action: input sent, right target received it, postcondition confirmed; desktop_act's ok becomes input_sent; verified=true only on postcondition), and CB-1 is an additional gate on the S2 flip for the flipped class (F2 9.4 step 6). Preconditions (EX1: unique, visible, enabled, right window, geometry and focus unchanged since grounding) land alongside the postcondition set. The V11 wording settlement stands (arm_typed_flag exists and is called from production code at dom_act.py:433-434 per the draft V-A5, lines moved by AMEND4 edits; the remaining open question is whether the production code-exec path reaches that call for every type action, confirmed by the P5 implementer, not load-bearing). |
| P6 | Measure the vision call | ADOPT, with specification fix | Cheapest item on the list and a precondition for honest speed claims: capture is 15-30ms and DOM rects 0.030s, but the model read that locates the target is seconds and timed nowhere. Bundle with S0. Specification fix, from RTD and accepted by all eight final positions: the model call happens in the calling agent's loop, outside cu.py, so the proposal must specify the timestamp points (observation delivered to the agent vs located target returned) and the owner of the logging (the harness, not cu.py), or it will be recorded as done when only capture timing is logged again. Additions adopted (F2 9.3, FGROUND, CB-7/CB-10 folded into ONE measurement workstream): P6a measure model INFERENCE time separately from vision-call latency; record a first-pointer-action timestamp; measure order-to-overlay from the user command, not from the wrapper start; P6b log the ERROR CLASS per miss (wrong target in the image vs orchestration fed the wrong frame or scope; G30 is class (a), J40 and the after-image trap are class (b)); P6c pin and log the capture parameters with every measurement (observe default 960, act-now 1920, JPEG q90 always). Until that number is in the logs, every speed claim about the screenshot path is incomplete, and nobody may claim the 10s target is met. |
| P7 | Session handover protocol (one protocol per browser per task phase, BiDi ground then Marionette input or stay on one) | MODIFY | The one-session constraint is proven (4 runs, Firefox allows exactly one remote session per instance), so a protocol is needed IF a task genuinely needs two protocols. Gating condition: first answer whether Marionette-only suffices (the benchmark already runs Marionette-only, harvest plus input, and zen_dom harvest IS Marionette). Write the handover protocol only if a task genuinely needs BiDi for grounding plus Marionette for input. Price noted: a handover costs 4-7s per switch (BiDi new 1.51-2.77s fresh, Marionette attach 2.65-4.12s), comparable to the SSH tax being deleted. Small and non-blocking either way. If CB-EXEC's single-owner broker is adopted, P7 dissolves into that design (the broker owns the one session); do not write a standalone protocol and a broker session design for the same slot. Single session owner added (CB 2.6, FGROUND): one owner for pointer, overlay, and the Firefox session, with a serialized queue, no competing BiDi plus Marionette clients. All eight final positions converge on MODIFY. |
| P8 | Zen chrome Marionette context test (set_context chrome) | CLOSED | Premise verified (no chrome-context support in zen_cli.py today), but the probe ANSWERED it: PROBE-P8 (3790901, V-Z6) BLOCKED, HTTP 500, error "unsupported operation", MOZ_REMOTE_ALLOW_SYSTEM_ACCESS required, C12 reproduced live. No chrome DOM is reachable without a Zen restart. The boundary is DECIDED and recorded in P1: screenshots ONLY for Zen chrome UI. The only reopen is an owner-approved Zen restart with MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1, which is a new decision, not probe evidence. No further time on this path. All eight final positions agree (F1, F2, F3, FRT, FARCH, FGROUND; FSPEED and FCODEX do not judge P8). The draft's ADOPT-as-probe is stale and is NOT finalized. |
| P9 | Keep one screenshot for the human (VISION 2 stays, machine scores by DOM) | ADOPT | Correct division: screenshots are a human evidence channel, not a machine perception channel. VISION 2 stays as unscored human evidence; the machine scores by DOM outcome. Wording correction, from RTD and accepted by all eight final positions: VISION 2 is the agent looking at the threads and reporting to the human, not the owner looking directly, so it is the agent's final sanity check reported to the human. Cost is about 0.25s plus one vision read, noise against the total. HARD CONDITION adopted (F2 9.3 A10, section 2 item (b)): the final screenshot must be reviewed before a live run scores as passed, and any DOM-vs-render mismatch FAILS the run. P9 capture parameters pinned (fixed size and compression, FGROUND): the human evidence channel must not vary by path the way machine perception does today. |

### 1.3 SPEED S0-S3 plus six deletions (worker-speed-review-log.md, a4ecb49)

| ID | Proposal | Verdict | Evidence, reasoning, and gating conditions |
|----|----------|---------|---------------------------------------------|
| S0 + D1 | Step 0 persistent SSH multiplexing, do now (S0) / delete fresh SSH per call (D1) | ADOPT on CORRECTED numbers | Fresh SSH mean 4.667s (n=10, PROBE-S0 interim 90eb8be, V-Z4); multiplexed mean 1.339s (n=18 accepted samples). Saving 3.328s per connection, 3.49x, NOT 460x and NOT 0.01s. SPEED's 0.01s figure matches a failed-fast connection (master not up, rc=255, D1's diagnosis, accepted by RTD and D3, re-confirmed by PROBE-S0); SPEED's log records no return codes and no master-liveness check. Corrected expectation: per act-now (3 connects) about 14s becomes about 4s, not about 2s; per observe (2 connects) about 6.7s saved. SPEED's 1.6x per-task estimate was built on 0.01s and must NOT be quoted; D1's revised roughly 1.3-1.4x on a CL2-MSG-class task is the working figure until a recompute on the corrected numbers. HARD REQUIREMENTS for the implementation, all measured (PROBE-S0 V-Z4, PROBE-S1 V-Z3): (a) start the master with setsid/nohup WITHOUT -f (or let ControlMaster=auto create it), never with ssh -M -f -N (refuses sessions, dies in about 1-2 min); (b) ControlMaster=auto on clients so master death self-heals with one slow correct fallback instead of a hard failure; (c) per-use liveness check plus restart-on-death (fresh SSH about 4.5s) as the normal path, not an exception; (d) ServerAliveInterval=15 (kept the PROBE-S1 master alive through the whole broker arm, about 4 min); (e) per-socket watchdog, not global (a half-dead master can hang rather than fail cleanly; ControlPersist=600 can leave a stale master holding a dead Tailscale route); (f) log master death. The 1-day soak test runs IN PARALLEL, advisory, not a gate (a master death falls back to fresh SSH, slow but correct); soak ends about 07:41 +07, section 7. The residual about 1.2-1.3s per session (server-side session setup per new channel, F2 V-F15, answering D1 R2) is itself an argument for S1 and A1. Do it now: no agent-logic code change, fallback safe. All eight final positions agree. |
| S1 + D3 | Step 1 act-now over the persistent relay broker (S1) / delete per-batch session spawn (D3) | ADOPT (proof met); the deletion is gated on the five measured conditions | Direction right: the per-batch session spawn is a real tax plus a real failure mode (20s deadline, timeout never falls back, council 1 B1), and JSON over the same channel kills the scp round trips. PROOF-FIRST IS SATISFIED: PROBE-S1 (1af7330, V-Z3) ran one live batch (observe plus click plus type) end to end over the relay broker from the VM, type visibly landed in the scratch field (PROBE-S1-OK), broker core batch 12.110s vs one-shot core batch 28.700s, delta 16.590s, broker 2.37x faster. The broker's own per-command cost is near zero (round trips equal plain mux SSH; laptop work 0.08-0.26s per command; act 71 plus 109 plus 78ms). The delta is mostly transport, not the spawn (spawn plus act plus teardown about 0.9s inside the 5.375s one-shot invocation). The draft's MODIFY (proof-first) is therefore LIFTED to ADOPT on the proof, as F2's addendum specified ("if the broker arm proves end to end, S1/D3 lift to ADOPT"). THE DELETION of the per-batch spawn is authorized ONLY after all five measured conditions are met: (1) SYNC THE LAPTOP TREE FIRST (laptop HEAD 56f5af4 vs VM HEAD 48c6aee; no act-now on the laptop; laptop cu.py/session_driver.py default the browser endpoint to 9222, so browser observe through the broker 404s and fatally ends the session; run sync-installed.py or equivalent and re-verify browser observe through the broker before any deletion); (2) KEEP fresh-SSH one-shot as fallback AND recovery (the broker dies, the master dies, the socket can go stale; the one-shot driver path at 5.375s per batch is the recovery path and must stay documented); (3) master watchdog with restart-on-death plus the 1-day soak for ServerAliveInterval=15; (4) DECIDE the fatal-on-read-failure behavior (a failed read-only browser observe ended the whole broker session; either make read-only failures non-fatal or keep browser commands out of the broker until the endpoint is fixed); (5) single-owner serialization under concurrent VM workers is still unexamined (the broker is single-task; a second start gets busy; VM-side queueing is not built; do not run two broker batches concurrently until that is decided). Session-level pill (keep the overlay server) lands in the same step, with the CB-10 precondition from A4. Socket correction recorded: the relay socket is /run/user/1000/computer-use-wayland/relay.sock, not cursor-guard.sock (V-Z3). CB-6 folds into this row (section 1.4). |
| S2 + D5 | Step 2 DOM-first plus code-exec plus checkpoint verification, CU_CODE_EXEC=1 on (S2) / delete per-action model call as the default (D5) | MODIFY, gated | The 10x path, already built and merged (code_exec.py 880 lines, Pick 1 winner, commits 714e4f9, 84b88bb, 2e2aeff, merge 453adc4), and the flag is OFF in the live path (verified live: CU_CODE_EXEC unset on the laptop). But the blanket flip is BLOCKED (B2, section 5). Gating conditions, in order: (a) run the fixture 2-vision bench green: MET (a1a672d, 10.86s, V-Z5); (b) fix the 3 Y1b real fails (1e, 2a, 2b): STILL OPEN at the 06:37 +07 check in PROBE-S2 (V-Z5); (c) CB-1 as an additional gate (F2 9.4 step 6, FCODEX): the verified/input_sent split lands for the flipped class BEFORE the flip, judged by postcondition pass rate, not envelope ok rate; (d) the numerical plateau is defined FIRST (HARD GATE, section 2 item (e), FRT-B7 adopted); (e) flip the flag for ONE live task class (clone chat sends, or a Zen-reachable class if P3 is still NOT-RUN, C-O3) with act-now as fallback, measure, then expand. A fixture bench pass alone does not fix the 3 real fails. The "10x path" label is corrected to 3-5x on unmeasured model inference time (SPEED's own honest limit: 30-60s if vision reading dominates); the mechanism can be about 1s, the model is the remaining unknown, and P6 must measure it before anyone claims the 10s target. CB-4's batch-validity rule applies to code-exec programs (re-validate per risky step). Code-exec becomes the default for the proven task class first; the stepwise loop stays the fallback for unknown shapes only. |
| S3 | Step 3 laptop-side task runner, only if Step 2 plateaus | MODIFY, fold into A1/CB-EXEC | S3 substantially overlaps A1: a laptop-side runner that grounds, acts, and verifies locally and streams back compact state IS the A1 driver daemon approached from the other side, and CB-EXEC is the same destination with the semantic contract. One design decision, not three builds; do not build a separate runner alongside A1/CB-EXEC. Gating condition: the plateau criterion must be defined NUMERICALLY BEFORE the S2 flip (HARD GATE, section 2 item (e)), so the trigger is not argued later. An undefined plateau either never triggers or triggers on one bad run. The decision itself happens only after steps 0-8 of section 3 are measured. All eight final positions agree on the merge. |
| D6 | Delete 120s freshness window as a gate on DOM work | MODIFY, scoped | For DOM-grounded work, re-read the DOM (0.030s) instead of refusing for staleness; the window is a patch for vision coordinates, not a law. Correction, from RTD and accepted by all eight final positions: the refusal at cu.py:773 also guards against future-clock observations, and a blanket delete removes the clock-skew guard. Gating condition: keep the future-clock refusal, drop only the age refusal for DOM paths. Keep the window for pixel-addressed work, where staleness is real and the refusal protects against acting on a dead frame. |

### 1.4 CODEX-BREAKTHROUGH CB-1..CB-10 + CB-EXEC (codex-breakthrough-report.md, 2596287, 138 lines, Vietnamese)

Cross-examination note: D1, D2, D3, RTD and all four cross-responses
(X1, X2, X3, XRT) predate the Codex report and mark CB PENDING, so no
council reviewer cross-examined CB-1..CB-EXEC before the final round.
F1, F2, F3, and FRT are the first cross-examination. FCODEX holds the
Codex position; it is not an independent cross-examiner. Section 8
records, per CB row, where the verdict survives, weakens, or falls under
this cross-examination.

| ID | Proposal | Verdict | Evidence, reasoning, and gating conditions |
|----|----------|---------|---------------------------------------------|
| CB-1 | Three-part result contract (input_sent / verified=true only with postcondition) | MODIFY, merge into P5/A8 | The failure mode is proven: G30 (click into empty space reported ok) and FRT V-F2 (envelope ok=True on session ok with no postcondition anywhere in the path; first_action.py:552-563 propagates session ok into envelope ok, and the comment at line 550 even cites "Council 1, A3: the exit code alone never proves success", then propagates session ok anyway). The contract is the right shape: split input sent, correct target received input, and post-state confirmed. BLOCKED as a standalone contract for two reasons (FRT, adopted): first, the rename breaks callers unless migrated in the same commit (envelope ok disappears or is misread downstream); second, "verified=true only with postcondition" presumes postconditions exist for every action, and for scroll, hover, and focus-only moves there is no cheap postcondition, so the contract needs the SAME per-action exception list as P5, or it mandates false refusals or vacuous postconditions. Gate: fold CB-1 into P5/A8 as the contract for DOM-verifiable actions, with the exception list, and migrate the envelope logic in the same commit. CB-1 is an ADDITIONAL gate on the S2 flip for the flipped class (F2 9.4, FCODEX): the split lands before the flip, judged by postcondition pass rate, not envelope ok rate. The 167/199 ok=true rate in Codex's JSONL aggregate (p50 order-to-overlay 337.5ms, max 368.4ms, p50 wrapper 2.288s, max 6.95s, 195 session, 4 fallback, 0 timeout, 5 source=captured) is NOT a success rate (FRT V-F8): 167 ok=true with no postcondition data anywhere in the log, and G30 proves false ok exists in this exact population. Nobody may quote 167/199 as a success rate. |
| CB-2 | Scope mandatory in action data, scope change stops the batch | MODIFY; blanket stop REJECTED | The defect class is real: J40 (window-scope point used on a full-screen image, miss about (+45,+12) px, command still returned ok) and the _fresh_observation substitution path (missing/stale/old observation replaced by a full-screen capture while the action list is passed through unchanged, no frame conversion, no stop). Scope must be a mandatory part of action data. The PRESCRIPTION overcorrects (FRT, adopted): a blanket stop on every scope change throws away cheap recovery. A DOM re-read costs 0.030s; when the target is unambiguous after re-grounding, re-ground-and-continue is strictly better than stopping the batch, on both accuracy and speed. DECIDED RULE (reconciling FRT, FGROUND, FARCH, section 2 item (f)): scope plus observation ID is mandatory in action data; a scope change triggers re-grounding first; stop only on ambiguity or a scope change re-grounding cannot resolve. Limb 1 (after-image scope) is CLOSED by AMEND4 item 12 (cbab398); limb 2 (silent substitution of a screen capture for a rejected window observation) is CLOSED in the repo copy by the G28 loud refusal (F2 V-F11: first_action.py:478-498 returns 1 with path='refused' before any session attempt, naming the given observation, its age, and why it was rejected, for EVERY batch including pointer-only batches; docstring lines 328-350 states the same rule). What remains of CB-2 as new work is the planned-action rule: actions planned on a window observation and executed after a screen observation arrived. That rule lands with P2 as part of the stale-ref protocol (one protocol, not two). |
| CB-3 | Vision error taxonomy + image uniformity + J37 codec false refusal | MODIFY (uniformity ADOPT, J37 fix ADOPT, taxonomy gated on P6) | Three parts, three verdicts (FRT, adopted over the four ADOPTs, which ignore the taxonomy-without-numbers problem). (a) Image uniformity: ADOPT. Verified from source (FRT V-F7): observe defaults to max_width=960 (cu.py:920/974) while act-now captures at 1920 (first_action.py:353/661), so the model's input resolution and detail change by path. One max_width for all captures. Condition: re-run an E2-style calibration after the change, because the model's input distribution changes and the old 58.6% number no longer applies. (b) J37 codec false refusal: ADOPT the fix. The preflight compares a decoded JPEG against a fresh uncompressed capture with a patch threshold of 6 (cu.py:1015, verified); J37's patch diff of 6.627 tripped it. A codec artifact is not a screen change; separate the two or the refusal stays flaky. (c) Vision error taxonomy: MODIFY. A taxonomy is classification, not a fix; without P6's measurement it is paperwork with no numbers to classify. Gate: taxonomy is populated from P6-measured vision calls, not written from the armchair. The Wilson interval (40.7-74.5%) widens the uncertainty on every vision-dependent claim; vision could be as bad as 40.7% first-try, which strengthens A2/P1 but also means no vision-dependent number in this round is tight. |
| CB-4 | Batch growth by proven validity (90% per-click math: 20 clicks 12.2%, 32 clicks 3.4%) | MODIFY, fold into P5/CB-EXEC postconditions; math must not be quoted as measured | The arithmetic is correct (FRT V-F7: 0.9^20 = 12.2%, 0.9^32 = 3.4%) and the conclusion is right: 90% per-click does not mean 90% task success, and a batch should grow only when the executor proves the next steps are still valid, not because coordinates can be stuffed into one image. But the math ASSUMES independent errors, and Codex itself says it is only an illustration. Real errors correlate through the shared frame: one wrong frame poisons every coordinate taken from it, so the true all-correct rate is likely WORSE than 12.2% when the frame is wrong. Do not quote 12.2%/3.4% as measured rates; no measured per-click rate on held-out tasks exists, and the 90% figure is hypothetical. As a standalone proposal CB-4 duplicates P5's assert set and CB-EXEC's postconditions; fold its rule (grow the batch only on proven validity) into the P5 assert set and the CB-EXEC prototype's postcondition design. BLOCK using CB-4's math as a gate threshold. |
| CB-5 | Common executor routing + Zen adapter + locate confirms visible/interactive/uncovered/stable/unique + remove unrestricted zen_dom eval from default interface + AT-SPI coverage reporting | MODIFY; routing half merged into the single build, eval removal ADOPTED now | Split verdict (FRT, adopted; F2's content-ADOPT folded into the same merge). (a) Remove unrestricted zen_dom eval from the default agent interface: ADOPT, with a debug-mode carve-out. The capability exists (evaluate() at zen_dom.py:441 per FRT V-F7; subparser at 1153, handled at 1171 per F2 V-F12): arbitrary JavaScript in the current tab as a default primitive is a correctness and safety hole (it can silently rewrite the page the agent is supposed to read). Keep it in an intentional debug mode only, as Codex itself concedes. Lands in step 0 (cheap, no dependency). (b) Locate confirmations (visible, interactive, uncovered, stable, unique): ADOPTED as requirements, with definitions owed. "Stable" and "unique" are unmeasurable as stated (stable for how long? unique by selector or by visible set?). They become acceptance criteria only with operational definitions, and they land as P2's re-confirm content (F2 9.3, FGROUND V-F12 verified: locate() at zen_dom.py:567-588 returns getBoundingClientRect only, no visibility/interactive/uncovered/stability/uniqueness check; hit_check() at 820-851 exists). (c) AT-SPI coverage reporting: ADOPT. The a11y tree is partial by design (500 nodes or 2s cap, max 80 items, truncated flag, a11y.py:83-104); a backend that silently returns a partial tree is a false-confidence source. Report coverage, then fall through to DOM or image when the tree is insufficient. (d) Common executor routing: BLOCKED as a standalone build. It IS CB-EXEC's routing layer; do not build routing twice (once in CB-5, once in CB-EXEC). Fold into the single merged build. F3's ADOPT would authorize a separate routing build alongside CB-EXEC; FRT and F2 are right that this duplicates. |
| CB-6 | act-now uses the long-lived session driver, one owner, sequential queue | ADOPT, merged into S1 | This duplicates S1 exactly except for "sequential queue": act-now today spawns a session per call (first_action.py attempt_session, verified), the Broker and session driver already exist, and the fix is to route act-now through the session driver with one owner. PROOF-FIRST IS SATISFIED by PROBE-S1 (1af7330, V-Z3): the broker path works from the VM, 2.37x faster on a live batch. The new content is the queue, and its discipline must be specified before the merge lands (FRT, adopted): what happens to the second queued batch (wait? refuse? timeout?), and how does a sequential queue behave under concurrent VM workers (the same single-owner socket question PROBE-S1 leaves unexamined, condition 5). Gate: fold CB-6 into S1; the queue discipline is specified in the S1 deletion step (section 3 step 8), not as a further proof gate. BLOCK CB-6 as a separate track. |
| CB-7 | Latency measurement fixes + measure VM-to-laptop dispatch separately | ADOPT | The strongest measurement item in the Codex report, and the one place Codex corrects the record. Its methodological point is real: the act-now JSONL starts after the command reaches the laptop, so it cannot support a dispatch share. CORRECTION adopted (section 2 item (h)): the 11.620s dispatch IS measured (F2b log lines 34-35, D1 V10, F2 V-F13: "ORDER-TO-OVERLAY = 12.262s. Breakdown: dispatch 11.620s (T_order to T_LAPTOP_START: scp script + SSH connect + shell startup), fresh observe 0.233s, Python startup 0.060s, overlay acquire 0.349s"); only the SSH-alone attribution is inference. CB 2.7's "no record supports 11.6s of 12.26s is SSH dispatch" is WRONG in the broad form. The "SSH is 95 percent" slogan dies; the dispatch figure does not. What CB-7 does NOT do: it does not kill the SSH tax. SPEED's fresh-SSH measurements (4.43-5.29s, 7 samples, four-way confirmed; PROBE-S0 fresh mean 4.667s n=10) are independent of the laptop JSONL. Adopted: redefine order_to_overlay from the user command on the VM (not from Python wrapper start); fix target_breached to compare first-pointer-action time against the 30s threshold, not whole-batch time; measure VM-to-laptop dispatch separately per phase (VM send, SSH connect, laptop work, return). Fold into P6 as ONE measurement workstream, not a second one. |
| CB-8 | Evidence discipline (DONE is a state of specific evidence) | ADOPT as a standing rule, scoped | Correct and overdue: the todolist marks items DONE for "direction determined" or "fixture proven", which is not the same as proven on a real app (Codex 2.8: 13/13 on a fixture cannot become a 90% commitment on another app; held-out new app is PARTIAL; J10 real think-time is OPEN). Its teeth: any proposal whose DONE basis is a fixture-only proof gets its DONE revoked until live evidence exists. SCOPE, to keep it from becoming an unbounded audit (FRT, adopted): apply it only to the DONE items that gate this final direction (S2's Pick 1 DONE, the bench DONE, the DOM-grounding DONE claims), not a full-history re-audit. CB-8 has no build and no measurement; it must not consume a build slot or delay the order of work. It is a rule the finalizer enforces when judging gates, and it is the ground for the B5 defective-test repair condition (section 2 item (d)). All eight final positions that judge it agree. |
| CB-9 | Deployment manifest (lock source commit + installed artifact + log) | ADOPT, ranked below accuracy/speed work | Cheap and obviously right. The drift is real and CONFIRMED LIVE (section 2 item (i)): FCODEX V-F7 and FGROUND V-F10 verified by a read-only SSH call at 06:40 +07 that installed first_action.py is 23442 bytes and DIFFERS from the repo copy (33893 bytes); installed cu.py also DIFFERS; laptop HEAD 3790901 at that check. The file-presence limb is STALE (first_action.py IS tracked on todolist-push now); the divergence limb is confirmed. The manifest is a PRECONDITION for the acceptance ladder (section 4): no rung scores without a manifest for the exact build under test, and the fixture bench pass (a1a672d) must not be quoted as a gate until its manifest is locked. Rank: under the 06:07 criterion it changes auditability, not the accuracy or speed of the final result, so it lands in step 0 as a habit of the deploy step, not as a separate audit project. It must be produced by the deploy step itself. All eight final positions that judge it agree. |
| CB-10 | Overlay flicker vs think-time separate, per-phase measurements | MODIFY, fold into P6/CB-7 | The separation is right: the todolist records 0 repaint and 0 event for overlay idle, but the LIQUID background test never ran because the plugin was not loaded, so there is no evidence the original flicker was reproduced or fixed; and think-time (J10, H2) is OPEN and unmeasured by act-now. Two problems as a standalone track (FRT, adopted). First, it duplicates P6/CB-7 measurement work; fold it into the ONE measurement workstream. Second, the flicker itself is unproven on the current build (plugin not loaded means the flicker may not even exist now). Gate: first establish the flicker reproduces on the current build; if it does not reproduce, CB-10 dissolves. Do not measure the phases of a phenomenon that may not exist. ADDITIONAL GATE adopted (F2 9.3): the LIQUID flicker probe (load the plugin, reproduce the flicker, count repaints) or an explicit recorded owner deferral PRECEDES the A4 session-level pill judgment, because the pill change interacts with flicker status. |
| CB-EXEC | The semantic transaction executor itself (semantic targets, preconditions, real mouse/keyboard, postconditions, retry only when surely unsent; one local broker; DOM/BiDi + AT-SPI + screenshot-crop backends under one contract; vision as fallback; 100 held-out tasks benchmark, 90% defined as task success, about 96/100 for 95% confidence) | MODIFY to prototype-only; the full build as stated is REJECTED | This is the biggest build in the round (2-3 day Zen prototype, 1-2 weeks to merge, plus days of benchmark) and the least proven. FRT's six findings stand (adopted, section 8): (1) No existence proof whatsoever: zero lines built, zero measurements. It fails RTD's C2 harder than A1 does: A1 at least has parts that individually run (code_exec, session_driver, Broker); CB-EXEC's semantic transaction executor with preconditions, postconditions, and retry-only-when-surely-unsent exists in no form at all. Under the 06:07 criterion a 1-2 week build cannot be authorized on zero running evidence when the much smaller S2 flip is BLOCKED on 3 known fails. (2) Single-session-slot risk, concentrated: Zen allows exactly one remote session per instance (proven in 4 runs). CB-EXEC's "one local broker, one owner" concentrates ALL execution through one session holder; a hung session blocks every client, and Codex names this risk itself without specifying recovery. The prototype must specify and prove the wedged-session recovery protocol (who kills a wedged session, on what timeout, with what watchdog). (3) Retry-only-when-surely-unsent is circular: it assumes the delivery knowledge it exists to provide. For a click that may have submitted a form, "surely unsent" is unknowable from DOM alone if the page navigated. The safe default (never retry a possibly-sent action) means real failures become unrecoverable without model intervention, which pushes model calls back up, the opposite of the speed goal. The prototype must prove the retry rule on a destructive-action test (no double-send on retry). (4) The 100-task benchmark is disproportionate as a design gate: 100 held-out tasks across browser and desktop apps, authored by one person, run across 4 variants with interleaved ordering, is 400 task runs plus days of task authoring, to inform a decision the A10 ladder already answers at 90%. The Wilson math is correct (96/100 gives a lower bound of about 90.2%, FRT V-F7) but its independence assumption does not hold: 100 tasks authored by one person on a handful of apps are NOT independent samples (shared app quirks correlate), so the 95% confidence claim is statistically decorative. The 100-task run is a RELEASE gate after the merge decision, if ever, not a design gate (FRT-B1, F2 9.3). (5) It absorbs A1/S3/P2/P5/S1/CB-1/CB-2/CB-5/CB-6. Adopting it as stated makes the staged order incoherent: there is no point flipping CU_CODE_EXEC=1 for one task class and rewriting P2's interface if both are about to be replaced by a new executor. ONE build, ONE design spec, ONE prototype (section 2 item (a)). (6) The schedule (2-3 days prototype, 1-2 weeks merge) is an estimate with no prototype behind it; under 06:07 cost is irrelevant, but an unproven estimate is not evidence. PROTOTYPE GATE (the MODIFY): authorize ONLY the 2-3 day Zen prototype (semantic targets, real mouse, preconditions, postconditions) on a handful of held-out tasks, proven on live tasks, with CB's own metric list (first-try target accuracy, end-to-end task success, wrong side effects, recovery actions, per-phase p50/p90, model calls, retry count, postcondition accuracy, false successes). THEN decide merge vs A1, on measured evidence. If the prototype fails or stalls, CB-EXEC dies and A1/S3 remains the destination. F3's ADOPT-as-design-spec is adopted ONLY in the limited sense that CB-EXEC IS the design spec for the merged prototype (the contract written at step 2); the full build is not adopted. Real-input default adopted (FARCH actuation concession, FGROUND, F2 9.2): real Pointer/keyboard input is the DEFAULT at DOM-located coordinates; DOM .click() only where equivalence is proven per control type. |

## 2. RECONCILIATION OF THE DISSENT MAP (decided with evidence, not averaged)

(a) FRT vs the other seven on CB-EXEC (prototype-only vs design spec /
contract). DECIDED: MODIFY to prototype-only (section 1.4 CB-EXEC row).
FRT's REJECT-as-stated is adopted as the characterization of the full
build; F3's ADOPT-as-design-spec is adopted only in the limited sense
that CB-EXEC IS the design spec for the merged prototype (the contract
written at step 2). F1 and F2 (MODIFY, fold A1/S3 into CB-EXEC) agree
with the prototype-only substance. The evidence decides it: zero lines
built, zero measurements, and the single-session-slot concentration risk
with no specified recovery (FRT findings 1-2). A 1-2 week build cannot
be authorized on zero running evidence while the much smaller S2 flip
is BLOCKED on 3 known fails. The 100-task benchmark is not authorized
before the prototype proves; it is a release gate after the merge
decision, if ever.

(b) B1 lift: FRT reverses it (live 2-vision required, P9 screenshot read
by the same fallible vision) vs draft / XRT / F1 / FARCH / F2
diagnostic-only, with F2's P9 load-bearing condition. DECIDED: B1 lift
STANDS; live 2-vision stays diagnostic only; F2's P9 load-bearing
condition is adopted as a HARD condition on scoring a live run as
passed. FRT's substantive point is real: the P9 screenshot is read by
the same fallible vision (58.6% first-try, Wilson 40.7-74.5%) it is
supposed to check, while the live-thread look is a direct human check
of the rendered outcome. But the rung it demands does not add a
distinct machine proof: in the bench design VISION 1 is a DOM harvest,
not a screenshot, and VISION 2 is a human look at the threads; the
machine never locates from pixels in either form, a point X1/X2/X3
concede even while keeping the rung. Live 2-vision and live 0-vision
with P9 are the same machine behavior; they differ only in whether the
human looks at live threads or at a screenshot, and the P9 screenshot
of the right thread shows the bubble present or absent, while a bubble
in the wrong thread shows absent in the right thread's screenshot
(F3 2a). The councils' stated purpose for the rung ("the live 2-vision
run is the proof that DOM works on real Messenger pages") is served
equally by the live 0-vision run itself, which also runs DOM on real
Messenger pages and scores by DOM outcome. The extra run buys
replication and localization, not a distinct proof, and it costs a
second live run on real clone chats (disruption, coordination, owner
approval) for that replication. Under the 06:07 criterion a gate must
protect accuracy or speed measurably; this rung protects neither beyond
what the 0-vision run plus P9 already protects. The diagnostic
retention supplies the localization value without making it a gate.
FRT is right, however, that a vision-read P9 cannot be a rubber stamp:
hence the load-bearing condition, which is the part of FRT's position
that survives. CONDITION (hard): the final screenshot must be reviewed
before a run scores as passed; any DOM-vs-render mismatch FAILS the
run.

(c) A4 deletion: FRT rejects (restores RTD's original REJECT) vs draft
MODIFY. DECIDED: MODIFY (staged sequence), with FRT's REJECT-as-stated
adopted as the characterization of the as-stated form (section 1.1 A4
row). The substance is identical across all eight positions: nobody
defends deleting the server with unbuilt replacements. The draft's
MODIFY label and FRT's REJECT label describe the same sequence
(session-level pill first with the server kept, then driver-owned pill
crash proof, then delete). FRT is right that relabeling a rejection as
a conditional adopt smuggles the deletion past the final decision; the
record therefore states both plainly: as stated REJECTED, as staged
ADOPTED.

(d) B5: FRT says NOT lifted (items 3, 4, 5-6 landed with defective proof
tests noted in their own commit messages) vs draft / F1 / F3 narrowed
to the protocol limb only. DECIDED: B5 STANDS, narrowed, with FRT's
repair condition ADDED. FRT's evidence is real and verified by me
(V-Z9): 62b740e records "F4 RT2 test defective", 72120aa records "F5
behavior test defective", b44a5ea records "F2/F3 RT2 tests defective".
Under CB-8, landing with a defective proof test is not proof-grade
landing; the draft/F1/F3 position that landing in form satisfies the
limb is wrong on that ground. LIFT CONDITION (two limbs): (i) the
stale-ref disagreement protocol is specified (refuse, re-plan, or
click stale, per case, plus the lifecycle across a multi-action plan,
with FARCH's protocol core and CB-2's binding folded in); AND (ii) the
defective proof tests for AMEND4 items 3, 4, 5-6 are repaired or
re-verified by the round-3 council. P2 starts only when both limbs are
met.

(e) Plateau: FRT makes it a HARD GATE on the S2 flip vs draft's open
condition. DECIDED: HARD GATE (FRT-B7 adopted). Until the numbers
exist, the flip is not authorized. The draft's "open condition with a
deadline" leaves the flip authorizable on a promise; the owner rules
(06:32 feasibility, 06:34 evidence) support the hard gate. The
coordinator defines the numbers from the fixture bench baseline
(10.86s, a1a672d) plus first live runs before the flip; the form is
RTD's (Step 2 live median wall time above a stated threshold for a
stated number of runs after the flag flip), the coordinator is the
decision owner. This does not stall the program: steps 0-5 proceed;
only the flip waits.

(f) FARCH's scope-refusal overturn vs F2's V-F11 refutation (live silent
substitution refuted) vs FGROUND's reconciliation (delete the legality
refusal with P2, keep the halt on scope change, enforced by the G28
refusal plus CB-2 binding). DECIDED: FGROUND's reconciliation, as
adopted by F2 (9.6 item 11). FARCH's overturn is NOT adopted as stated,
because its premise is refuted by F2 V-F11: the G28 loud refusal IS
enforced in the repo copy (first_action.py:478-498 returns 1 with
path='refused' before any session attempt and before any action runs,
naming the given observation, its age, and why it was rejected, for
EVERY batch including pointer-only batches; docstring lines 328-350
states the same rule). FGROUND cited the installed copy
(first_action.py:289-315), not the repo copy. FARCH's substance is
adopted through the binding form: the check must exist in binding
form, never simply vanish. DECIDED RULE: DELETE with P2 the legality
refusal (the refusal to act on a correctly-addressed action because
the OBSERVATION's scope is screen); KEEP the halt on a scope CHANGE
mid-batch, enforced by the G28 loud refusal for the given-observation
case and by CB-2 binding for the planned-action case. One is a legality
gate on a good action; the other is a halt on a changed world. The
remaining gap beyond both limbs is the planned-action case, covered by
CB-2 binding (section 1.4 CB-2 row).

(g) Ladder shape: F1's 3-rung ladder (fixture 2-vision, live 0-vision,
100-task held-out) vs F3's ladder (rung 2 is the 100-task benchmark,
final gate live 0-vision) vs FARCH's fold (96/100 bar folded into the
live gate itself) vs F2's separate live gate and 100-task bar. DECIDED:
F1's rung order with F2's separation. Rung 1 fixture 2-vision (PASSED,
a1a672d, pending manifest). Rung 2 live 0-vision (final gate for the
chat class, 90% task success, DOM-scored, per-phase timing split, P9
load-bearing condition). Rung 3 100-task held-out benchmark (general
gate, REQUIRED before any generality claim, but NOT a precondition for
the live gate and NOT folded into it). FARCH's fold is rejected: the
100-task set does not exist yet (Codex: a few days to build,
uncommitted estimate); folding an unbuilt benchmark into the live gate
would block the live proof on a build (F2). F3's order (100-task before
live) is rejected for the same reason: it delays the live proof on the
same unbuilt set. The live gate answers the chat class; rung 3 answers
generality. Both are required; the sequence is live first, then
general. FCODEX agrees the 100-task set SUPPLEMENTS the ladder, it
does not replace it.

(h) The CB-7 correction (F2b 11.620s dispatch IS measured, only the
SSH-alone attribution is inference; FGROUND and F1 agree, CB 2.7
overstates). DECIDED: adopted (section 1.4 CB-7 row). The 11.620s
dispatch IS measured (F2b log lines 34-35, D1 V10, F2 V-F13). CB 2.7's
"no record supports 11.6s of 12.26s is SSH dispatch" is WRONG in the
broad form. The "SSH is 95 percent" slogan dies; the dispatch figure
does not. S0's arithmetic survives on direct fresh-SSH probes (PROBE-S0
fresh mean 4.667s n=10, mux 1.339s n=18).

(i) The CB-9 manifest precondition (drift confirmed live: installed
first_action.py 23442 bytes vs repo 33893 bytes; installed cu.py also
differs). DECIDED: adopted (section 1.4 CB-9 row). The manifest is a
PRECONDITION before any acceptance rung scores, and the fixture bench
pass (a1a672d) must not be quoted as a gate until its manifest is
locked. The file-presence limb of CB-9 is STALE (first_action.py IS
tracked on todolist-push now); the divergence limb is confirmed live
by FCODEX V-F7 and FGROUND V-F10 (read-only SSH call 06:40 +07).

## 3. ORDER OF WORK (numbered, gated, with the gate evidence for each step)

Every step is independently verifiable, every step lands a measured win
before the next step starts, and no step depends on a bet (P3, DOMZEN,
S2 measurement) that has not yet paid off. Cost is irrelevant by the
criterion, but sequencing by dependency is not cost, it is correctness:
a daemon built from unproven parts inherits their failure modes.

0. S0 plus P6 plus CB-7 plus CB-3(a)(b) plus CB-5 eval removal plus CB-9
   manifest habit, now. Persistent SSH multiplexing with the six hard
   requirements from the S0 row (setsid/nohup master, ControlMaster=auto,
   per-use liveness plus restart-on-death, ServerAliveInterval=15,
   per-socket watchdog, master-death logging); P6 vision-call
   measurement with the timestamp points and harness owner specified,
   plus P6a/P6b/P6c and the CB-7 fixes (first-pointer timestamp,
   target_breached fixed, VM-to-laptop dispatch measured separately);
   CB-3 image uniformity (one max_width) plus J37 codec separation;
   remove unrestricted zen_dom eval from the default agent interface
   (debug mode only); CB-9 manifest produced by the deploy step from
   now on. Gate to step 1: fallback explicit and watchdog in place.
   The 1-day soak test runs IN PARALLEL, advisory, not a gate (a master
   death falls back to fresh SSH, slow but correct); soak ends about
   07:41 +07. Owner of each open condition: section 7.
1. AMEND4 close-out. All 12 items are landed (V-Z1). Remaining work:
   (a) run the four item-12 regression tests and record PASS on the new
   code (cbab398; F2 verified the shape from the diff only); (b)
   confirm the Codex-lane item-12 delivery or re-commission it (V-Z2,
   open; do not assume it done); (c) round-3 council: patch-vs-rewrite
   judgment per item under the 06:07 criterion, and repair or re-verify
   the defective proof tests for items 3, 4, 5-6 (B5 lift limb (ii),
   section 2 item (d)). Kill rule at reconciliation: items the rewrite
   deletes get killed; an item the rewrite subsumes is verified against
   the new code, not assumed gone. The two tracks run in sequence per
   item on shared files, not in parallel on the same functions.
2. Contract written (Layer 0 plus CB-EXEC merged spec) in parallel with
   AMEND4 close-out, no code deleted: snapshot/execute/verify, the CB-1
   three-part result contract, snapshot-bound refs, per-step
   preconditions, serialized queue, task lock, pill ownership,
   crash/stale/sleep lifecycle, allowlisted API with no arbitrary eval,
   the stale-ref protocol core (FARCH), and the wedged-session recovery
   protocol (FRT-B1). Purpose: stops P2/S1/P5 from inventing three
   ad-hoc interfaces. P3 Brave relaunch experiment attempted at the
   first real quiet window between clone batches, coordinator-owned,
   never mid-batch (clone1 batch 9 open, stalled 48 min, nudged 06:45,
   V-Z8). P8 boundary recorded (CLOSED, screenshots ONLY for Zen chrome
   UI). Gate: contract written; P3 gates ONLY the step 11 live
   acceptance run, not steps 3-6.
3. Fixture 2-vision bench: DONE. Bench PASSED (a1a672d, 10.86s,
   visions_used 2, both sends V12 gated, V-Z5). The runtime is installed
   on the VM. Pending: the CB-9 manifest for that build is locked before
   the pass is quoted as a gate. No further work in this step except the
   manifest.
4. Fix the 3 Y1b real fails on code-exec (1e chr NameError; 2a codemode
   wall preemption absent, elapsed 7.20s; 2b code_exec wall preemption
   absent, elapsed 6.20s, ok=True with NO error, silent success).
   Gate to step 6: the fails are fixed (B2 lift, part 1). Owner:
   section 7. This is the first worker commission (section 6).
5. P1 router plus P5 asserts per action type FOR THE S2 TASK CLASS
   (clone chat sends), plus CB-1 contract for the class, plus CB-5
   locate confirmations and eval removal (if not done in step 0).
   Rewiring of existing hooks; P5 per action type as its assert lands,
   plus the explicit exception list. Gate to step 6: the router logs its
   routing decisions, and the P5 assert set covers the S2 task class.
   Why this step precedes the flip: S2 IS "DOM-first plus code-exec
   plus checkpoint verification", and the checkpoint verification part
   IS P5; flipping S2 without P5 means flipping code-exec while DOM
   verification is still optional hooks, a window in which the live loop
   runs code-exec with pixel-band verification only.
6. Define the numerical plateau (coordinator, HARD GATE, section 2 item
   (e)), then the S2 flip for ONE live task class with act-now as
   fallback. CB-1 is an additional gate (the split lands before the
   flip, judged by postcondition pass rate). If P3 is still NOT-RUN,
   RE-SCOPE the flip class to a Zen-reachable task class (Marionette
   path, no Brave needed, C-O3); the flip still measures the same thing
   (DOM-first plus code-exec plus checkpoint verification, one class,
   act-now fallback), only the venue changes. Measure model-call count
   and wall time. Gate to expansion: measured on one class; expand only
   on measurement.
7. P2 element-ref interface rewrite, after B5 lifts (stale-ref protocol
   specified AND defective proof tests for items 3, 4, 5-6 repaired or
   re-verified). A9 one-system coordinates land in this step. The scope
   refusal is REFRAMED as snapshot binding in this step, not deleted
   (section 2 item (f)). CB-2 scope-in-action-data lands in this step.
   Gate to step 8: P2 proven on the S2 task class with DOM verification
   mandatory.
8. S1/CB-6 deletion step. The broker proof is DONE (1af7330, V-Z3).
   Now, in order: (a) sync the laptop tree (laptop HEAD 56f5af4 vs VM
   HEAD 48c6aee) and re-verify browser observe through the broker
   (the 9222 endpoint must be fixed or the broker must be told 9223);
   (b) decide the fatal-on-read-failure behavior (make read-only
   failures non-fatal, or keep browser commands out of the broker until
   the endpoint is fixed); (c) specify the queue discipline
   (wait/refuse/timeout for the second queued batch) and the
   single-owner serialization under concurrent VM workers; (d) delete
   the per-batch spawn, keeping one-shot SSH as fallback and recovery.
   Session-level pill (server kept) in the same step, with the CB-10
   precondition (LIQUID flicker probe run, or an explicit owner
   deferral recorded, before the pill judgment). P7's Marionette-only
   question is answered before any handover protocol is written. Gate
   to step 9: one live batch proven end to end over the broker from the
   VM (DONE, 1af7330) AND conditions (a)-(c) met AND the spawn deleted
   with the fallback documented.
9. A1/S3/CB-EXEC merged prototype: the semantic transaction executor
   per the step-2 contract (semantic target, preconditions, real input,
   postcondition, retry only when surely unsent, one local broker,
   backends under one contract, vision fallback). Gate to step 10:
   prototype proven snapshot/execute/verify end to end on one live ws2
   clone chat plus held-out tasks (B6 lift), with the wedged-session
   recovery protocol specified and proven, and a destructive-action
   test proving no double-send on retry. If the prototype fails or
   stalls, CB-EXEC dies and A1/S3 remains the destination.
10. A3/A4/A5 deletions last, each gated on its replacement proving (A3:
    driver holds scope plus cancel latch plus lock; A4: session-level
    pill measured, then driver-owned pill crash proof, then delete the
    server; A5: broker proven on the VM path with one-shot SSH kept as
    recovery). DATES: FARCH asks the final adjudication to attach dates
    to these gates. Dates are not invented here; the coordinator sets
    one date per deletion at the step-9 prototype decision, records it
    before any deletion executes, and a deletion with no date does not
    execute. A staged plan that never schedules its deletions is a
    patch track with a new name; the dates are the schedule.
11. Acceptance ladder (section 4): rung 1 done (step 3), rung 2 live
    0-vision on real ws2 clone chats as the final gate for the chat
    class, rung 3 100-task held-out benchmark as the general gate.

## 4. ACCEPTANCE TEST (exact criteria, rungs, pass bars, evidence)

Precondition (required before ANY rung scores): CB-9 deployment manifest.
The source commit, the installed artifact (hashes), and the log of the
same build are recorded for the exact build under test. Without a
manifest, a pass cannot be attributed to a build, and the rung does not
count. The fixture bench pass (a1a672d) is not quoted as a gate until its
manifest is locked.

- Rung 1 (required, first): fixture 2-vision benchmark. Headless
  Firefox, local fixture. PASSED: bench wall 10.8596s, visions_used 2,
  outcome PASS, both sends V12 gated, run_id
  bench-20261121T234030Z-86e8d8 (a1a672d, V-Z5). Pass criteria: the
  script's own gates (V12 sent-bubble gate after each message, scoring
  by OUTCOME in the thread DOM, never point-in-box). Status: passed,
  pending manifest lock.
- Rung 2 (required, final gate for the chat class): live 0-vision
  benchmark on the REAL ws2 clone chats (clone1 Brave plus clone2
  Chrome). DOM harvest, plan, execute, DOM verify, zero screenshots in
  the machine loop. Pass criteria: accuracy at least 90%, defined as
  end-to-end TASK SUCCESS (not per-click hit rate), scored by DOM
  outcome (V12 sent-bubble gate, message in the thread DOM, never
  point-in-box); total wall time measured end to end including
  transport, with the per-phase timing split recorded in the live run
  log (model, SSH, broker, observe, act, verify); the live run's log
  carries CB's three-way result contract per action (sent, target,
  verified); never pool the 13/13 fixture with real-task numbers
  (CB-8). One final screenshot is kept as unscored human evidence (P9);
  it must not feed the score. HARD CONDITION (F2, section 2 item (b)):
  the final screenshot must be reviewed before a run scores as passed,
  and any DOM-vs-render mismatch FAILS the run. Conditions on the live
  run: P3 closed first (otherwise it falls back to screenshots and
  proves nothing); quiet window with clone coordination; owner approval
  per run (the bench's --live plus --confirm-live gates plus plan-URL
  gate); agreed test messages so the clones' working threads are not
  polluted. No time pass bar is set on the first run until P6 has
  baselined model inference time; nobody may claim the 10s target until
  that baseline exists.
- Rung 3 (required, the general proof): 100-task held-out benchmark
  (CB-EXEC design). Browser plus desktop tasks, new content and layout,
  run by an independent agent. Pass criteria: task success end to end
  at least 90%, defined as task success (not per-click hit rate); at
  least 96 passes out of 100 (Wilson 95% lower bound about 90.2%,
  verified by F1 V-F1-8 and FRT V-F7); per-phase P50/P90 recorded
  separately (model, SSH, broker, observe, act, verify); model-call
  counts, full-screen images, crops, DOM/a11y queries, and retries
  counted; false-success count (ok=true without a postcondition)
  reported as its own metric with zero tolerance as a honesty gate (any
  false success fails the run's honesty gate even if the count passes);
  side effects and recovery actions counted. Comparison arms on the
  same task set, order interleaved: screenshot-only, DOM plus real
  mouse, AT-SPI plus real mouse, executor. The task set, sampling, and
  independence rules are specified BEFORE rung 3 runs, or 96/100 is a
  number without a denominator. LIMIT recorded (FRT): the Wilson
  independence assumption does not hold for 100 tasks authored by one
  person on a handful of apps (shared app quirks correlate), so the 95%
  confidence claim is indicative, not a proof of independence. Rung 3
  is sequenced AFTER rung 2 (section 2 item (g)) and is NOT a
  precondition for it.
- Diagnostic option (not a rung): live 2-vision. If the live 0-vision
  run fails, the team may run live 2-vision to localize (script vs DOM
  path). It is not required before the final gate (section 2 item (b)).

What counts as evidence: a run counts only with its manifest, its
per-phase timings, its three-way result contract per action, and its
DOM-scored outcome. Diagnostic only: the live 2-vision run, the pixel
band (wherever a DOM assert exists), the P9 screenshot (human evidence,
never a score input except through the hard condition above), and any
fixture-only number (never pooled with real-task numbers).

What the fixture run does NOT prove, recorded as a gap not papered
over: a fixture pass alone repeats the F1a/F2b pattern (pass on the
exercise, unproven on the real task). The live run is the proof the
fixture cannot give, because the real tasks fail on Brave on ws2, where
the DOM path does not reach yet (P3). And the chat-class live run does
not prove the general 90% claim either: that is what rung 3 is for.
What the 100-task benchmark does NOT prove: it does not prove the live
clone chats, which is why the live 0-vision run stays the final gate
for the chat class; and it does not prove Zen chrome UI, which stays
screenshot-only per P8.

## 5. WHAT STOPS (what is never built, what is deleted and when, what is killed)

Never built:
- A second separate S3 runner alongside A1/CB-EXEC. One design
  decision, one prototype, one benchmark. Any lane building a parallel
  runner is stopped.
- A second executor alongside CB-EXEC (same merge; CB-EXEC is the design
  specification for the one build).
- A big-bang daemon/executor build before the B6 prototype gate. The
  prototype proves first; the replacement follows.
- Unrestricted zen_dom eval in the default agent interface. Remove in
  step 0 (CB-5); keep it in an explicit debug mode only.
- Generic x/y as the everyday model input. Coordinates become an
  adapter-internal detail; the model addresses semantic targets and
  element refs (CB-EXEC, P2).
- The screen-scope after-capture as produced today. Replaced by the
  both-fields shape via AMEND4 item 12 (cbab398); never ship a
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
- The 460x claim and the 0.01s multiplexing figure. Dead, never quoted
  again (SPEED's 0.01s was a failed-fast connection, rc=255, no
  return-code check; PROBE-S0 re-confirmed: best single live mux sample
  0.753s).
- The "SSH is 95% of 12.26s" claim. Dead as a slogan (CB-7 correction,
  section 2 item (h)); the 11.620s dispatch figure stands as measured.
- CB-4's 12.2%/3.4% math quoted as measured rates. Illustration only.
- The 66-element / 5-of-5 sweep claim as a proven fact (CB could not
  verify it from local evidence; it is a single measurement from clone2
  batch 7 until re-run).
- Any DONE label without a named specific evidence (CB-8).
- Any live-task migration on P3 before the experiment passes.
- Any blanket CU_CODE_EXEC=1 flip before the Y1b fixes plus fixture
  green plus CB-1 gate plus plateau definition (B2).
- Any deletion (A3 supervisor, A4 overlay server, A5 one-shot SSH as
  recovery, A6 file transport) before its replacement proves (B3/B4).
- Any new AMEND4 scope beyond the 12 items. AMEND4 is complete.

Killed or deleted, each gated on its replacement proving:
- One-shot SSH as the default transport (kept as fallback and recovery
  only, A5). Fresh SSH per call dies with S0.
- scp for JSON files as transport (audit files stay, A6/D2).
- Per-batch session spawn (after the S1/CB-6 conditions in step 8,
  section 3).
- Pixel-band verification as a pass signal for structured targets (after
  the P5 assert set exists per action type, A8). The band stays as a
  diagnostic.
- dom_rect_to_image_point from the live path (after P2, step 7; kept for
  tests and legacy).
- Screen-scope after-capture as produced today (replaced by the
  both-fields shape via AMEND4 item 12, cbab398).
- The 120s age refusal for DOM paths (future-clock refusal kept, D6).
- The scope-as-capability refusal in its legality form (with P2, reframed
  as snapshot binding, section 2 item (f)).
- The overlay daemon server (after session-level pill measured plus
  driver-owned pill crash proof, A4, step 10).
- The session supervisor tree (after the driver holds scope plus cancel
  latch plus lock, A3, step 10).
- CB-EXEC as a full build, if the prototype fails or stalls (section 1.4
  CB-EXEC row); A1/S3 remains the destination then.
- The LIQUID flicker phenomenon as a work item, if it does not reproduce
  on the current build (CB-10 gate).

Blocking findings, final status:
- B1 (A10 straight to 0-vision live on ws2 clone chats): LIFTED, with
  F2's P9 load-bearing condition as a hard condition on scoring
  (section 2 item (b)). Live 2-vision is diagnostic only.
- B2 (S2/D5 blanket CU_CODE_EXEC=1 flip): STANDS. Lift condition:
  fixture bench green (MET, a1a672d) plus 3 Y1b real fails fixed plus
  CB-1 gate for the flipped class plus plateau defined (HARD GATE),
  then flip for ONE live task class with act-now as fallback, measure,
  then expand.
- B3 (A4 overlay daemon deletion without a replacement): STANDS as a
  gate. Lift condition: session-level pill measured (server kept, CB-10
  precondition met), then driver-owned pill proves no stale or missing
  pill on crash.
- B4 (A3/A5 delete-first ordering): STANDS as a gate. Lift condition:
  the driver proves scope plus cancel latch plus lock, and the broker
  proves on the VM path (DONE, 1af7330) with one-shot SSH kept as
  recovery.
- B5 (P2 immediate interface rewrite): STANDS, narrowed, with FRT's
  repair condition added (section 2 item (d)). Lift condition: the
  stale-ref disagreement protocol is specified AND the defective proof
  tests for AMEND4 items 3, 4, 5-6 are repaired or re-verified.
- B6 (A1 full replacement claim): STANDS as a gate. Lift condition: the
  merged A1/S3/CB-EXEC prototype runs snapshot/execute/verify end to end
  on one live ws2 clone chat plus held-out tasks, with the wedged-session
  recovery protocol specified and proven.

## 6. EXECUTION PLAN (first workers to spawn, in order)

The coordinator spawns these; I do not execute them. Order is dependency
order. Each worker lands a measured win before the next step starts.
Every worker log carries test command, output, commit hash, and time log
(Lauren Tan standard), and no em/en dashes.

1. Y1b fix commission (FIRST). One worker, lane named by the coordinator.
   Task: fix the 3 Y1b real fails on code-exec (1e chr NameError; 2a
   codemode wall preemption absent, elapsed 7.20s; 2b code_exec wall
   preemption absent, elapsed 6.20s, ok=True with NO error, silent
   success). Evidence of done: the Y1b probe set re-run green on the
   fixed code, with the failing-first record. Gate it unblocks: B2 lift
   part 1, step 6 flip. (Owner: COORD-CLICK-3 to commission; no input
   names a lane, section 7.)
2. S0 implementation plus the step-0 measurement bundle. One worker (or
   one worker per bundle item, sequenced by the coordinator). Tasks:
   (a) S0 with the six hard requirements from the S0 row (setsid/nohup
   master, ControlMaster=auto, per-use liveness plus restart-on-death,
   ServerAliveInterval=15, per-socket watchdog, master-death logging);
   (b) P6 plus CB-7 plus CB-10 as ONE measurement workstream
   (timestamp points, harness owner, first-pointer timestamp,
   target_breached fix, VM-to-laptop dispatch split per phase, inference
   time separate from vision-call latency, error class per miss,
   capture parameters pinned); (c) CB-3 uniformity (one max_width) plus
   J37 codec separation, then re-run an E2-style calibration; (d) CB-5
   eval removal from the default agent interface (debug mode only);
   (e) CB-9 manifest habit in the deploy step. Gate: fallback explicit
   and watchdog in place. The 1-day soak runs in parallel, advisory.
3. AMEND4 close-out worker. Tasks: (a) run the four item-12 regression
   tests and record PASS on cbab398; (b) confirm the Codex-lane item-12
   delivery (driver log queue-check 06:19 found 0 hits; Result section
   still pending) or re-commission it; do not assume it done. (c)
   Round-3 council (separate commission): patch-vs-rewrite judgment per
   AMEND4 item under the 06:07 criterion, and repair or re-verify the
   defective proof tests for items 3, 4, 5-6. Gate it unblocks: B5 lift
   limb (ii), A9 proof-grade reliance.
4. Contract writer. One worker. Task: write the Layer 0 plus CB-EXEC
   merged contract (section 3 step 2) in parallel with AMEND4
   close-out, no code deleted. Gate it unblocks: P2/S1/P5 stop inventing
   ad-hoc interfaces; the step-9 prototype has a spec to prove against.
5. P3 re-run worker, in the first real quiet window. Preconditions:
   clone1 batch 9 complete with a final report commit, no new clone1
   batch assigned, Brave confirmed idle (clone1 stalled 48 min at
   finalization, nudged 06:45, V-Z8; do NOT run mid-batch). Task: the
   controlled Brave relaunch experiment (section 1.2 P3 row), including
   the shadow-DOM check item and the Chromium fallback login-persistence
   check. Outcome changes: pass unblocks the step-11 live run; fail
   (Brave refuses the port AND the Chromium migration is too disruptive)
   re-plans the program around Zen Marionette only and is reported
   plainly.
6. DOMZEN probe commission. No log exists at finalization. Task: DOM
   harvest on real Zen Messenger pages (rects exact, clicks land, DOM
   verify reads back), the first independent re-measurement of the
   clone2 batch 7 numbers (C1). Outcome changes: if rects disagree with
   rendered positions or the harvest fails on real pages, P2 and S2 stay
   MODIFY with a narrower task class, A10's live gate cannot be
   DOM-scored until fixed, and CB-5's locate confirmations gain a
   failing case to fix first.
7. P1/P5-for-class worker. Task: router plus P5 asserts per action type
   FOR THE S2 TASK CLASS, plus CB-1 contract for the class, plus CB-5
   locate confirmations. Gate it unblocks: step 6 flip.
8. Plateau definition (coordinator, not a worker). COORD-CLICK-3 defines
   the numbers from the fixture bench baseline (10.86s) plus first live
   runs, in RTD's form, before the flip. HARD GATE on the flip.
9. S2 one-class flip worker. Task: flip CU_CODE_EXEC=1 for ONE live
   task class (clone chat sends, or a Zen-reachable class if P3 is still
   NOT-RUN, C-O3) with act-now as fallback; measure model-call count
   and wall time. Gate to expansion: measured on one class.
10. P2 spec worker. Task: write the stale-ref disagreement protocol
    (FARCH core plus CB-2 binding, one protocol, not two) and re-verify
    AMEND4 items 2-4 wiring against P2's target functions. Gate it
    unblocks: B5 lift, P2 implementation.
11. P2 implementation worker. Task: the element-ref interface rewrite
    (section 1.2 P2 row), A9 one-system coordinates, scope refusal
    reframed as snapshot binding. Gate: P2 proven on the S2 task class
    with DOM verification mandatory.
12. S1 deletion worker. Tasks: sync the laptop tree, re-verify browser
    observe through the broker (9222 endpoint), decide the
    fatal-on-read-failure behavior, specify the queue discipline and
    single-owner serialization, delete the per-batch spawn with one-shot
    SSH kept as fallback and recovery, land the session-level pill
    (server kept, CB-10 precondition met). Gate: conditions (a)-(c) of
    section 3 step 8 met.
13. Prototype worker (A1/S3/CB-EXEC merged). Task: build the 2-3 day Zen
    prototype per the step-2 contract and prove it on one live ws2
    clone chat plus held-out tasks, with the wedged-session recovery
    protocol specified and proven and a destructive-action test proving
    no double-send on retry. Gate it unblocks: B6 lift, step 10
    deletions, merge decision.
14. Acceptance workers. Rung 2 live 0-vision run (after P3 and P2, quiet
    window, owner approval per run). Rung 3 100-task benchmark builder
    (task set, sampling, and independence rules specified BEFORE rung 3
    runs; the set is built after the prototype proves, not before).
15. Deletion workers (A3, A4, A5), last, each with its date set by the
    coordinator at the step-9 prototype decision (section 3 step 10).

Still-running probes as gated steps (what outcome changes which verdict):
- S0 soak completion (ends about 07:41 +07): advisory, not a gate. If
  the master dies repeatedly or hangs instead of failing clean, the
  per-socket watchdog design changes and the soak stops being advisory
  (calling S0 done then requires a stated master-lifetime number). It
  does not flip any verdict.
- DOMZEN (no log): gates P2 live value, S2 live expansion, A10 live
  gate DOM-scoring, CB-5 locate confirmations (see worker 6 above).
- S1 follow-ups (sync, endpoint, fatal-read decision, queue
  discipline): gate the per-batch spawn deletion only, not the S1
  ADOPT verdict (proof already landed, 1af7330).
- P3 re-run (NOT-RUN, 7b1006a): gates only the step-11 live run and the
  S2 flip class venue (C-O3 re-scope if still NOT-RUN). It does not gate
  steps 3-6.
- Codex/FCC discussion positions (pending, V-Z7): if they land with
  evidence that contradicts a verdict in section 1, the coordinator
  re-opens that row. They do not block this direction.

## 7. OPEN CONDITIONS AND OWNERS

- Plateau definition (numbers): owner COORD-CLICK-3. Form: Step 2 live
  median wall time above a stated threshold for a stated number of runs
  after the flag flip, decision owner the coordinator. HARD GATE on the
  S2 flip (section 2 item (e)). Numbers set from the fixture bench
  baseline (10.86s) plus first live runs; not invented here.
- Stale-ref disagreement protocol: writer is the P2 implementer, to be
  named by COORD-CLICK-3 when P2 is staffed. Due before P2 starts; it
  is B5 lift condition (i). Content: refuse, re-plan, or click stale,
  per case, plus the lifecycle across a multi-action plan, with FARCH's
  protocol core and CB-2 binding folded in.
- Defective proof tests for AMEND4 items 3, 4, 5-6: owner the round-3
  council (commissioned in section 6 worker 3). Repair or re-verify;
  it is B5 lift condition (ii). Evidence: 62b740e "F4 RT2 test
  defective", 72120aa "F5 behavior test defective", b44a5ea "F2/F3 RT2
  tests defective" (V-Z9).
- Y1b fixes (1e, 2a, 2b): owner COORD-CLICK-3 to commission; the fix
  lane is to be named. Due before the S2 flip; it is B2 lift condition,
  part 1. First worker in section 6.
- Item 12 Codex-lane confirmation: owner COORD-CLICK-3 (via the
  Codex amend4 driver). Driver-log queue-check 06:19 found 0 hits for
  the queued follow-up messages; Result section still pending (V-Z2).
  Confirm it or re-commission it; do not assume it done.
- Item 12 regression-test pass: owner the AMEND4 close-out worker
  (section 6 worker 3). Four tests in tests/test_first_action.py;
  shape verified from the diff by F2 V-F17, tests not run by anyone.
- S0 soak completion: owner COORD-CLICK-3. Soak ends about 07:41 +07,
  22/11/2026. Advisory, not a gate (section 6).
- DOMZEN: owner COORD-CLICK-3 to commission. No log at finalization.
  Gates P2 live value, S2 live expansion, A10 live gate DOM-scoring.
- P3 re-run: owner COORD-CLICK-3. Quiet window between clone batches,
  never mid-batch; rollback (relaunch without the flag, Brave session
  restore, re-login cost) stated BEFORE the window, not after. Clone1
  batch 9 open and stalled 48 min at finalization (V-Z8).
- S1 deletion conditions: owner the S1 deletion worker (section 6
  worker 12), commissioned by COORD-CLICK-3. Five conditions in the S1
  row (sync laptop tree, one-shot fallback/recovery, master watchdog
  plus soak, fatal-on-read-failure decision, single-owner
  serialization).
- Codex/FCC discussion positions pending: owners the Codex discuss
  driver (position not written as of 06:48 check) and the FCC discuss
  driver (run 2 launched 06:48, PID 824585). They do not block this
  direction; a contradicting landing re-opens the affected row (V-Z7).
- FARCH's request to attach DATES to deletion gates: owner
  COORD-CLICK-3. Dates are set at the step-9 prototype decision, one
  per deletion, recorded before any deletion executes (section 3 step
  10). Not invented here.
- P6 specification: timestamp points are named in this direction
  (observation delivered to the agent vs located target returned);
  logging owner is the harness, not cu.py. The P6 implementer lands it
  bundled with S0 (section 6 worker 2).
- Residual per-connection cost probe (D1 R2): ANSWERED by F2 V-F15
  (residual about 1.2-1.3s is per-session server-side setup, not shell
  startup; mux -O check only about 0.058s). No longer open; it bounds
  every transport design, including the Broker.
- V11 wiring confirmation: the P5 implementer confirms whether the
  production code-exec path reaches the arm_typed_flag call for every
  type action. Open, not load-bearing for the P5/A8 verdicts or for
  benchmark scoring.
- P3 failure re-plan: if Brave refuses the debugging port on its
  default profile and the Chromium migration is too disruptive, the
  DOM-first live path loses its highest-leverage unlock and the whole
  program re-plans around Zen Marionette only. That outcome must be
  reported plainly, not worked around silently.
- CB-9 manifest for the fixture bench pass: owner the deploy step
  (section 6 worker 2, habit from now on). Lock it before a1a672d is
  quoted as a gate.
- CB-10 LIQUID flicker probe: owner the A4 step-(a) worker. Load the
  plugin, reproduce the flicker, count repaints, or record an explicit
  owner deferral, before the session-level pill judgment.

## 8. CROSS-EXAMINATION NOTE (the CB rows, first-round and single-reviewer)

F1 recorded that the CB verdicts are first-round and single-reviewer:
D1, D2, D3, RTD and all four cross-responses predate the Codex report
and mark CB PENDING, so no council reviewer cross-examined CB-1..CB-EXEC
before the final round. This section IS that cross-examination: each CB
row judged against the other reports and the landed evidence. FCODEX
holds the Codex position and is not an independent cross-examiner; F1,
F2, F3, and FRT are the first cross-examination, and this finalizer is
the second, deciding where they disagree.

- CB-1 SURVIVES in substance, WEAKENS as a standalone proposal. The
  failure mode is proven (G30; FRT V-F2 envelope ok with no
  postcondition). But the rename breaks callers unless migrated in the
  same commit (first_action.py:552-563), and postconditions do not exist
  for every action type, so the standalone contract is BLOCKED and the
  content folds into P5/A8 with the exception list. Verdict: MODIFY.
- CB-2 SURVIVES in substance, WEAKENS as stated. Both defect limbs it
  names are CLOSED in the repo (limb 1 by AMEND4 item 12 cbab398; limb
  2 by the G28 loud refusal, F2 V-F11). What survives as new work is
  the planned-action binding, and the blanket stop is REJECTED in favor
  of re-ground-first, stop on ambiguity (FRT). Verdict: MODIFY.
- CB-3 SURVIVES in part. Uniformity and the J37 fix are verified from
  source and adopted (FRT V-F7). The taxonomy WEAKENS to gated: without
  P6-measured calls it is paperwork with no numbers to classify.
  Verdict: MODIFY.
- CB-4 SURVIVES as a constraint, FALLS as a measured claim. The
  arithmetic is correct (0.9^20 = 12.2%, 0.9^32 = 3.4%, FRT V-F7) but
  assumes independence, and Codex itself calls it an illustration; real
  errors correlate through the shared frame, so the true all-correct
  rate is likely worse when the frame is wrong. The rule (grow the batch
  only on proven validity) is adopted as a constraint on S2/CB-EXEC.
  The math must not be quoted as measured or used as a gate threshold.
  Verdict: MODIFY.
- CB-5 SURVIVES in content, WEAKENS as a separate build. Eval removal
  and AT-SPI coverage reporting are adopted; locate confirmations are
  adopted as requirements with definitions owed. The routing half
  FALLS as a standalone build: it is CB-EXEC's routing layer, and
  building it twice is duplicate work (FRT, F2). Verdict: MODIFY.
- CB-6 SURVIVES and STRENGTHENS. It duplicates S1 except for the
  sequential queue, and the S1 proof-first gate that justified MODIFY
  is now satisfied by PROBE-S1 (1af7330, broker 2.37x faster on a live
  batch). What remains owed is the queue discipline specification, a
  design detail, not a proof gate. Verdict: ADOPT, merged into S1.
- CB-7 SURVIVES as method, PARTLY FALLS on its broad claim. The
  methodological point is real (the act-now JSONL starts after the
  command reaches the laptop, so it cannot support a dispatch share).
  But CB 2.7's "no record supports 11.6s of 12.26s is SSH dispatch" is
  WRONG in the broad form: the 11.620s dispatch IS measured (F2b log
  lines 34-35, D1 V10, F2 V-F13); only the SSH-alone attribution is
  inference. Verdict: ADOPT, with the correction recorded.
- CB-8 SURVIVES fully. The todolist's DONE labels are proven to
  overreach (13/13 on a fixture cannot become a 90% commitment on
  another app; held-out new app is PARTIAL; J10 real think-time is
  OPEN). Scoped to the DONE items that gate this direction. Verdict:
  ADOPT as a standing rule.
- CB-9 SURVIVES and STRENGTHENS. The file-presence limb is STALE
  (first_action.py IS tracked on todolist-push now), but the divergence
  limb is CONFIRMED LIVE (installed first_action.py 23442 bytes vs repo
  33893 bytes; installed cu.py also differs; FCODEX V-F7, FGROUND
  V-F10). The manifest is overdue and is a precondition for the
  acceptance ladder. Verdict: ADOPT.
- CB-10 SURVIVES as a separation, WEAKENS as a standalone track. The
  flicker-vs-think-time separation is right, but it duplicates P6/CB-7
  measurement work and the flicker itself is unproven on the current
  build (plugin not loaded). It folds into ONE measurement workstream,
  and the flicker probe (or an explicit owner deferral) gates the A4
  session-level pill judgment. Verdict: MODIFY.
- CB-EXEC SURVIVES as a design direction and a prototype, FALLS as a
  full build. The direction (semantic targets, preconditions, real
  input, postconditions, one local broker, backends under one contract)
  is the same destination as A1/S3 and is adopted as the design spec
  for the single merged prototype. The full build (1-2 week merge plus
  100-task benchmark as a design gate) falls on FRT's six findings:
  zero lines built and zero measurements; the concentrated
  single-session-slot risk with no specified recovery; the circular
  retry rule; the disproportionate benchmark with a decorative
  independence assumption; absorption of the staged order; and an
  unproven schedule estimate. The prototype is authorized; the merge is
  decided on measured evidence after it. Verdict: MODIFY to
  prototype-only.

No CB verdict in this direction rests on Codex's authority. Each rests
on its own evidence, on a cross-examining reviewer's verification, or on
landed probe evidence, as cited in section 1.4.

## 9. Evidence index

- ARCH log: improvements/worker-arch-review-log.md (074c1d7).
- GROUNDING log: improvements/worker-grounding-review-log.md (d1fc4e9).
- SPEED log: improvements/worker-speed-review-log.md (a4ecb49).
- CODEX-BREAKTHROUGH report: improvements/codex-breakthrough-report.md
  (2596287, 138 lines).
- D1: improvements/worker-click3-d1-review-log.md (37f457e).
- D2: improvements/worker-click3-d2-review-log.md (6d1bf04).
- D3: improvements/worker-click3-d3-review-log.md (14fc139).
- RTD: improvements/worker-click3-rtd-review-log.md (e96b2ff).
- X1: improvements/worker-click3-x1-response-log.md (0cf601c).
- X2: improvements/worker-click3-x2-response-log.md (d5b205d).
- X3: improvements/worker-click3-x3-response-log.md (2b0c73c).
- XRT: improvements/worker-click3-xrt-response-log.md (6cb3f95).
- Draft adjudication: improvements/worker-click3-adjudication-log.md
  (9d23834).
- F1: improvements/worker-click3-f1-review-log.md (7124f1e, 765 lines).
- F2: improvements/worker-click3-f2-review-log.md (48c6aee, 763 lines,
  addendum sections 9.1-9.9).
- F3: improvements/worker-click3-f3-review-log.md (433a6e6, 812 lines).
- FRT: improvements/worker-click3-frt-review-log.md (5f30908, 627
  lines).
- FARCH: improvements/worker-click3-farch-response-log.md (c3bf5e0, 697
  lines).
- FGROUND: improvements/worker-click3-fground-response-log.md (8d0e38a,
  890 lines).
- FSPEED: improvements/worker-click3-fspeed-response-log.md (e7562ca,
  853 lines).
- FCODEX: improvements/worker-click3-fcodex-response-log.md (09c6b3f,
  430 lines).
- PROBE-S0 interim: improvements/worker-probe-s0-log.md (90eb8be, 254
  lines).
- PROBE-S1: improvements/worker-probe-s1-log.md (1af7330).
- PROBE-S2: improvements/worker-probe-s2-log.md (f1952a5; bench pass
  a1a672d).
- PROBE-P3: improvements/worker-probe-p3-log.md (7b1006a, NOT-RUN).
- PROBE-P8: improvements/worker-probe-p8-log.md (3790901, BLOCKED).
- PROBE-DOMZEN: no log, no commit at finalization.
- AMEND4 landed state at HEAD 1af7330: all 12 items (cc964b2, c1ea773,
  62b740e, 72120aa, b44a5ea, 49081aa, af0fa87, 44c15bb, e912ad4, 8d75135,
  cbab398).
- Codex discuss driver log: improvements/worker-codex-discuss-driver-log.md
  (check 1 at 06:48 +07, position not yet written).
- FCC discuss driver log: improvements/worker-fcc-discuss-driver-log.md
  (run 1 finished 06:38 +07; run 2 launched 06:48 +07, PID 824585).
- Codex amend4 driver log: improvements/worker-codex-amend4-driver-log.md
  (queue-check 06:19 +07, 0 hits; Result pending).
- Y1b BLOCK: commit 9d9bd63 (14/20, 3 real fails 1e/2a/2b).
- Bench: tests/two_vision_bench.py on todolist-push (c5311ce, 868
  lines); fixture tests/two_vision_fixture.html (7f3a70b).
- Numbers used: fresh SSH mean 4.667s (n=10), mux mean 1.339s (n=18),
  3.49x, saving 3.328s per connection (PROBE-S0 90eb8be); broker core
  12.110s vs one-shot 28.700s, delta 16.590s, 2.37x, laptop act about
  258ms (PROBE-S1 1af7330); fixture bench 10.8596s, visions_used 2,
  PASS (a1a672d); vision 17/29 first-try 58.6%, Wilson 40.7-74.5%;
  pointer error 0.5-0.9px; DOM 66 rects median 0.030s, verify
  0.002-0.015s (single-source, clone2 batch 7, C1 applies); F2b
  order-to-overlay 12.262s (dispatch 11.620s measured, SSH-alone
  attribution inference); overlay acquire 315-349ms; scp 4.57-4.93s
  over live mux (n=4), 8.1-9.4s fresh; installed first_action.py 23442
  bytes vs repo 33893 bytes; tc02-t1 gap 722.955s (87.8%) measured with
  a local helper, no SSH hop in it.
- Code refs verified by the reviewers and accepted here: scripts/cu.py
  (observe 920, observe_screen 974, image_point 1000-1005,
  _input_line_changed 1023-1076, desktop_act 1619-2199, scope refusal
  1648/1649 and 1665-1666, after-capture 2083-2091, OBSERVATION_MAX_AGE
  120 at line 58, refusal 773, --dom-selector 2717, code-exec subparser
  2733, CU_CODE_EXEC gate 2770/2793), scripts/first_action.py
  (attempt_session 183, envelope after-capture 656, G28 loud refusal
  478-498, _scope_after 328, after_screen 462/737),
  scripts/fastpath.py (152, 195-243), scripts/dom_act.py
  (ground_many_one_shot 240-331, focus_type 425-491, arm_typed_flag
  call 433-434), scripts/zen_dom.py (harvest 905, locate 567-588,
  hit_check 820-851, arm_typed_flag with MutationObserver, eval
  subparser 1153/1171), scripts/cdp.mjs (616 lines, Brave
  debugging-port comment 227-243), scripts/cursor_session.py
  (supervise 228), scripts/overlay.py (613 lines),
  scripts/session_remote.py (1601 lines, Broker 463, relay socket
  /run/user/1000/computer-use-wayland/relay.sock),
  scripts/session_driver.py (180 lines), scripts/code_exec.py (880
  lines, gate 134), scripts/a11y.py (83-104, truncated flag).

## 10. Log commit record

- Written: 2026-11-22 about 07:12 +07 (T+20m from task receipt at
  06:52 +07). Branch todolist-push, HEAD at writing 1af7330.
- Commit: (filled after commit; see below).
- This log is the FINAL direction. It supersedes the adjudication DRAFT
  (9d23834) in full. Any later evidence that contradicts a verdict here
  (Codex/FCC discussion positions, S0 soak completion, DOMZEN, P3
  re-run) re-opens the affected row through the coordinator; it does
  not silently amend this log.
