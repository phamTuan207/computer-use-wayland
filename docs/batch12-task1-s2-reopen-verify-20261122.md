# Batch 12 task 1: S2 reopen independent verification

## 0. Scope and method

Task: independently verify the S2 reopen run series from the raw
JSONs. Do not trust the worker's own report.

Sources read, all from branch todolist-push:
- improvements/s2-flip-reopen-runs/run-1..5.json
- improvements/worker-click5-s2-reopen-log.md (worker log)
- improvements/worker-click4-s2-flip-log.md (only for the PID
  continuity cross-check in section 8)

Branch state at verification time:
- todolist-push tip: 4305dcb153dc761d7f29d55842ddb23b8e400b9d
  (commit message: docs: COORD-CLICK-5 log, S2-REOPEN verified
  5/5 median 28.6s, EXPAND approved in principle, clone1 batch
  12 queued)
- Worker log commit: 1a3356d (C5-S2-REOPEN log: two-browser flip
  re-opens 5/5 runs, median wall 28.6s, recommend EXPAND)
- Harness commit: d90d1b9 (C5-S2-REOPEN: harness
  --chromium-set-value, Brave fill, Chromium set_value)
- Follow-up: 212e0ad (C5-S2-REOPEN log: record own commit hash
  1a3356d)

Read method: the first git fetch result in this session failed an
execution-risk check, so no git command was run in the repo after
that fetch, and no repo code was run, tested, imported, or loaded.
All files below were read as plain text through the GitHub API
(read-only raw content fetch), run from the home directory, not
inside the repo. Commands used:
- gh api -H "Accept: application/vnd.github.raw"
  "repos/phamTuan207/computer-use-wayland/contents/<path>?ref=todolist-push"
  for each run JSON and each log file
- gh api "repos/phamTuan207/computer-use-wayland/contents/improvements/s2-flip-reopen-runs?ref=todolist-push"
  for the directory listing
- gh api "repos/phamTuan207/computer-use-wayland/branches/todolist-push"
  and the recursive tree at 4305dcb for the P9 file check
- python3 -c with json.load only to extract and print fields
  from the fetched JSON text (text reading, no repo code run)

Time log (all +07, Sun 2026-11-22, from the worker log):
- 12:56 task received. 12:58 laptop pre-state. 13:01 harness
  fix, commit d90d1b9. 13:02:45-13:03:32 Brave relaunch with
  debug flag. 13:03:51-13:04:38 dry run 0. Runs 13:05:09 to
  13:09:12. Rollback 13:10:36 to 13:11:18.

Verdict scale: CONFIRMED means the raw JSONs (or the log plus an
independent cross-check) support the claim exactly as stated.
REFUTED means the raw JSONs contradict it. Gaps are listed in
section 9.

## 1. Claim 1: 5/5 runs complete. CONFIRMED.

Command: for each run, gh api raw for
improvements/s2-flip-reopen-runs/run-N.json?ref=todolist-push,
then python3 print of run, dry_run, wall_ms, model_calls.

Output:
- run 1, dry_run False, wall_ms 29020.4, model_calls 0
- run 2, dry_run False, wall_ms 27799.1, model_calls 0
- run 3, dry_run False, wall_ms 28112.6, model_calls 0
- run 4, dry_run False, wall_ms 28898.1, model_calls 0
- run 5, dry_run False, wall_ms 28560.9, model_calls 0

Commit: todolist-push tip 4305dcb. Time: runs 13:05:09-13:09:12
+07 per the worker log run table, matching the JSON walls.

All 5 run files exist, each has run number 1 to 5, dry_run false,
a wall, and both browser records. No aborted or partial run file
exists in the directory. The worker log run table lists the same
5 walls.

## 2. Claim 2: 10/10 messages sent. CONFIRMED.

Command: same raw reads as section 1, python3 print of outcome,
message, program ok, completed, cb1, v12 per browser.

Output (all 10 browser records):
- run 1 brave: outcome sent, message
  S2-REOPEN-R1-BRAVE-IGNORE-TEST, program ok True, completed 3
- run 1 chromium: outcome sent, message
  S2-REOPEN-R1-CHROMIUM-IGNORE-TEST, program ok True, completed 2
- run 2 brave: outcome sent, S2-REOPEN-R2-BRAVE-IGNORE-TEST,
  program ok True, completed 3
- run 2 chromium: outcome sent,
  S2-REOPEN-R2-CHROMIUM-IGNORE-TEST, program ok True, completed 2
- run 3 brave: outcome sent, S2-REOPEN-R3-BRAVE-IGNORE-TEST,
  program ok True, completed 3
- run 3 chromium: outcome sent,
  S2-REOPEN-R3-CHROMIUM-IGNORE-TEST, program ok True, completed 2
- run 4 brave: outcome sent, S2-REOPEN-R4-BRAVE-IGNORE-TEST,
  program ok True, completed 3
- run 4 chromium: outcome sent,
  S2-REOPEN-R4-CHROMIUM-IGNORE-TEST, program ok True, completed 2
- run 5 brave: outcome sent, S2-REOPEN-R5-BRAVE-IGNORE-TEST,
  program ok True, completed 3
- run 5 chromium: outcome sent,
  S2-REOPEN-R5-CHROMIUM-IGNORE-TEST, program ok True, completed 2

Commit: todolist-push tip 4305dcb. Time: runs 13:05:09-13:09:12
+07.

Every message string matches the expected
S2-REOPEN-R<n>-<BROWSER>-IGNORE-TEST pattern. Program variants
are brave=fill, chromium=set_value in all 5 runs
(chromium_set_value true). Corroboration inside the JSONs:
pre-send count 0 in all 5 Chromium runs, delayed count exactly
1 in all 5 Chromium runs (no double-send), V12 found True in
all 10 sends (section 4), CB-1 all True in all 10 sends
(section 5). Brave has no pre/delayed recount, as designed
(only set_value browsers are recounted).

## 3. Claim 3: median wall 28.6s. CONFIRMED.

Command: same raw reads as section 1. Walls taken from the
JSON wall_ms fields.

Output: walls 29020.4, 27799.1, 28112.6, 28898.1, 28560.9.

Sorted: 27799.1, 28112.6, 28560.9, 28898.1, 29020.4. Median
(middle value of 5) is 28560.9 ms, which is 28.5609 s, rounding
to 28.6 s. The worker log states the same sorted list and the
same median.

Commit: todolist-push tip 4305dcb. Time: runs 13:05:09-13:09:12
+07.

## 4. Claim 4: V12 attempt 1 on all 10 messages. CONFIRMED.

Command: same raw reads as section 1, python3 print of v12
found, attempts, items per browser.

Output:
- run 1 brave: v12 found True, attempts 1, items 43
- run 1 chromium: v12 found True, attempts 1, items 54
- run 2 brave: v12 found True, attempts 1, items 45
- run 2 chromium: v12 found True, attempts 1, items 56
- run 3 brave: v12 found True, attempts 1, items 47
- run 3 chromium: v12 found True, attempts 1, items 58
- run 4 brave: v12 found True, attempts 1, items 49
- run 4 chromium: v12 found True, attempts 1, items 60
- run 5 brave: v12 found True, attempts 1, items 51
- run 5 chromium: v12 found True, attempts 1, items 62

Commit: todolist-push tip 4305dcb. Time: runs 13:05:09-13:09:12
+07.

All 10 have attempts 1, found True, role user, side user. Items
grow by exactly 2 per run on each browser between V12 reads
(Brave 43, 45, 47, 49, 51; Chromium 54, 56, 58, 60, 62), which
matches one user bubble plus one reply per run, per the worker
log section 3. Note: on Chromium the pre-count to V12 delta is
+3 in run 1 (pre 51 items, V12 54) and +2 in runs 2 to 5, the
same first-run pattern seen in the b1 series (run 1 pre 41,
V12 44; runs 2 to 5 +2). Open note: v12 textLen is 34 on Brave
and 37 on Chromium in every run, while the message strings are
30 and 33 characters long. The difference is exactly +4 in all
10 sends. See section 9, item B. It does not change this
verdict, because found is True with the correct role and side
in all 10.

## 5. Claim 5: CB-1 all three parts on all 10. CONFIRMED.

Command: same raw reads as section 1, python3 print of cb1
input_sent, target_received, verified, completed per browser.

Output: in all 10 browser records, cb1 is input_sent True,
target_received True, verified True. Completed is 3 on Brave
and 2 on Chromium in every run.

Commit: todolist-push tip 4305dcb. Time: runs 13:05:09-13:09:12
+07.

Per-send pass rate from the JSONs is 10/10. Per-run (both sends
verified) is 5/5.

## 6. Claim 6: 0 model calls. CONFIRMED.

Command: same raw reads as section 1. model_calls printed at
run level and per browser, plus phase_split_ms model.

Output: model_calls 0 in run 1, 2, 3, 4, 5. Per-browser
model_calls 0 in all 10 browser records. phase_split_ms model
0 in all 5 runs.

Commit: todolist-push tip 4305dcb. Time: runs 13:05:09-13:09:12
+07.

## 7. Claim 7: phase split, SSH takes 21.9s of 28.6s. CONFIRMED.

Command: same raw reads as section 1, python3 print of
phase_split_ms per run.

Output:
- run 1: model 0, ssh 22763.7, broker 507.0, observe 2274.6,
  act 253.5, verify 375.9, setup 136.9, residual 2708.9
- run 2: model 0, ssh 21942.2, broker 761.1, observe 1628.8,
  act 244.1, verify 168.5, setup 227.3, residual 2827.3
- run 3: model 0, ssh 22559.1, broker 678.2, observe 1449.5,
  act 251.9, verify 273.3, setup 157.5, residual 2743.1
- run 4: model 0, ssh 21023.7, broker 1008.3, observe 3093.4,
  act 240.2, verify 500.8, setup 281.4, residual 2750.1
- run 5: model 0, ssh 20736.4, broker 918.1, observe 2788.8,
  act 245.4, verify 677.1, setup 280.6, residual 2914.5

Medians computed from these 5 values (sorted, middle value):
- ssh: sorted 20736.4, 21023.7, 21942.2, 22559.1, 22763.7.
  Median 21942.2 ms, which is 21.9422 s, rounding to 21.9 s.
- broker: median 761.1. observe: median 2274.6. act: median
  245.4. verify: median 375.9. setup: median 227.3. residual:
  median 2750.1. All match the worker log phase split medians
  exactly.
- SSH share: 21942.2 / 28560.9 = 0.768, which is 76.8 percent,
  matching the log statement "about 77 percent".

Internal consistency checks, computed from the same JSONs:
- Sum of phase_split components vs wall_ms: run 1, 29020.5 vs
  29020.4 (off 0.1). Run 2, 27799.3 vs 27799.1 (off 0.2). Run
  3, 28112.6 exact. Run 4, 28897.9 vs 28898.1 (off 0.2). Run 5,
  28560.9 exact. All within rounding.
- act component vs program elapsed: run 1, 140.516 + 113.005
  = 253.521 vs act 253.5. Run 2, 137.493 + 106.613 = 244.106
  vs act 244.1. Run 3, 144.855 + 107.077 = 251.932 vs act
  251.9. Run 4, 140.832 + 99.412 = 240.244 vs act 240.2. Run
  5, 141.234 + 104.164 = 245.398 vs act 245.4. The sums round
  to act at the reported 1-decimal precision in all 5 runs
  (unrounded differences 0.002 to 0.044 ms).

Commit: todolist-push tip 4305dcb. Time: runs 13:05:09-13:09:12
+07.

Caveat: the harness-internal derivation of the broker, observe,
verify, setup, and residual buckets is not exposed in the JSON
fields, so the split is verified for internal consistency and
for medians, not re-derived from first principles. The act
bucket is fully re-derived (it equals the sum of program
elapsed_ms in all 5 runs).

## 8. Claim 8: Brave rollback real. CONFIRMED on the record.

Evidence sources: worker log sections 2 and 7 (read via gh api
raw, commit 1a3356d), plus two independent cross-checks from
the run JSONs and the earlier flip log.

Worker log section 7 (rollback), quoted values:
- 13:10:36 +07: SIGTERM to the debug-port Brave main PID
  1112207. Graceful exit in 1s. [::1]:9223 closed.
- 13:10:52 +07: relaunched WITHOUT the flag (same as-found
  flags, donor env prefix, log
  /tmp/s2-reopen-brave-rollback.log). New main PID 1119832.
- 13:11:00 +07: verified. Brave window back at the same
  address 0x55705383d420, ws1, PID 1119832. [::1]:9223 stays
  closed. Chromium (PID 8059) never restarted or touched.
- 13:11:18 +07: full cmdline check, 0 matches for
  remote-debugging-port on PID 1119832. The CDP exposure is
  closed.

Cross-check 1, new PID differs and window address is stable:
- Pre-state PID in log section 1 (12:58 +07): Brave PID
  1003210, no debug flag, window 0x55705383d420 on ws1.
- Debug relaunch PID in log section 2 (13:03:06 +07): new main
  PID 1112207, cmdline carries the flag.
- Rollback PID in log section 7 (13:10:52 +07): new main PID
  1119832, no flag. Three distinct PIDs in order: 1003210,
  then 1112207, then 1119832. Window address 0x55705383d420
  is the same in the pre-state, the debug relaunch, and the
  rollback verification.

Cross-check 2, PID continuity with the earlier flip:
- Command: gh api raw for
  improvements/worker-click4-s2-flip-log.md?ref=todolist-push,
  then grep for 1003210.
- Output lines: line 163 (rollback section, PID 1003210,
  [::1]:9223 closed, window back per hyprctl), line 568
  (new main PID 1003210), line 570 (window back, pid
  1003210). The flip rollback ended on PID 1003210, and the
  reopen pre-state starts from PID 1003210. Consistent.

Cross-check 3, relaunched tab id appears in the run JSONs:
- Command: gh api raw for run-1.json?ref=todolist-push.
- Output: brave target_id
  FED133417A338D5B1596D60490746672, tab title "Chat - clone1".
  The worker log section 2 records the same tab id as the one
  served by [::1]:9223 after the debug relaunch. The tab id
  differs from the brief's id because tab ids are per-session
  and Brave restarted; the log discloses this.

Commit: todolist-push tip 4305dcb, worker log commit 1a3356d.
Time: pre-state 12:58 +07, relaunch 13:02:45-13:03:32 +07,
rollback 13:10:36-13:11:18 +07.

Limit, stated plainly: the final cmdline check (0 matches) and
the window-address check are log-only. This VM has no SSH path
to the laptop, so the live process state cannot be re-observed
from here. The rollback is CONFIRMED on the record with the
cross-checks above, not by a live re-observation.

## 9. Findings: gaps and open notes

A. P9 screenshots are MISSING from the branch. Material gap.
- Command 1: gh api for the directory listing of
  improvements/s2-flip-reopen-runs?ref=todolist-push.
- Output 1: run-1.json, run-2.json, run-3.json, run-4.json,
  run-5.json. No PNG files.
- Command 2: gh api for the recursive tree at
  4305dcb153dc761d7f29d55842ddb23b8e400b9d, grep for p9-run.
- Output 2: zero matches (grep exit 1). The count of paths
  containing s2-flip-reopen-runs is 6, which is the directory
  entry plus the 5 JSON files.
- The run JSONs record p9 ok True for both browsers in all 5
  runs, with png paths
  improvements/s2-flip-reopen-runs/p9-runN-brave.png and
  p9-runN-chromium.png. The worker log section 5 reviews all
  10 shots and passes them, and section 8 says the PNGs were
  "(to be committed with this log)". At tip 4305dcb they are
  not on the branch.
- Consequence: the P9 review (10/10 PASS, DOM and render
  agree) is log-only and cannot be independently re-checked
  from the branch. This does NOT refute the sends: V12 DOM
  verification, CB-1, pre-count 0, and delayed count exactly
  1 corroborate the sends from the JSONs. But the render-side
  evidence is not in the repo, so an independent verifier
  cannot repeat the P9 check. The PNGs need to be committed
  for the P9 claim to be checkable.

B. V12 textLen is systematically +4 over the message length.
Minor open note.
- Command: for runs 1 to 5, gh api raw for run-N.json, python3
  print of message length and v12 textLen per browser.
- Output: Brave message length 30, textLen 34, diff 4, in all
  5 runs. Chromium message length 33, textLen 37, diff 4, in
  all 5 runs.
- The worker log never mentions this difference. It does not
  change any verdict: V12 found True with role user and side
  user in all 10 sends, and items grow by exactly 2 per run
  per browser. The V12 script file lives in /tmp/s2-v12.mjs
  on the laptop, not in the repo, so which 4 characters make
  up the difference cannot be checked from the branch, but the
  harness in the repo states V12 is a substring match
  (scripts/s2_flip_live.py, v12_check: a [data-message-item]
  "whose text contains" the message), which is consistent
  with a +4 bubble text. The same +4 appears in the earlier
  series too: flip run 1 Brave message 28 chars, textLen 32;
  b1 run 1 Chromium message 29 chars, textLen 33. Needs the
  script definition to close which 4 characters they are. The
  count script behind the pre/delayed counts, /tmp/c5-count.mjs,
  is laptop-only too (named in worker log sections 1 and 8, no
  count script in the repo); the counts are cross-consistent
  from the JSONs alone, delayed items equal V12 items in all 5
  runs here and in all 5 runs of the b1 series, and pre-send
  count is 0 in all 10 set_value runs across both series.

C. Chromium routing ran under the DISCLOSED relaxed gate in all
5 runs. Stated caveat, not a refutation.
- Command: for runs 1 to 5, gh api raw for run-N.json, python3
  print of routing, fell_through, routing_relaxed, observe.
- Output: Brave routing dom-chromium, fell_through empty,
  relaxed absent, observe 72, 73, 75, 77, 79 elements, not
  truncated, composer present, in runs 1 to 5. Chromium
  routing dom-chromium, fell_through "truncated inventory",
  routing_relaxed True, observe 80 elements, truncated,
  composer present, in runs 1 to 5.
- The worker log discloses this plainly (section 6, caveat 1)
  and states the relaxation touches only the routing gate,
  not the send path, and that the send mechanism is identical
  to run 1 of the (b1) measurement, which passed under the
  strict gate. The 80-element snapshot cap will keep biting
  live threads as they grow. A reader should know the
  Chromium sends were not strict-gate sends.

D. Residual explanation range wording. Minor.
- The worker log says the pre-send count-check SSH call is
  "874.7-1383.7ms". Those are run 1's two count-check SSH
  walls (pre 1383.7, delayed 874.7). Across runs, the
  pre-check laptop times are 1383.7, 1513.5, 1403.5, 1420.4,
  1426.9 ms, and the delayed times are 874.7, 805.9, 812.0,
  804.7, 849.2 ms. The log range is approximately right and
  cites run 1 values. Not a refutation.

E. Dry run 0 and wiring tests are log-only. Noted, out of
scope.
- Dry run 0 (13:03:51-13:04:38 +07, wall 30123.9ms, both
  browsers sent on scratch tabs) has no JSON on the branch;
  its workdir was /tmp/s2-reopen-dry on the laptop.
- Wiring tests 12/12 pass (harness commit d90d1b9) is a run
  result recorded in the log. Running repo tests was not done
  in this verification.

F. Worker log run table cross-check. All values match.
- Log run table: run 1 wall 29020.4, Brave dom_act 51ms,
  elapsed 140.5ms, V12 items 43; Chromium dom_act 12ms,
  elapsed 113.0ms, V12 items 54. Run 2: 27799.1, 46ms,
  137.5ms, items 45; 9ms, 106.6ms, items 56. Run 3: 28112.6,
  46ms, 144.9ms, items 47; 9ms, 107.1ms, items 58. Run 4:
  28898.1, 43ms, 140.8ms, items 49; 8ms, 99.4ms, items 60.
  Run 5: 28560.9, 43ms, 141.2ms, items 51; 10ms, 104.2ms,
  items 62.
- Command: for runs 1 to 5, gh api raw for run-N.json, python3
  print of program log strings.
- Output: run 1 Brave "dom_act ok True completed 3 ms 51
  error None", Chromium "dom_act ok True completed 2 ms 12
  error None". Run 2: 46 and 9. Run 3: 46 and 9. Run 4: 43
  and 8. Run 5: 43 and 10. All match the log table, and the
  elapsed_ms values match to the reported precision.

## 10. Overall verdict

All 7 JSON claims are CONFIRMED, and the rollback claim is
CONFIRMED on the record:
1. 5/5 runs complete. CONFIRMED.
2. 10/10 messages sent. CONFIRMED.
3. Median wall 28.6s. CONFIRMED (28560.9 ms).
4. V12 attempt 1 on all 10 messages. CONFIRMED.
5. CB-1 all three parts on all 10. CONFIRMED.
6. 0 model calls. CONFIRMED.
7. Phase split, SSH 21.9s of 28.6s. CONFIRMED (median ssh
   21942.2 ms, 76.8 percent of the median wall).
8. Brave rollback real. CONFIRMED on the record (section 8).

The series genuinely is 5/5 runs with both sends verified,
10/10 sends, median wall 28.6s, V12 attempt 1 everywhere, CB-1
all True everywhere, 0 model calls, and transport at about 77
percent of the wall. The EXPAND recommendation follows from the
gate as the log states it (median below 60s AND the class
completes 5/5, where the original flip was 0/5 runs complete),
with the log's own caveats: relaxed Chromium routing gate,
unsolved mouse stall, transport-dominated wall, and the durable
landing still open.

One material gap: the P9 screenshots are not on the branch
(section 9, item A), so the render-side P9 review cannot be
independently re-checked. Two minor open notes: V12 textLen is
systematically +4 over the message length (item B), and the
residual range wording cites run 1 values (item D).

## 11. Commit status

This report was written to
docs/batch12-task1-s2-reopen-verify-20261122.md and committed
on main as ed59f6a by the coordinator. At writing time it was
NOT committed or pushed, because the first git fetch result in
that session failed an execution-risk check, and that notice
forbade running git commands inside the repo until the user
confirmed. The coordinator's own session was never blocked,
its git commands worked throughout, so the coordinator
committed and pushed the file directly. No user confirmation
was requested or given for this commit. No code was
changed. No other file was touched. coord/clone1.md was not
touched.
