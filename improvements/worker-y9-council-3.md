# Council Member 3 review: Worker Y9 agy-y2 live-run plan (evidence and accounting only)

- Role: Council Member 3, Worker Y9 review council
- Date: 2026-11-21
- Scope: flagged-pass accounting, abort rule, evidence contract, slot polling, other accounting defects. No review of driving technique, spec fidelity, or fixture correctness.
- Reviewed: `improvements/worker-y9-agy-y2-live-plan.md` (commit 6f20fb5), `improvements/worker-y4d-council-2-ladder.md` sections Q3, Q4, Q5, `improvements/working-structure-redesign-20261121.md` sections 5.3 and 5.7, `tests/realistic/run_agyq2.py` main() lines 1215-1316, plus `tests/realistic/run_live.py` `Runner.summary`.
- Branch: todolist-push. Working tree at review time has uncommitted changes to `run_agyq2.py` and `run_live.py`.
- Method: every plan claim was checked against the code it cites. Line numbers below are from the files as read at review time.

## Verdict: BLOCK

The plan states most of the right rules in prose, but it cannot be executed as a checkable live run. The central problem is that the plan claims the Council 2 fixes are "already applied" while the runner file that must carry them, `tests/realistic/run_agy_y2.py`, does not exist, and the base file it is copied from still contains every defect Council 2 found. On top of that, the abort rule contradicts itself on session failures, the bootstrap-failure propagation has no specified output channel, the slot marker is not checkable, and the evidence contract is missing two legs. No live driving until the required fixes land and the actual runner code is re-reviewed.

## F1. BLOCKING: "fixes already applied" is false; the runner does not exist

- The plan says the harness is "copied from run_agyq2.py, with every known Y4d defect fixed up front" and "with these fixes already applied" (`improvements/worker-y9-agy-y2-live-plan.md`, lines 24-26). The commit message of 6f20fb5 repeats the claim ("all Y4d council fixes applied").
- `tests/realistic/run_agy_y2.py` does not exist in the working tree or on the branch (checked by `ls`; the plan itself lists it as a file to be written, plan line 66). There is no runner code to review, so no fix can be verified as applied.
- The base file still contains the exact defects the plan claims are fixed:
  - Council 2 F1: `tests/realistic/run_agyq2.py` line 253 sets `r.details["tz_hidden_removed"] = True` immediately after the removal eval (lines 251-252), BEFORE the post-remove `diagnose_body` at lines 259-261. The flag is still set on eval success, not on verified removal.
  - Council 2 F2: `bootstrap_tab` lines 1082-1084 create a throwaway `Runner("bootstrap", base)` and run `ensure_visible` on it; the flag and the encounter count on that throwaway are still discarded. The string `bootstrap_intervention` appears zero times in `run_agyq2.py` and zero times in `run_live.py`.
  - Council 2 F3: line 1287 `passed = sum(1 for s in results if s["pass"])` still folds flagged passes into the headline, and line 1312 `return 0 if passed == len(results) else 1` still exits 0 on an all-flagged suite.
  - Council 2 F4: `infra_blocked` is still reset only on a non-INFRA exception (line 1272). No reset on a pass exists anywhere in main().
  - Council 2 O1: the removal eval (lines 251-252) still clears only the `tz-hidden` class. The string `--zen-logo-path` appears nowhere in `run_agyq2.py` or `run_live.py`; it appears only in the plan, line 30.
- Consequence: the plan's section 3 is a list of intentions for a file that has not been written, presented as completed work. A plan may promise fixes; it may not report them as done. Until `run_agy_y2.py` exists and is diff-reviewed against Council 2 F1-F9, the flagged-pass rule does not hold end to end in any verifiable sense.

## F2. BLOCKING: the abort rule contradicts itself on session-creation failures

- Plan line 20 defines INFRA-blocked as "hidden-body unrecoverable after the recovery ladder, or a session-creation failure". Plan lines 20 and 31 then say `infra_blocked` "resets to 0 ... on the session-failure path".
- Those two instructions cannot both hold. If a session-creation failure IS an INFRA-blocked test, it must increment `infra_blocked` toward the two-consecutive abort. If it resets the counter, it is not counted as INFRA-blocked at all, and two consecutive session failures can never abort through this counter.
- The base code shows the two counters are separate and the plan never mentions the second one: session failures increment a separate `wd_failures` counter (`run_agyq2.py` lines 1252-1256, abort at `wd_failures >= 2`), reset `wd_failures = 0` after a successful session creation (line 1275), and never touch `infra_blocked`. The plan says nothing about whether the new runner keeps `wd_failures`, drops it, or merges it into `infra_blocked`.
- Required resolution: state exactly one rule, in code and in the plan. Either (a) session failures increment `infra_blocked` and the reset clause is deleted, or (b) session failures use only the separate `wd_failures` counter with its own two-consecutive abort, and line 20's definition is corrected to exclude session failures from INFRA-blocked. Either is defensible; the current text is neither.
- Secondary gap in the same rule: the plan is silent on non-INFRA runner failures. The base code resets `infra_blocked` on a non-INFRA exception (line 1272). If the new runner drops that reset, the sequence INFRA, RUNNER-FAIL, INFRA would wrongly abort as "consecutive". The plan must state whether a non-INFRA runner failure resets the counter.

## F3. BLOCKING: bootstrap propagation "including on the bootstrap-failure path" has no output channel

- Plan line 30: "bootstrap intervention is propagated to the suite JSON as a top-level bootstrap_intervention field, including on the bootstrap-failure path".
- In the base code, the bootstrap-failure path prints `BOOTSTRAP FAILED` and returns 2 with no JSON at all (`run_agyq2.py` lines 1230-1233). There is no suite JSON on that path to carry the field.
- The plan specifies no channel for this case: no stdout JSON line before return, no file written, no exit-code convention. It also specifies no schema for the field in any case: boolean, count, or detail object, and no value for "no intervention" (false, 0, or absent).
- Further, Council 2 F2 asked for the intervention AND the `hidden_body_encounters` count to be propagated. The plan mentions only the intervention field. The suite total in the base code sums encounters from per-test summaries only (`run_agyq2.py` lines 1290-1291), so bootstrap encounters would still be lost from the suite total even if the field existed.
- Also unspecified: tests share the bootstrap tab (plan line 33). If bootstrap intervened, do the 10 per-test summaries stay clean (flagged False) with the intervention recorded only at suite level? The plan must say so explicitly, or a reader cannot tell whether a clean headline means "no intervention anywhere" or "intervention happened before test 1".

## F4. BLOCKING: the slot-polling marker is not checkable

- Plan line 57: poll "every few minutes" for a marker that is "a commit on todolist-push recording Y8's E1 execution completion (its final report in improvements/worker-y8-e1-execution-log.md or a completion commit message)".
- Four defects:
  - (a) No exact match string. "A completion commit message" has no specified text, and the log file has no specified completion line. A commit that merely touches the log file (partial progress, mid-run note) is indistinguishable from completion under this rule.
  - (b) No polling interval. "Every few minutes" cannot be checked; the poll loop has no stated cadence, no stated timeout, and no stated action if the marker never appears.
  - (c) No abort handling. If Y8 aborts (infra, crash) instead of completing, no "completion" commit may ever appear, so Y9 would poll forever, even though the slot is actually free. The plan needs a rule for a Y8 abort marker or a dead-man timeout, and must state whether an aborted Y8 run frees the slot.
  - (d) The marker is git state only. Nothing in the plan re-checks live process state at launch: no geckodriver check, no check that Y8's server or driver is dead. The plan's own slot status (line 8: "no geckodriver running on laptop") is a plan-time observation that will be stale by run time. The `flock -w 1800` in the launch command (line 59) is the only live guard, and the plan does not say what happens when the 30 minute wait expires: retry, abort, or report.
- The transitive inference is sourced but thin: Y8 council-1 line 9 records "Y8 drives Zen only after Worker Y4d reports its agy-q2 rerun complete", which supports "Y8 done implies Y4d done" only if Y8 honored the order. The plan should verify Y4d's completion marker directly instead of inferring it through Y8.

## F5. BLOCKING: the evidence contract is missing two legs, and the stdout log has no capture path

- The contract as adopted requires "exact test command plus output/log, commit hash; timed run log plus end-state screenshot or video for machine tasks" (`improvements/working-structure-redesign-20261121.md`, line 110, section 5.3). A live Zen run is a machine task.
- Plan lines 65-66 list exact run command, stdout log, commit hash, timed JSONL, per-test summaries. End-state screenshot or video is absent. No capture step, no file path, no per-test or per-suite scope is specified.
- The stdout log itself has no capture path. The launch command (plan line 59) runs `python3 run_agy_y2.py all` under `flock` with no redirect, no `tee`, and no log file argument. `LIVE_LOG` points at the JSONL file, not stdout. As written, stdout from a detached SSH call is discarded, so the "stdout log" the contract requires would not exist.
- The commit-hash leg is also unachievable as the ship is specified. Plan line 26 ships from the "working tree at ship time" and line 60 ships files to `/tmp/worker-y9-server` on the laptop, but the working tree is currently dirty (uncommitted changes to `run_live.py` and `run_agyq2.py`), and no frozen commit hash for the shipped `run_live.py` is named anywhere. A dirty-tree ship has no commit hash to cite, and if Y4d lands changes between Y9's md5 recording and the ship, the shipped copy is undefined. The plan must name the exact commit (or require a commit first) and state where the md5 list is recorded.
- Secondary: the six per-run metrics in redesign section 5.7 (line 142) require wall time, tool calls, tokens best-effort, observation cost, VCR flag, and stall minutes. The plan measures wall time and recovery steps but never mentions tool calls, tokens, VCR, or stall minutes. At minimum the plan should state which of the six it reports and which it records as UNMEASURED.

## F6. The exit condition disagrees with itself, and the integrity-guard outcome is undefined

- Plan line 21: "Exit 0 iff clean + flagged == 10". Plan line 30: "exit 0 iff clean + flagged == total". The hardcoded 10 and the general `total` disagree if the runner is ever invoked on a subset (as `run_agyq2.py` supports via argv, main lines 1216-1217). One form must be chosen; `total` is the correct one.
- Plan line 18 (integrity guard): if verify passes on the untouched fixture, "abort that test as a suite defect, never a pass". The outcome value is undefined: is the test recorded as failed, as INFRA-blocked, or as skipped with no record? Does it increment `infra_blocked`? Does "abort that test" stop the suite or continue to the next test? A guard-triggered test currently has no defined entry in the suite JSON and no defined effect on the exit code. Specify the record (suggested: failed, `flagged` False, failure text naming the guard, suite continues) and its effect on the abort counter (suggested: no effect, it is a suite defect, not infra).
- Related: plan line 21 allows a re-run "ONLY for a test proven infra-blocked, logged as a re-run, never as a first pass". The interaction with the abort counter is unspecified: does the first INFRA still count toward two-consecutive after a successful re-run of the same test, and does the re-run's attempt count appear as a field in the per-test summary? Specify both, and the order (re-run immediately, or after the suite).

## F7. The flagged-pass definition has one unverified edge

- Plan line 19 requires the removal intervention to have run AND the post-remove snapshot to prove the class is gone. That is the correct F1 fix, and it is stated correctly.
- Edge not covered: if the removal is verified but the body is still hidden (OTHER_HIDDEN) and a later rebootstrap saves the test, is the test flagged? The intervention ran and the class is gone, so by the letter of line 19 it is flagged, but the pass was not caused by the removal. State the rule explicitly (suggested: flagged means verified removal happened on that test, regardless of which step later made it visible, and the summary must carry the full intervention log so the cause is auditable). This is minor and does not block on its own.

## What was checked and found sound

- The flagged-pass intent (plan lines 19, 30) states the correct F1 rule: flag only on verified removal, not on eval success. The wording is right; only the code is missing.
- The per-test `flagged` key on every summary including the session-failure path (plan line 30) is the correct F3 schema fix. In the base code the session path appends `r.summary()` directly (`run_agyq2.py` line 1253) with no `flagged` key, because `Runner.summary` (`run_live.py` lines 472-476) carries no such key and only the normal path adds it (line 1277). The plan's fix direction is correct.
- The INFRA match by `startswith("INFRA:")` (plan line 31) is stricter and better than the base code's substring match (`"INFRA:" in str(exc)`, line 1267), which would count any failure whose message merely contains the string. Correct direction, pending implementation.
- The 8 s ladder budget, handle registry, guarded diagnose, and swapped-tab tracking (plan lines 32-35) correctly restate Council 2 F5-F8. They are out of the accounting scope of this review except as noted in F1 (they cannot be verified without the runner file).
- The queue order itself (Y4d, then Y8, then Y9; one live runner at a time, plan line 7) is correctly stated and consistent with Y8 council-1 line 9.

## Required fixes (all must land before any live driving; then the runner code gets a fresh review)

1. Write `tests/realistic/run_agy_y2.py` and re-review it as code. Change the plan's "fixes already applied" (lines 24-26) to "fixes specified here, to be verified in the runner diff". Do not claim any Council 2 fix as applied until the diff shows it. In the runner: move the flag set to after the post-remove snapshot with an explicit `tz-hidden not in htmlClassList` check (F1); add the `--zen-logo-path` clear to the removal eval or soften the claim (O1); add the `flagged` key on the session-failure path; make `passed` count clean only and exit on `clean + flagged == total`.
2. Resolve the session-failure contradiction (F2) with one explicit rule: either session failures increment `infra_blocked` (delete the reset clause) or they use only the separate `wd_failures` counter with its own two-consecutive abort (correct line 20 to exclude them from INFRA-blocked). State the chosen rule in both the plan and the runner, and state whether a non-INFRA runner failure resets `infra_blocked`.
3. Specify the bootstrap propagation channel and schema (F3): exact field name, type, and no-intervention value; how the field is emitted on the bootstrap-failure path (stdout JSON line before return, or a file, with the exact format); and whether bootstrap `hidden_body_encounters` are added to the suite total. State explicitly that per-test `flagged` stays False for tests on a bootstrap-intervened tab, with the intervention recorded only at suite level.
4. Pin the slot marker (F4): exact commit-message string or exact log-file line to grep for; polling interval in minutes; a timeout and an abort-marker rule (Y8 abort frees the slot or not); a launch-time live check (geckodriver process check or equivalent) in addition to the git poll; and the action if `flock -w 1800` times out. Verify Y4d's completion marker directly rather than inferring it through Y8.
5. Close the evidence gaps (F5): add end-state screenshot or video capture for this machine task with a named path; add stdout capture to the launch command (redirect or tee with a named file); freeze the shipped tree to a named commit hash (commit the runner and base first, or record the exact hash shipped) and state where the md5 list lives; state which of the six section 5.7 metrics are reported and which are UNMEASURED.
6. Fix the exit wording and the guard outcome (F6): use `clean + flagged == total` everywhere, never the hardcoded 10; define the integrity-guard outcome record, whether the suite continues, and its effect on the abort counter; define the re-run's effect on the counter and its summary field.
7. Close the flagged edge (F7): state whether a test with verified removal but a rebootstrap save is flagged, and require the intervention log in the summary either way.

## Evidence index (sources for every finding above)

- Plan file: `improvements/worker-y9-agy-y2-live-plan.md` lines 7, 8, 18-21, 24-26, 30-33, 57, 59-61, 65-66.
- Council 2: `improvements/worker-y4d-council-2-ladder.md` Q3 (F1-F4), Q4 (F5), Q5 (F6-F9), observations O1.
- Evidence contract: `improvements/working-structure-redesign-20261121.md` line 110 (section 5.3), line 142 (section 5.7 six metrics).
- Base code: `tests/realistic/run_agyq2.py` lines 251-253 (flag set before verify), 1082-1084 (throwaway bootstrap Runner), 1230-1233 (bootstrap failure, no JSON), 1252-1256 (session path, separate counter, no flagged key), 1267-1272 (substring INFRA match, reset only on non-INFRA), 1275 (wd_failures reset), 1277 (flagged only on normal path), 1287 and 1312 (folded headline and exit), 1290-1291 (encounter total from per-test summaries only).
- `tests/realistic/run_live.py` lines 472-476 (`Runner.summary` carries no `flagged` key).
- Slot order source: `improvements/worker-y8-council-1.md` line 9 (Y8 drives only after Y4d reports complete).
- Absence checks at review time: `tests/realistic/run_agy_y2.py` does not exist; `bootstrap_intervention` occurs zero times in `run_agyq2.py` and `run_live.py`; `--zen-logo-path` occurs only in the plan, line 30; the launch command (plan line 59) contains no output redirect.
