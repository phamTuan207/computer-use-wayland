# Interactive agent driver

Use one initial model view, one batch of all predictable actions, then its final image. See the
required [batch-first policy](../SKILL.md#batch-first-required). Keep machine-side preflight
captures and guards enabled; these checks do not need a model decision.

Start `computer-use session -- computer-use session-driver` with your tool's
persistent interactive process facility (PTY/stdin session or background terminal).
Keep that process handle for the whole task; do not launch a new shell session
for each action and do not redirect stdin to `/dev/null`. The pill remains active
while the driver waits for the next instruction. Send one JSON object per line:

```json
{"args":["observe","--window","0xEXACT_ADDRESS","--focus"]}
{"args":["act","--observation","/returned/path.json","--actions","-"],"stdin":"[{\"type\":\"click\",\"x\":210,\"y\":140}]"}
{"args":["finish"]}
```

Inspect each returned image before choosing coordinates; these lines show the
wire format, not a batch to paste blindly. The relay reuses the installed Python CLI runtime
and returns decoded JSON in `result`, rather than escaped JSON in `stdout`.
Only non-JSON output falls back to `stdout`; empty stderr is omitted. It runs
directly without a shell and preserves session ownership. A fatal error stops
the relay. Continuation is the driver's own decision, never inferred from
response text: a typed preflight refusal (raised before focus/input, surfaced
as `recoverable: true, completed: 0`) or an exact transient guard refusal
(`screen changed`/`screen_changed` or `focus changed`/`focus_changed`, with no
`capture_error` or `ime_restore_failed` in the result) returns its JSON
response and keeps the relay alive.
EOF, finish, physical Esc, or a crash lets the guardian remove the overlay.
Do not automatically resume or repeat input after cancellation/failure.

Browser commands in this relay lazily start one private Node worker for the task.
It reuses the runtime and a validated CDP connection, never a cached snapshot or
page state: every command still fetches the tab list and checks the exact loopback
target, and the connection is reused only while endpoint, target id and page URL
are unchanged and the transport is healthy; an endpoint or tab change disposes the
connection and the next command builds a new one. A failed command (`ok: false`),
transport error, timeout, finish, EOF or cancellation closes the worker itself, and
the next command then reports `browser worker ended; stop this task` — start a new
session. Each browser command may carry its own `--endpoint`; an explicit
endpoint wins for that command. Without one, the relay session's retained
endpoint applies: the default `http://127.0.0.1:9222` lives for the whole
relay session, and a new relay session starts from the standalone default
again, never inheriting a previous session's retained endpoint. Only a
successful `browser start --endpoint ...` moves the retained endpoint for the
rest of the relay session; a failed start and non-start commands leave it
unchanged. Worker stderr is not discarded: the worker inherits the enclosing
session's stderr, which the MCP bridge keeps in its private per-session log,
so a worker crash leaves evidence there. Failures never restart the
worker or replay input. Browser
worker requests and responses are limited to 32 MiB; driver request lines to
8 MiB. The cold first request is not faster; standalone CLI commands keep their
one-connection-per-command behavior.

If your tool cannot keep stdin/process state between calls, run a complete task
driver inside one session instead. Do not simulate persistence with detached
sessions or manually copied session tokens.

All commands emit bounded JSON. `--actions -` accepts JSON from stdin. Prefer a JSON file for complex input; never interpolate user text into shell code.

If the caller exposes `yield_time_ms`, use a short output wait (about 250–1000 ms for short
requests, allowing for a longer drag/wait batch). A persistent driver remains alive after it
returns a response: waiting 10000 ms for it to exit adds avoidable caller latency. Consume one
response before sending the next request; wait again only while that response is pending.

### Ground once, execute, verify

- Use DOM/accessibility refs where supported. For screenshots, choose the center of a visible
  control, not its edge, and keep coordinates in the returned image's space. The executor applies
  crop offsets, resize factors and monitor origins.
- If small controls would be lost at 1280 px, choose a reliable crop or `--max-width 3840` on the
  initial observation to preserve available detail; this never creates detail absent at capture.
  With an image-viewing tool that supports it, request original detail. Avoid a second image just
  to recheck a clear large target.
- Example: in a visible Pinta canvas, plan ellipse-tool click → visible color click → Shift-drag
  a square bounding box → hand-tool click to commit. Submit one action array and inspect only
  its final result when every target is already visible and stays fixed. Setting an absolute
  visible width value is preferable to guessing how many plus clicks a previous value needs.
- An unseen fill-style popup is a real observation boundary. A selected-tool highlight is not.
  Keep the final result screenshot by default. Never use a fixed two-image ceiling to ignore
  uncertainty, errors, navigation or changed geometry.

Evidence and limits: [batching and grounding research](../../docs/research/2026-10-19-batching-grounding.md).

### Automatic duplicate-image delivery

The JSON-line driver accepts `"image_policy":"auto"` per request. The default remains `"always"`
for compatibility. `auto` adds a `visual` delivery hint without removing any observation or file:

```json
{"args":["observe","--window","0xEXACT_ADDRESS"],"image_policy":"auto"}
```

`visual.status` is `required` for the first frame, changed PNG bytes, another coordinate frame,
an error/refusal/warning, or unavailable metadata. It is `unchanged` only for identical PNG bytes
and matching window/monitor/region/size/scale/transform metadata within this session. Unknown or
nonvisual responses reset the checkpoint. The hint's `same_as` refers to the last required image.
This uses exact identity, not perceptual similarity: even a one-pixel change requires delivery.

An embedding/MCP wrapper may omit the image attachment only when `visual.status == "unchanged"`
and the image path equals `visual.path`. Keep the JSON result and fresh observation path. Send
other images normally; `image_policy: "always"` forces a repeated attachment. The local OpenCode
and CommandCode bridge enables `auto`; a plain shell caller follows the same hint when choosing
whether to view a returned file. Captures and all input guards still run. Visual identity says
nothing about invisible app state or whether the preceding action succeeded.
