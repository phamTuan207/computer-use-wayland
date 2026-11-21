# Worker Y9 run plan: agy-y2 suite LIVE on Zen (independent) - AMENDED v2

- Worker: Y9 (Muse live runner)
- Date: 2026-11-21
- Task: run tests/realistic/agy-y2/ (10 tests) LIVE on the owner's Zen via Marionette, independently. The owner handed the machine over, is out of the house and busy, and ordered the whole process to run automatically per the Lauren Tan direction.
- Suite state: commit 30a72e5 on todolist-push. Y2 generated it, Y2b verified 8/10 with 2 defects, Y2 fixed both, Y7 independently verified both fixes CORRECT with redteam NO BLOCK (improvements/worker-y7-fix-log.md, commit a07fd27). Headless: simulate.mjs --all 10/10 PASS (247-393 ms per test per the Y7 log), check.mjs --all 10/10 FAIL on fresh fixtures. The live run is still owed and is this task.
- Queue: Y4d runs the agy-q2 rerun FIRST, then Y8 runs E1 conditions A and B. Y9 drives Zen ONLY AFTER Y8 reports completion. Prep now, poll todolist-push for Y8's completion marker (section 5, exact), do not drive while Y4d or Y8 is live. One live runner at a time, no exceptions.
- Slot status at plan time (18:3x 21/11): Y4d is in council revision (Council 3 BLOCK on preflight, Council 1 APPROVE WITH FIXES on diagnose layer; no rerun started, no geckodriver running on laptop, 8768 server alive, Zen alive with BiDi). Y8 design v2 frozen (commit 4a78f7f), waiting Y4d slot. Y9 polls.
- REVIEW STATUS (v2): the v1 plan (commit 6f20fb5) was reviewed by Council 1 (BLOCK), Council 2 (APPROVE WITH FIXES), Council 3 (BLOCK), Redteam (BLOCK). All four verdicts are in improvements/worker-y9-council-1.md, improvements/worker-y9-council-2.md, improvements/worker-y9-council-3.md, improvements/worker-y9-redteam.md. This v2 amends the plan ONCE for all four verdicts and writes the runner (tests/realistic/run_agy_y2.py) with every fix IN CODE. The v1 claim "fixes already applied" was FALSE (the runner did not exist and the base still carried the defects); v2 corrects that language everywhere. A FRESH re-review of the runner code is still required before any live driving (Redteam re-review gate); v2 does not claim the gate is passed.

## 1. What the run measures

- Each test: the spec's exact steps (test-01..10 .md files), driven through real Marionette clicks and keystrokes on the live Zen, with intermediate spec verifies recorded as checks and the final state verified by a 1:1 port of check.mjs verifyTest (same selectors, same expected values, including test-07 'Root: 5 files'). The port is JS executed through Marionette eval, copied from check.mjs verifyTest bodies; the diff audit is in improvements/worker-y9-step-mapping.md section 4.
- Per-step wall time (JSONL, with an attempt field), per-test elapsed, suite total wall time, steps per test, hidden-body encounters with diagnosis (htmlClass incl. tz-hidden or not, rAF tick count, same tab same minute).
- Y7's surviving doubts are tracked live, not gated, and each has a NAMED control in the runner (not a promise): (1) test-07 skip hole: closed by the step 24 check (trash-counter "1" AND #file-row-img4 hidden) and the step 28 check (trash-counter "0"), both PASS-gating r.check() calls; the final verify alone cannot detect skipping steps 23-29. (2) test-09 rename-branch bypass off-spec: closed by the step 33 body check (pinned value "Milk, Eggs, Bread, Apples"); the rename rule is precisely "never save with title Shopping while the archived note is active" (the step 7 save MUST use the rename branch, it creates the 'shopping' key). (3) test-07 Root count depends on the moved set excluding img4: the move set is exactly img1-3; a Root 6 toast means the move set was wrong, not the fix. (4) simulate --all aborts on the first crash: the live runner wraps each test in try/except with a fresh-fixture reset (goto plus clear storage plus reload) before the next test, so a live step failure fails that test and the runner continues; only the two-consecutive-INFRA rule aborts the suite.

## 2. Pre-registered thresholds (frozen before any live run)

- Per-test PASS: zero step failures AND zero check failures AND final ported verify 0 failures AND the integrity guard held (verify FAILS on the untouched fixture before steps, run through the SAME ported verify code path as the final verify, after the fresh fixture load and before any action, per test; the untouched failure list is recorded as evidence; the guard is re-executed on any re-run). If the guard passes on untouched, that test is recorded as FAILED as a suite defect (flagged False, failure text names the guard, suite CONTINUES to the next test, no effect on the infra_blocked counter).
- FLAGGED pass: a pass where the tz-hidden removal intervention ran AND the post-remove snapshot proves the class is gone. A FLAGGED test still requires ALL PASS conditions (zero step, check, and verify failures). Counted separately, never folded into the headline clean count. Edge (C3-F7): flagged means verified removal happened on that test, regardless of which step later made it visible, and the summary carries the full intervention log so the cause is auditable. Per-test flagged stays False for tests run on a bootstrap-intervened tab; the bootstrap intervention is recorded only at suite level (section 3).
- INFRA-blocked: hidden-body unrecoverable after the recovery ladder. Session-creation failures are NOT INFRA-blocked; they use the separate wd_failures counter (own two-consecutive abort, reset to 0 after a successful session creation). infra_blocked resets to 0 on any pass, on any non-INFRA test failure, and on any non-INFRA runner failure. Two CONSECUTIVE infra-blocked tests abort the suite. A 30 s WD HTTP timeout is classified INFRA-blocked (driver or browser hung) unless evidence shows a fixture cause; a wait_for timeout (fixture condition never true) is a live failure, not infra.
- Suite headline: clean passes only. Exit 0 iff clean + flagged == total (total, never a hardcoded 10; the runner supports subsets via argv). A live failure is a finding, never a reason to re-run silently until it passes. A re-run is allowed ONLY for a test proven infra-blocked, max ONE re-run per test, run immediately after the failed attempt, logged with attempt 1 and 2 in the JSONL (attempt field on every log_step record and on the per-test summary, plus "reattempted_from_infra": true). The first INFRA still counts toward infra_blocked; a successful re-run resets it to 0 (pass rule); a second INFRA increments it again. The JSONL is rotated at launch (existing file renamed to .prev-<timestamp>, rotation logged).
- Timing expectation (diagnostic, not a gate): headless simulate 247-393 ms/test per the Y7 log; prior live Marionette suites about 4 s/test. No per-test timeout gate. Per ensure_visible call the worst case is 8 s; open_fixture calls it up to three times per test plus goto/refresh pairs, so the per-test worst case is about 35-40 s; state that bound so a slow test is not misread as a hang. There is no overall suite timeout; a hung Marionette call is bounded by its 30 s HTTP timeout, and the 4 h slot timeout bounds the suite.
- Mid-test hidden-body rule: diagnose runs after every refresh (run_live.refresh diagnoses like goto) AND on any step failure before classifying it. A hidden body found mid-test is classified INFRA, not a step failure.

## 3. Harness design (run_agy_y2.py, self-contained except run_live imports)

Base: run_live.py WD / Runner / diagnose_body / _classify_snapshot (working tree at ship time, md5 recorded; Y4d's diagnose layer got Council 1 APPROVE WITH FIXES, and the current working-tree copy already contains the Council-1 diagnose fixes: second-sample eval error keeps the snap1 classification, never FIXTURE_FAILURE; refresh() diagnoses via the same choke point as goto()). The ensure_visible / open_fixture / bootstrap_tab / preflight pattern is copied from run_agyq2.py and adapted to agy-y2 paths, with every fix below IMPLEMENTED IN THE RUNNER CODE (each maps to a Y4d council finding; "already in base" means verified present in the shipped bytes by reading, with the shipped md5 recorded):

- Preflight (Council 3 F1-F9): explicit LIVE_OWNER_AWAY=1 AND a timestamped handover token (never inferred; re-checked before every test); BiDi 9222 + Marionette 2828 liveness; fixture server loopback on MY port 8769 probing the agy-y2 fixture test-01-tmux-session.html; stale-geckodriver sweep where ppid None REFUSES instead of killing (C3-F3, already in base, verified), garbage PID files unlinked and logged (C3-F8, already in base, verified), stat parsed after the last ')' (C3-F7, already in base, verified); lock check accepts POSIX, FLOCK, OFDLCK (C3-F1, already in base, verified by live flock proof) and the ancestor set includes os.getpid() (C3-F7, already in base, verified); Hyprland IPC liveness as a labeled SAFETY gate with 10 s timeout, never a bare hyprctl call (C3-F9); the signature function is the Y4d two-source version (environ, then socket-dir with AF_UNIX verify) restored verbatim in this file (re-review B1: the environ-only rewrite FAILED live on this laptop at 18:40); log that idle time was NOT independently verified (C3-F9, already in base, verified). ADDED in Y9: launch-time laptop-side slot checks, Y8 ports 4451 and 8767 must be FREE (TCP connect must fail; if either answers, Y8's server or driver is still alive, refuse to run).
- WD orphan hardening (C3-F4/F5/F6): already FIXED in the shipped run_live.py (verified by reading): the geckodriver log opens in append mode "ab" (no truncation), the PID write and the session POST sit inside try blocks with _cleanup on any failure (no orphan with no PID file), and _cleanup's terminate is exception-proof. The log-copy mitigation is kept as defense in depth: after each test's WD exit AND on the session-creation-failure path, copy /tmp/geckodriver-4449.log to /tmp/worker-y9-gecko-{test}-a{attempt}.log, strictly before the next WD() starts (including before the suite-end cleanup WD()); log copy success or failure; tolerate a missing log file.
- Flagged-pass rule (Council 2 F1/F2/F3, already in base, verified): the flag is set ONLY after the post-remove snapshot proves htmlClassList no longer contains tz-hidden; the removal eval also clears the --zen-logo-path inline property (C2-O1); bootstrap intervention is propagated to the suite JSON as a top-level bootstrap_intervention field with schema {"intervened": bool, "tz_hidden_removed": bool, "hidden_body_encounters": int, "detail": str}, INCLUDING on the bootstrap-failure path (the runner emits the suite JSON line before returning 2; "no intervention" is {"intervened": false, "tz_hidden_removed": false, "hidden_body_encounters": 0, "detail": "none"}); bootstrap hidden_body_encounters ARE added to the suite total; suite `passed` counts clean only, exit 0 iff clean + flagged == total; every per-test summary carries the "flagged" key, including the session-failure path.
- Abort rule (C2-F4, C3-F2, resolved as option b): session-creation failures use ONLY the separate wd_failures counter with its own two-consecutive abort; line 20's old definition is corrected so INFRA-blocked excludes session failures. infra_blocked resets to 0 on any pass, on any non-INFRA test failure, and on any non-INFRA runner failure. INFRA matched with startswith("INFRA:") (stricter than the base substring match).
- Ladder budget (C2-F5, already in base, verified): ensure_visible enforces an 8 s deadline from its start and logs elapsed time against the budget on every return path including the VISIBLE early return; the deadline is checked before each phase (poll diagnose, removal eval, new-tab attempt); the enforceable rule is INFRA when the remaining budget is below the next phase's known cost (new tab about 1.7-2.0 s, removal about 1.1 s, diagnose about 0.5-0.7 s), never a new tab when the deadline is near; new-tab attempts are capped by remaining budget (max 3 in rebootstrap, budget-gated); poll cadence is about 3 samples in 2 s (docstring corrected, not every 250 ms).
- No handle scanning (C2-F6, already in base, verified): the runner keeps a registry of known test-tab handles (created by itself) and NEVER switches to an unregistered handle to read its URL. Bootstrap creates fresh tabs via window/new, verifies each with the ladder, and all 10 tests share the surviving tab (goto + clear storage + reload per test). Pre-existing fixture tabs from earlier probes are NOT reused; a fresh tab is created instead. rebootstrap_tab is rewritten create-only (no handles() scan; it switches only to REGISTERED handles to diagnose them, guarded, and creates new tabs otherwise). This removes the 13 s per-scan focus steal entirely.
- Guarded diagnose (C2-F7, already in base, verified): every diagnose_body call on a tab whose state is uncertain sits in try/except that skips the tab instead of aborting the scan; diagnose_body itself returns a FIXTURE_FAILURE dict instead of raising on eval error.
- Swapped-tab tracking (C2-F8, already in base, verified): when ensure_visible swaps, the old handle is recorded in the cleanup set and returned to about:blank at suite end (or closed explicitly, since it is ours); a new tab whose diagnose raises after it left opened_tabs is closed explicitly and dropped from the registry.
- INFRA classification (C2-F9, already in base, verified): rebootstrap failures and removal-eval raises raise INFRA-prefixed errors, never bare RuntimeErrors; a FIXTURE_FAILURE diagnosis raises FIXTURE-UNAVAILABLE immediately, without burning tabs.
- Bootstrap policy (Redteam A5, DECIDED): fresh-tab-only with bounded retries. Up to 3 fresh-tab attempts, each a new window/new tab plus the full ladder with allow_swap=False; a failed tab is closed and the next is tried; if all 3 fail, the runner emits the suite JSON (with bootstrap_intervention and bootstrap_failed true) and returns 2. This differs from the Y4b reuse-first design DELIBERATELY: reuse-first requires scanning handles to find a visible fixture tab, which C2-F6 forbids, and Y8 also rejected the Y4 bootstrap (its evidence is n=1 confounded by time). The ladder's removal step deterministically fixes a tz-hidden tab, so a fresh tab opening hidden is recoverable, and the retries bound the residual risk. The bootstrap handle is removed from opened_tabs before the bootstrap WD session exits (C1-R9), or the first test's WD.__exit__ closes the shared tab. If the ladder swaps during bootstrap verification, the surviving handle is the shared tab, not necessarily the created one.
- Server: my own HTTP server on port 8769 (not Y4's 8768), root = /tmp/worker-y9-server, probing the agy-y2 fixture test-01-tmux-session.html first. Launched under flock on zen_dom.lock, same as Y4/Y8 (the lock serializes the live-driving slot). The shipped layout is fixed (section 5); the laptop copy is frozen at ship time (md5s recorded in SHIPPED.md); later VM edits do not affect it. A Y4d landing after ship time is NOT picked up by design: the frozen ship is what runs, and the run log records the frozen md5s.
- Screenshots (C3-F5, evidence leg): end-state screenshot per test via the Marionette screenshot endpoint, saved to /tmp/worker-y9-shots/{test}-a{attempt}.png, plus a suite-end screenshot to /tmp/worker-y9-shots/suite-end.png. Best effort, never fatal.
- Six section 5.7 metrics: wall time REPORTED; Marionette call count REPORTED (counted in the WD subclass); tokens UNMEASURED (Python runner, no LLM calls); observation cost UNMEASURED; VCR flag False (live run); stall minutes REPORTED (total seconds spent in hidden-body recovery ladders, from ensure_visible timings).

## 4. Test-by-test driving notes (spec vs simulator deltas)

- All 10 tests follow simulate.mjs step for step (selectors and order), plus the spec's intermediate verifies as r.check() calls (recorded, non-fatal) and action steps as r.step() calls (fatal on exception). End state verified by the ported check.mjs logic. The full step-mapping table is in improvements/worker-y9-step-mapping.md (every spec step mapped to the runner call and the simulate.mjs line).
- test-01: type 'uptime' into the input scoped to the ACTIVE pane (Redteam A9): the runner marks the pane container holding #pane-active-output (only the active pane's content div carries that id, fixture lines 205-206) and finds #pane-terminal-input and #btn-send-command inside it via the element-from-element endpoint, never bare duplicate ids. Pin the intermediate check at spec step 15: selector #pane-active-output, expected substring "load average: 0.18, 0.22, 0.15" (spec line 40, fixture line 226). State explicitly that the ported final verify does NOT cover this step (check.mjs line 51 computes terminalOutput but lines 59-66 never assert it), so this r.check() is load-bearing. DECISION (Redteam A6): uptime is covered ONLY by this intermediate check, NOT added to the final verify, because later steps (new window, split vertical, kill pane, undo) re-render the panes and may replace the active pane output, so a final-verify assertion would be unsound. Same for test-07 selected-count (below).
- test-02: no explicit mistake step in the spec; the Bluetooth off/on persistence check plays that role. Follow as written.
- test-03: select PNG via JS value + change event (run_agyq2 select_option pattern), never Marionette keystrokes into a <select>.
- test-04: attachment picker is a modal with option buttons; drive by clicks as simulated. Every modal open is followed by a wait_for on its open/active selector (10 s timeout); the full modal-wait list is in improvements/worker-y9-step-mapping.md section 2.
- test-05: select Bar via JS value + change event. NOTE: the chart-type select has no onchange listener and the render-chart handler ignores the selected type (it always renders the bar SVG), so the "select Bar" step is outcome-irrelevant to the final verify; it is kept for spec fidelity and noted, not treated as coverage. Formula bar: type_text clears first, which is correct (bar starts empty each use). B4 correction: click cell, clear, type 1800 (same as simulator $eval clear). ORDERING (Redteam A13): #chart-title-controls is display:none (fixture line 136) until the render-chart handler shows it, so the chart-title steps run strictly AFTER the render-chart click.
- test-06: straightforward clicks and types as simulated.
- test-07 (WARNING, Y7 doubt 3): the move set is EXACTLY img1-3 (spec steps 15-17). A Root 6 toast on the live run means the move set was wrong, not the fix. Root 5 is correct. Y7 doubt 1 (skip hole): the hole-closers are the step 24 check (trash-counter "1" AND #file-row-img4 hidden) and the step 28 check (trash-counter "0"), both PASS-gating r.check() calls; the final verify alone cannot detect skipping steps 23-29. Selected-count is covered ONLY by the intermediate check at spec step 8 (selector #selected-files-count, expected "5"), NOT by the final verify (check.mjs line 216 reads selectedCount but never asserts it).
- test-08: step 18 clicks a <tr> in the simulator; per the P rule (click <td> never <tr>) the live run clicks the first <td> inside #row-req-api-checkout. Justification: the fixture attaches the handler to the tr itself (fixtures/test-08-devtools.html line 273) and a td click bubbles to it.
- test-09 (WARNING, Y7 doubt 2): follow the spec exactly, including step 29 click #note-item-archived-draft (direction B, verified correct by Y7) and step 33 body check (pinned expected value "Milk, Eggs, Bread, Apples", it mitigates the rename-branch bypass). The precise rename rule: NEVER save with title "Shopping" while the ARCHIVED note is active. The step 7 save MUST use the rename branch (it creates the 'shopping' key); no save happens after the archived note is selected (steps 29-34 are click, delete, view, finalize), so the bypass cannot trigger on the spec path. Step 10 APPENDS ", Apples" to the body: read the current value first, ASSERT it equals "Milk, Eggs, Bread", then type the full text "Milk, Eggs, Bread, Apples" via type_text (it clears first); do NOT use type_text to append. Step 14 clears then types the full new body.
- test-10: spec step 15 clicks #input-edit-watch-total, which the simulator SKIPS because the fixture has that input display:none (fixture line 114) with no handler that unhides it or listens to it. A pointer click cannot work on a hidden input, and click_js (el.click()) would be a no-op that always succeeds, so it is NOT counted as executing the step. The runner records step 15 as SKIPPED with reason "fixture gap: input display:none, no handler, simulator also skips it", carries it as a fixture gap in the test summary ("gaps" list), and the final report names it; a test-10 PASS never implies step 15 was performed.
- Contenteditable: none of the fixtures use it (all inputs/textareas per simulate.mjs). If any type fails with contenteditable symptoms, fall back to focus + execCommand insertText per the runner rule.
- No fixture verify hooks are used as oracles (zero __verify / __agyVerify / __fcckVerify in fixtures, simulate.mjs, and check.mjs; the sole mention in the suite tree is the README.md line 19 prose prohibition; the ported verify reads raw DOM only).

## 5. Slot polling and launch

- SLOT MARKER (exact, C3-F4): Y8's E1 execution is complete when ALL of these hold: (a) a commit exists on todolist-push AFTER 4a78f7f whose message matches regex ^Y8 E1: .*execution complete (case-insensitive on "execution complete"); (b) improvements/worker-y8-e1-execution-log.md contains a NEW line matching "E1 EXECUTION COMPLETE" that names both arm A and arm B results; (c) Y4d's completion is verified DIRECTLY, not inferred through Y8: a commit on todolist-push recording the agy-q2 rerun results (improvements/worker-y4-run-log.md updated with rerun per-test results, or a RUN-REPORT-AGYQ2 file). Polling process: Y9 checks on each wake (git fetch + log + grep); cadence every 15 minutes at most; timeout 4 hours after the Y4d marker appears, then report to the parent instead of launching. The marker is re-checked at launch time, immediately before launching, not only at poll time (Redteam re-review N13): if Y8 is live but momentarily between driver sessions (ports free), the poll-time check cannot tell, so the launch procedure confirms the marker in the same minute as the launch. ABORT rule: if Y8's log shows an ABORT marker (or Y8 reports completion-with-abort), the slot is free ONLY after the launch-time live checks pass (no foreign geckodriver via the preflight sweep, Y8 ports 4451 and 8767 free); an aborted Y8 run frees the slot. If flock -w 60 times out after the marker is confirmed, ABORT the launch and report (fail fast and loud, never wait silently).
- AMENDMENT 20:04 21/11 (Y8b re-scope, binding): the v2.1 comparison is CLOSED (arm A BLOCKED, A1/A2 FAIL incomplete, judge 7275171, no comparative verdict). The marker above is amended: legs (a') and (b') redefine "both arms' results" as "both arms' FINAL states". Leg (a'): a commit on todolist-push after 4a78f7f matching the SAME regex ^Y8 E1: .*execution complete (for example "Y8 E1: B single-arm observation execution complete, v2.1 comparison closed"). Leg (b'): a NEW line in improvements/worker-y8-e1-execution-log.md matching "E1 EXECUTION COMPLETE" that names both arms' FINAL states: arm A BLOCKED (A1 FAIL incomplete, A2 FAIL incomplete, judge 7275171) and arm B single-arm observation B1-v2.2 (PASS/FAIL, execution wall, burden), plus the literal words "no comparative verdict" and "live slot released to Y9". Leg (c) unchanged. Y9 treats EITHER the original marker OR this amended marker as release. The slot is free only after the launch-time live checks pass (Y8 ports 4451 and 8767 free, no foreign geckodriver). If the amended marker never arrives, Y9's 4-hour timeout still applies (report to the parent instead of launching).
- Launch (on the laptop, from the shipped server dir, under flock, detached, one SSH call):
  cd /tmp/worker-y9-server && LIVE_SERVER_ROOT=/tmp/worker-y9-server LIVE_SERVER_PORT=8769 LIVE_LOG=/tmp/worker-y9-live.jsonl WD_PORT=4449 LIVE_OWNER_AWAY=1 flock -w 60 ~/.cache/agent-computer-use/zen_dom.lock -c "python3 run_agy_y2.py all > /tmp/worker-y9-stdout.log 2>&1"
  The handover token /tmp/worker-y9-handover.json is written by the launcher at launch time (asserted_at_unix now, basis "owner handed the machine over 18:24 21/11, out of the house"); the runner re-checks it before every test (max age 4 h).
- Ship: exact layout under /tmp/worker-y9-server on the laptop:
  /tmp/worker-y9-server/run_live.py (frozen copy, md5 recorded)
  /tmp/worker-y9-server/run_agy_y2.py (the runner)
  /tmp/worker-y9-server/agy-y2-manifest.json (expected md5s for every shipped file; the runner verifies it at launch and refuses on mismatch)
  /tmp/worker-y9-server/agy-y2/ (the suite: test-*.md, simulate.mjs, check.mjs, fixtures/, README.md)
  /tmp/worker-y9-server/SHIPPED.md (file, md5, source commit for every shipped file)
  Fixture URLs are base + "/agy-y2/fixtures/test-XX-....html" with base http://127.0.0.1:8769. start_server probes /agy-y2/fixtures/test-01-tmux-session.html first for reuse detection (the copied agy-q2 probe is NOT reused verbatim). Ship via ssh-laptop.sh cat; record md5s of every shipped file; syntax-check both sides (python3 -m py_compile on VM and on laptop).
- Log: improvements/worker-y9-agy-y2-live-log.md on todolist-push, plus per-test JSON summaries on stdout (captured to /tmp/worker-y9-stdout.log) and per-step JSONL at /tmp/worker-y9-live.jsonl (copied back to the repo as tests/realistic/live-run-y9-agy-y2-20261121.jsonl), plus per-test screenshots in /tmp/worker-y9-shots/ (copied back as tests/realistic/live-run-y9-agy-y2-shots/).

## 6. Evidence contract

- Every claim in the final report attaches runnable evidence: exact run command + stdout log, commit hash, timed run log (JSONL with attempt fields), per-test summaries, end-state screenshots. A bare "done" is returned unread. The generator (Y2) never ran these tests live; Y9 is the independent runner.
- Files: improvements/worker-y9-agy-y2-live-plan.md (this file, v2), improvements/worker-y9-step-mapping.md (step mapping + verify-diff inventory + modal waits), tests/realistic/run_agy_y2.py (runner), improvements/worker-y9-agy-y2-live-log.md (run log), tests/realistic/RUN-REPORT-AGYY2-20261121.md (final report).

## 7. Re-review round 2 fixes (19:0x 21/11, before any live driving)

Fresh second pass on the runner as committed in a82bb41: council 1
GO WITH FIXES (F1-F8), council 2 GO WITH FIXES (3 fixes), council 3
GO WITH FIXES (F1-F10), redteam BLOCK (B1-B3 + N1-N14). Verdicts:
improvements/worker-y9-rereview-council-1.md,
worker-y9-rereview-council-2.md, worker-y9-rereview-council-3.md,
worker-y9-rereview-redteam.md. The redteam BLOCK is the gate: no
live driving until B1, B2, B3 are fixed in code and the diff passes
a fresh re-review.

- B1 (BLOCK): preflight could never pass on this laptop. The
  runner's _hyprland_signature() was an environ-only rewrite; Y4d
  proved at 18:40 that UWSM sessions do not carry the signature in
  the compositor environ, and fixed it with the socket-dir source.
  Fix: the Y4d two-source function restored verbatim (environ, then
  socket-dir candidates newest-first, each verified by AF_UNIX
  connect). Re-proved on the laptop before launch (python -c import
  + _hyprland_signature() returns a signature).
- B2 (BLOCK): session exit could close a user tab and screenshot
  user content. Y4d proved DELETE /session closes the session's
  current tab (shared tab died 20/20). The runner left the current
  window uncontrolled after close_tab() on the bootstrap failure
  path, the rebootstrap exhaustion path, and the _recheck session.
  Fix: Y9WD.__exit__ parks on a sacrificial about:blank tab first
  (opened test tabs closed, then a fresh throwaway tab created and
  switched to, kept out of opened_tabs), so the session delete
  closes the throwaway. The shared test tab therefore survives
  session exit; if the live run still prints "shared tab gone,
  rebootstrap", that itself is a finding. The finally screenshot
  also switches to a known test tab (or a sacrificial tab) before
  capturing, so it can never capture a user tab.
- B3 (BLOCK): no launch-time proof the shipped bytes are the
  committed bytes. The suite JSON recorded md5s with no expected
  values to compare against, and no fixture hash at all. Fix:
  tests/realistic/agy-y2-manifest.json lists every shipped file
  with md5 + source commit, generated mechanically from the
  committed bytes; the runner verifies it as the first thing in
  main() and refuses (exit 2, JSON line) on any mismatch. SHIPPED.md
  is generated from the same manifest at ship time. Dry-run flag:
  python3 run_agy_y2.py --verify-manifest (no driving).
- FROZEN BASE (C1 F2 / C3 F1): run_live.py is shipped ONLY from
  commit 1e3901c (md5 84fa106c253d5e7f16daccf2ce3f14a5), the Y4d
  live-proven base (10/10 twice). It is deliberately NOT taken from
  HEAD: HEAD's run_live.py changed in 91d3cd2 (Y11 live-metrics
  wiring, +415/-66), which is not live-proven, and the runner was
  written and reviewed against the 1e3901c API. The a82bb41 tree
  alone cannot run (its run_live.py has no diagnose_body and no
  allow_hidden kwarg; the runner raises ImportError against it).
  Before launch, re-check the laptop ship md5s against the manifest
  and record the check in the run report; any mismatch stops the
  launch and forces a re-ship. Ship gate on the laptop: python3 -m
  py_compile run_live.py run_agy_y2.py AND python3 -c "import
  run_agy_y2" AND python3 run_agy_y2.py --verify-manifest, all in
  the shipped dir; abort the launch if any fails.
- Merged fix list (all applied in the runner before launch):
  check() override logging every intermediate check to the JSONL
  with the attempt field (C1 F1 / C3 F5); post-removal
  FIXTURE_FAILURE raises FIXTURE-UNAVAILABLE immediately (C1 F3);
  FIXTURE-UNAVAILABLE is its own outcome in main, suite continues,
  no infra count, no re-run (C1 F4); mid-test reclassification
  narrowed to TZ_STUCK_V1 / OTHER_HIDDEN only, FIXTURE_FAILURE and
  UNKNOWN stay live failures (C3 F4); WD-timeout match fixed to the
  real wording ("timed out", TimeoutError/URLError) with the
  evidence recorded (C1 F5 / C3 F4); stall_ms accumulates
  ensure_visible ladder time only (C1 F6 / C3 F2 / N2); the
  superseded attempt-1 summary is printed before the re-run, and
  hidden-body encounters + verified removals are accumulated across
  attempts into the suite total with a superseded_attempts list (C1
  F7 / C3 F3 / C3 F6); marionette_calls counts ALL Y9WD sessions
  before the suite JSON (C3 F7); rebootstrap_tab raises
  INFRA-prefixed (C1 F8 / C3 F9a); JSONL rotation failure refuses
  instead of failing open (C3 F9b); test-03 step 31 tightened to
  exact "750 x 1000 px" (C2 F1); test-01 step 35 mid-run
  saved-message check added (C2 F2); the 7 containment checks
  tightened to parent-scoped queries (C2 F3); test-05 B4 correction
  clicks before typing, as the simulator does (C1 Q1); test-08 td
  click scrolls the row into view first (C1 F8 / N7); empty-snapshot
  guard restored in the post-remove path and the recheck (N1);
  handover token fingerprint-bound against mid-run swap (N5, plus
  the procedural rule that the launcher rewrites the token on every
  launch); preflight-failure suite JSON carries the common fields
  (N6); dead clear_input and the unused _rl_log_step import removed
  (N9); preflight PID sweep re-verifies cmdline before SIGTERM too
  (N11); the misleading "check body visible" step removed, the
  following r.check is the real gate (N14); per-test worst-case
  bound corrected to about 35-40 s (C1 F7 / N4); counts corrected
  in the paperwork (88 checks, not 93 and not 87; runner 2865 lines
  at 9564304, 2517 at a82bb41) (C3 F8); mapping test-09 step 10
  row corrected to the full-text type (C1 F7 / C3 F10).
- Accepted as notes, no code change: the infra counter counts
  attempts while the abort rule speaks of tests, with a guard-defect
  test able to leave a stale count of 1 (fail-safe direction, C3
  O1); session-creation failure has no retry by design (N12); slot
  enforcement is manual at launch, marker re-checked in the launch
  minute (N13, section 5); mid-test diagnose assumes the current
  window is the test tab on paths that already raise INFRA (N10);
  total_ms sums final attempts only while suite_wall_ms covers all
  (C3 O4, stated not hidden).
- Diff re-review fixes (council GO WITH FIXES, redteam NO BLOCK,
  19:26 on 21/11): council fix 1, runner line count corrected to
  2865 at 9564304 (the "2853" in this section and the log was
  wrong); council fix 2, the two best-effort B2 fallbacks hardened
  (skip the end-state screenshot if the pre-screenshot switch
  fails; if sacrificial-tab creation fails, park on a registered
  test tab from _TEST_TABS; if no park is possible at all, DELETE
  /session is skipped and the session reference dropped, the
  geckodriver proc is still terminated by cleanup); redteam F1 is
  the same park rule; redteam F2 manifest pinned to 26 files,
  non-hex/null expected md5 refuses, entry loop guarded; redteam
  F3 served bytes verified over HTTP against the manifest after
  start_server (a stale server on the port can no longer serve old
  fixture bytes past the disk check); redteam F4
  fixture-unavailable now counted separately in the suite JSON
  (still counts in "failed", still exits 1; the infra streak is
  deliberately not reset by it, fail-safe, consistent with the
  guard-defect precedent); redteam F5 check() logging wrapped so
  a JSONL I/O error cannot fail a check; redteam F7 bootstrap
  ladder time folded into suite stall_ms and the screenshot
  fallback tab registered in _TEST_TABS; redteam F8 Hyprland
  socket closed via context manager, run_02 paired check single
  eval, run_live.py md5 path via Path.with_name, screenshot skip
  same as council fix 2. Redteam F6 accepted as a note (the
  fingerprint is not a content hash; the threat is accidental
  swap, not a forger restoring mtime_ns). Runner 2982 lines after
  these fixes.
