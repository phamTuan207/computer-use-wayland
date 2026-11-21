# Worker S log - fix fcc-k fixtures (21/11/2026)

All times Asia/Ho_Chi_Minh. Repo: computer-use-wayland, branch todolist-push.
Task: fix the 10 fcc-k realistic test fixtures so they are actually runnable
and honestly verifiable. Starting point: Worker P's live run, 0/10 PASS as
specced, all fixture/spec defects, documented in
tests/realistic/RUN-REPORT-20261121.md.

## The core defect (all 10 tests)

Every `__fcckVerify()` self-simulated the intended flow (set values, push
facts, create events directly in JS) and then checked its own simulated state.
The offline 10/10 pass proved the fixtures' JS worked, not that an agent
could complete the tasks. I replaced ALL 10 checkers with real DOM assertions:
each reads only the DOM state the agent actually produced (cell text, inbox
list, rendered grid cell, saved snapshot, export view). No checker writes
expected state. A fresh fixture now FAILS every checker, as it should.

## What changed per test

- **f01 spreadsheet**: root cause was case-sensitive formula eval: `=C2*D2`
  threw because cell keys are lowercase. Fix: eval is now case-insensitive
  (real spreadsheets accept both cases), so the spec's uppercase formulas
  work unchanged. Also: typing a formula now stores it, so recompute cascades
  to E5/E6/E7 when inputs change. Spec step 23 wording fixed (E7 shows the
  text `COUNT text`, not 3, before the correction).
- **f02 email**: fixture had no read/flag/archive/compose UI at all. Added:
  real message bodies (vendor quote with price 45000, complaint, meeting with
  date/time, newsletters, follow-up), Mark as read / Flag / Star / Archive
  buttons for the open message, a Compose form (To, Subject, Body, Send), and
  a Sent folder that lists sent mail. Spec step 17 now names the corrected
  price 42000 (the checker requires it, and the old spec never told the agent
  what the corrected price was).
- **f03 calendar**: fixture had no event dialog and created events with
  hardcoded values on any click. Added: a real dialog (title, date, start,
  duration, 2 attendee emails, reminder) that opens on a free slot click and
  REFUSES to save an overlapping event; the saved event renders as a green
  block in the grid cell plus an event-detail line. Spec step 19 rewritten:
  there is no separate day view, the event block is verified in the day's
  grid column.
- **f04 research**: fixture had no typing UI for notes (clicking a card added
  a fact). Added: a source detail panel (name, price, support channel) and a
  real notes textarea the agent types fact lines into, plus a saved snapshot
  div. Spec step 15 now reads the saved snapshot. Deliberately no
  localStorage restore: a restored note would let a later run pass without
  agent work.
- **f05 image**: fixture had no folder creation, no rename UI, no index.txt
  UI. Added: New Folder flow, click-to-move, click-to-select + rename field,
  index.txt editor with a saved view. Spec fix: the old spec's extensions
  were wrong (trip-02.jpg for a .png file, trip-03.png for a .jpg file).
  Rename now keeps each file's original extension: trip-01.jpg, trip-02.png,
  trip-03.jpg, trip-04.jpg, trip-05.jpg, trip-06.png, trip-07.jpg,
  trip-08.jpg. Spec steps name the real controls.
- **f06 settings**: both Open buttons were dead, no settings UI at all.
  Added: per-app Settings panels (font size / zoom inputs + Apply + Close)
  and sample documents that render the applied values (Notes text at 18px,
  Reader text scaled to 150% of 16px = 24px, each with a label stating the
  applied value). Spec needed no changes.
- **f07 bug**: all four buttons were dead, no repro steps on the page.
  Added: the written repro steps on the page, real toggle/save behavior, and
  a saved-note view. The race is modeled deterministically: the first Save
  after a toggle writes the previous value back (bug reproduces), a second
  Save commits the toggled value. A real-time window (e.g. 300ms) was
  rejected on purpose: an agent's tool round-trip is seconds, so a
  millisecond window could never be reproduced through the driver. Spec:
  removed the duplicated step 9, documented the race in the Context, step 13
  reads the saved note view.
- **f08 form**: Submit had no handler, no validation code at all. Added:
  real validation (name required, email required + format, password >= 8,
  confirm must match) with per-error messages, and a success message on a
  clean submit. First submit per the spec shows exactly 3 errors. Spec
  needed no changes.
- **f09 convert**: source had 3 rows (spec says 4) already in converted
  form, target was a plain div with no input, Convert just copied. Added: a
  4-row source table (Item/Units/Price), a visible reference block with the
  canonical form, a target textarea the agent types into, and Convert/Apply
  renders the typed lines. Spec needed no changes.
- **f10 document**: all five buttons dead, document was one static line.
  Added: 3 sections (Intro, Details, Summary, each containing `old vendor`),
  a TOC with a table count, a real Find/Replace panel (search shows match
  count, Replace all edits text nodes only), an editable 3-column table
  inserted under Summary (contenteditable cells), Save, and an export view
  showing filename `report-export.md` plus the exported text. Spec step 12
  now verifies the auto-updated TOC count; step 15 reads the export view.

## Verification (jsdom simulation, VM, no live Zen)

No chromium on the VM, so I installed jsdom in /tmp and simulated the
agent's exact spec steps through the DOM for all 10 fixtures
(/tmp/worker-s-verify/simulate-agent.cjs, kept out of the repo because it
needs jsdom, which is not a repo dependency).

Result: **10/10 runnable.**
- Every fresh fixture FAILS its checker with genuine assertion failures
  (real missing state, no exceptions). This proves the checkers no longer
  self-simulate.
- Every simulated agent run PASSES its checker.
- Extra behaviors verified inline: f01 uppercase formulas compute
  (E2 540000, E5 1864000, E6 621333, E7 3); f03 clicking busy Tue 9:00
  refuses to open the dialog; f07 immediate save reverts (after=enabled)
  and deliberate save sticks (after2=disabled); f08 first submit shows
  exactly 3 errors; f10 search finds 3 `old vendor` matches.

## Commits (todolist-push)

- cbbb748 fix(fcc-k): DOM-only checkers + missing UI for f01-f03
- 00df1be fix(fcc-k): DOM-only checkers + missing UI for f04-f06
- 9cfbcf3 fix(fcc-k): DOM-only checkers + missing UI for f07-f10
- 14ef62f fix(fcc-k): specs match the fixed fixtures (+ README checker rule)
- this log (worker-s-fcck-fix-log.md)

## Open items for the parent

- Live Zen run is still the final proof; the jsdom simulation only proves
  each fixture CAN do what its spec asks. Hand to Worker R / the next runner.
- README now states the DOM-only checker rule so future fixture authors do
  not reintroduce self-simulating checkers.
- Nothing is BLOCKED. 10/10 genuinely runnable, 0/10 still blocked.
