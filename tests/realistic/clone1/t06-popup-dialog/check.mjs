// t06-popup-dialog check. Handles a real alert, an accepted and a
// dismissed confirm, a prompt, a custom modal, and a popup window whose
// form posts a value back to the main page. Prints one JSON result
// line. Exit 0 on pass, 1 on fail.
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
  const page = await context.newPage();
  await page.goto(baseUrl + '/fixture.html');

  page.once('dialog', async (dialog) => {
    await dialog.accept();
  });
  await page.click('#alert-btn');
  await page.waitForFunction(
    () => document.getElementById('out-alert').textContent !== '',
    { timeout: 10000 }
  );
  details.alert = await page.textContent('#out-alert');
  if (details.alert !== 'alert accepted') failures.push('alert outcome wrong: ' + details.alert);

  page.once('dialog', async (dialog) => {
    await dialog.accept();
  });
  await page.click('#confirm-btn');
  await page.waitForFunction(
    () => document.getElementById('out-confirm').textContent === 'confirmed',
    { timeout: 10000 }
  );
  page.once('dialog', async (dialog) => {
    await dialog.dismiss();
  });
  await page.click('#confirm-btn');
  await page.waitForFunction(
    () => document.getElementById('out-confirm').textContent === 'cancelled',
    { timeout: 10000 }
  );
  details.confirmDismissed = await page.textContent('#out-confirm');

  page.once('dialog', async (dialog) => {
    await dialog.accept('Reviewer');
  });
  await page.click('#prompt-btn');
  await page.waitForFunction(
    () => document.getElementById('out-prompt').textContent !== '',
    { timeout: 10000 }
  );
  details.prompt = await page.textContent('#out-prompt');
  if (details.prompt !== 'name: Reviewer') failures.push('prompt outcome wrong: ' + details.prompt);

  await page.click('#modal-btn');
  await page.fill('#note', 'Looks good, publish it.');
  await page.click('#modal-save');
  await page.waitForFunction(
    () => document.getElementById('out-modal').textContent !== '',
    { timeout: 10000 }
  );
  details.modal = await page.textContent('#out-modal');
  if (!details.modal.includes('Looks good, publish it.')) failures.push('modal note not recorded');

  const [popup] = await Promise.all([
    context.waitForEvent('page'),
    page.click('#popup-btn'),
  ]);
  await popup.waitForLoadState('domcontentloaded');
  await popup.fill('#pname', 'Popup Tester');
  await popup.click('#send');
  await page.waitForFunction(
    () => document.getElementById('out-popup').textContent !== '',
    { timeout: 10000 }
  );
  details.popup = await page.textContent('#out-popup');
  if (details.popup !== 'popup name: Popup Tester') failures.push('popup value wrong: ' + details.popup);
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
