# rust-anything: read, install, verify

Author: Luna 6 Max (W1-RELAUNCH, TRACK 1 of the fastest possible program)
Date: 2026-11-18, work done 21:37 to 21:52 Asia/Ho_Chi_Minh
Repo read: `~/workspace/rust-anything`, HEAD `a827562`, version 1.5.1 (`Cargo.toml:3`)
Toolchain on this VM: cargo 1.100.0, rustc 1.100.0, stable-x86_64-unknown-linux-gnu, Python 3.12.3, 4 CPUs
Deliverable status: installed, built, verified end to end on a fresh module. No git push made, no laptop touched, no ydotool used.

## Work log (wall clock, Asia/Ho_Chi_Minh)

- 21:37:55, toolchain confirmed: cargo 1.100.0, rustc 1.100.0, stable toolchain present.
- 21:37:58 to 21:42:24, `cargo build --release` in `~/workspace/rust-anything`, finished in 4m 25s. Binary `target/release/rust-anything`, 22,215,872 bytes, reports version 1.5.1.
- 21:42:39 to 21:43:38, `rust-anything build .` in `demo/fixtures/python-textkit-rs`, 59s, produced `python/textkit_rs/_native.abi3.so`.
- 21:43:41, `rust-anything diff .` on the fixture: 1144/1144 cases match.
- 21:43:43, `rust-anything bench .` on the fixture: overall 1.04x geometric mean, verdict "Do not ship this unit for speed".
- 21:43:46 to 21:43:53, `python3 bench_batch.py` four runs: 7.3x, 3.1x, 4.8x, 17.0x.
- 21:44:01, fresh end to end module `/tmp/ra-e2e/sample.py`: `analyze` rated it ready, readiness 99, bridge PyO3.
- 21:44:13 and 21:44:55, `record` killed twice by the Linux OOM killer (SIGKILL, signal 9). Root cause found and fixed, see Appendix B.
- 21:45:44, `record` after the fix: 344 cases (76 threw), 0 timed out.
- 21:46:13, `build` 26s, `diff`: 344/344 cases match.
- 21:46:14, `bench`: overall 0.76x, verdict "Do not ship this unit for speed".
- 21:46:39, `gate`: 10 of 11 checks pass, clippy failed on my own hand-written range check.
- 21:46:50, `gate` after a one-line fix: all 11 checks pass, "Gate passed."
- 21:46:53 to 21:47:25, async probe: `async def` bridges but the generated bindings do not compile (E0277). Proven, not guessed, see Section 2.
- 21:47:35 to 21:49:12, `cargo test --release --lib`: 133 passed, 0 failed.
- `git status` in `~/workspace/rust-anything` after all verification: clean. Build outputs are gitignored.

## 1. How it works, step by step

### 1.1 The idea in one paragraph

rust-anything does not translate code. It records what the original Python (or TS, C, Go, Ruby, Java) does on generated inputs, then checks a hand-written Rust port against that recording at every step. The original stays the source of truth and the source of the API: callers keep importing the same names. The loop is `profile, analyze, bridge, record, port.rs, build, diff, bench, shadow, gate` (`README.md`, "The loop" table; `rust-anything --help` prints the same order). A whole app goes through the same loop unit by unit behind a Rust front door (`app record`, `app replay`, `app front-door`, `app wire`, `app lift`).

### 1.2 The exact commands for a Python function

These are the commands I ran on a fresh module, `/tmp/ra-e2e/sample.py` (3 pure functions: `shout`, `safe_div`, `word_count`). They are the recipe for any Python function.

```sh
rust-anything analyze /tmp/ra-e2e
# Plan: sample.py, 9 lines, wave 0, priority 51, readiness 99, bridge PyO3.
# Risk listed: Exceptions x1 at sample.py:10.

rust-anything bridge /tmp/ra-e2e sample.py
# Created /tmp/ra-e2e/rust/sample-rs (Pyo3) for shout, safe_div, word_count.
# Files: Cargo.toml, src/lib.rs, src/port.rs, python/sample_rs/__init__.py,
#   .gitignore, README.md, rust-anything.json, build.rs.

# Write the Rust port in src/port.rs only. lib.rs and the wrapper are generated.
# Port stubs are unimplemented!() with the source file:line in the doc comment.
# Return Err("TypeName: message") where the source raises; it becomes that
# exception in Python (codegen_py.rs, PY_ERROR block).

rust-anything record /tmp/ra-e2e/rust/sample-rs --count 100
# Recorded 344 cases (76 threw) in ./cases.jsonl.

rust-anything build /tmp/ra-e2e/rust/sample-rs
# Built ./python/sample_rs  (cargo build --release, installs _native.abi3.so)

rust-anything diff /tmp/ra-e2e/rust/sample-rs
# 344/344 cases match

rust-anything bench /tmp/ra-e2e/rust/sample-rs
# Times recorded cases on the original and on Rust, bridge included, and
# prints a ship or do-not-ship verdict.

rust-anything gate /tmp/ra-e2e/rust/sample-rs
# 11 checks: fmt, clippy -D warnings, cargo test, unsafe audit, ported,
# size, error cases, panics, build, api, behavior. "Gate passed."
```

Useful variants: `record --from-tests -- pytest` records every call the original test suite makes to the unit (`src/main.rs:122-125`); `record --inputs cases.jsonl` adds real-world inputs (`{"fn", "args"}` per line); `record --float-tolerance 1e-9` lets floats match within that share; `record --count 2000` is the count used in the README fuzzy example.

### 1.3 What `record` actually records

Case generation is deterministic and seeded per function name (`src/harness.rs:812-830`, `generate`). It produces edge cases first, then seeded random mixes, plus semantic traps applied to every parameter one at a time (`src/harness.rs:836-927`, `trap_values`, `trap_args`): strings include non-ASCII, emoji, BOM and sigma variants; ints include -7, -1, 0, 2,147,483,648, 9,007,199,254,740,993, i64::MAX and i64::MIN; floats include 0.1, 0.30000000000000004, 1e21, 5e-324, -0, and 1.7976931348623157e308. Functions in files that use regexes also get regex traps. Each case is one JSONL line in `cases.jsonl` with `fn`, `args`, `kwargs`, and either `ok` or `error`.

Recording runs the original in-process through a generated Python driver (`src/harness_py.rs`, `DRIVER_PY`). The driver imports the original module with `importlib` (relative imports work), runs each case, and encodes results with markers: `{"$num": "NaN"}`, `{"$num": "Infinity"}`, `{"$num": "-0"}`, `{"$float": repr}`, `{"$int": str}` beyond 2^53, `{"$tuple": [...]}`, `{"$set": [...]}`, `{"$bytes": [...]}`, `{"$dict": [[k, v]]}` for non-string keys, `{"$object": name, "attrs": ...}` for dataclass instances, `{"$repr": type}` for anything else. It runs with `PYTHONHASHSEED=0` and `PYTHONDONTWRITEBYTECODE=1` (`src/harness_py.rs:68-70`), so no `__pycache__` is left in the source tree. A fingerprint of the unit files is saved in `recorded-from.json`; if the original changes later, `diff` warns and `gate` fails until you record again (`src/recording.rs:3-10`). Cases where the port is meant to differ can be listed in `known-diffs.jsonl` with a reason; any other difference still fails (`src/recording.rs:82-110`).

A per-case watchdog (default 10s, `RUST_ANYTHING_CASE_TIMEOUT`, `src/harness.rs:1193-1206`) stops a driver stuck on one input, keeps the lines recorded so far, and leaves that input out in `timed-out.json`. It does not protect against an input that allocates a huge amount of memory instantly: that kills the whole driver with SIGKILL before the watchdog can act. I hit exactly this, see Appendix B.

### 1.4 What `diff` checks, and what it does not

`diff` replays every recorded case against the Rust module through the same driver (`src/harness_py.rs:121-150`). Values must match exactly as canonical JSON. Exception types are part of the contract and must match, with one deliberate loophole: a Rust `TypeError` (the bindings rejected the arguments) is accepted as matching any error from the original (`src/harness_py.rs:357-367`, `same`). Passing means the Rust matches every recorded case, nothing more. The README "What it can't catch" section is explicit: inputs nobody recorded are the ceiling; timing, memory, concurrency under load, and side effects other than stdout, stderr, exit codes, written files and HTTP responses are not compared; a recording proves behavior only on the machine that ran it.

### 1.5 The Python bridge, concretely

`bridge` scaffolds a crate named `<unit>-rs` with `crate-type = ["cdylib", "rlib"]`, PyO3 0.30 with features `extension-module` and `abi3-py39`, `profile.release` with `lto = true` (generated `Cargo.toml` in my sample crate). The generated `src/lib.rs` is PyO3 `#[pyfunction]` wrappers that call `port::*` and map `Err("TypeName: message")` to that Python exception, defaulting to `ValueError` for unknown prefixes (`src/codegen_py.rs`, `PY_ERROR`). The generated `python/<lib>/__init__.py` re-exports the native functions so callers import the package where they imported the original module, with the same names. Types cross natively when they are strings, ints, floats, bools, lists or options of those; structured values cross through `pyconv.rs` with the same markers as the recorder (`src/codegen_py.rs:630-640`). Python ints beyond i64 become a `{"$int": ...}` marker or an `OverflowError` for the `Num` type, which models Python int-or-float semantics (`//` floors, `%` takes the divisor sign, `/` always gives a float, `src/codegen_py.rs`, `PYNUM_RS`). `bridge` parses types from hints (`src/lang/python.rs:1271-1322`, `to_ts_type`): `list[str]` to `string[]`, `Optional[int]` to `int | undefined`, `dict[str, X]` to `Record<string, X>`, `Callable` to a function type (which keeps the export in Python), `Any` and `object` to `unknown`.

Batch classes are the speed story. `bridge --batch fn:param` generates a class (e.g. `SlugifyBatch`) that takes the `param` values once, keeps them in Rust, and runs the function over all of them per call on all cores with rayon `par_iter`, without the GIL, allocating with mimalloc (`demo/fixtures/python-textkit-rs/src/lib.rs:170-263`; batch crate deps `rayon = "1"`, `mimalloc = "0.1"` in its `Cargo.toml:17-18`). `run(<other args>)` returns every result; `rank(<other args>, min)` returns item indexes best first. A custom `FnIndex` struct in `port.rs` with `new(items)` and `run(...)` can prepare items once (lowercasing, masks, position tables).

`shadow` generates a drop-in module that runs both the original and the Rust side by side, returns the original result, and reports mismatches; `RUST_ANYTHING_MODE=old|shadow|new` selects the mode (`src/codegen_go.rs:1401-1410` documents the same switch; README "Shadow" row). `gate` runs 11 checks (`src/gate.rs:170-197`): fmt, clippy with warnings as errors, cargo tests, unsafe audit (no `unsafe` without a `// SAFETY:` comment; the generated port has `#![forbid(unsafe_code)]`), nothing left `unimplemented!`, port size at most 3x the original plus 50 lines, a recorded failing case for every error path, no `unwrap`/`expect`/`panic!` where the original returns an error, build, API, and behavior (diff 100 percent).

### 1.6 How `profile` finds what to port

`rust-anything profile <repo> -- python3 bench.py` runs a real workload under cProfile (`python -m cProfile -o`, `src/profile.rs:414-427`) and reports hot functions with callers and a recommendation per function. It also flags code already compiled by numba, Cython or JAX, where a Rust port gains little (`src/profile.rs:74-100`, `risks::python_compiled`). The skill (`skills/rust-anything/SKILL.md`) states the rule plainly: a small function called once per item is not worth porting alone, port it with its callers or batch it.

## 2. What Python it can and cannot handle

### 2.1 Can handle (proven by a passing gate, not just claimed)

| Shape | Evidence |
| --- | --- |
| Pure functions over str, int, float, bool, list, dict, tuple, set, bytes, Optional | Type mapping `src/lang/python.rs:1271-1322`; conversion `src/codegen_py.rs:630-640` (`PYCONV_RS`); fixture `demo/fixtures/python-textkit-rs` diff 1144/1144, measured 21:43:41 |
| Classes with a constructor and plain methods | `src/codegen_py.rs` `#[pyclass]` generation; fixture `class Stack` in bench, 200 cases |
| Dataclass arguments and results | `$object` marker, `src/harness_py.rs:274-280` (`dataclass_named`); only dataclasses round-trip as objects |
| Default arguments, keyword-only arguments | `signature()` in `src/codegen_py.rs:11-33`; my sample `shout(text, times=1)` recorded with `{"$undefined": true}` for the omitted arg and passed |
| Exceptions with matching types | `PY_ERROR` mapping; `same()` in `src/harness_py.rs:361-367`; my sample recorded 76 throwing cases, all matched |
| Untyped parameters used as numbers | Inferred as numbers, `src/lang/python.rs:975-1040` (`infer_numbers`); `docs/real-world-languages.md:123-129` reports 1,709 garbage-input cases from untyped `colorsys` code forced that inference |
| Big ints, NaN, Infinity, -0, float versus int distinction | Markers in `src/harness_py.rs:200-260`; `Num` type in `src/codegen_py.rs` (`PYNUM_RS`) |
| Regexes with plain patterns | Recorded with regex traps; but see the limits row below |
| Whole-app CLI and server behavior | `app record` / `app replay` black-box cases, README "Port a whole app" |

The strongest external proof is `colorsys.py` from CPython 3.13: 6 functions, 2,400 recorded cases, 2,400/2,400, gate passes (`docs/real-world-languages.md:15`; demo `demo/real-world/python-colorsys-rs`, `cases.jsonl` present).

### 2.2 Cannot handle, or handles only with a trap

| Shape | What happens | Evidence |
| --- | --- | --- |
| `async def` functions | `bridge` exports them and `analyze` only lists Async as a risk, but the port stub is `pub async fn` while the generated `lib.rs` calls it synchronously with no `.await`, so `cargo build` fails with E0277. Proven 21:47:25, see Appendix B. There is no generated async runtime handling for Python. | `src/codegen_py.rs` has no `is_async` handling (only test line 1120); `src/bridge.rs:1270-1274` note says "Async TS functions are `async fn` in the port; the bindings return promises", TS only |
| Generator functions (`yield`) | Stay in Python, re-exported by the shadow module | `src/bridge.rs:119-121` (`js_only_reason`: "generator: returns a lazy iterator"); `src/lang/python.rs:1056-1065`; proven in my async probe: `gen` went to `js_only` with that reason |
| `*args`, `**kwargs` | Block the export, stays in Python | `src/lang/python.rs:1122-1126`, `1158-1162` ("takes `*args`", "takes `**kwargs`") |
| Callable parameters (a parameter the body calls) | Block the export | `src/lang/python.rs:1064-1081` ("calls its parameter ... : a callable"); `Callable` maps to a function type, `src/lang/python.rs:1316` |
| Non-safe decorators | Block the export. Safe list is only `cache`, `lru_cache`, `functools.cache`, `functools.lru_cache`, `staticmethod` | `src/lang/python.rs:777-784` (`SAFE_DECORATORS`), `1081-1087` |
| Classes with inheritance, class decorators, dunder methods, public attributes, or methods returning the class itself | Block the class | `src/lang/python.rs:1182-1268` (`class` blockers) |
| Arbitrary objects as arguments or results | Encoded as `{"$repr": ...}` and never round-trip; only dataclasses rebuild | `src/harness_py.rs:274-280`; `src/codegen_py.rs` `type_error` for unsupported argument types |
| `eval`, `exec`, `compile`, `__import__`, dynamic imports | Flagged as DynamicCode risk; cannot be ported, only flagged | `src/lang/python.rs:256-260` (`scan`); `src/analyze.rs:667` |
| `getattr`, `setattr`, `hasattr`, `isinstance`, `globals`, `locals`, `vars` | Flagged as DynamicTyping or Reflection risk | `src/lang/python.rs:262-268` |
| Threading, `asyncio.gather`, executors | Flagged as Concurrency risk | `src/lang/python.rs:252-256` |
| Dynamic regex (`re` with a non-literal pattern) | Flagged as DynamicRegex risk | `src/lang/python.rs:270-283` |
| Regex lookaround and backreferences | The `regex` crate has no lookaround or backreferences; `fancy-regex` is the suggested swap, but passing recorded cases still does not prove non-ASCII `\w`, `\b`, `\d` behavior matches | README "What it can't catch", Regexes; `skills/rust-anything/SKILL.md` |
| Float formatting and exact float equality | Number-to-text formatting differs between languages; `--float-tolerance` forgives rounding only, never formatting | README "What it can't catch", Floats |
| I/O, network, databases, signals, files written outside the recorded set | Not compared at all; `diff` only sees return values and raised errors, `app replay` sees stdout, stderr, exit codes, written files and HTTP responses | README "What it can't catch", "Anything not in the output" |
| C extensions, numba, Cython, JAX | Already machine code; `profile` and `analyze` flag them as gaining little | `src/profile.rs:74-100`; README FAQ "Is Rust always faster?" |
| Unbounded allocation from a trap input (e.g. string repeat by a huge int) | Kills the whole `record` driver with SIGKILL before the 10s watchdog can act | Measured 21:44:13 and 21:44:55, Appendix B |

## 3. Does it fit computer-use-wayland's hot paths?

Repo skimmed: `~/workspace/computer-use-wayland` at main `21684e7`, about 37,152 lines of Python across `scripts/` and `tests/`. Biggest files: `scripts/cu.py` 2,158 lines, `scripts/tc02_controller.py` 1,641, `scripts/session_remote.py` 1,556, `scripts/sync-installed.py` 1,191. `native/` already holds C and C++ (`pointer.c`, `modifiers.c`, `cursor-guard.cpp`) plus Hyprland Lua patches, so native code in this repo is not new. Zero `async def` or `asyncio` in `scripts/*.py` (grep count 0), so the async gap in Section 2 does not block this repo, but the other blockers do matter: `cu.py` is full of `*args`/`**kwargs`-style helpers, subprocess calls, and PIL objects that cannot cross a bridge.

### 3.1 What the hot path actually is

The per-observation path in `cu.py` is `observe()` (line 904) and `observe_screen()` (line 956): capture through a subprocess (`run`, line 479; `run_cancelable`, line 603), then `validate_desktop_observation()` (line 770) which PIL-decodes the PNG, checks mode `RGB` and size, and SHA256-hashes the raw pixels, then `save_observation()` (line 824) which LANCZOS-resizes above `max_width` and PNG-encodes at `compress_level=1`. The pure-Python work per observation is validation, metadata bookkeeping, and JSON parsing of `hyprctl -j` output (`hypr`, lines 486-513). The heavy operations (PNG decode, resize, encode, SHA256) are already C code inside Pillow and hashlib. The waits are sleeps and polling (`time.sleep` at lines 544, 1173, 1301, 1684, 1780) and subprocess spawns (`hyprctl`, `pgrep`, capture tools).

The 10x review already proved the think-observe-think loop is 87.8 percent of task time, agent think gaps run 25 to 150s, and broker requests are 0.11 to 0.61s. The r8 measurements file in this repo agrees in shape: native tasks show `command_ms` around 233 to 244ms against `wall_ms` of 8,296 to 14,340ms, with the rest labeled agent and tool roundtrips, not model think alone (`docs/benchmarks/r8_measurements.json`, native T1 and T2 entries). Rust can only speed the harness portion, never model think time, and inside the harness it can only speed pure compute, never process spawn, compositor capture, or sleeps.

### 3.2 Fit judgement, function by function

- Good fit in principle: small pure functions over strings, numbers, lists and dicts, called in a loop. `cu.py` has several: `validate_coordinate_metadata()` (line 691), `screen_changed()` (line 986), `plain_rgb_png()` (line 651), `intersect()` and `bounds()` (lines 548-550), `keyboard_groups()` (line 1082). These are exactly the shape rust-anything ports well. But each is microseconds of Python per call, and my measured bench says per-call ports of such functions run 0.68x to 0.95x, slower than Python, because one PyO3 crossing costs about 100 to 300ns and the work is smaller than the crossing (`docs/real-world-languages.md:47-48`). Porting them one by one would make the harness slower, not faster. The tool itself prints this verdict.
- Good fit only as a batch: the batch form wins where the per-call form loses. The only honest Rust win in this repo would be a loop moved whole into Rust, with data staying in Rust across calls. Candidates are the observation validation pipeline (decode, hash, resize, encode over many frames) and any scoring loop over many items. But the observation pipeline is already C inside Pillow, so a Rust port of the Python glue around Pillow buys almost nothing; the win would come from replacing Pillow calls with Rust image code, which rust-anything does not do for you, it only checks a port you write.
- Bad fit: anything doing I/O, subprocess management, Hyprland IPC, sleeps, or stateful session driving (`session_driver.py`, `mcp_bridge.py`, `session_remote.py`, `tc02_controller.py`). None of that crosses a bridge, and none of it is recorded by `record` (return values only). The broker and session driver are relay and polling code, not compute.
- Bad fit: any function taking PIL `Image` objects, file handles, sockets, or callbacks. Images become `$repr`, callbacks block the export, `*args` and `**kwargs` block the export.

### 3.3 What the numbers say about the ceiling

Per-call Python ports measured in this repo's own docs: 1.35x geometric mean, 1.5 to 1.9x on most calls (`docs/real-world-languages.md:30`). My fresh module measured 0.76x overall. My fixture bench measured 1.04x overall with only `slugify` above 1.1x (2.72x). Batch ports measured here: `slugify` over 20,000 strings, 3.1x to 17.0x across four runs on this VM (see Appendix A). Even a 17x speedup on a 150ms batch is about 140ms saved per batch, against think gaps of 25 to 150s. That is the honest scale: Rust is a rounding error on total task time unless the ported loop runs hundreds of times per task or the batch is the whole observation pipeline.

## 4. Verdict and first experiment

### Verdict

rust-anything is a real, working, honest tool, and it is the right vehicle for porting a pure-compute Python hot loop, with recorded proof at every step. It is not the right vehicle for speeding up computer-use-wayland as a whole, and it must not be sold as a 10x lever on task time. The 10x target is dominated by model think time (87.8 percent), which Rust cannot touch, and the harness remainder is dominated by subprocess spawn, compositor capture, sleeps, and already-compiled C code (Pillow, hashlib), which a PyO3 port of Python glue also cannot touch. The tool itself agrees: its `bench` verdict on small functions is "Do not ship this unit for speed".

Use it, but use it narrowly: one batch, one measured loop, with `bench` as the judge. Do not start a whole-app migration (`app front-door`, `app lift`) for this repo. The repo is a CLI plus broker plus session driver plus Hyprland integration, not a library of pure functions, and most of its units would land in `js_only` or in the "keep in source language" column.

### First concrete experiment

Port the observation validation plus resize plus encode loop as one batch, and let `bench` decide. Concretely:

1. Extract the pure part of `save_observation()` and `validate_desktop_observation()` in `scripts/cu.py` (lines 770-890) into a new leaf module, e.g. `scripts/obs_math.py`, with no PIL objects crossing the boundary: inputs are raw bytes and ints, outputs are bytes and ints. Keep PIL calls out of the ported functions at first, so the port is honest Python compute (bytes hashing is already C, so include the resize math, coordinate validation, and metadata checks, not the PNG encode).
2. Run `rust-anything profile ~/workspace/computer-use-wayland -- python3 scripts/cu.py <a real observe workload>` first. If `profile` does not name the extracted functions as hot, stop. Do not port on speculation.
3. Run the loop: `analyze`, `bridge <repo> scripts/obs_math.py --batch <fn>:<param>`, `record --count 2000`, write `src/port.rs`, `build`, `diff`, `bench`, `gate`.
4. Acceptance criteria, all measured: `diff` 100 percent on at least 2,000 recorded cases including real observation bytes passed via `--inputs`; `bench` shows at least 2x on the batch form and the verdict says ship; `gate` passes. If `bench` says "Do not ship", stop and report that, do not reframe it.
5. If the batch wins, the second experiment is the real one: replace the Pillow resize and encode inside the port with Rust image code (`image` crate) and re-run the same loop, because that is the only place a large speedup can come from, and rust-anything will check it against the same recording.

Do not do first: porting `cu.py` helpers one by one, porting anything in `session_driver.py` or `mcp_bridge.py`, or any whole-app lift. Those are proven losing moves by the measurements above.

## Appendix A. Measured verification log

Environment for all numbers: this VM, 4 CPUs, 1.5 shared CPU units, 6 GB RAM, cargo 1.100.0, Python 3.12.3, rust-anything 1.5.1 at HEAD `a827562`.

Fixture `demo/fixtures/python-textkit-rs` (slugify, word_counts, chunk, page_count, mean, class Stack; `cases.jsonl` 1,144 lines):

```text
$ rust-anything build .        # 21:42:39 to 21:43:38, 59s
Built ./python/textkit_rs
$ rust-anything diff .         # 21:43:41
1144/1144 cases match
$ rust-anything bench .        # 21:43:43
slugify       200 cases  orig 2942 ns/call  Rust 1081 ns/call  2.72x
word_counts   200 cases  orig  610 ns/call  Rust  770 ns/call  0.79x
chunk         200 cases  orig  583 ns/call  Rust  810 ns/call  0.72x
page_count    144 cases  orig  245 ns/call  Rust  259 ns/call  0.95x
mean          200 cases  orig  325 ns/call  Rust  357 ns/call  0.91x
class Stack   200 cases  orig 7329 ns/call  Rust 7828 ns/call  0.94x
Overall 1.04x (geometric mean); 1 of 6 functions at least 1.1x faster.
Do not ship this unit for speed: calling across costs more than the work
these functions do. Port a bigger unit (these functions together with their
callers), so one call does more work.
```

Batch benchmark `python3 bench_batch.py` (20,000 strings, `SlugifyBatch`, asserts equality with the Python original first, four consecutive runs):

```text
run 1: slugify x20000: python 186.1 ms, batch 25.4 ms: 7.3x
run 2: slugify x20000: python 148.4 ms, batch 47.4 ms: 3.1x
run 3: slugify x20000: python 139.6 ms, batch 29.0 ms: 4.8x
run 4: slugify x20000: python 147.7 ms, batch  8.7 ms: 17.0x
```

What the 17x claim rests on: `demo/fixtures/python-textkit-rs/bench_batch.py`, which builds `SlugifyBatch` once over 20,000 strings and times `b.run("-", None)` against a Python list comprehension, on 4 cores with rayon and mimalloc. The README table (`README.md:44`) says Python `slugify` over 20,000 strings takes 98 ms and the batch is 17x faster. On this VM the Python baseline was 139.6 to 186.1 ms (slower machine than the README machine), and the batch ranged 8.7 to 47.4 ms. The 17x figure is reproducible here as a best case (run 4 hit exactly 17.0x) but the median of four runs is about 4.8x to 7.3x, and the spread is large because rayon thread scheduling on shared CPUs is noisy. Report the range, not the best run. The equality assertions in `bench_batch.py` passed on every run, and the `ZeroDivisionError` behavior matched between Python and Rust.

Fresh module `/tmp/ra-e2e/sample.py` (my own 3 functions, port written by hand):

```text
$ rust-anything record . --count 100
Recorded 344 cases (76 threw) in ./cases.jsonl
  safe_div: 117, shout: 120, word_count: 107
$ rust-anything build .        # 26s
Built ./python/sample_rs
$ rust-anything diff .
344/344 cases match
$ rust-anything bench .
shout      120 cases  orig 495 ns/call  Rust 730 ns/call  0.68x
safe_div   117 cases  orig 224 ns/call  Rust 262 ns/call  0.86x
word_count 107 cases  orig 233 ns/call  Rust 305 ns/call  0.76x
Overall 0.76x (geometric mean); 0 of 3 functions at least 1.1x faster.
Do not ship this unit for speed: calling across costs more than the work
these functions do.
$ rust-anything gate .         # first run: 10 of 11 pass, clippy failed on
                               # manual_range_contains in my own port.rs line 11
$ rust-anything gate .         # after a one-line fix
pass fmt, clippy, cargo test, unsafe, ported, size (17 lines Rust for
11 lines Python, 1.5x), error cases, panics, build, api, behavior 344/344
Gate passed.
```

Own test suite: `cargo test --release --lib`, 133 passed, 0 failed, 0.42s of test time after a 97s compile.

## Appendix B. Two findings from verification

### B.1 `record` OOM-kills on an unbounded trap input (my test bug, tool gap)

My first `sample.py` had `shout` doing `(text.strip().upper() + "!") * times` with no bound. `record` applies int traps including 2,147,483,647 and i64::MAX to every int parameter (`src/harness.rs:836-860`), so it called the original with `times` near 2 billion. Python tried to allocate a multi-gigabyte string and the Linux OOM killer killed the whole driver with SIGKILL at 21:44:13 and again at 21:44:55, with 6.6 GB free at start, so this was not ambient memory pressure. The 10s per-case watchdog (`src/harness.rs:1193-1206`) cannot save this case: the allocation attempt is near-instant and kills the process before any timeout fires, and no `cases.jsonl` is written at all. Fix in my module: raise `ValueError` for `times` outside 0..100, and mirror it in `port.rs`. After the fix, `record` completed in under a second with 344 cases. Lesson for real ports: any function whose output size scales with an int input (repeat, multiply, range, list allocation) needs a bound in the original or a `--inputs` file that avoids the giant traps, or `record` will die the same way. Worth an upstream note: the watchdog handles slow cases, not instantly huge allocations.

### B.2 Python `async def` bridges but cannot build (tool gap, proven)

Probe module `/tmp/ra-async/asyncmod.py`: `async def fetch(url: str) -> str`, `def gen(n: int)` with `yield`, `def plain(x: int) -> int`. Results:

- `analyze` listed the unit ready, readiness 92, with risks "Async and promises x3" and "Generators x2". It did not block the unit.
- `bridge` exported `fetch` normally (`is_async: true` in `rust-anything.json:22`) and put only `gen` in `js_only` with reason "generator: returns a lazy iterator". The bridge note printed was "Async TS functions are `async fn` in the port; the bindings return promises", which is TS wording applied to a Python unit.
- The generated `src/port.rs:11` stub is `pub async fn fetch(url: String) -> Result<String, String>`, but the generated `src/lib.rs:30` calls `port::fetch(url)?` with no `.await`.
- With a trivial port body (`Ok(url.to_uppercase())`), `rust-anything build .` failed at 21:47:25 with `error[E0277]: the ? operator can only be applied to values that implement Try, src/lib.rs:30:31`. `src/codegen_py.rs` contains no `is_async` handling anywhere in its generation code, only in a test. So a Python `async def` can never complete the loop with generated bindings. Workarounds are hand-editing generated `lib.rs` (wiped by `refresh`) or making the port sync and changing the caller API. For computer-use-wayland this does not bite today (zero `async def` in `scripts/`), but it rules out rust-anything for any future async Python in this repo unless upstream adds async PyO3 bindings.
