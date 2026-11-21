// t01-terminal check. Drives the demo terminal fixture with real
// keyboard input: help, echo, ls, pwd, cd, cat, history, ArrowUp
// recall, clear, and an unknown command. Asserts the real DOM output
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
  const outputText = () => page.textContent('#output');
  const promptText = () => page.textContent('#prompt');
  const runCmd = async (text) => {
    await page.click('#cmd');
    await page.keyboard.type(text);
    await page.keyboard.press('Enter');
  };

  if ((await promptText()) !== '/home/demo $') failures.push('initial prompt wrong');
  await runCmd('help');
  if (!(await outputText()).includes('Available commands')) failures.push('help output missing');
  await runCmd('echo hello world');
  if (!(await outputText()).includes('hello world')) failures.push('echo output missing');
  await runCmd('ls');
  const lsOut = await outputText();
  for (const item of ['readme.txt', 'notes.txt', 'docs']) {
    if (!lsOut.includes(item)) failures.push('ls missing ' + item);
  }
  await runCmd('pwd');
  if (!(await outputText()).includes('/home/demo')) failures.push('pwd output missing');
  await runCmd('cd docs');
  if ((await promptText()) !== '/home/demo/docs $') failures.push('prompt after cd docs wrong');
  await runCmd('ls');
  if (!(await outputText()).includes('guide.txt')) failures.push('ls in docs missing guide.txt');
  await runCmd('cat guide.txt');
  if (!(await outputText()).includes('Welcome to the docs')) failures.push('cat guide.txt wrong');
  await runCmd('cat missing.txt');
  if (!(await outputText()).includes('cat: No such file: missing.txt')) failures.push('cat missing file error missing');
  await runCmd('cd ..');
  if ((await promptText()) !== '/home/demo $') failures.push('prompt after cd .. wrong');
  await runCmd('cd nowhere');
  if (!(await outputText()).includes('cd: No such directory: nowhere')) failures.push('cd bad dir error missing');
  await runCmd('cat docs');
  if (!(await outputText()).includes('cat: docs is a directory')) failures.push('cat directory error missing');
  await runCmd('history');
  const histOut = await outputText();
  for (const item of ['echo hello world', 'cd docs', 'cat docs']) {
    if (!histOut.includes(item)) failures.push('history missing ' + item);
  }
  details.historyLines = (histOut.match(/\d+\s+.*\n/g) || []).length;
  await page.click('#cmd');
  await page.keyboard.press('ArrowUp');
  const recalled = await page.inputValue('#cmd');
  if (recalled !== 'history') failures.push('ArrowUp recalled "' + recalled + '" instead of history');
  await page.keyboard.press('Enter');
  if (!(await outputText()).includes('history')) failures.push('recalled history command did not run');
  await runCmd('frobnicate');
  if (!(await outputText()).includes('command not found: frobnicate')) failures.push('unknown command error missing');
  await runCmd('clear');
  if ((await outputText()).trim() !== '') failures.push('clear did not empty output');
  await runCmd('pwd');
  if (!(await outputText()).includes('/home/demo')) failures.push('pwd after clear missing');
  if ((await promptText()) !== '/home/demo $') failures.push('prompt after clear wrong');
  await runCmd('echo final check');
  if (!(await outputText()).includes('final check')) failures.push('echo after clear missing');
  details.finalOutputLines = (await page.$$eval('#output .line', (els) => els.length));
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
