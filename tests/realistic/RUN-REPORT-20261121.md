# Realistic test live run report - 21/11/2026 (Worker P)

All times Asia/Ho_Chi_Minh. Runner: `tests/realistic/run_live.py`
(stdlib Python, geckodriver --connect-existing, Marionette 2828) against
the LIVE Zen on the laptop (PID 27958, --remote-debugging-port=9222
--marionette). One WebDriver session per test, always deleted in a
finally block. Fixtures served from a loopback HTTP server on
127.0.0.1:8765. End states verified by reading the DOM directly.

## Headline

| Set | Result (final full run + fixes) |
| --- | --- |
| clone1 t01-t10 | **10/10 PASS** |
| fcc-k test-01..10 | **0/10 PASS as specced** (all fail on fixture/spec defects, not on Zen control) |
| f01 diagnostic (lowercase formulas) | **PASS** (proves the spec bug) |
| Hand-driven t01 (agent think time) | **PASS** |

Final full run: 9/20 in 59,111 ms; t06 failed once on a popup settle
flake, then passed 3/3 after the settle fix, so the true final tally is
10/10 clone1. Batch 1 (before fixes) was 5/20 in 53,375 ms.

Per-test times below are the scripted DOM-driver times (machine floor),
NOT agent think time. See "Agent think time sample" for the real
agent-time measurement.

## Results table (final run, 21/11 ~16:25-16:27, plus t06 re-run)

| Test | Result | Time | Notes |
| --- | --- | --- | --- |
| t01 upload single | PASS | 2,678 ms | 4/4 checks |
| t02 upload multi error | PASS | 2,692 ms | 64 KB limit enforced |
| t03 long form | PASS | 2,532 ms | 14 fields, empty-submit errors |
| t04 long form draft | PASS | 4,580 ms | draft restore verified |
| t05 multi-tab | PASS | 5,561 ms | edit in detail tab reflects in list |
| t06 popup dialog | PASS | 5,822 ms | alert/confirm/prompt/modal/popup; failed once pre-fix (see below) |
| t07 download check | PASS | 2,650 ms | 6 lines, checksum ed70e477 |
| t08 login auth | PASS | 3,595 ms | session survives reload, logout works |
| t09 upload metadata | PASS | 2,491 ms | validation errors + success |
| t10 login+upload+download | PASS | 2,769 ms | verdict PASS, report file correct |
| f01 spreadsheet | FAIL | 3,550 ms | spec bug: uppercase formulas (see below) |
| f02 email triage | FAIL | 2,698 ms | fixture gap (see below) |
| f03 calendar | FAIL | 2,256 ms | fixture gap/limit |
| f04 research notes | FAIL | 2,370 ms | fixture gap |
| f05 image organize | FAIL | 2,262 ms | fixture gap + spec typo |
| f06 settings | FAIL | 2,396 ms | BLOCKED: no settings UI |
| f07 bug reproduction | FAIL | 2,514 ms | BLOCKED: dead buttons |
| f08 form validation | FAIL | 2,400 ms | BLOCKED: no validation |
| f09 data copy | FAIL | 2,327 ms | fixture gap |
| f10 long document | FAIL | 2,492 ms | BLOCKED: dead buttons, static doc |

## The three driver fixes (found by bisect, all in run_live.py)

1. **window/new does NOT switch tabs.** After POST /window/new, GET
   /window still returns the OLD handle. Every later command lands in
   the previously-current tab. Fix: explicit POST /window {handle} +
   verify current == new handle, else raise. Without this, goto/type/
   click all hit a user tab, and close_tab would close that user tab.
2. **A ~1 s settle after navigation is required.** readyState ==
   complete is NOT enough: the element already has a valid rect and
   the tab reports visible + focused, yet Marionette's interactability
   check fails ("could not be scrolled into view") until the tab has
   had ~1 s to paint. Proved by probe v2 (sleep, PASS) vs v4 (no
   sleep, FAIL). Fix: sleep 1.0 s at the end of goto() and refresh(),
   0.5 s in switch(), plus an explicit settle after switching to a
   newly-navigated tab (t05 detail tab, t06 popup).
3. **Do not maximize.** The live Zen is already 1863x1176; maximize
   is an unneeded variable. (Earlier "maximize is harmful" claim was
   WITHDRAWN: probe v3's failure is fully explained by the missing
   settle, maximize's effect was never isolated.)

## Serious finding: Worker J's 1.1.3 Selenium test probably closed a user tab

J's `tests/zen_selenium_attach.py` does window/new with NO switch,
then goto/type/click/close. Under finding 1, its goto/type/click ran
in the previously-current tab (a USER tab), and its close_tab closed
THAT tab, not the new one. Evidence: handles 29 -> 30 -> 29, and one
extra about:blank tab left over (the never-switched new tab). J's log
claims "no other user tabs touched", but the evidence says otherwise.
The closed user tab's URL is unrecoverable from here. The parent
should check Zen's recently-closed tabs / ask the user. My runner
switches explicitly, so my runs cannot repeat this. This also
reinterprets J's "Zen respawns a blank tab when a BiDi-opened tab is
closed": the blank tab is simply the never-switched new tab.

## fcc-k checkers are vacuous (offline 10/10 proves nothing)

Every fcc-k `__fcckVerify()` SELF-SIMULATES the intended flow (sets
values, pushes facts, creates events directly in JS) and then checks
its own simulated state. None reads the agent's actual UI state. The
offline 10/10 pass (headless Chromium, 157-166 ms each) proves the
fixtures' JS works, not that an agent can complete the tasks. This
runner never calls `__fcckVerify()`; it verifies end states by reading
the DOM directly. Fixture authors must be told: a checker that writes
its own expected state is not a checker.

## fcc-k failure analysis (all fixture/spec defects, not Zen control)

- **f01 spreadsheet: SPEC BUG.** Spec says type `=C2*D2`. The
  fixture's evalFormula looks up `cells['C2']`, but its keys are
  lowercase, so it throws and shows #ERR (E2-E4 #ERR, E5-E6 NaN).
  The checker's own formula() calls use lowercase (`c2*d2`).
  Diagnostic run with lowercase formulas PASSES fully (E2 540000,
  E3 574000, E4 750000, E5 1864000, E6 621333, E7 3). The spec must
  say lowercase, or the fixture must uppercase refs.
- **f02 email: FIXTURE GAP.** No read/flag/archive/compose/send UI.
  Only reading 6 messages + Sent folder works. Spec steps
  4,6,8,10,12,13,14-18 have no UI.
- **f03 calendar: FIXTURE GAP + LIMIT.** No event dialog; the event
  is not rendered in the grid; the created event lives in a top-level
  `let events` binding that Marionette execute/sync CANNOT read
  (ReferenceError). A top-level `let` is invisible to WebDriver
  execute; only `var` globals and `window.*` are visible. The click
  itself runs without error, but event creation is unverifiable from
  the DOM.
- **f04 research: FIXTURE GAP.** No typing UI for notes; clicking a
  card adds 1 fact (name + price only). 2 clicks per source give 6
  facts. Fact2 is always the price, never the support channel the
  spec asks for. The `saved` flag is a top-level `let`, unreadable
  via Marionette; verified instead that the summary textarea keeps
  its text after Save.
- **f05 image: FIXTURE GAP + SPEC TYPO.** No folder create/rename/
  index.txt UI. Spec step 9 names trip-03.png but the file is
  `photo from web.jpg` (trip-03.jpg). Clicking a file moves it to
  Organized with its original name; that part works.
- **f06 settings: BLOCKED.** No font-size input, no zoom input, no
  Apply button, no sample document. Both Open buttons are dead.
- **f07 bug: BLOCKED.** #toggle, #save, #saveNote have no click
  handlers. The toggle-save-revert bug cannot be observed.
- **f08 form: BLOCKED.** #submit has no handler; no validation code
  at all. No error or success can ever appear.
- **f09 convert: FIXTURE GAP.** Source has 3 rows, not 4 as specced.
  Convert copies src to tgt; #tgt is a plain div with no input.
- **f10 document: BLOCKED.** All five buttons dead; #doc is static
  text. No find/replace, table, TOC, or export can run.

## Clone1 tests are real (and short)

Each clone1 test is 5-7 steps, NOT 15-40 as the brief claimed. Their
checkers drive the actual UI with Playwright and assert DOM text, and
all 10 pass on live Zen. The "20 tests, 15-40 steps each" claim is
only true for the fcc-k half (16-26 steps each). A test set that is
supposed to measure agent think time on hard tasks needs the fcc-k
tests FIXED (gaps above) rather than the clone1 tests lengthened.

## Agent think time sample (hand-driven t01, 21/11 ~16:20-16:27)

Drove t01 by hand, one WebDriver command per step, through
`tests/realistic/hand_drive.py` (stdin JSON commands over a FIFO).
Machine time per op is 2-60 ms; the rest is agent think + tool
round-trip time (each SSH exec call takes 5-9 s wall clock).

| Step | Machine ms | What happened |
| --- | --- | --- |
| new_session | 12 | session 57eb7e2c |
| new_tab (fixture) | 1,151 | includes 1 s settle |
| find #title | 5 | |
| clear #title | 4 | |
| type "Sample Problem" | 14 | |
| find #file | 2 | |
| set_file (1st try, /file endpoint) | FAIL | HTTP 405: geckodriver does NOT implement POST /session/:id/file. Fixed: set the file input's value to the local path directly, geckodriver uploads it internally. |
| type path into #file | 3 | input shows C:\fakepath\t01-statement.txt |
| find #upload | 2 | |
| click #upload | 59 | |
| read #confirmation (1st try) | FAIL | HTTP 500: no such element. The id is #result, not #confirmation. My guess, not the fixture's fault. |
| read #result | 3 | "Uploaded t01-statement.txt (38 bytes, checksum 258f5a4f) for problem "Sample Problem"." PASS |
| close_tab + delete_session | 30 + 3 | clean, no geckodriver left |

Total hand-driven t01 wall time: ~7 minutes for 12 tool calls
(~35 s per step including my thinking and the SSH round trip).
Machine time for the same test scripted: 2,678 ms. The gap between
2.7 s machine and ~7 min agent is the think + tooling overhead the
speed work must attack. Two of my 12 hand steps failed on MY errors
(wrong endpoint, wrong id), both fixed in seconds once observed; a
real agent run must budget for self-correction like this.

Extrapolation (estimate, NOT measured): f01 has 70 scripted steps;
at ~35 s/agent-step that is ~40 min hand-driven. The fcc-k tests are
the right size to measure this; the clone1 tests (5-7 steps) are too
short to show think-time differences.

## Runner bugs found and fixed during the runs

- `log_step` crashed on Path details (t07, t10): `json.dumps` with
  no default. Fixed with `default=str`.
- `refresh()` had no settle (t04, t05, t08 failed on first element
  interaction after reload, and t04's select/change handler appeared
  not to fire). Fixed with 1 s sleep.
- `switch()` 0.5 s settle is flaky for freshly-navigated windows
  (t06 popup failed once). Explicit settle step added at t05/t06.
- f03 day-header selector read hour labels too (`#grid .hour`
  matches headers AND hour labels). Fixed to grid children[1..6].
- f03/f04/f07 read top-level `let` state via Marionette execute:
  ReferenceError. Replaced with DOM-visible verification.

## Session-slot correction

Earlier belief: "one remote session TOTAL per Zen; a leaked session
blocks everything until Zen restarts." Refined 21/11: the cap is per
geckodriver instance (and per BiDi client). Raw Marionette accepts
multiple sessions from different TCP connections (verified: two
concurrent NewSessions, both got ids, DeleteSession works). The
"Session is already started" error I hit was a STALE geckodriver
process (PID 78810, orphaned when I killed its parent python) still
listening on port 4450 and refusing a second session. Fix: kill stale
geckodrivers by PID (`pgrep -x geckodriver`), never `pkill -f` (it
matches the SSH command string and drops the session). The BiDi
leak case from the summary (hung node test) may still hold for BiDi;
this correction is about Marionette only.
`tests/realistic/recover_marionette.py` now speaks raw Marionette
correctly (framing is `<len>:<json>`, commands are arrays
`[0, id, name, params]`).

## Cleanup state at end of run

- All test tabs closed. 2 leftover secondary windows (t05 detail,
  t06 popup) closed explicitly at the end.
- 7 about:blank tabs remain in Zen; NOT closed, because I cannot
  tell which are mine (respawned by Zen when a test tab is deleted)
  and which are the user's own. Parent: ask the user or close them.
- The loopback server (port 8765) is stopped. No geckodriver left
  running. No BiDi session was opened by this run (Marionette only).
- 2 localhost service tabs (BiDi fixture on 127.0.0.1:40301, Claude
  Code Admin on 127.0.0.1:8082) were seen and NOT touched.

## Files

- `tests/realistic/run_live.py` - the runner (stdlib only).
- `tests/realistic/hand_drive.py` - hand-drive helper (FIFO JSON).
- `tests/realistic/probe_zen_state.py` / `probe_zen_state2.py` /
  `probe_zen_state3.py` - the bisect probes (switch, settle, select).
- `tests/realistic/diag_f01_lower.py` - f01 lowercase diagnostic.
- `tests/realistic/recover_marionette.py` - raw Marionette client.
- `improvements/worker-p-test-run-log.md` - full timed log.
- Raw logs on the laptop: /tmp/worker-p-final-run.log (final batch),
  /tmp/worker-p-live.jsonl (per-step JSONL, all runs).

## Open items for the parent

1. J's 1.1.3 user-tab finding (above): check Zen's recently-closed
   tabs with the user.
2. fcc-k fixtures need fixing before they can measure anything: the
   10 gaps/blockers above. f01 needs the lowercase fix (spec or
   fixture). The `__fcckVerify` self-simulation must be replaced by
   DOM assertions.
3. The 7 about:blank tabs: confirm with the user before closing.
4. t06's popup settle is timing-sensitive; if it flakes again, raise
   the post-switch settle.
