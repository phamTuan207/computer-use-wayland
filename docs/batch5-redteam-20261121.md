# Batch 5 redteam report, 2026-11-21

Method: every number below was recomputed from disk by me (wc -l,
grep, python json checks, git show on the named commits). Shell
writes are EPERM-blocked at the time of writing, so two live
re-runs I attempted could not complete; those are listed as
unverified rather than as failures. No number in this report is
taken on trust from an agent report.

Scope: all batch 5 deliverables (tasks 1 to 6), the t05 fix at
08f36d2, the Y10 reconcile at ed78e83, the Y10 followup and retry,
and coord/clone1.md batch 5 sections. Local HEAD f006137; the
coord blocks after f006137 (watchdog 19:27 onward, Y10 followup,
Y10 retry) are uncommitted working-tree additions at review time.

## 1. Wrong facts

1. Line counts in coord/clone1.md are all off by +1, the same
   systematic error batch 4 found (counting newline + 1 on files
   that end in a newline). Recomputed with wc -l:
   tests/run_atspi_session.sh claimed 251, actual 250;
   docs/research/2026-11-21-atspi-session-probe.md claimed 175,
   actual 174; docs/clone1-todolist-push-evidence-20261121.md
   claimed 508, actual 507; docs/clone1-a1-pilot-review-20261121.md
   claimed 616, actual 615.
2. A1 review doc lines 21 and 52, and the coord task 3 section,
   say FREEZE.md at f31abcf contains 10 sha256 hashes. It contains
   12 (grep -oE "[0-9a-f]{64}" on
   git show f31abcf:tests/realistic/a1-pilot/FREEZE.md returns 12).
   The evidence doc's "12/12 match" is the correct number; the A1
   review and coord are wrong.
3. Evidence doc, 695efea section, and its "New findings" item 2:
   "Four have NO `return` at all". False. I recomputed twice from
   improvements/worker-x-e1-plan-test-05.md at 695efea (19 raw
   "cmd":"eval" occurrences): 19 evals, 10 start with `return`, 9
   contain `return` later, 0 have no `return` at all. The two
   select-set evals the doc names as no-return (steps 16 and 42)
   both end with `return e.value`; the search-input dispatch eval
   also ends with a return. The true split is 10 + 9 + 0, not
   10 + 5 + 4. The 19 and 10 numbers are right. Consequence: the
   "plan file is NOT affected" conclusion is actually stronger
   than the audit states, but the audit's flagship correction
   contains a false sub-claim.
4. Y10 repeat-run count: commit ed78e83 and coord say "10/10 x7
   runs", but improvements/worker-y10-batch3-fix-log.md lists 8
   runs: first merged 27283 ms, sequential x3 (24408, 25168,
   24704 ms), load x3 concurrent (74500, 74396, 73534 ms), final
   25024 ms. 1 + 3 + 3 + 1 = 8, not 7.
5. A1 review B3b: "JSONDecodeError dong 125". The open() is line
   125 but json.loads(first) is line 128 in a1_unblind.py at
   f31abcf (verified with grep -n). B3c FileNotFoundError at line
   125 is correct, B2 line 80 (the len(manifest) != 12 check) is
   correct, B3a line 226 is correct.

## 2. Unverified claims stated as done

6. AT-SPI session probe numbers have no log artifact on disk.
   Runs 3 to 6 (19212, 13272, 12686, 13306 ms; find_app 52.1 ms;
   click 3.1 ms) and the coordinator's own re-run (verdict ok,
   23620 ms) appear only in the doc and coord; no log file exists
   (~/workspace/atspi-session-run*.log does not exist). I tried to
   re-run the wrapper myself with --mode dump: it failed at
   start_xvfb, "X socket never appeared" after 10.2 s, and a
   direct Xvfb :97 start also created no socket. The success is
   currently unreproducible in this environment, so the numbers
   rest on the agent report alone.
7. Firefox task 5 standalone confirmations "t10 3/3 pass, t05 1/1
   pass" have no JSON artifact in ~/workspace/b5t5-results/
   (only the 7 run files). The BiDi smoke numbers (connect 314,
   goto 219, click 149, type 95 ms) and the Playwright Juggler
   claim (stock 160.0.1 "exits silently with code 0 on
   -juggler-pipe", "tried by hand") likewise have no log.
8. Y10 9/9 mutation probes and 7 of the 8 repeat runs: the probe
   script, diffs and run JSONs lived in /tmp/y10m2* and
   /tmp/y10-probe2.py, which no longer exist (VM restart wiped
   /tmp). Only the final run's results.json (25024 ms) is
   committed. The table in
   improvements/worker-y10-batch3-fix-log.md is the only surviving
   evidence for the 9/9 and the other runs.
9. 08f36d2 t05 standalone times (5091, 5289, 5790 ms) and the
   second full run (59449 ms) have no surviving artifact;
   results.json at 08f36d2 holds only the 83294 ms run. The
   negative-proof mutation (comment out item.name = next, check
   FAILs) has no log. I tried to re-run it myself, but shell
   writes are EPERM-blocked right now, so the copy to /tmp came
   out as 0-byte files and the check could not run.
10. agy-y2 first live-run crash (test 02, geckodriver connection
    refused, load 8.23) and the separate 02-10 runs have no log
    artifact in /tmp/agy-y2-verify (grep for "refused" returns 0
    hits in live_steps.jsonl). The final live_results.json is
    solid; the crash story is single-source.
11. Retry-log free-memory range "121M to 242M" (coord 21:08) is
    not traceable in ~/workspace/b5t5-results-y10/ff-retry-log.txt,
    which lists free memory only for attempt 0 (132M). The
    available-memory range 179M to 688M is traceable (samples
    13:45 179M, 12:59 688M).
12. test_code_exec "53 tests OK (11.894 s)": the count 53 is
    confirmed, but my re-run on this machine gives 13 errors, all
    environmental (tempfile "No usable temporary directory" and
    EPERM), not assertion failures, because the write window is
    closed now. The claim is plausibly true when the window was
    open, but I could not re-verify it live.

## 3. Real bugs

13. tests/run_atspi_session.sh, dismiss poll conflates "no dialog"
    with "dismiss failed". Probe --mode dismiss returns 2 both
    when no dialog button is found and when the click fails, so
    the wrapper's 15-iteration poll retries futilely when the
    dialog is already gone instead of breaking through to the dump
    poll. In practice the fresh profile always shows the
    spotlight, so this wastes time rather than producing a wrong
    verdict, but the poll cannot distinguish the two states.
14. tests/run_atspi_session.sh, wait_document failure does not
    gate. If DOC_OK is false the script logs the stage as failed
    and then runs the probe stages anyway instead of exiting 2.
    The final verdict is still false (exit 2), so the outcome is
    the same, but it spends probe time on a dead session.
15. tests/run_atspi_session.sh, prereq does not check /tmp
    writability or free space, although the doc documents a
    /tmp-full failure mode (Xvfb socket never appeared at 100%
    /tmp). I reproduced exactly that failure live: start_xvfb
    false after 10.2 s with /tmp at 77% used and Xvfb creating no
    socket. The failure surfaces as a generic "X socket never
    appeared" after 10 s instead of a clear prereq error.
16. Batch-4 t05 check at 08f36d2 had 2 real holes that Y10 later
    closed. Verified by reading the 08f36d2 check: (a) it fills
    'meeting-notes.txt' (line 77), exactly the old hardcoded
    value, so a handler that ignored the input and hardcoded the
    old mapping would still pass; (b) the cancel test (lines
    66-69) types no name before Cancel, so a cancel that applied
    the prefill (equal to the current name) would still pass.
    Consequence: the coord 19:09 section's "batch 3 gio la 10/10
    that" was premature; only the Y10 version is mutation-proven.
    The Y10 section discloses the 2 holes honestly, but the 19:09
    section itself was never amended in the file.
17. The Firefox BiDi shim's page-registry fix (browser.pages() is
    async in Puppeteer, sync in Playwright) is unproven on a live
    popup flow. The Y10 README discloses this honestly: t05 never
    uses context.pages(), and the t09 connect failures came after
    the fix, so it must be re-tested when Firefox runs again. It
    is not a bug in the current tree (shim deleted, both
    lib/browser.mjs byte-identical to HEAD, verified by diff
    against git show HEAD), but it is a live claim that depends
    on the blocked t09/t10 rerun.

## 4. Minor

18. agy-y2 live: sum of per-test elapsed is 124.904 s against
    total_elapsed_s 140.821 s. The 15.9 s gap (per-test Firefox
    launch and profile setup, presumably counted in the total but
    not in per-test elapsed) is not explained in the report.
19. docs/clone1-batch5-firefox-20261121.md states "No newer fix
    for t09 or t10 batch3 has landed on main or todolist-push
    after b629e11". True when written (before 19:19), but now
    stale as a standalone document after ed78e83 landed; only
    coord carries the correction.
20. Batch2 Firefox run2 wall 65122 ms vs timestamp span 65120 ms
    (2 ms), batch3 run4 wall 56623 ms vs span 56622 ms (1 ms).
    Trivial runner overhead, not an error.
21. run_atspi_session.sh header comment ("full mode exits 2 even
    when the session is fine") contradicts the doc and the code:
    the probe's full mode exits 2, but the wrapper exits 0 when
    the session works. Misleading wording; the behaviour itself
    is correct per the doc.

## 5. Blocked items verdict

The Y10 t09/t10 Firefox BLOCKED verdict is honest. Evidence on
disk: 3 t09 standalone JSONs, all FAIL with "could not connect to
Firefox BiDi" after a 30 s timeout (30340, 30284, 30285 ms, ports
19586, 19520, 19338); no t10 or full-run JSON exists; the retry
log lists 10 attempts 12:37 to 14:07 UTC, all segfault exit 11,
each with a minidump id; t05 3/3 PASS (6145, 5925, 5058 ms)
immediately before the crash onset at about 12:29. The memory
explanation is the likely cause but not proven: available memory
bounced 179M to 688M with no recovery trend, and Firefox segfaults
even at 688M available, so low memory is a hypothesis, not a
demonstrated root cause. Nothing claimed as done depends on the
blocked rerun except the shim page-registry fix (finding 17) and
the Y10 t09/t10 Firefox comparison itself; coord correctly lists
task 5 as partial, not done.

## 6. Verified correct (spot check summary)

- Firefox doc: all 7 results.json files in ~/workspace/b5t5-results/
  match the doc exactly (pass/fail counts, wall clocks, per-test
  ms for batch2 runs 2-3 and batch3 run 4; run3 t05 failures are
  crumbs/empty-state, consistent with navigation never happening
  under the missing dblclick; run3 t10 failure is the Night Drive
  read "Morning Light", as stated; positionMinAfterNext 0 in runs
  2 and 3; batch2 t10 csvLines 9 in both 10/10 runs).
- Y10 followup: t05 3/3 JSONs match (6145, 5925, 5058 ms,
  finalHome with the novel names); t09 3x FAIL match.
- Shayxo: re-ran by me, 17 tests OK in 0.032 s; lua line 14
  blur_strength = 0.15 confirmed; pad 12.75 test present.
- agy-y2: live per-test seconds (20.094, 9.57, 10.376, 15.787,
  13.514, 17.503, 17.196, 6.903, 9.071, 4.89) and simulate ms
  (630, 506, 477, 626, 587, 561, 990, 490, 661, 724) match the
  JSONs exactly; 179 actions, 88/88 checks sum correctly;
  30a72e5 code verified as the run target by the agent's
  git-archive method (no hash file on disk, so this part is
  agent-reported); Y7 commits 9a74a70 and a07fd27 are ancestors
  of beebe50 (verified); clone2's 68.838 s is cited in
  coord/clone2.md line 136 with identical 179/88 counts.
- Evidence doc: 13 COMPLIANT / 6 PARTIAL / 1 MISSING recounts
  exactly from the table; a82bb41 verified exactly (runner 2517
  lines, 88 check() call lines excluding the definition, 79
  unique #id selectors, commit message says 87/80); 6f20fb5
  MISSING verdict stands (no runner file at that commit).
- A1 review: 28 holes recount exactly (3 blocker + 13 major +
  12 minor headings); B3a crash site exact (line 226 median
  unguarded while lines 182, 195, 234 guard with isinstance);
  Worker U exact (71 f01 rows, elapsed sum 2960.7 ms, RESULT
  line 3604 ms); f01 spec 26 steps confirmed in the frozen plan.
- Y10 diffs match their descriptions: t05 fixture diff vs
  08f36d2 is 0 lines; t09 removes the verify callback and adds a
  500 ms dwell; t10 adds sleep 350 ms and the advancing >= 2
  check; ed78e83 results.json is 10/10, 25024 ms with per-test
  t05 2983, t09 3216, t10 4990.
- T05 Y10 check, read in full: novel names, cancel with a typed
  name, empty-name rejection, trim test, dialog open/hidden and
  prefill assertions; fixture handler uses the trimmed input
  value (line 176) with no hardcoded mapping left.
