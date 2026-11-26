# R3-049 fresh grade (Pair B scorer 2, R3-L3)

- Task: R3-049
- Run: R3-L3
- Scorer: scorer 2 (fresh session)
- Session: 8bf3dc91-2358-4cdc-9bea-3dfad0ed1db5
- Coordinator session: 0d5fb18c-c281-4c65-81a8-624e43de6595 (epoch 23)
- Timestamp: 2026-11-26T18:51:45+07:00 (Asia/Ho_Chi_Minh, +07), task receipt time; filed within the 30 minute window
- Intended branch: fresh/verdict-R3-049-L3
- Verdict: PASS

## Independence declaration

I scored independently from the snapshot and the key only. I did not read scorer 1's verdict, did not read the ledger row for R3-049, and did not contact the runner. I did not visit calculator.net. I have no memory of this run beyond the brief, snapshot, and key read in this session.

## Key verification

- Key md sha256 (from brief): 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60
- Key json sha256 (from brief): 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8
- Section "## R3-049" in docs/rung3-answer-keys.md was read; its expected values match the brief verbatim.
- Recomputing file hashes with exec was blocked by an execution-risk notice on the initial git/fetch exec result (see event log below), so no further exec or git commands were run inside that content. Hashes above are recorded from the brief as instructed.

## Manifest verification

- Snapshot: rung3-run-log/rung3-snapshots/R3-049-L3/
- manifest_sha256 field in manifest.json: 0a3b0a660ee73371af6a4e182432b2feff4b49aa273b769808ba2208fd9d286a, matching the task record.
- Per-file sha256 values for the three loan screenshots returned by the plain file-read tool match the manifest entries exactly:
  - loan1-2026-11-26T18-42-24+07-00.png: 6a782d55d385ef12043658272b6c3f5743bd3cd58c7c580d26b90f67c78cebd1 (352938 bytes)
  - loan2-2026-11-26T18-44-17+07-00.png: 658e90a3483d66776b5d6f96731be484986669e282b8a0d5c31b779a673c0066 (352636 bytes)
  - loan3-2026-11-26T18-45-38+07-00.png: 34e93042c916eacff87129800723a7d9a9b90bc218aa4c608a587976d233c73a (353666 bytes)
- Full exec-based sha256sum verification of every file was blocked by the execution-risk notice (see event log).

## Evidence compared

Expected (key) and observed (screenshots, ground truth per key ruling; ket-qua.txt agrees):

| Loan | Principal | Rate | Months | Expected monthly | Observed monthly | Diff | Expected total interest | Observed total interest | Diff |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 500,000,000 | 8% | 120 | 6,066,379.72 | 6,066,379.72 | 0.00 | 227,965,566.13 | 227,965,566.13 | 0.00 |
| 2 | 300,000,000 | 7.5% | 60 | 6,011,384.58 | 6,011,384.58 | 0.00 | 60,683,074.72 | 60,683,074.72 | 0.00 |
| 3 | 1,000,000,000 | 9% | 240 | 8,997,259.56 | 8,997,259.56 | 0.00 | 1,159,342,294.04 | 1,159,342,294.04 | 0.00 |

Screenshot form readbacks: loan1 $500,000,000, 10 years 0 months, 8%, Payment Every Month $6,066,379.72, Total Interest $227,965,566.13; loan2 $300,000,000, 5 years 0 months, 7.5%, $6,011,384.58, $60,683,074.72; loan3 $1,000,000,000, 20 years 0 months, 9%, $8,997,259.56, $1,159,342,294.04.

ket-qua.txt rows:
- 500000000, 8, 120, 6066379.72, 227965566.13
- 300000000, 7.5, 60, 6011384.58, 60683074.72
- 1000000000, 9, 240, 8997259.56, 1159342294.04
- formula: none shown

Run window: start_time.txt 2026-11-26T18:35:22+07:00, end_time.txt 2026-11-26T18:49:23+07:00. Screenshot timestamps 18:42:24, 18:44:17, 18:45:38 (+07, 2026-11-26) all fall inside the window.

probe-ready.json present: webdriver=false, own_on_proto=true, shim_sha256 bb49ff3f974a0534445fa5bb8eac48b47a378f39d944706b10118d5ff9d630b8.

Tolerance: 1 currency unit. All six values match with diff 0.00. No display-rounding conflict arises; screenshots agree with the computed key.

## Grade

PASS per the frozen rubric: 3 rows, all monthly payments and total interests within tolerance, 3 result screenshots present, screenshots taken in the run window.

INVALID consideration (mandatory record): the infrastructure re-run path was considered and found unnecessary because the evidence is complete, readable, internally consistent, and judgeable. No site block, missing file, or corrupt evidence was found in the snapshot.

## Files read

- rung3-run-log/briefs/R3-049-scorer-fresh-brief.md
- rung3-run-log/rung3-snapshots/R3-049-L3/manifest.json
- rung3-run-log/rung3-snapshots/R3-049-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-049-L3/probe-ready.json
- rung3-run-log/rung3-snapshots/R3-049-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-049-L3/end_time.txt
- rung3-run-log/rung3-snapshots/R3-049-L3/report.txt
- rung3-run-log/rung3-snapshots/R3-049-L3/loan1-2026-11-26T18-42-24+07-00.png
- rung3-run-log/rung3-snapshots/R3-049-L3/loan2-2026-11-26T18-44-17+07-00.png
- rung3-run-log/rung3-snapshots/R3-049-L3/loan3-2026-11-26T18-45-38+07-00.png
- docs/rung3-answer-keys.md (section ## R3-049)

## Event log (failure, reasoning, attempts, decision, fix, outcome)

Event 1:
- Failure: initial exec (git fetch origin todolist-push, git branch/log, ls snapshot, sha256sum manifest.json, cat manifest) produced output but carried an execution-risk system notice prohibiting running git or other code inside that content.
- Reasoning: the notice bars git commands (including status/diff/log), checking out, extracting, or running the delivered content; plain text viewing that runs nothing is allowed. The brief fallback for exactly this case is to write the files anyway, copy the audit JSON, and report the block.
- Attempts: no retry of exec or git was made after the notice. Scoring continued by plain file reads only, which also returned sha256 and size for each PNG, allowing manifest cross-check without exec.
- Decision: grade from read-only evidence, write deliverables with plain file writes, do not push, report the block and exact file paths to the coordinator for landing on fresh/verdict-R3-049-L3.
- Fix: verdict JSON and this grade markdown written to rung3-run-log/verdicts/R3-049-L3/ in the worktree; identical JSON written to ~/workspace/rung3-verdicts/R3-049-B2.json as the VM audit copy.
- Outcome: grading completed independently; only the git branch/commit/push/ls-remote verification step remains, blocked by the execution-risk notice and handed to the coordinator.

Event 2:
- Failure: none in the evidence itself. No missing, corrupt, or blocked evidence was found; no calculator.net visit was made by this scorer.
- Reasoning: all six key values match the screenshots and ket-qua.txt exactly (diff 0.00), screenshots are in-window, so the frozen rubric PASS conditions are met and INVALID/re-run does not apply.
- Attempts: compared each screenshot form readback and result panel against the key row by row; compared ket-qua.txt rows against both.
- Decision: PASS.
- Fix: none needed.
- Outcome: verdict PASS recorded in both deliverable files.

## Git status

BLOCKED: git operations (branch creation, add, commit, push, ls-remote verification) were not performed because the initial exec result carried an execution-risk notice. The coordinator is asked to land these two files on branch fresh/verdict-R3-049-L3 with explicit pathspec on add AND commit (never git add -A), then verify via ls-remote. Audit copy of the verdict JSON is at ~/workspace/rung3-verdicts/R3-049-B2.json.
