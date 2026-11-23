// Offline automated simulator for tests/realistic/agy-y2 suite.
// Drives test steps with real puppeteer clicks and typing, asserts DOM directly.
// Fails on untouched fixture and passes after simulated execution.
// Usage: node tests/realistic/agy-y2/simulate.mjs --test 01
// Or:    node tests/realistic/agy-y2/simulate.mjs --all
import puppeteer from 'puppeteer-core';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { verifyTest } from './check.mjs';

const args = process.argv.slice(2);
function argValue(flag) {
  const i = args.indexOf(flag);
  return i >= 0 ? args[i + 1] : undefined;
}

const testId = argValue('--test') || '01';
const runAll = args.includes('--all');
const EXES = process.env.CU_CHROME_PATH || '/usr/bin/chromium';

const fixtureMap = {
  '01': 'tests/realistic/agy-y2/fixtures/test-01-tmux-session.html',
  '02': 'tests/realistic/agy-y2/fixtures/test-02-network-settings.html',
  '03': 'tests/realistic/agy-y2/fixtures/test-03-photo-editor.html',
  '04': 'tests/realistic/agy-y2/fixtures/test-04-email-compose.html',
  '05': 'tests/realistic/agy-y2/fixtures/test-05-spreadsheet-chart.html',
  '06': 'tests/realistic/agy-y2/fixtures/test-06-video-call.html',
  '07': 'tests/realistic/agy-y2/fixtures/test-07-file-manager.html',
  '08': 'tests/realistic/agy-y2/fixtures/test-08-devtools.html',
  '09': 'tests/realistic/agy-y2/fixtures/test-09-notes-sync.html',
  '10': 'tests/realistic/agy-y2/fixtures/test-10-ide-debug.html',
};

const testSimulators = {
  '01': async (page) => {
    // 1. Create session deploy
    await page.click('#btn-new-session');
    await page.waitForSelector('#session-modal.open');
    await page.type('#input-session-name', 'deploy');
    await page.click('#btn-create-session');

    // 2. Split horizontal
    await page.click('#btn-split-horizontal');

    // 3. Run uptime command
    await page.type('#pane-terminal-input', 'uptime');
    await page.click('#btn-send-command');

    // 4. Create new window and rename to worker-logs
    await page.click('#btn-new-window');
    await page.click('#btn-rename-window');
    await page.waitForSelector('#rename-window-modal.open');
    await page.$eval('#input-window-name', el => el.value = '');
    await page.type('#input-window-name', 'worker-logs');
    await page.click('#btn-confirm-rename');

    // 5. Split vertical in window 1
    await page.click('#btn-split-vertical');

    // 6. Mistake: kill pane
    await page.click('#btn-kill-pane');

    // 7. Recovery: undo pane
    await page.click('#btn-undo-pane');

    // 8. Detach and reattach
    await page.click('#btn-detach-session');
    await page.waitForSelector('#session-overview');
    await page.click('#btn-attach-deploy');

    // 9. Save session state
    await page.click('#btn-save-session-state');
  },

  '02': async (page) => {
    // 1. Toggle Wi-Fi on
    await page.click('#toggle-wifi');

    // 2. Connect HomeFiber-5G
    await page.click('#network-row-homefiber');
    await page.waitForSelector('#wifi-auth-modal.active');
    await page.type('#input-wifi-password', 'HomeKey2026');
    await page.click('#btn-connect-wifi');

    // 3. Forget CafeFree
    await page.click('#btn-manage-known-networks');
    await page.click('#btn-forget-cafefree');

    // 4. Switch to Bluetooth tab, scan, and pair MX Master 3S
    await page.click('#nav-tab-bluetooth');
    await page.click('#btn-scan-bt-devices');
    await page.click('#btn-pair-mx-master');

    // 5. Toggle Bluetooth off then on
    await page.click('#toggle-bluetooth');
    await page.click('#toggle-bluetooth');

    // 6. Return to Wi-Fi, open properties, enable metered connection
    await page.click('#nav-tab-wifi');
    await page.click('#btn-network-properties');
    await page.waitForSelector('#network-properties-panel.active');
    await page.click('#toggle-metered-connection');
    await page.click('#btn-save-wifi-properties');

    // 7. View status overview and apply
    await page.click('#nav-tab-status');
    await page.click('#btn-apply-network-settings');
  },

  '03': async (page) => {
    // 1. Select and load sunset.jpg
    await page.click('#file-item-sunset');
    await page.click('#btn-load-photo');

    // 2. Crop to 4:3
    await page.click('#tool-tab-crop');
    await page.click('#btn-ratio-4-3');
    await page.click('#btn-apply-crop');

    // 3. Apply Vivid filter
    await page.click('#tool-tab-filters');
    await page.click('#btn-filter-vivid');

    // 4. Adjust brightness +20 and undo
    await page.click('#tool-tab-adjust');
    await page.click('#btn-brightness-plus');
    await page.click('#btn-undo-adjust');

    // 5. Rotate 90 deg clockwise
    await page.click('#tool-tab-transform');
    await page.click('#btn-rotate-90-cw');

    // 6. Export as PNG
    await page.click('#btn-open-export');
    await page.waitForSelector('#export-modal.active');
    await page.select('#select-export-format', 'PNG');
    await page.click('#btn-confirm-export');
  },

  '04': async (page) => {
    // 1. Compose email
    await page.click('#btn-compose-mail');
    await page.waitForSelector('#compose-pane.open');
    await page.type('#input-recipient-to', 'team@example.com');
    await page.click('#btn-add-cc');
    await page.type('#input-recipient-cc', 'audit@example.com');
    await page.type('#input-mail-subject', 'Q4 report');
    await page.type('#input-mail-body', 'Attached is the Q4 performance overview.');

    // 2. Attach report.pdf
    await page.click('#btn-open-attachment-picker');
    await page.waitForSelector('#attachment-picker-modal.active');
    await page.click('#file-option-report-pdf');
    await page.click('#btn-confirm-attach-file');

    // 3. Save draft and close
    await page.click('#btn-save-draft-mail');
    await page.click('#btn-close-composer');

    // 4. Reopen draft
    await page.click('#nav-folder-drafts');
    await page.click('#draft-entry-q4');
    await page.waitForSelector('#compose-pane.open');

    // 5. Mistake: remove attachment
    await page.click('#btn-remove-attachment-report');

    // 6. Recovery: re-attach report.pdf
    await page.click('#btn-open-attachment-picker');
    await page.waitForSelector('#attachment-picker-modal.active');
    await page.click('#file-option-report-pdf');
    await page.click('#btn-confirm-attach-file');

    // 7. Send email
    await page.click('#btn-dispatch-send');
  },

  '05': async (page) => {
    // 1. Fill monthly sales table
    await page.type('#cell-input-a1', 'Month');
    await page.type('#cell-input-b1', 'Sales');
    await page.type('#cell-input-a2', 'Jan');
    await page.type('#cell-input-b2', '1200');
    await page.type('#cell-input-a3', 'Feb');
    await page.type('#cell-input-b3', '1500');
    await page.type('#cell-input-a4', 'Mar');

    // 2. Mistake entry: 9800
    await page.type('#cell-input-b4', '9800');

    // 3. Add Total and SUM formula
    await page.type('#cell-input-a5', 'Total');
    await page.click('#cell-input-b5');
    await page.type('#formula-bar-input', '=SUM(B2:B4)');
    await page.click('#btn-commit-formula');

    // 4. Add Average and AVERAGE formula
    await page.type('#cell-input-a6', 'Average');
    await page.click('#cell-input-b6');
    await page.type('#formula-bar-input', '=AVERAGE(B2:B4)');
    await page.click('#btn-commit-formula');

    // 5. Correct mistake in cell B4 from 9800 to 1800
    await page.click('#cell-input-b4');
    await page.$eval('#cell-input-b4', el => el.value = '');
    await page.type('#cell-input-b4', '1800');
    await page.click('#btn-recalculate-sheet');

    // 6. Insert bar chart
    await page.click('#btn-insert-chart-modal');
    await page.waitForSelector('#chart-modal.active');
    await page.select('#select-chart-type', 'Bar');
    await page.click('#btn-render-chart');

    // 7. Update chart title
    await page.click('#input-chart-title');
    await page.$eval('#input-chart-title', el => el.value = '');
    await page.type('#input-chart-title', 'Q1 Regional Sales');
    await page.click('#btn-apply-chart-title');

    // 8. Save sheet
    await page.click('#btn-save-sheet-state');
  },

  '06': async (page) => {
    // 1. Join meeting
    await page.type('#input-meeting-id', 'Sprint Planning');
    await page.type('#input-display-name', 'Alex');
    await page.click('#btn-join-meeting');

    // 2. Toggle mic mute then unmute
    await page.click('#btn-toggle-mic');
    await page.click('#btn-toggle-mic');

    // 3. Toggle cam off then on
    await page.click('#btn-toggle-cam');
    await page.click('#btn-toggle-cam');

    // 4. Share screen then stop
    await page.click('#btn-share-screen');
    await page.waitForSelector('#screenshare-modal.active');
    await page.click('#screen-option-desktop');
    await page.click('#btn-confirm-screenshare');
    await page.click('#btn-stop-screenshare');

    // 5. Raise hand
    await page.click('#btn-raise-hand');

    // 6. Send chat
    await page.click('#btn-open-chat');
    await page.type('#input-chat-message', 'Ready for updates');
    await page.click('#btn-send-chat');

    // 7. Leave and rejoin
    await page.click('#btn-leave-meeting');
    await page.click('#btn-rejoin-meeting');

    // 8. Save summary
    await page.click('#btn-save-call-summary');
  },

  '07': async (page) => {
    // 1. Select 5 files
    await page.click('#checkbox-file-img1');
    await page.click('#checkbox-file-img2');
    await page.click('#checkbox-file-img3');
    await page.click('#checkbox-file-img4');
    await page.click('#checkbox-file-img5');

    // 2. Bulk rename
    await page.click('#btn-open-bulk-rename');
    await page.waitForSelector('#bulk-rename-modal.active');
    await page.type('#input-rename-pattern', 'photo-2026-##');
    await page.click('#btn-apply-bulk-rename');

    // 3. Move 3 files to Archive
    await page.click('#checkbox-file-img1');
    await page.click('#checkbox-file-img2');
    await page.click('#checkbox-file-img3');
    await page.click('#btn-open-move-dialog');
    await page.waitForSelector('#move-modal.active');
    await page.click('#move-target-archive');
    await page.click('#btn-confirm-move');

    // 4. Delete 1 file by mistake
    await page.click('#btn-delete-file-img4');

    // 5. Restore from trash
    await page.click('#nav-folder-trash');
    await page.click('#btn-restore-file-img4');
    await page.click('#nav-folder-root');

    // 6. Create new folder Processed
    await page.click('#btn-new-folder');
    await page.waitForSelector('#new-folder-modal.active');
    await page.type('#input-new-folder-name', 'Processed');
    await page.click('#btn-confirm-create-folder');

    // 7. Generate inventory report
    await page.click('#btn-generate-inventory-report');
  },

  '08': async (page) => {
    // 1. Open DevTools
    await page.click('#devtools-toggle-btn');

    // 2. Console tab command
    await page.click('#tab-console');
    await page.type('#input-console-eval', 'window.appVersion');
    await page.click('#btn-eval-console');

    // 3. Network tab filter
    await page.click('#tab-network');
    await page.type('#input-network-filter', 'api');
    await page.click('#btn-apply-network-filter');

    // 4. Inspect 404 request
    await page.click('#row-req-api-checkout');
    await page.click('#tab-detail-response');
    await page.click('#btn-close-detail');

    // 5. Clear console and re-eval
    await page.click('#tab-console');
    await page.click('#btn-clear-console');
    await page.type('#input-console-eval', "console.log('ready')");
    await page.click('#btn-eval-console');

    // 6. Back to network and save report
    await page.click('#tab-network');
    await page.click('#btn-save-devtools-report');
  },

  '09': async (page) => {
    // 1. Create Shopping note
    await page.click('#btn-create-new-note');
    await page.$eval('#note-editor-title', el => el.value = '');
    await page.type('#note-editor-title', 'Shopping');
    await page.type('#note-editor-body', 'Milk, Eggs, Bread');
    await page.click('#btn-save-note-edit');

    // 2. Device A edit
    await page.click('#tab-device-a');
    await page.type('#note-editor-body', ', Apples');
    await page.click('#btn-stage-device-a');

    // 3. Device B conflicting edit
    await page.click('#tab-device-b');
    await page.$eval('#note-editor-body', el => el.value = '');
    await page.type('#note-editor-body', 'Milk, Eggs, Bread, Bananas, Orange Juice');
    await page.click('#btn-stage-device-b');

    // 4. Trigger cloud sync and keep both
    await page.click('#btn-trigger-cloud-sync');
    await page.waitForSelector('#conflict-resolution-modal.active');
    await page.click('#btn-resolve-keep-both');

    // 5. Rename conflict copy
    await page.click('#note-item-conflict-copy');
    await page.$eval('#note-editor-title', el => el.value = '');
    await page.type('#note-editor-title', 'Shopping - Phone Copy');
    await page.click('#btn-save-note-edit');

    // 6. Delete outdated note
    await page.click('#note-item-archived-draft');
    await page.click('#btn-delete-active-note');

    // 7. Verify primary note and finalize
    await page.click('#note-item-title-shopping');
    await page.click('#btn-finalize-sync-report');
  },

  '10': async (page) => {
    // 1. Open app.js
    await page.click('#file-item-app-js');

    // 2. Set breakpoint line 12
    await page.click('#gutter-line-12');

    // 3. Start debugger
    await page.click('#btn-start-debugger');

    // 4. Step over twice
    await page.click('#btn-step-over');
    await page.click('#btn-step-over');

    // 5. Edit watch total to 250
    await page.click('#btn-open-edit-watch');
    await page.waitForSelector('#edit-watch-modal.active');
    await page.type('#input-watch-override-value', '250');
    await page.click('#btn-confirm-watch-override');

    // 6. Set breakpoint line 16 and continue
    await page.click('#gutter-line-16');
    await page.click('#btn-continue-debugger');

    // 7. Stop debugger
    await page.click('#btn-stop-debugger');

    // 8. Save session
    await page.click('#btn-save-debug-session');
  }
};

async function simulateOne(browser, id, relPath) {
  const start = Date.now();
  const absolute = path.resolve(process.cwd(), relPath);
  const fileUrl = pathToFileURL(absolute).href;

  const page = await browser.newPage();
  try {
    await page.goto(fileUrl);

    // Verify assertion FAILS on untouched fixture
    const untouchedCheck = await verifyTest(page, id);
    if (untouchedCheck.passed) {
      throw new Error(`Integrity error: Test ${id} passed on untouched fixture.`);
    }

    // Run simulator
    const simFn = testSimulators[id];
    if (!simFn) {
      throw new Error(`No simulator defined for test ${id}`);
    }
    await simFn(page);

    // Run verification directly after simulation
    const result = await verifyTest(page, id);
    const totalMs = Date.now() - start;

    return {
      test: id,
      fixture: relPath,
      untouchedFailedAsExpected: !untouchedCheck.passed,
      passed: !!result.passed,
      failures: result.failures || [],
      score: result.score || 0,
      state: result.state || {},
      total_ms: totalMs,
    };
  } finally {
    await page.close();
  }
}

async function main() {
  const browser = await puppeteer.launch({
    executablePath: EXES,
    headless: true,
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu'],
  });

  try {
    if (runAll) {
      const keys = Object.keys(testSimulators);
      const results = [];
      let allPassed = true;
      for (const k of keys) {
        const res = await simulateOne(browser, k, fixtureMap[k]);
        results.push(res);
        if (!res.passed) allPassed = false;
      }
      console.log(JSON.stringify({ summary: 'all simulated', allPassed, count: results.length, results }, null, 2));
      process.exit(allPassed ? 0 : 1);
    } else {
      const res = await simulateOne(browser, testId, fixtureMap[testId]);
      console.log(JSON.stringify(res, null, 2));
      process.exit(res.passed ? 0 : 1);
    }
  } finally {
    await browser.close();
  }
}

main().catch(err => {
  console.error(JSON.stringify({ error: String(err && err.message || err) }));
  process.exit(3);
});
