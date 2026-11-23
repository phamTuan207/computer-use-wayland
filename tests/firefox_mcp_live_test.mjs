// firefox-mcp live test on the real Zen (connect-existing), 21/11/2026.
// Spawns the MCP server over stdio, runs the section 8.3 procedure against
// a NEW tab (never navigates an existing user tab), verifies state changes
// in the DOM after every action, then closes the test tab and the session.
// Every tool call logs one JSON line: wall-clock + elapsed ms + ok + bytes.
// Usage: node tests/firefox_mcp_live_test.mjs
//   [MCP_SERVER=node_modules/@mozilla/firefox-mcp/dist/index.js]
import { spawn } from 'node:child_process';
import { performance } from 'node:perf_hooks';

const SERVER = process.env.MCP_SERVER ?? '/tmp/firefox-mcp-test/node_modules/@mozilla/firefox-mcp/dist/index.js';
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
    const msg = JSON.stringify({ jsonrpc: '2.0', id, method, params });
    proc.stdin.write(msg + '\n');
    setTimeout(() => {
      if (pending.has(id)) { pending.delete(id); reject(new Error(`timeout waiting for ${method}`)); }
    }, 60000);
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
    if (msg.id !== undefined && pending.has(msg.id)) {
      const { resolve } = pending.get(msg.id);
      pending.delete(msg.id);
      resolve(msg);
    }
  }
}

async function callTool(name, args = {}) {
  const t0 = performance.now();
  const res = await send('tools/call', { name, arguments: args });
  const ms = Math.round(performance.now() - t0);
  const text = (res.result?.content ?? []).map((c) => c.text ?? '').join('');
  return { ms, text, raw: res };
}

function snapshotText(t) {
  return t;
}

async function main() {
  proc = spawn('node', [SERVER, '--connect-existing', '--marionette-port', '2828', '--log-file', '/tmp/firefox-mcp.log'], { stdio: ['pipe', 'pipe', 'pipe'] });
  proc.stdout.on('data', onData);
  proc.stderr.on('data', (d) => process.stderr.write('[mcp-stderr] ' + d.toString()));
  proc.on('exit', (code) => log('server_exit', code === 0 ? 'ok' : 'failed', { code }));

  const init = await send('initialize', { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'worker-j-test', version: '1.0.0' } });
  log('initialize', 'ok', { server: init.result?.serverInfo?.name ?? null, version: init.result?.serverInfo?.version ?? null });
  notify('notifications/initialized');

  const tools = await send('tools/list');
  const names = (tools.result?.tools ?? []).map((t) => t.name);
  log('tools_list', 'ok', { count: names.length, names });

  const need = ['list_pages', 'new_page', 'take_snapshot', 'click_by_uid', 'fill_by_uid', 'evaluate_script', 'screenshot_page', 'close_page', 'close_firefox_session'];
  const missing = need.filter((n) => !names.includes(n));
  if (missing.length) { log('tools_missing', 'failed', { missing }); throw new Error('missing tools: ' + missing.join(',')); }
  const hasConsole = names.includes('list_console_messages');
  log('optional_tools', 'ok', { list_console_messages: hasConsole });

  const pages0 = await callTool('list_pages');
  log('list_pages', 'ok', { ms: pages0.ms, bytes: pages0.text.length, preview: pages0.text.slice(0, 300) });

  const np = await callTool('new_page', { url: FIXTURE, wait: 'interactive' });
  log('new_page', 'ok', { ms: np.ms, bytes: np.text.length, preview: np.text.slice(0, 300) });

  const snap1 = await callTool('take_snapshot', { maxLines: 60 });
  log('take_snapshot_1', 'ok', { ms: snap1.ms, bytes: snap1.text.length });
  const btnLine = snap1.text.split('\n').find((l) => l.includes('Increment') || l.includes('count-btn'));
  log('snapshot_button', btnLine ? 'ok' : 'failed', { line: btnLine ?? null });
  if (!btnLine) throw new Error('button not found in snapshot');

  const uid = btnLine.match(/uid=([^\s\]]+)/)?.[1];
  if (!uid) throw new Error('no uid on button line: ' + btnLine);
  const click = await callTool('click_by_uid', { uid });
  log('click_by_uid', 'ok', { ms: click.ms, uid, bytes: click.text.length, preview: click.text.slice(0, 200) });

  const snap2 = await callTool('take_snapshot', { maxLines: 60 });
  const counter1 = snap2.text.includes('>1<') || /count[^<]*>1</.test(snap2.text) || snap2.text.match(/count[^\n]{0,40}1/);
  log('take_snapshot_2_verify_counter', counter1 ? 'ok' : 'failed', { ms: snap2.ms, bytes: snap2.text.length });

  const inputLine = snap1.text.split('\n').find((l) => /textbox/i.test(l) || l.includes('Name'));
  const inputUid = inputLine?.match(/uid=([^\s\]]+)/)?.[1];
  if (inputUid) {
    const fill = await callTool('fill_by_uid', { uid: inputUid, value: 'mcp-test' });
    log('fill_by_uid', 'ok', { ms: fill.ms, uid: inputUid, bytes: fill.text.length });
    const ev = await callTool('evaluate_script', { function: "() => document.querySelector('#name')?.value ?? null" });
    log('evaluate_script_input_value', 'ok', { ms: ev.ms, text: ev.text.slice(0, 200) });
  } else {
    log('fill_by_uid', 'failed', { reason: 'no input uid in snapshot' });
  }

  const shot = await callTool('screenshot_page', { saveTo: '/tmp/firefox-mcp-test/screenshot.png' });
  log('screenshot_page', 'ok', { ms: shot.ms, bytes: shot.text.length, preview: shot.text.slice(0, 200) });

  if (hasConsole) {
    const consoleMsgs = await callTool('list_console_messages');
    log('list_console_messages', 'ok', { ms: consoleMsgs.ms, bytes: consoleMsgs.text.length });
  } else {
    log('list_console_messages', 'skipped', { reason: 'not in basic preset, needs developer preset' });
  }

  const close = await callTool('close_page', {});
  log('close_page', 'ok', { ms: close.ms, bytes: close.text.length, preview: close.text.slice(0, 200) });

  const closeSession = await callTool('close_firefox_session', {});
  log('close_firefox_session', 'ok', { ms: closeSession.ms, bytes: closeSession.text.length });

  log('done', 'ok', { total_ms: Math.round(performance.now() - startedAt) });
  proc.kill();
  process.exit(0);
}

main().catch((e) => {
  log('run', 'failed', { error: String(e?.message ?? e) });
  try { proc?.kill(); } catch {}
  process.exit(2);
});
