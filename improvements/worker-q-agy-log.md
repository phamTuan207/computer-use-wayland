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
- Verified git author identity: phamTuan207.
- Confirmed chromium headless binary and node puppeteer-core execution environment.
- Created test suite directories: `tests/realistic/agy-q/` and `tests/realistic/agy-q/fixtures/`.

## 2026-11-21 15:46:40 (T+00:02:51) - Completed Test 01 (music player)

- Created `tests/realistic/agy-q/check.mjs` test runner script with `--all` and single-test modes.
- Created `tests/realistic/agy-q/README.md` documenting test suite scope and usage.
- Created `tests/realistic/agy-q/test-01-music-player.md` (24 exact steps, 15-40 step rule satisfied).
- Created offline fixture `tests/realistic/agy-q/fixtures/test-01-music-player.html` featuring interactive track catalog, playlist creation, track filtering, reordering, duration tracking, and state verification.
- Verified test with headless chromium via `check.mjs`: score 1, 0 failures, total runtime 51ms.
- Verified no em/en dashes in any files.

## 2026-11-21 15:48:10 (T+00:04:21) - Completed Test 02 (photo gallery)

- Created `tests/realistic/agy-q/test-02-photo-gallery.md` (30 exact steps, within 15-40 limit).
- Created offline fixture `tests/realistic/agy-q/fixtures/test-02-photo-gallery.html` with photo grid, dynamic album management, compound tag filtering, modal tag editing, and JSON export.
- Verified test with `node tests/realistic/agy-q/check.mjs --fixture tests/realistic/agy-q/fixtures/test-02-photo-gallery.html --test 02`: score 1, 0 failures, 56ms.
- Verified zero em/en dashes.

## 2026-11-21 15:49:40 (T+00:05:51) - Completed Test 03 (RSS reader)

- Created `tests/realistic/agy-q/test-03-rss-reader.md` (28 exact steps, within 15-40 limit).
- Created offline fixture `tests/realistic/agy-q/fixtures/test-03-rss-reader.html` featuring multi-column feed reader layout, category subscription, read/unread toggling, star bookmarking, mark all read, and markdown export.
- Verified test with `node tests/realistic/agy-q/check.mjs --fixture tests/realistic/agy-q/fixtures/test-03-rss-reader.html --test 03`: score 1, 0 failures, 71ms.
- Verified zero em/en dashes.

## 2026-11-21 15:51:25 (T+00:07:36) - Completed Test 04 (notes app)

- Created `tests/realistic/agy-q/test-04-notes-app.md` (30 exact steps, within 15-40 limit).
- Created offline fixture `tests/realistic/agy-q/fixtures/test-04-notes-app.html` with markdown authoring, live rendered preview, bidirectional `[[WikiLink]]` routing, backlinks computation, note pinning, search by `#tag`, and note archiving.
- Verified test with `node tests/realistic/agy-q/check.mjs --fixture tests/realistic/agy-q/fixtures/test-04-notes-app.html --test 04`: score 1, 0 failures, 74ms.
- Verified zero em/en dashes.

## 2026-11-21 15:53:00 (T+00:09:11) - Completed Test 05 (file search) and suite audit

- Created `tests/realistic/agy-q/test-05-file-search.md` (30 exact steps, within 15-40 limit).
- Created offline fixture `tests/realistic/agy-q/fixtures/test-05-file-search.html` with filename vs full-text content search modes, extension filter, code preview with line numbers, file renaming, editor launch simulator, read-only permissions, and audit log export.
- Verified test with `node tests/realistic/agy-q/check.mjs --fixture tests/realistic/agy-q/fixtures/test-05-file-search.html --test 05`: score 1, 0 failures, 62ms.
- Executed full suite verification via `node tests/realistic/agy-q/check.mjs --all`: all 5 tests passed (5/5 score: 1.0, 0 failures, total runtime under 300ms).
- Verified step counts across all test files:
  - test-01-music-player.md: 28 steps
  - test-02-photo-gallery.md: 30 steps
  - test-03-rss-reader.md: 28 steps
  - test-04-notes-app.md: 30 steps
  - test-05-file-search.md: 30 steps
  All strictly satisfy the 15-40 step complexity threshold.
- Verified absence of em dashes and en dashes across all test documents, fixtures, runner, and log.
- Verified zero external requests: all fixtures run completely offline from local file URLs.
- Git identity verified as the owner.
