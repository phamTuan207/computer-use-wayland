# F3 proof record: Cloudflare Proxy shim, cookie-cleared user-way (2026-11-26)

- Date: 2026-11-26. Role: F3 PROVER. I did not implement Fix B. I ran the prover runbook in replan-fixes-cloudflare-live-20261126.md section 7 cold, as a Muse subagent lane session owner.
- Run state: R3-L3 PAUSED, epoch 9 holds. Nothing in this file resumes the run, edits coordinator state, releases any run task, or commits anything. No message was sent to the owner or parent by the prover. Milestones were logged via log-event.sh with source replan-f3-prover.
- Evidence: improvements/f3-evidence/ (prover files listed in section 10, with sha256 list in sha256-f3-prover.txt). Copies also placed in improvements/fixb-evidence/prover/ per runbook cleanup. Laptop copies remain at /tmp/f3-evidence/ and /tmp/fixb-runner/ (runner kept, rpc and gate dirs removed after evidence copy).
- Rules followed: no em dashes or en dashes in text authored here (commas, periods, short hyphens only; raw site and tool text inside evidence logs is exempt and noted where it matters); English only; pill on every agent control with label Computer use active; one driver at a time on the shared Zen; owner tabs never closed or navigated; ws3 untouched; drives on ws2; no ydotool (ydotool is banned, restate the ban in every brief, never assume it); SSH only via ssh-laptop.sh with short commands, long drives detached with setsid nohup; Zen never restarted; no launcher, wrapper, or pref changes; full access; ponytail for code (smallest complete change, reuse the holder as-is, no new framework; the only new code is drive-prover.py, modeled on drive-fixb.py, see section 2).
- User-path test: enter via search or homepage and click through like a normal user; no deep links, no direct commands, no internal setters; evidence shows entry, path, action, and resulting state. End-state-only evidence is returned unread by the coordinator; none is filed here.
- User entry point for every site check: held blank tab, Ctrl+L, type the query, Return, click the first result on the SERP.
- Forbidden shortcuts for every site check: deep link, BiDi navigate to the target, internal setters, test-only endpoints, DOM click, warm-profile reuse without the cookie clear, uncleared-cookie retries.
- Named search engine: DuckDuckGo, reached by typing the query in the Zen address bar and pressing Return. Every SERP host read back as duckduckgo.com. No engine switch.
- Queries: runbook section 7 queries were used (coolors color palette generator, chatgpt, timeanddate world clock, openverse free images). The task brief shorthand (coolors, chatgpt, timeanddate, openverse) is recorded here for the coordinator; the runbook wording was followed exactly as ordered.
- No-waive rule honored: the one bot-wall failure below is recorded as FAIL with Ray ID, screenshots, webdriver read, and elapsed. No retry with cookies uncleared was run. No harness retry was needed (all grounding first-try, all act-now rc 0).

## 1. Verdict summary

Gate verdict: FAIL. The gate stays closed on the Zen lane. One required fresh-session repeat failed cookie-cleared user-way. The coordinator decides the fallback (Chromium or Brave lane per task with scorer agreement, or INVALID path). The prover does not waive.

| Check | Clear | Probe | SERP | Click | Landing usable | webdriver false | Interaction | Pill in images | Result |
|---|---|---|---|---|---|---|---|---|---|
| coolors.co (first) | PASS 6 to 0 | PASS | PASS | PASS | PASS | PASS | PASS generator opened | PASS, see note A | PASS |
| chatgpt.com (first) | PASS 81 to 0 | PASS | PASS | PASS | PASS | PASS | PASS typed, not sent | PASS | PASS |
| timeanddate.com | PASS 11 to 0 | PASS | PASS | PASS | PASS | PASS | PASS scroll | PASS, see note A | PASS |
| openverse.org | PASS 4 to 0 | PASS | PASS | PASS | PASS | PASS | PASS image opened | PASS, see note A | PASS |
| coolors.co (fresh repeat) | PASS 6 to 0 | PASS | PASS | PASS | FAIL challenge | PASS false | FAIL blocked | PASS | FAIL |
| chatgpt.com (fresh repeat) | PASS 16 to 0 | PASS | PASS | PASS | PASS | PASS | PASS typed, not sent | PASS | PASS |
| Descriptor probe | n/a | PASS, toString difference recorded | n/a | n/a | n/a | PASS | n/a | n/a | PASS with accepted risk |
| Driving regression | n/a | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| Revert verify | n/a | PASS true restored | n/a | n/a | n/a | PASS | n/a | n/a | PASS |

Note A, pill readability, stated plainly: every drive log records pill_acquired visible true with label Computer use active, and every SERP image plus every dark-page image shows the pill text clearly at top center. Three light-background captures (coolors landing, timeanddate landing and interacted, openverse landing) show the pill bar at top center with faint text that is hard to read in the JPEG. The bar is visible; the text is faint. Independent overlay status reads after each drive show visible false with holders empty, and pill acquire and release are clean in all 6 drives. The coordinator can judge note A from the images; the prover does not upgrade faint text to clear text.

What the coolors split means, without speculation beyond the evidence: the first cookie-cleared coolors check passed end to end, and the fresh-session repeat with cookies cleared again hit a Cloudflare managed challenge with webdriver still false. Cookie clearing alone therefore does not make the shim reliable cold on coolors.co in this profile. Both attempts stay in evidence. No third attempt was run.

## 2. Setup (once)

- Pause holds: coordinator state current_task reads PAUSED at pause point, epoch 9 deputy recorded. No run task was released by the prover.
- SSH note: the first SSH attempts at 06:03 to 06:04 +07 failed with proxy closed connection (5 consecutive short attempts). Retries at 06:05:49 and 06:06:38 succeeded. Transient outage, recorded in setup-baseline.log. All later SSH calls were short commands; drives ran detached on the laptop.
- Machine free at 06:07 +07: computer-use status ok; Zen window address 0x5614f01a0e20, class zen, workspace 2 (verified live, re-verified before the coolors drive, never assumed); ports 127.0.0.1:9222 and 127.0.0.1:2828 LISTEN (zen-bin pid 578117); overlay holders empty, visible false; cursor lock free by /proc fd scan; no holder, drive, or probe processes left from Fix B. Zen environ keys present: WAYLAND_DISPLAY, XDG_RUNTIME_DIR, DBUS_SESSION_BUS_ADDRESS, HYPRLAND_INSTANCE_SIGNATURE. DISPLAY absent in Zen environ; drives exported the present keys only and recorded the absence.
- Harness files on laptop, sha256 readback matches runbook section 7 step 2, no transfer needed: holder-fixb.mjs 70bfe8abbed9fdbec30a2cf323c61150322048ce2736dfe26186a1c075d4f213, probe-fixb.mjs 5329a574c7c7de6b003ad967d9706e75e589ce60c388f7a07f39f12dcf15c1f9, drive-fixb.py 6af74f2a4e03745504e9e9520019a9e5e097e943707ad01fe226c43e90d79f45. Shim string inside holder-fixb.mjs verified on the VM copy: 316 bytes, sha256 bb49ff3f974a0534445fa5bb8eac48b47a378f39d944706b10118d5ff9d630b8, matching the pinned hash. The holder also checks the hash at startup (shim_pinned in every holder log).
- Prover driver: drive-prover.py, sha256 14348b3b5e5692e1706f83e1ae893e5839d3fec89fc6d4cb930e1016db85c712, identical on VM and laptop after base64 transfer, py_compile OK on both. It reuses the holder, pill, act-now, and RPC shape from drive-fixb.py. Differences are listed in its header: argv parameters, agent name Prover, SERP host enforcement, second gate for the interact step, per-tag logs under /tmp/f3-evidence. Holder and probe files were used as-is with no edits.
- Image transfer: base64 over SSH with sha256 readback, one call per image, verified first on a Fix B observe image (hash matched). Every prover image hash below was verified the same way.
- Baseline probe at 06:07:03 to 06:07:08 +07, node probe-fixb.mjs probe, no shim: webdriver true, own_on_proto true, own_on_navigator false, get_name get webdriver, native toString form. PASS. Full lines in setup-baseline.log. No leaked session; driving was allowed to proceed.

Timing convention: wall-clock is Asia/Ho_Chi_Minh. Drive elapsed_s in drive logs starts at drive_start and includes coordinator grounding gate waits (image fetch, viewing, grounding, coords write). Landing elapsed_s is the cleaner drive-action measure. Both are given per site.

## 3. coolors.co, first check: PASS

- Cookie clear (cookies-coolors.log): before 6 (cf_clearance present, 2 entries, domain .coolors.co), delete 6 to 0, independent re-read 0. PASS. Logged via log-event.sh at 06:08:20 +07.
- Drive: start 2026-11-26T06:08:35+07:00, done elapsed 105.2s including gates; landing at elapsed 57.3s. Holder session cfa7c456-e9ce-4916-823d-051e071dd378, probe webdriver false, own_on_proto true, own_on_navigator false, get_name get webdriver, shim sha256 bb49ff3f...630b8. Pill acquired visible true.
- Entry and path: Ctrl+L, type coolors color palette generator, Return. SERP title coolors color palette generator at DuckDuckGo, url on duckduckgo.com. SERP image serp-coolors.jpg (sha256 ec23d2254d38d911671cff54aebe6db99560cc4920f3b78a15d3d666ccea6cea) shows the pill text clearly and first result Coolors on coolors.co. Grounding normalized point 345, 190; image pixels 331, 116 on the 960 by 609 observe image. Coords written atomically at 06:09:14 +07. Preclick re-observe, act-now click rc 0.
- Landing: url https://coolors.co/, real site title (Coolors, the super fast color palettes generator), webdriver false, has_cf_challenge false. Landing image landing-coolors.jpg (sha256 54aa47bec7050936ef7b19c2252fcd75edd39ce878f6c5c09c532d854b9763a9) shows the usable homepage; pill bar visible at top center with faint text (note A).
- Interaction: Start the Generator button grounded at normalized 263, 541, pixels 252, 329; act-now click rc 0. After state url on coolors.co with a palette path, title Create a Palette - Coolors, webdriver false, no challenge. Interacted image interacted-coolors.jpg (sha256 4d240ee3c0ff01c2d2d6934e4609a06b65697a1243a5f10bfcad372b163cb557) shows the generator with palette colors and the pill text clearly. Drive verdict landed_ok true. Holder preload_removed, context_closed, session_ended, done. Overlay visible false after.
- Sub-checks: clear PASS, probe PASS, SERP PASS, click PASS, landing usable PASS, webdriver false PASS, interaction PASS, pill PASS with note A. Result PASS. Logged at 06:11:12 +07.

## 4. chatgpt.com, first check: PASS

- Cookie clear (cookies-chatgpt.log plus cookies-chatgpt-delete-raw.log): before 81 (cf_clearance present, 3 entries, domain .chatgpt.com, plus __cf_bm, _cfuvid, and sign-in session cookies), delete 81 to 0, re-read 0. PASS. Deleting chatgpt.com cookies removes the sign-in session in this profile; expected for the gate and recorded. Logged at 06:11:31 +07.
- Drive: start 2026-11-26T06:11:45+07:00, done elapsed 106.0s; landing at elapsed 62.2s. Probe webdriver false with matching shape. Pill acquired visible true.
- Entry and path: query chatgpt. SERP title chatgpt at DuckDuckGo on duckduckgo.com. SERP image serp-chatgpt.jpg (sha256 8e6794f39a53f7107f536252d3b94c1d27d3944d51ffd3f045a812551f04acd7) shows the pill text clearly and first result ChatGPT on chatgpt.com. Grounding normalized 241, 188; pixels 231, 114. Coords written 06:12:29 +07. Click rc 0.
- Landing: url https://chatgpt.com/, real site title (ChatGPT: Chat, Work, Create and Code with AI), webdriver false, has_cf_challenge false, no Just a moment, no Verify you are human. Landing image landing-chatgpt.jpg (sha256 d9f88402d5094a483d72afe78e682570bdc0d504e15a33b5b192b919555f403e) shows the logged-out page with the Ask ChatGPT prompt box and the pill text clearly.
- Interaction: prompt box grounded at normalized 632, 496, pixels 607, 302; click plus type hello with no Enter (nothing sent). After state same url and title, webdriver false, no challenge. Interacted image interacted-chatgpt.jpg (sha256 1111e4e736670db044d6936eb3553faa0b4d36f51e246d0b6ba2ef65321cac40) shows hello in the box, unsent, pill text clearly. Verdict landed_ok true. Holder ended clean, overlay false after.
- Sub-checks: all PASS. Result PASS. Logged at 06:14:16 +07.

## 5. timeanddate.com: PASS

- Cookie clear (cookies-timeanddate.log): before 11 (cf_clearance present, 2 entries, domain .timeanddate.com), delete 11 to 0, re-read 0. PASS. Logged at 06:14:35 +07.
- Drive: start 2026-11-26T06:14:43+07:00, done elapsed 104.8s; landing at elapsed 64.7s. Probe PASS, pill visible true.
- Entry and path: query timeanddate world clock. SERP on duckduckgo.com. SERP image serp-timeanddate.jpg (sha256 ae8e39f3b96bbf6a58fc2fb6a822916b2218bf2d5f962223a3b800d78d4f9178) shows the pill text clearly and first result The World Clock on www.timeanddate.com. Grounding normalized 346, 190; pixels 332, 116. Coords written 06:15:29 +07. Click rc 0.
- Landing: url https://www.timeanddate.com/worldclock/, real world clock title (raw site title contains an em dash; the literal title is preserved in drive-timeanddate.log as raw site text, exempt, and is not reproduced with a long dash here), webdriver false, has_cf_challenge false. Landing image landing-timeanddate.jpg (sha256 c26c12e9bcd2fe77533030aa4e6aa348a92c745c7d71540857f1f7a55e42f3bd) shows world clock content including Hanoi time; pill bar visible with faint text (note A).
- Interaction: scroll per runbook (gate2 skip written 06:16:18 +07), act-now scroll rc 0. After state same url, webdriver false, no challenge. Interacted image interacted-timeanddate.jpg (sha256 bc0d27de7dbcb1343913d116efd18055629c2fcf49138d354b7988240f5a7ab1) shows the scrolled city list; pill bar faint (note A). Verdict landed_ok true. Holder clean, overlay false after.
- Sub-checks: all PASS with note A. Result PASS. Logged at 06:17:10 +07.

## 6. openverse.org: PASS

- Cookie clear (cookies-openverse.log): before 4 (cf_clearance present, 2 entries, domain .openverse.org, plus ui), delete 4 to 0, re-read 0. PASS. Logged at 06:17:28 +07.
- Drive: start 2026-11-26T06:17:36+07:00, done elapsed 110.0s; landing at elapsed 64.9s. Probe PASS, pill visible true.
- Entry and path: query openverse free images. SERP on duckduckgo.com. SERP image serp-openverse.jpg (sha256 6cab8678e249d8728ef121502c7b291bbb15db4fa5a367519b8e398cfe6b7a54) shows the pill text clearly and first result Openverse on openverse.org. Grounding normalized 356, 189; pixels 342, 115. Coords written 06:18:22 +07. Click rc 0.
- Landing: url https://openverse.org/, real site title (Openly Licensed Images, Audio and More, Openverse), webdriver false, has_cf_challenge false. Landing image landing-openverse.jpg (sha256 5706e4850a39cfc7778c025e6b96a785d9ea2b8d15130d3dfe027ce30249d96e) shows the usable homepage with search box and circular images; pill bar faint (note A).
- Interaction: top-left circular image grounded at normalized 692, 367, pixels 664, 224; act-now click rc 0. After state is an openverse.org image detail page, webdriver false, no challenge. Interacted image interacted-openverse.jpg (sha256 20881d6554c75063ff56d8e89e615a7832c8c52372a8bae4bbac48fe52c6c6a8) shows the image detail with the pill text clearly. Verdict landed_ok true. Holder clean, overlay false after.
- Sub-checks: all PASS with note A. Result PASS. Logged at 06:20:10 +07.

## 7. Fresh-session repeats

### 7.1 coolors.co repeat (tag coolors2): FAIL

- Cookie clear (cookies-coolors2.log): before 6 (cf_clearance present, 1 entry, minted during the first coolors drive), delete 6 to 0, re-read 0. Clear PASS. Logged at 06:20:28 +07.
- Drive: start 2026-11-26T06:20:36+07:00, done elapsed 113.2s; landing read at elapsed 67.1s. Fresh BiDi session, shim reinstalled, probe PASS (webdriver false, matching shape), pill visible true. SERP on duckduckgo.com, first result coolors.co. SERP image serp-coolors2.jpg (sha256 256b767f6a4fc79dbcc3a720f643b1cbcde93871268ecb838012c10c8dd3f183) shows the pill text clearly. Grounding normalized 345, 189; pixels 331, 115. Coords written 06:21:24 +07. Click rc 0.
- Landing FAIL: url https://coolors.co/, title Just a moment..., has_cf_challenge true, body shows Performing security verification and Verify you are human, Ray ID a60463cf2d869c27. webdriver reads false (the shim held; Cloudflare walled anyway). Landing image landing-coolors2.jpg (sha256 52d4cc30de8bb5df907bff40b4b2d02b317925d47d61fb25517e60e507390689) shows the challenge checkbox, the Ray ID, and the pill text clearly. Logged as FAIL at 06:22:06 +07 with the Ray ID.
- Interaction: palette open was blocked by the challenge. The drive was completed honestly with the standard scroll step (skip written 06:22:19 +07, scroll rc 0). After state still the challenge with the same Ray ID, webdriver false. Interacted image interacted-coolors2.jpg (sha256 a93baa3f7ae4c9526383a70a47f3ecf2962ec1048bedea68911bf0374dd77f9f) shows the same challenge and the pill text clearly. Drive verdict landed_ok false. Holder ended clean (preload_removed, context_closed, session_ended, done), overlay false after. No retry was run; a bot wall is not a harness failure under the no-waive rule.
- Sub-checks: clear PASS, probe PASS, SERP PASS, click PASS, landing usable FAIL, webdriver false PASS, interaction FAIL (blocked), pill PASS. Result FAIL. This single failure closes the gate.

### 7.2 chatgpt.com repeat (tag chatgpt2): PASS

- Cookie clear (cookies-chatgpt2.log plus raw logs): before 16 (cf_clearance count 0; __cf_bm present), delete 16 to 0, re-read 0. Clear PASS. Logged at 06:23:36 +07.
- Drive: start 2026-11-26T06:23:44+07:00, done elapsed 113.6s; landing at elapsed 68.2s. Fresh session, probe PASS, pill visible true. SERP on duckduckgo.com, first result chatgpt.com. SERP image serp-chatgpt2.jpg (sha256 fa83fb12bfb735e540fa15531fa9ac3f4aff783290394114b41de3cb2aa92469) shows the pill text clearly. Grounding normalized 244, 190; pixels 234, 116. Coords written 06:24:33 +07. Click rc 0.
- Landing: url https://chatgpt.com/, real site title, webdriver false, has_cf_challenge false. Landing image landing-chatgpt2.jpg (sha256 9592009b3671e44582f6a2e6dfa89de1ed96fbe791ae3f8cdc2f1cd8645fddd8) shows the usable prompt box and the pill text clearly. Honest note: the box already contained draft text hello at landing. Cookie delete does not clear local storage drafts, so the draft from the first chatgpt drive carried over in profile storage. The landing still proves a usable box; the draft carryover is recorded, not hidden.
- Interaction: prompt box grounded at normalized 633, 497, pixels 608, 303; click plus type hello with no Enter. Interacted image interacted-chatgpt2.jpg (sha256 ff0d581fd98e4049bd93f66a958d552a25511bf5410f2b4d01ad67f09d77654d) shows hellohello (draft plus typed text appended), unsent, pill text clearly. After state webdriver false, no challenge. Verdict landed_ok true. Holder clean, overlay false after.
- Sub-checks: all PASS. Result PASS. Logged at 06:26:31 +07.

## 8. Descriptor probe, driving regression, revert verify

- Descriptor probe (inside every shimmed holder session, data page, 6 of 6 identical): webdriver false, own_on_proto true, own_on_navigator false, get_name get webdriver, configurable true, enumerable true. Getter toString verbatim from holder logs: function () { [native code] } with newlines in the raw JSON (empty function name). Baseline without the shim reads function webdriver() { [native code] } with the webdriver name. The empty-name difference is recorded as accepted risk per the runbook; it is not counted as a fail on its own. No other field differed. PASS with accepted risk. A detector probing Function.prototype.toString on the getter can see this difference today; the proof does not hide it.
- Driving regression: 6 drives through the holder setup, each with user-path navigate (search plus real click), scroll or click or type interaction, and observe screenshots. All 18 act-now batches rc 0. All 28 observes rc 0. Pill acquired visible true 6 of 6 and released cleanly 6 of 6 (drive log visible_after reads null from the overlay socket path, the same code path as Fix B; independent overlay status after every drive and at final health reads visible false with holders empty). Holder ended clean 6 of 6 with no kill and no leak. Final health at 06:26:44 +07: computer-use status ok, BiDi 9222 LISTEN, Marionette 2828 LISTEN, Zen 1.24.3b session up. PASS.
- Revert verify at 06:26:34 +07, after the final holder ended: node probe-fixb.mjs probe reads webdriver true, own_on_proto true, own_on_navigator false, native toString restored. PASS. The signal is restored; nothing persisted from the shim.
- Tabs and processes at final health: zen_cli tabs shows a single about:blank, no leftover prover tab (each holder closed its own tab). No holder, drive, or probe processes remain. Windows unchanged (Zen on ws2, agent windows on ws3 untouched). Pill visible false.

## 9. Final cookie state and cleanup

Final cookie read at 06:27:02 +07, names only, after all drives:

- coolors.co: 0 cookies. The repeat challenge set none. The cf_clearance minted in the first drive was cleared before the repeat.
- chatgpt.com: 9 cookies (oai_pl_permission_state, oai-did, oai-did-first-seen, oai-mweb-route, oai-mweb-origin, _cfuvid, oai-sc, __cflb, __cf_bm). No cf_clearance. No sign-in session cookies (cleared by the gate; the coordinator decides any re-sign-in or re-warm).
- timeanddate.com: 11 cookies including cf_clearance (1 entry, minted during the drive).
- openverse.org: 2 cookies (cf_clearance 1 entry, ui 1 entry).

The prover clears and the new mints above are now run state. No further cookies were cleared. No other host was touched. Cleanup done: /tmp/fixb-rpc and /tmp/fixb-gate removed on the laptop after evidence copy; /tmp/fixb-runner kept as the runner integration; /tmp/f3-evidence kept on the laptop with VM copies as the record. No Zen restart, no launcher, wrapper, or pref change at any point. Owner tabs, pinned tabs, and essentials were never closed or navigated; the prover drove only its own held tabs, each closed by its holder.

Gate conclusion restated: checks 1 to 4 passed cookie-cleared on first attempt, the chatgpt fresh repeat passed, descriptor, driving, and revert passed, and the coolors fresh repeat FAILED with a Cloudflare managed challenge (Ray ID a60463cf2d869c27) despite webdriver false. Under runbook section 7 the gate passes only if all of those pass. It does not. The Zen lane gate stays closed. Recommended coordinator decision, for the coordinator to make: per-task fallback for coolors-class tasks (Chromium or Brave lane per task with scorer agreement, or INVALID path), with the coolors first-pass success treated as non-reliable cold evidence, not as a pass to bank. The prover ran no fallback and released no run task.

## 10. Evidence index (improvements/f3-evidence/, prover files)

Harness and setup:
- drive-prover.py (sha256 14348b3b5e5692e1706f83e1ae893e5839d3fec89fc6d4cb930e1016db85c712)
- setup-baseline.log (setup checks, shim verify, baseline probe, SSH outage note)
- sha256-f3-prover.txt (hash list for every prover file below)

Per site (tag in file name; coolors, chatgpt, timeanddate, openverse, coolors2, chatgpt2):
- cookies-<tag>.log (before, delete, re-read with counts; chatgpt also has cookies-chatgpt-delete-raw.log, chatgpt2 also has cookies-chatgpt2-before-raw.log and cookies-chatgpt2-delete-raw.log)
- drive-<tag>.log (timed drive log with SERP, landing, after_interact, verdict)
- holder-<tag>.log (shim_pinned, session, preload, descriptor_probe, RPC, clean end)
- stdout-<tag>.log (detached stdout, same lines as drive log plus overlay spawn line)
- serp-<tag>.jpg plus serp-<tag>-observation.json (entry evidence, pill visible)
- landing-<tag>.jpg plus landing-<tag>-observation.json (landing evidence)
- interacted-<tag>.jpg plus interacted-<tag>-observation.json (action and resulting state evidence)

Grounding record (normalized point, then image pixels on 960 by 609):
- coolors SERP 345, 190 to 331, 116; coolors Generator button 263, 541 to 252, 329
- chatgpt SERP 241, 188 to 231, 114; chatgpt prompt box 632, 496 to 607, 302
- timeanddate SERP 346, 190 to 332, 116
- openverse SERP 356, 189 to 342, 115; openverse circular image 692, 367 to 664, 224
- coolors2 SERP 345, 189 to 331, 115
- chatgpt2 SERP 244, 190 to 234, 116; chatgpt2 prompt box 633, 497 to 608, 303

Pre-existing files in improvements/f3-evidence/ that predate this proof (arm scripts, tab dumps, cleanup scripts, full.log) were left untouched and are not prover evidence. Copies of the prover files above are also in improvements/fixb-evidence/prover/ per runbook cleanup.
