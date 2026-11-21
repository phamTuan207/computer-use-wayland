# Council Member 3 verdict: Worker Y7 fixes, verification integrity (agy-y2 suite)

- Council member: 3 (verification integrity)
- Date: 2026-11-21 ~18:30 +07
- Scope: tests/realistic/agy-y2/ (check.mjs, simulate.mjs, 10 specs, 10 fixtures)
- Basis: improvements/worker-y2b-verification.md (full report, including minor findings and method), improvements/worker-y7-fix-log.md, direct reads of check.mjs, simulate.mjs, test-07 and test-09 specs and fixtures, plus targeted reads of test-01, test-02 and test-10 specs and fixtures.
- Role limits: I read, traced and judged only. I edited no suite file. I ran no live simulation on the VM (no Chromium binary exists here: `which chromium` returns nothing, node v24.22.1 only). My verdict is a static trace verdict grounded in Y2b's live evidence (laptop runs 18:10-18:25 +07) plus Y7's log. The laptop live re-run of `simulate.mjs --all` is still owed and is a condition of this verdict, not a step I completed.

## Correction to the record (material to the test-09 debate)

Y2b's Defect 2 premise is stale. Y2b wrote that renderList() rebuilds items as `note-item-` + key, so `#note-item-archived-draft` never exists at runtime, and that the checker assertion `check(!archivedItem, ...)` is VACUOUS. That was true of the fixture Y2b ran against. It is no longer true of the fixture in the tree: Y2 applied its own fix after Y2b's run, and fixtures/test-09-notes-sync.html:142 now reads `div.id = 'note-item-' + (k === 'shopping_conflict' ? 'conflict-copy' : (k === 'archived' ? 'archived-draft' : k))`. The key `archived` is explicitly mapped to `archived-draft`, so `#note-item-archived-draft` DOES exist at runtime after renderList() runs at load (fixtures/test-09-notes-sync.html:275). Y7's fix log confirms this (improvements/worker-y7-fix-log.md, Defect 2 CONFLICT note). Consequence: in the current tree the absence assertion is NOT vacuous, because the element exists on a fresh fixture and only disappears after a real delete of the `archived` key. Y2b's "vacuous" label applies only to the pre-edit fixture and to the mixed state described below, not to the current tree. Council 2's direction choice must be made against this corrected fact, not against Y2b's stale premise.

## Question 1: integrity guard after both fixes

The guard is simulate.mjs, function simulateOne: it calls verifyTest on the untouched fixture and throws unless the check FAILS (simulate.mjs, untouched check block), then drives the steps, then calls verifyTest again. A test can only pass by failing first and passing after. I traced both tests assertion by assertion below.

### Test-07 (fix already present in the tree)

Fix status verified in the tree: check.mjs:240 expects `Root: 5 files, Archive: 3 files, Trash: 0 files, Folder Processed created`, and test-07-file-manager.md step 35 (line 58) expects the same string. The fixture is untouched.

Fresh fixture trace (guard must fail):
- Names: `#file-name-img1` is `raw_001.jpg` in the static fixture, so check.mjs:219-220 values fail the `photo-2026-01.jpg` / `photo-2026-05.jpg` assertions.
- Archive: `#folder-count-archive` starts at `0 files`, so the `3 files` assertion fails.
- Toast: `#inventory-summary-toast` is empty and lacks class `active` until the report button is clicked, so check.mjs:239 (isToastActive) and check.mjs:240 (toast text) both fail.
- Trash `0` (check.mjs:217) and row img4 visible would pass on a fresh fixture, but the guard is whole-check pass/fail, so the check fails overall. Guard holds.

Post-steps trace (guard must pass only after the driven steps):
- simulate.mjs test-07 block (line 262): select img1-5, bulk rename with pattern `photo-2026-##` (names become photo-2026-01 to 05), re-select img1-3 and move to Archive (rows hidden, archive count `3 files`), delete img4 (row hidden, trash 1), restore img4 from Trash (row visible, trash 0), create folder `Processed` (`#folder-item-processed`, check.mjs:223 and 238), generate the inventory report.
- Toast computation, fixtures/test-07-file-manager.html:332-334: `rootVisible` counts `#table-root-files tbody tr:not(.hidden)`. Count at report time: 8 rows start, minus 3 moved to Archive, minus 1 deleted, plus 1 restored = 5 visible (img4, img5, doc1, doc2, doc3). Archive length 3, trash length 0. The produced toast is exactly `Root: 5 files, Archive: 3 files, Trash: 0 files, Folder Processed created`, matching check.mjs:240 and spec step 35. The old value `Root: 3 files` matched no reachable state (8 minus 3 moved is 5, not 3). The fix corrects the expectation to the fixture's computed value; it does not weaken any assertion. Guard holds: the check fails fresh and passes only after the full driven sequence.

### Test-09 (direction still open; traced under both directions)

Direction A (Y2b's direction): revert fixtures/test-09-notes-sync.html:142 to plain `div.id = 'note-item-' + key`, rename all three references to `#note-item-archived` (spec test-09-notes-sync.md step 29 line 52, simulate.mjs step 6 line 364, check.mjs lines 273 and 285), and keep the counter assertion (already present, check.mjs:282, `totalNotes === '3'`).
- Fresh fixture under A: renderList creates `#note-item-personal` and `#note-item-archived`. The checker reads total `2` (fails check.mjs:282), titleShopping and titleConflict are undefined (fail check.mjs:283-284), `#note-item-archived` exists so `!archivedItem` fails (check.mjs:285), toast inactive (fails check.mjs:286-287). Guard holds.
- Post-steps under A: create Shopping (new key renamed to `shopping` on save), stage Device A and B, sync keep-both (adds `shopping_conflict`, total 4), rename conflict copy to `Shopping - Phone Copy`, click `#note-item-archived` (exists), delete it (fixtures/test-09-notes-sync.html:255-265 deletes `notesState.notes[activeId]` and re-renders; total drops 4 to 3), click `#note-item-title-shopping`, finalize. Final state: total `3`, both titles present, archived absent, toast active with total 3. All checks pass. Guard holds.
- Note: under A the static HTML id at fixtures/test-09-notes-sync.html:66 (`note-item-archived-draft`) is irrelevant in both states, because renderList() wipes `#notes-list-container` innerHTML at load and rebuilds it.

Direction B (keep Y2's fixture edit): fixtures/test-09-notes-sync.html:142 stays as the ternary, and all three references stay `#note-item-archived-draft` (current tree state).
- Fresh fixture under B: renderList maps `archived` to `archived-draft`, so the element exists; total `2` fails, titles fail, `!archivedItem` fails, toast fails. Guard holds, by the identical trace with the id spelled `archived-draft`.
- Post-steps under B: identical trace to A, with step 6 clicking `#note-item-archived-draft`, which exists at that point (notes still contain `personal`, `archived`, `shopping`, `shopping_conflict` after keep-both). Delete removes the `archived` key, the element disappears, total 3. All checks pass. Guard holds.
- Direction B needs no checker change at all: the `!archivedItem` assertion plus the total assertion (check.mjs:282 and 285) already satisfy Y2b's "assert absence PLUS counter" requirement.

Conclusion on Question 1: both fixes preserve the integrity guard under EITHER direction, provided the direction is applied consistently. The one state that breaks integrity is the MIXED state: rename the three references to `#note-item-archived` while leaving the fixture ternary at line 142 in place. In that state `#note-item-archived` never exists anywhere, simulate.mjs step 6 crashes with no element found (the same exit 3 crash Y2b saw, for the opposite reason), and the checker assertion `!archivedItem` passes vacuously on a fresh fixture and after any run, including a run where the delete never happened. The mixed state must never be committed. Fixture line 142 and the three references change together, atomically, in whichever direction Council 2 picks.

## Question 2: any remaining way for test-07 or test-09 to pass without doing the work

Per-assertion audit. No vacuous assertion remains under either consistent direction. Two hard-coded toast clauses need naming, because they look stronger than they are, but the combined assertions close both gaps.

Test-07 (check.mjs lines 217-240):
- Names (photo-2026-01, photo-2026-05): only the bulk-rename handler writes these values, and only for selected files. Cannot match on a fresh fixture (`raw_001.jpg`). Not vacuous.
- Archive `3 files`: only the move handler increments the archive list, and only for selected rows. Fresh value is `0 files`. Not vacuous.
- Trash `0`: passes on a fresh fixture, but it is a conjunct, not the whole check; it only passes post-steps if the deleted file was actually restored. Not a hole on its own.
- Row img4 visible: passes fresh, but post-steps it only passes if the restore step ran (the delete step hides it). Conjunct only.
- Folder `#folder-item-processed` exists (check.mjs:238): only the create-folder handler creates this id, with the typed name lowercased. Fresh fixture has no such element. Not vacuous.
- Toast (check.mjs:239-240): the toast is written only by the report-button handler (fixtures/test-07-file-manager.html:332-334). `Root: 5 files` requires exactly 5 visible rows at report time. Shortcut audit: move 3 files then report immediately yields the same toast text (Root 5, Archive 3, Trash 0), BUT the run still fails on names (no rename done) and on the folder check (no folder created). Move a different 3 files: archive still 3 and root still 5, but names fail unless the renamed files are img1 and img5, which forces the rename step. Delete-without-restore: trash 1 fails and root 4 fails the toast. There is no shortcut path through all 8 assertions. One honest weakness: the toast's final clause `Folder Processed created` is a literal string in the handler, not a state proof; folder creation is proven only by the separate `#folder-item-processed` check (check.mjs:238). That separation is correct as written, and I verified the separate check exists. No fix needed.

Test-09 (check.mjs lines 270-287, under either consistent direction):
- Total `3` (check.mjs:282): fresh value is `2`, so it fails fresh. Weak alone: creating Shopping alone also yields 3 (personal, archived, shopping) without any sync or delete. But it is a conjunct; the other assertions discriminate. Not a hole in combination.
- Title `Shopping` (check.mjs:283): element `#note-item-title-shopping` does not exist on a fresh fixture (renderList builds title ids from note keys; only `personal` and `archived` exist). It exists only after the create-and-save-as-Shopping flow. Not vacuous.
- Title `Shopping - Phone Copy` (check.mjs:284): element `#note-item-title-conflict` exists only after keep-both creates `shopping_conflict`, and its text is `Shopping - Phone Copy` only after the rename step (without the rename it reads `Shopping (Conflict Copy)`). Not vacuous.
- Absence of the archived note (check.mjs:285): non-vacuous under both consistent directions, because the element exists on a fresh fixture (direction A: `#note-item-archived` built from key `archived`; direction B: `#note-item-archived-draft` built by the ternary at fixture line 142). This assertion is the sole discriminator for the delete target, and it works: deleting the wrong note instead of the archived one leaves the archived element present and fails the check, while total would still read `3`. Worked example: delete the conflict copy instead of the archived note and the final state is personal, archived, shopping (total 3, titles pass, toast passes) but `!archivedItem` fails. That is exactly why the mixed state (where this assertion goes vacuous) is disqualifying.
- Toast active plus text (check.mjs:286-287): the finalize handler (fixtures/test-09-notes-sync.html:268-274) interpolates only the total; the clause `Shopping and Shopping - Phone Copy verified` is a literal string. So the toast proves the finalize button was clicked and the total is 3, not that the two titles are correct. The titles are proven only by the separate title assertions (check.mjs:283-284), which exist. Same pattern as test-07's folder clause, correctly covered by separate checks. No fix needed.
- No `__verify`, `__agyVerify` or `__fcckVerify` hooks exist in the suite: my grep across check.mjs, simulate.mjs and all fixtures returned zero matches except the ban text in tests/realistic/agy-y2/README.md:19, which states the hook is forbidden. check.mjs reads raw DOM with expected values hard-coded in the checker. Confirmed independently of Y2b.

## Question 3: Y2b's minor findings, one verdict each

### (a) Test-01 duplicate dynamic ids, plus spec step 15 with no checker coverage

- Duplicate ids confirmed: fixtures/test-01-tmux-session.html:215 (`input.id = 'pane-terminal-input'`) and :219 (`sendBtn.id = 'btn-send-command'`) sit inside `win.panes.forEach`, so every pane gets its own copy of both ids. Invalid HTML, and Puppeteer `page.click` acts on the first match in document order.
- Verdict: DOCUMENTED LIMITATION, does not block the independent live run.
- Reasoning: the checker never queries either duplicated id. It reads `#active-session-name`, `#window-count`, `#pane-count`, tab ids, `#saved-status-message`, and `.pane-content` text (check.mjs test-01 branch, including line 51). The duplicate ids therefore cannot cause a false pass in the checker. The simulator passed live (Y2b: 289 ms, 0 failures), and the human live run clicks visible buttons, where duplicate ids are invisible. The only exposure is automated driving if the active pane is ever not the first pane, and the live evidence shows the current flow does not hit it. Fix later by suffixing the ids per pane; do not hold the suite for it.
- Spec step 15 coverage gap confirmed: test-01-tmux-session.md step 15 (line 40) verifies `#pane-active-output` contains `load average: 0.18, 0.22, 0.15`. The fixture does emit that exact string (fixtures/test-01-tmux-session.html:225-226, `uptime` branch). But check.mjs:51 computes `terminalOutput` from `.pane-content` and no check in the test-01 branch ever asserts on it, and `#pane-active-output` is never queried in check.mjs at all. A run that skips typing `uptime` still passes all 8 test-01 checks.
- Verdict on the coverage gap: DOCUMENTED LIMITATION, does not block the independent live run.
- Reasoning: checkers in this suite assert end state, not every intermediate observation; the same is true of intermediate verify steps in the other tests (for example test-02's Bluetooth off/on toggle leaves no end-state trace either, since Bluetooth starts `Enabled`, fixtures/test-02-network-settings.html:133). The test-01 core work, session create, splits, window rename, kill/undo pane, detach/reattach, save, is fully asserted by the 8 checks. The uptime typing produces no state any other check depends on. The human live runner follows the spec and will type it. Cheap hardening for after GO, not a gate: add one assertion on the already-computed `terminalOutput` for the load-average string.

### (b) Test-02 has no explicit "Simulate mistake" step

- Confirmed: test-02-network-settings.md contains no step labelled as a mistake (grep for mistake/wrong returns only the context line 22 describing the Bluetooth off/on toggle and the fail criteria). The other 9 specs each carry one labelled mistake step. The Bluetooth off/on toggle (simulate.mjs test-02 block, step 5) plays the mistake/recovery role in substance: toggle off, toggle back on, end state `Enabled`.
- Verdict: DOCUMENTED LIMITATION, does not block the independent live run.
- Reasoning: no checker assertion depends on a mistake having occurred, so nothing is vacuous and no false pass is possible through this gap. The pattern deviation is cosmetic. The substantive work, Wi-Fi connect to HomeFiber-5G, forget CafeFree, pair MX Master 3S, metered connection, apply, is all asserted in the test-02 checker branch. Inventing a labelled mistake step now would require fixture, simulator and checker changes for zero integrity gain.

### (c) Test-10 simulator skips spec step 15 (click #input-edit-watch-total)

- Confirmed: test-10-ide-debug.md step 15 says click input `#input-edit-watch-total` to focus the watch editor. The simulator test-10 block (simulate.mjs, line 372 onward) goes from verifying `#watch-val-total` is `120` straight to `#btn-open-edit-watch` and the modal override, with no step-15 click. Y2b's live run still passed (240 ms, 0 failures).
- The skip is CORRECT, not a gap to fill: fixtures/test-10-ide-debug.html:114 defines that input with `style="display: none;"`. A `display: none` element has no click target for a human in Zen or for Puppeteer; adding the click to the simulator would crash it. Step 15 also has no state effect (focus only); the actual override happens in spec steps 16-19 via the modal, and the checker asserts the result (`#watch-val-total` `250`, `#watch-val-grand-total` `250`, toast with `total=250`). The end state is fully verified with or without step 15.
- Verdict: DOCUMENTED LIMITATION, does not block the independent live run.
- Reasoning: the skipped step is unexecutable as written and state-free, so skipping it changes nothing observable. Recommended cleanup after GO, not a gate: delete or annotate spec step 15 (never add the click to the simulator). The spec author should also note that a human runner who tries step 15 literally will find no visible input; the step as written is dead text.

## Verdict: CONDITIONAL GO

GO, subject to two conditions, after which the suite is ready for the independent live run on Zen:

1. Test-09 is landed in ONE consistent direction, never mixed. Direction A (revert fixture line 142, rename spec step 29, simulate.mjs step 6 and check.mjs lines 273 and 285 to `#note-item-archived`) or direction B (keep fixture line 142 and all three references as `#note-item-archived-draft`, which is the current tree state and needs no suite change for test-09). Either direction preserves the integrity guard and the non-vacuous delete assertion, as traced above. The mixed state, renamed references with the fixture ternary left in place, is a NO-GO state: simulator crash plus a vacuous delete assertion.
2. The laptop live re-run `node tests/realistic/agy-y2/simulate.mjs --all` returns 10/10 with the untouched-fixture guard failing first for each test. This is still owed. Y2b's 8/10 was on the pre-fix tree, Y2's own re-run was still pending at the time of Y7's log, and I could not run it on the VM (no Chromium). Test-07's fix is already present in the tree (check.mjs:240, spec line 58), so condition 2 is the remaining proof for it; test-09's proof depends on which direction Council 2 picks.

If condition 1 is violated (mixed state) or condition 2 fails, the verdict flips to NO-GO with the exact additional fix being: make fixture line 142 and the three references agree, then re-run until 10/10.

## Post-GO hardening (recommendations, NOT gates)

- Test-01: add one checker assertion on the already-computed `terminalOutput` (check.mjs:51) for `load average: 0.18, 0.22, 0.15`, closing the step-15 coverage gap.
- Test-01: give each pane's terminal input and send button a unique id (suffix by pane index) in fixtures/test-01-tmux-session.html:215 and :219, removing the duplicate-id fragility.
- Test-10: delete or annotate spec step 15 (unclickable `display: none` input, fixtures/test-10-ide-debug.html:114).
- Test-02: optionally label the Bluetooth off/on toggle as the mistake step in the spec for pattern consistency; no code change needed.
- Record the test-09 correction in the Y7 fix log: Y2b's "id never exists" and "vacuous assertion" claims describe the pre-edit fixture, not the current tree.
