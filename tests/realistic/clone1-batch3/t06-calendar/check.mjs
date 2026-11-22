// t06-calendar check. Drives a demo calendar with real UI actions:
// create events, view details, edit a time, delete an event, move
// between months, cancel a new event, and jump back with Today.
// Asserts the real DOM chips, titles, and counts after each step.
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
  const chipsOn = (day) => page.$$eval(`.day[data-day="${day}"] .chip`, (els) => els.map((e) => e.textContent));
  const expectText = async (sel, wanted, what) => {
    const got = (await text(sel) || '').trim();
    if (got !== wanted) failures.push(what + ': got "' + got + '", want "' + wanted + '"');
  };
  const addEvent = async (day, title, time) => {
    await page.click(`.day[data-day="${day}"] .day-num`);
    await page.fill('#event-title', title);
    await page.fill('#event-time', time);
    await page.click('#save-event');
  };

  await expectText('#month-title', 'June 2026', 'initial month');
  const todayClass = await page.getAttribute('.day[data-day="15"]', 'class');
  if (!todayClass.includes('today')) failures.push('day 15 missing today highlight');
  await page.click('.day[data-day="12"] .day-num');
  if (!(await page.isVisible('#form'))) failures.push('event form not shown after clicking a day');
  await expectText('#form-day', 'June 12, 2026', 'form day label');
  await page.fill('#event-title', 'Team sync');
  await page.fill('#event-time', '10:00');
  await page.click('#save-event');
  let chips = await chipsOn(12);
  if (JSON.stringify(chips) !== JSON.stringify(['10:00 Team sync'])) {
    failures.push('day 12 chips after first event: ' + JSON.stringify(chips));
  }
  await addEvent(12, 'Lunch', '12:30');
  chips = await chipsOn(12);
  if (chips.length !== 2 || !chips.includes('12:30 Lunch')) {
    failures.push('day 12 chips after second event: ' + JSON.stringify(chips));
  }
  await addEvent(20, 'Deadline', '09:00');
  chips = await chipsOn(20);
  if (JSON.stringify(chips) !== JSON.stringify(['09:00 Deadline'])) {
    failures.push('day 20 chips: ' + JSON.stringify(chips));
  }
  await expectText('#status', 'Events: 3', 'status after 3 events');
  await page.locator('.day[data-day="12"] .chip').nth(0).click();
  await expectText('#details-title', 'Team sync', 'details title');
  if (!(await text('#details-meta')).includes('June 12, 2026 at 10:00')) {
    failures.push('details meta wrong: ' + (await text('#details-meta')));
  }
  await page.fill('#edit-time', '11:00');
  await page.click('#update-event');
  if (!(await text('#details-meta')).includes('at 11:00')) failures.push('details meta not updated to 11:00');
  chips = await chipsOn(12);
  if (!chips.includes('11:00 Team sync')) failures.push('chip not updated to 11:00: ' + JSON.stringify(chips));
  await page.locator('.day[data-day="12"] .chip').nth(1).click();
  await expectText('#details-title', 'Lunch', 'details title for Lunch');
  await page.click('#delete-event');
  chips = await chipsOn(12);
  if (JSON.stringify(chips) !== JSON.stringify(['11:00 Team sync'])) {
    failures.push('day 12 chips after delete: ' + JSON.stringify(chips));
  }
  await expectText('#status', 'Events: 2', 'status after delete');
  await page.click('#next-btn');
  await expectText('#month-title', 'July 2026', 'month after next');
  if ((await page.$$eval('.chip', (els) => els.length)) !== 0) failures.push('July should have no chips');
  await page.click('#prev-btn');
  await expectText('#month-title', 'June 2026', 'month after prev');
  if ((await page.$$eval('.chip', (els) => els.length)) !== 2) failures.push('June should have 2 chips again');
  await page.click('.day[data-day="5"] .day-num');
  await page.click('#cancel-event');
  chips = await chipsOn(5);
  if (chips.length !== 0) failures.push('day 5 gained a chip after cancel');
  await expectText('#status', 'Events: 2', 'status after cancel');
  await addEvent(15, 'Demo', '14:00');
  chips = await chipsOn(15);
  if (JSON.stringify(chips) !== JSON.stringify(['14:00 Demo'])) {
    failures.push('day 15 chips: ' + JSON.stringify(chips));
  }
  await expectText('#status', 'Events: 3', 'status after Demo');
  await page.click('#next-btn');
  await page.click('#next-btn');
  await expectText('#month-title', 'August 2026', 'month after two nexts');
  await page.click('#today-btn');
  await expectText('#month-title', 'June 2026', 'month after Today');
  await expectText('#status', 'Events: 3', 'status after Today');
  details.chips = await page.$$eval('.chip', (els) => els.map((e) => e.textContent));
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
