# Batch 12 redteam task 1: S2 reopen verification review

## 0. Scope and method

Target: docs/batch12-task1-s2-reopen-verify-20261122.md, commit
ed59f6a on main, 428 lines. Task 1 agent verified the S2 reopen
run series from the raw JSONs on branch todolist-push. This review
is adversarial: every load-bearing claim was re-checked against
the primary sources, not against the task 1 report.

Method: git read-only from branch todolist-push (fetch worked in
this session; no repo code was run, tested, imported, or loaded).
Files read with git show into /tmp scratch and printed with
python3 json.load only:
- improvements/s2-flip-reopen-runs/run-1..5.json
- improvements/worker-click5-s2-reopen-log.md (347 lines)
- improvements/worker-click4-s2-flip-log.md (PID cross-check)
- improvements/s2-flip-runs/run-1..5.json, improvements/s2-flip-b1-runs/run-1..5.json, improvements/s2-flip-a1-runs/run-1..5.json (cross-series checks)
- scripts/s2_flip_live.py at todolist-push (V12 match semantics)
- Commit 4305dcb diff (COORD-CLICK-5 log, EXPAND decision)
- git ls-tree of the full todolist-push tree (P9 absence check)

Branch state at review time: todolist-push tip 4305dcb, unchanged
from the task 1 report. Main HEAD at review time ed59f6a plus
watchdog commits.

Verdict scale: BREAKING means a finding overturns a CONFIRMED
verdict or the overall verdict. MINOR means a wrong fact, wrong
explanation, or gap that does not change any verdict.

## 1. What held: the numbers all reproduce

Claim by claim, re-derived from the raw JSONs:

- 5/5 runs complete, walls 29020.4, 27799.1, 28112.6, 28898.1,
  28560.9, dry_run False, model_calls 0. Report section 1
  correct. Directory holds exactly run-1..5.json, no aborted or
  partial file.
- Median wall: sorted 27799.1, 28112.6, 28560.9, 28898.1,
  29020.4. Middle value 28560.9 ms, 28.5609 s, rounds to 28.6 s.
  Report section 3 correct.
- 10/10 sent. All messages match S2-REOPEN-R<n>-<BROWSER>-
  IGNORE-TEST exactly. Program ok True everywhere, completed 3
  Brave and 2 Chromium every run. chromium_set_value True at run
  level in all 5 runs, per-browser program_variant fill on Brave
  and set_value on Chromium in all 5 runs. Pre-send count 0 and
  delayed count exactly 1 in all 5 Chromium runs. Report
  section 2 correct.
- V12 attempt 1, found True, role user, side user in all 10.
  Items exactly as stated: Brave 43, 45, 47, 49, 51; Chromium
  54, 56, 58, 60, 62. Report section 4 numbers correct.
- CB-1 all three True in all 10, completed 3 Brave and 2
  Chromium. Per-send pass 10/10, per-run 5/5. Report section 5
  correct.
- 0 model calls at run level, per browser, and phase model 0 in
  all 5 runs. Report section 6 correct.
- Phase split medians, re-sorted from the JSONs: ssh 21942.2,
  broker 761.1, observe 2274.6, act 245.4, verify 375.9, setup
  227.3, residual 2750.1. All match the report. SSH share
  21942.2 / 28560.9 = 0.7682, 76.8 percent. Report section 7
  correct.
- Phase sums vs wall: run 1, 29020.5 vs 29020.4 (off 0.1); run
  2, 27799.3 vs 27799.1 (off 0.2); run 3 exact; run 4, 28897.9
  vs 28898.1 (off 0.2); run 5 exact. Within rounding, as the
  report says.
- Act vs program elapsed sums: run 1, 140.516 + 113.005 =
  253.521 vs act 253.5; run 2, 137.493 + 106.613 = 244.106 vs
  244.1; run 3, 144.855 + 107.077 = 251.932 vs 251.9; run 4,
  140.832 + 99.412 = 240.244 vs 240.2; run 5, 141.234 +
  104.164 = 245.398 vs 245.4. All round to act at 1 decimal.
  Report section 7 correct, subject to wording nit M4.
- Worker log run table cross-check (report section 9F): dom_act
  ms from the JSON program log strings are 51/12, 46/9, 46/9,
  43/8, 43/10, and elapsed values match to the reported
  precision. Correct.
- Per-browser wall medians stated in the worker log, not in the
  task 1 report, also reproduce: Brave walls 3844.0, 3258.9,
  3699.4, 3959.7, 3526.6, median 3699.4; Chromium walls 6362.7,
  6243.9, 6207.1, 6225.3, 6960.4, median 6243.9.
- Rollback (report section 8): all three PIDs and the window
  address check out against the worker log. Pre-state Brave PID
  1003210, no flag, window 0x55705383d420 on ws1 (log section
  1). Debug relaunch PID 1112207, tab
  FED133417A338D5B1596D60490746672, "Chat - clone1" (log section
  2), and the same tab id is in run-1.json. Rollback PID
  1119832, same window address, [::1]:9223 closed, cmdline
  check 0 matches at 13:11:18 (log section 7). Flip log grep
  for 1003210 returns exactly lines 163, 568, 570 as the report
  states. The report correctly labels the final cmdline and
  window checks log-only and states this VM has no SSH path to
  re-observe the laptop. No finding: the limit is disclosed.
- Time log (report section 0): 12:56 task received, 12:58
  pre-state, 13:01 harness fix d90d1b9, 13:02:45-13:03:32
  relaunch, 13:03:51-13:04:38 dry run 0 wall 30123.9ms, runs
  13:05:09-13:09:12, rollback 13:10:36-13:11:18. All match the
  worker log sections 0, 1, 2, 3, 7. Wiring tests 12/12 match
  log section 1.
- Branch state (report section 0): tip 4305dcb, worker log
  commit 1a3356d, harness d90d1b9, follow-up 212e0ad. All
  correct. Tip commit message matches.
- P9 absence (report section 9A): correct, and re-checked from
  the right tree. The reopen directory holds only the 5 JSONs.
  Full-tree grep for "p9" returns zero paths. The only PNGs on
  todolist-push are unrelated (docs/benchmarks and test
  fixtures). Commit 1a3356d, the worker log commit, contains
  exactly 6 files (5 run JSONs plus the log) and no PNGs, even
  though the log section 8 says the PNGs were "(to be committed
  with this log)". The report's "6 paths" count is the 5 JSON
  files plus the directory tree entry in the GitHub recursive
  tree API; git ls-tree shows the same tree entry. The JSONs
  record p9 ok True for both browsers in all 5 runs with the
  stated png paths. The material gap stands: the P9 review is
  log-only and cannot be re-checked from the branch.
- Relaxed routing gate (report section 9C): Brave observe 72,
  73, 75, 77, 79 elements, not truncated, composer present, all
  5 runs. Chromium observe 80 elements, truncated, routing
  relaxed True, fell_through "truncated inventory", composer
  present, all 5 runs. Correct, subject to wording slip M3.
- Residual range wording (report section 9D): pre-check laptop
  times 1383.7, 1513.5, 1403.5, 1420.4, 1426.9 ms and delayed
  times 874.7, 805.9, 812.0, 804.7, 849.2 ms. All correct, and
  the log range does cite run 1 values. Correct.
- Overall verdict (report section 10): the EXPAND conclusion
  follows. The coordinator log at 4305dcb states it directly:
  "DECISION (coordinator): EXPAND APPROVED IN PRINCIPLE,
  SEQUENCED AFTER LANDING. The gate is met (median 28.6s <
  60s, class completes 5/5)". The original flip was 0/5 runs
  complete per run, confirmed from the flip log verdict. Note:
  the flip log section 0 gate text states only the median
  condition ("Below a 60s median, S2 is still improving and
  the class expands"); the completeness condition comes from
  the flip verdict precedent and the coordinator decision, not
  from the gate text alone. The report's attribution is loose
  but the conclusion is backed by the coordinator's own words.

## 2. Findings

Breaking findings: 0.
Minor findings: 5.

### M1. Section 4, lines 150-152: items-growth explanation is wrong, and the run-1 Chromium delta is unaddressed. MINOR.

Report text: "Items grow by exactly 2 per run on each browser
(Brave 43, 45, 47, 49, 51; Chromium 54, 56, 58, 60, 62), which
matches one new user bubble per run per thread."

Two errors in that sentence.

First, arithmetic: +2 items per run cannot be explained by one
new user bubble. One new bubble adds one item. The worker log
itself gives the correct explanation in section 3: "the Brave
thread grows by one user bubble plus clone1's reply per run".
The report's explanation contradicts its own numbers and the
log it read.

Second, the "exactly 2" pattern does not hold within run 1 on
Chromium. From the run JSONs: run 1 Chromium pre_count items
51, V12 items 54, a delta of +3, while runs 2 to 5 are +2
(54 to 56, 56 to 58, 58 to 60, 60 to 62). The report never
mentions the +3. The V12-to-V12 sequence is +2 in every run,
but the pre-to-V12 delta in run 1 is +3.

Cross-check done by this review: the b1 series shows the
identical pattern. b1 run 1 Chromium pre items 41, V12 items
44, delta +3; runs 2 to 5 delta +2 (44 to 46, 46 to 48, 48 to
50, 50 to 52). So the run-1 +3 is a systematic first-run
artifact across series, not a reopen defect. The likely cause
is an item landing between the pre-count and the V12 read on
the first run of a series (the worker log section 5 notes
clone1's task-4 agent replying live in the Brave thread and
cap banners in the Chromium thread), but no source on the
branch proves which item it was.

Why MINOR, not BREAKING: the no-double-send evidence is the
message count, not the items delta. Pre-send count is 0 and
delayed count is exactly 1 in all 5 Chromium runs in both the
reopen and b1 series, and delayed items equal V12 items in
every run of both series. The sends stand; only the report's
gloss is wrong.

Fix: replace "one new user bubble" with "one user bubble plus
one reply per run, per the worker log section 3", and add a
line noting the run-1 Chromium pre-to-V12 delta of +3, with
the b1 cross-check showing the same first-run pattern.

### M2. Section 9 item B, line 334: the textLen definition is partly checkable from the branch. MINOR.

Report text: "The V12 script that defines textLen lives in
/tmp/s2-v12.mjs on the laptop, not in the repo, so its
definition cannot be checked from the branch."

Partly wrong. The script file itself is indeed not in the repo
(no s2-v12 file exists anywhere on todolist-push; the harness
at scripts/s2_flip_live.py:72 sets LAPTOP_V12 =
'/tmp/s2-v12.mjs'). But the harness in the repo does state the
match semantics: lines 316-327, V12 looks for a
[data-message-item] "whose text contains" the message. A
substring match means the found bubble's text can legitimately
be longer than the message, so textLen +4 is consistent with
repo-visible semantics. Only which 4 characters make up the
difference is uncheckable from the branch.

Cross-check done by this review, strengthening the report's
"harmless" judgment: the +4 appears in all three series.
Flip Brave: message length 28, textLen 32. b1 Chromium:
message length 29, textLen 33. Reopen Brave: 30 to 34.
Reopen Chromium: 33 to 37. The flip series passed P9 visual
review with the same +4, so the +4 predates the reopen and is
not a reopen matching error.

Why MINOR: the report's conclusion (does not change any
verdict) is right and is now better supported. Only the
"cannot be checked" claim overstates the gap.

Fix: soften to "the script file is not in the repo, so which
4 characters make up the difference cannot be checked; the
harness states V12 is a substring match, which is consistent
with a +4 bubble text", and add the three-series cross-check.

### M3. Section 9C, line 339: command range does not match the output. MINOR.

Report text: "Command: for runs 2 to 5, gh api raw for
run-N.json, python3 print of routing, fell_through,
routing_relaxed, observe. Output: ... observe 72, 73, 75, 77,
79 elements ... in runs 1 to 5."

The output lists five observe values covering runs 1 to 5, so
the command as stated (runs 2 to 5) cannot have produced it.
The values themselves are all correct against the JSONs. This
is a method-description slip, not a data error.

Fix: change "for runs 2 to 5" to "for runs 1 to 5".

### M4. Section 7, line 222: "Exact" overstates the act check. MINOR.

Report text: "act component vs program elapsed: run 1,
140.516 + 113.005 = 253.521 vs act 253.5 ... Exact in all 5
runs to the reported precision."

The sums differ from act before rounding: run 1 off 0.021,
run 2 off 0.006, run 3 off 0.032, run 4 off 0.044, run 5 off
0.002 ms. The qualifier "to the reported precision" saves
the sentence, since act is reported to 1 decimal and every
sum rounds to it. But the word "Exact" standing alone would
be false. This is a wording nit; the check itself is sound.

Fix: write "rounds to act at the reported 1-decimal precision
in all 5 runs" instead of "Exact".

### M5. Omission: the count script is laptop-only too, and the report never says so. MINOR.

The report flags the V12 script as laptop-only (item B) but
never notes that the pre/delayed count script is equally
laptop-only. The worker log sections 1 and 8 name
/tmp/c5-count.mjs as a laptop helper, and no count script
exists in the repo. The count definitions behind the
no-double-send evidence (pre 0, delayed exactly 1) are
therefore also uncheckable from the branch.

Why MINOR: the counts are cross-consistent from the JSONs
alone. Delayed items equal V12 items in all 5 runs of the
reopen series and in all 5 runs of the b1 series, pre-send
count is 0 in all 10 set_value runs across both series, and
the V12 found results agree with the counts everywhere. The
gap is in the report's gap list, not in the evidence.

Fix: add one line to section 9 noting /tmp/c5-count.mjs is
laptop-only like /tmp/s2-v12.mjs, with the cross-consistency
above as the mitigation.

## 3. Verdict: SURVIVES

Breaking findings: 0. Minor findings: 5 (M1-M5).

All 8 claims in the task 1 report reproduce exactly from the
raw JSONs: 5/5 runs, 10/10 sends, median wall 28560.9 ms,
V12 attempt 1 everywhere with the stated item counts, CB-1
all True everywhere, 0 model calls, phase split medians and
SSH share 76.8 percent, and the Brave rollback confirmed on
the record with its log-only limit properly disclosed. The
P9 screenshots really are missing from the branch, and the
report is right to call that a material gap. The EXPAND
conclusion is backed by the coordinator's own decision at
4305dcb, not only by the worker log.

The 5 minor findings are a wrong explanation of the items
growth (M1), an overstated uncheckability claim for textLen
(M2), a command-range slip (M3), an "Exact" wording nit (M4),
and an omitted laptop-only note for the count script (M5).
None of them changes any CONFIRMED verdict or the overall
verdict. The report survives with those fixes applied.

## 4. Review status

This review was written to
docs/batch12-redteam-task1-20261122.md. No other file was
touched. coord/clone1.md was not touched. No personal
information in this file. No em dash or en dash anywhere.
