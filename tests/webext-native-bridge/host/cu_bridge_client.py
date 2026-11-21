#!/usr/bin/env python3
"""Minimal loopback client for the bridge host, for manual laptop tests.

Usage:
  python3 cu_bridge_client.py --port 18711 '{"id": 1, "op": "listTabs"}'
  python3 cu_bridge_client.py --port 18711 --file request.json

Prints the reply as one JSON object and exits 0 when the reply has
"ok": true, else exits 1. Times the round trip with wall-clock and
elapsed time and prints both to stderr.
"""

import argparse
import json
import socket
import sys
import time


def main():
    parser = argparse.ArgumentParser(description="Bridge host client")
    parser.add_argument("--port", type=int, default=18711)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("request", nargs="?", help="JSON request object")
    parser.add_argument("--file", help="file holding one JSON request object")
    args = parser.parse_args()
    if args.file:
        raw = open(args.file, encoding="utf-8").read()
    elif args.request:
        raw = args.request
    else:
        parser.error("give a JSON request or --file")
    request = json.loads(raw)
    started_wall = time.time()
    started = time.monotonic()
    with socket.create_connection((args.host, args.port), timeout=35) as sock:
        sock.sendall((json.dumps(request) + "\n").encode("utf-8"))
        data = b""
        while not data.endswith(b"\n"):
            chunk = sock.recv(65536)
            if not chunk:
                break
            data += chunk
    elapsed_ms = (time.monotonic() - started) * 1000
    reply = json.loads(data.decode("utf-8"))
    print(json.dumps(reply, ensure_ascii=False))
    print(
        f"wall-clock: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(started_wall))} "
        f"elapsed_ms: {elapsed_ms:.1f}",
        file=sys.stderr,
    )
    return 0 if reply.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
