// Run: node tests/cdp_worker.mjs. Fake stdin/CDP/DOM, no network or GUI.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import { createInterface } from 'node:readline';
import { performance } from 'node:perf_hooks';
import { Readable } from 'node:stream';

const benchmarkArg=process.argv.indexOf('--close-bench');
if(benchmarkArg>=0&&!process.argv[benchmarkArg+1])throw new Error('--close-bench needs ADAPTER_PATH');
const adapterPath=benchmarkArg>=0?process.argv[benchmarkArg+1]:new URL('../scripts/cdp.mjs',import.meta.url);
const source=fs.readFileSync(adapterPath,'utf8');
const request={operation:'observe',endpoint:'http://127.0.0.1:9222',target:'test'};
async function run(requests,{connectError=false,fetchError=false,debuggerUrl='ws://127.0.0.1:9222/test',single=false,
  closeOnSocket=0,closeBeforeOpen=false,sendError=false}={}) {
  const output=[],events=[],sockets=[],responseTimes=[],timers=new Set(),requestedTimeouts=[];
  let fetches=0,frames=0;
  const fixtureState={status:'Ready',inputEvents:0};
  const page=vm.createContext({document:{title:'fixture',querySelectorAll:()=>[]},__fixtureState:fixtureState,
    location:{href:'http://fixture/'},innerWidth:100,innerHeight:100});
  class WebSocket extends EventTarget {
    static CONNECTING=0;static OPEN=1;static CLOSING=2;static CLOSED=3;
    constructor(){
      super();
      assert.ok(sockets.every(s=>s.closed),'previous request socket must close first');
      this.closed=false;this.readyState=WebSocket.CONNECTING;sockets.push(this);events.push('connect');
      if(closeBeforeOpen)queueMicrotask(()=>this.remoteClose());
      else if(!connectError)queueMicrotask(()=>{this.readyState=WebSocket.OPEN;events.push('open');this.dispatchEvent(new Event('open'));});
      else queueMicrotask(()=>{const e=new Event('error');Object.defineProperty(e,'message',{value:'connect failed'});this.dispatchEvent(e);});
    }
    send(raw){
      if(this.readyState===WebSocket.CLOSED)return; // WebSocket.send silently ignores a closed socket.
      if(sendError)throw new Error('synchronous send failed');
      const {id,method,params}=JSON.parse(raw);let result;
      frames++;events.push(method);
      if(method.startsWith('Input.'))fixtureState.inputEvents++;
      assert.equal(method,'Runtime.evaluate');
      if(sockets.indexOf(this)+1===closeOnSocket){queueMicrotask(()=>this.remoteClose());return;}
      try{result={result:{value:vm.runInContext(params.expression,page)}};}
      catch(e){result={exceptionDetails:{text:e.message}};}
      queueMicrotask(()=>this.dispatchEvent(new MessageEvent('message',{data:JSON.stringify({id,result})})));
    }
    remoteClose(){
      if(this.readyState===WebSocket.CLOSED)return;
      this.readyState=WebSocket.CLOSED;this.closed=true;events.push('close');this.dispatchEvent(new Event('close'));
    }
    close(){this.remoteClose();}
  }
  const trackedSetTimeout=(fn,delay)=>{
    requestedTimeouts.push(delay);
    let timer;
    timer=setTimeout(()=>{timers.delete(timer);fn();},delay);
    timers.add(timer);return timer;
  };
  const trackedClearTimeout=timer=>{timers.delete(timer);clearTimeout(timer);};
  const lines=requests.map(value=>typeof value==='string'?value:JSON.stringify(value));
  const stdin=Readable.from([lines.join('\n')+(lines.length?'\n':'')]);
  const process={argv:single?[]:['node','cdp.mjs','--worker'],stdin,exitCode:0};
  await vm.runInNewContext('(async()=>{'+source.replace(/^import .*;$/gm,'')+'})()',{
    fs:{readFileSync:()=>lines[0]},crypto:{randomUUID:()=> 'snapshot-'+fetches},
    createInterface,process,URL,WebSocket,EventTarget,Event,MessageEvent,AbortSignal,queueMicrotask,
    setTimeout:trackedSetTimeout,clearTimeout:trackedClearTimeout,
    fetch:async()=>{
      fetches++;events.push('fetch');
      if(fetchError)throw new Error('fetch failed');
      return {json:async()=>[{type:'page',id:'test',title:'fixture',url:'http://fixture/',
        webSocketDebuggerUrl:debuggerUrl},{type:'worker',id:'ignored'}]};
    },
    console:{log:line=>{output.push(JSON.parse(line));events.push('response');responseTimes.push(performance.now());}}
  });
  assert.ok(sockets.every(s=>s.closed));
  if(!single)assert.equal(stdin.destroyed,true);
  return {output,events,fetches,frames,sockets,exitCode:process.exitCode,responseTimes,
    pendingTimers:timers.size,requestedTimeouts,fixtureState};
}

async function benchmarkClose() {
  const samples=[];
  for(let index=0;index<3;index++){
    const started=performance.now();
    try{
      const requests=[request,{...request,operation:'act',snapshot:'snapshot-1',no_after:true,
        actions:[{type:'assert',selector:'#status',text:'Saved fixture'}]}];
      const result=await run(requests,{closeOnSocket:2});
      const responseAt=result.responseTimes[1];
      const act=result.output[1],state={...result.fixtureState};
      const verified=act?.ok===false&&act.completed===0&&act.after_unavailable===true&&
        result.output[0]?.snapshot==='snapshot-1'&&state.status==='Ready'&&state.inputEvents===0&&result.pendingTimers===0;
      const verifiedAt=performance.now();
      samples.push({index,ok:verified,total_ms:+(verifiedAt-started).toFixed(3),
        response_ms:+(responseAt-started).toFixed(3),execution_ms:act?.execution_ms,
        whole_task_ms:+(verifiedAt-started).toFixed(3),
        result_bytes:result.output.reduce((sum,value)=>sum+Buffer.byteLength(JSON.stringify(value),'utf8'),0),
        completed:act?.completed,input_count:state.inputEvents,pending_timers:result.pendingTimers,
        error:act?.error});
    }catch(error){samples.push({index,ok:false,error:error.message});}
  }
  const values=key=>samples.map(sample=>sample[key]).filter(Number.isFinite).sort((a,b)=>a-b);
  const median=items=>items.length?+(items.length%2?items[(items.length-1)/2]:(items[items.length/2-1]+items[items.length/2])/2).toFixed(3):null;
  return {kind:'mock-cdp-protocol-only',chrome_measured:false,
    verification:'mock protocol input count/state only; no real DOM or Chrome',
    adapter:String(adapterPath).split('/').pop(),samples,
    medians:Object.fromEntries(['total_ms','response_ms','execution_ms','whole_task_ms','result_bytes'].map(key=>[key,median(values(key))]))};
}

if(benchmarkArg>=0){
  const report=await benchmarkClose();
  console.log(JSON.stringify(report));
  if(report.samples.length!==3||report.samples.some(sample=>!sample.ok))process.exitCode=1;
}else{
let result=await run([request,request]);
assert.equal(result.output.length,2);
assert.equal(result.output[0].snapshot,'snapshot-1');
assert.equal(result.output[1].snapshot,'snapshot-2');
assert.equal(result.sockets.length,2);
assert.deepEqual(result.events,['fetch','connect','open','Runtime.evaluate','close','response',
  'fetch','connect','open','Runtime.evaluate','close','response']);
assert.equal(result.pendingTimers,0);
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
const closeAct=await run([request,{...request,operation:'act',snapshot:'snapshot-1',no_after:true,
  actions:[{type:'assert',selector:'#status',text:'Saved fixture'}]}],{closeOnSocket:2});
assert.equal(closeAct.output.length,2);
assert.equal(closeAct.output[0].snapshot,'snapshot-1');
assert.equal(closeAct.output[1].ok,false);
assert.equal(closeAct.output[1].completed,0);
assert.equal(closeAct.output[1].after_unavailable,true);
assert.equal(closeAct.fixtureState.inputEvents,0);
assert.equal(closeAct.pendingTimers,0);
assert.ok(closeAct.events.includes('open'));
assert.ok(closeAct.requestedTimeouts.includes(5000),'open pending CDP calls retain the 5s timeout');
assert.equal(closeAct.requestedTimeouts.filter(delay=>delay===5000).length,2,
  'close diagnostic does not schedule another CDP timeout');
const earlyClose=await run([request],{closeBeforeOpen:true});
assert.equal(earlyClose.output.length,1);
assert.equal(earlyClose.output[0].ok,false);
assert.ok(earlyClose.output[0].error.includes('closed before open'));
assert.equal(earlyClose.pendingTimers,0);
const sendFailure=await run([request],{sendError:true});
assert.equal(sendFailure.output.length,1);
assert.equal(sendFailure.output[0].ok,false);
assert.ok(sendFailure.output[0].error.includes('synchronous send failed'));
assert.equal(sendFailure.pendingTimers,0);
console.log('all cdp worker sequential, close, send cleanup, EOF, stop-on-error and single-shot regressions pass');
}
