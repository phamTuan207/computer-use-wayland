# Speed swarm profile: measured computer-use loop, 2026-11-18

Run date: 2026-11-18, evening (v3 executor 22:04 to 22:31 +07, clean floor probe 22:35).
Owner: the owner. Repo: phamTuan207/computer-use-wayland, HEAD 21684e7.
Model in the loop: Codex gpt-6-luna, max reasoning, full access, on the laptop.
Method: real broker loop, optimized discipline (one observation, ground all controls,
batch actions in one act request, re-observe only to verify).

Sources: `~/workspace/speed-profile-20261118/records.jsonl` (87 lines),
`decisions.log` (43 entries), `summary-v3.md`, `analyze.py` output, `floor-probe2.sh`.
Wall time per task is session start submit to verified end state (the verify
observation result). Finish calls are excluded: their gaps (14s to 104s) are
post-task writeup, not loop time.

## Headline

All 4 held-out tasks SUCCEEDED. Combined wall time 289.9s. The loop is
dominated by model think time, not by local transactions. In the 3 clean tasks
(mean wall 36.4s) the broker did 1.4s of work (about 4%) and the model spent
34.2s thinking (about 94%). The scripted zero-thinking harness floor for the
same loop shape is 2.1s start to verified end state. Even a perfect harness
(0s) would save at most about 2s per task. The 10x lever is model think time.

## What was fixed first (v1/v2 blocker)

v1 (21:40) died when the user accidentally hit ESC and latched cancellation.
v2 (21:47 to 21:54) ran P1/P2 and both BLOCKED on a tooling gap, not the
machine: the `timed.py` wrapper dropped broker response bodies, so the window
address and observation paths were unavailable, and request files created with
a default umask were refused with `unsafe_file` (the broker requires request
files private, mode 600).

The v3 wrapper fix, verified live before any task:

- `cmd_req` now preserves the full broker result payload in every record:
  `result` (the cu.py output), `windows` (window list), `observation_path`,
  `image_path`, `after_observation_path`, `after_image_path`,
  `driver_returncode`, `result_stderr`.
- `cmd_req` chmods the envelope file and any `.json` file it references
  (actions file, observation file) to mode 600 before submitting.
- `emit` guards the JSONL append against a missing trailing newline.

Verification: the throwaway `test-windows` session returned the full window
list in its record (5 windows with address, class, title, position, size).
The P1 refusal below is preserved in full in its record, including the
`screen changed` error, `completed: 0`, and the after-image path. The latch
stayed clear through the whole v3 run (no ESC event).

## Per-task results

### P1, C-03: "O dia con trong bao nhieu?" (df -h /)

- Result: SUCCESS. Wall 180.712s (22:11:55 to 22:14:56).
- Evidence (OCR of verify observation): `Filesystem Size Used Avail Use%
  Mounted on`, `/dev/mapper/omarchy_root 3856 3786 5.46 99% /`. Free space
  of `/`: 5.4G.
- Requests: windows 1, observe 4, act 2, status 0 (3 startup polls).
  Observations 4, act requests 2, actions submitted 2, executed 1.
- Refusal: first act accepted by the broker, then refused `screen changed`,
  `completed: 0`, driver returncode 1, preflight 151ms. Recovery was 2 extra
  observes plus 1 retry act, which succeeded with `target_was_focused: true`.
- Request service (start to verify): 1.592s. Images: 4,754,939 bytes (4 obs).

| Step | Think before (s) | Service (s) |
| --- | --- | --- |
| session start (ready) | n/a | 0.191 call, ready 0.871 |
| windows | 5.9 | 0.114 |
| observe (terminal window) | 7.1 | 0.206 |
| act (df -h /) | 68.2 | 0.221, refused |
| observe screen (after refusal) | 24.7 | 0.164 |
| observe (terminal, retry) | 64.5 | 0.170 |
| act retry | 0.0 | 0.367 |
| verify observe | 7.7 | 0.159 |
| Think total | 178.1 | Service total 1.592 |

### P2, E-04: "144 tren 150 la bao nhieu phan tram?"

- Result: SUCCESS. Wall 39.384s (22:16:23 to 22:17:02).
- Evidence: verify observation output ends with `96.0`.
- Requests: windows 1, observe 2, act 1, status 0 (3 startup polls).
  No refusals, no session death.
- Request service: 1.132s. Images: 2,553,359 bytes (2 obs).

| Step | Think before (s) | Service (s) |
| --- | --- | --- |
| session start (ready) | n/a | 0.192 call, ready 0.857 |
| windows | 5.3 | 0.111 |
| observe (terminal window) | 9.1 | 0.179 |
| act (python3 print) | 16.4 | 0.491 |
| verify observe | 6.7 | 0.159 |
| Think total | 37.5 | Service total 1.132 |

### P3, B-01: mkdir hoc-ky-2 with 3 subdirs

- Result: SUCCESS. Wall 30.924s (22:17:33 to 22:18:04).
- Evidence: verify observation showed all 4 paths: `/tmp/hoc-ky-2`,
  `/tmp/hoc-ky-2/dsa`, `/tmp/hoc-ky-2/ktvm`, `/tmp/hoc-ky-2/oop`.
- Requests: windows 1, observe 2, act 1, status 0 (3 startup polls).
  No refusals, no session death.
- Request service: 1.440s. Images: 2,614,343 bytes (2 obs).

| Step | Think before (s) | Service (s) |
| --- | --- | --- |
| session start (ready) | n/a | 0.222 call, ready 0.893 |
| windows | 4.6 | 0.109 |
| observe (terminal window) | 7.3 | 0.184 |
| act (mkdir + find) | 10.3 | 0.760 |
| verify observe | 6.5 | 0.165 |
| Think total | 28.7 | Service total 1.440 |

### P4, A-01: write y-tuong.txt, 3 exact lines

- Result: SUCCESS. Wall 38.862s (22:18:42 to 22:19:21).
- Evidence: verify observation showed the exact 3 lines:
  `Ý tưởng 1: app nhắc uống nước.`,
  `Ý tưởng 2: bot tóm tắt bài giảng.`,
  `Ý tưởng 3: web bán đồ secondhand.`
  OCR (English-only model) read them approximately; the broker observation
  image itself shows the exact lines with diacritics.
- Requests: windows 1, observe 2, act 1, status 0 (3 startup polls).
  No refusals, no session death.
- Request service: 1.726s. Images: 2,687,751 bytes (2 obs).

| Step | Think before (s) | Service (s) |
| --- | --- | --- |
| session start (ready) | n/a | 0.190 call, ready 0.864 |
| windows | 4.8 | 0.114 |
| observe (terminal window) | 6.6 | 0.178 |
| act (printf + cat) | 18.1 | 1.086 |
| verify observe | 6.8 | 0.158 |
| Think total | 36.3 | Service total 1.726 |

### Combined

- P1 to P4 walls: 180.712 + 39.384 + 30.924 + 38.862 = 289.882s.
- Clean-task mean wall (P2, P3, P4): 36.390s. Clean-task mean request
  service: 1.433s. Clean-task mean think: 34.167s.
- No task was blocked. No session died. 0 logged sleeps.

## Verified loop breakdown: think gaps vs local transactions

Definitions. Think = time from the previous request result to the DECIDE line
the executor writes before the next timed.py call (model reasoning plus
reading the observation image). Prep = DECIDE line to timed.py submit.
Service = timed.py submit to result, measured on the laptop. All three come
from `records.jsonl` plus `decisions.log` through `analyze.py`.

Clean tasks (P2, P3, P4), mean of 3:

| Component | Mean seconds | Share of 36.4s wall | Seconds per 100s task at same share |
| --- | --- | --- | --- |
| Think before act | 14.9 (10.3 to 18.1) | 41% | 41 |
| Think before first observe | 7.7 (6.6 to 9.1) | 21% | 21 |
| Think before verify observe | 6.7 (6.5 to 6.8) | 18% | 18 |
| Think before windows | 4.9 (4.6 to 5.3) | 13% | 13 |
| Broker service, all requests | 1.4 (1.13 to 1.73) | 4% | 4 |
| Session startup (submit to ready) | 0.9 (0.86 to 0.89) | 2% | 2 |
| Prep (DECIDE to submit) | 0.0 | 0% | 0 |

Notes on the breakdown:

- Prep is 0.0s on every v3 request: once the model decides, it submits
  instantly. There is no measurable command-construction cost after deciding.
  All gap time is model-side, before the DECIDE line.
- The think gaps include the model reading the observation PNGs (about
  1.1 to 1.3 MB each at max-width 960, 924x1176). The observe service itself
  is only 0.16 to 0.21s, so image delivery is not the cost; the model reading
  the image is.
- Startup ready (0.86 to 0.89s) is start call 0.19s plus 3 status polls at
  about 0.06s each plus the 0.25s sleeps between polls inside timed.py.
  The first request follows ready by 0.04 to 0.05s in the scripted probe.
- P1 is not in the clean mean because of the refusal. Its think total was
  178.1s on a 180.7s wall (98.6% think, 0.9% service).

## Harness floor (scripted, zero model calls)

The executor's first floor probe (labels `floor-*`) ran 77.442s wall, but
75.113s of that was a repair gap: its probe script had a syntax error after
the observe steps, and the executor fixed it by hand before resuming. Its
clean segments were 1.477s before the gap and 0.851s after. That probe is
NOT a valid floor measurement, so a second clean probe was run as a script
(`floor-probe2.sh`, labels `floor2-*`): start, windows, observe screen,
observe window, act (one harmless empty command), observe window, finish,
back to back, no DECIDE lines, no model calls.

Clean floor (floor2), start submit to verify result: 2.116s. Start submit to
finish result: 2.406s.

| Component | Seconds | Share of 2.116s floor |
| --- | --- | --- |
| Session startup, submit to ready | 0.857 | 40% |
| Request service after ready | 0.980 | 46% |
| Script gaps between requests | 0.278 | 13% |
| windows service | 0.113 | 5% |
| observe service (3x, mean 0.174) | 0.521 | 25% |
| act service | 0.346 | 16% |

Per-request service detail (floor2 and v3 tasks):

- windows: 0.109 to 0.114s every time (request call about 0.06s, result
  call about 0.05s).
- observe: 0.159 to 0.206s. Capture itself is 43 to 60ms (`capture_ms` in
  the result); the rest is result polling plus image handling.
- act: 0.221 to 1.086s, driven by execution time, not by the harness.
  `execution_ms` was 29ms for the empty floor command, 66ms for the P1
  retry, 174ms for the P2 python one-liner, 457ms for the P3 mkdir plus
  find, 769ms for the P4 printf of 3 Vietnamese lines plus cat. Preflight
  is 65 to 151ms. Typing long text costs real execution time; the harness
  around it costs about 0.06s request call plus 0.10 to 0.31s result wait.
- finish: 0.155 to 0.261s.

Floor conclusion: one full loop (start, windows, 3 observes, 1 act, finish)
costs 2.4s with zero thinking. A 31s clean task therefore carries about 2s
of irreducible harness, about 6%. A 100s task carries the same 2s, about 2%.

## Top residual hot spots, ranked by measured seconds

Ranked on the clean-task means (P2, P3, P4), with the P1 refusal as a
conditional entry. The "per 100s" column scales each share to a 100s task.

1. Think before act: compose the action from the observation. Mean 14.9s,
   41% of a clean task, about 41s per 100s task. Largest single cost, and
   the most variable (10.3s in P3, 18.1s in P4). This is the model reading
   the terminal observation and deciding the exact command text. It is also
   where the P1 outlier sits: 68.2s before the first P1 act.
2. Think before first observe: read the windows list, pick the terminal,
   build the observe envelope. Mean 7.7s, 21%, about 21s per 100s.
3. Think before verify observe: read the act result, judge the end state,
   build the verify observe. Mean 6.7s, 18%, about 18s per 100s. Very
   stable across tasks (6.5 to 6.8s).
4. Think before windows: session start to first request. Mean 4.9s, 13%,
   about 13s per 100s. Stable (4.6 to 5.3s).
5. Broker service, all requests combined. Mean 1.4s, 4%, about 4s per 100s.
   Inside it, act service is the largest (0.49 to 1.09s, mostly typing
   execution time), then observes (0.34s for 2), then windows (0.11s) and
   the start call (0.19s).
6. Session startup ready wait. 0.86 to 0.89s, 2%, about 2s per 100s. About
   0.5s of it is the poll sleeps inside timed.py, which could be shortened.
7. Conditional: `screen changed` refusal cascade (P1 only). The refusal
   itself cost 0.221s of service and 0 completed actions. The recovery cost
   89.2s of extra think (24.7s before the screen re-observe, 64.5s before
   the retry observe), 0.701s of extra service, and 2 extra observations.
   In P1 it was about half the 180.7s wall (90s of 181s). In clean runs it
   is zero. If refusals are frequent, this is hot spot number 1; if rare,
   it is noise.

Two structural observations from the records:

- After the P1 refusal, the retry act think was 0.0s: the model did its
  retry-act composition during the 64.5s gap before the retry observe, then
  fired observe and act back to back. The model CAN batch thinking across
  steps when it plans ahead. In the clean tasks it did not: each step's
  think happened after the previous result.
- The P1 first-act think of 68.2s is unexplained by the records. It is 4 to
  7 times the clean mean for the same step. No refusal or error precedes it.
  Treat it as variance (one slow model call), not as a systematic cost,
  until it repeats.

## What this means for the 10x goal

- The harness is not the bottleneck. Broker service is about 1.4s per task
  and the scripted floor is 2.1s per loop. This matches the Track 1 verdict
  recorded in memory (Rust rewrite evaluation, 22:14): the pure Python CPU
  in the harness is only 1.0 to 1.5s of a 101s task, so a rewrite cannot
  move the total. Do not spend the 10x budget on the harness.
- The budget is model think time: 34.2s of a 36.4s clean task, and 178.1s
  of the 180.7s P1 task. The biggest single item is think-before-act
  (41%). Anything that cuts per-step model latency, or lets the model
  decide the next action while the current request is still in flight,
  attacks the largest share. The P1 retry (0.0s think before the retry act)
  shows the shape of the win: decide the next step during the current
  step's gap instead of after its result.
- Refusal avoidance is the second lever. One `screen changed` refusal cost
  about 90s, more than two whole clean tasks. If the screen-change rate can
  be driven down, the worst-case task time falls toward the clean mean.

## Limits of this profile

- 4 tasks, 1 run each, 1 model (gpt-6-luna max), 1 machine, 1 evening.
  Think times vary a lot (act think 10.3 to 68.2s), so the means are rough.
- Think is measured only as the gap to the DECIDE line. It lumps together
  model reasoning, vision reading of the observation image, and tool-call
  latency. The split between those three is not measurable from these
  records.
- The floor probe used an empty act (29ms execution). Real acts cost 66 to
  769ms of execution, so a real-task floor is about 2.1 to 2.9s, not 2.1s.
- P4 verification relied on the broker observation image for the exact
  diacritics; the installed tesseract model is English-only and misread
  them, so the byte-exact claim rests on the image, not on OCR text.
