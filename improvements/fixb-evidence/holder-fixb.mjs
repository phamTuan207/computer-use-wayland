// Fix B runner-lane holder: owns the ONE BiDi session for one drive.
// Reuses the council-2 holder.mjs pattern (ponytail: no new framework).
// Differences from holder.mjs, all minimal:
// - Proxy shim only, pinned by sha256, fail loud on mismatch.
// - Descriptor probe on a data page right after tab create, fail loud.
// - RPC ops: evaluate, cookies_list (names only), cookies_delete.
// - script.removePreloadScript + session.end in the finally path.
// Usage: node holder-fixb.mjs   (no args; proxy is the only mode)
// RPC dir: /tmp/fixb-rpc (req.json -> resp.json, stop file ends it).
// ydotool is banned. Restate the ban in every brief. Never assume it.
import fs from 'node:fs';
import crypto from 'node:crypto';

const RPC = '/tmp/fixb-rpc';
fs.mkdirSync(RPC, { recursive: true });
const t0 = Date.now();
function log(obj) { console.log(JSON.stringify({ wall: new Date().toISOString(), elapsed_s: ((Date.now() - t0) / 1000).toFixed(1), ...obj })); }

const SHIM = `(() => { try { const p = Object.getPrototypeOf(navigator); const d = Object.getOwnPropertyDescriptor(p, 'webdriver'); if (d && d.get) { const fakeGet = new Proxy(d.get, { apply: () => false }); Object.defineProperty(p, 'webdriver', { get: fakeGet, configurable: true, enumerable: d.enumerable }); } } catch(e){} })()`;
const SHIM_SHA256 = 'bb49ff3f974a0534445fa5bb8eac48b47a378f39d944706b10118d5ff9d630b8';
const actual = crypto.createHash('sha256').update(SHIM).digest('hex');
if (actual !== SHIM_SHA256) { log({ step: 'fatal', error: 'shim hash mismatch ' + actual }); process.exit(2); }
log({ step: 'shim_pinned', sha256: actual, bytes: SHIM.length });

const WS_URL = 'ws://127.0.0.1:9222/session';
let ws, id = 0;
const pending = new Map();
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const myId = ++id;
    pending.set(myId, { resolve, reject, method });
    ws.send(JSON.stringify({ id: myId, method, params }));
    setTimeout(() => { if (pending.has(myId)) { pending.delete(myId); reject(new Error('timeout ' + method)); } }, 60000);
  });
}
function connect() {
  return new Promise((resolve, reject) => {
    ws = new WebSocket(WS_URL);
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
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const DESC_EXPR = `(() => {
  const proto = Object.getPrototypeOf(navigator);
  const dProto = Object.getOwnPropertyDescriptor(proto, 'webdriver');
  const dNav = Object.getOwnPropertyDescriptor(navigator, 'webdriver');
  const d = dProto || dNav;
  return {
    webdriver: navigator.webdriver,
    own_on_navigator: !!dNav,
    own_on_proto: !!dProto,
    get_name: d && d.get ? d.get.name : null,
    get_tostring: d && d.get ? String(d.get).slice(0, 80) : null,
    configurable: d ? d.configurable : null,
    enumerable: d ? d.enumerable : null,
    title: document.title,
    url: location.href
  };
})()`;

async function evaluate(context, expression) {
  const r = await send('script.evaluate', { expression, target: { context }, awaitPromise: true, resultOwnership: 'none' });
  if (r.type === 'exception') throw new Error('evaluate exception: ' + JSON.stringify(r.exceptionDetails).slice(0, 400));
  return r.result.value;
}

function unwrapRemote(v) {
  // BiDi resultOwnership none returns objects as [[key, {type, value}], ...].
  if (Array.isArray(v)) {
    const out = {};
    for (const item of v) {
      if (Array.isArray(item) && item.length === 2) out[item[0]] = unwrapRemote(item[1]);
      else return v;
    }
    return out;
  }
  if (v && typeof v === 'object' && 'type' in v && 'value' in v) return unwrapRemote(v.value);
  return v;
}

async function cookiesList(domain) {
  // Names only, never values. Full read + suffix filter: a filtered read
  // for "coolors.co" misses cookies under ".coolors.co" (observed 26/11).
  const r = await send('storage.getCookies', {});
  return (r.cookies || [])
    .filter((c) => { const d = (c.domain || '').replace(/^\./, ''); return d === domain || d.endsWith('.' + domain); })
    .map((c) => ({ name: c.name, domain: c.domain }));
}

async function cookiesDelete(domain) {
  // Returns count before/after by name list. Mechanism under test for F3.
  // Deletes per exact domain form present (covers ".host"), then sweeps.
  const before = await cookiesList(domain);
  const forms = [...new Set(before.map((c) => c.domain))];
  for (const f of forms) { await send('storage.deleteCookies', { filter: { domain: f } }); }
  await send('storage.deleteCookies', { filter: { domain } });
  const after = await cookiesList(domain);
  return { domain, before_count: before.length, after_count: after.length, before_names: before.map((c) => c.name), after_names: after.map((c) => c.name) };
}

async function main() {
  let preloadId = null;
  let context = null;
  let sessionId = null;
  try {
    log({ step: 'start' });
    await connect();
    const session = await send('session.new', { capabilities: { alwaysMatch: {} } });
    sessionId = session.sessionId;
    log({ step: 'session', sessionId });
    // Install point: immediately after session.new, before any navigation.
    const r = await send('script.addPreloadScript', { functionDeclaration: SHIM });
    preloadId = r.script;
    log({ step: 'preload_installed', preloadId });
    const ctx = await send('browsingContext.create', { type: 'tab' });
    context = ctx.context;
    log({ step: 'context_created', context });
    await send('browsingContext.navigate', { context, url: 'data:text/html,<title>wdprobe</title><body>probe</body>', wait: 'complete' });
    await sleep(1500);
    const probe = unwrapRemote(await evaluate(context, DESC_EXPR));
    log({ step: 'descriptor_probe', info: probe });
    const ok = probe.webdriver === false && probe.own_on_proto === true && probe.own_on_navigator === false && probe.get_name === 'get webdriver';
    if (!ok) throw new Error('descriptor probe mismatch: ' + JSON.stringify(probe).slice(0, 300));
    log({ step: 'probe_ok' });
    fs.writeFileSync(RPC + '/ready.json', JSON.stringify({ context, sessionId, probe, shim_sha256: SHIM_SHA256 }));

    let lastId = null;
    while (!fs.existsSync(RPC + '/stop')) {
      await sleep(400);
      let req;
      try { req = JSON.parse(fs.readFileSync(RPC + '/req.json', 'utf8')); } catch { continue; }
      if (!req || req.id === lastId) continue;
      lastId = req.id;
      let resp;
      try {
        let value;
        if (req.op === 'cookies_list') value = await cookiesList(req.domain);
        else if (req.op === 'cookies_delete') value = await cookiesDelete(req.domain);
        else value = await evaluate(context, req.expr);
        resp = { id: req.id, ok: true, value };
      } catch (e) {
        resp = { id: req.id, ok: false, error: String(e).slice(0, 400) };
      }
      fs.writeFileSync(RPC + '/resp.json', JSON.stringify(resp));
      log({ step: 'rpc_done', id: req.id, op: req.op || 'evaluate', ok: resp.ok });
    }
  } finally {
    if (preloadId) { try { await send('script.removePreloadScript', { script: preloadId }); log({ step: 'preload_removed' }); } catch (e) { log({ step: 'preload_remove_error', error: String(e).slice(0, 200) }); } }
    if (context) { try { await send('browsingContext.close', { context }); log({ step: 'context_closed' }); } catch (e) { log({ step: 'close_error', error: String(e).slice(0, 200) }); } }
    try { await send('session.end', {}); log({ step: 'session_ended' }); } catch {}
    try { ws.close(); } catch {}
    log({ step: 'done' });
    process.exit(0); // pending send() timers would otherwise linger ~60s
  }
}
main().catch((e) => { log({ step: 'fatal', error: String(e).slice(0, 500) }); process.exit(1); });
