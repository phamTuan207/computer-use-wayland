// HCU-style batched action executor for a web page.
//
// Models the Hybrid Computer Use (HCU) AX act contract on the DOM channel:
// one call runs up to 64 ordered actions and wait steps, each target is
// re-resolved against live state before input (stale guard), and the call
// returns only a diff of what changed, not a fresh full observation.
// --mode batch runs all actions in one call. --mode single runs each action
// as its own call with a full observation before and after, which models
// the screenshot-every-step loop HCU replaces.
//
// Usage:
//   PLAYWRIGHT_PATH=/tmp/hcu-scratch/node_modules/playwright-core \
//   CHROMIUM_PATH=$HOME/.cache/ms-playwright/chromium-1254/chrome-linux64/chrome \
//     node tests/hcu_batch.mjs [--mode batch|single] [--url URL]
//     [--actions actions.json] [--timeout-ms 30000]
//
// With no --url the script serves tests/hcu_batch_fixture.html on a
// loopback HTTP server. Exit 0 on success, 2 on a failed run (guard abort
// or action failure), 3 when playwright-core is not installed.
//
// Every line printed is one JSON object with a wall-clock timestamp and
// elapsed milliseconds, plus a final summary line.

import { createRequire } from 'node:module';
import { homedir } from 'node:os';
import { readFileSync, existsSync } from 'node:fs';
import { createServer } from 'node:http';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const MAX_ACTIONS = 64;

const DEFAULT_ACTIONS = [
  { type: 'type', selector: '#name', text: 'Ada Lovelace' },
  { type: 'type', selector: '#email', text: 'ada@example.com' },
  { type: 'select', selector: '#plan', value: 'pro' },
  { type: 'check', selector: '#agree' },
  { type: 'click', selector: '#counter' },
  { type: 'click', selector: '#counter' },
  { type: 'click', selector: '#counter' },
  { type: 'click', selector: '#open-dialog' },
  { type: 'wait', selector: '#dialog.open' },
  { type: 'click', selector: '#confirm' },
  { type: 'scroll', selector: '#items', to: 'bottom' },
  { type: 'click', selector: '#save' },
];

const WATCHED = ['#name', '#email', '#plan', '#agree', '#counter', '#dialog', '#status', '#saved-count', '#items'];

function log(obj) {
  console.log(JSON.stringify({ wall_clock: new Date().toISOString(), ...obj }));
}

function fail(code, message, extra = {}) {
  log({ ok: false, code, error: message, ...extra });
  process.exit(2);
}

function parseArgs(argv) {
  const args = { mode: 'batch', timeoutMs: 30000 };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--help') { args.help = true; }
    else if (a === '--mode') { args.mode = argv[++i]; }
    else if (a === '--url') { args.url = argv[++i]; }
    else if (a === '--actions') { args.actionsFile = argv[++i]; }
    else if (a === '--timeout-ms') { args.timeoutMs = Number(argv[++i]); }
    else { fail('invalid_argument', `unknown argument: ${a}`); }
  }
  return args;
}

function validateActions(actions) {
  if (!Array.isArray(actions) || actions.length === 0) {
    fail('invalid_argument', 'actions must be a non-empty array');
  }
  if (actions.length > MAX_ACTIONS) {
    fail('invalid_argument', `batch limit is ${MAX_ACTIONS} actions, got ${actions.length}`);
  }
  const known = new Set(['click', 'type', 'select', 'check', 'scroll', 'wait', 'evaluate']);
  for (let i = 0; i < actions.length; i++) {
    const a = actions[i];
    if (!a || !known.has(a.type)) {
      fail('invalid_argument', `action ${i} has unknown type: ${a && a.type}`);
    }
    if (a.type !== 'evaluate' && typeof a.selector !== 'string') {
      fail('invalid_argument', `action ${i} (${a.type}) needs a selector`);
    }
    if (a.type === 'type' && typeof a.text !== 'string') {
      fail('invalid_argument', `action ${i} (type) needs text`);
    }
    if (a.type === 'select' && typeof a.value !== 'string') {
      fail('invalid_argument', `action ${i} (select) needs value`);
    }
    if (a.type === 'evaluate' && typeof a.expression !== 'string') {
      fail('invalid_argument', `action ${i} (evaluate) needs expression`);
    }
  }
  return actions;
}

// Read the watched state: values of the fixture fields plus scroll position.
async function observe(page) {
  const t0 = Date.now();
  const state = await page.evaluate((selectors) => {
    const out = {};
    for (const s of selectors) {
      const el = document.querySelector(s);
      if (!el) { out[s] = null; continue; }
      if (el.tagName === 'INPUT' && el.type === 'checkbox') { out[s] = el.checked; }
      else if (el.tagName === 'INPUT' || el.tagName === 'SELECT' || el.tagName === 'TEXTAREA') { out[s] = el.value; }
      else if (el.id === 'items') { out[s] = el.scrollTop; }
      else if (el.id === 'dialog') { out[s] = el.classList.contains('open'); }
      else { out[s] = el.textContent; }
    }
    return out;
  }, WATCHED);
  const domBytes = (await page.content()).length;
  return { state, domBytes, elapsed_ms: Date.now() - t0 };
}

function diffStates(before, after) {
  const diff = {};
  for (const k of Object.keys(after)) {
    if (JSON.stringify(before[k]) !== JSON.stringify(after[k])) {
      diff[k] = { before: before[k], after: after[k] };
    }
  }
  return diff;
}

// HCU stale guard: re-resolve the target against live state before input.

// HCU stale guard: re-resolve the target against live state before input.
// A reference-addressed action is fine when its element moved, because the
// reference is resolved live and the click uses the current box. It is
// rejected only when the element is missing, hidden, or disabled.
// (HCU applies its layout check, gui_frame_stale, to coordinate input
// planned from an old screenshot, not to reference-addressed actions.)
async function guard(page, action) {
  // Wait steps hold for a state that does not exist yet, so the guard
  // cannot resolve their target first. Evaluate sends no input either.
  if (action.type === 'wait' || action.type === 'evaluate') return null;
  const state = await page.evaluate((sel) => {
    const el = document.querySelector(sel);
    if (!el) return 'missing';
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) return 'hidden';
    if (el.disabled) return 'disabled';
    return 'ok';
  }, action.selector);
  if (state === 'ok') return null;
  return 'stale_ref';
}

async function runAction(page, action) {
  switch (action.type) {
    case 'click': {
      // DOM locate, then a real mouse click at the element center.
      const box = await page.locator(action.selector).boundingBox();
      if (!box) throw new Error(`no bounding box for ${action.selector}`);
      await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
      return { clicked: action.selector };
    }
    case 'type': {
      await page.locator(action.selector).click();
      await page.keyboard.type(action.text);
      return { typed: action.selector, length: action.text.length };
    }
    case 'select':
      await page.locator(action.selector).selectOption(action.value);
      return { selected: action.selector, value: action.value };
    case 'check':
      await page.locator(action.selector).check();
      return { checked: action.selector };
    case 'scroll': {
      if (action.to === 'bottom') {
        await page.evaluate((sel) => {
          const el = document.querySelector(sel);
          el.scrollTop = el.scrollHeight;
        }, action.selector);
      } else {
        await page.locator(action.selector).scrollIntoViewIfNeeded();
      }
      return { scrolled: action.selector, to: action.to || 'into-view' };
    }
    case 'wait':
      await page.locator(action.selector).waitFor({ state: 'visible', timeout: 5000 });
      return { waited: action.selector };
    case 'evaluate': {
      const value = await page.evaluate(action.expression);
      return { evaluated: action.expression, value: String(value) };
    }
    default:
      throw new Error(`unknown action type ${action.type}`);
  }
}

async function serveFixture() {
  const dir = dirname(fileURLToPath(import.meta.url));
  const html = readFileSync(join(dir, 'hcu_batch_fixture.html'), 'utf8');
  const server = createServer((req, res) => {
    res.writeHead(200, { 'content-type': 'text/html' });
    res.end(html);
  });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  return { server, url: `http://127.0.0.1:${server.address().port}/fixture` };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log('usage: node tests/hcu_batch.mjs [--mode batch|single] [--url URL] [--actions actions.json] [--timeout-ms 30000]');
    console.log('env: PLAYWRIGHT_PATH, CHROMIUM_PATH');
    process.exit(0);
  }
  if (args.mode !== 'batch' && args.mode !== 'single') {
    fail('invalid_argument', `mode must be batch or single, got ${args.mode}`);
  }
  let actions = DEFAULT_ACTIONS;
  if (args.actionsFile) {
    if (!existsSync(args.actionsFile)) fail('invalid_argument', `actions file not found: ${args.actionsFile}`);
    actions = JSON.parse(readFileSync(args.actionsFile, 'utf8'));
  }
  validateActions(actions);

  const playwrightPath = process.env.PLAYWRIGHT_PATH;
  if (!playwrightPath) {
    log({ ok: false, code: 'missing_dependency', error: 'set PLAYWRIGHT_PATH to the playwright-core package' });
    process.exit(3);
  }
  const { chromium } = createRequire(import.meta.url)(playwrightPath);
  const chromiumPath = process.env.CHROMIUM_PATH || join(homedir(), '.cache/ms-playwright/chromium-1254/chrome-linux64/chrome');

  const started = Date.now();
  const startedWall = new Date().toISOString();
  let server = null;
  let url = args.url;
  if (!url) {
    const fixture = await serveFixture();
    server = fixture.server;
    url = fixture.url;
  }
  const browser = await chromium.launch({ executablePath: chromiumPath, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  try {
    await page.goto(url, { timeout: args.timeoutMs });
    let observeMs = 0;
    let completed = 0;

    if (args.mode === 'batch') {
      const before = await observe(page);
      observeMs += before.elapsed_ms;
      for (let i = 0; i < actions.length; i++) {
        const t0 = Date.now();
        const guardCode = await guard(page, actions[i]);
        if (guardCode) {
          await browser.close();
          if (server) server.close();
          fail(guardCode, `batch stopped at step ${i}, target failed the stale guard`, { completed: i, actions: actions.length });
        }
        const result = await runAction(page, actions[i]);
        completed = i + 1;
        log({ ok: true, step: i, mode: 'batch', action: actions[i], result, elapsed_ms: Date.now() - t0 });
      }
      const after = await observe(page);
      observeMs += after.elapsed_ms;
      log({
        ok: true, mode: 'batch', actions: actions.length, completed,
        diff: diffStates(before.state, after.state),
        observe_ms: observeMs,
        total_elapsed_ms: Date.now() - started,
        wall_clock_start: startedWall, wall_clock_end: new Date().toISOString(),
      });
    } else {
      // Single mode: one full observation before and after every action.
      for (let i = 0; i < actions.length; i++) {
        const t0 = Date.now();
        const before = await observe(page);
        observeMs += before.elapsed_ms;
        const guardCode = await guard(page, actions[i]);
        if (guardCode) {
          await browser.close();
          if (server) server.close();
          fail(guardCode, `run stopped at step ${i}, target failed the stale guard`, { completed: i, actions: actions.length });
        }
        const result = await runAction(page, actions[i]);
        const after = await observe(page);
        observeMs += after.elapsed_ms;
        completed = i + 1;
        log({
          ok: true, step: i, mode: 'single', action: actions[i], result,
          diff: diffStates(before.state, after.state),
          observe_dom_bytes: after.domBytes,
          elapsed_ms: Date.now() - t0,
        });
      }
      log({
        ok: true, mode: 'single', actions: actions.length, completed,
        observe_ms: observeMs,
        total_elapsed_ms: Date.now() - started,
        wall_clock_start: startedWall, wall_clock_end: new Date().toISOString(),
      });
    }
  } finally {
    await browser.close();
    if (server) server.close();
  }
}

main().catch((err) => fail('run_failed', String(err && err.message ? err.message : err)));
