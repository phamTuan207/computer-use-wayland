// Dependency-free CDP adapter, Node >=22. Explicit target; no model API calls.
import fs from 'node:fs';
import crypto from 'node:crypto';

const request=JSON.parse(fs.readFileSync(0,'utf8'));
const endpoint=new URL(request.endpoint);
if (!['127.0.0.1','localhost','[::1]'].includes(endpoint.hostname)) throw new Error('CDP endpoint must be loopback');
const tabs=await (await fetch(new URL('/json/list',endpoint),{signal:AbortSignal.timeout(4000)})).json();
if(request.operation==='tabs') {
  console.log(JSON.stringify(tabs.filter(t=>t.type==='page').map(({id,title,url})=>({id,title,url}))));
  process.exit(0);
}
const target=tabs.find(t=>t.type==='page'&&t.id===request.target);
if(!target) throw new Error('exact --target required; use browser tabs');
const ws=new WebSocket(target.webSocketDebuggerUrl);
const pending=new Map();let sequence=0;
ws.addEventListener('message',event=>{
  const result=JSON.parse(event.data),p=pending.get(result.id);
  if(!p)return;
  pending.delete(result.id);clearTimeout(p.timer);
  if(result.error)p.reject(new Error(result.error.message));else p.resolve(result.result);
});
await new Promise((resolve,reject)=>{ws.addEventListener('open',resolve,{once:true});ws.addEventListener('error',reject,{once:true});});
async function call(method,params={}) {
  const id=++sequence;
  return await new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>{pending.delete(id);reject(new Error('CDP timeout: '+method));},5000);
    pending.set(id,{resolve,reject,timer});ws.send(JSON.stringify({id,method,params}));
  });
}
async function evaluate(expression) {
  const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});
  if(r.exceptionDetails)throw new Error(r.exceptionDetails.text+': '+(r.exceptionDetails.exception?.description||''));
  return r.result.value;
}
function pageState(snapshot,action) {
  const s=globalThis.__agentCu;
  if(!s||s.id!==snapshot)throw new Error('stale snapshot; observe again');
  if(Date.now()-s.created>90000)throw new Error('snapshot older than 90s');
  if(s.url!==location.href)throw new Error('page navigated; observe again');
  let e;
  if(action.ref)e=s.refs.get(action.ref);
  else if(action.selector){const all=document.querySelectorAll(action.selector);if(all.length!==1)throw new Error('selector must match exactly one element');e=all[0];}
  if(!e||!e.isConnected)throw new Error('element missing; observe again');
  return e;
}
const elementExpression=(a,body)=>`(()=>{const e=(${pageState.toString()})(${JSON.stringify(request.snapshot)},${JSON.stringify(a)});${body}})()`;
async function snapshot() {
  const id=crypto.randomUUID().slice(0,12);
  return await evaluate(`(()=>{
    const s=globalThis.__agentCu={id:${JSON.stringify(id)},created:Date.now(),url:location.href,refs:new Map()};
    const elements=[];let index=0;
    const candidates=document.querySelectorAll('button,a[href],input,textarea,select,summary,[role="button"],[role="checkbox"],[role="tab"],[role="menuitem"],[contenteditable="true"]');
    let truncated=false;
    for(const e of candidates){
      const r=e.getBoundingClientRect(),style=getComputedStyle(e);
      if(!r.width||!r.height||style.visibility==='hidden'||style.display==='none'||e.type==='hidden')continue;
      if(elements.length>=80){truncated=true;break;}
      const ref='e'+(++index);s.refs.set(ref,e);
      const label=e.getAttribute('aria-label')||e.labels?.[0]?.innerText||e.innerText||e.getAttribute('placeholder')||e.getAttribute('title')||e.name||'';
      const item={ref,role:e.getAttribute('role')||e.tagName.toLowerCase(),name:label.trim().slice(0,120)};
      if(e.disabled)item.disabled=true;
      if(e.type==='password')item.value='[redacted]';else if('value'in e)item.value=String(e.value).slice(0,120);
      if('checked'in e&&(e.type==='checkbox'||e.type==='radio'))item.checked=e.checked;
      if(r.bottom<0||r.top>innerHeight)item.offscreen=true;
      elements.push(item);
    }
    return {snapshot:s.id,title:document.title,url:location.href,elements,truncated,iframes:document.querySelectorAll('iframe').length};
  })()`);
}
async function click(a) {
  const point=await evaluate(elementExpression(a,`
    if(e.disabled)throw new Error('element disabled');
    e.scrollIntoView({block:'center',inline:'center',behavior:'instant'});
    const r=e.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2;
    const hit=document.elementFromPoint(x,y);
    if(!hit||!(e===hit||e.contains(hit)))throw new Error('element covered; observe again');
    return {x,y};`));
  await call('Input.dispatchMouseEvent',{type:'mouseMoved',...point});
  await call('Input.dispatchMouseEvent',{type:'mousePressed',...point,button:'left',clickCount:1});
  await call('Input.dispatchMouseEvent',{type:'mouseReleased',...point,button:'left',clickCount:1});
}
async function key(keys) {
  const mods={alt:1,ctrl:2,meta:4,super:4,shift:8};let modifiers=0;const regular=[];
  for(const k of keys){if(k.toLowerCase() in mods)modifiers|=mods[k.toLowerCase()];else regular.push(k);}
  const special={Enter:13,Tab:9,Escape:27,BackSpace:8,Backspace:8,Delete:46,ArrowLeft:37,ArrowUp:38,ArrowRight:39,ArrowDown:40,Home:36,End:35,PageUp:33,PageDown:34,space:32,' ':32};
  // US-layout shift layer, for the keys where uppercase is not the shifted form.
  const shifted={'1':'!','2':'@','3':'#','4':'$','5':'%','6':'^','7':'&','8':'*','9':'(','0':')',
                 '[':'{',']':'}','\\':'|',';':':',"'":'"',',':'<','.':'>','/':'?','-':'_','=':'+','`':'~'};
  for(const k of regular){
    const code=special[k]??(k.length===1?k.toUpperCase().charCodeAt(0):null);
    if(code===null)throw new Error('unsupported key '+k);
    const key=k==='BackSpace'?'Backspace':k==='space'?' ':k;
    const params={key,modifiers,windowsVirtualKeyCode:code,nativeVirtualKeyCode:code};
    const ctrl=modifiers&2,alt=modifiers&1,meta=modifiers&4;
    if(key.length===1&&!modifiers)params.text=key;
    // Shift alone turns the key into a character, so it needs text too. Without
    // this the chord fired the page's key handler but typed nothing. toUpperCase
    // is not the shifted character on a US layout for digits and punctuation,
    // so map those explicitly. Ctrl/Alt/Meta are shortcuts and carry no text.
    else if(key.length===1&&(modifiers&8)&&!ctrl&&!alt&&!meta)params.text=shifted[key]??key.toUpperCase();
    if(key==='Enter'&&!modifiers)params.text='\r';
    await call('Input.dispatchKeyEvent',{type:'keyDown',...params});
    await call('Input.dispatchKeyEvent',{type:'keyUp',...params});
  }
}
async function assertAction(a) {
  const start=Date.now(),limit=Math.min(a.timeout_ms??1000,3000);
  while(true){
    const ok=await evaluate(elementExpression(a,`
      return ${a.value!==undefined?'String(e.value)==='+JSON.stringify(String(a.value)):
        a.text!==undefined?'e.textContent.includes('+JSON.stringify(a.text)+')':
        a.checked!==undefined?'e.checked==='+JSON.stringify(a.checked):'Boolean(e.getBoundingClientRect().width)'};`));
    if(ok)return;
    if(Date.now()-start>=limit)throw new Error('assertion failed');
    await new Promise(r=>setTimeout(r,50));
  }
}
let result,completed=0;
try {
  if(request.operation==='act'){
    if(!request.snapshot)throw new Error('--snapshot required');
    // Preflight the entire schema before any side effects.
    for(const a of request.actions){
      if(['click','fill','assert'].includes(a.type)&&!a.ref&&!a.selector)throw new Error('ref or selector required');
      if(a.type==='key')for(const k of a.keys)if(!/^(ctrl|alt|shift|meta|super|Enter|Tab|Escape|Back[Ss]pace|Delete|Arrow(Left|Right|Up|Down)|Home|End|PageUp|PageDown|space|.)$/.test(k))throw new Error('unsupported key');
      if(a.type==='scroll'&&!Number.isFinite(a.dy))throw new Error('scroll dy required');
    }
    const start=Date.now();
    try{
      for(const a of request.actions){
        // Protect key/scroll operations as well as ref-based operations after navigation.
        await evaluate(`(()=>{const s=globalThis.__agentCu;if(!s||s.id!==${JSON.stringify(request.snapshot)}||s.url!==location.href||Date.now()-s.created>90000)throw new Error('stale snapshot');})()`);
        if(a.type==='click')await click(a);
        else if(a.type==='fill'){
          await click(a);
          const editable=await evaluate(elementExpression(a,'return document.activeElement===e && !e.readOnly && (e.isContentEditable || /^(INPUT|TEXTAREA)$/.test(e.tagName));'));
          if(!editable)throw new Error('field is not editable or did not gain focus');
          await key(['ctrl','a']);await call('Input.insertText',{text:a.text});
          const actual=await evaluate(elementExpression(a,'return e.isContentEditable?e.textContent:e.value;'));
          if(actual!==a.text)throw new Error('fill verification failed');
        }else if(a.type==='key')await key(a.keys);
        else if(a.type==='scroll')await call('Input.dispatchMouseEvent',{type:'mouseWheel',x:a.x??100,y:a.y??100,deltaX:a.dx??0,deltaY:a.dy});
        else if(a.type==='wait')await new Promise(r=>setTimeout(r,a.ms??100));
        else if(a.type==='assert')await assertAction(a);
        completed++;
      }
      result={ok:true,completed,execution_ms:Date.now()-start};
    }catch(e){result={ok:false,completed,error:e.message,execution_ms:Date.now()-start};}
    result.after=await snapshot();
  }else result=await snapshot();
  if(request.image)result.image_base64=(await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false})).data;
  console.log(JSON.stringify(result));
}catch(e){console.log(JSON.stringify({ok:false,completed,error:e.message}));process.exitCode=1;}
finally{ws.close();}
