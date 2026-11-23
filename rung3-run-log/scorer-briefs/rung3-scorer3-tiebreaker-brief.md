# Tiebreaker brief template: scorer 3 (rung 3 safe-only 55-task run)

- Run: rung 3 safe-only, 55 tasks. Run code and frozen key file path plus sha256 are filled in by the coordinator before task 1.
- Your role: tiebreaker scorer 3, a fresh session from the same pool as scorer 2. You are called ONLY on a disagreement between scorer 1 and scorer 2, or on a disputed invalid call. You must not be mei, must not be the runner, must not be mochi, and must not be scorer 2. The coordinator records your name and session ID in `thu-tu-chay.txt` and in `~/workspace/rung3-scorers.md` when you are called. You may be named at the same time as scorer 2, or spawned on demand by the coordinator.
- You decide blind: you see only the evidence snapshot and the frozen key file, never either scorer's verdict or reasoning.

## Independence conditions (all must hold for every grade)

1. Separate sessions. Your session ID differs from the runner session ID, from scorer 1 (mochi), from scorer 2, and from the list author sessions. The coordinator checks the IDs before accepting any grade.
2. No authorship. You did not write or edit the task, the answer key, or the runner code for any task you score.
3. No running. You did not run any task you score, and you did not run the preflight trial.
4. Evidence only. You score only from the evidence snapshot plus the frozen key file.
5. Signed grades. Every grade is a signed record (see format below). An unsigned grade does not count.
6. Coordinator as committer. Scoring records are committed and pushed by the coordinator, not by you.
7. Written declaration. Before grading, sign the no-prior-involvement declaration in writing (no list authorship, no key authorship, no trial run, no runner code) and give it to the coordinator for `thu-tu-chay.txt`.
8. No scorer-to-runner communication except through the coordinator, in writing, logged.

If any condition fails for a grade, that grade is void. The task is re-scored by a fresh scorer, the incident is recorded with session IDs and the forbidden source, and you are removed from the scorer pool for the rest of the run.

## Allowlist: what you may read for each task

- The evidence snapshot for that task, at the snapshot path the coordinator gives you (a copy of `~/rung3-chung-cu/R3-xxx/`, with a manifest and sha256 per file). Never touch the live evidence directory.
- The frozen key file (hash verified before scoring each task; record the hash in the signed grade).
- The task text from the list doc (section 6 only, never section 8 or any key material outside the frozen key file).
- The Tier C rubric for the task, if the frozen key file carries one.
- For a disputed invalid call: only the invalid evidence and the reason, the same packet scorer 2 saw.

## Denylist: what you must NOT read

- Runner logs, runner self-report, `reset-log.txt`, the run ledger, runner chat transcripts, any coord file, the trial log, the preflight report.
- The live evidence directory `~/rung3-chung-cu/` (score only from the snapshot).
- Scorer 1's or scorer 2's verdict or reasoning, in any form, before you record your own verdict.

## Trial-contamination prohibition (hard rule)

You are forbidden from reading `~/workspace/rung3-preflight-trial.md` and `~/workspace/rung3-preflight-REPORT.md` before grading. Those reports pre-label tasks and would anchor your judgment. FREEZE-2 decision: KEEP R3-076, R3-007, R3-011; REPLACE content for R3-082, R3-013. The old trial answers are wrong for the new R3-082 and R3-013 content; score those tasks only against the frozen key. Do not go looking for the trial answers.

## How to decide

- Verify the key file sha256 matches the frozen hash before scoring each task. If it does not match, stop and tell the coordinator.
- Score from the snapshot only. The truth is the timestamped evidence captured at run time, never the live site or a fresh re-run, unless the pre-run package states for that task that the gradeable value is a live re-read, with its tolerance.
- Re-read every re-readable final state yourself (re-open the page or file, re-run the read command) and record your own screenshot or readout. Never grade from the runner's artifacts alone where re-reading is possible.
- Check that every evidence file mtime falls inside the run window for that task.
- Score each task BEFORE its reset. Your verdict timestamp must be before the reset-log entry for that task.
- Apply the tier for the task as stated in the frozen key file. Both scorers apply the same rubric.
- Never change the key mid-run. If you show the key is wrong or ambiguous, the task is marked invalid, not re-graded with a fixed key.
- If you agree with one side, that verdict stands. All three verdicts stay in the ledger. On a disputed invalid call, you decide blind on the same packet scorer 2 saw. For an invalid declaration, collect independent evidence yourself: re-open the service from a clean session and record the same block.
- Agent-caused triggers count as FAIL, not invalid. Never attempt a blind screen-coordinate click on a Turnstile widget.

## Blind handoff rule

- You receive your evidence through a separate brief and a separate snapshot packet. Both earlier verdicts are stored where you have no read access. You record your verdict before you can see either one. There is no shared scoring file.

## Signed-grade format (every grade, no exceptions)

```
scorer session ID: <your session ID>
task ID: <R3-xxx>
verdict: PASS | FAIL | INVALID (confirm / reject, for invalid calls)
files read: <snapshot paths, one per line>
key file hash: <sha256 of the frozen key file you verified>
timestamp: <Asia/Ho_Chi_Minh wall-clock time of the verdict>
reason: <one or two lines, citing the evidence file and the key line>
```

## What you never do

- Never score your own work. Never write a grade into the ledger (the coordinator commits scoring records). Never contact the runner directly. Never read anything on the denylist. Never read the trial report or the preflight report. Never ask either scorer for its verdict.
- The coordinator cannot overrule your verdict. Only the owner can overrule a verdict, and only on a process dispute.

## Coordinator fill-in (when called)

- Scorer 3 name: ____________________
- Scorer 3 session ID: ____________________
- Called for task(s): ____________________
- Written declaration received: yes / no, time: __________
- Frozen key file path: ____________________
- Frozen key file sha256: ____________________
