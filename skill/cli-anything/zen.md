---
name: "cli-anything-zen"
description: >-
  Command-line interface for Zen Browser: list, open, activate, navigate
  and close tabs over loopback WebDriver BiDi on a dedicated session,
  read the current tab and page text, and search history from the real
  Zen profile, read-only. Designed for AI agents that need browser state
  without screenshots.
---

<!-- Repo-owned skill, NOT vendored upstream. -->
<!-- There is no upstream CLI-Anything harness for Zen. -->
<!-- Repo: phamTuan207/computer-use-wayland, branch speed-swarm. -->
<!-- Skill version: 1.0.0. Wrapper: scripts/zen_cli.py. -->
<!-- Verified: 2026-11-18 on the laptop, Zen 1.24.2b (see Verification). -->
<!-- Do not edit except with the wrapper. -->

# cli-anything-zen

Zen tabs and history without the GUI. Tab commands talk to Zen over
WebDriver BiDi (the Firefox Remote Agent) on a loopback WebSocket;
history reads the Zen profile read-only. Designed for AI agents and
power users who need browser state without screenshots. Reading a
page's DOM beyond title, URL and visible text still goes through
`computer-use browser observe/act`.

## Installation

No pip install. The wrapper ships in this repo at
`scripts/zen_cli.py` (stdlib only, Python 3) and runs through the
shared CLI once installed on PATH as `cli-anything-zen`:

```bash
cp scripts/zen_cli.py ~/.local/bin/cli-anything-zen
chmod +x ~/.local/bin/cli-anything-zen
computer-use cli run zen -- status
```

**Prerequisites:**
- Zen installed (`zen-browser` on PATH).
- For tab commands: a dedicated session started by the wrapper
  (`session start`, below). the owner's own Zen runs WITHOUT a remote
  debugging port (verified 2026-11-18: nothing listening on 9222, 2828
  or 6000), so the wrapper can never attach to his session.
- For history: a Zen profile dir (default auto-detected from
  `~/.config/zen/profiles.ini`, the Default=1 profile).

## Usage

### Basic Commands

```bash
# Probe first: is a dedicated session up, does the profile exist?
computer-use cli run zen -- status

# Start the dedicated session (headless, fresh profile, port 9222)
computer-use cli run zen -- session start
computer-use cli run zen -- session status

# List tabs (read-only), open a URL in a NEW tab, read it, close it
computer-use cli run zen -- tabs
computer-use cli run zen -- open https://example.com
computer-use cli run zen -- current
computer-use cli run zen -- page
computer-use cli run zen -- close <index>

# Read-only history from his real profile (no session needed)
computer-use cli run zen -- history --limit 20
computer-use cli run zen -- history github --limit 10

# Stop the dedicated session when done
computer-use cli run zen -- session stop
```

### Session and port flags

```bash
# A dedicated session on another loopback port
computer-use cli run zen -- --port 9223 session start
computer-use cli run zen -- --port 9223 tabs

# A different profile dir for history
computer-use cli run zen -- --profile ~/.config/zen/<profile-dir> history
```

Flags go after the `--` that separates the `cli run` arguments from
the wrapper arguments, and before the command. The BiDi endpoint is
always loopback; the wrapper never connects anywhere else.

## Command Groups

| Command | Description |
|---|---|
| `session start [--port N] [--profile DIR] [--no-headless]` | Start the dedicated BiDi session (default port 9222, tries up to 9231 if busy; default profile `~/.cache/cli-anything-zen/profile`; headless) |
| `session stop` | Stop the dedicated session (only the recorded pid with the recorded profile in its cmdline) |
| `session status` | Dedicated session probe; always exits 0 |
| `tabs` | List tabs of the dedicated session: index, url, title |
| `open <url>` | Open an http(s) URL in a NEW tab; records it as current |
| `open --live <url>` | Open a URL in a new tab of his RUNNING Zen via remoting; opt-in only, PROPOSED-live, see below |
| `navigate <url> [--tab INDEX]` | Navigate the current (or named) tab |
| `activate <index>` | Bring a tab to front; records it as current |
| `close <index>` | Close one tab by index; refuses the last remaining tab |
| `current` | Title and URL of the tracked current tab |
| `page [--tab INDEX] [--text-chars N]` | Title, URL and visible text of a tab (default 2000 chars, max 10000) |
| `history [query] [--limit N]` | Recent visits, or LIKE matches for query, from the real profile (default 20, max 200) |
| `status` | Session reachability plus profile and history presence; always exits 0 |

## Examples

```bash
# End-to-end tab round trip through the shared CLI
computer-use cli run zen -- session start
computer-use cli run zen -- tabs
computer-use cli run zen -- open https://example.com
computer-use cli run zen -- current
computer-use cli run zen -- page
computer-use cli run zen -- close <index-from-open>
computer-use cli run zen -- session stop

# What did he visit most recently? (read-only, his real profile)
computer-use cli run zen -- history --limit 10

# Search his history for a topic
computer-use cli run zen -- history github --limit 10
```

## State Management

State lives in one small JSON file,
`~/.local/share/agent-computer-use/zen-cli-state.json` (mode 0600).
It records the dedicated session (port, profile, pid, ws URL) and the
tab this wrapper last opened or activated (index, title, url,
timestamp). Tabs are tracked by INDEX and URL, never by BiDi context
id: context ids change on every new BiDi session (verified 2026-11-18,
see Verification), while the tab order and URLs stay the same. BiDi
`getTree` does not report which tab is active, so `current` returns
the tracked tab, verified live against `getTree`: the tracked index
when that position still holds the tracked URL, else the first tab
with the tracked URL. If no tab was tracked, `current` shows the
first live non-blank tab. Closing the tracked tab clears the
tracking.

The dedicated profile lives at `~/.cache/cli-anything-zen/profile`
and belongs to the wrapper; it never sees his data. `session start`
refuses any `--profile` inside `~/.config/zen` (his real profiles).
`session stop` refuses to kill a pid whose cmdline does not contain
the recorded dedicated profile path.

History reads copy the live places.sqlite file to a temp file first
(the live DB is locked while Zen runs) and open the copy read-only.
Nothing is ever written to the profile.

## Output Formats

Every command prints exactly one JSON object. Tab commands return
`{"ok": true, "command": ..., "port": ..., ...}`; history returns
`{"ok": true, "command": ..., "profile": ..., "visits": [...]}`.
On failure the wrapper prints
`{"ok": false, "command": ..., "error": ...}` and exits 1, except
`session status` and `status`, which always exit 0 and report
`session_up: true/false` so they can be used as the verify-first
probe. Through `computer-use cli run` the wrapper output also arrives
inside the usual envelope (`app`, `args`, `returncode`,
`stdout_truncated`, `stderr_truncated`) with the parsed wrapper
output under `result`.

## For AI Agents

1. Always run `status` first. If `session_up` is false, run
   `session start` to bring up the dedicated session, then retry.
   Never point the wrapper at his Zen: it has no debug port, and
   there is no flag that attaches to it.
2. List tabs before acting on a tab index. Indices come from
   `tabs` or from `open`, never from memory. Never use a BiDi context
   id from any output: the wrapper never prints one, because it is a
   per-session handle that is stale in the next invocation. If a
   command rejects your tab argument, it is probably a context id;
   re-list and use the index.
3. `open` always opens a NEW tab in the DEDICATED session. It does
   not touch his Zen. To open a page in his own Zen you must use
   `open --live`, and only when he asked for it (rule 9).
4. `close` closes exactly the index the task names. Never close
   a tab you did not list first, and never close all tabs. The last
   remaining tab of the dedicated session cannot be closed; use
   `session stop` instead.
5. `current` only knows tabs this wrapper opened or activated. After
   any other agent switches tabs, run `activate` first.
6. History is read-only and needs no session. It reads his real
   profile, so treat its contents as his private browsing data: use
   it for the task at hand, never paste it elsewhere.
7. Check the return code. A non-zero return after `open` or `close`
   may mean a partial change landed: list tabs to see the real state,
   never replay the command blindly.
8. Stop the dedicated session when the task is done
   (`session stop`). Do not leave headless Zen instances behind.
9. `open --live` is PROPOSED-live, not verified-live: the
   `--new-tab` remoting flag is documented in `zen-browser --help`,
   but it was deliberately never run against his session (it would
   add a tab to his Zen). Use it only when he explicitly asked to
   open something in his own Zen, and say so in the report.
10. Secure field values are never read. The DOM tools redact
    password fields where they control the bytes (snapshot
    values, `field_value`, RDP report URLs), but a raw
    `evaluate()` can still read `input.value`: never use it on
    a password or credential field, and never print a field
    value you did not need. Typing into a secure field is
    verified with `verify_typed` (bool only), never by reading
    the value back into a report.
10. For DOM work on a tab (click, fill, read elements), use
    `computer-use browser observe/act`. This wrapper does not do DOM.

## Verification

Verified 2026-11-18 on the laptop (Zen 1.24.2b, `zen-browser-bin
1.24.2b-1`), against a dedicated headless instance with a fresh
profile in /tmp, NOT against his session:

- `zen-browser --headless --no-remote --profile /tmp/zen-bidi-test
  --remote-debugging-port=9222 about:blank` listens on 127.0.0.1:9222
  and logs `WebDriver BiDi listening on ws://127.0.0.1:9222`. The
  BiDi WebSocket is at path `/session` (root returns an httpd.js
  placeholder page; a plain ws:// connect to root fails).
- `session.new` returns browserName `zen`, browserVersion `1.24.2b`.
- `browsingContext.getTree` lists the tabs with context ids and URLs
  (no title field; titles come from `script.evaluate`).
- `browsingContext.navigate` to https://example.com with wait
  complete, then `script.evaluate` returns title `Example Domain`
  and the URL.
- `browsingContext.createContext` is `unknown command` in this
  build, so a new tab is opened with `window.open(url, '_blank')`
  from an existing tab and found in `getTree` by its opener. That
  path is verified: the new context appears with the right URL,
  `browsingContext.activate` succeeds, and `browsingContext.close`
  removes it.
- BiDi context ids are NOT stable across sessions. Three sequential
  `session.new` connections against the same headless instance
  returned three different UUID sets for the same three tabs, and
  the clientWindow id changed too, while the tab order and the URLs
  stayed identical in all three listings. A one-shot CLI opens a new
  BiDi session per command, so a context id from `tabs` is already
  stale when `close` runs. The wrapper therefore addresses tabs by
  INDEX (position in `getTree` order) and resolves each index to a
  fresh context id inside its own BiDi session. It never prints a
  context id. The draft's context-id design does not work for a
  one-shot CLI; this is the correction.
- His running Zen (pid 546184) has no debug port: nothing listening
  on 9222, 2828 or 6000. Tab commands cannot see his tabs; only
  read-only `history` and opt-in `open --live` touch his session,
  and the second was never run.
- Audit that motivated this wrapper (Zen: 50 launches, 1364 visits
  in 14 days, heaviest GUI app, priority 1):
  `improvements/speed-cli-audit.md`.

## More Information

- Wrapper source: `scripts/zen_cli.py` in this repo.
- Shared CLI wiring: `computer-use cli run zen -- ...`
  (registry entry `zen`, entry point `cli-anything-zen`, via
  `scripts/cli-anything.py`).
- Browser DOM skill: `skill/references/browser.md`.
- Payoff draft this wrapper verifies (Zen/Firefox skill, WebDriver
  BiDi, opt-in remote debugging port, compatibility was UNVERIFIED):
  `improvements/cli-anything-payoff-drafts.md`.

## Version

1.0.0
