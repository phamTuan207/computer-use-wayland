# E1 execution comparison: DRAFT design (Worker Y8, pre-registration)

Status: DRAFT, under council + redteam debate. No executor has run. Nothing in this file is a result.

## Question

Does splitting deliberation (many agents) from execution (one agent) increase SPEED or ACCURACY versus one agent deciding and executing? Deliberation is already measured (8m 40s parallel max + about 2 min merge). This phase measures the two execution arms.

## Arms (same task, same machine, sequential)

- Task: test-05-contact-book, 28 spec steps. Fixture: tests/realistic/agy-q2/fixtures/test-05-contact-book.html.
- Condition A (DIRECT): 1 fresh executor reads spec + fixture, decides each step, drives live Zen hand-driven via /tmp/e1/step.sh. Brief: /tmp/e1/worker-x-e1-executor-a-brief.md.
- Condition B (DELIBERATED): 1 fresh executor executes ONLY the merged 58-step plan (/tmp/e1/plan-test-05.md, md5 a7b5646b2bf081386bb7bcea0563ad5a). It never sees the spec or fixture. Brief: /tmp/e1/worker-x-e1-executor-b-brief.md.
- Order: A first, then B, never concurrent. One live runner at a time on the shared Zen; E1 runs only after Worker Y4d reports its agy-q2 rerun complete.
- Executor mechanism (same as X used for deliberators): fresh codex CLI invocations on the laptop (codex 0.169.0, -m gpt-6-luna -c model_reasoning_effort=max -s danger-full-access --json), one process per executor, launched detached, briefed self-contained from a file. Tool calls counted from the --json event stream (completed command_execution items; agent_message excluded).

## Verified inputs (18:24 +07, 21/11)

md5 identical VM repo vs laptop repo: spec f1dd164ed2bdc70d5fb08cfafc75aebe, fixture 31b312f449308ca0911bc71f986f5fdb, hand_drive.py 8bcf048320249c253eb7b061a3ad9fb6. Plan md5 a7b5646b2bf081386bb7bcea0563ad5a matches the repo copy and /tmp/e1/plan-test-05.md. No geckodriver running; Zen PID 27958 alive; ports 4451/8767 free; Y4 fixture server still on 8768 (not E1's).

## Metrics recorded per arm (identical schema)

- Wall time: executor-recorded start/end (date "+%F %T %Z" in the brief) AND coordinator-observed launch-to-final-report wall. Both stated.
- Driver commands run (counted from the executor report + /tmp/e1/out.log lines).
- Tool calls (from the codex --json event stream).
- Errors: count of {"ok": false} driver results, with step numbers.
- Misclicks / failed clicks (real click failed, fell back to click_js), with step numbers.
- Recovery steps: retries + fallbacks + re-finds, with step numbers.
- Check failures recorded (a check whose read differed after its one retry), with step numbers.
- PASS/FAIL: decided ONLY from DOM reads + window.__agyVerify() returned JSON, never from an executor claim.
- B only: plan deviations (steps not followed verbatim) + PLAN DEFECTs, each with plan step number.
- Pre-flight diagnose result per arm (see below).

## Pre-registered win criteria (frozen BEFORE either arm runs)

Deliberation + merge already cost 8m 40s + about 2 min = about 10m 40s before B execution starts.

- SPEED (total): B wins ONLY if B total (deliberation + merge + B execution) < A total (A execution). Otherwise B loses on total speed, whatever B execution alone shows.
- SPEED (execution only): reported separately. If B execution < A execution but B total > A total, the verdict is: execution faster, total slower. That is a partial result, not a win.
- ACCURACY: B wins ONLY if (B passes and A fails) OR (both pass AND B has strictly fewer errors + recovery steps than A). If A passes and B fails, B loses on accuracy regardless of speed. If both fail, accuracy is a draw at failure, and the failure modes are compared.
- VERDICT: the experiment answers "faster?" and "more accurate?" separately. No single blended score.

## Invalid-run rules (decided in advance, not after seeing a result)

- INFRA: hidden-body. If the pre-flight diagnose classifies the fresh tab OTHER_HIDDEN or TZ_STUCK_V1 persisting after the recovery ladder (below), the arm does NOT start. That arm is INFRA-BLOCKED, not a FAIL. Retry the whole arm once after 5 min. If it recurs, report both arms as blocked with the infra evidence and stop; do not run one arm and compare it against nothing.
- DRIVER DEAD: if step.sh times out twice in a row, the executor records DRIVER DEAD and stops (per the brief). That arm is INVALID, not a fail. Retry once from scratch after infra restart; if it recurs, report as blocked.
- An arm that starts but whose executor crashes mid-run (codex process dies, SSH dies) is INVALID and is re-run once from scratch. The crashed partial run is logged, never silently discarded, never counted as the arm's result.
- The two arms must use the SAME tab-acquisition method. If the fresh-tab method fails for A and a fallback is used, the same fallback is used for B, and the change is recorded.

## Pre-flight diagnose (adapted from Y4b's fix design, E1 version)

Run by the coordinator before EACH arm, after infra start, before the executor launches. No executor drives until pre-flight passes.

- Open ONE fresh tab via the E1 driver to the fixture URL. One eval, one snapshot (diagnose_body): readyState, documentElement classList (tz-hidden, tz-initialized), body computed visibility/opacity/display, html visibility, body inline style, transition property/duration/delay, body rect, innerText length (corroboration only), hasFocus, visibilityState, URL. Sample twice 300 ms apart when hidden.
- Classification: VISIBLE, TZ_STUCK_V1 (tz-hidden present), OTHER_HIDDEN (class absent, computed hidden), FIXTURE_FAILURE (fixture itself fails to load, e.g. HTTP error, missing #contacts-count).
- Recovery ladder, 8 s total budget: poll 250 ms up to 2.0 s for the extension's own removal; if V1 persists, remove tz-hidden exactly as removeLoadingScreen does (single eval, test tab only, test origin only, logged as intervention); then re-diagnose. If still hidden, declare INFRA-BLOCKED per the rule above.
- A pass achieved only after the tz-hidden removal is a FLAGGED pass, counted separately in the summary, never folded silently into the headline pass count. Removing the class masks a real user-facing defect, so the intervention is disclosed in the test report.
- The pre-flight tab is closed after diagnose; each executor opens its own fresh tab afterwards. Never use a real click as a recovery probe. Never touch a user tab. Never dismiss the open alert on any user tab.
- V2 (transition frozen) is DEAD per Y4b and is not a category: class-absent plus computed-hidden is OTHER_HIDDEN.

## Deviation accounting (B only)

- B executor must follow the plan verbatim. Any step not followed verbatim is a deviation, logged with plan step number and reason. A deviation forced by a PLAN DEFECT (step impossible as written after the allowed retry) is logged as a defect, not as executor improvisation.
- The comparison of "plan followed verbatim" is decided by the coordinator reading the B run report against the plan file, not by the executor's own claim.

## Known confounds (stated now, not discovered later)

- Order effect: A runs first, B second. Zen/driver warm state could favor B; a hidden-body window could hit either arm. Pre-flight results per arm are the record of this.
- n=1 per arm: one run each, one task, one model. This is ONE observation, not proof of a general effect. Any verdict is scoped to "this task, this run". No claim about deliberation in general follows from n=1.
- Executor nondeterminism: same model and settings, but codex runs are not deterministic. A second A run could differ. This is a stated limit, not a fixable one at n=1.
- Deliberation cost is sunk before B runs: 10m 40s. B execution must beat A by more than that on total wall time to win on speed.

## Infra fix (appendix, implementation note)

X's stop-infra.sh uses `pkill -f`, which violates the standing rule (pkill -f matches the SSH command string itself and drops the session). Y8 will write worker-y8-start-infra.sh / worker-y8-stop-infra.sh that record exact PIDs at start (holder, driver, http server, geckodriver via the driver's child table) and kill by exact PID only, with pkill -x geckodriver only if its cmdline shows port 4451. X's scripts are not edited in place; the Y8 versions are new files in /tmp/e1/.

## Open questions for council + redteam

1. Are the win criteria fair, or do they bias toward A (total-time bar) or toward B (accuracy bar)?
2. Is the INFRA retry-once rule right, or should a hidden-body hit invalidate the whole comparison (both arms must run in the same browser-health window)?
3. Is n=1 acceptable as a first observation with honest scoping, or should each arm run twice (A1/A2/B1/B2) before any verdict?
4. Does the pre-flight recovery ladder (removing tz-hidden on the test tab) contaminate the comparison, since a FLAGGED pass is still a pass?
5. What else could produce a false win for B (or for A) that this design does not catch?
