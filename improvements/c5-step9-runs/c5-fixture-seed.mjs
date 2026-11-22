// Held-out fixture seed: create a Chromium tab with the two-vision
// benchmark fixture (tests/two_vision_fixture.html, batch 8, locked by
// the C4 bench manifest at sha256 147494cda4c6ae24a51ced03ccdfb3fc5a79a1b
// bab56dcdfc5afb4f72fba6cbf). Usage:
//   node c5-fixture-seed.mjs <endpoint> <fixture-url>
// Prints the new tab id on the last line. Never touches a real thread.
const endpoint = process.argv[2];
const url = process.argv[3];
const created = await (await fetch(endpoint + '/json/new', {method: 'PUT'})).json();
const tabId = created.id;
const ws = new WebSocket(created.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = () => rej(new Error('ws open failed')); });
let seq = 0;
const pending = new Map();
ws.onmessage = (ev) => {
  const msg = JSON.parse(ev.data);
  if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); }
};
function call(method, params) {
  return new Promise((resolve, reject) => {
    const id = ++seq;
    pending.set(id, (msg) => msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result));
    ws.send(JSON.stringify({id, method, params}));
    setTimeout(() => { if (pending.has(id)) { pending.delete(id); reject(new Error('timeout')); } }, 10000);
  });
}
await call('Page.enable', {});
await call('Page.navigate', {url});
for (let i = 0; i < 20; i++) {
  const r = await call('Runtime.evaluate', {expression: "typeof window.__bubblePresent === 'function' ? 'ready' : 'no'", returnByValue: true});
  if (r && r.result && r.result.value === 'ready') break;
  await new Promise((res) => setTimeout(res, 500));
}
const check = await call('Runtime.evaluate', {expression: "typeof window.__bubblePresent === 'function' ? 'ready' : 'no'", returnByValue: true});
if (!check || !check.result || check.result.value !== 'ready') throw new Error('fixture not ready');
console.log(tabId);
ws.close();
process.exit(0);
