# test-07-bug-reproduction.md

## Test ID
test-07-bug-reproduction

## Topic
Bug reproduction: follow written steps to reproduce a UI bug and document it.

## Context
the owner received a written bug report describing a UI defect in a local app:
when a user toggles a setting and immediately clicks Save without waiting, the
setting reverts to its previous value. The app has a known race: the first Save
after a toggle writes the previous value back; a second Save commits the
toggled value. The agent must follow the written
reproduction steps exactly, observe whether the bug occurs, capture the before
and after state, and document the result (reproduced or not) with evidence. This
is a strict step-following and documentation task.

## Goal
Execute the written reproduction steps verbatim, record before/after state,
determine whether the revert bug reproduces, and write a short bug note with
the outcome.

## Exact steps
1. Open the bug-repro fixture `fixtures/test-07-bug.html` in the local browser
   (offline, file:// URL).
2. Read the written reproduction steps displayed on the page (they describe
   toggling a setting then immediately saving).
3. Record the current value of the target setting as `before`.
4. Click the setting toggle to flip its value.
5. Click Save immediately (do not wait for any confirmation).
6. Wait briefly, then read the setting value again as `after`.
7. Compare before and after: if they differ, the bug reproduced; if equal, it
   did not.
8. Click Save again (a normal, deliberate save) and read the value as
   `after2`.
9. Read the setting state once more before typing any notes, so the note values
   come from a fresh observation and not from memory.
10. Open the bug notes text area on the page.
11. Type a bug note: title, steps followed, before value, after value, after2
    value, and conclusion (reproduced / not reproduced).
12. Click Save note.
13. Read the saved note below the Save note button and confirm the note text
    is present and includes the conclusion.
14. Confirm the note mentions both before and after values explicitly.
15. Confirm the setting value after the deliberate save (after2) matches the
    toggled value.
16. Record the final state (setting value and note text) as the end state.

## Pass/fail criteria
- Pass: all written reproduction steps executed in order, before/after/after2
  recorded, conclusion matches the observed behavior, note saved and reloadable.
- Fail: a step skipped or reordered, values not recorded, conclusion contradicts
  observed behavior, note missing or not saved.

## What to time
- Per-step wall time for each read/toggle/save/type (16 steps).
- Total wall time from step 1 to step 16.
- Time between toggle and immediate Save (reproduction timing, must be short).
- Time re-reading the note after save (stale observation check).

## Errors designed to expose
- click miss: clicking the wrong toggle, clicking a different Save button.
- slow think: waiting too long between toggle and Save (invalidates the "immediate"
  reproduction condition).
- stale observation: reading the setting before the toggle registers, using a
  stale before value.
- wrong diagnosis: declaring the bug reproduced because the UI blinked, or
  declaring it not reproduced because the deliberate save fixed it.
- fabrication: writing a conclusion not supported by the observed before/after
  values.

## Checker / expected end state
Checker script: `tests/realistic/fcc-k/check.mjs --fixture
fixtures/test-07-bug.html --test 07`.
Expected end state: bug note saved containing before, after, after2 values and
a conclusion consistent with the observed behavior; setting after deliberate
save equals the toggled value.