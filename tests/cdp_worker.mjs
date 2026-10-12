// Run: node tests/cdp_worker.mjs. Fake stdin/CDP/DOM, no network or GUI.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import { createInterface } from 'node:readline';
import { Readable } from 'node:stream';

const source=fs.readFileSync(new URL('../scripts/cdp.mjs',import.meta.url),'utf8');
const request={operation:'observe',endpoint:'http://127.0.0.1:9222',target:'test'};
async function run(requests,{connectError=false,fetchError=false,debuggerUrl='ws://127.0.0.1:9222/test',single=false}={}) {
  const output=[],events=[],sockets=[];
  let fetches=0,frames=0;
  const page=vm.createContext({document:{title:'fixture',querySelectorAll:()=>[]},
    location:{href:'http://fixture/'},innerWidth:100,innerHeight:100});
  class WebSocket {
    listeners={};
    constructor(){
      assert.ok(sockets.every(s=>s.closed),'previous request socket must close first');
      this.closed=false;sockets.push(this);events.push('connect');
    }
    addEventListener(name,fn){
      this.listeners[name]=fn;
      if(name==='open'&&!connectError)queueMicrotask(fn);
      if(name==='error'&&connectError)queueMicrotask(()=>fn(new Error('connect failed')));
    }
    send(raw){
      const {id,method,params}=JSON.parse(raw);let result;
      frames++;events.push(method);
      assert.equal(method,'Runtime.evaluate');
      try{result={result:{value:vm.runInContext(params.expression,page)}};}
      catch(e){result={exceptionDetails:{text:e.message}};}
      queueMicrotask(()=>this.listeners.message({data:JSON.stringify({id,result})}));
    }
    close(){assert.equal(this.closed,false);this.closed=true;events.push('close');}
  }
  const lines=requests.map(value=>typeof value==='string'?value:JSON.stringify(value));
  const stdin=Readable.from([lines.join('\n')+(lines.length?'\n':'')]);
  const process={argv:single?[]:['node','cdp.mjs','--worker'],stdin,exitCode:0};
  await vm.runInNewContext('(async()=>{'+source.replace(/^import .*;$/gm,'')+'})()',{
    fs:{readFileSync:()=>lines[0]},crypto:{randomUUID:()=> 'snapshot-'+fetches},
    createInterface,process,URL,WebSocket,AbortSignal,queueMicrotask,setTimeout,clearTimeout,
    fetch:async()=>{
      fetches++;events.push('fetch');
      if(fetchError)throw new Error('fetch failed');
      return {json:async()=>[{type:'page',id:'test',title:'fixture',url:'http://fixture/',
        webSocketDebuggerUrl:debuggerUrl},{type:'worker',id:'ignored'}]};
    },
    console:{log:line=>{output.push(JSON.parse(line));events.push('response');}}
  });
  assert.ok(sockets.every(s=>s.closed));
  if(!single)assert.equal(stdin.destroyed,true);
  return {output,events,fetches,frames,sockets,exitCode:process.exitCode};
}

let result=await run([request,request]);
assert.equal(result.output.length,2);
assert.equal(result.output[0].snapshot,'snapshot-1');
assert.equal(result.output[1].snapshot,'snapshot-2');
assert.equal(result.sockets.length,2);
assert.deepEqual(result.events,['fetch','connect','Runtime.evaluate','close','response',
  'fetch','connect','Runtime.evaluate','close','response']);
assert.equal(result.exitCode,0);

result=await run([{...request,operation:'tabs'},{...request,operation:'tabs'}]);
assert.equal(result.output.length,2);
assert.deepEqual(result.output[0],[{id:'test',title:'fixture',url:'http://fixture/'}]);
assert.deepEqual(result.output[1],result.output[0]);
assert.equal(result.sockets.length,0);
assert.equal(result.exitCode,0);

// Both an action result failure and a preflight throw stop queued input.
const errors=[
  [{...request,operation:'act',actions:[]},'--snapshot required'],
  [{...request,operation:'act',snapshot:'missing',actions:[{type:'key',keys:['ctrl']}]},'key action needs a non-modifier key'],
  [{...request,operation:'act',snapshot:'missing',actions:[{type:'key',keys:['a']}]},'stale snapshot'],
  [{...request,max_elements:0},'max_elements must be 1..80'],
  [{...request,endpoint:'http://outside.example'},'CDP endpoint must be loopback'],
  [{...request,target:'missing'},'exact --target required; use browser tabs'],
];
for(const [bad,message] of errors){
  result=await run([bad,request]);
  assert.equal(result.output.length,1);
  assert.equal(result.output[0].ok,false);
  assert.ok(result.output[0].error.includes(message));
  assert.equal(result.exitCode,1);
  assert.ok(result.fetches<=1);
}
for(const options of [{fetchError:true},{connectError:true},
  {debuggerUrl:'ws://outside.example/test'}]){
  result=await run([request,request],options);
  assert.equal(result.output.length,1);
  assert.equal(result.output[0].ok,false);
  assert.equal(result.fetches,1);
  assert.equal(result.exitCode,1);
}
result=await run(['{malformed',request]);
assert.equal(result.output.length,1);
assert.equal(result.output[0].ok,false);
assert.equal(result.output[0].completed,0);
assert.equal(result.fetches,0);
assert.equal(result.exitCode,1);
assert.equal((await run([])).output.length,0);

// Tabs still emit exactly one array and succeed in single-shot mode.
result=await run([{...request,operation:'tabs'}],{single:true});
assert.equal(result.output.length,1);
assert.equal(result.exitCode,0);
result=await run([{...request,operation:'act',snapshot:'missing',actions:[{type:'key',keys:['a']}]}],{single:true});
assert.equal(result.output[0].ok,false);
assert.equal(result.exitCode,0); // Preserve the legacy action-result exit status.
result=await run([{...request,operation:'act',snapshot:'missing',actions:[{type:'key',keys:['ctrl']}]}],{single:true});
assert.equal(result.output[0].ok,false);
assert.equal(result.exitCode,1);
console.log('all cdp worker sequential, EOF, stop-on-error and single-shot regressions pass');
