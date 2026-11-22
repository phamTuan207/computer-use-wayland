// Run: node tests/cdp_pill.mjs. CDP pill gate: every act acquires the
// overlay pill before any input and releases it after; reads never
// acquire; a failed acquire refuses the act with no input. Production
// adapter under a fake CDP/DOM; no network or GUI. The pill backend is
// the injected globalThis.__cdpPill hook: the vm harness strips import
// lines, so the real execFile backend is absent here by construction.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source = fs.readFileSync(new URL('../scripts/cdp.mjs', import.meta.url), 'utf8')
  .replace(/^import .*;$/gm, '');

async function run(request, { pill, env } = {}) {
  const calls = [];
  const order = [];
  let evaluates = 0, inputs = 0;
  const page = vm.createContext({
    document: { title: 'fixture', querySelectorAll: () => [] },
    location: { href: 'http://fixture/' }, innerWidth: 100, innerHeight: 100,
    window: { devicePixelRatio: 1, innerWidth: 100, innerHeight: 100,
      outerWidth: 100, outerHeight: 100, scrollX: 0, scrollY: 0,
      visualViewport: null },
    getComputedStyle: () => ({ visibility: 'visible', display: 'block' }),
  });
  vm.runInContext(
    "globalThis.__agentCu={id:'before',created:Date.now(),url:location.href,refs:new Map()}",
    page);
  class WebSocket {
    listeners = {};
    addEventListener(name, fn) {
      this.listeners[name] = fn;
      if (name === 'open') queueMicrotask(fn);
    }
    removeEventListener() {}
    send(raw) {
      const { id, method, params } = JSON.parse(raw);
      if (method.startsWith('Input.')) { inputs++; order.push('input'); }
      let result = {};
      if (method === 'Runtime.evaluate') {
        evaluates++; order.push('evaluate');
        try {
          result = { result: { value: vm.runInContext(params.expression, page) } };
        } catch (error) {
          result = { exceptionDetails: { text: error.message } };
        }
      } else if (method === 'Accessibility.getFullAXTree') {
        result = { nodes: [] };
      } else if (method === 'DOM.getDocument') {
        result = { root: { nodeId: 1 } };
      }
      queueMicrotask(() => this.listeners.message({ data: JSON.stringify({ id, result }) }));
    }
    close() {}
  }
  const output = [];
  const hook = pill === undefined ? {
    acquire: async (agent, method) => {
      calls.push(['acquire', agent, method]); order.push('acquire');
    },
    release: async (agent, method) => {
      calls.push(['release', agent, method]); order.push('release');
    },
  } : pill;
  const process = {
    exitCode: 0, argv: ['node', 'cdp.mjs'], env: env ?? {},
    destroy() {},
    get stdin() {
      return (async function* () { yield JSON.stringify(request); })();
    },
  };
  const sandbox = {
    crypto: { randomUUID: () => 'snapshot-test' },
    URL, WebSocket, process, AbortSignal, queueMicrotask, setTimeout, clearTimeout,
    fetch: async () => ({
      json: async () => [{ type: 'page', id: 'test', webSocketDebuggerUrl: 'ws://127.0.0.1:9222/test' }],
    }),
    console: { log: s => output.push(JSON.parse(s)) },
  };
  if (hook !== null) sandbox.__cdpPill = hook;
  const context = vm.createContext(sandbox);
  await vm.runInContext('(async()=>{' + source + '})()', context);
  assert.equal(output.length, 1, 'one envelope, got ' + JSON.stringify(output));
  return { result: output[0], calls, order, evaluates, inputs };
}

const ACT = {
  operation: 'act', endpoint: 'http://127.0.0.1:9222', target: 'test',
  snapshot: 'before', actions: [{ type: 'wait', ms: 0 }],
};

// 1. An act acquires before any evaluate/input and releases after;
// defaults name the holder Muse via CDP.
{
  const r = await run(ACT);
  assert.equal(r.result.ok, true, JSON.stringify(r.result));
  assert.deepEqual(r.calls, [['acquire', 'Muse', 'CDP'], ['release', 'Muse', 'CDP']]);
  assert.ok(r.order.indexOf('acquire') < r.order.indexOf('evaluate'),
    'pill up before first evaluate: ' + r.order.join(','));
  assert.equal(r.order[r.order.length - 1], 'release', 'pill down last: ' + r.order.join(','));
  console.log('ok act acquires the pill before any input and releases it after');
}

// 2. A validation failure acquires nothing and keeps its own error.
{
  const r = await run({ ...ACT, actions: [{ type: 'key', keys: ['ctrl'] }] });
  assert.equal(r.result.ok, false);
  assert.equal(r.result.error, 'key action needs a non-modifier key');
  assert.deepEqual(r.calls, []);
  assert.equal(r.evaluates, 0, 'no evaluate before the pill gate');
  console.log('ok validation failure acquires no pill and keeps its error');
}

// 3. Read-only operations never acquire: observe and harvest.
{
  const observed = await run({ operation: 'observe', endpoint: 'http://127.0.0.1:9222', target: 'test' });
  assert.equal(observed.result.ok !== false, true, JSON.stringify(observed.result));
  assert.deepEqual(observed.calls, [], 'observe must not raise the pill');
  const harvested = await run({ operation: 'harvest', endpoint: 'http://127.0.0.1:9222', target: 'test', selectors: [] });
  assert.equal(harvested.result.ok, true, JSON.stringify(harvested.result));
  assert.deepEqual(harvested.calls, [], 'harvest must not raise the pill');
  console.log('ok observe and harvest never raise the pill');
}

// 4. A failed acquire refuses the act with no input at all (fail closed).
{
  const failing = {
    acquire: async () => { throw new Error('daemon down'); },
    release: async () => {},
  };
  const r = await run(ACT, { pill: failing });
  assert.equal(r.result.ok, false);
  assert.match(r.result.error, /CDP pill unavailable: daemon down/);
  assert.equal(r.result.completed, 0);
  assert.equal(r.evaluates, 0, 'no evaluate when the pill cannot rise');
  assert.equal(r.inputs, 0, 'no input when the pill cannot rise');
  console.log('ok failed pill acquire refuses the act with no input');
}

// 5. CU_CDP_PILL=0 opts out (fixture tests only): the act runs, no pill.
{
  const r = await run(ACT, { pill: null, env: { CU_CDP_PILL: '0' } });
  assert.equal(r.result.ok, true, JSON.stringify(r.result));
  assert.deepEqual(r.calls, []);
  console.log('ok CU_CDP_PILL=0 opts out of the gate');
}

// 6. Request agent/method name the holder; an invalid name falls back.
{
  const r = await run({ ...ACT, agent: 'S2-flip', method: 'CDP' });
  assert.deepEqual(r.calls, [['acquire', 'S2-flip', 'CDP'], ['release', 'S2-flip', 'CDP']]);
  const bad = await run({ ...ACT, agent: 'bad name!', method: '' });
  assert.deepEqual(bad.calls, [['acquire', 'Muse', 'CDP'], ['release', 'Muse', 'CDP']]);
  console.log('ok request agent/method name the holder, invalid names fall back');
}

// 7. A release failure does not change the act result.
{
  const flaky = {
    acquire: async (agent, method) => {},
    release: async () => { throw new Error('daemon gone'); },
  };
  const r = await run(ACT, { pill: flaky });
  assert.equal(r.result.ok, true, JSON.stringify(r.result));
  console.log('ok release failure does not change the act result');
}

console.log('all cdp pill gate regressions pass');
