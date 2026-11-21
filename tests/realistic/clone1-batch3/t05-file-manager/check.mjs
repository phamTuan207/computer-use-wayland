// t05-file-manager check. Drives a demo file manager with real UI
// actions: sort, search, create folder, navigate, rename, delete with
// confirm, move between folders, and rename a folder. Asserts the real
// DOM list, crumbs, and status after each step.
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
  const items = () => page.$$eval('#list .item', (els) => els.map((e) => e.dataset.name));
  const expectItems = async (wanted, what) => {
    const got = await items();
    if (JSON.stringify(got) !== JSON.stringify(wanted)) {
      failures.push(what + ': got [' + got.join(', ') + '], want [' + wanted.join(', ') + ']');
    }
  };

  await expectItems(['budget.csv', 'notes.txt', 'photo.jpg', 'video.mp4'], 'initial Home order');
  if ((await text('#status')).trim() !== 'Home: 4 items') failures.push('initial status wrong');
  await page.selectOption('#sort', 'size-desc');
  if ((await items())[0] !== 'video.mp4') failures.push('size-desc first item is not video.mp4');
  await page.selectOption('#sort', 'name');
  if ((await items())[0] !== 'budget.csv') failures.push('name sort first item is not budget.csv');
  await page.selectOption('#sort', 'size-asc');
  if ((await items())[0] !== 'notes.txt') failures.push('size-asc first item is not notes.txt');
  await page.selectOption('#sort', 'name');
  await page.fill('#search', 'photo');
  await expectItems(['photo.jpg'], 'search photo');
  await page.fill('#search', '');
  await expectItems(['budget.csv', 'notes.txt', 'photo.jpg', 'video.mp4'], 'after clearing search');
  await page.click('#new-folder-btn');
  await expectItems(['Archive', 'budget.csv', 'notes.txt', 'photo.jpg', 'video.mp4'], 'after new folder');
  if (!(await page.$('#tree-archive'))) failures.push('tree button for Archive missing');
  await page.dblclick('#list .item[data-name="Archive"]');
  if ((await text('#crumbs')).trim() !== 'Archive') failures.push('crumbs wrong inside Archive');
  if (!(await page.isVisible('#empty'))) failures.push('empty state missing in Archive');
  if ((await text('#status')).trim() !== 'Archive: 0 items') failures.push('Archive status wrong');
  await page.click('#tree-home');
  if ((await text('#crumbs')).trim() !== 'Home') failures.push('crumbs wrong back in Home');
  await page.click('#list .item[data-name="notes.txt"]');
  await page.click('#rename-btn');
  if ((await items()).includes('notes.txt')) failures.push('notes.txt still present after rename');
  if (!(await items()).includes('meeting-notes.txt')) failures.push('meeting-notes.txt missing after rename');
  await page.click('#list .item[data-name="photo.jpg"]');
  await page.click('#delete-btn');
  if (!(await page.isVisible('#confirm'))) failures.push('delete confirm not shown');
  if (!(await text('#confirm-text')).includes('Delete photo.jpg?')) failures.push('confirm text wrong');
  await page.click('#confirm-no');
  if ((await items()).length !== 5) failures.push('cancelled delete changed the list');
  await page.click('#list .item[data-name="photo.jpg"]');
  await page.click('#delete-btn');
  await page.click('#confirm-yes');
  await expectItems(['Archive', 'budget.csv', 'meeting-notes.txt', 'video.mp4'], 'after delete');
  await page.click('#list .item[data-name="video.mp4"]');
  await page.click('#move-btn');
  await page.selectOption('#move-target', 'Archive');
  await page.click('#move-ok');
  await expectItems(['Archive', 'budget.csv', 'meeting-notes.txt'], 'Home after moving video out');
  await page.click('#tree-archive');
  await expectItems(['video.mp4'], 'Archive after moving video in');
  await page.click('#list .item[data-name="video.mp4"]');
  await page.click('#move-btn');
  await page.selectOption('#move-target', 'Home');
  await page.click('#move-ok');
  if ((await items()).length !== 0) failures.push('Archive not empty after moving video back');
  await page.click('#tree-home');
  await expectItems(['Archive', 'budget.csv', 'meeting-notes.txt', 'video.mp4'], 'Home after moving video back');
  await page.click('#list .item[data-name="Archive"]');
  await page.click('#rename-btn');
  if (!(await items()).includes('Old files')) failures.push('Old files missing after folder rename');
  if ((await items()).includes('Archive')) failures.push('Archive still present after folder rename');
  await page.fill('#search', 'old');
  await expectItems(['Old files'], 'search old');
  await page.fill('#search', '');
  await page.dblclick('#list .item[data-name="Old files"]');
  if ((await text('#crumbs')).trim() !== 'Old files') failures.push('crumbs wrong inside Old files');
  if (!(await page.isVisible('#empty'))) failures.push('empty state missing in Old files');
  await page.click('#tree-home');
  details.finalHome = await items();
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
