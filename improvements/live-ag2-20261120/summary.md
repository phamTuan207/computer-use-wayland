# Task 3: action-grouping discriminating test

## Verdict: LOSS on wall (mechanism confirmed working and discriminating)

Strict action grouping makes the discriminating task slower, not faster.
It enforces the split, but every split costs a full think-observe cycle,
and the service time it could save is only seconds. On G1 the method arm
took 555.955s vs the baseline 90.629s (6.1x), with 11 act requests vs 3
and 12 observes vs 1. On G2 the validator never fired (0 rejections) and
both arms hit the same focus-change refusal; the method arm ended BLOCKED
because its executor chose not to recover, while the baseline executor
recovered and succeeded. That G2 difference is executor behavior, not
grouping.

## Setup

- Model for both arms: Codex gpt-6-luna, max reasoning,
  `-m gpt-6-luna -c model_reasoning_effort="max" -s danger-full-access`.
- Baseline branch 8727135, method branch action-grouping ab5011a.
  Suite gates CITED (HEADs match the triple A/B: baseline 8727135,
  action-grouping ab5011a 1348 tests, 7F/0E/2S).
- Relay restarted after each checkout change; started_git_head verified
  before each arm (8727135 for baseline, ab5011a for method). Clean env
  both arms (no CU_CODE_EXEC, no CU_PRECAPTURE; the codeexec.conf
  drop-in was removed before the baseline).
- Run dirs: /tmp/live-ag2-20261120/ag2-baseline/ and ag2-method/.
- Tasks: G1, create /tmp/ghi-chu.txt with 3 ASCII lines via nano
  (type line 1, Return, line 2, Return, line 3, Return, Ctrl+O, Return,
  Ctrl+X), verify by cat. G2, create /tmp/y-tuong-2.txt with exactly
  "Hello grouping." via VS Code File menu then New Text File, type the
  line, Ctrl+S, in the Save dialog type the full path and press Return,
  verify by cat. Executor instruction (both arms): attempt the ENTIRE
  remaining sequence in ONE act request first; the method arm splits on
  a grouping refusal at the named boundary and logs it verbatim.
- VS Code launched with --ozone-platform=wayland (X11 default fails
  silently with no window).

## Baseline arm (8727135): G1 SUCCESS, G2 SUCCESS after recovery

### G1
- Wall 90.629s (start submit 00:59:49.456 to verify observe 01:01:20.085).
- Requests: windows 1, observe 1, act 3, status 0. Actions 11.
  Group sizes [1, 9, 1]: the full nano chain went as ONE 9-action
  mega-batch in a single request. 0 refusals, 0 session deaths.
- OCR verified all 3 lines. Coordinator note: /tmp/ghi-chu.txt was
  removed by the executor during G2 setup before I byte-checked it;
  the OCR quote plus the ls sighting stand as evidence.
- Analyze.py: span 141.779s (includes the finish deliberation),
  service 2.155s, gap share 98.3 percent.

### G2
- Wall 707.134s (start 01:03:09.011 to verify cat 01:14:56.144,
  includes session recovery).
- Requests: windows 5, observe 11, act 12, status 0. Actions 19.
  Group sizes [1, 1, 1, 1, 4, 1, 1, 1, 1, 1, 5, 1].
- One refusal, verbatim "focus changed": the 4-action tail batch
  [type line, Ctrl+S, type path, Return] completed 3 of 4, then the
  Save As dialog (xdg-desktop-portal-gtk) stole focus mid-batch and
  the driver refused with require_reobserve; the 4th action (Return)
  never ran. The executor pressed Return in the dialog (dialog stayed
  open, Name field showed suffix "ng-2.txt"), then the G2 session
  DIED at 01:07:50.195 (observe returned "window no longer exists",
  next request accepted=false request_error=task_stopped; the cause
  of the death is not established, no error in status).
- Executor recovered per the brief: fresh session g2-restart1
  (generation 84f259ee), new lease dir, retried the save carefully
  (observe dialog, navigate to /tmp, Ctrl+L location entry, correct
  full path), file created 01:14. One local path typo on the first
  retry request (missing ag2-baseline/ segment) cost one failed call,
  no broker request lost.
- Byte-check (coordinator): /tmp/y-tuong-2.txt exactly
  "Hello grouping.", 15 bytes, no trailing newline, sha256
  7b3b6e16fcf7a2b5c73f692fedbaca78d296995cd713c9bf02d5260d7c77767d.
- Analyze.py: span 794.439s, service 6.582s, gap share 99.1 percent.

### Floor probe (baseline)
- 160.140s (01:16:45.947 to 01:19:26.088), windows 1, observe 3,
  act 1, group [1]. One local observation_path read error fixed by
  using the top-level field, no broker request lost.
- Cleanup confirmed: VS Code closed, ag2-base-term closed via
  hl.dsp.window.close, hyprctl clients -j remaining_test_windows=0.
- Baseline totals: windows 7, observe 15, act 16, status 0;
  31 actions; 12 status-polls across 4 starts.
- Analyze.py floor: span 129.534s, service 0.446s, gap share 99.5 percent.

## Method arm (ab5011a): G1 SUCCESS (4 rejections), G2 BLOCKED

### G1
- Wall 555.955s (start 01:24:30.838 to verify 01:33:46.794).
- Requests: windows 1, observe 12, act 11, status polls 3.
  Actions submitted 35 total, 11 completed, 24 in rejected groups.
- Group sizes in request order: [1, 9, 2, 7, 2, 5, 2, 3, 2, 1, 1].
  Accepted: [1, 2, 2, 2, 2, 1, 1]. Rejected: [9, 7, 5, 3].
- Four validation rejections, all verbatim: "action 2 is the first
  unsafe boundary before action 3; split the group after action 2
  and observe again before the remaining actions: a terminal key or
  newline typing cannot be followed by another input action",
  completed 0, recoverable true, each time.
  1. Attempted 9 (full chain): split after action 2, before action 3.
  2. Attempted 7 (remainder: line 2, line 3, save): split after 2.
  3. Attempted 5 (remainder: line 3, save): split after 2.
  4. Attempted 3 (save: Ctrl+O, Return, Ctrl+X): split after 2
     (Return is terminal and must be last; Ctrl+X follows it).
- Accepted splits: [type, key Return] pairs for each line, [Ctrl+O,
  Return] as a pair, [Ctrl+X] alone. The executor re-attempted each
  remainder as one batch, so the brief's prediction (5 requests, 3
  rejections) became 4 rejections; the save batch is the extra boundary
  the prediction did not count separately.
- Byte-check (coordinator, before G2 setup removed it):
  /tmp/ghi-chu.txt 62 bytes, "Note 1: drink water.\nNote 2: read
  books.\nNote 3: go running.\n\n" (3 exact lines plus one trailing
  blank line from the third Return), sha256
  66fb03fafc002bbffad2a60c9a1b9784a3f27f6ab3258b1232c1a5f4b48cd043.
- OCR verified all 3 lines. 0 session deaths, 0 request errors.
- Analyze.py: span 639.540s, service 5.147s, gap share 99.2 percent,
  image bytes 7,702,094 (vs baseline G1 1,734,416: 12 observes vs 1).
- The executor's own summary notes the net act-request saving is 0
  against a one-action-per-request baseline (11 requests for 11
  actions). Against the actual unconstrained baseline (3 requests
  for the same 11 actions) it is 11 vs 3: more requests, not fewer.

### G2
- Status: BLOCKED, focus changed during the save chain. End state
  not verified. Wall 262.329s (start 01:36:48.003 to the focus
  refusal 01:41:10.332).
- Requests: windows 2, observe 5, act 5, status polls 3.
  Actions submitted 11, driver reported 10 completed before the
  final refusal, including 3 in the save chain whose effects are
  uncertain.
- Group sizes [1, 2, 2, 2, 4]. Validation grouping rejections: NONE.
  The menu opens used [move, click] pairs (legal); the tail batch
  [type line, Ctrl+S, type path, Return] is legal under strict policy,
  so the method executor sent it, exactly as the baseline did.
- Focus refusal: the 4-action tail batch completed 3 of 4, error
  "focus changed", broker next step "List windows and observe the new
  focused window, or observe the screen, before further input. The
  after image is not a new observe. Do not replay completed or
  uncertain actions." The executor followed what it read as the
  task-specific stop rule and sent no further actions and no terminal
  cat verification; it wrote the G2 summary and finished the session
  after a 117.387s deliberation (finish think 113.3s).
- /tmp/y-tuong-2.txt does NOT exist (verified by coordinator).
  No session death in the method G2 (the session was finished
  explicitly by the executor).
- The floor probe was skipped by the executor ("the focus-stop rule
  ended desktop driving"), so there is no method floor probe.
- Cleanup: the executor closed VS Code, the Save As dialog, and its
  terminal after the G2 finish; desktop verified clean (herdrdrop,
  Zen Pill fixture, executor kitty only). No file was created by
  the cleanup.
- Analyze.py: span 379.971s, service 2.962s, gap share 99.2 percent,
  image bytes 1,285,797.

### Method totals
- Grand totals (analyze.py): service 8.109s, gap 1011.041s.
  G1 service 5.147s, G2 service 2.962s.

## Comparison

| | Baseline (8727135) | Method (ab5011a) |
| G1 wall | 90.629s | 555.955s (6.1x) |
| G1 act requests | 3 | 11 |
| G1 observes | 1 | 12 |
| G1 group sizes | [1, 9, 1] | [1, 9, 2, 7, 2, 5, 2, 3, 2, 1, 1] |
| G1 grouping rejections | 0 | 4 (all verbatim, completed 0) |
| G1 image bytes | 1,734,416 | 7,702,094 |
| G1 result | SUCCESS | SUCCESS |
| G2 wall | 707.134s (to success) | 262.329s (to refusal) |
| G2 act requests | 12 | 5 |
| G2 group sizes | [1,1,1,1,4,1,1,1,1,1,5,1] | [1, 2, 2, 2, 4] |
| G2 grouping rejections | 0 | 0 |
| G2 focus refusals | 1 (recovered) | 1 (stopped, BLOCKED) |
| G2 session deaths | 1 (cause unknown) | 0 |
| G2 result | SUCCESS | BLOCKED |
| Floor probe | 160.140s, done | skipped |

## Why the method loses on wall

- The validator forces an observe between every [type, Return] pair.
  Each observe costs a full model think cycle (the method G1 thinks
  were 8-57s each; the finish deliberation alone was 78.7s). The
  service time of an observe is about 0.15s, so the cost is almost
  entirely model think, not harness service.
- The baseline's single 9-action mega-batch executed correctly in
  one request, so the safety benefit the validator is meant to buy
  did not materialize on G1, while the cost (8 extra act requests,
  11 extra observes, 4 rejections each followed by a re-observe)
  did.
- On G2 the validator changes nothing: the only multi-action group
  in the task (the 4-action tail) is legal under strict policy, so
  both arms send it and both hit the same focus-change refusal.
  The grouping validator cannot prevent a dialog from stealing
  focus mid-batch; that failure mode is outside its scope.
- The G2 outcome difference (baseline SUCCESS after recovery vs
  method BLOCKED) is the executors' recovery choice, not the
  validator: the baseline executor listed windows, observed the
  dialog, restarted the session, and retried the save; the method
  executor read the broker's next step as a stop and finished
  without retrying. Do not attribute the G2 BLOCKED to grouping.

## Notes and open items

- The baseline G2 session death (01:07:50.195, task_stopped) has no
  established cause; it is recorded as unknown with the evidence
  (observe "window no longer exists", next request accepted=false).
- The baseline G1 file was not byte-checked (removed by G2 setup
  before the check); the method G1 file was byte-checked promptly
  in the gap, 62 bytes with a trailing blank line.
- The method G2 BLOCKED is a single-executor outcome; a re-run
  with an executor that recovers (as the baseline one did) would
  test whether the method arm can also reach SUCCESS on G2, but
  that was not run: the arm finished and the campaign moves on to
  Task 4. The G1 result alone is enough to verdict the method a
  LOSS on wall.
- Executor files: baseline summary.md (51 lines) and method
  summary.md (42 lines) in their run dirs; records.jsonl,
  decisions.log, analyze.py output retained in both.
