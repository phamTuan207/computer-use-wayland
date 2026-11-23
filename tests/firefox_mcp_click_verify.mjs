// Focused firefox-mcp click verification, 21/11/2026.
// Question: does click_by_uid actually trigger the button handler on live Zen?
// (Puppeteer BiDi pointer clicks do NOT.) Verifies via evaluate_script,
// the reliable read path. Also verifies screenshot with an allowed path
// and close_page with pageIdx.
import { spawn } from 'node:child_process';
import { performance } from 'node:perf_hooks';

const SERVER = '/tmp/firefox-mcp-test/node_modules/@mozilla/firefox-mcp/dist/index.js';
const FIXTURE = new URL('./bidi_fixture.html', import.meta.url).href;
const startedAt = performance.now();
let nextId = 1;
let buffer = '';
const pending = new Map();
let proc = null;

function log(step, status, detail = {}) {
  console.log(JSON.stringify({ ts: new Date().toISOString(), step, status, elapsed_ms: Math.round(performance.now() - startedAt), ...detail }));
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
async function main() {
  proc = spawn('node', [SERVER, '--connect-existing', '--marionette-port', '2828', '--unrestricted-save-paths', '--log-file', '/tmp/firefox-mcp.log'], { stdio: ['pipe', 'pipe', 'pipe'] });
  proc.stdout.on('data', onData);
  proc.stderr.on('data', () => {});
  await send('initialize', { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'worker-j-verify', version: '1.0.0' } });
  notify('notifications/initialized');
  log('initialize', 'ok', {});

  const np = await callTool('new_page', { url: FIXTURE, wait: 'interactive' });
  const pageIdx = Number((np.text.match(/\[(\d+)\]/) || [])[1]);
  log('new_page', 'ok', { ms: np.ms, pageIdx });

  const before = await callTool('evaluate_script', { function: "() => document.querySelector('#count').textContent" });
  log('counter_before', 'ok', { ms: before.ms, text: before.text.slice(0, 120) });

  const snap = await callTool('take_snapshot', { maxLines: 60 });
  const btnLine = snap.text.split('\n').find((l) => l.includes('Increment'));
  const uid = btnLine?.match(/uid=([^\s\]]+)/)?.[1];
  log('snapshot_button', uid ? 'ok' : 'failed', { ms: snap.ms, uid: uid ?? null });

  const click = await callTool('click_by_uid', { uid });
  log('click_by_uid', 'ok', { ms: click.ms, text: click.text.slice(0, 100) });

  const after = await callTool('evaluate_script', { function: "() => document.querySelector('#count').textContent" });
  const counterAfter = (after.text.match(/"(\d+)"/) || [])[1];
  log('counter_after_click', counterAfter === '1' ? 'ok' : 'failed', { ms: after.ms, counter: counterAfter ?? null, text: after.text.slice(0, 120) });

  const shot = await callTool('screenshot_page', { saveTo: '/tmp/firefox-mcp-test/shot2.png' });
  log('screenshot_page', shot.text.includes('Error') ? 'failed' : 'ok', { ms: shot.ms, text: shot.text.slice(0, 200) });

  const close = await callTool('close_page', { pageIdx });
  log('close_page', close.text.includes('Error') ? 'failed' : 'ok', { ms: close.ms, text: close.text.slice(0, 150) });

  await callTool('close_firefox_session', {});
  log('done', 'ok', { total_ms: Math.round(performance.now() - startedAt) });
  proc.kill();
  process.exit(0);
}
main().catch((e) => { log('run', 'failed', { error: String(e?.message ?? e) }); try { proc?.kill(); } catch {} process.exit(2); });
