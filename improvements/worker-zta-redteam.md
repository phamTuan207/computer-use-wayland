# Redteam verdict: Zen ordinary-user tests (ZT-A scenarios)

Reviewer: Worker ZTA-Redteam (independent, blind to author intent beyond the file).
File reviewed: `improvements/zen-ordinary-user-tests-20261121.md` (branch todolist-push).
Date: 2026-11-21, 22:30 Asia/Ho_Chi_Minh.
Rule: file not modified. Never ydotool.

## Verdict: BLOCK

Do not run on the owner's live Zen as written. One step can close the
owner's protected tabs (R-01), the health gate contradicts itself so it can
block the whole run spuriously (R-02), and the cleanup check used by every
scenario cannot detect that damage (R-03). Fix the blockers, then run. No
re-review needed if every blocker fix is applied verbatim; major items
should be fixed in the same edit.

## Blockers (must fix before any live run)

### R-01 ZT-09 step 9: blind triple Ctrl+W can close a protected owner tab
- Scenario/step: ZT-09 step 9. `Ctrl+W three times, 1 s pause between presses`.
- Failure mode: Ctrl+W closes whatever tab is active, not a named tab. The
  assumed active-tab order (httpbin, then Wikipedia, then example.com)
  depends on R-07 (activation order after close is unproven) and R-08
  (reopen order). If any earlier step closed or activated a different tab,
  the second or third Ctrl+W closes a tab ZT-B did not open, possibly
  Gmail, Calendar, Muse chat, or PCCV Sheets. Tab-count check afterwards
  cannot catch this (see R-03): closing one owner tab and leaving one test
  tab open keeps the count correct.
- Fix: verify the active tab title by DOM immediately before EACH Ctrl+W;
  press Ctrl+W only if the title is one of the three tabs this scenario
  opened; STOP and report instead of pressing if it is anything else.
  Apply the same per-press title check to every Ctrl+W in ZT-03 step 8
  and ZT-10 step 7, which have the same shape on a smaller scale.

### R-02 ZT-00 step 2: the gate contradicts itself
- Scenario/step: ZT-00 step 2. Says curl to 127.0.0.1:9222 `must return 200`,
  then says 404 `is normal` and `is NOT a failure`.
- Failure mode: a blind executor cannot decide pass or fail. If it treats
  404 as failure, the gate fails and the whole run is BLOCKED for a normal
  Firefox response. If it treats 200-or-404 as pass, the step tests
  nothing. Either way the gate that guards the entire run is undecidable.
- Fix: rewrite step 2 as: curl must return 200 or 404 (proves something
  listens on 9222); connection refused or timeout is the failure. Make
  step 3 (Marionette session creates, tab list returns) the deciding check.

### R-03 Cleanup check is vacuous in every scenario: tab count cannot detect damage
- Scenario/step: ZT-00 step 7, ZT-01 step 8, ZT-02 step 7, ZT-03 step 8,
  ZT-04 step 8, ZT-05 step 6, ZT-06 step 8, ZT-07 step 8, ZT-08 step 9,
  ZT-09 step 9, ZT-10 step 7. All use `tab count must return to the
  pre-scenario count`.
- Failure mode: count is preserved when one owner tab is closed and one
  test tab is left open, or when a test tab is closed and a different tab
  was opened by mistake. A PASS on count can hide exactly the damage the
  protected-tabs rule exists to prevent.
- Fix: ZT-00 must snapshot the full ordered tab-title list at run start
  (not just a count). Every scenario's cleanup check becomes: title set
  equals the pre-scenario title set AND count matches. Record the
  pre-scenario title list in a per-scenario step 0. Also fix the gap that
  ZT-00 never records a baseline count at all, so its own step 7 has
  nothing to compare against.

### R-04 ZT-03 step 3: three different paths, one undefined expected tab
- Scenario/step: ZT-03 step 3. `Middle-click, or right-click and choose
  "Open Link in New Tab", on the "Wikipedia" wordmark link if present; if
  no such link exists, Ctrl+T and type example.com`.
- Failure mode: the executor may take any of three paths and open two
  different pages (Wikipedia main page again, or example.com). Step 4
  then checks `the active tab title must match the new tab`, but `the new
  tab` is undefined. Worst case the fallback is taken, the scenario PASSES
  while middle-click was never tested at all. Extra trap: the Wikipedia
  wordmark links to the main page itself, so a middle-clicked duplicate
  has the same title as the current tab and step 4 cannot tell the tabs
  apart by title.
- Fix: pick ONE path and delete the others. Recommended: middle-click the
  first article link in the Wikipedia main page body (give its DOM
  selector), expected new-tab title is that link's target title, not
  `Wikipedia`. If middle-click is itself the thing under test, the
  Ctrl+T fallback must be removed, not kept as an escape hatch. If no
  suitable link exists, the step FAILS and is reported, it does not
  silently switch to another test.

### R-05 ZT-05 steps 1-3: workspace numbers are assumed, not measured
- Scenario/step: ZT-05 preamble and steps 2-3. `Zen is on its starting
  workspace (usually 1)`, `Super+2`, `Super+1 to switch back`.
- Failure mode: if Zen is on workspace 2 or 3 when the run starts,
  Super+1 moves AWAY from Zen, and the `switch back` lands on the wrong
  workspace. The DOM title check still passes (Marionette sees the tab
  regardless of workspace), so the scenario can PASS while Zen is left
  stranded on another workspace.
- Fix: step 1 must record the actual starting workspace number N from
  `hyprctl activeworkspace` and Zen's workspace from `hyprctl clients`.
  Switch to a different workspace M (N+1, or 2 if N is not 2), then switch
  back to N by number. After the return, check `hyprctl clients` shows
  Zen on workspace N, not only that the active workspace is N.

### R-06 ZT-06 steps 3-5: a pre-existing dummy.pdf makes the download check vacuous, and step 7 can delete the owner's file
- Scenario/step: ZT-06 steps 3, 5, 7. Step 3 only `records` the Downloads
  listing; step 5 checks `~/Downloads/dummy.pdf` exists and is non-empty;
  step 7 does `rm ~/Downloads/dummy.pdf`.
- Failure mode: if dummy.pdf is already in Downloads from a previous run
  or from the owner, step 5 PASSES without any download happening in this
  run, and step 7 then deletes a file the owner may have put there.
  The scenario can PASS while testing nothing and end by deleting an
  owner's file.
- Fix: step 3 becomes an assertion, not a recording: dummy.pdf must NOT
  exist before step 4 (if it does, move it aside to /tmp with a timestamp
  name and note it, do not delete it). Step 7 deletes only a file whose
  mtime is within this run, and verifies with `ls` that it is gone.

## Major (fix in the same edit; each can cause a false FAIL or a vacuous PASS)

### R-07 ZT-09 steps 5-6: assumed tab-activation order after close is unproven
- Scenario/step: ZT-09 steps 5-6. After closing the httpbin tab, `the
  active tab must be the Wikipedia tab`; after closing Wikipedia, `the
  active tab must be the example.com tab`.
- Failure mode: Firefox/Zen activates the most-recently-used tab after a
  close, not necessarily the left neighbour. Correct browser behaviour
  can FAIL this step, and the failure then corrupts steps 7-9.
- Fix: state the activation rule being tested (left neighbour or MRU)
  explicitly, or relax steps 5-6 to check only that the count dropped by
  1 and the active tab is one of the scenario's own tabs, then navigate
  explicitly before steps 7-9.

### R-08 ZT-03 steps 6-7 and ZT-09 steps 7-8: Ctrl+Tab order is ambiguous
- Scenario/step: ZT-03 steps 6-7 (`Ctrl+Tab switches to the next tab`),
  ZT-09 steps 7-8 (reopen order, same dependency).
- Failure mode: Firefox Ctrl+Tab default is most-recently-used order, not
  sidebar order, and the setting can differ per profile. `Next tab` has
  two readings, so a correct switch can be scored wrong.
- Fix: define `next` as MRU order and write the expected title for each
  press from the known tab history, or replace Ctrl+Tab with explicit
  sidebar/DOM tab activation and test Ctrl+Tab only as `active tab
  changes`, not as a specific destination.

### R-09 ZT-04 steps 5 and 7: the bookmark library is chrome UI, not page DOM
- Scenario/step: ZT-04 steps 5 and 7, tagged `[DOM]`: `The library must
  list a bookmark titled "Example Domain"`, `The bookmark must no longer
  be listed`.
- Failure mode: Marionette page DOM cannot see the Library window. The
  executor has no DOM check to run, so it must eyeball a screenshot or
  invent a check. The `[DOM]` tag is false, and the step is ungroundable
  as written.
- Fix: retag both steps `[OBSERVE]` with an exact screenshot check (what
  the row looks like, which column holds the title and URL), or verify via
  the bookmark star plus `places.sqlite` read as the CLI check, and say
  which. Also fix step 5's other ambiguity: `Ctrl+Shift+O, or open it
  from the menu` gives two paths with no menu path spelled out; pick one.
  Also add a pre-check that example.com is not already bookmarked,
  otherwise Ctrl+D opens an edit dialog for an existing bookmark and the
  star state in step 4 is meaningless.

### R-10 ZT-04 step 7: delete step can delete the wrong bookmark
- Scenario/step: ZT-04 step 7. Right-click the bookmark and choose
  Delete, or select it and press Delete.
- Failure mode: if the list is sorted differently or the wrong row is
  focused, Delete removes one of the owner's bookmarks. No step verifies
  which row is selected before deleting, and the exact menu label
  (`Delete` vs `Delete Bookmark`) is not given.
- Fix: before deleting, screenshot the Library with the `Example Domain`
  row visibly selected and record its URL; delete only that row; after
  deleting, list the Library again and confirm no other bookmark vanished
  (compare row count before and after: exactly one fewer).

### R-11 ZT-10 step 6: the collapse toggle is not identified
- Scenario/step: ZT-10 step 6. `Click the sidebar collapse toggle (the
  icon at the top of the sidebar)`.
- Failure mode: the top of the Zen sidebar holds several icons
  (workspace switcher, new tab, settings, tab search). `The icon at the
  top` does not identify one of them. A mis-click can switch workspace,
  open settings, or open a new tab, and the second click does not undo
  that. The scenario also assumes a binary toggle; Zen sidebar modes may
  cycle through more than two states, so two clicks may not restore the
  original state.
- Fix: identify the toggle by its tooltip text or its exact position
  measured from a fresh observe at run time (state the tooltip string to
  look for, e.g. `Collapse sidebar` or whatever the live build shows;
  if the tooltip differs, STOP and report the actual label instead of
  guessing). Observe and record the sidebar state after the FIRST click
  before doing the second, and add a final check that the sidebar is back
  in its starting state.

### R-12 ZT-10 steps 3-5: no branch for the F-001 state the scenario exists to detect
- Scenario/step: ZT-10 step 3. `If it shows only icons and no tab titles,
  record that as F-001 still reproducing and take a screenshot before
  continuing`.
- Failure mode: `before continuing` has no continuation defined. Steps 4-5
  require clicking tab rows that do not exist in that state, so the
  executor must improvise (expand the sidebar how?) or fail steps 4-5
  spuriously for the same root cause already recorded in step 3.
- Fix: add the branch explicitly: if only icons show, record F-001, then
  expand the sidebar by the step 6 toggle, verify rows appear, and only
  then run steps 4-5; if rows never appear, FAIL ZT-10 at step 3 and skip
  steps 4-6 instead of running them blind.

### R-13 ZT-06 step 4: the PDF download button has no location and the fallback changes the test
- Scenario/step: ZT-06 step 4. `Click the download button in the PDF
  viewer toolbar (or press Ctrl+S and choose Save)`.
- Failure mode: the pdf.js download button position is not given, it may
  sit in an overflow menu, and the toolbar is chrome UI with no DOM
  selector supplied, so the click is vision-only. The Ctrl+S fallback
  opens a Save File dialog whose clicks are not specified at all, and it
  tests a different path (save dialog, not the viewer button). A PASS via
  Ctrl+S proves nothing about the viewer button.
- Fix: give the button's exact position (top-right toolbar, download
  icon) plus a screenshot reference of what it looks like, and delete the
  Ctrl+S fallback; if the button is not found, that is a FAIL with a
  screenshot, not a cue to switch methods.

### R-14 ZT-08 steps 4-6 and ZT-09 step 5: chrome-UI clicks have no coordinates and violate the DOM-rect rule
- Scenario/step: ZT-08 steps 4-6 (Back/Forward toolbar buttons), ZT-09
  step 5 (X on the httpbin tab in the sidebar), ZT-03 step 5 (sidebar tab
  row), ZT-02 step 5 (highlighted find match, see R-17).
- Failure mode: the Tools section says click coordinates must come from
  DOM rects, never vision estimates. Toolbar buttons, sidebar rows, and
  tab X buttons are chrome UI with no page-DOM rect. The executor must
  either break the stated rule (vision coordinates, the known error
  source) or cannot run the step. The tab X is worst: it appears only on
  hover, is a few pixels wide, and a mis-click switches tabs or closes
  the neighbouring tab.
- Fix: add an explicit chrome-UI exception to the Tools section: for
  toolbar/sidebar clicks, coordinates come from a fresh observe plus a
  named anchor (e.g. `Back arrow, top-left, left of the address bar`),
  with a screenshot before the click; for the tab X, prefer closing by
  keyboard (activate the tab by DOM, then Ctrl+W) and keep the sidebar-X
  click only as the explicit thing under test in one scenario.

### R-15 ZT-05 step 4: an unanchored body click can navigate away
- Scenario/step: ZT-05 step 4. `Click once in the page body` on
  example.com, with no coordinates.
- Failure mode: the Example Domain page contains a link (`More
  information...` to iana.org). A click placed on or near it navigates
  away, so step 5 then fails for a reason that has nothing to do with
  workspace switching. `In the page body` is not a coordinate.
- Fix: give exact coordinates from the DOM rect of a non-link element
  (e.g. the centre of the `h1`), or replace the click with a keyboard
  focus check (press Tab, observe focus) that cannot navigate.

### R-16 ZT-07 steps 5 and 8: native select dropdown and POST-back are unspecified
- Scenario/step: ZT-07 step 5 (`Click the size select and choose
  medium`), step 8 (Alt+Left back to the form after a POST submit).
- Failure mode: a native `<select>` dropdown is an OS popup, not a DOM
  element; no coordinates or keys are given for picking `medium`, so the
  executor improvises (mouse on popup vs arrow keys vs typing `m`). Step
  8 expects the form to be present after back from a POST result, but
  Firefox can show a resubmission warning or an expired document instead,
  which is correct browser behaviour scored as FAIL.
- Fix: step 5, choose by keyboard: focus the select, press `m` or Down
  arrow until `medium`, then verify the DOM value; delete the mouse
  option. Step 8, accept either the form present OR the resubmission
  prompt (screenshot it and report which), and do not score the prompt
  as a failure.

### R-17 ZT-02 step 5: the find-match check cannot be done from the DOM and the click is ungroundable
- Scenario/step: ZT-02 step 5. `The page must report at least one match
  (find bar shows a match count, or the first match is highlighted...)`,
  `[MOUSE] Click on the first highlighted match`.
- Failure mode: the find bar is chrome UI, its match count is not in the
  page DOM, so no DOM check exists for it. The highlighted match is a
  browser rendering, not a DOM element, so there is no DOM rect to click;
  the click must be vision-guessed. The `or` makes the check pass on
  either half, so it can pass without the match ever being visible.
- Fix: make the check single and observable: screenshot must show the
  find bar reading `1 of N` (or equivalent) with the match count visible,
  and drop the click-on-the-highlight step, or replace it with pressing
  Enter again to jump to the next match and screenshotting the new
  scroll position.

## Flaky expectations and timing races

### R-18 `Within 3 s` (ZT-10 steps 4-5) and `within 5 s` (ZT-01 step 7, ZT-08 steps 4-6) have no poll rule
- Failure mode: a single check at the deadline fails on a slow first
  switch; a check at 0 s fails before the switch lands. Under load
  (Marionette + observe + Zen) a tab switch that takes 3.5 s is scored
  FAIL though the browser worked. Same for ZT-09 steps 7-8 `within 5 s`.
- Fix: define polling everywhere: check every 500 ms until the deadline,
  pass if the condition holds at any poll, fail only if it never holds by
  the deadline. Raise ZT-10 to 5 s to match the other navigation checks.

### R-19 Wikipedia and httpbin are live external dependencies with no offline fallback
- Scenario/step: ZT-01, ZT-02 (Wikipedia), ZT-07, ZT-08 step 3, ZT-09
  steps 3, 8 (httpbin.org), ZT-06 step 1 (w3.org).
- Failure mode: httpbin.org is a demo service with no uptime promise; it
  502s and rate-limits. Wikipedia article content, the lead's first link
  (ZT-01 step 6), and the search box layout change over time and by skin.
  When the site is down, the curl control fails too, so the run records a
  FAIL against Zen that proves nothing about Zen, and four separate
  scenarios fail for one external outage.
- Fix: keep the live sites, but add a decision rule: if the curl control
  fails, the scenario is INCONCLUSIVE (site/network fault), not FAIL, and
  the run continues to the next scenario. Pin ZT-01 step 6 to a stable
  target: name the exact link (e.g. the link whose href is a fixed
  article) instead of `the first link in the lead`, and re-check the
  selector the morning of the run.

### R-20 ZT-08 step 7: reload check is vacuous
- Scenario/step: ZT-08 step 7. After Ctrl+R, `the title must still contain
  "Wikipedia"`.
- Failure mode: if reload does nothing and the old page simply stays,
  the title check still passes. The step cannot distinguish a successful
  reload from a no-op.
- Fix: check something that changes on reload, e.g. `performance.now()`
  or a DOM timestamp re-read, or navigate to a URL with a cache-busting
  query and check the URL, or drop step 7's title check and require a
  screenshot showing the page re-rendered (loading indicator seen).

### R-21 ZT-01 step 1: Ctrl+L then a mouse click fight each other
- Scenario/step: ZT-01 step 1. `Press Ctrl+L to focus the address bar.
  [MOUSE] Click the address bar`, expected `text is selected`.
- Failure mode: Ctrl+L already selects the address text; a click in the
  bar moves the caret and can clear the selection, so the expected
  highlight may vanish because of the scenario's own second action.
- Fix: delete the mouse click from step 1. Ctrl+L alone is the test;
  observe the selection after Ctrl+L only.

## Damage and staleness risks

### R-22 Protected-tabs list is a stale snapshot, and `never close a tab you did not open` is unenforceable from it
- Scenario/step: Rules section 3. Lists 14 tabs; the 22:10 cleanup note
  in the same repo records 28 tabs (13 real + 14 about:blank + 1 fixture).
  The list also omits the about:blank tabs, which an executor could close
  thinking they are its own blank tabs.
- Failure mode: the owner may open or close tabs between the file being
  written and the run. A tab opened after the list was written is not
  protected by the list, and a tab on the list may no longer exist, so
  the executor cannot tell a new owner tab from its own.
- Fix: ZT-00 step 0 must snapshot the live tab list (titles + URLs) at
  run start and treat THAT as the protected set. The 14-name list becomes
  a sanity check on the snapshot, not the protection mechanism.

### R-23 No per-step host is stated: laptop vs VM
- Scenario/step: Tools section and every `[CLI]` step. `ps`, `hyprctl`,
  `ls ~/Downloads`, `curl` must run on the laptop, but the file never
  says so per step. `scripts/zen_dom.py` path is given with no working
  directory (repo root on the laptop? on the VM?).
- Failure mode: an executor running `hyprctl` or `ls ~/Downloads` on the
  VM gets a spurious failure or reads the wrong Downloads folder, and a
  `curl` control run on the VM proves nothing about the laptop's network.
- Fix: tag every CLI step with its host (`[CLI laptop]` vs `[CLI VM]`)
  and give the absolute repo path for `zen_dom.py` and `cu.py`.

### R-24 Run budget and stop rule invite a half-run with no verdict
- Scenario/step: Run order and reporting. `Total expected about 30
  minutes, maximum 60; if the run passes 60 minutes, stop`.
- Failure mode: 11 scenarios with an observe screenshot plus DOM plus CLI
  per step will not fit 30 minutes once network waits and screenshots
  are counted, so the run is likely to stop mid-list with several
  scenarios unrun and no PASS/FAIL for them. There is also no retry rule:
  a single transient network blip fails a scenario with no second attempt.
- Fix: budget 60 minutes expected, 90 maximum; allow exactly one retry
  per scenario on a network-control failure only (curl control failed),
  never on a Zen-behaviour failure.

## Minor (fix opportunistically, do not block on these alone)

### R-25 ZT-00 step 1: process-flag grep is brittle
- `ps ... | grep zen-bin` with flags `--remote-debugging-port=9222
  --marionette` assumes flag order and spelling. If F3 restarts Zen with
  the flags in a different order or via a wrapper, the grep misses a live
  Zen and the gate fails spuriously. Fix: check the process exists and
  the Marionette port answers (step 3), and treat the flag string as a
  diagnostic, not a gate.

### R-26 ZT-00 step 6, ZT-01 step 3 and others: `hyprctl activewindow must show Zen` is flaky as a pass condition
- A notification, a dialog, or the observe overlay can steal focus for a
  moment. Fix: make it a diagnostic (record the output) unless focus is
  the behaviour under test; only ZT-05 needs a focus assertion.

### R-27 ZT-02 step 6: no verification after Escape
- Escape is pressed to close the find bar but nothing checks the bar is
  gone. Fix: add an observe check that the find input is no longer
  visible.

### R-28 ZT-04 steps 2-3: dialog button label is two options
- `Click Save or Done` and `Press Escape if the dialog stays open`:
  Escape after saving is harmless in Firefox but the file does not say
  whether the bookmark survives it. Fix: name the exact button label
  seen on the live build at run start (record it in ZT-00), and delete
  the Escape fallback.

### R-29 ZT-07 step 3-4: typing has no retry rule, and Zen typing is a known flaky area
- The owner's Zen has a known intermittent typing failure (Vietnamese
  input / Super-I switch). A single mistyped field fails the scenario
  with no retry. Fix: after each type, read the DOM value (the scenario
  already does this for custname/custtel); if it mismatches, clear the
  field and retype once, then fail if it still mismatches.

### R-30 Composite-rule claim is not checked
- Rule 2 says every scenario uses DOM + CLI + mouse + keyboard, but no
  step verifies it and ZT-02's mouse step is ungroundable (R-17). Fix:
  keep the rule as an authoring note, not a run-time assertion, or add a
  per-scenario channel checklist to the report template.

## What is sound (do not change)

- ZT-00 as a gate concept, and stopping the whole run on gate failure.
- example.com as the stable anchor page; its title and content do not change.
- The protected-tabs intent and the cleanup intent, only the mechanism
  (count-only, stale list) is broken, see R-03 and R-22.
- Re-testing F-001 in ZT-03/ZT-10 and F-002 in ZT-05, with a screenshot
  after every switch in ZT-05.
- Evidence rule 5 (screenshot + wall-clock + elapsed per error).
- `Never use ydotool` and `one runner at a time`, both correctly restated.

## Fix list for ZT-A (short version)

Blockers: R-01 (per-press title check before every Ctrl+W), R-02 (200-or-404
gate), R-03 (title-set cleanup + ZT-00 baseline snapshot), R-04 (one path
in ZT-03 step 3, no fallback), R-05 (measured workspace numbers), R-06
(assert dummy.pdf absent before download, mtime-checked delete).
Major: R-07 to R-17. Flaky/timing: R-18 to R-21. Damage/staleness: R-22
to R-24. Minor: R-25 to R-30.

After the blocker fixes, the file is runnable; the major fixes should land
in the same edit because R-07, R-09, R-11, and R-14 each decide whether a
scenario's result means anything.
