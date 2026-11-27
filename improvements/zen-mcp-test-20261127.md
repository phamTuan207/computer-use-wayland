# zen-mcp 0.6.0 isolated test + measurement vs the RDP lane

Date: 2026-11-27 (22:18-22:40 +07). Owner-approved isolated install and
test of @spaxe-dev/zen-mcp@0.6.0 after Clone2's code audit
(improvements/zen-mcp-study-20261127.md) concluded SAFE under conditions.
This report is the measurement half of that pipeline. Nothing was
integrated; integration scope is a council+redteam decision after this
report.

## Method and safety frame

- Pinned install: `npm install @spaxe-dev/zen-mcp@0.6.0` into a throwaway
  directory under /tmp on the laptop. Never @latest. The onboard and
  update commands were never run.
- zen-mcp ran with its own dedicated agent profile under /tmp, its own
  config and data directories under /tmp, `ZEN_MCP_NO_UPDATE_CHECK=1`,
  and `ZEN_MCP_ZEN_PATH` pointing at the installed Zen binary. The
  owner's real Zen profile was never attached, read, or written; the
  owner Zen process (same PID before and after, startup probe CLEAN,
  RDP port 6021 listening) was verified untouched at the end.
- `--use-default-profile` was never used. Test pages were three local
  fixtures served on 127.0.0.1 (page1: form with labelled inputs and a
  Submit button; page2: table page; big: 100 items x link+button+value,
  300 controls). No real accounts, no cookies, no sensitive data.
- Test windows ran headed on the agent workspace (ws2). Drives were via
  Marionette (zen-mcp) and RDP (our lane) on throwaway profiles only;
  no computer-use pill mechanism exists for these lanes (known gap,
  already a campaign task), so no pill was shown. No owner tab or
  window was closed, moved, or navigated. Test processes were killed
  by recorded profile match only.
- Egress was monitored (ss sampling every 3 s), not blocked. See the
  egress findings below; they are stated plainly.
- Two zen-mcp runs: research surface (17 tools, autoLaunch on, the
  product default) and full surface (55 tools, explicit zen_launch).
  One RDP run: dedicated throwaway session, --start-debugger-server
  9225, rdp_client.py from the landed integration tree
  (scripts/zen-rdp), --allow-unmarked-test-attach --unscoped-test
  (throwaway profile, fixture pages only).
- Config deviation, disclosed: `requireConsent: false` in the test
  config (their documented config key) so the benchmark did not need a
  human click per run. The profile was throwaway; the consent card
  itself was not tested.
- Timing: wall-clock per call from a stdlib Python MCP client
  (zen-mcp) and per CLI invocation (RDP). Single runs, not medians;
  localhost fixtures, so network variance is near zero. Treat small
  differences as indicative, not precise.

## (a) Install safety confirmation

- Installed version is exactly 0.6.0 (package.json verified after
  install). The package ships LICENSE, README.md, dist/, package.json.
  Its scripts are build/dev/start/typecheck/test/prepack only: no
  preinstall, install, postinstall, or prepare. The install log shows
  "added 98 packages", no script execution.
- Direct runtime dependencies are exactly the four the audit listed:
  @modelcontextprotocol/sdk, commander, ws, zod.
- Tool-surface equivalence (the audit's pre-measure condition) was
  verified by the previous worker: src/mcp/catalog.ts byte-identical
  between the v0.6.0 tag and HEAD, same 55 tool names; bridge diffs
  are additions only.
- Runtime egress, observed: the zen-mcp server process held only
  loopback connections (Marionette 127.0.0.1:2828 and the bridge
  WebSocket on an ephemeral loopback port). No external connection
  from the server process in either run; the npm version check stayed
  off under ZEN_MCP_NO_UPDATE_CHECK=1.
- The test Zen browser process itself made two external TLS
  connections (IPv6 :443) during the full-surface run. That is stock
  Firefox/Zen background traffic on a fresh profile (telemetry /
  remote-settings class), not zen-mcp traffic, and no owner data was
  involved (throwaway profile, fixture pages). Egress was monitored,
  not blocked, so this is an observation, not a prevention result.
- Live safety behaviours observed: zen_read_page refused about:blank
  with a typed `privileged_page` error; ambiguous semantic targets
  were refused with a typed `target_ambiguous` error; the server
  wrote its own audit.jsonl (65 entries) in the test data dir.

## (b) Measurement table (same fixtures, same machine)

Times are per-call wall-clock. zen-mcp calls ride one persistent MCP
connection (no process start per call). RDP calls are one-shot CLI
invocations (Python process start + attach + evaluate each time,
~50 ms floor). That asymmetry is part of each lane's real cost shape
today; the RDP library used in-process would amortize attach.

### Context payloads (the "initial context" claim surface)

| Payload | Bytes | Notes |
| --- | ---: | --- |
| zen-mcp initialize response | 1,479 | instructions 1,145 chars |
| zen-mcp tools/list, research (17) | 35,235 | product default surface |
| zen-mcp tools/list, full (55) | 83,261 | |
| research vs full, same version | -56.9% | chars, incl. instructions |
| research 0.6.0 vs their 0.5.0 baseline (95,852 chars / 21,807 tokens) | -62.0% | chars; claim is 62.9% in tokens |

### Launch / attach

| Op | zen-mcp | RDP lane |
| --- | ---: | ---: |
| Server/process start to ready | initialize 130 ms; browser ready 1,208-1,216 ms (launch incl. Marionette connect, nonce proof, bridge injection, lockdown) | RDP port listening 503 ms after process start (fresh profile + devtools prefs); first probe OK after a 3 s settle (ready <= 3.5 s) |
| Attach+probe per call | status 2-6 ms (persistent) | probe 58-85 ms (fresh process each call) |
| tabs list | 2.2-6.1 ms | 52 ms |

### Open / navigate / read

| Op | zen-mcp | RDP lane |
| --- | ---: | ---: |
| Open page1 (new tab) | 176-214 ms call; URL settled 179-226 ms | n/a (no tab-open in content lane) |
| Navigate pinned tab to page1, wait readyState complete | n/a (open is the primitive) | 104 ms |
| Read page1 snapshot | 13.5-14.9 ms, 4,323 B | 52 ms, 1,238 B (agent-written DOM-walk JS via eval) |
| Read page1 semantic | 8.2-18.0 ms, 5,088 B | n/a |
| Read page1 text | 3.8-5.2 ms, 996 B | innerText eval 53 ms; raw outerHTML 1,118 chars |
| Read big snapshot (300 controls) | 17.8-20.3 ms, 51,082 B | 54 ms, 25,919 B (same agent JS, cap 200) |
| Read big text | 4.9-5.5 ms, 6,624 B | raw outerHTML 13,378 chars |

### Interaction (form flow on page1, verified end-to-end both lanes)

| Op | zen-mcp | RDP lane |
| --- | ---: | ---: |
| Type "Bench User" into Name field | 154.6 ms (by label, WebDriver sendKeys actor) | 52 ms (JS value set + input/change events) |
| Click Submit | 138.8 ms (by role+name, WebDriver click actor) | 51 ms (JS find + .click()) |
| Verify "Submitted: Bench User" | find_text 5.8 ms; wait_for 3.5 ms | eval status text 50 ms |
| Ambiguous target (text "Action" on big) | refused in 5.4 ms, typed error | n/a (no ambiguity detection; JS find takes first match) |

### Tabs / Spaces / Folders

| Op | zen-mcp | RDP lane |
| --- | ---: | ---: |
| tab select | 65.8 ms | n/a (one pinned tab per client) |
| tab close | 7.6 ms | n/a |
| spaces list | 3.4 ms | 67 ms (peval gZenWorkspaces.getWorkspaces) |
| space create | 127.3 ms | 73 ms (peval createAndSaveWorkspace) |
| folders list | 1.7 ms | introspection only (55 ms method list) |
| folder create + add tab | 171.3 ms | 99 ms (peval gZenFolders.createFolder) |

### Events and ask

| Op | zen-mcp | RDP lane |
| --- | ---: | ---: |
| Event read after navigation | 0.7 ms; events carry ms timestamps (tab opened/selected at open time) | no event feed (client discards unsolicited packets); poll-based detection of page2 took 157 ms total (navigate + first 100 ms-interval poll) |
| zen_ask, waitSeconds=5, nobody answers | blocked 5,006 ms, returned pending + questionId; zen_answers listed it pending | no equivalent |

zen_ask caveat: the server-side flow (pending, questionId, late-answer
listing) is proven. The in-browser card's visual render was not
screenshot-verified; the test window was closed before a cross-check.

## (c) Verified / refuted claims

1. "62.9% reduction in initial context usage": SUBSTANTIALLY VERIFIED
   under the vs-0.5.0-baseline reading. Their own budget file sets
   the baseline at docs/context/baseline-0.5.0.json (full surface,
   95,852 combined chars / 21,807 tokens, tiktoken cl100k). Measured
   0.6.0 research surface: 36,380 combined chars, a 62.0% reduction
   by chars. The exact 62.9% is a token count with their tokenizer;
   my char-based figure lands within a point of it. Under the
   same-version reading (research vs full at 0.6.0) the reduction is
   56.9%. Either way the mechanism is real: progressive disclosure
   (17 listed tools + search/use gateway) roughly halves the initial
   payload. It is a tool-definition saving, not a page-read saving.
2. "55 tools": VERIFIED (tools/list under full surface = 55).
3. Snapshot/semantic reads with bounded payloads and completeness
   accounting: VERIFIED live (snapshot 4,323 B on page1; 51,082 B on
   the 300-control page, consistent with their element cap; semantic
   format returns a structured model). Note: on these synthetic
   pages both their snapshot and my agent-written equivalent exceed
   raw HTML size (element records duplicate text). The snapshot value
   is structure + refs + accounting, not byte savings vs raw HTML.
4. Semantic targeting with ambiguity refusal: VERIFIED (role+name
   click, label type, typed refusal on ambiguous text). One blemish:
   the refusal said "text matches 6 elements" on a page with 100
   matching buttons; the candidate count appears capped or sampled,
   which could mislead a caller about the true match count.
5. Browser events (push, cursor, long-poll): VERIFIED (events with ms
   timestamps delivered on read; backlog read 1.2 ms).
6. zen_ask human-in-the-loop: PARTIALLY VERIFIED (pending flow and
   late-answer listing proven; card render not visually checked;
   answering path not exercised).
7. Spaces/Folders as first-class context: VERIFIED (list/create in
   1.7-171 ms, typed results).
8. "Windows-only live-tested; Linux CI-only": this run is a live
   Linux data point against that: launch, bridge injection, and every
   tested tool worked on Zen 1.24.3b on this machine. One machine,
   one build; not a general Linux guarantee.
9. Their tabs_open returns before the page loads (URL field lags at
   about:blank while the title is already set). Callers must wait:
   zen_wait_for exists but is core-surface only, so research-surface
   callers poll tabs_list or consume events. Observed live; a real
   sharp edge for the default surface.

## Defects found in our own lane during this test

1. `rdp_client.py bench` subcommand failed on the dedicated test
   session: `wait_load timeout for 'slice'` after 30 s. Our defect;
   the bench subcommand's load-wait needs a look.
2. Deployment drift: the machine-layer copy of rdp_client.py lags the
   landed code (no I17 --wait-for/--wait-timeout on navigate/eval).
   The benchmark used the landed tree copy. The deployed copy should
   be refreshed or the drift made explicit.
3. A fresh-profile RDP session needs the devtools user.js prefs
   (remote-enabled, chrome.enabled, prompt-connection=false,
   remote-host/port) or --start-debugger-server never listens. One
   headed launch without prefs died with child "channel error" exits
   (cause not fully isolated; with prefs, two launches worked). A
   small launch helper for dedicated RDP sessions would remove this
   footgun.

## (d) Adoption recommendations (for council + redteam)

Ordered by expected value. Time savings are estimates, labelled as
such; none of this was integrated.

1. Snapshot command for zen-rdp. A fixed, server-authored read script
   returning a bounded result in their shape (text preview cap,
   element cap, completeness flags, snapshotId) instead of arbitrary
   eval for page reads. Measured basis: their snapshot read is
   13-20 ms over a persistent connection with disciplined payloads;
   ours is an agent-authored JS string per call site (~52 ms per CLI
   call plus authoring risk). Expected saving: fewer think-steps per
   read and bounded token spend on real pages. Extends queue items
   Q3/Q5 and the I5 accounting discipline to the page DOM.
2. Snapshot-qualified refs with digest re-verification and ambiguity
   refusal on the page DOM (extend the I3 pattern from the AT-SPI
   lane). Their refusal fired in 5.4 ms with a typed error; our eval
   path silently takes the first match. Expected saving: fewer
   wrong-element actions and retries, our known failure class.
3. Browser event feed in rdp_client. Stop discarding unsolicited RDP
   packets; keep a bounded event log (tab changes, navigation,
   target destruction) with cursor read and long-polling in their
   zen_events shape. Expected saving: wait_for polling burn (F11)
   shrinks; state-change detection becomes push instead of
   interval-bound (157 ms poll detection measured here on localhost;
   the gap grows on real pages).
4. Typed Spaces/Folders surface in the RDP parent context
   (list/create/move/switch) instead of raw chrome JS per call site.
   Measured: peval equivalents work (67-99 ms) but every caller
   hand-writes gZenWorkspaces/gZenFolders JS and discovers method
   names by introspection. Expected saving: fewer authoring errors,
   one audited implementation.
5. Progressive disclosure IF an MCP surface is ever built over
   zen-rdp: small default tool set + search/use gateway. Their
   measured default payload is 35 KB for 17 tools; our surface is
   far smaller today (7 subcommands), so this only matters if the
   surface grows. Pattern worth copying, numbers not needed yet.
6. zen_ask-style ask surface: spike through the parent context. The
   transferable part is the interaction contract (card in browser,
   blocking wait with pending fallback, late answers via a companion
   call), not their chrome code. Unproven on our lane; needs a spike
   before any commitment.
7. Launch-nonce ownership proof for split-profile sessions (nonce
   written at launch, read back through the browser) as a complement
   to our port-owner profile-marker gate.

Not to adopt: the owned-browser-only model (conflicts with our core
requirement to drive the owner's live Zen; zen-mcp refuses to attach
to a running browser at all, which is the single biggest design
difference and, for us, disqualifying as a replacement), npm
distribution for our channel, the update-check phone-home pattern,
and history access without allowlist filtering.

Bottom line: zen-mcp is a credible, disciplined piece of work whose
semantic layer, event feed, and Spaces/Folders surface are ahead of
our RDP channel, while our channel is ahead where it matters most for
this project: driving the owner's real live session, delivery/retry
semantics, attach-time defence in depth, and zero supply chain. The
fastest path is to port their five ideas (snapshot, refs+digest,
events, Spaces/Folders surface, ask contract) into zen-rdp, not to
adopt zen-mcp itself.

## Cleanup and verification

- Test Zen instances (agent-profile and rdp-profile3) killed by
  profile match; test server processes exited; fixture server stopped;
  the whole /tmp test tree removed after numbers were extracted.
- Owner Zen verified after cleanup: same PID as before the test,
  startup probe CLEAN (mode full), RDP 6021 listening, no test ports
  (2828/9225) left listening.
- Event logged via the master event log helper.

## Sources

All accessed 2026-11-27.

- Audit: improvements/zen-mcp-study-20261127.md and
  improvements/zen-mcp-study-lanes/lane2-security.md (this repo,
  todolist-push).
- Package: https://www.npmjs.com/package/@spaxe-dev/zen-mcp
  (installed @0.6.0 exactly; package.json inspected post-install).
- Repo at v0.6.0 tag: https://github.com/spaxe-dev/zen-mcp
  (docs/context/budget.json and docs/context/baseline-0.5.0.json read
  via gh api for the context-claim check).
- Our lane: scripts/zen-rdp (landed integration tree) and
  improvements/zen-sidebar/zen_live.py for the Spaces/Folders
  parent-context calls.
