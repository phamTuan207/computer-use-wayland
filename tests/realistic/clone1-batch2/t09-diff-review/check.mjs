// t09-diff-review check. Filters and searches a diff, adds inline
// comments, replies, resolves, navigates hunks, and submits two reviews.
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
  await page.evaluate(() => { localStorage.removeItem('pr42-threads'); localStorage.removeItem('pr42-reviews'); });
  await page.reload(); step('clear saved review and reload');
  const lineCount = () => page.evaluate(() => document.querySelectorAll('#diff .line').length);
  const threadCount = () => page.evaluate(() => document.querySelectorAll('#diff .thread').length);
  check((await page.evaluate(() => document.querySelectorAll('#diff .file').length)) === 2, 'diff should show 2 files');
  check((await lineCount()) === 12, 'diff should show 12 lines, got ' + (await lineCount())); step('check 2 files and 12 lines');
  await page.selectOption('#fileFilter', 'auth.js');
  check((await lineCount()) === 6, 'auth.js filter should show 6 lines'); step('filter to auth.js, check 6 lines');
  await page.selectOption('#fileFilter', ''); step('clear file filter');
  await page.fill('#search', 'token');
  await page.waitForTimeout(200);
  check((await lineCount()) === 4, 'token search should match 4 lines, got ' + (await lineCount()));
  check((await page.evaluate(() => document.querySelectorAll('#diff mark').length)) === 4, '4 matches should be highlighted');
  const searchInfo = (await page.textContent('#searchInfo')) || '';
  check(searchInfo.includes('Matched 4 lines'), 'search info wrong: ' + searchInfo); step('search token, check 4 lines, 4 highlights, info text');
  await page.fill('#search', ''); step('clear search');
  await page.locator('.line:has-text("await getToken")').click();
  check(await page.isVisible('.comment-form'), 'comment form should open'); step('click the await getToken line, check form opened');
  await page.fill('.commentInput', 'Why await here? The old call was sync.');
  await page.click('.addCommentBtn'); step('type and submit the comment');
  check((await threadCount()) === 1, 'one thread should show');
  check(((await page.textContent('.thread')) || '').includes('Why await here'), 'thread text missing');
  check(((await page.textContent('#commentCount')) || '') === '1', 'comment count should be 1'); step('check thread appears with text, count is 1');
  await page.locator('.thread .replyBtn').click();
  await page.fill('.replyInput', 'Because getToken now hits the network.');
  await page.click('.sendReplyBtn'); step('open reply box, type and send reply');
  check(((await page.textContent('.thread')) || '').includes('hits the network'), 'reply text missing');
  check(((await page.textContent('#commentCount')) || '') === '2', 'comment count should be 2 with reply'); step('check reply appears, count is 2');
  await page.locator('.thread .resolveBtn').click();
  check((await threadCount()) === 0, 'resolved thread should hide'); step('resolve the thread, check it hides');
  await page.check('#showResolved');
  check((await threadCount()) === 1, 'resolved thread should show again');
  check(((await page.textContent('.thread')) || '').includes('Why await here'), 'resolved thread text missing'); step('enable show resolved, check thread visible with text');
  await page.uncheck('#showResolved');
  await page.locator('.line:has-text("signal")').click();
  await page.fill('.commentInput', 'Good, abort is now wired through.');
  await page.click('.addCommentBtn'); step('disable show resolved, add second comment on signal line');
  check(((await page.textContent('#commentCount')) || '') === '3', 'comment count should be 3'); step('check comment count is 3');
  await page.click('#nextHunk');
  await page.click('#nextHunk');
  const currentHunk = await page.evaluate(() => {
    const el = document.querySelector('.file.current-hunk h2');
    return el ? el.textContent : '';
  });
  check(currentHunk.includes('api.js'), 'current hunk should be api.js, got: ' + currentHunk); step('go to next hunk twice, check current is api.js');
  await page.click('#prevHunk');
  const currentHunk2 = await page.evaluate(() => {
    const el = document.querySelector('.file.current-hunk h2');
    return el ? el.textContent : '';
  });
  check(currentHunk2.includes('auth.js'), 'current hunk should be auth.js, got: ' + currentHunk2); step('go to previous hunk, check current is auth.js');
  await page.click('#submitReview');
  const revErr = (await page.textContent('#reviewError')) || '';
  check(revErr.includes('Choose Approve or Request changes'), 'expected verdict error, got: ' + revErr); step('submit review with no verdict, check error');
  await page.check('input[name="verdict"][value="request"]');
  await page.fill('#reviewSummary', 'Please handle the missing token case.');
  await page.click('#submitReview'); step('choose Request changes, type summary, submit');
  const status1 = (await page.textContent('#status')) || '';
  check(status1.includes('Changes requested'), 'status should say Changes requested, got: ' + status1);
  check((await page.evaluate(() => document.querySelectorAll('#history li').length)) === 1, 'history should have 1 review'); step('check status is Changes requested, history has 1');
  await page.check('input[name="verdict"][value="approve"]');
  await page.fill('#reviewSummary', 'Looks good now.');
  await page.click('#submitReview'); step('choose Approve, type summary, submit');
  const status2 = (await page.textContent('#status')) || '';
  check(status2.includes('Approved'), 'status should say Approved, got: ' + status2);
  check((await page.evaluate(() => document.querySelectorAll('#history li').length)) === 2, 'history should have 2 reviews'); step('check status is Approved, history has 2');
  details = { reviews: 2, comments: 3 };
  await page.reload();
  const status3 = (await page.textContent('#status')) || '';
  check(status3.includes('Approved'), 'status should persist as Approved, got: ' + status3);
  check(((await page.textContent('#commentCount')) || '') === '3', 'comment count should persist at 3'); step('reload page, check status and comments persist');
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
