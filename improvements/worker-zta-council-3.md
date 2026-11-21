# Council review, Worker ZTA, Voice 3 (blind fairness, executability, safety)

Reviewed: `improvements/zen-ordinary-user-tests-20261121.md`, branch todolist-push, 21/11/2026.
Reviewer: Council Voice 3. The scenario file was NOT modified.

## Verdict: AMEND, do not run as-is

The scenarios are sound in shape: exact public URLs, exact expected strings in most steps, no login, fake form data, a health gate first, and cleanup inside ZT-04 and ZT-06. But as written a blind executor cannot run them exactly as specified, and the cleanup steps can close a tab the owner cares about. Every defect below is fixable by editing text, so this is AMEND, not BLOCK. Fix all numbered items, then re-review is not needed if the author confirms each item by line, but ZT-B must not start until they are fixed.

## 1. Blind fairness: the file breaks its own rule at L16-18

Rule 1 promises exact URLs, exact expected strings, and exact commands, with nothing depending on knowledge outside the file. Three gaps break that promise.

- No DOM command is ever given. L46-47 names `scripts/zen_dom.py` and its ports, but no step gives an invocation. A blind executor must read the script source to learn it has subcommands `list`, `eval "<JS>"`, and `locate "<selector>"`. Every `[DOM]` check in ZT-00 to ZT-10 depends on that undisclosed knowledge.
- No mouse command is ever given in full either. L40-44 names `computer-use act` and the Pointer class in `scripts/cu.py`, but no step gives a complete click command, so coordinates, action names, and argument order are all left to the executor to discover.
- Several steps are conditional or refer to an unnamed element, so the executor must decide, not follow. See A3, A4, and A8 below.

## 2. Executability: the chrome-click rule contradicts the scenarios

L41-44: click coordinates must come from DOM rects, never from vision estimates. But most clicks in the file are on browser chrome, not page DOM, so no DOM rect exists for them: sidebar tab rows and the tab X (ZT-03 step 5, ZT-09 step 5, ZT-10 steps 4-6), Back and Forward buttons (ZT-08 steps 4-6), the bookmark dialog and library (ZT-04 steps 3, 5, 7), and the PDF viewer download button and download panel (ZT-06 steps 4, 6). As written the executor must either break the Tools rule or stall. This is the single biggest executability defect.

Other executability defects:

- ZT-00 step 2 (L79-81) contradicts itself: it says curl must return 200, then says 404 is normal and NOT a failure. A blind executor cannot tell which value passes.
- ZT-02 step 5 (L141-144) asks Marionette (`[DOM]`) to report the find-bar match count. The find bar is browser chrome, not page DOM, so Marionette cannot read it. The check as written is uncheckable.
- ZT-05 assumes the starting workspace is 1 (L225, L231-236). If Zen starts on workspace 2, Super+2 is a no-op and the test is vacuous, and Super+1 goes to the wrong place.
- ZT-09 steps 5-6 (L370-373) assert which tab becomes active after a close (httpbin close lands on Wikipedia, Wikipedia close lands on example.com). That is Zen focus behaviour, not a specified rule, and it is asserted without a fallback if focus lands elsewhere.
- Timings are optimistic. ZT-00 expects 60 s for 7 steps including Marionette session creation, two curl checks, and a page load (L72). ZT-07 expects 240 s for 8 steps, each needing a DOM eval plus an observe plus evidence (L289). The scenario maxima sum to 51 minutes, leaving only 9 minutes inside the 60 minute total cap (L431-433) for session setup, screenshots, and reporting. Timings need the revision in A11.

Vague expectations that need an exact observable (each is currently a judgement call):

- L103-105, ZT-01 step 1: address bar "shows a highlight".
- L138-139, ZT-02 step 3: find bar "at the top or bottom".
- L233-234, ZT-05 step 2: workspace 2 shows "its own content, not a copy of Zen".
- L239-240, ZT-05 step 4: "Nothing must change except focus".
- L263-264, ZT-06 step 2: title contains dummy.pdf OR the viewer renders a page (an OR pass is two different tests).
- L341-342, ZT-08 step 7: page "is visible, not blank".
- L343-344, ZT-08 step 8: titles "must follow the history in order" with no titles listed.
- L400-402, ZT-10 step 3: sidebar shows "readable" titles.

## 3. Safety: the protected-tabs rule does not protect the tabs as written

- Count is not identity. Every scenario ends by checking only that the tab count returned to the pre-scenario count (for example L90-91, L120-121, L147-148). Closing an owner's tab and opening a new one leaves the count unchanged. The file never requires a snapshot of tab titles and URLs at the start of the run, so a wrong-tab close is undetectable by its own checks.
- Ctrl+W is pressed blind. No scenario verifies the active tab before closing it. If an earlier step failed, for example a sidebar click did nothing, which is exactly what F-001 tests, the active tab is not the test tab, and Ctrl+W closes whatever is active, which may be an owner's tab. Worst case is ZT-09 step 9 (L379-381): three Ctrl+W presses in a row with only a 1 s pause and no check between presses. One count drift turns the third press into a close of an owner's tab.
- The protected list (L22-26) is stale and incomplete. It says "include", so it is not exhaustive, and it omits the internal tabs known from the 21/11 tab count (13 about:blank tabs plus one BiDi fixture tab), while listing reddit, which was not in that count. A blind executor cannot know the full protected set from this list.
- ZT-04 can delete the owner's bookmark. There is no pre-check for whether example.com is already bookmarked. If it is, Ctrl+D opens an edit dialog, not a create dialog, and step 7 (L207-210) would delete a bookmark the owner already had. Step 7 also deletes by row position with no verification of title and URL first.
- ZT-06 can delete the owner's file. Step 3 (L267) records Downloads before the download, but step 7 (L277-278) runs `rm ~/Downloads/dummy.pdf` unconditionally. If dummy.pdf already existed before the run, the download overwrites the owner's file and the rm deletes the owner's original.
- ZT-00 has no fail-path cleanup. If the gate fails after step 4 opened a tab, the run stops (L93-95) and that tab is left open.
- ZT-05 step 4 (L239-240) clicks in the page body without first verifying Zen is focused and the Example Domain page is active. If a workspace switch landed elsewhere, that click lands in the wrong place.

What is safe as written: the form data in ZT-07 is fake (Test User, 0123456789), the download is one public PDF, no step deletes a bookmark or download except inside its own scenario, and no step touches the owner's other apps, music, or chats (L35-36).

## Required changes

### Blind and executability

- A1, L46-47 and every `[DOM]` step: give the exact `zen_dom.py` invocation for each check type, for example `python3 scripts/zen_dom.py list`, `... eval "document.title"`, `... eval "document.querySelector('[name=custname]').value"`, `... locate "<selector>"`. Give one worked example per type in Tools, then use the same form in every step. Do the same for one complete `computer-use act` click and one type action.
- A2, L41-44: resolve the chrome-click contradiction. Either explicitly permit observe-derived coordinates for browser chrome only, with the method spelled out (fresh observe, click the centre of the identified row or button, re-observe after), or replace each chrome click with a keyboard equivalent where one exists. Do not leave the rule and the scenarios in conflict.
- A3, L115-117, ZT-01 step 6: name the exact link. Give its selector or link text and its expected destination title and URL. "First link inside the article lead section" is not exact.
- A4, L166-169, ZT-03 step 3: remove the conditional branch. Pick one deterministic path (recommended: Ctrl+T, type `example.com`) and delete the wordmark alternative, or give the exact selector for the wordmark link and the exact context-menu item text.
- A5, L79-81, ZT-00 step 2: fix the contradiction. State one pass value, for example 404 is a pass for this endpoint and 200 is also a pass, and a connection refusal is the failure.
- A6, L141-144, ZT-02 step 5: make the match checkable. Either use a page-DOM check (for example eval that the page text contains `population`) or define the observe-only pass exactly (screenshot must show the find count text, transcribed as "N of M", with N at least 1).
- A7, vague expectations listed in section 2: replace each with one exact observable. ZT-08 step 8 must list the exact titles in order: Example Domain, then Wikipedia, then the form page, then back in reverse.
- A8, remove every "or" alternative and pick one exact path: L198-199 and L207-210 (ZT-04 steps 3, 5, 7: Save or Done, library by shortcut or menu, delete by right-click or Delete key), L268-270 and L274-276 (ZT-06 steps 4, 6: download button or Ctrl+S, panel click or open from Downloads), L304-305 (ZT-07 step 5: click the select then click the `medium` option, or use keyboard selection, with the exact keys).
- A9, L225 and L231-236, ZT-05: record the starting workspace number N in step 1, switch to a different workspace (N+1 or a named one), and return with Super+N. Do not hardcode 1 and 2.
- A10, L370-373, ZT-09 steps 5-6: do not assert Zen focus behaviour as a pass condition. Require the executor to read the active title after each close, and if it is not the expected test tab, navigate to that test tab explicitly before the next close.
- A11, L72, L289, L354, L431-433: revise timings. ZT-00 expected 60 s to 120 s, ZT-07 expected 240 s to 300 s, ZT-09 expected 240 s to 300 s, and total expected about 30 minutes to about 35 minutes with the maximum raised from 60 to 75 minutes, or state that reporting time sits outside the 60 minute cap.

### Safety

- S1, every Ctrl+W step (notably L90-91, L180-181, L379-381, L415-416): add a mandatory pre-close check before EVERY Ctrl+W. The DOM active title must equal the expected test-tab title named in that step. If it does not match, STOP, do not press Ctrl+W, and report. In ZT-09 step 9, check before each of the three presses, not once at the end.
- S2, L27-29 and each scenario end: replace count-only cleanup with identity cleanup. At the start of the run, record the full tab list (title and URL for every tab) with `zen_dom.py list` and save it. After each scenario, compare the list by identity, not just by count.
- S3, L22-26: replace the "include" list with the rule that any tab in the start-of-run snapshot is protected, with the named tabs kept only as examples. Note that the snapshot must be refreshed if F3 changed the tab set before the run.
- S4, L194-210, ZT-04: add a pre-check before step 2. If example.com is already bookmarked (star filled, or present in the library), STOP the scenario and report it, do not proceed to delete in step 7. In step 7, verify the exact title AND URL of the selected row before deleting, and re-check the library after.
- S5, L267 and L277-278, ZT-06: add a guard. If `~/Downloads/dummy.pdf` already exists in the step 3 listing, STOP the scenario, do not download over it and do not rm it in step 7. Step 7 may rm only a file the step 5 check proves this run downloaded.
- S6, L370-371 and L404-414, ZT-09 step 5 and ZT-10 steps 4-6: if the sidebar shows icons only with no tab rows (the F-001 state), record F-001 and skip the sidebar click step. Do not click at a guessed row position, because that can close a neighbouring owner's tab.
- S7, L93-95, ZT-00 fail path: if the gate fails after step 4 opened a tab, close that tab under the S1 pre-close check before stopping, so a failed gate leaves Zen exactly as found.
- S8, L225-227, ZT-05: if an example.com tab is already open among the owner's tabs, do not open a duplicate and do not close it at the end. Track the opened tab by its title and URL, and close only that tab.

## What passes this review

- URLs and most expected strings are exact and checkable (Example Domain, Ho Chi Minh City, Test User, 0123456789, medium).
- No login is needed anywhere, and no real personal data is submitted.
- The composite rule (L19-21) holds: every scenario does use DOM, CLI, mouse, and keyboard.
- The health gate first (L33-34, L72) and the one-runner rule (L35-36) are correct and should stay.
- F-001 and F-002 are correctly tied to the scenarios that re-test them (ZT-10 and ZT-01 for F-001, ZT-05 for F-002).
