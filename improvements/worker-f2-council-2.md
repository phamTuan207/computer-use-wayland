# Council Voice 2 verdict: Worker F2 silence fix (evidence + measurement)

Verdict: AMEND

Scope: audit of the EVIDENCE only. No code modified, no live browser action taken, no commit made by this council. Files read: improvements/worker-f2-silence-fix-log.md, improvements/first-visible-action-rule-20261121.md, scripts/first_action.py, scripts/cu.py (desktop_act, observe_screen), scripts/overlay.py, scripts/indicator.py, tests/test_first_action.py, improvements/worker-f3-marionette-slot-log.md. F2 commits checked: a576e69, afed06e, 8d1f775, 8979b30, 2495382, c2c0a8b, e016cde, 62ad028, 82539bf, all present on todolist-push. Tests re-run by this council: python3 -m unittest tests.test_first_action, 21 tests, OK in 0.56 s.

## What checks out (confirmed)

1. Overlay timings are internally consistent. Log vs rule doc agree on every run: run 1 order_to_overlay_ms 356, total 638, REFUSED; run 2 333, total 1477, 4/4; run 3 314, total 1592, 3/3; run 4 346, total 1998, 5/5; run 5 330, total 865, 1/1. Range 314 to 346 for runs 2 to 5, totals 865 to 1998 ms = 0.87 to 2.0 s, as claimed. Completed counts match the batch shapes in the log (run 2 Ctrl+N + click + type + Enter = 4, run 3 Ctrl+L + type + Enter = 3, run 4 Ctrl+N + wait + click + type + Enter = 5, run 5 Ctrl+W = 1).
2. Run 1 refusal is correct and matches code exactly. scripts/cu.py:1475 raises "screen observations support pointer actions only; use a window or accessibility target for typing" when a screen observation carries key/type actions. Run 1 used a screen observation with typing, so the refusal is the designed behavior, not a failure.
3. Click coordinate math is exact. Zen at [2509,914] (log 22:49, hyprctl clients) plus window (120,60) = global (2629,974). Monitor eDP-2 at [2464,902] gives screen (165,72), matching the log. hyprctl cursorpos (2629,974) equals the target, 0 px error. Label "Muse via act-now" matches overlay.py _label_for (agent + " via " + method).
4. Navigation failure is correctly attributed to Zen, not act-now. Run 2 mouse click plus type plus Enter did not navigate; run 3 Ctrl+L plus type plus Enter loaded Example Domain (obs5 22:58:53 verifies urlbar "example.com", tab "Example Domain", page text); run 4 retest with a 500 ms wait after Ctrl+N also did not navigate. That is 2/2 mouse-click failures vs 1/1 keyboard success, with the wait variable controlled in run 4. Calling this a Zen urlbar behavior is the supported reading.
5. ZT-00 INCONCLUSIVE is honest as far as F2 knew it. Step 4 mouse path not satisfied as written, step 5 met only via the keyboard diagnostic, step 7 set check stated as unverifiable. The verdict does not claim step 4 passed.

## Finding 1 (biggest): tab accounting is wrong, F3 ran a cleanup mid-rehearsal

F2's log says at 22:53:39 "NO F3 process running... Coast clear; F3 has not started its re-run yet." F3's log shows cleanup_full.py launched 22:54:22, 43 s later, BEFORE 68 tabs, CLOSED 52, AFTER 16 tabs at 22:54:50. F3's live Marionette verify at 22:55:34 lists 17 tabs, and close3.py at 22:56:01 lists BEFORE 18, CLOSED 3 (Example Domain + 2 blanks), AFTER 15.

Consequences, each contradicting F2's log:

- F2 run 3 note "Tab count now 68 (67 baseline + 1 run tab, sessionstore 22:55 confirms 68)" is false against F3's live list of 17 tabs at 22:55:34. The sessionstore was stale (F2 admits it was dated 22:55 and not updated since) and must not have been used as a counter at all.
- F2's final "67 or 68 vs baseline 67 (at most 1 extra blank tab from run 4's Ctrl+N)" is false. The 67 baseline no longer existed after 22:54:50. The true live count near the end was 15 to 17 tabs per F3, and the run-4 tab fate is unknown, not bounded at 1.
- F2 run 5 close attribution "Closed my run-opened Example Domain tab" is not proven. F3's close3 had already closed the Example Domain tab at 22:56:01. The sidebar "Example Domain" row F2 saw in obs7 at 23:01:36 is the zombie F3 proved at 23:01:10 (clicking the row selects "New Tab" instead, the row has no browsing context, BiDi lists no example.com tab). F2's claim that the row "is F3's BASELINE tab (index 10, part of the 67), NOT mine" is therefore wrong: the baseline tab was already closed, and the row is a dead element. Run 5 Ctrl+W closed whatever tab was active at 23:01:21, which followed F3's 23:01:10 click that had selected New Tab, so run 5 may have closed the sacrificial New Tab, not an Example Domain tab. The close is verified only as "active tab became Welcome!", not as "my Example Domain tab closed."

Required change: correct the log and rule doc to state the rehearsal ran concurrently with F3's cleanup, retract "67 or 68" and the run-5 close attribution, and record the tab identities as confounded, not merely unverifiable.

## Finding 2: the 330 s baseline comparison is not apples to apples, and "first action in 333 ms" mislabels the metric

The ~330 s baseline (order 22:11:30 to first click 22:17) is end to end: it includes the agent's thinking, source reads, retries, and diagnosis before any command ran. The act-now numbers start at t0 inside first_action.py run(), after the agent already decided to call act-now and after a fresh observation was captured and viewed. The rehearsal itself proves this: T_order 22:45:15 (fresh observe) to run 1 at 22:53:57 is 522 s of pre-work (workspace hunting, observes, viewing, focus command), and T0 22:40:00 to run 1 is 837 s. So the rehearsal did NOT demonstrate order-to-first-visible-action under 30 s from a user order. It demonstrated command-start-to-overlay under 1 s. The rule doc sentence "That is the fix, measured" states the comparison without this scope caveat.

Second, order_to_action_start_ms is set in first_action.py before attempt_session(), so it measures session-attempt start, not the first pointer move. The first pointer move happens only after the session attempt fails and the fallback runs, and its time is not recorded separately. It is bounded by total batch time (0.87 to 2.0 s) but "first action in 333 ms" is not a measured value. Only order_to_overlay_ms (314 to 346 ms) is a true first-visible-action measurement.

Required change: in the log verdict and the rule doc Measurement section, state plainly that act-now timings start at command start, exclude agent decision and observation time, and that the under-30 s rule from user order is not yet demonstrated end to end. Rename or define order_to_action_start_ms as session-attempt start, and do not report it as first pointer movement.

## Finding 3: no raw envelope output is in the repo, so the numbers are self-transcribed, not independently verifiable

first_action.py appends each envelope to STATE/first-action-YYYYMMDD.jsonl on the laptop. That file is not in the repo (no STATE/ dir in the VM checkout) and no envelope JSON is pasted in the log or rule doc. The log and the rule doc agree with each other, but both were written by F2, so that agreement is one author twice, not two sources. The after-capture image ids are cited (594806e130f1, de010258f1fd, c35ef9025e45, 2155674040fa) but no image bytes are attached, so the pill claim cannot be re-checked from the repo.

Required change: attach the five envelope JSON objects (or the JSONL excerpt) to the log, and attach or cite a viewable after-capture for at least run 2, or mark the numbers explicitly as self-transcribed from laptop-only output pending that attachment.

## Finding 4: pill visible is proven for run 2 only, not for runs 3 to 5

The log states the pill "Muse via act-now" was VISIBLE in run 2's after-capture. For runs 3, 4, and 5 it records only order_to_overlay_ms and the after-capture id, with no visual statement. The mechanism is plausible: first_action.py takes the after-capture before the finally block releases the overlay, and indicator.py request() returns False with command_skipped when no session.json exists, so capture_clean does not hide the daemon-owned pill on the fallback path. But plausibility is not proof. For 3 of 4 OK runs the only evidence is the daemon's own reply visible True, which is self-report.

Required change: scope the visual pill claim to run 2, and record runs 3 to 5 as daemon-reported only until their after-captures are viewed and noted.

## Finding 5: Marionette re-break attribution points at F3's close3, not at act-now

F2's log suspects "the act-now Ctrl+N / new-tab navigation, or the eval session DELETE." The timeline in F3's log is tighter: the slot worked at 22:55:34 (F3 verify listed 17 tabs, AFTER F2 run 2 at 22:55:31), close3 ended about 22:56:05, and the slot failed at 22:56:12. F3's refined hypothesis (closing a window/new-created tab leaves a zombie tab element with null linkedBrowser) fits that window. On timing evidence the break follows F3's close3, not F2's run 2, so act-now is exonerated more strongly than F2 claims, and F2's self-suspicion is the weaker reading. Note the F3 hypothesis is still unproven (needs BiDi diagnosis), so this is a timing correction, not a root-cause verdict.

Required change: correct the log to state the break window as 22:56:05 to 22:56:12, after F3 close3, with the slot verified working after run 2, and remove or downgrade the act-now suspicion. This is not F2's fault.

## Finding 6: "act-now PROVEN" overclaims scope, session path never ran

All 4 OK runs took the fallback path because the session guardian failed every time. Zero runs exercised the session path. The fallback path is the proven part. The rule doc Limits section already admits the session-path envelope ok is the command exit code, not the action result. The log verdict should carry the same scope. Separately, nothing in the diff compels the agent to call act-now first: it adds a subcommand, it does not change the agent loop or prompt, so the R1 claim "speed is structural, not a decision" is partial. The code provides the fast path; using it first is still a decision until a caller enforces it.

Required change: scope the verdict to "fallback path proven; session path untested in this rehearsal" and note the default-use gap as a follow-up, not as a proven structural fix.

## Finding 7 (minor): click exactness is run-2-only with a 60 s gap

cursorpos (2629,974) was read at 22:56:33, about 60 s after run 2 finished (about 22:55:33). No pointer move is recorded in between, and F3 made no mouse click in that window (its clicks are 23:00:03, 23:01:10, 23:01:53), so the reading is consistent with the click landing there, but it is not contemporaneous. desktop_act's own 3 px pointer verification output is not quoted in the log. Run 4 has no cursorpos check at all. Scope "click landed exactly" to run 2 with the timing caveat.

## What must change before GO

1. Correct tab accounting (Finding 1): retract "67 or 68" and the run-5 close attribution, state the F3 concurrency and confounded identities.
2. Correct the baseline comparison and the action-start label (Finding 2): scope act-now timings to command start, state the under-30 s rule from user order is not yet demonstrated end to end.
3. Attach raw evidence or mark it as self-transcribed (Finding 3): five envelope JSONs and at least the run-2 after-capture.
4. Scope the pill claim to run 2 (Finding 4), the Marionette attribution to the close3 window (Finding 5), and "proven" to the fallback path only (Finding 6), plus the run-2-only click caveat (Finding 7).
5. No live re-run is required by this council. The fixes are record corrections in the log and rule doc, plus attaching laptop-only evidence. A fresh clean rehearsal with no concurrent worker on the same browser is recommended for the next live proof, so tab counts are meaningful again.

## Bottom line

The mechanism is real and the core numbers are internally consistent: overlay in 314 to 346 ms, fallback batches in 0.87 to 2.0 s, run 1 refusal correct, urlbar finding supported 2/2 vs 1/1, tests 21/21 re-run clean. The INCONCLUSIVE verdict on ZT-00 is honest in direction. But the record overstates what was proven: the baseline comparison mixes end-to-end time with command-internal time, the tab counts are contradicted by F3's live lists, and the only independently checkable numbers are F2's own transcriptions. AMEND, then GO on the corrected record.
