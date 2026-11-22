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
  removeEventListener(){}
  send(){sent++;throw new Error('preflight must not dispatch');}
  close(){closed=true;}
}
const process={exitCode:0,stdin:(async function*(){yield JSON.stringify(request);})(),destroy(){}};
await vm.runInNewContext('(async()=>{'+source.replace(/^import .*;$/gm,'')+'})()',{
  fs:{readFileSync:()=>JSON.stringify(request)},crypto:{},URL,WebSocket,process,
  fetch:async ()=>({json:async ()=>[{type:'page',id:'test',webSocketDebuggerUrl:'ws://127.0.0.1:9222/test'}]}),
  AbortSignal,queueMicrotask,setTimeout,clearTimeout,console:{log:s=>output.push(JSON.parse(s))}
});
assert.equal(process.exitCode,1);
assert.equal(output[0].error,'key action needs a non-modifier key');
assert.equal(output[0].completed,0);assert.equal(sent,0);assert.equal(closed,true);
console.log('ok adapter preflight rejects modifiers only, emits reason, accepts IPv6');

// Run the harvest operation: one JS evaluate grounds the selector, one
// Accessibility.getFullAXTree call returns the protocol inventory, and
// DOM.getBoxModel cross-checks the rect. The fake transport evaluates
// the real harvest expression in a vm page (one input, focused), so the
// rect/hit/focused values come from production JS, not canned geometry.
const harvestRequest={operation:'harvest',endpoint:'http://127.0.0.1:9223',
  target:'test',selectors:['#msg-input']};
const harvestOutput=[],harvestEvents=[];
const inputEl={tagName:'INPUT',type:'text',isConnected:true,
  isContentEditable:false,readOnly:false,disabled:false,shadowRoot:null,
  getAttribute:k=>k==='aria-label'?'Message':k==='placeholder'?'Type a message':null,
  getBoundingClientRect:()=>({x:86,y:1101,width:440,height:63,
    left:86,top:1101,right:526,bottom:1164}),
  closest:()=>null,contains:()=>false,matches:()=>false};
const harvestPage=vm.createContext({
  window:{devicePixelRatio:1,screenPixelsPerCSSPixel:1,
    visualViewport:{scale:1},innerWidth:1615,innerHeight:1160,
    outerWidth:1863,outerHeight:1176,scrollX:0,scrollY:0},
  document:{title:'fixture',
    querySelector:sel=>sel==='#msg-input'?inputEl:null,
    querySelectorAll:sel=>sel==='*'?[inputEl]:[],
    elementFromPoint:(x,y)=>(x>=86&&x<=526&&y>=1101&&y<=1164)?inputEl:null,
    activeElement:inputEl},
  location:{href:'http://fixture/'},
  getComputedStyle:()=>({visibility:'visible',display:'block'})});
class HarvestWebSocket extends EventTarget {
  static CONNECTING=0;static OPEN=1;static CLOSING=2;static CLOSED=3;
  constructor(){
    super();this.readyState=HarvestWebSocket.CONNECTING;
    queueMicrotask(()=>{this.readyState=HarvestWebSocket.OPEN;
      this.dispatchEvent(new Event('open'));});
  }
  addEventListener(name,fn){super.addEventListener(name,fn);}
  send(raw){
    const {id,method,params}=JSON.parse(raw);
    harvestEvents.push(method);
    let result;
    if(method==='Runtime.evaluate'){
      let value;
      try{value=vm.runInContext(params.expression,harvestPage);}
      catch(e){this.emit({id,error:{message:e.message}});return;}
      // CDP nests the value: frame.result.result.value.
      result={result:{result:{value}}};
    }else if(method==='Accessibility.getFullAXTree'){
      result={result:{nodes:[{nodeId:'1',backendDOMNodeId:2,
        role:{value:'textbox'},name:{value:'Message'},value:{value:''},
        properties:[{name:'focused',value:{value:true}}]}]}};
    }else if(method==='DOM.getDocument'){
      result={result:{root:{nodeId:1}}};
    }else if(method==='DOM.querySelector'){
      result={result:{nodeId:params.selector==='#msg-input'?2:0}};
    }else if(method==='DOM.getBoxModel'){
      result={result:{model:{border:[86,1101,526,1101,526,1164,86,1164],
        content:[86,1101,526,1101,526,1164,86,1164],
        padding:[86,1101,526,1101,526,1164,86,1164],
        margin:[86,1101,526,1101,526,1164,86,1164],width:440,height:63}}};
    }else result={result:{}};
    this.emit({id,...result});
  }
  emit(frame){
    queueMicrotask(()=>this.dispatchEvent(
      new MessageEvent('message',{data:JSON.stringify(frame)})));
  }
  close(){this.readyState=HarvestWebSocket.CLOSED;}
}
const harvestProcess={exitCode:0,
  stdin:(async function*(){yield JSON.stringify(harvestRequest);})(),destroy(){}};
await vm.runInNewContext('(async()=>{'+source.replace(/^import .*;$/gm,'')+'})()',{
  fs:{readFileSync:()=>JSON.stringify(harvestRequest)},crypto:{},URL,
  WebSocket:HarvestWebSocket,process:harvestProcess,EventTarget,Event,MessageEvent,
  fetch:async ()=>({json:async ()=>[{type:'page',id:'test',
    webSocketDebuggerUrl:'ws://127.0.0.1:9223/test'}]}),
  AbortSignal,queueMicrotask,setTimeout,clearTimeout,
  console:{log:s=>harvestOutput.push(JSON.parse(s))}});
assert.equal(harvestProcess.exitCode,0);
assert.equal(harvestOutput[0].ok,true,JSON.stringify(harvestOutput[0]));
assert.equal(harvestOutput[0].device_pixel_ratio,1);
assert.equal(harvestOutput[0].screen_pixels_per_css_pixel,1);
assert.equal(harvestOutput[0].zoom,1);
const harvested=harvestOutput[0].items['#msg-input'];
assert.deepEqual(harvested.rect,
  {x:86,y:1101,width:440,height:63,center_x:306,center_y:1132.5});
assert.equal(harvested.hit,true);
assert.equal(harvested.focused,true);
assert.deepEqual(harvested.box_model,{x:86,y:1101,width:440,height:63});
assert.equal(harvested.box_model_matches,true);
assert.equal(harvestOutput[0].ax_tree.length,1);
assert.equal(harvestOutput[0].ax_tree[0].role,'textbox');
assert.equal(harvestOutput[0].ax_tree[0].name,'Message');
assert.equal(harvestOutput[0].ax_tree[0].focused,true);
for(const method of ['Runtime.evaluate','Accessibility.getFullAXTree',
  'DOM.getDocument','DOM.querySelector','DOM.getBoxModel']){
  assert.ok(harvestEvents.includes(method),'harvest calls '+method);
}
assert.equal(harvestEvents.filter(m=>m==='Runtime.evaluate').length,1,
  'one evaluate grounds the whole inventory');
console.log('ok harvest grounds one selector from one evaluate plus AX tree and box model');

// Focus action tests (C5-B1 landing, spec section 8 plus F10 (a),
// (b), (g)): whole-adapter vm run with a fake page carrying
// globalThis.__agentCu, refs, and an activeElement stub. The focus
// branch lives inline in the handle() dispatch loop, not in a
// standalone function, so no function slicing applies here.
function makeFocusPage({disabled=false, readOnly=false, focusWorks=true}={}) {
  const body={tagName:'BODY',isConnected:true};
  const textarea={
    tagName:'TEXTAREA',type:'textarea',isConnected:true,
    isContentEditable:false,readOnly,disabled,
    maxLength:-1,_value:'',
    getAttribute:k=>k==='aria-label'?'Message':null,
    getBoundingClientRect:()=>({x:86,y:1101,width:440,height:63,
      left:86,top:1101,right:526,bottom:1164}),
    getClientRects:()=>[{}],
    closest:()=>null,contains:()=>false,
    matches:sel=>sel===':disabled'?disabled:false,
    focus(){if(focusWorks)page.document.activeElement=textarea;},
    dispatchEvent:()=>true,
  };
  Object.defineProperty(textarea,'value',{
    get(){return textarea._value;},
    set(v){textarea._value=v;},
    configurable:true,enumerable:true});
  const page={
    window:{devicePixelRatio:1,innerWidth:1615,innerHeight:1160,
      outerWidth:1863,outerHeight:1176,scrollX:0,scrollY:0},
    document:{title:'fixture',
      activeElement:body,
      querySelector:sel=>sel==='textarea[aria-label="Message"]'?textarea:null,
      querySelectorAll:sel=>sel==='textarea[aria-label="Message"]'?[textarea]:[],
      elementFromPoint:(x,y)=>(x>=86&&x<=526&&y>=1101&&y<=1164)?textarea:null},
    location:{href:'http://fixture/'},
    getComputedStyle:()=>({visibility:'visible',display:'block'}),
  };
  // The native-setter path in set_value reads the prototype
  // descriptor, so the fake textarea class carries the same
  // accessor the element itself carries.
  page.HTMLTextAreaElement=function(){};
  page.HTMLTextAreaElement.prototype={};
  Object.defineProperty(page.HTMLTextAreaElement.prototype,'value',{
    get(){return this._value;},
    set(v){this._value=v;},
    configurable:true});
  page.HTMLInputElement=function(){};
  page.HTMLInputElement.prototype={};
  page.Event=class{constructor(type,init){this.type=type;Object.assign(this,init||{});}};
  page.InputEvent=class{constructor(type,init){this.type=type;Object.assign(this,init||{});}};
  page.globalThis=page;
  page.__agentCu={id:'test',created:Date.now(),url:'http://fixture/',
    refs:new Map([['e1',textarea]])};
  const context=vm.createContext(page);
  return {page,context,body,textarea};
}

class FocusWebSocket extends EventTarget {
  static CONNECTING=0;static OPEN=1;static CLOSING=2;static CLOSED=3;
  constructor(pageContext,record){
    super();this.readyState=FocusWebSocket.CONNECTING;this._page=pageContext;this._record=record;
    queueMicrotask(()=>{this.readyState=FocusWebSocket.OPEN;
      this.dispatchEvent(new Event('open'));});
  }
  addEventListener(name,fn){super.addEventListener(name,fn);}
  send(raw){
    const {id,method,params}=JSON.parse(raw);
    this._record.push(method);
    let result;
    if(method==='Runtime.evaluate'){
      let value;
      try{value=vm.runInContext(params.expression,this._page);}
      catch(e){result={result:{exceptionDetails:{text:'Uncaught',
        exception:{description:'Error: '+e.message}}}};
        this.emit({id,...result});return;}
      result={result:{result:{value}}};
    }else result={result:{}};
    this.emit({id,...result});
  }
  emit(frame){
    queueMicrotask(()=>this.dispatchEvent(
      new MessageEvent('message',{data:JSON.stringify(frame)})));
  }
  close(){this.readyState=FocusWebSocket.CLOSED;}
}

async function runFocusAdapter(request,pageSetup={}) {
  const {page,context}=makeFocusPage(pageSetup);
  const calls=[];
  const output=[];
  const proc={exitCode:0,
    stdin:(async function*(){yield JSON.stringify(request);})(),destroy(){}};
  await vm.runInNewContext('(async()=>{'+source.replace(/^import .*;$/gm,'')+'})()',{
    fs:{readFileSync:()=>JSON.stringify(request)},crypto:{randomUUID:()=>'snap-test-1'},URL,
    WebSocket:class extends FocusWebSocket{
      constructor(url){super(context,calls);}},
    process:proc,EventTarget,Event,MessageEvent,
    fetch:async ()=>({json:async ()=>[{type:'page',id:'test',
      webSocketDebuggerUrl:'ws://127.0.0.1:9223/test'}]}),
    AbortSignal,queueMicrotask,setTimeout,clearTimeout,
    console:{log:s=>output.push(JSON.parse(s))}});
  return {output:output[0],calls,page,exitCode:proc.exitCode};
}

const focusRequest={operation:'act',endpoint:'http://127.0.0.1:9223',
  target:'test',snapshot:'test',
  actions:[{type:'focus',ref:'e1'}]};
let focusRun=await runFocusAdapter(focusRequest);
assert.equal(focusRun.output.ok,true,JSON.stringify(focusRun.output));
assert.equal(focusRun.output.completed,1);
assert.equal(focusRun.page.document.activeElement.tagName,'TEXTAREA');
assert.ok(!focusRun.calls.some(m=>m.startsWith('Input.')),
  'focus dispatches zero Input methods: '+focusRun.calls.join(','));
console.log('ok focus resolves a ref, focuses, asserts activeElement, no Input methods');

// F10 (a): a focus where the element never gains focus throws the
// fill wording.
let focusFail=await runFocusAdapter(focusRequest,{focusWorks:false});
assert.equal(focusFail.output.ok,false);
assert.match(focusFail.output.error,/did not gain focus/);
assert.equal(focusFail.output.completed,0);
console.log('ok focus failure throws field is not editable or did not gain focus');

// Focus on a disabled or readOnly field throws 'field unavailable'.
let focusDisabled=await runFocusAdapter(focusRequest,{disabled:true});
assert.equal(focusDisabled.output.ok,false);
assert.match(focusDisabled.output.error,/field unavailable/);
let focusReadOnly=await runFocusAdapter(focusRequest,{readOnly:true});
assert.equal(focusReadOnly.output.ok,false);
assert.match(focusReadOnly.output.error,/field unavailable/);
console.log('ok focus on a disabled or readOnly field throws field unavailable');

// Focus on a missing ref throws 'element missing; observe again'.
let focusMissing=await runFocusAdapter({operation:'act',endpoint:'http://127.0.0.1:9223',
  target:'test',snapshot:'test',
  actions:[{type:'focus',ref:'e9'}]});
assert.equal(focusMissing.output.ok,false);
assert.match(focusMissing.output.error,/element missing; observe again/);
console.log('ok focus on a missing ref throws element missing');

// Focus with both ref and selector throws before any dispatch.
let focusBoth=await runFocusAdapter({operation:'act',endpoint:'http://127.0.0.1:9223',
  target:'test',snapshot:'test',
  actions:[{type:'focus',ref:'e1',selector:'textarea'}]});
assert.equal(focusBoth.output.ok,false);
assert.match(focusBoth.output.error,/exactly one ref or selector required/);
assert.equal(focusBoth.calls.length,0,'preflight must not dispatch');
console.log('ok focus with both ref and selector throws exactly one ref or selector required');

// F10 (b): focus via selector, not only by ref.
let focusSelector=await runFocusAdapter({operation:'act',endpoint:'http://127.0.0.1:9223',
  target:'test',snapshot:'test',
  actions:[{type:'focus',selector:'textarea[aria-label="Message"]'}]});
assert.equal(focusSelector.output.ok,true,JSON.stringify(focusSelector.output));
assert.equal(focusSelector.page.document.activeElement.tagName,'TEXTAREA');
console.log('ok focus via selector resolves and focuses');

// Key Enter after focus dispatches keyDown plus keyUp with text '\r'.
const focusKeyRequest={operation:'act',endpoint:'http://127.0.0.1:9223',
  target:'test',snapshot:'test',
  actions:[{type:'focus',ref:'e1'},{type:'key',keys:['Enter']}]};
let focusKey=await runFocusAdapter(focusKeyRequest);
assert.equal(focusKey.output.ok,true,JSON.stringify(focusKey.output));
assert.equal(focusKey.output.completed,2);
assert.deepEqual(focusKey.calls.filter(m=>m==='Input.dispatchKeyEvent').length,2);
console.log('ok key Enter after focus dispatches keyDown plus keyUp');

// set_value still does not focus: activeElement is unchanged after
// a set_value call.
let setValueRun=await runFocusAdapter({operation:'act',endpoint:'http://127.0.0.1:9223',
  target:'test',snapshot:'test',
  actions:[{type:'set_value',ref:'e1',text:'hello'}]});
assert.equal(setValueRun.output.ok,true,JSON.stringify(setValueRun.output));
assert.equal(setValueRun.page.document.activeElement.tagName,'BODY',
  'set_value must not move focus');
assert.equal(setValueRun.page.__agentCu.refs.get('e1').value,'hello');
console.log('ok set_value still does not focus');
