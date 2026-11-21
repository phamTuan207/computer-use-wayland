# fcc-k fixed fixtures live run report - 21/11/2026 (Worker U)

All times Asia/Ho_Chi_Minh. Runner: `tests/realistic/run_fcck.py`
(stdlib Python, geckodriver --connect-existing, Marionette 2828) against
the LIVE Zen on the laptop, reusing Worker P's proven driver from
`tests/realistic/run_live.py` (explicit tab switch after window/new,
1s settle after navigation, 0.5s after switch, no maximize, one
WebDriver session per test, always deleted in a finally block).
Fixtures served from a loopback HTTP server on 127.0.0.1:8767.
End states verified by reading the DOM directly. The fixtures'
`window.__fcckVerify()` hooks were NEVER used as oracles (they are now
real DOM assertions, but the verdicts below come from the runner's own
DOM reads, step by step).

## Headline

| Test | Result | Time |
| --- | --- | --- |
| f01 spreadsheet formulas | **PASS** | 3,604 ms |
| f02 email triage + reply | **PASS** | 3,335 ms |
| f03 calendar conflicts | **PASS** | 2,540 ms |
| f04 research notes | **PASS** | 2,584 ms |
| f05 image organize + rename | **PASS** | 3,539 ms |
| f06 settings two apps | **PASS** | 2,816 ms |
| f07 bug reproduction | **PASS** | 2,563 ms |
| f08 form validation | **PASS** | 2,479 ms |
| f09 copy format convert | **PASS** | 2,393 ms |
| f10 long document edit | **PASS** | 2,760 ms |

Final tally: **10/10 PASS as specced**. Total scripted machine time for
the 10 tests: 28,613 ms (plus q04 re-run 4,118 ms in the same batch,
11/11 overall, 32,731 ms). Per-step JSONL: 383 steps across the batch,
0 failed steps. This is the first live Zen run of Worker S's fixed
fixtures (previously: P's run 0/10, all fixture/spec defects; S's
jsdom simulation 10/10 runnable).

## Per-test evidence

### f01 spreadsheet: PASS (3,604 ms)

All 26 spec steps ran through the real UI. Evidence: headers Date,
Item, Units, Price, Total; the td-click trap still holds (clicking
`#a2` directly selects nothing, only the cell buttons select); E2
540000, E3 574000, E4 750000 from the uppercase formulas `=C2*D2`
etc. (case-insensitive eval works); E5 1864000, E6 621333; the wrong
formula `=COUNT(E2:E4)` shows exactly "COUNT text"; after correction
to `=COUNTA(E2:E4)`, E7 shows 3.

### f02 email: PASS (3,335 ms)

All 22 spec steps ran. Evidence: inbox 6 messages; message 1 body
quotes 45000; message 1 marked read; message 2 complaint ("damaged")
flagged; message 3 meeting at 10:00 marked read; messages 4 and 5
(Newsletter A/B) archived and absent from the inbox; message 6 marked
read and starred; reply composed to vendor@example.com with subject
"Re: vendor quote - price correction" and a 3-sentence body quoting
both 45000 and 42000; Sent folder shows the reply; final inbox is
exactly [msg1, msg2, msg3, msg6] with msg2 still flagged and msg1
still read.

### f03 calendar: PASS (2,540 ms)

All 20 spec steps ran. Evidence: week shows Tue-Sat; busy slots read
from the grid (Tue 9:00 and 13:00, Wed 10:00/11:00/14:00, Thu 9:00/12:00,
Fri 10:00, Sat 9:00/15:00); clicking busy Tue 9:00 refuses with "That
slot is busy. Pick a free (white) slot." and no dialog opens; clicking
free Tue 10:00 opens the dialog (day Tue, hour 10:00); saved event
renders as the single green cell "Project sync 10:00-10:30" on Tue
10:00; event detail reads "Title: Project sync | Day: Tue | Start:
10:00 | Duration: 30 minutes | Attendees: teammate1@example.com,
teammate2@example.com | Reminder: 10 minutes before"; no event on any
other day.

### f04 research: PASS (2,584 ms)

All 17 spec steps ran. Evidence: notes start empty, 3 source cards;
source details read (Alpha Service $12/mo email, Beta Service $19/mo
chat, Gamma Service $9/mo phone); 6 fact lines typed with source
labels (2 each for A/B/C); summary "Alpha $12/mo vs Beta $19/mo vs
Gamma $9/mo, all differ."; saved snapshot contains all 6 facts plus
the summary; notes survive save.

### f05 image: PASS (3,539 ms)

All 24 spec steps ran. Evidence: 8 files in Downloads; Organized
folder created; each file moved then renamed in order (trip-01.jpg,
trip-02.png, trip-03.jpg, trip-04.jpg, trip-05.jpg, trip-06.png,
trip-07.jpg, trip-08.jpg, each keeping its original extension);
Organized holds exactly the 8 trip names; Downloads empty; index.txt
saved with all 8 "original -> new" mappings; Downloads still empty
at the end.

### f06 settings: PASS (2,816 ms)

All 18 spec steps ran. Evidence: Notes font starts 14, Reader zoom
starts 100; Notes font set to 18 and applied (settings line reads
"font_size: 18", sample doc renders at 18px, label mentions 18);
Reader zoom set to 150 and applied (settings line reads "zoom: 150",
sample doc renders at 24px = 150% of 16px, label mentions 150); both
settings still show the applied values on re-read; both sample docs
remain open.

### f07 bug reproduction: PASS (2,563 ms)

All 16 spec steps ran in order. Evidence: written repro steps read
from the page; before = enabled; toggle then immediate Save gives
after = enabled (the bug reproduced, setting reverted); deliberate
second Save gives after2 = disabled (toggled value sticks); fresh
re-read before typing confirms disabled; saved note reads "Bug:
setting reverts on immediate save. Before enabled After enabled
After2 disabled. Conclusion: reproduced."; final setting value
disabled.

### f08 form validation: PASS (2,479 ms)

All 16 spec steps ran. Evidence: first submit with name filled, email
empty, 4-char password, mismatched confirm shows exactly 3 errors
("Email is required", "Password must be at least 8 characters",
"Passwords do not match"); after fixing email to pham@example.com,
password to password1234 (12 chars), confirm to match, the second
submit shows zero errors and "Registration successful."; final values
read back (name Pham Tuan, valid email, password 12 chars, passwords
match).

### f09 convert: PASS (2,393 ms)

All 18 spec steps ran. Evidence: header Item, Units, Price; 4 source
rows read (Widget 12 45000, Gadget 7 82000, Tool 5 150000, Cable 20
12000); reference block read (4 lines); 4 converted lines typed and
applied; output matches the reference line for line, exactly 4 lines,
no extras.

### f10 long document: PASS (2,760 ms)

All 17 spec steps ran. Evidence: 3 sections, TOC starts "Tables: 0";
search for "old vendor" finds 3 matches; Replace all leaves 0 matches;
no "old vendor" remains in the document, "new vendor" present; table
inserted under Summary with header Column A/B/C and body rows
[Widget, 12, 45000] and [Gadget, 7, 82000] (filled via
contenteditable focus + execCommand insertText, the user-equivalent
input path, since Marionette element/value does not apply to
contenteditable cells); TOC count now "Tables: 1"; saved; export view
reads "Filename: report-export.md", contains "new vendor" and the
table, no "old vendor".

## Driver notes

- No hidden-body incident in this run (body visibility checked visible
  right after opening every fixture). No stale geckodriver found before
  the run; none left after. No user tab touched: each test opens its
  own tab and closes it in the session finally block.
- No new Zen-control bug found. One runner-side note: Marionette
  element/value does not work on contenteditable cells (f10), so the
  runner uses focus + document.execCommand('insertText') for those.
- q04 was re-run in the same batch first (4,118 ms, PASS); see
  RUN-REPORT-Q04-RERUN-20261121.md.

## Files

- `tests/realistic/run_fcck.py` - the runner (q04 + f01-f10).
- `tests/realistic/run-u-all-20261121.log` - full step log of the
  11-test batch.
- `tests/realistic/run-u-q04-20261121.log` - full step log of the
  standalone q04 smoke run.
- `tests/realistic/live-run-u-20261121.jsonl` - per-step JSONL, 383
  steps across the batch, 0 failed steps.
- `improvements/worker-u-test-run-log.md` - full timed log.
