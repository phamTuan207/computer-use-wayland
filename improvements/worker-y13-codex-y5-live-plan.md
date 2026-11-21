# Worker Y13 run plan: codex-y5 live on Zen (v2, 2026-11-21 ~19:35 +07)

## Adjudication (v1 -> v2)
v1 was reviewed by council 1/2/3 + redteam (papers:
improvements/worker-y13-council-1.md, worker-y13-council-2.md,
worker-y13-council-3.md, worker-y13-redteam.md). Overall: APPROVE WITH
FIXES (C1, C3) / APPROVE WITH ONE REQUIRED FIX (C2) / 7 HIGH 9 MEDIUM
4 LOW (redteam). All findings below are ADOPTED unless marked rejected.
Nothing in v2 is decided by vote count; each fix is adopted on its
evidence.

Adopted, by finding:
- C1 Q1 / RT M1: base pin 1e3901c STANDS (md5 verified by two reviewers).
  CORRECTION to v1's evidence wording: the base has ONE 10/10 live run
  (Y4d run 2; run 1 was 8/10 on the same bytes), not "10/10 twice".
  "Third proof by Y9" is pending, not evidence. Never ship
  scripts/live_metrics.py next to run_live.py; never set LIVE_METRICS.
- C1 Q4 / RT H1/H6: the park is NOT in run_agyq2.py. The runner's
  source for park, bootstrap, recheck, and main is run_agy_y2.py
  (Y9WD verbatim, renamed). Parked WD is used for EVERY session.
  _park_before_exit asserts the shared tab is not in opened_tabs and
  verifies the current handle equals the throwaway after the switch
  (GET /window); any park failure logs PARK-FAILED loudly, and the
  next test rechecks the shared tab before driving. Park reliance is
  CONDITIONAL on Y9's live result: if Y9 still prints "shared tab
  gone, rebootstrap" every test, the park failed live and the
  rebootstrap fallback becomes primary, park kept only as defense in
  depth.
- C1 Q8: copy list extended: _ppid_of, _TEST_TABS, HANDOVER_FILE,
  TRACKED_ITEM, SERVER_PORT / _rl_start_server import, _md5_of,
  _verify_manifest, _copy_gecko_log, Runner.check JSONL override
  (Y9Runner). rebootstrap raises with the INFRA: prefix (Y9).
  open_fixture drops the no-op r.step("check body visible") (the
  False-return trap) and keeps the r.check gate. clear_input dropped
  (dead code, Y9 N9). set_date is fallback only.
- C1 preflight gaps vs Y9: predecessor free-port checks, runner-quiet
  check wired into CODE (not procedural), JSONL rotation at launch,
  handover fingerprint binding, preflight-failure suite JSON,
  --verify-manifest flag run BEFORE preflight, gecko-log copy per test.
- C2 F1/F2: use txt() (eval textContent, trimmed) for ALL intermediate
  text verifies, exact compare everywhere. This resolves test-10
  steps 2/22/25/27 (hidden panels, d.text returns empty) and test-01
  step 26 (plain <p>, newlines collapse in rendered text) in one
  change. No norm() needed anywhere; the frozen norm() list is EMPTY.
- C2 F3: test-01 step 27 is a click, not typing. Only steps 5/13 type
  multi-line values. Test-07 steps 6/9 also use selects (brief omitted
  them). Test-09 checkboxes re-render on change: re-find per step.
- C2 Q3 edge: if the shared tab is lost mid-test-10 and the
  open_fixture rebootstrap path runs, its clear-storage step wipes
  test-10 state: record INFRA, never a step failure.
- C3 F1/F2/F3: adopt Y9 superseded-attempt accounting verbatim:
  attempt-1 summary printed before the re-run; hidden-body encounters
  plus verified removals accumulate across attempts into the suite
  total with a superseded_attempts list; total_ms sums final attempts
  only; suite_wall_ms covers all; exit 0 iff clean + flagged ==
  total. First INFRA counts; a successful re-run resets
  infra_blocked to 0; a second INFRA increments again. A test that
  needed an intervention on any attempt is flagged, never clean.
- C3 F4: exit 0 iff clean + flagged == total (no hardcoded 10);
  exit 2 for preflight failure, bootstrap failure, handover abort.
- C3 F5 / RT H2: pin r.check for intermediate verifies, r.step for
  actions. A verify implemented as r.step with a False-returning
  lambda logs ok and records nothing; that trap is closed by this pin.
- C3 F6: norm() step list frozen pre-run: EMPTY (txt() everywhere).
  Any mid-run need for norm() is a checker finding, not a
  pass-with-deviation.
- C3 F7: checker-bug path: the test fails, the suite completes (or
  aborts per the abort rule), the checker is fixed, and a fresh FULL
  suite run is required. No single-test re-run after a checker fix.
- C3 F8: bootstrap intervention is suite-level only; per-test flagged
  stays False for tests run on a bootstrap-intervened tab. State the
  SUITE FLAGGED headline rule (flagged > 0 or bootstrap intervention).
- C3 F9: Y13 token path is /tmp/worker-y13-handover.json (never reuse
  Y4d's). Fingerprint binding adopted (Y9 N5): the token carries
  asserted_at_unix + basis + run id; each re-check verifies the
  fingerprint matches the launch fingerprint.
- C3 F10: rotate JSONL at launch; --verify-manifest dry-run flag;
  manifest verification FIRST in main(); WD-timeout match wording is
  "timed out" / TimeoutError / URLError.
- C3 F11 / RT H4/H7: mid-test hidden-body reclassification narrowed
  to TZ_STUCK_V1 / OTHER_HIDDEN only; FIXTURE_FAILURE and UNKNOWN
  stay live failures. AND the rule is implemented, not just stated:
  on ANY step failure, main runs diagnose_body once before
  classifying; TZ_STUCK_V1 / OTHER_HIDDEN reclassifies to INFRA and
  runs the ladder via ensure_visible; VISIBLE means the live failure
  stands. For test-10 reload steps: after the reload click, run
  ensure_visible (ladder), not just diagnose_body, because a reload
  is a new document.
- C3 G1: guard outcomes, all three: fresh-fail (expected): proceed,
  record the untouched failure list. fresh-pass: FAIL the test as a
  suite defect. fresh-error / fresh-timeout: FAIL the test as
  guard-inconclusive; suite continues; NEVER proceed.
- C3 G2: guard once per test, re-executed on any re-run, positioned
  after open_fixture and before step 1, same code path as the final
  verify, untouched failure list recorded per test.
- C3 G3: guard-pass failure has no effect on infra_blocked; suite
  continues.
- C3 G4 / RT M9: top-level `return` required in the ported verify;
  None or non-dict result is a verify FAILURE (fail closed); one live
  eval smoke test of the ported verify AND diagnose_body on one
  fixture before the suite runs (the exact lesson from Y4d's _DIAG_JS
  bug at 18:45).
- C3 G5: expected guard outcome stated: fresh verify fails on all 10
  fixtures (established by Y5's headless proof, commit 3c7c875).
- C3 S1: Y13's own completion marker for Y14 (queued after Y13): a
  todolist-push commit matching ^Y13 codex-y5: .*live complete, plus
  the log line "Y13 codex-y5 live complete: <clean>/<flagged>/<total>"
  in improvements/worker-y13-codex-y5-live-log.md. Y13 leaves the slot
  clean: shared tabs returned to about:blank, no leftover processes,
  its ports free.
- C3 S2: Y6c completion marker, exact: a todolist-push commit whose
  message matches ^Y6c.*(nested|Wayland).*(complete|DONE|verdict|
  REPRODUCED|NOT REPRODUCED) AND that touches an
  improvements/worker-y6c-*.md file, PLUS Muse's go order. A progress
  commit is NEVER a completion marker. An ABORT marker (message
  matching ^Y6c.*(ABORT|abort)) frees the slot only after the
  launch-time live checks pass (Y9 rule).
- C3 S3: launch-time checks, in ORDER: (1) git fetch + confirm the
  exact Y6c marker; (2) runner-quiet process check BEFORE flock (no
  run_*.py process other than self, no hand_drive_e1.py, no Codex
  executor process driving a browser, no live geckodriver with a live
  parent); (3) predecessor ports free by TCP connect (Y9 8769/4449,
  Y8b 8767/4451; Y11b ports once its plan names them; Y6c nested uses
  no TCP ports, so for Y6c the process check + marker + go order are
  load-bearing, stated explicitly); (4) Muse's go order, fresh, at
  run time; (5) flock -w 60 on zen_dom.lock, timeout ABORTS the
  launch and reports, never waits silently; (6) preflight
  (fail-closed), which re-verifies the flock ancestor + orphan sweep.
  NEGATIVE CONTROL: Y8b is live now (arm A launched 19:17:04), so
  any launch-time check run today MUST fail (Y8 ports answer, marker
  absent). The launcher verifies this negative control before Y13's
  turn.
- C3 S4: poll cadence every 15 minutes at most; timeout 4 hours
  without a Y6c completion marker, then report to Muse with the queue
  state instead of launching. Never wait silently.
- C3 S5/S6: no reliance on transitivity alone; the launch-time live
  checks must pass regardless of queue position. A crashed
  predecessor between WD sessions leaves no live geckodriver (sweep
  misses it) and may leave a stale HTTP server; the port-free checks
  catch the stale server, the process check catches a stale runner.
- C3 V1: per-test wall cap at each test's spec Maximum allowable
  latency: 01: 360s, 02: 330s, 03: 360s, 04: 360s, 05: 390s, 06: 420s,
  07: 360s, 08: 360s, 09: 360s, 10: 390s. Enforced by a deadline check
  in main. On trip: INFRA if a WD call is outstanding past its 30s
  HTTP timeout or the browser is unresponsive, else live failure;
  record the call in flight + elapsed. Suite wall expectation: about
  1 minute live (Y4d: ~5s per test), about 60 minutes at spec max.
- C3 section 4 details (a)-(o), restated as runner requirements:
  BiDi probe is GET / expecting 200, NOT /json/version (404 on
  Firefox/Zen); Marionette check is a TCP connect only, the session
  POST in WD.__enter__ is the real protocol probe; Hyprland signature
  is the TWO-SOURCE function (environ, then socket-dir, each verified
  by AF_UNIX connect), copied verbatim, never rewritten; orphan sweep
  refuse rules: ppid None REFUSES, live parent REFUSES, orphan gets
  SIGTERM + 1s sleep + cmdline re-verified to contain geckodriver
  before SIGKILL (and before SIGTERM per Y9 N11); lock check accepts
  POSIX, FLOCK, OFDLCK, WRITE, ancestor set includes os.getpid();
  _ppid_of parses /proc/<pid>/stat after the last ")"; idle time is
  NOT independently verified, the token records basis + timestamp;
  fixture server probe must probe Y13's OWN fixture
  (test-01-git-workflow.html on the Y13 port); handover re-check
  before every test, abort returns 2; session-creation failure
  discrimination: only a failure to CREATE the session counts toward
  wd_failures (a step failure URL contains "/session/<id>/..." and
  must never count); wd_failures resets to 0 after a successful
  session creation; suite-end tab cleanup returns every registered
  test tab to about:blank; _recheck_shared_tab runs after an INFRA
  failure; bootstrap is fresh-tab-only, no handle scanning, tab kept
  out of opened_tabs, registered in _TEST_TABS; the _DIAG_JS
  top-level `return` requirement applies to every value-returning
  eval in the runner.
- C3 section 5 conditions: the final report must NOT cite test-04
  step 22 as evidence that reverse cleared anything (evidence for
  reverse is step 21 + the final verify); note any reload before
  step 22.
- RT M2: visibility verifies get a mapping row: use d.visible() for
  "must become visible" steps (test-03 steps 6/17, test-06 step 3,
  test-07 step 20, test-09 step 12, test-10 steps 8/16/23). The
  fixtures use the hidden attribute, not a class; has_class(x,
  "visible") would fail everywhere. Hidden buttons unhidden by a
  prior step rely on spec order (the unhide is synchronous in the
  same handler); no wait/retry beyond the standard settle. Recorded
  as a known assumption.
- RT M3: test-06 step 13 split: step 13 = click #btn-select-forest
  THEN type_text playhead-input "5" (the click is load-bearing: the
  split acts on the SELECTED clip). Steps 17/22 are replace-only.
  The v1 line grouping all three as "replace" is corrected.
- RT M4: step-count audit: the runner emits exactly the spec step
  count per test (34/22/29/27/26/36/23/21/24/27); main() verifies
  the JSONL step count per test against this frozen table and FAILS
  the test if short. A driver that silently omits steps cannot pass.
- RT M5: ports CHANGED (collision found): P used WD 4450 / HTTP 8765
  (worker-x-e1-experiment-log.md line 20), exactly Y13's v1 WD port.
  New ports: server 8771, WD 4452 (E1 uses 4451/8767, Y9 8769/4449,
  Y4d 8768/4448). Ship-time check before launch: ss -ltn for 4452
  and 8771, pgrep -af geckodriver, /tmp/geckodriver-4452.pid. The
  start_server reuse probe must probe Y13's OWN fixture first (the
  run_live probe hardcodes a clone1 fixture path and would answer
  404 for a stale Y13 server, then die EADDRINUSE on rebind).
- RT M6: reload click tolerance: if d.click on #btn-reload-settings
  raises with a navigation-related error (stale element, dead
  object, document unloaded), treat as success-then-wait: wait_ready
  + 1s settle + diagnose + ensure_visible ladder; record the
  tolerance. Any other click error is a step failure.
- RT M7: test-05 has no mid-test navigation; its exposure is
  load-time (open_fixture ladder) plus the diagnose-on-failure
  safety net. Stated honestly, no general mid-test INFRA claim.
- RT M8: contingency: if Y9's run FAILS in a way that disproves the
  1e3901c base, Y13 does NOT proceed; report to Muse, revisit D1.
  If Y9 fails for a reason unrelated to the base, Y13 proceeds but
  applies Y9's park finding (park broken => do not use the park,
  rebootstrap fallback primary). D1 revisit trigger corrected: Y9
  failure implicating the base OR Y11b proof passing + council
  agreement. If the queue stalls (no Y6c marker within the 4h poll
  timeout), report to Muse.
- RT M9: ported verify return discipline: keep the arrow function
  and invoke it, or paste the body with a top-level return; pass
  testId via arguments[0]; None/non-dict is a verify FAILURE.
  Pre-suite live-eval smoke test of the ported verify AND
  diagnose_body on one fixture before test 01 (C3 G4).
- RT L1: value() trim divergence is theoretical here; do NOT add a
  trim in the port.
- RT L2: test-07 date inputs (#from-date-input, #to-date-input) are
  also plain text inputs; documented in the fixture facts below.
- RT L3: Y6c nested uses no TCP ports; hazard is screen tiling, so
  queue order is the only protection. Noted.
- RT L4: Y14 ports unknown (queued after Y13). v2 states the
  ship-time check for Y14's future ports and the requirement to leave
  the machine clean for Y14.
- REJECTED: none. Every finding was adopted. (Council 2's preferred
  "txt() for all intermediate verifies" was adopted over the
  "d.text + norm() at step 26" alternative because it resolves F1
  and F2 with one change and matches check.mjs line for line.)

## Task
Run all 10 tests in tests/realistic/codex-y5/ LIVE on the owner's Zen via
Marionette, independently. The generator (Y5/Codex) never runs its own
tests as the verdict; this live run IS the verdict.

Owner handed the machine over 18:24 +07, out of the house and busy. Full
autonomy per the Lauren Tan direction. Work directly with Muse.

## Suite facts (read, not assumed)
- 10 tests, 269 steps: 01 git workflow (34), 02 music player (22),
  03 password vault (29), 04 maps directions (27), 05 calendar recurring
  (26), 06 video editor (36), 07 chat search (23), 08 spreadsheet pivot
  (21), 09 file search+tag (24), 10 extension settings (27).
- Merge commit 7c07f6b on todolist-push; Y5 final commit 3c7c875.
  Headless proof by Y5 (independent): jsdom per-step verify 10/10,
  laptop check.mjs --all 10/10 + simulate.mjs --all 10/10, dashes PASS.
- Fixtures are single offline HTML files, no __verify hooks, no
  confirm/alert, deterministic. check.mjs verifyTest reads the DOM only.
- Known weak check: test-04 step 22 passes on a fresh load (same class
  as the 5 known weak checks in agy-y2). NOTE it in the report; do NOT
  silently strengthen the suite mid-run. The step is driven as written.
  The final report must NOT cite step 22 as evidence that reverse
  cleared anything; note any reload before step 22.
- test-07 spec already fixed (3 matches, not 2) before commit.
- Fixture facts verified by reading the HTML:
  - test-01 #file-config-editor is a <textarea> (multi-line values).
  - test-05 #event-start-date is a plain text input (placeholder
    YYYY-MM-DD), NOT type=date. test-07 #from-date-input and
    #to-date-input are also plain text inputs. There is NO type=date
    input anywhere in the 10 fixtures.
  - test-10 #btn-reload-settings calls location.reload(); state lives
    in sessionStorage. After clicking it, wait readyState + 1s settle
    + ensure_visible ladder; do NOT call d.refresh() on top of it.
  - test-03 #clipboard-buffer is a readonly input; value read only.
  - Visibility uses the hidden attribute, not a class, in all
    fixtures. Buttons that start hidden are unhidden synchronously by
    a prior spec step, in order.
  - test-06: after the step 14 split there is no #btn-select-forest
    anymore (ids become forest-head / forest-tail); the spec never
    clicks it after the split.
  - test-09: each checkbox click re-renders the file list and
    replaces the checkbox element; re-find per step.
  - test-08: source input listener is a no-op; the value is read only
    at refresh, so step 19 stale-state check is meaningful.
  - test-02 shuffle is a deterministic fixed reorder, not random.
- Y5 gotcha: check.mjs / simulate.mjs MUST run from the repo/worktree
  root, not from inside the suite dir (fixture paths double up,
  net::ERR_FILE_NOT_FOUND). Applies to any headless re-check I do.

## Runner design (follows Y9's file, proven-structure; Y4d harness inside)
- New file tests/realistic/run_codex_y5.py, self-contained except the
  run_live import (WD, Runner, diagnose_body, log_step, start_server
  as _rl_start_server, SERVER_PORT).
- SOURCE DISCIPLINE (C1 Q8, RT H6): the park, bootstrap_tab,
  _recheck_shared_tab, open_fixture (minus the no-op check step),
  rebootstrap_tab (INFRA prefix), and main are taken from
  run_agy_y2.py (Y9), adapted to codex-y5 paths and ports. The
  diagnose ladder, select/date/txt helpers, and preflight details
  are taken from run_agyq2.py (Y4d) at 1e3901c. No function is
  transcribed from memory; every copy is diff-checked line by line
  against its source before any live driving (runner-review gate,
  below).
- Park: Y9WD verbatim from run_agy_y2.py (renamed Y13WD), used for
  EVERY session: bootstrap_tab, each per-test session, _recheck, and
  the suite-end cleanup session. _park_before_exit asserts the shared
  tab is not in opened_tabs and verifies the current handle equals
  the throwaway after the switch (GET /window); any park failure logs
  PARK-FAILED loudly, and the next test rechecks the shared tab
  before driving. Park reliance is CONDITIONAL on Y9's live result
  (see Adjudication).
- Harness functions copied (source in brackets): _ppid_of [Y4d],
  _check_handover [Y4d, token path changed], _hyprland_signature
  [Y4d, verbatim, two-source], start_server [Y4d, probe URL changed
  to Y13's own fixture], select_option [Y4d], select_by_text [Y4d,
  unused unless needed], set_date [Y4d, fallback only], txt [Y4d],
  count [Y4d], has_class [Y4d], is_checked [Y4d], norm [Y4d, frozen
  list EMPTY], _log_diag [Y4d], rebootstrap_tab [Y9, INFRA prefix],
  ensure_visible [Y4d, 8.0s enforced deadline], _recheck_shared_tab
  [Y9], open_fixture [Y9, minus no-op check step], bootstrap_tab
  [Y9, 3 fresh-tab attempts], preflight [Y4d details + Y9 gaps],
  main [Y9 structure], _md5_of / _verify_manifest / _copy_gecko_log
  [Y9], Runner.check JSONL override with attempt and gaps handling
  [Y9Runner], _TEST_TABS / HANDOVER_FILE / TRACKED_ITEM [Y4d, paths
  adapted]. set_date is never called on this suite (no type=date).
  clear_input is DROPPED (dead code).
- Per-test drivers run_01..run_10 ported step by step from the specs.
- End states verified by a 1:1 port of check.mjs verifyTest (same
  selectors, same expected values, same messages) executed via
  Marionette eval, with a top-level `return` and testId passed via
  arguments[0]. None or non-dict result is a verify FAILURE.
  Integrity guard: the SAME ported verify runs on the untouched
  fixture after open_fixture and before step 1, once per test,
  re-executed on any re-run; the untouched failure list is recorded
  per test. Guard outcomes: fresh-fail (expected, proceed);
  fresh-pass (FAIL test as suite defect, suite continues,
  infra_blocked unchanged); fresh-error / fresh-timeout (FAIL test
  as guard-inconclusive, suite continues, NEVER proceed).
- Driving primitives: real Marionette clicks (d.click) for buttons
  and checkboxes; type_text (clear + element/value) for inputs and
  the test-01 textarea (multi-line values incl. \n, steps 5/13
  only); select_option (JS value + change event) for <select>;
  d.visible() for "must become visible" steps (test-03 steps 6/17,
  test-06 step 3, test-07 step 20, test-09 step 12, test-10 steps
  8/16/23).
- Intermediate text verifies: txt() (eval textContent, trimmed),
  exact compare everywhere, recorded via r.check. Actions via
  r.step. (r.step with a False-returning lambda logs ok and records
  nothing; verifies MUST be r.check.)
- One fresh WebDriver session per test, always deleted in finally.
  Sessions exit parked on a sacrificial about:blank tab (Y13WD park)
  so DELETE /session closes the throwaway, never the shared test tab
  and never a user tab. Shared test tab via bootstrap_tab. If
  "shared tab gone, rebootstrap" still prints, that is a FINDING
  (Y4d observed the shared tab does not survive its session; Y9's
  park is meant to fix it).
- FLAGGED: a pass only after a verified tz-hidden removal ran AND the
  post-remove snapshot proves the class is gone, accumulated across
  attempts (a test that needed an intervention on any attempt is
  flagged, never clean). Clean headline counts clean only. Exit 0
  iff clean + flagged == total.
- ABORT: infra_blocked counts hidden-body-unrecoverable only;
  session-creation failures use the separate wd_failures counter (own
  two-consecutive abort; only a failure to CREATE the session counts,
  a step failure URL contains "/session/<id>/..." and must never
  count; wd_failures resets to 0 after a successful session
  creation). infra_blocked resets on any pass and on any non-INFRA
  failure, EXCEPT fixture-unavailable and guard outcomes (guard
  defect / guard inconclusive), which leave the streak unchanged.
  AMENDMENT (redteam re-review M5, 21/11): the plan's original
  wording said "any non-INFRA failure", but the runner (following
  Y9's code precedent) deliberately does NOT reset on
  fixture-unavailable / guard outcomes. The fail-safe direction is
  kept: a fixture failure between two INFRA tests does not hide the
  streak, so the run aborts sooner rather than later. First INFRA
  counts, a successful re-run resets it to 0, a second INFRA
  increments again. A 30s WD HTTP timeout is INFRA
  (match wording "timed out" / TimeoutError / URLError); a wait_for
  timeout is a live failure.
- Mid-test hidden body: on ANY step failure, main runs diagnose_body
  once before classifying; TZ_STUCK_V1 / OTHER_HIDDEN reclassifies
  to INFRA and runs the ladder via ensure_visible; VISIBLE means the
  live failure stands; UNKNOWN stays a live failure. FIXTURE_FAILURE
  splits (redteam re-review H4): a positively proven no-body
  document (a snapshot with hasBody false and readyState complete)
  is fixture-unavailable; a diagnose transport error (eval_error
  present, or no snapshots) is INFRA. Test-05 has no mid-test
  navigation, so its exposure is load-time plus this safety net; no
  general mid-test INFRA claim is made.
- A re-run is allowed ONLY for a test proven infra-blocked, max ONE
  per test, immediately after the failed attempt, logged with the
  attempt field; attempt-1 summary printed before the re-run;
  superseded attempts listed in superseded_attempts; hidden-body
  encounters + verified removals accumulate across attempts into the
  suite total; total_ms sums final attempts only; suite_wall_ms
  covers all. Checker-bug path (separate): the test fails, the suite
  completes (or aborts per the abort rule), the checker is fixed, and
  a fresh FULL suite run is required; no single-test re-run after a
  checker fix.
- Preflight: fail-closed (handover token + BiDi 9222 GET / + Marionette
  2828 TCP connect, session POST is the real probe + Hyprland IPC
  SAFETY gate, two-source signature, 10s timeout + fixture server
  probe of Y13's OWN fixture + orphan geckodriver sweep by PID with
  parent check, ppid-None REFUSES, live parent REFUSES, SIGTERM +
  1s + cmdline re-verify before SIGKILL + zen_dom.lock flock held by
  an ancestor, lock types POSIX/FLOCK/OFDLCK). Handover token
  re-checked before every test (4h max age); expiry mid-run aborts
  with exit 2. Token path /tmp/worker-y13-handover.json, written by
  the LAUNCHER at run start (never at prep time), basis "owner
  handover 18:24 +07, out of house" + run id + fingerprint binding.
  Launch command sets LIVE_OWNER_AWAY=1.
- Ports (own namespace, collision-checked incl. P and E1): server
  8771, WD 4452, MARIONETTE 2828 (shared, connect-existing). Ship dir
  /tmp/worker-y13-server. Launch under flock -w 60
  ~/.cache/agent-computer-use/zen_dom.lock. Ship-time check before
  launch: ss -ltn for 4452 and 8771, pgrep -af geckodriver,
  /tmp/geckodriver-4452.pid.
- Ship: manifest with md5s of every shipped file + SHIPPED.md
  (frozen base, ship dir, launch command). live_metrics.py must be
  ABSENT from the ship dir. Launch-time manifest check refuses to run
  unless every shipped file matches; the check runs BEFORE preflight
  and the server start; --verify-manifest dry-run flag supported.
  Ship-time re-verification of run_live.py md5 from git.
- Per-test JSON summary lines on stdout; per-step JSONL at LIVE_LOG
  (rotated at launch: existing file renamed to .prev-<timestamp>);
  per-test screenshots in /tmp/worker-y13-shots/; gecko-log copied
  per test; preflight-failure suite JSON on preflight failure.
- Per-test wall cap (spec Maximum allowable latency): 01: 360s,
  02: 330s, 03: 360s, 04: 360s, 05: 390s, 06: 420s, 07: 360s,
  08: 360s, 09: 360s, 10: 390s. Enforced by a deadline check in main.
  On trip: INFRA if a WD call is outstanding past its 30s HTTP
  timeout or the browser is unresponsive, else live failure; record
  the call in flight + elapsed.
- Step-count audit: the runner must emit exactly the spec step count
  per test (34/22/29/27/26/36/23/21/24/27); main() verifies the JSONL
  step count per test against this frozen table and FAILS the test if
  short.
- Pre-suite live-eval smoke test: before test 01, run the ported
  verify AND diagnose_body live on one fixture and require both to
  return well-formed values; abort the suite if either returns None
  or a non-dict.

## Base pin (decision D1, settled)
- Ship run_live.py from commit 1e3901c ONLY (md5
  84fa106c253d5e7f16daccf2ce3f14a5, the Y4d live-proven base). Evidence
  corrected: ONE 10/10 live run on these bytes (Y4d run 2; run 1 was
  8/10), not two. Y9's run, when it lands, is the second 10/10
  proof. Deliberately NOT HEAD: HEAD's run_live.py changed in 91d3cd2
  (Y11 live-metrics wiring, +415/-66), unit-verified only, not
  live-proven. The runner is written and reviewed against the 1e3901c
  API.
- Metrics are NOT lost: per-step elapsed_ms is recorded by log_step
  in both versions. Think-time/hit-rate metrics are out of scope for
  this run; Y11b owns that proof.
- Revisit ONLY if (a) Y9's run FAILS in a way that disproves the
  1e3901c base (then do NOT proceed; report to Muse, revisit D1), or
  (b) Y11b's proof run passes before my run AND the council agrees
  the API diff is safe. If Y9 fails for a reason unrelated to the
  base, proceed but apply Y9's park finding. Default stays 1e3901c.

## Pre-registered thresholds
- Target 10/10. A test passes only if ALL spec steps pass AND the
  ported verifyTest passes AND the step-count audit passes.
- test-04 step 22 is expected to pass trivially (weak check); it does
  NOT count as evidence of anything beyond the step running, and the
  final report must not cite it as reverse evidence.
- norm() step list, frozen pre-run: EMPTY. Any mid-run need for
  norm() is a checker finding, not a pass-with-deviation.
- End-state verifyTest uses EXACT trimmed textContent comparison,
  identical to check.mjs. No norm() there.
- Suite wall time is reported; per-test caps are in the Runner
  design section above. Expected suite wall: about 1 minute live,
  about 60 minutes at spec max.

## Slot / queue (hard rule)
- The live-driving slot is EXCLUSIVE and queued: Y8b runs E1 A/B now,
  then Y9 runs the agy-y2 suite live, then Y11b runs its small live
  proof run, then Y6c runs the Wayland-nested probe. My live run goes
  AFTER Y6c reports completion. Y14 (batch-3 live) queues AFTER Y13.
- Y6b prep is DONE (commit c8bee88); the nested run itself is done by
  a NEW agent Y6c. Y6c completion marker, exact: a todolist-push
  commit whose message matches
  ^Y6c.*(nested|Wayland).*(complete|DONE|verdict|REPRODUCED|
  NOT REPRODUCED) AND that touches an improvements/worker-y6c-*.md
  file, PLUS Muse's go order. A progress commit is NEVER a completion
  marker. An ABORT marker (message matching ^Y6c.*(ABORT|abort))
  frees the slot only after the launch-time live checks pass.
- Launch-time checks, in ORDER: (1) git fetch + confirm the exact
  Y6c marker; (2) runner-quiet process check BEFORE flock (no
  run_*.py process other than self, no hand_drive_e1.py, no Codex
  executor process driving a browser, no live geckodriver with a live
  parent); (3) predecessor ports free by TCP connect (Y9 8769/4449,
  Y8b 8767/4451; Y11b ports once its plan names them; Y6c nested uses
  no TCP ports, so for Y6c the process check + marker + go order are
  load-bearing); (4) Muse's go order, fresh, at run time; (5) flock
  -w 60 on zen_dom.lock, timeout ABORTS the launch and reports, never
  waits silently; (6) preflight (fail-closed). NEGATIVE CONTROL: Y8b
  is live now (arm A launched 19:17:04), so any launch-time check run
  today MUST fail.
- Poll cadence every 15 minutes at most; timeout 4 hours without a
  Y6c completion marker, then report to Muse with the queue state
  instead of launching. Never wait silently.
- Do ALL prep now (plan, council + redteam, runner code, headless
  self-check of the runner's Python only, ship + manifest). Drive Zen
  ONLY after Y6c completes and Muse says go. One live runner at a
  time, no exceptions.

## Step-mapping table (spec step -> driver primitive)
- Open fixture: open_fixture (goto + clear storage + reload + ladder).
- "Verify #x text is ...": r.check with txt() (eval textContent,
  trimmed), exact compare. End state: ported verifyTest, exact
  trimmed textContent, identical to check.mjs.
- "Verify #x must become visible": r.check with d.visible().
- "Type ... into #x": r.step type_text.
- "Replace #x value with ...": r.step type_text (clear + value).
- "Click button #x": r.step d.click.
- "Click checkbox #x": r.step d.click, then verify via is_checked.
- "Select value ... in #x": r.step select_option (JS value + change),
  then verify via eval selected value.
- "Click #x, then replace #y": two steps, in order. test-06 step 13:
  click #btn-select-forest THEN type_text playhead-input "5" (the
  click is load-bearing: the split acts on the SELECTED clip). Steps
  17/22 are replace-only.
- test-10 steps 21/26 (reload): click #btn-reload-settings with
  navigation-error tolerance (stale element / dead object / document
  unloaded after the click counts as success-then-wait), then
  wait_ready + 1s settle + ensure_visible ladder (no d.refresh()).
- test-01 steps 5/13 (textarea multi-line): type_text with the exact
  \n value, verify via d.value exact compare. Step 27 is a click,
  not typing.
- test-06 steps 17/22 (replace input values): type_text.
- test-09 step 6 (replace search input): type_text.

## Runner-review gate (required before any live driving)
- After the runner is written and syntax-checked, a FRESH re-review
  (council + redteam) of the runner code against run_agyq2.py at
  1e3901c and run_agy_y2.py is required before any live driving.
  No live driving until the re-review passes or its findings are
  fixed and re-verified.

## Deliverables
- improvements/worker-y13-codex-y5-live-plan.md (this file, v2) +
  council 1-3 + redteam papers.
- tests/realistic/run_codex_y5.py + SHIPPED.md + manifest, shipped to
  /tmp/worker-y13-server on the laptop at run time.
- improvements/worker-y13-codex-y5-live-log.md (timeline, run, results).
- tests/realistic/RUN-REPORT-CODEX-Y5-20261121.md (per-test results).
- Report back: per-test PASS/FAIL with ms, total wall time, steps,
  hidden-body encounters with diagnosis, test-04 step 22 observation.
