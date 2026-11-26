// tail-read.mjs - read-only CDP tail read (all roles) for one Muse tab.
// Usage: node /tmp/tail-read.mjs <endpoint> <targetId> [count]
// Returns the last N bubbles with role/side/time + first 400 chars of text.
const endpoint = process.argv[2];
const targetId = process.argv[3];
const count = parseInt(process.argv[4] || '6', 10);
function out(obj) { console.log(JSON.stringify(obj)); process.exit(0); }
if (!endpoint || !targetId) out({ok: false, error: 'usage: node tail-read.mjs <endpoint> <targetId> [count]'});
const list = await (await fetch(endpoint + '/json/list')).json().catch((e) => { out({ok: false, error: 'json/list failed: ' + String(e).slice(0, 200)}); });
const tab = list.find((t) => t.type === 'page' && t.id === targetId);
if (!tab) out({ok: false, error: 'target not found'});
const ws = new WebSocket(tab.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = () => rej(new Error('ws open failed')); }).catch((e) => { out({ok: false, error: String(e).slice(0, 200)}); });
let seq = 0; const pending = new Map();
ws.onmessage = (ev) => { const msg = JSON.parse(ev.data); if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); } };
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
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.text || 'evaluate exception');
  return r.result.value;
}
const READ_EXPR = `(() => {
  const items = [...document.querySelectorAll('[data-message-item]')];
  return items.map((el, i) => {
    const timeEl = el.querySelector('time');
    const t = (el.textContent || '').trim();
    return { index: i, role: el.getAttribute('data-message-role') || null,
      side: el.getAttribute('data-message-side') || null,
      time: timeEl ? (timeEl.textContent || '').trim() : null,
      time_attr: timeEl ? (timeEl.getAttribute('datetime') || null) : null,
      text: t.slice(0, 400), len: t.length };
  }).filter((b) => b.len > 0);
})()`;
try {
  const items = await evaljs(READ_EXPR);
  ws.close();
  out({ok: true, endpoint, target: targetId, total_items: items.length, tail: items.slice(-count)});
} catch (e) {
  try { ws.close(); } catch (_) {}
  out({ok: false, error: String(e).slice(0, 300)});
}
