# Batch 12 redteam task 3: CB-8 audit of 2 DONE claims

- Date: 2026-11-22, 13:40 +07.
- Reviewer: clone1 redteam, independent of the batch 12 task 3 auditor.
- Target: docs/batch12-task3-cb8-audit-20261122.md, commit 73a759e on main, 169 lines.
- Verdict: SURVIVES.
- Breaking findings: 0. Minor findings: 3. All three are citation precision only. None changes a number, a verdict, or the repair list.
- Method: every load-bearing claim was re-checked first-hand against the primary sources, read-only, from branch todolist-push at HEAD 4305dcb (same HEAD the audit used, still the tip). All 5 reopen run JSONs, all 5 scored (b1) run JSONs, and all 4 aborted JSONs were re-parsed and recomputed. Both logs were re-read in full. The P9 absence check was re-run. No em dash or en dash anywhere in this file. No personal info.

## Breaking findings

None. The audit's central claim survives every attack tried below: the 15 P9 PNGs are absent from the whole repo history, P9 is a scoring condition by the logs' own words, and both REVOKED verdicts follow from CB-8.

## Minor findings

### M1. Audit line 102: "The log figure of 91.6 to 106.6 ms is correct" misattributes the figure

- What is wrong: the input-fix log never states program elapsed 91.6 to 106.6 ms. A grep of the full input-fix log at commit 4bd6292 finds no "91.6" and no "106.6". Its run table lists only dom_act ms (7 to 9) per run, not program elapsed. The figure 91.6 to 106.6 ms appears only in the reopen log, section 0, line 32, restating the (b1) result.
- Correct value: the range itself is right. Recomputed from the (b1) run JSONs, program elapsed values are 97.656, 106.622, 91.575, 102.811, 104.563 ms, so the exact range is 91.575 to 106.622 ms. The auditor evidently computed this from the JSONs, not from a log.
- Fix: change line 102 to say the range is the auditor's recomputation from the raw JSONs, and cite the reopen log section 0 as a restatement, not the input-fix log as the source. Line 142 repeats "program elapsed 91.6 to 106.6 ms" in the verified list; that value is correct and needs no change, only the attribution on line 102.
- Impact: none on the verdict. The number is correct, the source label is wrong.

### M2. Audit line 17: aborted JSONs listed as "in commit be2371e range"

- What is wrong: the 4 aborted JSONs were not added in be2371e or near it. `git log origin/todolist-push -- improvements/s2-flip-b1-runs/run-2-aborted.json` returns one commit only: 4bd6292, the same commit that added the scored (b1) JSONs. Commit be2371e is the relaxed routing gate harness change; it never touched those files.
- Correct value: improvements/s2-flip-b1-runs/run-2..5-aborted.json, commit 4bd6292.
- Fix: change the evidence base table entry to commit 4bd6292.
- Impact: none on the verdict. The files exist, were read, and their contents check out exactly. Only the commit attribution is wrong.

### M3. Audit lines 69 and 134: "The JSON field p9.ok True" names a field that does not exist

- What is wrong: there is no single `p9.ok` field in the run JSONs. The structure is top-level `p9`, with one object per browser: `p9.brave.ok` and `p9.chromium.ok` (reopen runs), or `p9.chromium.ok` ((b1) runs), each with `ok`, `png`, and `wall_ms`. The audit's sentence is true of each browser's `ok` value, but the field path as written does not exist.
- Correct value: `p9.<browser>.ok` is True for every browser half in all 10 runs, and each carries the `png` path the audit lists.
- Fix: write `p9.<browser>.ok` on lines 69 and 134.
- Impact: none on the verdict. The substance is right: an `ok` True only proves the capture call returned ok, not that any reviewer read the image.

## Numbers re-verified first-hand (all match the audit exactly)

Reopen runs, from improvements/s2-flip-reopen-runs/run-1..5.json:

- Walls: 29020.4, 27799.1, 28112.6, 28898.1, 28560.9. Sorted median 28560.9 ms, 28.6 s. Correct.
- Brave per run: program ok True, completed 3, dom_act 51, 46, 46, 43, 43 ms, elapsed 140.516, 137.493, 144.855, 140.832, 141.234 ms, V12 found True attempt 1 items 43, 45, 47, 49, 51, CB-1 all True. Correct.
- Chromium per run: program ok True, completed 2, dom_act 12, 9, 9, 8, 10 ms, elapsed 113.005, 106.613, 107.077, 99.412, 104.164 ms, V12 found True attempt 1 items 54, 56, 58, 60, 62, CB-1 all True, focus_enter ok True, enter 25, 21, 23, 25, 23 ms. Correct.
- Observe elements: Brave 72, 73, 75, 77, 79, not truncated, strict routing. Chromium 80, truncated, routing_relaxed True, composer present. Correct.
- Pre-send count 0, items 51, 54, 56, 58, 60. Delayed count 1, items 54, 56, 58, 60, 62. Correct.
- Model calls 0, dry_run False, activate False, chromium_set_value True, program_variant "brave=fill,chromium=set_value", all 5 runs. Correct.
- Top-level p9 per run lists exactly the 10 PNG paths the audit lists, each with ok True. Correct.

(b1) runs, from improvements/s2-flip-b1-runs/run-1..5.json:

- Walls: 18477.4, 20592.9, 18839.7, 18738.7, 19094.0. Sorted median 18839.7 ms, 18.8 s. Correct.
- Program elapsed exact: 97.656, 106.622, 91.575, 102.811, 104.563 ms. Range 91.575 to 106.622 ms. Correct (see M1 on attribution).
- V12 found True attempt 1 items 44, 46, 48, 50, 52. CB-1 all True. Focus enter 23, 23, 17, 18, 20 ms. Pre count 0, items 41, 44, 46, 48, 50. Delayed count 1, items 44, 46, 48, 50, 52. Messages C5-B1-R1 to R5-CHROMIUM-IGNORE-TEST, each once. Correct.

Aborted runs, from improvements/s2-flip-b1-runs/run-2..5-aborted.json:

- All 4 exist. Outcome aborted-routing, error "router fell through to screenshot: fail-closed fallback: no backend returned complete coverage", program None. Correct, word for word.

## Attacks tried and rejected

### A1. Is P9 really a scoring condition, or does the log say something weaker?

Rejected. The reopen log section 0 states it plainly: "P9: one final screenshot per run, reviewed before scoring (B1 condition: any DOM-vs-render mismatch FAILS the run)." The audit quotes this accurately. The condition is not a nicety the auditor invented.

### A2. Are the P9 PNGs really absent from all repo history, or did the auditor check the wrong branch or miss a commit?

Rejected. Re-run first-hand in this clone: `git rev-list --all --objects | grep -i p9` returns nothing (exit 1). All 38 origin branches are fetched locally (compared `git ls-remote --heads origin` against local remote-tracking branches, zero missing), so the check covers the whole remote history, not just todolist-push. `git ls-tree` at 1a3356d and at HEAD 4305dcb for improvements/s2-flip-reopen-runs lists only run-1..5.json. The same for improvements/s2-flip-b1-runs lists only the 5 scored JSONs and the 4 aborted JSONs. Other PNGs do exist in history (benchmark and clone2 screenshots), so the grep was not blind; it simply finds no p9 file. The audit's central claim holds.

### A3. Are the (b1) numbers actually from the (b1) run JSONs?

Rejected. Recomputed above to three decimals. Every figure matches, including the exact elapsed range 91.575 to 106.622 ms and the median wall 18839.7 ms.

### A4. Are the 4 aborted first attempts really disclosed, with aborted JSONs preserved?

Rejected. The input-fix log discloses them in three places: the time log (12:44:56-12:47:23, runs 2-5 ABORTED-ROUTING), section 7.5 (cause, "no program ran in runs 2-5, nothing was sent", "aborted JSONs are preserved as run-N-aborted.json"), and the commit record. The 4 aborted JSONs exist with the exact error string. The 5/5 figure counts the 5 scored runs, and the aborts are on the record.

### A5. Does the section 5 prose prove the PNGs were reviewed, since it is specific?

Rejected, but considered. The reopen log section 5 prose does contain specific incidental details (cap banners between bubbles, R1 scrolled off the top in run 5 Chromium), which are consistent with a real review having happened. Specificity is not committable evidence under CB-8: no reviewer can re-open the image and check the claim, because the image is not in the repo. The audit is right to treat prose as the claim itself, not evidence for it. This does not rescue either PASS.

### A6. Did the auditor reuse numbers from the batch 12 task 1 verification report?

Rejected. docs/batch12-task1-s2-reopen-verify-20261122.md is still absent from origin/main (checked with `git ls-tree -r --name-only origin/main`, no match). The independence claim holds.

### A7. Are the audit's line counts and hash records right?

Rejected as an attack. Reopen log: 346 lines at commit 1a3356d (347 at HEAD 4305dcb, because 212e0ad added the hash record). Input-fix log: 523 lines at commit 4bd6292 (525 at HEAD). Commit 212e0ad records hash 1a3356d; commit 030c227 records hash 4bd6292. All correct.

### A8. Is the "EXPAND approved in principle" gating consequence real?

Rejected. Commit 4305dcb's message says "EXPAND approved in principle", and its diff adds coord log section 26: "C5-S2-REOPEN verified: class completes 5/5, median 28.6s; EXPAND approved in principle, sequenced after landing". The audit's gating consequence is accurate. Note the coordinator's own wording sequences EXPAND after landing, which is consistent with the audit's "EXPAND should wait" rather than in tension with it.

### A9. Is the mechanism description right?

Rejected. scripts/s2_flip_live.py at HEAD 4305dcb: build_program_set_value docstring says "The input-free send program (C5-B1): set_value, no mouse" and "The Enter itself is NOT in this program", with the /tmp/c5-focusenter.mjs helper after. focus_enter docstring says "Runs /tmp/c5-focusenter.mjs (Runtime.evaluate focus plus Input.dispatchKeyEvent Enter, zero mouse events)". LAPTOP_FOCUSENTER is '/tmp/c5-focusenter.mjs' at line 76. Input-fix log section 7.1 confirms Input.dispatchKeyEvent answers in 2 ms on the stuck tab. The helper file itself is not in the repo (no match in a full tree listing), which the audit names as a secondary open item, not a verdict reason. Correct.

## Conclusion

The audit SURVIVES. Both REVOKED verdicts stand: the measured numbers in both claims are correct, and the single missing artifact class in both, the P9 screenshots, is a scoring condition whose absence CB-8 does not let through. The three minor findings are citation precision (M1 figure attribution, M2 commit attribution, M3 field path). They should be fixed in a one-line-each correction pass, but none of them changes a number, a verdict, or the repair list. The repair list (commit the 15 PNGs at the exact referenced paths, record or commit the focus-enter helper, then re-audit by opening the PNGs) is the correct next step.
