# Worker C4-S2-FLIP log: S2 one-class flip (CU_CODE_EXEC=1) for clone chat sends

Owner: Pham Tuan. Coordinator: COORD-CLICK-4. Step 6 of the FINAL
direction (improvements/worker-click3-final-direction-log.md, sections
1.3 S2 row, 2 item (e), 3 step 6, 6 workers 8-9, 4 rung 2 conditions).
Repo ~/workspace/computer-use-wayland, branch todolist-push.
Start: 09:21 +07, Sun 2026-11-22. No em dash or en dash anywhere in
this file. No personal info.

## 0. Plateau definition (coordinator-set, HARD GATE, recorded here)

- Task class: clone chat sends (clone1 Brave + clone2 Chrome on workspace 2).
- Form (RTD's): after the flip, run the class live 5 times; take the
  median wall time end to end including transport, DOM-scored by the
  V12 sent-bubble gate.
- Threshold: 60 seconds. Plateau REACHED if the median stays above 60s
  for those 5 runs (this triggers the step 9 prototype decision).
  Below a 60s median, S2 is still improving and the class expands.
- Grounding: fixture bench (same shape, headless, no transport) is
  10.86s (a1a672d) / 12.69s (re-run at d7d569b); live stepwise baseline
  is 150-243s (CL2-MSG 243s one clone; Codex about 150s action time).
  60s is about 5x the fixture bench and about 1/3 of the stepwise
  live time: demanding but reachable. If the flipped class cannot
  beat a 60s median, the mechanism (not the model) is the bottleneck
  and the prototype is the next lever.

## 1. B2 lift status at start (from the brief, verified below)

- (a) Fixture bench green: MET (a1a672d 10.86s, re-run 12.69s at
  d7d569b with manifest locked).
- (b) 3 Y1b real fails fixed: MET (per brief; re-verified from the
  step-1 closeout record in section 1.1).
- (c) CB-1 gate for the flipped class: MET (step 5 landed the
  three-part contract for the class, commit 76d0a56).
- (d) Plateau defined: SET ABOVE by the coordinator.
- Flip authorized for ONE class only, act-now as fallback.

## 2. Time log (wall-clock Asia/Ho_Chi_Minh, elapsed from 09:21 +07)

- 09:21 +07, T+0m: task received. VM HEAD 4d090fb (matches brief).
  Read the FINAL direction (sections 1.2 P1/P5/P3, 1.3 S2, 1.4 CB-1,
  2 items (b)(d)(e)(f), 3 steps 5-6, 4 rung 2, 5 B2, 6 workers 8-9),
  the step-5 log (76d0a56) and the P3 probe log (924ec3f) in full.
- 09:23 +07, T+2m: laptop state checked via ssh-laptop.sh. Laptop
  HEAD 56f5af4 (BEFORE sync, see section 3). Codex live-confirm PID
  945044 alive, 20:08 elapsed, working in /tmp/click4-live-confirm.
  Relay PID 1821 alive, 18:06 elapsed.
- 09:30 +07, T+9m: laptop divergence found (section 3). Read-only
  CDP inspection of the live clone2 thread (Chromium
  127.0.0.1:9223): composer is a TEXTAREA with aria-label Message
  (no name attribute); NO [data-sender] elements on the live page
  (count 0), so the bench default bubble selector does not apply
  live; message items are [data-message-item] x40 with
  data-message-role user/assistant and data-message-side user/agent
  (user 6, assistant 34); the log is one [role="log"] with 47 kids
  and its last child IS a message item;
  '[role="log"] > [data-message-item]:last-child' matches exactly 1
  element (the program trailing-assert selector). Composer rect
  (452, 1091, 622x24) matches the P3 harvest rect exactly.
- 09:39 +07, T+18m: Codex live-confirm is DONE (PID 945044 gone;
  the 970156 pgrep hits were my own ssh command line). Log
  /tmp/codex-live-confirm-out.log ends with the push to branch
  live-confirm-codex, commit b57f499: F1 sanitization PASS, item 8
  PASS, items 5-6 FAIL (ZenDomError). No live worker remains on the
  laptop; the sequencing constraint for live sends is lifted, but
  the pre-send Codex check stays in the harness procedure.
- 09:42 +07, T+21m: full test discover after wiring: Ran 2031 in
  210.967s, FAILED (errors=1, skipped=17), failures 0. The single
  error is the pre-existing test_cursor_file setUpClass (g++ does
  not recognize -std=c++26), unchanged from the step-5 baseline.
  Delta +9 over the step-5 after-run (2022) is exactly my 9 new
  wiring tests.
- 09:47 +07, T+26m: transport finding. Plain ssh-laptop.sh calls
  cost about 3.3s each (no multiplexing in effect: no ssh config,
  no live master, cm/ and pick3-cm/ socket dirs empty). S0 landed
  in 18f2304 (scripts/ssh-laptop-mux.sh, scripts/ssh_mux.py);
  first mux call 3.24s creates the master, second call 0.92s.
  The harness uses the S0 mux wrapper. A dead master costs one
  slow call and self-heals via ControlMaster=auto.
- 09:49 +07, T+28m: broker-env finding, harness v2. The broker
  cannot set CU_CODE_EXEC per request: the driver env comes from
  the relay process env (base_env = dict(os.environ) of the relay
  serve process), and the relay was started without the flag.
  So the code-exec send runs as a one-shot session-driver with
  CU_CODE_EXEC=1 on its own command line, the only place the flag
  is on. Broker stays for routing (tabs, observe) and P9 goes
  direct CDP. Harness v2 rewritten; 9/9 wiring tests still pass;
  /tmp/s2-p9.mjs copied to the laptop.

## 3. Laptop sync (step 8a pulled forward)

- Laptop HEAD before: 56f5af4 (detached HEAD, "Record H6 prefetch
  results"). Laptop HEAD after: (to be filled).
- Divergence found at 09:30 +07, BEFORE any sync step: 56f5af4 is NOT
  an ancestor of origin/todolist-push (ANCESTOR-NO), so a plain
  fast-forward is impossible. The laptop checkout sits on a different
  line (speed-swarm/harness-prefetch era). The sync therefore moves
  the checkout to origin/todolist-push by branch switch, not by
  fast-forward. The old HEAD stays recoverable via the reflog; the
  pre-switch HEAD is recorded here (56f5af4).
- Local modifications found on the laptop checkout (all preserved
  BEFORE the switch, see below): improvements/live-test-log.md (+654
  lines, Nov 19 watchdog entries, mtime 2026-11-20 14:41),
  native/hyprglass-local-optics.lua (6 insertions, 1 deletion, mtime
  2026-11-21 22:35), scripts/cu.py (OBSERVATION_MAX_AGE 90 to 120,
  mtime 2026-11-20 18:04; this change is ALREADY upstream on
  todolist-push, scripts/cu.py line 78 reads 120 there, so restoring
  it loses nothing). The live-test-log.md additions are NOT in the
  todolist-push copy (4233 lines upstream vs 4854 local); they are
  preserved verbatim in the backup below.
- (sync steps to be filled)

## 4. Wiring: P1 router into the live path, CU_CODE_EXEC=1 per class

### 4.1 cu.py code-exec --endpoint (P3 port split, load-bearing)

- Finding: `cu.py code-exec` had NO --endpoint flag and no env var
  for the browser endpoint. The CodeExecBackend reads the module
  global BROWSER_ENDPOINT, default http://127.0.0.1:9223. Without a
  fix, every code-exec program aimed at Brave ([::1]:9223, clone1)
  would silently drive Chromium (127.0.0.1:9223, clone2). This is
  the P3 trap in code form, and it made the clone1 half of the class
  unflippable.
- Change (scripts/cu.py, minimal): --endpoint added to the code-exec
  subparser; the branch validates it loopback-only
  (_validate_browser_endpoint, same rule browser_start enforces)
  and applies it to that program only, restoring the retained
  default in a finally, exactly like the browser tabs one-command
  override. The backend reads the global at construction and
  dom_start reads it at call time, so the override covers the whole
  run_program call.
- Tests: tests/test_s2_flip_wiring.py, 9 tests, 9/9 OK. Override
  reaches the backend and restores the default; no flag keeps the
  default; non-loopback and bad-port endpoints refuse before any
  program runs.

### 4.2 Harness scripts/s2_flip_live.py (VM-side driver, v2)

- One broker session per run for routing, both browsers, endpoints
  named per browser (Brave http://[::1]:9223, Chromium
  http://127.0.0.1:9223).
- Per browser: tabs (find the one muse.ai tab) -> observe (coverage
  probe) -> route_perception with the real harvest coverage, one
  perception_routing line logged per decision; a screenshot decision
  aborts the send, fail closed.
- The code-exec send itself is a one-shot session-driver with
  CU_CODE_EXEC=1 on its command line (section 4.3: the broker
  cannot set env per request, the driver env comes from the relay
  process env). After the send, an independent V12 verify (fresh
  DOM read via /tmp/s2-v12.mjs, not the program asserting its own
  success), then a P9 viewport capture via direct CDP screenshot
  (/tmp/s2-p9.mjs, no session, no workspace switch) after the
  scored wall stops.
- Transport: S0 mux (scripts/ssh-laptop-mux.sh). Plain
  ssh-laptop.sh costs about 3.3s per call with no master alive;
  the mux wrapper reuses the master at about 1s per call (first
  call 3.24s creates it, second 0.92s, measured 09:47 +07). A dead
  master costs one slow call and self-heals via
  ControlMaster=auto, so the harness does not need a separate
  master watchdog for the runs.
- The fixed send program (build_program, validated by the code-exec
  AST validator, 637 chars): dom_observe the tab, ground the
  composer from the snapshot (role textarea/textbox, name Message),
  fill (click plus focus check plus insertText plus read-back),
  Enter, trailing assert on
  '[role="log"] > [data-message-item]:last-child' with the message
  text, timeout 3000ms, then assert_state on the dom_act result so
  a failed send fails the envelope. The actions satisfy
  dom_asserts.require_asserts (tested).
- Model calls in the loop: 0. The program is written once before
  run 1 and reused unchanged; no vision call and no per-action
  model call in the machine loop. The P9 review is the only vision
  read, unscored human evidence.
- Wall time per run: harness t0 to both V12 verifies done, including
  all transport. Phase split from spans: model 0; ssh is transport
  above laptop work (mux baseline measured per run, 2 probes);
  broker/observe/act/verify are laptop-side times; residual is
  whatever the split does not attribute.
- CB-1 three-way per send, from the program log: input_sent is
  dom_act completed >= 2 (fill plus Enter ran), target_received is
  completed >= 1 (fill verified its read-back before completing),
  verified is the independent V12 result.
- Fallback: if the code-exec program fails, the run records the
  failure; the stepwise act-now fallback is available per the
  brief, but no fallback send is attempted inside a scored run
  (a fallback send would be a different mechanism and would void
  the measurement).
- Helper scripts on the laptop: /tmp/s2-v12.mjs (independent V12),
  /tmp/s2-p9.mjs (P9 screenshot), /tmp/s2-seed.mjs (dry-run
  scratch tab with a fake composer and thread),
  /tmp/s2-inspect*.mjs (read-only DOM inspection, already used,
  section 2).

### 4.3 CU_CODE_EXEC=1, scope of the flip

- The flag is set ONLY on the one-shot session-driver command
  line for the clone-chat-send class's code-exec sends
  (harness oneshot_code_exec). It is off everywhere else: the
  relay, the broker, and every other cu.py invocation run
  without it, and cu.py refuses code-exec without it.
- Why one-shot, not the broker: session_remote.py builds the
  driver env from the relay process env (base_env =
  dict(os.environ) of the relay serve process), and the relay
  was started 18h ago without CU_CODE_EXEC. The broker envelope
  carries only args, stdin, and image_policy, no env. So the
  broker path cannot flip the flag per request; the one-shot is
  the only scoped place it can be set.
- The flag propagates: CU_CODE_EXEC=1 is set on the cu.py session
  command line, and cu.environment() copies the parent env into
  the driver, so the in-process code-exec branch sees it. This
  propagation is verified by the dry run (section 5): a one-shot
  program runs with ok True only when the flag is on; without it
  the envelope returns code execution is disabled.

## 5. Live runs (5x, V12-scored, P9-reviewed)

- (to be filled)

## 6. Verdict

- (to be filled)
