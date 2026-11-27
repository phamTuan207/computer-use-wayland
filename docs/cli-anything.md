# CLI-Anything vendoring

## Decision

The MINIMAL integration vendors CLI-Anything documentation only: the
backend doc (`skill/references/cli-anything.md`), a registry snapshot
(`skill/cli-anything/registry.json`), and per-app skill files
(`skill/cli-anything/<app>.md`). No harness code is vendored and no
session, relay, or MCP change is made. A harness CLI is an out-of-band API
call that already works from a plain shell; the vendored docs turn the
existing policy sentence in `skill/SKILL.md` ("Prefer an existing CLI/API,
then Chromium DOM or verified accessibility, then screenshots") into a
usable procedure. The full path (a `computer-use cli` subcommand, session
logging, MCP exposure) is built only after the minimal path has passed its
live test and a real task has used a harness end to end. See
`improvements/cli-anything/d-integration-design.md` for the design.

## Upstream

- Repo: https://github.com/HKUDS/CLI-Anything.git
- Upstream HEAD: `34f5195` ("Merge pull request #481 from HKUDS/chaohuang-ai-patch-6")
- Vendoring date: 2026-11-18
- Credit: HKUDS, the Data Intelligence Lab at the University of Hong Kong, led by Prof. Chao Huang.
- Upstream registry `meta.updated`: 2026-06-19

## License

Upstream root `LICENSE` is Apache License 2.0 (verified in the checkout).
Vendored files are docs only, each carrying the upstream URL and HEAD in
its header, with the Apache 2.0 notice preserved. Harness code is not
vendored, so no code-license decision is needed yet. Resolved 2026-11-19:
The project owner got permission from the repo owner to use CLI-Anything freely,
so the MIT vs Apache 2.0 flag is cleared. Credit: CLI-Anything is by HKUDS,
the Data Intelligence Lab at the University of Hong Kong, led by Prof. Chao
Huang (https://github.com/HKUDS/CLI-Anything, Apache License 2.0).

## First-wave apps

Obsidian, LibreOffice, GIMP, Inkscape, Krita, Blender, Audacity, Kdenlive,
Shotcut, Zotero, Joplin, Calibre. The registry snapshot carries the
`name`, `entry_point`, `skill_md`, `install_cmd`, and `requires` of each.
Only LibreOffice is installed on this VM, so it is the only first-wave app
with a live test. No harness exists for Firefox,
or Pinta, so the GUI backends stay mandatory for those apps. Chromium
is the exception: it has no upstream harness, but the registry also
carries a repo-owned Chromium wrapper entry (`chromium`, version
1.0.0, skill `skill/cli-anything/chromium.md`, code
`scripts/chromium_cli.py`), which is repo code, not vendored upstream
docs, and is covered by `tests/test_chromium_cli.py` instead of the
LibreOffice live test. Zen is the second exception: a repo-owned
wrapper entry (`zen`, version 1.0.0, skill `skill/cli-anything/zen.md`,
code `scripts/zen_cli.py`) with the same shape. VS Code is the third
exception: a repo-owned wrapper entry (`vscode`, version 1.0.0, skill
`skill/cli-anything/vscode.md`, code `scripts/vscode_cli.py`),
covered by `tests/test_vscode_cli.py` and verified live on the laptop.

## Update procedure

1. Check out upstream at a new HEAD and record it.
2. Re-copy the vendored skill files from `skills/cli-anything-<app>/SKILL.md`
   verbatim (no body edits) and the registry entries for the first-wave
   apps from `registry.json`.
3. Bump the upstream HEAD and vendoring date in every vendored file header,
   in `skill/references/cli-anything.md`, and in this document.
4. Re-run the docs test (`tests/cli_anything_docs.py`): it asserts the
   snapshot parses, every listed app has a vendored skill file, every
   vendored skill states its upstream version, and `skill/SKILL.md` links
   to `references/cli-anything.md`.
5. Re-run the LibreOffice live test (`tests/cli_anything_live.py`).

Do not live-fetch the registry at task time: the snapshot is what makes
backend selection reproducible offline. Keep the snapshot small (first wave
only) and grow it per task, one app at a time.
