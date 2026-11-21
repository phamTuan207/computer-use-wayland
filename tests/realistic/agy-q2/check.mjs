// Offline automated checker for tests/realistic/agy-q2 suite.
// Run: node tests/realistic/agy-q2/check.mjs --fixture <fixtures/test-XX-....html> --test <XX>
// Or:  node tests/realistic/agy-q2/check.mjs --all
import puppeteer from 'puppeteer-core';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const args = process.argv.slice(2);
function argValue(flag) {
  const i = args.indexOf(flag);
  return i >= 0 ? args[i + 1] : undefined;
}

const fixturePath = argValue('--fixture');
const testId = argValue('--test');
const runAll = args.includes('--all');

if (!fixturePath && !runAll) {
  console.error('Usage: node tests/realistic/agy-q2/check.mjs --fixture <path> --test <id>');
  console.error('       node tests/realistic/agy-q2/check.mjs --all');
  process.exit(2);
}

const EXES = process.env.CU_CHROME_PATH || '/usr/bin/chromium';

async function verifyOneFixture(browser, relPath, id) {
  const start = Date.now();
  const absolute = path.resolve(process.cwd(), relPath);
  const fileUrl = pathToFileURL(absolute).href;
  const page = await browser.newPage();
  try {
    await page.goto(fileUrl);
    await page.waitForFunction('typeof window.__agyVerify === "function"', { timeout: 15000 });
    const result = await page.evaluate(() => {
      return window.__agyVerify();
    });
    const totalMs = Date.now() - start;
    return {
      test: id,
      fixture: relPath,
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

  const allFixtures = [
    { id: '01', path: 'tests/realistic/agy-q2/fixtures/test-01-whiteboard.html' },
    { id: '02', path: 'tests/realistic/agy-q2/fixtures/test-02-recipe-app.html' },
    { id: '03', path: 'tests/realistic/agy-q2/fixtures/test-03-habit-tracker.html' },
    { id: '04', path: 'tests/realistic/agy-q2/fixtures/test-04-budget-tracker.html' },
    { id: '05', path: 'tests/realistic/agy-q2/fixtures/test-05-contact-book.html' },
    { id: '06', path: 'tests/realistic/agy-q2/fixtures/test-06-file-converter.html' },
    { id: '07', path: 'tests/realistic/agy-q2/fixtures/test-07-weather-dashboard.html' },
    { id: '08', path: 'tests/realistic/agy-q2/fixtures/test-08-quiz-app.html' },
    { id: '09', path: 'tests/realistic/agy-q2/fixtures/test-09-pomodoro-timer.html' },
    { id: '10', path: 'tests/realistic/agy-q2/fixtures/test-10-markdown-editor.html' },
  ];

  try {
    if (runAll) {
      const results = [];
      let allPassed = true;
      for (const item of allFixtures) {
        const res = await verifyOneFixture(browser, item.path, item.id);
        results.push(res);
        if (!res.passed) allPassed = false;
      }
      console.log(JSON.stringify({ summary: 'all tests evaluated', allPassed, count: results.length, results }, null, 2));
      process.exit(allPassed ? 0 : 1);
    } else {
      const res = await verifyOneFixture(browser, fixturePath, testId || 'custom');
      console.log(JSON.stringify(res, null, 2));
      process.exit(res.passed ? 0 : 1);
    }
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error(JSON.stringify({ error: String(err && err.message || err), timestamp: Date.now() }));
  process.exit(3);
});
