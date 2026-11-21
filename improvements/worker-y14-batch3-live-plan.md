# Worker Y14 run plan: clone1-batch3 FIXED suite, LIVE on Zen

Worker: Y14 (Muse live runner). Owner order: full autonomy, machine handed
over 18:24 21/11, owner out and busy. Lauren Tan direction applies.
Slot: AFTER Y13 reports completion. Live queue: Y8b E1, Y9 agy-y2, Y11 proof,
Y6b nested, Y13 codex-y5, then Y14. One live runner at a time, no exceptions.

## Suite under test

Merged fixed suite, commit 1d23532 on main (Y15 D1 fix on top of Y10's
reconciled best of both; re-staged by Y14b 21/11, see "Re-stage (Y14b)"
below):
- t05: clone1 fixture (rename dialog Save/Cancel, empty shows error and
  stays open) + Y10 checker (novel names, typed cancel, dialog-open asserts,
  non-empty folder rename with trim, tree-button click).
- t09: clone1 checker (clickAndClose with 5 s verify polling) + Y10 cancel
  dwell 500 ms, no verify for Cancel.
- t10: Y15 checker (1d23532, 353 lines): same-task exact-zero reads after
  every playing Next (playing, shuffle, wrap), 500 ms sampler as second
  witness (min > 2 or min >= posBefore fails), three-point advancing
  checks (gain >= 2 per 350 ms sleep, 2..11 bound on the middle read),
  frozen exact-zero checks after paused Nexts (playing, shuffle, wrap),
  two-point resume reads after every frozen resume (2..11 + second
  gain >= 2). Sampler kept as second witness. t05/t09 untouched,
  fixture untouched. Documented limits (README): slow-side clock
  0.6x-1.0x not distinguished, later advancing read gain-only with no
  upper bound, no advancing check after the playing wrap (redteam
  round-6 escapes R1/R2/R3b, landed over the BLOCK per a pre-set
  stopping rule; they are documented limits, not gates). CORRECTION
  (Y14b fix pass, redteam H2/H3): the live run inherits these blind
  spots, it does not test them. The playing wrap is reset-only tested
  (liveness after the wrap is untested: a wrap that stops the timer
  passes exact-zero + sampler and is masked by the next playlist
  click), and the two later advancing reads are gain-only with no
  upper bound (a late position jump passes). The earlier claim that
  "the live run is the real test" for R1/R2/R3b was wrong and is
  withdrawn. The runner must translate the checker faithfully, so
  these checks cannot be added to the runner alone; a post-wrap
  advancing check and a later-read upper bound belong in a future
  checker revision (proposed follow-up, flagged to Muse).
- t01-t04, t06-t08: unchanged from clone1 batch 3 (Y3 passed them 7/10
  overall; these 7 passed then). Byte-identical between ed78e83 and
  1d23532 (git diff --stat: only t10 check.mjs + README changed).
- Headless evidence (Y10): 9/9 mutation probes v2 matched, 10/10 x7 runs
  (sequential about 24-27 s, load run 3 concurrent suites about 74 s each).
- Y12 verified the merged suite headless (see 'Y12 headless verdict'
  below); its D1 defect is fixed by Y15 in 1d23532, which this re-stage
  adopts. A Y12 FAIL on a test already run live means that live result
  is provisional until the fix lands and the test is re-run live.

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
  U+E011, ArrowLeft U+E012, ArrowUp U+E013, ArrowRight U+E014, ArrowDown
  U+E015. Note: the legacy Firefox Marionette Keys doc maps ENTER to
  0xE006, not E007; that is the old mapping, not the W3C Actions
  mapping, which is why preflight asserts the recorded `e.key` string
  is exactly `Enter`, not just that a keydown fired. Redteam D1: the
  first draft had Right and Down swapped (ArrowDown U+E014, ArrowRight
  U+E015). The W3C WebDriver key table, the Selenium wire table,
  go-selenium and the Haskell webdriver bindings all agree: Right
  U+E014, Down U+E015. The swapped codes would have failed the t08/t10
  volume steps, and the preflight range test would have caught it
  fail-closed, but the slot would have burned on a preflight abort.
  DELETE is best
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
  WITHOUT closing it, open prefs popup, assert the handle count is
  handles_before + 2, where handles_before is captured at t09 start
  (redteam D2: check.mjs counts 3/1 in a fresh Playwright context with
  only test pages; live handles() returns every tab/window in the
  attached Zen, so an absolute 3/1 is a guaranteed false-fail with any
  user tab open). Save the detail popup handle explicitly at open time,
  since the later switch to the still-open detail popup needs it.
  Close prefs, verify dark, switch to the still-open detail popup,
  rename, close, verify. The close-wait (_wait_handles_gone) raises on
  timeout and never proceeds on timeout, so a missed Cancel click cannot
  pass silently. Final assert: handles count is back to handles_before
  after all popups closed (L149-150).
- t10 music player: clicks; sleeps as in check.mjs (700 ms after play,
  400 ms paused, 500 ms after resume, 350 ms after sampler / advancing
  reads); exact-zero reads run the Next click and the position read in
  the SAME in-page task (eval click + return, Y15 comment: page JS is
  single-threaded, the click handler runs synchronously, so no 100 ms
  timer tick can land between reset and read; a plain d.click followed
  by a read cannot guarantee that); sampler: eval with top-level
  `return new Promise(...)` sampling #position data-seconds every 10 ms
  for 500 ms, taking the minimum (Y4d lesson: top-level return is
  required, Marionette runs the script as a function body; /execute/sync
  awaits a returned promise).
  Sampler ordering and thresholds (Council 2 A5): capture posBeforeNext,
  START the sampler promise BEFORE the now-playing assert (a
  now-playing assert first costs round trips, the timer advances 1 per
  100 ms, and a late sampler can read min above 2 and fail a correct
  reset), then check now-playing, then await the min; fail if min is
  greater than 2 or min is greater than or equal to posBeforeNext.
  Fail-closed rule (redteam D3): run_batch3.py raises a test failure on
  a None or non-numeric sampler result, never defaults it to 0 and never
  skips the assert, so a sampler that proves nothing cannot pass
  vacuously. The sampler start gap (click return to first sample, one
  HTTP round trip) is derivable from the step log timestamps in
  /tmp/worker-y14-live.jsonl; on a min in 3-5 with a gap over 200 ms,
  treat as INFRA/timing and retry once rather than recording a fixture
  failure. Advancing checks (Y15): after the sampler ends, read,
  sleep 350, read again (gain >= 2 AND 2..11), sleep 350, read again
  (gain >= 2, no absolute bound). Frozen Nexts: pause, Next, read
  exactly 0, resume with Play, sleep 350, read 2..11, sleep 350, read
  again (gain >= 2 AND 2..11). The frozen value was exactly 0, so the
  first resume read is itself a gain check. Prev sequence after the
  frozen Next is two clicks (River Road, then Morning Light), because
  the frozen Next left now-playing on Night Drive. Volume: click
  #volume, Home, ArrowRight x30, with the same live asserts as t08 (50
  after click, 0 after Home, 30 after the batch, checked immediately).
  Seek: pointer_click_at at 50% of #progress rect, then read the
  position IMMEDIATELY and require 85 to 100 (check.mjs L169; the
  timer keeps running, so a delayed read can exceed 100). Shuffle/repeat/
  search/track clicks as in check.mjs. The wrap Nexts: play 700 ms
  first so the pre-click position is >= 2 (a wrap that fails to reset
  is only observable when the pre-click position is nonzero), then the
  playing wrap gets the same exact-zero + sampler treatment, and the
  frozen wrap gets the frozen exact-zero + resume treatment. The old
  supplementary D1 diagnostic probe (details-only Next while paused
  at the end of t10) is REMOVED in the re-stage: Y15's checker now
  carries the real frozen-Next steps, so the probe is superseded.

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
  That rule is for MAIN test tabs only. For popup tabs (t09)
  `ensure_visible` is called with allow_swap=False, a popup that stays
  hidden after poll plus removal is INFRA, and the main fixture is NEVER
  reloaded into a popup slot (redteam D4: rebootstrap returns an
  about:blank tab or a reused visible test tab, never the popup
  document, so reloading the fixture there would put the runner on the
  wrong document and record the failure as a step failure instead of
  the INFRA hidden-body event it was).
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

## Line-by-line verification (redteam demand, 19:47)

run_batch3.py was diffed against all 10 check.mjs files before the slot.
The two items the redteam flagged as missing from the plan text are both
present in the runner: t04 asserts #empty visible on a no-match search,
and t06 asserts the #form-day label 'June 12, 2026'. The plan lines for
t04/t06 are summary-level; the runner is the faithful translation.
Details-only differences (no pass/fail effect): t01 historyLines counts
non-empty output lines while check.mjs counts a regex match; t10 records
a supplementary D1 diagnostic that does not affect the suite verdict. No
assert in any check.mjs was found missing from the runner. A second
redteam pass on run_batch3.py itself is required before the slot opens.

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
  `document.activeElement.id` is the input before each press. Then press
  ArrowRight and ArrowDown on the text input and assert the recorded
  `e.key` strings are exactly `ArrowRight` and `ArrowDown`, so a future
  Right/Down PUA swap is named directly instead of surfacing as a wrong
  volume number (redteam D1).
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
- (vii) Promise proof (redteam D3): eval `return new Promise(r =>
  setTimeout(() => r(42), 100))` must return 42, plus a control showing
  a bare IIFE returns null (the Y4d lesson). This proves on this Zen
  that /execute/sync awaits a returned Promise (W3C Execute Script
  13.2.1; Marionette bug 1398095, Firefox 67), which the t10 sampler
  depends on.
- (viii) window.open popup proof (redteam D5): click #probe-popup-btn,
  which opens run_batch3_probe_popup.html with width=500,height=400
  features, assert a new handle appears, switch to it, assert visible,
  close it, switch back, assert the handle count returns to baseline.
  This proves the window case live: t09 popups are window.open with
  features, which Firefox opens as separate windows, not the
  <a target=_blank> tabs proven live by run_t05/run_t06.
If /actions fails, fall back exactly as specified in the helpers section
(no-clear raw element/value for keys, d.click where a selector exists,
two d.click() for dblclick) and record the fallback as a deviation in
the log. Do not start t01 until the input path is proven one way or
the other.

## Run mechanics

- Server: the runner's own loopback server on port 8771 (fresh port, no
  collision with Y8b/Y9 servers), serving the suite copy from the laptop
  at /tmp/y14-server (suite copied from main 1d23532, md5-verified; see
  the pinned ship procedure in the re-stage section below).
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
- Launch gate (A4), all fail-closed before any Zen driving: the /proc
  tokenizer scan (_scan_other_runners) for a live runner process or a
  codex executor driving a browser (replaces the old pgrep -f sweep,
  which missed bare-relative launches and false-positived on path
  mentions); Zen alive; Marionette 2828 responsive; server port 8771
  free, or proven to serve /tmp/y14-server (the runner fetches all
  12 browser-served files, 10 fixtures + t09 detail.html/prefs.html,
  over HTTP after start_server() and compares each md5 to the
  on-disk root, refusing on mismatch or fetch failure; start_server()
  silently reuses any listening server on the port; known limits: a
  server that redirects or serves different bytes per User-Agent
  could still fool the check, adversarial behavior outside the
  threat model); WD port 4452 free
  and predecessor ports 8767/8768/8769/8770 and 4448/4449/4450/4451
  free or owned by no live runner; no other runner process live; the
  live slot is mine (Y13 DONE posted) and the Muse go-order is in
  force. Note: run_live.py enforces no flock/zen_dom.lock; the queue
  is coordinated by Muse, so the gate checks for a live runner process
  instead of a lock file. A flock lock held for the whole run would
  close the remaining gate shapes (renamed copies, spoofed argv[0]),
  but only fleet-wide, so that is a Muse-level fleet decision, not a
  change for this runner. run_one re-scans at the top of each test
  (redteam M2): a runner starting mid-suite aborts that test as INFRA
  before any tab is driven. Mid-test window (redteam F7): a runner
  starting mid-test, after the re-scan and during the test's WD
  session, is caught only at the next test's re-scan; the other
  runner's own gate is the backstop for documented launch forms.
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

## Y12 headless verdict (19:40 21/11, commits 897ca17 + ccebbf4)

Y12 independently verified the merged suite (ed78e83): 6/6 full suites
10/10 PASS (sequential x3 about 23-27 s, load x3 about 65-66 s), 11/12
mutation probes matched. Overall: SOUND WITH NOTED DEFECTS.
- t05 SOUND (4/4 probes). t09 SOUND (4/4 probes).
- t10 DEFECT D1 (minor, narrow, EXECUTED): the sampler accepts min
  <= 2, so a nextTrack that resets position to 1 (or 2) passes; probe
  t10-P2 (reset to 1) exited 0 with no failures. The sampler never
  asserts the reset value its own README states ("plays from position
  0"). Remedy (Y12 council t10): exact-zero assert on a clock-frozen
  path (pause before Next, require exactly 0, resume, keep advancing
  check). D1 does not block the suite's use; it blocks a clean SOUND
  label only.
- Consequence for this live run: SUPERSEDED by the re-stage (Y14b,
  1d23532). The paragraph below described the min <= 2 runner plus
  the supplementary D1 probe as the current state; both are gone.
  The Y15 checker plus the re-stage section govern now. (Original
  text kept for the record: a live PASS on t10 did NOT prove an
  exact-zero reset, because my runner translated the merged checker
  (min <= 2) faithfully. The live run therefore carried a supplementary
  diagnostic probe at the end of t10 (after the suite steps, recorded
  in r.details, NOT affecting the suite PASS/FAIL): click Next while
  paused, read #position immediately, record the value (want exactly
  0). That probe answered live whether the fixture resets to exactly 0
  or to 1, which is the datum D1 leaves open. If the probe read 1,
  the live fixture carried the D1 defect and the t10 live PASS was
  reported with that qualification.)
- UPDATE (19:40 21/11, from MEMORY.md): Y15 has been spawned to FIX D1
  per the council t10 remedy (exact-zero on a clock-frozen path, P2
  must FAIL + 3x 10/10), landing on main BEFORE Y14 runs live. So the
  suite under test will CHANGE: I must re-stage the suite from the new
  main HEAD (not ed78e83) when Y15 lands, re-verify md5s, and update
  my t10 translation to match Y15's new checker (the supplementary D1
  probe above is then superseded by the real suite step, and comes out
  or stays only as a duplicate diagnostic if Y15's step differs). Do
  NOT run live on the ed78e83 copy once Y15's fix has landed.
- Other Y12 notes (static, not gates): H1 novel names could be
  hardcoded by a future fixture; H3 t09 6 s delivery would false-fail
  on the 5 s poll cap (fixture posts synchronously and locally, so no
  realistic 6 s delivery exists here); H4 t10 position never read
  after Prev / playlist / shuffle / wrap Next.

## Re-stage (Y14b, 21/11)

Y15 landed D1 on main as 1d23532 (log 3b50e94). Y14b re-staged the
runner from the new HEAD (old staged suite ed78e83, new 1d23532;
only t10 check.mjs + README changed, t01-t09 byte-identical).
Changes to run_batch3.py (+452/-35 vs 70061e2, changed defs only:
header/imports, run_b3_t10, run_preflight, H2 helpers, launch_gate):
- t10 translation rewritten to the new checker (see the t10 section
  above): exact_zero_next() same-task click+read helper, three
  exact-zero reads (playing, shuffle, wrap), sampler as second
  witness, three-point advancing checks, frozen Nexts with resume
  reads, double Prev, wrap gates (700 ms play, posBefore >= 2).
  Supplementary D1 probe REMOVED (superseded by the real steps).
- H2 fix (Y13r f48b54c, Y13f's tokenizer copied verbatim from its
  working tree): _script_basename_is_runner, _is_python_token,
  _argv_tokens, _is_runner_cmdline, CODEX_REFUSE_MARKERS, _ppid_of
  all byte-identical to run_codex_y5.py except the _is_runner_cmdline
  docstring tail, which records this Y14 application instead of the
  "must apply" note (logic identical); new _scan_other_runners()
  helper; launch_gate() pgrep -f sweep replaced by the scan;
  run_preflight() re-checks at the top before any tab opens.
- Verification (all in improvements/worker-y14b-restage-log.md):
  py_compile OK, import OK (10 tests); H2 probe 21/21 PASS (14 unit
  synthetic cmdlines + 7 live /proc cases; wrappers themselves are
  hits by design); transcription 72 ordered assert alignments PASS
  (69 checker asserts + 3 volume extras) + D1 probe gone + 3
  exact-zero call sites + sleep counts 0.7x3/0.5x1/0.4x1/0.35x10 +
  sampler fail-closed; launch-gate dry run 4/4 PASS (quiet passes,
  bare-relative refuses, mention-only passes, no slot token refuses).
- Applicability notes (honest, not skipped): this runner has NO
  manifest mechanism and NO STEP_COUNTS audit mechanism, so the
  --verify-manifest cases and audit simulation do not apply here;
  the suite is verified by md5 against the git HEAD at ship time.
  Adding a manifest would be new design work beyond a re-stage.
- Ship-time md5 procedure (Council 3 F6, pinned; corrected by the
  fix re-review, Council 3 R1-R3): after copying the suite to
  /tmp/y14-server on the laptop, run from that dir:
  find clone1-batch3 -type f \( -name 'check.mjs'
  -o -name 'fixture.html' -o -name 'detail.html'
  -o -name 'prefs.html' -o -path '*/lib/*' -o -name 'run_all.mjs'
  \) -exec md5sum {} + | sort -k2
  (the suite lives at /tmp/y14-server/clone1-batch3/..., NOT under
  tests/realistic/; the earlier draft's find path was wrong and
  fails with "No such file or directory"). The file set covers
  every check.mjs, every fixture.html, the t09 detail.html and
  prefs.html the t09 fixture opens via window.open, lib/, and
  run_all.mjs. Per-test READMEs and results.json are not
  load-bearing (docs / previous-run output) and are not in the set.
  Compare against these expected md5s (suite HEAD 1d23532,
  computed from git blobs on the VM):
  run_all.mjs 526e418175c47f214004653402a63cc0;
  lib/browser.mjs 6068b11577e32bd2d299b00ae20a097f;
  lib/server.mjs 7ddd6b6a906292a6ed73e5d29c4d7ec4;
  t01 check.mjs caa89e9db0474f7ca1aa3e62e2a3a0c3,
  fixture.html b320cf07f567c05fc6fc9eff2c5f9e59;
  t02 check.mjs bf00442896b3c9dae0dd21abe983dfa7,
  fixture.html 9cd51959f33b086896635e3ff77a57cb;
  t03 check.mjs 2ff259c4b1c3f95e01ebe55bd4f626f1,
  fixture.html 33cafeca62226c24bc3031f856bf79b2;
  t04 check.mjs 4f6a15d566d26d094c749164f653681f,
  fixture.html 16d10cf31d141508a2315e8ed77ac705;
  t05 check.mjs c8d8bad8dd0bb5a8b8b137e7a9f98bce,
  fixture.html 72d0265a7097e1a322a6e7c861c1e9d8;
  t06 check.mjs 19dd37283be377a0654536952e50eb57,
  fixture.html 9f590523901d995757602184c4d55d98;
  t07 check.mjs a7181b4aa7b702cd9f91a475190696b4,
  fixture.html abc6d86195965f2ae2d64206d48dc1ac;
  t08 check.mjs f25fa0ce937059244d13f0b0fb93b128,
  fixture.html d588dc93c2a2e61dbe79ff025a9b7ede;
  t09 check.mjs 860a6cfef8002a94ef8d656361f5a233,
  fixture.html 7da064f7dcd94bcc3cad941e1f75e137,
  detail.html 40dfc0db44aa8448341587f8559b773a,
  prefs.html 1169a1d5a1a6599093bdedac9c2aa74e;
  t10 check.mjs c55ef3c792b2faaea7c829818eb6420b,
  fixture.html eb814c944dab6279417c6182e1950876.
  Also md5sum run_batch3.py (from /tmp/y14-server, where the runner
  is shipped) and compare against the md5 recorded in the re-stage
  log's fix-pass-2 entry (value filled in after the fix-pass-2
  commit). Paste the actual command output into the live log at ship
  time. Any mismatch refuses the slot.
- Council (3) + redteam over the re-stage diff f732d6a: Council 1 GO
  (t10 translation 69/69, watch item: middle advancing read margin);
  Council 2 AMEND (Fix 1: -m module form bypasses the gate, four-line
  fix; Fix 2: stale "pgrep sweep" comment); Council 3 AMEND (F1-F7
  plan/log wording + this pinned ship procedure); redteam BLOCK
  (H1 gate bypass x5, H2 wrap false-pass, H3 late jump, H4
  miscalibrated 2..11 bounds, M1 foreign server reuse, M2 no re-scan,
  M3 codex false-positive, M4 L413, L1/L2). Adjudication (Y14b fix
  pass, recorded in the log): BLOCK downgraded to AMEND with fixes.
  Fixed: -m + -c import coverage, codex anchor + plain-codex warning,
  served-fixture md5 check, per-test re-scan, now-playing assert moved
  out of the sampler-to-advancing path, int() truncation removed,
  F1-F7. Declined with reasons: flock lock (fleet-wide design
  decision, flagged to Muse; a lock taken by only this runner gives
  no guarantee), renamed-copy/shebang/spoofed-argv[0] forms
  (adversarial, outside the accidental-collision threat model),
  post-wrap advancing check and later-read bound in the runner
  (spec divergence from the checker; checker follow-up proposed for
  a future suite revision), caps re-derived in the runner
  (divergence; margin analysis recorded instead). Fresh council +
  redteam over the fix diff only, then ship.
- H4 margin note (redteam + Council 1 watch item, corrected by the
  fix re-review): the 2..11 bound on the middle advancing read was
  copied verbatim from check.mjs, whose timing is Playwright (~10 ms
  round trips, correct value near 8). The runner's path is 850 ms +
  about 3.5 effective Marionette round trips (Council 1 counts 3,
  Council 3 counts 4; the advancing read's own transit contributes
  about half a round trip, so the two counts bracket the true value
  and differ by at most 0.19 ticks). At the measured laptop rates
  (Y11b proof: eval median ~2 ms, click steps ~56 ms for ~3 POSTs,
  so a round trip is ~2-19 ms) the correct fixture reads about 8-9
  (8 at ~2 ms/round trip, 9 at ~19 ms), margin 2 discrete ticks
  (1.93-2.44 continuous). At 50 ms/round trip it reads 10 (margin
  1); the bound first fails when round trips exceed roughly 70-85 ms
  (tick-phase dependent) and fails surely at ~100-117 ms. The fix
  pass moves the now-playing assert (2 round trips) out of the
  sampler-to-advancing path at the playing and shuffle Nexts, raising
  the first-fail threshold from ~50 ms to ~70-85 ms. SHIP CONDITION
  (Council 1): the live run re-measures the round-trip time and
  honors this watch item. The live run must watch
  details.positionAdvancingAfterNext and
  details.positionAdvancingAfterShuffleNext: if either reads 11
  repeatedly, report the thin margin explicitly instead of calling
  it a fixture failure outright.
- Fix pass 2 (over the fix re-review verdicts, 21:44-21:52 +07):
  Council 1 GO, Council 2 AMEND (docstring-only), Council 3 AMEND
  (R1-R4 plan-only), redteam AMEND (no BLOCK-grade finding, F1-F8).
  Fixes: joined -m ("python3 -mrun_batch3") + dotted -m (exact
  runner names only) + spaced -W/-X value forms; codex anchored to
  executable positions only (argv[0], after -c, after env; grep/cat/
  echo false-positives fixed; sudo-prefixed codex recorded as a gap);
  served-fixture check extended to all 12 browser-served files;
  docstring corrected ("identical logic" claim false, siblings
  unfixed; double-nested -c removed from residuals per F8, it is
  caught live via the leaf; new residuals: comma-list imports,
  dynamic imports, import-only over-approximation; extensionless/
  .pyc qualified as run_*/hand_drive_e1 only); plan R1-R4 (find path
  clone1-batch3, t09 detail/prefs md5s, run_batch3.py md5 line,
  round-trip count 3.5 effective with margin restated as a range);
  F7 mid-test window recorded. Declined with reasons: redirect/UA
  refusal for the served check (md5 is the check; adversarial server
  behavior outside the threat model); -c import-list tracking
  (recorded as residual instead). Verification in the log. A redteam
  re-review over the fix-pass-2 diff is spawned after this commit;
  ship waits for it unless it BLOCKs, in which case one more fix
  pass follows.

## Runner status (21/11, after Y14b re-stage)

- `tests/realistic/run_batch3.py` re-staged (see above): all 10 tests
  (b3-t01..b3-t10), the /actions helpers with exact Council 1 payloads,
  the fallback routing (raw element/value keys, d.click('#progress')
  for the seek, two d.click() for dblclick, JS el.click() for
  click_nth), ensure_visible reuse, the launch gate (LIVE_SLOT_OK=1,
  Zen alive, Marionette 2828, ports 8771/4452 free, no geckodriver or
  other runner live via the /proc tokenizer scan), the circuit breaker,
  one INFRA-only retry, and LiveMetrics constructed as run_live.main()
  does. Compiles (py_compile OK), imports cleanly on the VM, all 10
  tests registered.
- `tests/realistic/run_batch3_probe.html` written (probe page for
  preflight step 0: text input, range input, scrolled pad, re-rendering
  list, filter list).
- Not yet shipped to the laptop, not yet run. Ship + syntax check on
  the laptop happen before the slot (ship includes live_metrics.py
  alongside the runner, per the redteam-2 shipping note, and the
  import is verified on the laptop before any slot run; a failed
  import degrades metrics to off silently). The t10 sampler stays in
  the Promise form pending the Redteam verdict on whether Marionette
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
- Redteam (BLOCK, 19:47 21/11): D1 ArrowRight/ArrowDown PUA codes swapped
  in the first draft (fixed: Right U+E014, Down U+E015 in plan + code,
  preflight (i) now asserts the ArrowRight/ArrowDown e.key strings);
  D2 t09 absolute handle counts 3/1 (fixed: relative to handles_before
  captured at t09 start, +2 at two-popups, baseline at end); D3 t10
  sampler Promise unproven + no fail-closed rule (fixed: preflight
  (vii) Promise proof returning 42 + bare-IIFE control, sampler raises
  on None/non-numeric, never defaults to 0); D4 hidden-body ladder
  wrong for popup tabs (fixed in plan text: main tabs only reload the
  fixture on swap; popups use allow_swap=False, persistent hidden is
  INFRA; the code already passed allow_swap=False for popups); D5
  window.open popup transfer unproven (fixed: preflight (viii) opens a
  real window.open popup from a click, switches, asserts visible,
  closes, asserts the handle count returns to baseline; new probe page
  run_batch3_probe_popup.html). The redteam reviewed the plan before
  run_batch3.py existed, so its "no code exists" claims were stale at
  arrival; Y12 HAS reported (897ca17, see the section above). During
  the fix, a sixth bug was found by inspection: run_preflight opened
  "/probe.html", a file that does not exist (fixed to
  "/run_batch3_probe.html", probe tab handle captured for the
  switch-back; the earlier fix attempt died on its first assert because
  it assumed the wrong URL, and the failure was caught by the
  verification inspect, not by the run). A second redteam pass on
  run_batch3.py itself is required before the slot opens.
- Redteam 2 (AMEND, 19:52 21/11, verdict file
  improvements/worker-y14-redteam2-verdict.md, commit 6f93469): reviewed
  run_batch3.py itself end to end against the plan and all 10 check.mjs
  files. Verified D1-D5 real in the code, all 10 translations faithful,
  probe pages complete, helpers byte-identical to run_fcck.py. No
  false-pass path found. Holes, all fixed in the runner before the slot:
  H1 open_test returned a stale tab handle on the swap path (now returns
  r.tab if swapped, reload_visible audited, returns no handle); H2 hung
  /actions and session death never classified INFRA (now _actions_post
  raises RuntimeError INFRA on TimeoutError/URLError, run_one prefixes
  TimeoutError, URLError, invalid session id, no such window,
  FIXTURE-UNAVAILABLE with INFRA so the retry and breaker count apply);
  H3 open_test skipped the final fresh tab (now mirrors open_fixture's
  final-tab block with rebootstrap_tab + goto + clear + refresh +
  ensure_visible allow_swap=False); H4 no ensure_visible after
  switch-backs (now added in click_and_close, both two-popup switches,
  and preflight viii, all allow_swap=False, raising INFRA or PREFLIGHT
  FAIL); H5 launch gate omitted predecessor-port checks and never
  verified LIVE_SERVER_ROOT (now binds 8767-8770/4448-4451 and checks
  the root exists and holds clone1-batch3/t01-terminal/fixture.html).
  M1 preflight (vi) now clicks #probe-input before the raw Enter send.
  M2 t10 min-3-5 gap rule is analysis-only, not code: if t10 fails with
  min 3-5, check the step-log gap before calling it a fixture failure.
  Shipping note from the verdict: ship live_metrics.py alongside the
  runner (run_live.py + run_agyq2.py + scripts/live_metrics.py) and
  verify the import on the laptop before the slot; if the import fails,
  metrics silently degrade to off. The AMEND verdict is conditional on
  the staged suite still being ed78e83 at slot time; if Y15's D1 fix
  has landed, re-stage from the new HEAD and update the t10 translation.
