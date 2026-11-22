// Generic CDP Runtime.evaluate, read-only. Usage:
//   node c5-eval.mjs <endpoint> <targetId> <expression>
// Prints JSON.stringify of the evaluated value on the last line.
const endpoint = process.argv[2];
const targetId = process.argv[3];
const expression = process.argv[4];
const list = await (await fetch(endpoint + '/json/list')).json();
const target = list.find((t) => t.id === targetId);
if (!target) throw new Error('target not found: ' + targetId);
const ws = new WebSocket(target.webSocketDebuggerUrl);
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
const r = await call('Runtime.evaluate', {expression, returnByValue: true});
if (r && r.exceptionDetails) throw new Error('evaluate failed: ' + JSON.stringify(r.exceptionDetails).slice(0, 300));
console.log(JSON.stringify(r && r.result ? r.result.value : null));
ws.close();
process.exit(0);
