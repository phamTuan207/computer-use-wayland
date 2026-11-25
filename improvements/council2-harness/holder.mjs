// Council-2 round 3 holder: opens one BiDi session, optionally installs the
// preload shim, creates one tab, then serves evaluate requests via files in
// /tmp/council2-rpc (req.json -> resp.json) until /tmp/council2-rpc/stop exists.
// Usage: node holder.mjs <mode>   mode: baseline | preload | proxy
import fs from 'node:fs';

const mode = process.argv[2] || 'preload';
const RPC = '/tmp/council2-rpc';
fs.mkdirSync(RPC, { recursive: true });
const t0 = Date.now();
function log(obj) { console.log(JSON.stringify({ wall: new Date().toISOString(), elapsed_s: ((Date.now() - t0) / 1000).toFixed(1), mode, ...obj })); }

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

const SHIMS = {
  preload: `(() => { try { const p = Object.getPrototypeOf(navigator); if (Object.prototype.hasOwnProperty.call(p, 'webdriver')) delete p.webdriver; } catch(e){} try { Object.defineProperty(navigator, 'webdriver', { get: () => false, configurable: true }); } catch(e){} })()`,
  proxy: `(() => { try { const p = Object.getPrototypeOf(navigator); const d = Object.getOwnPropertyDescriptor(p, 'webdriver'); if (d && d.get) { const fakeGet = new Proxy(d.get, { apply: () => false }); Object.defineProperty(p, 'webdriver', { get: fakeGet, configurable: true, enumerable: d.enumerable }); } } catch(e){} })()`
};

async function evaluate(context, expression) {
  const r = await send('script.evaluate', { expression, target: { context }, awaitPromise: true, resultOwnership: 'none' });
  if (r.type === 'exception') throw new Error('evaluate exception: ' + JSON.stringify(r.exceptionDetails).slice(0, 400));
  return r.result.value;
}

async function main() {
  log({ step: 'start' });
  await connect();
  const session = await send('session.new', { capabilities: { alwaysMatch: {} } });
  log({ step: 'session', sessionId: session.sessionId });
  let preloadId = null;
  if (SHIMS[mode]) {
    const r = await send('script.addPreloadScript', { functionDeclaration: SHIMS[mode] });
    preloadId = r.script;
    log({ step: 'preload_installed', preloadId });
  }
  const ctx = await send('browsingContext.create', { type: 'tab' });
  const context = ctx.context;
  log({ step: 'context_created', context });
  fs.writeFileSync(RPC + '/ready.json', JSON.stringify({ context, mode, sessionId: session.sessionId }));

  let lastId = null;
  while (!fs.existsSync(RPC + '/stop')) {
    await sleep(400);
    let req;
    try { req = JSON.parse(fs.readFileSync(RPC + '/req.json', 'utf8')); } catch { continue; }
    if (!req || req.id === lastId) continue;
    lastId = req.id;
    let resp;
    try {
      const value = await evaluate(context, req.expr);
      resp = { id: req.id, ok: true, value };
    } catch (e) {
      resp = { id: req.id, ok: false, error: String(e).slice(0, 400) };
    }
    fs.writeFileSync(RPC + '/resp.json', JSON.stringify(resp));
    log({ step: 'rpc_done', id: req.id, ok: resp.ok });
  }

  if (preloadId) { try { await send('script.removePreloadScript', { script: preloadId }); log({ step: 'preload_removed' }); } catch (e) { log({ step: 'preload_remove_error', error: String(e).slice(0, 200) }); } }
  try { await send('browsingContext.close', { context }); log({ step: 'context_closed' }); } catch (e) { log({ step: 'close_error', error: String(e).slice(0, 200) }); }
  try { await send('session.end', {}); } catch {}
  ws.close();
  log({ step: 'done' });
}
main().catch((e) => { log({ step: 'fatal', error: String(e).slice(0, 500) }); process.exit(1); });
