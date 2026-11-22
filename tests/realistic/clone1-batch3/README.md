# Realistic tests, clone1 batch 3

10 new hard test cases simulating real, complex browser work, on
topics nobody has done yet in this repo: terminal emulator,
spreadsheet with formulas, video call UI, email client, file
manager, calendar, code editor, settings panel, multi-window
workflow, and music player. Each test has 15 to 40 steps and is
harder than the batch 1 tests: more state changes, more error paths,
and more cross-step assertions. Fixtures are fully offline and
self-contained; no outside sites, no CDN, no network.

## Layout

Each test lives in its own folder `t01-...` to `t10-...` with three
files:

- `README.md`: context, goal, steps, pass and fail conditions.
- `fixture.html`: offline, self-contained fixture. All app state is
  simulated in the page. (t09 has two extra pages, `detail.html`
  and `prefs.html`, opened as real popup windows.)
- `check.mjs`: automated check. Drives the fixture with Playwright
  Chromium through real user actions (click, fill, keyboard, mouse),
  asserts the real DOM state after each step, prints one JSON result
  line, exits 0 on pass and 1 on fail. The checker never calls the
  page's internal functions and never trusts its own simulation; it
  only reads what the page shows.

Shared helpers live in `lib/`: `browser.mjs` (Playwright loading and
Chromium launch) and `server.mjs` (loopback static server). They are
copies of the batch 1 helpers so this folder runs on its own.

## How to run

One time setup, in a scratch folder outside the repo:

```sh
mkdir -p /tmp/realistic-b2-scratch && cd /tmp/realistic-b2-scratch
npm init -y && npm install playwright-core
```

Then, from the repo root:

```sh
node tests/realistic/clone1-batch3/run_all.mjs
```

That serves the fixtures on loopback, runs all 10 checks in order,
writes `results.json` in this folder with wall-clock start and end
plus elapsed ms per test, and prints a summary. To run one test
alone:

```sh
PLAYWRIGHT_CORE_PATH=/tmp/realistic-b2-scratch/node_modules/playwright-core \
  node tests/realistic/clone1-batch3/t01-terminal/check.mjs
```

Each check also starts its own loopback server when
`FIXTURE_BASE_URL` is not set, so it is self-running.

## What is verified, and what is not

- Verified here: every fixture loads and every check passes on
  Playwright Chromium from the local cache, with real timings
  recorded in `results.json`. See the run log in this folder.
- UNVERIFIED: the same flows on Firefox and Zen. No Firefox or Zen
  binary exists on this machine, so no check here proves anything
  about them. The fixtures are plain HTML and JS and should behave
  the same, but that is a claim, not a measurement. Run the same
  checks against Zen on the laptop before quoting any Zen timing.
