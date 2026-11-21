# Redteam review: Worker F3 Marionette slot fix

Verdict: BLOCK

Reviewer: Redteam (subagent of F3). Date: 23:07 21/11/2026 (+07).
Scope: worker-f3-marionette-slot-log.md (HEAD 6fb966f), error file entries J3, J22, J23, J24, source copies driver.sys.mjs-FIREFOX_160_0_RELEASE and TabManager.sys.mjs-FIREFOX_160_0_RELEASE, screenshots zen-ws1-20261121.jpg, after-welcome-click-20261121.jpg, after-example-click-20261121.jpg, after-example-close-20261121.jpg.

What is strong, stated plainly. Claim 1 is source-proven: I checked the lines myself. Line 4616 dereferences browserElement.namespaceURI with no null check, line 4640 passes getBrowserForTab(tab) unchecked, line 2707 loops every window and tab with registerBrowsers true, TabManager lines 39-41 return null when linkedBrowser is null. The file is 4,794 lines, matching F3. The wedge window is tight: verify OK 22:55:34, fail 22:56:12, only close3 in between. cleanup_full closing 52 tabs with the next session working is a genuine control against DELETE per se. Four retries over 6 minutes rule out transient. Restart fixing the first wedge in 0.1s at 22:37:32 is strong.

The blockers below are material. Each needs its stated fix or test before the zombie theory and the procedure change are accepted.

## Blockers

### B1. The zombie's key premise is unrecorded: no example.com in the BiDi tree

Evidence: log 22:58:05 says only "15 tabs, all normal with URLs. NO zombie visible via BiDi" and "1 sacrificial blank remains (index 9)". No URLs, no titles, no context ids are recorded anywhere in the log, and no output file for the probe exists on the VM. The whole zombie identification rests on a list nobody can re-read. zen_cli.py list_tabs (lines 558-574) can produce that list, but F3 never saved its output.

Fix or test: before any restart, re-run the BiDi tabs command, save the full output to a file, and diff it URL by URL against the 22:55:34 verify list. If an example.com context is present, the zombie theory is dead. If it is absent, the premise becomes checkable.

### B2. The screenshots contradict the zombie reading, and F3 never addresses it

Evidence: zen-ws1-20261121.jpg (observe 22:59:13, three minutes after close3 supposedly deleted the tab) shows the "Example Domain" row selected, the URL bar reading "example.com", and the full Example Domain page rendered in the content area. A tab element with null linkedBrowser has no content to render. F3's log calls this "page rendered" and moves on without explaining how a dead tab renders a page. Second contradiction in the same window: BiDi activate YouTube at 22:58:17 is logged "Activated OK", yet the 22:58:45 window title is still "Example Domain" and the 22:59:13 screenshot still shows Example selected, not YouTube. F3 labels the title "STALE", which assumes the conclusion it is meant to prove. Either the rendered page is a stale retained frame (unproven), or the tab is alive and BiDi missed it, or BiDi activate does not change selection the way F3 assumes.

Fix or test: before restart, test whether the rendered page is live: click a link on it, or scroll it, or run script.evaluate in the Example context through BiDi if one exists. Record the result. Also explain the activate non-effect. Until one of these is done, "dead tab element" is one of two live hypotheses, not a finding.

### B3. The trigger is confounded four ways; close3 does not discriminate between them

Evidence: close3 closed 3 tabs (Example Domain + 2 about:blank) between 22:56:01 and 22:56:05, and the slot wedged by 22:56:12. But the 3 closes differ from cleanup_full's 52 closes in at least four ways F3 never separates: (a) Example was BiDi-navigated, (b) Example was probably the SELECTED tab when deleted while the blanks were background tabs (the log never records which tab was selected during close3), (c) the 2 blanks were created via window/new while cleanup_full's blanks were session-restored, (d) close3 ended with a session DELETE whose current handle is unrecorded (J24 admits session DELETE does not reliably close the current tab). F3 picks (a) with no evidence against (b), (c), or (d). The log also never records the DELETE order, the HTTP responses, or a post-close3 sidebar inventory, so it cannot even show the 2 blanks closed cleanly at the UI level, only that their handles left Marionette's list.

Fix or test: after restart, run one controlled experiment. Create 4 test tabs: BiDi-navigated selected, BiDi-navigated background, window/new blank selected, window/new blank background. Close each via Marionette DELETE one at a time, attempting a fresh Marionette session after each close. The one that wedges the slot names the trigger. Do not adopt a procedure rule before this runs.

### B4. No scripts or logs exist for the recurrence window

Evidence: close3.py, cleanup_full.py, verify_list.py and /tmp/zen_tab_cleanup/full.log are absent from the VM and from the repo. A find across ~/workspace returns no close3.py, no cleanup_full.py, no verify_list.py; only zen_cli.py and zen_dom.py exist. The DELETE order, the DELETE responses, the 52-tab DOOMED list, and the verify URL lists therefore exist only as F3's summaries. The central event sequence of the recurrence is not reproducible or checkable by anyone else.

Fix or test: commit the three scripts plus the raw full.log and verify outputs to the repo (or attach them to the log) before this paper is accepted. No acceptance while the recurrence sequence is summary-only.

### B5. The procedure rule is unexecutable and unproven

Evidence: the rule says "NEVER close a BiDi-navigated tab via Marionette DELETE; close via the UI, or navigate away first" (log open item 4, J3, J22). Cleanup scripts select tabs by URL and title; navigation provenance (BiDi-navigated vs not) is never recorded anywhere, so the scripts cannot follow the rule. "Close via the UI" for a 50-tab cleanup is not a procedure, and F3's own UI close attempt at 23:01:53 misclicked and closed the wrong tab. "Navigate away first" was never tested on any tab. If the true trigger is B3 (b), (c), or (d) instead of (a), the rule also fails to prevent the recurrence.

Fix or test: record provenance per tab in the cleanup scripts, and test navigate-away-then-DELETE on a sacrificial BiDi-navigated tab (with a session attempt after) before adopting the rule. Rewrite the rule to name the trigger B3 actually proves.

### B6. The cleanup verification does not reconcile

Evidence: log 22:54:22 expects 15 real tabs after cleanup_full, but log 22:55:34 verifies 14 real tabs, with no reconciliation of the missing one. Log 22:55:34 says "VERIFY 17 tabs (incl. 1 sacrificial)" and in the same entry "2 '' about:blank = leftover sacrificial tabs", so the sacrificial count is 1 and 2 at once. The 14-real URL list is never published, so nobody can check it. Reddit is identified only as "Problem loading page" with no URL recorded. Sidebar rows visible in the screenshots, "Biome Finder - Minecraft", "Gamerule keepInventory", "Just a moment...", "ModelArk-Coding-Plan", are not in the 14-list, while Todoist, codeforces, chunkbase, duck.ai, BytePlus from the 14-list appear in no screenshot. The 52-tab DOOMED list was never recorded (B4), so a real tab deleted by a URL predicate could not be detected by a verify that only checks 14 names. The log also admits the restart lost the LMS login tab opened around 22:26, so "all real tabs intact" needs that qualifier.

Fix or test: publish the full URL lists for cleanup_full AFTER and for the 22:55:34 verify, reconcile each entry against the 22:10 keep-list (13 named) plus Reddit, and name every sidebar row's disposition: kept, closed as fixture, or unaccounted for. Until then the "zero fixture tabs, all real tabs intact" claim is a summary, not a verification.

### B7. "Restart is the only proven fix" overclaims: cheap non-restart attempts were never tried

Evidence: F3 tried BiDi activate on a real tab, a mouse click on a real tab, and one UI X-close that misclicked (23:01:53), then stopped UI attempts for misclick risk and declared restart the only fix. Never tried: (a) Ctrl+W with the zombie row selected, it was visibly selected at 22:59:13, (b) right-click context menu Close Tab on the zombie row, (c) BiDi browsingContext.close on the Example context if one exists, which depends on B1, (d) closing the whole Zen window holding the zombie, since newSession iterates all windows and removing the window removes its tabs. Any of these costs seconds and could save a restart and its unflushed-session loss.

Fix or test: try (a) through (d) in that order before restart, log each result. Only if all four fail does "restart is the only proven fix" hold for this recurrence.

## Amends

A1. Claim 1 is strong but incomplete as a fix target. The window count at failure time was never recorded; a null tab in a second window would throw identically, and F3 inspected only the ws1 sidebar. Also #registerBrowser has a second unchecked caller, line 3543 in switchToWindow passing tabBrowser.selectedBrowser, which the paper never addresses. And the step "removeTab sets linkedBrowser to null" is cited from stock Firefox Bug 1342723, not shown in Zen's tabbrowser code; Zen's vertical-tab and workspace overrides could behave differently.

A2. "Same stack (4616/4640/2707)" for the 22:56 recurrence is asserted, but no stack text is recorded for any of the four failures (22:56:12, 22:56:31, 23:00:24, 23:02:04). Only the HTTP 500 message is recorded.

A3. The first wedge trigger (22:03 to 22:06) is still unproven by F3's own admission in the log ("The 22:03 to 22:06 change trigger is still unproven"). The recurrence theory must not be read back as the explanation for the first wedge.

A4. The 23:01:10 Example-row click used coordinates from a screenshot about 67 seconds old. F3's own X-click 43 seconds later misclicked by a full row after the rows shifted, so a one-row shift at 23:01:10 is unlikely but not excluded by evidence. A fresh screenshot immediately before the click would have closed this.

A5. Restart is proven for the first wedge (22:37), not yet for this recurrence. Same error and same asserted stack make it likely, but the wording should say that until the restart after the recurrence is actually done.

A6. J3 and J22 in the error file already state the zombie theory as fact ("Zombie da xac dinh") and the procedure rule as a lesson, before council and redteam. Downgrade both to hypothesis until B1 through B3 are closed.

## What F3 should do next, in order

1. Before any restart, save the BiDi tab list and test whether the rendered Example page is live (B1, B2).
2. Try Ctrl+W, right-click Close Tab, BiDi close, then window close (B7).
3. Commit the scripts and raw logs (B4).
4. After restart, run the 4-tab trigger experiment (B3), then rewrite the procedure rule from its result (B5).
5. Publish the full verify URL lists and reconcile the real-tab inventory (B6).
