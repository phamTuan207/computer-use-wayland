# Sealed calibration assignment - Clone2 (R3-L3 resume, check 7)

From: run coordinator epoch 10. To: Clone2. Date: 2026-11-26.
Purpose: you are scorer 2 for R3-027 (Pair A) and 15 scoring assignments in the remaining run. Before you score any real task, you must calibrate 4 of 4 blind on a sealed held-out set (fix A F6). A verifier (TB-A lineage) sealed the set and will re-grade your cases from scratch and sign off. R3-027 may drive before this passes; your R3-027 scoring waits for the sign-off.

Standing rules (restated): ydotool is BANNED. English for all work. NO personal info on GitHub. Git: explicit pathspec on add and commit, never git add -A, never leave files staged, verify pushes via ls-remote. Never assume a capability; ask the coordinator directly if anything is unclear. Pill rule: you never drive in this task; if you ever control a browser, the "Computer use active" pill must show first. Tab rules: never close or navigate owner-opened tabs, pinned tabs, or essentials. Timeout: file all 4 grades within 60 minutes of this assignment.

Event-log duty: log key events (decisions, test results, fix milestones, revert actions, invalid rulings, gate results) via ~/workspace/agent-event-log/log-event.sh to the master log on the laptop at ~/agent-event-log/events.log, and keep state notes and per-task reports complete for the 15-minute harvest.

Ponytail (applies if you write any code; grading needs none): smallest complete change, reuse what exists before writing, standard library and platform before new dependencies, no unrequested abstraction, one small test for non-trivial logic, never cut validation, security, error handling, or accessibility. Confirm whether the ponytail skill is available to you before starting; if not, this brief text is your ruleset. State your answer in your first grade file.

User-path note: grading is not a user-facing test; you grade saved evidence. Real entry point: the sealed snapshots on branch todolist-push (paths below) plus the frozen key sections. Forbidden shortcuts for this task: reading the ledger (R3-L3-grades.jsonl, R3-L3-reruns.jsonl), reading any existing grade file or verdict json for these 4 tasks, reading the live sites, reading other scorers' verdicts, contacting the runner or the other candidate.

## The 4 cases (grade all 4, blind)

Pull branch todolist-push first. For each case, your allowlist is ONLY: the snapshot dir + the key section named. Verify every snapshot file sha256 against its manifest.json before grading; record the manifest hash. Verify key hashes: docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60; docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8. Record both in every grade file.

1. R3-001: snapshot rung3-run-log/rung3-snapshots/R3-001-L3/ (manifest_sha256 field 507086e2d379475fb3b9403a3e86deac4fa96d2c9777cdd6242fafde03d4d2ca). Key: docs/rung3-answer-keys.md section "## R3-001 (Tier B)" lines 109-118.
2. R3-007: snapshot rung3-run-log/rung3-snapshots/R3-007-L3/ (manifest_sha256 field 4be235466584890828e249224f0a8700a0f5f2eb783eaa4c609ac90c9d87a7c2). Key: section "## R3-007 (Tier A)" lines 173-184.
3. R3-011: snapshot rung3-run-log/rung3-snapshots/R3-011-L3/ (manifest_sha256 field df6d1163774df6c1719fd448b43bdb47257f5d2375e1c321fe0e8e4d9182aa1f). Key: section "## R3-011 (Tier B)" lines 213-224.
4. R3-014: snapshot rung3-run-log/rung3-snapshots/R3-014-L3/ (manifest_sha256 field b6540e2c0cb71c03830f8a902d95447bf8f427fc18ccb1b9e81a7ac2c1115e23). Key: section "## R3-014 (Tier A)" lines 237-245.

Grade each case PASS, FAIL, or INVALID by applying the key section's criteria to the snapshot evidence exactly as in real scoring (including the list section 1 invalid definition for bot-check evidence). Tier A cases: you may run rung3-ci/tier-a-check.py against the frozen key JSON as real scorers do, and state that you did.

## Deliverables (per case: 1 verdict json + 1 grade md)

Branch: clone2/calibration-sealed-20261126. Directory: rung3-run-log/calibration/clone2/.
- R3-001-calibration-grade.md + R3-001-calibration.json (same pattern for R3-007, R3-011, R3-014).
- Each grade md: your session id, both key hashes, manifest hash, per-file hash verification result, files_read list (allowlist only), independence declaration ("I graded blind from the snapshot and key section only; I did not read the ledger, any grade file, or any other verdict for these tasks"), verdict + reasons tied to specific files.
- Each json: task, verdict, session, keyfile_sha256 (json hash 5059f6c4...), manifest hash, files_read list.
- Push with explicit pathspec; verify via ls-remote. Notify the coordinator in chat with the branch name only (no verdict values in chat).

Pass bar: 4 of 4 agreement with the sealed verdicts. Under 4 of 4: one re-calibration on a second sealed set maximum; twice under means fresh sessions fill your scoring quota. The verifier sign-off names cases, hashes, and agreement.
