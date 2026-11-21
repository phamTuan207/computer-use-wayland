// t10-login-upload-download check. Logs in with a demo access code,
// uploads a 4-case test data file, asserts the PASS verdict, downloads
// the report, and verifies the report names the file, states 4 cases,
// and states PASS. Prints one JSON result line. Exit 0 on pass, 1 on fail.
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
  const tmpFile = path.join(os.tmpdir(), 't10-data.txt');
  fs.writeFileSync(tmpFile, 'case one\ncase two\ncase three\ncase four\n');
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
  await page.fill('#code', 'CODE-2026-ABCD');
  await page.click('#login-btn');
  await page.waitForSelector('#work:visible', { timeout: 10000 });
  await page.setInputFiles('#file', tmpFile);
  await page.click('#judge');
  await page.waitForSelector('#verdict:not(:empty)', { timeout: 10000 });
  details.verdict = await page.textContent('#verdict');
  if (details.verdict !== 'Judged: 4 cases, PASS.') {
    failures.push('verdict wrong: ' + details.verdict);
  }
  const download = await Promise.all([
    page.waitForEvent('download', { timeout: 10000 }),
    page.click('#download'),
  ]).then(([d]) => d);
  const reportPath = path.join(os.tmpdir(), 't10-report.txt');
  await download.saveAs(reportPath);
  const report = fs.readFileSync(reportPath, 'utf8');
  details.report = report;
  if (!report.includes('t10-data.txt')) failures.push('report does not name the uploaded file');
  if (!report.includes('Cases: 4')) failures.push('report states wrong case count');
  if (!report.includes('Verdict: PASS')) failures.push('report does not state PASS');
  fs.unlinkSync(tmpFile);
  fs.unlinkSync(reportPath);
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
