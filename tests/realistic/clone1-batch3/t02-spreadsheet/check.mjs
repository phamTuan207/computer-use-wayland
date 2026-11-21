// t02-spreadsheet check. Fills numbers and formulas into a demo
// spreadsheet grid and asserts the real computed values in the DOM:
// SUM, AVERAGE, arithmetic, chained formulas, text ignored by SUM,
// invalid formulas showing #ERR, and recompute after edits.
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
  const val = (cell) => page.inputValue('#cell-' + cell);
  const set = (cell, text) => page.fill('#cell-' + cell, text);
  const expect = async (cell, wanted, what) => {
    const got = await val(cell);
    if (got !== wanted) failures.push(what + ': ' + cell + ' is "' + got + '", want "' + wanted + '"');
    else details[cell] = got;
  };

  await set('A1', '10');
  await set('A2', '20');
  await set('A3', '30');
  await set('C1', '=SUM(A1:A3)');
  await expect('C1', '60', 'SUM after first fill');
  await set('C2', '=AVERAGE(A1:A3)');
  await expect('C2', '20', 'AVERAGE after first fill');
  await set('B1', '2');
  await set('D1', '=A1*B1');
  await expect('D1', '20', 'multiply after B1 set');
  await set('A1', '40');
  await expect('C1', '90', 'SUM after A1 edit');
  await expect('C2', '30', 'AVERAGE after A1 edit');
  await expect('D1', '80', 'multiply after A1 edit');
  await set('B2', '=A1+A2');
  await expect('B2', '60', 'addition formula');
  await set('D4', '=C1/2');
  await expect('D4', '45', 'chained formula over C1');
  await set('D2', '=FOO(1)');
  await expect('D2', '#ERR', 'unknown function');
  await set('D3', '=A9');
  await expect('D3', '#ERR', 'reference outside the grid');
  await set('A5', 'hello');
  await set('C3', '=SUM(A1:A5)');
  await expect('C3', '90', 'SUM ignores text cell');
  await set('A4', '5');
  await expect('C3', '95', 'SUM after A4 added');
  await expect('C1', '90', 'SUM range still correct after A4');
  await set('B1', '');
  await expect('D1', '0', 'multiply by cleared cell is 0');
  await set('A6', '2.5');
  await set('C4', '=A6*2');
  await expect('C4', '5', 'decimal multiply');
  await set('D5', '=A3/A2');
  await expect('D5', '1.5', 'division');
  await set('D6', '=A3/0');
  await expect('D6', '#ERR', 'division by zero');
  await set('A3', '10');
  await expect('C1', '70', 'SUM after A3 edit');
  await expect('D5', '0.5', 'division after A3 edit');
  const status = await page.textContent('#status');
  if (status !== 'Recalculated.') failures.push('status wrong: ' + status);
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
