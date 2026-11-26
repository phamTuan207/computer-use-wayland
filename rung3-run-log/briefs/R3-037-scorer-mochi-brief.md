# R3-037 scorer brief (Mochi, Pair A scorer 1) - R3-L3

From: run coordinator epoch 16. To: Mochi.
You are scorer 1 (Pair A) for R3-037. Score from the pushed snapshot only, independently of scorer 2 (Clone1). Never contact the runner or scorer 2 about this task.

Standing rules (restated): ydotool is BANNED (you never drive). English for all work. NO personal info on GitHub. Git: explicit pathspec on add and commit, never git add -A, never leave files staged, verify pushes via ls-remote. Pill rule: you never control a browser in this task; if you ever do, the "Computer use active" pill must show first. Tab rules: never close or navigate owner-opened tabs, pinned tabs, or essentials. Timeout: file your verdict within 30 minutes of the snapshot push notice.

Event-log duty: log key events (decisions, test results, fix milestones, revert actions, invalid rulings, gate results) via ~/workspace/agent-event-log/log-event.sh to the master log on the laptop at ~/agent-event-log/events.log, and keep state notes and per-task reports complete for the 15-minute harvest.

Ponytail (applies if you write any code; scoring needs none): smallest complete change, reuse what exists before writing, standard library and platform before new dependencies, no unrequested abstraction, one small test for non-trivial logic, never cut validation, security, error handling, or accessibility.

User-path note: scoring is not a user-facing test; you grade saved evidence. Real entry point: the pushed snapshot (path below) plus the frozen key section. Forbidden shortcuts for this task: reading the live site, reading scorer 2's verdict, reading the ledger row for this task before filing, contacting the runner.

## Scoring assignment R3-037 (Tier B)

Snapshot: rung3-run-log/rung3-snapshots/R3-037-L3/ on todolist-push (pull after the coordinator's push notice; verify every file sha256 against manifest.json and record the manifest hash).
Key: docs/rung3-answer-keys.md section "## R3-037 (Tier B)" (verify key hashes: md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60; json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8; record both).

Grade PASS, FAIL, or INVALID by applying the key section's criteria to the snapshot evidence (2 WHOIS result screenshots + ket-qua.txt 2 rows with registrar, expiry date, name servers, status). Values are live at run time; the screenshots are the ground truth. Judge from the snapshot files, not from any report text. If the snapshot evidences a reCAPTCHA or human-verification block on who.is, INVALID is the ruling per the list section 1 invalid definition; file your verdict either way.

## Deliverables

Branch: mochi/verdict-R3-037-L3. Directory: rung3-run-log/verdicts/R3-037-L3/.
- R3-037-L3-mochi.json (verdict, session id, keyfile_sha256 = the json hash above, manifest hash, files_read list).
- R3-037-L3-mochi-grade.md (verdict + reasons tied to specific files, per-file hash verification result, independence declaration: "I graded independently from the snapshot and key section only; I did not read scorer 2's verdict or contact the runner.").
Push with explicit pathspec; verify via ls-remote. Notify the coordinator with the branch name only (no verdict value in chat).
