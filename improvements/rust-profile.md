# Rust rewrite profiling baseline: where time goes in computer-use-wayland

- Author: Luna 6 Max (W3, TRACK 1), executor for Pham Tuan
- Date: 2026-11-18, night shift. Work log (Asia/Ho_Chi_Minh): 21:31 task received, repo at main 21684e7 confirmed; 21:31-21:35 read 10x review, test-scores, held-out validation results, code-hotspots, Step 2 report, observation report; 21:35-21:41 VM microbenchmarks of the real code paths (script /tmp/rust-profile-bench.py, synthetic 901x1176 frame like the tc02 VS Code window); 21:41-21:44 full offline suite on the VM; 21:44 this file written.
- 21:43 update noted: the owner hit ESC at 21:41 and cancelled a live session (latch set, no live session running, relay still active). No live session was needed for this profile, so nothing was restarted and the latch was left alone.
- Repo: ~/workspace/computer-use-wayland, HEAD 21684e7. Code line numbers below are at this HEAD. cu.py is now 2158 lines (was 1568 when code-hotspots.md was written), session_remote.py 1556 lines, session_driver.py 152 lines, tc02_controller.py 1641 lines.
- Rule followed: every claim carries a measured number and a source. Numbers from the laptop logs are labelled laptop-log; numbers I measured on this VM are labelled VM-measured. No em dash or en dash is used anywhere in this file.

## 0. The chosen task

Primary task: tc02, VS Code note `on-tap.txt`, trial 3 (t3), the best clean model-loop run. It is the tc02-class realistic task with the most complete instrumented breakdown (per-request records on the laptop, parsed by two independent workers). Cross-check task: H1, the held-out Omawrite shopping-list case (5 lines, exact 105 bytes), run OPTIMIZED in 1974 s. Both share the same conclusion, so this baseline is usable for TRACK 2 as well.

Why tc02-t3 and not tc02-t1: t1 (823 s) is first-run discovery (Save As retry loop seq 6-31, stray Welcome window, 4 s menu settle), not the steady-state cost. t3 is the learned procedure, 14 requests, 10 delivered images, byte-exact 50/50. t1 is cited alongside for the cold-path contrast.

## 1. Time breakdown: tc02-t3 (model loop, 101 s)

Total is ready-to-finish, 101 s. Sources: 10x-review-astra6.md section 1-2, 10x-executor-time.md section 1-2, 10x-observ-codex-report.md section 2-3. All three agree on these numbers.

| Part | Seconds | % of 101 s | Source |
|---|---:|---:|---|
| Session start to ready | 2.0 | 2.0% | test-scores.md tc02-t3: ready in 2.0 s; 10x-executor-time.md table |
| Broker service, all 14 requests (submission to result receipt) | 13.105 | 13.0% | 10x-executor-time.md table; 10x-review-astra6.md section 2 |
| Between-request gaps (executor think, read image, decide, build next request) | 52.813 | 52.3% | 10x-executor-time.md table; max single gap 11.834 s |
| Head and tail (ready to first request 25.978 s, last result to finish about 9.1 s) | 35.082 | 34.7% | 10x-executor-time.md section 1 (first request 25.978 s after ready); remainder by subtraction 101 - 13.105 - 52.813 |
| Total | 101 | 100% | |

Inside the 13.105 s of broker service (laptop-log):

| Sub-part | Seconds | Source |
|---|---:|---|
| Image-bearing request intervals, 10 images | 9.630 (mean 0.963 s) | 10x-observ-codex-report.md section 2 table |
| Non-image request intervals (windows, status, finish) | 3.475 | 9.630 subtracted from 13.105 |
| Timed capture/decode/encode stages inside the images | 1.58 total (capture_elapsed mean 115.0 ms + PNG encode mean 43.5 ms = 158.5 ms per image, 10 images) | 10x-observ-codex-report.md section 3 table |
| PNG payload delivered | 573,507 bytes, mean 57,351 bytes per image | 10x-observ-codex-report.md section 2 table |
| Result-poll sleep inside service | up to about 7 s (L3 helper sleeps 0.5 s before each result poll, 14 requests) | 10x-observ-codex-report.md section 3; 10x-executor-time.md section 2 |

What the logs cannot split (stated honestly): the 52.813 s gap has no inference start/end timestamps, so no sub-claim such as "thinking alone is X s" is made. The correct claim is "inter-request waiting dominates". The 0.5 s poll sleep and the 25.978 s first-request delay are caller-side, not broker-side: there is no broker state that holds the first request back (10x-executor-time.md section 2).

Cold-path contrast, tc02-t1 (823 s, 36 requests): service 37.721 s (4.6%), gaps 722.955 s (87.8%), max gap 101.395 s, head/tail about 62 s. Baseline failed run (1195.417 s, 25 requests): service 16.171 s (1.35%), gaps 1078.926 s (90.26%). tc01 Pinta (1550 s, 63 requests, 5 sessions): service 58.037 s (3.7%), gaps 1444.847 s (93.2%). The pattern is the same at every scale: service is 1-13%, gaps are 52-93%.

Held-out cross-check, H1-OPT3 (1974 s, 78 broker requests, 40 observations, 36 act requests, 112 actions, SUCCESS byte-for-byte 105 bytes): broker round-trips 0.1-2.5 s each, executor gaps 15-90 s each (heldout-validation-results.md). At the prior attempt's measured broker mean of about 0.45 s, total broker service is about 35 s, 1.8% of 1974 s. Even at the maximum 2.5 s per request it is at most 195 s, 9.9%. H1-BASE (1080 s to save, FAIL, 96 requests, 61 single-action acts) reached a saved file faster but with the wrong filename and 3 content errors, so its time is not a valid speed datapoint. H1 confirms the tc02 finding on unseen UI: the broker is never the bottleneck, the executor loop is.

## 2. The deterministic controller run (the harness ceiling)

Step 2 gate runs, tc02 via the local tc02_controller.py, no model round trips between steps (opt-step2-report.md). Run A2: execution 9.5962 s, end-to-end 13.4469 s. A1r2 9.6831/13.5265 s, A3 9.8992/13.7684 s, B1 cold 9.8188/13.6898 s. Byte-exact 50/50 in all 4, OCR crop hit 8/8, zero fallbacks, delivered image bytes down 46% (259 KB to about 140 KB).

| Step | A2 seconds | What it is |
|---|---:|---|
| P0 | 3.70 | VS Code cold launch to a mapped 901x1176 window (end-to-end only) |
| P1 | 2.53 | Session start: start CLI about 0.76 s + 3 status polls about 0.24 s each + 2 x 0.5 s sleeps |
| G0 | 1.02 | Windows round trip 0.32 s + observe round trip 0.33 s + crop OCR 0.26-0.30 s |
| S1 | 1.25 | Act receipt 0.85-0.88 s (exec 0.28 s + after-capture 0.14-0.21 s + CLI overhead) + crop OCR 0.30-0.36 s |
| S2 | 1.60 | Act 0.91-0.96 s (474 ms wait + about 115 ms work + CLI overhead) + dialog poll 0.65-0.80 s (dialog spawns about 0.44 s after the row click) |
| S3 | 0.34 | One crop-observe round trip |
| S4 | 0.90 | Act exec 434-471 ms + after 87-125 ms |
| S5 | 1.18 | Act 0.62 s + windows 0.53 s |
| S6 | 0.79 | Crop observe 0.33 s + finish 0.47 s |

Per-request floor (Step 2 report, Residual budget): every broker_driver call is a request CLI (0.13-0.19 s) plus a result CLI (0.11-0.25 s); instant commands cost about 0.32-0.33 s round trip; 12 task requests carry roughly 3 s of round-trip floor. This is the quantified trigger for the persistent-stream Step 3, not a guess. Even a perfect 8 s execution leaves end-to-end near 11.7 s because P0 alone is 3.7 s.

## 3. Hot paths, measured on the VM (ranked by seconds per task)

Method: cProfile-style direct timing with timeit (best of 3) of the real functions from scripts/cu.py at HEAD 21684e7, synthetic 901x1176 RGB frame like the tc02 window, plus a 1853x1176 frame like the old tc02 run. Script: /tmp/rust-profile-bench.py. VM: Python 3.12.3, PIL 10.2.0, 4 shared vCPU. VM times run about 1.5-2x the laptop's recorded stage times (laptop capture_elapsed 115 ms vs VM save_observation 88 ms is the exception, the VM is faster on pure PIL work), so per-task totals below use laptop-log stage times where they exist and VM times elsewhere, and each row says which.

Call counts per tc02-t3 task: 14 requests, 10 delivered images, 7 act requests, about 17 persisted observations (10 delivered plus 7 after-captures), 7 preflight re-captures with persist=False.

### Rank 1: per-request CLI process spawn plus result polling

- Function: session_remote.py _exchange() (line 1273) and main() (line 1468), driven by tc02_controller.py broker driver subprocess calls (lines 390-405); the long-poll path already exists in the controller (result-long-poll emit, poll_waste_s 0.0, lines 508-510).
- Per-call cost, laptop-log: request CLI 0.13-0.19 s + result CLI 0.11-0.25 s, instant commands 0.32-0.33 s round trip (opt-step2-report.md). VM-measured: `cu.py --help` 179.8 ms per call (mean of 5) vs bare `python3 -c pass` 38.3 ms, so about 140 ms is interpreter startup plus imports per spawn.
- Call count per task: 14 requests x 2 CLI calls (request + result) = 28, plus start and finish, about 30 spawns.
- Per-task total: about 3-4 s in the deterministic run (12 requests x about 0.3 s floor, 31% of 9.6 s execution), about 3.4-6.2 s inside tc02-t3 service. This is the largest task-level harness cost.
- Honest caveat: killing it needs a persistent client, not a faster language. A persistent Python client would remove the same 3-4 s. Rust only wins here if the port is built as a persistent binary, and the win is architectural, not from Rust being faster than Python.

### Rank 2: observation persist, save_observation()

- Function: scripts/cu.py save_observation() (lines 824-890).
- Per-call cost, VM-measured: 87.8 ms per call (n=10, best of 3; recorded encode_ms 70.9 ms in that run). Components, VM-measured: PNG encode 901x1176 level 1, 39.1-55.4 ms across runs; pixel sha256 (tobytes + hash), 13.6-25.1 ms; PNG sha256, 0.027 ms; file writes plus iterdir sweep, about 0.02 ms. persist=False costs 0.35-0.52 ms, proving the persist path is encode plus hashing, not validation.
- Call count per task: about 17 persisted saves (10 delivered + 7 after-captures). Preflight re-captures use persist=False and cost almost nothing.
- Per-task total: about 1.5 s per tc02-t3 task.
- Honest caveat: the PNG encode is libpng/zlib in C through Pillow, already native code. A Rust port only wins here with a faster PNG encoder than libpng level 1, not by rewriting Python. The resize branch (LANCZOS, VM-measured 69.6-121.0 ms for 1853x1176 to 960x612) does not run for the 901-wide tc02 window, it only matters for old 1853-wide frames.

### Rank 3: observation re-validation, validate_desktop_observation()

- Function: scripts/cu.py validate_desktop_observation() (lines 770-822).
- Per-call cost, VM-measured: load_image=True 30.8-52.8 ms; load_image=False 33.3-49.3 ms.
- Call count per task: 7, one per act request.
- Per-task total: about 0.22-0.37 s per tc02-t3 task.
- Defect found by measurement: load_image=False costs the same as True. When observation_path is set, the code always re-reads the PNG from disk, re-decodes it with PIL, and re-verifies both hashes (lines 792-821); the flag only controls whether the decoded copy is returned. The preflight validation therefore pays a full decode plus two hashes on every act, even when the caller does not need the pixels.
- Supporting micro-costs in the same path, VM-measured: screen_changed() (lines 986-999) 7.7-14.3 ms per call, 7 per task, about 0.06-0.10 s total; PPM decode (grim output) 2.2-4.7 ms; iterdir sweep 0.019 ms.

### Largest step cost Rust cannot speed: OCR (tesseract, already a C/C++ binary)

- Function: tc02_controller.py _ocr_text() (lines 1081-1137), subprocess to tesseract --psm 6.
- Per-call cost, laptop-log: crop OCR 0.26-0.36 s, full-frame OCR 0.79-0.98 s (opt-step2-report.md). VM-measured on the synthetic frame: menu crop 500x40, 174 ms; line crop 901x60, 182 ms; full frame 901x1176, 633 ms (best of 3; crops returned empty text on the synthetic image because of its tiny default font, timing only).
- Per-task total: 8 crop OCRs, about 2.1-2.9 s of the 9.6 s Step 2 execution (22-30%). A Rust port of the harness does not touch this at all. Any experiment claiming an OCR win must replace the OCR engine, which is out of scope for a harness port.

### Measured as NOT hot (microseconds, do not port for speed)

VM-measured, best of 3: image_point() (cu.py:980) 0.012 ms; validate_coordinate_metadata() (cu.py:691) 0.013-0.014 ms; check_cancel() (cu.py:570) 0.008 ms with no session token; keyboard_groups() (cu.py:1082) 0.004 ms; validate_actions() (cu.py:1011) 0.061-0.074 ms for a 5-action tc02-like list; key_names() (cu.py:52) 0.021-0.023 ms for 3 keys; json.loads of a 12-window hypr clients list (4946 bytes) 0.049-0.166 ms; sha256 of a 1 KB broker envelope line 0.002 ms. All coordinate math, validation, grouping, and JSON parsing combined is under 1 ms per request. The "Python is slow" intuition fails here: the metadata path is already negligible.

Unmeasured on the VM (needs the laptop compositor or broker, not attempted): grim fork/exec time on the real host (laptop-log capture 78 ms warm, code-hotspots.md section 1.1), Hyprland Unix-socket round-trip time (no compositor on the VM), SSH/Tailscale transfer time (laptop-log image receipt markers land about 0.0038 s after result receipt in total, but that is caller bookkeeping, not transfer time), wtype process cost (keyboard_argv could not run on the VM: private wtype helper missing, native/wtype absent), and fcitx5 IME switch budgets (up to 0.5 s off + 0.5 s restore per literal keyboard group, code budgets in cu.py:1132-1195, actual time unmeasured).

## 4. Harness fraction: the honest math

Definition: harness = broker service plus capture/encode plus CLI overhead, i.e. everything inside local transactions, excluding model think, executor gaps, and app waits (dialog spawn, VS Code launch, fixed sleeps). Two tasks, two fractions.

### Model-loop task, tc02-t3 (101 s)

| Slice | Seconds | % of task |
|---|---:|---:|
| Total task | 101 | 100% |
| Broker service (absolute ceiling for all harness + app-wait work) | 13.105 | 13.0% |
| Inside service: result-poll sleep, L3 helper only (0.5 s x 14) | up to about 7 | up to 6.9% |
| Inside service: CLI spawn floor (about 0.3 s x 14) | about 3.4-6.2 | 3.4-6.1% |
| Inside service: timed capture/decode/encode (laptop-log) | 1.58 | 1.6% |
| Inside service: validation, diff, app waits, remainder | about 1-2 | 1-2% |
| Pure Python CPU that Rust could speed (encode wrapper excluded, it is C; hashing, validation, diff, JSON, grouping) | about 1.0-1.5 | 1.0-1.5% |

20x speedup math for tc02-t3:
- 20x on pure Python CPU only (1.5 s): saves 1.5 x 19/20 = 1.43 s. Task 101 s becomes about 99.6 s, 1.4% faster.
- 20x on Python CPU plus eliminating CLI spawns with a persistent binary (about 3-4 s): saves about 4.3-5.2 s. Task becomes about 96 s, about 5% faster.
- Zeroing ALL broker service (13.105 s, impossible, it includes app waits and sleeps): task becomes 87.9 s, 1.15x. This matches the Amdahl bound in 10x-review-astra6.md section 2.

### Deterministic task, Step 2 run A2 (execution 9.5962 s, end-to-end 13.4469 s)

| Slice | Seconds | % of execution |
|---|---:|---:|
| Execution | 9.60 | 100% |
| Pure Python CPU (capture/encode wrapper, validation, diff) | about 1.5-2.5 | 16-26% |
| CLI spawn floor (about 0.3 s x 12) | about 3 | 31% |
| OCR tesseract (C binary, Rust cannot speed) | about 2.1-2.9 | 22-30% |
| App waits (dialog spawn 0.44 s, S2 wait 474 ms, finish 0.47 s, dialog poll remainder) | about 1.5 | 16% |
| Session start P1 (start CLI, polls, 2 x 0.5 s sleeps) | 2.53 | 26% (overlaps with the rows above in wall time accounting, listed separately in the step table) |

20x speedup math for the deterministic run:
- 20x on pure Python CPU only (about 2 s): saves about 1.9 s. Execution 9.6 s becomes about 7.7 s, 1.25x.
- If the Rust binary is also persistent (removes about 3 s of CLI spawns): execution becomes about 4.7 s, 2.0x; end-to-end 13.5 s becomes about 10.5 s. Still short of the 10 s end-to-end target, because P0 VS Code cold launch (3.7 s), OCR (about 2.4 s), and dialog/finish waits (about 1.6 s) are untouched by a harness port.

### Held-out task, H1-OPT3 (1974 s)

Broker service about 35 s at the measured mean 0.45 s per request (1.8% of task); at most 195 s at the 2.5 s maximum (9.9%). Pure Python CPU inside that is on the order of 2 s. A 20x harness speedup saves about 2 s of 1974 s, 0.1%. H1 is the least harness-sensitive task in the set, because its cost is 112 actions of executor deliberation plus Omawrite auto-formatting diagnosis (slowest step about 10.5 min).

## 5. First port candidate

**#1 port candidate: the observation persist plus validate pipeline, save_observation() (scripts/cu.py:824) + validate_desktop_observation() (scripts/cu.py:770), as one "observation store".**

Why this one: it is the largest measured pure-harness CPU block that runs on every step (about 1.5 s persist + about 0.3 s re-validation per tc02-t3 task), it has two concrete defects a port can fix (PNG and pixel hashes computed twice per observation, once at save and once at validate; load_image=False still paying the full decode plus hash cost), and it is self-contained (bytes in, verified frame out) with exact oracles already in the test suite (byte-exact read-backs, hash checks).

What it will not do, stated plainly: even a perfect port of this pipeline is about 1.8 s of a 101 s model-loop task (1.8%) and about 1.8 s of a 9.6 s deterministic execution (19%). The bigger task-level lever is the transport, a persistent client that kills the per-call CLI spawns (about 3-4 s per task), but that win is architectural and achievable in Python too, so it is not a Rust-specific result and should be measured as a separate experiment arm (persistent Python client vs persistent Rust binary), not credited to the language.

## 6. Claims checked, corrections to the starting numbers

- "Think-observe-think loop is 87.8% of task time": VERIFIED for tc02-t1 (gaps 722.955 s of 823 s, 10x-executor-time.md). For the best clean run t3 it is 52.3% gaps plus 34.7% head/tail, 87.0% outside service combined. The 87.8% figure is the t1 number, not the steady-state number.
- "Agent think gaps 25-150 s": PARTLY CORRECTED. Max single gaps: t1 101.395 s, t3 11.834 s, tc01 223.915 s, tc05 101.516 s. The judge's summary had t2 max gap as about 40 s and t3 as about 25 s; the raw records prove 20.993 s and 11.834 s (10x-executor-time.md section 1).
- "Broker requests 0.11-0.61 s": VERIFIED as the range for the prior H1 attempt (mean about 0.45 s, heldout-validation-results.md). H1-OPT3 ranged 0.1-2.5 s. Step 2 instant commands measure 0.32-0.33 s round trip.
- "Step 2 exec 9.60-9.90 s / e2e 13.45-13.77 s": VERIFIED (A1r2 9.6831/13.5265, A2 9.5962/13.4469, A3 9.8992/13.7684, B1 9.8188/13.6898, opt-step2-report.md).
- "H1-OPT PASS 1974 s": VERIFIED (heldout-validation-results.md, byte-for-byte 105-byte MATCH, verified 3x).
- "Full test suite 1127 tests in about 88 s": NOT VERIFIED on this VM at HEAD 21684e7. My run: `python3 -m unittest discover -s tests -p 'test_*.py'`, Ran 1064 tests in 187.333 s, FAILED (failures=11, errors=68, skipped=16), log /tmp/rustprof-suite.log. The count differs (1064 vs 1127) and the run fails on the VM for environment reasons (missing native wtype binary, fcitx5 absent, no Hyprland, pinned-header build failures; e.g. test_cursor_session fails to import, test_keyboard_preflight errors cluster on the missing wtype helper). This does not prove a code regression, the failures look environmental, but the 1127-in-88s claim must not be cited as verified at this HEAD until it is re-run on the laptop. Do not use the suite time as a Rust baseline until that re-run exists.

## 7. What the experiment phase should measure next (not done here)

- Persistent Python client vs persistent Rust binary on the Step 2 deterministic run, same 12 requests, to separate the architectural win (no spawns) from the language win.
- The observation store port (section 5) against the same run, with per-step timings, to confirm the predicted about 1.8 s.
- A re-run of the full offline suite on the laptop at HEAD 21684e7 to settle the 1127-test claim.
- No live laptop session was used for this profile and none is needed for the next two items; they are VM-side builds plus the existing detached harness runs.

## Sources

- improvements/10x-review-astra6.md (Astra 6, 17/11): t1/t2/t3 decomposition, Amdahl bound, 10 s target.
- improvements/10x-executor-time.md and improvements/10x-think-codex-report.md: per-request service vs gap tables, first-request delays, max-gap corrections.
- improvements/10x-observ-codex-report.md: image counts, PNG bytes, capture/decode/encode stage times, poll-sleep analysis.
- improvements/test-scores.md (independent judge, 17/11): 130/130, per-case evidence, readiness 1.8/2.0/2.1 s.
- improvements/heldout-validation-results.md: H1-OPT3 1974 s SUCCESS, H1-BASE 1080 s FAIL, broker 0.1-2.5 s, gaps 15-90 s.
- improvements/opt-step2-report.md: Step 2 gate runs, step spans, per-request floor, OCR crop times, residual budget.
- improvements/code-hotspots.md (15/11, older line numbers): per-request hyprctl fork, 3 captures per act, indicator round trips, IME budgets. Line numbers have drifted since (cu.py 1568 to 2158 lines); this profile re-checked the cited functions at HEAD 21684e7.
- improvements/heldout-generated-test-cases.md: 68 held-out cases, H1 baseline 1974 s.
- VM measurements: /tmp/rust-profile-bench.py (this run), /tmp/rustprof-suite.log (full suite, 1064 tests, 187.333 s).
