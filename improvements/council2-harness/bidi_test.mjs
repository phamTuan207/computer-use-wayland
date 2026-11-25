// Council-2 BiDi test harness. Node built-in WebSocket, no deps (ponytail).
// Usage: node bidi_test.mjs <mode> <outdir>
// modes: baseline | preload | private
// Logs JSON lines to stdout with wall-clock timestamps.
import fs from 'node:fs';
import path from 'node:path';

const mode = process.argv[2] || 'baseline';
const outdir = process.argv[3] || '/tmp/council2-evidence';
fs.mkdirSync(outdir, { recursive: true });

const t0 = Date.now();
function log(obj) {
  const now = new Date();
  const wall = now.toISOString();
  console.log(JSON.stringify({ wall, elapsed_s: ((Date.now() - t0) / 1000).toFixed(1), mode, ...obj }));
}

const WS_URL = 'ws://127.0.0.1:9222/session';
let ws, id = 0;
const pending = new Map();

function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const myId = ++id;
    pending.set(myId, { resolve, reject, method });
    ws.send(JSON.stringify({ id: myId, method, params }));
    setTimeout(() => {
      if (pending.has(myId)) { pending.delete(myId); reject(new Error('timeout ' + method)); }
    }, 60000);
  });
}

function connect() {
  return new Promise((resolve, reject) => {
    ws = new WebSocket(WS_URL);
    ws.onopen = () => resolve();
    ws.onerror = (e) => reject(new Error('ws error ' + (e.message || 'unknown')));
    ws.onmessage = (ev) => {
      let msg;
      try { msg = JSON.parse(ev.data); } catch { return; }
      if (msg.id && pending.has(msg.id)) {
        const p = pending.get(msg.id);
        pending.delete(msg.id);
        if (msg.error) p.reject(new Error(p.method + ': ' + JSON.stringify(msg.error).slice(0, 400)));
        else p.resolve(msg.result);
      }
    };
  });
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const WD_EXPR = `(() => {
  const proto = Object.getPrototypeOf(navigator);
  return {
    webdriver: navigator.webdriver,
    webdriver_type: typeof navigator.webdriver,
    own_on_navigator: Object.prototype.hasOwnProperty.call(navigator, 'webdriver'),
    own_on_proto: Object.prototype.hasOwnProperty.call(proto, 'webdriver'),
    title: document.title,
    url: location.href,
    body_start: (document.body ? document.body.innerText.slice(0, 300) : ''),
    has_turnstile_iframe: !!document.querySelector('iframe[src*="challenges.cloudflare.com"]'),
    has_cf_challenge: document.title.includes('Just a moment') || document.body?.innerText?.includes('Verify you are human') || false
  };
})()`;

async function evaluate(context, expression) {
  const r = await send('script.evaluate', {
    expression,
    target: { context },
    awaitPromise: true,
    resultOwnership: 'none'
  });
  if (r.type === 'exception') throw new Error('evaluate exception: ' + JSON.stringify(r.exceptionDetails).slice(0, 400));
  return r.result.value;
}

async function screenshot(context, name) {
  const r = await send('browsingContext.captureScreenshot', { context });
  const file = path.join(outdir, name + '.png');
  fs.writeFileSync(file, Buffer.from(r.data, 'base64'));
  log({ step: 'screenshot', file, bytes: fs.statSync(file).size });
  return file;
}

async function visitSite(context, url, tag, waitMs = 20000) {
  log({ step: 'navigate', tag, url });
  const navStart = Date.now();
  try {
    await send('browsingContext.navigate', { context, url, wait: 'complete' });
  } catch (e) {
    log({ step: 'navigate_error', tag, error: String(e).slice(0, 300) });
  }
  await sleep(waitMs);
  let info = null;
  try { info = await evaluate(context, WD_EXPR); } catch (e) { log({ step: 'evaluate_error', tag, error: String(e).slice(0, 300) }); }
  log({ step: 'page_info', tag, nav_elapsed_s: ((Date.now() - navStart) / 1000).toFixed(1), info });
  await screenshot(context, tag);
  return info;
}

async function main() {
  log({ step: 'start', ws: WS_URL });
  await connect();
  log({ step: 'connected' });
  const session = await send('session.new', { capabilities: { alwaysMatch: {} } });
  log({ step: 'session', sessionId: session.sessionId, capabilities: session.capabilities?.browserName });

  let preloadId = null;
  if (mode === 'preload') {
    const script = `(() => {
      try {
        const proto = Object.getPrototypeOf(navigator);
        if (Object.prototype.hasOwnProperty.call(proto, 'webdriver')) { delete proto.webdriver; }
      } catch (e) {}
      try {
        Object.defineProperty(navigator, 'webdriver', { get: () => false, configurable: true });
      } catch (e) {}
    })()`;
    const r = await send('script.addPreloadScript', { functionDeclaration: script });
    preloadId = r.script;
    log({ step: 'preload_installed', preloadId });
  }

  let userContext = null;
  if (mode === 'private') {
    try {
      const r = await send('browser.createUserContext', {});
      userContext = r.userContext;
      log({ step: 'user_context_created', userContext });
    } catch (e) {
      log({ step: 'user_context_failed', error: String(e).slice(0, 300) });
    }
  }

  const createParams = { type: 'tab' };
  if (userContext) createParams.userContext = userContext;
  const ctx = await send('browsingContext.create', createParams);
  const context = ctx.context;
  log({ step: 'context_created', context });

  // Local webdriver probe page first (no network dependency).
  const probeUrl = 'data:text/html,<title>wdprobe</title><body>probe</body>';
  await visitSite(context, probeUrl, mode + '-probe', 3000);

  // Real sites.
  await visitSite(context, 'https://coolors.co', mode + '-coolors', 25000);
  await visitSite(context, 'https://chatgpt.com', mode + '-chatgpt', 25000);

  // Driving regression: navigate to a plain site, click first link via BiDi input, screenshot.
  try {
    await send('browsingContext.navigate', { context, url: 'https://example.com', wait: 'complete' });
    await sleep(3000);
    const before = await evaluate(context, `({title: document.title, url: location.href})`);
    const linkPos = await evaluate(context, `(() => { const a = document.querySelector('a'); if (!a) return null; const r = a.getBoundingClientRect(); return {x: Math.round(r.left + r.width/2), y: Math.round(r.top + r.height/2), href: a.href}; })()`);
    log({ step: 'drive_before', before, linkPos });
    if (linkPos) {
      await send('input.performActions', {
        context,
        actions: [{
          type: 'pointer', id: 'mouse',
          actions: [
            { type: 'pointerMove', x: linkPos.x, y: linkPos.y },
            { type: 'pointerDown', button: 0 },
            { type: 'pointerUp', button: 0 }
          ]
        }]
      });
      await sleep(4000);
      const after = await evaluate(context, `({title: document.title, url: location.href})`);
      log({ step: 'drive_after', after, click_worked: after.url !== before.url });
    }
    await screenshot(context, mode + '-drive');
  } catch (e) {
    log({ step: 'drive_error', error: String(e).slice(0, 400) });
  }

  if (preloadId) {
    try { await send('script.removePreloadScript', { script: preloadId }); log({ step: 'preload_removed' }); } catch (e) { log({ step: 'preload_remove_error', error: String(e).slice(0, 200) }); }
  }
  try { await send('browsingContext.close', { context }); log({ step: 'context_closed' }); } catch (e) { log({ step: 'close_error', error: String(e).slice(0, 200) }); }
  if (userContext) {
    try { await send('browser.removeUserContext', { userContext }); log({ step: 'user_context_removed' }); } catch (e) { log({ step: 'user_context_remove_error', error: String(e).slice(0, 200) }); }
  }
  try { await send('session.end', {}); } catch {}
  ws.close();
  log({ step: 'done' });
}

main().catch((e) => { log({ step: 'fatal', error: String(e).slice(0, 500) }); process.exit(1); });
