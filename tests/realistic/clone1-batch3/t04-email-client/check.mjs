// t04-email-client check. Drives a demo mail client with real UI
// actions: search, open and read, star, compose and send, delete to
// trash, mark all read, and folder switching. Asserts the real DOM
// state after each step. Prints one JSON result line.
// Exit 0 on pass, 1 on fail.
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
  const count = (sel) => page.$$eval(sel, (els) => els.length);
  const expectText = async (sel, wanted, what) => {
    const got = (await text(sel) || '').trim();
    if (got !== wanted) failures.push(what + ': got "' + got + '", want "' + wanted + '"');
  };

  await expectText('#inbox-count', '3', 'initial inbox count');
  await expectText('#unread-count', '2', 'initial unread count');
  await page.fill('#search', 'invoice');
  if ((await count('#list .msg')) !== 1) failures.push('search invoice should show 1 message');
  const searchText = await text('#list');
  if (!searchText.includes('Your invoice for June')) failures.push('search invoice shows wrong message');
  await page.fill('#search', '');
  if ((await count('#list .msg')) !== 3) failures.push('clearing search should show 3 messages');
  await page.locator('#list .msg').nth(0).click();
  await expectText('#reader-subject', 'Your invoice for June', 'reader subject');
  await expectText('#reader-body', 'Invoice INV-1001 is attached. Total 42.00.', 'reader body');
  await expectText('#unread-count', '1', 'unread after opening one message');
  await page.click('#reader-back');
  await page.locator('#list .msg').nth(1).locator('.star').click();
  await expectText('#starred-count', '1', 'starred count after starring');
  await page.click('#compose-btn');
  await page.fill('#to', 'team@example.org');
  await page.fill('#subject', 'Demo report');
  await page.fill('#body', 'Hello, here is the demo report.');
  await page.click('#send-btn');
  await expectText('#toast', 'Message sent.', 'toast after send');
  await expectText('#sent-count', '1', 'sent count after send');
  await page.click('#folder-sent');
  await expectText('#folder-title', 'Sent', 'folder title Sent');
  if ((await count('#list .msg')) !== 1) failures.push('sent folder should show 1 message');
  if (!(await text('#list')).includes('Demo report')) failures.push('sent message subject missing');
  await page.click('#folder-inbox');
  await page.locator('#list .msg').nth(2).click();
  await expectText('#reader-subject', 'System maintenance Sunday', 'reader subject third message');
  await page.click('#reader-delete');
  await expectText('#inbox-count', '2', 'inbox count after delete');
  await expectText('#trash-count', '1', 'trash count after delete');
  await page.click('#folder-trash');
  if (!(await text('#list')).includes('System maintenance Sunday')) failures.push('deleted message missing from trash');
  await page.click('#folder-inbox');
  await page.click('#mark-all-read');
  await expectText('#unread-count', '0', 'unread after mark all read');
  await page.fill('#search', 'nomatch');
  if ((await count('#list .msg')) !== 0) failures.push('search nomatch should show 0 messages');
  if (!(await page.isVisible('#empty'))) failures.push('empty state not visible for nomatch search');
  await page.fill('#search', '');
  await page.click('#folder-starred');
  if ((await count('#list .msg')) !== 1) failures.push('starred folder should show 1 message');
  if (!(await text('#list')).includes('Weekly sync notes')) failures.push('starred message missing');
  await page.locator('#list .msg').nth(0).locator('.star').click();
  await expectText('#starred-count', '0', 'starred count after unstarring');
  await page.click('#folder-inbox');
  await expectText('#folder-title', 'Inbox', 'folder title Inbox');
  details.finalInbox = await text('#inbox-count');
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
