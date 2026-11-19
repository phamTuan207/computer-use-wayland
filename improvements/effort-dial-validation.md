# Effort-dial validation: resume-per-turn does NOT dial (M1 verdict)

- Owner: Pham Tuan. Date: 2026-11-19, 20:00-20:20 Asia/Ho_Chi_Minh.
- Worker: Luna 6 Max (effort-dial continuation). Report to the resume
  coordinator round 2, not to the user.
- Status: VERDICT, measured. The prototype harness is built and unit
  tested, but the dial mechanism it drives was FALSIFIED. Do NOT run
  the P1-P4 A/B until a working per-step mechanism is proven; the A/B
  would measure a no-op. The A/B script refuses the dial arm unless
  EFFORTDIAL_FORCE_DIAL=1 is set.
- Codex CLI: 0.169.0. Model: gpt-6-luna. No broker, no desktop in any
  validation call (read-only sandbox, pure Q and A).

## VERDICT: DIAL NOT WORKING

Per-turn `-c model_reasoning_effort=...` on `codex exec resume` (and
on `codex exec fork`) is accepted without error but does NOT move
reasoning tokens. The outcome tracks the session's bootstrap effort,
not the resume/fork flag. The only proven effort control is the fresh
`codex exec` invocation, and fresh-exec per step is the Pick 2 shape,
already proven bad (~22s wall, ~18k input tokens, 0 cached per call).
M1 as a resume-per-turn dial is dead on this CLI version.

## Evidence

Reasoning-forcing prompts (scheduling, novel numbers, exact answers):
F1 expected 40, F2 expected 24, F3 expected 30. All replies correct
in every call below.

### Fresh exec: the flag DOES work per invocation (controlled, same prompt)

| call | wall | reasoning | input | cached |
| --- | --- | --- | --- | --- |
| fresh low, F1 (run 1) | 6.7s | 0 | 18,096 | 0 |
| fresh max, F1 (run 1) | 13.7s | 285 | 18,188 | 0 |
| fresh low, F1 (run 2) | 6.4s | 0 | 18,155 | 0 |
| fresh max, F1 (run 2) | 17.3s | 430 | 18,188 | 17,152 |

Low is stably 0 reasoning tokens; max is 285-430. Wall roughly doubles
at max on a forcing prompt. Both correct. The effort saving is real IF
a per-step mechanism existed. The gate probe's trivial prompts (0 vs 8
reasoning) could not show this; the forcing prompt does.

### Resume: the flag does NOT move reasoning (same prompt F2 compared)

| call | wall | reasoning | input | cached |
| --- | --- | --- | --- | --- |
| resume max, F2, on LOW session | 10.9s | 221 | 42,361 | 0 |
| resume low, F3, on LOW session | 6.4s | 221 | 66,971 | 17,920 |
| resume low, F2, on MAX session (mirror) | 8.4s | 430 | 37,314 | 34,304 |

Same prompt F2: resume-max on the low session gives 221, resume-low
on the max session gives 430. The flag value and the outcome are
uncorrelated; the outcome tracks the bootstrap session (low session
221, max session 430). Exact-equality pairs (221/221, 430/430) further
suggest resumed-turn usage does not reflect per-turn effort at all.

### Fork: the flag does NOT dial down, and fork is expensive

| call | wall | reasoning | input | cached |
| --- | --- | --- | --- | --- |
| fork max, F2, on LOW session | 9.2s | 345 | 91,756 | 28,672 |
| fork low, F2, on MAX session | 12.2s | 430 | 56,613 | 45,056 |

Fork-low on the max session stays at 430: no dial down. Fork-max on
the low session gives 345, between the resume-max 221 and the fresh
max 430, which is run-to-run variance (F2 reasoning spans 221-430
across runs regardless of flags), not control. Fork also replays
history at full cost: 91,756 input tokens vs 42,361 for the same
resume turn. Even if fork dialed, it would cost ~2x input per turn.

### CLI facts found while building

- `codex exec resume` rejects `-s` and `-C` (rc=2, "unexpected
  argument '-s' found"). Sandbox and workdir are session-level, fixed
  by the bootstrap exec. The driver and the A/B script were fixed for
  this; the new unit tests assert `-s`/`-C` are absent from resume
  argv so the regression cannot come back.
- `codex exec resume` and `codex exec fork` both accept `-c`, `-m`,
  `--json`, `-o`, `--output-schema`, `--skip-git-repo-check`.
- `thread.started` carries the session id; `turn.completed` carries
  usage (input, cached, reasoning, output tokens). Resume preserves
  session context with prompt caching (input grows 18k to 67k across
  turns, cache hits present).

## What was built (harness, tested, ready IF a mechanism appears)

- `scripts/effort_dial_driver.py`: resume-per-turn driver. Bootstrap
  at max, one step per resumed turn, effort from supervisor level
  (subgoal_policy), strict L2 JSON validation, deterministic
  postcondition checks (broker record, file bytes, reply text, local
  command), exactly one escalation to max per failed step, per-turn
  JSONL log plus summary.md. Never executes task actions itself.
- `scripts/effort_dial_brief.md`: dial-arm session brief, turn
  protocol (one step per turn, end with the L2 JSON block), P1-P4.
- `improvements/effort-dial-plan-p1p4.json`: 24 steps, 6 per task
  (start, windows, observe, act at max, verify at low, finish).
- `scripts/run-effortdial-ab.sh`: baseline (single exec, max) vs dial
  arm, with broker-idle and /tmp-dirt gates. Refuses the dial arm
  while this verdict stands.
- `tests/test_effort_dial_driver.py`: 32 tests, all passing (fake
  runner: parsing, arg shapes, level routing, every postcondition
  type, escalation on bad JSON and on failed postcondition, L1 no-call,
  end-state skip, plan stop on failure, summary totals).
- Raw evidence: `improvements/effortdial-validation/summary.json`
  (resume validation) and `improvements/effortdial-validation/fork-summary.json`.

## Suite numbers (worktree, HEAD 8727135 + this branch)

- Worktree gap (found by the A4 worker, fixed here): a fresh worktree
  lacks the gitignored native binaries and generated protocol files,
  so the suite errored 66 tests and hid 23 more. Copied 18 files from
  the main checkout (`native/wtype`, `native/pointer`, `native/modifiers`,
  `native/indicator`, `native/cursor-guard.so`, `*-protocol.c/.h`,
  `native/*.json`, `native/visuals-login.lua`, `native/require-liquid`,
  `native/keyboard-protocol.o`) into the worktree. They stay gitignored
  (`!!` in git status) and are never committed.
- True baseline (artifacts in, before this branch's test fixes):
  1371 tests, 10 failures + 1 error (the 4 were this branch's own
  new tests, since fixed).
- Branch run (artifacts in, tests fixed): 1371 tests, 7 failures,
  0 errors, 2 skipped. Zero new failures vs the true baseline. The 7
  are pre-existing (5 test_session_driver DoctorCliTests around
  fcitx5-remote, 1 test_chromium_cli, 1 test_session_policy), identical
  in both baseline runs, untouched by this change.

## A/B: NOT RUN

Broker state at check time (19/11 evening): R3-baseline broker session
finished, driver stopped, guardian clean, no active sequence. But the
A/B was not attempted: with the dial falsified, the dial arm would run
every turn at the bootstrap effort, so the comparison would measure
turn-chunking overhead, not an effort saving. Do not run it until a
per-step mechanism is proven.

## Options forward (for the coordinator, not decided here)

1. KILL M1 as a live lever (recommended): the mechanism does not exist
   on Codex 0.169.0. Keep the harness in the branch for a future CLI
   version that honors per-turn effort; re-probe on upgrade.
2. Two-session dial (low session + max session, driver relays compact
   text state between them): unproven, needs its own probe; split
   context plus relay cost likely erases the saving. Probe before
   building.
3. Reallocate the M1 budget to M2 (DOM/text observation, already
   measured) or M3/M4 probes.

## Bai hoc

- Tam ly hoc cua viec do: mot co che chi ton tai khi no doi so lieu
  theo y muon. Resume chap nhan co -c ma khong bao loi, trong rat giong
  la no hoat dong, nhung so reasoning noi nguoc lai. Bai hoc: dung tin
  co hieu "chap nhan", chi tin so lieu doi chieu co kiem soat.
- Prompt tam thuong khong chung minh duoc gi: prompt 1 tu cho 0
  reasoning o ca low lan max. Bai hoc: muon chung minh mot cai nut co
  tac dung, phai dung prompt buoc model suy nghi that, va doi chieu
  cung mot prompt.
- Kiem tra guong la bat buoc: chi khi resume session max o muc low ma
  van ra 430 token thi moi chac chan nut resume khong co tac dung. Bai
  hoc: mot chieu chua du, phai thu chieu nguoc lai.
