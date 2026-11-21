# Batch 6 council 2: independent verification of the task 2 evidence audit

- Audit under review: docs/clone1-evidence-audit-full-20261121.md (378 lines),
  batch 6 task 2, tip e4082ff on origin/todolist-push.
- Council: batch 6 council 2, independent subagent (did not write the audit
  or any audited file).
- Method: read-only. Every check below was re-run by me from scratch with
  `git show e4082ff:path`, `git ls-tree`, `git cat-file -t`, `git diff
  --numstat`, `git grep`, `git branch -r`, `wc -l`. Never checked out the
  branch, never ran repo code. All line counts are `wc -l` on `git show`
  output, never newline count plus 1.
- Tip note: the audit was done at e4082ff. During my work the branch tip
  moved one commit forward to 167a2e9 ("Y13g R2 redteam: paper BLOCK").
  All my checks pin e4082ff, the audit's tip. At 167a2e9 the census is
  485 files / 10,308,922 bytes, not 484 / 10,287,241. That is tip movement,
  not an audit error.

## Verdict summary

- V1 HIGH: AGREE.
- V2 HIGH: AGREE.
- V3 HIGH: AGREE in substance, with one wrong sentence (correction C1).
- V4 MEDIUM: AGREE.
- V5 MEDIUM: AGREE.
- V6 MEDIUM: AGREE.
- V7 MEDIUM: AGREE.
- V8 MEDIUM: AGREE.
- V9 LOW-MEDIUM: AGREE.
- V10 LOW: AGREE.
- V11 LOW: AGREE (numbers re-verified; local-only paths checked in part).
- V12 LOW-MEDIUM: AGREE.
- V13 LOW: AGREE (arithmetic recomputed by hand, all exact).
- No violation was refuted. Two audit statements need correction (C1, C2),
  both minor and neither changes any verdict.

## V1 (HIGH): AGREE

- MEMORY.md does not exist on origin/todolist-push: `git cat-file -t
  origin/todolist-push:MEMORY.md` fails with "path does not exist", and
  the branch root listing has no MEMORY.md.
- All five citations verified at the exact lines the audit gives:
  - improvements/opt-council-m2-verdict.md:90: "the H3 gate question is
    resolved per MEMORY.md 22:57 (accepted Y13r2 proposal: 5a2b69d NO
    VERDICT plus runner-quiet/ports check counts as the marker leg...)".
  - Same file :107: "The H3 gate question is RESOLVED per MEMORY.md
    22:57 (accepted Y13r2 proposal...)".
  - improvements/opt-crawl-src-20261121.md:148: "H3 gate: Y13r2 proposal
    accepted (5a2b69d NO VERDICT + runner-quiet/ports check counts as
    the done marker leg...)".
  - improvements/optimal-fix-method-20261121.md:198: same acceptance
    wording.
  - improvements/worker-f1-guardian-fix-log.md:862-864: "H3 gate: accept
    Y13r2's proposal (5a2b69d NO VERDICT + runner-quiet/ports check is
    enough as the done marker leg...)".
- Extra observation from my own reading: the audited docs themselves flag
  the weakness. optimal-fix-method-20261121.md:131 says "Cite the H3
  acceptance in a council paper or log entry, not only MEMORY.md 22:57",
  and :198 repeats "G-10's H3 resolution must be cited in a council
  paper or log entry, not only MEMORY.md 22:57 (AM-13)". The audit's
  recommendation 1 is the same fix the docs already ask for.

## V2 (HIGH): AGREE

- All 9 cited logs do not exist on the branch. `git cat-file -t` fails
  for arm_a_run2.log, probe_a2.log, arm_b_run.log, probe_b.log,
  probe_c.log, arm_d_run2.log, probe_d2.log, arm_e_run.log, probe_e.log
  under improvements/f3-evidence/.
- improvements/f3-evidence/ holds exactly the 14 files the audit lists:
  4 arm .py scripts, 2 bidi-tabs JSONs, cleanup_full.py, close3.py,
  full.log, parse_sessionstore.py, probe_session.py, rclick.py,
  result_full.json, verify_list.py.
- full.log is 59 lines by wc -l and contains 0 mentions of arm_a, arm_b,
  arm_d or arm_e (grep -c).
- The five verdict lines match verbatim: worker-f3b-restart-log.md:65
  (Arm A PASS, arm_a_run2.log + probe_a2.log), :67 (Arm B PASS),
  :72 (Arm C PASS, probe_c.log), :76 (Arm D PASS), :79 (Arm E FAIL,
  WEDGE REPRODUCED, arm_e_run.log + probe_e.log). The inline session
  IDs, handle counts and exit codes are as the audit quotes them.

## V3 (HIGH): AGREE in substance, one wrong sentence (C1)

- live-test-log.md:985-991 verified verbatim: the judge section lists
  test-cases.md, test-scores.md, typing-fix-multipage-report.md,
  test-execution-report.md, 14 state.json + finish-record.json +
  start-readiness.json, stress.log, 20 screenshots in /tmp/judge/,
  repo_head c9b96a7, and the verdict "130/130, 13/13 full passes" at
  :991 with "SHA 8da1f562...".
- Whole-branch filename search at e4082ff: test-scores.md 0,
  test-cases.md 0, test-execution-report.md 0,
  typing-fix-multipage-report.md 0, stress.log 0.
- finish-record.json: 0 anywhere on the branch. start-readiness.json:
  0 anywhere on the branch.
- c9b96a7 resolves as a commit. 8da1f562 is not a git object ("Not a
  valid object name"), consistent with the audit's note that it is a
  file-content hash.
- CORRECTION C1: the audit's sentence "No state.json, finish-record.json
  or start-readiness.json exists on the branch" is wrong for state.json.
  At e4082ff there are 15 files matching state.json on the branch, all
  of them tests/realistic/a1-pilot/checker-selftest/cases/T*/end-state.json
  (T01-T10, T11a, T11b, T13, T14, T15, T16; 15 of the 16 case dirs have
  one). None of them is a judge tc state file, and no other state.json
  exists outside the checker-selftest cases. The verdict stands (the
  judge's 14 tc state files are not in the repo), but the sentence must
  be narrowed to "no judge tc state.json, finish-record.json or
  start-readiness.json exists on the branch".

## V4 (MEDIUM): AGREE

- det-finish-implementation.md:121 cites "/tmp/det-finish-baseline-tests.log
  on the laptop", :130 "/tmp/det-finish-after-tests.log on the laptop",
  :144 "/tmp/det-finish-worktree2-tests.log on the laptop", :149
  "/tmp/det-finish-final-tests.log". All four lines verified verbatim.
- 0 det-finish log files exist anywhere on the branch at e4082ff.

## V5 (MEDIUM): AGREE

- run_matrix.py:146 comment: "15 regular cases + T11 (arm leak) + T12
  (determinism) = 17 checks." Line 147: `total = 17`. Verified verbatim.
- Case dirs at e4082ff: 16 (T01-T10, T11a, T11b, T13, T14, T15, T16).
  No T12 dir. The script prints 17/17 while only 16 checks exist.

## V6 (MEDIUM): AGREE

- median() at a1_unblind.py:41-43 is `s = sorted(values); return
  s[len(s) // 2]`, no guard of any kind. Verified.
- Lines 216-219 filter code_thinks and step_gaps by isinstance
  (int, float). Lines 181, 186, 195, 234 guard with isinstance on
  code_walls / step_walls / walls. All verified verbatim.
- Line 226 `code_wall_med = median(code_walls)` sits inside the
  `if len(code_thinks) == 3 and len(step_gaps) == 3:` branch with no
  guard on code_walls. Lines 177-178 record the UNMEASURED wall in the
  inconclusive list but do not return early. In the exact B3a scenario
  (CODE wall UNMEASURED, thinks numeric) the branch is entered and
  sorted() on mixed str/int still raises TypeError. Code reading only,
  same as the audit; no execution performed.

## V7 (MEDIUM): AGREE

- worker-y12-batch3-verify-log.md:44-68 verified verbatim: 6/6 full
  suites 10/10, sequential walls 26929, 23378, 23051 ms, concurrent
  load walls 65998, 65702, 64939 ms, logs /tmp/y12/runs/seq-1..3.log
  and load-a/b/c.log, probe script /tmp/y12/probe.py, mutation probes
  11/12 matched.
- Not re-checked by me: the audit's sub-claim that the only batch3
  results.json on main is the Y10 run (wall 25024 ms). That is a
  main-branch check, out of the scope I re-ran.

## V8 (MEDIUM): AGREE

- worker-pr1-verify-log.md:32 verified verbatim: "python3
  tests/realistic_clone2/run_all.py --out
  /tmp/pr1-verify-suite-results.json: exit 0. 10/10 PASS, total
  1.5336s". Line :52 verified verbatim: trial merge against main
  2c54e56 clean, selftest 7/7.
- The only path on the branch matching "pr1-verify" is the log file
  itself (improvements/worker-pr1-verify-log.md). No result JSON
  exists anywhere on the branch. Commit 2c54e56 resolves.

## V9 (LOW-MEDIUM): AGREE

- worker-x-remaining-items-log.md:11 verified verbatim: "Final full
  run 9/10 in 59,111 ms, t06 passed 3/3 after settle fix."
- tests/realistic/RUN-REPORT-20261121.md:19 verified verbatim: "Final
  full run: 9/20 in 59,111 ms; t06 failed once on a popup settle...".
  The misquote is exactly as the audit states it. The 59,111 ms wall
  matches the report.

## V10 (LOW): AGREE

- `git diff --numstat ed78e83 1d23532 -- tests/realistic/clone1-batch3/`:
  README.md 87 insertions / 10 deletions, check.mjs 213 insertions /
  27 deletions. The audit's numbers are exact. The log's 240 and 97
  are the changed-line totals (213+27, 87+10), misread as insertions.
- check.mjs by wc -l: 167 lines at ed78e83, 353 at 1d23532. Net
  213-27=186, 167+186=353. Exact.
- Exactly 2 files changed in the suite diff. Exact.

## V11 (LOW): AGREE

- worker-y13g-r2-verify-log.md is 268 lines by wc -l. Line :234:
  "280 checks across 10 batteries: 277 pass, 3 fail". Line :266:
  "VERDICT: FAIL, 277/280, 2 defects". The internal consistency the
  audit cites is exact.
- I checked the numbers in the report and the log, but I did not
  re-list every ~/workspace/y13g-r2-verify/ local path the audit
  names. The local-only character of the staged ships and results is
  stated in the log itself, which I read.

## V12 (LOW-MEDIUM): AGREE

- 700144a does not resolve: `git cat-file -t 700144a` fails with "Not
  a valid object name".
- No remote branch matches step3 or stream: `git branch -r | grep -i
  -E "step3|stream"` returns nothing.
- The cited origin/main commit 9ecc167 resolves (verified in the hash
  spot checks).

## V13 (LOW): AGREE

- The five speed-swarm percentages recomputed by hand from the numbers
  in improvements/speed-swarm-report.md: 34.2/36.4 = 93.96 percent (94);
  (17.59-37.54)/37.54 = -53.1 percent (-53); (15.43-35.41)/35.41 =
  -56.4 percent (-56); 99.2-20.7 = 78.5s, 78.5/20.7 = 379.2 percent
  (+379); (205348-39930)/39930 = 414.3 percent (+414). All exact.
- The report labels its verdicts PROVISIONAL and cites the /tmp laptop
  paths as laptop paths, as the audit states.

## Numbers I recomputed independently (11)

| # | Claim | My recomputation | Verdict |
|---|-------|------------------|---------|
| 1 | 484 files under improvements/ at e4082ff | 484 (ls-tree, wc -l) | exact |
| 2 | 10,287,241 bytes at e4082ff | 10,287,241 (ls-tree -l sum) | exact |
| 3 | live-test-log.md 4229 lines, 1,058,871 bytes | 4229 (wc -l), 1058871 (cat-file -s) | exact |
| 4 | PASS lines in live-test-log.md 113 | 113 (grep -c PASS) | exact |
| 5 | /tmp/ lines in improvements/*.md 1664 | 1664 (git grep -c sum) | exact |
| 6 | FREEZE.md 12 sha256 at f31abcf | 12 (64-hex strings) | exact |
| 7 | A1 plan 1072 lines | 1072 (wc -l) | exact |
| 8 | FCCK 10 per-test times sum 28,613; +4,118 = 32,731 | 3604+3335+2540+2584+3539+2816+2563+2479+2393+2760 = 28613; 28613+4118 = 32731 | exact |
| 9 | Y8b out.log 59 lines, 59 ok true, 0 false | 59, 59, 0 (wc -l, grep -c) | exact |
| 10 | check.mjs 167 to 353; diff split 213/27, 87/10 | 167, 353, 213/27, 87/10 | exact |
| 11 | Y13g R2 verify log 268 lines, 277/280 | 268, 277 pass / 3 fail | exact |

## Audit arithmetic check

- 484 files: exact at e4082ff (see #1 above). Note the tip has since
  moved to 167a2e9 (485 files).
- 13 violations, 3 high / 5 medium / 5 low: V1-V13 are all present and
  numbered. The split holds if the two "LOW-MEDIUM" items (V9, V12)
  count as low. The label is ambiguous; see correction C4.
- 390 cited hashes (363 resolve, 27 do not): I did NOT reproduce the
  full 390 extraction, because the audit does not save the extraction
  command or list it was counted from, so there is nothing exact to
  re-run. The arithmetic 363+27=390 holds. Spot checks support the
  classification: 5 non-resolving hashes verified not to resolve
  (700144a, 03a57c4, 11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947,
  5cb507b6, c1a2b3c) and 9 resolving hashes verified to resolve
  (5a2b69d, c16dd4e, 1d23532, ed78e83, f31abcf, beebe50, 2c54e56,
  b8db405, c9b96a7).

## Corrections to the audit (mine, not the audited files)

- C1 (V3 sentence): "No state.json, finish-record.json or
  start-readiness.json exists on the branch" is wrong for state.json.
  15 end-state.json files exist at e4082ff in
  tests/realistic/a1-pilot/checker-selftest/cases/. Correct to: "no
  judge tc state.json, finish-record.json or start-readiness.json
  exists on the branch". The V3 verdict is unchanged.
- C2 (Y13g staleness note in V1): the audit says "51 Y13g commits and
  21 worker-y13g files exist". I count 50 commits with Y13g in the
  message (49 touching y13g paths) and 20 worker-y13g files
  branch-wide. Off by 1 on both. The conclusion (redteam-M's "zero
  observable output" claim is now stale) still holds by a wide margin.
- C3 (tip pinning): the audit's census is correct at e4082ff, but the
  branch has moved to 167a2e9. Any follow-up that re-runs these counts
  must re-pin the tip or the numbers will drift by one commit.
- C4 (severity labels): V9 and V12 are labeled "LOW-MEDIUM" while the
  summary counts 5 medium and 5 low. Pick one label per violation so
  the split is unambiguous.

## Not re-verified by me

- The full 390-hash extraction (no saved extraction list in the audit).
- The two Y8b md5 values (plan 63415e9b..., design e1909423...): both
  hashes are cited in the judge docs (worker-y8b-judge-b1-v2.2.md,
  worker-y8b-judge-void.md), but I did not locate the exact plan and
  design files to re-hash them, so I do not confirm or dispute them.
- V7's sub-claim that the only batch3 results.json on main is the Y10
  run (a main-branch check, not re-run here).
- V11's full list of local-only ~/workspace paths (numbers confirmed,
  paths checked in part only).
- The audit's census patterns PASS 1428 / "done" 603 / "complet" 1146 /
  "verified" 2479 / "10/10" 172 lines were not re-run; only the /tmp/
  census (1664) and the PASS count in live-test-log.md (113) were.

## Overall

The audit is sound. All 13 violations stand as written except for the
two wording corrections C1 and C2, neither of which changes a verdict.
The census numbers I re-ran (484 files, 10,287,241 bytes, 4229 lines,
1664 /tmp/ lines, 12 FREEZE hashes, 1072 plan lines, FCCK sums, Y8b
59/59) are all exact at the pinned tip e4082ff. The dominant pattern
the audit names, evidence living outside the repo in /tmp and laptop
paths, is confirmed independently in V2, V3, V4, V7 and V8. The audit's
recommendations 1-4 are the right fixes; recommendation 3 (derive the
run_matrix total from the case dirs, guard the line-226 wall median)
is confirmed necessary by my own code reading in V5 and V6.
