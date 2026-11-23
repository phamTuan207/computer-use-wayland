# Council A (feasibility): position paper on Worker Y6 hyprglass nested probe

- Date: 2026-11-21, 18:27-18:45 +07
- Council member: A (feasibility). Worker: Y6 (Muse subagent). Branch: todolist-push.
- Sources read: improvements/worker-y6-hyprglass-nested-probe.md (Y6 draft), docs/decision-2-2-3-hyprglass-test-20261121.md (Worker X decision doc).
- Raw evidence re-checked read-only via ssh-laptop.sh: /tmp/y6-nested/hyprland*.log (5 logs), ~/.cache/hyprland/hyprlandCrashReport21*.txt (5 reports), /tmp/y6-nested/conf/hyprland.conf, /tmp/y6-nested/run-nested.sh, /tmp/y6-nested/run/hypr/*/hyprland.log, session/group/device state. No launch, no write, no touch of the live session.
- Upstream code read: hyprwm/aquamarine src/backend/Backend.cpp (commit 4c72cd4, fetched 2026-11-21), Hyprland wiki environment variables page, seatd man page, libseat seatd backend source notes.

## Verdict: PARTIAL

AGREE with the narrow claim: headless nested Hyprland exactly as Y6 ran it is deterministically dead on this machine. DISAGREE with the broad claim as written: "HEADLESS nested Hyprland DOES NOT WORK on this machine" is NOT proven. Y6 tested one configuration family five times, not the headless space. Two concrete mechanisms that supply what actually failed were never tried: a correctly permissioned seatd seat (seatd-launch) plus a real DRM fd (render node, or a vkms virtual device). The strongest missed path is Path A below. The Wayland-nested path Y6 already designed remains the highest probability route overall and should run first.

## What Y6 proved (concede these)

1. The failure mode is deterministic. All 5 attempts crash identically at CBackend::create(), backtrace frame std::__throw_bad_any_cast in CCompositor::initServer, 5 coredumps 18:20-18:24 SIGABRT. The 5 nested hyprland.log files in /tmp/y6-nested/run/hypr/*/ are all 0 bytes, so the crash-report log tails are the only backend record, and they agree.
2. The logind seat is genuinely unavailable to a second compositor in the live session. Attempt 3 is the proof, and it is stronger than Y6's wording: its log tail says `[libseat/backend/logind.c:309] Could not take control of session: Device or resource busy`. The live session is session 2, seat0, tty1, Type=wayland, Active=yes (verified via loginctl 2026-11-21 18:30). TakeControl is exclusive and the live Hyprland holds it. This part of the root cause stands.
3. The allocator wall is structural, not incidental. Aquamarine Backend.cpp CBackend::start() builds the primary allocator ONLY from an implementation with drmFD() >= 0 (lines 207-227 in the fetched source), and returns false with "Cannot open backend: no allocator available" when none qualifies. The headless backend's drmFD() returns -1 (corroborated by the Omarchy WSL2 writeup, which verified this against Aquamarine source: headless is no escape hatch, its drmFD returns -1, so it hits the same wall). Consequence Y6 did not state: a headless-only backend can NEVER satisfy CBackend::start() by itself. Headless needs a DRM fd from somewhere else (a DRM backend, or a Wayland parent that supplies one via dmabuf). This strengthens the verdict for pure headless, and reframes the fix: the next attempt must supply a DRM fd, not just a seat.
4. The plugin line did NOT cause the crash. Hyprland initializes CPluginSystem in STAGE_LATE, after the backend and protocols are active, while the crash happens earlier in initServer during backend creation. No "plugin" string appears in any of the 5 attempt logs (grep, verified), and no plugin frame appears in any backtrace. The plugin-as-trigger hypothesis is refuted on ordering grounds.

## What Y6 did NOT prove (the attack)

### 1. Five attempts were one test, not five

All 5 attempts share the same broken seat, the same nonexistent WAYLAND_DISPLAY=wayland-y6, and the same config. The only variations were cosmetic env vars (WLR_BACKENDS, AQ_BACKENDS) that Aquamarine does not read. "5 identical crashes" proves the failure is deterministic, not that the space is exhausted. In particular:

- The Wayland backend was never genuinely tried in any attempt. Every log tail shows `Wayland backend cannot start: wl_display_connect failed`, because WAYLAND_DISPLAY pointed at a nonexistent socket in all 5 attempts, including attempt 3, whose launcher script overwrote the live session env (XDG_RUNTIME_DIR=/tmp/y6-nested/run, WAYLAND_DISPLAY=wayland-y6). Attempt 3 therefore does NOT test a Wayland-parent connection at all. Y6 already knows this and designed the Wayland-nested run separately, but the attempt table must not be read as evidence against nested Wayland.
- The env-var conclusion is overbroad. Y6 correctly found AQ_BACKENDS and WLR_BACKENDS do nothing (no AQ_BACKENDS string in libaquamarine.so.0.16.0, verified). But the env vars that DO matter for Aquamarine were never tried: AQ_DRM_DEVICES (explicit DRM device list, documented on the Hyprland wiki), AQ_NO_KMS_REQUIREMENT (disable KMS requirement for starting on headless GPUs, documented), AQ_TRACE (trace logging), LIBSEAT_BACKEND (force logind or seatd), SEATD_SOCK (seatd socket path). The right vars were never in the room.

### 2. The seatd attempt failed on permissions Y6 never fixed (strongest missed path, part 1)

Attempt 5 started seatd as root with default socket ownership. The socket came up root:root, and the nested process got EACCES (`Could not connect to socket /run/seatd.sock: Permission denied`). Two facts Y6 did not check:

- `seatd -h` on this machine offers `-u <user>` (user to own the socket) and `-g <group>` (group to own the socket). Y6 used neither.
- `/usr/bin/seatd-launch` IS installed on this machine (verified). seatd-launch is the purpose-built tool for exactly this: it starts seatd as root, chowns the socket to the target user, chmods it 0700, sets SEATD_SOCK, drops privileges, then runs the command. Y6 ran raw seatd and stopped at the first EACCES instead of using seatd-launch or `seatd -u user`.
- The user is not in the seat group (getent group seat: gid 965, no members) and not in the video group (getent group video: only ollama). The EACCES was therefore fully predictable from the launch method, and fully fixable in one command. It is not evidence that seatd cannot serve a seat here.

Caveat, stated honestly: fixing the socket only gets past the connect step. Whether a seatd seat and the logind seat can coexist on the same VT without fighting over input or VT switching is UNVERIFIED. seatd is normally run INSTEAD of logind, not alongside it. The coexistence question, not the permissions question, is the real unknown in Path A. Any attempt must run in a runner-quiet window with seatd killed immediately after and the live session re-verified.

### 3. No attempt ever supplied a DRM fd (strongest missed path, part 2)

Even with a working seat, the DRM backend still has to open a GPU. Y6 never gave it a usable one:

- /dev/dri/card1 (NVIDIA) and card2 (Intel) are root:video mode 660, and the user is NOT in the video group, so the nested process cannot open the primary nodes directly. The render nodes are world accessible (crw-rw-rw- root render): renderD128 is the NVIDIA render node, renderD129 is the Intel render node (verified via /dev/dri/by-path: pci-0000:01:00.0-render is renderD128, pci-0000:00:02.0-render is renderD129).
- AQ_DRM_DEVICES=/dev/dri/renderD128 (or renderD129) would point the DRM backend at a render node, and AQ_NO_KMS_REQUIREMENT=1 would drop the KMS requirement a render node cannot satisfy. Neither was tried. This combination has a real mechanism to produce a drmFD >= 0, which is exactly what CBackend::start() needs to build the GBM allocator. It is UNVERIFIED whether Aquamarine's DRM backend accepts a render-only node and starts on it, but it is a two-variable, ten-minute test, and it is the only headless-shaped path that addresses the allocator wall instead of only the seat wall.
- The live Hyprland holds DRM master on the real GPUs, so a second DRM master is impossible, but a render node does not need master. That distinction is why the render-node path is not blocked by the same exclusivity that blocks logind TakeControl.

### 4. vkms: a virtual DRM device exists on disk and was never considered

`modinfo vkms` on this machine reports vkms.ko.zst present in the running kernel tree (7.2.15-1-omarchy), not loaded. vkms is a virtual KMS driver: loading it creates a new /dev/dri/cardN plus render node that no live session holds, with real KMS support, so AQ_NO_KMS_REQUIREMENT would not even be needed. Combined with seatd-launch (for the seat) and AQ_DRM_DEVICES pointing at the vkms card, this is a complete headless stack that touches no real GPU and no VT. UNVERIFIED whether Aquamarine starts on vkms and whether GBM allocator creation and EGL init succeed there (hyprglass needs working GL; vkms rendering would likely fall back to software GL, which is fine for a flicker repro but slower). Cost is a sudo modprobe plus a sudo rmmod to unload, both reversible. Risk to the live session is LOW, lower than Path A, because vkms creates a new device instead of contending for an existing one. It still inherits the seatd coexistence unknown from Path A.

### 5. Candidate paths that are NOT worth trying (ruled out, with reasons)

- Fresh TTY login session (Ctrl+Alt+F3, second Hyprland on another VT): a new logind session could plausibly TakeControl, but switching VT deactivates session 2, which blanks the live GUI and pollutes every Zen runner observation. HIGH risk to the live session, and it answers a question option A already answers better. Do not try while the live session matters.
- systemd-run user scope: same logind session, no new seat, same TakeControl failure expected. Cheap (2 minutes) but predicts the same outcome; only worth it as a one-line disproof if someone insists.
- LIBSEAT_BACKEND / SEATD_SOCK alone: these only select which seat backend is tried first or where the socket lives. They change nothing about TakeControl being busy or the socket perms. Not paths by themselves.
- XDG_SESSION_TYPE: setting it does not create a seat. Not a path.
- cage / weston as a parent compositor: neither is installed (verified: no cage, no weston binary). weston 15.0.1-3 is available in the extra repo, and weston with its headless backend could parent a nested Hyprland without touching the live session at all. But Aquamarine's Wayland backend requires zwp_linux_dmabuf_v1 from the parent, and whether weston's headless backend advertises it is UNVERIFIED. This is strictly dominated by Y6's Wayland-nested design, which uses the already-running parent (live Hyprland, which does advertise dmabuf). Install weston only if the Wayland-nested run fails AND the dmabuf question is answered first.

## Candidate paths table (what to try, proof bar, cost)

### Path C (first): Wayland-nested under the live compositor, Y6 design as written

- What: run Y6's incident-reproduction design verbatim (960x540 window, WAYLAND_DISPLAY=wayland-1, real session env, plugin line included). Needs no seat, no root, no VT switch. The parent supplies the DRM fd via dmabuf, which is the only proven allocator source in this situation.
- Proof bar: a Hyprland window appears on the live screen, hyprctl inside the nest responds, `hyprctl -j plugin list` shows hyprglass, status shows version 1.1.1-cu.1 and layers.active=true after the optics profile.
- Cost: LOW risk (one window, brief focus steal, run only in a runner-quiet window), about 15 minutes. Highest probability of the four paths. Run this first.

### Path A (second): seatd-launch plus render-node DRM

- What, exact: `seatd-launch` wrapping the nested launch (it chowns the socket to the user and sets SEATD_SOCK), with AQ_DRM_DEVICES=/dev/dri/renderD128, AQ_NO_KMS_REQUIREMENT=1, LIBSEAT_BACKEND unset (let seatd win), and the plugin line REMOVED from the config as a cheap control (the crash cause is already refuted, but a no-plugin control costs nothing and closes the question empirically). Same isolated runtime dir and display name as Y6. Kill seatd immediately after the attempt, then re-verify live PID 1515 and hyprctl.
- Proof bar: log shows `Seat opened with backend 'seatd'`, DRM backend starts, a GBM allocator is created (no "no allocator available" line), the nested process stays alive over 30 seconds, `hyprctl -j monitors` inside the nest shows HEADLESS-1. Then re-add the plugin line and check plugin load.
- Cost: MODERATE risk. The open unknown is seatd versus logind coexistence on one VT: a VT switch fight or input grab is possible, though the nested process holds no input devices. Mitigate with a runner-quiet window, a timeout kill, and immediate live-session verification. About 10 minutes plus verification.

### Path B (third): vkms virtual DRM plus seatd-launch

- What, exact: sudo modprobe vkms, confirm a new /dev/dri/cardN appears, then seatd-launch wrapping the nested launch with AQ_DRM_DEVICES=/dev/dri/cardN (the vkms card), no AQ_NO_KMS_REQUIREMENT (vkms has KMS), plugin line removed as control. sudo rmmod vkms and kill seatd immediately after, then re-verify the live session.
- Proof bar: same alive checks as Path A, plus GBM allocator creation on the vkms fd. If the backend starts but EGL falls back to software GL, that still counts as a working nest for the flicker repro (note it in the log).
- Cost: LOW risk to the live session (new virtual device, no real GPU, no VT), but needs sudo for modprobe/rmmod and inherits the seatd coexistence unknown from Path A. About 15 minutes. Try only if Path A fails at the seat or DRM step, since Path B shares the seat step and adds a kernel module.

### Path D (do not try now): fresh TTY login session

- What: login on another VT, start Hyprland there with the plugin loaded.
- Proof bar: would be a second graphical session with its own seat.
- Cost: HIGH risk. VT switch deactivates the live session and pollutes runner observations. Revisit only if C, A, and B all fail AND the owner explicitly accepts a handover window, at which point option A from the decision doc (load the plugin live) is the better use of that window anyway.

## What I would do next (ordered)

1. Run Path C (Y6 Wayland-nested design) in the next runner-quiet window. It is the only path that needs no seat and no root, and it is the only one whose allocator source (parent dmabuf) is already known to exist.
2. If C fails, run Path A (seatd-launch plus render node) with the plugin line removed as control. If A fails at the seat step (seatd/logind conflict), that failure itself is evidence worth recording, and it kills Path B's seat step too.
3. If A fails at the DRM step only (seat opens, DRM backend rejects the render node), run Path B (vkms).
4. If C, A, and B all fail, option C is dead and the choice is A versus D from the decision doc, exactly as Y6 concluded. The headless verdict then becomes proven by exhaustion, not by five runs of one config.
5. In every further attempt, set AQ_TRACE=1 and keep WAYLAND_DISPLAY pointed at a real socket or unset, so the log shows which backends were actually requested instead of failing on a nonexistent socket.

## Corrections to Y6's report (for the record)

- The claim "logind cannot open a seat for a second compositor" is proven, but the proof is attempt 3's `Could not take control of session: Device or resource busy` line, not the mere fact that attempt 3 crashed. Cite that line.
- The claim "Env vars do not select headless" should read "AQ_BACKENDS and WLR_BACKENDS do not select headless". AQ_DRM_DEVICES, AQ_NO_KMS_REQUIREMENT, AQ_TRACE, LIBSEAT_BACKEND, and SEATD_SOCK were never tried.
- The claim "the headless backend EXISTS but was never reached" should add: even if reached, it cannot supply the allocator alone (drmFD -1, Backend.cpp start() requires drmFD >= 0). Pure headless is structurally impossible in Aquamarine 0.16 as shipped; the question was never "can headless start" but "can headless plus a DRM fd source start".
- The attempt table should note that all 5 attempts set WAYLAND_DISPLAY to a nonexistent socket, so the Wayland backend failure in those logs is an artifact of the test setup, not a finding about nested Wayland.

## Evidence contract for this paper

- Re-read Y6 draft and Worker X decision doc in full before writing.
- Re-verified on the laptop (read-only, short SSH calls): 5 crash reports (120-121 lines each, identical backtraces), 5 attempt logs (2.8 KB each, no "plugin" string), 5 nested hyprland.log files (0 bytes each), config file (358 bytes, plugin line present, monitor HEADLESS-1), run-nested.sh (overwrites WAYLAND_DISPLAY and XDG_RUNTIME_DIR), seatd.log (seatd ran 107 seconds as root, then stopped), loginctl (live session 2, seat0, tty1, wayland, active), groups (user not in seat or video; video holds only ollama), /dev/dri (card1 NVIDIA root:video 660, card2 Intel root:video 660, renderD128 NVIDIA and renderD129 Intel world accessible), seatd -h (-u and -g flags), seatd-launch present at /usr/bin/seatd-launch, vkms.ko.zst present in kernel 7.2.15-1-omarchy tree and not loaded, cage and weston not installed, weston 15.0.1-3 available in extra repo.
- Upstream: Aquamarine Backend.cpp (fetched 2026-11-21) allocator loop at start(), Hyprland wiki env vars (AQ_DRM_DEVICES, AQ_NO_KMS_REQUIREMENT, AQ_TRACE), seatd man page (SEATD_SOCK, -u, -g), Omarchy WSL2 writeup (headless drmFD -1, GBM-only allocator).
- UNVERIFIED, stated as such: seatd/logind coexistence on one VT; Aquamarine DRM backend acceptance of a render-only node; Aquamarine on vkms plus GBM/EGL behavior there; weston headless backend dmabuf advertisement; which render node (NVIDIA vs Intel) the live session prefers (renderD128 is NVIDIA, renderD129 is Intel, mapping verified, preference not tested).
- No launch was performed, no file was modified on the laptop, the live session was not touched. One desktop crash notification already exists from Y6's attempts; this review added none.
