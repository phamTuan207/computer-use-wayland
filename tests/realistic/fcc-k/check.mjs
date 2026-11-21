// Offline automated checker for tests/realistic/fcc-k.
// Run: node tests/realistic/fcc-k/check.mjs --fixture <fixtures/test-XX-....html> --test <XX>
// Launches headless chromium offline, opens the local fixture via file://, and
// calls window.__fcckVerify(). Prints JSON verdict. No network, no external
// sites, no GUI input.
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

if (!fixturePath) {
  console.error('usage: node tests/realistic/fcc-k/check.mjs --fixture <path> --test <id>');
  process.exit(2);
}

const EXES = process.env.CU_CHROME_PATH || '/usr/bin/chromium';

async function main() {
  const start = Date.now();
  const absolute = path.resolve(process.cwd(), fixturePath);
  const fileUrl = pathToFileURL(absolute).href;
  const browser = await puppeteer.launch({
    executablePath: EXES,
    headless: true,
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu'],
  });
  const page = await browser.newPage();
  await page.goto(fileUrl);
  await page.waitForFunction('!!(window.__fcckVerify)', { timeout: 15000 });
  const result = await page.evaluate(() => {
    const out = window.__fcckVerify();
    return out;
  });
  const totalMs = Date.now() - start;
  console.log(JSON.stringify({ test: testId, fixture: fixturePath, passed: !!result.passed, failures: result.failures || [], score: result.score || 0, state: result.state || {}, total_ms: totalMs }, null, 2));
  await browser.close();
  process.exit(result.passed ? 0 : 1);
}

main().catch((e) => {
  console.error(JSON.stringify({ error: String(e && e.message || e), total_ms: Date.now() }));
  process.exit(3);
});
