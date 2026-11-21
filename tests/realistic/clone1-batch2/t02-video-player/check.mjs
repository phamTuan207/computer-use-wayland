// t02-video-player check. Drives a real 10 s clip: play, pause, seek,
// volume, mute, speed, captions, and play to the end, then replay.
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
async function state(page, expr) { return page.evaluate(expr); }

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
  await page.waitForFunction(() => {
    const v = document.getElementById('vid');
    return v && v.readyState >= 1 && Number.isFinite(v.duration);
  }, { timeout: 10000 }); step('wait for metadata');
  const duration = await state(page, `document.getElementById('vid').duration`);
  check(Math.abs(duration - 10) < 0.5, 'duration should be about 10 s, got ' + duration); step('check duration is 10 s');
  details = { duration };
  await page.click('#playBtn'); step('press play');
  await page.waitForTimeout(2000); step('let it play 2 s');
  let t = await state(page, `document.getElementById('vid').currentTime`);
  check(t > 1.2, 'currentTime should advance past 1.2 s, got ' + t); step('check time advanced');
  check(await state(page, `!document.getElementById('vid').paused`), 'video should not be paused'); step('check not paused');
  await page.click('#pauseBtn'); step('press pause');
  await page.waitForTimeout(300);
  check(await state(page, `document.getElementById('vid').paused`), 'video should be paused'); step('check paused');
  const tPaused = await state(page, `document.getElementById('vid').currentTime`);
  await page.waitForTimeout(800);
  const tPaused2 = await state(page, `document.getElementById('vid').currentTime`);
  check(Math.abs(tPaused2 - tPaused) < 0.05, 'time moved while paused'); step('check time frozen while paused');
  await page.evaluate(() => { const v = document.getElementById('vid'); v.currentTime = 5; }); step('seek to 5 s');
  await page.waitForTimeout(300);
  t = await state(page, `document.getElementById('vid').currentTime`);
  check(Math.abs(t - 5) < 0.6, 'seek to 5 s failed, got ' + t); step('check seek landed at 5 s');
  await page.evaluate(() => {
    const v = document.getElementById('vol');
    v.value = '0.5';
    v.dispatchEvent(new Event('input', { bubbles: true }));
  }); step('set volume to 0.5');
  await page.waitForTimeout(200);
  const vol = await state(page, `document.getElementById('vid').volume`);
  check(Math.abs(vol - 0.5) < 0.05, 'volume should be 0.5, got ' + vol); step('check volume is 0.5');
  await page.click('#muteBtn'); step('press mute');
  check(await state(page, `document.getElementById('vid').muted`), 'video should be muted'); step('check muted');
  await page.click('#muteBtn'); step('press unmute');
  check(await state(page, `!document.getElementById('vid').muted`), 'video should be unmuted'); step('check unmuted');
  await page.selectOption('#speed', '2'); step('set speed to 2x');
  const rate = await state(page, `document.getElementById('vid').playbackRate`);
  check(rate === 2, 'playbackRate should be 2, got ' + rate); step('check speed is 2x');
  await page.selectOption('#speed', '1'); step('set speed back to 1x');
  await page.evaluate(() => { const v = document.getElementById('vid'); v.currentTime = 1; }); step('seek to 1 s for captions');
  await page.waitForTimeout(500);
  const cap1 = (await page.textContent('#captionBox')) || '';
  check(cap1.includes('Welcome to the demo clip'), 'first caption missing, got: ' + cap1); step('check first caption text');
  await page.evaluate(() => { const v = document.getElementById('vid'); v.currentTime = 7; }); step('seek to 7 s');
  await page.waitForTimeout(500);
  const cap2 = (await page.textContent('#captionBox')) || '';
  check(cap2.includes('Thanks for watching'), 'last caption missing, got: ' + cap2); step('check last caption text');
  await page.click('#ccBtn'); step('turn captions off');
  await page.waitForTimeout(300);
  check(((await page.textContent('#captionBox')) || '') === '', 'caption box should clear when off'); step('check captions cleared');
  await page.click('#ccBtn'); step('turn captions back on');
  await page.evaluate(() => { const v = document.getElementById('vid'); v.currentTime = 9.5; v.play(); }); step('seek near end and play');
  await page.waitForFunction(() => document.getElementById('status').textContent === 'ended', { timeout: 10000 }); step('wait for ended state');
  check(await state(page, `document.getElementById('vid').ended`), 'video should report ended'); step('check ended flag');
  await page.click('#replayBtn'); step('press replay');
  await page.waitForTimeout(800);
  t = await state(page, `document.getElementById('vid').currentTime`);
  check(t < 2, 'replay should restart near 0, got ' + t); step('check replay restarted');
  check(await state(page, `!document.getElementById('vid').paused`), 'video should play after replay'); step('check playing after replay');
  const label = (await page.textContent('#timeLabel')) || '';
  check(/\/ 10\.0 s/.test(label), 'time label should show / 10.0 s, got: ' + label); step('check time label format');
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
