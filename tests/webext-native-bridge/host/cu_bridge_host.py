#!/usr/bin/env python3
"""Native messaging host for the computer-use WebExtension bridge.

Stdlib only. Two channels, one bridge:

- Browser side: stdin/stdout, native messaging framing. Each message is
  JSON, UTF-8 encoded, prefixed with a 32-bit unsigned length in native
  byte order. The browser launches this host when the extension calls
  runtime.connectNative("computer_use_bridge") and kills it when the
  port closes. Outbound messages (host to extension) must stay under
  1 MB; inbound messages (extension to host) may be up to 4 GB, but
  this host refuses frames over 16 MB to avoid memory exhaustion.
- Agent side: a loopback TCP server on 127.0.0.1 (port from the
  CU_BRIDGE_PORT environment variable, default 18711). The agent sends
  one JSON object per line and gets one JSON object per line back.
  Requests carry a numeric "id" and an "op"; replies carry the same
  "id" plus "ok" and "elapsed_ms" measured inside the extension, and
  "host_elapsed_ms" measured here.

Ops answered by this host without touching the browser:
  host.ping, host.status
Every other op is forwarded to the extension, which runs it in a tab
and replies. The extension id is checked when the browser passes it
as argv[2]; the expected id is cu-bridge@example.local.

Logging goes to stderr only. Stdout is the framed browser channel and
must never carry log lines.

Run directly for a protocol self-check (no browser needed):
  python3 host/cu_bridge_host.py
together with the fake-extension harness in
tests/test_webext_native_bridge.py. See README.md in this folder.
"""

import json
import os
import socket
import struct
import sys
import threading
import time

HOST_NAME = "computer_use_bridge"
EXTENSION_ID = "cu-bridge@example.local"
MAX_OUTBOUND_BYTES = 1_048_576
MAX_INBOUND_BYTES = 16_777_216
DEFAULT_PORT = 18711
DEFAULT_TIMEOUT_S = 30.0


def log(message):
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    print(f"[{stamp}] cu-bridge-host: {message}", file=sys.stderr, flush=True)


def read_exact(stream, size):
    chunks = []
    remaining = size
    while remaining > 0:
        chunk = stream.read(remaining)
        if not chunk:
            return None
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def read_message(stream):
    """Read one framed native message. Returns a dict, or None on EOF."""
    header = read_exact(stream, 4)
    if header is None:
        return None
    (length,) = struct.unpack("<I", header)
    if length > MAX_INBOUND_BYTES:
        raise ValueError(f"native message too large: {length} bytes")
    payload = read_exact(stream, length)
    if payload is None:
        return None
    return json.loads(payload.decode("utf-8"))


def encode_message(obj):
    payload = json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    if len(payload) > MAX_OUTBOUND_BYTES:
        raise ValueError(f"native message too large: {len(payload)} bytes")
    return struct.pack("<I", len(payload)) + payload


def write_message(stream, obj, lock):
    frame = encode_message(obj)
    with lock:
        stream.write(frame)
        stream.flush()


class Bridge:
    def __init__(self, in_stream, out_stream, port, timeout_s):
        self.in_stream = in_stream
        self.out_stream = out_stream
        self.port = port
        self.timeout_s = timeout_s
        self.write_lock = threading.Lock()
        self.pending = {}
        self.pending_lock = threading.Lock()
        self.stop = threading.Event()
        self.started_at = time.monotonic()
        self.timeouts = 0
        self.errors = 0
        self.server_socket = None

    def answer_locally(self, message):
        op = message.get("op")
        if op == "host.ping":
            return {"ok": True, "result": {"pong": True, "host": HOST_NAME}}
        if op == "host.status":
            return {
                "ok": True,
                "result": {
                    "host": HOST_NAME,
                    "pending": len(self.pending),
                    "uptime_s": round(time.monotonic() - self.started_at, 3),
                    "timeouts": self.timeouts,
                    "errors": self.errors,
                },
            }
        return None

    def reader_loop(self):
        try:
            while not self.stop.is_set():
                try:
                    message = read_message(self.in_stream)
                except (ValueError, json.JSONDecodeError) as error:
                    self.errors += 1
                    log(f"bad native message, skipping: {error}")
                    continue
                if message is None:
                    log("browser closed stdin, shutting down")
                    break
                if not isinstance(message, dict):
                    log("ignoring non-object native message")
                    continue
                local = None
                if message.get("op") in ("host.ping", "host.status"):
                    local = self.answer_locally(message)
                if local is not None and "id" in message:
                    local["id"] = message["id"]
                    try:
                        write_message(self.out_stream, local, self.write_lock)
                    except ValueError as error:
                        log(f"cannot answer locally: {error}")
                    continue
                msg_id = message.get("id")
                delivered = False
                if msg_id is not None:
                    with self.pending_lock:
                        entry = self.pending.pop(msg_id, None)
                    if entry is not None:
                        entry["reply"] = message
                        entry["event"].set()
                        delivered = True
                if not delivered:
                    log(f"unsolicited native message: {message}")
        except (OSError, EOFError) as error:
            log(f"native reader stopped: {error}")
        finally:
            self.stop.set()
            if self.server_socket is not None:
                try:
                    self.server_socket.close()
                except OSError:
                    pass

    def handle_agent_request(self, request):
        started = time.monotonic()
        if not isinstance(request, dict) or "id" not in request or "op" not in request:
            return {
                "id": request.get("id") if isinstance(request, dict) else None,
                "ok": False,
                "error": "request must be a JSON object with id and op",
                "host_elapsed_ms": round((time.monotonic() - started) * 1000, 1),
            }
        local = self.answer_locally(request)
        if local is not None:
            local["id"] = request["id"]
            local["host_elapsed_ms"] = round((time.monotonic() - started) * 1000, 1)
            return local
        event = threading.Event()
        entry = {"event": event, "reply": None}
        with self.pending_lock:
            self.pending[request["id"]] = entry
        try:
            write_message(self.out_stream, request, self.write_lock)
        except ValueError as error:
            with self.pending_lock:
                self.pending.pop(request["id"], None)
            self.errors += 1
            log(f"cannot forward request id={request['id']}: {error}")
            return {
                "id": request["id"],
                "ok": False,
                "error": str(error),
                "host_elapsed_ms": round((time.monotonic() - started) * 1000, 1),
            }
        except OSError as error:
            with self.pending_lock:
                self.pending.pop(request["id"], None)
            self.errors += 1
            log(f"cannot write to browser, id={request['id']}: {error}")
            return {
                "id": request["id"],
                "ok": False,
                "error": f"cannot write to browser: {error}",
                "host_elapsed_ms": round((time.monotonic() - started) * 1000, 1),
            }
        if not event.wait(timeout=self.timeout_s):
            with self.pending_lock:
                self.pending.pop(request["id"], None)
            self.timeouts += 1
            log(
                f"timed out after {self.timeout_s}s waiting for browser "
                f"reply, id={request['id']} op={request.get('op')}"
            )
            return {
                "id": request["id"],
                "ok": False,
                "error": "timed out waiting for browser reply",
                "host_elapsed_ms": round((time.monotonic() - started) * 1000, 1),
            }
        reply = entry["reply"] or {"id": request["id"], "ok": False, "error": "empty reply"}
        reply["host_elapsed_ms"] = round((time.monotonic() - started) * 1000, 1)
        return reply

    def serve_agent(self, conn):
        try:
            reader = conn.makefile("r", encoding="utf-8", errors="replace")
            writer = conn.makefile("w", encoding="utf-8")
            for line in reader:
                line = line.strip()
                if not line:
                    continue
                try:
                    request = json.loads(line)
                except json.JSONDecodeError as error:
                    writer.write(json.dumps({"id": None, "ok": False, "error": f"bad JSON: {error}"}) + "\n")
                    writer.flush()
                    continue
                reply = self.handle_agent_request(request)
                writer.write(json.dumps(reply, ensure_ascii=False) + "\n")
                writer.flush()
                if self.stop.is_set():
                    break
        except OSError as error:
            log(f"agent connection error: {error}")
        finally:
            try:
                conn.close()
            except OSError:
                pass

    def serve_forever(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", self.port))
        server.listen(4)
        self.server_socket = server
        actual_port = server.getsockname()[1]
        log(f"listening on 127.0.0.1:{actual_port}")
        print(f"cu-bridge listening on 127.0.0.1:{actual_port}", file=sys.stderr, flush=True)
        server.settimeout(0.5)
        while not self.stop.is_set():
            try:
                conn, _addr = server.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            thread = threading.Thread(target=self.serve_agent, args=(conn,), daemon=True)
            thread.start()
        try:
            server.close()
        except OSError:
            pass


def main(argv):
    if len(argv) >= 3 and argv[2] != EXTENSION_ID:
        log(f"refusing unexpected extension id: {argv[2]}")
        return 1
    try:
        port = int(os.environ.get("CU_BRIDGE_PORT", str(DEFAULT_PORT)))
    except ValueError:
        log("CU_BRIDGE_PORT must be a number")
        return 1
    try:
        timeout_s = float(os.environ.get("CU_BRIDGE_TIMEOUT_S", str(DEFAULT_TIMEOUT_S)))
    except ValueError:
        log("CU_BRIDGE_TIMEOUT_S must be a number")
        return 1
    bridge = Bridge(sys.stdin.buffer, sys.stdout.buffer, port, timeout_s)
    reader = threading.Thread(target=bridge.reader_loop, daemon=True)
    reader.start()
    bridge.serve_forever()
    reader.join(timeout=2.0)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
