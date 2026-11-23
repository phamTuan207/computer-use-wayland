# Scorer 1 brief: mochi (rung 3 safe-only 55-task run)

- Run: rung 3 safe-only, 55 tasks. Run code and frozen key file path plus sha256 are filled in by the coordinator before task 1. Do not score until the coordinator hands you the snapshot path and the key file hash.
- Your role: scorer 1. You score every task independently from the evidence snapshot plus the frozen key file. You never see scorer 2's verdict, and scorer 2 never sees yours, until both are recorded.
- Availability confirmed: yes, 2026-11-23 19:16 +07 (reply read 19:17 +07).
- Written no-prior-involvement declaration received: yes. Mochi confirmed in writing it did not author the list, did not write any answer key, did not run any rung 3 task, did not run the preflight trial, and did not write runner code.
- Session ID: 70cd99d1-ecef-4d02-9f42-714d7e86ab85 (assigned 2026-11-23 23:26 +07, Phase 1; distinct from runner sessions and list author sessions; the coordinator checks the ID before accepting any grade).

## Independence conditions (all must hold for every grade)

1. Separate sessions. Your session ID differs from the runner session ID and from the list author sessions. The coordinator checks the IDs before accepting any grade.
2. No authorship. You did not write or edit the task, the answer key, or the runner code for any task you score.
3. No running. You did not run any task you score, and you did not run the preflight trial.
4. Evidence only. You score only from the evidence snapshot plus the frozen key file.
5. Signed grades. Every grade is a signed record (see format below). An unsigned grade does not count.
6. Coordinator as committer. Scoring records are committed and pushed by the coordinator, not by you.
7. Written declaration. Your declaration is stored in `~/workspace/rung3-scorers.md` and in `thu-tu-chay.txt` before task 1.
8. No scorer-to-runner communication except through the coordinator, in writing, logged.

If any condition fails for a grade, that grade is void. The task is re-scored by a fresh scorer, the incident is recorded with session IDs and the forbidden source, and you are removed from the scorer pool for the rest of the run.

## Allowlist: what you may read for each task

- The evidence snapshot for that task, at the snapshot path the coordinator gives you (a copy of `~/rung3-chung-cu/R3-xxx/`, with a manifest and sha256 per file). Never touch the live evidence directory.
- The frozen key file (hash verified before scoring each task; record the hash in the signed grade).
- The task text from the list doc (section 6 only, never section 8 or any key material outside the frozen key file).
- The Tier C rubric for the task, if the frozen key file carries one.

## Denylist: what you must NOT read

- Runner logs, runner self-report, `reset-log.txt`, the run ledger, runner chat transcripts, any coord file, the trial log, the preflight report.
- The live evidence directory `~/rung3-chung-cu/` (score only from the snapshot).
- Any other scorer's verdict or reasoning before you record your own.

## Trial-contamination prohibition (hard rule)

You are forbidden from reading `~/workspace/rung3-preflight-trial.md` and `~/workspace/rung3-preflight-REPORT.md` before grading. Those reports pre-label tasks and would anchor your judgment. The trial ran 5 rung 3 tasks live and published their exact answers, so the scored sample excludes or replaces those tasks; do not go looking for them.

## How to grade

- Verify the key file sha256 matches the frozen hash before scoring each task. If it does not match, stop and tell the coordinator.
- Score from the snapshot only. The truth is the timestamped evidence captured at run time, never the live site or a fresh re-run, unless the pre-run package states for that task that the gradeable value is a live re-read, with its tolerance. No task may be left with both rules applying.
- Re-read every re-readable final state yourself (re-open the page or file, re-run the read command) and record your own screenshot or readout. Never grade from the runner's artifacts alone where re-reading is possible.
- For terminal tasks, accept only the saved command output files produced by scripted capture; re-run read-only commands where the value is stable.
- Check that every evidence file mtime falls inside the run window for that task.
- Score each task BEFORE its reset. Your verdict timestamp must be before the reset-log entry for that task.
- Apply the tier for the task as stated in the frozen key file (Tier A deterministic script plus human evidence check, Tier B human with anchor, Tier C rubric). Both scorers apply the same rubric.
- Never change the key mid-run. If you show the key is wrong or ambiguous, the task is marked invalid, not re-graded with a fixed key.

## Invalid calls

- To propose invalid, write down the invalid evidence and the reason. Scorer 2 confirms or rejects blind, seeing only that evidence and reason, not your decision.
- An invalid declaration needs evidence you collect independently, not only the runner screenshot: re-open the service yourself from a clean session and record the same block.
- Agent-caused triggers count as FAIL, not invalid. If the block follows rate-limitable runner behavior (rapid repeat requests, many tabs, hammering a service), it is a fail. Bot-check pages make a task invalid only when the block is not caused by the runner's behavior.
- Never attempt a blind screen-coordinate click on a Turnstile widget.

## Blind handoff rule

- You record your verdict first, through the coordinator only. You never see scorer 2's verdict before recording your own, and scorer 2 never sees yours. There is no shared scoring file. Your verdict is stored where scorer 2 has no read access.
- If you disagree with scorer 2, both verdicts and both reasons go in the ledger. The coordinator does not decide by fiat. Scorer 3 (tiebreaker) decides blind, seeing only the evidence snapshot and the key file.

## Signed-grade format (every grade, no exceptions)

```
scorer session ID: <your session ID>
task ID: <R3-xxx>
verdict: PASS | FAIL | INVALID (proposed)
files read: <snapshot paths, one per line>
key file hash: <sha256 of the frozen key file you verified>
timestamp: <Asia/Ho_Chi_Minh wall-clock time of the verdict>
reason: <one or two lines, citing the evidence file and the key line>
```

## What you never do

- Never score your own work. Never write a grade into the ledger (the coordinator commits scoring records). Never contact the runner directly. Never read anything on the denylist. Never read the trial report or the preflight report.
- The coordinator cannot overrule your verdict. Only the owner can overrule a verdict, and only on a process dispute.

## Log

- 2026-11-23 19:16:20 +07: scorer availability request sent to mochi via warm daemon, run 101, V12 verified.
- 2026-11-23 19:17 +07: mochi replied yes to scorer 1 and gave the written declaration (exact text in `~/workspace/rung3-scorers.md`).
