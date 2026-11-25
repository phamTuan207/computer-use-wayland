// Council-2 round 5: descriptor tells per shim variant + Google Translate
// direct check (bot-wall class R3-022). Usage: node bidi_round5.mjs <mode> <outdir>
import fs from 'node:fs';
import path from 'node:path';
const mode = process.argv[2] || 'baseline';
const outdir = process.argv[3] || '/tmp/council2-evidence';
fs.mkdirSync(outdir, { recursive: true });
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
const DESC_EXPR = `(() => {
  const proto = Object.getPrototypeOf(navigator);
  const dProto = Object.getOwnPropertyDescriptor(proto, 'webdriver');
  const dNav = Object.getOwnPropertyDescriptor(navigator, 'webdriver');
  const d = dProto || dNav;
  return {
    webdriver: navigator.webdriver,
    own_on_navigator: !!dNav,
    own_on_proto: !!dProto,
    has_get: d ? typeof d.get === 'function' : null,
    get_name: d && d.get ? d.get.name : null,
    get_tostring_start: d && d.get ? String(d.get).slice(0, 60) : null,
    configurable: d ? d.configurable : null,
    enumerable: d ? d.enumerable : null,
    title: document.title,
    url: location.href,
    body_start: (document.body ? document.body.innerText.slice(0, 200) : ''),
    has_google_sorry: location.href.includes('/sorry/'),
    has_cf_challenge: document.title.includes('Just a moment')
  };
})()`;
async function evaluate(context, expression) {
  const r = await send('script.evaluate', { expression, target: { context }, awaitPromise: true, resultOwnership: 'none' });
  if (r.type === 'exception') throw new Error('evaluate exception: ' + JSON.stringify(r.exceptionDetails).slice(0, 400));
  return r.result.value;
}
async function screenshot(context, name) {
  const r = await send('browsingContext.captureScreenshot', { context });
  const file = path.join(outdir, name + '.png');
  fs.writeFileSync(file, Buffer.from(r.data, 'base64'));
  log({ step: 'screenshot', file, bytes: fs.statSync(file).size });
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
  await send('browsingContext.navigate', { context, url: 'data:text/html,<title>wdprobe</title><body>probe</body>', wait: 'complete' });
  await sleep(2000);
  log({ step: 'descriptor', info: await evaluate(context, DESC_EXPR) });
  await send('browsingContext.navigate', { context, url: 'https://translate.google.com', wait: 'complete' }).catch((e) => log({ step: 'nav_error', error: String(e).slice(0, 200) }));
  await sleep(12000);
  log({ step: 'translate', info: await evaluate(context, DESC_EXPR) });
  await screenshot(context, mode + '-translate');
  if (preloadId) { try { await send('script.removePreloadScript', { script: preloadId }); } catch {} }
  try { await send('browsingContext.close', { context }); } catch {}
  try { await send('session.end', {}); } catch {}
  ws.close();
  log({ step: 'done' });
}
main().catch((e) => { log({ step: 'fatal', error: String(e).slice(0, 500) }); process.exit(1); });
