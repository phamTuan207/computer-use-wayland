# Machine controllability for AI - final report

Date: Tue 2026-11-24, work 20:17-20:24 +07 (Asia/Ho_Chi_Minh)
Scope: owner's Omarchy laptop (Tailscale 100.70.92.52). Standing instruction: optimize for AI everything the user uses, so AIs can CONTROL everything on it more easily.
Track: CONTROLLABILITY, not cleanup. A machine-wide sweep finished earlier tonight (~/workspace/machine-opt-20261124/REPORT.md) and was mostly memory/disk cleanup. This track proves, live, the agent control path for every app the user uses. It does not redo cleanup.
Workers: BROWSERS (20:17:58-20:19:36), TERMINAL-SHELL-FILES (20:17:59-20:21:31), APPS (20:17-20:24). All via SSH (~/workspace/ssh-laptop.sh), short commands only.
Method: CLI/API first, then file/shell, then CDP/Marionette/BiDi, vision last. No restarts of Zen, Brave, or Chromium. No tab or window the owner opened was closed, navigated, or typed into. Zen R3-L3 setup untouched. No OpenRouter. No ydotool. No personal info in this report.
Worker logs: ~/workspace/machine-control-20261124/w-browsers.md, w-terminal-shell.md, w-apps.md, discord_ipc_probe.py.

## Answer to the owner's challenge

The earlier sweep freed memory and disk. This track answers the real question: can an agent DRIVE each app? The short answer: almost everything the user uses daily is already drivable by code, and the gaps are small and named below. Three things matter most tonight:
1. Chromium (mimeo PWA, Mochi's tab) is DOWN again. It was relaunched at 20:10 and exited cleanly at 20:15:54. Until it is relaunched detached, Mochi's tab has no control path and the whole webapp chain ends at a dead port 9223.
2. OmaCal has a full CLI. Earlier tracks recorded "no CLI/API found". That was wrong. `omacal agenda --days 1 --json` returned real events live tonight.
3. Discord has no message path. Presence write via IPC exists; reading or sending messages does not. That is the one large CLI-Anything candidate, and it carries ToS risk, so it needs the owner's explicit call.

## Per-app control table

### Browsers

| App | Control path | Exact command / endpoint | Live-test result |
|---|---|---|---|
| Brave (Muse PWA, clone1) | Chrome CDP 9224 via brave-origin-intel | curl http://127.0.0.1:9224/json/version, /json/list; WS Runtime.evaluate on page target | PASS. PID 375357, Chrome/157.0.8103.79, Protocol 1.3. 5 targets, page "Chat - clone1" at https://muse.ai/?__pwa=1. Read-only Runtime.evaluate returned document.title "Chat - clone1". Control proven live. |
| Chromium (mimeo PWA, clone2) | Chrome CDP 9223 via chromium-intel | curl http://127.0.0.1:9223/json/version; ps; ss; journalctl; /tmp/mimeo-relaunch.log | FAIL, DOWN. No chromium process, no 9223 listener at 20:18. See Chromium section. Not relaunched: relaunch needs an explicit order. |
| Zen | Firefox BiDi 9222 + Marionette 2828 | curl http://127.0.0.1:9222/json/version, /json/list, /; TCP connect to 2828 | PASS, READ-ONLY STATE ONLY. PID 404548, flags --remote-debugging-port=9222 --marionette, BuildID 20261118023529. 9222 answers httpd.js, /json/version 404, /json/list 404 (no Chrome CDP, as known). 2828 TCP open. No live session opened: Firefox allows one remote session and the Zen-update coordinator owns Zen for R3-L3. |
| Teams PWA | chromium-intel, --app-id | read ~/.local/share/applications/chrome-cifhbcnohmdccbgoicgdjpfamggdegmo-Default.desktop | PASS (file check, not launched). Exec points at chromium-intel. Pre-fix backup had /usr/bin/chromium, so the 22/11 fix holds. |
| Notion PWA | chromium-intel, --app-id | read ~/.local/share/applications/chrome-dcokohelbbehjlcjjfmhfbpdgfjcoopf-Default.desktop | PASS (file check, not launched). Exec points at chromium-intel. Fix holds. |
| open-url-in-chromium | chromium-intel, setsid detached | read script via which open-url-in-chromium | PASS (file check). Calls setsid chromium-intel --profile-directory=Default "$URL" detached, so the launcher never holds a live child. |
| Liner | CDP 9333 via ~/.local/bin/liner | read wrapper; TCP connect to 9333; read liner.desktop | PASS config, NOT RUNNING. Wrapper line 14 carries --remote-debugging-port=9333, AppImage Liner-0.2.11.AppImage exists, desktop Exec points at the wrapper. No Liner process, 9333 connection refused at 20:18. |
| Basecamp, Google Photos, Tailscale | omarchy-launch-webapp through chromium-intel | read *.desktop + omarchy-launch-webapp + chromium.desktop | PASS chain (file check, not launched). Default browser is zen.desktop, not Chromium-family, so the handler falls back to chromium.desktop, whose local Exec is chromium-intel. Chain ends at 9223. |
| HEY, Zoom | omarchy-webapp-handler-* then omarchy-launch-webapp | read HEY.desktop, Zoom.desktop, handler scripts | PASS chain (file check, not launched). Both handlers exec omarchy-launch-webapp (HEY rewrites mailto: to a compose URL, Zoom builds a join URL from confno/pwd). Same fallback chain, ends at chromium-intel, 9223. |

### Terminal, shell, files

| Item | Control path | Exact command (live) | Live-test result |
|---|---|---|---|
| kitty ls | kitty remote control over unix socket | kitty @ --to unix:/run/user/1000/omarchy-kitty-3726 ls | PASS. 1 OS window, 1 tab, window id 1, title omarchy: ~, cmdline herdr --session jarvis, cwd /home/james/Jarvis. Kitty 0.50.0. Bare `kitty @ ls` FAILS over SSH (no TTY); the --to form is required. |
| kitty get-text | kitty remote control, --match flag | kitty @ --to ... get-text --help; get-text --match id:99999 | PENDING. Command path proven (--help prints match docs, bad id errors cleanly). Real read not done: needs a scratch window, unsafe to pop one while the owner works, and the Jarvis window must never be read. Close during a handed-over window. |
| gh | gh CLI | gh auth status | PASS. Logged in github.com phamTuan207 (keyring), scopes gist, read:org, repo, workflow. |
| tailscale | tailscale CLI | tailscale status | PASS. 100.70.92.52 omarchy online, this VM 100.104.211.95 muse active via relay nyc. |
| zoxide | zoxide CLI, direct form | cd "$(zoxide query Documents)" && pwd | PASS. Resolved to /home/james/Documents. |
| fcitx5-remote | fcitx5-remote CLI | fcitx5-remote -n | PASS. Returned ngosen. |
| omarchy-shell ping | omarchy-shell IPC via guienv | guienv env OMARCHY_PATH=/usr/share/omarchy omarchy-shell shell ping | PASS, with correction. Bare guienv form FAILS (guienv omits OMARCHY_PATH). Correct form is target + method: omarchy-shell shell ping. Reply ok. |
| hyprctl | hyprctl via guienv | guienv hyprctl version; guienv hyprctl clients | PASS. Hyprland 0.57.2. clients lists 3 live windows (kitty herdrdrop, Muse PWA, Zen). Read-only. |
| wtype / grim / wl-copy | shell tools | command -v wtype grim wl-copy | PASS (presence). All in /usr/bin. Live wtype/wl-copy NOT tested (would inject keystrokes / clobber clipboard while the owner works). |
| grim screenshot | grim via guienv | guienv grim /tmp/control-test-20261124.png | PASS. 1,165,181 byte PNG 1920x1200, read back, deleted, sent nowhere. |
| Nautilus replacement | shell (this IS the control path) | echo > /tmp/...; ls; mv; cat; rm | PASS. Create, list, move, read, delete all worked, verified gone. No GUI driver needed or built. |
| Obsidian read | vault markdown files on disk (this IS the control path) | find "/home/james/James's second brain" -name "*.md"; head -n 10 note | PASS. Vault /home/james/James's second brain (has .obsidian). 24 .md files, 19,049 lines. First 10 lines of a real 1,331-line note read back. No note content pasted here. |
| Obsidian write + delete | shell write into vault | printf > vault/control-test-20261124.md; cat; rm; ls | PASS. Scratch note written (112 bytes), read back, deleted, verified gone. |
| nvim | nvim CLI | nvim --version; nvim --headless -c "%s/.../" -c "wq" file | PASS. NVIM v0.12.6. Headless edit exit 0, change verified, file deleted. |
| imv | /usr/bin/imv wrapper + scripts/image_viewer.py | cat /usr/bin/imv; python3 scripts/image_viewer.py list | PASS (resolution). /usr/bin/imv is a 117-byte sh wrapper that execs imv-wayland under Wayland. image_viewer.py list returned [] (no viewer running). Live launch NOT tested (would pop a window on the owner's screen). |
| mpv | mpv CLI, --input-ipc-server | mpv --version; mpv --list-options \| grep input-ipc; IPC get_property over unix socket | PASS. mpv v0.41.0-dirty. --input-ipc-server confirmed via --list-options. Idle IPC server launched, get_property mpv-version returned success over the socket, quit via IPC killed it. No audio or video played. Socket, log, dummy file deleted after. |
| foot | none needed | n/a | NOT COVERED by design. No remote control; agents use kitty/shell instead. Nothing built for it. |

### Desktop apps

| App | Control path | Exact command / endpoint | Live-test result |
|---|---|---|---|
| Discord | Rich Presence IPC socket, write-only presence. No CLI, no message path. | Socket $XDG_RUNTIME_DIR/discord-ipc-0, opcode 0 handshake {"v": 1, "client_id": ...}, opcode 1 SET_ACTIVITY. Binary /home/james/.local/opt/Discord/discord | PARTIAL. Socket path proven from the running presence service source, but Discord NOT running tonight: no process, no socket, probe exit 1. discord --help prints only Discord 1.0.169. Presence service discord-window-presence running (PID 1117) but logging connect failures every 2 s because Discord is down. discord-coding-status disabled, inactive. |
| Zalo | None proven. GUI-only Electron app. | Binary /usr/bin/zalo (156 MB ELF, not a wrapper; the --disable-gpu-sandbox flag lives in the .desktop Exec line). Config ~/.config/ZaloData | STATUS ONLY, per owner pause. NOT running tonight. zalo-cli dir exists on the VM (~/workspace/agent-native-3/zalo-cli/) but was NOT run, NOT built, NOT touched. Owner PAUSED Zalo CLI until after the acceptance test. |
| OmaCal | Full CLI, proven live. Reads hit local SQLite DB, writes go through the running app over a local socket. | omacal agenda --days 1 --json; omacal calendars --json; omacal events list/show/create/update/delete/respond; omacal tasks ...; omacal commands --json. Socket /run/user/1000/omacal/ipc.sock. DB ~/.local/share/com.omacal.app/omacal.db. Usage in ~/.agents/skills/omacal/SKILL.md on the laptop. | PASS. agenda --days 1 --json (with DISPLAY set) returned real events for 24/11 (eventId 768, eventId 141 wake-up block 05:00-05:15). calendars --json returned real calendars (the owner's calendar account, primary "School" id 9). Caveats: CLI needs DISPLAY set (without it, GTK init panics before parsing args); app NOT running tonight, reads still work, writes need it running. |
| ZCode | No CLI. GUI-only Electron editor. File args only. | AppImage /home/james/Applications/ZCode-3.17.1-linux-x64.AppImage, .desktop Exec "<AppImage>" %U | PASS (negative). --help printed no help, proceeded to launch, then died on missing X server and dumped core (harmless, no window). Not running tonight. Editing is file-based: files on disk, no GUI driving needed. |
| VS Code | code CLI + repo wrapper scripts/vscode_cli.py (tabs from workspaceStorage state.vscdb) | python3 ~/computer-use-wayland/scripts/vscode_cli.py tabs, version, status; code --version, code --status | PASS. tabs returned real open tabs across workspaces (LTHDT files). version 1.146.0. code --status warns it needs a running instance; VS Code NOT running now (pgrep empty), not launched. Note: the wrapper's status JSON says "running": true while stdout is the not-running warning, so read stdout, not the running field. |
| ComfyUI | systemd user unit, HTTP 8188 when running | systemctl --user start/stop/status comfyui; unit /home/james/.config/systemd/user/comfyui.service | PASS (status only, not started). status inactive (dead), is-enabled disabled, port 8188 closed. Log shows it ran today 20:00:32-20:01:01 (Codex start/stop test), which is the proven control path. |
| Liner | CDP 9333 (BROWSERS worker) | see Browsers table | Not duplicated by APPS. |
| Muse PWA (clone1) | Chrome CDP 9224 | see Browsers table | PASS (BROWSERS worker). |
| mimeo PWA (clone2) | Chrome CDP 9223 | see Browsers table | FAIL, DOWN (BROWSERS worker). |

### Services and CLIs already proven by earlier tracks (cited, not re-tested)

computer-use CLI + relay (broker running), opencode serve 4096 (HTTP 200), fcc-server 8082 (running), Codex 0.172.0 daemon (healthy), gh, tailscale, hyprctl via guienv, omarchy-shell. All from the agent-native inventory (22/11, independently verified 39/41 claims PASS) and the machine-opt sweep (24/11). No re-test tonight except where listed above.

## Chromium: down, what happened

Current state at 20:18-20:19: DOWN. No Chromium process, no 9223 listener.
- 20:10:07: systemd user scope app-org.chromium.Chromium-419746.scope started. /tmp/mimeo-relaunch.log: "DevTools listening on ws://127.0.0.1:9223/devtools/browser/cbf24134-6c39-4c21-a285-3daa64827dac". Parent confirmed CDP answered at ~20:10 with page "Chat - clone2".
- 20:15:27: last log line, viz "Frame latency is negative: -7.76 ms" (benign-looking display error, not a crash signature).
- 20:15:54: scope ended: "Consumed 7.296s CPU time over 5min 47.680s wall clock time, 103.4M memory peak." No killed, no signal, no stop reason in the journal (20:09:30 to 20:16:30).
- Sessions files written at 20:15 (Tabs_13439999409712610, 230407 bytes), consistent with a clean session save on exit.
- Crash Reports: newest dumps 14:25 and 13:18, nothing at 20:15. dmesg: no OOM or kill lines. Preferences exit_type keys read as None, inconclusive.
Conclusion: clean, silent exit at about 20:15:54, 5m47s after launch. NOT a crash (no dump), NOT OOM (no dmesg evidence), NOT a journal-recorded kill. Cause undetermined from logs. Hypothesis, not proven: the launch was tied to a transient launcher/SSH session (many short SSH scopes deactivating 20:09-20:11) rather than a detached session.
What restores it: a detached relaunch through chromium-intel (same pattern as open-url-in-chromium: setsid, own session, trailing &, detached from the launching shell) so it survives the launcher exiting. The BROWSERS worker did NOT relaunch it: relaunch needs an explicit order. When relaunched, verify with curl http://127.0.0.1:9223/json/list and confirm the mimeo PWA page target returns.
Impact until then: Mochi's tab has no agent control path, and the Teams/Notion/Basecamp/Photos/HEY/Zoom/Tailscale chain ends at a dead 9223.

## What was built

One minimal script, ~/workspace/machine-control-20261124/discord_ipc_probe.py (3,238 bytes, also committed to the repo alongside this report):
- Read-only Discord IPC probe. Checks for /run/user/1000/discord-ipc-0, attempts the opcode 0 handshake with a known client id, reports JSON (ok, running, socket, user on READY). Never sends SET_ACTIVITY, never writes presence, never touches config or messages. Default client id is the codex id 1517375602662051900 taken from the user's own discord-window-presence service (no new app registration, no new secret).
- Attribution: protocol from Discord's public Rich Presence IPC docs plus the user's own service source /home/james/.local/share/discord-window-presence/main.py (201 lines, read live tonight). No CLI-Anything code was used, so no original-author attribution is owed beyond the service source already on the owner's machine. The probe is original code written tonight.
- Live test: copied to the laptop as /tmp/discord_ipc_probe.py and run: {"ok": false, "running": false, "socket": "/run/user/1000/discord-ipc-0", "error": "socket absent, Discord not running"}, exit 1. The READY branch is untested because Discord was not running; it needs one run while Discord is open to prove end to end.
- Nothing else was built. No CLI was written for foot, Nautilus, Obsidian, ZCode, or OmaCal, because shell/files already cover them (CLI-Anything rule: CLI is last resort only, never CLI-ify a task plain shell already does).

## Corrections to earlier track claims

- OmaCal: earlier tracks recorded "no CLI/API found". Wrong. OmaCal has a full documented CLI (agenda, events, tasks, calendars, search, weather, commands catalog) plus a local skill file at ~/.agents/skills/omacal/SKILL.md. Reads proven live tonight.
- Zalo: an earlier brief said /usr/bin/zalo is "a wrapper with --disable-gpu-sandbox". Wrong on this machine: /usr/bin/zalo is the 156 MB ELF binary itself. The flag is in the .desktop Exec line.
- Discord: earlier tracks recorded "no CLI/API found". Refined, not overturned: there is no CLI and no message path, but there IS a working write-only presence path (IPC socket) proven by the running presence service's source.
- Brave double --remote-debugging-port=9224: already known (flags conf + wrapper). The live Brave cmdline still shows it twice (harmless, same value). The PWA optimizer removed the conf line tonight; the fix takes effect at the next Brave launch.
- Zen CDP: /json/version 404 is expected, not a failure. Zen has no Chrome CDP; its control path is Marionette 2828 + BiDi 9222.

## Still missing and why (needs an owner or coordinator decision)

1. Chromium up (mimeo PWA, Mochi's tab). Needs a detached relaunch order (setsid chromium-intel, own session). Until then, no control path for Mochi's tab and the webapp chain ends at a dead 9223.
2. Discord message read/send. No path exists. CLI-Anything candidate, HIGH gap, large build, and the user-token REST route is ToS-risky (account-lock risk). Do NOT build without the owner's explicit approval. The safe small piece (presence via IPC) is already covered by the existing service plus tonight's probe.
3. Zalo message control. PAUSED by owner order until after the acceptance test. Status only tonight. Do not resume without the user's go-ahead.
4. kitty @ get-text real read. Needs a handed-over machine window (create a scratch window, read it, close it). Blocked tonight because popping a window risks stealing focus while the owner works.
5. Zen live Marionette/BiDi session proof. Blocked by the one-session rule and R3-L3 ownership. Wait for a window where Zen is free.
6. OmaCal writes. Not live-tested (would touch the real calendar). Safe test: launch the app, add a throwaway task, verify, delete it. Left for a follow-up.
7. Liner live 9333 listener. Needs Liner launched first.
8. Webapp live end-to-end launch (Teams, Notion, Basecamp, Photos, HEY, Zoom, Tailscale). Not done: launching would open unrequested windows, and half the chain ends at dead 9223.
9. VS Code full --status diagnostics. Needs a running instance; not running tonight, launching was out of scope.
10. ComfyUI HTTP API. Not tested (service stopped, GPU/RAM cost). systemd start/stop is the proven control path.
11. Live imv launch, live wtype typing, live wl-copy use. Presence proven; live use needs a handed-over window or a safe target.
12. Chromium exit cause. Undetermined from logs. If it exits again after a detached relaunch, capture the exit live (watch the scope and window state at the moment it dies) instead of re-reading logs after the fact.

## Findings for future briefs

- guienv omits OMARCHY_PATH from its env allowlist, so `guienv omarchy-shell shell ping` fails. Use the full form `guienv env OMARCHY_PATH=/usr/share/omarchy omarchy-shell shell ping`, or add OMARCHY_PATH to guienv's allowlist on the laptop (machine-specific config, laptop only, never in the repo).
- `kitty @` over SSH needs the explicit socket: `kitty @ --to unix:/run/user/1000/omarchy-kitty-<pid> <cmd>`. Bare `kitty @` fails with no TTY.
- vscode_cli.py `status` JSON says "running": true even when VS Code is not running. Read its stdout, not the running field.
- Never reuse window/tab counts or ids; always look them up live (a Chromium window count changed between two probes 22/11 because the owner opened another window).
- OmaCal CLI needs DISPLAY set or GTK init panics before parsing args.
- ZCode --help with DISPLAY unset launches the app and core-dumps on the missing X server. Do not run it that way again; use DISPLAY=:0 or skip --help.
- mpv --help does not list --input-ipc-server; --list-options does.

## Files produced

- VM: ~/workspace/machine-control-20261124/REPORT.md (this file), w-browsers.md, w-terminal-shell.md, w-apps.md, discord_ipc_probe.py.
- Laptop: /tmp/cdp-probe.mjs (ephemeral Brave probe, harmless), /tmp/discord_ipc_probe.py (copy of the probe, used for the live test). No persistent change on the laptop except the probe copies in /tmp.
- Repo (todolist-push): improvements/machine-control-20261124.md (this report), improvements/machine-control-discord-ipc-probe.py (the probe script).
- Nothing was broken. No restarts of Zen, Brave, or Chromium. No tabs closed or navigated. No personal data, music, or Zen profile touched. All scratch files created tonight were deleted and their deletion verified.
