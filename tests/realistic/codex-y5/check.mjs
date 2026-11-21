// DOM-only end-state assertions for the codex-y5 realistic suite.
// The CLI replays the matching workflow before checking. verifyTest itself only reads the page.
import puppeteer from 'puppeteer-core';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const args = process.argv.slice(2);
function argValue(flag) {
  const index = args.indexOf(flag);
  return index >= 0 ? args[index + 1] : undefined;
}

const fixturePath = argValue('--fixture');
const testId = argValue('--test');
const runAll = args.includes('--all');
const CHROME = process.env.CU_CHROME_PATH || '/usr/bin/chromium';

export const allFixtures = [
  { id: '01', path: 'tests/realistic/codex-y5/fixtures/test-01-git-workflow.html' },
  { id: '02', path: 'tests/realistic/codex-y5/fixtures/test-02-music-player.html' },
  { id: '03', path: 'tests/realistic/codex-y5/fixtures/test-03-password-vault.html' },
  { id: '04', path: 'tests/realistic/codex-y5/fixtures/test-04-maps-directions.html' },
  { id: '05', path: 'tests/realistic/codex-y5/fixtures/test-05-calendar-recurring.html' },
  { id: '06', path: 'tests/realistic/codex-y5/fixtures/test-06-video-editor.html' },
  { id: '07', path: 'tests/realistic/codex-y5/fixtures/test-07-chat-search.html' },
  { id: '08', path: 'tests/realistic/codex-y5/fixtures/test-08-spreadsheet-pivot.html' },
  { id: '09', path: 'tests/realistic/codex-y5/fixtures/test-09-file-search-tag.html' },
  { id: '10', path: 'tests/realistic/codex-y5/fixtures/test-10-extension-settings.html' },
];

export async function verifyTest(page, id) {
  return page.evaluate((testId) => {
    const failures = [];
    const state = {};
    const text = (selector) => document.querySelector(selector)?.textContent?.trim();
    const value = (selector) => document.querySelector(selector)?.value?.trim();
    const check = (condition, message) => { if (!condition) failures.push(message); };
    const equal = (selector, expected) => {
      const actual = text(selector);
      state[selector.slice(1)] = actual;
      check(actual === expected, `Expected ${selector} to be ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
    };

    if (testId === '01') {
      equal('#current-branch', 'feature/cleanup');
      equal('#worktree-status', 'Clean');
      equal('#commit-count', '4');
      equal('#conflict-count', '0');
      equal('#merge-status', 'Merge committed');
      equal('#latest-commit', 'Merge main after resolving config');
      const config = value('#file-config-editor');
      state.config = config;
      check(config === 'mode=preview\nlog=compact', `Expected resolved config, got ${JSON.stringify(config)}`);
      const log = text('#git-log-list') || '';
      const expectedGitLog = 'Merge main after resolving config\nUse compact logs\nAdd preview mode\nInitial commit';
      state.gitLog = log;
      check(log === expectedGitLog, `Expected Git history ${JSON.stringify(expectedGitLog)}, got ${JSON.stringify(log)}`);
      const terminalLog = text('#terminal-output');
      const expectedTerminalLog = '4 Merge main after resolving config\n3 Use compact logs\n2 Add preview mode\n1 Initial commit';
      state.terminalLog = terminalLog;
      check(terminalLog === expectedTerminalLog, `Expected terminal log ${JSON.stringify(expectedTerminalLog)}, got ${JSON.stringify(terminalLog)}`);
    } else if (testId === '02') {
      equal('#playlist-name', 'Morning Focus');
      equal('#playlist-count', '3');
      equal('#playlist-duration', '10:10');
      equal('#shuffle-status', 'Shuffle On');
      equal('#save-status', 'Playlist saved: Morning Focus (3 tracks, 10:10)');
      equal('#playlist-track-list', 'Quiet Circuit\nPaper Planes\nLow Tide');
    } else if (testId === '03') {
      equal('#vault-status', 'Unlocked');
      equal('#vault-entry-count', '1');
      equal('#entry-title-display', 'Research Vault');
      equal('#entry-username-display', 'qa-operator');
      equal('#password-mask', '••••••••••••••');
      equal('#copy-status', 'Password copied');
      equal('#delete-status', 'Entry restored');
      const copied = value('#clipboard-buffer');
      state.copiedPassword = copied;
      check(copied === 'Cedar!9-Glass?', `Expected clipboard buffer to contain the generated password, got ${JSON.stringify(copied)}`);
    } else if (testId === '04') {
      equal('#origin-selected', 'Workshop District');
      equal('#destination-selected', 'Harbor Square');
      equal('#selected-route-summary', 'North Loop | 14.2 km | 24 min | No tolls');
      equal('#saved-route-summary', 'Workshop District to Harbor Square | North Loop | 14.2 km | 24 min | No tolls');
      equal('#route-result-count', '1');
      equal('#avoid-tolls-status', 'Avoid tolls On');
    } else if (testId === '05') {
      equal('#occurrence-count', '4');
      equal('#calendar-summary', '4 of 5 occurrences scheduled');
      equal('#title-1130', 'Design review prep');
      equal('#title-1123', 'Design review');
      equal('#title-1207', 'Design review');
      equal('#title-1214', 'Design review');
      equal('#series-location-summary', 'Room Cedar');
      equal('#delete-status', 'Deleted 2026-12-21');
      const occurrences = text('#occurrence-summary');
      const expectedOccurrences = '2026-11-23 | Design review | Room Cedar\n2026-11-30 | Design review prep | Room Cedar\n2026-12-07 | Design review | Room Cedar\n2026-12-14 | Design review | Room Cedar';
      state.occurrences = occurrences;
      check(occurrences === expectedOccurrences, `Expected occurrence summary ${JSON.stringify(expectedOccurrences)}, got ${JSON.stringify(occurrences)}`);
    } else if (testId === '06') {
      equal('#imported-clip-count', '3');
      equal('#timeline-clip-count', '3');
      equal('#timeline-duration', '19 sec');
      equal('#timeline-order', 'City B-roll (8 sec)\nForest A-roll (5 sec)\nForest A-roll (6 sec)');
      equal('#transition-summary', 'Cross Dissolve between City B-roll and Forest A-roll');
      equal('#export-resolution', '1920x1080');
      equal('#export-frame-rate', '30 fps');
      equal('#export-codec', 'H.264');
      equal('#export-filename', 'harbor-recap.mp4');
      equal('#export-status', 'Export complete: harbor-recap.mp4 (1920x1080, 30 fps, H.264)');
    } else if (testId === '07') {
      equal('#search-result-count', '1');
      equal('#active-message-text', 'Release checklist is ready for review.');
      equal('#active-message-sender', 'Build Bot');
      equal('#active-message-date', '2026-10-12');
      equal('#star-status', 'Starred');
      equal('#forward-status', 'Forwarded to Release Room');
      equal('#forwarded-count', '1');
      equal('#active-room', 'Release Room');
    } else if (testId === '08') {
      equal('#pivot-group-field', 'Category');
      equal('#pivot-value-field', 'Amount');
      equal('#pivot-aggregation', 'Sum');
      equal('#pivot-filter-region', 'South');
      equal('#pivot-row-count', '2');
      equal('#pivot-hardware-total', '900');
      equal('#pivot-software-total', '1400');
      equal('#pivot-grand-total', '2300');
      equal('#pivot-refresh-status', 'Pivot refreshed from 6 rows');
      const editedSource = value('#source-south-hardware');
      state['source-south-hardware'] = editedSource;
      check(editedSource === '900', `Expected #source-south-hardware value to be 900, got ${JSON.stringify(editedSource)}`);
    } else if (testId === '09') {
      equal('#active-folder', 'Reviewed');
      equal('#active-tag-filter', 'Review');
      equal('#visible-file-count', '2');
      equal('#file-name-checklist', 'approved-release-checklist.md');
      equal('#file-name-plan', 'approved-release-plan.md');
      equal('#tag-checklist', 'Review');
      equal('#tag-plan', 'Review');
      equal('#file-location-checklist', 'Reviewed');
      equal('#file-location-plan', 'Reviewed');
      equal('#file-action-status', 'Moved 2 tagged files to Reviewed');
    } else if (testId === '10') {
      equal('#extension-enabled-state', 'Enabled');
      equal('#site-calendar-permission', 'Ask');
      equal('#site-drive-permission', 'Ask');
      equal('#option-notify-state', 'On');
      equal('#option-auto-update-state', 'On');
      equal('#options-save-status', 'Defaults restored');
      equal('#extension-persistence-status', 'State restored after reload');
    } else {
      failures.push(`Unknown test id: ${testId}`);
    }

    return { passed: failures.length === 0, failures, score: failures.length === 0 ? 1 : 0, state };
  }, id);
}

export async function verifyOneFixture(browser, relPath, id, drive = false) {
  const started = performance.now();
  const absolute = path.resolve(process.cwd(), relPath);
  const page = await browser.newPage();
  try {
    await page.goto(pathToFileURL(absolute).href);
    let freshCheck = null;
    if (drive) {
      freshCheck = await verifyTest(page, id);
      if (freshCheck.passed) throw new Error(`Fixture ${id} passed before its workflow ran`);
      const { driveTest } = await import('./simulate.mjs');
      await driveTest(page, id);
    }
    const result = await verifyTest(page, id);
    return {
      test: id,
      fixture: relPath,
      passed: !!result.passed,
      fresh_fixture_failed_as_expected: drive ? !freshCheck.passed : undefined,
      failures: result.failures || [],
      score: result.score || 0,
      state: result.state || {},
      total_ms: Math.round(performance.now() - started),
    };
  } finally {
    await page.close();
  }
}

async function main() {
  if (!fixturePath && !runAll) {
    console.error('Usage: node tests/realistic/codex-y5/check.mjs --fixture <path> --test <id>');
    console.error('       node tests/realistic/codex-y5/check.mjs --all');
    process.exit(2);
  }
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: true,
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu'],
  });
  try {
    if (runAll) {
      const results = [];
      for (const item of allFixtures) results.push(await verifyOneFixture(browser, item.path, item.id, true));
      const allPassed = results.every((result) => result.passed && result.fresh_fixture_failed_as_expected);
      console.log(JSON.stringify({ summary: 'all workflows replayed and checked', allPassed, count: results.length, results }, null, 2));
      process.exitCode = allPassed ? 0 : 1;
      return;
    }
    const result = await verifyOneFixture(browser, fixturePath, testId || '01', true);
    console.log(JSON.stringify(result, null, 2));
    process.exitCode = result.passed && result.fresh_fixture_failed_as_expected ? 0 : 1;
  } finally {
    await browser.close();
  }
}

if (process.argv[1] && process.argv[1].endsWith('check.mjs')) {
  main().catch((error) => {
    console.error(JSON.stringify({ error: String(error?.message || error) }));
    process.exit(3);
  });
}
