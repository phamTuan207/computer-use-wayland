# Worker OA log: Omarchy agentic surfaces, Sat 2026-11-21 +07

## 23:37:32 probe 1: omarchy CLI top level
- `omarchy --help`: groups include agent, ascii, audio, bar, battery, bluetooth, branch, branding, brightness, capture, channel, clipboard, cmd, config, crash, debug, default, dev, dictation, disk, display, dns, dock, drive, file, finalize, font, games, hibernation, hook, hw, hyprland, install, installed, kernel, language, launch, menu, migrate, mise, monitor, network, notification. Version file: 4.0.0.alpha.
- walker NOT installed. ~/.local/share/omarchy/ does NOT exist.
- Web (search 23:37): Omarchy = DHH Arch + Hyprland + Quickshell, "Beautiful, fun & agentic Linux". Agent-first: default agent picker, lazy-loaded mise stubs in ~/.local/bin, `omarchy agent prompt` unattended auto-approve, crash diagnosis via systemd-coredump + diagnose-crash skill, agents usage panel (5h/weekly limits, token usage), Omarchy skill symlinked into agent skill dirs, LM Studio/Ollama local models, plain-text configs.

## 23:37:54 probe 2: agent groups + skill hunt
- agent group: `omarchy agent` (launch default), `agent prompt <prompt>` (unattended auto-approve), `agent crash <pid>` (diagnose with default agent), `agent usage update`, `agent account add/copy/list/mode/remove/rename/use`, `agent account exec/state/transfer`.
- hyprland group: focus app, monitor focused/internal/laptop/scaling/watch, toggle flags, window close all/minimize/pop/transparency/width, workspace layout current/default/toggle. NO workspace focus/goto command.
- menu group: toggle/summon/close/refresh/ping [route], clipboard, emoji, file, herdr/tmux keybindings --print, images, input, keybindings, plugin, select, share, timezone.
- capture group: qr, screenrecording, screenshot [smart|region|windows|fullscreen|scroll] [copy|save], text (OCR), webcam resize.
- launch group: 1password, about, browser [url], config editor, editor, floating terminal, nautilus, openclaw, or focus, or focus tui/webapp, signal, spotify, terminal, tui, webapp.
- notification group: battery, dismiss, send (with --exec/--action), time, weather. crash group: mute. debug: --print, idle. monitor: state. cmd: missing/present. clipboard group: no documented commands.
- Skill FOUND on disk: /usr/share/omarchy/default/agents/skills/{omarchy,diagnose-crash,omarchy-app}/SKILL.md. ~/.claude/skills/: computer-use, diagnose-crash, omacal, omarchy, omarchy-app. ~/.codex/skills/: many. /usr/share/omarchy/bin/ has omarchy-agent-* binaries including usage collectors per provider (agy, claude, codex, copilot, cursor, deepseek, devin, fireworks, grok, grokbot, hermes, kimchi, kimi, local, minimax, muse, ollama, opencode, openrouter, qwen, synthetic, vibe, zai).
- Web (search 23:37): official manual AI page confirms lazy mise stubs, `omarchy default agent`, Super+Shift+Ctrl+A, `omarchy agent prompt` auto-approve, terminal shortcuts a/c/cx/cy, agents panel with 5h/weekly limits, usage-update every 15 min, crash watch plus diagnose-crash skill, `omarchy agent crash <pid>`. 4.5 adds omarchy-app skill (C++/Qt Quick app builds).

## 23:38:20 probe 3: skill read + usage + plugin + menu select
- omarchy SKILL.md read in full (276 lines): REQUIRED for customization; never modify /usr/share/omarchy (read freely); edit ~/.config/; hyprctl reload plus configerrors validation; shell.json/menus hot-reload; command discovery via `omarchy commands` and `commands --json`; read source via cat $(which omarchy-<name>); hooks, plugins, reminders, debug flags.
- Default agent: opencode. Account list JSON: codex signed in (sol6.1xhigh@gmail.com, Free, 720h 1.0 percent, resets 2026-12-12); claude and grok not signed in; all manual, threshold 95.
- `omarchy commands --all` grep agent|mcp|skill: agent lines only, plus `omarchy install ai openclaw`. ZERO mcp lines. No MCP in stock.
- Usage commands crash over plain SSH: KeyError OMARCHY_PATH. menu select is a GUI picker with stdout result. plugin help: add/clone/disable/enable/list/remove/update/validate.
- Web (search 23:38): community MCP servers found. bruce-forte/omarchy-mcp-server (plugin, HTTP 127.0.0.1:8765/mcp, bearer token, supervised by omarchy-shell, permissions). hlsitechio Omarchy-MCP (stdio, Node/TS, 466 tools, 17 modules, verified state, agent_grid). Franzferdinan51 agent-room (rooms, MCP Mail, ACP). sergiudanstan omarchy-hardware (states: "Omarchy ships no serial support and no MCP servers").

## 23:38:41 probe 4: focus-app + capture sources + guides
- focus-app source: hyprctl clients -j plus jq match on class (regex, case-insensitive), fallback to initialTitle for org.omarchy.agent windows, most-recently-focused match, then hl.dsp.focus window address with focuswindow fallback.
- capture screenshot source: wrapper over omasnap with --notify. capture text source: hyprpicker freeze plus slurp region plus grim -g plus tesseract stdin stdout --oem 1 --psm 6 -l eng --dpi 300, wl-copy, notification.
- Skill grep mcp: ZERO matches. Skill dir: SKILL.md, capture.md, contributing.md, hooks.md, hyprland.md, plugins.md, theming.md.
- hyprland.md head: Lua config, o.bind/o.rebind, {launch}/{menu}/{panel} table forms (routes/panels go straight to the shell, no process per press), `omarchy menu keybindings --print`, hyprctl reload plus configerrors validation.
- hook help: `omarchy hook [name] [args...]`, install into ~/.config/omarchy/hooks/<type>.d/. omarchy-shell help: `omarchy-shell [-q] <target> <method> [args...]`, forwards IPC to the running shell.

## 23:39:12 probe 5: usage retry + hooks + plugins
- With OMARCHY_PATH=/usr/share/omarchy, `omarchy agent usage codex --limits-only` returns full JSON: Free tier, 720h 1.0 percent, resets 2026-12-12; today 18 prompts, 18 sessions, 190,927,021 tokens (all gpt-6-luna); total 1168 prompts, 403 sessions, 30 active days; recent days 15/11-21/11 messageCounts 143M/161M/173M/108M/271M/430M/190M; cache reads huge (gpt-6-luna 1.44B).
- ~/.local/state/omarchy/agents/usage/ has 20 JSON files (agy, claude, codex, cursor, deepseek, devin, fireworks, grok, grokbot, hermes, kimchi, kimi, local, minimax, muse, ollama, opencode, qwen, synthetic, vibe).
- Hooks dirs: battery-low.d, font-set.d, post-boot.d, post-update.d (install-voxtype.hook, reapply-indicator-patch.hook), pre-refresh-pacman.d, theme-set.d. All .sample except the two post-update hooks.
- `omarchy plugin list` without OMARCHY_PATH fails ("OMARCHY_PATH is not set").

## 23:39:41 probe 6: shell IPC + tesseract + indicator hook
- `omarchy-shell shell ping` and listPlugins fail without OMARCHY_PATH (same env gap).
- tesseract 5.5.4 installed (/usr/bin/tesseract), plus omasnap, slurp, grim. OCR pipeline usable headless with supplied geometry.
- reapply-indicator-patch.hook read: re-applies council Fix 2a indicator.py patch after Omarchy updates (patched copy at ~/.config/agent-computer-use/patches/indicator-patched-20261121.py, sudo-pass file, always exits 0, restarts the reader via pkill).
- `omarchy menu keybindings --print` over SSH prints only 2 lines (confirms KB). Default-agent file ~/.config/omarchy/default-agent does not exist. Agents plugin dir: Agent.qml, Main.qml, Panel.qml, README.md, collectors.py, manifest.json.

## 23:40:13 probe 7: shell IPC proven with OMARCHY_PATH
- With OMARCHY_PATH set: `omarchy-shell shell ping` returns ok. `omarchy-shell shell listPlugins` returns full JSON (60+ plugins), including james.agents (My Agents, enabled, cloned from omarchy.agents), james.menu (disabled), omarchy.agents (disabled), omarchy.indicators (enabled), omarchy.workspaces (enabled), crmne.todoist (enabled), omacal.upcoming (disabled), omarchy.reminders (enabled), omarchy.remote-session (enabled), omarchy.tailscale (disabled). No MCP plugin installed.
- `omarchy plugin list` works with OMARCHY_PATH. `omarchy agent usage muse --limits-only` returns all zeros (the Muse provider slot tracks Meta's Muse coding agent, not this agent).
- Verdict: IPC is the stock agent API. OMARCHY_PATH export is the one-line fix for SSH use.
