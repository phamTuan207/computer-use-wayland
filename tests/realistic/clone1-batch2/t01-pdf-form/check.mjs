// t01-pdf-form check. Fills a 3-page form like a PDF form, hits two
// validation errors midway, signs with the mouse, submits, and checks
// the confirmation and the saved record after reload.
// Prints one JSON result line. Exit 0 on pass, 1 on fail.
// Usage: node check.mjs  (FIXTURE_BASE_URL optional, see README)
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { launchBrowser, nowIso } from '../lib/browser.mjs';
import { serveDir } from '../lib/server.mjs';

const testDir = path.dirname(fileURLToPath(import.meta.url));
const testName = path.basename(testDir);
const startedAt = nowIso();
const started = Date.now();
const failures = [];
const steps = [];
let details = {};
let stepCount = 0;
function step(name) { stepCount += 1; steps.push(stepCount + '. ' + name); }
function check(cond, msg) { if (!cond) failures.push(msg); }

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
  await page.goto(fixtureUrl); step('open fixture');
  check((await page.title()).includes('Relief Application'), 'title missing'); step('check title');
  await page.fill('#fullName', 'Ada Lovelace'); step('fill full name');
  await page.fill('#idNum', '123456789'); step('fill ID number');
  await page.fill('#email', 'not-an-email'); step('fill invalid email');
  await page.click('#next1'); step('try next page with bad email');
  const err1 = (await page.textContent('#errors1')) || '';
  check(err1.includes('email is not valid'), 'expected email error, got: ' + err1); step('expect email error');
  check(await page.isVisible('#page1'), 'should stay on page 1 after error'); step('confirm still on page 1');
  await page.fill('#email', 'ada@example.com'); step('fix email');
  await page.click('#next1'); step('go to page 2');
  check(await page.isVisible('#page2'), 'page 2 not shown'); step('confirm page 2 shown');
  await page.fill('#address', '12 Analytical Way'); step('fill address');
  await page.fill('#city', 'London'); step('fill city');
  await page.fill('#postcode', 'E1 6AN'); step('fill postcode');
  await page.fill('#income', '2400'); step('fill income');
  await page.selectOption('#employment', 'employed'); step('select employment');
  await page.check('#decl1'); step('check declaration 1');
  await page.click('#next2'); step('try next page without declaration 2');
  const err2 = (await page.textContent('#errors2')) || '';
  check(err2.includes('declaration 2'), 'expected declaration 2 error, got: ' + err2); step('expect declaration 2 error');
  await page.check('#decl2'); step('check declaration 2');
  await page.click('#next2'); step('go to page 3');
  check(await page.isVisible('#page3'), 'page 3 not shown'); step('confirm page 3 shown');
  await page.click('#submit'); step('try submit without signature');
  const err3 = (await page.textContent('#errors3')) || '';
  check(err3.includes('signature is required'), 'expected signature error, got: ' + err3); step('expect signature error');
  const box = await page.locator('#sig').boundingBox();
  await page.mouse.move(box.x + 60, box.y + 70);
  await page.mouse.down();
  for (let i = 0; i < 10; i++) await page.mouse.move(box.x + 60 + i * 30, box.y + 70 + (i % 2 ? -18 : 18));
  await page.mouse.up(); step('draw signature on canvas');
  await page.click('#submit'); step('submit application');
  await page.waitForSelector('#confirmation', { state: 'visible', timeout: 10000 }); step('wait for confirmation');
  const appId = (await page.textContent('#appId')) || '';
  check(/^Application ID: RF-[0-9A-F]{6}$/.test(appId.trim()), 'bad application id: ' + appId); step('check application ID format');
  const summary = (await page.textContent('#summary')) || '';
  check(summary.includes('Ada Lovelace'), 'summary missing name'); step('check summary has name');
  check(summary.includes('2400'), 'summary missing income'); step('check summary has income');
  check(summary.includes('ada@example.com'), 'summary missing email'); step('check summary has email');
  details = { appId: appId.trim(), steps: stepCount };
  await page.reload(); step('reload page');
  check(await page.isVisible('#confirmation'), 'confirmation should persist after reload'); step('confirm record persists after reload');
  const appId2 = (await page.textContent('#appId')) || '';
  check(appId2.trim() === appId.trim(), 'application id changed after reload'); step('check same ID after reload');
  await page.click('#newApp'); step('start a new application');
  check(await page.isVisible('#page1'), 'page 1 not shown after reset'); step('confirm form reset to page 1');
  check(stepCount >= 15 && stepCount <= 40, 'step count ' + stepCount + ' outside 15-40');
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
  steps,
  started_at: startedAt,
  finished_at: nowIso(),
  elapsed_ms: Date.now() - started,
};
console.log(JSON.stringify(result));
process.exit(result.pass ? 0 : 1);
