# Pick 1 prototype: code execution as the action (M1)

- Owner: the owner. Repo: phamTuan207/computer-use-wayland, branch speed-swarm.
- Implementer: Luna 6 Max. Date: Wed 2026-11-18, evening.
- Status: IMPLEMENTED, COMMITTED, PUSHED. MEASUREMENT PAUSED MID-RUN by user order 23:50 (the user is cleaning disk space on the laptop; fleet quiet until resume). No before/after numbers exist yet; the partial run is reported plainly below. Do not claim a saving until the measurement finishes.
- No em dash or en dash in this file, per standing rule.

## What was built

A persistent local Python interpreter on the laptop that runs one short program per model call. The model writes the program at runtime, with loops, conditions, and asserts. One program replaces the 4 to 5 think calls of the baseline loop (windows, observe, act, verify observe) with one program-writing think call plus a finish confirmation.

Allowlisted API (the only names a program may call): `windows()`, `observe(window= or screen=, crop=, max_width=)`, `act(actions, observation)`, `read_file(path)`, `assert_state(condition, message)`, `assert_file_contains(path, text)`, `assert_file_exists(path)`. Plus safe builtins (len, str, int, range, min, max, sorted, and similar) and plain Python loops, conditions, and asserts.

Sandbox guard: AST scan before execution rejects imports, dunder access, eval/exec/open/__import__, getattr/setattr, lambdas, async, and any attribute outside a small safe whitelist. Execution runs with restricted builtins, a program size cap (8192 chars), a wall-clock budget (default 30s, max 60s), an API-call budget (32), and a trace step budget (20000 lines). A banned program fails closed with no side effect beyond API calls already made, and the failure is returned as a result envelope so the supervisor can replan from the partial result.

Safety invariants, unchanged:
- Ownership, lease, generation, cancellation, and explicit finish stay exactly as they are. check_cancel runs before every API call and inside the execution trace; a cancelled run raises instead of returning an envelope.
- Verification stays: the final state is verified from an exact source (file bytes via read_file, plus a final observation image inside the same program), never from the program asserting its own success alone.
- Brokered keyboard input stays: typing goes through the existing wtype path in desktop_act. act() calls desktop_act with the same validation as the normal act command, so the pointer miss check (over 3px refuses the click) and the screen-changed refusal still apply. A program may not disable them.
- read_file is restricted to /tmp, regular files only, no symlink escape. No shell commands, no subprocess, no network, no file writes outside the task target path (programs do not write files at all; file changes happen only through brokered act calls).
- State: JSON-serializable user variables persist across code-exec calls in the same session, in a mode 0600 file under STATE named code-exec-<token>.json. Observation bindings are kept there too and expire after 90s, like any observation. act() only accepts an observation dict this interpreter delivered in this session; a forged observation id fails closed.

Isolation: the pick is behind an explicit opt-in flag, default OFF. Enabled only when CU_CODE_EXEC=1. The cu.py seam refuses the code-exec command while the flag is off, returning a disabled envelope with exit 0 so the supervisor falls back to normal act. Measurement enables exactly this flag and no other pick.

## Files changed

- scripts/code_exec.py (new, 460 lines): the interpreter, allowlisted API, AST validator, budgets, per-session state. Docstring states the safety invariants.
- tests/test_code_exec.py (new, 18 tests): flag defaults off/on, import/subprocess/eval/open/dunder/lambda rejected with no side effect, program size cap, wall-clock budget, API-call budget, happy path (windows, observe, act, read_file, asserts, loop), act without observe fails closed, forged observation fails closed, read_file restricted to /tmp and symlink escape rejected, assert failure returns an envelope (not an exception), refusal dict returned not raised, state persists across runs, cancel raises instead of returning an envelope.
- scripts/cu.py (narrow seam): a code-exec subcommand (program from stdin or a mode 600 file, --intent max 200 chars, --target under /tmp, --wall-seconds 1..60), a CodeExecBackend adapter that routes observe/act through the existing brokered primitives with session-policy recording (record_observation, record_refusal, complete_requirement), and env acquisition for code-exec only when the flag is on (so the disabled path works without a GUI environment). Program-level failures return a result envelope with exit 0 so the supervisor can replan; only cancellation or an infrastructure exception stops the session.
- scripts/session_driver.py (1 line): code-exec added to the driver allowlist.
- scripts/session_remote.py (1 line): code-exec added to the broker COMMANDS allowlist. Found live: the relay rejected the first smoke test with unsupported_command because this second allowlist was missed in the first seam commit. A test was added for it.
- tests/test_session_remote.py (new test class, 2 tests): code-exec envelope validates, unknown command still rejected.

## Commits pushed (branch speed-swarm, never main)

- 93798ed pick1: code execution as the action, allowlisted interpreter (M1)
- 8ce88b9 pick1: narrow cu.py seam for code-exec (M1)
- ffa7acc pick1: allow code-exec through the broker envelope (M1)
- Verified with git ls-remote: origin speed-swarm at ffa7acc at push time. Later pulls show other workers landing on top (HEAD 2ef80dd at measurement time, a chromium commit). No commits on the laptop; the VM branch is the source of truth.

## Offline tests

- tests/test_code_exec.py: 18 tests, all pass. tests/test_core.py: 37 tests, all pass.
- Full offline suite (python3 -m unittest discover -s tests -p 'test_*.py'): 1082 tests with my changes vs 1076 on the clean tree, 9 failures and 68 errors in both runs, zero new failures from this pick. The failure-list diff showed only 2 lines from other workers (chromium CLI list, CDP snapshot), none in code_exec. The 7 test_session_driver failures (5 DoctorCliTests plus 2 FullRestoreEnvelope) reproduce on the clean tree without my changes; they are pre-existing on the VM, which lacks native/wtype.
- No new failures. The 5 pre-existing DoctorCliTests failures are unchanged.

## Live smoke test (laptop, before measurement)

- Relay lesson applied: the relay is a long-running systemd service (computer-use-relay.service) that loads session_remote.py once. My first smoke test was rejected with unsupported_command because the running relay still had pre-patch code. The relay was restarted while idle; status then showed started_git_head 2ef80dd, state idle, cancelled false.
- Second smoke test: broker ACCEPTED code-exec (accepted true, driver ran), but the driver reported "code execution is disabled". Root cause: the driver inherits the RELAY's environment, not the caller's shell, so CU_CODE_EXEC=1 in the measurement shell never reaches it. Fix in the measurement plan: baseline arm runs first with the relay env clean (flag off), then a systemd drop-in sets Environment=CU_CODE_EXEC=1 on the relay, daemon-reload plus relay restart, then the pick1 arm runs. The drop-in is removed and the relay restarted again during restore. This env-propagation point applies to the other picks too (Pick 4 reads CU_PICK4_FASTPATH the same way).

## Measurement: PAUSED, no before/after numbers yet

- Method: same 4 held-out tasks as the profile run (P1 C-03 df -h /, P2 E-04 144/150 percent, P3 B-01 mkdir hoc-ky-2 with 3 subdirs, P4 A-01 y-tuong.txt 3 exact lines), baseline arm (flag OFF, normal loop) then pick1 arm (flag ON, one code-exec program per task), same timed.py wrapper, records.jsonl plus decisions.log in a fresh directory /tmp/speed-profile-20261118/pick1/ on the laptop, never overwriting the profile records.
- Baseline anchor from the profile run: clean-task mean wall 36.4s, mean model think 34.2s (94 percent), mean broker service 1.4s (4 percent); think before act mean 14.9s (41 percent). Conservative bound for this pick from the prior art: OpenGCUA code-ALONE ablation, minus 14.8 percent steps, plus 6.1 points (NOT the 53 percent full-config number, which mixes batching and code). CoAct-1: 10.15 vs 15.22 steps. CLI beats GUI (Gu et al.): 10.7 vs 18.6 steps.
- Measurement agent: Codex gpt-6-luna max reasoning, full access, detached on the laptop, brief at /tmp/speed-profile-20261118/pick1/measure-brief.md (also saved on the VM at ~/workspace/pick1-measure-brief.md).
- What actually happened, in order:
  1. First agent launch waited in a broker-wait loop and never started: the brief said to wait for broker state "idle", but after any finished session the state stays "finished" (driver stopped, guardian clean), which is free to start. The agent was killed (stuck, no progress) and the brief was fixed (free to start on "finished" or "idle" with driver stopped and active_sequence null; wait only on "running" or "starting"). Relaunched.
  2. Second agent waited in backoff (broker-wait sleeps) while Pick 2 and Pick 3 workers held the broker, then got the broker and started baseline P1.
  3. Baseline P1 attempt 1 FAILED: start ok, windows ok, observe failed "window no longer exists", retry windows got task_stopped, finish failed driver_command_failed, session died. The speed-profile-term kitty terminal vanished during the roughly 30 minute broker wait. Suspected cause, not proven: another Track 2 worker uses the same kitty title (the profile brief title), so a same-titled terminal or another worker's cleanup may have collided with it. The pick1 arm brief already uses a distinct title (speed-pick1-term); the baseline arm title needs the same treatment on resume.
  4. Baseline P1 retry started, windows ok twice, then the PAUSE order arrived at 23:50. The retry session was finished cleanly by hand (pause-finish record, ok true, driver stopped, guardian clean). P1 never completed, P2 to P4 never started, the pick1 arm never started, floor probes not run.
- Partial records (laptop /tmp/speed-profile-20261118/pick1/records.jsonl, 16 lines): 9 baseline P1 attempt-1 records, 6 retry records, 1 pause-finish. decisions.log 9 DECIDE lines, sleeps.log 20 broker-wait sleeps. No task completed in either arm, so there is no wall time, no think total, and no model-call count to report yet.

## Pause state (23:50 user order, verified 23:51 to 23:52 +07)

- Measurement agent killed (codex exec pid 613054 and wrapper 613053, confirmed gone). Live broker session speed-base-p1 finished cleanly by hand (ok true, driver stopped, guardian clean). Broker state finished, owner speed-base-p1, driver stopped, cancelled false. No codex exec process remains.
- Desktop verified clean with hyprctl clients: only Jarvis (herdrdrop), the user's foot terminal, the user's ncdu kitty (the user's disk cleanup, untouched), and Zen. No test windows, no VS Code, no speed-profile-term, no speed-pick1-term. Zen tabs, Zalo, Teams, Jarvis, and music were not touched.
- Laptop repo left on branch speed-swarm at 2ef80dd for resume (NOT restored yet, so the measurement setup survives). The user's rust-rewrite-eval work is stashed (stash named "pick1-measure: save rust-rewrite-eval worktree before speed-swarm checkout": M scripts/cu.py, M skill/cli-anything/registry.json) and 5 untracked files are backed up at /tmp/pick1-untracked-backup/ (improvements/speed-prior-art.md, improvements/speed-swarm-prototype-plan.md, scripts/vscode_cli.py, skill/cli-anything/vscode.md, tests/test_vscode_cli.py). The relay is running speed-swarm code (head 2ef80dd) with NO drop-in yet (the flag switch was never reached). Run dir /tmp/speed-profile-20261118/pick1/ holds records.jsonl, decisions.log, sleeps.log, codex2.log, measure-brief.md, timed.py, analyze.py.

## Resume checklist (for the parent agent, when the resume order comes)

1. Relaunch the measurement agent with the fixed brief (already on the laptop at /tmp/speed-profile-20261118/pick1/measure-brief.md). It contains the corrected start condition, the relay flag switch, the pick1 program template, and the full restore section.
2. Redo baseline P1 from scratch (it never completed). Consider renaming the baseline kitty title to a Pick 1 unique title (for example speed-p1base-term) to avoid the title collision that likely killed the first P1 observe; the pick1 arm already uses speed-pick1-term.
3. After measurement, the brief's restore section must run: remove the relay drop-in, close test windows, verify the desktop clean with hyprctl clients, check out rust-rewrite-eval, pop the stash, move the 5 untracked files back, restart the relay, verify it serves the rust-rewrite-eval head and is idle.
4. Then write the before/after table here: per task per arm, wall time, think total, think-before-act (baseline) and think-before-code-exec (pick1), think-before-first-observe, think-before-verify, broker service total, request and image counts, refusals, misclicks, session deaths, program retries, model calls per task. Success is fewer model calls AND lower wall time with no rise in refusals, misclicks, or session deaths. If wall time does not fall even though model calls fall, report that plainly.
