# Realistic tests, clone1 share

10 test cases simulating real, complex browser work. Difficulty is near
uploading a problem to Polygon: create a problem, fill a long form, upload
a file, handle an error midway. Topics here are the first half of the
shared list only: file upload, long forms, many tabs, popup and dialog
handling, download then content check, login then authenticated work.
The second half (code editing, file management, terminal with editor,
error handling as a main topic) belongs to the other clone and is not
used here.

## Layout

Each test lives in its own folder `t01-...` to `t10-...` with three files:

- `README.md`: context, goal, steps, pass and fail conditions.
- `fixture.html`: offline, self-contained fixture. No outside sites, no
  CDN, no network. All state is simulated in the page.
- `check.mjs`: automated check. Drives the fixture with Playwright
  Chromium, asserts the pass conditions, prints one JSON result line,
  exits 0 on pass and 1 on fail.

Shared helpers live in `lib/`: `browser.mjs` (Playwright loading and
Chromium launch) and `server.mjs` (loopback static server).

## How to run

One time setup, in a scratch folder outside the repo:

```sh
mkdir -p /tmp/realistic-scratch && cd /tmp/realistic-scratch
npm init -y && npm install playwright-core
```

Then, from the repo root:

```sh
node tests/realistic/clone1/run_all.mjs
```

That serves the fixtures on loopback, runs all 10 checks in order, writes
`results.json` in this folder with wall-clock start and end plus elapsed
ms per test, and prints a summary. To run one test alone:

```sh
PLAYWRIGHT_CORE_PATH=/tmp/realistic-scratch/node_modules/playwright-core \
  node tests/realistic/clone1/t01-upload-single/check.mjs
```

Each check also starts its own loopback server when `FIXTURE_BASE_URL`
is not set, so it is self-running.

## What is verified, and what is not

- Verified here: every fixture loads and every check passes on Playwright
  Chromium from the local cache, with real timings recorded in
  `results.json`. See the run log in this folder.
- UNVERIFIED: the same flows on Firefox and Zen. No Firefox or Zen
  binary exists on this machine, so no check here proves anything about
  them. The fixtures are plain HTML and JS and should behave the same,
  but that is a claim, not a measurement. Run the same checks against
  Zen on the laptop before quoting any Zen timing.

## Tests

| Test | Topic | Fixture |
| --- | --- | --- |
| t01-upload-single | Upload one file to a web form | Upload a problem statement file with title, progress, checksum |
| t02-upload-multi-error | Upload several files, one fails midway | A too-large file fails, remove it, retry the rest |
| t03-long-form | Long multi-field form | Create a problem, 14 fields, validation errors, success summary |
| t04-long-form-draft | Long form, conditional fields, draft save | Interactive type reveals fields, draft survives reload |
| t05-multi-tab | Work across many tabs | Open 5 tabs, edit in one, verify the list tab updates |
| t06-popup-dialog | Popup and dialog handling | alert, confirm, prompt, modal, popup window with a form |
| t07-download-check | Download a file, check its contents | Download a generated CSV, verify header, rows, checksum |
| t08-login-auth | Login, then authenticated work | Access code login, protected page, session, logout |
| t09-upload-metadata | Upload plus metadata form | File plus metadata, missing file errors, problem ID on success |
| t10-login-upload-download | Login, upload, download result | Authenticated upload, judge counts lines, download report |
