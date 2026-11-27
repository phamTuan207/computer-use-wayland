# R10 seamless-control spike W2: Zen control surface beyond BiDi (27/11/2026)

Worker W2 of the R10 seamless-control spike. Scope: measure what each
control channel can do and how fast, on throwaway headed profiles only.
The owner's live Zen was never signalled, navigated, or closed; every
test instance used a /tmp profile with --no-remote on spare ports and
was killed by recorded pid plus cmdline profile check. Pill was held
for every control test. Zen build under test: 1.24.3b.

Method note: all latencies are medians of 5 to 7 runs after warm-up,
local HTTP page on loopback, headed instances. First-run (cold)
numbers are listed separately where they differ materially.

## Headline findings

1. **RDP (DevTools Remote Debugging Protocol) does NOT set
   navigator.webdriver.** With only --start-debugger-server plus four
   devtools prefs, pages read webdriver=false with the native getter
   (`function webdriver() { [native code] }`), verified two ways
   (beacon page and RDP evaluate). This is the only measured channel
   with agent control and a clean webdriver signal at the same time.
2. **RDP evaluate is the fastest measured round-trip: 0.4 ms median**,
   ahead of BiDi (1.6 ms trivial / 0.7 ms DOM read) and Marionette
   content execute (3.5 ms). RDP also does DOM write and navigate.
3. **Marionette chrome context reaches Zen internals** (gZenWorkspaces,
   gZenFolders, gBrowser, 29 Zen globals) at 1.4 ms median eval, but
   only with MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 in the launch env.
   Without it, chrome context is refused ("System access is
   required").
4. **The extension shim works.** A temporary MV3 extension installed
   via geckodriver moz/addon/install (85 ms) runs a MAIN-world content
   script at document_start that flips page-visible webdriver from
   true to false. The chrome-observer shim route failed in two
   variants (see below).
5. **SessionStore offline control is blocked by collection behavior.**
   Zen's session file (zen-sessions.jsonlz4) decodes trivially, but it
   stayed empty (0 tabs, 0 spaces) after 21 BiDi-created tabs and
   after 10 WebDriver-created tabs. Agent-created tabs are not
   collected on any timescale tested (up to 20 s live plus shutdown).

## Latency table (medians, headed throwaway, loopback page)

| Channel | Port open after launch | Attach (warm / first) | Evaluate trivial | Evaluate DOM read | Navigate (local page) | Screenshot |
| --- | --- | --- | --- | --- | --- | --- |
| BiDi (port 9353) | 0.45 s | 26.4 ms / 974 ms | 1.6 ms | 0.7 ms | 37.6 ms | 11.7 ms |
| Marionette via geckodriver (port 2858) | 0.35 s | 20.0 ms / 1056 ms | 3.5 ms | 3.2 ms | 26.3 ms | not measured |
| Marionette chrome context | (same session) | set-context instant | 1.4 ms (chrome eval) | n/a | n/a | n/a |
| RDP (port 6020) | 0.40 to 0.56 s | connect 18.2 ms, listTabs 22.3 ms, getTarget 19 to 27 ms | 0.4 ms | 0.4 ms | accepted, not timed | not measured |
| Extension bridge (scripting.executeScript) | install 85 ms | n/a | ~4 ms in-extension; 50.4 ms bridge round-trip (poll-bound) | same path | n/a | n/a |
| SessionStore decode (synthetic 20-tab file) | n/a | n/a | 0.0 ms median (373 B compressed, 1423 B raw) | n/a | n/a | n/a |

Notes on the numbers:

- BiDi and Marionette first-attach costs (~1 s) are one-time session
  setup; warm re-attach is 20 to 26 ms. A held session pays neither.
- The extension bridge round-trip (50.4 ms) is dominated by the
  50 ms background poll interval in the spike harness, not by the
  browser: the in-extension executeScript call itself measured ~4 ms.
  A WebSocket bridge or tighter long-poll would close most of the gap.
- RDP numbers come from a minimal hand-written client (stdlib socket,
  length-prefixed JSON packets). No geckodriver or DevTools frontend
  in the loop.

## Capability matrix

| Capability | BiDi | Marionette (content) | Marionette (chrome) | RDP | Extension | SessionStore file |
| --- | --- | --- | --- | --- | --- | --- |
| DOM read | yes | yes | yes (chrome DOM) | yes | yes | no |
| DOM write | yes | yes | yes | yes (verified) | yes | no |
| Trusted input (isTrusted=true) | yes, verified via input.performActions | yes (WebDriver actions, not re-measured here) | n/a | not available via console actor (untested beyond evaluate) | no, JS click measured isTrusted=false | no |
| Screenshot | yes, 11.7 ms | yes (WebDriver, not timed) | n/a | not measured | no | no |
| Zen internals (workspaces, folders, pinned) | no | no | yes, full surface (below) | untested (parent-process targets not probed) | no | read-only if collected (it was not) |
| Tab control (create, navigate, close) | yes | yes | yes (gBrowser) | list + navigate verified | partial (tabs API) | no |
| Workspace / folder control | no | no | yes (API present, read-verified) | untested | no | no |
| Session restore control | no | no | partial (gZenSessionStore exposes init / promiseInitialized / restoreInitialTabData only) | no | no | decode yes, write unproven (file stays empty for agent tabs) |
| webdriver side-effect | true | true | true (same launch flag) | **false, native getter** | flips true to false at document_start (MAIN world) | none |

## Per-route detail and verdicts

### 1. BiDi baseline

Attach, evaluate, navigate, screenshot all work as the existing
zen_cli.py lane expects. Trusted click verified: input.performActions
produces isTrusted=true. webdriver reads true (consistent with Stage
1). Verdict: fastest full-featured page control with trusted input
and screenshots; the webdriver cost is the known trade-off.

### 2. Marionette privileged

Content lane: session create 20 ms warm, eval 3.5 ms, navigate
26.3 ms. Chrome context is refused unless the browser launches with
MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1; with it, set-context succeeds and
chrome eval runs at 1.4 ms median.

Zen internals surface found from chrome context (names only):

- gZenWorkspaces (object; 27 own keys including workspaces cache,
  active workspace tracking, pinned-tab init promises). Workspace
  list read returned the throwaway's single workspace; active
  workspace read returned its UUID.
- gZenFolders (object). ZenFolders (bare name) is undefined.
- gBrowser (object); tab count, pinned count, and per-tab attributes
  readable, including zen-workspace-id and zen-empty-tab.
- 29 Zen globals total, including gZenSessionStore,
  gZenPinnedTabManager, gZenVerticalTabsManager, gZenViewSplitter,
  gZenCompactModeManager, gZenUIManager, gZenMods, gZenGlanceManager.
- gZenSessionStore prototype exposes only constructor, init,
  promiseInitialized, restoreInitialTabData. No save or collect
  method is exposed.

Webdriver shim via chrome observer (spike): FAILED, two variants.
Variant 1 (defineProperty on the content navigator prototype from a
content-document-global-created observer) left the native true in
place, consistent with Xray-wrapper isolation. Variant 2
(wrappedJSObject) also left true, and the observer callback marker
never appeared, consistent with per-call sandbox windows in
execute/sync chrome evaluation. Verdict: Marionette chrome is the
only measured path to Zen internals and the right lane for
workspace/folder/tab-strip control, but it is not a shim delivery
mechanism. The extension route (below) is.

### 3. RDP route (the unconsidered channel)

Launch requirements, measured: --start-debugger-server alone does
NOT open the port. The port opens (0.40 to 0.56 s) only with four
prefs set: devtools.debugger.remote-enabled,
devtools.chrome.enabled, devtools.debugger.prompt-connection=false,
devtools.debugger.remote-host/port. This is a pref-gated channel,
not a flag-only channel.

webdriver verdict: **false, native getter**, confirmed by (a) a
headless one-shot beacon page under the RDP launch config and (b)
RDP evaluateJSAsync returning boolean false. The debugger server
does not set webdriver=true.

Control capability, verified with a minimal stdlib client:
root listTabs, tabDescriptor getTarget (consoleActor rides in the
frame payload; attach is not recognized on windowGlobalTarget),
evaluateJSAsync read and write, navigateTo accepted. Eval latency
0.4 ms median is the fastest measured. Not measured: screenshot,
trusted input (console actor has none), chrome/parent targets,
network or storage actors.

Risks: RDP is the DevTools internal protocol, less stable as an API
contract than BiDi or WebDriver; actor shapes changed across
versions (descriptor vs target split observed here). It also needs
devtools prefs in the profile, which is a wider config change than a
launch flag. Verdict: the only channel that gives agent control
with a clean webdriver signal today, and the fastest evaluator.
Worth a dedicated follow-up on input injection and parent-process
(chrome) targets before any adoption decision.

### 4. SessionStore

Zen does not use the classic sessionstore.jsonlz4. Its file is
zen-sessions.jsonlz4 with magic bytes "mozLz40\0" (note the extra
0 versus stock mozLz4), then uint32 LE uncompressed size, then an
lz4 block. Decode with python-lz4 works; a synthetic 20-tab file
decodes in 0.0 ms median and round-trips byte-identical through
encode/decode.

Collection behavior is the blocker: after 21 BiDi-created tabs
(20 s live wait) and separately after 10 WebDriver-created tabs, the
file still held tabs=[] and spaces=[] (67 B compressed). Live read
while running shows the same empty content; there is no locking
problem, just nothing collected. BiDi browser.close did not produce
a graceful exit within 15 s in one test, and SIGTERM shutdown also
left the file empty. Offline write-and-relaunch verification is
therefore BLOCKED, honestly: there is no collected tab to modify.
Whether collection is timer-based on a longer interval, tied to
Zen UI tab-strip events that automation bypasses, or gated on
workspace state is unknown from this spike. Verdict: do not build
session control on this file until collection triggers are
understood; chrome-side gZenSessionStore offers no save hook.

### 5. Extension bridge

Feasibility: PROVEN. A minimal MV3 extension (content script at
document_start, world MAIN; background bridge) temp-installed via
geckodriver moz/addon/install in 85 ms, no signing needed for
temporary installs. Shim probe after install: webdriver=false,
type boolean, shim marker installed-main. Getter toString reads
`get() { return false; }`, so the same toString tell as the BiDi
preload shim remains (native is `function webdriver() { [native
code] }`); closing that tell is still open work for any build.

Bridge: background long-poll to a local HTTP server, executing via
scripting.executeScript in MAIN world. Round-trip median 50.4 ms,
of which ~4 ms is the in-extension call; the rest is the spike
harness poll interval. JS click isTrusted=false (synthetic), as
expected; trusted input still needs BiDi or WebDriver actions.
Verdict: the extension is the proven shim delivery vehicle and a
viable low-latency evaluate lane once the bridge transport is
tightened (WebSocket instead of polling).

## Cross-cutting notes

- One WebDriver session at a time (Stage 1, T8) still shapes lane
  design: BiDi and Marionette sessions must be sequenced, while RDP
  and extension lanes are independent of that limit.
- First-attach ~1 s costs argue for held sessions in any hot path.
- Port discipline mattered in practice: parallel lanes collided on
  the default spare ports during this spike; W2 moved to unique
  ports (BiDi 9353, Marionette 2858, RDP 6020, geckodriver 4465)
  and reran. Any multi-lane toolset needs a port registry.
- Machine-specific configuration details stay in the laptop machine
  layer; this report describes capabilities generically.

## Evidence

VM-local evidence (not committed): ~/workspace/r10-seamless-w2/
(harness scripts w2_*.py, ext/, www/, evidence/logs/*.jsonl with
per-test JSON-line logs including full run arrays, run logs with
wall-clock timestamps). Contaminated first-run logs were discarded
and rerun on unique ports; the evidence set holds the clean runs.

## Cleanup verification

All W2 throwaway profiles removed from the laptop, no test ports
listening (9353/2858/6020/4465/8931/8932 verified closed), all W2
pill holders released, owner Zen alive and flag-free at the end
(cmdline verified, no automation flags). Parallel lanes' instances
were left untouched.

## Evidence labels

- VERIFIED: BiDi latencies and trusted click; Marionette content
  and chrome latencies; chrome-context refusal without system-access
  env and success with it; Zen internals surface listed above;
  chrome-observer shim failure (2 variants); RDP pref requirement,
  webdriver=false (2 independent reads), RDP evaluate/write/navigate
  and 0.4 ms latency; extension install, document_start MAIN-world
  shim, bridge latency split, JS click isTrusted=false;
  zen-sessions.jsonlz4 format, decode cost, and empty collection
  for agent-created tabs (BiDi and WebDriver).
- ASSUMED: RDP parent-process targets could reach chrome internals
  (not probed); extension bridge latency would drop to single-digit
  ms with a WebSocket transport (in-extension call measured ~4 ms);
  Marionette WebDriver actions produce trusted input (standard
  behavior, not re-measured in this spike).
- BLOCKED: SessionStore offline write verification (no collected
  tabs to modify); RDP screenshot and trusted input (not measured).
