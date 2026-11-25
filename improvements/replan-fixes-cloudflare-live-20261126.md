# Fix B: Cloudflare shim runner-lane integration (F4) and prover runbook (F3)

- Date: 2026-11-26. Author: FIX WORKER B (implementer, not the prover). Run PAUSED, epoch 9 holds. Nothing in this file resumes the run, edits coordinator state, or commits anything.
- Scope: redteam fixes F4 (runner-lane integration plus one held-out drive) and F3 preparation (prover runbook). A separate prover who did not implement this runs section 7 cold.
- Evidence: improvements/fixb-evidence/ (logs, images, harness sources). Laptop copies at /tmp/fixb-runner/, /tmp/fixb-evidence/, /tmp/fixb-gate/, /tmp/fixb-rpc/.
- Rules followed: no em dashes or en dashes; English only; pill on every agent control (label "Computer use active"); one driver at a time on the shared Zen; owner tabs never closed or navigated; ws3 untouched; ws2 work workspace; no ydotool (ydotool is banned, restate the ban in every brief, never assume it); SSH only via ~/workspace/ssh-laptop.sh; long jobs detached with setsid nohup; Zen never restarted; no launcher, wrapper, or pref changes; full access (Codex --sandbox danger-full-access, fcc --dangerously-skip-permissions); ponytail for all code (smallest complete change, reuse before writing, standard library and platform before dependencies, no unrequested abstraction, one small test for non-trivial logic, never cut validation, security, or error handling); event-log duty (log key events via ~/workspace/agent-event-log/log-event.sh, source replan-fix-b); user-path test rule (enter via search or homepage and click through like a normal user, no deep links, no direct commands, no internal setters, evidence shows entry, path, action, and resulting state; end-state-only evidence for a user-facing claim is returned unread).

## 1. Chosen shim, pinned by hash

Function declaration string (verbatim, 316 bytes):

```
(() => { try { const p = Object.getPrototypeOf(navigator); const d = Object.getOwnPropertyDescriptor(p, 'webdriver'); if (d && d.get) { const fakeGet = new Proxy(d.get, { apply: () => false }); Object.defineProperty(p, 'webdriver', { get: fakeGet, configurable: true, enumerable: d.enumerable }); } } catch(e){} })()
```

- sha256 of the exact string: bb49ff3f974a0534445fa5bb8eac48b47a378f39d944706b10118d5ff9d630b8. Verified equal to the proxy entry in improvements/council2-harness/holder.mjs. The holder refuses to start on hash mismatch (exit code 2, step shim_pinned in holder log).
- Known descriptor difference, accepted risk: with the shim, the getter toString reads "function () { [native code] }" with an empty function name, while baseline reads "function webdriver() { [native code] }". Everything else matches baseline shape (own property on the prototype, getter name "get webdriver", configurable and enumerable true). A detector that probes Function.prototype.toString on the getter can see this difference today. The probe in section 7 tests toString explicitly and records the difference; it does not hide it.

## 2. F4.1: the real runner session setup (read-only findings)

Method: graphify query and explain on ~/workspace/cu-graphify/graphify-out/graph.json first (ZenSession, BidiSession, open_session, pill acquire), then direct reads of the laptop files. Note: the graph tree (~/workspace/cu-graphify) is a stale copy; laptop file hashes differ (zen_dom.py laptop 79efea0a..., graph copy 38b4c369...; zen_cli.py laptop 60de6bbd..., graph copy adc98d53...). Structure and function names match; line numbers below are laptop-verified.

What exists today on the laptop (~/computer-use-wayland/scripts/, installed copy ~/.local/share/agent-computer-use/scripts/ identical by hash):

- scripts/zen_dom.py, class ZenSession (L469), __enter__ (L494): starts geckodriver per session (--connect-existing, Marionette 2828), then POST /session (L515) with capabilities alwaysMatch browserName firefox. There is NO webSocketUrl capability. This is WebDriver classic only; it cannot send script.addPreloadScript. Sessions are short-lived per call and always deleted in _cleanup. One session at a time via file lock ~/.cache/agent-computer-use/zen_dom.lock.
- scripts/zen_cli.py, class BidiSession (L427), start() (L484): raw WebSocket to ws://127.0.0.1:9222/session, session.new with empty capabilities. open_session(port) (L686) wraps it. Each CLI command opens and ends its own short BiDi session. No addPreloadScript anywhere in scripts/ today (grep empty).
- scripts/first_action.py, acquire_overlay (L68) and release_overlay: the pill. computer-use act-now acquires the pill, attempts a broker session (session_remote.py), falls back to direct Pointer on session-start failure only. The computer-use "session" is the cursor-guard broker session, not a BiDi session held across a drive.
- Runner lanes in practice (lane briefs 2026-11-25, coordinator state, per-task reports): Codex lane = one codex exec invocation per task from /home/james (codex exec -m gpt-6-luna --sandbox danger-full-access --skip-git-repo-check), no interactive tmux. FCC lane = tmux session r3-fcc-runner-L3 (fcc-claude --dangerously-skip-permissions). Muse lane = fresh Muse subagents per task (most recent drives). All lanes drive Zen through computer-use observe, act, and act-now with overlay.py pill acquire per lane agent name, plus short zen_dom or zen_cli calls for DOM reads. No lane holds a BiDi session open during a drive today.

Exact integration points:

- BiDi lane (the proven shape): scripts/zen_cli.py BidiSession.start() (L484), immediately after session.new returns and before any browsingContext.create or navigate. That is where script.addPreloadScript with the pinned Proxy string must be sent, and script.removePreloadScript plus session.end belong in BidiSession.end() (L462 area, finally path).
- Classic lane (only if unified later): scripts/zen_dom.py ZenSession.__enter__ POST /session (L515) would need webSocketUrl true added to alwaysMatch, then a WebSocket client to the returned URL for addPreloadScript. Fix B does NOT make this change during the paused run; it would touch every ZenSession consumer (zen_backend.py, code_exec path) for no proven gain.

Single-slot constraint (load-bearing): BiDi and Marionette share one remote session slot per Zen instance. While a holder owns the BiDi session for a drive, zen_dom and zen_cli short sessions must not be opened; DOM reads during the drive go through the holder RPC (script.evaluate). Opening a second session fails or blocks (council-2 observed about 9 minutes to reap a leaked session). Leak rule: always session.end in a finally path; if session.new blocks, wait for reap, do not restart Zen.

## 3. F4.2: smallest integration implemented (machine-specific, local only)

Ponytail choice: reuse the council-2 holder pattern, no new framework, no edits to zen_dom.py, zen_cli.py, first_action.py, launcher, wrapper, or prefs. Three new files, all under /tmp on the laptop (ephemeral by design; VM evidence copies are the source of truth). No repo commit. Any future repo helper stays opt-in default off (for example CU_HIDE_WEBDRIVER=1); the laptop keeps the holder always-on locally per drive via the runner brief, not via profile state.

Files created on the laptop (each with revert):

- /tmp/fixb-runner/holder-fixb.mjs (sha256 70bfe8abbed9fdbec30a2cf323c61150322048ce2736dfe26186a1c075d4f213). Owns the ONE BiDi session for one drive: shim hash pin, session.new, addPreloadScript immediately after, one tab, descriptor probe on a data page (the one small test; mismatch throws and the drive fails loudly before any navigation), RPC over /tmp/fixb-rpc (evaluate, cookies_list names only, cookies_delete), removePreloadScript plus browsingContext.close plus session.end in finally, process.exit(0) after done. Revert: rm -rf /tmp/fixb-runner /tmp/fixb-rpc.
- /tmp/fixb-runner/probe-fixb.mjs (sha256 5329a574c7c7de6b003ad967d9706e75e589ce60c388f7a07f39f12dcf15c1f9). Short standalone BiDi session, own tab only: descriptor probe (revert check), cookie names per domain, cookie delete per domain. Revert: same rm as above.
- /tmp/fixb-runner/drive-fixb.py (sha256 6af74f2a4e03745504e9e9520019a9e5e097e943707ad01fe226c43e90d79f45). Held-out drive driver (section 4), stdlib only, pill via first_action, real input via act-now, state via holder RPC. Revert: same rm as above.
- Runtime dirs /tmp/fixb-evidence/ (logs, action batches) and /tmp/fixb-gate/ (serp.json, coords.json). Revert: rm -rf /tmp/fixb-evidence /tmp/fixb-gate. Observe images under ~/.cache/agent-computer-use/ are tool-owned cache, left in place (same as council-2).
- Transfer method (recorded for the prover): base64 -w0 on the VM piped through ssh-laptop.sh into base64 -d on the laptop, sha256 readback verified equal on both sides for every file. No scp, no exec-write of file content on the VM.

Session owner per lane (who starts and stops the holder):

- Codex exec lane: the codex exec invocation itself. Its brief starts the holder detached before the first navigation, checks ready.json probe, drives, writes the stop file in its cleanup step, and records the probe result in the snapshot manifest chain. If the probe mismatches, the invocation stops and reports; it never drives unshimmed.
- FCC tmux lane (r3-fcc-runner-L3): the FCC agent process in that pane, same start, probe, stop discipline. The tmux session itself never holds the BiDi session across tasks; one holder per task drive.
- Muse subagent lane: the Muse runner subagent for that task, same discipline. The coordinator never holds the session; the coordinator only verifies probe evidence at the manifest gate.
- One driver at a time still holds: holder start requires the session slot free (probe session.new succeeds) and the cursor lock free (/proc fd scan for cursor.lock). A busy slot means stop and report, never retry blindly.

Fail-loud behavior: holder probe mismatch exits non-zero with the probe JSON in the holder log; drive-fixb.py re-checks ready.json probe fields and raises before searching. Probe failure inside codex exec surfaces as a non-zero invocation with the holder log path in output; the coordinator treats it as a runner failure, not a task fail, and never releases the next task on a failed probe.

Three integration bugs found live and fixed in Fix B (recorded so the prover does not rediscover them):

1. BiDi result shape: script.evaluate with resultOwnership none returns objects as arrays of key and remote-value pairs. The first holder build compared raw pairs to plain fields and failed its own probe loudly (attempt 1, 05:50:59). Fix: unwrapRemote in holder and probe. Probe values were correct throughout (webdriver false, own_on_proto true, own_on_navigator false).
2. Gate race: the drive saw coords.json exist while the SSH write was still empty and crashed on JSON decode (attempt 2, 05:53:31). Fix: drive retries until the file parses; coords are written atomically (write tmp file, then rename).
3. Event-loop linger: pending 60-second send timers kept the Node holder alive after session.end, so the drive waited 30 seconds and killed it (attempt 2). Fix: process.exit(0) after the done log in holder and probe. Attempt 3 ended cleanly with no kill.

## 4. F4.3: one held-out drive of run shape (attempt 3, PASS)

User-path test: enter via search/homepage and click through like a normal user; no deep links, no direct commands, no internal setters; evidence shows entry, path, action, and resulting state.
User entry point for this test: held blank tab on ws2, Ctrl+L, type "cloudflare", Return (DuckDuckGo SERP), click first result.
Forbidden shortcuts for this test: deep link or BiDi navigate to cloudflare.com, internal setters, test-only endpoints, DOM click.

Target choice: cloudflare.com via search. It is Cloudflare-fronted, realistic, and not a frozen run task. The four run sites are reserved for the F3 prover (section 7) so Fix B does not mint fresh clearance on run hosts before the prover clears them.

Timeline (wall-clock Asia/Ho_Chi_Minh, elapsed from drive start; full log fixb-evidence/drive-fixb.log):

- 05:54:58 drive_start. 05:54:59 pill_acquired visible true, label "Computer use active" (agent FixB, method BiDi test).
- 05:55:01 holder_ready: session 404350e0-1acb-4549-b342-9c405406fec5, probe webdriver false, own_on_proto true, own_on_navigator false, get_name "get webdriver", get_tostring "function () { [native code] }", shim sha256 bb49ff3f...630b8. probe_ok.
- 05:55:07 act_now search rc 0 (Ctrl+L, type, Return). 05:55:14 SERP read via RPC: title "cloudflare at DuckDuckGo", url duckduckgo.com search for cloudflare. Observe image d54d853ec646.jpg (fixb-evidence/serp-cloudflare-attempt3.jpg, sha256 43645f4a...c8) shows the SERP with the pill visible at top center.
- Gate: first result grounded on the fresh SERP image (normalized point 306, 190; image pixels 294, 116 on the 960 by 609 observe image). Coords written atomically at 05:55:54 (gate_coords elapsed 55.5s; the wait includes image fetch and grounding by Fix B).
- 05:55:59 act_now click rc 0 with fresh preclick observation. 05:56:11 landing via RPC: url https://www.cloudflare.com/, title "Cloudflare: Build for the agent era", webdriver false, has_cf_challenge false. Observe image 24c3be90f232.jpg (fixb-evidence/landing-cloudflare.jpg, sha256 0af883e6...90) shows the usable homepage with the pill visible.
- 05:56:15 act_now scroll rc 0. 05:56:18 after_interact: same url and title, webdriver false, no challenge. Observe image 590550c9f436.jpg (fixb-evidence/interacted-cloudflare.jpg).
- 05:56:18 drive_verdict landed_ok true. 05:56:19 pill_released, drive_done. Total elapsed 80.4s including the 40-second grounding gate wait; drive actions alone about 40s.
- Holder log (fixb-evidence/holder-fixb.log): shim_pinned, session, preload_installed cc4068fc-a9d2-4373-a16c-db1a738d30b8 (attempt 3 session), context_created, descriptor_probe, probe_ok, 3 RPC evaluates ok, preload_removed, context_closed, session_ended, done. No kill, no leak.

Attempts 1 and 2 are preserved in fixb-evidence/drive-attempt2.log and holder-attempt2.log (attempt 1 failed at the probe unwrap bug before any navigation; attempt 2 reached the SERP then hit the gate race). No attempt touched owner tabs, ws3, or any run task. Epoch 9 pause held throughout; no run task was released.

Revert and health verification after the drive:

- Revert probe (fixb-evidence/probe-revert.log, 05:57:02): fresh short BiDi session, data page, webdriver true, own_on_proto true, own_on_navigator false, get_tostring "function webdriver() { [native code] }". The signal is restored; nothing persisted.
- Ports (fixb-evidence/ports-pill-cleanup.log): 127.0.0.1:9222 LISTEN (zen-bin), 127.0.0.1:2828 LISTEN, Marionette TCP open, BiDi endpoint answers (plain HTTP GET returns the expected WebSocket upgrade message). computer-use status ok.
- Pill: overlay status holders empty, visible false after release. Windows unchanged: Zen 0x5614f01a0e20 on ws2, four agent windows on ws3 untouched. Tabs read-only list: single about:blank, no leftover Fix B tab (each holder closed its own tab). No fixb processes remain.

## 5. F4.4: cf_clearance cookie state (names only, no values)

Read via storage.getCookies full read with suffix filter (a filtered read for the bare domain misses cookies stored under the dot domain; observed live). Full logs: fixb-evidence/probe-baseline-cookies-before.log (before drive), cookies-cloudflare-after-drive.log, cookies-after-all.log (after everything).

- coolors.co: cf_clearance present (2 entries, domain .coolors.co), plus __Secure-PHPSESSID, _ga family. Unchanged after Fix B.
- chatgpt.com: cf_clearance present (3 entries, domain .chatgpt.com), plus __cf_bm, _cfuvid, and normal site cookies. Not re-read after Fix B (no Fix B step touched this host).
- timeanddate.com: cf_clearance present (2 entries, domain .timeanddate.com). Not re-read after Fix B.
- openverse.org: cf_clearance present (2 entries, domain .openverse.org), plus ui. Unchanged after Fix B.
- cloudflare.com (held-out host): cf_clearance present before the drive (1 entry). After the drive, 10 cookies including cf_clearance. The delete-mechanism test (section 6) removed all 10 on this host only. This host is not a run host; no run state was cleared.

Rule restated for the run: cookies minted during council-2 and Fix B testing persist in the run profile and are now run state. No step clears run-host cookies mid-run without coordinator approval. The F3 prover clears per-host cookies only inside its own gate checks (section 7), one host at a time, immediately before that host check, and records before and after counts. Clearing can re-wall tasks the shim alone cannot pass cold (council-2 round 6: stock Zen blocked on coolors from a cold profile), so any cookie-cleared failure is a fix limit with a per-task fallback decision, never a waive.

## 6. Cookie-clear mechanism (tested live in Fix B)

Mechanism: BiDi storage.deleteCookies, per exact domain form present, then one sweep with the bare domain. Implemented in probe-fixb.mjs delete mode and holder RPC op cookies_delete. Tested 05:58:17 on cloudflare.com only: before count 10 (domains www.cloudflare.com, .cloudflare.com, .www.cloudflare.com, including cf_clearance), after count 0. Log: fixb-evidence/cookies-delete-mechanism-test.log.

Exact prover steps per host (run with no holder session active; the probe opens its own short session):

1. node /tmp/fixb-runner/probe-fixb.mjs cookies <domain>  (record names and domains; confirm cf_clearance presence or absence)
2. node /tmp/fixb-runner/probe-fixb.mjs delete <domain>  (records delete_before and delete_after counts; after count must be 0)
3. node /tmp/fixb-runner/probe-fixb.mjs cookies <domain>  (independent re-read; must still be 0 before the drive starts)

Domains: coolors.co, chatgpt.com, timeanddate.com, openverse.org. Note: deleting chatgpt.com cookies also removes its sign-in session cookies in this profile. That is expected for the gate (the check needs a usable landing with prompt box, not a signed-in session), and the prover records it. Do not delete cookies for any other host.

## 7. F3 prover runbook (run cold, by a non-implementer)

You are the prover. You did not implement Fix B. Your job is to prove or break the pinned Proxy shim user-way, cookie-cleared, on the four run sites. If any of checks 1 to 4 fails cookie-cleared, record it as a fix limit and stop for a per-task fallback decision; do not waive, do not substitute direct navigation, do not fall back to warm-profile evidence.

Standing rules for every step: ponytail (reuse the Fix B files as-is; if a file needs a change, stop and report instead of editing silently); ydotool is banned (restate in every brief); pill on any agent control; one driver at a time; never close or navigate owner tabs, pinned tabs, or essentials; ws3 untouched; drives on ws2; SSH only via ~/workspace/ssh-laptop.sh; long jobs detached (setsid nohup ... > log 2>&1 < /dev/null & disown); never restart Zen or change launcher, wrapper, or prefs; full access; log every milestone via ~/workspace/agent-event-log/log-event.sh with source replan-prover; no personal info in any file; no commit.

User-path test: enter via search/homepage and click through like a normal user; no deep links, no direct commands, no internal setters; evidence shows entry, path, action, and resulting state.
User entry point for every site check: held blank tab, Ctrl+L, type the query, Return, click the first result on the SERP.
Forbidden shortcuts for every site check: deep link, BiDi navigate to the target, internal setters, test-only endpoints, DOM click, warm-profile reuse without the cookie clear in section 6.

Named search engine: DuckDuckGo, reached by typing the query in the Zen address bar and pressing Return (the run profile default; council-2 round 4 and Fix B both landed on duckduckgo.com SERPs this way). If the SERP host is not duckduckgo.com, stop and record it; do not switch engines mid-gate.

Setup (once):

1. Confirm the pause still holds and the machine is free: coordinator state epoch 9 paused; ~/workspace/ssh-laptop.sh 'computer-use status' returns ok; cursor lock free by /proc fd scan for cursor.lock; overlay status visible false; Zen window on ws2 (computer-use windows shows class zen on workspace 2; record its address, do not assume the Fix B address); ports 9222 and 2828 LISTEN.
2. Transfer the three harness files from improvements/fixb-evidence/ to /tmp/fixb-runner/ on the laptop with the base64 pipe method in section 3, then verify sha256 on the laptop equals: holder-fixb.mjs 70bfe8abbed9fdbec30a2cf323c61150322048ce2736dfe26186a1c075d4f213, probe-fixb.mjs 5329a574c7c7de6b003ad967d9706e75e589ce60c388f7a07f39f12dcf15c1f9, drive-fixb.py 6af74f2a4e03745504e9e9520019a9e5e097e943707ad01fe226c43e90d79f45. Verify the shim string inside holder-fixb.mjs hashes to bb49ff3f974a0534445fa5bb8eac48b47a378f39d944706b10118d5ff9d630b8 (the holder checks this at startup; also record it yourself).
3. Baseline probe: node /tmp/fixb-runner/probe-fixb.mjs probe. Expected without the shim: webdriver true, own_on_proto true, own_on_navigator false, get_name "get webdriver", get_tostring "function webdriver() { [native code] }". Record wall-clock Asia/Ho_Chi_Minh plus elapsed. If webdriver reads false here, stop: a session is leaked or the profile changed; report, do not drive.

Per-site check (run for each host in order: coolors.co, chatgpt.com, timeanddate.com, openverse.org):

Queries: coolors color palette generator (expect coolors.co), chatgpt (expect chatgpt.com), timeanddate world clock (expect timeanddate.com), openverse free images (expect openverse.org). These match council-2 round 4.

1. Clear cookies for this host only, exactly as section 6 (cookies, delete, cookies). After count must be 0. Record before and after counts with cookie names. Log the clear via log-event.sh.
2. Start the holder for this check (fresh BiDi session per site): clear /tmp/fixb-rpc and /tmp/fixb-gate, launch detached with display env exported from the live Zen process environ (WAYLAND_DISPLAY, XDG_RUNTIME_DIR, DBUS_SESSION_BUS_ADDRESS, HYPRLAND_INSTANCE_SIGNATURE, DISPLAY), pill acquired before the holder starts (overlay.py acquire --agent Prover --method "BiDi test" --pid <your pid>, label "Computer use active"; fail closed if visible is not true). Wait for /tmp/fixb-rpc/ready.json. Descriptor probe must read: webdriver false, own_on_proto true, own_on_navigator false, get_name "get webdriver", get_tostring "function () { [native code] }" (empty name, accepted risk, record verbatim). Any mismatch: stop the holder, release the pill, record FAIL for the gate, do not drive.
3. Search like a user: act-now Ctrl+L, type the query, Return. Wait, read SERP title and url via holder RPC evaluate. Observe the Zen window. The observe image must show the pill. Fetch the image to your workspace (base64 pipe, sha256 verified), view it, ground the first result title link, convert normalized 0 to 1000 coords to image pixels using the observation image_size, write /tmp/fixb-gate/coords.json atomically (tmp file then rename).
4. Click with real input: re-observe for freshness, act-now click at the grounded coords with that observation. Wait for landing. Read landing state via RPC: url host must match the expected host, title must be the real site title (not "Just a moment"), has_cf_challenge false, webdriver false, own_on_proto true, own_on_navigator false. Observe again; image must show usable content and the pill.
5. Interact like a user: coolors, scroll and open a palette if visible without deep-linking; chatgpt, click into the prompt box and type a short prompt (do not send anything that needs an account; typing alone proves the box); timeanddate, scroll; openverse, scroll and click a visible image or category link if present. Re-read state via RPC after the interaction; webdriver still false, no challenge. Observe again.
6. End the check: write /tmp/fixb-rpc/stop, wait for holder exit (preload_removed, context_closed, session_ended, done in holder log), release the pill, verify overlay status visible false. Record pass or fail per sub-check (clear, probe, SERP, click, landing usable, webdriver false, interaction, pill in images) with wall-clock plus elapsed for the whole check. Log the result via log-event.sh.
7. Path evidence per site (all required; end-state-only is returned unread): holder log, drive log lines, SERP observe image, landing observe image, interacted observe image, RPC landing JSON, cookie before and after logs. Name files with the site tag.

Fresh-session repeat: repeat the full per-site check for coolors.co and chatgpt.com once more from a brand-new holder session (new tab, shim reinstalled, cookies cleared again first). Same pass criteria. This proves the result is not a warm-session artifact.

Driving regression (once, with the shim installed): navigate by user path to a plain page (the SERP click already proves navigate plus real click), scroll, screenshot via observe, all act-now batches rc 0, pill acquires and releases cleanly, BiDi 9222 and Marionette 2828 still answer after (ss LISTEN plus a short probe session). Record each item pass or fail.

Descriptor probe (once, inside a shimmed session, data page): webdriver false, own_on_proto true, own_on_navigator false, get_name "get webdriver", get_tostring recorded verbatim (expected empty-name form). Compare against the baseline probe from setup. Record the toString difference as accepted risk, not as a fail, unless any other field differs.

Revert verify (last): after the final holder ends, run node /tmp/fixb-runner/probe-fixb.mjs probe. Expected: webdriver true, native toString restored. Confirm no holder or drive processes remain, pill visible false, tabs list shows no leftover prover tab (holder closes its own tab; if a tab remains, close only your own tab by context id and record it). Confirm run-host cookie state after the gate (names only) and record that the prover clears are now part of run state; the coordinator decides any re-warm before resume.

Pass and fail: the gate passes only if checks 1 to 4 pass cookie-cleared, both fresh-session repeats pass, the descriptor probe matches (toString difference recorded), driving regression passes, and revert verifies. Any failure in checks 1 to 4 cookie-cleared is recorded as a fix limit with the exact site, step, Ray ID if shown, and screenshots; the coordinator then makes a per-task fallback decision (Chromium lane per task with scorer agreement, or INVALID path). The prover never waives, never retries with cookies restored to manufacture a pass, and never substitutes direct navigation. Stock-launch webdriver read (council-2 gate check 8) is out of scope for this runbook; it failed for harness reasons in round 6 and proves nothing about the shim.

Cleanup: rm -rf /tmp/fixb-rpc /tmp/fixb-gate only after evidence is copied to the VM; keep /tmp/fixb-runner until the coordinator says otherwise (it is the integration the runners will use). Copy all logs and images to improvements/fixb-evidence/prover/ (create it) with sha256 list. Log completion via log-event.sh.

## 8. What Fix B did not do

- No F3 site checks were run by Fix B (implementer and prover stay separate). The held-out drive used cloudflare.com, not a run site.
- No repo files were edited or committed. zen_dom.py, zen_cli.py, first_action.py, launcher, wrapper, and prefs are untouched (hashes in section 2).
- No run-host cookies were cleared. Only cloudflare.com cookies were deleted, for the mechanism test.
- No coordinator state was edited, no run task was released, no message was sent to the owner or parent by Fix B. Milestones were logged to the master event log only.
- Google sorry (R3-022 class) remains uncovered, as in council-2. Managed click-tier Turnstile and Precursor Armed mode remain unproven; the F3 gate tests the actual run sites and records limits honestly.

## 9. Evidence index (improvements/fixb-evidence/)

- holder-fixb.mjs, probe-fixb.mjs, drive-fixb.py: harness sources (hashes in section 3).
- drive-fixb.log: full drive log, attempts 1 to 3 appended. holder-fixb.log: attempt 3 holder log. drive-attempt2.log, holder-attempt2.log: attempt 2 preserved. drive-stdout-attempt3.log: attempt 3 stdout including the attempt 2 traceback context.
- serp-cloudflare.jpg (attempt 2 SERP), serp-cloudflare-attempt3.jpg (attempt 3 SERP), landing-cloudflare.jpg, interacted-cloudflare.jpg: observe images, pill visible in SERP and landing frames.
- probe-baseline-cookies-before.log: baseline descriptor (webdriver true) plus pre-drive cookie inventories. probe-revert.log: post-drive revert descriptor (webdriver true).
- cookies-cloudflare-after-drive.log, cookies-delete-mechanism-test.log (10 to 0), cookies-after-all.log (coolors and openverse unchanged).
- ports-pill-cleanup.log: listeners, pill status, windows, process and tab cleanup checks.
