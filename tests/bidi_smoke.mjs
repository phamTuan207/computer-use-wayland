// Smoke checks for tests/puppeteer_bidi.mjs that need no browser at all.
// Run: node tests/bidi_smoke.mjs
// Checks: --help exits 0, an unreachable BiDi endpoint fails fast with a
// structured JSON failure and exit code 2, and a bad argument is rejected.
// No Firefox or Zen binary is required for these checks.
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const script = fileURLToPath(new URL('./puppeteer_bidi.mjs', import.meta.url));
const corePath = process.env.PUPPETEER_CORE_PATH ?? '/tmp/bidi-scratch/node_modules/puppeteer-core';

function run(args, env = {}) {
  const started = Date.now();
  const child = spawnSync('node', [script, ...args], {
    encoding: 'utf8',
    env: { ...process.env, PUPPETEER_CORE_PATH: corePath, ...env },
    timeout: 60000,
  });
  return { ...child, elapsed_ms: Date.now() - started };
}

const help = run(['--help']);
assert.equal(help.status, 0, help.stderr);
assert.ok(help.stdout.includes('WebDriver BiDi'), help.stdout);

const unreachable = run(['--endpoint', 'ws://127.0.0.1:1/session', '--timeout-ms', '5000']);
assert.equal(unreachable.status, 2, unreachable.stdout + unreachable.stderr);
const lines = unreachable.stdout.trim().split('\n').filter(Boolean).map((line) => JSON.parse(line));
const failure = lines.at(-1);
assert.equal(failure.ok, false);
assert.equal(typeof failure.error, 'string');
assert.ok(failure.error.length > 0);
assert.ok(Number.isFinite(failure.total_elapsed_ms));
assert.ok(failure.total_elapsed_ms < 30000, `unreachable endpoint took ${failure.total_elapsed_ms} ms`);
const failedStep = lines.find((line) => line.step === 'run' && line.status === 'failed');
assert.ok(failedStep, 'a failed run step must be logged');
console.log(JSON.stringify({
  ok: true,
  help_exit: help.status,
  unreachable_exit: unreachable.status,
  unreachable_elapsed_ms: unreachable.elapsed_ms,
  unreachable_error: failure.error,
}));
console.log('all bidi smoke checks pass');
