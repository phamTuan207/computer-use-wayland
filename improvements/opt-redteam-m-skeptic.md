# REDTEAM-M, Voice 2: THE SKEPTIC

Every unproven premise in the three verdicts and the four evidence bases, each with its file:line or its absence. Status scale: PROVEN (verified by this redteam by direct read), STATED (in the verdicts with a citation this redteam confirmed exists), UNPROVEN (asserted without a citation, or cited to a source that does not show it), STALE (true when written, overtaken by a later commit or log), CONTRADICTED (a newer fact says otherwise), ABSENT (the file or record does not exist). Branch todolist-push. Written 23:14-23:25 +07 Sat 2026-11-21. No live tests, no laptop driving. No em dashes or en dashes anywhere.

## 0. Premises this redteam PROVED by direct read (the skeptic concedes these)

- S-0.1 PROVEN. A5 two-stale-commits story. `git show d27ad0a:native/hyprglass-local-optics.lua | sha256sum` = 674441ea1b7d27f347aa8e31224ac5a8fcd923fc22ae75e65a0936ad8acc17c9. Manifest pin 674441ea matches d27ad0a exactly. 09a8df7 = 545455d3, b2afcd1 = 9a151634. M1 mechanism A6 and M1 verdict A step 1 are confirmed.
- S-0.2 PROVEN. D throw site. driver.sys.mjs line 4616 dereferences browserElement.namespaceURI with no null check, reached via #registerWindow line 4640 and newSession lines 2706-2707, in ~/workspace/zen_tab_cleanup/source/driver.sys.mjs-FIREFOX_160_0_RELEASE. TabManager.sys.mjs getBrowserForTab lines 39-41 returns tab?.linkedBrowser ?? null. M2 mechanism section D and M2 verdict D-2 discussion are confirmed at the code level.
- S-0.3 PROVEN. hl.dsp.focus string exists in repo precedent. tests/browser_field_live.py:98, tests/browser_task_benchmark.py:234, tests/optimization_live.py:147 and 241 all call `hl.dsp.focus({ workspace = "N" })` via cu.run. M2 verdict's correction of its own mechanism paper is confirmed as a citation.
- S-0.4 PROVEN. run_live.py has no ensure_visible. Grep returns nothing in tests/realistic/run_live.py; ensure_visible exists at tests/realistic/run_agyq2.py:351 and tests/realistic/run_codex_y5.py:1161. ZEN crawl G-11 and M2 G-2 note are confirmed as stated.
- S-0.5 PROVEN. test_cursor_session.py does not compile on VM Python 3.12.3. py_compile fails with SyntaxError line 585, too many statically nested blocks. M1 evidence lines 110-112 and M1 verdict lines 52-53 are confirmed in substance; the line number drifted from 570 to 585.
- S-0.6 PROVEN. Commit 26366a9 swept another worker's file. `git show 26366a9 --stat` lists improvements/worker-y14b-fix4-council-1.md (+329) alongside improvements/worker-opt-method-log.md (+37). CM-3 / Rule 3 violation is proven.
- S-0.7 PROVEN. F3 22:56 recurrence. improvements/worker-f3-marionette-slot-log.md tail: POST /session HTTP 500 browserElement is null at 22:56:12 and 22:56:31, after close3 (AFTER 15 tabs). Not mentioned in M2 or ORDER.
- S-0.8 PROVEN. Graph rule empirically confirmed by the merge. MEMORY.md 23:05: merge 0ac4311 (313 commits) + 0c473f9, main HEAD 5c94e6c, graph UTC 21/11 re-measured 455 commits + 1 PR = 456, exceeding 240 (was 145 at 22:51). CM-4's falsifier did not fire. The mechanism is confirmed; the 22:52 tooltip-vs-GraphQL gap (136 vs 145) remains unexplained except by the uncited "cache" claim.
- S-0.9 PROVEN. F1 round-2 commits landed after M1 verdict part 1. 392bc09 at 22:55:43 +07, 5b11696 at 22:56:44 +07, M1 verdict part 1 (7f96153) at 22:53:37 +07. M1 A step 2 items A1-A6 are done in code: guard_reply catches UnicodeDecodeError (scripts/cursor_theme.py:108), drain errors=replace with deque maxlen=200 (scripts/cursor_session.py:237), _settle_drain present, redact_text in _tail.
- S-0.10 PROVEN. Flicker work log file absent. `ls improvements/ | grep -i flicker` returns nothing. SRC section 3.2 gap and M1 mechanism C2 note are confirmed.

## 1. Premises that are UNPROVEN (asserted, no citation that shows it)

- P-1. UNPROVEN. D-2 veto premise, the signature story. M2 verdict section D and M2 safety VETO 1 assert "no verified signature story for a repacked omni.ja". No source in the F3 log, the M2 mechanism paper, or the M2 verdict shows what Zen does with a repacked omni.ja. The only occurrence is the mechanism paper's own assertion (opt-council-m2-mechanism.md:35). The veto's other two grounds (repack on every update, restart already clears it) are cited; the signature premise is not.
- P-2. UNPROVEN. The workspace-switch command works live. The string exists (S-0.3), but no live run on this Hyprland 0.57.2 proves `hl.dsp.focus({ workspace = "N" })` switches workspaces. F3 introspection 22:50-22:51 shows hl.dsp.workspace has NO goto/switch and hl.dsp.focus is a FUNCTION; the test files citing the form record no live run against this compositor in the verdicts. E-1 and E-3 rest on it.
- P-3. UNPROVEN. The 20s session deadline. scripts/first_action.py:56 sets DEFAULT_SESSION_DEADLINE_S = 20.0. No measured distribution of session-start times exists in any verdict, crawl, or log read. M1 B step 6 admits it is a chosen value. The deadline is load-bearing in B step 3 (every start slower than 20s becomes a fallback) with zero measurements behind it.
- P-4. UNPROVEN. The 30s order-to-first-visible-action target. scripts/first_action.py:57 sets FIRST_VISIBLE_ACTION_TARGET_MS = 30000. It is the owner's stated requirement (22:21), not a measured floor. M1 B step 6 admits the floor may be above 30s on a cold start (daemon up to 15s, scripts/overlay.py:420-453; liquid warm-up up to 30.0s, scripts/indicator.py:72-79). No cold-start measurement exists.
- P-5. UNPROVEN. The warm-up window for the A6/C1 hyprglass gate. M1 A step 6 and C1 step 2 require the gate to distinguish "glass not loaded" from "glass loading" (shader warm-up window, F1 council 2 F9). No number of seconds is given anywhere in the verdicts. A gate with an unquantified window cannot be implemented as written.
- P-6. UNPROVEN. The lock-holding wrapper for live activation. M1 A step 4 precondition 4 says "build the lock-holding wrapper FIRST, because activate-glass.py takes no lock today". No wrapper file is cited. activate-cursor-guard.py:63 takes owner_lock itself; activate-glass.py has no owner_lock reference (grep). F1 log line 371 mentions a wrapper, but no wrapper exists in the repo as read. The precondition's first clause is an instruction, not a fact; whether the wrapper exists is unproven.
- P-7. UNPROVEN. The old `act` path prints a pointer to act-now. M1 B step 1 gates on it. Grep for 'act-now' in scripts/cu.py returns only the subparser (line 2311) and the dispatch (line 2491). The refusal text (require_session, lines 2599-2602) contains no act-now pointer. The gate is not met in current code.
- P-8. UNPROVEN. The fallback classifier covers the new error strings. scripts/first_action.py:157-177 keys one branch on 'Expecting value', the old bare JSONDecodeError text. Commit 392bc09 rewrote the error to the named form, which lacks that substring. No test in the verdicts re-verifies the classifier against post-392bc09 strings. M1 B step 3's gate ("one new test per fallback predicate branch") does not require it.
- P-9. UNPROVEN. session_live() distinguishes a dead session from a transient socket error. scripts/overlay.py:146-161 returns False on ANY RuntimeError/OSError/ValueError. first_action.py:296 uses it to decide the timed_out fallback case. No verdict examines whether a transient error can produce a False that authorizes a replay while a session is live. Safety veto V6 is the property at risk.
- P-10. UNPROVEN. The A3 marker proves layer() registration and material values. The marker prints after config() and layer() return (M2 F-2). A silent failure inside layer() (returns without registering) still prints the marker. No read-back of registration or values is specified. The claim in M2 section F and ORDER O-2 ("proves the FULL profile") exceeds what the specified marker can show.
- P-11. UNPROVEN. Parse-2 determinism across restarts. Y6r R1's chain (pin diff lines 6270, 6507, 1913-1915; layers.enabled true at 21:57) proves config() applied once. The F no-reload ruling generalizes one load run (n=1) into "parse 2 already applies the profile deterministically". No second load run is cited. The load-only trial (F-8) is the test that would prove it, and it has not run.
- P-12. UNPROVEN. The pre-flight's false-positive rate and perturbation cost. ORDER A-4 asks it; no verdict answers it. diagnose_body samples twice 300 ms apart when hidden and the experiment payload includes a 5 s rAF window, all run as evals on the tab to be driven. No measurement on healthy tabs exists. O-6 makes it a gate on every live run at ranks 5-7.
- P-13. UNPROVEN. The 71 lines / 45 files PII count. ORDER section 3.4 cites "live-test-log.md line 3288 and 71 lines / 45 files of real name" with no citation to the sweep that produced the count. The scrub's scope (O-5) rests on an uncited number.
- P-14. UNPROVEN. The tooltip-vs-GraphQL gap explanation. ORDER section 4.2 says the tooltip (136) and GraphQL (145) differ "because they were read at different times and the graph caches". No evidence for the caching claim is cited. The 9-count gap is unexplained, not explained.
- P-15. UNPROVEN. The wedge and the slot share one cause. M2 mechanism section E leans toward the common-cause reading ("one restart cured both") and says the lean is not evidence. No capture supports it. The 22:56 recurrence (slot failed, no wedge reported) is evidence in the other direction and is not in the verdicts. The split (treat as separate until a capture proves otherwise) is the honest stance; the lean itself is unproven and should not be carried as a prior.

## 2. Premises that are STALE (true when written, overtaken since)

- P-16. STALE. M1 A step 2 (seven code gaps). True at M1 verdict part 1 (7f96153, 22:53:37 +07). Overtaken by 392bc09 (22:55:43) and 5b11696 (22:56:44). Six of seven items are done in code (S-0.9). Only A7 (exact-envelope assertion, tests/test_cursor_session.py:791) remains open.
- P-17. STALE. "VM re deletion cause unknown". M1 open gaps, ORDER P0, M2 safety paper ("root cause is still unknown"). Solved 22:57 (MEMORY.md): Y13r2 redteam self-deleting shim A6e deleted the wrong file; VMFIX c16dd4e restored durably. M1's reasoning does not depend on it; ORDER's P0 watch rationale does.
- P-18. STALE. M2 D-7 target of 28 tabs (13 real + 14 about:blank + 1 httpbin + 1 BiDi fixture, 22:10 baseline). Overtaken by F3's FULL cleanup 22:54-22:56 (AFTER 15 tabs, 14 real + 1 sacrificial) under the owner steer to delete tabs definitely no longer used. The target now contradicts the executed cleanup.
- P-19. STALE. "F3 slot FIXED 22:48" as the live baseline. Overtaken by the 22:56:12 recurrence (S-0.7). Every verdict that treats 22:48 as the closing evidence for rank 1 (M1 B5, M2 D, ORDER O-1) is stale.
- P-20. STALE. "Exact Omarchy launcher command unknown" (ZEN G-06, M2 E-1). Closed by F3 log 22:50: `omarchy-menu toggle root` (SUPER+SPACE), in ~/.config/hypr/bindings.lua.
- P-21. STALE. "Exact hl.dsp command string is NOT in any primary source" (ORDER 5.2). False since M2 verdict section 2 (b21fe1c, 22:58:29) corrected it with four repo citations (S-0.3). ORDER s5 was committed 22:55:47, before the correction landed; the contradiction is a timing artifact, but the document as it stands contradicts its sibling.
- P-22. STALE. ORDER 4.3 deadline arithmetic (gap ~95, 68 minutes left at 22:52). The graph target is exceeded (456 at 23:05, S-0.8). The arithmetic is moot and should be archived, not left as a live claim.
- P-23. STALE. "No merge of todolist-push into main has landed recently". Last merge before this redteam's check was 96438bb at 15:43 +07. Overtaken 23:05 by merge 0ac4311 (313 commits) + 0c473f9, main HEAD 5c94e6c. This redteam's own section-0 N-5 claim is withdrawn.
- P-24. STALE. ZEN crawl P2 note that Y13r2's log is "IN PROGRESS, final verdict PENDING". Y13r2 final landed (2fee242, BLOCK, redteam be88321). ZEN G-04 is closed.
- P-25. STALE. "F1 adjudication deferred" (ZEN G-09). F1 council 3 landed with verdict AMEND (improvements/worker-f1-council-3.md:3). Closed.
- P-26. STALE. M1 verdict line citations for the diagnostic path. M1 cites guard_reply lines 99-113 and supervise lines 210-260; current code has guard_reply at line 104 and supervise at line 212, with the function bodies extended by the round-2 commits. The citations drifted by about 5 lines. Minor, but the evidence contract demands file:line accuracy at fix time, and the verdict's lines no longer point at the code it describes.

## 3. Records that are ABSENT (the file, log, or artifact does not exist)

- P-27. ABSENT. The flicker work log file. improvements/overlay-flicker-work-log-20261121.md does not exist in the VM repo (S-0.10). The 2.2.1 numbers (0 idle paints in 122 windows, 32/32 frames identical) are cited as todolist-recorded, not re-verified. M1 mechanism C2 and M1 verdict C2 step 3 both carry this honestly; the numbers still rest on a missing file.
- P-28. ABSENT. The pre-restart tab-list snapshot for the 22:36 restart. ZEN G-08: F3 verified 67 contexts and 13 real tabs present after restart, but the pre-restart list was never saved as a file. The LMS login tab loss (opened about 22:26, never flushed) is recorded only in prose. M2 D-4 prescribes a snapshot FIRST for future restarts; the 22:36 instance cannot be retroactively verified.
- P-29. ABSENT. Any wedge signature capture. ZEN G-03, M2 E-4: no hyprctl clients/workspaces/activewindow dump, no BiDi getTree, no Marionette POST attempt against the wedged state exists for the 22:25 wedge or for the 22:56 recurrence. E-4's capture rule has never been executed. The wedge mechanism is unknown because the evidence was never taken, twice.
- P-30. ABSENT. Any saved probe output from a hidden tab. M2 G: probe_q05e was built to capture htmlClass, but the output was never saved; zero positive sightings of tz-hidden on a hidden tab; zero saved htmlClass outputs; zero opacity readings; zero screenshots of the logo pulse markers. The V1 burden (two concordant "no class" records, output unsaved) is correctly placed by M2, but the underlying absence means V1 is neither proven nor falsified, and will stay so until the decisive experiment runs.
- P-31. ABSENT. The new-conf ldd output. ZEN G-10: Y6e's run has no saved ldd log for the rebuilt conf. M2 F-1 requires saving it. The ldd proof (rc=0) is asserted in the Y6r log, not saved as a file.
- P-32. ABSENT. The Y13g fix output. No log file, no commits matching Y13g, only a spawn note (worker-opt-method-log.md:79). Y13r2 BLOCK (2fee242, B1-B4 + 5 amend) names the fix worker; the worker has produced nothing observable by 23:14. ORDER rank 5 and M2 G-10 gate the Y13 live run on Y13g + fresh re-review; the gate's first leg has no artifact.
- P-33. ABSENT. The H3 acceptance record. M2 G-10 and U-1 resolve H3 per MEMORY.md 22:57 ("accepted Y13r2 proposal: 5a2b69d NO VERDICT + runner-quiet/ports check counts as the marker leg for this run, gate text unchanged, Y6 retry after Y13"). No council paper, log entry, or owner message is cited as the acceptance. The resolution rests on a MEMORY.md entry alone.
- P-34. ABSENT. The ZT-B run report. ZEN G-07: no ZT-B report file exists. ZT-00 steps 0-3 PASS as run by F2 at 22:44, but steps 4-7 and ZT-01..ZT-10 are unrun. The F2 ZT-00 run was INCONCLUSIVE (F2 log tail). No blind composite suite has ever run to completion.
- P-35. ABSENT. A live proof of the workspace-switch command. See P-2. The command exists in test code; no live run record exists.
- P-36. ABSENT. A measured session-start distribution. See P-3. No timing log of session starts exists in the evidence read.
- P-37. ABSENT. A saved BiDi getTree + tab list before any slot failure. M2 D-3 prescribes it; F3's 22:56 recurrence produced no getTree file. D-3 was not executed at the recurrence, the first failure after the method was written.
- P-38. ABSENT. The re-pin check (M1 A step 3). No check exists in sync-installed.py or setup that compares installed manifest profile_sha256 and library pins against the repo optics sha256 and fails loudly. The durability step is a prescription, not a fact; nothing in the repo implements it yet.

## 4. What would close each premise (the proof step, in one line each)

- P-1: cite a source for Zen's behavior on a repacked omni.ja, or strike the signature premise and restate the veto on the two cited grounds.
- P-2: one live run of `hl.dsp.focus({ workspace = "N" })` with activeworkspace + clients + screenshot before and after, saved to a file.
- P-3: a timing log of at least 10 session starts (cold and warm) with the distribution published, then set the deadline from it.
- P-4: a cold-start order-to-overlay measurement (daemon + liquid warm-up) published before the 30s target is enforced as a gate.
- P-5: a measured shader warm-up window in seconds, published in the gate design.
- P-6: the lock-holding wrapper as a file with a path, or a record that activate-cursor-guard.py:63 already holds the lock and no wrapper is needed.
- P-7: add the act-now pointer to the require_session refusal text, or strike the gate.
- P-8: a unit test per classifier branch against post-392bc09 error strings, run by an independent checker.
- P-9: a test where the session socket fails transiently while a session is live, showing the fallback is refused.
- P-10: a registration read-back after layer() returns, or downgrade O-2 to "proves the calls returned".
- P-11: a second nested load run showing parse-2 application again, or run the F-8 load-only trial and record it.
- P-12: a false-positive measurement of diagnose_body on healthy tabs, published before O-6 becomes a gate.
- P-13: cite the sweep that produced the 71/45 count, with its file and date.
- P-14: resolve the 136-vs-145 gap with a second GraphQL read at a stated time, or drop the cache explanation.
- P-15: one wedge capture with a BiDi click attempt recorded; until then, carry no common-cause prior.
- P-16: strike A1-A6 from M1 A step 2, keep A7, re-pin the line numbers.
- P-17: update ORDER P0 and Q-6 to record the solved cause and narrow the G-VMFIX watch.
- P-18: replace the D-7 target with the 22:56 baseline (14 real + 1 sacrificial, blanks closed).
- P-19: re-verify G-RESTORE after the last tab-close, and record the 22:56 recurrence in D and ORDER.
- P-20: record `omarchy-menu toggle root` as the launcher command in E-1.
- P-21: reconcile ORDER 5.2 with the M2 correction and the F3 introspection.
- P-22: archive ORDER 4.3; the target is exceeded (456 at 23:05).
- P-23: withdrawn by this redteam; the merge landed (0ac4311, 313 commits).
- P-24, P-25: record G-04 and G-09 as closed in the verdicts.
- P-26: re-pin M1's line citations to current code at fix time.
- P-27: recover or re-derive the 2.2.1 numbers from the todolist, or mark them unreproducible.
- P-28: no retroactive fix; enforce D-4's snapshot-first rule on the next restart and log compliance.
- P-29: execute E-4 at the next wedge or recurrence; a restart without a signature is a safety violation, enforce it.
- P-30: run the G-7 decisive experiment with every probe output saved, or stop citing V1 as wounded by unsaved records.
- P-31: run ldd on the staged conf path and save the output (M2 F-1).
- P-32: Y13g must land a log file and a fix diff, or Worker OPT must record that Y13g is stalled and reassign.
- P-33: cite the H3 acceptance in a council paper or log entry, not only MEMORY.md.
- P-34: run ZT-B and publish the report, or stop citing ZT-A as the test design.
- P-35: same as P-2.
- P-36: same as P-3.
- P-37: execute D-3 at the next slot failure; log the getTree file path.
- P-38: implement the re-pin check with a test on a deliberately drifted fixture (M1 A step 3 gate).

## 5. Count

Proven by this redteam: 10 (S-0.1 to S-0.10). Unproven: 15 (P-1 to P-15). Stale: 11 (P-16 to P-26). Absent records: 12 (P-27 to P-38). The verdicts are strongest where they cite code (D throw site, F1 fix, act-now code) and weakest where they prescribe gates, deadlines, and counts without measurements (P-3, P-4, P-5, P-12, P-13) and where later events overtook them (P-16 to P-23). No verdict relies on a premise this paper shows to be false, except ORDER 5.2 (contradicted by the M2 correction) and M2 D-7's 28-tab target (contradicted by the executed cleanup). Those two are the only premises that are wrong, not merely unproven.
