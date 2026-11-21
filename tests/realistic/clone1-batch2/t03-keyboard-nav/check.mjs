// t03-keyboard-nav check. Every interaction is keyboard only: Tab order,
// arrow keys in a menu and a listbox, form entry, a focus-trapped dialog
// closed with Escape, and a Ctrl+K search overlay.
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
  const activeId = () => page.evaluate(() => document.activeElement.id || document.activeElement.tagName);
  const tabOrder = [];
  for (let i = 0; i < 8; i++) {
    await page.keyboard.press('Tab');
    tabOrder.push(await activeId());
  }
  step('walk Tab order, 8 stops');
  const expected = ['skip', 'menuBtn', 'listbox', 'name', 'email', 'country', 'submitBtn', 'openDlg'];
  check(JSON.stringify(tabOrder) === JSON.stringify(expected),
    'tab order wrong: ' + JSON.stringify(tabOrder)); step('check Tab order matches');
  details = { tabOrder };
  for (let i = 0; i < 6; i++) await page.keyboard.press('Shift+Tab');
  check((await activeId()) === 'menuBtn', 'expected focus back on menuBtn, got ' + (await activeId())); step('Shift+Tab back to menu button');
  await page.keyboard.press('Enter'); step('open menu with Enter');
  check(await page.isVisible('#menu'), 'menu should be visible'); step('check menu opened');
  await page.keyboard.press('ArrowDown'); step('arrow to second menu item');
  const menuFocus = await page.evaluate(() => document.activeElement.textContent);
  check(menuFocus === 'Reference', 'arrow should focus Reference, got: ' + menuFocus); step('check arrow focused Reference');
  await page.keyboard.press('Enter'); step('pick menu item with Enter');
  const nav = (await page.textContent('#navResult')) || '';
  check(nav.includes('Reference'), 'menu pick should be Reference, got: ' + nav);
  check((await activeId()) === 'menuBtn', 'focus should return to menu button'); step('check menu picked Reference, focus returned');
  await page.keyboard.press('Tab');
  check((await activeId()) === 'listbox', 'expected listbox focus, got ' + (await activeId())); step('Tab to listbox, check focused');
  await page.keyboard.press('ArrowDown');
  await page.keyboard.press('ArrowDown'); step('arrow down twice in listbox');
  await page.keyboard.press('Enter'); step('pick listbox item with Enter');
  const list = (await page.textContent('#listResult')) || '';
  check(list.includes('Forms'), 'listbox pick should be Forms, got: ' + list); step('check listbox picked Forms');
  await page.keyboard.press('Tab');
  await page.keyboard.type('Ada Lovelace'); step('Tab to name field, type name');
  await page.keyboard.press('Tab');
  await page.keyboard.type('ada@example.com'); step('Tab to email field, type email');
  await page.keyboard.press('Tab'); step('Tab to country select');
  await page.keyboard.press('ArrowDown'); step('arrow down to first country');
  const country = await page.evaluate(() => document.getElementById('country').value);
  check(country === 'vn', 'country should be vn, got ' + country); step('check country is vn');
  await page.keyboard.press('Tab'); step('Tab to Send button');
  await page.keyboard.press('Space'); step('submit form with Space');
  const form = (await page.textContent('#formResult')) || '';
  check(form.includes('Sent: Ada Lovelace'), 'form result wrong: ' + form); step('check form submitted');
  await page.keyboard.press('Tab');
  check((await activeId()) === 'openDlg', 'expected dialog button focus, got ' + (await activeId())); step('Tab to dialog button, check focused');
  await page.keyboard.press('Enter'); step('open dialog with Enter');
  check(await page.isVisible('#dlg'), 'dialog should be visible');
  check((await activeId()) === 'dlgInput', 'dialog input should be focused'); step('check dialog opened with input focused');
  await page.keyboard.type('Great demo'); step('type feedback');
  await page.keyboard.press('Tab'); step('Tab inside dialog, trap check');
  check((await activeId()) === 'dlgClose', 'focus trap should move to Close, got ' + (await activeId())); step('check focus trap cycles to Close');
  await page.keyboard.press('Escape'); step('close dialog with Escape');
  check(!(await page.isVisible('#dlg')), 'dialog should be closed');
  check((await activeId()) === 'openDlg', 'focus should return to dialog button');
  const dlgRes = (await page.textContent('#dlgResult')) || '';
  check(dlgRes.includes('Great demo'), 'dialog result should keep feedback, got: ' + dlgRes); step('check dialog closed, focus returned, feedback kept');
  await page.keyboard.press('Control+k');
  check(await page.isVisible('#searchOverlay'), 'search overlay should open');
  check((await activeId()) === 'searchInput', 'search input should be focused'); step('open search with Ctrl+K, check focused');
  await page.keyboard.type('apple'); step('type search query');
  await page.keyboard.press('Enter'); step('pick first match with Enter');
  const search = (await page.textContent('#searchResult')) || '';
  check(search.includes('apple pie'), 'search pick should be apple pie, got: ' + search);
  check(!(await page.isVisible('#searchOverlay')), 'search overlay should close after pick'); step('check search picked apple pie, overlay closed');
  await page.keyboard.press('Control+k');
  await page.keyboard.press('Escape');
  check(!(await page.isVisible('#searchOverlay')), 'search overlay should close on Escape'); step('open search again, close with Escape');
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
