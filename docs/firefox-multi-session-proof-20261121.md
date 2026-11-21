# Firefox Marionette one-session rule: raw protocol proof

Date: 2026-11-21
Test script: `tests/marionette_multi_session.py`
Primary evidence run: 2026-11-21T11:44:09Z to 11:44:16Z (UTC), exit code 0.
A second run of the same script immediately afterwards reproduced
every outcome identically.

## Claim tested

A single Firefox instance driven through Marionette allows only one
WebDriver session at a time, so two agents cannot drive the same
browser concurrently through two sessions. This test also pins down
the exact shape of the limit: is it per connection, per browser, and
what does a second client actually observe?

## Environment

- Browser: Mozilla Firefox 160.0.1, binary at
  `~/workspace/tools/firefox/firefox`, started headless with
  `-marionette` and `-no-remote` on a throwaway profile.
- Marionette port: 3849 on 127.0.0.1, chosen for this test.
- Client: a purpose-written Python 3 script speaking the raw
  Marionette wire protocol over TCP sockets (length-prefixed JSON).
  No Selenium and no geckodriver anywhere in the path.
- Handshake received from the server on an accepted connection:
  `{"applicationType": "gecko", "marionetteProtocol": 3}`.

## Method

1. Launch Firefox with Marionette enabled. The port is set through
   the `marionette.port` preference seeded in a `user.js` inside the
   throwaway profile. Note: the `--marionette-port` command line
   flag was tried first and is ignored by Firefox 160.0.1; a debug
   run with that flag logged `Marionette INFO Listening on port
   2828`, the default, and nothing ever listened on the requested
   port.
2. Connection A connects, reads the handshake, and sends
   `WebDriver:NewSession` with
   `{"capabilities": {"alwaysMatch": {"browserName": "firefox"}}}`.
3. While that session is active, A sends NewSession twice more, and
   a second TCP connection B is opened in parallel.
4. A deletes its session and creates a new one on the same
   connection. B is probed again while that second session is
   active, and once more after A deleted it but is still connected.
5. A disconnects. B, already handshaken at that point, sends
   NewSession, then deletes its session.
6. Cleanup: all sessions deleted, sockets closed, Firefox
   terminated with SIGTERM, and the script verifies the process is
   gone and port 3849 refuses new connections.

Every request and response is logged to stdout as JSONL with UTC
timestamps and per-attempt elapsed seconds.

## Results

All rows are from the primary evidence run. Elapsed is the
round-trip time of the single attempt in seconds.

| Attempt | Conn | What was tried | Outcome | Error name | Error message | Elapsed (s) |
|---|---|---|---|---|---|---|
| A1 | A | First NewSession | ok, session `3a86c86e-5546-46a2-ba34-a2ab1c8fdebc` | n/a | n/a | 4.0110 |
| A2 | A | Second NewSession, A1 active | error | `session not created` | `Maximum number of active sessions` | 0.0573 |
| A3 | A | Third NewSession, A1 active | error | `session not created` | `Maximum number of active sessions` | 0.0007 |
| B1 | B | New TCP connection while A connected, A1 active | connection closed by server, no handshake received | n/a | n/a | 0.0007 |
| A-del-1 | A | DeleteSession for A1 | ok | n/a | n/a | 0.0055 |
| A4 | A | NewSession after A1 deleted | ok, session `9502bdf7-7eed-4baf-b37a-2164d2fd1fe9` | n/a | n/a | 0.0072 |
| B2 | B | New TCP connection, A still connected, A4 active | connection closed by server, no handshake received | n/a | n/a | 0.0006 |
| A-del-2 | A | DeleteSession for A4 | ok | n/a | n/a | 0.0019 |
| B-mid | B | New TCP connection, A still connected but holding no session | handshake received (`marionetteProtocol: 3`) | n/a | n/a | 0.0006 |
| B3 | B | NewSession on B after A disconnected | ok, session `4c0dcd8e-ed96-4dfd-8534-58f67119c8e9` | n/a | n/a | 0.0038 |
| B-del | B | DeleteSession for the B session | ok | n/a | n/a | 0.0029 |

Supporting timings from the same run: process launch to port 3849
accepting connections took 1.3565 s; the handshake on connection A
took 0.3286 s; the B-mid handshake arrived at
2026-11-21T11:44:15.754157Z, just before connection A was closed at
11:44:15.754405Z, which proves B was accepted while A was still
connected. After cleanup, Firefox (pid 36826) exited on SIGTERM and
port 3849 was verified closed.

The slow first NewSession (4.0110 s) against the fast later ones
(0.0038 to 0.0072 s) is the one-time cost of creating the first
session in a freshly started browser; the rejections (A2, A3) are
answered in under 0.06 s, so the limit is enforced immediately, not
by a timeout.

## Raw log excerpt

Verbatim lines from the primary run's JSONL output:

```json
{"ts": "2026-11-21T11:44:15.736374+00:00", "event": "recv", "conn": "A", "attempt": "A2", "command": "WebDriver:NewSession", "elapsed_s": 0.0573, "outcome": "error", "error": {"error": "session not created", "message": "Maximum number of active sessions", "stacktrace_present": true}, "result": null}
{"ts": "2026-11-21T11:44:15.737910+00:00", "event": "handshake_failed", "conn": "B", "elapsed_s": 0.0004, "detail": "ConnectionError('conn B: server closed connection')"}
{"ts": "2026-11-21T11:44:15.750896+00:00", "event": "recv", "conn": "A", "attempt": "A4", "command": "WebDriver:NewSession", "elapsed_s": 0.0072, "outcome": "ok", "error": null, "result": {"sessionId": "9502bdf7-7eed-4baf-b37a-2164d2fd1fe9", "capabilities_keys": ["acceptInsecureCerts", "browserName", "browserVersion", "capabilities", "moz:accessibilityChecks", "moz:buildID", "moz:headless", "moz:platformVersion", "moz:processID", "moz:profile", "moz:shutdownTimeout", "moz:webdriverClick", "moz:windowless", "pageLoadStrategy", "platformName", "proxy", "setWindowRect", "strictFileInteractability", "timeouts", "unhandledPromptBehavior", "userAgent"], "browserName": "firefox", "browserVersion": "160.0.1"}}
{"ts": "2026-11-21T11:44:15.837482+00:00", "event": "info", "step": "firefox_exited", "pid": 36826, "returncode": -15, "still_alive": false}
{"ts": "2026-11-21T11:44:16.337941+00:00", "event": "info", "step": "port_after_exit", "port": 3849, "port_open": false}
```

The full JSONL log is the stdout of the test script; rerun it to
reproduce:

```sh
python3 tests/marionette_multi_session.py 3849
```

## Conclusion

The one-session rule is real, and its exact shape on Firefox
160.0.1 with Marionette protocol 3 is:

- Per browser instance: at most one WebDriver session can be active
  at any moment. The limit is a count of active sessions, not a
  lifetime limit: after DeleteSession, the same connection created
  a fresh session immediately (A4, new session id), and later a
  different connection did the same (B3).
- Per connection: a second NewSession on the same connection while
  a session is active is rejected with the WebDriver error
  `session not created` and the message `Maximum number of active
  sessions`. It does not queue, wait, or replace the live session.
- A second simultaneous client gets less than an error: while a
  session is active, the server accepts the TCP connection and
  closes it at once, so the client never receives the handshake and
  cannot even send a command (B1, B2). There is no error frame to
  inspect; a client library just sees the connection drop.
- The gate follows the session, not the open socket: once A had
  deleted its session, a new connection B received its handshake
  even though A was still connected (B-mid). One boundary was not
  probed: B's NewSession was sent only after A disconnected, so
  whether B could have created its session in the short window
  where A was connected but sessionless is untested.

Practical consequence for agent tooling: exactly one driver can own
a Marionette-controlled Firefox at a time. A second agent attaching
to the same browser will either fail session creation with
`session not created` (if it shares the connection path, as
geckodriver does) or see its connection dropped outright (raw
socket). Sharing one browser between two agents requires a single
session owner that multiplexes commands, or separate browser
instances with separate profiles and ports.
