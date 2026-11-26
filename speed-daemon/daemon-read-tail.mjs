// read-only tail check: last N message items with roles (user + assistant).
// Runs ON the laptop via ssh mux. Usage:
//   node /tmp/daemon-read-tail.mjs <endpoint> <targetId> [count]
const endpoint = process.argv[2];
const targetId = process.argv[3];
const count = parseInt(process.argv[4] || '4', 10);
function out(obj) { console.log(JSON.stringify(obj)); process.exit(0); }
if (!endpoint || !targetId) out({ok: false, error: 'usage'});
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
    setTimeout(() => { if (pending.has(id)) { pending.delete(id); reject(new Error('CDP timeout')); } }, timeout);
  });
}
const EXPR = `(() => { const items=[...document.querySelectorAll('[data-message-item]')]; return items.map((el,i)=>{const t=el.querySelector('time'); return {index:i, role: el.getAttribute('data-message-role')||null, side: el.getAttribute('data-message-side')||null, time: t?(t.textContent||'').trim():null, time_attr: t?(t.getAttribute('datetime')||null):null, text:(el.textContent||'').trim().slice(0,300)};}).filter(b=>b.text.length>0); })()`;
try {
  const r = await call('Runtime.evaluate', {expression: EXPR, returnByValue: true, awaitPromise: true});
  if (r.exceptionDetails) throw new Error('evaluate exception');
  const items = r.result.value; ws.close();
  out({ok: true, target: targetId, total_items: items.length, tail: items.slice(-count)});
} catch (e) { try { ws.close(); } catch (_) {} out({ok: false, error: String(e).slice(0, 300)}); }
