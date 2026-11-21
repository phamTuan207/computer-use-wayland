// t02-upload-multi-error check. Uploads two small files and one 100 KB
// file, expects exactly the large one to fail, removes it, retries, and
// asserts the final confirmation lists only the two small files.
// Prints one JSON result line. Exit 0 on pass, 1 on fail.
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
  const small1 = path.join(tmp, 't02-a.txt');
  const small2 = path.join(tmp, 't02-b.txt');
  const large = path.join(tmp, 't02-big.txt');
  fs.writeFileSync(small1, 'test one\n');
  fs.writeFileSync(small2, 'test two\n');
  fs.writeFileSync(large, 'x'.repeat(100 * 1024));
  details.files = ['t02-a.txt', 't02-b.txt', 't02-big.txt'];

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
  await page.setInputFiles('#files', [small1, small2, large]);
  await page.click('#upload');
  await page.waitForFunction(
    () => document.querySelectorAll('#rows .err').length === 1,
    { timeout: 10000 }
  );
  const rowsText = (await page.textContent('#rows')) || '';
  details.rowsAfterFirstUpload = rowsText.replace(/\s+/g, ' ').trim();
  if (!rowsText.includes('64 KB limit')) failures.push('failed row does not mention the 64 KB limit');
  if ((rowsText.match(/ok/g) || []).length !== 2) failures.push('expected exactly two ok rows after first upload');
  await page.click('#remove-failed');
  await page.click('#retry');
  await page.waitForSelector('#result:not(:empty)', { timeout: 10000 });
  const result = (await page.textContent('#result')) || '';
  details.finalResult = result;
  if (!result.includes('t02-a.txt') || !result.includes('t02-b.txt')) {
    failures.push('final confirmation missing a small file');
  }
  if (result.includes('t02-big.txt')) failures.push('final confirmation wrongly lists the large file');
  for (const f of [small1, small2, large]) fs.unlinkSync(f);
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
