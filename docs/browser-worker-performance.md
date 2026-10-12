# Session-owned browser runtime experiment

## Decision

Reuse one lazy Node runtime only inside the interactive session driver. Keep the
standalone browser CLI isolated. Do not retain a CDP WebSocket: the measured
runtime benefit is already large, and fresh connections simplify target and
disconnect handling. Every command rechecks its exact loopback target; snapshots
and page state are not cached or silently refreshed for input.

The child has no listening socket, external service or new dependency. It belongs
to the guardian's existing process group. Finish, EOF, exception, cancellation,
transport failure or an action result with `ok:false` closes it. Requests are
sequential and never replayed; the worker cannot be restarted after a failure.
The default timeout calculation is shared with the standalone path (maximum
60 seconds). Nonblocking pipe writes and polled reads check cancellation every
40 ms. Complete request/response JSON messages are bounded to 32 MiB, including
base64 images. Oversized messages stop rather than silently truncate.

## Real measurements

On an isolated Chromium fixture with 16-ref DOM observations, twenty alternating
samples per path measured:

| Path | Median | p95 |
|---|---:|---:|
| New Node process per request | 55.345 ms | 61.937 ms |
| Warm session-owned Node runtime | 3.230 ms | 4.878 ms |

The first worker request took 102.522 ms in this run. It includes cold initialization
and is not evidence of a first-command speedup. Timings include loopback discovery,
WebSocket setup, DOM snapshot and JSON transport, but not model reasoning, agent
tool overhead or image capture. No paid model API was used. Smaller command
latency does not establish model-token savings or arbitrary-app success rates.

Read-only reproduction against a locally owned inert tab:

```sh
python3 tests/control_benchmark.py --samples 20 --endpoint http://127.0.0.1:PORT --target EXACT_TAB_ID
```

The report omits target IDs, paths, window titles and screenshot contents. Results
vary with browser, page content and host load. Worker initialization adds a live
Node process for the task; it is not a machine-wide daemon.

## Verification

The real session-driver fixture filled Unicode text, clicked Save, asserted the
application result and decoded its screenshot. Six subsequent observations used
the same owned Node child (5.644 ms median including CLI/relay processing).
Finish exited the driver with code zero and the worker process was gone. These
are scripted Chromium fixture outcomes, not general computer-use success rates.
The synchronized installed copy passed the same fixture (4.688 ms median for six
warm relay observations). Final source suite: 267 tests, one optional skip,
23.892 seconds, no failures; capture/adapter regressions also passed.

```sh
computer-use session -- python3 tests/browser_driver_live.py
```

Transport regression tests use owned fake children to verify cancellation during
blocked reads/writes, cancellation before a subsequent request, oversized messages,
fragmented UTF-8/large images, EOF, malformed framing, timeout and no replay after
failure. They also verify inherited process-group ownership and restoration of
the browser binding. Node VM tests cover sequential requests and stopping queued
input after failure. Existing stale/covered-target, focus and capture checks
remain enabled; no real user accounts are touched by the fixture.
