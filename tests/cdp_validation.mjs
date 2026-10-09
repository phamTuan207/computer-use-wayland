// Run: node tests/cdp_validation.mjs. Execute production code with fake CDP; no network.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const source=fs.readFileSync(new URL('../scripts/cdp.mjs',import.meta.url),'utf8');
const keySource=source.slice(source.indexOf('async function key('),source.indexOf('async function assertAction('));
const calls=[];
const key=vm.runInNewContext(keySource+';key',{call:async (...args)=>calls.push(args)});
for(const keys of [['ctrl'],['alt','shift','meta','super'],['CTRL']]){
  await assert.rejects(key(keys),{message:'key action needs a non-modifier key'});
}
assert.equal(calls.length,0);
await key(['shift','1']);assert.equal(calls[0][1].text,'!');
console.log('ok production key rejects modifiers only before dispatch');

// Run the whole adapter: a bad later action must reject before an earlier click.
const request={operation:'act',endpoint:'http://[::1]:9222',target:'test',snapshot:'test',
               actions:[{type:'click',selector:'#button'},{type:'key',keys:['ctrl']}]};
const output=[];let sent=0,closed=false;
class WebSocket {
  addEventListener(name,fn){if(name==='open')queueMicrotask(fn);}
  send(){sent++;throw new Error('preflight must not dispatch');}
  close(){closed=true;}
}
const process={exitCode:0};
await vm.runInNewContext('(async()=>{'+source.replace(/^import .*;$/gm,'')+'})()',{
  fs:{readFileSync:()=>JSON.stringify(request)},crypto:{},URL,WebSocket,process,
  fetch:async ()=>({json:async ()=>[{type:'page',id:'test',webSocketDebuggerUrl:'ws://fake'}]}),
  AbortSignal,queueMicrotask,setTimeout,clearTimeout,console:{log:s=>output.push(JSON.parse(s))}
});
assert.equal(process.exitCode,1);
assert.equal(output[0].error,'key action needs a non-modifier key');
assert.equal(output[0].completed,0);assert.equal(sent,0);assert.equal(closed,true);
console.log('ok adapter preflight rejects modifiers only, emits reason, accepts IPv6');
