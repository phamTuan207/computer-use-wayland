# Batch 12 council 3: task 1 report review

## 0. Scope and method

Review target: docs/batch12-task1-s2-reopen-verify-20261122.md,
commit ed59f6a on main, 428 lines by wc -l.

Brief checked against: batch 12 task 1 from Muse, commit 26ebe40,
coord/clone1.md. The brief asks: read all 5 raw JSONs on
todolist-push, verify independently without trusting the worker
report, check each run has both messages verified, median wall
really 28.6s, V12/CB-1/model calls as claimed, phase split (SSH
21.9s of 28.6s) correct, Brave rollback real (new PID, no flag,
window back in place). Every claim must have command plus output
plus commit hash plus time log. Report only, change no code.

My method: independent re-derivation, not a re-read of the report.
I read the 5 raw JSONs myself with git show from origin/todolist-push
(read-only) into /tmp and extracted every field with python3
json.load. I also read improvements/worker-click5-s2-reopen-log.md
and improvements/worker-click4-s2-flip-log.md from
origin/todolist-push with git show. No repo code was run, tested,
imported, or loaded. No file was modified except this review.

Branch state at review time:
- todolist-push tip: 4305dcb153dc761d7f29d55842ddb23b8e400b9d
  (docs: COORD-CLICK-5 log, S2-REOPEN verified 5/5 median 28.6s,
  EXPAND approved in principle, clone1 batch 12 queued)
- Worker log commit 1a3356d and harness commit d90d1b9 are both
  ancestors of origin/todolist-push (checked with git merge-base
  --is-ancestor, both OK).
- Task 1 report commit ed59f6a on main, 428 insertions, 1 file.

Verdict scale: CONFIRMED means my own extraction from the raw
JSONs and logs matches the report exactly. A gap means the brief
asked for something the report does not cover or covers only
vaguely. Findings are listed in section 3.

## 1. Independent re-derivation of every number

Command: for n in 1..5, git show
origin/todolist-push:improvements/s2-flip-reopen-runs/run-N.json,
then python3 print of run, dry_run, wall_ms, model_calls,
phase_split_ms, and per browser outcome, message, program ok,
program elapsed_ms, program log, cb1, v12, routing, observe,
program_variant, pre_count, delayed_count, focus_enter, p9.

Output, my own extraction:
- run 1, dry_run False, wall_ms 29020.4, model_calls 0
- run 2, dry_run False, wall_ms 27799.1, model_calls 0
- run 3, dry_run False, wall_ms 28112.6, model_calls 0
- run 4, dry_run False, wall_ms 28898.1, model_calls 0
- run 5, dry_run False, wall_ms 28560.9, model_calls 0
- Sorted walls: 27799.1, 28112.6, 28560.9, 28898.1, 29020.4.
  Median 28560.9 ms, which is 28.5609 s, rounding to 28.6 s.
- Per browser, all 10 records: outcome sent, program ok True,
  v12 found True, attempts 1, role user, side user, cb1
  input_sent True, target_received True, verified True.
  Completed 3 on Brave, 2 on Chromium, every run.
- Messages: S2-REOPEN-R<n>-BRAVE-IGNORE-TEST (30 chars) and
  S2-REOPEN-R<n>-CHROMIUM-IGNORE-TEST (33 chars), all 5 runs.
- Program variants: run level program_variant
  brave=fill,chromium=set_value, chromium_set_value True,
  per browser program_variant fill on Brave, set_value on
  Chromium, all 5 runs.
- V12 items: Brave 43, 45, 47, 49, 51; Chromium 54, 56, 58,
  60, 62. Growth exactly 2 per run per browser.
- V12 textLen: 34 on Brave, 37 on Chromium, every run.
  Message length 30 and 33, so textLen is +4 in all 10 sends.
- Model calls: 0 at run level and 0 in all 10 browser records.
  phase_split_ms model 0 in all 5 runs.
- Chromium pre_count count 0 and delayed_count chromium count 1
  in all 5 runs. focus_enter ok True in all 5 Chromium runs.
  Brave has no pre_count or delayed_count keys, as designed.
- Routing: Brave dom-chromium, fell_through empty, observe 72,
  73, 75, 77, 79 elements, not truncated, composer present.
  Chromium dom-chromium, fell_through truncated inventory,
  routing_relaxed True, observe 80 elements, truncated,
  composer present, all 5 runs.
- Phase split medians, computed from the 5 runs: model 0,
  ssh 21942.2, broker 761.1, observe 2274.6, act 245.4,
  verify 375.9, setup 227.3, residual 2750.1. SSH share:
  21942.2 / 28560.9 = 0.768, which is 76.8 percent.
- Phase sum vs wall: run 1 29020.5 vs 29020.4 (off 0.1),
  run 2 27799.3 vs 27799.1 (off 0.2), run 3 28112.6 exact,
  run 4 28897.9 vs 28898.1 (off 0.2), run 5 28560.9 exact.
- Act vs program elapsed sum: run 1 140.516 + 113.005 =
  253.521 vs act 253.5; run 2 137.493 + 106.613 = 244.106
  vs 244.1; run 3 144.855 + 107.077 = 251.932 vs 251.9;
  run 4 140.832 + 99.412 = 240.244 vs 240.2; run 5 141.234 +
  104.164 = 245.398 vs 245.4. Exact to reported precision.
- p9 at run level: ok True for both browsers in all 5 runs,
  png paths improvements/s2-flip-reopen-runs/p9-runN-brave.png
  and p9-runN-chromium.png.
- Brave target_id FED133417A338D5B1596D60490746672 in all 5
  run JSONs.

Every number above matches the task 1 report exactly, including
the phase split medians, the internal consistency checks, the
+4 textLen note, and the routing details.

## 2. Brief coverage checklist

Each brief requirement, the report section that answers it, and
my verdict:

1. Read all 5 raw JSONs. Report sections 0 to 7 plus 9A, 9C,
   9F read and cross-check all 5. CONFIRMED. My own read of
   all 5 confirms the same values.
2. Each run has both messages verified. Report section 2
   (10/10 sent, program ok, completed) and section 5 (CB-1
   verified True all 10), corroborated by V12 in section 4
   and pre-count 0 plus delayed count 1. CONFIRMED.
3. Median wall really 28.6s. Report section 3: sorted list
   and median 28560.9 ms. CONFIRMED by my own sort.
4. V12/CB-1/model calls as claimed. Report sections 4, 5, 6.
   CONFIRMED by my own extraction of all 10 records.
5. Phase split, SSH 21.9s of 28.6s. Report section 7: median
   ssh 21942.2 ms, 76.8 percent, plus sum and act checks.
   CONFIRMED by my own medians and sums.
6. Brave rollback real. Report section 8: three PIDs in order,
   window address stable, 0 matches for the flag, with the
   stated limit that the final checks are log-only because
   this VM has no SSH path to the laptop. CONFIRMED on the
   record, see below.
7. Command plus output plus commit hash plus time log for
   every claim. Report sections 1 to 8 each carry Command,
   Output, Commit (todolist-push tip 4305dcb, worker log
   1a3356d), and Time (runs 13:05:09-13:09:12 +07).
   CONFIRMED. The commands describe gh api raw reads, because
   the task agent's first git fetch failed an execution-risk
   check and it read through the GitHub API instead. The
   method is disclosed in section 0. My council review
   re-derived every number with git show on todolist-push,
   which independently confirms the API-based reads.
8. Report only, change no code. Commit ed59f6a stat: 1 file
   changed, 428 insertions, only
   docs/batch12-task1-s2-reopen-verify-20261122.md. No code
   file touched. CONFIRMED. No em dash or en dash in the
   report (grep for both returns no match).

Rollback cross-checks, my own grep of the worker log
(commit 1a3356d, 347 lines):
- Pre-state, log line 84: Brave PID 1003210, no debug flag,
  window 0x55705383d420 on ws1.
- Debug relaunch, log lines 120-145: SIGTERM 13:02:45 +07 to
  PID 1003210, new main PID 1112207 at 13:03:06 +07, cmdline
  carries the flag, tab FED133417A338D5B1596D60490746672
  ("Chat - clone1") served by [::1]:9223, window back at the
  same address 0x55705383d420, ws1, PID 1112207.
- Rollback, log lines 307-323: SIGTERM 13:10:36 +07 to PID
  1112207, graceful exit in 1s, [::1]:9223 closed, relaunch
  WITHOUT the flag 13:10:52 +07, new main PID 1119832,
  verified 13:11:00 +07, window back at the same address
  0x55705383d420, ws1, PID 1119832, [::1]:9223 stays closed,
  full cmdline check 13:11:18 +07 with 0 matches for
  remote-debugging-port on PID 1119832.
- PID continuity with the earlier flip, my own grep of
  worker-click4-s2-flip-log.md: PID 1003210 at lines 163,
  568, 570. The flip rollback ended on PID 1003210 and the
  reopen pre-state starts from PID 1003210. CONFIRMED.
- Time log in report section 0 matches the worker log:
  task received 12:56, pre-state 12:58, harness fix 13:01,
  relaunch 13:02:45-13:03:32, dry run 0 13:03:51-13:04:38
  wall 30123.9ms, runs 13:05:09-13:09:12, rollback
  13:10:36-13:11:18. CONFIRMED.
- Worker log run table, lines 184-188: walls, dom_act ms,
  elapsed ms, V12 items, CB-1, pre 0, delayed 1 all match
  my JSON extraction. Log line 190 states median wall
  28560.9ms. Log lines 206-208 state the phase split
  medians, identical to my computed medians. CONFIRMED.

## 3. Findings

A. P9 screenshots missing from the branch. Material gap,
   correctly flagged by the report (section 9, item A).
   My own check: git ls-tree -r origin/todolist-push for
   improvements/s2-flip-reopen-runs lists exactly the 5 JSON
   files, and grep for p9-run across the whole tree returns
   0 matches, at tip 4305dcb. The run JSONs record p9 ok
   True with png paths, and the worker log section 5 reviews
   all 10 shots and section 8 says the PNGs were "(to be
   committed with this log)" (log line 335). The render-side
   P9 review therefore cannot be independently re-checked
   from the branch. This does not refute the sends: V12 DOM
   verification, CB-1, pre-count 0, and delayed count 1
   corroborate the sends from the JSONs. The PNGs still need
   to be committed for the P9 claim to be checkable. Agree
   with the report, no new action from council 3 beyond
   restating it.

B. V12 textLen systematically +4 over message length.
   Minor open note, correctly flagged by the report
   (section 9, item B). My extraction confirms it: Brave
   message 30 chars, textLen 34; Chromium message 33 chars,
   textLen 37, in all 10 sends. Does not change any verdict.
   The V12 script lives in /tmp on the laptop, not in the
   repo, so its definition cannot be checked from the
   branch. Agree with the report.

C. Chromium routing ran under the disclosed relaxed gate in
   all 5 reopen runs. Stated caveat, correctly flagged by
   the report (section 9, item C). My extraction confirms:
   Chromium routing_relaxed True, 80 elements, truncated,
   composer present, runs 1 to 5. The worker log line 35
   phrase "runs 2-5 under a DISCLOSED relaxed gate" refers
   to the earlier (b1) probe runs of 12:44-12:51, where run
   1 passed under the strict gate; the reopen log section 6
   states the Chromium half is "routing RELAXED every run".
   The report reads this distinction correctly. Agree.

D. Residual range wording cites run 1 values. Minor,
   correctly flagged by the report (section 9, item D).
   Worker log line 210 says "874.7-1383.7ms". My extraction
   confirms those are run 1 pre-check 1383.7 ms and delayed
   874.7 ms, and across runs pre-check is 1383.7, 1513.5,
   1403.5, 1420.4, 1426.9 ms and delayed is 874.7, 805.9,
   812.0, 804.7, 849.2 ms. Approximately right, not a
   refutation. Agree.

E. Dry run 0 and wiring tests are log-only. Noted by the
   report (section 9, item E), out of scope for the brief.
   Dry run 0 (13:03:51-13:04:38 +07, wall 30123.9ms) has no
   JSON on the branch; wiring tests 12/12 pass is a log
   record. The brief did not ask for these. No gap.

F. Run table cross-check. Report section 9, item F: all
   values match. My own comparison of log lines 184-188
   against the JSON program logs and elapsed_ms confirms
   it. Agree.

G. Report section 11 is now stale, not a defect. At writing
   time the report said it was NOT committed or pushed,
   because the task agent's git fetch had failed an
   execution-risk check. It is now committed on main as
   ed59f6a (author phamTuan207, 2026-11-22 06:31:47 UTC,
   13:31:47 +07), by the parent agent after the task agent
   wrote it. Future readers should read section 11 as
   true at writing time only. No fix pass needed from the
   task agent; this council note records it.

H. EXPAND framing. Report section 10 says the EXPAND
   recommendation "follows from the gate as the log states
   it". That recommendation is the worker log's judgment,
   not something this verification establishes on its own.
   What this verification establishes is the numeric basis
   it rests on: 5/5 runs complete, 10/10 sends verified,
   median wall 28.6s, 0 model calls. The report hedges this
   with the log's own caveats (relaxed Chromium routing
   gate, unsolved mouse stall, transport-dominated wall,
   durable landing still open). Acceptable as written, but
   the distinction matters for task 3's CB-8 audit: the
   numbers are confirmed, the recommendation is the
   worker's.

## 4. Overall verdict

COMPLETE.

The report covers every item the brief asked for, each with
command plus output plus commit hash plus time log. All 7
worker claims I re-derived from the raw JSONs are CONFIRMED:
5/5 runs complete, 10/10 messages sent, median wall 28.6s
(28560.9 ms), V12 attempt 1 on all 10 messages, CB-1 all
three parts on all 10, 0 model calls, phase split with SSH
median 21942.2 ms (21.9s, 76.8 percent of the median wall),
and Brave rollback real on the record (PIDs 1003210, then
1112207, then 1119832; window 0x55705383d420 stable; 0
matches for remote-debugging-port on the final PID).

No brief item is uncovered or covered only vaguely. No code
was changed. One material gap stands, already flagged by the
report itself: the P9 screenshots are not on the branch
(section 3, item A), so the render-side P9 review cannot be
independently re-checked. Two minor open notes stand:
V12 textLen is systematically +4 (item B), and the residual
range wording cites run 1 values (item D). No fix pass is
required from council 3, because the report already states
all of these plainly; the only new notes are the stale
section 11 (item G) and the EXPAND framing (item H), both
recorded here for the record.
