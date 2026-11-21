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

## Council + redteam verdicts (arriving)

- Council 2 structure: DONE (commit bf3b25b). Overall AMEND, not BLOCK.
  7 findings, all closable by writing. Accepted in full (see below).
  It verified pick4 md5 matches and froze the f01 md5 above.
- Council 1 performance: PENDING.
- Council 3 measurement: PENDING.
- Redteam: PENDING.

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

- Council 1, Council 3, Redteam verdicts pending; synthesis after.
- Executor selection: ONE fresh Codex (Luna 6 Max) session on the
  laptop, broker SOLO, briefed from the runbook only. Not launched
  until resume.
- Browser: managed Chromium via the code-exec DOM path (CDP), as D1
  did. NOT Zen (isolates the lever from Zen's open failure modes).
  Endpoint resolution (9222 vs the chromium-intel wrapper's 9223) is
  a resume-time pre-flight check, recorded in the setup log.
