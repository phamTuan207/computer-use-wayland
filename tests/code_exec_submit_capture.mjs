// Run: node tests/code_exec_submit_capture.mjs. No network or GUI; stubs the
// Codex exec-tool globals (tools, text, store, load, exit) in a vm context.
//
// Covers the 2026-11-23 run 78be9c5a failure: the executor's hand-composed
// program-submit script defined `thinkMs` but referenced bare `think_ms` in
// the final capture object, so the script threw
// `ReferenceError: think_ms is not defined` at the capture line, after the
// program had already been sent to the relay. The write result was discarded
// and the program response was lost.
//
// The canonical snippet lives in skill/references/session.md ("Submitting a
// code-exec program"). This test extracts that exact fenced block and runs
// it, so the doc and the test cannot drift apart. It also runs the broken
// shape inline and asserts it throws, proving the test detects the bug.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DOC = path.join(ROOT, 'skill', 'references', 'session.md');

// The broken shape, faithful minimal excerpt of the 78be9c5a submit script:
// `thinkMs` defined, bare `think_ms` shorthand referenced in the capture.
const BROKEN = [
  'const program = `started = dom_start()`;',
  'const submitMs = 1795439700000;',
  'const startMs = 1795439280000;',
  'const thinkMs = submitMs - startMs;',
  'const r = { chunk_id: "x" };',
  'text(JSON.stringify({program_chars: program.length, think_ms, submit_ms: submitMs, write_result: r}));',
].join('\n');

const JS_KEYWORDS = new Set([
  'new', 'typeof', 'instanceof', 'in', 'of', 'function', 'return', 'if',
  'else', 'for', 'while', 'do', 'switch', 'case', 'break', 'continue', 'try',
  'catch', 'finally', 'throw', 'await', 'async', 'class', 'extends',
  'import', 'export', 'from', 'delete', 'void', 'yield', 'let', 'var',
  'const', 'this', 'super',
]);

const KNOWN_GLOBALS = new Set([
  'JSON', 'Date', 'Math', 'Object', 'Array', 'String', 'Number', 'Boolean',
  'Promise', 'console', 'parseInt', 'parseFloat', 'isNaN', 'isFinite',
  'undefined', 'NaN', 'Infinity',
  // Codex exec-tool globals, provided by the harness, not declared in snippets.
  'tools', 'text', 'store', 'load', 'exit',
]);

function extractSnippet(docText) {
  const heading = '### Submitting a code-exec program';
  const at = docText.indexOf(heading);
  assert.ok(at >= 0, 'doc is missing the submit-snippet section');
  const fence = docText.indexOf('```js', at);
  assert.ok(fence >= 0, 'doc is missing the js fenced snippet');
  const start = fence + '```js'.length;
  const end = docText.indexOf('```', start);
  assert.ok(end > start, 'unterminated js fence');
  return docText.slice(start, end).replace(/^\n/, '').replace(/\n$/, '');
}

function declaredConsts(code) {
  return new Set([...code.matchAll(/const\s+([A-Za-z_$][\w$]*)/g)].map((m) => m[1]));
}

// Static audit of the capture line: every value identifier in the final
// text(...) call must be a declared const or a known global. Object keys
// (followed by ':') and properties (preceded by '.') are not values.
function auditCaptureLine(code) {
  const line = code.split('\n').find((l) => l.trimStart().startsWith('text('));
  assert.ok(line, 'snippet has no text(...) capture line');
  const declared = declaredConsts(code);
  const violations = [];
  for (const m of line.matchAll(/[A-Za-z_$][\w$]*/g)) {
    const name = m[0];
    const prev = line[m.index - 1];
    const rest = line.slice(m.index + name.length);
    const next = rest.match(/^\s*(.)/)?.[1];
    if (prev === '.' || next === ':') continue;
    if (KNOWN_GLOBALS.has(name)) continue;
    if (JS_KEYWORDS.has(name)) continue;
    if (!declared.has(name)) violations.push(name);
  }
  return violations;
}

function hasBareThinkMsShorthand(code) {
  // Bare `think_ms` as a shorthand property: preceded by { or , and NOT
  // followed by ':'. The explicit mapping `think_ms: thinkMs` does not match.
  return /(?:[{,]\s*)think_ms(?!\s*:)/.test(code);
}

// Run a snippet as an async module body with stubbed exec-tool globals.
// Returns { texts, stored, order, requests } on success; throws on failure.
async function runSnippet(code, { sessionId = 1 } = {}) {
  const texts = [];
  const stored = new Map();
  const order = [];
  const requests = [];
  const fakeEnvelope = {
    chunk_id: 'test-envelope', wall_time_seconds: 1.234, exit_code: 0,
    original_token_count: 120,
    output: JSON.stringify({ returncode: 0, result: { ok: true, completed: 1 }, session_continues: true }),
  };
  const sandbox = {
    tools: {
      write_stdin: async (args) => {
        requests.push(args);
        const req = JSON.parse(args.chars);
        assert.equal(req.args[0], 'code-exec');
        assert.equal(args.session_id, sessionId);
        return fakeEnvelope;
      },
      exec_command: async () => ({ output: '', exit_code: 0 }),
    },
    text: (v) => { order.push('text'); texts.push(typeof v === 'string' ? v : JSON.stringify(v)); },
    store: (k, v) => { order.push('store'); stored.set(k, v); },
    load: (k) => stored.get(k),
    exit: () => { throw new Error('__exit__'); },
  };
  vm.createContext(sandbox);
  const wrapped = `(async () => {\n${code}\n})()`;
  await vm.runInContext(wrapped, sandbox, { filename: 'code-exec-submit-snippet.mjs' });
  return { texts, stored, order, requests, fakeEnvelope };
}

// 1. The broken shape throws exactly the run 78be9c5a error.
{
  let error = null;
  try {
    await runSnippet(BROKEN);
  } catch (e) {
    error = e;
  }
  assert.ok(error, 'broken snippet should throw');
  assert.equal(error.name, 'ReferenceError');
  assert.match(error.message, /think_ms is not defined/);
  console.log('PASS 1: broken shape throws ReferenceError: think_ms is not defined');
}

// 2. The static audit flags the broken shape (think_ms undefined).
{
  const violations = auditCaptureLine(BROKEN);
  assert.deepEqual(violations, ['think_ms']);
  assert.ok(hasBareThinkMsShorthand(BROKEN), 'broken shape must show bare think_ms shorthand');
  console.log('PASS 2: audit flags think_ms as undefined in the broken shape');
}

// 3. The canonical snippet from the doc runs clean and captures a response.
const docText = fs.readFileSync(DOC, 'utf-8');
const snippet = extractSnippet(docText);
const testSnippet = snippet.replace(
  'const RELAY_SESSION_ID = 0;',
  'const RELAY_SESSION_ID = 1;',
);
assert.ok(testSnippet.includes('const RELAY_SESSION_ID = 1;'), 'session id substitution failed');
{
  const { texts, stored, order, requests, fakeEnvelope } = await runSnippet(testSnippet);
  assert.equal(texts.length, 1, 'exactly one capture print');
  const capture = JSON.parse(texts[0]);
  assert.equal(typeof capture.think_ms, 'number');
  assert.ok(Number.isFinite(capture.think_ms) && capture.think_ms > 0, 'think_ms is a positive number');
  assert.equal(typeof capture.submit_ms, 'number');
  assert.equal(typeof capture.submit_utc, 'string');
  const programText = snippet.match(/const program = `([\s\S]*?)`;/)[1];
  assert.equal(capture.program_chars, programText.length, 'program_chars equals the program length');
  assert.deepEqual(capture.write_result, fakeEnvelope, 'captured write_result is the relay envelope');
  assert.equal(requests.length, 1, 'exactly one relay request sent');
  assert.equal(requests[0].session_id, 1);
  assert.deepEqual(stored.get('a1_program_result'), fakeEnvelope, 'result stored before print');
  assert.ok(order.indexOf('store') < order.indexOf('text'), 'store runs before text');
  console.log('PASS 3: canonical snippet captures response with numeric think_ms, store before text');
}

// 4. The canonical snippet has no bare think_ms shorthand, only the explicit mapping.
{
  assert.equal(hasBareThinkMsShorthand(snippet), false, 'canonical snippet must not use bare think_ms shorthand');
  assert.ok(/think_ms:\s*thinkMs/.test(snippet), 'canonical snippet must use think_ms: thinkMs');
  console.log('PASS 4: canonical snippet uses explicit think_ms: thinkMs, no bare shorthand');
}

// 5. The static audit passes on the canonical snippet: every capture value defined.
{
  const violations = auditCaptureLine(snippet);
  assert.deepEqual(violations, [], 'canonical snippet capture line has undefined names: ' + violations.join(', '));
  console.log('PASS 5: audit finds every capture name defined in the canonical snippet');
}

console.log('ALL PASS: code_exec_submit_capture');
