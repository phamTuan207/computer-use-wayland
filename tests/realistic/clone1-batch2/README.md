# Realistic tests, clone1 batch 2

10 NEW test cases simulating real, complex browser work, on topics that
do not overlap batch 1 (upload, long form, multi-tab, popup, download,
login) and do not overlap the other clone's topics. Difficulty is near
uploading a problem to Polygon: multi-step flows with validation errors,
state changes, and a checkable end result.

## Layout

Each test lives in its own folder `t01-...` to `t10-...` with three files:

- `README.md`: context, goal, steps (15-40 each), pass and fail conditions.
- `fixture.html`: offline, self-contained fixture. No outside sites, no
  CDN, no network. All state is simulated in the page. The video test
  ships one generated asset, `clip.mp4` (10 s, 320x180, ffmpeg test
  picture and tone), plus `captions.vtt`.
- `check.mjs`: automated check. Drives the fixture with Playwright
  Chromium, asserts the pass conditions, prints one JSON result line,
  exits 0 on pass and 1 on fail.

Shared helpers live in `lib/`: `browser.mjs` (Playwright loading and
Chromium launch) and `server.mjs` (loopback static server).

## How to run

One time setup, in a scratch folder outside the repo:

```sh
mkdir -p /tmp/realistic-b2-scratch && cd /tmp/realistic-b2-scratch
npm init -y && npm install playwright-core
```

Then, from the repo root:

```sh
PLAYWRIGHT_CORE_PATH=/tmp/realistic-b2-scratch/node_modules/playwright-core \
  node tests/realistic/clone1-batch2/run_all.mjs
```

That serves the fixtures on loopback, runs all 10 checks in order, writes
`results.json` in this folder with wall-clock start and end plus elapsed
ms per test, and prints a summary. To run one test alone:

```sh
PLAYWRIGHT_CORE_PATH=/tmp/realistic-b2-scratch/node_modules/playwright-core \
  node tests/realistic/clone1-batch2/t01-pdf-form/check.mjs
```

Each check also starts its own loopback server when `FIXTURE_BASE_URL`
is not set, so it is self-running.

## What is verified, and what is not

- Verified here: every fixture loads and every check passes on Playwright
  Chromium from the local cache, with real timings recorded in
  `results.json`.
- UNVERIFIED: the same flows on Firefox and Zen. No Firefox or Zen
  binary exists on this machine, so no check here proves anything about
  them. The fixtures are plain HTML and JS and should behave the same,
  but that is a claim, not a measurement. Run the same checks against
  Zen on the laptop before quoting any Zen timing.

## Tests

| Test | Topic | Fixture |
| --- | --- | --- |
| t01-pdf-form | PDF form fill | 3-page form, validation errors, mouse signature, saved record |
| t02-video-player | Video player | Real 10 s clip, play, pause, seek, volume, speed, captions, replay |
| t03-keyboard-nav | Keyboard-only navigation | Tab order, menu, listbox, form, trapped dialog, Ctrl+K search |
| t04-kanban-drag | Drag-drop kanban | HTML5 drag between columns, reorder, add, delete, filter, persist |
| t05-canvas-draw | Canvas drawing | Pen, eraser, undo, redo, fill, PNG save, pixel checks |
| t06-chat-app | Chat app | Two contacts, replies, typing, emoji, attach, search, edit, delete, unread |
| t07-map-directions | Map directions | Fake grid map, modes, toll, detour, alternate route, swap, save |
| t08-cart-checkout | Shopping cart checkout | Catalog, coupons, quantities, checkout validation, order, persist |
| t09-diff-review | Code review diff | Filter, search, inline comments, replies, resolve, hunks, reviews |
| t10-dashboard | Data dashboard filter/export | KPIs, filters, sort, pages, selection, chart, CSV export |
