# Worker Y7 redteam: attack both fixes (test-07 count, test-09 id)

- Redteam: independent Muse, reporting to Worker Y7 (coordinator)
- Date: 2026-11-21 ~18:35 +07
- Scope: tests/realistic/agy-y2/, defects 1 and 2 from improvements/worker-y2b-verification.md
- Rules kept: no suite file edited (fixture, check.mjs, simulate.mjs, spec untouched by this redteam), no ydotool, no em dash or en dash in this file, no personal info.
- Verdicts below are per attack: PROVEN (with file + line + exact failing scenario) or REFUTED (with reasoning).

## State under attack (verified first, not assumed)

- Test-07 fix is already present in the tree AND committed. check.mjs:240 and test-07-file-manager.md step 35 (line 58) both read 'Root: 5 files, Archive: 3 files, Trash: 0 files, Folder Processed created'. Grep finds no 'Root: 3' anywhere in tests/realistic/agy-y2/. All six files I attacked (check.mjs, simulate.mjs, both fixtures, both specs) are byte-identical to commit 30a72e5 on origin/todolist-push (verified by diffing each worktree file against `git show origin/todolist-push:<path>`). Y2 committed and pushed 30a72e5; the local branch HEAD is still behind origin, but the worktree content is the committed content.
- Test-09 current tree state is direction B (keep Y2's fixture edit). fixtures/test-09-notes-sync.html:142 maps key 'archived' to id 'archived-draft'; the three references are unchanged (spec step 29 line 52, simulate.mjs:364, check.mjs:273 and :285). Direction A (rename to 'note-item-archived' + revert fixture line 142) is a proposal, not yet applied. No council-2 direction file exists yet in improvements/ (only council-1 and council-3 were found).
- Method limit: the VM cannot run the simulator (no chromium binary, no puppeteer-core installed; `node -e require.resolve('puppeteer-core')` fails). All verdicts below are code-trace verdicts, plus primary-log evidence read from the laptop via ssh-laptop.sh. I ran no fresh simulation myself.
- Primary-log evidence (laptop /tmp, read directly):
  - /tmp/y2-sim3.log (Y2 re-run 3, current tree): allPassed true, count 10, ten `"passed": true` entries. Tests 07 and 09 both show `untouchedFailedAsExpected: true`, `passed: true`, `failures: []` (07 in 443 ms, 09 in 360 ms).
  - /tmp/y2-check3.log (fresh fixtures, current tree): allPassed false, ten `"passed": false` entries. The checker fails all 10 on untouched fixtures.
  - /tmp/y2b-sim-07.log (Y2b live run, pre-fix tree): toast text 'Root: 5 files, Archive: 3 files, Trash: 0 files, Folder Processed created'. Confirms Y2b's defect 1 live evidence.
  - /tmp/y2b-sim-09.log (Y2b live run, pre-edit fixture): 'No element found for selector: #note-item-archived-draft'. Confirms Y2b's defect 2 crash on the fixture as Y2b saw it.

## Attack 1: test-07, is '5' REALLY the right number

### 1a. Spec-path determinism: REFUTED (5 is forced on the spec path)

Trace from fixtures/test-07-file-manager.html. 8 tbody rows (img1-5, doc1-3). Rename handler (line 233) renames selected img1-5 then clears the selection, so the move step re-selects exactly img1-3 per spec steps 15-17. Move handler (lines 259-271) hides rows img1-3 and pushes 3 ids to state.archive. Delete handler (line 275) hides file-row-img4 and pushes 'img4' to state.trash. Restore handler (lines 289-294) filters 'img4' out of trash and unhides file-row-img4. Toast handler (lines 331-334) counts `#table-root-files tbody tr:not(.hidden)` at click time: 8 - 3 moved - 1 deleted + 1 restored = 5 visible (img4, img5, doc1, doc2, doc3). Archive is state.archive.length = 3, Trash is state.trash.length = 0. The live toast in /tmp/y2b-sim-07.log matches exactly. The old value 3 matches no reachable state on this path.

### 1b. Timing / race: REFUTED (no async exists to race)

Grep for setTimeout, setInterval, requestAnimationFrame, fetch(, XMLHttpRequest across both fixtures returns zero matches. Every handler in the test-07 fixture (rename 233, move 259, delete 275, restore 289, toast 331) is synchronous DOM mutation; class changes apply immediately, and the toast text is computed synchronously inside the report click handler (lines 332-334). There is no animation and no delayed update to settle. A runner reading the toast after clicking the report button always reads the final text. The spec's "stale observation" error (reading the count before the move settles) cannot trigger as a timing fault in this fixture; the only way to read a wrong count is to click the report button at the wrong step, and a later click at step 34 overwrites the toast. The toast is also idempotent: clicking report twice recomputes the same text from the same state.

### 1c. Restore before delete: REFUTED (fails loudly, prints no wrong count)

The restore button #btn-restore-file-img4 is created only inside the delete handler (fixture line 286, inside the line 275 handler). Before any delete it does not exist in the DOM, so neither Puppeteer (simulate.mjs) nor a coordinate click in Zen can press it. There is no silent wrong-count path here; the step errors out instead.

### 1d. Move selects different files: PROVEN, conditional (Root becomes 6 when img4 is in the moved set)

This is the real dependency, and it is on SELECTION, not on timing. General formula from the handlers: Root = 8 - M + I, where M is the number of files moved and I is 1 if img4 was among the moved files, else 0. The I term exists because the restore handler (lines 289-294) unconditionally removes class 'hidden' from file-row-img4 even if that row was hidden by the move rather than by the delete.

Exact failing scenario: move img1, img2, img4 (instead of spec img1, img2, img3), then delete img4, then restore img4, then report. Move hides img1, img2, img4 (archive 3, visible 5: img3, img5, doc1-3). Delete hides img4 (already hidden) and sets trash 1. Restore unhides img4 (visible 6: img3, img4, img5, doc1-3). Toast prints 'Root: 6 files, Archive: 3 files, Trash: 0 files, Folder Processed created', and the checker (check.mjs:240) fails on the toast only; Archive ('3 files') and Trash ('0') still pass. Any moved set of exactly 3 files that excludes img4 gives 5; any moved set that includes img4 gives 6; moving 2 files gives 6; moving 4 gives 4. The spec pins img1-3 (spec steps 15-17) and the simulator clicks exactly those (simulate.mjs test-07 block, line 262), so a spec-compliant run is safe. But the fix's number is conditional on the moved set excluding img4, and a live Zen runner who mis-clicks one checkbox (img4 instead of img3) fails the toast while having done the task in spirit. This also corrects council 3's shortcut audit (improvements/worker-y7-council-3.md, Question 2), which claims "Move a different 3 files: archive still 3 and root still 5". That is false when img4 is among the moved 3.

### 1e. Archive '3' and Trash '0': REFUTED on the spec path, with stated conditions

Archive: the move handler pushes one id per selected id (fixture lines 259-271) and the selection is a Set, so no duplicates per move. A second move cannot re-push the same ids because the first move clears the selection (lines 268-269) and the moved rows are hidden, so their checkboxes have no click target. Archive is 3 if and only if exactly 3 files are selected at move time, which the spec pins. Trash: the delete handler is the only writer that pushes to state.trash, and only for img4 (line 275 is the only delete onclick in the fixture; the other seven delete buttons at lines 99-141 have no handler at all). Trash is 1 after delete and 0 after restore (lines 290-292). A double delete cannot happen through the UI because the first delete hides the row containing the button. Both numbers hold on the spec path.

### 1f. NEW PROVEN HOLE (not an attack on the number, an attack on the checker): skipping delete + restore entirely still passes all 8 test-07 checks

Scenario: rename img1-5, move img1-3, create folder Processed, generate report, never touching delete or restore (skip spec steps 23-29). End state: names photo-2026-01/05 pass, archive '3 files' passes, trash counter '0' passes (trash was never touched; the counter starts at '0' in static HTML), row img4 visible passes (never hidden), folder #folder-item-processed passes, toast active passes, toast text passes: after move only, visible rows are img4, img5, doc1-3 = 5, archive 3, trash 0, so the toast is character-identical to the full-run toast. All 8 assertions in check.mjs test-07 branch (lines 215-240) pass. The two end states (full run vs skip run) are DOM-identical on every node the checker reads: the trash table body is empty in both (the restore removes the row the delete created), and grep confirms the fixture contains no restore marker of any kind (only the restore button creation at line 286 and its handler at line 289; no flag, counter, or 'restored' text). The simulator cannot catch the omission either: simulateOne performs steps then calls verifyTest once at the end (simulate.mjs, function simulateOne line 404); it asserts nothing mid-run. So the delete/restore mistake-recovery portion of test-07 is unverifiable by this suite as designed. The wrong number 3 was masking this hole (with 3 expected, both the full run and the skip run failed); the correct number 5 exposes it. This does not make 5 wrong, and it does not block landing 5, but it means test-07 over-credits any runner who skips steps 23-29. Fixing it needs new work (a fixture restore marker or a mid-run simulator assertion), not a different number.

## Attack 2: test-09, direction A (rename to 'note-item-archived', revert fixture line 142)

### 2a. Missed references: REFUTED as a runtime break, with one PROVEN leftover

Grep for 'archived-draft' across tests/realistic/agy-y2/ returns exactly six hits: fixture:66 (static HTML), fixture:142 (renderList ternary), check.mjs:273 and :285, simulate.mjs:364, spec step 29 (line 52). Direction A renames the three non-fixture references and reverts :142, which covers every live reference. The README mentions 'delete archived draft' only in prose (tests/realistic/agy-y2/README.md:34), not as an id. No other file references the id. Leftover: the static HTML line 66 keeps id="note-item-archived-draft", which under direction A never exists at runtime (renderList wipes #notes-list-container innerHTML at load, fixture line 142 area, and rebuilds; renderList() runs at load, fixture line 275). That leftover is dead markup, not a runtime break, but direction A as specified leaves one 'archived-draft' in the tree and a future grep audit will flag it. For completeness the static id should be renamed too, or the direction should say explicitly that line 66 is intentionally dead.

### 2b. A step depends on the 'draft' suffix: REFUTED

No logic depends on the suffix. The title id for the archived note is 'note-item-title-archived' (fixture line 147: key 'archived' falls to the else branch, no 'draft'), and no spec step, simulator step, or checker assertion reads #note-item-title-archived. The only other 'draft' strings are the 'Draft ready: Laptop/Phone' status texts (fixture stage handlers), which are unrelated to the note id. Renaming the div id changes nothing else.

### 2c. The de-vacuoused assertion (id absence PLUS counter 3): REFUTED on the spec path, PROVEN bypassable off-spec

On the spec path the pair is sound. Skip the delete (spec steps 29-30): keys stay personal, archived, shopping, shopping_conflict = 4, counter reads 4, the totalNotes check (check.mjs:282) fails. Delete the wrong note instead: counter drops to 3, but #note-item-archived is still present, so the absence check (check.mjs:285) fails. Either single omission is caught. PROVEN bypass, off-spec only: the save handler's rename branch (fixture lines 181-187) deletes notesState.notes[activeId] whenever the edited title is exactly 'Shopping' and activeId is not 'shopping'. Scenario: click the archived row (activeId becomes 'archived'), type title 'Shopping', click Save, never click Delete. The archived key is deleted by the rename branch and re-added as 'shopping' (overwriting the real Shopping note with the archived note's object). Final keys: personal, shopping, shopping_conflict = 3, counter 3, #note-item-archived absent, #note-item-title-shopping reads 'Shopping', #note-item-title-conflict reads 'Shopping - Phone Copy', toast reads 'Sync completed: 3 notes active...'. All six test-09 checker assertions (check.mjs lines 269-287) pass without #btn-delete-active-note ever being clicked. Mitigating fact, which keeps this from being a live-run hazard: the bypass is caught by the SPEC, not the checker. After the bypass the editor holds the archived note's body ('Old project notes 2025'), so spec step 33 (body must contain 'Milk, Eggs, Bread, Apples') fails visibly for a spec-following runner. The hole is a checker-completeness gap, not a path any spec step performs. Hardening option (not a gate): assert the editor title is 'Personal Tasks' after the delete, since the delete handler falls back to remaining[0] = 'personal' (fixture line 259), while the bypass leaves activeId = 'shopping'.

### 2d. Title id alignment after rename: REFUTED

The title id mapping (fixture line 147) is independent of the div id mapping (line 142). For key 'archived' the title id is 'note-item-title-archived' under both directions, the div contains the title div by DOM nesting, and the static HTML lines 66-67 already pair the ids this way. Nothing in the suite derives one id from the other (grep shows no string manipulation joining 'note-item-' to a title lookup). The simulator's step 7 click on #note-item-title-shopping (simulate.mjs:368) is a literal id, unaffected.

## Attack 3: test-09, direction B (keep Y2's fixture edit, change nothing else)

### 3a. The ternary breaks another key mapping: REFUTED by enumeration

The ternary at fixture:142 maps shopping_conflict to 'conflict-copy', archived to 'archived-draft', and every other key to itself. The only keys that can ever exist are: personal and archived (initial state), note_<timestamp> (create handler, fixture line 168), shopping (save rename branch, lines 181-187), shopping_conflict (keep-both handler). No key 'archived-draft' is ever created as a key, so the branch fires exactly for the archived note. personal, shopping, note_<timestamp> all map to themselves. No other mapping is touched.

### 3b. Title id mapping (line 147) vs div id: REFUTED

For key 'archived', div id is 'note-item-archived-draft' and title id is 'note-item-title-archived'. That pairing is identical to the static HTML (lines 66-67) and the title div is nested inside the item div, so alignment is by nesting, not by string equality. The checker reads #note-item-title-shopping and #note-item-title-conflict (check.mjs:271-272); the simulator clicks #note-item-title-shopping (simulate.mjs:368). No code derives a title id from a div id. No break.

### 3c. A state where renderList produces a DIFFERENT id for the archived note: REFUTED

The div id depends only on the key, and the key 'archived' is stable through the whole flow: the conflict-copy rename changes only a TITLE (save with 'Shopping - Phone Copy' does not hit the exact-'Shopping' rename branch, fixture lines 181-187), keep-both only adds keys, and clicking a row only changes activeId. The archived note's id is 'note-item-archived-draft' in every renderList call from load until deletion, and absent after deletion. There is no rename path for the archived key except the off-spec save-as-'Shopping' case in 2c, which deletes the key rather than re-iding it.

### 3d. The old checker assertion is still vacuous under B: REFUTED

Under direction B the assertion is load-bearing. On a fresh fixture the element exists (renderList maps archived to archived-draft at load), so `check(!archivedItem, ...)` (check.mjs:285) FAILS on the untouched fixture, and it passes only after the archived key is actually deleted. This is confirmed live: /tmp/y2-sim3.log shows test 09 passing with untouchedFailedAsExpected true, and /tmp/y2-check3.log shows the fresh-fixture check failing. Direction B needs no checker change: the existing absence check plus the counter check (check.mjs:282) already satisfy Y2b's "absence PLUS counter" requirement. Y2b's 'vacuous' label describes the pre-edit fixture only; council 3 already corrected this, and I confirm the correction against the current tree.

### 3e. The mixed state (rename references, keep ternary, or vice versa): PROVEN hazard, process constraint

Both mixed states break loudly. References renamed to #note-item-archived with the ternary left in place: renderList never produces that id, simulate.mjs step 6 crashes with no element found (the same exit 3 Y2b saw, for the opposite reason), and the checker absence assertion passes vacuously on fresh and run fixtures. Fixture reverted with references left at -draft: the original Y2b crash returns. The four edits (fixture:142, spec:52, simulate:364, check:273 and :285) must land atomically in whichever direction is chosen. This is a constraint on HOW direction A is applied, not a block on either direction. The current tree is consistent (direction B), so no mixed-state risk exists in the committed state.

### 3f. Direction B is less robust than A in one respect: NOTED, not a block

The ternary is a special case that exists only to satisfy the three references. If a future edit removes it, the suite breaks again (simulator crash + vacuous assertion) with no warning from the fixture itself. Direction A derives the id uniformly from the key and has no special case to regress. That is a genuine maintainability argument for A, but it is not a functional break of B: B is the tested, committed, 10/10-passing state, and switching to A now would churn four files for no integrity gain while risking the mixed state in 3e.

## Attack 4: the verification method itself (simulate.mjs --all)

### 4a. --all aborts on the first throwing test: PROVEN

simulate.mjs main loop (lines 457-458) awaits simulateOne per test with no try/catch inside the loop; the outer main().catch (line 474) prints the error and exits 3. Y2b observed exactly this: the --all run died at test 09 and tests after 09 never ran in that invocation (improvements/worker-y2b-verification.md, defect 2). A crashing test therefore masks the status of every later test, and --all cannot establish 10/10 unless it runs to completion. Y2's re-run 3 did run to completion (10/10, /tmp/y2-sim3.log), so this gap does not taint the current result, but the method as written is not fault-isolated. Per-test runs are the workaround.

### 4b. Simulate cannot catch spec/checker drift: PROVEN

simulate.mjs:9 imports verifyTest from check.mjs, and neither simulate.mjs nor check.mjs reads any .md spec (grep for .md, readFile, spec across both files returns only a code comment). A fix that changes the checker but not the spec (or vice versa) still passes simulate --all. Concretely: if the test-07 spec still said 'Root: 3 files' while check.mjs said 5, simulate --all would still report 10/10. The spec/checker agreement for test-07 (both read 5) was established only by human cross-reading (council 1, and this redteam's grep), not by any automated step. The method proves checker/simulator/fixture consistency, not spec consistency.

### 4c. The untouched-fixture guard proves the conjunction fails, not that each assertion is load-bearing: PROVEN, with the instance that motivated it

simulateOne throws unless verifyTest fails on the untouched fixture, then requires it to pass after the steps (simulate.mjs, function simulateOne line 404). That proves the check as a whole is not trivially passing. It does not prove each assertion matters. The instance: on the pre-edit test-09 fixture, the archived-absence assertion (check.mjs:285) PASSED vacuously on the untouched fixture (querySelector at line 273 returned null, !null is true) while the overall check still failed on the total and title assertions. The guard was green while one assertion was vacuous. That is exactly how defect 2's second flaw survived generation. The current tree has no known vacuous assertion (traced in attacks 1-3), but --all passing cannot by itself certify that; it took the per-assertion audit in council 3 and this redteam to establish it.

### 4d. Puppeteer clicks are not Zen coordinate clicks: PROVEN as a limitation, no concrete instance found in these two tests

page.click acts on a selector handle and scrolls it into view; a live Zen runner clicks coordinates derived from screenshots. An element can exist in the DOM and pass Puppeteer while being unclickable in Zen (covered, off-viewport, zero-size). I found no such instance in test-07 or test-09: every clicked id (checkboxes, modal buttons, nav items, note rows) is a visible control in the fixture layout, and the fixtures carry no overlapping overlays except the modals, which the flows open and close in order. The gap is methodological and is the reason the independent live Zen run is still owed; it is not a proven failure of either fix.

### 4e. Cross-test state leakage in --all: REFUTED as a gap

simulateOne opens a fresh page and loads the fixture URL per test (simulate.mjs, function simulateOne line 404), and check.mjs likewise verifies one fresh fixture per test. No state carries between tests in the same --all run.

## Corrections to the record

- Council 3 (improvements/worker-y7-council-3.md, Question 2, test-07 shortcut audit): "Move a different 3 files: archive still 3 and root still 5" is wrong when img4 is among the moved 3. Root becomes 6 (attack 1d). The audit missed the restore handler's unconditional unhide.
- Council 3 (same section, test-09): "delete the conflict copy instead of the archived note... titles pass" is wrong in detail. Deleting the conflict copy removes #note-item-title-conflict, so the titleConflict check (check.mjs:284) fails too, not only the archived-absence check (check.mjs:285). The conclusion (the check fails) still holds; the example understates how many assertions fire, which strengthens rather than weakens the checker.
- Y2b's 'vacuous assertion' label for test-09 is stale for the current tree (council 3 already noted this; confirmed here in attack 3d). It correctly described the pre-edit fixture.
- Y7's fix log (improvements/worker-y7-fix-log.md) says "No suite edits by Y7 until Y2 commits". That condition is now moot: Y2 has committed and pushed 30a72e5 (verified on origin), and the suite in the tree is the committed suite. The remaining coordination point is that the local branch is behind origin; the worktree content is already the committed content.

## Verdict: NO BLOCK

Neither fix is proven wrong. Test-07 '5' is the correct number on the spec path (attack 1a), confirmed by live toast evidence (/tmp/y2b-sim-07.log) and by the 10/10 re-run (/tmp/y2-sim3.log). Test-09 direction B, the state actually in the tree, is functionally sound: the id exists at runtime, the delete assertion is load-bearing, and the guard holds (attacks 3a-3d), confirmed by the same 10/10 re-run. Direction A is also sound as specified (attacks 2a-2d) but is not needed: switching to it now would churn four files for no integrity gain and would risk the mixed state in attack 3e. Recommendation: land direction B as-is (it is already committed as 30a72e5) and do not apply direction A.

Strongest surviving doubts, stated plainly:

1. Test-07 cannot prove the delete/restore happened. Skipping spec steps 23-29 passes all 8 checks (attack 1f, PROVEN). This is the biggest hole left in the suite, and it is a checker-design gap, not a wrong number. Follow-up, not a gate: add a fixture restore marker or a mid-run simulator assertion.
2. Test-09's delete assertion can be bypassed off-spec through the save handler's rename branch (attack 2c, PROVEN), though the spec's step 33 body check catches it for a live runner. Follow-up, not a gate: assert the editor title is 'Personal Tasks' after the delete.
3. Test-07's Root count depends on the moved set excluding img4 (attack 1d, PROVEN). A live Zen runner who mis-selects one checkbox fails the toast. The live-run brief should warn the runner that the move set must be exactly img1-3, and a Root 6 toast on the live run means the move set (not the fix) is wrong.
4. Method: simulate --all cannot catch spec/checker drift (attack 4b) and aborts on the first crash (attack 4a). The independent live Zen run is still owed (attack 4d); the 10/10 headless result is necessary, not sufficient, evidence for it.
