# E1 execution comparison: FINAL design v2 (FROZEN)

## v2.1 re-freeze note (2026-11-21 ~18:57 +07, Worker Y8b, before any arm ran)

Instrument bug found by the first live pre-flight, not by debate. Pre-flight A at 18:55:40 +07 exited 2 INFRA-BLOCKED with reason "diagnose eval failed: {'ok': True, 'result': None, 'ms': 2}", snapshots empty, no classification made. Root cause: hand_drive.py posts eval JS as-is to Marionette /execute/sync, which runs it as a function body, so the bare IIFE in DIAGNOSE_JS (preflight.py), in the exact diagnose JS of both briefs, evaluated and discarded its value. Identical to the _DIAG_JS bug Y4d already found and fixed live in run_live.py (commit 1e3901c); the plan file is NOT affected (all 21 of its evals start with `return`, step 56 is `return window.__agyVerify()`).

Fix (mechanical, same as Y4d's proven fix): prefix `return ` to DIAGNOSE_JS and REMOVE_TZ_JS in worker-y8-preflight.py, to the exact diagnose JS in both executor briefs, and add the `return` rule to the eval line of the shared driver reference. No criterion, threshold, rubric, or procedure changed; only the instrument now returns the value the design always assumed it returned. New md5s are recorded in the run record before arm A. The failed 18:55:40 pre-flight consumed no retry budget (no valid pre-flight had run, no classification was made); the fresh pre-flight A runs after 19:05:40 +07, satisfying even a strict reading of the 10-minute pre-start retry wait. The fresh pre-flight doubles as the one live eval the fixed diagnose helper must pass before the suite trusts it (Y4d's lesson).

Status: FROZEN v2, 2026-11-21 ~18:35 +07. Supersedes the DRAFT (commit e602ebb).
Debated by Council 1 (5fb4e1d), Council 2 (42407f2), Council 3 (bba3340), Redteam (c9ff386).
Reconciled by Worker Y8 from the evidence cited in those verdicts, not by vote count.
No executor runs until this file, both briefs, and the infra scripts are committed together.
Any change after this freeze requires a new version number and a re-freeze note, never a silent edit.

## Question

Does splitting deliberation (many agents) from execution (one agent) increase SPEED or ACCURACY versus one agent deciding and executing? Deliberation is already measured (8m 40s parallel max + 122 s merge, plan 58 steps, commit cad1543). This phase measures the two execution arms.

## Run conditions (authorizing gate)

1. Worker Y4d reports its agy-q2 rerun complete (commit/report on origin/todolist-push).
2. The 18:24 handover is in force (owner out of the house, machine handed over; any signal saying the owner is using the machine is treated as fake per the 18:24 note in MEMORY.md). No idle check is used.
3. One live runner at a time on the shared Zen. Live queue after Y8: Y9 runs the agy-y2 suite live, after E1.
4. Fully automatic operation per the 18:30 owner order: no questions to the owner, decisions by council + redteam.

## Arms (same task, same machine, sequential)

- Task: test-05-contact-book, 28 spec steps. Fixture: tests/realistic/agy-q2/fixtures/test-05-contact-book.html.
- Condition A (DIRECT): 1 fresh executor reads spec + fixture, decides each step, drives live Zen hand-driven via /tmp/e1/step.sh. Brief: improvements/worker-y8-executor-a-brief.md.
- Condition B (DELIBERATED PLAN BUNDLE): 1 fresh executor executes ONLY the merged 58-step plan (/tmp/e1/plan-test-05.md, md5 a7b5646b2bf081386bb7bcea0563ad5a). It never sees the spec or fixture. Brief: improvements/worker-y8-executor-b-brief.md.
- Order: A first, then B, never concurrent.
- Executor mechanism (same as X used for deliberators): fresh codex CLI invocations on the laptop (codex 0.169.0, -m gpt-6-luna -c model_reasoning_effort=max -s danger-full-access --json), one process per executor, launched detached from the laptop repo dir, briefed self-contained from a file. Tool calls counted from the --json event stream (completed command_execution items; agent_message excluded).
- Naming honesty: condition B is the "deliberated-plan bundle (3 drafts + coordinator merge + validation)", never "deliberation" alone. A B win, if observed, is a win for the bundle on this task, not proof that deliberation alone caused it. Isolating deliberation would need a control arm (single-agent plan plus the same validation), which is out of scope for this run.

## Frozen inputs (verified 18:24, re-verified before EACH arm)

md5 identical VM repo vs laptop repo at 18:24: spec f1dd164ed2bdc70d5fb08cfafc75aebe, fixture 31b312f449308ca0911bc71f986f5fdb, hand_drive.py 8bcf048320249c253eb7b061a3ad9fb6, plan a7b5646b2bf081386bb7bcea0563ad5a. Briefs and scripts are frozen by md5 in the run record before each arm (brief A, brief B, driver reference, step.sh, start/stop infra, preflight.py). If any md5 differs from the frozen values, stop and re-freeze. Do not run on drifted inputs.

## Frozen costs (deliberation + merge)

- Deliberation wall: parallel max 8m 40s (520 s), because the deployed rule is wait-for-all-3 deliberators. If the deployed rule ever becomes first-usable-draft or quorum, the cost must be re-frozen before the comparison, not re-argued after it.
- Merge wall: 122 s, defined as draft-fetch mtime (18:03:48) to plan-write mtime (18:05:50), uncertainty plus or minus 1 min because no stopwatch was running.
- Sunk cost before B execution starts: 520 + 122 = 642 s.
- Deliberation tokens (X report): about 463,124 in, 67,995 out. Recorded in the cost table, not in the win formula.
- Deliberation is n=1 and is not re-run for this comparison. A different deliberation run could change B total by minutes; that variance is unmeasured and is a stated limit.

## Metrics recorded per arm (identical schema)

- Wall time, PRIMARY clock: coordinator-observed, from executor process launch (first codex spawn) to the coordinator receiving the executor final report message. Pre-flight diagnose time and infra start time are excluded from execution wall and recorded separately per arm. Executor-recorded start/end is secondary (diagnostic). If the two clocks disagree by more than 60 s, the report must explain it before any verdict.
- Driver commands run: counted mechanically from out.log, only between the executor's new_session and delete_session lines (session-boundary counting). The executor report (one line per action, required by both briefs) is the primary count; out.log is the cross-check. Pre-flight commands are excluded by range. out.log is archived per arm (out-a.log, out-b.log) before the next infra start; never truncate without archiving.
- Tool calls: from the per-arm codex --json event file (events-a.jsonl, events-b.jsonl), completed command_execution items only. Report-writing calls are counted separately. One driver command per tool call (pinned in both briefs).
- Tokens in/out per executor, from the event stream or final message. Reported alongside wall time. A speed win does not imply a cost win.
- Error INCIDENTS: one root-cause driver failure (one {"ok": false} result) plus every recovery action it triggered (re-find, retry, click_js fallback), counted as ONE incident. Category table (disjoint, each event counted once in exactly one category):
  - Error incident: one {"ok": false} result and all recovery it triggered.
  - Check failure: a check read differing after its one retry.
  - Misclick: a click that SUCCEEDED on the WRONG element (wrong target clicked). A failed click is an error incident, not a misclick.
  - Recovery steps (cost, not burden): retries, re-finds, fallbacks. Reported separately, never added to the burden.
- Accuracy burden per arm = check failures + error incidents + misclicks, each counted once with step numbers.
- PASS/FAIL: decided ONLY from the fixed final-read list (identical for both arms, see below) plus window.__agyVerify() returned JSON, read from out.log by the independent judge, never from an executor claim.
- B only: plan deviations + PLAN DEFECTs, each with plan step number.
- Pre-flight diagnose result per arm (full JSON saved to /tmp/e1/preflight-a.json, preflight-b.json).
- Per-arm state: Zen uptime, time since the last Marionette session, load average, running live processes at arm start, infra restart times, inter-arm gap.

## Fixed final verification (identical for both arms)

Before tab close, each executor performs the same fixed read list (B's plan steps 48-56 already contain it; A's brief now mandates the identical list):
banner text (expect "Directory saved: 6 contacts (1 favorite)"), visible count (expect "6"), search value (expect ""), group value (expect "all"), Bob phone (expect "+1-555-9999"), David favorite DOM read (starActive true, cardFavorite true), Spam Bot absence read (cardPresent false, namePresent false), Frank DOM read (cardPresent true, name "Frank Sinatra", group "Engineering", email "frank.s@example.com", phone "+1-555-0106", notes "Vocal Architect"), window.__agyVerify() (PASS requires passed: true, failures: [], score: 1, state equal to {"saved": true, "contactCount": 6, "favCount": 1, "bobPhone": "+1-555-9999", "banner": "Directory saved: 6 contacts (1 favorite)"}).
PASS requires every fixed read to match AND the __agyVerify conditions. The judge reads these values from out.log, not from the executor report.

## Pre-registered win criteria (frozen BEFORE either arm runs)

- SPEED (total, headline): B wins ONLY if B total (642 s sunk + B execution on the primary clock) < A total (A execution on the primary clock). Otherwise B does not win on total speed, whatever B execution alone shows. "Does not win", not "loses".
- ARITHMETIC EXPECTATION (stated now, not discovered later): B total is at least 642 s. The spec puts this task at 150 s expected and 260 s maximum. B wins total speed only if A execution exceeds 642 s plus B execution, that is, only if A takes more than about 10m 40s on a task whose own max is 260 s. A total-speed win for B is therefore unlikely by arithmetic. The decision-relevant speed question is execution-only speed (below) plus the break-even task length: the task length at which the execution saving would repay the 642 s overhead. Both are reported; neither is hidden.
- SPEED (execution only, decision-relevant): reported separately. If B execution < A execution but B total > A total, the verdict is: execution faster, total slower. That is a partial result, not a win. The headline speed verdict is always the total-speed verdict. The execution-only number is reported second and is never headlined as a win.
- Meaningful-difference threshold: a wall-time difference under 60 s on the primary clock is "no detectable difference", not a win, on either speed bar.
- ACCURACY: B wins ONLY if (B passes and A fails) OR (both pass AND B has strictly fewer burden AND B has zero material deviations AND the burden difference is at least 2). A wins ONLY on the mirror condition (A passes and B fails, or both pass and A has strictly fewer burden by at least 2). Equal burden when both pass is a draw. A burden difference of exactly 1 is a draw (within noise at n=1), not a win.
- Material deviation (B): any step where the executor used a different selector, order, or value than the plan, except retries and fallbacks the plan itself allows. Re-finding an element after a re-render, when the plan instructs it, is not a deviation. If B passes with a material deviation, the accuracy verdict is "B passed by improvisation, not by the plan; no deliberation win", with the deviation quoted by plan step number.
- PLAN DEFECT: a plan step impossible as written after the allowed retry (selector not found, or a check differing after retry because the plan's expected value is wrong). Defects are classified separately and are NEVER counted as B executor errors. If B fails and the failure traces to a single plan defect, the accuracy verdict is "plan defect, not a deliberation loss; comparison inconclusive on accuracy", with the defect recorded by plan step number. If it traces to executor error, B loses on accuracy.
- Both fail: no accuracy win is awarded to either arm. Report steps completed before the first unrecovered failure, failed-check count, earliest failing step, and final verifier state for each arm, and state which arm got further. A flat draw label for two failures at different depths is forbidden.
- A FLAGGED pass (pre-flight cleared spontaneously during the poll, or executor-tab diagnose needed no intervention) is a pass, but a flagged pass cannot win on accuracy over an unflagged pass. A manual-removal-assisted start never happens (see pre-flight section).
- VERDICT: "faster?" and "more accurate?" are answered separately. No single blended score. No headline may say "deliberation wins" or "deliberation loses" outside the scoped sentence: "On test-05, this run, [B total vs A total on the primary clock; accuracy burden A vs B; PASS/FAIL per arm]." Any wider claim is forbidden from this run.

## Pre-flight diagnose (read-only gate + executor-tab diagnose)

Pre-flight is a GATE, not a test. It runs per arm, after infra start, before the executor launches.

- Per-arm infra checklist (coordinator, recorded in the arm report, before pre-flight): Zen PID alive (re-checked at run time, not the 18:24 snapshot), ports 4451/8767 owned by E1 or free, no foreign geckodriver, fixture HTTP 200, Y4d complete, handover in force, single live runner (no other runner active).
- Pre-flight diagnose (coordinator, via worker-y8-preflight.py): one fresh tab via the E1 driver to the fixture URL, 1.0 s settle after new_tab, one eval, one snapshot (diagnose_body): readyState, documentElement classList (tz-hidden, tz-initialized), htmlInline, bodyClass, bodyInline, body computed visibility/opacity/display, html visibility, transition property/duration/delay (collected as a stated diagnostic only; V2 is dead), body rect, innerText length (corroboration only), hasFocus, visibilityState, URL, countText. Sample twice 300 ms apart when hidden. Full JSON saved per arm. Pre-flight commands are excluded from arm counts by session-boundary ranges.
- Classification: VISIBLE (body visibility visible AND opacity not "0" AND display not "none" AND countText present), TZ_STUCK_V1 (tz-hidden present), OTHER_HIDDEN (class absent, computed hidden), FIXTURE_FAILURE (fixture failed to load: HTTP error or countText null). readyState not complete means do not classify as hidden yet; wait for load first.
- Recovery ladder, 8 s wall-clock deadline (enforced in code): poll 250 ms up to 2.0 s for the extension's own removal. If V1 persists, run the single removal eval ONCE as a DIAGNOSTIC (test tab only, test origin only, logged), wait at least 600 ms, re-diagnose once. If the tab becomes visible after removal, record "V1 CONFIRMED (manual removal unhid this tab)" and declare INFRA-BLOCKED. Do NOT start the arm. If the tab is still hidden after removal, the hiding mechanism is not V1; classify OTHER_HIDDEN and declare INFRA-BLOCKED.
- FLAGGED (proceed) applies ONLY when the tab cleared by the extension's own removal during the poll, with no manual intervention. A manual-removal-assisted visibility NEVER authorizes a start.
- Pre-flight warming is a known confound, stated here: opening a tab warms the driver, the fixture server, and the extension's content-script chain, so hidden-body incidence in E1 is a lower bound, not a true rate. The hidden-body defect is therefore unmeasured by this experiment, not absent.
- Executor-tab diagnose (executor's first step after new_tab, mandated in both briefs, exact JS in the brief): the executor runs the diagnose eval on its OWN tab and proceeds past step 1 only if that diagnose is VISIBLE. If the executor tab is hidden, the executor stops immediately, records INFRA-SUSPECT with the read values, and the arm is INVALID (INFRA), not a FAIL. The coordinator classifies the saved JSON (V1 vs OTHER_HIDDEN vs FIXTURE_FAILURE). A removal eval on the stopped tab is permitted only as a diagnostic probe to classify the incident; the tab is left open for later inspection, not closed by the executor, and the arm is never resumed on that tab.
- No real click is used as a recovery probe. Never touch a user tab. Never dismiss the open alert on any user tab.
- V2 (transition frozen) is DEAD and is not a category: class-absent plus computed-hidden is OTHER_HIDDEN.

## Invalid-run rules (one retry budget per arm, total, across all causes)

- Max 2 starts per arm. A second start, if any, is labelled A2 or B2 in every table and every verdict sentence. It never silently replaces A1 or B1.
- Pre-start INFRA-BLOCKED (pre-flight diagnose fails before the executor issues its first driver command, zero executor steps attempted): the arm does not start. The block is recorded with the full diagnose JSON. One retry is allowed after at least 10 minutes, timed from the failed diagnose timestamp, and only after a fresh clean pre-flight. If the second pre-flight also fails, the arm is INFRA-BLOCKED and the comparison is ABORTED: each arm is reported as it stands (a completed arm stays completed, a blocked arm stays blocked). Never relabel a completed clean arm as blocked. Never compare one measured arm against nothing.
- Post-start INVALID (crash, DRIVER DEAD, mid-run hidden body, or any stop after the executor's first driver command): the first started run IS the arm's result for accuracy. If the executor never reaches final verification, the arm is recorded as FAIL (incomplete), with the partial step reached, the failed checks so far, and the crash or timeout evidence. A re-run, if the coordinator judges it worth doing, is a second observation (A2/B2) reported alongside A1/B1, never a replacement. No accuracy or speed win may be claimed from a second observation alone; a win requires the first observations to support it, or requires both observations to agree.
- DRIVER DEAD: two consecutive step.sh failures of any kind (timeout or immediate error, including "fifo missing"), not only timeouts. Before declaring DRIVER DEAD, the coordinator must check the driver process is alive, the geckodriver process is alive, and port 4451 answers, and must log those three checks. If the driver is alive, the event is a timeout, not a death, and the arm continues or fails on its own evidence.
- MID-RUN HIDDEN BODY: if the executor tab goes hidden mid-run (executor reports body hidden on its own tab, or two consecutive type/click steps fail and a diagnose on the executor tab shows hidden), the executor stops, the coordinator diagnoses the executor tab and classifies it, and the arm is INVALID (INFRA), not a FAIL. It is re-run once from scratch under the single retry budget. The partial run is logged, never counted.
- FIXTURE_FAILURE (pre-flight exit 3, fixture HTTP error, or missing #contacts-count): neither INFRA-BLOCKED nor a FAIL. It stops the run. The coordinator re-verifies the fixture file and the HTTP server, fixes or restores them, then re-runs pre-flight from scratch. It does not consume the INFRA retry.
- Ambiguous timeouts: a click on Save or Delete can succeed in the browser while its response is lost. Clean failures (element not found, error proving non-execution) may retry once. Ambiguous timeouts must re-read state first (eval the DOM) and retry only if the state shows the command did not take effect. Every ambiguous timeout is recorded separately.
- Second crash of any kind ends the arm as BLOCKED. Before any re-run, inventory Zen tabs and close only the crashed run's tab (or record that it is already gone).
- Retry waiting time and failed-attempt wall time count toward the arm's total wall time. A retry is never free time.
- A retry executor is a fresh codex process that must not see the previous attempt: it must not read the previous run report, the previous out.log, or any coordinator note about what failed. Fresh report filename (run-a2-report.md, run-b2-report.md).
- If either arm needed an infra retry or any recovery-ladder intervention, no clean win or loss is claimed on either criterion. The result is reported as an observed difference, confounded by browser health, with the pre-flight evidence attached.
- Inter-arm gap: record A end to B start. If the gap exceeds 60 min, re-verify the frozen inputs by md5 before B starts and record the gap in the B report. A gap over 60 min does not invalidate the comparison by itself, but it must be disclosed in the verdict.
- Tab acquisition: fresh tab via the E1 driver for both arms. NO fallback method. A fresh-tab failure blocks the arm (INFRA-BLOCKED). The Y4 bootstrap tab is not used; its evidence is n=1 confounded by time.
- Infra: restarted between arms (fresh driver, fresh HTTP server, fresh session), with start times recorded per arm. The pre-flight uses its own session, deleted before the executor launches, so only one session ever exists at a time (single-session rule).

## Independent judge (blinding)

- The coordinator (Y8) runs infra and both arms. The JUDGE is a fresh subagent who decides PASS/FAIL, burden, deviations, defects, and invalidity from arm-stripped evidence.
- After both arms complete, Y8 renames the artefacts to run-p and run-q (mapping held only by Y8), and the judge receives: run-p and run-q reports + out.log ranges + event files, the plan file, the spec, the fixed final-read list, and the classification rubric below. The judge does not know which run is A or B.
- The judge's verdict is committed unedited before Y8 maps p/q back to A/B. Y8's verdict must cite the judge's file and the report lines it rests on, so a second reader can audit every call.
- Classification rubric (pre-registered, for borderline cases):
  - Timeout vs DRIVER DEAD: two consecutive step.sh failures of any kind + the three liveness checks logged. Driver alive means timeout, not death.
  - Hidden tab vs FIXTURE_FAILURE: countText null or HTTP error means FIXTURE_FAILURE; countText present and hidden means INFRA (V1 if tz-hidden present, else OTHER_HIDDEN).
  - Deviation vs PLAN DEFECT: a step the executor could not execute as written after the allowed retry is a PLAN DEFECT; a step the executor chose to do differently is a deviation. A retry or fallback the plan itself allows is neither.
  - Error incident boundaries: one {"ok": false} plus all recovery it triggered is one incident. A check differing after its retry is one check failure. A click succeeding on the wrong element is one misclick.

## Known confounds (stated now, not discovered later)

- Order effect: A runs first, B second. Zen/driver warm state could favor B; a hidden-body window could hit either arm. Pre-flight results per arm are the record of this. Infra is restarted between arms to reduce the warmth gap. Pre-flight itself serves as the warm-up round-trip; no separate warm-up is run.
- n=1 per arm: one run each, one task, one model. This is ONE observation, not proof of a general effect. Any verdict is scoped to "this task, this run".
- Executor nondeterminism: same model and settings, but codex runs are not deterministic. A second A run could differ. This is a stated limit, not a fixable one at n=1.
- Task selection favors B: test-05 was chosen for its varied decision surface (modal add, edit, star, delete, search, group filter, save) precisely because deliberation has more room to matter there. A B win here is a win on a deliberation-friendly task. Generality would need a second task (for example test-09, linear timer flow) and is out of scope for this run.
- Granularity: the plan has 58 steps and 64 JSON commands for a 28-step spec. B runs one driver command per plan step (stated in the B brief; batching across a check step is forbidden). A decides its own granularity. Driver-command counts are therefore reported alongside wall time and checks performed, never compared raw without the granularity caveat. Error counts are rates where the formula uses them (burden is a count of distinct failures, not of commands; see the category table).
- Click policy is shared: real click first, click_js only after a real-click retry fails (in the driver reference both briefs read). Exception, plan-given: plan step 31 uses click_js directly on the star. That is a plan command, not an executor choice, and is recorded as a known plan-given difference.
- Information asymmetry is the treatment, not an accident: B's plan hands it pre-verified runtime facts A must extract live (Bob's preloaded phone, star is a span, delete has no confirmation, select by JS value plus change, search live on input, exact banner text, slug rules, lastElementChild reads, notes selector). A B win is a win for the bundle including those facts, not for deliberation in the abstract.
- Plan assertions are labelled: static-verified (read from fixture HTML) vs runtime-guessed (decided by 2-1 deliberator vote, untested live). The two voted guesses are: explicit input-event dispatch after clear (draft-3 wins), and no re-find of the phone input after clear (draft-1/3 win over draft-2). If a voted guess is right, B's accuracy win is partly luck; if wrong, B eats a plan defect. The split is visible in the report.
- Codex cached context: X's report notes delib-1 consumed 198,978 input tokens "because codex loads large cached context per run". The design asserts a fresh codex process has no memory of other agents, but offers no proof. Mitigation: record input-token counts per executor; audit event streams for reads of forbidden paths; state plainly that isolation is attested by the audit, not independently proven.

## Replication trigger (pre-registered)

Stage 1 is the n=1 pilot (A1, B1). Its verdict language is frozen to pilot language (see the win-criteria section). A second pair (B2, A2, swapped order) is run before any comparative verdict beyond pilot language if ANY of these holds: the arms split PASS/FAIL; total times differ by less than 2 min on the primary clock; accuracy burden difference is 1 or less; either arm is flagged or invalid; the coordinator's independent error count disagrees with either executor report by more than 2; execution wall times differ by less than 20 percent. If none holds, the pilot verdict stands as a pilot verdict and the replication is recorded as not triggered, not as unnecessary. If a second pair runs, its order is B then A (ABBA overall), same briefs, same plan file (same md5), same tab-acquisition method, and its results are reported as a second pair, never merged into a single average with the first pair without showing both pairs separately. The second pair runs only in a fresh handover window, not by extending a window that has already closed.

## Infra (Y8 scripts, repo copies authoritative)

- Start: worker-y8-start-infra.sh. Verifies the sed port replacement (grep WD_PORT = 4451, exit non-zero if absent); fails closed if ports 4451/8767 are already bound or if PID files reference live processes (require a clean stop first); archives the previous out.log to a timestamped file before truncating; records holder, driver, HTTP PIDs with cmdline snapshots; verifies BOTH ports listening after the 3 s sleep and exits non-zero if either is missing; runs the per-arm infra checklist (Zen PID alive, no foreign geckodriver, fixture HTTP 200) and fails closed.
- Stop: worker-y8-stop-infra.sh. Kills by exact PID only, verifying /proc/<pid>/cmdline contains the expected string before TERM (holder, driver, HTTP server); verifies the holder is dead (kill -0) before killing the driver, so the driver's finally block can run; finds the E1 geckodriver at stop time by pgrep -x plus cmdline containing --port 4451, kills by exact PID only (never pkill -x geckodriver, never pkill -f); verifies ports 4451/8767 free and no E1 geckodriver remains before printing INFRA_DOWN. A geckodriver on another port (for example Y4's 4448) is not E1's and is never touched.
- The E1 driver (hand_drive_e1.py, built by sed from hand_drive.py) still has the orphan bug Y4b records (geckodriver stdout/stderr to DEVNULL, no PID file; a session POST timeout orphans the geckodriver because __exit__ never runs). Y8 does not patch hand_drive.py (shared with other workers); the manual sweep in the stop script is the cover, and the risk is recorded here.
- Deployed copies live in /tmp/e1/; repo copies under improvements/ are authoritative. The per-arm md5 re-verification covers the deployed copies.

## Files

- This design: improvements/worker-y8-e1-comparison-design.md (FROZEN v2)
- Briefs: improvements/worker-y8-executor-a-brief.md, improvements/worker-y8-executor-b-brief.md
- Driver reference: improvements/worker-y8-driver-reference.md
- Infra: improvements/worker-y8-start-infra.sh, improvements/worker-y8-stop-infra.sh, improvements/worker-y8-preflight.py
- Log: improvements/worker-y8-e1-execution-log.md
- Council + redteam: improvements/worker-y8-council-1.md, worker-y8-council-2.md, worker-y8-council-3.md, worker-y8-redteam.md
- Prior work: improvements/worker-x-e1-experiment-log.md, improvements/worker-x-e1-experiment-report.md, improvements/worker-x-e1-plan-test-05.md
