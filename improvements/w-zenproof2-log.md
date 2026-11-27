# W-ZENPROOF2: Zen pointer delegate live proof, run 2 (close R13)

Owner: the owner. Coordinator: COORD-CLICK-9. Worker: W-ZENPROOF2.
Repo ~/workspace/computer-use-wayland, branch todolist-push.
No em dash or en dash anywhere in this file. No personal info.
Report goes to COORD-CLICK-9, not directly to the owner.

## 0. Task receipt and sources read (before any live touch)

- Task received 19:55:04 +07, 22/11/2026. T+0m.
- Laptop is free: the owner hung may 19:10 22/11, not at the machine.
  Per task order, ignore every idle/activity signal (IdleHint, input,
  focus, mouse, keyboard) as fake, do not gate live work on idle
  checks, keep running. Order 19:11 22/11.
- Sources read before running, procedure and R13 pass criteria
  recorded here verbatim from them:
  - improvements/w-zen-delegate-liveproof-prep.md (W-ZENPREP, prep
    cb741fe, fix B 161de2a, run kit 2d1dc82, run 1 abort d2ba7db):
    procedure phases 0-7, scratch target
    tests/two_vision_fixture.html?clone=zen, title 'Clone zen thread',
    message/intent fresh per run, viewport gate P2.4 (innerWidth and
    innerHeight > 0, hasFocus true, elementFromPoint non-null) before
    any input, send program phase 4 (set_value, focus, key Enter with
    ref, assert), pass only when dom_act ok True, completed 4, error
    None, post-checks P5.1 (bubble present, bubbles exactly [MESSAGE],
    input empty, input_events >= 1), retry already-sent P5.2, delayed
    count 1 after 10s P5.3, P9 screenshot reviewed by sight P5.4,
    cleanup P6 (scratch tab closed, handle count restored, current tab
    restored to owner tab, Zen alive, slot free).
  - R13 definition (prep file section 10.7, coord-click-6-log.md):
    run 1 aborted phase 1 because the active window was mochi
    Chromium on ws2 (0x56307e202df0) and mei Brave was also live on
    ws2; Zen on ws1 (0x56307e2771d0) was not active; focusing Zen
    would yank the visible workspace away from two live agent lanes.
    Coordinator decision then: do NOT authorize the focus switch;
    live proof WAITS until the mei/mochi lanes are idle, then rerun.
    R13 is closed by this run only when: (a) liveness check (ps plus
    relay state, P1.5 fix 902ffbe) shows NO live lane holds the
    machine, and (b) the full send program then passes every phase
    4/5 criterion live on Zen. A P1.1 abort on a still-live lane
    would leave R13 open, not closed.
  - R14 cleared by W-GECKO (0cb2b20): geckodriver 0.37.1 at
    ~/.local/bin/geckodriver, sha256 f831b7e6...,
    default now prefers that persistent path; minimal Marionette
    verify 18:11:01 +07 ok, 18 handles. P1.5 cleared by W-GECKO
    (902ffbe): liveness from ps plus relay state, leases evidence
    only, 13/13 unit tests.
  - Final direction: improvements/worker-click3-final-direction-log.md
    (read, grep R13/zenproof: no separate R13 pass criteria beyond
    the coord log decision above; the live proof waits for the same
    idle condition).
  - Todolist docs/zen-error-fix-todolist-20261121.md: item 4.29 pill
    must show on any agent control (hard rule 18:30); gate 4.29 met
    by W-PILLVERIFY2 (9ac4dcd, live pill render PASS after 8f600b9).
    Pill must show during this proof; verify with grim before and
    during, stop at once if the pill is not visible.
  - Run 1 abort lesson: do not re-run with the same intent/message
    after a send; run 1 sent nothing, but this is run 2 with fresh
    intent c5-zen-delegate-r2 and fresh message
    ZEN-DELEGATE-R2-IGNORE-TEST (G0d), so no ledger reuse at all.
- Hard rules restated: never close or navigate any tab of the owner
  (18:23); pill must show on any agent control (18:30); no
  self-review, no self-fix of my own failure (19:15: if proof FAILS,
  report and stop, an independent worker fixes via council 3 plus
  redteam); no em dash; no ydotool; no personal info on GitHub; no
  self-grading; log continuously with wall-clock Asia/Ho_Chi_Minh
  plus elapsed; if stuck 15 minutes with no progress, record it.
- Commit rule: git add with explicit pathspec AND git commit -m
  with explicit pathspec, never bare commit, never add -A, never
  amend. Push at once, verify with git ls-remote.

## 1. Time log (wall-clock Asia/Ho_Chi_Minh, elapsed from 19:55:04 +07)

- 19:55:40 +07, T+0m: VM HEAD 71e807a (W-PILLFIX-CLOSEOUT), origin
  9ac4dcd (W-PILLVERIFY2). Local one commit ahead of origin, both
  children of fd77698. git merge --ff-only failed (diverged).
- 19:56 +07, T+1m: git rebase onto origin/todolist-push produced
  HEAD 394a989 (same W-PILLFIX-CLOSEOUT content, rebased onto
  9ac4dcd). History now linear on origin. Verified: diff 71e807a to
  394a989 is exactly the w-pillverify2-log.md addition (200 lines),
  no content lost. Pre-existing dirty tree untouched: modified
  tests/realistic/clone1-batch3/results.json (not mine, never
  commit), plus 8 untracked improvements files from other workers
  (not mine, never commit).
- 19:56 to 19:59 +07, T+1m to T+4m: phase 0 gates (section 2).
  Laptop as-found read-only checks (section 3): no live lane by
  ps plus relay (relay idle, owner null), active window is the
  Pick 4 fixture Chromium on ws2 with no driver behind it.
- 19:59 +07, T+4m: run-2 runner written (section 2, geckodriver
  check fix). Two laptop checkouts found: ~/workspace/
  computer-use-wayland at 9ac4dcd (current, pill fix present) and
  ~/computer-use-wayland at 331523f (old, contains fix B,
  R14, P1.5, missing only pill fix 8f600b9, dirty overlay/indicator
  files from another lane). Relay serve cwd is the old checkout,
  so live sessions run from the old checkout. Decision: do NOT
  touch either laptop checkout (the old one has another lane's
  dirty files and the live relay runs from it; the new one was
  synced by W-PILLVERIFY2 for CDP pill verify). The runner uses
  the old checkout paths, as run 1 did; both checkouts resolve
  geckodriver to ~/.local/bin/geckodriver and both
  fixture shas match. Session-path pill showed in 6 sessions at
  18:43 with the old code (W-F4FIX); pill will be verified live
  with grim during this run, stop at once if absent.
- 20:00:37 +07, T+5m: run 2 attempt 1 ABORTED in phase 1, wall
  2.7s, outcome error, no tab opened, no input sent. Error:
  "zen-tab list failed rc=2: python3: can't open file
  '~/c5-zenproof-run/zen-tab.py': No such file or
  directory". Cause: phase 1 calls tab('list') but the driver scp
  only happens in phase 2; run 1 never reached phase 2 (it
  aborted at the activewindow gate), so the driver was never on
  the laptop. Positive evidence from the abort: P1.1 PASSED this
  time (Zen 0x56307e2771d0 active on ws1, bounds [2509, 914, 1863,
  1176], recorded in run-2-attempt1.json), so the R13 focus
  switch is effective. Fix: move the driver transfer (mkdir plus
  scp plus sha verify) from phase 2 to phase 1, before the first
  tab call. This is a run-kit ordering fix, not a change to the
  delegate or the proof program. py_compile OK. Attempt 1 JSON
  preserved as improvements/c5-zenproof-runs/run-2-attempt1.json.
  Retry as run 2 attempt 2 with the same fresh intent/message
  (nothing was sent, no ledger entry exists).
- 20:01:14 +07, T+6m: commit cfa687b (driver transfer fix +
  log + attempt 1 JSON) pushed, ls-remote verified.
- 20:01:23 +07, T+6m: run 2 attempt 2 launched detached,
  PID 41606. Zen re-verified active (0x56307e2771d0 zen 1)
  immediately before launch.
- 20:01:44 +07, T+6m: attempt 2 finished, wall 20.4s,
  outcome error, phase 2 title mismatch (section 5). No
  input sent. Grim pill-1 taken 20:02:13 (after the run, not
  during a session).
- 20:02 to 20:04 +07, T+7m to T+9m: verification reads found
  the Muse chat tab missing (section 6). Two back-to-back
  lists confirm the URL set has no muse.ai tab and handles
  are ephemeral per session. Grim pill-1 reviewed by sight:
  Zen shows Calendar, Muse tab absent from the sidebar.
- 20:05 +07, T+10m: final window map shows OmaCal active on
  ws1, launched ~20:05 by another lane (PID 132112), not by
  me. No further live action taken after seeing it.
- 20:05 to 20:08 +07, T+10m to T+13m: evidence copied to the
  VM (/tmp/w-zenproof2-baseline.png, /tmp/w-zenproof2-pill-1
  .png, list A/B JSONs), log completed, STOP per the task
  (procedure wrong, no self-fix) and the 19:15 rule. No stall
  over 15 minutes at any point in this task.

## 2. Phase 0 gates (VM, no live touch)

- G0a PASS, 19:56 +07: `python3 -m unittest tests.test_zen_pointer
  tests.test_p2_element_ref tests.test_code_exec` returned Ran 177
  tests in 12.992s, OK (zen_pointer 17 including the 2
  RealSignatureTests from fix B, p2_element_ref 100, code_exec 60).
  Fix B commit 161de2a is an ancestor of HEAD.
- G0b PASS, 19:58:56 +07: probe program and send program (run 2
  text, message ZEN-DELEGATE-R2-IGNORE-TEST) both pass
  code_exec.validate_program with no exception.
- G0c PASS, 19:56 +07: `sha256sum tests/two_vision_fixture.html`
  on the VM = 147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5a
  f72fba6cbf, matching the manifest.
- G0d PASS: fresh intent c5-zen-delegate-r2, fresh message
  ZEN-DELEGATE-R2-IGNORE-TEST for run 2.
- Runner run 2: improvements/c5-zenproof-runs/c5-zen-delegate-
  run2.py, copied from the run 1 runner, diff limited to: run
  number 2, message/intent R2, workdir /tmp/c5-zenproof-2, run-2
  .json, p9-zen-r2.png, plus ONE functional change: the phase 1
  geckodriver check. The prep procedure P1.3 asked for
  /tmp/geckodriver, but R14 (0cb2b20) moved the default to the
  persistent ~/.local/bin/geckodriver and /tmp/geckodriver no
  longer exists on the laptop (verified 19:57 +07, "No such file
  or directory"; resolved path via zen_dom on the laptop prints
  ~/.local/bin/geckodriver True for both checkouts).
  The old check would false-abort every run, so the run 2 runner
  asks zen_dom itself for the resolved path and requires the file
  to exist there. py_compile OK. This is a check alignment with
  the landed R14 fix, not a change to the delegate or the proof
  program.

## 3. Phase 1 laptop as-found checks (run 2 attempt 1, read-only + focus)

- Window map 19:57 +07 (before focus): Zen 0x56307e2771d0 ws1
  'Muse - Zen Browser'; chromium 0x56307e202df0 ws2 'Pick 4 DOM
  fixture - Chromium' (ACTIVE, leftover window, no driver
  behind it); chromium 0x56307e7d9bb0 ws2 'Chat - mochi -
  Chromium'; brave-origin 0x56307e4c2f90 ws2 'Muse - Brave
  Origin'; herdrdrop special.
- Liveness 19:57 +07: ps shows NO session-driver and NO
  session_remote client (start/request/result/finish); relay
  serve PID 70985 up, status state idle, owner null, driver
  idle, guardian idle, recovery none, next_sequence 1. Leases
  all stale (16:04 to 16:31, step 9 runs). P1.5 verdict:
  live=False. No live lane holds the machine. R13 condition
  (lanes idle) met in fact, with this task as the coordinator
  authorization to run now as the sole live runner.
- Geckodriver: /tmp/geckodriver missing (expected, R14 moved
  the default); ~/.local/bin/geckodriver present, 6029440 bytes,
  18:10; zen_dom resolves GECKODRIVER to
  ~/.local/bin/geckodriver in both laptop checkouts.
- Fixture sha on the laptop (both checkouts) matches the
  manifest hash.
- Focus switch 19:59:42 +07: `hyprctl dispatch
  "hl.dsp.focus({ workspace = 1 })"` returned ok; activewindow
  verified Zen 0x56307e2771d0 ws1 'Chat - Muse - Zen Browser'.
  No tab of the owner navigated or closed; only the visible
  workspace changed ws2 to ws1 while no lane was live.
- Baseline grim 19:59 +07: /tmp/w-zenproof2-baseline.png,
  768335 bytes (to be reviewed with the P9 evidence).
- Runner commit 4f31371 pushed and ls-remote verified before
  the run. Note: at commit time HEAD had moved to c6e5a2f
  (Council 1 review of W-PILLFIX, pushed by another lane after
  my fetch); my commit landed on top of it cleanly, no content
  lost.

## 4. Pill verification

- Gate 4.29 was met before this run (W-PILLVERIFY2 9ac4dcd,
  19:50: pill HIEN in grim during CDP act, ok:true completed:5).
- Baseline grim 19:59 (/tmp/w-zenproof2-baseline.png, 768335
  bytes, reviewed by sight): pill VISIBLE top center, label
  "S2-flip via CDP". This is a leftover holder pill from
  W-PILLVERIFY2 (S2-flip re-acquired 19:51:53), NOT a pill
  spawned by this run. No session-driver ran in this task before
  the baseline, so no run pill existed yet.
- Pill-1 grim 20:02:13 (/tmp/w-zenproof2-pill-1.png, 796339
  bytes, reviewed by sight): the same "S2-flip via CDP" pill
  still visible top center. Again a leftover holder, not a run
  pill: attempt 2 never reached a session-driver (it aborted in
  phase 2), so this run never spawned a pill and the pill rule
  was never satisfied by this run for its own control actions.
  Recorded honestly: the Marionette tab-driver operations
  (open, list, close) run OUTSIDE the session/pill mechanism,
  so no pill covered the open/close that closed the Muse tab
  (section 6). The pill gate for the probe/send phases was never
  reached, so pill-during-send remains unproven for this run.
- No input was sent through any session-driver in this task, so
  there is no "control without pill" session to report; the gap
  above is the Marionette path having no pill at all.

## 5. Phase 2 scratch tab + viewport gate (attempt 2)

- Attempt 2, wall 20.4s, outcome error. Phase 1 passed fully
  (tabs_before 18 tabs, current ef90cb33 'Chat - Muse',
  liveness live=False, relay idle, 10 stale leases). Phase 2
  open FAILED: "zen-tab open failed rc=1: ZenDomError: scratch
  tab title 'Two-vision benchmark fixture' != 'Clone zen
  thread'".
- Root cause, verified from the fixture source: the prep
  procedure assumes ?clone=zen sets document.title to 'Clone
  zen thread'. It does not. tests/two_vision_fixture.html has a
  static <title>Two-vision benchmark fixture</title>; its JS
  only sets the H1 text to 'Clone zen thread' and never touches
  document.title. git log confirms the fixture was brought onto
  todolist-push unedited (7f3a70b) and no commit ever set
  document.title to 'Clone zen thread' (git log -S 'Clone zen
  thread' and -S 'document.title' on the fixture both return
  nothing). The premise was wrong from the start, so phase 2 as
  written can never pass.
- Second, independent blocker from the same premise: even if
  the open gate were bypassed, the probe/send programs target
  'Clone zen thread', and _resolve_target matches the target as
  a substring over title, url, or handle only. The scratch tab
  has title 'Two-vision benchmark fixture', url
  file:///.../two_vision_fixture.html?clone=zen, and an opaque
  handle, none containing 'Clone zen thread', so dom_observe
  would raise 'no tab matches target'. The snapshot title
  returned by dom_observe is tab.get('title'), again the
  document title, so the runner's probe title check would fail
  too. Three gates, one wrong literal.
- Per the task (procedure wrong, not vague: report and stop, do
  not invent a new proof) and the 19:15 rule (no self-fix), I did
  NOT change the target to a URL substring, even though that is
  the likely one-line fix. The coordinator decides the fix and
  the re-run. The viewport gate P2.4 was never reached (no
  viewport measurement was taken on a scratch tab).

## 6. INCIDENT: the run closed the owner's Muse chat tab

- What is missing: the Zen tab 'Chat - Muse',
  https://muse.ai/thread/750c8dae-58fb-4a65-82ac-753e78d6ce93,
  handle ef90cb33 in tabs_before, which was the visible tab at
  19:59:42 ('Chat - Muse - Zen Browser', baseline grim shows
  the Muse conversation on screen).
- Evidence it is gone (three independent reads, all after
  attempt 2, all by URL, not by handle):
  - 20:02 list: count 18, current Calendar, no muse.ai URL.
  - 20:04 list A and list B (back-to-back identical calls):
    identical 18-URL sets, no muse.ai URL in either.
  - Grim pill-1 20:02:13, reviewed by sight: Zen shows Google
    Calendar, sidebar tab list has no muse.ai tab.
- Evidence of when: baseline 19:59 shows the Muse tab visible;
  the first list after attempt 2 (20:02) already shows it gone.
  Nothing else touched Zen in between except this run's attempt
  2 and read-only list scans (GETs and tab switches, no close).
  The only DELETE in attempt 2 is cmd_open's exception handler
  (DELETE /session/{id}/window after the title mismatch).
- Likely mechanism (inference from the evidence, not proven by
  a separate experiment): finding C's suspected cause, that
  Zen's own tab management never selects a Marionette opened
  tab. If POST /window/new did not make the scratch tab
  current, then POST /url navigated the CURRENT tab (the Muse
  tab) to the fixture, the title read returned the fixture
  title, and DELETE closed the current window, which was the
  Muse tab. This fits every observation: Muse tab gone, no
  fixture tab remains, count back to 18 (18 + 1 opened - 1
  deleted), visible tab afterwards is Calendar (adjacent tab
  Zen activates on close). I did NOT run a confirming
  experiment (it would need another open/navigate/close cycle
  with the same misfire risk), so the mechanism is stated as
  the best explanation, not a proven fact.
- Related finding, proven by the two back-to-back lists:
  Marionette window handles are EPHEMERAL per session on this
  Zen: 15 of 15 comparable URLs had a different handle between
  list A and list B one minute apart, and the reported current
  handle differed too. Handles therefore cannot identify tabs
  across sessions, which breaks the runner's phase 6 design
  (restore the owner's tab by stored handle). Tab identity
  across sessions must use URL, not handle.
- What else changed: the 4 about:blank entries in tabs_before
  now resolve to real tabs (Todoist, Calendar, 127.0.0.1:8082
  admin, Codeforces); that is the list scan loading unloaded
  tabs as it switches through them, not new tabs (count stayed
  18). No other URL is missing besides the Muse thread. The
  fixture file was never modified. No input was typed or sent
  anywhere in this task.
- Recovery NOT attempted by me: reopening the exact thread URL
  in a new tab would use the same Marionette open/navigate path
  that just misfired, and a second misfire could navigate or
  close another of the user's tabs. The thread itself lives
  server-side at muse.ai (URL preserved in run-2.json and in
  this log), so nothing is lost beyond the open tab. The
  coordinator decides the recovery path. This is reported here
  in full, not hidden.
- Rule 18:23 was violated in effect by this run (a tab of the owner was closed), through the mechanism above. Recorded
  plainly as my run's incident.

## 7. Phase 3 pre-select + read-only probe

- Not reached in either attempt. No probe program ran, no
  snapshot was taken, no pre-checks ran.

## 8. Phase 4 send program

- Not reached in either attempt. No dom_act ran, no message
  was typed, no Enter was sent. The message
  ZEN-DELEGATE-R2-IGNORE-TEST was never sent anywhere.

## 9. Phase 5 post-checks + P9

- Not reached. No post-checks, no retry check, no delayed
  recount. P9 as specified (screenshot of the sent bubble)
  does not exist because nothing was sent. The two grims that
  do exist (baseline, pill-1) are evidence of the tab state,
  not of a send.

## 10. Phase 6 cleanup and restore

- Attempt 1: cleanup skipped (no scratch handle, nothing
  opened).
- Attempt 2: cleanup skipped by the runner (scratch_handle
  never set), but cmd_open's exception handler closed the
  current window itself. That close is the incident in
  section 6, not a cleanup. Tab count is back to 18, but the
  set is wrong by one (Muse thread gone, no scratch tab left).
  Zen is alive (same window 0x56307e2771d0, ws1, still in the
  clients list at 20:05). The Marionette session slot is free
  (list calls after the run all exit 0). No kill-hung was
  needed. No Zen restart was done or is requested by me.
- Final window map 20:05 +07: Zen 0x56307e2771d0 ws1 (Calendar
  visible); Chromium 0x56307e202df0 ws2 'Pick 4 DOM fixture';
  Chromium 0x56307e7d9bb0 ws2 'Chat - mochi'; Brave
  0x56307e4c2f90 ws2 'Muse - Brave Origin'; OmaCal
  0x56307e5e8200 ws1 (ACTIVE, launched ~20:05 by another lane,
  not by me: PID 132112, I ran no omacal command). The OmaCal
  launch means another lane is active on ws1 now; I touched
  nothing further after seeing it.
- The visible workspace is ws1 (my focus switch) with OmaCal
  now active on top. I did not switch it back: switching focus
  again would be another live action without authorization
  while another lane is active there.

## 11. Verdict

- FAIL (BLOCKED as written, plus a live incident). The Zen
  pointer delegate live proof did NOT pass: no send program
  ran, no P4/P5 criterion was met, no P9 of a sent bubble
  exists. R13 is NOT closed: the R13 condition (lanes idle,
  focus switch authorized) was met in fact and the focus
  switch worked (P1.1 passed in attempt 2), but the proof
  itself could not execute because the procedure's title
  premise is wrong (section 5), and the attempt closed one of
  the owner's tabs (section 6).
- Checklist status: G0a PASS (177 OK), G0b PASS (both programs
  validate), G0c PASS (fixture sha), G0d PASS (fresh intent and
  message), P1.1 PASS (attempt 2, Zen active ws1), P1.2 PASS
  (list ok, 18 tabs, current recorded), P1.3 PASS as fixed
  (resolved geckodriver path exists), P1.4 PASS (fixture sha on
  laptop), P1.5 PASS (live=False, relay idle), P2.2 FAIL (title
  mismatch, procedure premise wrong), all later boxes
  UNTESTED, not failed. Pill: gate 4.29 met before the run,
  leftover holder pill visible in both grims, but no run pill
  ever spawned and the Marionette tab path has no pill cover.
- What the coordinator must decide, in order:
  1. Recovery of the Muse chat tab
     (https://muse.ai/thread/750c8dae-58fb-4a65-82ac-753e78d6ce93):
     reopen it, or leave it to the owner/history. Do not let
     the next runner attempt recovery through the Marionette
     open/navigate path until the mechanism in section 6 is
     understood.
  2. The title fix: target the scratch tab by URL substring
     (two_vision_fixture.html?clone=zen) or by H1 text instead
     of document.title, in zen-tab.py (open gate), the probe and
     send programs (dom_observe target and action scopes), and
     the runner's probe title check; plus a mechanism check that
     POST /window/new actually makes the new tab current before
     any /url navigate or DELETE runs (if it does not, the
     driver must select the tab through Zen's own UI or refuse
     to navigate/close).
  3. Handle ephemerality: stop using stored Marionette handles
     across sessions for restore/close; identify tabs by URL.
  4. Re-run the proof only after 1-3 are landed and reviewed,
     as a fresh run number with a fresh intent/message.
- No self-grading beyond the verdict above, which follows the
  written criteria: PASS requires every R13 criterion live with
  evidence, and none of the send criteria were reached.

## 12. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received 19:55:04 +07. VM HEAD at start 71e807a,
  origin 9ac4dcd; rebased to 394a989 (diff to 71e807a is
  exactly the w-pillverify2-log.md addition, 200 lines).
- Phase 0, 19:56 +07: `python3 -m unittest
  tests.test_zen_pointer tests.test_p2_element_ref
  tests.test_code_exec` Ran 177 tests in 12.992s, OK.
  Fixture sha VM 147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab
  56dcdfc5afb4f72fba6cbf. Programs validate 19:58:56 +07.
- Commit 4f31371 (run 2 runner + log phase 0), pushed,
  ls-remote 4f31371bf8598680498c269a2cb1257aa3580fa8.
  Note: origin had moved to c6e5a2f (Council 1 review of
  W-PILLFIX) between my fetch and commit; my commit landed
  on top cleanly.
- Focus switch 19:59:42 +07: hyprctl dispatch
  "hl.dsp.focus({ workspace = 1 })" ok; activewindow Zen
  0x56307e2771d0 ws1 'Chat - Muse - Zen Browser'.
- Baseline grim 19:59 +07: /tmp/w-zenproof2-baseline.png,
  768335 bytes, Muse chat visible, "S2-flip via CDP" pill
  visible (leftover holder).
- Run 2 attempt 1, 20:00:37 +07, wall 2.7s, outcome error:
  "zen-tab list failed rc=2: can't open file
  '~/c5-zenproof-run/zen-tab.py'". JSON preserved
  as improvements/c5-zenproof-runs/run-2-attempt1.json.
- Runner fix (driver transfer to phase 1), commit cfa687b,
  pushed, ls-remote cfa687bde2efccce72fbc11635982e6a944f918f.
- Run 2 attempt 2, launched 20:01:23 +07, PID 41606, wall
  20.4s, outcome error: "zen-tab open failed rc=1:
  ZenDomError: scratch tab title 'Two-vision benchmark
  fixture' != 'Clone zen thread'". JSON
  improvements/c5-zenproof-runs/run-2.json (also
  /tmp/c5-zenproof-2/run-2.json). tabs_before: 18 tabs,
  current ef90cb33 'Chat - Muse',
  https://muse.ai/thread/750c8dae-58fb-4a65-82ac-753e78d6ce93.
- Pill-1 grim 20:02:13 +07: /tmp/w-zenproof2-pill-1.png,
  796339 bytes, Zen shows Google Calendar, Muse tab absent
  from the sidebar, "S2-flip via CDP" pill still visible.
- List A and B, 20:04 +07:
  improvements/c5-zenproof-runs/zenproof2-list-a.json and
  -b.json, both count 18, identical URL sets, no muse.ai
  URL, 15 of 15 comparable URLs with different handles.
- Fixture source check: <title>Two-vision benchmark
  fixture</title>, H1 set by JS to 'Clone zen thread',
  document.title never set; git log -S 'Clone zen thread'
  and -S 'document.title' on the fixture return nothing;
  fixture last touched by 7f3a70b (brought unedited).
- Final window map 20:05 +07: Zen 0x56307e2771d0 ws1
  (Calendar visible); OmaCal 0x56307e5e8200 ws1 ACTIVE,
  PID 132112, launched ~20:05 by another lane, not by me.
- No input was sent anywhere in this task. No tab was
  navigated by me except through the attempt 2 open sequence
  described in section 6. No Zen restart, no kill-hung.
