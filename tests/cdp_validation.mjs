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
