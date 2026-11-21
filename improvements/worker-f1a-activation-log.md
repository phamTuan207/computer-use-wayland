# Worker F1a log: F1 live activation + council-3 5-step positive proof
# Owner order: F1 phase of the F1+F2 end-to-end proof. F3b healed the slot
# (Zen PID 496121, restart #3 23:44:11, probes OK 23:51:12) and signed off.
# All times wall-clock Asia/Ho_Chi_Minh + elapsed from task start 23:51.
# Rule: log EVERY event as it happens, never batched. No em/en dashes.

## 23:51 task start
- Spawned as F1a. Brief: run python3 scripts/activate-session-backend.py
  from the installed tree, then the council-3 5-step positive proof.
- Read improvements/worker-f1-guardian-fix-log.md in full (F1 root cause
  4 layers, drift repair, round 1 + round 2 fixes, wrapper, council-3
  5-step proof, preconditions 1-8).
- Read F3b final report (commit 7cde3d2, log improvements/worker-f3b-restart-log.md):
  slot HEALED by restart #3 (PID 496121), probe_r3 PASS, final probe
  23:51:12 PROBE1 OK 3d32d968 + PROBE2 OK b79465cd, 14 real tabs, 0 fixtures,
  Marionette 17 = 14 real + 3 pre-existing blanks. F1 SIGN-OFF given.
  Trigger: Arm E combination (sac + multiple DELETE /window + DELETE with
  sac current); A/B/C/D alone PASS. Rule: never Marionette-close tabs in
  bulk, never Marionette-close about:blank; BiDi close or UI right-click
  Close Tab only. Owner was active on ws2 at 23:43:43 (clone2 confirming
  todo): do NOT yank his screen; observe first, wait if he is active.
- VM repo todolist-push HEAD 7cde3d2 (F3b handover). 2 untracked files
  (multi-agent-deliberation-idea, muse-coordinate-accuracy) are not mine.

## 23:52 pre-flight (council-2 precondition 2, same-minute)
- Pinned values (installed native/visuals.json): abi
  11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_aq_0.16_hu_0.14_hg_0.6_hc_0.1_hlg_0.6;
  glass hyprglass-199153aea84a833d86f3eee21708e186c5a722c52259397735898b52f86df07f.so;
  guard cursor-guard-06712eafb74c15297f7c63cdd2ebdb752c1026e988660bb0c319ee1bb7f2c800.so;
  profile_sha256 9a15163491b543dde09c8388a8faf01f9b491c831647320ce2949d5737d8993c.
- Plugin list: hyprbars 1.0 ONLY. configerrors: empty. cu-cursor status:
  "unknown request" (guard not loaded, expected). Socket dir
  /run/user/1000/agent-computer-use/: does not exist (no session).
- Glass sha 199153ae... = filename + manifest. Guard sha 06712eaf... =
  filename + manifest. ldd: 0 not found on both.
- Live abiHash 11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_aq_0.16_hu_0.14_hg_0.6_hc_0.1_hlg_0.6
  = manifest abi exactly. Zen PID 496121 (stable, matches F3b handover).
- Wrapper --help: --manifest (default native/visuals.json), --glass-library,
  --guard-library, --abi, --profile-sha256. Holds owner_lock across glass +
  guard. Pre-flight ALL PASS. Next: fresh observe (owner-activity check)
  before any driving.

## 23:53 fresh observe (owner-activity check)
- Observe 23:53:00 id 9aec1ea20a69, capture 21.7ms, region [2464,902,1920,1200],
  monitor eDP-2, image /home/james/.cache/agent-computer-use/9aec1ea20a69.jpg,
  indicator inactive (no session). Viewed the screenshot.
- Screen: Zen on ws1, full screen, sidebar visible (zen basics: PCCV CF26,
  Free Claude Code Admin, Welcome!, 2x New Tab, 2x Just a moment..., Biome
  Finder, Gamerule keepInventory, ModelArk-Coding-Plan). Main area is a
  blurred wallpaper-like background; no pill. Cursor at ~(1437,598) image
  coords, static. No typing, no menu, no visible activity. Owner NOT
  visibly active. Proceed with the activation (plugin load drives nothing
  on screen; the proof click comes later, after another fresh observe).
- NOTE: top-right notification "Process crashed: omasnap, Click to
  diagnose with AI" (2m old, ~23:51). omasnap is Omarchy's screenshot
  tool, not Hyprland, not used by my observe (grim direct) or by F3b.
  Possibly the owner pressed the screenshot key on ws2. Not a blocker
  for the activation; noted here, flag to the parent in the final report.

## 23:53-23:54 activation attempt 1: FAILED at the guard step (glass loaded, shaders pending)
- Launched detached (setsid nohup, stdout /tmp/f1a-activation.out,
  stderr /tmp/f1a-activation.err): python3 scripts/activate-session-backend.py
  --manifest /home/james/.local/share/agent-computer-use/native/visuals.json,
  cwd the installed tree. Checked after ~5s: stdout EMPTY, stderr:
  "activate-session-backend: config reload did not reach an accepted ready
  state: accepted glass status is not ready". Wrapper process gone (exit 1).
- Diagnosis (state re-query, no retry yet): plugin list = hyprbars +
  hyprglass 1.1.1-cu.1 (GLASS LOADED). hyprctl hyprglass status:
  active, version check match, shaders: PENDING, windows off, layers on,
  subsurfaces off, protocol active. cu-cursor status: "unknown request"
  (guard NOT loaded). Socket dir absent. configerrors empty. Hyprland
  PID 1515 alive, Zen PID 496121 alive.
- Root of the failure: the error comes from the guard activation step
  (activate-cursor-guard.py refuses unless glass is ready), not from the
  wrapper's verify. The glass is loaded but its shaders are still warming
  up (council-2 F9: shader warm-up can exceed the 8s wait; a first guard
  refusal may mean slow shaders only). This is a HALF-LOADED state:
  glass loaded, guard not loaded.
- Half-state recovery (council-2 precondition 5, agreed in advance):
  NEVER re-run activate-glass after a partial success; guard-only retry;
  longer wait for slow shaders; re-query the plugin list before any
  retry; never blind retry a load. Next: poll hyprglass status until
  shaders leave "pending", then run the GUARD activation only.

## 23:54-23:55 diagnosis: shaders need a trigger, not more time
- 23:54:37 poll (~60s after load): shaders STILL pending. 23:55:25 poll
  (~2 min after load): STILL pending. Not a time-based warm-up.
- Correction to my earlier note: the wrapper error came from
  glass_activate's wait_for_profile (activate-glass.py:66, 8s timeout),
  NOT from the guard step. The guard was never attempted. Half-state
  is the same: glass loaded, guard not loaded, shaders pending.
- Mechanism (read from source): indicator.py:70 "The first overlay
  triggers shader compilation; keep it alive while polling."
  Native.__init__ spawns the indicator, replies 'ready', then if liquid
  calls wait_for_profile(timeout=LIQUID_READY_TIMEOUT=30s). _valid_liquid
  ready=False accepts 'pending'; ready=True does not.
- Guard activation (activate-cursor-guard.py:40) uses
  liquid_available(env) with ready=False, so it ACCEPTS pending shaders.
- Session R3 gate (cursor_session.py:172-175) checks ready=False first
  (glass active?) then ready=True (shaders ready?), failing with
  "hyprglass shaders are still warming up... retry the session in a few
  seconds" while pending. So a session CANNOT be the trigger; the gate
  blocks it. The designed trigger is the login loader's
  indicator_shader_warmup (visuals.py:310-317): create indicator.Native,
  keep it alive, close it. That is the recovery to run now (a /tmp
  script replicating those exact lines, glass already loaded, loads
  nothing new). Then guard-only activation.

## 23:56 shader warm-up: WORKED, shaders ready
- Launched /tmp/f1a-warmup.py detached (scp from VM). stdout:
  "shader warm-up done: overlay up, process alive" + "overlay closed".
  stderr: indicator events redraw ready, buffer presented, closed,
  0 present failures (one benign Gdk Vulkan warning, fallback used).
- hyprglass status right after: shaders: READY (was pending for 2+ min
  without the overlay). The designed trigger is confirmed live: the
  first overlay triggers shader compilation. Glass state now: active,
  version check match, shaders ready, layers on, protocol active.
- Next: guard-only activation (never re-run activate-glass; glass is
  loaded and ready). Command: python3 scripts/activate-cursor-guard.py
  <guard 06712eaf .so> --abi <manifest abi>, installed tree, detached,
  stdout/stderr to files.

## 23:57 guard activation: SUCCESS, backend verified
- Guard out: "native cursor backend ready", err empty, process done.
- Verify: plugins hyprbars 1.0 + hyprglass 1.1.1-cu.1 +
  computer-use-cursor 1.0.0. cu-cursor status JSON:
  {"active":false,"ok":true,"schema":1,"token":""} (no session yet,
  expected). Socket dir exists with cursor-guard.sock. Shaders ready.
  BACKEND IS UP. The F1 fix is live on the compositor.
- Session mechanics (read from source): supervise spawns the guardian
  (waits 15s for 'ready'), then the driver as cursor_session.py driver
  <gate> <argv>, which execs argv after 'go'. So `computer-use session
  -- sleep N` keeps the session (guardian + pill) up N seconds. STATE =
  ~/.cache/agent-computer-use, SNAPSHOT = STATE/session.json (token).
  Token values are NEVER written in this log (R11 redaction).
- Proof plan (council-3, 3 sessions): S1 sleep 25, observe pill during
  it, prove pill is the session pill (indicator pid + state-dir token
  match, compared programmatically, values never printed), let it stop,
  observe pill gone. S2 sleep 15, pill returns. S3 the click session
  (fresh observe first to re-check the active tab; skip if whiteboard
  or unsaved state; click center of the active tab only; verify via
  cursorpos + fresh observe). Stdout and stderr recorded separately
  for the whole run.
