#!/usr/bin/env python3
"""Small MCP server for computer-use-wayland. Stdlib only.

Exposes the repo's main ops as named MCP tools over stdio (newline
delimited JSON-RPC, the same framing as scripts/mcp_bridge.py):

  session_start, session_status, session_finish,
  locate, click, type, screenshot, overlay

How it reuses repo code, by op:

- session_*: scripts/session_manager.py (SessionManager) enforces the
  one owner rule and logs every open and close. The live browser
  session itself is scripts/zen_dom.py (ZenSession, Marionette over
  WebDriver), which deletes the session in a finally block.
- locate: ZenSession.locate, exact rect from getBoundingClientRect.
- click: the repo hybrid from zen_dom.py. Locate through the DOM,
  then a REAL mouse click at the rect center through the native
  pointer binary in scripts/cu.py (cu.Pointer), with the same
  cursor position check the repo uses: after the absolute move the
  cursor must be within 3 px of the target or the click is refused.
  Never a DOM click: BiDi click failed to fire a handler and
  Marionette click fails on windowed Zen, see zen_dom.py.
- type: ZenSession.evaluate, the reliable read/write path. Focus the
  element, set the value through the native setter, dispatch input
  and change events. Returns the value before and after.
- screenshot: WebDriver screenshot endpoint through ZenSession,
  returned as MCP image content (base64 PNG).
- overlay: scripts/overlay.py add_holder, remove_holder, load_holders.
  Acquire shows the computer-use pill, release hides it when the
  last holder leaves.

Transport and safety:

- Local stdio only. There is no network listener, no auth, and no
  token. Never put this server on a network, never expose its stdio
  to another machine, and never run it as root.
- At most one live browser session. A second session_start fails
  until session_finish closes the first.
- The server only talks to the Zen that scripts/zen_dom.py connects
  to: the Zen instance with Marionette on 127.0.0.1:2828. Enable
  Marionette only on a dedicated test Zen, never on a daily use Zen.
- Tool errors come back as MCP results with isError true, never as
  crashes. Protocol errors come back as JSON-RPC errors. Typed text
  is never written to any log; only the tool name and elapsed time
  are logged to stderr.
- --fake runs a test-only in-memory backend with a fake DOM. It
  proves the tool plumbing without a browser. Never use --fake to
  claim a real browser result.

Usage:
  python3 scripts/mcp_server.py [--fake]
  python3 scripts/mcp_server.py --help

Environment: ZEN_MARIONETTE_PORT, ZEN_WD_PORT, ZEN_GECKODRIVER,
as in scripts/zen_dom.py.
"""
import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import session_manager
import zen_dom

MAX_LINE_BYTES = 8 * 1024 * 1024
MAX_SELECTOR_CHARS = 1000
MAX_TEXT_CHARS = 10000
MAX_AGENT_CHARS = 80
PROTOCOL_VERSION = "2024-11-05"
# Protocol versions this server accepts at initialize. Anything else
# is rejected with a JSON-RPC error. These are the real published
# MCP protocol versions; the server answers with the negotiated one.
SUPPORTED_PROTOCOL_VERSIONS = ("2024-11-05", "2025-03-26", "2025-06-18")
SERVER_NAME = "computer-use-mcp"
SERVER_VERSION = "0.1.0"

# JS used by ZenBackend.type. Branch on the element kind: the native
# value setter of HTMLInputElement throws "Illegal invocation" when
# called on a textarea or a contenteditable element, so each kind
# gets its own setter, and contenteditable gets textContent.
# Runs through ZenSession.evaluate with arguments [selector, text].
TYPE_JS = (
    "const el = document.querySelector(arguments[0]);"
    " if (!el) return {found: false};"
    " const isInput = el instanceof window.HTMLInputElement;"
    " const isTextarea = el instanceof window.HTMLTextAreaElement;"
    " const read = () => el.isContentEditable ? el.textContent : el.value;"
    " const before = read();"
    " el.focus();"
    " if (isInput) {"
    " const setter = Object.getOwnPropertyDescriptor("
    " window.HTMLInputElement.prototype, 'value');"
    " if (setter) setter.set.call(el, arguments[1]);"
    " else el.value = arguments[1];"
    " } else if (isTextarea) {"
    " const setter = Object.getOwnPropertyDescriptor("
    " window.HTMLTextAreaElement.prototype, 'value');"
    " if (setter) setter.set.call(el, arguments[1]);"
    " else el.value = arguments[1];"
    " } else if (el.isContentEditable) {"
    " el.textContent = arguments[1];"
    " } else if ('value' in el) {"
    " el.value = arguments[1];"
    " } else {"
    " el.textContent = arguments[1];"
    " }"
    " el.dispatchEvent(new Event('input', {bubbles: true}));"
    " el.dispatchEvent(new Event('change', {bubbles: true}));"
    " return {found: true, before: before, after: read()};")

# 1x1 transparent PNG, used only by the fake backend screenshot.
_FAKE_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8"
    "/x8AAwMCAO+ip1sAAAAASUVORK5CYII="
)


class ToolError(RuntimeError):
    """A tool call failed. Reported as an MCP result with isError."""


def log_event(event, **fields):
    record = {"time": time.time(), "event": event}
    record.update(fields)
    try:
        sys.stderr.write(json.dumps(record, ensure_ascii=False) + "\n")
        sys.stderr.flush()
    except Exception:
        pass


def _require_str(args, name, max_chars=None):
    value = args.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ToolError("%s must be a non-empty string" % name)
    if max_chars is not None and len(value) > max_chars:
        raise ToolError("%s is longer than %d characters"
                        % (name, max_chars))
    return value


def _optional_int(args, name, default, low, high):
    value = args.get(name, default)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ToolError("%s must be an integer" % name)
    if value < low or value > high:
        raise ToolError("%s must be between %d and %d"
                        % (name, low, high))
    return value


class ZenBackend:
    """Live backend: SessionManager lock plus a ZenSession."""

    def __init__(self):
        self.manager = session_manager.SessionManager()
        self.zen = None
        self.session_id = None

    def session_start(self, args):
        if self.zen is not None:
            raise ToolError("a session is already active; "
                            "call session_finish first")
        timeout_s = _optional_int(args, "timeout_s", 10, 1, 120)
        marionette_port = _optional_int(
            args, "marionette_port", zen_dom.DEFAULT_MARIONETTE_PORT, 1, 65535)
        wd_port = _optional_int(
            args, "wd_port", zen_dom.DEFAULT_WD_PORT, 1, 65535)
        try:
            self.manager.acquire(timeout_s=timeout_s)
        except session_manager.SessionBusy as exc:
            raise ToolError(str(exc)) from exc
        zen = zen_dom.ZenSession(marionette_port=marionette_port,
                                 wd_port=wd_port, timeout_s=timeout_s)
        try:
            zen.__enter__()
        except Exception as exc:
            self.manager.release()
            raise ToolError("could not start Zen session: %s" % exc) from exc
        self.zen = zen
        self.session_id = zen.session
        try:
            self.manager.record_open(self.session_id, kind="mcp-zen",
                                     port=wd_port)
        except Exception as exc:
            # record_open failed after the Zen session was created.
            # Without a rollback the live session and the lock stay
            # held while the caller was told the start failed, so
            # nobody ever calls session_finish: the single remote
            # session slot leaks until Zen restarts. Close the Zen
            # session, release the lock, clear our state, then fail.
            try:
                zen.__exit__(None, None, None)
            finally:
                self.zen = None
                self.session_id = None
                self.manager.release()
            raise ToolError("could not record Zen session: %s"
                            % exc) from exc
        return {"ok": True, "session": "active",
                "session_id": self.session_id,
                "marionette_port": marionette_port, "wd_port": wd_port}

    def session_status(self, args):
        hung = self.manager.detect_hung()
        return {"ok": True, "session_active": self.zen is not None,
                "session_id": self.session_id,
                "manager": self.manager.status(),
                "hung_detected": hung is not None}

    def session_finish(self, args):
        if self.zen is None:
            return {"ok": True, "session": "inactive",
                    "already_finished": True}
        try:
            self.zen.__exit__(None, None, None)
        finally:
            self.zen = None
            self.manager.record_close(self.session_id, reason="finish")
            self.session_id = None
            self.manager.release()
        return {"ok": True, "session": "inactive"}

    def _need_session(self):
        if self.zen is None:
            raise ToolError("no live session; call session_start first")
        return self.zen

    def locate(self, args):
        selector = _require_str(args, "selector", MAX_SELECTOR_CHARS)
        zen = self._need_session()
        try:
            rect = zen.locate(selector)
        except Exception as exc:
            raise ToolError("locate failed: %s" % exc) from exc
        if rect is None:
            raise ToolError("no element matches selector")
        return {"ok": True, "selector": selector, "rect": rect}

    def click(self, args):
        selector = _require_str(args, "selector", MAX_SELECTOR_CHARS)
        zen = self._need_session()
        try:
            rect = zen.locate(selector)
        except Exception as exc:
            raise ToolError("locate failed: %s" % exc) from exc
        if rect is None:
            raise ToolError("no element matches selector")
        center_x = rect["center_x"]
        center_y = rect["center_y"]
        self._real_click(center_x, center_y)
        return {"ok": True, "selector": selector,
                "clicked_at": {"x": center_x, "y": center_y},
                "rect": rect}

    def _real_click(self, x, y):
        """Real mouse click at CSS pixel x, y, via scripts/cu.py.

        Same guard as cu.py: move the pointer with an absolute move,
        read the cursor back, and refuse the click when the cursor is
        more than 3 px from the target. Needs a Wayland session with
        the native pointer binary; without one this raises a clear
        error instead of pretending to click.
        """
        import math
        import cu
        try:
            env = cu.environment()
            monitors = cu.hypr(env, "monitors")
        except Exception as exc:
            raise ToolError("real click needs a Wayland session: %s"
                            % exc) from exc
        pos = cu.hypr(env, "cursorpos")
        monitor = None
        for m in monitors:
            box = cu.monitor_box(m)
            if (box[0] <= pos["x"] < box[0] + box[2]
                    and box[1] <= pos["y"] < box[1] + box[3]):
                monitor = box
                break
        if monitor is None:
            raise ToolError("cursor is not on any known monitor")
        mx, my, mw, mh = monitor
        pointer = cu.Pointer(env, None)
        try:
            pointer.command(
                "abs %d %d 1000000 1000000"
                % (round((x - mx) / mw * 1000000),
                   round((y - my) / mh * 1000000)))
            after = cu.hypr(env, "cursorpos")
            if math.hypot(after["x"] - x, after["y"] - y) > 3:
                raise ToolError(
                    "pointer missed target; refusing click")
            pointer.command("button 1 1")
            pointer.command("button 1 0")
        finally:
            pointer.close()

    def type(self, args):
        selector = _require_str(args, "selector", MAX_SELECTOR_CHARS)
        text = _require_str(args, "text", MAX_TEXT_CHARS)
        zen = self._need_session()
        try:
            result = zen.evaluate(TYPE_JS, [selector, text])
        except Exception as exc:
            raise ToolError("type failed: %s" % exc) from exc
        if not result.get("found"):
            raise ToolError("no element matches selector")
        return {"ok": True, "selector": selector,
                "before": result.get("before"),
                "after": result.get("after")}

    def screenshot(self, args):
        zen = self._need_session()
        try:
            shot = zen._wd("GET", "/session/%s/screenshot" % zen.session)
        except Exception as exc:
            raise ToolError("screenshot failed: %s" % exc) from exc
        data = shot.get("value")
        if not isinstance(data, str) or not data:
            raise ToolError("screenshot returned no image data")
        return {"ok": True, "image_base64": data, "mime_type": "image/png"}

    def overlay(self, args):
        action = _require_str(args, "action")
        if action not in ("acquire", "release", "status"):
            raise ToolError("action must be acquire, release, or status")
        import overlay
        if action == "status":
            return {"ok": True, "holders": overlay.load_holders()}
        agent = _require_str(args, "agent", MAX_AGENT_CHARS)
        method = _require_str(args, "method", MAX_AGENT_CHARS)
        if action == "acquire":
            try:
                holders, is_new = overlay.add_holder(agent, method)
                overlay._ensure_daemon()
            except Exception as exc:
                raise ToolError("overlay acquire failed: %s" % exc) from exc
            return {"ok": True, "acquired": True, "is_new": is_new,
                    "holders": holders}
        holders, was_present = overlay.remove_holder(agent)
        return {"ok": True, "released": True,
                "was_present": was_present, "holders": holders}

    def close(self):
        if self.zen is not None:
            try:
                self.zen.__exit__(None, None, None)
            except Exception:
                pass
            finally:
                self.zen = None
                try:
                    self.manager.record_close(self.session_id,
                                              reason="server exit")
                except Exception:
                    pass
                self.session_id = None
                self.manager.release()


class FakeBackend:
    """Test-only in-memory backend. No browser, no Wayland.

    Fake DOM: two elements, a counter button and a text input.
    Clicking the button increments the counter. Typing sets the
    input value. Screenshot returns a 1x1 PNG.
    """

    def __init__(self):
        self.active = False
        self.session_id = None
        self.counter = 0
        self.elements = {
            "#count-btn": {"x": 100, "y": 50, "width": 80, "height": 30,
                           "center_x": 140, "center_y": 65},
            "#name": {"x": 100, "y": 100, "width": 200, "height": 24,
                      "center_x": 200, "center_y": 112, "value": ""},
            "#notes": {"x": 100, "y": 140, "width": 200, "height": 60,
                       "center_x": 200, "center_y": 170, "value": "",
                       "kind": "textarea"},
            "#editor": {"x": 100, "y": 220, "width": 200, "height": 60,
                        "center_x": 200, "center_y": 250, "text": "",
                        "kind": "contenteditable"},
        }
        self.last_click = None
        self.holders = {}

    def session_start(self, args):
        if self.active:
            raise ToolError("a session is already active; "
                            "call session_finish first")
        self.active = True
        self.session_id = "fake-1"
        return {"ok": True, "session": "active",
                "session_id": self.session_id,
                "backend": "fake"}

    def session_status(self, args):
        return {"ok": True, "session_active": self.active,
                "session_id": self.session_id, "backend": "fake",
                "hung_detected": False}

    def session_finish(self, args):
        if not self.active:
            return {"ok": True, "session": "inactive",
                    "already_finished": True}
        self.active = False
        self.session_id = None
        return {"ok": True, "session": "inactive"}

    def _need_session(self):
        if not self.active:
            raise ToolError("no live session; call session_start first")

    def locate(self, args):
        selector = _require_str(args, "selector", MAX_SELECTOR_CHARS)
        self._need_session()
        rect = self.elements.get(selector)
        if rect is None:
            raise ToolError("no element matches selector")
        return {"ok": True, "selector": selector, "rect": dict(rect)}

    def click(self, args):
        selector = _require_str(args, "selector", MAX_SELECTOR_CHARS)
        self._need_session()
        rect = self.elements.get(selector)
        if rect is None:
            raise ToolError("no element matches selector")
        self.last_click = {"selector": selector,
                           "x": rect["center_x"], "y": rect["center_y"]}
        if selector == "#count-btn":
            self.counter += 1
        return {"ok": True, "selector": selector,
                "clicked_at": {"x": rect["center_x"],
                               "y": rect["center_y"]},
                "rect": dict(rect), "counter": self.counter}

    def type(self, args):
        selector = _require_str(args, "selector", MAX_SELECTOR_CHARS)
        text = _require_str(args, "text", MAX_TEXT_CHARS)
        self._need_session()
        element = self.elements.get(selector)
        if element is None:
            raise ToolError("no element matches selector")
        # Mirror the live TYPE_JS read path: a contenteditable
        # element has no value, its text lives in textContent.
        if element.get("kind") == "contenteditable":
            before = element.get("text", "")
            element["text"] = text
        else:
            before = element.get("value", "")
            element["value"] = text
        return {"ok": True, "selector": selector,
                "before": before, "after": text}

    def screenshot(self, args):
        self._need_session()
        return {"ok": True, "image_base64": _FAKE_PNG_B64,
                "mime_type": "image/png"}

    def overlay(self, args):
        action = _require_str(args, "action")
        if action not in ("acquire", "release", "status"):
            raise ToolError("action must be acquire, release, or status")
        if action == "status":
            return {"ok": True, "holders": dict(self.holders)}
        agent = _require_str(args, "agent", MAX_AGENT_CHARS)
        method = _require_str(args, "method", MAX_AGENT_CHARS)
        if action == "acquire":
            is_new = agent not in self.holders
            self.holders[agent] = {"agent": agent, "method": method}
            return {"ok": True, "acquired": True, "is_new": is_new,
                    "holders": dict(self.holders)}
        was_present = agent in self.holders
        self.holders.pop(agent, None)
        return {"ok": True, "released": True,
                "was_present": was_present, "holders": dict(self.holders)}

    def close(self):
        self.active = False
        self.session_id = None


TOOLS = [
    ("session_start", "Open the single Zen session. Fails when one "
     "is already active.",
     {"type": "object",
      "properties": {
          "marionette_port": {"type": "integer"},
          "wd_port": {"type": "integer"},
          "timeout_s": {"type": "integer", "default": 10}},
      "required": []}),
    ("session_status", "Report whether a session is active, plus the "
     "session manager state.",
     {"type": "object", "properties": {}, "required": []}),
    ("session_finish", "Close the live session and release the "
     "single-owner lock. Safe to call twice.",
     {"type": "object", "properties": {}, "required": []}),
    ("locate", "Return the exact rect of an element by CSS selector, "
     "from getBoundingClientRect.",
     {"type": "object",
      "properties": {"selector": {"type": "string"}},
      "required": ["selector"]}),
    ("click", "Locate an element through the DOM, then send a REAL "
     "mouse click at its center through the native pointer, with a "
     "cursor position check. Never a DOM click.",
     {"type": "object",
      "properties": {"selector": {"type": "string"}},
      "required": ["selector"]}),
    ("type", "Type text into an element: focus, set the value through "
     "the native setter, dispatch input and change events.",
     {"type": "object",
      "properties": {"selector": {"type": "string"},
                     "text": {"type": "string"}},
      "required": ["selector", "text"]}),
    ("screenshot", "Take a screenshot of the current tab through "
     "WebDriver, returned as MCP image content.",
     {"type": "object", "properties": {}, "required": []}),
    ("overlay", "Show, hide, or report the computer-use pill. "
     "action is acquire, release, or status.",
     {"type": "object",
      "properties": {"action": {"type": "string"},
                     "agent": {"type": "string"},
                     "method": {"type": "string"}},
      "required": ["action"]}),
]


class Server:
    def __init__(self, backend):
        self.backend = backend
        self.methods = {
            "session_start": backend.session_start,
            "session_status": backend.session_status,
            "session_finish": backend.session_finish,
            "locate": backend.locate,
            "click": backend.click,
            "type": backend.type,
            "screenshot": backend.screenshot,
            "overlay": backend.overlay,
        }

    def tools_list(self):
        return {"tools": [
            {"name": name, "description": desc, "inputSchema": schema}
            for name, desc, schema in TOOLS]}

    def call_tool(self, params):
        if not isinstance(params, dict):
            raise ToolError("tools/call params must be an object")
        name = params.get("name")
        if name not in self.methods:
            raise ToolError("unknown tool: %s" % (name,))
        args = params.get("arguments", {})
        if not isinstance(args, dict):
            raise ToolError("arguments must be an object")
        started = time.monotonic()
        try:
            value = self.methods[name](args)
        except ToolError:
            raise
        except Exception as exc:
            raise ToolError(str(exc) or exc.__class__.__name__) from exc
        finally:
            log_event("tool_call", tool=str(name),
                      elapsed_ms=round((time.monotonic() - started) * 1000))
        content = [{"type": "text",
                    "text": json.dumps(value, ensure_ascii=False)}]
        image = value.get("image_base64")
        if isinstance(image, str) and image:
            try:
                image_bytes = len(base64.b64decode(image, validate=True))
            except Exception as exc:
                # A bad payload used to raise here, outside the tool
                # error handler, and surface as a JSON-RPC protocol
                # error. Report it as a tool error result instead.
                raise ToolError("tool returned invalid base64 image: %s"
                                % exc) from exc
            content.append({"type": "image", "data": image,
                            "mimeType": value.get("mime_type",
                                                  "image/png")})
            content[0]["text"] = json.dumps(
                {"ok": value.get("ok", True),
                 "mime_type": value.get("mime_type", "image/png"),
                 "image_bytes": image_bytes},
                ensure_ascii=False)
        return {"content": content}

    def handle(self, message):
        """Return a JSON-RPC response dict, or None for notifications."""
        if not isinstance(message, dict):
            raise ValueError("message must be a JSON object")
        method = message.get("method")
        ident = message.get("id")
        if method in ("notifications/initialized",
                      "notifications/cancelled"):
            return None
        if method == "initialize":
            params = message.get("params", {})
            if not isinstance(params, dict):
                raise ValueError("initialize params must be an object")
            version = params.get("protocolVersion", PROTOCOL_VERSION)
            if version not in SUPPORTED_PROTOCOL_VERSIONS:
                raise ValueError(
                    "unsupported protocol version: %s" % (version,))
            return {"protocolVersion": version,
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": SERVER_NAME,
                                   "version": SERVER_VERSION}}
        if method == "ping":
            return {}
        if method == "tools/list":
            return self.tools_list()
        if method == "tools/call":
            try:
                return self.call_tool(message.get("params", {}))
            except ToolError as exc:
                result = {"content": [{"type": "text", "text":
                                       json.dumps({"ok": False,
                                                   "error": str(exc)},
                                                  ensure_ascii=False)}],
                          "isError": True}
                return result
        if ident is None:
            return None
        raise ValueError("unknown method: %s" % (method,))

    @staticmethod
    def _write_error(ident, code, message):
        sys.stdout.buffer.write(json.dumps(
            {"jsonrpc": "2.0", "id": ident,
             "error": {"code": code, "message": message}}).encode()
            + b"\n")
        sys.stdout.buffer.flush()

    def _drain_line(self, line):
        """Consume the rest of an overlong input line, so the next
        read starts at a message boundary."""
        while not line.endswith(b"\n"):
            chunk = sys.stdin.buffer.readline(MAX_LINE_BYTES + 1)
            if not chunk:
                break
            line = chunk

    def serve(self):
        while True:
            line = sys.stdin.buffer.readline(MAX_LINE_BYTES + 1)
            if not line:
                break
            if len(line) > MAX_LINE_BYTES:
                # A single input line over the limit used to raise
                # ValueError and kill the server with exit 1. Drain
                # the rest, answer with a JSON-RPC error, keep serving.
                self._drain_line(line)
                self._write_error(None, -32700,
                                  "message exceeds maximum size")
                continue
            try:
                message = json.loads(line)
            except ValueError as exc:
                self._write_error(None, -32700,
                                  "parse error: %s" % exc)
                continue
            ident = message.get("id") if isinstance(message, dict) else None
            try:
                result = self.handle(message)
            except Exception as exc:
                if ident is None:
                    continue
                text = str(exc)
                if "unknown method" in text:
                    code = -32601
                elif "unsupported protocol version" in text:
                    code = -32602
                else:
                    code = -32000
                self._write_error(ident, code, text)
                continue
            if result is None or ident is None:
                continue
            sys.stdout.buffer.write(json.dumps(
                {"jsonrpc": "2.0", "id": ident, "result": result},
                ensure_ascii=False).encode() + b"\n")
            sys.stdout.buffer.flush()


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Small local MCP server for computer-use-wayland.")
    parser.add_argument("--fake", action="store_true",
                        help="test-only in-memory backend, no browser")
    args = parser.parse_args(argv)
    backend = FakeBackend() if args.fake else ZenBackend()
    server = Server(backend)
    try:
        server.serve()
    finally:
        try:
            backend.close()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
