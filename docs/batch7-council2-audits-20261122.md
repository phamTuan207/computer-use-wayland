# Batch 7 council 2: independent verification of the HIGH fixes (V1, V2, V3)

- Verifier: batch 7 council 2, independent subagent, 22/11/2026, 04:13 to 04:30 +07.
- Reports reviewed: docs/clone1-batch7-high-fixes-verify-20261122.md (clone1 task 3, 56 lines by wc -l) and docs/clone2-batch7-high-fixes-20261122.md (clone2 task 3, 57 lines by wc -l). Audit appendix in docs/clone1-evidence-audit-full-20261121.md (458 lines by wc -l).
- Method: read-only git checks only (git fetch, git show, git cat-file, git grep, git ls-tree, git log --all, git merge-base, wc). No file edited, no test run (there is no code to test). No file, log, number, or evidence item invented.
- Anchor tip: origin/todolist-push da60024, fetched fresh for this review. The tip has NOT moved since da60024. The parent brief said it had moved; that is wrong. Clone1's report says the tip "moved twice" since c19c227; the log shows 36 commits between c19c227 and da60024, so that count is also wrong. Neither error affects any verdict: every check below was run at da60024, which is the current tip.

## Verdicts

| # | Severity | Verdict | Basis |
|---|----------|---------|-------|
| V1 | HIGH | PARTIALLY FIXED, CONFIRMED | Correction present at tip, five cited sites verified, acceptance record still missing |
| V2 | HIGH | PARTIALLY FIXED, CONFIRMED | Correction present at tip, all 14 logs absent, cited lines verbatim, session IDs 0 hits |
| V3 | HIGH | PARTIALLY FIXED, CONFIRMED | Correction present at tip, verdict line exact, all cited files absent, SHA corroboration holds |

## Fix commits: CONFIRMED exactly

All four clone2 fix commits exist on origin/todolist-push and are ancestors of tip da60024 (git merge-base --is-ancestor: yes for each). All are pure insertions with exactly the stated counts, and 0 em dashes and 0 en dashes in the added lines:

- 748cc35 "docs: batch 7 correction V2, F3 arm logs missing, verdicts inline-summary-only": 5 added, 0 deleted.
- 219720c "docs: batch 7 correction V3, 130/130 judge evidence missing, verdict unverifiable": 4 added, 0 deleted.
- 05ee34d "docs: batch 7 correction V1, H3 acceptance unverified from repo": 5 added, 0 deleted.
- 16c4196 "docs: batch 7 corrections record for HIGH violations V1 V2 V3": 78 added, 0 deleted.

Each correction is present at the tip: "BATCH 7 CORRECTION" count is 1 in each of the three logs. Positions: worker-f1-guardian-fix-log.md header at line 1207 of 1210 (end of file); worker-f3b-restart-log.md header at line 130 of 134 (end of file); live-test-log.md correction at line 4231 of 4233 (end of file). The corrections document improvements/batch7-high-corrections-20261122.md is 78 lines at the tip. I read all three correction entries and the corrections document in full; each says what the reports claim it says.

## V1 (HIGH): H3 gate acceptance. PARTIALLY FIXED, CONFIRMED.

Checks at da60024, all confirmed:
- `git log --all -- MEMORY.md` returns 0 lines. MEMORY.md exists nowhere on todolist-push (whole-branch filename search: none) and never existed in any history among the 36 remote-tracking branches fetched here.
- Commit 5a2b69d exists ("Y6c: nested v2 run BLOCKED at launch (F0 --socket/--wayland-fd, F1 hyprglass ABI dead, U5b wrong log); NO VERDICT, probes + evidence"). Commit c16dd4e exists ("VMFIX: VM Python re breakage verified + durable (SSH back 22:31-22:38)").
- All five citation sites still carry the claim at the cited lines: opt-council-m2-verdict.md:90 (G-10, "H3 gate question is resolved per MEMORY.md 22:57") and :107 (U-1, "H3 gate question is RESOLVED per MEMORY.md 22:57"); opt-crawl-src-20261121.md:148 (G8, ends with the H3 acceptance text); optimal-fix-method-20261121.md:198 ("H3 gate: accepted Y13r2 proposal (5a2b69d NO VERDICT + runner-quiet/ports check counts as the done marker leg for this run, gate text kept, Y6 retry after Y13). G-10's H3 resolution must be cited in a council paper or log entry, not only MEMORY.md 22:57 (AM-13)."); worker-f1-guardian-fix-log.md:862 ("H3 gate: accept Y13r2's proposal...", continuing on line 863).
- Method file line 131 requires the acceptance to be cited in a council paper or log entry, not only MEMORY.md 22:57 (AM-13). Method file line 202 states the file is amended only by a new council + redteam cycle and a worker does not edit it directly. Clone2 was right not to edit it.
- A whole-branch grep for accept+Y13r2/H3-gate finds no acceptance record beyond the claim sites and the redteam flags (P-33, AM-13). The claim "no council paper, log entry, or owner message in the repo records who accepted it" holds for the branch as fetched.
- The V1 correction entry (tail of worker-f1-guardian-fix-log.md) states exactly what clone1's report says: line 862 cites no acceptance artifact, MEMORY.md exists on no branch and never existed in git history, 5a2b69d exists but no council paper, log entry, or owner message records who accepted it, corrected status UNVERIFIED, re-record needed before the Y13 live run, and the re.py deleter claim is independently corroborated by c16dd4e.

Discrepancies (minor, no verdict change):
- D1. Line 148 is 766 characters, not 767. Both reports say 767. Measured three ways: awk length($0) = 766, Python len after stripping the newline = 766, wc -c = 767 (766 characters plus the line terminator). The reports counted bytes including the newline. This is the same +1 newline-counting error as batches 4, 5, and 6. Substance confirmed: the line ends with "H3 gate: Y13r2 proposal accepted (5a2b69d NO VERDICT + runner-quiet/ports check counts as the done marker leg for this run, gate text unchanged, Y6 retry after Y13)."
- D2. NEW FINDING: the H3 acceptance is stated as fact in TWO more places the "five places" list does not include. improvements/worker-f2-silence-fix-log.md:598: "H3 gate: accept Y13r2's proposal (5a2b69d NO VERDICT + a runner-quiet/ports check counts as a done-marker for this run, keep the gate text, Y6 retry after Y13)." improvements/worker-opt-method-log.md:81: "H3 gate: accept Y13r2 proposal (5a2b69d NO VERDICT + runner-quiet/ports check counts as the done marker leg for this run, keep gate text, Y6 retry after Y13)." The method-log line sits under a "Parent MEMORY.md updated 22:57" heading, so it rests on the same entry. The five-place count is correct for the exact citation string "MEMORY.md 22:57", but the claim itself stands uncorrected in these two logs. A reader of either log still sees H3 stated as accepted with no UNVERIFIED marker. Follow-up: append correction entries to those two logs too. This does not change the PARTIALLY FIXED verdict: the central record is corrected and the underlying acceptance record is still missing either way.
- Note: whole-branch lines citing the exact string "MEMORY.md 22:57" now total 20, up from 13 at the batch 6 audit. The increase is fully explained by the corrections themselves: 5 mentions in the new corrections document plus 2 in the V1 correction entry. Not a discrepancy.

Still missing (UNFIXABLE FROM HERE): the acceptance record itself (MEMORY.md 22:57, laptop-only). Full fix needs the coordinator to re-record the acceptance in a council paper or log entry (who accepted, when, on what basis), per AM-13.

## V2 (HIGH): F3 arm verdicts cite missing run logs. PARTIALLY FIXED, CONFIRMED.

Checks at da60024, all confirmed:
- All 14 logs absent by git cat-file on each path under improvements/f3-evidence/: arm_a_run2.log, probe_a2.log, arm_b_run.log, probe_b.log, probe_c.log, arm_d_run.log, probe_d.log, arm_d_run2.log, probe_d2.log, arm_e_run.log, probe_e.log, probe_f.log, probe_r3.log, relaunch-f3b.log. Each has 0 commits in git history on any branch (git log --all per path), and whole-branch filename search finds none of them anywhere.
- improvements/f3-evidence/ holds exactly the 14 files clone2 lists (arm_a.py, arm_b.py, arm_d.py, arm_e.py, bidi-tabs-225805-redacted.json, bidi-tabs-231520.json, cleanup_full.py, close3.py, full.log, parse_sessionstore.py, probe_session.py, rclick.py, result_full.json, verify_list.py).
- Cited lines in improvements/worker-f3b-restart-log.md read verbatim as the reports say: line 55 STEP 3 relaunch attempt 1 (relaunch-f3b.log); lines 64-65 Arm A run 3 and VERDICT PASS (arm_a_run2.log + probe_a2.log, session 0979bcf5); lines 66-67 Arm B launched and VERDICT PASS (arm_b_run.log + probe_b.log, session 29183d85); line 72 Arm C VERDICT PASS (probe_c.log); lines 73-74 Arm D launched and attempt 1 FAILED (arm_d_run.log + probe_d.log); lines 75-76 Arm D attempt 2 and VERDICT PASS (arm_d_run2.log + probe_d2.log, session 2d3cd2de); line 77 Arm E launched and line 79 Arm E VERDICT FAIL, WEDGE REPRODUCED (arm_e_run.log + probe_e.log, session 6304b1d8); line 82 BiDi-close probe (probe_f.log); line 85 restart #3 probe (probe_r3.log).
- None of the four arm session IDs (0979bcf5, 29183d85, 2d3cd2de, 6304b1d8) appears in full.log (59 lines) or result_full.json (0 hits each). Those two files do not corroborate the arms.
- The "14, not 9" correction is RIGHT. The 5 extra logs (arm_d_run.log, probe_d.log, probe_f.log, probe_r3.log, relaunch-f3b.log) are cited at lines 55, 73-74, 82, 85 and are all absent. The audit's V2 count of 9 was short; clone2's 14 is correct.
- The V2 correction entry (tail of worker-f3b-restart-log.md) lists all 14 logs, states the verdicts rest on the inline summary only, and names full.log and result_full.json as non-corroborating. It also carries the redteam follow-up note that relaunch-f3b.log is cited at STEP 3 (line 55), not STEP 4/5; that note was added by commit 177c85a, after the four fix commits.

Wording looseness (no verdict change): clone1's report says "lines 77 and 79 Arm E verdict FAIL". Line 77 is the Arm E launch row; line 79 is the VERDICT row. Substance is right.

Still missing (UNFIXABLE FROM HERE): all 14 run/probe logs. Full fix needs the 14 logs from the laptop where the arms ran, committed under improvements/f3-evidence/, or a re-run of arms A-E with logs committed.

## V3 (HIGH): 130/130 judge verdict evidence missing. PARTIALLY FIXED, CONFIRMED.

Checks at da60024, all confirmed:
- The verdict line still reads at live-test-log.md line 991: "VERDICT: 130/130, 13/13 full passes. tc02 10/10 (3/3 byte-exact 50/50, SHA 8da1f562...); tc01-tc13 each 10/10. No zero gate fires on any case; no prohibited shortcut in any case. Stress (separate, not added): S1 5/5, S2 PASS, S3 15/15, S4 PASS (rerun, explicit stale refusal + recovery), S5 PASS (S5d, third attempt; S5/S5b/S5c failures all driver/environment causes, confirmed from stress.log)."
- Whole-branch filename search finds none of test-cases.md, test-scores.md, test-execution-report.md, typing-fix-multipage-report.md, stress.log, finish-record.json, start-readiness.json (0 each). The only filenames containing "judge" on the branch are improvements/worker-y8b-judge-b1-v2.2.md and improvements/worker-y8b-judge-void.md, unrelated.
- The 15 end-state.json files on the branch are all A1 pilot checker-selftest fixtures (tests/realistic/a1-pilot/checker-selftest/cases/T01..T16/end-state.json), not judge files. The judge's 14 state.json files are absent.
- SHA corroboration holds: scripts/plans/tc02-v1.json:9 records expected_sha256 8da1f5624c1b482bcdfae9d7c6883fdc52313dbe4120c2d1df2623ec5bcb9772. Trial entries in the live-test-log record the same SHA: line 836 (full hash), lines 938, 941, 2091 (short hash 8da1f562). That corroborates the sentence hash, not the judge's per-case scores.
- "16 JSON files" is consistent: 14 judge state.json + finish-record.json + start-readiness.json. The V3 correction entry says "14 judge state.json files" and names the other two separately.
- "test-scores.md (174 lines)" is the log's own citation, not an independent measurement: the line after the verdict reads "Full per-case evidence in test-scores.md (rewritten, 174 lines)." Both reports handle it correctly as a cited claim.
- The verdict section honestly lists WITHHELD items (pill/overlay visibility, cursor-glyph appearance, Worker N's offline claims not re-verified), as clone2's report says. That honesty does not substitute for the missing files.
- The V3 correction entry (live-test-log.md line 4231, end of file) states the verdict is UNVERIFIABLE from repo evidence and lists the missing files.

Still missing (UNFIXABLE FROM HERE): the 5 report files, stress.log, the 16 JSON files, and the 20 screenshots. Full fix needs those files from the laptop/VM where the judge ran, committed to the repo, or a re-run of the judge with evidence committed.

## Audit appendix: CORRECT

The "Fix status after batch 7" appendix in docs/clone1-evidence-audit-full-20261121.md (lines 431-458) records the fix commits (05ee34d, 16c4196, 748cc35, 219720c), the 14-vs-9 V2 correction with the 5 extra logs named, and the remaining gaps for all three HIGHs. Every statement in it matches the checks above. One precision note: it repeats clone1's "0 discrepancies found". My review finds the two minor counting items above (D1, tip-moved-twice) and the one new coverage gap (D2); none of them changes the PARTIALLY FIXED verdict for any violation.

## What I could not re-check

- "None exists on the clone2 VM" (all three violations, both reports). I have no access to clone2's VM from this machine. The claim is unverifiable here, not disproven.
- The V1 correction entry's statement that the redteam flagged this at opt-redteam-m-skeptic.md:58 (P-33) and opt-redteam-m-verdict.md:33,81 (AM-13): I confirmed P-33 exists at opt-redteam-m-skeptic.md:58 via the whole-branch grep (the line reads "P-33. ABSENT. The H3 acceptance record..."), and the method file line 131 states the AM-13 requirement. I did not read the full redteam verdict file lines 33 and 81.
- Whether the tip moved "twice" in the sense of two pushes between c19c227 and da60024: push counts are not visible in the log. By commit count it moved 36 times, not twice.

## Bottom line

- All three HIGH violations are PARTIALLY FIXED, exactly as clone2 reported and clone1 verified. The record in the repo is corrected at the cited sites; the underlying missing material is still missing in all three cases.
- The "14, not 9" V2 correction is right. The V1 five-place list is right for the exact citation string, but the H3 acceptance claim also stands uncorrected in two more worker logs (D2); appending correction entries there is the remaining small follow-up.
- Full fixes still need, per violation: V1, the coordinator re-recording the acceptance (AM-13); V2, the 14 logs or a re-run; V3, the files or a judge re-run. Nothing further is fixable from this machine.
