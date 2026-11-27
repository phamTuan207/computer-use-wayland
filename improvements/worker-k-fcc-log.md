# Worker K (fcc-claude) test generation log

All times are local wall-clock (UTC+0700). Elapsed is from the first entry of
this task (2026-11-21 15:24:58).

Task: generate 10 hard realistic test cases in `tests/realistic/fcc-k/`,
each in its own `test-XX-name.md`, plus offline fixture HTML and an automated
checker script where possible. Topics are fixed by Muse (spreadsheet, email,
calendar, research notes, image organize, settings, bug reproduction, form
validation, copy conversion, long document edit).

Hard rules kept in mind: no em or en dashes, never ydotool, never touch the
user's Zen tabs, Zalo, Teams, Jarvis, or music, no fabrication, clean up after
testing, small commits, push often to todolist-push.

## 2026-11-21 15:24:58  T+00:00

- Read environment: repo on branch todolist-push (behind origin by 1 commit,
  fast-forwardable). Working tree had untracked files that block the merge:
  `tests/bidi_click_retest.mjs` etc. I did not delete them; merge was deferred
  because the pull would overwrite an untracked file I did not author.
- Confirmed local git identity: user.name phamTuan207,
  email the owner's GitHub noreply address (matches requirement).
- Confirmed Chrome binaries exist for offline checkers:
  ~/.cache/puppeteer/chrome/linux-157.0.8103.78/chrome-linux64/chrome
  and system /usr/bin/chromium.
- `tests/realistic/` did not exist. Created `tests/realistic/fcc-k/` and
  `tests/realistic/fcc-k/fixtures/`.

## 2026-11-21 15:34:23  T+09:25

- Wrote all 10 test case files: test-01-spreadsheet-formula.md,
  test-02-email-triage-reply.md, test-03-calendar-conflicts.md,
  test-04-research-notes.md, test-05-image-organize-rename.md,
  test-06-settings-two-apps.md, test-07-bug-reproduction.md,
  test-08-form-validation-fix.md, test-09-copy-format-convert.md,
  test-10-long-document-edit.md.
  Each file has: Test ID, Topic, Context, Goal, Exact steps (15-40 steps each,
  verified by counting numbered lines), Pass/fail criteria, What to time,
  Errors designed to expose (click miss, slow think, stale observation, wrong
  diagnosis, fabrication), and Checker / expected end state.
- Wrote 10 offline fixture HTML files under fixtures/, one per test.
  Each fixture is a self-contained local HTML app with an inline
  `window.__fcckVerify()` that simulates the intended flow and returns
  `{passed, failures, score, state}`.
- Wrote shared checker `tests/realistic/fcc-k/check.mjs`: launches headless
  chromium via puppeteer-core (executable /usr/bin/chromium by default,
  override with CU_CHROME_PATH), opens the local fixture via file:// URL, calls
  window.__fcckVerify(), prints JSON verdict, exits 0 on pass.
- Verified all 10 fixtures pass offline: ran
  `node tests/realistic/fcc-k/check.mjs --fixture ... --test XX` for every test.
  All 10 returned passed:true, score 1. Representative states:
  test-01 e5=1864000, e6=621333, e7=3; test-05 orgCount=8, dlCount=0;
  test-10 exportClean=true, exportName=report-export.md.
- Verified all fcc-k files are ASCII-clean (no non-ASCII bytes, no em or en
  dashes) and contain no ydotool references.
- Fixed arithmetic error in test-01 (1325000 -> 1864000, 441666 -> 621333
  after recomputing 12*45000+7*82000+5*150000).
- Wrote README.md for the fcc-k directory explaining how to run each checker
  offline and the rules kept.
- Committed in 3 small commits and pushed to todolist-push:
  bab56ec (fixtures + checker), test cases, aeeae09 (log). After a remote
  push from another worker, rebased onto origin/todolist-push and pushed as
  a5d0849 (branch now in sync: local == origin == a5d0849).