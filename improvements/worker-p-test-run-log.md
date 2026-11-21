# Worker P run log - realistic test execution - 21/11/2026

All times Asia/Ho_Chi_Minh, wall-clock + elapsed. Independent Muse subagent.
Job: RUN the 20 realistic tests (clone1 10 + fcc-k 10) on laptop Zen, measure
per-step and total wall time, record every error. A fail with a clear error
is a good result. Do NOT drive Zen while Worker J is still running live tests
(shared BiDi/Marionette session cap, one session total per Zen).

## 15:41 - Start, status check
- Worker J STILL RUNNING (started 15:21, ~20 min in, last activity seconds ago).
  Its log (laptop improvements/worker-j-post-reboot-log.md) ends 15:31-15:35 at
  item 2.2.3 (E2 phase B, BLOCKED, hyprglass not loaded). Remaining J items:
  real-task re-test 1.3.2/5.1, final report, merge todolist-push into main.
  Log file mtime 15:36, unchanged at 15:42 check. J is mid real-task test.
  DECISION: preparation only until J finishes. No Zen driving yet.
- Worker N (Code Mode) DONE. Worker M (agy) still running.
- VM repo on todolist-push, HEAD 625507f (code-mode commit). Laptop repo HEAD
  d96d0bd, branch todolist-push, main still at 2e558f7 (merge NOT done).
- NOTE: will NOT push to origin/todolist-push until J's merge completes, to
  avoid a push race with J. Local commits only until then.

## 15:42 - Test inventory read (all 20 specs)
- clone1 t01-t10 (from origin/main, extracted to /tmp/worker-p): each 5-7 steps
  only, NOT 15-40 as the brief stated. Topics: upload single, upload multi
  error, long form, long form draft, multi-tab, popup/dialog, download check,
  login auth, upload metadata, login+upload+download. Each has fixture.html +
  check.mjs (Playwright) + README.md. Shared lib/browser.mjs (playwright-core
  + Chromium from Playwright cache or CHROMIUM_PATH) and lib/server.mjs
  (loopback static server). run_all.mjs runs all 10, writes results.json.
- fcc-k test-01..10 (VM checkout): 16-26 steps each, matches the 15-40 spec.
  Topics: spreadsheet formulas, email triage, calendar conflicts, research
  notes, image organize/rename, settings two apps, bug reproduction, form
  validation, format convert, long document edit. Each has a .md spec + offline
  fixture HTML exposing window.__fcckVerify(). Checker: check.mjs with
  puppeteer-core + /usr/bin/chromium (or CU_CHROME_PATH), file:// URL.
- Discrepancy to report: clone1 tests are 5-7 steps, fcc-k tests are 16-26.
  The "20 tests, 15-40 steps each" claim is only true for the fcc-k half.

## 15:43 - Offline verification setup (laptop, headless, no Zen)
- VM has node v24.22.1 but NO chromium and no node_modules: offline checks
  cannot run on the VM. Laptop has /usr/bin/chromium, node v26.13.1, repo
  node_modules with @puppeteer. Offline checks run on the LAPTOP via SSH with
  headless chromium. This does not touch Zen or J's session.
- Laptop repo has tests/realistic/fcc-k and fcc-k2 but NOT clone1. Copying
  clone1 tests to /tmp/worker-p-clone1 on the laptop (outside the repo) so
  J's working tree is untouched.

## 15:44 - Offline verification results (laptop, headless Chromium)
- fcc-k checks: 10/10 passed, each 157-166ms, score 1. Clone1 run_all:
  10/10 passed, wall clock 6253ms (t01 1238ms, t02 734ms, t03 519ms,
  t04 527ms, t05 519ms, t06 691ms, t07 421ms, t08 571ms, t09 507ms,
  t10 523ms). Full log: /tmp/worker-p-offline.log on the laptop.
- BUT the fcc-k 10/10 is VACUOUS. Reading every fixture's __fcckVerify()
  shows all 10 SELF-SIMULATE the intended flow (set values, push facts,
  create events directly in JS) and then check their own simulated state.
  None reads the agent's actual UI state. The offline pass proves the
  fixtures' JS works, not that an agent can complete the tasks. My live
  run verifies end states by reading the DOM directly and NEVER calls
  __fcckVerify() as an oracle.

## 15:45 - Fixture-vs-spec audit (from reading all 10 fcc-k fixtures)
- f01 spreadsheet: RUNNABLE via the A2/B2... buttons + #typed + type/Enter
  buttons. TRAP: the <td> cells have no click handler; clicking a cell
  directly selects nothing.
- f02 email: PARTIAL. No read toggle, flag, archive, compose, or send UI.
  Only reading messages + Sent button work. Spec steps 4,6,8,10,12,13,14-18
  have no UI.
- f03 calendar: PARTIAL. No event dialog; clicking a free slot creates a
  hardcoded event in JS state; the event is NOT rendered in the grid.
  Spec steps 7-14, 19 have no UI.
- f04 research: PARTIAL. No typing UI for notes; clicking a source card
  adds 1 fact (name + price). 2 clicks per source give 6 facts. Summary
  textarea + Save work. Fact2 is always price, never the support channel
  the spec asks for.
- f05 image: PARTIAL. Clicking a file moves it to Organized. No folder
  creation, no rename, no index.txt UI. Spec step 9 has a wrong extension:
  trip-03.png, but the file is photo from web.jpg (trip-03.jpg).
- f06 settings: BLOCKED. No font-size input, no zoom input, no Apply,
  no sample doc. Both Open buttons are dead.
- f07 bug: BLOCKED. #toggle, #save, #saveNote have no click handlers.
- f08 form: BLOCKED. #submit has no handler; no validation code at all.
- f09 convert: PARTIAL. Source has 3 rows, not 4 as specced. Convert
  copies src to tgt; #tgt is a plain div, no typing UI.
- f10 document: BLOCKED. All five buttons dead; #doc is static text.
- Clone1 fixtures are REAL (checkers drive the actual UI with Playwright
  and assert DOM text); all 10 passed on headless Chromium.

## 15:46 - Live runner built
- tests/realistic/run_live.py (stdlib Python WebDriver client over
  geckodriver --connect-existing, Marionette 2828). One session per test,
  deleted in finally. Loopback HTTP server in-process serving
  /tmp/worker-p-server (clone1 + fcc-k) on 127.0.0.1:8765. Per-step JSONL
  log to /tmp/worker-p-live.jsonl. Uploads from /tmp/worker-p-uploads;
  downloads polled in ~/Downloads.
- Driver choice note: per-step times from the scripted runner are the
  DOM-driver floor (machine time), not agent think time. One test will
  also be hand-driven step by step to measure true agent wall time.
- Worker J's log updated 15:46: merge todolist-push -> main DONE
  (commit 96438bb, main now abb51bf, 46/46 tests pass on merged tree).
  Todo 111/115. J notes the laptop repo is NOT synced (detached HEAD
  56f5af4, uncommitted changes) and the deployed overlay.py is now stale
  vs main; redeploy is a follow-up. J's log has NO run evidence for the
  real-task re-test 1.3.2 it ticked at 15:38; flagging to parent.
- Worker M DONE (agy root cause found, helper installed). Worker N DONE.

## 15:49 - Session slot probe + t01 smoke test
- Slot probe: created a WebDriver session, listed 30 tabs, deleted cleanly.
  The session slot is FREE; Worker J is no longer driving Zen. Safe to
  start live runs.
- t01 smoke test FAILED at step 2 "fill title": Marionette
  `element not interactable: Element <input id="title"> could not be
  scrolled into view`. Open fixture worked (85ms). First fix attempt
  (maximize window + scrollIntoView before click/type/set_file + close
  test tabs in WD cleanup) did NOT fix it: second run failed identically
  (5ms). Hypothesis wrong; kept the maximize/scroll changes (harmless)
  and probed deeper.
- Probe v1 (probe_zen_state.py): found the session attaches to a leftover
  fixture tab; new-tab probe failed with HTTP 500 because the runner's
  HTTP server was dead (server runs in-process, dies with the runner).
  Started a persistent server: python3 -m http.server 8765 on the laptop
  (PID 59470), curl 200 confirmed.

## 15:52 - ROOT CAUSE FOUND: window/new does not switch tabs
- Probe v2 (tests/realistic/probe_zen_state2.py) proves it: after
  POST /window/new, GET /window still returns the OLD handle. An explicit
  POST /window {handle} is required. After the explicit switch, the exact
  failing op works: CLEAR OK, TYPE OK, readback "Sample Problem".
  Visibility visible, hasFocus True, rect #title [487.5, 111.6, 202, 22].
- Fix applied to run_live.py new_tab(): switch + verify current == new
  handle, else raise. Re-running t01.
- SERIOUS IMPLICATION for Worker J's 1.1.3 Selenium test (tests/
  zen_selenium_attach.py): it does window/new with NO switch, then goto,
  type, click, close. Under this behavior its goto/type/click ran in the
  previously-current tab (a USER tab), and its close_tab closed THAT tab,
  not the new one. Evidence fits: handles 29 -> 30 -> 29, and one extra
  about:blank tab left over (the never-switched new tab). J's log claims
  "no other user tabs touched", but the evidence says otherwise. The closed
  user tab's URL is unrecoverable from here. REPORT TO PARENT: flag this,
  do not silently re-tick 1.1.3 as clean; the parent should check Zen's
  recently-closed tabs / ask the user. My runner now switches explicitly,
  so my runs cannot repeat this.
- Also noted: tab count grew 30 -> 33 from leftover test tabs (my two
  failed t01 runs + probes). Cleanup of my leftovers happens at the end
  of my run; the leftover fixture tab from run 1 was already closed by
  the probe --close-leftovers pass.

## 15:53-15:57 - Settle delay is the real fix (not maximize)
- t01 still failed after the switch fix (same "could not be scrolled
  into view"). Bisect with probes:
  - v2 (switch, 1s sleep after goto, no maximize): CLEAR OK, TYPE OK.
  - v3 (switch, maximize, no sleep): CLEAR FAILED.
  - v4 (switch, no maximize, no sleep): CLEAR FAILED.
  Conclusion: the settle delay after navigation is REQUIRED; maximize's
  effect was never isolated (v3's failure is fully explained by no-sleep,
  so the earlier "maximize is harmful" claim is WITHDRAWN). readyState ==
  complete is not enough: the element already has a valid rect and the
  tab reports visible + focused, yet Marionette's interactability check
  fails until the tab has had ~1s to paint.
- Fix in run_live.py: sleep 1.0s at the end of goto(), 0.5s in switch().
  Maximize stays out (unneeded, Zen already 1863x1176). Re-running t01.

## 15:57-16:00 - Batch 1: 5/20 in 53,375 ms
- PASS: t01 2654ms, t02 2679ms, t03 2556ms, t06 4862ms, t09 2512ms.
- FAIL t04 (refresh settle: select/change did not fire, #title not
  interactable), t05 (refresh settle: link click not interactable),
  t07 + t10 (runner bug: PosixPath not JSON serializable in log_step),
  t08 (refresh settle: session check read before init), f01 (uppercase
  formulas #ERR/NaN), f02/f05/f09 (fixture gaps, by design), f03/f04/
  f07 (ReferenceError on top-level let state), f06/f08/f10 (BLOCKED,
  by design).
- Fixes applied: refresh() + 1s settle; log_step default=str; f03 days
  selector to grid children[1..6]; f03/f04/f07 let-state reads replaced
  with DOM-visible verification; t05 detail-tab settle step.
- Probe v3/v4 correction: maximize's effect was never isolated; the
  "maximize is harmful" claim is WITHDRAWN. The settle delay is the
  proven variable.

## 16:01-16:03 - Re-run of 8 affected tests: 4/8 pass
- t04 PASS, t07 PASS, t08 PASS, t10 PASS. f03/f04/f07 fail only on
  their (correct) fixture-gap/blocked entries; all runnable steps pass.
- t05 failed at a NEW point: "edit title" after switching to the
  detail tab (switch 0.5s settle not enough for a freshly-navigated
  tab). Fix: explicit settle step after the switch. Re-run: t05 PASS
  (5573ms).
- f01 diagnostic (diag_f01_lower.py, lowercase formulas): ALL CHECKS
  PASS (e2 540000, e3 574000, e4 750000, e5 1864000, e6 621333, e7 3).
  The spec's uppercase formulas are the only f01 problem.

## 16:05-16:27 - Hand-drive sample (t01) + session-slot investigation
- Built hand_drive.py (FIFO JSON commands). Setup cost ~20 min of
  fighting: (a) both FIFOs created with mkfifo, so `tail` on the
  output FIFO hung forever (fix: regular file for output); (b)
  `pkill -f` matched the SSH command string and dropped the session
  (fix: kill by PID, pgrep -x / bracket patterns); (c) a stale
  geckodriver (PID 78810, orphaned when its parent python was killed)
  held port 4450 and returned "Session is already started" for new
  sessions.
- SESSION-SLOT CORRECTION: the cap is per-geckodriver-instance, NOT
  a global Marionette lock. Raw Marionette accepts multiple sessions
  from different TCP connections (verified: two concurrent NewSessions,
  both got ids; DeleteSession works). The earlier "leaked session
  blocks everything until Zen restarts" belief is refined: it was a
  stale geckodriver process, not a Marionette session. recover_
  marionette.py now speaks raw Marionette correctly (framing
  <len>:<json>, commands [0, id, name, params]).
- Hand-driven t01: PASS in ~7 min over 12 tool calls. My own errors:
  set_file via /file endpoint -> HTTP 405 (geckodriver does not
  implement it; set the input value to the local path directly);
  read #confirmation -> HTTP 500 (the id is #result). Both fixed in
  seconds once observed. Machine time for the same test scripted:
  2,678 ms. See the report for the full step table.
- Cleanup: session deleted, no geckodriver left.

## 16:27-16:35 - Final full run: 9/20 in 59,111 ms, then t06 fix
- t06 FAILED once ("fill popup name" not interactable): the popup
  window needs the full settle after switching, same as t05. Fix
  applied; t06 re-run PASS, then 2/2 more passes. True final tally:
  clone1 10/10, fcc-k 0/10 as-specced (all fixture/spec defects).
- Final cleanup: closed 2 leftover secondary windows (t05 detail,
  t06 popup). 7 about:blank tabs remain, NOT closed (cannot tell
  mine from the user's). Loopback server stopped. No geckodriver
  left. Zen tab count 33 (was 30 at start; +3 = blanks, see report).
- Report written: tests/realistic/RUN-REPORT-20261121.md.
