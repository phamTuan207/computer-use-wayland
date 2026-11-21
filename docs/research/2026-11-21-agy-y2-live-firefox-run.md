# agy-y2 suite: live run on real Firefox (batch 4, task 2)

- Date: 2026-11-21
- Runner: clone2 subagent, independent of the suite generator (Worker Y2)
- Headline result: 10/10 PASS, confirmed live. 179 WebDriver actions, 88 of 88
  ported checker assertions passed, 0 step failures, 0 check failures,
  integrity guard held on all 10 tests.
- Suite source: tests/realistic/agy-y2 on origin/todolist-push, extracted at
  tip 66e5e48a20775064098e34247e4ee3dec93f04c6. The suite content itself is
  commit 30a72e538c4e8b5fddc2bc1fbfe4bf1b1915012b, the state Y7 verified.

## Environment

- Machine: this VM, Linux 7.0.0-44-generic x86_64, headless (no display)
- Browser: Mozilla Firefox 160.0.1, headless, fresh profile per test
- Driver: geckodriver 0.37.1, Selenium 4.53.0 (Python venv)
- Fixtures: local file:// URLs from a scratch extraction at
  ~/workspace/tools/batch4/agy-y2-live (fixtures byte-identical to the branch)
- Run window (UTC): 2026-11-21T11:42:02Z to 2026-11-21T11:43:23Z, in two
  invocations (test 01 first as a smoke run, then tests 02 to 10). Each test
  ran in its own fresh Firefox session in both invocations.
- Runner and raw evidence: ~/workspace/tools/batch4/agy-y2-live/run_live.py,
  live_results.json (per-test records with final DOM state), live_steps.jsonl
  (per-step wall times).

## Method

The method follows the Y9 live-run plan (improvements/worker-y9-agy-y2-live-plan.md,
commit 6f20fb5) where it defines the run, adapted from its target environment
(the owner's Zen via Marionette, still queued behind Y4d and Y8) to real
Firefox via Selenium WebDriver on this VM, as tasked. This run does not
replace the Zen run Y9 owes; it is the Firefox live confirmation for batch 4.

- Steps follow simulate.mjs action for action: same selectors, same order,
  driven with real WebDriver interactions (element clicks, send_keys typing,
  Selenium Select for the two dropdowns).
- Spec step counts (32 to 35 per test) include observation and verify lines
  from the .md specs. The actions column below counts the WebDriver actions
  actually executed, which is the simulate.mjs action count for each test.
- Final state is verified by a 1:1 port of check.mjs verifyTest (same
  selectors, same expected values, including test-07 'Root: 5 files'),
  executed in the live page. The only change to the ported body is an added
  counter so the number of assertions run is reported.
- Y9 PASS threshold applied per test: zero step failures AND ported verify
  0 failures AND the integrity guard held. Guard: the ported verify must
  FAIL on the untouched fixture before any step runs; a pass on untouched
  would abort the test as a suite defect, never a pass.
- Y9 flagged-pass category (tz-hidden removal intervention on Zen) does not
  exist in this environment: clean passes 10, flagged passes 0,
  infra-blocked 0. The Y9 exit criterion, clean + flagged == 10, is met.

## Per-test results

| Test | Spec steps | Live actions | Checks passed/run | Guard failures on untouched | Elapsed (s) | Result |
| --- | --- | --- | --- | --- | --- | --- |
| 01 tmux session | 35 | 16 | 8/8 | 8 | 8.161 | PASS |
| 02 network settings | 35 | 17 | 11/11 | 10 | 5.739 | PASS |
| 03 photo editor | 33 | 15 | 11/11 | 9 | 4.931 | PASS |
| 04 email compose | 33 | 18 | 7/7 | 4 | 5.116 | PASS |
| 05 spreadsheet chart | 35 | 26 | 12/12 | 12 | 5.503 | PASS |
| 06 video call | 35 | 18 | 9/9 | 7 | 7.128 | PASS |
| 07 file manager | 35 | 22 | 8/8 | 6 | 6.188 | PASS |
| 08 devtools | 35 | 16 | 8/8 | 7 | 7.270 | PASS |
| 09 notes sync | 35 | 19 | 6/6 | 6 | 9.458 | PASS |
| 10 ide debug | 32 | 12 | 8/8 | 8 | 9.344 | PASS |
| Total | 343 | 179 | 88/88 | (guard held 10/10) | 68.838 | 10/10 PASS |

Elapsed is per-test wall time including browser start and both verify
passes. The guard column is the number of checker assertions that failed on
the untouched fixture; it is above zero for every test, so no assertion set
was trivially green.

## Y7 follow-up items, live outcome

Source: improvements/worker-y7-redteam.md, commit a07fd27 (redteam NO BLOCK).

1. Test-07 skip hole (redteam attack 1f, PROVEN there): skipping the delete
   and restore steps (spec steps 23 to 29) passes all 8 final checks because
   the two end states are DOM-identical. That is a checker-design gap, and
   the final verify alone cannot close it. In this live run the delete and
   restore steps were actually performed, and mid-run observations recorded
   at the moment prove it: after the delete click, the trash counter read
   '1' and the img4 row had the hidden class; after the restore click, the
   trash counter read '0' and the img4 row was visible again. So the hole
   did not touch this run's evidence. It remains open as a suite follow-up
   (needs a fixture restore marker or a mid-run checker assertion).
2. Test-09 rename-branch bypass (redteam attack 2c, PROVEN there, off-spec
   only): the save handler can delete the archived note without the delete
   button ever being clicked. This run followed the spec exactly and used
   the real delete button (#btn-delete-active-note); the rename branch was
   never used. Evidence the delete path ran: immediately after the delete,
   the editor title had fallen back to 'Personal Tasks' (the delete
   handler's fallback to the first remaining note, the exact signal the
   redteam suggested asserting), the total counter read '3', and the spec
   step 33 body check read the Shopping note body as
   'Milk, Eggs, Bread, Apples'. The bypass did not occur.
3. Test-07 Root count depends on the moved set excluding img4 (redteam
   attack 1d): heeded. The move set was exactly img1, img2, img3, and the
   ported checker verified the toast 'Root: 5 files, Archive: 3 files,
   Trash: 0 files, Folder Processed created'.
4. simulate.mjs --all aborts on the first crash (redteam attack 4a): does
   not apply here. Each test ran independently in a fresh session, and no
   test crashed.

## Script substitution record (complete)

No step in any test required script-driven input. Every action was a real
WebDriver interaction. The honest details:

- Field clears: simulate.mjs clears six fields with page.$eval (script):
  test-01 window name, test-05 cell B4 and chart title, test-09 note title
  (twice) and note body. The live run cleared the same fields with the
  WebDriver element.clear() command instead, then typed with send_keys.
  That is a real WebDriver interaction, not page script, and it is stricter
  than what the simulator itself does.
- Dropdowns: test-03 export format (PNG) and test-05 chart type (Bar) used
  Selenium's Select, which performs a real option selection through
  WebDriver. The Y9 Marionette plan had planned a JS value plus change
  event for these; none was needed here.
- Test-08 row click: simulate.mjs clicks the <tr> #row-req-api-checkout.
  Per the Y9 P rule (click a <td>, never a <tr>), the live run clicked the
  first <td> inside that row. Same handler path, recorded here as the one
  deliberate selector deviation from simulate.mjs.
- Script was used only to READ state, never to change it: the ported
  verifyTest (same as check.mjs's own page.evaluate) and the mid-run
  observations in tests 07, 09, and 10.
- Test-10 spec/fixture gap (from the Y9 plan, confirmed live): spec step 15
  names #input-edit-watch-total. That element exists in the fixture and its
  computed display is 'none' (observed live), so no pointer click can reach
  it. The live run followed the simulator path instead: click
  #btn-open-edit-watch, type 250 into #input-watch-override-value, confirm.
  The checker does not test the hidden input. Recorded as a known
  spec/fixture gap, not a run failure.

## Conclusion

10/10 confirmed live on real Firefox 160.0.1: all 10 tests pass with zero
step failures and zero check failures, and the integrity guard held on all
10 (the checker fails on every untouched fixture). The two Y7 follow-ups
that could have weakened a live result, the test-07 skip hole and the
test-09 bypass, were both neutralized for this run by following the spec
exactly and recording mid-run evidence; both remain valid suite follow-ups
for Y2 to fix in the checker and fixture. The Zen live run in the Y9 plan
is a separate, still-owed run and is not claimed here.
