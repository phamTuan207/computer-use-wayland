# R10 seamless-control REDTEAM (27/11/2026)

Independent redteam for the R10 seamless-control decision. I attack
every route, especially the fashionable one (RDP). I do not build or
test; I find what breaks, what is unproven, and what the councils
will underweight.

Owner ruling 27/11 12:08 (fixed): seamless same-session agent
control of Zen; split rejected as end state; team chooses method;
full control surface beyond BiDi; speed is the headline; dedicated
build weighted as a serious primary candidate; machine-specific
layer stays laptop-only, repo stays generic. Owner criterion:
normal browsing plus Google search with no Cloudflare block AND
agent computer-use at any time in the same session.

Evidence base (all 27/11, throwaway headed profiles, same machine,
same IP, one day): r10-stage1-report, r10-stage2-decision,
r10-stage2-redteam (S1-S8, B1-B9, A1-A7), r10-a5-report,
r10-split-adoption, r10-seamless-w1-shim-spike,
r10-seamless-w2-control-surface, r10-seamless-w3-relaunch.

Routes under attack:
- R1: flagged always plus shim (holder preload, v3 best case)
- R2: attach-on-demand relaunch (flag-free browsing, flagged
  relaunch per agent call, relaunch back)
- R3a: RDP-based dedicated build (DevTools Remote Debugging
  Protocol, pref-gated debugger server)
- R3b: extension-bridge dedicated build (persistent extension as
  control and/or shim lane)
- R3c: hybrid toolset (multiple channels, channel selection)
- R3d: other combos (e.g. RDP plus OS-level input, extension plus
  RDP, Marionette-chrome hybrids)

Severity: CRITICAL = owner criterion fails or unproven on the
decisive leg; HIGH = real tasks break or serious risk;
MEDIUM = cost, rot, or narrow breakage. Each attack is tagged
BLOCKING (must spike before any landing) or MITIGABLE (acceptable
with a named mitigation and owner).

## Headline verdict

No route is proven against the owner criterion today. R1 is
PROVEN to fail the Google leg. R2 is PROVEN to fail leg 1 during
every agent session and to cost 46.5s of BiDi attach per call.
R3a (RDP) is the only route that could pass, and its decisive
variable - Google search entry and Cloudflare panel behaviour
with the RDP debugger server actually running and an agent
attached - has never been tested. R3b as spiked still needed a
flagged launch to install, so it inherits R1's proven Google
failure. R3c multiplies every breakage surface and its port
collisions are already observed fact, not theory. The interim
split, rejected as end state, remains the only configuration
with a proven clean human leg. Landing any seamless route before
the blocking spikes below is buying the fashionable answer on
untested evidence.

## Attacks on R3a - RDP-based build (attacked first, hardest)

### RT-01. "webdriver=false" is not the whole story, and Google is untested with RDP running
- Route: R3a. Claim attacked: RDP gives agent control with a
  clean browser, therefore the owner criterion passes.
- Evidence: W2 verified webdriver=false with native getter two
  ways (beacon page, RDP evaluate) under the RDP launch config.
  W1 verified that Google search entry blocks 6/6 under the
  BiDi/Marionette flags even with a CLEAN-grade v3 shim
  (webdriver=false), with input method and active session both
  isolated out. The Google block therefore tracks flag-correlated
  signals BEYOND page-visible navigator.webdriver. Nobody knows
  what those signals are. If they are tied to the two WebDriver
  flags specifically, RDP passes. If they are tied to "any remote
  debugging surface present", to devtools prefs, or to other
  JS-visible artifacts a debugger server creates, RDP fails the
  same way. W2 ran no Google entry and no Cloudflare panel site
  with the RDP server running. The single most decision-relevant
  measurement for R3a does not exist.
- Severity: CRITICAL. BLOCKING. Spike: Google homepage entry
  (typed query, real keyboard and agent input as separate arms)
  plus P1/P2 panel, RDP server running, agent attached, cold
  profile, flagged-raw control arm same day. Until this passes,
  R3a is a hypothesis wearing a latency table.

### RT-02. RDP has no trusted input; isTrusted=false breaks real tasks
- Route: R3a (and R3b, R3d without a trusted lane). Claim
  attacked: RDP evaluate plus navigate equals computer-use.
- Evidence: W2 capability matrix: trusted input "not available
  via console actor (untested beyond evaluate)". JS-dispatched
  clicks carry isTrusted=false (W2 measured this for the
  extension lane; the same physics applies to RDP evaluate).
  Any page can read event.isTrusted trivially. Real breakage
  classes: file-upload pickers and clipboard APIs that require
  trusted activation, fullscreen and pointer-lock requests,
  HTML5 drag-and-drop, Turnstile and CAPTCHA widgets that score
  synthetic events, OAuth consent and payment confirmation
  flows that gate on trusted gestures, keyboard-driven widgets
  that ignore synthetic keys. The frozen R3-L3 task set is
  fresh-page public sites and will under-sample exactly these.
  "Full control surface" with no trusted input is not full.
- Severity: CRITICAL for the "full control surface" requirement.
  BLOCKING for any R3a-only design. Mitigation exists only by
  adding a trusted lane (BiDi flag, which reintroduces the
  proven Google failure, or OS-level input, which reintroduces
  focus-steal and kills the speed headline) - see RT-17.

### RT-03. Screenshot and Zen internals via RDP are untested, not "assumed available"
- Route: R3a. Claim attacked: RDP can grow to cover the full
  surface beyond BiDi (screenshots, Zen workspaces/folders,
  tab-strip control).
- Evidence: W2: screenshot "not measured"; chrome/parent
  targets "not probed"; Zen internals "untested (parent-process
  targets not probed)". The only measured path to Zen internals
  is Marionette chrome context, which needs the Marionette flag
  plus MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 - i.e. the flagged
  configuration R3a exists to avoid. RDP parent-process actors
  may or may not reach gZenWorkspaces and friends; DevTools
  protocol actor shapes for chrome targets are version-specific.
  Councils will read "untested" as "probably fine". It is not
  evidence.
- Severity: HIGH. BLOCKING for the beyond-BiDi requirement.
  Spike: RDP screenshot of a real page, and RDP read/write of
  one Zen internal (workspace list, pinned tab) on this build.

### RT-04. prompt-connection=false plus a listening localhost port is a silent-attach security surface
- Route: R3a. Claim attacked: RDP prefs are just configuration.
- Evidence: W2 measured that the port opens only with four
  prefs including devtools.debugger.prompt-connection=false.
  That pref removes the one consent prompt Firefox puts between
  a local process and full JS evaluation in every tab. With it,
  any local process - any app, any compromised dependency, any
  script the owner runs, any other agent CLI with shell access -
  can attach silently to the owner's live session and evaluate
  JS in his Gmail, banking, and GitHub tabs. The port number is
  predictable (6000-class; W2 used 6020). BiDi and Marionette
  ports have the same localhost property, but R3a proposes
  making this the always-on end state on the owner's real
  profile, and explicitly disabling the prompt to do it. No
  report prices this. Also unexamined: bind address discipline
  (localhost only vs 0.0.0.0), Tailscale exposure if misbound,
  and whether the owner's other software ever forwards or
  scans these ports.
- Severity: HIGH. MITIGABLE only with named mitigations:
  loopback-only bind verified per launch, non-default port from
  a registry, prompt-connection kept true if the workflow
  tolerates it (untested), startup check that fails loud if the
  port is reachable from a non-loopback interface, and an
  explicit owner decision that silent local attach is accepted.
  Without that decision recorded, this is BLOCKING on security
  grounds alone.

### RT-05. RDP is an internal DevTools protocol, not a supported automation API
- Route: R3a. Claim attacked: build the dedicated tool on RDP.
- Evidence: W2 itself notes actor shapes changed across versions
  (descriptor vs target split observed on this very build) and
  calls RDP "less stable as an API contract than BiDi or
  WebDriver". The hand-written client already had to learn that
  attach is not recognized on windowGlobalTarget and that
  consoleActor rides in the frame payload - exactly the kind of
  undocumented shape that changes silently per Firefox release.
  Zen tracks Firefox on its own cadence; every Zen update is a
  breakage lottery for the RDP client, with no deprecation
  promise and no version negotiation guarantee. Devtools prefs
  are likewise not a supported automation surface: Mozilla can
  rename, gate, or remove them, and the failure mode is "agent
  lane dead at call time" (the S8 pattern, now on the primary
  lane). The Stage 2 kill criteria (one broken update retires
  the layer) would fire on protocol churn, not on anyone's bug.
- Severity: HIGH. MITIGABLE only with a per-update automated
  RDP smoke test (attach, evaluate, navigate, screenshot if
  claimed), a named maintenance owner, and a fallback lane that
  works when RDP breaks. Councils must price "protocol client
  maintenance forever" into the build, not just the build.

### RT-06. Concurrency with the owner's own DevTools use is untested
- Route: R3a. Claim attacked: agent attaches at any time.
- Evidence: no report opens DevTools in the same browser while
  an RDP agent client is attached, or attaches a second RDP
  client. DevTools itself is an RDP client. Whether the server
  allows concurrent clients, whether the owner's F12 session
  and the agent's evaluate interleave safely, and what happens
  to a paused-at-breakpoint page under agent evaluate are all
  unknown. The owner is a software-engineering student who will
  open DevTools in his own browser; "at any time" includes
  those times.
- Severity: MEDIUM-HIGH. MITIGABLE with a concurrency spike:
  owner DevTools open plus agent evaluate/navigate, both
  directions, recorded.

### RT-07. The 0.4ms headline is a loopback trivial-eval number and will be overweighted
- Route: R3a (and all speed claims). Claim attacked: RDP is
  fastest, therefore RDP wins the speed headline.
- Evidence: W2 latencies are medians on a local loopback page,
  warm sessions. RDP evaluate 0.4ms vs BiDi 1.6ms trivial /
  0.7ms DOM read. Real agent tasks are dominated by page load,
  network, grounding/vision, and model think time - seconds,
  not sub-milliseconds. A 1ms round-trip saving is noise in
  wall-clock task time, and W2's own table shows first-attach
  costs (~1s class) and navigate costs (tens of ms) dwarf eval
  deltas. Speed as the headline metric must be end-to-end task
  wall time on real sites, or the decision optimizes the one
  number that does not matter. (Stage 1 and the standing timing
  rule already say total wall time is the metric.)
- Severity: MEDIUM as a technical matter, HIGH as a decision
  matter: it is the number most likely to stampede the councils.
  MITIGABLE by requiring end-to-end task timings (same task,
  same site, per route) before any speed claim is scored.

### RT-08. Devtools-pref presence may itself be page-detectable; nobody looked
- Route: R3a. Claim attacked: pages see a normal browser under
  RDP.
- Evidence: pages cannot read prefs directly, but "normal" was
  certified only by the unified probe's fixed signal list
  (webdriver value, descriptor, getter toString, doc attribute,
  plugins length, fixed globals). Debugger-server presence has
  classic detection surfaces outside that list: debugger
  statement timing, console formatting side effects, DevTools
  open-detection tricks, and any JS-visible difference the
  Remote Agent or debugger server introduces. W1 proved Google
  uses signals outside the probe list (CLEAN probe, still
  blocked). The probe cannot certify RDP clean; only real-site
  behaviour can (RT-01 spike). Treating probe-clean as
  RDP-clean repeats A1 exactly.
- Severity: HIGH. BLOCKING jointly with RT-01 (same spike
  answers it behaviourally).

## Attacks on R1 - flagged always plus shim

### RT-09. R1 is proven to fail the Google leg; no shim variant fixes it
- Route: R1. Claim attacked: v3 shim plus flagged launch
  satisfies normal browsing plus Google search.
- Evidence: W1 Test 2: flagged browsers block Google entry with
  BiDi input 3/3, real keyboard plus session 3/3, real keyboard
  no session 2/2; flag-free passes 2/2. CLEAN-grade v2/v3 shims
  included. A5: flagged+shim ENTRY-CHALLENGE 7/7. This is the
  most replicated result in the whole evidence base. The owner
  criterion names Google search explicitly. R1 fails it by
  construction: the flags stay on the human's browser.
  "Use DuckDuckGo under flags" (W1 recommendation) is a
  criterion downgrade, not a pass - the owner searches with
  Google.
- Severity: CRITICAL. Not mitigable within R1. R1 is dead as
  end state; it survives only as the interim agent-profile
  configuration under the split.

### RT-10. v3 still leaks under pristine-realm attack, and fresh-profile P2 still challenged once
- Route: R1 (and any JS shim). Claim attacked: v3 closes the
  tell (B3 answered).
- Evidence: W1: v3 is byte-exact in the page realm, but a
  pristine iframe realm's genuine Function.prototype.toString
  applied to the shimmed getter returns the anonymous form
  `function () { [native code] }` - name missing, shim
  existence leaked. Any checker that creates a pristine realm
  (a standard bot-detection move) detects that a shim exists,
  even if it cannot read source. Separately, fresh-profile v3
  passed P1 but CHALLENGED on P2 once, with fresh raw
  challenging both - n=1 per cell, probabilistic scoring. The
  honest claim (W1's own words) is "passes most of the time",
  which is not the owner criterion ("no Cloudflare block").
  B3 is weakened, not closed; B7 (arms race) stands: Cloudflare
  needs one new pristine-realm check to re-open this.
- Severity: HIGH. MITIGABLE only by accepting a probabilistic
  pass rate in writing, which the owner criterion does not
  currently do.

### RT-11. Pre-existing tabs cannot be un-seen; seamless attach arrives too late for open pages
- Route: R1. Claim attacked: shim covers the owner's session.
- Evidence: W1 Test 3: evaluate-install on an already-loaded
  document fixes the live value but the page's earliest script
  already recorded webdriver=true (early=true unchanged). Only
  reload under preload gives early=false. The owner's real
  session has dozens of already-loaded tabs at any attach time;
  every one is either early-exposed or must be reloaded
  (destroying the page state seamless control exists to
  preserve - S7's whole point). B4's race is won for new
  documents and lost for the documents that matter.
- Severity: HIGH. MITIGABLE only by reload-on-attach, which
  trades away the seamless benefit. Councils must state which
  they are buying.

## Attacks on R2 - attach-on-demand relaunch

### RT-12. R2 fails leg 1 during every agent session, by design
- Route: R2. Claim attacked: relaunch gives clean browsing and
  agent control in the same session.
- Evidence: W3 confirms Stage 2's rejection reason (b): during
  the whole agent session the owner's browsing in that session
  is flagged (webdriver=true). The owner criterion requires
  clean browsing AND agent control in the same session, not
  clean browsing between agent calls. If the owner browses
  while an agent works - the normal case for "help me with
  what I am looking at" - he is flagged exactly then. W3
  corrects the "minutes to usable" pricing (window in ~1s)
  but the criterion failure is unchanged.
- Severity: CRITICAL. Not mitigable within R2.

### RT-13. 46.5s BiDi attach plus lazy-tab unreachability kills "at any time"
- Route: R2. Claim attacked: relaunch is fast enough to be
  seamless.
- Evidence: W3: BiDi session.new takes 46.5s consistently
  across five flagged launches (port listens at ~1s; delay is
  inside session.new; cause not isolated). Marionette attaches
  in ~6s. After relaunch, restored tabs are lazy: BiDi sees 1
  context, Marionette switch_to_handle does not load the
  pending document, JS navigation is denied or loses restore
  data; only an OS-level sidebar click loads a restored tab
  with its form/scroll data. JS heap state is lost every cycle,
  the active tab resets to New Tab, and tab 0 was replaced by
  about:blank in the ad-hoc profile (registered-profile
  behaviour untested). An agent called to work on the owner's
  restored tabs cannot reach them through the agent lanes
  alone. "At any time" plus 46.5s plus OS-click activation is
  not seamless; it is a restart ritual.
- Severity: CRITICAL for the speed headline and the seamless
  requirement. Not mitigable without solving the 46.5s cause
  (unisolated) and the lazy-tab activation gap (no browser
  mechanism found).

## Attacks on R3b - extension-bridge build

### RT-14. The spiked extension still needed a flagged launch; persistent install on Zen release is unproven
- Route: R3b. Claim attacked: extension bridge is feasible
  (W2 "PROVEN").
- Evidence: W2 temp-installed the MV3 extension via geckodriver
  moz/addon/install - which requires a Marionette session,
  which requires the --marionette flag, which forces
  webdriver=true and the proven Google failure. Temporary
  addons do not survive restart. A persistent end state needs
  a signed install path on Zen release builds
  (xpinstall.signatures.required, AMO signing or enterprise
  policy install), none of which was tested. An update can
  disable an unsigned or policy-loaded extension silently
  (B5 fail-open: shim gone, webdriver=true, nothing alarms
  unless the startup probe runs). W2 proved the content-script
  mechanism, not the deployment.
- Severity: CRITICAL. BLOCKING. Spike: persistent install on
  this Zen build with no automation flags, survive restart,
  survive a Zen update (or a simulated one), fail loud if
  disabled.

### RT-15. Extension detectability and the remaining toString tell
- Route: R3b. Claim attacked: extension shim makes pages see a
  normal browser.
- Evidence: W2's extension shim getter reads
  `get() { return false; }` - a worse tell than v3, source
  visible in the page realm. Beyond that, extensions have
  their own detection surface: web-accessible resources
  fetchable by pages, moz-extension:// URL probes, content-
  script injection timing, and extension-ID fingerprinting.
  None was tested. An extension that runs at document_start
  in MAIN world on every page is also a new privileged code
  path in every tab the owner opens, including banking; its
  update channel (AMO or local file) becomes part of the
  owner's trusted computing base. Native-messaging host
  variants add a privileged local process with its own
  install and security surface - unpriced in every report.
- Severity: HIGH. BLOCKING jointly with RT-14 for any claim
  of page-invisibility; MITIGABLE for a control-only extension
  (no shim claim) if detectability is accepted in writing.

### RT-16. Extension lane still has no trusted input and no screenshot
- Route: R3b. Claim attacked: extension bridge as the control
  surface.
- Evidence: W2 matrix: trusted input no (JS click
  isTrusted=false, measured), screenshot no, Zen internals no,
  tab control partial. The extension lane is an evaluate lane
  (~4ms in-extension; 50.4ms bridge round-trip poll-bound in
  the spike; WebSocket improvement ASSUMED, not measured).
  As a sole control surface it fails the beyond-BiDi
  requirement the same way RDP does (RT-02, RT-03), with a
  slower measured bridge.
- Severity: HIGH. Not mitigable within R3b alone.

## Attacks on R3c / R3d - hybrid toolset and other combos

### RT-17. Any hybrid containing a flagged channel on the human browser inherits R1's proven Google failure
- Route: R3c, R3d. Claim attacked: combine channels to get
  RDP speed plus BiDi trusted input/screenshot plus Marionette
  chrome internals.
- Evidence: Stage 1 (VERIFIED): each flag alone forces
  webdriver=true; W1: flags drive the Google block regardless
  of shim. A hybrid that keeps --remote-debugging-port or
  --marionette on the owner's browser for trusted input,
  screenshots, or chrome internals is R1 with extra steps.
  The only hybrids that escape are flag-free combos (RDP plus
  extension, RDP plus OS-level input), and those inherit
  RT-02/RT-03/RT-16 (no trusted input or no screenshot or no
  internals) or the OS-input costs (focus steal, slow lane,
  pill discipline; the 21/11 live-runner focus-steal incident
  is the precedent). There is no combination in the evidence
  base that simultaneously delivers: clean Google entry,
  trusted input, screenshot, Zen internals, and speed. Every
  combo drops at least one, and the councils must say which
  one, in writing, before scoring.
- Severity: CRITICAL. BLOCKING as a design question: name the
  dropped capability per combo or the combo is underspecified.

### RT-18. Port collisions are observed fact; the registry and channel-selection logic have no owner
- Route: R3c (and any multi-lane design). Claim attacked:
  hybrid complexity is manageable.
- Evidence: all three spikes collided on ports. W1: BiDi 9333
  held by W3's lane, NS_ERROR_SOCKET_ADDRESS_IN_USE, session
  not created. W2: parallel lanes collided on default spare
  ports, full rerun on unique ports. W3 run1: a parallel
  worker's 19 probe tabs entered the throwaway browser through
  shared port 9333 (session file showed 38-39 tabs) - i.e. a
  collision did not just fail, it cross-contaminated another
  lane's browser. W2 concludes "any multi-lane toolset needs a
  port registry". No report names who builds it, who owns it,
  how channel selection decides which lane drives a given
  task, or what happens when selection is wrong. Wrong-channel
  selection on the owner's live session is B8's blast radius
  with a new trigger: the fast lane driving the wrong tab.
  N channels also means N breakage surfaces per Zen update
  (RDP protocol churn RT-05, extension signing RT-14, BiDi/
  Marionette session limits, shim tells RT-10), each needing
  its own per-update smoke test and its own named owner (B6).
- Severity: HIGH. MITIGABLE only with a written registry
  design, a named owner, per-channel update drills, and a
  fail-closed default (no channel selected = no drive, never
  guess). Unowned, this is BLOCKING.

### RT-19. Hybrid blast radius: a bug in any lane now lands in the owner's live session
- Route: R3c, and seamless generally. Claim attacked: seamless
  control is safe enough with tab-safety discipline.
- Evidence: VERIFIED history: agent automation closed 24 owner
  tabs including 5 essentials and 3 pinned (26/11); a drill
  worker's window-close killed the owner's live Zen (27/11).
  The split removed that blast radius structurally. Seamless
  restores it by design, and a hybrid multiplies the code
  paths that can reach the live session (each channel's tab
  control, each client's close semantics, each selection bug).
  Tab-safety discipline (record before attach, never close
  owner tabs, kill by pid plus cmdline) is necessary and was
  honoured in every spike - on throwaway profiles, by careful
  workers, for hours. The end state runs it on the real
  profile, by rotating agents, forever. B8 stands at full
  force and is worse under hybrid.
- Severity: HIGH. MITIGABLE partially (record-before-attach
  enforced in the tool, not in briefs; close operations
  refused on owner tabs at the tool level), never fully.
  Councils must price the residual risk explicitly; the owner
  has already paid it twice.

## Cross-cutting attacks (all seamless routes)

### RT-20. Same-session control deletes the split's credential isolation; S2's silent-option-(c) becomes the main road
- Route: all seamless. Claim attacked: agent in the owner's
  session is acceptable because tasks need it.
- Evidence: Stage 2 redteam S2/S5: the split's safety win was
  no owner credentials in the automation blast radius. Seamless
  puts full-access agent CLIs inside the owner's logged-in
  Gmail, GitHub, Drive, banking, and Codeforces sessions, in
  tabs whose page content is attacker-controlled input to the
  agent (prompt injection via page text is a live class, not
  hypothetical). The S2 escape-hatch discipline (explicit,
  logged, per-task approval for owner-account work) was
  designed for rare exceptions; under seamless every task is
  an owner-session task, and logging discipline under time
  pressure is exactly what S2 predicted would rot into silent
  option (c). No seamless report proposes a replacement
  discipline (e.g. per-task tab scoping enforced by the tool,
  credential-tab denylist, drive-report probe plus tab-list
  diff). Without one, seamless trades a proven isolation
  property for convenience and calls it a requirement.
- Severity: HIGH. MITIGABLE only with tool-enforced scoping
  and a written credential policy for same-session work,
  approved as an owner-level security decision. Unwritten, it
  is BLOCKING on security grounds.

### RT-21. All seamless evidence is throwaway-profile evidence; the owner's real profile is a different browser
- Route: all seamless. Claim attacked: spike results transfer
  to the owner's session.
- Evidence: every W1/W2/W3 result is a fresh or lightly warmed
  throwaway profile: no history, no logged-in Google account,
  no 60-plus tabs, no extension set, no cookie warmth. W1
  itself caught warmth confounding (warmed raw P1 PASS vs
  fresh raw CHALLENGE same day). Google's unusual-traffic
  scoring with a real logged-in account and real history could
  be better (reputation) or worse (account-level flags from
  prior flagged browsing) - untested in both directions.
  Cloudflare cf_clearance carryover (A7) further separates
  spike trials from real browsing. A route can pass every
  spike and fail on the real profile, or fail spikes and pass
  for real; neither direction is evidence until the real
  profile is tested at a task boundary with the pill visible.
- Severity: HIGH. BLOCKING for acceptance (see acceptance
  test below); spikes remain valid for mechanism claims only.

### RT-22. Machine-layer vs repo-generic is unresolved for every build route (B9 returns)
- Route: R3a, R3b, R3c. Claim attacked: dedicated build,
  machine-specific layer laptop-only, repo generic.
- Evidence: RDP needs four profile prefs plus a hand-written
  protocol client plus port discipline; the extension needs a
  signing/install path; the hybrid needs a registry. None of
  that is stock-Zen generic. If the build lands in the repo
  default-on, stock users break or inherit silent-attach
  prefs (RT-04) - unacceptable. If it is machine-layer opt-in
  default-off, its only user is this laptop and the repo
  carries dead weight plus a second code path every consumer
  must reason about. The owner ruling states the placement
  principle but no report draws the line for RDP prefs, the
  RDP client, or the registry. B9 is unanswered for the new
  routes.
- Severity: MEDIUM. MITIGABLE with a written placement
  decision per component before building.

### RT-23. The one-session limit does not disappear; it moves
- Route: all. Claim attacked: seamless removes session
  serialization.
- Evidence: VERIFIED (Stage 1 T8): one WebDriver session at a
  time across BiDi and Marionette. RDP and extension lanes are
  independent of that limit (W2), which helps - but their own
  concurrency limits are unmeasured (RT-06), and any hybrid
  that falls back to BiDi/Marionette for trusted input or
  internals re-enters the one-session world, now contended by
  the owner's own browsing in the same session. Multi-agent
  simultaneous drives of one live session (two workers, one
  owner, one window) have no locking story in any report.
- Severity: MEDIUM. MITIGABLE with a session-locking design;
  currently undesigned.

## Which Stage 2 attacks (S1-S8, B1-B9) still apply under the new ruling

- S1 (lawyerly same-install): RESOLVED by the owner ruling -
  same live session is now explicit. Inverse risk replaces it:
  the team must not reinterpret "seamless" down to R2 relaunch.
- S2 (0/55 selection bias, continuity trilemma): APPLIES WITH
  FORCE. Seamless makes every task a continuity task; the
  escape hatch becomes the main road (RT-20).
- S3 (headed concurrency unproven): TRANSFORMED, WORSE. Two
  instances became one shared window; owner-plus-agent
  concurrency in a single session (focus, input interleaving,
  DevTools RT-06) is untested.
- S4 (parity rot): MOOT. One profile, nothing to sync. A
  genuine win of seamless; councils may claim it.
- S5 (credential blast-radius inversion): APPLIES, WORSE
  (RT-20). The agent profile's separate credentials problem is
  replaced by direct access to the real ones.
- S6 (launch-path leakage): TRANSFORMED. Now pref leakage:
  RDP prefs missing on a launch path = agent lane dead; any
  path adding WebDriver flags = Google dead. The startup
  probe discipline from split adoption must be re-pointed, not
  retired.
- S7 (benchmark vs real help): ANSWERED by seamless. Agents
  can act on what the owner is looking at. A genuine win;
  councils may claim it. (R2 only half-answers it: RT-13.)
- S8 (update split-brain): APPLIES, MULTIPLIED. RDP protocol
  churn (RT-05), extension signing (RT-14), shim tells
  (RT-10) each break per update on their own schedule.
- B1 (frozen coverage theatre): APPLIES to shim routes;
  REBORN for RDP as RT-08 (probe list cannot certify Google).
- B2 (spend on ASSUMED cause): PARTIALLY ANSWERED. A5/W1
  proved webdriver drives the Cloudflare panel class; the
  Google cause is still unknown (RT-01). Spending on RDP
  before the RT-01 spike repeats B2 with a new protocol.
- B3 (toString unclosable): WEAKENED by v3 page-realm exactness,
  NOT CLOSED (pristine leak, RT-10).
- B4 (document_start races): ANSWERED for new documents (W1
  race test: iframes, earliest script, dynamic iframe all
  false; worker has no property). Pre-existing documents
  remain exposed (RT-11).
- B5 (autoconfig dead browser / silent exposure): APPLIES to
  pref and extension routes (RT-14 fail-open). RDP prefs fail
  as dead lane, not dead browser - the one softer failure.
- B6 (maintenance-owner fiction): APPLIES to every build,
  worst for hybrid (RT-18). Still no named owner for RDP
  client, registry, or per-update drills.
- B7 (arms-race asymmetry): APPLIES to shim/extension. RDP
  escapes the webdriver arms race but enters a protocol-churn
  race with Mozilla (RT-05) - a treadmill with a different
  adversary and no evasion upside if RT-01 fails.
- B8 (24-tab blast radius, one-session limit): APPLIES AT FULL
  FORCE (RT-19, RT-23). Seamless is the configuration that
  caused both incidents, now as the design.
- B9 (stock-app principle): APPLIES (RT-22). Placement line
  undrawn for every new component.

## Decision-blocking vs acceptable-with-mitigation

BLOCKING (must spike or decide before any landing):
- RT-01 + RT-08: Google entry and Cloudflare panel with RDP
  server running and agent attached (the R3a make-or-break).
- RT-02: trusted-input story for the chosen route, named and
  tested on isTrusted-gated tasks.
- RT-03: RDP screenshot and Zen-internals reach, if claimed.
- RT-04: silent-attach security decision (owner-level) plus
  loopback-bind verification.
- RT-14: persistent extension install on Zen release without
  flags, surviving restart and update, failing loud.
- RT-17: per-combo dropped-capability statement for hybrids.
- RT-20: same-session credential policy and tool-enforced tab
  scoping, or an explicit owner acceptance of the risk.
- RT-21: real-profile acceptance (below) before declaring
  the criterion met.

Already decided by evidence (no spike can save them):
- R1 fails Google (RT-09). R2 fails leg 1 during agent work
  and the speed/seamless bar (RT-12, RT-13). Both are dead as
  end states; R1 remains valid only as the interim agent
  profile under the split.

MITIGABLE (acceptable with named mitigation plus owner):
- RT-05 (per-update RDP smoke test, fallback lane, named
  owner), RT-06 (concurrency spike), RT-07 (end-to-end task
  timings, not eval micro-benchmarks), RT-10 (written
  probabilistic-pass acceptance, if the owner grants it),
  RT-11 (reload-on-attach with the trade-off stated), RT-15
  (control-only extension, detectability accepted), RT-18
  (registry design plus owner plus fail-closed default),
  RT-19 (tool-enforced tab safety; residual risk priced),
  RT-22 (placement decision per component), RT-23 (session
  locking design).

## Recommended route

None survives as a proven end state today, and the redteam
recommends landing none of them yet.

Conditionally, the only candidate worth the blocking spikes is
R3a-primary: RDP as the always-on evaluate/navigate lane on the
owner's real profile, with a named trusted-input fallback
(OS-level input via the existing computer-use lane, pill
visible) for isTrusted-gated tasks, and Marionette-chrome kept
OUT of the human browser (its flag kills Google). This
candidate is recommended ONLY as the spike target, in this
order: RT-01/RT-08 first (cheapest, most decisive), then
RT-03, RT-06, RT-04 verification. If RT-01 fails - Google
blocks with the RDP server running - R3a is dead, R3b/R3c
flag-free variants become the only remaining candidates, and
they still owe RT-14/RT-02/RT-03. If all flag-free candidates
fail their blocking spikes, the honest outcome is: seamless
same-session control with clean Google entry is not achievable
on this build, the interim split stays, and the criterion is
renegotiated with the owner on that evidence - the Stage 2
fallback, reached honestly instead of by reinterpretation.

Until a candidate passes acceptance, the interim split remains
the operating configuration. It is rejected as end state; it
is not rejected as the bridge, and it is still the only setup
with a proven clean human leg.

## Acceptance test that would catch a fake pass

A fake pass looks like: probe CLEAN on a throwaway profile,
loopback eval fast, panel sites pass warm - while Google
blocks on the real profile, isTrusted tasks fail, and the
first Zen update kills the lane. The acceptance test must
therefore be behavioural, cold, controlled, and on the real
profile. Pre-register all of it before running; a test whose
control arm never blocks is void, not passed (A2).

1. Configuration under test: the exact end-state launch (prefs,
   flags, ports, extension state) on the owner's real profile,
   at a task boundary, pill visible, tabs recorded before.
   Throwaway-profile runs are mechanism checks only and cannot
   pass acceptance (RT-21).
2. Control arm, same day, same IP, interleaved: flagged-raw
   throwaway must challenge on P1/P2 and block Google entry.
   If it does not, the day is void.
3. Owner-browsing arm (leg 1, decisive): the owner himself,
   no agent input, RDP server running and an agent client
   attached and idle: Google homepage, typed queries (at
   least 5, varied), SERP loads with no unusual-traffic wall;
   click through to P1 timeanddate, P2 coolors, P5 codeforces,
   plus at least two high-protection Cloudflare sites with
   observed blocks in this environment; no interstitial.
   Repeat cold (fresh tab set, cf_clearance cleared or new
   profile-clone) at least 3 times across different hours.
4. Agent arm (leg 2, same session, immediately after arm 3
   without relaunch): agent evaluates, navigates, screenshots
   (if claimed), reads one Zen internal (if claimed), and
   completes an isTrusted task suite: file-upload picker,
   clipboard write, HTML5 drag, a Turnstile/CAPTCHA-gated
   form, each recorded pass/fail per task. Owner tabs before
   and after diffed; zero owner tabs closed or navigated.
5. Concurrency arm: owner opens DevTools and uses it while
   the agent evaluates; owner types in a page while the agent
   navigates another tab; no errors, no focus theft beyond
   the pill contract.
6. Security checks: RDP/BiDi/Marionette ports bound to
   loopback only (verified from a non-loopback interface);
   attach attempt from an unrelated local process recorded
   (prompt behaviour as designed); startup probe fails loud
   if webdriver=true or if the RDP port is missing/misbound.
7. Update drill: after the next Zen update (or a simulated
   profile/pref break), cold-call the agent lane with no
   human touching the browser; record attach, evaluate,
   Google entry. One broken update retires the route to the
   split automatically (Stage 2 kill criteria, unchanged).
8. Speed, honestly: end-to-end wall time for 3 fixed real
   tasks per route vs the split baseline, same sites, same
   day. Eval micro-benchmarks are reported but never scored.

Pass requires arms 3 and 4 in the same session with no
relaunch between them, control arm valid, and arms 5-7
recorded. Anything less is a spike result, not acceptance.

## Evidence labels

- VERIFIED (per cited reports): each WebDriver flag forces
  webdriver=true, pref route dead (Stage 1); A5 panel and
  Google outcomes (A5 report); W1 shim variants, pristine
  leak, Google isolation 6/6 blocked under flags, pre-existing
  tab early-read, fresh v3 P2 challenge once; W2 RDP
  webdriver=false two ways, 0.4ms loopback eval, four-pref
  requirement, extension temp-install via geckodriver,
  isTrusted=false JS clicks, SessionStore empty collection,
  port collisions in all three spikes; W3 46.5s BiDi attach,
  ~6s Marionette, lazy-tab unreachability, JS heap loss,
  tab-0 replacement in ad-hoc profile; 24-tab incident 26/11
  and Zen-death 27/11 (Stage 2 redteam, AGENTS.md).
- ASSUMED (flagged where load-bearing): RDP parent-process
  targets reach Zen internals; WebSocket bridge closes the
  extension latency gap; Google's flag-correlated signal is
  tied to the WebDriver flags specifically (the RT-01
  unknown); real-profile Google scoring resembles throwaway
  scoring.
- UNTESTED (the blocking list): Google/Cloudflare behaviour
  with RDP running; RDP screenshot, trusted input, chrome
  targets, DevTools concurrency; persistent extension install
  on Zen release; extension detectability; any seamless route
  on the owner's real profile.
