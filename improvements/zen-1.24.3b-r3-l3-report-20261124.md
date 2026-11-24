# Zen 1.24.3b R3-L3 Long-Run Report (clone1)

- Source: clone1 (Muse PWA, chat "Chat - clone1"), Space "Zen 1.24.3b R3-L3 Report"
- Space URL: https://muse.ai/library/artifacts/zen-1-24-3b-r3-l3-report
- Fetched: 2026-11-24 ~20:10 +07 via CDP (Brave 9224, muse.ai page target), read from the artifact iframe
- Verdict: GO on 1.24.3b, driven via WebDriver BiDi + Marionette (not CDP)
- Note: verbatim copy of clone1's report text as rendered in the Space.

---

● GO — on 1.24.3b · update lock: verify before launch
Research window 25 Oct – 24 Nov 2026 · Run: R3-L3, 19–31 h, Wayland / Linux · Prepared 24 Nov 2026
Zen 1.24.3b for a 19–31 hour automated run

Short answer: run Zen 1.24.3b on Firefox 160.0.1, drive it with WebDriver BiDi + Marionette — not CDP, protect the run tab from unloading, freeze the window, and plan a watchdog restart. Firefox 161 shipped today (24 Nov) — keep the automation update-disabled default and verify no update can fire before you start; the exact Zen update lock was not confirmed in the research.

✓ USE THIS VERSION

1.24.3b (17 Nov 2026) — fixes the closed-window memory leak (gh-16587) that grows memory and pauses over time. Do not start on 1.24.2b / 1.24b.

✕ NOT CDP

Firefox removed its experimental CDP in Firefox 141 (22 Jul 2025). --remote-debugging-port now serves BiDi only. connectOverCDP and /json/* will not work.

! WATCH TONIGHT

Firefox 161.0 released 24 Nov 2026. A Zen rebase is imminent. Keep the automation update-disabled default, verify the version at launch, and confirm the update lock holds — it was not verified for 1.24.3b.

Top 10 tweaks
Launch + user.js
What 1.24.3b fixes
Settings
Risks & mitigations
Watchdog plan
Open questions
Sources
Ranked — the 10 tweaks that matter most

In impact order for a 19–31 h run. Items 1–6 are sourced from in-window releases/issues; 7–10 carry weaker or undated evidence and are flagged as such.

Run 1.24.3b (Firefox 160.0.1) and keep the automation update-disabled default — verify the lock before launch

The closed-window leak fix (17 Nov 2026) is the only in-window fix that directly addresses multi-hour memory growth. Source: Zen release notes. The update lock itself was not verified for 1.24.3b (see the red warning under user.js) — do not start until you have confirmed updates cannot fire mid-run.

Drive via BiDi + Marionette, not CDP

Dedicated profile: zen --new-instance -P r3l3 --marionette --remote-debugging-port (+ --headless if headed UI is not needed). CDP was removed in Fx141.

Protect the run tab from unloading

Set zen.tab-unloader.excluded-urls to the run URL(s), keep memory headroom, monitor about:unloads. The old zen.tab-unloader.timeout-minutes pref no longer exists.

Freeze the window

Set size/viewport at launch. Never resize, move, or switch spaces mid-run — resize-render freeze #16706 (19 Nov), spaces disappearing #16515 (closed 18 Nov).

Watchdog + planned restart, not crash recovery

Heartbeat BiDi/Marionette every 30–60 s, poll RSS, snapshot tab URLs externally, restart at a checkpoint with session restore. Do not rely on Safe Mode (#16694, 18 Nov).

Avoid video / HLS / YouTube-scroll / WebGL-game loads on Wayland

RDD SIGSEGV #16718 (20 Nov), ~46% frames dropped #16690 (17 Nov), YouTube-scroll freeze #16634 (15 Nov). Prefer headless for a non-visual run.

Set remote.prefs.recommended=false

So Gecko testing prefs do not silently change autofill/update behaviour (Zen DevTools MCP README, undated). Also check about:policies for DisableDeveloperTools (Fx160, 10 Nov 2026).

Session-store interval → 60000 ms

From the 15000 ms default, to cut disk/CPU churn without losing more than ~1 min of state on crash. Low-authority source (~26 Oct 2026) — test it.

Strip UI overhead

No Mods/Boosts, no gradient themes, zen.theme.gradient=false, ui.prefersReducedMotion=1. Community gist, undated — lowest evidence, lowest risk.

Disable OS suspend for the run

Zen blocking sleep was fixed Sep 2026 (older); the OS suspending an idle headed session is now the risk. Use systemd-inhibit or disable suspend/screen-lock.

Launch + profile config — copy and go

Use a dedicated profile. If Zen is already running with the same profile, a second launch only opens a new window and the automation flags are ignored (Mozilla Firefox DevTools MCP README, undated).

Copy
MOZ_ENABLE_WAYLAND=1 zen --new-instance -P r3l3 \
  --marionette --remote-debugging-port

# Headless variant (avoids the Wayland compositor entirely):
# zen --new-instance -P r3l3 --headless --marionette --remote-debugging-port

# Marionette port: 2828 (default)
# BiDi: WebSocket on the --remote-debugging-port value you pass

Sources: Zen DevTools MCP — https://github.com/simon-ami/zen-devtools-mcp (undated, verified 24 Nov 2026) · Firefox CLI docs — https://firefox-source-docs.mozilla.org/browser/CommandLineParameters.html (undated)

Copy
// user.js — R3-L3 dedicated profile
user_pref("remote.prefs.recommended", false);
user_pref("marionette.enabled", true);

// Protect the run tab — replace with the real run URL(s)
user_pref("zen.tab-unloader.excluded-urls", "https://YOUR-RUN-URL.example");
user_pref("browser.tabs.unloadOnLowMemory", true);
user_pref("browser.tabs.min_inactive_duration_before_unload", 360000000); // 100 h

// Session store: 60 s instead of 15 s; restore on restart
user_pref("browser.sessionstore.interval", 60000);
user_pref("browser.startup.page", 3);
user_pref("browser.sessionstore.resume_from_crash", true);

// Reduce background churn (community gist, undated — test first)
user_pref("browser.newtab.preload", false);
user_pref("media.suspend-bkgnd-video.enabled", true);
user_pref("network.predictor.enabled", false);
user_pref("zen.theme.gradient", false);
user_pref("ui.prefersReducedMotion", 1);

// Debug only — verbose:
// user_pref("remote.log.level", "Trace");

Caveats: browser.startup.page=3 + restore prefs are standard Firefox prefs, not Zen-verified in-window. browser.sessionstore.max_resumed_crashes defaults to 1 — a 2nd consecutive crash shows about:sessionrestore and can block automation. After the run, reset signon.autofillForms / signon.rememberSignons if left false.

Do not set app.update.disabledForTesting=false — it re-enables auto-updates and “updates may interrupt your session” (Zen MCP README, undated). Leave the automation default in place and pin 1.24.3b. Exact Zen app.update.* defaults in 1.24.3b were not confirmed by an in-window primary source.

What 1.24.3b actually fixes

All items below: Zen release notes, 17 Nov 2026, verified live 24 Nov 2026 — https://zen-browser.app/release-notes/ — unless noted.

Zen 1.24.3b — 17 Nov 2026
Closed browser/popup windows never freed from memory (gh-16587) — memory and pauses grew over time. The headline fix for R3-L3.
Split-view / Glance tabs unloaded under memory pressure (gh-16624) — fixed.
Faster new-window opening with mods installed (gh-16674); gradient-space switching no longer choppy (gh-13029).
Inherits Firefox 160.0.1: ChatGPT tab crashes, slow links (Google Store), WebTransport datagrams after burst, trackpad-swipe scrolling.
Firefox 160.0.1 — 17 Nov 2026
Incorrect colours in WebGL/canvas on some Linux Wayland systems — games, Google Meet backgrounds (Bug 2089043).
Tabs crashing, most notably ChatGPT (Bug 2088486); slow links (2087787); WebTransport (2092532); swipe scrolling (2086786).
Thin PDF lines printing as black boxes (2091728); blank PDF/WebGL on AMD Macs (2091596).
MFSA 2026-130 (high, 17 Nov 2026): CVE-2026-130020 Canvas/WebGL privilege escalation (Android); CVE-2026-130021 Audio/Video use-after-free (Bug 2088644).

Source: https://www.firefox.com/en-US/firefox/160.0.1/releasenotes/ · https://www.mozilla.org/en-US/security/advisories/mfsa2026-130/

Also in-window, for context
1.24.2b (11 Nov 2026): Firefox 160.0, MFSA 2026-125; PiP speed 0.25–2.0×; fixed multi-second freeze on NTLM/Kerberos sign-in; first character lost in urlbar; simultaneous downloads never finishing.
1.24b (28 Oct 2026): memory growing rapidly with Zoom web app in a minimised window; excessive memory on Linux+AMD viewing map/place results; tabs detaching into a new window on Linux/Wayland; cross-space tab routing freeze (gh-14171).
Firefox 160.0 (10 Nov 2026): Mini Window, PiP speed, MKV (FLAC/MP3/PCM) playback, Metal WebGL on macOS.
Note: Little Zen mini-windows and Zen’s own settings window are Twilight (pre-release) only in the 17 Nov notes — not in stable 1.24.3b. Do not depend on them.
Automation reality check — BiDi, not CDP
FACT	DATE	SOURCE
CDP removed in Firefox 141 (Bug 1882096); remote.active-protocols also removed. --remote-debugging-port now serves a BiDi WebSocket only; /json/* returns 404.	22 Jul 2025 — OLDER, decisive	MDN Firefox 141
Firefox 160 BiDi changes: CDDL for moz: extensions (2057588); script.message fix for window.open preload scripts (2079905); network events stop computing unused security details — “could have visible impacts on performance, e.g. during a page load” (2075175); runtime.PlatformInfo.arch now arm64 (2080310); windowId on runtime.MessageSender (2072133).	10 Nov 2026	MDN Firefox 160
Puppeteer 25.18.0 rolls to Firefox 160.0; BiDi fixes for goBack/goForward signals, permission-override reset, RemoteException.	17 Nov 2026	pptr.dev CHANGELOG
Drivers that fit this stack: Puppeteer-over-BiDi, Playwright-Firefox, Selenium/geckodriver, Mozilla firefox-devtools-mcp, Zen fork zen-devtools-mcp. Both MCPs need --marionette + --remote-debugging-port together; Marionette port defaults to 2828.	Undated READMEs, retrieved Nov 2026	zen-devtools-mcp · firefox-devtools-mcp
Zen MCP caveats: BiDi console/network events are not available in --connect-existing mode; Marionette sets navigator.webdriver=true (bot-detection risk); --enable-privileged-context needs MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1.	Undated, verified 24 Nov 2026	zen-devtools-mcp
Firefox 160 Enterprise: DisableDeveloperTools can now disable BiDi + Marionette without a restart. Check about:policies before the run.	10 Nov 2026	Firefox Enterprise 160 notes

Wayland check: about:support → Window Protocol should read wayland, not xwayland; Compositing should be WebRender. MOZ_ENABLE_WAYLAND=1 forces native Wayland (guide ~16 Oct 2026, older).

Settings reference

Recommended values, with evidence strength. “Undated” means the source was retrieved 24 Nov 2026 but carries no publication date — treat those values as candidates to test, not verified 1.24.3b recommendations.

SETTING	VALUE	WHY / EVIDENCE
zen.tab-unloader.excluded-urls	Run URL(s), comma-separated	Exempts the run tab from unloading. Zen docs, undated.
browser.tabs.unloadOnLowMemory	true on Linux	May be required for the native unloader to work at all (Discussion #9087, undated). Keep headroom so it never fires on the run tab — prefer exclusion + headroom over false, which removes the OOM safety net.
browser.tabs.min_inactive_duration_before_unload	360000000 ms (100 h) to effectively prevent eligibility; default 600000 ms	Minimum inactivity before a tab is considered; actual unload still needs memory pressure. Discussion #9087 + user.js, undated.
browser.sessionstore.interval	60000 ms	Default 15000 ms causes frequent disk writes / CPU spikes. Do not use 300000 ms if crash recovery matters. DEV tuning, ~26 Oct 2026, low authority.
remote.prefs.recommended	false	Skips Gecko testing prefs for a closer-to-regular Zen instance. Zen MCP README, undated.
dom.ipc.processCount	Leave default (8)	Community gist suggests 2–4, but that trades responsiveness and crash isolation. Gist, undated.
browser.newtab.preload · media.suspend-bkgnd-video.enabled · network.predictor.enabled	false · true · false	Background-churn reductions. Community gist, undated, unverified.
MOZ_ENABLE_WAYLAND · MOZ_REMOTE_ALLOW_SYSTEM_ACCESS	1 · 1 only if privileged tools needed	Native Wayland (headed); privileged context gate. Wayland guide older; MCP README undated.
Avoid — do not set for this run
AVOID	REASON
app.update.disabledForTesting=false / app.update.auto=true	Re-enables updates mid-run. Pin the version instead.
zen.tab-unloader.timeout-minutes	Pref no longer exists — setting it does nothing. Zen’s timed unloader was replaced by Firefox’s native memory-pressure unloader; monitor at about:unloads.
Any CDP client / connectOverCDP / /json/list	CDP removed in Firefox 141. Use BiDi + Marionette.
Re-using the everyday profile while Zen is already running	Automation flags are ignored; only a new window opens. Use a dedicated profile with --new-instance.
Blanket hardware-acceleration disable	Community gist suggests it for battery (undated), but on Wayland/Linux it forces software WebRender, raises CPU, and can worsen video/WebGL. Use only as a diagnostic for the RDD/WebRender crashes below.
gfx.webrender.all=true / layers.acceleration.force-enabled=true	Older forcing advice, no in-window verification, risky on Nvidia/proprietary drivers.
Safe Mode as the recovery path	#16694 (18 Nov 2026): safe mode never opens a window and keeps the profile lock on Linux/Wayland.
Risks to watch — open issues, 15–20 Nov 2026

From the zen-browser/desktop issues index (titles + dates only; bodies were not opened — treat as signals, not confirmed reproductions on R3-L3 hardware). Full list: https://github.com/zen-browser/desktop/issues

HIGH RDD process SIGSEGV → browser self-kills

#16718 · 20 Nov 2026 — RDD SIGSEGV in system libavutil av_buffer_unref, browser self-SIGKILLs several times/day (GTX 1660Ti, Wayland).

Mitigation: avoid video-heavy workloads; prefer --headless if headed UI is not needed; log coredumpctl / RDD crashes.
HIGH Memory exceeding installed RAM

#16685 · 17 Nov 2026 — “Zen using more memory than my machine even has.” Reported the same day as the 1.24.3b leak fix; unresolved, title only.

Mitigation: RSS watchdog every 5–15 min (see Watchdog plan); one window, low tab count, no popups; planned restart at a checkpoint.
MED Window stops rendering after resize

#16706 · 19 Nov 2026 — window stops rendering after resize while a game runs [Linux/Wayland]. Also: floating search bar laggy after 1.24.2b (#16671, 17 Nov); search stutter with background video (#16710, 19 Nov).

Mitigation: set viewport at launch and never resize/move the window mid-run.
MED Video on Wayland: frame drops & freezes

#16690 · 17 Nov — ~46% of video frames dropped on HLS/MSE (Chrome drops 0% on same hardware). #16696 · 18 Nov — playback fails when seeking forward. #16634 · 15 Nov — AppImage 1.24.2b freezes scrolling YouTube.

Mitigation: keep HLS/YouTube-scroll/WebGL-game loads off the run tab if the run allows it.
MED Safe mode holds the profile lock

#16694 · 18 Nov 2026 — safe mode never opens a window and keeps the profile lock (Linux/Wayland).

Mitigation: never use Safe Mode for automated restart. Watchdog checks for a stale .parentlock / lock and removes it only after confirming no zen process is alive.
MED Mid-run update — Firefox 161 is out

Firefox 161.0 released 24 Nov 2026; Zen rebase imminent. Related: “Zen updates not showing” #16686 closed 17 Nov; spaces disappearing on startup #16515 closed 18 Nov; ghost/frozen tab breaking other tabs #16715, 19 Nov.

Mitigation: pin 1.24.3b, verify version before launch, ignore update toasts, use a single workspace, snapshot tab URLs externally every few minutes.

Bot detection: Marionette sets navigator.webdriver=true (Zen MCP README, undated) — expect Cloudflare/Akamai challenges on some sites. Use the dedicated run profile only; do not browse normally with it. ChatGPT tabs: the crash fix (Bug 2088486) is only in 1.24.3b — if the run uses ChatGPT, treat that tab as highest-risk and snapshot its state externally.

Watchdog plan for 19–31 hours

Analyst recommendations built on the risks above — no source gives a multi-hour stability guarantee for BiDi/Marionette (see Open questions), so assume disconnects will happen and rehearse recovery.

Before launch

Verify: version = 1.24.3b / Fx 160.0.1 · about:support shows wayland + WebRender (if headed) · about:policies has no DisableDeveloperTools · dedicated profile, single workspace, window size set · OS suspend disabled / systemd-inhibit active.

Every 30–60 s

Heartbeat: BiDi session.status / Marionette TCP 2828 + a trivial evaluate. On disconnect: reconnect with backoff; relaunch the browser if reconnect fails twice. Log every disconnect with a timestamp.

Every 5–15 min

Health: poll zen RSS + about:memory / about:processes; check the run tab is still loaded (title/URL/evaluate) and check about:unloads; snapshot the list of open tab URLs externally.

Threshold

Restart trigger (recommendation — no source gives one): RSS above ~60–70% of system RAM, or sustained growth, triggers a planned restart with session restore (browser.startup.page=3) at a checkpoint — not a crash recovery.

On failure

Recover: confirm no zen process is alive before clearing a stale profile lock; never launch a second instance on the same profile; never use Safe Mode; reopen from the external URL snapshot if Spaces state is lost.

Open questions — could not verify
BiDi / Marionette stability over many hours: no in-window source measures disconnect rates or reconnect behaviour on Zen 1.24.3b / Firefox 160. Do not assume a single BiDi session survives 19–31 h — the watchdog above is a precaution, not a sourced guarantee.
Issue bodies not read: #16685, #16718, #16706, #16690, #16694 and others are titles + dates from the Pulse/issues index (crawled ~20 Nov 2026) only. Severity, hardware, and workarounds in the bodies were not verified.
Exact Zen app.update.* defaults in 1.24.3b and whether Zen’s updater respects app.update.auto=false: no in-window primary source; the disabledForTesting note is from the undated Zen MCP README.
Headless vs headed, Wayland vs XWayland for 19–31 h: no in-window comparative data. Preferring headless is inferred from the headed-Wayland crash reports, not from a headless long-run test.
Zen on Firefox 161: Firefox 161.0 was released 24 Nov 2026, but no Zen 1.24.4b / 1.25 build had been published as of this research.
zen.tab-unloader.enabled=false in 1.24.3b: the exclusion pref is still in Zen docs (retrieved 24 Nov), but whether enabled=false still works was not verified live in the browser.
Confidence note — how to read this report
Sources — with dates
Zen official release notes — https://zen-browser.app/release-notes/ — verified live 24 Nov 2026 (1.24.3b 17 Nov, 1.24.2b 11 Nov, 1.24b 28 Oct 2026)
Firefox 160.0.1 release notes — https://www.firefox.com/en-US/firefox/160.0.1/releasenotes/ — 17 Nov 2026, verified live 24 Nov 2026
MFSA 2026-130 — https://www.mozilla.org/en-US/security/advisories/mfsa2026-130/ — announced 17 Nov 2026, impact high
MDN Firefox 160 for developers — https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/160 — 10 Nov 2026
MDN Firefox 141 (CDP removal) — https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/141 — 22 Jul 2025, OLDER
Firefox Enterprise 160 notes — https://firefox-admin-docs.mozilla.org/release-notes/version/firefox-160/ — 10 Nov 2026
Zen GitHub Pulse / Issues — https://github.com/zen-browser/desktop/pulse · https://github.com/zen-browser/desktop/issues — index crawled ~20 Nov 2026
Zen Discussion #9087 (tab-unload timer removed) — https://github.com/zen-browser/desktop/discussions/9087 — verified live 24 Nov 2026, date not shown
Zen docs, Hidden/Advanced Preferences — https://docs.zen-browser.app/guides/about-config-flags — verified live 24 Nov 2026, undated
Zen DevTools MCP — https://github.com/simon-ami/zen-devtools-mcp — verified live 24 Nov 2026, undated
Mozilla Firefox DevTools MCP — https://github.com/mozilla/firefox-devtools-mcp — retrieved Nov 2026, undated
Puppeteer changelog 25.18.0 — https://pptr.dev/CHANGELOG — 17 Nov 2026
PiunikaWeb, Zen 1.24.3b — https://piunikaweb.com/2026/11/19/zen-browser-1-24-3b-update-memory-leak-chatgpt-fix/ — 19 Nov 2026
LinuxCompatible, Zen 1.24.3b — https://www.linuxcompatible.org/story/zen-browser-1243b-release-security-fixes-chatgpt-crash-fixes/ — Nov 2026
Firefox 161 release — https://endoflife.date/firefox (updated 24 Nov 2026) · https://www.omgubuntu.co.uk/2026/11/firefox-161-released-vpn-classic-themes (updated 2026-11-24)
Firefox Source Docs, Command Line Parameters — https://firefox-source-docs.mozilla.org/browser/CommandLineParameters.html — verified live 24 Nov 2026, undated
Firefox Source Docs, Tab Unloading — https://firefox-source-docs.mozilla.org/browser/components/tabbrowser/docs/tab-unloading.html — retrieved Nov 2026, undated
Zen community performance gist — https://gist.github.com/omniscientpolymath/ae1a5579b3584ae3f5d865c0f760a2ae — verified live 24 Nov 2026, undated, community only
Firefox performance tuning (DEV) — http://dev.to/weatherclockdash/firefox-performance-tuning-making-firefox-faster-on-any-hardware-4k0h — ~26 Oct 2026
Firefox on Wayland (DEV) — https://dev.to/weatherclockdash/firefox-on-wayland-native-support-va-api-screen-sharing-via-pipewire-20ja — ~16 Oct 2026, OLDER
Built for the R3-L3 run starting 25 Nov 2026 from research dated 25 Oct – 24 Nov 2026. Every value above carries its source and date from that research; hedges and “not verified” flags are preserved, not smoothed over. Test the undated prefs on the run profile before the real run.
