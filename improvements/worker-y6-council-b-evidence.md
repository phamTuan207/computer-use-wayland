# Council Member B audit: Worker Y6 hyprglass nested probe evidence

- Date: 2026-11-21, audit run ~18:28 to ~18:45 +07
- Auditor: Council Member B (evidence and method)
- Subject: improvements/worker-y6-hyprglass-nested-probe.md (Y6 draft report)
- Method: every load-bearing claim re-checked against raw artifacts on the laptop via short read-only ssh calls only. No launch, no live-session drive, no config edit. All commands were reads (ls, cat, sha256sum, strings, nm, coredumpctl, ps, hyprctl version/clients/plugin list).

## Overall verdict

SOUND with corrections. The load-bearing facts hold: 5 distinct launches, 5 identical crashes at CBackend::create(), seat failure as proximate cause, no AQ_BACKENDS string, both hashes exact, live session untouched, notification explained by Y6's own dumps. No claim is refuted outright. But the report overstates in four places (attempt 4, "most complete" tail, "even for headless" as proven, notification attributed to all 5), the per-attempt env for attempts 1, 2, 4, 5 is report-only with no launch artifact, and the Wayland-nested design is not runnable as written (two files do not exist yet). Fix the items in "What must be fixed" before the report goes final. The headless verdict stands in its narrow form: the attempted configuration cannot start. The stronger form (the headless backend itself needs a seat) was never directly observed, because headless was never reached.

## Per-claim verdicts

### 1. Five distinct launches with the env claimed

Verdict: CONFIRMED that 5 distinct launches happened and crashed. UNVERIFIED for the per-attempt env of attempts 1, 2, 4, 5.

Evidence for 5 distinct launches (independent artifacts agree to the second):
- 5 stdout logs: /tmp/y6-nested/hyprland.log, hyprland2.log, hyprland3.log, hyprland4.log, hyprland5.log, mtimes 18:20, 18:21, 18:22, 18:23, 18:24.
- 5 crash reports: hyprlandCrashReport215337.txt (18:20), 217032.txt (18:22), 217712.txt (18:22), 218283.txt (18:23), 219789.txt (18:24).
- 5 coredumps (see claim 6): 18:20:16, 18:22:00, 18:22:35, 18:23:03, 18:24:52, PIDs 215337, 217032, 217712, 218283, 219789.
- 5 per-instance run dirs under /tmp/y6-nested/run/hypr/ with distinct epoch suffixes 1795260016, 1795260119, 1795260155, 1795260183, 1795260292 (gaps 103s, 36s, 28s, 109s, matching the coredump gaps 104s, 35s, 28s, 109s).
- All 5 stdout logs end with the same two lines: "terminate called after throwing an instance of 'std::runtime_error'" and "what(): CBackend::create() failed!" Each names its own crash report file.

Env gaps:
- Only attempt 3 has a launch artifact: /tmp/y6-nested/run-nested.sh sets XDG_RUNTIME_DIR=/tmp/y6-nested/run, WAYLAND_DISPLAY=wayland-y6, WLR_BACKENDS=headless, AQ_BACKENDS=headless, unsets HYPRLAND_INSTANCE_SIGNATURE. Its logind EBUSY line (claim 2) corroborates it ran as a live-session child.
- Attempts 1, 2, 4, 5 have no saved launch script or command. The logs record no env vars. Attempts 1 and 2 are byte-identical apart from run-dir suffix and PID, so the claimed difference (WLR only vs WLR plus AQ) is not distinguishable from any artifact. It rests on Y6's word alone.
- Attempt 4 is CONTRADICTED on its own terms. The report says attempt 4 ran with debug.enable_stdout_logs=true in config. The conf file on disk now does contain enable_stdout_logs = true (mtime 18:23), but ALL FIVE stdout logs print "[Config::Lua::CConfigManager::postConfigReload] Disabling stdout logs (debug.enable_stdout_logs = 0)", including attempt 5 at 18:24. The setting never took effect in any attempt. Attempt 4 is therefore observationally identical to attempt 1, and "no extra backend lines" is vacuous: the Aquamarine lines exist only in the crash-report tails, which all five attempts have.
- Attempt 3 framing needs correction. The report calls it "real graphical session" via hyprctl dispatch. It did run as a live child (logind EBUSY line proves session context), but run-nested.sh still set WAYLAND_DISPLAY=wayland-y6, a nonexistent socket, so it never tried the live Wayland display. The Wayland backend failure line in its tail is failure to connect to wayland-y6, not to the live compositor.
- Per-instance hyprland.log files under /tmp/y6-nested/run/hypr/*/ are all 0 bytes (crash happened before any log was written there). They add no evidence either way.

### 2. Root cause: Aquamarine needs a libseat seat even for headless

Verdict: CONFIRMED in narrow form (seat failure is the proximate cause of all 5 crashes). The extension "even for headless" is INFERENCE, not direct observation. Two wording errors in the report.

Exact log tail, shared by all 5 crash reports (quoted from 219789.txt; 215337, 217032, 218283 identical except the seatd line, see below):

```
DEBUG from aquamarine ]: Creating an Aquamarine backend!
ERR from aquamarine ]: [libseat] [libseat/backend/seatd.c:66] Could not connect to socket /run/seatd.sock: Permission denied
DEBUG from aquamarine ]: [libseat] [libseat/libseat.c:76] Backend 'seatd' failed to open seat, skipping
DEBUG from aquamarine ]: [libseat] [libseat/libseat.c:76] Backend 'logind' failed to open seat, skipping
ERR from aquamarine ]: [libseat] [libseat/libseat.c:79] No backend was able to open a seat
ERR from aquamarine ]: libseat: failed to open a seat
ERR from aquamarine ]: Failed to open a session
ERR from aquamarine ]: DRM Backend failed
DEBUG from aquamarine ]: Starting the Aquamarine backend!
DEBUG from aquamarine ]: Starting the Wayland backend!
ERR from aquamarine ]: Wayland backend cannot start: wl_display_connect failed (is a wayland compositor running?)
ERR from aquamarine ]: Requested backend (wayland) could not start, enabling fallbacks
ERR from aquamarine ]: Implementation wayland failed, erasing.
CRIT from aquamarine ]: Cannot open backend: no allocator available
```

Differences by attempt (the report misses these):
- Attempts 1, 2, 4: seatd line is seatd.c:64 "Could not connect to socket /run/seatd.sock: No such file or directory".
- Attempt 5: seatd.c:66 "Permission denied", proving a seatd socket existed at that time. This corroborates seatd having been started before attempt 5.
- Attempt 3 is the most complete tail, not attempt 5. It adds a line the others lack: "[libseat] [libseat/backend/logind.c:309] Could not take control of session: Device or resource busy". The report says "Attempt 4/5 crash reports contain the Aquamarine log tail. Attempt 5 is the most complete." Both halves are wrong: ALL FIVE contain the tail, and attempt 3 has the extra logind line.
- Backtrace confirmed identical in all 5: #11 std::__throw_bad_any_cast(), #12 CCompositor::initServer, signal 6 (ABRT), version 11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947, tag v0.57.2, Aquamarine built against 0.16.0, system has 0.16.0. (Note: the "Date: Mon Nov 9 11:05:46 2026" line in every crash report is the build date, not the crash date. Do not cite it as crash time.)

What follows and what does not:
- Follows: a libseat seat open is attempted during CBackend::create() before any backend starts, it fails in all 5 attempts, and the fallback chain (DRM failed, Wayland failed, no allocator) then throws. Seat failure is the proximate cause of all 5 crashes.
- Follows with a caveat: logind exclusivity. Only attempt 3 shows the logind reason, "Could not take control of session: Device or resource busy", which is the best evidence that the live session holds the seat. The mechanism name (logind TakeControl is exclusive) is inferred from that EBUSY line, not from a logind-side record. "Strongly supported" is the right strength, not "proven".
- Does NOT follow directly: "needs a seat even for headless". No attempt ever selected headless: AQ_BACKENDS does not exist (claim 3), WLR_BACKENDS is unread, and the log sequence never mentions a headless backend attempt. The inference is reasonable (seat open precedes backend dispatch in the log order), but the report must label it inference. The proven statement is: the attempted configuration cannot start because the seat open fails first.
- Seatd sub-claim: seatd binary exists (/usr/bin/seatd), seatd.log confirms "Created VT-bound seat seat0" and "seatd started", then "seatd stopped" after 00:01:47. The attempt-5 EACCES line confirms the permission failure. The socket permission detail in the report ("srwxr-xr-x root root") is UNVERIFIED now: the socket is gone (see claim 5), no surviving record of its mode. Keep the EACCES line as the evidence, drop or soften the mode claim. The seatd PID 219625 likewise has no surviving record; seatd.log plus EACCES prove seatd ran during attempt 5, not the PID.

### 3. AQ_BACKENDS does not exist in libaquamarine 0.16.0

Verdict: CONFIRMED, recomputed by me.

- /usr/lib/libaquamarine.so.0.16.0, 1,417,176 bytes. Symlink chain: libaquamarine.so -> libaquamarine.so.15 -> libaquamarine.so.0.16.0.
- strings plus grep for AQ_BACKENDS, AQ_DRM_DEVICES, WLR_BACKENDS returns only AQ_DRM_DEVICES lines (the variable name and the hint "set AQ_DRM_DEVICES to disambiguate"). Zero hits for AQ_BACKENDS, zero hits for WLR_BACKENDS.
- Cross-check on /usr/bin/Hyprland: strings grep returns 0 hits for both AQ_BACKENDS and WLR_BACKENDS. Neither the compositor nor its backend library reads those variables.
- Headless backend existence confirmed independently: strings and nm -D on libaquamarine.so.0.16.0 show CHeadlessBackend and CHeadlessOutput symbols (for example _ZN10Aquamarine16CHeadlessBackend5startEv, CHeadlessOutput4testEv). The code exists; it was never reached in any attempt.
- Caveat on method: strings proves no literal env name in the binary. A name constructed at runtime would not appear, but for a getenv-style lookup this is the standard check, and the crash logs independently show no headless attempt.

### 4. .so identity claims (both sha256s recomputed)

Verdict: CONFIRMED, both hashes recomputed by me.

- Backup 1: ~/.local/share/agent-computer-use/backups/full-1791544423/native/hyprglass.so, 26,643,888 bytes, sha256 2671d4ac41941ca62ae8100fc3b57bf3153bf6def893334f3a8ecbc1ea0145d5. Matches the report exactly.
- Backup 2: ~/.local/share/agent-computer-use/backups/sync-20261116-230254-783160-a9a24690/trees/native/hyprglass.so, 30,622,520 bytes, sha256 ddfff1c2f2cebb66e10b85a739beae0c7c562ccf9d78e3250647c07f8f31fa8b. Matches the report exactly. Different build, not used.
- Vendor copy: ~/.local/share/agent-computer-use/vendor/hyprglass/hyprglass.so, 26,643,888 bytes, sha256 2671d4ac41941ca62ae8100fc3b57bf3153bf6def893334f3a8ecbc1ea0145d5. Identical to backup 1, as claimed. Correction for the report: name this laptop path explicitly. The bare path "vendor/hyprglass/hyprglass.so" does not exist in the VM repo checkout (no vendor/ dir there, git ls-files shows no hyprglass.so), so a reader of the repo alone cannot verify it.
- Backup 1 is ELF 64-bit LSB shared object, x86-64, BuildID 1fd1cf18ea1648b70ddd779ec4c49fc8304da1e1, with debug_info, not stripped.
- nm -D on backup 1 shows __hyprland_api_get_client_hash and pluginAPIVersion, as claimed.
- No version string embedded: strings on backup 1 shows only "Hyprnux" for the name/version area, no 1.1.1 string. The report is correct that plugin version 1.1.1-cu.1 is UNVERIFIED until a successful load.
- Installed tree check: ~/.local/share/agent-computer-use/native/ contains NO hyprglass .so (only hyprglass-LICENSE, patches, and lua files), matching the report and the decision doc.
- Live Hyprland version confirmed via hyprctl: 0.57.2, commit 11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947. Terminals foot and kitty both present (/usr/bin/foot, /usr/bin/kitty).
- Optics profile values confirmed in repo native/hyprglass-local-optics.lua: blur_strength 0.15, refraction_strength 0.55, layers enabled = true. Small precision gap: the report says "mask_mode contour". The lua file has layers mask_mode "region" at line 26 and a "contour" mask_mode at line 37 in a different context. Quote precisely or drop the mask_mode shorthand.

### 5. Live-session safety

Verdict: CONFIRMED.

- Live PID 1515 alive at my check, started Sat Nov 21 15:17:25, elapsed 03:10:58. That start predates the whole probe window (18:17 to 18:28), so the same live process survived it.
- hyprctl responds: "Hyprland 0.57.2 built from branch v0.57.2 at commit 11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947". Live instance signature 11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795249046_1138556825, consistent with a 15:17 start.
- hyprctl clients shows a mapped window: omarchy terminal 1574x816, special:herdrdrop, as the report states.
- pgrep Hyprland returns only PID 1515 (with --watchdog-fd 4). No nested Hyprland process survives.
- Live configs untouched: ~/.config/hypr/hyprland.lua mtime 2026-11-16 04:50:46, ~/.config/hypr/agent_computer_use_glass.lua mtime 2026-11-15 01:58:31, both days before the probe. No file under ~/.config/hypr/ has a mtime in 18:17 to 18:28 on 2026-11-21 (nearest are autostart.lua 17:38 and bindings.lua 17:36, both before the probe).
- Live plugin list shows only hyprbars v1.0. No hyprglass loaded in the live session.
- Cleanup confirmed: no seatd process (pgrep exit 1), /run/seatd.sock gone, matching the report's 18:28 cleanup claim.
- Limit: my check ran after the probe, not at 18:23:33. The contemporaneous 18:23:33 check is Y6's own and cannot be re-verified now, but the 15:17 start time plus the current responsive state prove the same live process lived through the window.

### 6. Crash-notification attribution

Verdict: CONFIRMED with a timing correction. The notification was caused by the first four dumps, not all five.

- coredumpctl lists exactly 5 Hyprland SIGABRT coredumps on 2026-11-21: 18:20:16 PID 215337, 18:22:00 PID 217032, 18:22:35 PID 217712, 18:23:03 PID 218283, 18:24:52 PID 219789. All COREFILE present, 1M each. PIDs and times match the report's table.
- No other Hyprland coredump exists on 2026-11-21. The only other Hyprland coredumps nearby are 2026-11-14 00:44:34 PID 1701 (SIGABRT) and a 2026-11-13 SIGSEGV cluster, none of which can explain an 18:23 notification on 2026-11-21.
- Crash-report dir on 2026-11-21 contains only those 5 reports. Older reports are Nov 14, Oct 15, Oct 10.
- Correction: the notification appeared ~18:23. At that moment only four dumps had happened (18:20:16, 18:22:00, 18:22:35, 18:23:03). The fifth dump is 18:24:52, after the notification. The report's incident section attributes the notification to "my 5 nested attempts" and lists the fifth as "~18:25". Say instead: the notification was caused by the first four; the fifth followed at 18:24:52. This matches the memory note that counts 4 coredumps 18:20 to 18:23 at notification time.

## Reproduction design judgement (Wayland-nested, not yet run)

### Preconditions: partly checkable, partly assumed

1. "No Zen runner active: flock on zen_dom.lock free AND no run_agyq2/run_live/E1 process AND Muse confirms no runner scheduled in the next 30 minutes." The first two parts are checkable: the lock file exists (~/.cache/agent-computer-use/zen_dom.lock, 0 bytes, mtime 17:48) and runner processes are visible via ps. The third part names no check and no confirmer. Fix: name who confirms (parent agent, by what check) or replace it with a concrete check.
2. "Owner away (handover confirmed 18:24, still in force)." A handover is time-bound. A later run must re-confirm it at run time, not assume it is still in force.
3. "seatd NOT required (Wayland backend needs no seat)." This is an assertion, not a checkable precondition. Reframe it as an assumption the run itself tests. If the Wayland backend also demands a seat, the run fails at the same place and that is a result, not a precondition violation.

### GO/NO-GO criteria: mostly sharp, two gaps

- Sharp parts: GO needs nested starts, plugin loads, version 1.1.1-cu.1, layers.active=true after the profile. NO-GO covers nested crash, plugin refusal, version mismatch, shaders not ready after 30 s. That is usable.
- Gap 1: no abort rule if a runner starts mid-run or the nested window steals focus during the run. Precondition 1 is the only guard, and it only covers run start.
- Gap 2: "shaders never become ready after 30 s" should be tied to the already-defined readiness (layers.active=true via indicator.liquid_available), not restated loosely. Also the "live activation needed ~8 s" figure is borrowed, not evidenced in this probe: the plugin was never loaded anywhere here. Mark it as borrowed.

### Steps that could touch the live session

- The nested window itself: by design a 960x540 window opens on the live screen and steals focus. The design acknowledges this and guards it only with precondition 1. Acceptable if the precondition is made concrete (see above), plus a mid-run abort rule.
- Launch via hyprctl dispatch Lua os.execute: attempt 3 proves this dispatch path works and launches a live child, so the mechanism is proven. But the design is NOT runnable as written: /tmp/y6-nested/run-nested-wayland.sh and /tmp/y6-nested/conf/hyprland-wayland.conf do not exist yet. Both must be created and reviewed before the run is claimed ready.
- `HYPRLAND_INSTANCE_SIGNATURE="$(ls /run/user/1000/hypr/ | head -1)"`: unordered pick. If a stale entry ever appears under /run/user/1000/hypr/, it could target the wrong instance. Pin it deterministically, for example from the live PID 1515 start-time-anchored entry, or from the live process environ.
- Step 3 reloads the nested compositor with a sourced lua profile. A bad source line kills only the nest, not live, but the design does not say how a failed nested reload is detected. Add a check (nested hyprctl still responds, or nest PID alive) before proceeding to step 4.
- Step 5 runs scripts/indicator.py against the nest. Nothing in the design verifies indicator.py honors the nested env (it may hardcode live socket paths or the live instance signature). Verify that before the run, do not assume it. Same for the paint-callback counting method: it is the live measurement method per the decision doc, but its applicability inside the nest is assumed, not shown.
- Step 4 grim usage is sound as specified (confirm the output name from hyprctl -j monitors inside the nest; the config names it WAYLAND-1).
- Missing teardown: the design has no cleanup step. The headless probe left run dirs behind; the Wayland nest needs a defined teardown (kill nested PID, confirm its window is gone, confirm live hyprctl still responds, confirm no hyprglass in the live plugin list). Add it.

## What must be fixed in the report before it is final

1. Attempt 4: correct or drop the stdout-logs claim. All five logs show debug.enable_stdout_logs = 0, so the setting never took effect. Either re-run a real stdout-logs attempt with a config that takes effect, or state plainly that attempt 4 duplicates attempt 1 observationally.
2. Attempt table env column: mark attempts 1, 2, 4, 5 env as report-only (no launch artifact saved). Save the launch command or script for every future attempt. Clarify attempt 3 never pointed at the live Wayland display (WAYLAND_DISPLAY was wayland-y6 in run-nested.sh).
3. Root-cause wording: change "Attempt 4/5 crash reports contain the Aquamarine log tail. Attempt 5 is the most complete." to "All five crash reports contain the Aquamarine log tail. Attempt 3 is the most complete (extra logind.c:309 line)." Downgrade "Aquamarine needs a seat even for headless" from proven to inference, with the reasoning (seat open precedes backend dispatch; headless never reached). Downgrade logind exclusivity from "proven" to "strongly supported by the attempt-3 EBUSY line".
4. Notification attribution: the ~18:23 notification was caused by the first four dumps; the fifth is 18:24:52, after the notification.
5. Vendor path: name the laptop path ~/.local/share/agent-computer-use/vendor/hyprglass/hyprglass.so explicitly, since vendor/ does not exist in the repo checkout.
6. Soften the two unverifiable details: seatd socket mode (keep the EACCES line as the evidence) and seatd PID 219625 (no surviving record; seatd.log plus EACCES prove seatd ran).
7. Optics profile: fix or drop the "mask_mode contour" shorthand (lua has layers mask_mode "region" at line 26 and "contour" at line 37 in a different context).
8. Design: create run-nested-wayland.sh and hyprland-wayland.conf before claiming the design runnable; re-confirm handover at run time; make the runner-free check concrete with a named confirmer; add a mid-run abort rule for focus steal or a runner starting; add a teardown step; pre-verify indicator.py honors the nested env; pin the live instance signature deterministically.
9. Note the crash-report "Date: Mon Nov 9 11:05:46 2026" is the build date, so nobody cites it as crash time later.

## Gaps found (summary)

- Sharpest gap: attempt 4 is not a distinct experiment. Its claimed distinguishing condition (stdout logs on) is contradicted by its own log, which prints enable_stdout_logs = 0 like all the others, and its env has no launch artifact. The five attempts collapse observationally to: two SSH attempts with indistinguishable env (1, 2), one live-child attempt (3, the only one with a script and the only one with the logind EBUSY line), one SSH attempt indistinguishable from attempt 1 (4), and one SSH attempt distinguished only by the seatd EACCES line (5).
- Second gap: the design references two files that do not exist yet, so it cannot run as written.
- Third gap: the report's strongest sentence ("needs a seat even for headless", stated as proven) goes one step past what the logs show, because no attempt ever reached a headless backend.
