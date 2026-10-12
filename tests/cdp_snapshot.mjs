// Run: node tests/cdp_snapshot.mjs. Production adapter + fake CDP/DOM; no network or GUI.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const source=fs.readFileSync(new URL('../scripts/cdp.mjs',import.meta.url),'utf8');
const token='fake-api-token-NEVER-EXPOSE';
class FakeInput {get value(){return this._value??'';} set value(value){this._value=value;}}
class FakeTextarea {get value(){return this._value??'';} set value(value){this._value=value;}}
function element(name,options={}) {
  const {left=10,top=10,width=20,height=20,tagName='BUTTON',...rest}=options;
  const proto=tagName==='INPUT'?FakeInput.prototype:tagName==='TEXTAREA'?FakeTextarea.prototype:Object.prototype;
  const node=Object.assign(Object.create(proto),{tagName,innerText:name,textContent:name,isConnected:true,
    type:'text',disabled:false,readOnly:false,maxLength:-1,
    getAttribute:key=>key==='aria-disabled'?rest.ariaDisabled??null:null,
    closest:()=>rest.inert?node:null,matches:selector=>selector===':disabled'&&Boolean(rest.disabled),
    contains:other=>other===node,scrollIntoView(){},getClientRects:()=>[{}],
    dispatchEvent:event=>{(node.events??=[]).push({type:event.type,trusted:event.isTrusted});rest.onEvent?.(event,node);return true;},
    getBoundingClientRect:()=>({left,top,right:left+width,bottom:top+height,width,height}),...rest});
  return node;
}
async function run(elements,actions,{mutate=text=>text,maxElements,debuggerUrl='ws://127.0.0.1:9222/test'}={}) {
  const expressions=[],replies=[],output=[];
  const document={title:'fixture',activeElement:null,
    querySelectorAll:selector=>selector==='iframe'?[]:selector.startsWith('#')?
      elements.filter(e=>e.id===selector.slice(1)):elements,
    elementFromPoint:()=>elements[0]};
  const page=vm.createContext({document,location:{href:'http://fixture/'},innerWidth:100,innerHeight:100,
    HTMLInputElement:FakeInput,HTMLTextAreaElement:FakeTextarea,
    InputEvent:class {constructor(type,options){this.type=type;this.isTrusted=false;Object.assign(this,options);}},
    Event:class {constructor(type,options){this.type=type;this.isTrusted=false;Object.assign(this,options);}},
    getComputedStyle:e=>({visibility:e.visibility??'visible',display:e.display??'block'})});
  if(actions){
    vm.runInContext("globalThis.__agentCu={id:'before',created:Date.now(),url:location.href,refs:new Map()}",page);
    vm.runInContext('__agentCu',page).refs.set('e1',elements[0]);
  }
  const request={operation:actions?'act':'observe',endpoint:'http://127.0.0.1:9222',target:'test',snapshot:'before',actions,max_elements:maxElements};
  let closed=false;
  class WebSocket {
    listeners={};
    addEventListener(name,fn){this.listeners[name]=fn;if(name==='open')queueMicrotask(fn);}
    send(raw){
      const {id,method,params}=JSON.parse(raw);let result={};
      if(method==='Runtime.evaluate'){
        expressions.push(params.expression);
        try {
          const value=vm.runInContext(params.expression,page);
          replies.push(value);
          result={result:{value}};
        } catch(error){result={exceptionDetails:{text:error.message}};}
      }else if(method==='Input.dispatchMouseEvent'&&params.type==='mousePressed'){
        document.activeElement=elements[0];
      }else if(method==='Input.dispatchKeyEvent'&&params.type==='keyDown'&&elements[0]?.stealFocus){document.activeElement=elements[1];
      }else if(method==='Input.insertText'){
        const e=document.activeElement;
        if(e.isContentEditable)e.textContent=mutate(params.text);else e.value=mutate(params.text);
      }
      queueMicrotask(()=>this.listeners.message({data:JSON.stringify({id,result})}));
    }
    close(){closed=true;}
  }
  const process={exitCode:0};
  await vm.runInNewContext('(async()=>{'+source.replace(/^import .*;$/gm,'')+'})()',{
    fs:{readFileSync:()=>JSON.stringify(request)},crypto:{randomUUID:()=> 'snapshot-test'},
    URL,WebSocket,process,AbortSignal,queueMicrotask,setTimeout,clearTimeout,
    fetch:async()=>({json:async()=>[{type:'page',id:'test',webSocketDebuggerUrl:debuggerUrl}]}),
    console:{log:s=>output.push(JSON.parse(s))}
  });
  assert.equal(closed,true);
  assert.equal(output.length,1);
  return {result:output[0],expressions,replies,page};
}

// `fill` can misroute across CDP key requests. It may falsely succeed when the
// observed target already contained the desired value; R1's set_value is bound
// to the original object and never sends focus-dependent keyboard commands.
let runResult;
for(const initial of ['', 'synthetic-payload']){
  const target=element('',{id:'field',tagName:'INPUT',value:initial});target.stealFocus=true;
  const decoy=element('',{id:'decoy',tagName:'INPUT',value:''});
  runResult=await run([target,decoy],[{type:'fill',ref:'e1',text:'synthetic-payload'}]);
  assert.equal(runResult.result.ok,Boolean(initial));
  assert.equal(decoy.value,'synthetic-payload');
  target.stealFocus=false;decoy.value='';
  runResult=await run([target,decoy],[{type:'set_value',ref:'e1',text:'synthetic-payload'}]);
  assert.equal(runResult.result.ok,true,JSON.stringify(runResult.result));
  assert.equal(target.value,'synthetic-payload');
  assert.equal(decoy.value,'');
  assert.equal(runResult.result.completed,1);
}

// set_value rejects non-fields and constraints before mutation; unchanged text
// does not fire synthetic notifications.
for(const field of [
  element('',{tagName:'INPUT',type:'password',value:''}),
  element('',{tagName:'INPUT',disabled:true,value:''}),
  element('',{tagName:'INPUT',readOnly:true,value:''}),
  element('',{tagName:'INPUT',inert:true,value:''}),
  element('',{tagName:'INPUT',type:'text',maxLength:2,value:''}),
  element('',{tagName:'INPUT',type:'text',visibility:'hidden',value:''}),
  element('',{tagName:'BUTTON',value:''}),
]){
  runResult=await run([field],[{type:'set_value',ref:'e1',text:'payload'}]);
  assert.equal(runResult.result.ok,false);
  assert.equal(runResult.result.completed,0);
  assert.equal(field.value??'', '');
}
const unchanged=element('',{tagName:'INPUT',value:'same'});
runResult=await run([unchanged],[{type:'set_value',ref:'e1',text:'same'}]);
assert.equal(runResult.result.ok,true);assert.deepEqual(unchanged.events??[],[]);
const rewritten=element('',{tagName:'TEXTAREA',value:'',onEvent:(_event,node)=>{node.value='rewritten';}});
runResult=await run([rewritten],[{type:'set_value',ref:'e1',text:'exact'}]);
assert.equal(runResult.result.ok,false);assert.equal(runResult.result.mutation_may_have_occurred,true);
assert.equal(JSON.stringify(runResult.result).includes('exact'),false);
runResult=await run([element('',{tagName:'INPUT',value:''})],[{type:'set_value',ref:'e1',selector:'#field',text:'x'}]);
assert.equal(runResult.result.ok,false);

// Visible targets win even when the DOM starts with eighty offscreen controls.
const outside=Array.from({length:80},(_,i)=>element('outside '+i,{top:100}));
const visible=element('visible target');
runResult=await run([...outside,visible]);
assert.equal(runResult.result.elements.length,80);
assert.equal(runResult.result.elements[0].name,'visible target');
assert.equal(runResult.result.elements[0].offscreen,undefined);
assert.equal(runResult.result.elements[1].offscreen,true);
assert.equal(runResult.result.truncated,true);
assert.equal(vm.runInContext("__agentCu.refs.get('e1')",runResult.page),visible);

// Both axes, exact boundaries, partial intersections, and hidden exclusions.
const edges=[element('right',{left:100}),element('left',{left:-20}),
  element('below',{top:100}),element('above',{top:-20}),
  element('partial',{left:-10,top:-10}),element('hidden',{visibility:'hidden'}),
  element('zero',{width:0}),element('hidden input',{tagName:'INPUT',type:'hidden'})];
runResult=await run(edges);
assert.deepEqual(runResult.result.elements.map(e=>e.name),['partial','right','left','below','above']);
assert.deepEqual(runResult.result.elements.map(e=>Boolean(e.offscreen)),[false,true,true,true,true]);
assert.equal(runResult.result.truncated,false);
assert.equal((await run(outside)).result.truncated,false);
assert.equal((await run([...outside,element('extra',{left:100})])).result.truncated,true);

// Values and editable innerText never become snapshot labels or values.
const fields=['INPUT','TEXTAREA','SELECT'].map(tagName=>element(token,{tagName,value:token,name:tagName}));
fields.push(element(token,{isContentEditable:true,name:'editable'}),
  element('',{tagName:'INPUT',type:'checkbox',value:token,checked:true}),
  element('',{tagName:'INPUT',type:'radio',value:token,checked:false}),
  element('',{tagName:'INPUT',type:'password',value:token}));
runResult=await run(fields);
assert.equal(JSON.stringify(runResult.result).includes(token),false);
assert.ok(runResult.result.elements.every(e=>e.value==='[redacted]'));
assert.equal(runResult.result.elements[4].checked,true);
assert.equal(runResult.result.elements[5].checked,false);

// Fill and assertions inspect real values internally, returning only booleans.
const payload='P'.repeat(10_000);
for(const editable of [false,true]){
  const field=element('',{id:'field',tagName:editable?'DIV':'INPUT',isContentEditable:editable,value:''});
  const target=editable?{ref:'e1'}:{selector:'#field'};
  runResult=await run([field],[{type:'fill',...target,text:payload},
    editable?{type:'assert',...target,text:payload}:{type:'assert',...target,value:payload}]);
  assert.equal(runResult.result.ok,true);
  assert.equal(runResult.result.completed,2);
  assert.equal(JSON.stringify(runResult.result).includes(payload),false);
  assert.equal(runResult.replies.some(value=>value===payload),false);
  const lookups=runResult.expressions.filter(expression=>expression.includes('const e=(function pageState'));
  assert.ok(lookups.length>=4);
  for(const expression of lookups){
    assert.equal(expression.split(payload).length-1,expression.includes('return (e.isContentEditable?')||expression.includes('return String(e.value)')||expression.includes('return e.textContent.includes')?1:0);
    assert.equal(expression.includes('"type":"fill"'),false);
    assert.equal(expression.includes('"text":'),false);
    assert.equal(expression.includes('"value":'),false);
  }
}
runResult=await run([element('',{id:'field',tagName:'INPUT',value:''})],
  [{type:'fill',selector:'#field',text:token}],{mutate:()=> 'rejected'});
assert.equal(runResult.result.ok,false);
assert.equal(runResult.result.completed,0);
assert.equal(runResult.result.error,'fill verification failed');
assert.equal(JSON.stringify(runResult.result).includes(token),false);
assert.ok(runResult.replies.includes(false));
runResult=await run([element('',{id:'field',tagName:'INPUT',value:token})],
  [{type:'assert',selector:'#field',value:'wrong',timeout_ms:0}]);
assert.equal(runResult.result.error,'assertion failed');
console.log('all cdp snapshot, redaction, fill and payload regressions pass');

const many=Array.from({length:80},(_,i)=>element('control '+i));
const full=await run(many);
const compact=await run(many,undefined,{maxElements:16});
assert.equal(compact.result.elements.length,16);
assert.equal(compact.result.truncated,true);
assert.ok(JSON.stringify(compact.result).length<JSON.stringify(full.result).length*.3);
for(const maxElements of [0,81,1.5,'16',true]){
  const field=element('',{tagName:'INPUT',value:'unchanged'});
  await assert.rejects(run([field],[{type:'fill',ref:'e1',text:'change'}],{maxElements}),/max_elements must be 1..80/);
  assert.equal(field.value,'unchanged');
}
console.log(JSON.stringify({fixture:'80 visible controls',full_bytes:JSON.stringify(full.result).length,
  compact_bytes:JSON.stringify(compact.result).length,compact_refs:16}));
for(const debuggerUrl of ['ws://outside.example/test','wss://outside.example/test','http://127.0.0.1/test'])
  await assert.rejects(run([],undefined,{debuggerUrl}),/debugger must be loopback WebSocket/);
