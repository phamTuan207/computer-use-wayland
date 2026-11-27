# R10 seamless Council B position - owner intent and real usage (27/11/2026)

Council B lens only: what "seamless" means in the owner's actual day.
No building or testing here; judgement on the spike evidence.

Owner ruling carried in (27/11 12:08 + 06:20 criterion + addendums):
seamless experience in his live Zen session; two-profile split is not
the end state; team chooses the method; full control surface allowed
(BiDi, Marionette privileged chrome JS, Zen internal APIs, sessionstore,
extension bridge, combinations); speed is a headline criterion; a
dedicated custom toolset for his config/machine is a serious PRIMARY
candidate, machine-specific layer on the laptop only, repo stays
generic. Criterion: owner opens Zen normally, searches normally, no
Cloudflare block, AND can call an agent to computer-use Zen at any
time; Zen stays AI-optimized.

## Verdict

**Chosen route: 3c hybrid dedicated toolset, flag-free owner session
as the base.** RDP is the fast primary lane (evaluate, DOM read/write,
navigate, tab list) on the owner's normal flag-free Zen; the existing
OS trusted-input lane (computer-use act-now, pill visible) covers
trusted clicks, typing, and screenshots that RDP has not proven; an
extension bridge is kept as the fallback evaluate lane if RDP breaks
across a Zen update. Zen-internals asks (workspaces, folders,
essentials, pinned tabs) are NOT served by a permanently flagged
browser: first investigate RDP parent-process targets for chrome
reach, and until that is proven, serve internals asks through a rare,
explicit, logged flagged escape hatch (Route 2 mechanics, used
exceptionally, not as the daily path). No flags on the owner's daily
session. No second profile as end state. No relaunch on a normal
agent call.

**Runner-up: 3b extension-bridge + OS lane on the flag-free session**
(permanently installed bridge extension in the owner profile, machine
layer only; OS lane for trusted input and screenshots). Chosen as
runner-up because extension APIs are a more stable contract than the
DevTools RDP protocol. It loses to 3c today on speed (50.4 ms
poll-bound round-trip vs RDP 0.4 ms evaluate, W2) and because a
permanent install in the owner profile is a bigger standing footprint
than devtools prefs. If RDP proves unstable across one Zen update,
3b becomes the primary without changing the owner-visible experience.

Explicitly rejected as end states: Route 1 (flagged + improved shim
always on) and Route 2 (attach-on-demand flagged relaunch). Both are
kept only as interim/escape mechanics. Route 3a pure RDP alone is
rejected as incomplete today: trusted input, screenshot, and Zen
internals over RDP are unmeasured (W2 BLOCKED/ASSUMED), and the
owner's day needs all three.

## The owner's day, defined

From the Stage 2 record and standing rules, the day to judge against:

1. Entry: he opens Zen normally (desktop entry / Super+Z), his real
   profile, his restored tabs, workspaces, essentials, pinned tabs,
   his logins. He does not think about profiles or flags.
2. Search: his main entry path is Google search (standing rule
   2026-11-10: Google first; A5 Entry A is his path). He types in the
   address bar or Google homepage and clicks through.
3. Work: he works in logged-in tabs as himself (Gmail, Codeforces
   under his manager nick, class and club tools). The Stage 2 Council
   B record: R3-056 tab restore, Gmail confirmations by agent as a
   standing rule, "do X in my account" asks. The 0/55 continuity
   count measured a frozen fresh-page list, not this day (Stage 1
   caveat; redteam S2; Stage 2 ruling: same live session is the bar).
4. Agent call mid-task: he calls an agent while looking at a tab,
   expects it to act in that tab, in his account, with the pill
   visible, without him restarting anything or switching windows.
5. Zen-internals ask: at times the ask is about Zen itself - restore
   my tabs, fix my workspaces/folders/essentials, pin or move tabs
   (R3-056 is the type specimen).

"Seamless" therefore means: steps 1-3 never degrade because an agent
might be called later, and step 4 never interrupts steps 1-3.

## Route-by-route walk through that day

### Route 1 - Flagged + improved shim always on owner session

- Entry: opens normally in shape, but the browser is flagged from
  launch. Every page sees the flagged launch. Silent degradation
  starts before he does anything.
- Search: FAILS his main path. W1 Test 2 isolated it: flagged
  browsers hit Google's unusual-traffic wall 3/3 with BiDi input,
  3/3 with real keyboard + session, 2/2 with real keyboard and no
  session; flag-free passes 2/2. A5 Entry A: flagged and flagged+shim
  ENTRY-CHALLENGE 7/7, flag-free PASS 7/7. The best shim (W1
  v3-proxy-patch-exact, probe CLEAN, byte-exact page realm) does not
  fix Google: the block tracks flag-correlated signals beyond
  page-visible navigator.webdriver. His lived experience: Google
  search is broken every day, he falls back to DuckDuckGo, and the
  standing "Google first" habit is silently taxed. That is the
  opposite of seamless.
- Agent call mid-task: works mechanically (BiDi held session, shim
  preload), and Cloudflare-panel-class sites mostly pass (A5: P1/P2
  flagged+shim PASS like flag-free; W1 fresh v3: P1 PASS, P2
  CHALLENGE once, n=1, probabilistic). But pre-existing tabs - the
  tabs he already has open, which are the point of same-session
  control - carry early=true already read by page scripts; only
  reload under preload gives early=false (W1 Test 3). Acting in the
  tab he is looking at either accepts the early-read exposure or
  reloads his tab mid-flow.
- Zen-internals ask: Marionette chrome reaches gZenWorkspaces,
  gZenFolders, gBrowser (W2), so internals are covered - at the cost
  of the browser being flagged all day.
- Verdict: fails criterion leg 1 on his actual entry path. The shim
  quality (v3 dominates pinned v1) is not the bottleneck; the flags
  are. Rejected as end state regardless of shim improvements.

### Route 2 - Attach-on-demand flagged relaunch

- Entry + search (between agent calls): perfect. Flag-free, Google
  passes, Cloudflare clean. This is the route's real strength.
- Agent call mid-task: breaks the flow he is in. W3 measured the
  honest numbers: about 1 s window absence per restart (about 2 s
  total), but 46.5 s before BiDi session.new succeeds after the
  flagged relaunch (consistent across five launches; Marionette
  about 6 s). Is 46 s acceptable mid-flow? No. He called the agent
  because he is mid-task; a 46 s dead wait plus two window
  disappearances reads as "the browser crashed and came back", not
  seamless. The 2 s absence alone might be tolerable once; 2 s plus
  46 s plus a second restart at the end is not.
- Fidelity losses land on his in-progress work: JS heap state lost
  (counter 7 to 0, W3), active tab not restored (New Tab active
  instead of his tab), 19/20 tabs in the ad-hoc profile (tab 0
  replaced; registered-profile behaviour untested). Form text and
  scroll survive exactly, which helps, but heap loss kills exactly
  the unsaved interactive state (editors, dashboards, half-done
  flows) that mid-task help is usually about.
- During the agent session his own browsing is flagged again
  (webdriver=true), so Google and Cloudflare degrade while the agent
  works - leg-1 failure for the whole session (W3, Stage 2).
- Restored tabs are lazy and unreachable to BiDi/Marionette agents
  without an OS-level sidebar click (W3 run9 was the only route that
  loaded restore data). The agent cannot simply act in the tab he
  was looking at.
- Zen-internals ask: covered after relaunch via Marionette chrome,
  with all the above costs.
- Verdict: Stage 2 rejection stands, with corrected pricing (seconds
  to window, 46.5 s to BiDi attach - not "minutes"). Correct as a
  rare logged escape hatch; wrong as the daily seamless answer.

### Route 3a - Dedicated build, RDP-based only

- Entry + search: the only measured channel with agent control and a
  clean signal at once. W2: RDP launch (devtools prefs +
  --start-debugger-server) reads webdriver=false with the native
  getter, verified two ways. No flags, so Google entry should behave
  flag-free - BUT Google entry under the RDP pref set itself was not
  directly tested (W2 verified the webdriver signal, not a Google
  SERP). This is the single most important untested assumption in
  the whole decision (see unknowns).
- Agent call mid-task: fastest measured lane (evaluate 0.4 ms median
  vs BiDi 1.6 ms, Marionette content 3.5 ms; W2). DOM read/write and
  navigate verified. Same live session, no restart, no second
  window. Speed criterion: best on the table.
- Gaps against his day: trusted input not available via console
  actor (untested beyond evaluate); screenshot not measured; Zen
  internals untested (parent-process targets not probed). His asks
  regularly need a real trusted click (submit, confirm) and a
  screenshot for evidence, and sometimes Zen internals. Pure RDP
  cannot serve the full day today.
- Risk: RDP is the DevTools internal protocol, actor shapes change
  across versions (W2 observed descriptor/target split). A Zen
  update can break the lane silently unless a startup probe fails
  loud.
- Verdict: correct primary lane, incomplete as the whole toolset.

### Route 3b - Dedicated build, extension-bridge only

- Entry + search: depends on how the extension gets in. Installed
  via geckodriver (W2: 85 ms temp install), the browser must be
  Marionette-flagged, webdriver flips true to false at
  document_start in MAIN world, but the flagged launch remains - and
  W1 proved Google blocks the flagged launch regardless of the
  page-visible value. That variant inherits Route 1's Google
  failure. A permanently installed extension on a flag-free browser
  avoids flags entirely and keeps Google clean, but permanent
  install/signing in Zen and its update survival are unproven here.
- Agent call mid-task: evaluate via scripting.executeScript works
  (about 4 ms in-extension; 50.4 ms bridge round-trip poll-bound in
  the spike harness, W2). JS clicks are isTrusted=false - synthetic
  clicks fail exactly the submit/confirm class of actions. No
  screenshot lane. No Zen internals (extension APIs do not reach
  gZenWorkspaces/gZenFolders).
- Verdict: proven shim/evaluate vehicle, insufficient alone for his
  day (trusted input, screenshots, internals). Right as fallback
  lane inside 3c, and as runner-up end state when paired with the
  OS lane.

### Route 3c - Hybrid toolset (CHOSEN)

Composition judged: flag-free owner session + RDP fast lane + OS
trusted-input/screenshot lane (existing computer-use, pill visible)
+ extension bridge as fallback evaluate lane + Zen-internals path
investigated over RDP parent targets first, logged flagged escape
hatch only until proven. SessionStore reads excluded as a control
lane (W2: zen-sessions.jsonlz4 stayed empty after 21 BiDi tabs and
10 WebDriver tabs; collection triggers unknown - do not build on it).

- Entry: he opens Zen normally, flag-free, his profile, his tabs.
  The only standing footprint is devtools prefs (machine layer) and
  the RDP port. Nothing about his morning changes.
- Search: flag-free launch, so Google entry is expected to pass as
  in A5 Arm 3 / W1 flag-free arms (7/7, 2/2). Must be proven under
  the exact RDP pref set in acceptance (below) - expected, not
  assumed.
- Agent call mid-task: agent attaches over RDP to the session he is
  already in (connect about 18 ms, evaluate 0.4 ms, W2), reads and
  writes the tab he is looking at, in his logged-in account, no
  restart, no second window, no 46 s wait. When a trusted click or
  typing is needed, the OS lane does it with the pill visible (the
  standing pill rule); when evidence needs a screenshot, the OS lane
  captures it. His parallel browsing stays clean throughout - no
  flagged window while the agent works.
- Zen-internals ask: the honest weak point. Marionette chrome is
  the only measured path to gZenWorkspaces/gZenFolders/gBrowser
  (W2), and it needs the --marionette flag at launch plus
  MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 - incompatible with a flag-free
  daily session. 3c therefore requires, in order: (1) probe RDP
  parent-process targets for chrome reach (W2 ASSUMED, not probed);
  (2) if RDP cannot reach chrome, keep internals asks on the rare
  logged escape hatch (Route 2 mechanics with W3 numbers known:
  about 2 s absence, about 6 s Marionette attach, heap loss warned
  in the drive report). Internals asks are occasional (R3-056 class),
  not the daily flow, so an exceptional path for them does not break
  seamlessness for steps 1-4 - but it must be named, not hidden.
- Silent-degradation check: devtools prefs are a wider config change
  than a flag (W2). Acceptance must confirm no owner-visible side
  effects (no connection prompts - prompt-connection=false is in the
  pref set - no DevTools UI surprises, no Google/Cloudflare change).
  The RDP port is a local control surface; it must bind localhost
  only and be covered by the startup probe (fail loud if the lane is
  down or the signal is dirty).
- Speed: best measured evaluate, warm attach in tens of ms, held
  session pays neither first-attach cost. The OS lane is slower per
  action but is only used where trust/screenshot requires it.
- Verdict: the only route that serves entry, search, work, and
  mid-task agent calls in his real day without degrading any of
  them, and the only one aligned with his explicit dedicated-build
  steer (custom toolset for his machine, generic repo, machine layer
  local). Its cost is build + per-update verification discipline,
  which he authorized ("build a dedicated tool if needed").

### Route 3d - Council B variant considered and folded into 3c

Considered: flag-free + extension bridge as primary (no RDP), OS
lane for trust. Rejected as primary on speed (50 ms class vs 0.4 ms)
and permanent-install footprint; retained inside 3c as fallback and
as runner-up. No separate 3d needed.

## Evidence citations (load-bearing only)

- Flags force webdriver=true; pref route dead; no runtime toggle:
  Stage 1 T2/T3/T5/T6.
- Same-live-session is the bar; split is interim only: Stage 2
  decision, fork ruling (Council B reading adopted).
- Google entry only flag-free passes (7/7); flagged+shim passes
  Cloudflare panel like flag-free: A5 report, Entry A + P1/P2 table.
- Google block tracks flags, not input method or session; best shim
  v3 probe CLEAN still blocked; pre-existing tabs early=true: W1
  Tests 1-3.
- RDP webdriver=false native getter (two reads), evaluate 0.4 ms,
  DOM write + navigate verified; trusted input/screenshot/internals
  unmeasured: W2 route 3 + latency table.
- Marionette chrome reaches Zen internals (gZenWorkspaces,
  gZenFolders, gBrowser, 29 globals) only with system-access env;
  chrome-observer shim failed: W2 route 2.
- Extension bridge proven (85 ms install, document_start MAIN shim,
  about 4 ms in-extension, 50.4 ms poll-bound round-trip, JS click
  isTrusted=false): W2 route 5.
- SessionStore empty for agent tabs (21 BiDi + 10 WebDriver tabs):
  W2 route 4. Excluded as a control lane.
- Relaunch: about 1 s window, 46.5 s BiDi attach, about 6 s
  Marionette, 19/20 tabs, heap lost, active tab reset, lazy tabs
  need OS click: W3 timing + fidelity tables.
- Split adoption (interim, launch-path audit, startup probe): split
  adoption report. It remains the interim until 3c acceptance
  passes; R10 stays open per Stage 2.

## Acceptance test Council B requires

Normal-user path only (standing hard rule 2026-11-26): enter via
search/homepage and click through; no deep links, no internal
setters as proof; evidence shows entry, path, action, resulting
state. Throwaway profile first, then owner profile at a task
boundary with the pill visible. Fixed panel frozen before testing,
cold trials, flagged control arm interleaved same-day; if the
control never blocks, the test is void, not passed (Stage 2 rigor).

1. Owner opens Zen normally: launch via the normal desktop entry
   (Super+Z path) on the owner profile with the 3c configuration.
   Pass: window up, his tabs/workspaces present, startup probe
   CLEAN (webdriver=false, native getter), no connection prompts,
   no visible DevTools side effects.
2. Google search works: from the new-tab/address bar, search
   Google for at least 3 queries (including one Cloudflare-fronted
   target, e.g. the A5 panel queries), click through to results.
   Pass: SERP loads 3/3 with no unusual-traffic wall, target sites
   load with no Cloudflare interstitial. This must run under the
   exact RDP pref set, not a plain flag-free browser.
3. Agent acts in the same session - with the owner session from
   step 1 still running (same PID, no restart), an agent attaches
   over RDP, reads the active tab, performs a DOM write and a
   navigate, then performs one trusted action via the OS lane
   (pill visible in evidence) in a logged-in tab (test account
   first, owner account only per credential policy). Pass: all
   actions land in the same session, attach-to-first-evaluate
   under 2 s, owner tabs untouched except the tasked tab.
4. Zen-internals ask: perform one internals read (active workspace
   + pinned count) and, if the RDP chrome path is claimed, one
   internals write (e.g. workspace switch) without a flagged
   relaunch. If this step needs the escape hatch, it is recorded
   as escape-hatch use with W3 costs stated, and 3c acceptance is
   marked partial (daily flow proven, internals exceptional) -
   not silently passed.
5. Update drill: after the next Zen update, repeat steps 1-3 cold
   (no human touching the config first). One broken update retires
   the RDP lane to the 3b fallback automatically (Stage 2 kill
   discipline: one update / 7 days), with the startup probe failing
   loud rather than degrading silently.

## Open unknowns, ranked by impact on the owner's day

1. Does Google entry pass under the exact RDP pref set? W2 proved
   webdriver=false under RDP prefs; nobody has loaded a Google SERP
   in that configuration. If devtools prefs correlate with a block
   the way flags do, 3c loses its main advantage. Test first, cheap.
2. Can RDP reach chrome/parent targets (Zen internals) without
   Marionette flags? Determines whether internals asks are seamless
   or permanently exceptional. W2: not probed.
3. RDP trusted input and screenshot: is there any RDP actor path, or
   is the OS lane permanently load-bearing for clicks/evidence?
   Affects speed claims for click-heavy tasks.
4. RDP protocol stability across Zen updates + a fail-loud startup
   probe design. One silent break turns "agent callable at any
   time" into a dead lane he discovers mid-task.
5. Permanent extension install in Zen (signing, update survival) -
   needed only for the 3b fallback/runner-up; temp installs need
   flagged geckodriver and reintroduce the Google problem.
6. Why BiDi session.new takes 46.5 s after relaunch (W3, cause not
   isolated) - matters only for escape-hatch cost; Marionette
   (about 6 s) is the escape lane meanwhile.
7. SessionStore collection triggers (W2 blocked) - nice-to-have for
   tab recording; not load-bearing for 3c.
8. Registered-profile tab-0 restore behaviour (W3 caveat) - matters
   for escape-hatch fidelity claims only.

## Bottom line for the coordinator

His day breaks at Google under flags and breaks at the restart
under relaunch. The hybrid flag-free toolset is the only route that
leaves his morning, his search, and his tabs exactly as they are,
while making the agent faster than today (0.4 ms evaluate) in the
same session. Build that, gate it on the acceptance above, and keep
the flagged paths as named exceptions - never as the daily browser.
