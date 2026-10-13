// Dependency-free CDP adapter, Node >=22. Explicit target; no model API calls.
import fs from 'node:fs';
import crypto from 'node:crypto';
import { createInterface } from 'node:readline';

async function handle(request) {
let ws;
// Preflight failures must also return completed:0 from the catch.
let result,completed=0;
try {
const maxElements=request.max_elements??80;
if(!Number.isInteger(maxElements)||maxElements<1||maxElements>80)throw new Error('max_elements must be 1..80');
// The after-scope only narrows the successful act result; validate it like scope,
// before any network request, any input, or any snapshot.
if(request.after_scope!==undefined){
  if(request.operation!=='act')throw new Error('after_scope is only valid for act');
  if(typeof request.after_scope!=='string'||!request.after_scope.trim())throw new Error('after_scope must be a non-empty CSS selector');
  if(request.after_scope.length>1024)throw new Error('after_scope must be at most 1024 characters');
  if(request.no_after)throw new Error('after_scope is incompatible with no_after');
}
// Validate the substitute for the after-snapshot before any network/input effect.
if('no_after'in request){
  if(typeof request.no_after!=='boolean')throw new Error('no_after must be a boolean');
  if(request.no_after){
    if(request.operation!=='act')throw new Error('no_after requires act');
    if(request.image)throw new Error('no_after is incompatible with image');
    const actions=request.actions;
    if(!Array.isArray(actions)||!actions.length)throw new Error('no_after requires a final assert action');
    const last=actions[actions.length-1];
    if(!last||last.type!=='assert')throw new Error('no_after requires the final action to be assert');
    // Match assertAction precedence; ignored predicates cannot prove success.
    const effective=last.value!==undefined?'value':last.text!==undefined?'text':
      last.checked!==undefined?'checked':'';
    const meaningful=effective==='value'?typeof last.value==='string':
      effective==='text'?typeof last.text==='string'&&last.text.length>0:
      effective==='checked'?typeof last.checked==='boolean':false;
    if(!meaningful)throw new Error('no_after final assert needs text, value or checked');
  }
}
// Scope filters one observation; validate before any network request.
if(request.scope!==undefined){
  if(typeof request.scope!=='string'||!request.scope.trim())throw new Error('scope must be a non-empty CSS selector');
  if(request.scope.length>1024)throw new Error('scope must be at most 1024 characters');
  if(request.operation!=='observe')throw new Error('scope is only valid for observe');
}
const endpoint=new URL(request.endpoint);
if (!['127.0.0.1','localhost','[::1]'].includes(endpoint.hostname)) throw new Error('CDP endpoint must be loopback');
const tabs=await (await fetch(new URL('/json/list',endpoint),{signal:AbortSignal.timeout(4000)})).json();
if(request.operation==='tabs') {
  return tabs.filter(t=>t.type==='page').map(({id,title,url})=>({id,title,url}));
}
const target=tabs.find(t=>t.type==='page'&&t.id===request.target);
if(!target) throw new Error('exact --target required; use browser tabs');
const debuggerUrl=new URL(target.webSocketDebuggerUrl);
if(!['127.0.0.1','localhost','[::1]'].includes(debuggerUrl.hostname)||!['ws:','wss:'].includes(debuggerUrl.protocol))throw new Error('CDP debugger must be loopback WebSocket');
ws=new WebSocket(debuggerUrl.href);
const pending=new Map();let sequence=0;
ws.addEventListener('close',()=>{
  const error=new Error('CDP WebSocket closed');
  for(const p of pending.values()){clearTimeout(p.timer);p.reject(error);}
  pending.clear();
});
ws.addEventListener('message',event=>{
  const result=JSON.parse(event.data),p=pending.get(result.id);
  if(!p)return;
  pending.delete(result.id);clearTimeout(p.timer);
  if(result.error)p.reject(new Error(result.error.message));else p.resolve(result.result);
});
await new Promise((resolve,reject)=>{
  ws.addEventListener('open',resolve,{once:true});
  ws.addEventListener('error',reject,{once:true});
  ws.addEventListener('close',()=>reject(new Error('CDP WebSocket closed before open')),{once:true});
});
async function call(method,params={}) {
  if(ws.readyState!==WebSocket.OPEN)throw new Error('CDP WebSocket is not open');
  const id=++sequence;
  return await new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>{pending.delete(id);reject(new Error('CDP timeout: '+method));},5000);
    pending.set(id,{resolve,reject,timer});
    try{ws.send(JSON.stringify({id,method,params}));}
    catch(error){pending.delete(id);clearTimeout(timer);reject(error);}
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
const elementExpression=(a,body)=>`(()=>{const e=(${pageState.toString()})(${JSON.stringify(request.snapshot)},${JSON.stringify({ref:a.ref,selector:a.selector})});${body}})()`;
const INTERACTIVE='button,a[href],input,textarea,select,summary,[role="button"],[role="checkbox"],[role="tab"],[role="menuitem"],[contenteditable="true"]';
async function snapshot(explicitScope) {
  const id=crypto.randomUUID().slice(0,12);
  // An explicit scope applies to this one snapshot only; request.scope is never mutated.
  const resolve=JSON.stringify(explicitScope===undefined?request.scope:explicitScope);
  return await evaluate(`(()=>{
    ${resolve?`let roots;
    try{roots=document.querySelectorAll(${resolve});}catch(_){throw new Error('scope selector is not valid CSS');}
    if(!roots.length)throw new Error('scope selector matched no element');
    if(roots.length!==1)throw new Error('scope selector must match exactly one element');
    const scope=roots[0];`:'const scope=null;'}
    const s=globalThis.__agentCu={id:${JSON.stringify(id)},created:Date.now(),url:location.href,refs:new Map()};
    const elements=[],visible=[],offscreen=[];let index=0;
    let candidates=(scope??document).querySelectorAll(${JSON.stringify(INTERACTIVE)});
    if(scope?.matches(${JSON.stringify(INTERACTIVE)}))candidates=[scope,...candidates];
    for(const e of candidates){
      const r=e.getBoundingClientRect(),style=getComputedStyle(e);
      if(!r.width||!r.height||style.visibility==='hidden'||style.display==='none'||e.type==='hidden')continue;
      const outside=r.right<=0||r.left>=innerWidth||r.bottom<=0||r.top>=innerHeight;
      (outside?offscreen:visible).push(e);
    }
    const ordered=visible.concat(offscreen),truncated=ordered.length>${maxElements};
    for(const e of ordered.slice(0,${maxElements})){
      const ref='e'+(++index);s.refs.set(ref,e);
      const field=/^(INPUT|TEXTAREA|SELECT)$/.test(e.tagName)||e.isContentEditable;
      const label=e.getAttribute('aria-label')||e.labels?.[0]?.innerText||(!field&&e.innerText)||e.getAttribute('placeholder')||e.getAttribute('title')||e.name||'';
      const item={ref,role:e.getAttribute('role')||e.tagName.toLowerCase(),name:label.trim().slice(0,120)};
      if(e.disabled)item.disabled=true;
      if('value'in e||e.isContentEditable)item.value='[redacted]';
      if('checked'in e&&(e.type==='checkbox'||e.type==='radio'))item.checked=e.checked;
      if(index>visible.length)item.offscreen=true;
      elements.push(item);
    }
    const frames=scope?(scope.matches('iframe')?1:0)+scope.querySelectorAll('iframe').length
      :document.querySelectorAll('iframe').length;
    return {snapshot:s.id,title:document.title,url:location.href,elements,truncated,iframes:frames,
      ${resolve?'scoped:true,':''}};
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
  if(!regular.length)throw new Error('key action needs a non-modifier key');
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
  if(request.operation==='act'){
    if(!request.snapshot)throw new Error('--snapshot required');
    // Preflight the entire schema before any side effects.
    for(const a of request.actions){
      if(['click','fill','set_value','assert'].includes(a.type)&&(!a.ref&&!a.selector||a.ref&&a.selector))throw new Error('exactly one ref or selector required');
      if(a.type==='key'&&a.keys.every(k=>/^(ctrl|alt|shift|meta|super)$/i.test(k)))throw new Error('key action needs a non-modifier key');
      if(a.type==='key')for(const k of a.keys)if(!/^(ctrl|alt|shift|meta|super|Enter|Tab|Escape|Back[Ss]pace|Delete|Arrow(Left|Right|Up|Down)|Home|End|PageUp|PageDown|space|.)$/.test(k))throw new Error('unsupported key');
      if(a.type==='scroll'&&!Number.isFinite(a.dy))throw new Error('scroll dy required');
    }
    const start=Date.now();
    try{
      for(const a of request.actions){
        // Protect key/scroll operations as well as ref-based operations after navigation.
        await evaluate(`(()=>{const s=globalThis.__agentCu;if(!s||s.id!==${JSON.stringify(request.snapshot)}||s.url!==location.href||Date.now()-s.created>90000)throw new Error('stale snapshot');})()`);
        if(a.type==='click')await click(a);
        else if(a.type==='set_value'){
          const text=JSON.stringify(a.text),locator=JSON.stringify({ref:a.ref,selector:a.selector});
          const source=`(()=>{let attempted=false;try{
            const e=(${pageState.toString()})(${JSON.stringify(request.snapshot)},${locator});
            if(!/^(INPUT|TEXTAREA)$/.test(e.tagName)||e.tagName==='INPUT'&&!/^(text|search|tel|url|email)$/.test(e.type||'text'))return {ok:false,error:'unsupported field'};
            if(e.disabled||e.matches(':disabled')||e.readOnly||e.getAttribute('aria-disabled')==='true'||e.closest('[inert]'))return {ok:false,error:'field unavailable'};
            if(e.maxLength>=0&&${text}.length>e.maxLength)return {ok:false,error:'value exceeds maxlength'};
            const r=e.getBoundingClientRect(),style=getComputedStyle(e),x=r.left+r.width/2,y=r.top+r.height/2,hit=document.elementFromPoint(x,y);
            if(!e.getClientRects().length||!r.width||!r.height||style.display==='none'||style.visibility!=='visible'||x<0||x>=innerWidth||y<0||y>=innerHeight||!hit||!(e===hit||e.contains(hit)))return {ok:false,error:'field is not visible'};
            if(e.value===${text})return {ok:true};
            const proto=e.tagName==='INPUT'?HTMLInputElement.prototype:HTMLTextAreaElement.prototype;
            const setter=Object.getOwnPropertyDescriptor(proto,'value')?.set;if(!setter)return {ok:false,error:'field setter unavailable'};
            attempted=true;setter.call(e,${text});
            if(!e.isConnected||e.value!==${text})return {ok:false,error:'value verification failed',mutation_may_have_occurred:true};
            e.dispatchEvent(new InputEvent('input',{bubbles:true,composed:true,inputType:'insertReplacementText',data:null}));
            e.dispatchEvent(new Event('change',{bubbles:true}));
            if(!e.isConnected||e.value!==${text})return {ok:false,error:'value verification failed',mutation_may_have_occurred:true};
            return {ok:true};
          }catch(_){return {ok:false,error:'value update failed',mutation_may_have_occurred:attempted};}})()`;
          const updated=await evaluate(source);
          if(!updated?.ok){const error=new Error(updated?.error||'value update failed');error.mutation_may_have_occurred=!!updated?.mutation_may_have_occurred;throw error;}
        }
        else if(a.type==='fill'){
          await click(a);
          const editable=await evaluate(elementExpression(a,'return document.activeElement===e && !e.readOnly && (e.isContentEditable || /^(INPUT|TEXTAREA)$/.test(e.tagName));'));
          if(!editable)throw new Error('field is not editable or did not gain focus');
          await key(['ctrl','a']);await call('Input.insertText',{text:a.text});
          const matches=await evaluate(elementExpression(a,'return (e.isContentEditable?e.textContent:e.value)==='+JSON.stringify(a.text)+';'));
          if(!matches)throw new Error('fill verification failed');
        }else if(a.type==='key')await key(a.keys);
        else if(a.type==='scroll')await call('Input.dispatchMouseEvent',{type:'mouseWheel',x:a.x??100,y:a.y??100,deltaX:a.dx??0,deltaY:a.dy});
        else if(a.type==='wait')await new Promise(r=>setTimeout(r,a.ms??100));
        else if(a.type==='assert')await assertAction(a);
        completed++;
      }
      result={ok:true,completed,execution_ms:Date.now()-start};
    }catch(e){result={ok:false,completed,error:e.message,execution_ms:Date.now()-start};if(e.mutation_may_have_occurred)result.mutation_may_have_occurred=true;}
    // Failed tasks still need their diagnostic snapshot.
    if(result.ok&&request.no_after)result.after_skipped=true;
    else if(result.ok)try{result.after=await snapshot(request.after_scope);}catch(_){result.after_unavailable=true;}
    else try{result.after=await snapshot();}catch(_){result.after_unavailable=true;}
  }else result=await snapshot();
  if(request.image)result.image_base64=(await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false})).data;
  return result;
}catch(e){process.exitCode=1;return {ok:false,completed,error:e.message};}
finally{ws?.close();}
}

if(process.argv?.includes('--worker')) {
  const lines=createInterface({input:process.stdin,crlfDelay:Infinity});
  try {
    for await(const line of lines) {
      let result;
      try{result=await handle(JSON.parse(line));}
      catch(e){result={ok:false,completed:0,error:e.message};}
      console.log(JSON.stringify(result));
      if(result?.ok===false){process.exitCode=1;break;}
    }
  }finally{lines.close();process.stdin.destroy();}
}else {
  console.log(JSON.stringify(await handle(JSON.parse(fs.readFileSync(0,'utf8')))));
}
