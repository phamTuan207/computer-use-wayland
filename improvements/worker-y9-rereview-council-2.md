# Council Member 2 re-review verdict: Worker Y9 agy-y2 live-run runner (test fidelity only)

- Reviewer: Council Member 2 (re-review, test fidelity scope only)
- Runner under review: tests/realistic/run_agy_y2.py as committed in a82bb41
- Suite under review: tests/realistic/agy-y2/ specs test-01 through test-10, check.mjs, simulate.mjs
- Supporting docs: improvements/worker-y9-step-mapping.md, improvements/worker-y7-fix-log.md, improvements/worker-y9-council-2.md (first round)
- Date: 2026-11-21
- Method: read the runner code line by line against the spec files, check.mjs, simulate.mjs, and the fixture files. No live driving, no browser, no commits. The working tree copy of the runner is byte identical to a82bb41 (md5 1defa4ebf184c7e52df9604e75cd7f4b, both copies), so line numbers below cite the committed file.

## Verdict: GO WITH FIXES

The runner is faithful. Every spec step in all 10 tests is driven in order with the right selector and the right expected value, the ported verify matches check.mjs exactly, and every first-round Council 2 fix is present in code. Three minor fixes remain, all small, all in code or in the mapping table. No fix blocks the live run on fidelity grounds once applied, but Fix 1 and Fix 2 should land before launch because they are one-line tightenings, and Fix 3 should at least be recorded as an accepted weakening if the code is not changed.

## What was checked and found correct

### Ported verify is a 1:1 transcription of check.mjs

A mechanical extraction of every check() call from the runner _VERIFY_JS block (lines 584-841) and from check.mjs shows identical conditions, selectors, expected values, and order in all 10 tests: test 01, 8 checks; test 02, 11; test 03, 11; test 04, 7; test 05, 12; test 06, 9; test 07, 8; test 08, 8; test 09, 6; test 10, 8. Total 88 checks in both files. Note N1 below: the a82bb41 commit message says 87, the true count is 88. The port also preserves the two read-but-never-asserted values exactly as check.mjs does: test 01 terminalOutput and test 07 selectedCount are read into variables and never asserted in the port, matching check.mjs lines 51 and 216. Test 07 "Root: 5 files" is present in the port (line 187) and in check.mjs line 240.

### Per-test step fidelity

Test 01 (run_01, lines 1000-1089): all 35 steps in order. Step 2 initial checks, step 4 and 19 modal waits on class "open", step 20 rename via type_text (which clears first, run_live.py lines 516-521, so it equals the spec clear-and-type), steps 25-28 kill and undo with pane count and alert text checks, step 30 detached status plus d.visible on #session-overview (a real visibility proof, not the presence-only wait the simulator uses at line 68, M3 closed), step 31 "2 windows", step 33 reattached, step 34 save. Steps 13-14 use the scoped active-pane helpers _active_pane_type and _active_pane_click_send (lines 967-999) instead of the plain #pane-terminal-input and #btn-send-command selectors. This is a deliberate, justified deviation: the fixture creates duplicate ids per pane (fixture lines 215 and 219) and only the active pane content carries #pane-active-output (fixture lines 205-206), so scoping by closest('.pane') of #pane-active-output targets the right pane where a plain selector would take the first match in document order. One gap, see Finding F2 on step 35.

Test 02 (run_02, lines 1090-1191): all 35 steps in order, plus the unnumbered M1 apply action. Step 4 wifi enabled plus #wifi-content visible, step 6 auth modal wait, step 9 SSID and badge, step 11 known panel visible, step 13 CafeFree absent from DOM, steps 15-16 Bluetooth panel active and enabled, step 18 list visible plus MX Master present, step 20 paired badge "Paired", steps 21-25 Bluetooth off/on with persistence, step 28 properties panel wait, step 30 metered, step 31 save properties, steps 33-35 summary values. See Finding F3 on the containment wording of steps 18, 20, 25.

Test 03 (run_03, lines 1192-1267): all 33 steps in order. Steps 5-6 filename and 1200x900, steps 8-12 crop 4:3 to 1000x750, steps 14-16 Vivid, steps 18-22 brightness 0, 20, back to 0, steps 25-26 rotation 90 deg and 750x1000, step 28 export modal wait, step 29 PNG select via select_option (sets value plus change event, lines 202-210), step 30 format PNG. One gap, see Finding F1 on step 31.

Test 04 (run_04, lines 1268-1362): all 33 steps in order. Step 2 counters 12 and 0, step 4 compose pane wait, step 7 CC group visible, steps 15-16 chip present and counter 1, step 18 drafts 1, step 20 compose hidden, step 23 reopen with wait plus subject read (M10 closed, line 1324: d.value("#input-mail-subject") == "Q4 report"), steps 24-25 remove with counter 0 and empty list, steps 26-29 re-attach with counter 1 and chip, steps 31-33 hidden after send, toast, sent 13. See Finding F3 on steps 15 and 29.

Test 05 (run_05, lines 1363-1445): all 35 steps in order. Steps 3-9 data entry loop (exactly A1, B1, A2, B2, A3, B3, A4), step 10 mistake 9800, step 11 B4 check, steps 13-16 SUM formula to 12500, steps 18-21 AVERAGE to 4166.67, step 22 correction to 1800 via type_text (clears first, equivalent to the simulator $eval clear at simulate.mjs lines 204-206), step 23 recalculate, steps 24-25 totals 4500 and 1500.00, step 27 chart modal wait, step 28 Bar select (M14: performed, with a code comment noting no fixture handler reads the select value and no check asserts the chart type), step 29 render, step 30 SVG present, steps 31-33 title with the M12 wait, step 35 save toast. See M12 confirmation below.

Test 06 (run_06, lines 1446-1536): all 35 steps in order. Steps 6-7 connected, 4 participants, room name; steps 9 and 11 mic text plus class muted/active; steps 13 and 15 camera text plus class off/active; step 17 screenshare modal wait; step 20 banner text plus visible; step 22 banner hidden class; step 24 hand class plus text; step 26 chat sidebar open; step 29 chat message; step 31 disconnected plus rejoin panel visible; step 33 reconnected with 4; step 35 summary toast. No deviations.

Test 07 (run_07, lines 1537-1625): all 35 steps in order. Steps 3-7 select img1-5, step 8 selected count check, steps 9-14 bulk rename with name checks, steps 15-17 re-select exactly img1-3 (line 1570 loop, Y7 doubt 3 closed, with a warning comment that a Root 6 toast means the move set was wrong), steps 18-22 move with Archive "3 files", steps 23-28 delete and restore with the hole-closing checks, steps 29-33 back to root and create folder Processed, steps 34-35 inventory report with toast "Root: 5 files, Archive: 3 files, Trash: 0 files, Folder Processed created". See the intermediate checks section below.

Test 08 (run_08, lines 1626-1709): all 35 steps in order. Step 2 collapsed plus toggle text, step 4 expanded, steps 6-10 console view, log 0, eval window.appVersion, v2.4.1, log 1; steps 12-17 network view, total 6, filter api, visible 3, both rows visible; step 18 clicks the first td inside #row-req-api-checkout (line 1664) instead of the tr. This is a deliberate, justified deviation: the fixture attaches the handler to the tr itself (fixture line 273) and a td click bubbles to it, and the code comment cites that line. Steps 19-22 detail open, 404, response body; step 24 detail closed; steps 27-28 clear with log 0 and empty output; steps 29-31 re-eval to log 1; step 33 visible still 3; step 35 toast. No deviations beyond the justified td click.

Test 09 (run_09, lines 1710-1818): all 35 steps in order. Step 2 counters, step 4 untitled, steps 5-7 title Shopping and body "Milk, Eggs, Bread" then save, step 8 counter 3 and Shopping listed, step 10 read plus assert plus full retype (D6, M6), steps 11-12 stage A, steps 14-16 stage B with full conflicting body, steps 17-19 sync and conflict modal plus banner, steps 20-23 resolve keep both, modal closed, counter 4, conflict copy present, steps 24-28 open conflict copy, title read, rename to "Shopping - Phone Copy", save, title check, steps 29-31 select archived draft and delete with counter back to 3, step 32 view primary note, step 33 body check, steps 34-35 finalize and toast. See the Y7 doubts section below.

Test 10 (run_10, lines 1819-1906): all steps except the documented fixture gap. Steps 3-4 file load, steps 5-7 breakpoint 12 and count 1, steps 8-9 paused with calculateSum line 12, steps 10-14 step over to lines 13 and 14 with watch 120, step 15 handled as a gap (see below), steps 16-20 edit watch modal, override 250, watch 250, steps 21-27 breakpoint 16, count 2, continue to line 16, stack renderSummary, grand total 250, steps 28-32 stop, line None, save, toast. Step 18 uses type_text (clears first) where the simulator only types into an empty field (simulate.mjs line 389); clearing an empty field is harmless.

### Intermediate checks the mapping calls load-bearing are present as mid-run r.check calls

All five named checks are present, in order, mid-run, with the pinned expected values:

- Test 01 step 15: lines 1038-1040, r.check("uptime output has load average", "load average: 0.18, 0.22, 0.15" in output). This is the only coverage of the uptime output, since the ported final verify never asserts terminalOutput. First-round C2 Fix 3 closed.
- Test 07 step 8: line 1549, r.check("selected 5 files", #selected-files-count == "5"). Only coverage, since check.mjs line 216 reads the count but never asserts it. First-round C2 Fix 4 closed.
- Test 07 step 24: lines 1591-1594, r.check("row img4 hidden after delete", #file-row-img4 has class "hidden") and r.check("trash counter 1", #trash-counter == "1").
- Test 07 step 28: line 1602, r.check("trash counter 0 after restore", #trash-counter == "0"). Steps 24 and 28 together close the Y7 doubt 1 skip hole: skipping delete plus restore would still pass all 8 final checks, but it cannot pass these two mid-run checks. First-round C2 Fix 4 closed.
- Test 09 step 33: lines 1806-1808, r.check("primary body has Apples", "Milk, Eggs, Bread, Apples" in body value). Only coverage of any note body, since check.mjs test 09 never reads a body value. First-round C2 Fix 4 closed.

A failed r.check appends to the runner failures list (base Runner.check, run_live.py lines 584-590) and the summary pass flag requires zero failures, so these mid-run checks are PASS-gating even though execution continues past them.

### Y7 doubts are heeded

- Doubt 1, test 07 skip hole: closed by the step 24 and step 28 intermediate checks above, not by a fixture change. Confirmed in code.
- Doubt 2, test 09 rename-branch bypass: the precise rule is stated in a code comment at lines 1728-1731, "never save titled 'Shopping' while the ARCHIVED note is active", and the code obeys it. The step 7 save uses title Shopping while the active note is the fresh generated key, so the rename branch fires and creates the 'shopping' key (fixture lines 181-186), proven by the step 8 check on #note-item-title-shopping. After step 29 selects the archived draft, the only action is the delete click; no save ever runs while the archived note is active. Step 27 saves with title "Shopping - Phone Copy", which is not exactly "Shopping", so the rename branch cannot fire there. The step 33 body check is the bypass detector. Closed.
- Doubt 3, test 07 move set: the move loop at line 1570 selects exactly img1, img2, img3, never img4, with a warning comment that a Root 6 toast means the move set was wrong. The delete target at step 23 is img4, which is outside the moved set, as the spec requires. Closed.
- Doubt 4, per-test independence: main() (lines 2265-2517) wraps each test in try/except with a fresh Y9Runner per attempt, and open_fixture (lines 853-943) clears storage and reloads the fixture per test. A live step failure fails that test and the suite continues to the next test; only the two-consecutive-INFRA rule and the separate two-consecutive-session-creation-failure rule abort the suite. The first-round C2 Fix 5 and Fix 6 behaviors are in code: session-creation failures increment their own wd_failures counter and abort at 2, and a 30 s Marionette timeout is reclassified INFRA unless it is a wait_for timeout. First-round C2 Fix 7 is also in code: the integrity guard runs through the same ported verify as the final verify, after the fresh load and before any action, per test, records the untouched failure list, is re-executed on any re-run, and a guard pass fails that test as a suite defect while the suite continues.

### M1 and M12 confirmed in code

- M1: test 02 applies the network settings even though the spec has no step for it. Line 1179 clicks #btn-apply-network-settings after the step 35 summary checks, matching simulate.mjs line 107 and the order in the mapping table. The apply toast is then checked mid-run (class "active" plus text "Network settings applied successfully") and again in the final verify (check.mjs lines 96-97). Present.
- M12: test 05 waits for the chart title controls before touching the title input. Lines 1421-1426 wait for computed display of #chart-title-controls to be not "none", then line 1428 clicks #input-chart-title and the next step types the title. This matches the fixture: #chart-title-controls is display:none (fixture line 136) until the render handler sets it to block (fixture line 281). A click before render would hit a hidden input. Present.

### First-round Council 2 fixes, closure check

Fix 1 (runner exists, step mapping, verify diff): closed. The runner exists, the mapping table covers all 10 tests, and this review performed the verify diff mechanically: 88 of 88 checks identical. Fix 2 (test 10 step 15 as a gap, never a step success): closed. Lines 1853-1858 record it with r.gap, which logs a gap-probe line, appends to the gaps list, and never counts as a driven step; the string #input-edit-watch-total appears nowhere else in the runner and no click_js call targets it. The fixture confirms the gap: the input is display:none (fixture line 114) and no other fixture line references that id. Fix 3 (test 01 step 15 pinned): closed, see above. Fix 4 (hole-closing checks named and pinned): closed, see above. Fix 5 (per-test independence): closed, see above. Fix 6 (INFRA counter and hang classification): closed, see above. Fix 7 (integrity guard procedure): closed, see above. Fix 8a (test 09 step 10 read assert): closed, line 1743 asserts the read body equals "Milk, Eggs, Bread" before typing the full text. Fix 8b (test 08 td-click justification): closed, the code comment at lines 1661-1663 cites the fixture tr handler line. Fix 8d (flagged still requires all PASS conditions): closed, main() counts a flagged pass only when the summary pass flag is true, which requires zero failures. Fix 8c and 8e are plan-text items, outside runner scope, not re-litigated here.

### Other confirmations

- The runner contains no banned driver calls (grep, zero hits).
- No em dash or en dash appears in this verdict file.

## Findings

### F1 (minor): test 03 step 31 checks contains "750 x 1000", not the spec exact value "750 x 1000 px"

- Spec test-03-photo-editor.md step 31 requires #dialog-dimensions-display text to be "750 x 1000 px".
- Runner line 1256 checks "750 x 1000" in the display text, without the " px" suffix and without equality. The ported final verify does the same (check.mjs line 127 is also contains "750 x 1000").
- The mapping table row for step 31 claims r.check("dialog-dims", #dialog-dimensions-display == "750 x 1000 px"), so the code is weaker than its own mapping row, not just weaker than the spec.
- The mapping already records this as M5 and notes step 26 (dims 750 and 1000) carries the real proof, so this is a known weak spot, not a new hole. Still, the exact value is cheap to assert: the fixture refreshes the dialog dims from live width and height when the modal opens, so exact equality should hold on a correct run.

### F2 (minor): test 01 step 35 has no mid-run r.check, the mapping table says it does

- Mapping table test 01 step 35 claims r.check("saved-message", #saved-status-message contains "Session deploy saved with 2 windows").
- Runner lines 1085-1087 click #btn-save-session-state and go straight to final_verify. There is no standalone saved-message r.check in run_01.
- Coverage is complete anyway: the ported final verify asserts both the saved message class "visible" and the text contains "Session deploy saved with 2 windows" (check.mjs lines 65-66, ported at lines 29-30 of the verify block), and it runs immediately after the save click. So this is a mapping-versus-code mismatch, not a missing assertion. Either add the mid-run check or correct the mapping row.

### F3 (minor): seven "contains / present in" spec checks are reduced to id-presence checks in the whole DOM

- Spec wording says a parent contains a child, but the runner asserts the child id exists or its count is 1, without scoping to the parent. Sites: test 02 step 18 (#available-bt-list contains #bt-device-mx-master, runner lines 1130-1133), test 02 step 20 (#paired-bt-list contains #paired-item-mx-master with badge "Paired", runner lines 1137-1140), test 02 step 25 (#paired-item-mx-master remains present in #paired-bt-list, runner lines 1155-1157), test 04 step 15 (#attached-files-list contains #attachment-chip-report, runner lines 1300-1302), test 04 step 29 (chip present again, runner lines 1348-1350), test 05 step 30 (#chart-wrapper contains #sales-bar-svg, runner line 1419), test 07 step 26 (#trash-table contains #trash-row-img4, runner lines 1597-1600).
- Practical risk is low: each child id is unique in its fixture and the fixture only renders that child inside the named parent, so presence implies containment on these fixtures. The mapping table repeats the spec "contains" wording for these rows, so the code is weaker than the mapping states. This is one pattern in seven places, not seven separate problems.

## Notes (not fixes)

- N1: the a82bb41 commit message says the ported verify has 87 assertions. The mechanical count is 88 in both check.mjs and the port (8, 11, 11, 7, 12, 9, 8, 8, 6, 8). The count in the commit message is off by one; the transcription itself is exact.
- N2: deliberate deviations from the literal spec selectors, both justified and both documented in code: test 01 steps 13-14 use active-pane scoping instead of plain duplicate ids, and test 08 step 18 clicks the first td instead of the tr. Neither is a fidelity loss.
- N3: wherever the mapping says clear_and_type (test 01 step 20, test 05 steps 22 and 31, test 09 steps 5, 14, 26, test 10 step 18), the runner uses type_text. These are equivalent because run_live.py type_text clears the element before typing (lines 516-521). Test 09 step 10 is the exception by design: it reads first, asserts, then types the full text, because type_text clears and a plain append would not work.
- N4: this review is code-only. Whether Marionette key events update the fixture state the same way puppeteer typing does (for example, typing into #cell-input-b4 updating #cell-value-b4) is a live-run question, not a code-fidelity question, and it is not decided here.

## Required fixes (numbered)

1. Test 03 step 31: tighten runner line 1256 to exact equality with "750 x 1000 px", matching the spec text and the mapping table row. If exact equality proves flaky in the live run for a documented fixture reason, correct the mapping row to the contains check instead and record why. Do one or the other, do not leave code and mapping disagreeing.
2. Test 01 step 35: add a mid-run r.check after the save click asserting #saved-status-message contains "Session deploy saved with 2 windows", matching the mapping table row, or correct the mapping row to state that step 35 is covered by the final verify only.
3. Containment checks: tighten the seven sites in F3 to parent-scoped queries (for example, count the child inside the named parent element) so the code asserts what the spec says, or record in the mapping table that id-presence is the accepted check at each site with the justification that each child id is unique and only rendered inside that parent. One recorded decision covering all seven sites is enough.

## Verdict restated

GO WITH FIXES. Apply fixes 1 to 3, then the runner is cleared for the live run on test fidelity. No blocker was found: every spec step is driven in order, every load-bearing intermediate check is present as a PASS-gating r.check, the Y7 doubts are heeded in code, M1 and M12 are present, the ported verify matches check.mjs 88 for 88, and the first-round Council 2 fixes are all closed in code.
