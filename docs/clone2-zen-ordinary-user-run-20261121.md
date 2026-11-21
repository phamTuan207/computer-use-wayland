# Blind run of Zen ordinary-user test scenarios on Firefox

Date: 2026-11-21, 22:46 to 23:22 +07 (about 36 minutes, inside the 90 minute budget).
Scenario file: `improvements/zen-ordinary-user-tests-20261121.md`, revision v2, from `origin/todolist-push`.
Author: Worker ZT-A. Executor: Worker ZT-B (see the blindness basis note below).
Stand-in: Firefox 160.0.1, headed, under Xvfb:98 at 1920x1080, driven by Selenium 4.53
and geckodriver 0.37.1. One fresh browser profile per scenario. Zen itself never
ran on this machine, so every Zen-only difference is listed in the adaptations
section below, and anything that needs Zen is marked NOT APPLICABLE rather than
claimed from the stand-in.

## Result summary

11 scenarios, ZT-00 to ZT-10. Ran: 10. Not applicable: 1 (ZT-05).
Pass: 6 (4 clean, 2 qualified). Fail: 4. Not applicable: 1.

| Scenario | Verdict | Window (+07) | Elapsed |
|---|---|---|---|
| ZT-00 Health gate | PASS (stand-in adaptation) | about 22:46 to 22:55 | about 9 min |
| ZT-01 Open a site and read an article | FAIL at step 6 | about 22:56 to 22:59 | about 3 min |
| ZT-02 Search inside a page | PASS | about 23:00 to 23:02 | about 2 min |
| ZT-03 Open a link in a new tab | FAIL at step 2 | about 23:02 to 23:03 | about 1 min |
| ZT-04 Bookmark a page | PASS | about 23:03 to 23:05 | about 2 min |
| ZT-05 Switch workspace and back | NOT APPLICABLE | about 23:05 | 0 s |
| ZT-06 Download a file and open it | FAIL at step 6 | about 23:06 to 23:08 | about 3 min |
| ZT-07 Fill and submit a web form | FAIL at step 5 | about 23:11 to 23:12 | about 2 min |
| ZT-08 Back, forward, reload | PASS | about 23:13 to 23:14 | about 1 min |
| ZT-09 Open many tabs, close, reopen | PASS, one sub-check unverified | about 23:14 to 23:18 | about 4 min |
| ZT-10 Sidebar switching and collapse | PASS except step 6 not applicable | about 23:19 to 23:22 | about 3 min |

Time note: the per-scenario records in `scenarios.jsonl` (the executor's own
timing file, at `~/workspace/tools/ztb/scenarios.jsonl`) are unreliable across
the board, not only for ZT-06: ZT-00 is recorded as starting 22:55:06 while
the run log shows activity from 22:46:34; ZT-04 is recorded as 23:08 to 23:16
(8 min) while its screenshots are stamped 23:03:12 to 23:05:04; ZT-05 is
recorded as 23:16 while the run places it about 23:05; ZT-09 is recorded as
ending 23:20 (6 min) while its last shot is 23:18:12; ZT-10 is recorded as
ending 23:25 (5 min) while its last shot is 23:22:13; ZT-03 is recorded as
180 s while the table below says about 1 min, and ZT-03 has no screenshots,
so neither figure is directly anchored. The windows above are anchored on
screenshot file timestamps and the run log (`~/workspace/tools/ztb/runlog.jsonl`,
first entry 22:46:34, last 23:22:13), which agree with each other, and that
shot-anchored table is the reliable basis. Elapsed figures are approximate
to the minute. The total run time, about 36 minutes, is solid.
Raw logs (outside the repo): `~/workspace/tools/ztb/runlog.jsonl`,
`~/workspace/tools/ztb/scenarios.jsonl`, `~/workspace/tools/ztb/results.jsonl`.

Blindness basis: the executor (Worker ZT-B) was a separate agent from the
scenario author (Worker ZT-A), the scenario file v2 was committed at
22:36:47 +07 and the run started 22:46:34 +07, about 10 minutes later, and
the executor's behaviour supports blindness: ZT-03 stopped at the failing
selector per the scenario rule instead of substituting, ZT-07 made no
substitution for the submit button, and the genuine misclick at (1878,63)
in ZT-06 was a real aim error. But no artifact timestamps the executor's
first read of the scenario file, so prior exposure is neither proved nor
disproved. "Blind" here describes that operational basis, not a verified
property.

Worst failure in one line: ZT-06 step 6, clicking the downloaded file in the
download panel does nothing, no new tab and no navigation after two clicks
on the entry, while the file itself downloads correctly.

## Owner findings re-checked

F-001 (22:25 21/11, Zen sidebar collapsed to icons with no tab list, screenshot
a14e82980194): partly re-checked. The tab-clicking half does NOT reproduce on
this stand-in: tab rows show full readable titles and every tab-row click
switched tabs within 5 s (ZT-09 step 5, ZT-10 steps 3 to 5). The collapse half
cannot be re-checked here: Firefox has no Zen-style sidebar collapse toggle
(ZT-10 step 6), so F-001 stays open for the laptop run on that half only.

F-002 (22:25 21/11, switching workspaces has many strange errors): cannot be
re-checked here. ZT-05 is NOT APPLICABLE on this stand-in, no Hyprland, no
workspaces. F-002 stays open for the laptop run.

## New findings

F-003, live-page selector drift, Wikipedia (ZT-01 step 6, ZT-03 step 2).
The selector `a[href='/wiki/Vietnam']` matches 0 elements on the live Ho Chi
Minh City article. Links with the text "Vietnam" exist, but their hrefs are
absolute `https://en.wikipedia.org/wiki/Vietnam`, not the relative path the
scenario assumes. Verified twice: DOM count 0 and curl HTML grep 0. Both
scenarios were run as written with no substitution. This is a scenario-vs-live-
page mismatch, not a browser failure. Evidence:
`docs/clone2-zen-ordinary-user-run-20261121-screenshots/zt01_06_nolink_evidence.png`.

F-004, download panel entry does not open the file (ZT-06 step 6). The PDF
downloads correctly (140815 bytes, matches Content-Length, `file` reports PDF
1.7) and the download panel lists fw9.pdf as "Completed - 138 KB", but
clicking the entry opened no new tab and changed no URL. Still 1 tab at the
IRS URL after both entry clicks. The exact click sequence, from
`~/workspace/tools/ztb/runlog.jsonl` (mouse_click_screen events, all with
recorded coordinates): (1878,63) at 23:07:33, a wrong click that opened the
Extensions panel instead of Downloads; (1895,150) at 23:07:46; (1788,63) at
23:07:47, the Downloads toolbar toggle; shot 06b at 23:07:49, panel open with
the entry listed; (1390,108) at 23:08:01, the first entry click; shot 06c at
23:08:04, panel closed, still 1 tab; (1788,63) at 23:08:40, panel reopened;
(1385,107) at 23:08:41, the second entry click; shot 06d at 23:08:55, still
1 tab. One more Downloads toggle click at (1788,63) at 23:09:21 followed,
before step 7. In `zt06_06b_downloads.png` (1920x1080) the fw9.pdf entry row
sits about x 1340-1760, y 90-140, with the filename text about (1390,108),
so both (1390,108) and (1385,107) land squarely on the entry row. The two
23:08:40/41 clicks one second apart are not a double-click; the earlier
"double-click" wording is withdrawn. The file, the viewer, and the panel
listing all work; only open-from-panel does nothing observable on this
stand-in. Correction note: an earlier review draft claimed no click
coordinates exist for these attempts and proposed downgrading this finding
to inconclusive. That premise was wrong: the runlog records coordinates for
every click, and they establish the entry clicks landed on target, so F-004
stands as a browser failure. The panel-state observation stands as secondary
evidence: shot 06b shows the panel still open after the 23:07:46/47 clicks,
and shot 06c shows it closed after the first entry click, which is
consistent with the entry click landing. Evidence:
`docs/clone2-zen-ordinary-user-run-20261121-screenshots/zt06_06b_downloads.png`,
`zt06_06d_after_second_click.png`.

F-005, form size control is a radio group, not a select (ZT-07 step 5). The
live httpbin form uses radio buttons for size (small, medium, large), while
the scenario requires a select named `size` and checks
`document.querySelector('[name=size]').value`. Clicking the first radio and
pressing Down DID move the selection to medium (diagnostic `:checked` value
medium), but the scenario check reads the first radio and always returns
"small", so the pass condition can never hold for this form. The keyboard
interaction itself works; the scenario premise is wrong. Evidence:
`docs/clone2-zen-ordinary-user-run-20261121-screenshots/zt07_06_filled.png`.

F-006, submit button locate fails (ZT-07 step 7). The scenario selector
`button[type=submit], input[type=submit]` matches nothing. The live form
submit is a BUTTON with no type attribute (default submit behaviour, text
"Submit order"), so the attribute selector cannot match it. No substitution
was made, per the blind rule, so the submit and echo were not tested. The
step 8 pre-close check then also failed (still on /forms/post, never reached
/post), so Ctrl+W was not pressed and the browser was closed by driver quit
instead. Evidence:
`docs/clone2-zen-ordinary-user-run-20261121-screenshots/zt07_07_submit_locate_fail.png`.

## Rig note (not a product finding)

R-001, Marionette tab listing changes the active tab. The helper that lists
all tabs switches Selenium through every handle and back to the first handle,
and each switch changes the browser's visible active tab. In ZT-09 step 5 the
tab list was read between the X click and the screenshot, so the screenshot
showed the blank baseline tab active and the step's active-tab clause could
not be verified. The same MRU activation was verified cleanly in ZT-09 steps
6 and 9 and in ZT-10 step 7 by taking the screenshot BEFORE any tab listing.
Future runs should screenshot first, then list tabs.

## Environment incident

During ZT-03 the /tmp tmpfs (512M) filled to 100 percent from stale Firefox
profiles plus a sibling agent's copy. 161M was freed by deleting two stale
profiles (`/tmp/rust_mozprofileVTv0c3` 102M, `/tmp/rust_mozprofileiZNZ2U` 60M)
after confirming no live firefox process referenced them. The sibling's files
were left untouched. No scenario result was affected.

## The known segfault did not reproduce

The pre-existing Firefox segfault reported as blocking t09/t10 live runs did
NOT occur in this run, with a caveat: the doc never recorded what triggers
that segfault or where it was reported, so this is "no crash observed during
tab churn, trigger unknown", not a proven non-reproduction. ZT-09 and ZT-10
together performed 5 tab opens, 1 tab-bar X close, 3 Ctrl+W closes, 2
Ctrl+Shift+T reopens, and 3 more Ctrl+W closes. The browser stayed alive
through all of them, the firefox process was confirmed alive after each
reopen, and no minidump appeared in any scenario. Caveat on the minidump
evidence: the server's end-of-run check globbed only
`/tmp/rust_mozprofile*/minidumps/`, while the profiles actually used live in
`~/workspace/tools/ztb/tmp/`; a wider search of both locations found no
`.dmp` files, so the conclusion holds, but the stated evidence path was
incomplete. Ctrl+W on the last tab closes the window and Marionette then
fails to decode a response, but the process exits cleanly with no minidump,
so that is a clean window close, not a segfault.

## Stand-in adaptations (Zen-only differences)

1. Zen was not run. Firefox 160.0.1 headed on Xvfb is the stand-in for every
   scenario. Anything that behaves differently in Zen is flagged, not assumed.
2. No Hyprland, no workspaces, no hyprctl on this VM. ZT-05 is NOT APPLICABLE.
   `ps` checks look for the firefox process, not zen-bin.
3. Zen's sidebar tab rows are the Firefox tab bar at the top of the window.
   Tab-row clicks, hovers, and X buttons were done on the tab bar.
4. Firefox has no Zen-style sidebar collapse toggle. ZT-10 step 6 is NOT
   APPLICABLE. The only sidebar control is "Show sidebar (Alt+Ctrl+Z)", which
   opens the bookmarks/history sidebar, not a tab sidebar collapse.
5. Ctrl+W on the last tab closes the window. Cleanup was verified by "window
   closed, process gone, no minidump" instead of the literal title-set check.
6. ZT-00 step 2 (curl 127.0.0.1:9222) was adapted: Marionette session creation
   is the deciding check, since Firefox has no CDP port. Step 6 hyprctl is
   NOT APPLICABLE.
7. A new tab is about:newtab, a privileged page whose title Marionette cannot
   read ("The command does not support browsing contexts in privileged
   scope"). It is recorded as "<unreadable>" in tab lists.
8. In ZT-06 the PDF viewer Save button opens a system Save dialog (name
   fw9.pdf, location Downloads) rather than a silent download. Save was
   clicked in the dialog at (1469,926).
9. Selenium's current handle does not follow UI tab switches (Ctrl+T, mouse
   tab clicks). Title polls that read the current handle can fail spuriously
   even when the navigation succeeded. The full tab list is the reliable
   check, and screenshots are the only ground truth for the visible active
   tab (see R-001).
10. Each scenario used a fresh browser profile, so there were no owner tabs.
    Cleanup identity is the title set against the step 0 baseline (one blank
    tab) in every scenario.

## Per-scenario reports

### ZT-00 Health gate, PASS with stand-in adaptation

Goal: prove the browser, Marionette, and cleanup work before any scenario.
Window about 22:46 to 22:55. Channels: DOM, CLI, keyboard. No mouse steps.
Steps 0 to 5 pass: Marionette session created, firefox process alive, Ctrl+L
plus typing example.com navigated, title "Example Domain". Step 2 adapted
(see adaptation 6). Step 6 hyprctl NOT APPLICABLE. Step 7 cleanup verified by
clean window close (firefox main pid gone, no minidump). No screenshot of a
failure; evidence: `zt00_00_initial.png`, `zt00_05_example.png`,
`zt00_07_after_ctrlw.png`.

### ZT-01 Open a site and read an article, FAIL at step 6

Goal: open Wikipedia, search, open the Ho Chi Minh City article, follow the
Vietnam link, go back. Window about 22:56 to 22:59. Channels: DOM, CLI,
keyboard, mouse.
Steps 1 to 5 pass: address bar focus with selection visible, Wikipedia Main
Page loaded, search box click and typing worked, HCMC article loaded with
exact title and URL. Step 6 FAIL: F-003, the selector matches 0 elements on
the live article. Step 7 not evaluable as written (premise broken by step 6);
Alt+Left itself was proven working earlier in the run, returning to the Main
Page. Evidence timing note: `zt01_06_nolink_evidence.png` is stamped
22:59:21, after `zt01_07_back.png` (22:57:23), so the step 6 evidence shot
was captured after the back navigation, implying an undocumented forward
navigation back to the HCMC article. The screenshot itself is genuine and
F-003 is independently confirmed, so this is a provenance wrinkle only.
Step 8 cleanup verified by window close. Curl control:
https://en.wikipedia.org/ returns 301 to www, 200 with -L. Evidence:
`zt01_01_ctrl_l.png`, `zt01_05_hcmc.png`, `zt01_06_nolink_evidence.png`,
`zt01_07_back.png`.

### ZT-02 Search inside a page, PASS

Goal: Ctrl+F find inside the HCMC article. Window about 23:00 to 23:02.
Channels: DOM, keyboard. No mouse steps, no CLI steps.
Ctrl+F opened the find bar at the BOTTOM of the window. Typing "population"
plus Enter gave "2 of 27 matches" with the match highlighted green in the
article lead. DOM innerText includes "population". Escape closed the find bar,
firefox stayed alive, title stayed Ho Chi Minh City. Cleanup verified by
window close. Evidence: `zt02_03_findbar.png`, `zt02_05_match.png`,
`zt02_06_escaped.png`.

### ZT-03 Open a link in a new tab and switch tabs, FAIL at step 2

Goal: middle-click the Vietnam link to open it in a new tab, switch to it.
Window about 23:02 to 23:03. Channels: DOM, keyboard, mouse.
Step 1 passes (HCMC article loaded). Step 2 FAIL exactly as the scenario's
own rule anticipates: middle-click on `a[href='/wiki/Vietnam']` raises
NoSuchElementException, 0 matches (F-003, same drift as ZT-01). Per the
scenario instruction, stopped here and did not switch to another test. Steps
3 to 7 not run. The F-001 sidebar re-test inside ZT-03 was not reached; it is
covered by ZT-10. Cleanup verified by window close. No screenshots: the
failure is a DOM locate error, already evidenced in ZT-01. This deviates
from scenario rule 7 (every error needs a screenshot), justified by the
identical selector failure evidenced in ZT-01.

### ZT-04 Bookmark a page, PASS

Goal: bookmark the HCMC article with Ctrl+D, verify in the Library, reopen
it, delete it. Window about 23:03 to 23:05. Channels: DOM, CLI, keyboard,
mouse.
Step 2 pre-check: star empty (outline). Step 3: Ctrl+D opened the Add
bookmark dialog, primary button label Save, clicked Save at (1669,344).
Step 4: star filled blue, firefox alive. Step 5: Ctrl+Shift+O opened the
Library; the Bookmarks Toolbar folder held exactly 1 row, "Ho Chi Minh City
- Wikipedi..." with the article URL. Step 6: clicking the row loaded the
article, title and URL exact. Step 7: row selected, details pane verified
Name "Ho Chi Minh City - Wikipedia" and URL
https://en.wikipedia.org/wiki/Ho_Chi_Minh_City before Delete; after Delete
the folder shows "No items", count 1 to 0, nothing else vanished, star empty
again. Step 8 cleanup verified by window close. Note: page render lagged a
few seconds behind the title on first load (blank viewport with "Transferring
data" status), then rendered fully. One extra Ctrl+W closed the Library window
first (it is a separate window, documented, not a scenario step); no
pre-close check was recorded for that extra press, which deviates from
scenario rule 6 (a pre-close check before every Ctrl+W). It closed a window,
not a tab, no harm done. Evidence:
`zt04_02_star_empty.png`, `zt04_02b_rendered.png`, `zt04_03_dialog.png`,
`zt04_04_star_filled.png`, `zt04_05_library.png`, `zt04_05b_toolbar.png`,
`zt04_06_reopened.png`, `zt04_07_deleted.png`, `zt04_08_lib_closed.png`.

### ZT-05 Switch workspace and back, NOT APPLICABLE

Goal: Hyprland workspace switching (Super+M/N, hyprctl activeworkspace,
hyprctl clients) and Zen window placement across workspaces. Window about
23:05, 0 s. Channels: none.
This VM has no Hyprland, no window manager workspaces, and no Zen. Xvfb:98
is a single static screen. F-002 therefore cannot be re-checked on this
stand-in and remains open for the laptop run. No browser behaviour is
asserted from this non-run.

### ZT-06 Download a file and open it, FAIL at step 6

Goal: download the IRS Form W-9 PDF and open it from the download panel.
Window about 23:06 to 23:08. Channels: DOM, CLI, keyboard, mouse.
Steps 1 to 5 pass: PDF viewer rendered Form W-9 page 1 of 6, title "Form W-9
(Rev. March 2024) - fw9.pdf". Step 3: no pre-existing file. Step 4: viewer
toolbar Save button found by hover tooltip at (1855,106); clicking it opened
a system Save dialog rather than a silent download; clicked Save in the
dialog at (1469,926). Step 5: file landed, 140815 bytes matching
Content-Length, `file` reports PDF document version 1.7, mtime within the
run. Step 6 FAIL: F-004, download panel listed fw9.pdf "Completed - 138 KB",
but the two entry clicks at (1390,108) and (1385,107) (see F-004 for the
full recorded sequence) opened no new tab and changed no URL. First wrong
click at (1878,63) opened the Extensions panel instead of Downloads,
corrected to (1788,63). Step 7: pre-close check
passed, Ctrl+W closed the tab, rm removed the run's file, ls confirms gone,
window closed, process gone, no minidump. Step 8 vacuous: step 6 created no
second tab, so there was no separate original tab to close. Curl control:
200, application/pdf, 140815 bytes. Evidence: `zt06_02_pdf.png`,
`zt06_04_hover_download.png`, `zt06_05_after_save_click.png`,
`zt06_06_panel.png`, `zt06_06b_downloads.png`, `zt06_06c_reopened.png`,
`zt06_06d_after_second_click.png`.

### ZT-07 Fill and submit a web form, FAIL at step 5

Goal: fill the httpbin form and submit it, echo must contain all four values.
The scenario states the values are placeholders, not the owner's data.
Window about 23:11 to 23:12. Channels: DOM, CLI, keyboard, mouse.
Step 1: https://httpbin.org/forms/post loaded (curl control 200). Step 2
does NOT meet its literal requirement: the scenario requires "a select named
`size`" present, and the live form has no select at all (see F-005). The
first field check ran too early (page still loading) and returned all false;
the re-check showed all four named fields present, though the size control
is a radio group, not the select the step requires. The scenario is recorded
as failing at step 5 in the summary table, but strictly step 2 already
failed its literal condition; this is outcome-neutral, ZT-07 fails either
way. Step 3 PASS:
clicked [name=custname], typed "Nguyen Van A", DOM value exact. Step 4 PASS:
clicked [name=custtel], typed "0901234567", DOM value exact. Step 5 FAIL:
F-005, radio group, scenario check can never pass. Step 6 PASS: comments
typed to the exact text "Ordinary user test, no login, no account.". Step 7
NOT PERFORMED as written: F-006, submit locate matches nothing, no
substitution made. Step 8 NOT PERFORMED: pre-close check requires
httpbin.org/post, the tab is still on /forms/post, so Ctrl+W was not pressed
per the pre-close rule; the browser was closed by driver quit instead, no tab
touched. Evidence: `zt07_06_filled.png`,
`zt07_07_submit_locate_fail.png`.

### ZT-08 Back, forward, reload, PASS

Goal: navigate three articles, go back and forward with toolbar buttons,
reload, go back and forward with Alt+arrows. Window about 23:13 to 23:14.
Channels: DOM, CLI, keyboard, mouse.
Steps 1 to 3 pass: three articles navigated by address bar typing (HCMC,
Vietnam, Southeast Asia), curl control 200 with -L. Steps 4 to 6 pass:
toolbar Back button clicked by real mouse at (57,63) to Vietnam, then to Ho
Chi Minh City; toolbar Forward button at (94,63) to Vietnam again. Step 7
PASS: T1 performance.now 9551 ms, after Ctrl+R T2 3405 ms, T2 less than T1,
title stayed Vietnam, h1 "Vietnam" visible in the viewport. Step 8 PASS:
Alt+Left to HCMC, Alt+Right to Vietnam, exact order. Step 9 cleanup verified
by window close. Evidence: `zt08_07_reloaded.png`.

### ZT-09 Open many tabs, close them, reopen them, PASS with one sub-check unverified

Goal: open three tabs, close two by different means, reopen both with
Ctrl+Shift+T in most-recently-closed order, close all three. Window about
23:14 to 23:18. Channels: DOM, CLI, keyboard, mouse.
Steps 1 to 3: three tabs opened by Ctrl+T plus address bar typing; tab list
showed blank plus HCMC, Vietnam, Southeast Asia (4 tabs, 3 more than step 0).
Note: the title polls failed spuriously because Selenium's current handle
does not follow UI tab switches (see adaptation 9); the tab list is the
reliable evidence and it confirmed all three loads. Step 4: count exact.
Step 5: hovered the Southeast Asia tab row and clicked its X at (883,20);
count dropped 4 to 3 and the tab was gone. Its active-tab clause is
UNVERIFIED for the R-001 harness reason; the same MRU activation was verified
cleanly in steps 6 and 9. Then clicked the Vietnam tab row at (550,20): the
tab switched by mouse and the Vietnam article rendered. Step 6 PASS:
pre-close Vietnam confirmed, Ctrl+W, count 3 to 2, active tab became Ho Chi
Minh City. Step 7 PASS: Ctrl+Shift+T restored Vietnam as the active tab,
count 2 to 3, firefox process alive. Step 8 PASS: Ctrl+Shift+T restored
Southeast Asia as the active tab, count 3 to 4, reopen order
most-recently-closed first confirmed. Step 9 PASS: three Ctrl+W presses, each
preceded by a screenshot pre-close check (after press 1 active was Vietnam,
after press 2 active was Ho Chi Minh City), after press 3 only the blank
baseline tab remained, title set equals step 0. No segfault, no minidump.
Evidence: `zt09_04_four_tabs.png`, `zt09_04b_sea_rendered.png`,
`zt09_05_hover_sea.png`, `zt09_05_after_close_sea.png`,
`zt09_05b_vietnam_active.png`, `zt09_06_after_close_vn.png`,
`zt09_07_reopen_vn.png`, `zt09_08_reopen_sea.png`,
`zt09_09a_after_w1.png`, `zt09_09b_after_w2.png`, `zt09_09c_after_w3.png`.

### ZT-10 Sidebar tab switching and sidebar collapse, PASS except step 6 not applicable

Goal: switch tabs from the sidebar and collapse and expand it. Direct
re-test of F-001. Window about 23:19 to 23:22. Channels: DOM, CLI, keyboard,
mouse.
Steps 1 to 2: two tabs opened, tab list blank plus Ho Chi Minh City plus
Vietnam. Step 3 PASS: tab rows show full readable titles, HCMC truncated at
about 24 characters, Vietnam full at 20, both well over 10 characters. F-001
does NOT reproduce on this stand-in: no collapsed-to-icons state, the tab
list is visible. Step 4 PASS: clicked the HCMC tab row at (340,20), HCMC
became active within 5 s with the article visible. Step 5 PASS: clicked the
Vietnam tab row at (550,20), Vietnam became active within 5 s with the
article visible. Step 6 NOT APPLICABLE: hovered the only sidebar control in
Firefox, the button at (21,63), and its tooltip reads "Show sidebar
(Alt+Ctrl+Z)". It does not mention collapsing or expanding the sidebar, and
Firefox has no Zen-style tab-sidebar collapse toggle, so per the step's own
rule the step stopped here and no toggle was clicked. The collapse half of
F-001 cannot be re-tested on this stand-in. Step 7 PASS: pre-close check
before each Ctrl+W; after closing Vietnam the active tab became Ho Chi Minh
City; after closing HCMC only the blank baseline tab remained, title set
equals step 0, firefox process alive, no minidump. Evidence:
`zt10_03_tabrows.png`, `zt10_04_hcmc.png`, `zt10_05_vietnam.png`,
`zt10_06_sidebar_button_tooltip.png`, `zt10_07_after_w1.png`.

## Screenshots

All screenshots are in
`docs/clone2-zen-ordinary-user-run-20261121-screenshots/` (51 files in total:
45 scenario shots named ztNN_*.png plus 6 dbg_*.png rig setup shots from
before ZT-00: `dbg_00_launched.png`, `dbg_01_example.png`,
`dbg_02_after_ctrlt.png`, `dbg_03_after_ctrll.png`, `dbg_04_after_type.png`,
`dbg_05_after_enter.png`. The 6 dbg shots are counted in the total but are
not referenced by filename anywhere else in this report; they are rig
setup shots, not scenario evidence).
Note: the repo .gitignore ignores `*.png`, so these files exist on disk but
will not be committed unless the coordinator force-adds them or adjusts the
ignore rule. That decision is the coordinator's, not this run's.

Byte-identical screenshot pairs (md5-verified): `zt07_07_submit_locate_fail.png`
is identical to `zt07_06_filled.png`; it adds no new visual evidence beyond
the step 6 state, which is consistent with nothing happening at step 7.
`zt09_04b_sea_rendered.png` is identical to `zt09_04_four_tabs.png`; the
image shows the tab bar with all four tabs, but the active tab is the blank
New Tab and the viewport is empty white, so the filename overstates what it
shows (the Southeast Asia article is not rendered in it) and the file is
annotated here rather than renamed. `zt09_05_after_close_sea.png` is
identical to `zt10_03_tabrows.png`, a cross-scenario duplicate; both states
are plausibly identical blank viewports with the same three tabs, so this is
consistent rather than contradictory, but the ZT-10 file is not an
independent capture from ZT-10. Two further consistent duplicates:
`zt06_06c_reopened.png` is identical to `zt06_06d_after_second_click.png`
(the clicks changed nothing) and `zt00_00_initial.png` is identical to
`dbg_00_launched.png` (same blank initial state).

## What still needs the laptop run

1. ZT-05 (workspace switching) and F-002: needs Hyprland on the user's
   machine.
2. F-001 collapse half: needs the real Zen sidebar and its collapse toggle.
3. ZT-01 and ZT-03 need a scenario fix first (F-003): the Wikipedia link
   selector must match the live page's absolute hrefs, or use a text-based
   locate. The browser did nothing wrong.
4. ZT-06 step 6 (F-004) needs a Zen check: does clicking a download panel
   entry open the file in Zen? The stand-in says no for Firefox.
5. ZT-07 needs a scenario fix first (F-005, F-006): the size control is a
   radio group and the submit button has no type attribute. The form fill
   itself works.
6. ZT-09 step 5 active-tab clause needs a re-run with screenshot-first
   discipline (see R-001) if a clean verdict on that clause is wanted.
