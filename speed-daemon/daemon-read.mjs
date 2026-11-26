// daemon-read.mjs - read-only CDP read for the speed daemon.
// Runs ON the laptop (node v26, built-in WebSocket + fetch), talking CDP
// on 127.0.0.1:9223 (Chromium/mochi) or 127.0.0.1:9224 (Brave/mei).
//
// Usage:
//   node /tmp/daemon-read.mjs <endpoint> <targetId> [count]
//     count = number of most recent assistant messages to return (default 5)
//
// READ-ONLY: it only fetches /json/list and runs Runtime.evaluate that
// reads the DOM. It never types, clicks, navigates, or modifies anything.
// No pill is needed (no agent control), and it never runs cu.py
// session-driver, so it cannot collide with the session guardian.
//
// What it returns (ONE JSON line on stdout, always exits 0):
//   {ok, endpoint, target, total_items, assistant_count, returned,
//    messages: [{index, role, side, time, time_attr, text}], ...}
//   messages are the most recent assistant messages (role !== 'user'),
//   oldest-first, text verbatim. time/time_attr come from a <time>
//   element inside the bubble; they are null when the bubble carries none
//   (the Muse UI shows group timestamps as separators between bubbles,
//   not inside them, so per-message time is often null).
const endpoint = process.argv[2];
const targetId = process.argv[3];
const count = parseInt(process.argv[4] || '5', 10);

const t0 = Date.now();
const timings = {};
function out(obj) {
  obj.ms_total = Date.now() - t0;
  obj.timings = timings;
  console.log(JSON.stringify(obj));
  process.exit(0);
}

if (!endpoint || !targetId) {
  out({ok: false, error: 'usage: node daemon-read.mjs <endpoint> <targetId> [count]'});
}

const list = await (await fetch(endpoint + '/json/list')).json().catch((e) => { out({ok: false, error: 'json/list failed: ' + String(e).slice(0, 200)}); });
const tab = list.find((t) => t.type === 'page' && t.id === targetId);
if (!tab) out({ok: false, error: 'target not found'});
const ws = new WebSocket(tab.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = () => rej(new Error('ws open failed')); }).catch((e) => { out({ok: false, error: String(e).slice(0, 200)}); });
let seq = 0;
const pending = new Map();
ws.onmessage = (ev) => {
  const msg = JSON.parse(ev.data);
  if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); }
};
function call(method, params, timeout = 8000) {
  return new Promise((resolve, reject) => {
    const id = ++seq;
    pending.set(id, (msg) => msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result));
    ws.send(JSON.stringify({id, method, params}));
    setTimeout(() => { if (pending.has(id)) { pending.delete(id); reject(new Error('CDP timeout: ' + method)); } }, timeout);
  });
}
async function evaljs(expr) {
  const r = await call('Runtime.evaluate', {expression: expr, returnByValue: true, awaitPromise: true});
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.text || r.exceptionDetails.exception?.description || 'evaluate exception');
  return r.result.value;
}

const READ_EXPR = `(() => {
  const items = [...document.querySelectorAll('[data-message-item]')];
  return items.map((el, i) => {
    const timeEl = el.querySelector('time');
    return {
      index: i,
      role: el.getAttribute('data-message-role') || null,
      side: el.getAttribute('data-message-side') || null,
      text: (el.textContent || '').trim(),
      time: timeEl ? (timeEl.textContent || '').trim() : null,
      time_attr: timeEl ? (timeEl.getAttribute('datetime') || null) : null
    };
  }).filter((b) => b.text.length > 0);
})()`;

try {
  let t = Date.now();
  const items = await evaljs(READ_EXPR);
  timings.read_ms = Date.now() - t;
  ws.close();
  const assistant = items.filter((b) => b.role !== 'user');
  const recent = assistant.slice(-count);
  out({ok: true, endpoint, target: targetId,
    total_items: items.length, assistant_count: assistant.length,
    returned: recent.length, messages: recent});
} catch (e) {
  try { ws.close(); } catch (_) {}
  out({ok: false, error: String(e).slice(0, 300)});
}
