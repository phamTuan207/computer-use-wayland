// t06-chat-app check. Sends messages, waits for simulated replies,
// uses the emoji picker and attach, searches, edits, deletes, and
// checks unread badges across contacts.
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
  const msgCount = () => page.evaluate(() => document.querySelectorAll('#messages .msg').length);
  const msgTexts = () => page.evaluate(() => [...document.querySelectorAll('#messages .msg .text')].map((e) => e.textContent));
  check((await msgCount()) === 2, 'Alice thread should start with 2 messages'); step('check Alice starts with 2 messages');
  await page.fill('#msgInput', 'Hello Alice, release notes look great'); step('type a message to Alice');
  await page.click('#sendBtn'); step('send the message');
  check((await msgCount()) === 3, 'message count should be 3 after send'); step('check own message appears');
  check((await msgTexts()).includes('Hello Alice, release notes look great'), 'own message text missing'); step('check own message text');
  const typing = (await page.textContent('#typing')) || '';
  check(typing.includes('typing'), 'typing indicator should show, got: ' + typing); step('check typing indicator shows');
  await page.waitForFunction(() => {
    return [...document.querySelectorAll('#messages .msg .text')].some((e) => e.textContent.includes('Sounds good'));
  }, { timeout: 10000 }); step('wait for Alice reply');
  check((await msgCount()) === 4, 'message count should be 4 after reply'); step('check reply arrived');
  check(((await page.textContent('#typing')) || '') === '', 'typing indicator should clear'); step('check typing indicator cleared');
  await page.click('.emoji[data-emoji="🎉"]'); step('pick party emoji');
  const inputVal = await page.evaluate(() => document.getElementById('msgInput').value);
  check(inputVal.includes('🎉'), 'emoji should be in the input, got: ' + inputVal); step('check emoji inserted in input');
  await page.fill('#msgInput', 'Shipping it 🎉'); step('type message with emoji');
  await page.keyboard.press('Enter'); step('send with Enter key');
  check((await msgTexts()).includes('Shipping it 🎉'), 'emoji message missing'); step('check emoji message sent');
  await page.waitForFunction(() => {
    return [...document.querySelectorAll('#messages .msg .text')].some((e) => e.textContent.includes('Let me check'));
  }, { timeout: 10000 }); step('wait for the reply to the emoji message');
  check((await msgCount()) === 6, 'message count should be 6 after second reply, got ' + (await msgCount())); step('check 6 messages after second reply');
  await page.click('#attachBtn'); step('attach a file');
  check((await msgTexts()).includes('Attached: notes.txt (12 KB)'), 'attachment message missing'); step('check attachment message');
  await page.fill('#searchBox', 'shipping'); step('search for shipping');
  await page.waitForTimeout(200);
  check((await msgCount()) === 1, 'search should leave 1 visible message, got ' + (await msgCount())); step('check search filters to 1 message');
  await page.fill('#searchBox', ''); step('clear search');
  await page.waitForTimeout(200);
  check((await msgCount()) === 7, 'all 7 messages should show again'); step('check all messages back after clear');
  const own = page.locator('#messages .msg.me .editBtn').first();
  await own.click(); step('open edit on first own message');
  await page.fill('#messages .msg.me .editInput', 'Hello Alice, release notes look great!'); step('edit the message text');
  await page.locator('#messages .msg.me .saveBtn').click(); step('save the edit');
  check((await msgTexts()).includes('Hello Alice, release notes look great!'), 'edited text missing'); step('check edited text saved');
  const before = await msgCount();
  await page.locator('#messages .msg.me .delBtn').first().click(); step('delete first own message');
  check((await msgCount()) === before - 1, 'message count should drop by 1 after delete'); step('check count dropped after delete');
  await page.click('#contacts button[data-contact="bob"]'); step('switch to Bob');
  check((await msgCount()) === 1, 'Bob thread should have 1 message'); step('check Bob thread has 1 message');
  check(((await page.textContent('#chatTitle')) || '').includes('Bob'), 'title should say Bob'); step('check title says Bob');
  await page.fill('#msgInput', 'Hi Bob, see you at 3'); step('type a message to Bob');
  await page.click('#sendBtn'); step('send to Bob');
  await page.click('#contacts button[data-contact="alice"]'); step('switch back to Alice before reply');
  await page.waitForFunction(() => {
    const b = document.getElementById('badge-bob');
    return b && !b.hidden && b.textContent === '1';
  }, { timeout: 10000 }); step('wait for Bob unread badge');
  const badge = (await page.textContent('#badge-bob')) || '';
  check(badge === '1', 'Bob badge should be 1, got: ' + badge); step('check Bob badge is 1');
  await page.click('#contacts button[data-contact="bob"]'); step('switch to Bob again');
  check(await page.evaluate(() => document.getElementById('badge-bob').hidden), 'Bob badge should clear after opening');
  check((await msgTexts()).some((t) => t.includes('Yes, 3 works')), 'Bob reply missing'); step('check badge cleared and Bob reply visible');
  const metas = await page.evaluate(() => [...document.querySelectorAll('#messages .msg .meta')].map((e) => e.textContent));
  check(metas.every((m) => /\d{2}:\d{2}/.test(m)), 'every message should show a time'); step('check timestamps on messages');
  details = { aliceMessages: 5, bobMessages: await msgCount() };
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
