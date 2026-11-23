// Real-task re-test (1.3.2 / 5.1), 21/11/2026.
// Task: create a problem through the 3-step fixture form (mimics the Polygon
// problem-creation flow): fill 4 fields, next step, fill statement + checker,
// next step, upload a test zip, set points, submit, verify the result.
// Driver: firefox-mcp over stdio (connect-existing to the live Zen), the
// DOM-first path. Every action is state-verified: after each click/fill the
// script reads the DOM back and checks the expected change. A click that does
// not produce its expected change counts as a MISS. Total wall time, per-step
// timings, miss count, and slow steps are logged as JSON lines.
// Usage: node tests/real_task_problem_create.mjs
import { spawn } from 'node:child_process';
import { performance } from 'node:perf_hooks';

const SERVER = '/tmp/firefox-mcp-test/node_modules/@mozilla/firefox-mcp/dist/index.js';
const FIXTURE = new URL('./fixtures/problem-create-fixture.html', import.meta.url).href;
const ZIP = '/tmp/realtask/problem-tests.zip';
const startedAt = performance.now();
let nextId = 1;
let buffer = '';
const pending = new Map();
let proc = null;
let misses = 0;
const steps = [];

function log(step, status, detail = {}) {
  const e = { ts: new Date().toISOString(), step, status, elapsed_ms: Math.round(performance.now() - startedAt), ...detail };
  steps.push(e);
  console.log(JSON.stringify(e));
  return e;
}
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = nextId++;
    pending.set(id, { resolve, reject, method });
    proc.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n');
    setTimeout(() => { if (pending.has(id)) { pending.delete(id); reject(new Error('timeout ' + method)); } }, 60000);
  });
}
function notify(method, params = {}) {
  proc.stdin.write(JSON.stringify({ jsonrpc: '2.0', method, params }) + '\n');
}
function onData(chunk) {
  buffer += chunk.toString();
  let idx;
  while ((idx = buffer.indexOf('\n')) >= 0) {
    const line = buffer.slice(0, idx).trim();
    buffer = buffer.slice(idx + 1);
    if (!line) continue;
    let msg;
    try { msg = JSON.parse(line); } catch { continue; }
    if (msg.id !== undefined && pending.has(msg.id)) { const { resolve } = pending.get(msg.id); pending.delete(msg.id); resolve(msg); }
  }
}
async function callTool(name, args = {}) {
  const t0 = performance.now();
  const res = await send('tools/call', { name, arguments: args });
  const text = (res.result?.content ?? []).map((c) => c.text ?? '').join('');
  return { ms: Math.round(performance.now() - t0), text };
}
async function evalJs(fn) {
  const r = await callTool('evaluate_script', { function: fn });
  const m = r.text.match(/```json\n([\s\S]*?)\n```/);
  return m ? JSON.parse(m[1]) : r.text;
}
async function snapshot() {
  const s = await callTool('take_snapshot', { maxLines: 120 });
  return s.text;
}
function findUid(snap, needle) {
  const line = snap.split('\n').find((l) => l.includes(needle));
  return line?.match(/uid=([^\s\]]+)/)?.[1] ?? null;
}
async function fillChecked(needle, value, verifyFn) {
  const snap = await snapshot();
  const uid = findUid(snap, needle);
  if (!uid) { misses++; log('fill', 'failed', { needle, reason: 'uid not found' }); return false; }
  const t0 = performance.now();
  await callTool('fill_by_uid', { uid, value });
  const ms = Math.round(performance.now() - t0);
  const ok = await verifyFn();
  if (!ok) misses++;
  log('fill', ok ? 'ok' : 'MISS', { needle, value, ms });
  return ok;
}
async function clickChecked(needle, verifyFn) {
  const snap = await snapshot();
  const uid = findUid(snap, needle);
  if (!uid) { misses++; log('click', 'failed', { needle, reason: 'uid not found' }); return false; }
  const t0 = performance.now();
  await callTool('click_by_uid', { uid });
  const ms = Math.round(performance.now() - t0);
  const ok = await verifyFn();
  if (!ok) misses++;
  log('click', ok ? 'ok' : 'MISS', { needle, ms });
  return ok;
}
async function main() {
  proc = spawn('node', [SERVER, '--connect-existing', '--marionette-port', '2828', '--unrestricted-save-paths', '--log-file', '/tmp/firefox-mcp.log'], { stdio: ['pipe', 'pipe', 'pipe'] });
  proc.stdout.on('data', onData);
  proc.stderr.on('data', () => {});
  await send('initialize', { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'worker-j-realtask', version: '1.0.0' } });
  notify('notifications/initialized');
  log('initialize', 'ok', {});

  const np = await callTool('new_page', { url: FIXTURE, wait: 'interactive' });
  const pageIdx = Number((np.text.match(/\[(\d+)\]/) || [])[1]);
  log('new_page', 'ok', { ms: np.ms, pageIdx });

  // Dismiss any leftover alert dialog from a previous run, if present.
  try { const d = await callTool('dismiss_dialog'); log('dismiss_leftover_dialog', 'ok', { text: d.text.slice(0, 80) }); } catch { log('dismiss_leftover_dialog', 'skipped', { reason: 'no dialog' }); }

  // Step 1: general info (snapshot lines use label text, not HTML ids)
  await fillChecked('Problem title', 'Bubble Sort Practice', async () => (await evalJs("() => document.querySelector('#title').value")) === 'Bubble Sort Practice');
  await fillChecked('Short name', 'bubble-sort', async () => (await evalJs("() => document.querySelector('#shortname').value")) === 'bubble-sort');
  await fillChecked('Time limit', '2000', async () => (await evalJs("() => document.querySelector('#timelimit').value")) === '2000');
  await clickChecked('Next: Statement', async () => (await evalJs("() => document.querySelector('#step2').classList.contains('active')")) === true);

  // Step 2: statement + checker
  await fillChecked('Statement (English)', 'Sort the array in non-decreasing order.', async () => (await evalJs("() => document.querySelector('#statement').value")) === 'Sort the array in non-decreasing order.');
  await fillChecked('Checker', 'lcmp', async () => (await evalJs("() => document.querySelector('#checker').value")) === 'lcmp');
  await clickChecked('Next: Tests', async () => (await evalJs("() => document.querySelector('#step3').classList.contains('active')")) === true);

  // Step 3: upload + points + submit
  const snap3 = await snapshot();
  const fileUid = findUid(snap3, 'Test archive') || findUid(snap3, 'Choose File') || findUid(snap3, 'No file chosen');
  if (!fileUid) { misses++; log('upload', 'failed', { reason: 'file input uid not found' }); }
  else {
    const t0 = performance.now();
    const up = await callTool('upload_file_by_uid', { uid: fileUid, filePath: ZIP });
    const ms = Math.round(performance.now() - t0);
    const shown = await evalJs("() => document.querySelector('#upload-status').textContent");
    const ok = shown.includes('problem-tests.zip');
    if (!ok) misses++;
    log('upload', ok ? 'ok' : 'MISS', { ms, status: shown, tool: up.text.slice(0, 100) });
  }
  await fillChecked('Points per hidden test', '20', async () => (await evalJs("() => document.querySelector('#points').value")) === '20');
  await clickChecked('Submit problem', async () => (await evalJs("() => document.querySelector('#result').style.display")) === 'block');

  // Verify the result summary
  const res = await evalJs("() => ({ title: document.querySelector('#res-title')?.textContent, short: document.querySelector('#res-short')?.textContent, checker: document.querySelector('#res-checker')?.textContent, file: document.querySelector('#res-file')?.textContent, points: document.querySelector('#res-points')?.textContent })");
  const resOk = res.title?.includes('Bubble Sort Practice') && res.short?.includes('bubble-sort') && res.checker?.includes('lcmp') && res.file?.includes('problem-tests.zip') && res.points?.includes('20');
  if (!resOk) misses++;
  log('verify_result', resOk ? 'ok' : 'MISS', { res });

  const close = await callTool('close_page', { pageIdx });
  log('close_page', 'ok', { ms: close.ms });
  await callTool('close_firefox_session', {});
  const totalMs = Math.round(performance.now() - startedAt);
  const slow = steps.filter((s) => s.ms !== undefined && s.ms > 1000).map((s) => s.step);
  log('SUMMARY', misses === 0 ? 'ok' : 'failed', { total_ms: totalMs, total_s: (totalMs / 1000).toFixed(2), misses, slow_steps: slow, steps_count: steps.length });
  proc.kill();
  process.exit(misses === 0 ? 0 : 2);
}
main().catch((e) => { log('run', 'failed', { error: String(e?.message ?? e), misses }); try { proc?.kill(); } catch {} process.exit(2); });
