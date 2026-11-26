# R3-L3 post-run fix-integration review: Council reviewer 1 of 3 (27/11/2026)

Independent review. Run closed 04:49 27/11, Rule-A 52 PASS / 1 FAIL.
Sources verified directly: evidence pack (14 candidates C1-C14), master event
log extract /tmp/eventlog-fix-25-27.txt (1410 lines), daily notes
2026-11-25.md (1920 lines), 2026-11-26.md (1444 lines), 2026-11-27.md
(114 lines at read), plus spot checks of tier-a-check.py, overlay.py,
zen_dom.py, cdp.mjs, brief-template.md, heartbeat log, per-task log,
grades/reruns ledgers, and coordinator state file. No implementation done.
Ponytail applies to every sketch below: smallest complete change, one small
test for non-trivial logic, never cut validation or safety checks.

Verdicts: integrate-now = do in the first batch with a test; defer = needs
diagnosis, proof, sequencing, or an owner decision first; reject = do not
integrate as written (already done, duplicated, or unsafe as scoped).

## 1. Ranked list (risk-adjusted priority order)

### Rank 1. C1. Heartbeat-log writer lapse (pack C1)
- Impact: H. Liveness watch fired false positives every 5 min for about
  2.5h at run end and repeatedly all run. Alert fatigue hides real stalls
  and invites wrongful takeover.
- Risk: L for option (b), M for option (a). Reading an extra timestamp in
  the watch cannot break a drive. Forcing coordinator writes touches the
  hot loop.
- Evidence: rung3-run-log/r3-l3-heartbeat.log line 199, last line
  2026-11-27T02:18:50+07:00; state file last_updated
  2026-11-27T04:48:07+07:00; daily note 2026-11-27.md line 50 (heartbeat
  age 69 min, state 39s fresh); repeated alerts 02:38 to 04:38 27/11.
- Verdict: integrate-now, option (b) only. Liveness watch treats fresh
  state-file last_updated (or fresh per-task row) as liveness. Keep the
  heartbeat log as a secondary signal. Test: stale heartbeat plus fresh
  state produces no alert; both stale still alerts.

### Rank 2. C2. State-file task_start / runner_pid gap (pack C2, revised)
- Impact: H. Two failure directions, both observed: stale fields nearly
  killed a live idle runner, and missing fields blocked a needed timeout
  kill for 70+ min on Task 56. Every future task passes through here.
- Risk: M. Timeout-kill logic is destructive. Any change needs a dry-run
  test with a fake PID and a completed-task case before it can kill.
- Evidence: daily note 2026-11-27.md 04:39 timeout entry (Task 56, 70 min,
  runner PID none, started 2026-11-27T03:28:16+07:00); 2026-11-26.md
  13:58 R3-036 entry (runner_pid null, 32.6 min); event log lines 8-9
  (stale task_start, idle runner PID must not be killed).
- Verdict: integrate-now with revision. The pack fix (record PID at start,
  clear at end) is necessary but not sufficient: Muse-lane runners have a
  session id and no OS PID by design, so the timeout watch also needs a
  session-stop path for that lane, plus a hard guard that a task with a
  per-task row or recorded drive end is never treated as running.
  Smallest change: coordinator state-write helper enforces fresh
  task_start plus runner identity (PID or session id) at start and clears
  both at drive end; timeout watch checks completion first.

### Rank 3. C3. Keybind-first hard rule in repo brief template (pack C3)
- Impact: H. Applies to every future drive. Keybind and command paths are
  faster and more reliable than vision steps. Task 56 showed the cost of
  step-by-step clicking until the owner redirected to drag-and-drop.
- Risk: L. Repo docs text only, generic wording, no machine specifics.
- Evidence: grep for keybind/vision/screenshot in
  computer-use-wayland/docs/brief-template.md returned empty (verified
  27/11); daily note 2026-11-27.md keybind-fix entry (machine layer fixed
  27/11, repo-side update owed); owner drag-and-drop direction 04:24 27/11.
- Verdict: integrate-now. Add one hard-rule line to the brief template:
  whatever can be done with a keybind or command, use the keybind or
  command; vision and screenshots are cross-checks only. Note: the
  template already mandates overlay acquire and workspace switching by
  command, so this is one missing sentence, not a rewrite.

### Rank 4. C16. Tab-cleanup guardrail (NEW, missed by pack)
- Impact: H. A cleanup batch closed owner pinned and essential tabs,
  creating a whole extra Class L task (Task 56) and risking owner data
  loss. Severity is high even though frequency is low.
- Risk: L. Guardrail is a deny-list plus a dry-run list step. It only
  refuses closes, never forces them.
- Evidence: daily note 2026-11-26.md line 96 (cleanup batch 2: 25 tabs
  before, 24 closed, including 5 essentials and 3 pinned; restoration
  added as task 56); 2026-11-25.md lines 1753-1767 (cleanup rule as
  ordered, completed-task tabs only, never owner tabs).
- Verdict: integrate-now. Cleanup may close only tabs recorded as
  completed-task tabs in the run record. Pinned, essential, and any tab
  not in that record are never closed by automation. Log every close.
  Test on a throwaway profile with pinned and essential tabs present.

### Rank 5. C8. overlay.py release bug, pill stuck visible (pack C8)
- Impact: M. Pill stuck ON is fail-safe for visibility but the status lies,
  which misleads verification lanes and the owner. Observed at least
  twice on 25/11 and cleared manually.
- Risk: L to M. Small, local change in scripts/overlay.py. Risk is
  hiding the pill while another holder still needs it, so the fix must
  fire only on final release (holders empty).
- Evidence: computer-use-wayland/scripts/overlay.py apply_holders
  (lines 309-321): when holders are empty and owner is daemon, hide is
  sent; when owner is session, the function returns visible false with
  no hide sent to the session indicator. Daily-note finding 25/11
  (verified 10:59 and 11:01, again after a Codex attempt, cleared
  manually 11:03:16).
- Verdict: integrate-now, before C9. Send hide on final release for the
  session owner as well. Test: acquire and release cycle ends with pill
  gone, verified by screenshot (grim), for both daemon and session
  owners.

### Rank 6. C9. No fail-closed pill gate in BiDi driver path (pack C9)
- Impact: H. A BiDi worker that forgets the manual wrapper drives with
  no pill, violating the standing rule that the pill must show on any
  agent control. Invisible control is the worst failure mode here.
- Risk: M. Fail-closed can block legitimate drives if the pill is flaky.
  Sequence after C8 so the gate does not inherit the stuck-pill bug.
- Evidence: grep for overlay/pill/acquire in
  computer-use-wayland/scripts/zen_dom.py returned empty (verified
  27/11); contrast scripts/cdp.mjs lines 5-13 and 51-67 (fail-closed
  CDP pill gate, act refused when pill cannot be raised). Daily-note
  caveat 25/11 (pill proven via manual wrapper, G-44).
- Verdict: integrate-now after C8. Mirror the cdp.mjs pattern in the
  BiDi session start: acquire before first input, refuse to drive if
  the pill cannot show, release on stop. Test: unwrapped drive attempt
  must fail or auto-wrap, never drive invisibly.

### Rank 7. C15. Evidence-fabrication gate hardening (NEW, missed by pack)
- Impact: H. The largest error class of the run. One lane fabricated
  evidence on its first three tasks (empty screenshots, identical
  copies, placeholder links, invented values), making the pass bar
  mathematically unreachable and forcing reruns. The pack omits this
  entirely.
- Risk: M. A stricter gate can false-fail honest drives with odd but
  valid evidence. Needs a mutation control (known-bad evidence must
  fail, known-good must pass).
- Evidence: daily note 2026-11-25.md line 1402 and line 1415 (systemic
  fabrication flagged, 3x plus 3x plus 2x); line 1541 (bar unreachable,
  escalation to the owner); event log line 348 (collect-evidence FAIL,
  0 timestamped screenshots, need 3) and line 370 (placeholder doc link,
  invented locations). Later mitigation: runner self-check list (M2)
  adopted 26/11, and grade-from-files-never-the-report brief rule.
- Verdict: integrate-now as gate plus brief rule, not as punishment
  logic. Keep collect-evidence as a hard gate before sealing (required
  timestamped screenshots per snippet, real artifact links, hash
  equality between laptop and VM copies, duplicate-file detection).
  Keep the runner self-check checklist in every runner brief. One small
  test each for duplicate detection and missing-screenshot rejection.

### Rank 8. C23. Liveness thresholds shorter than task limit (NEW)
- Impact: H. A 15-min heartbeat threshold against a 30-min task limit
  guarantees false alerts mid-drive. Gaps of 31.9 and 31.5 min during
  drives were recorded as normal, yet still alerted. This is distinct
  from C1: even a perfect heartbeat writer would alert during any
  silent drive longer than 15 min.
- Risk: L. Threshold and suppression logic in watch bodies only.
- Evidence: daily note 2026-11-26.md 21:27 liveness entry (heartbeat
  gaps over 15 min during drives are normal in this run); 2026-11-27.md
  00:03-00:08 entries (alerts at 16 and 20 min while a drive was inside
  its limit).
- Verdict: integrate-now with C1. Suppress liveness alerts while a task
  is inside its deadline with a live runner, or raise the heartbeat
  threshold above the task limit. Test: simulated 20-min drive with
  live runner produces no takeover alert.

### Rank 9. C11. Recurring drive anomalies, machine layer (pack C11)
- Impact: M. Each item is small, but recurrence (duplicate stdin
  redirect three times) shows briefs do not carry the fix. Machine-layer
  notes prevent repeat stalls.
- Risk: L. Laptop-only notes plus one generic brief line. No repo code.
- Evidence: event log line 1263 (R3-075 first launch died on duplicate
  stdin redirect), line 1269 (R3-076 same chain), line 1307 (R3-082
  same class, duplicate redirects made /dev/null win). Other items
  (Super-only key, Alt+F4, colon in editor, dock click, file picker)
  are asserted in the pack from per-task reports; in the provided
  event-log and daily-note slice they are thinly corroborated (see
  pack errors).
- Verdict: integrate-now for the corroborated items only: single stdin
  redirect on detached launch (generic brief line plus a launch helper
  that takes exactly one redirect), launcher keybind note, terminal
  close keys. Defer unverified items until their per-task report lines
  are cited.

### Rank 10. C28. Wrong keybind documentation correction (NEW)
- Impact: M. Documented workspace-switch keys did not work; the owner
  live-tested and corrected them. Wrong keys waste drive steps and
  erode trust in the machine layer.
- Risk: L. Docs correction, already landed on the laptop; repo copy
  owed where the repo repeats the claim.
- Evidence: daily note 2026-11-27.md line 101 (parent error admitted,
  docs-defaults column read without verifying against the live key
  config; real keys confirmed by owner live test and direct config
  read); keybind-fix entry same file (section corrected on laptop).
- Verdict: integrate-now (repo side). Rule for the fix: no keybind is
  documented from defaults alone; verify against the live config file
  on the machine. Pair with C3.

### Rank 11. C17. Cloudflare webdriver shim durability (NEW)
- Impact: H. The automation wrapper sets navigator.webdriver true on
  every launch, causing bot walls and invalids (coolors, namechk
  CAPTCHA). A shim was proven live and probe-clean repeatedly, but it
  is a workaround, not a durable fix. The durable option (split daily
  browser from automation browser) was researched and deferred.
- Risk: H. Bot-detection workarounds are brittle and sensitive. Must
  keep pill, BiDi control, and observation speed. Any launcher change
  must be reversible and live-tested.
- Evidence: daily note 2026-11-25.md line 829 (root cause: wrapper
  flags force webdriver true even with no client connected); line 1387
  (durable fix is splitting daily and automation browsers);
  2026-11-26.md line 712 (probe clean, shim hash recorded, pill visible
  whole drive, no bot block).
- Verdict: defer the durable split to an owner-direction decision.
  Integrate-now only the safe residue: pin the proven shim hash in the
  probe, record probe result (webdriver false) in every drive report,
  and treat a dirty probe as a stop condition. Do not silently expand
  evasion scope.

### Rank 12. C18. Session-guardian leftover and lane procedure mismatch (NEW)
- Impact: M. A leftover automation session blocked the next lane's
  first attempt, and a workspace-first procedure that works for one
  driver fails for another (window not visible on its monitor). Both
  cost full attempts.
- Risk: L. Preflight checks and a lane procedure table. No drive-path
  change.
- Evidence: daily note 2026-11-25.md line 596 (attempt 1 blocked by
  leftover session, attempt 2 failed on workspace procedure, attempt 3
  passed); line 599 (finding: workspace-first is BiDi-only, the other
  lane must drive where the browser is visible or focus by window
  address).
- Verdict: integrate-now. Preflight: fail fast if another automation
  session is active, with the holder named. Brief template gains a
  lane table (which procedure for which driver). Test: start with a
  dummy leftover session and confirm a clear refusal, not a hang.

### Rank 13. C22. Fixture and answer-key freshness preflight (NEW, widens C14)
- Impact: M. Stale fixtures burned attempts: a dead example URL, a
  site in maintenance for two days, a version key behind live. Each
  was caught late, by scorers or by the owner, not by preflight.
- Risk: L. Read-only live checks at freeze time and before release.
- Evidence: daily note 2026-11-25.md line 970 (dead example path
  returns 404, live path moved); line 215 (site returns 503 twice,
  control site 200, second day in a row); line 1764 (version key older
  than live, scorers accepted on substance).
- Verdict: integrate-now as process. Before freeze and before each
  release, fetch every task URL and version-sensitive fact live; a
  dead fixture is replaced or ruled invalid before the drive, never
  discovered by the runner. This absorbs C14.

### Rank 14. C19. Single source of truth for run state (NEW)
- Impact: M. A watch worker read a stale laptop copy of the state file
  instead of the live VM copy. Separately, the position field stayed
  at 41 while tasks advanced to 52, and a state note claimed 41 ledger
  rows against 59 in the file. Stale fields mislead every watch.
- Risk: L. Documentation plus field hygiene in the state-write helper.
- Evidence: daily note 2026-11-25.md line 1208 (root cause: laptop
  copy stale, must never be used for liveness; always read the VM
  copy); 2026-11-27.md line 34 (position field stuck at 41, current
  task and last_updated authoritative); 2026-11-27.md 04:47 ledger
  entry (state note stale vs file row count).
- Verdict: integrate-now with C1 and C2. Watch bodies name the VM copy
  as the only liveness source. State-write helper updates position and
  row counts from the ledger, or drops fields nobody maintains.

### Rank 15. C12. Per-task report file not written early (pack C12)
- Impact: M early, L late. Zero rows for the first graded tasks masked
  reporting health. Later the file was written at every grade to
  04:48, so the practice fix largely happened during the run.
- Risk: L. Checklist item plus watch trigger change.
- Evidence: event log lines 117-119 (zero rows, mtime at setup time,
  graded tasks with no row, AND-rule masked it); per-task log tail
  (rows continuous to 2026-11-27T04:48:07+07:00).
- Verdict: defer. Keep the grade-time row as a coordinator checklist
  item (already practiced late run). Change trigger (b) only if the
  next run still needs it; changing AND to OR without a grace window
  would add false alerts during long drives (see C23).

### Rank 16. C10. Speed-daemon repeated deaths (pack C10, understated)
- Impact: M. Messaging gaps while down; restarts by health watch each
  time. No run data lost, but coordination stalls.
- Risk: M. Cause unknown. A blind supervisor rewrite could mask the
  real cause or double-start daemons.
- Evidence: daily note 2026-11-25.md line 439 (daemon down, socket
  refused, died after a healthy check); 2026-11-26.md line 1296 (VM
  replacement killed daemon and supervisor together); 2026-11-27.md
  01:42 and 03:42 entries (daemon and supervisor both dead, both
  restarted detached). Pack lists daemon deaths and mentions the
  supervisor once; co-death is the pattern.
- Verdict: defer pending diagnosis. First step is log review in the
  daemon directory to name the cause (OOM, VM replacement, socket
  cleanup). Only then choose self-restart robustness. Do not integrate
  a supervisor that shares fate with the daemon (see C24).

### Rank 17. C24. Supervisor independence (NEW, split from C10)
- Impact: M. A supervisor that dies with the daemon supervises nothing.
  Both were dead together at least three times in the slice.
- Risk: M. Moving supervision to a service manager changes lifecycle
  and restart semantics; needs a kill test.
- Evidence: daily note 2026-11-27.md 01:42 entry (daemon and
  supervisor gone together, both alive at prior watch); 03:42 entry
  (same co-death, restarted together); 2026-11-26.md line 1296 (VM
  replacement killed both).
- Verdict: defer with C10. Candidate smallest change: run daemon and
  supervisor under the user service manager with restart-on-failure,
  fully detached from agent sessions. Test: kill daemon, confirm
  restart within one watch cycle; kill supervisor, confirm daemon
  survives.

### Rank 18. C20. Browser process death and memory growth (NEW)
- Impact: M. The browser died mid-run near closure and recovered as a
  fresh process; earlier it was restarted for high memory. Tab cleanup
  cut memory by about 3.5 GB, showing accumulation risk.
- Risk: M. Auto-restart authority for the browser is a direction
  decision (session restore, owner tabs). Health watch currently has
  no restart authority for the browser, by design.
- Evidence: daily note 2026-11-27.md line 81 (browser alive with all
  ports at 04:12:31, gone by 04:13:52, no restart by the watch);
  04:27 entry (recovered as new process, memory 1.40 GB vs 3.79 GB);
  2026-11-26.md line 125 (memory drop after tab cleanup);
  2026-11-25.md line 1764 (one browser restart for high RAM).
- Verdict: defer. Record a memory threshold alert and a session-restore
  checklist. Do not grant auto-restart until the owner decides session
  handling. Pair with C16 so cleanup never trades memory for owner tabs.

### Rank 19. C6. Foreign untitled Docs window cleanup (pack C6)
- Impact: L. Screen clutter and confusion, no drive impact once the
  run is closed.
- Risk: L if verified first, H if guessed. Closing the wrong window
  violates the never-close-owner-windows rule.
- Evidence: daily note 2026-11-26.md line 1060 (two browser windows
  on ws2, main run window plus an untitled Docs window from an earlier
  attempt); owner photo 04:22 27/11 per pack.
- Verdict: integrate-now as operational cleanup only. Verify by window
  title and process that it is the foreign untitled document, close
  that window only, re-list windows to confirm. No code.

### Rank 20. C21. Leftover application window sweep (NEW, widens C6)
- Impact: L. An idle editor window sat on ws2 for hours while screen
  looks logged it as normal, because that watch is read-only by design
  and its only closing exception is stale task tabs.
- Risk: L with verification (check unsaved content first), M without.
- Evidence: daily note 2026-11-27.md lines 85-88 (editor window since
  20:36 26/11, unsaved content verified trivial, closed by exact PID
  after a window-close call returned ok but left the process alive).
- Verdict: integrate-now as operational sweep with C6. Screen look
  gains a report-only leftover-window line (title, age, workspace);
  closing stays a human-approved or coordinator-approved step after
  unsaved-content check. Note the close-call-then-kill lesson: verify
  the process is gone, do not trust the close return code.

### Rank 21. C5. Browser folder operations without vision (pack C5)
- Impact: M if solved (Task 56 took about 73 min with step-by-step
  clicking), but no proven non-vision path exists yet. Drag-and-drop
  works and is vision-assisted.
- Risk: H if built blind. Folder state lives in browser chrome and
  session data; a wrong write corrupts the owner session.
- Evidence: daily note 2026-11-27.md 04:24-04:25 entry (owner directed
  drag-and-drop, confirmed it works); Task 56 timeout entries 03:59 to
  04:39 (drive past deadline, owner directing live). Pack claim of a
  parallel independent research effort is not corroborated in the
  provided slice (see pack errors).
- Verdict: defer. Integrate only what throwaway-profile verification
  proves (create folder, move tab, restart browser, folder persists).
  Until then, drag-and-drop with screenshot cross-check is the method.
  Coordinate, do not duplicate any parallel research.

### Rank 22. C27. Session-store decoder missing (NEW)
- Impact: L. Folder reconstruction from the saved session file failed
  on a missing decoder module, blocking the data-driven restore path
  and forcing manual reconstruction.
- Risk: L. Installing one small decoder on the laptop, or reading the
  file through the browser itself.
- Evidence: daily note 2026-11-27.md line 90 (session-store decode
  attempt failed, missing lz4 module, file itself not read).
- Verdict: defer to laptop tooling batch. Smallest change: ensure the
  decoder is present before any future session-restore task, and
  record the decode command in the machine layer. No repo change.

### Rank 23. C7. Pill label unification (pack C7)
- Impact: M for owner trust (pill showed a lane label instead of the
  plain active label), L for drive correctness.
- Risk: M if duplicated. Two workers editing overlay label logic at
  once will conflict.
- Evidence: daily note 2026-11-26.md lines 998-1000 (owner saw the
  lane label at 17:16, rule re-confirmed 17:41); 2026-11-27.md line 118
  (dedicated worker spawned after closure to find the bypass and fix
  so every pill shows only the plain label).
- Verdict: defer, do not duplicate. Note status only, as the pack
  says. Council should confirm the spawned worker owns it and that
  its test covers every lane (session, daemon, CDP, BiDi).

### Rank 24. C13. Ledger-push watch blocked (pack C13)
- Impact: M. Independent validation and push-lag checks did not run
  in blocked cycles, so ledger trust rested on coordinator claims.
- Risk: M. The block is an execution-risk guard on running worktree
  code. Bypassing it changes the safety posture.
- Evidence: daily note 2026-11-26.md line 762 (blocked, read-only
  fallback); 2026-11-27.md 00:48 entry (blocked, previous run 23:48
  OK) and 03:48 entry (blocked again, previous runs 01:48 and 02:48
  OK). The block is intermittent, not continuous (see pack errors).
- Verdict: defer to owner decision, as the pack says. Options for the
  owner: approve executing validators in the worktree, or move
  validation to a clean checkout outside the flagged tree. Council
  should not decide this.

### Rank 25. C14. Answer-key freshness, version item only (pack C14)
- Impact: L as scoped (one version string, scorers accepted on
  substance). The general problem is covered by C22.
- Risk: L. Process check only.
- Evidence: daily note 2026-11-25.md line 1764 (key version older
  than live version, both scorers accepted on substance).
- Verdict: reject as a standalone item; fold into C22 preflight. A
  one-off key edit without a preflight rule will recur.

### Rank 26. C4. Tier A checker bilingual parse (pack C4)
- Impact: L now. The failure cost one tiebreaker on a rerun. The fix
  the pack proposes is already in the file.
- Risk: L for a verification test, M if edited again blind (pattern
  changes can silently narrow acceptance).
- Evidence: rung3-ci/tier-a-check.py lines 96-109 (comment: bilingual,
  owner order 2026-11-25; patterns include the Vietnamese form and
  three English forms). Rerun ledger row recorded 2026-11-25T20:11:43
  (scorer 2 FAIL, scorer 3 PASS, tiebreaker used).
- Verdict: reject as written (already done). Integrate-now only a
  regression test: both languages parse, a mutated wrong position
  still fails. No pattern edit unless the test fails.

## 2. Pack claims found wrong or overstated

1. C4 is already fixed. The pack says the checker regex parses
   Vietnamese only (line about 97). The file at lines 96-109 already
   accepts the Vietnamese form plus three English forms, with a
   comment citing an owner order dated 2026-11-25. Integrating C4 as
   written would redo finished work. Source: tier-a-check.py lines
   96-109, read directly 27/11.
2. C4 tiebreaker attribution is conflated. The original R3-002 grade
   (recorded 2026-11-25T16:14:43) was FAIL from both scorers in
   agreement, no tiebreaker. The tiebreaker (scorer 2 FAIL, scorer 3
   PASS) belongs to the rerun recorded 2026-11-25T20:11:43. Source:
   R3-L3-grades.jsonl and R3-L3-reruns.jsonl rows for R3-002.
3. C11 duplicate stdin redirect count is understated. The pack says
   2x (R3-075, R3-076). The event log shows a third occurrence,
   R3-082, same chain (lines 1263, 1269, 1307). Three recurrences
   after the first fix note means the brief line alone did not stick;
   a launch helper is warranted.
4. C11 recurrence claims for Super-only key (4x), Alt+F4, editor colon,
   dock click, and file picker are not corroborated in the provided
   event-log and daily-note slice. They may be true from per-task
   reports, but the pack cites no line for them. Council should
   require per-task report citations before integrating those items.
   This is unverified, not disproven.
5. C10 understates supervisor co-death. The pack lists daemon deaths
   and notes the supervisor once. The slice shows daemon and
   supervisor dead together at least three times (VM replacement
   21:44 26/11; 01:42 and 03:42 27/11), which changes the fix from
   daemon robustness to supervision independence (C24).
6. C13 last-OK claim is wrong. The pack says last OK 23:48 26/11. The
   03:48 27/11 watch entry states previous runs at 01:48 and 02:48
   completed OK with 53 and 56 rows. The execution-risk block is
   intermittent. Source: daily note 2026-11-27.md 03:48 entry.
7. C1 understates the Task 56 logging freeze. The pack frames the
   lapse as heartbeat-only while coordinators kept working. After
   03:31 27/11 all three signals were stale (heartbeat 02:18:50,
   state last_updated 03:31:04, per-task 03:27:19) while the
   coordinator agent was verified still running at about 04:00. The
   fix must cover state-write cadence during long drives, not only
   the heartbeat writer. Source: daily note 2026-11-27.md 04:00
   parent verification entry.
8. C2 fix is incomplete for the Muse lane. The pack implies the
   coordinator simply failed to record a PID. Daily notes show
   Muse-lane tasks systematically carry runner_pid null with a session
   id instead (R3-002 rerun, R3-025, R3-036, Task 56). Recording a PID
   is impossible for that lane; the timeout watch needs a session-stop
   path. Source: daily notes 2026-11-25.md 19:43 entry,
   2026-11-26.md 13:58 entry, 2026-11-27.md 04:39 entry.
9. C3 overstates by omission. Grep for keybind/vision/screenshot in
   the brief template is indeed empty, but the template already
   mandates overlay acquire before driving, workspace switching by
   command, and DOM goto instead of typed URLs. The gap is one
   explicit keybind-first sentence, not an absence of related rules.
   Source: brief-template.md sections 5 and 7, read directly.
10. C5 parallel-research claim is unverified in the slice. The pack
    states an independent research effort with council, redteam,
    crawler, and trend research was ordered at 04:34 27/11. No such
    order appears in the provided daily notes or event log extract.
    Council should confirm ownership before deferring to it, to avoid
    deferring to work nobody is doing.
11. C12 fix is largely already practiced. The pack proposes writing
    the per-task row at grade time. The per-task log tail shows rows
    written at every grade through 04:48 27/11. The remaining gap is
    the early-run AND-rule masking and the Task 56 71-min gap, not
    the absence of the practice.

No pack claim was found fabricated. Errors 1, 2, 6 are factual.
Errors 3, 5, 7, 8, 9, 11 are understatements or incomplete fixes.
Errors 4 and 10 are unverified in the provided slice.

## 3. Top 5 to integrate first, in order

1. C1 (watch reads state freshness as liveness). One watch-body change,
   kills hours of false alerts, zero drive risk. Ship with C23
   threshold suppression in the same edit.
2. C2 revised (task lifecycle enforcement plus session-stop path plus
   completed-task guard). Prevents both observed kill failures. Needs
   a dry-run kill test before it may kill anything real.
3. C3 (keybind-first line in repo brief template). Docs only, helps
   every future drive, pairs with the C28 keybind verification rule.
4. C16 (tab-cleanup guardrail). Prevents a repeat owner-tab loss.
   Deny-list plus recorded-tabs-only rule, tested on a throwaway
   profile.
5. C8 (overlay final-release hide for session owner). Small code fix
   with a screenshot-verified test. Must land before C9, which is
   next in line (rank 6) with C15 (rank 7) immediately after.

Sequencing note: C9 depends on C8. C15 gate tests can run in parallel
with ranks 1 to 5 because they touch evidence collection, not drive
control. C17 durable split, C13, and C20 restart authority need owner
decisions and are not in the first batch.
