// t09-upload-metadata check. Expects an empty submit and a .png file
// to be rejected, then a valid title plus a .txt file to succeed with
// a problem ID. Prints one JSON result line. Exit 0 on pass, 1 on fail.
import fs from 'node:fs';
import os from 'node:os';
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
  const tmp = os.tmpdir();
  const txtFile = path.join(tmp, 't09-statement.txt');
  const pngFile = path.join(tmp, 't09-statement.png');
  fs.writeFileSync(txtFile, 'Statement text.\n');
  fs.writeFileSync(pngFile, 'not really an image');
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
  await page.waitForSelector('#error:not(:empty)', { timeout: 10000 });
  details.emptyError = await page.textContent('#error');
  if (!details.emptyError.includes('Title is required.')) failures.push('empty submit missing title error');
  if (!details.emptyError.includes('Statement file is required.')) failures.push('empty submit missing file error');
  await page.fill('#title', 'Metadata Problem');
  await page.setInputFiles('#file', pngFile);
  await page.click('#submit');
  await page.waitForFunction(
    () => document.getElementById('error').textContent.includes('Only .txt files'),
    { timeout: 10000 }
  );
  details.pngError = await page.textContent('#error');
  await page.setInputFiles('#file', txtFile);
  await page.click('#submit');
  await page.waitForSelector('#result:not(:empty)', { timeout: 10000 });
  const result = (await page.textContent('#result')) || '';
  details.result = result;
  if (!result.includes('P-1042')) failures.push('success message missing problem ID P-1042');
  if (!result.includes('Metadata Problem')) failures.push('success message missing title');
  if (!result.includes('t09-statement.txt')) failures.push('success message missing file name');
  fs.unlinkSync(txtFile);
  fs.unlinkSync(pngFile);
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
