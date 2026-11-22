// t05-file-manager check. Drives a demo file manager with real UI
// actions: sort, search, create folder, navigate, rename through a
// dialog (type a check-chosen name, Save; Cancel leaves the name;
// an empty name is rejected), delete with confirm, move between
// folders, and rename a folder through the same dialog. Asserts the
// real DOM list, crumbs, and status after each step.
// Prints one JSON result line. Exit 0 on pass, 1 on fail.
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { launchBrowser, nowIso } from '../lib/browser.mjs';
import { serveDir } from '../lib/server.mjs';

const testDir = path.dirname(fileURLToPath(import.meta.url));
const testName = path.basename(testDir);
const startedAt = nowIso();
const started = Date.now();
const failures = [];
const details = {};
// H1: novel names carry a per-run random suffix. Fixed strings let a
// future fixture hardcode the expected names and pass without applying
// the typed rename, so the names must be ones the fixture cannot know.
const runTagFile = Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
const runTagFolder = Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
const novelFile = 'field-notes-' + runTagFile + '.txt';
const novelFolder = 'Old Files ' + runTagFolder;
const novelFolderTreeId = 'tree-' + novelFolder.toLowerCase().replace(/\s+/g, '-');
details.novelFileName = novelFile;
details.novelFolderName = novelFolder;

let browser = null;
let closeServer = null;
try {
  let fixtureUrl;
  if (process.env.FIXTURE_BASE_URL) {
    fixtureUrl = process.env.FIXTURE_BASE_URL.replace(/\/$/, '') + '/' + testName + '/fixture.html';
  } else {
    const server = await serveDir(testDir);
    fixtureUrl = server.url + '/fixture.html';
    closeServer = server.close;
  }
  browser = await launchBrowser();
  const page = await browser.newPage();
  await page.goto(fixtureUrl);
  const text = (sel) => page.textContent(sel);
  const items = () => page.$$eval('#list .item', (els) => els.map((e) => e.dataset.name));
  const expectItems = async (wanted, what) => {
    const got = await items();
    if (JSON.stringify(got) !== JSON.stringify(wanted)) {
      failures.push(what + ': got [' + got.join(', ') + '], want [' + wanted.join(', ') + ']');
    }
  };
  const dialogVisible = () => page.isVisible('#rename-dialog');
  const expectDialogHidden = async (what) => {
    if (await dialogVisible()) failures.push(what + ': rename dialog still visible');
  };
  const expectDialogOpen = async (prefill, what) => {
    if (!(await dialogVisible())) failures.push(what + ': rename dialog not visible');
    const got = await page.inputValue('#rename-input');
    if (got !== prefill) failures.push(what + ': rename prefill is "' + got + '", want "' + prefill + '"');
  };

  await expectItems(['budget.csv', 'notes.txt', 'photo.jpg', 'video.mp4'], 'initial Home order');
  if ((await text('#status')).trim() !== 'Home: 4 items') failures.push('initial status wrong');
  await page.selectOption('#sort', 'size-desc');
  if ((await items())[0] !== 'video.mp4') failures.push('size-desc first item is not video.mp4');
  await page.selectOption('#sort', 'name');
  if ((await items())[0] !== 'budget.csv') failures.push('name sort first item is not budget.csv');
  await page.selectOption('#sort', 'size-asc');
  if ((await items())[0] !== 'notes.txt') failures.push('size-asc first item is not notes.txt');
  await page.selectOption('#sort', 'name');
  await page.fill('#search', 'photo');
  await expectItems(['photo.jpg'], 'search photo');
  await page.fill('#search', '');
  await expectItems(['budget.csv', 'notes.txt', 'photo.jpg', 'video.mp4'], 'after clearing search');
  await page.click('#new-folder-btn');
  await expectItems(['Archive', 'budget.csv', 'notes.txt', 'photo.jpg', 'video.mp4'], 'after new folder');
  if (!(await page.$('#tree-archive'))) failures.push('tree button for Archive missing');
  await page.dblclick('#list .item[data-name="Archive"]');
  if ((await text('#crumbs')).trim() !== 'Archive') failures.push('crumbs wrong inside Archive');
  if (!(await page.isVisible('#empty'))) failures.push('empty state missing in Archive');
  if ((await text('#status')).trim() !== 'Archive: 0 items') failures.push('Archive status wrong');
  await page.click('#tree-home');
  if ((await text('#crumbs')).trim() !== 'Home') failures.push('crumbs wrong back in Home');
  await page.click('#list .item[data-name="budget.csv"]');
  await page.click('#rename-btn');
  await expectDialogOpen('budget.csv', 'rename dialog for cancel check');
  if (!(await items()).includes('budget.csv')) failures.push('budget.csv gone while rename dialog open');
  if ((await items()).includes('budget2.csv')) failures.push('budget2.csv present before rename applied');
  await page.fill('#rename-input', 'budget2.csv');
  await page.click('#rename-cancel');
  await expectDialogHidden('after rename cancel');
  if (!(await items()).includes('budget.csv')) failures.push('budget.csv missing after rename cancel');
  if ((await items()).includes('budget2.csv')) failures.push('budget2.csv present after rename cancel');
  // Empty rename: submitting an empty name must change nothing, show
  // the error, and leave the dialog open.
  await page.click('#rename-btn');
  await expectDialogOpen('budget.csv', 'rename dialog for empty check');
  await page.fill('#rename-input', '');
  await page.click('#rename-save');
  if (!(await items()).includes('budget.csv')) failures.push('budget.csv missing after empty rename');
  if (!(await page.isVisible('#rename-dialog'))) failures.push('rename dialog closed on empty name');
  if (!(await page.isVisible('#rename-error'))) failures.push('empty rename error not shown');
  // H2: visibility alone passes a fixture that shows the wrong message,
  // so assert the exact error text too.
  const emptyError = ((await text('#rename-error')) || '').trim();
  if (emptyError !== 'Name cannot be empty.') failures.push('empty rename error text wrong: "' + emptyError + '"');
  await page.click('#rename-cancel');
  await expectDialogHidden('after cancelling the empty rename');
  // Whitespace-only rename: the fixture trims, so a name of only spaces
  // is empty and must be rejected with the same error, dialog open.
  await page.click('#rename-btn');
  await expectDialogOpen('budget.csv', 'rename dialog for whitespace check');
  await page.fill('#rename-input', '   ');
  await page.click('#rename-save');
  if (!(await items()).includes('budget.csv')) failures.push('budget.csv missing after whitespace-only rename');
  if (!(await page.isVisible('#rename-dialog'))) failures.push('rename dialog closed on whitespace-only name');
  if (!(await page.isVisible('#rename-error'))) failures.push('whitespace-only rename error not shown');
  const wsError = ((await text('#rename-error')) || '').trim();
  if (wsError !== 'Name cannot be empty.') failures.push('whitespace-only rename error text wrong: "' + wsError + '"');
  await page.click('#rename-cancel');
  await expectDialogHidden('after cancelling the whitespace-only rename');
  // Real rename of a file: the typed novel name must appear. The
  // name is one the fixture cannot know in advance, so a rename that
  // ignored the typed input cannot pass.
  await page.click('#list .item[data-name="notes.txt"]');
  await page.click('#rename-btn');
  await expectDialogOpen('notes.txt', 'rename dialog for notes.txt');
  if (!(await items()).includes('notes.txt')) failures.push('notes.txt gone while rename dialog open');
  if ((await items()).includes(novelFile)) failures.push(novelFile + ' present before rename applied');
  await page.fill('#rename-input', novelFile);
  await page.click('#rename-save');
  await expectDialogHidden('after file rename');
  if ((await items()).includes('notes.txt')) failures.push('notes.txt still present after rename');
  if (!(await items()).includes(novelFile)) failures.push(novelFile + ' missing after rename');
  await page.click('#list .item[data-name="photo.jpg"]');
  await page.click('#delete-btn');
  if (!(await page.isVisible('#confirm'))) failures.push('delete confirm not shown');
  if (!(await text('#confirm-text')).includes('Delete photo.jpg?')) failures.push('confirm text wrong');
  await page.click('#confirm-no');
  if ((await items()).length !== 5) failures.push('cancelled delete changed the list');
  await page.click('#list .item[data-name="photo.jpg"]');
  await page.click('#delete-btn');
  await page.click('#confirm-yes');
  await expectItems(['Archive', 'budget.csv', novelFile, 'video.mp4'], 'after delete');
  await page.click('#list .item[data-name="video.mp4"]');
  await page.click('#move-btn');
  await page.selectOption('#move-target', 'Archive');
  await page.click('#move-ok');
  await expectItems(['Archive', 'budget.csv', novelFile], 'Home after moving video out');
  await page.click('#tree-archive');
  await expectItems(['video.mp4'], 'Archive after moving video in');
  // Rename the folder while it still holds video.mp4. The typed name
  // is padded with spaces: the fixture must trim it. The contents
  // must survive the rename.
  await page.click('#tree-home');
  await page.click('#list .item[data-name="Archive"]');
  await page.click('#rename-btn');
  await expectDialogOpen('Archive', 'rename dialog for folder');
  if (!(await items()).includes('Archive')) failures.push('Archive gone while rename dialog open');
  if ((await items()).includes(novelFolder)) failures.push(novelFolder + ' present before folder rename applied');
  await page.fill('#rename-input', '  ' + novelFolder + '  ');
  await page.click('#rename-save');
  await expectDialogHidden('after folder rename');
  if (!(await items()).includes(novelFolder)) failures.push(novelFolder + ' missing after folder rename');
  if ((await items()).includes('Archive')) failures.push('Archive still present after folder rename');
  const treeBtn = await page.$('#' + novelFolderTreeId);
  if (!treeBtn) failures.push('tree button for ' + novelFolder + ' missing');
  else if (((await treeBtn.textContent()) || '').trim() !== novelFolder) {
    failures.push('tree button text wrong for ' + novelFolder);
  }
  await page.click('#' + novelFolderTreeId);
  if ((await text('#crumbs')).trim() !== novelFolder) failures.push('crumbs wrong inside ' + novelFolder);
  await expectItems(['video.mp4'], novelFolder + ' still holds video.mp4 after rename');
  await page.click('#list .item[data-name="video.mp4"]');
  await page.click('#move-btn');
  await page.selectOption('#move-target', 'Home');
  await page.click('#move-ok');
  if ((await items()).length !== 0) failures.push(novelFolder + ' not empty after moving video back');
  await page.click('#tree-home');
  await expectItems(['budget.csv', novelFile, novelFolder, 'video.mp4'], 'Home after moving video back');
  await page.fill('#search', runTagFolder);
  await expectItems([novelFolder], 'search ' + runTagFolder);
  await page.fill('#search', '');
  await page.dblclick('#list .item[data-name="' + novelFolder + '"]');
  if ((await text('#crumbs')).trim() !== novelFolder) failures.push('crumbs wrong inside ' + novelFolder);
  if (!(await page.isVisible('#empty'))) failures.push('empty state missing in ' + novelFolder);
  await page.click('#tree-home');
  // Duplicate name: this demo has no duplicate rule (the rename applies
  // whatever name is typed, trimmed), so renaming a file to a name that
  // already exists must apply verbatim. A fixture that rejects
  // duplicates with an error fails here.
  await page.click('#list .item[data-name="budget.csv"]');
  await page.click('#rename-btn');
  await expectDialogOpen('budget.csv', 'rename dialog for duplicate check');
  await page.fill('#rename-input', 'video.mp4');
  await page.click('#rename-save');
  await expectDialogHidden('after duplicate rename');
  const dupNames = await items();
  if (dupNames.filter((n) => n === 'video.mp4').length !== 2) {
    failures.push('duplicate rename did not apply verbatim: got [' + dupNames.join(', ') + ']');
  }
  if (dupNames.includes('budget.csv')) failures.push('budget.csv still present after duplicate rename');
  details.finalHome = await items();
} catch (err) {
  failures.push(String(err && err.message ? err.message : err));
} finally {
  if (browser) await browser.close();
  if (closeServer) await closeServer();
}

const result = {
  test: testName,
  pass: failures.length === 0,
  failures,
  details,
  started_at: startedAt,
  finished_at: nowIso(),
  elapsed_ms: Date.now() - started,
};
console.log(JSON.stringify(result));
process.exit(result.pass ? 0 : 1);
