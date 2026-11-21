// Headless driver for the documented codex-y5 workflows.
import puppeteer from 'puppeteer-core';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { verifyTest } from './check.mjs';

const args = process.argv.slice(2);
function argValue(flag) {
  const index = args.indexOf(flag);
  return index >= 0 ? args[index + 1] : undefined;
}

const selectedTest = argValue('--test');
const runAll = args.includes('--all');
const CHROME = process.env.CU_CHROME_PATH || '/usr/bin/chromium';

const fixtures = {
  '01': 'tests/realistic/codex-y5/fixtures/test-01-git-workflow.html',
  '02': 'tests/realistic/codex-y5/fixtures/test-02-music-player.html',
  '03': 'tests/realistic/codex-y5/fixtures/test-03-password-vault.html',
  '04': 'tests/realistic/codex-y5/fixtures/test-04-maps-directions.html',
  '05': 'tests/realistic/codex-y5/fixtures/test-05-calendar-recurring.html',
  '06': 'tests/realistic/codex-y5/fixtures/test-06-video-editor.html',
  '07': 'tests/realistic/codex-y5/fixtures/test-07-chat-search.html',
  '08': 'tests/realistic/codex-y5/fixtures/test-08-spreadsheet-pivot.html',
  '09': 'tests/realistic/codex-y5/fixtures/test-09-file-search-tag.html',
  '10': 'tests/realistic/codex-y5/fixtures/test-10-extension-settings.html',
};
const orderedTestIds = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10'];

async function fill(page, selector, value) {
  await page.click(selector);
  await page.$eval(selector, (element) => {
    element.value = '';
    element.dispatchEvent(new Event('input', { bubbles: true }));
  });
  await page.type(selector, value);
}

async function gitCommand(page, command) {
  await page.type('#terminal-command-input', command);
  await page.click('#btn-run-git-command');
}

export async function driveTest(page, id) {
  if (id === '01') {
    await gitCommand(page, 'git switch -c feature/cleanup');
    await fill(page, '#file-config-editor', 'mode=preview\nlog=verbose');
    await gitCommand(page, 'git add config.txt');
    await gitCommand(page, 'git commit -m "Add preview mode"');
    await gitCommand(page, 'git switch main');
    await fill(page, '#file-config-editor', 'mode=stable\nlog=compact');
    await gitCommand(page, 'git add config.txt');
    await gitCommand(page, 'git commit -m "Use compact logs"');
    await gitCommand(page, 'git switch feature/cleanup');
    await gitCommand(page, 'git merge main');
    await page.click('#btn-use-incoming');
    await page.click('#btn-undo-conflict-resolution');
    await page.click('#btn-use-ours');
    await gitCommand(page, 'git commit -m "Merge main after resolving config"');
    await gitCommand(page, 'git status --short');
    await gitCommand(page, 'git log --oneline');
  } else if (id === '02') {
    await page.type('#playlist-name-input', 'Morning Focus');
    await page.click('#btn-create-playlist');
    await page.click('#btn-add-track-low-tide');
    await page.click('#btn-add-track-paper-planes');
    await page.click('#btn-add-track-quiet-circuit');
    await page.click('#btn-add-track-night-shift');
    await page.click('#btn-move-paper-up');
    await page.click('#btn-remove-quiet-circuit');
    await page.click('#btn-undo-playlist-change');
    await page.click('#btn-shuffle');
    await page.click('#btn-remove-night-shift');
    await page.click('#btn-save-playlist');
  } else if (id === '03') {
    await page.type('#master-key-input', 'vault-access-key');
    await page.click('#btn-unlock-vault');
    await page.click('#btn-add-entry');
    await page.type('#entry-title-input', 'Research Portal');
    await page.type('#entry-username-input', 'research-user');
    await page.click('#btn-generate-password');
    await page.click('#btn-save-entry');
    await page.click('#btn-reveal-password');
    await page.click('#btn-copy-password');
    await page.click('#btn-edit-entry');
    await fill(page, '#entry-title-input', 'Research Vault');
    await fill(page, '#entry-username-input', 'qa-operator');
    await page.click('#btn-save-entry');
    await page.click('#btn-delete-entry');
    await page.click('#btn-undo-delete');
    await page.click('#btn-lock-vault');
    await page.type('#master-key-input', 'vault-access-key');
    await page.click('#btn-unlock-vault');
  } else if (id === '04') {
    await page.type('#origin-input', 'Harbor Square');
    await page.click('#btn-search-origin');
    await page.click('#btn-pick-origin-harbor-square');
    await page.type('#destination-input', 'Workshop District');
    await page.click('#btn-search-destination');
    await page.click('#btn-pick-destination-workshop-district');
    await page.click('#btn-find-routes');
    await page.click('#btn-select-river-express');
    await page.click('#avoid-tolls-toggle');
    await page.click('#btn-select-north-loop');
    await page.click('#btn-save-route');
    await page.click('#btn-reverse-route');
    await page.click('#btn-find-routes');
    await page.click('#btn-select-north-loop');
    await page.click('#btn-save-route');
  } else if (id === '05') {
    await page.type('#event-title-input', 'Design review');
    await page.type('#event-start-date', '2026-11-23');
    await page.type('#event-location-input', 'Room Ash');
    await page.select('#repeat-frequency', 'weekly');
    await fill(page, '#occurrence-limit', '5');
    await page.click('#btn-create-event');
    await page.click('#btn-edit-1130');
    await fill(page, '#edit-event-title', 'Design review prep');
    await page.click('#btn-save-event-changes');
    await page.click('#btn-edit-1123');
    await page.select('#edit-scope', 'series');
    await fill(page, '#edit-event-location', 'Room Cedar');
    await page.click('#btn-save-event-changes');
    await page.click('#btn-delete-1207');
    await page.click('#btn-undo-calendar-delete');
    await page.click('#btn-delete-1221');
  } else if (id === '06') {
    await page.click('#btn-open-import');
    await page.waitForSelector('#import-modal:not([hidden])');
    await page.click('#chk-import-forest');
    await page.click('#chk-import-city');
    await page.click('#chk-import-score');
    await page.click('#btn-import-selected');
    await page.click('#btn-add-forest');
    await page.click('#btn-add-city');
    await page.click('#btn-select-forest');
    await fill(page, '#playhead-input', '5');
    await page.click('#btn-split-selected');
    await page.click('#btn-select-forest-tail');
    await fill(page, '#trim-duration-input', '2');
    await page.click('#btn-apply-trim');
    await page.click('#btn-undo-edit');
    await fill(page, '#trim-duration-input', '6');
    await page.click('#btn-apply-trim');
    await page.click('#btn-select-city');
    await page.click('#btn-move-selected-left');
    await page.click('#btn-move-selected-left');
    await page.select('#transition-type', 'Cross Dissolve');
    await page.click('#btn-add-transition');
    await page.select('#export-resolution-select', '1920x1080');
    await page.select('#export-frame-rate-select', '30 fps');
    await page.select('#export-codec-select', 'H.264');
    await page.type('#export-filename-input', 'harbor-recap.mp4');
    await page.click('#btn-export-video');
  } else if (id === '07') {
    await page.type('#search-query-input', 'Release checklist');
    await page.click('#btn-search-messages');
    await page.select('#sender-filter', 'Design Bot');
    await page.click('#btn-apply-filters');
    await page.select('#sender-filter', 'Build Bot');
    await page.click('#btn-apply-filters');
    await page.type('#from-date-input', '2026-10-12');
    await page.type('#to-date-input', '2026-10-12');
    await page.click('#btn-apply-filters');
    await page.click('#btn-open-result-m1');
    await page.click('#btn-star-message');
    await page.click('#btn-forward-message');
    await page.type('#forward-room-input', 'Release Room');
    await page.click('#btn-confirm-forward');
  } else if (id === '08') {
    await page.click('#btn-create-pivot');
    await page.select('#pivot-group-select', 'Category');
    await page.select('#pivot-value-select', 'Amount');
    await page.select('#pivot-aggregation-select', 'Sum');
    await page.select('#pivot-aggregation-select', 'Count');
    await page.click('#btn-refresh-pivot');
    await page.select('#pivot-aggregation-select', 'Sum');
    await page.click('#btn-refresh-pivot');
    await page.select('#pivot-filter-select', 'South');
    await page.click('#btn-refresh-pivot');
    await fill(page, '#source-south-hardware', '900');
    await page.click('#btn-refresh-pivot');
  } else if (id === '09') {
    await page.type('#file-search-input', 'releases');
    await page.click('#btn-search-files');
    await fill(page, '#file-search-input', 'release');
    await page.click('#btn-search-files');
    await page.click('#check-file-checklist');
    await page.click('#check-file-plan');
    await page.click('#btn-open-tag-panel');
    await page.type('#tag-name-input', 'Review');
    await page.click('#btn-apply-tag');
    await page.click('#btn-filter-review');
    await page.click('#btn-select-visible-files');
    await page.type('#rename-prefix-input', 'approved-');
    await page.click('#btn-rename-selected');
    await page.select('#move-target-folder', 'Reviewed');
    await page.click('#btn-move-selected');
  } else if (id === '10') {
    await page.click('#btn-toggle-extension');
    await page.click('#btn-toggle-extension');
    await page.click('#btn-toggle-extension');
    await page.click('#btn-open-sites');
    await page.select('#site-calendar-select', 'Block');
    await page.click('#btn-save-site-permissions');
    await page.select('#site-calendar-select', 'Allow');
    await page.select('#site-drive-select', 'Block');
    await page.click('#btn-save-site-permissions');
    await page.click('#btn-open-options');
    await page.click('#option-notify-toggle');
    await page.click('#option-auto-update-toggle');
    await page.click('#btn-save-options');
    await page.click('#btn-reload-settings');
    await page.waitForFunction(() => document.querySelector('#extension-persistence-status')?.textContent === 'State restored after reload');
    await page.click('#btn-open-options');
    await page.click('#btn-reset-defaults');
    await page.click('#btn-reload-settings');
    await page.waitForFunction(() => document.querySelector('#extension-persistence-status')?.textContent === 'State restored after reload');
  } else {
    throw new Error(`Unknown test id: ${id}`);
  }
}

async function runOne(browser, id, fixture) {
  const started = performance.now();
  const page = await browser.newPage();
  try {
    await page.goto(pathToFileURL(path.resolve(process.cwd(), fixture)).href);
    const fresh = await verifyTest(page, id);
    if (fresh.passed) throw new Error(`Fixture ${id} passed before its workflow ran`);
    await driveTest(page, id);
    const result = await verifyTest(page, id);
    return {
      test: id,
      passed: result.passed,
      fresh_fixture_failed_as_expected: !fresh.passed,
      failures: result.failures,
      total_ms: Math.round(performance.now() - started),
      state: result.state,
    };
  } finally {
    await page.close();
  }
}

async function main() {
  const tests = runAll ? orderedTestIds.map((id) => [id, fixtures[id]]) : [[selectedTest || '01', fixtures[selectedTest || '01']]];
  if (tests.some(([id, fixture]) => !fixture || !fixtures[id])) {
    console.error('Use --test 01 through --test 10, or --all');
    process.exit(2);
  }
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: true,
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu'],
  });
  try {
    const results = [];
    for (const [id, fixture] of tests) results.push(await runOne(browser, id, fixture));
    const allPassed = results.every((result) => result.passed && result.fresh_fixture_failed_as_expected);
    console.log(JSON.stringify({ summary: 'simulated workflows', allPassed, count: results.length, results }, null, 2));
    process.exitCode = allPassed ? 0 : 1;
  } finally {
    await browser.close();
  }
}

if (process.argv[1] && process.argv[1].endsWith('simulate.mjs')) {
  main().catch((error) => {
    console.error(JSON.stringify({ error: String(error?.message || error) }));
    process.exit(3);
  });
}
