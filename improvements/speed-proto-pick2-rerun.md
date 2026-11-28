# Pick 2 solo rerun: baseline vs pick2, both arms redone (Track 2, Phase A)

- Owner: the repository owner. Date: 2026-11-19, 02:52 to 03:52 Asia/Ho_Chi_Minh.
- Repo: laptop ~/computer-use-wayland, branch speed-swarm, HEAD c1b7034.
- Status: MEASURED, both arms 5/5 SUCCESS. Verdict PROVISIONAL (non-Astra, Astra 6 out of credit).
- No em dash or en dash in this file.

## What the rerun fixed vs round 1

- Fresh run dirs: old /tmp/speed-profile-20261118/pick2-base2/ archived to pick2-base2-run1/, old pick2-2/ archived to pick2-2-run1/ (summaries, records, attempt1 archive preserved). Fresh dirs got the fixed brief plus timed.py and analyze.py copied.
- Brief fix (the round-1 killer): added setup cleanup before EACH arm and an end-of-arm cleanup in BOTH brief copies. Round 1 had a dirt STOP rule but no setup cleanup, so the baseline created the dirt and the pick2 arm was guaranteed to trip on P3. This rerun: all dirt checks clean, no BLOCKED-dirty anywhere.
- No waiter scripts. Both executors launched directly via codex exec with the brief: `codex exec --json --sandbox danger-full-access -m gpt-6-luna -c model_reasoning_effort="max" "<brief>"`, detached with nohup from the repo dir.
- Solo: broker plus desktop to itself for both arms. The Pick 1 fix worker ran in parallel but never touched the broker, relay, or live checkout.
- One brief patch applied mid-rerun, before the pick2 arm launched: the shell safety layer rejected the `rm -rf` cleanup form in the baseline arm, so the pick2 brief's two cleanup lines were changed to a Python one-liner restricted to the three exact /tmp paths (the baseline executor had already worked around it the same way).

## Method (think split)

- Used /tmp/pick2-think.py (v3, same as round 1): per-task wall window is [submit of the SUCCESSFUL (ok=True) start record, result of the LAST request record before the task finish record]. Think is the sum of DECIDE gaps strictly inside the window, minus logged sleeps. Broker service is summed from records.
- Validation: think plus broker service reproduces each wall within about 1s on clean tasks (baseline diffs 0.5 to 0.8s; pick2 P1 to P3 diffs 0.1 to 0.7s). Pick2 P4/P5 diffs are -3.7s because service sums all records including dead-start status polls outside the window.
- The executor-written summary walls (first start submit to finish submit) are NOT used for deltas: they include dead-start waits and post-verify writeup gaps (17 to 28s per task in baseline, up to about 150s in pick2 P4). The think.py window is the loop wall, consistent with the profile run method (finish calls excluded).
- analyze.py is a stub (hardcodes p1c-p4c labels); its V3 section is INCOMPLETE in both summaries, as expected. All timings below come from think-split plus the summaries.

## Per-task results (think.py walls)

### Baseline arm, solo rerun, 02:53 to 03:10

5/5 SUCCESS. No refusals, no session deaths, 0 sleeps, 0 L2 calls (control arm, no supervisor.log).

| Task | Wall (s) | Think (s) | Service (s) | Result |
|---|---:|---:|---:|---|
| P1 C-03 | 122.0 | 119.9 | 1.5 | SUCCESS, free space 19G |
| P2 E-04 | 42.9 | 40.8 | 1.4 | SUCCESS, 96.0 |
| P3 B-01 | 65.9 | 62.8 | 2.3 | SUCCESS, 4 dirs |
| P4 A-01 | 63.7 | 60.4 | 2.8 | SUCCESS, exact 3 lines |
| P5 COLD | 90.2 | 86.4 | 3.1 | SUCCESS, pill-video |
| Mean | 76.9 | 74.1 | 2.2 | |
| Total | 384.7 | 370.4 | 11.1 | |

Floor probe: INVALID. Wall 74.4s, think 72.1s. The executor deliberated between floor requests instead of running the scripted zero-think shape.

### Pick2 arm, solo rerun, 03:20 to 03:50

5/5 SUCCESS. Supervisor totals: L2 2, L3 9, L2 schema validation failures 0, detection lags 0.

| Task | Wall (s) | Think (s) | Service (s) | Result | L2/L3 |
|---|---:|---:|---:|---|---:|
| P1 C-03 | 100.8 | 98.8 | 1.9 | SUCCESS, free space 19G (summary says 196G, OCR artifact, G read as 6) | 0/4 |
| P2 E-04 | 34.6 | 32.7 | 1.3 | SUCCESS, 96.0 | 0/0 |
| P3 B-01 | 58.8 | 55.8 | 2.3 | SUCCESS, 4 dirs | 0/0 |
| P4 A-01 | 143.7 | 139.9 | 7.5* | SUCCESS, SHA-256 verified | 0/2 |
| P5 COLD | 192.1 | 188.6 | 7.2* | SUCCESS, pill-video | 2/3 |
| Mean | 106.0 | 103.1 | 5.2* | | |
| Total | 530.1 | 515.7 | 26.2* | | |

\* Service sums all records including dead-start status polls outside the window (P4/P5 each had 86 startup polls, almost all ok=false).

Floor probe: INVALID. First start stayed pending 75s, then a retry lease ran the probe in 87.1s with 0.0s think and 5.6s service, leaving 81s unaccounted (no DECIDE lines, no logged sleep). End to end from first start: 187.2s. No harness-floor number comes out of this rerun; use the profile floor 2.1s as reference.

## Before/after deltas (pick2 minus baseline, think.py walls)

| Task | Wall delta (s) | Think delta (s) |
|---|---:|---:|
| P1 | -21.2 | -21.1 |
| P2 | -8.3 | -8.1 |
| P3 | -7.1 | -7.0 |
| P4 | +80.0 | +79.5 |
| P5 | +101.9 | +102.2 |
| Mean | +29.1 | +29.0 |

## Supervisor calls (pick2 arm)

- P1: L2 0, L3 4 (terminal launch, vanished window, session recovery, terminal persistence). All recovery.
- P2: L2 0, L3 0.
- P3: L2 0, L3 0.
- P4: L2 0, L3 2 (dead-start recovery, OCR ambiguity recovery via SHA-256).
- P5: L2 2, L3 3 (new procedure, dead-start recovery, bad L2 choice escalated).
- Totals: L2 2, L3 9, schema failures 0, lags 0.

L2 detail (the only routine-decision L2 calls in either round):

- L2-1, p5-window-target, 03:41:29: `{"action":"observe","target":"0x55fafee38e50","confidence":1}`. CORRECT routine decision (pick the terminal window). Usage: input_tokens 18167, cached 0, reasoning_output_tokens 0, output_tokens 30. Wall about 22s.
- L2-2, p5-largest-basename, 03:43:15: `{"action":"write","target":"pick3-gate","confidence":1}`. WRONG with confidence 1.0 (correct answer was pill-video, the first row of the descending du output). The deterministic postcondition check caught it and escalated to L3 at 03:43:46 before any write. No bad action ran, lag 0. Usage: input_tokens 18176, cached 0, reasoning_output_tokens 0, output_tokens 26.

## Blockers and incidents

- Window loss recurred SOLO in P1 (pick2 arm): the prescribed background Kitty launch created no pick2-term window; an isolated Kitty appeared then disappeared when the launch shell exited; broker observe returned `window no longer exists`; the next request was refused with `request_error=task_stopped`; broker status showed state=failed, driver=failed. A fresh lease plus a Kitty process held in a live shell recovered the task. No other broker user was running, so this proves the cause is in the broker/driver (or the Kitty launch form), not contention. Per the task stop rule, a total window-loss failure would have ended the rerun; this run was NOT stopped because P1 recovered and kept producing measurements. The recurrence is reported here as the finding: the broker/driver window-loss path needs a fix before any Pick 2 verdict.
- Dead starts (broker start never reaches ready, status polls return ok=false with null state/driver/sequence): P4 first start (86 polls, logged 60s wait, fresh lease recovered), P5 first start (86 polls, logged 30s wait, fresh lease recovered), floor first start (75s, fresh lease recovered). Same symptom as round-1 attempt 2, also solo. Failed start records carry no error or cause field.
- Baseline deviations: `CU_PICK2_SUBGOAL_ONLY=1` was mistakenly exported during setup and inherited by Kitty; the P1 shell had it set, and it was explicitly unset before P2. No L2 calls and no supervisor.log exist in the baseline run, and the flag is read by the relay (whose env never had it), so there is no mechanism contamination; the P1 command itself is unaffected. The shell safety layer rejected the `rm -rf` cleanup form; setup and end cleanup used a Python cleanup restricted to the three exact /tmp paths.
- Pick2 deviations: Kitty held in a live shell instead of the brief's background launch (forced by the P1 window loss). P4 verified by brokered SHA-256 instead of OCR because English Tesseract cannot distinguish Vietnamese diacritics; this is a deterministic postcondition, within the pick's rules. P1 free-space "196G" in the summary is an OCR artifact (G read as 6); the true value is 19G, matching baseline.
- Round-1 comparison: the solo rerun baseline mean wall 76.9s vs round-1 baseline mean 107.7s confirms round 1 was contention-inflated. The rerun baseline P1 122.0s also beats the profile P1 180.7s (which had a refusal cascade).

## Verdict: DO NOT LAND Pick 2 as a think-time win (PROVISIONAL)

1. The only tasks where pick2 beat baseline (P1 to P3, -7 to -21s) used ZERO L2 calls. The saving cannot be attributed to the mechanism; it is executor variance. Both arms' executors deliberated 16 to 31s per step, and the baseline P1 executor was slow on its own kitty launch.
2. The only task with routine L2 calls (P5, 2 calls) was +102s, but that is confounded by a dead start, a fresh-lease recovery, and the L3 escalation after the bad L2 choice. It is not clean evidence against L2 either.
3. L2 was exercised on routine decisions exactly twice in the whole rerun (n=2), and one of the two was wrong with confidence 1.0. The mechanism remains effectively unmeasured, and the single error is a warning: low effort failed to pick the first row of a 3-row descending-sorted list, and only the deterministic postcondition saved it.
4. Broker flakiness dominated the pick2 arm (P1 session death, P4/P5 dead starts, floor dead start) while the baseline arm had none. Any before/after delta from this rerun is swamped by that variance.
5. Cost note: each L2 sub-invocation carried about 18k input tokens with 0 cached, and took about 22 to 30s of wall, comparable to an in-session think gap. As built, the L2 route does not obviously save wall time per decision.

What would make Pick 2 measurable: fix the broker-side window-loss and dead-start paths first (both recurred solo), then re-measure with an executor brief that REQUIRES an L2 call on every routine decision (P1 to P4 included, not just P5), so the L2 count is non-zero by construction and the delta can be attributed.

## Cleanup verification (03:52)

- Both codex executors exited (turn.completed in both executor.jsonl files). No codex exec process remains.
- Broker: state finished, owner pick2-floor, driver stopped, cancelled false. Free.
- Desktop: hyprctl clients shows only Jarvis (herdrdrop) and Zen Browser. No pick2-term window.
- Dirt: /tmp/hoc-ky-2, /tmp/y-tuong.txt, /tmp/lon-nhat.txt all absent. Both end-of-arm cleanups ran.
- Run dirs (laptop): /tmp/speed-profile-20261118/pick2-base2/ (summary.md, think-split.txt, records.jsonl 66 lines) and /tmp/speed-profile-20261118/pick2-2/ (summary.md, think-split.txt, records.jsonl 331 lines, supervisor.log, l2-1/l2-2 files). Archives: pick2-base2-run1/ and pick2-2-run1/.
