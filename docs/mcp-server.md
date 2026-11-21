# MCP server for computer-use-wayland

A small MCP server that exposes the repo's main ops as named tools,
over local stdio only. Server: `scripts/mcp_server.py` (stdlib only).
Tests: `tests/test_mcp_server.py`.

This is a prototype. It is NOT the repo's existing session bridge:
`scripts/mcp_bridge.py` exposes one generic `computer_use_session`
tool that forwards raw driver commands. This server exposes one tool
per op, with strict argument checks, so an MCP client can call
locate, click, type, screenshot, overlay, and session ops directly.

## Tools

| Tool | What it does |
| --- | --- |
| session_start | Open the single Zen session. Optional marionette_port, wd_port, timeout_s (default 10 s). Fails when a session is already active. |
| session_status | Report whether a session is active, plus the session manager state and hung detection. |
| session_finish | Close the live session and release the single-owner lock. Safe to call twice. |
| locate | Exact rect of an element by CSS selector, from getBoundingClientRect. |
| click | Locate through the DOM, then send a REAL mouse click at the rect center through the native pointer, with a cursor position check. Never a DOM click. |
| type | Type text into an element: focus, set the value through the native setter, dispatch input and change events. Returns the value before and after. |
| screenshot | Screenshot of the current tab through WebDriver, returned as MCP image content (base64 PNG). |
| overlay | Show, hide, or report the computer-use pill. action is acquire, release, or status. |

## How to run

```sh
python3 scripts/mcp_server.py
```

Stdio transport, newline delimited JSON-RPC, MCP protocol version
2024-11-05. The server reads one JSON message per line on stdin and
writes one JSON response per line on stdout. Tool call logs (tool
name and elapsed time only, never typed text) go to stderr.

Environment, same as `scripts/zen_dom.py`: `ZEN_MARIONETTE_PORT`
(default 2828), `ZEN_WD_PORT` (default 4444), `ZEN_GECKODRIVER`
(default /tmp/geckodriver).

## Client config example

Any MCP client that can spawn a local stdio server works. Example
for a client config file:

```json
{
  "mcpServers": {
    "computer-use": {
      "command": "python3",
      "args": ["/path/to/computer-use-wayland/scripts/mcp_server.py"]
    }
  }
}
```

No MCP client library is installed on this machine, so the server
was tested with the minimal stdio JSON-RPC client in
`tests/test_mcp_server.py`, not with a real MCP client. That test
file is the reference for the wire format: initialize, then
notifications/initialized, then tools/list and tools/call.

## Test-only fake backend

```sh
python3 scripts/mcp_server.py --fake
```

Runs an in-memory backend with a fake DOM (a counter button
`#count-btn` and a text input `#name`). It proves the tool plumbing
without a browser. Never use `--fake` to claim a real browser
result. The test suite runs the fake backend plus one real backend
check: with no browser present, session_start must fail cleanly
and fast.

Run the tests:

```sh
python3 tests/test_mcp_server.py
```

Measured on this machine, 2026-11-21: 12 tests, all pass, suite
wall clock about 1.4 s. Each fake backend test takes about 80-90 ms
including server spawn. The real backend no-browser check fails
in about 0.15 s with a clear "could not start Zen session" error.

## Limits, read before use

- Local stdio only. There is no network listener, no auth, and no
  token. Never put this server on a network, never expose its stdio
  to another machine, and never run it as root.
- One live session at a time. The single-owner lock comes from
  `scripts/session_manager.py`. A leaked session still blocks
  everything until Zen restarts.
- The server only talks to the Zen that `scripts/zen_dom.py`
  connects to: the Zen instance with Marionette on 127.0.0.1:2828.
  Enable Marionette only on a dedicated test Zen, never on a
  daily use Zen.
- Click needs a Wayland session with the native pointer binary.
  Without one it fails with a clear error instead of pretending
  to click.
- Tool errors come back as MCP results with isError true. Protocol
  errors come back as JSON-RPC errors. Typed text is never logged.

## UNVERIFIED on this machine

No Firefox or Zen binary exists here, no geckodriver, no Wayland
session, and no MCP client is installed. So the live paths are
unverified: session_start against a real Zen, locate, click, type,
and screenshot on a real tab, overlay acquire on a real desktop,
and a handshake with a real MCP client. All of those need the
laptop. What is verified here is the protocol, the argument checks,
the error paths, and the full tool flow against the fake backend.
