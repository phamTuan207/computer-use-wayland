// t03-video-call check. Joins a demo video call and drives the real
// controls: mute, camera, hand raise, chat, screen share, invite and
// remove a participant, leave and rejoin. Asserts the real DOM state
// after each step. Prints one JSON result line. Exit 0 on pass, 1 on fail.
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
  const visible = (sel) => page.isVisible(sel);
  const expectText = async (sel, wanted, what) => {
    const got = (await text(sel) || '').trim();
    if (got !== wanted) failures.push(what + ': got "' + got + '", want "' + wanted + '"');
  };

  await expectText('#status', 'Not in a call.', 'initial status');
  if (!(await visible('#lobby'))) failures.push('lobby not visible at start');
  if (await visible('#call')) failures.push('call shown before join');
  await page.click('#join-btn');
  await expectText('#status', 'In call: Weekly sync', 'status after join');
  if (!(await visible('#call'))) failures.push('call not visible after join');
  await expectText('#participant-count', 'Participants: 3', 'initial participants');
  await page.click('#mute-btn');
  await expectText('#tile-you .mic-state', 'Muted', 'mic after mute');
  await expectText('#mute-btn', 'Unmute', 'mute button label after mute');
  await page.click('#mute-btn');
  await expectText('#tile-you .mic-state', 'Live', 'mic after unmute');
  await expectText('#mute-btn', 'Mute', 'mute button label after unmute');
  await page.click('#cam-btn');
  await expectText('#tile-you .cam-state', 'Camera off', 'camera state after off');
  const camClass = await page.getAttribute('#tile-you', 'class');
  if (!camClass.includes('camera-off')) failures.push('tile missing camera-off class');
  await page.click('#cam-btn');
  await expectText('#tile-you .cam-state', 'Camera on', 'camera state after on');
  await page.click('#hand-btn');
  await expectText('#hand-count', 'Hands raised: 1', 'hand count after raise');
  await expectText('#hand-btn', 'Lower hand', 'hand button label after raise');
  await page.click('#hand-btn');
  await expectText('#hand-count', 'Hands raised: 0', 'hand count after lower');
  await page.fill('#chat-input', 'Hello team');
  await page.click('#chat-send');
  await page.fill('#chat-input', 'Can we start with item one?');
  await page.click('#chat-send');
  const chatText = await text('#chat-log');
  if (!chatText.includes('You: Hello team')) failures.push('first chat message missing');
  if (!chatText.includes('You: Can we start with item one?')) failures.push('second chat message missing');
  details.chatMessages = await page.$$eval('#chat-log .chat-msg', (els) => els.length);
  await page.click('#share-btn');
  await expectText('#share-state', 'Sharing screen.', 'share state after start');
  if (!(await visible('#tile-screen'))) failures.push('screen tile missing while sharing');
  await expectText('#participant-count', 'Participants: 4', 'participants while sharing');
  await page.click('#share-btn');
  await expectText('#share-state', 'Not sharing.', 'share state after stop');
  if (await page.$('#tile-screen')) failures.push('screen tile still present after stop');
  await page.click('#invite-btn');
  await expectText('#participant-count', 'Participants: 4', 'participants after invite');
  if (!(await visible('#tile-cara'))) failures.push('Cara tile missing after invite');
  await page.click('#tile-cara .remove-btn');
  await expectText('#participant-count', 'Participants: 3', 'participants after remove');
  if (await page.$('#tile-cara')) failures.push('Cara tile still present after remove');
  await page.click('#leave-btn');
  await expectText('#status', 'Left the call.', 'status after leave');
  if (!(await visible('#lobby'))) failures.push('lobby not visible after leave');
  await expectText('#join-btn', 'Rejoin call', 'join button label after leave');
  await page.click('#join-btn');
  await expectText('#status', 'In call: Weekly sync', 'status after rejoin');
  await expectText('#participant-count', 'Participants: 3', 'participants after rejoin');
  await page.click('#leave-btn');
  await expectText('#status', 'Left the call.', 'status after second leave');
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
