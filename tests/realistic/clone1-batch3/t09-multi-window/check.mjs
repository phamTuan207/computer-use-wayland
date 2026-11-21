// t09-multi-window check. Drives a dashboard that opens real popup
// windows: a detail window that renames a project and a preferences
// window that changes the theme. The popups post results back to the
// main window, and the check asserts the real DOM of the main window
// after each popup closes. Also checks cancel leaves state unchanged
// and two popups open at once.
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
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto(fixtureUrl);
  const text = (sel) => page.textContent(sel);
  const titleOf = (id) => page.textContent(`.project[data-id="${id}"] .title`);
  const expectTitle = async (id, wanted, what) => {
    const got = (await titleOf(id) || '').trim();
    if (got !== wanted) failures.push(what + ': project ' + id + ' is "' + got + '", want "' + wanted + '"');
  };
  const openPopup = async (clickSel) => {
    const [popup] = await Promise.all([
      context.waitForEvent('page', { timeout: 10000 }),
      page.click(clickSel),
    ]);
    await popup.waitForLoadState('domcontentloaded');
    return popup;
  };
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  // Click a button that closes its own popup window. Under load the
  // window can close between Playwright's click steps, which throws
  // "Target page, context or browser has been closed" even though the
  // click landed. That error is tolerated only when the popup really
  // closed, and only together with a verify step: after the close,
  // the expected effect on the main window is polled for up to 5 s,
  // because the popup posts its result with postMessage and closes
  // synchronously, so the opener applies the effect on a later task.
  // If the effect never appears, the click is reported as a failure
  // instead of being silently swallowed.
  const clickAndClose = async (popup, sel, verify, what) => {
    const closed = popup.waitForEvent('close', { timeout: 10000 });
    try {
      await popup.click(sel);
    } catch (err) {
      if (!String(err && err.message ? err.message : err).includes('has been closed')) throw err;
      const didClose = await Promise.race([
        closed.then(() => true, () => false),
        sleep(2000).then(() => false),
      ]);
      if (!didClose) throw err;
    }
    await closed;
    if (verify) {
      const deadline = Date.now() + 5000;
      let seen = false;
      while (Date.now() < deadline) {
        try {
          if (await verify()) { seen = true; break; }
        } catch (err) {
          // A verify that throws (page gone, selector missing) counts
          // as not seen yet; the loop retries until the deadline.
        }
        await sleep(50);
      }
      if (!seen) {
        failures.push(what + ': expected effect not seen after popup closed, click may not have landed');
      }
    }
  };
  const titleIs = (id, wanted) => async () => (await titleOf(id) || '').trim() === wanted;
  const bodyIsDark = async () => ((await page.getAttribute('body', 'class')) || '').includes('dark');
  const bodyIsLight = async () => !((await page.getAttribute('body', 'class')) || '').includes('dark');

  await expectTitle('alpha', 'Alpha', 'initial Alpha title');
  await expectTitle('beta', 'Beta', 'initial Beta title');
  await expectTitle('gamma', 'Gamma', 'initial Gamma title');
  let popup = await openPopup('.project[data-id="alpha"] .detail-btn');
  if ((await popup.inputValue('#title-input')) !== 'Alpha') {
    failures.push('detail window did not prefill Alpha');
  }
  await popup.fill('#title-input', 'Alpha v2');
  await clickAndClose(popup, '#save-btn', titleIs('alpha', 'Alpha v2'), 'Alpha title after first rename');
  await expectTitle('alpha', 'Alpha v2', 'Alpha title after first rename');
  if (!(await text('#status')).includes('Renamed alpha to Alpha v2.')) {
    failures.push('status wrong after first rename: ' + (await text('#status')));
  }
  popup = await openPopup('.project[data-id="alpha"] .detail-btn');
  if ((await popup.inputValue('#title-input')) !== 'Alpha v2') {
    failures.push('detail window did not prefill Alpha v2 on reopen');
  }
  await popup.fill('#title-input', 'Alpha Final');
  await clickAndClose(popup, '#save-btn', titleIs('alpha', 'Alpha Final'), 'Alpha title after second rename');
  await expectTitle('alpha', 'Alpha Final', 'Alpha title after second rename');
  popup = await openPopup('#prefs-btn');
  await popup.selectOption('#theme-select', 'dark');
  await clickAndClose(popup, '#apply-btn', bodyIsDark, 'main window dark class after prefs dark');
  if (!((await page.getAttribute('body', 'class')) || '').includes('dark')) {
    failures.push('main window missing dark class after prefs dark');
  }
  popup = await openPopup('#prefs-btn');
  await popup.selectOption('#theme-select', 'light');
  await clickAndClose(popup, '#apply-btn', bodyIsLight, 'main window light class after prefs light');
  if (((await page.getAttribute('body', 'class')) || '').includes('dark')) {
    failures.push('main window still dark after prefs light');
  }
  popup = await openPopup('.project[data-id="beta"] .detail-btn');
  await popup.fill('#title-input', 'Beta Changed');
  await clickAndClose(popup, '#cancel-btn');
  // No verify here: the title is already 'Beta', so waiting for it
  // would return instantly and prove nothing. Dwell instead, then
  // read immediately: a wrong rename message would have arrived.
  await sleep(500);
  await expectTitle('beta', 'Beta', 'Beta title after cancelled rename');
  const detailPopup = await openPopup('.project[data-id="gamma"] .detail-btn');
  const prefsPopup = await openPopup('#prefs-btn');
  if (context.pages().length !== 3) {
    failures.push('expected 3 pages with two popups open, got ' + context.pages().length);
  }
  await prefsPopup.selectOption('#theme-select', 'dark');
  await clickAndClose(prefsPopup, '#apply-btn', bodyIsDark, 'main window dark class after second prefs popup');
  if (!((await page.getAttribute('body', 'class')) || '').includes('dark')) {
    failures.push('main window missing dark class after second prefs popup');
  }
  await detailPopup.fill('#title-input', 'Gamma v2');
  await clickAndClose(detailPopup, '#save-btn', titleIs('gamma', 'Gamma v2'), 'Gamma title after rename with two popups');
  await expectTitle('gamma', 'Gamma v2', 'Gamma title after rename with two popups');
  await expectTitle('alpha', 'Alpha Final', 'Alpha title at the end');
  await expectTitle('beta', 'Beta', 'Beta title at the end');
  if (context.pages().length !== 1) {
    failures.push('expected 1 page after all popups closed, got ' + context.pages().length);
  }
  details.finalTitles = {
    alpha: await titleOf('alpha'),
    beta: await titleOf('beta'),
    gamma: await titleOf('gamma'),
  };
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
