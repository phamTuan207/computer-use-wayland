// Offline automated checker for tests/realistic/agy-y2 suite.
// Run: node tests/realistic/agy-y2/check.mjs --fixture <fixtures/test-XX-....html> --test <XX>
// Or:  node tests/realistic/agy-y2/check.mjs --all
import puppeteer from 'puppeteer-core';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const args = process.argv.slice(2);
function argValue(flag) {
  const i = args.indexOf(flag);
  return i >= 0 ? args[i + 1] : undefined;
}

const fixturePath = argValue('--fixture');
const testId = argValue('--test');
const runAll = args.includes('--all');

const EXES = process.env.CU_CHROME_PATH || '/usr/bin/chromium';

export const allFixtures = [
  { id: '01', path: 'tests/realistic/agy-y2/fixtures/test-01-tmux-session.html' },
  { id: '02', path: 'tests/realistic/agy-y2/fixtures/test-02-network-settings.html' },
  { id: '03', path: 'tests/realistic/agy-y2/fixtures/test-03-photo-editor.html' },
  { id: '04', path: 'tests/realistic/agy-y2/fixtures/test-04-email-compose.html' },
  { id: '05', path: 'tests/realistic/agy-y2/fixtures/test-05-spreadsheet-chart.html' },
  { id: '06', path: 'tests/realistic/agy-y2/fixtures/test-06-video-call.html' },
  { id: '07', path: 'tests/realistic/agy-y2/fixtures/test-07-file-manager.html' },
  { id: '08', path: 'tests/realistic/agy-y2/fixtures/test-08-devtools.html' },
  { id: '09', path: 'tests/realistic/agy-y2/fixtures/test-09-notes-sync.html' },
  { id: '10', path: 'tests/realistic/agy-y2/fixtures/test-10-ide-debug.html' },
];

export async function verifyTest(page, id) {
  return await page.evaluate((testId) => {
    const failures = [];
    const state = {};

    function check(cond, msg) {
      if (!cond) failures.push(msg);
    }

    if (testId === '01') {
      const sessName = document.querySelector('#active-session-name')?.textContent?.trim();
      const statusInd = document.querySelector('#status-indicator')?.textContent?.trim();
      const winCount = document.querySelector('#window-count')?.textContent?.trim();
      const paneCount = document.querySelector('#pane-count')?.textContent?.trim();
      const tab0 = document.querySelector('#window-tab-0')?.textContent?.trim();
      const tab1 = document.querySelector('#window-tab-1')?.textContent?.trim();
      const savedMsg = document.querySelector('#saved-status-message')?.textContent?.trim();
      const isSavedVisible = document.querySelector('#saved-status-message')?.classList?.contains('visible');
      const terminalOutput = Array.from(document.querySelectorAll('.pane-content')).map(el => el.textContent || '').join('\n');

      state.sessionName = sessName;
      state.status = statusInd;
      state.windowCount = winCount;
      state.paneCount = paneCount;
      state.savedMessage = savedMsg;

      check(sessName === 'deploy', `Expected active session 'deploy', got '${sessName}'`);
      check(statusInd && statusInd.includes('deploy: Attached'), `Expected status to contain 'deploy: Attached', got '${statusInd}'`);
      check(winCount === '2', `Expected window count 2, got '${winCount}'`);
      check(paneCount === '2', `Expected pane count 2, got '${paneCount}'`);
      check(tab0 && tab0.includes('0:bash'), `Expected tab 0 '0:bash', got '${tab0}'`);
      check(tab1 && tab1.includes('1:worker-logs'), `Expected tab 1 '1:worker-logs', got '${tab1}'`);
      check(isSavedVisible, 'Saved status message is not visible');
      check(savedMsg && savedMsg.includes('Session deploy saved with 2 windows'), `Saved message mismatch, got '${savedMsg}'`);

    } else if (testId === '02') {
      const wifiStatus = document.querySelector('#wifi-toggle-status')?.textContent?.trim();
      const connectedSsid = document.querySelector('#connected-network-name')?.textContent?.trim();
      const connBadge = document.querySelector('#wifi-connection-badge')?.textContent?.trim();
      const cafeFree = document.querySelector('#item-cafefree');
      const btStatus = document.querySelector('#bt-toggle-status')?.textContent?.trim();
      const mxMaster = document.querySelector('#paired-item-mx-master');
      const summarySsid = document.querySelector('#summary-wifi-ssid')?.textContent?.trim();
      const summaryMetered = document.querySelector('#summary-wifi-metered')?.textContent?.trim();
      const summaryBt = document.querySelector('#summary-bt-device')?.textContent?.trim();
      const toast = document.querySelector('#settings-status-toast');
      const toastText = toast?.textContent?.trim();
      const isToastActive = toast?.classList?.contains('active');

      state.wifiStatus = wifiStatus;
      state.connectedSsid = connectedSsid;
      state.btStatus = btStatus;
      state.summaryMetered = summaryMetered;

      check(wifiStatus === 'Enabled', `Expected Wi-Fi 'Enabled', got '${wifiStatus}'`);
      check(connectedSsid === 'HomeFiber-5G', `Expected connected SSID 'HomeFiber-5G', got '${connectedSsid}'`);
      check(connBadge === 'Connected', `Expected connection badge 'Connected', got '${connBadge}'`);
      check(!cafeFree, 'Network CafeFree was not forgotten (still exists in DOM)');
      check(btStatus === 'Enabled', `Expected Bluetooth 'Enabled', got '${btStatus}'`);
      check(!!mxMaster && mxMaster.textContent.includes('MX Master 3S'), 'Device MX Master 3S not paired');
      check(summarySsid === 'HomeFiber-5G', `Expected summary SSID 'HomeFiber-5G', got '${summarySsid}'`);
      check(summaryMetered === 'Yes', `Expected summary metered 'Yes', got '${summaryMetered}'`);
      check(summaryBt === 'MX Master 3S', `Expected summary BT 'MX Master 3S', got '${summaryBt}'`);
      check(isToastActive, 'Settings toast notification is not active');
      check(toastText && toastText.includes('Network settings applied successfully'), `Toast mismatch, got '${toastText}'`);

    } else if (testId === '03') {
      const filename = document.querySelector('#current-filename')?.textContent?.trim();
      const dimW = document.querySelector('#dim-width')?.textContent?.trim();
      const dimH = document.querySelector('#dim-height')?.textContent?.trim();
      const cropRatio = document.querySelector('#active-crop-ratio')?.textContent?.trim();
      const filterName = document.querySelector('#active-filter-name')?.textContent?.trim();
      const brightness = document.querySelector('#brightness-display')?.textContent?.trim();
      const rotation = document.querySelector('#rotation-angle')?.textContent?.trim();
      const banner = document.querySelector('#export-status-banner');
      const bannerText = banner?.textContent?.trim();
      const isBannerActive = banner?.classList?.contains('active');
      const formatDisplay = document.querySelector('#dialog-format-display')?.textContent?.trim();
      const dimsDisplay = document.querySelector('#dialog-dimensions-display')?.textContent?.trim();

      state.filename = filename;
      state.dimensions = `${dimW}x${dimH}`;
      state.filter = filterName;
      state.rotation = rotation;
      state.brightness = brightness;

      check(filename === 'sunset.jpg', `Expected file 'sunset.jpg', got '${filename}'`);
      check(cropRatio === '4:3', `Expected crop ratio '4:3', got '${cropRatio}'`);
      check(filterName === 'Vivid', `Expected filter 'Vivid', got '${filterName}'`);
      check(brightness === '0', `Expected brightness '0' (undone), got '${brightness}'`);
      check(rotation === '90 deg', `Expected rotation '90 deg', got '${rotation}'`);
      check(dimW === '750', `Expected width '750', got '${dimW}'`);
      check(dimH === '1000', `Expected height '1000', got '${dimH}'`);
      check(formatDisplay === 'PNG', `Expected format display 'PNG', got '${formatDisplay}'`);
      check(dimsDisplay && dimsDisplay.includes('750 x 1000'), `Expected dialog dims '750 x 1000', got '${dimsDisplay}'`);
      check(isBannerActive, 'Export banner is not active');
      check(bannerText && bannerText.includes('Image exported: sunset.png (750x1000, PNG)'), `Banner mismatch, got '${bannerText}'`);

    } else if (testId === '04') {
      const sentCount = document.querySelector('#sent-folder-counter')?.textContent?.trim();
      const draftsCount = document.querySelector('#drafts-folder-counter')?.textContent?.trim();
      const sentRow = document.querySelector('#sent-row-1');
      const sentRowDisplay = sentRow ? window.getComputedStyle(sentRow).display : 'none';
      const toast = document.querySelector('#toast-alert');
      const toastText = toast?.textContent?.trim();
      const isToastVisible = toast?.classList?.contains('visible');

      state.sentCount = sentCount;
      state.draftsCount = draftsCount;
      state.sentRowDisplay = sentRowDisplay;

      check(sentCount === '13', `Expected Sent count 13, got '${sentCount}'`);
      check(draftsCount === '0', `Expected Drafts count 0, got '${draftsCount}'`);
      check(sentRow && sentRowDisplay !== 'none', 'Sent table row #sent-row-1 is not visible');
      check(sentRow && sentRow.textContent.includes('team@example.com'), 'Sent row missing recipient team@example.com');
      check(sentRow && sentRow.textContent.includes('Q4 report'), 'Sent row missing subject Q4 report');
      check(isToastVisible, 'Sent toast alert is not visible');
      check(toastText && toastText.includes('Email sent to team@example.com with attachment report.pdf'), `Toast mismatch, got '${toastText}'`);

    } else if (testId === '05') {
      const a1 = document.querySelector('#cell-input-a1')?.value?.trim();
      const b1 = document.querySelector('#cell-input-b1')?.value?.trim();
      const a2 = document.querySelector('#cell-input-a2')?.value?.trim();
      const b2 = document.querySelector('#cell-input-b2')?.value?.trim();
      const a3 = document.querySelector('#cell-input-a3')?.value?.trim();
      const b3 = document.querySelector('#cell-input-b3')?.value?.trim();
      const a4 = document.querySelector('#cell-input-a4')?.value?.trim();
      const b4 = document.querySelector('#cell-input-b4')?.value?.trim();
      const valB5 = document.querySelector('#cell-value-b5')?.textContent?.trim();
      const valB6 = document.querySelector('#cell-value-b6')?.textContent?.trim();
      const chartSvg = document.querySelector('#sales-bar-svg');
      const chartTitle = document.querySelector('#chart-title-text')?.textContent?.trim();
      const toast = document.querySelector('#sheet-status-toast');
      const toastText = toast?.textContent?.trim();
      const isToastActive = toast?.classList?.contains('active');

      state.a1 = a1;
      state.b4 = b4;
      state.valB5 = valB5;
      state.valB6 = valB6;
      state.chartTitle = chartTitle;

      check(a1 === 'Month', `Expected A1 'Month', got '${a1}'`);
      check(b1 === 'Sales', `Expected B1 'Sales', got '${b1}'`);
      check(a2 === 'Jan' && b2 === '1200', `Expected Jan 1200, got '${a2} ${b2}'`);
      check(a3 === 'Feb' && b3 === '1500', `Expected Feb 1500, got '${a3} ${b3}'`);
      check(a4 === 'Mar', `Expected A4 'Mar', got '${a4}'`);
      check(b4 === '1800', `Expected B4 corrected to '1800', got '${b4}'`);
      check(valB5 === '4500', `Expected Total (B5) '4500', got '${valB5}'`);
      check(valB6 === '1500.00', `Expected Average (B6) '1500.00', got '${valB6}'`);
      check(!!chartSvg, 'Bar chart SVG #sales-bar-svg not found');
      check(chartTitle === 'Q1 Regional Sales', `Expected chart title 'Q1 Regional Sales', got '${chartTitle}'`);
      check(isToastActive, 'Sheet status toast is not active');
      check(toastText && toastText.includes('Sheet saved: Total=4500, Average=1500.00, Chart=Q1 Regional Sales'), `Toast mismatch, got '${toastText}'`);
    } else if (testId === '06') {
      const room = document.querySelector('#room-name-display')?.textContent?.trim();
      const partCount = document.querySelector('#participant-count')?.textContent?.trim();
      const statusBadge = document.querySelector('#call-status-badge')?.textContent?.trim();
      const micStatus = document.querySelector('#mic-status-indicator')?.textContent?.trim();
      const camStatus = document.querySelector('#cam-status-indicator')?.textContent?.trim();
      const handStatus = document.querySelector('#hand-raise-indicator')?.textContent?.trim();
      const chatText = document.querySelector('#chat-message-list')?.textContent || '';
      const toast = document.querySelector('#call-summary-toast');
      const toastText = toast?.textContent?.trim();
      const isToastActive = toast?.classList?.contains('active');

      state.room = room;
      state.participants = partCount;
      state.status = statusBadge;
      state.mic = micStatus;
      state.cam = camStatus;

      check(room === 'Sprint Planning', `Expected room 'Sprint Planning', got '${room}'`);
      check(partCount === '4', `Expected 4 participants, got '${partCount}'`);
      check(statusBadge === 'Connected', `Expected call status 'Connected', got '${statusBadge}'`);
      check(micStatus === 'Unmuted', `Expected mic 'Unmuted', got '${micStatus}'`);
      check(camStatus === 'Camera On', `Expected camera 'Camera On', got '${camStatus}'`);
      check(handStatus === 'Hand Raised', `Expected hand 'Hand Raised', got '${handStatus}'`);
      check(chatText.includes('Ready for updates'), 'Chat message missing in chat list');
      check(isToastActive, 'Call summary toast is not active');
      check(toastText && toastText.includes('Meeting Sprint Planning: 4 participants, audio active, video active'), `Toast mismatch, got '${toastText}'`);

    } else if (testId === '07') {
      const selectedCount = document.querySelector('#selected-files-count')?.textContent?.trim();
      const trashCount = document.querySelector('#trash-counter')?.textContent?.trim();
      const archiveCount = document.querySelector('#folder-count-archive')?.textContent?.trim();
      const name1 = document.querySelector('#file-name-img1')?.textContent?.trim();
      const name5 = document.querySelector('#file-name-img5')?.textContent?.trim();
      const row4 = document.querySelector('#file-row-img4');
      const isRow4Visible = row4 && !row4.classList.contains('hidden');
      const newFolderItem = document.querySelector('#folder-item-processed');
      const toast = document.querySelector('#inventory-summary-toast');
      const toastText = toast?.textContent?.trim();
      const isToastActive = toast?.classList?.contains('active');

      state.name1 = name1;
      state.name5 = name5;
      state.trash = trashCount;
      state.archive = archiveCount;

      check(name1 === 'photo-2026-01.jpg', `Expected file 1 'photo-2026-01.jpg', got '${name1}'`);
      check(name5 === 'photo-2026-05.jpg', `Expected file 5 'photo-2026-05.jpg', got '${name5}'`);
      check(archiveCount && archiveCount.includes('3 files'), `Expected Archive to have '3 files', got '${archiveCount}'`);
      check(trashCount === '0', `Expected Trash count '0', got '${trashCount}'`);
      check(isRow4Visible, 'File row img4 is not restored and visible');
      check(!!newFolderItem, 'Custom folder item #folder-item-processed not found');
      check(isToastActive, 'Inventory summary toast is not active');
      check(toastText && toastText.includes('Root: 5 files, Archive: 3 files, Trash: 0 files, Folder Processed created'), `Toast mismatch, got '${toastText}'`);

    } else if (testId === '08') {
      const panel = document.querySelector('#devtools-panel');
      const isExpanded = panel?.classList?.contains('expanded');
      const logCount = document.querySelector('#console-log-count')?.textContent?.trim();
      const netVisible = document.querySelector('#network-visible-count')?.textContent?.trim();
      const logOutput = document.querySelector('#console-output-log')?.textContent || '';
      const checkoutRow = document.querySelector('#row-req-api-checkout');
      const isCheckoutVisible = checkoutRow && !checkoutRow.classList.contains('hidden');
      const stylesRow = document.querySelector('#row-req-styles');
      const isStylesHidden = stylesRow && stylesRow.classList.contains('hidden');
      const toast = document.querySelector('#devtools-toast-summary');
      const toastText = toast?.textContent?.trim();
      const isToastActive = toast?.classList?.contains('active');

      state.isExpanded = isExpanded;
      state.logCount = logCount;
      state.netVisible = netVisible;

      check(isExpanded, 'DevTools panel is not expanded');
      check(logCount === '1', `Expected console log count '1', got '${logCount}'`);
      check(netVisible === '3', `Expected visible network count '3', got '${netVisible}'`);
      check(logOutput.includes('ready'), 'Console log does not contain "ready"');
      check(isCheckoutVisible, 'Filtered row /api/v1/checkout is not visible');
      check(isStylesHidden, 'Unmatched row styles.css was not filtered out');
      check(isToastActive, 'DevTools summary toast is not active');
      check(toastText && toastText.includes('DevTools diagnostics: 1 logs, 3 filtered network rows, error 404 checked'), `Toast mismatch, got '${toastText}'`);

    } else if (testId === '09') {
      const totalNotes = document.querySelector('#notes-total-counter')?.textContent?.trim();
      const titleShopping = document.querySelector('#note-item-title-shopping')?.textContent?.trim();
      const titleConflict = document.querySelector('#note-item-title-conflict')?.textContent?.trim();
      const archivedItem = document.querySelector('#note-item-archived-draft');
      const toast = document.querySelector('#sync-summary-toast');
      const toastText = toast?.textContent?.trim();
      const isToastActive = toast?.classList?.contains('active');

      state.totalNotes = totalNotes;
      state.titleShopping = titleShopping;
      state.titleConflict = titleConflict;

      check(totalNotes === '3', `Expected total notes '3', got '${totalNotes}'`);
      check(titleShopping === 'Shopping', `Expected note 'Shopping', got '${titleShopping}'`);
      check(titleConflict === 'Shopping - Phone Copy', `Expected note 'Shopping - Phone Copy', got '${titleConflict}'`);
      check(!archivedItem, 'Outdated note #note-item-archived-draft was not deleted');
      check(isToastActive, 'Sync summary toast is not active');
      check(toastText && toastText.includes('Sync completed: 3 notes active, Shopping and Shopping - Phone Copy verified'), `Toast mismatch, got '${toastText}'`);

    } else if (testId === '10') {
      const fileName = document.querySelector('#active-file-name')?.textContent?.trim();
      const bpCount = document.querySelector('#breakpoint-count-indicator')?.textContent?.trim();
      const statusBadge = document.querySelector('#debug-state-badge')?.textContent?.trim();
      const watchTotal = document.querySelector('#watch-val-total')?.textContent?.trim();
      const watchGrand = document.querySelector('#watch-val-grand-total')?.textContent?.trim();
      const stackList = document.querySelector('#call-stack-list')?.textContent || '';
      const toast = document.querySelector('#debug-toast-summary');
      const toastText = toast?.textContent?.trim();
      const isToastActive = toast?.classList?.contains('active');

      state.file = fileName;
      state.breakpoints = bpCount;
      state.status = statusBadge;
      state.watchTotal = watchTotal;
      state.watchGrand = watchGrand;

      check(fileName === 'app.js', `Expected file 'app.js', got '${fileName}'`);
      check(bpCount === '2', `Expected 2 breakpoints, got '${bpCount}'`);
      check(statusBadge === 'Stopped', `Expected debug status 'Stopped', got '${statusBadge}'`);
      check(watchTotal === '250', `Expected watch total '250', got '${watchTotal}'`);
      check(watchGrand === '250', `Expected watch grandTotal '250', got '${watchGrand}'`);
      check(stackList.includes('renderSummary (line 16)'), 'Call stack missing renderSummary');
      check(isToastActive, 'Debug toast summary is not active');
      check(toastText && toastText.includes('Debug session complete: watched total=250, breakpoints=2, final line 16'), `Toast mismatch, got '${toastText}'`);

    } else {
      failures.push(`Unknown test id: ${testId}`);
    }

    return {
      passed: failures.length === 0,
      failures,
      score: failures.length === 0 ? 1 : 0,
      state,
    };
  }, id);
}

export async function verifyOneFixture(browser, relPath, id) {
  const start = Date.now();
  const absolute = path.resolve(process.cwd(), relPath);
  const fileUrl = pathToFileURL(absolute).href;
  const page = await browser.newPage();
  try {
    await page.goto(fileUrl);
    const result = await verifyTest(page, id);
    const totalMs = Date.now() - start;
    return {
      test: id,
      fixture: relPath,
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
  if (!fixturePath && !runAll) {
    console.error('Usage: node tests/realistic/agy-y2/check.mjs --fixture <path> --test <id>');
    console.error('       node tests/realistic/agy-y2/check.mjs --all');
    process.exit(2);
  }

  const browser = await puppeteer.launch({
    executablePath: EXES,
    headless: true,
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu'],
  });

  try {
    if (runAll) {
      const results = [];
      let allPassed = true;
      for (const item of allFixtures) {
        const res = await verifyOneFixture(browser, item.path, item.id);
        results.push(res);
        if (!res.passed) allPassed = false;
      }
      console.log(JSON.stringify({ summary: 'all tests evaluated', allPassed, count: results.length, results }, null, 2));
      process.exit(allPassed ? 0 : 1);
    } else {
      const res = await verifyOneFixture(browser, fixturePath, testId || '01');
      console.log(JSON.stringify(res, null, 2));
      process.exit(res.passed ? 0 : 1);
    }
  } finally {
    await browser.close();
  }
}

// Only run main when called directly
const isDirectCall = process.argv[1] && (
  process.argv[1].endsWith('check.mjs') ||
  process.argv[1].endsWith('check.js')
);
if (isDirectCall) {
  main().catch((err) => {
    console.error(JSON.stringify({ error: String(err && err.message || err), timestamp: Date.now() }));
    process.exit(3);
  });
}
