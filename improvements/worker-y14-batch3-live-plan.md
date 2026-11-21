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
  Y10 advance assert (position must advance past 0 after the sample window).
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

New helpers, all on WD via the existing `_wd`/`_s` plumbing:
- `press_keys(d, keys)`: WebDriver Actions API, POST /session/:id/actions,
  one key action source, keyDown+keyUp per key, batched max 10 pairs per
  call, then DELETE /session/:id/actions to release. Key values are the
  WebDriver PUA codes: Enter U+E007, Home U+E011, ArrowLeft U+E012,
  ArrowUp U+E013, ArrowDown U+E014, ArrowRight U+E015. Used for: t01 Enter
  after each command and ArrowUp recall; t08 Home + ArrowRight x70 on
  #volume; t10 Home + ArrowRight x30 on #volume.
- `pointer_click_at(d, x, y)`: Actions API pointer source, move to
  viewport coords + button down/up. Used for: t10 seek click at 50% of
  #progress rect (fixture computes frac from clientX vs rect, so a real
  pointer click at x + w*0.5 is the exact Playwright mouse.click
  equivalent).
- `dblclick_el(d, js_expr)`: rect of the element from eval, then one
  Actions call with two down/up pairs at the rect center. Used for:
  t05 dblclick on folder items (fixture has separate click and dblclick
  handlers; two separate Marionette clicks could straddle the OS
  double-click interval, one Actions call cannot).
- `click_nth(d, js_expr)`: rect of the element located by JS index, then
  pointer_click_at at its center. Used for: t04 `#list .msg` nth(0/1/2)
  and the nested `.star`; t06 `.day[data-day="12"] .chip` nth(0/1).
  All other clicks use the proven `d.click(css)` Marionette element click.
- `poll_effect(d, js_cond, timeout=5.0)`: mirror of clone1 t09 verify
  polling. Polls a JS condition every 50 ms up to 5 s after a popup
  closes; returns True when seen. Used for every t09 save/apply that
  carries a verify in check.mjs. A missing effect after the deadline is
  a test failure, never silently swallowed.

## Per-test translation (Playwright op to Marionette op)

- t01 terminal: click #cmd, type_text, press_keys Enter per command.
  ArrowUp recall: click #cmd, press_keys ArrowUp, read value #cmd.
  Fixture keydown handler checks e.key Enter/ArrowUp/ArrowDown.
- t02 spreadsheet: type_text per cell (#cell-A1 etc. are plain inputs;
  fixture recomputes on the input event, which Marionette sendKeys
  fires per keystroke). Read back via value. Status text via text().
- t03 video call: clicks + type_text (#chat-input). Plain CSS clicks.
- t04 email: type_text search, click_nth for .msg rows and .star,
  type_text compose fields, clicks. Counts via eval querySelectorAll.
- t05 file manager: select_option #sort; type_text #search; clicks;
  dblclick_el for Archive / Old Files 2026 list items; rename dialog
  via type_text #rename-input + clicks on #rename-save / #rename-cancel;
  dialog-open asserts via visible() + value() prefill; empty rename:
  type_text empty, click Save, assert error visible + dialog open, then
  Cancel; move via select_option #move-target + #move-ok; tree clicks
  via d.click on #tree-home / #tree-archive / #tree-old-files-2026.
- t06 calendar: clicks on .day[data-day="N"] .day-num; type_text
  #event-title / #event-time / #edit-time; click_nth for chips;
  select-free month nav via #next-btn / #prev-btn / #today-btn.
- t07 code editor: type_text #editor (textarea; fixture marks dirty on
  input), clicks, d.refresh() for reload steps (refresh diagnoses and
  raises on hidden body, same as goto). Tab switches via clicks on
  #tabs button[data-file="..."]. Find/replace via type_text + clicks.
- t08 settings: select_option #theme; d.click on radio
  input[name="accent"][value="blue"] and on the three toggles (native
  inputs, change event fires on real click); type_text #display-name;
  click #volume then press_keys Home + ArrowRight x70; d.refresh() for
  reload steps; isChecked via eval el.checked; search via type_text.
- t09 multi-window: openPopup = click detail/prefs button, wait for a
  new handle, switch, settle, require_visible. Interact in the popup
  (type_text #title-input, select_option #theme-select), then
  clickAndClose = click the popup close button, wait for the close
  (handle disappears), switch back to main, poll_effect up to 5 s for
  the expected main-window effect. Cancel: click #cancel-btn, dwell
  500 ms, read title immediately, no verify. Two-popups step: open
  detail popup, switch back to main WITHOUT closing it, open prefs
  popup, assert handles count is 3, close prefs, verify dark, switch
  to the still-open detail popup, rename, close, verify.
- t10 music player: clicks; sleeps as in check.mjs (700 ms after play,
  400 ms paused, 500 ms after resume, 350 ms after sampler); sampler:
  eval with top-level `return new Promise(...)` sampling
  #position data-seconds every 10 ms for 500 ms, taking the minimum
  (Y4d lesson: top-level return is required, Marionette runs the script
  as a function body; /execute/sync awaits a returned promise).
  Advance assert after the sampler. Volume: click #volume, Home,
  ArrowRight x30. Seek: pointer_click_at at 50% of #progress rect.
  Shuffle/repeat/search/track clicks as in check.mjs.

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

The /actions helper has never run against live Zen. Before t01, open a
scratch tab with a probe page served from the same loopback server
(an input + a div that records keydown keys, click clientX/Y, and
dblclick count). Prove live: type into the input, press_keys Enter and
ArrowUp, read the recorded keys; pointer_click_at a known point, read
the recorded coords; dblclick_el, read the dblclick count. Close the
scratch tab. If /actions fails, fall back to element/value with PUA key
codes for keys (test that path in the same preflight), use Marionette
element click where a selector exists, and record the fallback as a
deviation in the log. Do not start t01 until the input path is proven
one way or the other.

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
- Council 1, Council 2, Redteam: verdicts pending at the time of this
  edit; fold them in when they arrive.
