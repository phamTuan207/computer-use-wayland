# R3-L3 Scorer Brief Addendum (supersedes R3-L2 briefs for the R3-L3 run)

- Run: R3-L3, 55 tasks, starts 2026-11-25 on the owner's word. This addendum supersedes any conflicting part of the R3-L2 scorer briefs (rung3-scorer1-mochi-brief.md, rung3-scorer2-brief.md, rung3-scorer3-tiebreaker-brief.md) for the R3-L3 run. The independence conditions, allowlist, denylist, and invalid rules in those briefs still apply unless this addendum states otherwise.
- Frozen key: docs/rung3-answer-keys.md sha256 21f8b61a, docs/rung3-answer-keys.json sha256 5059f6c4. List: docs/rung3-list-100-tasks.md sha256 c1d9a220. Pass bar 53/55. Invalid cap max 5 total, max 2 per difficulty group. No key/list edit after task 1.
- Branch: todolist-push, tip fa72d87. Execution plan: ~/workspace/r3-l3-execution-plan-20261124.md (565 lines, authoritative).

## Pairs (lane-aligned)

- Pair A (positions 1-28, FCC lane, R3-001 to R3-037): scorer 1 Mochi (70cd99d1), scorer 2 dc7e0d0d, tiebreaker 97290681 (TB-A, calibration 4/4 APPROVED).
- Pair B (positions 29-55, Codex lane, R3-040 to R3-100): scorer 1B 4e2f52d4, scorer 2B 2e3ae678, tiebreaker df4defcc (TB-B2, calibration 4/4 APPROVED). Original TB-B (3f3aca86) is NOT used.
- A backup inherits the pair of the task it replaces. DP-01 is retired and is never assigned. Medium backups in order: DP-03, DP-06, DP-07. Hard: DP-02 only (Class L). Very hard: DP-05 only.
- Mei is disqualified as a scorer (authored the list and keys). She does review/analysis only.

## Decoupled scoring (this replaces the R3-L2 serial rule)

- Class S (46 tasks): score ASYNC from the sealed snapshot (~/workspace/rung3-snapshots/R3-xxx-L3/) AFTER the runner proceeds. The runner does NOT wait for your grade. The "score each task BEFORE its reset" line in the R3-L2 brief does NOT apply to Class S tasks in R3-L3.
- Class L (9 tasks, score-before-reset, runner waits): R3-001, R3-055, R3-074, R3-075, R3-089, R3-096, R3-078, R3-079, R3-088. Score from the LIVE state before the reset. Full list: rung3-run-log/r3-l3-exception-list.txt.
- R3-001 (position 1, Pair A, the only Class L task in Pair A): the todos live in the runner's Zen browser storage, which your Chromium cannot read. Procedure: the runner leaves the TodoMVC tab open with the final list visible; the coordinator reads the live todo list via CDP from the Zen session and writes the live state (todo list JSON + screenshot) into the snapshot R3-001-L3; you compare that live state plus ket-qua.txt against the key. You do NOT open TodoMVC in your own Chromium (it would show an empty list). If the coordinator cannot capture the live state, tell the coordinator before grading; do not guess.
- Tier A tasks (Pair A: R3-002, R3-007, R3-013, R3-014, R3-021): the coordinator runs the checker once and hands the identical output to both scorers. You still do the human check (evidence files exist, screenshot legible) and sign your own verdict.

## Grade file and key hash

- Grade file name (R3-L3): rung3-scorer1-R3-xxx-L3-grade.md for scorer 1 (Mochi), rung3-scorer2-R3-xxx-L3-grade.md for scorer 2, and the same -L3 pattern for Pair B (rung3-scorer1B- / rung3-scorer2B-) and tiebreaker files. The -L3 suffix is mandatory to avoid collision with R3-L2 grade files.
- Key hash in the grade file: record BOTH hashes. keyfile_sha256 (ledger field) = the JSON hash 5059f6c4. Also record the md hash 21f8b61a in the grade file. The coordinator copies the JSON hash (5059f6c4) into the ledger row.
- Verdict file (machine-readable): ~/workspace/rung3-verdicts/R3-xxx-A1.json (Pair A scorer 1), R3-xxx-A2.json (Pair A scorer 2), R3-xxx-B1.json, R3-xxx-B2.json, R3-xxx-TB.json (tiebreaker only when invoked). VM-local, never committed.

## Scoring deadline and order

- Target: score within 30 minutes of handoff (keeps the pipeline flowing, avoids pausing the runner). Hard limit: 60 minutes (R3-L2 precedent). If you receive 2 tasks, score in position order (lowest position first).
- Backpressure: max 2 unscored tasks per runner. If scoring lags over 30 minutes, the coordinator pauses that runner (the other lane continues).

## Handoff channel

- Primary: the coordinator sends you a daemon message per task (task ID + snapshot path). 
- Fallback: if no daemon message arrives within 10 minutes of a task finishing, check the run-log on GitHub (rung3-run-log/) for the handoff note, and tell the coordinator the daemon message did not arrive.
- Report verdicts to the coordinator only, in writing. Never message the owner directly. Never contact the runner directly.

## Tiebreaker and audit

- Tiebreaker packet (exact): scorer 1 verdict, scorer 2 verdict, evidence manifest, key excerpt. The tiebreaker does NOT see the runners' outcomes, the other pair's verdicts, or the live state. The coordinator assembles the packet; you provide nothing extra.
- Audit: the coordinator audits your first 2 grades of each new task type (Tier A, Tier C, B-hybrid, Class L) before those grades enter the ledger. If your grade is overturned on audit, the coordinator tells you, re-assigns the task to the other scorer in your pair, and records the overturn. You do NOT re-score that task. Two overturns for the same scorer trigger a re-calibration (re-do the 4-task calibration before grading again).
- Calibration limitation (recorded): the 4-task calibration proves you can grade those 4 task types, not all 55. The coordinator audit is the guarantee, not calibration alone.

## Invalid (pre-run candidates and cap math)

- Pre-run invalid candidates (declared by the coordinator at preflight, before task 1): R3-011, R3-028, R3-036, R3-046 (one shared cause, timeanddate.com), R3-047 (separate cause, Gutenberg maintenance). You do NOT score tasks that do not run; there is no evidence to score.
- Cap math (R3-011 ruling): a proven shared cause counts as 1 invalid for BOTH the total cap (5) and the group cap (2). So the 4 tasks R3-011/028/036/046 = 1 invalid, R3-047 = 1 invalid, total medium group = 2, which is AT the group cap. If a 3rd medium invalid occurs during the run, the group cap is exceeded and the coordinator STOPS the run; only the owner decides whether to continue, re-freeze, or cancel.
- R3-047 re-check: the coordinator re-checks gutenberg.org in a browser right before R3-047 runs (position 34, not 35). If still down, R3-047 is declared INVALID and backup DP-03 is used. If back, R3-047 runs normally.

## Class L timeout

- If a Class L task times out (30 minutes, runner stopped), you STILL do the live re-read from the live state as it exists at timeout, because the reset has not happened yet (for Class L, reset happens after scoring). Score from the live state as it exists; incomplete evidence usually means FAIL. The timeout freezes the evidence folder but does not change the Class L procedure.

## Run schedule

- Task 1 starts tomorrow (2026-11-25) when the owner says "start rung 3". The exact start time is the owner's decision. The run lasts 19-31 hours, continuous. There is no formal rest window in the plan. Scoring is continuous as tasks arrive. If you need a break, tell the coordinator in advance; the coordinator pauses the runner via backpressure so you do not fall behind.
