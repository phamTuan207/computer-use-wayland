# Sealed calibration assignment - Clone1 (R3-L3, check 7 clone1 rule)

From: run coordinator epoch 10. To: Clone1. Date: 2026-11-26.
Purpose: you are scorer 2 for R3-037 (Pair A). Before you score any real task, you must calibrate 4 of 4 blind on a sealed held-out set (fix A F6). A verifier (TB-A lineage) sealed the set and will re-grade your cases from scratch and sign off. R3-037 scoring with you waits for the sign-off.

Standing rules (restated): ydotool is BANNED. English for all work. NO personal info on GitHub. Git: explicit pathspec on add and commit, never git add -A, never leave files staged, verify pushes via ls-remote. Never assume a capability; ask the coordinator directly if anything is unclear. Pill rule: you never drive in this task; if you ever control a browser, the "Computer use active" pill must show first. Tab rules: never close or navigate owner-opened tabs, pinned tabs, or essentials. Timeout: file all 4 grades within 60 minutes of this assignment.

Event-log duty: log key events (decisions, test results, fix milestones, revert actions, invalid rulings, gate results) via ~/workspace/agent-event-log/log-event.sh to the master log on the laptop at ~/agent-event-log/events.log, and keep state notes and per-task reports complete for the 15-minute harvest.

Ponytail (applies if you write any code; grading needs none): smallest complete change, reuse what exists before writing, standard library and platform before new dependencies, no unrequested abstraction, one small test for non-trivial logic, never cut validation, security, error handling, or accessibility. Confirm whether the ponytail skill is available to you before starting; if not, this brief text is your ruleset. State your answer in your first grade file.

User-path note: grading is not a user-facing test; you grade saved evidence. Real entry point: the sealed snapshots on branch todolist-push (paths below) plus the frozen key sections. Forbidden shortcuts for this task: reading the ledger (R3-L3-grades.jsonl, R3-L3-reruns.jsonl), reading any existing grade file or verdict json for these 4 tasks, reading the live sites, reading other scorers' verdicts, contacting the runner or the other candidate.

## The 4 cases (grade all 4, blind)

Pull branch todolist-push first. For each case, your allowlist is ONLY: the snapshot dir + the key section named. Verify every snapshot file sha256 against its manifest.json before grading; record the manifest hash. Verify key hashes: docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60; docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8. Record both in every grade file.

1. R3-002: snapshot rung3-run-log/rung3-snapshots/R3-002-L3/ (manifest_sha256 field 0741a1aa90bc20b1257888fc6be33377aae02b351693a581c850b1b4d6852f15). Key: docs/rung3-answer-keys.md section "## R3-002 (Tier A)" lines 119-129.
2. R3-013: snapshot rung3-run-log/rung3-snapshots/R3-013-L3/ (manifest_sha256 field 7d4a5c763010c87fb5b90378edfe022eb0dad88601105019207ad7bb5e8e161d). Key: section "## R3-013 (Tier A)" lines 225-236.
3. R3-016: snapshot rung3-run-log/rung3-snapshots/R3-016-L3/ (manifest_sha256 field dd4992764d5923e5baf24b408471bcfd41e13cbc987a663b5350c6d82a0bdf2d). Key: section "## R3-016 (Tier B)" lines 246-254.
4. R3-024: snapshot rung3-run-log/rung3-snapshots/R3-024-L3/ (manifest_sha256 field 0aa2cb239c8c5b75d900c42fbe1fc7559836729dcc6902086eb5b06d4f95c02d). Key: section "## R3-024 (Tier B)" lines 307-313.

Grade each case PASS, FAIL, or INVALID by applying the key section's criteria to the snapshot evidence exactly as in real scoring (including the list section 1 invalid definition for bot-check evidence). Tier A cases: you may run rung3-ci/tier-a-check.py against the frozen key JSON as real scorers do, and state that you did.

## Deliverables (per case: 1 verdict json + 1 grade md)

Branch: clone1/calibration-sealed-20261126. Directory: rung3-run-log/calibration/clone1/.
- R3-002-calibration-grade.md + R3-002-calibration.json (same pattern for R3-013, R3-016, R3-024).
- Each grade md: your session id, both key hashes, manifest hash, per-file hash verification result, files_read list (allowlist only), independence declaration ("I graded blind from the snapshot and key section only; I did not read the ledger, any grade file, or any other verdict for these tasks"), verdict + reasons tied to specific files.
- Each json: task, verdict, session, keyfile_sha256 (json hash 5059f6c4...), manifest hash, files_read list.
- Push with explicit pathspec; verify via ls-remote. Notify the coordinator in chat with the branch name only (no verdict values in chat).

Pass bar: 4 of 4 agreement with the sealed verdicts. Under 4 of 4: one re-calibration on a second sealed set maximum; twice under means fresh sessions fill your scoring quota. The verifier sign-off names cases, hashes, and agreement.
