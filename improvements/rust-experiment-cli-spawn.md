# Rust experiment: CLI-spawn replacement (W5, TRACK 1)

- Author: Luna 6 Max (W5), executor for Pham Tuan
- Date: 2026-11-18, night shift. Work log (Asia/Ho_Chi_Minh): 21:51 task
  received, repo at main 21684e7 confirmed, cargo 1.100.0 found at
  ~/.cargo/bin; 21:51-21:53 read rust-profile.md (W3), session_remote.py,
  tc02_controller.py broker driver, opt-step3-design.md; 21:53 real broker
  started on the VM (XDG_RUNTIME_DIR=/tmp/w5/rt) and live status verified;
  21:53-21:56 breakdown bench (n=21) plus importtime plus probe scripts;
  21:57-22:02 strace proof of the __main__ recompile; 22:02-22:04 Rust
  prototype written, first release build 5.7 s; 22:04-22:05 diff harness
  run 1 found two bugs (result help indent, -hx cluster); 22:05-22:06
  fixed both, rebuilt, before/after run 1 found the 100 KB JSON quadratic
  bug (Rust 181 ms); 22:06-22:07 JSON parser fixed to a linear fast run,
  rebuilt, diff 74/74, before/after run 2; 22:07-22:08 clean rebuild 7.5 s,
  final diff 74/74 on the fresh binary, this file written.
- Repo: ~/workspace/computer-use-wayland, HEAD 21684e7. Prototype:
  ~/workspace/rust-experiment-cli-spawn/ (Rust source, bench scripts,
  JSON result files, README with rebuild and rerun steps).
- Rule followed: every claim carries a measured number and a source. No
  em dash or en dash is used anywhere in this file.

## 0. Correction to the task framing: the per-step spawn is session_remote.py, not cu.py

The controller (`tc02_controller.py` `run_remote`, lines 387-405) spawns
`[sys.executable, scripts/session_remote.py, ...]` per step, never `cu.py`
directly. Each `broker_driver` cycle is two spawns: `request --lease-file
... --sequence N --request FILE` and `result --lease-file ... --sequence N`,
plus `status` polls (`auth_status`, `_ensure_clean_broker`, `start`,
`finish`). `session_remote.py` imports all of `cu` at its top
(`import cu`, line 29), so it pays the full `cu.py` import cost plus its
own. `cu.py` itself only runs once per task as the long-lived
`session-driver` child process, and its `observe`/`act`/`windows` work
happens inside that process, not in per-step spawns. So the thinnest hot
CLI path is `session_remote.py status` (one Unix-socket exchange, no lease
file), and the per-step paths are `status`/`result`/`request` with a lease
file (two exchanges each: a status exchange for the generation check, then
the command exchange). That is what was measured and what the prototype
replaces. `cu.py --help` and `cu.py status` were measured too (section 1)
for the record, but replacing `cu.py` buys nothing per step.

## 1. Per-invocation breakdown (VM-measured)

Method: wall-clock `subprocess.run` timing, n=21, medians, plus
`python3 -X importtime`, plus in-process `time.perf_counter` splits, plus
`strace` on the exact syscalls. Script: `bench/bench_breakdown.py`,
results `bench/bench-results-breakdown.json`. VM: Python 3.12.3, 4 shared
vCPU (1.5 CPU quota), same VM as W3. Live broker: real
`session_remote.py serve` on the VM at /tmp/w5/rt.

### 1.1 `session_remote.py status` against the live broker (median 107.5 ms)

| Stage | ms | How measured |
|---|---:|---|
| Process spawn plus interpreter startup | 25.5 | `python3 -c pass`, median 25.5, range 24.0-31.8 |
| Imports (`session_remote`, `cu`, stdlib, PIL, etc.) | 59.5 | `python3 -c "import session_remote"` median 85.0 minus bare 25.5; `-X importtime` cumulative for `session_remote` 53.4 ms (self 4.0 ms, the rest is its imports) |
| `__main__` source recompile (see 1.3) | 19.5 | Script-mode status 111.3 minus `-c` import-plus-main 91.8; standalone `compile()` of session_remote.py 22.5 ms over bare |
| Argparse build, dispatch, print, teardown | about 3.0 | Residual 107.5 - 25.5 - 59.5 - 19.5; in-process `main(['status'])` 1.3 ms, fresh-process delta 4.7 ms |
| Unix-socket exchange (status round trip) | 0.2 | In-process `_exchange({'command': 'status'})`, median 0.2 ms, range 0.2-0.9 |
| Total | 107.5 | Wall clock, median, range 105.6-114.1 |

The actual work is 0.2 ms out of 107.5 ms. The spawn is 99.8 percent overhead.

### 1.2 All invocation shapes (medians, n=21)

| Invocation | Python ms (median) | Range ms | Exit |
|---|---:|---:|---:|
| `python3 -c pass` (bare interpreter) | 25.5 | 24.0-31.8 | 0 |
| `python3 -c "import argparse"` | 34.0 | 32.3-44.5 | 0 |
| `python3 -c "import json, socket"` | 39.2 | 36.9-45.7 | 0 |
| `python3 -c "import cu"` | 63.1 | 60.8-70.2 | 0 |
| `python3 -c "import session_remote"` | 85.0 | 82.6-154.3 | 0 |
| `session_remote.py --help` | 109.0 | 105.8-119.4 | 0 |
| `cu.py --help` | 110.4 | 104.5-140.8 | 0 |
| `cu.py status` (local latch read, no broker) | 105.7 | 101.8-184.5 | 0 |
| `session_remote.py status`, no broker | 107.8 | 102.8-121.0 | 1 |
| `session_remote.py status`, live broker | 107.5 | 105.6-114.1 | 0 |
| `session_remote.py status --lease-file` (unknown generation) | 110.8 | 106.0-324.8 | 1 |
| `session_remote.py status --lease-file` (bad broker generation) | 108.5 | 104.9-154.0 | 1 |
| `session_remote.py status --lease-file` (malformed lease) | 107.7 | 104.5-124.8 | 1 |
| `session_remote.py result --lease-file --sequence 1` | 109.6 | 105.6-112.8 | 1 |
| `session_remote.py request --lease-file --sequence 1 --request FILE` | 107.9 | 106.2-123.7 | 1 |
| `session_remote.py status --lease-file` (missing value, argparse error) | 107.6 | 104.0-114.7 | 2 |
| `session_remote.py bogus` (argparse error) | 107.4 | 105.0-109.5 | 2 |

Every invocation costs about 105-111 ms regardless of what it does, even
an argparse error (107.6 ms) and `--help` (109.0 ms). The lease-file
variants cost the same as plain status: the second exchange adds 0.2 ms
(in-process `_client_with_lease` status 0.4 ms vs `_exchange` 0.2 ms) and
the lease read and validation are sub-millisecond. `cu.py status` is a
local latch read and still costs 105.7 ms, which confirms the cost is the
spawn, not the work.

### 1.3 The `__main__` recompile: script mode never uses the .pyc

The 19.5 ms residual was chased, not assumed. Three probes
(`bench_breakdown.py` plus scratch probes, all n=21):

- `python3 -c "import session_remote"` is 87.1 ms; the same work as
  `python3 -c "import session_remote; session_remote.main(['status'])"`
  is 91.8 ms; but `python3 session_remote.py status` is 111.3 ms. The
  19.5 ms gap is in how `__main__` loads, not in `main()`.
- Touching `session_remote.py` (invalidating its .pyc) changed nothing:
  script mode 110.1 ms before, 111.3 ms after; `-c` import mode 88.6 ms
  on the first stale-cache run, 88.5 ms after the cache rebuilt.
- `strace` settles it: script mode opens `session_remote.py` source twice
  and never opens the .pyc; import mode opens
  `__pycache__/session_remote.cpython-312.pyc` once. CPython recompiles
  the main script from source on every run. Standalone `compile()` of
  session_remote.py costs 22.5 ms over bare, matching the residual.
  For `cu.py` the same effect is larger: standalone `compile()` costs
  41.1 ms over bare, and `cu.py status` (105.7 ms) decomposes as 25.5
  interpreter plus 37.6 imports (`import cu` 63.1 minus bare 25.5) plus
  about 41 recompile plus about 1 work.

Consequence: even a perfect persistent Python client is not the only way
to kill this cost, and even a zero-import Python CLI would still pay
about 25 ms interpreter plus about 20-41 ms recompile per spawn.

## 2. What was prototyped

A minimal Rust binary (`session-remote-rs`, binary `session_remote`,
373,984 bytes stripped, release, LTO, std-only, zero crates, no network
needed to build; clean build 7.5 s, incremental 7.0 s; cargo/rustc 1.100.0).
Files: `src/main.rs` (argparse-compatible front end), `src/client.rs`
(Unix-socket exchange, lease handling, safe file reads),
`src/json.rs` (ordered JSON value, strict parser, Python-compatible
compact serializer), `src/help.rs` (exact `--help` texts, generated from
captured Python output).

Implemented, faithfully: `status [--lease-file]`, `result --lease-file
--sequence N`, `request --lease-file --sequence N --request FILE`. That is
every CLI spawn the controller makes per step. The binary reproduces the
Python wire behavior: default socket from `XDG_RUNTIME_DIR` or
`/run/user/{uid}` (relative path is `invalid_socket_path`), one JSON line
per exchange with `shutdown(SHUT_WR)`, single-newline response validation,
`broker_unavailable` on connect or I/O failure, lease read with the same
safety checks (symlink is `file_unavailable`, non-regular or group-readable
or foreign-owned is `unsafe_file`, oversize is `too_large`, bad JSON or bad
fields is `invalid_lease_file`, missing generation is
`start_outcome_unknown`, generation mismatch is `broker_changed`), request
envelope read and JSON validation, exit 0 only when the response has
`ok` true, argparse-compatible `--help` text, usage lines, and error
messages (including the quirks: unrecognized arguments report top-level
usage, required-argument errors fire before unrecognized-argument errors,
`-h` in a short cluster such as `-hx` prints help, `--sequence -1` is
accepted, `--sequence -1.5` is an invalid-int error).

Deliberately not implemented: `serve` (a daemon, not a spawn), `start`
and `finish` (once per task, with lease writes and a polling loop). They
parse exactly like Python, but execution exits 1 with a stderr note
telling the caller to use `session_remote.py`. This is a scope boundary,
not a bug; the per-step saving does not need them.

## 3. Fidelity: 74 diff cases, 74 pass, 0 fail

Method: `bench/diff_harness.py` runs the Python CLI and the Rust binary
(invoked through a symlink named `session_remote.py` so argparse `prog`
matches) on identical inputs and compares return code, stdout bytes, and
stderr bytes. Final run 22:08 on the freshly built binary: 74 pass,
0 fail. Cases: 18 live-broker and no-broker behavior cases, 8 lease-shape
cases (null generation, version 2, extra keys, mode 0644, symlink, bad
start_id, uppercase hex, `~` path), 33 argparse cases (help for all six
subcommands, unknown commands and flags, missing values, invalid ints,
repeated options, `--` handling, `-hx`/`-xh`), 3 Rust-only scope checks
(serve/start/finish refuse with the note), 2 XDG cases, 10 fake-broker
canned responses (full nested object with unicode, spaced JSON, error
object, array response, invalid JSON, two lines, no trailing newline,
closed connection, 100 KB response, non-canonical number). Full detail:
`bench/diff-report.json`.

Two known divergences, both unreachable in controller use:

1. Non-canonical number lexemes. Rust keeps number lexemes verbatim;
   Python re-serializes them (`1e2` becomes `100.0`). The broker only
   emits numbers via `json.dumps`, so its lines are already canonical.
   The diff case proves the only difference is the lexeme.
2. Relative `XDG_RUNTIME_DIR`. Python crashes with an uncaught traceback
   (the `serve --socket` default is evaluated at parser build, outside
   the `try` block), exit 1, empty stdout. Rust prints the clean error
   JSON `{"ok":false,"error":"invalid_socket_path"}`, exit 1. Same exit
   code. Replicating the traceback would embed repo paths and line
   numbers, so it is documented instead of faked.

Minor: a lease `version` of JSON `true` passes Python (`True == 1`) but
fails Rust validation. No real lease contains it.

## 4. Before/after (same inputs, same VM, interleaved runs, n=31)

Method: `bench/bench_before_after.py`, runs interleaved (Python, Rust,
Python, Rust) so shared-CPU drift hits both arms, outputs verified
byte-identical on every run (0 mismatches in all 217 pairs). Second run
reported below; the first run agreed within about 5 ms on every median.

| Case | Python median ms (range) | Rust median ms (range) | Saving ms | Speedup |
|---|---:|---:|---:|---:|
| `status`, no broker | 107.25 (103.18-130.68) | 1.74 (1.60-8.30) | 105.5 | 61.6x |
| `status`, live broker | 105.85 (102.37-174.03) | 2.18 (2.01-4.22) | 103.7 | 48.6x |
| `status --lease-file`, live broker | 109.98 (104.47-147.55) | 2.58 (2.33-5.43) | 107.4 | 42.6x |
| `result --lease-file --sequence 1` | 109.78 (105.06-141.25) | 2.58 (2.39-3.77) | 107.2 | 42.6x |
| `request --lease-file --sequence 1` | 109.05 (105.31-172.53) | 2.60 (2.37-4.16) | 106.5 | 41.9x |
| `--help` | 107.88 (105.96-129.48) | 1.65 (1.47-1.96) | 106.2 | 65.4x |
| `status`, fake broker, 100 KB response | 109.49 (104.85-188.88) | 2.64 (2.40-3.67) | 106.8 | 41.5x |

Per-spawn saving is about 104-107 ms on every path, including the 100 KB
response, so the JSON layer is not a bottleneck after the fix in section 5.

## 5. Bug found by measuring: the first JSON parser was quadratic

The first before/after run showed Rust slower than Python on the 100 KB
canned response: Rust 181.03 ms vs Python 108.89 ms. Root cause: the
string parser called `from_utf8` on the remaining input for every
character, which is O(n) per character and O(n squared) over a long
string. Fix: copy fast runs of bytes up to the next quote, backslash, or
control byte in one slice (safe because the whole input is validated as
UTF-8 up front, and delimiters are ASCII so run boundaries always fall
on char boundaries). After the fix: Rust 2.64 ms on the same 100 KB
response. The diff harness still passes 74/74 after the fix, including
the unicode and escape cases.

## 6. End-to-end impact math

Spawn count per tc02-class task: about 29 (Step 3 design: 12 task requests
times 2 spawns, plus 3 status polls, plus start, plus finish; W3: about
30). Per-spawn saving: about 105 ms VM-measured, about 118 ms on the
laptop (Step 3 design, spawn median, n=20).

| Task | Spawns | Saving (VM) | Saving (laptop extrap.) | New total |
|---|---:|---:|---:|---|
| Step 2 deterministic run A2, exec 9.5962 s | 29 | about 3.0 s | about 3.4 s | exec about 6.6 s, end-to-end 13.45 s to about 10.5 s |
| tc02-t3 model loop, 101 s, 14 requests | 28 | about 2.9 s | about 3.3 s | about 98 s, about 3 percent faster |
| H1-OPT3, 1974 s, 78 broker requests | 156 | about 16.4 s | about 18.4 s | about 1958 s, about 0.8 percent faster |

Reading this honestly:

- The Step 2 execution target of 8 s is beaten (about 6.6 s), but the
  end-to-end target of 10 s is still missed by about 0.5 s, because P0
  VS Code cold launch (3.7 s), OCR (about 2.4 s), and dialog and finish
  waits (about 1.6 s) are untouched by a CLI port.
- The model-loop task improves about 3 percent. W3's Amdahl bound holds:
  even zeroing all broker service (13.105 s) only gives 101 s to 87.9 s
  (1.15x); Rust recovers about 23 percent of that ceiling. The think
  gaps (52.8 s) and head/tail (35.1 s) dominate, and no harness port
  touches them.
- H1 improves under 1 percent. Its cost is executor deliberation, not
  transport.

### 6.1 The Rust one-shot vs Step 3 persistent stream comparison

Both attack the same about 3 s, and they do not stack. Per request, a
persistent Python client is actually faster than the one-shot Rust binary:
in-process `_exchange` is 0.2 ms and `_client_with_lease` is 0.4 ms,
against one-shot Rust at 2.2-2.6 ms (the Rust binary still pays process
spawn and dynamic linking, about 1.7 ms). The Rust one-shot wins on
deployment risk, not on per-request speed: it is a drop-in binary swap
for the controller's subprocess call, with no broker change, no protocol
change, no persistent-connection lifecycle, and no stream auth state.
Step 3 wins the last about 2 ms per request and removes the result-poll
round trip as a separate spawn, at the cost of a broker change. If Step 3
ships, this Rust binary is redundant for speed; if Step 3 stalls on risk,
this binary captures about 97 percent of the same saving with no broker
touch. A persistent Rust client would be faster than both (about 0.2 ms
per exchange with no spawn), but that is a different experiment: it needs
the same stream design Step 3 already wrote, and its win over persistent
Python would be under 0.5 ms per request, which is noise at task scale.

## 7. Corrections to the starting numbers

- W3 anchor "`cu.py --help` 179.8 ms vs bare Python 38.3 ms, so roughly
  140 ms is interpreter startup plus imports": not reproduced. My medians
  are `cu.py --help` 105.5 ms (run 1) and 110.4 ms (run 2), bare Python
  25.5-28.0 ms. W3's number was a mean of 5 and likely a cold-cache or
  loaded-VM run. My split for `cu.py` is 25.5 ms interpreter, 37.6 ms
  imports, about 41 ms `__main__` recompile, about 1 ms work. Step 3's
  independent spawn median of about 118 ms agrees with my 107-110 ms,
  so the 179.8 ms figure should not be cited.
- "About 140 ms of each spawn is interpreter plus imports": corrected to
  about 85 ms (interpreter 25.5 plus imports 59.5) for session_remote.py,
  with a further about 20 ms of `__main__` recompile that is neither.
- W3 hot path rank 1 ("about 0.32-0.33 s per request, about 3-4 s per
  task, about 30 spawns"): verified in shape, tightened in size. On this
  VM one spawn is about 107 ms, so one request cycle (2 spawns) is about
  214 ms, and 29 spawns are about 3.1 s. The laptop numbers (0.13-0.19 s
  per CLI, 0.32-0.33 s round trip) are larger, so the laptop saving is
  about 3.4 s, not 3.0 s. Either way the rank 1 conclusion stands: the
  spawn is the largest task-level harness cost.

## 8. Sources

- improvements/rust-profile.md (W3): hot-path ranking, tc02-t3 and Step 2
  decompositions, 1127-test caveat, observation-store port candidate.
- improvements/opt-step2-report.md: Step 2 gate runs (A2 exec 9.5962 s,
  end-to-end 13.4469 s), per-request floor, step spans, OCR times.
- improvements/opt-step3-design.md: Step 3 persistent-stream design,
  spawn median about 118 ms (n=20), 12 task requests plus 3 status polls
  plus start and finish per run, poll sleep already gone.
- improvements/10x-executor-time.md: tc02-t3 gaps 52.813 s, service
  13.105 s, head/tail 35.082 s.
- VM measurements: bench/bench-results-breakdown.json (n=21),
  bench/bench-results-before-after.json (n=31, two runs),
  bench/diff-report.json (74 cases), plus scratch probes and strace runs
  in /tmp/w5 (probe.py, probe2.py, probe3.py, probe4.py, strace-script.txt,
  strace-import.txt).
- Repo code at HEAD 21684e7: scripts/session_remote.py (exchange line
  1273, client lines 1412-1461, main lines 1468-1555), scripts/cu.py
  (main lines 1915-2158), scripts/tc02_controller.py (run_remote lines
  387-405, broker_driver lines 471-527).
