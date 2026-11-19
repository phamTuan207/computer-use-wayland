# Local small-model cascade for routine steps (Rank 1 / M4)

- Owner: Pham Tuan. Date: 2026-11-19, evening Asia/Ho_Chi_Minh.
- Worker: Luna 6 Max, cascade prototype. Report to the resume coordinator round 2, not to the user.
- Branch: `cascade-local-model`, from origin/speed-swarm 8727135. Worktree: /home/james/cu-cascade (the shared main checkout was left untouched on its own branch).
- Status: GATE DONE, PROTOTYPE BUILT AND TESTED, LIVE A/B NOT ATTEMPTED (broker busy with the R3 live run and other live measures). READY-FOR-LIVE-MEASURE with the 7B configuration below.
- No em dash or en dash in this file.

## 0. Verdict up front

- Qwen2.5-3B-Instruct (4-bit) FAILS the accuracy gate: 2 of 9 routine steps wrong, both confident (1.0 / 0.95), both uncaught by the deterministic postcondition. Do not use 3B for routine loop steps.
- Qwen2.5-7B-Instruct (4-bit, partial GPU offload) PASSES the accuracy gate: 0 of 9 wrong, 3 safe escalations, mean 1.59s per call. This is the cascade model.
- Llama-3.1-8B-Instruct was not downloaded or tested: same size class as the 7B (about 4-5GB 4-bit), so the VRAM verdict transfers by size, but its accuracy is unmeasured. Do not substitute it without its own gate run.
- Full GPU offload of 7B alongside voxtype FAILS (KV cache allocation error). 7B runs only as partial offload (20 of 28 layers on GPU) with voxtype running, or whole with voxtype stopped (unmeasured, do not claim).
- The deterministic postcondition catches format errors and hallucinated citations, but it CANNOT catch a wrong-but-listed window pick or a wrong pass=false verdict backed by verbatim evidence. Both failure modes were proven by the 3B run. The 7B gate had zero such cases in 9, but n=9 is small; the live A/B must count wrong answers explicitly.

## 1. Gate measurements

Runtime: llama.cpp b12359, cudart CUDA 12.8 x64 binary, served by llama-server on 127.0.0.1:8088. GPU: RTX 4050 Laptop 6141 MiB. voxtype running the whole time (1552 MiB). ComfyUI stopped (not running) the whole time. Disk was 96-98% full during the gate; see section 6.

### 1.1 Qwen2.5-3B-Instruct Q4_K_M (1,929,903,264 bytes, size-verified against HuggingFace)

- Load: server ready about 2s after start (model loaded about 0.7s after process start per server log).
- VRAM: 1570 MiB used before, 3741-3745 MiB used after load, 2109-2113 MiB free. Model cost about 2.17GB. Fits alongside voxtype with room to spare. (The Pick 3 figure of 88 MiB free was with ComfyUI at 1800 MiB also running; ComfyUI was not running here.)
- Latency (CLI wall, python startup plus HTTP, steady state): mean 447-457ms, max 682-715ms over 9 calls. Server-side predicted 290-710ms.
- Accuracy, gate harness 9 cases (live state: hyprctl clients, df, du, ls of a scratch dir): 6 correct, 2 wrong, 1 escalated.
  - W2 WRONG: goal "the web browser window", picked the herdrdrop scratchpad (org.omarchy.herdrdrop, "omarchy: Jarvis") at confidence 0.95 instead of Zen. Address was listed, so the postcondition could not catch it.
  - V2b WRONG: du output top line "2.7G /tmp/pill-video", condition "the largest entry in /tmp is pill-video" is TRUE, model answered pass=false at confidence 1.0 with the verbatim proving line as evidence. This is the Pick 2 L2-2 regression case (Luna L2 also got it wrong at confidence 1.0); the 3B model repeats the exact failure.
  - W4 escalated (safe): correct null answer for "the calculator window" but confidence 0.00, below the 0.70 threshold, so it escalated instead of being used.
  - V1, V2, V3, V4, F1, F2 correct. V1 ground truth is computed live from df Avail (the disk filled during the gate as the 7B file downloaded, so a hardcoded want would have gone stale; fixed in the harness).
- Evidence pattern worth noting: in every wrong-judgment case the model's cited EVIDENCE was right while its JUDGMENT was wrong (V1 probe: evidence line proves True, judged False; V2b: same). The 3B model extracts correctly and judges wrong. That points at a redesign (model as extractor, code as judge on typed conditions) rather than a prompt tweak; see section 5.

### 1.2 Qwen2.5-7B-Instruct Q4_K_M (4,683,074,240 bytes, size-verified)

- Full GPU offload (99 layers, ctx 4096): FAILS to load. Server error: "failed to allocate buffer for kv cache". Weights 4.68GB plus KV cache do not fit in 4284 MiB free alongside voxtype.
- Partial offload (20 of 28 layers on GPU, ctx 2048): loads about 1.2s after process start, health ok. VRAM 1570 MiB used before, 4881-4901 MiB used after, 953-973 MiB free.
- Latency (CLI wall, steady state): mean 1590ms, max 1991ms over 9 calls. Slower than 3B (CPU holds 8 layers) but still about 3-5x faster than a Luna framing think (4.9-7.7s per step).
- Accuracy, same 9-case harness: 6 correct, 0 wrong, 3 escalated.
  - W2 CORRECT: picked Zen (0x5564a6338420) at confidence 1.0.
  - V2b CORRECT: pass=true with verbatim evidence "2.7G /tmp/pill-video".
  - Escalations, all safe (fell back to Luna instead of being used): W4 (null answer, confidence 0.20), V2 (confidence 0.00), V4 (evidence not verbatim in observation).
  - V1, V3, F1, F2 correct.
- Full offload with voxtype stopped was NOT tested. It would free 1552 MiB (about 5836 MiB free vs about 5.2GB needed), so it is plausible, but stopping his dictation service was not done for a gate measurement. If the A/B wants full offload, that is a separate decision with a visible cost to him.

### 1.3 Derived saving (not measured live)

Framing steps cost 19.3s of Luna think per clean task (windows 4.9s + first observe 7.7s + verify observe 6.7s). At 7B partial offload, three routine calls cost about 3 x 1.6s = 4.8s. Escalation rate in the gate was 3 of 9 calls (one per task on average), each escalation costs one Luna think of about 5-7s. Expected framing about 4.8s + 6s = about 10.8s, saving about 8.5s per task (DERIVED). The 3B shape would have cost about 1.4s but with a 22% wrong-answer rate, which fails the success bar. The live A/B must measure the real number; the derived figure is only for sequencing.

## 2. Luna reference on the same steps

Two real Luna invocations (codex exec, gpt-6-luna, max effort, text-only, same prompt text as the gate) on the two 3B-wrong cases:

- V2b (largest entry in /tmp): Luna answered {"pass": true, "evidence": "2.7G /tmp/pill-video", "confidence": 1}. CORRECT. This is the decisive case: 3B wrong at confidence 1.0, 7B correct, Luna correct. The 3B failure is a small-model failure, not a bad case.
- W2 (browser window): Luna answered {"address": "0x5564a6607d40", "confidence": 0.51}, the Chromium window. The harness want was Zen (first browser listed). Both Zen and Chromium were open at Luna-check time, so the goal "the web browser window" is AMBIGUOUS with two browsers, and Luna's low confidence (0.51) signals exactly that. The case is weak as designed (it needs a distinguishing title, e.g. "the Zen browser window"); the honest read is: 3B's pick (the herdrdrop scratchpad at 0.95) is clearly wrong because a scratchpad is not a browser, 7B's pick (Zen at 1.0) matches the harness want, and Luna's pick (Chromium at 0.51) is a reasonable answer to an ambiguous goal. Do not score W2 as a clean Luna-vs-model comparison.

My own Luna judgments on all 9 cases (same inputs): W2 Zen, W4 null, V1 per live Avail, V2 false, V2b true, V3 true, V4 false, F1 true, F2 true. The spot-check above grounds the two decisive cases with independent invocations rather than my own judgment alone.

## 3. What was built

Branch `cascade-local-model` (from 8727135). Three new files, no changes to existing files. Flag-gated, default OFF.

- `scripts/local_cascade.py`: the cascade module plus CLI.
  - Steps: `windows` (pick one window from a hyprctl clients list), `verify` (judge one condition against observation text), `finish` (confirm the goal from final state text), `health` (server check).
  - Transport: stdlib urllib POST to llama-server /completion with a JSON schema (constrained output), temperature 0, 256 output tokens, 30s timeout. No new dependencies.
  - Deterministic escalation (never a judgment call by the small model). An answer is used only when all hold: valid JSON matching the step schema, confidence at or above 0.70, and the postcondition passes (windows: address exists in the given clients list; verify/finish: a pass=true answer cites evidence appearing verbatim, whitespace-normalised, in the observation). Anything else returns escalate=true with a machine-readable reason, and the executor falls back to a Luna think call. Act composition is never routed to the small model.
  - CLI prints one JSON object on stdout, exit 0 on every handled outcome including escalate. Disabled flag prints escalate JSON.
- `scripts/cascade_server.sh`: start/stop/status for llama-server. Env-overridable binary, model, port, GPU layers, ctx size. Refuses a second server on the same port. No broker or desktop changes.
- `tests/test_local_cascade.py`: 27 unit tests, all passing, no broker, no desktop, no model calls (fake transport injected). Covers flag default, prompt building, validator boundaries (confidence 0.69 escalates, 0.70 passes, confidence 1.0 with an unknown address still escalates), verbatim evidence rules, transport failure escalation, and CLI disabled/unreachable paths. One test documents the residual risk explicitly: a wrong-but-listed window pick passes the postcondition and needs the downstream focus check, same as a Luna pick.
- Gate harness (NOT committed, lives at /tmp/cascade-gate/gate-cascade.py on the laptop): builds cases from live machine state, calls the real CLI once per case, scores against ground truth computed from the same live state. Results in /tmp/cascade-gate/gate-3b-v3/ and /tmp/cascade-gate/gate-7b/.

## 4. Tests

- New tests: 27/27 OK (tests.test_local_cascade, 0.104s).
- Full suite baseline at 8727135 in the worktree, AFTER the artifact fix: 1339 tests, 7 failures, 0 errors, 2 skipped, 106.513s. The 7 failures are pre-existing on this commit: 5 DoctorCliTests (the known allowed set), test_cli_list_includes_chromium, and test_screen_refusal_keeps_session_then_fresh_act_succeeds.
- Full suite after (with the 3 new files): 1366 tests (1339 + 27 new), 7 failures, 0 errors, 2 skipped, 104.963s. FAIL set IDENTICAL to the clean baseline. Zero new failures.

## 5. Design notes and open questions

- The 3B evidence pattern (right evidence, wrong judgment) suggests the durable shape is model-as-extractor plus code-as-judge on typed conditions (threshold, contains, equals), not model-as-judge on free-form conditions. That redesign was NOT built in this prototype; the prototype keeps the judge shape with deterministic escalation, and the 7B gate passes in that shape. If the live A/B shows judgment errors at 7B, the extractor redesign is the next step, not a bigger model.
- The false branch is weaker than the true branch by construction: a pass=false answer with empty evidence passes validation, and a pass=false answer with any verbatim line passes too. The validator pins the true branch (evidence must prove it) and relies on the model's honesty plus the confidence threshold on the false branch. The 7B gate had no false-branch errors in 9 cases; watch it in the A/B.
- The server start script's readiness poll reported "ready after 2s" for the failed 7B full-offload start (the process died right after). The poll is weak: it only checks the port answers. A real readiness check should call /health and confirm status ok, and the A/B executor brief should run `health` before the first routine call.

## 6. Cleanup and machine state

- 7B server (partial offload) STOPPED at handoff. Leaving it running would hold about 3.3GB VRAM and block his ComfyUI/Qwen image work, so the A/B executor must start it (section 8 step 1). 3B server was stopped before the 7B start.
- Model files under /home/james/.cache/cascade-gate/: Qwen2.5-3B-Instruct-Q4_K_M.gguf DELETED at cleanup (1.93GB, failed the gate, no reason to keep it); Qwen2.5-7B-Instruct-Q4_K_M.gguf KEPT (4.68GB, passed, needed for the A/B); llama.cpp b12359 binaries plus cudart libs KEPT extracted (about 1.4GB); both download tarballs DELETED (about 793MB, re-downloadable). Disk freed about 2.7GB at cleanup.
- No desktop changes. No Zen tabs touched, no Jarvis/music touched, no broker session started, no relay restart. The gate used only read-only hyprctl/df/du/ls plus the local server.
- Live A/B needs: broker free, 7B server up (partial offload, port 8088), CU_LOCAL_CASCADE=1 in the executor env, and the brief in section 8.

## 7. Worktree suite gap (found by the A4 worker, fixed during this task)

A fresh worktree lacks the gitignored native binaries (native/wtype etc.) and generated *-protocol.c/.h files, so the full suite there errors 66 tests and hides 23 more. My first baseline run showed exactly that (1316 tests, 9 failures, 66 errors, 2 skipped). Fix, per the A4 finding: copy the ignored build artifacts from the main checkout into the worktree (never commit them). I copied the 18 ignored files under native/ via tar from /home/james/computer-use-wayland. After the copy, git status shows only my 3 new files as untracked, and the clean baseline re-run is the true baseline in section 4. Do not diagnose those 66 errors as code failures.

## 8. A/B executor brief (for the coordinator to use when the broker is free)

Cascade arm, same 4 held-out tasks as the profile (P1 C-03, P2 E-04, P3 B-01, P4 A-01) plus D1 where it touches the browser, same timed.py wrapper, fresh broker session and fresh lease per task, baseline arm first, then cascade arm. Report wall (headline), think total, per-step model used, escalation count, wrong-answer count, misclicks.

Setup before the cascade arm:
1. Start the 7B server: `CU_CASCADE_MODEL=/home/james/.cache/cascade-gate/Qwen2.5-7B-Instruct-Q4_K_M.gguf CU_CASCADE_GPU_LAYERS=20 CU_CASCADE_CTX=2048 ./scripts/cascade_server.sh start` from the cascade-local-model checkout. Confirm with `./scripts/cascade_server.sh status` (health must say ok, VRAM used about 4900 MiB).
2. Export `CU_LOCAL_CASCADE=1` in the executor env.

Routine-step rules for the cascade arm (Luna executor):
- For the windows-listing step, first observe verification, and finish confirmation, run the local CLI and use its JSON when escalate=false: `python3 scripts/local_cascade.py windows --clients <hyprctl clients JSON file> --goal "<goal>"`, `verify --observation <file> --condition "<condition>"`, `finish --final-state <file> --goal "<goal>"`. Each call logs its own latency_ms.
- When the CLI returns escalate=true, think that step yourself (Luna max) as today. Never retry the CLI on the same step; one escalate means Luna does it.
- NEVER route act composition to the CLI. Act steps, recovery, and genuine ambiguity stay on Luna max.
- Log every routine call (step, model used, latency_ms, escalate reason, wrong-answer flag) in the run records. Count a wrong routine answer (one that passed the CLI checks but was wrong) as a wrong answer even if the later focus check caught it.
- Success bar: lower wall than the Luna-only arm with no rise in wrong answers or misclicks.

## 9. Bai hoc

(Danh cho Pham Tuan, viet bang tieng Viet don gian.)

- Model nho chi thang khi no lam viec hep ma no lam dung. Bai hoc: model 3B doc dung nhung ket luan sai, nen khong the tin phan ket luan cua no, chi tin phan trich dan cua no.
- Kiem tra bang code bat duoc loi dinh dang, khong bat duoc loi suy luan. Bai hoc: muon bat loi suy luan thi phai de code tu tinh ket qua tu cai model trich ra, dung de model tu ket luan.
- VRAM la gioi han that, khong phai ly thuyet. Bai hoc: model 7B khong chay het tren GPU khi voxtype dang chay, phai chia mot phan sang CPU, cham hon nhung van dung duoc.
