# R3-L3 fix-integration review: council reviewer 3 of 3 (27/11/2026)

Independent review. Run closed 04:49 27/11 at Rule-A 52 PASS / 1 FAIL.
Method: verified the evidence pack against primary sources (run logs,
state file, checker source, brief template, overlay source, daemon log,
watch log, error tracker full text, improvements files 25-27/11).
Ponytail applies to every code sketch below: smallest complete change,
reuse first, one small test for non-trivial logic.

Verdicts: integrate-now means land it in the post-run batch with a test.
Defer means real but blocked on diagnosis, an owner decision, or another
owner. Reject means do not do it (done already, duplicated, or wrong).

## 1. Ranked candidates

Rank order is by impact first, then risk. C1-C14 are pack candidates.
C15-C22 are new candidates found in this deep read.

### C2. State-file task_start / runner_pid gap - RANK 1
- Impact: H. Prevents the worst failure in the run record: a timeout
  watch killing a live idle session on stale fields, and the opposite
  failure, a drive that cannot be killed at all. Both happened.
- Risk: M. A watch that treats completed tasks as not running could
  mask a real hang if the completion signal is wrong. Mitigate by
  checking two signals (per-task row exists OR drive-end recorded)
  and by clearing fields only at drive end.
- Evidence: per-task report R3-078 honest record (26/11 22:20 drive,
  no task_start or runner_pid recorded, watcher had no PID);
  state notes 25/11 (stale task_start cleared by emergency fix so the
  watch would not kill the persistent FCC pane PID 22399 at the
  30-minute mark; stale codex fields PID 302252 cleared the same way);
  per-task R3-056 (drive stopped at about 73 minutes, overrun
  recorded). Current state file still carries task_start and
  runner_pid fields, both null at closure.
- Verdict: integrate-now. One state-write helper used at every task
  start and drive end, plus the watch-side completed check. Test:
  stale-field fixture must not kill, missing-PID fixture must alert.

### C9. No fail-closed pill gate in BiDi driver path - RANK 2
- Impact: H. The pill must show on any agent control. The BiDi path
  today relies on a manual wrapper. A worker that forgets it drives
  invisibly. That is a trust breach, not a cosmetic bug.
- Risk: M. Fail-closed can block legitimate drives when the pill is
  flaky. The CDP path already proves the pattern works, so reuse it
  rather than inventing a second gate.
- Evidence: scripts/zen_dom.py and scripts/zen_cli.py contain zero
  overlay or pill references (verified 27/11); scripts/cdp.mjs lines
  5-16 implement the fail-closed gate (acquire first, refuse with
  CDP pill unavailable, one documented opt-out). Fix B holder notes
  confirm the BiDi drive acquires the pill manually per drive.
- Verdict: integrate-now. Acquire and release inside BiDi session
  start and stop, fail-closed, mirroring cdp.mjs. Test: unwrapped
  drive must fail or auto-wrap, wrapped drive must show the pill.

### C3. Keybind-first hard rule missing from repo brief template - RANK 3
- Impact: H. Every future brief inherits this template. The rule is
  the main speed lever (command and keybind first, vision only as
  cross-check) and it is currently absent where workers actually read.
- Risk: L. Text change plus one checker line. No behavior change.
- Evidence: docs/brief-template.md (138 lines) grep for keybind,
  vision, screenshot returns empty (verified 27/11, exit 1).
  scripts/brief_check.py (96 lines) checks the ydotool ban only, no
  keybind rule. Machine layer was fixed 27/11 per pack (keybinds and
  fastest-paths files on the laptop, not re-verified here).
- Verdict: integrate-now. Add the hard rule to the template and one
  matching check to brief_check.py so the rule is machine-enforced,
  not advice. Repo text stays generic.

### C15. Cloudflare webdriver shim holder is ephemeral (NEW) - RANK 4
- Impact: H. This shim was the resume gate for four run sites. It
  lives only in /tmp on the laptop by design. A reboot or cleanup
  loses the only proven Cloudflare workaround, and the next run
  re-discovers it from zero.
- Risk: M. Known fingerprint difference (getter toString empty-name
  form) is accepted and recorded. Single remote-session slot means a
  leaked holder blocks all DOM work for about 9 minutes. Both risks
  are documented in the Fix B record with mitigations.
- Evidence: improvements/replan-fixes-cloudflare-live-20261126.md
  sections 1-4 (pinned shim hash, held-out drive PASS 26/11,
  three integration bugs found and fixed live); section 8 states no
  repo files were edited and the harness is /tmp only. The pack
  omits this candidate entirely.
- Verdict: integrate-now as preservation, not as default-on code.
  Land the three harness files as an opt-in helper (default off,
  for example an env flag) with the hash pin and probe, and record
  the per-lane start and stop discipline in the brief template.
  Do not unify the classic Marionette lane in the same change.

### C8. overlay.py release bug: pill stuck visible - RANK 5
- Impact: M. Status lies in the safe direction (stuck on), but the
  owner sees a pill with no driver and every verify lane must
  second-guess status output. Manual clears were needed mid-run.
- Risk: L. One missing hide call on one owner path, plus a cycle
  test. No other behavior changes.
- Evidence: scripts/overlay.py apply_holders empty-holders branch
  sends hide only when owner is daemon; the serve finally block does
  the same. When owner is session, no hide is ever sent to the
  session indicator (session_label only shows, there is no session
  hide helper). Pack daily-note evidence 25/11 (stuck at 10:59 and
  11:01, cleared manually 11:03:16) matches this code shape.
- Verdict: integrate-now. Send hide on final release for the session
  owner too. First confirm the indicator accepts a hide request;
  if it does not, record that and use the documented session-end
  path instead. Test: acquire and release cycle ends pill-gone,
  verified by screenshot.

### C1. Heartbeat-log writer lapse - RANK 6
- Impact: M. About 2.5 hours of false liveness alarms every 5 minutes
  trains everyone to ignore the alarm that matters.
- Risk: L. Either fix option is small. Prefer writing the heartbeat
  on every state update (one writer, one truth) over teaching the
  watch a second signal.
- Evidence: rung3-run-log/r3-l3-heartbeat.log last line
  2026-11-27T02:18:50+07:00 (199 lines) while state last_updated is
  2026-11-27T04:48:07+07:00 and per-task rows continue to 04:48.
- Verdict: integrate-now, folded into the C2 helper. Do not fix C1,
  C2, C12 as three separate changes; they are one signal-hygiene
  defect with three symptoms.

### C12. Per-task report file not written early in run - RANK 7
- Impact: M. Same cluster as C1 and C2. A reporting chain that masks
  a missing file defeats the purpose of the file.
- Risk: L. Checklist line plus watch trigger change.
- Evidence: pack daily-note 25/11 (zero rows, stale mtime, AND-rule
  masked it). Current file has 132 lines to 04:48 27/11, so writing
  resumed; the trigger logic, not the writer alone, is the defect.
- Verdict: integrate-now, folded into C2. Write the row at grade
  time; change the watch trigger to OR with a grace window.

### C17. Act-now silent fallback to captured screen observation (NEW) - RANK 8
- Impact: H. This is the proven mechanism behind the largest error
  class in the tracker (click misses from coordinate-space shift).
  A stale given observation silently becomes a screen observation,
  window-space points execute in screen space, the click misses by
  the window origin offset, and the envelope still reads success.
- Risk: M. Failing loud will increase refusals until workers learn
  the fresh-observe discipline. That is the correct trade: a refusal
  is recoverable, a silent miss is not.
- Evidence: tracker J35 (window region 1863x1176 vs monitor
  1920x1200, offset about +45,+12) and J40 (about 3-minute
  observe-act gap, source captured not given, click missed, no
  error). Same class as tracker G28 and G30. The pack does not list
  this candidate.
- Verdict: integrate-now. Refuse or auto-convert when the envelope
  source is captured and the point was window-space; require the
  source check in the brief template. Test: stale-observation
  fixture must refuse, fresh fixture must pass.

### C11. Recurring drive anomalies (machine-layer knowledge gaps) - RANK 9
- Impact: M. Each item recurred 2-4 times and cost minutes per
  drive. Together they are the largest repeatable time sink after
  the signal cluster.
- Risk: L. Documentation only, laptop layer. No code risk.
- Evidence (verified in per-task reports): Super-only key refused
  4 times (R3-075, R3-076, R3-078, and one more), fix Super+Space;
  duplicate stdin redirects killed launch twice (R3-075, R3-076);
  Alt+F4 does not close Kitty or Foot (R3-072 area, R3-078), fix
  Ctrl+D or Super+Q; driver launch SSH broken pipe about 36s
  recurred and is benign (detached runner alive); colon refused as
  unsupported XKB in nvim (R3-078); dock click opened the wrong
  panel and file picker stuck in /tmp (R3-078). Pack understates
  two items: session driver exited mid-drive twice (R3-072 Unknown
  process id, R3-076 session ended about 21:41 with about 10-minute
  wait), and screen-changed refusals plus an unsaved-tab hazard
  recur without a written rule.
- Verdict: integrate-now (laptop fastest-paths and keybinds files).
  Add generic lines to the brief template only where they are not
  machine-specific (single stdin redirect on launch, fresh observe
  after any session restart). Keep machine specifics off the repo.

### C16. Tier A checker remaining brittleness plus missing tests (NEW) - RANK 10
- Impact: M. Two more Tier A FAILs needed human override after the
  json-errors fix. Each one costs a tiebreaker or scorer time.
- Risk: L. Test file only, plus narrow parser broadening if the
  tests prove a miss. Union-style broadening cannot turn a PASS
  into a FAIL.
- Evidence: per-task R3-021 (Tier A FAIL was a CSV header-assumption
  parse miss, tiebreaker PASS) and DP-02 (Tier A FAIL on per-file
  detail lines, judged beyond pass criteria). No test file exists
  for tier-a-check.py (only test-keys.json). The pack covers only
  the json-errors instance (C4).
- Verdict: integrate-now. Add one small test file covering
  json-errors in both languages plus the R3-021 and DP-02 shapes,
  with a mutation control (wrong values must still FAIL).

### C19. Focus-theft guard codification (NEW) - RANK 11
- Impact: M. One drive was interrupted by a foreign window stealing
  focus. The runner stopped correctly, but only because that brief
  happened to carry the rule.
- Risk: L. Brief-template line now, driver check later.
- Evidence: state note R3-046 attempt 1 (26/11 about 17:15, untitled
  docs window became active, act-now refused, runner stopped, no
  grade). The decision recorded there (focus-verify before each act)
  was applied to that re-run brief only. Pack C6 covers cleanup of
  the window, not prevention.
- Verdict: integrate-now (template line: verify holder window focus
  before each act batch, stop and report on focus theft). Driver
  enforcement is a follow-up, not part of this change.

### C21. Preflight park-move rule correction (NEW) - RANK 12
- Impact: M. The current park rule both causes and cures screen-
  changed refusals depending on background. Workers cannot follow
  contradictory guidance.
- Risk: L. Documentation correction with the proven condition.
- Evidence: tracker J36 (park at 500,600 proven fix) and J37 (park
  move itself trips the patch threshold on photographic backgrounds,
  mean 6.627 vs threshold 6; fix is to drop the park move and park
  only when the next point equals the cursor position, on a flat
  light area). The pack does not list this.
- Verdict: integrate-now (machine layer plus one generic template
  line). Keep J36 and J37 together; neither alone is the rule.

### C18. Ctrl+Shift+T guard over-broad (NEW) - RANK 13
- Impact: L. Reopen-closed-tab is unusable via computer-use today.
  Narrow but real: recovery from a wrong close needs it.
- Risk: L. Narrow the match to bare Ctrl+T without Shift. One test.
- Evidence: tracker J43 (Ctrl+Shift+T refused twice with the Ctrl+T
  message, deterministic). Brief template section 7 already states
  the Ctrl+T rule correctly; the driver guard is broader than the
  rule.
- Verdict: integrate-now.

### C6. Foreign untitled docs window cleanup on ws2 - RANK 14
- Impact: L. One leftover window. Operational, not systemic.
- Risk: M if done carelessly (closing the wrong window violates the
  never-close-owner-tabs rule). L with verification first.
- Evidence: state note R3-046 attempt 1 (window active from about
  17:15 26/11); runner brief R3-067 line 75 warns drivers about it;
  pack owner photo 04:22 27/11. Run is closed, so the mid-drive
  freeze no longer applies.
- Verdict: integrate-now as ops cleanup. Verify by title and window
  list that it is the foreign untitled document, close only it,
  re-list to confirm. No code.

### C10. Speed-daemon repeated deaths - RANK 15
- Impact: M. Messaging gaps stall scorer coordination. The daemon
  is on the critical path for verdict traffic.
- Risk: M. Cause is unknown. A blind robustness change can hide the
  cause and still die.
- Evidence: daemon.log contains 45 daemon_start events from 23/11
  to 27/11 (pack lists about 9 in the run window; the full log is
  worse). Starts cluster at roughly 2-hour intervals on 24/11 and
  continue through 27/11 03:42. A supervisor exists on paper
  (supervisor.sh, 60-second watchdog loop) but supervisor.log is
  0 bytes, so there is no evidence it ran or logged. No death
  reason is recorded in daemon.log (starts only, no exit events).
- Verdict: defer pending diagnosis. First instrument: log exit
  reason and supervisor heartbeat, then fix the proven cause.
  Do not add a second supervisor on top of an unproven first one.

### C20. Zen memory growth and boundary restart policy (NEW) - RANK 16
- Impact: M. At the observed rate the browser exhausts available
  memory in about 4 hours. Any long run hits this.
- Risk: M. Restarting mid-drive loses session state. The proven
  procedure is boundary-only, which must be enforced, not advised.
- Evidence: state notes 25/11 (RSS 5.50 GB at 16:27, 6.76 GB at
  16:42, 8.11 GB at 16:58; restart at task boundary dropped RSS
  from 7950 MB to 978 MB, ports and session restore verified).
  The pack does not list this candidate.
- Verdict: defer. Add RSS to the existing health watch first
  (observe one full cycle), then codify the boundary-only restart
  with a threshold. No auto-restart code in this batch.

### C22. Marionette and BiDi session hygiene (NEW) - RANK 17
- Impact: M. Session-slot wedges block all DOM work and the only
  proven fix is a browser restart. Recurrence is proven.
- Risk: M. The minimal trigger was never isolated (Arm F owed).
  Fixing without it risks a rule that does not cover the trigger.
- Evidence: tracker J3 and J22 (browserElement null wedge 3 times,
  Arms A-D pass, Arm E full-sequence fails, restart proven 3 of 3;
  standing rule: never close tabs by Marionette DELETE in batches,
  never close blank tabs by Marionette); tracker J49 (session sticks
  to privileged context after about: pages, workaround is window
  title plus visual count). Fix B notes add the about 9-minute leak
  reap and switch timeouts.
- Verdict: defer. The standing rule already prevents the known
  trigger shape. Schedule Arm F and the privileged-scope repro as
  one bounded experiment before any code change.

### C14. Answer-key freshness (R3-004) - RANK 18
- Impact: L. One task, both scorers accepted on substance. Cost was
  scorer judgment time, not a wrong grade.
- Risk: L. Process check at freeze time.
- Evidence: per-task R3-004 note (live go1.27.4 vs key go1.14.3,
  both scorers PASS on substance). Verified.
- Verdict: defer to next freeze. Add a version-sensitive key check
  to the freeze checklist. No action for the closed run.

### C5. Zen folder and tab operations without vision - RANK 19
- Impact: M. Task 56 took about 73 minutes and overran. Folder
  operations remain vision-heavy with no API.
- Risk: M. Duplicating the parallel research wastes the scarcest
  resource (laptop verification time) and can land two conflicting
  mechanisms.
- Evidence: per-task R3-056 PASS 27/11 04:48 on owner inspection
  with overrun recorded, so the run no longer blocks on this.
  Pack states parallel research was ordered 04:34 27/11. No API
  for folders exists (BiDi does not expose them).
- Verdict: defer. Integrate only what the parallel research plus
  throwaway-profile verification proves. This review adds nothing.

### C13. Ledger-push watch blocked - RANK 20
- Impact: L for the closed run. The ledger is complete and pushed.
  Impact would be M for a future run if the gate stays flaky.
- Risk: M. Changing how pushes run touches the evidence chain.
  That is an owner-shaped decision, not a council fix.
- Evidence: watch log shows intermittent blocking, not a hard stop:
  OK at 23:48 26/11, blocked 00:48, OK 01:48, OK 02:48, blocked
  03:48, blocked 04:47 27/11. Pack claim of last OK 23:48 is
  therefore overstated (see section 3).
- Verdict: defer to the owner. Options (fallback API path, watch
  retirement at run close) need an explicit decision. Recommend
  disabling the watch for the closed run either way to stop noise.

### C4. Tier A checker bilingual parse - RANK 21 (REJECT, already done)
- Impact: none remaining. The fix landed during the run.
- Risk: L if re-done, but re-doing it risks touching graded-task
  behavior for no gain.
- Evidence: rung3-ci/tier-a-check.py check_json_errors unions 4
  patterns (Vietnamese plus 3 English forms, case-insensitive).
  Commit 4db97480 (25/11) and state note OWNER INSTRUCTION 21:20
  record the change, verified both ways (re-run snapshot now PASS,
  original still FAIL on values). Pack cites the pre-fix regex.
- Verdict: reject as a fix. The only remainder is regression tests,
  counted under C16.

### C7. Pill label unification - RANK 22 (REJECT here, owned elsewhere)
- Impact: L. Label text only. The pill itself works.
- Risk: L, but duplicate work by two owners on overlay code is the
  real risk.
- Evidence: pack records the owner sighting 17:16 26/11 and the
  re-confirmed rule 17:41 (only Computer use active), assigned to
  a separate independent worker. Per-task R3-072 notes the label
  fix stays queued post-run per that decision.
- Verdict: reject in this batch. Note status only, do not duplicate.

## 2. Error-tracker recount

File: cf26-upload/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md, 905 lines.

Counting method: one item per numbered heading matching
A, B, C, D, E, G, H, I, J plus a number. Structural headings
(scope, context, conclusions) are not items. Section F bullets
(7 owed items, unnumbered) are counted separately.

Heading recount (verified by grep 27/11):
- A1-A9: 9. B1-B14: 14. C1-C8: 8. D1-D5: 5. E1-E3: 3.
- G1-G24 plus G27-G31: 29 (G25 and G26 do not exist in the file).
- H1-H3: 3. I1-I46: 46. J1-J50: 50.
- Total numbered items: 167. Total headings including structural: 185.

Memory figure check: 121 done / 17 open / 138 total is exact for
the scope A1 through J21 (117 items A-I plus 21 items J1-J21 equals
138). The file grew by J22-J50 (29 items, night of 21-22/11)
outside that scope. Full-file recount: 144 done / 23 open / 167
total at heading level. H2 and J10 describe the same work
(think-time); merged as work items the full file is 144 done /
22 open / 166. Section F adds 7 owed bullets, all still owed or
historical, counted outside the 167.

Open definition: the file text explicitly says not yet determined,
not yet proven, under investigation, needs experiment, paused,
still owed, or partial. Everything else with a recorded fix,
rule, or proven workaround counts as done (as knowledge; code
follow-ups are called out below).

Still-open items (heading level, 23):
- E3 speed program paused. G10 pill shape temporary default.
  G11 pill blur and refraction still to increase. G12 coordinate
  accuracy program. G13 think-observe loop program.
  G28 follow-up (auto window observation for typing batches) not done.
  G29 urlbar click hypothesis unproven, 4 discriminating probes owed.
- H1 flicker cause unverified. H2 think-time unmeasured (partial).
  H3 click-miss root not closed in file (later narrowed, see below).
- J8 history scrub not run. J9 hidden-body experiment plus
  follow-ups owed. J10 same work as H2. J13 snippet Phase A block.
  J14 checker follow-ups owed. J15 input freeze cause unknown.
  J16 watchdog log missing. J17 PR conflicting (file state;
  not re-verified here).
- J26 Ctrl+Tab switch hypothesis untested. J34 PDF toolbar has no
  download button (known limit, scenario failed). J43 guard
  over-broad (candidate C18). J49 privileged-scope stickiness
  (candidate C22).

R3-L3 evidence against tracker items:
- Proven still live: A7 and A8 (do not invent, verify claims).
  Rules were recorded, yet fabrication recurred on three early
  tasks 25/11 (state escalation note, epoch 5). Rules alone did
  not prevent it; lane reassignment did. Treat as process risk,
  not closed by documentation.
- Proven still live: H3 click accuracy. Root narrowed by G30 and
  G31 to vision grounding error (30-50px on compressed images,
  clicks accurate to 0-1px) and by J35 and J40 to coordinate-space
  shift. No calibration fix is proven. Candidate C17 addresses the
  silent-fallback half. The grounding half remains open.
- Proven still live: G28 class (screen observation cannot type).
  Recurred as J32 and J40 during the run window. Workaround known
  (window observation), auto-fix still owed.
- No R3 evidence either way: H1 flicker (zero flicker reports in
  per-task log; pill verified visible and gone repeatedly, which
  proves the pill path works but does not prove the flicker cause
  is gone). H2 think-time (drive durations recorded, think time
  never instrumented). J9, J13, J14, J15, J16, J8 (untouched by
  the run). J17 (not checked).
- Superseded by later evidence: J12 (clone1 report missing) is
  closed in practice by the calibration approval recorded 26/11
  (per-task calibration row, 4 of 4). J23 (workspace by command)
  is closed by the proven hl.dsp.focus form recorded in workspace
  lessons 21/11. E1 (deliberation split) is closed per J11 itself.
  E2 (Firefox automation research) is closed in practice: the BiDi
  driver exists and ran the whole run.

## 3. Pack claims found wrong or overstated

1. C4 is wrong. The checker is already bilingual (4 patterns,
   commit 4db97480, 25/11, state note 21:20 with two-way
   verification). The pack quotes the pre-fix single regex and
   presents the fix as owed. Integrating C4 again would be a no-op
   at best. Remainder moved to C16 (tests).
2. C13 is overstated. The watch was intermittently blocked, not
   stopped. Watch log: OK 23:48 26/11, blocked 00:48, OK 01:48,
   OK 02:48, blocked 03:48 and 04:47 27/11. Last OK is 02:48, not
   23:48.
3. C10 is understated. Daemon log holds 45 starts (23-27/11), not
   the about 9 listed. A supervisor script exists but its log is
   empty, so pack wording (add a supervisor) misdiagnoses the gap:
   the gap is unproven supervision plus unlogged deaths.
4. Tracker figures lack scope. 121/17/138 covers A1-J21 only.
   Full file is 167 numbered items. Any integration plan sized on
   138 undercounts J22-J50, which contain two live code candidates
   (J43, J49) the pack misses.
5. C1, C2, C12 are one defect split into three candidates.
   Fixing them separately risks three partial helpers. This review
   folds them into one state-write helper (C2 first).
6. C11 understates session-driver exits. Two mid-drive exits are in
   the per-task log (R3-072, R3-076), one with an about 10-minute
   wait. The pack lists the class once without recurrence.
7. C5 omits closure. Task 56 passed 27/11 04:48 (owner inspection,
   overrun recorded). The candidate is real but no longer blocking.
8. C2 detail partially unverified. The 70-plus-minute unkillable
   figure for task 56 has no file pointer in the pack. The 73-minute
   overrun is verified (per-task R3-056); the null-PID duration is
   plausible from closure state but not independently timed here.
   The R3-078 and 25/11 stale-field evidence carries C2 without it.

No other pack claim failed verification. C1 lapse, C3 empty grep,
C6 window, C8 code shape, C9 missing gate, C14 version drift, and
the C11 anomaly list (as far as it goes) all check out.

## 4. Top 5 to integrate first, in order

1. C2 with C1 and C12 folded in (state-write helper plus watch
   completed check). Safety first: wrong-kill and unkillable-drive
   are the only candidates that can destroy live work.
2. C9 (BiDi fail-closed pill gate, mirroring cdp.mjs). Owner hard
   rule, proven pattern to copy, no new design needed.
3. C3 (keybind-first rule in template plus brief_check line).
   Cheapest high-leverage change; every future brief benefits.
4. C15 (preserve the Cloudflare holder as opt-in helper with hash
   pin and probe). Proven live, currently ephemeral; preservation
   is urgent before any laptop cleanup or reboot.
5. C8 (session-owner hide on final release plus cycle test).
   Small, self-contained, removes a lying status signal.

Next after the top 5: C17, then the documentation batch (C11, C19,
C21), then C16 tests and C18. C10 and C20 wait for diagnosis data.
C13 waits for the owner. C4 and C7 are not done in this batch.
