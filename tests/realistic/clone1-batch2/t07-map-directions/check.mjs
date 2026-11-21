// t07-map-directions check. Plans routes on a fake offline map: distance
// and time by mode, toll and avoid-tolls detour, alternate route, swap,
// save and load, and the same-place error.
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
  const optCount = await page.evaluate(() => document.getElementById('origin').options.length);
  check(optCount === 6, 'origin should list 6 places, got ' + optCount); step('check 6 places listed');
  const summary = () => page.textContent('#summary');
  const stepTexts = () => page.evaluate(() => [...document.querySelectorAll('#steps li')].map((e) => e.textContent));
  const mins = async () => {
    const s = (await summary()) || '';
    const m = s.match(/(\d+) min/);
    return m ? Number(m[1]) : -1;
  };
  await page.selectOption('#origin', 'home');
  await page.selectOption('#dest', 'office'); step('pick Home to Office');
  await page.click('#goBtn'); step('get directions');
  check(((await summary()) || '').includes('4.0 km'), 'Home to Office should be 4.0 km, got: ' + (await summary())); step('check distance is 4.0 km');
  const walkMins = await mins();
  check(walkMins === 48, 'walk time should be 48 min, got ' + walkMins); step('check walk time is 48 min');
  const steps1 = await stepTexts();
  check(steps1.length === 5, 'route should have 5 steps, got ' + steps1.length);
  check(steps1.some((s) => s.includes('toll bridge')), 'steps should mention the toll bridge');
  check(steps1[1].includes('east'), 'first move should head east, got: ' + steps1[1]);
  check(((await summary()) || '').includes('Toll: yes'), 'summary should say Toll: yes'); step('check 5 steps, toll bridge, east first, Toll yes');
  await page.check('input[name="mode"][value="bike"]');
  await page.click('#goBtn'); step('switch to bike, get directions');
  const bikeMins = await mins();
  check(bikeMins === 16, 'bike time should be 16 min, got ' + bikeMins);
  check(bikeMins < walkMins, 'bike should be faster than walk'); step('check bike time is 16 min, faster than walk');
  await page.check('input[name="mode"][value="drive"]');
  await page.click('#goBtn'); step('switch to drive, get directions');
  const driveMins = await mins();
  check(driveMins === 6, 'drive time should be 6 min, got ' + driveMins);
  check(driveMins < bikeMins, 'drive should be faster than bike'); step('check drive time is 6 min, faster than bike');
  await page.check('#avoidTolls');
  await page.click('#goBtn'); step('enable avoid tolls, get directions');
  check(((await summary()) || '').includes('4.8 km'), 'detour should be 4.8 km, got: ' + (await summary()));
  check(((await summary()) || '').includes('Toll: no'), 'summary should say Toll: no');
  const steps2 = await stepTexts();
  check(steps2.some((s) => s.includes('North Bridge detour')), 'steps should mention the detour'); step('check detour is 4.8 km, Toll no, detour step present');
  await page.uncheck('#avoidTolls');
  await page.check('#altRoute');
  await page.click('#goBtn'); step('disable avoid tolls, enable alternate route, get directions');
  const steps3 = await stepTexts();
  check(steps3[1].includes('south'), 'alternate first move should head south, got: ' + steps3[1]);
  check(steps3[1].includes('1st Ave'), 'alternate first move should use 1st Ave, got: ' + steps3[1]); step('check alternate starts south on 1st Ave');
  await page.click('#swapBtn');
  await page.click('#goBtn'); step('swap origin and destination, get directions');
  check(((await summary()) || '').includes('4.0 km'), 'swapped route should still be 4.0 km');
  check(((await summary()) || '').includes('Office to Home'), 'summary should say Office to Home'); step('check swapped route is 4.0 km, Office to Home');
  await page.click('#saveBtn'); step('save the route');
  const savedCount = await page.evaluate(() => document.querySelectorAll('#savedList li').length);
  check(savedCount === 1, 'saved list should have 1 route, got ' + savedCount); step('check saved list has 1 route');
  await page.selectOption('#origin', 'station');
  await page.selectOption('#dest', 'library');
  await page.click('#goBtn'); step('plan Station to Library');
  check(((await summary()) || '').includes('1.2 km'), 'Station to Library should be 1.2 km'); step('check Station to Library is 1.2 km');
  await page.locator('#savedList .loadBtn').click(); step('load the saved route');
  const originVal = await page.evaluate(() => document.getElementById('origin').value);
  check(originVal === 'office', 'loading saved route should set origin to office, got ' + originVal);
  check(((await summary()) || '').includes('Office to Home'), 'summary should be Office to Home again'); step('check saved route restored Office to Home');
  await page.locator('#savedList .delBtn').click(); step('delete the saved route');
  check((await page.evaluate(() => document.querySelectorAll('#savedList li').length)) === 0, 'saved list should be empty'); step('check saved list empty');
  await page.selectOption('#origin', 'market');
  await page.selectOption('#dest', 'market');
  await page.click('#goBtn'); step('pick Market as both origin and destination, get directions');
  const err = (await page.textContent('#error')) || '';
  check(err.includes('two different places'), 'expected same-place error, got: ' + err); step('check same-place error shown');
  details = { walkMins, bikeMins, driveMins };
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
