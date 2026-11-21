// t08-login-auth check. Rejects a short access code, logs in with a
// valid demo code, does the protected review action, reloads to check
// the session survives, logs out, and asserts the protected page hides.
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
  await page.fill('#code', 'abc');
  await page.click('#login-btn');
  await page.waitForSelector('#error:not(:empty)', { timeout: 10000 });
  details.shortCodeError = await page.textContent('#error');
  details.protectedVisibleAfterShortCode = await page.isVisible('#protected');
  if (details.protectedVisibleAfterShortCode) failures.push('short code logged in');
  await page.fill('#code', 'CODE-2026-ABCD');
  await page.click('#login-btn');
  await page.waitForSelector('#protected:visible', { timeout: 10000 });
  details.welcome = await page.textContent('#welcome');
  await page.click('#review');
  await page.waitForSelector('#review-result:not(:empty)', { timeout: 10000 });
  details.reviewResult = await page.textContent('#review-result');
  if (details.reviewResult !== 'Problem 42 marked reviewed.') {
    failures.push('review action wrong: ' + details.reviewResult);
  }
  await page.reload();
  details.protectedVisibleAfterReload = await page.isVisible('#protected');
  if (!details.protectedVisibleAfterReload) failures.push('session lost on reload');
  await page.click('#logout');
  await page.waitForSelector('#login:visible', { timeout: 10000 });
  details.protectedVisibleAfterLogout = await page.isVisible('#protected');
  if (details.protectedVisibleAfterLogout) failures.push('protected page still visible after logout');
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
