# R3-028 scorer brief (Mochi, Pair B scorer 1) - R3-L3 resume

From: run coordinator epoch 10. To: Mochi.
You are scorer 1 (Pair B) for R3-028. Score from the pushed snapshot only, independently of scorer 2 (Fresh). Never contact the runner or scorer 2 about this task.

Standing rules (restated): ydotool is BANNED (you never drive). English for all work. NO personal info on GitHub. Git: explicit pathspec on add and commit, never git add -A, never leave files staged, verify pushes via ls-remote. Pill rule: you never control a browser in this task; if you ever do, the "Computer use active" pill must show first. Tab rules: never close or navigate owner-opened tabs, pinned tabs, or essentials. Timeout: file your verdict within 30 minutes of the snapshot push notice.

Event-log duty: log key events (decisions, test results, fix milestones, revert actions, invalid rulings, gate results) via ~/workspace/agent-event-log/log-event.sh to the master log on the laptop at ~/agent-event-log/events.log, and keep state notes and per-task reports complete for the 15-minute harvest.

Ponytail (applies if you write any code; scoring needs none): smallest complete change, reuse what exists before writing, standard library and platform before new dependencies, no unrequested abstraction, one small test for non-trivial logic, never cut validation, security, error handling, or accessibility.

User-path note: scoring is not a user-facing test; you grade saved evidence. Real entry point: the pushed snapshot (path below) plus the frozen key section. Forbidden shortcuts for this task: reading the live site, reading scorer 2's verdict, reading the ledger row for this task before filing, contacting the runner.

## Scoring assignment R3-028 (Tier B)

Snapshot: rung3-run-log/rung3-snapshots/R3-028-L3/ on todolist-push (pull after the coordinator's push notice; verify every file sha256 against manifest.json and record the manifest hash).
Key: docs/rung3-answer-keys.md section "## R3-028 (Tier B)" (verify key hashes: md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60; json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8; record both).

Grade PASS, FAIL, or INVALID by applying the key section's criteria to the snapshot evidence. This task is a pre-declared INVALID candidate (shared timeanddate cause with R3-011): if the snapshot evidences a browser block on timeanddate.com, INVALID is the ruling per the list section 1 invalid definition; judge from the snapshot files (block screenshots, block-evidence.txt, probe-ready.json), not from any report text. File your verdict even if you rule INVALID; the shared-cause counting (0 new cap events) needs scorer-2 confirmation, so your independent judgment matters.

## Deliverables

Branch: mochi/verdict-R3-028-L3. Directory: rung3-run-log/verdicts/R3-028-L3/.
- R3-028-L3-mochi.json (verdict, session id, keyfile_sha256 = the json hash above, manifest hash, files_read list).
- R3-028-L3-mochi-grade.md (verdict + reasons tied to specific files, per-file hash verification result, independence declaration: "I graded independently from the snapshot and key section only; I did not read scorer 2's verdict or contact the runner.").
Push with explicit pathspec; verify via ls-remote. Notify the coordinator with the branch name only (no verdict value in chat).
