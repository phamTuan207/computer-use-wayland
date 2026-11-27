# COORD-AGENT-NATIVE-2 log

Coordinator: COORD-AGENT-NATIVE-2, reporting to Muse tong only.
Task received: 17:45 +07 Sun 2026-11-22.
Repo: ~/workspace/computer-use-wayland (VM copy), branch todolist-push.
Scope: MACHINE SETUP ONLY. Do not touch the paused campaign track
(steps 0-11, rung 3, todolist, error file). Do not message the owner.
Owner is USING the machine right now (logging into new Muse accounts
in Brave). No relaunch of Brave/Zen/Chromium, no focus steal, no tab
moves in the user's Zen, no keystrokes, no clicks.

Standing rules: wall-clock Asia/Ho_Chi_Minh plus elapsed time. No em
dash (U+2014) or en dash (U+2013) anywhere. No ydotool. No personal
info on GitHub. Machine-specific config lives ONLY on the laptop,
never in the repo. Lauren Tan evidence standard: every claim carries
a test command, its output, a commit hash, and a time log. No
self-grading: each claim gets an independent verification worker.
Stall over 15 min with no progress: report to Muse tong at once.

## Time log

- 17:45 +07, T+0m: task received from Muse tong.
- 17:45-17:47 +07, T+0m to T+2m: read prior report
  improvements/worker-click5-agent-native-exec-log.md (P1-P10 done
  16:02-16:22, commit 53639c7) in full. Inventory doc on laptop
  (~/.config/agent-computer-use/machine/agent-native-inventory-20261122.md,
  810 lines) assigned to both inventory workers to read live.
- 17:47 +07, T+2m: spawned INV-DESKTOP (desktop files + wrappers)
  and INV-SYSTEM (autostart + systemd services + CLIs + live port
  map) in parallel. Reports go to ~/workspace/agent-native-2/
  inv-desktop-report.md and inv-system-report.md.

## Initial state (verified by Muse tong 17:43-17:47, to re-verify live)

- Chromium from menu via wrapper ~/.local/bin/chromium-intel, already
  carries --remote-debugging-port=9223. CDP 9223 answering,
  Chromium PID 18451.
- Brave from menu via wrapper ~/.local/bin/brave-origin-intel, JUST
  fixed by Muse tong: --remote-debugging-port=9224 added, backup at
  brave-origin-intel.bak-20261122-9224, syntax checked OK. CDP 9224
  answering, Brave PID 17673/17681. Cold-launch NOT verified:
  owner is using Brave to log in new accounts, relaunch FORBIDDEN
  until the user permits.
- Zen from menu/Super Z via wrapper ~/.local/bin/zen-ai, already
  carries --remote-debugging-port=9222 --marionette. Zen PID 14625
  running.
- Hyprland new PID 3638 from 17:19 after the black screen incident
  (fixed: input-stall-monitor.service Wants=graphical-session.target
  line removed). Desktop is up.
- Convention proven by zen-ai: flags live in the WRAPPER SCRIPT in
  ~/.local/bin, NOT in the Exec= line of the .desktop file, because
  omarchy-launch-browser (Super Z) takes only the binary path and
  drops all arguments. All fixes follow this convention.

## Prior work, not to redo

- C5-AGENT-NATIVE-INV (inventory 14:07, laptop-only doc, 810 lines,
  sha256 d750a3e14f2363a6e2a0e40b9e33cb062acec974f17533bebad5ff9c12d568a8).
- C5-AGENT-NATIVE-EXEC (P1-P10 done 16:22, commit 53639c7, coord log
  a46180b "Brave 9224 live"). P1 leaks killed. P2 Brave 9224 via
  flags conf + relaunch, verified live. P3 no pending Zen update.
  P4 second-Chromium 9223 trap proven + documented. P5 kitty @ ls
  proven, get-text blocked (no scratch terminal). P6 VS Code tabs
  read proven, no instance running, wrapper running:true false
  positive recorded as unexplained. P7 no Omafile API, closed.
  P8 reboot recovery design doc only, autostart edit NOT done,
  needs separate owner approval. P9 Super+T/n/zd fixed in docs.
  P10 port map + launch chains in fastest-paths.md.

## Delegation

- INV-DESKTOP: full .desktop + wrapper inventory, read-only.
- INV-SYSTEM: autostart + systemd services + CLIs + live port map,
  read-only.
- Next after both return: synthesize gaps, spawn fix worker(s),
  then an independent verification worker for every claim.

## INV-SYSTEM returned 17:48 +07 (report
~/workspace/agent-native-2/inv-system-report.md)

Work time 17:46:24-17:47:44 +07, about 1m20s of probes. Read-only,
zero changes on the laptop, zero keystrokes/clicks/grim/relaunch.

- Autostart: 4 files, 1 runs (omacal), 0 browsers. Matches P8.
  Autostart.lua also has no browser. Ready per current P8 design,
  not ready if the goal is browsers auto-open after reboot.
- Services: 13 units checked. 10 enabled and active running
  (relay, input-stall-monitor, discord-window-presence,
  crash-watch, fcitx5, sleep-lock, opencode-serve,
  opencode-telegram, tele-image-inbox, voxtype). Verified
  separately: input-stall-monitor.service has NO
  Wants=graphical-session.target line any more, only After=.
  The 17:19 fix holds. discord-coding-status disabled + inactive
  (intent unclear). 1 oneshot static inactive (normal).
  1 masked (app-zalo@autostart).
- Ports 5/5 answer as expected: Zen 9222 BiDi (404 on
  /json/version, expected, Zen has no CDP), Marionette 2828
  (TCP connect OK, no HTTP), Chromium 9223 (Chrome/157.0.8103.38),
  Brave 9224 (Chrome/157.0.8103.79, persistent, flags conf line
  10 intact after reboot), opencode 4096 (HTTP 200). No listener
  left on [::1]:9223. Clean split.
- Processes: Zen PID 14625, Brave 17681, Chromium 18451, kitty
  3726 (Jarvis), relay 3913, opencode 1102 all running. No
  Puppeteer leak (P1 still clean). Missing: code, fcc-server.
- CLI: 13/17 ready. Relay status idle, hyprctl 0.57.2 via guienv,
  kitty @ ls works, omarchy-shell ping ok, gh logged in, tailscale
  online 192.0.2.1, nvim 0.12.6, zoxide 0.10.0, fcitx5-remote
  ngosen. Not ready: kitty get-text (no scratch terminal),
  code --status (VS Code not running), Omafile API (none, P7
  closed), fcc (missing from PATH, no server).
- Gaps queued for fix decisions (9 items, see the report section
  7): browser autostart needs owner decision; kitty scratch
  terminal; VS Code launch; fcc startup path; discord-coding-status
  enable question; Zen Marionette/BiDi live session untested
  (single session, do not compete); opencode quota dead; browser
  tabs changed (owner's new accounts, endpoint lookup must redo
  by URL prefix, never reuse old tab ids).
- INV-DESKTOP still running at 17:48 +07. Waiting for it before
  synthesizing fixes.

## INV-DESKTOP returned 17:56 +07 (report
~/workspace/agent-native-2/inv-desktop-report.md)

Work time 17:46-17:56 +07, about 10 min. Read-only, zero changes
on the laptop, zero keystrokes/clicks/navigation.

- Census: 32 user-local .desktop files, 96 system, 107 wrappers
  in ~/.local/bin. Main table 26 entries: 15 agent-ready, 11 not.
- All 3 browsers ready, verified live 17:47:34 +07: Zen PID 14625
  (9222 BiDi + 2828 Marionette), Brave PID 17681 (9224,
  Chrome/157.0.8103.79), Chromium PID 18451 (9223,
  Chrome/157.0.8103.38).
- omarchy-launch-browser read in full: takes ONLY the first token
  of Exec= (sed first-token), drops all args. Handoff fast path
  never applies to a wrapper binary. Fallback runs the wrapper
  under systemd-run + uwsm-app. Convention CONFIRMED live:
  flags must live in the wrapper, never in Exec=.
  omarchy-launch-webapp forces chromium.desktop for non-Chromium
  default browsers, reads Exec (user-local first, so
  chromium-intel), carries 9223. Basecamp, Google Photos, HEY,
  Zoom, Tailscale all CO by that chain.
- Wrappers read in full: zen-ai (9222 + marionette), brave-origin-intel
  (9224, edited 17:44 by Muse tong, backup .bak-20261122-9224
  correct), chromium-intel (9223), liner (9333, APPIMAGE_EXTRACT_AND_RUN=1),
  guienv (support tool), open-url-in-chromium (raw binary, no flag),
  zalo (GPU workaround only).
- Gaps: (1) Teams PWA + Notion PWA Exec point at raw
  /usr/bin/chromium, bypass chromium-intel, no 9223; same gap in
  open-url-in-chromium. (2) Brave wrapper-flag cold launch
  UNPROVEN (live Brave started 17:36:48, before the 17:44 wrapper
  edit); next launch will carry 9224 TWICE (conf line added 16:13
  + wrapper line added 17:44), same value, expected harmless
  (last-wins), but must be a conscious choice. (3) VS Code no
  launch flag, CLI-side control only, not running. (4) foot,
  Nautilus, Omafile, Obsidian, ZCode, Discord, Zalo, OmaCal have
  no agent control path, outside campaign workload, no fix
  proposed. (5) Zen background update timer still active. (6) 3
  junk NoDisplay .desktop files, harmless. (7) mimeapps.list in
  ~/.local/share/applications is 0 bytes, cosmetic, defaults
  resolve via ~/.config/mimeapps.list.
- Firefox and Google Chrome NOT installed. `brave` and `zen` missing
  as bare commands by design (wrappers + absolute paths).

## Fix plan (decided 17:57 +07)

- FIX-1 (spawned now): (F1) Teams + Notion PWA Exec to
  chromium-intel, backup first. (F2) open-url-in-chromium to
  chromium-intel, backup first. (F3) Brave double-9224: read both
  scripts, document exact composition, KEEP BOTH as deliberate
  belt-and-braces, do NOT remove either line, cold-launch
  verification stays pending owner permission. (F4) fcc startup
  path investigation, start the background server only if the
  path is clear and safe, else record pending. (F5) record
  dispositions for the rest (VS Code quiet window, kitty scratch
  terminal, discord-coding-status question, autostart owner
  decision, Zen update timer, junk files, mimeapps, liner 9333,
  opencode quota). No launches, no relaunches, no tab moves.
- VERIFY-1 after FIX-1: independent worker re-checks every claim
  in both inventory reports plus every fix claim, live, read-only.

## FIX-1 returned 17:54 +07 (report
~/workspace/agent-native-2/fix-1-report.md)

Work time 17:51-17:54 +07, about 3 min on the laptop. Zero
windows opened, zero tabs moved, zero keystrokes/clicks. All three
browsers untouched (PIDs 14625/17681/18451 intact start to end).

- F1 DONE, live check pending: Teams + Notion PWA Exec changed to
  ~/.local/bin/chromium-intel, backups
  .bak-20261122-1752 (409 + 326 bytes), desktop-file-validate OK,
  diff exactly 1 line per file. Live launch check blocked (would
  open a window on the owner's screen), waits for a quiet window.
- F2 DONE, live check pending: open-url-in-chromium line 21
  changed to chromium-intel, backup .bak-20261122-1752 (1129
  bytes), bash -n OK, diff exactly 1 line. Live run check blocked
  for the same reason.
- F3 DONE (decision, no edit): Brave double-9224 confirmed
  (wrapper line 5 + conf line 10, conf flags first then wrapper
  args, verified by reading /usr/bin/brave-origin). KEEP BOTH as
  deliberate belt-and-braces, remove neither. Cold-launch check
  waits for owner permission.
- F4 DONE + verified live twice: fcc-server restarted detached as
  `fcc-server --auto-started` (the exact form from
  launchers/common.py server_command()), PID 36226, port 8082
  LISTEN, /admin/api/status {"status":"running"}, Admin HTTP 200.
  Correction to INV-SYSTEM: fcc-server IS on PATH via symlink
  ~/.local/bin/fcc-server, only bare `fcc` is missing. Caveat:
  no systemd unit or autostart keeps it alive after reboot,
  persistence needs a decision.
- F5: 9 items recorded with dispositions, no changes (VS Code
  quiet window, kitty scratch terminal, discord-coding-status
  question, browser autostart owner decision, Zen update timer,
  junk .desktop files, mimeapps.list 0 bytes, liner 9333 no
  conflict, opencode quota dead).
- One exec call in the worker returned exit 1: the expected
  `command -v fcc` rc=1 (fcc missing), accounted for in the
  report, nothing broken.

## Verification (spawned 17:57 +07)

- VERIFY-1: independent worker, fresh eyes, re-checks every claim
  in inv-desktop-report.md, inv-system-report.md and
  fix-1-report.md live and read-only, then reports PASS/FAIL per
  claim with its own evidence. No launches, no relaunches, no
  tab moves, no file changes.

## VERIFY-1 returned 17:56 +07 (report
~/workspace/agent-native-2/verify-1-report.md)

Work time 17:54:37-17:55:56 +07, about 1m20s. Read-only, zero
changes, zero launches/relaunches/tab moves/keystrokes/clicks.

- 41 claims checked: 39 PASS, 2 FAIL, 10 not verifiable live.
- PASS highlights: 32/96 .desktop counts, all 3 wrappers carry
  the right flags, liner 9333, kitty allow_remote_control yes,
  firefox/google-chrome not installed, autostart 4 files 0
  browsers, input-stall-monitor Wants line gone (plus a sweep:
  NO local service has Wants=graphical-session.target any more),
  5 ports live with the right versions (Chromium 157.0.8103.38,
  Brave 157.0.8103.79), 3 browsers on the same PIDs, both PWA
  backups + diffs 1 line + validate OK, open-url backup + diff
  1 line + bash -n OK, fcc-server PID 36226 port 8082 status
  running with the same instance_id, admin HTTP 200.
- FAIL 1 (minor, explained): INV-SYSTEM counted 4 windows at
  17:47:03, VERIFY-1 counted 5 entries at 17:55:56, Chromium PID
  18451 appearing on ws1 and ws2. The owner opened another
  Chromium window between the two probes (the user is using the
  machine). The count is time-varying, not a report defect.
  Lesson recorded: never reuse window/tab counts or ids, always
  look them up live.
- FAIL 2 (minor, explained): INV-SYSTEM counted 8 local service
  files, VERIFY-1 counted 9, the 9th is the masked
  app-zalo@autostart.service. Total 13 units still correct, only
  the categorization differed.
- Not verifiable live (10, all with reasons): PWA launches,
  open-url run, Brave cold-launch, kitty get-text, Marionette
  live session, VS Code live status, autostart after reboot,
  opencode quota, fcc --help re-run, the 17:47 window count.
  All blocked because launching or relaunching would disturb
  live use.
- Drift noted: relay state changed idle/owner null at 17:47:10
  to finished/owner w-sync at 17:54:55, broker still running.
  That is live campaign work, not a report error.

## Context change during this run (from MEMORY.md, 17:55 +07)

- The owner handed the machine to Muse tong (GIAO MAY) and will
  not touch it any more. mei replaces clone1, mochi replaces
  clone2, all processes unchanged, only nicknames changed.
  COORD-CLICK-6 resumed the campaign at 17:47. Watchdog-zen
  moved to every 20 min.
- Consequence for the blocked live checks: they stay blocked, now
  because live campaign work is running on the laptop (relay
  owner w-sync), not only because the owner is using the machine.
  Do not relaunch Brave or open PWA windows while campaign lanes
  are live. Re-attempt in a quiet window owned by the coordinator.

## Final verified inventory (condensed)

- Zen (menu/Super Z via zen-ai): YES, 9222 BiDi + 2828
  Marionette, PID 14625, verified live 17:47 + 17:55.
- Brave (menu via brave-origin-intel): YES, 9224, PID 17681,
  verified live; cold-launch after the 17:44 wrapper edit NOT
  verified (blocked, see above).
- Chromium (menu via chromium-intel): YES, 9223, PID 18451,
  verified live.
- Muse Brave PWA: YES, 9224 via wrapper. mimeo Chromium PWA:
  YES, 9223 via wrapper.
- Teams PWA: YES after F1 fix (was NO), live launch NOT verified.
  Notion PWA: YES after F1 fix (was NO), live launch NOT verified.
- Basecamp, Google Photos, HEY, Zoom, Tailscale: YES via the
  webapp chain (9223 through chromium-intel).
- kitty: YES (remote control on, ls proven; get-text NOT verified,
  no scratch terminal).
- nvim: YES (CLI-native). imv: YES (resolves to imv-wayland).
  mpv: YES (CLI-native). liner: YES (9333).
- VS Code: PARTIAL (tabs readable via vscode_cli.py, code --status
  needs a running instance, not running).
- computer-use CLI + relay: YES (broker running).
- hyprctl via guienv: YES (0.57.2). omarchy-shell via guienv:
  YES (ping ok; Omafile has no CLI API, P7 closed).
- gh: YES (logged in). tailscale: YES (online). fcitx5-remote:
  YES. zoxide: YES (direct form). wtype/grim/wl-copy: present
  (grim not run while the machine was in use).
- fcc-server: YES after F4 (PID 36226, port 8082 running); bare
  `fcc`: NO (missing from PATH).
- opencode: YES technically (4096 HTTP 200), but the Deepseek
  free quota is exhausted, so it is not a live execution path.
- foot, Nautilus, Obsidian, ZCode, Discord, Zalo, OmaCal: NO
  agent control path, outside the campaign workload, no fix
  proposed.
- Autostart: no browser autostarts (pending owner decision).

## Decisions needed (for Muse tong / the owner)

1. Browser autostart after reboot (P8): design doc only. Needs
   owner decision before adding any autostart entry. A wrong
   autostart can open a second Chromium fighting for port 9223.
2. discord-coding-status disabled + inactive: intentional or not?
   Do not enable without confirmation.
3. fcc-server persistence: running detached now (PID 36226), no
   systemd unit or autostart keeps it alive after reboot. Needs
   a decision on adding a service or autostart entry.
4. VS Code launch + kitty scratch terminal: both need a quiet
   window (opening either changes the screen state).
5. Brave cold-launch + PWA live launches + open-url live run:
   all wait for a quiet window with coordinator ownership (live
   campaign work is running now).
6. Zen Marionette/BiDi live session test: single remote session
   only, do not compete with live work.
7. Brave double-9224: keep both lines (conf + wrapper) as
   deliberate belt-and-braces. Revisit only if the cold-launch
   check shows a problem.

## Handover

- Inventory verified: 41 claims independently re-checked, 39
  PASS, 2 minor FAILs explained, 10 not verifiable live (all
  with reasons recorded).
- Fixed in this round: F1 (Teams + Notion PWA to chromium-intel),
  F2 (open-url-in-chromium to chromium-intel), F4 (fcc-server
  restarted, verified answering). F3 (Brave double-9224) decided:
  keep both lines.
- Still pending (with reasons): Brave cold-launch, PWA live
  launches, open-url live run, VS Code launch, kitty scratch
  terminal, browser autostart, fcc-server persistence,
  discord-coding-status question, Zen Marionette live session.
- Worker reports (VM workspace, not repo):
  ~/workspace/agent-native-2/inv-desktop-report.md,
  inv-system-report.md, fix-1-report.md, verify-1-report.md,
  coord-log.md.
- Repo log: improvements/worker-click5-agent-native-2-log.md
  on todolist-push (this file).
