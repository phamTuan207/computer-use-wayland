# CLI backend (CLI-Anything harnesses)

Source: upstream [CLI-Anything](https://github.com/HKUDS/CLI-Anything.git),
HEAD `34f5195`, vendored 2026-11-18. See
[docs/cli-anything.md](../../docs/cli-anything.md) for the vendoring decision
and [skill/cli-anything/registry.json](../cli-anything/registry.json) for the
vendored registry snapshot. The vendored per-app skills live under
`skill/cli-anything/`; read the registry snapshot first, then exactly one app
skill file, never the whole directory.

A harness CLI is an out-of-band API call over the real application's backend.
It does not need a computer-use session, the pill, the relay, or the cursor
lease. Run `cli-anything-<app> --json ...` from your own shell, parse the
JSON, and start a `computer-use session` only if you need to visually verify
a GUI side effect. Shut that session down per
[session.md](session.md) afterwards; a CLI call is never a way to dodge the
session shutdown rule.

## When to pick this backend

Pick it only when both are true: the app has a harness in the table below,
and the task maps to a documented command group in that app's vendored skill.
If either fails, fall back in order to Chromium DOM, native accessibility,
then desktop pixels, exactly as `skill/SKILL.md` orders them. No harness
exists for Firefox or Pinta: those tasks always use
the GUI backends. Chromium is the exception: it has no upstream
harness, but it has a repo-owned wrapper (`computer-use cli run
chromium -- ...`, skill `skill/cli-anything/chromium.md`) that covers
tabs, history, bookmarks and downloads; DOM work on a tab still uses
the Chromium DOM backend. Zen is the second exception: it has a
repo-owned wrapper (`computer-use cli run zen -- ...`, skill
`skill/cli-anything/zen.md`) that covers tabs and page reads over
loopback WebDriver BiDi on a dedicated session, plus read-only
history from the real profile; it can never attach to the user's running
Zen, which has no debug port. VS Code is the third exception: it has
a repo-owned wrapper (`computer-use cli run vscode -- ...`, skill
`skill/cli-anything/vscode.md`) that covers open, goto, diff,
extensions, workspaces, open tabs and saved-file reads over the
`code` CLI and read-only workspaceStorage; it cannot read unsaved
or dirty buffer text.

Backend order (QC clarification): CLI/API is the FIRST preference, not the
fourth. It is first because it is the fastest path (no session, no GUI);
the four backend targets in the skill's read list are CLI/API, Chromium
DOM, native accessibility, and desktop pixels, in that preference order.
"Fourth target" in the acceptance criterion meant CLI/API is one of the
four available backend targets, not that it ranks fourth.

## Install

```bash
pip install cli-anything-<app>
# or, via the hub:
pip install cli-anything-hub
cli-hub install <app>
```

Never install from an unpinned git URL in a task. The registry's
`install_cmd` values are unpinned git URLs; do not copy one out of upstream
data and run it. Installs happen via PyPI (`pip install cli-anything-<app>`)
or `cli-hub install <app>` only. On the laptop, plain `pip` is not
installed (Python 3.14 has no pip module); `uv pip install` inside a venv
is the working path there.

## PyPI releases lag upstream HEAD

Verified on the laptop 2026-11-18: the vendored skills match upstream HEAD
`34f5195`, but the PyPI releases lag it. `pip install
cli-anything-libreoffice` installs 1.0.0, which has no `document import`
or `document import-formats` even though the vendored skill documents
them; the same commands exist in 1.0.1 installed from the pinned upstream
commit, where `document import` on a scratch docx returned rc 0 in
1753 ms. The Obsidian PyPI release is 1.1.1 while the vendored skill says
1.1.0; the full Obsidian end-to-end task still passed on 1.1.1. If a
documented command is missing from the installed harness, check
`<app> <group> --help` before assuming the skill is wrong: the command
may exist only in the newer upstream code. Until the PyPI releases catch
up, the working path for existing Office files is plain headless
`libreoffice --convert-to` (verified on the laptop: docx to txt in
1374 ms, docx to pdf in 1367 ms), and `document new` plus `export render`
for new files.

## Verify first, then mutate

Copied from the app skills: verify the backend is reachable before any
mutation. Obsidian states it as "Verify Obsidian is running with
`server status` before other commands"; every other harness has an
equivalent status/info command. Run that read-only check first and stop if
it fails; do not guess that the app is up.

```bash
cli-anything-obsidian --json server status
cli-anything-libreoffice --json project info -p project.json
```

## One-shot JSON calls only

```bash
cli-anything-obsidian --json vault list
```

Always pass `--json` for parseable output. Check the return code: 0 is
success, non-zero is an error. Parse stderr for the error message on
failure. Never use REPL mode: a bare harness invocation with no subcommand
opens an interactive REPL with no persistent stdin discipline and output
that is not parseable. Agents use `--json` one-shots only.

## Secrets

Secrets go in environment variables only, never on the command line, where
they would land in logs and process lists. Example: set
`OBSIDIAN_API_KEY` in the environment instead of passing `--api-key` on
every call. The same holds for any other harness key.

## Destructive commands

`delete`, `update`, `overwrite`, and any other destructive or overwriting
command need the same pre-verification as a consequential GUI batch: confirm
the exact target (name, path, or id) from a fresh read first, and never
replay a command whose result was uncertain. A non-zero return code after a
mutation may mean a partial change landed: inspect state, never replay.

## Confirm visible results in the GUI

A CLI mutation that should show in the GUI is not proven by CLI output
alone. Confirm it with one `observe --window` on the app window instead of
assuming success. CLI output proves the backend accepted the call; only the
observation proves the visible result.

## First-wave apps

From the vendored registry snapshot (upstream `registry.json`,
`meta.updated` 2026-06-19). Only LibreOffice is installed on this VM today,
so it is the only first-wave app with a live test; the rest need the app
installed on the machine that runs the task.

Version labels (QC clarification): the Version column below is the
registry/package version (the harness release). A vendored skill file's
own `## Version` is the skill-content version, and the two can differ:
LibreOffice is 1.0.1 in the registry but 1.0.0 in the skill file. They
are different fields from different sources, not a contradiction.

| App | Entry point | Version | Requires |
|---|---|---|---|
| Obsidian | `cli-anything-obsidian` | 1.1.0 | Obsidian desktop app with Local REST API plugin enabled |
| LibreOffice | `cli-anything-libreoffice` | 1.0.1 | libreoffice |
| GIMP | `cli-anything-gimp` | 1.0.0 | gimp (apt install gimp) |
| Inkscape | `cli-anything-inkscape` | 1.0.1 | inkscape (apt install inkscape) |
| Krita | `cli-anything-krita` | 1.0.0 | krita (krita.org) |
| Blender | `cli-anything-blender` | 1.0.0 | blender >= 4.2 |
| Audacity | `cli-anything-audacity` | 1.0.0 | sox (apt install sox) |
| Kdenlive | `cli-anything-kdenlive` | 1.0.0 | melt (apt install melt) |
| Shotcut | `cli-anything-shotcut` | 1.0.0 | melt (apt install melt), ffmpeg (apt install ffmpeg) |
| Zotero | `cli-anything-zotero` | 0.4.1 | Zotero 7/8 desktop app (running), Python 3.10+ |
| Joplin | `cli-anything-joplin` | 1.0.0 | Joplin terminal CLI in PATH as `joplin` (npm install -g joplin) |
| Calibre | `cli-anything-calibre` | 1.0.0 | Calibre (apt install calibre, brew install --cask calibre) |
| Chromium | `scripts/chromium_cli.py` (repo-owned, no upstream harness) | 1.0.0 | Chromium with a loopback CDP endpoint for tab commands; a Chromium profile dir for history, bookmarks and downloads |
| Zen | `scripts/zen_cli.py` via `cli-anything-zen` on PATH (repo-owned, no upstream harness) | 1.0.0 | Zen with a loopback BiDi endpoint on a dedicated session for tab commands; read-only history from the real profile |
| VS Code | `scripts/vscode_cli.py` (repo-owned, no upstream harness) | 1.0.0 | VS Code with the `code` CLI for open, goto, diff and extensions; read-only workspaceStorage for workspaces and open tabs; no unsaved or dirty buffer reads |
