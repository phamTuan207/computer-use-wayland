#!/usr/bin/env python3
"""Talk raw Marionette (21/11/2026, Worker P).
The Marionette wire protocol frames messages as <decimal-len>:<json>,
and commands are arrays [0, msg-id, name, params]. Responses are
[1, msg-id, result-or-error, value].
Usage:
  python3 recover_marionette.py status   # greeting + try NewSession
  python3 recover_marionette.py newsession # create a session, print id
  python3 recover_marionette.py delete <session-id>
"""
import json
import socket
import sys


def recv_msg(s):
    buf = b""
    while b":" not in buf:
        chunk = s.recv(1)
        if not chunk:
            raise RuntimeError("eof before length prefix")
        buf += chunk
    n = int(buf.split(b":")[0])
    body = buf.split(b":", 1)[1]
    while len(body) < n:
        chunk = s.recv(n - len(body))
        if not chunk:
            raise RuntimeError("eof in body")
        body += chunk
    return json.loads(body.decode())


def send_msg(s, obj):
    data = json.dumps(obj).encode()
    s.sendall(str(len(data)).encode() + b":" + data)


def connect():
    s = socket.create_connection(("127.0.0.1", 2828), timeout=10)
    s.settimeout(10)
    greet = recv_msg(s)
    print("GREETING:", json.dumps(greet), flush=True)
    return s


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "status"
    s = connect()
    if mode == "newsession":
        send_msg(s, [0, 1, "WebDriver:NewSession",
                     {"capabilities": {"alwaysMatch": {"browserName": "firefox"}}}])
        r = recv_msg(s)
        print("NEWSESSION:", json.dumps(r)[:600], flush=True)
        # Leave the session alive for the caller to use; print its id.
        if r[2] is None and isinstance(r[3], dict):
            print("SESSION_ID:", r[3].get("sessionId"), flush=True)
    elif mode == "delete":
        sid = sys.argv[2]
        send_msg(s, [0, 2, "WebDriver:DeleteSession", {"sessionId": sid}])
        print("DELETE:", json.dumps(recv_msg(s))[:300], flush=True)
    else:
        print("status: Marionette reachable; use newsession/delete.", flush=True)
    s.close()


if __name__ == "__main__":
    main()
