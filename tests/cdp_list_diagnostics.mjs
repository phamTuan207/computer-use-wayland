// Run: node tests/cdp_list_diagnostics.mjs. The REAL adapter over REAL loopback
// HTTP sockets on ephemeral ports owned by this test. No browser, no GUI, no
// CDP session: only the /json/list preflight is exercised, so a refused or
// failed preflight names the exact URL and the underlying cause instead of a
// bare "fetch failed".
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const adapter = fileURLToPath(new URL('../scripts/cdp.mjs', import.meta.url));

// One adapter run in one-shot CLI mode: request JSON on stdin, one JSON
// envelope on stdout, exit code carries the failure.
function runOnce(args, request) {
  return new Promise(resolve => {
    const child = spawn(process.execPath, [adapter, ...args], { stdio: ['pipe', 'pipe', 'pipe'] });
    const out = [], err = [];
    child.stdout.on('data', c => out.push(c));
    child.stderr.on('data', c => err.push(c));
    child.stdin.end(JSON.stringify(request) + '\n');
    child.on('close', code => resolve({
      code,
      out: Buffer.concat(out).toString(),
      err: Buffer.concat(err).toString(),
    }));
  });
}

function envelope(out) { return JSON.parse(out.trim().split('\n').pop()); }

function listen(server) {
  return new Promise((resolve, reject) =>
    server.once('error', reject).listen(0, '127.0.0.1', () => resolve(server.address().port)));
}

// An owned /json/list fixture; the handler asserts the exact preflight path.
function listServer(handler) {
  const server = createServer((req, res) => {
    assert.equal(req.method, 'GET');
    assert.equal(req.url, '/json/list');
    handler(req, res);
  });
  return listen(server).then(port => ({ server, port, close: () => server.close() }));
}

const listUrl = port => new RegExp(`CDP GET http://127\\.0\\.0\\.1:${port}/json/list: `);

// 1. No listener: the refusal keeps the full URL and the kernel cause code.
{
  const holder = createServer();
  const port = await listen(holder);
  await new Promise(resolve => holder.close(resolve));
  const { code, out } = await runOnce([], { operation: 'tabs', endpoint: `http://127.0.0.1:${port}` });
  assert.equal(code, 1);
  const result = envelope(out);
  assert.equal(result.ok, false);
  assert.equal(result.completed, 0);
  assert.match(result.error, listUrl(port), 'the failed preflight names the exact URL');
  assert.match(result.error, /ECONNREFUSED/, 'the kernel cause code survives');
  console.log('ok connection refused keeps the full /json/list URL and ECONNREFUSED');
}

// 2. A non-2xx preflight preserves the HTTP status next to the URL.
{
  const { server, port, close } = await listServer((req, res) => {
    res.writeHead(500, { 'content-type': 'text/plain' }); res.end('boom');
  });
  try {
    const { code, out } = await runOnce([], { operation: 'tabs', endpoint: `http://127.0.0.1:${port}` });
    assert.equal(code, 1);
    const result = envelope(out);
    assert.match(result.error, listUrl(port));
    assert.match(result.error, /HTTP 500;/, 'the non-2xx status is preserved');
    assert.match(result.error, /cause:\s*unavailable/, 'a response error has no kernel cause');
  } finally { close(); }
  console.log('ok an HTTP 500 preflight reports the status and the URL');
}

// 3. An unparseable tab list surfaces the parse error with the URL.
{
  const { server, port, close } = await listServer((req, res) => {
    res.writeHead(200, { 'content-type': 'application/json' }); res.end('not json');
  });
  try {
    const { code, out } = await runOnce([], { operation: 'tabs', endpoint: `http://127.0.0.1:${port}` });
    assert.equal(code, 1);
    const result = envelope(out);
    assert.match(result.error, listUrl(port));
    assert.doesNotMatch(result.error, /fetch failed/, 'the parse failure is not swallowed');
    assert.match(result.error, /not valid JSON|Unexpected token/, 'the parse reason is surfaced');
  } finally { close(); }
  console.log('ok an invalid JSON tab list surfaces the parse error with the URL');
}

// 4. A successful list is parsed exactly as before: pages only, projections kept.
{
  const { server, port, close } = await listServer((req, res) => {
    res.writeHead(200, { 'content-type': 'application/json' });
    res.end(JSON.stringify([
      { type: 'page', id: 'p1', title: 'Fixture', url: 'http://fixture/' },
      { type: 'iframe', id: 'f1', title: 'hidden', url: 'about:blank' },
      { type: 'page', id: 'p2', title: 'Other', url: 'http://other/',
        webSocketDebuggerUrl: `ws://127.0.0.1:${port}/p2` },
    ]));
  });
  try {
    const { code, out } = await runOnce([], { operation: 'tabs', endpoint: `http://127.0.0.1:${port}` });
    assert.equal(code, 0);
    assert.deepEqual(envelope(out), [
      { id: 'p1', title: 'Fixture', url: 'http://fixture/' },
      { id: 'p2', title: 'Other', url: 'http://other/' },
    ]);
  } finally { close(); }
  console.log('ok a successful list still filters to pages and keeps the projection');
}

// 5. The persistent worker keeps answering after tab lists (reuse path intact).
{
  const { server, port, close } = await listServer((req, res) => {
    res.writeHead(200, { 'content-type': 'application/json' });
    res.end(JSON.stringify([{ type: 'page', id: 'p1', title: 'Fixture', url: 'http://fixture/' }]));
  });
  try {
    const request = { operation: 'tabs', endpoint: `http://127.0.0.1:${port}` };
    const child = spawn(process.execPath, [adapter, '--worker'], { stdio: ['pipe', 'pipe', 'pipe'] });
    const out = [], err = [];
    child.stdout.on('data', c => out.push(c));
    child.stderr.on('data', c => err.push(c));
    child.stdin.end(JSON.stringify(request) + '\n' + JSON.stringify(request) + '\n');
    const code = await new Promise(resolve => child.on('close', resolve));
    assert.equal(code, 0);
    const lines = Buffer.concat(out).toString().trim().split('\n').map(envelope);
    assert.equal(lines.length, 2, 'the worker answers every tab list, not just the first');
    for (const line of lines)
      assert.deepEqual(line, [{ id: 'p1', title: 'Fixture', url: 'http://fixture/' }]);
  } finally { close(); }
  console.log('ok worker mode still answers tab lists over the grafted preflight');
}

console.log('all /json/list diagnostics regressions pass');
