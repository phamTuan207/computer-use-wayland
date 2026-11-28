# Hidden-body incident: root cause (Worker Y4b synthesis)

- Date: 2026-11-21, incidents 16:36-16:44 and 17:52-~17:59 +07
- Status: SUSPECT IDENTIFIED, MECHANISM UNPROVEN, WORKAROUNDS UNVALIDATED
- Method: read-only investigation (no Zen driving), council of 3 + redteam, all papers in `improvements/worker-y4b-council-*.md` and `improvements/worker-y4b-redteam.md`. Evidence pack: `improvements/worker-y4b-evidence-pack.md`.

## Verdict

Transparent Zen 0.9.4 is the prime suspect: it is the only examined mechanism that produces exactly this symptom by code. But its two proposed variants do not both survive. V1 (the `tz-hidden` class stuck on) is badly wounded but not logically dead, and it survives only because the one observation that would kill it was never saved. V2 (the class removed but the 250 ms visibility transition frozen) is dead as stated, killed by the CSS visibility interpolation rule, which was verified against two independent sources after the council met. If R's "no class" summary is accurate, BOTH variants are falsified and a third mechanism is required, so the council's V1-vs-V2 binary is a false dichotomy. The stale-geckodriver link is dead as a common cause. The runner workarounds survive as unvalidated harness defense with an honest failure mode, not as a validated fix. Nothing in the current record licenses closing the incident or treating a green rerun as evidence the browser is healthy.

## What is proven

Transparent Zen 0.9.4, installed in `~/.config/zen/profile.Default (release)/extensions/{74186d10-f6f2-4f73-b33a-83bb72e50654}.xpi`, injects a content script on every page (`<all_urls>`, `document_start`): CSS `dist/transparent-zen.css` plus JS `dist/transparent-zen.js`.

- CSS: `:root.tz-hidden body { transition: none; visibility: hidden; background: none; opacity: 0 }` and `:root body { transition: visibility .25s, opacity .25s, background-color .25s; visibility: visible; opacity: 1 }`.
- JS: `initLoadingScreen()` runs first in the constructor, adds `tz-hidden` to `documentElement` synchronously at document start. The only removal is `removeLoadingScreen()`, which removes the class 500 ms after being called. Removal is gated on an async chain: fetch of `data/ContentScripts.json`, then `browser.storage.local.get("transparentZenSettings")`, then branch paths (supported site, dynamic transparency, or `processPage()`), with a `.catch` that also removes. A stall anywhere before a remove call leaves the class on, with no timeout or fallback in the decoded chain.
- This produces exactly the observed symptom: body computed visibility hidden plus opacity 0, html visible, no inline style, no author rule, DOM present, innerText empty, visibilityState and hasFocus unaffected.

Ruled out, with evidence (not assertion):

- Author CSS: fixture contains zero occurrences of "visibility"; example.com has no author stylesheet and was hidden; the same fixture URL was visible in a reused tab.
- Inline style: probe_q05e collected bodyInline/htmlInline; reported none (incident 1). Incident 2 collected inline body visibility only.
- User stylesheet: no `chrome/` directory in either Zen profile, so no userContent.css.
- UA stylesheet: `res/html.css` in omni.ja contains zero occurrences of "visibility". `forms.css` was checked after the council met: its three `visibility: hidden` rules are scoped to `:-moz-autofill-preview::-moz-text-control-editing-root`, `input:-moz-value-empty::-moz-reveal` / `::-moz-search-clear-button`, and `select option:not(:checked)::checkmark`. None can hide a body. forms.css is now properly excluded.
- Ambient Light for YouTube: its `visibility: hidden` rules are scoped to its own settings-menu tooltips and buttons, and it matches youtube.com only.
- Browsec VPN content scripts: https only; fixtures are http://127.0.0.1.
- Transparent Zen's dynamically injected sheet: `styles/shared/dynamic-transparency.css` (inserted via background `insertStyles`) contains no `visibility` and no `body` rule. It is not a hiding carrier.

Not fully verified: Obsidian Web Clipper content script (runs on http+https, not cleanly grepped, no loading-screen pattern known). Low prior.

## V1 (class stuck): badly wounded, not dead

V1 says the async chain stalls, `tz-hidden` stays on `<html>`, body stays hidden until the chain settles. It needs only one failure point and predicts the exact CSS state, the new-tab-only pattern (22 pre-existing tabs visible, fresh tabs hidden), and persistence through `window.focus()`.

Wounds, each tied to an evidence line:

1. R's "no class" is two concordant records, not one loose summary. R's report says "No inline style, no class, and no stylesheet rule sets it" (RUN-REPORT-AGYQ-20261121.md lines 133-135) and R's log repeats it (worker-r-test-run-log.md line 73). Probe_q05e was built to capture exactly this field (htmlClass, probe_q05e.py lines 12-14). A `tz-hidden` value there would have been the headline finding of a probe whose whole purpose was finding the source. The synthesis accepts the mechanism paper's discount only in part: the output was never saved, so V1 is not logically falsified, but the defense requires R to have misread or mis-summarized his own probe's headline output twice, in two documents written hours apart. The burden of proof now sits on V1.
2. A second, independent V1 prediction is denied by the same summary. `initLoadingScreen()` sets the `--zen-logo-path` custom property on documentElement as inline style, and `removeLoadingScreen()` removes it. Under V1 the removal never ran, so the inline property should still be present. Probe_q05e collected htmlInline. R reported "no inline style". Same caveat as wound 1 (output unsaved), but it is a second denied prediction, not a restatement of the first.
3. Zero positive sightings. No probe ever read opacity, saved a `classList.contains("tz-hidden")` result, or took a screenshot (the `:root.tz-hidden:before/after` fixed Zen-logo pulse elements would have been visible on screen). V1's case rests entirely on code fit.
4. No clearing mechanism. A geckodriver kill cannot unstick an extension content-script fetch in already-loaded tabs (incident 1), and a click in a different, already visible tab cannot settle a stalled chain in the hidden tabs (incident 2). The record never re-checked an old hidden tab in either incident, so whether any hidden tab ever cleared is unknown.
5. The reused-tab datum is awkward for V1. Probe_y4c navigated a pre-existing about:blank tab to q01 and got a visible body with working click and type, while new tabs to the same fixture and to example.com were hidden seconds earlier in the same probe. A `document_start` content script runs on a navigation in an existing tab exactly as on a `window/new` tab, so a globally stalled chain should have hidden the reused tab too. Escapes: the stall lifted in the 10-20 s gap (then the datum proves nothing about tab type), or the stall is per-load and random (then some new-tab loads should have been visible too; about 6 of 6 hid). Either way V1 needs an auxiliary hypothesis it does not have.

## V2 (transition frozen): dead as stated

V2 said the class is removed on time, but the 250 ms visibility transition never advances because refresh ticks stopped, so computed visibility stays hidden. This is falsified by the CSS visibility interpolation rule, verified after the council met against two independent sources (css-animation.com: "during a transition between visible and hidden, the interpolated value is visible for the whole duration if either end is visible... a transition from hidden to visible becomes visible on the first frame"; blog.kizu.dev quoting the spec: values of p between 0 and 1 map to visible). The interpolated visibility is `visible` from the first frame of a hidden-to-visible transition, whether or not any further refresh tick arrives, and `getComputedStyle` forces the style flush that starts the transition. The probes read `hidden` minutes later, across many evals. V2 predicts the exact opposite of the measured value for the exact property measured. There is no escape through "the transition never started": if it runs, interpolation yields visible; if it is suppressed entirely, the computed value is the after-change value, also visible. The only way computed visibility stays hidden is if a hiding rule is still applying, which is V1 or a third mechanism, not V2.

Supporting points: V2 also needed refresh ticks to stop entirely for 5+ minutes on an active, focused tab (hasFocus true, visibilityState visible, evals returning promptly), which nothing in the evidence shows; background throttling alone (about 1 Hz) would complete a 250 ms transition within about 1 s. The Hyprland prop fails on both incidents (persists through the clear in incident 2, absent from incident 1, timescales mismatch: hidden state about 7 minutes, input freeze about 1 minute).

Consequence: any future observation of class-absent plus computed-hidden must be classified as OTHER_HIDDEN (third mechanism), not as V2. The fix design's V2 category and repaint step must be removed or reclassified accordingly.

## Stale geckodriver as common cause: dead

Incident 2 ran on a fresh port (4448, never used before; R used 4446, P used 4450, default 4445), no geckodriver process was running at the 18:05 check, and the state cleared with no kill performed. A stale geckodriver cannot be the common cause. Incident 1's kill proved only that the orphan blocked session creation (POST /session timed out before, succeeded after); it proved nothing about hidden bodies, and the clear was verified only on a new tab under a new session, with no mechanism and about 8 minutes for spontaneous resolution. The WD orphaning bug itself (session POST timeout orphans the geckodriver because `__exit__` never runs) is real and should still be fixed as session hygiene, not as a visibility cure.

## Hyprland IPC wedge: unproven correlate

Real concurrent anomaly in incident 2 only (hyprctl and direct socat hung 17:53-18:00; journal shows no Hyprland errors 17:50-18:02; one xdg-desktop-portal-gtk ScreenSaver dbus error at 17:58:13). No onset or end timestamp, no mechanism linking an IPC hang to a CSS visibility value, persists through the clear, absent from incident 1. Wrong layer for a CSS value. It must not be used as a run gate labeled as an incident detector; at most it is a fail-closed safety gate, labeled as one.

## Third mechanism (required if R's "no class" is accurate)

If htmlClass was truly empty during a hidden tab, V1 and V2 are both falsified and a third mechanism is required. Strongest sketch (redteam E1, blind-scan / hidden-sheet): the hiding rule lives in a stylesheet probe_q05e could not see, so "no matching rule" is a probe artifact and no class is needed. Carriers visible in the probe's own code: a rule nested inside a grouping rule (`@media`, `@supports`, `@layer`, `@container`) that the flat top-level scan never visits (`r.style` is undefined on grouping rules), or a sheet whose `cssRules` throws in page context (cross-origin or extension sheet, silently skipped by `catch (e) { continue; }`). This fits every datum including R's "no class" at face value. It is only a sketch: no candidate sheet has been identified, and it needs the rule to be conditional (an unconditional body rule would hide every load always). Transparent Zen's dynamically injected sheet is ruled out as the carrier (no visibility/body rule, checked after the council). Obsidian Web Clipper remains the unexamined candidate with a loading or overlay mechanism. Proving E1 needs a saved stylesheet inventory (href, readable or not, rule count, recursive into grouping rules) plus opacity, logo-marker, and screenshot checks during a live incident, and a reproduce run with Transparent Zen disabled.

## Corrections to the record (found during this investigation)

1. "Switch away and back does not fix it" is a non-observation, cited wrongly twice. Probe_y4d's fresh tab was visible from the start, so it never tested un-hiding a hidden tab. Probe_q05d's docstring promises an explicit re-switch, but the code only fetches handles and prints the count; the switch was never executed. Switch-away-and-back has ZERO observations in either direction. The fix paper repeats the mis-citation and uses it against its own repaint step.
2. "Cleared by itself" is mislabelled in both incidents. Clearing was verified only on NEW tabs under new sessions. Old hidden tabs were never re-checked. Whether any hidden tab ever cleared is unknown.
3. The fix paper's bootstrap mechanism story is false. It claims a reused tab avoids the extension's `document_start` loading screen path. A navigation in a reused tab creates a new document and `document_start` content scripts run on it. The reused-tab evidence is n=1 confounded by time (it ran seconds before the incident cleared).
4. The geckodriver-kill causation for incident 1 is unproven correlation (see above).
5. The input freeze onset (17:59:13) predates probe_y4c's navigations (17:59:27, 17:59:33), so y4c did not cause the freeze.

## Fix design (adopted, with redteam corrections)

Adopt Council B's diagnose-first design in `run_live.py` / `run_agyq2.py`, with these corrections:

- Detection: one eval, one snapshot (`diagnose_body`): readyState, documentElement classList (`tz-hidden`, `tz-initialized`), body computed visibility/opacity/display plus html visibility, body inline style, transition property/duration/delay, body rect, innerText length (corroboration only), hasFocus/visibilityState, URL. Sample twice 300 ms apart when hidden. Classification: VISIBLE, TZ_STUCK_V1, OTHER_HIDDEN, FIXTURE_FAILURE. The TRANSITION_FROZEN_V2 category is removed: class-absent plus computed-hidden is OTHER_HIDDEN, not a live diagnosis.
- Recovery ladder (8 s total budget per tab opening): poll 250 ms up to 2.0 s for the extension's own removal; if V1 persists, remove `tz-hidden` exactly as `removeLoadingScreen` does (single eval, test tab only, test origin only, logged as intervention); then fall back to the bootstrap tab; then declare infra-blocked (`INFRA: hidden-body`, never a fixture failure, two consecutive infra-blocked tests abort the suite). The repaint step is removed as a remedy (V2 is dead; the step was justified by the mis-cited probe d). Never use a real click as a recovery probe.
- The switch-away step is removed entirely. The landed `ensure_visible` switches to the first non-test handle, which is a user tab by definition in a live Zen: a focus steal, and it violates the no-tab-driving rule while the owner is present. Replace `ensure_visible` internals, keep the name and call sites.
- `bootstrap_tab`: KEEP and strengthen (verify the reused tab with `diagnose_body` before returning it; narrow the reuse match to known fixture paths; record handle and URL; re-verify the handle still exists per test; add a `rebootstrap_tab` path). Its evidence base is n=1 confounded by time, so it is harness defense, not a validated fix. It must never take an about:blank tab without an ownership check, and the tab is returned to about:blank at suite end, never closed.
- Pass accounting: a test that passed only after `removed-tz-hidden` is a FLAGGED pass, counted separately in the summary, not folded silently into the headline pass count. Removing the class masks a real user-facing defect (a real user opening a new tab in this Zen during such a window sees a blank page for minutes), so the intervention must be disclosed in the test report and tracked as a separate item to fix or disable the extension. The fix is legitimate only paired with that tracked item.
- `WD.goto` is the choke point: diagnose after the 1.0 s settle, never return a hidden page as ready. `WD.__enter__` orphan fix: cleanup on raise, PID file, geckodriver log file instead of DEVNULL. `preflight()` fails closed before any tab opens: stale-geckodriver sweep by PID with parent check (kill only verified orphans), single-session lock check, Zen liveness, fixture server loopback check, owner-away check (explicit `LIVE_OWNER_AWAY=1`, never inferred from silence). The Hyprland IPC check, if kept, is a safety gate, not an incident detector.
- Never-do list stands: never touch a user tab, never dismiss the open alert on tab [4], never close tabs it did not open, never fake a PASS, never remove the class on a non-test tab, never kill Zen or a live driver's geckodriver, never retry unbounded, never drive while the owner is at the keyboard.
- Keep as genuine runner bugs (unrelated to the incident): the abort-heuristic fix (only session-creation failures count) and the server-reuse fix.
- Non-code options, in order: code fix first; trial blacklisting `127.0.0.1` in Transparent Zen settings in parallel (scoped, reversible; premise unverified, settings never read); disable-extension only as a one-off diagnostic with immediate re-enable, never as a standing procedure; reject a separate clean profile for live runs.

## Decisive experiment (adopted, design only, do NOT run now)

Adopt Council C's 6-phase design, plus the redteam's probe additions. Run only when the owner is away from the keyboard, under the Zen lock, with every probe output saved to disk with timestamps. Never navigate, type into, or click a user tab; never touch the tab with the open alert.

- Phase 0: baseline snapshot (Zen PID, Marionette, hyprctl with 10 s timeout, geckodriver ps table, extension state incl. `enableTransparency` / `lightweightTransparency` if readable, bootstrap tab recorded).
- Phase 1: reproduction loop, extension ENABLED, up to 30 `window/new` opens alternating example.com and the q01 fixture, full payload at 0 / 0.5 / 1 / 2 / 5 s. Stop early on a hidden tab, keep it open, go to Phase 2.
- Phase 2: frozen-state capture on the SAME hidden tab, in order: wait 10 s, `window.focus()` + 2 s, switch away and back (the test that never ran), Marionette click attempt (record the exact error), then open a NEW tab and IMMEDIATELY re-capture the OLD tab. This old-versus-new pair is the single most important capture.
- Phase 3: stale-driver test, only if a hidden tab persists: ps table, kill orphan by PID only (or record that none exists), fresh session on a fresh port, re-eval the SAME old tab, then a fresh new tab.
- Phase 4: control arm, extension DISABLED, repeat Phase 1 (30 iterations). Re-enable at the end and confirm the original state.
- Phase 5: control arm, bootstrap navigation vs `window/new`, 10 each, extension enabled.
- Capture payload at every step: htmlClass (full string) + classList array, htmlInline, bodyClass, bodyInline, bodyVis, bodyOpacity, htmlVis, transition property/duration/delay, matching-rules scan (recursive into grouping rules, with per-sheet readability flags), innerLen, hasFocus, visState, readyState, URL, rect, rAF tick count and largest gap over a 5 s window, presence of the Transparent Zen `::before`/`::after` logo markers, a screenshot of the visible screen, and the geckodriver ps table at the same minute.
- Pass/fail criteria (Council C, with V2 removed): V1 is PROVEN if a hidden tab shows `tz-hidden` in htmlClass at 5 s and every later capture while hidden, with rAF ticks flowing, opacity 0, zero reproductions in the disabled arm, and the old tab staying hidden after new tabs go visible. V1 is REFUTED by one clean counterexample: hidden tab, no `tz-hidden`, output saved. Stale-driver is PROVEN only by orphan present plus old-tab re-check after the kill; incident 2 already refutes it as a necessary cause. If a hidden tab appears with the extension disabled, no orphan, rAF flowing, and no `tz-hidden`, then V1, V2, and stale-driver are all out at once and the cause is unknown with a complete capture. That outcome is a success for the experiment.
- Stop rule: no reproduction after the full Phase 1 and Phase 4 loops means INCONCLUSIVE, not negative. The state is intermittent.

## Dissent record

- Mechanism paper leaned V1 and discounted R's "no class" as an unverified summary. The redteam held the discount weak (two concordant records, probe built to capture exactly that field) and the synthesis agrees the burden sits on V1. The mechanism paper's V2 case is overturned by the interpolation rule, which neither council paper knew.
- Fix paper treated V2 as a live diagnosis with a repaint remedy and cited probe d as evidence against repaint. Both are corrected above (V2 dead; probe d never tested it).
- Timeline paper and redteam agree on the record corrections and on the experiment design; the synthesis adopts both, with the redteam's probe additions.

## Sources

- `improvements/worker-y4b-evidence-pack.md` (evidence pack)
- `improvements/worker-y4b-council-mechanism.md` (Council A)
- `improvements/worker-y4b-council-fix.md` (Council B)
- `improvements/worker-y4b-council-timeline.md` (Council C)
- `improvements/worker-y4b-redteam.md` (Redteam)
- `improvements/worker-y4-run-log.md`, `tests/realistic/RUN-REPORT-AGYQ-20261121.md` lines 115-230, `improvements/worker-r-test-run-log.md` lines 55-110
- Transparent Zen 0.9.4 XPI, `dist/transparent-zen.css` and `dist/transparent-zen.js` (decoded from minified source on the laptop)
- CSS visibility interpolation: css-animation.com visibility reference; blog.kizu.dev quoting the CSS Transitions spec ("values of p between 0 and 1 map to visible")
