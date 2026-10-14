// Run: node tests/cdp_errors.mjs. Production adapter under a native-API-only fake
// WebSocket. No browser, no network, no GUI: frames and transports are injected.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import { Readable } from 'node:stream';

const source = fs.readFileSync(new URL('../scripts/cdp.mjs', import.meta.url), 'utf8')
  .replace(/^import .*;$/gm, '');

const ACT = { operation: 'act', endpoint: 'http://127.0.0.1:9222', target: 'test',
  snapshot: 'test', actions: [{ type: 'wait', ms: 5 }] };

async function run(request, options = {}) {
  const corrupt = options.corrupt || null;
  const output = [], timers = new Set(), requestedTimeouts = [], events = [];
  let fetches = 0, inputs = 0;
  const fixtureState = { inputEvents: 0, shots: 0 };
  const page = vm.createContext({ document: { title: 'fixture', querySelectorAll: () => [] },
    location: { href: 'http://fixture/' }, innerWidth: 100, innerHeight: 100,
    getComputedStyle: () => ({ visibility: 'visible', display: 'block' }),
    getBoundingClientRect: () => ({ left: 0, top: 0, width: 10, height: 10, right: 10, bottom: 10 }),
    __fixtureState: fixtureState });

  class WebSocket extends EventTarget {
    static CONNECTING = 0; static OPEN = 1; static CLOSING = 2; static CLOSED = 3;
    constructor() {
      super();
      this.closed = false;
      this.readyState = WebSocket.CONNECTING;
      // Only the native surface: no terminate, no resend helper.
      assert.equal(typeof this.terminate, 'undefined', 'the fake exposes only the native API');
      queueMicrotask(() => {
        if (options.neverOpen) return;
        this.readyState = WebSocket.OPEN;
        if (options.openMode === 'error') {
          events.push('error'); this.dispatchEvent(new Event('error')); return;
        }
        if (options.openMode === 'close') {
          events.push('close'); this.closed = true; this.readyState = WebSocket.CLOSED;
          this.dispatchEvent(new Event('close')); return;
        }
        events.push('open');
        this.dispatchEvent(new Event('open'));
        if (options.earlyEvent === 'error') this.dispatchEvent(new Event('error'));
        if (options.earlyEvent === 'close') this.close();
      });
    }
    send(raw) {
      const { id, method, params } = JSON.parse(raw);
      events.push(method);
      if (method.startsWith('Input.')) { inputs++; fixtureState.inputEvents++; }
      if (method === 'Page.captureScreenshot') {
        fixtureState.shots++;
        if (options.screenshotFails) {
          // CDP reports a command failure as {id,error:{message}}, not inside result.
          this.emit({ id, error: { message: 'screenshot exploded' } });
          return;
        }
        this.reply(id, { data: 'aW1n' }); return;
      }
      // An in-loop action failure: the page rejects the next evaluate.
      if (options.actionErrorAfter !== undefined && method === 'Runtime.evaluate' &&
          options.actionErrorAfter <= (options._evaluates = (options._evaluates || 0) + 1)) {
        this.emit({ id, error: { message: 'element missing' } });
        return;
      }
      if(options.mutationFails && params.expression.includes('let attempted=false')){
        this.reply(id,{result:{value:{ok:false,error:'mutation failed',mutation_may_have_occurred:true}}});return;
      }
      let value = null;
      try {
        // The staleness guard installs the page state; the snapshot expression reads it.
        if (params.expression.includes('if(!s||s.id!==')) {
          vm.runInContext('globalThis.__agentCu={id:"test",created:Date.now(),url:location.href,refs:new Map()}', page);
          value = null;
        } else value = vm.runInContext(params.expression, page);
      } catch (e) { this.reply(id, { exceptionDetails: { text: e.message } }); return; }
      this.reply(id, { result: { value } });
      if (!corrupt) return;
      // A frame with a pending reply is the dangerous one.
      if (corrupt.pending) {
        this.dispatchEvent(new MessageEvent('message', { data: corrupt.pending }));
      } else if (corrupt.idle) {
        // A frame that arrives with nothing pending, between actions.
        queueMicrotask(() => this.dispatchEvent(new MessageEvent('message', { data: corrupt.idle })));
      }
    }
    reply(id, result) {
      this.emit({ id, result });
    }
    emit(frame) {
      queueMicrotask(() => this.dispatchEvent(new MessageEvent('message', { data: JSON.stringify(frame) })));
    }
    close() {
      if (this.closed) return;
      this.closed = true; this.readyState = WebSocket.CLOSED; events.push('close');
      this.dispatchEvent(new Event('close'));
    }
  }

  const trackedSetTimeout = (fn, delay) => {
    requestedTimeouts.push(delay);
    let timer;
    timer = setTimeout(() => { timers.delete(timer); fn(); }, delay);
    timers.add(timer);
    return timer;
  };
  const trackedClearTimeout = timer => { timers.delete(timer); clearTimeout(timer); };
  const stdin = Readable.from(options.chunks ?? [JSON.stringify(request) + '\n']);
  // Single-shot mode is the one-shot CLI path: it must print the envelope, not exit.
  const process = { argv: options.single ? [] : ['node', 'cdp.mjs', '--worker'], stdin, exitCode: 0 };

  await vm.runInNewContext('(async()=>{' + source + '})()', {
    crypto: { randomUUID: () => 'errors-test' }, process, URL, WebSocket, EventTarget, Event,
    MessageEvent, AbortSignal, queueMicrotask,
    console: { log: line => output.push(JSON.parse(line)) },
    setTimeout: trackedSetTimeout, clearTimeout: trackedClearTimeout,
    fetch: async () => {
      fetches++;
      return { json: async () => [{ type: 'page', id: 'test', title: 'fixture',
        url: 'http://fixture/', webSocketDebuggerUrl: 'ws://127.0.0.1:9222/test' }] };
    },
  });
  return { output, events, fetches, inputs, pendingTimers: timers.size, requestedTimeouts,
    exitCode: process.exitCode, fixtureState };
}

// 1. A malformed frame poisons the transport even when nothing is pending, and the
//    next action in the same batch must never be dispatched.
const INPUT_BATCH = { ...ACT, actions: [{ type: 'wait', ms: 5 }, { type: 'click', selector: '#b' }] };
let r = await run(INPUT_BATCH, { corrupt: { idle: '{not json' } });
assert.equal(r.output.length, 1, 'exactly one response, never a replay');
assert.equal(r.output[0].ok, false);
assert.equal(r.output[0].completed, 1, 'the first action was already acknowledged');
assert.equal(r.fixtureState.inputEvents, 0, 'no input after the corrupt frame');
assert.ok(r.events.includes('close'), 'the owned socket was closed');
assert.equal(r.pendingTimers, 0, 'no timer survives corruption');
console.log('ok a corrupt frame stops the batch before the next input, even with nothing pending');

// 2. A malformed frame while a reply is pending rejects that call and clears every timer.
r = await run(ACT, { corrupt: { pending: '{not json' } });
assert.equal(r.output[0].ok, false);
assert.match(r.output[0].error, /malformed CDP WebSocket JSON/);
assert.equal(r.pendingTimers, 0, 'every pending timer is cleared');
assert.equal(r.exitCode, 1);
console.log('ok malformed frame with a pending reply rejects it and clears every timer');

// 3. A syntactically valid but non-object frame is a transport failure too.
for (const frame of ['null', '7', '"text"']) {
  r = await run(ACT, { corrupt: { pending: frame } });
  assert.equal(r.output[0].ok, false, frame);
  assert.match(r.output[0].error, /unexpected CDP WebSocket frame/, frame);
  assert.equal(r.pendingTimers, 0, frame);
}
console.log('ok null and primitive frames fail the transport instead of throwing in a callback');

// 4. A notification without an id is a normal CDP event, not corruption.
const notification = JSON.stringify({ method: 'Page.frameNavigated', params: {} });
r = await run(ACT, { corrupt: { idle: notification } });
assert.equal(r.output[0].ok, true, 'a notification without an id stays acceptable');
assert.ok(r.events.includes('close'), 'the normal close path still runs');
console.log('ok a notification without an id remains accepted');

// 5. The open handshake is bounded and clears its timer on every outcome.
r = await run(ACT, { neverOpen: true });
assert.equal(r.output[0].ok, false);
assert.match(r.output[0].error, /open timed out/);
assert.ok(r.requestedTimeouts.includes(4000), 'a 4s handshake budget was armed');
assert.equal(r.pendingTimers, 0, 'the handshake timer is cleared after it fires');
r = await run(ACT, { openMode: 'error' });
assert.match(r.output[0].error, /error before open/);
assert.equal(r.pendingTimers, 0);
r = await run(ACT, { openMode: 'close' });
assert.match(r.output[0].error, /closed before open/);
assert.equal(r.pendingTimers, 0);
r = await run(ACT, { earlyEvent: 'error' });
assert.equal(r.pendingTimers, 0, 'an early error still clears the handshake timer');
console.log('ok the open handshake is bounded and every early outcome clears its timer');

// 6. A screenshot failure keeps the envelope after a successful act.
r = await run({ ...ACT, image: true }, { screenshotFails: true, single: true });
assert.equal(r.output[0].ok, false);
assert.equal(r.output[0].completed, 1, 'the acknowledged action count survives');
assert.equal(typeof r.output[0].execution_ms, 'number', 'timing survives');
assert.match(r.output[0].capture_error, /screenshot exploded/);
assert.equal(r.fixtureState.shots, 1, 'the screenshot was attempted exactly once');
assert.equal(r.exitCode, 0, 'the one-shot CLI receives structured JSON instead of an adapter exit');
console.log('ok a screenshot failure keeps count, timing and exit status for the CLI');

// 7. A screenshot failure must not replace an earlier action error.
// An in-loop action failure: a false assertion with a zero budget fails immediately.
const failedAct = { ...ACT, image: true,
  actions: [{ type: 'click', selector: '#status' }] };
r = await run(failedAct, { screenshotFails: true, actionErrorAfter: 2, single: true });
assert.equal(r.output[0].ok, false);
assert.equal(r.output[0].completed, 0);
assert.match(r.output[0].error, /element missing/, 'the action error is the original one');
assert.ok(!/screenshot exploded/.test(r.output[0].error || ''), 'the original action error is kept');
assert.match(r.output[0].capture_error, /screenshot exploded/);
console.log('ok the original action error survives a later screenshot failure');

// 8. A successful act still reports ok:true with a count, and no replay happens.
//    A final observation that cannot be taken stays after_unavailable, not ok:false.
r = await run(ACT);
assert.equal(r.output[0].ok, true);
assert.equal(r.output[0].completed, 1);
assert.equal(typeof r.output[0].execution_ms, 'number');
assert.equal(r.output.length, 1, 'one response, never a replay');
assert.equal(r.fixtureState.inputEvents, 0, 'a wait batch dispatches no input');
console.log('ok a successful act reports ok:true with a count and no replay');

// 9. Worker mode stops on a failed batch rather than draining queued requests.
r = await run({ ...ACT, actions: [{ type: 'click', selector: '#b' }, { type: 'click', selector: '#c' }] },
  { actionErrorAfter: 1, chunks: [JSON.stringify({...ACT,actions:[{type:'click',selector:'#b'}]})+'\n'+JSON.stringify(ACT)+'\n'] });
assert.equal(r.output.length, 1, 'the worker stops after the first failing request');
assert.equal(r.exitCode, 1);
console.log('ok the worker stops on a failed batch and never starts the next request');

console.log('all cdp error-path, transport and envelope regressions pass');
// Exercise the actual UTF-8 stream boundary in both entry modes, including split bytes.
for(const single of [true,false]){
  const payload=Buffer.from(JSON.stringify({...ACT,padding:'é'.repeat(5*1024*1024)}));
  const chunks=(function*(){for(let i=0;i<payload.length;i+=65535)yield payload.subarray(i,i+65535);})();
  const limited=await run(ACT,{single,chunks});
  assert.equal(limited.output.length,1);
  assert.match(limited.output[0].error,/exceeds 8 MiB/);
  assert.equal(limited.fetches,0);
}
const unicode=Buffer.from(JSON.stringify({...ACT,padding:'Tiếng Việt 🙂'}));
const split=await run(ACT,{single:true,chunks:Array.from(unicode,b=>Buffer.from([b]))});
assert.equal(split.output[0].ok,true,'UTF-8 split between bytes must round-trip');

// Execute the production assertion loop against a fake clock: 9000 clamps to 3000.
const assertionSource=source.slice(source.indexOf('async function assertAction('),source.indexOf("  if(request.operation==='act'){",source.indexOf('async function assertAction(')));
let elapsed=0,evaluations=0;
const assertAction=vm.runInNewContext(assertionSource+';assertAction',{
  Date:{now:()=>elapsed},evaluate:async()=>{evaluations++;return false;},elementExpression:()=>'',
  setTimeout:(fn,ms)=>{elapsed+=ms;fn();}
});
await assert.rejects(assertAction({timeout_ms:9000,text:'missing'}),/assertion failed/);
assert.equal(elapsed,3000);assert.equal(evaluations,61);
console.log('ok UTF-8 byte streams are bounded and assertion timeout 9000 clamps to 3000');

for(const single of [true,false]){
  const result=await run({...ACT,image:true,actions:[{type:'wait',ms:0},{type:'set_value',selector:'#field',text:'x'}]},
                         {single,screenshotFails:true,mutationFails:true});
  assert.equal(result.output[0].completed,1);
  assert.equal(result.output[0].error,'mutation failed');
  assert.equal(result.output[0].mutation_may_have_occurred,true);
  assert.equal(typeof result.output[0].execution_ms,'number');
  assert.match(result.output[0].capture_error,/screenshot exploded/);
}
// Whole-batch preflight rejects every malformed later action before any CDP command.
for(const bad of [null,{type:[]},{type:'scroll',dy:true},{type:'key',keys:[1]},
                   {type:'fill',selector:'#f',text:5},{type:'assert',selector:'#f',timeout_ms:Infinity},
                   {type:'click',ref:5}]){
  const result=await run({...ACT,actions:[{type:'key',keys:['a']},bad]});
  assert.equal(result.output[0].completed,0);
  assert.equal(result.inputs,0);
  assert.equal(result.events.filter(x=>x==='Runtime.evaluate').length,0);
}
console.log('ok mutation markers and acknowledged counts survive capture errors in both entries');
