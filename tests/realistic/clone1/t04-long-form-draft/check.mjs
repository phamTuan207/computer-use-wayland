// t04-long-form-draft check. Verifies conditional fields per problem
// type, saves a draft, reloads, asserts the draft is restored, then
// submits successfully. Prints one JSON result line. Exit 0 on pass,
// 1 on fail.
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
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  details.batchExtraVisible = await page.isVisible('#interactive-fields');
  if (details.batchExtraVisible) failures.push('interactive fields visible for batch type');
  await page.selectOption('#ptype', 'interactive');
  details.interactiveExtraVisible = await page.isVisible('#interactive-fields');
  if (!details.interactiveExtraVisible) failures.push('interactive fields hidden for interactive type');
  await page.fill('#title', 'Interactive Guessing Problem');
  await page.fill('#interactor', 'Judge answers each query.');
  await page.fill('#qlimit', '30');
  await page.fill('#statement', 'Guess the hidden number.');
  await page.click('#save-draft');
  await page.waitForSelector('#draft-msg:not(:empty)', { timeout: 10000 });
  await page.reload();
  const restored = {
    title: await page.inputValue('#title'),
    interactor: await page.inputValue('#interactor'),
    qlimit: await page.inputValue('#qlimit'),
    statement: await page.inputValue('#statement'),
  };
  details.restored = restored;
  if (restored.title !== 'Interactive Guessing Problem') failures.push('draft title lost after reload');
  if (restored.interactor !== 'Judge answers each query.') failures.push('draft interactor lost after reload');
  if (restored.qlimit !== '30') failures.push('draft query limit lost after reload');
  if (restored.statement !== 'Guess the hidden number.') failures.push('draft statement lost after reload');
  await page.click('#submit');
  await page.waitForSelector('#result:not(:empty)', { timeout: 10000 });
  const result = (await page.textContent('#result')) || '';
  details.result = result;
  if (!result.includes('Interactive Guessing Problem')) failures.push('success message missing title');
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
