# Council Member 2 verdict: Worker Y8 E1 comparison design

- Role: Council Member 2 of 3, judging the DRAFT design. Independent, no coordination with the other council members.
- Date: 2026-11-21, about 18:40 +07.
- Design judged: `improvements/worker-y8-e1-comparison-design.md` (DRAFT, pre-registration).
- Read before judging, in order: the design; `improvements/worker-x-e1-experiment-report.md`; `improvements/worker-y4b-hidden-body-root-cause.md`; the merged plan `improvements/worker-x-e1-plan-test-05.md` (58 steps); both executor briefs (`worker-x-e1-executor-a-brief.md`, `worker-x-e1-executor-b-brief.md`); X's infra scripts (`worker-x-e1-start-infra.sh`, `worker-x-e1-stop-infra.sh`).
- Method: paper debate only. No Zen driving, no tab opened, no infra started. Never ydotool.
- Verdict scale per question: AGREE (sound as written), AMEND (sound with a specific change, exact change stated), BLOCK (unsound as written, must change before any executor runs).

## Verdicts at a glance

| # | Question | Verdict |
|---|----------|---------|
| 1 | Are the win criteria fair, or biased toward A or B? | AMEND |
| 2 | Is the INFRA retry-once rule right, or should a hidden-body hit invalidate the whole comparison? | AMEND |
| 3 | Is n=1 acceptable with honest scoping, or run each arm twice? | AMEND |
| 4 | Does the pre-flight recovery ladder contaminate the comparison? | BLOCK |
| 5 | What else could produce a false win for B (or A)? | See list. Five items must be fixed before running; three are reporting fixes. |

## Overall

DO NOT RUN as written. The design is close: its invalid-run rules, its same-tab-acquisition rule, its FLAGGED-pass disclosure intent, and its honest n=1 scoping are all good. But Q4 is a BLOCK, and the Q1, Q2, and Q3 amendments change the win criteria themselves, so they must be applied and the design re-frozen before any executor launches. The checklist at the end of this file is the gate.

## Q1. Win criteria: AMEND

The bars themselves are fair. The total-time bar is the question as posed: deliberation plus merge is real cost, and B total must beat A total for deliberation to be faster in wall time. The accuracy bar is symmetric in structure. What is unsound is not the bars but the measurement definitions underneath them. Three fixes, all required before running.

### 1a. The accuracy sum double-counts single incidents and ignores the best accuracy signal

The design states:

> "ACCURACY: B wins ONLY if (B passes and A fails) OR (both pass AND B has strictly fewer errors + recovery steps than A)."

And the metrics schema defines "Errors" as the count of `{"ok": false}` results and "Recovery steps" as "retries + fallbacks + re-finds, with step numbers". These two counts overlap by construction, because the retry rules make recovery follow error. I checked both sources of the retry rules:

- The plan's error rule: "On any {"ok": false}: record the step and error. Retry that same command once; for clear, type, or click, first run find again with that step exact selector and use the newly returned element id. If a real click still fails, try click_js with the exact selector given at that step."
- The A brief, step 5: "On any {"ok": false} result: retry the same command once after re-finding the element; if it fails again, use click_js for clicks; if that fails, record the error with the step number and continue."

So one failed real click under the plan's rule produces 1 error + 1 re-find + 1 retry + 1 click_js fallback = 1 error + 3 recovery steps = 4 points in the design's sum, for a single underlying failure. The sum is dominated by mandated recovery actions, not by inaccuracy. Worse, the most direct accuracy signal is missing from the sum entirely: a check whose read differs after its one retry is recorded as a check failure, but check failures do not enter the accuracy criterion at all. An arm could record check failures and still "win" on accuracy if it had fewer error-plus-recovery points. And "Misclicks / failed clicks" is a third metric counting the same incident again.

Credit where due: both arms carry the same retry policy, so the mandates are symmetric. The asymmetry is that B's recovery is floored by the plan's mandatory rules while A's executor decides for itself and may skip a retry. The sum therefore measures rule-following at least as much as accuracy.

Exact replacement for the accuracy criterion:

> "Count error INCIDENTS, not actions. One incident is one root-cause driver failure (one {"ok": false} result) plus every recovery action it triggered (re-find, retry, click_js fallback), counted as ONE incident. A check that differs after its one retry is ONE check failure, counted separately and never folded into the incident count. PLAN DEFECTs are never counted as B executor errors. Comparison order: (1) PASS/FAIL first: if one arm passes and the other fails, the passer wins on accuracy. (2) If both pass: fewer check failures wins; if tied on check failures, fewer error incidents wins, but only when the margin is 2 or more; a margin of exactly 1 error incident with zero check-failure difference is a draw, not a win, at n=1. (3) If both fail: accuracy is a draw at failure, and the failure modes are compared. A B failure caused solely by a recorded PLAN DEFECT is reported as 'B failed on a plan defect', not as an executor accuracy loss."

### 1b. The design never states whether PLAN DEFECTs enter B's error total

The metrics list puts "plan deviations + PLAN DEFECTs" on a separate line from "Errors", but the accuracy criterion says "strictly fewer errors + recovery steps" without saying whether a defect-driven deviation and its forced recovery count toward B. A defect that forces B to deviate and retry inflates B's count through no fault of the executor. The replacement text in 1a settles this: defects never count as executor errors.

### 1c. The deciding clock and the merge time are not frozen

The design records two wall clocks per arm (executor-recorded start/end, and coordinator-observed launch-to-final-report) and says "Both stated", but the win criteria never say which clock decides. The two clocks differ: executor-recorded starts at the executor's first action and excludes pre-flight and infra start, while coordinator-observed includes them. Pre-flight and infra are real cost and real confound surface, so the deciding clock must be the coordinator-observed one.

The merge time is "about 2 min", but X's report bounds it exactly by file mtimes: drafts fetched 18:03:48, plan written 18:05:50. That is 2m02s. Freeze it.

Exact replacement for the speed criterion:

> "Deciding clock: coordinator-observed launch-to-final-report wall time for each arm. Executor-recorded start/end is reported as a secondary check. B total = deliberation 8m40s + merge 2m02s (frozen from X's mtimes) + B coordinator-observed wall. A total = A coordinator-observed wall. The merge time is frozen at 2m02s, not 'about 2 min'."

## Q2. INFRA retry-once rule: AMEND

The design states:

> "If the pre-flight diagnose classifies the fresh tab OTHER_HIDDEN or TZ_STUCK_V1 persisting after the recovery ladder (below), the arm does NOT start. That arm is INFRA-BLOCKED, not a FAIL. Retry the whole arm once after 5 min. If it recurs, report both arms as blocked with the infra evidence and stop; do not run one arm and compare it against nothing."

Full invalidation of the whole comparison on any single hidden-body hit is overkill, and I do not require it. The "same browser-health window" ideal is not achievable in practice: the hidden-body window is intermittent, its cause is unproven (Y4b: V1 badly wounded, V2 dead, third mechanism unknown), and it is observable only by probing. A pre-flight diagnose plus per-arm record plus a downgraded verdict can contain it. But the rule as written has four defects. Fix all four.

### 2a. Wait 10 minutes, not 5

Both observed incidents lasted 7 to 8 minutes (16:36-16:44, 17:52-17:59). A 5-minute wait risks burning the single retry inside the same episode. Change "Retry the whole arm once after 5 min" to "Retry the whole arm once after 10 min". The retry re-runs the FULL pre-flight from scratch on a new tab; state that explicitly.

### 2b. Add a mid-run hidden-body rule (currently missing)

The design gates only the start of an arm. Nothing proves an already-open tab cannot go hidden mid-run: Y4b records that old hidden tabs were never re-checked in either incident, so whether an open tab can transition to hidden is unknown. If the window opens after pre-flight passes, the executor will burn its plan-mandated retries on an infra fault and record errors that then enter the accuracy comparison. Add this rule:

> "If, after pre-flight passes, the executor's first fixture reads show a hidden body (computed visibility hidden, or innerText length 0 with the DOM present), the executor stops immediately, records INFRA-SUSPECT with the read values, and the arm is INVALID, not FAIL. Retry once from scratch after the 10-minute wait. If it recurs mid-run, report as blocked."

### 2c. Downgrade the verdict for any arm that needed a retry or a ladder intervention

A retried arm did not run under the same conditions as a clean arm. Add to the win-criteria section:

> "If either arm needed an infra retry or any recovery-ladder intervention, no clean win or loss is claimed on either criterion. The result is reported as an observed difference, confounded by browser health, with the pre-flight evidence attached."

### 2d. The double-block wording is false when one arm already ran

"If it recurs, report both arms as blocked" is wrong in the case where A already ran cleanly and B is then blocked twice. A is measured, not blocked. Replace with:

> "If it recurs, report each arm as it stands: a ran arm is reported as measured, the blocked arm as INFRA-BLOCKED, and the comparison as unanswerable. Stop. Do not run one arm and compare it against nothing, and do not report a ran arm as blocked."

## Q3. n=1: AMEND (keep n=1, fix the verdict language, add a replication trigger)

The design already states the honest scope:

> "n=1 per arm: one run each, one task, one model. This is ONE observation, not proof of a general effect. Any verdict is scoped to 'this task, this run'. No claim about deliberation in general follows from n=1."

And:

> "Executor nondeterminism: same model and settings, but codex runs are not deterministic. A second A run could differ. This is a stated limit, not a fixable one at n=1."

On the parent's specific challenge, whether A-first-then-B ordering plus executor nondeterminism makes the comparison meaningless at n=1: no, not meaningless, but the binary win/lose language is not supportable at n=1. One draw from A's distribution against one draw from B's distribution still measures two real runs, validates the harness, and measures the effect-size scale, which is exactly what a pilot is for. What n=1 cannot support is a "B wins" / "B loses" claim, because a single nondeterministic hiccup (one failed-click cascade, one slow decide) can flip either criterion, and the order effect (warm Zen and driver favoring B on execution) pulls against the 10m40s total-time bar (disfavoring B) with neither magnitude quantified. A small margin in either direction is uninterpretable.

Three changes:

1. Keep n=1 for this first run. It is a pilot. Do not mandate A1/A2/B1/B2 up front: that doubles Zen time and hidden-body exposure for a variance estimate that the trigger in change 2 buys only when needed. If a stronger claim is wanted later, the honest price is 2 runs per arm with interleaved order (A1, B1, A2, B2), reusing the same plan for B1/B2 with no new deliberation cost.

2. Replace binary verdict language with observed-difference language plus a mandatory noise caveat. The design's "B wins ONLY if..." / "B loses" phrasing must become: "on this run, B was faster/slower by X; A had N error incidents, B had M", followed by a caveat naming both unmeasured variances (executor nondeterminism, A-first order effect). No "deliberation wins" or "deliberation loses" claim may be published from n=1.

3. Pre-register a replication trigger: if the winning margin on either criterion is within one incident (accuracy margin of 1, or time margin smaller than the cost of a single retry cascade), the verdict is "inconclusive at n=1, replicate", and a second run of BOTH arms is required before any win claim. If replication runs happen, run B before A (B2, then A2) to counterbalance the A-first order effect.

## Q4. Pre-flight recovery ladder: BLOCK

The design states:

> "Recovery ladder, 8 s total budget: poll 250 ms up to 2.0 s for the extension's own removal; if V1 persists, remove tz-hidden exactly as removeLoadingScreen does (single eval, test tab only, test origin only, logged as intervention); then re-diagnose. If still hidden, declare INFRA-BLOCKED per the rule above."

And:

> "A pass achieved only after the tz-hidden removal is a FLAGGED pass, counted separately in the summary, never folded silently into the headline pass count. Removing the class masks a real user-facing defect, so the intervention is disclosed in the test report."

The FLAGGED-pass disclosure intent is right. The mechanics are unsound as written, for one reason: after a manual tz-hidden removal, a re-diagnose of the SAME tab is vacuous. Of course the tab is visible; the hiding class was just removed by hand. That re-diagnose cannot distinguish "the hidden-body window lifted" from "I removed the class". Pre-flight would then green-light an executor launch into a browser that is demonstrably inside a hidden-body episode, the executor's own fresh tab would very likely be hidden too (6 of 6 new tabs hid during the incident), and the executor's resulting infra errors would be counted as executor errors under the accuracy criterion. That is a false-verdict path, not a wording issue. Hence BLOCK, not AMEND.

Exact fix, to be applied before any executor runs:

1. Split "then re-diagnose" into two steps: "(a) re-diagnose the SAME tab: if still hidden after the class removal, the hiding mechanism is not V1; classify OTHER_HIDDEN and declare INFRA-BLOCKED. (b) If the same tab is now visible, close it and open a NEW fresh tab with NO intervention; diagnose it. Only a new tab that is visible WITHOUT any intervention passes pre-flight."

2. A FLAGGED pass may result ONLY from the poll-wait path (the extension removed the class itself within 2.0 s). A manual tz-hidden removal never yields a pass. A manual removal followed by a clean new tab is logged as a V1 sighting plus a clean pass; a manual removal followed by a hidden new tab is INFRA-BLOCKED.

3. State in the win criteria: a FLAGGED pass does not count as a pass for the accuracy win criterion. An arm whose pre-flight needed any intervention is reported as INFRA-FLAGGED and its verdict is downgraded to observed/confounded (see Q2 change 2c).

4. Specify the exact removal eval. "Remove tz-hidden exactly as removeLoadingScreen does" is unspecified as written, and removeLoadingScreen also removes the --zen-logo-path inline property that initLoadingScreen sets on documentElement (Y4b wound 2). Either write out the exact eval (remove the class AND the inline property) or drop the "exactly as removeLoadingScreen does" claim.

Note what the ladder does NOT contaminate: the executor never drives the intervened tab, because "The pre-flight tab is closed after diagnose; each executor opens its own fresh tab afterwards." The contamination is indirect (launching into a bad window), not direct (driving a doctored tab). The fix above closes the indirect path.

## Q5. Other false-win sources

### F1. Plan/spec leakage has no enforcement or verification (false win for either arm, MUST FIX)

A's brief forbids reading any plan file, and B's brief forbids reading the spec and fixture. But nothing enforces or verifies this, and the merged plan sits in the repo at `improvements/worker-x-e1-plan-test-05.md`, which A can reach while reading the spec, fixture, and hand_drive.py from the same repo. A's brief forbids `/tmp/e1/plans/` but does not name the repo copy. If A reads the plan, A is no longer DIRECT; if B reads the spec or fixture, B is no longer plan-only. Either leak falsifies the condition and any win from it.

Fix: amend A's brief to forbid the exact repo path `improvements/worker-x-e1-plan-test-05.md` as well as `/tmp/e1/plans/` and `/tmp/e1/plan-test-05.md`. Add a coordinator check: grep both executors' --json event streams and run reports for references to the forbidden files; any hit makes that arm INVALID, not a result.

### F2. File-read timing is ambiguous against the measured window (false win for A, MUST FIX)

Both briefs list file reads in Inputs ("read it fully first") while Procedure step 1 is the date command that starts the measured window. If the executor reads the spec and fixture before the date command, A's deliberation time (its read plus its deciding) falls outside the measured window, understating A total. The same ambiguity slightly understates B total for the plan read.

Fix: freeze "date command first, then all file reads" in both briefs, and verify from the event stream that no file read precedes the date command.

### F3. Raw error counts are not normalized by command volume (bias against B, reporting fix)

B executes a 58-step plan; A works from 28 spec steps and will run a different, probably smaller, number of driver commands. More commands mean more opportunities for {"ok": false}. A raw-count accuracy comparison biases against the arm that runs more commands. Fix: report errors per 100 driver commands alongside raw counts, and make check failures (not raw recovery actions) the primary accuracy signal after PASS/FAIL, per the Q1 replacement criterion.

### F4. click_js policy differs between the arms (false win for A, MUST FIX)

B's plan mandates a real click first and click_js only after a failed retry. A's brief says "prefer click_js for the star icon if a real click fails" but otherwise lets A decide, so A may use click_js throughout. click_js never fails on interactability and is faster, so an A that goes click_js-first wins on speed and errors through a click-policy difference, not through direct deciding.

Fix (preferred): amend A's brief to the same rule as the plan, real click first and click_js only after a real-click retry fails, so the arms differ in deciding, not in click method. Fallback if not frozen: record click_js count per arm, and if A's click_js share exceeds B's by a wide margin, the verdict must name the click-policy difference as a confound.

### F5. Infra state between the arms is uncontrolled (false win for B, MUST FIX)

No rule restarts infra between A and B. B inherits a warm driver and HTTP server, and possibly a session state A left behind. The design notes warm state could favor B but does nothing about it.

Fix: restart infra between the arms (fresh driver, fresh HTTP server, fresh session), record infra start times per arm, and specify the pre-flight session lifecycle: pre-flight uses its own session, which is deleted before the executor launches, so only one session ever exists at a time (the single-session lock from the Y4b fix design).

### F6. Machine load and competing live work are unrecorded (either arm, reporting fix)

The runs are sequential and may be an hour apart. Nothing records system load at each arm start, and nothing bars another live runner from starting mid-arm.

Fix: record load average and running live processes at each arm start. If any other live-runner session starts mid-arm, that arm is INVALID and is re-run.

### F7. Tool-call counting is a command count, not a tool-call count (reporting fix)

Tool calls are counted from "completed command_execution items; agent_message excluded". File reads and other non-command items may not appear as command_execution, so the count understates deciding work, especially for A, which reads the spec and fixture. Fix: label the metric as driver-command count, or count all completed item types and state the rule.

### F8. Mid-run hidden-body (either arm, MUST FIX)

Covered under Q2 change 2b. Listed here because it is also a false-win source: an infra fault mid-run becomes executor errors in the accuracy comparison.

## Additional pre-flight flags (beyond Q4)

- P1. FIXTURE_FAILURE has no response rule. The invalid-run rules cover INFRA (hidden-body) and DRIVER DEAD, but not a pre-flight classification of FIXTURE_FAILURE (HTTP error, missing #contacts-count). Add: the arm does not start; fix the server or fixture; retry once; if it recurs, report as blocked.
- P2. The raw diagnose output must be saved to disk per arm (for example `/tmp/e1/preflight-a.json` and `/tmp/e1/preflight-b.json`) with timestamps. The design lists the diagnose result as a metric but never requires the raw snapshot JSON to be saved. Y4b's decisive-experiment standard is that every probe output is saved; a verdict that cannot be re-checked from a saved snapshot is not auditable.
- P3. The transition property/duration/delay fields in the diagnose payload are dead weight now that V2 is dead (Y4b killed the transition-frozen mechanism by the CSS visibility interpolation rule). Keep them only if the design states they are collected as a stated diagnostic, otherwise drop them.
- P4. The design's pre-flight is only the diagnose. It omits the Y4b preflight() gate items: stale-geckodriver sweep by PID with parent check, single-session lock, Zen liveness, fixture-server loopback check, owner-away check. Add them before the diagnose. The design does state the resume condition (Y4d complete) in the Arms section, but the per-arm gate must re-check Zen liveness and the fixture server at run time, because the "Verified inputs" snapshot (Zen PID 27958, ports free) is from 18:24 and will be stale by run time.
- P5. The pre-flight tab close must be specified as closing via the same session that opened it, with the session deleted before the executor launches (single-session rule, see F5).

## Infra appendix flags

- I1. Y8's characterization of X's stop script is accurate. I read `worker-x-e1-stop-infra.sh`: it uses `pkill -f "hand_drive_e1.py"` and `pkill -f "http.server 8767"` in the body while its own header comment says "Never pkill -f". The file contradicts itself, and the pkill -f use is exactly the standing-rule violation Y8 describes. This part of the appendix is correct.
- I2. The replacement as written is unsafe. "pkill -x geckodriver only if its cmdline shows port 4451" cannot be expressed as a single pkill invocation, and pkill -x kills every process with that exact name, including Y4's geckodriver on port 4448. As written, the Y8 stop script could kill another worker's driver. Replacement: look up the geckodriver PID whose cmdline contains port 4451 (ps plus a cmdline match, or pgrep -f with a pattern anchored to the E1 driver), then kill that PID only. Never run pkill -x geckodriver.
- I3. "geckodriver via the driver's child table" needs a concrete method in the script, not just in the design: record the driver's child PID at start (for example from the driver's process children) and kill by that PID.
- I4. Commit the Y8 scripts to the repo like X's were. "New files in /tmp/e1/" are laptop scratch that no reviewer can check from the repo. The design file is committed; its infra scripts should be too.
- I5. Keep X's post-stop verification in the Y8 versions: after killing by PID, verify ports 4451 and 8767 are free and no E1 geckodriver remains.

## Gate: what must change before any executor runs

1. Q4 BLOCK: rewrite the ladder's re-diagnose step per the exact fix (same-tab check for OTHER_HIDDEN, then a NEW unassisted tab as the only pass condition; FLAGGED pass only from the poll-wait path; FLAGGED pass does not count for the accuracy criterion; exact removal eval specified).
2. Q1: apply the replacement accuracy criterion (incident counting, check failures primary, PLAN DEFECTs excluded, 1-incident margin is a draw) and the frozen speed rule (coordinator-observed clock decides, merge frozen at 2m02s).
3. Q2: 10-minute retry wait, mid-run hidden-body rule, verdict downgrade for retried or intervened arms, corrected double-block wording.
4. Q3: observed-difference verdict language with the noise caveat, and the pre-registered replication trigger (B before A on replication).
5. Q5 must-fix items: F1 (leakage check plus repo-copy ban in A's brief), F2 (date command before all reads), F4 (shared click policy), F5 (infra restart between arms, single-session rule), F8 (same as Q2 2b).
6. P1 (FIXTURE_FAILURE response rule), P2 (save raw pre-flight JSON per arm), P4 (Y4b preflight gate items), and I2 (PID-only geckodriver kill, never pkill -x) from the additional flags.

After those changes, re-freeze the design (bump it from DRAFT, record the frozen text) and then, and only then, launch the executors.
