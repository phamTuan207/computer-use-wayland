# R3-L3 fix-integration review: council reviewer 2 of 3 (27/11/2026)

Independent review. Scope read in full: evidence pack (14 candidates C1-C14),
per-task reports log (132 lines), grades ledger (60 rows) plus re-run ledger
(3 rows), coordinator state notes array, and drive reports R3-096, R3-098,
R3-099, R3-100. Pack claims were checked against sources and against current
code where the pack pointed at code. No implementation. Ponytail applies to
every fix sketched below: smallest complete change, one small test for
non-trivial logic.

Ranking rule: impact first (time saved, errors prevented), risk as tiebreak
(low risk first). Verdicts: integrate-now, defer, reject.

## Ranked list (all candidates, rank order)

### Rank 1. C2. State-file task_start / runner_pid gap
- Impact: H. Prevents the worst failure class in the run: a timeout watch
  killing a live idle pane, and a 30-minute limit that cannot fire. Recurred
  at R3-001, R3-040 attempts, R3-072, R3-078, R3-046, DP-03.
- Risk: L. Checklist plus a small state-write helper plus one guard in the
  timeout watch. No drive-path change.
- Evidence: per-task log R3-078 honest record (26/11 22:20 drive, no
  task_start or PID recorded); R3-072 block (fields recorded late 20:15:13,
  deadline 20:15:07, kill could not fire, 31m29s graded on evidence);
  coordinator notes 25/11 13:52:30 emergency clear of stale fields, 26/11
  17:59 DP-03 gap fix, 26/11 20:15:13 R3-072 gap closed.
- Verdict: integrate-now. Enforce fresh task_start plus runner PID at every
  task start, cleared at drive end. Timeout watch must treat a completed
  task (per-task row exists or drive end recorded) as not running. For the
  Muse lane there is no OS PID by design, so record the runner session id
  and enforce the timeout by closing the subagent (see pack error E3).

### Rank 2. C15 (NEW). Tier A checker remaining parser brittleness
- Impact: H. Four live false negatives each cost a tiebreaker or a dual
  scorer override with proof. Fixing them removes scorer toil on every
  future Tier A task and stops checker FAIL from masquerading as runner
  failure.
- Risk: L. Union-style broadening only, same pattern as the 25/11 bilingual
  fix. Acceptance only grows. One small test per check with a mutation
  control (wrong values must still FAIL).
- Evidence: per-task log line 42 (R3-021, header-assumption parse miss,
  tiebreaker needed); line 45 (DP-02, per-file detail lines judged beyond
  task criteria; coordinator note 26/11 03:42:47 records a brief defect:
  brief marked detail lines optional, checker requires them); line 67
  (R3-072, pipe table read as 0 of 5 images); line 96 (R3-076, 3 reasons).
  Current code: rung3-ci/tier-a-check.py line 214 still counts CSV rows as
  lines minus 1 (assumes header; R3-021 CSV is headerless with 4 rows);
  line 221 image regex still requires filename directly followed by size;
  check_report_consistency still accepts only Disk free / Free disk /
  RAM free / Free RAM labels and whitespace rows, while the sealed R3-076
  report uses "Free on /:", "Free (free column):" and pipe rows (snapshot
  R3-076-L3 d42-bao-cao.txt, tier-a-output.json 3 reasons).
- Verdict: integrate-now. Accept pipe separators in image-sizes and process
  rows, accept headerless CSV (count rows that match the expected shape,
  or accept lines or lines minus 1), accept the two extra disk/RAM labels,
  and align the keyword-counts brief template with the checker (detail
  lines required, stated in the brief). Keep the checker an aid, not the
  judge.

### Rank 3. C3. Keybind-first hard rule missing from repo brief template
- Impact: H. Vision-heavy driving was the main time sink late in the run
  (task 56 slow step-by-step clicking). One paragraph in the template
  steers every future runner to keybind or command first.
- Risk: L. Docs text only, generic wording, no machine specifics.
- Evidence: grep for keybind, vision, screenshot in
  computer-use-wayland/docs/brief-template.md returns no hits (checked
  27/11, exit 1). Machine layer already fixed 27/11 per pack. Owner hard
  rule 27/11.
- Verdict: integrate-now. Add the hard rule to docs/brief-template.md:
  whatever can be done with a keybind or command, use the keybind or
  command; vision and screenshots for cross-checks only.

### Rank 4. C9. No fail-closed pill gate in BiDi driver path
- Impact: H. The pill must show on any agent control. Today the BiDi path
  relies on a manual wrapper. One forgotten wrapper means invisible
  control, which breaks owner trust in the whole setup.
- Risk: M. Touches session start and stop. Fail-closed can block a drive
  if the overlay is down, which is the intended trade, but it needs a
  tested error message so runners stop instead of retrying blindly.
- Evidence: coordinator notes record pill proven via manual acquire and
  release wrapper (G-44, 25/11) and repeated grim proof of release per
  task; no overlay hook in the BiDi driver itself. Drive reports
  R3-096 to R3-100 all acquire and release manually around the drive.
- Verdict: integrate-now. Acquire inside BiDi session start, release at
  stop, refuse to drive if the pill cannot show. Test: drive without
  wrapper must fail or auto-wrap, pill visible during drive, gone after.

### Rank 5. C16 (NEW). Overlay daemon spawn fragility (30s block vs 15s deadline)
- Impact: H. Blocks every drive that needs a fresh overlay daemon. Cost
  R3-049 attempt 1 outright and can recur whenever a stale config error
  exists.
- Risk: M. Daemon startup path. Fix must not hide real indicator failures.
  Pre-flight check is zero risk and lands first.
- Evidence: coordinator notes 26/11 18:13 and 18:17 (R3-049 attempt 1):
  act-now refused with overlay daemon did not answer within 15s; root
  cause was a stale Lua config error making each native spawn burn 30s
  while the ensure step waits 15s; cleared by a no-op eval, verified
  live (spawn 209 ms). Drive reports R3-096 to R3-100 all pre-flight
  configerrors empty.
- Verdict: integrate-now in two steps. Step 1 (no code): pre-flight rule
  in every drive brief, configerrors must be empty before acquire, object
  form dispatch only. Step 2 (code): make native spawn non-blocking or
  align the two timeouts, with one acquire and release test.

### Rank 6. C8. overlay.py release bug: pill stuck visible
- Impact: M. Fail-safe direction (stuck on) but status lies, so grim proof
  of release becomes unreliable and cleanup is manual.
- Risk: L. Single missing hide send on final release, narrow test.
- Evidence: pack daily-note finding 25/11 (verified 10:59 and 11:01,
  again after Codex attempt 1, cleared manually 11:03:16). Consistent
  with repeated pill-gone grim checks in per-task reports.
- Verdict: integrate-now. Send hide on final release when the owner is
  the session indicator. Test acquire and release cycle ends with pill
  gone, grim verified. Land with C18 (same file, same test cycle).

### Rank 7. C17 (NEW). Holder swallows session error and orphans the BiDi session
- Impact: H. Cost R3-049 attempt 2 plus about 10 minutes of reap wait, and
  the real error never reached the log, so diagnosis needed a live probe.
- Risk: L for the brief rule, M for the holder change (exit code change
  can break callers that ignore it; log first, then exit non-zero).
- Evidence: coordinator notes 26/11 18:26 and 18:35 (R3-049 attempt 2):
  detached holder exits at 0.0s with no ready file; finally block exits 0
  and swallows the session error; orphaned session reaped after about
  9m44s; proof run with the exact detached variant then succeeded.
- Verdict: integrate-now. Brief rules now: never timeout-kill the holder,
  stop via stop file and wait for session end; if the holder dies, poll
  session creation, never retry-launch in a loop. Code: log the session
  error and exit non-zero. One test with a forced session failure.

### Rank 8. C11. Recurring drive anomalies (machine-layer knowledge gaps)
- Impact: H in aggregate. Each item is small, together they fired on most
  late-run drives and each cost minutes of re-grounding.
- Risk: L. Laptop machine layer plus generic brief lines. No repo code.
- Evidence: per-task log lines 77, 87, 97, 106, 116 (R3-074 to R3-079
  anomaly chains): Super-only refused 4 times (lines 87, 97, 106, 116),
  duplicate stdin redirects 2 times (R3-075, R3-076), Alt+F4 does not
  close Kitty or Foot, colon refused as unsupported XKB in nvim (R3-078),
  dock click opened Bar Folder panel, file picker stuck in /tmp, driver
  SSH broken pipe about 36s (benign, detached runner alive). Drive
  reports add: grim output name guesses (R3-100), focused-output pipeline
  failure (R3-098), Ctrl+T refused as new window (R3-100). See C24 for
  the grim item.
- Verdict: integrate-now. Machine-layer fastest-paths and keybinds
  additions on the laptop only. Generic brief lines where they apply to
  any machine: single stdin redirect on detached launch, launcher via
  Super+Space, terminal close via Ctrl+D or Super+Q, expect SSH launch
  pipe drops and verify the detached runner instead of relaunching.

### Rank 9. C1. Heartbeat-log writer lapse
- Impact: M. No task result was wrong, but liveness alerts fired false
  positives for about 2.5 hours and real stalls would have been masked.
- Risk: L. Watch-side change only.
- Evidence: heartbeat log last line 2026-11-27T02:18:50+07:00 (checked
  27/11) while work continued to 04:48; coordinator note 26/11 20:15:13
  records liveness alerts at 20:02 and 20:07 as the known heartbeat-lag
  pattern with the coordinator alive.
- Verdict: integrate-now, option (b) only: liveness watch treats a fresh
  state-file last_updated as liveness. Smallest change, no new writer
  discipline to remember. Option (a) (write heartbeat on every state
  update) is more moving parts for the same signal; reject it.

### Rank 10. C25 (NEW). State counters stale and per-task format drift
- Impact: M. Every coordinator takeover had to recompute counts from the
  ledgers because top-level counters were stale, and the per-task log
  mixes pipe rows, JSON lines, markdown blocks and one-line summaries,
  so watches that grep it are fragile.
- Risk: L. One writer helper plus a validate step. No scoring change.
- Evidence: coordinator notes 26/11 08:03:21 (counters corrected at
  takeover, prior epoch left 29/1/0/7), 19:06:52 (counters stale, ledger
  files authoritative); per-task log format changes at R3-002 (JSON),
  R3-072 (markdown block), R3-082 onward (one-line summaries).
- Verdict: integrate-now with C1, C2, C12 as one signal-hygiene change:
  single append helper that validates each row, counters derived from
  ledgers at write time, one row format. Do not rewrite history rows.

### Rank 11. C12. Per-task report file not written early in run
- Impact: M. The reporting watch greps this file; missing rows hide
  progress and force backfills.
- Risk: L. Checklist item at grade time.
- Evidence: coordinator note 25/11 15:27:25 (per-task report file has no
  rows, backfill R3-001 and R3-040) and 15:32:17 (backfilled, pushed).
  Later rows run to 04:48 27/11.
- Verdict: integrate-now as part of Rank 10. Coordinator writes the
  per-task row at grade time. Keep the watch trigger as is; fixing the
  writer is smaller than changing watch logic.

### Rank 12. C18 (NEW). Pill release must pass the same PID as acquire
- Impact: M. First pill-off capture was not pill-free; cost a re-capture
  cycle and could have sealed false release proof.
- Risk: L. Brief line plus an overlay warning when a pid-keyed holder is
  released without its PID.
- Evidence: drive report R3-096 anomaly chain (release reported success
  at 02:29:57 while holder still visible; help text states pid-keyed
  holder needs its own PID; explicit release at 02:30:20 fixed it).
  R3-098, R3-099, R3-100 applied the lesson first try.
- Verdict: integrate-now with C8. Briefs state acquire and release use
  the same long-lived PID. Overlay release without PID on a pid-keyed
  holder should warn loudly instead of reporting success.

### Rank 13. C21 (NEW). Tab cleanup safeguard (allowlist only, never close-all)
- Impact: H if it recurs, M expected. One over-close removed pinned and
  essential tabs and created a whole extra counted task (task 56, about
  73 minutes). Rare but expensive.
- Risk: L. Rule plus script guard. No drive-path change.
- Evidence: coordinator notes 26/11 02:17:37 (batch 2 closed 24 tabs
  including owner pinned and essentials under a close-everything-except-
  active wording) and 02:20:43 (restoration became counted task 56);
  per-task log R3-056 line (graded on owner inspection, overrun
  recorded). Batch 1 (21:23, 27 tabs, URL allowlist) closed nothing
  wrong, which proves the safe method.
- Verdict: integrate-now. Cleanup scripts take an explicit URL allowlist
  of completed-task pages only, list matches before closing, and refuse
  a keep-only-one-tab mode. Pinned and essential tabs are never matched.

### Rank 14. C20 (NEW). Snapshot and evidence pipeline traps
- Impact: M. Each trap cost a re-seal, a force-add, or a gate debate.
  Together they slow every task boundary.
- Risk: L. Small script and checklist fixes, each independently testable.
- Evidence: coordinator notes 25/11 16:02:38 (collect step writes a
  manifest into the evidence dir, snapshot then includes it with a stale
  self-hash; fix is delete before snapshot), 26/11 03:42:47 (snapshot
  copies top-level files only; DP-02 evidence has a subdir and needed a
  recursive seal), 26/11 19:43:44 (gitignore *.png silently drops
  snapshot PNGs; always force-add and verify tree count vs manifest),
  26/11 13:22:00 (collect check failed on screenshot naming HHMM vs
  HHMMSS while 4 real screenshots existed).
- Verdict: integrate-now. Snapshot step deletes or excludes the collect
  manifest, supports subdirs, force-adds PNGs with a count check, and
  the collect check accepts both timestamp precisions. One test per fix
  with a sealed fixture.

### Rank 15. C24 (NEW). Grim capture defaults (output name guesses fail)
- Impact: L to M. Two drive reports lost the first pill capture to a
  guessed output name or a focused-output pipeline.
- Risk: L. Machine-layer note only.
- Evidence: drive report R3-098 (focused-output pipeline returned no
  JSON, plain grim fixed it), R3-100 anomaly 1 (grim -o DP-1 unknown
  output, default output fixed it), coordinator note 26/11 19:42:55
  (monitor guess DP-1 failed, doctor showed eDP-2).
- Verdict: integrate-now with C11. Machine layer: plain grim on the
  default output for pill proof; discover the output name, never guess
  DP-1.

### Rank 16. C6. Foreign Google Docs tab cleanup on ws2
- Impact: L. Clutter and one interrupted drive (R3-046 attempt 1). No
  scoring impact now that the run is closed.
- Risk: M if done carelessly (closing owner tabs is the C21 failure).
  L with the C21 allowlist method and a verify-first step.
- Evidence: coordinator notes 26/11 17:21:00 (untitled Google Docs window
  became active on ws2, drive stopped fail-closed) and 19:42:55
  (correction: it is a tab inside the main Zen window, not a separate
  window; left untouched). See pack error E4.
- Verdict: integrate-now as operational cleanup only, after C21 lands:
  verify the tab is the foreign untitled doc, close only that tab, never
  owner tabs. No code.

### Rank 17. C19 (NEW). Zen memory growth and D1 restart policy
- Impact: M. At about 4.8 GB per hour the browser would have exhausted
  available memory mid-run. The restart worked, but it was improvised.
- Risk: M. Restarting the browser mid-run risks session loss; the
  procedure must stay at task boundaries with tab restore verified.
- Evidence: coordinator notes 25/11 17:02:01 (RSS 5.50 GB, 6.76 GB,
  8.11 GB readings, restart decision) and 17:05:00 (restart done, RSS
  7950 MB to 978 MB, ports and session restored).
- Verdict: defer code, integrate the procedure now: monitor RSS at task
  boundaries, restart via the wrapper past about 8 GB, verify ports,
  session restore and pill after. Root-cause the leak only if it recurs
  outside long runs.

### Rank 18. C26 (NEW). Holder probe path inconsistency (webdriver true vs false)
- Impact: M. The guard worked (Zen step stopped, no false evidence), but
  a graded-adjacent confirmation step was lost and the cause is unknown.
- Risk: M. Touching the probe risks weakening the fail-loud guard.
  Investigate read-only first.
- Evidence: drive report R3-100 anomaly 3 (zen_dom eval returned
  webdriver true at 03:16:07, Zen part stopped per rule) versus probe
  clean false on R3-028, R3-029, R3-035, R3-036, R3-046, R3-049 drives
  (coordinator notes and per-task reports).
- Verdict: defer. Reproduce both probe paths on the same session, find
  why they disagree, unify on one probe. Do not loosen the stop rule.

### Rank 19. C22 (NEW). Cross-VM verdict delivery has no standard channel
- Impact: M. Blocked ledger writing for R3-001 until an ad-hoc repo
  branch transfer was arranged. The fallback worked every time after.
- Risk: L. Process standardization, no code.
- Evidence: coordinator notes 25/11 14:07:12 (verdict files on another
  VM, files-only channel has no transfer mechanism, deviation to repo
  branch) and 14:18:26 (resolved via branch, pulled and audited).
- Verdict: defer. Formalize the repo-branch fallback as the standard
  cross-VM path with the same audit steps. No new tooling.

### Rank 20. C14. Answer-key freshness (R3-004)
- Impact: L. One task, both scorers accepted on substance. No wrong
  grade.
- Risk: L. Process item.
- Evidence: per-task log R3-004 note (live go1.27.4 vs key go1.14.3);
  coordinator note 25/11 20:55:12 (key verified 2026-11-23, live doc
  changed by run time, step commands otherwise identical).
- Verdict: defer. A freeze-time refresh would not have caught drift
  during a multi-day run. Better: version-sensitive keys carry a
  run-time tolerance note (accept the live version when steps match),
  plus a refresh check at freeze. Process only.

### Rank 21. C23 (NEW). PII scan false positives hold out evidence logs
- Impact: L. Raw runner logs were excluded from two snapshots; manual
  review passed three more. No leak occurred, but evidence completeness
  suffers.
- Risk: M. Loosening a PII gate is the risky direction. Triage rules
  must stay conservative.
- Evidence: per-task log R3-067 and R3-072 blocks (codex log held out
  after high-entropy hit); coordinator notes 26/11 12:46:27, 13:22:00,
  14:04:51 (manual-review hits on task-created doc URLs and demo-store
  routes, passed on review).
- Verdict: defer. Add a documented manual-review class for task-created
  doc URLs with coordinator sign-off recorded. Do not add broad
  allowlists for high-entropy strings.

### Rank 22. C10. Speed-daemon repeated deaths
- Impact: M. Messaging gaps while down; each restart was manual via a
  watch. No task grade was lost.
- Risk: M. Cause unknown; blind supervisor changes can mask the real
  fault or loop.
- Evidence: pack death list (26/11 five times plus VM replacement,
  27/11 twice). Coordinator notes corroborate restarts at 25/11 22:38:25
  and 26/11 03:30:16 (daemon down, restarted before send).
- Verdict: defer. Diagnose from logs first (exit reason, memory, socket
  state), then decide. No fix without a named cause.

### Rank 23. C5. Zen folder and tab operations without vision
- Impact: H if solved, but effort is unbounded without research. Task 56
  showed the cost of the vision path.
- Risk: H. Browser chrome automation with no API; wrong moves touch
  owner tabs (see C21).
- Evidence: per-task log R3-056 line (about 73 min, owner inspection);
  pack notes no API exposes folders and independent research is already
  running.
- Verdict: defer. Coordinate with the independent research, integrate
  only what is proven on a throwaway profile. Do not duplicate.

### Rank 24. C7. Pill label unification
- Impact: L. Cosmetic label, bar present. Owner rule is clear (only
  "Computer use active").
- Risk: L, but owned by a separate worker.
- Evidence: per-task log R3-074 block (label washed out in capture, bar
  present, fix queued post-run per owner 17:41 26/11).
- Verdict: defer. Note status only, do not duplicate the assigned work.

### Rank 25. C13. Ledger-push watch blocked
- Impact: L. Ledger pushes still happened by coordinator hand; the watch
  automation is blocked, not the ledger.
- Risk: M. Changes how pushes run; owner-decision shaped per pack.
- Evidence: pack only (hourly runs blocked, last OK 23:48 26/11). No
  corroborating entry in the deep-read slice; coordinator notes show
  pushes landing throughout (ls-remote verified repeatedly).
- Verdict: defer to the owner. List it, do not decide it here.

### Rank 26. C4. Tier A checker bilingual parse (json errors)
- Impact: none remaining. Already fixed mid-run.
- Risk: none for new work; a regression test still has value.
- Evidence: coordinator note 25/11 21:21:13 (owner instruction applied:
  check_json_errors unions 4 patterns, verified R3-002 re-run snapshot
  now checker-PASS, original still FAIL on wrong values); current code
  rung3-ci/tier-a-check.py lines 95 to 106 already contains the English
  patterns. See pack error E1.
- Verdict: reject as new integration work (done 25/11). Keep one
  bilingual regression test under C15 so the union cannot regress.

## Pack claims found wrong or overstated

E1. C4 describes pre-fix code as current. The pack quotes the Vietnamese
only regex at line about 97 as the live state. The bilingual fix landed
25/11 21:21 (coordinator state note, owner instruction number 1 APPLIED,
with before and after verification). Current tier-a-check.py lines 95 to
106 union Vietnamese and three English forms. C4 needs no integration,
only a regression test.

E2. C4 scope understates Tier A brittleness. The pack lists only the json
parse. The deep read shows three more live false negatives plus a brief
defect, none in the pack: R3-021 CSV header assumption (tier-a-check.py
line 214, per-task log line 42, tiebreaker spent), R3-072 pipe table
(line 221, per-task log line 67, dual override), R3-076 labels and pipe
rows (per-task log line 96, snapshot tier-a-output.json), DP-02 detail
lines (per-task log line 45, coordinator note 26/11 03:42:47). These are
new candidate C15.

E3. C2 task 56 framing overstates the PID point. The pack says a null
runner_pid blocked the timeout kill for 70 plus minutes. For the Muse
lane, runner_pid null is by design (coordinator notes state this at every
Muse release; timeout is enforced by closing the subagent). Task 56 ran
about 73 minutes because the coordinator did not close the runner at 30
minutes on an owner-inspection task, not because a PID was missing. The
fix differs: enforce the subagent close, and record the session id. The
R3-072 and R3-078 gaps in C2 are real and stand.

E4. C6 says window, source says tab. Coordinator note 26/11 19:42:55
corrects the record: the untitled doc is a tab inside the main Zen
window on ws2, not a separate window. Cleanup must target one tab, with
the C21 verify-first method.

E5. C11 misattributes the session driver exit. The pack places "Unknown
process id" at R3-072 area. Per-task log line 77 places it in R3-074
(Kitty observe). R3-072 anomalies are the image viewer clip, a sudo
prompt terminal, and a save-dialog focus error. Session ends also recur
in R3-076 (line 97) and R3-079 (line 116), so the fix belongs with the
session lifecycle items C17 and C11, not R3-072.

E6. C12 evidence pointer is weaker than stated. The pack cites a daily
note mtime that is not in the deep-read slice. The slice corroborates
the substance (coordinator note 25/11 15:27:25 found no rows and
backfilled at 15:32:17), so the candidate stands, but the mtime detail
should not be quoted as verified.

## Top 5 to integrate first (in order)

1. C2. State task_start and runner identity discipline plus timeout-watch
   completed-task guard. Prevents killing live work and makes the
   30-minute limit real. Smallest change, highest error prevention.
2. C15. Tier A remaining parsers (pipe separators, headerless CSV, extra
   labels, brief and checker alignment) with mutation controls. Removes
   tiebreakers and scorer overrides on every future Tier A task.
3. C3. Keybind-first hard rule in the repo brief template. One paragraph,
   steers all future driving away from vision-heavy paths.
4. C9. Fail-closed pill gate inside the BiDi session. Makes the owner
   pill rule structural instead of remembered.
5. C16. Overlay spawn pre-flight now, timeout alignment in code next.
   Unblocks every fresh-daemon drive; pre-flight is zero risk today.

Next batch after the top 5: C8 plus C18 (same pill test cycle), C17,
C11 plus C24 (machine layer), then C1 plus C12 plus C25 as one
signal-hygiene change, then C21 and C20.
