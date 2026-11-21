// t04-kanban-drag check. Drags cards between columns and reorders them,
// adds and deletes cards, filters, and checks persistence after reload.
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
  await page.evaluate(() => localStorage.removeItem('kanban'));
  await page.reload(); step('clear saved board and reload');
  const count = (col) => page.evaluate((c) => {
    return document.querySelectorAll('#cards-' + c + ' .card').length;
  }, col);
  const titles = (col) => page.evaluate((c) => {
    return [...document.querySelectorAll('#cards-' + c + ' .card strong')].map((e) => e.textContent);
  }, col);
  check((await count('todo')) === 3, 'todo should start with 3'); step('check starting counts');
  check((await count('doing')) === 2, 'doing should start with 2'); step('check doing starts with 2');
  check((await count('done')) === 1, 'done should start with 1'); step('check done starts with 1');
  await page.locator('[data-id="c1"]').dragTo(page.locator('#cards-doing')); step('drag bug card Todo to Doing');
  await page.waitForTimeout(300);
  check((await count('todo')) === 2, 'todo should be 2 after drag'); step('check Todo is 2 after drag');
  check((await count('doing')) === 3, 'doing should be 3 after drag'); step('check Doing is 3 after drag');
  check((await titles('doing')).includes('Fix login redirect bug'), 'dragged card missing in Doing'); step('check dragged card is in Doing');
  const status1 = (await page.textContent('#status')) || '';
  check(status1.includes('to doing'), 'status should say moved to doing, got: ' + status1); step('check move status text');
  await page.locator('[data-id="c1"]').dragTo(page.locator('[data-id="c4"]')); step('drag card above another to reorder');
  await page.waitForTimeout(300);
  const doingOrder = await titles('doing');
  check(doingOrder[0] === 'Fix login redirect bug', 'reordered card should be first, got: ' + JSON.stringify(doingOrder)); step('check reorder put card first');
  await page.locator('[data-id="c1"]').dragTo(page.locator('#cards-done')); step('drag card to Done');
  await page.waitForTimeout(300);
  check((await count('done')) === 2, 'done should be 2'); step('check Done is 2');
  check((await titles('done')).includes('Fix login redirect bug'), 'card missing in Done'); step('check card is in Done');
  await page.fill('#newTitle', 'Fix mobile menu overlap'); step('type new card title');
  await page.selectOption('#newTag', 'bug'); step('pick bug tag');
  await page.click('#addBtn'); step('add the new card');
  check((await count('todo')) === 3, 'todo should be 3 after add'); step('check Todo is 3 after add');
  check((await titles('todo')).includes('Fix mobile menu overlap'), 'new card missing'); step('check new card appears');
  await page.fill('#filter', 'bug'); step('filter by bug');
  await page.waitForTimeout(200);
  const info = (await page.textContent('#filterInfo')) || '';
  check(info.includes('Showing 3 of 7'), 'filter info wrong: ' + info); step('check filter shows 3 of 7');
  await page.fill('#filter', ''); step('clear filter');
  await page.waitForTimeout(200);
  check((await count('todo')) === 3, 'todo should be 3 after clearing filter'); step('check counts back after filter clear');
  await page.locator('[data-id="c2"] .del').click(); step('delete a card');
  check((await count('todo')) === 2, 'todo should be 2 after delete'); step('check Todo is 2 after delete');
  const status2 = (await page.textContent('#status')) || '';
  check(status2.includes('Deleted'), 'status should say deleted, got: ' + status2); step('check delete status text');
  await page.reload(); step('reload page');
  check((await count('todo')) === 2, 'todo should still be 2 after reload'); step('check Todo persists after reload');
  check((await count('doing')) === 2, 'doing should still be 2 after reload'); step('check Doing persists after reload');
  check((await count('done')) === 2, 'done should still be 2 after reload'); step('check Done persists after reload');
  check((await titles('done')).includes('Fix login redirect bug'), 'moved card lost after reload'); step('check moved card still in Done');
  details = { todo: await count('todo'), doing: await count('doing'), done: await count('done') };
  await page.locator('[data-id="c3"]').dragTo(page.locator('#cards-done')); step('drag last Todo feature card to Done');
  await page.waitForTimeout(300);
  await page.locator('.card:has-text("Fix mobile menu overlap")').dragTo(page.locator('#cards-done')); step('drag new bug card to Done');
  await page.waitForTimeout(300);
  check((await count('todo')) === 0, 'todo should be empty'); step('check Todo is empty');
  const empty = (await page.textContent('#cards-todo')) || '';
  check(empty.includes('No cards'), 'empty column should say No cards'); step('check empty column message');
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
