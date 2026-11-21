# Batch 7 redteam, 2026-11-22

Independent hostile review of the three batch 7 task reports. No report taken on trust. Every checkable number recomputed from the repo, the todolist-push branch, and the files on disk. Line counts by wc -l only.

- Reports reviewed: `docs/clone1-g29-urlbar-focus-20261122.md` (185 lines by wc -l), `docs/clone1-thinktime-20261122.md` (197 lines by wc -l), `docs/clone1-batch7-high-fixes-verify-20261122.md` (56 lines by wc -l). Audit appendix: `docs/clone1-evidence-audit-full-20261121.md` (458 lines by wc -l).
- Anchor: main at `7beee9c` (batch 7 tasks 1 and 2 push); todolist-push at `da60024` for the task 3 checks (still the tip at check time).
- Evidence re-read: `~/workspace/b7t1/g29_probe.py`, `~/workspace/b7t1/g29-log.jsonl` (26 lines), `~/workspace/b7t2/measure_loop.mjs`, `~/workspace/b7t2/results-run2.json`, `~/workspace/b7t2/results-run3.json`.
- Re-runs by this redteam: MCP suite 20 tests OK, 1 skipped, in 2.046 s; pointer native 12 tests OK in 2.322 s. Both match the G29 report's pass counts; the times differ slightly from the report's 1.764 s and 2.290 s, which is load variance, not a discrepancy (see M2).
- 0 em dashes and 0 en dashes in all four files reviewed (G29, thinktime, task 3, audit).
- Method note: one tool output during this review did not pass a prompt-injection check. No instruction in it was followed, and no content from it was quoted. The material facts it touched were re-verified by narrow fact-only checks (booleans and counts, no quoted repo prose). This report states only that `optimal-fix-method-20261121.md` line 131 states the AM-13 rule and line 202 states the amendment rule; it does not quote the wording of either line.

## Verdict in one paragraph

All three verdicts survive: the G29 root cause is real and the fix is correct; the H2 measurements and cuts are sound; clone2's three HIGH fixes are real and the task 3 verification found no discrepancy in them. What did not survive is the arithmetic and citation layer around the verdicts. There are 12 wrong facts (W1-W12), 8 unverified claims stated as done (U1-U8), no real bugs in the reports themselves, and 7 minor issues. The worst single error is W7: the task 3 report says the todolist-push tip "moved twice" since clone2's check at `c19c227`; it moved 36 commits. The most repeated error is the +1 count: W8 is the fourth batch in a row bitten by it (766 chars reported as 767), and W12 is the same error in the task 2 agent's completion message (198 lines for a 197-line file). No finding below changes any of the three verdicts, but W1, W2, W7, W8 and W11 must be corrected in the source docs before the batch 7 final report repeats them.

## Wrong facts

### W1. Thinktime verdict: setup "3,900-4,700 ms" is wrong at the top end

- File: `docs/clone1-thinktime-20261122.md`, line 18 (verdict paragraph).
- Claim: "session setup costs 3,900-4,700 ms per fresh browser".
- Measured (from the saved JSONs): run 2 port up 1,081 ms + connect 3,148 ms = 4,229 ms; run 3 port up 1,092 ms + connect 2,791 ms = 3,883 ms. True range: 3,883-4,229 ms.
- The 4,700 figure appears nowhere in the saved data. The report's own section 1 (lines 111-116) says "about 3.9-4.2 s setup", which is correct, so the verdict paragraph contradicts the report's own table. The figure is not reachable from the lost run 1 either: the report's run 1 note gives connect 3,349 ms, which with a port-up of about 1,100 ms gives about 4,450 ms, still not 4,700.
- Correct value: setup costs 3,883-4,229 ms (3.9-4.2 s) per fresh browser.

### W2. Thinktime verdict: screenshot "24-29 ms" matches no saved statistic

- File: `docs/clone1-thinktime-20261122.md`, line 23 (verdict paragraph).
- Claim: a screenshot costs "24-29 ms" per shot.
- Saved medians: run 2 25.9 ms, run 3 24.2 ms. Saved means: 28 ms and 26 ms. Saved maxes: 40.8 ms and 35.1 ms. No saved statistic is 29 ms. The report's own section 1 says "At 24.2-25.9 ms", which is correct.
- The 29 ms figure may come from the lost run 1 (its file was overwritten), but that is unverifiable, and the verdict range as written contradicts the report's own section 1.
- Correct value: screenshot medians 24.2-25.9 ms.

### W3. Thinktime: "about 3.6-3.9 ms per call" for per-element rects

- File: `docs/clone1-thinktime-20261122.md`, line 67.
- Claim: the 38-50x gap is "about 3.6-3.9 ms per call".
- Computed from the saved medians: 219.8 / 60 = 3.66 ms per call; 239.5 / 60 = 3.99 ms per call.
- Correct value: 3.7-4.0 ms per call. Both ends of the stated range are 0.1 ms low. Minor.

### W4. Thinktime: local think "max 0.157 ms" matches no saved run

- File: `docs/clone1-thinktime-20261122.md`, line 79.
- Claim: the local policy "measures 0.0 ms median over 100 runs, max 0.157 ms".
- Saved maxes: run 2 `think_local_policy_100x.max_ms` = 0.133 ms; run 3 = 0.174 ms. The figure 0.157 matches neither saved run. The true max across the saved runs is 0.174 ms.
- The 0.157 figure may come from the lost run 1, but that is unverifiable.
- Correct value: max 0.174 ms across the saved runs (medians 0.0 ms and 0.001 ms).

### W5. Thinktime: naive 10-step total "about 6.4-7.0 s" mixes two bases

- File: `docs/clone1-thinktime-20261122.md`, lines 111-116 and line 27 (verdict).
- The report's own derivation: naive shape = setup 3.9-4.2 s + 10 x 35-41 ms loop = 4.3-4.6 s; "add about 2.1-2.3 s more" for per-element rects; total "about 6.4-7.0 s".
- Two problems. First, the report's own components sum to 6.4-6.9 s (4.3 + 2.1 = 6.4; 4.6 + 2.3 = 6.9), not 6.4-7.0 s. The 7.0 upper bound needs the full per-element rects range, 2.2-2.4 s. Second, the "2.1-2.3 s" figure is the delta of per-element rects over one-shot rects ((219.8 - 5.8) x 10 = 2,140 ms; (239.5 - 4.8) x 10 = 2,347 ms), which is the right increment only if the baseline loop already contains a one-shot rects call. The naive loop does not: `~/workspace/b7t2/measure_loop.mjs` lines 215-226 show the naive shape is full DOM observe + screenshot, click, full DOM observe verify, with no rects call at all. Adding per-element rects to that loop adds the full 2.2-2.4 s, giving a consistent total of 6.5-7.0 s.
- Correct statement: on the delta basis the total is 6.4-6.9 s; on the full-addition basis (which matches the naive loop as actually measured) it is 6.5-7.0 s. The stated "6.4-7.0 s" takes the lower bound from one basis and the upper bound from the other. Minor, 0.1 s.

### W6. G29: run 2 wall time is 7,516.5 ms, not 7,646 ms

- File: `docs/clone1-g29-urlbar-focus-20261122.md`, run 2 header.
- Claim: run 2 wall 7,646 ms.
- `~/workspace/b7t1/g29-log.jsonl` records run 2 total as 7,516.5 ms. The report's figure is 129.5 ms too high.
- Run 1 matches exactly (7,476.5 ms in both the report and the log), so this is a transcription slip in run 2 only, not a measurement error.
- Correct value: run 2 wall 7,516.5 ms.

### W7. Task 3: the todolist-push tip moved 36 commits since c19c227, not twice

- File: `docs/clone1-batch7-high-fixes-verify-20261122.md`, anchor line.
- Claim: "clone2 checked at c19c227; the tip moved twice since".
- `git rev-list --count c19c227..da60024` returns 36. `c19c227` is an ancestor of `da60024` (verified), and the 36 commits include the four fix commits (748cc35, 219720c, 05ee34d, 16c4196) plus 32 other commits (clone2 batch 8 work, coord2 messages, CLICK-AMEND, CLICK-BASELINE, and others).
- Correct value: the tip moved 36 commits between c19c227 and da60024.

### W8. Task 3: the :148 line is 766 chars, not 767

- File: `docs/clone1-batch7-high-fixes-verify-20261122.md`, V1 precision notes.
- Claim: the citation line `improvements/opt-crawl-src-20261121.md:148` is "767 chars".
- True length excluding the newline is 766 chars. 767 is the byte count including the newline (`wc -c` = 767). This is the +1 error (counting the newline as a character) for the fourth batch in a row.
- The parent's coord note for batch 7 task 3 repeats the 767 figure; both need correcting.
- Correct value: 766 chars (767 bytes including the newline).

### W9. Thinktime research: agentpatterns was updated 19 days before 2026-11-22, not 18

- File: `docs/clone1-thinktime-20261122.md`, research section (agentpatterns.ai entry).
- Claim: "updated 18 days before 2026-11-22".
- The page (fetched 2026-11-21 21:15 UTC) shows Published 2026-07-27, Updated 2026-11-03. 2026-11-22 minus 2026-11-03 is 19 days.
- Correct value: 19 days. The page content the report cites checks out (20,000-80,000 tokens per step; 200-400 tokens per snapshot vs 3,000-5,000 for a screenshot; re-read only on signal).

### W10. Thinktime research: frowse was updated 3 days before 2026-11-22, not 2

- File: `docs/clone1-thinktime-20261122.md`, research section (frowse entry).
- Claim: "updated 2 days before 2026-11-22".
- The PyPI page (fetched 2026-11-21 21:15 UTC) shows the latest release 0.1.2 uploaded Nov 19, 2026. 2026-11-22 minus 2026-11-19 is 3 days.
- Correct value: 3 days. The page content the report cites checks out (compact summary about 100-300 tokens; Folate grounding 10-25 ms, under 250 MB RAM, $0 API cost; up to 90%+ token saving claimed; vendor claim, not independently verified here).

### W11. Task 3: clone2's fix doc is on main, not on todolist-push

- File: `docs/clone1-batch7-high-fixes-verify-20261122.md`, "What clone2 did" section.
- The report groups `docs/clone2-batch7-high-fixes-20261122.md` with the four fix commits (748cc35, 219720c, 05ee34d, 16c4196) "on todolist-push", which reads as the doc being part of the todolist-push materials.
- The four fix commits are on todolist-push (all ancestors of da60024, verified). The doc is not: `git cat-file -e da60024:docs/clone2-batch7-high-fixes-20261122.md` fails, and `git log --all -- docs/clone2-batch7-high-fixes-20261122.md` shows a single commit, 5777535, present on main only.
- The parent's coord note repeats the same grouping, so the coord carries the same imprecision.
- Correct statement: the four fix commits are on todolist-push; clone2's fix report doc lives on main (commit 5777535).

### W12. Task 2 agent's completion message claimed 198 lines; the file is 197

- The task 2 agent's completion message said the thinktime report is 198 lines. `wc -l docs/clone1-thinktime-20261122.md` returns 197.
- The report itself states no line count, and the parent's coord note correctly says 197. This is the same +1 error as W8, in the agent's message rather than the report. Recorded because the brief asks for every line count quoted anywhere.

## Unverified claims stated as done

### U1. G29: the dismiss is "(AT-SPI dismiss, 'Continue', 0.2 ms)" with no log artifact

- File: `docs/clone1-g29-urlbar-focus-20261122.md`, experiment E2.
- The claim that the context menu was dismissed with an AT-SPI dismiss on a button named "Continue" in 0.2 ms has no artifact: `~/workspace/b7t1/g29-log.jsonl` has no dismiss entry at all, and the only "0.2" in the probe code is `time.sleep(0.2)`, which is 0.2 seconds, not 0.2 ms.
- The dismiss happening is corroborated indirectly (the address bar node appears in the tree afterwards, and E3/E4 then pass), but the 0.2 ms figure, the "Continue" button name, and the claim "before that the bar is not in the tree at all" (no failed-find record exists) are all unverified.
- The report should state the dismiss as observed-but-untimed, or drop the 0.2 ms figure.

### U2. Thinktime run 1 preliminary numbers have no saved file

- File: `docs/clone1-thinktime-20261122.md`, run 1 note.
- The run 1 numbers (connect 3,349 ms, rects 60x 283.5 ms, loop one-vision 26.0 ms, loop naive 41.2 ms) rest on the report's word only: the file was overwritten when run 2 wrote results.json. The report discloses this honestly ("its file was overwritten by run 2 writing results.json, so the table below uses runs 2 and 3 only"), and no conclusion in the report depends on run 1 alone.
- Unverifiable, honestly disclosed. Do not cite run 1 numbers in the batch 7 final report.

### U3. Thinktime: "No Firefox process was left running after any of the three runs (checked)"

- File: `docs/clone1-thinktime-20261122.md`.
- No artifact records this check, and run 1's evidence is gone (see U2). The claim is unverifiable as stated for run 1. For runs 2 and 3 the JSONs exist but contain no process-list evidence either.

### U4. Thinktime research: guibai "updated 7 days before 2026-11-22" is not verifiable from the page

- File: `docs/clone1-thinktime-20261122.md`, research section (guibai.dev entry).
- The fetched page (2026-11-21 21:15 UTC) shows no visible publication or update date. The text gives the incident date (November 10) and describes a two-week run, which is consistent with a mid-November article, but the exact "7 days" figure cannot be confirmed from the page.
- The page content the report cites checks out (screenshot route has a low ceiling; coordinates unstable across viewport widths; one image is thousands to tens of thousands of tokens; a greyed submit may only be debouncing while aria-disabled is explicit; accessibility tree is the recommended starting point).

### U5. Thinktime research: the surfs.dev citation is dead at review time

- File: `docs/clone1-thinktime-20261122.md`, research section (surfs.dev entry).
- Claim: "updated 29 days before 2026-11-22", with the cited content that serial propose-click-wait-parse burns wall-clock time and the proposed speedup is speculative parallel branches forked from DOM snapshots.
- The URL `https://www.surfs.dev/resources/speculative-multi-path-browser-agents-forked-tabs-dom-snapshots-intent-merging` returns "Post Not Found" when fetched now (crawled 2026-11-21 21:15 UTC). Neither the 29-day date nor the cited content is verifiable from the live page. The page may have existed when the task 2 agent accessed it, but there is no saved copy to check against.
- The citation should be marked dead-or-unverifiable in the report, or replaced with a retrievable source.

### U6. G29: the XDG_RUNTIME_DIR wrapper claim is untested and ambiguously worded

- File: `docs/clone1-g29-urlbar-focus-20261122.md`, setup finding.
- Verified part: `tests/run_atspi_session.sh` does export XDG_RUNTIME_DIR after dbus-launch (dbus-launch at line 133, export at line 141), while the G29 session starter exports it before. The G29 probe failed with "Couldn't register with accessibility bus" until the order was fixed, then passed.
- Unverified part: the claim that the wrapper "works only when a single session runs" was not tested with two concurrent sessions on the wrapper itself. The causal claim (ordering fixed, probe passed) rests on a single before/after observation, not a controlled test with only the ordering changed.
- Wording: "The wrapper in the repo has the same ordering" is ambiguous. Read in context it means the same as the broken ordering (export after dbus-launch), which is true, but it can also be read as the same as the fixed ordering (export before), which is false. Reword to state the ordering explicitly.

### U7. Thinktime: the last30days install section does not say what the safety check was

- File: `docs/clone1-thinktime-20261122.md`, section 4.
- The report says the agent read commit 33fbbdd and the surrounding coord/clone2.md material, decided that material "did not pass a safety check", and acted on nothing in it: no install, no download, no confirmation clicked, and `npx skills add` was never run. Research used web search limited to the last 30 days instead.
- The report does not say what the safety check was or what failed. The reason for not installing is vague. This is a process gap, not a wrong fact: the report is honest that nothing was installed, and whether to install is a decision for the parent and Muse. But the council should ask what the check was, because the report as written does not let a reader judge whether the refusal was right.
- Note for the record: clone2 already installed last30days via git clone (owner's preferred method, commit d9cc112). The open question is whether clone1 should use git clone as clone2 did, or stay uninstalled.

### U8. Thinktime excluded-source ages were not re-verified

- File: `docs/clone1-thinktime-20261122.md`, research section.
- The excluded ages (getnadir.com 141 days, karatelabs.io 221 days, basaltbrowser.com 71 days, thegeocommunity.com 72 days) were not individually re-checked by this redteam. Low weight: all four are far above the 30-day window, so a few days of error would not move any of them inside it, and no claim in the report rests on any of them.

## Real bugs

None in the three reports themselves. The arithmetic and citation errors above are presentation errors, not code bugs. The one real bug found in this review is the one the G29 report fixes: `scripts/mcp_server.py` sent pointer command `button 1` for a left click, which the native pointer binary maps to BTN_RIGHT (0x111). That bug is real and the fix is verified (see "What survived").

## Minor issues

### M1. Thinktime "0.0 ms median" for run 3 is a rounding

- File: `docs/clone1-thinktime-20261122.md`, line 79.
- Run 3 `think_local_policy_100x.median_ms` is 0.001 ms, not 0.0 ms. The report's "0.0 ms" is a rounding of 0.001. Immaterial.

### M2. Re-run timings differ slightly from the report's timings

- G29 report says the pointer native suite ran "12 tests OK, 2.290 s" and the MCP suite "20 tests OK in 1.764 s". This redteam's re-runs gave 2.322 s and 2.046 s with the same pass counts. Timing varies with load; not a discrepancy.

### M3. The pointer-native "272/273/274" claim rests on a computed loop

- File: `docs/clone1-g29-urlbar-focus-20261122.md`.
- The claim that the mock records evdev codes 272/273/274 is supported by the release assertion loop over 0x110-0x112 in `tests/test_pointer_native.py` (the hold helper sends button 0/1/2, and the release assertion checks the 0x110-0x112 release lines). There is no literal "273" or "274" text in the test file; the codes are computed. The claim is correct.

### M4. Task 3: the :862 citation is imprecise

- File: `docs/clone1-batch7-high-fixes-verify-20261122.md`, V1 sites.
- The H3 acceptance text spans lines 862-863 of `improvements/worker-f1-guardian-fix-log.md`; the word "proposal" is on line 863, not line 862. Line 862 alone does not contain it. The citation should be 862-863. The correction entry in the log itself cites line 862 the same way, so the imprecision is inherited, not invented.

### M5. The day-count errors share a likely cause

- W9 and W10 are both off by exactly one day in the same direction, and both fit a Nov 21 reference date (Nov 21 minus Nov 3 = 18; Nov 21 minus Nov 19 = 2) rather than the stated access date Nov 22. The agent likely counted days against the UTC calendar date (Nov 21) while stating the access date in +07 (Nov 22). Hypothesis only, offered so the fix agent can check it; the correct values for the stated access date are 19 and 3 days.

### M6. Task 3 "0 discrepancies found" refers to clone2's fixes, not to the report's own numbers

- File: `docs/clone1-batch7-high-fixes-verify-20261122.md`.
- The "0 discrepancies" verdict is correct for clone2's fixes (all four fix commits verified: pure insertions, 0 deletions, 0 dashes in added lines; all cited lines, hashes, and session IDs check out). But the report's own claims contain W7, W8 and W11. The batch 7 final report must not quote "0 discrepancies" without that scope.

### M7. G29 run 1 shared one marker for all four experiments

- File: `docs/clone1-g29-urlbar-focus-20261122.md`.
- Run 1 used the shared marker "g29t" for E1-E4 because of a probe bug; run 2 used unique markers g29a-g29d. The report discloses this. It does not affect the verdicts, because run 2 (unique markers) reproduces run 1 exactly, and the typed-marker read-back is the decisive check in both runs.

## What survived the hunt

- **G29 root cause and fix.** The evdev mapping is proven three ways: kernel header BTN_LEFT 0x110, BTN_RIGHT 0x111, BTN_MIDDLE 0x112; `native/pointer.c` sends 0x110 + button; `cu.py` maps left to 0 (lines 1621, 1649). The fix at `scripts/mcp_server.py` lines 308-309 (`button 0 1` / `button 0 0` with the mapping comment) is correct. The new `RealClickButtonTest` fails on the old code and passes after the fix (negative control verified by this redteam in a scratch worktree at `ad7da5b~1`). Repo-wide grep finds no other production sender of literal `button 1`: only `tests/pointer_benchmark.py:53`, which is an intentional benchmark against the mock server and is disclosed as such. `98edc39` contains the old `button 1 1` / `button 1 0` at lines 248-249, confirming the bug is present since the file was created.
- **G29 live experiment record.** `g29-log.jsonl` (26 lines) confirms E1 left click PASS, E2 right click FAIL reproducing G29 exactly (context menu role "menu", extents [621, 66, 81, 204], typed marker read back as ""), E3 AT-SPI doAction click PASS (0.3 ms), E4 Ctrl+L PASS (29.3 ms), mouse at (619, 64), and the nuance that a right-click DOES set AT-SPI STATE_FOCUSED on the bar node while the keyboard goes to the context menu. The type test is the decisive check, and it is recorded.
- **H2 measurement table.** Every median in the thinktime report re-checks exactly against `results-run2.json` and `results-run3.json`: port up 1,081/1,092 ms, connect 3,148/2,791 ms, setup totals 4,229/3,883 ms, goto 306/383 ms, full DOM 3.7/3.45 ms, compact snapshot 6.85/7.8 ms, rects one-shot 5.8/4.8 ms, rects per element 219.8/239.5 ms, screenshot 25.9/24.2 ms with 41,625 bytes, cheap verify 2.9/4.2 ms, click+verify 34.4/26.6 ms, type 18.9/12.1 ms, loop one-vision 27.9/29.6 ms, loop naive 39.1/34.7 ms, final counter 18 in both files. Cross-run ranges also check out. The proposed cuts are each tied to a measured number, and the biggest saving (one-shot rect sweep, 214-235 ms per round) is the right one to lead with.
- **Task 3 verification of clone2's HIGH fixes.** At tip `da60024`: all four fix commits exist and are ancestors of the tip; diffstats 5/5/4/78 insertions, 0 deletions; 0 em/en dashes in the added lines of all four; `git log --all -- MEMORY.md` returns nothing; `5a2b69d` and `c16dd4e` exist with the stated messages; V1 citation sites :90, :107 and :198 contain "MEMORY.md 22:57" and :862 does not (the H3 text spans 862-863); method file lines 131 and 202 state the AM-13 rule and the amendment rule (verified by boolean checks only, wording not quoted here); V2 all 14 logs absent via git cat-file, `f3-evidence/` holds exactly the 14 listed files, all cited lines match, and the four arm session IDs have 0 hits in full.log and result_full.json; V3 verdict at line 991 with the exact text, all 7 evidence filenames have 0 hits branch-wide, the only judge filenames on the branch are the two unrelated worker-y8b files, and SHA 8da1f562 is corroborated (tc02-v1.json:9 full hash; trial lines 836/938/941/2091). The corrections doc is 78 lines; "BATCH 7 CORRECTION" counts are 1/1/1 in the three logs. The V2 true count is 14, not 9 as the batch 6 audit said (the 5 extra logs are arm_d_run.log, probe_d.log, probe_f.log, probe_r3.log, relaunch-f3b.log); the audit appendix records this correction.
- **Audit appendix.** `docs/clone1-evidence-audit-full-20261121.md` is 458 lines by wc -l, and the batch 7 appendix added at the end correctly records all three HIGHs as PARTIALLY FIXED, the V2 count correction to 14, and that nothing further is fixable from this machine.
- **Line counts.** G29 185, thinktime 197, task 3 report 56, audit appendix 458, all by wc -l. The only line-count error is W12 (the task 2 agent's message, 198 for 197), and W8 (766 chars as 767).

## Corrections owed before the batch 7 final report

1. Thinktime verdict: setup 3,883-4,229 ms (not 3,900-4,700 ms); screenshot medians 24.2-25.9 ms (not 24-29 ms); per-call rects 3.7-4.0 ms (not 3.6-3.9 ms); think max 0.174 ms (not 0.157 ms); naive total 6.5-7.0 s on the full-addition basis, or 6.4-6.9 s on the delta basis (not a mixed 6.4-7.0 s).
2. Thinktime research: agentpatterns 19 days, frowse 3 days; guibai date unverifiable from the page; surfs.dev citation dead, mark it or replace it.
3. Task 3 report: tip moved 36 commits since c19c227 (not twice); :148 line is 766 chars (not 767); clone2's fix doc is on main, not todolist-push.
4. G29 report: run 2 wall 7,516.5 ms (not 7,646 ms); drop or re-time the "(AT-SPI dismiss, 'Continue', 0.2 ms)" figure; reword the XDG wrapper sentence to state the ordering explicitly.
5. Open for Muse: the last30days install decision for clone1 (git clone as clone2 did, or stay uninstalled), and the three HIGH full fixes (V1 coordinator re-record per AM-13; V2 laptop logs or re-run; V3 laptop files or judge re-run).

## Correction to this report (batch 7 fix): W11 is wrong and is withdrawn

W11 claimed the task 3 report wrongly groups clone2's fix report
doc with the four fix commits "on todolist-push". That finding is
itself wrong, and it is withdrawn. The task 3 report's grouping was
correct. Evidence, re-checked first-hand by the fix agent:

- Commit 16c4196 IS an ancestor of origin/todolist-push
  (git merge-base --is-ancestor 16c4196 origin/todolist-push
  returns true).
- The consolidated corrections document
  improvements/batch7-high-corrections-20261122.md EXISTS in the
  todolist-push tree at tip da60024 (78 lines, read back with
  git show da60024:...). This is the document the task 3 report
  verifies in its V1 section ("Present at the tip, read in full"),
  and the "on todolist-push" in the task 3 report attaches to the
  four fix commits, all verified ancestors of da60024.
- Commit 5777535 is a different document,
  docs/clone2-batch7-high-fixes-20261122.md, clone2's task 3 report,
  on main only (git log --all shows that single commit for the
  file; git cat-file -e da60024:docs/clone2-batch7-high-fixes-20261122.md
  fails). W11 conflated the two documents: the corrections record
  (16c4196) is on todolist-push, the report doc (5777535) is on main.

The narrow fact inside W11 is true (the report doc is not in the
todolist-push tree at da60024), but it does not make the task 3
report wrong, because the task 3 report never claims that doc is on
todolist-push: its operative citations are to the corrections
document, which is on todolist-push. At most the intro bullet's
grouping is ambiguous wording, not a wrong fact.

Consequences: item 3 in "Corrections owed" is struck to the extent
it repeats W11 (no change to the task 3 report is owed for it), the
verdict paragraph's "W1, W2, W7, W8 and W11 must be corrected in
the source docs" is corrected to "W1, W2, W7 and W8" only, and M6's
list of the task 3 report's own errors is corrected from "W7, W8
and W11" to "W7 and W8" only. No other finding in this report is
affected.
