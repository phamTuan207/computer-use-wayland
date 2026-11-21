// Safe BiDi click re-test on the LIVE Zen (post-reboot, 21/11).
// Unlike tests/puppeteer_bidi.mjs, this NEVER navigates an existing tab:
// it opens a NEW tab, loads the fixture there, tests three click variants,
// then closes the new tab and disconnects (session.end) in a finally block.
// Variants: (1) page.click (Puppeteer el.click), (2) script.evaluate el.click(),
// (3) input.performActions real pointer events.
// Every step logs one JSON line with wall-clock + elapsed ms. Exit 0 if any
// variant increments the counter, 2 otherwise.
import fs from 'node:fs';
import http from 'node:http';
import { performance } from 'node:perf_hooks';

const ENDPOINT = 'ws://127.0.0.1:9222/session';
const FIXTURE_PATH = new URL('./bidi_fixture.html', import.meta.url);

function logStep(steps, name, status, detail = {}) {
  const entry = { step: name, status, wall_clock: new Date().toISOString(), elapsed_ms: Math.round(performance.now() - steps.startedAt), ...detail };
  steps.entries.push(entry);
  console.log(JSON.stringify(entry));
  return entry;
}

async function main() {
  const steps = { startedAt: performance.now(), entries: [] };
  const wallStart = new Date().toISOString();
  let server = null;
  let browser = null;
  let page = null;
  try {
    const { default: puppeteer } = await import('puppeteer-core');
    const fixture = fs.readFileSync(FIXTURE_PATH, 'utf8');
    server = http.createServer((req, res) => {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(fixture);
    });
    await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
    const url = `http://127.0.0.1:${server.address().port}/fixture`;

    const connectStart = performance.now();
    browser = await puppeteer.connect({ browserWSEndpoint: ENDPOINT, protocol: 'webDriverBiDi', timeout: 30000 });
    logStep(steps, 'connect', 'ok', { endpoint: ENDPOINT, connect_ms: Math.round(performance.now() - connectStart) });

    const before = await browser.pages();
    logStep(steps, 'list_tabs_before', 'ok', { tab_count: before.length });

    const newStart = performance.now();
    page = await browser.newPage();
    logStep(steps, 'new_tab', 'ok', { new_ms: Math.round(performance.now() - newStart) });

    const gotoStart = performance.now();
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    logStep(steps, 'goto', 'ok', { url, goto_ms: Math.round(performance.now() - gotoStart) });

    const readStart = performance.now();
    const dom = await page.evaluate(() => ({
      title: document.title,
      counter: document.querySelector('#count')?.textContent ?? null,
    }));
    logStep(steps, 'read_dom', 'ok', { ...dom, read_ms: Math.round(performance.now() - readStart) });

    const results = {};
    // Variant 1: Puppeteer page.click
    const v1Start = performance.now();
    await page.click('#count-btn');
    results.v1_puppeteer_click = await page.$eval('#count', (el) => el.textContent);
    logStep(steps, 'click_v1_puppeteer', 'ok', { counter: results.v1_puppeteer_click, click_ms: Math.round(performance.now() - v1Start) });

    // Variant 2: script.evaluate el.click()
    const v2Start = performance.now();
    await page.evaluate(() => document.querySelector('#count-btn').click());
    results.v2_evaluate_click = await page.$eval('#count', (el) => el.textContent);
    logStep(steps, 'click_v2_evaluate', 'ok', { counter: results.v2_evaluate_click, click_ms: Math.round(performance.now() - v2Start) });

    // Variant 3: page.mouse.click at the button center (BiDi input.performActions,
    // real pointer events through the BiDi protocol, no CDP).
    const v3Start = performance.now();
    const rect = await page.evaluate(() => {
      const r = document.querySelector('#count-btn').getBoundingClientRect();
      return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
    });
    await page.mouse.click(rect.x, rect.y);
    results.v3_bidi_pointer = await page.$eval('#count', (el) => el.textContent);
    logStep(steps, 'click_v3_bidi_pointer', 'ok', { counter: results.v3_bidi_pointer, rect, click_ms: Math.round(performance.now() - v3Start) });

    const ok = Object.values(results).some((v) => v !== '0');
    console.log(JSON.stringify({ ok, results, wall_clock_start: wallStart, wall_clock_end: new Date().toISOString(), total_elapsed_ms: Math.round(performance.now() - steps.startedAt) }));
    return ok ? 0 : 2;
  } catch (error) {
    logStep(steps, 'run', 'failed', { error: String(error?.message ?? error) });
    console.log(JSON.stringify({ ok: false, error: String(error?.message ?? error), wall_clock_start: wallStart, wall_clock_end: new Date().toISOString(), total_elapsed_ms: Math.round(performance.now() - steps.startedAt) }));
    return 2;
  } finally {
    try { if (page) await page.close().catch(() => {}); } catch {}
    try { if (browser) await browser.disconnect().catch(() => {}); } catch {}
    if (server) await new Promise((resolve) => server.close(resolve));
  }
}

process.exitCode = await main();
