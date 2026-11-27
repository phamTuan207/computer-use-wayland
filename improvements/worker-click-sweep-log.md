# Worker CLICK-SWEEP log: enumerate and triage ALL open computer-use failure modes
# Owner order 01:20 22/11 (scope widened from the one G30 click error to every
# computer-use failure). Read only. No code changes. No laptop driving. No ydotool.
# All times wall-clock Asia/Ho_Chi_Minh + elapsed from task start 01:21:35.
# No em/en dashes anywhere in this file.

## Step log

### 01:21:35 task start (elapsed 0m)
- Spawned as CLICK-SWEEP. Brief: read LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md (768 lines),
  docs/zen-error-fix-todolist-20261121.md (open items), recent worker logs on
  todolist-push (F1/F2/F3b/F1a/F2b/CL1-MSG, commits 334cf69 and later). For each
  failure mode record error id, what fails, root-cause status (proven with
  file/line, hypothesis, or open), what it needs (code fix, procedure fix, or
  live probe), rank by impact on real tasks. A pass on exercises does not count
  for real tasks (per G30).
- Repo: ~/workspace/computer-use-wayland, branch todolist-push, HEAD 682d061.
  Only my file, explicit pathspec, verify via ls-remote.

### 01:21-01:22 read LOI file (elapsed 0-1m)
- Read ~/workspace/cf26-upload/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md in full
  (768 lines, 3 reads). Sections covered: A1-A9, B1-B14, C1-C8, D1-D5, E1-E3,
  F, G1-G30 (note: G25/G26 do not exist in the file, numbering jumps G24 to
  G27), H1-H3, I1-I46, J1-J24.
- Key new facts: G30 (3 batches ok, message never in thread; 50px offset
  reading; owner-mouse suspicion refuted 01:16, owner not home); G28 (screen
  observation typing refusal, cu.py:1475); G29 (Zen urlbar click no focus,
  HYPOTHESIS per redteam A7, not confirmed); J3/J22 (Marionette wedge, Arm E
  reproduces, restart only fix); J21 (workspace-1 click opened Omarchy menu,
  F3 attribution); J23 (workspace switch by command, listed unsolved).

### 01:22 read todolist (elapsed 1m)
- Read docs/zen-error-fix-todolist-20261121.md in full (215 lines).
- Open items: 2.1.7 (I7 video, unmeasurable), 2.2.3 (hyprglass test, option C
  chosen 18:24, Y6c/d/e done, Y6r AMEND A1-A10), 3.4.1 (E1, closed single-arm,
  parked), 4.7-4.28 (4.7-4.12 in progress or done via F3/F1a/F2b/ZT-B; 4.13-4.28
  open; 4.26 PR #1 conflict now resolved by merge d322cd7 per MEMORY).
- Ticked done and relevant: 2.1.1-2.1.6, 2.1.8-2.1.11 (DOM rects 100% vs vision
  58.6%), 2.2.1/2.2.2/2.2.4/2.2.5/2.2.6 (flicker sub-items except 2.2.3), 2.3.x,
  2.4.x, 2.5.x, 2.6.x, 2.7.x, 2.8.x, 3.1.x, 3.2.x, 3.3.x, 3.4.2, 4.1-4.6, 5.x.

### 01:22 git log since 334cf69 (elapsed 1m)
- git log 334cf69..HEAD: HEAD is 682d061 (cl1msg2 ground-truth probe). Commits
  since 334cf69 include F2b (115ae4d, c41aac2, 80929e5), F1a (9bd153b, 9165881,
  bc274ea, 7e4afe7), F3b (7cde3d2, 05d7701, 0b88ed3, 4ae26ea), ZT-B (9fb5a74
  ZT-01 PASS, ade0dc0 ZT-03 FAIL steps 3,5, 1bca71b ZT-02 FAIL step 6),
  PR1-VERIFY (c7cb332, mergeable), Y13g R2 verify FAIL 277/280 (75dff55,
  21f3a7a, a410510, b3736c8), Y13g councils/redteam (1e49436, 31c1126).
- Untracked sibling logs present (not mine, do not touch):
  worker-click-probe-log.md, worker-click-src-log.md, worker-codex-demo-log.md,
  worker-coord-click-log.md, worker-click-codex-cmp-log.md.

### 01:22-01:23 read CL1-MSG + CL1-MSG2 (elapsed 1-2m)
- worker-cl1msg-log.md (334cf69): 3 batches 00:46-00:56, all ok/completed on
  session path, message never in thread, verified by 6+ observes. Batch 1
  silent no-effect. Batch 2 REFUSED (screen-observation fallback, G28).
  Batch 3 atomic, given window observation used, 7/7 ok, still no effect.
  After-capture cursor reading ~50px down-left, hedged +-30-50px by author.
- worker-cl1msg2-log.md (682d061): probe 01:20, P1 (300,960) exact 0px,
  P2 (750,1150) off (-1,-1) 1px rounding, P3 (300,45) REFUSED "screen
  changed", click never happened (session-settle timing, ~200ms after P2
  session ended). VERDICT: no systematic offset, region-origin conversion
  correct, CL1-MSG offset reading was a JPEG cursor-arrow artifact. Retry
  planned (same input point, focus/wait fixes, atomic call) but NOT YET RUN
  at 01:23: log ends "Next: run the send retry now", mtime 01:21:34.

### 01:23 read click-probe, coord-click, codex-demo, click-src, codex-cmp (elapsed 2m)
- worker-click-probe-log.md: uses CL1-MSG2 probe data, does not re-probe,
  waits for its retry verdict. Confirms ws flip 00:52-00:53 was ZT-B itself.
- worker-coord-click-log.md: COORD-CLICK spawned 01:18, scope widened 01:20
  to all failures, spawned CLICK-SWEEP (me) + CLICK-CODEX-CMP at 01:21.
- worker-codex-demo-log.md: Codex CLI verified on laptop (0.169.0, auth
  present), brief prepared, lane busy, will launch only after CL1-MSG2 retry
  verdict. Still prep phase at 01:21.
- worker-click-src-log.md: just started 01:19:11, reading scripts/cu.py
  (2641 lines) + scripts/first_action.py (539 lines). No findings yet.
- worker-click-codex-cmp-log.md: comparison baseline written (Muse 3-batch
  method vs pending Codex demo). Open question restated: click-focus
  consumption, type target, or Enter/send. NOT coordinates.

### 01:23 read F1a + F2b (elapsed 2m)
- worker-f1a-activation-log.md: F1 activation PASS. Attempt 1 failed on glass
  readiness (shaders pending, 8s timeout); fix was login-loader warm-up
  (indicator.Native up, keep alive, close); guard activation ok; session 3b
  click PASS 0px error (3569,1547); pill visible in raw grim 00:04:01, gone
  after stop, returns on restart. New findings: observe hides pill by design
  (capture_clean), act --actions/--observation take FILE PATHS not inline
  JSON, SSH round trip ~30s so proof sessions need long sleeps.
- worker-f2b-live-session-log.md: F2 session-path PASS. Order-to-overlay
  12.262s (<30s PASS; SSH dispatch 11.620s, fresh observe 0.233s, Python
  0.060s, overlay acquire 0.349s). Envelope path session, completed 5/5,
  total 2850.639ms, click 0px. Grim 1 mid-run pill "Computer use active"
  visible; grim 2 Example Domain rendered, no pill (teardown correct).
  F2b-1: act converts coords with observation REGION origin, not monitor_box.
  F2b-2: session path has ONE pill ("Computer use active"), ends with session,
  after-capture cannot evidence it. F2b-3: SSH dispatch is 95% of
  order-to-overlay. Spawn-to-overlay 6m56.4s (think/setup time, H2 gap).

### 01:23 read F3b + ZT-B (elapsed 2m)
- worker-f3b-restart-log.md: slot healed by restart #3 (PID 496121, probe
  PASS 23:51:12). Zombie-as-Example REFUTED (Example tab served DOM text
  23:16:35). Arms A/B/C/D PASS, Arm E (full close3 reproduction) FAILS,
  wedge reproduced 3rd time (~23:42). Restart only fix (3/3). New findings:
  (1) Marionette tab-switch intermittently HANGS (Arm A run 2 at 30s timeout,
  Arm D run 1 at 10s; raw TimeoutError escapes zen_dom.py _wd, which catches
  ZenDomError only); (2) Zen profile is ~/.config/zen/, not ~/.zen; (3) BiDi
  getTree lists only loaded tabs post-restart, sessionstore is ground truth;
  (4) sidebar shows fewer rows than BiDi, order differs, never infer a row
  from a BiDi index. Procedure rule: never Marionette DELETE /window in bulk,
  never Marionette-close about:blank; BiDi close or UI right-click grounded.
- worker-ztb-blind-run-log.md: ZT-00 PASS (with deviations), ZT-01 PASS,
  ZT-02 FAIL step 6 (Escape does not close find bar), ZT-03 FAIL steps 3,5
  (middle-click opens background tab; Ctrl+Tab opens switcher but does not
  switch), ZT-04 in progress. Key findings: Ctrl+N no-op via act (custom
  keybinding gets no synthetic wtype events; built-ins Ctrl+L/Ctrl+W/Alt+Left/
  Ctrl+F work); "+" button (265,1155) no-op; Ctrl+T refused by policy;
  "screen changed" preflight false refusal when cursor sits on click point
  (fix: park cursor at (500,600), never click where cursor sits); offset
  (240,16) validated, image-coordinate estimates unreliable (+-45px);
  activeElement not a reliable focus check; ws flip hazard (clone2-watch cron
  flips ws mid-call, act-now falls back to captured screen observation and
  acts on ws2, ZT-B 00:44:51 clicked into clone1 chat input, harmless);
  window.open via eval is the working-tab opener.

### 01:23 read F1 + F2 root causes (elapsed 2m)
- worker-f1-guardian-fix-log.md: root cause COMPLETE, 4 layers. L0: session
  dies 0.46s "session guardian startup failed". L1 code defect:
  scripts/cursor_theme.py:99-108 (guard_reply + check_guard): json.loads(raw)
  on "unknown request" raises JSONDecodeError; Hyprland answers unknown
  request with exit code 0, so no subprocess exception. L2 runtime: neither
  plugin loaded (hyprbars only). L3 login loader failed at
  manifest_validation (visuals.py _login, profile_sha256 mismatch). L4 THE
  DRIFT (root): laptop repo stale vs setup-published state (optics blur 0.0
  vs manifest pin blur 0.10 vs installed blur 0.15). Fixed live by F1a.
- worker-f2-silence-fix-log.md: root causes R1-R6 proven. R1 no structural
  fast path. R2 guardian startup fails fast with swallowed error (same F1
  chain, cursor_session.py:230 supervise). R3 overlay not tied to any action
  (act requires session, cu.py:2595; direct Pointer path never touches
  overlay). R4 act chain is 3 serial failure points (observe, session, act).
  R5 Marionette slot wedged (F3 owns). R6 re/__init__.py deleted 22:25:39,
  cause SOLVED 22:57 (Y13r2 self-deleting shim A6e, globals().update overwrote
  __file__ before os.remove), VMFIX restored durably (c16dd4e). Rehearsal
  verdict: ZT-00 INCONCLUSIVE as written (urlbar click 2/2 no focus, G29;
  navigation via Ctrl+L worked). F2 fix proven on fallback path only in
  rehearsal; session path proven later by F2b.

### 01:23 status checks (elapsed 2m)
- git status: no new commits after 682d061. CL1-MSG2 retry not yet logged.
  CODEX-DEMO still prep. CLICK-SRC still reading source.
- Y13g R2 verify report: FAIL 277/280, 2 defects both in _check_entry_pyc
  (defect 1: relative-path py_compile self-heal FAIL, A3h; defect 2: symlink
  set outside .pyc rc 2, A7-6b). Commits 75dff55, 21f3a7a, a410510, b3736c8.
- J23 re-check: LOI lists workspace-switch-by-command unsolved, but later
  live evidence closes it: hl.dsp.focus({workspace=2}) proven by CL1-MSG
  00:46 (~1s) and hl.dsp.focus({workspace=1}) proven by ZT-B 00:52:05.
  J23 is CLOSED by later evidence, not open.
- PR #1: MERGED d322cd7 01:06 per MEMORY (todolist 4.26 resolved).

### 01:24 write this log + ranked list (elapsed 3m)
- Writing improvements/worker-click-sweep-log.md now. Next: commit with
  explicit pathspec only, push, verify via ls-remote.

## Ranked fix list (open computer-use failure modes, by impact on REAL tasks)

### Rank 1. G30: clone1 send fails silently, 3 batches ok, zero effect (OPEN, root cause UNKNOWN)
- What fails: 3 act-now batches 00:46-00:56 (batch 1 ok 4/4, batch 3 ok 7/7,
  session path, given window observation used) never put the message into
  clone1's Brave thread on ws2. Verified by 6+ observes, input empty, last
  message still clone1's 22:28 reply.
- Root-cause status: OPEN. Coordinates REFUTED as the cause: CL1-MSG2
  ground-truth probe 01:20, P1 exact 0px, P2 off 1px rounding, region-origin
  conversion correct (worker-cl1msg2-log.md, 682d061). The ~50px down-left
  reading was a JPEG cursor-arrow artifact. Owner-mouse suspicion REFUTED
  (owner confirmed 01:16 not home; ws flip was ZT-B's own rule).
- Remaining hypotheses (untested): (a) click consumed to focus the unfocused
  Brave window, type went nowhere; (b) type target wrong; (c) Enter does not
  send in this chat input. Note batch 1 had no title-bar focus click; batch 3
  had one and still failed, which weakens (a) but does not kill it (focus
  click may have landed on the wrong window, both ws2 windows titled "Muse").
- Needs: LIVE PROBE, not code yet. CL1-MSG2 retry pending (not run at 01:23);
  CODEX-DEMO comparison pending (prep phase); CLICK-SRC source read pending.
  The retry verify observe discriminates: text in input but no message means
  Enter failed; empty input and no message means click/type failed.
- Evidence: improvements/worker-cl1msg-log.md (334cf69),
  improvements/worker-cl1msg2-log.md (682d061), LOI G30.
- Why rank 1: a real task (message a teammate) fails with a success report.
  Silent success is worse than a loud failure. F1a/F2b exercise passes do not
  prove this path (click on a New Tab wallpaper, Example Domain navigation).

### Rank 2. G29: Zen urlbar click lands exact but does not focus, typed keys go nowhere (HYPOTHESIS)
- What fails: click on the Zen urlbar/search box lands exactly (cursorpos
  2629,974, 0px error) but does NOT focus the address input; following type +
  Enter goes nowhere, no navigation. Seen 2/2 (F2 rehearsal run 2 without
  wait, run 4 with 500ms wait after Ctrl+N).
- Root-cause status: HYPOTHESIS, not proven. Redteam A7 downgraded it from
  CONFIRMED: same coords, same sequence (Ctrl+N then click then type then
  Enter), no hover dwell before click, no control click into a known-focusable
  box, no double-click, no click without preceding Ctrl+N, box identified
  from screenshot not DOM/a11y. Cannot yet tell Zen UI behavior from click
  method. Same failure class as rank 1 (click lands, no effect).
- Needs: LIVE PROBE with discriminating cases first (hover 100ms then click;
  click a control text box; click urlbar with no Ctrl+N before it;
  double-click). Record which probe changes the result. Do NOT call it proven
  before then.
- Workaround proven: focus urlbar with Ctrl+L, then type + Enter (F2 run 3,
  F2b). ZT-A must fix scenario ZT-00 step 4 (no mouse click into the address
  box until probes prove clicking works).
- Evidence: LOI G29; improvements/worker-f2-silence-fix-log.md (rehearsal
  verdict, ZT-00 INCONCLUSIVE as written).
- Why rank 2: blocks real navigation-by-mouse, the default way an agent
  drives a browser. Same silent-no-effect class as rank 1.

### Rank 3. H3 / I1-I6: click-miss on real tasks, uncalibrated screen model (ADMITTED, live real-task proof MISSING)
- What fails: aiming View hits Remove (805, 825) and Rejudge (837, 850);
  Discard hit instead of Continue, nearly deleted a working copy; Add to
  Contest not hittable for a long stretch; General info missed several times,
  lost to home page; dragging around hunting the commit button. Owner: the
  biggest error, fix first.
- Root-cause status: ADMITTED by Muse in chat 19:25-19:27 20/11 (I6): coords
  read from the image do not match the real screen, drift to the right,
  screen ratio and spacing differ from assumed, never calibrated for the user's
  machine. No live real-task hit-rate measurement exists (I8: tests only
  measured task done + time, misses buried in retry; no hit-rate metric).
- Partial mitigation (done, todolist 2.1.1-2.1.6, 2.1.8): DOM rects exact,
  vision 58.6% (17/29), pointer <1px on fixtures; monitor 1920x1200 scale 1,
  Zen [2509,914,1863,1176]; ZT-01 validated DOM offset (240,16), image
  estimates unreliable (+-45px). But all of that is fixture/exercise proof.
- Needs: LIVE PROBE on real tasks + hit-rate measurement on real tasks
  (fixtures do not count, per G30). Also a standing hit-rate metric in every
  test run (2.1.8 done for fixtures, not for real tasks).
- Evidence: LOI H3, I1-I8; todolist 2.1.x; improvements/worker-ztb-blind-run-log.md (ZT-01 offset validation).
- Why rank 3: the owner's stated biggest error; every speed optimization is
  worthless while clicks miss and retry. Still open because no real-task
  hit-rate number exists.

### Rank 4. J3 / J22: Marionette slot wedge, browserElement is null (ROOT CAUSE PROVEN, trigger COMBINATION proven, minimal trigger OPEN)
- What fails: new Marionette session fails HTTP 500 "session not created",
  TypeError browserElement is null. Wedged 3 times (22:06, 22:56, ~23:42).
  Blocks every live run (J1 Zen unusable, J4 guardian blocked) until restart.
- Root-cause status: PROVEN from source. driver.sys.mjs #registerBrowser
  line 4616 reads browserElement.namespaceURI with no null-check;
  #registerWindow line 4639 passes TabManager.getBrowserForTab(tab) unchecked
  (returns null when linkedBrowser is null, TabManager.sys.mjs lines 39-41);
  newSession line 2707 registers every tab of every window, one null tab
  kills the whole session. Crawl: Bug 1366988 (2017, same error), Bug 1342723
  (removeTab sets linkedBrowser = null).
- Trigger status: COMBINATION proven. Arms A/B/C/D each PASS alone; Arm E
  (full close3 reproduction: sac + multiple DELETE /window closes + DELETE
  with sac current) FAILS and reproduces the wedge. Refined suspects inside E,
  not yet separated: (1) multiple DELETE /window closes in one session,
  (2) closing about:blank tabs via DELETE /window (never done in A-D),
  (3) the sac surviving the session DELETE. Zombie-as-Example Domain REFUTED
  (Example tab served DOM text 23:16:35). The dead element is invisible to
  BiDi in all 3 wedges.
- Fix status: restart is the ONLY fix (3/3: 22:36, 23:26, 23:44). Non-restart
  tries all failed: right-click Close Tab on Example row (23:23), BiDi
  browsingContext.close on sac (23:43). Ctrl+W on a zombie row never tried
  (no dead row identified, low expected value).
- Needs: (a) PROCEDURE FIX, done and recorded (never Marionette DELETE
  /window in bulk, never Marionette-close about:blank; BiDi close or UI
  right-click with grounded coords only; teardown clean, verify zero
  about:blank via BiDi getTree); (b) CODE FIX for the new sub-finding:
  Marionette tab-switch intermittently HANGS (Arm A run 2 at 30s timeout,
  Arm D run 1 at 10s; raw TimeoutError escapes zen_dom.py _wd, which catches
  ZenDomError only). Fix: target tabs by known handle index instead of
  scanning, catch TimeoutError per call; (c) LIVE PROBE Arm F (one blank
  close via DELETE /window, then probe) to isolate the minimal combination,
  deferred to the cleanup-procedure owner because each wedge costs a restart.
- Evidence: improvements/worker-f3b-restart-log.md; LOI J3, J22; improvements/f3-evidence/arm_*.py + probe_session.py.
- Why rank 4: it kills the whole live lane when it hits, and the only fix
  costs a Zen restart. Procedure containment exists, so it ranks below the
  silent send failures, which have no containment at all.

### Rank 5. G28 + silent observation fallback (CODE DEFECT PROVEN, procedure containment EXISTS, loud-refusal fix OPEN)
- What fails: (a) a batch with typing on a screen observation is refused:
  "screen observations support pointer actions only; use a window or
  accessibility target for typing" (scripts/cu.py:1475). (b) Worse, act-now
  SILENTLY falls back to a captured screen observation when the given window
  observation is stale or mismatched, instead of refusing: CL1-MSG batch 2
  (given window observation 8fef498445d2 valid, ~2 min old, not used;
  observation used was captured screen); ZT-B 00:44:51 (observe failed, OBS
  empty, act-now fell back to captured screen and clicked on ws2 into
  clone1's chat input, harmless only by luck).
- Root-cause status: PROVEN (code line + live envelopes). Fallback trigger
  not yet proven from source (staleness suspected; batch 1's ~1.75 min old
  observation WAS accepted).
- Needs: (a) PROCEDURE FIX, done (same SSH call for observe + act-now, like
  F2b; window observation for any batch with typing; ws check first; verify
  OBS non-empty before act-now; never let act-now fall back); (b) CODE FIX,
  open: act-now must refuse loudly instead of silently falling back, or
  auto-capture a window observation of the focused window when the batch has
  typing and the given observation is a screen observation (follow-up named
  in G28, not done); (c) LIVE PROBE for the P3 "screen changed" refusal
  (CL1-MSG2 P3, ~200ms after prior session ended, click never happened):
  likely a session-settle timing artifact, candidate fix is a settle delay
  or one retry.
- Evidence: LOI G28; improvements/worker-cl1msg-log.md (batch 2);
  improvements/worker-ztb-blind-run-log.md (00:44:51 hazard);
  improvements/worker-cl1msg2-log.md (P3).
- Why rank 5: the refusal itself is correct behavior, but the silent
  fallback turned it into a misdirected live click on the wrong workspace.
  Containment exists, so it ranks below ranks 1-4.

### Rank 6. H2: think time / silence before first action (PARTIALLY FIXED, measurement OPEN)
- What fails: near 5 minutes of silence from the order (22:11:30) to the
  first visible click (22:17); the click itself took 0.31s. Owner: fix this
  FIRST and best (22:16:54), fast + continuous + overlay must show.
- Fix status: MECHANISM PROVEN. act-now overlay in 314-349ms; F2b
  order-to-overlay 12.262s PASS (<30s, session path, 5/5 continuous ops).
  F2 root causes R1-R4 proven with file/line (no structural fast path;
  guardian swallowed error; overlay not tied to any action, cu.py:2595;
  3 serial failure points).
- OPEN remainder: spawn-to-overlay 6m56.4s (think/setup time, the H2 gap);
  per-step think time never measured on an agent-driven run. J10: todolist
  2.3.1 ticked but only scripted (think null by design); only a run with
  real agent-driven think closes H2. Todolist 4.18: instrumentation goes into
  Y13/Y14/A1 (gate G-H2), no separate run.
- Needs: INSTRUMENTATION (gap think-time logging into Y13/Y14/A1), not a new
  run. Also SSH dispatch is 95% of order-to-overlay (11.620s of 12.262s);
  a persistent connection would cut it to ~1s (F2b-3), an improvement, not
  a failure fix.
- Evidence: LOI H2, J5, J10; improvements/worker-f2-silence-fix-log.md;
  improvements/worker-f2b-live-session-log.md; todolist 4.18.
- Why rank 6: the mechanism is proven fast; what remains is unmeasured think
  time, which matters but no longer blocks a visible first action.

### Rank 7. H1 / I9-I11: overlay flicker ~10Hz when Muse drives directly (PARTIALLY FIXED, 20/11 trigger UNIDENTIFIED)
- What fails: pill "Computer use active" flickered continuously, about 10
  times a second by owner estimate, while Muse drove directly 18:53-19:02
  20/11; Codex driving looked normal. Owner ordered computer-use off at
  19:13 because it hurt the user's eyes. Overlay also vanished entirely once (I12,
  15:28, session dropped without the worker noticing).
- Fix status: PARTIAL. Indicator proven NOT to repaint at idle (0 idle paints
  in 122 one-second windows, 32/32 frames pixel-identical, 60s idle 0 events,
  Worker G E2 live). No in-repo 10Hz driver exists (redteam worker4). The
  ~10Hz rate was never measured, only estimated. Most likely remaining cause
  is a compositor/plugin repaint loop triggered by an animated backdrop (H-E)
  in LIQUID mode, unmeasured because hyprglass is not loaded now. E1
  per-event logging added to catch any recurrence. I12 fixed by daemon
  respawn (2.2.4, unit tests pass, live respawn proof still owed).
- Needs: LIVE PROBE. Todolist 2.2.3 / serial 4: Y6 pill measurement retry,
  option C chosen 18:24 (nested Hyprland, isolated). Y6c no verdict, Y6d
  launcher v3 + C2 all PASS, Y6e rebuild .so 34MB + nested load test PASS
  21:57, Y6r AMEND A1-A10 (fix paper first, fresh re-review, then retry).
  Gate G-PILL. Pill measurement still unproven.
- Evidence: LOI H1, I9-I12; todolist 2.2.3, 4.13; overlay-flicker-work-log-20261121.md.
- Why rank 7: recurs only in LIQUID mode with an animated backdrop, and the
  idle case is proven clean. Real but narrower than ranks 1-6.

### Rank 8. ZT blind-test live failures, ordinary-user scenarios (OPEN, new, ZT-04 in progress)
- 8a. Ctrl+N is a NO-OP via act in this Zen (3 attempts, count stayed 18).
  Custom keybindings do not receive synthetic (wtype) events; built-ins work
  (Ctrl+L, Ctrl+W, Alt+Left, Ctrl+F). Ctrl+T is refused by session policy
  (opens a new window in Zen). The "+" new-tab button (265,1155) is also a
  no-op. No working UI new-tab path found yet. Workaround: window.open via
  eval (used by ZT-B for every working tab). Needs: CODE or PROCEDURE fix
  (record Zen keybinds into the machine-specific layer, owner-deferred low;
  fix scenario files ZT-05/09/10 which use Ctrl+T for new tab).
- 8b. ZT-02 step 6 FAIL: Escape does not close the find bar (focus is on the
  page match, not the find input, so Escape goes to page content). Needs a
  probe (focus find input first, or click the X). Scenario as written fails.
- 8c. ZT-03 step 5 FAIL: Ctrl+Tab opens the tab-switcher overlay but does
  not switch (selection stays, title stays HCMC after Escape dismisses it).
- 8d. ZT-03 step 3 FAIL as written: middle-click OPENS a new tab (mechanism
  works, count +1) but in the BACKGROUND (Firefox default), active tab stays
  HCMC. Scenario expectation wrong, not a mechanism failure. Scenario fix only.
- 8e. "screen changed" preflight false refusal when the cursor sits on the
  click point (proven by experiment; fix proven: park cursor at (500,600) at
  batch end, never click where the cursor sits). Procedure fix exists; code
  fix candidate: preflight patch comparison should exclude the cursor or move
  the cursor first.
- Evidence: improvements/worker-ztb-blind-run-log.md (ZT-00 PASS, ZT-01 PASS,
  ZT-02 FAIL step 6, ZT-03 FAIL steps 3,5; commits 9fb5a74, 1bca71b, ade0dc0).
- Why rank 8: real ordinary-user operations fail, but workarounds exist for
  the blocking ones (window.open, Ctrl+L) and ZT-04 is still running.

### Rank 9. Y13g round-2 verify FAIL 277/280: 2 defects in _check_entry_pyc (OPEN, verification-found)
- What fails: (defect 1) relative-path `python3 -m py_compile run_codex_y5.py`
  self-heal FAIL (A3h); (defect 2) symlink set: outside .pyc rc 2 with the
  file intact (A7-6b). Both in _check_entry_pyc, not harness artifacts.
- Root-cause status: PROVEN as defects by verification (3 failing checks from
  2 root causes, report lines 19-36, 177-211). Fix not yet landed; Y13g R2
  council/redteam AMEND in progress (commits 1e49436, 31c1126).
- Needs: CODE FIX in _check_entry_pyc, then re-verify.
- Evidence: improvements/worker-y13g-r2-verify-report.md;
  improvements/worker-y13g-r2-verify-log.md; commits 75dff55, 21f3a7a, a410510.
- Why rank 9: verification-found defects in the code-exec driver, not yet
  failures on a live real task. They matter because the driver is what
  computer-use runs, but they rank below live failures.

### Rank 10. G10 / G11: pill optics, blur + interior refraction (PARTIALLY FIXED, deploy + owner taste OPEN)
- What fails: pill flat in the middle (G10, bend only at rim, must bend like
  a cylindrical bottle, seamless top priority); pill nearly transparent, blur
  and refraction almost none, bend only at rim (G11, interior must carry
  refraction too, lighter than the rim but present).
- Fix status: copy-exactly direction set (Kyant0 FluidGlass, shayxo, Haze,
  MacShell, only less blur); candidate 2 (cylindrical bottle) is the temp
  default, candidate 1 kept. Blur 0.0 to 0.15 code DONE (Worker E, todolist
  4.1). Deploy PENDING reboot (installed binary on the user's machine does not have
  it yet; relay was off, sync-installed reported broker_unavailable).
- Needs: DEPLOY after reboot + live verify, then owner taste-judges (the user is the
  judge; send candidate photos). Interior refraction still to verify after
  deploy.
- Evidence: LOI G10, G11; todolist 4.1, 4.5; docs/pending-user-decisions.md.
- Why rank 10: cosmetic/optics, owner-gated, does not block any task from
  completing.

### Rank 11. 2.1.7 / I7: owner video proving bad button-finding (UNMEASURABLE, owner-gated)
- What fails: owner video 19:04 20/11 shows Muse finding buttons very badly.
  No file of it exists in the workspace, laptop, or media library (only
  hieu-tutorial.mp4 and IMG_6089.mp4 12:04 20/11, a phone-camera video 7 hours
  earlier). The video lives only in E2EE Messenger chat, which the connector
  cannot read as media.
- Needs: OWNER to resend the original video file. The measurable part (hit
  rate) is already done at 2.1.8 (vision 58.6%, DOM 100%) and folded into
  rank 3.
- Evidence: todolist 2.1.7 (Worker X re-check 17:52 21/11).
- Why rank 11: blocked on the owner, and its measurable content is already
  covered by rank 3.

### Rank 12. Remaining open todolist items (PARKED or GATED, not live failures)
- 4.13 Y6 pill retry: covered by rank 7, serial 4, gate G-PILL.
- 4.14 Y13/Y14 live runs: serial 5-6, gated on G-RESTORE, G-SINGLE-LIVE,
  G-HIDDEN, G-H2. Y13 after Y13r2 clear + H3 direction + slot healed; Y14
  after Y13, Y14b re-stage from 1d23532 + H2 regex clear.
- 4.15 A1 pilot resume: serial 7, only after the 3 clone1 blockers are fixed
  + preconditions (hand-named 12 run-ids, broker SOLO, relay verified,
  Layer-2 probes, checker cross-check). Chromium via CDP, not Zen.
- 4.17 Hidden-body decision experiment + Y4d/Y7 follow-up: serial 8. 0
  occurrences in Y4d (20 tests) and Y9b (10 tests live); Y4b design
  (htmlClass + rAF tick count on the SAME hidden tab at the SAME minute)
  not yet run. Gate G-HIDDEN already pulled forward into serial 5-6.
- 4.19 Y1b snippets: serial 10, gate G-Y1B absolute. Phase A BLOCK still
  stands (12-item checklist, unmerged). Probes 10b/10f + 1e/4a must be
  rewritten (they would PASS both the vulnerable and fixed builds).
  Codex watch PID 184702 unconfirmed since ~19:00.
- 4.20 Scrub email + real name from history: serial 11, gate G-SCRUB. Email
  clean from main (1c7d252); real name 71 lines / 45 files remain. Only in a
  truly quiet window (all pushes up, PR #1 done, no live run, all agents told
  to re-clone); if none exists, wait.
- 4.21 Final test (independent Codeforces contest, 5 problems via Polygon):
  LAST, only after everything else.
- 4.23 Clone1 missing report (J12): lane P-B. docs/clone1-batch23-verification-20261121.md
  does not exist; Firefox re-run results Y10 t05/t09/t10 not uploaded.
- 4.24 Batch-3 checker follow-up (J14): lane P-A. Y12 H1-H4 + Y15 follow-up
  (R1/R2/R3b fix sketch, R5, W1 probe, E5 wart).
- 4.25 Keyboard/mouse freeze 17:59 (J15): onset 17:59:13, self-recovered
  18:00:08; Y4b proved y4c did not cause it (navigation 17:59:27/33 after
  onset). Low, only redo if it recurs.
- 4.27 Commit + push diffs immediately (M4/J19, lane P-H, rule D3): ongoing
  discipline, not a failure mode.
- J16 clone2 watchdog 10-min task (19:09): no log ever written
  (docs/clone2-watchdog-log.md missing). Close or re-assign with the next
  batch. Minor.
- 3.4.1 E1 deliberation-vs-execution experiment: CLOSED single-arm (Y8b: A
  BLOCKED judge 7275171, B PASS single-arm 522s, no comparative verdict).
  Fresh comparison PARKED (needs new design + new people + pre-registration).
  If ever scheduled, runs before the final test.
- Evidence: docs/zen-error-fix-todolist-20261121.md (4.13-4.28); LOI J8-J20.

## Closed in this sweep window (for the record, not ranked)
- J1/J2 Zen frozen + workspace errors (owner-reported 22:25): resolved by F3
  restart, slot healed, 14 real tabs, session restore verified.
- J4 session guardian startup failed: root cause proven 4 layers (F1),
  fixed live by F1a (activation PASS, 5-step proof all PASS).
- J5 5-min silence: fixed by F2/F2b (order-to-overlay 12.262s).
- J7 re/__init__.py deleted: VMFIX restored durably (c16dd4e), root cause
  known (Y13r2 self-deleting shim A6e).
- J21 workspace-1 click opened Omarchy menu: attribution found (F3, click
  22:43:15 at (15,30) is the app-launcher button, not workspace 1; second
  menu open 22:45:38 Logo+1). Owner rule: menu + workspace by COMMAND only
  (hl.dsp), never click bar buttons. CLI first, mouse last.
- J23 workspace switch by command: CLOSED by later live evidence
  (hl.dsp.focus({workspace=2}) proven CL1-MSG 00:46; {workspace=1} proven
  ZT-B 00:52:05), despite LOI J23 listing it unsolved.
- 4.26 PR #1 conflict: RESOLVED, merged d322cd7 01:06.
- G1 stale-code relay, G2 geometry 901x1176, G3 leases, G4 Lua dispatch
  (hl.dsp object form), G5 imv-wayland, G6 SSH ~30s death (detached + short
  polls), G7 ssh-laptop.sh, G8 agy non-interactive, G9 VM Chromium proxy,
  G20 Google sign-in chooser rule, G24 JSONL trailing newline, G27 reply in
  group at once: all ticked / rule-recorded.
- C1-C8, B1-B14, D1-D5, A1-A9, I41-I43 (observation 90s to 120s, driver PNG
  bug): ticked done. I-series fabrication/reporting/supervision failures:
  mostly closed via standing rules in MEMORY.md; residuals are measurement
  (hit rate on real tasks, rank 3; think time, rank 6) and the live G30
  proof (rank 1).
- J24 sac-tab leak: procedure fix recorded (teardown clean, verify zero
  about:blank via BiDi getTree; verify runs must not mint a sac tab).

## Pending parallel work that may close rank 1 (status at 01:23)
- CL1-MSG2 send retry: planned, not yet run. Its verify observe is the
  discriminator (text in input = Enter failed; empty input = click/type
  failed).
- CODEX-DEMO: prep phase only (Codex CLI verified, brief ready, lane busy).
  Demo result not yet landed.
- CLICK-SRC: just started reading source (cu.py 2641 lines,
  first_action.py 539 lines). No findings yet.
- CLICK-PROBE: polling CL1-MSG2, no screen touch.
- ZT-B: in ZT-04, verdicts so far ZT-00 PASS, ZT-01 PASS, ZT-02 FAIL step 6,
  ZT-03 FAIL steps 3,5.

## Method note
- Every item above is grounded in a file read this session (LOI file,
  todolist, or a named worker log with commit hash). No item is inferred from
  memory alone. Where the sources disagree (LOI J23 vs later live evidence),
  the later live evidence wins and the disagreement is noted.
- Rank is by impact on REAL tasks. Exercise passes (F1a click on a New Tab
  wallpaper, F2b Example Domain navigation, ZT fixture runs, DOM 100% on
  fixtures) prove mechanism only and do not move an item down the list.
