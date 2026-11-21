# Realistic test live run report, agy-q set - 21/11/2026 (Worker R)

All times Asia/Ho_Chi_Minh. Runner: `tests/realistic/run_agyq.py`
(stdlib Python, geckodriver --connect-existing, Marionette 2828) against
the LIVE Zen on the laptop, reusing Worker P's proven driver from
`tests/realistic/run_live.py` (explicit tab switch after window/new,
1s settle after navigation, 0.5s after switch, no maximize, one
WebDriver session per test, always deleted in a finally block).
Fixtures served from a loopback HTTP server on 127.0.0.1:8766.
End states verified by reading the DOM directly. The fixtures'
`window.__agyVerify()` hooks were NEVER used as oracles.

## Headline

| Test | Result | Time |
| --- | --- | --- |
| q01 music player | **PASS** | 4,188 ms |
| q02 photo gallery | **PASS** | 4,138 ms |
| q03 RSS reader | **PASS** | 3,972 ms |
| q04 notes app | **FAIL on 1 check only: fixture bug** | 4,120 ms |
| q05 file search | **PASS** | 4,041 ms |

Final tally: **4/5 PASS as specced**. q04 fails only on the wiki-link
rendering defect below; every other q04 check passed, including both
directions of backlink registration, pin, tag search, archive, and the
export manifest. Total scripted machine time for the 5 tests: 20,486 ms
(final full run). Per-step JSONL: 402 steps logged across all runs in
this session, 3 failed steps, all 3 in q05 (see the hidden-body incident).

## q01 music player: PASS (4,188 ms)

All 24 spec steps ran through the real UI. Evidence: library 12 tracks;
sidebar Favorites (8) and Recently Played (15); new playlist "Deep Work
2026" created and active; adds in order Neon Horizon, Midnight Pulse,
Coffee Beans, Solar Winds, plus the mistaken Rainy Window (5 tracks,
19:10); after remove, 4 tracks, 15:40; Solar Winds moved up 3x gives
Solar, Neon, Midnight, Coffee; Coffee up 1x gives the final order Solar,
Neon, Coffee, Midnight; save banner reads exactly "Playlist Deep Work
2026 saved successfully (4 tracks, 15:40)".

## q02 photo gallery: PASS (4,138 ms)

All 30 spec steps ran. Evidence: 12 cards; album "Tokyo Architecture"
created (0); Tokyo filter gives 6 cards with ids 101, 103, 104, 105,
107, 108; batch select 101/104/108 shows "3 photos selected"; album
count becomes (3); photo 108 tags edited to architecture, skyline, night
with nature removed; tag search "night" returns exactly 102, 106, 108;
adding 102 gives album view [101, 102, 104, 108]; export banner reads
"Exported 4 photo records successfully".

## q03 RSS reader: PASS (3,972 ms)

All 28 spec steps ran. Evidence: initial unread badge 6; feed "Wayland
Gazette" subscribed under "Display Servers", badge goes to 9; feed view
shows exactly the 3 Gazette articles, all unread; opening 201 marks it
read (feed count 2) and starring highlights the star button; opening 202
then toggling it back to unread restores count 2 and the unread class;
"Mark All As Read" drops the global badge to 0 with no unread rows left;
Starred view shows exactly article 201; export markdown contains
"- [Explicit Sync Lands in Mainline](https://wayland.local/art-201)".

## q04 notes app: FAIL on 1 check, fixture bug (4,120 ms)

Everything except the wiki-link rendering passed: note "Memory Tiering
RFC" created with tags rfc, performance, memory; backlink data works in
BOTH directions ("Storage Engine" backlinks show "Linked from: Memory
Tiering RFC", and after appending the reciprocal link, the new note's
backlinks show "Linked from: Storage Engine"); "Storage Engine" pinned
(PINNED section lists it); tag search `#performance` returns exactly 2
notes; "Security Model" archived and present in the archived list; active
count badge 3; export summary "Active: 3, Archived: 1, Pinned: 1".

**The failing check, a REAL fixture bug (proven by probe, not a guess):**
`renderPreview()` in `fixtures/test-04-notes-app.html` (lines 252-257)
has double-escaped regexes:

- `.replace(/\\[\\[(.*?)\\]\\]/g, ...)` - the pattern matches a literal
  backslash plus `[[X]\]`, never the plain `[[X]]` in the note body.
- `.replace(/\\n\\n/g, '</p><p>')` and `.replace(/\\n/g, '<br>')` -
  these match a literal backslash followed by "n", never a newline.

Probed live 21/11 ~16:31: after typing the body with
`[[Storage Engine]]` and `[[Security Model]]` and clicking Save, the
rendered preview HTML is
`<p></p><h1>Memory Tiering Architecture</h1>\n\nThis proposal...\n\nRelated: [[Storage Engine]] and [[Security Model]].<p></p>`.
The `[[...]]` markup survives untouched, no `<a id="link-note-...">`
element exists, and the `\n\n` paragraph breaks survive too. Spec steps
9-10 (click the rendered wiki link in Preview) CANNOT run as written.
Fix: single backslashes in those three regexes
(`/\\[\\[(.*?)\\]\\]/` should be `/\[\[(.*?)\]\]/`, `/\\n\\n/` should be
`/\n\n/`, `/\\n/` should be `/\n/`). The run continued the flow via
sidebar navigation instead, so the pin/search/archive/export verdicts
above are real.

## q05 file search: PASS (4,041 ms)

All 30 spec steps ran. Evidence: "Results (15)"; Filename radio selected
by default; filename search "compositor" returns 2 files; preview pane
renders the JSON with line numbers; content search "socket_path" returns
3 files (server.rs, compositor.json, launch.sh); `.json` filter isolates
1 result; rename banner reads "File config/compositor.json renamed to
config/wayland-compositor.json"; post-rename search returns exactly the
renamed file; editor status reads "Active in editor:
config/wayland-compositor.json"; audit summary reads "Renamed: 1, Active
Editor: config/wayland-compositor.json, Read-Only Files: 1".

**Spec bug (noted, not faked):** spec step 27 says the preview badge
displays "[RO]", but the fixture sets exactly "RO" (fixture line 266:
`badge.textContent = f.readOnly ? 'RO' : 'RW'`). The read-only state
itself is proven by the audit summary ("Read-Only Files: 1") and the
badge change RW to RO. The check accepts "RO" and records the wording gap.

## New driver finding: Marionette cannot click a `<tr>` directly

First q05 run: clicking `#row-file-6` failed with HTTP 400 "element not
interactable: Element `<tr id=\"row-file-6\">` could not be scrolled into
view". The row sits inside a scrollable `.results-scroll` container.
Clicking the filename `<td>` inside the row (`#row-file-6 td:nth-child(2)`)
with a real Marionette click works, and the row's onclick fires on the
bubbled click. Rule for future runners: click the `<td>`, never the
`<tr>`, in scrollable tables.

## Incident: new Marionette tabs rendered with body hidden, 16:36-16:44

Two solo q05 re-runs failed at the first interaction ("could not be
scrolled into view" on the search input, `document.body.innerText`
empty). Six probes bisected it:

- The tab reports visible and focused, viewport 1615x1160, readyState
  complete, DOM fully present (body HTML 19,472 bytes).
- `getComputedStyle(document.body).visibility` is `hidden`, inherited
  down the whole tree (HTML itself is visible).
- No inline style, no class, and no stylesheet rule sets it: the
  fixture contains zero occurrences of the word "visibility", and a
  stylesheet scan found no matching rule. The hiding comes from the
  browser side, not the page.
- A pre-existing user tab (muse.ai thread) in the same Zen at the same
  time renders normally (body visible, innerText 10,883 chars). Only
  tabs opened through Marionette `window/new` were affected.
- The state persisted across 5 seconds and across `window.focus()`.
- The same q05 flow had passed 8 minutes earlier in the full run
  (16:34), so the state flipped on between 16:34 and 16:36.

The state cleared at ~16:44-16:45, right after I killed a stale
orphaned geckodriver (PID 113280, listening on port 4446, parent python
long gone) that was blocking new Marionette sessions (a later probe's
POST /session timed out after 30s against it). Correlation, not proven
causation: killing the stale geckodriver is the only change I made in
that window, and the very next probe showed body visible with working
clicks and typing, followed by the clean q05 pass. Lesson recorded:
when a session creation hangs, check for a stale geckodriver by PID and
kill it before retrying; a leaked geckodriver can wedge Marionette, and
the run_live WD class orphans its geckodriver if `__enter__` raises
before `__exit__` ever runs (session POST timeout path).

## Runner bugs fixed during this run (mine, not fixtures)

These were false FAILs in the first full run, fixed in `run_agyq.py`
before the final verdicts above:

1. `select_option` sets a select by VALUE. q02's batch-target album
   options carry album ids as values, so setting the value to the album
   NAME silently selected nothing and the batch add no-op'd (album
   stayed at 0). Added `select_by_text`, which picks the option by its
   visible text and sets the real value. Same trap existed for q05's
   batch action (values are `ro`/`rw`, not "Mark Read-Only").
2. `click_by_text` matched the FIRST element whose text contains the
   string, which is often a wrapper div with no click handler (q03 feed
   tree wrapper, q02 albums-list container). Scoped the calls to the
   clickable elements (`.feed-item`, `#albums-list .nav-item`).
3. q04 sidebar matching used whole-item text, but a note's body snippet
   can contain another note's title (the RFC snippet contains "Security
   Model"), so the click picked the wrong note and the run archived the
   RFC note instead. Added `click_note_by_title`, matching the title
   element only, and `note_titles`, which strips the pin marker.
4. Count checks assumed single-line rendering ("All Photos (12)",
   "Wayland Gazette (3)"), but the fixture renders the count on its own
   line. Added `norm()` whitespace collapsing.
5. q03's export content lives in a `<textarea>`: read `.value`, not
   `.text` (`.text` is empty even when the export worked).
6. q01's playlist title selector read `td:first-child`, which is the
   track-number column; titles are in `td:nth-child(2) strong`.
7. q05 row text is "filename folder ext" columns, not "folder/filename"
   paths; checks now match bare filenames plus the folder separately.

## Cleanup state at end of run

- All test tabs closed by session cleanup. No geckodriver left running
  (verified by pgrep). Loopback server on port 8766 stopped (port free).
  No BiDi session was opened by this run (Marionette only).
- 23 window handles were present at probe time; none were touched
  except the test tabs this runner opened, which it closed itself.
  The 7 about:blank tabs P noted are still there; not closed, same
  reason as P's: cannot tell mine from the user's.

## Files

- `tests/realistic/run_agyq.py` - the runner (stdlib only, imports
  WD/Runner from `run_live.py`).
- `tests/realistic/probe_q04.py` - the q04 wiki-link probe.
- `tests/realistic/probe_q05.py`, `probe_q05b.py`, `probe_q05c.py`,
  `probe_q05d.py`, `probe_q05e.py`, `probe_q05f.py` - the hidden-body
  bisect probes (chain, current-tab comparison, time/focus, rule scan,
  override test).
- `improvements/worker-r-test-run-log.md` - full timed log.
- Raw logs on the laptop: /tmp/worker-r-run-all2.log (final full run),
  /tmp/worker-r-run-q05c.log (q05 clean pass), /tmp/worker-r-live.jsonl
  (per-step JSONL, 402 steps across all runs in this session).

## Open items for the parent

1. q04 fixture bug: fix the three double-escaped regexes in
   `test-04-notes-app.html` renderPreview, then re-run q04 to verify
   the wiki-link navigation steps as specced.
2. q05 spec wording: change "[RO]" to "RO" in `test-05-file-search.md`
   step 27 (or change the fixture to render "[RO]").
3. Hidden-body incident: the root cause is not proven (stale
   geckodriver kill correlates with the clear). If new Marionette tabs
   ever render hidden again, check `getComputedStyle(document.body)
   .visibility` first, then look for stale geckodrivers before
   blaming the fixture.
4. run_live WD should terminate its geckodriver even when `__enter__`
   raises (session POST timeout orphans it).
