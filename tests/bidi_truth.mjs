#!/usr/bin/env node
// Dependency-free WebDriver BiDi helper (Node 22+ built-in WebSocket).
// No puppeteer, no npm install. Talks to Zen on ws://127.0.0.1:9222/session.
// Usage:
//   node tests/bidi_truth.mjs --list
//   node tests/bidi_truth.mjs --match calibration-grid --out /tmp/truth.json
//   node tests/bidi_truth.mjs --match calibration-grid --expr "window.__hits" --out /tmp/hits.json
//   node tests/bidi_truth.mjs --match calibration-grid --expr "window.__hits.length" --out /tmp/n.json
import { writeFileSync } from 'node:fs';

const BIDI_URL = process.env.BIDI_URL || 'ws://127.0.0.1:9222/session';

const TRUTH_EXPR = `(() => {
  const targets = [...document.querySelectorAll('[data-tid]')].map((el) => {
    const r = el.getBoundingClientRect();
    return { id: el.dataset.tid, x: r.x, y: r.y, w: r.width, h: r.height,
             cx: r.x + r.width / 2, cy: r.y + r.height / 2 };
  });
  return {
    url: location.href,
    innerX: window.mozInnerScreenX, innerY: window.mozInnerScreenY,
    dpr: window.devicePixelRatio, vw: window.innerWidth, vh: window.innerHeight,
    scrollX: window.scrollX, scrollY: window.scrollY,
    targets, hits: window.__hits || null,
  };
})()`;

function parseArgs(argv) {
  const out = { match: '', outPath: '', expr: TRUTH_EXPR, list: false };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--match') out.match = argv[++i];
    else if (argv[i] === '--out') out.outPath = argv[++i];
    else if (argv[i] === '--expr') out.expr = argv[++i];
    else if (argv[i] === '--list') out.list = true;
  }
  return out;
}

let nextId = 1;
const pending = new Map();

function send(ws, method, params) {
  return new Promise((resolve, reject) => {
    const id = nextId++;
    pending.set(id, { resolve, reject });
    ws.send(JSON.stringify({ id, method, params }));
    setTimeout(() => {
      if (pending.has(id)) {
        pending.delete(id);
        reject(new Error('timeout waiting for ' + method));
      }
    }, 15000);
  });
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const ws = new WebSocket(BIDI_URL);
  await new Promise((resolve, reject) => {
    ws.onopen = resolve;
    ws.onerror = () => reject(new Error('cannot connect to ' + BIDI_URL));
  });
  ws.onmessage = (event) => {
    let msg;
    try { msg = JSON.parse(event.data); } catch { return; }
    if (msg.id && pending.has(msg.id)) {
      const { resolve, reject } = pending.get(msg.id);
      pending.delete(msg.id);
      if (msg.type === 'error' || msg.error) reject(new Error(JSON.stringify(msg.error || msg)));
      else resolve(msg.result);
    }
  };
  try {
    const session = await send(ws, 'session.new', { capabilities: {} });
    const sessionId = session.sessionId;
    const tree = await send(ws, 'browsingContext.getTree', {});
    const contexts = [];
    const walk = (nodes) => {
      for (const n of nodes || []) {
        contexts.push({ id: n.context, url: n.url || '' });
        if (n.children) walk(n.children);
      }
    };
    walk(tree.contexts);
    if (args.list) {
      console.log(JSON.stringify(contexts, null, 2));
      ws.close();
      return;
    }
    const target = contexts.find((c) => c.url.includes(args.match));
    if (!target) {
      throw new Error('no browsing context url contains: ' + args.match +
        '; contexts: ' + JSON.stringify(contexts));
    }
    const evalResult = await send(ws, 'script.evaluate', {
      expression: args.expr,
      target: { context: target.id },
      awaitPromise: true,
      resultOwnership: 'root',
    });
    const value = evalResult?.result?.value ?? null;
    const out = JSON.stringify({ context: target.id, url: target.url, value }, null, 2);
    if (args.outPath) writeFileSync(args.outPath, out + '\n');
    console.log(out);
  } finally {
    ws.close();
  }
}

main().catch((err) => { console.error('bidi_truth error: ' + err.message); process.exit(1); });
