# Redteam: attack on the hidden-body leading theory (Worker Y4b)

## Verdict first

The leading theory keeps its suspect and loses both of its variants as established fact. Transparent Zen is still the only examined mechanism that produces exactly this symptom by code, so it survives as prime suspect. V1 (class stuck) is badly wounded but not logically dead, and it survives only because the one observation that would kill it was never saved. V2 (transition frozen) is dead as stated, killed by a CSS rule the pack gets wrong, not by a lack of evidence. The stale-geckodriver link is dead as a common cause. The runner workarounds survive as reasonable harness defense, not as a validated fix, and one of them rests on a false claim about how content scripts work. Worst of all for the council's framing: if R's "no class" summary is accurate, it falsifies BOTH variants, not just V1, so the V1-vs-V2 binary is a false dichotomy and a third mechanism is required.

How this paper was built: read-only. Evidence pack, Y4 run log, R run report lines 115 to 230, R test run log, probe files probe_q05c, probe_q05d, probe_q05e, probe_q05f, probe_y4b, probe_y4c, probe_y4d, run_agyq2.py bootstrap and ensure_visible code, the council mechanism and fix papers, and the css.dev visibility reference. No Zen driving, no tab navigation, no clicks. Every attack below names the exact evidence line that creates the hole. Where the evidence does not decide a point, this paper says so.

## A. Attacks on V1 (class stuck)

### A1. The "summary may be loose" defense is not strong enough

The hole: V1 predicts `document.documentElement.className` contains `tz-hidden` during the hidden state (pack, V1 prediction). R's report says "No inline style, no class, and no stylesheet rule sets it" (RUN-REPORT-AGYQ-20261121.md lines 133-135), and R's log repeats "No inline style, no class, no matching stylesheet rule" (worker-r-test-run-log.md line 73). That is two concordant records, not one loose summary. The probe was built to capture exactly this: probe_q05e.py lines 12-14 collect `bodyClass` and `htmlClass`. A value of `tz-hidden` in `htmlClass` would have been the headline finding of a probe whose whole purpose was "find the source of body visibility:hidden", not something summarized as "no class".

The pack's defense is that the probe output was not saved to disk, so the exact htmlClass value is unverified (pack, note on V1 vs R's finding). That defense saves V1 from logical falsification, and nothing more. It requires R to have misread or mis-summarized his own probe's headline output twice, in two documents written hours apart. The mechanism paper's sub-defense, that "no class" is ambiguous about which element it refers to, does not repair this: the sentence lists three checks (inline style, class, rule) as a summary of the probe's three checks, and htmlClass was the more important of the two class reads. "No class" most naturally covers both. The mechanism paper itself concedes the htmlClass read has no blind spot, which is exactly why R's summary of it, if accurate, is fatal.

Score: V1 is not logically killed, because the raw value is genuinely unsaved. But the defense is weak, and the burden of proof now sits on V1. One saved re-probe during a live incident decides it either way.

### A2. A second, independent V1 prediction is denied by the same summary

The hole: the pack says `initLoadingScreen()` sets the `--zen-logo-path` custom property on documentElement, and `removeLoadingScreen()` removes that property (pack, Transparent Zen JS). A `removeProperty` call only makes sense if the property was set through inline style. Under V1, `removeLoadingScreen()` never ran, so the inline custom property should still be present on the element. Probe_q05e collected `htmlInline` (probe_q05e.py line 15). R reported "no inline style". That is a second V1 prediction denied by the same summary, not just the class.

Caveat, stated honestly: the XPI lives on the laptop, not on this VM, so the inline-style setting is pack-reported and could not be re-verified here. If the property were set some other way, this point evaporates. But on the pack's own description of `removeLoadingScreen`, the inference stands.

### A3. V1 has zero positive sightings of anything it uniquely predicts

The hole: V1 predicts, in addition to the class, computed opacity 0 on body, and visible `:root.tz-hidden:before/after` fixed Zen-logo pulse elements on screen (pack, injected CSS). No probe in either incident ever read opacity: a grep over all probe files finds no `opacity` read at all, and the pack itself notes only that empty innerText is "consistent with visibility hidden, not opacity". No screenshot was taken in either incident, so nobody checked whether a pulsing Zen logo was on screen. No probe saved a `classList.contains("tz-hidden")` result, and incident 2 never collected htmlClass at all.

This is not a falsification. It is a ledger problem: V1's case rests entirely on code fit, with zero observations of any artifact the mechanism uniquely predicts, while its two most checkable predictions (class, inline property) are denied by the only summary that records them. A theory with no positive sightings and two denied predictions is a suspect, not a leading mechanism.

### A4. The reused-tab datum contradicts the global-stall form of V1, and V1 has no tab-creation dependence

The hole: probe_y4c navigated a pre-existing about:blank tab to the q01 fixture and got a visible body with working click and type, while new tabs to the same fixture and to example.com were hidden seconds earlier in the same probe (pack, incident 2; probe_y4c.py lines 40-60). Under V1 the extension chain runs fresh on every document load: a manifest content script with `run_at: document_start` runs on a navigation in an existing tab exactly as it runs on a `window/new` tab. If the chain was stalled at 17:59, the reused navigation should have hidden too.

V1 has two escapes, and both cost it something. Escape one, the stall lifted in the roughly 10 to 20 second gap between the example.com check and the reused-tab check: then the single reused-tab datapoint is a coincidence of timing and proves nothing about tab type, which removes the entire evidence base for the bootstrap workaround (see D3). Escape two, the stall is per-load and random rather than global: then some new-tab loads should have been visible too, but about 6 of 6 new-tab loads hid across the probe windows while 1 of 1 reused navigation did not, a pattern that looks like tab-creation dependence, which V1's mechanism does not provide. Either way V1 needs an auxiliary hypothesis it does not currently have.

Related: the fix paper's rationale for bootstrap is wrong as a mechanism claim. It says "a reused tab is not a fresh `window/new` document, so the extension's `document_start` loading screen path does not run again on it in the same way" (fix paper, section 6). That is false. A navigation in a reused tab creates a new document, and `document_start` content scripts run on it. The fix paper's bootstrap defense therefore rests on a misunderstanding of content-script semantics, and its claim that the reused-tab evidence is "direct positive evidence" inherits the time confound in A4.

### A5. V1 has no clearing mechanism for either incident

The hole: incident 1's clear is attributed by correlation to killing the stale geckodriver, but a geckodriver kill cannot unstick an extension content-script fetch or storage call in already-loaded tabs (see C2). Incident 2's clear is described as happening "right after a real click in the reused tab" (Y4 run log), but a click in a different, already visible tab cannot settle a stalled fetch in the hidden tabs. V1 predicts the hidden tabs stay hidden until their own chain settles or the tab reloads. The record never re-checked an old hidden tab in either incident (pack, clearing caveat), so whether any hidden tab ever cleared is unknown. V1's clear story is therefore not "explained", it is absent.

The stall itself is equally unexplained: no extension background state, no console error, no fetch timing was ever collected. The stall is inferred from the symptom, which is circular: the class is stuck because the chain stalled, and the chain stalled because the class is stuck.

### A6. Untested V1 predictions (not holes, but owed observations)

V1 predicts every new tab opened by any means during the window, including tabs the owner opens with mouse or keyboard, would show the blank loading screen. No such observation exists. V1 also predicts the class would be present on any tab that loaded during the window. Untested. These do not damage V1, but they show how little of V1 was ever put to a test.

## B. Attacks on V2 (transition frozen)

### B1. The killer: V2 predicts the opposite of the measured value

The hole: the pack states V2 as "Computed visibility stays hidden even though the class is gone and no rule matches" (pack, V2 prediction). That statement assumes `visibility` interpolates like `opacity`, frozen at its start value when the transition does not advance. That assumption is wrong.

CSS gives `visibility` a special interpolation rule: during a transition between `visible` and `hidden`, the value stays `visible` for the whole duration if either end is `visible`. The reference states it plainly: "During a transition between `visible` and `hidden`, the value stays `visible` for the whole duration, so it turns on at the start of a fade-in and off at the end of a fade-out" (css.dev visibility page, lines 212-215; same point at lines 74-75: "it turns visible at the start of the fade-in"). Baseline is Firefox 1 and up.

Apply it to V2. The class is removed, so body transitions from hidden to visible under the `:root body { transition: visibility .25s, opacity .25s, ... }` rule (pack, injected CSS). The interpolated visibility is `visible` from the first frame of that transition, at progress 0, whether or not any further refresh tick ever arrives. And `getComputedStyle`, which every probe used to read the value, forces a style flush, which is what starts the transition in the first place. So the first probe eval after class removal must read `visible`. The probes read `hidden` minutes later, across many evals (probe_q05d at t+0, t+5s, and after `window.focus()`; probe_y4b after `window.focus()` plus 2 s). V2 predicts the exact opposite of the measured value for the exact property that was measured.

There is no escape through "the transition never started". If the transition runs, interpolation yields visible. If the transition is suppressed entirely, the computed value is simply the after-change value, which is also visible. The only way computed visibility stays hidden is if a hiding rule is still applying, which is V1 or a third mechanism, not V2. The only escape left is to deny the interpolation rule applies in Gecko, which has no evidence behind it and contradicts the spec and Firefox's baseline behavior since version 1.

Honest caveat: this rests on the spec rule as documented, not on a live Gecko test, and this subagent could not run one (read-only, no browser driving). The decisive live test takes about 30 seconds in any browser: toggle the class, stop advancing frames, read computed visibility. But on the evidence as it stands, V2 is falsified as stated, not merely unproven. Consequence: the mechanism paper treats R's "no class" as V2's only support (mechanism paper, Evidence for V2 item 1). It is V2's refutation too. If R's summary is accurate, BOTH variants are falsified, and the council's binary is a false dichotomy.

### B2. V2 needs refresh ticks to stop entirely for 5+ minutes, and the evidence points the other way

The hole: the pack itself concedes that background tabs tick at about 1 Hz, which would complete a 250 ms transition within about 1 s, so "for V2 to hold 5+ minutes, refresh ticks must STOP entirely, not just throttle" (pack, note on V2's premise). Nothing in the evidence shows a stop. What it shows is an active docshell: `hasFocus` true, `visibilityState` visible, readyState complete, Marionette evals returning promptly throughout both incidents, `window.focus()` executing (probe_y4b.py lines 51-56; probe_q05d). An active, focused tab in a window the owner was using, with a fully stopped refresh driver for 7 minutes, is extraordinary and unevidenced. No probe measured paint ticks, frames, or vsync. The mechanism paper agrees the window was evidently painting (mechanism paper, Evidence against V2 item 2: all 22 pre-existing tabs rendered visible).

Timescale mismatch, incident 2: the hidden state lasted about 7 minutes (17:52 to 17:59) while the only compositor-level symptom in the record, the owner input freeze, lasted about 1 minute (17:59:13 to 18:00:08, pack). A single compositor stall cannot cover both timescales.

### B3. The Hyprland prop for V2 fails on both incidents

The hole: incident 2 is the only incident with any compositor evidence, and it cuts against V2. Hyprland IPC was unresponsive "the whole time" (pack, incident 2 side findings), yet the state cleared around 17:59 while the wedge allegedly persisted. An IPC socket hang is a control-plane symptom, not frame-callback starvation, and the journal shows no Hyprland errors from 17:50 to 18:02 (pack, not fully verified). Incident 1 has no reported Hyprland wedge at all, so V2-via-Hyprland cannot be the common cause; V2 would need a second, unevidenced refresh-stop mechanism for incident 1. The input freeze onset (17:59:13) also slightly predates probe_y4c's navigations (17:59:27, 17:59:33, pack), so the freeze cannot be blamed cleanly on those navigations, and the freeze is the only compositor-level symptom in the record.

### B4. V2's predicted clear was never observed, and the pack mis-cites the probe that supposedly tested it

The hole: the pack's symptom list says "switch-away-and-back does not fix it (Y4 probe d)". That citation is wrong. Probe_y4d's fresh tab was visible from the start (Y4 run log line 20; probe_y4d.py lines 38-47), so the switch-away-and-back recovery was never tested on a hidden tab in incident 2. In incident 1 it was never tested either: probe_q05d's docstring promises "an explicit re-switch", but the code only fetches handles and prints the count (probe_q05d.py lines 40-42). The switch was never executed.

So switch-away-and-back has ZERO observations in either direction, in either incident. The mechanism paper gets this right (mechanism paper, Evidence against V2 item 3: probe_y4d "proves nothing about un-hiding"), but the pack and the fix paper get it wrong: the fix paper repeats "Probe d, switch away and back, did not fix it" (fix paper, section 6) and then uses that non-observation as evidence against its own repaint step (fix paper, section 3 step 3). The claim that repaint "does not fix it" is exactly as unevidenced as the claim that it does. Consequence: `ensure_visible`'s core recovery step is untested, and the fix paper's reasoning about repaint is built on a non-observation in both directions.

### B5. V2's core prediction was never tested in incident 2

The hole: V2 predicts the class is absent during the hidden state. None of the Y4 probes collected htmlClass: probe_y4b's VIS_JS reads body visibility, html visibility, rect, focus, visibility state, and viewport only (probe_y4b.py lines 12-20); probe_y4c adds only inline body visibility (probe_y4c.py lines 12-17); probe_y4d reads only body visibility, focus, and visibility state (probe_y4d.py lines 12-17). V2's only positive evidence is incident 1's unverified summary, which B1 shows actually refutes V2. V2 therefore has zero supporting observations anywhere in the record.

### B6. V2 gets the measured property wrong and the unmeasured one right

The hole: under V2 the page would be invisible-with-computed-visibility-visible (opacity frozen at 0, visibility flipped to visible at transition start). The observed state is the reverse signature: computed visibility hidden. Opacity was never measured in either incident, so the one property V2 predicts correctly (opacity 0) went unmeasured, while the one property anyone measured (visibility hidden) is the one V2 gets wrong. This is a missing discriminator, but the asymmetry is damning: the record's single quantitative style reading contradicts V2 and is consistent with V1 or a third rule.

## C. Attacks on the stale-geckodriver link

### C1. Dead as the common cause

The hole: incident 2 ran on a fresh port, 4448, never used before (R used 4446, P used 4450, default 4445), and no geckodriver process was running at the 18:05 check (pack, incident 2). The incident cleared with no kill. A stale geckodriver cannot be the common cause of both incidents when the second incident had a fresh port, no stale process found, and a clear with no kill.

Honest caveat: Y4's pre-run checks did NOT check for stale geckodriver PIDs (pack, incident 2), and no check ran during 17:52 to 17:59, so a stale process on another port during the incident cannot be strictly excluded. But a stale listener on a different port has no proposed mechanism to affect tabs driven through port 4448, and it would have had to vanish by itself before 18:05. The theory survives only as "an unobserved process on an unobserved port did something by an unproposed mechanism", which is not a theory.

### C2. The incident 1 kill was not shown to be causal

The hole, three ways. First, the clear was verified only on a NEW tab under a NEW session (pack, incident 1; RUN-REPORT lines 143-148). The experiment that would show causality, re-checking an old hidden tab after the kill, was never done. A new tab would be visible under almost any theory of a transient state, including spontaneous resolution. Second, there is no mechanism: a listening TCP socket on port 4446 cannot set CSS visibility in already-loaded tabs. The orphan's demonstrated effect was blocking SESSION CREATION (probe6 POST /session timed out after 30s at 16:42, pack), not rendering. Third, timing: about 8 minutes elapsed between onset (16:36) and the kill (16:42 to 16:44), so spontaneous resolution in that window is equally consistent. R's own note says correlation, not proven causation (pack; RUN-REPORT lines 143-148). The kill proved the orphan blocked session creation (timeout before, success after). It proved nothing about hidden bodies. The two effects were conflated.

### C3. The orphan theory cannot explain the new-tab-only scope

The hole: a wedged Marionette or geckodriver is session-level. It would be expected to affect session operations, not per-tab CSS, and the pre-existing muse.ai tab rendered fine under the same browser and Marionette connection at the same time (RUN-REPORT lines 137-141). Also the orphan's birth time is unknown (parent python "long gone"), so there is no temporal link between the orphan appearing and the state flipping on between 16:34 and 16:36.

Note: the WD orphaning bug itself (session POST timeout orphans the geckodriver because `__exit__` never runs) is real and worth fixing regardless. It is a session-management bug, not a visibility mechanism, and fixing it does not touch the hidden-body question.

## D. Attacks on the fix direction

### D1. The tz-hidden eval removal is proposed, not implemented, and it bakes in V1

The hole: a grep over run_agyq2.py and run_live.py finds no tz-hidden removal; the only classList reads are test selectors. The eval removal exists only as a proposal (fix paper, section 3 step 2). Attacked as proposed: it addresses V1 only. Under V2 the class is already gone, so the eval is a no-op and the test still fails. It bakes V1 in as fact while V1 is the weaker, wounded variant. And per B1, if R's "no class" is accurate, NEITHER variant holds and the eval is doubly useless.

Masking: a real user opening a new tab in this Zen during such a window sees a blank page for minutes. That is a genuine user-facing defect in the owner's daily browser. Removing the class in the runner makes tests green while the owner's browser stays broken. If the incident is then closed as "worked around", the defect is buried. The eval is legitimate ONLY if paired with a separately tracked item to fix or disable the extension AND disclosure in the test report that the harness intervened in page state. The fix paper's flagged-pass logging (r.details tz_intervention) is the right instinct, but a flagged pass still counts as a pass in the suite summary (fix paper, section 1 step 10: "A test that passed only after `removed-tz-hidden` is still a pass"), so the masking risk survives in the headline number.

It also edits the state under test: the loading screen gates the page until the extension finishes setup, so force-removing it tests the fixture in a state no real user sees (extension settings and transparency rules not yet applied). For these fixtures that likely does not matter, but the principle stands. And it does not fix the cause, so the hazard recurs on every reload; with the shared bootstrap tab reloading per test, each test re-runs the extension chain.

### D2. ensure_visible has zero observed conversions

The hole: the rerun never launched, so `ensure_visible` was never run against a hidden tab. Both incidents cleared without it. Its recovery (switch away and back, focus, wait 2 s) rests on steps the probes never validated (see B4). The fix paper admits the current version is a placebo ("Keeping the current body as the recovery would be keeping a placebo that costs 2 s"), but its replacement ladder has the same problem one level down: step 2 (class removal) assumes V1, and step 3 (repaint) is equally unproven and is justified with the mis-cited probe d non-observation (see B4). Per B1, the ladder's TRANSITION_FROZEN_V2 category cannot occur as described (class gone plus computed hidden via a frozen visibility transition). That signature should be reclassified as OTHER_HIDDEN (third mechanism) instead of treated as a live diagnosis with a repaint remedy. The fix paper's section 8 draws the wrong lesson from a future class-absent-plus-hidden observation ("lean harder on the V2 repaint and fallback steps"); the right lesson is to open a third-mechanism investigation.

### D3. The bootstrap tab: n=1 confounded evidence, false mechanism story, isolation holes

The hole, in four parts. First, evidence: the entire "reused tabs avoid it" claim rests on one datapoint (probe_y4c) that is confounded by time (see A4): it ran seconds before the incident cleared, so it is equally explained by "the incident ended at that moment". Incident 1 has zero reused-tab datapoints. Second, mechanism: the fix paper's story for why reuse works is false (see A4): `document_start` content scripts run on navigations in a reused tab too, so under V1 the reused tab should have hidden as well. Third, ownership: `bootstrap_tab` takes the FIRST about:blank tab found (run_agyq2.py, bootstrap_tab), and there were 7 about:blank tabs in the window; an about:blank tab may be a user tab, and the code navigates it with no ownership check, then leaves it at about:blank with polluted history at suite end. The fallback branch, "any tab already on our test origin", could in principle grab a user tab on that origin; the fix paper itself flags that branch as too broad. Fourth, isolation: a shared browsing context shares history, bfcache, service workers, and per-tab extension state across tests. A fresh WebDriver session plus storage clear plus reload covers localStorage and cookies, not all of it; a test that navigates away, opens a popup, or leaves a modal leaks into the next test. And the tab is deliberately kept out of `opened_tabs` and never closed, so a test tab persists in the owner's Zen after the run. Finally, the hazard (if the extension is the cause) triggers per document load, so reloading the fixture in the reused tab re-runs the whole chain: the workaround bets the trigger is `window/new`-specific, which is unproven (A4).

Credit where due: the failure mode is honest (explicit driver-state error, never a fake fixture verdict), and the abort-heuristic fix and the server-reuse fix are genuine runner bugs that survive intact.

### D4. The recovery itself violates the standing no-tab-driving rule

The hole: `ensure_visible` switches to the first non-test handle as its "away" tab (run_agyq2.py, ensure_visible). In a live Zen with 22 pre-existing tabs, that is a user tab by definition. That is a focus steal, and the 17:59 input freeze followed probe tab navigation in the same window; the pause order forbids tab-driving while the owner is at the keyboard. Any recovery that switches tabs by design cannot run while the user is present. The fix paper notes this too and proposes removing the switch-away step, which is correct, but the currently landed code still contains it.

### D5. The fix paper's preflight Hyprland gate and blacklist trial overreach the evidence

The hole: the preflight check "abort if hyprctl hangs" (fix paper, section 4 step 4) treats an unverified correlate as a gate. Incident 1 has no Hyprland evidence, so the check would not have caught incident 1, and it may abort runs for an IPC issue unrelated to rendering. Fail-closed is defensible as a safety gate, but it should be labeled as one, not as an incident detector. The blacklist trial (fix paper, section 7) is worth doing, but its premise is unverified: the settings were never read, so nobody knows whether a per-site disable exists or whether `127.0.0.1` can be added. And if the true cause is not Transparent Zen at all (see section E), the blacklist tests nothing.

## E. The strongest alternative theory

### E1. The blind-scan / hidden-sheet theory (primary alternative)

Statement: the hiding rule lives in a stylesheet the probe could not see, so R's "no matching rule" is an artifact of the probe, not a fact about the page, and no class is needed because the rule is not class-gated. Three carriers, all visible in the probe's own code:

1. A dynamically injected and removed hiding stylesheet. An extension injects a sheet setting body visibility hidden at `document_start` and removes it when ready; if the removal signal never arrives (background wedged, message lost), the sheet stays. This is V1's structure with a different carrier: a sheet instead of a class toggle.
2. A rule nested inside a grouping rule (`@media`, `@supports`, `@layer`, `@container`). Probe_q05e's scan iterates top-level rules only (probe_q05e.py lines 20-28); on a grouping rule `r.style` is undefined, so the nested rules are never visited and the scan silently misses them.
3. A sheet whose `cssRules` throws in page context (cross-origin or extension sheet, SecurityError), silently skipped by the probe's `catch (e) { continue; }` (probe_q05e.py lines 20-28). The mechanism paper already concedes this blind spot for the Transparent Zen sheet (mechanism paper, Evidence against V1 item 1c), but frames it as saving V1; it equally opens the door to a non-TZ sheet.

Candidate owner: Obsidian Web Clipper runs on http and https and was not cleanly grepped, with no loading-screen pattern known (pack, not fully verified). Any other content script with a loading or overlay mechanism qualifies. Transparent Zen is not excluded as the sheet owner, but the theory does not need its class toggle.

Why this is the strongest alternative: it accepts R's "no class" at face value, which V1 cannot do, and it accepts "no matching rule" as a probe limitation, which the probe's code independently shows (carriers 2 and 3 are in the code, not speculative). It explains the new-tab-only scope (injection happens at `document_start` on fresh loads; pre-existing tabs loaded before the wedge), example.com (content scripts match all URLs), persistence (a stuck sheet stays until removed), and the clears as wedge-lifting observed on new tabs (with the same old-tab caveat as everything else).

Why it is only a sketch: no candidate sheet has been identified; no extension other than Transparent Zen has a known hiding rule; and it needs the rule to be conditional, since a plain unconditional body rule would hide every load always, not intermittently. So it posits a removal step that stalls, which is V1's structure with a different carrier, and it inherits V1's need for a stall cause it does not name.

What would prove it: during a live incident, a saved stylesheet inventory (href, readable or not, rule count, recursive into grouping rules) showing an extra sheet, or an unreadable sheet, that is absent in a healthy tab; chrome-privileged inspection (Browser Toolbox) revealing a rule setting body visibility hidden; htmlClass empty (consistent with R); computed opacity and the Transparent Zen `::before`/`::after` logo markers absent (which would exclude the class mechanism specifically). The decisive experiment: reproduce with Transparent Zen disabled (or in a clean profile). If the incident recurs with Transparent Zen disabled, Transparent Zen is out and the sheet belongs to something else. If it never recurs across many `window/new` loads, Transparent Zen (or extensions generally) is implicated.

### E2. Secondary sketches, weaker

Per-instance V1 refinement: the extension chain stalls per content-script instance, not globally. It keeps Transparent Zen but drops the global wedge. It still needs htmlClass present, so it inherits V1's wound from A1 and is weaker than E1.

The forms.css loose end: the pack rules out the UA stylesheet by grepping `res/html.css` for "visibility" (zero occurrences) but notes `forms.css` was NOT grepped, asserting without evidence that it "targets form controls, not body" (pack, ruled out). A 10-second grep was never done, so the UA exclusion is incomplete. This is a loose end, not a theory: `forms.css` setting body visibility hidden is implausible, but the exclusion as written is asserted, not shown.

Considered and rejected as standalone mechanisms: Firefox background-tab throttling and inactive-window paint suppression (throttling changes paint frequency, it does not set computed visibility hidden); the open alert on user tab 4 (tab-modal alerts block JS in that tab only); a Marionette session or tab mismatch (URL, title, and body HTML matched the fixture in the probes).

## F. Verdict: what survives

- Transparent Zen as prime suspect: SURVIVES. It is the only examined mechanism that produces exactly the symptom by code (pack, Transparent Zen finding). The byte-level match is real and specific. But "prime suspect" is not "proven cause": it has zero positive sightings of its predicted artifacts (A3).
- V1 (class stuck): BADLY WOUNDED, not logically dead. It survives only as "unfalsified because the key output was never saved". Its defense against A1 is weak, it takes a second hit in A2, it has no clearing mechanism (A5), and it needs an auxiliary hypothesis for the reused-tab datum (A4). Credibility low. A single saved re-probe decides it.
- V2 (transition frozen): DEAD as stated. Killed by B1 (the visibility interpolation rule) independently of R's summary, and by B2 and B3 (no refresh-stop evidence, wrong layer, mismatched timescales). The fix paper's V2 category and repaint step should be removed or reclassified as OTHER_HIDDEN.
- Stale geckodriver as common cause: DEAD. Incident 2 kills it (C1); the incident 1 link was correlation on a new tab with no mechanism (C2). The orphaning bug is real and should still be fixed, as session hygiene, not as a visibility cure.
- Hyprland IPC wedge as cause: UNPROVEN CORRELATE. Wrong layer for a CSS value, persists through the clear, absent from incident 1, timescales mismatch (B3).
- Bootstrap tab plus ensure_visible as workarounds: SURVIVE as reasonable harness defense with an honest failure mode, NOT as a validated fix. Evidence base is n=1 confounded by time (A4, D3), zero observed recoveries (D2), a false mechanism story (A4), ownership and isolation holes (D3), and a recovery step that violates the no-tab-driving rule while the owner is present (D4). The abort-heuristic fix and server-reuse fix survive intact as genuine runner bugs.
- The council's binary framing (V1 vs V2): DOES NOT SURVIVE. If R's "no class" is accurate, both variants are falsified and a third mechanism is required. The next probe must be built to find the third mechanism (stylesheet inventory, opacity, screenshot, class), not merely to re-litigate V1 vs V2.
- Overall status: suspect identified, mechanism unproven, workarounds unvalidated. Nothing in the current record licenses closing the incident or treating a green rerun as evidence the browser is healthy.

## G. The probe that settles it

One probe, run on a hidden tab before any recovery step, kill, or navigation, with output saved verbatim to disk: computed body visibility, computed body opacity, `documentElement.classList.contains("tz-hidden")`, full `className` for html and body, html inline style, a stylesheet inventory (each sheet's href, whether `cssRules` is readable, rule count, and a recursive scan into grouping rules), presence of the Transparent Zen `::before`/`::after` markers, a screenshot of the visible screen, and a re-check of the SAME tab 10 seconds later and after `window.focus()`. Then, as a separate experiment, the same `window/new` load with Transparent Zen disabled. The first probe discriminates V1, V2, and E1 in one shot. The second decides whether Transparent Zen is the owner at all. Until those two exist, every verdict in this incident is a lean, including this paper's.
