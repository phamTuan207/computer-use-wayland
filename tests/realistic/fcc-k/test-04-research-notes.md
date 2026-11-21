# test-04-research-notes.md

## Test ID
test-04-research-notes

## Topic
Research + note taking across 3+ sources.

## Context
Pham Tuan is researching three competing services and needs to gather facts
from 3 local source pages (offline HTML fixtures) into a single note. The
agent opens each source page, reads specific facts (price, tier, support
channel), copies them into a notes page, adds a source URL for each fact, then
writes a one-line comparison summary. This tests reading across multiple
tabs/pages, copying without dropping characters, and assembling a structured
note.

## Goal
Read 3 source pages, extract 2 facts from each (6 facts total), write them into
a notes page with source attribution, and add a final comparison summary line.

## Exact steps
1. Open the research notes fixture `fixtures/test-04-research.html` in the
   local browser (offline, file:// URL).
2. Verify the notes area is empty and the source list shows 3 source cards.
3. Open source card A; read fact 1 (service name) and fact 2 (monthly price).
4. Switch to the notes page; type fact 1 with source label `Source A`.
5. Type fact 2 with source label `Source A` and the price value.
6. Return to sources; open source card B; read fact 1 and fact 2.
7. Switch to notes; type fact 1 with source label `Source B`.
8. Type fact 2 with source label `Source B` and the price value.
9. Return to sources; open source card C; read fact 1 and fact 2.
10. Switch to notes; type fact 1 with source label `Source C`.
11. Type fact 2 with source label `Source C` and the price value.
12. Verify all 6 facts are present in the notes area (scan the text).
13. Click the summary field and type a one-line comparison covering all 3
    sources (at least 20 characters).
14. Click Save notes.
15. Read the saved notes snapshot below the Save button and verify the summary
    line is present in it.
16. Count facts in notes: confirm exactly 6 fact lines with 3 distinct source
    labels.
17. Confirm no fact text is truncated (each fact fully visible).

## Pass/fail criteria
- Pass: 6 facts recorded, each with correct source label, summary line present
  and >= 20 chars, notes saved and reloadable, no truncated text.
- Fail: a fact missing or wrong value, source label mismatched, summary missing
  or too short, notes not saved after reload, text truncated.

## What to time
- Per-step wall time for each open/read/type/click (17 steps).
- Total wall time from step 1 to step 17.
- Time switching between source cards and notes (tab switching latency).
- Time re-reading notes after save (stale observation check).

## Errors designed to expose
- click miss: clicking the wrong source card or the wrong fact field.
- slow think: long pause between reading a fact and typing it into notes.
- stale observation: reading notes before Save completes, seeing old content.
- wrong diagnosis: concluding a source page failed to load when a fact is just
  located lower on the page.
- fabrication: inventing a fact value or source label not read from the page.

## Checker / expected end state
Checker script: `tests/realistic/fcc-k/check.mjs --fixture
fixtures/test-04-research.html --test 04`.
Expected end state: notes contain 6 fact lines with labels Source A/B/C (each
twice), a summary line >= 20 chars, saved state present after reload, no
truncated fact text.