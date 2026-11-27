# Pain-point sweep: last30days scan verification + upstream Firefox/Zen notes, 2026-11-28

Assignment: owner, chat 2026-11-28 06:32 +07 (English). The whole team works on the
pain-point sweep. Mei's part: (1) verify the last30days scan findings against their
sources as they land in improvements/ on todolist-push; (2) research upstream
Firefox/Zen changes in the last 30 days that affect our RDP lane (remote debugging
protocol changes, BiDi, Zen releases). Delivery: this file, committed to todolist-push
improvements/.

Bottom line: no breaking change to the RDP lane in the window; the one watch item
is U1 (bug 2095150). Scan verification: 3 of 7 findings VERIFIED as written,
4 CORRECTED (none rejected).

Window: 2026-10-28 to 2026-11-28. Access date for all sources: 2026-11-28.
Method: three parallel research lanes (A: Firefox releases + remote debugging
protocol; B: WebDriver BiDi; C: Zen releases), each reading its sources directly
with browser.search + browser.open. A claim counts only if its lane opened and read
the source; anything unopened is UNVERIFIED and quarantined in section 4, never
stated as fact. "Opened and read" includes a search-result-text or search-excerpt
read when the page itself could not be opened, and every such claim stays marked
as such. Lane working files: ~/workspace/pain-point-sweep/lanes/
(lane-a-firefox-rdp.md, lane-b-bidi.md, lane-c-zen-releases.md).

Impact scale, judged against our RDP lane only: none / watch / breaking. Our RDP
lane: stdlib-only client in scripts/zen-rdp/, attaching via --start-debugger-server
to a flag-free Zen session, using evaluate, navigate, tab list, with
devtools.debugger.prompt-connection=false in user.js. The owner machine sets no
enterprise policies. The owner Zen profile is read-only for this work; no live
work was run.

## 1. last30days scan findings verification

Verification method for findings as they land (each landing gets its own entry
here, appended by follow-up commit):
- (0) Detect a landing: git fetch origin; list new files under improvements/ on
  todolist-push since the last check (filename listing via git ls-tree, not a
  content grep, which returns 400 files case-sensitive (406 case-insensitive)
  at tip 72d95175, measured 2026-11-28); grep the filenames
  for last30, pain, sweep, scan. A file counts as a sweep finding only if it
  is named last30days-scan-* or is explicitly filed as a scan finding for this
  sweep, dated 2026-11-28. Older hits (worker-click-sweep-log.md,
  worker-cl1sweep-fail-invest-log.md, y6e-evidence/scan-added.txt,
  y6e-evidence/scan-removed.txt) are from earlier sweeps and fail that test.
- (a) Read the finding file in full from todolist-push.
- (b) Open every source the finding cites and check the cited claim against the
  source text. A finding whose source cannot be opened is UNVERIFIED, never
  confirmed.
- (c) Record per finding: VERIFIED (source supports the claim as written),
  CORRECTED (claim fixed, with old and new wording), REJECTED (source
  contradicts the claim or does not exist), or UNVERIFIED (a cited source
  could not be opened; claim not confirmed), plus the source URL and access
  date.
- (d) Cross-lane conflicts are recorded in the open, not silently resolved;
  section 4 holds the current conflict list (U6, see Q2).

Status: checked 06:32 +07 (todolist-push tip 72d95175, filename listing, the 4
older hits only, no scan file); re-checked 06:35 +07 (todolist-push tip
unchanged, 72d95175). At 06:36:44 +07 commit ea57a60f landed
improvements/last30days-scan-20261128.md (247 lines, 7 findings). Two more
files landed in the same window and are NOT scan findings, so they get no
entry here: improvements/pain-point-meeting-20261128.md (86d271a4, Part 2
meeting decision) and improvements/cloudflare-code-mode-research-20261128.md
(9ca3406f). All 7 scan findings were verified against their cited sources at
todolist-push tip 631e685c (06:41 +07). Verifier working file:
~/workspace/pain-point-sweep/review/scan-verification.md.

Verification table (scan file improvements/last30days-scan-20261128.md, commit ea57a60f):

| # | Finding | Claim (short) | Source URL + access date | Verdict |
|---|---------|---------------|--------------------------|---------|
| 1 | firefox-mcp v0.11.1 (2026-11-27) | wait_for tool, container-scoped sessions, BiDi-only server, tool presets, idle-timeout, confirm_repost pref | Discourse post discourse.mozilla.org/t/firefox-mcp-v0-11-1-released/150479, Planet Mozilla, GitHub API mozilla/firefox-mcp, Bugzilla 2089768; 2026-11-28 | VERIFIED |
| 2 | Bugzilla 2081604 | Page settling after input is its own bug class, separate from later-appearing content | https://bugzilla.mozilla.org/show_bug.cgi?id=2089768; 2026-11-28 | VERIFIED |
| 3 | Kitsune | Extension-based shared-browser MCP, background agent tabs, per-tab handoff model, six tools | https://github.com/junyeong-nero/kitsune (README + API); 2026-11-28 | VERIFIED |
| 4 | claude-for-zen | BiDi with existing profile, ws://127.0.0.1:9333, trusted input events, isolated runtime | https://glama.ai/mcp/servers/ilhamnadhif/claude-for-zen and https://github.com/ilhamnadhif/claude-for-zen; 2026-11-28 | CORRECTED |
| 5 | Field convergence | wait_for + snapshot + scoped sessions across Playwright, Chrome DevTools, Mozilla, agent-browser; Firefox 155 parallel BiDi + DevTools | https://bugzilla.mozilla.org/show_bug.cgi?id=2089768 and https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/155 (agent-browser changelogs via search excerpts); 2026-11-28 | CORRECTED |
| 6 | Bugzilla 2090753 | Remote Agent data collection, RESOLVED INVALID | https://bugzilla.mozilla.org/show_bug.cgi?id=2090753; 2026-11-28 | CORRECTED |
| 7 | Noise items | zen-mcp post, firefox-bidi-mcp, Workspace MCP mandate, Firefox memory benchmark, WebMCP thread | Per-bullet sources in detail below (Glama listings, dev.to, samcodeman.com, gigazine.net, search excerpts); 2026-11-28 | CORRECTED |

Verification detail (corrections only; VERIFIED findings need no detail):
- Finding 4, CORRECTED: old wording "Glama lists it with A license / A quality."
  New wording: "Glama listing opened and read; no license/quality grades shown on
  the page as fetched (431 lines read in full)." Nuance, not a correction: the
  README says BiDi needs no extension, but there IS an optional "Claude for Zen"
  helper add-on for --no-restart mode; the scan wording is accurate for the core
  BiDi path. "Single maintainer" was not independently confirmed (repo: 7 commits,
  0 forks).
- Finding 5, CORRECTED: the Firefox 155 bullet is UPGRADED from the scan's own
  UNVERIFIED to VERIFIED. MDN states verbatim: "Updated the Mozilla-specific
  moz:debugging module to no longer rely on the same nested event loop API as
  DevTools, which prevents conflicts when WebDriver BiDi and DevTools are used
  in parallel. (Firefox bug 2041335)." Release date September 1, 2026. Remove
  the "(secondary source, treat as UNVERIFIED until checked against MDN)"
  qualifier. The agent-browser items rest on search excerpts (agentgid.com,
  agent-browser.dev changelogs).
- Finding 6, CORRECTED (minor date correction only): old wording "Bugzilla 2090753
  (opened ~2026-11-11, closed RESOLVED INVALID)". New wording: "Bugzilla 2090753
  (opened ~2026-11-08, closed ~2026-11-16, RESOLVED INVALID)". Reason: the bug
  page says "Opened 19 days ago" (= ~2026-11-08) and "Closed 11 days ago"
  (= ~2026-11-16), as crawled 2026-11-27 23:40 UTC.
- Finding 7, CORRECTED (mixed per-bullet): firefox-bidi-mcp (177 tools, 17
  domains) EXISTS AS CITED (Glama listings, search excerpts). Google Workspace
  MCP mandate substance EXISTS AS CITED (eight Workspace MCP servers generally
  available Nov 24, 2026, agent use required from Feb 1, 2027); the HN 420 pts
  score is UNVERIFIED. zen-mcp v0.6.0 Reddit post (2026-11-22, r/zen_browser,
  35 pts) is UNVERIFIED (partial corroboration only: npm @spaxe-dev/zen-mcp
  0.6.2, updated 2026-11-22). Firefox v10-to-v160 memory benchmark (382 pts)
  is UNVERIFIED. WebMCP / generate-MCP-servers thread is UNVERIFIED (not
  independently checked; speculative thread, low stakes).
- Method note: the scan's "Every claim below cites a source that was opened" is
  slightly overstated: the shadowgraph.io mirror citation (Finding 3) could not
  be located, and the Glama A/A grades (Finding 4) were not on the page as
  fetched. All load-bearing claims check out regardless. Finding 3 carries a
  README caveat the scan does not mention ("site-opened popups and OS-level
  trusted input can still move focus"), worth carrying into the meeting record.
- REJECTED: none. No finding is contradicted by its sources.

Cross-checks against section 2: scan Finding 1 corroborates draft U12 (bug
2081635, the BiDi-only move). Scan Finding 6 (VERIFIED with the date correction)
confirms the standing rule that RDP/BiDi ports must stay loopback-only. Scan
Finding 5's Firefox 155 item (now MDN-confirmed) adds the moz:debugging
parallel-use fix to the BiDi background in U5.

## 2. Upstream notes: what changed in the window, and what it means for the RDP lane

Bottom line: NO BREAKING CHANGE to the RDP lane landed in the window. Firefox
159.0.1, 160, 160.0.1 and 161 contain no DevTools remote-protocol changes, and
Zen's four bumps in the window touch nothing debugger-related. The one item to
watch is U1 (bug 2095150, prompt-connection forced true on all channels).

### U1. Bug 2095150: devtools.debugger.prompt-connection forced true on all channels, WATCH (top item)
- Claim: "We recently forced the preference devtools.debugger.prompt-connection
  to true on all channels, whereas it used to be false on Nightly and local
  builds." The bug reverts that decision for local builds only; status RESOLVED
  FIXED, target Firefox 163 branch, closed about 20-21 Nov 2026. This is the
  pref our silent attach depends on.
- Source: https://bugzilla.mozilla.org/show_bug.cgi?id=2095150 (lane A, opened and read)
- Impact: watch, not breaking on current evidence. Our lane sets
  prompt-connection=false explicitly in user.js, and the bug text discusses
  setting the pref via config as a workaround, which indicates a default-value
  change rather than a lock. Two gaps stay open: whether the forcing overrides
  a user-set pref, and exactly which Firefox version the forcing landed in
  (see section 4, Q1). Standing check: on the next Zen update drill, verify
  that prompt-connection=false still suppresses the connection prompt (already
  an R10 drill item).
- Zen context (lane C): Zen's own baseline already defaults prompt-connection
  to true (Zen PR #927, merged 26 Aug 2024, commit d87315d, set
  devtools.debugger.remote-enabled true to false and
  devtools.debugger.prompt-connection false to true). Our lane overrides both
  via user.js plus --start-debugger-server, exactly as the R10 switch proof
  did on 1.24.3b. The Firefox-level forcing therefore changes nothing about
  Zen's default, but the user-pref question in Q1 still stands.

### U2. No Mozilla deprecation of the DevTools remote protocol (RDP), none
- Claim: no Mozilla statement, release note, or bug in the window announces
  deprecation or removal of the DevTools remote protocol itself (the
  length-prefixed JSON protocol on the --start-debugger-server port). No
  announcement in the window deprecates Marionette either, and no Marionette
  removal plan was found; Marionette is still maintained as internal test
  infrastructure (MozillaWiki M14/M15 notes). The only related open meta-bug
  is 1816085, "replace the Marionette executor for Firefox with a
  WebDriver-BiDi backend" for web-platform-tests, opened 2023, with no
  in-window movement found. What Mozilla deprecated and removed was CDP:
  deprecated in Firefox 129 (May 2024), removed in Firefox 141 (2025, outside
  the window), with the remote.active-protocols pref removed alongside. The
  claim "Mozilla is moving away from RDP in favor of BiDi" traces to a
  third-party fork's migration document, not to Mozilla. Firefox DevTools
  itself still uses the RDP protocol (about:debugging, Browser Toolbox), and
  firefox-source-docs still documents remote-debugging smoke tests plus a
  backward-compatibility policy (client supports a server up to 3 versions
  older) with automated backward-compat CI (bug 2053559). Note the port
  distinction: --remote-debugging-port now serves a BiDi WebSocket, while
  --start-debugger-server serves the DevTools RDP; our lane uses the latter,
  which this change does not touch. Per-tool CDP migration background:
  Puppeteer switched to BiDi for Firefox and removed its CDP support; Cypress
  uses BiDi by default for Firefox; Selenium migrated its CDP-reliant APIs to
  BiDi; Playwright never used Firefox CDP. Mozilla "strongly encourage[s]
  anyone maintaining tools that still depend on CDP support in Firefox to
  migrate to WebDriver BiDi".
- Sources: https://fxdx.dev/cdp-retirement-in-firefox/ (opened and read);
  https://firefox-source-docs.mozilla.org/devtools/release.html (opened and read);
  https://wiki.mozilla.org/WebDriver/RemoteProtocol/WebDriver_BiDi (opened);
  https://bugzilla.mozilla.org/show_bug.cgi?id=1816085 (read via search excerpt)
- Impact: none for now; watch long-term, since Mozilla's new tooling is
  BiDi-first (see U12).

### U3. Firefox releases in the window: no DevTools remote-protocol changes, none
- Firefox 159.0.1 (3 Nov 2026): point release with 7 fixes (tab attention dot,
  Windows cmd window on update restart, shared passkeys, antivirus crashes,
  Linux WebGL red/blue swap, Cuba DST data, Settings text wrap) plus MFSA
  2026-123. No DevTools, remote debugging, or protocol items.
  Source: https://www.firefox.com/en-GB/firefox/159.0.1/releasenotes/
- Firefox 160 (10 Nov 2026): Mini Window, PiP speed control, history drag,
  MathML PDF accessibility, MKV playback, macOS Metal WebGL, Smart Window in
  French, SpeechRecognition. MDN developer notes list no DevTools changes.
  Sources: https://www.firefox.com/en-US/firefox/160.0/releasenotes/;
  https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/160
- Firefox 160.0.1 (17 Nov 2026): graphics/tab-crash fixes only (thin PDF lines
  printing as black boxes on Windows, blank PDFs/WebGL on AMD Macs, WebGL/canvas
  colors on Linux Wayland, slow links (e.g. Google Store), tab crashes
  (notably ChatGPT), WebTransport datagrams, trackpad swipe scrolling). No
  DevTools or protocol items.
  Source: https://www.firefox.com/en-GB/firefox/160.0.1/releasenotes/
  (read via search result text from firefox.com)
- Firefox 161 (24 Nov 2026): the only DevTools item in the release notes is
  the eyedropper showing wrong colors after scrolling. MDN developer notes
  list no DevTools changes. MFSA 2026-131 lists 110 security fixes.
  User-facing notes also record a session-restore fix: tabs disappearing after
  restart when a saved session referenced a deleted tab group. Direction is
  favorable for restore-dependent work.
  Sources: https://www.firefox.com/en-US/firefox/161.0/releasenotes/;
  https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/161
- Date note: lane B reported Firefox 161 as 25 Nov, citing a news article
  dated 25 Nov. Lanes A and C opened MDN and firefox.com, which give
  24 Nov. 24 Nov is used here.
- Impact: none. The next major release, Firefox 162, is scheduled for
  8 Dec 2026 (outside the window; gigazine, read via search excerpt); re-run
  this check after it lands and the following Zen bump lands.

### U4. BiDi specification churn: 8 Working Draft snapshots, small fixes only, none
- Claim: W3C published BiDi Working Drafts on 3, 6, 9, 10, 11, 12, 13 and
  26 Nov 2026. No new maturity stage was reached. Substantive merges in the
  window are all small fixes, no new module and no new command: 26 Nov
  editorial, switch remote-end configs to WebDriver configuration (#1220);
  13 Nov fix script value serialization/deserialization inputs (#1206);
  12 Nov fix negative-zero test in BiDi rounding; 11 Nov pass maxNodeCount
  to CSS and XPath locators (#1209); 10 Nov fix device pixel ratio document
  (#1208), unwrap results from text and accessibility locators (#1210);
  9 Nov input.setFiles reads files before checking their count (#1205);
  6 Nov proposals directory removed; 3 Nov fix intercept phase set during
  network.responseStarted, editorial use of declared contexts in
  network.addIntercept (#1191), fix collector lookup order in network.getData
  (#1192). The Browser Testing and Tools WG opened 11 issues and merged 12
  PRs in w3c/webdriver-bidi in November 2026 (read via search excerpt).
- Sources: https://www.w3.org/standards/history/webdriver-bidi/;
  https://github.com/w3c/webdriver-bidi/commits/main/ (both opened and read);
  WG activity page read via search excerpt.
- Impact: none for the RDP lane. Closest to relevance: #1206 (script
  serialization) and #1209 (maxNodeCount on locators) matter only to a future
  BiDi client, not to RDP evaluate.

### U5. Firefox 160/161 BiDi fixes, none for the RDP lane, watch for a future BiDi client
- Firefox 160 BiDi items (MDN): machine-readable CDDL for all Firefox BiDi
  vendor extensions (moz: commands, events, parameters, capabilities),
  bug 2057588; script.message event context field fixed for preload scripts
  triggered by window.open, bug 2079905; Set-Cookie handling fixed so
  newline-separated values appear as individual entries (also
  proxy-authenticate, www-authenticate), bug 1940389;
  network-events monitoring stopped computing unused security details (page-load
  perf), bug 2075175; runtime.PlatformInfo now returns arch as arm64 (was
  aarch64), bug 2080310; runtime.MessageSender gains a windowId property,
  bug 2072133.
- Firefox 161 BiDi items (MDN): script.callFunction now returns invalid
  argument when an argument or the this value contains a local value with an
  unknown type, including nested values (previously silently replaced with
  undefined), bug 2084105; script.evaluate and script.callFunction no longer
  clear a pre-existing user activation flag when called with userActivation:
  false, bug 2084107; browsingContext.navigate / reload hang/wrong-error fixed
  when a navigation starts while the previous document is still loading,
  bug 2088640; browsingContext.setViewport per-call slowdown over session
  lifetime fixed, bug 2084362; network.continueRequest now updates
  Content-Length when replacing a body that already had one, bug 2088814.
  User-facing notes also say "fixed bugs related to multiple WebDriver BiDi
  commands".
- Sources: https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/160;
  https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/161
- Impact: none for the RDP lane (all BiDi-side). Watch for a future BiDi
  client: the arm64 string change breaks any client that string-matches
  aarch64, and the stricter callFunction errors plus the navigate-hang fix are
  exactly the class of bug a BiDi migration would need to re-verify. Mozilla
  BiDi milestones: M21 done 27 Sep 2026; M22 is "In Development" with goal
  listed as TODO. No milestone in the window targets RDP or announces a
  protocol switch.
  Source: https://wiki.mozilla.org/WebDriver/RemoteProtocol/WebDriver_BiDi

### U6. Firefox 160 Enterprise DisableDeveloperTools policy, DISPUTED between lanes, quarantined, impact none
- Lane B and lane C claim: the Firefox 160 Enterprise release notes say the
  DisableDeveloperTools policy "can now disable remote automation (WebDriver
  BiDi and Marionette) without a restart".
  Source cited by B and C:
  https://www-dev.springfield.moz.works/en-US/firefox/enterprise/160.0/releasenotes/
  (opened and read).
- Lane A disputes it: the official Firefox 160 administrator release notes
  were read in full and list no such change (new policy is only
  DisableMacOSUserPolicies; other items are Cookies, Enterprise
  studies/Normandy lock, telemetry lock, SitePolicies fix).
  Source checked by A:
  https://firefox-admin-docs.mozilla.org/release-notes/version/firefox-160/
  (opened and read; claim absent).
- Resolution in this file: UNVERIFIED. The springfield.moz.works host is a
  Mozilla dev host (www-dev.springfield.moz.works), not the published admin
  docs, so the two lanes read different documents. What would establish it: an
  entry in the published Firefox 160/161 admin docs or the implementing bug
  number. See section 4, Q2.
- Impact: none for our lane even if true (enterprise policy, default off; the
  owner machine sets no enterprise policies; and the claim names BiDi and
  Marionette, not the DevTools RDP server). Drill check carried to section 3:
  confirm no policies.json / active policy exists on the owner machine
  (one about:policies check).

### U7. Zen stable releases in the window: four bumps, none touching the debugger server, none
- Zen 1.24b (changelog 28 Oct 2026, Firefox 159.0, MFSA 2026-118): Arc/Dia
  Spaces and Profiles import, shareable Boosts, Paste and Search on
  new-tab-button hover, Library tab add/remove, tab-not-visible indicator,
  keyboard shortcuts moved to about:keyboard, Space Routing moved to Library.
  Fixes include glance tabs not appearing on the right Space (#16080) and
  Wayland tab-detach issues.
- Zen 1.24.1b (changelog 5 Nov 2026, Firefox 159.0.1, MFSA 2026-123): theme
  picker grain options, SF Symbols icons on macOS, redesigned About Zen.
  Fixes: command-prompt window flashing on Windows when Zen restarts to apply
  an update, passkey sign-in across related sites, Windows AV crashes, WebGL
  red/blue swap on Linux.
- Zen 1.24.2b (changelog 11 Nov 2026, Firefox 160.0, MFSA 2026-125):
  downloads pause button, semi-transparent urlbar, PiP playback speed
  0.25x-2.0x, MathML in saved PDFs, mailto "Never allow", MKV playback,
  Metal WebGL on macOS. Fixes include NTLM/Kerberos sign-in freeze and macOS
  background-link focus.
- Zen 1.24.3b (changelog 17 Nov 2026, Firefox 160.0.1, MFSA 2026-130):
  copy-URL shortcuts copy all selected tabs, zoom button hidden in
  single-toolbar layout (toast instead); fixes for closed browser/popup windows
  never freed from memory, split-view/glance tabs unloaded under memory
  pressure (#16624), Spaces Sync for built-in containers (#16614), ChatGPT tab
  crashes, Wayland WebGL/canvas colors, PDF thin lines on Windows.
- Sources: https://zen-browser.app/release-notes/;
  https://github.com/zen-browser/desktop/releases (both opened and read, bodies
  agree). No release in the window mentions remote debugging, Marionette,
  devtools prefs, or the debugger server. Latest stable as of 28 Nov 2026 is
  1.24.3b. No Zen release on Firefox 161 yet; the next Zen update will
  likely jump to Firefox 161, so re-verify silent attach on that drill.
- Date note: one secondary source (linuxcompatible.org) claims 1.24.2b runs
  Firefox 159.0.1; the official changelog and the GitHub release body both
  say Firefox 160.0. Official sources win.
- Impact: none, with two watch notes carried to section 3: (a) the 1.24.3b
  Spaces Sync fix creates missing built-in containers on profiles that lack
  them, the only in-window change that writes to profile state; (b) the
  split-view/glance tab-unload fix changes tab lifecycle under memory pressure
  in a direction favorable to tab-list stability.

### U8. Firefox 159 changes adjacent to the lane, watch (two items), otherwise none
- (a) Removed the --remote-allow-system-access command-line argument
  (bug 2054896); system access is now enabled with the
  MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 environment variable instead. Impact: none
  for our lane (we do not pass that flag; we use --start-debugger-server,
  and the R10 live proof on Firefox 160 passed without it). Watch only if a
  future lane ever needs system-level remote access.
- (b) "Recommended preferences are now set as default values instead of user
  values, so they no longer remain in prefs.js after an unclean shutdown"
  (bug 2074275). Impact: watch. Our RDP prefs live in user.js (user values),
  not "recommended" prefs, so unaffected in principle; verify the user.js
  prefs still take effect after the next Zen update as part of the post-update
  drill.
- Firefox 159 was released 27 Oct 2026, one day before the window; it is the
  base of Zen 1.24b/1.24.1b. Otherwise BiDi-only: emulation.setMediaFeaturesOverride
  (bug 2064354) and CDDL for moz: extensions (bug 2057588). No RDP/Marionette
  changes.
  Source: https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/159

### U9. Zen Twilight 1.25t: Little Zen + Zen's own settings window, watch
- Claim: Twilight now has its own settings window instead of Firefox's
  preferences page, and a "Little Zen" mini-window. Both are Twilight-only,
  not in any stable release in the window. A Zen-owned settings window could
  eventually change how prefs are presented or managed, but it changes no pref
  values and does not touch the debugger server.
- Source: official changelog, Twilight section (undated); corroborated by
  Bugzilla 2087883, which runs Zen Twilight 1.25t on Gecko 159.
- Impact: watch. Re-check when it reaches stable.

### U10. Bugzilla 2087883: WebDriver version gates read Zen's own version string, watch for future tooling
- Claim: Zen Twilight 1.25t (Gecko 159, macOS) started with --marionette
  --remote-debugging-port; @mozilla/firefox-devtools-mcp 0.10.7 refuses
  screencast/profiler/moz:debugging with "Screencast recording requires
  Firefox 154 or later (connected: 1.25t)". Cause: the server stores
  browserVersion ("1.25t", Zen's own version) and compares it against
  154/153. The underlying BiDi commands work when called directly (screencast
  returned a path, stop closed a 112,862-byte webm). Zen returns browserName
  "zen", browserVersion "1.25t"; the Gecko version is only in the userAgent
  ("rv:159.0 ... Firefox/159.0"). Bug status UNCONFIRMED in Bugzilla, opened
  ~1 Nov 2026; the status does not change the claim, which is about what the
  bug page reports.
- Source: https://bugzilla.mozilla.org/show_bug.cgi?id=2087883 (opened and read)
- Impact: none for the RDP lane (it uses the remote debugger protocol
  directly and does no version gating). Watch: any future tooling we adopt
  that gates on browserVersion must be checked against this. Same version-string
  class of issue as Zen issue #14744 (opened 28 Jul 2026, out of window):
  the remote gfx blocklist matches Zen's app version instead of the Gecko
  version, permanently disabling hardware video overlay.

### U11. Google WICG "Agentic extensions for WebDriver BiDi" proposal, watch
- Claim: Google engineers published a WICG proposal for permission-gated BiDi
  sessions: sessionType "restricted" in session.new starts with an empty ACL,
  session.setAcl grants origins/commands/events, with a proposed session.changed
  event and per-tab actuation indicators. Intent to Prototype was posted to
  blink-dev on 19 Nov 2026; Chromium issue 587865766 was filed 19 Nov 2026;
  the Chromium BiDi mapper already prototypes goog:sessionType "restricted"
  and goog:session.setAcl. Chrome Platform Status lists it as Proposed / in
  Incubation, with no confirmed release schedule and no formal signals yet
  from Mozilla or Apple.
- Source: https://windowsforum.com/news/google-proposes-webdriver-bidi-permissions-to-limit-ai-browser-agent-access.453803/
  (opened and read); Chromium issue number/date and blink-dev Intent date via
  search excerpts of https://newsanalysis.net/google-mirror-dimension-chrome-ai-agents/ and https://groups.google.com/a/chromium.org/g/blink-dev
- Impact: watch, not breaking. If this graduates to the standard and Mozilla
  adopts it, a future BiDi-based lane would run under a permission model; the
  RDP lane is unaffected today. Its framing is relevant to our pill/consent
  design: it pushes per-tab actuation indicators and pause/revoke into the
  browser.

### U12. Bug 2081635: Mozilla firefox-devtools-mcp moving to a BiDi-only session, watch
- Claim: open task (status NEW) to remove the selenium-webdriver dependency
  from Mozilla's Firefox DevTools MCP server and use a WebDriver BiDi-only
  session, since all tools are moving to BiDi. Notes open questions about
  --connect-existing and Android mode without the classic session.
- Source: https://bugzilla.mozilla.org/show_bug.cgi?id=2081635
  (read via search result text)
- Impact: watch. It concerns Mozilla's MCP server, not the RDP lane, but it
  confirms the direction of travel in U2. Corroborated by the scan: Finding 1
  of improvements/last30days-scan-20261128.md (VERIFIED) records the same
  BiDi-only move in the shipped v0.11.1.

### U13. Bug 1915891: Remote Protocol documentation overhaul, none
- Claim: open task (P2, NEW, updated 27 days ago) to overhaul Remote Protocol
  documentation in firefox-source-docs and the Mozilla Wiki to reflect CDP
  deprecation and the current state (BiDi as the supported remote protocol,
  CDP listed only until Firefox 140 ESR support ends). Documentation work,
  no protocol change.
- Source: https://bugzilla.mozilla.org/show_bug.cgi?id=1915891
  (read via search result text)
- Impact: none.

### U14. No Zen issue in the window reports the debugger server failing after an update, none
- Claim: searches of the Zen GitHub issues list and targeted queries for
  remote debugging / debugger-server / automation failures found open issues
  about crashes, tab restore, Wayland rendering, and memory, not remote
  debugging. Search terms used: "remote debugging", "debugger-server",
  "automation failures" on the Zen GitHub issues list. The most recent
  devtools-related Zen fix is gh-15261 ("devtools not appearing on glance
  tabs"), fixed in 1.23.4b on 20 Oct 2026, 8 days before the window, out of
  scope; it concerns the devtools UI, not the RDP protocol. Lane B rated the
  glance-tab fix watch (minor): if a driven target ever sits in a glance tab,
  DevTools visibility there was broken before this fix. This file rates it
  none: the fix shipped before the window, and the RDP lane attaches at the
  debugger-server level, not through the DevTools UI, so it has no direct
  effect.
- Impact: none.

## 3. Watch list for the next Zen update drill (and the next sweep)

Runner: the live/coordinator lane on the owner machine, not mei (mei does no
live work; owner Zen is read-only for her). The R10 drill is documented in
improvements/r10-switch-report-20261127.md (commit 91547db1): it stays open
until the first post-update drill passes (smoke test
scripts/zen-rdp/rdp_smoke.py plus a Google spot check before agent use resumes
after a Zen update). The checks below extend that drill; each is a check, not
a change.

1. Silent attach and RDP prefs: with prompt-connection=false in user.js, attach
   and confirm no connection prompt appears, the debugger server accepts the
   session, and the RDP prefs are in effect (U1, U8b). This merges the two
   draft items, which had no distinct observable between them.
2. Profile intact: one-time catch-up check for the 1.24.3b update, verify the
   profile after the update, including the built-in containers the 1.24.3b
   Spaces Sync fix creates (U7a).
3. Tab count: the R10 drill's tab-count check (tab decode after settle, count
   and hash identical to before the update), which also covers tab-restore
   counts after the update (U7b, Q4).
4. Policies: confirm no policies.json / active enterprise policy exists on the
   owner machine, one about:policies check (U6).
5. Tab list under memory pressure: procedure-TBD, not a runnable check yet.
   Measurement is defined (tab count from the RDP tab list, before and after
   the pressure step); the pressure step and the pass threshold are not
   defined in any source and must be set by the drill owner before running
   (U7b).
6. Re-checks for the next sweep: any Mozilla signal on the WICG
   restricted-session proposal (U11); the scope of the DisableDeveloperTools
   policy (U6); any Mozilla timeline for Marionette removal (section 4, Q3);
   the exact text of the WICG explainer (section 4, Q5); and U9 (re-check when
   the Twilight settings window reaches stable; signal: a stable Zen release
   whose changelog lists the Zen-owned settings window).

## 4. UNVERIFIED quarantine

Cross-lane conflicts: U6 (see Q2). Nothing in this section is stated as fact
elsewhere in this file. Each item names what would establish it.

- Q1. Exact version/date and mechanism of the prompt-connection forcing (U1).
  Bug 2095150 describes the revert, not the forcing change. What would
  establish it: searchfox blame on the devtools.debugger.prompt-connection
  definition in StaticPrefList.yaml / all.js, or the Nightly changelog for
  the forcing bug. Impact if established either way: the drill check in
  section 3 item 1 stays mandatory until the mechanism is known.
- Q2. Whether the Firefox 160 DisableDeveloperTools policy change (U6) is
  real. Lanes B and C read the dev enterprise notes; lane A read the
  published admin docs and found no such entry. What would establish it: an
  entry in the published Firefox 160/161 admin docs or the implementing bug
  number. Sub-question (lane B E1): whether the policy also disables the
  DevTools debugger server started by --start-debugger-server, or only
  BiDi/Marionette. What would establish it: the policy documentation at
  firefox-admin-docs.mozilla.org or the Firefox source for the policy. An admin
  reference (URL not recorded) reportedly confirms the policy sets
  devtools.policy.disabled and blocks about:debugging /
  about:devtools-toolbox; unverified until the URL is recorded.
- Q3. Whether Mozilla has any internal timeline for Marionette removal beyond
  the 2023 wpt-executor meta-bug 1816085 (lane B C1). Nothing in the window
  addresses it. What would establish it: a Mozilla roadmap or announcement;
  none found.
- Q4. Zen dev PR #16716, "Perform better session backup recovery and reserved
  storage" (merged 19 Nov 2026, closes issue #14276 "All spaces, pins and
  essentials are gone"). Basis is a GitHub Pulse listing only; the page content
  is JS-only and did not render, and the PR body and diff were not opened.
  What would establish it: open PR #16716 on github.com/zen-browser/desktop
  and read the diff. Why it matters if verified: session backup/recovery
  touches the same sessionstore state the task-56 tab restore depends on. It
  merged to dev after 1.24.3b shipped (17 Nov), so it is not in any stable
  release in the window; it is a candidate for the next stable.
- Q5. The exact text of the WICG agentic-BiDi explainer (U11). Secondary
  coverage was read (WindowsForum article, opened); the explainer repo itself
  was not opened (no verbatim URL was returned by search). The Chromium
  mapper behaviour quoted in U11 comes from a package-stats mirror excerpt,
  not the mapper source.

## Sources

All sources were opened and read on 2026-11-28 by lanes A, B, or C, except
where marked "read via search excerpt", "read via search result text", or
"search excerpts" in the entries above. Full lane reports (working files, not committed):
~/workspace/pain-point-sweep/lanes/lane-a-firefox-rdp.md,
lane-b-bidi.md, lane-c-zen-releases.md. Council and redteam reviews plus the
scan verification report (working files, not committed):
~/workspace/pain-point-sweep/review/council-1-fidelity.md,
council-2-executability.md, council-3-completeness.md, redteam.md,
scan-verification.md.
