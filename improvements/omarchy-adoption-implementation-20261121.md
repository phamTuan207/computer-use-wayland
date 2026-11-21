# Omarchy adoption implementation (items 2-10)

Worker OI, Sat 2026-11-21 23:52-00:1x +07. Owner order 23:49: implement the
whole OA adoption list for ALL agents, via the shared repo. Sources: OA
findings improvements/omarchy-agentic-surfaces-20261121.md (commits
53a22e4 + 9db1587); KB keybind integration (commit 9e9b811); Omarchy skill
already in Muse's catalog (~/workspace/custom-skills/omarchy/, 23:42).
Log: improvements/worker-oi-omarchy-integrate-log.md.

## What was wired (all on todolist-push, all pushed, ls-remote verified)

### 2. focus_app in scripts/hypr_cmd.py (commit f08ba39)
- `focus_app_clients_argv()` = `["hyprctl", "clients", "-j"]`.
- `pick_focus_address(clients, pattern)`: mirrors omarchy-hyprland-focus-app
  exactly: regex match on class (case-insensitive), fallback to agent
  windows (initialClass org.omarchy.agent, match initialTitle),
  most-recently-focused wins (lowest focusHistoryID).
- `focus_window_argv(address)`: `hl.dsp.focus({ window = "address:..." })`.
- Deliberate divergence: the omarchy script falls back to
  `hyprctl dispatch focuswindow address:...`, but that string-dispatcher
  form is broken on Hyprland 0.57.2 Lua (KB proved rc=7). It is NOT
  emitted here; the hl.dsp form is the only focus path.
- Verified live on real clients -j (4 clients): pick zen =
  0x557052b62dd0, the known Zen address. No focus executed (read-only).

### 8. launch-or-focus in scripts/hypr_cmd.py (commit f08ba39)
- `pick_launch_or_focus_address(clients, pattern)`: whole-word match
  (case-insensitive) on class or title, first in clients order
  (omarchy takes head -n1, no focus-history sort). Pattern is treated
  as a plain app name (regex-escaped), not a regex.
- `launch_or_focus_cmd(pattern, launch_cmd=None)`: default
  `uwsm-app -- <pattern>`, as in the omarchy script. Caller runs it
  (via setsid) only when the pick returns None.

### 3. Usage JSON reader in scripts/omarchy_cmd.py (commit 8b969ac)
- `read_usage(agent, state_dir=None)` parses
  ~/.local/state/omarchy/agents/usage/<agent>.json (schemaVersion 1):
  today prompts/sessions/tokens, tokens by model, limits (label,
  percent, resets_at), totals, active days. Agent name validated
  (lowercase provider id); FileNotFoundError when absent, ValueError
  on bad name or malformed JSON.
- `usage_summary_text(summary)`: one watchdog log line.
- `usage_cli_argv(agent, limits_only=True)`: the CLI form.
- CLI: `python3 scripts/omarchy_cmd.py usage codex` prints the summary;
  `--argv` prints the CLI argv instead of reading.
- Verified live over SSH (stdin, no file copy to the laptop):
  `codex: today 18 prompts / 190,927,021 tokens; (gpt-6-luna
  190,927,021); 720h window 1.0% resets 2026-12-12; total 1168 prompts
  / 403 sessions / 30 active days`. Matches OA's live numbers exactly.
- Note: the "muse" slot tracks Meta's Muse coding agent, not this
  agent, and reads all zeros. Our usage is not tracked by Omarchy.

### 4. OMARCHY_PATH in SSH sessions (commit 7137b40)
- `cu.environment()` now sets OMARCHY_PATH=/usr/share/omarchy at all
  three returns, only when unset and the directory exists. Non-Omarchy
  machines are unaffected; an explicit value is never overridden.
  SESSION_KEYS untouched (no donor-contract change).
- The same helper lives in omarchy_cmd.py (`with_omarchy_path`) for
  other callers. Both resolve the default at call time (a definition-
  time default would defeat monkeypatching; caught by test, fixed).
- NOT done in this run: editing ~/workspace/ssh-laptop.sh (the VM-side
  helper). It is a live shared helper used by every worker mid-flight;
  a quoting mistake there would break all SSH calls. The repo-side fix
  covers cu.py-driven sessions. The one-line equivalent for direct
  ssh-laptop.sh use is to prefix the remote command with
  `export OMARCHY_PATH=/usr/share/omarchy;` (proven by OA's probes).
  Left for the owner to approve as a separate change.

### 5. omarchy-shell IPC wrapper (commit 8b969ac)
- `shell_argv(target, method, arg=None)`: allowlist only, shell
  ping/listPlugins (no arg) and shell toggle (one JSON-object arg).
  Unknown calls raise ValueError.
- `menu_argv(action, route=None)`: toggle/summon/close/refresh/ping,
  optional route (`system`, `appearance.theme`). This is the command
  form of the 22:45 menu-by-command rule.
- Verified live: `omarchy-shell shell ping` returns ok (OA 23:40,
  re-proven by the post-boot hook run below, shell=yes).

### 6. grim + tesseract OCR helper (commit 8b969ac)
- `grim_argv(geometry)`, `tesseract_argv()`, `ocr_shell(geometry)`:
  `grim -g '<geometry>' - | tesseract stdin stdout --oem 1 --psm 6
  -l eng --dpi 300 -c preserve_interword_spaces=1`. Geometry is
  validated (`X,Y WxH`, ranges checked) and supplied by the caller
  (DOM rect or known window box), never picked with slurp.
  tesseract 5.5.4 and grim both present on the laptop (verified).

### 7. notification send (commit 8b969ac)
- `notify_argv(headline, description=None, urgency="normal",
  app_name=None, action=None, exec_cmd=None)`: --action (label,
  program, args) or --exec (program, args), never both; urgency
  low/normal/critical. For user-facing fleet alerts with an action
  button. NOT sent live in this run (no alert was due; sending a
  test notification to the owner's desktop uninvited would be noise).

### 9. omasnap screenshot fallback (commit 8b969ac)
- `screenshot_argv(mode="fullscreen", dest="save")`: only
  smart/fullscreen are CLI-safe. region/windows/scroll need a GUI
  pick and are rejected (use computer-use observe instead).
  omasnap exists at /usr/bin/omasnap (verified).

### 10. Hooks for fleet maintenance (commit c6c5282)
- Repo copy: scripts/hooks/post-boot-health-check.hook.
- Installed on the laptop:
  ~/.config/omarchy/hooks/post-boot.d/post-boot-health-check.hook
  (scp + chmod +x, verified: bash -n SYNTAX-OK).
- Check-only: logs one line per boot to
  ~/.cache/agent-computer-use/post-boot-health.log
  (hyprland/zen/relay/shell yes/no). Never restarts, kills, or
  changes anything; always exits 0, mirroring the post-update
  reapply-indicator-patch.hook pattern.
- Dry run 23:58: exit 0, log line `2026-11-21 23:58:27 +0700 boot
  health: hyprland=yes zen=yes relay=yes shell=yes`. Relay matched
  as `session_remote.py serve` (PID 1821, verified live); the first
  draft's guessed pattern (`computer-use.*relay`) was wrong and was
  fixed before install. The hook exports the GUI env first (hyprctl
  fails without HYPRLAND_INSTANCE_SIGNATURE; proven live).
- post-boot.d previously held only weather.sample.

## Tests

- New: tests/test_omarchy_cmd.py (26 tests), extended
  tests/test_hypr_cmd.py (focus_app + launch-or-focus, 11 tests), 3 new
  tests in tests/test_environment_host.py (OMARCHY_PATH added/absent/
  preserved).
- Focused runs: 50/50 (hypr + omarchy), then 75/75 (with env tests).
- Two test bugs of mine found and fixed (not code bugs): None means
  "no route" / "default launch" by design; summary-text separator.
  One real bug found by test: default args bind at definition time,
  so monkeypatching the constant had no effect; helpers now resolve
  the default at call time.
- Full suite (unittest discover, 1657 tests): PENDING, see below.

## Suite comparison (baseline vs with OI changes)

- Baseline worktree /tmp/oi-baseline at 0cc8e27 (parent of OI commits):
  Ran 1594 tests in 260.8s, FAILED (failures=3, errors=68, skipped=17).
- Mine worktree /tmp/oi-mine at c6c5282 (OI HEAD): Ran 1634 tests in
  262.7s, FAILED (failures=3, errors=68, skipped=17).
- Failing-test name lists are IDENTICAL (diff empty, 71 lines each).
  The 71 pre-existing failures include the tc02 typed-text checks
  (tesseract unavailable on the VM) and other environment-dependent
  tests; they fail on the clean baseline too.
- Delta is +40 tests, exactly the new OI tests (26 omarchy + 11 hypr
  + 3 env), all passing. ZERO regressions from OI changes.
- (The earlier shared-checkout run showed 1657 tests / 1 failure /
  2 errors because that tree held other workers' uncommitted changes;
  the clean worktrees are the rigorous comparison. Worktrees removed
  after the comparison.)

## Explicitly NOT implemented (OA section 6, owner-excluded)

- `omarchy agent prompt` (wrong default agent opencode, auto-approve).
- Community MCP servers (bruce-forte, hlsitechio, agent-room): third
  party, need security review + install decision first.
- OpenClaw install, account exec/use switching, refresh/update/restart
  without owner confirmation.

## Per-machine setup for agents on other machines

Omarchy's files are stock upstream docs; never vendor them into the
repo and never modify /usr/share/omarchy (overwritten on update).
- Skill: /usr/share/omarchy/default/agents/skills/omarchy/SKILL.md
  (276 lines) + hyprland.md, plugins.md, theming.md, hooks.md,
  capture.md, contributing.md. Sibling skills: diagnose-crash,
  omarchy-app. On Claude Code / Codex the skill is linked at
  ~/.claude/skills/omarchy and ~/.codex/skills/omarchy. For Muse,
  copy the directory into ~/workspace/custom-skills/omarchy/ (done
  23:42, scp from the laptop).
- SSH sessions: export OMARCHY_PATH=/usr/share/omarchy, plus the GUI
  env (XDG_RUNTIME_DIR=/run/user/1000, WAYLAND_DISPLAY=wayland-1,
  DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus,
  HYPRLAND_INSTANCE_SIGNATURE from ls /run/user/1000/hypr/).
- Usage JSON: ~/.local/state/omarchy/agents/usage/<agent>.json,
  readable directly without the CLI.
- Hooks: ~/.config/omarchy/hooks/<type>.d/ (post-boot.d,
  post-update.d, theme-set.d, battery-low.d, ...). Hook files must
  always exit 0. Install the repo copy with scp + chmod +x.
- No machine data in the repo copy of anything above (stock docs,
  generic builders, no personal info).

## Commits (todolist-push, ls-remote verified)

- 8b969ac OI: omarchy_cmd.py pure builders + usage reader, 31 tests
  (message overcounts: the file holds 26 tests; see Tests section)
- f08ba39 OI: hypr_cmd focus_app + launch-or-focus
- 7137b40 OI: cu.environment() sets OMARCHY_PATH, 3 env tests
- c6c5282 OI: post-boot health check hook (check-only)
- (report + log commit: fill in)
