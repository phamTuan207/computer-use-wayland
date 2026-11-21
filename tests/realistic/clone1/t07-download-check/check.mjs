// t07-download-check. Downloads the generated CSV, then reads it back
// and asserts the header, the 6-line count, and the checksum shown on
// the page. Prints one JSON result line. Exit 0 on pass, 1 on fail.
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
  const info = (await page.textContent('#info')) || '';
  details.pageInfo = info;
  const expectedSum = (info.match(/checksum ([0-9a-f]{8})/) || [])[1];
  if (!expectedSum) failures.push('page does not show a checksum');
  const download = await Promise.all([
    page.waitForEvent('download', { timeout: 10000 }),
    page.click('#download'),
  ]).then(([d]) => d);
  const tmpFile = path.join(os.tmpdir(), 't07-downloaded.csv');
  await download.saveAs(tmpFile);
  const data = fs.readFileSync(tmpFile);
  const text = data.toString('utf8');
  const lines = text.split('\n').filter((l) => l.length > 0);
  details.lines = lines.length;
  details.firstLine = lines[0] || '';
  details.checksum = checksum(data);
  if (lines[0] !== 'id,input,expected') failures.push('wrong header: ' + lines[0]);
  if (lines.length !== 6) failures.push('expected 6 lines, got ' + lines.length);
  if (expectedSum && details.checksum !== expectedSum) {
    failures.push('checksum mismatch: file ' + details.checksum + ', page ' + expectedSum);
  }
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
