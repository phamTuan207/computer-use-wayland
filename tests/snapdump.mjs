// One-off snapshot dump for the problem-create fixture (debug helper).
import { spawn } from 'node:child_process';
const SERVER = '/tmp/firefox-mcp-test/node_modules/@mozilla/firefox-mcp/dist/index.js';
const FIXTURE = new URL('./fixtures/problem-create-fixture.html', import.meta.url).href;
let nextId = 1, buffer = '';
const pending = new Map();
let proc = spawn('node', [SERVER, '--connect-existing', '--marionette-port', '2828', '--log-file', '/tmp/firefox-mcp.log'], { stdio: ['pipe', 'pipe', 'pipe'] });
proc.stdout.on('data', (c) => { buffer += c.toString(); let i; while ((i = buffer.indexOf('\n')) >= 0) { const line = buffer.slice(0, i).trim(); buffer = buffer.slice(i + 1); if (!line) continue; let m; try { m = JSON.parse(line); } catch { continue; } if (m.id !== undefined && pending.has(m.id)) { const { resolve } = pending.get(m.id); pending.delete(m.id); resolve(m); } } });
proc.stderr.on('data', () => {});
function send(method, params = {}) { return new Promise((resolve, reject) => { const id = nextId++; pending.set(id, { resolve, reject }); proc.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n'); setTimeout(() => reject(new Error('timeout')), 30000); }); }
function notify(method, params = {}) { proc.stdin.write(JSON.stringify({ jsonrpc: '2.0', method, params }) + '\n'); }
async function callTool(name, args = {}) { const res = await send('tools/call', { name, arguments: args }); return (res.result?.content ?? []).map((c) => c.text ?? '').join(''); }
await send('initialize', { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'snapdump', version: '1.0.0' } });
notify('notifications/initialized');
const np = await callTool('new_page', { url: FIXTURE, wait: 'interactive' });
console.log('NEWPAGE:', np.slice(0, 120));
const snap = await callTool('take_snapshot', { maxLines: 120 });
console.log('=== SNAPSHOT ===');
console.log(snap);
console.log('=== END ===');
const idx = Number((np.match(/\[(\d+)\]/) || [])[1]);
await callTool('close_page', { pageIdx: idx });
await callTool('close_firefox_session', {});
proc.kill();
process.exit(0);
