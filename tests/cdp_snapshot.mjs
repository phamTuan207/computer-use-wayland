// Run: node tests/cdp_snapshot.mjs. Production adapter + fake CDP/DOM; no network or GUI.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
const source=fs.readFileSync(new URL('../scripts/cdp.mjs',import.meta.url),'utf8');
const token='fake-api-token-NEVER-EXPOSE';
class FakeInput {get value(){return this._value??'';} set value(value){this._value=value;}}
class FakeTextarea {get value(){return this._value??'';} set value(value){this._value=value;}}
// The fake DOM needs enough selector support for scoped observe: which nodes are
// interactive, and which live inside a subtree.
const TAGS=/^(BUTTON|INPUT|TEXTAREA|SELECT|SUMMARY|A)$/;
const ROLES=/^(button|checkbox|tab|menuitem)$/;
function matchesSelector(node,selector){
  if(selector==='*')return true;
  if(selector==='iframe')return node.tagName==='IFRAME';
  if(selector===':disabled')return Boolean(node.disabled);
  if(/^[a-z]+$/i.test(selector))return node.tagName===selector.toUpperCase();
  return TAGS.test(node.tagName)||ROLES.test(node.attributes?.role)||node.isContentEditable===true;
}
function flatten(nodes){
  const all=[];
  for(const node of nodes){all.push(node);all.push(...descendants(node,'*'));}
  return all;
}
function descendants(node,selector){
  const found=[];
  for(const child of node.children??[]){
    if(matchesSelector(child,selector))found.push(child);
    found.push(...descendants(child,selector));
  }
  return found;
}
function element(name,options={}) {
  const {left=10,top=10,width=20,height=20,tagName='BUTTON',...rest}=options;
  const proto=tagName==='INPUT'?FakeInput.prototype:tagName==='TEXTAREA'?FakeTextarea.prototype:Object.prototype;
  const node=Object.assign(Object.create(proto),{tagName,innerText:name,textContent:name,isConnected:true,
    type:'text',disabled:false,readOnly:false,maxLength:-1,
    getAttribute:key=>key==='aria-disabled'?rest.ariaDisabled??null:rest.attributes?.[key]??null,
    closest:()=>rest.inert?node:null,children:rest.children??[],
    matches:selector=>selector===':disabled'?Boolean(rest.disabled):matchesSelector(node,selector),
    contains:other=>other===node,scrollIntoView(){},getClientRects:()=>[{}],
    dispatchEvent:event=>{(node.events??=[]).push({type:event.type,trusted:event.isTrusted});rest.onEvent?.(event,node);return true;},
    getBoundingClientRect:()=>({left,top,right:left+width,bottom:top+height,width,height}),...rest});
  return node;
}
async function run(elements,actions,{mutate=text=>text,maxElements,debuggerUrl='ws://127.0.0.1:9222/test',
  noAfter,operation,image,allowNoSocket=false,scope,afterScope,seed,followup}={}) {
  const expressions=[],replies=[],output=[],calls=[],measured=new Set();
  const document={title:'fixture',activeElement:null,
    querySelectorAll:selector=>{
      if(/[[]{2}|\]\]/.test(selector))throw new SyntaxError('not a valid selector');
      if(selector.startsWith('#'))return flatten(elements).filter(e=>e.id===selector.slice(1));
      return flatten(elements).filter(e=>matchesSelector(e,selector));},
    elementFromPoint:()=>elements[0]};
  const page=vm.createContext({document,location:{href:'http://fixture/'},innerWidth:100,innerHeight:100,
    HTMLInputElement:FakeInput,HTMLTextAreaElement:FakeTextarea,
    InputEvent:class {constructor(type,options){this.type=type;this.isTrusted=false;Object.assign(this,options);}},
    Event:class {constructor(type,options){this.type=type;this.isTrusted=false;Object.assign(this,options);}},
    getComputedStyle:e=>{measured.add(e);return {visibility:e.visibility??'visible',display:e.display??'block'};}});
  if(seed??Boolean(actions)){
    vm.runInContext("globalThis.__agentCu={id:'before',created:Date.now(),url:location.href,refs:new Map()}",page);
    vm.runInContext('__agentCu',page).refs.set('e1',elements[0]);
  }
  const request={operation:operation??(actions?'act':'observe'),endpoint:'http://127.0.0.1:9222',target:'test',snapshot:'before',actions,max_elements:maxElements};
  if(noAfter!==undefined)request.no_after=noAfter;
  if(image!==undefined)request.image=image;
  if(scope!==undefined)request.scope=scope;
  if(afterScope!==undefined)request.after_scope=afterScope;
  // A followup runs the adapter again against the SAME fake page, so a scoped
  // observe can be followed by a real act using the snapshot and refs it returned.
  const runs=followup?2:1;
  const queue=[request];
  const allNodes=flatten(elements);
  for(const node of allNodes){
    node.querySelectorAll=selector=>descendants(node,selector);
    const box=node.getBoundingClientRect.bind(node);
    node.getBoundingClientRect=()=>{measured.add(node);return box();};
  }
  let closed=false,fetches=0;
  const sandboxRead=()=>JSON.stringify(queue.shift()??request);
  class WebSocket {
    listeners={};
    addEventListener(name,fn){this.listeners[name]=fn;if(name==='open')queueMicrotask(fn);}
    send(raw){
      const {id,method,params}=JSON.parse(raw);let result={};
      calls.push({method,params});
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
  // The adapter reads single-shot stdin as a bounded stream, not one fs call.
  // A getter yields a fresh bounded stdin each run, mirroring one process per request.
  const process={exitCode:0,destroy(){},
                 get stdin(){return (async function*(){yield sandboxRead();})();}};
  const sandbox={fs:{readFileSync:()=>JSON.stringify(queue.shift()??request)},
    crypto:{randomUUID:()=> 'snapshot-test'},
    URL,WebSocket,process,AbortSignal,queueMicrotask,setTimeout,clearTimeout,
    fetch:async()=>{fetches++;return {json:async()=>[{type:'page',id:'test',webSocketDebuggerUrl:debuggerUrl}]};},
    console:{log:s=>output.push(JSON.parse(s))}};
  // One context, run once per queued request, so a followup sees the page state the
  // first request left behind.
  const context=vm.createContext(sandbox);
  const body='(async()=>{'+source.replace(/^import .*;$/gm,'')+'})()';
  for(let i=0;i<runs;i++){
    // A followup may be a function of the previous result, so a real act can use
    // the snapshot id and refs the scoped observe actually returned.
    if(i)queue.push({...request,...(typeof followup==='function'?followup(output[i-1]):followup)});
    await vm.runInContext(body,context);
  }
  // A preflight rejection can return before the endpoint fetch and the socket, so
  // the harness must tolerate a run that opened neither. Callers assert the fetch
  // count themselves, since some checks legitimately run after the tab list.
  assert.equal(closed,!allowNoSocket);
  assert.equal(output.length,runs);
  return {result:output[0],expressions,replies,page,fetches,calls,measured,outputs:output};
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
// no_after: the default keeps the after-snapshot, opt-in drops it only on success.
// snapshot() evaluates the big __agentCu={id:...} expression, so its presence in the
// evaluate log is direct evidence of whether a snapshot happened.
const SNAPSHOT_EXPRESSION=expression=>expression.includes('__agentCu={id:');
const okAct=[{type:'set_value',selector:'#field',text:'payload'},
  {type:'assert',selector:'#field',value:'payload'}];

for(const [label,options] of [['default',{}],['no_after false',{noAfter:false}]]){
  const field=element('',{id:'field',tagName:'INPUT',value:''});
  const result=await run([field],okAct,options);
  assert.equal(result.result.ok,true,label+': '+JSON.stringify(result.result));
  assert.equal(result.result.completed,2,label);
  assert.ok(result.expressions.some(SNAPSHOT_EXPRESSION),label+' must still take the after-snapshot');
  assert.equal(result.result.after_skipped,undefined,label);
  assert.ok(result.result.after?.elements,label+' must keep after');
}

// Each accepted terminal assert predicate, including empty value and checked false.
// The text case needs a textContent node: set_value writes .value on an input.
for(const [label,fixture,first,terminal] of [
  ['text',element('payload',{id:'field'}),{type:'click',selector:'#field'},{type:'assert',selector:'#field',text:'payload'}],
  ['value',element('',{id:'field',tagName:'INPUT',value:''}),{type:'set_value',selector:'#field',text:'payload'},{type:'assert',selector:'#field',value:'payload'}],
  ['empty value',element('',{id:'field',tagName:'INPUT',value:'payload'}),{type:'set_value',selector:'#field',text:''},{type:'assert',selector:'#field',value:''}],
  ['checked false',element('',{id:'field',tagName:'INPUT',type:'checkbox',value:'',checked:false}),{type:'click',selector:'#field'},{type:'assert',selector:'#field',checked:false}],
]){
  const result=await run([fixture],[first,terminal],{noAfter:true});
  assert.equal(result.result.ok,true,label+': '+JSON.stringify(result.result));
  assert.equal(result.result.completed,2,label);
  assert.equal(result.result.after_skipped,true,label);
  assert.equal(result.result.after,undefined,label+' must not carry after');
  assert.equal(result.expressions.some(SNAPSHOT_EXPRESSION),false,label+' must not snapshot');
  assert.equal(vm.runInContext('__agentCu.id',result.page),'before',label+' keeps the original snapshot identity');
}

// A failed act still takes the diagnostic after-snapshot and never claims it was skipped.
let failed=await run([element('',{id:'field',tagName:'INPUT',value:''})],
  [{type:'assert',selector:'#field',value:'never',timeout_ms:0}],{noAfter:true});
assert.equal(failed.result.ok,false);
assert.equal(failed.result.after_skipped,undefined);
assert.ok(failed.result.after??failed.result.after_unavailable,
  'a failed no_after act must still attempt the diagnostic after-snapshot');
assert.equal(vm.runInContext('__agentCu.id',failed.page),'snapshot-tes');

// Every rejection lands before the endpoint fetch, before the socket and before input.
for(const [label,options,actions,error] of [
  ['non-boolean no_after',{noAfter:'yes'},okAct,'no_after must be a boolean'],
  ['no_after on observe',{noAfter:true,operation:'observe'},okAct,'no_after requires act'],
  ['no_after with image',{noAfter:true,image:true},okAct,'no_after is incompatible with image'],
  ['empty actions',{noAfter:true},[],'no_after requires a final assert action'],
  ['terminal wait',{noAfter:true},[{type:'wait',ms:5}],'no_after requires the final action to be assert'],
  ['terminal click',{noAfter:true},[{type:'click',ref:'e1'}],'no_after requires the final action to be assert'],
  ['terminal fill',{noAfter:true},[{type:'fill',ref:'e1',text:'x'}],'no_after requires the final action to be assert'],
  ['size-only assert',{noAfter:true},[{type:'assert',ref:'e1'}],'no_after final assert needs text, value or checked'],
  ['empty text only',{noAfter:true},[{type:'assert',ref:'e1',text:''}],'no_after final assert needs text, value or checked'],
  // assertAction resolves value>text>checked and ignores the rest, so the ignored
  // checked:true must not rescue an empty effective text.
  ['ignored predicate',{noAfter:true},[{type:'assert',ref:'e1',text:'',checked:true}],'no_after final assert needs text, value or checked'],
  ['non-string value',{noAfter:true},[{type:'assert',ref:'e1',value:5}],'no_after final assert needs text, value or checked'],
]){
  const untouched=element('',{id:'field',tagName:'INPUT',value:'untouched'});
  const result=await run([untouched],actions,{...options,allowNoSocket:true});
  assert.equal(result.result.ok,false,label);
  assert.equal(result.result.error,error,label);
  assert.equal(result.fetches,0,label+' must reject before the endpoint fetch');
  assert.equal(result.expressions.length,0,label+' must not evaluate anything');
  assert.equal(untouched.value,'untouched',label+' must not mutate the DOM');
}

// The raw --worker entry frames the same rejection as stable JSON, completed 0.
// The worker stops on the first ok:false, so exit status 1 is expected, not a test failure.
function worker(request){
  const child=spawnSync('node',[fileURLToPath(new URL('../scripts/cdp.mjs',import.meta.url)),'--worker'],
    {input:JSON.stringify(request),encoding:'utf8'});
  return {status:child.status,lines:child.stdout.trim().split('\n').filter(Boolean).map(JSON.parse)};
}
const rawWorker=worker({operation:'act',endpoint:'http://127.0.0.1:9222',target:'test',
  snapshot:'before',no_after:true,actions:[{type:'assert',ref:'e1',text:'',checked:true}]});
assert.equal(rawWorker.status,1,'worker exits nonzero after an ok:false result');
assert.equal(rawWorker.lines.length,1,'the worker must not keep going after a rejection');
assert.deepEqual(rawWorker.lines[0],{ok:false,completed:0,error:'no_after final assert needs text, value or checked'});

const rawWorkerAccepted=worker({operation:'act',endpoint:'http://127.0.0.1:9222',target:'test',
  snapshot:'before',no_after:'yes',actions:[{type:'assert',ref:'e1',text:''}]});
assert.equal(rawWorkerAccepted.lines[0].error,'no_after must be a boolean');
const rawCold=spawnSync('node',[fileURLToPath(new URL('../scripts/cdp.mjs',import.meta.url))],
  {input:JSON.stringify({operation:'act',no_after:'yes'}),encoding:'utf8'});
assert.equal(rawCold.status,1);
assert.equal(rawCold.stderr,'');
assert.deepEqual(JSON.parse(rawCold.stdout),{ok:false,completed:0,error:'no_after must be a boolean'});
// Scoped observe: one read, never sticky, never an input boundary.
const taskPanel=element('panel',{id:'task',tagName:'DIV',attributes:{role:'region'}});
const nameField=element('name field',{id:'name',tagName:'INPUT',value:'secret-value'});
const saveButton=element('save',{id:'save',attributes:{role:'button'}});
taskPanel.children=[nameField,saveButton];
const strayButton=element('stray',{id:'stray'});
const strayField=element('stray field',{id:'strayfield',tagName:'INPUT',value:'other-secret'});
const pageFrames=[element('',{tagName:'IFRAME'}),element('',{tagName:'IFRAME'})];
for(const frame of pageFrames)frame.children=[element('',{tagName:'IFRAME'})];

const scoped=await run([taskPanel,strayButton,strayField],undefined,{scope:'#task'});
assert.equal(scoped.result.scoped,true);
assert.deepEqual(scoped.result.elements.map(e=>[e.ref,e.role]),[['e1','input'],['e2','button']]);
assert.equal(scoped.result.elements[0].value,'[redacted]','scoped field values stay redacted');
assert.ok(!JSON.stringify(scoped.result).includes('secret-value'),'raw value never returned');
assert.equal(scoped.result.title,'fixture');
assert.equal(scoped.result.url,'http://fixture/','page metadata is still global');
assert.equal(scoped.result.iframes,0,'iframes counted inside the scope only');
assert.ok(scoped.measured.has(nameField)&&scoped.measured.has(saveButton),
  'in-scope nodes must be measured');
assert.ok(!scoped.measured.has(strayButton)&&!scoped.measured.has(strayField),
  'outside nodes must never be measured');

// A root that is itself interactive is included exactly once, and refs map 1:1.
const rootButton=await run([element('root save',{id:'root'}),element('inner',{id:'inner'})],
  undefined,{scope:'#root'});
assert.deepEqual(rootButton.result.elements.map(e=>e.name),['root save']);
const withRootAndChild=element('root both',{id:'both',attributes:{role:'button'}});
const child=element('child only',{id:'child'});
withRootAndChild.children=[child];
const both=await run([withRootAndChild],undefined,{scope:'#both'});
assert.deepEqual(both.result.elements.map(e=>e.name),['root both','child only'],
  'interactive root included once, then its descendants');
assert.deepEqual(both.result.elements.map(e=>e.ref),['e1','e2'],'refs stay sequential');
assert.equal(vm.runInContext("__agentCu.refs.get('e1').innerText",both.page),'root both');

// An iframe root counts itself plus its own subtree.
const frameRoot=element('',{id:'fr',tagName:'IFRAME'});
frameRoot.children=[element('',{tagName:'IFRAME'}),element('inner',{id:'inframe'})];
const framed=await run([frameRoot,...pageFrames],undefined,{scope:'#fr'});
assert.equal(framed.result.iframes,2,'iframe root itself plus its subtree');

// Truncation and visible-first ordering survive scoping.
const scopedMany=Array.from({length:20},(_,i)=>element('c'+i,{id:'c'+i}));
const wide=element('wide',{id:'wide'});
wide.children=scopedMany;
const capped=await run([wide],undefined,{scope:'#wide',maxElements:4});
assert.equal(capped.result.elements.length,4);
assert.equal(capped.result.truncated,true);
const offscreen=[element('below',{id:'below',top:200}),element('visible',{id:'vis'})];
const box=element('box',{id:'box',tagName:'DIV'});
box.children=offscreen;
const ordered=await run([box],undefined,{scope:'#box'});
assert.deepEqual(ordered.result.elements.map(e=>e.name),['visible','below'],'visible first');
assert.equal(ordered.result.elements[1].offscreen,true);

// Bad scopes fail read-only, before the usable snapshot is replaced.
for(const [label,selector,message] of [
  ['zero matches','#nothing','scope selector matched no element'],
  ['multiple','div','scope selector must match exactly one element'],
  ['invalid CSS','#a[[','scope selector is not valid CSS'],
]){
  const secondPanel=element('panel two',{id:'task2',tagName:'DIV'});
  const reused=await run([taskPanel,secondPanel,strayButton],undefined,
    {scope:selector,operation:'observe',seed:true});
  assert.equal(reused.result.ok,false,label);
  assert.ok(reused.result.error.startsWith(message),label+': '+reused.result.error);
  assert.equal(vm.runInContext('__agentCu.id',reused.page),'before',label+' must keep the old snapshot id');
  assert.equal(vm.runInContext("__agentCu.refs.get('e1').innerText",reused.page),'panel',
    label+' must keep old refs usable');
  assert.equal(reused.result.scoped,undefined,label+' returns no scope field');
}

// A selector is a JSON string literal, never evaluated as code.
const injected=await run([taskPanel],undefined,{scope:'#task\").constructor.name&&1||1,globalThis.__pwned=1,#task'});
assert.ok(injected.result.error.includes('scope selector'),'injected selector is not executed');
assert.equal(vm.runInContext('globalThis.__pwned',injected.page),undefined);

// Scope is not sticky: a real scoped observe is followed by a real act in the SAME
// fake page, using the snapshot id and ref the observe actually returned.
// Whole page = every interactive node in the tree: the two inside #task plus the
// two outside it. The DIV container is not interactive and must not appear.
const wholePageNames=['','','save','stray'];
const scopedThenAct=await run([taskPanel,strayButton,strayField],undefined,
  {operation:'observe',scope:'#task',
   followup:observed=>({operation:'act',scope:undefined,snapshot:observed.snapshot,
     actions:[{type:'assert',ref:observed.elements[1].ref,text:'save'}]})});
const [observed,acted]=scopedThenAct.outputs;
assert.equal(observed.scoped,true);
assert.deepEqual(observed.elements.map(e=>e.ref),['e1','e2'],'scoped observe refs');
assert.equal(acted.ok,true,JSON.stringify(acted));
assert.equal(acted.after.scoped,undefined,'the act result carries no scope field');
assert.deepEqual(acted.after.elements.map(e=>e.name).sort(),wholePageNames,
  'the after-snapshot is whole page again, not the earlier scope');
assert.equal(acted.after.elements.length,4,'four interactive nodes, container excluded');
assert.equal(observed.snapshot,'snapshot-tes','the act used the snapshot the observe returned');

// An explicit after-scope keeps the next refs within the same task panel.
const scopedAfter=await run([taskPanel,strayButton,strayField],undefined,
  {operation:'observe',scope:'#task',
   followup:observed=>({operation:'act',scope:undefined,after_scope:'#task',
     snapshot:observed.snapshot,
     actions:[{type:'assert',ref:observed.elements[1].ref,text:'save'}]})});
const next=scopedAfter.outputs[1];
assert.equal(next.ok,true,JSON.stringify(next));
assert.equal(next.after.scoped,true);
assert.deepEqual(next.after.elements.map(e=>e.ref),['e1','e2']);
assert.ok(!next.after.elements.some(e=>e.name==='stray'));
assert.equal(vm.runInContext("__agentCu.refs.get('e2').innerText",scopedAfter.page),'save');

// The same flow with a failing act: the diagnostic after-snapshot is also whole page.
const scopedThenFail=await run([taskPanel,strayButton,strayField],undefined,
  {operation:'observe',scope:'#task',
   followup:observed=>({operation:'act',scope:undefined,snapshot:observed.snapshot,
     actions:[{type:'assert',ref:observed.elements[0].ref,text:'never',timeout_ms:0}]})});
const [observedFail,failedAct]=scopedThenFail.outputs;
assert.equal(failedAct.ok,false);
assert.equal(failedAct.after.scoped,undefined);
assert.deepEqual(failedAct.after.elements.map(e=>e.name).sort(),wholePageNames,
  'a failed act still reports a whole-page diagnostic snapshot');
assert.equal(observedFail.scoped,true);

const scopedAfterFail=await run([taskPanel,strayButton,strayField],undefined,
  {operation:'observe',scope:'#task',
   followup:observed=>({operation:'act',scope:undefined,after_scope:'#task',
     snapshot:observed.snapshot,
     actions:[{type:'assert',ref:observed.elements[0].ref,text:'never',timeout_ms:0}]})});
assert.equal(scopedAfterFail.outputs[1].ok,false);
assert.equal(scopedAfterFail.outputs[1].after.scoped,undefined,
  'a failed act retains a whole-page diagnostic');
assert.equal(scopedAfterFail.outputs[1].after.elements.length,4);

for(const [label,afterScope,noAfter,error] of [
  ['null',null,undefined,'after_scope must be a non-empty CSS selector'],
  ['array',['#task'],undefined,'after_scope must be a non-empty CSS selector'],
  ['number',7,undefined,'after_scope must be a non-empty CSS selector'],
  ['empty','',undefined,'after_scope must be a non-empty CSS selector'],
  ['oversize','x'.repeat(1025),undefined,'after_scope must be at most 1024 characters'],
  ['conflict','#task',true,'after_scope is incompatible with no_after'],
]){
  const rejected=await run([taskPanel],[{type:'assert',ref:'e1',text:'panel'}],
    {operation:'act',afterScope,noAfter,allowNoSocket:true});
  assert.equal(rejected.result.error,error,label);
  assert.equal(rejected.fetches,0,label+' must reject before network');
}
for(const operation of ['observe','tabs']){
  const rejected=await run([taskPanel],undefined,
    {operation,afterScope:'#task',allowNoSocket:true});
  assert.equal(rejected.result.error,'after_scope is only valid for act');
  assert.equal(rejected.fetches,0);
}
for(const selector of ['#missing','div','#bad[[']){
  const secondPanel=element('second',{tagName:'DIV'});
  const unavailable=await run([taskPanel,secondPanel],
    [{type:'assert',ref:'e1',text:'panel'}],{afterScope:selector});
  assert.equal(unavailable.result.ok,true);
  assert.equal(unavailable.result.completed,1);
  assert.equal(unavailable.result.after_unavailable,true);
  assert.equal(unavailable.result.after,undefined);
}

// --image still captures the full viewport.
const shot=await run([taskPanel],undefined,{scope:'#task',image:true});
const capture=shot.calls.find(c=>c.method==='Page.captureScreenshot');
assert.ok(capture,'screenshot requested');
assert.equal(capture.params.captureBeyondViewport,false);
assert.equal(capture.params.clip,undefined,'scoped observe must not crop the screenshot');

// Raw scope values are rejected before the endpoint fetch, on both entries.
for(const [label,value,message] of [
  ['null',null,'scope must be a non-empty CSS selector'],
  ['boolean',true,'scope must be a non-empty CSS selector'],
  ['number',7,'scope must be a non-empty CSS selector'],
  ['empty','','scope must be a non-empty CSS selector'],
  ['whitespace','   ','scope must be a non-empty CSS selector'],
]){
  const rejected=await run([taskPanel],undefined,{scope:value,allowNoSocket:true});
  assert.equal(rejected.result.ok,false,label);
  assert.equal(rejected.result.error,message,label);
  assert.equal(rejected.fetches,0,label+' must reject before fetch');
}
const wrongOperation=await run([taskPanel],undefined,{scope:'#task',operation:'tabs',allowNoSocket:true});
assert.equal(wrongOperation.result.error,'scope is only valid for observe');
assert.equal(wrongOperation.fetches,0);
for(const operation of ['start','act']){
  const refused=await run([taskPanel],undefined,{scope:'#task',operation,allowNoSocket:true});
  assert.equal(refused.result.error,'scope is only valid for observe',operation);
  assert.equal(refused.fetches,0,operation+' must reject before fetch');
}
const arrayScope=await run([taskPanel],undefined,{scope:['#task'],allowNoSocket:true});
assert.equal(arrayScope.result.error,'scope must be a non-empty CSS selector');
assert.equal(arrayScope.fetches,0);
// The adapter counts UTF-16 code units, so non-BMP selectors reach the limit at half
// the code-point count. 1024 units is accepted, 1026 is not.
for(const [label,selector,accepted] of [
  ['1024 units', 'x'.repeat(1024), true],
  ['1025 units', 'x'.repeat(1025), false],
  ['512 emoji = 1024 units', '\u{1F431}'.repeat(512), true],
  ['513 emoji = 1026 units', '\u{1F431}'.repeat(513), false],
]){
  const sized=await run([taskPanel],undefined,{scope:selector,operation:'observe',
    allowNoSocket:!accepted});
  if(accepted)assert.ok(!/1024/.test(sized.result.error??''),
    label+' must pass the length check, got: '+sized.result.error);
  else{assert.equal(sized.result.error,'scope must be at most 1024 characters',label);
    assert.equal(sized.fetches,0,label+' must reject before fetch');}
}
const scopeWorker=spawnSync('node',[fileURLToPath(new URL('../scripts/cdp.mjs',import.meta.url)),'--worker'],
  {input:JSON.stringify({operation:'observe',endpoint:'http://127.0.0.1:9222',target:'test',scope:null}),
   encoding:'utf8'});
assert.deepEqual(JSON.parse(scopeWorker.stdout.trim()).error,'scope must be a non-empty CSS selector');
console.log('all cdp snapshot, redaction, fill, payload, no_after and scope regressions pass');

const many=Array.from({length:80},(_,i)=>element('control '+i));
const full=await run(many);
const compact=await run(many,undefined,{maxElements:16});
assert.equal(compact.result.elements.length,16);
assert.equal(compact.result.truncated,true);
assert.ok(JSON.stringify(compact.result).length<JSON.stringify(full.result).length*.3);
// Setup and input preflight failures use the same framed error contract.
for(const maxElements of [0,81,1.5,'16',true]){
  const field=element('',{tagName:'INPUT',value:'unchanged'});
  const rejected=await run([field],[{type:'fill',ref:'e1',text:'change'}],{maxElements,allowNoSocket:true});
  assert.equal(rejected.result.ok,false,String(maxElements));
  assert.equal(rejected.result.error,'max_elements must be 1..80',String(maxElements));
  assert.equal(rejected.fetches,0,String(maxElements)+' must reject before the fetch');
  assert.equal(field.value,'unchanged',String(maxElements));
}
console.log(JSON.stringify({fixture:'80 visible controls',full_bytes:JSON.stringify(full.result).length,
  compact_bytes:JSON.stringify(compact.result).length,compact_refs:16}));
for(const debuggerUrl of ['ws://outside.example/test','wss://outside.example/test','http://127.0.0.1/test']){
  // tabs are fetched before the debugger URL is checked, so only the socket is skipped
  const rejected=await run([],undefined,{debuggerUrl,allowNoSocket:true});
  assert.equal(rejected.result.ok,false,debuggerUrl);
  assert.equal(rejected.result.error,'CDP debugger must be loopback WebSocket',debuggerUrl);
  assert.equal(rejected.fetches,1,debuggerUrl);
}
