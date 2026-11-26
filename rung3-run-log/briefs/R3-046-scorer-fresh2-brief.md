# R3-046 scorer brief (Fresh session, Pair B scorer 2) - R3-L3

From: run coordinator epoch 23 (0d5fb18c). To: fresh Muse scorer session (spawned by the coordinator at scoring time; you have no memory of this run).
You are scorer 2 (Pair B) for R3-046. Score from the pushed snapshot only, independently of scorer 1 (also a fresh session). Never contact the runner or scorer 1 about this task. As scorer 2 you also confirm or deny the shared-cause claim (see below).

Standing rules (restated): ydotool is BANNED (you never drive). English for all work. NO personal info on GitHub. Git: explicit pathspec on add and commit, never git add -A, never leave files staged, verify pushes via ls-remote. Pill rule: you never control a browser in this task; if you ever do, the "Computer use active" pill must show first. Tab rules: never close or navigate owner-opened tabs, pinned tabs, or essentials. Timeout: file your verdict within 30 minutes of spawn.

Event-log duty: log key events (decisions, test results, fix milestones, revert actions, invalid rulings, gate results) via ~/workspace/agent-event-log/log-event.sh to the master log on the laptop at ~/agent-event-log/events.log, and keep state notes and per-task reports complete for the 15-minute harvest.

Ponytail (applies if you write any code; scoring needs none): smallest complete change, reuse what exists before writing, standard library and platform before new dependencies, no unrequested abstraction, one small test for non-trivial logic, never cut validation, security, error handling, or accessibility.

User-path note: scoring is not a user-facing test; you grade saved evidence. Real entry point: the pushed snapshot (path below) plus the frozen key section. Forbidden shortcuts for this task: reading the live site, reading scorer 1's verdict, reading the ledger row for this task before filing, contacting the runner.

## Scoring assignment R3-046 (Tier B)

Snapshot: rung3-run-log/rung3-snapshots/R3-046-L3/ on todolist-push (pull first; verify every file sha256 against manifest.json and record the manifest hash).
Key: docs/rung3-answer-keys.md section "## R3-046 (Tier B)" plus the R3-011 ruling at the top of the same file (verify key hashes: md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60; json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8; record both).

Grade PASS, FAIL, or INVALID by applying the key section's criteria to the snapshot evidence (6 timestamped result screenshots, ket-qua.txt with 6 rows + 3 day-length differences). Judge from the snapshot files, not from any report text. Sunrise/sunset/day-length values are live at run time on timeanddate.com; the screenshots are the ground truth. If the snapshot evidences a browser block on timeanddate.com, INVALID is the ruling per the list section 1 invalid definition; file your verdict either way.

Shared-cause confirmation (scorer 2 duty): R3-046 is in the timeanddate shared-cause group (R3-011/028/036/046). If you grade INVALID, state in your verdict JSON whether the block evidence proves the same timeanddate browser-block cause as R3-011 (shared_cause_confirmed true/false, with the evidence you relied on: screenshot, Ray ID if present, wait log). Curl evidence alone is never proof.

SCORER PROCESS ADDITION (mandatory from epoch 23): before filing an INVALID verdict, record in your grade file whether the infrastructure re-run path was considered (re-running the task when the service recovers, instead of INVALID), and why it was or was not applicable. An INVALID verdict without this record will be returned.

## Deliverables

Branch: fresh2/verdict-R3-046-L3. Directory: rung3-run-log/verdicts/R3-046-L3/.
- R3-046-L3-fresh2.json (verdict, your session id, keyfile_sha256 = the json hash above, manifest hash, files_read list, shared_cause_confirmed if INVALID).
- R3-046-L3-fresh2-grade.md (verdict + reasons tied to specific files, per-file hash verification result, infrastructure re-run consideration record if INVALID, independence declaration: "I graded independently from the snapshot and key section only; I did not read scorer 1's verdict or contact the runner.").
Push with explicit pathspec; verify via ls-remote. Report the branch name to the coordinator (no verdict value in the report subject line).
