# Independent verification of clone1's 13 evidence violations

- Verifier: batch 7 task 1, independent subagent. Did not write the audit or any audited file.
- Audit under test: docs/clone1-evidence-audit-full-20261121.md, commit 581736e, 01:45 22/11.
- Anchor tip: origin/todolist-push e4082ff, the tip the audit used.
- Current tip checked: origin/todolist-push c450f5d, 02:21 22/11. None of V1, V2, V3, V5, V6 changed between the two tips.
- Method: read-only git checks against the branch (git show, git ls-tree, git cat-file, git grep, git diff --numstat, blob hash comparison), plus one live reproduction of V6 in a throwaway worktree at e4082ff with a synthetic manifest. No audited file was edited. No browser.
- Date of verification: 2026-11-22, 02:21 to 02:40 +07.

## Result summary

All 13 violations UPHELD. 0 rejected. Severity counts match the audit: 3 HIGH, 5 MEDIUM, 5 LOW (V9 and V12 carry the audit's own LOW-MEDIUM label inside the LOW count).

| # | Severity | Verdict |
|---|----------|---------|
| V1 | HIGH | UPHELD |
| V2 | HIGH | UPHELD |
| V3 | HIGH | UPHELD |
| V4 | MEDIUM | UPHELD |
| V5 | MEDIUM | UPHELD |
| V6 | MEDIUM | UPHELD, reproduced live |
| V7 | MEDIUM | UPHELD |
| V8 | MEDIUM | UPHELD |
| V9 | LOW-MEDIUM | UPHELD |
| V10 | LOW | UPHELD |
| V11 | LOW | UPHELD |
| V12 | LOW-MEDIUM | UPHELD |
| V13 | LOW | UPHELD |

## V1 (HIGH): H3 gate acceptance rests on a file that is not in the repo. UPHELD

Claim: the H3 gate question is resolved because the Y13r2 proposal (5a2b69d NO VERDICT plus runner-quiet/ports check counts as the marker leg) was accepted per MEMORY.md 22:57.

Evidence, checked by me:
- `git cat-file -t origin/todolist-push:MEMORY.md` fails: path does not exist in the branch. The branch root listing has no MEMORY.md. Still absent at current tip c450f5d.
- The claim is present in all five places the audit cites, verified line by line: improvements/opt-council-m2-verdict.md:90 and :107, improvements/opt-crawl-src-20261121.md:148, improvements/optimal-fix-method-20261121.md:198, improvements/worker-f1-guardian-fix-log.md:862.
- A branch-wide grep for H3 acceptance citations finds no acceptance artifact other than MEMORY.md 22:57. The redteam already flagged this as P-33, M-1 and AM-13 (opt-redteam-m-skeptic.md:58, opt-redteam-m-verdict.md:33,81), and it is still unresolved at the tip.
- The audit's staleness note is also correct: redteam-M's "Y13g has zero observable output" was true when written and is stale at the tip (50 Y13g commits exist at the anchor e4082ff, 52 at the current tip c450f5d).

Verdict: UPHELD. A gate decision that unblocks a live run rests on a citation that cannot be checked from the repo.

## V2 (HIGH): F3 arm verdicts cite 9 run logs that do not exist. UPHELD

Claim: STEP 4 Arm A/B/C/D/E verdicts in improvements/worker-f3b-restart-log.md cite arm_a_run2.log, probe_a2.log, arm_b_run.log, probe_b.log, probe_c.log, arm_d_run2.log, probe_d2.log, arm_e_run.log, probe_e.log.

Evidence, checked by me:
- `git cat-file -t` fails for all 9 paths under improvements/f3-evidence/ at e4082ff.
- A whole-branch filename search (`git ls-tree -r --name-only` piped to grep for the 9 names) returns nothing at e4082ff and nothing at current tip c450f5d. The logs exist nowhere on the branch.
- improvements/f3-evidence/ holds exactly the 14 files the audit lists: arm_a.py, arm_b.py, arm_d.py, arm_e.py, bidi-tabs-225805-redacted.json, bidi-tabs-231520.json, cleanup_full.py, close3.py, full.log, parse_sessionstore.py, probe_session.py, rclick.py, result_full.json, verify_list.py.
- full.log is 59 lines and contains 0 mentions of arm_a, arm_b, arm_d or arm_e.
- The verdict rows themselves are present in the log with inline session IDs, handle counts and exit codes (Arm A PASS 23:35:31, Arm B PASS 23:36:16, Arm C PASS 23:38:24, Arm D PASS 23:41:01, Arm E FAIL, WEDGE REPRODUCED 23:42:12), so the inline summary is real, but the cited raw logs cannot be re-checked.

Verdict: UPHELD. The arm verdicts rest only on the inline summary in the log itself.

## V3 (HIGH): the 130/130 judge verdict's evidence files are not in the repo. UPHELD

Claim: improvements/live-test-log.md:991, "VERDICT: 130/130, 13/13 full passes. tc02 10/10 (3/3 byte-exact 50/50, SHA 8da1f562...); tc01-tc13 each 10/10."

Evidence, checked by me:
- The claim text is present at lines 985-991 as cited, including the evidence list: test-cases.md, test-scores.md (rewritten, 174 lines), typing-fix-multipage-report.md, test-execution-report.md, stress.log, 14 state.json files plus finish-record.json and start-readiness.json, 20 screenshots in /tmp/judge/, repo_head c9b96a7 in all 14 state.json.
- Whole-branch filename search at e4082ff: test-scores.md 0 hits, test-cases.md 0 hits, test-execution-report.md 0 hits, typing-fix-multipage-report.md 0 hits, stress.log 0 hits. Still 0 hits at current tip c450f5d.
- The cited commit c9b96a7 does exist (`git cat-file -t` returns commit). The cited content hash 8da1f562 is not a git object, which is expected for a file-content hash.
- Precision note on the audit's wording: a filename search for state.json does return 15 hits, but all 15 are tests/realistic/a1-pilot/checker-selftest/cases/T*/end-state.json, A1 pilot fixtures unrelated to the judge's tc01-tc13 trial state files. No finish-record.json or start-readiness.json exists anywhere on the branch. The audit's conclusion stands; its sentence "No state.json exists" is true only for the judge's files, not for every file ending in state.json.
- Mitigating factor confirmed: the section honestly lists WITHHELD items (pill/overlay visibility, cursor-glyph appearance, Worker N's offline claims not re-verified), so the judge did not overclaim scope.

Verdict: UPHELD. The verdict cannot be re-run or re-checked from the repo; only the inline summary survives.

## V4 (MEDIUM): det-finish test counts cite laptop-local logs only. UPHELD

Claim: improvements/det-finish-implementation.md:121, 130, 144, 149. "Ran 1359 tests, FAILED (failures=8, skipped=2)"; "Ran 87 tests, OK (11 det_finish + 76 mcp_bridge)"; final full suite "Ran 1350 tests, FAILED (failures=7, errors=1, skipped=2)".

Evidence, checked by me:
- All three claims are present at the cited lines, each citing a laptop log: /tmp/det-finish-baseline-tests.log, /tmp/det-finish-after-tests.log, /tmp/det-finish-worktree2-tests.log (the fourth cited log, /tmp/det-finish-final-tests.log, is explicitly marked INVALID in the doc itself because the shared checkout switched branches mid-run).
- No file matching det-finish*.log exists anywhere on the branch at e4082ff.
- The cited commit e01399d exists.
- Arithmetic is internally consistent as the audit says: 1339 baseline, +20 from 10 det_finish + 10 from another worker's file gives 1359 after the first pass, 1350 final in a clean worktree without the untracked files (+11 over baseline).

Verdict: UPHELD. The counts are consistent on paper, but the raw logs cannot be re-checked from the repo.

## V5 (MEDIUM): run_matrix.py still hardcodes total 17 with only 16 case dirs. UPHELD

Claim: tests/realistic/a1-pilot/checker-selftest/run_matrix.py:146-147, comment "15 regular cases + T11 (arm leak) + T12 (determinism) = 17 checks", line 147 `total = 17`.

Evidence, checked by me:
- Lines 146-147 read exactly as cited at e4082ff.
- Case dirs at e4082ff: T01 to T10, T11a, T11b, T13, T14, T15, T16, 16 dirs total. There is no T12 dir.
- Still true at current tip c450f5d: line 147 is still `total = 17`, still 16 case dirs.

Verdict: UPHELD. The script prints 17/17 while only 16 checks exist, so the nonexistent T12 counts as a phantom pass.

## V6 (MEDIUM): a1_unblind.py B3a crash is only partly fixed at the tip. UPHELD, reproduced live

Claim: in tests/realistic/a1-pilot/a1_unblind.py, the think lists are now isinstance-filtered (lines 216-219) and the dispersion, timeout-median and robustness blocks guard with isinstance (lines 181, 186, 195, 234), but line 226 `code_wall_med = median(code_walls)` sits inside the `if len(code_thinks) == 3 and len(step_gaps) == 3:` branch with no guard on code_walls, so the exact B3a scenario (CODE wall UNMEASURED, thinks numeric) still crashes with TypeError in median().

Evidence, checked by me:
- Code reading confirms every cited line: median() at line 41 is `s = sorted(values)` with no guard; the UNMEASURED wall is recorded in the inconclusive list at lines 177-178 but execution continues; lines 181, 186, 195, 234 all guard with isinstance; lines 216-219 filter thinks and gaps to int/float only; line 226 calls median(code_walls) inside the branch with no guard on code_walls.
- Live reproduction, stronger than the audit's code reading: I built a synthetic manifest in /tmp (12 lines, cases pick4/f01, arms CODE/STEP, run numbers [1, 2, 3] per case-arm, matching the loader's exact requirements) with run dirs, run-log.jsonl files and stage1/stage2 JSONs, where pick4 CODE run 1 has wall_ms "UNMEASURED" and numeric total_composition_think_ms, and all STEP runs have numeric gap_ms. I ran the script from a throwaway worktree at e4082ff. Result: Traceback ending at line 226 `code_wall_med = median(code_walls)`, line 42 `s = sorted(values)`, `TypeError: '<' not supported between instances of 'int' and 'str'`, exit code 1, no verdict printed. The worktree and synthetic files were removed afterwards.
- Still true at current tip c450f5d: line 226 is still the unguarded `code_wall_med = median(code_walls)`.

Verdict: UPHELD, and reproduced live. The B3a crash is still present at the tip.

## V7 (MEDIUM): Y12 "6/6 full suites 10/10" evidence is local-only. UPHELD

Claim: improvements/worker-y12-batch3-verify-log.md:44-68. 6/6 full suites 10/10 PASS, sequential x3 (walls 26929, 23378, 23051 ms) plus concurrent load x3 (walls 65998, 65702, 64939 ms). Mutation probes 11/12 matched.

Evidence, checked by me:
- The claim text is present at the cited lines, with the full command and all six walls as stated.
- All run logs are cited as /tmp/y12/runs/seq-1..3.log and load-a/b/c.log; the probe script is /tmp/y12/probe.py and the summary /tmp/y12-mutations/probe-summary.json. None is in the repo: the only file matching "y12" anywhere on the branch is the log itself.
- No batch3 results.json exists on todolist-push at e4082ff.
- The only batch3 results.json on origin/main is the Y10 run: started 2026-11-21T12:18:46Z, wall 25024 ms, 10/10. That wall matches none of Y12's six walls, so no Y12 run output survives in any branch.

Verdict: UPHELD. The command is re-runnable in principle, but the claimed outputs cannot be checked from the repo.

## V8 (MEDIUM): PR1 verify result JSON is local-only. UPHELD

Claim: improvements/worker-pr1-verify-log.md:32, 52. "python3 tests/realistic_clone2/run_all.py --out /tmp/pr1-verify-suite-results.json: exit 0. 10/10 PASS, total 1.5336s" and "Trial merge against current main 2c54e56 is clean (0 conflicts). Selftest reproduced by me (7/7, exit 0, both modes)."

Evidence, checked by me:
- Both claims are present at the cited lines, with the per-test times and the 1.5336s total as stated.
- The cited commit 2c54e56 exists.
- The result JSON lives at /tmp/pr1-verify-suite-results.json, a local path. The only file matching "pr1-verify" anywhere on the branch is the log itself. No pr1-verify result file exists on the branch.

Verdict: UPHELD. The 10/10 output cannot be re-checked from the repo.

## V9 (LOW-MEDIUM): worker-x misquotes the P run report (9/10 vs 9/20). UPHELD

Claim: improvements/worker-x-remaining-items-log.md:11. "Worker P: clone1 t01-t10 10/10 PASS live on Zen. Report tests/realistic/RUN-REPORT-20261121.md, commit b8db405. Final full run 9/10 in 59,111 ms, t06 passed 3/3 after settle fix."

Evidence, checked by me:
- The worker-x line reads exactly as cited.
- Commit b8db405 exists.
- The report (tests/realistic/RUN-REPORT-20261121.md, on the branch) says at line 19: "Final full run: 9/20 in 59,111 ms; t06 failed once on a popup settle flake, then passed 3/3 after the settle fix, so the true final tally is 10/10 clone1." The run covered 20 tests (10 clone1 + 10 fcc-k), 9 passed in-run.
- The report's "10/10 PASS" headline (line 14) is itself a post-fix tally, and the report discloses this in its own text, so the headline is qualified in the body but overstated as a bare number. The worker-x line misquotes the denominator (9/10 for 9/20) and repeats the headline without the qualifier.
- The 59,111 ms wall is consistent with the report.

Verdict: UPHELD. The misquote is real, though small: the underlying tally, once the disclosed re-run is counted, is 10/10.

## V10 (LOW): Y14b restage log misreads git diff --stat. UPHELD

Claim: improvements/worker-y14b-restage-log.md, Baseline section. The diff ed78e83..1d23532 touches ONLY t10-music-player/check.mjs "(+240/-37, 167 -> 353 lines)" and README.md "(+97)".

Evidence, checked by me:
- The log text reads exactly as cited.
- `git diff --numstat ed78e83 1d23532 -- tests/realistic/clone1-batch3/` returns: README.md 87 insertions / 10 deletions, check.mjs 213 insertions / 27 deletions. The log's 240 and 97 are the diffstat "changed lines" totals (213+27=240, 87+10=97), misread as insertions.
- Net lines confirmed: check.mjs is 167 lines at ed78e83 and 353 lines at 1d23532 (213-27=186, 167+186=353).
- Scope confirmed: the range touches 7 files overall, but exactly those 2 files inside the suite. The t01-t09 check.mjs files are byte-identical between the two commits, verified by git blob hash comparison per file (all 9 identical).
- Related Y14b claims verified correct: run_batch3.py is 2093 lines at commit 70061e2; commits b913d7d, c7199ee, 8888f22 all exist.
- Note on my own check: my first diff command used wrong directory names (t03-typing, t04-kanban, from the fcc-k set) and returned a misleading count. I re-ran it with the correct names (t03-video-call, t04-email-client, t05-file-manager, t06-calendar, t07-code-editor, t08-settings-panel, t09-multi-window) and with blob-hash comparison, which settles it.

Verdict: UPHELD. Only the insertion/deletion split is wrong; the scope claim and the net line counts are right.

## V11 (LOW): Y13g R2 verify staged ships and results are local-only. UPHELD

Claim: improvements/worker-y13g-r2-verify-report.md. "Verdict: FAIL (narrow, 2 defects, both in _check_entry_pyc). 277 of 280 checks pass." Running log improvements/worker-y13g-r2-verify-log.md, harnesses improvements/y13g-r2-verify/.

Evidence, checked by me:
- The report states the FAIL verdict and 277 of 280 checks pass, with the 2 defects both in _check_entry_pyc.
- The verify log (268 lines) states "280 checks across 10 batteries: 277 pass, 3 fail" and "VERDICT: FAIL, 277/280", so the numbers are internally consistent.
- The harnesses ARE committed under improvements/y13g-r2-verify/ (attack_a2.py, attack_a3.py, attack_a4_live.py, and others listed).
- The staged ships and result logs cited are at ~/workspace/y13g-r2-verify/ (ships/, results/, so-plants/, so-markers/, a5/, a5b/, a7-outside/), a local VM path not in the repo. The same local-only pattern holds for the R2 council probes (~/workspace/y13g-r2-council-1/probe_r2.py and similar); the council papers themselves are in-repo with md5 pins.

Verdict: UPHELD. The verdict is reproducible in principle from the committed harnesses, but the exact staged ships and results are not preserved.

## V12 (LOW-MEDIUM): cited this-repo commit 700144a does not resolve. UPHELD

Claim: improvements/live-test-log.md:2282, 2297. "VM computer-use-wayland clone state: on branch step3-stream-prep (700144a, ahead 1 / behind 1 vs origin/main); working tree clean; origin/main at 9ecc167".

Evidence, checked by me:
- The claim text is present at both cited lines.
- 700144a is not a valid object name after fetching all branches (`git cat-file -t 700144a` fails).
- No remote branch named step3-stream-prep, or matching "step3" or "stream", exists (`git branch -a` grep returns nothing).
- The cited origin/main commit 9ecc167 does exist.

Verdict: UPHELD. The 700144a citation is a this-repo commit that cannot be resolved from any fetched ref; it was presumably a local-only commit on the laptop that was never pushed.

## V13 (LOW): speed swarm report cites laptop /tmp sources (disclosed). UPHELD

Claim: improvements/speed-swarm-report.md, Sources list (line 7). The report cites laptop paths /tmp/speed-profile-20261118/pick1/summary-pick1.md, /tmp/speed-mask/mask-before-after.md, /tmp/speed-pick4-20261118/g1-reprobe/summary-g1-reprobe.md, /tmp/speed-pick4-20261118/g1-reprobe2/summary-g1r2.md and /tmp/speed-pick4-20261118/g1-sidebar/summary-g1-sidebar.md. None is in the repo.

Evidence, checked by me:
- All five paths appear in the Sources list at line 7, each labeled "laptop /tmp/...". A whole-branch filename search finds none of them (the similarly named improvements/summary-g1-sidebar.md and improvements/summary-pick1-landing.md are different files, not the cited /tmp summaries).
- The report discloses them as laptop paths and labels its verdicts PROVISIONAL (line 5: "Status: FINAL, PROVISIONAL verdicts (non-Astra)"; line 13: "all PROVISIONAL, non-Astra"), so this is disclosed local-only evidence, not hidden.
- The in-repo proto files it also cites all exist: speed-swarm-profile.md, speed-proto-pick1.md, speed-proto-pick2.md, speed-proto-pick3.md, speed-proto-pick4.md, speed-prior-art.md, speed-proto-pick2-rerun.md, speed-proto-pick4-summary.md, speed-proto-pick1-p34remeasure.md, speed-proto-pick4-baseline-browser.md.
- Arithmetic recomputed exactly from the numbers in the report: think 34.2s of 36.4s wall = 93.96 percent (report: 94 percent); P1-P4 wall 37.54s to 17.59s = -53.1 percent (report: -53 percent); think 35.41s to 15.43s = -56.4 percent (report: -56 percent); D1 core-loop think 99.2s vs 20.7s = +78.5s, +379.2 percent (report: +78.5s, +379 percent); image bytes 205,348 vs 39,930 = +414.3 percent (report: +414 percent).

Verdict: UPHELD, as a disclosed low-severity finding. The evidence is local-only but the report says so and labels its verdicts provisional.

## Notes on the audit itself

- The audit is accurate on all 13 violations. Two precision notes, neither of which changes any verdict:
  - V3: the audit's sentence "No state.json exists on the branch" is true for the judge's trial state files, but 15 A1 pilot end-state.json fixtures do exist under tests/realistic/a1-pilot/checker-selftest/cases/. They are unrelated to the judge's files.
  - V10: the audit's "t01-t09 check.mjs diff is 0 lines" is confirmed by blob-hash comparison; my first attempt at re-checking it used wrong directory names and I corrected it before concluding.
- V6 was verified more strongly than the audit did: the audit verified by code reading only; I reproduced the crash live with a synthetic B3a manifest (TypeError at line 226, exit 1, no verdict).
- Nothing in this verification changes the audit's census or its recommendations. The highest-priority items remain: an H3 acceptance artifact in the repo (V1), the missing raw evidence files (V2, V3, V4, V7, V8), the run_matrix.py total (V5), and finishing the a1_unblind.py B3a guard (V6).
