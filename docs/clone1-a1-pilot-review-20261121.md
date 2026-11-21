# INDEPENDENT REVIEW OF THE FROZEN A1 PILOT PLAN, 21/11/2026

Reviewer: clone1, batch 5 task 3. Review only, no live pilot run, no
change to the plan file itself. This review covers the FROZEN version
only, at freeze commit f31abcf on branch todolist-push. Every file
cited below was read from that commit with git show f31abcf:path.
The frozen file list is tests/realistic/a1-pilot/FREEZE.md at f31abcf.

## Scope and method

- Frozen plan: improvements/worker-a1-pilot-plan.md, 1072 lines.
- Frozen artifacts read from f31abcf: runbook.md (241 lines),
  run-log-schema.md (267 lines), check_run.py (472 lines),
  a1_manifest.py (94 lines), a1_unblind.py (283 lines),
  preflight-probe.md (182 lines), FREEZE.md (127 lines),
  checker-selftest build_matrix.py and run_matrix.py plus the T01-T16
  cases, tests/test_a1_preflight.py (171 lines), scripts/code_exec.py
  (880 lines), tests/realistic/fcc-k/test-01-spreadsheet-formula.md
  (81 lines), both fixtures, tests/realistic/live-run-u-20261121.jsonl
  and run-u-all-20261121.log, improvements/worker-a1-council-measurement-20261121.md.
- Freeze integrity checked first: all 12 sha256 hashes in FREEZE.md
  at f31abcf match the files at f31abcf (0 mismatches). CORRECTION
  (redteam, 21:15): the review first wrote 10, the file has 12. No frozen
  file changed after f31abcf; only the pilot log and the FREEZE.md
  hash line changed, in commit dce42ca, which adds the freeze hash
  and changes nothing else. The plan file at f31abcf is byte-identical
  to the plan at the todolist-push tip.
- Independent re-runs from the f31abcf files in /tmp (repo untouched):
  checker self-test matrix 17/17 passed (after running build_matrix.py
  first, see M12); Layer-1 preflight test 7/7 passed in 0.002s;
  unblinder crash paths reproduced on synthetic data (see B3).
- Prior reviews were read only to avoid duplicating settled points:
  Council 1, Council 2, Council 3 measurement, Redteam, and the
  independent checker review (commit 9cf6391). Every hole below was
  found by reading the frozen text and code myself, not copied from
  those reviews. Where a hole overlaps a prior finding, that is noted.

## Verdict

3 blockers, 13 major holes, 12 minor holes. The plan is thorough and
honest about its limits, and most of its numbers check out (see the
verified section). But the three blockers each break the pilot on a
plausible event: a Case B run that takes the plan's own estimated 40
minutes is declared dead at 30 minutes; any death, invalid run, or
incomplete run makes the frozen unblinder refuse to produce a verdict;
and the unblinder crashes outright on three reachable inputs. No live
arm should run until B1, B2, and B3 are fixed by amendment before run 1.

Counts: blocker 3, major 13, minor 12. Total 28 holes.

## What checked out (verified correct, not holes)

- Freeze intact: 10 of 10 FREEZE.md sha256 hashes match the files at
  f31abcf; the plan, runbook, schema, checker, manifest script,
  unblinder, preflight probe, and self-test matrix are all unchanged
  since the freeze.
- Fixture md5s match the frozen values exactly: pick4
  91b2f92945c167306a13ae32977a9bf3 (719 bytes), f01
  2b6eda97036af51510b7eefe6d36dd93.
- f01 spec: 26 numbered steps; step 23 is the wrong-formula diagnosis
  ("Read E7: it shows the text COUNT text instead of a number"); the
  six end-state cells E2=540000, E3=574000, E4=750000, E5=1864000,
  E6=621333, E7=3 match the checker exactly.
- Worker U scripted run: 71 f01 rows in live-run-u-20261121.jsonl,
  elapsed_ms sums to 2960.7 ms, and the RESULT line in
  run-u-all-20261121.log carries elapsed_ms 3604. The plan's three-way
  step counts (26 spec, 40+ low-level, 71 scripted) and the 3604 ms
  citation are exact.
- Layer-1 preflight: tests/test_a1_preflight.py re-run by me from the
  f31abcf files, 7/7 PASS in 0.002s (plan says 0.014s on its machine;
  same count, faster run).
- Checker self-test matrix: re-run by me from the f31abcf files,
  17/17 passed, and the regenerated expected outputs are byte-identical
  to the frozen ones (see M12 for the build-step caveat).
- Caps exist in code: scripts/code_exec.py has MAX_PROGRAM_CHARS 8192,
  MAX_API_CALLS 32, DEFAULT_WALL_SECONDS 30, matching the plan.
- Checker blinding: check_run.py contains 0 occurrences of the string
  "manifest"; stage1_verdict opens only end-state.json and verify.png.
- Council 3 citations verified: section 1.2 (Case A cannot confirm a
  30 percent win; Case B about 40 minutes hand-driven, extrapolated,
  not measured), section 1.3 (power table, joint true-30 power 25.3
  percent at sigma 0.5, 100,000 to 200,000 simulated trials, seed
  20261121), section 4.2 (frozen definitions), section 5.3 (freeze
  mechanism), section 6.4 (blinded checker). All match the plan's use.
- agy-q2 held-out pool: test-06 through test-10 specs and fixtures all
  exist at f31abcf; the 10/10 simulation is recorded in
  improvements/worker-q2-agy-log.md line 96 ("all 10 tests passed
  (10/10, summary: all simulated, allPassed: true)").
- Independent checker review findings F1, F2, F3 (commit 9cf6391)
  verified fixed in the frozen code: misclicks emits "none detected"
  at 0; vcr_service counts the final desktop observe in both
  verification and production; gap-before is measured from the
  previous metric line with framing lines skipped.
- Probe programs use only allowlisted API names (dom_start, windows,
  observe, act, dom_tabs, dom_observe, dom_act, dom_assert,
  assert_state, all in the code_exec.py allowlist), and the expected
  bad-ref error ("ref is not present in the bound snapshot; observe
  again", code_exec.py line 210) matches the probe doc's expected
  substring.

## BLOCKERS (fix before any live run)

### B1. The 30-minute executor-death rule kills legitimate Case B runs

- Claim: plan section 9c, event A, line 842: "A run with a start
  marker and no end marker within 30 minutes is declared DEAD by
  Muse." Runbook section 7 repeats it verbatim.
- Contradiction: plan section 4, line 260, sets the Case B run cap at
  60 minutes, and the plan's own cited source estimates a Case B run
  at about 40 minutes hand-driven (Council 3 measurement section 1.2,
  "about 40 min hand-driven per run, extrapolated from 70 scripted
  steps at about 35s per agent step, NOT measured"). A model-driven
  STEP run is likely slower than hand-driven, not faster.
- Consequence: a Case B run taking the estimated 40 minutes is
  declared DEAD at 30 minutes, voided, and replaced. The replacement
  run takes about 40 minutes too and is declared DEAD again. The
  second death pauses the pilot (plan section 9c, event A). The pilot
  cannot complete Case B under its own rules if runs take the
  estimated time.
- The rule keys on run start and run end markers only. The 15-minute
  progress markers (plan section 9c, event C, line 875: "one per run
  start, per program submission, per 15 min of wall") are a different
  stream and do not save a live run from the 30-minute declaration.
  Events A and C contradict each other on a live 45-minute run: not
  stalled under C, DEAD under A.
- What must change: rewrite the death declaration to key off the last
  progress marker of any kind (for example, no marker for 30 minutes),
  not off run start. State the Case B expected wall explicitly next to
  the rule so the contradiction is visible.

### B2. Every re-run path is incompatible with the frozen unblinder

- Claim: plan section 9c, event A, line 849: a dead run is replaced
  with "a new manifest entry appended by Muse (the hash is
  re-published)". Plan section 5A (line 781) and runbook section 6:
  an INVALID run is "re-run once"; an INCOMPLETE run is "re-run under
  a new run-id".
- Contradiction: the frozen unblinder a1_unblind.py requires the
  manifest to have exactly 12 lines (line 80: "if len(manifest) != 12"),
  run numbers exactly [1, 2, 3] per case-arm, and manifest run-ids to
  equal the run directories exactly. A replacement entry makes 13
  lines. A preserved dead run directory makes the dir set mismatch.
- Verified by running the frozen unblinder on synthetic data:
  13-line manifest exits 2 with "manifest has 13 lines, expected 12",
  "run numbers for pick4 STEP are [1, 1, 2, 3]", and a run-dir
  mismatch. A 12-line manifest plus a preserved dead run directory
  exits 2 with "only in runs ['deadbeef']". Both failure modes were
  reproduced, not assumed.
- Consequence: the first executor death, the first INVALID run, or
  the first INCOMPLETE run makes the pilot un-unblindable without
  editing the frozen unblinder (itself a freeze violation) or deleting
  the dead run's directory (violating the preservation rule that its
  partial evidence stays, marked DEAD).
- What must change: define replacement entries before run 1 (for
  example a "status": "dead" or "replacement" field, excluded from the
  12-count, the run-number check, and the dir-match check), and amend
  the unblinder to accept them. The amendment must land before run 1,
  not after the first death.

### B3. The frozen unblinder crashes on three reachable inputs

- All three were reproduced by running the frozen a1_unblind.py on
  synthetic run data in /tmp. Each exits 1 with an uncaught traceback
  and no verdict, instead of the outcome the plan promises.
- B3a. CODE wall UNMEASURED with complete think lines. Plan section 8
  promises that a gate metric UNMEASURED on any run makes the case
  INCONCLUSIVE. Instead, a1_unblind.py line 226 computes
  code_wall_med = median(code_walls) where code_walls contains the
  string "UNMEASURED" alongside numbers, and median() (line 41) calls
  sorted() on the mixed list. Reproduced: TypeError "'<' not
  supported between instances of 'int' and 'str'". Reachable because
  wall is UNMEASURED when ts is non-decreasing-violated or run_start
  or run_end is missing, while think_before_program lines still carry
  numeric ms values. The think block runs before the inconclusive
  check, so the promised INCONCLUSIVE verdict is unreachable for this
  input.
- B3b. Malformed first run-log line. a1_unblind.py line 125 opens the
  run log, line 128 parses the first line with no try/except.
  Reproduced:
  json.decoder.JSONDecodeError on "{not json" as line 1. The checker
  would have flagged the line as a problem (run FAIL with problems),
  but the unblinder crashes before computing any verdict.
- B3c. Missing run-log.jsonl. Same line 125, open() with no
  existence check. Reproduced: FileNotFoundError. Again the checker
  would have reported "missing run-log.jsonl" as a problem, but the
  unblinder crashes first.
- What must change: harden the unblinder before run 1 (guard the
  median inputs to numeric-only, tolerate unparseable or missing log
  files by treating the run as failed with problems, and re-run the
  smoke tests including these three inputs). This needs an amendment
  to a frozen file, so it must happen before run 1, not after the
  first bad log.

## MAJOR HOLES (fix before any live run, or record as accepted risk)

### M1. The held-out draw is sealed in an unmentioned sidecar file

- Claim: plan section 2, line 114: Muse "draws one task from the
  validated pool by a recorded random draw, seals it in the manifest".
  Freeze mechanism item 2, line 736: the manifest script writes "the
  12 run-ids plus the sealed held-out draw".
- Fact: a1_manifest.py line 78 draws the held-out task with
  rng.choice(pool), but line 83 writes it to a separate file,
  args.out + ".meta.json", together with the seed: meta = {"seed",
  "held_out_draw", "pool"}. The draw is NOT in the manifest file.
- Consequences: (a) the plan's custody rule (section 9b) covers the
  manifest only; the meta file has no custodian, no published hash,
  and no tamper check. (b) The unblinder never reads the meta file,
  so the draw's integrity is never verified at any point. (c) Anyone
  holding the seed can reconstruct the arm-start pattern, because the
  start assignment (lines 61-63) is drawn from rng seeded by it; the
  seed is as sensitive as the manifest for the arm mapping.
- What must change: put the draw inside the manifest file, or add the
  meta file to the custody rule with a published sha256 and an
  unblinder verification step. Do not leave a sealed value in a file
  the plan never names.

### M2. The frozen caps are not enforced by any script

- Claim: the plan freezes the program caps (8192 chars, Case A 1
  planned + 1 recovery, Case B 2 planned + 1 recovery) and the
  per-case run caps (Case A 15 min, Case B 60 min). The freeze list
  (plan lines 792-793) names them explicitly.
- Fact: check_run.py computes program_calls and program_chars but
  never compares them to any cap, and never compares wall_ms to the
  run caps. a1_unblind.py never reads program_calls or program_chars
  at all. A CODE run with 3 planned calls, a program over 8192 chars,
  or a run over its cap would silently count, provided the executor
  did not self-report it.
- Enforcement today is honor-system: the runbook tells the executor
  to STOP and report a design miss. A run that busts a cap and does
  not report it is indistinguishable from a clean run in every
  script output.
- What must change: add cap checks to the checker or the unblinder
  (amendment before run 1), or name the manual check, who does it,
  and what happens to a run that busts a cap (FAIL, INVALID, or
  flagged).

### M3. INVALID has no implementation in the verdict script

- Claim: plan section 5A and run-log-schema.md define INVALID with
  three causes (fixture or harness fault, executor violated the
  runbook, run evidence lost) and "re-run once" with the original
  preserved. The schema says a run whose fixture md5 differs from the
  frozen value is INVALID, not FAIL.
- Fact: a1_unblind.py never outputs INVALID and has no code path for
  it. A fixture md5 mismatch is flagged by check_run.py as a problem
  (line 408), which makes run_pass False through the join rule
  (Stage 1 pass AND no Stage 2 problems). The run then counts as a
  FAIL in the pass rate, dragging it down, instead of being excluded
  and re-run as the plan requires.
- What must change: implement INVALID handling in the unblinder
  (distinguish problem types that void a run from problems that fail
  it), or amend the plan to state that md5 mismatches count as FAIL.
  Either way the re-run path must also satisfy B2.

### M4. STEP total think is undefined in the frozen docs

- Claim: plan section 5, condition 4, lines 293 and 303: total
  composition think (CODE) must be less than "STEP median total think
  for that case". The rationale is that batching claims to cut think
  by cutting turns, so a wall win bought elsewhere must not pass.
- Fact: no frozen document defines STEP total think or how to compute
  it. The run-log schema lists per-run fields including "gap ms (wall
  minus summed service ms)" but never links it to condition 4. The
  only definition lives in a code comment in check_run.py line 348:
  gap_ms is "the STEP arm's total think proxy for GO condition 4".
- The proxy is biased in CODE's favor: gap_ms is wall minus service
  time, which includes model think AND idle, stalls, broker waits, and
  any unlogged time. CODE's composition think is a pure think measure
  (think_before_program lines only, finish think excluded). Comparing
  a pure think number against a think-plus-idle-plus-stall number
  makes condition 4 easier to pass, so the gate cannot detect a wall
  win bought elsewhere, which is its stated purpose.
- What must change: define STEP total think in section 5A (or state
  explicitly that gap_ms is the proxy, why the bias is acceptable,
  and what the flag threshold means). The definition must be frozen
  text, not a code comment.

### M5. Censored timeout walls are treated as exact values

- Claim: plan section 5A (Timeout): "A timed-out run wall is censored
  data: its true wall is greater than the kill-time wall, not equal to
  it. In the verdict table it is printed with a '>' flag."
- Fact: a1_unblind.py uses the kill-time wall as a point value in the
  dispersion rule and the robustness label, with no timeout handling.
  Dispersion (max minus min over median) is understated: a timeout run
  is always the cell max, so a computed dispersion below 0.5 can hide
  a true dispersion above 0.5. Robustness ("every CODE run wall at or
  below the STEP median") can wrongly PASS when a timeout CODE run's
  kill-time wall sits at or below the STEP median while its true wall
  is above it. Only the median-timeout case is handled (INCONCLUSIVE
  when the median itself is a timeout).
- What must change: exclude timeout runs from dispersion and
  robustness, or mark those labels UNMEASURED when a cell contains a
  timeout, or bound them using the cap. The '>' flag must exist in the
  computation, not only in the printed table.

### M6. The eight-evidence-items rule is unenforceable as written

- Claim: plan section 6, line 522: "All eight items are written into
  runs/<run-id>/ before the run is counted as complete. A run missing
  any item is not counted in n=3; it is recorded as INCOMPLETE and
  re-run under a new run-id."
- Contradiction: the plan and the runbook enumerate different eights.
  The plan counts setup.json contents as four items (git HEAD, relay
  head plus flags, broker-status SOLO proof, fixture md5s) plus run
  log, end-state dump, screenshot, and commands. The runbook section 6
  counts run log, end state, screenshot, commands, setup, setup log,
  "verify image", and progress markers, where "screenshot" and "verify
  image" are both verify.png, the same file counted twice, and
  verify_start/verify_end lines are not an item at all. There is no
  single canonical list, so "missing any of the eight" cannot be
  checked.
- Fact: no script checks most of the items. check_run.py reads only
  run-log.jsonl, end-state.json, verify.png, commands.txt, and
  setup.json (fixture md5 only). setup-log.jsonl, the broker-SOLO
  proof, the relay head and flags, and progress-marker presence are
  never read by any script. The between-run reset evidence (fresh
  session, storage cleared, fixture reloaded, desktop clean) and the
  SOLO/relay proofs are therefore unverified; a stale fixture state
  leaking between runs would be invisible to every script.
- What must change: write one canonical eight-item list in the plan,
  schema, and runbook, and add a checker or unblinder check for each
  item, including setup-log.jsonl and the SOLO/relay proofs.

### M7. The Stage 1 operator and verdict-commit path are undefined

- Claim: plan section 6: Stage 1 verdict files "are committed before
  unblinding". Section 9b names a "checker operator" as a role distinct
  from Muse, the executor, and the Stage 2 metrics runner.
- Fact: no frozen document names who runs Stage 1 per run, who commits
  the verdict files, to which branch, or when (after each run, or after
  all 12). The run directories live in /tmp/a1-pilot-20261121/ on the
  laptop (runbook section 0), and the commit path from there to the
  repo is undefined.
- Consequence: if verdicts are committed after each run, the executor
  (repo access except improvements/) can read prior runs' PASS/FAIL,
  violating the no-feedback rule (plan section 3, item (c): the
  executor must not know "the wall time, pass/fail, or any metric of
  any completed run"). If they are committed only after all 12 runs,
  that must be stated, with an owner.
- What must change: name the Stage 1 operator and the commit timing
  (after all 12 runs, by Muse or the independent checker operator,
  never the executor), and state where the sealed outputs live until
  then.

### M8. The checker-output seal has no mechanism

- Claim: plan section 6, line 496: checker outputs are sealed per run
  in runs/<run-id>/check-output-sealed.json, "which no human reads
  before unblinding", because Stage 2 output leaks the arm
  (program_calls above 0 implies CODE).
- Fact: check_run.py prints to stdout and writes no files at all. No
  frozen script writes check-output-sealed.json. The seal depends on
  the operator redirecting stdout to the file without reading it, a
  step no document describes. Unlike the manifest rule (section 9b),
  which states its honest limit plainly ("no technical seal can stop a
  determined same-user agent from reading a file"), the checker-output
  seal states no limit and no mechanism.
- What must change: a wrapper script that runs the checker and writes
  the sealed file without displaying it, plus the honest-limit note
  matching section 9b. The manual flag check (which needs log reads
  after Stage 2) must be sequenced so the seal is not broken by it.

### M9. A replacement executor breaks the single-executor control

- Claim: plan section 11, decision D3: ONE executor, because
  between-executor skill variance at n=3 is a larger confound than
  within-executor learning under alternation. Plan section 3: "ONE
  fresh executor agent runs both arms (same model, same harness)".
- Contradiction: plan section 9c, event A, allows a replacement
  executor after a death, briefed identically from the same runbook,
  and states this "does not void the pre-registration". A different
  executor reintroduces exactly the between-executor variance D3 was
  adopted to avoid, and the manifest hardcodes agent "one Codex (Luna
  6 Max) session" (a1_manifest.py line 61 region) with no field to
  record a replacement. Runs before and after a replacement are not
  comparable under the design's own reasoning, and nothing flags them.
- What must change: record executor identity per run in the manifest
  and the run log, and decide before run 1 what a replacement means
  for the verdict (flag the affected case INCONCLUSIVE, or restart the
  affected case with the new executor).

### M10. The manual flag conditions are unautomated and undefined

- Claim: plan section 5: a run is flagged if it contains session
  death and restart, broker contention, a stale-snapshot refusal, or
  "an extra verification act not in the runbook". Two or more flagged
  runs in one arm-case cell make the case INCONCLUSIVE.
- Fact: a1_unblind.py detects only session_deaths above 0, refusals
  above 0, or entries in an optional --flags file. Broker contention
  and extra verification acts have no detector, no operational
  definition, and no checklist. "Extra verification act" is undefined:
  the runbook's procedures include observes and asserts throughout,
  so distinguishing a verification act from a normal act requires
  judgment Muse must apply by reading all 12 logs, with no script and
  no criteria.
- What must change: define the check operationally (for example,
  assert or desktop-observe counts beyond the runbook's final
  verification phase, or a broker-status anomaly), or record it as a
  documented manual step with a written checklist and a named
  reviewer.

### M11. Probe 5 logs the wrong op category

- Claim: preflight-probe.md lines 158-159: for Probe 5 the executor
  logs "1 retry line (the re-issued click after the failed assert)".
  Line 181: the probe passes only if "the retry line" is present.
- Contradiction: plan section 5A, line 386, defines retry as repeating
  "the same action (same intent, same target) after a refusal or
  failure", and "op recovery otherwise". The failed action in Probe 5
  is a dom_act assert on #result; the corrective click targets the
  button, a different action on a different target. Per section 5A it
  is a recovery line, not a retry line.
- Consequence: the probe that validates the retry-logging procedure
  encodes a miscount. The gate total is unaffected (recovery equals
  retry lines plus recovery lines), but the per-category counts and the
  probe's pass criterion are wrong, and an executor trained by this
  probe will miscategorize the same pattern in live runs.
- What must change: correct Probe 5 to expect a recovery line (and
  rename it the recovery-logging probe), or amend section 5A. The fix
  must land before run 1, because Probe 5 runs at resume.

### M12. The checker self-test cannot be re-run as documented

- Claim: the pilot log and run_matrix.py docstring say "one command
  runs the whole matrix" (python3 run_matrix.py), and the plan section
  9 names the T1-T16 matrix as the checker trust gate.
- Fact: on a clean checkout of f31abcf, python3 run_matrix.py alone
  fails 3/17 passed. Stage 1 requires verify.png to exist and be
  non-empty, and the frozen tree contains 0 verify.png files under
  checker-selftest/cases/. The PNGs are generated by build_matrix.py
  (a minimal 1x1 PNG, line 28-29), which must run first. After running
  build_matrix.py, the matrix passes 17/17, and the regenerated
  expected outputs are byte-identical to the frozen ones, so the
  matrix itself is sound. The defect is the documented procedure, not
  the checker.
- What must change: document the build step (or commit the PNGs) by
  amendment. The trust gate must be re-runnable from the frozen commit
  by following the written instructions alone.

### M13. Executor repo access is honor-system, not enforced

- Claim: plan section 3, line 234: "The executor's repo access during
  runs excludes improvements/ (enforced by the spawn brief)."
- Fact: a spawn brief is an instruction, not enforcement. The executor
  runs on the laptop with filesystem and repo access. It could read
  the pilot plan, the design file, prior run reports, committed Stage 1
  verdicts, and completed runs' directories (which contain commands.txt
  with full program text, revealing the arm of each prior run). The only
  controls are the brief itself and a post-hoc transcript check.
- The plan states an honest limit for the manifest (section 9b: "no
  technical seal can stop a determined same-user agent from reading a
  file") but presents the improvements/ exclusion as enforced, which
  it is not.
- What must change: state the honest limit for executor access the same
  way section 9b does for the manifest, or technically restrict access
  (separate checkout without improvements/, read-only run dirs).

## MINOR HOLES

### m1. Plan says the runbook contains "no numbers"; it does

- Plan section 3, line 216: "The runbook contains the procedure for
  each arm and no numbers, no hypothesis, and no prior results." The
  runbook contains caps (8192 chars, 1+1 and 2+1 calls, 30s and 60s
  budgets, 15 and 60 minute run caps), task values (E5=1864000,
  E6=621333, E7=3), and fixture md5s. Runbook section 8 states it
  correctly: "no hypothesis, no GO bar, and no prior results".
- Fix: correct the plan sentence to match the runbook's wording.

### m2. FREEZE.md does not hash-list the self-test expected outputs

- The plan's frozen list says "the checker self-test matrix and its
  expected outputs" are frozen. FREEZE.md at f31abcf lists 10 files
  with sha256 (plan, runbook, schema, checker, preflight probe,
  manifest script, unblinder, build_matrix.py, run_matrix.py, f01
  spec) and no cases/ file. The expected outputs are pinned by the
  freeze commit itself, but not individually hashed, so a later change
  to one would not show as a FREEZE.md diff.
- Fix: list the cases/ files in FREEZE.md, or state that the freeze
  commit pins them.

### m3. The Case B split point is "preferred", not frozen

- Plan section 3: "Planned split points are frozen in the runbook
  before the first live run". Runbook section 5.3: "a single program
  covering all 26 steps is allowed and preferred if it fits the caps.
  If you split, split after step 17". "Preferred" is not frozen: the
  executor chooses 1 or 2 planned programs per run, adding
  uncontrolled variance to the CODE arm (program count affects think
  measurement and comparability across the 3 runs).
- Fix: freeze one choice (single program), or record the choice per
  run as a design variable.

### m4. Two ref-taking action types are never probed

- Layer-2 probes cover click, fill, set_value, assert. The
  interpreter's _validate_dom_actions (code_exec.py line 187) also
  allows ref-taking confirm_click and hover_click. If the executor's
  live program uses either, its preflight is unproven. The probe doc
  itself applies the same logic to set_value ("the executor's live
  program may use either, so both are probed") but not to
  confirm_click or hover_click.
- Fix: probe all ref-taking types, or forbid the unprobed ones in the
  runbook. Low risk, since the runbook template says click and fill.

### m5. Case order is fixed A-then-B, not randomized

- a1_manifest.py runs Case A pairs 1-3 first, then Case B pairs 1-3.
  The plan's freeze list calls the run order "stratified-randomized
  per pair", but only the start arm within each pair is randomized;
  the case order is fixed. Program-composition skill learned in Case A
  CODE runs transfers to Case B CODE runs more than STEP skill
  transfers to Case B STEP runs, a cross-case learning asymmetry the
  plan never discusses.
- Fix: state the fixed case order in the plan and note the transfer as
  a limitation. The per-case first-run reporting already mitigates it
  in analysis.

### m6. The fabrication rule has no operational definition

- Plan section 5A: a run that reaches the end state "by writing
  fixture internals directly" is FAIL by fabrication, "checked at
  unblinding by Muse, not by the checker". No frozen document defines
  what text in commands.txt counts as fabrication. The code-exec
  allowlist has no page-JS-eval op, so the feasible paths are narrow
  (for example desktop act() into a devtools console), but the check
  has no criteria.
- Fix: define the check (forbidden patterns, for example act() calls
  targeting a devtools console inside a program).

### m7. A missing fixture md5 is silently accepted

- check_run.py line 408 flags a fixture md5 MISMATCH as a problem,
  but if fixture_md5 is absent from setup.json, got is None and no
  problem is recorded. A run with no md5 recorded passes the check.
- Fix: flag a missing fixture_md5 as a problem, the same as a
  mismatch.

### m8. Mixed-shape end-state.json is silently judged as f01

- check_run.py stage1_verdict: if end-state.json contains both
  result_text and E5, the f01 branch runs and result_text is ignored.
  The runbook fixes the shapes, so this is unlikely, but the checker
  should flag a mixed shape instead of silently picking one.
- Fix: add a problem for end states matching both case shapes.

### m9. No INCONCLUSIVE-rate baseline under the plan's own noise model

- Council 3 section 1.2 models incidents at p=0.25 to 0.50 per run,
  each multiplying wall by about 7x. With 3 runs per cell, the
  dispersion rule ((max minus min) over median above 0.5) will likely
  trigger INCONCLUSIVE on at least one cell. The plan computes the GO
  probability for a true 30 percent effect (about 25 percent on both
  cases) but never states the expected INCONCLUSIVE rate, so the team
  has no baseline for judging whether an INCONCLUSIVE outcome means
  the pilot worked as designed or something went wrong.
- Fix: compute and state the expected INCONCLUSIVE rate, or record it
  as a known unknown.

### m10. Resume-time stall risks are unaddressed

- Runbook section 0.1 asserts "SSH to the laptop is already available
  to you" with no verification step. Section 0.3 requires Muse's reply
  before run 1 if the Chromium endpoint is not 127.0.0.1:9222, with no
  timeout or fallback, so a 9223 endpoint stalls run 1 on a reply.
  Run directories live in /tmp/a1-pilot-20261121/ on the laptop with no
  persistence plan across reboots (the VM lost /tmp repeatedly).
- Fix: verify SSH and the endpoint at resume with a record-and-proceed
  rule, and state where run evidence lives if the laptop reboots
  mid-pilot.

### m11. The manifest script prints the meta path on stderr

- a1_manifest.py docstring says it "prints ONLY the sha256 of the
  manifest file to stdout", but it also prints "meta: <path> (seed and
  held-out draw sealed there)" to stderr. Minor, since stderr goes to
  Muse, who holds the manifest anyway. Fix the docstring or drop the
  stderr line.

### m12. The held-out runner briefing has no extraction procedure

- Plan section 2: the held-out runner is "briefed with the task spec
  and the GO-arm procedure only, no pilot numbers, no plan reference".
  The runbook is one file containing both arm procedures, the caps,
  and the no-knowledge list (which names the GO bar's existence). No
  frozen document says how to brief the runner with only the GO-arm
  part.
- Fix: name the briefing artifact (an extract of the runbook's CODE
  section plus the task spec) and who prepares it.

## What this review does not cover

- No live pilot run was attempted. Layer-2 preflight probes, the live
  held-out pool validation, the resume preconditions, and the Zen
  transfer probe are all untested by this review and remain owed at
  resume.
- The executor (a Codex session on the laptop) and the broker were not
  available to this reviewer. Claims about SSH availability, the
  Chromium endpoint, and broker SOLO behavior are UNVERIFIED here.
- The Council 1, Council 2, Council 3, and Redteam position papers
  were read for context, not re-verified line by line. The plan's
  synthesis decisions D1-D21 were checked for internal consistency
  against the frozen text, not re-litigated on the merits, except
  where a decision contradicts the frozen code (B2, B3, M1, M4).

## Recommendation

Do not run any live arm until B1, B2, and B3 are fixed by amendment
before run 1. The major holes M1 through M13 should be fixed in the
same amendment round, or each recorded in the pilot log as an accepted
risk with a named owner. The minor holes can be fixed in the same
round at low cost. After the amendment, re-run the matrix (build then
run) and the unblinder smoke tests including the three B3 inputs, and
re-verify FREEZE.md hashes before issuing the resume order.

## Correction after council 2 (21:16, 21/11)

The "17/17" matrix numbers in this review are wrong. Council 2
found, and I verified: run_matrix.py hardcodes total = 17 (line
147, comment line 146 "15 regular cases + T11 + T12 = 17 checks"),
but the frozen tree has only 16 case dirs (T01 to T10, T11a, T11b,
T13, T14, T15, T16; there is no T12 dir). The script prints
17/17 while only 16 checks exist, so the nonexistent T12 counts
as a phantom pass. True figures: 16/16 with the build step,
2/16 without it (not 3/17). Both this review and the evidence
audit repeated the script's printed number. This is a defect in
the frozen checker self-test itself, on top of the M12 build-step
gap already reported: the matrix total must be derived from the
case dirs on disk, not hardcoded.
