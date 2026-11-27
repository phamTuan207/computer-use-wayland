// Dependency-free CDP adapter, Node >=22. Explicit target; no model API calls.
import crypto from 'node:crypto';

function createTransport(url) {
  const ws=new WebSocket(url),pending=new Map();
  let sequence=0,transportError,usable=true,disposed=false;
  function rejectPending(error){
    for(const p of pending.values()){clearTimeout(p.timer);p.reject(error);}
    pending.clear();
  }
  function closed(){
    transportError??=new Error('CDP WebSocket closed');
    usable=false;rejectPending(transportError);
    ws.removeEventListener('message',message);
    ws.removeEventListener('error',failed);
    ws.removeEventListener('close',closed);
  }
  function failTransport(error){
    if(transportError)return;
    transportError=error;usable=false;rejectPending(error);
    try{ws.close();}catch(_){}
  }
  function failed(){failTransport(new Error('CDP WebSocket error'));}
  function message(event){
    let result;
    try{result=JSON.parse(event.data);}
    catch(_){failTransport(new Error('malformed CDP WebSocket JSON'));return;}
    if(!result||typeof result!=='object'||Array.isArray(result)){failTransport(new Error('unexpected CDP WebSocket frame'));return;}
    const p=pending.get(result.id);
    if(!p)return;
    pending.delete(result.id);clearTimeout(p.timer);
    if(result.error){usable=false;p.reject(new Error(result.error.message));}
    else p.resolve(result.result);
  }
  const ready=new Promise((resolve,reject)=>{
    const finish=error=>{
      clearTimeout(timer);
      ws.removeEventListener('open',opened);
      ws.removeEventListener('error',openError);
      ws.removeEventListener('close',openClose);
      if(error)reject(error);else resolve();
    };
    const opened=()=>finish();
    const openError=()=>finish(new Error('CDP WebSocket error before open'));
    const openClose=()=>finish(new Error('CDP WebSocket closed before open'));
    const timer=setTimeout(()=>finish(new Error('CDP WebSocket open timed out')),4000);
    ws.addEventListener('open',opened,{once:true});
    ws.addEventListener('error',openError,{once:true});
    ws.addEventListener('close',openClose,{once:true});
  });
  ws.addEventListener('message',message);
  ws.addEventListener('close',closed);
  ws.addEventListener('error',failed);
  async function call(method,params={}){
    if(transportError)throw transportError;
    if(ws.readyState!==WebSocket.OPEN)throw new Error('CDP WebSocket is not open');
    const id=++sequence;
    return await new Promise((resolve,reject)=>{
      // A failed call keeps its diagnostic path, but its transport cannot be reused.
      const timer=setTimeout(()=>{usable=false;pending.delete(id);reject(new Error('CDP timeout: '+method));},5000);
      pending.set(id,{resolve,reject,timer});
      try{ws.send(JSON.stringify({id,method,params}));}
      catch(error){usable=false;pending.delete(id);clearTimeout(timer);reject(error);}
    });
  }
  function dispose(){
    if(disposed)return;
    disposed=true;usable=false;
    transportError??=new Error('CDP WebSocket closed');
    rejectPending(transportError);
    ws.removeEventListener('message',message);
    try{ws.close();}catch(_){}
  }
  return {ready,call,dispose,get error(){return transportError;},
    get reusable(){return usable&&!disposed&&!transportError&&ws.readyState===WebSocket.OPEN&&pending.size===0;}};
}

async function handle(request,owner=null) {
let connection,connectionKey;
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
  if(request.after_scope.length>1024)throw new Error('after_scope must be at most 1024 UTF-16 code units');
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
  if(request.scope.length>1024)throw new Error('scope must be at most 1024 UTF-16 code units');
  if(request.operation!=='observe')throw new Error('scope is only valid for observe');
}
if(!['tabs','observe','act'].includes(request.operation))throw new Error('unknown operation');
const endpoint=new URL(request.endpoint);
if (!['127.0.0.1','localhost','[::1]'].includes(endpoint.hostname)) throw new Error('CDP endpoint must be loopback');
// A failed tab-list fetch must name the exact URL and the underlying cause;
// otherwise preflight failures look like bare "fetch failed" with no anchor.
const listUrl=new URL('/json/list',endpoint);
let tabs;
try {
  const response=await fetch(listUrl,{signal:AbortSignal.timeout(4000)});
  if(response.ok===false)throw new Error(`HTTP ${response.status}`);
  tabs=await response.json();
}catch(e){
  const cause=e.cause;
  throw new Error(`CDP GET ${listUrl.href}: ${e.message}; cause: ${cause?.code??''} ${cause?.message??'unavailable'}`);
}
if(request.operation==='tabs') {
  result=tabs.filter(t=>t.type==='page').map(({id,title,url})=>({id,title,url}));
  // Listing grants no target authority; the next action still fetches its own list.
  connection=owner?.connection;connectionKey=owner?.key;
  return result;
}
const target=tabs.find(t=>t.type==='page'&&t.id===request.target);
if(!target) throw new Error('exact --target required; use browser tabs');
const debuggerUrl=new URL(target.webSocketDebuggerUrl);
if(!['127.0.0.1','localhost','[::1]'].includes(debuggerUrl.hostname)||!['ws:','wss:'].includes(debuggerUrl.protocol))throw new Error('CDP debugger must be loopback WebSocket');
connectionKey=JSON.stringify([endpoint.href,target.id,debuggerUrl.href,target.url]);
if(owner?.connection&&owner.key===connectionKey&&owner.connection.reusable)connection=owner.connection;
else{
  owner?.connection?.dispose();
  if(owner)owner.connection=null;
  connection=createTransport(debuggerUrl.href);
  await connection.ready;
}
const call=connection.call;
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
// Pick 4 DOM-first fast path (speed-swarm prototype): with
// CU_PICK4_FASTPATH=1 the snapshot also carries each element's viewport
// rect and center, so the executor can ground from the DOM alone and skip
// the screenshot. Read on the Node side, never in-page: the snapshot
// expression runs in the page context, where process does not exist.
// Rects are viewport-relative; clicks still go through the in-page ref
// path with its hit test. Default off: the snapshot shape is exactly
// the baseline shape.
const pick4Rects=process.env?.CU_PICK4_FASTPATH==='1';
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
      const item={ref,role:e.getAttribute('role')||(e.tagName==='A'?'link':e.tagName.toLowerCase()),name:label.trim().slice(0,120)};
      ${pick4Rects?`const __r=e.getBoundingClientRect();
      item.rect={x:Math.round(__r.left),y:Math.round(__r.top),width:Math.round(__r.width),height:Math.round(__r.height)};
      item.center={x:Math.round(__r.left+__r.width/2),y:Math.round(__r.top+__r.height/2)};`:''}
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
async function harvest(request) {
  // One-shot bulk grounding (VISION 1, CDP path): one JS evaluate
  // returns rects for every requested selector plus the viewport
  // metrics, one Accessibility.getFullAXTree call returns the
  // protocol's own interactive inventory (roles/names/values), and
  // DOM.getBoxModel cross-checks each requested selector's quad
  // against the JS rect where the element is reachable from the
  // document root. Shadow-DOM elements are not reachable by CDP
  // querySelector, so their box_model is null and the JS rect stands.
  // No screenshot is taken and no observation is needed: the executor
  // clicks from these rects. Open item: the remote-debugging-port
  // needs a custom profile/relaunch vs the already-logged-in Brave
  // (Brave holds no debugging port on its default profile), so this
  // operation runs against the agent-managed Chromium, not Brave,
  // until that is resolved.
  if (request.selectors !== undefined) {
    if (!Array.isArray(request.selectors) || request.selectors.some(s => typeof s !== 'string' || !s.trim() || s.length > 1024))
      throw new Error('selectors must be an array of non-empty CSS selectors');
  }
  const selectors = request.selectors ?? [];
  const dom = await evaluate(`(()=>{const out={device_pixel_ratio:window.devicePixelRatio,screen_pixels_per_css_pixel:(typeof window.screenPixelsPerCSSPixel==='number'?window.screenPixelsPerCSSPixel:null),zoom:(window.visualViewport?window.visualViewport.scale:1),inner_size:[window.innerWidth,window.innerHeight],outer_size:[window.outerWidth,window.outerHeight],scroll:[window.scrollX,window.scrollY],items:{}};
  function pierce(sel,root){let e=root.querySelector(sel);if(e)return e;const all=root.querySelectorAll('*');for(const el of all){if(el.shadowRoot){e=pierce(sel,el.shadowRoot);if(e)return e;}}return null;}
  function interactive(el){if(!el)return false;const tag=(el.tagName||'').toUpperCase();if(/^(BUTTON|A|INPUT|TEXTAREA|SELECT|OPTION|LABEL|SUMMARY)$/.test(tag))return true;if(el.closest&&el.closest('[role="button"],[role="link"],[role="checkbox"],[role="menuitem"],[role="tab"]'))return true;return false;}
  let a=document.activeElement;while(a&&a.shadowRoot&&a.shadowRoot.activeElement)a=a.shadowRoot.activeElement;
  for(const sel of ${JSON.stringify(selectors)}){const e=pierce(sel,document);if(!e){out.items[sel]=null;continue;}const r=e.getBoundingClientRect();const x=r.left+r.width/2,y=r.top+r.height/2;const hit=document.elementFromPoint(x,y);out.items[sel]={rect:{x:r.x,y:r.y,width:r.width,height:r.height,center_x:x,center_y:y},hit:!!hit&&(e===hit||(e.contains(hit)&&!interactive(hit))),focused:(a===e),tag:e.tagName,role:e.getAttribute('role')||'',name:(e.getAttribute('aria-label')||e.getAttribute('placeholder')||'').slice(0,120)};}
  return out;})()`);
  const ax = await call('Accessibility.getFullAXTree', {});
  const axTree = [];
  for (const node of ax.nodes ?? []) {
    const role = node.role?.value;
    if (!role || !/^(button|link|textbox|checkbox|radio|combobox|searchbox|spinbutton|slider|menuitem|menuitemcheckbox|menuitemradio|tab|switch|treeitem)$/i.test(role)) continue;
    axTree.push({nodeId: node.nodeId, backendDOMNodeId: node.backendDOMNodeId ?? null,
      role, name: node.name?.value ?? '',
      // I22: never carry a protected (password) field's value.
      value: (node.properties ?? []).some(p => p.name === 'protected' && p.value?.value === true) ? '[redacted]' : (node.value?.value ?? null),
      focused: (node.properties ?? []).some(p => p.name === 'focused' && p.value?.value === true),
      disabled: (node.properties ?? []).some(p => p.name === 'disabled' && p.value?.value === true)});
  }
  const doc = await call('DOM.getDocument', {depth: 0});
  const rootId = doc.root.nodeId;
  for (const sel of selectors) {
    const item = dom.items[sel];
    if (!item) continue;
    try {
      const found = await call('DOM.querySelector', {nodeId: rootId, selector: sel});
      if (!found.nodeId) {
        item.box_model = null;
        item.box_model_note = 'not reachable from the document root (shadow DOM or iframe)';
        continue;
      }
      const box = await call('DOM.getBoxModel', {nodeId: found.nodeId});
      const q = box.model.border;
      const xs = [q[0], q[2], q[4], q[6]], ys = [q[1], q[3], q[5], q[7]];
      const bx = Math.min(...xs), by = Math.min(...ys);
      const bw = Math.max(...xs) - bx, bh = Math.max(...ys) - by;
      // The quad is document-space (viewport rect plus scroll), so
      // the cross-check compares the scroll-invariant size; x/y are
      // recorded as-is for the caller.
      item.box_model = {x: bx, y: by, width: bw, height: bh};
      item.box_model_matches = Math.abs(bw - item.rect.width) <= 1 && Math.abs(bh - item.rect.height) <= 1;
    } catch (_) {
      item.box_model = null;
    }
  }
  return {ok: true, ...dom, ax_tree: axTree};
}
async function click(a) {
  const point=await evaluate(elementExpression(a,`
    if(e.disabled)throw new Error('element disabled');
    ${a.type==='confirm_click'?`
    if(e.getAttribute('aria-disabled')==='true'||e.closest('[inert]'))
      throw new Error('element disabled');
    const role=(e.getAttribute('role')||(e.tagName==='A'?'link':e.tagName.toLowerCase())).toLowerCase();
    const field=/^(INPUT|TEXTAREA|SELECT)$/.test(e.tagName)||e.isContentEditable;
    const name=(e.getAttribute('aria-label')||e.labels?.[0]?.innerText||(!field&&e.innerText)||
      e.getAttribute('placeholder')||e.getAttribute('title')||e.name||'').trim().slice(0,120);
    const text=(e.innerText||'').trim().replace(/\\s+/g,' ');
    if(role!==${JSON.stringify(a.expected_role.toLowerCase())}||
       name!==${JSON.stringify(a.expected_name)}||text!==${JSON.stringify(a.expected_text)})
      throw new Error('confirmation text or role/name mismatch');` : ''}
    e.scrollIntoView({block:'center',inline:'center',behavior:'instant'});
    const r=e.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2;
    const hit=document.elementFromPoint(x,y);
    if(!hit||!(e===hit||e.contains(hit)))throw new Error('element covered; observe again');
    return {x,y};`));
  await call('Input.dispatchMouseEvent',{type:'mouseMoved',...point});
  await call('Input.dispatchMouseEvent',{type:'mousePressed',...point,button:'left',clickCount:1});
  await call('Input.dispatchMouseEvent',{type:'mouseReleased',...point,button:'left',clickCount:1});
}
const hoverStyleSignature=`e=>{const s=getComputedStyle(e);return JSON.stringify([
  s.backgroundColor,s.backgroundImage,s.color,s.borderTopColor,s.borderRightColor,
  s.borderBottomColor,s.borderLeftColor,s.boxShadow,s.outlineColor,s.outlineStyle,
  s.filter,s.opacity,s.transform
]);}`;
async function hoverClick(a,timeoutMs){
  const away=await evaluate(elementExpression(a,`
    if(e.disabled||e.getAttribute('aria-disabled')==='true'||e.closest('[inert]'))
      throw new Error('element disabled');
    e.scrollIntoView({block:'center',inline:'center',behavior:'instant'});
    const r=e.getBoundingClientRect(),style=getComputedStyle(e);
    if(!r.width||!r.height||style.display==='none'||style.visibility==='hidden')
      throw new Error('element is not visible');
    if(r.width<8||r.height<8)throw new Error('element too small for off-center hover');
    const x=r.left+r.width*0.25,y=r.top+r.height*0.5;
    if(x<0||x>=innerWidth||y<0||y>=innerHeight)
      throw new Error('off-center hover point is outside the viewport');
    const candidates=[{x:r.left-1,y},{x:r.right+1,y},{x,y:r.top-1},{x,y:r.bottom+1}];
    const point=candidates.find(p=>p.x>=0&&p.x<innerWidth&&p.y>=0&&p.y<innerHeight&&
      !(p.x>=r.left&&p.x<r.right&&p.y>=r.top&&p.y<r.bottom));
    if(!point)throw new Error('cannot establish a non-hover baseline');
    return point;`));
  const deadline=Date.now()+timeoutMs;
  await call('Input.dispatchMouseEvent',{type:'mouseMoved',...away});
  let previousSignature,stableSamples=0,baseline;
  while(Date.now()<=deadline){
    const state=await evaluate(elementExpression(a,`
      const style=getComputedStyle(e),r=e.getBoundingClientRect();
      if(!e.isConnected||!r.width||!r.height||style.display==='none'||style.visibility==='hidden')
        return {visible:false};
      return {visible:true,hovering:e.matches(':hover'),signature:(${hoverStyleSignature})(e)};`));
    if(!state.visible)throw new Error('element became unavailable before hover');
    if(!state.hovering&&state.signature===previousSignature)stableSamples++;
    else stableSamples=0;
    if(stableSamples>=1){baseline=state.signature;break;}
    previousSignature=state.signature;
    await new Promise(resolve=>setTimeout(resolve,16));
  }
  if(baseline===undefined)throw new Error('could not establish a stable non-hover state');
  const point=await evaluate(elementExpression(a,`
    const r=e.getBoundingClientRect(),style=getComputedStyle(e);
    if(e.disabled||e.getAttribute('aria-disabled')==='true'||e.closest('[inert]'))
      throw new Error('element disabled');
    if(!r.width||!r.height||style.display==='none'||style.visibility==='hidden')
      throw new Error('element is not visible');
    const x=r.left+r.width*0.25,y=r.top+r.height*0.5,hit=document.elementFromPoint(x,y);
    if(x<0||x>=innerWidth||y<0||y>=innerHeight||!hit||!(e===hit||e.contains(hit)))
      throw new Error('element covered; observe again');
    if(e.matches(':hover'))throw new Error('could not establish a non-hover baseline');
    return {x,y,signature:(${hoverStyleSignature})(e)};`));
  baseline=point.signature;
  await call('Input.dispatchMouseEvent',{type:'mouseMoved',x:point.x,y:point.y});
  let detected=false;
  while(Date.now()<=deadline){
    const state=await evaluate(elementExpression(a,`
      const r=e.getBoundingClientRect(),hit=document.elementFromPoint(${point.x},${point.y});
      if(!e.isConnected||!r.width||!r.height||!hit||!(e===hit||e.contains(hit)))
        return {valid:false};
      return {valid:true,hovering:e.matches(':hover'),signature:(${hoverStyleSignature})(e)};`));
    if(!state.valid)throw new Error('element moved or became covered during hover');
    if(state.hovering&&state.signature!==baseline){detected=true;break;}
    await new Promise(resolve=>setTimeout(resolve,16));
  }
  if(!detected)throw new Error('hover state did not visibly change; click refused');
  await new Promise(resolve=>setTimeout(resolve,16));
  const confirmed=await evaluate(elementExpression(a,`
    const r=e.getBoundingClientRect(),hit=document.elementFromPoint(${point.x},${point.y});
    return Boolean(e.isConnected&&e.matches(':hover')&&
      ${point.x}>=r.left&&${point.x}<r.right&&${point.y}>=r.top&&${point.y}<r.bottom&&
      hit&&(e===hit||e.contains(hit))&&(${hoverStyleSignature})(e)!==${JSON.stringify(baseline)});`));
  if(!confirmed)throw new Error('hover state changed before click; click refused');
  const clickPoint={x:point.x,y:point.y};
  await call('Input.dispatchMouseEvent',{type:'mousePressed',...clickPoint,button:'left',clickCount:1});
  await call('Input.dispatchMouseEvent',{type:'mouseReleased',...clickPoint,button:'left',clickCount:1});
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
    await new Promise(r=>setTimeout(r,10));
  }
}
  if(request.operation==='act'){
    if(!request.snapshot)throw new Error('--snapshot required');
    // Preflight the entire batch once, before any input or DOM effect.
    if(!Array.isArray(request.actions)||request.actions.length<1||request.actions.length>32)throw new Error('actions must contain 1..32 items');
    const finite=v=>typeof v==='number'&&Number.isFinite(v);
    for(const a of request.actions){
      if(!a||typeof a!=='object'||Array.isArray(a))throw new Error('each action must be an object');
      if(!['click','confirm_click','hover_click','fill','set_value','key','scroll','wait','assert'].includes(a.type))throw new Error('unsupported action');
      if(['click','confirm_click','hover_click','fill','set_value','assert'].includes(a.type)){
        if(('ref' in a)===('selector' in a))throw new Error('exactly one ref or selector required');
        for(const k of ['ref','selector'])if(k in a&&(typeof a[k]!=='string'||!a[k].trim()))throw new Error(k+' must be a non-empty string');
      }
      if(a.type==='confirm_click')for(const [field,limit] of [['expected_role',64],['expected_name',120],['expected_text',256]])
        if(typeof a[field]!=='string'||!a[field].trim()||a[field].length>limit)
          throw new Error('confirm_click requires expected_role, expected_name and expected_text');
      if(a.type==='hover_click'&&'hover_timeout_ms'in a&&
         (!finite(a.hover_timeout_ms)||a.hover_timeout_ms<0||a.hover_timeout_ms>2000))
        throw new Error('hover_timeout_ms must be 0..2000');
      if(a.type==='fill'||a.type==='set_value')
        if(typeof a.text!=='string'||a.text.length>10000)throw new Error('text must be string <=10000 chars');
      if(a.type==='key'){
        if(!Array.isArray(a.keys)||!a.keys.length||!a.keys.every(k=>typeof k==='string'&&k.length<40))throw new Error('keys must be an array of key names');
        if(a.keys.every(k=>/^(ctrl|alt|shift|meta|super)$/i.test(k)))throw new Error('key action needs a non-modifier key');
        for(const k of a.keys)if(!/^(ctrl|alt|shift|meta|super|Enter|Tab|Escape|Back[Ss]pace|Delete|Arrow(Left|Right|Up|Down)|Home|End|PageUp|PageDown|space|.)$/.test(k))throw new Error('unsupported key');
      }
      if(a.type==='scroll'){
        for(const k of ['dx','dy','x','y'])if(k in a&&!finite(a[k]))throw new Error('scroll '+k+' must be a finite number');
        if(!finite(a.dy))throw new Error('scroll dy required');
      }
      if(a.type==='wait'){const ms=a.ms??100;if(!finite(ms)||ms<0||ms>2000)throw new Error('wait ms must be 0..2000');}
      if(a.type==='assert'){
        if('value' in a&&typeof a.value!=='string')throw new Error('assert value must be a string');
        if('text' in a&&typeof a.text!=='string')throw new Error('assert text must be a string');
        if('checked' in a&&typeof a.checked!=='boolean')throw new Error('assert checked must be a boolean');
        if('timeout_ms' in a&&(typeof a.timeout_ms!=='number'||!Number.isFinite(a.timeout_ms)||a.timeout_ms<0))
          throw new Error('assert timeout_ms must be a non-negative finite number');
      }
    }
    const start=Date.now();
    try{
      for(const a of request.actions){
        if(connection.error)throw connection.error;
        // Protect key/scroll operations as well as ref-based operations after navigation.
        await evaluate(`(()=>{const s=globalThis.__agentCu;if(!s||s.id!==${JSON.stringify(request.snapshot)}||s.url!==location.href||Date.now()-s.created>90000)throw new Error('stale snapshot');})()`);
        if(a.type==='click'||a.type==='confirm_click')await click(a);
        else if(a.type==='hover_click')await hoverClick(a,a.hover_timeout_ms??800);
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
        else throw new Error('unsupported action');
        completed++;
        if(connection.error)throw connection.error;
      }
      result={ok:true,completed,execution_ms:Date.now()-start};
    }catch(e){result={ok:false,completed,error:e.message,execution_ms:Date.now()-start};if(e.mutation_may_have_occurred)result.mutation_may_have_occurred=true;}
    // Failed tasks still need their diagnostic snapshot.
    if(result.ok&&request.no_after)result.after_skipped=true;
    else if(result.ok)try{result.after=await snapshot(request.after_scope);}catch(_){result.after_unavailable=true;}
    else try{result.after=await snapshot();}catch(_){result.after_unavailable=true;}
  }else result=await snapshot();
  if(request.image){
    // A capture failure updates the envelope; it never replaces count, timing or
    // the original action error, and never becomes a transport-level exit.
    try{result.image_base64=(await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false})).data;}
    catch(e){
      result.ok=false;
      result.capture_error=e.message;
      if(!result.error)result.error='screenshot failed: '+e.message;
    }
  }
  return result;
}catch(e){process.exitCode=1;return {ok:false,completed,error:e.message};}
finally{
  if(owner&&connection&&result&&result.ok!==false&&connection.reusable){
    owner.connection=connection;owner.key=connectionKey;
  }else{
    connection?.dispose();owner?.connection?.dispose();
    if(owner)owner.connection=null;
  }
}
}

const READ_LIMIT=8*1024*1024;

// UTF-8 byte length without Buffer, so the adapter also runs in a bare sandbox.
function utf8Length(text){
  let bytes=0;
  for(const ch of text){const code=ch.codePointAt(0);bytes+=code<0x80?1:code<0x800?2:code<0x10000?3:4;}
  return bytes;
}

// Bounded line source: refuse past the cap before the whole request is buffered,
// and keep the final unterminated line of the stream exactly as it arrived.
async function* boundedLines(stream){
  stream.setEncoding?.('utf8');
  let parts=[],total=0;
  for await(const chunk of stream){
    const text=String(chunk);
    let start=0;
    while(start<text.length){
      const newline=text.indexOf('\n',start),end=newline<0?text.length:newline+1;
      const part=text.slice(start,end);
      total+=utf8Length(part);
      if(total>READ_LIMIT)throw new Error('request exceeds 8 MiB');
      parts.push(part);
      if(newline>=0){const line=parts.join('');parts=[];total=0;yield line;}
      start=end;
    }
  }
  if(parts.length)yield parts.join('');
}

async function readBounded(stream){
  stream.setEncoding?.('utf8');
  const parts=[];let total=0;
  for await(const chunk of stream){
    const text=String(chunk);
    total+=utf8Length(text);
    if(total>READ_LIMIT)throw new Error('request exceeds 8 MiB');
    parts.push(text);
  }
  return parts.join('');
}

if(process.argv?.includes('--worker')) {
  const owner={connection:null,key:null};
  try {
    for await(const line of boundedLines(process.stdin)){
      let result;
      try{result=await handle(JSON.parse(line),owner);}
      catch(e){result={ok:false,completed:0,error:e.message};}
      console.log(JSON.stringify(result));
      if(result?.ok===false){process.exitCode=1;break;}
    }
  }catch(e){process.exitCode=1;console.log(JSON.stringify({ok:false,completed:0,error:e.message}));}
  finally{owner.connection?.dispose();process.stdin.destroy();}
}else {
  try{
    console.log(JSON.stringify(await handle(JSON.parse(await readBounded(process.stdin)))));
  }catch(e){
    console.log(JSON.stringify({ok:false,completed:0,error:e.message}));
    process.exitCode=1;
  }
}
