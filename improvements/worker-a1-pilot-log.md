# Worker A1 pilot log - A1 narrow pilot (code-exec batching)

- Worker: A1 (Muse). Owner approved the W redesign proposal 2026-11-21
  18:17, follow it as Lauren Tan advises.
- Proposal: improvements/working-structure-redesign-20261121.md section 6,
  commit fb00973. Design: improvements/a1-code-exec-dom-design.md.
- Branch: todolist-push. No live arm has run. No speedup is claimed.

## Status

- Plan DRAFT written: improvements/worker-a1-pilot-plan.md (commit
  1399342). Thresholds proposed, frozen only after council + redteam
  debate and synthesis.
- Council + redteam spawned 2026-11-21 ~18:20: Council 1 performance,
  Council 2 structure, Council 3 measurement, Redteam. Each writes its
  own position paper and commits on todolist-push.

## Prep done (all committed in 1399342)

- Pick 4 fixture FROZEN into the repo:
  tests/realistic/a1-pilot/fixtures/pick4-fixture.html, md5
  91b2f92945c167306a13ae32977a9bf3, 719 bytes, byte-identical to the
  18/11 original. The laptop /tmp copy is gone (directory no longer
  exists after the 21/11 reboots); the VM copy at
  ~/workspace/speed-pick4-20261118/pick4-fixture.html is the survivor.
  Provenance in tests/realistic/a1-pilot/fixtures/README.md.
- f01 fixture verified in the repo:
  tests/realistic/fcc-k/fixtures/test-01-spreadsheet.html, md5
  2b6eda97036af51510b7eefe6d36dd93. Spec has 26 steps; the proposal's
  "70 scripted steps" is Worker U's scripted DOM run (71 steps logged
  in tests/realistic/live-run-u-20261121.jsonl, f01 PASS 3,604 ms).
  All three counts recorded in the plan.
- DOM API verified present in scripts/code_exec.py: dom_start,
  dom_tabs, dom_observe, dom_act, dom_assert. MAX_PROGRAM_CHARS 8192,
  DEFAULT_WALL_SECONDS 30.
- Layer-1 preflight (interpreter, FakeDomBackend, no browser):
  tests/test_a1_preflight.py, 7/7 PASS in 0.014s. Bad ref mid-list
  refused before any backend call, for click, fill, set_value,
  assert, plus first/last positions and a positive control. The
  existing suite had no mid-list test; this is the new coverage.
- Blinded checker, two stages: tests/realistic/a1-pilot/check_run.py.
  Stage 1 reads ONLY end-state.json + verify.png (no log read, no
  run number, no timestamps). Stage 2 (--metrics) reads the log only
  after Stage 1 verdicts lock. grep for "manifest" in check_run.py
  returns nothing. Self-test: known-good pick4 PASS (exit 0),
  known-bad f01 (E7=2) FAIL with the exact problem (exit 1), missing
  verify.png FAIL (exit 1). Stage 2 metrics recompute correctly
  (wall 11000ms, tool_calls 1, vcr 0.40 on the synthetic log).
- Runbook: tests/realistic/a1-pilot/runbook.md (executor brief, both
  arms, both cases, no-knowledge list, provenance evidence, death
  rule alignment).
- Run-log schema: tests/realistic/a1-pilot/run-log-schema.md
  (run_sequence, provenance.json, two-stage blinding note).
- Layer-2 preflight probe: tests/realistic/a1-pilot/preflight-probe.md
  (4 probes x 2 submits, live browser, runs at resume before run 1).
  Note: the code-exec language has NO try/except, so each probe is
  P1 (expected CodeExecError) + P2 (state dump, expect zero effects).

## Council + redteam verdicts (all landed)

- Council 2 structure: DONE (commit bf3b25b). Overall AMEND, not BLOCK.
  7 findings, all closable by writing.
- Council 1 performance: DONE (commit f2d64e7). Overall AMEND, 6 points.
- Council 3 measurement: DONE (improvements/worker-a1-council-measurement-20261121.md).
  AMEND on 7 points, BLOCK on the two-directory checker self-test.
- Redteam: DONE (commits c4743dd, 536c41e). 7 attacks KILL the design as
  written, all fixable. Top 3: off-clock authorship (A1), 30% bar
  unreachable on Case A (B1), recovery invisible inside programs (A5).
  Also: STEP Case B path unspecified (A4), checker arm leak (A6),
  held-out pool half undefined (H1), held-out selection after the
  verdict (H2).

## Synthesis (Worker A1, 2026-11-21, plan section 11, decisions D1-D21)

All four verdicts resolved in the frozen plan. Key resolutions:
- D1 Case A wall: feasibility gate only (Council 1 + Redteam B1/C4);
  Council 3 section 1.5 per-case wall gate superseded on this point.
  Deviates from the proposal "per case" bar, deliberately, with reason.
- D2 Run order: stratified per-pair randomization (2-1 per case, sealed
  in the manifest). Supersedes Council 1 counterbalance (confounds
  start-arm with case) and Council 2 STEP-first endorsement (backwards).
- D3 Executor: ONE (Council 1 + Council 2); Redteam A3 two-executor
  option rejected (skill variance is the larger confound at n=3).
  A3 minimum controls adopted (no improvements/ access, transcript check).
- D4 Off-clock authorship: no program text in the runbook; live
  composition inside the timed run; pre-session program text voids the run.
- D5 STEP Case B path frozen to DOM observe/act with the same refs as CODE.
- D6 Recovery: section 5A definitions adopted verbatim (Council 3 4.2);
  CODE programs log one act line per DOM action incl. in-program retries.
- D7 Wall ends at verified end state; finish think outside wall; think
  per program call; GO condition 4 (total CODE composition think below
  STEP median total think).
- D8 n=3 stays; 2-of-3, dispersion, flagged-run, INCONCLUSIVE rules
  adopted; robustness is a reporting label, not a gate. Redteam B2
  separate variance probe rejected as superseded (pilot STEP runs measure
  the spread; a separate probe would contaminate the executor).
- D9 Caps: Case A 1 planned + 1 recovery, Case B 2 planned + 1 recovery,
  split points frozen. Char check measured (see below).
- D10 Zen transfer probe mandatory between a Chromium GO and Exp1.
- D11 Unblinding by Muse, not Worker A1 (Council 2 9b + Redteam C1).
  A1's role after the freeze is evidence packager only.
- D12 Custody: Muse holds the only manifest copy outside the repo,
  sha256 published (Council 2 9b).
- D13 Death/stall merged rule (section 9c): session death one-restart
  (Council 3 5A); executor-liveness 30-min death declaration + second
  death pauses pilot (Council 2 9c); stall first flag kills the run
  (Redteam C3).
- D14 Checker self-test: T1-T16 matrix built (Council 3 BLOCK closed);
  verdict-critical cases ALSO validated against real runs at resume
  (Redteam C2); matrix reviewed by an INDEPENDENT worker (pending).
- D15 Held-out: pool is agy-q2 test-06..test-10 only (clone1-batch3
  t-series dropped as undefined); draw sealed before run 1; candidates
  live-validated first; both arms n=1 exploratory.
- D16 Preflight: stop-fix-reprobe, not automatic safety NO-GO (Redteam B4).
- D17 Citations corrected (3,604 ms to the run-u-all log; "18s vs 8.59s"
  deleted as UNVERIFIED; 21s labeled think; 87.8% labeled UNVERIFIED;
  f01 pinned by commit cbbb748 + md5).
- Timing note: Council 2 Finding 0 and Redteam A8/C6 (runbook, schema,
  checker "do not exist") were true at review time and are stale now:
  the artifacts were written and committed after the reviews began.

## Case B program-length preflight (measured 2026-11-21, no browser)

- Loop/table shape (one program, 18 values, chunks of 8 = 32 actions per
  dom_act, E7 branch, COUNTA fix, six asserts, final observe): 2,453
  chars, 70.1% headroom under 8192, about 18 of 32 API calls.
- Fully unrolled shape: 8,603 chars, 411 over the cap, about 31 of 32
  API calls. The cap is satisfiable only in a compact shape.
- No cap reversion (draft well under 2x8192). Draft text DELETED after
  measurement; only the counts are recorded in the plan (Redteam A1).
- Program wall budgets frozen: Case A 30s, Case B 60s.

## Checker self-test matrix T1-T16 (built 2026-11-21)

- tests/realistic/a1-pilot/checker-selftest/ (build_matrix.py +
  run_matrix.py + cases/ with frozen expected outputs).
- Result: 17/17 passed (one command: python3 run_matrix.py).
  Two matrix bugs found during the run were in MY expected files, not
  the checker (T09 early-return shape, T16 ts order); both fixed and
  re-verified. The checker correctly flagged the T16 ts problem.
- Checker changes (Council 3 item 11): metrics from whatever files
  exist (T5/T8 report metrics with FAIL); ts non-decreasing validation;
  zero tool_call lines with act lines flagged; program_submit framing
  excluded from metric input; vcr_service + silence_minutes renamed;
  observation cost split by (kind, image) with gap-before; think per
  call + total composition think; gap_ms + run_end_reason added;
  commands.txt char-count check; setup.json fixture md5 check.
- Independent checker review: SPAWNED (agent 834a5254), report pending
  at improvements/worker-a1-checker-review-20261121.md. The freeze
  commit waits for its verdict.

## Manifest + unblinding scripts (smoke-tested 2026-11-21)

- tests/realistic/a1-pilot/a1_manifest.py: 12 run-ids, stratified
  starts, sealed held-out draw, prints only the sha256. Smoke test:
  12 lines, run numbers 1-3 per case-arm, draw from the pool.
- tests/realistic/a1-pilot/a1_unblind.py: manifest verification, join,
  frozen GO bar evaluation (Case B 4 conditions + Case A feasibility +
  2-of-3 + dispersion + flagged + robustness label + INCONCLUSIVE).
  Smoke test on synthetic data: GO, NO-GO, and INCONCLUSIVE scenarios
  all correct with expected exit codes (0, 0, 3). Harness in /tmp
  (not committed).
- FREEZE.md written with per-file sha256 (to be re-verified at commit
  time) + the GO bar in full text. Freeze commit hash to be recorded
  after the commit lands.

## Independent checker review (2026-11-21, reviewer agent 834a5254)

- Verdict: FAIL (narrow, fixable). Report
  improvements/worker-a1-checker-review-20261121.md, commit 9cf6391
  on todolist-push. Reviewer is not Worker A1 and not the executor.
- Reviewer re-ran the matrix: 17/17 passed. Hand-recomputed T01 and
  T03 golden metrics line by line from the raw logs, cross-checked
  with a second independent implementation written from the spec
  text only (no import of the checker): all values matched
  expected-stage2.json exactly. Confirmed working-tree sha256 of
  every reviewed file matched FREEZE.md. Confirmed check_run.py has
  no "manifest" string and Stage 1 opens only end-state.json plus
  verify.png. Verified clean: recovery steps = retry + recovery
  lines; program_submit excluded from metric input except program
  caps; wall = run_end minus run_start; ts non-decreasing validated
  with wall UNMEASURED on violation; zero tool_call lines with act
  lines flagged; T05/T08 still report full metrics; T12 determinism
  by byte comparison; T11 diff (logs differ only in program_submit +
  think_before_program lines; Stage 2 differs only in the 4
  arm-revealing fields); unblinder join rule (pass = Stage 1 pass
  AND no Stage 2 problems).
- Three diagnostic findings, none on any gate metric. All fixed by
  Worker A1 before the freeze commit:
  F1 misclicks reported as numeric 0 (plan section 8 and schema
  section 5A require "none detected", never "0 misclicks"). Checker
  now emits misclick_lines (count) plus a misclicks field
  ("none detected" at 0, else the count); matrix expected files
  updated; unblinding script carries misclicks per run.
  F2 vcr_service doc conflict: checker summed production over ALL
  act+observe lines (plan section 8), schema metric 5 said "all
  other" (excluding the final desktop observe). Schema amended to
  the plan reading, final desktop observe counted in both
  verification and production. Numbers differ (T01 0.25 vs 0.30,
  T03 0.184 vs 0.212, T05 1.0 vs UNMEASURED, T06 0.333 vs 0.5).
  F3 gap-before wording: checker measures from the previous metric
  line (framing lines skipped); schema and plan said "the previous
  line". One clarifying sentence added to schema metric 4 and plan
  section 8 metric 4.
- After the fixes: matrix rebuilt and re-run 17/17 passed; Layer-1
  preflight 7/7 PASS; test_code_exec suite 53 tests OK; manifest +
  unblinding smoke tests all passed (GO, NO-GO, INCONCLUSIVE
  scenarios, exit codes 0, 0, 3). FREEZE.md hashes regenerated for
  the five changed files (plan, schema, check_run.py, a1_unblind.py,
  build_matrix.py); the other frozen files re-verified unchanged.
  Limits: synthetic dirs only; the real-run cross-check on Layer-2
  preflight probe directories is still owed at resume.

## Council 2 amendments applied so far

- Checker restructured to two stages (Stage 1 verdict from end state
  only, Stage 2 metrics after verdicts lock). "manifest" removed from
  check_run.py (grep returns nothing). Self-test re-run and passing.
- Runbook: provenance.json evidence added (repo HEAD, relay head +
  flags, broker-SOLO proof, fixture md5s); no-knowledge list (a)-(f)
  added as section 8; 30-min rule aligned with the death rule.
- Schema: run_sequence in run_start detail; provenance.json section;
  blinding note rewritten for two stages.
- Still to apply at synthesis (plan text): sections 3 (executor +
  no-knowledge list), 6 (two-stage checker + evidence + independent
  re-run), 8 (run_sequence), 9 (replaced with checkable
  preconditions), new 9b (custody: Muse holds the only manifest copy
  outside the repo, sha256 published, unblinding by Muse), new 9c
  (death + restart rule). Plan stays DRAFT until all four debate
  reports land and contradictions are resolved.

## Resume preconditions (all must hold before any live arm)

Per Council 2 Finding 4 (to be frozen in the plan at synthesis):
frozen plan commit hash in this log; written timestamped resume order
from Muse naming the 12 run-ids; broker SOLO + idle; relay verified
(flags + HEAD); Layer-1 output committed (done, this log); Layer-2
probes pass at resume; fixture md5s re-verified; run dirs + sealed
manifest under custody 9b; checker self-test committed (done, this
log); runbook + schema + checker exist and committed (done, 1399342).

## Open items

- All debate verdicts landed; synthesis done (D1-D21); independent
  checker review done (FAIL narrow, 3 diagnostic findings, all
  fixed, matrix re-run 17/17). Freeze commit next, then resume
  preconditions (below) before any live arm.
- Executor selection: ONE fresh Codex (Luna 6 Max) session on the
  laptop, broker SOLO, briefed from the runbook only. Not launched
  until resume.
- Browser: managed Chromium via the code-exec DOM path (CDP), as D1
  did. NOT Zen (isolates the lever from Zen's open failure modes).
  Endpoint resolution (9222 vs the chromium-intel wrapper's 9223) is
  a resume-time pre-flight check, recorded in the setup log.
