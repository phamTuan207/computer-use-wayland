# Opencode proposals council decision (Zen 1.24.3b, R3-L3)

- Date: 2026-11-24, evening. Run starts 25/11.
- Ordered by: the owner. The user ordered the whole team to meet, read everything, and decide together whether to apply the opencode P0/P1 proposals. The user will not decide; the council decides.
- Coordinator: opencode-proposals council coordinator.
- Council members (3, independent verdicts in ~/workspace/zen-opencode-council/):
  - Stability/risk: stability-risk-verdict.md (11 APPLY, 6 DEFER, 0 REJECT, plus additive app.update.disabledForTesting=true as APPLY).
  - Speed/benefit: speed-benefit-verdict.md (14 APPLY, 0 REJECT, 3 DEFER).
  - Red-team: redteam-verdict.md (2 APPLY, 7 REJECT, 12 DEFER across 21 items).
- Inputs read by the council: ~/workspace/zen-r3l3-opencode-report.md (336 lines, P0-1 to P0-9, P1-A to P1-H, P2, rejected list), ~/workspace/zen-r3l3-opencode-prompt.txt, ~/workspace/computer-use-wayland/README.md (design principles), Zen 1.24.3b source (zen-browser/desktop, tag 1.24.3b) and Mozilla upstream docs/Bugzilla.
- Decision rule: majority (2 of 3) APPLY = council APPLY. A REJECT blocks only if its objection is not concretely mitigated by stated conditions. A DEFER is a "needs more evidence" vote, not a safety veto.
- No em dash or en dash in this file. Commas, periods, short hyphens only.

## Council decision summary

- APPLY: 10 proposals (P0-1, P0-2, P0-3, P0-4, P0-5, P0-6, P0-8, P1-A, P1-D, P1-H). 13 pref lines.
- DEFER: 6 proposals (P0-7, P0-9 config change, P1-B, P1-C, P1-E, P1-F, P1-G) plus all 4 P2 items (skip unless a symptom appears).
- REJECT: 1 item (the additive app.update.disabledForTesting=true; it duplicates the already-live app.update.enabled=false).
- The report's own rejected list (11 items) is agreed in full by all three members.
- Nothing here saves hours. The honest run range stays 19-31 hours. The value of the APPLY set is avoiding hard stops: a crash loop into a locked safe mode (P0-1), a silently lost session (P0-2), unanswerable dialogs at the D1 restart (P0-3, P0-4), a slow-script stall (P0-5), background-tab command stalls under load (P1-A), and a portal tab hijacking the window (P1-H).

## Design principle: machine-specific vs repo-common (owner, 2026-11-24)

The owner reminded the council of a design principle that governs this whole decision. Apps on the user's machine are deliberately optimized for AI (CDP port, CLI, Marionette, custom setup), but the computer-use repo is for outsiders to use together, and their apps are usually NOT optimized for AI (no CDP, no CLI, no setup). So the council must distinguish two types, and this record does:

- **Type 1, machine-specific optimization:** applies only on the user's laptop, never goes to the repo. A Zen pref, a profile change, a system threshold, a wrapper flag, anything that assumes the user's setup.
- **Type 2, repo-common improvement:** goes into the computer-use repo and must work on a stock app that is NOT optimized for AI. That means the vision, mouse, and accessibility path must be strong, because there is no CDP, no CLI, and no setup to lean on.

Classification of everything in this decision:

- **All 10 APPLY proposals are Type 1 (machine-specific).** P0-1, P0-2, P0-3, P0-4, P0-5, P0-6, P0-8, P1-A, P1-D, P1-H are Zen profile prefs set in the user's run profile on the user's laptop only. On the user's machine they are always on. They must never be forced on repo users.
- **All 6 DEFER proposals are Type 1.** P0-7, P0-9, P1-B, P1-C, P1-E, P1-F, P1-G are also machine prefs, deferred for the user's laptop. Same rule: never forced on repo users.
- **All 4 P2 items are Type 1.** Same reason.
- **The additive app.update.disabledForTesting (REJECT) is Type 1.** A pref, rejected.
- **The report's 11 rejected items are Type 1.** Prefs, rejected.
- **Nothing in this council decision is Type 2 (repo-common code).** The council evaluated machine prefs, not repo code. No repo code change is proposed, approved, or implied by this decision.

Refinement from the owner (20:49): machine-specific optimization CAN still go to the repo, but only as OPTIONAL (opt-in), never forced like the local version on the user's machine (where it is always on). So for the repo, every machine-specific optimization is optional, default OFF. A repo user may turn it on if they set up their app for AI, but the repo must run even when it is off. Per-proposal optional/mandatory and default:

| Proposal | Council | The user's laptop | Repo form | Repo default |
|---|---|---|---|---|
| P0-1 max_resumed_crashes -1 | APPLY | ON (always) | OPTIONAL | OFF |
| P0-2 sessionstore.max_resumed_crashes 10 | APPLY | ON (always) | OPTIONAL | OFF |
| P0-3 warnOnQuit false | APPLY | ON (always) | OPTIONAL | OFF |
| P0-4 warnOnCloseOtherTabs false | APPLY | ON (always) | OPTIONAL | OFF |
| P0-5 max_script_run_time 0 (both) | APPLY | ON (always) | OPTIONAL | OFF |
| P0-6 telemetry.fog.init_on_shutdown false | APPLY | ON (always) | OPTIONAL | OFF |
| P0-7 disable 5 extensions | DEFER | OFF (not applied) | Not included | OFF |
| P0-8 unloadOnLowMemory false | APPLY | ON (pinned false) | OPTIONAL | OFF |
| P0-9 oomd threshold 85%/60s | DEFER | OFF (monitor only) | Not included | OFF |
| P1-A processPriorityManager off | APPLY | ON (always) | OPTIONAL | OFF |
| P1-B sessionstore.interval 15000 | DEFER | OFF (not applied) | Not included | OFF |
| P1-C RDD mitigation | DEFER | OFF (not applied) | Not included | OFF |
| P1-D pagethumbnails off | APPLY | ON (always) | OPTIONAL | OFF |
| P1-E backup off | DEFER | OFF (not applied) | Not included | OFF |
| P1-F focusmanager.testmode | DEFER | OFF (not applied) | Not included | OFF |
| P1-G apz timeout 60000 | DEFER | OFF (not applied) | Not included | OFF |
| P1-H captive-portal off | APPLY | ON (always) | OPTIONAL | OFF |
| Additive app.update.disabledForTesting | REJECT | OFF (not applied) | Not included | OFF |
| P2-A to P2-D | DEFER/skip | OFF (not applied) | Not included | OFF |
| Report's 11 rejected items | REJECT | OFF (not applied) | Not included | OFF |

What "OPTIONAL, default OFF" means in practice: if any of these ever goes to the repo, it goes as a documented opt-in (a doc or an optional setup step), never as a default and never as a requirement. The repo's core (vision, mouse, accessibility) must work with all of them off. No repo test may depend on them being on. Nothing in this decision is mandatory for the repo.

- **Type 2 implication recorded for the repo (not a change, a standing principle):** the repo must not assume CDP, BiDi, Marionette, a CLI, or any setup exists on a user's machine. The vision, mouse, and accessibility path must be strong enough to drive a stock app. The machine-specific wins in this record (BiDi responsiveness from P1-A, no dialogs from P0-3/P0-4, no portal hijack from P1-H) are the user's-laptop-only advantages. They must not leak into repo assumptions or repo tests. A repo test that passes only because the app was pre-optimized for AI proves nothing about the repo.

## Vote matrix

| Proposal | Stability | Speed | Red-team | Council |
|---|---|---|---|---|
| P0-1 max_resumed_crashes -1 | APPLY | APPLY | REJECT | APPLY (mitigated) |
| P0-2 sessionstore.max_resumed_crashes 10 | APPLY | APPLY | DEFER | APPLY |
| P0-3 warnOnQuit false | APPLY | APPLY | APPLY | APPLY (unanimous) |
| P0-4 warnOnCloseOtherTabs false | APPLY | APPLY | APPLY | APPLY (unanimous) |
| P0-5 max_script_run_time 0 (both) | APPLY | APPLY | REJECT | APPLY (mitigated) |
| P0-6 telemetry.fog.init_on_shutdown false | APPLY | APPLY | DEFER | APPLY |
| P0-7 disable 5 extensions | DEFER | APPLY | REJECT | DEFER (no majority) |
| P0-8 unloadOnLowMemory false | APPLY | APPLY | DEFER | APPLY (verify-and-pin) |
| P0-9 oomd threshold 85%/60s | DEFER | APPLY | REJECT | DEFER (monitor only) |
| P1-A processPriorityManager off | APPLY | APPLY | DEFER | APPLY |
| P1-B sessionstore.interval 15000 | DEFER | APPLY | DEFER | DEFER |
| P1-C RDD mitigation (conditional) | DEFER | DEFER | DEFER | DEFER (unanimous) |
| P1-D pagethumbnails off | APPLY | APPLY | DEFER | APPLY |
| P1-E backup off | DEFER | DEFER | DEFER | DEFER (unanimous) |
| P1-F focusmanager.testmode | DEFER | APPLY | DEFER | DEFER |
| P1-G apz timeout 60000 | APPLY | DEFER | DEFER | DEFER |
| P1-H captive-portal off | APPLY | APPLY | REJECT | APPLY (mitigated) |
| Additive app.update.disabledForTesting | APPLY | (silent) | REJECT | REJECT |

## Per-proposal decision, reasons, evidence

### APPLY

**P0-1 toolkit.startup.max_resumed_crashes = -1.** Votes 2 APPLY, 1 REJECT. Red-team REJECT: removes the safe-mode escape hatch, endless restart loop risk (Bugzilla 2083176), verification needs kill -9 on the frozen profile. Mitigation accepted: the watchdog caps consecutive restarts (external circuit breaker, the correct place for the cap), and verification is by config read plus one clean restart, never a double kill -9 on the live profile. Evidence: shipped default 3 verified in installed firefox.js; in the RecommendedPreferences set (verified in the installed omni.ja, 23,496 bytes); Zen issue #16694 (safe mode keeps profile lock, open) confirmed. Condition: the run coordinator's watchdog must cap restarts and alert instead of looping forever.

**P0-2 browser.sessionstore.max_resumed_crashes = 10.** Votes 2 APPLY, 1 DEFER. Red-team DEFER: arbitrary number, no local session-loss cited, crash test needed. The number 10 is bounded and sane; the direction is right (at default 1, the second consecutive crash silently loses the tab set). Verification by config read only, no crash test. Evidence: shipped default 1 verified; resume_from_crash stays true (verified default true). Do NOT also set browser.startup.couldRestoreSession.count=-1 (unverified pref).

**P0-3 browser.warnOnQuit = false.** Unanimous APPLY. A quit-confirm modal no automation client can dismiss is a guaranteed hang at the D1 restart. Removing it has no downside. Evidence: shipped default true verified; in the RecommendedPreferences set and Bugzilla 1595878.

**P0-4 browser.tabs.warnOnCloseOtherTabs = false.** Unanimous APPLY. Same hang class as P0-3; A1 tab hygiene closes other tabs. Evidence: shipped default true verified; in the RecommendedPreferences set and Bugzilla 1595878.

**P0-5 dom.max_script_run_time = 0 and dom.max_chrome_script_run_time = 0.** Votes 2 APPLY, 1 REJECT. Red-team REJECT: 0 disables the dialogue but does not make a runaway script stop or a blocked CDP command return; trades a visible stall for a silent one. Mitigation accepted: the asymmetry holds (a dialog unattended is a guaranteed hang; a hung script with a coordinator timeout is recoverable), and the backstop is the coordinator's per-task timeout plus a CPU watch. Both APPLY members stated this backstop as a condition. Evidence: both prefs in the RecommendedPreferences set (verified). Condition: the run coordinator keeps per-task timeouts and a CPU watch as the backstop.

**P0-6 telemetry.fog.init_on_shutdown = false.** Votes 2 APPLY, 1 DEFER. Red-team DEFER: no local timing, and Bugzilla 2079627 records locking it false in CI produced a 7 s shutdown delay and a Glean error in Firefox 160. The majority holds: it is a locked pref in Mozilla's own automation set citing bug 2076854, and the benefit is seconds at the D1 restart. The 2079627 counter-evidence is recorded here as a known risk: time the D1 restart shutdown and note it if slow. Evidence: in the RecommendedPreferences set as a locked pref (verified present).

**P0-8 browser.tabs.unloadOnLowMemory = false (verify-and-pin).** Votes 2 APPLY, 1 DEFER (as a check only). All three agree it is already false on this Linux build and the item is a verification, not a change. Council APPLY means: confirm it is false at run start and pin it explicitly in user.js so it stays false. Evidence: shipped default false on this Linux build, verified in installed firefox.js. This is the only mechanism that can silently discard a needed tab.

**P1-A dom.ipc.processPriorityManager.enabled = false and threads.lower_mainthread_priority_in_background.enabled = false.** Votes 2 APPLY, 1 DEFER. Red-team DEFER: no local latency measurement. The majority holds on the upstream measurement: Bugzilla 1963001 measured background-tab commands at 13-266 ms with the manager off versus 1.3-5.1 s hangs with it on under CPU saturation, and Bugzilla 1960734 (Firefox 139) disabled the manager for Remote Protocols through the recommended-prefs path, so remote.prefs.recommended=false removed it here. Cost is CPU fairness, the right trade on a 32 GB host. Evidence: both prefs in the RecommendedPreferences set (verified); Bugzilla 1960734 and 1963001.

**P1-D browser.pagethumbnails.capturing_disabled = true.** Votes 2 APPLY, 1 DEFER. Red-team DEFER: no evidence thumbnails cost anything on this host. The majority holds: it removes periodic full-page raster captures with no automation value and no behavioural risk. Evidence: in the RecommendedPreferences set (verified).

**P1-H network.captive-portal-service.enabled = false and network.connectivity-service.enabled = false.** Votes 2 APPLY, 1 REJECT. Red-team REJECT: the connectivity service detects link down/up, disabling it can delay reconnect detection; no portal incident cited; if a task needs a portal login it fails with no diagnosis. Mitigation accepted: reconnection is OS-level; the portal tab stealing the task's window is a real disruption on flaky campus WiFi; for an unattended run a portal login cannot happen anyway, so the portal tab only harms. Condition: revert both prefs after the run (they persist into daily use). Evidence: both prefs in the RecommendedPreferences set (verified); shipped defaults true.

### DEFER

**P0-7 Disable the 5 installed extensions.** Votes 1 APPLY, 1 DEFER, 1 REJECT. No majority. Red-team REJECT is the strongest in the list: 3 of 5 extensions are unidentified GUIDs, no dedicated automation profile is shown to exist, and disabling the daily profile's extensions the night before the run is the most invasive proposal. Stability correction (live extensions.json): Browsec is already inactive, so the headline proxy risk does not exist; the five are Browsec VPN 3.93.7, Obsidian Web Clipper 1.7.1, Open In mpv 2.4.3, Transparent Zen 0.9.4, Ambient light for YouTube 2.38.17. Stability offered a safe two-extension subset (disable Ambient light for YouTube and Obsidian Web Clipper after confirming no task uses them), but without a dedicated automation profile and without a task-list check, the council defers the whole item. Do not disable extensions tonight.

**P0-9 systemd-oomd threshold (85%/60s) or browser exclusion.** Votes 1 APPLY, 1 DEFER, 1 REJECT. No majority. Red-team REJECT: system-level change outside the browser, no local evidence (no oomd kill cited), Omarchy set 50%/20s deliberately so a misbehaving app dies instead of the whole Hyprland session, numbers arbitrary, needs sudo plus an /etc drop-in plus daemon-reload plus oomd restart the night before a frozen run. Monitor-only is agreed: journalctl -u systemd-oomd in the run checklist at T+0 and after D1, and revisit only if memory pressure actually appears. Live facts: oomd active, 50%/20s, ManagedOOMMemoryPressure=auto, 20.5 GB available, zero kill lines this boot.

**P1-B browser.sessionstore.interval = 15000.** Votes 1 APPLY, 2 DEFER. Zen deliberately overrode Firefox's default to 40000; more frequent main-thread session writes trade against the main-thread stalls the run already worries about, and P0-2 already fixes crash restore. No session-loss symptom observed. Defer.

**P1-C RDD mitigation (widget.dmabuf.force-enabled + media.hardware-video-decoding.force-enabled).** Unanimous DEFER. The report's own conditional framing is correct and is kept: apply only if about:crashes shows an RDD signature. No RDD signature on this host in this build (one pre-1.24.3b SIGSEGV, corefile missing, signature unknown; issue #16718 is a single reporter on a GTX 1660Ti, different GPU from this RTX 4050 Max-Q + Intel iGPU). Forcing hardware decode plus dmabuf on a hybrid NVIDIA + Wayland host can create crashes, and issue #14067 identifies forced VA-API on NVIDIA + Wayland as a crash trigger. Keep the triage steps (about:crashes, coredumpctl list zen-bin, journal grep) as the run-time trigger.

**P1-E browser.backup.enabled = false.** Unanimous DEFER. The claimed benefit (fewer pause spikes from profile-archive IO) is speculation with no measurement, and the cost is real: it removes the recovery artifact (profile backups) the night before a 19-31 h run, exactly when a corrupt profile would need one. It also contradicts P0-2's session-restore goal. Keep the backup.

**P1-F focusmanager.testmode = true.** Votes 1 APPLY, 2 DEFER. No focus no-op symptom has been observed, and the run drives via BiDi/CDP, not synthetic focus. Stability's counter-evidence is specific to this machine: Bugzilla 1717145 shows a persisted focusmanager.testmode=true broke fcitx5 IME activation, and this laptop runs fcitx5 and the owner types Vietnamese. Apply only if a focus no-op is actually observed in the pre-run trial, then with an IME check and a revert plan.

**P1-G apz.content_response_timeout = 60000.** Votes 1 APPLY, 2 DEFER. No APZ timeout event was observed in R1/R2 or attributed to any task. Raising the timeout turns a fast, diagnosable stall into a 60 s silent hang, which delays failure detection instead of speeding anything up. Defer.

**P2-A to P2-D.** All DEFER/skip, agreed by all three members. P2-A translations off: only if a task hits a foreign-language page (none known). P2-B idle-animation surface: code-side, not pref-side, no idle-CPU symptom measured. P2-C reportProcessHangs off: telemetry suppression only, no behavioural gain. P2-D unloadDelayMs 0: inert while P0-8 keeps the unloader off.

### REJECT

**Additive app.update.disabledForTesting = true (report section 6).** Votes 1 APPLY, 1 REJECT, 1 silent. No majority. Red-team REJECT accepted: it is a test-only pref that duplicates the already-live and verified app.update.enabled=false, with no verification and no need. The existing pin is sufficient. Do not add it.

### Report's rejected list: agreed in full

All three members agree with all 11 rejections in the opencode report section 5: remote.active-protocols=3 (confirmed removed in Firefox 141, cannot exist in Firefox 160), media.rdd-process.enabled=false (weakens the RDD sandbox), disabling Safe Browsing, origin/permission weakening prefs, fission/process-count collapse, dom.min_background_timeout_value=0, gfx/webrender/dmabuf force flags alone, any Twilight/pre-release build, community pref gists and Auto Tab Discard-style extensions, dom.disable_open_during_load=false, browser.sessionstore.resume_from_crash=false.

## Central finding: verified, with corrections

- remote.prefs.recommended=false is live in prefs.js, and the RecommendedPreferences set is skipped. The stability member verified independently (read-only): the file exists in the installed build, 23,496 bytes, in the root omni.ja (not browser/omni.ja as the report states), and contains 14 of the 15 prefs checked (the absent one is browser.sessionstore.max_resumed_crashes, which the report itself says is not in Mozilla's set). None of the P0/P1 prefs is currently set.
- Shipped defaults verified from the installed build: toolkit.startup.max_resumed_crashes 3, browser.sessionstore.max_resumed_crashes 1, browser.sessionstore.resume_from_crash true, browser.warnOnQuit true, browser.tabs.warnOnCloseOtherTabs true, browser.tabs.unloadOnLowMemory false, browser.sessionstore.interval 40000, browser.backup.enabled true. All match the report.
- Red-team corrections recorded: the report publishes no inventory of the 100+ entry set and no audit trail for what was excluded; line-number citations to defaults/preferences/firefox.js are upstream-Firefox lines, not Zen-specific lines, and Zen may override defaults in its own pref files; the report's LOCAL-VERIFIED citations carry no hash or excerpt, so they were re-verified by the stability member on the laptop (above) rather than taken on trust.
- Prompt bias noted (red-team): the prompt opencode was given demanded a P0 apply list and asked for what is MISSING, with no "do nothing / nothing needed" outcome offered, and its evidence base was degraded (websearch 402 for every query, SUMO bot-walled, Reddit empty, Discord unfetchable, no Zen stability docs). The council weighed the proposals on their own evidence, not on the prompt's framing.

## What was applied (with verification)

Applied 2026-11-24 evening by the council-decision applier. Full report: ~/workspace/zen-opencode-council/apply-report.md. Work 20:43-21:07 +07 (elapsed ~24 min). No crash test (no kill -9). ZCode untouched. No OpenRouter.

**Prefs applied (13 lines, appended to user.js in the run profile):** backup first (user.js copied to user.js.bak-council-20261124, 760 bytes, md5 fde3e441ef3f593991af3c9da80d58c2). New user.js 1566 bytes, md5 f74d47c48fb3f563bddb7b41ffe5561b. Syntax check: 17 user_pref lines total (4 pre-existing + 13 new), zero failing the pattern. The 4 pre-existing prefs (browser.shell.checkDefaultBrowser, toolkit.legacyUserProfileCustomizations.stylesheets, remote.prefs.recommended, app.update.enabled) were left untouched.

**All 13 effective:**
- 9 appear in prefs.js with exactly the council values: toolkit.startup.max_resumed_crashes=-1, browser.sessionstore.max_resumed_crashes=10, browser.warnOnQuit=false, browser.tabs.warnOnCloseOtherTabs=false, dom.max_script_run_time=0, dom.ipc.processPriorityManager.enabled=false, browser.pagethumbnails.capturing_disabled=true, network.captive-portal-service.enabled=false, network.connectivity-service.enabled=false.
- 4 are absent from prefs.js (dom.max_chrome_script_run_time, telemetry.fog.init_on_shutdown, browser.tabs.unloadOnLowMemory, threads.lower_mainthread_priority_in_background.enabled) but proven effective by a clean headless scratch-profile experiment on this exact build: the same 4 did not appear in a scratch prefs.js either, with a control pref (browser.warnOnQuit=false) appearing, so on this build these 4 council values EQUAL the build defaults and the effective value IS the council value. unloadOnLowMemory=false was also confirmed directly in the shipped firefox.js defaults. All 13 council values are exactly the values in the remote agent's shipped RecommendedPreferences list.

**Restart (ONE controlled restart):** SIGTERM 20:44:29 to old PID 404548 (RSS 644264 KB), all zen-bin exited in 2 s, relaunched via the zen-ai wrapper 20:44:30, new PID 788926 with ports 9222/2828 listening by 20:44:31 (about 2 s downtime). Pre: PID 404548 (since 19:59:31), RSS 642064 KB, 72 tabs, 1 window, 49 pinned. Post: PID 788926, RSS 663052 KB, 72 tabs, 1 window, 49 pinned. Version still 1.24.3b, BuildID 20261118023529 (application.ini and BiDi caps agree). Tabs 72/72 restored, 0 lost. One tab's current page changed from the repo page to the user profile page on GitHub (within-tab navigation, not a restore failure, not caused by the applier's probes). BiDi session.new + clean session.end verified three times (20:50, 20:54, final 21:07); no session left open, runner slot free.

**Incidents during verification (all resolved, no lasting effect):** (1) A BiDi probe that tried to navigate to about:config failed (Firefox forbids WebDriver navigation to about:config) and its script exited without session.end; the orphaned session blocked new sessions about 3 min until the server reaped it, then a retry succeeded; it also left a stray about:blank tab, reaped with the session (tab count back to 72). Lesson: always session.end in a finally/error path, never navigate to about: pages via WebDriver. (2) Marionette needed protocol v3 array framing; the legacy object format gets no reply. (3) Chrome-context pref reads via Marionette are blocked without MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1; no second restart was done to add it (one restart only, already used). (4) One Marionette probe opened a tab and failed its navigate step; the tab did not persist. (5) toolkit.telemetry.server leftover in prefs.js predates this task (from an earlier session), not set by this task, left as is.

**Bottom line:** all 13 council prefs applied and effective. Zen restarted cleanly in about 2 s. Ready for tomorrow's R3-L3 run.

## Conditions carried to the run coordinator

- One controlled restart total, tonight, bundling all approved prefs. Re-verify after: ports 9222/2828 live, tab set intact, the 13 prefs effective in about:config/prefs.js, version still 1.24.3b.
- No deliberate crash test (no kill -9) on the live profile. P0-1/P0-2 are verified by config read plus one clean restart.
- P0-1 removes the browser's crash circuit breaker: the run watchdog must cap consecutive restarts and alert instead of looping forever.
- P0-5 backstop: the run coordinator keeps per-task timeouts and a CPU watch; a hung script is caught by the timeout, not by a dialog.
- P1-H reverts after the run (both prefs persist into daily use otherwise).
- Monitor-only items for the run checklist: journalctl -u systemd-oomd at T+0 and after D1 (P0-9); about:crashes plus coredumpctl list zen-bin as the P1-C triage gate; about:config spot-check of browser.tabs.unloadOnLowMemory at T+0 (P0-8).
- P0-7 and P0-9 are deferred, not rejected: revisit only on an observed symptom (an extension causing a failure, or sustained memory pressure in the journal).

## Files

- Council verdicts: ~/workspace/zen-opencode-council/stability-risk-verdict.md, ~/workspace/zen-opencode-council/speed-benefit-verdict.md, ~/workspace/zen-opencode-council/redteam-verdict.md.
- Applier report: ~/workspace/zen-opencode-council/apply-report.md (pending).
- Inputs: ~/workspace/zen-r3l3-opencode-report.md, ~/workspace/zen-r3l3-opencode-prompt.txt.
