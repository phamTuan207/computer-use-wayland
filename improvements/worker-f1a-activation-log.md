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
  todo): do NOT yank the user's screen; observe first, wait if the user is active.
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
  monitor eDP-2, image ~/.cache/agent-computer-use/9aec1ea20a69.jpg,
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
  --manifest ~/.local/share/agent-computer-use/native/visuals.json,
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

## 23:58 session 1: STARTED, pill up, stopped CLEANLY
- Launched 23:58:30 (sleep 25, detached). Indicator up at 23:58:32:
  redraw ready, buffer presented, hidden:0. Ended 23:58:57 (elapsed
  25076ms): final redraw closed, hidden:1. After: no session procs,
  no indicator procs, no session.json, cu-cursor back to
  {"active":false,"ok":true,"schema":1,"token":""}. CLEAN STOP.
- Observe ea455ca57d89 during S1 (23:58:35-40) shows workspace 2
  (clone1 Idle + clone2 Connected chats), NO pill. Two facts: the
  screen had switched ws1 to ws2 (clone2-watch run 23:56:56, by
  command; cursor unmoved at (1437,598), same as 23:53), AND the
  observe HIDES the pill during capture by design.
- PROOF of the hide: session1.err has exactly 1 hide_commands:1 and
  1 show_commands:1 (25 windows with 0). cu.py:942-943 and 979-980
  wrap captures in indicator.capture_clean (hide, capture, show).
  F2's after-captures show the pill because act-now holds its OWN
  overlay, not the session guardian's. Consequence: a computer-use
  observe can NEVER show the session pill; the pill proof needs a
  RAW grim (bypasses capture_clean). Lesson recorded: use grim for
  pill visuals, observe for everything else.
- The ws2 screenshot also shows the owner is NOT visibly active:
  static chats, cursor unmoved, messages timestamped 22:28 (old).
  The clone chats are context only, not my task.

## 00:01-00:04 sessions 2/2b/2c: SSH latency vs short sessions
- S2 (sleep 30, launched 00:01:37) ended before my grim landed: SSH
  round trips take ~30s (connect + broken pipe), comparable to the
  session windows. S2b (sleep 45, launched 00:02:28) also ended
  before the grim. Lesson: use LONG sessions (120s) for proof
  windows; short sleeps race the SSH latency.
- S2c (sleep 120, launched 00:03:18) gave a comfortable window.
- NOTE on tokens: one cu-cursor status output printed a full token
  value to my tool output (00:04:01 check). That value is NOT
  recorded anywhere in this log, the repo, or my report. All token
  checks below print booleans only (R11).

## 00:04 pill VISIBLE in raw grim (session 2c) + token proof
- Raw grim 00:04:01 (/tmp/f1a-grim-2c.png, 1,869,950 B), ws1/Zen:
  pill at top center, "Computer use active" + green dot + "Esc".
  THE SESSION PILL, VISIBLE. Screen back on ws1 (watch run returned).
- Token proof (tokcheck, booleans only, during S2c): snapshot token
  32hex True; cu-cursor active True, ok True; cursor token matches
  snapshot True; indicator endpoint socket exists True.
- Cursor moved (1437,598) to (985,598) between 23:58 and 00:04,
  same y, cause unidentified; static since 00:04 (same spot in the
  00:05:30 observe). No typing, no window change. Re-check owner
  activity before the click; if active, wait.

## 00:05 pill GONE after session 2c stops
- S2c ended ~00:05:18. Fresh observe 753ac7a9c974 (~00:05:30), ws1/Zen:
  NO pill at top center. Pill gone after stop, confirmed visually.
  No session procs, no snapshot. The omasnap crash notification
  (15m) is still on screen; cause known per MEMORY (OA ran
  `omasnap --help` via SSH without DISPLAY, Qt xcb fail, not a
  system fault; OA told to stop running Qt GUI commands via SSH).

## 00:06-00:07 indicator PID (session 2d)
- S2d (sleep 60, launched ~00:06:25) for the pid. pgrep for
  "computer-use-indicator" finds NOTHING: the binary is the installed
  native/indicator (fallback path), not the PATH name. PID 513273,
  ~/.local/share/agent-computer-use/native/indicator,
  alive during S2d; cu-cursor active True, token present True.
  (The Omarchy input-method indicator.py PID 165692 is a different
  process; ignore it.) Pill proof is now complete: plugin list +
  cu-cursor JSON active + token match + endpoint + visible pill +
  pid 513273 + pill gone after stop + pill returns on restart.
- Next: session 3, the click. Wait for S2d to end (~00:07:25),
  confirm no stray session/indicator, fresh observe + activewindow
  title to re-check the active tab, then the click session.

## 00:08 session 3 attempt 1: FAILED, act CLI takes file paths (not the session)
- Fresh observe f6edf8b1c426 (region [2464,902,1920,1200]): Zen ws1,
  active tab is the New Tab wallpaper (NOT whiteboard, no unsaved
  state), cursor static at (985,598) since 00:04, owner not active.
  Click point: center of the content area, image (1105,645), global
  (3569,1547). S2d had ended cleanly (no session.json, no indicator,
  cu-cursor inactive). Window title is just "Zen Browser".
- Launched 00:08:30: computer-use session -- computer-use act
  --observation f6edf8b1c426 --actions '[{"type":"click",...}]'.
  Result: {"ok": false, "error": "[Errno 2] No such file or directory:
  '[{\"type\":\"click\",\"x\":1105,\"y\":645}]'"}. The SESSION started
  fine (indicator up 00:08:30, redraw ready, buffer presented, closed
  141ms, clean stop, no session procs after). The failure is the act
  CLI usage, NOT the session/guardian.
- Root cause (read from source): cu.py:2329 --actions is "JSON path
  or - for stdin"; line 2489 read_json_file(args.actions). --observation
  is also read via read_json_file (line 2506). BOTH need FILE PATHS,
  not inline JSON or bare ids. F1's negative test passed inline JSON
  + a bare id too, but the guardian died first, so the act parsing
  was never exercised; the masked misuse is recorded here, not blamed.
- cursorpos after attempt 1: (3440,1502) vs pre-session (3449,1500):
  9px shift, NO click happened (act errored before any action). The
  shift is the cursor theme/hotspot change on session start, not a
  click landing.
- Fix: write /tmp/f1a-click.json with the action, pass
  --actions /tmp/f1a-click.json --observation
  ~/.cache/agent-computer-use/f6edf8b1c426.json. The screen
  is unchanged since f6edf8b1c426, so the observation stays valid.
  require_observation only constrains after a transient refusal
  (no marker here), so the pre-session observe is accepted.

## 00:09 session 3b: CLICK SUCCEEDED, 0px error
- Launched 00:09:47 with the corrected file paths. Result:
  {"ok":true,"completed":1,"preflight_ms":107.188,
  "execution_ms":32.632}. focus_before 0x557052b62dd0 (the Zen
  window). After-capture observation 0efbc71e453b (clean-observation).
  Session ran ~1s, indicator closed at 950ms, 3 hide + 3 show
  (capture_clean cycles), no stray procs after.
- cursorpos after: (3569,1547). Expected global from image
  (1105,645) + region [2464,902]: (3569,1547). EXACT, 0px error.
- Fresh observe f88074c35f5a after the click: same Zen ws1, same
  New Tab wallpaper, NO pill (session stopped), no navigation, no
  damage; cursor visible at the click point (1105,645) in the image.
  The click was harmless, as designed.

## 00:11 teardown: CLEAN
- No session procs, no indicator procs, no session.json, cu-cursor
  {"active":false,"ok":true,"schema":1,"token":""}. Hyprland PID 1515
  alive, Zen alive (window 0x557052b62dd0 unchanged, tabs intact).
  Desktop clean. (pgrep -f zen-ai shows PID 516844 vs F3b's 496121;
  window address and tabs unchanged, so this is the wrapper/child
  PID, not a Zen restart; no action needed.)
- NOTE for the parent: the OI (Omarchy adoption) worker finished
  00:08 (todolist-push d8a2ee2, 0 regression, +40 tests pass) and
  modified cu.environment() (OMARCHY_PATH) in the REPO; the installed
  tree I used was F1's md5-verified deploy, unaffected. The omasnap
  crash notification is explained (OA probe, not a system fault).

## VERDICT: F1 LIVE ACTIVATION PASS
- Backend: activate-session-backend.py works live; guard + glass
  load; shaders ready after the login-loader warm-up; cu-cursor
  active with the session token; socket dir + cursor-guard.sock
  present. 5-step proof: fresh observe, one click center of the
  active New Tab only, 0px error, verified by cursorpos + fresh
  observe, clean stop, second start returns the pill. Session pill
  PROVEN: visible in raw grim during the session, token matches
  snapshot, indicator endpoint exists, indicator PID 513273,
  gone after stop. New findings: (1) computer-use observe hides the
  pill during capture by design, so pill visuals need raw grim;
  (2) act --actions/--observation take FILE PATHS, not inline JSON
  or bare ids (F1's negative test never exercised this; the guardian
  died first); (3) SSH round trips take ~30s, so proof sessions
  need long sleeps (120s) to survive the latency. F1 phase DONE;
  F2 phase (act-now end-to-end with a live session) is next.
