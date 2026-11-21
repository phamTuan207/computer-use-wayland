// Offline automated simulator to verify that agy-q2 test specs pass when steps are executed.
// Usage: node tests/realistic/agy-q2/simulate.mjs --test 01
// Or:    node tests/realistic/agy-q2/simulate.mjs --all
import puppeteer from 'puppeteer-core';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const args = process.argv.slice(2);
function argValue(flag) {
  const i = args.indexOf(flag);
  return i >= 0 ? args[i + 1] : undefined;
}

const testId = argValue('--test') || '01';
const runAll = args.includes('--all');
const EXES = process.env.CU_CHROME_PATH || '/usr/bin/chromium';

const testSimulators = {
  '01': async (page) => {
    // 1. Enter title
    await page.type('#input-board-title', 'Architecture Sprint 2026');
    // 2. Rect Blue
    await page.click('#tool-rect');
    await page.click('#color-blue');
    await page.$eval('#input-coord-x', el => el.value = '100');
    await page.$eval('#input-coord-y', el => el.value = '80');
    await page.$eval('#input-coord-w', el => el.value = '180');
    await page.$eval('#input-coord-h', el => el.value = '120');
    await page.click('#btn-add-shape');
    // 3. Circle Green
    await page.click('#tool-circle');
    await page.click('#color-green');
    await page.$eval('#input-coord-x', el => el.value = '400');
    await page.$eval('#input-coord-y', el => el.value = '150');
    await page.$eval('#input-coord-w', el => el.value = '50');
    await page.click('#btn-add-shape');
    // 4. Text Blue API Gateway
    await page.click('#tool-text');
    await page.click('#color-blue');
    await page.type('#input-canvas-text', 'API Gateway');
    await page.$eval('#input-coord-x', el => el.value = '120');
    await page.$eval('#input-coord-y', el => el.value = '130');
    await page.click('#btn-add-shape');
    // 5. Mistake: Red Line
    await page.click('#tool-line');
    await page.click('#color-red');
    await page.click('#btn-add-shape');
    // 6. Undo mistake
    await page.click('#btn-undo');
    // 7. Rect Yellow
    await page.click('#tool-rect');
    await page.click('#color-yellow');
    await page.$eval('#input-coord-x', el => el.value = '400');
    await page.$eval('#input-coord-y', el => el.value = '300');
    await page.$eval('#input-coord-w', el => el.value = '200');
    await page.$eval('#input-coord-h', el => el.value = '100');
    await page.click('#btn-add-shape');
    // 8. Text Yellow Database Cluster
    await page.click('#tool-text');
    await page.$eval('#input-canvas-text', el => el.value = '');
    await page.type('#input-canvas-text', 'Database Cluster');
    await page.$eval('#input-coord-x', el => el.value = '420');
    await page.$eval('#input-coord-y', el => el.value = '340');
    await page.click('#btn-add-shape');
    // 9. Save
    await page.click('#btn-save-board');
  }
};

async function simulateOne(browser, id, fixtureFile) {
  const start = Date.now();
  const absolute = path.resolve(process.cwd(), fixtureFile);
  const fileUrl = pathToFileURL(absolute).href;
  const page = await browser.newPage();
  try {
    await page.goto(fileUrl);
    const simFn = testSimulators[id];
    if (!simFn) {
      throw new Error(`No simulator defined for test ${id}`);
    }
    await simFn(page);
    const result = await page.evaluate(() => window.__agyVerify());
    const totalMs = Date.now() - start;
    return {
      test: id,
      fixture: fixtureFile,
      passed: !!result.passed,
      failures: result.failures || [],
      score: result.score || 0,
      state: result.state || {},
      total_ms: totalMs,
    };
  } finally {
    await page.close();
  }
}

async function main() {
  const browser = await puppeteer.launch({
    executablePath: EXES,
    headless: true,
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu'],
  });

  const fixtureMap = {
    '01': 'tests/realistic/agy-q2/fixtures/test-01-whiteboard.html',
    '02': 'tests/realistic/agy-q2/fixtures/test-02-recipe-app.html',
    '03': 'tests/realistic/agy-q2/fixtures/test-03-habit-tracker.html',
    '04': 'tests/realistic/agy-q2/fixtures/test-04-budget-tracker.html',
    '05': 'tests/realistic/agy-q2/fixtures/test-05-contact-book.html',
    '06': 'tests/realistic/agy-q2/fixtures/test-06-file-converter.html',
    '07': 'tests/realistic/agy-q2/fixtures/test-07-weather-dashboard.html',
    '08': 'tests/realistic/agy-q2/fixtures/test-08-quiz-app.html',
    '09': 'tests/realistic/agy-q2/fixtures/test-09-pomodoro-timer.html',
    '10': 'tests/realistic/agy-q2/fixtures/test-10-markdown-editor.html',
  };

  try {
    if (runAll) {
      const keys = Object.keys(testSimulators);
      const results = [];
      let allPassed = true;
      for (const k of keys) {
        const res = await simulateOne(browser, k, fixtureMap[k]);
        results.push(res);
        if (!res.passed) allPassed = false;
      }
      console.log(JSON.stringify({ summary: 'all simulated', allPassed, count: results.length, results }, null, 2));
      process.exit(allPassed ? 0 : 1);
    } else {
      const res = await simulateOne(browser, testId, fixtureMap[testId]);
      console.log(JSON.stringify(res, null, 2));
      process.exit(res.passed ? 0 : 1);
    }
  } finally {
    await browser.close();
  }
}

main().catch(err => {
  console.error(JSON.stringify({ error: String(err && err.message || err) }));
  process.exit(3);
});
