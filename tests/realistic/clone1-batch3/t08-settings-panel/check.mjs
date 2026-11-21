// t08-settings-panel check. Drives a demo settings panel with real
// UI actions: theme select, accent radio, toggles, slider, display
// name, save and reload for persistence, search filter, and reset to
// defaults. Asserts the real DOM state after each step.
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
  const text = (sel) => page.textContent(sel);
  const visibleSections = () => page.$$eval('section', (els) =>
    els.filter((e) => e.style.display !== 'none').map((e) => e.id));
  const expectText = async (sel, wanted, what) => {
    const got = (await text(sel) || '').trim();
    if (got !== wanted) failures.push(what + ': got "' + got + '", want "' + wanted + '"');
  };

  await expectText('#preview-theme', 'Light', 'initial preview theme');
  await expectText('#volume-value', '50', 'initial volume');
  await expectText('#notif-state', 'On', 'initial notifications state');
  await page.selectOption('#theme', 'dark');
  await expectText('#preview-theme', 'Dark', 'preview after dark theme');
  if (!((await page.getAttribute('body', 'class')) || '').includes('dark')) {
    failures.push('body missing dark class after dark theme');
  }
  await page.check('input[name="accent"][value="blue"]');
  const swatch = await page.$eval('#swatch', (el) => el.style.background);
  if (swatch !== 'blue') failures.push('swatch wrong after blue accent: ' + swatch);
  await page.uncheck('#notif-toggle');
  await expectText('#notif-state', 'Off', 'notifications state after toggle off');
  await page.check('#digest-toggle');
  await expectText('#digest-state', 'On', 'digest state after toggle on');
  await page.uncheck('#privacy-toggle');
  await expectText('#privacy-state', 'Off', 'privacy state after toggle off');
  await page.fill('#display-name', 'Demo User');
  await page.click('#volume');
  await page.keyboard.press('Home');
  for (let i = 0; i < 70; i++) await page.keyboard.press('ArrowRight');
  await expectText('#volume-value', '70', 'volume value after slider');
  await page.click('#save-btn');
  await expectText('#toast', 'Settings saved.', 'toast after save');
  await page.reload();
  await expectText('#preview-theme', 'Dark', 'preview theme after reload');
  await expectText('#volume-value', '70', 'volume after reload');
  if ((await page.inputValue('#display-name')) !== 'Demo User') {
    failures.push('display name not persisted after reload');
  }
  await expectText('#notif-state', 'Off', 'notifications state after reload');
  await expectText('#digest-state', 'On', 'digest state after reload');
  await expectText('#privacy-state', 'Off', 'privacy state after reload');
  if (!(await page.isChecked('input[name="accent"][value="blue"]'))) {
    failures.push('blue accent not persisted after reload');
  }
  await page.fill('#search', 'theme');
  let shown = await visibleSections();
  if (JSON.stringify(shown) !== JSON.stringify(['section-appearance'])) {
    failures.push('search theme shows wrong sections: ' + JSON.stringify(shown));
  }
  await page.fill('#search', '');
  shown = await visibleSections();
  if (shown.length !== 4) failures.push('clearing search should show 4 sections, got ' + shown.length);
  await page.fill('#search', 'xyz');
  if (!(await page.isVisible('#no-match'))) failures.push('no-match message missing for xyz search');
  await page.fill('#search', '');
  await page.click('#reset-btn');
  await expectText('#toast', 'Settings reset.', 'toast after reset');
  await expectText('#preview-theme', 'Light', 'preview theme after reset');
  await expectText('#volume-value', '50', 'volume after reset');
  await expectText('#notif-state', 'On', 'notifications state after reset');
  if ((await page.inputValue('#display-name')) !== '') {
    failures.push('display name not cleared after reset');
  }
  await page.reload();
  await expectText('#preview-theme', 'Light', 'preview theme after reload post reset');
  await expectText('#volume-value', '50', 'volume after reload post reset');
  await page.check('#notif-toggle');
  await page.click('#save-btn');
  await expectText('#toast', 'Settings saved.', 'toast after second save');
  details.finalTheme = await text('#preview-theme');
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
