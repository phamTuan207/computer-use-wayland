# Track 2 rerun plan: Pick 1 fix + rerun, Pick 2 solo rerun, Masking measurement

- Date: 2026-11-19 (after Pick 4 arm2 finished 02:35 +07)
- Owner: the repository owner. Status: PROVISIONAL (non-Astra, Astra 6 out of credit).
- Precondition met: Pick 4 arm2 finished, broker free (state finished, driver stopped, cancelled false). No executor running.

## First-round results (why a rerun is needed)

- Pick 1: baseline 4/4 SUCCESS (clean mean P2-P4 wall 46.1s, think 43.8s). Pick1 arm 0/4 BLOCKED. Every program did windows() + observe() then died in the sandbox with `trace step budget exceeded (20000)` before act(). P4 blocked before any session (11 refused broker starts). No valid wall-time delta. Smoke test succeeded (flag live), so the failure is the sandbox budget, not the flag.
- Pick 2: baseline 5/5 SUCCESS (mean wall 107.7s, think 104.9s, inflated by broker contention and a 113.7s P1 recheck gap). Pick2 arm has NO valid measurement. Attempt 1 gave 2 valid tasks (P1, P2) then stopped on dirt at P3. Attempt 2 lost all 5 tasks to the terminal window dying under the broker (0 acts, 0 end states). Only comparable task is P2 (n=1, 6.4s think saved, 0 L2 calls), which is variance, not evidence. The L2 mechanism was never exercised on a routine in-task decision.
- Pick 4: DONE, no rerun needed. Final combined summary filed 02:40 19/11 (speed-proto-pick4-summary.md on VM). Arm1 run2 (baseline) 4/4 SUCCESS: P1 281.5s, P2 43.6s, P3 43.9s, P4 312.5s, mean 170.4s, clean P2/P3 mean 43.7s. Arm2 (fastpath) 4/4 SUCCESS: P1 114.2s, P2 42.3s, P3 41.2s, P4 121.9s, mean 79.9s, clean P2/P3 mean 41.7s. Honest read: think-time saved is about 2s on the clean pair (-5%); the raw -90.5s mean delta is executor variance (arm1 P1 stale retry, arm1 P4 extra verification rounds), not Pick 4. D1 SUCCESS via DOM-first (0 browser screenshots, assert passes, core DOM loop think about 21s) but no arm1 baseline, so feasibility only, not a speedup claim. G1 BLOCKED (broker rejects a11y with `unsupported_command`, 3 attempts; direct ground also broken, coord-frame bug). Verdict: CONDITIONAL (PROVISIONAL). Do not land Pick 4 as a think-time win. DOM-first browser half works but needs a baseline browser task before any speedup claim; a11y half is blocked at two layers and cannot land until both are fixed. G1 needs a separate a11y-wiring fix; it is not part of this rerun plan.
- Masking prototype (Pick 5 prep): built, 31/31 tests pass, pushed to origin speed-swarm-masking (bfdbfb0), brief ready at improvements/mask-executor-brief.md in the worktree. Not yet measured.

## Sequencing (solo, one broker user at a time)

The broker is single-owner. All reruns and measurements run SOLO (no concurrent workers). The parallel design of the first round caused broker contention that inflated baselines and blocked starts; the reruns correct that by running one at a time.

- Phase A (parallel, starts when the broker is free): Pick 2 rerun worker (broker, solo) AND Pick 1 fix worker (code, separate worktree, no broker, no relay restart). These do not interfere: the fix worker never touches the live checkout, the relay, or the broker.
- Phase B (sequential, after Phase A): coordinator merges the Pick 1 fix into speed-swarm, restarts the relay, verifies it serves the fixed code. Then Pick 1 rerun worker (broker, solo).
- Phase C (sequential, after Phase B): Masking measurement worker (broker, solo).
- Phase D (sequential, after Phase C): final report (fill the three tables + landing recommendation) + Track 1 restore.

Track 1 restore is DELAYED until Phase D. The repo stays on speed-swarm until all reruns and measurements are done. The restore (checkout rust-rewrite-eval, stash pop, untracked files back, relay restart) happens once, at the end.

Time estimate (not a commitment): Phase A about 1-2 hours, Phase B about 1 hour, Phase C about 1 hour. Total about 3-4 hours for all three, then the final report + restore.

## Pick 1 fix (code, no broker)

Root cause (confirmed): scripts/code_exec.py MAX_TRACE_STEPS = 20000 (line 77). The trace counts every Python line executed, including inside the observe() and act() API implementations, so one observe() burns thousands of steps. The docstring (line 50) says the budget is "20000 executed lines". The error is raised at line 323. The Codex sandbox is NOT the issue (Codex is already danger-full-access, verified in ps). Do NOT change the Codex sandbox.

Fix direction (the owner, 19/11): stop counting API-implementation lines. Two implementation options; the fix worker picks the cleaner one given the code:
- (a) Clear or reset the trace counter around API calls in _api (in CodeExecSession, when an API function is invoked, save and reset the step counter, then restore it after, so only the program's own lines count).
- (b) Filter the trace to the program's own file (in the trace function, only increment the counter when the executing frame's filename is the program file; skip frames in the API implementation and stdlib).
- Fallback only if (a) and (b) are not feasible: raise MAX_TRACE_STEPS substantially (for example to 200000), since the wall-clock limit (60s) and the API-call limit (32) already bound runaway execution. The fix worker must measure per-call step counts first to pick a principled value, not guess.

Work location: SEPARATE worktree (for example ~/computer-use-wayland-pick1fix, branch speed-swarm-pick1fix, from origin/speed-swarm). Do NOT touch the live checkout (~/computer-use-wayland). Do NOT restart the relay. Do NOT start a broker session. Verify with pwd and git rev-parse --show-toplevel before every edit.

Steps for the fix worker:
1. Read code_exec.py (CodeExecSession line 225, run_program line 509, the trace hook, MAX_TRACE_STEPS line 77) and the _api module to understand how the trace is counted.
2. Instrument and measure per-call step counts: run windows() alone, observe() alone, act() alone, read_file() alone, and log the step count each consumes. Report these numbers.
3. Implement the fix, option (a) or (b). Fallback (c) only if (a) and (b) are not feasible, with the measured per-call counts justifying the new value.
4. Unit tests: a full program (windows + observe + act + observe) completes without hitting the budget; the budget still catches a genuinely runaway program (for example an infinite loop, which the wall-clock limit should also catch, but verify the trace budget still functions). Tests must pass.
5. Dry-run without the broker: test the fixed code_exec.py in isolation (direct Python invocation of run_program with a mock backend, or a unit test that calls the API functions). Do NOT start a broker session (the Pick 2 rerun is using it). The live broker test happens in the Pick 1 rerun, which includes the smoke test.
6. Commit to speed-swarm-pick1fix in small atomic commits and push to origin. Report the per-call step counts, the fix chosen, test results, and the branch.
7. If the fix does not let a full program complete, report that plainly and do NOT proceed to a rerun. A rerun on an unproven fix wastes a broker slot.

Merge (coordinator, after Phase A): fast-forward or merge speed-swarm-pick1fix into speed-swarm, verify the diff is only the fix, restart the relay, verify it serves the fixed code (head + a smoke check in the Pick 1 rerun).

## Pick 1 rerun (broker, solo, after the fix is merged + relay restarted)

- Solo (broker + desktop to itself, no other workers).
- Fresh run dir: archive the old /tmp/speed-profile-20261118/pick1/ to /tmp/speed-profile-20261118/pick1-run1/ (preserve records.jsonl 1025 lines + summary-pick1.md), then use a fresh pick1/ dir with timed.py and analyze.py copied from the archive.
- Follow the ORIGINAL pick1 brief (measure-brief.md) EXCEPT ignore the two COORDINATOR OVERRIDE lines (they were for the parallel run). Do the flag-switch as written, adapted for the shared drop-in:
  - Baseline (flag OFF): FIRST remove the shared drop-in ~/.config/systemd/user/computer-use-relay.service.d/speed-swarm.conf, run systemctl --user daemon-reload, restart the relay, verify active + idle + started_git_head, and verify the disabled envelope (CU_CODE_EXEC=0 code-exec must print disabled). This gives a clean flag-OFF baseline (the first round's baseline ran with the shared drop-in on, which was contaminated in the strict sense).
  - Pick1 arm (flag ON): create pick1.conf with Environment=CU_CODE_EXEC=1, daemon-reload, restart relay, verify, run the smoke test (must be ok:true). Then run the pick1 arm.
  - After the pick1 arm: remove pick1.conf, daemon-reload, restart the relay to a clean env, verify active + idle.
- Do restore steps 1-3 only (finish sessions, remove the drop-in, close test windows, verify desktop clean). Do NOT do the Track 1 restore (steps 4-5); the coordinator does that in Phase D.
- Measure both arms (baseline P1-P4, pick1 P1-P4). Write summary-pick1.md + records.jsonl in the fresh run dir. Report the per-task table, the before/after deltas, whether pick1 beat baseline on wall time with no rise in refusals/misclicks/session deaths, and any blockers with verbatim errors.

## Pick 2 rerun (broker, solo, ready first)

- Fix the brief FIRST (the rerun worker applies this): add the setup cleanup step `rm -rf /tmp/hoc-ky-2 /tmp/y-tuong.txt /tmp/lon-nhat.txt` before EACH arm (baseline and pick2), in both the baseline copy and the pick2 copy of the brief. This is the Pick 1 brief's setup step. Also add a cleanup-rm at the end of each arm so the next arm starts clean. The first round's brief had a dirt STOP rule but no setup cleanup, so the baseline created the dirt and the pick2 arm was guaranteed to trip on P3. That killed attempt 1.
- Do NOT use the waiter scripts. The waiters had a stale-DIR bug (they pointed at /tmp/speed-profile-20261118-pick2-base2 with a hyphen; the worker fixed them, but the rerun worker must not rely on them). Launch the executors directly via codex exec with the brief (the same form Pick 1's worker used), not via the waiter scripts.
- Solo (broker + desktop to itself). Redo BOTH arms (baseline + pick2) for a clean within-run comparison. The existing baseline (mean 107.7s) was measured under contention and with a deliberating executor; comparing a solo pick2 arm against it would be confounded. Redoing both arms costs more time but gives a valid before/after.
- Fresh run dirs: archive the old /tmp/speed-profile-20261118/pick2-base2/ to pick2-base2-run1/ and /tmp/speed-profile-20261118/pick2-2/ to pick2-2-run1/ (preserve summaries, records, and the attempt1 archive), then use fresh dirs with the fixed brief + timed.py and analyze.py copied.
- The pick2 arm must actually exercise L2 on routine in-task decisions. The first round used 0 L2 calls on normal tasks (attempt 1) and 5 L2 calls only for recovery terminal selection (attempt 2). The rerun worker must verify from the summary that L2 was called on routine decisions (not just recovery). If the executor again uses 0 L2 calls, the worker must note it plainly; the mechanism remains unmeasured.
- The bundled analyze.py is a stub (it hardcodes p1c-p4c labels, so its timings are incomplete for pick2 runs). The rerun worker must use a validated think-split method (the first worker's /tmp/pick2-think.py approach: think + broker service reproduces each wall within about 1s) and report the method.
- If the window-loss failure recurs solo (pick2-term dies within 1-2 min of being listed, observe returns window no longer exists), STOP the rerun and report it. That would prove the cause is in the broker/driver, not contention, and it needs a broker-side fix before any Pick 2 verdict.
- Write summaries in the fresh run dirs. Report the per-task table for both arms, the before/after deltas, supervisor calls (L2 count, L3 escalations, validation failures, lags), and any blockers.

## Masking measurement (Pick 5, broker, solo, after the Pick 1 rerun)

- Use the built prototype: worktree ~/computer-use-wayland-masking, branch speed-swarm-masking, flag CU_MASK_HISTORY=1, brief improvements/mask-executor-brief.md in the worktree. Tests 31/31 pass. Push confirmed at bfdbfb0.
- The measurement worker follows the mask-executor-brief.md: baseline arm first (flag unset, kitty mask-base-term), masked arm second (CU_MASK_HISTORY=1 in the executor shell only, kitty mask-pick-term), same 4 held-out tasks P1-P4, same timed.py and analyze.py pattern, before/after think-time table, per-step-index think growth so the history-growth curve is visible.
- Solo (broker + desktop to itself).
- Key constraint: masking is executor-side (a helper module + brief discipline), NOT a harness change. The prompt/history is not built anywhere in the repo (cu.py has zero occurrences of prompt/history; the history lives in the Codex executor's own transcript). So the relay does NOT need to change and no relay restart is needed. The flag lives in the executor's shell only. The executor needs the mask_history.py module from the worktree path.
- The measurement worker must verify from the summary and records that the masked arm actually carried at most 2 images in the prompt (the dry run proved the module works; the live run must confirm the discipline was followed). If the masked arm carried more than 2 images, the worker must note it; the discipline was not followed and the measurement is invalid.
- Fresh run dir (the brief specifies it; the worker follows the brief). No relay restart, no repo restore.

## Workers to spawn (when the parent approves)

1. Pick 2 rerun worker (broker, solo, both arms, fixed brief, fresh dirs, direct codex launch, no waiter scripts).
2. Pick 1 fix worker (code, separate worktree, no broker, no relay restart). Runs in parallel with worker 1.
3. Pick 1 rerun worker (broker, solo, both arms, clean flag switch, fresh dir). Starts after worker 1 finishes AND the fix is merged + relay restarted.
4. Masking measurement worker (broker, solo, follows the mask brief). Starts after worker 3 finishes.

## Risks and caveats

- The Pick 1 fix might not work first try. If the trace counting is deeper than expected, the fix worker reports the per-call step counts and the rerun is blocked. Do not rerun on an unproven fix.
- The Pick 2 window-loss might recur solo. If it does, the cause is the broker/driver, not contention, and it needs a broker-side fix.
- The masking discipline might not be followed by the executor (it is a discipline, not enforced by the harness). The measurement worker must verify the image count in the prompt.
- The parallel design of the first round caused broker contention that inflated baselines (Pick 2 P1 219.2s with 360s of broker-busy waits, Pick 1 P4 11 refused starts, Pick 4 arm1 run1 0/4 blocked). The reruns correct this by running solo. The final report must carry this caveat for the first-round numbers.
- My prep bug (owned): I created the pick2 waiter by sed from a stale base2 waiter without verifying its DIR (it pointed at the hyphenated dir). The Pick 2 worker caught and fixed it. The rerun avoids the waiter scripts entirely.

## Standing rules (restate in every worker brief)

- Codex launch form: codex exec --sandbox danger-full-access -m gpt-6-luna -c model_reasoning_effort="max". codex 0.169.0 does NOT accept --model_reasoning_effort as a flag. Launch from the repo dir (or the worker's own worktree for code work).
- NEVER use ydotool on his machine. Banned.
- Cleanup after EVERY test run: close every test window/app, verify desktop clean via hyprctl clients, never touch his Zen tabs, Zalo, Teams, Jarvis, music. He is at the machine studying; live tests run even while he uses it (authorized), but keep disruption minimal.
- Push to GitHub as work lands, small atomic commits of real work.
- Timing always on: every test timed precisely, logged with wall-clock timestamps (Asia/Ho_Chi_Minh) in improvements/live-test-log.md.
- SSH only via ~/workspace/ssh-laptop.sh. SSH dies about 30s, launch laptop jobs detached (nohup ... > log 2>&1 < /dev/null &) and check with short calls. Never use sudo.
- Kill a stuck subagent immediately without asking, and report it.
- In repo/handoff text refer to him as the owner, never by nickname.
- Astra 6 is OUT of credit (blocked). Use Luna 6 Max (Codex). Mark verdicts as PROVISIONAL (non-Astra).
- A dedicated watchdog is already running (polls every 5 min). Do not spawn another.
- Do NOT message the user directly. Report back to the coordinator.
- The owner's 5 standing orders apply: (1) keep working, do not stop, push through blockers, find workarounds; (2) continue what is unfinished; (3) keep optimizing to reduce think time; (4) cut whatever step can be cut; (5) learn from predecessors' docs and repos (improvements/speed-prior-art.md), do not reinvent. Safety limits hold: never bypass a rate limit or account lock, never break his machine or touch his personal data.
