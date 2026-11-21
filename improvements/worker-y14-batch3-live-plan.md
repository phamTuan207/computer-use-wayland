# Worker Y14 run plan: clone1-batch3 FIXED suite, LIVE on Zen

Worker: Y14 (Muse live runner). Owner order: full autonomy, machine handed
over 18:24 21/11, owner out and busy. Lauren Tan direction applies.
Slot: AFTER Y13 reports completion. Live queue: Y8b E1, Y9 agy-y2, Y11 proof,
Y6b nested, Y13 codex-y5, then Y14. One live runner at a time, no exceptions.

## Suite under test

Merged fixed suite, commit ed78e83 on main (Y10 reconciled best of both):
- t05: clone1 fixture (rename dialog Save/Cancel, empty shows error and
  stays open) + Y10 checker (novel names, typed cancel, dialog-open asserts,
  non-empty folder rename with trim, tree-button click).
- t09: clone1 checker (clickAndClose with 5 s verify polling) + Y10 cancel
  dwell 500 ms, no verify for Cancel.
- t10: clone1 checker (500 ms in-page position sampler, take the minimum) +
  Y10 advance assert (position must be at least 2 after a 350 ms sleep
  following the sample window, check.mjs L93-95).
- t01-t04, t06-t08: unchanged from clone1 batch 3 (Y3 passed them 7/10
  overall; these 7 passed then).
- Headless evidence (Y10): 9/9 mutation probes v2 matched, 10/10 x7 runs
  (sequential about 24-27 s, load run 3 concurrent suites about 74 s each).
- Y12 is independently verifying the merged suite headless. If Y12 reports
  a defect before my slot opens, I re-read its verdict and adjust; a Y12
  FAIL on a test I already ran live means that live result is provisional
  until the fix lands and the test is re-run live.

## Runner design: tests/realistic/run_batch3.py (new file)

Reuses the proven driver, never reinvents it:
- `from run_live import WD, Runner, start_server` (Worker P driver, with
  Y4d diagnose ladder and Y11 live metrics already wired in).
- `select_option` copied verbatim from run_fcck.py (Worker U, 6 lines, JS
  value + change event), attributed in a comment. Precedent also in
  run_agyq2.py. Used for: t05 #sort and #move-target, t08 #theme,
  t09 #theme-select.
- Popup pattern copied from run_live.py run_t05/run_t06 (proven live):
  click, _wait_handles(n+1), switch, wait_ready + 1.0 s settle,
  require_visible, interact, close_tab, switch back to main handle.
- `clear_search` pattern from run_fcck.py is NOT needed: type_text clears
  before typing, and every search step types a full new value or empty.

New helpers, all on WD via the existing `_wd`/`_s` plumbing. Exact JSON
payloads (Council 1 A1), always explicit, never relying on defaults:
- `press_keys(d, keys)`: WebDriver Actions API, POST /session/:id/actions,
  one key source:
  `{"actions": [{"type": "key", "id": "keyboard", "actions": [{"type": "keyDown", "value": "\uE007"}, {"type": "keyUp", "value": "\uE007"}]}]}`.
  Batched max 10 pairs per call, then DELETE /session/:id/actions to
  release. Key values are the WebDriver PUA codes: Enter U+E007, Home
  U+E011, ArrowLeft U+E012, ArrowUp U+E013, ArrowDown U+E014, ArrowRight
  U+E015. Note: the legacy Firefox Marionette Keys doc maps ENTER to
  0xE006, not E007; that is the old mapping, not the W3C Actions
  mapping, which is why preflight asserts the recorded `e.key` string
  is exactly `Enter`, not just that a keydown fired. DELETE is best
  effort (Council 1 A2): wrap in try/except, never raise; try
  `_wd("DELETE", _s("/actions"), {})` first, if geckodriver rejects
  the `{}` body retry with body None, and log which form worked.
  A POST /actions that hits the 30 s `_wd` timeout is INFRA (Council 1
  A7): close the session, record the test INFRA, start the next test
  on a fresh session, never retry inside the same session.
  Used for: t01 Enter after each command and ArrowUp recall; t08 Home
  + ArrowRight x70 on #volume; t10 Home + ArrowRight x30 on #volume.
- `pointer_click_at(d, x, y)`: Actions API pointer source, explicit
  origin and parameters:
  `{"actions": [{"type": "pointer", "id": "mouse", "parameters": {"pointerType": "mouse"}, "actions": [{"type": "pointerMove", "duration": 0, "x": 100, "y": 200, "origin": "viewport"}, {"type": "pointerDown", "button": 0}, {"type": "pointerUp", "button": 0}]}]}`.
  Coords are `int(round(...))` (W3C x/y are integers; getBoundingClientRect
  returns floats). Used for: t10 seek click at 50% of #progress rect
  (fixture computes frac from clientX vs rect, so a real pointer click
  at x + w*0.5 is the exact Playwright mouse.click equivalent).
- `dblclick_el(d, js_expr)`: scroll_into_view first, re-read the rect
  after scrolling, elementFromPoint check at the center (reuse the
  `_probe_click` pattern), then one Actions call: move, down, up,
  pause 50 ms, down, up (Council 1 A4). The pause is closer to human
  input and still far inside the double-click interval. Used for:
  t05 dblclick on folder items (fixture has separate click and dblclick
  handlers; two separate Marionette clicks could straddle the OS
  double-click interval, one Actions call cannot). Sharpest hole, named
  by Council 1: the t05 fixture rebuilds the list on every click
  (refresh() does list.innerHTML = '' and recreates all item divs), so
  the second down/up in the same Actions call lands on a NEW div at
  the same coords; whether Gecko still fires dblclick when the target
  node was replaced between the two clicks is UNVERIFIED, so preflight
  must use a re-rendering list mirroring t05.
- `click_nth(d, js_expr)`: scroll_into_view first, re-read the rect
  after scrolling, elementFromPoint check at the center, then
  pointer_click_at at its center (Council 1 A4, Council 2 A7). The JS
  expression must use the nested form where check.mjs nests locators:
  t04 star is `querySelectorAll('#list .msg')[1].querySelector('.star')`,
  not `querySelectorAll('.star')[1]`. Used for: t04 `#list .msg`
  nth(0/1/2) and the nested `.star`; t06 `.day[data-day="12"] .chip`
  nth(0/1). All other clicks use the proven `d.click(css)` Marionette
  element click.
- Fallback, specified exactly (Council 1 A5): keys fall back to no-clear
  raw element/value with PUA codes, the `append_text` pattern
  (`run_fcck.py` lines 61-70: find, then POST /element/{id}/value with
  no clear), never `type_text` (which clears first and would erase the
  typed command). Pointer fallback: `d.click('#progress')` for the t10
  seek (clicks the bar center, which is exactly 50 percent), `d.click`
  where a selector exists, and for dblclick two `d.click()` calls back
  to back. Record any fallback use as a deviation in the log. Note
  (Council 2 A9): two Marionette element clicks are not a proven
  dblclick; if the fixture's dblclick handler does not fire under the
  fallback, the test fails and the failure is recorded as input-path
  degradation, never as a fixture failure and never as a pass.
- `poll_effect(d, js_cond, timeout=5.0)`: mirror of clone1 t09 verify
  polling. Polls a JS condition every 50 ms up to 5 s after a popup
  closes; returns True when seen. Used for every t09 save/apply that
  carries a verify in check.mjs. A missing effect after the deadline is
  a test failure, never silently swallowed.

## Per-test translation (Playwright op to Marionette op)

- t01 terminal: click #cmd, type_text, press_keys Enter per command.
  ArrowUp recall: click #cmd, press_keys ArrowUp, assert the recalled
  value is `history`, then press_keys Enter again and assert the output
  includes `history` (Council 2 A3; check.mjs L72-76). Fixture keydown
  handler checks e.key Enter/ArrowUp/ArrowDown. Before the Enter and
  ArrowUp presses, assert `document.activeElement.id` is `cmd` (Council
  1: focus is assumed, never verified; a metrics read-back or eval
  between type and key press could in principle move focus).
- t02 spreadsheet: type_text per cell (#cell-A1 etc. are plain inputs;
  fixture recomputes on the input event, which Marionette sendKeys
  fires per keystroke). Read back via value. Status text via text().
- t03 video call: clicks + type_text (#chat-input). Plain CSS clicks.
  Name the existence and class asserts in the runner (Council 2 A10):
  camera-off class on #tile-you after cam off (check.mjs L54), screen
  tile present while sharing (L72) and absent after stop (L76, via
  `page.$` so translate as an eval null check, not visible()), Cara tile
  present after invite and absent after remove (L82). These are
  existence or class asserts, not visible() asserts.
- t04 email: type_text search, click_nth for .msg rows and .star,
  type_text compose fields, clicks. Counts via eval querySelectorAll.
- t05 file manager: sort sequence exactly as check.mjs L54-60:
  select_option #sort size-desc, name, size-asc, name, asserting the
  first item after each. type_text #search; clicks; dblclick_el for
  Archive / Old Files 2026 list items; rename dialog via type_text
  #rename-input + clicks on #rename-save / #rename-cancel; dialog-open
  asserts via visible() + value() prefill. Typed cancel (check.mjs
  L79-80): fill `budget2.csv`, click Cancel, assert budget.csv present
  and budget2.csv absent and the dialog closed. Empty rename: type_text
  empty, click Save, assert error visible + dialog open, then Cancel.
  Real file rename: fill `field-notes-7.txt`, Save, assert the new name
  appears and notes.txt is gone. Delete flow (check.mjs L108-117, omitted
  from the first draft of this plan): select photo.jpg, click Delete,
  assert the confirm dialog is visible and its text includes
  `Delete photo.jpg?`, click confirm-no, assert the list length is still
  5, re-select photo.jpg, Delete, click confirm-yes, assert items are
  [Archive, budget.csv, field-notes-7.txt, video.mp4]. Move via
  select_option #move-target + #move-ok. Folder rename: fill
  `  Old Files 2026  ` with leading and trailing spaces (tests trim),
  Save, assert the trimmed name appears, Archive is gone, and the tree
  button reads `Old Files 2026`. Second move: select video.mp4, move to
  Home, assert Old Files 2026 has length 0. Final search `2026`, assert
  only Old Files 2026 shows, clear, dblclick it, assert crumbs and the
  empty state. Tree clicks via d.click on #tree-home / #tree-archive /
  #tree-old-files-2026.
- t06 calendar: clicks on .day[data-day="N"] .day-num; type_text
  #event-title / #event-time / #edit-time; click_nth for chips;
  select-free month nav via #next-btn / #prev-btn / #today-btn. Assert
  the event form is visible after clicking a day (check.mjs L49).
- t07 code editor: type_text #editor (textarea; fixture marks dirty on
  input), clicks, d.refresh() for reload steps (refresh diagnoses and
  raises on hidden body, same as goto). Tab switches via clicks on
  #tabs button[data-file="..."]. Find/replace via type_text + clicks.
  Name the dirty asserts in the runner (Council 2 A10): the tab's dirty
  class after edit and its absence after save (check.mjs L50-51, L55-56,
  L65-66). That class is the only proof type_text fired the input event
  in fixture t07 L83; if the runner omits the dirty checks, a JS set
  fallback could pass silently.
- t08 settings: select_option #theme; d.click on radio
  input[name="accent"][value="blue"] and on the three toggles (native
  inputs, change event fires on real click); type_text #display-name;
  click #volume then press_keys Home + ArrowRight x70; d.refresh() for
  reload steps; isChecked via eval el.checked; search via type_text.
  Live volume asserts (Council 1 A6): value is 50 after clicking
  #volume, 0 after Home, 70 after the ArrowRight batch, checked
  immediately, not only via the final #volume-value text. If Home does
  not reset, fail fast: ArrowRight x70 from a click-changed value (say
  51) clamps at 100 instead of landing on 70. Final toggle guard
  (Council 2 A6): the last step (check.mjs L98) is page.check on
  #notif-toggle after reset + reload, when notif is already On, so
  Playwright check is a no-op; guard with isChecked and click only if
  unchecked, or a plain click would turn notif Off. Also assert: swatch
  background blue (L49-50), section visibility (L33, L76-85), no-match
  message (L84-85), and the reset + second reload asserts (L88-98).
- t09 multi-window: openPopup = click detail/prefs button, wait for a
  new handle, switch, settle, require_visible. Interact in the popup
  (type_text #title-input, select_option #theme-select), then
  clickAndClose = click the popup close button, wait for the close
  (handle disappears), switch back to main, poll_effect up to 5 s for
  the expected main-window effect. Close race tolerance (Council 2 A4):
  if the Marionette element click raises when window.close runs during
  dispatch, tolerate it exactly as check.mjs L60-72 does (tolerate a
  `has been closed` error only when the popup really closed within
  2 s), then await the close, then poll verify 5 s every 50 ms; the
  verify poll is the arbiter. Prefill asserts: detail window prefills
  Alpha, then Alpha v2 on reopen (check.mjs L99, L109). Status assert
  after the first rename: status includes `Renamed alpha to Alpha v2.`
  (L104). Cancel: clickAndClose on #cancel-btn (await the close first),
  then dwell 500 ms, then read the title immediately, no verify
  (L128-133). Two-popups step: open detail popup, switch back to main
  WITHOUT closing it, open prefs popup, assert handles count is 3,
  close prefs, verify dark, switch to the still-open detail popup,
  rename, close, verify. Final assert: handles count is 1 after all
  popups closed (L149-150).
- t10 music player: clicks; sleeps as in check.mjs (700 ms after play,
  400 ms paused, 500 ms after resume, 350 ms after sampler); sampler:
  eval with top-level `return new Promise(...)` sampling
  #position data-seconds every 10 ms for 500 ms, taking the minimum
  (Y4d lesson: top-level return is required, Marionette runs the script
  as a function body; /execute/sync awaits a returned promise).
  Sampler ordering and thresholds (Council 2 A5): capture posBeforeNext,
  START the sampler promise BEFORE the now-playing assert (a
  now-playing assert first costs round trips, the timer advances 1 per
  100 ms, and a late sampler can read min above 2 and fail a correct
  reset), then check now-playing, then await the min; fail if min is
  greater than 2 or min is greater than or equal to posBeforeNext.
  Advance assert: after sleep 350, position must be at least 2, not
  just past 0 (check.mjs L93-95). Volume: click #volume, Home,
  ArrowRight x30, with the same live asserts as t08 (50 after click,
  0 after Home, 30 after the batch, checked immediately). Seek:
  pointer_click_at at 50% of #progress rect, then read the position
  IMMEDIATELY and require 85 to 100 (check.mjs L103-106; the timer
  keeps running, so a delayed read can exceed 100). Shuffle/repeat/
  search/track clicks as in check.mjs.

## Fresh-profile equivalence

t07, t08, t09 fixtures persist state in localStorage (editor files,
demo-settings, project titles + theme). A Playwright check gets a fresh
browser profile per run, so the live run must clear that state or a
re-run starts from stale values and fails its initial checks. Every
test starts with, in this exact order (A3): `new_tab(url)`, then
`localStorage.clear()` plus `sessionStorage.clear()` (parity with
`run_agyq2.py` open_fixture), then `refresh()`, only at test start and
on retry re-entry, never mid-test. The order matters: clearing before
navigation would clear the wrong origin (all fixtures share one origin
on 127.0.0.1:8771, so the clear must run on the fixture origin). This
is the proven precedent in `run_live.py` run_t05 and `run_fcck.py`
q04. This is harness setup, not part of the spec flow. It does not
break intra-test persistence: t07/t08/t09 save then reload within one
test, and the plan's per-test sections do no mid-test clear, so those
writes survive.

## Hidden-body handling (Y4d ladder, reused verbatim)

Do NOT write a new ladder. Import and reuse `ensure_visible` from
`run_agyq2.py` verbatim (Council 3 amendment A2). Its design: 8.0 s total
budget enforced by deadline; poll up to 2.0 s for the extension's own
removal; verified tz-hidden removal only for TZ_STUCK_V1 (the removal
flag is set ONLY when the post-remove snapshot proves the class is gone);
rebootstrap in the remainder; FIXTURE_FAILURE raises
FIXTURE-UNAVAILABLE immediately without burning tabs. Correction to the
first draft of this plan: the 2 s poll and 8 s budget are design numbers,
not measured removal times. Y4d's rerun had 0 hidden-body encounters in
20 tests, so the poll/removal/rebootstrap paths never fired for a real
hidden body; removal was never measured live.
- Every navigation wraps `goto`/`refresh` with `allow_hidden=True`
  followed by `ensure_visible` (the wrapping Y4d uses in
  `run_agyq2.py` open_fixture). The bare `goto`/`refresh` choke point
  raises INFRA immediately on non-VISIBLE, so the plan's first-draft
  poll-only rule could not run at those points.
- Every popup tab goes through `ensure_visible` at its
  `require_visible` point, and after every `switch` (including both
  switches in the t09 two-popup step, not only switch-back to main).
- If `ensure_visible` swaps tabs, reload the fixture on the new tab
  exactly as `open_fixture` does (goto + clear + refresh +
  `ensure_visible` again, one final fresh tab before finalising INFRA).
  The swapped tab handle is appended to `d.opened_tabs` so the session
  cleanup closes it (rebootstrap keeps it out of opened_tabs by design,
  and this runner uses one session per test, so an unappended swap
  would leak a test tab in Zen).
- A test that passes after a verified removal is a FLAGGED pass, counted
  separately from clean passes. The flag is recorded in `r.details`
  under Y4d's field name `tz_hidden_removed`.
- If a tab diagnoses non-VISIBLE and the ladder returns not-ok, fail
  that test as INFRA, close its tab, and continue with the next test.
  Never hang the suite on one tab.
- Circuit breaker (A5): abort the suite after 2 consecutive INFRA
  failures and report, instead of grinding through the remaining tests
  on a wedged Zen.

## Preflight step 0 (inside my slot, before t01)

The /actions helpers have never run against live Zen. Before t01, open a
scratch tab with a probe page served from the same loopback server. The
probe page carries: a text input recording keydown `e.key` strings; a
range input (min 0, max 100, value 50); a div recording pointer click
clientX/Y; a re-rendering list that rebuilds its nodes on click,
mirroring t05 fixture lines 103-117; and a filterable list for the empty
clear probe. Prove live, and FAIL the preflight (blocking t01) on any
miss (Council 1 A3, Council 2 A1/A9):
- (i) Type into the text input, press_keys Enter and ArrowUp, assert the
  recorded `e.key` strings are exactly `Enter` and `ArrowUp`, and assert
  `document.activeElement.id` is the input before each press.
- (ii) On the range input: click leaves value 50, Home sets 0,
  ArrowRight x70 in 10-pair batches sets 70. This proves the full 70-key
  batch and that focus survives across batches.
- (iii) Pointer click at a known point AFTER scrolling the probe page,
  reading back clientX/Y.
- (iv) dblclick_el on the re-rendering list: assert the dblclick count
  is 1. A static-div dblclick proves nothing about t05, where the
  target node is replaced between the two clicks.
- (v) Empty clear probe: type a value into the filter input, type_text
  empty, assert the filtered list updates. This proves Marionette
  /clear fires the input event; if it does not, use clear_search (JS
  set + input event, run_fcck.py lines 48-53) for ALL empty steps
  (t02 B1 '', t04/t05/t08/t10 search '').
- (vi) Test the key fallback in the same preflight: no-clear raw
  element/value with PUA codes (append_text pattern) on both a text
  input (Enter, ArrowUp) and a range input (Home, ArrowRight).
If /actions fails, fall back exactly as specified in the helpers section
(no-clear raw element/value for keys, d.click where a selector exists,
two d.click() for dblclick) and record the fallback as a deviation in
the log. Do not start t01 until the input path is proven one way or
the other.

## Run mechanics

- Server: the runner's own loopback server on port 8771 (fresh port, no
  collision with Y8b/Y9 servers), serving the suite copy from the laptop
  at /tmp/y14-server (suite copied from main ed78e83, md5-verified).
- One WebDriver session per test (WD context manager, always deleted in
  finally). One new tab per test. Test tabs closed at the end of each
  test; user tabs never navigated, typed into, or clicked.
- Logs: per-step JSONL at /tmp/worker-y14-live.jsonl (Runner.step),
  Y11 metrics sibling file (LIVE_METRICS default, run id y14-batch3).
- Env: LIVE_SERVER_ROOT=/tmp/y14-server LIVE_SERVER_PORT=8771
  LIVE_LOG=/tmp/worker-y14-live.jsonl LIVE_RUN_ID=y14-batch3
  WD_PORT=4452. Correction to the first draft of this plan (A1): 4449
  is Y9's port (run_agy_y2.py), 4450 is Y13's, 4451 is Y8b's, so 4452
  is the next free WD port. Y11b/Y6c ports are UNVERIFIED from the
  files read; the launch gate below verifies 4452 is actually free.
  Pid/log files are keyed by WD_PORT, so a collision would also
  collide there.
- Launch gate (A4), all fail-closed before any Zen driving: sweep for
  stale geckodriver processes by PID (pgrep, parent PID, cmdline; kill
  orphans by PID only, never by port alone or pkill -x geckodriver);
  Zen alive; Marionette 2828 responsive; server port 8771 free, or
  proven to serve /tmp/y14-server (probe a Y14 fixture, fail closed
  on foreign-root reuse; start_server() silently reuses any listening
  server on the port); WD port 4452 free and predecessor ports
  8767/8768/8769/8770 and 4448/4449/4450/4451 free or owned by no live
  runner; no other runner process live; the live slot is mine (Y13
  DONE posted) and the Muse go-order is in force. Note: run_live.py
  enforces no flock/zen_dom.lock; the queue is coordinated by Muse,
  so the gate checks for a live runner process instead of a lock file.
- In run_batch3.py, construct LiveMetrics exactly as run_live.main()
  does (A6) and verify the -metrics.jsonl sibling exists after
  preflight.
- Order: b3-t01 through b3-t10 in suite order. On a test failure, record
  and continue with the next test (a failure in one test must not kill
  the other nine). One retry per failed test at most, only if the failure
  is INFRA (hidden body, session death), never a re-run to flip a real
  assertion failure.
- Report: per-test PASS/FAIL with ms, total wall time, steps, hidden-body
  encounters with diagnosis. Special attention in the report to t05, t09,
  t10: whether the Y3 races stay fixed live.

## Evidence contract

Commit + push on todolist-push: run_batch3.py, this plan (updated with
council/redteam verdicts), improvements/worker-y14-batch3-live-log.md
with exact commands, outputs, and commit hash, and the run report.
A bare done without runnable evidence is returned unread.

## Polling while waiting for the slot

Poll origin/todolist-push about every 15 min for Y13 DONE and for the
Y12 headless verdict on the merged suite. Do not drive Zen before the
slot opens. Prep (this plan, council, redteam, runner code, ship to
laptop, syntax check) all happens before the slot.

## Runner status (19:40 21/11)

- `tests/realistic/run_batch3.py` written (1908 lines): all 10 tests
  (b3-t01..b3-t10), the /actions helpers with exact Council 1 payloads,
  the fallback routing (raw element/value keys, d.click('#progress')
  for the seek, two d.click() for dblclick, JS el.click() for
  click_nth), ensure_visible reuse, the launch gate (LIVE_SLOT_OK=1,
  Zen alive, Marionette 2828, ports 8771/4452 free, no geckodriver or
  other runner live), the circuit breaker, one INFRA-only retry, and
  LiveMetrics constructed as run_live.main() does. Compiles
  (py_compile OK), imports cleanly on the VM, all 10 tests registered.
- `tests/realistic/run_batch3_probe.html` written (probe page for
  preflight step 0: text input, range input, scrolled pad, re-rendering
  list, filter list).
- Not yet shipped to the laptop, not yet run. Ship + syntax check on
  the laptop happen before the slot. The t10 sampler stays in the
  Promise form pending the Redteam verdict on whether Marionette
  /execute/sync awaits a returned Promise; the sampler is one function
  (sample_position_min), so swapping to a two-eval form is a small
  change if the verdict says the Promise form is unsound.
- Redteam verdict still pending at the time of this edit.

## Amendments applied

- Council 3 (AMEND, 19:28 21/11): A1 WD_PORT 4449 to 4452 + LIVE_RUN_ID
  + launch-time port verification; A2 reuse ensure_visible verbatim
  instead of the invented poll-only ladder; A3 pinned clear order
  (new_tab, clear local+session storage, refresh); A4 launch gate
  (stale-geckodriver sweep by PID, Zen alive, Marionette responsive,
  port-free or proven-root server, no other runner live, slot + go
  in force); A5 circuit breaker (abort after 2 consecutive INFRA);
  A6 LiveMetrics constructed as run_live.main() does; A7 corrected
  the WD port claim and the "Y4d measured removal" claim.
- Council 1 (AMEND, 19:33 21/11): A1 exact Actions JSON payloads in plan
  + code (origin viewport, pointerType mouse, button 0, duration 0,
  int-rounded coords); A2 DELETE /actions best effort ({} body first,
  retry body None, log which worked); A3 strengthened preflight
  (exact e.key asserts, range input 50/0/70, full 70-key batch,
  re-rendering dblclick probe, scrolled pointer probe); A4 scroll +
  re-read rect + elementFromPoint in pointer helpers, dblclick sequence
  move/down/up/pause 50 ms/down/up in one call; A5 exact fallback
  (no-clear raw element/value, never type_text; d.click('#progress')
  for the seek; two d.click() for dblclick); A6 live volume asserts
  (50/0/70/30 checked immediately); A7 hung-Actions rule (30 s timeout
  is INFRA, close session, fresh session for the next test).
- Council 2 (AMEND, 19:33 21/11): A1 empty clears (prove /clear fires
  input in preflight or use clear_search for all empty steps); A2 t05
  delete flow + exact typed strings + sort sequence; A3 t01 Enter after
  ArrowUp recall; A4 t09 close race tolerance + cancel ordering
  (await close, dwell 500, read) + prefill/status/final-count asserts;
  A5 t10 sampler starts before the now-playing assert + thresholds
  (min > 2 or min >= posBeforeNext fails; advance >= 2) + immediate
  seek read 85-100; A6 t08 final toggle guard (isChecked, click only
  if unchecked) + omitted asserts (swatch, sections, no-match, reset);
  A7 click_nth nested star locator + scroll before measuring; A8 clear
  order (already covered by Council 3 A3); A9 preflight extensions
  (range probe, re-render dblclick probe, empty clear probe); A10 t07
  dirty asserts + t03/t06 existence/class asserts named in the runner.
- Redteam: verdict pending at the time of this edit; fold it in when
  it arrives.
