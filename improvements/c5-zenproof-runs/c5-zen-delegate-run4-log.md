# W-ZT-B: Zen pointer delegate live proof, run 4 (F1 + F2 verification)

Owner: the owner. Coordinator: COORD-CLICK-12. Worker: W-ZT-B.
Repo ~/workspace/computer-use-wayland, branch todolist-push.
No em dash or en dash anywhere in this file. No personal info.
Report goes to COORD-CLICK-12, not directly to the owner.

## 0. Task receipt and sources read (before any live touch)

- Task received 21:55:58 +07, 22/11/2026. T+0m. Single lane,
  quiet machine, owner away from the machine.
- Sources read before running:
  - improvements/w-zen-delegate-liveproof-prep.md (procedure
    phases 0-7, scratch target
    tests/two_vision_fixture.html?clone=zen, viewport gate P2.4,
    send program phase 4, pass only when dom_act ok True,
    completed 4, error None, post-checks P5.1, retry already-sent
    P5.2, delayed count 1 P5.3, P9 screenshot reviewed by sight
    P5.4, cleanup P6).
  - improvements/c5-zenproof-runs/c5-zen-delegate-run3-log.md
    (run 3: attempt 1 F1 transient empty scan read, attempt 2
    phases 1-3 PASS, phase 4 refused by the dimension closure
    gate on the narrowed 925-wide Zen window, no input sent).
  - improvements/c5-zenproof-runs/run-3.json (attempt 2 result:
    program error dimension closure, mozInner [274, 66] + inner
    [677, 1160] exceeds window [925, 1176], wall 38811.6ms).
  - improvements/w-zenproof2-f1-fix-log.md (F1 fix 5794c8f:
    direct-read fallback for the current tab URL in cmd_list,
    zen-tab.py, 7 tests, 51/51, G0a 177/177, full suite 2377).
  - improvements/w-zenproof2-f2-fix-log.md (F2 fix db21dd7:
    settle the viewport-origin read after tab activation,
    scripts/zen_dom.py, 4 tests, settle budget 2.0s, poll 0.1s,
    3 stable reads, check_viewport_geometry untouched).
- Hard rules restated: never close or navigate any tab of the owner; do NOT reopen the Muse chat tab closed in run 2
  (https://muse.ai/thread/750c8dae-58fb-4a65-82ac-753e78d6ce93);
  pill must show on any agent control (gate 4.29); on a 'not
  made current' refusal, STOP at once, no retry open in a loop,
  no DELETE via Marionette, report to the coordinator; if any
  owner tab is closed or navigated wrong, or the pill is not
  visible during control, STOP at once and report; no em dash;
  no ydotool; no personal info on GitHub; log continuously with
  wall-clock Asia/Ho_Chi_Minh plus elapsed; commit with an
  explicit pathspec, never bare commit, never add -A; if run 4
  still refuses, record the error, STOP, report, do NOT self-fix.
- This run is run 4, NEW run number, NEW intent
  c5-zen-delegate-r4, NEW message ZEN-DELEGATE-R4-IGNORE-TEST.
  It verifies both fixes landed after run 3: F1 (direct-read
  fallback, zen-tab.py 5794c8f) and F2 (viewport-origin settle,
  scripts/zen_dom.py db21dd7).

## 1. Time log (wall-clock Asia/Ho_Chi_Minh, elapsed from 21:55:58 +07)

- 21:56:28 +07, T+0m: task received. VM HEAD 4cf115c, branch
  todolist-push, origin equal. Sources read (section 0).
- 21:56 +07, T+0m: run4.py created by copying run3.py,
  identical copy verified by diff (no output), then the
  renames (section 2). py_compile OK, 0 em dash, 0 en dash.
  Fixture sha on the VM matches the manifest.
- 21:56 to 21:57 +07, T+0m to T+1m: phase 0 gates (section 2):
  G0a 177 OK in 14.642s, G0b probe plus send validate OK.
- 21:57 +07, T+1m: laptop as-found read-only checks (section 2):
  Zen 0x56307e2771d0 on ws1, bounds [2509, 914, 925, 1176],
  still narrowed 925 wide, OmaCal tiled beside it; active window
  Chromium on ws2 (not Zen); laptop repo BEHIND at 8b0b32d,
  fixture sha matches, geckodriver present at
  ~/.local/bin/geckodriver, pill OFF (holders {}, visible false).
- 21:57 +07, T+1m: laptop repo fast-forwarded 8b0b32d to
  4cf115c (origin/todolist-push), so the F2 fix in
  scripts/zen_dom.py is live on the laptop. Settle code present
  (6 grep hits), F1 fallback present in zen-tab.py (4 hits).
- 21:57:30 +07, T+2m: pill acquire (section 3). Daemon spawned,
  holder S2-flip:204881, visible true.
- 21:57 +07, T+2m: pre-run grim reviewed by sight: pill
  VISIBLE top center, label "S2-flip via CDP". Copy to the VM
  needed one retry (missing /tmp dir on the VM, not a grim
  failure).
- 21:58 +07, T+2m: runner commit 1448dc3 pushed, ls-remote
  verified.
- 21:58:19 +07, T+2m: focus Zen by window address, dispatch ok,
  activewindow Zen 0x56307e2771d0 ws1. No tab navigated or
  closed, only focus.
- 21:58:22 +07, T+2m: run 4 launched detached,
  PILL_SLEEP_PID=204881.
- 21:59:07 +07, T+3m: run 4 finished, wall 39.3s, outcome
  error, phase 4 "point outside observed image". No input sent.
  Pill released ok.
- 21:59:30 +07, T+4m: end-state verification (section 6):
  independent fresh list, count 18, exact original URL set,
  current is the Calendar tab, no fixture tab. Pill holders {},
  visible false; no live session-driver; runner process gone.
- 21:59 to 22:01 +07, T+4m to T+5m: evidence copied to the
  repo, log written, STOP per the task (proof FAILS on a new
  refusal, no self-fix) and report to COORD-CLICK-12. No stall
  over 15 minutes at any point in this task.

## 2. Phase 0 gates (VM, no live touch) and the run4.py runner

- G0a PASS, 21:56 +07: `python3 -m unittest
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec` returned Ran 177 tests in 14.642s, OK.
- G0b PASS, 21:56 +07: probe program and send program (run 4
  text, message ZEN-DELEGATE-R4-IGNORE-TEST) both pass
  code_exec.validate_program with no exception.
- G0c PASS, 21:56 +07: `sha256sum
  tests/two_vision_fixture.html` on the VM =
  147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6cbf,
  matching the manifest. Same hash on the laptop.
- G0d PASS: fresh intent c5-zen-delegate-r4, fresh message
  ZEN-DELEGATE-R4-IGNORE-TEST for run 4.
- Runner run 4: improvements/c5-zenproof-runs/
  c5-zen-delegate-run4.py, copied from the run 3 runner
  (c5-zen-delegate-run3.py, which itself was copied from the
  fixed run 2 runner). Diff run3 to run4 limited to the briefed
  renames: docstring run 4 plus coordinator COORD-CLICK-12 plus
  the F1/F2 fix note, RUN_NO 4, MESSAGE/INTENT R4, WORKDIR
  /tmp/c5-zenproof-4, run-4.json, p9-zen-r4.png,
  pill-during-r4.png, usage line. Everything else (transport,
  phases, programs, gates, pill handling, grim Wayland-env
  prefix) is byte-identical to run3.py. py_compile OK. 0 em
  dash, 0 en dash in run4.py. Commit 1448dc3 pushed and
  ls-remote verified before the run.
- Laptop sync (not in run 3, required here): the laptop
  checkout was at 8b0b32d, behind the VM at 4cf115c. The F2 fix
  lives in scripts/zen_dom.py on the laptop, and the runner
  only scps zen-tab.py (the F1 fix), so the laptop repo had to
  be fast-forwarded before the run, or run 4 would have tested
  the old viewport_origin. `git fetch origin todolist-push`
  then `git merge --ff-only origin/todolist-push` moved it
  8b0b32d to 4cf115c, equal to the VM HEAD. Verified after:
  settle symbols present in scripts/zen_dom.py, fallback
  symbols present in improvements/c5-zenproof-runs/zen-tab.py.
  The laptop working tree had only untracked files, no tracked
  modifications, so the fast-forward was safe.

## 3. Pill verification (gate 4.29)

- Pill started OFF for this run (holders {}, owner none,
  visible false), confirmed by read-only status check at 21:57.
- Acquire, 21:57:30 +07: overlay acquire returned daemon
  spawned PID 204884, holder S2-flip:204881 acquired
  21:57:30 +07, label "S2-flip via CDP", owner daemon, visible
  true, PILL_SLEEP_PID=204881.
- Pre-run grim, 21:57 +07: /tmp/c5-zenproof-4/pill-pre-r4.png,
  512983 bytes, sha256
  98755c11a31a5a11bf2d53534133a25a267560f9d5268fae518efb46fde552a5,
  reviewed by sight: pill VISIBLE top center, label "S2-flip
  via CDP", green dot. The screen shows the mochi Muse chat
  (another lane's live work, left) and a Pick 4 fixture in a
  second browser window (right); neither was touched. A
  "Process crashed: WebKitWebProcess" notice (20:04) is
  pre-existing, not mine. The first scp of the grim failed
  only because /tmp/c5-zenproof-4 did not exist yet on the VM;
  mkdir then re-scp succeeded with the same sha.
- During-run pill: the runner re-verified the holder alive and
  status visible true at the start of the run (recorded in
  run-4.json under "pill") and re-checked the holder
  immediately before the phase 4 send. No pill-during grim
  exists because the run never reached phase 5 (it failed in
  phase 4). The pill was released cleanly at the end of the
  run (pill_release ok, pid 204881); final status 21:59 is
  holders {}, visible false.
- No control ran without a visible pill: every Zen control in
  this task (focus switch, tab lists, open, switch, probe,
  send attempt) ran while the S2-flip holder was up and the
  pill was verified visible.

## 4. F1: PROVEN LIVE, the direct-read fallback fired

- tabs_before in run-4.json carries "current_fallback": true.
  The phase 1 scan again returned an empty entry for the
  current tab (the same transient scan-read artifact as run 3
  attempt 1: the list_tabs switch-through read of the Calendar
  tab came back with no URL), and the new _resolve_current_entry
  fallback in zen-tab.py resolved it by direct read in the
  same session (handle read, URL read, handle read, URL read,
  all agreeing) to the Calendar tab,
  https://calendar.google.com/calendar/u/1/r/week.
- Phase 1 therefore PASSED instead of aborting with "could not
  identify the current tab" as run 3 attempt 1 did. The run
  proceeded through phases 2-4 on the correctly identified
  original tab. This is the live proof the F1 fix was built
  for: the fallback fired on a real transient empty read, and
  the rest of the run used the resolved URL.
- Evidence: run-4.json tabs_before.current is 1d15500e with
  title "Lich Google - Tuan 16 thang 11, 2026" and the Calendar
  URL, current_fallback true; the end-state direct diagnostic
  (section 6) independently confirms the current tab is that
  same Calendar tab.

## 5. Attempt 1 (only attempt): phases 1-3 PASS, phase 4 refused by a NEW error (F2 gate passed, F3)

- Launched 21:58:22 +07, finished about 21:59:07, wall
  39347.0ms, outcome error, "send program did not complete 4/4".
- Phase 1 PASS: Zen 0x56307e2771d0 on ws1, bounds [2509, 914,
  925, 1176], still narrowed 925 wide with OmaCal tiled beside
  it on ws1 (same as run 3); tabs_before 18, current Calendar
  1d15500e with URL resolved by the F1 fallback
  (current_fallback true); liveness live false (ps shows no
  session-driver, relay state finished, owner s2-flip-run6,
  guardian clean, recovery none; 11 stale leases recorded as
  evidence only).
- Phase 2 PASS: open ok, new handle
  42b20719-0174-4a44-8c0c-5bdebe874ddf, count 18 to 19,
  selected_by explicit-select (POST /window/new did NOT make
  the new tab current; the one explicit select did, exactly
  the amend fix working as designed), URL the fixture,
  H1 'Clone zen thread', ready complete, viewport_ok true,
  metrics innerWidth 677, innerHeight 1160, hasFocus true,
  element_at_point 'msg-input', rect x 20 y 228.87 w 340
  h 36, harvest moz_inner [251, 26], inner [677, 1160],
  outer [925, 1176].
- Phase 3 PASS: switch ok; read-only probe ok (PROBE zen-1
  fixture URL, 1 element, wall 2024.7ms, envelope elapsed
  519.019ms, snapshot title the static fixture title as
  evidence only); pre-checks clean (H1 'Clone zen thread',
  bubble_present false, bubbles [], input '', input_events 0).
- Phase 4 FAIL, NEW error: send_switch ok (handle 459760b8,
  fixture URL); then dom_act ok False, elapsed 1123.553ms,
  completed null, log only the PROBE line. Error verbatim:
  "point outside observed image", error_type "sandbox". The
  backend refused BEFORE any dom_act result line: no set_value,
  no focus, no key, no message typed, no bubble. The send
  snapshot URL and count gates passed (fixture URL, 1 element),
  so the failure is not a wrong-tab send.
- F2 verdict: the dimension-closure refusal that killed run 3
  is GONE. No "dimension closure fails" error appears anywhere
  in run-4.json or the runner stdout. The send snapshot read
  went through the settled viewport_origin (F2 fix) and the
  closure gate passed. The program elapsed rose from run 3's
  677.055ms to 1123.553ms (plus 446ms), consistent with the
  settle loop polling, but that is consistency only, not a
  measurement of the settle itself.
- last_viewport_settle, honest limitation: the settle record
  (reads, settled moz, elapsed ms) lives only on the
  ZenSession object in the oneshot process
  (scripts/zen_dom.py self.last_viewport_settle) and is NOT
  surfaced in the code-exec envelope, the dom_act result, or
  any log line. I checked: no caller of viewport_origin in
  scripts/zen_backend.py or scripts/dom_act.py reads or logs
  last_viewport_settle. So run 4 cannot report the settle
  reads/elapsed as numbers. What run 4 proves about F2 is:
  no dimension-closure refusal, and the send reached the
  point-validation step past the geometry gate. If the
  coordinator wants the settle reads/elapsed as numbers, the
  settle record must be surfaced in the envelope by a fix, or
  measured by a dedicated diagnostic that calls
  viewport_origin directly and prints last_viewport_settle.
  I did not add that instrumentation: the brief fixed the
  runner to the run 3 copy plus renames.
- The new refusal, recorded not diagnosed: the string "point
  outside observed image" is raised at scripts/cu.py:1030 in
  image_point(meta, x, y), when the point is outside the
  observed image dimensions (iw, ih) from
  validate_coordinate_metadata(meta). That is the full extent
  of what I established by reading the code. I did NOT
  determine which point, which image, or which coordinate
  frame mismatched, and I did NOT fix anything. Per the task
  order: record the error, STOP, report to COORD-CLICK-12.
- Phase 5 not reached: no post-checks, no retry check, no
  delayed recount, no P9 (nothing was sent to photograph).
  No pill-during grim exists for the same reason.

## 6. Cleanup and end state

- Cleanup reported ok False: "zen-tab close failed rc=1:
  Browsing context has been discarded" (NoSuchWindowError, a
  post-DELETE verification read hitting the discarded
  context). This is the known amend-4 open item (amend4 log
  section 4), reproduced in run 3 as well: cmd_close
  post-DELETE verification reads can still raise after a
  successful DELETE and mask the close success. Consequence
  is a spurious error, never a wrong navigate or DELETE.
- End state verified by an independent fresh list, 21:59 +07
  (improvements/c5-zenproof-runs/list-after-r4.txt): count back
  to 18, the EXACT original 18-URL set from tabs_before (only
  before [] and only after []), no fixture tab, 0 empty-URL
  entries, Calendar URL present. The DELETE did succeed; only
  its success report was masked.
- Current tab verified by a read-only direct diagnostic
  (diag-current-tab.py, fresh ZenSession, no switch, only GET
  /window, /url, /title plus one JS evaluate), 21:59 +07:
  url endpoint 'https://calendar.google.com/calendar/u/1/r/week',
  title 'Lich Google - Tuan 16 thang 11, 2026', JS document.URL
  the same Calendar week view, readyState complete, 19 inputs.
  The current tab is the original tab.
- Final state, 21:59 +07: pill holders {}, visible false; no
  live session-driver on the laptop; no runner process on the
  VM (the pgrep hits during the wait were self-matches of the
  wrapping shell command line, confirmed gone by a ps check
  that excludes the pattern); laptop run dir holds the amend-4
  zen-tab.py plus the pill grims.
- The Muse chat tab closed in run 2 is still absent (no
  muse.ai URL in any list). It was NOT reopened in this task,
  per the task order.

## 7. Verdict

- FAIL. The Zen pointer delegate live proof did NOT pass: no
  send program completed, no P4/P5 criterion was met, no P9
  of a sent bubble exists. Attempt 1 passed phases 1-3 and was
  refused in phase 4 by a NEW error, "point outside observed
  image" (error_type sandbox).
- F1: PASS, proven live. The direct-read fallback fired
  (current_fallback true) on a real transient empty scan read
  of the current tab, resolved it to the Calendar tab, and
  phase 1 passed where run 3 attempt 1 aborted.
- F2: PARTIAL PASS, proven as far as the run reaches. The
  dimension-closure refusal from run 3 is gone: the send
  snapshot went through the settled viewport_origin and the
  closure gate passed. But the settle reads/elapsed numbers
  are NOT available in the run evidence (section 5 limitation),
  and the send still did not complete, so F2 is not proven
  end to end by a sent bubble.
- F3 (new): "point outside observed image", error_type
  sandbox, scripts/cu.py:1030 image_point. Unfixed, undiagnosed
  beyond the raise site. Needs an independent fix plus review,
  same route as F1 and F2.
- Checklist status: G0a PASS (177 OK), G0b PASS (both programs
  validate), G0c PASS (fixture sha both sides), G0d PASS (fresh
  intent and message), P1.1 PASS (Zen active ws1, narrowed 925),
  P1.2 PASS (list ok, 18 tabs, current Calendar identified via
  the F1 fallback), P1.3 PASS (geckodriver at the resolved
  path), P1.4 PASS (fixture sha on the laptop, laptop repo
  fast-forwarded to 4cf115c first), P1.5 PASS (live false, relay
  finished), P2.2 PASS (open ok, count +1, URL and H1 verified,
  viewport_ok true), P2.3 PASS (rect recorded), P2.4 PASS
  (viewport gate true), P3.1 PASS (switch ok), P3.2 PASS
  (activewindow Zen before probe), P3.3 PASS (probe ok,
  snapshot URL, count 1), P3.4 PASS (pre-checks clean), P4.1
  PARTIAL (focus re-checked, send_switch ok, envelope recorded
  verbatim; the program did NOT complete 4/4), P4.2 FAIL
  (dom_act ok False, "point outside observed image"),
  all P5 boxes UNTESTED, not failed, P6.1 EFFECTIVE (scratch
  tab closed, count restored, current restored, despite the
  spurious close error), P6.2 PASS (Zen alive, same address,
  list exits 0, slot free), P6.3 PASS (final map matches
  as-found except the scratch tab gone, which was never in
  as-found). Pill: gate 4.29 met for this run (acquired first,
  status visible true, grim sight-verified before the run,
  holder re-checked before the send).
- Safety accounting: no owner tab was closed or navigated
  (count 18 before, 18 after, identical URL sets, current
  restored to Calendar); the only tab opened and closed was
  the scratch fixture tab; no input was sent anywhere (the
  program failed before any dom_act result line, completed
  null, log only PROBE; phase 5 post-checks could not run
  because the fixture tab was closed, so no bubble state was
  observable after the failure, and none is claimed); the pill
  covered every control. No stop condition in the task fired
  (no 'not made current' refusal, no owner tab harmed, pill
  visible throughout).
- What the coordinator must decide, in order:
  1. F3, "point outside observed image" (error_type sandbox,
     scripts/cu.py:1030 image_point): diagnose which point and
     which image frame mismatch, fix through an independent
     worker plus council and redteam review; I did not
     self-fix or self-diagnose beyond the raise site.
  2. Surface last_viewport_settle (reads, settled moz, elapsed
     ms) in the code-exec envelope or a diagnostic, if the
     settle numbers are wanted as run evidence (section 5).
  3. The cmd_close spurious-error open item from amend 4,
     reproduced live here for the second run in a row: a
     post-DELETE verification read masks a successful close.
     Same fix route as 1.
  4. Re-run the proof only after 1 is landed and reviewed, as
     a fresh run number with a fresh intent/message (R5).
- No self-grading beyond the verdict above, which follows the
  written criteria: PASS requires every phase 4/5 criterion
  live with evidence, and the send never completed.

## 8. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received 21:55:58 +07. VM HEAD at start 4cf115c,
  origin equal.
- Phase 0, 21:56 +07: `python3 -m unittest
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec` Ran 177 tests in 14.642s, OK.
  Fixture sha VM 147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab
  56dcdfc5afb4f72fba6cbf. Programs validate 21:56 +07.
- Runner commit 1448dc3 (run4.py, 780 insertions), pushed,
  ls-remote 1448dc39028845d294cbe2817915eb42fb406fd0.
- Laptop repo fast-forward, 21:57 +07: 8b0b32d to 4cf115c,
  origin/todolist-push, verified equal to the VM HEAD.
- Pill acquire, 21:57:30 +07: daemon spawned PID 204884,
  holder S2-flip:204881, visible true.
- Pre-run grim, 21:57 +07: /tmp/c5-zenproof-4/pill-pre-r4.png,
  512983 bytes, sha256
  98755c11a31a5a11bf2d53534133a25a267560f9d5268fae518efb46fde552a5,
  pill visible by sight.
- Focus switch, 21:58:19 +07: hyprctl dispatch
  "hl.dsp.focus({ window = \"address:0x56307e2771d0\" })" ok;
  activewindow Zen 0x56307e2771d0 ws1.
- Run 4, launched 21:58:22 +07, wall 39347.0ms, outcome error:
  "send program did not complete 4/4: ... 'point outside
  observed image', 'error_type': 'sandbox'". JSON
  improvements/c5-zenproof-runs/run-4.json, sha256
  0925e148137ae560fc9addae2735a02066dcfafb41ff35f1eec274d089602a22.
  Program elapsed 1123.553ms (run 3: 677.055ms).
- F1 evidence: run-4.json tabs_before.current_fallback true,
  current 1d15500e Calendar URL.
- F2 evidence: no "dimension closure" string in run-4.json or
  the runner stdout; program reached the point-validation
  step past the geometry gate.
- End-state list, 21:59 +07:
  improvements/c5-zenproof-runs/list-after-r4.txt, count 18,
  URL sets identical to tabs_before, no fixture tab.
- Current-tab diagnostic, 21:59 +07: Calendar
  https://calendar.google.com/calendar/u/1/r/week, readyState
  complete, 19 inputs.
- Final state, 21:59 +07: pill holders {}, visible false; no
  live session-driver; no runner on the VM.
- No input was sent anywhere in this task. No owner tab was
  navigated or closed. No Zen restart, no kill-hung.
