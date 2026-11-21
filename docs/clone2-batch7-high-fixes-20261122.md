# Batch 7 task 3: fix the three confirmed HIGH violations (V1, V2, V3)

- Worker: clone2, batch 7 task 3, 22/11/2026, work window 02:24 to 02:29 +07 (about 5 minutes, all read-only git checks plus 4 small commits).
- Basis: clone1 audit docs/clone1-evidence-audit-full-20261121.md (581736e), independently verified by clone2 docs/clone2-violation-verify-20261122.md (ebf6ec8, all 13 UPHELD). Anchor tip: origin/todolist-push c19c227.
- Method: read-only git checks for every missing path (git ls-tree, git cat-file, git grep, git log --all), plus a search of the clone2 VM workspace and /tmp. No test was run: there is no code to test, the work is evidence recovery. No file, log, number, or evidence item was invented anywhere in this task.
- Where the fixes live: the violations are on todolist-push, so the fixes are on todolist-push, pushed as tip 16c4196. This report is on main.

## Outcome summary

All three HIGH violations are PARTIALLY FIXED. In each case the record in the repo is now corrected: the false or unverifiable claim is marked with its honest status, with exact file and line references and the evidence for the correction. In each case the underlying missing material is still missing, because it lives only on the user's laptop or VM and was never committed anywhere. That part is UNFIXABLE FROM HERE, and each section below states exactly what would be needed for a full fix. Nothing was fabricated to fill the gaps.

| # | Severity | Status | Commits on todolist-push |
|---|----------|--------|--------------------------|
| V1 | HIGH | PARTIALLY FIXED: H3 acceptance now marked UNVERIFIED from repo evidence; acceptance record itself still missing | 05ee34d, 16c4196 |
| V2 | HIGH | PARTIALLY FIXED: arm verdicts now marked inline-summary-only; 14 missing logs listed (audit had 9) | 748cc35, 16c4196 |
| V3 | HIGH | PARTIALLY FIXED: 130/130 verdict now marked UNVERIFIABLE from repo evidence; evidence files still missing | 219720c, 16c4196 |

## V1 (HIGH): H3 gate acceptance. PARTIALLY FIXED.

What was done:
- Checked all five citation sites at tip c19c227: improvements/opt-council-m2-verdict.md:90 and :107, improvements/opt-crawl-src-20261121.md:148, improvements/optimal-fix-method-20261121.md:198, improvements/worker-f1-guardian-fix-log.md:862. All five still say the gate is resolved per MEMORY.md 22:57.
- Proved MEMORY.md is absent: it exists on no branch and never existed in git history on any branch (git log --all -- MEMORY.md returns nothing), and it does not exist on the clone2 VM.
- Proved the proposal itself is real but is not an acceptance: commit 5a2b69d exists ("Y6c: nested v2 run BLOCKED at launch ... NO VERDICT, probes + evidence"). No council paper, log entry, or owner message in the repo records who accepted it.
- Appended a dated correction entry to improvements/worker-f1-guardian-fix-log.md (commit 05ee34d), stating the H3 acceptance is UNVERIFIED from repo evidence and must be re-recorded by the coordinator before the Y13 live run treats it as resolved. No existing line was changed.
- Wrote the consolidated corrections document improvements/batch7-high-corrections-20261122.md (commit 16c4196), which records the correction for all five sites. The other three files were NOT edited: two are council/method papers (optimal-fix-method-20261121.md states it is amended only by a new council + redteam cycle, and a worker must not edit it directly) and one is a council verdict record.
- Precision note found during the fix: not every MEMORY.md 22:57 citation is equally broken. The re.py deleter claim citing the same entry is independently corroborated in-repo by the VMFIX commit c16dd4e, which exists. Only the H3 acceptance lacks any in-repo corroboration.

Still missing (UNFIXABLE FROM HERE): the acceptance record itself (MEMORY.md 22:57, laptop-only). Full fix needs the coordinator to re-record the acceptance decision in a council paper or log entry (who accepted, when, on what basis), per AM-13. Only the coordinator can do this, because only the coordinator can read that MEMORY.md entry. Clone2 cannot write that record without inventing a decision it did not witness.

## V2 (HIGH): F3 arm verdicts cite missing run logs. PARTIALLY FIXED.

What was done:
- Checked all 14 cited log paths: arm_a_run2.log, probe_a2.log, arm_b_run.log, probe_b.log, probe_c.log, arm_d_run.log, probe_d.log, arm_d_run2.log, probe_d2.log, arm_e_run.log, probe_e.log, probe_f.log, probe_r3.log, relaunch-f3b.log. All 14 are missing: none exists under improvements/f3-evidence/ (14 files only), none exists anywhere on the branch, none ever existed in git history on any branch, none exists on the clone2 VM.
- New finding beyond the audit: the audit listed 9 missing logs; the other 5 (arm_d_run.log, probe_d.log, probe_f.log, probe_r3.log, relaunch-f3b.log, cited at lines 55, 73-74, 82, 85 of the F3b log) are missing too. V2 is 14 logs, not 9.
- Checked for corroboration and found none: improvements/f3-evidence/full.log (59 lines) and result_full.json are from the earlier full close3 run (68 tabs, 52 closed), not from the STEP 4 arms, and contain none of the arm session IDs (0979bcf5, 29183d85, 2d3cd2de, 6304b1d8) or probe IDs.
- Appended a dated correction entry to improvements/worker-f3b-restart-log.md (commit 748cc35), listing all 14 missing logs and stating the arm verdicts (A/B/C/D PASS, E FAIL with the wedge reproduced) rest on the inline summary in the log only. No existing line was changed.

Still missing (UNFIXABLE FROM HERE): all 14 run/probe logs. Full fix needs the 14 logs from the laptop where the arms ran, committed under improvements/f3-evidence/, or a re-run of arms A-E with logs committed.

## V3 (HIGH): 130/130 judge verdict evidence missing. PARTIALLY FIXED.

What was done:
- Checked every cited evidence file: test-cases.md, test-scores.md (174 lines), typing-fix-multipage-report.md, test-execution-report.md, stress.log, 14 judge state.json files, finish-record.json, start-readiness.json, 20 screenshots in /tmp/judge/. None exists anywhere on the branch or in git history on any branch, and none exists on the clone2 VM. No judge screenshot exists in the repo.
- Checked for corroboration: the SHA 8da1f562... cited for tc02 is the expected hash of the 50-byte test sentence, recorded in-repo at scripts/plans/tc02-v1.json:9, and the trial entries in the live-test-log itself record the same SHA. That corroborates the sentence hash, not the judge's per-case scores, and the trial entries are the same log, not independent evidence. The verdict section honestly lists WITHHELD items, which is noted but does not substitute for the missing files.
- Appended a dated correction entry to improvements/live-test-log.md (commit 219720c), stating the 130/130 verdict is UNVERIFIABLE from repo evidence and only the inline summary at line 991 survives. No existing line was changed. (Note: live-test-log.md already contains 706 em dashes and 17 en dashes in pre-existing content; this task added none.)

Still missing (UNFIXABLE FROM HERE): the 5 report files, stress.log, the 16 JSON files, and the 20 screenshots. Full fix needs those files from the laptop/VM where the judge ran, committed to the repo, or a re-run of the judge with evidence committed.

## Commits

On todolist-push (pushed, tip verified by ls-remote as 16c4196):
- 748cc35 docs: batch 7 correction V2, F3 arm logs missing, verdicts inline-summary-only.
- 219720c docs: batch 7 correction V3, 130/130 judge evidence missing, verdict unverifiable.
- 05ee34d docs: batch 7 correction V1, H3 acceptance unverified from repo.
- 16c4196 docs: batch 7 corrections record for HIGH violations V1 V2 V3.

No existing line in any of the three logs was changed. All corrections are dated appends plus the corrections document. Work was done in a separate worktree (~/workspace/tools/batch7-tp) so the main checkout was not disturbed.
