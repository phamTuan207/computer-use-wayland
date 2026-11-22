# Worker C4-S2-FLIP log: S2 one-class flip (CU_CODE_EXEC=1) for clone chat sends

Owner: the owner. Coordinator: COORD-CLICK-4. Step 6 of the FINAL
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
- 09:50 +07, T+29m: wiring committed and pushed, 350934a
  (ls-remote confirms). Laptop sync begins: 3 local files
  preserved to /tmp/s2-flip-laptop-local-20261122/ (sha256 in
  section 3.1); lease in /tmp rejected (unsafe_lease_directory),
  lease moved to ~/.cache/agent-computer-use/; envelope needs
  umask 077 (unsafe_file at 0644). Trivial broker task moves
  the relay failed to finished (state finished, explicit_finish).
  An exec service restart hit mid-chain; the follow-up status
  call confirmed the chain had completed.
- 09:51 +07, T+30m: laptop checkout switched to todolist-push,
  HEAD 350934a. First sync attempt FAILS on the stale
  native/indicator (555c7de0 vs ledger bf29c610); installed
  tree untouched, relay not restarted. Root cause pinned by
  staging-evidence.json (fresh build bf29c610, deterministic).
- 09:57 +07, T+36m: natives rebuilt in the checkout
  (scripts/build.py, /tmp/s2-build.log); checkout indicator
  now bf29c610. Second sync SUCCEEDS 09:59 +07: release
  ledger 20261122-095940-475319-350934a4bf, --check exit 0
  (643 managed files), relay restarted to PID 983809, loaded
  hash matches the source, started_git_head 350934a.
- 10:00 +07, T+39m: Chromium observe re-verified on the new
  relay (tabs 1, observe 70 elements, not truncated, session
  finished clean). Brave SIGTERM (PID 940441, exit about 10s);
  first relaunch fails (no Wayland display in the SSH env);
  donor env from zen-bin fixes it; second relaunch 10:02 +07,
  PID 987006, [::1]:9223 serves the clone1 tab
  06074E282C000A95EF89CC9EBB8F9713, login intact. Stripe iframe
  tabs force the harness filter to url.startswith
  ('https://muse.ai/').
- 10:05 +07, T+44m: dry run 0, FIRST attempt: both sends
  failed-unverified. The programs ran fine (ok True, completed
  3, CB-1 input_sent and target_received True); only the V12
  helper failed: s2-v12.mjs JSON.parsed argv[4], but the remote
  shell strips the JSON quotes, so node got the bare message
  and JSON.parse threw. Fix: the script takes argv[4] as a
  plain string; the harness passes it with shlex.quote. Also
  added a setup phase bucket (seed + lease-cleanup spans) so
  the residual stays small.
- 10:08 +07, T+47m: dry run 0, SECOND attempt: PASS, both
  browsers sent. Wall 15866.4ms, mux 775.9ms. CB-1 all three
  True both browsers (completed 3). V12 found True, role user,
  side user, attempts 1, elapsed 2-3ms. Phase split: ssh
  13129.0, broker 753.4, observe 771.7, act 192.0, verify
  337.7, setup 680.1, residual 2.4ms. P9 captures ok True
  (1.2s each). Transport dominates the dry-run wall (13.1s of
  15.9s); the live runs add the tabs lookups (+4 calls) and
  drop the seeding (-2 calls), so a live wall near 16-19s is
  expected if the live page behaves like the scratch page.
- 10:11 +07, T+50m: live run 1. Wall 33655.6ms. Brave SENT
  (program 72ms, V12 attempt 1, items 41). Chromium FAILED:
  dom_act completed 0 in 5003ms, V12 40 attempts not found.
  P9 reviewed both: Brave bubble visible, composer empty;
  Chromium no bubble, composer empty. DOM and render agree
  both sides. Diagnosis started (section 5, run 1).
- 10:16 +07, T+55m: live run 2. Wall 33953.2ms. Same pattern.
  The error print names it: "CDP timeout:
  Input.dispatchMouseEvent". Isolated reproduction
  (/tmp/s2-diag2.mjs): Runtime.evaluate 1-3ms, scrollIntoView
  a no-op (rect top stays 1091), bare mouseMoved times out at
  5000ms. The Input domain is stuck on the Chromium tab; the
  renderer is fine. Leading explanation: Chromium sits on
  workspace 2 while workspace 1 is active (hyprctl confirms).
  I did not switch workspaces to test it (would change the
  user's screen and the measurement conditions). Program stays
  unchanged for runs 3-5.
- 10:21 +07, T+60m: live run 3. Wall 33061.9ms. Same pattern,
  third identical Chromium failure. P9 reviewed both.
- 10:26 +07, T+65m: live run 4. Wall 33121.8ms. Same pattern,
  fourth identical Chromium failure. P9 reviewed both.
- 10:31 +07, T+70m: live run 5. Wall 33166.9ms. Same pattern,
  fifth identical Chromium failure. P9 reviewed both. All 5
  runs complete and scored.
- 10:34 +07, T+73m: Brave rolled back to no-flag per the P3
  plan (SIGTERM PID 987006, relaunch without the flag, new PID
  1003210, [::1]:9223 closed, Muse window back per hyprctl).
  Machine returned to as-found state. Median wall 33166.9ms,
  postcondition pass rate 50% (5/10 sends, 0/5 runs complete).
  Verdict written (section 6): do not expand.

## 3. Laptop sync (step 8a pulled forward)

### 3.1 Before

- Laptop HEAD before: 56f5af4e521e1c20b26b56dc31d662e34f1c2668
  ("Record H6 prefetch results"), DETACHED HEAD. 56f5af4 is NOT an
  ancestor of origin/todolist-push (ANCESTOR-NO), so a plain
  fast-forward is impossible; the sync moves the checkout by branch
  switch. The old HEAD stays recoverable via reflog.
- Local modifications, all preserved verbatim to
  /tmp/s2-flip-laptop-local-20261122/ on the laptop (sha256 below)
  before any checkout change:
  - improvements/live-test-log.md (df061165c54ee2c7c6290db442cdced240f950b9a478781e11819227b792dbf0)
  - native/hyprglass-local-optics.lua (9a15163491b543dde09c8388a8faf01f9b491c831647320ce2949d5737d8993c)
  - scripts/cu.py (a6b4d7a86a70494e3d0d263df9c038cf1602a96c136eb8f16c5ffe395f68ca2c)
  The cu.py change (OBSERVATION_MAX_AGE 90 to 120) is ALREADY
  upstream on todolist-push, so restoring it loses nothing. The
  live-test-log.md local copy (4854 lines) is NOT in the
  todolist-push tree (4233 lines upstream); the preserved copy is
  the only record of the Nov 19 watchdog entries.
- No untracked-file collisions with the todolist-push tree.
  Existing stashes on the laptop untouched.
- Relay before: PID 1821, 18h uptime, state failed, driver failed,
  guardian clean, broker_generation ee8e59d3, loaded_code_sha256
  84f65d16, started_git_head 56f5af4, owner probe-s1.
  No task active. session_remote.py changed 5 lines between
  56f5af4 and todolist-push, so the sync wants a relay restart.
- Codex live-confirm (PID 945044) finished 09:29 +07, commit
  b57f499 on branch live-confirm-codex. No Codex process remains.

### 3.2 Lease and envelope file rules (found by failing first)

- The broker rejects a lease in /tmp: unsafe_lease_directory
  (/tmp is root-owned, the lease directory must be owned by
  james). The harness and all manual broker calls use
  /home/james/.cache/agent-computer-use/ (james, 0700) for leases.
- The broker request envelope must be a private regular file
  owned by james (mode 0600): a plain heredoc creates 0644 and
  fails unsafe_file. The harness writes the envelope with
  `umask 077` first. The harness also removes a stale per-run
  lease before start (O_EXCL otherwise blocks a re-run).

### 3.3 Trivial broker task (relay failed to finished)

- 09:50 +07: start (owner s2-flip-trivial) plus a status request
  plus finish, all through the new relay path. Result: state
  finished, stop_reason explicit_finish, next_sequence 2, status
  request completed ok True. The relay is now idle, which the
  sync's _relay_idle requires. (One exec service restart hit
  mid-chain; the follow-up status call confirmed the whole
  chain had completed before the restart.)
- Relay state after: state finished, owner s2-flip-trivial,
  driver stopped, guardian clean, recovery none.

### 3.4 Checkout switch

- 09:51 +07: `git checkout --` the 3 preserved files, then
  `git checkout -B todolist-push origin/todolist-push`.
  Laptop HEAD after: 350934a4bfc53a7dc2c287b757f4dc1afae99939
  (the wiring commit, including the --endpoint code). Tree clean
  except pre-existing untracked files (cf26 lessons, latency
  CSVs, live-a2t/live-a4r). Previous HEAD 56f5af4 recorded above.

### 3.5 sync-installed.py, first attempt FAILS, root cause, fix

- 09:51 +07: sync launched detached (log /tmp/s2-sync.log).
  It built the natives, snapshotted, then aborted with:
  "ledger managed digest differs from repository source:
  native/indicator; repo sha256 555c7de0; staged bf29c610".
  The installed tree was NOT changed (publish happens only
  after the check). Relay NOT restarted (still PID 1821).
- Root cause (evidence, not guess): the laptop checkout held a
  STALE generated binary native/indicator (555c7de0, built
  2026-11-19 17:59 from older sources). The sync treats a
  generated file present in the checkout as source and demands
  it match the last published release ledger (bf29c610). The
  sync's own staged fresh build of the same sources produced
  bf29c610 (staging-evidence.json: staged and installed rebuild
  both bf29c610), so the build is deterministic and the checkout
  binary was simply stale. The other three build outputs
  (pointer, modifiers, wtype) already matched everywhere.
  The 2026-11-21 release ledger records the 2026-11-16 hand
  patches as superseded, so no hand-patch is lost by rebuilding;
  native/ sources are unchanged between the installed release
  (b0c17acd3e) and todolist-push HEAD (git diff empty).
- Fix: rebuilt the natives in the checkout from the current
  sources (`python3 scripts/build.py`, log /tmp/s2-build.log).
  After the rebuild the checkout native/indicator is bf29c610,
  matching the ledger. The checkout's native binaries are the
  LIVE ones (scripts/indicator.py resolves the binary from the
  checkout, cu.py checks ROOT/native/pointer and ROOT/native/
  wtype), so deleting the stale binary instead of rebuilding it
  would have broken the next session; rebuilding was the right
  fix. The running indicator process keeps its loaded inode,
  so replacing the file mid-run is safe.

### 3.6 sync-installed.py, second attempt SUCCEEDS

- 09:59 +07: sync re-run detached (log /tmp/s2-sync2.log).
  Output: "Release ledger:
  /home/james/.local/share/agent-computer-use/releases/
  20261122-095940-475319-350934a4bf.json", "Deploy manifest:
  /home/james/.local/share/agent-computer-use/
  deploy-manifest.json", "--check: exit 0 (643 managed files;
  11 preserved-history exceptions)", "Installed sync published
  and verified.", "Computer-use relay restarted; loaded broker
  code hash matches the source."
- Relay after: NEW PID 983809 (was 1821), started Sun
  2026-11-22 09:59:40 +07. Status: broker running, generation
  136fefc43e215fd9b491c857ed98d48f, loaded_code_sha256
  43a492177f2317a26111c44bddf7526f4b079e4d8aa59451417a11020fdd00ea,
  started_git_head 350934a4bfc53a7dc2c287b757f4dc1afae99939,
  state idle, driver idle, guardian idle. This restart is the
  sync's own restart, authorized by the brief ("unless the sync
  requires it").
- Deploy manifest verified (artifacts: indicator bf29c610,
  modifiers f483faab, pointer ba2786a8, wtype 83b8b9b2).

### 3.7 Browser observe re-verification (new relay, new code)

- Chromium (127.0.0.1:9223): broker session s2-verify, tabs
  returns exactly 1 tab (D1374C7C994D3DA72678E20C7FD099A0,
  "Chat - clone2"), observe on that tab returns 70 elements,
  truncated False, composer present. Session finished clean,
  guardian clean. PASS.
- Brave ([::1]:9223): see section 3.8 (relaunch required first).
- Zen: alive (zen-bin PID 496121), Marionette listening on
  127.0.0.1:2828. The cu.py browser observe path is CDP-only
  (no Marionette in cu.py); Zen's path is the fixture bench
  Marionette driver, not this command. Zen is up; no Zen action
  is needed for the clone-chat-send class.

### 3.8 Brave relaunch with --remote-debugging-port=9223

- Brave as found: PID 940441, no debug flag (P3 revert),
  window on workspace 1. SIGTERM 10:00 +07, graceful exit in
  about 10 s, no brave main remains.
- First relaunch FAILED: the SSH session has no Wayland env,
  Brave exited with "Failed to connect to Wayland display".
  Fix: prefix the donor env from a running GUI process
  (zen-bin 496121): WAYLAND_DISPLAY=wayland-1,
  XDG_RUNTIME_DIR=/run/user/1000,
  DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus.
  (The P3 log does not record how its relaunch got the env;
  the donor-env prefix is the explicit fix.)
- Second relaunch 10:02 +07, same as-found flags plus
  --remote-debugging-port=9223, detached, log
  /tmp/s2-brave-debug.log. New main PID 987006, cmdline
  carries the flag, ver 157.1.99.57.
- Verified: [::1]:9223 serves exactly 1 tab,
  06074E282C000A95EF89CC9EBB8F9713, "(2) Chat - clone1",
  https://muse.ai/?__pwa=1. Login intact (the thread is
  loaded, 2 unread). Chromium 127.0.0.1:9223 untouched
  (4 tabs: clone2 plus 3 Stripe iframe tabs).
- Tab-selection fix (found during verification): the Chromium
  /json/list Stripe iframe tabs carry "muse.ai" in their
  fragment (encoded referrer), so a substring filter matches
  4 tabs, not 1. The harness now filters by
  url.startswith('https://muse.ai/'). The broker tabs command
  already returns only the 1 page tab, but the harness filter
  is now correct on its own.
- The flag stays on for the 5 runs; the P3 rollback (relaunch
  without the flag) runs after the runs, per the P3 plan.

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

### Run 1 (10:11 +07, T+50m)

- Wall 33655.6ms, mux 790.5ms. Model calls 0.
- Brave: SENT. Routing dom-chromium (56 elements, not truncated).
  Program ok True, completed 3, 72ms. V12 found True, attempt 1,
  items 41, role user, side user. CB-1 all three True.
  P9 reviewed: the blue user bubble
  "S2-FLIP-R1-BRAVE-IGNORE-TEST" is visible in the render, the
  composer is empty. DOM and render agree. P9 PASS.
- Chromium: FAILED-UNVERIFIED. Routing dom-chromium (70 elements,
  not truncated). Program ok False, "assert failed: dom_act
  failed", dom_act completed 0 in 5003ms. CB-1 all three False.
  V12 found False after 40 attempts (10051ms), items 40. P9
  reviewed: the composer is empty, no sent bubble, the last
  message is the assistant's confirmation about clone1. DOM and
  render agree (the send genuinely did not happen). P9 confirms
  the failure is real, not a V12 false negative.
- Diagnosis: the dom_act execution time is 5003ms, which is
  exactly the 5000ms CDP call timeout in cdp.mjs (line 60).
  One CDP call during the fill never answered within 5s. A
  read-only diagnostic right after (node /tmp/s2-diag.mjs)
  shows the composer is fine: exactly one TEXTAREA named
  Message, rect (452, 1091, 622x24), visible, not disabled, not
  readOnly, value empty, and the click center hits the TEXTAREA
  itself. The grounding is correct and the element is
  clickable. The V12 right after the failure was fast (each
  evaluate 2-3ms), so the stall cleared. Most likely cause: a
  transient 5s main-thread stall on the clone2 tab, which is
  the ACTIVE work thread (clone2 is running batch 9), while
  the clone1 tab is quiet (clone1 is stalled, out of tokens).
  The failure is transient until proven otherwise; run 2 will
  show whether it recurs.
- Logging-only program change after run 1: the program print
  now includes res.get("error"), so the next failure names the
  failing CDP sub-step. The three actions (fill, key Enter,
  trailing assert) and all their parameters are unchanged; the
  mechanism is identical, only the failure diagnostic is
  richer. Wiring tests still 9/9.

### Run 2 (10:16 +07, T+55m)

- Wall 33953.2ms, mux 777.8ms. Model calls 0.
- Brave: SENT. Routing dom-chromium (54 elements, not truncated).
  Program ok True, completed 3, 51ms. V12 found True, attempt 1,
  items 45, role user, side user. CB-1 all three True.
  P9 reviewed: both the R1 and R2 test bubbles are visible, plus
  a clone1 assistant reply between them (clone1 is responding to
  the test messages; they are marked IGNORE-TEST). Composer
  empty. DOM and render agree. P9 PASS.
- Chromium: FAILED-UNVERIFIED, same sub-step as run 1. Program
  ok False, dom_act completed 0 in 5002ms, log now names it:
  "error CDP timeout: Input.dispatchMouseEvent". CB-1 all three
  False. V12 found False after 40 attempts (10054ms), items 40.
  P9 reviewed: no R2 bubble, composer empty, identical to run 1.
  DOM and render agree. P9 confirms the failure is real.
- Diagnosis, isolated reproduction: a standalone node script
  (/tmp/s2-diag2.mjs) on the live Chromium tab shows baseline
  Runtime.evaluate 3ms, scrollIntoView 1ms (the textarea does
  NOT move, rect top stays 1091, so scrollIntoView is a no-op
  and is NOT the trigger), post-scroll evaluates 0-1ms, and a
  bare Input.dispatchMouseEvent mouseMoved TIMES OUT at 5000ms.
  The renderer answers Runtime.evaluate in 1ms but will not
  answer Input.dispatchMouseEvent at all. The Input domain
  specifically is stuck on this tab; it is not a main-thread
  stall and not the scroll.
- Leading explanation (not proven): the Chromium window sits
  on workspace 2 while workspace 1 is active (hyprctl confirms
  active workspace 1, Brave on ws1 is the last window). The
  occluded window's input pipeline may not dispatch synthetic
  mouse events. Brave on the active workspace works 2/2;
  Chromium on the inactive workspace fails 2/2 at the same
  sub-step. I did NOT switch workspaces to test this: it would
  change the user's screen and the measurement conditions
  mid-run. The finding stands as measured under the as-found
  conditions.
- Decision: the program stays unchanged for runs 3-5. The
  Chromium failure is data, not a reason to redesign the
  program mid-measurement. Runs 3-5 run under the same
  conditions; if the pattern holds 5/5, the class does not
  flip and the verdict follows from that.

### Run 3 (10:21 +07, T+60m)

- Wall 33061.9ms, mux 789.9ms. Model calls 0.
- Brave: SENT. Program ok True, completed 3, 53ms. V12 found
  True, attempt 1, items 47, role user, side user. CB-1 all
  three True. P9 reviewed: the R3 bubble is visible, composer
  empty. DOM and render agree. P9 PASS. (Clone1's own messages
  in the thread discuss runs 1 and 2; it is following the test
  messages.)
- Chromium: FAILED-UNVERIFIED, third identical failure.
  "CDP timeout: Input.dispatchMouseEvent", completed 0, 5003ms.
  V12 found False after 40 attempts (10052ms), items 40. P9
  reviewed: no R3 bubble, composer empty. DOM and render agree.
  P9 confirms the failure is real.
- Pattern is now 3/3: Brave sends in about 50-70ms of program
  time; Chromium fails at the first mouse event every time.

### Run 4 (10:26 +07, T+65m)

- Wall 33121.8ms, mux 836.1ms. Model calls 0.
- Brave: SENT. Program ok True, completed 3, 48ms. V12 found
  True, attempt 1. CB-1 all three True. P9 reviewed: the R4
  bubble is visible, composer empty. DOM and render agree.
  P9 PASS. (Clone1's messages in the thread now discuss runs
  1-3 and quote the Input diagnosis; it is following the test
  messages.)
- Chromium: FAILED-UNVERIFIED, fourth identical failure.
  "CDP timeout: Input.dispatchMouseEvent", completed 0, 5003ms.
  V12 found False after 40 attempts, items 40. P9 reviewed:
  no R4 bubble, composer empty. DOM and render agree.
- Pattern is now 4/4. One run remains.

### Run 5 (10:31 +07, T+70m)

- Wall 33166.9ms, mux 826.9ms. Model calls 0.
- Brave: SENT. Program ok True, completed 3, 41ms. V12 found
  True, attempt 1. CB-1 all three True. P9 reviewed: the R5
  bubble is visible, composer empty. DOM and render agree.
  P9 PASS. (Clone1's messages summarize runs 1-4 and the
  pattern.)
- Chromium: FAILED-UNVERIFIED, fifth identical failure.
  "CDP timeout: Input.dispatchMouseEvent", completed 0, 5003ms.
  V12 found False after 40 attempts, items 40. P9 reviewed:
  no R5 bubble, composer empty. DOM and render agree.
- Pattern is 5/5. All 5 runs are complete and scored.

### Rollback (P3 plan, after run 5)

- 10:34 +07: SIGTERM to the debug-port Brave main PID 987006,
  graceful exit, [::1]:9223 closed. Relaunch WITHOUT the flag
  (same as-found flags, donor env prefix, log
  /tmp/s2-brave-rollback.log). New main PID 1003210, cmdline
  carries no debug flag. [::1]:9223 stays closed. hyprctl
  confirms the Brave "Muse" window is back (pid 1003210).
  The CDP exposure is closed; the machine is back to its
  as-found state. Chromium (clone2, PID 8059) was never
  restarted or touched. Relay stays on 350934a (PID 983809).

## 6. Verdict

### 5-run table (wall ms, end to end including transport)

| run | wall | Brave | Chromium | Brave program | Chromium program |
|-----|------|-------|----------|---------------|------------------|
| 1 | 33655.6 | sent | failed-unverified | 163.7ms, completed 3 | 5103.7ms, completed 0, CDP timeout Input.dispatchMouseEvent |
| 2 | 33953.2 | sent | failed-unverified | 154.0ms, completed 3 | 5106.3ms, completed 0, CDP timeout Input.dispatchMouseEvent |
| 3 | 33061.9 | sent | failed-unverified | 150.1ms, completed 3 | 5104.5ms, completed 0, CDP timeout Input.dispatchMouseEvent |
| 4 | 33121.8 | sent | failed-unverified | 134.8ms, completed 3 | 5105.8ms, completed 0, CDP timeout Input.dispatchMouseEvent |
| 5 | 33166.9 | sent | failed-unverified | 133.0ms, completed 3 | 5102.6ms, completed 0, CDP timeout Input.dispatchMouseEvent |

- Median wall: 33166.9ms (33.2s). Sorted walls: 33061.9,
  33121.8, 33166.9, 33655.6, 33953.2.
- Model calls per run: 0 (all 5 runs). The machine loop makes
  no model call and no vision call; the program is fixed.
- Per-phase split, median across runs (ms): ssh transport
  about 15000, broker about 700, observe about 1500, act about
  5250 (dominated by the Chromium 5s timeout), verify about
  10400 (dominated by the Chromium 10s V12 poll), setup about
  150, residual 2.3-2.5 (tiny, the split accounts for the wall).
  Median mux baseline 790.5ms per SSH call.
- Brave half, median: program elapsed 150.1ms (dom_act 41-72ms),
  per-browser wall 2698.9ms. V12 found attempt 1 in all 5 runs.
  perception_routing dom-chromium in all 10 browser decisions
  (5 runs x 2 browsers), zero fell through to screenshot.
- Chromium half, median: program elapsed 5104.5ms (the 5000ms
  CDP timeout, nothing else), V12 11045.1ms (the 10000ms poll,
  40 attempts, never found). 0 of 5 sends verified.

### Postcondition pass rate (CB-1 verified, not envelope ok)

- Per send: 5 of 10 verified (50%). Brave 5/5, Chromium 0/5.
- Per run (both sends verified): 0 of 5 (0%).
- The CB-1 gate is judged by verified, not by envelope ok:
  the Brave envelopes are ok True AND verified; the Chromium
  envelopes are ok False AND unverified. No envelope-ok run
  hides a failed send.

### Plateau: reached or not

- By the letter of the gate: NO. The median wall is 33.2s,
  below the 60s threshold, so the "median stays above 60s"
  condition is not met.
- But the class does NOT flip. Zero of 5 runs completed both
  sends, and the postcondition pass rate is 50%. A median
  below 60s on runs that fail the class is not a pass: the
  failed runs are fast only because they terminate early (the
  Chromium half costs a 5s timeout plus a 10s V12 poll instead
  of a successful send). The gate's spirit is "the class
  completes faster than 60s"; the class does not complete.
- The bottleneck is the mechanism, not the model: 0 model
  calls, Brave sends in 41-72ms of program time, and the
  Chromium failure is a CDP Input stall that no model call
  would fix. That is exactly the condition the plateau was
  designed to detect ("the mechanism (not the model) is the
  bottleneck").
- So the honest reading is: the flip works for the Brave half
  and is blocked on the Chromium half by a mechanism fault.
  The class as defined does not flip.

### Recommendation: DO NOT EXPAND

- Do not expand the flip to more classes. The clone-chat-send
  class itself is only half flipped (Brave 5/5, Chromium 0/5).
  Expanding now would spread a broken half.
- Next lever, in order:
  1. Prove or kill the visibility hypothesis: focus the
     Chromium window (switch to workspace 2) and re-run the
     isolated mouseMoved diagnostic. If Input answers while
     the window is visible, the fix is a visibility
     precondition in the send path (focus the target window
     before the program runs), not a new mechanism.
  2. If visibility is not the cause, try set_value instead of
     fill for the composer (no mouse events, no Input domain).
     That is a program change, so it needs its own dry run
     and a fresh 5-run measurement, not a mid-measurement
     swap.
  3. If neither works, the Input stall is a mechanism fault
     for the step 9 prototype to solve (a different input
     channel for occluded windows, or a longer CDP timeout
     with a retry that does not count as a new mechanism).
- Keep the Brave half flipped: it is measured green (5/5,
  median program 150ms, per-browser wall 2.7s, V12 attempt 1).
  The Brave half is the proof the S2 mechanism works when the
  Input domain answers.
- The step 9 prototype decision is now informed by a concrete
  mechanism fault (CDP Input.dispatchMouseEvent stalls on the
  occluded Chromium window) rather than by a slow median.
  That fault is the prototype's first target if the visibility
  test kills the cheap fix.

## 6. Verdict

- (to be filled)
