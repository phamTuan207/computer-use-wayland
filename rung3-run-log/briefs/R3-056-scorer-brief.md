# Task 56 scorer briefs (position 56, Class L, counted)

Prepared by coordinator (epoch 24), 2026-11-27. Scorers per F5.2: Mochi + Clone2 (scorer 1 = Mochi, scorer 2 = Clone2 per table "Mochi plus Clone2"). Prep: coordinator-live (F5.2 row; the task brief is improvements/r3-l3-task56-restore-tabs-20261126.md, epoch 8 finalized, unchanged). Reviewer: Mei (F5.2 row). Disjointness re-checked: prep = coordinator-live, scorers = Mochi + Clone2, reviewer = Mei, no overlap. Runner: Muse fresh independent subagent by default (Codex approved alternative if the Muse runner fails twice; opencode never assigned).

## VM-local restriction (F8.3, verbatim, must be honored by both scorers)

Task 56 tab URLs are owner data. The task 56 snapshot stays VM-local by default. It is not pushed with full URLs unless the owner approves (notification point F2.4 item 4 covers ambiguity; a push decision is separate and explicit). Scorers for task 56 (Mochi plus Clone2, F5 table) grade from the VM-local snapshot plus the coordinator live verification note, with URLs redacted to host plus path pattern where the key allows. If redaction would break grading, the coordinator asks the owner before pushing. Default is no push of task 56 URLs. This restriction must appear in council-3 operations (section 3.2 currently lists the restore set without it) and verbatim in both task 56 scorer briefs before position 56 arrives. This record deliberately does not reproduce the restore URLs; the sessionstore on the laptop is the source of truth, and any list in a brief stays VM-local.

Practical effect: grade from the VM-local snapshot directory the coordinator names at assignment (not from a repo snapshot). Do NOT commit full URLs anywhere. In your verdict files, refer to tabs by host + path pattern (for example youtube.com, docs.google.com/spreadsheets/<id>) unless the coordinator tells you otherwise.

## Independence

- Score independently from the snapshot + task key only. Do NOT read the other scorer's verdict, the ledger row for task 56, or the drive report. Do NOT contact the runner.
- Class L score-before-reset: the restored tabs stay LIVE; the coordinator verifies against the live tab list + sessionstore before scoring closes and files a live verification note into the snapshot. No reset exists for this task.

## Task + key (summary; full text in improvements/r3-l3-task56-restore-tabs-20261126.md)

- Restore 8 tabs closed in the 2026-11-26 02:15 cleanup, from the preserved sessionstore (laptop ~/zen-sessionstore-pre-cleanup-20261126.jsonlz4; source of truth for URLs, pinned/zenEssential flags, zenWorkspace, order).
- 5 ESSENTIALS inserted after the first YouTube and before GitHub, in order: YouTube (2nd copy), Reddit, Todoist Today, Gmail, Google Calendar.
- 3 PINNED at the head of the pinned section, in order: PCCV CF26 Google Sheet, Free Claude Code Admin, Welcome.
- 16 closed normal tabs NOT restored.
- Pass: all 8 tabs present with exact URLs from the preserved sessionstore, correct pinned/essential flags, correct workspaces, correct insertion order, verified from tab list + sessionstore, ket-qua.txt complete, screenshot shows the restored order.
- Fail: any tab missing, wrong URL, wrong pinned/essential state, wrong workspace, wrong order, or a normal task tab recreated instead.
- If pinned or essential state cannot be determined from the preserved sessionstore, the coordinator asks the owner to confirm before position 56 (notification point); do not guess the setup.

## Before any INVALID grade

- Record whether an infrastructure re-run was considered (infrastructure_rerun_considered + note).

## Deliverables

- Mochi (scorer 1): commit the verdict JSON + grade md to branch mochi/verdict-R3-056-L3 under rung3-run-log/verdicts/R3-056-L3/ (explicit pathspec, add+commit atomically, push, verify ls-remote), with URLs redacted per F8.3. Coordinator copies to ~/workspace/rung3-verdicts/R3-056-B1.json + R3-056-B1-grade.md. Verdicts via branch only, never chat.
- Clone2 (scorer 2): commit the verdict JSON + grade md to branch clone2/verdict-R3-056-L3 under rung3-run-log/verdicts/R3-056-L3/ (explicit pathspec, add+commit atomically, push, verify ls-remote), with URLs redacted per F8.3. Coordinator copies to ~/workspace/rung3-verdicts/R3-056-B2.json + R3-056-B2-grade.md.
- Verdict JSON fields: verdict (PASS/FAIL/INVALID), task_id ("R3-056" or "Task 56" per coordinator instruction at assignment), session, timestamp (Asia/Ho_Chi_Minh), manifest_sha256 (VM-local snapshot manifest), files_read, per-criterion results, infrastructure_rerun_considered + note.
- Include the full event log chain (failure -> reasoning -> attempts -> decision -> fix -> outcome) per the 18:20 super-detailed logging rule.
- English only, no personal info, no em/en dashes. No full tab URLs in any committed file (F8.3).
- Ponytail for any code: smallest complete change, reuse before writing, stdlib/platform before dependencies, no unrequested abstraction, one small test for non-trivial logic, never cut validation/security/error handling. Graphify for codebase context if needed (~/workspace/cu-graphify/graphify-out/).
