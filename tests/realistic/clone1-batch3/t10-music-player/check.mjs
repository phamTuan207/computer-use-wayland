// t10-music-player check. Drives a demo music player with real UI
// actions: play and pause with a running position, next and previous,
// volume slider, seek by clicking the progress bar, shuffle, repeat
// modes, search filter, and picking a track from the list. Asserts
// the real DOM state after each step.
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
  const position = async () => Number(await page.getAttribute('#position', 'data-seconds'));
  const tracks = () => page.$$eval('#playlist .track', (els) => els.map((e) => e.textContent));
  const expectText = async (sel, wanted, what) => {
    const got = (await text(sel) || '').trim();
    if (got !== wanted) failures.push(what + ': got "' + got + '", want "' + wanted + '"');
  };
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  let listed = await tracks();
  if (listed.length !== 5) failures.push('playlist should list 5 tracks, got ' + listed.length);
  if (!listed[0].startsWith('Morning Light')) failures.push('first track is not Morning Light: ' + listed[0]);
  await page.click('#play-btn');
  await expectText('#status', 'Playing', 'status after play');
  await expectText('#now-playing', 'Morning Light - The Demos', 'now playing after play');
  await sleep(700);
  let pos = await position();
  if (pos < 5) failures.push('position did not advance while playing: ' + pos);
  details.positionAfter700ms = pos;
  await page.click('#pause-btn');
  await expectText('#status', 'Paused', 'status after pause');
  const frozen1 = await position();
  await sleep(400);
  const frozen2 = await position();
  if (frozen1 !== frozen2) failures.push('position moved while paused: ' + frozen1 + ' to ' + frozen2);
  await page.click('#play-btn');
  await sleep(500);
  const resumed = await position();
  if (resumed <= frozen2) failures.push('position did not advance after resume: ' + resumed);
  await page.click('#next-btn');
  // The fixture advances position by 1 every 100 ms while playing,
  // so a single immediate read races the timer tick and flakes under
  // load. Sample the position inside the page for 500 ms right after
  // the click and take the minimum: a real reset passes through 0
  // (allowing up to 2 ticks of delay before sampling starts), while
  // a missed reset would leave the position at its pre-click value
  // (10 or more). Start sampling before the now-playing check so the
  // first sample lands as close to the click as possible.
  const posBeforeNext = resumed;
  const minAfterNextP = page.evaluate(() => new Promise((resolve) => {
    let min = Infinity;
    const t0 = Date.now();
    const sample = () => {
      const v = Number(document.getElementById('position').dataset.seconds);
      if (v < min) min = v;
      if (Date.now() - t0 >= 500) resolve(min);
      else setTimeout(sample, 10);
    };
    sample();
  }));
  await expectText('#now-playing', 'River Road - The Demos', 'now playing after next');
  const minAfterNext = await minAfterNextP;
  if (minAfterNext > 2 || minAfterNext >= posBeforeNext) {
    failures.push('position not reset after next: min observed ' + minAfterNext + ' after ' + posBeforeNext);
  }
  details.positionMinAfterNext = minAfterNext;
  // The sampler only proves the reset happened, not that the clock
  // kept running: a nextTrack that stopped the timer would also
  // show min 0. After the 500 ms sample window the position must
  // have advanced well past 0 while playing.
  await sleep(350);
  const advancing = await position();
  if (advancing < 2) failures.push('position did not advance after next while playing: ' + advancing);
  await page.click('#prev-btn');
  await expectText('#now-playing', 'Morning Light - The Demos', 'now playing after prev');
  await page.click('#volume');
  await page.keyboard.press('Home');
  for (let i = 0; i < 30; i++) await page.keyboard.press('ArrowRight');
  await expectText('#volume-value', '30', 'volume value after slider');
  const bar = await page.$('#progress');
  const box = await bar.boundingBox();
  await page.mouse.click(box.x + box.width * 0.5, box.y + box.height / 2);
  pos = await position();
  if (pos < 85 || pos > 100) failures.push('position after 50% seek out of range: ' + pos);
  details.positionAfterSeek = pos;
  await page.click('#shuffle-btn');
  await expectText('#shuffle-btn', 'Shuffle: On', 'shuffle button after on');
  listed = await tracks();
  if (!listed[1].startsWith('Mountain Air')) {
    failures.push('second track after shuffle should be Mountain Air: ' + JSON.stringify(listed));
  }
  await expectText('#now-playing', 'Morning Light - The Demos', 'now playing unchanged by shuffle');
  await page.click('#next-btn');
  await expectText('#now-playing', 'Mountain Air - The Demos', 'now playing after next in shuffle order');
  await page.click('#shuffle-btn');
  await expectText('#shuffle-btn', 'Shuffle: Off', 'shuffle button after off');
  listed = await tracks();
  if (!listed[0].startsWith('Morning Light')) failures.push('first track after shuffle off is not Morning Light');
  await expectText('#now-playing', 'Mountain Air - The Demos', 'now playing unchanged by shuffle off');
  await page.click('#repeat-btn');
  await expectText('#repeat-btn', 'Repeat: All', 'repeat after first click');
  await page.click('#repeat-btn');
  await expectText('#repeat-btn', 'Repeat: One', 'repeat after second click');
  await page.click('#repeat-btn');
  await expectText('#repeat-btn', 'Repeat: Off', 'repeat after third click');
  await page.click('#playlist .track[data-track="4"]');
  await expectText('#now-playing', 'Mountain Air - The Demos', 'now playing after clicking Mountain Air');
  await page.click('#repeat-btn');
  await expectText('#repeat-btn', 'Repeat: All', 'repeat All before wrap test');
  await page.click('#next-btn');
  await expectText('#now-playing', 'Morning Light - The Demos', 'repeat All wraps to first track');
  await page.click('#repeat-btn');
  await expectText('#repeat-btn', 'Repeat: One', 'repeat One after wrap');
  await page.click('#repeat-btn');
  await expectText('#repeat-btn', 'Repeat: Off', 'repeat Off after wrap');
  await page.fill('#search', 'river');
  listed = await tracks();
  if (listed.length !== 1 || !listed[0].startsWith('River Road')) {
    failures.push('search river shows wrong tracks: ' + JSON.stringify(listed));
  }
  await page.fill('#search', '');
  listed = await tracks();
  if (listed.length !== 5) failures.push('clearing search should show 5 tracks, got ' + listed.length);
  await page.click('#playlist .track[data-track="2"]');
  await expectText('#now-playing', 'Night Drive - The Demos', 'now playing after clicking Night Drive');
  await page.click('#pause-btn');
  await expectText('#status', 'Paused', 'status after final pause');
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
