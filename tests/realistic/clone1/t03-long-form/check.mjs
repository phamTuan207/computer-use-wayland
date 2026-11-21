// t03-long-form check. Submits the 14-field form empty, expects at
// least 4 errors, fills all fields, submits again, and asserts the
// success summary. Prints one JSON result line. Exit 0 on pass, 1 on fail.
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { launchBrowser, nowIso } from '../lib/browser.mjs';
import { serveDir } from '../lib/server.mjs';

const testDir = path.dirname(fileURLToPath(import.meta.url));
const testName = path.basename(testDir);
const startedAt = nowIso();
const started = Date.now();
const failures = [];
const details = {};

let browser = null;
let closeServer = null;
try {
  let fixtureUrl;
  if (process.env.FIXTURE_BASE_URL) {
    fixtureUrl = process.env.FIXTURE_BASE_URL.replace(/\/$/, '') + '/' + testName + '/fixture.html';
  } else {
    const server = await serveDir(testDir);
    fixtureUrl = server.url + '/fixture.html';
    closeServer = server.close;
  }
  browser = await launchBrowser();
  const page = await browser.newPage();
  await page.goto(fixtureUrl);
  await page.click('#submit');
  await page.waitForSelector('#errors:not(:empty)', { timeout: 10000 });
  const errors = (await page.textContent('#errors')) || '';
  details.emptySubmitErrors = errors;
  for (const word of ['Title', 'Statement', 'Sample input', 'Sample output']) {
    if (!errors.includes(word)) failures.push('empty submit error list missing: ' + word);
  }
  const values = {
    '#title': 'Long Form Problem',
    '#short': 'lfp',
    '#time': '2',
    '#memory': '256',
    '#tags': 'graphs, shortest path',
    '#statement': 'Find the shortest path.',
    '#inputfmt': 'First line has n and m.',
    '#outputfmt': 'One integer, the distance.',
    '#samplein': '3 2\n1 2\n2 3',
    '#sampleout': '2',
    '#notes': 'Draft for review.',
  };
  for (const [sel, value] of Object.entries(values)) {
    await page.fill(sel, value);
  }
  await page.selectOption('#difficulty', 'medium');
  await page.selectOption('#checker', 'token');
  await page.click('#submit');
  await page.waitForSelector('#summary:not(:empty)', { timeout: 10000 });
  const summary = (await page.textContent('#summary')) || '';
  details.summary = summary;
  if (!summary.includes('Long Form Problem')) failures.push('summary missing title');
  if (!summary.includes('14 fields')) failures.push('summary does not confirm 14 fields');
  const leftover = (await page.textContent('#errors')) || '';
  if (leftover.trim() !== '') failures.push('errors remain after successful submit: ' + leftover);
} catch (err) {
  failures.push(String(err && err.message ? err.message : err));
} finally {
  if (browser) await browser.close();
  if (closeServer) await closeServer();
}

const result = {
  test: testName,
  pass: failures.length === 0,
  failures,
  details,
  started_at: startedAt,
  finished_at: nowIso(),
  elapsed_ms: Date.now() - started,
};
console.log(JSON.stringify(result));
process.exit(result.pass ? 0 : 1);
