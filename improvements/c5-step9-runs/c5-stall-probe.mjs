// C5-STEP9 stall probe: bare Input.dispatchMouseEvent on the live
// clone2 tab, with a Runtime.evaluate baseline and a key-event
// control in the same session. Modes:
//   reproduce: baseline + key + mouseMoved, as found.
//   activate: Target.activateTarget + Page.bringToFront in the SAME
//     session immediately before mouseMoved (the (a1) activation had
//     an SSH gap; this variant closes it).
//   scratch: fresh scratch tab in the same window, mouseMoved on it
//     (control: per-tab wedge vs per-window visibility).
// Usage: node c5-stall-probe.mjs <endpoint> <targetId> <mode>
// Prints one JSON line. No click, no key sent to the page except the
// key-event control (Shift, harmless); mouseMoved only hovers.
const endpoint = process.argv[2];
const targetId = process.argv[3];
const mode = process.argv[4] || 'reproduce';
const started = Date.now();
const out = {mode, endpoint, target: targetId, steps: {}};

function timedCall(ws, pending, method, params, timeoutMs) {
  return new Promise((resolve) => {
    const id = ++timedCall.seq;
    const timer = setTimeout(() => {
      pending.delete(id);
      resolve({timeout: true, ms: timeoutMs});
    }, timeoutMs);
    pending.set(id, (result) => {
      clearTimeout(timer);
      resolve({ms: Date.now() - timedCall.t0, result});
    });
    ws.send(JSON.stringify({id, method, params}));
  });
}
timedCall.seq = 0;

async function main() {
  let liveTargetId = targetId;
  if (mode === 'scratch') {
    const created = await fetch(endpoint + '/json/new?' + encodeURIComponent('data:text/html,<textarea aria-label="Message"></textarea>'), {method: 'PUT'});
    const createdTarget = await created.json();
    liveTargetId = createdTarget.id;
    out.scratch_tab = liveTargetId;
  }
  const list = await (await fetch(endpoint + '/json/list')).json();
  const target = list.find((t) => t.type === 'page' && t.id === liveTargetId);
  if (!target) throw new Error('target not in /json/list: ' + liveTargetId);
  out.pageUrl = target.url;
  const ws = new WebSocket(target.webSocketDebuggerUrl);
  const pending = new Map();
  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('ws open timeout')), 4000);
    ws.addEventListener('open', () => { clearTimeout(timer); resolve(); }, {once: true});
    ws.addEventListener('error', () => { clearTimeout(timer); reject(new Error('ws error')); }, {once: true});
  });
  ws.addEventListener('message', (event) => {
    const frame = JSON.parse(event.data);
    const p = pending.get(frame.id);
    if (!p) return;
    pending.delete(frame.id);
    if (frame.error) p({error: frame.error.message});
    else p(frame.result);
  });
  timedCall.t0 = Date.now();
  const call = (method, params, timeoutMs = 5000) =>
    timedCall(ws, pending, method, params, timeoutMs);

  // Baseline: Runtime.evaluate answers?
  let t = Date.now();
  let r = await call('Runtime.evaluate', {expression: '1+1', returnByValue: true});
  out.steps.baseline_evaluate = {ms: Date.now() - t, ok: !r.timeout, value: r.result?.result?.value, error: r.result?.error};

  // Ground the composer rect fresh (no mouse).
  t = Date.now();
  r = await call('Runtime.evaluate', {expression: `(()=>{const e=document.querySelector('textarea[aria-label="Message"]');if(!e)return null;const b=e.getBoundingClientRect();return {x:b.left+b.width/2,y:b.top+b.height/2,active:document.activeElement===e};})()`, returnByValue: true});
  const ground = r.result?.result?.value || null;
  out.steps.ground = {ms: Date.now() - t, ok: !r.timeout, ground};
  const point = ground ? {x: Math.round(ground.x), y: Math.round(ground.y)} : {x: 286, y: 1103};
  out.point = point;

  // Key control: dispatchKeyEvent answers?
  t = Date.now();
  r = await call('Input.dispatchKeyEvent', {type: 'keyDown', key: 'Shift', modifiers: 8, windowsVirtualKeyCode: 16, nativeVirtualKeyCode: 16});
  const keyDown = {ms: Date.now() - t, ok: !r.timeout};
  t = Date.now();
  r = await call('Input.dispatchKeyEvent', {type: 'keyUp', key: 'Shift', modifiers: 8, windowsVirtualKeyCode: 16, nativeVirtualKeyCode: 16});
  out.steps.key_control = {down: keyDown, up: {ms: Date.now() - t, ok: !r.timeout}};

  if (mode === 'activate') {
    t = Date.now();
    r = await call('Target.activateTarget', {targetId});
    out.steps.activate_target = {ms: Date.now() - t, ok: !r.timeout};
    t = Date.now();
    r = await call('Page.bringToFront', {});
    out.steps.bring_to_front = {ms: Date.now() - t, ok: !r.timeout};
  }

  // The stall question: bare mouseMoved, unless the mode is
  // press-first (press/release before any move).
  if (mode === 'press-first') {
    t = Date.now();
    r = await call('Input.dispatchMouseEvent', {type: 'mousePressed', x: point.x, y: point.y, button: 'left', clickCount: 1});
    out.steps.mouse_pressed_first = {ms: Date.now() - t, ok: !r.timeout, error: r.result?.error};
    t = Date.now();
    r = await call('Input.dispatchMouseEvent', {type: 'mouseReleased', x: point.x, y: point.y, button: 'left', clickCount: 1});
    out.steps.mouse_released_first = {ms: Date.now() - t, ok: !r.timeout, error: r.result?.error};
  }
  t = Date.now();
  r = await call('Input.dispatchMouseEvent', {type: 'mouseMoved', x: point.x, y: point.y});
  out.steps.mouse_moved = {ms: Date.now() - t, ok: !r.timeout, error: r.result?.error};
  if (mode === 'click') {
    // Full click sequence on the composer: focuses it, sends
    // nothing. Proves press/release answer too, not just hover.
    t = Date.now();
    r = await call('Input.dispatchMouseEvent', {type: 'mousePressed', x: point.x, y: point.y, button: 'left', clickCount: 1});
    out.steps.mouse_pressed = {ms: Date.now() - t, ok: !r.timeout, error: r.result?.error};
    t = Date.now();
    r = await call('Input.dispatchMouseEvent', {type: 'mouseReleased', x: point.x, y: point.y, button: 'left', clickCount: 1});
    out.steps.mouse_released = {ms: Date.now() - t, ok: !r.timeout, error: r.result?.error};
    t = Date.now();
    r = await call('Runtime.evaluate', {expression: `(()=>{const e=document.querySelector('textarea[aria-label="Message"]');return e?document.activeElement===e:null;})()`, returnByValue: true});
    out.steps.focus_after_click = {ms: Date.now() - t, focused: r.result?.result?.value};
  }
  out.wall_ms = Date.now() - started;
  ws.close();
  if (mode === 'scratch' && out.scratch_tab) {
    try { await fetch(endpoint + '/json/close/' + out.scratch_tab); } catch (_) {}
  }
  console.log(JSON.stringify(out));
}

main().catch((e) => {
  out.error = String(e && e.message || e);
  out.wall_ms = Date.now() - started;
  console.log(JSON.stringify(out));
  process.exitCode = 1;
});
