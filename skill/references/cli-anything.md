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
exists for VS Code, Zen, Chromium, Firefox, or Pinta: those tasks always use
the GUI backends.

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
or `cli-hub install <app>` only.

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
