// Run: node tests/cdp_worker.mjs. Fake CDP/DOM plus owned loopback native sockets; no GUI.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import { createInterface } from 'node:readline';
import { performance } from 'node:perf_hooks';
import { Readable } from 'node:stream';
import { createServer } from 'node:http';
import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const benchmarkArg=process.argv.indexOf('--close-bench');
if(benchmarkArg>=0&&!process.argv[benchmarkArg+1])throw new Error('--close-bench needs ADAPTER_PATH');
const adapterPath=benchmarkArg>=0?process.argv[benchmarkArg+1]:new URL('../scripts/cdp.mjs',import.meta.url);
const source=fs.readFileSync(adapterPath,'utf8');
const request={operation:'observe',endpoint:'http://127.0.0.1:9222',target:'test'};
async function run(requests,{connectError=false,fetchError=false,debuggerUrl='ws://127.0.0.1:9222/test',single=false,
  closeOnRequest=0,closeBeforeOpen=false,sendError=false,
  beforeFetch=()=>{},onResponse=()=>{},onSend=()=>false,tabList=null,delayClose=false,fastTimeout=false}={}) {
  const output=[],events=[],sockets=[],responseTimes=[],timers=new Set(),requestedTimeouts=[];
  let fetches=0,frames=0;const ids=[];
  const fixtureState={status:'Ready',inputEvents:0};
  const page=vm.createContext({document:{title:'fixture',querySelectorAll:()=>[]},__fixtureState:fixtureState,
    location:{href:'http://fixture/'},innerWidth:100,innerHeight:100});
  class WebSocket extends EventTarget {
    static CONNECTING=0;static OPEN=1;static CLOSING=2;static CLOSED=3;
    constructor(url){
      super();this.url=url;this.handlers=new Map();
      assert.ok(sockets.every(s=>s.closed||s.readyState===WebSocket.CLOSING),'old socket must be retired before replacement');
      this.closed=false;this.readyState=WebSocket.CONNECTING;sockets.push(this);events.push('connect');
      if(closeBeforeOpen)queueMicrotask(()=>this.remoteClose());
      else if(!connectError)queueMicrotask(()=>{this.readyState=WebSocket.OPEN;events.push('open');this.dispatchEvent(new Event('open'));});
      else queueMicrotask(()=>{const e=new Event('error');Object.defineProperty(e,'message',{value:'connect failed'});this.dispatchEvent(e);});
    }
    addEventListener(name,fn,options){
      if(!this.handlers.has(name))this.handlers.set(name,new Set());
      this.handlers.get(name).add(fn);super.addEventListener(name,fn,options);
    }
    removeEventListener(name,fn,options){
      this.handlers.get(name)?.delete(fn);super.removeEventListener(name,fn,options);
    }
    emit(value){this.dispatchEvent(new MessageEvent('message',{data:typeof value==='string'?value:JSON.stringify(value)}));}
    send(raw){
      if(this.readyState===WebSocket.CLOSED)return; // WebSocket.send silently ignores a closed socket.
      if(sendError)throw new Error('synchronous send failed');
      const {id,method,params}=JSON.parse(raw);let result;
      frames++;ids.push({socket:sockets.indexOf(this),id,method});events.push(method);
      if(method.startsWith('Input.'))fixtureState.inputEvents++;
      if(onSend({socket:this,id,method,params,fetches,sockets,page,events}))return;
      if(method.startsWith('Input.')){queueMicrotask(()=>this.emit({id,result:{}}));return;}
      assert.equal(method,'Runtime.evaluate');
      if(fetches===closeOnRequest){queueMicrotask(()=>this.remoteClose());return;}
      try{result={result:{value:vm.runInContext(params.expression,page)}};}
      catch(e){result={exceptionDetails:{text:e.message}};}
      queueMicrotask(()=>this.dispatchEvent(new MessageEvent('message',{data:JSON.stringify({id,result})})));
    }
    remoteClose(){
      if(this.readyState===WebSocket.CLOSED)return;
      this.readyState=WebSocket.CLOSED;this.closed=true;events.push('close');this.dispatchEvent(new Event('close'));
    }
    close(){
      if(this.readyState===WebSocket.CLOSED)return;
      if(delayClose){this.readyState=WebSocket.CLOSING;events.push('closing');}
      else this.remoteClose();
    }
  }
  const trackedSetTimeout=(fn,delay)=>{
    requestedTimeouts.push(delay);
    let timer;
    timer=setTimeout(()=>{timers.delete(timer);fn();},fastTimeout&&delay===5000?1:delay);
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
      beforeFetch({fetches,sockets,page,events});
      if(fetchError)throw new Error('fetch failed');
      if(tabList)return {json:async()=>tabList(fetches)};
      return {json:async()=>[{type:'page',id:'test',title:'fixture',url:'http://fixture/',
        webSocketDebuggerUrl:debuggerUrl},{type:'worker',id:'ignored'}]};
    },
    console:{log:line=>{output.push(JSON.parse(line));events.push('response');responseTimes.push(performance.now());onResponse({output,fetches,sockets,page,events});}}
  });
  if(delayClose)for(const socket of sockets)socket.remoteClose();
  assert.ok(sockets.every(s=>s.closed));
  for(const socket of sockets)assert.equal([...socket.handlers.values()].reduce((n,set)=>n+set.size,0),0,'all connection listeners released');
  if(!single)assert.equal(stdin.destroyed,true);
  return {output,events,fetches,frames,sockets,exitCode:process.exitCode,responseTimes,
    pendingTimers:timers.size,requestedTimeouts,fixtureState,ids,page};
}

async function benchmarkClose() {
  const samples=[];
  for(let index=0;index<3;index++){
    const started=performance.now();
    try{
      const requests=[request,{...request,operation:'act',snapshot:'snapshot-1',no_after:true,
        actions:[{type:'assert',selector:'#status',text:'Saved fixture'}]}];
      const result=await run(requests,{closeOnRequest:2});
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
assert.equal(result.sockets.length,1);
assert.deepEqual(result.events,['fetch','connect','open','Runtime.evaluate','response',
  'fetch','Runtime.evaluate','response','close']);
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
  actions:[{type:'assert',selector:'#status',text:'Saved fixture'}]}],{closeOnRequest:2});
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

// Persistent-worker contracts: each request still fetches and evaluates fresh state.
const act={...request,operation:'act',snapshot:'snapshot-1',actions:[{type:'wait',ms:0}]};
result=await run(Array.from({length:40},()=>request));
assert.equal(result.sockets.length,1);
assert.equal(result.fetches,40);
assert.equal(result.output.length,40);
assert.deepEqual(result.ids.map(x=>x.id),Array.from({length:40},(_,i)=>i+1));
assert.equal(result.pendingTimers,0);
for(let i=0;i<40;i++)assert.equal(result.output[i].snapshot,'snapshot-'+(i+1));

const tab=(id='test',url='http://fixture/',webSocketDebuggerUrl='ws://127.0.0.1:9222/test')=>
  ({type:'page',id,url,webSocketDebuggerUrl});
for(const change of ['endpoint','target','debugger','url']){
  const second={...request,...(change==='endpoint'?{endpoint:'http://127.0.0.1:9333'}:
    change==='target'?{target:'other'}:{})};
  result=await run([request,second],{tabList:n=>[n===1?tab():tab(
    change==='target'?'other':'test',change==='url'?'http://fixture/next':'http://fixture/',
    change==='debugger'?'ws://127.0.0.1:9222/replaced':'ws://127.0.0.1:9222/test')]});
  assert.equal(result.sockets.length,2,change);
  assert.equal(result.fetches,2,change);
  assert.equal(result.output[1].snapshot,'snapshot-2',change);
}
for(const invalid of [[],[{...tab(),type:'worker'}],[tab('test','http://fixture/','ws://outside.example/test')]]){
  result=await run([request,request,request],{tabList:n=>n===1?[tab()]:invalid});
  assert.equal(result.output.length,2);
  assert.equal(result.output[1].ok,false);
  assert.equal(result.sockets.length,1,'fresh invalid target never uses retained socket');
  assert.equal(result.frames,1);
  assert.equal(result.exitCode,1);
}
result=await run([request,{...request,endpoint:'http://outside.example'},request]);
assert.equal(result.fetches,1);assert.equal(result.output.length,2);assert.equal(result.frames,1);
result=await run([request,'{malformed',request]);
assert.equal(result.output.length,2);assert.equal(result.fetches,1);assert.equal(result.exitCode,1);
result=await run([request,{...request,operation:'tabs'},request]);
assert.equal(result.sockets.length,2);assert.equal(result.fetches,3);assert.ok(Array.isArray(result.output[1]));

// A new explicit request may replace an idle dead socket; it never retries a send.
for(const fault of ['close','error','malformed']){
  result=await run([request,request],{onResponse:({output,sockets})=>{
    if(output.length!==1)return;
    if(fault==='close')sockets[0].remoteClose();
    else if(fault==='error')sockets[0].dispatchEvent(new Event('error'));
    else sockets[0].emit('{bad JSON');
  }});
  assert.equal(result.sockets.length,2,fault);assert.equal(result.frames,2,fault);
  assert.equal(result.output[1].snapshot,'snapshot-2',fault);
}
for(const fault of ['close','error','malformed']){
  result=await run([request,act,request],{onSend:({socket,fetches})=>{
    if(fetches!==2)return false;
    if(fault==='close')socket.remoteClose();
    else if(fault==='error')socket.dispatchEvent(new Event('error'));
    else socket.emit('{bad JSON');
    return true;
  }});
  assert.equal(result.sockets.length,1,fault);assert.equal(result.output.length,2,fault);
  assert.equal(result.output[1].ok,false,fault);assert.equal(result.output[1].completed,0,fault);
  assert.equal(result.fixtureState.inputEvents,0,fault);assert.equal(result.pendingTimers,0,fault);
}

// A close from the retired transport must not invalidate its replacement.
result=await run([request,{...request,endpoint:'http://127.0.0.1:9333'},
  {...request,endpoint:'http://127.0.0.1:9333'}],{
  delayClose:true,onSend:({fetches,sockets})=>{if(fetches===2)sockets[0].remoteClose();return false;}});
assert.equal(result.sockets.length,2);assert.equal(result.output[2].snapshot,'snapshot-3');
assert.deepEqual(result.ids.map(x=>[x.socket,x.id]),[[0,1],[1,1],[1,2]]);

// Late/duplicate replies are ignored; IDs keep increasing on the retained socket.
result=await run([request,request],{onSend:({socket,id,fetches})=>{
  if(fetches===2){assert.equal(id,2);socket.emit({id:1,result:{result:{value:{snapshot:'wrong'}}}});}
  return false;
}});
assert.equal(result.output[1].snapshot,'snapshot-2');assert.equal(result.sockets.length,1);

// The same live transport cannot make a stale snapshot valid (including same-URL reload).
for(const stale of ['reload','url','age','id']){
  const input={...act,actions:[{type:'key',keys:['a']}]};
  result=await run([request,input,request],{onResponse:({output,page})=>{
    if(output.length!==1)return;
    if(stale==='reload')delete page.__agentCu;
    if(stale==='url')page.location.href='http://fixture/navigated';
    if(stale==='age')page.__agentCu.created=Date.now()-90001;
    if(stale==='id')page.__agentCu.id='another-snapshot';
  }});
  assert.equal(result.sockets.length,1,stale);assert.equal(result.output.length,2,stale);
  assert.equal(result.output[1].ok,false,stale);assert.equal(result.fixtureState.inputEvents,0,stale);
}


// Element checks are still evaluated live on the reused connection.
for(const unavailable of ['removed','disabled','covered']){
  result=await run([request,{...act,actions:[{type:'click',selector:'#button'}]},request],{
    onResponse:({output,page})=>{
      if(output.length!==1)return;
      const element={isConnected:unavailable!=='removed',disabled:unavailable==='disabled',
        scrollIntoView(){},getBoundingClientRect(){return {left:0,top:0,width:20,height:20};}};
      page.document.querySelectorAll=selector=>selector==='#button'?[element]:[];
      page.document.elementFromPoint=()=>({});
      element.contains=()=>false;
    }
  });
  assert.equal(result.output.length,2,unavailable);assert.equal(result.output[1].ok,false,unavailable);
  assert.equal(result.fixtureState.inputEvents,0,unavailable);assert.equal(result.sockets.length,1,unavailable);
}
result=await run([request,{...act,actions:[{type:'scroll',dy:20}]},request],{
  onResponse:({output,page})=>{if(output.length===1)delete page.__agentCu;}
});
assert.equal(result.output[1].ok,false);assert.equal(result.fixtureState.inputEvents,0);

// A close after mousePressed is ambiguous input: do not send release, retry, or next request.
result=await run([request,{...act,actions:[{type:'click',selector:'#button'},{type:'key',keys:['a']}]},request],{
  onResponse:({output,page})=>{
    if(output.length!==1)return;
    const element={isConnected:true,scrollIntoView(){},getBoundingClientRect(){return {left:0,top:0,width:20,height:20};}};
    page.document.querySelectorAll=selector=>selector==='#button'?[element]:[];
    page.document.elementFromPoint=()=>element;
  },
  onSend:({socket,method,params})=>{
    if(method==='Input.dispatchMouseEvent'&&params.type==='mousePressed'){
      socket.remoteClose();return true;
    }
    return false;
  }
});
assert.equal(result.output.length,2);assert.equal(result.output[1].ok,false);
assert.equal(result.output[1].completed,0);assert.equal(result.fixtureState.inputEvents,2);
assert.equal(result.sockets.length,1);assert.equal(result.fetches,2);assert.equal(result.pendingTimers,0);

for(const fault of ['preflight','fetch']){
  result=await run([request,fault==='preflight'?{...request,max_elements:0}:request,request],{
    beforeFetch:({fetches})=>{if(fault==='fetch'&&fetches===2)throw new Error('owned list failed');}
  });
  assert.equal(result.output.length,2,fault);assert.equal(result.output[1].ok,false,fault);
  assert.equal(result.sockets.length,1,fault);assert.equal(result.frames,1,fault);
}

// A swallowed after-snapshot failure keeps its envelope, but retires the transport.
for(const failure of ['cdp-error','transport-error','timeout','send-throw']){
  result=await run([request,act,request],{fastTimeout:true,onSend:({socket,id,params,fetches})=>{
    if(fetches!==2||!params.expression?.includes('const s=globalThis.__agentCu={'))return false;
    if(failure==='cdp-error')socket.emit({id,error:{message:'after failed'}});
    if(failure==='transport-error')socket.dispatchEvent(new Event('error'));
    if(failure==='send-throw')throw new Error('after send failed');
    return true; // timeout deliberately leaves the reply pending.
  }});
  assert.equal(result.output.length,3,failure);assert.equal(result.output[1].ok,true,failure);
  assert.equal(result.output[1].completed,1,failure);assert.equal(result.output[1].after_unavailable,true,failure);
  assert.equal(result.sockets.length,2,failure);assert.equal(result.output[2].snapshot,'snapshot-3',failure);
  assert.equal(result.pendingTimers,0,failure);
}

// EOF after a healthy request closes exactly one reusable transport; standalone never keeps it.
result=await run([request],{single:true});
assert.equal(result.sockets.length,1);assert.deepEqual(result.events.slice(-2),['close','response']);
console.log('persistent worker identity, refresh, stale state, bounded listeners, idle faults, no replay and poison-retirement regressions pass');
console.log('all cdp worker sequential, close, send cleanup, EOF, stop-on-error and single-shot regressions pass');
}


// Real Node WebSocket + production Python owner against an owned loopback peer.
// Only CDP payloads are simulated; native framing, close and process teardown are real.
async function nativeShutdown(mode){
  let upgrades=0,fetches=0,commands=0,closeFrames=0;
  const sockets=new Set();let child,server,fixtureError;
  function frame(opcode,payload){
    const data=Buffer.from(payload),header=Buffer.alloc(data.length<126?2:4);
    header[0]=0x80|opcode;
    if(data.length<126)header[1]=data.length;
    else{header[1]=126;header.writeUInt16BE(data.length,2);}
    return Buffer.concat([header,data]);
  }
  server=createServer((req,res)=>{
    if(req.url!=='/json/list'){fixtureError??=new Error('unexpected fixture URL');res.writeHead(404);res.end();return;}
    fetches++;
    res.setHeader('content-type','application/json');
    res.end(JSON.stringify([{type:'page',id:'test',url:'http://fixture/',
      webSocketDebuggerUrl:`ws://127.0.0.1:${server.address().port}/target`} ]));
  });
  server.on('connection',socket=>{
    sockets.add(socket);socket.on('close',()=>sockets.delete(socket));socket.on('error',()=>{});
  });
  server.on('upgrade',(req,socket,head)=>{
    upgrades++;
    const accept=createHash('sha1').update(req.headers['sec-websocket-key']+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest('base64');
    socket.write('HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: '+accept+'\r\n\r\n');
    let buffer=head;
    socket.on('end',()=>socket.end());
    const parse=()=>{
      while(buffer.length>=2){
        const opcode=buffer[0]&15,masked=!!(buffer[1]&128);let size=buffer[1]&127,offset=2;
        if(size===126){if(buffer.length<4)return;size=buffer.readUInt16BE(2);offset=4;}
        else if(size===127){if(buffer.length<10)return;size=Number(buffer.readBigUInt64BE(2));offset=10;}
        assert.ok(size<8*1024*1024,'owned test frame bounded');
        const maskBytes=masked?4:0;
        if(buffer.length<offset+maskBytes+size)return;
        const mask=buffer.subarray(offset,offset+maskBytes),data=Buffer.from(buffer.subarray(offset+maskBytes,offset+maskBytes+size));
        if(masked)for(let i=0;i<data.length;i++)data[i]^=mask[i%4];
        buffer=buffer.subarray(offset+maskBytes+size);
        if(opcode===8){
          closeFrames++;
          if(mode==='cooperative'){socket.write(frame(8,data));socket.end();}
          continue;
        }
        assert.equal(opcode,1);commands++;
        const call=JSON.parse(data);assert.equal(call.method,'Runtime.evaluate');
        if(mode==='cancel-pending'&&commands===2){
          // Signal cancellation only after the second CDP call reached the peer.
          child.kill('SIGUSR1');continue;
        }
        const result={result:{value:{snapshot:'native-'+commands,elements:[]}}};
        socket.write(frame(1,JSON.stringify({id:call.id,result})));
      }
    };
    const consume=()=>{try{parse();}catch(error){fixtureError??=error;socket.destroy();}};
    socket.on('data',chunk=>{buffer=Buffer.concat([buffer,chunk]);consume();});consume();
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const code=String.raw`
import json,signal,sys,types
sys.path.insert(0,sys.argv[1])
from browser_worker import BrowserWorker
cancelled=False
def cancel(*unused):
    global cancelled
    cancelled=True
def check():
    if cancelled:raise RuntimeError('owned cancel fixture')
signal.signal(signal.SIGUSR1,cancel)
sys.modules['cu']=types.SimpleNamespace(check_cancel=check,browser_timeout=lambda request:5)
worker=BrowserWorker()
try:
    request={'operation':'observe','endpoint':sys.argv[2],'target':'test'}
    first=worker.request(request)
    process=worker.process
    if sys.argv[3]=='cancel-pending':
        try:worker.request(request)
        except RuntimeError as error:assert str(error)=='owned cancel fixture'
        else:raise AssertionError('cancel not observed')
    else:
        second=worker.request(request)
        assert first['snapshot']=='native-1' and second['snapshot']=='native-2'
        assert worker.process is process
        worker.close()
    assert worker.closed and worker.process is None and process.poll() is not None
    try:worker.request(request)
    except RuntimeError as error:assert 'worker ended' in str(error)
    else:raise AssertionError('terminal worker restarted')
    worker.close()
    print(json.dumps({'ok':True,'mode':sys.argv[3],'returncode':process.returncode}))
finally:
    worker.close()
`;
  let stdout='',stderr='',deadline;
  try{
    const args=['-B','-c',code,fileURLToPath(new URL('../scripts/',import.meta.url)),
      `http://127.0.0.1:${server.address().port}`,mode];
    child=spawn('python3',args,{stdio:['ignore','pipe','pipe'],detached:true});
    child.stdout.setEncoding('utf8');child.stderr.setEncoding('utf8');
    child.stdout.on('data',text=>stdout+=text);child.stderr.on('data',text=>stderr+=text);
    const status=await new Promise((resolve,reject)=>{
      deadline=setTimeout(()=>{try{process.kill(-child.pid,'SIGKILL');}catch(_){}reject(new Error('native lifecycle fixture timeout'));},10000);
      child.once('error',reject);child.once('close',(code,signal)=>resolve({code,signal}));
    });
    assert.equal(fixtureError,undefined);
    assert.equal(status.code,0,stderr);assert.equal(status.signal,null);
    const result=JSON.parse(stdout);assert.equal(result.ok,true);assert.equal(result.mode,mode);
    assert.equal(upgrades,1,'two requests reused one real WebSocket');
    assert.equal(fetches,2,'each native request fetched a fresh list');
    assert.equal(commands,2,'no duplicate/replayed command');
    if(mode==='cooperative'){
      assert.equal(result.returncode,0,'cooperative EOF exits normally');
      assert.equal(closeFrames,1,'normal EOF sends one close frame');
    }else assert.equal(result.returncode,-15,'existing Python owner terminates an unresponsive child');
    // Parent exit/reap means the owned CDP socket must already have received EOF.
    await new Promise(resolve=>setImmediate(resolve));
    assert.equal(sockets.size,0,'native sockets closed before fixture cleanup');
    console.log('native lifecycle '+mode+': fresh list x2, one socket, no replay, child reaped, no restart');
  }finally{
    clearTimeout(deadline);
    if(child&&child.exitCode===null&&child.signalCode===null){
      try{process.kill(-child.pid,'SIGKILL');}catch(_){}
      await new Promise(resolve=>child.once('close',resolve));
    }
    for(const socket of sockets)socket.destroy();
    await new Promise(resolve=>server.close(resolve));
  }
}
if(benchmarkArg<0){
  for(const mode of ['cooperative','unresponsive','cancel-pending'])await nativeShutdown(mode);
}
