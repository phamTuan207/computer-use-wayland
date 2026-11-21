# Batch 7 task 3: independent verification of clone2's HIGH fixes (V1, V2, V3)

- Verifier: clone1, batch 7 task 3, 22/11/2026, 04:01 to 04:10 +07.
- What I found first: clone2 had already fixed the three HIGH violations (docs/clone2-batch7-high-fixes-20261122.md, commits 748cc35, 219720c, 05ee34d, 16c4196 on todolist-push). I did NOT duplicate the fixes. This report independently verifies them.
- Anchor tip: origin/todolist-push da60024 (clone2 checked at c19c227; the tip moved twice since, and every correction below was re-checked at da60024).
- Method: read-only git checks only (git show, git cat-file, git grep, git ls-tree, git log --all, git merge-base). No file was edited on todolist-push, no test was run (there is no code to test, the work is evidence recovery). No file, log, number, or evidence item was invented anywhere in this task.

## Outcome summary

All three HIGH violations are PARTIALLY FIXED, exactly as clone2 reported. 0 discrepancies found in clone2's fixes. In each case the record in the repo is now corrected and the correction is still present at the current tip; in each case the underlying missing material is still missing, because it lives only on the user's laptop or VM and was never committed anywhere. That part is UNFIXABLE FROM HERE.

| # | Severity | Status | Fix commits on todolist-push |
|---|----------|--------|------------------------------|
| V1 | HIGH | PARTIALLY FIXED, verified: H3 acceptance marked UNVERIFIED; acceptance record itself still missing | 05ee34d, 16c4196 |
| V2 | HIGH | PARTIALLY FIXED, verified: arm verdicts marked inline-summary-only; 14 missing logs listed (audit had 9) | 748cc35, 16c4196 |
| V3 | HIGH | PARTIALLY FIXED, verified: 130/130 verdict marked UNVERIFIABLE; evidence files still missing | 219720c, 16c4196 |

Fix commits are ancestors of the current tip (git merge-base --is-ancestor 16c4196 origin/todolist-push: yes). All four commits are pure insertions (5, 5, 4, 78 lines added, 0 deleted). No existing line in any of the three logs was changed. Added lines contain 0 em dashes and 0 en dashes (checked per commit).

## V1 (HIGH): H3 gate acceptance. PARTIALLY FIXED, verified.

What clone2 did, and what I re-checked at da60024:
- Correction entry appended to improvements/worker-f1-guardian-fix-log.md (commit 05ee34d, 5 lines, at the end of the file). Present at the tip (tail read back verbatim). It states the H3 gate line at line 862 cites no acceptance artifact, MEMORY.md exists on no branch and never existed in git history, the proposal commit 5a2b69d exists but no council paper, log entry, or owner message records who accepted it, and the corrected status is UNVERIFIED, to be re-recorded by the coordinator before the Y13 live run treats it as resolved. It also notes the re.py deleter claim is independently corroborated by VMFIX commit c16dd4e.
- Consolidated corrections document improvements/batch7-high-corrections-20261122.md (commit 16c4196, 78 lines). Present at the tip, read in full. It records the correction for all five sites and states the other three files were not edited (two are council/method papers, one is a council verdict record).
- My checks, all at da60024: git log --all -- MEMORY.md returns nothing (never existed in any history). Commit 5a2b69d exists ("Y6c: nested v2 run BLOCKED at launch ... NO VERDICT, probes + evidence"). Commit c16dd4e exists ("VMFIX: VM Python re breakage verified + durable"). All five citation sites still carry the original claim at the cited lines: opt-council-m2-verdict.md:90 (G-10, H3 resolved per MEMORY.md 22:57) and :107 (U-1, H3 RESOLVED per MEMORY.md 22:57), opt-crawl-src-20261121.md:148 (G8, line is 767 chars; the H3 acceptance text is at the end of the line), optimal-fix-method-20261121.md:198 (H3 gate: accepted Y13r2 proposal), worker-f1-guardian-fix-log.md:862 (H3 gate: accept Y13r2's proposal). The method file line 131 requires the acceptance to be cited in a council paper or log entry, not only MEMORY.md 22:57 (AM-13). The method file line 202 states it is amended only by a new council + redteam cycle and a worker does not edit it directly, so clone2 was right not to edit it.

Still missing (UNFIXABLE FROM HERE): the acceptance record itself (MEMORY.md 22:57, laptop-only). Full fix needs the coordinator to re-record the acceptance decision in a council paper or log entry (who accepted, when, on what basis), per AM-13. Only the coordinator can do this, because only the coordinator can read that MEMORY.md entry.

## V2 (HIGH): F3 arm verdicts cite missing run logs. PARTIALLY FIXED, verified.

What clone2 did, and what I re-checked at da60024:
- Correction entry appended to improvements/worker-f3b-restart-log.md (commit 748cc35, 5 lines). Present at the tip (grep count for "BATCH 7 CORRECTION" is 1). It lists all 14 missing logs and states the arm verdicts rest on the inline summary in the log only.
- My checks, all at da60024: git cat-file fails for all 14 paths under improvements/f3-evidence/ (arm_a_run2.log, probe_a2.log, arm_b_run.log, probe_b.log, probe_c.log, arm_d_run.log, probe_d.log, arm_d_run2.log, probe_d2.log, arm_e_run.log, probe_e.log, probe_f.log, probe_r3.log, relaunch-f3b.log). improvements/f3-evidence/ holds exactly the 14 files clone2 lists (arm_a.py, arm_b.py, arm_d.py, arm_e.py, bidi-tabs-225805-redacted.json, bidi-tabs-231520.json, cleanup_full.py, close3.py, full.log, parse_sessionstore.py, probe_session.py, rclick.py, result_full.json, verify_list.py). The cited lines in the log read exactly as clone2 says: lines 64-65 Arm A verdict PASS (arm_a_run2.log + probe_a2.log, session 0979bcf5), lines 66-67 Arm B verdict PASS (arm_b_run.log + probe_b.log, session 29183d85), line 72 Arm C verdict PASS (probe_c.log), lines 73-74 Arm D attempt 1 FAILED (arm_d_run.log + probe_d.log), lines 75-76 Arm D attempt 2 verdict PASS (arm_d_run2.log + probe_d2.log, session 2d3cd2de), lines 77 and 79 Arm E verdict FAIL, WEDGE REPRODUCED (arm_e_run.log + probe_e.log, session 6304b1d8), line 82 BiDi-close probe (probe_f.log), line 85 restart #3 probe (probe_r3.log), line 55 STEP 3 relaunch attempt 1 (relaunch-f3b.log). None of the four arm session IDs (0979bcf5, 29183d85, 2d3cd2de, 6304b1d8) appears in full.log or result_full.json (0 hits each), so those two files do not corroborate the arms.

Still missing (UNFIXABLE FROM HERE): all 14 run/probe logs. Full fix needs the 14 logs from the laptop where the arms ran, committed under improvements/f3-evidence/, or a re-run of arms A-E with logs committed.

## V3 (HIGH): 130/130 judge verdict evidence missing. PARTIALLY FIXED, verified.

What clone2 did, and what I re-checked at da60024:
- Correction entry appended to improvements/live-test-log.md (commit 219720c, 4 lines). Present at the tip (grep count for "BATCH 7 CORRECTION" is 1). It states the 130/130 verdict at line 991 cites evidence files that are not in the repo and the corrected status is UNVERIFIABLE, with only the inline summary surviving.
- My checks, all at da60024: the verdict line still reads "VERDICT: 130/130, 13/13 full passes. tc02 10/10 (3/3 byte-exact 50/50, SHA 8da1f562...); tc01-tc13 each 10/10." at line 991. Whole-branch filename search finds none of test-cases.md, test-scores.md, test-execution-report.md, typing-fix-multipage-report.md, stress.log, finish-record.json, start-readiness.json. The only filenames containing "judge" on the branch are improvements/worker-y8b-judge-b1-v2.2.md and improvements/worker-y8b-judge-void.md, unrelated. The SHA corroboration holds: scripts/plans/tc02-v1.json:9 records expected_sha256 8da1f5624c1b482bcdfae9d7c6883fdc52313dbe4120c2d1df2623ec5bcb9772, and the trial entries at lines 836, 938, 941, 2091 record the same SHA. That corroborates the sentence hash, not the judge's per-case scores.

Still missing (UNFIXABLE FROM HERE): the 5 report files, stress.log, the 16 JSON files, and the 20 screenshots. Full fix needs those files from the laptop/VM where the judge ran, committed to the repo, or a re-run of the judge with evidence committed.

## Precision notes

- None of my checks contradicts any claim in clone2's fix report or in the corrections document. The one place I first suspected an error, the V1 "five places" list including opt-crawl-src-20261121.md:148, turned out to be correct: the line is 767 characters long and ends with "H3 gate: Y13r2 proposal accepted (5a2b69d NO VERDICT + runner-quiet/ports check counts as the done marker leg for this run, gate text unchanged, Y6 retry after Y13)."
- The audit's V2 listed 9 missing logs; the true count is 14, as clone2 found. The 5 extra logs (arm_d_run.log, probe_d.log, probe_f.log, probe_r3.log, relaunch-f3b.log) are cited at lines 55, 73-74, 82, 85 of the F3b log and are missing too. I verified all 5 citations and all 5 absences.
- The corrections document says its checks were done at anchor tip c19c227. I re-ran every check at the current tip da60024 and every result still holds.

## What awaits Muse's decision

1. V1 full fix: the coordinator re-records the H3 acceptance in a council paper or log entry (who accepted, when, on what basis), per AM-13. Only the coordinator can do this. Until then the Y13 live run must not treat H3 as resolved on the MEMORY.md 22:57 citation alone.
2. V2 full fix: the 14 logs from the laptop, or a re-run of arms A-E with logs committed under improvements/f3-evidence/. Needs the owner or the laptop worker.
3. V3 full fix: the 5 report files, stress.log, 16 JSON files and 20 screenshots from the laptop/VM, or a re-run of the judge with evidence committed. Needs the owner or the judge worker.
4. Nothing further is fixable from this machine. No additional commit on todolist-push is needed from clone1 for these three HIGHs; the record is corrected and the gaps are named with exact file lists.
