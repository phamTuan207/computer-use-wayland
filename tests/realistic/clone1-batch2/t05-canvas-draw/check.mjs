// t05-canvas-draw check. Draws with pen and eraser, checks real pixels,
// undo and redo, background fill, PNG save, clear, and brush width.
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
  const box = await page.locator('#board').boundingBox();
  const pixel = (x, y) => page.evaluate(([px, py]) => window.__pixel(px, py), [x, y]);
  const count = () => page.evaluate(() => Number(document.getElementById('strokeCount').textContent));
  async function draw(x1, y1, x2, y2) {
    await page.mouse.move(box.x + x1, box.y + y1);
    await page.mouse.down();
    const n = 12;
    for (let i = 1; i <= n; i++) {
      await page.mouse.move(box.x + x1 + ((x2 - x1) * i) / n, box.y + y1 + ((y2 - y1) * i) / n);
    }
    await page.mouse.up();
    await page.waitForTimeout(150);
  }
  const isWhite = (p) => p[0] > 250 && p[1] > 250 && p[2] > 250;
  const isRed = (p) => p[0] > 200 && p[1] < 80 && p[2] < 80;
  const isBlue = (p) => p[2] > 200 && p[0] < 80 && p[1] < 80;
  const isGreen = (p) => p[1] > 100 && p[0] < 100 && p[2] < 100;
  const isBlack = (p) => p[0] < 40 && p[1] < 40 && p[2] < 40;
  check(isWhite(await pixel(10, 10)), 'canvas should start blank white'); step('check canvas starts blank');
  await page.click('.swatch[data-color="#ff0000"]'); step('pick red pen');
  await page.selectOption('#brushSize', '8'); step('pick brush size 8');
  await draw(50, 100, 300, 100); step('draw red line');
  check(isRed(await pixel(175, 100)), 'red line pixel wrong: ' + JSON.stringify(await pixel(175, 100))); step('check red pixel on line');
  check((await count()) === 1, 'stroke count should be 1'); step('check stroke count is 1');
  await page.click('.swatch[data-color="#0000ff"]'); step('pick blue pen');
  await draw(50, 200, 300, 200); step('draw blue line');
  check(isBlue(await pixel(175, 200)), 'blue line pixel wrong'); step('check blue pixel on line');
  check((await count()) === 2, 'stroke count should be 2'); step('check stroke count is 2');
  await page.click('#undoBtn'); step('press undo');
  check((await count()) === 1, 'stroke count should be 1 after undo'); step('check count is 1 after undo');
  check(isWhite(await pixel(175, 200)), 'blue line should be gone after undo'); step('check blue line gone after undo');
  await page.click('#redoBtn'); step('press redo');
  check((await count()) === 2, 'stroke count should be 2 after redo'); step('check count is 2 after redo');
  check(isBlue(await pixel(175, 200)), 'blue line should be back after redo'); step('check blue line back after redo');
  await page.click('#eraserBtn'); step('pick eraser');
  await draw(160, 100, 190, 100); step('erase middle of red line');
  check(isWhite(await pixel(175, 100)), 'erased pixel should be white'); step('check erased pixel is white');
  check(isRed(await pixel(80, 100)), 'untouched red pixel should stay red'); step('check untouched red pixel stays red');
  await page.click('.swatch[data-color="#008000"]'); step('pick green for fill');
  await page.click('#fillBtn'); step('fill background green');
  check(isGreen(await pixel(5, 5)), 'corner pixel should be green after fill'); step('check corner is green after fill');
  await page.click('#saveBtn'); step('save PNG');
  check(await page.isVisible('#preview'), 'preview image should show after save'); step('check preview shown');
  const src = await page.evaluate(() => document.getElementById('preview').src);
  check(src.startsWith('data:image/png') && src.length > 1000, 'preview should be a PNG data URL, length ' + src.length); step('check preview is a PNG data URL');
  details = { pngDataUrlLength: src.length };
  const href = await page.evaluate(() => document.getElementById('downloadLink').href);
  check(href.startsWith('data:image/png'), 'download link should point at the PNG'); step('check download link set');
  await page.click('#clearBtn'); step('clear canvas');
  check((await count()) === 0, 'stroke count should be 0 after clear'); step('check count is 0 after clear');
  check(isWhite(await pixel(10, 10)), 'canvas should be white after clear'); step('check canvas white after clear');
  await page.click('.swatch[data-color="#000000"]'); step('pick black pen');
  await page.selectOption('#brushSize', '20'); step('pick brush size 20');
  await draw(50, 300, 300, 300); step('draw thick black line');
  check(isBlack(await pixel(175, 308)), 'pixel 8 px off center should be black with size 20'); step('check thick line covers 8 px off center');
  check((await count()) === 1, 'stroke count should be 1'); step('check final stroke count is 1');
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
