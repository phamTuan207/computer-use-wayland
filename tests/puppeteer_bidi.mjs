// Puppeteer over WebDriver BiDi against a running Firefox or Zen.
// Run: node tests/puppeteer_bidi.mjs [--endpoint ws://127.0.0.1:9222/session] [--url http://127.0.0.1:PORT/fixture]
// The browser must already be running with remote BiDi enabled, for example:
//   firefox --remote-debugging-port=9222 --profile /tmp/bidi-profile
//   zen --remote-debugging-port=9222 --profile /tmp/bidi-profile
// Firefox 129 and later exposes WebDriver BiDi on that port. Zen is a Firefox
// fork, so it exposes the same endpoint, but that is UNVERIFIED on this machine
// because no Firefox or Zen binary exists here.
// Requires puppeteer-core. Install it once in a scratch folder, then run with
// PUPPETEER_CORE_PATH set to that package folder, for example:
//   mkdir -p /tmp/bidi-scratch && cd /tmp/bidi-scratch && npm init -y && npm install puppeteer-core@24
//   PUPPETEER_CORE_PATH=/tmp/bidi-scratch/node_modules/puppeteer-core node tests/puppeteer_bidi.mjs
// Every step logs one JSON line with wall-clock time and elapsed milliseconds.
// Exit 0 on success, 2 on a failed run, 3 when puppeteer-core is not installed.
import fs from 'node:fs';
import http from 'node:http';
import { performance } from 'node:perf_hooks';
import { fileURLToPath } from 'node:url';

const DEFAULT_ENDPOINT = 'ws://127.0.0.1:9222/session';
const FIXTURE_PATH = new URL('./bidi_fixture.html', import.meta.url);

function parseArgs(argv) {
  const out = { endpoint: process.env.BIDI_WS ?? DEFAULT_ENDPOINT, url: null, timeoutMs: 30000, help: false };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--help' || arg === '-h') out.help = true;
    else if (arg === '--endpoint') out.endpoint = argv[i + 1] ?? out.endpoint, i += 1;
    else if (arg === '--url') out.url = argv[i + 1] ?? null, i += 1;
    else if (arg === '--timeout-ms') out.timeoutMs = Number(argv[i + 1] ?? out.timeoutMs), i += 1;
    else if (arg.startsWith('--endpoint=')) out.endpoint = arg.slice('--endpoint='.length);
    else if (arg.startsWith('--url=')) out.url = arg.slice('--url='.length);
    else if (arg.startsWith('--timeout-ms=')) out.timeoutMs = Number(arg.slice('--timeout-ms='.length));
    else throw new Error(`unknown argument: ${arg}`);
  }
  return out;
}

function logStep(steps, name, status, detail = {}) {
  const now = performance.now();
  const entry = {
    step: name,
    status,
    wall_clock: new Date().toISOString(),
    elapsed_ms: Math.round(now - steps.startedAt),
    ...detail,
  };
  steps.entries.push(entry);
  console.log(JSON.stringify(entry));
  return entry;
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help) {
    console.log('Usage: node tests/puppeteer_bidi.mjs [--endpoint ws://127.0.0.1:9222/session] [--url URL] [--timeout-ms 30000]');
    console.log('Connects to a running Firefox or Zen over WebDriver BiDi, lists tabs, reads the DOM, clicks a button, types into an input, and logs timed JSON per step.');
    return 0;
  }
  if (!Number.isFinite(options.timeoutMs) || options.timeoutMs <= 0) {
    throw new Error('timeout-ms must be a positive number');
  }
  const steps = { startedAt: performance.now(), entries: [] };
  const wallStart = new Date().toISOString();
  let server = null;
  let browser = null;
  try {
    let puppeteer;
    try {
      ({ default: puppeteer } = await import('puppeteer-core'));
    } catch {
      const fallback = process.env.PUPPETEER_CORE_PATH;
      if (!fallback) {
        console.log(JSON.stringify({ ok: false, error: 'puppeteer-core is not installed. Run: npm install puppeteer-core@24 in a scratch folder, then set PUPPETEER_CORE_PATH to its package folder.' }));
        return 3;
      }
      try {
        const { createRequire } = await import('node:module');
        const loaded = createRequire(import.meta.url)(fallback);
        puppeteer = loaded.default ?? loaded;
      } catch {
        console.log(JSON.stringify({ ok: false, error: `puppeteer-core could not be loaded from PUPPETEER_CORE_PATH: ${fallback}` }));
        return 3;
      }
    }
    let url = options.url;
    if (!url) {
      const fixture = fs.readFileSync(FIXTURE_PATH, 'utf8');
      server = http.createServer((req, res) => {
        res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
        res.end(fixture);
      });
      await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
      url = `http://127.0.0.1:${server.address().port}/fixture`;
    }
    const connectStart = performance.now();
    browser = await puppeteer.connect({
      browserWSEndpoint: options.endpoint,
      protocol: 'webDriverBiDi',
      timeout: options.timeoutMs,
    });
    logStep(steps, 'connect', 'ok', {
      endpoint: options.endpoint,
      protocol: 'webDriverBiDi',
      connect_ms: Math.round(performance.now() - connectStart),
    });
    const pagesStart = performance.now();
    const pages = await browser.pages();
    logStep(steps, 'list_tabs', 'ok', {
      tab_count: pages.length,
      tab_urls: pages.map((p) => p.url()),
      list_ms: Math.round(performance.now() - pagesStart),
    });
    const page = pages[0] ?? (await browser.newPage());
    const gotoStart = performance.now();
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: options.timeoutMs });
    logStep(steps, 'goto', 'ok', { url, goto_ms: Math.round(performance.now() - gotoStart) });
    const readStart = performance.now();
    const dom = await page.evaluate(() => ({
      title: document.title,
      heading: document.querySelector('h1')?.textContent ?? null,
      input_value: document.querySelector('#name')?.value ?? null,
      counter: document.querySelector('#count')?.textContent ?? null,
    }));
    logStep(steps, 'read_dom', 'ok', { ...dom, read_ms: Math.round(performance.now() - readStart) });
    const clickStart = performance.now();
    await page.click('#count-btn');
    const afterClick = await page.$eval('#count', (el) => el.textContent);
    logStep(steps, 'click', 'ok', {
      selector: '#count-btn',
      counter_after_click: afterClick,
      click_ms: Math.round(performance.now() - clickStart),
    });
    if (afterClick !== '1') throw new Error(`click did not increment the counter, got: ${afterClick}`);
    const typeStart = performance.now();
    await page.click('#name');
    await page.type('#name', 'bidi-test');
    const typed = await page.$eval('#name', (el) => el.value);
    logStep(steps, 'type', 'ok', {
      selector: '#name',
      typed_value: typed,
      type_ms: Math.round(performance.now() - typeStart),
    });
    if (typed !== 'bidi-test') throw new Error(`typed value mismatch, got: ${typed}`);
    const tabsStart = performance.now();
    const tabsAfter = await browser.pages();
    logStep(steps, 'list_tabs_after', 'ok', {
      tab_count: tabsAfter.length,
      list_ms: Math.round(performance.now() - tabsStart),
    });
    console.log(JSON.stringify({
      ok: true,
      wall_clock_start: wallStart,
      wall_clock_end: new Date().toISOString(),
      total_elapsed_ms: Math.round(performance.now() - steps.startedAt),
      steps: steps.entries.length,
    }));
    return 0;
  } catch (error) {
    logStep(steps, 'run', 'failed', { error: String(error?.message ?? error) });
    console.log(JSON.stringify({
      ok: false,
      error: String(error?.message ?? error),
      wall_clock_start: wallStart,
      wall_clock_end: new Date().toISOString(),
      total_elapsed_ms: Math.round(performance.now() - steps.startedAt),
    }));
    return 2;
  } finally {
    if (browser) await browser.disconnect().catch(() => {});
    if (server) await new Promise((resolve) => server.close(resolve));
  }
}

process.exitCode = await main();
