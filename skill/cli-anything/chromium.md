---
name: "cli-anything-chromium"
description: >-
  Command-line interface for Chromium: list, open, activate and close tabs
  over the loopback DevTools HTTP endpoints, read the current tab, and read
  history, bookmarks and downloads from the Chromium profile, read-only.
  Designed for AI agents that need browser state without screenshots.
---

<!-- Repo-owned skill, NOT vendored upstream. -->
<!-- There is no upstream CLI-Anything harness for Chromium. -->
<!-- Repo: phamTuan207/computer-use-wayland, branch speed-swarm. -->
<!-- Skill version: 1.0.0. Wrapper: scripts/chromium_cli.py. -->
<!-- Written: 2026-11-18. Do not edit except with the wrapper. -->

# cli-anything-chromium

Chromium tabs, history, bookmarks and downloads without the GUI. Tab
commands talk to Chromium over its loopback DevTools HTTP endpoints
(`/json/list`, `/json/new`, `/json/activate`, `/json/close`); history,
bookmarks and downloads read the Chromium profile read-only. Designed
for AI agents and power users who need browser state without
screenshots. Reading a page's DOM still goes through
`computer-use browser observe/act`, which owns the WebSocket side.

## Installation

No install. The wrapper ships in this repo at
`scripts/chromium_cli.py` (stdlib only, Python 3) and runs through the
shared CLI:

```bash
computer-use cli run chromium -- <command>
```

**Prerequisites:**
- Chromium installed (`chromium` on PATH).
- For tab commands: a Chromium with a loopback CDP endpoint, normally
  started by `computer-use browser start` (endpoint
  `http://127.0.0.1:9222`, dedicated agent profile). The owner's own
  Chromium runs WITHOUT a remote debugging port (verified 2026-11-18:
  no DevToolsActivePort file, nothing listening on 9222), so the
  wrapper can never attach to his session.
- For history, bookmarks and downloads: a Chromium profile dir
  (default `~/.config/chromium/Default`).

## Usage

### Basic Commands

```bash
# Probe first: is the endpoint up, does the profile exist?
computer-use cli run chromium -- status

# List tabs (read-only, never disturbs his session)
computer-use cli run chromium -- tabs

# Open a URL in a NEW tab, read its title, close it
computer-use cli run chromium -- open https://example.com
computer-use cli run chromium -- current
computer-use cli run chromium -- close <tab-id>

# Read-only profile data (no endpoint needed)
computer-use cli run chromium -- history --limit 20
computer-use cli run chromium -- bookmarks
computer-use cli run chromium -- downloads --limit 20
```

### Endpoint and profile flags

```bash
# A test Chromium on another loopback port (separate --user-data-dir)
computer-use cli run chromium -- --endpoint http://127.0.0.1:9333 tabs

# A different profile dir for history/bookmarks/downloads
computer-use cli run chromium -- --profile ~/.config/chromium/Default history
```

Flags go after the `--` that separates the `cli run` arguments from
the wrapper arguments, and before the command. The endpoint must be
loopback http; any other host is refused. The profile may be a profile
dir (with History directly inside, as the agent profile does) or a
user-data dir (with Default/History inside).

## Command Groups

| Command | Description |
|---|---|
| `tabs` | List page tabs: id, title, url |
| `open <url>` | Open an http(s) URL in a NEW tab; navigates it and waits for load (max 10 s); records it as current |
| `activate <tab-id>` | Bring a tab to front; records it as current |
| `close <tab-id>` | Close one tab by id |
| `current` | Title and URL of the tracked current tab |
| `history [--limit N]` | Recent visits from the profile History DB (default 20, max 200) |
| `bookmarks` | All bookmarks from the profile Bookmarks file |
| `downloads [--limit N]` | Recent downloads from the History DB (default 20, max 200) |
| `status` | Endpoint and profile reachability probe; always exits 0 |

## Examples

```bash
# End-to-end tab round trip through the shared CLI
computer-use cli run chromium -- status
computer-use cli run chromium -- tabs
computer-use cli run chromium -- open https://example.com
computer-use cli run chromium -- current
computer-use cli run chromium -- close <tab-id-from-open>

# What did he visit most recently? (read-only, his Default profile)
computer-use cli run chromium -- history --limit 10

# Downloads, newest first, with state (complete, in_progress, cancelled)
computer-use cli run chromium -- downloads --limit 10
```

## State Management

State lives in one small JSON file,
`~/.local/share/agent-computer-use/chromium-cli-state.json` (mode
0600). It records only the tab this wrapper last opened or activated
(tab id, title, url, timestamp). The CDP HTTP endpoints do not report
which tab is active, so `current` returns that tracked tab, verified
live against `/json/list`. If no tab was tracked, or the tracked tab
is closed, `current` fails and tells the agent to list tabs and
activate one. Closing the tracked tab clears the state.

History reads copy the live History sqlite file to a temp file first
(the live DB is locked while Chromium runs) and open the copy
read-only. Nothing is ever written to the profile. Bookmarks are
parsed from the profile `Bookmarks` JSON file; when the file is
absent (his Default profile has none, verified 2026-11-18),
`bookmarks` returns an empty list with a note, not an error.

## Output Formats

Every command prints exactly one JSON object. Tab commands return
`{"ok": true, "command": ..., "endpoint": ..., ...}`; profile
commands return `{"ok": true, "command": ..., "profile": ..., ...}`.
On failure the wrapper prints
`{"ok": false, "command": ..., "error": ...}` and exits 1, except
`status`, which always exits 0 and reports `reachable: true/false`
so it can be used as the verify-first probe. Through
`computer-use cli run` the wrapper output also arrives inside the
usual envelope (`app`, `args`, `returncode`, `stdout_truncated`,
`stderr_truncated`) with the parsed wrapper output under `result`.

## For AI Agents

1. Always run `status` first. If `reachable` is false, run
   `computer-use browser start` to bring up the agent-managed
   Chromium, then retry. Never point the wrapper at his Chromium:
   it has no debug port, and there is no flag that attaches to it.
2. List tabs before acting on a tab id. Tab ids come from `tabs` or
   from `open`, never from memory.
3. `open` always opens a NEW tab and navigates it. Chromium 157
   ignores the `url` parameter of PUT /json/new (verified live
   2026-11-18: the new tab stays about:blank), so `open` creates the
   tab over HTTP and then drives CDP Page.navigate over the tab's
   WebSocket, waiting up to 10 s for the load event, and returns the
   tab with its settled title and URL. If `open` reports a navigation
   failure or timeout, the tab exists but is about:blank: close it by
   the tab id in the error, or list tabs and retry. Never treat an
   about:blank result as the URL having opened.
4. `close` closes exactly the tab id the task names. Never close a
   tab you did not list first, and never close all tabs.
5. `current` only knows tabs this wrapper opened or activated. After
   any other agent or the user switches tabs, run `activate` first.
6. History, bookmarks and downloads are read-only. They need no
   endpoint and never touch a running browser.
7. Check the return code. A non-zero return after `open` or `close`
   may mean a partial change landed: list tabs to see the real state,
   never replay the command blindly.
8. For DOM work on a tab (click, fill, read elements), use
   `computer-use browser observe/act` with the tab id from `tabs`.
   This wrapper does not do DOM.

## More Information

- Wrapper source: `scripts/chromium_cli.py` in this repo.
- Shared CLI wiring: `computer-use cli run chromium -- ...`
  (`scripts/cu.py`, `cli_run_chromium`).
- Browser DOM skill: `skill/references/browser.md`.
- Audit that motivated this wrapper (Chromium: 28 launches, 535
  visits in 14 days, priority 2):
  `improvements/speed-cli-audit.md`.

## Version

1.0.0
