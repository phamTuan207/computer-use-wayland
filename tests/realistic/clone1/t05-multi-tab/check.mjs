// t05-multi-tab check. Opens the list page, opens problem 2 in a new
// tab, edits its title, closes the tab, refreshes the list, and asserts
// the new title appears while the other four rows are unchanged.
// Prints one JSON result line. Exit 0 on pass, 1 on fail.
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
  let baseUrl;
  if (process.env.FIXTURE_BASE_URL) {
    baseUrl = process.env.FIXTURE_BASE_URL.replace(/\/$/, '') + '/' + testName;
  } else {
    const server = await serveDir(testDir);
    baseUrl = server.url;
    closeServer = server.close;
  }
  browser = await launchBrowser();
  const context = await browser.newContext();
  const list = await context.newPage();
  await list.goto(baseUrl + '/fixture.html');
  await list.evaluate(() => localStorage.clear());
  await list.reload();
  const rowCount = await list.locator('#rows tr').count();
  details.initialRowCount = rowCount;
  if (rowCount !== 5) failures.push('expected 5 rows at start, got ' + rowCount);
  const before = await list.locator('#rows tr .title').allTextContents();
  details.titlesBefore = before;
  const [detail] = await Promise.all([
    context.waitForEvent('page'),
    list.locator('#rows tr:nth-child(2) a').click(),
  ]);
  await detail.waitForLoadState('domcontentloaded');
  const detailTitle = await detail.inputValue('#title');
  details.detailInitialTitle = detailTitle;
  if (detailTitle !== 'Problem Two') failures.push('detail tab opened with wrong title: ' + detailTitle);
  await detail.fill('#title', 'Edited Title Two');
  await detail.click('#save');
  await detail.waitForSelector('#saved:not(:empty)', { timeout: 10000 });
  await detail.close();
  await list.click('#refresh');
  const after = await list.locator('#rows tr .title').allTextContents();
  details.titlesAfter = after;
  if (after[1] !== 'Edited Title Two') failures.push('list still shows old title for problem 2: ' + after[1]);
  for (const i of [0, 2, 3, 4]) {
    if (after[i] !== before[i]) failures.push('row ' + (i + 1) + ' changed unexpectedly');
  }
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
