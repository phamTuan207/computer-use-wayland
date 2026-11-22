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
  // Sample the position inside the page for 500 ms and return the
  // minimum seen. A real reset passes through 0; a missed reset
  // leaves the position at its pre-click value.
  const sampleMin = () => page.evaluate(() => new Promise((resolve) => {
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
  // Exact-zero read on the playing path. The click and the read run
  // in the same in-page task, so no 100 ms timer tick can land
  // between the reset and the read: page JavaScript is
  // single-threaded, and the click handler runs synchronously
  // inside the task. A plain page.click followed by a read cannot
  // guarantee that.
  const posAfterNext = await page.evaluate(() => {
    document.getElementById('next-btn').click();
    return Number(document.getElementById('position').dataset.seconds);
  });
  if (posAfterNext !== 0) failures.push('position not exactly 0 after next while playing: ' + posAfterNext);
  details.positionAfterPlayingNext = posAfterNext;
  // Second witness: sample the position inside the page for 500 ms
  // right after the click and take the minimum. A real reset passes
  // through 0, while a missed reset would leave the position at its
  // pre-click value (10 or more). Start sampling before the
  // now-playing check so the first sample lands as close to the
  // click as possible.
  const posBeforeNext = resumed;
  const minAfterNextP = sampleMin();
  await expectText('#now-playing', 'River Road - The Demos', 'now playing after next');
  const minAfterNext = await minAfterNextP;
  if (minAfterNext > 2 || minAfterNext >= posBeforeNext) {
    failures.push('position not reset after next: min observed ' + minAfterNext + ' after ' + posBeforeNext);
  }
  details.positionMinAfterNext = minAfterNext;
  // Three-point advancing check: a Next that stops the timer
  // part-way through would still pass an absolute read, so read the
  // position when the sampler window ends and again after two
  // 350 ms sleeps, requiring a gain of at least 2 ticks across each
  // sleep. The absolute 2-11 bound on the middle read still catches
  // a clock that runs fast: one tick per 100 ms over about 850 ms
  // of playing puts the correct value near 8.
  const afterSampler = await position();
  details.positionAtSamplerEnd = afterSampler;
  await sleep(350);
  const advancing = await position();
  details.positionAdvancingAfterNext = advancing;
  if (advancing - afterSampler < 2) failures.push('position did not gain after next while playing: ' + afterSampler + ' to ' + advancing);
  if (advancing < 2 || advancing > 11) failures.push('position after next while playing out of range 2-11: ' + advancing);
  // Second gain window: a timer that dies late in the first sleep
  // still shows a gain there, so read once more after another
  // 350 ms and require a second gain of at least 2 ticks. No
  // absolute bound here: the correct value is near 12 by then.
  await sleep(350);
  const advancingLater = await position();
  details.positionAdvancingLaterAfterNext = advancingLater;
  if (advancingLater - advancing < 2) failures.push('position did not gain again after next while playing: ' + advancing + ' to ' + advancingLater);
  // Exact-zero check on a clock-frozen path. The 500 ms sampler above
  // cannot tell a correct reset sampled late from a wrong reset to 1
  // or 2, so pause first (the timer stops, so no tick can land
  // between the click and the read) and require exactly 0 after Next.
  // This runs as a second Next on purpose: pausing before the first
  // Next and resuming with Play would restart the timer and hide a
  // nextTrack that stops the clock, and the advancing check above is
  // the only witness for that defect.
  await page.click('#pause-btn');
  await expectText('#status', 'Paused', 'status before frozen next');
  await page.click('#next-btn');
  const frozenAfterNext = await position();
  if (frozenAfterNext !== 0) failures.push('position not exactly 0 after next while paused: ' + frozenAfterNext);
  details.positionAfterFrozenNext = frozenAfterNext;
  await expectText('#now-playing', 'Night Drive - The Demos', 'now playing after frozen next');
  await page.click('#play-btn');
  await expectText('#status', 'Playing', 'status after resume from frozen next');
  // The frozen value was exactly 0, so this read is a gain check: a
  // Play that does not restart the timer fails here, before the
  // Previous clicks (which reset position themselves) can mask it.
  await sleep(350);
  const afterFrozenNextResume = await position();
  details.positionAfterFrozenNextResume = afterFrozenNextResume;
  if (afterFrozenNextResume < 2 || afterFrozenNextResume > 11) failures.push('position did not advance after resume from frozen next: ' + afterFrozenNextResume);
  // Second read after another 350 ms: a timer that dies shortly
  // after the resume still shows a gain on the first read, so
  // require a second gain of at least 2 ticks as well as the
  // absolute 2-11 bound.
  await sleep(350);
  const afterFrozenNextResumeLater = await position();
  details.positionAfterFrozenNextResumeLater = afterFrozenNextResumeLater;
  if (afterFrozenNextResumeLater - afterFrozenNextResume < 2) failures.push('position did not gain again after resume from frozen next: ' + afterFrozenNextResume + ' to ' + afterFrozenNextResumeLater);
  if (afterFrozenNextResumeLater < 2 || afterFrozenNextResumeLater > 11) failures.push('position after resume from frozen next out of range 2-11: ' + afterFrozenNextResumeLater);
  await page.click('#prev-btn');
  await expectText('#now-playing', 'River Road - The Demos', 'now playing after prev from frozen next');
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
  // Same sampler read as the first Next: the shuffle Next must reset
  // the position too, and the track-name assert alone cannot see a
  // Next that skips the reset while shuffle is on.
  const posBeforeShuffleNext = await position();
  const posAfterShuffleNext = await page.evaluate(() => {
    document.getElementById('next-btn').click();
    return Number(document.getElementById('position').dataset.seconds);
  });
  if (posAfterShuffleNext !== 0) failures.push('position not exactly 0 after shuffle next while playing: ' + posAfterShuffleNext);
  details.positionAfterPlayingShuffleNext = posAfterShuffleNext;
  const minAfterShuffleNextP = sampleMin();
  await expectText('#now-playing', 'Mountain Air - The Demos', 'now playing after next in shuffle order');
  const minAfterShuffleNext = await minAfterShuffleNextP;
  if (minAfterShuffleNext > 2 || minAfterShuffleNext >= posBeforeShuffleNext) {
    failures.push('position not reset after shuffle next: min observed ' + minAfterShuffleNext + ' after ' + posBeforeShuffleNext);
  }
  details.positionMinAfterShuffleNext = minAfterShuffleNext;
  // Three-point advancing check, as after the first Next: a shuffle
  // Next that stops the timer would also show min 0, and the step
  // 14 playlist click restarts the timer, so this is the only
  // witness for it. Require a gain of at least 2 ticks across each
  // of two 350 ms sleeps, not just an advanced absolute value.
  const afterShuffleSampler = await position();
  details.positionAtShuffleSamplerEnd = afterShuffleSampler;
  await sleep(350);
  const advancingAfterShuffle = await position();
  details.positionAdvancingAfterShuffleNext = advancingAfterShuffle;
  if (advancingAfterShuffle - afterShuffleSampler < 2) failures.push('position did not gain after shuffle next while playing: ' + afterShuffleSampler + ' to ' + advancingAfterShuffle);
  if (advancingAfterShuffle < 2 || advancingAfterShuffle > 11) failures.push('position after shuffle next while playing out of range 2-11: ' + advancingAfterShuffle);
  await sleep(350);
  const advancingLaterAfterShuffle = await position();
  details.positionAdvancingLaterAfterShuffleNext = advancingLaterAfterShuffle;
  if (advancingLaterAfterShuffle - advancingAfterShuffle < 2) failures.push('position did not gain again after shuffle next while playing: ' + advancingAfterShuffle + ' to ' + advancingLaterAfterShuffle);
  // Paused shuffle Next, mirroring step 7: the sampler above proves
  // the reset happens, this exact-zero read proves the reset value
  // in shuffle order. Previous returns to Mountain Air so the
  // shuffle-off step still checks the track it started from.
  await page.click('#pause-btn');
  await expectText('#status', 'Paused', 'status before frozen shuffle next');
  await page.click('#next-btn');
  const frozenAfterShuffleNext = await position();
  if (frozenAfterShuffleNext !== 0) failures.push('position not exactly 0 after shuffle next while paused: ' + frozenAfterShuffleNext);
  details.positionAfterFrozenShuffleNext = frozenAfterShuffleNext;
  await expectText('#now-playing', 'City Rain - The Demos', 'now playing after frozen shuffle next');
  await page.click('#play-btn');
  await expectText('#status', 'Playing', 'status after resume from frozen shuffle next');
  // Gain check, as after the first frozen resume: a Play that does
  // not restart the timer fails here, before the step 14 playlist
  // click can restart it and mask the defect.
  await sleep(350);
  const afterFrozenShuffleResume = await position();
  details.positionAfterFrozenShuffleResume = afterFrozenShuffleResume;
  if (afterFrozenShuffleResume < 2 || afterFrozenShuffleResume > 11) failures.push('position did not advance after resume from frozen shuffle next: ' + afterFrozenShuffleResume);
  // Second read after another 350 ms, as after the first frozen
  // resume: a timer that dies shortly after the resume still shows
  // a gain on the first read.
  await sleep(350);
  const afterFrozenShuffleResumeLater = await position();
  details.positionAfterFrozenShuffleResumeLater = afterFrozenShuffleResumeLater;
  if (afterFrozenShuffleResumeLater - afterFrozenShuffleResume < 2) failures.push('position did not gain again after resume from frozen shuffle next: ' + afterFrozenShuffleResume + ' to ' + afterFrozenShuffleResumeLater);
  if (afterFrozenShuffleResumeLater < 2 || afterFrozenShuffleResumeLater > 11) failures.push('position after resume from frozen shuffle next out of range 2-11: ' + afterFrozenShuffleResumeLater);
  await page.click('#prev-btn');
  await expectText('#now-playing', 'Mountain Air - The Demos', 'now playing after prev from frozen shuffle next');
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
  // Let the track play so the position is clearly past 0 before the
  // wrap Nexts: a wrap that fails to reset is only observable when
  // the pre-click position is nonzero (a fresh playlist click leaves
  // it at 0, which a broken wrap would also read as 0).
  await sleep(700);
  const posBeforePlayingWrap = await position();
  details.positionBeforePlayingWrap = posBeforePlayingWrap;
  if (posBeforePlayingWrap < 2) failures.push('position did not advance before playing wrap next: ' + posBeforePlayingWrap);
  await page.click('#repeat-btn');
  await expectText('#repeat-btn', 'Repeat: All', 'repeat All before wrap test');
  // Playing wrap first: the wrap while playing must reset the
  // position too. The sampler catches a wrap that resets only when
  // paused (or never resets); the frozen check below catches a wrap
  // that resets to the wrong value. Neither alone covers both. The
  // click and the read run in the same in-page task (see the first
  // Next), so the exact-zero read below is deterministic.
  const posAfterPlayingWrap = await page.evaluate(() => {
    document.getElementById('next-btn').click();
    return Number(document.getElementById('position').dataset.seconds);
  });
  if (posAfterPlayingWrap !== 0) failures.push('position not exactly 0 after playing wrap next while playing: ' + posAfterPlayingWrap);
  details.positionAfterPlayingWrap = posAfterPlayingWrap;
  const minAfterPlayingWrapP = sampleMin();
  await expectText('#now-playing', 'Morning Light - The Demos', 'repeat All wraps to first track (playing)');
  const minAfterPlayingWrap = await minAfterPlayingWrapP;
  if (minAfterPlayingWrap > 2 || minAfterPlayingWrap >= posBeforePlayingWrap) {
    failures.push('position not reset after playing wrap next: min observed ' + minAfterPlayingWrap + ' after ' + posBeforePlayingWrap);
  }
  details.positionMinAfterPlayingWrap = minAfterPlayingWrap;
  // Frozen wrap second: go back to the last track and wrap again,
  // this time paused, so the reset value can be read exactly.
  await page.click('#playlist .track[data-track="4"]');
  await expectText('#now-playing', 'Mountain Air - The Demos', 'now playing after clicking Mountain Air again');
  await sleep(700);
  const posBeforeFrozenWrap = await position();
  details.positionBeforeFrozenWrap = posBeforeFrozenWrap;
  if (posBeforeFrozenWrap < 2) failures.push('position did not advance before frozen wrap next: ' + posBeforeFrozenWrap);
  // Same frozen exact-zero check as the mid-list Next above, for the
  // repeat-All wrap branch: the wrap path resets position too, and
  // the track-name assert alone cannot see a wrap that leaves the
  // old position behind. Pausing here masks nothing: no advancing
  // check follows the wrap Next.
  await page.click('#pause-btn');
  await expectText('#status', 'Paused', 'status before frozen wrap next');
  await page.click('#next-btn');
  const frozenAfterWrap = await position();
  if (frozenAfterWrap !== 0) failures.push('position not exactly 0 after wrap next while paused: ' + frozenAfterWrap);
  details.positionAfterFrozenWrap = frozenAfterWrap;
  await expectText('#now-playing', 'Morning Light - The Demos', 'repeat All wraps to first track (paused)');
  await page.click('#play-btn');
  await expectText('#status', 'Playing', 'status after resume from frozen wrap next');
  // Gain check, as after the other frozen resumes: a Play that does
  // not restart the timer fails here, before the later playlist
  // clicks can restart it and mask the defect.
  await sleep(350);
  const afterFrozenWrapResume = await position();
  details.positionAfterFrozenWrapResume = afterFrozenWrapResume;
  if (afterFrozenWrapResume < 2 || afterFrozenWrapResume > 11) failures.push('position did not advance after resume from frozen wrap next: ' + afterFrozenWrapResume);
  // Second read after another 350 ms, as after the other frozen
  // resumes: a timer that dies shortly after the resume still shows
  // a gain on the first read.
  await sleep(350);
  const afterFrozenWrapResumeLater = await position();
  details.positionAfterFrozenWrapResumeLater = afterFrozenWrapResumeLater;
  if (afterFrozenWrapResumeLater - afterFrozenWrapResume < 2) failures.push('position did not gain again after resume from frozen wrap next: ' + afterFrozenWrapResume + ' to ' + afterFrozenWrapResumeLater);
  if (afterFrozenWrapResumeLater < 2 || afterFrozenWrapResumeLater > 11) failures.push('position after resume from frozen wrap next out of range 2-11: ' + afterFrozenWrapResumeLater);
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
