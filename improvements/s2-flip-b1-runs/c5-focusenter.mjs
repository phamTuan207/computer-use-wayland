// C5-FOCUSENTER: focus the composer + CDP Enter (variant B).
// Usage: node /tmp/c5-focusenter.mjs <endpoint> <targetId>
// 1. Runtime.evaluate: focus textarea[aria-label="Message"], assert
//    it is document.activeElement. 2. Input.dispatchKeyEvent keyDown
//    + keyUp Enter (trusted CDP event, goes to the focused composer).
// No mouse event, no click, no typing. Prints one JSON line.
const endpoint = process.argv[2];
const targetId = process.argv[3];
const list = await (await fetch(endpoint + '/json/list')).json();
const tab = list.find(t => t.id === targetId);
if (!tab) { console.log(JSON.stringify({ok: false, error: 'tab not found'})); process.exit(0); }
const ws = new WebSocket(tab.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = () => rej(new Error('ws open failed')); });
let seq = 0; const pending = new Map();
ws.onmessage = (ev) => {
  const msg = JSON.parse(ev.data);
  if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); }
};
function call(method, params, timeoutMs = 5000) {
  return new Promise((resolve, reject) => {
    const id = ++seq;
    pending.set(id, (msg) => msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result));
    ws.send(JSON.stringify({id, method, params}));
    setTimeout(() => { if (pending.has(id)) { pending.delete(id); reject(new Error('CDP timeout: ' + method)); } }, timeoutMs);
  });
}
const out = {ok: true};
try {
  const r = await call('Runtime.evaluate', {expression: `(() => { const e = document.querySelector('textarea[aria-label="Message"]'); if (!e) return {focused: false, error: 'no-textarea'}; e.focus(); return {focused: document.activeElement === e, tag: e.tagName}; })()`, returnByValue: true, awaitPromise: true});
  if (r.exceptionDetails) throw new Error('evaluate exception: ' + (r.exceptionDetails.text || ''));
  out.focus = r.result.value;
  if (!out.focus.focused) throw new Error('composer did not gain focus');
  const t0 = Date.now();
  await call('Input.dispatchKeyEvent', {type: 'keyDown', key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 13, text: '\r'});
  await call('Input.dispatchKeyEvent', {type: 'keyUp', key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 13});
  out.enter = {ms: Date.now() - t0, ok: true};
} catch (e) {
  out.ok = false; out.error = String(e).slice(0, 200);
}
console.log(JSON.stringify(out));
ws.close();
process.exit(0);
