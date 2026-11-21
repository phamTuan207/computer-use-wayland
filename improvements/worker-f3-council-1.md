# Council Voice 1 (root-cause rigor): verdict on Worker F3 Marionette slot fix

## Verdict: AMEND

The failure mechanism is source-proven and correct. The zombie identification is the best available hypothesis, but it is NOT proven, and the log contradicts itself on the trigger. The trigger claim must be downgraded from "identified" to "prime suspect, unproven" in J3/J22, and the procedure change must be recorded as a precaution, not a proven rule, until the discriminating test in Finding 7 runs.

Scope reviewed: worker-f3-marionette-slot-log.md (full log), error file entries J3, J22, J23, J24, VM source copies driver.sys.mjs-FIREFOX_160_0_RELEASE (4,794 lines) and TabManager.sys.mjs-FIREFOX_160_0_RELEASE (300 lines). All line numbers below were re-checked against the VM copies, not taken from the log.

## Findings

### F1. Source citations VERIFIED, with one off-by-one correction
- driver.sys.mjs line 4616 is exactly `browserElement.namespaceURI != XUL_NS ||` inside `#registerBrowser` (lines 4608-4623). No null check anywhere in that function. Confirmed.
- driver.sys.mjs line 2707 is exactly `this.#registerWindow(win, { registerBrowsers: true });` inside `async newSession(cmd)` (starts line 2616). Confirmed.
- TabManager.sys.mjs lines 39-41 are exactly `getBrowserForTab(tab) { return tab?.linkedBrowser ?? null; }`. Confirmed.
- CORRECTION: the log says "line 4640 passes TabManager.getBrowserForTab(tab) unchecked". The getBrowserForTab call is line 4639; line 4640 is `this.#registerBrowser(contentBrowser);`. The substance is right (the null value flows unchecked into `#registerBrowser` at 4640), but J3 should cite "call at 4639, unchecked pass at 4640".
- Supporting check: TabManager `getBrowsers()` (lines 59-80) does map plus filter nulls, and `#registerWindow` does NOT use it. The log's claim on this point is correct.

### F2. Failure mechanism CORRECT and complete for the 500 error
- At line 4616 the guard order is `!lazy.AppInfo.isFirefox || browserElement.namespaceURI != XUL_NS || ...`. On Firefox `isFirefox` is true, so the first disjunct is false and evaluation reaches `browserElement.namespaceURI`. A null input throws exactly the observed `TypeError: can't access property "namespaceURI", browserElement is null`. One null browser in any window kills the whole newSession, because the loop at 2707 registers every tab of every window. This explains all 9 observed failures (22:06, 22:10, 22:12, 22:20, 22:31, 22:56:12, 22:56:31, 23:00:24, 23:02:04) with a single mechanism.
- The log's corrected theory (22:38) that lazy tabs do NOT break `#registerBrowser` is also correct: the restart at 22:36:48 created a session in 0.1s with about 52 lazy tabs present (log 22:37:32), so lazy tabs have a live linkedBrowser.

### F3. The recurrence window is correctly narrowed, and a transient race is ruled out
- The wedge reappeared between the successful verify at 22:55:34 and the failed verify at 22:56:12. The only tab-closing session in that window is close3 (22:56:01, closed 3 tabs). Failures persisted at 22:56:31, 23:00:24 and 23:02:04, so a removal still in flight is ruled out. Session DELETE alone is also ruled out as the trigger: the verify_list session DELETE at about 22:55 left 2 blank tabs behind, yet the next session at 22:56:01 worked. Credit to F3 for this narrowing. It leaves close3's 3 tab DELETEs as the trigger set.

### F4. MATERIAL HOLE 1: the log holds TWO competing trigger hypotheses and never reconciles them
- At 22:56 the log's refined hypothesis blames the 2 window/new-created sacrificial blanks ("closing a window/new-created tab leaves a zombie tab element"). J22 blames the BiDi-navigated Example Domain tab instead. Both candidates were closed in the SAME close3 run at 22:56:01 by the SAME method, so timing cannot discriminate between them. The log switches hypotheses without a test and without noting the switch. One of the two must be wrong, or both partial. J22 must record both candidates, not only Example Domain.

### F5. MATERIAL HOLE 2: the causal link from Marionette DELETE to a zombie in tabbrowser.tabs is asserted, not proven
- Bug 1342723 is real and verified: its patch diff sets `aTab.linkedBrowser = null` inside removeTab (Bugzilla 1342723, verified by web search 23:0x). But removeTab also removes the tab from the tab list. Nothing in the VM source copies proves a removed tab element STAYS in `tabbrowser.tabs` with a null linkedBrowser. The VM copies do not include tabbrowser.js, so removeTab's list-removal behavior could not be checked here. For the zombie to break newSession, the tab must remain in the iterated list; that step needs a mechanism (Zen custom tab handling, interrupted removal, selected-tab edge case) and evidence. Until then, "DELETE leaves the zombie" is a correlation over one incident, not a proven causal chain.

### F6. The zombie identification is circumstantial, and one observation cuts against it
- Evidence FOR Example Domain as the zombie: sidebar row still visible at 22:59:13 while BiDi's tree at 22:58:05 lists 15 contexts with no example.com; the click at 23:01:10 on the Example Domain row selected the neighboring New Tab instead; the screenshot after-example-click-20261121.jpg confirms this (New Tab row highlighted, cursor on it, content area showing a new-tab page, not Example Domain); the window title stayed stale as "Example Domain, Zen Browser" at 22:58:45.
- Evidence AGAINST, or weakening: (a) BiDi absence is expected for ANY closed tab, so it proves the tab is closed, not that its element lingers in tabbrowser.tabs. (b) The Zen sidebar is custom Zen UI, so a leftover row can be a stale sidebar render rather than a live tab element. (c) Click-based row attribution is weakened by proven row shift: the X-click at 23:01:53 closed the wrong tab (sacrificial New Tab) because rows had shifted between screenshot and click. (d) TENSION: the log at 22:59:13 says the Example Domain row was "selected, page rendered". If linkedBrowser were null and the browser element destroyed, the content area could not render that page. Either the render was stale/cached, which the log does not establish, or the tab still had a live browser and the real zombie is a different tab. This tension is unresolved in the log.
- Net: Example Domain is the prime suspect, but the identification is not proven. The direct test (enumerate tabbrowser.tabs and report any tab with null linkedBrowser, with title/URL) was never run.

### F7. The trigger hypothesis has no mechanism, and the control arms were never run
- Why would BiDi navigation make a Marionette DELETE leave a zombie, when cleanup_full closed 52 tabs by the same DELETE method at 22:54:50 and the next session worked? The log offers no mechanism for the BiDi-navigation distinction. The 2 blanks are an equally live alternative (F4). No control was run.
- What would prove or disprove it (after a restart clears the slot): three arms, each followed by a newSession attempt. Arm A: open a blank via window/new, BiDi-navigate to example.com, close via Marionette DELETE. Arm B: open a blank via window/new, close via Marionette DELETE with NO BiDi navigation. Arm C: open a blank via window/new, BiDi-navigate to example.com, close via UI X-click. If only Arm A wedges the slot, the trigger hypothesis is proven. If Arm B also wedges it, the trigger is window/new plus DELETE, not BiDi navigation. If neither wedges it, the 22:56 incident had a different cause (for example the selected-tab edge case or a Zen sidebar desync) and the procedure change is wrong.
- REQUIRED CORRECTION: until Arm A/B/C run, J3/J22 must say "prime suspect, unproven" and the procedure change ("NEVER close a BiDi-navigated tab via Marionette DELETE") must be labeled a precaution. The "navigate it away first" alternative is likewise untested and must not be recorded as a proven fix.

### F8. Minor: close3 method rests on the log alone
- close3.py, cleanup_full.py and verify_list.py are NOT present on the VM (find over ~/workspace returned nothing), so the claim that close3 closed the 3 tabs via Marionette DELETE /window could not be verified from code. It is consistent with the checked-in pattern: cleanup.py line 83 and cleanup2.py line 68 both use DELETE /session/{id}/window. Treat as log-only evidence, low risk, but note it.

### F9. Minor: Bug 1366988 citation not independently verified
- The log cites Bug 1366988 (2017, same namespaceURI error family). It was not verified in this review and is not load-bearing. Keep the citation but mark it as log-sourced, or verify it before the next revision of J3.

### F10. J23 and J24 are sound as written
- J23 (hl.dispatch takes dispatcher objects only, workspace table has no goto/switch, launcher command `omarchy-menu toggle root` from bindings.lua) matches the log events at 22:50-22:58 and needs no correction.
- J24 (session DELETE does not reliably close the sacrificial tab; verify_list adds 1 blank per run) matches the log counts at 22:55:34 (17 tabs incl. 1 sacrificial) and 22:56:01 (BEFORE 18, AFTER 15). No correction.

## Required corrections (for F3, before this is recorded as proven)
1. Fix the line citation in J3: getBrowserForTab call at driver.sys.mjs 4639, unchecked pass into #registerBrowser at 4640.
2. In J3/J22, downgrade the zombie claim to "prime suspect, unproven" and list BOTH close3 candidates (Example Domain tab AND the 2 window/new blanks). Record the 22:56 hypothesis switch explicitly.
3. Add the unresolved tension to J22: 22:59:13 "page rendered" while selected vs null linkedBrowser.
4. Label the procedure change a precaution, not a proven rule, and schedule the Arm A/B/C discriminating test (F7) as the next step after a restart. Do not record "Marionette DELETE on a BiDi-navigated tab leaves the zombie" as fact until Arm A wedges the slot while Arm B does not.
5. Note in J3 that the removeTab-to-zombie causal link is unproven (tabbrowser.js not in the VM source copies; Bug 1342723 proves the nulling, not the lingering).

## What is NOT in dispute
- The 500 mechanism, the restart fix (22:37:32, 0.1s, 67 tabs), the cleanup verification (52 plus 3 closed, all 14 real tabs present, zero fixture tabs), and the recurrence itself (4 failures) are all sound and well logged.
