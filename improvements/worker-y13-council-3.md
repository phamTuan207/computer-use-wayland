# Council 3 verdict: Worker Y13 codex-y5 live plan v1

- Reviewer: Council Member 3 (thresholds + slot/queue + integrity guard)
- Date: 2026-11-21 ~19:25 +07
- Plan under review: improvements/worker-y13-codex-y5-live-plan.md (v1, 2026-11-21 ~19:20 +07)
- Runner under review: none yet (plan states council debate happens before the runner is written)
- Base checked: tests/realistic/run_agyq2.py at commit 1e3901c, tests/realistic/run_live.py at 1e3901c, tests/realistic/codex-y5/check.mjs, improvements/worker-y4d-rerun-log.md, improvements/worker-y9-agy-y2-live-plan.md (v2 + re-review round 2 fixes)
- Branch state at review time: todolist-push, HEAD f50a536 "Y8 E1: log pre-flight 2 driver death, infra restart, pre-flight 3 VISIBLE, arm A launch 19:17:04". Y8b is LIVE now. Y9 is in re-review, slot still Y8b (commit 2357a91).

## Verdict: APPROVE WITH FIXES

The plan's direction is right: frozen base 1e3901c, exclusive queued slot, fail-closed preflight, clean-only headline, integrity guard, no mid-run strengthening. But v1 is a summary, not a pre-registration, on exactly the points this council owns. Ten findings below are BLOCKING (must be pinned in plan v2 before the runner is written); the rest are notes. No live driving is affected yet, since the plan already forbids driving until Y6c completes and Muse says go.

Verified correct as written (evidence checked, not assumed):

- Base pin md5 84fa106c253d5e7f16daccf2ce3f14a5 matches `git show 1e3901c:tests/realistic/run_live.py`. Correct.
- Handover max age 4h matches HANDOVER_MAX_AGE_S = 4 * 3600 in run_agyq2.py line 72. Correct.
- Own ports are collision-free: server 8770, WD 4450, vs Y4d 8768/4448 and Y9 8769/4449; Marionette 2828 shared connect-existing. Correct.
- Y5 headless proof plus check.mjs verifyOneFixture (lines 159-171, throw on fresh pass; main lines 180-186, allPassed requires fresh_fixture_failed_as_expected) establishes all 10 codex-y5 fixtures fail verify fresh. The guard's expected outcome per test is a recorded failure list.

## 1. Thresholds: NOT COMPLETE

### F1 (BLOCKING): re-run accounting conflicts with the exit-0 rule

The plan allows one re-run per infra-blocked test, "logged with the attempt field", and states "Exit 0 iff clean + flagged == 10". It never states whether results[] holds one entry per test or one per attempt. The copied run_agyq2.py main() (lines 1501-1639) returns 0 iff total_passed == len(results). If the runner copies that rule and appends a summary per attempt, a suite with one infra-blocked attempt re-run to a pass has 11 results and 10 passes, so total_passed (10) != len(results) (11), exit 1 on a 10/10 test pass. If instead the runner implements the plan's own "clean + flagged == 10" rule, the failed superseded attempt is invisible in the exit code. Either way the plan must pick one rule and state the results-list semantics. Y9 v2 resolved this exact point (section 2 and section 7): superseded attempt-1 summary printed before the re-run, hidden-body encounters plus verified removals accumulated across attempts into the suite total with a superseded_attempts list, total_ms sums final attempts only while suite_wall_ms covers all, exit 0 iff clean + flagged == total. Y13 v1 carries none of that. Required fix: adopt the Y9 accounting verbatim, or write an equivalent and state which list the exit rule counts.

### F2 (BLOCKING): infra_blocked counting across a re-run is unspecified

Does the first INFRA still count toward infra_blocked? Does a successful re-run reset it to 0? Does a second INFRA on the re-run increment it again, so two consecutive infra-blocked attempts abort the suite? The plan is silent. Y9 v2 pins: first INFRA counts, successful re-run resets to 0, second INFRA increments again. Pin the same. Also pin that a guard-defect failure (see G3) has no effect on infra_blocked, and that the handover re-check runs before a re-run attempt, not only before first attempts.

### F3 (BLOCKING): flagged state across a re-run is unspecified

If attempt 1 needed a verified tz-hidden removal and attempt 2 passes clean on a fresh Runner, the per-attempt details lose the flag and the test reads clean. The copied ensure_visible sets r.details["tz_hidden_removed"] only when the post-remove snapshot proves the class is gone (run_agyq2.py lines ~430-445), and the copied main() flags from the final Runner only. A re-run can therefore wash a flagged pass into a clean pass. Required fix: accumulate verified removals and hidden-body encounters across attempts into the suite total with a superseded_attempts list, as Y9 did. A test that needed an intervention on any attempt is flagged, never clean.

### F4: exit-0 hardcodes 10; exit codes for failure paths are unstated

"Exit 0 iff clean + flagged == 10" hardcodes 10, but the copied main() supports subsets via argv. Y9 uses "== total (total, never a hardcoded 10)". State exit 0 iff clean + flagged == total, or state subsets are unsupported. Also state the exit codes the copied code already uses and the plan never mentions: preflight failure returns 2, bootstrap failure returns 2, handover abort mid-run returns 2 (run_agyq2.py lines 1501-1639: aborted_handover returns 2).

### F5: intermediate verifies are not pinned to r.step or r.check

The step-mapping table writes "r.step check", which blurs the two primitives in run_agyq2.py: r.step raises and aborts the test, r.check records and continues. The pass/fail outcome is the same either way (any failure fails the test at summary, since Runner.summary pass = len(failures) == 0, run_live.py lines 902-906), but the evidence trail and the abort path differ. Required fix: pin r.check for intermediate verifies (recorded, continue) and r.step for actions, as Y9 did. Do not leave it to the runner author mid-write.

### F6 (BLOCKING): norm() for intermediate verifies is not frozen pre-run

The plan says any intermediate verify needing norm() "must be recorded as a deviation with the reason; never silently". That lets the runner decide mid-run to switch from exact trimmed textContent to norm(). The norm() step list must be frozen BEFORE driving, from reading the fixtures (the only known case class is template-literal whitespace, Y4d q06). Any step needing norm() mid-run that was not pre-registered is a checker finding, not a pass-with-deviation.

### F7 (BLOCKING): no checker-bug path

The re-run rule covers only infra-blocked tests. The most likely mid-run discovery is a checker bug (Y4d run 1 failed q02/q06 on checker bugs, fixed the checkers, ran the full suite again as run 2, 10/10; see worker-y4d-rerun-log.md). Y13's plan states no handling for this case. Required fix: on a checker bug, the test fails, the suite completes (or aborts per the abort rule), the checker is fixed, and a fresh full suite run is required. A single-test re-run after a checker fix is NOT covered by the infra re-run rule and must not be used to manufacture a pass.

### F8: bootstrap intervention accounting is unspecified

The plan copies bootstrap_tab but never states that a tz-hidden removal during bootstrap is suite-level only and must not flag test-01. Y9 v2 section 2 pins this: per-test flagged stays False for tests run on a bootstrap-intervened tab; the bootstrap intervention is recorded only at suite level. The copied main() prints SUITE FLAGGED if flagged > 0 or boot_info tz_hidden_removed; the plan never mentions the SUITE FLAGGED headline. State both.

### F9: handover abort behavior and token path are unstated

The plan says the token is re-checked before every test but not what happens on expiry mid-run (copied code: print, aborted_handover = True, break, return 2). State it. The token file path for Y13 is never named (run_agyq2.py line 71 uses /tmp/worker-y4d-handover.json; Y13 must use its own path and must not reuse Y4d's). Y9 N5 fingerprint binding against mid-run token swap is not carried over. Minor, but name the path in v2.

### F10: evidence hygiene gaps carried from neither Y4d nor Y9

The plan says "per-step JSONL at LIVE_LOG" with no rotation rule. Y9 rotates the JSONL at launch (existing file renamed to .prev-<timestamp>, rotation logged). Without rotation, a stale LIVE_LOG from a prior run mixes into the evidence. Add rotation or a fresh per-run path. The plan also has no --verify-manifest dry-run flag (Y9 B3) and does not state that manifest verification is the first thing in main(). Add both. The plan states the WD-timeout classification ("A 30s WD HTTP timeout is INFRA; a wait_for timeout is a live failure") but not the match wording Y9 fixed in re-review ("timed out", TimeoutError/URLError); a wrong-string match misclassifies WD timeouts as live failures. State the wording.

### F11: mid-test hidden-body reclassification is broader than Y9's narrowed rule

The plan says "A hidden body found mid-test (on any step failure) is INFRA, not a step failure." Y9 re-review narrowed this: reclassification only for TZ_STUCK_V1 / OTHER_HIDDEN; FIXTURE_FAILURE and UNKNOWN stay live failures (C3 F4). The blanket rule can misclassify a FIXTURE_FAILURE diagnosis as INFRA, which would then allow a re-run for what is actually a fixture problem. Narrow it to the two hidden-body classifications.

## 2. Integrity guard: UNDER-SPECIFIED, fail-open on error outcomes

### G1 (BLOCKING): only one of three guard outcomes is specified

The plan says "the SAME ported verify runs on the untouched fixture before steps; a pass there is a SUITE DEFECT, the test fails, never passes." It never states what happens on fresh-ERROR (ported verify eval raises, e.g. Marionette error or timeout) or fresh-TIMEOUT (30s WD HTTP timeout during the guard eval). In check.mjs, a fresh-verify throw propagates and verifyOneFixture throws (check.mjs lines 159-171; main catches, exit 3). The live port must specify all three outcomes:

- fresh-fail (expected): proceed, with the untouched failure list recorded as evidence.
- fresh-pass: FAIL the test as a suite defect (see G3 for counters).
- fresh-error / fresh-timeout: FAIL the test as guard-inconclusive, suite continues, and NEVER treat it as "guard held, proceed".

If the runner swallows a guard exception and proceeds, the guard fails open and a defective fixture (or a broken ported verify) can pass the suite. This is the sharpest fail-open hole in the plan.

### G2 (BLOCKING): guard scope, position, and re-execution are unspecified

"Runs on the untouched fixture before steps" never says explicitly "once per test" (one per fixture, since each test has its own fixture) nor "re-executed on any re-run" (Y9 v2 pins both). The guard's position in the sequence is unpinned: it must run after open_fixture (goto plus clear storage plus reload plus ladder) and before any workflow action, through the SAME ported verify code path as the final verify. Pin the position (after the body-visible check, before step 1 of the workflow) and require the untouched failure list to be recorded per test as evidence.

### G3: guard-defect effect on counters and suite flow is unspecified

Y9 pins: a guard-pass failure has no effect on the infra_blocked counter and the suite continues to the next test. Y13 says "the test fails, never passes" but not whether the suite continues or aborts, and not the infra_blocked effect. State both: suite continues, infra_blocked unchanged.

### G4 (BLOCKING): the ported verify's return-value handling is unspecified

Y4d proved live at 18:45 that Marionette /execute/sync runs a script as a function body, so a bare IIFE discards its value and eval returns None (the _DIAG_JS bug; fixed with a top-level `return`). The ported verify is a large eval and the plan never requires (a) a top-level `return` in the ported script, (b) a None or non-dict result from the verify eval to be treated as a verify FAILURE (fail closed), never as 0 failures, (c) one live eval proof of the ported verify before the suite trusts it (Y4d finding 3: "a diagnose helper needs one live eval before the suite trusts it"). The plan's only self-check is "headless self-check of the runner's Python only", which cannot catch a Marionette eval return bug. Note the guard mitigates an always-pass port (a fresh pass trips the defect), but only if G1's error handling is fail-closed. If a None result is treated as pass in the final verify AND a guard None is swallowed as "held", the suite can report passes that are not passes. Require the None guard in code and a live eval smoke test of the ported verify on one fixture before the suite runs.

### G5: state the expected guard outcome explicitly

check.mjs verifyOneFixture (lines 159-171) throws on fresh-pass and its main() requires fresh_fixture_failed_as_expected for allPassed (lines 180-186). Y5's headless proof (10/10, commit 3c7c875) therefore establishes that all 10 codex-y5 fixtures fail verify fresh. The plan should state this expected outcome per test so a guard that passes on any fixture is immediately recognizable as the defect case.

## 3. Slot / queue: ORDER CORRECT, GATE INSUFFICIENT AS SPECIFIED

### S1: queue order confirmed correct

Brief order: Y8b E1, then Y9 agy-y2, then Y11b proof, then Y6c nested, then Y13 codex-y5. MEMORY.md 19:15 lists "Y8b E1, Y9 agy-y2, Y11 proof, Y6b nested, Y13 codex-y5"; the Y6b note (19:16) states the nested run is done by a new agent Y6c. Y13 after Y6c is correct. New since the plan was written: MEMORY.md 19:20 adds Y14 batch-3 live AFTER Y13 (queue now ends ... Y13, Y14). Consequence for Y13: it must define its own exact completion marker so Y14 can gate on it, and must leave the slot clean (tab cleanup to about:blank, no leftover processes). The plan defines no completion marker for itself. Add one in v2.

### S2 (BLOCKING): no exact Y6c completion marker is defined

The plan says "I poll todolist-push for Y6c's completion marker" but never defines the marker. Y9 section 5 defines it exactly: a commit after a given hash matching regex ^Y8 E1: .*execution complete, plus a log line naming both arms, plus direct verification of the earlier predecessor. Without an exact marker, Y13 can misread a Y6c progress commit as completion (false go, two runners live) or wait forever on a marker that never takes the expected form. Required fix: define the marker (commit message pattern, log file plus line) and what counts as completion vs abort (Y9: an ABORT marker frees the slot only after the launch-time live checks pass).

### S3 (BLOCKING): the runner-quiet process check is named but not specified

The plan lists "poll marker + runner-quiet process check + Muse's go order" with no order, no commands, no port list, no abort rule. Given the flock does NOT coordinate between runners (only Y4's run_agyq2.py enforces it in preflight; Y9 enforces it too by copying the check and launching under flock; Y11b and Y6c are unverified), these launch-time checks ARE the gate, and they must be written down. Exact checks the launcher must do, in order:

1. git fetch plus confirm the exact Y6c completion marker on todolist-push (see S2).
2. Confirm no other runner processes on the laptop: no run_*.py processes other than self, no live geckodriver with a live parent. Note the preflight sweep covers the geckodriver case, but the launch-time check must run BEFORE flock, since a predecessor between WD sessions has no live geckodriver and the sweep would miss it.
3. Predecessor ports free: TCP connect must fail to Y9's 8769/4449 and Y8b's 4451/8767 (per Y9 plan section 5), plus Y11b's and Y6c's ports once their plans name them. Y6c's nested probe may not use geckodriver at all, so port checks may not exist for it, which makes the process check plus marker plus Muse go order load-bearing for Y6c. State this explicitly.
4. Muse's go order at run time, fresh, not inferred from the queue position.
5. Launch under flock -w 60 on zen_dom.lock. If flock -w 60 times out after the marker is confirmed, ABORT the launch and report (Y9 section 5). Never wait silently. The plan states the flock launch but not the timeout-abort rule.
6. Preflight (fail-closed), which re-verifies the flock ancestor plus the orphan sweep.

Also record that Y8b is live RIGHT NOW (arm A launched 19:17:04, HEAD f50a536), so any launch-time check run today must fail: Y8 ports must answer and the marker is absent. That is the negative control for the launcher to verify before Y13's turn.

### S4 (BLOCKING): no poll cadence or poll timeout

Y9: cadence every 15 minutes at most, timeout 4 hours after the predecessor marker, then report to the parent instead of launching. Y13: no cadence, no timeout. If Y6c never completes, Y13 waits silently, violating the never-wait-silently rule. Add cadence plus timeout plus report-to-Muse rule.

### S5: the transitive-queue assumption is unstated and unverified

"After Y6c" frees Y13 only if every earlier link actually gates on its predecessor. Y9 gates on Y8 explicitly; Y11b gating on Y9 and Y6c gating on Y11b are not verified in this review. Y13 must not rely on transitivity alone: the launch-time live checks (S3) must pass regardless of queue position. The plan's direction is right ("the queue is coordinated by Muse" plus runner-quiet plus go order) but the checks are the real gate and they are unspecified.

### S6: stale-runner race

A predecessor that crashed between WD sessions leaves no live geckodriver (the sweep misses it) and may leave a stale HTTP server holding its port. Y13's own ports differ, so there is no collision, but the stale server is evidence the predecessor did not finish cleanly. The port-free checks in S3 catch the stale server; the process check catches a stale runner process; the marker plus Muse go order cover the rest. The plan's preflight alone does not cover this case, because the orphan sweep only looks at geckodriver PID files.

### S7: predecessor ports to check are never listed

Y13's own ports are collision-free (verified above), but the plan never states which predecessor ports the launcher must probe. List them in v2 (Y9 8769/4449, Y8b 4451/8767, Y11b and Y6c ports to be confirmed from their plans).

## 4. Handover / preflight copy: NAMES MOSTLY PRESENT, DETAILS COMPRESSED

The plan's preflight summary compresses run_agyq2.py preflight (lines 1323-1500) to one line. Line-by-line comparison against the copied base:

Present in the summary: handover token, BiDi 9222, Marionette 2828, Hyprland SAFETY gate, fixture server, orphan sweep, flock ancestor. The copied-function list also names _check_handover, _hyprland_signature, start_server, rebootstrap_tab, ensure_visible, _recheck_shared_tab, open_fixture, bootstrap_tab, preflight, main. Good.

Dropped or compressed to the point of unverifiability (each is load-bearing in the base):

- (a) BiDi probe is GET / expecting 200, NOT /json/version (404 on Firefox/Zen; Y4d caught this live at 18:40). Plan says only "BiDi 9222".
- (b) Marionette check is a TCP connect only; the real protocol probe is the session POST in WD.__enter__. Plan does not state this.
- (c) Hyprland signature is the TWO-SOURCE function (environ, then socket-dir newest-first, each verified by AF_UNIX connect; run_agyq2.py lines 89-138). Y9 B1 proved the environ-only rewrite FAILS live on this laptop (18:40). Plan says only "Hyprland IPC SAFETY gate" and never names the two-source function. If Y13 rewrites instead of copying verbatim, this is a known live-failure trap. Name it in v2.
- (d) Orphan sweep refuse rules: ppid None REFUSES rather than kills (C3 F3, run_agyq2.py lines ~1460-1475); live parent REFUSES; orphan gets SIGTERM, 1s sleep, then cmdline re-verified to contain geckodriver before SIGKILL (pid-recycling guard). Plan says only "sweep by PID with parent check". Y9 N11 adds cmdline re-verification before SIGTERM too; not carried over.
- (e) Lock check accepts POSIX, FLOCK, OFDLCK and WRITE (run_agyq2.py lines ~1490-1500); requiring POSIX alone fails every correct launch (C3 F1, Y4d council 3 BLOCK). Plan says only "flock held by an ancestor". State the accepted lock types and that the ancestor set includes os.getpid().
- (f) _ppid_of parses /proc/<pid>/stat after the last ")" (run_agyq2.py lines 76-88, C3 F7). Not mentioned.
- (g) Idle time is NOT independently verified; the token records basis plus timestamp (run_agyq2.py lines 139-165, _check_handover docstring). Plan does not state this limitation.
- (h) Fixture server probe must probe Y13's OWN fixture (test-01-git-workflow.html on 8770), not the copied agy-q2 probe path (Y9 section 3: "the copied agy-q2 probe is NOT reused verbatim"). Plan says only "fixture server".
- (i) Handover re-check before every test with abort returning 2 (run_agyq2.py main lines 1520-1529). Plan mentions the re-check, not the abort/return code (see also F9).
- (j) Session-creation failure discrimination: only a failure to CREATE the session counts toward wd_failures; a step failure inside a test contains "/session/<id>/..." in its URL and must never count (run_agyq2.py main lines 1530-1555; this bug aborted the first Y4 run after 2 tests). Plan says "session-creation failures use the separate wd_failures counter" but never states the URL discrimination mechanism.
- (k) wd_failures resets to 0 after a successful session creation (run_agyq2.py line ~1590). Plan does not state the reset.
- (l) Suite-end tab cleanup: every registered test tab returned to about:blank (run_agyq2.py lines ~1625-1639). Plan silent. This matters now that Y14 queues after Y13.
- (m) _recheck_shared_tab after an INFRA failure (RT H5, run_agyq2.py lines 472-493) is named in the plan's copy list. Present. Good.
- (n) bootstrap_tab fresh-tab-only, no handle scanning (C2 F6, run_agyq2.py lines 1282-1321): pre-existing fixture tabs NOT reused; the tab is kept out of opened_tabs and registered in _TEST_TABS. Plan lists bootstrap_tab in the copy list but never states the no-reuse / no-scan rule in text. It is carried by the code copy, but the plan should state it, since Y4d finding 1 shows the shared tab does not survive its session anyway ("shared tab gone, rebootstrap" printed 10/10 in both Y4d runs).
- (o) The plan's copy list does not name diagnose_body / _classify_snapshot / _diagnose_or_raise / WD.__exit__ park, though the park pattern is described in text ("Sessions exit parked on a sacrificial about:blank tab (Y9 park pattern)"). The _DIAG_JS top-level `return` requirement (G4) is the load-bearing part of the diagnose layer and is nowhere in the plan.

Overall on the copy: the function NAMES are mostly present, but the plan is a summary, not a line-by-line spec, for at least 10 load-bearing details above. That is acceptable ONLY if the runner is produced by verbatim copy plus a line-by-line diff review against run_agyq2.py at 1e3901c before any live driving. The plan must state that review gate explicitly (Y9's v2 did: "a FRESH re-review of the runner code is still required before any live driving"). Y13's plan has no runner-review gate; it only lists council questions. Add it in v2.

## 5. Test-04 step 22 (known weak check): CONFIRM the plan's handling, with two conditions

Step 22 verifies #selected-route-summary is "No route selected" and #saved-route-summary is "No saved route". Step 2 of the same spec lists exactly those two strings as the FRESH-LOAD defaults. So step 22 passes on a fresh load and cannot distinguish "reverse cleared the state" from "state was never set". It is vacuous as evidence for the reverse action. The plan's "note it, do not strengthen" is correct, because the weak step cannot manufacture a pass:

- The test passes only if ALL steps pass AND the ported verify passes.
- The reverse action itself is pinned by step 21 (origin/destination swapped, checked immediately after the click) and by the end-state verify (check.mjs test-04: origin "Workshop District", destination "Harbor Square", selected "North Loop | 14.2 km | 24 min | No tolls", saved "Workshop District to Harbor Square | North Loop | 14.2 km | 24 min | No tolls"), which fails if the reverse never happened.
- Steps 19/20 (save), 25/26 (re-select, re-save), and 27 (final checks) must all pass as well.

Two conditions the plan should add in v2: (1) the final report must not cite step 22 as evidence that reverse cleared anything; the evidence for reverse is step 21 plus the final verify. (2) If the fixture is reloaded mid-test (rebootstrap path in open_fixture), step 22 passing after a reload is doubly vacuous, and the report must note any reload that happened before step 22. The plan's pre-registration ("expected to pass trivially") is the right handling; these conditions keep it honest.

## 6. Per-test wall cap: RECOMMEND A HARD CAP AT SPEC MAX

### V1 (BLOCKING): "no fixed cap" is a gap

The plan says "Suite wall time is reported, no fixed cap (specs allow 210-420s per test; the live run is expected far under that)." Two corrections:

- The range is wrong. Spec Timing sections give expected 210-300s and maximum allowable 330-420s per test (test-02 max 330s; test-06 max 420s; most 360s; test-05/10 390s). The plan's "210-420s" conflates expected with maximum. Correct ranges: expected 210-300s, max 330-420s.
- Y4d live per-test times were about 4.8-5.6s (run 2 total 49,885 ms for 10 tests), so a cap at the spec maximum has roughly 60-80x headroom and cannot false-trip on a healthy run.

Recommendation: per-test wall cap equal to that test's spec "Maximum allowable latency", enforced by a deadline check in main (not by trusting each call's timeout). On trip, abort the test. Classification on trip: INFRA if a WD call is outstanding past its 30s HTTP timeout or the browser is unresponsive, else live failure; record which call was in flight and the elapsed time. Without a cap, the only suite bound is the 4h handover token age (HANDOVER_MAX_AGE_S = 4 * 3600, run_agyq2.py line 72), which is checked only BEFORE each test, never during one, so a single hung test can hold the exclusive slot until the token expires, and a pathological test (many calls each just under the 30s WD timeout) could run far past its spec maximum. Y9's v2 also had no per-test gate but stated the per-test worst-case bound (about 35-40s) and the 4h slot bound; Y13's plan states neither bound. At minimum the plan must state the worst-case bound and the 4h suite bound; my recommendation is a hard per-test cap at spec max.

### V2: state the suite wall expectation

10 tests at about 5s live is about 1 minute; at spec max it is about 60 minutes. The plan should state both so a slow run is recognizable as a slow run, not misread as a hang or as normal.

## Blocking fixes required in plan v2 (before the runner is written)

1. F1: re-run accounting vs exit-0 rule. Adopt Y9's superseded-attempt accounting verbatim or write an equivalent; state which list the exit rule counts.
2. F2: infra_blocked counting across a re-run (first INFRA counts, successful re-run resets, second INFRA increments).
3. F3: flagged state accumulates across attempts; a test that needed an intervention on any attempt is flagged, never clean.
4. F6/F7: freeze the norm() step list pre-run; add the checker-bug path (fail the test, fix the checker, fresh full suite run; no single-test re-run after a checker fix).
5. G1: specify all three guard outcomes; fresh-error/fresh-timeout fails the test as guard-inconclusive, never proceeds.
6. G2: guard once per test, re-executed on any re-run, positioned after open_fixture and before step 1, same code path as the final verify, untouched failure list recorded.
7. G4: top-level `return` in the ported verify, None/non-dict result treated as verify FAILURE, one live eval smoke test of the ported verify before the suite runs.
8. S2: exact Y6c completion marker (commit pattern, log file plus line, completion vs abort).
9. S3: exact launch-time checks in order (marker, runner-quiet process check, predecessor ports free, Muse go order, flock with timeout-abort, preflight).
10. S4: poll cadence plus poll timeout plus report-to-Muse rule.
11. V1: per-test wall cap at each test's spec maximum allowable latency.
12. Add the runner-review gate: fresh re-review of the runner code against run_agyq2.py at 1e3901c before any live driving. Plus S1: define Y13's own completion marker for Y14.

## Notes (non-blocking, fold into v2)

- F4: exit 0 iff clean + flagged == total; state exit codes 2 for preflight, bootstrap, and handover-abort paths.
- F5: pin r.check for intermediate verifies, r.step for actions.
- F8: bootstrap intervention is suite-level only; state the SUITE FLAGGED headline rule.
- F9: name Y13's handover token file path; consider Y9 N5 fingerprint binding.
- F10: rotate the JSONL at launch; add a --verify-manifest dry-run flag; manifest verification first in main(); state the WD-timeout match wording.
- F11: narrow mid-test hidden-body reclassification to TZ_STUCK_V1 / OTHER_HIDDEN only.
- G3: guard-pass failure has no effect on infra_blocked; suite continues.
- G5: state the expected guard outcome (fresh verify fails on all 10 fixtures).
- Section 4 items (a) to (o): restate the compressed preflight details in v2, or record explicitly that the runner is a verbatim copy plus a line-by-line diff review.
- Section 5 conditions: do not cite step 22 as reverse evidence; note any reload before step 22.
- V2: state the suite wall expectation (about 1 minute live, about 60 minutes at spec max).
