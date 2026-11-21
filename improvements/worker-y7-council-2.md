# Council Member 2 verdict: test-09 fix direction (Worker Y7)

- Council member: 2 (Muse, independent of Y2 and Y7)
- Date: 2026-11-21 ~18:25 +07
- Question: which test-09 fix direction is correct, Direction A (Y2b's specified fix, ordered by the parent) or Direction B (Y2's applied fix)?
- Verdict: **GO for B. KEEP Y2's fixture fix. Change nothing in spec, simulator, or checker.**
- Branch: todolist-push. No suite files were edited by this council member.

## Evidence base

Files read in full or in the cited ranges, on the VM repo:

- improvements/worker-y2b-verification.md (Defect 2)
- improvements/worker-y2-agy-log.md lines 34-35 (Y2's fix record)
- improvements/worker-y7-fix-log.md lines 14, 16 (conflict note, Y2 re-run result pending)
- tests/realistic/agy-y2/fixtures/test-09-notes-sync.html (full)
- tests/realistic/agy-y2/check.mjs test-09 branch, lines 269-287
- tests/realistic/agy-y2/simulate.mjs test-09 block, lines 333-369, and integrity guard, lines 413-416
- tests/realistic/agy-y2/test-09-notes-sync.md step 29, line 52

Greps run:

- `archived-draft` across tests/realistic/: exactly 6 occurrences, all inside agy-y2.
- Bare `note-item-archived` (excluding the `-draft` form): zero occurrences in the suite.
- `archived-draft` across the whole repo: only improvements logs mention it outside agy-y2 (Y2 log, Y2b log, Y2b verification, Y7 fix log). Logs are history, not code, and must not be edited to match.

Live attempt: I tried to run `simulate.mjs --test 09` on the VM against a copy in /tmp (never the suite itself). It could not launch the browser: /opt/meta-chromium/chrome fails with "Hatch WebGL domain policy is required for browser startup". That is a VM environment limitation, not a test result. Direction B therefore has no live confirmation from me. Y2's log claims a re-run after the fix, but Y7's log records that result as still pending. A live run on the laptop is still owed by Y7 (see "What Y7 must do").

Note on provenance: the agy-y2 directory is untracked (`?? tests/realistic/agy-y2/`), so there is no committed copy to diff Y2's edit against. The pre-edit form of fixture line 142 (single ternary, key `archived` producing id `note-item-archived`) is established by three agreeing sources: Y2b's verification report line 45, Y2's log line 34, and the task brief.

## (a) Hard requirement: the checker must FAIL on a fresh fixture and when delete never runs

**Finding: TIE. Both directions satisfy it. The vacuity Y2b flagged belonged to the ORIGINAL fixture, not to either fix.**

The original defect: renderList() rebuilt every row as `note-item-` + key, so key `archived` produced `note-item-archived` at runtime while the checker queried `#note-item-archived-draft` (check.mjs line 273). That id never existed at runtime, so `check(!archivedItem, ...)` at line 285 passed no matter what, including when delete never ran. Either fix cures this the same way: it makes the queried id actually exist before delete, so the assertion can fail.

Direction B trace (current state, Y2's edit in place):

- Fresh load: initial `renderList()` (fixture line 275) wipes the static list (`listContainer.innerHTML = ''`, line 135) and rebuilds from keys `personal`, `archived` (line 121). Line 142 maps key `archived` to id `note-item-archived-draft`. The element EXISTS at runtime. Checker on the untouched fixture: totalNotes reads `2` (line 270, counter set from key count), so the line 282 check (`totalNotes === '3'`) FAILS; `archivedItem` is non-null, so the line 285 check FAILS. The integrity guard (simulate.mjs lines 413-416, which throws unless the check fails on the untouched fixture) is satisfied by two independent checks.
- Delete never runs (flow through spec step 28, steps 29-30 skipped): notes are personal, archived, shopping, shopping_conflict, 4 keys. Counter reads `4`, line 282 FAILS. The archived element is still present, so line 285 FAILS. The deletion assertion genuinely detects the skipped delete. Not vacuous.
- Delete runs (correct flow): the step 6 click (simulate.mjs line 364) selects the row, the row onclick handler (fixture lines 157-162) sets `activeId = 'archived'`, the delete handler (lines 255-265) deletes `notesState.notes['archived']` and re-renders. The element is gone, counter is `3`. Lines 282 and 285 both PASS.

Direction A trace (revert line 142 to the single ternary, rename the four references to `note-item-archived`):

- Fresh load: key `archived` maps by the default branch to id `note-item-archived`. The element EXISTS. The renamed checker query finds it, so the renamed line 285 check FAILS; counter `2` fails line 282.
- Delete never runs: counter `4` fails line 282; `#note-item-archived` still present, so the renamed line 285 check FAILS.
- Delete runs: element gone, counter `3`, both PASS.

Identical end state on this criterion. The hard requirement does not discriminate between A and B. Any claim that only A de-vacuouses the checker is wrong: B de-vacuouses it too, by making the already-written query match a real runtime element.

## (b) Simulator click at step 6

**Finding: TIE, conditional on A being applied completely.**

- Direction B: `#note-item-archived-draft` exists from load onward (fixture line 142 mapping) and is still present at step 6, because the `archived` key is not deleted until steps 6-7. `page.click('#note-item-archived-draft')` (simulate.mjs line 364) succeeds, the onclick sets `activeId = 'archived'`, and the next click (line 365, `#btn-delete-active-note`) deletes it. This is the exact crash Y2b reported (exit 3, no element for the selector), cured by the element now existing.
- Direction A: after the rename, `page.click('#note-item-archived')` targets the id the reverted line 142 produces. The element exists at step 6 for the same reason. The click succeeds.

No live run confirms either click from this council member (VM browser launch blocked, see Evidence base). The static trace proves both. For B, Y2's claimed re-run is unconfirmed (result pending per Y7's log), so Y7 must still run it live on the laptop.

## (c) Naming convention: does the fix follow the fixture's own convention or add a confusing special case?

**Finding: slight edge to A on abstract cleanliness, but B follows the fixture's demonstrated pattern and is not confusing. Call this a wash, not decisive.**

The fixture's id rule (line 142) is `note-item-` + key, with explicit descriptive mappings where the spec needs them. The pre-existing special case is `shopping_conflict` to `conflict-copy`, which exists because the spec (step 23), simulator (step 5), and title rule all use the descriptive `conflict-copy` / `conflict` ids instead of the raw key. The fixture therefore already tolerates descriptive-id mappings; B's `archived` to `archived-draft` mapping is a second instance of the same pattern, not a new kind of hack. A reader who understands the conflict-copy branch understands the archived-draft branch immediately.

Points for A: reverting to one special case is cleaner in the abstract, and it makes the row id pair with the title id: row `note-item-archived` with title `note-item-title-archived` (title rule line 147 has no special case for `archived`, and static line 67 already uses `note-item-title-archived`). Under B the row carries a `-draft` suffix the title lacks.

Points for B: the row/title asymmetry B preserves already exists in the author's own static HTML (line 66 row `note-item-archived-draft` versus line 67 title `note-item-title-archived`), so B introduces no new inconsistency. The `-draft` suffix is descriptive, matching the note title `Archived Draft` (line 121). And the static HTML (lines 64-69) is dead markup at runtime: `renderList()` at load (line 275) wipes it (line 135) before any step runs, so matching line 66 is cosmetic, not functional. Nothing at runtime reads `#note-item-title-archived`, so the asymmetry buys no confusion in practice.

## (d) Other references either direction misses

**Finding: neither direction misses a live reference. But Direction A as specified is incomplete: it omits the static HTML line 66.**

Full grep of `archived-draft` in tests/realistic/ (6 occurrences, all in agy-y2):

1. Fixture line 66: static `id="note-item-archived-draft"`.
2. Fixture line 142: renderList mapping (Y2's edit).
3. check.mjs line 273: `document.querySelector('#note-item-archived-draft')`.
4. check.mjs line 285: `check(!archivedItem, 'Outdated note #note-item-archived-draft was not deleted')`.
5. simulate.mjs line 364: `page.click('#note-item-archived-draft')`.
6. Spec line 52 (step 29): click row `#note-item-archived-draft`.

No other test in the suite references the id. Bare `note-item-archived` appears nowhere, so Direction A introduces a new id string and nothing else needs updating for it.

Direction B misses nothing: the one fixture edit (line 142) makes all five other occurrences consistent. Zero further edits.

Direction A as specified renames occurrences 3, 4, 5, 6 and reverts occurrence 2, but says nothing about occurrence 1 (static line 66). After A as specified, line 66 would still say `note-item-archived-draft` while the runtime id is `note-item-archived`: a stale static id of exactly the kind that caused this defect (static HTML claiming an id the runtime never produces). A complete A needs a fifth edit (line 66 to `note-item-archived`). That is a real gap in A as ordered.

Second asymmetry, on failure mode if a future edit drifts:

- Under B, if someone removes the line 142 branch, the simulator click (line 364) throws `No element found for selector` and the run crashes loudly (exit 3, as Y2b saw). Degradation is loud.
- Under A, if the rename is applied to simulator and spec but missed in check.mjs line 273, the checker query matches nothing, line 285 goes vacuous again, and the suite can still pass while the deletion assertion is dead. The totalNotes `3` check (line 282) still catches a skipped delete (counter stays `4`), so the suite would not silently pass a skipped delete, but one assertion would silently degrade. A's correctness depends on 4-5 coordinated edits staying in sync; B's depends on one line.

## Why B over A

Both directions are correct: both end with a working test and a non-vacuous checker, proven by trace in (a) and (b). The decision turns on robustness and on which artifact was actually wrong.

- The spec is the contract. The spec (step 29, line 52), the simulator (line 364), the checker (lines 273, 285), and the static HTML (line 66) all agreed on `note-item-archived-draft`. Only renderList's id generation disagreed. Four artifacts against one. The minimal, intent-preserving fix is to correct the one outlier (B), not to rewrite the contract and three consumers to match a generator accident (A).
- B is one edit, already applied, with zero remaining missed-reference risk. A is four edits as specified, five when done completely, each a chance to miss one, and as specified it leaves line 66 stale.
- B's future failure mode is loud (simulator crash); A's is a silent re-vacuousing of one assertion.
- The convention edge for A in (c) is real but cosmetic: no runtime code reads the archived title id, and the fixture already carries a descriptive-mapping precedent.

The parent's order for A was reasonable when written: Y2b's report predates Y2's fix and specified the rename. But Y2's fix achieves the identical end state on the hard requirement with less risk, so the order's premise (that only the rename cures the vacuity) does not hold. Judge the artifact, not the process: Y2's process was hasty, the resulting line is correct.

## What Y7 must do (GO for B)

1. Keep fixture line 142 exactly as Y2 left it. Change nothing in test-09-notes-sync.md, simulate.mjs, or check.mjs for this defect.
2. Live-verify on the laptop (the VM browser cannot launch here): run `node tests/realistic/agy-y2/simulate.mjs --test 09` and confirm PASS with the integrity guard satisfied (check fails on untouched fixture first, simulate.mjs lines 413-416). Record the run output in the Y7 fix log. Y2's claimed re-run does not count as this verification, since its result is still pending in the log.
3. After the separate test-07 fix, re-run `simulate.mjs --all` on the laptop and confirm 10/10 before declaring the suite fixed.
4. If the parent insists on Direction A for convention reasons despite this verdict, A is also correct ONLY with the amendment: update static fixture line 66 to `id="note-item-archived"` as a fifth edit, in addition to the four renames. A without the line 66 edit leaves a stale static id and is not acceptable.

## Caveats

- This verdict is static verification plus trace. No live browser run confirms either direction from this council member, because the VM Chrome at /opt/meta-chromium/chrome refuses to launch (Hatch WebGL domain policy required). The trace is complete and the line citations are exact, but the live PASS for B is still owed by Y7 on the laptop.
- This verdict covers test-09 only (Defect 2). Test-07 (Defect 1, toast `Root: 5 files` versus checker `Root: 3 files`) is a separate fix and is not judged here.
