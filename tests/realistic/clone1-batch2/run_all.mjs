// Run all realistic tests in tests/realistic/clone1-batch2/ in order.
// Serves the fixtures on loopback, runs each check.mjs as a child
// process, records wall-clock start and end plus elapsed ms per test,
// writes results.json next to this file, and prints a summary.
// Exit 0 when every test passes, 1 otherwise.
// Usage: node tests/realistic/clone1-batch2/run_all.mjs
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { serveDir } from './lib/server.mjs';
import { nowIso } from './lib/browser.mjs';

const rootDir = path.dirname(fileURLToPath(import.meta.url));
const testDirs = fs
  .readdirSync(rootDir, { withFileTypes: true })
  .filter((e) => e.isDirectory() && /^t\d\d-/.test(e.name))
  .map((e) => path.join(rootDir, e.name))
  .sort();

function runOne(checkPath, env) {
  return new Promise((resolve) => {
    const started = Date.now();
    const child = spawn('node', [checkPath], { env, stdio: ['ignore', 'pipe', 'pipe'] });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (d) => {
      stdout += d;
    });
    child.stderr.on('data', (d) => {
      stderr += d;
    });
    child.on('close', (code) => {
      resolve({
        test: path.basename(path.dirname(checkPath)),
        exitCode: code,
        pass: code === 0,
        elapsed_ms: Date.now() - started,
        stdout: stdout.trim(),
        stderr: stderr.trim(),
      });
    });
  });
}

const runStarted = Date.now();
const startedAt = nowIso();
const server = await serveDir(rootDir);
const env = { ...process.env, FIXTURE_BASE_URL: server.url };
const results = [];
for (const dir of testDirs) {
  const checkPath = path.join(dir, 'check.mjs');
  if (!fs.existsSync(checkPath)) {
    results.push({
      test: path.basename(dir),
      exitCode: 2,
      pass: false,
      elapsed_ms: 0,
      stdout: '',
      stderr: 'missing check.mjs',
    });
    continue;
  }
  results.push(await runOne(checkPath, env));
}
await server.close();
const finishedAt = nowIso();
const summary = {
  started_at: startedAt,
  finished_at: finishedAt,
  wall_clock_ms: Date.now() - runStarted,
  passed: results.filter((r) => r.pass).length,
  failed: results.filter((r) => !r.pass).length,
  results,
};
fs.writeFileSync(path.join(rootDir, 'results.json'), JSON.stringify(summary, null, 2));
for (const r of results) {
  console.log(`${r.pass ? 'PASS' : 'FAIL'} ${r.test} ${r.elapsed_ms} ms`);
}
console.log(
  `summary: ${summary.passed} passed, ${summary.failed} failed, ` +
  `wall clock ${summary.wall_clock_ms} ms, results written to results.json`
);
process.exit(summary.failed === 0 ? 0 : 1);
