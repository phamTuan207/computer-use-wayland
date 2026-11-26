# Zen Browser sidebar control without vision: folders, workspaces, pinned tabs

Research report, 2026-11-27. Scope: moving tabs into Zen folders, moving
tabs between Zen workspaces, pinning/unpinning, and reordering pinned
tabs, all programmatically, with no screenshots and no mouse. Method:
five parallel research strands (sessionstore schema, offline edit route,
live chrome APIs, community tools, a last30days sweep for recent
sources), checked against the Zen source tree (zen-browser/desktop),
Mozilla documentation, and the tools that already edit these files.
Claims that rest on a single secondary source or could not be confirmed
are marked UNVERIFIED. Two prototype tools were built alongside this
report in `improvements/zen-sidebar/` (see section 4).

## Headline answer

The fast path exists and it is not the sessionstore. Zen's sidebar
objects are reachable live, in the running browser, through Zen's own
chrome managers (`gZenWorkspaces`, `gZenFolders`,
`gZenPinnedTabManager`) by executing JavaScript in Marionette's chrome
context on the Marionette listener the laptop's Zen already exposes
(127.0.0.1:2828). The exact "move tab into folder" call Zen's own menu
uses is `folder.addTabs(tabs)`; workspace switching is
`gZenWorkspaces.changeWorkspaceWithID(uuid)`; pinning is stock
`gBrowser.pinTab/unpinTab`, which Zen intercepts and re-files itself.
No restart, no vision, milliseconds per operation. For bulk
reorganization while Zen is closed, the offline target is
`zen-sessions.jsonlz4` (Zen 1.18 and later), not
`sessionstore.jsonlz4`; that route is proven by the actively
maintained zen-browser-flake and by zenform, a small alpha tool built
for exactly this file, and is ranked second because it costs a full
browser restart and carries a silent-fallback failure mode.

## 1. Where the state actually lives

### 1.1 `zen-sessions.jsonlz4` is the Zen sidebar store (Zen 1.18+)

Since the 1.18 "Window Sync & Recovery" rework, Zen keeps its own
session file in the profile root: `zen-sessions.jsonlz4`, with backups
in `zen-sessions-backup/`. Zen's own recovery documentation treats this
file (renamed alongside `sessionstore.jsonlz4`) as the store for
windows and Spaces state. The schema below is from zenform, a
third-party tool that parses real files (last checked against Zen
1.24.3b); the format is undocumented, so treat field lists as
version-sensitive. (The 1.18 dating itself rests on Zen's recovery
docs and issue history; the schema below is the part verified
against real files and source.)

- Top level is flat and global (not nested under windows):
  `{lastCollected, tabs, folders, splitViewData, groups, spaces}`.
  Open unpinned tabs are in this file too.
- Workspaces: `spaces[]`, each `{uuid, name, theme, containerTabId, ...}`.
- Folder definitions: `folders[]`, each `{id, name, collapsed,
  workspaceId, prevSiblingInfo, emptyTabIds, ...}`, plus a parallel
  `groups[]` with the same ids holding the Firefox tab-group view
  `{id, name, color, collapsed, ...}`. Folder order among siblings is
  a linked list: `prevSiblingInfo` is null for the first folder, else
  `{"type": "group", "id": <previous folder id>}`.
- Tabs: `tabs[]` in positional order (Essentials first, then each
  folder's placeholder plus its pins, then the rest). A tab entry
  carries `entries` (history) with a 1-based `index`, `pinned`
  (boolean, true for any pin including Essentials), `zenEssential`
  (boolean), `zenWorkspace` (workspace uuid, null for Essentials,
  which span workspaces), `groupId` (the folder the tab is in, absent
  for a loose tab), `zenSyncId` (`<ms-timestamp>-<uuid>`, a stable id
  to select tabs by), `zenStaticLabel`, and
  `_zenPinnedInitialState` (the pin's home entry).
- Folder membership is a per-tab field (`groupId`), in both session
  files. There is no member list inside the folder object, except the
  folder's `emptyTabIds`: every folder owns an empty placeholder tab
  (`about:blank`, `zenIsEmpty`) that must be kept or recreated.
- Live folders (RSS/GitHub) are separate: `zen-live-folders.jsonlz4`.
  Zen also writes `zen-space-routing.jsonlz4` for space routing
  (reported by the flake's documentation).

### 1.2 `sessionstore.jsonlz4` still exists, with Zen fields patched in

Firefox's file keeps the classic windows/tabs layout. Zen patches
Firefox's TabState collection to add per-tab fields:
`zenWorkspace` (from the tab's `zen-workspace-id` attribute),
`zenEssential`, `zenPinnedId`, `zenPinnedEntry`, `zenIsEmpty`, plus
stock `groupId`, `pinned`, `hidden`, `userContextId`. Window group
definitions there are Firefox's `{id, name, color, collapsed}`.
Consequence: an offline edit that moves a tab between workspaces may
need to keep both files consistent; whether Zen rebuilds one from the
other at startup is a laptop-test question (section 6).

File lifecycle that matters for editing: `sessionstore.jsonlz4` in
the profile root exists only while the browser is closed; while it
runs, live state is `sessionstore-backups/recovery.jsonlz4` (rewritten
about every 15 s) with `recovery.baklz4` and `previous.jsonlz4` behind
it. Zen's fallback chain for `zen-sessions.jsonlz4` (per a Zen
maintainer in issue #11994) is: the session file, then a recovery
backup, then a clean backup, then older timestamped backups in
`zen-sessions-backup/`, then Firefox's own recovery. A malformed edit
therefore does not crash Zen; it silently resurrects an older layout.
The symptom of a rejected edit is "my old layout came back".

### 1.3 The mozlz4 container (both files)

8-byte magic `mozLz40\0`, a 4-byte little-endian uncompressed size,
then one raw LZ4 block of UTF-8 JSON. It is not the LZ4 frame format
(the stock `lz4` CLI refuses these files) and there is no checksum or
integrity field. In Python: `lz4.block` from the `lz4` package, with
one trap that our own first test run hit: `lz4.block.compress` must be
called with `store_size=False`, because the size must appear exactly
once, in the header; python-lz4's default 4-byte store-size prefix
emits it a second time inside the payload and makes the file
unreadable as mozlz4.

### 1.4 Two more stores to know about

- Zen's commit history repeatedly references a folder database
  ("restoring folders from saved SQL backup database", "the folder
  database"), and migration tooling makes a separate database backup.
  Which SQLite file this is, and whether it can resurrect folder state
  over `zen-sessions.jsonlz4` edits, is UNVERIFIED from public
  sources. This is the top risk to the offline route for folders
  specifically, and a required laptop check.
- Historical workspace storage (ZenWorkspacesStorage) went from a
  `zen-workspaces/Workspaces.json` file to SQLite tables in
  `places.sqlite` (`zen_workspaces`) before spaces moved into the
  session file in the Dec 2025 cross-window sync rework. Whether the
  SQLite table still exists in the laptop's build as a cache is
  UNVERIFIED.
- Prefs hold pointers, not definitions: `zen.workspaces.active`
  holds the active workspace uuid. Zen Sync can sync Spaces and
  folders since 1.22b but is off by default; if it is enabled on the
  laptop profile it could fight local edits (state on the target
  machine UNVERIFIED).

## 2. Ranked routes

### Route 1 (fastest, recommended): live Marionette chrome-context JS

Transport: Marionette protocol on 127.0.0.1:2828, already running on
the laptop's Zen. With Mozilla's `marionette_driver` (or the minimal
stdlib client in `zen_live.py`): `set_context(CONTEXT_CHROME)`, then
`execute_async_script(script, sandbox="system")`. Chrome context is
documented by Mozilla as "a privileged scope where you can access
things like the Firefox UI itself"; the `system` sandbox tag gives
the system principal. The built client requests `sandbox="system"`
as a protocol parameter on every execute; that the laptop's build
accepts it and grants the principal is an end-to-end check the
`introspect` op performs (laptop test step 2), not something the fake
server test can show. Zen's discussion forum confirms there is no
public API and that chrome-privileged access to `gZenFolders` is the
route (discussion #11824).

The managers (per-browser-window chrome globals, registered in
`src/zen/zen.globals.mjs`; signatures confirmed against the
zen-browser/desktop source at commit b12eaefb, permalinks in
Sources, unless noted; paths drift on main, so introspection on the
actual build is the authority):

Workspaces, `gZenWorkspaces` (`nsZenWorkspaces`,
`src/zen/spaces/ZenSpaceManager.mjs`):
- `activeWorkspace` (uuid string, backed by pref `zen.workspaces.active`)
- `getWorkspaces()` returns the workspace records (`.uuid`, `.containerTabId` verified)
- `changeWorkspaceWithID(workspaceId)` returns a Promise; switching is
  serialized internally and animated, so always await it and never
  fire overlapping switches
- `createAndSaveWorkspace(name, icon, dontChange, containerTabId, options)` (async)
- `workspaceElement(workspaceId)` returns the workspace DOM element
  (`.pinnedTabsContainer`, `.tabsContainer`)
- `getEssentialsSection(container = 0)`, `getCurrentEssentialsContainer()`
- `promiseInitialized`: await before operating
- `moveTabToWorkspace(tab, workspaceUuid)`: verified in an older
  commit (ebdc936), UNVERIFIED in the current snapshot. The built
  tool feature-detects it and refuses to guess a fallback, because
  setting the `zen-workspace-id` attribute alone skips container
  placement and the manager's bookkeeping (Zen's own folder-to-space
  code also moves the element into the target workspace's
  `pinnedTabsContainer` and flushes tab state).

Folders, `gZenFolders` (`nsZenFolders`, `src/zen/folders/ZenFolders.mjs`)
and the `zen-folder` element (`src/zen/folders/ZenFolder.mjs`). Zen
folders subclass Firefox tab groups (the element inherits
`MozTabbrowserTabGroup`) with nesting (max depth pref
`zen.folders.max-subfolders`, default 5), workspace scoping, and
pinned-area placement on top:
- `gZenFolders.createFolder(tabs = [], options = {})` returns the
  folder element. Options seen in source: `label`, `collapsed`,
  `workspaceId`, `insertBefore`, `insertAfter`, `id`. Side effects:
  it pins every tab passed in (a newer PR adds unpinned folders
  behind the `zen.folders.auto-pin` pref), creates the folder's
  `about:blank` placeholder tab, and flushes tab state.
- Move tabs into a folder: `folder.addTabs(tabs)`. This is exactly
  what Zen's "Move to folder" menu dispatches (`group.addTabs` on the
  selected or context tab).
- `folder.delete()`, `folder.unpackTabs()` (ungroup, keep tabs),
  `folder.createSubfolder()`, `folder.rename()`. Caution: stock
  `gBrowser.removeTabGroup(group)` closes all member tabs; whether
  Zen's `folder.delete()` closes or unpacks is UNVERIFIED, and the
  menu having separate Delete and Unpack entries suggests Delete is
  destructive. Do not script Delete until tested.
- Move a whole folder to another workspace:
  `gZenFolders.changeFolderToSpace(folder, workspaceId, {hasDndSwitch})`,
  which re-parents the folder, rewrites `zen-workspace-id` on member
  tabs and groups, flushes state, and switches workspace unless told
  not to. On a live session, always pass the no-switch option:
  switching the visible workspace mid-task is a user-visible
  disruption.
- Enumerate folders: `gBrowser.tabGroups.filter(g => g.isZenFolder)`,
  optionally filtered by
  `g.getAttribute("zen-workspace-id") === gZenWorkspaces.activeWorkspace`.
- Remove one tab from a folder: no Zen-specific method found;
  `gBrowser.ungroupTab(tab)` is the Firefox-level operation.
  UNVERIFIED whether Zen's folder bookkeeping (activeTabs, pins
  storage) fully follows a raw ungroupTab; laptop test required.

Pinning and Essentials:
- `gBrowser.pinTab(aTab, options)` / `gBrowser.unpinTab(aTab, options)`
  (Mozilla Tabbrowser API; options currently only `metricsContext`).
  In Zen, pin/unpin is intercepted by `gZenFolders.handleTabPin` /
  `handleTabUnpin` and `gZenPinnedTabManager`, so the stock call is
  the correct entry point and Zen re-files the tab itself.
- Pinned order is tab order: reorder with
  `gBrowser.moveTabTo(element, {tabIndex})` (or `{elementIndex}`),
  with `forceUngrouped` available to keep a pinned tab out of groups.
  Name drift warning: `gBrowser.moveTabToGroup` was renamed
  `moveTabToExistingGroup` in current Mozilla code; which name a
  given Zen build exposes must be introspected.
- Essentials are a separate tier: a pinned tab with the
  `zen-essential` attribute, living in a dedicated essentials section
  (`gZenWorkspaces.getEssentialsSection(containerTabId)`), global
  across workspaces unless pref `zen.workspaces.separate-essentials`
  is set, capped by pref `zen.tabs.essentials.max` (default 12).
  Manager: `gZenPinnedTabManager` (`src/zen/tabs/ZenPinnedTabManager.mjs`),
  with pins persisted as records (uuid, url, title, isEssential,
  workspaceUuid, parentUuid, position, containerTabId) via
  `ZenPinnedTabsStorage`. No direct `addToEssentials(tab)` method
  could be verified from web sources: UNVERIFIED. The fastest way to
  settle it is prototype introspection in a chrome script on the
  laptop (the built tool's `introspect` op does exactly this).

Persistence: changes made through the manager APIs flow into
SessionStore and `ZenPinnedTabsStorage` automatically (that is how
the UI persists), but writes are asynchronous and debounced; Zen
forces immediate flushes at deliberate-action points via
`gBrowser.TabStateFlusher.flush(tab.linkedBrowser)`. A scripted
change followed by a hard kill can lose the change. So a mutation op
is not done when the call returns: flush the affected tabs (or wait
out the debounce) and re-run `list` to confirm the new state before
reporting success; the quit-and-relaunch check in the test plan only
catches a lost write after the fact. Raw DOM or attribute edits
bypass the managers' caches and can be re-filed or reverted on the
next switch or save: always go through the manager calls above.
There is also no live rollback: the only restorable backup of the
session files is a closed-browser file copy, so a live batch on a
profile that matters either accepts the risk explicitly or is
scheduled inside a planned restart window where a backup was taken
first.

Two transport caveats. First, Marionette allows one session per
instance, and the repo's existing BiDi tooling deliberately never
attaches to the owner's live session; whether a Marionette session on
2828 coexists cleanly with the BiDi session on 9222 is UNVERIFIED and
must be tested on the throwaway profile first. Second, a community
tool already ships this exact transport for Zen: zen-devtools-mcp (a
Zen fork of Mozilla's Firefox DevTools MCP) with `--connect-existing`
(Marionette, port 2828) and `--enable-privileged-context`
(`evaluate_privileged_script`, Zen prefs), requiring
`MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1`. It is an alternative driver for
the same payloads, and a useful cross-check.

### Route 2: offline `zen-sessions.jsonlz4` edit, then restart

Proven prior art:
- zenform (PyPI, v0.1.0, 2026-11-20, tested on Zen 1.24.3b) manages
  Essentials, pinned folders and pinned tabs by editing this file,
  with dump / plan / apply / rollback / doctor commands. Its apply
  refuses to run while Zen is open, backs up first, validates shape,
  reads back after writing, and auto-restores on a failed read-back.
  Limits: alpha (0 stars, 4 commits, macOS-tested), manages one named
  workspace, and never edits open tabs.
- zen-browser-flake (Nix/Home Manager, widely starred, actively
  maintained) declaratively manages Spaces, pins with folder
  grouping, containers and live folders by the same pipeline on every
  system activation: check `.parentlock` via lsof, decompress, edit
  with jq, recompress, restore backup on failure. Its option docs
  are the best public schema reference for pins (`id` UUIDv4,
  `folderParentId`, `isGroup` rows). Nix-only delivery.
- arc2zen / arc2zen-node generate a complete `zen-sessions.jsonlz4`
  from Arc's sidebar file; after the write Zen starts with the right
  Spaces, pins and folder hierarchy, which proves wholesale file
  generation is honored. One failure report in that project (a grey
  window after writing while Zen was not fully closed, stale
  `.parentlock` implicated) underlines the closure requirement.

What the edit can express: a tab's workspace (set `zenWorkspace`),
folder membership (set or clear `groupId`, keeping the folder's
`workspaceId` consistent with the tab's), pin flags (`pinned`,
`zenEssential`), and pinned order (the positional order of `tabs[]`).
Folder reordering means repairing the `prevSiblingInfo` linked list;
folder creation means also creating the placeholder tab and the
parallel `groups[]` entry. All doable, all validated in the built
tool where the risk is mechanical (section 4).

Safe procedure (matches zenform's and the flake's discipline):
Pre-flight: check whether Zen Sync covers Spaces and folders on
this profile (Settings, Sync). Sync (1.22b+) can reconcile sidebar
state in either direction on the first restart after an edit. If it
is on, turn it off, or keep the machine offline through the first
post-edit restart; the same applies after a rollback, so a sync
push cannot resurrect the pre-rollback state.
1. Note the Zen version; express the edit as data (tab id to target),
   never hand-edit JSON in place.
2. Quit Zen properly (Quit, not closing windows), so all windows'
   state is saved.
3. Prove closure: no zen process remains, `.parentlock` is not held,
   `sessionstore.jsonlz4` is present in the profile root.
4. Back up outside the profile, with hashes: `zen-sessions.jsonlz4`,
   `sessionstore.jsonlz4`, and the whole `zen-sessions-backup/` and
   `sessionstore-backups/` folders. Keep the existing pre-cleanup
   backup on the laptop untouched.
5. Decompress (block recipe, section 1.3), parse, snapshot counts.
6. Edit minimally: change only the target fields; copy target
   workspace/folder ids from objects already in the file; never
   invent UUIDs; preserve ordering conventions elsewhere.
7. Validate referential integrity and hard-fail on any problem:
   every `zenWorkspace` exists in `spaces[]`; every `groupId` exists
   in `folders[]`/`groups[]`; every folder's `workspaceId` exists;
   `prevSiblingInfo` chains terminate without cycles; every
   `emptyTabIds` entry has its tab; no duplicate `zenSyncId`; tab
   counts differ only as intended.
8. Recompress to a temp file, decompress it back, deep-compare with
   the intended JSON; only then atomically replace. If
   `sessionstore.jsonlz4` was also edited, move `recovery.jsonlz4`
   and `recovery.baklz4` aside (backed up) so the edited file is
   authoritative. Do the equivalent for the zen-sessions fallback
   chain: move the contents of `zen-sessions-backup/` aside into
   the outside backup set, so a rejected edit cannot silently
   resurrect the old layout from a timestamped backup; restore
   them on rollback.
9. Restart and verify with the BiDi tab list plus a sidebar check;
   watch for the silent-fallback symptom in both files (old layout
   back means the edit was rejected, for the zen-sessions file
   specifically if the fallback backups were left in place).
10. Rollback with Zen closed: restore the timestamped backups over
    both session files (and the recovery files and
    `zen-sessions-backup/` contents if moved), restart, confirm
    the original layout.

Gate: do not use Route 2 on a real profile until laptop probes (c)
and (d) in section 5 are answered. Probe (c) settles whether the
two session files must be edited together; until it is answered,
every offline move on a real profile is an uncontrolled experiment
in which file wins at startup. Probe (d) identifies the folder
database; until it is identified and added to the backup set,
folder-move rollback is not guaranteed, because that database may
be able to resurrect folder state over both the edit and the
rollback.

Speed profile: the edit itself is sub-second to seconds for a few-MB
JSON (the flake runs the whole pipeline as a routine activation
step; no sourced timing measurements exist, so treat numbers as
UNVERIFIED until measured). The real cost is the quit-plus-restart
cycle and losing live page state (forms, media, calls, anything not
yet flushed). Right tool for batch reorganization (dozens of moves
amortized over one restart, or a planned maintenance window); wrong
tool for one-off moves while the user is browsing.

Zen-specific fragility to respect: Zen's issue history in exactly
this area is rough (issue #11994, tabs and workspaces lost on the
1.18 upgrade; "Folder tree breaks with live folders fetch" #12509;
repeated restore fixes for folder ordering, empty-tab position, and
pinned parent placement in the commit history). The restore code is
sensitive to ordering and parent consistency in undocumented ways;
preserve every invariant of the original file, not just the fields
being changed. Zen 1.24.3b also actively repairs space and pinned-tab
container assignments on sync, so container ids must stay consistent
in edits.

### Route 3: WebDriver BiDi chrome scope (future, needs a relaunch flag)

Up to Firefox 147, BiDi `script.evaluate` reached content realms
only. Firefox 148 added initial chrome-scope support:
`browsingContext.getTree` accepts the vendor parameter
`moz:scope: "chrome"` and returns chrome contexts usable with
`script.evaluate` / `script.callFunction`, but only when the browser
was started with `--remote-allow-system-access` (the MCP tools use
the `MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1` environment equivalent).
Current Zen is built on a Firefox version well past 148 (release
coverage for 1.24.3b lists a Firefox 160-series base; another
secondary source puts some current builds on Firefox 158), so the
capability should exist in the build; whether the laptop's launcher sets the flag is
UNVERIFIED, and the default launcher almost certainly does not. If a
future launcher change adds the flag, the same JS payloads as Route 1
run over the existing BiDi connection and the separate Marionette
session caveat disappears. Until then, Route 1 is the no-relaunch
path.

### Rejected routes

- WebExtensions `tabGroups` / `tabs.group()`: operates on Firefox
  native tab groups only. Zen folders and workspaces are Zen chrome
  objects with no extension API, and extension tab APIs are
  demonstrably unreliable in Zen (issue #7062: tab indices offset by
  pinned tabs, tabs disappearing from extension listings since
  1.8b). The extension grouping semantics also unpin pinned tabs
  first, which is destructive for Zen's pinned-folder layout.
- Keyboard shortcuts: workspace switching exists (on this machine
  Ctrl+Alt+Left/Right; switch-to-workspace 1-10 is unbound by
  default), but no shortcut moves a tab into a folder or between
  workspaces. Keystroke driving is also the slow, focus-sensitive
  path this research was asked to replace.
- `sessionstore.jsonlz4`-only editing for Zen state: wrong file
  since 1.18 (section 1.1), and its fallback chain silently discards
  edits when the recovery files are newer.

## 3. What a runner should call, per operation

| Operation | Route 1 call (live) | Route 2 edit (offline) |
|---|---|---|
| List state | `gZenWorkspaces.getWorkspaces()`; `gBrowser.tabGroups.filter(g => g.isZenFolder)`; `gBrowser.tabs` with `zen-workspace-id`, `pinned`, `zen-essential`, `tab.group` | Parse `spaces[]`, `folders[]`, `tabs[]` |
| Move tab to workspace | `gZenWorkspaces.moveTabToWorkspace(tab, uuid)` (feature-detect; UNVERIFIED in current build) | Set tab `zenWorkspace` (and keep `sessionstore.jsonlz4` consistent) |
| Move tab into folder | `folder.addTabs([tab])` | Set tab `groupId` (folder `workspaceId` must equal tab workspace) |
| Remove tab from folder | `gBrowser.ungroupTab(tab)` (bookkeeping UNVERIFIED) | Clear tab `groupId` |
| Create folder | `gZenFolders.createFolder(tabs, {label})` (pins the tabs) | Create `folders[]` + `groups[]` entries, placeholder tab, repair `prevSiblingInfo` |
| Move folder to workspace | `gZenFolders.changeFolderToSpace(folder, uuid, {hasDndSwitch})` (pass the no-switch option on a live session) | Set folder `workspaceId` plus every member tab's `zenWorkspace` |
| Pin / unpin | `gBrowser.pinTab(tab)` / `gBrowser.unpinTab(tab)` | Set `pinned` and move the entry to the pinned-region boundary of `tabs[]`; unpinning an Essential is refused offline (its `zenWorkspace` is null) |
| Reorder pinned | `gBrowser.moveTabTo(tab, {tabIndex})` | Reorder the movable pins in `tabs[]` (Essentials and folder placeholders keep their positions) |
| Switch workspace | `await gZenWorkspaces.changeWorkspaceWithID(uuid)` | Set pref `zen.workspaces.active` (next start only) |
| Essentials add/remove | UNVERIFIED (introspect `gZenPinnedTabManager` on the laptop) | Set `zenEssential`, `zenWorkspace: null`, move to the Essentials-first position in `tabs[]` |

## 4. What was built (prototypes, not integrated)

In `improvements/zen-sidebar/`, Ponytail-sized and stdlib-first:

- `zen_live.py` (Route 1): a minimal Marionette wire-protocol client
  (stdlib socket only, no pip dependency; every execute requests
  `sandbox="system"` and every response id is checked against its
  request) plus the JS payloads for
  `introspect`, `list`, `switch-workspace`, `move-workspace`,
  `create-folder`, `move-folder`, `leave-folder`,
  `move-folder-space`, `pin`, `unpin`, `move-tab`. Tabs are selected
  by URL substring resolved inside the chrome JS, so indexes never go
  stale between calls. Every payload feature-detects its Zen API and
  returns an error instead of guessing when a build differs;
  `move-workspace` refuses to fall back to raw attribute edits when
  `moveTabToWorkspace` is absent. `introspect` dumps the three
  managers' prototype method names, which settles the UNVERIFIED
  signatures (above all the Essentials entry point) in one call.
- `zen_sessions.py` (Route 2): mozlz4 read/write (with the
  `store_size=False` trap handled), `dump`, and the operations
  `move-workspace`, `move-folder`, `pin`, `unpin`, `reorder-pins`
  over `zen-sessions.jsonlz4`. Dry-run by default. `--apply` refuses
  to run while Zen appears to be running with the profile: the
  `.parentlock` probe tests BOTH lock domains (Gecko holds the
  profile lock with POSIX fcntl record locks, which a flock-only
  probe cannot see on Linux) and a /proc scan checks for a process
  using the profile. Validation covers referential integrity,
  `prevSiblingInfo` cycles, tab-vs-folder workspace consistency,
  and the positional rule (pinned region first); an apply is
  rejected only for problems the edit introduces, not pre-existing
  ones. Pin and unpin move the entry to the pinned-region boundary,
  because `tabs[]` order is positional; unpinning an Essential and
  moving a foldered tab across workspaces are refused. Backups go
  OUTSIDE the profile (default `zen-editor-backups/` next to the
  profile, `--backup-dir` overrides) and cover both session files
  and both backup folders, with a sha256 manifest and the Zen
  version hint recorded; the backup copy is parse-verified before
  anything is written. The write is atomic with fsync, the running
  check is repeated immediately before it, the result is read back
  and deep-compared, and the original is restored if verification
  fails. Needs the Python `lz4` package; everything else is stdlib.
- `test_zen_sidebar.py`: 20 unittest cases, all passing
  (python3 -m unittest, about 0.2 s on the build VM): mozlz4
  round-trip, bad-magic and truncated-file rejection, integrity
  validation (dangling ids, sibling cycles, tab/folder workspace
  mismatch), the state operations including every refusal case and
  the positional pin moves, CLI dry-run vs apply against a
  synthetic profile (backup with manifest created outside the
  profile, file changed only on apply), the backup-restore path
  when post-write verification fails, the POSIX-lock refusal (a
  subprocess holds `.parentlock` with lockf, as Gecko does), JS
  payload contents, and the Marionette client against an in-process
  fake server (handshake, split frames, error frames, mismatched
  response ids). No real profile is touched by the tests.
- `README.md`: usage for both tools.

## 5. Prototype test plan for the laptop worker (throwaway profile)

Prerequisites: a throwaway Zen profile (fresh profile dir, a handful
of tabs across 2 workspaces, 1 folder, 2 pinned tabs, 1 Essential),
Zen launched on that profile with the usual launcher flags
(Marionette 2828, BiDi 9222). Measure wall-clock time for every step;
the point of the fast path is the timing comparison against the
vision-driven runner.

1. Baseline: `zen_live.py list` on the throwaway profile; save the
   JSON. Confirm the workspace uuids, folder id, and per-tab
   workspace/folder/pin fields match what the sidebar shows.
2. Introspection: `zen_live.py introspect`; record the Zen version
   and the three method lists. Settles: does
   `gZenWorkspaces.moveTabToWorkspace` exist in this build, is the
   group-move named `moveTabToGroup` or `moveTabToExistingGroup`,
   and what the Essentials entry point is (look for an
   essentials-named method or the menu item's oncommand).
3. Live moves, in order, verifying with `list` after each and timing
   each call: switch-workspace; move-workspace on an open tab;
   create-folder with 2 tabs; move-folder for a third tab;
   leave-folder; pin and unpin; move-tab to reorder two pinned tabs;
   move-folder-space to move the folder and its tabs together.
   Pass criteria: every call returns without error, `list` reflects
   each change, and the sidebar visually agrees on a spot check.
4. Persistence: quit Zen gracefully on the throwaway profile,
   relaunch, `list` again. Pass criteria: the final state from step 3
   survives the restart unchanged. Also confirm the BiDi session on
   9222 was undisturbed by the Marionette session during step 3.
5. Offline route: with Zen closed, `zen_sessions.py --profile
   <throwaway> dump`; then one move-workspace and one move-folder
   with `--apply`; relaunch and compare against the plan. Then the
   rollback: restore the backup from the outside-profile backup
   directory (default `zen-editor-backups/` next to the profile),
   relaunch, confirm the original layout.
6. Hostile probes (throwaway profile only): (a) hand-edit one tab's
   `zenWorkspace` to a nonexistent uuid, relaunch, record what Zen
   does (whole-file fallback, tab dropped, or tab demoted); (b) same
   with a dangling `groupId`; (c) edit only `zen-sessions.jsonlz4`
   without touching `sessionstore.jsonlz4` and check whether the two
   files' workspace assignments agree after one restart; (d) check
   whether a folder-related SQLite file exists in the profile and
   whether its contents change after a folder move made in the UI
   (the folder-database question from section 1.4); (e) confirm
   whether editing `sessionstore.jsonlz4` alone is overridden by
   `recovery.jsonlz4` on this build.
7. Report back: timings per operation for Route 1 vs the vision
   runner's per-operation cost, the introspection results, and the
   hostile-probe outcomes. Those results decide whether Route 1
   becomes the runner's sidebar path and which fallbacks Route 2
   needs.

## 6. Risks and open questions

- Internal API drift is the norm: within about a year Zen renamed
  `ZenWorkspaces` to `gZenWorkspaces`, moved `src/zen/workspaces/` to
  `src/zen/spaces/`, and refactored the pinned manager's event set;
  Mozilla renamed `moveTabToGroup` to `moveTabToExistingGroup`. Any
  tool must feature-detect per build (both built tools do) and be
  re-introspected after Zen upgrades.
- UNVERIFIED items that the laptop test must settle: existence and
  signature of `moveTabToWorkspace` in the current build; the
  Essentials add/remove entry point; `folder.delete()` semantics;
  whether raw `ungroupTab` keeps Zen's folder bookkeeping;
  Marionette session coexistence with the live BiDi session; the
  folder SQL database's file and authority; whether the `places.sqlite`
  `zen_workspaces` table persists in this build; whether
  `zen-sessions.jsonlz4` and `sessionstore.jsonlz4` edits must be
  kept in sync; dangling-reference behavior; whether Zen Sync is
  enabled on the laptop profile; whether the raw Marionette
  protocol-3 command names and the `sandbox="system"` parameter
  behave on the laptop's build exactly as Mozilla's docs describe
  (the `introspect` op is the check).
- Zen's restore path has a documented history of losing tabs,
  folders and workspaces on upgrades (issues #11994, #12422, #12443,
  #12493, #12509). Offline edits should be treated as surgery:
  backups outside the profile, one change class at a time, verify
  after restart.
- Security posture: Marionette chrome execution is full
  system-principal control of the profile (arbitrary file and XPCOM
  access). Keep the listener bound to localhost only, and treat
  attaching to the owner's live session (versus a worker profile) as
  a policy decision, not a technical one. Leaving Marionette enabled
  also sets `navigator.webdriver=true`, which some sites react to.
- The last30days sweep's community coverage was partial (Reddit
  unreachable from the research network, X/YouTube unconfigured), so
  "no community discussion found" for these topics is itself
  UNVERIFIED; the findings above rest on source code, official docs,
  and the tools' own documentation rather than forum consensus.

## Sources (selection)

- Zen source (snapshot b12eaefb): src/zen/spaces/ZenSpaceManager.mjs,
  src/zen/folders/ZenFolders.mjs, src/zen/folders/ZenFolder.mjs,
  src/zen/tabs/ZenPinnedTabManager.mjs, src/zen/zen.globals.mjs,
  src/browser/components/sessionstore/TabState-sys-mjs.patch
  (github.com/zen-browser/desktop). Commit-pinned permalinks for
  the two load-bearing files:
  github.com/zen-browser/desktop/blob/b12eaefb/src/zen/folders/ZenFolders.mjs
  and
  github.com/zen-browser/desktop/blob/b12eaefb/src/zen/spaces/ZenSpaceManager.mjs
  (paths on main have since drifted; the pinned commit is the
  citation)
- Zen docs, Window Sync and recovery: docs.zen-browser.app/user-manual/window-sync
- zenform (schema, offline tool): pypi.org/project/zenform,
  github.com/cathal-killeen/zenform (docs/session-format.md)
- zen-browser-flake: github.com/0xc000022070/zen-browser-flake,
  zen-browser-flake.nshard.com
- arc2zen write-up: crixu.blog/2026/05/26/migrating-from-arc-to-zen-browser-and-bringing-everything-with-me/
- Zen issue #11994 (fallback chain, 1.18 session loss):
  github.com/zen-browser/desktop/issues/11994
- Zen discussion #11824 (no public API, chrome route):
  github.com/zen-browser/desktop/discussions/11824
- Zen issue #7062 (extension tab APIs broken in Zen):
  github.com/zen-browser/desktop/issues/7062
- Mozilla Tabbrowser API (pinTab, moveTabTo, addTabGroup):
  firefox-source-docs.mozilla.org/browser/components/tabbrowser/docs/api.html
- Marionette driver docs (contexts, system sandbox):
  firefox-source-docs.mozilla.org/python/marionette_driver.html,
  github.com/mozilla/gecko-dev testing/marionette/client/docs/basics.rst
- Firefox 148 WebDriver newsletter (BiDi chrome scope,
  --remote-allow-system-access): fxdx.dev/firefox-webdriver-newsletter-148/
- zen-devtools-mcp: glama.ai/mcp/servers/simon-ami/zen-devtools-mcp
- mus-uc-devtools: jsr.io/@f3liz/mus-uc-devtools
- mozlz4 format: deepwiki.com/jscher2000/Firefox-File-Utilities,
  fx5sec.github.io/guides/browser-artifacts/sessions/,
  gist.github.com/Tblue/62ff47bef7f894e92ed5
- DeepWiki Zen indexes: deepwiki.com/zen-browser/desktop
  (3.1 workspaces, 3.3 tab organization, 3.3.1 pinned and essentials)
