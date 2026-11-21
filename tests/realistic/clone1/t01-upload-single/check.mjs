// t01-upload-single check. Uploads a temp statement file through the
// fixture form and asserts name, size, and checksum in the confirmation.
// Prints one JSON result line. Exit 0 on pass, 1 on fail.
// Usage: node check.mjs  (FIXTURE_BASE_URL optional, see README)
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
let details = {};

function checksum(buf) {
  let h = 0;
  for (const b of buf) {
    h = ((h * 31) + b) >>> 0;
  }
  return h.toString(16).padStart(8, '0');
}

let browser = null;
let closeServer = null;
try {
  const content = 'polygon statement\nline two\nline three\n';
  const tmpFile = path.join(os.tmpdir(), 't01-statement.txt');
  fs.writeFileSync(tmpFile, content);
  const expectedSum = checksum(Buffer.from(content, 'utf8'));
  const expectedSize = Buffer.byteLength(content, 'utf8');
  details = { file: 't01-statement.txt', size: expectedSize, checksum: expectedSum };

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
  await page.fill('#title', 'Sample Problem');
  await page.setInputFiles('#file', tmpFile);
  await page.click('#upload');
  await page.waitForSelector('#result:not(:empty)', { timeout: 10000 });
  const text = (await page.textContent('#result')) || '';
  details.confirmation = text;
  if (!text.includes('t01-statement.txt')) failures.push('confirmation missing file name');
  if (!text.includes(String(expectedSize) + ' bytes')) failures.push('confirmation missing size');
  if (!text.includes(expectedSum)) failures.push('confirmation missing checksum');
  if (!text.includes('Sample Problem')) failures.push('confirmation missing title');
  fs.unlinkSync(tmpFile);
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
