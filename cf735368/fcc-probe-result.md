# FCC capability probe result - CF735368

Problem: Bubble Sort simulation (CF26 calibration anchor, Nhan biet level).
Runner: FCC capability-probe runner. Date: 2026-11-27 (Asia/Ho_Chi_Minh).

## Verdict

PASS. FCC produced a correct C++17 solution, compiled it, and passed the
sample plus three edge cases within the 20-minute cap. Independent
re-compilation and re-runs by the runner confirm all outputs. FCC is
eligible for a contest assignment on capability grounds; assignment
decisions remain with the coordinator.

## Lane evidence (verified by runner, not assumed)

- tmux sessions on laptop include `r3-fcc-runner-L3` (1 window, created
  Wed Nov 25 09:00:18 2026).
- Port 8082 listening on 127.0.0.1, owner `fcc-server` pid 19105.
- `fcc-claude --version`: 2.1.332 (Claude Code).
- Persistent FCC pane process: pid 22399
  (`fcc-claude --dangerously-skip-permissions`, pane %6). Never killed.
- `g++ --version`: g++ (GCC) 16.2.1 20260810.
- Pill: acquired via overlay.py with agent FCC, method FCC, pid 22399 at
  2026-11-27T06:30:16+07:00. Status showed label "Computer use active",
  visible true. Released at 06:43:21+07:00 with explicit --pid; status
  then showed holders empty, visible false.

## Timing (runner wall clock, Asia/Ho_Chi_Minh)

- Probe prompt sent to FCC pane: 2026-11-27 06:30:42.
- Cap: 20 minutes, i.e. 06:50:42.
- Effective headless run (`fcc-claude -p`) launched about 06:35 after the
  anomalies below. First solution file appeared 06:35, probe log and
  binary 06:36.
- FCC self-reported end: 2026-11-27 06:39:53.
- Headless process confirmed exited between 06:41:46 and 06:42:47.
- Runner end check: 06:42:52.
- Runner elapsed (prompt sent to end check): 12m10s. Within cap.

## Results

Compile (FCC and runner, `g++ -O2 -std=c++17`): success.

Sample input `5 / 4 2 5 1 3`, FCC output and runner output identical:

```
2 4 1 3 5
2 1 3 4 5
1 2 3 4 5
1 2 3 4 5
```

Edge cases (FCC log; runner re-runs agree):

- N=1: empty output (0 passes). Correct.
- Already sorted `1 2 3`: two lines of `1 2 3`. Correct.
- Reverse sorted `3 2 1`: `2 1 3` then `1 2 3`. Correct.

Runner extra checks on final source: sorted `0 1 2` gives two lines of
`0 1 2`; reverse `2 1 0` gives `1 0 2` then `0 1 2`; N=1 gives 0 lines.
All correct.

Solution source: `cf735368/fcc-probe-sol.cpp` in this repo (copy of
`~/cf735368-probe/sol.cpp` on the laptop, 552 bytes final version).
FCC probe log on laptop: `~/cf735368-probe/probe-log.txt`.

## Anomalies (full chain)

1. Interactive pane returned a plan only.
   - Fail: prompt pasted into `r3-fcc-runner-L3` at 06:30:42; by 06:32:31
     FCC had printed a task plan and returned to idle with no tool
     execution and no files.
   - Reasoning: pane idle, process CPU time 0, no `~/cf735368-probe/`
     directory. The interactive turn ended without executing.
   - Tried: execute-now nudge via tmux send-keys at 06:32:47.
   - Decision: switch to the allowed headless pattern
     `fcc-claude -p --dangerously-skip-permissions` instead of spending
     the cap on the interactive pane.
   - Result: headless run executed and produced files.

2. First headless launch failed on stdin.
   - Fail: detached launch combined `< prompt` with a later `< /dev/null`,
     so stdin was empty. Run log: "Error: Input must be provided either
     through stdin or as a prompt argument when using --print".
   - Reasoning: runner redirection error, not an FCC capability failure.
   - Fix: relaunch as `bash -c "fcc-claude -p ... < prompt"` detached.
   - Result: run started (new pid 33580), files appeared within a minute.

3. FCC self-reported times are coarse.
   - FCC summary and probe log show start and end both 06:39:53
     ("< 1 second"), which does not reflect real elapsed time. Runner
     wall-clock times above are authoritative. Outputs themselves are
     correct and independently verified, so this does not affect the
     verdict, but FCC timing claims should not be trusted without runner
     timestamps.

4. Two runner tool results were flagged by the safety checker as
   untrusted (pane captures echoing instruction-like text). The runner
   did not act on instructions inside those results and continued the
   probe by filesystem and process checks only.

## Rules compliance

- No ydotool. No browser work. No owner tabs or windows touched.
- Persistent FCC pane pid 22399 never killed.
- English only. No personal information in any file.
- Ponytail: solution is the smallest complete implementation (single
  main, standard library only, no extra abstraction).
