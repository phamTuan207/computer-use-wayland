// Regression test for the CDP keyboard path.
//
// scripts/cdp.mjs used to set params.text only when there were no modifiers at
// all, so Shift+letter and Ctrl+letter reached Chromium as a bare key event with
// no character attached: the shortcut fired in the page's JS but nothing was
// typed. This asserts the exact params each chord produces.
//
// Run: node tests/cdp_keys.mjs
// No dependencies, no browser, no network.

const mods={alt:1,ctrl:2,meta:4,super:4,shift:8};
const special={Enter:13,Tab:9,Escape:27,BackSpace:8,Backspace:8,Delete:46,
               ArrowLeft:37,ArrowUp:38,ArrowRight:39,ArrowDown:40,
               Home:36,End:35,PageUp:33,PageDown:34,space:32,' ':32};

// Kept in sync with cdp.mjs keydown(); if you change one, change both.
//
// Shift+<key> has to carry the shifted character. toUpperCase() is not enough:
// it maps '1' to '1', while the US layout expects '!' there.
const shifted={'1':'!','2':'@','3':'#','4':'$','5':'%','6':'^','7':'&','8':'*','9':'(','0':')',
               '[':'{',']':'}','\\':'|',';':':',"'":'"',',':'<','.':'>','/':'?','-':'_','=':'+','`':'~'};

function keydown(keys) {
  let modifiers=0;const regular=[];
  for(const k of keys){if(k.toLowerCase() in mods)modifiers|=mods[k.toLowerCase()];else regular.push(k);}
  const out=[];
  for(const k of regular){
    const code=special[k]??(k.length===1?k.toUpperCase().charCodeAt(0):null);
    if(code===null)throw new Error('unsupported key '+k);
    const key=k==='BackSpace'?'Backspace':k==='space'?' ':k;
    const params={key,modifiers,windowsVirtualKeyCode:code,nativeVirtualKeyCode:code};
    const ctrl=modifiers&2,alt=modifiers&1,meta=modifiers&4;
    if(key.length===1&&!modifiers)params.text=key;
    else if(key.length===1&&(modifiers&8)&&!ctrl&&!alt&&!meta)params.text=shifted[key]??key.toUpperCase();
    if(key==='Enter'&&!modifiers)params.text='\r';
    out.push(params);
  }
  return out;
}

let failed=0;
function check(name,got,want){
  const a=JSON.stringify(got),b=JSON.stringify(want);
  if(a===b){console.log('  ok   '+name);}
  else{failed++;console.log('  FAIL '+name+'\n       got  '+a+'\n       want '+b);}
}

console.log('cdp keyboard: text field per chord');

// A bare letter types itself.
check('plain a',keydown(['a']),[{key:'a',modifiers:0,windowsVirtualKeyCode:65,nativeVirtualKeyCode:65,text:'a'}]);

// Shift+letter must carry the shifted character, not nothing. This is the
// regression: params.text used to be absent whenever any modifier was present.
check('Shift+a',keydown(['Shift','a']),[{key:'a',modifiers:8,windowsVirtualKeyCode:65,nativeVirtualKeyCode:65,text:'A'}]);
check('Shift+1',keydown(['Shift','1']),[{key:'1',modifiers:8,windowsVirtualKeyCode:49,nativeVirtualKeyCode:49,text:'!'}]);
check('shift+enter is not text',keydown(['Shift','Enter']),[{key:'Enter',modifiers:8,windowsVirtualKeyCode:13,nativeVirtualKeyCode:13}]);

// Shortcut chords intentionally carry no text: Ctrl+C is a command, not a
// character to insert.
check('Ctrl+a',keydown(['Ctrl','a']),[{key:'a',modifiers:2,windowsVirtualKeyCode:65,nativeVirtualKeyCode:65}]);
check('Ctrl+Shift+a',keydown(['Ctrl','Shift','a']),[{key:'a',modifiers:10,windowsVirtualKeyCode:65,nativeVirtualKeyCode:65}]);
check('Alt+a',keydown(['Alt','a']),[{key:'a',modifiers:1,windowsVirtualKeyCode:65,nativeVirtualKeyCode:65}]);

// Enter types a newline only unmodified.
check('Enter',keydown(['Enter']),[{key:'Enter',modifiers:0,windowsVirtualKeyCode:13,nativeVirtualKeyCode:13,text:'\r'}]);
check('Ctrl+Enter',keydown(['Ctrl','Enter']),[{key:'Enter',modifiers:2,windowsVirtualKeyCode:13,nativeVirtualKeyCode:13}]);

// Multiple keys in one action keep their order.
check('two letters',keydown(['a','b']).map(p=>p.text),['a','b']);

if(failed){console.log('\n'+failed+' FAILED');process.exit(1);}
console.log('\nall cdp keyboard cases pass');