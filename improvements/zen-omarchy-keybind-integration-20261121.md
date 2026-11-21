# Zen + Omarchy keybind integration into computer-use — report

Worker KB, Sat 2026-11-21 23:22-23:45 +07. Owner order 23:22: find ALL keybinds, integrate into computer-use.
(The clone2-watch run fumbled the workspace command ~4 min; the owner asked why, since "the Omarchy skill has it all".)

## Verdict

1. **There is NO Omarchy skill.** `muse.skill_search 'omarchy'` = 0 matches; no Omarchy/Hyprland skill in
   `~/workspace/custom-skills/` (24 skills) or `/opt/muse/skills/`. The keybinds never lived in a skill.
   They live in config files on the laptop. That is the whole answer to the owner's question.
2. **The knowledge existed locally but was not where the watch run looked.** The machine layer already had
   `~/.config/agent-computer-use/machine/fastest-paths.md` (with the correct signature discovery
   `ls /run/user/1000/hypr/`), but its workspace row recommended the BROKEN string dispatcher
   `hyprctl dispatch workspace <N>`, and 5 more rows had broken string forms. The watch run used a
   different wrong form (`hl.dsp.workspace.goto`, `goto` is a Lua reserved word).
3. **Integrated now (laptop-local only):** full keybind map in the machine layer + broken fastest-path rows
   fixed + a generic repo command-builder module with tests.

## What was integrated (counts verified)

- Omarchy/Hyprland effective bindings: **250** (defaults 249 active after dropping 1 JIS-only bind;
  10 default chords unbound by user; 11 new user chords; 7 default chords rebound to new actions).
  Table rows in the map: 179 (ranges unexpanded, e.g. SUPER+1..10 = 10 bindings).
- Zen effective bindings: **85 actions** (docs table rows incl. Ctrl+Tab next/prev; 3 overridden by
  customKeys.json: New Tab Ctrl+N, New Window Ctrl+T, Open Add-ons Ctrl+Shift+A; workspace-switch 1-10 cleared).
- Unbound/dead chords: **8** (7 Hyprland + Zen workspace-switch).
- Sources: /usr/share/omarchy/default/hypr/bindings/*.lua (8 files, 468 lines) + user
  ~/.config/hypr/bindings.lua (186 lines) + Zen docs (crawled 21/11 16:05 UTC) + customKeys.json (ZK probe).

## Files

Laptop only (NEVER in any repo):
- `~/.config/agent-computer-use/machine/keybinds.md` (31,581 B) — full map with command forms.
- `~/.config/agent-computer-use/machine/keybinds.json` (48,514 B) — structured mirror (179 omarchy rows,
  85 zen rows, 8 unbound); generated from the md by `~/workspace/kb-gen-keybinds.py` (VM staging script).
- `~/.config/agent-computer-use/machine/fastest-paths.md` — 6 broken string-dispatcher rows fixed + Keybind map note appended.

Repo (generic, no machine data; todolist-push):
- `scripts/hypr_cmd.py` — pure command builders: focus_workspace(n), focus_next/prev/former_workspace,
  focus_direction(d), close_window, dispatch_argv (rejects non-hl.dsp and workspace.goto), desktop_env
  (signature discovery, fails closed). No desktop access.
- `tests/test_hypr_cmd.py` — 13 tests, 13/13 OK on the VM.

## Verification (live)

- Workspace switch by command: proven live 23:19-23:20 by the parent (ws1 to ws2 and back, ~1s each,
  `hl.dsp.focus({ workspace = N })` with signature from `ls /run/user/1000/hypr/`).
- String dispatcher PROVEN broken live 23:32 by KB: `hyprctl dispatch workspace 1` →
  `error: 3 [string "return hl.dispatch(workspace 1)"]:1: ')' expected near '1'` + note
  "dispatch in lua is a shorthand for hl.dispatch(...)". RC=7. No visible change (failed before switching).
  This single error explains the watch run's fumble and invalidates every string-dispatcher row.
- JSON parses on the laptop (`python3 -c json.load`, counts match). Map files present with sizes above.
- `hyprctl clients -j` read-only check OK (4 windows listed). No window, tab, or setting was changed.
- Repo tests: `python3 -m unittest tests.test_hypr_cmd` 13/13 OK.

## What could NOT be wired (honest gaps)

- Move window to workspace N: the hl.dsp equivalent of `o.workspaces.move_window(N)` (monitor-aware,
  monitor-workspaces.lua) was not verified live; recorded as keypress-only in the map. One live test
  with a scratch window (owner away) would settle it.
- Absolute resize (`resizeactive exact W H`, 901x1176 "proven" in fastest-paths.md): the string form is
  broken like the rest; no hl.dsp absolute-resize form was established from the sources. Recorded as
  keypress/drag only; needs a probe.
- `{omarchy=...}`, `{panel=...}`, `{ipc=...}`, `{menu=...}` table forms and most webapp/TUI binds have no
  established CLI equivalent: recorded as keypress-only rather than invented.
- Zen shortcuts have no CLI: they are keypresses inside Zen. Agents must prefer Marionette/BiDi (DOM)
  for tab operations, never bare keypresses at the session.
- `omarchy menu keybindings --print` printed only 2 lines via SSH (exit 0); the Lua files are ground truth.
- JIS bind (Ctrl+Shift+semicolon zoom) is INACTIVE: layout is not jp. Dictation binds are conditional on
  the dictation backend being installed.
- The repo module is builders only: it does not change cu.py or any runner. Wiring `hypr_cmd` into
  runners/cron bodies is a follow-up (the clone2-watch body already uses the proven string).

## Follow-ups

1. Live-test the move-window and absolute-resize hl.dsp forms once, on a scratch window, owner away.
2. Wire `scripts/hypr_cmd.py` into cu.py runners and any cron body that switches workspaces.
3. Regenerate keybinds.md/json after Omarchy package updates (see map section E).
4. Consider a real Omarchy skill in the catalog (the owner assumed one existed): the map files are the
   content; a skill would just package them. Owner decision, not taken here.
