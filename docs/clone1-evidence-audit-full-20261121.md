# Full evidence audit of improvements/ on origin/todolist-push

- Branch: origin/todolist-push, tip e4082ff1d1c82dc8a46907d7939f6b098ae57502
- Date of audit: 2026-11-22 (work 01:40 to 02:30 +07)
- Auditor: batch 6 task 2, independent subagent (did not write any of the audited files)
- Method: read-only. Files read with `git show origin/todolist-push:path`,
  `git ls-tree`, `git grep`, `git cat-file -t`, `git log`, `git diff --numstat`.
  Never checked out the branch into a working tree. No repo code was run,
  imported, or applied. No browser. One early exec call was flagged by an
  execution-risk check; from then on all reads were plain text retrieval only.
- Scope: all 484 files under improvements/ at the tip (10,287,241 bytes).
  Claims in docs/, tests/, coord/ or on main are out of scope except where
  a todolist-push file cites them.

## Census (recomputed by me, wc -l and grep -c on git show output)

- Files under improvements/: 484. Total bytes: 10,287,241.
- Largest: improvements/live-test-log.md 1,058,871 bytes, 4229 lines.
- Claim-ish lines in improvements/*.md (git grep -c, per pattern):
  PASS 1428, "done" 603, "complet" 1146, "verified" 2479, "passed" 420,
  "10/10" 172 lines, "ALL PASS" 25, "all tests" 2.
- Strong-claim lines extracted (10/10, ALL PASS, gate green, APPROVE,
  BLOCK): 1011 lines, saved during the audit and triaged.
- Lines citing /tmp/ paths: 1664, in 227 files. Lines mentioning
  "laptop": 1675.
- Cited commit hashes (patterns `commit|HEAD|pushed|at|tip|merge` +
  hex 7-40): 390 unique. 363 resolve as commits in the local object
  store after fetching all branches. 27 do not resolve; classified below.

## Result summary

- Headline claims read in full with a verdict: 39.
- Numbers recomputed independently: 15, of which 13 exact and 2 wrong.
- Violations found: 13 numbered (V1-V13), plus the hash-classification note.
- Severity: 3 high, 5 medium, 5 low.
- The single biggest pattern is not fabrication of numbers (most numbers
  recompute exactly) but evidence that lives outside the repo: raw logs,
  screenshots, result JSONs and staged ships cited from /tmp or laptop
  paths that are not in the branch and cannot be re-run from the repo
  as written.

## V1 (HIGH): H3 gate acceptance rests on a file that is not in the repo

- Tip e4082ff, files:
  improvements/opt-council-m2-verdict.md:90 and :107,
  improvements/opt-crawl-src-20261121.md:148,
  improvements/optimal-fix-method-20261121.md:198,
  improvements/worker-f1-guardian-fix-log.md:862.
- Claim, repeated in all five places: the H3 gate question is resolved
  because the Y13r2 proposal (5a2b69d NO VERDICT plus runner-quiet/ports
  check counts as the marker leg) was "accepted per MEMORY.md 22:57".
- Check: MEMORY.md does not exist in origin/todolist-push
  (`git cat-file -t origin/todolist-push:MEMORY.md` fails; the branch
  root listing has no MEMORY.md). No council paper, log entry, or owner
  message is cited as the acceptance anywhere in the branch; every
  citation I found is MEMORY.md 22:57 alone.
- This was already flagged by redteam-M (P-33, M-1, AM-13) and is still
  unresolved at the tip. A gate decision that unblocks a live run has no
  acceptance artifact runnable or checkable from the repo.
- Related staleness note, not a violation: redteam-M's claim "Y13g has
  zero observable output: no log file, no commits matching Y13g"
  (opt-redteam-m-attack.md:108, opt-redteam-m-verdict.md:33,81) was TRUE
  when written (files added 16:06-16:07 UTC) because the first Y13g
  commit landed 16:19 UTC (4ad7b88). At the tip it is STALE: 50 Y13g
  commits and 20 worker-y13g files exist. Do not quote it as current.
  (CORRECTION after council 2, 03:12 22/11: the audit first wrote 51
  commits and 21 files; council 2 counts 50 and 20. The conclusion,
  that the redteam-M claim is stale, still holds.)

## V2 (HIGH): F3 arm verdicts cite 9 run logs that do not exist

- Tip e4082ff, file improvements/worker-f3b-restart-log.md, lines 65, 67, 72, 76, 79.
- Claims: STEP 4 Arm A VERDICT PASS (cites arm_a_run2.log +
  probe_a2.log), Arm B PASS (arm_b_run.log + probe_b.log), Arm C PASS
  (probe_c.log), Arm D PASS (arm_d_run2.log + probe_d2.log), Arm E
  FAIL, WEDGE REPRODUCED (arm_e_run.log + probe_e.log). The log gives
  session IDs, handle counts and exit codes inline for each arm.
- Check: none of the 9 cited log files exists on the branch
  (`git cat-file -t` fails for all 9). improvements/f3-evidence/ holds
  only 14 files: 4 arm .py scripts, 2 bidi-tabs JSONs, cleanup_full.py,
  close3.py, full.log, parse_sessionstore.py, probe_session.py,
  rclick.py, result_full.json, verify_list.py. full.log is 59 lines and
  contains 0 mentions of arm_a, arm_b, arm_d or arm_e. result_full.json
  is a before/after tab-list snapshot, not arm output.
- The arm verdicts therefore rest only on the inline summary in the log
  itself. The runs cannot be re-checked from the repo.

## V3 (HIGH): the 130/130 judge verdict's evidence files are not in the repo

- Tip e4082ff, file improvements/live-test-log.md:991.
- Claim: "VERDICT: 130/130, 13/13 full passes. tc02 10/10 (3/3
  byte-exact 50/50, SHA 8da1f562...); tc01-tc13 each 10/10."
- Evidence cited in the same section (lines 985-990): test-cases.md,
  test-scores.md ("rewritten, 174 lines"), typing-fix-multipage-report.md,
  test-execution-report.md, stress.log, 14 state.json files plus
  finish-record.json and start-readiness.json, 20 screenshots fetched to
  /tmp/judge/, re-hashed output/result files, repo_head c9b96a7 in all
  14 state.json.
- Check: test-scores.md, test-cases.md, test-execution-report.md,
  typing-fix-multipage-report.md and stress.log return 0 hits in a
  whole-branch filename search. None of the judge's 14 tc state.json
  files, nor finish-record.json or start-readiness.json, exists on the
  branch. (CORRECTION after council 2, 03:12 22/11: the audit first
  wrote "No state.json exists on the branch", which is wrong as a
  blanket sentence: 15 end-state.json files exist in the A1
  checker-selftest case dirs. None of them are the judge's tc files,
  so the verdict stands, but the sentence is narrowed here.) The cited
  commit c9b96a7 does exist, and the cited content hash 8da1f562 is
  not a git object (it is a file-content hash, which is expected), but
  the files it hashes are not in the repo either.
- The verdict cannot be re-run or re-checked from the repo. Mitigating:
  the section honestly lists WITHHELD items (pill/overlay visibility,
  cursor-glyph appearance, Worker N's offline claims not re-verified),
  so the judge did not overclaim scope; the missing piece is the
  underlying evidence files themselves.

## V4 (MEDIUM): det-finish test counts cite laptop-local logs only

- Tip e4082ff, file improvements/det-finish-implementation.md:121, 130,
  144, 149.
- Claims: "Ran 1359 tests, FAILED (failures=8, skipped=2)"; "Ran 87
  tests, OK (11 det_finish + 76 mcp_bridge)"; final full suite "Ran
  1350 tests, FAILED (failures=7, errors=1, skipped=2)".
- Evidence cited for each run: "/tmp/det-finish-baseline-tests.log on
  the laptop", "/tmp/det-finish-after-tests.log on the laptop",
  "/tmp/det-finish-worktree2-tests.log on the laptop",
  "/tmp/det-finish-final-tests.log". None of these logs is in the repo.
- Check: the cited commit e01399d exists. The arithmetic in the text
  (1359 baseline, +20 from 10 det_finish + 10 from another worker's
  file, 1350 final) is internally consistent, but the raw logs cannot
  be re-checked from the repo.

## V5 (MEDIUM): run_matrix.py still hardcodes total 17 with only 16 case dirs

- Tip e4082ff, files tests/realistic/a1-pilot/checker-selftest/run_matrix.py:146-147
  and the case directory tests/realistic/a1-pilot/checker-selftest/cases/.
- The script comment says "15 regular cases + T11 (arm leak) + T12
  (determinism) = 17 checks" and line 147 sets `total = 17`.
- Check: the frozen tree has 16 case dirs (T01 to T10, T11a, T11b, T13,
  T14, T15, T16). There is no T12 dir. The script prints 17/17 while
  only 16 checks exist, so the nonexistent T12 counts as a phantom pass.
  True figures: 16/16 with the build step, 2/16 without it.
- This was found in batch 5 (council 2) and is still open at this tip.
  Every "matrix 17/17" claim in the A1 review and the evidence audit
  repeats the script's printed number.

## V6 (MEDIUM): a1_unblind.py B3a crash is only partly fixed at the tip

- Tip e4082ff, file tests/realistic/a1-pilot/a1_unblind.py, lines 41, 216-226.
- Background (batch 5, B3a): a CODE run with wall UNMEASURED but complete
  think lines crashed the unblinder with TypeError in median() (mixed
  str/int), exit 1, no verdict.
- Check at the tip: the think lists are now isinstance-filtered (lines
  216-219: code_thinks and step_gaps keep only int/float), and the
  dispersion, timeout-median and robustness blocks all guard with
  isinstance (lines 181, 186, 195, 234). But line 226,
  `code_wall_med = median(code_walls)`, sits inside the
  `if len(code_thinks) == 3 and len(step_gaps) == 3:` branch with no
  guard on code_walls. In the exact B3a scenario (CODE wall UNMEASURED,
  thinks numeric) the branch is entered and `sorted()` on mixed str/int
  still raises TypeError, because median() itself (line 41) has no guard
  and the code does not return early after recording the UNMEASURED wall
  at line 177-178.
- Verified by code reading only. No execution was performed (read-only
  audit; running repo code is out of scope for this task).

## V7 (MEDIUM): Y12 "6/6 full suites 10/10" evidence is local-only

- Tip e4082ff, file improvements/worker-y12-batch3-verify-log.md:44-68.
- Claim: 6/6 full suites 10/10 PASS, sequential x3 (walls 26929, 23378,
  23051 ms) plus concurrent load x3 (walls 65998, 65702, 64939 ms).
  Command given in full. Mutation probes 11/12 matched.
- Check: all run logs are cited as /tmp/y12/runs/seq-1..3.log and
  load-a/b/c.log; the probe script is /tmp/y12/probe.py and the summary
  /tmp/y12-mutations/probe-summary.json. None is in the repo. The only
  batch3 results.json on main is the Y10 run (wall 25024 ms, started
  2026-11-21T12:18:46Z), which matches none of Y12's six walls, so no
  Y12 run output survives in any branch. The command is re-runnable in
  principle, but the claimed outputs cannot be checked from the repo.

## V8 (MEDIUM): PR1 verify result JSON is local-only

- Tip e4082ff, file improvements/worker-pr1-verify-log.md:32, 52.
- Claim: "python3 tests/realistic_clone2/run_all.py --out
  /tmp/pr1-verify-suite-results.json: exit 0. 10/10 PASS, total
  1.5336s" and "Trial merge against current main 2c54e56 is clean
  (0 conflicts). Selftest reproduced by me (7/7, exit 0, both modes)."
- Check: the cited commit 2c54e56 exists. The result JSON lives at
  /tmp/pr1-verify-suite-results.json (local path); no pr1-verify result
  file exists anywhere on the branch. The 10/10 output cannot be
  re-checked from the repo.

## V9 (LOW-MEDIUM): worker-x misquotes the P run report (9/10 vs 9/20)

- Tip e4082ff, file improvements/worker-x-remaining-items-log.md:11.
- Claim: "Worker P: clone1 t01-t10 10/10 PASS live on Zen. Report
  tests/realistic/RUN-REPORT-20261121.md, commit b8db405. Final full
  run 9/10 in 59,111 ms, t06 passed 3/3 after settle fix."
- Check: commit b8db405 exists. The report (tests/realistic/
  RUN-REPORT-20261121.md, on the branch) says "Final full run: 9/20
  in 59,111 ms", not 9/10: the run covered 20 tests (10 clone1 + 10
  fcc-k), 9 passed in-run (t06 failed once on a popup settle flake).
  The report's "10/10 PASS" headline is itself a post-fix tally (t06
  passed 3/3 on re-run); the report discloses this in its own text,
  so the headline is qualified in the body but overstated as a bare
  number. The worker-x line misquotes the denominator and repeats the
  headline without the qualifier.
- The 59,111 ms wall itself is consistent with the report.

## V10 (LOW): Y14b restage log misreads git diff --stat

- Tip e4082ff, file improvements/worker-y14b-restage-log.md, Baseline section.
- Claim: the diff ed78e83..1d23532 touches ONLY t10-music-player/
  check.mjs "(+240/-37, 167 -> 353 lines)" and README.md "(+97)".
- Check (`git diff --numstat ed78e83 1d23532 -- tests/realistic/clone1-batch3/`):
  check.mjs is 213 insertions / 27 deletions; README.md is 87
  insertions / 10 deletions. The log's 240 and 97 are the diffstat
  "changed lines" totals (213+27=240, 87+10=97), misread as insertions.
  The net is right: check.mjs 167 -> 353 lines (verified by wc -l at
  both commits; 213-27=186, 167+186=353). The scope claim is right:
  exactly those 2 files changed in the suite, and the t01-t09 check.mjs
  diff is 0 lines (byte-identical). Only the insertion/deletion split
  is wrong. Related Y14b claims verified correct: run_batch3.py 2093
  lines at commit 70061e2 (exists), b913d7d exists, c7199ee exists,
  8888f22 exists.

## V11 (LOW): Y13g R2 verify staged ships and results are local-only

- Tip e4082ff, file improvements/worker-y13g-r2-verify-report.md.
- Claim: "Verdict: FAIL (narrow, 2 defects, both in _check_entry_pyc).
  277 of 280 checks pass." Running log
  improvements/worker-y13g-r2-verify-log.md, harnesses
  improvements/y13g-r2-verify/.
- Check: the verify log (268 lines) states "280 checks across 10
  batteries: 277 pass, 3 fail" and "VERDICT: FAIL, 277/280", so the
  numbers are internally consistent, and the harnesses ARE committed.
  But the staged ships and result logs cited are at
  ~/workspace/y13g-r2-verify/ (ships/, results/, so-plants/,
  so-markers/, a5/, a5b/, a7-outside/), a local VM path not in the
  repo. The verdict is reproducible in principle from the committed
  harnesses, but the exact staged ships and results are not preserved.
  The same local-only pattern holds for the R2 council probes
  (~/workspace/y13g-r2-council-1/probe_r2.py etc.); the council papers
  themselves are in-repo with md5 pins.

## V12 (LOW-MEDIUM): cited this-repo commit 700144a does not resolve

- Tip e4082ff, file improvements/live-test-log.md:2282, 2297.
- Claim: "VM computer-use-wayland clone state: on branch
  step3-stream-prep (700144a, ahead 1 / behind 1 vs origin/main);
  working tree clean; origin/main at 9ecc167".
- Check: 700144a is not a valid object name after fetching all
  branches, and no remote branch named step3-stream-prep (or matching
  "step3"/"stream") exists. The cited origin/main commit 9ecc167 does
  exist. The 700144a citation is a this-repo commit that cannot be
  resolved from any fetched ref; it was presumably a local-only commit
  on the laptop that was never pushed.

## V13 (LOW): speed swarm report cites laptop /tmp sources (disclosed)

- Tip e4082ff, file improvements/speed-swarm-report.md, Sources list.
- The report cites laptop paths /tmp/speed-profile-20261118/pick1/
  summary-pick1.md, /tmp/speed-mask/mask-before-after.md,
  /tmp/speed-pick4-20261118/g1-reprobe/summary-g1-reprobe.md,
  /tmp/speed-pick4-20261118/g1-reprobe2/summary-g1r2.md and
  /tmp/speed-pick4-20261118/g1-sidebar/summary-g1-sidebar.md. None is
  in the repo. The report discloses them as laptop paths and labels its
  verdicts PROVISIONAL, so this is disclosed local-only evidence, not
  hidden. The in-repo proto files it also cites do exist.
- Arithmetic in the report recomputed exact: think 34.2s of 36.4s wall
  = 94 percent; P1-P4 wall 37.54s to 17.59s = -53 percent; think
  35.41s to 15.43s = -56 percent; D1 core-loop think 99.2s vs 20.7s
  = +78.5s, +379 percent; image bytes 205,348 vs 39,930 = +414 percent.

## Cited-commit-hash classification (all 390 checked)

- 363 resolve as commits in the local object store after fetching all
  branches. Two of those (84b88bb, 87cd34f) resolved only after the full
  fetch; they live on other branches.
- 27 do not resolve. Classification by reading each citation in context:
  - 1 genuine this-repo unresolvable commit: 700144a (V12).
  - About 20 external-repo commits, unverifiable from this repo but
    expected: hyprglass-1.1.1 03a57c4, CLI-Anything 34f5195 and 784fee3,
    Haze 30528aa and 355c03b35c2f94006c567a1e4f52f180218de148, aquamarine
    4c72cd4, Kyant0 eb4a0ea, samasante 4e7b769, ziuus 5841c24, MacShell
    a05e0dc and a4144b3, rust-anything a827562, liquidglass f5e1fb56 and
    88f681a, atx/wtype d71be3a7b3f93b534a2823fd68cabd7ac2a02359 and
    99e8e15. These are upstream citations, not this repo's evidence.
  - 6 false positives, not commit citations at all: Wayland socket
    signature 11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947, Unix timestamp
    1794947807, chat IDs 750c8dae and 8fb75ccd, filename components
    99f30ca (diff-99f30ca-03a57c4.txt), file-content SHA 5cb507b6
    (cu.py sha256 prefix) and pin hash 674441ea (profile_sha256, itself
    questioned in the council doc it appears in), placeholder c1a2b3c
    in a steps list.

## Claims that check out (sample, all verified by me)

- Key commits cited across the logs all exist: 5a2b69d, 72eb8ad, 915121d,
  2fee242, be88321, 6239298, b53a593, c16dd4e, dbaba59, 1fa25bb9, 9ecc167,
  1d23532, ed78e83, 30a72e5, f31abcf, beebe50, 6f20fb5, a82bb41, 695efea,
  2c54e56, 7f547c6, aa302f7, b8db405, 70061e2, b913d7d, c7199ee, 8888f22,
  2e595ed, 431b2a9, e01399d, c9b96a7.
- FREEZE.md at f31abcf holds 12 sha256 hashes (64-hex strings counted),
  matching the batch 5 correction (not 10).
- worker-a1-pilot-plan.md is 1072 lines at the tip (council 2's number).
- live-test-log.md is 4229 lines; PASS lines 113 (matches git grep -c).
- RUN-REPORT-FCCK-FIXED-20261121.md arithmetic exact: 10 per-test times
  sum to 28,613 ms; plus q04 re-run 4,118 ms = 32,731 ms; 383 steps, 0 failed.
- Y8b B1 evidence chain exact: out.log 59 lines, 59 `"ok": true`, 0
  `"ok": false`; plan md5 63415e9b6cd63dc2185ca23242180424 matches the
  judge's cited value; design md5 at 695efea e1909423ee987b355783f22c7d804494
  matches the judge-void citation; executor wall 20:06:45-20:15:27 = 522 s;
  coordinator wall 20:06:32-20:15:35 = 543 s.
- Y13g R2 verify numbers internally consistent: 280 checks, 277 pass, 3
  fail, verdict FAIL, in both the report and the 268-line verify log.
- Y13r2 re-review probe totals as stated in its log: A 8/8, B 36/38,
  C 10/10 twice, D 16/16, E 24/24.
- The fcc-k 10/10 vacuousness is caught by the workers themselves
  (worker-p-test-run-log.md:53, RUN-REPORT-20261121.md:86-91, worker-s-fcck-fix-log.md:13):
  the offline pass proved the fixtures' JS worked, not agent control.
  That self-correction is honest and is not a violation.
- Y9 prep claims check out: a82bb41 and b913d7d exist, SHIPPED-y9.md is
  on the branch, and the log honestly records PREP + SHIP COMPLETE with
  NO LIVE DRIVING YET (slot not free), not a done live run.

## Recomputed numbers (15)

| # | Claim | Recomputed | Verdict |
|---|-------|-----------|---------|
| 1 | FREEZE.md 12 sha256 hashes | 12 (64-hex strings) | exact |
| 2 | run_matrix total 17 | 16 case dirs, no T12 | WRONG (V5) |
| 3 | A1 plan 1072 lines | 1072 | exact |
| 4 | live-test-log 4229 lines | 4229 | exact |
| 5 | live-test-log PASS 113 lines | 113 | exact |
| 6 | FCCK fixed total 28,613 ms | sum of 10 times = 28,613 | exact |
| 7 | FCCK 28,613 + 4,118 = 32,731 | 32,731 | exact |
| 8 | Y8b out.log 59/59 ok:true | 59 true, 0 false | exact |
| 9 | Y8b plan md5 63415e9b... | 63415e9b6cd63dc2185ca23242180424 | exact |
| 10 | Design md5 at 695efea e1909423... | e1909423ee987b355783f22c7d804494 | exact |
| 11 | Y8b executor wall 522 s | 20:06:45 to 20:15:27 = 522 s | exact |
| 12 | Y8b coordinator wall 543 s | 20:06:32 to 20:15:35 = 543 s | exact |
| 13 | check.mjs 167 to 353 lines | 167, 353 | exact |
| 14 | Y14b diff split +240/-37, +97 | +213/-27, +87/+10 | WRONG split (V10) |
| 15 | Speed swarm percents 94, -53, -56, +379, +414 | 93.96, 53.1, 56.4, 379.2, 414.3 | exact |

## Out of scope / not checked

- improvements/worker-y10-batch3-fix-log.md (the "10/10 x7 runs" claim
  from batch 5 redteam) exists on disk on main but NOT on
  origin/todolist-push, so the x7-vs-x8 count could not be re-verified
  inside this audit's scope.
- The 695efea plan eval split (19 evals, 10 start with return, 9
  contain it later, 0 with none) was recomputed in batch 5 from the
  plan at 695efea; it is not re-derived here.
- External-repo commits (about 20, listed above) cannot be verified
  from this repo's object store; checking them would need the upstream
  repos.
- The "183 managed files, 11 preserved-history exceptions" sync claim
  (live-test-log.md:474) has no sync manifest in the repo and is
  unverifiable from the branch.
- No live re-runs were performed: this audit is evidence-against-record
  only. Anything whose only evidence is a local /tmp or laptop path is
  recorded as local-only, not re-run.

## Recommendations

1. Highest priority: put an H3 acceptance artifact in the repo (a council
   paper or log entry naming who accepted, when, and in what file), or
   stop citing MEMORY.md 22:57 as the acceptance. Until then the Y13 live
   run's gate rests on an uncheckable citation (V1).
2. Commit the missing raw evidence or stop citing it: the 9 F3 arm logs
   (V2), the 130/130 judge evidence files (V3), the det-finish logs
   (V4), the Y12 run logs and probe summary (V7), the PR1 result JSON
   (V8). If the files are gone (wiped /tmp), say so in the logs and
   downgrade the claims to "inline summary only, raw log lost".
3. Fix run_matrix.py total to derive from the case dirs on disk instead
   of hardcoding 17 (V5), and finish the a1_unblind.py B3a fix by
   guarding the line-226 wall median the same way the think medians are
   guarded (V6).
4. Adopt a rule going forward: no "done" claim lands without its raw
   evidence file committed in the same push (log, JSON, screenshot, or
   results file), never a /tmp or ~/workspace path alone. The workers
   already do this well in places (Y8b out.log + judge files, Y13g
   harnesses, FCCK report arithmetic); make it the default.
