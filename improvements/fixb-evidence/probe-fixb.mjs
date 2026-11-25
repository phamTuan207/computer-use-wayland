// Fix B standalone probe: short BiDi session, own tab only, always ends.
// Modes:
//   node probe-fixb.mjs probe            descriptor probe, no shim (revert check)
//   node probe-fixb.mjs cookies <domain> cookie names for one domain (names only)
//   node probe-fixb.mjs delete <domain>  delete cookies for one domain, before/after counts
// Never navigates owner tabs. Creates one tab, closes it, ends session.
// ydotool is banned. Restate the ban in every brief. Never assume it.
import fs from 'node:fs';

const mode = process.argv[2] || 'probe';
const domain = process.argv[3] || '';
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

async function cookiesList(dom) {
  // Full read + suffix filter: a filtered read for "coolors.co" misses
  // cookies stored under ".coolors.co" (observed live 26/11).
  const r = await send('storage.getCookies', {});
  return (r.cookies || [])
    .filter((c) => { const d = (c.domain || '').replace(/^\./, ''); return d === dom || d.endsWith('.' + dom); })
    .map((c) => ({ name: c.name, domain: c.domain }));
}

async function main() {
  log({ step: 'start' });
  await connect();
  const session = await send('session.new', { capabilities: { alwaysMatch: {} } });
  log({ step: 'session', sessionId: session.sessionId });
  let context = null;
  try {
    if (mode === 'probe') {
      const ctx = await send('browsingContext.create', { type: 'tab' });
      context = ctx.context;
      await send('browsingContext.navigate', { context, url: 'data:text/html,<title>wdprobe</title><body>probe</body>', wait: 'complete' });
      await sleep(1500);
      log({ step: 'descriptor', info: unwrapRemote(await evaluate(context, DESC_EXPR)) });
    } else if (mode === 'cookies') {
      log({ step: 'cookies', domain, cookies: await cookiesList(domain) });
    } else if (mode === 'delete') {
      const before = await cookiesList(domain);
      log({ step: 'delete_before', domain, count: before.length, cookies: before });
      // Delete per exact domain form present (covers ".host" cookies),
      // then one filtered delete for the bare domain as a sweep.
      const forms = [...new Set(before.map((c) => c.domain))];
      for (const f of forms) { await send('storage.deleteCookies', { filter: { domain: f } }); }
      await send('storage.deleteCookies', { filter: { domain } });
      const after = await cookiesList(domain);
      log({ step: 'delete_after', domain, count: after.length, cookies: after });
    } else {
      throw new Error('unknown mode ' + mode);
    }
  } finally {
    if (context) { try { await send('browsingContext.close', { context }); } catch {} }
    try { await send('session.end', {}); } catch {}
    ws.close();
    log({ step: 'done' });
    process.exit(0); // pending send() timers would otherwise linger ~60s
  }
}
main().catch((e) => { log({ step: 'fatal', error: String(e).slice(0, 500) }); process.exit(1); });
