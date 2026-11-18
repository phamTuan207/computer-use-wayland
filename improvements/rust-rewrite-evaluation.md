# Rust rewrite evaluation: final verdict (TRACK 1)

- Author: Luna 6 Max (W6, final report writer), executor for Pham Tuan
- Date: 2026-11-18, night shift. Work log (Asia/Ho_Chi_Minh): 22:11 task received, all five worker reports read; 22:12 this file written on the VM; mirror and push to branch rust-rewrite-eval follow.
- Repo: ~/workspace/computer-use-wayland, HEAD 21684e7. All numbers below are measured, with a source per claim. No em dash or en dash is used anywhere in this file.
- Scope: Track 1 of the "fastest possible, every way, everything" program. Track 2 (broad speed crawl, non-Rust) shares the profiling baseline in section 1. The question answered here is only: does rewriting the Python harness in Rust make real tasks faster, and by how much, measured?

## Verdict in one paragraph

STAY PYTHON. A full Rust rewrite is not worth doing, and the one Rust port that looked promising on paper (the observation store) is measurably slower than Python and must not ship. The only Rust artifact with a real win is the one-shot CLI-spawn binary (about 3.0 s per task), and even that win is not Rust-specific: a persistent Python client is faster per request (0.2 to 0.4 ms) than the one-shot Rust binary (2.2 to 2.6 ms), and Step 3 already owns that saving, so the two do not stack. The honest ceiling is small: the whole harness is 13.0 percent of the best model-loop task and 1.8 percent of the held-out task, and the pure Python CPU Rust could speed is 1.0 to 1.5 s of a 101 s task. A 20x speedup on that CPU saves 1.4 percent of task time. That is the number the whole evaluation comes down to.

## 1. Measured time breakdown of a real task

### 1.1 tc02-t3, the best clean model-loop run (101 s)

Source: rust-profile.md section 1 (W3), built from 10x-review-astra6.md, 10x-executor-time.md, 10x-observ-codex-report.md. All three agree.

| Part | Seconds | Percent of 101 s |
|---|---:|---:|
| Session start to ready | 2.0 | 2.0 |
| Broker service, all 14 requests (submission to result receipt) | 13.105 | 13.0 |
| Between-request gaps (executor think, read image, decide, build next request) | 52.813 | 52.3 |
| Head and tail (ready to first request 25.978 s, last result to finish about 9.1 s) | 35.082 | 34.7 |
| Total | 101 | 100 |

Inside the 13.105 s of broker service (laptop log):

| Sub-part | Seconds |
|---|---:|
| Image-bearing request intervals, 10 images | 9.630 (mean 0.963 s) |
| Non-image request intervals (windows, status, finish) | 3.475 |
| Timed capture, decode, encode stages inside the images | 1.58 total (capture mean 115.0 ms plus PNG encode mean 43.5 ms, 10 images) |
| PNG payload delivered | 573,507 bytes, mean 57,351 bytes per image |
| Result-poll sleep inside service | up to about 7 s (L3 helper sleeps 0.5 s before each result poll, 14 requests) |

What the logs cannot split, stated honestly (rust-profile.md section 1): the 52.813 s gap has no inference start and end timestamps, so no sub-claim such as "thinking alone is X s" is made. The correct claim is "inter-request waiting dominates". The 0.5 s poll sleep and the 25.978 s first-request delay are caller-side, not broker-side.

### 1.2 The same pattern at every scale

Source: rust-profile.md section 1.

| Task | Total | Broker service | Gaps |
|---|---:|---:|---:|
| tc02-t1, 36 requests, first-run discovery | 823 s | 37.721 s (4.6 percent) | 722.955 s (87.8 percent), max single gap 101.395 s |
| tc02-t3, 14 requests, learned procedure | 101 s | 13.105 s (13.0 percent) | 52.813 s (52.3 percent), max gap 11.834 s |
| Baseline failed run, 25 requests | 1195.417 s | 16.171 s (1.35 percent) | 1078.926 s (90.26 percent) |
| tc01 Pinta, 63 requests, 5 sessions | 1550 s | 58.037 s (3.7 percent) | 1444.847 s (93.2 percent) |

Correction to the starting numbers (rust-profile.md section 6): "think-observe-think loop is 87.8 percent" is the tc02-t1 number, not the steady-state number. For the best clean run t3 it is 52.3 percent gaps plus 34.7 percent head and tail, 87.0 percent outside service combined. "Agent think gaps 25 to 150 s" is partly corrected: max single gaps are t1 101.395 s, t3 11.834 s, tc01 223.915 s, tc05 101.516 s.

### 1.3 H1 cross-check, held-out Omawrite case (1974 s)

Source: rust-profile.md sections 1 and 4, from heldout-validation-results.md. H1-OPT3: 1974 s, 78 broker requests, 40 observations, 36 act requests, 112 actions, SUCCESS byte-for-byte on a 105-byte file, verified 3 times. Broker round-trips 0.1 to 2.5 s each, executor gaps 15 to 90 s each. At the prior attempt's measured broker mean of about 0.45 s, total broker service is about 35 s, 1.8 percent of 1974 s. Even at the maximum 2.5 s per request it is at most 195 s, 9.9 percent. Pure Python CPU inside that is on the order of 2 s. A 20x harness speedup saves about 2 s of 1974 s, 0.1 percent. H1 confirms the tc02 finding on unseen UI: the broker is never the bottleneck, the executor loop is.

### 1.4 The deterministic controller run, the harness ceiling (Step 2)

Source: rust-profile.md section 2, from opt-step2-report.md. No model round trips between steps. Run A2: execution 9.5962 s, end-to-end 13.4469 s. A1r2 9.6831 and 13.5265 s, A3 9.8992 and 13.7684 s, B1 cold 9.8188 and 13.6898 s. Byte-exact 50/50 in all 4, OCR crop hit 8/8, zero fallbacks, delivered image bytes down 46 percent (259 KB to about 140 KB).

| Step | A2 seconds | What it is |
|---|---:|---|
| P0 | 3.70 | VS Code cold launch to a mapped 901x1176 window |
| P1 | 2.53 | Session start: start CLI about 0.76 s plus 3 status polls about 0.24 s each plus 2 x 0.5 s sleeps |
| G0 | 1.02 | Windows round trip 0.32 s plus observe round trip 0.33 s plus crop OCR 0.26 to 0.30 s |
| S1 | 1.25 | Act receipt 0.85 to 0.88 s plus crop OCR 0.30 to 0.36 s |
| S2 | 1.60 | Act 0.91 to 0.96 s plus dialog poll 0.65 to 0.80 s (dialog spawns about 0.44 s after the row click) |
| S3 | 0.34 | One crop-observe round trip |
| S4 | 0.90 | Act exec 434 to 471 ms plus after-capture 87 to 125 ms |
| S5 | 1.18 | Act 0.62 s plus windows 0.53 s |
| S6 | 0.79 | Crop observe 0.33 s plus finish 0.47 s |

Per-request floor (rust-profile.md section 2): every broker_driver call is a request CLI (0.13 to 0.19 s) plus a result CLI (0.11 to 0.25 s); instant commands cost about 0.32 to 0.33 s round trip; 12 task requests carry roughly 3 s of round-trip floor. Even a perfect 8 s execution leaves end-to-end near 11.7 s because P0 alone is 3.7 s.

### 1.5 The harness fraction, the honest math

Source: rust-profile.md section 4. Harness means broker service plus capture and encode plus CLI overhead, everything inside local transactions, excluding model think, executor gaps, and app waits.

Model-loop task, tc02-t3 (101 s):

| Slice | Seconds | Percent of task |
|---|---:|---:|
| Total task | 101 | 100 |
| Broker service (absolute ceiling for all harness plus app-wait work) | 13.105 | 13.0 |
| Inside service: result-poll sleep, L3 helper only (0.5 s x 14) | up to about 7 | up to 6.9 |
| Inside service: CLI spawn floor (about 0.3 s x 14) | about 3.4 to 6.2 | 3.4 to 6.1 |
| Inside service: timed capture, decode, encode (laptop log) | 1.58 | 1.6 |
| Inside service: validation, diff, app waits, remainder | about 1 to 2 | 1 to 2 |
| Pure Python CPU that Rust could speed (encode wrapper excluded, it is C; hashing, validation, diff, JSON, grouping) | about 1.0 to 1.5 | 1.0 to 1.5 |

20x speedup math for tc02-t3:

- 20x on pure Python CPU only (1.5 s): saves 1.5 x 19/20 = 1.43 s. Task 101 s becomes about 99.6 s, 1.4 percent faster.
- 20x on Python CPU plus eliminating CLI spawns with a persistent binary (about 3 to 4 s): saves about 4.3 to 5.2 s. Task becomes about 96 s, about 5 percent faster.
- Zeroing ALL broker service (13.105 s, impossible, it includes app waits and sleeps): task becomes 87.9 s, 1.15x. This matches the Amdahl bound in 10x-review-astra6.md section 2.

Deterministic task, Step 2 run A2 (execution 9.5962 s, end-to-end 13.4469 s):

| Slice | Seconds | Percent of execution |
|---|---:|---:|
| Execution | 9.60 | 100 |
| Pure Python CPU (capture and encode wrapper, validation, diff) | about 1.5 to 2.5 | 16 to 26 |
| CLI spawn floor (about 0.3 s x 12) | about 3 | 31 |
| OCR tesseract (C binary, Rust cannot speed) | about 2.1 to 2.9 | 22 to 30 |
| App waits (dialog spawn 0.44 s, S2 wait 474 ms, finish 0.47 s, dialog poll remainder) | about 1.5 | 16 |
| Session start P1 (start CLI, polls, 2 x 0.5 s sleeps) | 2.53 | 26 (overlaps with the rows above in wall time accounting, listed separately in the step table) |

20x speedup math for the deterministic run:

- 20x on pure Python CPU only (about 2 s): saves about 1.9 s. Execution 9.6 s becomes about 7.7 s, 1.25x.
- If the Rust binary is also persistent (removes about 3 s of CLI spawns): execution becomes about 4.7 s, 2.0x; end-to-end 13.5 s becomes about 10.5 s. Still short of the 10 s end-to-end target, because P0 VS Code cold launch (3.7 s), OCR (about 2.4 s), and dialog and finish waits (about 1.6 s) are untouched by a harness port.

## 2. Hot paths, ranked, with measured numbers

Source: rust-profile.md section 3. Method: direct timing with timeit (best of 3) of the real functions from scripts/cu.py at HEAD 21684e7, synthetic 901x1176 RGB frame like the tc02 window, plus a 1853x1176 frame like the old tc02 run. VM: Python 3.12.3, PIL 10.2.0, 4 shared vCPU. Call counts per tc02-t3 task: 14 requests, 10 delivered images, 7 act requests, about 17 persisted observations (10 delivered plus 7 after-captures), 7 preflight re-captures with persist=False.

### Rank 1: per-request CLI process spawn plus result polling

- Function: session_remote.py _exchange() (line 1273) and main() (line 1468), driven by tc02_controller.py broker driver subprocess calls (lines 390 to 405).
- Per-call cost, laptop log: request CLI 0.13 to 0.19 s plus result CLI 0.11 to 0.25 s, instant commands 0.32 to 0.33 s round trip (opt-step2-report.md). VM-measured by W5, tighter: one spawn about 107 ms (section 3 of this report).
- Call count per task: 14 requests x 2 CLI calls (request plus result) = 28, plus start and finish, about 30 spawns.
- Per-task total: about 3 to 4 s in the deterministic run (12 requests x about 0.3 s floor, 31 percent of 9.6 s execution), about 3.4 to 6.2 s inside tc02-t3 service. This is the largest task-level harness cost.
- Honest caveat: killing it needs a persistent client, not a faster language. A persistent Python client would remove the same 3 to 4 s. Rust only wins here if the port is built as a persistent binary, and the win is architectural, not from Rust being faster than Python.

### Rank 2: observation persist, save_observation()

- Function: scripts/cu.py save_observation() (lines 824 to 890).
- Per-call cost, VM-measured: 87.8 ms per call (n=10, best of 3; recorded encode_ms 70.9 ms in that run). Components, VM-measured: PNG encode 901x1176 level 1, 39.1 to 55.4 ms across runs; pixel sha256 (tobytes plus hash), 13.6 to 25.1 ms; PNG sha256, 0.027 ms; file writes plus iterdir sweep, about 0.02 ms. persist=False costs 0.35 to 0.52 ms, proving the persist path is encode plus hashing, not validation.
- Call count per task: about 17 persisted saves (10 delivered plus 7 after-captures).
- Per-task total: about 1.5 s per tc02-t3 task.
- Honest caveat: the PNG encode is libpng and zlib in C through Pillow, already native code. A Rust port only wins here with a faster PNG encoder than libpng level 1, not by rewriting Python. The resize branch (LANCZOS, VM-measured 69.6 to 121.0 ms for 1853x1176 to 960x612) does not run for the 901-wide tc02 window, it only matters for old 1853-wide frames.

### Rank 3: observation re-validation, validate_desktop_observation()

- Function: scripts/cu.py validate_desktop_observation() (lines 770 to 822).
- Per-call cost, VM-measured: load_image=True 30.8 to 52.8 ms; load_image=False 33.3 to 49.3 ms.
- Call count per task: 7, one per act request.
- Per-task total: about 0.22 to 0.37 s per tc02-t3 task.
- Defect found by measurement: load_image=False costs the same as True. When observation_path is set, the code always re-reads the PNG from disk, re-decodes it with PIL, and re-verifies both hashes (lines 792 to 821); the flag only controls whether the decoded copy is returned. The preflight validation therefore pays a full decode plus two hashes on every act, even when the caller does not need the pixels. This is a Python-side fix, no Rust needed.
- Supporting micro-costs in the same path, VM-measured: screen_changed() (lines 986 to 999) 7.7 to 14.3 ms per call, 7 per task, about 0.06 to 0.10 s total; PPM decode (grim output) 2.2 to 4.7 ms; iterdir sweep 0.019 ms.

### Largest step cost Rust cannot speed: OCR (tesseract, already a C and C++ binary)

- Function: tc02_controller.py _ocr_text() (lines 1081 to 1137), subprocess to tesseract --psm 6.
- Per-call cost, laptop log: crop OCR 0.26 to 0.36 s, full-frame OCR 0.79 to 0.98 s (opt-step2-report.md). VM-measured on the synthetic frame: menu crop 500x40, 174 ms; line crop 901x60, 182 ms; full frame 901x1176, 633 ms (best of 3).
- Per-task total: 8 crop OCRs, about 2.1 to 2.9 s of the 9.6 s Step 2 execution (22 to 30 percent). A Rust port of the harness does not touch this at all. Any experiment claiming an OCR win must replace the OCR engine, which is out of scope for a harness port.

### Measured as NOT hot (microseconds, do not port for speed)

VM-measured, best of 3 (rust-profile.md section 3): image_point() (cu.py:980) 0.012 ms; validate_coordinate_metadata() (cu.py:691) 0.013 to 0.014 ms; check_cancel() (cu.py:570) 0.008 ms with no session token; keyboard_groups() (cu.py:1082) 0.004 ms; validate_actions() (cu.py:1011) 0.061 to 0.074 ms for a 5-action tc02-like list; key_names() (cu.py:52) 0.021 to 0.023 ms for 3 keys; json.loads of a 12-window hypr clients list (4946 bytes) 0.049 to 0.166 ms; sha256 of a 1 KB broker envelope line 0.002 ms. All coordinate math, validation, grouping, and JSON parsing combined is under 1 ms per request. The "Python is slow" intuition fails here: the metadata path is already negligible.

Unmeasured on the VM (needs the laptop compositor or broker, not attempted): grim fork and exec time on the real host (laptop-log capture 78 ms warm, code-hotspots.md section 1.1), Hyprland Unix-socket round-trip time (no compositor on the VM), SSH and Tailscale transfer time, wtype process cost (keyboard_argv could not run on the VM: private wtype helper missing, native/wtype absent), and fcitx5 IME switch budgets (up to 0.5 s off plus 0.5 s restore per literal keyboard group, code budgets in cu.py:1132 to 1195, actual time unmeasured).

## 3. The tools: what rust-anything and craft-anything actually are

### 3.1 rust-anything (W1): real, honest, narrow

Source: rust-anything-read.md (W1), repo ~/workspace/rust-anything, HEAD a827562, version 1.5.1. Toolchain on the VM: cargo 1.100.0, rustc 1.100.0, Python 3.12.3.

- What it does: it does not translate code. It records what the original Python does on generated inputs, then checks a hand-written Rust port against that recording at every step. Loop: profile, analyze, bridge, record, port.rs, build, diff, bench, shadow, gate.
- Verified end to end on this VM: cargo build --release in 4m 25s, binary 22,215,872 bytes, version 1.5.1. Demo fixture diff 1144/1144 cases match; bench overall 1.04x geometric mean, verdict "Do not ship this unit for speed" (only slugify won per-call, 2.72x; word_counts 0.79x, chunk 0.72x, page_count 0.95x, mean 0.91x, Stack 0.94x). Fresh module (/tmp/ra-e2e/sample.py): record 344 cases (76 threw), diff 344/344, bench overall 0.76x ("Do not ship"), gate 11/11 after a one-line clippy fix. Own test suite: cargo test --release --lib, 133 passed, 0 failed.
- The 17x claim, dissected: batch slugify over 20,000 strings, four runs on this VM: 7.3x, 3.1x, 4.8x, 17.0x. Median about 5 to 7x; 17x is the best run only, and the spread is large because rayon thread scheduling on shared CPUs is noisy. Report the range, not the best run. Even a 17x speedup on a 150 ms batch is about 140 ms saved per batch, against think gaps of 25 to 150 s.
- What it cannot handle (proven, not claimed): Python async def bridges but cannot build (generated lib.rs calls the async port stub synchronously with no .await, error E0277, proven 21:47:25); generator functions stay in Python; *args and **kwargs block the export; callable parameters block the export; non-safe decorators block the export; classes with inheritance, class decorators, dunder methods, or public attributes block the class; arbitrary objects become $repr and never round-trip; PIL Image objects, file handles, sockets, and callbacks cannot cross the bridge. The repo has zero async def in scripts/ (grep count 0), so the async gap does not block this repo today, but the other blockers do: cu.py is full of *args and **kwargs-style helpers, subprocess calls, and PIL objects.
- Two real findings: record OOM-kills on an unbounded trap input (a string repeat by a near-2-billion int trap killed the whole driver with SIGKILL at 21:44:13 and 21:44:55; the 10 s per-case watchdog cannot save an instant huge allocation); and per-call ports of small functions run 0.68x to 0.95x, slower than Python, because one PyO3 crossing costs about 100 to 300 ns and the work is smaller than the crossing.
- W1 verdict: rust-anything is a real, working, honest tool, and the right vehicle for one pure-compute batch loop with bench as judge. It is not a 10x lever on task time.

### 3.2 craft-anything (W2): irrelevant, skip it

Source: craft-anything-read.md (W2), repo ~/workspace/craft-anything, HEAD 9c9f5a1, version 0.6.1, workspace edition 2024, 806 .rs files, 13 crates, 3 apps. Verdict: irrelevant.

- It does not port code. It clones apps by observing behaviour and having an external coding agent write a fresh implementation from that evidence. That is the opposite direction from a faithful source-to-source port whose logic must survive.
- A grep for transpil and port-a-code phrasing across crates/, apps/, docs/, README.md and AGENTS.md returns zero hits for any transpiler or code-port feature. There is no Python source parser in the dependency tree: no tree-sitter, no rustpython, no pyo3 in any Cargo.toml. Its Python handling is three shallow things: .pyc header inventory (bytecode is not decoded, "this shows what functions exist and what they name, not what they do"), PyInstaller bundle extraction (target is not a PyInstaller bundle), and Python launch recipes (how to RUN Python, not convert it).
- Maturity: early alpha by its own badge, 164 open roadmap items, engine tools tested only against stand-ins. Do not install it, do not vendor any crate, do not route port work through its rebuild loop. The only action worth taking is a 30-minute skim of crates/ai/src/rebuild/check.rs and crates/platform/src/process.rs as design references for build, check, and timeout handling.

## 4. Prototype 1: observation store (W4). Verdict: DO NOT SHIP

Source: rust-experiment-observation-store.md (W4). Prototype under ~/workspace/rust-experiment-observation-store/ (leaf module, bench scripts, real inputs, built Rust crate under rust/obs-math-rs/).

### What was ported

Leaf module obs_math.py (166 lines), sync pure functions only, no I/O, no PIL objects, no async, no generators, no *args or **kwargs, no callables. Source: scripts/cu.py at HEAD 21684e7, lines 548 to 890, plus image_point at line 980.

| Leaf function | Source in cu.py | What it is |
| --- | --- | --- |
| plain_rgb_png(data: bytes) -> bool | line 651, verbatim logic | Walks PNG chunks, checks IHDR is plain single-frame RGB. Plus a 16 MiB bound. |
| resize_dimensions(width, height, max_width) -> list | resize math inside save_observation, lines 824 to 890 | Dimension math only. The LANCZOS resize itself stays in Pillow. |
| validate_coordinate_metadata(meta, require_frame=False) -> list | line 691, verbatim logic | Validates image_size, region, monitor_box, monitor_scale, monitor_transform, window_bounds, scope, monitor, crop. |
| image_point(meta, x, y) -> list | line 980, verbatim logic | Validates the meta, maps an image point to screen coordinates. |
| check_png_batch(datas) -> list | batch form, one call checks N PNGs | Whole-loop form of plain_rgb_png, bounded to 1000 items. |
| validate_batch(metas) -> list | batch form, one call validates N metas | Whole-loop form of validate_coordinate_metadata with require_frame=True, bounded to 1000 items. |

Deliberately left in Python: PNG encode, decode, and resize (Pillow, C code), sha256 (hashlib, C code), file writes, Hyprland calls, grim capture, sleeps. Note: plain_rgb_png only runs inside save_observation when an encoded_png is supplied for reuse; in the normal capture path it runs 0 times per task, so its per-task Python cost in the standard flow is zero.

### Profile said stop, and the bench confirmed it

rust-anything profile on a realistic workload (51 simulated observations, wall time 1.343 s): 1481 ms in all, 1 percent of it in the repository own code. Profile named no function hot and listed nothing under "What to port". By the W1 spec this is a STOP: do not port on speculation. W4 reported the stop plainly and ran one bounded batch experiment anyway, because a bare profile stop would leave no bench verdict. The batch measurement confirmed the profile instead of overturning it.

Direct timeit on the same inputs (best of 3, 21:52:50): plain_rgb_png on a 16 KB PNG 0.0021 ms; validate_coordinate_metadata 0.0105 ms; resize_dimensions 0.0005 ms; image_point 0.0107 ms; check_png_batch x51 0.1039 ms per call; validate_batch x51 0.5431 ms per call; Pillow PNG encode 901x1176 level 1, same frame, 17.2101 ms; sha256 of pixels 7.2191 ms; sha256 of PNG bytes 0.0181 ms. The whole leaf is about 0.7 ms for 51 observations against 1,393 ms wall time for the same 51, about 0.05 percent.

### Record, diff, bench, gate

- Record: 5,496 cases (78 ok, 5,418 threw as expected; generated inputs for validators are mostly invalid), including 36 real-input cases (real Pillow PNGs, real tc02-shaped metas). No OOM incident: every size-scaling int input is bounded in the leaf.
- Diff: 5496/5496 cases match, 100 percent, first try and again after the clippy fixes.
- Bench (rust-anything, per-call form), two runs, essentially identical:

| Function | Cases | Orig ns/call | Rust ns/call | Speedup |
| --- | ---: | ---: | ---: | ---: |
| plain_rgb_png | 17 | 1094 | 121803 | 0.01x |
| resize_dimensions | 1749 | 802 | 972 | 0.83x |
| validate_coordinate_metadata | 50 | 3448 | 3679 | 0.94x |
| image_point | 2020 | 1743 | 1336 | 1.30x |
| check_png_batch | 830 | 1217 | 34659 | 0.04x |
| validate_batch | 830 | 1438 | 2353 | 0.61x |

Overall 0.24x geometric mean in both runs, 1 of 6 functions at least 1.1x faster. Tool verdict, verbatim: "Do not ship this unit for speed: calling across costs more than the work these functions do. Port a bigger unit (these functions together with their callers), so one call does more work."

- Gate: first run 9 of 11 pass (fmt and clippy fail, 21 clippy errors); after fixes, 11 of 11 pass, "Gate passed." (fmt, clippy, cargo test, unsafe, ported, size 495 lines Rust for 166 lines Python at the 3.0x limit, error cases, panics, build, api, behavior 5496/5496.)

### Before and after on realistic inputs (the batch form)

Script bench_real.py, best of 5 timeit runs, agreement asserted between Python and Rust on every case first. Two runs, 22:00:50 and 22:01:01, numbers stable.

| Case | Python ms/call | Rust ms/call | Speedup |
| --- | ---: ---: | ---: ---: | ---: |
| plain_rgb_png, solid 16 KB PNG | 0.0021 | 0.1115 | 0.02x |
| plain_rgb_png, noisy 230 KB PNG | 0.0036 | 1.6246 | 0.00x |
| plain_rgb_png, wide 31 KB PNG | 0.0020 | 0.2219 | 0.01x |
| validate_coordinate_metadata, real meta | 0.0102 | 0.0083 | 1.23x |
| resize_dimensions, 1853x1176 to 960 | 0.0007 | 0.0004 | 1.60x |
| image_point, real meta | 0.0103 | 0.0082 | 1.24x |
| check_png_batch x17 real PNGs | 0.0350 | 5.5973 | 0.01x |
| check_png_batch x51 real PNGs | 0.1052 | 44.4125 | 0.00x |
| validate_batch x17 real metas | 0.1718 | 0.1603 | 1.07x |
| validate_batch x51 real metas | 0.5107 | 0.4787 | 1.07x |

Root cause of the bytes slowness: the bridge converts every PNG byte to one JSON number (the $bytes codec), so a 16 KB PNG costs 0.11 ms of conversion to save 0.002 ms of work, and a 230 KB PNG costs 1.62 ms. The batch form makes it worse, not better: 51 PNGs cost 44 ms in Rust against 0.11 ms in Python. The dict functions do best because their inputs are small, but even their best batch number is 1.07x to 1.10x, far below the 2x acceptance bar. The fastest function, resize_dimensions at 1.60x to 1.82x across runs, saves 0.0003 ms per call.

### End-to-end impact

Per-task leaf totals in Python, VM-measured, using W3 call counts (17 persisted observations, 7 act validations, a few image points): coordinate validation 24 calls x 0.0102 ms = 0.24 ms per task; image_point a few calls, under 0.05 ms; resize_dimensions 17 calls x 0.0007 ms = 0.012 ms; plain_rgb_png and check_png_batch 0 ms in the normal flow. Total leaf Python per tc02-t3 task: under 0.5 ms of a 101 s task, about 0.0005 percent.

At the measured batch speedups, the saving is about 0.03 ms per task. At infinite speedup (the whole leaf free) the saving is under 0.5 ms, and the task goes from 101 s to 100.9995 s. For the deterministic Step 2 run (execution 9.6 s), the same leaf total is under 0.5 ms of 9,600 ms, about 0.005 percent. Cross-check on H1-OPT3 (1974 s, 40 observations): leaf total about 1.2 ms of 1974 s, about 0.00006 percent.

Do not confuse this with the 1.5 s save_observation figure in W3: that 87.8 ms per call is Pillow PNG encode (17 to 55 ms) plus pixel sha256 (7 to 25 ms), both C code that this port does not touch. A glue port of the observation store can never claim that 1.5 s.

### Acceptance check

Diff 100 percent on 2,000+ cases: PASS, 5496/5496. Bench 2x+ on the batch form and verdict says ship: FAIL, best batch number 1.07x to 1.10x, best single number 1.60x to 1.82x, bytes batch 0.00x to 0.01x. Gate passes: PASS, 11 of 11. Verdict: DO NOT SHIP. Shipping it would make the harness slower, dominated by the bytes bridge cost.

## 5. Prototype 2: CLI-spawn replacement (W5). Verdict: REAL WIN, DO NOT SHIP YET

Source: rust-experiment-cli-spawn.md (W5). Prototype under ~/workspace/rust-experiment-cli-spawn/ (Rust source, bench scripts, JSON result files, README with rebuild and rerun steps).

### Correction to the task framing

The per-step spawn is session_remote.py, not cu.py. The controller (tc02_controller.py run_remote, lines 387 to 405) spawns [sys.executable, scripts/session_remote.py, ...] per step, never cu.py directly. Each broker_driver cycle is two spawns: request and result, plus status polls. session_remote.py imports all of cu at its top (import cu, line 29), so it pays the full cu.py import cost plus its own. cu.py itself only runs once per task as the long-lived session-driver child process. So the thinnest hot CLI path is session_remote.py status (one Unix-socket exchange, no lease file), and the per-step paths are status, result, and request with a lease file (two exchanges each). That is what was measured and what the prototype replaces.

### Per-invocation breakdown (VM-measured, n=21, medians)

Method: wall-clock subprocess.run timing, plus python3 -X importtime, plus in-process time.perf_counter splits, plus strace on the exact syscalls. Live broker: real session_remote.py serve on the VM.

session_remote.py status against the live broker, median 107.5 ms:

| Stage | ms | How measured |
|---|---:|---|
| Process spawn plus interpreter startup | 25.5 | python3 -c pass, median 25.5, range 24.0 to 31.8 |
| Imports (session_remote, cu, stdlib, PIL, etc.) | 59.5 | python3 -c "import session_remote" median 85.0 minus bare 25.5; -X importtime cumulative for session_remote 53.4 ms (self 4.0 ms, the rest is its imports) |
| __main__ source recompile (see below) | 19.5 | Script-mode status 111.3 minus -c import-plus-main 91.8; standalone compile() of session_remote.py 22.5 ms over bare |
| Argparse build, dispatch, print, teardown | about 3.0 | Residual; in-process main(['status']) 1.3 ms, fresh-process delta 4.7 ms |
| Unix-socket exchange (status round trip) | 0.2 | In-process _exchange({'command': 'status'}), median 0.2 ms, range 0.2 to 0.9 |
| Total | 107.5 | Wall clock, median, range 105.6 to 114.1 |

The actual work is 0.2 ms out of 107.5 ms. The spawn is 99.8 percent overhead.

All invocation shapes, medians, n=21: python3 -c pass 25.5 ms; import argparse 34.0 ms; import json, socket 39.2 ms; import cu 63.1 ms; import session_remote 85.0 ms; session_remote.py --help 109.0 ms; cu.py --help 110.4 ms; cu.py status (local latch read, no broker) 105.7 ms; session_remote.py status, no broker 107.8 ms; live broker 107.5 ms; status --lease-file 107.7 to 110.8 ms across lease shapes; result 109.6 ms; request 107.9 ms; argparse errors 107.4 to 107.6 ms. Every invocation costs about 105 to 111 ms regardless of what it does, even an argparse error and --help. The lease-file variants cost the same as plain status: the second exchange adds 0.2 ms.

The __main__ recompile, proven by strace: script mode opens session_remote.py source twice and never opens the .pyc; import mode opens __pycache__/session_remote.cpython-312.pyc once. CPython recompiles the main script from source on every run. Standalone compile() of session_remote.py costs 22.5 ms over bare, matching the residual. For cu.py the same effect is larger: standalone compile() costs 41.1 ms over bare. Consequence: even a zero-import Python CLI would still pay about 25 ms interpreter plus about 20 to 41 ms recompile per spawn.

Correction to W3 (rust-experiment-cli-spawn.md section 7): "cu.py --help 179.8 ms vs bare Python 38.3 ms, so roughly 140 ms is interpreter startup plus imports" is not reproduced. W5 medians are cu.py --help 105.5 ms (run 1) and 110.4 ms (run 2), bare Python 25.5 to 28.0 ms. W3's number was a mean of 5 and likely a cold-cache or loaded-VM run. The split for cu.py is 25.5 ms interpreter, 37.6 ms imports, about 41 ms __main__ recompile, about 1 ms work. Step 3's independent spawn median of about 118 ms agrees with 107 to 110 ms, so the 179.8 ms figure should not be cited.

### What was prototyped

A minimal Rust binary (session-remote-rs, binary session_remote, 373,984 bytes stripped, release, LTO, std-only, zero crates, no network needed to build; clean build 7.5 s, incremental 7.0 s; cargo and rustc 1.100.0). Files: src/main.rs (argparse-compatible front end), src/client.rs (Unix-socket exchange, lease handling, safe file reads), src/json.rs (ordered JSON value, strict parser, Python-compatible compact serializer), src/help.rs (exact --help texts, generated from captured Python output).

Implemented, faithfully: status [--lease-file], result --lease-file --sequence N, request --lease-file --sequence N --request FILE. That is every CLI spawn the controller makes per step. The binary reproduces the Python wire behavior: default socket from XDG_RUNTIME_DIR or /run/user/{uid}, one JSON line per exchange with shutdown(SHUT_WR), single-newline response validation, broker_unavailable on connect or I/O failure, lease read with the same safety checks (symlink is file_unavailable, non-regular or group-readable or foreign-owned is unsafe_file, oversize is too_large, bad JSON or bad fields is invalid_lease_file, missing generation is start_outcome_unknown, generation mismatch is broker_changed), request envelope read and JSON validation, exit 0 only when the response has ok true, argparse-compatible --help text, usage lines, and error messages including the quirks.

Deliberately not implemented: serve (a daemon, not a spawn), start and finish (once per task, with lease writes and a polling loop). They parse exactly like Python, but execution exits 1 with a stderr note telling the caller to use session_remote.py. This is a scope boundary, not a bug; the per-step saving does not need them.

### Fidelity: 74 diff cases, 74 pass, 0 fail

Method: bench/diff_harness.py runs the Python CLI and the Rust binary (invoked through a symlink named session_remote.py so argparse prog matches) on identical inputs and compares return code, stdout bytes, and stderr bytes. Final run 22:08 on the freshly built binary: 74 pass, 0 fail. Cases: 18 live-broker and no-broker behavior cases, 8 lease-shape cases, 33 argparse cases, 3 Rust-only scope checks (serve, start, finish refuse with the note), 2 XDG cases, 10 fake-broker canned responses (full nested object with unicode, spaced JSON, error object, array response, invalid JSON, two lines, no trailing newline, closed connection, 100 KB response, non-canonical number).

Two known divergences, both unreachable in controller use: non-canonical number lexemes (Rust keeps number lexemes verbatim; Python re-serializes them, 1e2 becomes 100.0; the broker only emits numbers via json.dumps, so its lines are already canonical); relative XDG_RUNTIME_DIR (Python crashes with an uncaught traceback, exit 1, empty stdout; Rust prints the clean error JSON, exit 1, same exit code). Minor: a lease version of JSON true passes Python (True == 1) but fails Rust validation. No real lease contains it.

### Before and after (same inputs, same VM, interleaved runs, n=31)

Method: bench/bench_before_after.py, runs interleaved (Python, Rust, Python, Rust) so shared-CPU drift hits both arms, outputs verified byte-identical on every run (0 mismatches in all 217 pairs). Second run reported below; the first run agreed within about 5 ms on every median.

| Case | Python median ms (range) | Rust median ms (range) | Saving ms | Speedup |
|---|---:|---:|---:|---:|
| status, no broker | 107.25 (103.18 to 130.68) | 1.74 (1.60 to 8.30) | 105.5 | 61.6x |
| status, live broker | 105.85 (102.37 to 174.03) | 2.18 (2.01 to 4.22) | 103.7 | 48.6x |
| status --lease-file, live broker | 109.98 (104.47 to 147.55) | 2.58 (2.33 to 5.43) | 107.4 | 42.6x |
| result --lease-file --sequence 1 | 109.78 (105.06 to 141.25) | 2.58 (2.39 to 3.77) | 107.2 | 42.6x |
| request --lease-file --sequence 1 | 109.05 (105.31 to 172.53) | 2.60 (2.37 to 4.16) | 106.5 | 41.9x |
| --help | 107.88 (105.96 to 129.48) | 1.65 (1.47 to 1.96) | 106.2 | 65.4x |
| status, fake broker, 100 KB response | 109.49 (104.85 to 188.88) | 2.64 (2.40 to 3.67) | 106.8 | 41.5x |

Per-spawn saving is about 104 to 107 ms on every path, including the 100 KB response, so the JSON layer is not a bottleneck after the fix below.

Bug found by measuring: the first JSON parser was quadratic. The first before and after run showed Rust slower than Python on the 100 KB canned response: Rust 181.03 ms vs Python 108.89 ms. Root cause: the string parser called from_utf8 on the remaining input for every character, which is O(n) per character and O(n squared) over a long string. Fix: copy fast runs of bytes up to the next quote, backslash, or control byte in one slice. After the fix: Rust 2.64 ms on the same 100 KB response. The diff harness still passes 74/74 after the fix, including the unicode and escape cases.

### End-to-end impact

Spawn count per tc02-class task: about 29 (Step 3 design: 12 task requests times 2 spawns, plus 3 status polls, plus start, plus finish; W3: about 30). Per-spawn saving: about 105 ms VM-measured, about 118 ms on the laptop (Step 3 design, spawn median, n=20).

| Task | Spawns | Saving (VM) | Saving (laptop extrap.) | New total |
|---|---:|---:|---:|---|
| Step 2 deterministic run A2, exec 9.5962 s | 29 | about 3.0 s | about 3.4 s | exec about 6.6 s, end-to-end 13.45 s to about 10.5 s |
| tc02-t3 model loop, 101 s, 14 requests | 28 | about 2.9 s | about 3.3 s | about 98 s, about 3 percent faster |
| H1-OPT3, 1974 s, 78 broker requests | 156 | about 16.4 s | about 18.4 s | about 1958 s, about 0.8 percent faster |

Reading this honestly:

- The Step 2 execution target of 8 s is beaten (about 6.6 s), but the end-to-end target of 10 s is still missed by about 0.5 s, because P0 VS Code cold launch (3.7 s), OCR (about 2.4 s), and dialog and finish waits (about 1.6 s) are untouched by a CLI port.
- The model-loop task improves about 3 percent. W3's Amdahl bound holds: even zeroing all broker service (13.105 s) only gives 101 s to 87.9 s (1.15x); Rust recovers about 23 percent of that ceiling. The think gaps (52.8 s) and head and tail (35.1 s) dominate, and no harness port touches them.
- H1 improves under 1 percent. Its cost is executor deliberation, not transport.

### The Rust one-shot vs Step 3 persistent stream comparison

Both attack the same about 3 s, and they do not stack. Per request, a persistent Python client is actually faster than the one-shot Rust binary: in-process _exchange is 0.2 ms and _client_with_lease is 0.4 ms, against one-shot Rust at 2.2 to 2.6 ms (the Rust binary still pays process spawn and dynamic linking, about 1.7 ms). The Rust one-shot wins on deployment risk, not on per-request speed: it is a drop-in binary swap for the controller's subprocess call, with no broker change, no protocol change, no persistent-connection lifecycle, and no stream auth state. Step 3 wins the last about 2 ms per request and removes the result-poll round trip as a separate spawn, at the cost of a broker change. If Step 3 ships, this Rust binary is redundant for speed; if Step 3 stalls on risk, this binary captures about 97 percent of the same saving with no broker touch. A persistent Rust client would be faster than both (about 0.2 ms per exchange with no spawn), but that is a different experiment: it needs the same stream design Step 3 already wrote, and its win over persistent Python would be under 0.5 ms per request, which is noise at task scale.

## 6. Honest end-to-end impact estimate

### Per path

| Path | Saving per tc02-t3 task (101 s) | Saving per Step 2 exec (9.6 s) | Saving per H1 task (1974 s) |
|---|---:|---:|---:|
| Observation store port (W4, measured) | about 0.03 ms (0.00003 percent) | under 0.5 ms (0.005 percent) | about 1.2 ms (0.00006 percent) |
| CLI-spawn Rust binary (W5, measured) | about 2.9 s VM, about 3.3 s laptop (about 3 percent) | about 3.0 s VM (exec 9.6 to about 6.6 s) | about 16.4 s VM (about 0.8 percent) |
| Step 3 persistent Python stream (design, not re-measured here) | same about 3 s as the CLI binary, does not stack with it | same about 3 s | same about 16 to 18 s |
| Pure Python CPU at 20x, whole harness (W3 bound) | 1.43 s (1.4 percent) | about 1.9 s (exec 9.6 to about 7.7 s) | about 2 s (0.1 percent) |

### A full rewrite

A full rewrite means porting about 37,152 lines of Python across scripts/ and tests/ (rust-anything-read.md section 3), biggest files scripts/cu.py 2,158 lines, scripts/tc02_controller.py 1,641, scripts/session_remote.py 1,556, scripts/sync-installed.py 1,191. Most of that code is I/O, subprocess management, Hyprland IPC, sleeps, and stateful session driving, none of which a Rust port speeds, and much of which rust-anything cannot even export (section 3.1 of this report). The measured ceiling for the whole harness is 13.105 s of a 101 s model-loop task, and most of that ceiling is app waits, sleeps, OCR, and spawn overhead, not Python CPU. The most generous honest full-rewrite estimate is the W3 bound: 20x on pure Python CPU plus a persistent transport, about 4.3 to 5.2 s saved, task 101 s to about 96 s, about 5 percent faster. On H1 it is about 2 s of 1974 s, 0.1 percent. On the deterministic run it is execution 9.6 s to about 4.7 s, but end-to-end still about 10.5 s, missing the 10 s target because P0, OCR, and app waits are untouched.

Cost side, measured: rust-anything took 4m 25s just to build itself; the W4 leaf port (166 lines Python to 495 lines Rust) took about 10 minutes of worker time plus a 44 s build and still shipped slower; the W5 binary (a thin CLI front end, std-only) took about 15 minutes plus two bug-fix rebuilds. Scaling that by hand to 37,152 lines, with the async, generator, *args, callable, and PIL blockers forcing hand-written bridges throughout, is weeks of work for about 5 percent on the best task and 0.1 percent on the held-out task. The 10 s end-to-end target is not reachable by any harness rewrite: even a perfect harness leaves P0 (3.7 s), OCR (about 2.4 s), and dialog and finish waits (about 1.6 s) standing, which alone sum to about 7.7 s before a single action runs.

One number is missing and is stated as missing, not estimated: no full-rewrite prototype was built, so there is no measured full-rewrite time. The estimate above is an Amdahl bound from measured parts, not a measured whole. It is an upper bound, and the W4 result (a real port running slower than Python) shows real ports can land below their bound.

## 7. RECOMMENDATION: STAY PYTHON

Decision, from the numbers, no hedge: stay Python. Do not do a full Rust rewrite. Do not port the observation store. Do the transport fix in Python (Step 3), and keep the Rust CLI binary only as a proven fallback.

Reasons:

1. The ceiling is too small. Pure Python CPU Rust could speed is 1.0 to 1.5 s of a 101 s task. A 20x speedup there is 1.4 percent. Zeroing the entire broker service is only 1.15x. No rewrite of the harness can move a task dominated by 52.8 s of executor gaps and 35.1 s of head and tail.
2. The best-measured Rust port is slower than Python. The observation store, the largest pure-harness CPU block W3 could find, benches 0.24x overall and 0.00x to 0.01x on bytes, because the $bytes codec costs 50x to 400x the work it saves. Its measured saving is 0.03 ms per task. Shipping it would make the harness slower.
3. The one real Rust win is not Rust-specific. The CLI-spawn binary saves about 3.0 s per task, but a persistent Python client is faster per request (0.2 to 0.4 ms vs 2.2 to 2.6 ms) and Step 3 already owns that saving. Paying for a Rust binary to capture a saving Python captures better is the wrong trade.
4. The tooling does not fit this repo. rust-anything cannot export async def, generators, *args and **kwargs, callables, or PIL objects, and per-call ports of small functions run 0.68x to 0.95x. craft-anything does not port code at all. A full rewrite would be largely hand-written, not tool-assisted.
5. The 10 s target is unreachable from the harness side. Even a perfect harness leaves about 7.7 s of P0, OCR, and app waits. The remaining path to 10 s runs through faster app launch, faster or fewer OCR calls, and shorter executor gaps, which is Track 2 territory, not a language rewrite.

### What IS worth doing

- Step 3 persistent Python stream, first. It captures the same about 3 s as the Rust CLI binary, is faster per request, and removes the result-poll round trip as a separate spawn. This is the transport win, and it belongs in Python.
- Keep the W5 Rust session-remote binary on branch rust-rewrite-eval as a proven fallback, not as a shipped component. If Step 3 stalls on risk, the binary captures about 97 percent of the same saving with no broker change, at 74/74 diff fidelity. That is its value: insurance, not speed.
- Fix the validate defect in Python (rust-profile.md section 3, rank 3): load_image=False currently pays the full PNG re-decode plus two hashes on every act. Skipping the decode when the caller does not need the pixels is free, no Rust needed. Measured cost today is about 0.22 to 0.37 s per task.
- Revisit Rust only through a hand-written PyO3 module over native PyBytes, never through the rust-anything JSON $bytes codec, and only if a future profile names a bytes-heavy loop that Pillow does not already cover in C. The W4 report (section 6) names this shape. No such loop exists in the current measurements.

### What is NOT worth doing

- Full rewrite of computer-use-wayland in Rust. Weeks of work for about 5 percent on the best task, 0.1 percent on the held-out task, and still missing the 10 s end-to-end target.
- Shipping the W4 observation-store port. Correct (diff 5496/5496, gate 11/11) and slower than Python (bench 0.24x). Do not ship, do not reframe.
- Porting microsecond metadata helpers one by one (image_point, validate_coordinate_metadata, resize_dimensions, keyboard_groups, validate_actions). Combined they are under 1 ms per request; the tool's own bench says one PyO3 crossing costs more than the work.
- Any whole-app lift via rust-anything (app front-door, app lift) or any routing through craft-anything. Both are proven wrong for this repo.
- A persistent Rust client as a follow-up experiment. Its win over persistent Python would be under 0.5 ms per request, noise at task scale, and it needs the same stream design Step 3 already wrote.

## 8. Corrections log (numbers fixed during this evaluation)

- "Full suite 1127 tests in about 88 s": NOT VERIFIED on the VM at HEAD 21684e7. W3's run: python3 -m unittest discover -s tests -p 'test_*.py', Ran 1064 tests in 187.333 s, FAILED (failures=11, errors=68, skipped=16), log /tmp/rustprof-suite.log. The count differs (1064 vs 1127) and the run fails on the VM for environment reasons (missing native wtype binary, fcitx5 absent, no Hyprland, pinned-header build failures). This does not prove a code regression, but the 1127-in-88s claim must not be cited as verified until it is re-run on the laptop. (rust-profile.md section 6.)
- "cu.py --help 179.8 ms vs bare Python 38.3 ms": not reproduced. W5 medians are cu.py --help 105.5 ms (run 1) and 110.4 ms (run 2), bare Python 25.5 to 28.0 ms. (rust-experiment-cli-spawn.md section 7.)
- "About 140 ms of each spawn is interpreter plus imports": corrected to about 85 ms (interpreter 25.5 plus imports 59.5) for session_remote.py, with a further about 20 ms of __main__ recompile that is neither. (rust-experiment-cli-spawn.md section 7.)
- "Think-observe-think loop is 87.8 percent": the tc02-t1 number. For the best clean run t3 it is 52.3 percent gaps plus 34.7 percent head and tail. (rust-profile.md section 6.)
- "17x faster with rust-anything batch": best run only. Four runs on this VM: 7.3x, 3.1x, 4.8x, 17.0x. Median about 5 to 7x. (rust-anything-read.md Appendix A.)
- "W3 hot path rank 1, about 0.32 to 0.33 s per request": verified in shape, tightened in size. On the VM one spawn is about 107 ms, so one request cycle (2 spawns) is about 214 ms, and 29 spawns are about 3.1 s. (rust-experiment-cli-spawn.md section 7.)

## 9. Sources

- improvements/rust-profile.md (W3, 21:44): time breakdown, hot-path ranking, harness fraction, suite re-run caveat.
- improvements/rust-anything-read.md (W1, 21:50): tool loop, verified install, bench numbers, async gap, OOM finding, 17x dissection.
- improvements/craft-anything-read.md (W2, 21:33): irrelevance verdict, no transpiler, no Python parser, early alpha.
- improvements/rust-experiment-observation-store.md (W4, 22:01): diff 5496/5496, bench 0.24x, gate 11/11, $bytes codec root cause, do not ship.
- improvements/rust-experiment-cli-spawn.md (W5, 22:10): spawn breakdown, diff 74/74, before and after 42 to 65x, about 3.0 s per task, does not stack with Step 3.
- improvements/live-test-log.md (entries 21:30 to 22:11, 2026-11-18): evaluation start, phase completions, W4 and W5 closeouts.
- Underlying measurements cited through W3: improvements/10x-review-astra6.md, improvements/10x-executor-time.md, improvements/10x-observ-codex-report.md, improvements/test-scores.md, improvements/heldout-validation-results.md, improvements/opt-step2-report.md, improvements/opt-step3-design.md.
- Prototypes (VM only, not pushed yet): ~/workspace/rust-experiment-observation-store/, ~/workspace/rust-experiment-cli-spawn/.

## 10. Bai hoc

- Doi toc do bang phan tram tren tac vu that, khong phai bang lan tren ham nho. Mot ham nhanh hon 17 lan nghe rat lon, nhung neu ham do chi chiem 0.0005 phan tram tac vu thi tac vu gan nhu khong doi. Bai nay chung minh ca hai chieu: observation store dung 100 phan tram nhung cham hon Python, CLI spawn nhanh 42 den 65 lan nhung ca tac vu chi nhanh hon 3 phan tram.
- Tim cho nao that su ton thoi gian truoc khi doi ngon ngu. O day 52.8 giay la khoang trong giua cac request va 35.1 giay la dau cuoi, con toan bo broker chi co 13.1 giay. Rust khong cham duoc vao suy nghi cua model, khong cham duoc vao cho doi ung dung mo, khong cham duoc vao OCR cua tesseract. Doi ngon ngu ma khong doi cho ton thoi gian thi chi la doi cho dep.
- Kien truc thang ngon ngu. Khoan tiet kiem lon nhat (khoang 3 giay, bo spawn CLI) den tu viec giu mot client chay lien tuc, khong phai tu viec viet lai bang Rust. Python chay lien tuc con nhanh hon moi request so voi binary Rust chay mot lan roi tat (0.2 den 0.4 ms so voi 2.2 den 2.6 ms). Khi mot loi ich thuoc ve kien truc, hay lay no bang kien truc, dung tra gia bang mot cuoc viet lai.
- Cong cu trung thuc dang tin hon cong cu hua hen. rust-anything tu in ra "Do not ship this unit for speed" hai lan, va ca hai lan deu dung. Nghe cong cu noi khong, dung co gang bien cau khong thanh co.
- Bai hoc lon nhat cho muc tieu nhanh nhat moi cach: tran dau that su nam o Track 2, rut ngan khoang trong suy nghi, bot OCR, mo app nhanh hon, chu khong phai o viec viet lai harness. Rust da duoc thu nghiem tu te, co so lieu, va ket luan la khong dang. Dong track nay lai, giu binary CLI lam phuong an du phong, va do suc vao cho nao thuc su ton thoi gian.
