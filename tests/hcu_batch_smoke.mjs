// Browser-free smoke checks for tests/hcu_batch.mjs.
// No browser is launched: every check below fails in argument validation,
// which runs before any browser starts.
//
// Run: node tests/hcu_batch_smoke.mjs
// Exit 0 when all checks pass, 1 otherwise.

import { spawnSync } from 'node:child_process';
import { writeFileSync, unlinkSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const dir = dirname(fileURLToPath(import.meta.url));
const script = join(dir, 'hcu_batch.mjs');
const env = { ...process.env, PLAYWRIGHT_PATH: '/tmp/hcu-scratch/node_modules/playwright-core' };

let failures = 0;
function check(name, ok, detail = '') {
  console.log(JSON.stringify({ check: name, ok, detail }));
  if (!ok) failures += 1;
}

function run(args) {
  return spawnSync('node', [script, ...args], { encoding: 'utf8', env });
}

// 1. --help exits 0 and names the modes.
const help = run(['--help']);
check('help_exits_0', help.status === 0, help.stdout.split('\n')[0] || '');
check('help_names_modes', help.stdout.includes('batch|single'));

// 2. Batch limit: 65 actions are rejected before any browser work.
const tooMany = Array.from({ length: 65 }, () => ({ type: 'click', selector: '#counter' }));
writeFileSync('/tmp/hcu_smoke_65.json', JSON.stringify(tooMany));
const limit = run(['--actions', '/tmp/hcu_smoke_65.json']);
check('limit_65_rejected', limit.status === 2, `exit=${limit.status}`);
check('limit_mentions_64', limit.stdout.includes('64'), limit.stdout.trim().slice(0, 200));
unlinkSync('/tmp/hcu_smoke_65.json');

// 3. Unknown action type is rejected.
writeFileSync('/tmp/hcu_smoke_bad.json', JSON.stringify([{ type: 'teleport', selector: '#counter' }]));
const bad = run(['--actions', '/tmp/hcu_smoke_bad.json']);
check('unknown_type_rejected', bad.status === 2, `exit=${bad.status}`);
check('unknown_type_names_type', bad.stdout.includes('teleport'));
unlinkSync('/tmp/hcu_smoke_bad.json');

// 4. Missing selector is rejected.
writeFileSync('/tmp/hcu_smoke_nosel.json', JSON.stringify([{ type: 'click' }]));
const nosel = run(['--actions', '/tmp/hcu_smoke_nosel.json']);
check('missing_selector_rejected', nosel.status === 2, `exit=${nosel.status}`);
unlinkSync('/tmp/hcu_smoke_nosel.json');

// 5. Bad mode is rejected.
const mode = run(['--mode', 'turbo']);
check('bad_mode_rejected', mode.status === 2, `exit=${mode.status}`);

if (failures === 0) {
  console.log(JSON.stringify({ ok: true, checks: 'all hcu batch smoke checks pass' }));
  process.exit(0);
}
console.log(JSON.stringify({ ok: false, failures }));
process.exit(1);
