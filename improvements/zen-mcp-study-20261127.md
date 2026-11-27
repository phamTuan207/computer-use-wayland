# zen-mcp (spaxe-dev) study: architecture, security verdict, comparison

Date: 2026-11-27. Read-only study ordered by the owner 2026-11-27
21:36 and 21:37. Nothing was installed, nothing of theirs was run,
no data was given to the project. Four independent lanes read the
repository, the docs, and the public record; this report is the
synthesis. The four lane files are committed alongside this
report in improvements/zen-mcp-study-lanes/
(lane1-architecture.md, lane2-security.md, lane3-community.md,
lane4-ours.md), so every claim here can be checked against its
lane evidence.

Subject: github.com/spaxe-dev/zen-mcp, an MCP server for Zen
Browser. Two framing corrections before anything else. First, the
version: v0.6.0 exists as a tag, but the latest release is v0.6.3;
the whole 0.6.x line (v0.6.0 to v0.6.3) shipped on one day,
2026-11-22. The security audit was pinned to the v0.6.0 tag
exactly, and the version matters to the verdict (see the
Verdict section). Second, a name collision: most "zen-mcp"
coverage online belongs
to a different, unrelated project (sh6drack/zen-mcp, WebDriver
BiDi based). This report is only about spaxe-dev/zen-mcp.

## Verdict: SAFE, under stated conditions

For installing v0.6.0 in an isolated test environment that never
touches the real Zen profile, the code audit concludes SAFE,
under all of these conditions:

- Pin version 0.6.0 exactly. Do not install @latest: HEAD (0.6.3)
  adds a postinstall skill offer that can run
  "npx skills add ... --global" on a yes answer. The audited
  0.6.0 package itself defines no preinstall, install,
  postinstall, or prepare script.
- Before measuring, verify the 0.6.0 tool surface against the
  HEAD catalog described in section 1: the audit confirms the
  same 55-tool count at v0.6.0, but the architecture detail was
  read at HEAD (0.6.3). A diff of src/mcp/catalog.ts and the
  bridge between the v0.6.0 tag and HEAD settles the equivalence
  cheaply; until it is run, section 1 describes 0.6.3.
- Dedicated agent profile only. Never run with the normal-profile
  opt-in (--use-default-profile); that flag is the one
  configuration that changes the risk class.
- Set ZEN_MCP_NO_UPDATE_CHECK=1, or block network egress from the
  test environment. The project's only outbound request is its
  npm version check; blocking egress also settles the one
  UNVERIFIED sub-point about transitive dependency behaviour.
- Run as a throwaway OS user or in a VM, and skip the onboard and
  update commands unless they are the specific thing being
  tested (onboard writes other MCP clients' config files; the
  update path installs @latest from npm behind a user click).

Evidence chain, in one paragraph each; full line-level evidence
is in lane2-security.md.

No exfiltration channel exists in the project's own code. The
whole tree (148 files) was searched for fetch, axios, http and
https clients, WebSocket clients, net and dns imports, and
telemetry names (sentry, posthog, mixpanel, segment, amplitude,
telemetry, analytics): zero telemetry or error-reporting code or
dependencies. The single outbound request in the tree is a
version check, GET https://registry.npmjs.org/@spaxe-dev%2Fzen-mcp/latest
(src/zen/updates.ts:9-11, 125-131), sending only a
"zen-mcp/<version>" user-agent, no body and no browser data, once
per server start, disableable via ZEN_MCP_NO_UPDATE_CHECK
(src/zen/runtime.ts:221). All control traffic is loopback:
Marionette on 127.0.0.1:2828 and a bridge WebSocket on 127.0.0.1
with an ephemeral port and mutual HMAC-SHA256 authentication. By
design, tool results (page text) flow to whatever model provider
the MCP client uses; that is the client's data flow, and the
project discloses it (docs/security.md:151).

Install and dependency surface is small and clean at 0.6.0. No
preinstall, install, postinstall, or prepare script; the package
ships a prebuilt dist. Four direct runtime dependencies
(@modelcontextprotocol/sdk ^1.32.2, commander ^14.0.3,
ws ^8.22.0, zod ^4.6.7, semver ranges as declared in
package.json); 130 lockfile entries, 126 unique names; no telemetry
packages, no typosquat-shaped names; only two lockfile packages
have install scripts, both dev-only and standard (esbuild, fsevents).

Permissions demanded are narrow. There is no browser extension,
no manifest, and no native messaging manifest; the bridge is
injected at runtime through Marionette. The code never reads
profile files on disk: nothing touches cookies.sqlite,
logins.json, key4.db, or places.sqlite as files. By default it
creates and uses a dedicated agent profile; the normal profile is
an explicit opt-in. The server process itself is an unsandboxed
user-level Node process: it can spawn and kill Zen, write its own
config and data, and, only through the explicit onboard command,
write other MCP clients' config files. A consent card gates
access by default.

Data exposure is real but bounded. Tools can read page content,
snapshots and semantic page models, browsing history
(zen_history_search, implemented as Places SQL in
src/bridge/ops.ts:3966-4011, and notably not filtered by the
domain allowlist), bookmarks (ops.ts:4014-4047), recently closed
tabs, and tabs, spaces, folders, and containers. Tools cannot
read cookies, saved credentials, or local or session storage: no
code path exists for any of them (full-tree search plus the
55-tool catalog). Sensitive form values are classified and
withheld (src/shared/sensitive.ts); password typing never echoes;
the clipboard is write-only; there is no screenshot, upload, or
download handling. There is also no tool that evaluates
agent-supplied JavaScript: all browser-side execution uses fixed,
server-authored scripts.

The riskiest capabilities, for the test plan to watch:
zen_click and zen_type perform real input that can submit forms
or trigger downloads and purchases; normal-profile mode;
zen_tabs_open and session restore with the default empty domain
allowlist; zen_clipboard_write; the destructive space, session,
and tab deletion tools; and the user-click-gated Update button
that installs @latest globally.

UNVERIFIED sub-points (each has a settling check in the lane
file): whether the published npm tarball is byte-identical to a
build of the v0.6.0 tag; transitive dependencies' internal
network behaviour (settled by blocking egress); Zen's own
Marionette bind address inside the browser (the server dials
127.0.0.1; the listener is Zen's); the exact wording of the
2026-11-22 Reddit thread (not retrieved, section 2).

## 1. Architecture

This section describes HEAD (0.6.3), the version read for
architecture; the security audit behind the Verdict pinned the
v0.6.0 tag. The audit confirms the same 55-tool count at
v0.6.0; full surface equivalence between the tag and HEAD is
the settling check named in the Verdict conditions.

Two loopback channels, no extension, no native messaging, no
CDP, no WebDriver BiDi. The server launches Zen itself and
refuses to attach to a running browser. Launch uses a dedicated
agent profile with -marionette -no-remote, the environment
variable MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1, and a random
ZEN_MCP_LAUNCH_NONCE. A hand-written, dependency-free Marionette
protocol v3 client (src/zen/marionette.ts) speaks raw TCP to
127.0.0.1:2828. Chrome scope is used only for setup: reading the
nonce back through Services.env to prove the server owns this
browser instance, injecting the bridge, and a lockdown step that
closes every other Marionette connection and the listener itself
(setAcceptConnections(false)).

The data plane is a bridge bundle (src/bridge/entry.ts, built to
dist/bridge.js) injected into each normal Zen window's chrome
through a resource:// substitution and
Services.scriptloader.loadSubScript. The bridge connects out to
the server's WebSocket listener (127.0.0.1, ephemeral port,
path /bridge), mutually authenticated with an HMAC-SHA256
challenge-response keyed by a per-session 32-byte token, and
serves a fixed map of 31 ops (the BRIDGE_METHODS map in
src/shared/protocol.ts, dispatched by src/bridge/ops.ts). Page content is
reached from the bridge through Gecko's built-in
MarionetteCommands JSWindowActor
(MarionetteCommandsParent:executeScript, clickElement,
sendKeysToElement) with fixed server-authored scripts. A
consequence worth noting: it can act on tabs in inactive spaces
without selecting them first.

Tool surface: exactly 55 tools, verified by count
(src/mcp/catalog.ts: 17 research, 21 core-only, 17 full-only;
src/mcp/server.ts registers all 55 and throws at startup if the
catalog and registrations disagree). Only the configured surface
is listed by default (research, 17 tools); the rest are hidden
and reachable through a discovery gateway (zen_tools_search and
zen_tools_use), with optional publishing into tools/list.
Groups, from the catalog's own categories: browser 4, spaces 4,
tabs 6, reading 4, evidence 3, interaction 3, layout 3,
organization 6, history 3, coordination 9, sessions 4,
templates 4, discovery 2. The full per-tool table is in
lane1-architecture.md.

Snapshots are not an accessibility tree. zen_read_page runs a
fixed DOM-walking script (buildReadScript in
src/shared/read-script.ts) inside the page through the
MarionetteCommands actor and returns one of nine formats (text,
markdown, links, tables, metadata, outline, interactive,
snapshot, semantic). The snapshot format is a bounded
PageReadResult: a 4,000 character text preview, a heading
outline, and an elements array of control records (tag, inferred
role, type, label, placeholder, href, disabled, checked,
readOnly, sensitive, editable, plus value-presence metadata but
never values), capped at 100 elements by default and 200 at
most, carrying an opaque snapshotId and explicit completeness
flags (snapshotComplete, framesComplete, limitations) that
account for unscanned or unreadable frames. Elements are
referenced by short refs (e12; f0-e3 or f0.1-e2 inside frames)
held in a bridge-side RefRegistry mapping refs to Marionette
WebElements. A re-read or a navigation replaces the refs, and
before any click or type the bridge re-inspects the element and
refuses if it was removed, its document was replaced, or its
descriptor digest changed. The semantic format adds a heuristic
page model: classification with confidence, landmark regions,
collections, dialogs, coverage. Semantic targeting accepts
exactly one strategy per call (ref, CSS selector, role plus
name, visible text, label, or placeholder); ambiguous matches
are refused with the candidates listed. Actions use WebDriver
click and sendKeys actor commands and report a before and after
page-signature delta labelled, honestly,
"observed_after_action_not_proven".

Zen-specific surface. Spaces are native gZenWorkspaces
workspaces (uuid, name, icon, containerTabId); tabs carry
zen-workspace-id; spaces are context everywhere: background tab
opens target a space (and optionally a folder), list and search
filter by space, sessions record space layouts,
and notification cards can deep-link to a space. Folders are
native zen-folder elements through gZenFolders.createFolder and
folder.addTabs, with tabs pinned first, a single space enforced,
nested folders through parentId, and a liveFolder flag;
zen_tabs_group auto-groups tabs by domain into folders.
zen_ask renders a question card in the browser chrome (up to 6
options, freeform, multi-select), blocks up to a configurable
wait (default 120 s) or returns pending; late answers arrive
through zen_answers and zen://questions. Companion UI:
zen_notify cards, zen_progress cards with a user Stop button, a
Pause and Resume banner, and a one-time in-browser consent card
gating all access. Browser events are push-based inside the
browser (tab open, close, select, navigation phases, document
replacement, dialog shown and hidden, from chrome observers in
src/bridge/browser-events.ts), sent over the WebSocket into a
bounded 200-entry host event log, and consumed through
zen_events with a cursor and up to 25 s long-polling;
zen_watch_add adds server-side polling watches (change, appear,
disappear) on top. Also native: Essentials
(gZenPinnedTabManager), Glance, split views, containers, Places
SQL for history and bookmarks, SessionStore recently-closed.

One UNVERIFIED item from lane 1: the exact in-page ref counter
code inside buildReadScript was not read line by line; the ref
format and document-order assignment rest on the protocol types,
the server-side ref regex, and the frame-path code. No behaviour
was runtime-tested, per the read-only rules.

## 2. Community claims, checked

The Reddit post itself could not be found. Nine distinct web
searches, including a site:reddit.com query for r/zen_browser
and zen-mcp that returned zero results, surfaced no Reddit post
about this project, and no Reddit URL could be opened. The
post's author claims, commenter praise and criticism, and
usernames are therefore UNVERIFIED as community statements. A
launch moment on 2026-11-22 is corroborated circumstantially:
four releases tagged that day, the npm package updated
2026-11-22T14:10Z, and stars growing from 21 (a crawl around
Nov 23) to 30 (live on 2026-11-27). The two headline concerns
were checked against the repository directly instead.

Windows-only testing: TRUE, and self-declared. The README states
that Windows is the only platform with a live-tested Zen launch
and that macOS and Linux are CI only. The author's own issue #15
is a detailed audit listing real POSIX defects, including
profile-lock detection returning false on all non-Windows
platforms and pgrep -x zen missing Flatpak and Snap process
names. The cross-platform engineering is nonetheless real: a CI
matrix on three operating systems and two Node versions, per-OS
Zen discovery including Flatpak and Snap paths
(src/zen/launcher.ts:91-132), and a POSIX profile-lock parser.
Linux live behaviour is unproven; in an isolated test that is a
reliability risk, not a security one.

Vibe code: as a community claim, UNVERIFIED (no accessible source
makes it). On the artifacts, the fair label is single-author,
AI-accelerated, unusually security-conscious, pre-1.0. For the
suspicion: 69 commits in 22 days with 26 on one day, 68 of 69
single-author, monolith files (ops.ts 4,247 lines, read-script.ts
3,561 lines), 47 uses of "any" concentrated at the untyped
browser boundary. Against sloppiness: 42 test files, about
14,185 test lines, 542 test declarations including a security
end-to-end suite, CI on three OSes and two Node versions, zero
TODO or FIXME markers, typed errors (319 catches, 244 throws),
and security work that careless code rarely produces:
symlink-refusing atomic writes, an installer PATH-hijack defence
(src/zen/updates.ts:205-250), the launch-nonce ownership proof,
and a security document that lists residual risks against
itself. The real risk is bus factor: it is a solo project, 27
days old at the time of study.

Security worries in public: no public security issue or
accusation was found. The one independent assessment is
PolicyLayer's vendor catalogue (scan dated 2026-11-08): of 50
tools, 24 can modify or destroy data without limits, and 6
destructive tools have no built-in limits; three named tools
(zen_essentials, zen_template_delete, zen_session_delete) are
rated "Destructive tool with critical risk" on their per-tool
pages. That is a capability
statement, consistent with our own audit's riskiest list, not a
vulnerability report. The author's stated model is an owned
browser with a dedicated no-login profile by default, an opt-in
normal profile, a consent card, Pause, a read-only mode, an
allowlist, and an audit log.

Repo social proof, live on 2026-11-27: 30 stars, 1 fork,
1 watcher, 80 commits, created 2026-10-31, MIT licence. Only 5
open issues, all author-filed roadmap and design items from
Oct 31 to Nov 1; zero external bug reports, platform complaints,
or security questions. The exact contributor count is UNVERIFIED
(the contributors page did not render), but all evidence points
to a solo project. No Hacker News thread, YouTube video, or blog
post about this project was found; the one how-to article that
surfaces is about the other zen-mcp.

## 3. Comparison with our RDP channel (scripts/zen-rdp)

Our channel, as landed on todolist-push at a831e250 (lane 4's
inventory): a hand-rolled, stdlib-only Python client for the
Firefox Remote Debugging Protocol, length-prefixed JSON over one
TCP socket to 127.0.0.1, attaching to the owner's real Zen
launched with --start-debugger-server. Two evaluation contexts
(content, and parent or chrome behind a gate and audit), one
pinned tab per client, one request in flight, 7 CLI subcommands
and about 12 library operations, an 8-check fail-loud smoke run
after every Zen update. Safety machinery: a versioned JSON
envelope with a closed error-code set, a delivery vocabulary
(not_delivered, delivery_uncertain, delivered_unverified,
delivered_verified) and a retry vocabulary, per-session tab
scope, a credential denylist on by default, I22 redaction of
sensitive URL parameters in snapshots and reports, fail-closed
attach gates with a profile-marker check, a hardened single-drive
flock (set by the machine-layer wrapper; the client does not
force it), and a drive-report audit. Semantic element interaction
exists in our stack only on the separate AT-SPI lane
(scripts/a11y.py), which sees Zen as a desktop accessibility
tree, not as a page DOM.

Where zen-mcp is ahead of our channel:

- An MCP interface with progressive disclosure: 17 default
  tools plus a search and use gateway for the rest. Our zen-rdp
  has no MCP surface at all (the repo's scripts/mcp_bridge.py
  serves the wider computer-use CLI, not zen-rdp).
- A semantic interaction layer on the page DOM: bounded
  snapshots in nine formats with completeness accounting, short
  refs with digest re-verification before acting, ambiguity
  refusal with candidates, and honestly labelled action deltas.
  Our channel has no DOM snapshot command; page reads are
  arbitrary JavaScript through eval.
- Spaces and Folders as first-class context across opens,
  search, sessions, and templates. In our channel they are
  reachable only as raw chrome JavaScript through the gated
  parent evaluate, or through the Marionette prototype
  (improvements/zen-sidebar/zen_live.py), which cannot attach to
  the owner's current live Zen.
- Human-in-the-loop UI inside the browser: zen_ask question
  cards, notify and progress cards with a Stop button, a Pause
  banner, a consent card. Our channel has nothing in the
  browser; approvals live outside it.
- A browser event stream: push events with a cursor and
  long-polling, plus polling watches. Our client skips
  unsolicited RDP packets inside request() and surfaces no
  events at all.
- Acting on tabs in inactive spaces without selecting them,
  through the MarionetteCommands actor. Our channel pins one
  tab per client.
- An owned-browser lockdown pattern: launch-nonce ownership
  proof, then closing the Marionette listener to everyone else.

Where our channel is ahead:

- It drives the owner's real, live Zen: the actual session,
  logins, and restored tabs. zen-mcp refuses to attach to a
  running browser at all, and its default mode is a dedicated
  no-login profile; driving the real profile is an opt-in it
  treats as the risky configuration. This is the core
  requirement of our project, and the two designs are opposed
  on it by intention, not by quality.
- Delivery and retry semantics: our envelope distinguishes
  not_delivered from delivery_uncertain and marks retry safety,
  which is what makes unattended driving safe to resume.
  zen-mcp's action reporting is honest ("observed, not proven")
  but carries no delivery-uncertainty model and no retry
  vocabulary.
- Attach-time defence in depth on a shared live browser:
  profile-marker verification of the port owner, per-session
  tab scope, a credential denylist on by default, single-drive
  locking. zen-mcp's allowlist, consent card, audit log,
  read-only mode, and capability policy are
  real, but its history search bypasses the allowlist entirely.
- Proven live on Linux and Wayland, on the owner's machine,
  including tonight's integration landing. zen-mcp on Linux is
  CI-only with author-documented POSIX defects (issue #15).
- No supply chain: stdlib-only Python. zen-mcp is an npm
  package; clean at the audited tag, but its own 0.6.3
  postinstall addition shows the surface can move between
  versions.
- Our defect list is known and shrinking in the open: the
  integration review's A1, C1, C2, and F7 are fixed in the
  landed code (C1 with a residual: a fragment carrying no "="
  or "&", a bare token or an SPA route, still passes through
  verbatim), F11 is partially fixed, and from the earlier
  review the headline open items are the F1 double-execution
  trigger and the F5 denylist class, with F2, F3, F4, F6, and
  F9 also still open and recorded in lane 4's inventory.
  zen-mcp's defect surface on Linux is largely
  unmeasured because it has never been live-tested there.

## 4. What to take: concrete proposals

If the team proceeds with the isolated test the owner described
(pinned 0.6.0, dedicated profile, egress blocked or the update
check off, throwaway user), measure it against the RDP channel
on the same task set, with wall-clock timing and success rates:
open a tab into a named space, snapshot a real page, click by
role and name, type into a field, read history, answer a
zen_ask. The council and redteam decision the owner plans
should get those numbers, plus this report's conditions list as
the test's safety frame.

Independent of whether zen-mcp itself is adopted, five of its
ideas port cleanly into our channel, in priority order:

1. A snapshot command for zen-rdp. A fixed, server-authored read
   script returning a bounded result in their shape (text
   preview cap, element cap, completeness flags, snapshotId),
   instead of arbitrary eval for page reads. This extends our
   queue items Q3 and Q5 and the I5 accounting discipline to
   the page DOM, and it removes most routine uses of raw eval.
2. Snapshot-qualified refs with digest re-verification. Extend
   the I3 pattern from the AT-SPI lane to the page DOM: refs
   issued by the snapshot command, re-inspected before click or
   type, refused when the descriptor digest changed, ambiguous
   targets refused with candidates. This is the missing
   semantic layer between our eval-only channel and the a11y
   lane.
3. Spaces and Folders as context in zen-rdp. Expose workspace
   and folder identity in tab listings and accept a space
   target on open and navigate, implemented once in the
   channel's gated parent context, instead of hand-written
   chrome JavaScript at every call site. The folder-tool
   research already established the underlying calls
   (gZenWorkspaces, gZenFolders); this makes them a surface.
4. A browser event feed. Stop discarding unsolicited RDP
   packets: keep a bounded event log (tab list changes,
   navigation, target destruction) with a cursor read and
   long-polling, in their zen_events shape. Several of our
   wait_for uses, and the F11 dead-tab burn, get cheaper or
   disappear when state changes are pushed instead of polled.
5. An ask surface for human decisions. Their zen_ask pattern (a
   card in the browser, blocking with a pending fallback, late
   answers through a companion call) maps onto our approval
   flow for the moments the user is at the machine. It needs a
   spike through the parent context before any commitment; the
   transferable part is the interaction contract, not their
   chrome code.

Two smaller patterns worth copying on sight: progressive
disclosure for any future MCP surface over zen-rdp (a small
default tool set plus a search and use gateway keeps model
context small), and an ownership proof at attach (our
profile-marker gate checks who owns the port; a nonce written
at launch and read back through the browser, their pattern,
proves the browser itself is the one we launched, for the
split-profile case).

What not to take: the owned-browser-only model, which conflicts
with our core requirement to drive the owner's live Zen; npm
distribution for our own channel; the update-check phone-home
pattern, however benign; and history access without allowlist
filtering, which their own design leaves open and ours should
not copy.

## Sources

All accessed 2026-11-27.

- The repository, read at the v0.6.0 tag for the audit and at
  HEAD (0.6.3) for architecture: https://github.com/spaxe-dev/zen-mcp
- Its README and security document:
  https://github.com/spaxe-dev/zen-mcp/blob/main/README.md and
  https://github.com/spaxe-dev/zen-mcp/blob/main/docs/security.md
- Its issue #15 (author's POSIX platform audit):
  https://github.com/spaxe-dev/zen-mcp/issues/15
- npm package page: https://www.npmjs.com/package/@spaxe-dev/zen-mcp
- PolicyLayer vendor catalogue entry (scan dated 2026-11-08),
  as recorded in lane3-community.md.
- Our channel: scripts/zen-rdp in this repo at todolist-push
  a831e250, improvements/integration-review-20261127.md, and
  improvements/zen-rdp-clone2-review-20261127.md.
- The 2026-11-22 Reddit thread in r/zen_browser could not be
  retrieved through any of nine searches; its contents are
  UNVERIFIED and nothing in this report rests on them.

## Appendix: the 55 tools (catalog at HEAD 0.6.3; count confirmed at v0.6.0)

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
