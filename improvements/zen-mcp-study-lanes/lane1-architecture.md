# Lane 1: Architecture of spaxe-dev/zen-mcp

Read-only study. Nothing was installed and none of their code was run. The repo
was shallow-cloned for reading only; all findings below are from reading source
files, with file paths and function or symbol names as evidence.

Version note: the owner brief said v0.6.0. The cloned HEAD (branch `main`,
accessed 2026-11-27) is newer: `package.json` says `"version": "0.6.3"` and
`src/shared/brand.ts` sets `SERVER_VERSION = "0.6.3"`,
`BRIDGE_PROTOCOL_VERSION = 2`. All findings describe HEAD 0.6.3, not 0.6.0.

## 1. Connection mechanism

Two loopback channels, no extension, no native messaging host, no CDP, no
WebDriver BiDi, and no direct profile-file control path.

### 1a. Bootstrap/control plane: hand-written Marionette v3 client

- `src/zen/marionette.ts`: `MarionetteClient`, a dependency-free client for
  Firefox's Marionette protocol v3 over a raw TCP socket (`node:net`).
  Default `127.0.0.1:2828` (env `ZEN_MCP_MARIONETTE_HOST`,
  `ZEN_MCP_MARIONETTE_PORT`). Wire format is the standard length-prefixed
  framing (`<bytes>:<json>`), commands sent as `[0, id, name, params]`
  (`sendRaw`), handshake packet detected by `applicationType`, session via
  `WebDriver:NewSession`, then `WebDriver:SetTimeouts` and
  `Marionette:SetContext` to `chrome`.
- The server only ever controls a browser it launched itself. If port 2828 is
  already listening, launch/connect refuse (`src/zen/launcher.ts`
  `launchZen`, `src/zen/runtime.ts` `#connectOnce`).
- Launch (`src/zen/launcher.ts`, `buildLaunchArgs`, `launchZen`): spawns the
  Zen executable with args `-marionette -no-remote` plus
  `-profile <profile>` and env `MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1`,
  `ZEN_MCP_LAUNCHED=1`, `ZEN_MCP_LAUNCH_NONCE=<random UUID>`. No preference is
  written, so a normal Zen launch never opens the port. Default profile is a
  dedicated agent profile at `<dataDir>/agent-profile`
  (`resolvedProfilePath`); using the user's normal profile is opt-in
  (`useDefaultProfile`).
- Ownership proof (`src/zen/runtime.ts` `#connectOwnedSession`): after the
  Marionette session is up, a chrome-context script reads
  `ZEN_MCP_LAUNCH_NONCE` back via `Services.env` and compares it with the
  launch nonce. Mismatch means no attach.
- Lockdown (`MarionetteClient.lockdown` in `src/zen/marionette.ts`): a chrome
  script imports `chrome://remote/content/components/Marionette.sys.mjs`,
  closes every Marionette connection except its own session, and calls
  `server.setAcceptConnections(false)`, so the Marionette listener is closed
  for the rest of the browser's life. Startup fails if lockdown fails.
- Marionette is also used for `Marionette:Quit` on shutdown.

### 1b. Data plane: injected in-browser bridge over authenticated WebSocket

- The bridge is a browser bundle built from `src/bridge/entry.ts` by esbuild
  to `dist/bridge.js` (platform browser, IIFE, target firefox128;
  `scripts/build.mjs`).
- Injection (`BridgeHub.#injectOnce` and `buildInjectionScript` in
  `src/bridge/host.ts`): a fixed chrome script run through
  `marionette.executeChrome` enumerates `navigator:browser` windows via
  `Services.wm`, skips private windows (and destroys any bridge found there),
  registers a `resource://` substitution alias `zen-mcp-bridge` pointing at
  the dist directory, sets `window.__zenMcpConfig` (WebSocket URL, token,
  tokenId, versions, policy snapshot, policy path), and loads the bundle with
  `Services.scriptloader.loadSubScript`. Re-injection reuses or reconnects an
  existing bridge when version and tokenId match. `ensureInjected` is called
  on connect, and a 20 s auto-attach timer (`AUTO_ATTACH_MS` in
  `src/zen/runtime.ts`) attaches bridges to new windows.
- Transport (`BridgeHub.start` in `src/bridge/host.ts`): a `ws` WebSocket
  server on `127.0.0.1`, ephemeral port (`port: 0`), path `/bridge`
  (`BRIDGE_PATH` in `src/shared/protocol.ts`), 2 MB max payload. The bridge
  connects out to the server; the browser opens no listening port.
  Non-loopback connections are rejected.
- Authentication (`src/shared/bridge-auth.ts`, host `#onConnection`, bridge
  `entry.ts`): mutual HMAC-SHA256 challenge-response with fresh nonces per
  connection, keyed by a per-server-session 32-byte random token
  (`#token = randomBytes(32)`) that only reaches the browser during
  injection. Nothing but `auth.response` is accepted before the handshake;
  protocol version and bridge version must match the server version.
- Requests are JSON messages `{type: "req", id, method, params,
  policyRevision, policyDigest}` answered by `{type: "res", id, ok, result |
  error}` (`src/shared/protocol.ts`). Default request timeout 25 s
  (`REQUEST_TIMEOUT_MS` in host.ts). The fixed operation map has 31 methods
  (`BRIDGE_METHODS` in `src/shared/protocol.ts`): status, spaces.list/create/
  switch/delete, tabs.list/open/close/select/pin/read/click/type/waitFor/
  evidence/evidenceClear/findText, folders.list/create/addTabs,
  essentials.add/remove, containers.list, glance.open, split.open/close,
  history.search, history.recentlyClosed, bookmarks.search, clipboard.write.
- The bridge side dispatcher is `createOps` in `src/bridge/ops.ts`. It runs
  with the browser's system principal in each window's chrome context and
  only exposes that fixed map; agents cannot submit scripts.

### 1c. Page-content access from the bridge: Gecko's MarionetteCommands actor

The bridge does not use Marionette's content context. For any loaded tab,
including tabs in inactive spaces, it takes
`tab.linkedBrowser.browsingContext.currentWindowGlobal.getActor("MarionetteCommands")`
(`pageActor` / `runEvidenceScript` in `src/bridge/ops.ts`) and sends queries
to Gecko's built-in JSWindowActor:

- `MarionetteCommandsParent:executeScript` with fixed, server-authored script
  strings built in `src/shared/read-script.ts` and `src/shared/evidence-script.ts`
  (builders: `buildReadScript`, `buildInspectElementScript`,
  `buildSemanticTargetScript`, `buildPageSignatureScript`,
  `buildVerifyTypedValueScript`, `buildWaitProbeScript`).
- `MarionetteCommandsParent:clickElement` with capabilities
  `{ "moz:accessibilityChecks": false, "moz:webdriverClick": true }`.
- `MarionetteCommandsParent:clearElement` and
  `MarionetteCommandsParent:sendKeysToElement` for typing.

Because DOM elements cross this actor as Marionette WebElement references,
the bridge keeps a bounded `RefRegistry` (`src/bridge/ref-registry.ts`,
64 documents, up to 400 refs per document as configured in ops.ts) mapping
agent-facing refs to WebElements.

## 2. Tool surface: 55 tools, verified

Count verified from `src/mcp/catalog.ts`: `RESEARCH_TOOLS` has 17 names,
`CORE_ONLY_TOOLS` has 21, `FULL_ONLY_TOOLS` has 17; `ALL_TOOL_NAMES` is their
concatenation, 55 total. `createZenMcpServer` in `src/mcp/server.ts`
registers every one of the 55 with `server.registerTool` and throws at
startup if registrations and the catalog disagree, so the catalog count is
the registered count.

Important nuance: `tools/list` does not show all 55 by default. Tools are
grouped into nested surfaces (`research` is a subset of `core` is a subset of
`full`; config `toolSurface`, default `research`). After registration, tools
outside the configured surface are moved into a `hiddenTools` map and deleted
from the SDK registry, so the default surface exposes only 17 tools. Hidden
tools stay callable through the discovery gateway: `zen_tools_search`
(keyword search over the catalog) and `zen_tools_use` (validates arguments
against the hidden tool's schema and executes it; `publish: true` also
promotes it into `tools/list` and sends `sendToolListChanged`).

Groups (categories from `CATEGORY_BY_TOOL` in `src/mcp/catalog.ts`):

| Category | Count | Tools |
| --- | --- | --- |
| browser | 4 | zen_status, zen_launch, zen_config, zen_audit_tail |
| spaces | 4 | zen_spaces_list, zen_space_create, zen_space_switch, zen_space_delete |
| tabs | 6 | zen_tabs_list, zen_tabs_open, zen_tabs_close, zen_tab_select, zen_pin_tabs, zen_essentials |
| reading | 4 | zen_read_page, zen_read_pages, zen_find_text, zen_search_tabs |
| evidence | 3 | zen_show_evidence, zen_show_evidence_batch, zen_clear_evidence |
| interaction | 3 | zen_click, zen_type, zen_wait_for |
| layout | 3 | zen_glance, zen_split_view, zen_split_close |
| organization | 6 | zen_containers_list, zen_folders_list, zen_folder_create, zen_folder_add_tabs, zen_tabs_audit, zen_tabs_group |
| history | 3 | zen_history_search, zen_history_recently_closed, zen_bookmarks_search |
| coordination | 9 | zen_progress, zen_events, zen_ask, zen_answers, zen_notify, zen_watch_add, zen_watch_list, zen_watch_remove, zen_clipboard_write |
| sessions | 4 | zen_session_save, zen_session_list, zen_session_restore, zen_session_delete |
| templates | 4 | zen_space_templates, zen_template_apply, zen_template_save, zen_template_delete |
| discovery | 2 | zen_tools_search, zen_tools_use |
| Total | 55 | |

Surfaces: research = the 17 RESEARCH_TOOLS; core = research + 21; full = 55.

Also exposed: MCP resources `zen://status`, `zen://spaces`, `zen://tabs`,
`zen://questions`, `zen://watches`, `zen://capabilities` (registered in
`src/mcp/server.ts`), and three prompts: `zen_github_triage`,
`zen_research_brief`, `zen_clean_tabs`.

Every tool call passes through a guard (`guarded` wrapper and `ToolGuard` in
`src/mcp/server.ts` / `src/mcp/guard.ts`): capability policy check, URL
extraction and allowlist check, and an audit record (started/completed
phases) written to `audit.jsonl` in the data directory. If the audit record
cannot be started, the tool does not run.

## 3. Snapshot and semantic interaction

There is no accessibility-tree snapshot. The snapshot is produced by a fixed
DOM-walking script, not by an a11y API.

Read path for `zen_read_page` (formats: text, markdown, links, tables,
metadata, outline, interactive, snapshot, semantic):

1. MCP handler (`src/mcp/server.ts`) calls `ZenRuntime.readPage`
   (`src/zen/runtime.ts`), which delegates to `readActivePage` /
   `readTabPage` in `src/zen/page.ts`; both call `BridgeHub.readTab`, i.e.
   the bridge op `tabs.read`. Page reads never go through a Marionette
   content script on the host side (comment in `src/zen/page.ts`: "The
   authenticated bridge is the only read path").
2. Bridge `tabs.read` in `src/bridge/ops.ts` resolves the tab, rejects
   non-http(s) pages, handles PDFs separately (text pulled from the pdf.js
   `PDFViewerApplication` via `readPdfTab`), then runs
   `buildReadScript(options)` through the tab's MarionetteCommands actor
   (`MarionetteCommandsParent:executeScript`, 15 s timeout). Child frames
   are enumerated from the browsing-context tree (`listFrames`, max 20,
   depth 3) and, for interactive/snapshot reads, up to 10 descendant frames
   are read and merged.
3. The in-page script (built in `src/shared/read-script.ts`) extracts, in one
   pass: visible text (paged by `offset`/`nextOffset`, default cap 24,000
   chars, max 60,000), markdown, links (max 300), tables, metadata
   (OpenGraph/Twitter), heading outline, and a control scan. Results are
   coerced and bounded host-side by `coercePageSnapshot` and
   `toPageReadResult` in the same file.

Snapshot format (`format: "snapshot"`): a `PageReadResult`
(`src/shared/protocol.ts`) with a 4,000-char text preview
(`SNAPSHOT_TEXT_CHARS` in `src/shared/snapshot.ts`), an outline (max 80
headings), and an `elements` array of `PageElement` records: `ref`, `tag`,
`role`, `type`, `label`, `placeholder`, `href`, `disabled`, `checked`,
`readOnly`, `sensitive`, `editable`, plus snapshot-only `valuePresent`,
`autocomplete`, `selected`, `form` (values themselves are never included in
snapshot or semantic reads). Element cap defaults to 100, max 200
(`clampSnapshotElements`). The result carries an opaque `snapshotId`,
`elementsTotal`, and completeness reporting (`snapshotComplete`,
`framesComplete`, up to 5 `limitations`) computed by `snapshotCompleteness`
in `src/shared/snapshot.ts`: output caps never make a snapshot incomplete,
but unreadable, skipped, or unscanned frames do.

Element references: refs are short handles assigned by the read, in document
order, of the form `e12`; controls inside frames carry a frame-path prefix,
`f0-e3` or `f0.1-e2` (format enforced by the regex in
`pageTargetShortcutRef`, `src/mcp/server.ts`, and by
`src/shared/frame-path.ts`). A new interactive or snapshot read of the same
document replaces that document's refs; navigation invalidates them.

Semantic format (`format: "semantic"`): the same read additionally returns a
`SemanticPage` model (types in `src/shared/protocol.ts`, caps and coercion in
`src/shared/semantic.ts`): a heuristic page classification (article,
search-results, product, listing, dashboard, login, form, documentation,
discussion, generic) with confidence and signals; landmark regions (max 40)
with role, label and label source, heading, parent, optional anchor ref, and
control/link/item counts; collections (cards, results, links, items) with
sample refs; dialogs; and a coverage block (nodes scanned up to 6,000,
regions, controls, headings, tables, images, missing alt text, shadow
roots). It is a structural DOM model with inferred labels, not an
accessibility tree.

Semantic interaction (`zen_click`, `zen_type`): the caller names exactly one
target strategy (`normalizeTargetInput` in `src/shared/target.ts`): a ref
from a read, a CSS selector, or a `target` object with one of role+name,
visible text, label, or placeholder (exact or contains matching). Code path:
MCP handler to `ZenRuntime.clickElement`/`typeText` to `BridgeHub` request
`tabs.click`/`tabs.type` to bridge `resolvePageTarget` in
`src/bridge/ops.ts`. For a ref, the bridge re-inspects the stored WebElement
with `buildInspectElementScript` and refuses the action when the element is
gone (`element_removed`), the document was replaced (documentElement
WebElement id comparison, `documentChanged` in `src/bridge/ref-registry.ts`),
or the element's descriptor digest (FNV hash of tag, role, type, label,
href) changed. For semantic targets, `buildSemanticTargetScript` scans the
document; zero matches fail, multiple matches fail with up to 5 candidates
(`target_ambiguous`), and a scan that hits its node limit fails rather than
guessing. The action itself is the actor query `clickElement` (WebDriver
click semantics) or `clearElement` + `sendKeysToElement`. Before and after,
a page-signature script (text hash, value hash, control/heading/alert
descriptors) is captured, and the result reports an observed `effect` delta
explicitly labelled `observed_after_action_not_proven`. Typing into
sensitive fields is never read back for verification. `zen_wait_for` polls
a fixed probe script (selector state present/visible/enabled, text, URL,
title) or chrome-side conditions (document change, new tab, tab closed,
dialog) with a 5 s default and 30 s max timeout.

## 4. Zen-specific features

Spaces (Zen workspaces): modeled directly on Zen's chrome API object
`gZenWorkspaces` in `src/bridge/ops.ts`. A space is
`{ id (workspace uuid), name, icon, active, index, containerTabId }`, with
list results adding tab, pinned, and folder counts. Ops use
`gZenWorkspaces.getWorkspaces()`, `createAndSaveWorkspace`,
`changeWorkspaceWithID`, `removeWorkspace`, and `moveTabsToWorkspace`. A
tab's space is its `zen-workspace-id` attribute. Spaces are first-class
context throughout: `zen_tabs_open` targets a space (and optionally a folder
inside it) and opens in the background by default, tab listing and tab
search filter by space, watches and sessions record the space, and
`zen_notify` can carry an "open this space" action button.

Folders: modeled on Zen's `zen-folder` chrome elements and `gZenFolders`.
A folder is `{ id, label, spaceId, collapsed, parentId (nested folders),
tabIds, liveFolder }` (`folderInfo` in ops.ts, folders found with
`document.querySelectorAll("zen-folder")`, a tab's folder is `tab.group`
when it is a Zen folder). Creation uses
`win.gZenFolders.createFolder(tabs, { workspaceId, label, collapsed })`;
adding tabs pins them first if needed and calls `folder.addTabs(tabs)`;
all tabs in a folder must share one space. `zen_tabs_group` plans
domain-based folders host-side (`planDomainFolders` in
`src/zen/tab-audit.ts`) and creates them through the same op.

Other Zen-native surface: Essentials via `gZenPinnedTabManager.addToEssentials`
/ `removeEssentials` (with capture and restore of prior space and pin state),
Glance via `gZenGlanceManager.openGlance`, split views via
`gZenViewSplitter.splitTabs`, Firefox containers via
`ContextualIdentityService`, history and bookmarks via Places SQL
(`moz_places`, `moz_bookmarks` through `PlacesUtils.promiseDBConnection`),
recently closed tabs via `SessionStore.getClosedTabData`, and clipboard via
`nsIClipboardHelper`.

zen_ask: yes, it exists (core surface). `zen_ask` sends a `ui.ask` message
over the bridge socket; the bridge renders a question card in the browser
chrome (shadow-root UI, `src/bridge/ui.ts`) with up to 6 options, optional
freeform text, and multi-select. The tool blocks up to `waitSeconds`
(default `askTimeoutSeconds`, 120 s; max 600) for a `ui.answer` reply, or
returns `pending` with a question id; late answers are collected with
`zen_answers` and the `zen://questions` resource. Related in-browser UI:
`zen_notify` activity cards with action buttons, `zen_progress` persistent
progress cards with a Stop button, a status banner with Pause/Resume, and a
one-time consent card (`requireConsent`, default on, 90 s default timeout)
that must be approved before any browser operation.

Browser events: push-based inside the browser, polled by the agent. The
bridge's `observeBrowserEvents` (`src/bridge/browser-events.ts`) subscribes
to chrome observers: `TabOpen`/`TabClose`/`TabSelect` on the tab container,
`gBrowser.addTabsProgressListener` for navigation started, committed,
completed, failed, redirect, and same-document changes plus document
replacement, and dialog observation via `Services.obs` domwindowopened/
closed and modal-dialog events (dialog class only, never dialog text). It
sends `browser.event` messages over the WebSocket; the host validates kind
and phase pairs, applies the domain allowlist and policy to event URLs and
titles, and appends to a bounded 200-entry `EventLog`
(`src/bridge/event-log.ts`). Agents read events with `zen_events` using an
`after` cursor and an optional long-poll `waitSeconds` (max 25). Server-side
control events (stop, pause, resume, watch, question) share the same log.
Separately, `zen_watch_add` registers server-side polling watches
(`ZenRuntime` watch timers, default interval 60 s, server minimum
`watchMinIntervalSeconds` default 15 s, max 50 watches) that re-read a tab
and emit `watch` events on text change or selector appear/disappear.

## 5. Runtime shape

- Language and packaging: TypeScript, ESM, Node >= 22 (`package.json`
  `engines`). Built with esbuild (`scripts/build.mjs`) into `dist/cli.js`
  (Node bundle, the `zen-mcp` bin) and `dist/bridge.js` (browser bundle).
- Entry point: `src/cli.ts`, a commander CLI. Commands: `serve` (default;
  also the bare command), `launch`, `status`, `doctor`, `update`, `setup`,
  `onboard`, `config show|set`, `policy show|set|mode|init`.
- MCP transport: stdio only. `serve()` in `src/cli.ts` builds a
  `ZenRuntime`, calls `createZenMcpServer`, and connects a
  `StdioServerTransport` from the MCP SDK. No HTTP MCP transport was found
  in the code read. UNVERIFIED: whether any other entry point offers HTTP;
  none appears in `src/cli.ts` or `package.json` bin/scripts.
- Runtime dependencies (from `package.json`, complete list):
  `@modelcontextprotocol/sdk` ^1.32.2, `commander` ^14.0.3, `ws` ^8.22.0,
  `zod` ^4.6.7. Dev dependencies: esbuild, tsx, typescript, @types/node,
  @types/ws. The Marionette client and the bridge protocol are hand-rolled;
  there is no Playwright, Puppeteer, or Selenium dependency.
- Configuration (`src/config.ts`): JSON config file at
  `$APPDATA/zen-mcp/config.json` or `~/.config/zen-mcp/config.json`
  (XDG_CONFIG_HOME honored), overridable with `ZEN_MCP_CONFIG`. Data
  directory next to the config (`ZEN_MCP_DATA_DIR` override) holds
  `sessions.json`, `templates.json`, `audit.jsonl`, `update.json`, and the
  default `agent-profile/`. Notable config keys with defaults:
  `useDefaultProfile` false, `requireConsent` true,
  `consentTimeoutSeconds` 90, `autoLaunch` true, `launchTimeoutMs` 45000,
  `askTimeoutSeconds` 120, `marionettePort` 2828, `readOnly` false,
  `allowedDomains` [], `auditLog` true, `autoAttachWindows` true,
  `watchMinIntervalSeconds` 15, `launchArgs` [], `toolSurface` "research".
  Env overrides include `ZEN_MCP_ZEN_PATH`, `ZEN_MCP_PROFILE`,
  `ZEN_MCP_USE_DEFAULT_PROFILE`, `ZEN_MCP_REQUIRE_CONSENT`,
  `ZEN_MCP_CONSENT_TIMEOUT_SECONDS`, `ZEN_MCP_MARIONETTE_PORT`,
  `ZEN_MCP_READ_ONLY`, `ZEN_MCP_ALLOWED_DOMAINS`, `ZEN_MCP_AUDIT_LOG`,
  `ZEN_MCP_WATCH_MIN_INTERVAL_SECONDS`, `ZEN_MCP_LAUNCH_ARGS`,
  `ZEN_MCP_TOOL_SURFACE`, plus `ZEN_MCP_BRIDGE_SCRIPT` (bridge bundle path)
  and `ZEN_MCP_NO_UPDATE_CHECK`. A separate capability policy lives in
  `policy.json` (`src/shared/policy*.ts`), watched live by the server and
  pushed to bridges as `policy.update`; the bridge re-reads the file itself
  via IOUtils and rejects requests whose revision or digest is stale.

## Appendix: all 55 tools

| # | Tool | Category | Surface |
| --- | --- | --- | --- |
| 1 | zen_status | browser | research |
| 2 | zen_spaces_list | spaces | research |
| 3 | zen_space_create | spaces | research |
| 4 | zen_tabs_list | tabs | research |
| 5 | zen_tabs_open | tabs | research |
| 6 | zen_read_page | reading | research |
| 7 | zen_read_pages | reading | research |
| 8 | zen_find_text | reading | research |
| 9 | zen_search_tabs | reading | research |
| 10 | zen_show_evidence | evidence | research |
| 11 | zen_show_evidence_batch | evidence | research |
| 12 | zen_progress | coordination | research |
| 13 | zen_events | coordination | research |
| 14 | zen_config | browser | research |
| 15 | zen_notify | coordination | research |
| 16 | zen_tools_search | discovery | research |
| 17 | zen_tools_use | discovery | research |
| 18 | zen_ask | coordination | core |
| 19 | zen_answers | coordination | core |
| 20 | zen_launch | browser | core |
| 21 | zen_space_switch | spaces | core |
| 22 | zen_tabs_close | tabs | core |
| 23 | zen_tab_select | tabs | core |
| 24 | zen_glance | layout | core |
| 25 | zen_split_view | layout | core |
| 26 | zen_split_close | layout | core |
| 27 | zen_pin_tabs | tabs | core |
| 28 | zen_essentials | tabs | core |
| 29 | zen_containers_list | organization | core |
| 30 | zen_folders_list | organization | core |
| 31 | zen_folder_create | organization | core |
| 32 | zen_folder_add_tabs | organization | core |
| 33 | zen_click | interaction | core |
| 34 | zen_type | interaction | core |
| 35 | zen_wait_for | interaction | core |
| 36 | zen_clear_evidence | evidence | core |
| 37 | zen_tabs_audit | organization | core |
| 38 | zen_tabs_group | organization | core |
| 39 | zen_space_delete | spaces | full |
| 40 | zen_history_search | history | full |
| 41 | zen_history_recently_closed | history | full |
| 42 | zen_bookmarks_search | history | full |
| 43 | zen_watch_add | coordination | full |
| 44 | zen_watch_list | coordination | full |
| 45 | zen_watch_remove | coordination | full |
| 46 | zen_clipboard_write | coordination | full |
| 47 | zen_audit_tail | browser | full |
| 48 | zen_session_save | sessions | full |
| 49 | zen_session_list | sessions | full |
| 50 | zen_session_restore | sessions | full |
| 51 | zen_session_delete | sessions | full |
| 52 | zen_space_templates | templates | full |
| 53 | zen_template_apply | templates | full |
| 54 | zen_template_save | templates | full |
| 55 | zen_template_delete | templates | full |

## Sources

All accessed 2026-11-27. Repository: https://github.com/spaxe-dev/zen-mcp
(shallow clone of `main`, HEAD version 0.6.3). Files read in full or in
relevant part:

- https://github.com/spaxe-dev/zen-mcp/blob/main/package.json
- https://github.com/spaxe-dev/zen-mcp/blob/main/src/zen/marionette.ts
- https://github.com/spaxe-dev/zen-mcp/blob/main/src/zen/launcher.ts
- https://github.com/spaxe-dev/zen-mcp/blob/main/src/zen/runtime.ts
- https://github.com/spaxe-dev/zen-mcp/blob/main/src/zen/page.ts
- https://github.com/spaxe-dev/zen-mcp/blob/main/src/bridge/host.ts
- https://github.com/spaxe-dev/zen-mcp/blob/main/src/bridge/entry.ts
- https://github.com/spaxe-dev/zen-mcp/blob/main/src/bridge/ops.ts
- https://github.com/spaxe-dev/zen-mcp/blob/main/src/bridge/browser-events.ts
- https://github.com/spaxe-dev/zen-mcp/blob/main/src/bridge/ref-registry.ts
- https://github.com/spaxe-dev/zen-mcp/blob/main/src/mcp/catalog.ts
- https://github.com/spaxe-dev/zen-mcp/blob/main/src/mcp/server.ts
- https://github.com/spaxe-dev/zen-mcp/blob/main/src/cli.ts
- https://github.com/spaxe-dev/zen-mcp/blob/main/src/config.ts
- https://github.com/spaxe-dev/zen-mcp/blob/main/src/shared/protocol.ts
- https://github.com/spaxe-dev/zen-mcp/blob/main/src/shared/snapshot.ts
- https://github.com/spaxe-dev/zen-mcp/blob/main/src/shared/semantic.ts
- https://github.com/spaxe-dev/zen-mcp/blob/main/src/shared/target.ts
- https://github.com/spaxe-dev/zen-mcp/blob/main/src/shared/read-script.ts
- https://github.com/spaxe-dev/zen-mcp/blob/main/src/shared/brand.ts
- https://github.com/spaxe-dev/zen-mcp/blob/main/scripts/build.mjs
- https://github.com/spaxe-dev/zen-mcp/blob/main/docs/architecture.md

## UNVERIFIED items

- The exact in-page ref counter code inside `buildReadScript` was not read
  line by line; the ref format (`e12`, `f0-e3`, `f0.1-e2`) and
  document-order assignment are established by `src/shared/protocol.ts`
  type comments, the `pageTargetShortcutRef` regex in `src/mcp/server.ts`,
  and `src/shared/frame-path.ts`.
- Behavior on Zen versions other than what the code targets (bridge bundle
  target firefox128; nonce error text mentions Zen 138 or newer) was not
  tested; nothing was run.
- The Reddit thread and community claims are outside this lane's scope.
