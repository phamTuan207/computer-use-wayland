# W-A1 pilot decision log: A1 pilot resume decision

- Owner: Pham Tuan. Worker: W-A1, for COORD-CLICK-6 (queue item 10).
- Branch: todolist-push. Repo: ~/workspace/computer-use-wayland.
- HEAD at task start: 05140c1 (05140c10d180ce7d26548df0f5b6f9c4d431e316).
  Verified before work: git ls-remote origin todolist-push returned
  05140c10d180ce7d26548df0f5b6f9c4d431e316, equal to local HEAD
  (checked 17:49:41 +07, 22/11/2026). A plain git pull --ff-only
  reported no such ref fetched, because the local tracking ref was
  already at the remote value; the ls-remote equality is the check
  that stands.
- Session: task received 17:49:23 +07, 22/11/2026. Dossier read in
  this session, no live arm run by W-A1 (see section 0.1).
- Rules honored: no em dash (U+2014) or en dash (U+2013) anywhere in
  this file. No personal info. No ydotool. Explicit pathspec commits
  only, never plain git commit, never git add -A. The file
  tests/realistic/clone1-batch3/results.json was not touched and is
  not part of this log.

## 0. Decision

DECISION: SUA ROI RESUME (fix then resume).

The A1 pilot runs, but only after the fix list in section 4 is closed
with evidence. No live arm starts before then. The frozen design
(freeze commit f31abcf, 21/11) stands unchanged: no threshold, case,
cap, fixture, run order, or checker change. Any change to those after
run 1 starts means a new pre-registered pilot, not an amendment.

Plain RESUME is false: 4 of the 9 resume preconditions are unmet on
the record (section 3). KILL is false: no measurement so far falsifies
the pilot premise, the executor blocks that gated the work are now
fixed, and the pilot asks a question no run so far answers (section 2).

## 0.1 Safeguard note: no fresh live re-measure by W-A1 in this session

An exec result in this session failed an execution-risk check, and
the safeguard that came with it forbids running, building, testing,
or loading the repo content and forbids git commands inside it until
an explicit go-ahead is given. W-A1 therefore paused all git, build,
and test actions and did the dossier work by plain file reading only.
Consequences, stated plainly:

- W-A1 ran NO fresh live re-measure in this session. Every number in
  section 1 below is a number measured by an independent worker and
  recorded in a committed log, cited here with its commit hash and
  its run time. The decision rests on that dossier evidence, not on
  a new W-A1 measurement.
- This log file is written but NOT committed and NOT pushed. Commit
  (explicit pathspec, one file) and push (verified by git ls-remote)
  are blocked until the go-ahead arrives. COORD-CLICK-6 decides
  whether to authorize the blocked actions or to accept the
  dossier-based decision as it stands.
- W-A1 did not re-run any test suite, did not re-verify any fixture
  checksum, and did not touch the laptop. The HEAD equality check
  above is the only git verification W-A1 performed, and it was done
  before the safeguard arrived.

## 1. Evidence (measured numbers only, each with source, commit, time)

### 1.1 A1 live run, 19/11: functional pass, speed bar FAIL

Source: improvements/summary-a1-live.md. Repo speed-swarm HEAD
f95807d, A1 DOM implementation 83f4224 in history. Verdict: FAIL
success bar, PROVISIONAL (non-Astra). Astra 6 out of credit.

| Task | Wall, start submit to verified | Baseline wall | Model calls | Refusals / misclicks / deaths |
|---|---:|---:|---:|---|
| D1 | 128.736s (14:08:10 to 14:10:19 +07) | about 82s | 4 | 0 / 0 / 0 |
| P1 | 30.769s (14:14:13 to 14:14:44 +07) | 18.89s | 2 | 0 / 0 / 0 |
| P2 | 19.387s (14:15:26 to 14:15:46 +07) | 10.18s | 2 | 0 / 0 / 0 |

Cause recorded in the same log: D1 attempt 1 returned IndexError
(list index out of range) after dom_start and windows, before any
desktop input, because browser_start returns once CDP answers while
the Wayland window maps later. The same program succeeded on retry.
Open items from that run: a readiness check between dom_start and
the window lookup, and the Pick 1 template missing P1/P2 blocks.
The brief states this speed bar FAIL was re-noted at 05:15 on
22/11. W-A1 could not locate a 05:15 entry in the files read; the
substance above is grounded in summary-a1-live.md, the 05:15 time
is taken from the brief as coordinator-supplied, not independently
re-verified (see section 6).

### 1.2 A1 re-measure, 19/11: PASS success bar, PROVISIONAL (non-Astra)

Source: improvements/summary-a1-remeasure.md. Worker Luna 6 Max.
Fix commit 52480e7 (api_dom_start polls windows until a chromium
window appears, bounded 10s at 0.2s), tests 2fbc732 (test_code_exec
47 to 50, all pass), templates 663be6f. Repo HEAD for the re-measure:
663be6f on branch speed-swarm.

| Task | Baseline wall | Code-exec wall | Baseline calls | Code-exec calls |
|---|---:|---:|---:|---|
| D1 | 107.068s | 58.340s (-48.7s, -46%) | 10 | 2 |
| P1 mean | 33.225s | 16.643s (-50%) | 5 | 2 |
| P2 mean | 35.364s | 16.567s (-53%) | 5 | 2 |

D1 passed on attempt 1 with no IndexError and no program retry, so
the race fix works live. Refusals, misclicks, session deaths: 0 / 0
/ 0 in both arms. Honest limits from the same log: n=1 for D1 per
arm, n=2 for P1/P2 per arm; think variance visible; no precise
speedup factor claimed, direction consistent across all 5 tasks and
both pairs. The code-exec walls still carry a post-result verify gap
(D1 49.427s of 55.960s think; P1/P2 9 to 14s), an asymmetry counted
against code-exec. The brief states this provisional PASS was
re-noted at 04:27 on 22/11. W-A1 could not locate a 04:27 entry in
the files read; the substance above is grounded in
summary-a1-remeasure.md, the 04:27 time is taken from the brief as
coordinator-supplied, not independently re-verified (see section 6).

### 1.3 Fixture 2-vision bench (PROBE-S2), 22/11 06:40 +07: PASS, gate (a) met

Source: improvements/worker-probe-s2-log.md, commit a1a672d
(2026-11-22 06:44 +07). Command: /tmp/probe-s2-venv/bin/python
tests/two_vision_bench.py --fixture --mode run --workdir
/home/hatch/probe-s2-work. Second attempt 06:40:30-06:40:41 +07,
EXIT 0, outer wall 11,305ms. results.json: run_id
bench-20261121T234030Z-86e8d8, mode run, live false, visions_used 2,
outcome PASS, wall_s 10.8596. Both sends V12-gated (clone1 0.6904s,
clone2 0.6807s). Same probe, 06:41 +07: the 3 Y1b real fails were
STILL OPEN then (1e chr NameError; 2a codemode wall preemption
absent, elapsed 7.20s; 2b code_exec wall preemption absent, elapsed
6.20s, ok=True with NO error, silent success). Gate (b) was NOT met
at that hour. That is now stale: see 1.4.

### 1.4 Step-1 closeout, 22/11 08:48-08:58 +07: Y1b blocks GONE, discover 0 failures

Source: improvements/worker-click4-step1-closeout-log.md, commit
4ac9320. HEAD at start 36364b1.

- Item-12 regression tests 4/4 PASS, run 08:49:39-08:49:40 +07, in
  0.008s (test_first_action.py TestRun, 4 tests). Whole file 71
  tests OK in 0.762s.
- Codex-lane item 12 LANDED via the resume run (07:27-07:48 +07,
  commits ee8ccb7, aa0fbbb, f4c0482, 06a34e8; git ls-remote origin
  amend4-codex 06a34e8610a9467c3884f6dd7a567293c747da45).
- Full discover at 36364b1, launched 08:50:43 +07, finished about
  08:54:54 +07: Ran 1974 tests in 248.397s, 0 failures, 4
  pre-existing errors, 17 skipped.
- Y1b 8 issues GONE at 36364b1: test_code_exec 55 plus test_codemode
  26, Ran 81 tests in 14.757s, OK. The Y1b executor fix
  (Y1B-RPC-LAND, ed2d559) plus TESTREPAIR-D (29083cd) closed all 8.
- CB-9 manifest for the bench build a1a672d NOT locked, and a
  retroactive manifest cannot be manufactured: the mechanism only
  landed in 18f2304 (S0-IMPL), after the bench ran at 06:40 +07,
  and the installed tree at bench time is gone. The bench pass
  (10.86s) must not be quoted as a gate until a manifest is locked
  (final direction section 4 precondition). This does not block the
  pilot, which generates its own evidence, but the bench number is
  cited here as a passed probe, not as a locked gate.

### 1.5 S2 one-class flip, 22/11 10:11-10:31 +07: DO NOT EXPAND (mechanism fault found)

Source: improvements/worker-click4-s2-flip-log.md. Wiring commit
350934a. Plateau definition (coordinator-set, HARD GATE): median
wall over 5 runs above 60s equals plateau reached.

| Run | Wall ms | Brave (fill) | Chromium (fill) |
|---:|---:|---|---|
| 1 | 33655.6 | sent | failed-unverified, CDP timeout Input.dispatchMouseEvent, 5003ms |
| 2 | 33953.2 | sent | failed-unverified, same sub-step, 5002ms |
| 3 | 33061.9 | sent | failed-unverified, same sub-step, 5003ms |
| 4 | 33121.8 | sent | failed-unverified, same sub-step, 5003ms |
| 5 | 33166.9 | sent | failed-unverified, same sub-step, 5003ms |

Median wall 33166.9ms (33.2s). Model calls 0 in all 5 runs.
Per-send 5/10 verified (Brave 5/5, Chromium 0/5). Per-run both
sends verified 0/5. Brave program elapsed 41-72ms, V12 attempt 1
all 5. Chromium program elapsed 5102.6-5106.3ms, all of it the
5000ms CDP timeout, V12 40 attempts never found. P9 reviewed both
sides every run, DOM and render agree. Rollback 10:34 +07: Brave
back to no-flag, PID 1003210, [::1]:9223 closed, machine as found.
Verdict in the log: DO NOT EXPAND. The plateau gate by the letter
was NOT reached (median 33.2s below 60s), but the class did not
complete, so the gate spirit was not met either: the failed runs
were fast only because they terminated early. Leading explanation
(not proven): the Chromium window sits on workspace 2 while
workspace 1 is active, and the occluded window input pipeline does
not dispatch synthetic mouse events. The worker did not switch
workspaces to test it mid-run.

### 1.6 S2 flip re-open, 22/11 13:05-13:09 +07: EXPAND (class now completes)

Source: improvements/worker-click5-s2-reopen-log.md, commit 1a3356d.
Harness split-variant commit d90d1b9 (wiring tests 12/12 pass).
Brave with FILL (unchanged, it already sent 5/5), Chromium with
(b1) set_value plus focus plus CDP key Enter (zero mouse events).

| Run | Time +07 | Wall ms | Brave | Chromium |
|---:|---|---|---|---|
| 1 | 13:05:09-13:05:57 | 29020.4 | sent, strict, completed 3, dom_act 51ms | sent, RELAXED 80 el trunc, completed 2, dom_act 12ms |
| 2 | 13:06:02-13:06:46 | 27799.1 | sent, strict, completed 3, dom_act 46ms | sent, RELAXED, completed 2, dom_act 9ms |
| 3 | 13:06:50-13:07:34 | 28112.6 | sent, strict, completed 3, dom_act 46ms | sent, RELAXED, completed 2, dom_act 9ms |
| 4 | 13:07:39-13:08:24 | 28898.1 | sent, strict, completed 3, dom_act 43ms | sent, RELAXED, completed 2, dom_act 8ms |
| 5 | 13:08:27-13:09:12 | 28560.9 | sent, strict, completed 3, dom_act 43ms | sent, RELAXED, completed 2, dom_act 10ms |

Median wall 28560.9ms (28.6s). Sorted: 27799.1, 28112.6, 28560.9,
28898.1, 29020.4. Per-send 10/10 verified (Brave 5/5, Chromium
5/5). Per-run both sends verified 5/5. V12 attempt 1 in all 10
sends. CB-1 all three True in all 10 sends. Model calls 0 in all
runs. Pre-send count 0 and delayed count exactly 1 in every
Chromium run: no double-send. P9 reviewed 10/10, DOM and render
agree every shot. Phase split, median: ssh transport 21942.2ms
(about 77 percent of the wall), broker 761.1ms, observe 2274.6ms,
act 245.4ms, verify 375.9ms, setup 227.3ms, residual 2750.1ms
(accounted for in the log, not a hole). Rollback 13:10:36-13:11:18
+07: Brave back to no-flag, PID 1119832, [::1]:9223 closed.
Verdict in the log: EXPAND. The plateau gate is met in letter and
spirit: median 28.6s below 60s AND the class completes 5/5. Caveats
in the same log: (1) the Chromium half ran under the DISCLOSED
relaxed routing gate in all 5 runs (truncated inventory, composer
covered); the 80-element snapshot cap keeps biting live threads;
(2) the mouse stall itself is UNSOLVED, (b1) routes around it for
this class only; (3) transport dominates the wall, further speed
gains for this class must come from transport (S0/S1), not the send
mechanism (about 0.25s of program time per run); (4) the durable
landing of the (b1) shape in cdp.mjs with tests is still open.

### 1.7 Final direction: A1, S3, CB-EXEC are ONE build

Source: improvements/worker-click3-final-direction-log.md, commit
e05fc58. A1 (Layer 0 driver daemon) is MODIFY, merged with S3 and
CB-EXEC into ONE build under the CB-EXEC contract, with ONE design
spec and ONE prototype. Gating: the contract is written at step 2;
a staged prototype must prove snapshot/execute/verify end to end
on one live ws2 clone chat plus held-out tasks before anything is
deleted (B6 lift). Step order 0-11: step 0 S0, step 1 AMEND4
close-out, step 2 contract, step 3 fixture 2-vision bench, step 4
fix 3 Y1b fails, step 5 P1 router plus P5 asserts, step 6 S2 flip
one task class, step 7 P2 element-ref, step 8 S1 broker, step 9
prototype semantic executor, step 10 delete A3/A4/A5, step 11
acceptance 3-rung (rung 1 fixture 2-vision, rung 2 live 0-vision
on real ws2 clone chats as the final gate for the chat class,
rung 3 100-task held-out benchmark). The A1 pilot is not a step
in that order; it is the parallel evidence track for the batching
lever that step 9 depends on. Its GO means proceed to the
confirmatory run, never adoption.

### 1.8 Freeze record: the design is frozen and reviewed

Source: tests/realistic/a1-pilot/FREEZE.md, freeze commit f31abcf
(2026-11-21). Frozen: amended plan, run-log schema, runbook,
check_run.py, checker self-test matrix and expected outputs,
fixtures (pick4 md5 91b2f92945c167306a13ae32977a9bf3, 719 bytes;
f01 md5 2b6eda97036af51510b7eefe6d36dd93, last changed cbbb748),
f01 spec, GO bar in full text, section 5A definitions, program caps
(8192 chars; Case A 1 planned plus 1 recovery; Case B 2 planned
plus 1 recovery), run caps (Case A 15 min, Case B 60 min), run
order (stratified-randomized per pair, sealed in the manifest),
invalidation rules, unblinding procedure. Verification at freeze:
checker matrix 17/17 passed; Layer-1 preflight
tests/test_a1_preflight.py 7/7 PASS (0.014s in the pilot log,
0.002s in FREEZE.md, both recorded, minor difference, not
load-bearing); test_code_exec suite 53 tests OK; manifest plus
unblinding smoke tests passed on synthetic data (GO, NO-GO,
INCONCLUSIVE, exit codes 0, 0, 3). Independent checker review:
FAIL narrow, fixable, report
improvements/worker-a1-checker-review-20261121.md, commit 9cf6391;
reviewer re-ran the matrix 17/17, hand-recomputed T01 and T03
golden metrics with a second independent implementation (all
values matched), confirmed working-tree sha256 matched FREEZE.md,
confirmed check_run.py has no "manifest" string and Stage 1 opens
only end-state.json plus verify.png. Three diagnostic findings
(F1 misclicks wording, F2 vcr_service doc conflict, F3 gap-before
wording), none on any gate metric, all fixed before the freeze
commit, matrix rebuilt and re-run 17/17. The real-run cross-check
on Layer-2 preflight probe directories is still owed at resume
(synthetic dirs only so far).

## 2. Why not KILL

- The pilot asks a question no run so far answers. The S2 flip and
  re-open used a FIXED program, written once before run 1 and reused
  unchanged, with 0 model calls. The pilot tests LIVE COMPOSITION:
  the executor composes each program fresh inside the timed run,
  including the Case B mid-task diagnosis branch (re-read E7, if
  text then replace COUNT with COUNTA, re-read), against the
  step-by-step loop on the same fixture, same browser, same task.
  The re-measure (1.2) is the only live-composition evidence, and
  it is n=1 for D1 and n=2 for P1/P2, provisional, non-Astra, with
  the verify-gap asymmetry. A KILL would discard a frozen,
  council-reviewed, blinded design on the basis of evidence that
  does not test its lever.
- The two historical FAILs both have measured causes that are fixed
  or routed around. The live speed FAIL (1.1) was driven by the D1
  startup race plus think variance; the race fix (52480e7) works
  live on attempt 1 in the re-measure. The flip DO NOT EXPAND (1.5)
  was driven by the Chromium mouse stall; the (b1) set_value path
  routes around it 5/5 in the re-open (1.6), and the stall itself
  is the step 9 prototype first target, not a pilot blocker: the
  pilot uses managed Chromium via the code-exec DOM path, not the
  occluded-tab mouse path.
- The executor blocks are gone. The 3 Y1b real fails that blocked
  the S2 flip at 06:41 (1.3) are closed by the step-1 closeout
  (1.4): 81 executor tests OK, full discover 1974 tests with 0
  failures. The pilot precondition that depended on them is met.
- The mechanism is proven live on a real task class. The re-open
  (1.6) is 5/5 runs complete, 10/10 sends verified, median 28.6s,
  0 model calls. The pilot now measures whether live composition
  preserves that win on harder tasks, which is exactly the step 9
  decision input.
- The pilot GO bar is built to catch a real failure, not to pass on
  a fast draw: median ratio, pass rate, recovery steps, composition
  think condition 4, plus the 2-of-3 rule, the dispersion rule, and
  the flagged-run rule (section 5). A NO-GO from this pilot means
  "not proven at pilot scale", never "batching does not work", per
  the frozen detection limit (powered for a 50 percent cut, not a
  30 percent cut). Killing before running it would trade a bounded
  measurement for an unmeasured judgment.

## 3. Why not plain RESUME: resume preconditions status

From the frozen plan section 9 and the pilot log (all must hold
before any live arm):

| Precondition | Status on the record |
|---|---|
| Frozen plan commit hash recorded in the pilot log | MET. f31abcf, in FREEZE.md and the pilot log. |
| Written timestamped resume order from Muse naming the 12 run-ids | NOT MET. No such order is in the record W-A1 read. This decision is the input to it, not the order itself. |
| Broker SOLO and idle, proven per run | TO VERIFY AT RESUME. Broker-status output saved per run. |
| Relay verified before run 1: started_git_head equals repo HEAD, CU_CODE_EXEC=1, CU_PICK4_FASTPATH=1 | NOT MET. Known defect, see F3. The relay was started without the flag, and the broker cannot set env per request (flip log section 4.3). |
| Layer-1 preflight 7/7 PASS, output committed | MET. tests/test_a1_preflight.py, 7/7 PASS. |
| Layer-2 preflight probes pass at resume | NOT MET. Probes in preflight-probe.md (4 probes x 2 submits, live browser, completed 0 and zero DOM effects) have not run. The checker real-run cross-check on the probe dirs is also owed. |
| Pool live validation done and held-out draw sealed | NOT MET. Pool is agy-q2 test-06 through test-10 only. Validated by simulation only (10/10 simulated). Live validation owed; draw not sealed. The fcc-k precedent is that simulation passes while live runs go 0/10 on fixture or spec defects. |
| Fixture checksums re-verified | TO VERIFY AT RESUME. pick4 md5 91b2f92945c167306a13ae32977a9bf3, f01 md5 2b6eda97036af51510b7eefe6d36dd93. |
| Run dirs plus sealed manifest under custody 9b | NOT MET. Manifest not created; Muse holds the only copy outside the repo and publishes only its sha256 before run 1. |
| Checker self-test T1-T16 run and passing, expected outputs committed, reviewed by an independent worker | MET. 17/17 passed, independent review done (FAIL narrow, 3 diagnostics fixed, matrix re-run 17/17). |
| Runbook, run-log schema, checker exist and committed | MET. Committed in 1399342 and frozen in f31abcf. |

Four preconditions unmet plus two to verify at resume. A plain
RESUME would assert a readiness the record does not support.

## 4. Fix list: close each item with evidence, then resume

All items are setup, none changes the frozen design. No threshold,
case, cap, fixture, run order, or checker change is authorized here.
If any fix requires such a change, stop and re-freeze instead.

- F1. Resume order plus manifest. Muse issues a written,
  timestamped resume order naming the 12 pre-generated run-ids.
  Muse pre-generates the run-ids with a1_manifest.py (not by hand),
  writes the sealed mapping outside the repo, and publishes only
  the manifest sha256 in the pilot log before run 1. Custody rule
  9b: Muse holds the only copy; the executor and the checker never
  receive the file, its path, or its contents. Close-out evidence:
  the order text plus the published sha256, recorded in the pilot
  log. Also re-confirm at resume that a fresh Luna 6 Max executor
  session can be launched on the laptop; if that executor is
  unavailable, the pilot does not start with a substitute, because
  the plan requires ONE fresh executor, same model and harness for
  both arms.
- F2. Pool live validation plus sealed held-out draw. Live-validate
  each agy-q2 test-06 through test-10 candidate once with the
  scripted runner (not the GO arm, not the executor). Only
  candidates that pass live as specced stay in the pool. Muse draws
  one task from the validated pool by a recorded random draw and
  seals it in the manifest before run 1. Close-out evidence: per
  candidate live result plus the sealed draw record.
- F3. Relay flags. Before run 1, verify from relay status output
  that started_git_head equals the repo HEAD and that CU_CODE_EXEC=1
  and CU_PICK4_FASTPATH=1 are set. The defect: the S2 flip log
  (section 4.3) proves the broker cannot set env per request, the
  driver env comes from the relay process env, and the relay was
  started without the flag, so the code-exec send ran as a one-shot
  session-driver with the flag on its own command line. The pilot
  precondition requires the relay to carry the flags. Fix by either
  restarting the relay with the flags (and re-verifying
  started_git_head after any laptop tree sync to the resume-time
  HEAD) or by a pre-run-1 amendment to the runbook adopting the
  one-shot path (amendments before run 1 are free: commit them,
  update FREEZE.md hashes, record the new freeze hash). Do not run
  with the flag off and do not silently substitute a path: cu.py
  refuses code-exec without the flag. Also resolve the endpoint
  preflight at resume (9222 versus the chromium-intel wrapper 9223,
  recorded as a resume-time check in the pilot log). Close-out
  evidence: relay status output saved in the pilot log.
- F4. Layer-2 preflight probes plus checker cross-check. Run the
  probes in tests/realistic/a1-pilot/preflight-probe.md at resume
  before any pilot arm: one probe per ref-taking action type the
  Case B program uses (click, fill, set_value, assert), each P1
  expecting CodeExecError plus P2 state dump expecting zero effects,
  plus Probe 5 (a program that retries internally must produce retry
  lines in the run log). Save probe evidence (completed 0 and zero
  DOM effects) per probe. Then run check_run.py on the real probe
  directories and confirm the hand-verified PASS/FAIL (the real-run
  cross-check owed since the freeze). Close-out evidence: probe
  evidence files plus the checker cross-check result. A probe
  failure triggers STOP, FIX THE ADAPTER, RE-PROBE, not a safety
  NO-GO (plan section 7). Only a partial effect that survives a fix
  attempt, or one the owner explicitly accepts as unfixable,
  becomes a safety NO-GO.
- F5. Fixture checksums re-verified at resume: pick4 md5
  91b2f92945c167306a13ae32977a9bf3 (719 bytes), f01 md5
  2b6eda97036af51510b7eefe6d36dd93. If either differs from the frozen
  value, the freeze is broken: re-verify and re-record before the
  first live run. Close-out evidence: md5 outputs recorded per run
  in runs/<run-id>/.
- F6. Broker SOLO plus desktop state. Before run 1, prove broker
  SOLO and idle by broker-status output saved per run. Check desktop
  state before run 1 and after run 12. Zen untouched by the pilot
  (Chromium only). Between runs: fresh browser session, fresh
  fixture state (storage cleared, fixture reloaded), desktop
  verified clean. Wall excludes reset time. Close-out evidence:
  broker-status output per run plus the before/after desktop checks.

## 5. Pass/fail criteria at the pilot verdict (frozen GO bar, verbatim summary)

GO (proceed to the confirmatory run, not adoption) only if ALL of
these hold. Case B (f01), all four conditions: (1) median wall time
(CODE) at or below 0.70 times median wall time (STEP), medians of 3
runs, all six walls printed; (2) pass rate (CODE) equal to or better
than pass rate (STEP), passes out of 3, every failure reason printed;
(3) total recovery steps across the 3 runs (CODE) not higher than
total recovery steps across the 3 runs (STEP), per-run counts
printed; (4) total composition think (CODE, sum over all program
calls) less than STEP median total think for that case. Case A
(Pick 4), feasibility gate: pass rate (CODE) equal or better than
pass rate (STEP), recovery steps (CODE) not higher than recovery
steps (STEP) in total across the 3 runs, and total composition think
(CODE) less than STEP median total think; its median wall time is a
diagnostic only, not a gate. Additional rules: 2-of-3 rule (at least
2 of the 3 CODE runs in Case B individually at least 20 percent
below the STEP median wall); dispersion rule (INCONCLUSIVE if
(max-min)/median exceeds 50 percent in any arm-case cell); flagged
runs stay in the median, and 2 or more flagged runs in one arm-case
cell means INCONCLUSIVE; INCONCLUSIVE is a third outcome. Robustness
check (every CODE run wall at or below the STEP median wall) is
mandatory reporting that sets the GO HIGH/LOW CONFIDENCE label, not
a gate. Detection limit: at n=3 the pilot is powered to detect a 50
percent wall cut, not a 30 percent cut; NO-GO means "not proven at
pilot scale", GO means "proceed to the confirmatory run".

Kill and pause conditions (from the frozen plan, not new): a Layer-2
probe partial effect surviving a fix attempt is a safety NO-GO
(section 7); the executor dying twice PAUSES the pilot (9c), Muse
reviews in writing before any new executor; a second session death
inside one run ends that run as FAIL; a restart that itself fails to
start ends the pilot (STOP, report to Muse, do not start the next
run); any threshold change after run 1 starts requires a new pilot,
the old pilot stays NO-GO or INCONCLUSIVE. Zen transfer probe is
mandatory between a Chromium GO and Exp1 (D10), not before the pilot.

## 6. Limitations and open items (honest record)

- No fresh W-A1 live measurement exists for this decision (section
  0.1). The decision rests on dossier evidence measured by
  independent workers on 19/11 and 22/11, cited with commit hashes
  and run times in section 1. If COORD-CLICK-6 wants a fresh W-A1
  re-measure, it must authorize the blocked git, build, and test
  actions first.
- The brief times 04:27 (provisional remeasure PASS) and 05:15
  (functional pass, speed bar FAIL) on 22/11 could not be located
  in the files W-A1 read (final direction log, probe-s2 log, S2
  flip log, S2 re-open log, step-1 closeout log, pilot log, pilot
  plan, FREEZE.md, remeasure summary, live summary, landing
  summary, fspeed response log, coord-click-6 log, S2 pilot
  digest). Their substance is grounded in sections 1.2 and 1.1.
  The clock times are taken from the brief as coordinator-supplied
  and are NOT independently re-verified by W-A1.
- The Layer-1 preflight duration is recorded as 0.014s in the pilot
  log and 0.002s in FREEZE.md. Both say 7/7 PASS. The difference is
  not load-bearing and is recorded here rather than resolved.
- Machine state at COORD-CLICK-6 resume (from the coord log): the
  laptop had a Hyprland exit 17:05 and a black screen after reboot
  (fixed by removing the Wants line from
  input-stall-monitor.service), Zen PID 14625, Brave 9224, Chromium
  9223 alive, disk 17G free. Clone1 locked until 20:01 Mon 23/11,
  clone2 locked until 02:38 Wed 25/11, so no clone work. Mei and
  mochi are active on other items. The pilot needs a quiet-ish
  laptop for its Chromium runs and broker SOLO; the coordinator
  schedules it around the other lanes.
- The CB-9 manifest gap (1.4) is noted for the record and does not
  change this decision: the pilot generates its own evidence with
  its own per-run provenance (repo HEAD, relay head plus flags,
  broker SOLO proof, fixture md5s), so it does not depend on the
  bench manifest.

## 7. Commit record

- This log: improvements/w-a1-pilot-decision-log.md.
- Status: WRITTEN, NOT COMMITTED, NOT PUSHED. Commit (explicit
  pathspec for this one file) and push (verified by git ls-remote)
  are blocked by the safeguard in section 0.1 until an explicit
  go-ahead arrives. The file tests/realistic/clone1-batch3/
  results.json was not touched.
- Session times: task received 17:49:23 +07, 22/11/2026. Dossier
  read and decision written in the same session. Elapsed time after
  the safeguard pause is not clocked here, because no further clock
  read was taken under the pause; the evidence times that matter
  are the run times cited in section 1.
