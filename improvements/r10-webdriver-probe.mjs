#!/usr/bin/env node
// webdriver-probe.mjs - ONE unified automation-signal probe (R10 Stage 1).
//
// Replaces the split probe-fixb.mjs (BiDi) / zen_dom eval (Marionette)
// readings that disagreed on R3-100. Same expression, two transports,
// one verdict vocabulary.
//
// Coverage (stated plainly): this probe certifies the page-visible
// navigator.webdriver signal, its descriptor shape, the getter
// toString form (native vs shimmed), the documentElement webdriver
// attribute, navigator.plugins length, and a fixed list of known
// automation globals. It does NOT certify TLS fingerprints, IP
// reputation, behaviour, or any signal outside that list. A CLEAN
// verdict means "these listed signals present as a normal browser",
// nothing more.
//
// Usage:
//   node webdriver-probe.mjs --transport bidi      --port 9333 --mode probe
//   node webdriver-probe.mjs --transport webdriver --port 4445 --mode probe
//   node webdriver-probe.mjs --transport bidi      --port 9333 --mode shimtest
//
// probe:    one fresh tab (BiDi) or current tab (WebDriver), one reading.
// shimtest: BiDi only. Reads a pre-existing tab before the pinned shim,
//           a new tab after addPreloadScript, the pre-existing tab after
//           reload, and a new tab after removePreloadScript. This is the
//           R3-100 disagreement reproduction.
//
// Output: one JSON object per reading on stdout.
// Exit code: 0 if every reading produced a verdict, 1 on transport error.
// ydotool is banned. Restate the ban in every brief. Never assume it.
import crypto from 'node:crypto';

const args = process.argv.slice(2);
function arg(name, dflt) {
  const i = args.indexOf('--' + name);
  return i >= 0 && args[i + 1] ? args[i + 1] : dflt;
}
const TRANSPORT = arg('transport', 'bidi');
const PORT = parseInt(arg('port', TRANSPORT === 'bidi' ? '9222' : '4444'), 10);
const MODE = arg('mode', 'probe');
const DATA_URL = 'data:text/html,<title>wdprobe</title><body>probe</body>';

const SHIM = `(() => { try { const p = Object.getPrototypeOf(navigator); const d = Object.getOwnPropertyDescriptor(p, 'webdriver'); if (d && d.get) { const fakeGet = new Proxy(d.get, { apply: () => false }); Object.defineProperty(p, 'webdriver', { get: fakeGet, configurable: true, enumerable: d.enumerable }); } } catch(e){} })()`;
const SHIM_SHA256 = 'bb49ff3f974a0534445fa5bb8eac48b47a378f39d944706b10118d5ff9d630b8';

const PROBE_EXPR = `(() => {
  const proto = Object.getPrototypeOf(navigator);
  const dProto = Object.getOwnPropertyDescriptor(proto, 'webdriver');
  const dNav = Object.getOwnPropertyDescriptor(navigator, 'webdriver');
  const d = dProto || dNav;
  const GLOBALS = ['cdc_adoQpoasnfa76pfcZLmcfl_Array','cdc_adoQpoasnfa76pfcZLmcfl_Promise','cdc_adoQpoasnfa76pfcZLmcfl_Symbol','_Selenium_IDE_Recorder','__webdriver_evaluate','__driver_evaluate','__webdriver_script_fn','__lastWatirAlert'];
  return {
    webdriver: navigator.webdriver,
    webdriver_type: typeof navigator.webdriver,
    own_on_navigator: !!dNav,
    own_on_proto: !!dProto,
    get_name: d && d.get ? d.get.name : null,
    get_tostring: d && d.get ? String(d.get) : null,
    configurable: d ? d.configurable : null,
    enumerable: d ? d.enumerable : null,
    doc_webdriver_attr: document.documentElement ? document.documentElement.getAttribute('webdriver') : null,
    plugins_length: navigator.plugins ? navigator.plugins.length : null,
    automation_globals: GLOBALS.filter((k) => k in window),
    title: document.title,
    url: location.href
  };
})()`;

function verdict(p) {
  if (!p || typeof p !== 'object') return 'UNKNOWN';
  if (p.webdriver_type === 'undefined') return 'ABSENT';
  if (p.webdriver === true) return 'DIRTY';
  if (p.webdriver === false) {
    const nativeForm = typeof p.get_tostring === 'string' && /^function webdriver\(\)/.test(p.get_tostring);
    const globalsClean = Array.isArray(p.automation_globals) && p.automation_globals.length === 0;
    const attrClean = p.doc_webdriver_attr === null || p.doc_webdriver_attr === undefined;
    if (!nativeForm) return 'SHIMMED';
    if (!globalsClean || !attrClean) return 'DIRTY-OTHER-SIGNAL';
    return 'CLEAN';
  }
  return 'UNKNOWN';
}

function emit(label, probe) {
  console.log(JSON.stringify({ transport: TRANSPORT, mode: MODE, label, verdict: verdict(probe), probe }));
}

// ---------- BiDi transport ----------
let ws, msgId = 0;
const pending = new Map();
function bidiSend(method, params = {}) {
  return new Promise((resolve, reject) => {
    const myId = ++msgId;
    pending.set(myId, { resolve, reject, method });
    ws.send(JSON.stringify({ id: myId, method, params }));
    setTimeout(() => { if (pending.has(myId)) { pending.delete(myId); reject(new Error('timeout ' + method)); } }, 30000);
  });
}
function bidiConnect() {
  return new Promise((resolve, reject) => {
    ws = new WebSocket(`ws://127.0.0.1:${PORT}/session`);
    ws.onopen = () => resolve();
    ws.onerror = (e) => reject(new Error('ws error ' + (e.message || 'unknown')));
    ws.onmessage = (ev) => {
      let msg; try { msg = JSON.parse(ev.data); } catch { return; }
      if (msg.id && pending.has(msg.id)) {
        const p = pending.get(msg.id); pending.delete(msg.id);
        if (msg.error) p.reject(new Error(p.method + ': ' + JSON.stringify(msg.error).slice(0, 400)));
        else p.resolve(msg.result);
      }
    };
  });
}
function unwrapRemote(v) {
  if (Array.isArray(v)) {
    // BiDi resultOwnership none: objects arrive as [[key, remote], ...],
    // plain arrays as [remote, ...]. Distinguish by the first element.
    if (v.length && Array.isArray(v[0]) && v[0].length === 2 && typeof v[0][0] === 'string') {
      const out = {};
      for (const item of v) out[item[0]] = unwrapRemote(item[1]);
      return out;
    }
    return v.map(unwrapRemote);
  }
  if (v && typeof v === 'object' && 'type' in v) {
    if (v.type === 'null' || v.type === 'undefined') return null;
    if ('value' in v) return unwrapRemote(v.value);
  }
  return v;
}
async function bidiEval(context, expression) {
  const r = await bidiSend('script.evaluate', { expression, target: { context }, awaitPromise: true, resultOwnership: 'none' });
  if (r.type === 'exception') throw new Error('evaluate exception: ' + JSON.stringify(r.exceptionDetails).slice(0, 400));
  return unwrapRemote(r.result.value);
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function runBidi() {
  await bidiConnect();
  const session = await bidiSend('session.new', { capabilities: { alwaysMatch: {} } });
  const created = [];
  try {
    if (MODE === 'probe') {
      const ctx = await bidiSend('browsingContext.create', { type: 'tab' });
      created.push(ctx.context);
      await bidiSend('browsingContext.navigate', { context: ctx.context, url: DATA_URL, wait: 'complete' });
      await sleep(800);
      emit('fresh_tab', await bidiEval(ctx.context, PROBE_EXPR));
    } else if (MODE === 'shimleave') {
      // Install shim, load one tab, end session WITHOUT removing the
      // preload script or closing the tab. The loaded document keeps the
      // redefined getter; a later Marionette read (sequenced, since the
      // Remote Agent allows one WebDriver session at a time) sees it.
      const actual = crypto.createHash('sha256').update(SHIM).digest('hex');
      if (actual !== SHIM_SHA256) throw new Error('shim hash mismatch ' + actual);
      await bidiSend('script.addPreloadScript', { functionDeclaration: SHIM });
      const ctx = await bidiSend('browsingContext.create', { type: 'tab' });
      await bidiSend('browsingContext.navigate', { context: ctx.context, url: DATA_URL, wait: 'complete' });
      await sleep(800);
      emit('shimleave_bidi_read', await bidiEval(ctx.context, PROBE_EXPR));
      // deliberately: no removePreloadScript, no tab close; session.end in finally
    } else if (MODE === 'shimtest') {
      const actual = crypto.createHash('sha256').update(SHIM).digest('hex');
      if (actual !== SHIM_SHA256) throw new Error('shim hash mismatch ' + actual);
      const tree = await bidiSend('browsingContext.getTree', {});
      const existing = (tree.contexts || []).map((c) => c.context);
      if (!existing.length) throw new Error('no pre-existing context in getTree');
      const pre = existing[0];
      await bidiSend('browsingContext.navigate', { context: pre, url: DATA_URL, wait: 'complete' });
      await sleep(800);
      emit('preexisting_before_shim', await bidiEval(pre, PROBE_EXPR));
      const r = await bidiSend('script.addPreloadScript', { functionDeclaration: SHIM });
      const preloadId = r.script;
      try {
        const ctx = await bidiSend('browsingContext.create', { type: 'tab' });
        created.push(ctx.context);
        await bidiSend('browsingContext.navigate', { context: ctx.context, url: DATA_URL, wait: 'complete' });
        await sleep(800);
        emit('newtab_after_shim', await bidiEval(ctx.context, PROBE_EXPR));
        await bidiSend('browsingContext.navigate', { context: pre, url: DATA_URL, wait: 'complete' });
        await sleep(800);
        emit('preexisting_after_shim_reload', await bidiEval(pre, PROBE_EXPR));
      } finally {
        await bidiSend('script.removePreloadScript', { script: preloadId });
      }
      const ctx2 = await bidiSend('browsingContext.create', { type: 'tab' });
      created.push(ctx2.context);
      await bidiSend('browsingContext.navigate', { context: ctx2.context, url: DATA_URL, wait: 'complete' });
      await sleep(800);
      emit('newtab_after_remove', await bidiEval(ctx2.context, PROBE_EXPR));
    } else {
      throw new Error('unknown mode ' + MODE);
    }
  } finally {
    for (const c of created) { try { await bidiSend('browsingContext.close', { context: c }); } catch {} }
    try { await bidiSend('session.end', {}); } catch {}
    try { ws.close(); } catch {}
  }
}

// ---------- WebDriver (geckodriver connect-existing) transport ----------
async function wd(method, path, body) {
  const res = await fetch(`http://127.0.0.1:${PORT}${path}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  let parsed; try { parsed = JSON.parse(text); } catch { throw new Error(`non-JSON from ${method} ${path}: ${text.slice(0, 200)}`); }
  if (!res.ok) throw new Error(`HTTP ${res.status} on ${method} ${path}: ${text.slice(0, 300)}`);
  return parsed;
}

async function runWebDriver() {
  if (MODE !== 'probe') throw new Error('webdriver transport supports probe mode only');
  const noNav = args.includes('--no-navigate');
  const sess = await wd('POST', '/session', { capabilities: { alwaysMatch: {} } });
  const sid = sess.value.sessionId;
  try {
    if (noNav) {
      const handles = (await wd('GET', `/session/${sid}/window/handles`)).value;
      if (Array.isArray(handles) && handles.length) {
        await wd('POST', `/session/${sid}/window`, { handle: handles[handles.length - 1] });
      }
    } else {
      await wd('POST', `/session/${sid}/url`, { url: DATA_URL });
      await sleep(800);
    }
    const r = await wd('POST', `/session/${sid}/execute/sync`, { script: 'return (' + PROBE_EXPR + ');', args: [] });
    emit(noNav ? 'last_tab_no_navigate' : 'current_tab', r.value);
  } finally {
    try { await wd('DELETE', `/session/${sid}`); } catch {}
  }
}

(async () => {
  try {
    if (TRANSPORT === 'bidi') await runBidi();
    else if (TRANSPORT === 'webdriver') await runWebDriver();
    else throw new Error('unknown transport ' + TRANSPORT);
    process.exit(0);
  } catch (e) {
    console.log(JSON.stringify({ transport: TRANSPORT, mode: MODE, label: 'error', verdict: 'ERROR', error: String(e).slice(0, 500) }));
    process.exit(1);
  }
})();
