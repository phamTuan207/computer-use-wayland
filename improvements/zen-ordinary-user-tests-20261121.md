# Zen ordinary-user tests (2026-11-21)

Author: Worker ZT-A (Muse test author). Executor: Worker ZT-B (separate agent, blind).
Status: scenarios only, NOT run. Run only after Worker F3 reports Zen restored.
Branch: todolist-push. Goal: computer-use-g-n-nh-kh-ng-l-i-nhanh-g-p-v-i-l-n.

Revision: v2 (22:34 21/11). Applies council 1 R1-R14, council 2 R1-R15,
council 3 A1-A11 + S1-S8, redteam R-01-R-30. Verdicts:
improvements/worker-zta-council-1.md, worker-zta-council-2.md,
worker-zta-council-3.md, worker-zta-redteam.md. Redteam verdict was BLOCK
on a live-data risk (blind Ctrl+W could close an owner tab); v2 fixes all
six blockers plus the majors in the same edit.

## Purpose

Simulate an ORDINARY user doing everyday things in Zen browser, find every
error, and feed the errors into fixing. These are live tests on the owner's
real Zen, not fixtures. No scenario uses a fixture page. Every site is public,
stable, and needs no login.

## Rules for the executor (ZT-B)

1. BLIND. The executor has not seen these scenarios before the run starts.
   The scenarios are self contained: exact URLs, exact expected strings,
   exact commands. Nothing in them depends on knowledge outside this file.
2. COMPOSITE (authoring rule). Every scenario uses DOM + CLI + mouse +
   keyboard together, because a real task is never single-channel. The
   report template at the end has a per-scenario channel checklist; the
   executor fills it in, it is not a run-time assertion.
3. [CHECK] STEPS ARE INSTRUMENTATION, NOT USER STEPS. Steps tagged
   [CHECK] (curl controls, hyprctl diagnostics, ps, file checks, tab-list
   identity checks) are the harness verifying the world, not things a user
   does. A failed control (curl, hyprctl, ps) makes the scenario
   INCONCLUSIVE (site or network fault), not FAIL, and the run continues
   to the next scenario. The two exceptions are safety gates: the
   identity cleanup check and the pre-close check. A failure there is a
   FAIL and the executor stops.
4. PROTECTED TABS ARE THE SNAPSHOT, NOT THE LIST BELOW. ZT-00 step 0
   snapshots the live tab list (title and URL for every tab, in order) at
   run start, and THAT is the protected set. The named tabs below are
   examples and a sanity check only. The owner may have opened or closed
   tabs since this file was written. Never close a tab that is in the
   snapshot unless this run opened it.
5. CLEANUP IS IDENTITY, NOT COUNT. After each scenario, the tab title
   set must equal the pre-scenario title set AND the count must match.
   A count-only check can hide a closed owner tab, so it is never enough.
6. PRE-CLOSE CHECK BEFORE EVERY Ctrl+W. Before every Ctrl+W press, the
   DOM active title (or URL where the title is not distinctive) must
   equal the expected test-tab identity named in that step. If it does
   not match, STOP, do not press Ctrl+W, and report. This applies to
   every Ctrl+W in every scenario, including multi-press closes where
   the check runs before EACH press.
7. EVIDENCE. Every error needs: a screenshot (observe), wall-clock time
   (Asia/Ho_Chi_Minh), elapsed time for the step, what was expected, what
   was observed. No bare claim counts.
8. POLL RULE. Every "within N s" check is polled every 500 ms until the
   deadline. It passes if the condition holds at any poll, and fails only
   if it never holds by the deadline. No single check at the deadline.
9. HEALTH GATE FIRST. Run ZT-00 before any scenario. If the gate fails,
   the whole run is BLOCKED: report to Muse and stop, do not force through.
10. ONE RUNNER AT A TIME. Never run while another live runner drives Zen.
    Never use ydotool. Never touch the owner's other apps, music, or chats.
11. HOSTS. Every [DOM], [MOUSE], [KEYBOARD], and [CLI laptop] step runs ON
    THE LAPTOP via ~/workspace/ssh-laptop.sh from the VM. Paths on the
    laptop are home-relative (~/computer-use-wayland/scripts/...).
    The run log and report live on the VM.
12. RETRY. Exactly one retry per scenario, and only when a network
    control failed (curl control failed). Never retry a Zen-behaviour
    failure. A retried scenario is marked RETRIED in the report.
13. TIMING. Total expected about 45 minutes, maximum 90 minutes. If the
    run passes 90 minutes, stop, report what finished, and hand the rest
    to Muse.

Protected-tab examples (sanity check on the snapshot only): YouTube,
Todoist, Gmail inbox, Google Calendar, Muse chat, PCCV CF26 Sheets, Free
Claude Code Admin on 127.0.0.1:8082, Welcome, Polygon, codeforces,
chunkbase, duck.ai, BytePlus, reddit, plus about:blank tabs and the BiDi
fixture tab if they are in the snapshot.

## Tools

- OBSERVE: `computer-use observe --screen eDP-2 --max-width 1920`
  (screenshot, on the laptop). A fresh observe is at most 120 s old when
  an act uses it.
- MOUSE: `computer-use act` inside a session, with an actions file.
  Worked example. Actions file /tmp/zt-act.json:
  `[{"type": "click", "x": 135, "y": 272}]`
  Command (on the laptop):
  `computer-use session -- computer-use act --observation
  ~/.cache/agent-computer-use/<OBS_ID>.json --actions
  /tmp/zt-act.json`
  Coordinates for PAGE-CONTENT targets come from a DOM rect (see locate
  below), never from vision estimates. Coordinates for BROWSER-CHROME
  targets (address bar, sidebar rows, toolbar buttons, dialogs, library,
  download panel, find bar) come from a fresh observe plus a named anchor
  (for example "Back arrow, top-left, left of the address bar"), and the
  screenshot is saved as evidence. Chrome UI has no DOM rect, so the
  DOM-rect rule cannot apply to it.
- KEYBOARD: same act mechanism. Worked examples:
  type: `[{"type": "type", "text": "en.wikipedia.org"}]`
  key: `[{"type": "key", "keys": ["ctrl", "l"]}]`
- DOM: scripts/zen_dom.py on the laptop
  (~/computer-use-wayland/scripts/zen_dom.py, Marionette port
  2828, WebDriver port 4444, flock zen_dom.lock). Exact invocations:
  `python3 ~/computer-use-wayland/scripts/zen_dom.py list`
  (tab list, title and URL per tab)
  `python3 ~/computer-use-wayland/scripts/zen_dom.py eval
  "document.title"` (title of the active tab)
  `python3 ~/computer-use-wayland/scripts/zen_dom.py eval
  "location.href"` (URL of the active tab)
  `python3 ~/computer-use-wayland/scripts/zen_dom.py locate
  "a[href='/wiki/Vietnam']"` (exact rect of a page element, for a click)
  `python3 ~/computer-use-wayland/scripts/zen_dom.py eval
  "document.querySelector('[name=custname]').value"` (field value)
  `python3 ~/computer-use-wayland/scripts/zen_dom.py eval
  "Math.floor(performance.now())"` (page age in ms, for reload checks)
- CLI laptop: `hyprctl activeworkspace`, `hyprctl clients`,
  `hyprctl activewindow`, `ps -eo pid,etime,args | grep zen-bin`,
  `ls -la ~/Downloads/`, `file <path>`, `curl -s -o /dev/null -w
  "%{http_code}" <url>`, `curl -sI <url>`.
- NOTE: the find bar, the bookmark star and library, the sidebar rows,
  and the download panel are browser chrome, NOT page DOM. They are
  verified by [OBSERVE], never by [DOM]. Marionette cannot see them.

## Findings list

The executor appends new findings here as F-003, F-004, and so on, with:
scenario, step, expected, observed, screenshot path, wall-clock time, elapsed.
The first two entries are OWNER-REPORTED and must be re-checked after F3.

### F-001 (OWNER-REPORTED, 22:25 21/11)
Zen unclickable. The owner could not click or open any website. Screenshot
a14e82980194 (22:25) shows the sidebar collapsed to icons with no tab list
and a blurred new-tab page. Re-check in ZT-10 (sidebar tab clicks) and ZT-01
(address bar navigation). If it still reproduces after F3, it is the top
priority fix. If it does not reproduce, record the exact steps that now work.

### F-002 (OWNER-REPORTED, 22:25 21/11)
Switching workspaces has many strange errors. No exact symptom was captured
in words; the owner reported it right after the unclickable Zen report.
Re-check in ZT-05 (workspace switch and back). Record the exact symptom the
executor sees: blank screen, lost window, wrong workspace, tab closed, or
anything else, with a screenshot for each switch.

## ZT-00 Health gate (run first, 120 s expected, 180 s max)

Goal: prove Zen is alive and drivable before any scenario runs.
Preconditions: none.

0. [DOM] Run `zen_dom.py list` and save the FULL ordered tab list
   (title and URL for every tab) to the run log. This is the protected
   set and the baseline for every cleanup check. Record the baseline
   count too. If the list is empty, STOP and report.
1. [CLI laptop] `ps -eo pid,etime,args | grep zen-bin | grep -v grep`:
   a zen-bin process must exist. The exact flag string
   (--remote-debugging-port=9222 --marionette) is a diagnostic only,
   not a gate: if the flags differ after F3's restore, record the actual
   flags and continue.
2. [CHECK CLI laptop] `curl -s -o /dev/null -w "%{http_code}"
   http://127.0.0.1:9222/`: 200 or 404 passes (both prove something
   listens on 9222). Connection refused or timeout is the failure.
3. [DOM] Create a Marionette session with scripts/zen_dom.py and list
   tabs: the session must create without error and the tab list must
   return. This is the deciding check. The known failure
   "browserElement is null" at newSession is a gate failure, not a pass.
4. [MOUSE] Click the address bar (fresh observe coords, named anchor
   "address bar, top of the window"). [KEYBOARD] Type `example.com`
   and press Enter.
5. [DOM] `eval "document.title"` must be "Example Domain" within 10 s
   (poll every 500 ms).
6. [CHECK CLI laptop] `hyprctl activewindow` output is recorded as a
   diagnostic. It is not a pass condition; focus is not under test here.
7. [DOM] `eval "document.title"` must be "Example Domain" (pre-close
   check). [KEYBOARD] Press Ctrl+W. [CHECK] Run `zen_dom.py list`:
   the title set must equal the step 0 snapshot.

Pass: all steps 0 to 7. Fail: any step fails. On fail, if step 4 opened
a tab, close it first under the pre-close check, then STOP the whole run,
report BLOCKED to Muse with the step number and the evidence, do not run
ZT-01 to ZT-10.

## ZT-01 Open a site and read an article (180 s expected, 300 s max)

Goal: an ordinary user opens Wikipedia from the address bar, searches for a
topic, and reads the article.
Preconditions: ZT-00 passed. Step 0: record the pre-scenario title list.

1. [KEYBOARD] Press Ctrl+L to focus the address bar. [OBSERVE] The
   screenshot must show the address bar focused with the URL text
   selected (highlighted). Do not click the bar after Ctrl+L: the click
   can clear the selection.
2. [KEYBOARD] Type `en.wikipedia.org` and press Enter.
3. [DOM] Within 10 s (poll), `eval "document.title"` must contain
   "Wikipedia". [CHECK CLI laptop] `curl -s -o /dev/null -w
   "%{http_code}" https://en.wikipedia.org/` must return 200. If the
   curl control fails, this scenario is INCONCLUSIVE, not FAIL.
4. [MOUSE] Click the search box on the Wikipedia main page (page DOM:
   get its rect with `locate "input#searchInput"`). [KEYBOARD] Type
   `Ho Chi Minh City` and press Enter.
5. [DOM] Within 10 s (poll), the article title must be "Ho Chi Minh
   City" and `eval "location.href"` must contain `Ho_Chi_Minh_City`.
6. [MOUSE] Click the link with text "Vietnam" in the article lead
   (selector `a[href='/wiki/Vietnam']`, rect from `locate`). [DOM] The
   new page title must contain "Vietnam" and the URL must contain
   `/wiki/Vietnam`.
7. [KEYBOARD] Press Alt+Left to go back. [DOM] Within 5 s (poll), the
   title must return to the Ho Chi Minh City article.
8. [DOM] Pre-close check: the active title must contain "Ho Chi Minh
   City". [KEYBOARD] Press Ctrl+W. [CHECK] The title set must equal
   the step 0 list.

Pass: article opens, search works, the named link navigates, back returns.
Fail: any navigation does nothing, the page stays blank, the title never
changes, or a click lands on the wrong element. Evidence: screenshot of
the stuck page + the DOM title + the curl control result.

## ZT-02 Search inside a page (120 s expected, 240 s max)

Goal: an ordinary user finds a word inside a long article with Ctrl+F.
Preconditions: ZT-00 passed. Step 0: record the pre-scenario title list.

1. [KEYBOARD] Ctrl+L, type `en.wikipedia.org/wiki/Ho_Chi_Minh_City`,
   press Enter.
2. [DOM] Within 10 s (poll), the title must contain "Ho Chi Minh City".
   [CHECK CLI laptop] `curl -s -o /dev/null -w "%{http_code}"
   https://en.wikipedia.org/wiki/Ho_Chi_Minh_City` must return 200.
   If the curl control fails, this scenario is INCONCLUSIVE, not FAIL.
3. [KEYBOARD] Press Ctrl+F. [OBSERVE] The find input must be visible
   in the screenshot. Record its position (top or bottom) in the report.
4. [KEYBOARD] Type `population` in the find bar and press Enter.
5. [OBSERVE] The screenshot must show the find bar reading a match
   count ("N of M" or equivalent) with N at least 1, and the match
   highlighted in the page. [DOM] `eval
   "document.body.innerText.includes('population')"` must be true.
   Do not click the highlighted match: a user who finds a word reads it
   where it is highlighted.
6. [KEYBOARD] Press Escape to close the find bar. [OBSERVE] The find
   input must no longer be visible. [CHECK CLI laptop] `ps` must still
   show the zen-bin process alive.
7. [DOM] Pre-close check: the active title must contain "Ho Chi Minh
   City". [KEYBOARD] Press Ctrl+W. [CHECK] The title set must equal
   the step 0 list.

Pass: the find bar appears, a match is found and visible, Escape closes it.
Fail: Ctrl+F does nothing, the find bar never appears, no match is reported
on a page that contains the word, or the highlight never becomes visible.
Evidence: screenshot of the page with the find bar state + the DOM check.

## ZT-03 Open a link in a new tab and switch tabs (180 s expected, 300 s max)

Goal: an ordinary user opens a link in a new tab with a middle-click and
moves between tabs with the sidebar and the keyboard.
Preconditions: ZT-00 passed. Step 0: record the pre-scenario title list.

1. [KEYBOARD] Ctrl+L, type
   `en.wikipedia.org/wiki/Ho_Chi_Minh_City`, press Enter. [DOM] Within
   10 s (poll), the title must contain "Ho Chi Minh City". [CHECK CLI
   laptop] `curl -s -o /dev/null -w "%{http_code}"
   https://en.wikipedia.org/wiki/Ho_Chi_Minh_City` must return 200.
   If the curl control fails, this scenario is INCONCLUSIVE, not FAIL.
2. [MOUSE] Middle-click the link with text "Vietnam" in the article
   lead (selector `a[href='/wiki/Vietnam']`, rect from `locate`). This
   is the only path: there is no keyboard fallback. If the link does
   not exist, FAIL and report it, do not switch to another test.
   Expected: a new tab opens and becomes active.
3. [DOM] List tabs via Marionette: the count must be exactly one more
   than step 0, and the active tab title must contain "Vietnam".
4. [MOUSE] Click the Ho Chi Minh City tab row in the Zen sidebar
   (fresh observe coords plus a named anchor, screenshot saved).
   [DOM] The active tab title must contain "Ho Chi Minh City". This
   step directly re-tests F-001: if the sidebar click does nothing,
   record it as F-001 reproducing.
5. [KEYBOARD] Press Ctrl+Tab. [DOM] The active tab must CHANGE (record
   the new title). This step tests that the switch happens, not a
   specific destination order: Firefox Ctrl+Tab order is
   most-recently-used, not sidebar order. This is a cross-channel
   comparison with step 4, not a second destination assertion.
6. [DOM] Pre-close check: the active title must be one of the two
   scenario tabs ("Ho Chi Minh City" or "Vietnam"). [KEYBOARD] Press
   Ctrl+W.
7. [DOM] Pre-close check again: the active title must be the remaining
   scenario tab. [KEYBOARD] Press Ctrl+W. [CHECK] The title set must
   equal the step 0 list.

Pass: the middle-click opens the new tab, the sidebar click switches tabs,
Ctrl+Tab switches again, cleanup restores the title set.
Fail: the sidebar click does nothing, the tab count is wrong, Ctrl+Tab does
nothing, or a closed tab reappears. Evidence: screenshot of the sidebar
state + the Marionette tab list before and after each switch.

## ZT-04 Bookmark a page (120 s expected, 240 s max)

Goal: an ordinary user bookmarks the Ho Chi Minh City Wikipedia article
and finds the bookmark again.
Preconditions: ZT-00 passed. Step 0: record the pre-scenario title list.

1. [KEYBOARD] Ctrl+L, type
   `en.wikipedia.org/wiki/Ho_Chi_Minh_City`, press Enter. [DOM] Within
   10 s (poll), the title must contain "Ho Chi Minh City". [CHECK CLI
   laptop] `curl -s -o /dev/null -w "%{http_code}"
   https://en.wikipedia.org/wiki/Ho_Chi_Minh_City` must return 200.
   If the curl control fails, this scenario is INCONCLUSIVE, not FAIL.
2. [OBSERVE] Pre-check: the bookmark star in the address bar must be
   empty (not bookmarked). If the star is filled or the article is
   already bookmarked, STOP the scenario and report it. Do not proceed
   to the delete step.
3. [KEYBOARD] Press Ctrl+D. [OBSERVE] The bookmark dialog must appear.
   [MOUSE] Click the primary button in the dialog and record its exact
   label as shown (for example Save or Done). Do not press Escape
   afterwards.
4. [OBSERVE] The star must now be filled. [CHECK CLI laptop] `ps` must
   still show the zen-bin process alive. Bookmark state is verified by
   observe (star plus the library row in step 5): no reliable shell read
   of Zen's live bookmark store exists without sqlite3, so no CLI
   bookmark check is claimed here.
5. [CHECK] Open the bookmark library with Ctrl+Shift+O only (one path).
   [OBSERVE] The library must list a row titled "Ho Chi Minh City"
   with the article URL. Record the row and the row count.
6. [MOUSE] Click that bookmark row in the library. [DOM] The active
   tab must load the article and the title must contain "Ho Chi Minh
   City".
7. [OBSERVE] In the library, select the row titled "Ho Chi Minh City"
   and verify its title AND URL before deleting anything. [KEYBOARD]
   Press Delete. [CHECK] List the library again: the row count must be
   exactly one fewer and no other bookmark may have vanished.
   [OBSERVE] The star on the article tab must be empty again.
8. [DOM] Pre-close check: the active title must contain "Ho Chi Minh
   City". [KEYBOARD] Press Ctrl+W. [CHECK] The title set must equal
   the step 0 list.

Pass: the bookmark is created, found in the library, reopens the page, and
is deleted afterwards, with no other bookmark touched.
Fail: Ctrl+D does nothing, the dialog never appears, the bookmark is not in
the library, clicking it does not navigate, or the star never shows the
bookmarked state. Evidence: screenshot of the dialog and the library +
the DOM title.

## ZT-05 Switch workspace and back (120 s expected, 240 s max)

Goal: an ordinary user switches to another Hyprland workspace and comes
back, and Zen is exactly where they left it. This tests the window
manager, not the browser, and it directly re-tests owner-reported F-002.
A failure here is scored as a window-manager failure, not a browser
failure.
Preconditions: ZT-00 passed. Step 0: record the pre-scenario title list.
If a Ho Chi Minh City article tab is already open, use it and do not close
it at the end; track it by title and URL.

1. [CHECK CLI laptop] Record the starting workspace number N from
   `hyprctl activeworkspace` and Zen's workspace from `hyprctl
   clients`. [DOM] Record the active tab title. If no article tab is
   open, open one now (Ctrl+T, type
   `en.wikipedia.org/wiki/Ho_Chi_Minh_City`, press Enter; the title
   must contain "Ho Chi Minh City" within 10 s).
2. [KEYBOARD] Press Super+M, where M is N+1 (a different workspace).
   [CHECK CLI laptop] `hyprctl activeworkspace` must report M, and
   `hyprctl clients` must not list the Zen window on workspace M.
   [OBSERVE] The screenshot of workspace M must not show the Zen window.
3. [KEYBOARD] Press Super+N to switch back. [CHECK CLI laptop]
   `hyprctl activeworkspace` must report N, and `hyprctl clients`
   must show Zen on workspace N. [DOM] The active tab title must still
   contain "Ho Chi Minh City". [OBSERVE] The article page must be
   visible.
4. [MOUSE] Click the centre of the h1 "Ho Chi Minh City" (rect from
   `locate "h1"`; the heading is not a link, so the click cannot
   navigate away). Before the click, record `eval
   "Math.floor(performance.now())"` as T1. After the click, [DOM] the
   title and URL must be identical to before, and a fresh
   `performance.now()` reading T2 must be greater than T1 (the page did
   not reload).
5. [KEYBOARD] Press Super+M again, then Super+N again. [DOM] The title
   must still contain "Ho Chi Minh City". [CHECK CLI laptop] Zen must
   be on workspace N.
6. If this scenario opened the article tab: [DOM] pre-close check (the
   active title must contain "Ho Chi Minh City"), [KEYBOARD] press
   Ctrl+W. If the tab already existed at step 0, leave it open.
   [CHECK] The title set must equal the step 0 list.

Pass: both round trips return to the same tab with the same content, and
no window is lost or stranded on another workspace.
Fail: the screen goes blank or black after a switch, Zen disappears, the
tab closes by itself, the wrong workspace shows, or Zen comes back on the
wrong workspace. Record the exact symptom with a screenshot after each
switch. Evidence: hyprctl output before and after each switch +
screenshots.

## ZT-06 Download a file and open it (180 s expected, 300 s max)

Goal: an ordinary user downloads a real document (a US tax form PDF) and
opens it in the browser.
Preconditions: ZT-00 passed. Step 0: record the pre-scenario title list.
The file is removed at the end of the scenario.

1. [KEYBOARD] Ctrl+L, type
   `https://www.irs.gov/pub/irs-pdf/fw9.pdf`, press Enter.
2. [DOM] Within 15 s (poll), BOTH must hold: the built-in PDF viewer
   renders a page, AND the title contains "fw9.pdf". A title-only pass
   fails. [CHECK CLI laptop] `curl -sI` on the same URL must return
   200 with Content-Type application/pdf. If the curl control fails,
   this scenario is INCONCLUSIVE, not FAIL.
3. [CHECK CLI laptop] `ls -la ~/Downloads/fw9.pdf` must report no such
   file. If the file already exists, move it aside to
   `/tmp/fw9.pdf.<timestamp>` and note it in the report. Do not delete
   a pre-existing file.
4. [MOUSE] Click the download button in the PDF viewer toolbar
   (top-right, download icon; fresh observe coords plus a named anchor,
   screenshot saved). This is the only path: there is no Ctrl+S
   fallback. If the button is not found, FAIL with a screenshot.
5. [CHECK CLI laptop] Poll `ls -la ~/Downloads/fw9.pdf` every 2 s for
   up to 20 s: the file must exist, be larger than 0 bytes, and have an
   mtime within this run. `file ~/Downloads/fw9.pdf` must report a PDF
   document.
6. [MOUSE] Click the downloaded file entry in the download panel (fresh
   observe coords plus a named anchor, screenshot saved). [DOM] The PDF
   must render again in a new tab.
7. [DOM] Pre-close check on the PDF tab (title contains "fw9.pdf").
   [KEYBOARD] Press Ctrl+W. [CHECK CLI laptop] `rm
   ~/Downloads/fw9.pdf` only if step 5 proved this run downloaded it
   (mtime within the run). `ls` must confirm it is gone. If step 3
   moved a pre-existing file aside, restore it from /tmp and note it.
8. [DOM] Pre-close check on the original tab (title contains "fw9.pdf").
   [KEYBOARD] Press Ctrl+W. [CHECK] The title set must equal the step
   0 list.

Pass: the PDF renders, the download lands on disk with a real size and a
fresh mtime, it opens again, and it is removed afterwards.
Fail: the PDF never renders, the download never starts, the file is 0
bytes or missing, the download panel never appears, or the file cannot be
removed. Evidence: screenshot of the viewer and the download panel +
ls and file output.

## ZT-07 Fill and submit a web form (300 s expected, 360 s max)

Goal: an ordinary user fills in a form and submits it, and the site echoes
the values back. The form lives on httpbin.org, a developer test service
used here only because no public login-free form with an echo exists; the
behaviour under test is form filling and submission, not the site itself.
The values are placeholders, not the owner's data.
Preconditions: ZT-00 passed. Step 0: record the pre-scenario title list.

1. [KEYBOARD] Ctrl+L, type `https://httpbin.org/forms/post`, press
   Enter.
2. [DOM] Within 10 s (poll), the form must be present: an input named
   `custname`, an input named `custtel`, a select named `size`, a
   textarea named `comments`. [CHECK CLI laptop] `curl -s -o /dev/null
   -w "%{http_code}" https://httpbin.org/forms/post` must return 200.
   If the curl control fails, this scenario is INCONCLUSIVE, not FAIL.
3. [MOUSE] Click the `custname` input (rect from `locate
   "[name=custname]"`). [KEYBOARD] Type `Nguyen Van A`. [DOM] `eval
   "document.querySelector('[name=custname]').value"` must be exactly
   `Nguyen Van A`. Retry rule: if it mismatches, clear the field and
   retype once, then fail if it still mismatches.
4. [MOUSE] Click the `custtel` input (rect from `locate
   "[name=custtel]"`). [KEYBOARD] Type `0901234567`. [DOM] The value
   must be exactly `0901234567`. Same retry rule as step 3.
5. [KEYBOARD] Focus the `size` select (click it once to focus, rect
   from `locate "[name=size]"`), then press the Down arrow key until
   the value is `medium`, or type `m` until it is `medium`. [DOM]
   `eval "document.querySelector('[name=size]').value"` must be
   `medium`. The native select dropdown is an OS popup with no DOM
   rect, so the choice is made by keyboard only.
6. [MOUSE] Click the `comments` textarea (rect from `locate
   "[name=comments]"`). [KEYBOARD] Type `Ordinary user test, no login,
   no account.` [DOM] The value must match exactly. Same retry rule
   as step 3.
7. [MOUSE] Click the submit button (rect from `locate
   "button[type=submit], input[type=submit]"`). [DOM] Within 10 s
   (poll), the result page must show the submitted values: the echoed
   form data must contain `Nguyen Van A`, `0901234567`, `medium`, and
   the comment text.
8. End the scenario on the result page. [DOM] Pre-close check: `eval
   "location.href"` must contain `httpbin.org/post`. [KEYBOARD] Press
   Ctrl+W. [CHECK] The title set must equal the step 0 list.

Pass: every field holds what was typed, the submit echoes all four values.
Fail: typing does not land in the field, the select does not change, the
submit does nothing, or the echo misses a value. Evidence: screenshot of
the filled form and the result page + the DOM values before submit.

## ZT-08 Back, forward, and reload (180 s expected, 300 s max)

Goal: an ordinary user reads three Wikipedia articles on one topic, then
retraces them with back, forward, and reload.
Preconditions: ZT-00 passed. Step 0: record the pre-scenario title list.

1. [KEYBOARD] Ctrl+L, type
   `en.wikipedia.org/wiki/Ho_Chi_Minh_City`, press Enter. [DOM] Within
   10 s (poll), the title must contain "Ho Chi Minh City".
2. [KEYBOARD] Ctrl+L, type `en.wikipedia.org/wiki/Vietnam`, press
   Enter. [DOM] Within 10 s (poll), the title must contain "Vietnam".
3. [KEYBOARD] Ctrl+L, type
   `en.wikipedia.org/wiki/Southeast_Asia`, press Enter. [DOM] Within
   10 s (poll), the title must contain "Southeast Asia". [CHECK CLI
   laptop] `curl -s -o /dev/null -w "%{http_code}"
   https://en.wikipedia.org/wiki/Southeast_Asia` must return 200. If
   the curl control fails, this scenario is INCONCLUSIVE, not FAIL.
4. [MOUSE] Click the Back button in the toolbar (fresh observe coords,
   named anchor "Back arrow, top-left, left of the address bar",
   screenshot saved). [DOM] Within 5 s (poll), the title must contain
   "Vietnam".
5. [MOUSE] Click the Back button again. [DOM] Within 5 s (poll), the
   title must contain "Ho Chi Minh City".
6. [MOUSE] Click the Forward button (fresh observe coords, named anchor
   "Forward arrow, top-left, next to the Back arrow", screenshot saved).
   [DOM] Within 5 s (poll), the title must contain "Vietnam" again.
7. [DOM] Before reloading, record `eval
   "Math.floor(performance.now())"` as T1. [KEYBOARD] Press Ctrl+R to
   reload. [DOM] Within 10 s (poll), record T2 the same way: T2 must be
   less than T1 (a fresh page, not the old one still sitting there),
   the title must still contain "Vietnam", and [OBSERVE] the article
   heading "Vietnam" must be visible in the screenshot.
8. [KEYBOARD] Press Alt+Left (back) and then Alt+Right (forward). [DOM]
   After Alt+Left the title must contain "Ho Chi Minh City"; after
   Alt+Right the title must contain "Vietnam". These are the exact
   titles, in order.
9. [DOM] Pre-close check: the active title must contain "Vietnam".
   [KEYBOARD] Press Ctrl+W. [CHECK] The title set must equal the step
   0 list.

Pass: back and forward follow history exactly, reload provably reloads.
Fail: back or forward does nothing, the history order is wrong, reload
leaves the old page in place, or the toolbar buttons do not respond.
Evidence: screenshot after each navigation + the DOM title at each step.

## ZT-09 Open many tabs, close them, reopen them (300 s expected, 360 s max)

Goal: an ordinary user opens three research tabs on one topic, closes
them, and brings them back with reopen-closed-tab.
Preconditions: ZT-00 passed. Step 0: record the pre-scenario title list.

1. [KEYBOARD] Press Ctrl+T, type
   `en.wikipedia.org/wiki/Ho_Chi_Minh_City`, press Enter. [DOM] Within
   10 s (poll), the title must contain "Ho Chi Minh City".
2. [KEYBOARD] Press Ctrl+T, type `en.wikipedia.org/wiki/Vietnam`,
   press Enter. [DOM] Within 10 s (poll), the title must contain
   "Vietnam".
3. [KEYBOARD] Press Ctrl+T, type
   `en.wikipedia.org/wiki/Southeast_Asia`, press Enter. [DOM] Within
   10 s (poll), the title must contain "Southeast Asia". [CHECK CLI
   laptop] `curl -s -o /dev/null -w "%{http_code}"
   https://en.wikipedia.org/wiki/Southeast_Asia` must return 200. If
   the curl control fails, this scenario is INCONCLUSIVE, not FAIL.
4. [DOM] List tabs via Marionette: the count must be exactly 3 more
   than step 0.
5. [MOUSE] Hover the Southeast Asia tab row in the sidebar until its X
   appears, then click the X (fresh observe coords, screenshot saved
   before the click). [DOM] The count must drop by 1 AND the active
   tab must be one of the scenario's own tabs (Ho Chi Minh City or
   Vietnam). Do not assert which one: activation after close is
   most-recently-used behaviour, not a specified rule. Then click the
   Vietnam tab row in the sidebar to make it active before step 6.
6. [DOM] Pre-close check: the active title must contain "Vietnam".
   [KEYBOARD] Press Ctrl+W. [DOM] The count must drop by 1 and the
   active tab must be the Ho Chi Minh City tab.
7. [KEYBOARD] Press Ctrl+Shift+T to reopen the last closed tab. [DOM]
   Within 5 s (poll), the count must rise by 1 and the active tab
   title must contain "Vietnam" (reopen restores the most recently
   closed tab first). [CHECK CLI laptop] `ps` must still show the
   zen-bin process alive.
8. [KEYBOARD] Press Ctrl+Shift+T again. [DOM] Within 5 s (poll), the
   count must rise by 1 and the active tab title must contain
   "Southeast Asia".
9. Close the three tabs one by one. Before EACH Ctrl+W press, [DOM]
   the active title must be one of the three scenario titles ("Ho Chi
   Minh City", "Vietnam", "Southeast Asia"). If it is anything else,
   STOP and report, do not press. [KEYBOARD] Press Ctrl+W, repeat the
   check, press Ctrl+W, repeat the check, press Ctrl+W. [CHECK] The
   title set must equal the step 0 list.

Pass: the count is exact at every step, reopen-closed-tab restores the tabs
in most-recently-closed order, cleanup restores the title set.
Fail: the count is wrong at any step, reopen-closed-tab restores the wrong
tab or nothing, or a close removes two tabs at once. Evidence: the
Marionette tab list after every step + a screenshot of the sidebar.

## ZT-10 Sidebar tab switching and sidebar collapse (180 s expected, 300 s max)

Goal: an ordinary user switches tabs from the Zen sidebar and collapses and
expands the sidebar. This directly re-tests F-001 and the 22:25 screenshot
(sidebar collapsed to icons, no tab list).
Preconditions: ZT-00 passed. Step 0: record the pre-scenario title list.

1. [KEYBOARD] Ctrl+T, type
   `en.wikipedia.org/wiki/Ho_Chi_Minh_City`, press Enter. [DOM] Within
   10 s (poll), the title must contain "Ho Chi Minh City".
2. [KEYBOARD] Ctrl+T, type `en.wikipedia.org/wiki/Vietnam`, press
   Enter. [DOM] Within 10 s (poll), the title must contain "Vietnam".
   [CHECK CLI laptop] `curl -s -o /dev/null -w "%{http_code}"
   https://en.wikipedia.org/wiki/Vietnam` must return 200. If the curl
   control fails, this scenario is INCONCLUSIVE, not FAIL.
3. [OBSERVE] Look at the sidebar in a fresh observe. Exact observable:
   each tab row must show at least 10 characters of the tab title. If
   the sidebar shows only icons with no tab titles, record F-001
   reproducing with a screenshot, then expand the sidebar with the
   step 6 toggle, verify the rows appear, and only then run steps 4
   and 5. If the rows never appear, FAIL ZT-10 at step 3 and skip
   steps 4 to 6 instead of running them blind.
4. [MOUSE] Click the Ho Chi Minh City tab row in the sidebar (fresh
   observe coords plus a named anchor, screenshot saved). [DOM] Within
   5 s (poll), the active tab title must contain "Ho Chi Minh City"
   and the page content must be visible.
5. [MOUSE] Click the Vietnam tab row in the sidebar (fresh observe
   coords plus a named anchor, screenshot saved). [DOM] Within 5 s
   (poll), the active tab title must contain "Vietnam".
6. [MOUSE] Identify the sidebar collapse toggle first: hover the icons
   at the top of the sidebar and read their tooltips from a fresh
   observe. The toggle is the one whose tooltip mentions collapsing or
   expanding the sidebar. If no tooltip matches, STOP and report the
   actual labels instead of guessing. Click the toggle. [OBSERVE]
   Record the sidebar state after this FIRST click before doing the
   second. Click the toggle again. [OBSERVE] The sidebar must be back
   in its starting state. [DOM] The active tab title must not change
   during either toggle. [CHECK CLI laptop] Record `hyprctl clients`
   window geometry before and after: the toggle must not resize or move
   the window.
7. [DOM] Pre-close check before EACH press: the active title must be
   one of the two scenario tabs. [KEYBOARD] Press Ctrl+W, repeat the
   check, press Ctrl+W. [CHECK] The title set must equal the step 0
   list.

Pass: every sidebar click switches the tab within 5 s, the sidebar shows
readable tab rows, collapse and expand both work without changing the tab
or moving the window.
Fail: a sidebar click does nothing, the sidebar shows only icons with no
way to see tab titles, the toggle does nothing, or a toggle closes a tab.
Evidence: screenshot of the sidebar before and after every click + the
DOM active title after every click.

## Run order and reporting

Run in order: ZT-00, then ZT-01 to ZT-10. Stop at the first BLOCKED gate.
Report per scenario: PASS, FAIL, INCONCLUSIVE, or RETRIED, wall-clock
start and end, elapsed, and for every failure the finding entry (F-00x)
with screenshot path.

Report template (fill in for every scenario): goal, verdict, start/end,
elapsed, channels used (DOM steps: list them; CLI steps: list them;
mouse steps: list them; keyboard steps: list them), findings with
evidence. A scenario that did not use all four channels is reported as
such and does not claim composite coverage.

Total expected run time: about 45 minutes for all 10 scenarios plus the
gate. Maximum: 90 minutes. If the run passes 90 minutes, stop, report
what finished, and hand the rest to Muse.

Traceability: the two owner-reported errors in the findings list are also
logged in the error summary file as J1-J6 and in the todolist as 4.7-4.12
(recorded by Muse on 21/11). New findings from this run go into the same
two places when the run report lands.

## What this file is NOT

- It is not a fixture suite. Nothing here runs on a local fixture page.
- It is not a self-grading suite. The author (ZT-A) never runs these
  scenarios. The executor (ZT-B) runs them blind and reports the evidence.
- It is not a replacement for the existing realistic suites (codex-y5,
  agy-y2, batch-3). Those test web apps in fixtures; this file tests the
  browser itself the way an ordinary user meets it.
