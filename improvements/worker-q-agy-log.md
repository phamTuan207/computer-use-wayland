# Worker Q (agy) Realistic Test Generation Log

All timestamps are local wall-clock (UTC+0700). Elapsed time is measured from
task start (2026-11-21 15:43:49).

Task: Generate 5 hard realistic test cases for computer-use evaluation in
`tests/realistic/agy-q/`, each in its own test-XX-name.md file with companion
offline HTML fixture and automated verification script.

Topics assigned:
1. Music player: create playlist, add songs, reorder, save
2. Photo gallery: organize photos into albums, tag, search by tag
3. RSS/news reader: subscribe to feeds, mark read, save articles
4. Notes app: write markdown notes, format, link notes, search
5. File search: search by name and content, preview, open, rename results

Strict requirements enforced:
- Step count per test: 15 to 40 exact steps.
- Required sections in each test: context, goal, exact steps, pass/fail criteria,
  what to time (per-step wall time + total), errors designed to expose (click miss,
  slow think, stale observation, wrong diagnosis, fabrication), and checker script
  or exact expected end state.
- Fixtures must be self-contained and run offline (file:// URLs, zero external CDN
  or network requests).
- No em dashes or en dashes anywhere in text or code.
- Small commits, pushed incrementally to todolist-push branch.
- No touching of user applications (Zen tabs, Zalo, Teams, Jarvis, music).

---

## 2026-11-21 15:45:00 (T+00:01:11) - Environment initialization

- Inspected git status on branch todolist-push.
- Synchronized branch with origin/todolist-push (pulled commit b2c9645 fast-forward).
- Verified git author identity: phamTuan207 <232407559+phamTuan207@users.noreply.github.com>.
- Confirmed chromium headless binary and node puppeteer-core execution environment.
- Created test suite directories: `tests/realistic/agy-q/` and `tests/realistic/agy-q/fixtures/`.

## 2026-11-21 15:46:40 (T+00:02:51) - Completed Test 01 (music player)

- Created `tests/realistic/agy-q/check.mjs` test runner script with `--all` and single-test modes.
- Created `tests/realistic/agy-q/README.md` documenting test suite scope and usage.
- Created `tests/realistic/agy-q/test-01-music-player.md` (24 exact steps, 15-40 step rule satisfied).
- Created offline fixture `tests/realistic/agy-q/fixtures/test-01-music-player.html` featuring interactive track catalog, playlist creation, track filtering, reordering, duration tracking, and state verification.
- Verified test with headless chromium via `check.mjs`: score 1, 0 failures, total runtime 51ms.
- Verified no em/en dashes in any files.
