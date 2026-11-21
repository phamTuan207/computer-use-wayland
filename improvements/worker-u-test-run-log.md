# Worker U log - q04 re-run + fcc-k live run (21/11/2026)

All times Asia/Ho_Chi_Minh. Repo: computer-use-wayland, branch todolist-push.
Task: fix the q04 fixture bug, re-run q04 on live Zen, run all 10 fixed
fcc-k tests on live Zen.

## 16:49 - start
- Read R's report (RUN-REPORT-AGYQ-20261121.md) and S's log.
- q04 bug confirmed at byte level (python backslash-run counts, not display
  guessing): renderPreview lines 253/256/257 had TWO backslashes before
  each `[`, `]`, `n` (regex matches literal backslash sequences, never
  plain `[[...]]` or real newlines). Same double-escape disease in
  INITIAL_NOTES bodies (147-149, literal `\n` text not newlines), the
  sidebar snippet regex (221), and the __agyVerify hook body (399).
  Line 404 already correct (single backslash).
- Fix: all 8 lines collapsed to single backslashes. Verified in jsdom:
  initial preview renders h1 + paragraphs, RFC preview renders both wiki
  links as `<a class="wiki-link">`, `</p><p>` splits present, no raw
  `[[...]]` survives.
- Commit a4cd520, rebased onto 22b0fa3, pushed as 8af1ead (remote moved
  twice mid-push, another worker pushing).
- Runner written: tests/realistic/run_fcck.py (q04 full re-run with real
  wiki-link click + f01-f10 against S's fixed fixtures, DOM verification
  only, never the fixtures' own checkers). Syntax checked.

## 16:56 - q04 smoke run, live Zen: PASS (4,172 ms)
- Wiki link renders as <a>, real Marionette click navigates to Storage
  Engine, backlinks both directions, pin/search/archive/export all pass.
- Full batch launched right after.

## 16:56 - full batch, live Zen: 11/11 PASS, total 32,731 ms
- q04 PASS 4,118 ms (second run, same verdict).
- f01 PASS 3,604 ms (E5 1864000, E6 621333, E7 3 after COUNTA fix;
  td-click trap still holds).
- f02 PASS 3,335 ms (6 triaged, 2 archived, complaint flagged, reply
  in Sent with both prices).
- f03 PASS 2,540 ms (busy Tue 9:00 refuses, free Tue 10:00 saves with
  2 attendees + 10-min reminder, single green cell).
- f04 PASS 2,584 ms (6 facts, 2 per source, summary saved).
- f05 PASS 3,539 ms (8 moved + renamed with original extensions,
  index 8 mappings, downloads empty).
- f06 PASS 2,816 ms (font 18px, zoom 150% = 24px, both persist).
- f07 PASS 2,563 ms (before enabled, after enabled = bug reproduced,
  after2 disabled, note saved with conclusion).
- f08 PASS 2,479 ms (3 errors first submit, zero after fix, success).
- f09 PASS 2,393 ms (4 lines match reference exactly).
- f10 PASS 2,760 ms (3 matches replaced, table Column A/B/C + 2 rows,
  TOC Tables: 1, export report-export.md clean).
- 383 steps in JSONL, 0 failed steps. No hidden-body incident, no stale
  geckodriver, no user tab touched, none left running.
- Runner note: Marionette element/value does not work on
  contenteditable cells (f10), used focus + execCommand insertText.
- No new Zen-control bug found.
- Reports: RUN-REPORT-Q04-RERUN-20261121.md, RUN-REPORT-FCCK-FIXED-20261121.md.
  Raw logs in repo: run-u-all-20261121.log, run-u-q04-20261121.log,
  live-run-u-20261121.jsonl.
