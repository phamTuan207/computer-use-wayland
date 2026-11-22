// Live Chromium scripted runner for agy-q2 pool validation (W-A1FIX, F2).
//
// Runs the SAME scripted steps as tests/realistic/agy-q2/simulate.mjs
// (page.click / page.select / page.type / page.$eval, then
// window.__agyVerify()), but against the LIVE agent Chromium on the
// laptop (CDP 127.0.0.1:9223, workspace 2) instead of a fresh headless
// instance. No model calls, no executor, no pilot arm. One fresh tab
// per test, tab closed after the test.
//
// Dependency-free Node (global WebSocket, Node 22+). No puppeteer:
// puppeteer-core is not installed on the laptop or the VM.
//
// Clicks use real CDP mouse input (Input.dispatchMouseEvent) after
// scrollIntoView, with the Chromium window visible on workspace 2.
// Typing uses Input.insertText after a real click to focus. Selects
// and direct value sets use the native setter plus input/change
// events, the same effect as puppeteer page.select / page.$eval.
// Every step is logged as one JSONL line; the gate per test is
// window.__agyVerify().passed after all spec actions ran.
//
// Usage (on the laptop):
//   node tests/realistic/agy-q2/run_live_chromium.mjs \
//     --port 9223 --base http://127.0.0.1:8768 \
//     --tests 06,07,08,09,10 --out /tmp/a1fix-20261122/f2-results.jsonl
//   node tests/realistic/agy-q2/run_live_chromium.mjs --selftest \
//     --port 9223 --base http://127.0.0.1:8768
//     (selftest: real mouse click on the pick4 "Show result" button,
//      proves the mouse pipeline works on visible workspace 2.)
//
// Exit: 0 all tests passed, 1 a test failed, 3 infra error.
// No em dash or en dash in this file.

import { writeFileSync, appendFileSync } from 'node:fs';

const args = process.argv.slice(2);
function argValue(flag, def) {
  const i = args.indexOf(flag);
  return i >= 0 ? args[i + 1] : def;
}
const PORT = argValue('--port', '9223');
const BASE = argValue('--base', 'http://127.0.0.1:8768');
const TESTS = (argValue('--tests', '06,07,08,09,10')).split(',').map(s => s.trim()).filter(Boolean);
const OUT = argValue('--out', '');
const SELFTEST = args.includes('--selftest');

const FIXTURES = {
  '06': 'test-06-file-converter.html',
  '07': 'test-07-weather-dashboard.html',
  '08': 'test-08-quiz-app.html',
  '09': 'test-09-pomodoro-timer.html',
  '10': 'test-10-markdown-editor.html',
};

function nowIso() { return new Date().toISOString(); }
function logLine(obj) {
  const line = JSON.stringify({ ts: nowIso(), ...obj });
  console.log(line);
  if (OUT) appendFileSync(OUT, line + '\n');
}

class Cdp {
  constructor(wsUrl) {
    this.ws = new WebSocket(wsUrl);
    this.nextId = 1;
    this.pending = new Map();
    this.events = [];
    this.waiters = [];
    this.ws.addEventListener('message', (ev) => {
      let msg;
      try { msg = JSON.parse(ev.data); } catch (_) { return; }
      if (msg.id && this.pending.has(msg.id)) {
        const p = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        clearTimeout(p.timer);
        if (msg.error) p.reject(new Error(msg.error.message || 'CDP error'));
        else p.resolve(msg.result || {});
      } else if (msg.method) {
        this.events.push(msg);
        for (const w of [...this.waiters]) {
          if (w.method === msg.method) {
            this.waiters.splice(this.waiters.indexOf(w), 1);
            clearTimeout(w.timer);
            w.resolve(msg);
          }
        }
      }
    });
    this.open = new Promise((resolve, reject) => {
      this.ws.addEventListener('open', () => resolve(), { once: true });
      this.ws.addEventListener('error', () => reject(new Error('CDP WebSocket error')), { once: true });
      setTimeout(() => reject(new Error('CDP WebSocket open timed out')), 10000);
    });
  }
  async waitOpen() { await this.open; }
  call(method, params = {}, sessionId = undefined, timeoutMs = 10000) {
    const id = this.nextId++;
    const payload = { id, method, params };
    if (sessionId) payload.sessionId = sessionId;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`CDP call ${method} timed out after ${timeoutMs}ms`));
      }, timeoutMs);
      this.pending.set(id, { resolve, reject, timer });
      this.ws.send(JSON.stringify(payload));
    });
  }
  dropEvents(method) {
    this.events = this.events.filter(e => e.method !== method);
    this.waiters = this.waiters.filter(w => w.method !== method);
  }
  waitEvent(method, timeoutMs = 15000) {
    for (let i = 0; i < this.events.length; i++) {
      if (this.events[i].method === method) return Promise.resolve(this.events.splice(i, 1)[0]);
    }
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        const ix = this.waiters.findIndex(w => w.resolve === resolve);
        if (ix >= 0) this.waiters.splice(ix, 1);
        reject(new Error(`wait for ${method} timed out after ${timeoutMs}ms`));
      }, timeoutMs);
      this.waiters.push({ method, resolve, timer });
    });
  }
  close() { try { this.ws.close(); } catch (_) {} }
}

async function httpJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
  return res.json();
}

class Tab {
  constructor(cdp, sessionId, targetId) {
    this.cdp = cdp;
    this.sessionId = sessionId;
    this.targetId = targetId;
  }
  call(method, params = {}, timeoutMs = 10000) {
    return this.cdp.call(method, params, this.sessionId, timeoutMs);
  }
  async eval(expression) {
    const r = await this.call('Runtime.evaluate', {
      expression, awaitPromise: true, returnByValue: true,
    }, 15000);
    if (r.exceptionDetails) {
      throw new Error('page JS exception: ' + JSON.stringify(r.exceptionDetails).slice(0, 500));
    }
    return r.result ? r.result.value : undefined;
  }
  async navigate(url) {
    // Drop stale load events from earlier tabs sharing this connection,
    // or waitEvent would return an old event and report loaded early.
    this.cdp.dropEvents('Page.loadEventFired');
    await this.call('Page.navigate', { url }, 15000);
    await this.cdp.waitEvent('Page.loadEventFired', 15000);
    // Poll until the fixture script has run: load alone does not prove
    // __agyVerify exists yet. Fail only after a real timeout.
    const deadline = Date.now() + 10000;
    for (;;) {
      const ok = await this.eval(`location.href === ${JSON.stringify(url)} && typeof window.__agyVerify === 'function'`);
      if (ok) return;
      if (Date.now() > deadline) {
        throw new Error('fixture did not reach loaded state with __agyVerify within 10s: ' + url);
      }
      await new Promise(r => setTimeout(r, 200));
    }
  }
  async rect(selector) {
    const r = await this.eval(`(() => {
      const el = document.querySelector(${JSON.stringify(selector)});
      if (!el) return null;
      el.scrollIntoView({ block: 'center' });
      const b = el.getBoundingClientRect();
      return { x: b.x, y: b.y, w: b.width, h: b.height,
        cx: b.x + b.width / 2, cy: b.y + b.height / 2,
        visible: b.width > 0 && b.height > 0 };
    })()`);
    if (!r) throw new Error(`element not found: ${selector}`);
    if (!r.visible) throw new Error(`element has zero size: ${selector}`);
    return r;
  }
  async realClick(selector) {
    const r = await this.rect(selector);
    const x = Math.round(r.cx), y = Math.round(r.cy);
    await this.call('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y, button: 'none' });
    await this.call('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 });
    await this.call('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 });
    return { x, y };
  }
  async typeText(selector, text) {
    await this.realClick(selector);
    await this.call('Input.insertText', { text });
  }
  async setValue(selector, value) {
    await this.eval(`(() => {
      const el = document.querySelector(${JSON.stringify(selector)});
      if (!el) throw new Error('missing ' + ${JSON.stringify(selector)});
      const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')
        || Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value');
      if (setter && setter.set) setter.set.call(el, ${JSON.stringify(value)});
      else el.value = ${JSON.stringify(value)};
      el.dispatchEvent(new Event('input', { bubbles: true }));
    })()`);
  }
  async selectOption(selector, value) {
    await this.eval(`(() => {
      const el = document.querySelector(${JSON.stringify(selector)});
      if (!el) throw new Error('missing ' + ${JSON.stringify(selector)});
      el.value = ${JSON.stringify(value)};
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    })()`);
  }
  async readText(selector) {
    return this.eval(`(() => {
      const el = document.querySelector(${JSON.stringify(selector)});
      return el ? el.textContent : null;
    })()`);
  }
}

// Step lists mirror simulate.mjs testSimulators '06'..'10' exactly
// (same actions, same order, same values), plus spec read-backs as
// observations (not gates). The gate is __agyVerify() at the end.
const STEPS = {
  '06': [
    ['select', '#select-source-file', 'sample-data.csv'],
    ['select', '#select-target-format', 'JSON'],
    ['select', '#select-compression', 'High'],
    ['click', '#check-preserve-meta'],
    ['click', '#btn-add-queue'],
    ['select', '#select-source-file', 'photo.png'],
    ['select', '#select-target-format', 'WEBP'],
    ['click', '#btn-add-queue'],
    ['select', '#select-source-file', 'corrupted.bin'],
    ['click', '#btn-add-queue'],
    ['read', '#status-corrupted-bin'],
    ['click', '#btn-remove-queue-corrupted-bin'],
    ['click', '#btn-convert-all'],
    ['read', '#queue-status-text'],
    ['read', '#output-count'],
    ['click', '#btn-download-sample-data-csv'],
    ['read', '#badge-download-sample-data-csv'],
    ['click', '#btn-download-photo-png'],
    ['read', '#badge-download-photo-png'],
    ['click', '#btn-save-session'],
    ['read', '#converter-status-banner'],
  ],
  '07': [
    ['click', '#btn-unit-f'],
    ['read', '#temp-tokyo'],
    ['click', '#btn-unit-c'],
    ['read', '#temp-tokyo'],
    ['select', '#select-add-city', 'ho-chi-minh-city'],
    ['click', '#btn-add-city'],
    ['read', '#temp-ho-chi-minh-city'],
    ['select', '#select-add-city', 'reykjavik'],
    ['click', '#btn-add-city'],
    ['read', '#stat-city-count'],
    ['click', '#btn-remove-city-reykjavik'],
    ['read', '#stat-city-count'],
    ['click', '#btn-primary-city-ho-chi-minh-city'],
    ['click', '#btn-unit-f'],
    ['read', '#active-unit-indicator'],
    ['read', '#temp-ho-chi-minh-city'],
    ['click', '#btn-save-weather'],
    ['read', '#weather-status-banner'],
  ],
  '08': [
    ['click', '#opt-q1-201'],
    ['click', '#btn-next-question'],
    ['click', '#opt-q2-compositor'],
    ['click', '#btn-next-question'],
    ['click', '#opt-q3-linked-list'],
    ['click', '#opt-q3-hash-table'],
    ['click', '#btn-next-question'],
    ['click', '#opt-q4-will-change'],
    ['click', '#btn-next-question'],
    ['click', '#opt-q5-sigkill'],
    ['click', '#btn-prev-question'],
    ['click', '#btn-next-question'],
    ['click', '#btn-submit-quiz'],
    ['read', '#stat-final-score'],
    ['read', '#stat-score-percent'],
    ['click', '#btn-save-quiz'],
    ['read', '#quiz-status-banner'],
  ],
  '09': [
    ['click', '#btn-open-settings'],
    ['set', '#input-work-duration', '30'],
    ['set', '#input-break-duration', '6'],
    ['click', '#check-auto-break'],
    ['click', '#btn-save-settings'],
    ['read', '#timer-display'],
    ['click', '#btn-start-pause'],
    ['click', '#btn-complete-cycle'],
    ['read', '#timer-display'],
    ['click', '#btn-complete-cycle'],
    ['read', '#timer-display'],
    ['click', '#btn-start-pause'],
    ['click', '#btn-reset-timer'],
    ['read', '#timer-display'],
    ['click', '#btn-complete-cycle'],
    ['read', '#stat-completed-cycles'],
    ['read', '#stat-total-focus'],
    ['click', '#btn-save-session'],
    ['read', '#pomodoro-status-banner'],
  ],
  '10': [
    ['set', '#input-doc-title', ''],
    ['type', '#input-doc-title', 'Release Notes v2.3.0'],
    ['setmd', '#markdown-source', '# Architecture Overview\n## Core Changes\n- Replaced X11 with native Wayland compositor\n- Added offline test validation suite\n**Zero regressions** observed in test suite.'],
    ['click', '#btn-export-html'],
    ['read', '#export-status-tag'],
    ['click', '#btn-save-doc'],
    ['read', '#editor-status-banner'],
  ],
};

async function runSteps(tab, testId) {
  const steps = STEPS[testId];
  for (let i = 0; i < steps.length; i++) {
    const [kind, selector, value] = steps[i];
    const t0 = Date.now();
    let detail = null;
    try {
      if (kind === 'click') detail = await tab.realClick(selector);
      else if (kind === 'type') await tab.typeText(selector, value);
      else if (kind === 'set') await tab.setValue(selector, value);
      else if (kind === 'setmd') {
        await tab.eval(`(() => {
          const el = document.querySelector(${JSON.stringify(selector)});
          el.value = ${JSON.stringify(value)};
          el.dispatchEvent(new Event('input', { bubbles: true }));
        })()`);
      } else if (kind === 'select') await tab.selectOption(selector, value);
      else if (kind === 'read') detail = await tab.readText(selector);
      logLine({ test: testId, step: i + 1, kind, selector, ok: true, ms: Date.now() - t0, detail });
    } catch (err) {
      logLine({ test: testId, step: i + 1, kind, selector, ok: false, ms: Date.now() - t0, error: String(err.message || err) });
      throw err;
    }
    await new Promise(r => setTimeout(r, 120));
  }
}

async function main() {
  const version = await httpJson(`http://127.0.0.1:${PORT}/json/version`);
  const cdp = new Cdp(version.webSocketDebuggerUrl);
  await cdp.waitOpen();
  try {
    await cdp.call('Target.setDiscoverTargets', { discover: true });
    if (SELFTEST) {
      const target = await cdp.call('Target.createTarget', { url: 'about:blank' });
      const targetId = target.targetId;
      const attached = await cdp.call('Target.attachToTarget', { targetId, flatten: true });
      const tab = new Tab(cdp, attached.sessionId, targetId);
      try {
        await tab.call('Page.enable');
        await tab.call('Runtime.enable');
        const t0 = Date.now();
        await tab.navigate(`${BASE}/pick4-fixture.html`);
        const clicked = await tab.realClick('button');
        const result = await tab.readText('#result');
        const ok = typeof result === 'string' && result.includes('pick4-ok');
        logLine({ selftest: true, ok, ms: Date.now() - t0, clicked, result });
        console.log(JSON.stringify({ selftest: true, mouse_pipeline_ok: ok, result }));
        process.exitCode = ok ? 0 : 1;
      } finally {
        await cdp.call('Target.closeTarget', { targetId }).catch(() => {});
      }
      return;
    }
    const results = [];
    for (const testId of TESTS) {
      const fixture = FIXTURES[testId];
      if (!fixture) throw new Error(`unknown test ${testId}`);
      const t0 = Date.now();
      const target = await cdp.call('Target.createTarget', { url: 'about:blank' });
      const targetId = target.targetId;
      const attached = await cdp.call('Target.attachToTarget', { targetId, flatten: true });
      const tab = new Tab(cdp, attached.sessionId, targetId);
      let outcome;
      try {
        await tab.call('Page.enable');
        await tab.call('Runtime.enable');
        await tab.navigate(`${BASE}/${fixture}`);
        const hasVerify = await tab.eval(`typeof window.__agyVerify === 'function'`);
        if (!hasVerify) throw new Error('__agyVerify missing after load');
        await runSteps(tab, testId);
        const verify = await tab.eval(`window.__agyVerify()`);
        outcome = {
          test: testId, fixture, passed: !!verify.passed,
          failures: verify.failures || [], score: verify.score || 0,
          state: verify.state || {}, total_ms: Date.now() - t0,
        };
      } catch (err) {
        outcome = { test: testId, fixture, passed: false, error: String(err.message || err), total_ms: Date.now() - t0 };
      } finally {
        await cdp.call('Target.closeTarget', { targetId }).catch(() => {});
      }
      logLine({ result: outcome });
      results.push(outcome);
    }
    const allPassed = results.every(r => r.passed);
    console.log(JSON.stringify({ summary: 'live chromium agy-q2', allPassed, count: results.length, results }, null, 2));
    process.exitCode = allPassed ? 0 : 1;
  } finally {
    cdp.close();
  }
}

main().catch(err => {
  console.error(JSON.stringify({ error: String(err && err.message || err) }));
  process.exit(3);
});
