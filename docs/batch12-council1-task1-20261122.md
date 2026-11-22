# Batch 12 council 1: task 1 review

## 0. Scope and method

Task: council 1 review of docs/batch12-task1-s2-reopen-verify-20261122.md
(commit ed59f6a on main, 428 lines). Verify every number in it against
the primary sources, first-hand, and mark each claim CONFIRMED or REFUTED
with the command run and its output.

Sources read, all from branch todolist-push, read-only:
- improvements/s2-flip-reopen-runs/run-1..5.json
- improvements/worker-click5-s2-reopen-log.md (worker log, commit 1a3356d)
- improvements/worker-click4-s2-flip-log.md (PID continuity cross-check)

Branch state at review time:
- todolist-push tip: 4305dcb153dc761d7f29d55842ddb23b8e400b9d
- main tip: ed59f6a (the task 1 report itself)

Read method: git fetch worked in this session with no execution-risk
check, so the JSONs and logs were read directly with git show from
origin/todolist-push. One check (the P9 tree absence) was replicated
with the GitHub recursive tree API exactly as the task 1 author did it,
because git ls-tree -r lists blobs only while the recursive tree API
also lists the directory entry. No repo code was run, tested, imported,
or loaded. No file besides this review was written.

Verification script: ~/workspace/b12c1-scratch/verify.py, run with
python3. It reads all 5 run JSONs through git show and checks 296
assertions. Result: 294 PASS, 2 apparent FAIL, both resolved below as
checker artifacts, not report errors. The script was kept out of the
repo.

## 1. Claim 1: 5/5 runs complete. CONFIRMED.

Command: python3 ~/workspace/b12c1-scratch/verify.py, section C1.
It runs git show origin/todolist-push:improvements/s2-flip-reopen-runs/run-N.json
for N 1 to 5, then json.load and prints run, dry_run, wall_ms, model_calls.

Output:
- run 1, dry_run False, wall_ms 29020.4, model_calls 0
- run 2, dry_run False, wall_ms 27799.1, model_calls 0
- run 3, dry_run False, wall_ms 28112.6, model_calls 0
- run 4, dry_run False, wall_ms 28898.1, model_calls 0
- run 5, dry_run False, wall_ms 28560.9, model_calls 0

All 5 files exist, each has run number 1 to 5, dry_run false, a wall,
and both browser records. Walls match the report exactly. The directory
listing from the recursive tree API shows only run-1.json to run-5.json,
no aborted or partial run file.

## 2. Claim 2: 10/10 messages sent. CONFIRMED.

Command: same script, section C2. It prints outcome, message, program
ok, completed, program_variant, chromium_set_value, pre_count, and
delayed_count per browser.

Output (all 10 browser records):
- run 1 brave: outcome sent, message S2-REOPEN-R1-BRAVE-IGNORE-TEST,
  program ok True, completed 3, program_variant fill
- run 1 chromium: outcome sent, message
  S2-REOPEN-R1-CHROMIUM-IGNORE-TEST, program ok True, completed 2,
  program_variant set_value
- run 2 brave: outcome sent, S2-REOPEN-R2-BRAVE-IGNORE-TEST, program
  ok True, completed 3, fill
- run 2 chromium: outcome sent, S2-REOPEN-R2-CHROMIUM-IGNORE-TEST,
  program ok True, completed 2, set_value
- run 3 brave: outcome sent, S2-REOPEN-R3-BRAVE-IGNORE-TEST, program
  ok True, completed 3, fill
- run 3 chromium: outcome sent, S2-REOPEN-R3-CHROMIUM-IGNORE-TEST,
  program ok True, completed 2, set_value
- run 4 brave: outcome sent, S2-REOPEN-R4-BRAVE-IGNORE-TEST, program
  ok True, completed 3, fill
- run 4 chromium: outcome sent, S2-REOPEN-R4-CHROMIUM-IGNORE-TEST,
  program ok True, completed 2, set_value
- run 5 brave: outcome sent, S2-REOPEN-R5-BRAVE-IGNORE-TEST, program
  ok True, completed 3, fill
- run 5 chromium: outcome sent, S2-REOPEN-R5-CHROMIUM-IGNORE-TEST,
  program ok True, completed 2, set_value

Also confirmed: program_variant "brave=fill,chromium=set_value" and
chromium_set_value true in all 5 runs; Chromium pre_count count 0 in
all 5 runs; delayed_count chromium count 1 in all 5 runs. Every message
string matches S2-REOPEN-R<n>-<BROWSER>-IGNORE-TEST exactly.

## 3. Claim 3: median wall 28.6s. CONFIRMED.

Command: same script, section C3. Walls taken from the JSON wall_ms
fields.

Output: walls [29020.4, 27799.1, 28112.6, 28898.1, 28560.9]. Sorted:
[27799.1, 28112.6, 28560.9, 28898.1, 29020.4]. Median (middle value
of 5) is 28560.9 ms, which is 28.5609 s, rounding to 28.6 s. Matches
the report and the worker log.

## 4. Claim 4: V12 attempt 1 on all 10 messages. CONFIRMED.

Command: same script, section C4. It prints v12 found, attempts,
items, role, side, textLen per browser, and the message length.

Output:
- run 1 brave: v12 found True, attempts 1, items 43, role user,
  side user, textLen 34
- run 1 chromium: v12 found True, attempts 1, items 54, role user,
  side user, textLen 37
- run 2 brave: found True, attempts 1, items 45, textLen 34
- run 2 chromium: found True, attempts 1, items 56, textLen 37
- run 3 brave: found True, attempts 1, items 47, textLen 34
- run 3 chromium: found True, attempts 1, items 58, textLen 37
- run 4 brave: found True, attempts 1, items 49, textLen 34
- run 4 chromium: found True, attempts 1, items 60, textLen 37
- run 5 brave: found True, attempts 1, items 51, textLen 34
- run 5 chromium: found True, attempts 1, items 62, textLen 37

Items grow by exactly 2 per run on each browser (Brave 43, 45, 47, 49,
51; Chromium 54, 56, 58, 60, 62). Message lengths are 30 on Brave and
33 on Chromium in every run, so textLen is +4 in all 10 sends, exactly
as the report notes in section 9, item B.

## 5. Claim 5: CB-1 all three parts on all 10. CONFIRMED.

Command: same script, section C5. It prints cb1 input_sent,
target_received, verified, completed per browser.

Output: in all 10 browser records, cb1 is input_sent True,
target_received True, verified True. Completed is 3 on Brave and 2 on
Chromium in every run. Per-send pass rate 10/10, per-run (both sends
verified) 5/5.

## 6. Claim 6: 0 model calls. CONFIRMED.

Command: same script, section C6. It prints model_calls at run level,
per browser, and phase_split_ms model.

Output: model_calls 0 in runs 1, 2, 3, 4, 5. Per-browser model_calls 0
in all 10 browser records. phase_split_ms model 0 in all 5 runs.

## 7. Claim 7: phase split, SSH takes 21.9s of 28.6s. CONFIRMED.

Command: same script, section C7. It prints phase_split_ms per run,
computes medians, the SSH share, the per-run split sum against the
wall, and act against the program elapsed sum.

Output, phase_split_ms per run:
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

Medians (sorted, middle value of 5):
- ssh: sorted 20736.4, 21023.7, 21942.2, 22559.1, 22763.7.
  Median 21942.2 ms, 21.9422 s, rounding to 21.9 s.
- broker: median 761.1. observe: median 2274.6. act: median 245.4.
  verify: median 375.9. setup: median 227.3. residual: median 2750.1.
  All match the report and the worker log exactly.
- SSH share: 21942.2 / 28560.9 = 0.768, 76.8 percent, matching the
  log statement "about 77 percent".

Internal consistency, split sum vs wall_ms:
- run 1: sum 29020.5 vs wall 29020.4, off 0.1
- run 2: sum 27799.3 vs wall 27799.1, off 0.2
- run 3: sum 28112.6 vs wall 28112.6, exact
- run 4: sum 28897.9 vs wall 28898.1, off 0.2
- run 5: sum 28560.9 vs wall 28560.9, exact
All within 0.2 ms at the reported 1-decimal precision.

Act vs program elapsed sum (Brave elapsed + Chromium elapsed):
- run 1: 140.516 + 113.005 = 253.521 vs act 253.5
- run 2: 137.493 + 106.613 = 244.106 vs act 244.1
- run 3: 144.855 + 107.077 = 251.932 vs act 251.9
- run 4: 140.832 + 99.412 = 240.244 vs act 240.2
- run 5: 141.234 + 104.164 = 245.398 vs act 245.4
Exact in all 5 runs to the reported precision.

Note on the first run of the script: the run 2 sum check flagged
FAIL because binary floating point gives 0.2000000000007276, which
is above a strict 0.2 cutoff. At the reported 1-decimal precision
the difference is exactly 0.2, so the report claim "off 0.2" and
"within 0.2 ms" is correct. This was a checker artifact, not a
report error.

The caveat in the report stands: the broker, observe, verify, setup,
and residual buckets are not re-derivable from the JSON fields, so the
split is verified for internal consistency and medians, not from first
principles. The act bucket is fully re-derived.

## 8. Claim 8: Brave rollback real. CONFIRMED on the record.

Command: git show origin/todolist-push:improvements/worker-click5-s2-reopen-log.md,
then grep and sed for the rollback section; plus the verify script
section C8 for the tab id and the flip log PID lines.

Worker log section 7 (rollback), read verbatim:
- 13:10:36 +07, T+14m: SIGTERM to the debug-port Brave main PID
  1112207. Graceful exit in 1s; no brave process remains.
  [::1]:9223 closed.
- 13:10:52 +07, T+15m: relaunched WITHOUT the flag (same as-found
  flags, donor env prefix, log /tmp/s2-reopen-brave-rollback.log).
  New main PID 1119832.
- 13:11:00 +07: verified. Brave window back at the same address
  0x55705383d420, ws1, PID 1119832. [::1]:9223 stays closed.
  Chromium (clone2, PID 8059) never restarted or touched; its tab
  D1374C7C994D3DA72678E20C7FD099A0 still serving on 127.0.0.1:9223.
- 13:11:18 +07: full cmdline check: 0 matches for
  remote-debugging-port on PID 1119832. The CDP exposure is closed.

Cross-check 1, three distinct PIDs in order with a stable window:
- Pre-state (log line 84, 12:58 +07): Brave PID 1003210, no debug
  flag, window 0x55705383d420 on ws1.
- Debug relaunch (log line 129, 13:03:06 +07): new main PID 1112207,
  cmdline carries the flag.
- Rollback (log lines 310-314, 13:10:52 +07): new main PID 1119832,
  no flag. Window address 0x55705383d420 is the same in all three.

Cross-check 2, PID continuity with the earlier flip:
- Command: git show origin/todolist-push:improvements/worker-click4-s2-flip-log.md,
  grep for 1003210.
- Output lines: 163, 568, 570. Line 163 is the flip rollback section
  (PID 1003210, [::1]:9223 closed, window back per hyprctl). The
  flip rollback ended on PID 1003210, and the reopen pre-state starts
  from PID 1003210. Consistent.

Cross-check 3, relaunched tab id appears in the run JSONs:
- Command: verify script section C8, prints brave target_id per run.
- Output: FED133417A338D5B1596D60490746672 in runs 1, 2, 3, 4, 5.
  The worker log line 131 records the same tab id ("Chat - clone1")
  as the one served by [::1]:9223 after the debug relaunch.

Same limit as the report: the final cmdline check (0 matches) and the
window-address check are log-only. This VM has no SSH path to the
laptop, so the live process state cannot be re-observed from here.
CONFIRMED on the record with the cross-checks above, not by a live
re-observation.

## 9. Findings re-check (report section 9, items A to F)

A. P9 screenshots MISSING from the branch. CONFIRMED as a material gap.
- Command 1: gh api repos/phamTuan207/computer-use-wayland/git/trees/4305dcb153dc761d7f29d55842ddb23b8e400b9d?recursive=1,
  jq select paths containing s2-flip-reopen-runs.
- Output 1: 6 entries, tree improvements/s2-flip-reopen-runs plus
  blobs run-1.json, run-2.json, run-3.json, run-4.json, run-5.json.
  No PNG files.
- Command 2: same tree, jq select paths containing p9-run.
- Output 2: zero matches.
- Note on the first run of the script: git ls-tree -r lists blobs
  only, so it counted 5 paths and flagged FAIL. The recursive tree
  API lists the directory entry too, giving 6, exactly as the report
  states. This was a checker artifact, not a report error.
- The run JSONs record p9 ok True for both browsers in all 5 runs,
  with png paths improvements/s2-flip-reopen-runs/p9-runN-brave.png
  and p9-runN-chromium.png. The PNGs are not on the branch at tip
  4305dcb, so the P9 review (10/10 PASS, DOM and render agree) is
  log-only and cannot be independently re-checked. This does not
  refute the sends: V12, CB-1, pre-count 0, and delayed count 1
  corroborate them from the JSONs.

B. V12 textLen systematically +4 over the message length. CONFIRMED
as a minor open note.
- Command: verify script section C4. Brave message length 30,
  textLen 34, diff 4, in all 5 runs. Chromium message length 33,
  textLen 37, diff 4, in all 5 runs. The worker log never mentions
  this difference. It does not change any verdict.

C. Chromium routing ran under the DISCLOSED relaxed gate in all 5 runs.
CONFIRMED as a stated caveat.
- Command: verify script section C9C. Brave routing dom-chromium,
  fell_through empty, routing_relaxed absent, observe 72, 73, 75, 77,
  79 elements, not truncated, composer present, in runs 1 to 5.
  Chromium routing dom-chromium, fell_through "truncated inventory",
  routing_relaxed True, observe 80 elements, truncated, composer
  present, in runs 1 to 5. Matches the report exactly.

D. Residual explanation range wording. CONFIRMED as a minor note.
- Command: verify script section C9D. Pre-check laptop times are
  1383.7, 1513.5, 1403.5, 1420.4, 1426.9 ms. Delayed times are
  874.7, 805.9, 812.0, 804.7, 849.2 ms. The log range "874.7-1383.7ms"
  cites run 1 values. Approximately right, not a refutation.

E. Dry run 0 and wiring tests are log-only. CONFIRMED as noted, out
of scope.
- Command: git ls-tree -r --name-only origin/todolist-push, grep for
  dry and s2-reopen.
- Output: improvements/worker-click5-s2-reopen-log.md and
  improvements/worker-y8-stop-dryrun.sh only. No dry run JSON on the
  branch. Wiring tests 12/12 is a log-recorded run result, not
  re-run here.

F. Worker log run table cross-check. CONFIRMED, all values match.
- Command: verify script section C9F. Program log strings per run:
  run 1 Brave "dom_act ok True completed 3 ms 51 error None",
  Chromium "dom_act ok True completed 2 ms 12 error None". Run 2:
  46 and 9. Run 3: 46 and 9. Run 4: 43 and 8. Run 5: 43 and 10.
  Elapsed ms: Brave 140.516, 137.493, 144.855, 140.832, 141.234;
  Chromium 113.005, 106.613, 107.077, 99.412, 104.164. All match
  the log table to the reported precision. All 5 wall values
  (29020.4, 27799.1, 28112.6, 28898.1, 28560.9) appear in the
  worker log text.

## 10. Report metadata check

- todolist-push tip hash: git rev-parse origin/todolist-push gives
  4305dcb153dc761d7f29d55842ddb23b8e400b9d, matching the report.
- Commit messages, git log origin/todolist-push -4: 4305dcb "docs:
  COORD-CLICK-5 log, S2-REOPEN verified 5/5 median 28.6s, EXPAND
  approved in principle, clone1 batch 12 queued", 212e0ad "C5-S2-REOPEN
  log: record own commit hash 1a3356d", 1a3356d "C5-S2-REOPEN log:
  two-browser flip re-opens 5/5 runs, median wall 28.6s, recommend
  EXPAND", 507a50b "C5-P2-AMEND-FIX items 1,3,4". All match.
- Harness commit: git log --all grep d90d1b9 gives "C5-S2-REOPEN:
  harness --chromium-set-value (Brave fill, Chromium set_value)".
  Matches.

## 11. Overall verdict

All 8 numbered claims in the task 1 report are CONFIRMED:
1. 5/5 runs complete. CONFIRMED.
2. 10/10 messages sent. CONFIRMED.
3. Median wall 28.6s. CONFIRMED (28560.9 ms).
4. V12 attempt 1 on all 10 messages. CONFIRMED.
5. CB-1 all three parts on all 10. CONFIRMED.
6. 0 model calls. CONFIRMED.
7. Phase split, SSH 21.9s of 28.6s. CONFIRMED (median ssh 21942.2
   ms, 76.8 percent of the median wall).
8. Brave rollback real. CONFIRMED on the record.

All 6 findings in report section 9 are CONFIRMED as stated: A, the
P9 screenshots are missing from the branch (material gap); B, V12
textLen is +4 (minor open note); C, Chromium routing used the
disclosed relaxed gate (stated caveat); D, the residual range wording
cites run 1 values (minor); E, dry run 0 and wiring tests are
log-only (noted, out of scope); F, the worker log run table matches
the JSONs (all values match).

No claim is REFUTED. No number in the report needed correction.
The two apparent FAILs in the first script run were checker artifacts
in this review (binary float comparison on the run 2 split sum, and
git ls-tree -r omitting the directory entry in the reopen path
count), both resolved with direct evidence in sections 7 and 9A.

Council 1 verdict: the task 1 report STANDS. No fix pass items from
this council.

## 12. Commit status

This review was written to docs/batch12-council1-task1-20261122.md
and committed as "Batch 12 council 1 task 1" on main, pushed to
origin/main. No other file was touched. coord/clone1.md was not
touched. todolist-push was not modified.
