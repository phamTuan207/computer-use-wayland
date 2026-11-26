// daemon-send.mjs - single-shot CDP send for the speed-test warm daemon.
// Runs ON the laptop (node v26, built-in WebSocket + fetch), talking CDP
// on 127.0.0.1:9223 (Chromium/mochi) or 127.0.0.1:9224 (Brave/mei).
//
// Usage:
//   node /tmp/daemon-send.mjs <endpoint> <targetId> <message> [timeoutMs]
//   node /tmp/daemon-send.mjs --probe <endpoint> <targetId>
//     probe = read-only: ground the composer + count bubbles, no input.
//
// What it does in ONE node process (no session-driver, no cu.py, so the
// laptop session guardian never sees it and cannot refuse a second send):
//   1. count bubbles containing the message (must be 0, else already-sent)
//   2. ground the composer (visible INPUT/TEXTAREA, or contenteditable,
//      with accessible name "Message")
//   3. set_value via the native setter + input event, with read-back
//   4. focus() + activeElement proof
//   5. Enter via Input.dispatchKeyEvent keyDown/keyUp (key Enter, code 13,
//      text \r) - exactly the landed cdp.mjs key() shape
//   6. poll for the sent bubble [data-message-item] containing the message
//      (same V12 shape as /tmp/s2-v12.mjs), up to timeoutMs (default 10000)
//
// Prints exactly ONE JSON line on stdout and always exits 0 (transport
// failures are JSON too, so the caller can parse stdout unconditionally).
// No pill handling here: the daemon holds the pill around this process
// via SSH (acquire before, release after, both verified).
const mode = process.argv[2] === '--probe' ? 'probe' : 'send';
const endpoint = mode === 'probe' ? process.argv[3] : process.argv[2];
const targetId = mode === 'probe' ? process.argv[4] : process.argv[3];
const message = mode === 'probe' ? '' : process.argv[4];
const timeoutMs = parseInt((mode === 'probe' ? process.argv[5] : process.argv[5]) || '10000', 10);

const t0 = Date.now();
const timings = {};
function out(obj) {
  obj.ms_total = Date.now() - t0;
  obj.timings = timings;
  console.log(JSON.stringify(obj));
  process.exit(0);
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
function call(method, params, timeout = 5000) {
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

const GROUND_EXPR = `(() => {
  const cands = [...document.querySelectorAll('textarea, input, [contenteditable="true"]')];
  const vis = cands.filter(e => {
    const r = e.getBoundingClientRect();
    if (!r.width || !r.height) return false;
    const s = getComputedStyle(e);
    return s.display !== 'none' && s.visibility !== 'hidden';
  });
  const info = vis.map(e => ({
    tag: e.tagName, type: e.type || '', label: e.getAttribute('aria-label') || '',
    ph: e.getAttribute('placeholder') || '', ce: e.getAttribute('contenteditable') || '',
    name: (e.getAttribute('aria-label') || e.getAttribute('placeholder') || '').trim()
  }));
  const pick = vis.find(e => (e.getAttribute('aria-label') || '') === 'Message')
    || vis.find(e => ((e.getAttribute('aria-label') || '') + ' ' + (e.getAttribute('placeholder') || '')).includes('Message'))
    || vis.find(e => e.tagName === 'TEXTAREA')
    || vis[0] || null;
  if (!pick) return {found: false, candidates: info};
  pick.setAttribute('data-daemon-pick', '1');
  return {found: true, tag: pick.tagName, type: pick.type || '', label: pick.getAttribute('aria-label') || '',
    ce: pick.getAttribute('contenteditable') || '', candidates: info};
})()`;

const COUNT_EXPR = (msg) => `(() => { const items = [...document.querySelectorAll('[data-message-item]')];
  const hits = items.filter(b => (b.textContent || '').includes(${JSON.stringify(msg)}));
  return {count: hits.length, items: items.length}; })()`;

const V12_EXPR = (msg) => `(() => {
  const items = [...document.querySelectorAll('[data-message-item]')];
  const hit = items.find(b => (b.textContent || '').includes(${JSON.stringify(msg)}));
  if (!hit) return {found: false, items: items.length};
  return {found: true, items: items.length,
    role: hit.getAttribute('data-message-role'),
    side: hit.getAttribute('data-message-side'),
    textLen: (hit.textContent || '').length};
})()`;

try {
  let t = Date.now();
  const ground = await evaljs(GROUND_EXPR);
  timings.ground_ms = Date.now() - t;
  if (!ground.found) out({ok: false, error: 'composer not found', ground});
  if (mode === 'probe') out({ok: true, mode: 'probe', ground});

  t = Date.now();
  const pre = await evaljs(COUNT_EXPR(message));
  timings.count_ms = Date.now() - t;
  if (pre.count > 0) out({ok: false, outcome: 'already-sent', pre_count: pre, ground});

  // set_value: native setter + input event, with read-back.
  t = Date.now();
  const setExpr = `(() => {
    const e = document.querySelector('[data-daemon-pick="1"]');
    if (!e) return {ok: false, error: 'picked composer gone'};
    const text = ${JSON.stringify(message)};
    if (e.tagName === 'TEXTAREA' || e.tagName === 'INPUT') {
      const proto = e.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(proto, 'value').set.call(e, text);
      e.dispatchEvent(new Event('input', {bubbles: true}));
      return {ok: e.value === text, value: e.value, kind: 'native-setter'};
    }
    e.focus();
    document.execCommand('selectAll', false, null);
    const okIns = document.execCommand('insertText', false, text);
    e.dispatchEvent(new Event('input', {bubbles: true}));
    return {ok: (e.textContent || '').includes(text), text: e.textContent, kind: 'contenteditable', inserted: okIns};
  })()`;
  const setRes = await evaljs(setExpr);
  timings.set_ms = Date.now() - t;
  if (!setRes.ok) out({ok: false, error: 'set_value read-back failed', set: setRes, ground, pre_count: pre});

  // focus + activeElement proof
  t = Date.now();
  const focusRes = await evaljs(`(() => { const e = document.querySelector('[data-daemon-pick="1"]'); e.focus(); return {focused: document.activeElement === e}; })()`);
  timings.focus_ms = Date.now() - t;
  if (!focusRes.focused) out({ok: false, error: 'focus failed', focus: focusRes, ground, pre_count: pre, set: setRes});

  // Enter via CDP key events (landed cdp.mjs key() shape)
  t = Date.now();
  const keyParams = {key: 'Enter', modifiers: 0, windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 13, text: '\r'};
  await call('Input.dispatchKeyEvent', {type: 'keyDown', ...keyParams});
  await call('Input.dispatchKeyEvent', {type: 'keyUp', ...keyParams});
  timings.enter_ms = Date.now() - t;

  // V12 poll for the sent bubble
  t = Date.now();
  let result = {found: false, items: 0};
  let attempts = 0;
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    attempts++;
    try { result = await evaljs(V12_EXPR(message)); } catch (e) { result = {found: false, error: String(e).slice(0, 200)}; break; }
    if (result.found) break;
    await new Promise((r) => setTimeout(r, 250));
  }
  timings.verify_ms = Date.now() - t;
  ws.close();
  out({ok: Boolean(result.found), outcome: result.found ? 'sent' : 'failed-unverified',
    ground, pre_count: pre, set: setRes, focus: focusRes,
    v12: {...result, attempts, elapsed_ms: Date.now() - t}});
} catch (e) {
  try { ws.close(); } catch (_) {}
  out({ok: false, error: String(e).slice(0, 300)});
}
