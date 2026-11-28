# Worker Y6: hyprglass nested probe (option C for 2.2.3) - FINAL

- Date: 2026-11-21, 18:17-19:00 +07
- Worker: Y6 (Muse subagent). Branch: todolist-push.
- Decision doc: docs/decision-2-2-3-hyprglass-test-20261121.md (Worker X). Owner chose C at 18:16.
- Status: FINAL. Council A/B/C + redteam debate complete, all corrections applied,
  Council A missed paths tested (attempts 6-8), Wayland-nested design fixed and its
  files created and verified on the laptop. Wayland-nested run NOT yet run.

## Verdict (one line)

HEADLESS-AS-RUN DEAD: 8 nested launches, 8 SIGABRT crashes, two signatures, one wall
(the live session holds DRM master on every KMS device, including the vkms card it
grabbed on hotplug). Wayland-nested is the only remaining option-C path; its design
is fixed and its files are created and verified, not yet run.

## Evidence

### Attempt table (all times +07, 2026-11-21)

| # | Time | Env / change | Result | Signature |
|---|------|--------------|--------|-----------|
| 1 | 18:20 | SSH, XDG_RUNTIME_DIR=/tmp/y6-nested/run, WAYLAND_DISPLAY=wayland-y6 (nonexistent), WLR_BACKENDS=headless | Crash, exit 134 | A: initServer / CBackend::create() |
| 2 | 18:21 | SSH, same + AQ_BACKENDS=headless | Crash, identical | A |
| 3 | 18:22 | Hyprland child via hyprctl dispatch Lua os.execute (real session), headless env | Crash, identical; tail adds logind.c:309 Device or resource busy | A |
| 4 | 18:22 | SSH, AQ_BACKENDS=headless, debug.enable_stdout_logs=true in config | Crash, identical. The stdout-logs flag never took effect: all 8 logs print enable_stdout_logs = 0. Attempt 4 duplicates attempt 1. | A |
| 5 | 18:24 | SSH, headless env, seatd started as root, default socket | Crash, identical + seatd EACCES (seatd.c:66 Permission denied). Socket mode and PID from the draft have no surviving record and are dropped. | A |
| 6 | 18:40 | SSH, seatd -u user, LIBSEAT_BACKEND=seatd, SEATD_SOCK=/run/seatd.sock, AQ_DRM_DEVICES=/dev/dri/renderD128, AQ_TRACE=1, WAYLAND_DISPLAY unset | Crash, exit 134, coredump 18:40:37 PID 235189. Seat OPENED (see below). DRM backend rejected the render node. | A |
| 7 | 18:42 | SSH, seatd -u user, vkms loaded (card0 created), AQ_DRM_DEVICES=/dev/dri/card2 | INVALID as a vkms test: my sort -V bug picked live card2 (Intel), not vkms card0. Still informative: backend came up, died later (see below). Crash, coredump 18:42:05 PID 236437. | B: enterLoop / initFB |
| 8 | 18:43 | SSH, seatd -u user, AQ_DRM_DEVICES=/dev/dri/card0 (correct vkms card), config without monitor line | Crash, exit 134, coredump 18:43:30 PID 238521. Backend, allocator and outputs all came up; died at modeset commit. | B: enterLoop / initFB |

Observable experiments, not launches: attempts 1, 2, 4 are one experiment (identical
conditions; AQ_BACKENDS does not exist in the binary, the stdout-logs flag never
applied, no launch artifact for 1, 2, 4). Attempt 3 is distinct (live child, logind
EBUSY line). Attempt 5 is distinct only by the seatd EACCES line. Attempt 6 is
distinct (seat actually opened). Attempts 7 and 8 are distinct (backend came up).
So: 8 launches, 5 observable experiments, 2 crash signatures, 1 wall.

### The wall, stage by stage (what each attempt proved)

Attempt 6 log (crash report 235189, per-instance log tail):
```
drm: Enumerated device /sys/devices/pci0000:00/0000:00:01.0/0000:01:00.0/drm/card1
libseat: Device /dev/dri/card1 supports kms
drm: Enumerated device /sys/devices/pci0000:00/0000:00:02.0/0000:02:00.0/drm/card2
libseat: Device /dev/dri/card2 supports kms
drm: Explicit device list /dev/dri/renderD128
ERR: drm: Explicit device /dev/dri/renderD128 not found
ERR: drm: Found no gpus to use, cannot continue
ERR: DRM Backend failed
ERR: Wayland backend cannot start: wl_display_connect failed
CRIT: Cannot open backend: no allocator available
```
Seatd log (seatd2.log): socket srwxrwx--- user:seat, client connected
(pid 235189, uid 1000), "Opened client 1 on seat0". Then 2x
"Could not make device fd drm master: Device or resource busy" (card1, card2)
and 2x "Could not revoke drm master: Invalid argument". The seat fix works.
The render-node half of Council A Path A is wrong in mechanism: the DRM backend
needs a KMS card, and a render node is not one, so the explicit device list
matched nothing. AQ_TRACE=1 is a real variable (TRACE lines observed).

Attempt 8 log (per-instance hyprland.log, 2842 lines, sig
11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795261409_796081127):
```
drm: Enumerated device /sys/devices/faux/vkms/drm/card0
drm: Explicit device list /dev/dri/card0
drm: Explicit device /dev/dri/card0 found
DRM Dumb: created a dumb allocator
Created a GBM allocator with drm fd 38
Created a GBM allocator with drm fd 45
GBM: Explicit scanout output, output has 33 explicit formats  (repeated)
atomic drm request: failed to commit: Permission denied, flags: ATOMIC_ALLOW_MODESET ATOMIC_TEST_ONLY  (20x)
ERR: atomic drm request: failed to commit: Permission denied, flags: ATOMIC_ALLOW_MODESET PAGE_FLIP_EVENT
```
Backtrace (both 236437 and 238521, identical frames): #7
Monitor::CMonitorResources::initFB, #8 CMonitorResources ctor, #9
CMonitor::resources(), #15 CEventLoopManager::enterLoop(). Signal 6 (ABRT).

So the progression is: seat (attempts 1-5 fail) -> seat opens (attempt 6, then
device selection fails) -> device found, backend + allocator + outputs up
(attempts 7-8) -> modeset commit Permission denied (not DRM master). The live
session holds DRM master on card1, card2, AND card0: seatd reports master-busy
for all three devices in attempts 7 and 8. The initFB/enterLoop signature is
PROGRESS past the initServer signature, not a second root cause. One wall,
two stages of manifestation.

### Crash rate finding (watchdog alert 18:44)

8 nested SIGABRT in 24 minutes (18:20-18:43), over the 5/hour threshold
(watchdog counted 7 at its 18:44 snapshot; the 8th landed 18:43:30). Each crash
writes a report to ~/.cache/hyprland/ and can produce a desktop crash
notification. STOP launching nested DRM attempts: the wall is proven, further
attempts without a DRM-master solution only repeat signature B and add noise.

### vkms contamination and leftover (attempt 7 side effect, must be recorded)

- `sudo modprobe vkms` created card0 (lowest free number, NOT card3) plus
  /dev/fb1 at 18:41. No render node appeared for vkms (only renderD128/129).
- The LIVE session grabbed card0 on hotplug: fuser shows PID 1515 holding
  /dev/dri/card0 open, confirmed by /proc/1515/fd. The live session also holds
  DRM master on card0 (seatd master-busy for all three cards in attempt 8).
- `modprobe -r vkms` FAILS: "Module vkms is in use" (refcount 2). The module,
  card0 and /dev/fb1 remain on the machine. Removal requires the live session
  to release card0; no Hyprland command releases a GPU, and restarting the
  live session is forbidden. Leave it loaded and record it; do NOT force rmmod.
- Live session impact checked 18:42: exactly ONE monitor (eDP-2, 1920x1200@144),
  no phantom vkms output, layout unchanged, PID 1515 alive since 15:17:25,
  hyprctl responsive, version 0.57.2. The grab is invisible to the owner.

### Plugin file verification (done before launching)

- Backup 1 (decision-doc first path, on the laptop):
  ~/.local/share/agent-computer-use/backups/full-1791544423/native/hyprglass.so,
  26,643,888 bytes, sha256
  2671d4ac41941ca62ae8100fc3b57bf3153bf6def893334f3a8ecbc1ea0145d5. IDENTICAL
  (same sha256) to the laptop vendor copy. Note: vendor/ does not exist in the
  repo checkout; the vendor path is the laptop path above.
- Backup 2: ~/.local/share/agent-computer-use/backups/sync-20261116-230254-783160-a9a24690/trees/native/hyprglass.so,
  30,622,520 bytes, sha256 ddfff1c2f2cebb66e10b85a739beae0c7c562ccf9d78e3250647c07f8f31fa8b.
  DIFFERENT build, not used, and never compat-checked against Hyprland 0.57.2.
  That is an open gap: identify the load-compatible .so by loading it, not by hash.
- Both are ELF 64-bit shared objects; nm -D shows __hyprland_api_get_client_hash
  and pluginAPIVersion. No version string is embedded. Plugin version
  (expected 1.1.1-cu.1) is only visible via `hyprctl hyprglass status` AFTER a
  successful load, so it is UNVERIFIED. Backup 1 is an Oct 9 build against a
  Nov 9 Hyprland; load compatibility with 0.57.2 is unverified.
- Installed tree has NO hyprglass .so in native/. Live Hyprland 0.57.2, commit
  11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947.
- Optics profile: native/hyprglass-local-optics.lua (repo), applied live via a
  Lua hook (scripts/setup.py _hook_body: dofile the profile when exactly one
  hyprglass of the right version is loaded). Global layers mask_mode is region
  (line 26); the per-layer call for namespace computer-use-indicator is contour
  (line 37). Blur 0.15, refraction 0.55. Readiness is indicator.liquid_available
  with ready=True semantics (see design section).

### Env vars: what is real, what is not (binary-checked)

- AQ_BACKENDS: absent from libaquamarine.so.0.16.0 (0 hits). WLR_BACKENDS: absent.
  Neither selects headless. Attempts 1, 2, 4 differ only in words.
- AQ_DRM_DEVICES: present in the binary, honored by the DRM backend (attempt 6
  and 8 log lines prove it). A render node is not a usable explicit device.
- AQ_NO_KMS_REQUIREMENT: literal count 0 in the shipped binary (only one
  truncated AQ_NO_KMS_REQUIR fragment). Dropped from every prescription.
- AQ_TRACE=1: real (TRACE lines in attempt-6 crash report).
- LIBSEAT_BACKEND=seatd + SEATD_SOCK=/run/seatd.sock: work (seat opened, attempts 6-8).
- seatd-launch: /usr/bin/seatd-launch is -rwxr-xr-x, NO setuid bit. Its man page
  requires root or SUID; under sudo the nested process runs as root. It cannot
  do what Council A Path A asked unprivileged. Path A rewritten around
  `seatd -u user` (flag verified in seatd -h), tested in attempts 6-8, works.

## Council + redteam debate (resolved)

Papers: improvements/worker-y6-council-a-feasibility.md (57755ae),
improvements/worker-y6-council-b-evidence.md (3dff065),
improvements/worker-y6-council-c-reproduction.md (f3ba3a1),
improvements/worker-y6-redteam.md (66e5e48). Draft report: db1f0de.

### Council A: PARTIAL, then WEAKENED by testing

- Missed paths named: seatd-launch, AQ_DRM_DEVICES + AQ_NO_KMS_REQUIREMENT, vkms.
- Path A (seatd-launch + render node): TESTED in corrected form. seatd -u works
  (seat opens); render node fails (not a KMS device); AQ_NO_KMS dropped (not in
  binary); seatd-launch cannot run unprivileged (no setuid). The path as written
  is dead; its seat half survives and is now the standard seat method.
- Path B (vkms + seatd-launch): TESTED. vkms loads, card0 appears, but the live
  session grabs card0 on hotplug and holds master on it, so the nested client
  still cannot modeset. Risk label corrected LOW to MODERATE (stacked experiment:
  kernel module + root + unproven seat step + unverified vkms GL behavior).
- Path C (Wayland-nested first): STANDS, highest probability, only path whose
  allocator source is known to exist (parent supplies DRM fd via dmabuf).
- Path D (fresh TTY): SURVIVES as the only remaining untested headless path. A
  new logind session on another VT would hold its own DRM master. NOT attempted:
  needs a VT switch (blanks the live screen) plus a TTY login, high live-session
  risk, dominated by option A in a handover window. Do not try now.
- "Pure headless is structurally impossible (drmFD -1)": WEAKENED. Cited to
  fetched source the redteam could not re-verify. The observed allocator failure
  is real but was downstream of the seat failure in attempts 1-5, and attempts
  7-8 prove the allocator CAN be created (GBM allocators on fd 38 and 45).
  The true wall is DRM master, not the allocator.

### Council B: SOUND with corrections, survives

Every correction re-checked and holds, with three gaps the redteam found and this
report adopts: B missed the XDG launch bug in the Wayland design, the AQ_NO_KMS
gap, and the seatd-launch SUID gap. B's collapse of the attempts (attempt 4
duplicates attempt 1; three observable experiments in the first five) is the
accurate count.

### Council C: APPROVE-WITH-CHANGES, all 7 applied

1. Parent connection env fixed: WAYLAND_DISPLAY=/run/user/1000/wayland-1
   (absolute), XDG_RUNTIME_DIR=/tmp/y6-nested/run for the nest only, plus
   --socket wayland-y6 to pin the nest socket. Pre-launch check test -S on the
   live socket; post-launch check that the nested log shows the Wayland backend
   started. Socket-naming evidence: the nest socket defaults to wayland-1 under
   its own XDG_RUNTIME_DIR (observed /tmp/y6-nested/run/wayland-1 after
   attempt 8, when WAYLAND_DISPLAY was unset), and `Hyprland --socket NAME`
   sets the socket name explicitly.
2. Missing files created (see design section below) and stale sig dirs cleaned.
3. Animated backdrop named (ffmpeg testsrc2 video looped by mpv fullscreen)
   plus positive control (two frames must differ before the pill starts) plus
   the E2 two-arm comparison (static arm, then animated arm).
4. Measurement named exactly: grim frame diff per arm (region, tool, threshold
   in the launcher), plus a raw nested-log pattern count as a secondary arm
   with its UNVERIFIED status stated. The callback counter source does not
   exist in scripts/indicator.py; the frame arm is primary.
5. `source=optics.lua` replaced with the dofile hook mechanism (setup.py
   _hook_body form), adapted only where the live re-apply command would be
   wrong inside the nest (documented in the hook file). Reload branch dropped;
   restart is the safe branch.
6. Check-then-launch race closed: the launcher holds zen_dom.lock (flock) for
   the whole run, which blocks any runner from starting (all live runners
   launch under that flock per run_agyq2.py preflight). Exact flock method is
   the lock file itself, not a bare check. Duration estimate ~4 minutes inside
   a 30 minute window.
7. Teardown added (trap on EXIT: kill pill + nest, remove runtime dir,
   re-verify live PID 1515, hyprctl, live plugin list) and GO/NO-GO sharpened
   (liquid_available(ready=True) semantics exactly; version-mismatch branch
   records the observed version and returns to council; shader pending gets one
   30s extension, then NO-GO; verdict asymmetry written in: a nest negative is
   only "not reproduced in the nest", never an exoneration of the live backdrop).

### Redteam: verdicts adopted

- Broad verdict HEADLESS DOES NOT WORK: KILL. Adopted as HEADLESS-AS-RUN DEAD,
  HEADLESS UNTESTED, now narrowed by attempts 6-8 to: headless dead at the DRM
  master wall on every device tried (card1, card2, renderD128, vkms card0);
  only a fresh TTY session remains untested.
- Narrow claims survive: the attempted config cannot start; the seat failure was
  proximate for attempts 1-5 (attempt 6 proves the seat can open and the run
  still dies, at device selection, then at master).
- "Aquamarine needs a seat even for headless" as proven: KILL. Downgraded to
  inference from log order; no attempt ever reached a headless backend.
- "Attempt 4 is a distinct experiment": KILL. It duplicates attempt 1.
- "Attempt 5 has the most complete log tail": KILL. Attempt 3 has the extra
  logind.c:309 line; all five contain the tail.
- "All 5 attempts caused the ~18:23 notification": WEAKENED. Only the first
  four dumps predate it; the fifth is 18:24:52. Attempts 6-8 (18:40:37,
  18:42:05, 18:43:30) may have produced notifications; the owner was away and
  it was not observed, so it is recorded as unknown, not claimed.
- "Live session untouched": WEAKENED. Outcome true (same PID 1515 survived).
  Reworded below to survived undamaged, with the touches disclosed.
- Seatd socket mode + PID 219625: KILL as stated. Dropped; only the EACCES line kept.
- Mask mode contour: WEAKENED. Region globally, contour for the indicator layer.
- Wayland-nested design as written: KILL. Fixed; files created (below).
- Plugin choice backup 1: WEAKENED. Oct 9 build vs Nov 9 Hyprland; load
  compatibility unverified; backup 2 dismissed without a compat check.
- Council A Path A: WEAKENED (see above). Path B risk LOW: WEAKENED to MODERATE.
- Council B SOUND: SURVIVES, with the three gaps noted above.

### All 16 contradiction resolutions (redteam, adopted in full)

1. Broad verdict: A and B right, Y6 headline wrong. Correct: HEADLESS-AS-RUN DEAD.
2. Attempt count: five launches, three observable experiments in the first five
   (baseline, live child, seatd-EACCES); B most precise. With 6-8: five
   observable experiments total.
3. Most complete tail: B right, attempt 3.
4. Seat even for headless: B right, inference not proven. A drmFD claim not
   re-verified; attempts 7-8 now prove the allocator can be created.
5. Logind exclusivity: B right, strongly supported, not proven (no logind-side record).
6. Seatd socket and PID: B right, drop both, keep the EACCES line.
7. Notification attribution: B right, first four dumps predate it.
8. Mask mode: B right, region globally, contour for the indicator layer.
9. Design runnability: B right, A wrong to say verbatim. Fixed before the files
   were created (attack 1: absolute parent display path).
10. Wayland backend in attempts 1-5: A and B right. Every wl_display_connect
    failure is an artifact of pointing at nonexistent wayland-y6, not evidence
    about nested Wayland.
11. Env vars: both partly right. AQ_BACKENDS and WLR_BACKENDS absent (Y6 right);
    AQ_DRM_DEVICES present and AQ_TRACE real; AQ_NO_KMS_REQUIREMENT absent
    (A overstates one of its own vars).
12. seatd-launch: A right that raw seatd with default socket ownership was the
    wrong tool and -u exists; A wrong that seatd-launch is a one-command
    unprivileged fix (no setuid; under sudo the nest runs as root). Fix is
    seatd -u user, tested in attempts 6-8.
13. vkms risk: A understates it. LOW for GPU and VT, MODERATE as a stacked
    experiment. Ranking third was right; the label was wrong. Now tested:
    the live session grabs the vkms card, which A did not foresee.
14. Live safety: outcome confirmed, wording narrowed to survived undamaged.
15. Instance signature pick: B right in principle; one entry existed in practice.
    Fixed: launcher pins the live signature by value and the nest signature
    with ls -t (newest first) plus an existence check.
16. Handover and timing: B right on both. Handover is time-bound; the launcher
    requires Y6_HANDOVER_CONFIRMED=1 at run time. The 8s shader figure is
    borrowed from live, marked as such; the launcher allows 30s + 30s.

## Safety record (reworded: survived undamaged)

Live session outcome: PID 1515 started 15:17:25, still the only Hyprland
process; hyprctl version responds 0.57.2; plugin list shows only hyprbars 1.0;
exactly one monitor (eDP-2); no ~/.config/hypr/ file touched 18:17-18:50;
seatd dead after each attempt; live socket intact. The touches, disclosed:

- Attempt 3 executed code inside the live compositor process (hyprctl dispatch
  with Lua os.execute runs the chunk in-process in live Hyprland).
- seatd ran as root four times: attempt 5 for 107s, attempts 6-8 for ~4-5s each,
  creating a VT-bound seat seat0 while logind session 2 holds the same VT.
- 8 SIGABRT coredumps of /usr/bin/Hyprland (18:20-18:43) plus a desktop crash
  notification the owner saw at ~18:23 (first four dumps predate it).
- vkms module loaded and NOT removed (card0 + /dev/fb1 remain); the live
  session holds card0 open and holds DRM master on it.

## Incident-reproduction design (Wayland-nested, FIXED, files created, NOT run)

Goal: reproduce the 20/11 flicker (pill flickering ~10x per second while idle,
18:53-19:02, no input, no screenshots; hypothesis H-E, animated backdrop, an
UNVERIFIED CANDIDATE from docs/redteam-council-20261121/worker4-overlay-flicker-redteam.md;
E2 is a static-versus-animated comparison) inside the nest, or prove the
backdrop is not the cause.

### Files created on the laptop (all verified 18:50-18:55)

- /tmp/y6-nested/run-nested-wayland.sh (11,648 bytes, bash -n OK): the runner.
  Holds zen_dom.lock for the whole run; requires Y6_HANDOVER_CONFIRMED=1;
  checks live socket, all files, flock; launches the nest with
  WAYLAND_DISPLAY=/run/user/1000/wayland-1, XDG_RUNTIME_DIR=/tmp/y6-nested/run,
  --socket wayland-y6, timeout 300; verifies Wayland backend started, nested
  socket exists, hyprglass in plugin list, liquid gate (ready=True, 60s);
  positive control (backdrop must move); starts the pill; reads pill geometry
  from nested `hyprctl -j layers`; runs arm A then arm B; prints verdict lines;
  teardown on EXIT (kill pill + nest, remove runtime dir, re-verify live).
- /tmp/y6-nested/conf/hyprland-wayland.lua (935 bytes): hl.monitor WAYLAND-1
  960x540@60, hl.plugin.load backup 1, hl.exec_cmd mpv fullscreen loop +
  foot, dofile nested-visuals-hook.lua in a managed block.
- /tmp/y6-nested/conf/nested-visuals-hook.lua (967 bytes): setup.py _hook_body
  form, profile /tmp/y6-nested/conf/optics.lua, version 1.1.1-cu.1; else branch
  prints a marker instead of running the live visuals.py command (documented).
- /tmp/y6-nested/conf/optics.lua (2,141 bytes): copy of
  native/hyprglass-local-optics.lua from the laptop repo.
- /tmp/y6-nested/run-nested-pill.py (1,407 bytes, py_compile OK): minimal idle
  pill. Imports scripts/indicator.py; STATE=/tmp/y6-nested/cache/agent-computer-use
  (separate from live, so socket and token cannot collide); nested env
  (XDG_RUNTIME_DIR=/tmp/y6-nested/run, WAYLAND_DISPLAY=wayland-y6,
  HYPRLAND_INSTANCE_SIGNATURE from Y6_NEST_SIG); calls indicator.Native (which
  probes liquid and waits for the profile) then native.command("show"); serves
  commands in a thread. Pill namespace is computer-use-indicator (native
  indicator.c:502 gtk_layer_set_namespace), so the optics profile contour call
  applies to it.
- /tmp/y6-nested/backdrop.mp4 (1,991,554 bytes, 10.0s): ffmpeg testsrc2
  960x540@30, deterministic moving pattern. Played with mpv --loop=inf
  --no-audio --fullscreen. PIL and ImageMagick `compare` both available on the
  laptop; the launcher uses grim + cmp (deterministic PNG bytes).
- Stale signature dirs under /tmp/y6-nested/run/hypr/ cleaned (5 dirs removed).

### Measurement (exact, per Council C change 4)

- Positive control: 2 full-output grim frames 1s apart, no pill, mpv running.
  Must differ (cmp), or the animation source is broken and the run stops.
- Arm A (STATIC backdrop, pill idle, 32 frames 1s apart, pill region only via
  grim -g): decisive. Any pill-region change = flicker = REPRODUCED. 32/32
  identical = not reproduced in this arm.
- Arm B (ANIMATED backdrop, pill idle, 32 frames): per-pair readout
  (pill_diff?, backdrop_diff?) on 31 consecutive pairs. Pill differs while the
  backdrop sample is identical = flicker evidence. Both differing is expected
  motion. Backdrop sample region is a 200x200 corner away from the pill,
  chosen after the pill geometry is known.
- Callback arm (secondary, UNVERIFIED as a counter): count lines matching
  repaint|paint|commit|frame in the nested per-instance log segment for each
  arm. Recorded as raw counts only; the frame arm is primary. No paint or
  callback counter exists in scripts/indicator.py.
- GO: nested starts, Wayland backend started in the log, plugin loads, status
  version 1.1.1-cu.1 with versionCheck match, liquid_available(ready=True)
  true within 60s (30s + one 30s extension for nested shader compile).
- NO-GO: nested crashes, plugin refuses to load, version mismatch (record the
  observed version, return to council, do NOT substitute backup 2), shaders
  error/failed or still pending after the extension, pill surface absent from
  nested layers, positive control fails.
- Asymmetry clause (Council C): a POSITIVE result (pill region changes with a
  static backdrop, or pill-only changes in the animated arm) is decisive, it
  reproduces the incident. A NEGATIVE result (32/32 identical, 0 callbacks) is
  only "not reproduced in the nest". It does NOT exonerate the live backdrop,
  because the flicker may depend on live timing the nest does not replicate
  (nest renders 960x540@60 through the Wayland backend and the parent
  compositor presentation timing, possibly with software GL).

### What the design does NOT do

- It does not run yet. It needs a runner-quiet window (flock held for the whole
  run) plus a handover re-confirmed at run time. Do NOT run it while any Zen
  runner is active: the nested window is sized by the live tiler (it will tile
  and resize Zen, not float at 960x540), which pollutes hasFocus and visibility
  observations of a concurrent runner even if nobody clicks it.
- It does not test the headless route further. Headless is dead at the DRM
  master wall; no further nested DRM launch is justified.

## Recommended next step

Run /tmp/y6-nested/run-nested-wayland.sh in the next runner-quiet window, with
handover re-confirmed at run time (Y6_HANDOVER_CONFIRMED=1). If Wayland-nested
fails (parent-connection failure, plugin refusal, version mismatch), option C
is dead by exhaustion and the choice is A (handover + live load, crash risk)
versus D (skip repro, monitor via E1 logging). If it works, the run itself
produces the reproduction verdict (REPRODUCED vs NOT reproduced in the nest)
from its printed SUMMARY lines. Do NOT launch more nested DRM attempts.

## Evidence contract

- Commands that produced the load-bearing evidence (all on the laptop via
  ssh-laptop.sh): `coredumpctl --no-pager list` (8 Hyprland SIGABRT 18:20:16,
  18:22:00, 18:22:35, 18:23:03, 18:24:52, 18:40:37, 18:42:05, 18:43:30);
  `grep -a` over ~/.cache/hyprland/hyprlandCrashReport{235189,236437,238521}.txt
  and the per-instance logs under /tmp/y6-nested/run/hypr/*/hyprland.log
  (seat lines, DRM lines, allocator lines, atomic-commit lines, backtrace
  frames); seatd logs seatd2/3/4.log (client connected, master-busy errors);
  `fuser -v /dev/dri/card0` + /proc/1515/fd (live holds card0);
  `lsmod | grep vkms` + `modprobe -r vkms` (FATAL: in use, refcount 2);
  `hyprctl -j monitors` live (1 monitor, eDP-2); `ls -l /run/seatd.sock`
  (srwxrwx--- user:seat); `strings` + `grep -a -c` on
  /usr/lib/libaquamarine.so.0.16.0 (AQ_DRM_DEVICES present, AQ_BACKENDS 0,
  AQ_NO_KMS_REQUIREMENT literal 0, one AQ_NO_KMS_REQUIR fragment);
  `ls -l /usr/bin/seatd-launch` (-rwxr-xr-x, no setuid); `ffmpeg` + `ffprobe`
  (backdrop.mp4, 10.0s); `bash -n` + `python3 -m py_compile` on the design files.
- Commits on todolist-push: draft db1f0de; Council A 57755ae; Council B 3dff065;
  Council C f3ba3a1; redteam 66e5e48; final report 482e4ba.
- No em dash or en dash in this report. No personal info in this report.
  No test was self-graded: attempts 6-8 were run by Y6 as the prober (the task
  is a probe, not a test of Y6 code); the design files were verified by syntax
  checks and file inspection only, not by a run; the Wayland run is still owed.

## Timed run log

- 18:17-18:19: read decision doc + pending decisions; verified .so files (ls + file + sha256); Hyprland 0.57.2.
- 18:19-18:20: read optics lua, setup.py hook, liquid_available; attempt 1 -> crash 18:20:16.
- 18:21: attempt 2 -> crash 18:22:00.
- 18:22: attempt 3 (Hyprland child) -> crash 18:22:35; attempt 4 -> crash 18:23:03.
- 18:23: desktop crash notification; verified live PID 1515 alive + hyprctl responsive.
- 18:24: seatd installed but not running; attempt 5 -> crash 18:24:52.
- 18:26: headless backend symbols confirmed in libaquamarine, never reached.
- 18:28: killed seatd, socket gone. Draft report written.
- 18:34-18:45: Council A, B, C + redteam spawned and debated; draft committed db1f0de.
- 18:40:33-18:40:49: attempt 6 (seatd -u + renderD128) -> crash 18:40:37, seat opened, render node rejected.
- 18:41:59-18:42:18: vkms modprobe (card0 created) + attempt 7 (wrong card picked) -> crash 18:42:05, signature B.
- 18:42:44-18:42:45: cleanup investigation: live PID 1515 holds card0, rmmod fails, live has 1 monitor.
- 18:43:26-18:43:42: attempt 8 (vkms card0) -> crash 18:43:30, allocator up, modeset denied.
- 18:44: watchdog alert (7 SIGABRT/hour, threshold 5). No further DRM launches.
- 18:45-18:50: crash-report forensics (236437/238521 backtraces, identical signature B).
- 18:50-18:55: socket-naming evidence; design files written, transferred, verified
  (bash -n OK, py_compile OK, backdrop.mp4 10.0s, optics.lua copied, stale sig dirs cleaned).
- 18:55-19:00: final report written (this file).
