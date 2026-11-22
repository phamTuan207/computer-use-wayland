# W-ZT-B: Zen pointer delegate live proof, run 3 (blind run, NEW)

Owner: Pham Tuan. Coordinator: COORD-CLICK-10. Worker: W-ZT-B.
Repo ~/workspace/computer-use-wayland, branch todolist-push.
No em dash or en dash anywhere in this file. No personal info.
Report goes to COORD-CLICK-10, not directly to Pham Tuan.

## 0. Task receipt and sources read (before any live touch)

- Task received 21:23:07 +07, 22/11/2026. T+0m. Single lane,
  quiet machine, owner away from the machine.
- Sources read before running:
  - improvements/w-zen-delegate-liveproof-prep.md (procedure
    phases 0-7, scratch target
    tests/two_vision_fixture.html?clone=zen, viewport gate P2.4,
    send program phase 4, pass only when dom_act ok True,
    completed 4, error None, post-checks P5.1, retry already-sent
    P5.2, delayed count 1 P5.3, P9 screenshot reviewed by sight
    P5.4, cleanup P6).
  - improvements/w-zenproof2-amend4-log.md (amend 4: second
    baseline just_before, honest handle-stability docstring,
    Q-J1 residual pinned, hypr-first phase-4 pin; next proof is
    a fresh run number with a fresh intent/message, copying the
    fixed run2.py; run 1 must not be re-run as-is).
  - improvements/c5-zenproof-runs/c5-zen-delegate-run2.py (the
    fixed runner to copy; method saved verbatim: Harness.ssh
    over the mux, scp driver transfer in phase 1 with sha
    verify, oneshot session-driver with CU_DOM_BACKEND=zen,
    target by URL substring, identity by URL never by handle).
  - improvements/w-zenproof2-log.md section 6 (run 2 incident:
    the title premise closed the Muse chat tab; the fixed driver
    verifies the new tab was made current, requires count +1,
    and deletes in the open exception handler only when the
    current tab is the fixture tab by URL AND by handle).
  - improvements/coord-click-10-log.md section 0 (coordinator
    pre-checks: pill OFF, holders {}, daemon idle-exited after
    the 21:21 cleanup; first acquire in ZT-B must restart it;
    if the pill does not appear on acquire, STOP).
- Hard rules restated: never close or navigate any tab of Pham
  Tuan; do NOT reopen the Muse chat tab closed in run 2
  (https://muse.ai/thread/750c8dae-58fb-4a65-82ac-753e78d6ce93);
  pill must show on any agent control (gate 4.29); on a 'not
  made current' refusal, STOP at once, no retry open in a loop,
  no DELETE via Marionette, report to the coordinator; if any
  owner tab is closed or navigated wrong, or the pill is not
  visible during control, STOP at once and report; no em dash;
  no ydotool; no personal info on GitHub; log continuously with
  wall-clock Asia/Ho_Chi_Minh plus elapsed; commit with an
  explicit pathspec, never bare commit, never add -A.
- This run is run 3, NEW run number, NEW intent
  c5-zen-delegate-r3, NEW message ZEN-DELEGATE-R3-IGNORE-TEST.
  Run 1 and run 2 were never run as-is in this task.

## 1. Time log (wall-clock Asia/Ho_Chi_Minh, elapsed from 21:23:07 +07)

- 21:23:17 +07, T+0m: VM HEAD ffc94b5, branch todolist-push,
  origin equal. Sources read (section 0).
- 21:24 +07, T+1m: phase 0 gates (section 2). Laptop as-found
  read-only checks: pill holders {}, visible false; active
  window OmaCal 0x56307e5e8200 on ws1 (not Zen); Zen
  0x56307e2771d0 on ws1 showing Calendar; no live
  session-driver; relay idle, owner null; zen-tab.py on laptop
  sha 65cd45dd (stale, run 2 version) vs VM b881019e (amend 4),
  to be overwritten by the phase 1 scp as in run 2; fixture sha
  matches the manifest on both checkouts; geckodriver present
  at /home/james/.local/bin/geckodriver.
- 21:25:22 +07, T+2m: run3.py created by copying run2.py,
  identical copy verified by diff (no output).
- 21:25 to 21:26 +07, T+2m to T+3m: run3.py edits (section 2),
  py_compile OK, diff reviewed, G0b validation OK.
- 21:26:07 +07, T+3m: pill acquire 1 (section 3). Daemon
  spawned, holder S2-flip:181823, visible true.
- 21:26:57 +07, T+4m: pre-run grim 1 reviewed by sight: pill
  VISIBLE top center, label "S2-flip via CDP". First grim
  failed "failed to create display" (no WAYLAND_DISPLAY in the
  SSH shell); retried with the W-PILLVERIFY2 env prefix and
  it worked. Same prefix applied to the run3.py grim calls.
- 21:27:17 +07, T+4m: focus Zen by window address
  (hl.dsp.focus), dispatch ok, activewindow Zen
  0x56307e2771d0. No tab navigated or closed, only focus.
- 21:27:28 +07, T+4m: runner commit cff51d0 pushed,
  ls-remote verified.
- 21:27:33 +07, T+4m: run 3 attempt 1 launched detached,
  PILL_SLEEP_PID=181823.
- 21:27:47 +07, T+5m: attempt 1 finished, wall 13.8s, outcome
  error, phase 1 "could not identify the current tab". No tab
  opened, no input sent. Pill released ok.
- 21:28:43 +07, T+6m: diagnosis list 1: same empty current-tab
  entry, count 18, same URL set.
- 21:29:34 +07, T+6m: direct diagnostic (diag-current-tab.py):
  the current tab IS the Calendar tab, alive, readyState
  complete. The scan entry read is the artifact, not the tab.
- 21:30:25 +07, T+7m: diagnosis list 2: Calendar URL resolves,
  0 empty entries. Changed precondition, retry justified.
- 21:30:43 +07, T+7m: attempt 1 evidence preserved
  (run-3-attempt1.json, sha e8ceaa28...).
- 21:30:50 +07, T+8m: pill acquire 2 (section 5). Daemon
  spawned, holder S2-flip:185033, visible true.
- 21:31:06 +07, T+8m: pre-run grim 2 reviewed by sight: pill
  VISIBLE top center. Active window still Zen.
- 21:31:13 +07, T+8m: run 3 attempt 2 launched detached,
  PILL_SLEEP_PID=185033.
- 21:32:32 +07, T+9m: attempt 2 finished, wall 38.8s, outcome
  error, phase 4 send refused by the dimension closure gate.
  No input sent. Cleanup reported an error but the end state
  verified correct (section 6).
- 21:32:51 +07, T+10m: end-state list: count 18, exact original
  URL set, current is the Calendar tab, no fixture tab.
- 21:33:17 +07, T+10m: final state: pill holders {}, visible
  false; no live session-driver; no runner on the VM.
- 21:33 to 21:36 +07, T+10m to T+13m: evidence copied to the
  repo, log written, STOP per the task (proof FAILS, no
  self-fix) and report to COORD-CLICK-10. No stall over 15
  minutes at any point in this task.

## 2. Phase 0 gates (VM, no live touch) and the run3.py runner

- G0a PASS, 21:24 +07: `python3 -m unittest
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec` returned Ran 177 tests in 12.517s, OK.
- G0b PASS, 21:26 +07: probe program and send program (run 3
  text, message ZEN-DELEGATE-R3-IGNORE-TEST) both pass
  code_exec.validate_program with no exception.
- G0c PASS, 21:24 +07: `sha256sum
  tests/two_vision_fixture.html` on the VM =
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6cbf,
  matching the manifest.
- G0d PASS: fresh intent c5-zen-delegate-r3, fresh message
  ZEN-DELEGATE-R3-IGNORE-TEST for run 3.
- Runner run 3: improvements/c5-zenproof-runs/
  c5-zen-delegate-run3.py, copied from the fixed run 2 runner.
  Diff limited to: run number 3, message/intent R3, workdir
  /tmp/c5-zenproof-3, run-3.json, p9-zen-r3.png, plus the pill
  handling and one grim fix, both required by this task:
  (a) pill_setup takes the sleeper pid from PILL_SLEEP_PID,
  re-verifies the exact holder key is alive and overlay status
  reports visible true before any tab operation, re-checks the
  holder immediately before the phase 4 send, captures a
  during-run grim in phase 5, and releases the holder in
  finally after cleanup; with no env pid it acquires its own
  holder and gates on the same checks; (b) both grim calls
  (P9 and pill-during) carry the XDG_RUNTIME_DIR=/run/user/1000
  WAYLAND_DISPLAY=wayland-1 prefix, because a bare grim over
  SSH fails "failed to create display" with no file (proven
  live 21:26 in this task and in the W-PILLVERIFY2 log; run 2
  never reached phase 5, so its bare grim was never exercised).
  Everything else (transport, phases, programs, gates) is
  byte-identical to run2.py. py_compile OK. 0 em dash, 0 en
  dash in run3.py. Commit cff51d0 pushed and ls-remote
  verified before the run.

## 3. Pill verification (gate 4.29)

- Pill started OFF for this run (holders {}, owner none,
  visible false, daemon dead after the 21:21 idle-exit),
  confirmed by the coordinator pre-checks and by my own
  read-only check at 21:24.
- Acquire 1, 21:26:07 +07: overlay acquire returned daemon
  spawned PID 181825, holder S2-flip:181823 acquired
  21:26:08 +07, label "S2-flip via CDP", owner daemon, visible
  true, PILL_SLEEP_PID=181823.
- Pre-run grim 1, 21:26 +07: /tmp/c5-zenproof-3/pill-pre-r3.png,
  892422 bytes, sha256
  813ed098639fd228076ee4c0825a000dfae260264d59da7b2e21be5a2d54c278,
  reviewed by sight: pill VISIBLE top center, label "S2-flip
  via CDP", green dot. Zen shows Google Calendar week view;
  OmaCal tiled on the right; a "Process crashed:
  WebKitWebProcess" notice (20:04) and a Calendar notification
  dialog are pre-existing, not mine.
- Acquire 2, 21:30:50 +07: daemon spawned PID 185035, holder
  S2-flip:185033 acquired 21:30:50 +07, label "S2-flip via
  CDP", visible true, PILL_SLEEP_PID=185033.
- Pre-run grim 2, 21:31 +07: /tmp/c5-zenproof-3/
  pill-pre-r3-a2.png, 894416 bytes, sha256
  47261f5dd2a83e1aabd4988ef309c60e0a2e77371347d2242ad2169fa3edbb2c,
  reviewed by sight: pill VISIBLE top center, same label. The
  Calendar notification dialog is gone in this shot. Active
  window still Zen.
- During-run pill: the runner re-verified the holder alive and
  status visible true at the start of each attempt (recorded
  in run-3.json under "pill"), and re-checked the holder
  immediately before the phase 4 send in attempt 2. No
  pill-during grim exists because attempt 2 never reached
  phase 5 (it failed in phase 4), and attempt 1 never reached
  phase 2. The pill was released cleanly at the end of each
  attempt (pill_release ok, pid recorded); final status 21:33
  is holders {}, visible false.
- No control ran without a visible pill: every Zen control in
  this task (focus switch, tab lists, open, switch, probe,
  send attempt) ran while the S2-flip holder was up and the
  pill was verified visible.

## 4. Attempt 1: phase 1 abort, transient empty scan read (F1)

- Launched 21:27:33 +07, finished 21:27:47, wall 13.8s,
  outcome error, "could not identify the current tab".
  Phase 1 tab list succeeded (18 tabs) but the entry matching
  the current handle had title '' and url '', so the runner
  set original_url to '' (falsy) and raised. No tab was opened,
  no input was sent, cleanup skipped (nothing opened).
- Diagnosis, all read-only:
  - Second list, 21:28:43 +07: count 18, same URL set, current
    handle 79ea8247 (handles are ephemeral per session), still
    the empty-URL entry. The empty read reproduced twice.
  - Direct diagnostic, 21:29:34 +07
    (improvements/c5-zenproof-runs/diag-current-tab.py, fresh
    ZenSession, no tab switch, only GET /window, /url, /title
    plus one JS evaluate): current handle 471b28b6, url
    endpoint 'https://calendar.google.com/calendar/u/1/r/week',
    title endpoint 'Lich Google - Tuan 16 thang 11, 2026', JS
    document.URL the same Calendar week view, readyState
    complete, 19 inputs. The current tab IS the visible
    Calendar tab, alive and fully loaded. The empty scan entry
    is a list_tabs scan-read artifact for this tab, not a dead
    or crashed tab.
  - Third list, 21:30:25 +07: count 18, Calendar URL present,
    0 empty entries. The read resolved on its own after the
    repeated scans and the direct read (the run 2 log records
    the same effect: the list scan loads unloaded tabs as it
    switches through them).
- Retry justification (run 2 attempt-1 to attempt-2 precedent):
  nothing was sent in attempt 1, so the same fresh R3
  intent/message is reused with no ledger entry; the failing
  read now succeeds, a changed precondition, not a blind
  retry; no code was changed for the retry. Attempt 1 JSON
  preserved as improvements/c5-zenproof-runs/
  run-3-attempt1.json (sha256
  e8ceaa28fbacf170314fe0a23aaf9fff283cb42832026d95f19539c741cb8d79).

## 5. Attempt 2: phases 1-3 PASS, phase 4 refused by the geometry gate (F2)

- Launched 21:31:13 +07, finished 21:32:32, wall 38.8s,
  outcome error, "send program did not complete 4/4".
- Phase 1 PASS: Zen 0x56307e2771d0 on ws1, bounds [2509, 914,
  925, 1176]; tabs_before 18, current Calendar 8de3458a with
  URL https://calendar.google.com/calendar/u/1/r/week;
  liveness live false (ps shows no session-driver, relay idle,
  owner null, guardian idle, recovery none; 10 stale leases
  recorded as evidence only). NOTE: Zen is 925 wide, half of
  run 2's 1863 wide at 19:59. OmaCal (launched ~20:05 by
  another lane) is now tiled beside Zen on ws1 instead of
  floating over it. My focus switch does not resize windows;
  the narrowing predates this run and is recorded, not
  attributed.
- Phase 2 PASS: open ok, new handle
  73ae0c84-0ed0-40c8-bbe5-2545fdcd5ac3, count 18 to 19,
  selected_by explicit-select (POST /window/new did NOT make
  the new tab current; the one explicit select did, exactly
  the amend fix working as designed), URL the fixture,
  H1 'Clone zen thread', ready complete, viewport_ok true,
  metrics innerWidth 677, innerHeight 1160, hasFocus true,
  element_at_point 'msg-input', rect x 20 y 228.87 w 340
  h 36, harvest moz_inner [253, 30], inner [677, 1160],
  outer [925, 1176].
- Phase 3 PASS: switch ok; read-only probe ok (PROBE zen-1
  fixture URL, 1 element, wall 2027.7ms, snapshot title the
  static fixture title as evidence only); pre-checks clean
  (H1 'Clone zen thread', bubble_present false, bubbles [],
  input '', input_events 0).
- Phase 4 FAIL: send_switch ok (handle 9b629a71, fixture URL);
  then dom_act ok False, elapsed 677.055ms, completed null,
  log only the PROBE line. Error verbatim: "dimension closure
  fails: mozInner [274, 66] + inner [677, 1160] exceeds window
  size [925, 1176] (gaps -26, -50); the reported mozInner is
  displaced from the true viewport origin (pixel proof
  a42ef12: true origin (240, 8) on the live narrowed window);
  supply a verified mozInner (independent screenshot/click
  cross-check) to override". The backend refused BEFORE any
  desktop act: no set_value, no focus, no key, no message
  typed, no bubble. The send snapshot URL and count gates
  passed (fixture URL, 1 element), so the failure is purely
  the geometry closure, not a wrong-tab send.
- The mozInner MOVED between the open harvest and the send:
  open harvest [253, 30], send snapshot [274, 66], a shift of
  +21/+36, while the true origin is (240, 8) per the pixel
  proof. On the narrowed 925-wide window the reported origin
  is displaced by (+34, +58) from the true origin, so
  [274, 66] + [677, 1160] = [951, 1226] exceeds the window
  [925, 1176]. Whether the displacement also occurs on a
  full-width Zen window is UNPROVEN: run 2 never reached
  phase 4.
- Phase 5 not reached: no post-checks, no retry check, no
  delayed recount, no P9 (nothing was sent to photograph).

## 6. Cleanup and end state (attempt 2)

- Cleanup reported ok False: "zen-tab close failed rc=1:
  Browsing context has been discarded" (NoSuchWindowError, a
  post-DELETE verification read hitting the discarded
  context). This is the known amend-4 open item (amend4 log
  section 4): cmd_close post-DELETE verification reads can
  still raise after a successful DELETE and mask the close
  success. Consequence is a spurious error, never a wrong
  navigate or DELETE.
- End state verified by an independent fresh list, 21:32:51
  +07: count back to 18, the EXACT original 18-URL set from
  tabs_before, current tab the Calendar tab
  (https://calendar.google.com/calendar/u/1/r/week), the
  original tab, no fixture tab left. The DELETE did succeed;
  only its success report was masked.
- Final state, 21:33:17 +07: pill holders {}, visible false;
  no live session-driver on the laptop; no runner process on
  the VM; laptop run dir holds the amend-4 zen-tab.py, the
  diagnostic script, and both pill grims.
- The Muse chat tab closed in run 2 is still absent (no
  muse.ai URL in any list). It was NOT reopened in this task,
  per the task order.

## 7. Verdict

- FAIL. The Zen pointer delegate live proof did NOT pass: no
  send program completed, no P4/P5 criterion was met, no P9
  of a sent bubble exists. Attempt 1 aborted in phase 1 on a
  transient scan-read artifact (F1); attempt 2 passed phases
  1-3 and was refused in phase 4 by the dimension closure
  gate on the narrowed Zen window (F2).
- Checklist status: G0a PASS (177 OK), G0b PASS (both programs
  validate), G0c PASS (fixture sha), G0d PASS (fresh intent
  and message), P1.1 PASS in attempt 2 (Zen active ws1),
  P1.2 PASS in attempt 2 (list ok, 18 tabs, current Calendar
  identified), P1.3 PASS (resolved geckodriver path exists),
  P1.4 PASS (fixture sha on the laptop), P1.5 PASS (live
  false, relay idle), P2.2 PASS (open ok, count +1, URL and
  H1 verified, viewport_ok true), P2.3 PASS (rect recorded),
  P2.4 PASS (viewport gate true), P3.1 PASS (switch ok),
  P3.2 PASS (activewindow Zen before probe), P3.3 PASS
  (probe ok, snapshot URL, count 1), P3.4 PASS (pre-checks
  clean), P4.1 PARTIAL (focus re-checked, send_switch ok,
  envelope recorded verbatim; the program did NOT complete
  4/4), P4.2 FAIL (dom_act ok False, dimension closure),
  all P5 boxes UNTESTED, not failed, P6.1 EFFECTIVE (scratch
  tab closed, count restored, current restored, despite the
  spurious close error), P6.2 PASS (Zen alive, same address,
  list exits 0, slot free), P6.3 PASS (final map matches
  as-found except the scratch tab gone, which was never in
  as-found). Pill: gate 4.29 met for this run (acquired first,
  status visible true, grim sight-verified before each
  attempt, holder re-checked before the send).
- Safety accounting: no owner tab was closed or navigated
  (count 18 before, 18 after, identical URL sets, current
  restored to Calendar); the only tab opened and closed was
  the scratch fixture tab; no input was sent anywhere in
  either attempt (attempt 1 opened nothing; attempt 2 was
  refused before dispatch); the pill covered every control.
  No stop condition in the task fired (no 'not made current'
  refusal, no owner tab harmed, pill visible throughout).
- What the coordinator must decide, in order:
  1. F2, the dimension closure refusal on the narrowed Zen
     window: fix the geometry origin computation (delegate or
     viewport code, independent worker plus council and
     redteam review; I did not self-fix), or restore Zen to
     full width by moving the OmaCal tiling (a
     window-management decision: OmaCal state belongs to
     another lane, do not move it without a decision).
  2. F1, the transient empty scan read of the current tab:
     consider a direct-read fallback for the original URL when
     the scan entry is empty, or a re-list, through an
     independent fix plus review (tab identification is
     safety-critical; I did not self-fix it).
  3. The cmd_close spurious-error open item from amend 4,
     reproduced live here: a post-DELETE verification read
     masks a successful close. Same fix route as 1 and 2.
  4. Re-run the proof only after 1-3 are landed and reviewed,
     as a fresh run number with a fresh intent/message (R4).
- No self-grading beyond the verdict above, which follows the
  written criteria: PASS requires every phase 4/5 criterion
  live with evidence, and the send never completed.

## 8. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received 21:23:07 +07. VM HEAD at start ffc94b5,
  origin equal.
- Phase 0, 21:24 +07: `python3 -m unittest
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec` Ran 177 tests in 12.517s, OK.
  Fixture sha VM 147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab
  56dcdfc5afb4f72fba6cbf. Programs validate 21:26 +07.
- Runner commit cff51d0 (run3.py, 775 insertions), pushed,
  ls-remote cff51d0d05c4755a00324348b18df40c1e916fcc.
- Pill acquire 1, 21:26:07 +07: daemon spawned PID 181825,
  holder S2-flip:181823, visible true.
- Pre-run grim 1, 21:26 +07: /tmp/c5-zenproof-3/pill-pre-r3.png,
  892422 bytes, sha256 813ed098639fd228076ee4c0825a000dfae2
  60264d59da7b2e21be5a2d54c278, pill visible by sight. First
  grim failed "failed to create display" (missing
  WAYLAND_DISPLAY); the env prefix fixed it.
- Focus switch, 21:27:17 +07: hyprctl dispatch
  "hl.dsp.focus({ window = \"address:0x56307e2771d0\" })" ok;
  activewindow Zen 0x56307e2771d0 ws1.
- Attempt 1, launched 21:27:33 +07, wall 13.8s, outcome error:
  "could not identify the current tab". JSON
  improvements/c5-zenproof-runs/run-3-attempt1.json, sha256
  e8ceaa28fbacf170314fe0a23aaf9fff283cb42832026d95f19539c741cb8d79.
- Diagnosis list 1, 21:28:43 +07: count 18, current 79ea8247,
  empty-URL entry still present.
- Direct diagnostic, 21:29:34 +07: current tab is Calendar,
  https://calendar.google.com/calendar/u/1/r/week, readyState
  complete, 19 inputs.
- Diagnosis list 2, 21:30:25 +07: count 18, Calendar URL
  present, 0 empty entries.
- Pill acquire 2, 21:30:50 +07: daemon spawned PID 185035,
  holder S2-flip:185033, visible true.
- Pre-run grim 2, 21:31 +07: /tmp/c5-zenproof-3/
  pill-pre-r3-a2.png, 894416 bytes, sha256
  47261f5dd2a83e1aabd4988ef309c60e0a2e77371347d2242ad2169fa3edbb2c,
  pill visible by sight.
- Attempt 2, launched 21:31:13 +07, wall 38.8s, outcome error:
  "send program did not complete 4/4: ... dimension closure
  fails: mozInner [274, 66] + inner [677, 1160] exceeds window
  size [925, 1176] (gaps -26, -50)". JSON
  improvements/c5-zenproof-runs/run-3.json, sha256
  c84cd560c4fad8f1437921e1ba558be2934a30c78d4aecc0dd1af6ad2eada534.
- End-state list, 21:32:51 +07: count 18, exact original URL
  set, current Calendar, no fixture tab.
- Final state, 21:33:17 +07: pill holders {}, visible false;
  no live session-driver; no runner on the VM.
- No input was sent anywhere in this task. No owner tab was
  navigated or closed. No Zen restart, no kill-hung.
