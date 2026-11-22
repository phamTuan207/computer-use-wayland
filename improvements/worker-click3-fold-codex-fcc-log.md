# Worker CLICK3-FOLD: fold of the Codex and FCC discussion positions into the FINAL direction

Owner: the owner. Role: fold worker (Worker CLICK3-FOLD) for COORD-CLICK-3.
Task: the final direction is already decided (commit e05fc58). I do NOT
re-decide it. Two discussion positions landed after it. I check whether
either changes any verdict, order step, acceptance criterion, or
execution step. The bar for a change is evidence: a position changes
the direction only if it brings measured evidence or a verified
code/source finding the finalizer did not have. An opinion without
evidence does not change a verdict. One exception, stated in the brief:
the final direction leaves the plateau numbers as an open condition
owned by the coordinator, so a concrete plateau proposal may fill that
open condition; filling a delegated open condition is not overturning
a verdict.

Rules honored: no em dash (U+2014) or en dash (U+2013) anywhere in
this file. No personal info. Evidence with every claim (Lauren Tan
standard: test command, output, commit hash, time log). Commit with an
EXPLICIT pathspec immediately after staging, never plain git commit,
never git add -A. Verify push with git ls-remote. Never ydotool. First
principles (06:01). No self-healing question arises: this is a fold,
not a fix of my own work.

Times are Asia/Ho_Chi_Minh wall-clock, with elapsed time from task
start at 07:00 +07 on 2026-11-22.

## 0. What I verified myself in this session

- 07:00 +07 (T+0m): task received. Repo ~/workspace/computer-use-wayland,
  branch todolist-push. `git log --oneline -20` confirms the landing
  order: e05fc58 (final direction) is the parent-era commit, then
  3d55646 (fcc discuss) and 8008662 (codex discuss) landed on top of
  0668327. Both positions landed AFTER the finalizer, as briefed.
  Current HEAD at writing: 8008662.
- 07:00-07:03 (T+0-3m): read in full the final direction
  (improvements/worker-click3-final-direction-log.md, e05fc58, 1073
  lines), the Codex position (improvements/codex-discussion-position.md,
  8008662, 126 lines), the FCC position
  (improvements/fcc-discussion-position.md, 3d55646, 78 lines), and
  both driver logs (worker-codex-discuss-driver-log.md,
  worker-fcc-discuss-driver-log.md).
- 07:03-07:08 (T+3-8m): my own spot checks (section 0.1). All numbers
  below are recomputed or re-grepped by me in this session, not copied
  from any position file.

### 0.1 Spot checks run by me in this session (new verification)

- V-F1. Wilson arithmetic recomputed with python3 (math, z=1.959964):
  17/29 = 58.62 percent, Wilson 95 percent interval 40.74-74.49;
  96/100 Wilson 95 percent lower bound 90.16, interval 90.16-98.43;
  27/30 Wilson 95 percent lower bound 74.38, interval 74.38-96.54;
  54/60 Wilson 95 percent lower bound 79.85, interval 79.85-95.34.
  Codex's recomputations (17/29 = 58.62 percent, Wilson 40.74-74.49;
  96/100 lower bound 90.16) are CORRECT. The 27/30 and 54/60 figures
  are mine, used in the plateau decision (section 3, D-1).
- V-F2. SSH savings arithmetic recomputed: D1 pairing 5.29 minus 1.18
  = 4.110 s, ratio 4.48x; D3 pairing 4.447 minus 1.266 = 3.181 s,
  ratio 3.51x; PROBE-S0 pairing 4.667 minus 1.339 = 3.328 s, ratio
  3.49x. Codex's two pairings (3.181 s / 3.51x and 4.110 s / 4.48x)
  are CORRECT arithmetic on the cited probe numbers. The final's
  single figure (3.328 s / 3.49x, PROBE-S0 interim 90eb8be) sits
  inside Codex's range. No contradiction.
- V-F3. AMEND4 item 12 IS landed in the current tree, and Codex's
  "fix NOT landed" premise is REFUTED. `grep -n observe_screen
  scripts/first_action.py` returns lines 381 and 735 only. Line 381
  is inside `_fresh_observation` (the fresh-capture default, not the
  envelope after). Line 735 is the `after_screen` capture
  (verification-only). The envelope `after` is scope-matching via
  `_scope_after` (defined line 328, called line 743), and
  `after_screen` is set at lines 737-739. `git merge-base
  --is-ancestor cbab398 HEAD` confirms cbab398 is an ancestor of HEAD.
  Codex read laptop HEAD 3790901, where line numbers differed and the
  laptop tree lagged; on the current tree the both-fields shape is in
  place. The final's A7 ADOPT (landed, tests to run) stands.
- V-F4. Codex's four bench findings VERIFIED from the current tree
  (`tests/two_vision_bench.py`): (a) hardcoded absolute paths at
  lines 49-53 (FF, GD, FIXTURE, FIXTURE_DIR under /home/hatch) and
  line 310 (geckodriver log /tmp/two_vision_geckodriver.log) and line
  53 (DEFAULT_WORKDIR /tmp/two_vision_bench); (b) `--instances two`
  REFUSED at lines 696-697; (c) no P9 screenshot is saved by the
  script: VISION 2 is described as the agent looking at threads (line
  826) and `finish()` (lines 855-863) writes only results.json; (d)
  `wall_s` is `time.monotonic() - t_start` of the Python process only
  (line 858), excluding model and transport outside the process. All
  four are real source findings the finalizer did not record in this
  detail. They change no verdict (section 3, D-3).
- V-F5. Eval-removal parity check (Codex CB-10 gate): repo-wide grep
  for callers of the `zen_dom.py eval` CLI subcommand returns NO
  production caller. The only hits outside scripts/zen_dom.py itself
  are discussion logs and the contract doc
  (docs/layer0-cbexec-contract.md:574, which already records the
  removal). The internal `evaluate()` stays as the transport for
  harvest, locate, and hit_check (zen_dom.py:587, 593, 610, 691, 832,
  859, 889), exactly as the final's P2 row states. One live use in a
  log (worker-ztc-blind-run-log.md:75) is an ad-hoc diagnostic, which
  is the intentional-debug-mode use the final preserves. Codex's
  parity gate therefore has no blocking in-tree dependency. The
  final's step-0 removal stands (section 3, D-6).
- V-F6. FCC's independent verifications corroborated, not re-measured
  by me: SSH mux 0.91-1.46 s vs fresh 4.43-5.29 s (consistent with
  PROBE-S0 fresh mean 4.667 s n=10, mux mean 1.339 s n=18);
  MutationObserver exists in zen_dom.py (lines 954, 993) and
  `arm_typed_flag` is called from production code at dom_act.py:483-484
  (zen_dom.py:948 defines it). Both match the final's V11 settlement.
  No contradiction with any final verdict.
- V-F7. PROBE-S1 exists as commit 1af7330 with the message "probe-s1:
  broker batch proven live from VM, 12.11s vs one-shot 28.70s". The
  finalizer read its log (V-Z3: broker core batch 12.110 s vs one-shot
  28.700 s, delta 16.590 s, 2.37x). Codex's S1 MODIFY gate (one batch
  VM end to end, serialize or refuse on contention, latency phases,
  spawn kept as fallback) is the gate PROBE-S1 satisfies. Codex wrote
  before PROBE-S1 landed; its S1 verdict is superseded by that
  evidence, not by opinion.
- V-F8. FCC run 2's one independently verifiable claim checks out:
  the Codex report does propose measuring on 100 held-out tasks with
  90 percent task success and a Wilson interval (codex-breakthrough-report.md,
  proof plan section), as the FCC driver already verified. The CB
  ADOPT row in FCC's file is grounded in the report on that point.

### 0.2 A numbering trap, stated once so no row is miscompared

Codex numbers its CB rows by the Codex report's section 3 fields:
CB-1 to CB-6 are Target, Scope, Preconditions, Input, Postcondition,
Retry; CB-7 is backend choice; CB-8 is the model/executor split;
CB-9 is the merged session/results/image/coords bundle; CB-10 is the
zen_dom eval limit. The final direction numbers its CB rows by the
report's ten proposal items (CB-1 three-part contract, CB-2 scope,
CB-3 taxonomy/uniformity/J37, CB-4 batch math, CB-5 routing/eval,
CB-6 long-lived session, CB-7 latency, CB-8 evidence discipline,
CB-9 manifest, CB-10 flicker). The two CB numberings DO NOT align.
Every CB comparison below maps by CONTENT, never by number. A naive
number-to-number comparison would manufacture disagreements that do
not exist.

## 1. Codex position vs the final direction, per proposal

Codex tally: ADOPT 19, MODIFY 21, REJECT 0, over 40 rows (30 draft
proposals plus 10 CB rows under Codex's own numbering). Final tally:
ADOPT 19, MODIFY 20, CLOSED 1, REJECT 0 in full. Headline: Codex
agrees with the final on 36 of 40 rows in substance. The four
substantive disagreements are S1, Codex CB-2 (scope), Codex CB-5
(postcondition), and Codex CB-10 (eval). Each is decided in section 3.

### 1.1 ARCH A1-A10

| ID | Final | Codex | Agree? | Note |
|----|-------|-------|--------|------|
| A1 | MODIFY | MODIFY | Yes | Same gate: pilot live snapshot/execute/verify before any deletion; B6 stands. |
| A2 | ADOPT | ADOPT | Yes | Codex adds the Zen chrome clarification (screenshot stays, P8 blocked). Final already has it as a sequencing constraint. |
| A3 | MODIFY | MODIFY | Yes | Same gate: driver holds scope, cancel, lock first. |
| A4 | MODIFY | MODIFY | Yes | Same staged sequence; server deleted only after crash/clear proof. |
| A5 | MODIFY | MODIFY | Yes | Same: broker default after proof, fresh SSH kept as fallback and recovery. |
| A6 | ADOPT | ADOPT | Yes | Same: transport only, files stay as audit. |
| A7 | ADOPT | ADOPT | Yes in verdict; premise stale | Codex says the fix is NOT landed at laptop HEAD 3790901 (first_action.py 661-665 still observe_screen). REFUTED on the current tree (V-F3): item 12 cbab398 is landed, envelope after is scope-matching. The verdict agrees; the premise does not survive. No change. |
| A8 | MODIFY | MODIFY | Yes | Same: band stays diagnostic until per-action DOM asserts exist. |
| A9 | ADOPT | ADOPT | Yes | Same, structured targets only, origin/scale re-read per ground. |
| A10 | MODIFY | MODIFY | Yes in label | Reasons differ and both matter: final's MODIFY is the 3-rung ladder (fixture passed a1a672d pending manifest, live 0-vision final gate, 100-task general gate). Codex's MODIFY is that the bench is not ready as an acceptance runner (Marionette-only, refuses instances=two, hardcoded paths, no P9 save, wall_s excludes model/transport). Codex's four bench findings are VERIFIED (V-F4) and are recorded as repair items on the rung-1 manifest lock (section 3, D-3). No verdict change. |

### 1.2 GROUNDING P1-P9

| ID | Final | Codex | Agree? | Note |
|----|-------|-------|--------|------|
| P1 | ADOPT | ADOPT | Yes | Same router, fail closed, per-target proof; Zen chrome and Brave stay screenshot until their probes pass. |
| P2 | MODIFY | MODIFY | Yes | Same: stale-ref protocol first; items 2-4 landed; protocol is the remaining B5 limb. |
| P3 | ADOPT as experiment, CONDITIONAL as live path | ADOPT as probe | Yes in substance | Codex: NOT-RUN, needs a quiet window. Final: same, plus P3 gates only the step-11 live run, not steps 3-6 (FGROUND C-O2). |
| P4 | ADOPT | ADOPT | Yes | Same both-fields shape; regression for item 12 still owed. |
| P5 | MODIFY | MODIFY | Yes | Same: mandatory per action type as its assert lands, exception list, band stays diagnostic. |
| P6 | ADOPT | ADOPT | Yes | Same two timestamp points; capture ms is not model locate time. |
| P7 | MODIFY | MODIFY | Yes | Same: Marionette-only sufficiency first, handover only if a task genuinely needs two protocols. |
| P8 | CLOSED | ADOPT | Yes in substance | Label differs only. Codex ADOPTs the probe result (BLOCKED, HTTP 500, restart needed). Final CLOSED records the same answered probe. Zen chrome stays screenshot-only in both. |
| P9 | ADOPT | ADOPT | Yes | Same: one final screenshot as unscored human evidence; Codex adds the script does not save it yet (V-F4), which the final's P9 hard condition already requires for rung 2. |

### 1.3 SPEED S0-S3, deletions D1-D6

| ID | Final | Codex | Agree? | Note |
|----|-------|-------|--------|------|
| S0 | ADOPT | ADOPT | Yes | Numbers refined, verdict unchanged (D-5): Codex's pairings give 3.181 s / 3.51x and 4.110 s / 4.48x; final's PROBE-S0 figure is 3.328 s / 3.49x, inside that range. 460x dead in both. |
| S1 | ADOPT (proof met) | MODIFY (proof-first) | No in label; resolved by evidence | Codex's gate is exactly what PROBE-S1 (1af7330) proves: one batch VM end to end, 12.110 s vs 28.700 s, 2.37x. Codex wrote before PROBE-S1 landed. The MODIFY is superseded, not overruled. No change to the final's ADOPT. |
| S2 | MODIFY | MODIFY | Yes | Same gates: fixture green (met), 3 Y1b fails fixed (open), CB-1 gate, plateau defined first, one class with fallback. |
| S3 | MODIFY | MODIFY | Yes, plus concrete numbers | Same merge into A1/CB-EXEC. Codex adds the plateau definition (2 cohorts of 30, at least 90 percent outcome, median e2e above 10 s). ADOPTED as the fill for the open condition (section 3, D-1). This is the one change in this fold. |
| D1 | ADOPT | ADOPT | Yes | Same: fresh SSH dies as the default, stays as fallback. |
| D2 | ADOPT | ADOPT | Yes | Same: scp dies as transport, files stay as audit. |
| D3 | MODIFY (deletion gated on five conditions) | MODIFY | Yes in substance | Codex's MODIFY is the proof-first form; the proof is met (PROBE-S1) and the deletion conditions sit at final step 8. |
| D4 | ADOPT | ADOPT | Yes | Same both-fields shape. |
| D5 | MODIFY | MODIFY | Yes | Same: one class first, stepwise fallback for unknown shapes. |
| D6 | MODIFY | MODIFY | Yes | Same: drop age refusal for DOM paths only; keep future-clock refusal and the pixel window. |

### 1.4 CODEX-BREAKTHROUGH, content-mapped (see 0.2)

| Codex row | Content | Codex | Final row (content match) | Final | Agree? |
|-----------|---------|-------|---------------------------|-------|--------|
| CB-1 | Target by role/name/ref from a fresh snapshot; non-unique selector is a refusal | ADOPT | CB-5 locate confirmations (MODIFY, definitions owed) + P2 + A9 | MODIFY | Yes in substance. The target principle is adopted; the final's MODIFY is about unmeasurable "stable"/"unique" wording, which Codex does not define either. |
| CB-2 | Scope (window/tab/frame + observation ID) bound to every ref; refuse scope mismatch or expired snapshot | ADOPT | CB-2 scope mandatory | MODIFY | No on prescription. Final rejects the blanket stop: re-ground first (0.030 s DOM re-read), stop only on ambiguity. Decided in D-6, no change. |
| CB-3 | Preconditions: unique, visible, enabled, right window; re-read geometry/focus close to input | ADOPT | CB-5 locate confirmations + P5 preconditions (EX1) | MODIFY | Yes in substance. Same requirement set; final's MODIFY is the definitions-owed qualifier. |
| CB-4 | Real mouse/keyboard or fitting API per control; no default DOM set_value/click for everything | MODIFY | CB-EXEC real-input default (inside MODIFY prototype-only) | MODIFY | Yes. Same rule: real input default, DOM click only where equivalence is proven per control type. |
| CB-5 | Postcondition per action (new bubble, URL, checked, value) | ADOPT | CB-1 three-part contract | MODIFY | No in label; yes in substance. Final folds the contract into P5/A8 with the exception list and same-commit envelope migration. Codex does not address the two blockers (caller migration, actions with no cheap postcondition). Decided in D-6, no change. |
| CB-6 | Retry only when the executor knows input was surely unsent; if uncertain, re-read state first | ADOPT | CB-EXEC retry rule + CB-1 input_sent/verified split | MODIFY | Yes in substance. Codex's re-read-first refinement is consistent with the final, which demands the prototype prove the retry rule on a destructive-action test (no double-send). |
| CB-7 | Route DOM/BiDi/CDP per proven target class, AT-SPI for a11y, screenshot crop for canvas; P8 blocked, P3 undetermined; one owner per Zen session | MODIFY | CB-5 routing half (folded into merged build) + P1 + P7 | MODIFY | Yes. Same routing discipline and same single-owner rule. |
| CB-8 | Model picks target/hard branch; executor does stable steps with checkpoints after nav/focus change; multi-op program only when postconditions prove the target still valid | MODIFY | CB-4 batch validity (fold into P5/CB-EXEC) + S2 | MODIFY | Yes. Same validity rule; no 32-op cap on a stale image in either. |
| CB-9 | Merge session/broker/input/overlay under one owner; input_sent separate from verified=true; coords inside the adapter | MODIFY | CB-6 (ADOPT, merged into S1) + CB-EXEC (MODIFY prototype-only) | ADOPT/MODIFY | Yes in substance. Codex's gate (prove serialized ownership, cancel/lock, recovery, pill, one session per browser before building a mega-driver) is the final's prototype gate. |
| CB-EXEC | Semantic transaction executor as the main direction for structured controls | MODIFY | CB-EXEC | MODIFY prototype-only | Yes. Same MODIFY: prototype authorized, full build not authorized on zero running evidence. |

### 1.5 Codex order of work vs the final order

Codex's 12 steps: (1) S0 + P6; (2) AMEND4; (3) fixture portability fix then bench; (4) Y1b fixes; (5) P3 in a quiet window; (6) P1/P5 + P7; (7) S1 proof; (8) plateau definition then S2 flip; (9) stale-ref protocol then P2/A9; (10) A1/S3 prototype only if plateau; (11) deletions; (12) final acceptance.

Differences from the final order (steps 0-11), all explained by
evidence that landed after Codex's read or by decisions already in
the final:
- Codex puts the S1 proof (its step 7) before the S2 flip (its step 8).
  The final satisfies this in time: PROBE-S1 (1af7330) already proved
  the broker path before the final was written, and the S2 flip is
  final step 6 while only the S1 deletion conditions sit at step 8.
  "S1 proof before S2" is met. No order change.
- Codex puts the fixture bench (its step 3) before the Y1b fixes.
  The final's bench already PASSED (a1a672d, 10.86 s), so the final
  goes straight to the Y1b fixes at step 4. No order change.
- Codex puts P3 at its step 5. The final attempts P3 at the first real
  quiet window in step 2 and gates ONLY the step-11 live run on it
  (FGROUND C-O2, adopted). No order change.
- Codex's acceptance (100 new tasks, split across two clones/browsers
  and multiple sessions, Wilson 95 percent lower bound at least 90
  percent needs at least 96/100, 0 screenshot-grounding not 0 model
  call, P9 saved unscored, per-phase timing, baseline vs semantic
  arms interleaved) matches the final's rung 2 + rung 3 combined,
  with the same 96/100 bar (verified in V-F1). The final keeps rung 2
  (chat class) and rung 3 (general) separate and sequenced live first
  (section 2 item (g)); Codex does not separate them, but nothing in
  Codex's text argues against the separation. No acceptance change.

## 2. FCC position vs the final direction, per proposal

FCC run 1 tally: ADOPT 15, MODIFY 14, REJECT 0, CB PENDING (30 rows).
FCC run 2 changes one row: CB PENDING to ADOPT (single row covering
the semantic transaction executor, broker consolidation, and the
100-task proof plan). Run 1 is row-for-row IDENTICAL to the adjudication
DRAFT (9d23834), as its own driver log records; it states no
disagreement with the draft anywhere. The final direction supersedes
the draft in full, on evidence that landed after run 1 (PROBE-S1,
PROBE-S2 bench pass, PROBE-P8 closed, plus the F1/F2/F3/FRT round).

### 2.1 FCC run 1 rows vs the final

Agree in substance (26 rows): A1 MODIFY, A2 ADOPT, A3 MODIFY, A4
MODIFY, A5 MODIFY, A6 ADOPT, A7 ADOPT, A8 MODIFY, A9 ADOPT, P1 ADOPT,
P2 MODIFY, P3 ADOPT, P4 ADOPT, P5 MODIFY, P6 ADOPT, P7 MODIFY, P9
ADOPT, S0 ADOPT, S2 MODIFY, S3 MODIFY, D1 ADOPT, D2 ADOPT, D4 ADOPT,
D5 MODIFY, D6 MODIFY. (P8 is counted under disagreements below only
for its label; see the next paragraph.)

Disagreements (4 rows), each decided in section 3:
- A10: FCC ADOPT vs final MODIFY (3-rung ladder). FCC offers no
  per-proposal evidence and does not engage the ladder reasoning
  (F1/F2/FRT) or Codex's verified bench findings. No change (D-8).
- P8: FCC ADOPT (as probe) vs final CLOSED. Substance agrees: the
  probe answered BLOCKED and Zen chrome stays screenshot-only.
  Label only. No change.
- S1: FCC MODIFY (proof-first) vs final ADOPT (proof met by PROBE-S1,
  1af7330, landed after run 1). The gate FCC states is satisfied by
  evidence run 1 did not have. No change.
- D3: FCC MODIFY vs final ADOPT (deletion gated on five measured
  conditions at step 8). Same situation as S1: the proof is met, the
  deletion conditions remain. No change.
- CB: run 1 PENDING, closed by run 2 ADOPT (section 2.2).

### 2.2 FCC run 2 (Codex follow-up) vs the final

Run 2 gives three verdicts and one row: semantic transaction executor
ADOPT, broker consolidation ADOPT, proof plan (100 held-out tasks)
ADOPT; CB row PENDING to ADOPT. It agrees with Codex on the ten
weaknesses but discusses only 2.1 (reporting success on input
submission) and 2.2 (scope changes) by name. It states no change to
the order of work or to B1-B6 (B1 lifted, B2-B6 stand), which matches
the final's blocker statuses exactly.

Against the final's per-row CB adjudication (section 8 of e05fc58),
run 2 is coarser, not contradictory: it does not give per-weakness
verdicts for 2.3-2.10, does not rule on the reuse/merge details (Zen
adapter under one contract, snapshot-bound target refs, desktop_act
ok to input_sent, removing unrestricted zen_dom eval), and does not
answer whether Codex re-measures independently or cites the same
evidence base second-hand. It does not engage FRT's six findings
against the full CB-EXEC build (zero lines built, single-session
concentration risk, circular retry rule, disproportionate benchmark
with a decorative independence assumption, absorption of the staged
order, unproven schedule). A single-row ADOPT of a whole report cannot
overturn a per-row adjudication that rests on those findings. The
parts of run 2 that carry evidence point the same way as the final:
broker consolidation ADOPT matches final CB-6 ADOPT (merged into S1),
and the 100-task proof plan ADOPT matches final rung 3 (96/100,
Wilson lower bound about 90.2 percent, sequenced after rung 2).
No verdict change (D-8).

### 2.3 FCC defects and their effect

The FCC driver log flags four defects in the position file, kept
verbatim and not silently fixed. I record them here with their effect
on this fold:
- (a) Run 2 header times are WRONG: "Start time: 2026-11-22 10:20
  +07, Finished time: 2026-11-22 10:45 +07", but run 2 actually ran
  06:48-06:54 (file mtime 06:54, log DONE 06:55). Same future-time
  fabrication as run 1 (header said finished 07:15, file written
  06:38). True times: run 1 06:36-06:38, run 2 06:48-06:54.
  Effect: provenance only. The verdicts are unaffected; the file's
  timestamps must not be quoted as a time log. No effect on any
  verdict, order step, acceptance criterion, or the AMEND4 close-out.
- (b) The stale verification line "Verified
  codex-breakthrough-report.md PENDING status and that no proposals
  are present to adopt" is STILL in the file, contradicting the new CB
  ADOPT row. Effect: internal inconsistency in FCC's file. The CB
  ADOPT row is the operative verdict (grounded in the report per
  V-F8). No effect on the direction.
- (c) Run 2 coverage is partial (section 2.2): no per-weakness
  verdicts for 2.3-2.10, no reuse/merge or eval verdicts, no answer on
  re-measurement vs second-hand citation. Effect: run 2 cannot serve
  as the cross-examination of the CB rows. The final's section 8
  cross-examination (F1/F2/F3/FRT plus the finalizer) stands as the
  operative one. No effect on the direction.
- (d) Run 1 verdicts are row-for-row identical to the draft with no
  stated disagreement. Effect: run 1 adds independent verification
  (SSH timings, MutationObserver existence, after-image trap; all
  corroborated in V-F6 and V-F3) but no independent divergence. A
  position that repeats the draft cannot move a final that superseded
  the draft on newer evidence. No effect on the direction.

None of the four defects touches AMEND4 items, test evidence, probe
results, or any verdict. The AMEND4 close-out (final section 6
worker 3: run the four item-12 regression tests, confirm the
Codex-lane item-12 delivery, round-3 patch-vs-rewrite judgment plus
defective-test repair for items 3, 4, 5-6) is UNAFFECTED. No FCC
re-run is commissioned: run 2's substance is already carried by the
final's CB-6 ADOPT and rung 3, and its gaps are covered by the
final's section 8.

## 3. Decisions (change or no change, with the deciding evidence)

### D-1. Plateau: ADOPT Codex's 2x30 @90 percent. THE ONE CHANGE.

Decision: the plateau definition is now FIXED as follows, closing the
open condition in final section 2 item (e) and section 7:
- Target: live median end-to-end wall time above 10 s (the SPEED
  program target, measured the same way as rung 2: from the task
  being given to the DOM-verified outcome, including transport,
  model, observe, act, and verify).
- Cohorts: TWO independent cohorts of 30 NEW held-out tasks each
  (not repeats of one session, not the fixture set).
- Trigger: plateau is called ONLY if BOTH cohorts reach at least 90
  percent task outcome (at least 27 of 30 each) AND the live median
  end-to-end wall time is still above 10 s in both cohorts.
- If accuracy is below 90 percent in either cohort, that is an
  accuracy failure, not a speed plateau: fix accuracy first, do not
  build the prototype.
- The trigger authorizes the step-9 A1/S3/CB-EXEC merged prototype.
  It does not authorize the merge; the merge is decided on the
  prototype's measured evidence.

Why this is adopted (evidence, not deference):
- The final direction DELEGATED the numbers to the coordinator
  (section 2 item (e): "the coordinator defines the numbers";
  section 6 worker 8; section 7). This fold is the coordinator's
  delegated decision point, and the brief names this exact proposal
  as a possible fill. Filling a delegated open condition is not
  overturning a verdict.
- The numbers are the final's own bars, not new inventions: 10 s is
  the SPEED stated target; 90 percent is the final's rung-2 live-gate
  bar (90 percent task success, DOM-scored). Codex proposes nothing
  the final does not already use.
- The two-cohort structure guards the exact failure mode the HARD
  GATE exists to prevent: a single bad run (or a single good run)
  triggering or blocking the prototype decision. Both cohorts must
  clear 90 percent, which is stricter than one 60-task pool at 90
  percent.
- Arithmetic verified by me (V-F1): 96/100 gives Wilson 95 percent
  lower bound 90.16, which is the rung-3 bar and is unchanged.

Precision notes, recorded so the trigger is never misquoted:
- The plateau trigger is a POINT-ESTIMATE rule, not a confidence
  claim. Wilson 95 percent lower bound for 27/30 is 74.38 percent,
  and for 54/60 is 79.85 percent. Nobody may quote the plateau
  trigger as "90 percent with 95 percent confidence". The 95
  percent confidence bar lives only in rung 3 (96/100, lower bound
  90.16).
- The fixture bench baseline (10.86 s, a1a672d) is process-only time
  (V-F4: wall_s excludes model and transport). It must NOT be used as
  the live-time baseline. The 10 s threshold comes from SPEED's
  stated target, not from the fixture number. The final's section 2
  item (e) instruction to define numbers "from the fixture bench
  baseline (10.86 s) plus first live runs" is corrected on this
  point: the threshold is 10 s from SPEED; first live runs confirm
  the measurement, they do not re-derive the threshold.
- If the first live runs after the S2 flip already show median at or
  below 10 s, there is no plateau by definition and no prototype
  triggers. That is the intended semantics, not a reason to re-open
  the threshold.

Effect: section 2 item (e) open condition CLOSED with these numbers;
section 6 worker 8 becomes "apply the 2x30 @90 percent plateau
definition" instead of "define the numbers"; section 7 plateau row
changes from "owner COORD-CLICK-3 defines" to "defined: 2 cohorts
of 30, at least 90 percent outcome each, live median above 10 s".
No verdict changes, no order changes, no acceptance-bar changes.

### D-2. "S1 proof before S2": NO order change. Already satisfied.

Codex's ordering demand is met in time: PROBE-S1 (1af7330) proved
the broker path (12.110 s vs 28.700 s, 2.37x) before the final was
written, and the S2 flip is final step 6 while only the S1 deletion
conditions sit at step 8. Codex's S1 MODIFY gate is satisfied by
evidence Codex did not have when it wrote (V-F7). The final's S1
ADOPT stands. The queue discipline Codex and CB-6 both require is
still specified at step 8, as the final already orders it.

### D-3. Codex's A10 bench findings: VERIFIED, no verdict change.

All four findings check out against the current tree (V-F4):
hardcoded tool/fixture paths (lines 49-53, 310), `--instances two`
refused (lines 696-697), no P9 screenshot saved (only results.json),
wall_s is process-only (line 858). They do not change A10 MODIFY
(the final already gates rung 1 on the CB-9 manifest and already
requires per-phase timing and a reviewed P9 screenshot for rung 2).
They are recorded here as concrete items on the rung-1 manifest lock,
owned by the deploy step / acceptance workers (final section 6
worker 2 and worker 14):
- (a) Before the bench pass a1a672d is quoted as a gate, the manifest
  must record the exact tool and fixture paths used, and the bench
  must resolve tool/fixture paths repo-relatively or via explicit
  parameters before it is re-run anywhere but the VM that holds
  /home/hatch paths.
- (b) The 10.86 s bench wall is process-only time and must never be
  quoted as end-to-end time. Live timing (rung 2) carries the
  per-phase split; the fixture wall is a harness number only.
- (c) The P9 screenshot save missing from the bench script is a rung-2
  requirement already (final section 4, hard condition), not a new
  rung-1 requirement. No new gate is created here.

### D-4. Codex's A7 "fix NOT landed": REFUTED, no change.

Codex's premise (first_action.py 661-665 still calls observe_screen
for the envelope after) does not hold on the current tree (V-F3):
item 12 cbab398 is landed, `_scope_after` returns the
scope-matching after, and the remaining observe_screen calls are the
fresh-capture default (line 381) and the verification-only
after_screen (line 735). Codex read a lagging laptop tree. The
final's A7 ADOPT (landed, four regression tests still to run) stands
unchanged. The close-out worker (final section 6 worker 3) still
runs the four item-12 regression tests; if they fail, that worker
reports it as a live failure, not as a fold finding.

### D-5. S0 savings numbers: CORROBORATED, no change.

Codex's recomputation (3.181 s / 3.51x from D3, 4.110 s / 4.48x from
D1) is correct arithmetic (V-F2) and brackets the final's PROBE-S0
figure (3.328 s / 3.49x). The recorded range is now 3.18-4.11 s
saved per connection (3.5-4.5x), instead of a single point. The
verdict (ADOPT, 460x and 0.01 s dead) is unchanged. This is a
precision note, not a direction change.

### D-6. CB prescription disagreements: NO verdict changes.

- Codex CB-2 (scope) ADOPT (refuse on scope mismatch) vs final CB-2
  MODIFY (re-ground first, stop only on ambiguity). Codex brings no
  new measured evidence for the blanket stop, and does not engage
  FRT's cost argument that the final adopted: a DOM re-read costs
  0.030 s, so re-ground-and-continue is strictly better than
  throwing away the batch. The final's rule stands.
- Codex CB-5 (postcondition) ADOPT vs final CB-1 MODIFY (fold into
  P5/A8 with the exception list and same-commit envelope migration).
  Codex does not address the two blockers the final adopted: the
  envelope `ok` rename breaks callers unless migrated in the same
  commit (first_action.py:552-563), and postconditions do not exist
  for every action type (scroll, hover, focus-only). The substance
  (postconditions required where they exist) is already adopted. The
  final's MODIFY stands.
- Codex CB-10 (eval) MODIFY (prove allowlisted parity first) vs
  final CB-5(a) ADOPT (remove from the default interface in step 0).
  My grep (V-F5) finds NO production caller of the `zen_dom.py eval`
  CLI subcommand anywhere in the repo, and the internal evaluate()
  stays as the transport. The parity gate has no blocking in-tree
  dependency, and F1 already judged the removal "small, safe, no
  dependency". The final's step-0 removal stands.
- Codex CB-1/CB-3 (target, preconditions) ADOPT vs final CB-5 MODIFY
  (adopted as requirements, definitions owed for "stable"/"unique").
  Codex defines neither term. The final's qualifier stands.
- Codex CB-EXEC MODIFY vs final CB-EXEC MODIFY prototype-only.
  Identical in substance. No change.

### D-7. FCC defects: NO effect on the direction.

Section 2.3 lists all four defects with their effects. None touches
a verdict, an order step, an acceptance criterion, or the AMEND4
close-out. The FCC position file stays verbatim (its driver already
decided that); this log is where the defects are flagged so no later
reader trusts the file's header times or its stale PENDING line.

### D-8. FCC run 1 repeats the draft: NO change.

Run 1 is row-for-row identical to the draft with no stated
disagreement, and the final superseded the draft on evidence run 1
did not have (PROBE-S1, PROBE-S2 bench pass, PROBE-P8 closed, the
F1/F2/F3/FRT round). Its independent verifications (V-F6) corroborate
the final; its divergences (A10 ADOPT, S1/D3 MODIFY) are the draft's
positions, already adjudicated with newer evidence in the final.
Run 2's CB ADOPT is coarser than the final's per-row adjudication
and does not engage FRT's six findings; its evidenced parts (broker
consolidation, 100-task proof plan) already match the final's CB-6
ADOPT and rung 3. No verdict, order, or acceptance change from FCC.

## 4. Updated execution plan

Execution continues UNCHANGED except for the two items below. Every
other step, gate, worker, and date rule in final sections 3, 5, 6,
and 7 stands as written.

1. PLATEAU DEFINITION (the one change, D-1). Final section 6 worker 8
   and section 7 plateau row are updated: the coordinator no longer
   defines the numbers at flip time; the numbers are DEFINED NOW as
   2 cohorts of 30 new held-out tasks, at least 90 percent task
   outcome in EACH cohort, live median end-to-end wall time above
   10 s in both cohorts, measured the same way as rung 2. Below 90
   percent in either cohort is an accuracy failure, not a plateau.
   The trigger authorizes the step-9 prototype only.
2. RUNG-1 MANIFEST LOCK (clarification, D-3). Before the fixture
   bench pass a1a672d is quoted as a gate, the manifest must record
   the exact tool/fixture paths, and the bench must resolve paths
   repo-relatively or via parameters before any re-run off the VM.
   The 10.86 s bench wall is process-only time and is never quoted
   as end-to-end time. Owned by the deploy step / acceptance workers
   (final section 6 workers 2 and 14). No new gate is created.

Everything else: Y1b fixes first (final section 6 worker 1); S0
plus the step-0 measurement bundle (worker 2); AMEND4 close-out
(worker 3, UNAFFECTED by the FCC defects); contract writer (worker
4); P3 re-run in the first quiet window (worker 5); DOMZEN probe
(worker 6); P1/P5-for-class (worker 7); S2 one-class flip (worker 9,
gated on Y1b fixes, fixture green, CB-1 gate, and the plateau
definition now fixed by D-1); P2 spec and implementation (workers 10
and 11); S1 deletion (worker 12); prototype (worker 13); acceptance
rungs 2 and 3 (worker 14); deletions last with dates set at the
step-9 prototype decision (worker 15). B1 lifted with the P9 hard
condition; B2, B3, B4, B5, B6 stand as gates with the lift
conditions in final section 5.

## 5. Evidence index for this fold

- Final direction: improvements/worker-click3-final-direction-log.md
  (e05fc58, 1073 lines).
- Codex position: improvements/codex-discussion-position.md
  (8008662, 126 lines); driver log
  improvements/worker-codex-discuss-driver-log.md (Codex PID 813390,
  06:38-06:55 +07, 232,259 tokens, position written 06:55).
- FCC position: improvements/fcc-discussion-position.md (3d55646,
  78 lines); driver log
  improvements/worker-fcc-discuss-driver-log.md (run 1 06:28-06:38,
  run 2 06:48-06:54, launcher PIDs 803608 and 824526).
- Checks run by me in this session (section 0.1): Wilson
  recomputation (python3, V-F1); SSH arithmetic (V-F2); first_action.py
  observe_screen grep plus _scope_after read plus merge-base check
  (V-F3); two_vision_bench.py path/instances/P9/wall_s greps (V-F4);
  zen_dom eval caller grep repo-wide plus MutationObserver and
  arm_typed_flag greps (V-F5, V-F6); PROBE-S1 commit message check
  (V-F7).
- Numbers used: 17/29 = 58.62 percent, Wilson 40.74-74.49; 96/100
  Wilson lower bound 90.16; 27/30 Wilson lower bound 74.38; 54/60
  Wilson lower bound 79.85; D1 saving 4.110 s / 4.48x; D3 saving
  3.181 s / 3.51x; PROBE-S0 saving 3.328 s / 3.49x; broker core
  12.110 s vs one-shot 28.700 s, 2.37x (1af7330); fixture bench
  10.8596 s process-only (a1a672d); DOM re-read 0.030 s.

## 6. Log commit record

- Written: 2026-11-22 about 07:10 +07 (T+10m from task receipt at
  07:00 +07). Branch todolist-push, HEAD at writing 8008662.
- Commit: (filled after commit; see below).
- This log is an ADDENDUM to the final direction (e05fc58). It does
  not supersede it. The final direction stands, with exactly two
  updates: the plateau definition fixed by D-1 and the rung-1
  manifest clarification by D-3. Any later evidence that contradicts
  a verdict re-opens the affected row through the coordinator; it
  does not silently amend this log or the final direction.
