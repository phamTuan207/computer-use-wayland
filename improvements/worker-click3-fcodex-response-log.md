# Worker CLICK3-FCODEX: response holding the CODEX-BREAKTHROUGH position

Owner: the owner. Role: final discussion participant holding the
CODEX-BREAKTHROUGH position. The original CODEX-BREAKTHROUGH worker
completed and cannot receive follow-ups, so I hold its position from
its report: improvements/codex-breakthrough-report.md, commit 2596287
(138 lines, Vietnamese), plus its launch log
improvements/worker-codex-breakthrough-log.md. Decision criterion
(owner standing rule 06:07): judge every proposal by the accuracy and
speed of its FINAL RESULT, never by rewrite size or cost. Cost is
IRRELEVANT. Evidence standard (owner 06:34, Lauren Tan standard):
every claim carries real measured numbers; where evidence is missing I
say so plainly, including for the report's own section 4.

Rules honored: no em dash (U+2014) or en dash (U+2013) anywhere in
this file. No personal info. Evidence with every claim. Wall-clock
Asia/Ho_Chi_Minh plus elapsed time. Commit with an explicit pathspec
immediately after staging, never plain git commit, never git add -A.
Verify every push with git ls-remote. Never ydotool. This is a review
response, not my own work, so no self-healing question arises.

## 0. Log and what I verified myself

- 06:37 +07 (T+0s): task received. Repo ~/workspace/computer-use-wayland,
  branch todolist-push. Fetched first; local HEAD was 7b1006a at start,
  in sync with origin/todolist-push.
- 06:37-06:39 (T+0-2m): read all 11 inputs in full: the draft joint
  adjudication (improvements/worker-click3-adjudication-log.md,
  9d23834), ARCH-REVIEW (074c1d7), GROUNDING-REVIEW (d1fc4e9),
  SPEED-REVIEW (a4ecb49), CODEX-BREAKTHROUGH report (2596287) and its
  launch log, D1 (37f457e), D2 (6d1bf04), D3 (14fc139), RTD (e96b2ff),
  X1 (0cf601c), X2 (d5b205d), X3 (2b0c73c), XRT (6cb3f95).
- 06:39-06:41 (T+2-4m): spot checks of my own (section 0.1). The branch
  moved during this work: HEAD at writing was 2864be4 (probe-p8 record
  commit). AMEND4 items 5, 6, 7, 8 have landed since the draft
  (b44a5ea items 5-6, 49081aa item 7, af0fa87 item 8). The bench files
  are now on todolist-push (c5311ce, 7f3a70b). Probe-p3 is NOT-RUN
  (7b1006a, clone1 batch 9 open since 06:01, Brave untouched).
  Probe-p8 has returned (3790901).
- 06:41 +07 (T+4m): wrote this log.
- 06:43 +07 (T+6m): branch moved again during writing (HEAD now
  8d0e38a). Two load-bearing facts landed and are incorporated before
  commit: the fixture 2-vision bench PASSED in 10.86 s (a1a672d, Y1b 3
  fails still open, flag NOT flipped, gate b unmet), and AMEND4 items
  9, 10, 11 landed (44c15bb, e912ad4, 8d75135). Parallel final
  responses also landed (farch c3bf5e0, fspeed e7562ca, fground
  8d0e38a); they are not inputs to this response, and the ARCH merge
  of CB-EXEC into Layer 0 is consistent with section 2.1 (one build,
  not two). Updated V-F10, section 3, section 6, and section 8.

### 0.1 Spot checks run by me in this session (new verification, not trust)

- V-F1. Wilson intervals recomputed by me (python3, z=1.96): 17/29
  gives 40.7%-74.5%, exactly CB section 2.3; 96/100 gives
  90.16%-98.43%, lower bound just above 90%, confirming CB section 3
  (96 pass needed for 95% confidence that the true rate is at least
  90%); 95/100 gives a lower bound of 88.8%, insufficient. Batch
  math recomputed: 0.9^20 = 0.1216 (CB 12.2%), 0.9^32 = 0.0343
  (CB 3.4%). CB's arithmetic is correct in all three places.
- V-F2. The false-success contract (CB 2.1) still holds in the current
  tree. scripts/cu.py:2113 states the pixel-hash result meaning in
  plain text: "Exact captured pixel hash differs; animations count.
  Does not confirm app action succeeded." scripts/first_action.py:552-563
  sets envelope ok=True when the session result says ok, or when the
  completed-capture shape holds (full batch ran). The fallback path at
  line 637 passes through result.get('ok') from desktop_act. The
  envelope therefore reports ok on input-sent evidence, not on
  target-state evidence. scripts/a11y.py:208 confirms the AT-SPI limb:
  do_action returning true is treated as the click done, with no
  post-state check.
- V-F3. CB 2.2, second limb, is CLOSED since CB's checkout. The G28
  loud refusal is enforced in the current tree:
  scripts/first_action.py:478-498 returns 1 with path='refused'
  before any session attempt and before any action runs, when a given
  observation was rejected and a screen capture substituted. The
  _fresh_observation docstring (lines 328-350) states the same rule.
  CB's silent-substitution finding was true at its checkout and is
  fixed now. The first limb is still OPEN: line 661 still captures
  the envelope after-image with cu.observe_screen unconditionally
  (max_width=1920), regardless of input scope.
- V-F4. CB 2.3 image non-uniformity, verified in the current tree:
  observe_screen defaults to max_width=960 (scripts/cu.py:974
  signature), while act-now captures at max_width=1920
  (scripts/first_action.py:353 and 661). The model sees different
  resolutions and compression by path, as CB states.
- V-F5. Broker wiring gap, re-verified by me: grep for
  session_remote|Broker in scripts/first_action.py and scripts/cu.py
  returns 0 and 0, same as X1/X2/X3. CB 2.6 stands.
- V-F6. Code-exec flag gate, re-verified: scripts/code_exec.py:134
  gates on CU_CODE_EXEC in 1/true/yes; scripts/cu.py:2815 and 2838
  refuse code-exec when the flag is off. CB 2.5's "DOM actions only
  behind the flag" stands.
- V-F7. Deployment drift (CB 2.9), checked LIVE with one read-only
  SSH call at 06:40 +07 (about 4.4s, no GUI touched, no task
  disturbed). Laptop repo HEAD is 3790901 (probe-p8), working tree
  clean except untracked improvements files. Installed
  first_action.py is 23442 bytes (Nov 21 23:26) and DIFFERS from the
  repo copy (33893 bytes); installed cu.py also DIFFERS from the repo
  copy. The "first_action.py not in repo" limb is CLOSED (git ls-files
  shows scripts/first_action.py tracked on todolist-push), but the
  drift limb is CONFIRMED LIVE and worse than CB stated: not merely
  untracked, but diverged. The "behind 622 commits" count was per
  remote-tracking ref without a fetch (CB's own caveat); the material
  fact is installed != repo, verified live.
- V-F8. Draft coverage gaps, verified by grep on the draft file:
  0 hits for "liquid", 0 for "622", 0 for "manifest", 0 for
  "first_pointer" (case-insensitive for liquid). The draft does not
  handle the LIQUID flicker probe, the 622/behind count, the manifest,
  or the first-pointer timestamp. See section 6.
- V-F9. P8 has returned since the draft: commit 3790901 records
  Marionette chrome context BLOCKED without a Zen restart (HTTP 500,
  MOZ_REMOTE_ALLOW_SYSTEM_ACCESS required), C12 reproduced live. The
  Zen-chrome structured path needs an owner-approved restart or stays
  screenshot-only. CB-EXEC keeps screenshot-crop for chrome UI.
- V-F10. AMEND4 landed state, updated 06:43 +07 to HEAD 8d0e38a:
  items 1-11 landed (item 1 cc964b2, item 2 c1ea773, item 3 62b740e,
  item 4 72120aa, items 5-6 b44a5ea, item 7 49081aa, item 8 af0fa87,
  item 9 44c15bb, item 10 e912ad4, item 11 8d75135). Item 12 is the
  only outstanding item, in flight on two lanes. The B5 second limb
  (items 2-4 landed) is satisfied; the stale-ref protocol limb is
  still the single outstanding gate for P2. Fixture 2-vision bench
  PASSED in 10.86 s (a1a672d); Y1b 3 fails still open, flag NOT
  flipped (gate b unmet).
- V-F11. CB 2.5 zen_dom locate weakness: I verified the shape, not
  every missing check. scripts/zen_dom.py evaluate() exists at line
  441 and the rect path goes through evaluate (line 587); the locate
  path is querySelector plus getBoundingClientRect, as CB cites (its
  lines 172-185, moved since its checkout). I did not re-verify each
  absent check (visible, interactable, uncovered, stationary,
  uniqueness) line by line, so I cite CB's reading with its source
  and mark the per-check absence as CB-reported, not re-proven here.

### 0.2 Numbering note

CB's report does not number its proposals. I number them here so the
draft's missing verdicts can be given per proposal: CB-1 to CB-10 map
to report sections 2.1 to 2.10 in order, and CB-EXEC maps to section 3
(the semantic transaction executor). Every verdict below cites the
report section, so the mapping is checkable.

### 0.3 What CB adds that is new, and what is a re-read

CB agrees with the draft's caution (draft section 1.4, RTD C1): a
fourth reading of the same evidence base is still the same evidence
base, and CB's arrival is not a tie-breaker by default. Where CB is
new evidence, not a re-read: the read-only synthesis of the act-now
JSONL (199 lines, p50 order-to-overlay 337.5 ms, max 368.4 ms, wrapper
p50 2.288 s, max 6.95 s, 167 ok true, 32 false, 195 session, 4
fallback, 0 timeout, 5 captured observations); the deployment-drift
observation from its own checkout (section 2.9, now live-confirmed
by V-F7); the Wilson intervals and the batch-probability arithmetic
(both recomputed correct, V-F1); the unrestricted-eval restriction
(CB-5, named by no reviewer before CB); and the 100-task held-out
benchmark design with the 96/100 bar (CB-EXEC, section 5 below).
Those are judged on their own numbers, not as a tie-break. Where CB
re-reads (E2 17/29, G30 64/75 px, clone2 batch 7, F2b), C1 applies:
one measurement cited a fourth time is still one measurement.

## 1. Per-proposal verdicts (CB-1 to CB-10 plus CB-EXEC)

Legend: ADOPT means do it as proposed. MODIFY means do it with the
stated change; the gating conditions attached are what must be proven
before it proceeds. REJECT means do not do it (no CB proposal is
rejected in full).

| ID | Proposal (report section) | Verdict | Evidence, reasoning, and gating conditions |
|----|---------------------------|---------|---------------------------------------------|
| CB-1 | 2.1 False-success contract: split input_sent from verified; every result must state input sent, right target received it, target state reached; postcondition per action | ADOPT | Strongest finding in the round. Verified in the current tree (V-F2): cu.py:2113 disclaims the pixel hash as success evidence; first_action.py:552-563 sets envelope ok on session ok or on the completed-capture shape; a11y.py:208 treats do_action true as done. Live proof: G30, 3 batches ok/completed, 0 messages sent, clicks 64 px and 75 px above the real field. The same flaw inside code-exec: Y1b 2b, wall preemption returns ok=True with NO error after 6.20 s (commit 9d9bd63, 14/20, 3 real fails). Council 1 A3 (exit code never proves success) does not cure it, because the stdout envelope ok it requires is still input-sent level. Gating condition, NEW: the verified/input_sent split lands for a task class BEFORE the S2 flip for that class. Without it the flip ships the same flaw in the new path. This is an additional gate on S2 alongside B2, not a replacement for B2. |
| CB-2 | 2.2 Scope is mandatory action data; a scope change stops the batch, no silent frame swap | ADOPT in principle, MODIFY in scope | Limb 1 (after-image scope) still OPEN: first_action.py:661 still captures the envelope after with observe_screen unconditionally (V-F3). ADOPT the both-fields fix (A7/P4, AMEND4 item 12) as the remedy for this limb. Limb 2 (_fresh_observation silent substitution) is CLOSED since CB's checkout: the G28 loud refusal is enforced at first_action.py:478-498, returning 1 before any session attempt, path='refused' (V-F3). Do not re-do limb 2. Remaining gap beyond both-fields: the planned-action case, actions planned on a window observation and executed after a screen observation arrived. CB-2's rule (scope plus observation ID as mandatory action data, refuse on mismatch) covers it; both-fields alone does not. The scope-as-capability refusal deletion stays sequenced with P2 (D3's timing, adopted by the draft), not with the fix. |
| CB-3 | 2.3 Vision is wrong, scale is not the whole story; image inputs are non-uniform; JPEG preflight false refusal | ADOPT as diagnosis | Vision 17/29 = 58.6% first-try, Wilson 40.7%-74.5%, recomputed exact (V-F1). G30 64/75 px misses are vision reads, not scale: screen 1920x1200 scale 1, mapping at cu.py:973-977. Non-uniform inputs verified (V-F4): observe defaults to max_width=960, act-now captures at max_width=1920, JPEG q90 in between. J37 patch 6.627 vs threshold 6 (CB-cited, not re-verified by me) is the codec false-refusal candidate. Consequence: no global scale fix; the fix is semantic grounding plus a uniform capture spec for the vision fallback (lossless crop, one width). The prescription folds into CB-EXEC; no separate build. |
| CB-4 | 2.4 Maximizing actions per image is the wrong goal; batch grows only when the executor proves the next steps still valid | ADOPT | Math verified (V-F1): 0.9^20 = 12.16%, 0.9^32 = 3.43%. CB states the independence assumption as illustration, and I hold it as an upper bound, not a measurement: real errors correlate, so compound success is worse than the illustration only if errors cluster, better if the executor re-validates. The 32-action batch cap (CB cites cu.py:1013-1019, code_exec.py:187-192) is not a feature to maximize. Consequence, and a direct qualification of S2/D5: code-exec programs must checkpoint per side-effecting step, not batch 32 blind. Batching is earned per step by postcondition, which is CB-1 applied to batching. |
| CB-5 | 2.5 No common executor; backends exist but unrouted; zen_dom locate is weak; unrestricted eval out of the default agent interface | ADOPT | Act-now calls desktop_act only; code-exec DOM actions sit behind CU_CODE_EXEC (V-F6) and are Chromium-scoped per CB; zen_dom opens and closes a session per invocation (CB cites 81-115, 221-245, consistent with the CLI shape); AT-SPI truncates at 500 nodes or 2 s, max 80 items (CB cites a11y.py:83-104, taken as cited). Locate weakness: shape verified, per-check absence CB-reported (V-F11). The eval restriction is new in this round: zen_dom evaluate() exists (line 441) and the CLI exposes eval; CB's prescription (read/query API only by default, eval kept in an intentional debug mode) is ADOPT, no reviewer before CB named it. Backend coverage reporting (a backend must report its coverage, then fall back) is ADOPT as part of P1's router: the router log line the draft requires (section 1, P1) is where the coverage report lands. |
| CB-6 | 2.6 Act-now does not use the long-lived session driver; one owner of pointer, overlay, and browser session, sequential queue, no competing BiDi plus Marionette | ADOPT | Broker wiring gap re-verified by me: 0 references to session_remote or Broker in first_action.py and cu.py (V-F5). The Broker and session_driver exist as files; the live path does not use them. Same substance as S1/A1's single-owner requirement, stated from the session-lifecycle side. Fold into S1/A1, do not build separately: the single-owner rule (one owner, sequential queue, timeout, session closed in finally) becomes an explicit CB-EXEC requirement on the A1 prototype. The one-session-per-Firefox constraint (proven in 4 runs, GROUNDING 1.2) is the reason the owner must be single. |
| CB-7 | 2.7 Latency measurement is wrong: order_to_overlay from wrapper start, no first-pointer timestamp, target_breached compares the whole batch to 30 s | ADOPT | Wrapper-start point verified: envelope order_to_overlay_ms = _ms(t0) at first_action.py:470, where t0 is the wrapper start, not the user command on the VM. The JSONL synthesis (199 lines, p50 337.5 ms, max 368.4 ms, wrapper p50 2.288 s, max 6.95 s, 167 ok, 32 not, 195 session, 4 fallback, 0 timeout, 5 captured) is CB's read-only synthesis, taken as reported, not re-run by me. Prescription ADOPT: first-pointer-action timestamp, VM-to-laptop dispatch measured separately with the same workload (fresh SSH vs connection reuse), target_breached redefined on first action, not the whole batch. This belongs in draft step 0 with S0/P6; the draft does not name it (V-F8, 0 hits for first_pointer). MODIFY the draft step 0 to include it. |
| CB-8 | 2.8 Speed evidence is not representative: fixture 0.64 s / 15 steps has no baseline; 13/13 cannot become a 90% commitment; held-out PARTIAL; J10 think time OPEN | ADOPT | The fixture-vs-real distinction is CB's reading of docs/final-report-20261121.md:160-194 (taken as cited with source, not re-read in full by me). The 13/13 point is arithmetic plus C1: a fixture pass is one task class, not a held-out rate. Consequence: no 90% claim until the held-out benchmark runs. This agrees with the draft's own section 3 gap note (a fixture pass alone repeats the F1a/F2b pattern). J10 think time OPEN is the same gap P6/CB-7 address. |
| CB-9 | 2.9 Deployment drift: checkout behind, first_action.py untracked, installed cu.py has extra branches; lock source commit, installed artifact, and log into a manifest | ADOPT, with status update | At CB's checkout (4500a18) the claim held. At HEAD 2864be4 the untracked limb is CLOSED (scripts/first_action.py is tracked; repo copy 33893 bytes), but the drift limb is CONFIRMED LIVE by my probe (V-F7): installed first_action.py is 23442 bytes and DIFFERS from the repo copy; installed cu.py also DIFFERS, at laptop HEAD 3790901. The "behind 622" count was per remote-tracking ref without a fetch (CB's own caveat); the material fact is installed != repo, verified live. Prescription ADOPT: a manifest locking source commit plus installed artifact hashes plus the log of the build that ran, before any benchmark is quoted as a release gate. This is a NEW gate the draft lacks (V-F8, 0 hits for manifest). Owner: coordinator; due before the fixture bench run is quoted as a gate. |
| CB-10 | 2.10 Overlay flicker LIQUID untested plus think time unmeasured; do not attribute either to SSH or screenshot without phase numbers | ADOPT, split | Think-time limb: covered by draft P6 (ADOPT with the timestamp-points and harness-owner spec) plus CB-7. Overlay limb: NOT handled by the draft (V-F8, 0 hits for LIQUID). The todolist record CB cites (LIQUID test not run because the plugin was not loaded) means there is no evidence the initial flicker was reproduced or fixed. Prescription ADOPT: probe first (load the LIQUID plugin, reproduce flicker, count repaints) before A4's session-level pill is judged, or record an explicit deferral with an owner. The pill change alters overlay acquisition, so flicker status interacts with it; judging A4 without a flicker measurement risks fixing the wrong thing. |
| CB-EXEC | Section 3: local semantic transaction executor (semantic targets, preconditions, real mouse/keyboard input, postconditions, retry only when surely unsent), vision as fallback, one local broker, DOM/BiDi plus AT-SPI plus screenshot-crop backends under one contract | ADOPT as the contract, MODIFY as the build | The contract is the correct end state under 06:07: it is the only proposal that fixes the false-success flaw at the contract level rather than at one call site. Evidence for the flaw is the strongest in the round (G30, Y1b 2b, cu.py:2113, V-F2). Build MODIFY: do not build a new daemon on day 1. Implement the contract inside the existing parts in the draft's order (P1 router, P5 asserts, P2 element-ref, S2 code-exec as the first host), prototype on one live ws2 clone chat as the B6 lift evidence, and let that prototype BE the A1/S3 daemon decision (one build, not two). Effort estimates (2-3 days Zen prototype, 1-2 weeks full merge, days for the benchmark) are CB's planning numbers, unexecuted; the prototype gate, not the estimate, decides. "Remove generic x/y as everyday model input" is ADOPT for structured targets, MODIFY for the fallback: pixel coordinates stay as the internal detail of the pointer adapter and as the fallback input form for canvas, games, and chrome UI until P8 resolves. |

Tally for CB: ADOPT 9 (CB-1, CB-3, CB-4, CB-5, CB-6, CB-7, CB-8, CB-9, CB-10 in its split form), MODIFY 2 (CB-2 scope, CB-EXEC build), REJECT 0.

## 2. How CB-EXEC relates to A1, P2, and S2

### 2.1 CB-EXEC vs ARCH A1 (persistent driver daemon): same direction, overlapping, not competing

A1 is the process shape: a persistent driver daemon with
snapshot/execute/verify, structured-first. CB-EXEC is the contract
that daemon must implement: semantic targets, preconditions,
postconditions, verified vs input_sent, retry only when surely
unsent, one owner. A1 as stated does not specify the contract; a
daemon can snapshot, execute, and verify by the same weak signals
(envelope ok, pixel band) and still report false success. CB-EXEC as
stated does not specify the process shape beyond "one local broker".
They are two halves of one design, not two designs. Adopt both, with
one merge: the A1 prototype must implement the CB-EXEC contract, and
the B6 lift (prototype proves snapshot/execute/verify end to end on
one live ws2 clone chat) is extended with CB-EXEC's per-action proof:
no ok=true without a verified postcondition on side-effecting
actions. The draft's A1 MODIFY (staged prototype, B6 gate) stands;
CB-EXEC supplies the acceptance spec the prototype is judged against.
No second daemon build is authorized.

### 2.2 CB-EXEC vs GROUNDING P2 (element-ref interface): P2 is a proper sub-piece, CB-EXEC is the superset

P2 (live rect re-read at execution, screen-point action form, delete
dom_rect_to_image_point from the live path) is the addressing half of
CB-EXEC: it makes the target address exact. It has no preconditions,
no postconditions, no retry policy, and no scope binding. An
element-ref click that lands on the right element but does not change
the target state would still report ok under P2 alone. CB-EXEC is the
superset that gives P2 its acceptance test. Same direction, no
competition. P2 is the first implementation slice of CB-EXEC,
sequenced per B5: the items 2-4 limb is satisfied (V-F10), the
stale-ref disagreement protocol is still the single outstanding gate.
Note the protocol CB-EXEC needs is exactly the protocol B5 demands:
when a live rect re-read disagrees with the plan, refuse, re-plan,
or click stale, per case. CB-EXEC and B5 name the same missing piece
from opposite sides.

### 2.3 CB-EXEC vs SPEED S2 (code-exec switch-on): S2 is the delivery vehicle, CB-EXEC is the contract the vehicle must satisfy

Same direction, complementary, with one hard qualification. Code-exec
already has DOM actions, assertions, and an allowlisted API; flipping
CU_CODE_EXEC=1 is how CB-EXEC gets a live path without building a new
daemon first. But S2 as stated is INSUFFICIENT and, without CB-1,
actively repeats the flaw in the new path: Y1b 2b (ok=True, no error,
6.20 s past the wall budget) is a code-exec instance of CB-1. The S2
one-class flip therefore gains a new gate: the verified/input_sent
split (CB-1) lands first for the flipped task class, and the flip is
judged by postcondition pass rate, not by envelope ok rate. The
draft's B2 gate (Y1b fixes plus fixture bench green) is necessary but
not sufficient; CB-1 is the additional gate. CB-4 also qualifies S2:
code-exec programs must checkpoint per side-effecting step, not batch
32 blind. S2 remains the 10x-path chassis; CB-EXEC is the contract
that makes its wins real instead of reported.

## 3. The draft's order of work: accepted with four amendments

The draft's section 2 order is accepted in substance: S0 plus P6,
AMEND4 slower, P3, fixture bench, Y1b fixes, P1/P5, S2 one class, P2,
S1, A1/S3, deletions, acceptance ladder. CB's position amends it in
four places. None of the four changes the direction; each adds a
gate the draft's own evidence requires.

- Amendment 1 (step 0): S0 plus P6 PLUS CB-7 instrumentation and the
  CB-9 manifest. P6 measures the vision call; CB-7 measures dispatch
  plus first action (first-pointer timestamp, dispatch split fresh vs
  reuse, target_breached redefined); CB-9 locks which build ran
  (source commit plus installed artifact hashes plus log). All three
  are measurement hygiene, and all three must exist before the
  fixture bench run is quoted as a gate. The draft bundles P6 with S0
  but names neither CB-7 nor CB-9 (V-F8).
- Amendment 2 (step 2, P8): P8's question is now partly ANSWERED by
  probe-p8 (3790901): Marionette chrome context is BLOCKED without a
  Zen restart (HTTP 500, MOZ_REMOTE_ALLOW_SYSTEM_ACCESS required),
  C12 reproduced live (V-F9). The Zen-chrome structured path needs an
  owner-approved restart or stays screenshot-only. CB-EXEC keeps
  screenshot-crop for chrome UI and records the boundary explicitly.
  P3 is still NOT-RUN (7b1006a, clone1 batch 9 open since 06:01).
- Amendment 3 (steps 4-6, S2 gating): the S2 one-class flip is gated
  on B2 (Y1b 1e/2a/2b fixed, fixture bench green) AND on CB-1 (the
  verified/input_sent split lands for the flipped class, judged by
  postcondition pass rate). I hold D3's P1/P5-before-S2 ordering: S2's
  checkpoint verification IS P5, and CB-1's split is part of P5's
  assert set for the flipped class. Flipping before P5/CB-1 means
  running code-exec with pixel-band verification only, which is the
  window CB-1 exists to close.
- Amendment 4 (step 9, A1/S3): the merged daemon/runner decision IS
  the CB-EXEC prototype decision. One prototype, implementing the
  CB-EXEC contract, on one live ws2 clone chat. B6 lifts on that
  proof. No separate CB-EXEC build alongside A1.

AMEND4 sequencing: CONTINUE, slower, per the owner 06:09 TWO TRACKS
rule. All four cross-responses and the draft agree, and CB adds
nothing to contradict it. Landed state, updated 06:43 +07: items 1-11
landed (V-F10); item 12 is the only outstanding item, in flight.
Triage per the draft (D1 order: first 5, 6, 7, 8, 12, then 9, 10;
item 11 anytime; items 1-4 done) stands. Items 5-6 landing closes
the A9 origin-staleness dependency. Item 12 landing closes A7/P4 and
CB-2 limb 1.

## 4. Acceptance test: the 100-held-out-tasks benchmark SUPPLEMENTS the ladder, it does not replace it

The draft's ladder (section 3): fixture 2-vision (required, first),
then live 0-vision on real ws2 clone chats as the final gate, live
2-vision as a diagnostic only (B1 lifted). CB's proposal (section 3):
100 held-out tasks across browser and desktop, new content and
layout, scored by task success end to end, with 90% defined as task
success and 96/100 required for 95% confidence.

CB's position: SUPPLEMENT, not replace. Three reasons, each with
numbers.

- Different axis. The ladder measures the DOM-first live path on one
  task class (clone chats): DOM harvest, plan, execute, DOM verify,
  accuracy at least 90% scored by DOM outcome. CB's benchmark measures
  generalization: held-out apps, desktop apps, side effects, recovery
  actions, model-call counts, crop counts, retry counts. The ladder
  cannot measure what it does not run, and CB's set cannot measure the
  live clone path, which needs P3 and clone coordination. Neither
  replaces the other.
- Readiness. The ladder's script exists (868 lines, now on
  todolist-push at c5311ce, 7f3a70b; the draft's V-A3 absence is
  closed) and its fixture run is the immediate next measurement.
  CB's 100-task set does not exist yet: no task list, no harness, no
  baseline, and CB's own estimate is days of work for an independent
  benchmark. A gate that does not exist cannot replace a gate that
  does. The 100-task benchmark becomes the acceptance gate for
  CB-EXEC as a general executor, run once the prototype exists,
  before any claim of 90% task success.
- The 90% bar is consistent, and CB's statistics are correct. The
  draft's live ladder defines 90% as DOM-outcome task success on the
  clone-chat class. CB defines 90% as end-to-end task success on 100
  held-out tasks, with 96/100 for 95% confidence. My recompute
  (V-F1): 96/100 Wilson lower bound 90.16%, 95/100 lower bound 88.8%.
  CB's 96/100 is right, and it also settles the draft's open point:
  the live ladder's run count is unspecified, so its 90% has no
  confidence attached. The ladder keeps its 90% bar; the 100-task
  benchmark supplies the statistical form for the general claim.

On B1: CB agrees with the lift's reasoning. In the bench design
VISION 1 is a DOM harvest, not a screenshot, and VISION 2 is a human
look; live 2-vision and live 0-vision-with-P9-screenshot are the same
machine behavior. CB's benchmark does not restore the live-2-vision
rung; it adds the held-out axis the ladder does not measure.

## 5. Section 4 unverified items: what the draft handles correctly, and what it does not

| Item (CB report section 4) | Draft handling | CB position |
|----|----|----|
| 66-rect / 5-click claim unverifiable from CB's checkout | CORRECT as a citation warning, INCOMPLETE as a step. Draft 0.2 applies C1: three reviews citing one measurement is one measurement. | Correct direction. Missing: no DOM-bench re-run is scheduled in the draft's order, and P2/A9/A1 verdicts still rest on the single measurement (clone2 batch 7, Marionette median 0.030 s). Add a re-run, or let the fixture bench run serve as the re-proof for the grounding path, before P2 lands. |
| SSH 95% of 12.26 s unverified | CORRECT on the S0 numbers, ONE annotation missing. Draft V-A6 settles fresh 4.43-5.29 s, mux 0.91-1.46 s, saving about 3.2-3.5 s per connection, about 3.5-5x; SPEED 460x dead. | The S0 correction is right. Gap: draft section 8 still quotes F2b "dispatch 11.620 s, 95%" without CB's caveat that the act-now JSONL cannot attribute that share to SSH specifically (logs start after the command arrives; another record shows service 11.611 s and gap 1208.942 s for many tasks, a different measurement). The 95% is F2b's dispatch share (SSH plus scp plus setup), not a pure-SSH share. CB-7's dispatch-split measurement is still owed. |
| Overlay flicker LIQUID unverified | NOT HANDLED. Draft has 0 hits for LIQUID (V-F8). No verdict, no owner, no step. | Missing. CB-10 ADOPT: probe (load the LIQUID plugin, reproduce flicker, count repaints) before A4's session-level pill is judged, or record an explicit deferral with an owner. |
| Think time unmeasured | CORRECT in direction. Draft P6 ADOPT with the spec fix (timestamp points, harness owner) and the S2 honest limit (30-60 s, 3-5x). | Correct direction. Gap: CB-7's first-pointer timestamp and target_breached redefinition are not named (V-F8, 0 hits for first_pointer). Add CB-7 to step 0 (Amendment 1). |
| 90% task success unproven | CORRECT in definition. Draft defines 90% as DOM-outcome task success and records the fixture gap (section 3: a fixture pass alone repeats the F1a/F2b pattern). | Correct definition. Gap: no statistical bar and no held-out set; the live ladder's run count is unspecified. CB's 100-task benchmark supplies them as a supplement (section 4). |
| Checkout behind 622 commits | NOT HANDLED. Draft has 0 hits for 622 (V-F8). | Missing. Note the count itself was per remote-tracking ref without a fetch (CB's own caveat); the material finding is drift, not the number. |
| Deployment drift finding 2.9 | NOT HANDLED as a verdict. Draft has 0 hits for manifest (V-F8). | Missing as a verdict; confirmed live by my probe (V-F7): installed first_action.py (23442 bytes) differs from the repo copy (33893 bytes); installed cu.py also differs, at laptop HEAD 3790901. CB-9 ADOPT with the manifest gate before any bench gate (Amendment 1). |

## 6. What probe evidence would change the CB verdicts

Probes are running in parallel; results are not in yet. Each row names
the probe, its current status at HEAD 2864be4, and what outcome flips
which CB verdict.

| Probe | Current status | Outcome that changes a CB verdict |
|----|----|----|
| P3 Brave relaunch (debugging port) | NOT-RUN (7b1006a, clone1 batch 9 open since 06:01, Brave untouched) | Pass (login intact, /json/list shows the Muse tab, one fill plus assert on a scratch input): CB-EXEC's CDP backend is viable for the clone chats. Fail (port refused AND Chromium migration too disruptive): CB-EXEC loses its CDP backend for the live task class; the prototype narrows to Zen Marionette-only and the live ladder re-plans around Zen only. Changes CB-EXEC's backend scope, not its contract. |
| Fixture 2-vision bench run | PASSED in 10.86 s (a1a672d, landed during this response); Y1b 3 fails still open, flag NOT flipped (gate b unmet) | The pass is in: DOM-first availability is confirmed on the fixture path; it strengthens CB-EXEC, P2, S2 and moves the fixture rung from pending to passed. No CB verdict letter changes: B2 still stands because the Y1b gate is unmet, which is exactly the S2 gating in section 3 (bench green PLUS Y1b fixes). The remaining unknown is the live run, which still needs P3. Had the bench failed on DOM harvest or the sent-bubble gate, CB-EXEC's DOM backend assumption would have needed re-proof and CB-1's severity would have risen. |
| S2 pilot / one-class flip measurement | Probe-s2 brought the bench onto the branch; flip not run | Code-exec shows ok=True without a postcondition (Y1b 2b reproduced live): CB-1 becomes a hard gate, which is already my position. Code-exec already verifies postconditions for the flipped class: CB-1's urgency drops for that class; the desktop_act instance still stands. |
| P6 vision-call measurement | In draft step 0, not yet run | Vision read is seconds (expected): CB's model-call-count case stands. Vision read under about 1 s: the speed case for DOM-first weakens; the accuracy case is unchanged (58.6% first-try, G30 64/75 px still stand). |
| DOM bench re-run (clone2 numbers) | Single-source (clone2 batch 7, Marionette median 0.030 s, 66 rects, 5 clicks) | Reproduces: the single-source caveat is cured; P2/A1 timings stand. Fails to reproduce: P2/A1/CB-EXEC timings are recomputed; the prototype gate is unchanged (the prototype must prove itself live anyway). |
| LIQUID overlay probe | Not run; plugin not loaded per the todolist record | Flicker reproduces with the plugin loaded: overlay work becomes a real item; A4 sequencing gains a flicker gate. No flicker: CB-10's overlay limb closes. |
| SSH dispatch split (VM to laptop, same workload, fresh vs reuse) | Not run; CB-7's prescription | SSH is about 95% of order-to-overlay: CB-7's unverified softens to confirmed; S0 priority rises. Dispatch dominated by non-SSH (scp, Python startup, Tailscale handshake): S0 saving shrinks; S1/A1 priority rises. |
| Y1b fixes (1e, 2a, 2b) | BLOCK stands (9d9bd63, 14/20, 3 real fails) | Fixed: B2 lifts; S2 flip proceeds. CB-1's code-exec instance closes; the desktop_act instance remains. |
| P8 Zen chrome context probe | RETURNED (3790901): BLOCKED without a Zen restart (HTTP 500, MOZ_REMOTE_ALLOW_SYSTEM_ACCESS required), C12 reproduced live | Already incorporated (V-F9, Amendment 2): CB-EXEC keeps screenshot-crop for Zen chrome UI. If a later probe with an owner-approved restart succeeds, the chrome-UI fallback can be replaced by Marionette chrome. |
| AMEND4 item 12 (A7/P4) | In flight on two lanes | Lands: closes A7/P4 and CB-2 limb 1. The planned-action scope case in CB-2 still needs the scope-plus-observation-ID rule. |
| CB-EXEC prototype on one live ws2 clone chat | Not built | Pass (postconditions verified, no false ok): B6 lifts; the A1/S3/CB-EXEC decision is made. Fail (false ok persists, or postconditions cannot be defined for the task class): CB-EXEC's contract needs revision; which postconditions are definable per action type becomes the open question, in the same shape as P5's exception list. |

## 7. What STOPS (CB position)

- The S2 one-class flip stops until B2 lifts (Y1b 1e/2a/2b fixed,
  fixture bench green) AND CB-1 lands for the flipped class
  (verified/input_sent split, judged by postcondition pass rate).
- P2 stops until the stale-ref disagreement protocol is specified
  (B5 protocol limb; the items 2-4 limb is satisfied at HEAD 2864be4).
- The A1/S3/CB-EXEC daemon decision stops until the prototype proves
  snapshot/execute/verify plus postconditions on one live ws2 clone
  chat (B6).
- Any benchmark quoted as a release gate stops until the CB-9 manifest
  exists (source commit plus installed artifact hashes plus log for
  the build that ran).
- Live-task migration to CDP stops until P3 passes (Brave port, login
  intact, one fill plus assert on a scratch input).
- Deletions (A3/A4/A5) stop until their replacements prove (B3/B4),
  per the draft.
- A live 0-vision run stops until P3 closes and owner approval per run
  is given (draft A10 staging, agreed).
- The CB-EXEC prototype itself does not stop on cost: under 06:07 cost
  is irrelevant, and the prototype is the existence proof the whole
  program is gated on.

## 8. Evidence index

- CB report: improvements/codex-breakthrough-report.md (2596287, 138
  lines, Vietnamese). Launch log:
  improvements/worker-codex-breakthrough-log.md (Codex PID 781223,
  launched 06:04:15, report written 06:20, about 16 min wall).
- Draft: improvements/worker-click3-adjudication-log.md (9d23834).
- ARCH (074c1d7), GROUNDING (d1fc4e9), SPEED (a4ecb49).
- D1 (37f457e), D2 (6d1bf04), D3 (14fc139), RTD (e96b2ff).
- X1 (0cf601c), X2 (d5b205d), X3 (2b0c73c), XRT (6cb3f95).
- Y1b BLOCK: commit 9d9bd63 (14/20, 3 real fails 1e/2a/2b).
- AMEND4 landed, updated 06:43 +07 to HEAD 8d0e38a: item 1 cc964b2,
  item 2 c1ea773, item 3 62b740e, item 4 72120aa, items 5-6 b44a5ea,
  item 7 49081aa, item 8 af0fa87, item 9 44c15bb, item 10 e912ad4,
  item 11 8d75135; item 12 only outstanding, in flight.
- Fixture 2-vision bench PASS: a1a672d, 10.86 s, Y1b 3 fails still
  open, flag NOT flipped (gate b unmet).
- Parallel final responses landed during this response: farch c3bf5e0
  (CB-EXEC merged into Layer 0), fspeed e7562ca (460x conceded, S1/S2/D6
  gated, CB-4/CB-6/CB-7/CB-8 answered), fground 8d0e38a (P8 closed, P2
  expanded per CB-5).
- Bench on todolist-push: c5311ce (tests/two_vision_bench.py, 868
  lines), 7f3a70b (tests/two_vision_fixture.html, 48 lines).
- Probe-p3 NOT-RUN: 7b1006a (clone1 batch 9 open since 06:01).
- Probe-p8 returned: 3790901 (chrome context BLOCKED without Zen
  restart, HTTP 500, MOZ_REMOTE_ALLOW_SYSTEM_ACCESS required).
- My verifications this session: Wilson 17/29 40.7%-74.5%, 96/100
  90.16%-98.43%, 95/100 lower 88.8%, 0.9^20 12.16%, 0.9^32 3.43%;
  cu.py:2113 pixel-hash disclaimer; first_action.py:470
  order_to_overlay from wrapper start, :478-498 G28 loud refusal
  enforced, :552-563 envelope ok pass-through, :661 unconditional
  observe_screen after-capture; a11y.py:208 do_action true as done;
  grep session_remote|Broker 0 hits in first_action.py and cu.py;
  code_exec.py:134 CU_CODE_EXEC gate; laptop live drift check 06:40
  +07 (installed first_action.py 23442 bytes differs from repo
  33893 bytes; installed cu.py differs; laptop HEAD 3790901);
  draft grep 0 hits for liquid, 622, manifest, first_pointer.
- Numbers used: vision 17/29 first-try 58.6%, pointer error 0.5-0.9
  px; G30 clicks 64 px and 75 px above the real field; J40 offset
  (+45,+12) px (CB-cited); J37 patch 6.627 vs threshold 6 (CB-cited);
  DOM 66 rects Marionette median 0.030 s, 5 clicks all landed, verify
  0.002-0.015 s (single-source, clone2 batch 7, C1 applies); fresh SSH
  4.43-5.29 s, mux 0.91-1.46 s, saving about 3.2-3.5 s per connection,
  about 3.5-5x (460x dead); act-now JSONL 199 lines, p50
  order-to-overlay 337.5 ms, max 368.4 ms, wrapper p50 2.288 s, max
  6.95 s, 167 ok true, 32 false, 195 session, 4 fallback, 0 timeout,
  5 captured (CB synthesis, taken as reported); overlay acquire
  315-349 ms; F2b order-to-overlay 12.262 s, dispatch 11.620 s (F2b's
  dispatch share, not a pure-SSH share, see section 5).
