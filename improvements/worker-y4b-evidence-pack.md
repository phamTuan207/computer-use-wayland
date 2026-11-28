# Evidence pack: hidden-body incident (Worker Y4b root-cause investigation)

Read this pack, the Y4 run log, R's run report, and the probe files before writing your position paper. Do NOT drive the owner's Zen. Read-only work only.

## The symptom (both incidents)

New tabs opened through Marionette `window/new` render with:
- `getComputedStyle(document.body).visibility === "hidden"`, inherited through the whole tree; `document.documentElement` visibility is `visible`.
- `document.body.innerText` empty (consistent with visibility hidden, not opacity).
- rect non-zero, display block, `document.hasFocus() === true`, `document.visibilityState === "visible"`, readyState complete, DOM fully present.
- Persists 5+ s; `window.focus()` does not fix it; switch-away-and-back does not fix it (Y4 probe d).
- First interaction fails: "element not interactable: could not be scrolled into view" (Marionette interactability check).
- Only tabs opened via Marionette `window/new` are affected; pre-existing user tabs render normally at the same time.
- Not content-specific: same fixture URL, and `https://example.com` (bare page, no author stylesheet), both hidden.
- Not localhost-specific.

## Incident 1: 16:36-16:44 (Worker R, agy-q run)

- 16:34: same q05 flow PASSED in the full run. State flipped on 16:34-16:36.
- 16:36:05 and 16:36:56: two solo q05 re-runs fail at first interaction.
- Probes q05-q05e (~16:37-16:41): see `tests/realistic/probe_q05*.py` and `improvements/worker-r-test-run-log.md` lines 63-100.
- probe_q05e (source hunt) collected: bodyInline, bodyClass, htmlClass, htmlInline, per-sheet rule scan (rules with `r.style.visibility === "hidden"` where `document.body.matches(selector)`). Reported result: no inline style, no class, no matching stylesheet rule; fixture contains zero occurrences of "visibility". Conclusion at the time: browser-side, not the page.
- 16:42: probe6 (q05f, the override test) first attempt: POST /session timed out after 30s. Found orphaned geckodriver PID 113280 listening on port 4446 (R's WD_PORT), parent python long gone. Killed it by PID.
- 16:44: pgrep confirms geckodriver gone.
- 16:45: probe6 retry on a NEW tab: body visible, innerText 677 chars, click + type work, q05 passes 4,041 ms at 16:46. NO override was ever applied (the override test never ran against a hidden tab: it timed out first).
- IMPORTANT: the "clearing" was verified ONLY on a NEW tab. The old hidden tabs were never re-checked. Whether they stayed hidden is UNKNOWN.
- R's own note: correlation, not proven causation. Also recorded: WD class orphans its geckodriver if `__enter__` raises before `__exit__` runs (session POST timeout path).

## Incident 2: 17:52-~17:59 (Worker Y4, agy-q2 run)

- 17:52: first run 0/2 aborted (q01, q02 both body visible=False, then element not interactable). Abort itself was a Y4 runner bug (abort heuristic counted any error containing "session"; fixed in 03307cd).
- Probes y4 (17:53), y4b (17:57), y4c (17:59), y4d (18:00): see `tests/realistic/probe_y4*.py` and `improvements/worker-y4-run-log.md`.
- probe_y4b: all 22 pre-existing tabs visible; new test tab hidden; `window.focus()` + 2 s does not fix.
- probe_y4c: new tab to q02 fixture hidden; new tab to example.com hidden; navigating a PRE-EXISTING about:blank tab to q01 fixture gives VISIBLE body, click OK, type OK.
- probe_y4d (18:00): fresh new tab visible from the start; switch away+back checks pass; click OK.
- The hidden state "cleared by itself ~17:59, right after a real click in the reused tab" (Y4 log). Same caveat as incident 1: the clear was verified on a NEW tab (probe_y4d), old hidden tabs never re-checked.
- Side findings: Hyprland IPC socket unresponsive the whole probe window (`hyprctl version/monitors/clients` and direct socat to `.socket.sock` hang until timeout). Zen PID 27958 alive, Marionette fine. One user tab has an open alert (tab [4], "unexpected alert open" on eval) - never touched.
- 17:59:13-18:00:08: owner's physical keyboard + mouse stopped responding (~1 min), self-recovered. Likely focus steal from probe tab navigation; reported to owner, Y4 paused on tab-driving. The freeze onset (17:59:13) slightly PREDATES probe_y4c's navigations (HTTP log: 17:59:27, 17:59:33). probe_y4b ran ~17:57 (HTTP log 17:57:03).
- No geckodriver process running at 18:05 check. Y4's WD_PORT was 4448 (fresh port; R used 4446, P used 4450, default 4445). Y4's pre-run checks did NOT check for stale geckodriver PIDs.
- Y4's runner fixes (commit 03307cd on todolist-push): abort heuristic (only session-creation failures count), shared visible bootstrap tab (reuse pre-existing about:blank tab, fresh WebDriver session per test, storage cleared, fixture reloaded), `ensure_visible()` recovery (switch away+back, window.focus(), wait 2 s, re-check; explicit driver-state error if still hidden), server-reuse fix.
- U's fcc-k run (16:58, 10/10 PASS) had NO hidden-body incident. So incident 2 flipped on between ~16:58 and 17:52.

## The Transparent Zen finding (Y4b, byte-level, from the installed XPI)

Extension: Transparent Zen 0.9.4, XPI `{74186d10-f6f2-4f73-b33a-83bb72e50654}.xpi` in `~/.config/zen/profile.Default (release)/extensions/`. Manifest content_scripts: matches `<all_urls>`, css `dist/transparent-zen.css`, js `dist/transparent-zen.js`, run_at `document_start`. It runs on EVERY page, including http://127.0.0.1 fixtures and example.com.

Injected CSS (`dist/transparent-zen.css`, minified, 2,532 bytes):
- `:root body { transition: visibility .25s, opacity .25s, background-color .25s; visibility: visible; opacity: 1 }`
- `:root.tz-hidden { background: none }`
- `:root.tz-hidden body { transition: none; visibility: hidden; background: none; opacity: 0 }`
- Plus `:root.tz-hidden:before/after` fixed Zen-logo pulse elements.

Injected JS (`dist/transparent-zen.js`, minified, 18,320 bytes; key functions, decoded):
- `initLoadingScreen()`: called FIRST in the main class constructor (`new E` at file end). Sets `--zen-logo-path` custom property on documentElement, then `document.documentElement.classList.add("tz-hidden")`. Synchronous, at document_start.
- `removeLoadingScreen()`: `setTimeout(() => { document.documentElement.classList.remove("tz-hidden"); document.documentElement.style.removeProperty("--zen-logo-path"); }, 500)`. Removes the class 500 ms AFTER BEING CALLED.
- Call chain (all async): constructor runs `checkIfWebsiteAlreadySupported()` = `fetch(browser.runtime.getURL("data/ContentScripts.json"))`, then `.then(...)` runs `browser.storage.local.get("transparentZenSettings")`, then branches:
  - Supported site: `initSupportedWebsite()` -> removeLoadingScreen on DOMContentLoaded / readystatechange-complete / immediately-if-complete.
  - Otherwise: `initDynamicTransparency()` -> if transparency disabled: removeLoadingScreen() immediately; if enabled and domain allowed: `browser.runtime.sendMessage({action:"insertStyles", filePath:"styles/shared/dynamic-transparency.css"})` (fire-and-forget, not awaited), then `lightweightTransparency ? removeLoadingScreen() : processPage()`.
  - `processPage()`: defines `e()` = initExtensionSettingsStyles + applyTransparencyRules + MutationObserver (100 ms debounce -> applyTransparencyRules + removeLoadingScreen once). Registers DOMContentLoaded listener for `e()`, readystatechange listener (complete -> removeLoadingScreen), and `document.readyState === "complete" && removeLoadingScreen()` (immediate).
  - `.catch(...)` on the outer chain: logs error, calls removeLoadingScreen().
- Background script (`dist/background.js`, 660 bytes): onMessage `insertStyles`/`removeStyles` -> `browser.tabs.query({currentWindow:true})` + `insertCSS`/`removeCSS` per tab (skips tabs if >40 tabs and not active).
- This mechanism produces EXACTLY the observed symptom: body computed visibility hidden + opacity 0, html visible, no inline style, no author rule, DOM present, innerText empty, visibilityState/hasFocus unaffected (those are document/window properties, not CSS).

## Two variants of the Transparent Zen theory (debate these)

- V1 (class stuck): the async chain before removeLoadingScreen stalls (fetch of ContentScripts.json hangs, or `browser.storage.local.get` never settles, or the extension background process is wedged), so `tz-hidden` stays on `<html>` for minutes. Predicts: during the hidden state, `document.documentElement.className` contains `tz-hidden` (and `tz-initialized` after settings load).
- V2 (transition frozen): the chain completes normally and the class IS removed ~0.5-1.5 s after load, but the CSS `visibility .25s` transition from hidden to visible never advances because the tab's refresh driver is stalled (no paint ticks: window occluded / compositor wedged / no vsync). Computed visibility stays hidden even though the class is gone and no rule matches. Predicts: during the hidden state, `document.documentElement.className` does NOT contain `tz-hidden`; no stylesheet rule matches body; the state clears the moment the window repaints (tab activation, real click, compositor recovery).
- Note on V2's premise: CSS transitions advance by wall-clock time per refresh tick. Background tabs in Firefox are throttled (about 1 Hz), which alone would complete a 250 ms transition within ~1 s of wall time. For V2 to hold 5+ minutes, refresh ticks must STOP entirely, not just throttle. Whether a visible-window tab can have a fully stopped refresh driver is an open question for the council.
- Note on V1 vs R's "no class" finding: R's probe_q05e collected htmlClass, and R's report says "no class". If htmlClass was truly empty during incident 1, V1 is weakened for incident 1 (the class would have been present). But the probe output itself was not saved to disk (only R's summary survives), so the exact htmlClass value is UNVERIFIED. Do not over-claim either way.

## Ruled out (with evidence)

- Author CSS: fixture contains zero occurrences of "visibility" (R's grep); example.com has no author stylesheet and was hidden; reused blank tab with the SAME fixture URL was visible.
- Inline style: probe_q05e bodyInline/htmlInline, probe_y4c inlineVis - reported none (incident 1 explicit; incident 2 per Y4 log summary).
- User stylesheet: no `chrome/` directory in either Zen profile, so no userContent.css/userChrome.css.
- UA stylesheet: `res/html.css` in /opt/zen-browser-bin/omni.ja contains zero occurrences of "visibility" (grep, 21/11). (forms.css not grepped; it targets form controls, not body.)
- Ambient Light for YouTube (content.css `visibility: hidden` at lines 1848, 2062): rules are scoped to `.ytpa-ambientlight-settings-menu` tooltips/buttons, and the extension only matches youtube.com. Not our pages.
- Browsec VPN content scripts: match https only; our fixtures are http://127.0.0.1. Cannot explain fixture tabs (could run on example.com, but the fixture evidence rules it out as the common cause).
- Page content / fixture bug: same URL visible in reused tab, hidden in window/new tab; example.com hidden.

## Not fully verified

- Obsidian Web Clipper content script (runs on http+https): not cleanly grepped (one exec dumped a large locale file); no loading-screen pattern known; treat as unexamined, low prior.
- Whether htmlClass contained `tz-hidden` during either incident (probe outputs not saved).
- Whether the stale-geckodriver kill CAUSED incident 1's clear (correlation only; the clear was verified on a new tab under a new session).
- Whether the Hyprland IPC wedge caused incident 2, or was coincidence, or was an effect (e.g., a client flooding IPC). Journal shows no Hyprland errors 17:50-18:02; one xdg-desktop-portal-gtk ScreenSaver dbus error at 17:58:13. Current IPC state could not be re-verified from SSH (no instance signature found under /run/user/1000/hyprland/).
- Whether the open alert on user tab [4] plays any role (tab-modal alerts block JS in that tab only; no evidence it affects other tabs).
- Whether the extension's `enableTransparency` / `lightweightTransparency` settings are on (settings live in extension storage, not read).

## Runner mechanics (for the fix design)

- `tests/realistic/run_live.py` WD class: geckodriver `--connect-existing --marionette-host 127.0.0.1 --marionette-port 2828 --port <WD_PORT> --log warn`, stdout/stderr DEVNULL (no geckodriver log file exists). One WD per `with` block; `__exit__` closes opened tabs + deletes session + terminates geckodriver. `__enter__` raising orphans the geckodriver (known bug, R's open item 4).
- `new_tab()`: POST `/window/new` type tab, switch to it (verified), `goto(url)` = POST /url + wait readyState complete + 1.0 s settle. `switch()` sleeps 0.5 s. `visible(css)` checks rect + display + computed visibility. `click()` scrolls into view, then POST /element/.../click (Marionette interactability check requires visible).
- Ports used: default 4445, R 4446, Y4 4448, P 4450. Marionette 2828. Zen PID 27958 since 15:31, flags --remote-debugging-port=9222 --marionette.
- Y4's fixes already in run_agyq2.py (03307cd): bootstrap_tab (reuse pre-existing visible tab), ensure_visible() recovery, abort heuristic fix. These WORK AROUND the incident; they do not remove its cause.

## Your deliverable

Write a position paper to `improvements/worker-y4b-council-<role>.md` (role = mechanism, fix, timeline, or redteam). Keep it short and evidence-cited: verdict first, then the evidence lines that decide it, then what would change your mind. No em dash or en dash anywhere. Never claim what the evidence does not show.
