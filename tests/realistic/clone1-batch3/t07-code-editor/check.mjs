// t07-code-editor check. Drives a demo code editor with real UI
// actions: edit, run, save and reload for persistence, switch tabs,
// dirty indicator, find, and replace. Asserts the real DOM output,
// status, and editor contents after each step.
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
  const editorVal = () => page.inputValue('#editor');
  const expectText = async (sel, wanted, what) => {
    const got = (await text(sel) || '').trim();
    if (got !== wanted) failures.push(what + ': got "' + got + '", want "' + wanted + '"');
  };
  const expectEditor = async (wanted, what) => {
    const got = await editorVal();
    if (got !== wanted) failures.push(what + ': editor is "' + got + '", want "' + wanted + '"');
  };
  const tabClass = (file) => page.getAttribute(`#tabs button[data-file="${file}"]`, 'class');

  await expectEditor('2 + 3', 'initial main.js content');
  await page.click('#run-btn');
  await expectText('#output', 'Result: 5', 'run 2 + 3');
  await page.fill('#editor', '10 * 4');
  await page.click('#run-btn');
  await expectText('#output', 'Result: 40', 'run 10 * 4');
  if (!((await tabClass('main.js')) || '').includes('dirty')) {
    failures.push('main.js tab missing dirty mark after edit');
  }
  await page.click('#save-btn');
  await expectText('#status', 'Saved main.js.', 'status after save');
  if (((await tabClass('main.js')) || '').includes('dirty')) {
    failures.push('main.js tab still dirty after save');
  }
  await page.reload();
  await expectEditor('10 * 4', 'main.js content after reload');
  await page.click('#tabs button[data-file="utils.js"]');
  await expectEditor('7 - 2', 'utils.js content');
  await page.click('#run-btn');
  await expectText('#output', 'Result: 5', 'run utils.js');
  await page.fill('#editor', '7 - 2 + 100');
  if (!((await tabClass('utils.js')) || '').includes('dirty')) {
    failures.push('utils.js tab missing dirty mark after edit');
  }
  await page.click('#tabs button[data-file="main.js"]');
  await expectEditor('10 * 4', 'main.js content after tab switch');
  await page.click('#tabs button[data-file="utils.js"]');
  await expectEditor('7 - 2 + 100', 'utils.js unsaved edit kept after tab switch');
  await page.click('#save-btn');
  await expectText('#status', 'Saved utils.js.', 'status after saving utils.js');
  await page.reload();
  await page.click('#tabs button[data-file="utils.js"]');
  await expectEditor('7 - 2 + 100', 'utils.js content after reload');
  await page.click('#tabs button[data-file="main.js"]');
  await page.fill('#find-input', '10');
  await page.click('#find-btn');
  await expectText('#find-result', '1 match', 'find 10');
  await page.fill('#replace-input', '20');
  await page.click('#replace-btn');
  await expectText('#find-result', 'Replaced.', 'replace result');
  await expectEditor('20 * 4', 'editor after replace');
  await page.click('#run-btn');
  await expectText('#output', 'Result: 80', 'run after replace');
  await page.fill('#find-input', 'zzz');
  await page.click('#find-btn');
  await expectText('#find-result', '0 matches', 'find missing text');
  await page.click('#tabs button[data-file="notes.md"]');
  await page.click('#run-btn');
  await expectText('#output', 'Error: cannot run a markdown file.', 'run markdown');
  await page.fill('#editor', '# Notes\nRemember to ship the demo.\nShip on Friday.');
  await page.click('#save-btn');
  await page.reload();
  await page.click('#tabs button[data-file="notes.md"]');
  if (!(await editorVal()).includes('Ship on Friday.')) {
    failures.push('notes.md content not persisted after reload');
  }
  await page.click('#tabs button[data-file="main.js"]');
  await page.fill('#editor', '2 +');
  await page.click('#run-btn');
  const runErr = await text('#output');
  if (!runErr.startsWith('Error:')) failures.push('invalid code did not produce an error: ' + runErr);
  await page.fill('#editor', '');
  await page.click('#run-btn');
  const emptyErr = await text('#output');
  if (!emptyErr.startsWith('Error:')) failures.push('empty code did not produce an error: ' + emptyErr);
  details.lines = await text('#lines');
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
