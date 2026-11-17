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
- Upstream registry `meta.updated`: 2026-06-19

## License

Upstream root `LICENSE` is Apache License 2.0 (verified in the checkout).
Vendored files are docs only, each carrying the upstream URL and HEAD in
its header, with the Apache 2.0 notice preserved. Harness code is not
vendored, so no code-license decision is needed yet. Open flag: individual
harness `setup.py` classifiers claim MIT while the repo root is Apache 2.0;
resolve that contradiction with the maintainer before vendoring any harness
code.

## First-wave apps

Obsidian, LibreOffice, GIMP, Inkscape, Krita, Blender, Audacity, Kdenlive,
Shotcut, Zotero, Joplin, Calibre. The registry snapshot carries the
`name`, `entry_point`, `skill_md`, `install_cmd`, and `requires` of each.
Only LibreOffice is installed on this VM, so it is the only first-wave app
with a live test. No harness exists for VS Code, Zen, Chromium, Firefox,
or Pinta, so the GUI backends stay mandatory for those apps.

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
