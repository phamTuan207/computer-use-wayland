# Batch 12 task 3: CB-8 audit of 2 DONE claims

- Date: 2026-11-22, 13:20 +07.
- Auditor: clone1, independent of the workers who ran the measurements.
- Rule (CB-8): DONE must have concrete evidence (test command, output, commit hash, time log). If the evidence is not complete, the claim is REVOKED, not qualified.
- Sources read first-hand, read-only, from branch todolist-push at HEAD 4305dcb. Nothing on todolist-push was modified.
- The batch 12 task 1 verification report (docs/batch12-task1-s2-reopen-verify-20261122.md) was NOT on main when this audit ran (checked twice), so no numbers below are reused from it. Every number below was recomputed from the raw JSONs by this auditor.
- No em dash or en dash anywhere in this file. No personal info.

## Evidence base

| Source | Commit or location | What was checked |
|---|---|---|
| improvements/s2-flip-reopen-runs/run-1..5.json | todolist-push, in commit 1a3356d | All 5 runs, both browsers, every field below |
| improvements/worker-click5-s2-reopen-log.md | commit 1a3356d, 346 lines, hash recorded in 212e0ad | Run table, section 5 P9 review, section 6 verdict, section 8 commit record |
| improvements/s2-flip-b1-runs/run-1..5.json | todolist-push, in commit 4bd6292 range | All 5 scored (b1) runs, Chromium only |
| improvements/s2-flip-b1-runs/run-2..5-aborted.json | todolist-push, in commit 4bd6292 | All 4 aborted first attempts |
| improvements/worker-click5-input-fix-log.md | commit 4bd6292, 523 lines, hash recorded in 030c227 | (b1) section, abort disclosure, section 7.5 P9 review, section 9 commit record |
| scripts/s2_flip_live.py | todolist-push HEAD 4305dcb | build_program_set_value and focus_enter docstrings, LAPTOP_FOCUSENTER path |
| git rev-list --all --objects, grep p9 | whole repo history | Whether any P9 PNG object exists anywhere |

## Claim (a): S2 flip reopen PASS (5/5 runs, 10/10 messages, median 28.6s)

### Numbers verified first-hand from run-1..5.json

Walls in ms: run 1 29020.4, run 2 27799.1, run 3 28112.6, run 4 28898.1, run 5 28560.9. Sorted: 27799.1, 28112.6, 28560.9, 28898.1, 29020.4. Median 28560.9 ms, which is 28.6 s. The claimed median is correct.

Per send, all 10 sends:

| Run | Brave (fill) | Chromium (set_value) |
|---|---|---|
| 1 | sent, program ok True, completed 3, dom_act 51 ms, elapsed 140.5 ms, CB-1 all True, V12 found True attempt 1 items 43, message S2-REOPEN-R1-BRAVE-IGNORE-TEST | sent, program ok True, completed 2, dom_act 12 ms, elapsed 113.0 ms, focus_enter ok True enter 25 ms, CB-1 all True, V12 found True attempt 1 items 54, message S2-REOPEN-R1-CHROMIUM-IGNORE-TEST |
| 2 | sent, completed 3, dom_act 46 ms, elapsed 137.5 ms, CB-1 all True, V12 attempt 1 items 45 | sent, completed 2, dom_act 9 ms, elapsed 106.6 ms, focus_enter ok True enter 21 ms, CB-1 all True, V12 attempt 1 items 56 |
| 3 | sent, completed 3, dom_act 46 ms, elapsed 144.9 ms, CB-1 all True, V12 attempt 1 items 47 | sent, completed 2, dom_act 9 ms, elapsed 107.1 ms, focus_enter ok True enter 23 ms, CB-1 all True, V12 attempt 1 items 58 |
| 4 | sent, completed 3, dom_act 43 ms, elapsed 140.8 ms, CB-1 all True, V12 attempt 1 items 49 | sent, completed 2, dom_act 8 ms, elapsed 99.4 ms, focus_enter ok True enter 25 ms, CB-1 all True, V12 attempt 1 items 60 |
| 5 | sent, completed 3, dom_act 43 ms, elapsed 141.2 ms, CB-1 all True, V12 attempt 1 items 51 | sent, completed 2, dom_act 10 ms, elapsed 104.2 ms, focus_enter ok True enter 23 ms, CB-1 all True, V12 attempt 1 items 62 |

- Outcome "sent" in 10 of 10 browser halves. CB-1 input_sent, target_received, verified all True in 10 of 10. V12 found True at attempt 1 in 10 of 10.
- Model calls 0 in all 5 runs. dry_run False in all 5 runs.
- chromium_set_value True in all 5 runs, program_variant "brave=fill,chromium=set_value" in all 5 runs.
- The log run table matches the JSONs exactly on every checked field (wall, program elapsed, dom_act ms, V12 items, observe elements).
- Observe elements: Brave 72, 73, 75, 77, 79, not truncated, strict routing every run. Chromium 80, truncated, routing_relaxed True every run, composer present in the snapshot every run.
- Chromium pre-send count 0 and delayed count exactly 1 in every run (pre items 51, 54, 56, 58, 60; delayed items 54, 56, 58, 60, 62). No double-send in any run.
- The numbers in the claim are correct. The numbers are not the problem.

### Verdict: REVOKED

### What is missing

The 10 P9 screenshots do not exist anywhere in the repo. The JSONs reference them:

- improvements/s2-flip-reopen-runs/p9-run1-brave.png
- improvements/s2-flip-reopen-runs/p9-run1-chromium.png
- improvements/s2-flip-reopen-runs/p9-run2-brave.png
- improvements/s2-flip-reopen-runs/p9-run2-chromium.png
- improvements/s2-flip-reopen-runs/p9-run3-brave.png
- improvements/s2-flip-reopen-runs/p9-run3-chromium.png
- improvements/s2-flip-reopen-runs/p9-run4-brave.png
- improvements/s2-flip-reopen-runs/p9-run4-chromium.png
- improvements/s2-flip-reopen-runs/p9-run5-brave.png
- improvements/s2-flip-reopen-runs/p9-run5-chromium.png

Checks run:

- git ls-tree at commit 1a3356d for improvements/s2-flip-reopen-runs lists only run-1..5.json. No PNG.
- git ls-tree at todolist-push HEAD 4305dcb lists only run-1..5.json. No PNG.
- git rev-list --all --objects, grep p9, returns nothing. No P9 PNG object exists in any commit in the whole repo history.

The reopen log section 8 says the PNGs were "to be committed with this log". They were not committed. The log section 5 claims "P9 PASS 10/10" from reading the PNGs, with one prose description per run. Prose is the claim itself, not evidence for it. The JSON field p9.<browser>.ok True only proves the capture call returned ok. It does not prove any reviewer read the image.

This matters because P9 is a scoring condition, not a nicety. The log section 0 states it plainly: one final screenshot per run, reviewed before scoring, and any DOM-vs-render mismatch FAILS the run (the B1 condition). V12 and CB-1 both read the DOM. Neither checks rendering. So the render half of "DOM and render agree" is unverified for all 10 sends. A PASS verdict whose render check cannot be checked by any reviewer does not meet CB-8.

### What is verified, what is not

- Verified: 5/5 runs, 10/10 messages, median 28.6 s, 0 model calls, per-run program and V12 and CB-1 numbers, pre-send count 0 and delayed count 1 on Chromium, no double-send.
- Not verified: that any P9 screenshot was reviewed, that DOM and render agree in any run, and therefore the PASS verdict itself.

### Gating consequence

Claim (a) gates EXPAND. Commit 4305dcb records "EXPAND approved in principle" on the strength of this PASS. That approval rests on a PASS whose render evidence is missing. EXPAND should wait until the 10 PNGs are committed and this claim is re-audited.

### Qualification, not missing evidence

The Chromium half ran under the DISCLOSED relaxed routing gate in all 5 runs (truncated 80-element inventory, composer covered). This is disclosed in the log caveat 1 and recorded per run in the JSONs (routing_relaxed True). It is a qualification on the PASS, not hidden evidence. The activate field is False in all 5 runs, which matches the log focus rule (no workspace switch, no activation anywhere in the task). That is consistent, not a gap. The dry run 0 JSON lives in /tmp and is not committed, but the dry run is not part of the claim.

## Claim (b): (b1) 5/5 on Chromium (set_value + focus + CDP Enter)

### Numbers verified first-hand from s2-flip-b1-runs/run-1..5.json

Walls in ms: run 1 18477.4, run 2 20592.9, run 3 18839.7, run 4 18738.7, run 5 19094.0. Sorted: 18477.4, 18738.7, 18839.7, 19094.0, 20592.9. Median 18839.7 ms, which is 18.8 s. The log figure of 18.8 s is correct.

Per run, Chromium only, all 5 scored runs:

| Run | Program | Focus and Enter | CB-1 | V12 | Pre and delayed |
|---|---|---|---|---|---|
| 1 | ok True, completed 2, dom_act 8 ms, elapsed 97.7 ms | focus_enter ok True, focused TEXTAREA, enter ok True 23 ms | all True | found True attempt 1 items 44 | pre 0, delayed 1 |
| 2 | ok True, completed 2, dom_act 9 ms, elapsed 106.6 ms | focus_enter ok True, enter ok True 23 ms | all True | found True attempt 1 items 46 | pre 0, delayed 1 |
| 3 | ok True, completed 2, dom_act 8 ms, elapsed 91.6 ms | focus_enter ok True, enter ok True 17 ms | all True | found True attempt 1 items 48 | pre 0, delayed 1 |
| 4 | ok True, completed 2, dom_act 7 ms, elapsed 102.8 ms | focus_enter ok True, enter ok True 18 ms | all True | found True attempt 1 items 50 | pre 0, delayed 1 |
| 5 | ok True, completed 2, dom_act 8 ms, elapsed 104.6 ms | focus_enter ok True, enter ok True 20 ms | all True | found True attempt 1 items 52 | pre 0, delayed 1 |

- Program elapsed range 91.575 to 106.622 ms, recomputed from the raw JSONs. The reopen log section 0 line 32 restates the same range as 91.6 to 106.6 ms; the input-fix log does not state this range.
- Model calls 0 in all 5 runs. dry_run False in all 5 runs. program_variant "set_value" in all 5 runs.
- Outcome "sent" in 5 of 5. Messages C5-B1-R1 to R5-CHROMIUM-IGNORE-TEST, each exactly once.
- The (b1) shape is independently re-proven by the reopen Chromium halves: 5 of 5 sent with set_value, focus_enter ok True (enter 21 to 25 ms), CB-1 all True, V12 attempt 1, pre 0, delayed 1. Same mechanism, same outcome measures, a second measurement.

### Aborts: disclosed, not hidden

Runs 2 to 5 each had a first attempt that aborted with outcome aborted-routing, error "router fell through to screenshot: fail-closed fallback: no backend returned complete coverage". The aborted JSONs are preserved as run-2..5-aborted.json. The input-fix log discloses this in the time log, in the (b1) section, and in the commit record, and states that nothing was sent in the aborted attempts. The 5/5 figure counts the 5 scored runs, and the aborts are on the record. This is not a gap.

### Mechanism: confirmed from repo code

- scripts/s2_flip_live.py, build_program_set_value docstring: the input-free send program, set_value with zero Input calls. The Enter is not in this program; it runs after, with the /tmp/c5-focusenter.mjs helper.
- scripts/s2_flip_live.py, focus_enter docstring: runs /tmp/c5-focusenter.mjs, Runtime.evaluate focus plus Input.dispatchKeyEvent Enter, zero mouse events.
- Input-fix log, section 7.1: Input.dispatchKeyEvent answers in 2 ms on the stuck tab, while Input.dispatchMouseEvent stalls. The helper description matches: Runtime.evaluate focus on the textarea, then Input.dispatchKeyEvent keyDown plus keyUp Enter.
- The "CDP Enter" in the claim is therefore Input.dispatchKeyEvent, not a keystroke and not a mouse event. The mechanism as described is confirmed.

### Verdict: REVOKED

### What is missing

The 5 (b1) P9 screenshots do not exist anywhere in the repo. The JSONs reference them:

- improvements/s2-flip-b1-runs/p9-run1-chromium.png
- improvements/s2-flip-b1-runs/p9-run2-chromium.png
- improvements/s2-flip-b1-runs/p9-run3-chromium.png
- improvements/s2-flip-b1-runs/p9-run4-chromium.png
- improvements/s2-flip-b1-runs/p9-run5-chromium.png

Checks run:

- git ls-tree at todolist-push HEAD 4305dcb for improvements/s2-flip-b1-runs lists only run-1..5.json and run-2..5-aborted.json. No PNG.
- git rev-list --all --objects, grep p9, returns nothing. No P9 PNG object exists in any commit in the whole repo history.
- The input-fix log section 9 says the PNGs were "to be committed with this log". They were not committed. Its section 7.5 claims "P9 PASS all 5 runs" from reading them. As with claim (a), prose is the claim, not evidence for it, and the JSON p9.<browser>.ok True only proves the capture call returned ok.

The same scoring-condition argument applies: P9 is the render check, and the render half of the (b1) result is unverified.

Secondary gap, named but not the reason for the verdict: the focus-enter helper /tmp/c5-focusenter.mjs is laptop-only and is not in the repo, so its exact code cannot be reviewed from the branch. Its behavior is recorded per run in the JSONs and its contract is documented in the harness docstring, so the outcome evidence is complete. The code itself is not reviewable, and that stays an open item for the landing work.

### What is verified, what is not

- Verified: 5/5 Chromium sends with set_value plus focus plus CDP Enter, median wall 18.8 s, program elapsed 91.6 to 106.6 ms, V12 attempt 1 all 5, CB-1 all True all 5, pre 0 and delayed 1 all 5, 0 model calls, aborts disclosed, mechanism confirmed from repo code, shape re-proven by the reopen Chromium halves.
- Not verified: that any (b1) P9 screenshot was reviewed, and therefore the P9 PASS half of the (b1) result.

### Gating consequence

Claim (b) gates the (b1) landing spec (batch 12 task 2) and the durable landing in cdp.mjs. The landing should wait for the 5 PNGs to be committed and this claim to be re-audited, or it should land with the missing P9 evidence recorded as an open item against it. Landing a shape whose render check was never verifiably run repeats the exact gap this audit exists to catch.

## Verdict summary

| Claim | Numbers | Evidence complete | Verdict |
|---|---|---|---|
| (a) S2 flip reopen PASS, 5/5 runs, 10/10 messages, median 28.6 s | Verified correct from raw JSONs | No, 10 P9 PNGs missing | REVOKED |
| (b) (b1) 5/5 on Chromium, set_value plus focus plus CDP Enter | Verified correct from raw JSONs | No, 5 P9 PNGs missing | REVOKED |

Both revocations are narrow. The measured numbers are correct in both claims. What is missing in both is the same single artifact class: the P9 screenshots that the scoring procedure requires. Nothing in this audit invents or assumes those screenshots.

## Repair list

1. Commit the 10 reopen P9 PNGs to todolist-push at exactly the paths the run JSONs reference (improvements/s2-flip-reopen-runs/p9-runN-brave.png and p9-runN-chromium.png, N 1 to 5).
2. Commit the 5 (b1) P9 PNGs to todolist-push at exactly the paths the (b1) run JSONs reference (improvements/s2-flip-b1-runs/p9-runN-chromium.png, N 1 to 5).
3. If the laptop PNG files are gone, re-capture equivalent P9 shots on the live threads and commit them with a note saying they are re-captures, not the originals. Do not rewrite the logs to pretend the originals were committed.
4. For the landing work, commit the focus-enter helper code, or record its exact hash, so the Enter mechanism is reviewable from the branch.
5. Re-audit both claims after the files land. The re-audit only needs to open the 15 PNGs and confirm each claimed bubble is visible with an empty composer. The numeric checks in this report do not need redoing.

## Method note

- This audit read the raw JSONs and the two logs directly. It did not run the harness or the live browsers, and it did not re-run the wiring tests (the log claim of 12/12 wiring tests passing was not re-verified). The verdicts rest on the committed artifacts only, which is what CB-8 asks for.
- The batch 12 task 1 verification report was not on main when this audit ran, so nothing was reused from it. If task 1 lands later with different numbers, the two reports should be reconciled before the claims are re-audited.
