// Council-2 round 2: user-way arrival + fixed drive click. Node built-in WebSocket.
// Usage: node bidi_userway.mjs <mode> <outdir>   mode: baseline | preload
// User way: open Google, type query with real key input, click first organic
// result with real pointer input, record wall outcome on the landing page.
import fs from 'node:fs';
import path from 'node:path';

const mode = process.argv[2] || 'preload';
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
    setTimeout(() => { if (pending.has(myId)) { pending.delete(myId); reject(new Error('timeout ' + method)); } }, 90000);
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

const WD_EXPR = `(() => ({
  webdriver: navigator.webdriver,
  own_on_navigator: Object.prototype.hasOwnProperty.call(navigator, 'webdriver'),
  title: document.title,
  url: location.href,
  body_start: (document.body ? document.body.innerText.slice(0, 300) : ''),
  has_cf_challenge: document.title.includes('Just a moment') || (document.body?.innerText?.includes('Verify you are human') ?? false),
  has_google_sorry: location.href.includes('/sorry/') || document.title.includes('unusual traffic')
}))()`;

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
async function pointerClick(context, x, y) {
  await send('input.performActions', {
    context,
    actions: [{
      type: 'pointer', id: 'mouse', parameters: { pointerType: 'mouse' },
      actions: [
        { type: 'pointerMove', x, y },
        { type: 'pointerDown', button: 0 },
        { type: 'pointerUp', button: 0 }
      ]
    }]
  });
  await send('input.releaseActions', { context });
}
async function typeText(context, text) {
  const actions = [];
  for (const ch of text) { actions.push({ type: 'keyDown', value: ch }, { type: 'keyUp', value: ch }); }
  actions.push({ type: 'keyDown', value: 'Enter' }, { type: 'keyUp', value: 'Enter' });
  await send('input.performActions', { context, actions: [{ type: 'key', id: 'kb', actions }] });
  await send('input.releaseActions', { context });
}

async function userWayVisit(context, query, expectHost, tag) {
  log({ step: 'userway_start', tag, query, expectHost });
  const start = Date.now();
  await send('browsingContext.navigate', { context, url: 'https://www.google.com', wait: 'complete' });
  await sleep(3000);
  const box = await evaluate(context, `(() => { const el = document.querySelector('textarea[name=q], input[name=q]'); if (!el) return null; const r = el.getBoundingClientRect(); return {x: Math.round(r.left + r.width/2), y: Math.round(r.top + r.height/2)}; })()`);
  log({ step: 'search_box', tag, box });
  if (!box) { log({ step: 'userway_fail', tag, reason: 'no search box' }); await screenshot(context, tag + '-nosearch'); return; }
  await pointerClick(context, box.x, box.y);
  await sleep(500);
  await typeText(context, query);
  await sleep(5000);
  const serp = await evaluate(context, `({title: document.title, url: location.href})`);
  log({ step: 'serp', tag, serp });
  await screenshot(context, tag + '-serp');
  const link = await evaluate(context, `(() => { const as = [...document.querySelectorAll('a')]; const a = as.find(x => x.href && x.href.includes('${expectHost}') && x.querySelector('h3')); if (!a) return null; const r = a.getBoundingClientRect(); return {x: Math.round(r.left + Math.min(r.width/2, 200)), y: Math.round(r.top + r.height/2), href: a.href}; })()`);
  log({ step: 'result_link', tag, link });
  if (!link) { log({ step: 'userway_fail', tag, reason: 'no result link for host' }); return; }
  await pointerClick(context, link.x, link.y);
  await sleep(15000);
  const info = await evaluate(context, WD_EXPR);
  log({ step: 'userway_landing', tag, elapsed_s: ((Date.now() - start) / 1000).toFixed(1), info });
  await screenshot(context, tag + '-landing');
}

async function driveCheck(context, tag) {
  await send('browsingContext.navigate', { context, url: 'https://example.com', wait: 'complete' });
  await sleep(3000);
  const before = await evaluate(context, `({title: document.title, url: location.href})`);
  const pos = await evaluate(context, `(() => { const a = document.querySelector('a'); if (!a) return null; const r = a.getBoundingClientRect(); return {x: Math.round(r.left + r.width/2), y: Math.round(r.top + r.height/2), href: a.href}; })()`);
  log({ step: 'drive_before', tag, before, pos });
  if (pos) {
    await pointerClick(context, pos.x, pos.y);
    await sleep(4000);
    const after = await evaluate(context, `({title: document.title, url: location.href})`);
    log({ step: 'drive_after', tag, after, click_worked: after.url !== before.url });
  }
  await screenshot(context, tag + '-drive');
}

async function main() {
  log({ step: 'start' });
  await connect();
  const session = await send('session.new', { capabilities: { alwaysMatch: {} } });
  log({ step: 'session', sessionId: session.sessionId });
  let preloadId = null;
  if (mode === 'preload') {
    const script = `(() => { try { const p = Object.getPrototypeOf(navigator); if (Object.prototype.hasOwnProperty.call(p, 'webdriver')) delete p.webdriver; } catch(e){} try { Object.defineProperty(navigator, 'webdriver', { get: () => false, configurable: true }); } catch(e){} })()`;
    const r = await send('script.addPreloadScript', { functionDeclaration: script });
    preloadId = r.script;
    log({ step: 'preload_installed', preloadId });
  }
  const ctx = await send('browsingContext.create', { type: 'tab' });
  const context = ctx.context;
  log({ step: 'context_created', context });

  await userWayVisit(context, 'coolors color palette generator', 'coolors.co', mode + '-uw-coolors');
  await userWayVisit(context, 'chatgpt', 'chatgpt.com', mode + '-uw-chatgpt');
  await userWayVisit(context, 'timeanddate world clock', 'timeanddate.com', mode + '-uw-timeanddate');
  await userWayVisit(context, 'openverse free images', 'openverse.org', mode + '-uw-openverse');
  await driveCheck(context, mode);

  if (preloadId) { try { await send('script.removePreloadScript', { script: preloadId }); log({ step: 'preload_removed' }); } catch (e) { log({ step: 'preload_remove_error', error: String(e).slice(0, 200) }); } }
  try { await send('browsingContext.close', { context }); } catch {}
  try { await send('session.end', {}); } catch {}
  ws.close();
  log({ step: 'done' });
}
main().catch((e) => { log({ step: 'fatal', error: String(e).slice(0, 500) }); process.exit(1); });
