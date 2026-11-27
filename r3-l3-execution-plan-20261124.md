# R3-L3 Execution Plan (Authoritative)

- SUPERSEDED ON IDS (stamped 2026-11-25 Phase 0, gate G-32): the session IDs, Class L counts, and branch tip in this file are stale and superseded. The canonical sources are the state file (rung3-run-log/r3-l3-coordinator-state.json), thu-tu-chay.txt, and the FINAL re-plan (improvements/r3-l3-replan-final-20261124.md). Canonical values: scorer 1B 4e2f52d4, 2B 2e3ae678, TB-A 97290681, TB-B2 df4defcc; Class L 9, Class S 46; todolist-push tip 81919c0c. Do not use the IDs, counts, or tip in this file; use the canonical sources.
- Date: 2026-11-24, written before task 1.
- Author: planning council (3 independent members plus redteam), convened by the planning coordinator on the owner's order (16:53 +07 24/11): super detailed plan, full direction, many subagents working in parallel without stepping on each other.
- Status: run ON HOLD. 0 tasks run, 0 graded, next task R3-001 (FCC lane).
- Sources: speedup decision `~/workspace/r3-l3-speedup-decision-20261124.md` (APPROVE 3-0, decisions A-H); grading decision `~/workspace/rung3-grading-DECISION.md` (2026-11-23); R3-L3 decision `~/workspace/r3-l3-decision-20261124.md`; member sections `~/workspace/r3-l3-plan/member-1-roadmap.md`, `member-2-no-overlap.md`, `member-3-rules-risks.md`; redteam `~/workspace/r3-l3-plan/redteam.md` (46 objections).
- No em dash or en dash in this file. Commas, periods, short hyphens only.

## 0. Verdict: CONDITIONAL GO, NOT READY FOR TASK 1 YET

The speedup direction is sound (decouple scoring, split scorers, async ledger). The council approves it. But the redteam proved the execution package is NOT READY FOR TASK 1. There are 6 blocking defects and 19 must-fix items. Task 1 must NOT start until every item in the pre-task-1 precondition checklist (section 11) is green and VERIFIED WITH FILES, not merely asserted.

The single most dangerous defect is the DP-01 contradiction: DP-01 is retired (it FAILED in R3-L2) but is listed as a live medium backup in both du-phong files, so the first medium invalid would pick a retired, published backup and void the run. The second most dangerous defect is the Class S misclassification: R3-096 is provably Class L on the key's own words, and four more tasks rest on an unproven snapshot assumption. The most corrosive defect is the reuse of the R3-L2 runner sessions for the same 11 tasks, which quietly voids the held-out claim for a fifth of the run.

One further gate can stop the run before it starts. If the R3-029 and R3-075 keys are truly wrong (as the repo du-phong note asserts), 2 failures are already booked against the 53/55 bar, leaving zero margin. The plan requires both keys to be verified before task 1. If either key is truly wrong, the owner must decide (re-freeze with corrected keys, or exclude the task before task 1 with the pass bar recomputed in advance) before task 1 starts. Do not start a run whose bar is already unreachable.

## 1. Ground truth (verified first-hand by council members)

- Frozen: branch todolist-push tip 175cfd7. H1 9b9d900, H2 5fac0eb. Key JSON sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8 (verified by sha256sum by two members). List sha256 c1d9a220, keys.md sha256 21f8b61a. Post-freeze commits 6c95c51 (gitleaks allowlist), 6a7d31c (du-phong.txt), 175cfd7 (exception list) touch only rung3-run-log files, not frozen list or key files.
- 55 tasks: 35 browser, 20 desktop; 37 trung binh, 11 kho, 7 rat kho. Pass bar 53/55. Invalid cap max 5 total, max 2 per difficulty group.
- Tier A run tasks: R3-002, R3-007, R3-013, R3-014, R3-021, R3-072, R3-082, plus DP-02 and DP-05 if used as backups. Tier C: R3-010, R3-067, R3-083, R3-085. Tier B hybrid: R3-003, R3-004, R3-022, R3-042. All other tasks Tier B.
- Run order (verified two ways, laptop and branch files carry the identical 55-ID sequence): FCC positions 1-28, R3-001 to R3-037. Codex positions 29-55, R3-040 to R3-100. Task 1 is R3-001 (FCC). R3-089 is position 49 (Codex).
- Exception list (commit 175cfd7, read in full): 5 Class L tasks, 50 Class S tasks. Class L: R3-001, R3-055, R3-074, R3-075, R3-089. DP-02 is Class L if used as a backup. DP-03, DP-05, DP-06, DP-07 are Class S. NOTE: redteam objection 32 proves R3-096 is Class L, not Class S. The plan moves R3-096 to Class L (section 10, objection 32) and requires the exception list to be republished before task 1. The Class L count is therefore 6 minimum, possibly up to 10 if R3-078, R3-088, R3-093, R3-079 also move. The time estimate in section 2 is revised for this.
- Backups: medium DP-03, DP-06, DP-07; hard DP-02 only; very hard DP-05 only. DP-01 RETIRED (it FAILED in R3-L2, ledger commit 7ca7f46, and is spent). DP-04 removed. NOTE: the du-phong files currently list DP-01 as live. That is blocking defect 1. The plan removes it (section 10, objection 1).
- WAVE gate passed 16:31-16:32 +07 24/11 (Mochi, live browser): Fox News Errors 2, BBC /news Errors 0. R3-009 runs normally. No DP-03 backup. The full 5-number WAVE record per page must be confirmed in writing before task 1 (redteam objection 42).
- Runners alive and idle: FCC PID 2046632 (tmux r3-fcc-runner), Codex PID 1235041 (tmux r3-codex-runner). NOTE: these are the R3-L2 sessions. Redteam objection 39 requires FRESH runner sessions for R3-L3 (section 10). The PIDs above are the old sessions, not the R3-L3 sessions.
- Scorers: Pair A scorer 1 Mochi (session 70cd99d1-ecef-4d02-9f42-714d7e86ab85, declaration 2026-11-23 19:17 +07), scorer 2 dc7e0d0d-24b2-4d94-9729-f106d21eff16. Pair A tiebreaker 6e844611-a34b-448b-ace1-5120a3644444, declaration 16:53 +07, calibration PASS. Pair B scorer 1B 2890a5de-61bd-4240-8045-eca744cf59a7, declaration 16:53:47 +07, calibration PASS; scorer 2B b8c9b7b8-d2ec-4d07-8f27-590bf160e22d, declaration 16:53:29 +07, calibration PASS; tiebreaker B 3f3aca86-57f1-4ade-81ec-838f65c61f07, declaration 16:54:18 +07, calibration PASS. NOTE: redteam objections 19 and 37 require the calibration to be re-run with Tier C and B-hybrid tasks and verified by someone other than the coordinator before task 1.
- Session: FREE by /proc fd scan for cursor.lock (stated in brief; the coordinator re-confirms immediately before task 1). The cursor.lock mechanism is undocumented in frozen files (speedup residual risk 4). The rule is unchanged.
- R3-089 fixture gate: refresh the day before R3-089 runs (touch -d "1 day ago" log-01 to log-06, touch -d "10 days ago" log-07 to log-12 in ~/rung3/nd09-logs; find with -mtime -7 must return exactly 6 files; record in the run log before R3-089 starts). Hard expiry: 2026-11-29 19:20.
- R3-029 and R3-075 have wrong keys per the repo du-phong note, frozen, fail-by-key. This assertion must be verified before task 1 (redteam objection 41).
- R3-011, R3-028, R3-036, R3-046 are pre-run invalid candidates, undeclared, with no group mapping (redteam objection 42).

## 2. Hard constraints (not votable, not changeable)

- Frozen H1 9b9d900 / H2 5fac0eb and frozen key hash 5059f6c4 do not change. No key, list, Tier C rubric, or tier edit of any kind after task 1.
- Pass bar 53/55 does not change, except by an owner decision before task 1 if a task is excluded with a recomputed bar (redteam objection 41).
- Invalid cap max 5 total, max 2 per difficulty group, does not change.
- Scoring stays evidence versus key and independent. The evidence contract holds. The single-driver session rule holds: one driver at a time, session free only by /proc fd scan for cursor.lock. No third runner. No parallel driving.
- Mei is disqualified as a scorer. She authored the list and keys.
- The 30-minute task timeout is enforced. Over 30 minutes is FAIL, stop, log.
- If any hard constraint is found broken mid-run, the coordinator stops the affected lane, preserves the evidence, and escalates in writing. The coordinator does not repair a broken constraint by improvising.

## 3. Roadmap

### Phase 0: Preparation and pre-task-1 gates

Goal: every precondition in section 11 green and verified with files, then the coordinator releases task 1. Nothing runs before the exit checklist is green. This phase is where the redteam blocking defects are fixed. The owner ordered thorough preparation before execution, and the run does not start until this phase closes.

Steps, in order:

1. Fix the blocking defects (section 10): remove DP-01 from both du-phong files and declare the laptop file canonical; wipe and recreate ~/rung3-chung-cu/ and restore fixtures from ~/rung3-goc/; move R3-096 to Class L and resolve R3-078, R3-088, R3-093, R3-079, then republish the exception list; start fresh runner sessions and record their IDs; name a deputy coordinator and define the coordinator state file; create the R3-L3 ledger file with schema and trial row.
2. Fix the must-fix items (section 10): manifest-gate script and audit scan named, committed, and proven; timeout watcher and kill procedure named; R3-029 account and product names confirmed in writing; calibration re-run with Tier C and B-hybrid tasks, signed grades on file, verified by someone other than the coordinator; Pair B declarations and calibration verified independently; R3-029 and R3-075 keys verified (owner decision if wrong); the 4 pre-run invalid candidates declared or verified with group mapping; R3-009 WAVE re-check recorded with all 5 numbers per page; R3-L3 liveness report signed off; snapshot naming fixed to R3-xxx-L3; thu-tu-chay.txt rewritten to the decoupled rule with runner IDs, tip 175cfd7, and deputy, then timestamped.
3. Coordinator records the FCC and Codex runner agent session IDs (fresh sessions, step 1) in rung3-run-log/thu-tu-chay.txt on todolist-push.
4. Coordinator corrects the handoff text in the committed thu-tu-chay.txt to the decoupled pipeline (Decision B), and issues runner briefs carrying the same pipeline.
5. Coordinator syncs the laptop ~/thu-tu-chay.txt to the R3-L3 version, or repoints resume.py at the repo copy. The laptop file is stale R3-L2 (BBC URLs, old key hash 71fe1d79, scorer 3 TBD). The run order sequence is identical in both files, but the header, scorer, and key lines on the laptop are stale.
6. Coordinator confirms the scripted manifest check exists and runs (required files, sha256 per file, mtimes inside the run window, about 2 minutes) and confirms the Tier A single-run procedure (coordinator runs each Tier A checker once, hands the identical deterministic output to both scorers).
7. Coordinator confirms Pair B briefing in writing (Class S and Class L lists, backpressure cap, Tier A single-run, allowlist and denylist, invalid procedure).
8. Coordinator re-confirms the session is FREE by /proc fd scan for cursor.lock immediately before releasing task 1, and confirms both runners are idle in their fresh tmux sessions.
9. Coordinator confirms the R3-089 fixture freshness plan and its 2026-11-29 19:20 deadline is on the run log watch list, and assigns an owner and a date for the refresh.
10. Coordinator publishes the time budget (section 3, estimate) with a line for coordinator serial work, and records the honest planning range (19 to 31 hours).

Duration: the speedup decision estimated 30-60 minutes of coordinator admin for the preconditions as originally listed. The redteam blocking defects add real work (fresh runner sessions, evidence wipe, du-phong correction, exception list republication, manifest script, audit scan, deputy, ledger creation, liveness report, key verification). The honest Phase 0 duration is 2-4 hours of focused coordinator work, not 30-60 minutes. Do not compress it by skipping verification. A precondition verified with a file is done; a precondition asserted without a file is not done.

Exit criteria: all items in section 11 green, each verified with a named file, commit, or output. Task 1 releases only then.

### Phase 1: Execution, rolling (cuon chieu)

Goal: all 55 tasks run in fixed order, two lanes in parallel, scoring async behind the runners, no one waiting for a stage that is not a hard dependency.

Lane structure:

- FCC lane: positions 1-28, R3-001 to R3-037, one task at a time, sequential inside the lane.
- Codex lane: positions 29-55, R3-040 to R3-100, one task at a time, sequential inside the lane.
- Both lanes start together. A wait on one lane never blocks the other lane, except for the shared single-driver session (only one driver at a time, free only by /proc fd scan).

Per-task pipeline, Class S (decoupled scoring):

1. Runner drives the task (single driver at a time).
2. Runner writes evidence into ~/rung3-chung-cu/R3-xxx/ and the snapshot directory with a manifest.
3. Coordinator runs the scripted manifest gate (required files, sha256 per file, mtimes in the run window, about 2 minutes). If the manifest fails, the runner does NOT proceed and no reset happens. The failure branch is in section 5.
4. Coordinator performs the surgical per-task reset (only that task's fixture from ~/rung3-goc/, never a whole-directory restore while the other lane runs). Runner proceeds to the next task.
5. Scorers score asynchronously from the sealed snapshot (both scorers in the pair, concurrent, blind within the pair).
6. Tier A tasks: coordinator runs the checker once and hands the identical deterministic output to both scorers. Each scorer still does the human check (evidence files exist, screenshot legible) and signs its own verdict. The checker input hash (snapshot manifest hash plus key hash) is recorded with the single output.
7. Coordinator audits reads (forbidden-read scan), compares verdicts, calls the tiebreaker on disagreement or disputed invalid, appends the ledger row locally immediately, pushes async (at least hourly, immediately on any invalid or dispute).
8. Reset-log entry kept per task. Backpressure cap enforced.

Per-task pipeline, Class L (score-before-reset, runner waits):

1. Same as steps 1-2 above.
2. Both scorers finish scoring from the live state BEFORE the reset. The runner waits.
3. Coordinator audits, compares, appends the ledger row, then performs the reset. Runner proceeds to the next task.
4. Class L tasks (after the redteam fix): R3-001 (position 1), R3-055 (position 36), R3-074 (position 39), R3-075 (position 40), R3-089 (position 49), R3-096 (position in Codex lane, to be confirmed from the run order), plus any of R3-078, R3-088, R3-093, R3-079 that the coordinator moves to Class L under section 10 objection 32. Backup DP-02 is Class L if it replaces a task. The republished exception list is the authority; this plan does not fix the Class L count in advance.

Pilot (redteam objection 38): the decoupling is piloted on the first Class S task (R3-002, Tier A, simple evidence). The coordinator verifies the snapshot contents against the key's evidence line before the runner proceeds to task 3, and only then continues decoupled. If the pilot snapshot is incomplete, the coordinator reverts to serial for the affected task class. The rolling start does not proceed on an unvalidated decoupling.

Timeout: 30 minutes per task, enforced by the coordinator (watcher and kill procedure named in Phase 0). Over 30 minutes is FAIL, stop, log. No exception.

Invalid handling during execution: scorer 1 proposes invalid with independent scorer-collected evidence and a written reason; scorer 2 confirms or rejects blind (sees only the invalid evidence and the reason); if scorer 2 disagrees, the tiebreaker decides blind on the same packet. Coordinator countersigns each invalid. Owner is notified at invalid 3, 4, and 5. Backup assignment (first unused backup of the same difficulty, fixed order in du-phong.txt) is recorded in du-phong.txt at decision time, with both scorers' names. A backup inherits the pair of the task it replaces. Agent-caused blocks count as FAIL, not invalid. Correlated outage: one event counts as 1 invalid against the cap, each affected task still leaves the sample and consumes a backup slot; coordinator records event plus affected tasks plus backup consumption together.

Milestones inside Phase 1:

- M1: R3-001 graded (position 1, Class L serial, first ledger row).
- M2: checkpoint after the first 3 graded tasks (see below).
- M3: FCC lane complete (position 28, R3-037). Codex lane passes its Class L tasks.
- M4: R3-089 fixture gate passed before position 49 runs (hard deadline 2026-11-29 19:20 for the refresh).
- M5: run-complete, position 55 (R3-100) evidence frozen. Run-complete and ledger-complete are separate timestamps.

### Phase 2: Scoring drain

Goal: every run task graded, every ledger row appended locally, ledger pushed to GitHub, ledger-complete timestamp recorded.

Steps:

1. Scorers finish the outstanding async grades (at most 2 outstanding per runner by the backpressure cap, so at most 4 tasks can be unscored at run-complete).
2. Coordinator audits each remaining grade, resolves any disagreement through the tiebreaker, appends each ledger row locally immediately.
3. Coordinator pushes the ledger (async push already running at least hourly; a final push closes the ledger). Ledger-complete deadline: within 2 hours of run-complete, owned by the coordinator.
4. Coordinator verifies ledger completeness: 55 rows or fewer only where the invalid and backup rules explain the count, every row signed, every invalid countersigned with its backup recorded in du-phong.txt.

Duration: about 0.5-1 hour after run-complete.

### Phase 3: Closure

Goal: verified result, pass or fail call against 53/55, written report to the owner.

Steps:

1. Coordinator verifies the frozen hashes one last time (list, keys.md, keys.json) and the ledger schema.
2. Coordinator computes inter-pair agreement stats and the coupled-task checks (R3-078 with R3-079; R3-067 with R3-083, same drawing approach or not). The coupled checks run when the second task of each pair is graded, not only at the end.
3. Coordinator reconciles the invalid count against the caps (max 5 total, max 2 per group) and the backup consumption against du-phong.txt.
4. Coordinator applies the pass bar: 53 pass on 55 valid, recomputed from the section 1 table if the valid count shrank (54 valid needs 52, 53 needs 51, and so on). The recomputation is recorded in the ledger at the time it happens, and only by an owner decision if the shrink was not pre-declared.
5. Coordinator writes the closure report (run-complete timestamp, ledger-complete timestamp, tally, invalids with backups, disputes with tiebreaker outcomes, estimate vs actual, checkpoint revisions) and reports run-complete and ledger-complete as separate timestamps to the owner.

Duration: about 1-2 hours after ledger-complete.

### Timeline and milestones summary

| Milestone | What | When |
|---|---|---|
| M0 | Pre-task-1 gates green, task 1 released | Before task 1, Phase 0 about 2-4 hours (revised from 30-60 min, see section 3 estimate) |
| M1 | R3-001 graded, first ledger row | First task cycle |
| M2 | Checkpoint, estimate revised in writing, decision rule applied | At the 3rd graded task |
| M3 | FCC lane complete (position 28, R3-037) | Inside Phase 1 |
| M4 | R3-089 fixture gate passed | Before position 49, hard deadline 2026-11-29 19:20 |
| M5 | Run-complete (position 55, R3-100) | See estimate below |
| M6 | Ledger-complete | Within 2 hours of M5 |
| M7 | Closure report, pass or fail call | About 1-2 hours after M6 |

### Time estimate: honest range, not a promise

- Baseline: 24-30 hours, midpoint 27 hours (speedup council, serial pipeline).
- Saving per decoupled task: about 12 minutes of scoring wait plus about 3 minutes of ledger-push block removed from the critical path, about 15 minutes per lane-task. Run time per task is unchanged.
- Lane arithmetic (using the verified exception list, 5 Class L, 50 Class S): FCC lane 27 decoupled x 15 minutes = 405 minutes = 6.75 hours saved; Codex lane 23 decoupled x 15 minutes = 345 minutes = 5.75 hours saved. Wall saving is set by the longer lane: about 6.75 hours from decoupling alone.
- Council consensus is 7-8 hours saved, new total about 19-21 hours. That consensus sits just above the pure decoupling arithmetic.
- Redteam correction: 19-21 hours is a LOWER BOUND, not a forecast. It counts zero minutes for the new coordinator serial work (55 manifest verifications at about 2 minutes each is 1.8 hours alone; 110 grade audits at 5 minutes each is about 9 hours; 55 ledger appends; 9 Tier A checker runs; invalid and tiebreaker handling). It also assumes the scoring wait sat on the critical path for every task, but Class L tasks stay serial. And the Class L count rises from 5 to at least 6 (R3-096) and possibly up to 10, which returns serial wait to those lanes.
- Honest planning range: 19 hours (best case, everything steady-state) to 31 hours (pessimistic: one recurring 4-hour stall, two backpressure pauses, three invalids or disputes). A correlated service outage is UNBOUNDED until the pause rule's maximum wait is written (Phase 0 sets it). The run is staffed and scheduled for 31 hours, not 20 hours. Do not promise the owner a 20-hour finish.
- The R3-L2 observed rate contradicts the baseline: 11 tasks took about 16 hours of wall time (about 1.5 hours per task across the run), including one 4h05 run and two scoring batching anomalies. The council attributes the gap to anomalies, but no per-task timing table was produced to show the steady-state rate. The checkpoint below replaces assumption with measurement.

### Checkpoint after the first 3 graded tasks

Trigger: the moment the 3rd ledger row is appended. Expected to be R3-001, R3-002, R3-003 in run order if scoring keeps up; if scoring lags, it is the first 3 rows in ledger order, whatever they are.

Coordinator records at the checkpoint: wall elapsed since task 1 start; per-lane tasks run and per-task run wall times (start to evidence-ready); manifest gate times; scoring lag per task (evidence-ready to both verdicts in); ledger append times; any timeout, invalid, dispute, or backpressure pause so far.

Recomputation, done separately per lane (do not average Class L and Class S cycles together): remaining FCC cycle = remaining FCC tasks x measured mean FCC lane cycle (run plus gate, plus serial scoring wait only for the remaining Class L tasks in that lane); remaining Codex cycle = remaining Codex tasks x measured mean Codex lane cycle (same, plus serial scoring wait for the remaining Class L tasks). Revised run-complete = elapsed plus the larger of the two remaining lane cycles. Revised ledger-complete = revised run-complete plus measured drain (outstanding unscored tasks x mean scoring lag, capped by the backpressure limit).

Decision rule: if the revised run-complete is inside 19-21 hours, continue and record the revised point estimate in writing. If the revised run-complete is outside 19-21 hours, OR if the mean cycle time exceeds the estimate by more than 25 percent, the coordinator PAUSES and reports to the owner with options (continue, add scorers, slow down, or stop). The run continues only on the owner's decision. No stop unless a hard constraint is breached.

Caution on the early sample: the first 3 tasks mix shapes (R3-001 is Class L serial with a live re-read, R3-002 is Tier A). R3-001's serial scoring is the slowest scoring shape in Pair A, so the early sample can overstate scoring lag. Separate the Class L cycle from the Class S cycle when recomputing, and do not project the R3-001 serial wait onto the Class S tasks.

## 4. Work division

### Role table (9 sessions)

| Role | Who | Scope | Spawned / briefed by |
|---|---|---|---|
| Coordinator | Coordinator agent (Muse subagent, one session, plus deputy in Phase 0) | Owns the run: releases task 1, runs the manifest gate, does resets, runs Tier A checkers once, audits grades, appends ledger rows, calls tiebreakers, enforces timeout and backpressure, reports to the parent (Muse). The coordinator's own work is serial and is not on the critical path for running, but it is a bottleneck risk (see section 8). | Parent (Muse) |
| FCC runner | FCC runner agent (one session, fresh for R3-L3) | Drives positions 1-28 (R3-001 to R3-037), one task at a time, sequential. Writes evidence and snapshot. | Coordinator |
| Codex runner | Codex runner agent (one session, fresh for R3-L3) | Drives positions 29-55 (R3-040 to R3-100), one task at a time, sequential. Writes evidence and snapshot. | Coordinator |
| Pair A scorer 1 | Mochi (browser session) | Scores positions 1-28, from sealed snapshots. Blind within the pair. | Coordinator |
| Pair A scorer 2 | dc7e0d0d | Scores positions 1-28, from sealed snapshots. Blind within the pair. | Coordinator |
| Pair B scorer 1B | 2890a5de | Scores positions 29-55, from sealed snapshots. Blind within the pair. | Coordinator |
| Pair B scorer 2B | b8c9b7b8 | Scores positions 29-55, from sealed snapshots. Blind within the pair. | Coordinator |
| Pair A tiebreaker | 6e844611 | Pre-named standby. Acts only on PASS/FAIL disagreement, disputed invalid, or formal key dispute (exact blind packet contents, section 6). | Coordinator, on demand |
| Pair B tiebreaker | 3f3aca86 | Pre-named standby. Acts only on PASS/FAIL disagreement, disputed invalid, or formal key dispute. | Coordinator, on demand |

Total: 9 sessions (1 coordinator + deputy counted as 1 role, 2 runners, 4 scorers, 2 standby tiebreakers). If a standby tiebreaker is invoked, it becomes an active scorer for that one task only, then returns to standby.

### Spawn and briefing order

The owner ordered rolling execution (cuon chieu): do not wait for each other, each part proceeds as soon as its hard dependencies are met. The coordinator owns the dependency graph and releases each part as soon as its dependencies are met, and no earlier.

Hard dependencies (block the next step until met):

- H1: All of Phase 0 (section 11) complete before task 1.
- H2: Exception list published and understood by both runners and all 4 scorers before task 1. If it cannot be published, the serial pipeline stands (Decision B fallback).
- H3: Pair A fully declared and calibrated (Mochi, dc7e0d0d, tiebreaker 6e844611) before position 1.
- H4: Pair B fully declared and calibrated (1B, 2B, tiebreaker B) before position 29. Pair B can be ready after task 1 starts, because positions 29-55 do not start until the FCC lane is well in progress, but Pair B must be ready before the first Codex task that needs scoring.
- H5: Fresh runner sessions started and their IDs recorded in thu-tu-chay.txt before task 1.
- H6: The session is FREE by /proc fd scan immediately before a runner drives a task.
- H7: Per-task manifest gate passes before a runner proceeds to the next task.
- H8: Ledger row appended locally before a task is counted as graded.
- H9: The R3-089 fixture refresh is done and recorded the day before R3-089 runs (hard deadline 2026-11-29 19:20).
- H10: A scorer must not score a task it has already seen scored.
- H11: Tier A checker output from the coordinator must be recorded before the scorers grade a Tier A task.
- H12: Only the coordinator commits to the run-log branch during the run.

Non-dependencies (parts that run in parallel, do not wait):

- N1: Scoring a task does not wait for the next task to finish. It starts as soon as its snapshot is sealed.
- N2: Ledger push does not block the next task. Append locally, push async at least hourly.
- N3: Pair B preparation does not wait for the FCC lane. Brief and calibrate Pair B while the FCC lane runs.
- N4: The auditor does not wait for a pair to finish a lane. Audits run per grade.
- N5: Class S tasks in a lane do not wait for the other lane.
- N6: Inter-pair agreement checks (after each pair's first 3 graded tasks) do not block the next task, unless a disagreement pattern triggers the council review in section 6.
- N7: The closure report does not wait for the run-complete timestamp; it starts as soon as the ledger is complete.
- N8: The R3-089 refresh preparation does not wait for position 49 to approach; the owner and date are assigned in Phase 0.

### What is already done (do not redo)

- Pair A declaration and calibration: done (Mochi, dc7e0d0d, tiebreaker 6e844611).
- Pair B declaration and calibration: done in the members' records, BUT the calibration must be re-run with a Tier C task and a B-hybrid task and verified by someone other than the coordinator before task 1 (redteam objections 19 and 37).
- Exception list: published at commit 175cfd7, BUT it must be republished with R3-096 as Class L and the R3-078, R3-088, R3-093, R3-079 resolution before task 1 (redteam objection 32).
- WAVE gate: passed 16:31-16:32 +07, BUT the full 5-number record must be confirmed in writing before task 1 (redteam objection 42).
- Runners alive and idle in their old sessions, BUT fresh sessions must be started and recorded before task 1 (redteam objection 39).

### Where the plan may be wrong (honest gaps)

- The laptop thu-tu-chay.txt is still R3-L2 (BBC URLs, old key hash 71fe1d79, scorer 3 TBD). If the coordinator launches from the laptop copy, the run reads a stale header and stale scorer lines. Fix in Phase 0, step 5.
- The file `~/rung3-chung-cu/` still holds R3-L2 evidence (R3-001 ket-qua.txt dated 2026-11-24 01:38, 12 subdirectories). Fix in Phase 0 (wipe and recreate).
- The exception list contents are not yet verified against the 55 task files. The coordinator verifies each Class L task has a live re-read and each Class S task does not need one, before task 1.
- The runner PIDs and session IDs in the briefs are the old R3-L2 sessions. Fresh sessions are a precondition.
- The key hash was recomputed by two members and matches (5059f6c4). The frozen list and key hashes are unchanged since the freeze.
- The snapshot and verdict root paths are prescriptions, not pre-existing facts. The coordinator creates them before task 1.

## 5. No-overlap rules

### Boundaries

- Each task is assigned to exactly one lane and exactly one runner. No two runners ever drive the same task. No two scorers ever grade the same task outside their own pair.
- Each task's snapshot lives in exactly one directory: `~/workspace/rung3-snapshots/R3-xxx-L3/` (the -L3 suffix is mandatory; R3-L2 used `R3-xxx-s1`, so reusing that pattern collides). Each snapshot carries a manifest.json with a sha256 per file and the mtime window.
- Each verdict lives in exactly one file: `~/workspace/rung3-verdicts/R3-xxx-A1.json` (Pair A scorer 1), `R3-xxx-A2.json` (Pair A scorer 2), `R3-xxx-B1.json` (Pair B scorer 1), `R3-xxx-B2.json` (Pair B scorer 2), `R3-xxx-TB.json` (tiebreaker, only when invoked). Verdict files are VM-local, never committed. A scorer never writes to another scorer's verdict file.
- Each runner has exactly one tmux session, fresh for R3-L3. Each scorer has exactly one session. No session is shared between two agents.
- Only the coordinator writes to the ledger. Only the coordinator writes to the run-log branch. Only the coordinator performs resets and runs Tier A checkers.
- No two agents drive the browser at the same time. Only one driver at a time, session free only by /proc fd scan for cursor.lock.

### File and directory ownership

| Path | Owner | Who else may read | Who else may write |
|---|---|---|---|
| Frozen list and keys (rung3-files/) | Coordinator (read only) | All (read) | Nobody after task 1 |
| rung3-run-log/thu-tu-chay.txt | Coordinator | All (read) | Nobody during the run |
| rung3-run-log/du-phong.txt | Coordinator | All (read) | Nobody, except coordinator at a backup decision |
| rung3-run-log/R3-L3-grades.jsonl | Coordinator | All (read) | Nobody else |
| rung3-run-log/ (other files) | Coordinator | All (read) | Nobody else |
| ~/rung3-chung-cu/R3-xxx/ | The runner for that task, until sealed | Scorers (read, after seal) | Nobody else |
| ~/workspace/rung3-snapshots/R3-xxx-L3/ | Coordinator (sealed) | Both scorers in the pair (read) | Nobody after seal |
| ~/workspace/rung3-verdicts/R3-xxx-*.json | The scorer who signs it | Coordinator (read) | Nobody else |
| ~/rung3-goc/ (pristine fixtures) | Coordinator (read only) | Runners (read) | Nobody during the run |
| ~/rung3/ (live task files) | Runner for the current task | Coordinator (read, reset) | Only the runner for the current task, until reset |
| ~/workspace/computer-use-wayland repo (other paths) | Nobody during the run | All (read) | Nobody, except coordinator for run-log commits |
| ~/workspace/r3-l3-plan/ (council files) | Coordinator (read) | All (read) | Nobody |

### Conflict matrix: who touches which resource

| Resource | FCC runner | Codex runner | Pair A scorers | Pair B scorers | Tiebreakers | Coordinator |
|---|---|---|---|---|---|---|
| Shared browser session (cursor.lock) | Drive, one at a time | Drive, one at a time | Never | Never | Never | Never drive |
| ~/rung3/ live task files | Current task only | Current task only | Never | Never | Never | Reset only |
| ~/rung3-chung-cu/R3-xxx/ | Own tasks only | Own tasks only | Read after seal | Read after seal | Read after seal | Read, seal |
| Snapshot R3-xxx-L3/ | Write, then sealed | Write, then sealed | Read (own lane) | Read (own lane) | Read (on invoke) | Create, seal, verify |
| Verdict R3-xxx-*.json | Never | Never | Own file only | Own file only | Own file only | Read |
| Ledger R3-L3-grades.jsonl | Never | Never | Never | Never | Never | Write only |
| thu-tu-chay.txt / du-phong.txt | Read only | Read only | Read only | Read only | Read only | Write only |
| Run-log branch commits | Never | Never | Never | Never | Never | Only committer |
| Frozen list and keys | Read only | Read only | Read only | Read only | Read only | Read only |

### Dangerous pairs and how they are handled

- Both runners need the browser session at the same time: the second waits. Session free only by /proc fd scan for cursor.lock. No driver starts while the lock exists. If the lock is stale (a dead driver), the coordinator verifies the driver process is dead by /proc before clearing it, and records the clearing in the run log.
- Both runners need the same fixture file: they never do, because each task's fixture is per-task and the reset is per-task. If a task's fixture overlaps another task's fixture, the coordinator records the overlap in the run log and sequences the two tasks, never letting both runners touch the shared file at once.
- A scorer needs a snapshot while the runner is still writing it: the scorer waits. A snapshot is readable only after the coordinator seals it (manifest complete, sha256 per file, mtimes in the window). An unsealed snapshot is not a scoring input.
- The coordinator needs to reset a task while its scorer is still reading the live state: this happens only for Class L tasks, where scoring finishes BEFORE the reset. For Class S tasks, the reset happens after the manifest gate, and the scorers read the sealed snapshot, not the live state.
- Two scorers in a pair need the same snapshot: they read the same sealed snapshot concurrently. That is safe because the snapshot is read-only after sealing. They must not read from each other's verdict files or from the live state.
- A tiebreaker needs the same packet as a scorer: the tiebreaker reads the exact blind packet (scorer 1 verdict, scorer 2 verdict, evidence manifest, key excerpt) from the coordinator. It does not read from the scorers' sessions or from live state.

### Session sharing rule

- The laptop is a shared session for the run, but only one agent drives it at a time. The rule is: before a runner drives, it checks the session is free by /proc fd scan for cursor.lock. If the lock exists, it waits. If the lock is stale, it reports to the coordinator, who verifies and clears it.
- Scorers drive live ONLY for Class L tasks (for example Mochi re-opening TodoMVC for R3-001, or opening directories for R3-055). When a scorer needs to drive live for a Class L task, the other lane's runner pauses driving until the scorer releases the session. The coordinator coordinates the handoff and records it in the run log. This is the interleaving rule (redteam objection 7). The /proc fd scan command is documented verbatim in Phase 0 with its expected output, and the coordinator is the person who runs it (redteam objection 31).
- The tiebreakers never drive the session.
- The coordinator never drives the session. It verifies, seals, resets, and commits.

### Manifest-gate failure branch

Pre-reset content check (redteam objection 23): before resetting a Class S task, the coordinator confirms the snapshot contains every file the key's "Vat chung cham" line names for that task. If a file is missing, the task is treated as Class L for that run (score-before-reset) and the exception list is corrected. This check is part of the manifest gate.

If the manifest gate fails (a required file missing, a sha256 mismatch, or an mtime outside the run window), the runner does NOT proceed to the next task, and NO reset happens. The coordinator logs the failure, the runner re-collects the missing or changed evidence, the coordinator re-runs the gate, and the runner proceeds only after the gate passes. If the gate fails three times for the same task, the coordinator pauses the lane, preserves the evidence, and escalates in writing to the parent (Muse). The task is not marked FAIL on a manifest failure alone; it is marked FAIL only if the 30-minute timeout expires while the gate is still failing.

### Git discipline

- Only the coordinator commits to the run-log branch (todolist-push) during the run. All commits use an explicit pathspec: `git add -- <paths>` then `git commit -m <message>` with no pathspec on the commit itself. Never `git add -A`. Never `git commit -- <paths>`. Never leave files staged across a gap (add and commit atomically).
- Every push is verified with `git ls-remote`. Every JSONL append is preceded by a check that the file ends with a newline, and followed by a parse verification.
- Evidence PNGs are force-added (`git add -f`) because the repo .gitignore blocks `*.png`. A narrow exception for the rung3 snapshot dirs is the long-term fix; until then, coordinators force-add.
- No agent other than the coordinator touches the repo during the run. Runners and scorers never commit, never push, never edit repo files.

## 6. Decision rules

### Tiebreaker

Called only when: (a) the two scorers in a pair disagree PASS/FAIL; (b) a proposed invalid is disputed; (c) a formal key dispute is raised (the scorer claims the frozen key is wrong for that task). The tiebreaker receives the exact blind packet: scorer 1 verdict, scorer 2 verdict, evidence manifest, key excerpt. It does not see the runners' outcomes, the other pair's verdicts, or the live state. Its verdict is final for that task. The coordinator records the tiebreaker invocation and outcome in the ledger row.

### Invalid

A task is INVALID only when: the scorer can show, with independent scorer-collected evidence, that the task cannot be fairly graded (fixture broken, key provably wrong, external service down with no alternative source, or the task's own evidence requirement is impossible). Agent-caused blocks count as FAIL, not invalid. A curl 403 alone is NEVER sufficient for an invalid. The procedure: scorer 1 proposes invalid with a written reason and independent evidence; scorer 2 confirms or rejects blind (sees only the invalid evidence and the reason); if scorer 2 disagrees, the tiebreaker decides blind on the same packet. The coordinator countersigns each invalid. The owner is notified at invalid 3, 4, and 5. Each invalid consumes a backup slot (first unused backup of the same difficulty, fixed order in du-phong.txt, recorded in du-phong.txt at decision time with both scorers' names). A backup inherits the pair of the task it replaces.

### Backpressure

Max 2 unscored tasks outstanding per runner. If a runner has 2 unscored tasks and the scoring lag for the oldest exceeds 30 minutes, the coordinator pauses that runner (the other lane continues). The runner resumes when the outstanding count drops below 2. The pause is recorded in the run log with the reason and the resume time.

### Timeout

30 minutes per task, wall clock, from task start to evidence-ready. Over 30 minutes is FAIL, stop, log. The coordinator enforces it with the watcher named in Phase 0. No task is exempt unless the owner approved an exemption in writing before task 1, with the reason recorded. R3-040 ran 4h05 in R3-L2; that must not recur. If a task's legitimate run exceeds 30 minutes, the coordinator records it in Phase 0 and the owner decides before task 1 whether to exempt it or to let it fail on timeout.

### Backup assignment

When a task is declared invalid, the coordinator assigns the first unused backup of the same difficulty, in the fixed order in du-phong.txt (medium: DP-03, DP-06, DP-07; hard: DP-02 only; very hard: DP-05 only). DP-01 is retired and is never assigned. The assignment is recorded in du-phong.txt at decision time, with both scorers' names. The backup task runs in the same lane as the task it replaces, at the next position after the invalid decision (not at the end of the lane), so the lane order stays sequential. A backup inherits the pair of the task it replaces. If a backup itself is declared invalid, the next backup of the same difficulty is assigned; if no backup of that difficulty remains, the coordinator escalates to the owner.

### R3-011 (per-event ruling)

A proven shared cause counts as 1 invalid for BOTH the total cap (5) and the group cap (2). If a shared cause cannot be proven, count per-task. Trigger conditions: the real browser is blocked after at least 2 attempts at different times, independent scorer confirmation, and the task has no alternative source. A curl 403 is NEVER sufficient. The coordinator records the proof (browser attempts with timestamps, scorer confirmation) in the ledger row.

### Key disputes

If a scorer claims the frozen key is wrong for a task (for example R3-029 or R3-075), the scorer raises a formal key dispute with the exact key text and the exact evidence. The tiebreaker decides blind on the exact packet. The frozen key is graded as written unless the tiebreaker rules otherwise. A key dispute does not change the frozen key for other tasks. If the tiebreaker rules the key is wrong, the task is marked INVALID (not PASS, not FAIL) and a backup is assigned, and the coordinator records the ruling in the ledger.

### Coupled tasks

R3-078 and R3-079 share the same file set and the same grading logic (file order and count). If R3-078 is graded first, its verdict is recorded, and R3-079 is graded independently against the same key, but the coordinator flags the coupling in the ledger. R3-067 and R3-083 share the same drawing approach; the coordinator records whether both used the same approach or not when the second is graded. The coupled checks run when the second task of each pair is graded, not only at the end.

### R3-100 port check

R3-100 is graded from the saved report and HTML files only. The live port check (port 8899 closed) is done by the runner at run time, immediately after the task, and recorded in the evidence. The scorer grades from that recorded port state, not from a live check hours later, because a port found open later could be another task's server and a port found closed later proves nothing about run time. (Redteam objection 33.)

### Checkpoint decision rule

At the checkpoint (after the 3rd graded task), if the revised run-complete is outside 19-21 hours, OR if the mean cycle time exceeds the estimate by more than 25 percent, the coordinator PAUSES and reports to the owner with options (continue, add scorers, slow down, or stop). The run continues only on the owner's decision. See section 3.

## 7. Escalation paths

### Blocker table

| Blocker | Who reports | To whom | When | Response |
|---|---|---|---|---|
| Runner session dies | Runner | Coordinator | Immediately | Coordinator restarts a fresh session for that lane, records the restart, resumes from the next task. The dead task is re-run from the start. |
| Scorer silent over 15 minutes with an outstanding task | Coordinator | Parent (Muse) | At 15 minutes | Coordinator checks delivery first (not just the send receipt), then pokes the scorer directly. If silent for 30 minutes, the coordinator reassigns the outstanding tasks to the tiebreaker as a temporary scorer and escalates to the parent. |
| Session lock stale or contested | Runner or coordinator | Coordinator, then parent if unresolved | Immediately | Coordinator verifies the driver process is dead by /proc before clearing. If the lock cannot be cleared safely, the coordinator pauses both lanes and escalates. |
| Manifest gate fails 3 times for one task | Coordinator | Parent (Muse) | At 3rd failure | Coordinator pauses the lane, preserves the evidence, escalates. The task is not marked FAIL on a manifest failure alone. |
| Timeout over 30 minutes | Coordinator | Ledger (record) | At timeout | Task marked FAIL, runner stops, next task proceeds. No escalation unless the timeout recurs (see risk R4). |
| Invalid 3, 4, or 5 reached | Coordinator | Owner (via parent) | Immediately | Coordinator notifies the owner, records the invalid and backup, continues the run. |
| Invalid cap exceeded (6th invalid, or 3rd in a group) | Coordinator | Owner (via parent) | Immediately | Coordinator STOPS the run. Only the owner decides whether to continue, re-freeze, or cancel. |
| Pass bar becomes unreachable (R3-029/R3-075 keys confirmed wrong, or failures exceed 2 before the end) | Coordinator | Owner (via parent) | Immediately | Coordinator STOPS the run. Only the owner decides whether to re-freeze, exclude, or cancel. |
| Correlated service outage (both lanes blocked by the same external cause) | Coordinator | Parent (Muse) | Immediately | Coordinator pauses both lanes, records the event, waits for the service. Maximum wait is set in Phase 0. If the wait exceeds the maximum, the coordinator escalates to the owner. |
| Frozen file changed or hash mismatch | Coordinator | Parent (Muse) | Immediately | Coordinator STOPS the affected lane, preserves the evidence, escalates. No task is graded against a changed key. |
| Coordinator unavailable or unresponsive | Deputy | Parent (Muse) | Immediately | Deputy takes over using the coordinator state file (section 10, objection 26). |
| Any hard constraint broken | Coordinator | Parent (Muse) | Immediately | Coordinator stops the affected lane, preserves the evidence, escalates in writing. |

### Run-stop conditions (only the owner decides)

The coordinator STOPS the run (both lanes) when any of these is true:

1. Invalid cap exceeded (6th invalid total, or 3rd invalid in a difficulty group).
2. Pass bar becomes unreachable (failures plus confirmed invalids make 53/55 impossible).
3. Frozen file changed or hash mismatch.
4. A correlated outage exceeds the maximum wait set in Phase 0.
5. The owner orders a stop.

The coordinator does NOT stop the run for: a single runner death, a single scorer silence, a single timeout, a single invalid, a backpressure pause, or a checkpoint overrun (those pause one lane or trigger a report, not a run stop).

### Scorer replacement

If a scorer is silent for 30 minutes with an outstanding task, or if a scorer's verdict is found to be compromised (for example, it read another scorer's verdict before scoring), the coordinator reassigns its outstanding tasks to the standby tiebreaker for that pair, and escalates to the parent. The replacement scorer must be a fresh session that has not scored that task before. The coordinator records the replacement in the ledger.

Fallback scorer 1 designation (redteam objection 28): the Pair A standby (6e844611) is the designated fallback scorer 1 for Pair A, and the Pair B standby (3f3aca86) is the designated fallback scorer 1 for Pair B, with their declarations already on file. If Mochi (Pair A scorer 1) or 1B (Pair B scorer 1) becomes unavailable, the designated fallback takes over as scorer 1 for that pair so the pair can continue without waiting for the owner or a deputy to name a replacement.

## 8. Risk management

| Risk | Trigger | Response | Owner |
|---|---|---|---|
| R1: Runner death mid-task | Runner process exits or tmux session dies | Coordinator restarts a fresh session for that lane, records the restart, re-runs the dead task from the start. | Coordinator |
| R2: Scorer silence | Scorer does not reply for 15 minutes with an outstanding task | Coordinator checks delivery first, pokes directly. At 30 minutes, reassign to tiebreaker and escalate. | Coordinator |
| R3: Session lock contested | Two drivers need the session, or a stale lock | Second driver waits. Coordinator verifies the driver is dead by /proc before clearing a stale lock. | Coordinator |
| R4: Long task over 30 minutes | Task wall time exceeds 30 minutes | Task marked FAIL, runner stops, next task proceeds. If timeouts recur (3 in a lane), coordinator pauses the lane and escalates. | Coordinator |
| R5: Invalid cluster | 3 invalids reached, or 2 in one group | Coordinator notifies the owner at invalid 3, 4, and 5. At the 6th invalid or 3rd in a group, the run stops. | Coordinator, owner |
| R6: Correlated service outage | Both lanes blocked by the same external cause (for example, a website down, a service 429) | Coordinator pauses both lanes, records the event, waits. Maximum wait set in Phase 0. If exceeded, escalate to the owner. | Coordinator, owner |
| R7: Scoring lag and backpressure | Outstanding unscored tasks reach 2 per runner, or lag exceeds 30 minutes | Coordinator pauses that runner (the other lane continues). Resume when the count drops below 2. | Coordinator |
| R8: Tiebreaker dispute | Scorers disagree, or an invalid is disputed, or a key dispute is raised | Coordinator calls the pre-named tiebreaker with the exact blind packet. Tiebreaker verdict is final for that task. | Coordinator |
| R9: Frozen file drift | Hash mismatch on list or keys, or a frozen file edited | Coordinator stops the affected lane, preserves the evidence, escalates. No task is graded against a changed key. | Coordinator, parent |
| R10: Coordinator overload | Coordinator serial work (55 manifest gates, 110 audits, 55 ledger appends, 9 Tier A runs) exceeds its capacity | Coordinator reports at the checkpoint with measured times. If the coordinator is the bottleneck, the owner decides whether to add a second coordinator for audit only (never for ledger writes). | Coordinator, owner |
| R11: Class L miscount | The exception list misses a task that needs a live re-read | Coordinator moves the task to Class L on discovery, records the move, republishes the list. If the task already ran as Class S, its verdict is voided and the task is re-run as Class L. | Coordinator |
| R12: Snapshot or verdict collision | Two agents write to the same snapshot or verdict path | The -L3 suffix and the per-scorer verdict filenames prevent this. If a collision is found, the coordinator stops the affected lane, preserves both copies, and escalates. | Coordinator |
| R13: Inter-pair drift | Pair A and Pair B grade the same difficulty differently | Coordinator reports inter-pair agreement after each pair's first 3 graded tasks. If agreement differs by more than 1 task, the coordinator calls a council review before the next task in the affected pair. | Coordinator |

## 9. Communication

### How subagents report

- Every subagent reports to the coordinator ONLY, in writing, in its own session. No subagent reports directly to the owner, to the parent (Muse), or to another subagent. No subagent messages the owner.
- A runner reports: task started, task evidence-ready (with snapshot path and manifest), task failed or timed out, session died, session lock contested. A runner does not report a verdict.
- A scorer reports: verdict for a task (with the verdict file path), invalid proposal (with reason and evidence), key dispute (with exact key text and evidence), or silence (it reports when it is ready for the next task).
- A tiebreaker reports: verdict for the invoked task only.
- The coordinator reports to the parent (Muse) only. The coordinator never messages the owner directly.

### How the coordinator reports to the parent (Muse)

- Per task: the ledger row (task ID, verdict, scorer pair, tiebreaker if invoked, invalid or backup if any, elapsed time). The coordinator reports each graded task as it lands, in writing.
- Blockers: immediately, in writing, when any item in the blocker table (section 7) fires.
- Invalid 3, 4, and 5: immediately, in writing.
- Checkpoint: after the 3rd graded task, with the recomputed estimate and the decision rule applied.
- Run-complete: when position 55 evidence is frozen, with the run-complete timestamp.
- Ledger-complete: when the ledger is pushed and verified, with the ledger-complete timestamp.
- Closure: the closure report (section 3, Phase 3).

### What is NOT reported

- Ordinary progress (a task started, a snapshot sealed, a grade in progress) is not reported to the owner. The owner sees only the coordinator's reports to the parent, and the parent decides what to tell the owner.
- A single timeout, a single backpressure pause, or a single runner restart is not reported to the owner. It is recorded in the ledger and the run log.
- The owner is notified only at: invalid 3, 4, and 5; a run stop; a checkpoint overrun; a hard constraint breach. This is the owner's standing rule (serious only), except that during the active run the parent may report more often at its discretion.

### Reporting cadence

- Ledger push: at least hourly, immediately on any invalid or dispute.
- Coordinator to parent: per graded task, plus blockers immediately, plus the checkpoint, plus run-complete and ledger-complete.
- No hourly status message to the owner. The owner is not nagged with progress updates.

## 10. Redteam objections and answers

The redteam read every file first-hand and returned 46 objections with verdict NOT READY FOR TASK 1. The council answers each one below. No objection is dismissed without an answer. A fix is a precondition (section 11) with a named owner. An accepted risk is recorded with an owner and a date. A plan fix is already written into this document in the section named.

### A. Overlaps and conflicts

1. DP-01 retired but listed as live backup. BLOCKS RUN. ANSWER: FIX. Phase 0 precondition 1. Remove DP-01 from both du-phong files, write the medium order as DP-03, DP-06, DP-07 in both files, record the correction with a timestamp, and have the coordinator verify both files match byte for byte before task 1. Owner: coordinator. The plan's backup order (section 1) already excludes DP-01; the files must be corrected to match.
2. Two divergent du-phong files, no canonical source. BLOCKS RUN. ANSWER: FIX. Phase 0 precondition 1. Overwrite the laptop file with the corrected R3-L3 content (after objection 1 is fixed), declare in thu-tu-chay.txt that the laptop ~/du-phong.txt is canonical and the repo copy is a mirror, and verify both match byte for byte before task 1. Owner: coordinator.
3. Snapshot name collision with R3-L2. MUST FIX. ANSWER: FIX. Phase 0 precondition 13. Name R3-L3 snapshots R3-xxx-L3 (never R3-xxx-s1), create the directories before task 1, verify no R3-L2 snapshot path is reused. Owner: coordinator. The plan's snapshot pattern (section 5) already uses the -L3 suffix.
4. Stale R3-L2 evidence in the evidence folders. BLOCKS RUN. ANSWER: FIX. Phase 0 precondition 2. Wipe and recreate ~/rung3-chung-cu/ and restore fixtures from ~/rung3-goc/ before task 1, record the wipe with timestamps in the run log, and verify the R3-001 folder is empty before the runner starts. Owner: coordinator.
5. Run file orders both serial and decoupled scoring. MUST FIX. ANSWER: FIX. Phase 0 precondition 14. Rewrite the handoff and scoring-window sections of thu-tu-chay.txt to state the decoupled rule, the Class L exceptions by ID, and the backpressure cap, and have the coordinator confirm both runners have read the rewritten section. Owner: coordinator.
6. Runner session IDs still TBD. MUST FIX. ANSWER: FIX. Phase 0 precondition 4. Record both runner session IDs in thu-tu-chay.txt before task 1. A process PID is not a session ID. The sessions are fresh (objection 39). Owner: coordinator.
7. Three concurrent drivers, one undocumented lock. MUST FIX. ANSWER: FIX. Phase 0 precondition 19. Interleaving rule: when Mochi (or any scorer) needs to drive live for a Class L task, the other lane's runner pauses driving until the scorer releases the session. The coordinator coordinates the handoff and records it. The /proc fd scan command is documented verbatim in Phase 0 with its expected output, and the coordinator is the person who runs it. Owner: coordinator. The rule is added to section 5 by amendment.
8. Shared services and fixtures across lanes, no shared-resource table. SHOULD FIX. ANSWER: FIX (cheap). Phase 0 precondition 15. Publish a one-page shared-resource table (service and fixture directory per task) before task 1, and state the pause rule: when a shared service returns 429 or a bot check in either lane, the coordinator pauses both lanes' tasks on that service until the service recovers, and records the pause. Owner: coordinator.
9. Coupled-task mitigation is one sentence, not a procedure. SHOULD FIX. ANSWER: FIX (cheap). Phase 0 precondition 16. Write the two coupled checks as concrete steps with a pass/fail criterion, assign them to the coordinator, and run them when the second task of each pair is graded (R3-078 with R3-079; R3-067 with R3-083), not at the end. The checks are: (a) for R3-078/R3-079, compare the two verdicts and the shared file set state, and flag if the verdicts are inconsistent with the shared fixture; (b) for R3-067/R3-083, record whether both used the same drawing approach or not, and flag if the approaches differ without a reason in the evidence. Owner: coordinator. The rule is in section 6.
10. Ledger append has no writer protocol and the file does not exist. MUST FIX. ANSWER: FIX. Phase 0 precondition 11. Create R3-L3-grades.jsonl plus its schema before task 1, write one trial row, validate it, commit it, and state the append protocol (one writer, the coordinator, sequential commits, no concurrent appends). Owner: coordinator.
11. Scorer identities are session IDs only, and Mochi's role text is stale. SHOULD FIX. ANSWER: FIX (cheap). Phase 0 precondition 14 (part of the thu-tu-chay.txt rewrite). Add names for all four new sessions, correct line 38 to Pair A only (Mochi scores positions 1-28, not every task), and record how each session's independence was verified (not Mei, not a runner, no authorship, no trial run). Owner: coordinator.

### B. Gaps

12. No manifest-gate script exists. MUST FIX. ANSWER: FIX. Phase 0 precondition 7. Name the script, commit it, run it against a trial folder (must pass) and an empty folder (must fail), record both outputs, and state the failure branch (section 5: runner does not proceed, no reset, re-collect, re-run gate, 3 failures then pause the lane and escalate). If no script exists, the coordinator writes one before task 1. The gate also includes the pre-reset content check from objection 23. Owner: coordinator.
13. No audit scan exists. MUST FIX. ANSWER: FIX. Phase 0 precondition 7. Write the scan, or state honestly that the audit is manual. The plan states honestly: for subagent scorers, the coordinator reviews tool calls (or the verdict file and its read list); for Mochi (a Chromium session on the laptop), the audit is manual (the coordinator reviews her messages and the files she reports reading in the browser session). Define the audit record per grade (scorer, task, files read, forbidden reads found or none, auditor signature). Owner: coordinator.
14. No timeout enforcement mechanism. MUST FIX. ANSWER: FIX. Phase 0 precondition 8. Name the watcher (the coordinator, checking wall-clock time every 5 minutes during a run), the kill command for each runner (the coordinator stops the runner's task via its session), the check interval (5 minutes), and the partial-evidence rule (evidence kept, scoring skipped, task marked FAIL). Owner: coordinator.
15. No deputy coordinator. MUST FIX. ANSWER: FIX. Phase 0 precondition 9. Name the deputy with session ID and declaration before task 1. Owner: coordinator (names the deputy), parent (Muse) confirms.
16. No backup-assignment procedure across pairs. SHOULD FIX. ANSWER: FIX (plan). Section 6 now states the full procedure: the backup runs in the same lane as the task it replaces, at the next position after the invalid decision (not at the end of the lane), inherits the pair of the task it replaces, and if it is DP-02 (Class L, score-before-reset) the runner waits for scoring before the reset. Owner: coordinator.
17. No R3-089 fixture-refresh confirmation. SHOULD FIX. ANSWER: FIX (cheap). Phase 0 step 9 and precondition 17. Assign an owner and a date for the refresh, and record the confirmation (refresh time, new mtimes of 6 files, find returning exactly 6 files) in the run log before position 49 runs. Hard deadline 2026-11-29 19:20. Owner: coordinator (assigns the owner in Phase 0).
18. No R3-029 account and product-name confirmation. MUST FIX. ANSWER: FIX. Phase 0 precondition 5 (part of the key verification). Produce the account confirmation and the 5-name check in writing before task 1, or declare R3-029 invalid before task 1 with the backup rule applied. Owner: coordinator.
19. Calibration has no auditable record and tests the wrong skills. MUST FIX. ANSWER: FIX. Phase 0 precondition 10. Re-run calibration with one Tier C task and one B-hybrid task added, keep the signed calibration grades as files, and have someone other than the coordinator verify them before task 1. Owner: coordinator (runs it), independent verifier (verifies it).
20. No checkpoint decision rule. SHOULD FIX. ANSWER: FIX (plan). Section 3 now states the rule: if the revised run-complete is outside 19-21 hours, OR if the mean cycle time exceeds the estimate by more than 25 percent after the 3rd graded task, the coordinator PAUSES and reports to the owner with options (continue, add scorers, slow down, or stop). The run continues only on the owner's decision.
21. No hourly ledger-push mechanism. SHOULD FIX. ANSWER: FIX. Phase 0 precondition 20. Create the push job (a cron job or a background timer owned by the coordinator) that pushes the ledger hourly, define the retry rule (retry once after 5 minutes, then escalate to the parent), and define what happens if a push fails twice (the coordinator escalates to the parent and the local ledger remains the authority). Owner: coordinator.
22. No procedure when the manifest gate fails. SHOULD FIX. ANSWER: FIX (plan). Section 5 now states the failure branch: the runner does NOT proceed, NO reset happens, the coordinator logs the failure, the runner re-collects the missing or changed evidence, the coordinator re-runs the gate, and the runner proceeds only after the gate passes. If the gate fails three times for the same task, the coordinator pauses the lane, preserves the evidence, and escalates in writing to the parent. The task is not marked FAIL on a manifest failure alone.
23. The exception-list fail-safe cannot work after a reset. SHOULD FIX. ANSWER: FIX (plan). Add a pre-reset check to the manifest gate: before resetting a Class S task, the coordinator confirms the snapshot contains every file the key's "Vat chung cham" line names for that task. If a file is missing, the task is treated as Class L for that run (score-before-reset) and the exception list is corrected. This check is part of Phase 0 precondition 7. Owner: coordinator.

### C. Timeline

24. The estimate has no per-task run-time table and ignores the coordinator's serial load. MUST FIX. ANSWER: FIX (plan). Section 3 now publishes a time budget with a line for coordinator serial work (55 manifest verifications at about 2 minutes each is 1.8 hours; 110 grade audits at 5 minutes each is about 9 hours; 55 ledger appends; 9 Tier A checker runs; invalid and tiebreaker handling) and states the honest range (19 to 31 hours). The 19-21 hour figure is a lower bound, not a forecast. The coordinator publishes the per-task run-time assumption in Phase 0 step 10. Owner: coordinator.
25. The R3-L2 observed rate contradicts the baseline. MUST FIX. ANSWER: FIX (plan). Section 3 runs the checkpoint after the first 3 graded tasks with the decision rule from objection 20, and the plan does NOT promise the owner a 20-hour finish. The run is staffed and scheduled for 31 hours, not 20 hours. Owner: coordinator.

### D. Single points of failure

26. The coordinator is the only whole-run view, no deputy, no handover state. BLOCKS RUN. ANSWER: FIX. Phase 0 precondition 9. Name a deputy with session ID and declaration before task 1, and keep a coordinator state file (next task per lane, unscored queue, invalid counts, backup consumption) updated after every task so a deputy can resume. Owner: coordinator (names the deputy), parent (Muse) confirms.
27. The run file itself is a single point of silent mutation. SHOULD FIX. ANSWER: FIX (cheap). Phase 0 precondition 14 (part of the rewrite). Stamp every edit with a timestamp and editor, and record the file's sha256 in the run log at task 1 start. Owner: coordinator.
28. Mochi is a single point for Pair A scorer 1. SHOULD FIX. ANSWER: FIX. Designate the Pair A standby (6e844611) as the fallback scorer 1 for Pair A, and the Pair B standby (3f3aca86) as the fallback scorer 1 for Pair B, with their declarations already on file, so a pair can continue if its scorer 1 becomes unavailable. This is added to section 7 by amendment. Owner: coordinator.
29. The laptop is a single point for all evidence. SHOULD FIX. ANSWER: FIX (cheap). Phase 0 precondition 11 (part of the ledger protocol). Push the ledger immediately after every task for the first 10 tasks (until the pipeline is proven), then hourly; and copy each snapshot to the repo the same day it is created. Owner: coordinator.
30. The daemon send queue is a single point for coordinator communication. SHOULD FIX. ANSWER: FIX. Phase 0 precondition 18. Name a fallback channel (direct SSH to the laptop plus the speed-lean fallback at ~/workspace/speed-lean/) and test it before task 1. Owner: coordinator.
31. The cursor.lock mechanism is a single undocumented gate. ACCEPTED RISK (recorded, not fixed here). ANSWER: The council accepts the risk as recorded by the speedup council (residual risk 4), but the documentation gap is closed in Phase 0 precondition 19: the scan command is documented verbatim with its expected output before task 1. Owner: coordinator.

### E. Accuracy risks from the speedup itself

32. At least one Class S task is provably misclassified, four more rest on an unproven snapshot assumption. BLOCKS RUN for R3-096; MUST FIX for the rest. ANSWER: FIX. Phase 0 precondition 3. Move R3-096 to Class L now (the key's own words prove it: the scorer re-runs diff on live files the reset restores, so a post-reset diff shows 4, not 3). For R3-078, R3-088, R3-093, R3-079, either move them to Class L or publish the per-task snapshot contents proving each required file is copied into the snapshot, and make the manifest gate check for those files by name. The exception list is republished before task 1 with the corrected Class L set. The Class L count is therefore 6 minimum, possibly up to 10, and the time estimate in section 3 is revised for this. Owner: coordinator.
33. R3-100's live port check has no scoring window. SHOULD FIX. ANSWER: FIX. Phase 0 precondition 21 and section 6 amendment. R3-100 is graded from the saved report and HTML files only. The live port check (port 8899 closed) is done by the runner at run time, immediately after the task, and recorded in the evidence. The scorer grades from that recorded port state, not from a live check hours later. Owner: coordinator.
34. Tier A single-run creates a correlated failure. SHOULD FIX. ANSWER: FIX (plan). Section 3 (Phase 1) already requires the checker input hash (snapshot manifest hash plus key hash) to be recorded with the single output, and each scorer verifies the output against the snapshot files they can see. If the checker script cannot be located (objection 12), Decision D cannot be executed at all, and the coordinator must resolve that in Phase 0 precondition 7 before task 1. Owner: coordinator.
35. Inter-pair drift is real and the mitigations do not measure it in time. MUST FIX. ANSWER: FIX. Phase 0 precondition 10 (calibrate Pair B on one Tier C and one B-hybrid task) plus section 8 risk R13 (report inter-pair agreement after each pair's first 3 graded tasks, with a named threshold that triggers a council review: if agreement differs by more than 1 task, the coordinator calls a council review before the next task in the affected pair). Owner: coordinator.
36. Async ledger push risks losing grades. SHOULD FIX. ANSWER: FIX (plan). Section 3 (Phase 2) already sets the ledger-complete deadline (within 2 hours of run-complete, owner is the coordinator) and the push rule (immediately after every invalid, dispute, and the first 10 tasks; then at least hourly). Owner: coordinator.

### F. Rolling (cuon chieu) execution risk

37. Pair B was named minutes before task 1 and verified by nobody independent. MUST FIX. ANSWER: FIX. Phase 0 precondition 10. Have someone other than the coordinator verify Pair B's declarations and calibration files before task 1, or hold the Codex lane start until that verification lands. Do not let task 1 start on a promise about position 29. Owner: independent verifier (not the coordinator).
38. The exception list is wrong in the one place that matters most for the rolling start. BLOCKS RUN (same defect as objection 32, stated here for its rolling consequence). ANSWER: FIX. Phase 0 precondition 3 (move R3-096 and resolve the four more) plus a pilot. Pilot the decoupling on the first Class S task (R3-002, Tier A, simple evidence): verify the snapshot contents against the key's evidence line before the runner proceeds to task 3, and only then continue decoupled. If the pilot snapshot is incomplete, revert to serial for the affected task class. The pilot is added to Phase 1 by amendment. Owner: coordinator.
39. Reusing the same runner sessions breaks the held-out rule for 11 tasks. BLOCKS RUN. ANSWER: FIX. Phase 0 precondition 4. Start fresh runner sessions for R3-L3 and record their session IDs (objection 6). The old sessions (FCC PID 2046632, Codex PID 1235041) ran R3-L2 tasks and must not be reused. If fresh sessions are impossible, record in writing that the 11 repeated tasks are not held-out for their runners and scorers, and exclude them from any held-out claim about the run. Owner: coordinator.
40. DP-01 reuse contradicts the freeze and the R3-L3 decision. BLOCKS RUN (same defect as objection 1). ANSWER: FIX. Same as objection 1 (Phase 0 precondition 1). Owner: coordinator.

### G. Contradictions with hard constraints

41. Pass-bar arithmetic: if the repo note is right, the run cannot pass. MUST FIX. ANSWER: FIX. Phase 0 precondition 5. Verify the R3-029 and R3-075 keys before task 1. If either key is truly wrong, either re-freeze with corrected keys (new freeze, new hashes, owner approval) or exclude the task before task 1 with the pass bar recomputed in advance. Do not start a run whose bar is already unreachable. If both keys are wrong, the run needs 53 passes from 53 remaining tasks, which is not a measurement. The owner decides before task 1. Owner: coordinator (verifies), owner (decides if wrong).
42. Invalid-cap headroom is nearly exhausted before task 1. MUST FIX. ANSWER: FIX. Phase 0 precondition 6. Verify or declare each of the four pre-run invalid candidates (R3-011, R3-028, R3-036, R3-046) before task 1, with difficulty-group mapping, and confirm the R3-009 WAVE re-check result in writing with all 5 numbers per page (the cited gate at 16:31-16:32 records only Errors counts). Owner: coordinator.
43. Calibration on R3-L2 rows breaks scorer blindness for repeated tasks. SHOULD FIX. ANSWER: ACCEPTED LIMITATION (recorded). Do not use repeated tasks for calibration in future rounds. For this round, record the exposure as a limitation in the run log and do not cite Pair B's R3-041 grade as independent evidence. The R3-041 calibration grade is a rehearsal record, not an independent verdict. Owner: coordinator. This is Phase 0 precondition 22.
44. The 30-minute timeout contradicts R3-L2 precedent and has no enforcement. MUST FIX. ANSWER: FIX. Phase 0 precondition 8 (enforcement mechanism, objection 14) plus a list. Publish the list of tasks (if any) whose legitimate run exceeds 30 minutes, with the owner's decision on each, before task 1. If no task legitimately exceeds 30 minutes, record that in writing. The R3-L2 violations (R3-040 4h05, R3-042 50 minutes) are recorded as precedent that must not recur. Owner: coordinator (publishes the list), owner (decides on any exemption).
45. Laptop run file does not record the current tip. SHOULD FIX. ANSWER: FIX (cheap). Phase 0 precondition 14 (part of the rewrite). Record tip 175cfd7 and the du-phong commit 6a7d31c in thu-tu-chay.txt before task 1. Owner: coordinator.
46. No R3-L3 liveness or preflight sign-off is cited. MUST FIX. ANSWER: FIX. Phase 0 precondition 12. Produce the R3-L3 liveness report (service checks, test accounts log in, fixtures exist, DP-03 port count, R3-009 URLs, quota) with a named sign-off before task 1, or state in writing which checks were skipped and why. Owner: coordinator (produces it), named signer (signs it).

## 11. Pre-task-1 precondition checklist (all must be green, verified with files, not assertions)

The redteam's 14-item checklist is reproduced here (items 1-14) and extended with the additional preconditions from the council's answers (items 15-22). Task 1 releases only when every item is green.

1. DP-01 removed from both du-phong files; laptop and repo du-phong files byte-identical; laptop file declared canonical. (Objections 1, 2, 40)
2. Evidence folders wiped and recreated; R3-001 folder empty before the runner starts. (Objection 4)
3. R3-096 moved to Class L; R3-078, R3-088, R3-093, R3-079 either moved to Class L or proven snapshot-sufficient per task; exception list republished. (Objections 32, 38)
4. Fresh runner sessions started; session IDs recorded in thu-tu-chay.txt; or the 11 repeated tasks recorded as not held-out. (Objections 6, 39)
5. R3-029 and R3-075 keys verified; if wrong, re-freeze or exclude with a recomputed bar before task 1; R3-029 account and product names confirmed in writing. (Objections 18, 41)
6. Four pre-run invalid candidates declared or verified, with group mapping; R3-009 WAVE re-check recorded with all 5 numbers per page. (Objection 42)
7. Manifest-gate script and audit scan named, committed, and proven (pass on trial, fail on empty); pre-reset snapshot content check defined (the snapshot must contain every file the key's "Vat chung cham" line names). (Objections 12, 13, 23)
8. Timeout watcher, kill procedure, and partial-evidence rule named; list of tasks (if any) whose legitimate run exceeds 30 minutes published with the owner's decision on each. (Objections 14, 44)
9. Deputy coordinator named with declaration; coordinator state file defined (next task per lane, unscored queue, invalid counts, backup consumption), updated after every task. (Objections 15, 26)
10. Pair B declarations and calibration verified by someone other than the coordinator, with signed calibration grades on file including one Tier C and one B-hybrid task. (Objections 19, 35, 37)
11. R3-L3 ledger file created with schema, trial row validated and committed; append and push protocol written (one writer, sequential commits; push immediately after every invalid, dispute, and the first 10 tasks, then at least hourly; copy each snapshot to the repo the same day). (Objections 10, 29, 36)
12. R3-L3 liveness report signed off by a named person (or skipped checks stated in writing with reasons). (Objection 46)
13. Snapshot naming scheme fixed (R3-xxx-L3 suffix) so no R3-L2 snapshot is overwritten; snapshot directories created before task 1. (Objection 3)
14. Thu-tu-chay.txt rewritten (decoupled handoff and scoring-window, Pair A only for Mochi, names for all four new sessions, runner IDs, tip 175cfd7, du-phong commit 6a7d31c, deputy) and timestamped; sha256 recorded in the run log at task 1 start. (Objections 5, 6, 11, 27, 45)
15. Shared-resource table published (service and fixture directory per task); pause rule on 429 or bot check stated. (Objection 8)
16. Coupled-task checks written as concrete steps with pass/fail criteria (R3-078/R3-079, R3-067/R3-083), assigned to the coordinator, run when the second task of each pair is graded. (Objection 9)
17. R3-089 fixture-refresh owner and date assigned; confirmation procedure defined (refresh time, new mtimes of 6 files, find returning exactly 6 files). (Objection 17)
18. Daemon fallback channel named (direct SSH plus speed-lean) and tested before task 1. (Objection 30)
19. Interleaving rule for 3 drivers written (Class L scoring pauses the other lane's driving); /proc fd scan command documented verbatim with expected output; coordinator named as the person who runs it. (Objections 7, 31)
20. Ledger push job created (cron or background timer, owned by the coordinator); retry rule defined (retry once after 5 minutes, then escalate); push-failure escalation defined. (Objection 21)
21. R3-100 port check rule defined (runner records the port state at run time; scorer grades from the recorded port state and the saved report and HTML files only). (Objection 33)
22. Calibration exposure limitation recorded in the run log (Pair B's R3-041 grade is a rehearsal record, not an independent verdict; do not cite it as independent evidence). (Objection 43)

## 12. Goals and definition of done

### Goals

- Prove the computer-use tool works reliably for the Muses on 55 real tasks, with a pass bar of 53/55.
- Run the acceptance test in a way that is defensible: held-out tasks, independent scoring, evidence versus key, no reused sessions, no retired backups, no stale evidence.
- Finish in 19-31 hours of wall time (staffed for 31 hours, not promised at 20 hours).
- Produce a ledger that is complete, signed, and pushed, with run-complete and ledger-complete as separate timestamps.

### Definition of done for the plan

- This file exists, is super detailed and actionable, and has 0 em dashes and 0 en dashes (verified by command).
- Every redteam objection (46) has an answer in section 10.
- The precondition checklist (section 11) is complete and each item has a named owner and a verification method.
- The run coordinator has the file and can execute it without guessing.

### Definition of done for the run

- All 55 tasks run in fixed order, two lanes in parallel, scoring async behind the runners.
- Every run task graded by two independent scorers in its pair, with the tiebreaker called only on disagreement, disputed invalid, or formal key dispute.
- Ledger complete: 55 rows or fewer only where the invalid and backup rules explain the count, every row signed, every invalid countersigned with its backup recorded in du-phong.txt.
- Frozen hashes verified unchanged at closure.
- Pass or fail called against 53/55 (recomputed only by an owner decision before task 1 if the valid count shrank).
- Closure report written and reported to the owner with run-complete and ledger-complete as separate timestamps.

### Residual risks (accepted, with owners)

- The cursor.lock mechanism is undocumented in frozen files. Accepted by the speedup council (residual risk 4). The documentation gap is closed in Phase 0 precondition 19. Owner: coordinator.
- The 19-21 hour estimate is a lower bound. The honest planning range is 19-31 hours. A correlated service outage is unbounded until the pause rule's maximum wait is written in Phase 0. Owner: coordinator.
- The Class L count may rise from 5 to 6-10, which returns serial wait to those lanes and reduces the decoupling saving. The estimate is revised at the checkpoint. Owner: coordinator.
- Mochi re-scores 11 tasks she already scored in R3-L2, knowing the prior verdicts. This is a limitation of the repeated tasks, recorded in the run log (precondition 22). The independence check is scorer 2 plus the tiebreaker. Owner: coordinator.
- The R3-L2 observed rate (about 1.5 hours per task of wall time) contradicts the baseline. The checkpoint after the first 3 graded tasks replaces assumption with measurement. Owner: coordinator.

## Appendix Z: Zen 1.24.3b run rules (added 2026-11-24, deep dive)

Laptop ground truth at probe time: Zen 1.24.3b, BuildID 20261118023529, Firefox 160.0.1, PID 381258, ports 9222 and 2828 listening on 127.0.0.1, profile `~/.config/zen/********.Default (release)/`, 1 window, 72 tabs, 49 pinned, 30 GB RAM with 17 GB available, Zen RSS about 2.5 GB. One tab content process burns about 49 percent CPU sustained (owner tab, identity unknown without a live check, never close it unilaterally, see rule Z4). Full evidence: `rung3-run-log/r3-l3-zen-1.24.3b-optimizations-20261124.md` on todolist-push.

- Z1. Runner tab hygiene. Each runner works in ONE dedicated task tab and reuses it by navigation. A new tab per task is forbidden. After a task's evidence is sealed, the runner closes every tab or popup IT created for that task, except its one dedicated task tab. NEVER close, unload, or navigate any of the owner's 72 baseline tabs. Cap: at most 2 runner-created tabs per runner. Reason: on Linux Firefox does not auto-unload tabs by default, and Zen removed its own unload timer, so opened tabs stay loaded for the whole run unless the runner closes them.
- Z2. BiDi session end-on-handover. Firefox allows exactly ONE BiDi session at a time, and the session OUTLIVES its WebSocket connection. Dropping the socket or killing the driver does NOT free it. Whoever holds the session MUST call session end before handing over. The next driver checks `session.status` before creating its session. On "Session already started": do NOT retry in a loop, report to the coordinator and use rule Z3.
- Z3. Mid-run Zen restart point. When: at the first task boundary AFTER the FCC lane completes (position 28), or after 12 hours of run wall time, whichever comes first. Also immediately on any zombie BiDi session or if Zen total RSS passes 8 GB. Steps: pause BOTH lanes at task boundaries; current BiDi holder ends its session cleanly; clean quit of Zen (never `kill -9`, because a second consecutive unclean start shows the session-restore prompt and blocks automation); verify no zen-bin processes and ports 9222/2828 free; relaunch via the `zen-ai` wrapper (supplies `--remote-debugging-port=9222 --marionette`); verify ports listening, `WebDriverBiDiServer.json` shows ws_port 9222, version is still 1.24.3b (BuildID 20261118023529), tabs restored, and a new BiDi session is accepted; record restart time, RSS before and after, and the version check in the run log; resume both lanes. If the version is not 1.24.3b after restart, STOP and escalate to the owner.
- Z4. Pre-task-1 live checks (coordinator). Identify the hot tab via `about:processes` and close it ONLY if it is a runner or test leftover (for example `file:///tmp/pill-video/fixture.html` or the `example.com` driver-test tab). If it is an owner tab, leave it and record the CPU cost. Open `about:unloads` once and record the unload priority order as a baseline.
- Z5. Do NOT set `browser.tabs.unloadOnLowMemory=true` before task 1. Enable it ONLY if Zen RSS passes 8 GB mid-run, applied at the Z3 restart point. Pinned tabs are only deprioritized by the unloader, not exempt, so a pre-emptive enable risks unloading a reference or Class L re-read tab.
- Z6. Update freeze. The run stays on 1.24.3b. VERIFIED 2026-11-24 evening (clone1-report applicator): `app.update.enabled=false` and `remote.prefs.recommended=false` are both in user.js AND effective in prefs.js after the 19:59 restart; no staged update exists (no install `updates/` dir, no profile `updates/` dir, no `updates.xml` / `active-update.xml`); running Zen is PID 404548, 1.24.3b BuildID 20261118023529, ports 9222/2828 listening. Firefox 161.0 released 2026-11-24, so a Zen rebase is coming, but with the pin effective and nothing staged, no update can fetch or apply during the run. The install does ship an `updater` binary, so the pref (not the absence of an updater) is the guard. Live about:config was not read (needs a BiDi/Marionette session; single-session rule); file evidence is the verification.
- Z7. Already optimal, no action: background video suspend is on by default; Firefox 160 BiDi perf (bug 2075175) is in; gh-16587 and gh-16624 are in; pill optics and launch line are correct. Do NOT apply pastebin user.js tables, process-count cuts, sessionstore gutting, auto-unload extensions, screenshot readback, or experimental BiDi prefs. Rejected with reasons in the evidence file.
