# Batch 7 corrections to the three HIGH evidence violations (V1, V2, V3)

- Author: clone2, batch 7 task 3, 22/11/2026.
- Basis: clone1 audit docs/clone1-evidence-audit-full-20261121.md (commit 581736e), independently verified by clone2 docs/clone2-violation-verify-20261122.md (commit ebf6ec8, all 13 UPHELD). Anchor tip for the checks below: origin/todolist-push c19c227.
- Method: read-only git checks (git ls-tree, git cat-file, git grep, git log --all for every missing path), plus a search of the clone2 VM workspace and /tmp. No test was run: there is no code to test, the work is evidence recovery. No file, log, number, or evidence item in this document is invented. Where the source material is gone, this document says so.
- What this document does: it corrects the record for the three HIGH violations in one place, so a reader does not have to trust a citation that cannot be checked. It does NOT restore the missing material. Each section states what is still missing and what would be needed for a full fix.

## V1 (HIGH): H3 gate acceptance has no in-repo record. Record corrected, acceptance still missing.

Claim as written in five places: the H3 gate question is resolved because the Y13r2 proposal (5a2b69d NO VERDICT plus runner-quiet/ports check counts as the marker leg) was accepted per MEMORY.md 22:57.

Sites, verified at tip c19c227:
- improvements/opt-council-m2-verdict.md:90 (G-10) and :107 (U-1).
- improvements/opt-crawl-src-20261121.md:148 (G8).
- improvements/optimal-fix-method-20261121.md:198 (Y13r2 BLOCK items).
- improvements/worker-f1-guardian-fix-log.md:862 (H3 gate line). A dated correction entry was appended to this log by this task; the other three files were NOT edited, because two are council/method papers (optimal-fix-method-20261121.md states it is amended only by a new council + redteam cycle, and a worker must not edit it directly) and one is a council verdict record. Their text still carries the old wording; this document is the correction for those sites.

Checks, all done 22/11/2026:
- MEMORY.md exists on no branch (git cat-file fails on todolist-push and on main) and never existed in git history on any branch (git log --all -- MEMORY.md returns nothing). It does not exist on the clone2 VM either.
- The proposal commit 5a2b69d DOES exist ("Y6c: nested v2 run BLOCKED at launch ... NO VERDICT, probes + evidence"). What exists is the proposal, not its acceptance. No council paper, log entry, or owner message in the repo records who accepted the proposal, in what file, at what time. The redteam already flagged this (opt-redteam-m-skeptic.md:58 P-33, opt-redteam-m-verdict.md:33,81 AM-13), and the method file itself requires the acceptance to be cited in a council paper or log entry, not only MEMORY.md 22:57.

Corrected status: the H3 gate acceptance is UNVERIFIED from repo evidence. The Y13 live run must not treat the gate as resolved on this citation alone.

What is needed for a full fix: the coordinator re-records the acceptance decision in a council paper or log entry in the repo (who accepted, when, on what basis), per AM-13. Only the coordinator can do this, because only the coordinator can read the MEMORY.md 22:57 entry. Clone2 cannot write that record without inventing a decision it did not witness.

Precision note: not every MEMORY.md 22:57 citation is equally broken. The re.py deleter claim citing the same entry (opt-council-m2-verdict.md:71,108, opt-crawl-src-20261121.md:148 G8) is independently corroborated in-repo by the VMFIX commit c16dd4e, which exists. Only the H3 acceptance lacks any in-repo corroboration.

## V2 (HIGH): F3 arm verdicts cite 14 run logs that do not exist. Record corrected, logs still missing.

Claim as written in improvements/worker-f3b-restart-log.md STEP 4 and STEP 5: Arm A/B/C/D PASS and Arm E FAIL (wedge reproduced), each citing its run log and probe log.

Missing logs, all 14 checked 22/11/2026 (git cat-file on every path, whole-branch filename search, git log --all, clone2 VM search):
- arm_a_run2.log, probe_a2.log (Arm A run 3, lines 64-65).
- arm_b_run.log, probe_b.log (Arm B, lines 66-67).
- probe_c.log (Arm C, line 72).
- arm_d_run.log, probe_d.log (Arm D attempt 1, lines 73-74).
- arm_d_run2.log, probe_d2.log (Arm D attempt 2, lines 75-76).
- arm_e_run.log, probe_e.log (Arm E, lines 77, 79).
- probe_f.log (BiDi-close probe, line 82).
- probe_r3.log (restart #3 probe, line 85).
- relaunch-f3b.log (STEP 3 relaunch attempt 1, line 55).
The clone1 audit (V2) listed 9 of these; the other 5 (arm_d_run.log, probe_d.log, probe_f.log, probe_r3.log, relaunch-f3b.log) are cited in the same log and are missing too. None ever existed in git history on any branch. improvements/f3-evidence/ holds exactly 14 files, none of them a run log for arms A-E.

What was checked as possible corroboration, and failed:
- improvements/f3-evidence/full.log (59 lines) and result_full.json are from the earlier full close3 run (68 tabs, 52 closed), not from the STEP 4 arms, and contain none of the arm session IDs (0979bcf5, 29183d85, 2d3cd2de, 6304b1d8) or probe IDs.
- The verdict rows themselves are present in the log with inline session IDs, handle counts, exit codes and probe results recorded at the time. That inline summary is real, but it is the only surviving evidence.

Corrected status: the arm verdicts rest on the inline summary in the log only. The raw logs cannot be re-checked from the repo. A dated correction entry stating this was appended to improvements/worker-f3b-restart-log.md by this task; no existing line was changed.

What is needed for a full fix: the 14 logs from the laptop where the arms ran, committed under improvements/f3-evidence/, or a re-run of arms A-E with logs committed.

## V3 (HIGH): the 130/130 judge verdict's evidence files are not in the repo. Record corrected, evidence still missing.

Claim as written in improvements/live-test-log.md:991 (as of todolist-push c19c227): "VERDICT: 130/130, 13/13 full passes. tc02 10/10 (3/3 byte-exact 50/50, SHA 8da1f562...); tc01-tc13 each 10/10."

Missing evidence files, all checked 22/11/2026 (whole-branch filename search, git log --all, clone2 VM search):
- test-cases.md, test-scores.md (174 lines), typing-fix-multipage-report.md, test-execution-report.md, stress.log.
- 14 judge state.json files, finish-record.json, start-readiness.json.
- 20 screenshots in /tmp/judge/.
None exists anywhere on the branch or in git history on any branch. None exists on the clone2 VM. No judge screenshot exists in the repo (the only "judge" filenames on the branch are improvements/worker-y8b-judge-b1-v2.2.md and improvements/worker-y8b-judge-void.md, unrelated).

What IS corroborated in-repo, and its limit:
- The SHA 8da1f562... cited for tc02 is the expected hash of the 50-byte test sentence, recorded in-repo at scripts/plans/tc02-v1.json:9, and the trial entries in the live-test-log itself (lines 836, 938, 941, 2091) record the same SHA for the tc02 trials. That corroborates the sentence hash, not the judge's per-case scores, and the trial entries are the same log, not independent evidence.
- The verdict section honestly lists WITHHELD items (pill/overlay visibility, cursor-glyph appearance, Worker N's offline claims not re-verified), so the judge did not overclaim scope. That honesty does not substitute for the missing files.

Corrected status: the 130/130 verdict is UNVERIFIABLE from repo evidence; only the inline summary at line 991 survives. A dated correction entry stating this was appended to improvements/live-test-log.md by this task; no existing line was changed.

What is needed for a full fix: the 5 report files, stress.log, the 16 JSON files and the 20 screenshots from the laptop/VM where the judge ran, committed to the repo, or a re-run of the judge with evidence committed.

## Summary

| # | Severity | Record corrected in-repo | Still missing (UNFIXABLE FROM HERE) | Full fix needs |
|---|----------|--------------------------|-------------------------------------|----------------|
| V1 | HIGH | Yes: this document plus a correction entry appended to improvements/worker-f1-guardian-fix-log.md; H3 acceptance now marked UNVERIFIED | The acceptance record itself (MEMORY.md 22:57, laptop-only) | Coordinator re-records the acceptance in a council paper or log entry (AM-13) |
| V2 | HIGH | Yes: correction entry appended to improvements/worker-f3b-restart-log.md; arm verdicts now marked inline-summary-only; 14 missing logs listed (audit had 9) | All 14 run/probe logs | The 14 logs from the laptop, or a re-run of arms A-E with logs committed |
| V3 | HIGH | Yes: correction entry appended to improvements/live-test-log.md; 130/130 verdict now marked UNVERIFIABLE from repo evidence | 5 report files, stress.log, 16 JSON files, 20 screenshots | The files from the laptop/VM where the judge ran, or a re-run of the judge with evidence committed |

No existing line in any of the three logs was changed. All corrections are dated appends plus this document. Nothing in this document or in the appended entries is invented: every missing file was checked by git cat-file, whole-branch search, and git log --all, and every surviving corroboration is cited with file and line.
