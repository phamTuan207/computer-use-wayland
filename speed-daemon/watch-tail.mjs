// watch-tail.mjs - read-only CDP tail read for agents watch.
// Usage: node /tmp/watch-tail.mjs <endpoint> <targetId>
// Returns last 10 message items (all roles) + generating heuristics. Read-only.
const endpoint = process.argv[2];
const targetId = process.argv[3];
function out(obj){ console.log(JSON.stringify(obj)); process.exit(0); }
if(!endpoint||!targetId) out({ok:false,error:'usage'});
const list = await (await fetch(endpoint+'/json/list')).json().catch(e=>{out({ok:false,error:'json/list failed: '+String(e).slice(0,200)})});
const tab = list.find(t=>t.type==='page'&&t.id===targetId);
if(!tab) out({ok:false,error:'target not found', title:null});
const ws = new WebSocket(tab.webSocketDebuggerUrl);
await new Promise((res,rej)=>{ws.onopen=res;ws.onerror=()=>rej(new Error('ws open failed'));}).catch(e=>{out({ok:false,error:String(e).slice(0,200)})});
let seq=0; const pending=new Map();
ws.onmessage=(ev)=>{const m=JSON.parse(ev.data); if(m.id&&pending.has(m.id)){pending.get(m.id)(m);pending.delete(m.id);}};
function call(method,params,timeout=8000){return new Promise((resolve,reject)=>{const id=++seq;pending.set(id,(msg)=>msg.error?reject(new Error(msg.error.message)):resolve(msg.result));ws.send(JSON.stringify({id,method,params}));setTimeout(()=>{if(pending.has(id)){pending.delete(id);reject(new Error('CDP timeout: '+method));}},timeout);});}
async function evaljs(expr){const r=await call('Runtime.evaluate',{expression:expr,returnByValue:true,awaitPromise:true}); if(r.exceptionDetails) throw new Error(r.exceptionDetails.text||r.exceptionDetails.exception?.description||'evaluate exception'); return r.result.value;}
const EXPR = `(() => {
  const items=[...document.querySelectorAll('[data-message-item]')];
  const tail=items.slice(-10).map((el,i)=>{
    const t=(el.textContent||'').trim();
    return {index: items.length-10+i <0 ? i : items.indexOf(el), role: el.getAttribute('data-message-role')||null, side: el.getAttribute('data-message-side')||null, len: t.length, text: t.slice(0,400)};
  });
  // fix indices properly
  const tail2=items.slice(-10).map((el,k)=>{
    const idx=items.length-Math.min(10,items.length)+k;
    const t=(el.textContent||'').trim();
    return {index: idx, role: el.getAttribute('data-message-role')||null, side: el.getAttribute('data-message-side')||null, len: t.length, text: t.slice(0,400)};
  });
  const bodyText=(document.body?document.body.innerText:'')||'';
  const hasStop=!![...document.querySelectorAll('button')].find(b=>/stop/i.test(b.textContent||'')||/stop/i.test(b.getAttribute('aria-label')||''));
  const busy=document.querySelector('[aria-busy="true"]')?true:false;
  const composer=document.querySelector('textarea,[contenteditable="true"]');
  return {title: document.title, total: items.length, tail: tail2, hasStop, busy, composerEmpty: composer? ((composer.value!==undefined?composer.value:composer.textContent)||'').trim().length===0 : null, url: location.href};
})()`;
try{
  const v=await evaljs(EXPR);
  ws.close();
  out({ok:true,endpoint,target:targetId,...v});
}catch(e){ try{ws.close();}catch(_){} out({ok:false,error:String(e).slice(0,300)}); }
