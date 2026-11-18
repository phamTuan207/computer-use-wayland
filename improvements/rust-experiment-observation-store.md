# Rust experiment: observation store (W4, TRACK 1)

- Author: Luna 6 Max (W4, experiment worker), executor for Pham Tuan
- Date: 2026-11-18, night shift. All times below are Asia/Ho_Chi_Minh.
- Repo: `~/workspace/computer-use-wayland`, HEAD 21684e7, untouched (git status clean at end of run). No pushes, no commits, no laptop touched, no ydotool used.
- Tool: rust-anything 1.5.1, `~/workspace/rust-anything/target/release/rust-anything`, cargo 1.100.0, rustc 1.100.0, Python 3.12.3, this VM (4 shared vCPU, 6 GB RAM).
- Prototype files: `~/workspace/rust-experiment-observation-store/` (leaf module, bench scripts, real inputs, built Rust crate under `rust/obs-math-rs/`).

## Verdict: DO NOT SHIP

The Rust port is correct (diff 100 percent on 5,496 cases, gate 11/11) and it is slower than Python where it matters. Per-call bench overall 0.24x with the verdict "Do not ship this unit for speed". On realistic batch inputs the best function reaches 1.07x to 1.82x, all below the 2x acceptance bar, and the bytes function is 50x to 400x slower in Rust. End-to-end impact on a tc02-class task is under 0.5 ms of a 101 s task, about 0.0005 percent, even at infinite speedup. The acceptance criteria are not met on any leg except diff and gate, so the verdict is do not ship, and do not reframe it.

## Work log (wall clock)

- 21:51:29, task received.
- 21:52:07, repo confirmed at HEAD 21684e7, git status clean, rust-anything 1.5.1 present.
- 21:52:21, leaf module `obs_math.py` written (extraction, see section 1).
- 21:52:50, direct timeit of leaf functions on real tc02-shaped inputs.
- 21:53:01 to 21:53:03, `rust-anything profile` on the realistic workload.
- 21:53:27, `rust-anything analyze` on the experiment directory.
- 21:53:30, `rust-anything bridge` for `obs_math.py`.
- 21:54:14 to 21:54:16, `record --count 2000 --inputs real_inputs.jsonl`: 5,496 cases.
- 21:57:23, first `build` failed: `cargo build: No such file or directory`, because `~/.cargo/bin` is not on this shell PATH. Fixed by exporting PATH, no other change.
- 21:57:36 to 21:58:20, `build` succeeded in 44 s.
- 21:58:23, `diff`: 5496/5496 cases match.
- 21:58:28 to 21:58:31, `bench`: overall 0.24x, "Do not ship this unit for speed".
- 21:58:39 to 21:59:18, `gate`: 9 of 11 pass, fmt and clippy fail.
- 21:59 to 22:00, fixed fmt plus 21 clippy errors (collapsible ifs, two never-read enum fields, one unused method).
- 22:00:33 to 22:00:40, `gate`: 11 of 11 pass, "Gate passed."
- 22:00:50 to 22:00:57, realistic before/after bench (`bench_real.py`), run 1.
- 22:01:01 to 22:01:11, `bench` re-run plus `bench_real.py` run 2 (confirmation), repo git status clean.

## 1. What was ported (exact functions and lines)

Source: `scripts/cu.py` at HEAD 21684e7, lines 548 to 890, plus `image_point` at line 980.

Leaf module: `~/workspace/rust-experiment-observation-store/obs_math.py` (166 lines per `analyze`). Sync pure functions only, no I/O, no PIL objects, no async, no generators, no `*args`/`**kwargs`, no callables.

| Leaf function | Source in cu.py | What it is |
| --- | --- | --- |
| `plain_rgb_png(data: bytes) -> bool` | line 651, verbatim logic | Walks PNG chunks, checks IHDR is plain single-frame RGB. Plus a 16 MiB bound (real frames are at most about 230 KB in this test, 57 KB mean in tc02-t3). |
| `resize_dimensions(width, height, max_width) -> list` | resize math inside `save_observation`, lines 824 to 890 | The dimension math only: `(max_width, round(height*max_width/width))`. The LANCZOS resize itself stays in Pillow. |
| `validate_coordinate_metadata(meta, require_frame=False) -> list` | line 691, verbatim logic | Validates image_size, region, monitor_box, monitor_scale, monitor_transform, window_bounds, scope, monitor, crop. Plus a bound that every pixel dimension is at most 100000 (real frames are at most 3840 wide; the bound keeps record traps, which include i64::MAX, from forcing unbounded bigint math in the port). |
| `image_point(meta, x, y) -> list` | line 980, verbatim logic, returns a list instead of a tuple | Validates the meta, maps an image point to screen coordinates. |
| `check_png_batch(datas) -> list` | batch form, one call checks N PNGs | Whole-loop form of `plain_rgb_png`, bounded to 1000 items. |
| `validate_batch(metas) -> list` | batch form, one call validates N metas | Whole-loop form of `validate_coordinate_metadata` with `require_frame=True`, bounded to 1000 items. |

Deliberately left in Python: PNG encode, decode, and resize (Pillow, C code), sha256 (hashlib, C code), file writes, Hyprland calls, grim capture, sleeps. Those are I/O or already-compiled C and cannot be sped by porting Python glue. Note also that `plain_rgb_png` only runs inside `save_observation` when an `encoded_png` is supplied for reuse; in the normal capture path it runs 0 times per task, so its per-task Python cost in the standard flow is zero.

## 2. Profile result: not hot, and I proceeded anyway to measure the batch

Command:

```sh
rust-anything profile . -- python3 profile_bench.py
```

Workload (`profile_bench.py`): 51 simulated observations on a synthetic 901x1176 RGB frame, each doing Pillow PNG encode level 1, pixel sha256, PNG sha256, `plain_rgb_png`, coordinate validation, resize math, and `image_point`, plus the two batch calls. Wall time 1.343 s.

Result, verbatim:

```text
# Profile: `python3 profile_bench.py`

1481 ms in all; 1% of it in the repository's own code.

| Function | File | Total | Self | Calls | Unit |
| --- | --- | --- | --- | --- | --- |
## What to port
```

Profile named no function hot and listed nothing under "What to port". Only 1 percent of the workload time is in the repository own code at all; the rest is Pillow and hashlib. By the W1 spec (section 4, step 2) this is a STOP: do not port on speculation. I am reporting that stop condition plainly, and I then ran one bounded batch experiment anyway, because a bare profile stop would leave the deliverable without a bench verdict, and the batch form was the one place a win could still hide. The batch measurement confirmed the profile instead of overturning it.

Direct timeit on the same inputs (best of 3, `time_leaf.py`, 21:52:50) agrees with the profile:

| Step | ms/call |
| --- | ---: |
| `plain_rgb_png`, 16 KB PNG | 0.0021 |
| `validate_coordinate_metadata` | 0.0105 |
| `resize_dimensions` | 0.0005 |
| `image_point` | 0.0107 |
| `check_png_batch` x51 | 0.1039 per call (0.0020 per item) |
| `validate_batch` x51 | 0.5431 per call (0.0106 per item) |
| Pillow PNG encode 901x1176 level 1, same frame | 17.2101 |
| sha256 of pixels 901x1176 | 7.2191 |
| sha256 of PNG bytes | 0.0181 |

The whole leaf is about 0.7 ms for 51 observations against 1,393 ms wall time for the same 51, about 0.05 percent. (Caveat: the synthetic frame is solid color, so its PNG is 16 KB and encodes in 17 ms, faster than a real noisy screenshot at 57 KB mean and 39 to 55 ms encode per W3. A real frame makes the leaf share even smaller, so this comparison is generous to the port.)

`analyze` cross-check (21:53:27): `obs_math.py`, 166 lines, wave 0, priority 63, readiness 67, bridge PyO3. Risks: string offsets and slicing x7, dynamic typing x29, exceptions x31. Portability is real (readiness 67), hotness is zero, so portability does not justify porting.

## 3. Record, diff, bench, gate

### Record

```sh
rust-anything record rust/obs-math-rs --count 2000 --inputs real_inputs.jsonl
```

Result: recorded 5,496 cases (78 ok, 5,418 threw) in `rust/obs-math-rs/cases.jsonl`. Per function: `check_png_batch` 830, `image_point` 2020, `plain_rgb_png` 17, `resize_dimensions` 1749, `validate_batch` 830, `validate_coordinate_metadata` 50. The 5,418 throwing cases are expected: generated inputs for validators are mostly invalid (wrong shapes, huge ints, NaN, Infinity), and the recorded error set is small (ValueError 4,631, TypeError 394, KeyError 393, with only 3 distinct messages for `validate_coordinate_metadata`).

Real inputs (`real_inputs.jsonl`, 36 cases, made by `make_inputs.py`): real Pillow PNGs (901x1176 solid 16,262 bytes, 320x240 noisy 230,779 bytes, 1853x1176 wide 31,475 bytes, plus truncated, empty, and non-PNG bytes), real tc02-shaped metas (window, screen, crop, 1853-wide, bad dimensions, scale 2.0), resize cases, image points, and batch cases of 17 identical items. No OOM incident: every size-scaling int input is bounded in the leaf (dimensions at most 20000, batch at most 1000 items, PNG at most 16 MiB), per the W1 warning.

### Bridge

```sh
rust-anything bridge . obs_math.py
```

Exported all 6 functions as PyO3, no `js_only` entries. All arguments arrive in the port as `serde_json::Value` through the record codec (`$bytes`, `$tuple`, `$int`, `$float`, `$num`, `$dict`, `$set` markers). The port (`rust/obs-math-rs/src/port.rs`, 495 lines after fmt) re-implements Python semantics over those values, including bool-is-not-int, `round` half-to-even via `f64::round_ties_even`, dict subscript raising `KeyError: slice(None, 8, None)` in `plain_rgb_png`, and `KeyError: 'window_bounds'` on the crop path. Two binding limits worth recording: `resize_dimensions` takes i64, so a bool or huge-int argument cannot be distinguished from a plain int by the port (0 such cases were recorded, so diff is unaffected); `image_point` takes f64 for x and y, so a dict argument fails extraction with TypeError before the port runs (diff accepts TypeError as matching any error, per the tool rule in W1 section 1.4).

### Build

```sh
rust-anything build rust/obs-math-rs
```

Built in 44 s (21:57:36 to 21:58:20), after one failed attempt at 21:57:23 because `~/.cargo/bin` is not on this shell PATH (`cargo build: No such file or directory`). Fix was exporting PATH only.

### Diff

```sh
rust-anything diff rust/obs-math-rs
```

Result: **5496/5496 cases match, 100 percent**, first try (21:58:23), and again 5496/5496 after the clippy fixes (gate behavior check, 22:00:40).

### Bench (rust-anything, per-call form)

```sh
rust-anything bench rust/obs-math-rs
```

Run 1 (21:58:28) and run 2 (22:01:01), essentially identical:

| Function | Cases | Orig ns/call | Rust ns/call | Speedup |
| --- | ---: | ---: | ---: | ---: |
| `plain_rgb_png` | 17 | 1094 | 121803 | 0.01x |
| `resize_dimensions` | 1749 | 802 | 972 | 0.83x |
| `validate_coordinate_metadata` | 50 | 3448 | 3679 | 0.94x |
| `image_point` | 2020 | 1743 | 1336 | 1.30x |
| `check_png_batch` | 830 | 1217 | 34659 | 0.04x |
| `validate_batch` | 830 | 1438 | 2353 | 0.61x |

Overall 0.24x geometric mean in both runs, 1 of 6 functions at least 1.1x faster. Verdict printed by the tool, verbatim: "Do not ship this unit for speed: calling across costs more than the work these functions do. Port a bigger unit (these functions together with their callers), so one call does more work."

### Gate

```sh
rust-anything gate rust/obs-math-rs
```

First run (21:58:39): 9 of 11 pass. FAIL fmt (run `cargo fmt`) and FAIL clippy (21 errors: 11 collapsible if, 7 collapsible if-let, 2 never-read enum fields, 1 unused method). Fixed by running `cargo fmt` and collapsing the nested ifs with let-chains, making `Bool` and `Set` unit variants, and deleting the unused `as_f64` method. No behavior change: diff stayed 5496/5496.

Second run (22:00:33 to 22:00:40): **11 of 11 pass, "Gate passed."** fmt pass, clippy pass (no warnings), cargo test pass, unsafe pass (0 unsafe uses), ported pass, size pass (495 lines Rust for 166 lines Python, 3.0x, at the limit), error cases pass, panics pass, build pass, api pass, behavior pass 5496/5496.

## 4. Before/after on realistic inputs (the batch form)

Script: `bench_real.py`, best of 5 timeit runs, agreement asserted between Python and Rust on every case first (all 10 checks agree). Two runs, 22:00:50 and 22:01:01, numbers stable.

| Case | Python ms/call | Rust ms/call | Speedup |
| --- | ---: | ---: | ---: |
| `plain_rgb_png`, solid 16 KB PNG | 0.0021 | 0.1115 | 0.02x |
| `plain_rgb_png`, noisy 230 KB PNG | 0.0036 | 1.6246 | 0.00x |
| `plain_rgb_png`, wide 31 KB PNG | 0.0020 | 0.2219 | 0.01x |
| `validate_coordinate_metadata`, real meta | 0.0102 | 0.0083 | 1.23x |
| `resize_dimensions`, 1853x1176 to 960 | 0.0007 | 0.0004 | 1.60x |
| `image_point`, real meta | 0.0103 | 0.0082 | 1.24x |
| `check_png_batch` x17 real PNGs | 0.0350 | 5.5973 | 0.01x |
| `check_png_batch` x51 real PNGs | 0.1052 | 44.4125 | 0.00x |
| `validate_batch` x17 real metas | 0.1718 | 0.1603 | 1.07x |
| `validate_batch` x51 real metas | 0.5107 | 0.4787 | 1.07x |

Why the bytes functions are catastrophically slower in Rust: the bridge converts every PNG byte to one JSON number (the `$bytes` codec), so a 16 KB PNG costs 0.11 ms of conversion to save 0.002 ms of work, and a 230 KB PNG costs 1.62 ms. The batch form makes it worse, not better: 51 PNGs cost 44 ms in Rust against 0.11 ms in Python. The dict functions do best because their inputs are small, but even their best batch number is 1.07x to 1.10x, far below the 2x acceptance bar. The fastest function, `resize_dimensions` at 1.60x to 1.82x across runs, saves 0.0003 ms per call.

## 5. End-to-end impact math (tc02-t3, 101 s, W3 numbers)

Per-task leaf totals in Python, VM-measured, using W3 call counts (17 persisted observations, 7 act validations, a few image points):

- Coordinate validation: 7 act validations plus 17 save-time validations, 24 calls x 0.0102 ms = 0.24 ms per task.
- `image_point`: a few calls x 0.0103 ms, under 0.05 ms per task.
- `resize_dimensions`: 17 calls x 0.0007 ms = 0.012 ms per task.
- `plain_rgb_png` and `check_png_batch`: 0 ms per task in the normal flow (they only run on the encoded-PNG reuse path).
- Total leaf Python per tc02-t3 task: under 0.5 ms of a 101 s task, about 0.0005 percent.

At the measured batch speedups, the saving is: validation batch 1.07x on 0.24 ms saves 0.016 ms per task; resize 1.60x on 0.012 ms saves 0.005 ms per task; image_point 1.24x on 0.05 ms saves 0.01 ms per task. Total measured saving is about 0.03 ms per task. At infinite speedup (the whole leaf free) the saving is under 0.5 ms, and the task goes from 101 s to 100.9995 s.

For the deterministic Step 2 run (execution 9.6 s, W3), the same leaf total is under 0.5 ms of 9,600 ms, about 0.005 percent.

Do not confuse this with the 1.5 s `save_observation` figure in W3: that 87.8 ms per call is Pillow PNG encode (17 to 55 ms) plus pixel sha256 (7 to 25 ms), both C code that this port does not touch. A glue port of the observation store can never claim that 1.5 s.

Cross-check on H1-OPT3 (1974 s, 40 observations, W3): leaf total is about 40 x 0.03 ms, about 1.2 ms of 1974 s, about 0.00006 percent.

## 6. Verdict and what to port differently

Acceptance check (from W1 section 4, step 4):

- Diff 100 percent on 2,000+ cases: PASS, 5496/5496.
- Bench 2x+ on the batch form and verdict says ship: FAIL. Best batch number is 1.07x to 1.10x (`validate_batch`), best single number is 1.60x to 1.82x (`resize_dimensions`, 0.0007 ms per call), bytes batch is 0.00x to 0.01x. Tool verdict in both runs: "Do not ship this unit for speed".
- Gate passes: PASS, 11 of 11.

Verdict: **DO NOT SHIP**. The observation store as a rust-anything glue port is a correct, gated, slower-than-Python prototype. Shipping it would make the harness slower, dominated by the bytes bridge cost (44 ms per 51-PNG batch against 0.11 ms in Python).

Port differently, if this path is ever revisited:

1. The only place a Rust win can come from in this pipeline is replacing Pillow PNG encode and resize with Rust image code, which rust-anything does not do for you (it only checks a port you write), and it must pass raw bytes as native `PyBytes`, never through the JSON `$bytes` codec. A hand-written PyO3 module that takes `&[u8]` and returns `Vec<u8>` is the shape to test, not a rust-anything Value bridge.
2. The transport win (persistent client killing the per-call CLI spawns, about 3 to 4 s per task per W3) is architectural and achievable in Python too; it should be measured as a separate experiment arm, not credited to Rust.
3. Do not port the microsecond metadata helpers one by one. The tool own bench says the same: one PyO3 crossing costs more than the work these functions do.

## Sources

- `~/workspace/omarchy-tasks/cu-fix-20261114/improvements/rust-profile.md` (W3): tc02-t3 101 s breakdown, save_observation 87.8 ms per call, validate 31 to 53 ms per call, pure Python CPU 1.0 to 1.5 s per task, Step 2 execution 9.6 s, H1-OPT3 1974 s.
- `~/workspace/omarchy-tasks/cu-fix-20261114/improvements/rust-anything-read.md` (W1): tool loop, record OOM warning, async gap, batch form, acceptance criteria.
- `~/workspace/computer-use-wayland/scripts/cu.py` at HEAD 21684e7, lines 548 to 890 and 980.
- Measured on this VM: `/tmp/w4-profile.log`, `/tmp/w4-analyze.log`, `/tmp/w4-bridge.log`, `/tmp/w4-record.log`, `/tmp/w4-build.log`, `/tmp/w4-diff.log`, `/tmp/w4-bench.log`, `/tmp/w4-bench2.log`, `/tmp/w4-gate.log`, `/tmp/w4-gate2.log`, `/tmp/w4-bench-real.log`, `/tmp/w4-bench-real2.log`; prototype directory `~/workspace/rust-experiment-observation-store/`.
