# Independent checker review, A1 narrow pilot (2026-11-21)

Reviewer: independent checker reviewer (not Worker A1, not the pilot executor).
Scope: `tests/realistic/a1-pilot/check_run.py`, the T1-T16 self-test matrix
(`checker-selftest/build_matrix.py`, `checker-selftest/run_matrix.py`),
`tests/realistic/a1-pilot/run-log-schema.md`, and plan
`improvements/worker-a1-pilot-plan.md` sections 5, 5A, 6, 8.
Method: ran the matrix myself, recomputed T01 and T03 by hand from the raw
log lines (plus a second independent implementation written from the spec
text only), read `check_run.py` line by line against the frozen spec, and
diffed the T11 pair myself. No frozen file was edited. No live browser arm
was run. No em dash or en dash in this file.

## Verdict: FAIL (narrow, fixable)

The checker is correct on every verdict-critical path I verified: Stage 1
blinding and pass/fail, wall time, recovery steps, composition think,
program caps, ts validation, missing-file handling, determinism, and the
T11 arm-leak test. The FAIL rests on three discrepancies, all in
diagnostic or reporting fields, none in any gate metric (wall, pass rate,
recovery steps, composition think). The most important one (F1) is a frozen
reporting rule that is implemented nowhere in the pipeline, and the matrix
cannot catch it because its expected files encode the same deviation.
Fix the three findings, update the matrix expected files, re-run the matrix,
re-freeze the hashes, then this review flips to PASS.

## 1. Matrix run (done by me)

Commands, from `tests/realistic/a1-pilot/checker-selftest`:

```
$ python3 build_matrix.py
built 16 cases under ~/workspace/computer-use-wayland/tests/realistic/a1-pilot/checker-selftest/cases
build exit: 0
$ python3 run_matrix.py
matrix: 17/17 passed
matrix exit: 0
```

16 case dirs built (T01-T10, T11a, T11b, T13-T16; T12 is determinism, not a
dir). 17 checks passed: 15 regular cases plus T11 (arm leak) plus T12
(determinism). Note the matrix compares parsed JSON dicts, so int/float
spelling differences (for example `3` vs `3.0` in Stage 1 `checked` values)
do not fail a case; that is exact under Python equality, not approximate
matching.

Freeze integrity: the working-tree sha256 of every frozen file I reviewed
matches `tests/realistic/a1-pilot/FREEZE.md` exactly (check_run.py
`ae655badff5e60a502006f14373d2e5ad2ae019941253de1bacf993b1e839d05`,
run-log-schema.md `bdef7155600f0b4f6d233732eb12932499ef1ad9dad633ea7aff4cf90f1f1893`,
plan `b5c495f3381de94df950cf602343c4b12b2afeff3ead88f22ac59e67eb708972`,
build_matrix.py `535d205e325808f8cc0de2a58110e960753f8c599fe05ab22d068a2fca6ad88a`,
run_matrix.py `1bff602173b740cd4af7c4380dc6a6ab2546efb9f26ebee1da433c4b8a2ba674`,
a1_unblind.py `f1bc248713bc1699b89fcac77ed02416b2554932ef4e583d9baebf460974c144`).
The `git diff` against HEAD is only because the freeze commit has not landed
yet; the files on disk are the frozen versions. This review covers exactly
those versions.

## 2. Hand recomputation, T01 and T03

I read each `run-log.jsonl` line by line and computed every metric by hand.
I then cross-checked with a second implementation written from the plan and
schema text only (`/tmp/indep_recompute.py`, times as ms since 10:00:00 by
string parsing, no import of `check_run.py`). Every number below matched
`expected-stage2.json` exactly. The arithmetic is shown so it can be
re-checked without running anything.

### T01 (known-good pick4, CODE-shaped, 14 lines)

- wall_ms: run_end 10:00:11.000 minus run_start 10:00:00.000 = 11000.
  Expected 11000. OK.
- tool_calls: tool_call lines at steps 1, 3, 5 = 3. Expected 3. OK.
- tokens_in / tokens_out: no tokens line, UNMEASURED both. OK.
- observation_service_cost_ms_by_type: two desktop/image observes.
  Step 2: elapsed 500, prev line tool_call 10:00:02.000, gap =
  (02.500 minus 02.000) minus 500 = 0. Step 11: elapsed 400, prev line
  verify_start 10:00:08.500, gap = (08.900 minus 08.500) minus 400 = 0.
  Service mean (500 + 400) / 2 = 450.0. Gap mean (0 + 0) / 2 = 0.0.
  Expected `desktop:image` {service_ms 450.0, gap_before_ms 0.0}. OK.
- vcr_service: verify = assert 200 + last desktop observe 400 = 600.
  Production (checker/plan reading, all act plus observe) = act 1200 + 300
  plus observe 500 + 400 = 2400. 600 / 2400 = 0.25. Expected 0.25. OK.
  (Schema-literal reading gives 0.30; see F2.)
- vcr_wall: verify phase 10:00:08.500 to 10:00:08.900 = 400 ms.
  Production wall = 11000 minus 400 = 10600. 400 / 10600 = 0.0377358,
  rounded to 3 decimals = 0.038. Expected 0.038. OK.
- silence_minutes: inter-line gaps in seconds are 2.0, 0.5, 1.5, 1.2, 1.8,
  1.0, 0, 0.3, 0.2, 0, 0.4, 0, 2.1. None exceeds 900 s. 0.0. OK.
- recovery_steps: retry lines 0 + recovery lines 0 = 0. OK.
- refusals 0, misclicks 0, session_deaths 0, retries 0. OK.
- program_calls: max calls_so_far over program_submit lines = 1.
  program_chars: sum of chars = 900. OK.
- think_per_call_ms: think_before_program detail.ms = [6000].
  total_composition_think_ms = 6000. OK.
- gap_ms: wall minus summed elapsed over all lines. Elapsed values sum to
  0 + 0 + 500 + 0 + 1200 + 0 + 0 + 0 + 300 + 200 + 0 + 400 + 0 + 0 = 2600.
  11000 minus 2600 = 8400. Expected 8400. OK.
- run_end_reason "done", case_task "pick4", run_id "a1b2c3d4",
  run_sequence 1, fixture md5 as frozen, problems [], notes []. OK.

### T03 (known-good f01, STEP-shaped, 14 lines)

- wall_ms: 10:01:00.000 minus 10:00:00.000 = 60000. Expected 60000. OK.
- tool_calls: tool_call lines at steps 1, 3, 5, 7 = 4. Expected 4. OK.
- observation_service_cost_ms_by_type: desktop/image observes 600 (gap 0:
  prev tool_call 10:00:03.000, 600 minus 600) and 500 (gap 0: prev
  verify_start 10:00:13.000, 500 minus 500), service mean
  (600 + 500) / 2 = 550.0, gap 0.0. dom/noimage observe 400 (gap 0: prev
  tool_call 10:00:09.000, 400 minus 400), service 400.0, gap 0.0.
  Expected `desktop:image` {550.0, 0.0} and `dom:noimage` {400.0, 0.0}. OK.
- vcr_service: verify = assert 200 + last desktop observe 500 = 700.
  Production (checker/plan reading) = act 1500 + 800 plus observe
  600 + 400 + 500 = 3800. 700 / 3800 = 0.184210, rounded = 0.184.
  Expected 0.184. OK. (Schema-literal reading gives 0.212; see F2.)
- vcr_wall: verify phase 10:00:13.000 to 10:00:13.500 = 500 ms.
  Production wall = 60000 minus 500 = 59500. 500 / 59500 = 0.008403,
  rounded = 0.008. Expected 0.008. OK.
- silence_minutes: gaps include a 46.5 s tail gap, none exceeds 900 s.
  0.0. OK.
- recovery_steps 0, refusals 0, misclicks 0, session_deaths 0, retries 0.
  OK.
- program_calls 0, program_chars 0, think_per_call_ms UNMEASURED,
  total_composition_think_ms UNMEASURED. OK.
- gap_ms: summed elapsed = 600 + 1500 + 400 + 800 + 200 + 500 = 4000.
  60000 minus 4000 = 56000. Expected 56000. OK.
- run_end_reason "done", case_task "f01", run_sequence 4. OK.

## 3. Spec conformance checks (plan sections 5, 5A, 6, 8)

- Stage 1 reads ONLY end-state.json plus verify.png: CONFIRMED BY READING
  THE CODE. `stage1_verdict` opens only `end-state.json` (line 92) and
  checks `verify.png` with `isfile`/`getsize` only (lines 81-88); it never
  opens it. The only other `open(` calls in the file are in Stage 2 code:
  run-log.jsonl (line 139), commands.txt (line 360), setup.json (line 399).
  Stage 1 never opens the log, the manifest, or any other file.
- No reference to "manifest" in check_run.py: CONFIRMED.
  `grep -n "manifest" tests/realistic/a1-pilot/check_run.py` returns
  nothing (exit 1). The matrix also checks this.
- recovery_steps equals retry lines plus recovery lines: CONFIRMED.
  Lines 422-424 count lines whose op is in ("recovery", "retry"). This
  matches plan section 5A exactly.
- program_submit lines excluded from metric input except for the program
  caps: CONFIRMED. `METRIC_EXCLUDED_OPS` (line 61) holds
  `program_submit` and `think_before_program`; `metric_lines` (lines
  206-214) keeps only `known_ops`, which excludes both; program_calls and
  program_chars are computed separately from the full line list.
  Note `think_before_program` is still used for the think metrics, which
  is its purpose, not a metric-input leak.
- wall uses run_end minus run_start: CONFIRMED. Lines 190-198 take the
  first run_start ts and the last run_end ts. First-start/last-end is the
  right choice if duplicate framing lines ever appear.
- ts non-decreasing is validated: CONFIRMED. Lines 175-189 flag the first
  offending line and set wall to UNMEASURED instead of producing a
  negative wall (T13 exercises this).
- Zero tool_call lines with act lines is flagged: CONFIRMED. Lines 228-233
  append the "tool_call lines missing" problem (T15 exercises this).
- Missing-file cases still report metrics where computable: CONFIRMED BY
  DIRECT RUNS. T05 (timeout, bad end state) Stage 2 reports wall_ms
  900000, tool_calls 1, vcr_service 1.0, vcr_wall UNMEASURED, gap_ms
  899500, problems []. T08 (missing end-state.json) Stage 2 reports the
  full T01 metrics (wall_ms 11000, vcr_service 0.25, gap_ms 8400,
  problems []). T07 (missing run-log.jsonl) Stage 2 correctly returns
  only the missing-log problem, which the plan allows.
- Exit codes: Stage 1 exits 0 on PASS (T01) and 1 on FAIL (T02); Stage 2
  exits 1 when problems exist (T07). The join verdict (Stage 1 pass AND
  Stage 2 with no problems) is enforced by `a1_unblind.py` line 136
  (`run_pass = bool(s1.get("pass")) and not s2.get("problems")`), which I
  read to confirm the checker output contract it relies on.
- Determinism (T12): CONFIRMED BY MY OWN RERUN. Two runs of the checker
  on T01 give byte-identical stdout for Stage 1 and for Stage 2
  (checked with `cmp`, not only through run_matrix.py).

## 4. T11 arm-leak test (verified by my own diff, not only run_matrix)

- The two logs differ ONLY in the two arm-revealing lines. My diff of the
  op sequences: T11a has `program_submit` and `think_before_program` at
  10:00:08.000; T11b drops exactly those two lines and renumbers
  step_index; every other op and ts is identical. end-state.json and
  setup.json are byte-identical between T11a and T11b. commands.txt
  differs only in that T11a carries the one program text and T11b is
  empty, which is inherent to the arm difference (a CODE run has program
  text, a STEP run has none) and the checker handles both with no problem.
- My own Stage 2 comparison: all fields identical except the four
  arm-revealing fields (program_calls 1 vs 0, program_chars 900 vs 0,
  think_per_call_ms [6000] vs UNMEASURED, total_composition_think_ms 6000
  vs UNMEASURED) and run_dir, which is just the directory path. Stage 1
  outputs are identical. The leak test genuinely tests what it claims.
  Note the two dropped lines share a ts (10:00:08.000) with their
  neighbours, so dropping them does not change silence gaps or gap_ms;
  that is why the arm-neutral metrics stay identical, and it is the
  correct design for this test.

## 5. Findings

### F1. Misclicks reported as numeric 0, but the frozen spec requires "none detected"

- Location: `check_run.py` lines 427-428, in `metrics.update`:
  `"misclicks": sum(1 for line in lines if line.get("op") == "misclick")`.
  With zero misclick lines this outputs `"misclicks": 0`. Every matrix
  expected file likewise contains `"misclicks": 0`, so the matrix cannot
  catch this; the checker and its expected files agree with each other
  and disagree with the frozen spec.
- What the spec requires: plan section 8, per-run list: "misclicks (none
  detected, never 0, until act lines carry target_ref and intended)".
  Schema section 5A, Misclick paragraph: "The checker counts misclick
  lines. A run with zero misclick lines is reported as 'none detected',
  never as '0 misclicks'." The reason is the stated limitation: a misclick
  the executor never detects is never logged, so 0 lines must not be
  presented as 0 misclicks.
- I checked whether the reporting rule is implemented downstream instead:
  it is not. `a1_unblind.py` never mentions misclicks at all (no match for
  "misclick" in the file), and no file under `tests/realistic/a1-pilot/`
  contains the string "none detected" except the plan and the schema.
  The rule is implemented nowhere in the pipeline.
- Correct behavior: the checker must not emit a bare numeric 0 for this
  field. Recommended fix (cleanest, keeps JSON numeric where a count is a
  true fact): rename the field to `misclick_lines` (a count of logged
  lines, which 0 describes truthfully) and have the verdict layer render
  0 as "none detected" in every human-facing report. Alternative: emit
  `"misclicks": "none detected"` when the count is 0. Either way, the
  matrix expected files must be updated to match, and the unblinder or
  verdict renderer must carry the "none detected" wording. Diagnostic
  field only; no gate metric is affected.

### F2. vcr_service: checker follows the plan, contradicts the schema (frozen-doc conflict)

- Location: `check_run.py` lines 286-287. `production_ms` sums elapsed_ms
  over ALL act plus observe lines, including the final desktop observe,
  which is also counted in the numerator (`verify_ms`, lines 282-285).
- What the plan requires (section 8, metric 5): "verification service
  time divided by production service time (assert elapsed plus last
  desktop observe, over act plus observe elapsed)". The checker matches
  this reading.
- What the schema requires (run-log-schema.md lines 108-110, metric 5):
  "Verification ops: assert lines + final desktop observe. Production
  ops: all other act/observe lines." "All other" excludes the final
  desktop observe from production. The checker does not do that.
- The numbers differ under the two readings. My independent recomputation:
  T01 0.25 (checker/plan) vs 0.30 (schema-literal); T03 0.184 vs 0.212;
  T05 1.0 vs UNMEASURED (schema-literal production would be 0, a division
  by zero); T06 0.333 vs 0.5. The matrix expected files follow the
  checker/plan reading, so the matrix passes either way; it cannot detect
  a doc conflict.
- Correct behavior: pick one definition and make all three agree. I
  recommend amending the schema to the plan reading (production is all act
  plus observe elapsed), since that is what the checker and the whole
  matrix already implement; changing the checker instead would require
  rebuilding every expected file. Either direction is acceptable as long
  as plan, schema, checker, and expected files all say the same thing.
  Diagnostic metric only; no gate metric is affected.

### F3. gap-before uses the previous metric line, the spec says the previous line

- Location: `check_run.py` lines 243-261. `prev_metric_ts` advances only
  over `metric_lines`, so framing lines (`program_submit`,
  `think_before_program`) are skipped when computing gap-before for an
  observe.
- What the spec requires: schema metric 4 and plan section 8 metric 4
  both say gap-before is the "mean of ts difference from the previous
  line minus elapsed_ms". The literal reading is the previous line in the
  file, framing lines included.
- Impact: nil on T01 and T03 (my independent recomputation used the
  literal previous-line reading and got identical gap values, because no
  observe follows a framing line in either golden case). The readings
  diverge in principle on a real CODE run, where a program's internal
  observe lines follow its `program_submit` line: the checker would span
  the gap from the earlier tool_call line, overstating think before that
  observe, while the literal reading would span from the submit ts.
  Neither reading is exactly "think plus idle" there, which is why this
  needs one clarifying sentence in the schema, not a silent choice.
- Correct behavior: amend the schema (and the plan wording if touched) to
  state explicitly whether gap-before is measured from the previous log
  line or the previous metric line, and keep the checker on the stated
  side. Diagnostic metric only; no gate metric is affected.

## 6. Minor notes (not findings, no action required before resume)

- gap-before values are clamped at zero (`max(gap_ms, 0)`, line 260). If a
  real run ever had an observe whose elapsed_ms exceeded the ts gap from
  the previous line, the checker would silently report 0 instead of
  flagging the inconsistency. The clamp never fires in the matrix. Worth
  a problem flag if it ever fires in a real run, but not a defect now.
- `gap_ms` sums elapsed_ms over ALL lines, including unknown ops, while
  unknown ops are otherwise "ignored for metrics". Unknown ops should not
  occur in real runs (the executor uses only known ops), so this is
  untestable in practice and not a defect.
- Stage 1 case inference: a state containing both `result_text` and `E5`
  is treated as f01 (the `elif "E5" in state` branch). No real run
  produces such a state; not a defect.
- Stage 1 `checked` values keep int type for int input (for example E7
  3, not 3.0) while the expected files write 3.0. Python dict equality
  treats them as equal, so the matrix passes; byte-level JSON diffs would
  show a difference. Cosmetic only.

## 7. Limits of what I verified

- Synthetic directories only. The matrix proves the checker handles its
  own synthetic edge cases; it does not prove the checker handles a real
  executor log. The real-run cross-check is still owed at resume: the
  checker run on the real Layer-2 preflight probe directories must
  produce the hand-verified PASS/FAIL (plan section 9, Redteam C2).
- I reviewed `check_run.py` and the matrix, and read `a1_unblind.py` only
  far enough to confirm the join rule and the absence of any misclick
  handling. The unblinder and the manifest script were not fully reviewed
  here.
- I did not review the runbook, the fixtures, or the executor procedure.
  The fixture md5 values in the checker match the frozen values, and the
  checker reports a mismatch as a problem, but I did not re-hash the
  fixture files themselves in this review.

## 8. Required fix path

1. Worker A1 amends: F1 (misclicks reporting), F2 (one-line schema
   clarification to the plan reading, or the checker plus all expected
   files to the schema reading), F3 (one clarifying sentence on gap-before).
2. Regenerate the matrix expected files with `build_matrix.py` and re-run
   `run_matrix.py` to 17/17.
3. Record the new freeze hashes in FREEZE.md (the freeze commit has not
   landed yet, so this is a pre-freeze amendment, not a post-freeze one).
4. This review flips to PASS once the amended checker plus matrix are
   re-verified; the verdict-critical paths already pass and need no
   re-review beyond the matrix re-run.

## Appendix: exact evidence

- Matrix: `python3 build_matrix.py` then `python3 run_matrix.py` in
  `tests/realistic/a1-pilot/checker-selftest`, output "built 16 cases"
  then "matrix: 17/17 passed", exit 0.
- Grep: `grep -n "manifest" tests/realistic/a1-pilot/check_run.py`
  returns nothing, exit 1.
- Grep: `grep -n "misclick" tests/realistic/a1-pilot/a1_unblind.py`
  returns nothing; `grep -rn "none detected" tests/realistic/a1-pilot/`
  matches only the plan and the schema.
- Hand recomputation: section 2 above, plus the independent second
  implementation at `/tmp/indep_recompute.py` (not committed; it imports
  nothing from the checker and parses ts by string arithmetic).
