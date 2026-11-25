// G-44 pill live test drive over WebDriver BiDi (Zen, laptop).
// Procedure under test (manual central-overlay acquire, docs/overlay.md):
//   1. switch to Hyprland ws2
//   2. pre grim (pill must be absent)
//   3. overlay.py acquire --agent G44 --method BiDi --pid <own pid>
//      (fail closed: if visible is not true, NO drive happens)
//   4. BiDi session.new on ws://127.0.0.1:9222/session
//   5. getTree (read state), create ONE new about:blank tab, getTree,
//      grim DURING (pill must be visible), close the new tab
//   6. session.end, close WS, re-probe session.new + session.end to
//      prove the single session slot is free (no leak)
//   7. overlay.py release, post grim (pill must be gone), back to ws1
// Logs only counts, never tab titles or URLs (no personal info).
// Every step timestamped Asia/Ho_Chi_Minh. Runs detached on the laptop.
import { execFile } from 'node:child_process';
import fs from 'node:fs';

const OVERLAY = '/home/james/computer-use-wayland/scripts/overlay.py';
const BIDI = 'ws://127.0.0.1:9222/session';
const AGENT = 'G44';
const METHOD = 'BiDi';

const sig = fs.readdirSync('/run/user/1000/hypr')[0];
const ENV = { ...process.env,
  HYPRLAND_INSTANCE_SIGNATURE: sig,
  WAYLAND_DISPLAY: 'wayland-1',
  XDG_RUNTIME_DIR: '/run/user/1000' };

function stamp() {
  return new Date().toLocaleString('en-GB', { timeZone: 'Asia/Ho_Chi_Minh', hour12: false });
}
function log(...a) { console.log(`[${stamp()}]`, ...a); }
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function run(cmd, args, timeoutMs = 20000) {
  return new Promise((resolve) => {
    execFile(cmd, args, { env: ENV, timeout: timeoutMs }, (err, stdout, stderr) => {
      resolve({ code: err ? (err.code ?? 1) : 0, stdout: String(stdout || ''), stderr: String(stderr || '') });
    });
  });
}

async function overlay(args) {
  const r = await run('python3', [OVERLAY, ...args]);
  let json = null;
  try { json = JSON.parse(r.stdout.trim().split('\n').pop()); } catch { /* keep null */ }
  return { ...r, json };
}

// ---- BiDi minimal client ----
let nextId = 1;
const pending = new Map();
let ws = null;
function bidiSend(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = nextId++;
    const timer = setTimeout(() => { pending.delete(id); reject(new Error(`timeout ${method}`)); }, 15000);
    pending.set(id, { resolve, reject, timer, method });
    ws.send(JSON.stringify({ id, method, params }));
  });
}
function bidiConnect() {
  return new Promise((resolve, reject) => {
    const socket = new WebSocket(BIDI);
    const timer = setTimeout(() => reject(new Error('ws connect timeout')), 15000);
    socket.addEventListener('open', () => { clearTimeout(timer); ws = socket; resolve(); });
    socket.addEventListener('error', (e) => { clearTimeout(timer); reject(new Error('ws error ' + (e.message || 'unknown'))); });
    socket.addEventListener('message', (ev) => {
      let msg; try { msg = JSON.parse(ev.data); } catch { return; }
      if (msg.id && pending.has(msg.id)) {
        const p = pending.get(msg.id); pending.delete(msg.id); clearTimeout(p.timer);
        if (msg.type === 'success') p.resolve(msg.result);
        else p.reject(new Error(`${p.method} error: ${JSON.stringify(msg.error || msg)}`));
      }
    });
    socket.addEventListener('close', () => {
      for (const [, p] of pending) { clearTimeout(p.timer); p.reject(new Error('ws closed during ' + p.method)); }
      pending.clear();
    });
  });
}
async function treeCount() {
  const tree = await bidiSend('browsingContext.getTree', {});
  return Array.isArray(tree.contexts) ? tree.contexts.length : -1;
}

let pillHeld = false;
let newContext = null;
let sessionOpen = false;
try {
  log('START G-44 BiDi pill test, pid', process.pid);

  // 1. ws2
  const ws2 = await run('hyprctl', ['dispatch', 'hl.dsp.focus({ workspace = 2 })']);
  log('switch ws2 rc=', ws2.code, ws2.stdout.trim().slice(0, 200), ws2.stderr.trim().slice(0, 200));
  await sleep(1000);
  const active = await run('hyprctl', ['activeworkspace']);
  log('activeworkspace:', active.stdout.trim().replace(/\n/g, ' | ').slice(0, 200));

  // 2. pre grim
  const pre = await run('grim', ['/tmp/g44-pill-pre.png']);
  log('pre grim rc=', pre.code, 'bytes=', fs.existsSync('/tmp/g44-pill-pre.png') ? fs.statSync('/tmp/g44-pill-pre.png').size : -1);

  // 3. acquire pill (fail closed)
  const acq = await overlay(['acquire', '--agent', AGENT, '--method', METHOD, '--pid', String(process.pid)]);
  log('acquire rc=', acq.code, 'json=', JSON.stringify(acq.json), 'stderr=', acq.stderr.trim().slice(0, 300));
  if (acq.code !== 0 || !acq.json || acq.json.visible !== true) {
    throw new Error('PILL ACQUIRE FAILED, refusing to drive (fail closed)');
  }
  pillHeld = true;
  const st1 = await overlay(['status']);
  log('status after acquire:', JSON.stringify(st1.json));

  // 4. BiDi session
  await bidiConnect();
  log('BiDi ws open');
  const created = await bidiSend('session.new', { capabilities: {} });
  sessionOpen = true;
  log('session.new ok, sessionId present=', typeof created.sessionId === 'string');
  const before = await treeCount();
  log('contexts before create:', before);

  // 5. harmless drive: one new blank tab, read, grim during, close it
  const ctx = await bidiSend('browsingContext.create', { type: 'tab', url: 'about:blank' });
  newContext = ctx.context;
  log('created blank tab context=', newContext);
  const during = await treeCount();
  log('contexts after create:', during);
  const grim = await run('grim', ['/tmp/g44-pill-during.png']);
  log('during grim rc=', grim.code, 'bytes=', fs.existsSync('/tmp/g44-pill-during.png') ? fs.statSync('/tmp/g44-pill-during.png').size : -1);
  const st2 = await overlay(['status']);
  log('status during drive:', JSON.stringify(st2.json));
  await bidiSend('browsingContext.close', { context: newContext });
  log('closed blank tab');
  newContext = null;
  const after = await treeCount();
  log('contexts after close:', after, '(must equal before:', before, ')');

  // 6. end session, prove slot free with a fresh session
  await bidiSend('session.end', {});
  ws.close(); sessionOpen = false;
  log('session.end sent, ws closed');
  await sleep(1000);
  await bidiConnect();
  const reprobe = await bidiSend('session.new', { capabilities: {} });
  log('re-probe session.new ok, sessionId present=', typeof reprobe.sessionId === 'string');
  await bidiSend('session.end', {});
  ws.close();
  log('re-probe session ended, slot free, NO LEAK');
} catch (err) {
  log('ERROR:', err && err.message ? err.message : String(err));
  try {
    if (newContext && ws && ws.readyState === 1) { await bidiSend('browsingContext.close', { context: newContext }); log('cleanup: closed blank tab'); }
  } catch (e) { log('cleanup close tab failed:', e.message); }
  try {
    if (sessionOpen && ws && ws.readyState === 1) { await bidiSend('session.end', {}); log('cleanup: session.end'); }
  } catch (e) { log('cleanup session.end failed:', e.message); }
  try { if (ws) ws.close(); } catch { /* ignore */ }
} finally {
  if (pillHeld) {
    const rel = await overlay(['release', '--agent', AGENT, '--method', METHOD, '--pid', String(process.pid)]);
    log('release rc=', rel.code, 'json=', JSON.stringify(rel.json));
    const st3 = await overlay(['status']);
    log('status after release:', JSON.stringify(st3.json));
  }
  const post = await run('grim', ['/tmp/g44-pill-post.png']);
  log('post grim rc=', post.code, 'bytes=', fs.existsSync('/tmp/g44-pill-post.png') ? fs.statSync('/tmp/g44-pill-post.png').size : -1);
  const ws1 = await run('hyprctl', ['dispatch', 'hl.dsp.focus({ workspace = 1 })']);
  log('switch back ws1 rc=', ws1.code);
  log('END G-44');
}
