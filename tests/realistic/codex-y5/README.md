# Realistic Test Suite codex-y5 (Codex Worker Y5)

This suite contains 10 realistic desktop-style browser workflows for testing computer-use agents. Each local fixture is a small application with real DOM state and deterministic controls.

## Hard Rules Enforced

1. Complexity and step count: Each test has 15 to 40 numbered steps, including exact UI targets, values, and verification points.
2. Fixed topics: The 10 topics follow the Worker Y5 brief without substitutions.
3. Offline fixtures: Each fixture is a single HTML document with inline CSS and JavaScript. No network resources are required.
4. Error sensitivity: Every workflow includes an intentional mistake and a visible recovery, plus values that expose stale observations, wrong diagnosis, and fabricated claims.
5. DOM verification without fixture hooks: Fixtures contain no `__verify` or self-grading function. `verifyTest` reads the rendered DOM and checks fixed expected values.
6. Fresh-state check: The checker asserts that a new fixture does not already pass, then replays the workflow and checks the resulting DOM. The simulator also performs this fresh-state check independently.
7. Zero em and en dashes: Only ASCII hyphens are used in suite files.

## Test Directory

- `test-01-git-workflow.md` (34 steps): Create a branch, commit a config change, create a merge conflict, recover from the wrong resolution, and verify the log.
- `test-02-music-player.md` (22 steps): Create Morning Focus, add tracks, reorder, shuffle, undo the wrong removal, and save a 10:10 playlist.
- `test-03-password-vault.md` (29 steps): Generate, copy, edit, delete and restore an entry, then lock and unlock the vault.
- `test-04-maps-directions.md` (27 steps): Search locations, avoid a toll route, save a route, reverse it, and save again.
- `test-05-calendar-recurring.md` (26 steps): Create five weekly events, edit one occurrence and the series, undo a wrong deletion, and delete one date.
- `test-06-video-editor.md` (36 steps): Import media, split and trim clips, recover from a bad trim, reorder, add a transition, and export.
- `test-07-chat-search.md` (23 steps): Search, filter by sender and date, jump to a result, star it, and forward it.
- `test-08-spreadsheet-pivot.md` (21 steps): Group six source rows by category, sum and filter them, then refresh after editing a source value.
- `test-09-file-search-tag.md` (24 steps): Search filenames, tag two files, filter, bulk rename, and move them to Reviewed.
- `test-10-extension-settings.md` (27 steps): Toggle the extension, edit site permissions and options, reset defaults, and verify persistence after reload.

## Local Dependency

`puppeteer-core` is pinned in this directory's package files and installed locally. To restore it, run:

```bash
npm install --prefix tests/realistic/codex-y5
```

The browser path defaults to `/usr/bin/chromium`. Set `CU_CHROME_PATH` to use another Chromium binary.

## Running the Automated Checker

The checker first confirms that the untouched fixture fails its end-state assertions, then replays the workflow and checks the final DOM.

```bash
# Run one workflow and verify its end state:
node tests/realistic/codex-y5/check.mjs --fixture tests/realistic/codex-y5/fixtures/test-01-git-workflow.html --test 01

# Replay and check all workflows:
node tests/realistic/codex-y5/check.mjs --all
```

## Running the Simulator

```bash
# Run one workflow:
node tests/realistic/codex-y5/simulate.mjs --test 01

# Run all 10 workflows:
node tests/realistic/codex-y5/simulate.mjs --all
```

The simulator drives the controls with Puppeteer clicks and typing, confirms the fresh fixture fails the final assertion, then calls `verifyTest` after the full workflow.

## Verifying Zero Em and En Dashes

```bash
python3 tests/realistic/codex-y5/check-dashes.py tests/realistic/codex-y5
```
