# Council-2 Cloudflare fix: live-test evidence log

- Date: 2026-11-26 (Asia/Ho_Chi_Minh). Role: COUNCIL-2 (Cloudflare fix), R3-L3 re-plan. Run PAUSED by owner order.
- Scope: Zen-AI Cloudflare Turnstile wall (coolors.co, chatgpt.com), bot-wall class (R3-011 timeanddate, R3-022 Google sorry, R3-024 Openverse, R3-026 coolors).
- Rules followed: no em dashes or en dashes; English only; pill on every agent control (label "Computer use active"); one driver at a time on the shared Zen; owner tabs never closed or navigated (one leaked test tab of mine, google.com from round 2, closed at cleanup); ws3 untouched; no ydotool; SSH only via ~/workspace/ssh-laptop.sh; long jobs detached with setsid nohup; Zen never restarted; no launcher, wrapper, or pref changes; temp profiles deleted after use.
- Ponytail rule for all code work: smallest complete change, reuse before writing, standard library/platform before dependencies, no unrequested abstraction, one small test for non-trivial logic, never cut validation/security/error handling.
- Raw logs and screenshots: improvements/council2-evidence-raw/ (run.log, run2.log, run3-preload.log, run4-preload.log, run4-baseline.log, run5.log, run6-stock.log, plus SERP and landing images). Harness: improvements/council2-harness/ (bidi_test.mjs, bidi_userway.mjs, holder.mjs, bidi_round5.mjs, run_tests.py, run_round2.py, run_round3.py, run_round4.py, run_round5.py, stock_retry.py). Laptop copies at /tmp/council2-harness/ and /tmp/council2-evidence/.

## Timeline (all times +07)

- 04:40:56 task received. Read prior research doc in full (zen-cloudflare-chatgpt-fix-research-20261125.md).
- 04:41 state check: in-flight R3-025 drive + R3-026 scoring running (task_start 04:39:00). Live tests held. Research phase first.
- 04:41:16 daemon send to mei run 32 (last30days crawl request), outcome=sent verified=True. Run number re-verified from daemon.log (last mei run 31 at 04:38:00).
- 04:41:19 daemon send to mochi run 233 (last30days crawl request), outcome=sent verified=True. Run number re-verified (last mochi run 232 at 04:38:07).
- 04:41 to 04:43 web research (plan file section 2).
- 04:50:09 state file: task_start cleared, R3-025 sealed. Live tests cleared to start.
- 04:54:42 round 1 runner start. Pill acquired 04:54:43 (holder Council-2, method BiDi test, label "Computer use active", visible true).
- 05:01:52 round 1 done, pill released (visible_after false).
- 05:03 round 2 (user-way via BiDi input) launched. Failed: input.performActions invalid argument; leaked BiDi session blocked later sessions.
- 05:07 round 3 first launch failed: holder session.new "session not created" (leaked round 2 session). No Zen restart. Session reaped on its own by 05:10 (probe: session.status ready true).
- 05:10 round 3 preload relaunched (user-way via act-now real input + held BiDi preload).
- 05:14:24 round 3 done, pill released. Stock grim screenshots in round 3 captured the wrong surface (see failures).
- 05:15 round 4 preload launched (gated user-way, image-grounded clicks).
- 05:23 round 4 baseline coolors launched (contrast).
- 05:26 round 5 launched (descriptor tells + Google Translate direct + stock observe attempt).
- 05:31:45 round 5 done, pill released.
- 05:32 round 6 stock retry launched (mkdir profile dir first).
- 05:34:00 round 6 done.
- 05:35 cleanup: closed my one leaked google.com tab via BiDi; computer-use status ok.
- 05:36 milestone logged via ~/workspace/agent-event-log/log-event.sh.

## Round 1: direct navigation A/B in run Zen (BiDi, pill held)

Harness: bidi_test.mjs via run_tests.py. One BiDi session per mode, new tab, navigate, wait, evaluate, screenshot, close tab, end session.

- Baseline probe (data page): navigator.webdriver = true, own property on Navigator.prototype = true, own on navigator = false. Confirms the forced signal in the run Zen.
- Baseline coolors.co (direct): title "Just a moment...", body "Performing security verification... Ray ID: a603e4d349ac3dc3", challenge detected = true. BLOCKED. This reproduces the owner photo and the R3-026 block (epoch 8 Ray ID a603c518ed7945df).
- Baseline chatgpt.com (direct): redirected to Google account chooser (auth flow), no challenge in snapshot. Recorded as observed; the warm profile session cookie drives the redirect.
- Private user-context (browser.createUserContext, fresh context): webdriver still true; coolors BLOCKED (Just a moment); chatgpt real title, no challenge. Check 0a result: fresh context and cookies do not change the signal or the coolors outcome. Cookies and extensions ruled out as the cause, same as the 25/11 research.
- Preload (script.addPreloadScript, delete from prototype + defineProperty false on navigator): webdriver reads false on probe, coolors, and chatgpt. Coolors title "Coolors - The super fast color palettes generator!", no challenge. ChatGPT title "ChatGPT: Chat, Work, Create & Code with AI", no challenge. Candidate 3a PASSES both sites on direct navigation.
- Drive check in round 1: input.performActions returned "invalid argument" in all three modes (harness bug, Firefox BiDi pointer needs more than my payload). Recorded as a harness failure, not a product failure. Fixed in later rounds by using the runner lane (act-now) for real input.

## Round 2: user-way via BiDi input (FAILED, harness)

- baseline user-way: search box found on google.com, then input.performActions "invalid argument" at the first click. Fatal exit without session.end leaked the BiDi session.
- preload user-way: session.new "session not created" (leaked session). 
- Stock grim screenshots: rc=1, 0 bytes (detached process lacked WAYLAND_DISPLAY). Fixed in round 3 by exporting display env from the live Zen process.
- Lesson recorded: Firefox BiDi pointer/key input via raw performActions is not the working lane on this build; the runners use desktop input via computer-use act-now. Round 3 and 4 use that lane.

## Round 3: user-way via act-now + held preload (partial)

- Holder (holder.mjs) held one BiDi session with the preload shim and created the tab; run_round3.py drove real keyboard and mouse via computer-use act-now (Ctrl+L, type query, Return), then read state via holder RPC.
- Search step worked (DuckDuckGo SERP reached for coolors and chatgpt, webdriver false). Click step failed: act-now refused with "point outside observed image" because my screen-to-image conversion used mozInnerScreenX, which reads 0 on this build. Landings stayed on the SERP. Recorded as a grounding failure, fixed in round 4 by viewing the observe image and clicking in image coordinates with --observation.
- Stock screenshots in round 3 (grim full screen) captured the run Zen surface, not the stock window. Superseded by round 6 window observe.

## Round 4: user-way proof, image-grounded clicks (the proof round)

Method per Lauren Tan worked example and the owner hard rule: start in the held tab, Ctrl+L, type the query like a user, Return, observe the SERP, click the first result with real mouse input (act-now, image coordinates from visual grounding on the observe image), wait, read landing state via holder RPC, scroll (interact), re-read, observe again. Pill held for the whole run; observe images show "Computer use active".

Preload mode (shim installed, webdriver false at probe):
- coolors: SERP "coolors color palette generator at DuckDuckGo", clicked first result, landing title "Coolors - The super fast color palettes generator!", url https://coolors.co/, challenge false, webdriver false. After scroll: same, usable. PASS. Landing image viewed: real Coolors homepage with palettes, pill visible.
- chatgpt: landing title "ChatGPT: Chat, Work, Create & Code with AI", url https://chatgpt.com/, challenge false, webdriver false. PASS.
- timeanddate: landing title "The World Clock, Worldwide" (site title verbatim in raw log), url https://www.timeanddate.com/worldclock/, challenge false, webdriver false. PASS (R3-011 class).
- openverse: landing title "Openly Licensed Images, Audio and More | Openverse", url https://openverse.org/, challenge false, webdriver false. PASS (R3-024 class).
- All act-now batches rc=0 (search, click, scroll). Driving regression under the shim: real click navigated, scroll worked, screenshots captured. PASS.

Baseline mode (no shim, coolors only, same user-way):
- Landing: real Coolors homepage, challenge false, webdriver TRUE. PASS on the surface, but CONFOUNDED: the preload visits minutes earlier minted cf_clearance cookies in the same profile (verified by cookie name query after the run: cf_clearance present for .coolors.co, .chatgpt.com, .timeanddate.com, .openverse.org). A warm clearance plus real human-like input can pass even with webdriver true. The clean A/B contrast is round 1 (baseline blocked first, preload passed after, same profile, no clearance at baseline time). Round 4 baseline is recorded as confounded, not as evidence that baseline is fine.

## Round 5: descriptor tells + Google Translate (R3-022 class)

Direct BiDi, data-page probe, three modes:
- Baseline: webdriver true, own on prototype true, own on navigator false, getter name "get webdriver", getter toString "function webdriver() { [native code] }".
- Preload (delete + defineProperty): webdriver false, own on navigator TRUE, own on prototype false, getter name "get", getter toString "() => false". Two tells: own property on navigator, and a non-native getter body.
- Proxy (claude-for-zen pattern, Proxy around the native getter on the prototype): webdriver false, own on navigator false, own on prototype TRUE (same shape as baseline), getter name "get webdriver", getter toString "function () { [native code] }". Cleanest tell profile of the three. This is the shim variant the plan recommends.
- Google Translate (translate.google.com, direct): all three modes loaded the real page (title in Vietnamese, "Google Dich" in raw log), no /sorry/ redirect, no challenge at test time. The R3-022 sorry wall did not reproduce today in any mode; it is rate and IP based, not webdriver-value based. Recorded honestly: the shim neither fixes nor worsens Google sorry; the INVALID path remains for it.

## Round 6: stock launch decisive check 0b (no flags, fresh temp profile)

Method: /opt/zen-browser-bin/zen-bin --profile /tmp/zen-stock6-<tag> --no-remote <url>, profile dir pre-created (round 5 without mkdir showed "Profile Missing"; round 2 with -P showed the Profile Manager dialog; both recorded as harness failures). Window found via computer-use windows diff, observed with computer-use observe --window. Temp profiles deleted after each test. Pill held.

- Probe (data page): window title "Zen Browser", observe image shows the Zen first-run welcome screen ("Welcome to a calmer internet"); the data page sits behind onboarding, so webdriver value in stock was not read from the image. Limitation recorded: stock webdriver value is inferred false by construction (no remote agent flags), not directly read. A follow-up read via a local http page after dismissing onboarding is listed in the plan as a redteam check.
- coolors.co (direct): window title "Just a moment..." BLOCKED even with no automation flags on a cold profile.
- chatgpt.com (direct): window title "ChatGPT: Chat, Work, Create & Code with AI" PASSED with no flags on a cold profile.
- Interpretation: the flags are not the sole cause of the coolors block. On a cold profile with no clearance and no behavioral history, coolors challenges even stock Zen on direct navigation. In the warm run profile, round 1 proves the webdriver signal is a real contributor (baseline blocked, preload passed, same profile, same network, minutes apart). Both facts stand; the plan does not claim flags are the only cause.

## Failures and harness bugs (all recorded, none hidden)

1. Round 1 drive click: BiDi input.performActions invalid argument (all modes).
2. Round 2: same input failure plus leaked BiDi session blocking session.new for about 9 minutes; reaped on its own, no Zen restart.
3. Round 2 stock grim: rc=1 (missing WAYLAND_DISPLAY in detached env).
4. Round 3 click grounding: mozInnerScreenX reads 0; act-now refused "point outside observed image".
5. Round 3 stock grim: captured the wrong surface (run Zen in front).
6. Round 5 stock: "Profile Missing" dialog (profile dir not pre-created).
7. Round 2 stock with -P: Profile Manager dialog (Zen build wants --profile <dir>).
8. SSH banner timeouts twice (transient, retried).
9. Round 4 baseline coolors pass is confounded by cf_clearance minted in the preload visits (cookie names verified).

## What was NOT changed

No launcher, wrapper, pref, or profile changes. No Zen restart. The only writes to the laptop: /tmp/council2-harness/, /tmp/council2-evidence/, /tmp/council2-rpc/, /tmp/council2-gate/, temp stock profiles under /tmp (deleted), observe cache images under ~/.cache/agent-computer-use/ (tool-owned), and cf_clearance cookies minted by normal site visits in the run profile. One leaked test tab (google.com) closed at cleanup. Pill released after every round (visible_after false each time).
