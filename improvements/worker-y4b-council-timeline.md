# Council Member C: timeline and decisive experiment (hidden-body root cause)

Role: timeline and decisive experiment. Read-only work only. No Zen driving. No experiment run.

## Verdict first

The two incidents share one symptom and one scope, but they do not share a proven trigger. No ON flip was observed in either incident, and the two OFF flips have different candidate causes and neither is proven. The only causal story that fits all timestamps is narrow: a per-document state, set at document start in newly opened tabs, that persisted for minutes and then stopped applying to new documents. Whether the old hidden documents ever cleared is unknown in both incidents, because clearing was verified only on new tabs. That single gap keeps every trigger theory alive and prevents any of them from being eliminated.

What the timeline does decide:

- The stale geckodriver kill is correlated with incident 1 clearing and is not necessary for clearing, because incident 2 cleared with no kill. It cannot be the general cause.
- Tab activation in its tested form failed in both incidents. `window.focus()` did not un-hide a hidden tab in incident 1 or in incident 2. Switch away and back was never tested on a still hidden tab, so that form remains open, not proven and not refuted.
- The ON flip for incident 2 sits in a 54 minute unlogged gap (16:58 to 17:52). Any theory of what turned it on is guessing until that gap is explained or the state is reproduced under capture.
- The Transparent Zen mechanism (tz-hidden added at document start, removed about 500 ms after the async chain calls removeLoadingScreen) is the only proposed mechanism that produces exactly the observed symptom. But the discriminating evidence, documentElement classList during the hidden state, was never saved in incident 1 and never collected in incident 2. V1 versus V2 is therefore undecided, and the experiment below is built to settle exactly that.

Sources: worker-y4b-evidence-pack.md; worker-r-test-run-log.md lines 55-110; worker-y4-run-log.md; worker-u-test-run-log.md; probe_q05e.py, probe_y4b.py, probe_y4c.py, probe_y4d.py; run_fcck.py (tab method and WD port).

## Part 1: reconciled minute-by-minute timeline

Labels used below: PROVEN means a log or a saved output shows it. CORRELATED means the timing fits but another change happened at the same time, or the observation is indirect. UNKNOWN means no log or output covers it.

All times Asia/Ho_Chi_Minh, 2026-11-21. Zen PID 27958 alive since 15:31 through both incidents. Marionette port 2828 throughout.

### Incident 1: 16:34 to 16:47 (Worker R, agy-q run, WD_PORT 4446)

| Time | Event | Status |
|---|---|---|
| 16:34 | q05 passes in the full run. State normal. | PROVEN (pass logged) |
| 16:34-16:36 | ON flip. State changes from normal to hidden-body in new tabs. No logged event in this window. No trigger observed. | UNKNOWN cause; flip itself PROVEN by the pass then fail pair |
| 16:36:05-16:36:08 | Solo q05 re-run 1 fails at first interaction: HTTP 400 "could not be scrolled into view", body innerText empty. | PROVEN |
| 16:36:56-16:36:59 | Solo q05 re-run 2 fails the same way. | PROVEN |
| 16:37-16:41 | Probes q05 to q05e. New tab: body computed visibility hidden, inherited through the tree, html visible, readyState complete, DOM present (19,472 bytes), rect non-zero, persists past 5 s and past `window.focus()`. Pre-existing user tab (muse.ai) renders normally at the same time (body visible, innerText 10,883 chars). Only Marionette opened tabs affected. | PROVEN (symptom); focus failure PROVEN |
| 16:37-16:41 | Probe q05e source hunt: reported no inline style, no class, no matching stylesheet rule; fixture contains zero occurrences of "visibility". Note: probe_q05e.py did capture `document.documentElement.className` as htmlClass, but the probe output itself was not saved to disk. Only R's summary ("no class") survives. The exact htmlClass value is therefore UNVERIFIED, not proven empty. | CORRELATED summary; exact value UNKNOWN |
| 16:42 | Probe6 (q05f, override test) first attempt: POST /session times out after 30 s. Orphaned geckodriver PID 113280 found listening on port 4446, parent python long gone. Killed by PID. | PROVEN (timeout, PID, port, kill) |
| 16:44 | pgrep confirms geckodriver gone. | PROVEN |
| 16:44-16:45 | OFF flip window. No other logged change in this window except the kill plus a new session plus a new tab. | CORRELATED with kill; causation UNKNOWN |
| 16:45 | Probe6 retry on a NEW tab: body visible, innerText 677 chars, click and type work. No override was ever applied (the override test timed out before running against a hidden tab). | PROVEN (new tab visible); old hidden tabs never re-checked, UNKNOWN whether they cleared |
| 16:46:26-16:46:30 | q05 final run PASSES, 4,041 ms, zero failures. | PROVEN |
| 16:47 | Cleanup verified: no geckodriver left, no runner processes, port 8766 free, test tabs closed. | PROVEN |

Incident 1 ON window: 2 minutes, 16:34 to 16:36, with no observed trigger.
Incident 1 OFF window: about 1 minute, 16:44 to 16:45, with the kill as the only recorded change.

### The gap between incidents: 16:47 to 17:52 (Worker U, fcc-k run)

| Time | Event | Status |
|---|---|---|
| 16:49 | Worker U starts. Reads R's report. Fixes q04 fixture bug. | PROVEN |
| 16:56 | q04 smoke run on live Zen: PASS, 4,172 ms. Uses `d.new_tab(url)` per test (run_fcck.py). | PROVEN |
| 16:56-16:58 | Full batch: 11/11 PASS, 383 steps, 0 failed steps, total 32,731 ms. WD_PORT 4447. No hidden-body incident, no stale geckodriver, no user tab touched. | PROVEN (state normal at 16:58) |
| 16:58-17:52 | 54 minutes with no runner log and no recorded event. Zen still PID 27958. | UNKNOWN (the whole ON window for incident 2) |

This gap matters more than it looks. U's run used `window/new` tabs, the same tab creation path as the incidents, and passed 11/11. So `window/new` by itself does not cause the hidden state. Something changed between 16:58 and 17:52, and nothing in the record says what. Any ON theory for incident 2 must explain a clean 11/11 run at 16:58 followed by a 0/2 failure at 17:52 with no logged change in between.

### Incident 2: 17:52 to 18:05 (Worker Y4, agy-q2 run, WD_PORT 4448)

| Time | Event | Status |
|---|---|---|
| 17:52 | Files shipped, run launched detached (PID 175805). First run fails 0/2 and aborts. q01 and q02 both body visible=False, then "element not interactable / could not be scrolled into view". ON state already present at first test. The abort itself was a Y4 runner bug (abort heuristic counted any error containing "session"; every WebDriver error URL contains "/session/..."). Fixed later in 03307cd. | PROVEN (failure); onset UNKNOWN within 16:58-17:52 |
| 17:52 | Y4 pre-run checks: Zen alive, geckodriver present, lock free, no other runner active. Y4 did NOT check for stale geckodriver PIDs. Stale geckodriver status at 17:52 is therefore unknown. | UNKNOWN |
| 17:53-18:00 | Diagnosis probes y4, y4b, y4c, y4d. Hidden state persists across probes. | PROVEN |
| 17:53 | Probe y4: body computed visibility hidden on new tabs, rect non-zero, display block, hasFocus true, visibilityState visible. | PROVEN |
| 17:57 (HTTP log 17:57:03) | Probe y4b: all 22 pre-existing tabs visible; new test tab hidden; `window.focus()` plus 2 s does not fix it; click after focus fails. | PROVEN (focus failure, second incident) |
| 17:50-18:02 | Hyprland journal shows no Hyprland errors in this window. One xdg-desktop-portal-gtk ScreenSaver dbus error at 17:58:13. | PROVEN (journal) |
| 17:53-18:00 | Hyprland IPC socket unresponsive the whole probe window: `hyprctl version/monitors/clients` and direct socat to `.socket.sock` hang until timeout. Zen alive, Marionette fine. One user tab has an open alert (tab [4], "unexpected alert open" on eval), never touched. | PROVEN (IPC unresponsive during window); wedge onset and wedge end UNKNOWN |
| 17:59:13-18:00:08 | Owner's physical keyboard and mouse stop responding, about 1 minute, self-recovered. Y4 pauses tab driving. Note the onset: 17:59:13 PREDATES probe_y4c's navigations (HTTP log 17:59:27 and 17:59:33). The freeze cannot have been caused by y4c's navigations. | PROVEN (freeze window); cause UNKNOWN |
| 17:59 (HTTP 17:59:27, 17:59:33) | Probe y4c: new tab to q02 fixture hidden; new tab to example.com hidden; navigating a PRE-EXISTING about:blank tab to q01 fixture gives VISIBLE body, click OK, type OK. Note: probe_y4c.py captures inline visibility only, not htmlClass, not opacity, not transition state. | PROVEN (new tabs hidden, reused tab visible); htmlClass UNKNOWN |
| 17:59-18:00 | OFF flip window, between the y4c click in the reused tab and the y4d fresh tab. Y4 log says cleared "right after a real click in the reused tab". The click is the last recorded intervention before the clear. | CORRELATED with the reused-tab click; causation UNKNOWN |
| 18:00 | Probe y4d: fresh new tab visible from the start; switch away and back keeps it visible; click OK. Correction to the record: probe_y4d.py was DESIGNED to test switch away and back on a hidden tab, but its fresh tab was visible from the start, so it never tested un-hiding a hidden tab. It proves only that a visible tab stays visible across a switch. | PROVEN (new tab visible); switch as a fix UNTESTED on a hidden tab |
| 18:01 | Pause order from parent. Rerun prepared but not launched. | PROVEN |
| 18:05 | No geckodriver process running at check. Y4 performed no kill. | PROVEN (absence at 18:05); says nothing about 17:52 |

Incident 2 ON window: 54 minutes, 16:58 to 17:52, unlogged.
Incident 2 OFF window: about 1 minute, 17:59 to 18:00, with the reused-tab click as the last recorded intervention and the owner freeze overlapping it.

### One causal story, stated as far as the evidence allows

1. A condition turns ON at some point in a short window (2 minutes in incident 1, 54 minutes in incident 2). While ON, every newly opened Marionette tab gets a hidden body. Pre-existing tabs are unaffected, because their documents were created before the condition turned on.
2. The per-document character is the strongest structural clue. The reused about:blank tab in incident 2 rendered the same fixture URL visibly while fresh tabs to the same URL were hidden at the same minute. The difference is not the URL, not the content, not localhost, not the fixture. It is how and when the document was created. That points at something that runs at document start in new documents, which is exactly where Transparent Zen adds tz-hidden, and not at page content or author CSS.
3. The condition turns OFF in about a minute in both incidents. After it turns off, new documents render normally. Whether old hidden documents also recover is unknown in both incidents, because nobody re-checked them.
4. The two ON flips and the two OFF flips have no shared observed trigger. Incident 1 OFF follows a geckodriver kill. Incident 2 OFF follows a real click in a reused tab, with no kill. Either the two incidents have different OFF triggers, or the shared OFF trigger is something unlogged that happened to coincide with the kill in incident 1 and with the click in incident 2 (for example, time passing, extension background recovery, or a compositor event). The timeline cannot distinguish these. That is the central open fact, and the experiment in Part 4 is designed to close it.

## Part 2: trigger analysis

Each trigger is judged separately as an ON trigger and as an OFF trigger, against timestamps only.

### Stale geckodriver kill

- Incident 1 OFF: SUPPORTS, weakly. Sequence fits: timeout at 16:42, kill, pgrep clear at 16:44, visible new tab at 16:45. It is the only recorded change in the OFF window. But it is correlation only: the kill coincided with a new session and a new tab, so session state, tab state, and time passing are all confounded with it. No mechanism is in evidence for how an orphaned geckodriver on port 4446 would set body visibility hidden in new tabs. R's own note says correlation, not proven causation.
- Incident 1 ON: CONTRADICTS as an explanation, or at best UNKNOWN. For the kill theory to explain the ON flip, the orphan must have appeared before 16:36. No timestamp exists for when PID 113280 was orphaned, and no `__enter__` raise (the known orphan path in the WD class) is logged in the 16:34 to 16:36 window.
- Incident 2 OFF: CONTRADICTS as a necessary cause. The state cleared with no kill performed. Y4 checked at 18:05 and found no geckodriver running, but that does not show a kill happened, and no kill is logged. A theory that requires a kill to clear cannot explain incident 2.
- Incident 2 ON: UNKNOWN. Y4 did not check for stale PIDs before the run, so a stale geckodriver may or may not have been present at 17:52. Its absence at 18:05 does not prove absence at 17:52.
- Verdict: a correlated OFF event in one incident, refuted as the general OFF cause by the other incident, and unsupported as an ON cause in either.

### Hyprland IPC wedge clearing

- Incident 2 ON: UNKNOWN. IPC was unresponsive through the whole probe window (17:53 to 18:00), but there is no timestamp for when the wedge started. It may have started before 17:52, during the 54 minute gap, or only during the probes. The journal shows no Hyprland errors 17:50 to 18:02, which gives no onset time.
- Incident 2 OFF: UNKNOWN, leaning against. No successful hyprctl call after 17:59 is recorded, so there is no evidence the wedge cleared at 17:59 to 18:00. The IPC state could not be re-verified from SSH afterward (no instance signature found under /run/user/1000/hyprland/). A clearing that was never observed cannot be credited with causing the OFF flip.
- Incident 1: UNKNOWN. No IPC check is recorded at all in incident 1, so the wedge theory has no cross-incident support and no cross-incident test.
- Verdict: timing supports neither ON nor OFF. The wedge is a real concurrent anomaly in incident 2, but its onset and end are both unobserved, so it cannot be tied to either flip. It also has no stated mechanism linking a Hyprland IPC hang to a CSS visibility value in a Firefox tab, which would be needed before it outranks the extension mechanism that does have one.

### Real click in the reused tab

- Incident 2 OFF: SUPPORTS, weakly. Sequence fits: y4c navigates the reused about:blank tab to q01, click OK and type OK succeed, then y4d at 18:00 finds a fresh new tab visible. The click is the last recorded intervention before the clear. But the click happened in a DIFFERENT tab from the hidden ones. Under V1 (class stuck per document), a click in another tab should not unstick the extension chain in a new tab. Under V2 (global refresh stall), a real click could in principle restart painting, but the tested activations (`window.focus()`, switch away and back on a visible tab) did not produce that effect, so a click theory must explain why a real click works where focus and switch did not. Time passing and the owner freeze are confounded with the click in the same minute.
- Incident 1 OFF: CONTRADICTS as a general cause. No reused-tab click is recorded before the 16:45 clear. The clear followed the kill and a new session instead.
- ON side: not applicable as an ON trigger in either incident. No click precedes either ON flip in the logs.
- Verdict: a correlated OFF event in incident 2 only, with a missing cross-tab mechanism and two confounds in the same minute. It is the best timestamped OFF candidate for incident 2 and it does not generalize.

### User sitting down at 17:59

- Incident 2 OFF: CORRELATED at best, mechanism UNKNOWN. The owner freeze (keyboard and mouse unresponsive 17:59:13 to 18:00:08) overlaps the OFF window (17:59 to 18:00). If the owner sat down, moved the mouse, or changed focus in that minute, that activity could in principle have triggered a repaint (V2) or woken a stalled compositor. But no log records what the owner did, or when the user sat down. The only timed fact is the freeze, and the freeze is an input failure, not an action. Its onset at 17:59:13 predates y4c's navigations at 17:59:27 and 17:59:33, so the freeze is not an effect of y4c. Whether it is an effect of y4b (17:57) is also weak, with a two minute gap.
- Incident 1 OFF: UNKNOWN. No owner activity is recorded around 16:44 to 16:45, so there is no cross-check.
- ON side: no evidence in either incident that owner presence or absence turned the state on. The owner was presumably away or inactive during both ON windows, but that is not logged, and U's clean run at 16:58 happened under presumably similar conditions.
- Verdict: the freeze is a real timed event overlapping the OFF flip, but it is not evidence of a sit-down action, and it cannot be credited as the OFF cause. It is also a safety signal: tab driving while the owner is at the keyboard caused a one minute input freeze, which is why the decisive experiment must run only when the user is away.

### Extension background recovery

- This is the V1 OFF mechanism: the extension background process, or the async chain (fetch of ContentScripts.json, then `browser.storage.local.get`), stalls, tz-hidden stays on, then the background recovers or the chain settles, and new documents render normally.
- Incident 1 OFF: timing COMPATIBLE but unobserved. A background recovery at about 16:44 would fit the OFF window, but no extension log, background state, or settings read was collected, so there is no recovery timestamp. It coincides with the geckodriver kill, and the two cannot be separated from the record.
- Incident 2 OFF: timing COMPATIBLE but unobserved, same problem. A recovery at about 17:59 would fit, but no evidence of a recovery event exists.
- ON side, both incidents: COMPATIBLE but unobserved. A background stall starting in 16:34 to 16:36, and again in 16:58 to 17:52, would fit both ON windows. But no stall timestamp exists for either, and the extension settings (`enableTransparency`, `lightweightTransparency`) were never read, so it is unknown which branch of the chain even ran.
- Verdict: the only trigger theory with a precise mechanism for the symptom, and the least timestamped of all. It is neither supported nor contradicted by any timestamp, because the timestamps that would decide it were never collected. That is what the experiment must fix.

### Tab activation and repaint

- Tested form, OFF: CONTRADICTED in both incidents. Incident 1: `window.focus()` did not fix a hidden tab, and the state persisted past 5 s. Incident 2 probe_y4b: `window.focus()` plus 2 s did not fix a hidden tab, and the follow-up click failed. Focus is not the fix.
- Switch away and back, OFF: UNTESTED on a hidden tab. Probe_y4d was designed for this, but its fresh tab was visible from the start, so the switch test ran on a visible tab and proved nothing about un-hiding. Incident 1 records no switch test. The evidence pack and the Y4 log both phrase this as "switch away and back did not un-hide", but the probe code and the log's own parenthetical show the test never ran against a hidden tab. This is a correction to the record, not a minor wording point: one of the six triggers is currently judged on a test that did not happen.
- As a V2 global repaint theory: UNKNOWN and under strain. If a repaint anywhere clears hidden tabs globally, focus or switch should have had some chance of doing it, and they did not (focus) or were not tested (switch). A real click succeeding where focus failed needs a mechanism, not just a label.
- ON side: the "new tabs in an inactive window" variant is UNSUPPORTED. `document.hasFocus()` was true and `visibilityState` was visible in the hidden tabs, which argues against a background-tab throttle explanation. A 250 ms transition would complete within about a second even at 1 Hz background throttling, so V2 needs refresh ticks to have stopped entirely, not merely throttled. No tick measurement was ever taken.
- Verdict: focus as a fix is refuted twice. Switch as a fix is untested. Repaint as a global mechanism is unproven and must survive the focus failures to be credible.

## Part 3: the "clearing verified only on NEW tabs" caveat

In both incidents, the OFF verification was a new tab under a new session. The old hidden tabs were never re-checked. Incident 1: probe6 retry at 16:45 opened a new tab; the tabs hidden at 16:36 to 16:41 were never evaled again. Incident 2: probe_y4d at 18:00 opened a fresh new tab; the tabs hidden at 17:52 to 17:59 were never evaled again. The reused about:blank tab in y4c is not a re-check of a hidden document: navigating it to q01 reloaded the document and re-ran the extension from document start, so it is a new document in an old tab, with the same confound as a new tab.

What this caveat does to each theory:

- V1 (class stuck): the caveat HELPS V1, or at least does not hurt it. Under V1, tz-hidden is added per document at document start and the removal chain stalls per document. A background recovery would fix new documents and leave old documents hidden, because nothing re-runs the stalled chain in an old document. New-tab-only clearing is exactly what V1 predicts. If the old tabs had been re-checked and found still hidden, V1 would have gained. If they had been found cleared, V1 would have needed an extra mechanism (a later removal firing in old documents) and would have weakened.
- V2 (transition frozen): the caveat HIDES the test that matters most for V2. Under V2, the class is already gone and only the transition is frozen by stopped refresh ticks. When ticks resume, the transition should complete and the OLD tabs should clear, at the same moment as new tabs start working. If old tabs had been re-checked and found cleared together with new tabs, V2 would have gained. If old tabs had stayed hidden while new tabs worked, V2 would have weakened sharply, because a resumed refresh driver should have finished their transitions.
- Stale geckodriver kill: the caveat leaves the theory UNTESTED in the direction that matters. A kill that fixes session or Marionette state predicts new tabs work; it says nothing about old documents, whose CSS state is per document. The kill theory therefore cannot be separated from "time passed and new documents were fine" without a same-tab re-check.
- Real click in reused tab, and Hyprland IPC clearing: the caveat weakens both in the same way as V2. Both are global mechanisms (a repaint, a compositor recovery). A global mechanism should clear old tabs too. New-tab-only verification cannot show that, so both keep their correlation and lose their mechanism test.
- Extension background recovery: same as V1. A recovery predicts new documents work. Whether old documents also clear depends on whether the stalled chain later fires in old documents, which is unknown. The caveat preserves the theory without testing it.
- Tab activation and repaint: same as V2. A repaint theory lives or dies on whether the OLD tab repaints. Never re-checking it means the theory was never tested where it counts.

The re-check that would have settled it, in both incidents, costs one eval per old tab and no navigation:

1. Before opening any new tab, re-eval each still open hidden tab at the same minute: documentElement classList, body computed visibility and opacity, innerText length.
2. Then open the new tab and eval it the same way.
3. Then re-eval the old tabs again, with timestamps.

That three step comparison splits the theories cleanly. Old tabs stay hidden while new tabs work: V1 gains, V2 and global repaint theories lose. Old tabs clear at the same minute as new tabs work: V2 and global theories gain, V1 loses unless a late removal is also observed. The experiment in Part 4 builds this comparison into every phase, so the mistake is not repeated a third time.

## Part 4: the decisive experiment (design only, do NOT run now)

Do not run this while the owner is at the keyboard. Run it later, when the user is away, under the Zen lock, with every probe output saved to disk with timestamps. The experiment is a capture loop, not a fix attempt. It does not apply overrides, it does not kill anything until Phase 3, and it never navigates, types into, or clicks a user tab. The tab with the open alert (tab [4] in incident 2) is never touched.

### Preconditions

- Owner confirmed away from the keyboard. Abort at once if the user returns.
- Lock held (flock on ~/.cache/agent-computer-use/zen_dom.lock). No other runner active.
- Fixture server up (reuse the persistent server pattern; record port and root).
- Zen PID recorded; Marionette port 2828 confirmed; `hyprctl` attempted with a 10 s timeout and its result (success or hang) logged at each phase.
- Extension state recorded before any change: Transparent Zen 0.9.4 enabled or disabled, and the `enableTransparency` and `lightweightTransparency` settings read from extension storage if reachable. Restore the original state at the end.
- All geckodriver processes recorded before the run: PID, parent PID, listening port, parent alive or dead. This is the stale baseline.
- Every probe writes its full JSON output to a timestamped file under `improvements/` (never print only). R's loss of the q05e output must not repeat.
- Stop rule: if no hidden tab appears after the full Phase 1 and Phase 4 loops, stop and report INCONCLUSIVE, not negative. The state is intermittent. Failing to reproduce it does not refute any theory.

### Capture payload (every eval, every step)

One JS payload, run identically at every capture point, so phases are comparable. Save the raw return plus a wall-clock timestamp (Asia/Ho_Chi_Minh) and a monotonic timestamp.

Fields:

- `htmlClass`: `document.documentElement.className` (full string, not a boolean). This is the V1 versus V2 discriminator. Also `document.documentElement.classList` as an array, so `tz-hidden` and `tz-initialized` are explicit.
- `htmlInline`: `document.documentElement.getAttribute('style')`.
- `bodyClass`, `bodyInline`: body className and style attribute.
- `bodyVis`, `bodyOpacity`: `getComputedStyle(document.body).visibility` and `.opacity`.
- `htmlVis`: `getComputedStyle(document.documentElement).visibility`.
- `transition`: `getComputedStyle(document.body).transitionProperty`, `.transitionDuration`, `.transitionDelay`.
- `matchingRules`: the probe_q05e scan, all sheets, every rule with `style.visibility === 'hidden'` where `document.body.matches(selectorText)`, with sheet href.
- `innerLen`: `document.body.innerText.length`.
- `hasFocus`, `visState`, `readyState`, `url`.
- `rect`: body bounding rect width and height.
- `rafTicks`: refresh tick measurement, see below. This is the V2 discriminator.
- `gecko`: from the shell at the same minute, `ps` output for geckodriver PIDs and parents (not from the page).

Refresh tick measurement (rAF timestamps). Run this JS at each capture point and read the result after a fixed window:

- Start an array `window.__rafLog = []`.
- Call `requestAnimationFrame` in a loop that pushes `performance.now()` into the array on every callback and re-registers itself.
- Wait 5 seconds by wall clock (setTimeout in the driver, not in the page), then read the array: count of ticks, first and last timestamp, largest gap between consecutive timestamps.
- Interpretation is fixed in advance: more than 10 ticks in 5 s means the refresh driver is flowing. Zero ticks in 5 s means ticks have stopped. One to ten ticks, or a largest gap above 5 s, means severely stalled. A background tab throttled to about 1 Hz would still give about 5 ticks in 5 s and would complete a 250 ms transition within about a second of wall time, so throttling alone cannot explain a hidden state lasting minutes. Only zero ticks, or gaps far beyond the transition duration, support V2.

### Phase 0: baseline snapshot (extension enabled, no tabs opened yet)

1. Record Zen PID, Marionette responsiveness (one trivial eval on a pre-existing tab, no navigation), Hyprland IPC result with timeout, geckodriver ps table, extension state.
2. Pick a bootstrap tab: a pre-existing about:blank tab if one exists, else any pre-existing tab already on the test origin. Record its handle and URL. Do not navigate it yet.
3. Open one `window/new` tab to `https://example.com` and capture the full payload at 0 s, 0.5 s, 1 s, 2 s, 5 s. If it is hidden, go to Phase 2 at once on that tab. If visible, close it and proceed to Phase 1.

### Phase 1: reproduction loop, extension ENABLED, window/new tabs

Loop up to 30 iterations, or stop early the moment a hidden tab appears:

1. Open a new tab with `window/new` to `https://example.com` (odd iterations) or to the q01 fixture URL (even iterations). Alternate so a content-specific cause cannot hide behind one URL. `example.com` is the content control: it has no author stylesheet.
2. Capture the full payload at 0 s, 0.5 s, 1 s, 2 s, 5 s after load. Save every capture to disk.
3. If visible at 5 s, close the tab and continue to the next iteration.
4. If hidden at 5 s (body visibility hidden, or opacity 0 with empty innerText), STOP the loop. Do not close the tab. Do not navigate it. Go to Phase 2 on that exact tab.

If 30 iterations pass with no hidden tab, record the run as no reproduction in the enabled arm and go to Phase 4 (disabled arm) anyway, then Phase 5. A no-reproduction result is inconclusive, not a pass.

### Phase 2: frozen-state capture on the SAME hidden tab (the decisive phase)

Do the steps in this order, capturing the full payload (including a fresh 5 s rAF window) after each step. Do not navigate the hidden tab at any point in this phase.

1. Wait 10 s with no intervention. Capture. This tests "time alone clears it".
2. `window.focus()`. Wait 2 s. Capture. This retests the focus intervention that failed twice, now with classList and rAF recorded.
3. Switch away to a different pre-existing tab, wait 1 s, switch back to the hidden tab. Wait 2 s. Capture. This is the switch test that never ran on a hidden tab. It runs here, for the first time, with full state.
4. Attempt a Marionette click on a real element in the hidden tab (for example `#tool-rect` on q01). Record success or the exact interactability error. Do not use a JS click as a substitute; the Marionette failure mode is part of the symptom. Capture after the attempt.
5. Open a NEW tab (do not close the hidden tab) to the same URL and capture the full payload on the new tab at 0 s, 1 s, 5 s. Then IMMEDIATELY re-capture the full payload on the OLD hidden tab. This is the old-versus-new comparison from Part 3, and it is the single most important capture in the experiment.
6. Record geckodriver ps and Hyprland IPC result at this minute, with timestamps.

Phase 2 ends with the old tab either still hidden or cleared, and the new tab visible or hidden, both recorded with classList and rAF. That four-way outcome is what separates the hypotheses (see pass and fail criteria below).

### Phase 3: stale geckodriver test (only if Phase 2 ended with a hidden old tab, or with a hidden new tab)

1. Record the full geckodriver ps table: every PID, parent PID, listening port, parent alive or dead. Note any orphan (parent dead, still listening).
2. Close the current WebDriver session cleanly. If an orphaned geckodriver exists, kill that PID only, by PID, and confirm with pgrep. If no orphan exists, record that fact and kill nothing. Do not kill a live session's geckodriver.
3. Start a fresh WebDriver session on a fresh WD port. Re-eval the SAME old hidden tab (attach by window handle, do not navigate it) with the full payload, then open a fresh new tab and capture it the same way.
4. Record which of the two (old tab, new tab) is visible after the kill and fresh session, with timestamps.

This phase separates "the kill fixed it" from "a new session and a new tab fixed it", because the old tab is re-checked after the kill instead of only the new one.

### Phase 4: control arm, extension DISABLED, window/new tabs

1. Disable Transparent Zen in about:addons (toggle off, no restart unless the UI requires one; record whether a restart happened). Confirm the extension is off by checking that a fresh tab has no `tz-hidden` class at document start and no injected `transparent-zen.css` rules. Record the confirmation.
2. Repeat the Phase 1 loop exactly: up to 30 iterations, alternating example.com and the q01 fixture, full payload at 0, 0.5, 1, 2, 5 s, stop early on a hidden tab and go back to Phase 2 capture on that tab.
3. Re-enable Transparent Zen at the end of the phase and confirm the original state is restored.

If the enabled arm reproduced the hidden state and the disabled arm runs 30 iterations with zero reproductions, the extension is implicated. If the disabled arm reproduces it even once with the full hidden symptom, the extension is ruled out as the necessary cause.

### Phase 5: control arm, bootstrap tab versus window/new, extension ENABLED

1. With the extension re-enabled, reuse the Phase 0 bootstrap tab: navigate it to the q01 fixture with `goto`, capture the full payload at 0, 1, 5 s. Repeat 10 times (navigate to about:blank, then back to the fixture, capturing each time).
2. Then run 10 more `window/new` iterations to the same fixture, capturing the same way.
3. Compare reproduction rates. If `window/new` reproduces and bootstrap navigation never does across the same window, the trigger is tied to the new-tab creation path (new document plus new tab plus document start injection), not to the page or the URL. If bootstrap navigation also reproduces, the trigger is tied to document creation generally, and the new-tab scope in the incidents needs re-examination.

### Cleanup

- Close all test tabs opened by the experiment. Return the bootstrap tab to about:blank. Never close a user tab.
- Restore Transparent Zen to its original enabled state. Confirm and log it.
- Confirm no geckodriver processes are left running and no runner processes remain.
- Commit the probe outputs and a run log to the repo.

### Pass and fail criteria per hypothesis

V1 (class stuck: the async chain stalls, tz-hidden stays on):

- PROVEN if all of these hold on the same hidden tab: `htmlClass` contains `tz-hidden` at 5 s and at every later capture while hidden; rAF ticks are flowing (more than 10 ticks in 5 s); body opacity is 0; the disabled arm (Phase 4) runs 30 iterations with zero reproductions; and the old tab stays hidden after new tabs go visible (Phase 2 step 5).
- REFUTED if any hidden tab shows no `tz-hidden` in `htmlClass` at any capture while body visibility is hidden, with the full classList saved to disk. One clean counterexample refutes it, provided the capture ran while the tab was hidden and the output was saved.
- WEAKENED if the old tab clears at the same minute as new tabs work with no late removal observed, or if the disabled arm reproduces the hidden state.

V2 (transition frozen: the class is removed on time, but the visibility transition never advances because refresh ticks stopped):

- PROVEN if all of these hold on the same hidden tab: `htmlClass` does NOT contain `tz-hidden` at any capture while hidden; no matching stylesheet rule and no inline style explain the hidden state; rAF ticks are zero in a 5 s window while hidden (or the largest gap is far beyond the 250 ms transition); and body visibility flips to visible within about 1 s of the first rAF tick resuming, with the old tab clearing at the same moment as new tabs.
- REFUTED if any hidden tab shows rAF ticks flowing normally (more than 10 in 5 s) while body visibility stays hidden, or if the class is present (that is V1, not V2), or if the tab stays hidden after rAF ticks resume.
- WEAKENED if the old tab stays hidden while new tabs work after ticks resume, or if ticks are merely throttled (about 5 in 5 s) rather than stopped.

Stale geckodriver (an orphaned geckodriver causes the hidden state, killing it clears it):

- PROVEN if all of these hold: the hidden state appears only on iterations where an orphaned geckodriver (parent dead, still listening on a WD port) is present in the Phase 0 or Phase 3 ps table; killing that PID, with no extension change and no click, makes a NEW tab visible; and the SAME old tab is re-checked after the kill and its state is recorded (stays hidden or clears, either is informative as long as it is recorded). Two such kill and clear cycles would be stronger than one.
- REFUTED if any of these hold: the hidden state appears with zero orphaned geckodriver processes (all PIDs have live parents and ports match live sessions); or new tabs stay hidden after the kill plus a fresh session; or the hidden state clears in Phase 2 with no kill at all (as incident 2 already shows once, which already refutes the kill as a necessary cause; the experiment would confirm or overturn that reading under capture).
- WEAKENED if the kill correlates with a new tab clearing but the old tab is never re-checked, which would repeat the Part 3 caveat instead of closing it.

None of the above:

- If a hidden tab appears with the extension disabled, with no orphaned geckodriver, with rAF ticks flowing, and with no `tz-hidden` in `htmlClass`, then V1, V2, and stale geckodriver are all out at once. Record the full payload, the ps table, and the IPC result, and treat the cause as unknown with a complete capture. That outcome is a success for the experiment (it eliminates three theories cleanly) even though it leaves the cause open.

### The exact observations that decide it

- V1 versus V2 is decided by two fields on the SAME hidden tab at the SAME minute: `htmlClass` (contains `tz-hidden` or not) and `rafTicks` (flowing or zero). No other evidence substitutes for that pair, and no earlier probe collected both.
- Stale geckodriver is decided by the Phase 3 pair: the ps table showing an orphan before the kill, and the old tab re-check after the kill.
- The old-versus-new question is decided by Phase 2 step 5: the old tab and the new tab captured back to back, with classList and rAF on both.

## What would change my mind

- A saved probe output showing `htmlClass` empty during a hidden tab in incident 1 would weaken V1 for that incident. No such output exists, only a summary, so I do not count it.
- A single hidden tab with `tz-hidden` present and rAF flowing would prove V1 for that tab and would end the V1 versus V2 debate for the mechanism, even if the ON trigger stayed unknown.
- A single hidden tab with no `tz-hidden`, no matching rule, and zero rAF ticks for 5 s, clearing within a second of ticks resuming, would prove V2 for that tab.
- A reproduction with the extension disabled would remove Transparent Zen as the necessary cause entirely, and would force the investigation back to the compositor, the IPC wedge, or an unexamined content script.
- A reproduction with zero orphaned geckodriver processes would remove the stale driver theory as a necessary cause, and incident 2 already points that way.

## Limits of this paper

- The 54 minute gap (16:58 to 17:52) is unobserved. Nothing in this paper explains what happened in it, and no trigger theory should claim to.
- The freeze at 17:59:13 is timed but unexplained. I do not attribute it to y4b, y4c, or the owner sitting down, because the timestamps fit none of those cleanly.
- The Hyprland IPC wedge is a real concurrent anomaly with no onset, no end, and no mechanism linking it to CSS visibility. I keep it as an open correlate, not a cause.
- The switch away and back test never ran on a hidden tab. Any paper that cites it as a failed fix is citing a test that did not happen. The experiment above runs it properly, in Phase 2 step 3.
