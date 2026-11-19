# Event-wait + sequence prototype (Rank 4) + H4 then flag

- Owner: Pham Tuan. Worker: Luna 6 Max, Track 2 resume round 2, 19/11.
- Branch: `event-wait-seq`, base `origin/speed-swarm` 8727135.
- Status: PROTOTYPE DONE, unit tests green, READY FOR LIVE MEASURE. A/B NOT run (broker busy, see below).

## What was built (scripts/cu.py only, no broker/relay change)

- `wait_for_event(env, match, timeout_ms)`: blocks on the Hyprland event
  socket (`.socket2.sock`) instead of a fixed sleep. Events: openwindow,
  closewindow, activewindow, workspace, windowtitle, movewindow, with
  address/class/title/workspace filters. Answers instantly with
  `already: true` when the condition already holds (hypruse semantics).
  Timeout (0-30000 ms, default 5000) returns `timed_out: true`; the caller
  falls back to a full observe. A missing event socket raises RuntimeError
  (same fallback, never a hang). Closewindow class/title filters resolve to
  the live address first, since the event carries only the address.
- `sequence`: `desktop_act` now accepts `{"type": "wait_for", ...}` steps
  interleaved with actions in one act list. Stop-on-unexpected-change is
  enforced by the existing guard before and after every step; a timed-out
  wait stops the sequence with `error_code: wait_for_timeout` and
  `next_step` re-observe. `expect_focus: "same" | "any" | <address>` declares
  a focus change the awaited event legitimately causes. Results carry a
  `wait_for` list (index, event, already, elapsed_ms, timed_out).
- Terminal transition: the 1.5 s poll loop after the final group now tries
  the guard first (same single query as before when focus is already on the
  terminal window), then the activewindow event wait, then the poll fallback
  if the event socket is missing.
- `then`: `act --then` returns the post-action observation in the same
  result (`result['then'] = result['after']`, `then_included: true`);
  conflicts with `--no-after` (fast ValueError). `compact_result` now
  compacts `then` like `after`.

## H4 (act returns post-action observation)

- (a) CONFIRMED by code reading, no build needed: `desktop_act` captures
  after the act (`after_capture=True`); `compact_result` keeps
  `after.image` (path + geometry); the session driver returns it; and
  `scripts/mcp_bridge.py` `image_paths` walks the whole response and
  base64-attaches every `.png` image path (including `result.after.image`)
  to the executor's tool result. `VisualCheckpoint` (image_policy auto)
  suppresses only pixel-identical repeats. The post-action image DOES reach
  the executor in the same call.
- (b) Brief change written in the A/B executor brief template
  (`improvements/heldout-executor-brief-template.md`, VM working copy):
  OPTIMIZED now says judge the end state from the act result's post-action
  image in the same call, re-observe only if it is stale, unclear, or does
  not show the end state; plus an arm-only EVENT-WAIT + SEQUENCE block
  (wait_for steps, timeout fallback, expect_focus, `act --then`).
- Overlap note: H4's incremental value is only on the non-code-exec,
  non-file-provable path. A4 (deterministic postcondition verify) already
  covers file-provable tasks and Pick 1 code-exec already asserts
  in-program. Do not claim H4's 6.7 s verify-observe saving until an A/B
  shows the finish call does not absorb the judge think.

## Tests (full suite, worktree with ignored native artifacts restored)

- Worktree gap (found by the A4 worker, applied here): a fresh worktree
  lacks gitignored native binaries (`native/wtype`, `pointer`, `indicator`,
  `modifiers`, `cursor-guard.so`) and generated `*-protocol.c/.h` files.
  Without them the suite errors 66 tests and hides 23 more. Fix: copied
  the 18 `native/` entries from git's ignored-files list in the main
  checkout (tar, never committed). Do not diagnose those 66 as code
  failures.
- Clean baseline (baseline3, 8727135 + artifacts): Ran 1339 tests in
  106.589 s, FAILED (failures=7, skipped=2), 0 errors. FAIL sha
  e6442202b3a4ca9c7b1db55479b62b44b35d624d34c40895ea5619fb7ce14720.
- Post-change (postchange4, +21 new tests): Ran 1360 tests in 102.779 s,
  FAILED (failures=7, skipped=2), 0 errors. FAIL sha identical
  (e6442202...). Zero new failures, zero errors.
- New tests: `tests/test_event_wait_seq.py`, 21 tests, all pass
  (validate_wait_for, validate_actions, keyboard grouping, already:true
  paths, real Unix event-socket match/skip/timeout, --then/--no-after
  conflict, compact_result keeps `then`).
- One real failure found and fixed during the run: postchange3 added
  `test_expected_successor_allows_dialog_close_without_after_capture`.
  Cause: the wait-first terminal ordering issued an extra activewindow
  query, draining the harness's consumable answer queue. Fix: guard-first
  ordering in cu.py (same single query on the fast path) plus the harness
  mock made sticky-last (`tests/test_act_diagnostics.py`: the last answer
  repeats, like a real compositor). Both terminal tests pass after the fix.

## A/B status: READY FOR LIVE MEASURE, not run

- Broker was busy for the whole prototype window: relay MainPID 538032,
  owner `r3-baseline`, state running (checked 19:58-20:00, next_sequence 8).
  R3-baseline finished 20:03:39 (`r3-final-finish rc=0`, broker state
  finished, driver stopped), but the DOM-REPLICATE worker has R3-dom
  briefed and queued (`/tmp/speed-dom-replicate-20261119/r3-dom/`), so the
  broker is effectively reserved next.
- Blocker beyond the broker: the prototype lives on branch
  `event-wait-seq` in the worktree
  (`/home/james/computer-use-wayland-eventwait`); the relay serves cu.py
  from the main checkout (`/home/james/computer-use-wayland`), which
  currently holds another worker's uncommitted A4/det-finish work. The A/B
  cannot run live until the coordinator sequences the landing (my branch
  into the main checkout, or a rebase after the A4 work lands).
- A/B plan (unchanged): 4 held-out tasks (P1-P4), event-wait + sequence
  arm vs sleep + single-action arm, reporting wall (headline), think
  total, model calls, timeouts, missed-event incidents. Success bar: lower
  wall with no rise in timeouts or missed events.

## Follow-ups (not done here)

- Expose `wait_for` to code-exec programs (needs `code_exec.py`
  allowlist + API dispatch; out of scope for this prototype).
- Live probe of `wait_for` against a real kitty open (event socket on the
  live desktop) as part of the A/B, not as a standalone claim.
- Live-test-log entries for this work are in
  `improvements/live-test-log.md` (laptop repo + VM copy).

## Timing (Asia/Ho_Chi_Minh, 19/11)

- 19:40 start, research + repo recon. 19:42 branch `event-wait-seq` created
  (worktree, main checkout left untouched with the other worker's dirty
  files). 19:46 baseline1 (gap env) 1316 tests, 9 failures, 66 errors.
  19:47 baseline2 died mid-run (concurrent load). 19:57 post-change run
  killed (gap env, superseded by the A4 worktree-gap finding). 20:00
  baseline3 clean 1339 tests, 7 failures, 0 errors. 20:03 postchange3
  1360 tests, 8 failures (1 new, fixed). 20:05 postchange4 1360 tests,
  7 failures, 0 errors, FAIL set identical to baseline3.
