# Council-2: Zen-AI Cloudflare fix plan (R3-L3 re-plan)

- Date: 2026-11-26. Author: COUNCIL-2 (Cloudflare fix). Status: fix candidate proven live (see section 4 and the evidence log); resume gate criteria in section 6 for council + redteam unanimous sign-off.
- Evidence: improvements/replan-council2-cloudflare-evidence-20261126.md, raw logs in improvements/council2-evidence-raw/, harness in improvements/council2-harness/.
- Rules: no em dashes or en dashes; English only; ponytail for all code (smallest complete change, reuse before writing, standard library/platform before dependencies, no unrequested abstraction, one small test for non-trivial logic, never cut validation/security/error handling); every worker brief restates the event-log duty (log key events: decisions, test results, fix milestones, revert actions, via ~/workspace/agent-event-log/log-event.sh); every test brief carries the user-path short form plus user entry point and forbidden shortcuts fields.

## 1. Problem in one paragraph

The run Zen is launched by the zen-ai wrapper with --remote-debugging-port=9222 --marionette. Both flags force navigator.webdriver=true in every page, all the time (Mozilla bugs 1719505, 1632821; the flag is not bound to session lifetime, bug 1696425 open). Cloudflare reads that signal plus behavior and answers with "Verify you are human" / "Just a moment..." on coolors.co and chatgpt.com. Four bot-wall hits so far: R3-011 (timeanddate Cloudflare, INVALID), R3-022 (Google sorry/reCAPTCHA, INVALID), R3-024 (Openverse Cloudflare, INVALID), R3-026 (coolors Cloudflare, INVALID, Ray ID a603c518ed7945df, the owner photo). The fix must keep BiDi 9222 driving, Marionette 2828, the pill on any agent control, and fast observation. Machine-specific optimizations stay always-on locally; anything committed to the repo is OPTIONAL (opt-in, default off).

## 2. Research summary (25/11 doc + fresh 26/11)

Prior research (zen-cloudflare-chatgpt-fix-research-20261125.md, read in full): wrapper flags are the most likely cause; privacy.resistFingerprinting ruled out (not set); no VPN/proxy/blocker; ranked fixes 0a private check, 0b stock check, 1 Chromium workaround, 2 clear cookies, 3 launcher split, 4 runtime toggle add-on, 5 BiDi preload script, 6 Zen build investigation.

Fresh research 26/11 (web search + mei run 32 + mochi run 233 last30days crawls, both delivered):
- Current Firefox: the pref trick (dom.webdriver.enabled) has not worked since Firefox 88. Working approaches: inject before page scripts (BiDi preload script or WebExtension) or patched binary. (codestudy.net, Oct 2026.)
- firefox-bidi-mcp browser_hide_automation_flags: BiDi preload reporting webdriver false, measured true to false; honest limit, other signals can still expose automation. (glama.ai, Nov 2026.)
- claude-for-zen (ilhamnadhif): BiDi script.addPreloadScript redefining Navigator.prototype.webdriver with a Proxy so the getter stays native-shaped, ZEN_HIDE_WEBDRIVER=1 by default, verified live 26 Nov 2026 (mei crawl). Its add-on toggles remote control via the privileged RemoteAgent.startAtRuntime method (not a pref), gated on remote.experimental.dynamicstart.enabled, port 9222 (mei crawl, extension/parent.js). The project states CAPTCHAs are not solved by design.
- Negative evidence (both crawls, high confidence): no reliable no-solve pass in the last 30 days for real-key managed Turnstile without a click (Ujeebu, 19 Nov 2026, 13 browsers, no token). Preload patching fixes a naive value read but leaves descriptor and prototype tells that detectors probe (mochi crawl). Google refused requests on the native webdriver value in controlled trials (RESONEO, Oct 2026, via mochi crawl).
- Cloudflare Precursor (July 2026): continuous session behavior scoring (pointer, keyboard, focus, visibility); Armed mode can invalidate cf_clearance mid-session. Single-signal fixes have a ceiling. (Cloudflare blog/docs via mochi crawl; decodo.com 19 Nov 2026.)
- Skill-scout constraints folded in: agent-browser 0.45.0 (VM) does not fix Zen Cloudflare, not proposed. Rejected and not proposed: Anchor Browser, browser-use as driver, MCP reference bundle, LLMLingua, computer-use-linux MCP as runtime (ydotool ban + pill rule), opencode-marketplace, GitHub MCP for VM. Parked: Steel, Exa, Firecrawl, dogtail/AT-SPI. Playwright MCP is installed on Codex (laptop) but the run drives Zen via BiDi/Marionette, not Chromium; noted as a non-fit for the Zen lane. promptfoo 0.126.0 is available on the VM if the redteam wants an eval harness; not required.
- Graphify: codebase questions in this workstream were answered with graphify query on ~/workspace/cu-graphify/graphify-out/ (pill acquire in scripts/first_action.py, validate_actions in scripts/cu.py). Laptop-CLI graphify installs are council-3 scope.

## 3. Decisive checks (live, 26/11, pill held, timed)

Full detail in the evidence log. Headlines:
- 0a private/fresh context: webdriver still true, coolors still blocked. Cookies and extensions ruled out.
- 0b stock launch, no flags, fresh temp profile: chatgpt PASSED, coolors BLOCKED (Just a moment). So flags are not the sole cause on a cold profile. In the warm run profile, the round 1 A/B proves the signal is a real contributor: baseline direct blocked (Ray ID a603e4d349ac3dc3), preload passed minutes later, same profile, same network.
- Baseline user-way after preload visits passed coolors with webdriver true, confounded by cf_clearance minted earlier (cookie names verified). Recorded as confounded, not as baseline evidence.

## 4. Chosen fix (candidate 3a, Proxy variant) and live proof

Chosen: BiDi preload script installed by the driving session, Proxy variant from claude-for-zen (wrap the native Navigator.prototype.webdriver getter in a Proxy that returns false). Why this variant: round 5 descriptor probe shows it matches the baseline shape (own property stays on the prototype, getter name "get webdriver", toString shows native code), while the delete + defineProperty variant leaves two tells (own property on navigator, getter body "() => false"). The Proxy variant is the smallest change with the cleanest profile. It is session-scoped: installed with script.addPreloadScript when a BiDi session starts, removed with script.removePreloadScript at session end. No profile, wrapper, launcher, or pref changes. Revert = end the session (or remove the preload); nothing persists.

Live proof (round 4, user-way, runner lane act-now + held BiDi session, pill visible in observe images):
- coolors.co: search, click first result, landed usable, no challenge, webdriver false, scroll worked. PASS.
- chatgpt.com: same path, landed usable, no challenge, webdriver false. PASS.
- timeanddate.com: landed on World Clock, no challenge, webdriver false. PASS.
- openverse.org: landed usable, no challenge, webdriver false. PASS.
- Driving regression: real click navigated, scroll worked, screenshots captured, all act-now batches rc=0, pill acquired and released cleanly every round.
- Direct-navigation A/B (round 1): baseline blocked, preload passed on coolors + chatgpt.
- Google Translate (round 5): no sorry wall reproduced in any mode today. The shim does not claim to fix Google sorry.

Honest limits: this fixes the webdriver value read on the sites and tiers tested today. Managed Turnstile that demands a click, Precursor Armed mode, and future detector probes of the Proxy are not proven away. The crawls are right that no no-solve pass is guaranteed. The gate criteria in section 6 therefore test the actual run sites user-way, fresh session, by an agent that did not implement the fix.

## 5. Implementation steps (exact)

Owner of implementation: SSH worker on the laptop (coordinator assigns). Mei/mochi: research only (done). Redteam: attacks the gate criteria.

Step 1, add the shim to the Zen driving path (machine-specific, always-on locally):
- Where: the BiDi session setup used by the runners. Today the laptop drives Zen through geckodriver WebDriver classic (zen_dom.ZenSession, Marionette 2828) and through raw BiDi where needed. The shim needs a BiDi session: create the WebDriver session with webSocketUrl capability (geckodriver supports it), then send script.addPreloadScript with the Proxy shim before any navigation. Reference implementation: improvements/council2-harness/holder.mjs (SHIMS.proxy) and bidi_round5.mjs. Ponytail: reuse the holder pattern, do not build a new framework.
- Shim (verbatim, from holder.mjs):
  (() => { try { const p = Object.getPrototypeOf(navigator); const d = Object.getOwnPropertyDescriptor(p, 'webdriver'); if (d && d.get) { const fakeGet = new Proxy(d.get, { apply: () => false }); Object.defineProperty(p, 'webdriver', { get: fakeGet, configurable: true, enumerable: d.enumerable }); } } catch(e){} })()
- Install point: immediately after session.new, before browsingContext.create or any navigate. Remove at session end. Log install and remove with timestamps (event-log duty).
- One small test for the logic (ponytail): the descriptor probe in bidi_round5.mjs (webdriver false, own_on_proto true, own_on_navigator false, getter name "get webdriver") run on a data page at session start; fail the drive loudly if the probe does not match.

Step 2, runner brief update (coordinator): every Zen drive brief states the shim is installed by the session setup, the probe result is part of evidence, and the user-path fields (entry point, forbidden shortcuts) are filled. End-state-only evidence is returned unread (fast-reject).

Step 3, repo commit (optional, default off): if the shim helper is committed to computer-use-wayland, it lands behind an opt-in flag (for example CU_HIDE_WEBDRIVER=1), default off, generic text, no personal info. The laptop keeps it always-on via local env, per the 24/11 design principle.

Step 4, permanent structural fix (candidate 3c, post-run, separate approval): split daily Zen (flag-free) from run Zen (zen-ai wrapper). Exact edits when approved: point ~/.local/share/applications/zen.desktop Exec lines at /opt/zen-browser-bin/zen-bin with no flags; keep ~/.local/bin/zen-ai unchanged as the explicit run launcher; restart Zen once; re-verify BiDi 9222 + Marionette 2828 come up only under zen-ai; re-verify the run coordinator launch path. Revert: restore the .desktop Exec lines to zen-ai (record before/after file hashes at edit time). This fixes daily browsing (webdriver false with no session) but does not by itself fix run drives, because the run still needs the flags. It is complementary, not a substitute for step 1. Do not execute during the paused run without coordinator + redteam agreement; it needs a Zen restart.

Candidate 3b (runtime toggle add-on) disposition: evaluated, not chosen for now. It needs xpinstall.signatures.required=false and extensions.experiments.enabled=true, an unsigned experiment add-on calling RemoteAgent.startAtRuntime, tested in a temp profile first. It solves daily browsing elegantly (remote control only while connected) but is a bigger build, changes profile trust settings, and is untested against Turnstile (mei crawl). Keep as the post-run project if 3c is not enough. If built: temp profile test first, same gate criteria, revert = remove add-on + restore the two prefs (record before values).

## 6. Live test criteria = resume gate (redteam verifiable, pass/fail)

The fix counts as proven ONLY when all of these pass, run by an agent that did NOT implement the fix (Lauren Tan evidence standard: exercise the real user path, capture the action and the resulting state, not just the final screen). User entry point for every site test: blank tab or start page, type the query in the address bar or search engine, press Enter, click the first result. Forbidden shortcuts: deep links, direct navigation commands to the target, internal setters, test-only endpoints.

Gate checks (each PASS/FAIL, timed, wall-clock + elapsed logged):
1. coolors.co user-way: search "coolors", click first result, landing usable (homepage content, no "Just a moment", no "Verify you are human"), webdriver reads false, scroll or palette interaction works, pill visible in evidence images.
2. chatgpt.com user-way: search "chatgpt", click first result, landing usable (prompt box present, no challenge), webdriver false, pill visible.
3. timeanddate.com user-way: search, click, landing usable, no challenge, webdriver false. (Bot-wall class R3-011.)
4. openverse.org user-way: search, click, landing usable, no challenge, webdriver false. (Bot-wall class R3-024.)
5. Fresh-session repeat: checks 1 and 2 repeated once from a new BiDi session (new tab, shim reinstalled) so the result is not a warm-profile artifact. Note: cf_clearance from earlier passes can mask a regression; the redteam should also run one check with site cookies cleared for the target host, or accept the round 1 style A/B (baseline blocked, shim passed) as the unconfounded contrast.
6. Driving regression: navigate + real click + scroll + screenshot all work with the shim installed; BiDi 9222 and Marionette 2828 still answer; pill acquires and releases cleanly.
7. Descriptor probe: webdriver false, own property on prototype true, own on navigator false, getter name "get webdriver".
8. Stock webdriver read (closes the round 6 gap): stock launch, dismiss onboarding, read navigator.webdriver on a local page (expected false), record value.
If any of 1 to 4 fails, the gate does not open on the Zen lane. Fallback in section 8 applies.

## 7. Bot-wall class coverage

- Cloudflare Turnstile / Just a moment (R3-011, R3-024, R3-026): covered for the value-read tier proven today on all three hosts plus chatgpt. Not guaranteed for managed click-tier Turnstile or Precursor Armed mode.
- Google sorry/reCAPTCHA (R3-022): NOT covered. No sorry wall reproduced today in any mode; it is rate/IP based. The INVALID path remains.
- Invalid budget note (epoch 9 handoff): R3-026 INVALID, no medium backup remains, denominator 55, medium invalid count 3 over the per-group cap of 2. The breach is already incurred; the fix reduces future bot-wall invalids but the plan must not assume zero. Cap-breach and bar recompute are the coordinator decision at synthesis.

## 8. Fallback if the gate fails

- Chromium/Brave lane for Cloudflare-heavy tasks (CDP 9223/9224 already running on ws3 for the agents; a task lane there keeps webdriver false without any shim). Limits: the run is specified on Zen via BiDi/Marionette; moving a task to Chromium changes the tested surface and needs coordinator + scorer agreement per task.
- INVALID path stays for tasks that still hit walls (bot-check rule: stop, record Ray ID, declare INVALID candidate). Budget impact per section 7.
- Do not use: agent-browser (does not fix Zen), VPN/DNS changes (IP is not the differentiator), privacy.resistFingerprinting (makes Turnstile worse), dom.webdriver.enabled pref (dead since Firefox 88), Chrome-only flags (ignored by Firefox).

## 9. Risks

- Detector evolution: Precursor and Turnstile update often (Nov 2026 tightening). The Proxy shim may be probed later (for example Function.prototype.toString on the getter returns native-looking output today; deeper probes may differ). Mitigation: gate re-run before resume and after any Zen update; keep the INVALID path.
- Session leak: a crashed BiDi client can block session.new for about 9 minutes (observed). Mitigation: always session.end in a finally path (harness does); if leaked, wait for reap, do not restart Zen mid-run.
- BiDi input: raw input.performActions fails on this build; real input goes through act-now. Any future BiDi-input work must re-prove itself live.
- Cold-profile coolors: stock Zen blocks on direct nav with no flags. A task that starts from a cold profile or clears cookies may still wall. Mitigation: run tasks in the warm run profile, user-way arrival.
- Shim scope: session-scoped only. The owner daily browsing in the same Zen still sees webdriver true when no agent session is active. Only 3c or 3b fixes that; both are post-run.

## 10. Revert path

- Shim: removePreloadScript or end the BiDi session. Nothing persisted. Verify: probe page reads webdriver true again.
- Repo flag (if committed): set the opt-in env off; default is off.
- 3c (if executed later): restore .desktop Exec lines from recorded hashes, restart Zen, re-verify listeners.
- 3b (if built later): remove the add-on, restore xpinstall.signatures.required and extensions.experiments.enabled to recorded before values.

## 11. Who does what

- SSH worker (laptop): implement step 1 + step 2 support, run the gate checks as implementer (not as prover).
- Independent prover (not the implementer): run section 6 gate checks fresh, file evidence.
- Mei/mochi: research (done, runs 32 and 233). No laptop work (no SSH).
- Redteam: attack the gate (cookie-clear variant, descriptor probes, managed-Turnstile tier, session-leak drill).
- Coordinator: synthesis, cap/bar decision, resume word to epoch 9 when council + redteam unanimously agree tools are sufficient and the plan is good enough.
- Every brief in this workstream restates: ponytail rule, event-log duty, user-path short form with entry point and forbidden shortcuts, delivery path, and the ydotool ban. Never assume an agent capability; ask it directly.
