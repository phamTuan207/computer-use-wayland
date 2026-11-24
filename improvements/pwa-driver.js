// pwa-driver.js - CDP driver for the Muse / mimeo PWA. Runs ON the laptop via SSH.
// No dependencies: uses Node's global WebSocket (Node 22+) and fetch.
// Usage: node pwa-driver.js <port> <title-substring> <action> [action-args...]
// Prints one JSON object to stdout. Exit 0 on ok, 1 on failure.
// Actions: send, read, status, list, search, attach, unattach, newchat, back,
//          call, endcall, reply, react, stop, panel, raw
// This file is shipped to the laptop by pwa-send.py (cat > /tmp/pwa-driver.js).

const port = process.argv[2];
const titleMatch = process.argv[3];
const action = process.argv[4];
const args = process.argv.slice(5);
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

async function main() {
  const out = { ok: false, action };
  try {
    const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
    const page = list.find(t => t.type === 'page' && t.title.includes(titleMatch));
    if (!page) { out.error = 'NO PAGE for title ' + titleMatch; console.log(JSON.stringify(out)); process.exit(1); }
    out.target = page.title;
    const ws = new WebSocket(page.webSocketDebuggerUrl);
    let id = 0; const pending = new Map();
    const send = (method, params = {}) => new Promise((res) => {
      const mid = ++id; pending.set(mid, res);
      ws.send(JSON.stringify({ id: mid, method, params }));
    });
    ws.onmessage = (ev) => {
      const m = JSON.parse(ev.data);
      if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
    };
    await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; setTimeout(() => rej(new Error('ws timeout')), 8000); });
    await send('Runtime.enable');
    const ev = async (expr) => {
      const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
      if (r.result && r.result.exceptionDetails) throw new Error('JS EXC: ' + JSON.stringify(r.result.exceptionDetails).slice(0, 300));
      return r.result && r.result.result ? r.result.result.value : undefined;
    };
    const esc = async () => {
      for (const t of ['keyDown', 'keyUp'])
        await send('Input.dispatchKeyEvent', { type: t, key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27, nativeVirtualKeyCode: 27 });
      await sleep(500);
    };
    const clickBtn = async (matchFn) => ev(`(function(){
      const b=[...document.querySelectorAll('button')].find(${matchFn});
      if(!b) return 'NO BTN';
      b.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}));
      return 'CLICKED';
    })()`);
    const composerText = async () => ev(`(function(){
      const ta=document.querySelector('textarea[placeholder="Message"]');
      if(!ta) return null;
      let root=ta; for(let i=0;i<7 && root.parentElement;i++) root=root.parentElement;
      return root.innerText.replace(/\\n/g,' | ').slice(0,300);
    })()`);

    if (action === 'send') {
      const message = args.join(' ');
      await ev(`(function(){const t=document.querySelector('textarea[placeholder="Message"]'); if(!t) throw new Error('NO TEXTAREA'); t.focus(); return document.activeElement===t;})()`);
      await send('Input.insertText', { text: message });
      await sleep(400);
      const before = await ev(`document.querySelector('textarea[placeholder="Message"]').value`);
      if (before !== message) { out.error = 'insertText mismatch: ' + JSON.stringify(before); }
      else {
        for (const t of ['keyDown', 'keyUp'])
          await send('Input.dispatchKeyEvent', { type: t, key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 13 });
        await sleep(1500);
        out.sent = await ev(`document.body.innerText.includes(${JSON.stringify(message)})`);
        out.textareaCleared = (await ev(`document.querySelector('textarea[placeholder="Message"]').value`)) === '';
        out.ok = out.sent === true && out.textareaCleared === true;
      }
    } else if (action === 'read') {
      const n = parseInt(args[0] || '5', 10);
      out.messages = await ev(`[...document.querySelectorAll('[data-message-id]')].slice(-${n}).map(e=>{
        const mid=e.getAttribute('data-message-id');
        const sender = mid.startsWith('assistant-msg') ? 'agent' : (mid.startsWith('presentation-carrier') ? 'system' : 'owner');
        return {sender, mid: mid.slice(0,24), text: (e.innerText||'').replace(/\\n/g,' | ').slice(0,300)};
      })`);
      out.ok = Array.isArray(out.messages);
    } else if (action === 'status') {
      out.status = await ev(`(function(){
        const nameEl=[...document.querySelectorAll('*')].find(e=>e.children.length===0 && e.textContent.trim()==='${titleMatch}');
        if(!nameEl) return null;
        let box=nameEl; for(let i=0;i<5 && box.parentElement;i++) box=box.parentElement;
        return box.innerText.replace(/\\n/g,' | ').slice(0,200);
      })()`);
      out.ok = out.status !== null;
    } else if (action === 'list') {
      // Open the side-chats nav (hamburger), read its entries, close with Escape.
      const clicked = await clickBtn(`e=>/Open chat and side chats/i.test((e.getAttribute('aria-label')||'')+' '+(e.getAttribute('title')||'')+' '+(e.textContent||''))`);
      if (clicked !== 'CLICKED') { out.error = 'no hamburger: ' + clicked; }
      else {
        await sleep(900);
        out.items = await ev(`(function(){
          const nav=document.querySelector('nav[aria-label="Side chats"]');
          if(!nav) return null;
          return nav.innerText.split('\\n').map(s=>s.trim()).filter(s=>s.length>0);
        })()`);
        out.ok = Array.isArray(out.items);
        await esc();
      }
    } else if (action === 'search') {
      const query = args.join(' ');
      const clicked = await clickBtn(`e=>e.getAttribute('aria-label')==='Search'`);
      if (clicked !== 'CLICKED') { out.error = 'no Search button: ' + clicked; }
      else {
        await sleep(1000);
        const focused = await ev(`(function(){const i=[...document.querySelectorAll('input')].find(e=>/search/i.test((e.placeholder||'')+' '+(e.getAttribute('aria-label')||''))); if(!i) return 'NO INPUT'; i.focus(); return 'FOCUSED';})()`);
        if (focused !== 'FOCUSED') { out.error = focused; }
        else {
          await send('Input.insertText', { text: query });
          await sleep(1500);
          out.results = await ev(`[...document.querySelectorAll('[role=dialog]')].map(e=>(e.innerText||'').replace(/\\n/g,' | ').slice(0,400))`);
          out.ok = true;
        }
        await esc();
      }
    } else if (action === 'attach') {
      const file = args[0];
      await send('DOM.enable');
      const doc = await send('DOM.getDocument', { depth: -1, pierce: true });
      const q = await send('DOM.querySelector', { nodeId: doc.result.root.nodeId, selector: 'input[type=file]' });
      if (!q.result || !q.result.nodeId) { out.error = 'no file input'; }
      else {
        await send('DOM.setFileInputFiles', { nodeId: q.result.nodeId, files: [file] });
        await sleep(1500);
        out.composer = await composerText();
        out.ok = out.composer !== null && out.composer !== 'Message';
      }
    } else if (action === 'unattach') {
      const r = await ev(`(function(){
        const ta=document.querySelector('textarea[placeholder="Message"]');
        let root=ta; for(let i=0;i<6 && root.parentElement;i++) root=root.parentElement;
        const b=[...root.querySelectorAll('button')].find(e=>/remove attachment/i.test(e.getAttribute('aria-label')||''));
        if(!b) return 'NO REMOVE BTN';
        b.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}));
        return 'CLICKED';
      })()`);
      await sleep(800);
      out.composer = await composerText();
      out.ok = r === 'CLICKED';
    } else if (action === 'newchat') {
      // hamburger -> nav -> + icon (index 2) opens a new side chat
      await clickBtn(`e=>/Open chat and side chats/i.test((e.getAttribute('aria-label')||'')+' '+(e.getAttribute('title')||'')+' '+(e.textContent||''))`);
      await sleep(900);
      const r = await ev(`(function(){
        const nav=document.querySelector('nav[aria-label="Side chats"]');
        if(!nav) return 'NO NAV';
        const b=[...nav.querySelectorAll('button')][2];
        if(!b) return 'NO BTN 2';
        b.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}));
        return 'CLICKED';
      })()`);
      await sleep(1200);
      out.header = await ev(`document.body.innerText.slice(0,120).replace(/\\n/g,' | ')`);
      out.ok = r === 'CLICKED' && /New side chat/.test(out.header || '');
    } else if (action === 'back') {
      const r = await clickBtn(`e=>/Back to main chat/i.test((e.getAttribute('aria-label')||'')+' '+(e.textContent||''))`);
      await sleep(1200);
      out.ok = r === 'CLICKED';
      out.hasMainChat = await ev(`document.body.innerText.includes('Open chat and side chats')`);
    } else if (action === 'call') {
      const holdMs = parseInt(args[0] || '2000', 10);
      const r = await clickBtn(`e=>e.getAttribute('aria-label')==='Call'`);
      await sleep(2000);
      out.controls = await ev(`[...document.querySelectorAll('button')].map(e=>e.getAttribute('aria-label')||'').filter(a=>/End call|Cancel call|Mute call/i.test(a))`);
      out.ok = r === 'CLICKED' && out.controls.length > 0;
      if (out.ok) {
        await sleep(holdMs);
        await clickBtn(`e=>e.getAttribute('aria-label')==='End call'`);
        await sleep(1200);
        out.ended = await ev(`![...document.querySelectorAll('button')].some(e=>e.getAttribute('aria-label')==='End call')`);
      }
    } else if (action === 'endcall') {
      const r = await clickBtn(`e=>e.getAttribute('aria-label')==='End call'`);
      await sleep(1000);
      out.ok = r === 'CLICKED';
      out.stillInCall = await ev(`[...document.querySelectorAll('button')].some(e=>e.getAttribute('aria-label')==='End call')`);
    } else if (action === 'reply') {
      const sendIt = args[0] === '--send';
      const text = sendIt ? args.slice(1).join(' ') : args.join(' ');
      const mid = await ev(`(function(){const m=[...document.querySelectorAll('[data-message-id^="assistant-msg-"]')].pop(); return m? m.getAttribute('data-message-id') : null;})()`);
      if (!mid) { out.error = 'no agent message visible'; }
      else {
        out.mid = mid.slice(0, 24);
        await ev(`(function(){const m=document.querySelector('[data-message-id="${mid}"]'); const b=[...m.querySelectorAll('button')].find(e=>e.getAttribute('aria-label')==='More options'); if(!b) return 'NO BTN'; b.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true})); return 'CLICKED';})()`);
        await sleep(900);
        const r = await clickBtn(`e=>((e.getAttribute('aria-label')||'')+' '+(e.textContent||'').trim()).trim()==='Reply'`);
        await sleep(1000);
        out.composer = await composerText();
        out.ok = r === 'CLICKED' && /Replying to/.test(out.composer || '');
        if (out.ok && sendIt && text) {
          await ev(`document.querySelector('textarea[placeholder="Message"]').focus()`);
          await send('Input.insertText', { text });
          await sleep(400);
          for (const t of ['keyDown', 'keyUp'])
            await send('Input.dispatchKeyEvent', { type: t, key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 13 });
          await sleep(1500);
          out.sent = await ev(`document.body.innerText.includes(${JSON.stringify(text)})`);
        } else {
          await esc();
          out.cancelled = true;
        }
      }
    } else if (action === 'react') {
      const emoji = args[0] || '👍';
      const mid = await ev(`(function(){const m=[...document.querySelectorAll('[data-message-id^="assistant-msg-"]')].pop(); return m? m.getAttribute('data-message-id') : null;})()`);
      if (!mid) { out.error = 'no agent message visible'; }
      else {
        await ev(`(function(){const m=document.querySelector('[data-message-id="${mid}"]'); const b=[...m.querySelectorAll('button')].find(e=>e.getAttribute('aria-label')==='More options'); if(b) b.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true})); return 'ok';})()`);
        await sleep(900);
        const r = await clickBtn(`e=>((e.getAttribute('aria-label')||'')+' '+(e.textContent||'').trim()).trim()==='React'`);
        await sleep(1500);
        const picked = await ev(`(function(){
          const b=[...document.querySelectorAll('button')].find(e=>((e.getAttribute('aria-label')||e.textContent||'').trim()==='${emoji}'));
          if(!b) return 'NO EMOJI BTN';
          b.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}));
          return 'CLICKED';
        })()`);
        await sleep(1000);
        out.menu = r;
        out.picked = picked;
        out.hasReaction = await ev(`(function(){const m=document.querySelector('[data-message-id="${mid}"]'); return m? m.innerText.includes('${emoji}') : false;})()`);
        out.ok = out.hasReaction === true;
        await esc();
      }
    } else if (action === 'stop') {
      const force = args[0] === '--force';
      out.stopPresent = await ev(`(function(){
        const ta=document.querySelector('textarea[placeholder="Message"]');
        if(!ta) return false;
        let root=ta; for(let i=0;i<7 && root.parentElement;i++) root=root.parentElement;
        return [...root.querySelectorAll('button')].some(e=>e.getAttribute('aria-label')==='Stop');
      })()`);
      if (!out.stopPresent) { out.error = 'no Stop button (agent idle)'; }
      else if (!force) { out.error = 'REFUSED: Stop would kill the agent current generation. Re-run with --force.'; }
      else {
        await clickBtn(`e=>e.getAttribute('aria-label')==='Stop'`);
        await sleep(1000);
        out.ok = true;
        out.stopped = true;
      }
    } else if (action === 'panel') {
      const name = args[0] || '';
      const before = await ev(`(function(){const t=document.body.innerText; let h=0; for(let i=0;i<t.length;i++) h=(h*31+t.charCodeAt(i))>>>0; return h;})()`);
      // Match by aria-label OR by text content (the Chats nav button has no aria-label).
      const r = await clickBtn(`e=>{const n='${name[0].toUpperCase() + name.slice(1)}'; return (e.getAttribute('aria-label')||'')===n || (e.textContent||'').trim().startsWith(n);}`);
      await sleep(1100);
      const after = await ev(`(function(){const t=document.body.innerText; let h=0; for(let i=0;i<t.length;i++) h=(h*31+t.charCodeAt(i))>>>0; return h;})()`);
      out.clicked = r;
      out.viewChanged = before !== after;
      out.ok = r === 'CLICKED' && out.viewChanged;
      await esc();
    } else if (action === 'raw') {
      out.value = await ev(args.join(' '));
      out.ok = true;
    } else {
      out.error = 'unknown action: ' + action;
    }
    ws.close();
    console.log(JSON.stringify(out));
    process.exit(out.ok ? 0 : 1);
  } catch (e) {
    out.error = String(e).slice(0, 500);
    console.log(JSON.stringify(out));
    process.exit(1);
  }
}
main();
