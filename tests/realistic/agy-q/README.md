# Realistic Test Suite agy-q (Antigravity Worker Q)

This test suite provides 5 realistic, multi-step browser and application workflows
designed specifically to benchmark computer-use agents (such as Muse or Claude)
under realistic human-like UI constraints.

## Hard Rules Enforced
1. Complexity and Step Count: Each test contains between 20 and 30 concrete,
   reproducible steps (within the 15-40 steps requirement). Short or trivial tasks
   are excluded because they fail to exercise agent perception, latency, error recovery,
   or observation drift.
2. Distinct Topics: Zero overlap with prior test suites (fcc-k, fcc-k2, clone1, clone2).
3. Offline Fixtures: All fixtures are local, standalone HTML documents with pure
   JavaScript and CSS. No network access or external CDNs required.
4. Error Sensitivity: Specifically targets click misses (sub-pixel pointer accuracy
   vs vision grounding errors), slow thinking latency, stale observation drift (over
   120s observation window expiry), misdiagnoses, and hallucinated/fabricated values.
5. Automated Checker: Every fixture exposes a `window.__agyVerify()` verification hook
   that evaluates DOM state, internal data models, and action logs.

## Test Directory
- `test-01-music-player.md`: Playlist creation, track library filtering, reordering,
  volume balance check, and playlist export verification.
- `test-02-photo-gallery.md`: Photo album creation, batch tag application, search
  filtering by compound tags, metadata inspection, and album export.
- `test-03-rss-reader.md`: Feed subscription management, category organization, unread
  filtering, full-article reader view, star bookmarking, and OPML export check.
- `test-04-notes-app.md`: Markdown note authoring, header formatting, bidirectional
  wiki-style link navigation, tag search, and note archive confirmation.
- `test-05-file-search.md`: File system explorer search by pattern and text content,
  file detail preview panel, file renaming, and batch move confirmation.

## Running the Automated Checker
```bash
# Check single test fixture:
node tests/realistic/agy-q/check.mjs --fixture tests/realistic/agy-q/fixtures/test-01-music-player.html --test 01

# Check all 5 fixtures:
node tests/realistic/agy-q/check.mjs --all
```
