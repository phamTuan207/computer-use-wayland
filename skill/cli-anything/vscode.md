---
name: "cli-anything-vscode"
description: >-
  Repo-owned agent wrapper for VS Code: open files and folders, jump to a
  line, compare files, list extensions, list workspaces and open tabs from
  persisted state, and read saved files, without screenshots.
---

<!-- Repo-owned skill, NOT vendored upstream. -->
<!-- There is no upstream CLI-Anything harness for VS Code. -->
<!-- Wrapper: scripts/vscode_cli.py (stdlib only), run via -->
<!-- `computer-use cli run vscode -- <command>`. -->
<!-- Skill version: 1.0.0. Wrapper: scripts/vscode_cli.py. -->
<!-- Verified on the laptop 2026-11-18: VS Code 1.146.0, `code` CLI -->
<!-- (visual-studio-code-bin 1.146.0-1). Open-tab reads verified -->
<!-- across all 10 workspaceStorage dirs; unsaved buffer text is -->
<!-- NOT verified readable (see Limits). -->

# cli-anything-vscode

A repo-owned command-line wrapper for VS Code, for AI agents that need
to drive the editor without screenshots. The `code` CLI covers opening
and diagnostics; this wrapper adds the read side the CLI does not
document (workspaces, open tabs, saved-file reads) by parsing VS Code's
own persisted workspace state, read-only.

## Installation

No package to install. The wrapper ships in this repo at
`scripts/vscode_cli.py` and is reached through the `computer-use` CLI:

```bash
computer-use cli run vscode -- <command>
```

**Prerequisites:**
- VS Code installed and its `code` command available in `PATH`
  (laptop: `visual-studio-code-bin 1.146.0-1`, `code` 1.146.0).
- Open-tab reads need `~/.config/Code/User/workspaceStorage/` to exist;
  they work even when no VS Code instance is running, because they read
  persisted state, not a live process.
- Opening a window needs the desktop session env (`WAYLAND_DISPLAY`,
  `XDG_SESSION_TYPE=wayland`, `HYPRLAND_INSTANCE_SIGNATURE`,
  `ELECTRON_OZONE_PLATFORM_HINT=wayland`). From a bare shell the
  wrapper discovers it from a GUI donor process (kitty, quickshell,
  waybar, Hyprland via `/proc` environ); without it `code` exits 0
  while the app dies on an Electron X11 error, so `open` and `diff`
  verify afterwards that a `code` process is running and report
  `process_running: false` instead of a bare ok when the launch did
  not stick. Always check that field after an open.

## Usage

### Basic Commands

```bash
# Show help
computer-use cli run vscode -- --help

# List known workspaces
computer-use cli run vscode -- workspaces

# List open tabs in every known workspace
computer-use cli run vscode -- tabs

# Read a saved file (bounded)
computer-use cli run vscode -- read ~/Work/iac-eval/README.md

# List extensions with versions
computer-use cli run vscode -- extensions
```

Or run the wrapper directly from the repo checkout:

```bash
python3 scripts/vscode_cli.py tabs --workspace ~/Work/iac-eval
```

## Command Groups

### Workspaces

Workspace discovery commands.

| Command | Description |
|---------|-------------|
| `workspaces` | List known workspaces from workspaceStorage (folder or workspace path per entry) |
| `tabs [--workspace PATH] [--all]` | List open tabs per workspace, from persisted editor state; default is all workspaces |
| `backups` | List VS Code backup files (metadata only, never parsed) |

### Files

Saved-file commands. These read the file on disk, not the editor.

| Command | Description |
|---------|-------------|
| `read <file> [--max-chars N]` | Read a saved file (default cap 20000 chars, hard cap 1 MiB) |
| `files <folder> [--max N]` | List files under a folder (default cap 200; skips .git, node_modules, __pycache__) |

### Open

Opening commands. All pass through to `code` with argv only.

| Command | Description |
|---------|-------------|
| `open <path> [--new-window\|--reuse-window] [--goto LINE[:COL]]` | Open an existing file or folder; refuses a nonexistent path because `code` would create a missing file; reports `process_running` so a launch that died silently is visible |
| `diff <left-file> <right-file>` | Open a two-file diff; both files must exist |

### Extensions

Extension inventory commands.

| Command | Description |
|---------|-------------|
| `extensions` | List installed extensions with versions (`code --list-extensions --show-versions`) |

### Diagnostics

| Command | Description |
|---------|-------------|
| `status` | `code --status` diagnostics; empty output when VS Code is not running, or when the call cannot reach the instance (missing session env); `running` means diagnostics were reachable, not that a process exists |
| `version` | `code --version`, first line only |

## Examples

### Open a file at a line

```bash
computer-use cli run vscode -- open ~/Work/iac-eval/evaluation/metrics.py --goto 42
```

### Open a scratch workspace in a new window

```bash
computer-use cli run vscode -- open /tmp/vscode-live-test --new-window
```

### Find what is open in one workspace

```bash
computer-use cli run vscode -- tabs --workspace ~/Work/iac-eval
```

### Compare two files

```bash
computer-use cli run vscode -- diff /tmp/vscode-live-test/a.txt /tmp/vscode-live-test/b.txt
```

## State Management

- Open tabs come from `~/.config/Code/User/workspaceStorage/<hash>/state.vscdb`,
  key `memento/workbench.parts.editor`. The wrapper copies the DB to a
  temp file first and opens the copy read-only, so a running VS Code
  (whose live DB is locked) is never touched. The persisted state is
  written when VS Code saves state, so a tab opened seconds ago may not
  appear until VS Code flushes it; treat the list as last-persisted,
  not live.
- `tabs` reports one group per editor group, with the most-recently-used
  editor as `active`. Editors that are not plain files (untitled buffers,
  agent-session views) are reported with an `untitled:` label or their
  editor id, not a filesystem path.
- `read` and `files` read the filesystem directly. A file that is open
  with unsaved changes reads as its last SAVED content; the unsaved
  delta is not visible to this wrapper.
- `open` never creates a file: a nonexistent path is refused. Use the
  shell (`touch`, `mkdir`) to create the target first when a new file
  is genuinely wanted, and only inside a scratch workspace.

## Output Formats

Every command prints exactly one JSON object on stdout and exits 0 on
success, 1 on error:

```json
{"ok": true, "workspaces": [{"workspace": "~/Work/iac-eval", "kind": "folder", "hash": "92fcf26671f2e2328dcb22795279d90e", "groups": [{"group": 0, "editors": ["~/Work/iac-eval/templates/aws_iam_policy/demo_policy.rego"], "active": "~/Work/iac-eval/templates/aws_iam_policy/demo_policy.rego"}]}]}
```

Through `computer-use cli run`, that object arrives inside the standard
CLI envelope as `result`. Check `ok` first; on failure read `error`.

## For AI Agents

When using this wrapper programmatically:

1. **Always read before opening.** Run `workspaces` and `tabs` before
   `open`, so you open into the right workspace instead of guessing.
2. **Use absolute paths** for all file operations.
3. **Never open a path you have not checked exists.** A misspelled path
   is refused on purpose; fix the path, do not force it.
4. **Check `process_running` after every open or diff.** `code` exits 0
   even when the app fails to start. If `process_running` is false, the
   window did not open; re-run with the desktop session env exported
   (the wrapper normally discovers it itself) and do not claim success.
4. **Writes go to scratch only.** Never write into his real workspaces
   (iac-eval, Reasearch-IaC, Legacy-link, LTHDT) for a test; use a
   scratch folder under `/tmp` and open that.
5. **Never close his VS Code windows or touch his open files.** `open`
   only adds a tab or window; there is no close command in this wrapper.
   Close only a scratch window you opened yourself, and only to leave
   the desktop clean after a test.
6. **Extension install/uninstall is NOT wrapped.** It mutates his
   profile and was not verified live. Run raw
   `code --install-extension <publisher.name>` from the shell only when
   explicitly requested, never as a discovery step.
7. **Tabs are last-persisted, not live.** If a tab you just opened does
   not appear in `tabs`, VS Code has not flushed state yet; wait and
   re-read, do not re-open it.
8. **Check return codes** - 0 for success, non-zero for errors - and
   parse `error` on failure.

## Limits (verified, not assumed)

- **No live buffer reads.** The `code` CLI documents no operation for
  reading the current editor buffer or listing open tabs, and this
  wrapper does not add one: `tabs` reads persisted state, `read` reads
  saved files. Unsaved changes are invisible.
- **No dirty-buffer text.** The only Backups entry found on the laptop
  is a 94-byte metadata blob for an untitled editor (no text content
  observed). `backups` lists backup files only; their content is never
  parsed as buffer text.
- **`code --status` is empty when VS Code is not running, and also when
  the call cannot reach a running instance.** Diagnostics need the
  desktop session env; from a bare shell `status` prints nothing with
  exit 0 either way. The wrapper's `running` field means "diagnostics
  were reachable".
- **Opening from a bare shell used to fail silently.** Without the
  session env `code` exits 0 while the app dies on an Electron X11
  ozone error. The wrapper now discovers the session env from a donor
  process and verifies a `code` process is running after every open
  and diff; if the process check ever reports false, treat the open
  as failed.
- **No `--json` flag on `code`.** The wrapper emits JSON itself; do not
  pass `--json` to `code`.

## More Information

- VS Code CLI docs: https://code.visualstudio.com/docs/configure/command-line
- Verification report: `improvements/speed-cli-vscode.md`
- Wrapper source: `scripts/vscode_cli.py`, tests: `tests/test_vscode_cli.py`

## Version

1.0.0
