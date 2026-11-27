# Omarchy agentic surfaces: what is built in, what computer-use can use

Worker OA, Sat 2026-11-21 23:37-23:41 +07. Machine: user laptop, Omarchy 4.0.0.alpha. Method: read-only probes over SSH (help text, --help, JSON output, source reads) plus docs crawl (official manual AI page, GitHub, Glama). Nothing installed, no setting changed, no window or tab touched.

## 0. Verdict

Omarchy is NOT an agent runtime. It is an opinionated Hyprland setup with agent-friendly CLI surfaces plus a skill. There is no built-in agent that acts on its own, no OS-level agent daemon, and no MCP server in stock. The "agentic OS" label covers: pre-wired agent CLI launchers, a default-agent picker, an auto-approve prompt launcher, usage tracking, a crash-to-agent handoff, the omarchy skill, hooks and plugins, and plain-text configs an agent can read. All of that helps agents that run ON the machine. None of it lets an external agent (Muse on the VM) drive the desktop: that still needs SSH plus Hyprland IPC plus computer-use. The community MCP servers below fill exactly that gap, but they are third-party, not installed here, and need a security review before adoption.

Evidence for "no MCP in stock": `omarchy commands --all` has zero lines matching mcp; zero matches for "mcp" in /usr/share/omarchy/default/agents/skills/; the omarchy-hardware README states "Omarchy ships no serial support and no MCP servers". Community MCP servers found by crawl: bruce-forte/omarchy-mcp-server (Omarchy plugin, HTTP MCP on 127.0.0.1:8765/mcp, bearer token, every omarchy command plus shell IPC, permission tiers, supervised by omarchy-shell), hlsitechio/Omarchy-MCP (stdio MCP, Node/TypeScript, 466 tools across 17 modules, verified desktop-state confirmation, agent_grid multi-agent workspaces), Franzferdinan51/omarchy-agent-room (multi-agent rooms with shared MCP Mail over stdio, ACP seats, Quickshell console).

## 1. The Omarchy skill exists on the laptop (not in Muse's catalog)

This answers the owner's 23:22 question precisely. `muse.skill_search 'omarchy'` returns 0 matches and there is nothing in ~/workspace/custom-skills/ or /opt/muse/skills/. But the skill DOES exist on the machine:

/usr/share/omarchy/default/agents/skills/omarchy/SKILL.md (276 lines)
- Guides next to it: hyprland.md, plugins.md, theming.md, hooks.md, capture.md, contributing.md
- /usr/share/omarchy/default/agents/skills/diagnose-crash/SKILL.md (128 lines)
/usr/share/omarchy/default/agents/skills/omarchy-app/SKILL.md (181 lines, build Qt Quick desktop apps with an agent)
~/.claude/skills/omarchy, diagnose-crash, omarchy-app, omacal, computer-use (symlinked/installed for Claude Code)
~/.codex/skills/ (many, including chromium-cdp, claude-handoff, chief-of-staff)

So KB and my catalog search were right in letter (no skill in Muse's catalog) and the owner was right in substance (the skill exists on the user's machine). The gap is that Muse never had it in its catalog. Adoption item 1 below closes it.

What the skill says (read in full): REQUIRED for end-user customization; NEVER modify /usr/share/omarchy/ (read freely, it is overwritten on update); edit in ~/.config/; Hyprland auto-reloads on save, validate with `hyprctl reload` plus `hyprctl configerrors`; shell.json and menus hot-reload; command discovery via `omarchy commands` and `omarchy commands --json`; read any command's source with `cat $(which omarchy-<name>)`; hooks via `omarchy hook install <type> <file>`; plugins via `omarchy plugin clone`; reminders via `omarchy reminder <minutes> [message]`; debug always with `omarchy debug --no-sudo --print`.

## 2. Surface inventory

Usable-now means callable from SSH by an agent with no GUI interaction. Value is for our computer-use work (workspace/window control, app launching, screenshots, input, system state).

| Surface | What it does | Exact form | Usable now? | Value | Notes |
|---|---|---|---|---|---|
| agent prompt | Launch default agent with a prompt, unattended auto-approve | `omarchy agent prompt [--inline] <prompt...>` | Yes | Med | Goes to the DEFAULT agent, which here is opencode, not Codex/Luna. Auto-approve risk. Do not use for fleet work. |
| agent (launch) | Launch default agent in a terminal | `omarchy agent [--inline] [--pick]` | Yes | Low | Same default-agent caveat. |
| agent crash | Hand a crashed PID to the default agent with diagnose-crash skill | `omarchy agent crash <pid> [comm] [exe] [signal]` | Yes | Med | Crash watch is on by default; notification offers the handoff. Also manual by PID from coredumpctl. |
| agent usage | Per-agent usage as JSON (limits, today tokens, per-model) | `omarchy agent usage <agent> [--force] [--limits-only]` (25 providers: codex, claude, agy, copilot, cursor, deepseek, grok, kimi, muse, ollama, opencode, qwen, vibe, zai, ...) | Yes, with OMARCHY_PATH set | High | Live numbers below. Usage files also directly readable at ~/.local/state/omarchy/agents/usage/*.json (20 files). |
| agent account | Subscription accounts for claude/codex/grok | `omarchy agent account list [--json]`, `use`, `mode`, `exec <provider> [args]`, `add`, `copy`, `remove`, `rename`, `transfer` | Yes | Med | Account switching has billing/limit side effects. `exec` runs a CLI as the selected account. |
| default agent | Get/set the default agent (24 names) | `omarchy default agent [name]` | Yes | Low | Current: opencode. Changing it is the user's choice, not ours. |
| hyprland focus app | Focus a window by app identity (class regex, falls back to agent-window title, most-recently-focused match) | `omarchy hyprland focus app <app-name>` | Yes | High | Source uses hyprctl clients -j plus jq, then `hl.dsp.focus({ window = "address:..." })` with a focuswindow fallback. The exact pattern computer-use needs for focusing Zen without coordinates. |
| hyprland window/monitor/toggle | Window ops, monitor ops, permanent flags | `omarchy hyprland window close all/minimize/pop/transparency/width`, `monitor focused/laptop/scaling/internal`, `toggle <flag>`, `workspace layout current/default/toggle` | Yes | Med | No workspace focus/goto command in this group, which is why KB found no CLI for it. `window close all` is destructive, never use blindly. |
| menu | Control the Omarchy menu | `omarchy menu [toggle|summon|close|refresh|ping] [route]`, e.g. `omarchy menu toggle system`, `omarchy menu summon appearance.theme` | Yes | High | This is the command form of the 22:45 owner rule (menu by command). Routes go to the running shell. |
| menu select/input/file | Scriptable pickers | `omarchy menu select <prompt> [options...] [-- --multiple --selected <v> ...]`, `omarchy menu input <prompt>`, `omarchy menu file <label> <paths> <formats>` | GUI only | Med | Opens a GUI menu; the choice comes back on stdout. Usable while the owner is away, not headless. |
| menu keybindings | Show Hyprland keybindings in an interactive menu | `omarchy menu keybindings`, `omarchy menu keybindings --print` | Partial | Low | --print over SSH prints only 2 lines (verified twice). The Lua files are ground truth. |
| capture screenshot | Screenshot via omasnap | `omarchy capture screenshot [smart|region|windows|fullscreen|scroll] [copy|save]` (alias `omarchy screenshot`) | Partial | Med | Thin wrapper over omasnap with --notify. Region/windows/scroll need a GUI pick; fullscreen/smart are CLI-safe. Our grim path already works; this is a fallback. |
| capture text | OCR text from a screenshot region | `omarchy capture text` | GUI only, pipeline reusable | Med | Needs slurp region pick by mouse. But the pipeline is `grim -g <geometry> - | tesseract stdin stdout --oem 1 --psm 6 -l eng --dpi 300`, and tesseract 5.5.4 IS installed. Headless OCR with supplied geometry is a real text-reading fallback. |
| capture qr / screenrecording | Decode QR from a region; screen recording | `omarchy capture qr`, `omarchy capture screenrecording [--fullscreen] [--stop-recording] [--status]` | Partial | Low | QR needs a region pick. Recording start/stop/status are CLI-safe. |
| launch | App launchers | `omarchy launch browser [url]`, `omarchy launch or focus <pattern> <cmd>`, `omarchy launch or focus tui/webapp`, `omarchy launch terminal [cmd]`, `omarchy launch tui`, `omarchy launch webapp <url>`, `omarchy launch editor`, `omarchy launch openclaw` | Yes | High | `launch or focus` is launch-or-focus by pattern without coordinates. `launch browser` uses xdg-settings default. |
| notification send | Desktop notification, with clickable actions that run programs | `omarchy notification send [--app-name] [-g glyph] [-u low|normal|critical] [-i icon] [-t ms] [-r id] <headline> [description] [--exec <prog> [args] | --action <label> <prog> ...]` | Yes | High | Agent-to-user alerts with action buttons. Also `notification dismiss <summary>`, `notification time/weather/battery`. |
| omarchy-shell IPC | IPC calls into the running Quickshell shell | `omarchy-shell [-q] <target> <method> [args...]`, e.g. `omarchy-shell shell ping`, `omarchy-shell shell listPlugins`, `omarchy-shell shell toggle omarchy.menu '{"menu":"root"}'` | Yes, with OMARCHY_PATH set | High | PROVEN live 23:40: ping returns ok, listPlugins returns full plugin JSON. Closest thing to an agent API in stock Omarchy. |
| reminder | Desktop notification reminders | `omarchy reminder <minutes> [message]`, `omarchy reminder show/clear` | Yes | Low | Built-in timed nudges. Our crons already cover reminders. |
| debug | Diagnostics | `omarchy debug [--no-sudo] [--print]`, `omarchy debug idle [log-lines]` | Yes | Med | Always use --no-sudo --print over SSH to avoid interactive sudo hangs. |
| monitor state | Monitor panel state for the shell | `omarchy monitor state` | Yes | Low | Read-only state. |
| crash mute | Silence crash notifications per program | `omarchy crash mute [program] [on|off|toggle]` | Yes | Low | Fleet already watches coredumps via watchdog. |
| hook | Event automation hooks | `omarchy hook [name] [args...]`, `omarchy hook install <type> <file>` into ~/.config/omarchy/hooks/<type>.d/ | Yes | Med | Hook dirs present: battery-low.d, font-set.d, post-boot.d, post-update.d, pre-refresh-pacman.d, theme-set.d. A post-update hook already re-applies the council Fix 2a indicator.py patch after Omarchy updates (pattern to reuse). |
| plugin | Shell plugins (bar widgets, overlays, panels) | `omarchy plugin add <git-url> [--enable]`, `clone <source-id>`, `list [--json]`, `enable/disable/remove/update/validate` | Yes, with OMARCHY_PATH set | Med | 60+ plugins listed live. `user.agents` (My Agents, cloned from omarchy.agents) and `user.menu` are user clones. No MCP plugin installed. |
| install ai openclaw | Install the OpenClaw agent platform plus Control UI | `omarchy install ai openclaw` | Install, not probe | Low | Out of scope for this read-only task. OpenClaw is a multi-agent harness; needs a separate decision. |
| commands | Machine-readable command registry | `omarchy commands`, `omarchy commands --all`, `omarchy commands --json`, `omarchy commands --check` | Yes | Med | Self-documenting CLI; the skill's recommended discovery path. |
| theme/bar/toggle/restart/refresh | Theme, bar layout, feature toggles, restarts, config reset | `omarchy theme set <name>`, `omarchy bar move ...`, `omarchy toggle <flag>`, `omarchy restart shell/terminal/hyprsunset`, `omarchy refresh <app>` | Yes | Low | Refresh backs up first but resets config; never run without owner confirmation. |

## 3. Environment gotcha: OMARCHY_PATH

Several commands crash over plain SSH with `KeyError: 'OMARCHY_PATH'` (agent usage) or print `OMARCHY_PATH is not set` (plugin list, omarchy-shell). The variable is set by the desktop session only. Fix: export OMARCHY_PATH=/usr/share/omarchy in SSH sessions. Proven live: with it set, `omarchy agent usage codex` returns full JSON, `omarchy-shell shell ping` returns ok, `omarchy plugin list` works. The usage JSON files are also directly readable without the CLI.

## 4. What is broken, missing, or GUI-only

- No workspace focus/goto command in `omarchy hyprland` (the CLI never had one). KB's gap was real. The working form stays `hl.dsp.focus({ workspace = N })` via hyprctl (proven 23:19), now wrapped in scripts/hypr_cmd.py.
- `omarchy menu keybindings --print` prints only 2 lines over SSH (verified twice). Use the Lua files.
- `omarchy menu select/input/file` and `omarchy capture text/qr` need a GUI pick (slurp/mouse). Only their pipelines or stdout results are agent-usable.
- `omarchy agent prompt` dispatches to the default agent (opencode here), not Codex/Luna, and runs auto-approve. Not a fleet launcher.
- `omarchy agent usage muse` returns all zeros: the "Muse" provider slot tracks Meta's Muse coding agent, not this agent. Our usage is not tracked by Omarchy.
- `omarchy commands --json` exists per the skill; its exact top-level shape was not fully parsed here (one probe printed a count of 2 top-level keys, inconclusive, not relied on).
- Default agent file ~/.config/omarchy/default-agent does not exist; the default is stored elsewhere (shell state). `omarchy default agent` with no arg prints the current default (opencode).

## 5. Adoption list (ranked)

1. Import the omarchy skill into Muse's catalog. Copy /usr/share/omarchy/default/agents/skills/omarchy/ (SKILL.md plus hyprland.md, plugins.md, theming.md, hooks.md, capture.md, contributing.md) into ~/workspace/custom-skills/omarchy/ with an upstream-path note. Closes the exact gap the owner hit: every Muse then has command discovery, Hyprland validation rules, hooks, and capture guides. No machine data in the copy (it is stock upstream docs).
2. Adopt `omarchy hyprland focus app` for window focus by class/title. Add focus_app to scripts/hypr_cmd.py using its exact pattern (hyprctl clients -j plus jq match on class, fallback to agent-window initialTitle, most-recently-focused, then hl.dsp.focus window address with focuswindow fallback). Replaces coordinate clicks for focusing Zen and agent terminals.
3. Read agent usage JSON for fleet token/limit tracking. Either `OMARCHY_PATH=/usr/share/omarchy omarchy agent usage codex --limits-only` or read ~/.local/state/omarchy/agents/usage/codex.json directly. Add a small usage reader (scripts/ or watchdog) that logs the 720h window percent and today tokens per agent. The coordinator can then see Codex/Luna burn without parsing logs.
4. Export OMARCHY_PATH=/usr/share/omarchy in SSH sessions (ssh-laptop.sh env and cu.py environment()). Unblocks usage, plugin, and shell IPC commands from SSH. One-line change, no behavior change on the desktop.
5. Use `omarchy-shell` IPC for shell health and menu/panel control by command (`shell ping` health check, `shell listPlugins`, `shell toggle <route>`). Add a thin wrapper (scripts/hypr_cmd.py or a new scripts/omarchy_cmd.py) once item 4 lands. This is the stock command route for the 22:45 menu-by-command rule.
6. Adopt the grim plus tesseract OCR pipeline as a headless text-reading fallback: `grim -g <geometry> - | tesseract stdin stdout --oem 1 --psm 6 -l eng --dpi 300 -c preserve_interword_spaces=1`. tesseract 5.5.4 is installed. Use when vision is uncertain and a DOM read is unavailable. New small helper in scripts/, geometry supplied by the caller, never a slurp pick.
7. Use `omarchy notification send` (with --action) for user-facing fleet alerts (blocker needs the owner, live run done, approval needed). The watchdog and worker completion paths can post a notification with an action button instead of relying only on chat.
8. Use `omarchy launch or focus <pattern> <cmd>` for launch-or-focus of apps by pattern (Zen, terminal) without coordinates. Add to scripts/hypr_cmd.py next to focus_app.
9. Use `omarchy capture screenshot [smart|fullscreen] [save]` (omasnap) as a fallback screenshot path if the grim path ever fails. Lower priority; computer-use already has grim.
10. Install hooks for fleet maintenance, reusing the existing pattern. The post-update hook reapply-indicator-patch.hook already re-applies the council Fix 2a indicator.py patch after Omarchy updates (reads the patched copy from ~/.config/agent-computer-use/patches/, uses the sudo-pass file, always exits 0). A post-boot hook could verify relay/computer-use health. Hooks live in ~/.config/omarchy/hooks/ (local-only). Needs owner awareness since hooks run automatically.

## 6. Explicitly NOT adopted now

- `omarchy agent prompt`: wrong default agent (opencode, not Luna) plus auto-approve. The fleet already launches Codex directly.
- Community MCP servers (bruce-forte omarchy-mcp-server, hlsitechio Omarchy-MCP, Franzferdinan51 agent-room): they would give an MCP client full desktop control (every omarchy command plus shell IPC). Promising, but third-party, needs a security review, an install decision, and a permissions policy first. Do not install on this task.
- `omarchy install ai openclaw`: installing a second multi-agent harness while the fleet already runs is a separate decision.
- `omarchy agent account exec/use/mode` switching: touches subscription accounts and billing/limits. Only on explicit owner order.
- `omarchy refresh` / `omarchy update` / `omarchy restart shell`: reset or restart user config/services. Never without owner confirmation.

## 7. Live numbers (23:38-23:40 +07)

- Default agent: opencode. Codex account: [email redacted], Free plan, signed in, 720h window 1.0 percent used, resets 2026-12-12T12:17:17Z. Claude and Grok accounts: not signed in. All switch modes manual, threshold 95.
- Codex usage today (21/11): 18 prompts, 18 sessions, 190,927,021 tokens, all gpt-6-luna. Total: 1168 prompts, 403 sessions, 30 active days. Recent days (messageCount, reads as tokens): 15/11 143,943,986; 16/11 161,709,396; 17/11 173,404,828; 18/11 108,771,107; 19/11 271,955,516; 20/11 430,589,581; 21/11 190,927,021. Model cache reads are huge (gpt-6-luna cacheReadInputTokens 1,448,384,768).
- Shell plugins live: 60+ listed, including user.agents (My Agents, enabled, cloned from omarchy.agents), user.menu (disabled), omarchy.indicators (enabled), omarchy.workspaces (enabled), crmne.todoist (enabled), omarchy.reminders (enabled), omarchy.remote-session (enabled), omarchy.tailscale (disabled). No MCP plugin installed.

## Sources

- On-disk: /usr/share/omarchy/default/agents/skills/omarchy/SKILL.md (276 lines, read in full), hyprland.md (head 80 lines), diagnose-crash and omarchy-app skill paths; `omarchy --help`, `omarchy agent/hyprland/menu/capture/launch/cmd/notification/crash/debug/monitor/plugin --help`; `omarchy commands --all`; sources of omarchy-hyprland-focus-app, omarchy-capture-screenshot, omarchy-capture-text; `omarchy-shell shell ping/listPlugins` (proven with OMARCHY_PATH); `omarchy agent usage codex/muse --limits-only`; `omarchy agent account list --json`; `omarchy plugin list`; ~/.local/state/omarchy/agents/usage/ (20 JSON files).
- Web (crawled 21/11): Omarchy manual AI page (https://announce-brian-cartmell-and-american-cloud-omarchy.dhh-220.workers.dev/manual/ai/); Glama omarchy-mcp-server page (https://glama.ai/mcp/servers/bruce-forte/omarchy-mcp-server); hlsitechio Omarchy-MCP README (https://github.com/hlsitechio/omarchy-mcp/blob/HEAD/README.md); Franzferdinan51 agent-room README; omarchy-hardware README (states stock Omarchy ships no MCP servers); Next Token wiki Omarchy page; Frank Jung first-look article; Jimmy Song landscape page; Digital Yeast article.
