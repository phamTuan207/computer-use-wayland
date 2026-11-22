# Batch 12 council 1, task 3: independent re-verification of the CB-8 audit

- Date: 2026-11-22, 13:40 +07.
- Reviewer: clone1, council 1, independent of the task 3 auditor.
- Report under review: docs/batch12-task3-cb8-audit-20261122.md, commit 73a759e on main, 169 lines (wc -l).
- Sources read first-hand, read-only, from branch todolist-push at HEAD 4305dcb. Nothing on todolist-push was modified. No live browser run, no harness run.
- Method: every number in the report was recomputed from the raw run JSONs on todolist-push; every evidence claim was re-checked against the two logs, the harness code, and whole-history git object lists. Each item below is marked CONFIRMED or REFUTED with the command run and its output.
- No em dash or en dash anywhere in this file. No personal info.

## 1. Claim (a) numbers, from improvements/s2-flip-reopen-runs/run-1..5.json

Command: git show origin/todolist-push:improvements/s2-flip-reopen-runs/run-N.json for N 1 to 5, fields extracted with python3 json.

- Walls: run 1 29020.4, run 2 27799.1, run 3 28112.6, run 4 28898.1, run 5 28560.9. Sorted: 27799.1, 28112.6, 28560.9, 28898.1, 29020.4. Median 28560.9 ms, 28.6 s. CONFIRMED.
- Brave, all 5: outcome sent, program ok True, completed 3, dom_act ms 51, 46, 46, 43, 43, program elapsed ms 140.5, 137.5, 144.9, 140.8, 141.2, CB-1 input_sent, target_received, verified all True, V12 found True, attempts 1, items 43, 45, 47, 49, 51, messages S2-REOPEN-R1 to R5-BRAVE-IGNORE-TEST. CONFIRMED.
- Chromium, all 5: outcome sent, program ok True, completed 2, dom_act ms 12, 9, 9, 8, 10, program elapsed ms 113.0, 106.6, 107.1, 99.4, 104.2, focus_enter ok True, focus focused True, tag TEXTAREA, enter ok True, ms 25, 21, 23, 25, 23, CB-1 all True, V12 found True, attempts 1, items 54, 56, 58, 60, 62, messages S2-REOPEN-R1 to R5-CHROMIUM-IGNORE-TEST. CONFIRMED.
- Observe: Brave elements 72, 73, 75, 77, 79, truncated False, routing reason "complete coverage", fell_through empty, composer_present True. Chromium elements 80, truncated True, routing_relaxed True, reason "relaxed gate: truncated inventory (80 elements), send target covered", composer_present True. CONFIRMED.
- Chromium pre-send count 0, items 51, 54, 56, 58, 60; delayed_count chromium count 1, items 54, 56, 58, 60, 62, every run. No double-send. CONFIRMED.
- Top level, all 5 runs: dry_run False, activate False, model_calls 0, program_variant "brave=fill,chromium=set_value", chromium_set_value True. Per-browser model_calls 0. CONFIRMED.
- p9 ok True in all 10 halves, png paths exactly the 10 paths the report lists. CONFIRMED.
- The reopen log run table (section 4, lines 180-220) matches the JSONs exactly on every checked field: wall, program elapsed, dom_act ms, V12 items, observe elements, pre and delayed counts. CONFIRMED.

## 2. Claim (b) numbers, from improvements/s2-flip-b1-runs/run-1..5.json

Command: git show origin/todolist-push:improvements/s2-flip-b1-runs/run-N.json for N 1 to 5, fields extracted with python3 json.

- Walls: run 1 18477.4, run 2 20592.9, run 3 18839.7, run 4 18738.7, run 5 19094.0. Sorted: 18477.4, 18738.7, 18839.7, 19094.0, 20592.9. Median 18839.7 ms, 18.8 s. CONFIRMED.
- Program elapsed ms, exact values: 97.656, 106.622, 91.575, 102.811, 104.563. Range 91.575 to 106.622 ms. The report and log figure of 91.6 to 106.6 ms is correct. CONFIRMED.
- All 5: outcome sent, program ok True, completed 2, dom_act ms 8, 9, 8, 7, 8, focus_enter ok True, focused TEXTAREA, enter ok True, ms 23, 23, 17, 18, 20, CB-1 all True, V12 found True, attempts 1, items 44, 46, 48, 50, 52, pre count 0, items 41, 44, 46, 48, 50, delayed count 1, items 44, 46, 48, 50, 52, model_calls 0, dry_run False, program_variant "set_value", messages C5-B1-R1 to R5-CHROMIUM-IGNORE-TEST, each exactly once. CONFIRMED.
- p9 ok True in all 5, png paths exactly the 5 paths the report lists. CONFIRMED.
- The input-fix log (b1) run table (lines 426-457) matches the JSONs exactly on every checked field. CONFIRMED.

## 3. Aborts, disclosed

Command: git show origin/todolist-push:improvements/s2-flip-b1-runs/run-N-aborted.json for N 2 to 5.

- Runs 2 to 5 each have a first attempt with outcome aborted-routing and error "router fell through to screenshot: fail-closed fallback: no backend returned complete coverage", exact string, all 4. CONFIRMED.
- The aborted JSONs are preserved as run-2..5-aborted.json on the branch. CONFIRMED.
- The input-fix log discloses the aborts in the time log (lines 116-122), in section 7.5 ("The aborts are a measurement-gate artifact, not send failures: no program ran in runs 2-5, nothing was sent"), and in the commit record (section 9, "plus run-2..5-aborted.json (the first-attempt routing aborts)"). CONFIRMED.

## 4. Mechanism, from scripts/s2_flip_live.py at todolist-push HEAD 4305dcb

Command: git show 4305dcb:scripts/s2_flip_live.py, grep and sed of the two functions.

- build_program_set_value docstring: "The input-free send program (C5-B1): set_value, no mouse. ... inside cdp.mjs set_value, zero Input calls ... The Enter itself is NOT in this program ... the harness focuses the composer and dispatches Enter with the /tmp/c5-focusenter.mjs helper after this program returns." CONFIRMED.
- focus_enter docstring: "C5-B1 send step: focus the composer + CDP Enter. Runs /tmp/c5-focusenter.mjs (Runtime.evaluate focus plus Input.dispatchKeyEvent Enter, zero mouse events)." CONFIRMED.
- LAPTOP_FOCUSENTER = '/tmp/c5-focusenter.mjs', line 76. CONFIRMED.
- The "CDP Enter" is Input.dispatchKeyEvent, not a keystroke and not a mouse event. CONFIRMED.
- /tmp/c5-focusenter.mjs is not in the repo: git rev-list --all --objects | grep -i focusenter returns 0 lines. CONFIRMED.
- The (b1) shape is re-proven by the reopen Chromium halves: 5 of 5 sent with set_value, focus_enter ok True, enter 21 to 25 ms, CB-1 all True, V12 attempt 1, pre 0, delayed 1. CONFIRMED.

## 5. Central claim: the 15 P9 PNGs do not exist anywhere in repo history

Commands and outputs:

- git ls-tree -r --name-only 1a3356d improvements/s2-flip-reopen-runs/ lists only run-1..5.json. No PNG. CONFIRMED.
- git ls-tree -r --name-only 4305dcb improvements/s2-flip-reopen-runs/ lists only run-1..5.json. No PNG. CONFIRMED.
- git ls-tree -r --name-only 4305dcb improvements/s2-flip-b1-runs/ lists only run-1..5.json and run-2..5-aborted.json. No PNG. CONFIRMED.
- git rev-list --all --objects | grep -i p9 returns 0 lines (exit 1). No object path in the whole history contains "p9". CONFIRMED.
- git rev-list --all --objects | grep -i "\.png" returns 51 lines, none under any s2-flip directory (they are docs/benchmarks and docs/clone2-zen-ordinary-user-run-20261121-screenshots). The repo does contain PNGs; it contains no P9 PNGs. CONFIRMED.
- git cat-file -e 4305dcb:<path> for each of the 15 exact paths the JSONs reference returns missing for all 15: 10 reopen paths p9-runN-brave.png and p9-runN-chromium.png, N 1 to 5, and 5 (b1) paths p9-runN-chromium.png, N 1 to 5. CONFIRMED.
- The repair list paths in the report match the JSON-referenced paths exactly. CONFIRMED.

## 6. Log promises and P9 review claims

- Reopen log, commit 1a3356d, 346 lines (git show 1a3356d:improvements/worker-click5-s2-reopen-log.md | wc -l = 346). CONFIRMED.
- Reopen log section 8 is the commit record and says: "Re-open run JSONs + P9 PNGs: improvements/s2-flip-reopen-runs/run-1..5.json plus p9-runN-brave.png and p9-runN-chromium.png (to be committed with this log)." The promise is real and the section citation is correct. CONFIRMED.
- Reopen log section 0 states the B1 condition verbatim: "P9: one final screenshot per run, reviewed before scoring (B1 condition: any DOM-vs-render mismatch FAILS the run)." CONFIRMED.
- Reopen log section 5 claims "P9 PASS 10/10" with one prose description per run (10 descriptions, run 1 to 5, both browsers). CONFIRMED as a log claim; the PNGs it rests on are the missing files from section 5 above.
- Reopen log section 6 verdict: median 28560.9 ms (28.6 s), 5/5 runs, 10/10 sends, recommend EXPAND; caveat 1 states the DISCLOSED relaxed routing gate. CONFIRMED.
- Input-fix log, commit 4bd6292, 523 lines (git show 4bd6292:improvements/worker-click5-input-fix-log.md | wc -l = 523). CONFIRMED.
- Input-fix log section 7.1, "D-B1: dispatchKeyEvent answers on the stuck tab": "Input.dispatchKeyEvent answers in 2ms, on the same tab, in the same minute." CONFIRMED.
- Input-fix log section 7.5 contains the (b1) P9 review: "P9 reviewed: run 1 P9 shows the blue user bubble C5-B1-R1-CHROMIUM-IGNORE-TEST, composer empty. Run 5 P9 shows the R2, R3, R4 and R5 bubbles, composer empty. DOM and render agree in both. P9 PASS all 5 runs." CONFIRMED as a log claim; the PNGs it rests on are missing.
- Commit 4305dcb message: "docs: COORD-CLICK-5 log, S2-REOPEN verified 5/5 median 28.6s, EXPAND approved in principle, clone1 batch 12 queued." The "EXPAND approved in principle" record is real. CONFIRMED.
- Reopen log hash recorded in 212e0ad ("C5-S2-REOPEN log: record own commit hash 1a3356d", log line 338). Input-fix log hash recorded in 030c227 ("C5-INPUT-FIX log: record own commit hash 4bd6292", log line 516 at HEAD). CONFIRMED.
- The batch 12 task 1 report was not on main when the audit ran: task 3 commit 73a759e is 2026-11-22 06:26:33 UTC; the task 1 report landed in ed59f6a at 2026-11-22 06:31:48 UTC, about 5 minutes later. CONFIRMED.
- The report has 0 em dashes and 0 en dashes (grep returns 0 lines) and 169 lines. CONFIRMED.
- No dry-run JSON is committed: the reopen run directory holds only run-1..5.json at every checked commit. CONFIRMED.

## 7. Corrections (2, neither changes any verdict)

### C1. Input-fix log commit record is section 9, not section 8. REFUTED as cited.

The report cites the input-fix log commit record as "section 8" in two places: the evidence base table ("section 8 commit record") and claim (b) ("The input-fix log section 8 says the PNGs were 'to be committed with this log'").

Section 8 of the input-fix log is the verdict: "## 8. Verdict: (b1) WORKS, 5/5 verified. The S2 flip CAN re-open on the Chromium half." It says nothing about committing PNGs.

The commit record is section 9, and it does contain the promise verbatim: "(b1) run JSONs + P9 PNGs: improvements/s2-flip-b1-runs/run-1..5.json, plus run-2..5-aborted.json (the first-attempt routing aborts), to be committed with this log."

Correction: change both "section 8" references for the input-fix log to "section 9". The promise itself is confirmed, so the REVOKED verdict for claim (b) stands unchanged. The error likely came from copying the reopen log, where the commit record really is section 8.

### C2. Aborted JSONs landed in 4bd6292, not "be2371e range". REFUTED as cited.

The evidence base table says the aborted JSONs are "in commit be2371e range".

Command: git log origin/todolist-push --diff-filter=A --format="%h %s" -- improvements/s2-flip-b1-runs/run-2-aborted.json returns 4bd6292 only. The same command for run-1.json also returns 4bd6292 only. Commit be2371e changed exactly one file, scripts/s2_flip_live.py (35 lines, the relaxed routing gate); it added no JSON.

The input-fix log's own time log carries the same wrong reference: "Aborted run JSONs preserved as run-N-aborted.json. Committed be2371e, push verified." That is presumably where the auditor took it from, and the log itself is inaccurate on this point.

Correction: the aborted JSONs landed in 4bd6292. This does not affect any verdict: the aborted JSONs exist on the branch and were verified first-hand in section 3 above.

## 8. Council 1 verdict

- All numbers in the report are verified correct from the raw JSONs: claim (a) walls and median, all 10 per-send rows, observe and routing, pre and delayed counts, 0 model calls; claim (b) walls and median, program elapsed range, all 5 per-run rows, aborts, mechanism.
- All evidence claims are verified: the 15 P9 PNGs do not exist anywhere in repo history, both logs promised them ("to be committed with this log"), both logs claim P9 PASS from reading them, and the EXPAND approval in 4305dcb rests on the reopen PASS.
- The report's reasoning stands: p9.ok True in a JSON only proves the capture call returned ok, not that any reviewer read the image; prose in a log is the claim, not evidence for it; P9 is a scoring condition under the B1 rule, so a PASS whose render check cannot be checked by any reviewer does not meet CB-8.
- Verdict: CONFIRMED WITH 2 CORRECTIONS (C1, C2, both citation fixes). Both REVOKED verdicts STAND. The repair list stands as written; its 15 paths were verified against the JSONs.
- The 2 corrections should be applied to the report before it is cited further, but they do not require re-auditing any number.
