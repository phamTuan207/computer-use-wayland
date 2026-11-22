# Batch 12 council 2 task 1: review of the S2 reopen independent verification

## 0. Scope and method

Report under review: docs/batch12-task1-s2-reopen-verify-20261122.md,
commit ed59f6a on main, 428 lines.

Council 2 method: re-read the same primary sources independently,
from branch todolist-push, read-only. No repo code was run. The
sources re-read in this session:
- improvements/s2-flip-reopen-runs/run-1..5.json, via git show
  from origin/todolist-push, parsed with python3 json.load only
  to print fields.
- improvements/worker-click5-s2-reopen-log.md (347 lines), via
  git show from origin/todolist-push.
- improvements/worker-click4-s2-flip-log.md, grep for PID 1003210
  only.
- Directory listing of improvements/s2-flip-reopen-runs on
  todolist-push, plus a tree-wide grep for p9-run paths.

Branch state at council time: todolist-push tip 4305dcb, same tip
the report cites. Worker log commit 1a3356d, follow-up 212e0ad,
harness commit d90d1b9, all confirmed in the log.

Verdict scale for this review: STANDS means the report's claim
and its reasoning both hold against the re-read evidence.
NEEDS CHANGE means a sentence or a verdict is wrong or
imprecise and should be fixed. Minor wording fixes do not change
any verdict.

## 1. Claim 1: 5/5 runs complete. STANDS.

Re-derived from the JSONs: run 1 wall 29020.4, run 2 wall
27799.1, run 3 wall 28112.6, run 4 wall 28898.1, run 5 wall
28560.9. All 5 have dry_run False, a wall, and both browser
records. The directory listing on todolist-push shows exactly
run-1.json through run-5.json, no aborted or partial file. The
report's statement is exact, and its reasoning (existence plus
matching run numbers plus matching walls in the worker log run
table) is sound.

## 2. Claim 2: 10/10 messages sent. STANDS.

Re-derived from the JSONs: all 10 browser records have outcome
sent. Messages are S2-REOPEN-R1..R5-BRAVE-IGNORE-TEST and
S2-REOPEN-R1..R5-CHROMIUM-IGNORE-TEST, matching the expected
pattern exactly. Program ok True in all 10, completed 3 on
Brave and 2 on Chromium in every run. Top-level
chromium_set_value True and program_variant
brave=fill,chromium=set_value in all 5 runs, with per-browser
program_variant fill on Brave and set_value on Chromium. The
report's corroboration is also confirmed: pre_count count 0 in
all 5 Chromium runs, delayed_count chromium count exactly 1 in
all 5 Chromium runs, V12 found True in all 10, CB-1 all True
in all 10. The note that Brave has no pre/delayed recount is
correct: the Brave record carries no pre_count field, and the
top-level delayed_count carries only a chromium key. The
no-double-send inference follows from pre 0 plus delayed
exactly 1.

## 3. Claim 3: median wall 28.6s. STANDS.

Walls re-derived: 29020.4, 27799.1, 28112.6, 28898.1, 28560.9.
Sorted: 27799.1, 28112.6, 28560.9, 28898.1, 29020.4. The
middle value of 5 is 28560.9 ms, which is 28.5609 s, rounding
to 28.6 s. The arithmetic is correct and the worker log states
the same sorted list and median.

## 4. Claim 4: V12 attempt 1 on all 10 messages. STANDS.

Re-derived from the JSONs: V12 found True, attempts 1, in all
10 browser records. Items: Brave 43, 45, 47, 49, 51; Chromium
54, 56, 58, 60, 62. The growth is exactly +2 per run on each
browser, as the report states. Role user and side user are
recorded in the V12 fields in all 10 sends (verified in the
JSON text). The verdict follows: found True at attempt 1 with
the correct role and side in every send.

Minor wording note, no verdict change: the report's gloss says
the +2 growth "matches one new user bubble per run per
thread". One new user bubble per run would explain +1, not
+2. The worker log's own explanation covers Brave (+1 test
bubble plus +1 clone1 reply per run), and the Chromium +2 is
not explained in the report. The regularity of the +2 growth
still supports consistency, and the verdict does not depend
on the gloss, but the sentence as written is arithmetically
loose. Suggested fix: say the items grow by exactly 2 per
run on each browser, matching one test bubble plus one reply
or banner item per run, and cite the log for the Brave half.
Recorded as minor correction M2 in section 10.

## 5. Claim 5: CB-1 all three parts on all 10. STANDS.

Re-derived from the JSONs: cb1 input_sent True,
target_received True, verified True in all 10 browser records.
Completed is 3 on Brave and 2 on Chromium in every run. The
per-send pass rate 10/10 and the per-run rate 5/5 (both sends
verified in each run) follow directly. No logic gap.

## 6. Claim 6: 0 model calls. STANDS.

Re-derived from the JSONs: model_calls 0 at run level in all
5 runs, 0 per browser in all 10 records, and phase_split_ms
model 0 in all 5 runs. Three independent fields agree, so the
verdict is over-determined, not merely asserted.

## 7. Claim 7: phase split, SSH 21.9s of 28.6s. STANDS.

Re-derived from the JSONs, all phase_split_ms values match the
report's printed values exactly. Medians recomputed from the
5 values: ssh 21942.2, broker 761.1, observe 2274.6, act
245.4, verify 375.9, setup 227.3, residual 2750.1. All match
the report and the worker log. SSH share: 21942.2 / 28560.9
= 0.7683, which is 76.8 percent, matching "about 77
percent". Internal consistency re-derived: phase sums vs
walls are run 1 29020.5 vs 29020.4 (off 0.1), run 2 27799.3
vs 27799.1 (off 0.2), run 3 exact, run 4 28897.9 vs 28898.1
(off 0.2), run 5 exact. Act bucket re-derived: run 1
140.516 + 113.005 = 253.521 vs act 253.5, run 2 137.493 +
106.613 = 244.106 vs 244.1, run 3 144.855 + 107.077 =
251.932 vs 251.9, run 4 140.832 + 99.412 = 240.244 vs
240.2, run 5 141.234 + 104.164 = 245.398 vs 245.4. Exact in
all 5 runs to the reported precision. The report's caveat is
correct and properly scoped: the broker, observe, verify,
setup, and residual buckets are verified for internal
consistency and medians, not re-derived from first
principles, while the act bucket is fully re-derived. The
verdict follows from the JSON fields directly.

## 8. Claim 8: Brave rollback real. STANDS on the record.

The worker log section 7 values quoted in the report were
re-read in full and match: SIGTERM 13:10:36 +07 to PID
1112207, graceful exit in 1s, [::1]:9223 closed; relaunch
13:10:52 +07, new main PID 1119832; verification 13:11:00
+07, Brave window back at address 0x55705383d420, ws1, PID
1119832; 13:11:18 +07 full cmdline check, 0 matches for
remote-debugging-port on PID 1119832.

Cross-check 1 re-derived: pre-state PID 1003210 with no
flag and window 0x55705383d420 (log section 1), debug PID
1112207 with the flag and the same window address (log
section 2), rollback PID 1119832 with no flag and the same
window address (log section 7). Three distinct PIDs in
order, one stable window address. The window-address
stability across three different process IDs is a genuine
cross-check, not a restatement of one log line: it is what
a session restore of the same window looks like, and it
would not hold if the rollback had produced a different
window.

Cross-check 2 re-derived: grep for 1003210 in the flip log
returns lines 163, 568, and 570, exactly as the report
states. The flip rollback ended on PID 1003210 and the
reopen pre-state starts from PID 1003210. Consistent.

Cross-check 3 re-derived: run-1.json Brave target_id
FED133417A338D5B1596D60490746672, tab title "Chat - clone1".
The reopen log section 2 records the same tab id as the one
served by [::1]:9223 after the debug relaunch, and discloses
that the id differs from the brief because tab ids are
per-session.

The report's limit is stated plainly and correctly: the
final cmdline check and the window-address check are
log-only, and this VM has no SSH path to the laptop, so the
live process state cannot be re-observed from here. The
verdict is scoped as "CONFIRMED on the record", not as a
live re-observation. That scoping is the honest one, and
the three cross-checks justify it. No over-claim.

## 9. Finding A: P9 screenshots missing. STANDS.

Re-derived: the directory listing of
improvements/s2-flip-reopen-runs on todolist-push at tip
4305dcb contains exactly run-1.json through run-5.json, no
PNG files. A tree-wide grep for p9-run returns 0 matches.
The run JSONs record p9 ok True for both browsers in all 5
runs, with png paths
improvements/s2-flip-reopen-runs/p9-runN-brave.png and
p9-runN-chromium.png. The worker log section 5 reviews all
10 shots and passes them, and section 8 says the PNGs were
"(to be committed with this log)". At tip 4305dcb, which is
after the log commits 1a3356d and 212e0ad, the PNGs are not
on the branch. The report's characterization is correct on
both halves: the P9 review is log-only and cannot be
independently re-checked from the branch, and that does NOT
refute the sends, because V12 (fresh DOM read finding the
exact message), CB-1 verified, pre-count 0, and delayed
count exactly 1 corroborate the sends from the JSONs. The
reasoning is sound: P9 is a render-side cross-check, and
losing it removes one check, not the DOM-side evidence.
The gap is material (the render claim is uncheckable until
the PNGs land) and the report says so. No over-claim in
either direction.

## 10. Findings B, C, D: minor open notes. STANDS.

B. V12 textLen +4. Re-derived: Brave message length 30,
textLen 34; Chromium message length 33, textLen 37; diff
exactly +4 in all 10 sends. The report is right that this
does not change the V12 verdict: found True with role user
and side user in all 10, and items grow regularly. The
systematic +4 in all 10 sends points at a definition
difference in the V12 script, not at a mismatch in any one
send. The report correctly notes the defining script lives
in /tmp on the laptop, not in the repo, so its definition
cannot be checked from the branch. Correctly judged as an
open note, not a refutation.

C. Chromium relaxed routing gate in all 5 runs. Re-derived:
Brave routing dom-chromium, fell_through empty, routing_relaxed
absent, observe 72, 73, 75, 77, 79 elements, not truncated,
composer present, in runs 1 to 5. Chromium routing
dom-chromium, fell_through "truncated inventory",
routing_relaxed True, observe 80 elements, truncated,
composer present, in runs 1 to 5. The worker log discloses
this plainly in section 6, caveat 1, and states the
relaxation touches only the routing gate, not the send path,
and that the send mechanism is identical to run 1 of the
(b1) measurement, which passed under the strict gate. The
report presents that as the log's stated position, not as
something it re-verified, which is the correct attribution.
The report is right to add that a reader should know the
Chromium sends were not strict-gate sends, and right that
this does not refute the sends: the gate governs which
observation the send is routed from, and the send itself
is verified by V12 and CB-1. Correctly judged.

D. Residual range wording. Re-derived from the JSONs: the
two count-check ssh_calls in run 1 are 1383.7 ms (pre) and
874.7 ms (delayed). Across runs the pre-check times are
1383.7, 1513.5, 1403.5, 1420.4, 1426.9 ms and the delayed
times are 874.7, 805.9, 812.0, 804.7, 849.2 ms. The log's
"874.7-1383.7ms" is exactly run 1's pair, presented without
saying it is run 1 only. The true cross-run range over all
10 count-check calls is 804.7 to 1513.5 ms, so the log
understates both ends. The report judges this "approximately
right and cites run 1 values" and "not a refutation". That
judgment is correct: the residual explanation does not
depend on the exact range, and the phase sums match the
walls to within 0.2 ms, so the residual is accounted for
regardless. A minor wording imprecision in the log, not a
verdict change. Correctly judged.

## 11. Findings E and F. STANDS.

E. Dry run 0 and wiring tests are log-only, noted, out of
scope. The log section 3 records dry run 0 (13:03:51 to
13:04:38 +07, wall 30123.9 ms, both browsers sent on scratch
tabs) and section 1 records wiring tests 12/12 pass. No dry
run JSON exists on the branch, which is consistent with its
workdir being /tmp/s2-reopen-dry on the laptop. The report
is right to note this and right not to claim it re-ran repo
tests. Correct scoping.

F. Worker log run table cross-check. All values match.
Re-derived from the JSONs: run 1 Brave dom_act 51 ms,
elapsed 140.516 ms, V12 items 43; Chromium dom_act 12 ms,
elapsed 113.005 ms, items 54. Run 2: 46 ms, 137.493 ms, 45;
9 ms, 106.613 ms, 56. Run 3: 46 ms, 144.855 ms, 47; 9 ms,
107.077 ms, 58. Run 4: 43 ms, 140.832 ms, 49; 8 ms, 99.412
ms, 60. Run 5: 43 ms, 141.234 ms, 51; 10 ms, 104.164 ms,
62. All match the log table to the reported precision.

## 12. Overall verdict and the EXPAND recommendation. STANDS.

The report's overall verdict follows from its sections: 5/5
runs complete, 10/10 sends verified, median wall 28.6 s,
V12 attempt 1 everywhere, CB-1 all True everywhere, 0
model calls, transport about 77 percent of the wall. The
report's reading of the gate is correct as stated in the
worker log section 6: median below 60 s AND the class
completes 5/5, where the original flip was 0/5 runs
complete. The original flip verdict's own point was that a
median below 60 s on runs that fail the class is not a
pass; the reopen fixes the completeness half, so the gate's
spirit is met as well as its letter. The report carries the
log's caveats with the verdict (relaxed Chromium routing
gate, unsolved mouse stall, transport-dominated wall,
durable landing still open) instead of dropping them. The
reasoning is sound end to end.

## 13. Minor corrections. NEEDS CHANGE (wording only, no verdict change).

M1. Section 10 lead sentence: "All 7 worker claims checked
from the raw JSONs are CONFIRMED", followed by a numbered
list of 8 items (1 to 7 from the JSONs, 8 the rollback).
A reader counts 8 items under a "7 claims" lead. The 7
refers to the JSON claims and item 8 is sourced
differently, but the sentence does not say that. Fix the
lead to name both groups, for example: "All 7 JSON claims
are CONFIRMED, and the rollback claim is CONFIRMED on the
record". No verdict change.

M2. Section 4 gloss on items growth (see section 4 above):
"+2 per run ... matches one new user bubble per run per
thread" is arithmetically loose; one bubble explains +1,
not +2. Fix to state the +2 growth and the log's
explanation for the Brave half (one test bubble plus one
clone1 reply per run). No verdict change.

M3. Section 11 is stale: it says the report "was NOT
committed or pushed" and that the commit step "needs the
user's confirmation". The report now stands committed on
main at ed59f6a, so that paragraph no longer describes the
file's state. Update it to record that the file was
committed at ed59f6a after user confirmation. No verdict
change.

## 14. Council 2 verdict

STANDS WITH MINOR CORRECTIONS. All 7 JSON claims and the
rollback claim are CONFIRMED on re-derived evidence. The
P9 gap is correctly characterized as material but not a
refutation. The minor open notes B, C, and D are correctly
judged as not changing any verdict. The overall verdict
and the EXPAND recommendation follow from the evidence with
the log's caveats carried. Three one-line wording fixes
(M1, M2, M3) are needed; none changes any verdict. No
refutation was found.
