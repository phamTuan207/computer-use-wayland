// t10-dashboard check. Filters, sorts, paginates, selects, exports CSV,
// and checks KPIs and chart totals on a sales dashboard.
// Prints one JSON result line. Exit 0 on pass, 1 on fail.
// Usage: node check.mjs  (FIXTURE_BASE_URL optional, see README)
import fs from 'node:fs';
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
  const kpi = (id) => page.textContent(id);
  const rowCount = () => page.evaluate(() => document.querySelectorAll('#rows tr').length);
  const firstRowId = () => page.evaluate(() => {
    const tr = document.querySelector('#rows tr');
    return tr ? tr.dataset.id : '';
  });
  const firstRowAmount = () => page.evaluate(() => {
    const tr = document.querySelector('#rows tr');
    return tr ? tr.cells[7].textContent : '';
  });
  check((await kpi('#kpiRevenue')) === '$610.39', 'revenue should be $610.39, got ' + (await kpi('#kpiRevenue')));
  check((await kpi('#kpiOrders')) === '12', 'orders should be 12');
  check((await kpi('#kpiAvg')) === '$50.87', 'avg should be $50.87, got ' + (await kpi('#kpiAvg'))); step('check starting KPIs: 610.39, 12 orders, 50.87 avg');
  check((await rowCount()) === 5, 'page 1 should show 5 rows'); step('check page 1 shows 5 rows');
  check((await firstRowId()) === 'A1001', 'first row should be A1001'); step('check first row is A1001');
  await page.selectOption('#statusFilter', 'paid'); step('filter status paid');
  check((await kpi('#kpiRevenue')) === '$437.92', 'paid revenue should be $437.92, got ' + (await kpi('#kpiRevenue')));
  check((await kpi('#kpiOrders')) === '8', 'paid orders should be 8');
  check((await kpi('#kpiAvg')) === '$54.74', 'paid avg should be $54.74, got ' + (await kpi('#kpiAvg'))); step('check paid KPIs: 437.92, 8 orders, 54.74 avg');
  await page.selectOption('#catFilter', 'electronics'); step('filter category electronics too');
  check((await kpi('#kpiRevenue')) === '$369.96', 'paid electronics revenue should be $369.96');
  check((await kpi('#kpiOrders')) === '4', 'paid electronics orders should be 4'); step('check paid electronics: 369.96, 4 orders');
  await page.selectOption('#catFilter', ''); step('clear category filter');
  await page.fill('#search', 'lamp'); step('search for lamp');
  check((await kpi('#kpiOrders')) === '2', 'paid lamp orders should be 2');
  check((await kpi('#kpiRevenue')) === '$49.98', 'paid lamp revenue should be $49.98'); step('check paid lamp: 2 orders, 49.98');
  await page.fill('#search', ''); step('clear search');
  await page.fill('#fromDate', '2026-11-05');
  await page.fill('#toDate', '2026-11-10'); step('set date range Nov 5 to Nov 10');
  check((await kpi('#kpiOrders')) === '3', 'paid orders in range should be 3');
  check((await kpi('#kpiRevenue')) === '$187.97', 'paid revenue in range should be $187.97, got ' + (await kpi('#kpiRevenue'))); step('check date range: 3 orders, 187.97');
  await page.click('#resetBtn'); step('reset filters');
  check((await kpi('#kpiRevenue')) === '$610.39', 'revenue should be back to $610.39'); step('check KPIs back to full set');
  await page.locator('th[data-sort="amount"]').click(); step('sort by amount ascending');
  check((await firstRowAmount()) === '$7.99', 'first row ascending should be $7.99, got ' + (await firstRowAmount())); step('check cheapest first');
  await page.locator('th[data-sort="amount"]').click(); step('sort by amount descending');
  check((await firstRowAmount()) === '$129.99', 'first row descending should be $129.99, got ' + (await firstRowAmount())); step('check priciest first');
  await page.click('#resetBtn'); step('reset to date order');
  await page.click('#nextPage'); step('go to page 2');
  check((await page.textContent('#pageInfo')) === 'Page 2 of 3', 'page info wrong: ' + (await page.textContent('#pageInfo')));
  check((await firstRowId()) === 'A1006', 'page 2 first row should be A1006, got ' + (await firstRowId())); step('check page 2 starts with A1006');
  await page.click('#prevPage'); step('go back to page 1');
  check((await firstRowId()) === 'A1001', 'page 1 first row should be A1001 again'); step('check back on page 1');
  await page.locator('#rows tr[data-id="A1001"] .rowSel').check();
  await page.locator('#rows tr[data-id="A1002"] .rowSel').check(); step('select two rows');
  check(((await page.textContent('#selectedCount')) || '') === '2', 'selected count should be 2'); step('check 2 rows selected');
  await page.check('#selectAll'); step('select all on page');
  check(((await page.textContent('#selectedCount')) || '') === '5', 'selected count should be 5'); step('check 5 rows selected');
  await page.uncheck('#selectAll'); step('deselect all on page');
  check(((await page.textContent('#selectedCount')) || '') === '0', 'selected count should be 0'); step('check 0 rows selected');
  await page.selectOption('#statusFilter', 'paid'); step('filter paid for export');
  const downloadPromise = page.waitForEvent('download', { timeout: 10000 });
  await page.click('#exportBtn'); step('export CSV');
  const download = await downloadPromise;
  const dlPath = await download.path();
  const csv = fs.readFileSync(dlPath, 'utf8');
  const lines = csv.trim().split('\n');
  check(lines[0] === 'id,date,customer,product,category,status,amount', 'CSV header wrong: ' + lines[0]);
  check(lines.length === 9, 'CSV should have header plus 8 rows, got ' + lines.length + ' lines');
  check(csv.includes('A1004,2026-11-05,Dan,Monitor,electronics,paid,129.99'), 'CSV missing the Monitor row'); step('check CSV has header, 8 paid rows, Monitor row');
  details = { csvLines: lines.length };
  const chart = await page.evaluate(() => window.__chart());
  check(Math.abs(chart.electronics - 369.96) < 0.01, 'chart electronics should be 369.96, got ' + chart.electronics);
  check(Math.abs(chart.home - 49.98) < 0.01, 'chart home should be 49.98, got ' + chart.home);
  check(Math.abs(chart.office - 17.98) < 0.01, 'chart office should be 17.98, got ' + chart.office); step('check chart totals for paid filter');
  await page.selectOption('#statusFilter', 'refunded');
  await page.fill('#search', 'zzz'); step('filter to an empty result');
  check(await page.isVisible('#emptyMsg'), 'empty message should show'); step('check empty message shown');
  check((await kpi('#kpiOrders')) === '0', 'orders should be 0 for empty filter'); step('check 0 orders for empty filter');
  await page.click('#resetBtn'); step('reset filters');
  check((await kpi('#kpiOrders')) === '12', 'orders should be back to 12'); step('check 12 orders after reset');
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
