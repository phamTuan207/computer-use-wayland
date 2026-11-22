# Council Voice 2 verdict: Worker F3 Marionette slot fix (procedure + safety)

Verdict: AMEND

The direction is sound as a precaution, but the procedure change as written states an unproven cause as fact, prescribes a fallback that misfired in this same run, and accepts a leak that feeds the next recurrence. The corrections below are mandatory before the rule is recorded as procedure.

## Answers to the three questions

1. The proposed change (never DELETE a BiDi-navigated tab via Marionette) is NOT proven correct, and NOT sufficient. It would have prevented this recurrence only if the BiDi-navigation hypothesis is the true cause, and this run cannot show that.
2. "Accept 1 leftover empty tab" is the wrong tradeoff. There is a cleaner teardown, and the leak must be closed, not accepted.
3. Click risk was managed AFTER the owner ban, not before. The X misclick proves the guard gap. A fresh-observe plus select-then-close guard is required.

## Findings

### F1. The BiDi-navigation cause is UNPROVEN, n=1, confounded (BLOCKS the rule as written)

Evidence: close3 closed 3 tabs in one run at 22:56:01, Example Domain plus 2 about:blank sacrificial tabs (log 22:56:01). The wedge appeared by 22:56:12. F3's own first hypothesis (log 22:56) blamed window/new-created tabs; J22 blames the Example Domain tab instead. One run with 3 tabs closed cannot distinguish the two causes.

Counter-evidence to the broad form of the rule: cleanup_full DELETE-closed the BiDi fixture 40301 tab first (log 22:54:22) and the next session worked (verify 22:55:34, 17 tabs listed). A DELETE of a BiDi-associated tab did not wedge the slot there. This weakens the broad claim, though it does not refute the narrow form (a tab navigated by BiDi in the current Zen lifetime, as opposed to a restored tab).

Correction: J3 and J22 must record the BiDi-navigation cause as an UNPROVEN HYPOTHESIS, not a fact. The rule below keeps it as a precaution only.

### F2. "Close tabs only via the UI" is unsafe at bulk scale, and it misfired in this run

Evidence: the X click at 23:01:53 closed the wrong tab (the sacrificial New Tab, not the zombie) because the rows had shifted between the screenshot and the click (log 23:01:53). F3 then correctly stopped UI-close attempts, citing rising misclick risk near real tabs. Closing 52 tabs by UI clicks would be 52 stale-screenshot gambles next to real tabs.

Correction: NO bulk UI closing. The preferred close path for BiDi-touched tabs is BiDi browsingContext.close via scripts/zen_cli.py close (implemented, lines 926-948, with a last-tab refusal guard). BiDi never calls Marionette #registerBrowser, and BiDi worked throughout the wedge (getTree 22:58:05, activate 22:58:17). Test BiDi close once on a sacrificial tab before adopting it as standard. A single UI close is allowed only under the guard in F5.

### F3. "Navigate them away first" is untested and has no mechanism

Evidence: no run in the log navigated a tab away and then DELETE-closed it. Nothing in the cited driver source (driver.sys.mjs lines 4608-4645) suggests re-navigation repairs a tab element whose linkedBrowser is null.

Correction: strike it from the rule until a test proves it.

### F4. The sacrificial-tab leak must be closed, not accepted

Evidence: session DELETE left the sacrificial tab alive in 0 of 3 runs in this run (cleanup_full, verify_list, close3). Verify at 22:55:34 found 2 blank tabs; BiDi at 22:58:05 still found 1 sacrificial blank. J24 confirms every verify_list run mints a new sacrificial tab. Blanks accumulate run over run, and the 2 blanks closed by close3 are themselves a candidate wedge cause (F1). Accepting the leak feeds the suspect pool of the very failure being fixed.

The Y4d premise behind the sacrificial tab (DELETE /session closes the current window) is also unproven in this setup: 0 of 3 session DELETEs closed the tab here. Keep the sacrificial focus as cheap insurance, but never rely on session DELETE to remove it.

Correction: teardown is now a BiDi pass. After Marionette session DELETE, open a BiDi session, close any leftover blank sacrificial tabs via browsingContext.close, and verify zero about:blank tabs via BiDi getTree. A verify run must NOT mint a new sacrificial tab; verify read-only via BiDi getTree.

### F5. Click safety: one root cause behind the bar click and the wrong-tab X click, a stale screenshot

Evidence: the 22:41:39 click selected the wrong row (Offline Whiteboard, not the labeled target) because rows had shifted one row versus the 22:38 screenshot. The 22:42:28 rail click hit the system dock, not Zen. The 22:43:15 click at img(15,30) opened the Omarchy launcher menu, which the owner saw, leading to the 22:45 ban on bar clicks and the CLI-first order. The click.py miss guard (refuse if miss over 3px) measures cursor movement accuracy only, not target correctness, so it catches none of these. After the ban, F3 complied: the 23:00:03, 23:01:10 and 23:01:53 clicks were all on Zen tab rows, never on the bar.

Correction (guard, mandatory for any future close click): take a fresh observe in the same step, re-read the row labels from it, select-then-close (click the row, observe it selected, then close it), and never click an X from a stale frame. Never click an X adjacent to real tabs without that fresh observe. The owner 22:45 bar ban stands and is restated in the rule.

### F6. What F3 got right (verified)

Cleanup counts check out: 52 closed in 8.5s with 0 errors (log 22:54:50, cleanup_full.py prints DONE closed N errors N elapsed); verify 22:55:34 found all 14 real tabs present by URL with zero fixture tabs; close3 closed 3 (log 22:56:01). The zombie identification is solid: Example Domain row visible in the sidebar (observe 22:59:13), absent from the BiDi tree (22:58:05, 15 contexts, no example.com), unselectable by click (23:01:10, fell back to the neighboring tab). Restart is the only proven wedge fix (session created in 0.1s at 22:37:32 after restart; 4 failures 22:56:12 to 23:02:04 after the recurrence). Stopping UI-close attempts after the misclick was correct judgment.

### F7. Minor corrections

Final-state count needs a timestamp: "14 real plus 1 sacrificial" held at the BiDi check 22:58:05, but the 23:01:53 X click closed the sacrificial tab, so the live state after that is 14 real plus the zombie row, 0 sacrificial. Also, click.py getenv has a dead filter (`or True` in the hypr dir glob), so it picks the first long dir name rather than the signature dir. It works now, but it is fragile if several socket dirs exist.

## Revised rule (exact wording, replaces the proposed procedure change)

1. Open one sacrificial tab FIRST via window/new. Exclude its handle from the doomed set. End the Marionette session focused on it. (Unchanged. Cheap insurance under Y4d.)
2. NEVER close a tab via Marionette DELETE if that tab was navigated or created by BiDi in the current Zen lifetime. This is a PRECAUTION, cause UNPROVEN, until the discriminating test below runs. Restored tabs closed by DELETE in cleanup_full (52 tabs, 0 wedge) stay allowed.
3. Close BiDi-touched doomed tabs via BiDi browsingContext.close (scripts/zen_cli.py close), one tab at a time, verifying each close in BiDi getTree. Test it once on a sacrificial tab first.
4. NO bulk UI tab closing. A single UI close is allowed only with a fresh observe in the same step, select-then-close, and never an X click from a stale screenshot. No clicks on the bar, dock, or workspace buttons, ever (owner order 22:45).
5. Teardown: after Marionette session DELETE, open a BiDi session, close any leftover blank sacrificial tabs via browsingContext.close, and verify zero about:blank tabs via BiDi getTree. A verify run must NOT mint a new sacrificial tab.
6. If a newSession fails with browserElement null after any cleanup, STOP. No further Marionette DELETEs, no UI close attempts near real tabs. Restart Zen is the only proven fix, and it needs direction before running.

## Required follow-up (not part of the rule)

Discriminating test for F1: in a controlled run where a restart is already acceptable, close ONE BiDi-navigated sacrificial tab via Marionette DELETE, then probe newSession; separately, close ONE window/new blank via DELETE, then probe newSession. Only this separates the two hypotheses. Do not run it on the live Zen without restart approval.

## Sources read

Worker F3 log (improvements/worker-f3-marionette-slot-log.md, HEAD 6fb966f at brief time), error file entries J3, J22, J23, J24 (cf26-upload/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md lines 660-667, 733-746), cleanup scripts on the laptop via ssh-laptop.sh (cleanup.py, cleanup2.py, cleanup_full.py, close3.py, verify_list.py, click.py, zen_dom.py), scripts/zen_cli.py close (lines 926-948).
