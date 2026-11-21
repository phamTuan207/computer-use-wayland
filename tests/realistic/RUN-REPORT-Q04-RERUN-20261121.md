# q04 re-run report - fixed fixture, live Zen - 21/11/2026 (Worker U)

All times Asia/Ho_Chi_Minh. Runner: `tests/realistic/run_fcck.py`
(stdlib Python, geckodriver --connect-existing, Marionette 2828) against
the LIVE Zen on the laptop, reusing Worker P's proven driver from
`tests/realistic/run_live.py` and Worker R's helpers from
`tests/realistic/run_agyq.py` (explicit tab switch after window/new,
1s settle after navigation, 0.5s after switch, no maximize, one
WebDriver session per test, always deleted in a finally block).
Fixtures served from a loopback HTTP server on 127.0.0.1:8767.
End states verified by reading the DOM directly. The fixture's
`window.__agyVerify()` hook was NEVER used as an oracle.

## Headline

| Test | Result | Time |
| --- | --- | --- |
| q04 notes app (fixed fixture) | **PASS, all 30 spec steps** | 4,172 ms |

Final tally: **1/1 PASS**. This run was also repeated as the first test
of the full `run_fcck.py all` batch (4,118 ms, PASS again).

## The fix (Task 1, done before this run)

R proved the bug with a live probe: `renderPreview()` in
`fixtures/test-04-notes-app.html` had double-escaped regexes, so
`[[WikiLink]]` markup and paragraph breaks never rendered.

Byte-level confirmation (python backslash-run counts, not display
guessing): lines 253/256/257 had TWO backslashes before each `[`, `]`,
`n`, so the patterns matched literal backslash sequences, never plain
`[[...]]` or real newlines. The same double-escape disease was in
INITIAL_NOTES bodies (lines 147-149, literal `\n` text instead of
newlines), the sidebar snippet regex (line 221), and the `__agyVerify`
hook body (line 399). Line 404 was already correct (single backslash).

Fix (commit 8af1ead on todolist-push): all 8 lines collapsed to single
backslashes. Verified in jsdom before the live run: initial preview
renders h1 + paragraphs, the RFC preview renders both wiki links as
`<a class="wiki-link">`, `</p><p>` splits present, no raw `[[...]]`
survives.

## What this run proves (spec steps 9-10, the part that could not run before)

- Preview HTML after save:
  `<p></p><h1>Memory Tiering Architecture</h1><p></p><p>This proposal
  integrates tiered RAM and CXL memory.</p><p>Related: <a
  class="wiki-link" id="link-note-Storage Engine"
  onclick="openNoteByName('Storage Engine')">Storage Engine</a> and
  <a class="wiki-link" id="link-note-Security Model" ...>Security
  Model</a>.</p>`
- Both wiki links render as `<a>` elements. No raw `[[Storage Engine]]`
  text survives in the preview. Paragraph breaks render as `</p><p>`.
- A real Marionette click on `#link-note-Storage Engine` navigates to
  the Storage Engine note (title field reads "Storage Engine").
- Backlinks box on Storage Engine reads "Linked from: Memory Tiering RFC".

## Rest of the flow (same as R's run, all passing)

Note "Memory Tiering RFC" created with tags rfc, performance, memory;
reciprocal link appended to Storage Engine and its backlinks show
"Linked from: Storage Engine"; "Storage Engine" pinned (PINNED section
lists it); tag search `#performance` returns exactly 2 notes;
"Security Model" archived and present in the archived list; active
count badge 3; export summary "Active: 3, Archived: 1, Pinned: 1".

## Driver notes

- No hidden-body incident in this run (body visibility checked visible
  right after open). No stale geckodriver found before the run.
- No user tab touched: the runner opens its own tab and closes it in
  the session finally block. No geckodriver left running after the run.

## Files

- `tests/realistic/run_fcck.py` - the runner (q04 + f01-f10).
- `tests/realistic/run-u-q04-20261121.log` - full step log of the
  standalone q04 smoke run.
- `tests/realistic/run-u-all-20261121.log` - full step log of the
  11-test batch (q04 first, then f01-f10).
- `tests/realistic/live-run-u-20261121.jsonl` - per-step JSONL, 383
  steps across the batch, 0 failed steps.
- `improvements/worker-u-test-run-log.md` - full timed log.
