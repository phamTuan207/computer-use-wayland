// C5-STEP9 focus timing: on a scratch tab, time the exact focus
// branch evaluation (unavailable checks + e.focus() + activeElement
// proof) 5 times, plus one CDP Enter and the bubble latency after it.
// Usage: node c5-focus-time.mjs <endpoint>
// Prints one JSON line. Seeded by s2-seed.mjs (same scratch shape as
// the dry run); the tab is closed at the end.
const endpoint = process.argv[2];
const out = {focus_ms: [], enter_ms: null, bubble_latency_ms: null};
const seed = await (await fetch(endpoint + '/json/new', {method: 'PUT'})).json();
const tabId = seed.id;
const ws = new WebSocket(seed.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = () => rej(new Error('ws open failed')); });
let seq = 0;
const pending = new Map();
ws.onmessage = (ev) => {
  const msg = JSON.parse(ev.data);
  if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); }
};
function call(method, params, timeoutMs = 5000) {
  return new Promise((resolve, reject) => {
    const id = ++seq;
    const t0 = Date.now();
    pending.set(id, (msg) => msg.error ? reject(new Error(msg.error.message)) : resolve({result: msg.result, ms: Date.now() - t0}));
    ws.send(JSON.stringify({id, method, params}));
    setTimeout(() => { if (pending.has(id)) { pending.delete(id); reject(new Error('timeout')); } }, timeoutMs);
  });
}
const page = `<!DOCTYPE html><html><head><title>S2-SCRATCH</title></head><body>
<div role="log" style="display:flex;flex-direction:column;gap:8px;max-width:600px;margin:40px auto;">
<div data-message-item data-message-role="assistant" data-message-side="agent">hello from the scratch thread</div>
</div>
<div style="max-width:600px;margin:0 auto;"><textarea aria-label="Message" rows="1" style="width:100%;"></textarea></div>
<script>
const ta = document.querySelector('textarea[aria-label="Message"]');
const log = document.querySelector('[role="log"]');
ta.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    const div = document.createElement('div');
    div.setAttribute('data-message-item', '');
    div.setAttribute('data-message-role', 'user');
    div.setAttribute('data-message-side', 'user');
    div.textContent = ta.value;
    log.appendChild(div);
    ta.value = '';
  }
});
</script></body></html>`;
await call('Runtime.evaluate', {expression: `document.open(); document.write(${JSON.stringify(page)}); document.close(); 'seeded';`, returnByValue: true, awaitPromise: true});
// The focus branch evaluation, verbatim shape (checks + focus + proof).
const focusExpr = `(()=>{const e=document.querySelector('textarea[aria-label="Message"]');if(!e)throw new Error('element missing; observe again');if(e.disabled||e.matches(':disabled')||e.readOnly||e.getAttribute('aria-disabled')==='true'||e.inert)throw new Error('field unavailable');e.focus();if(document.activeElement!==e)throw new Error('field is not editable or did not gain focus');return true;})()`;
for (let i = 0; i < 5; i++) {
  // Blur first so each run really re-focuses.
  await call('Runtime.evaluate', {expression: `document.activeElement&&document.activeElement.blur();'blurred';`, returnByValue: true});
  const r = await call('Runtime.evaluate', {expression: focusExpr, returnByValue: true});
  out.focus_ms.push(r.ms);
}
// Type a value, then time one CDP Enter and the bubble latency.
await call('Runtime.evaluate', {expression: `(()=>{const e=document.querySelector('textarea[aria-label="Message"]');e.value='FOCUS-TIME-TEST';return true;})()`, returnByValue: true});
const tEnter = Date.now();
await call('Input.dispatchKeyEvent', {type: 'keyDown', key: 'Enter', text: '\r', windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 13});
await call('Input.dispatchKeyEvent', {type: 'keyUp', key: 'Enter', text: '\r', windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 13});
out.enter_ms = Date.now() - tEnter;
const tBubble = Date.now();
let found = false;
for (;;) {
  const r = await call('Runtime.evaluate', {expression: `document.querySelectorAll('[data-message-item]').length`, returnByValue: true});
  if (r.result.result.value >= 2) { found = true; break; }
  if (Date.now() - tBubble > 5000) break;
  await new Promise((res) => setTimeout(res, 10));
}
out.bubble_latency_ms = found ? Date.now() - tBubble : -1;
ws.close();
try { await fetch(endpoint + '/json/close/' + tabId); } catch (_) {}
console.log(JSON.stringify(out));
