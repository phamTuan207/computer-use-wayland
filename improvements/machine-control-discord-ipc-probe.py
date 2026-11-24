#!/usr/bin/env python3
"""Discord IPC probe (read-only check, no activity sent).

Probes the Discord Rich Presence IPC socket that the desktop client
exposes while it runs: $XDG_RUNTIME_DIR/discord-ipc-0 (Unix socket).
Protocol (from Discord's RPC docs and from the working service at
/home/james/.local/share/discord-window-presence/main.py, which uses
the same handshake): connect, send opcode 0 handshake
{"v": 1, "client_id": ...}, expect a READY event back. This script
stops after the handshake: it never sends SET_ACTIVITY, never writes
any presence, and never touches Discord's config or message store.

Usage:
  python3 discord_ipc_probe.py [--client-id ID]

Exit 0: socket exists and handshake returned READY (Discord running,
IPC reachable). Exit 1: Discord not running / socket absent.
Exit 2: socket exists but handshake failed (Discord running, IPC
refusing this client id or protocol mismatch).

Known client ids on this machine (from discord-window-presence):
  codex 1517375602662051900, opencode 1538957549364322404,
  claude 1521213655092428923. Default here is the codex id.
"""
import argparse
import json
import os
import socket
import struct
import sys

DEFAULT_CLIENT_ID = "1517375602662051900"  # codex, from discord-window-presence


def main():
    parser = argparse.ArgumentParser(description="Probe Discord IPC socket (read-only).")
    parser.add_argument("--client-id", default=DEFAULT_CLIENT_ID)
    args = parser.parse_args()

    path = os.path.join(
        os.environ.get("XDG_RUNTIME_DIR", "/run/user/" + str(os.getuid())),
        "discord-ipc-0",
    )
    if not os.path.exists(path):
        print(json.dumps({"ok": False, "running": False, "socket": path,
                          "error": "socket absent, Discord not running"}))
        return 1

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        sock.connect(path)
        data = json.dumps({"v": 1, "client_id": args.client_id},
                          separators=(",", ":")).encode()
        sock.sendall(struct.pack("<II", 0, len(data)) + data)
        header = sock.recv(8)
        if len(header) != 8:
            raise OSError("handshake reply missing header")
        _, length = struct.unpack("<II", header)
        body = b""
        while len(body) < length:
            chunk = sock.recv(length - len(body))
            if not chunk:
                raise OSError("handshake reply truncated")
            body += chunk
        reply = json.loads(body)
        if reply.get("evt") != "READY":
            print(json.dumps({"ok": False, "running": True, "socket": path,
                              "error": "handshake did not return READY",
                              "reply": reply}))
            return 2
        print(json.dumps({"ok": True, "running": True, "socket": path,
                          "user": reply.get("data", {}).get("user", {})}))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "running": True, "socket": path,
                          "error": "handshake failed: " + str(exc)}))
        return 2
    finally:
        sock.close()


if __name__ == "__main__":
    sys.exit(main())
