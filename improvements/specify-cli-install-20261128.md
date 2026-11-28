# specify CLI install record - 2026-11-28

Item 5.2, owner order 2026-11-28 10:14 Asia/Ho_Chi_Minh. Council decision 3 of
2026-11-24 (r3-decision record): install the specify CLI, YES 2-1, VM only, in
the inter-run window, version recorded, frozen R3 files verified unchanged,
first real use to judge value, drop the CLI if the first use shows no value.

## What specify is

GitHub Spec Kit CLI. Source repo: github/spec-kit. PyPI package: specify-cli,
maintained by the Spec Kit maintainers. Official install docs
(docs/installation.md and docs/install/pypi.md in that repo) give two routes:
install from the GitHub source pinned to a release tag, or install the PyPI
package. The council route was the PyPI route: uv tool install specify-cli,
then the Codex integration. The team integration files (constitution, task
spec template, bug report template) were already pushed on 2026-11-24 as
commit 4c3e7ec on branch spec-kit-integration; the CLI itself was not
installed at that time.

## Install state before (checked 2026-11-28 10:17 Asia/Ho_Chi_Minh)

- VM: specify not found. uv present, version 0.13.10 at ~/.local/bin/uv.
  uv tool list showed only graphifyy v0.9.120.
- Laptop (checked read-only over the team SSH helper): specify not found.
  uv present, version 0.13.9. uv tool list showed no specify-cli.
- Council said VM only, so the laptop was checked but not installed on.

## Install (VM, 2026-11-28 10:17-10:18 Asia/Ho_Chi_Minh)

Command: uv tool install specify-cli

Result: specify-cli 1.4.5 installed, 42 packages resolved, 1 executable
installed at ~/.local/bin/specify. Exit code 0. uv tool list after install:

    graphifyy v0.9.120
    - graphify
    - graphify-mcp
    specify-cli v1.4.5
    - specify

## Live-use proof (2026-11-28 10:19 Asia/Ho_Chi_Minh)

1. specify version: exit 0. CLI Version 1.4.5, Python 3.11.17, Platform
   Linux, Architecture x86_64.
2. specify --help: exit 0. Commands include init, check, version, mcp, self,
   extension, integration, event, preset, artifact, bundle, workflow.
3. specify check: exit 0. Codex CLI reported available on this VM.
4. Throwaway project init in /tmp (deleted after the check):
   specify init smokeproj --integration codex --non-interactive
   Result: exit 0, Project ready. Created .specify/ (memory/constitution.md,
   templates, scripts, workflows, integration manifests) and
   .agents/skills/ with 9 skills: speckit-analyze, speckit-checklist,
   speckit-clarify, speckit-constitution, speckit-converge,
   speckit-implement, speckit-plan, speckit-specify, speckit-tasks.
   Note: --no-git is not an option in 1.4.5; first attempt failed with
   No such option, retried with --non-interactive and succeeded.

## Council conditions check

- VM only: yes. Laptop untouched.
- Inter-run window: yes. R3-L3 closed 2026-11-27; no run in flight.
- Version recorded: 1.4.5, above.
- Frozen R3 files unchanged: the install is a per-user uv tool install
  outside any repo checkout. The main computer-use-wayland checkout status
  before and after the install was identical (same pre-existing modified
  and untracked entries, nothing added by the install). The throwaway init
  ran only under /tmp and was deleted after verification.
- Integration into a real repo: proven only in the throwaway project. No
  .specify/ or .agents/ files were written into this repo. Wiring the
  Codex integration into a real checkout stays a separate decision, per
  the dissent drift concern in the council record.
- Drop-if-no-value condition stays open: judge at first real use.

## Cleanup

Throwaway project under /tmp removed after the proof. No browser work, no
window work, no laptop changes in this task.
