# DP-03 scorer brief (Fresh session, Pair B scorer 2) - R3-L3

From: run coordinator epoch 23 (0d5fb18c). To: fresh Muse scorer session (spawned by the coordinator at scoring time; you have no memory of this run).
You are scorer 2 (Pair B) for DP-03. Score from the pushed snapshot only, independently of scorer 1 (Clone2). Never contact the runner or scorer 1 about this task.

Standing rules (restated): ydotool is BANNED (you never drive). English for all work. NO personal info on GitHub. Git: explicit pathspec on add and commit, never git add -A, never leave files staged, verify pushes via ls-remote. Pill rule: you never control a browser in this task; if you ever do, the "Computer use active" pill must show first. Tab rules: never close or navigate owner-opened tabs, pinned tabs, or essentials. Timeout: file your verdict within 30 minutes of spawn.

Event-log duty: log key events via ~/workspace/agent-event-log/log-event.sh to the master log on the laptop at ~/agent-event-log/events.log.

Ponytail (applies if you write any code; scoring needs none): smallest complete change, reuse what exists before writing, standard library and platform before new dependencies, no unrequested abstraction, one small test for non-trivial logic, never cut validation, security, error handling, or accessibility.

User-path note: scoring is not a user-facing test; you grade saved evidence. Real entry point: the pushed snapshot (path below) plus the frozen key section. Forbidden shortcuts: running ss yourself to compare against live ports (ports change; the saved ss-output.txt is ground truth), reading scorer 1's verdict, reading the ledger row for this task before filing, contacting the runner.

## Scoring assignment DP-03 (Tier B)

Snapshot: rung3-run-log/rung3-snapshots/DP-03-L3/ on todolist-push (pull first; verify every file sha256 against manifest.json and record the manifest hash).
Key: docs/rung3-answer-keys.md section "## DP-03 (Tier B, du phong trung binh)" plus the DP-03 ruling at the top of the same file (verify key hashes: md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60; json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8; record both).

Grade PASS, FAIL, or INVALID by applying the key section's criteria to the snapshot evidence (ss-output.txt, bao-cao.txt, terminal screenshot). The report must list the first 5 ports with process names in ascending order (N minimum 3; fewer than 5 with names is acceptable only if the actual count is recorded), each with port, protocol, process name matching the saved ss-output.txt. Judge from the snapshot files, not from any report text.

SCORER PROCESS ADDITION (mandatory from epoch 23): before filing an INVALID verdict, record in your grade file whether the infrastructure re-run path was considered, and why it was or was not applicable. An INVALID verdict without this record will be returned.

## Deliverables

Branch: fresh/verdict-DP-03-L3. Directory: rung3-run-log/verdicts/DP-03-L3/.
- DP-03-L3-fresh.json (verdict, your session id, keyfile_sha256 = the json hash above, manifest hash, files_read list).
- DP-03-L3-fresh-grade.md (verdict + reasons tied to specific files, per-file hash verification result, infrastructure re-run consideration record if INVALID, independence declaration: "I graded independently from the snapshot and key section only; I did not read scorer 1's verdict or contact the runner.").
Push with explicit pathspec; verify via ls-remote. Report the branch name to the coordinator (no verdict value in the report subject line). Also copy your verdict JSON to ~/workspace/rung3-verdicts/DP-03-B2.json on the VM (coordinator audit path).
