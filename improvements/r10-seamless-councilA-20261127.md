# R10 seamless-control Council A position (evidence and cost) - 2026-11-27

Council A deliberates on measured spike evidence only. No build, no test in
this document. Question: which route to seamless same-session agent control
of the owner's live Zen does the evidence support, and at what cost?

Owner bar (27/11 12:08 ruling plus 06:20 criterion): the user opens Zen
normally, searches normally, no Cloudflare block, AND can call an agent to
computer-use Zen at any time in the same live session. Zen stays
AI-optimized. The two-profile split does not fit as end state. A dedicated
build is weighted as a serious primary candidate and is authorized.
Machine-specific layer stays on the laptop only, never in repo. Speed
(attach plus per-action latency) is a headline criterion.

Reports cited: W1 shim spike, W2 control surface, W3 relaunch, Stage 1,
Stage 2 decision, A5 A/B gate, split adoption. All in
~/workspace/r3l3-run-wt/improvements/.

## Verdict

**Chosen route: 3c/3d phased hybrid, RDP-primary.** Flag-free owner session
(no --remote-debugging-port, no --marionette) with a dedicated Zen control
toolset: RDP as the fast DOM lane (read, write, navigate), the existing
OS-input computer-use lane as the trusted-input and screenshot lane, and
Marionette chrome kept OUT of the owner session as a separate maintenance
lane for Zen internals only when a task truly needs workspace or folder
control. SessionStore reads used for owner-tab inventory only, never as a
control path. Phase 1 ships RDP plus OS-input. The extension bridge (3b) is
added only if a measured gap demands it.

**Runner-up: 3a RDP-only plus OS-input** (the Phase 1 subset standing
alone, no extension, no Marionette chrome lane at all). Adopted if Zen
internals demand proves rare in real use.

**Rejected on measured evidence: Route 1 (flagged plus improved shim always
on) and Route 2 (attach-on-demand flagged relaunch).** Both fail the owner
bar on facts already measured, not on taste. Details below.

Ponytail note, stated plainly: Ponytail asks for the smallest COMPLETE
change. Route 1 is smaller but incomplete, because it fails the Google
search leg of the criterion on 6 of 6 measured attempts (W1 Test 2). A
smaller change that does not meet the bar is not the Ponytail answer. The
phased hybrid is the smallest build that can meet the bar, reusing lanes
that already exist (OS-input computer-use, the unified probe, the split
launcher and probe machinery as fallback) and adding one new lane (RDP)
whose minimal client pattern is already proven in W2.

## What the evidence proves, claim by claim

### Route 1 fails on Google entry, and no shim fixes it

- W1 Test 2 (Google entry isolation) is decisive. Flagged browser with a
  CLEAN-probe shim blocks on Google with BiDi input 3/3, with real keyboard
  plus session 3/3, and with real keyboard and no session 2/2. Flag-free
  with real keyboard and no session passes 2/2. Input method is not the
  cause. Active session is not the cause. The block tracks the launcher
  flags, or flag-correlated signals beyond page-visible
  navigator.webdriver (W1 Headline 2, Test 2 table and isolation
  conclusion).
- A5 found the same shape a day-part earlier: Google Entry A blocked 7/7 in
  both flagged arms, passed 7/7 flag-free, with an honest caveat that input
  method was not isolated (A5 Verdict, Per-site outcomes, Interpretation 2).
  W1 closed that caveat. The two reports agree.
- W1's best shim v3-proxy-patch-exact is genuinely strong: probe CLEAN,
  page-realm String(getter) byte-identical to native, pristine-realm attack
  leaks only the anonymous form with no source (W1 Headline 1, Test 1
  table). It still does not clear Google. Improving the shim further
  cannot fix a block that is not driven by the value the shim rewrites.
- Owner criterion says "searches normally." Google is the normal search
  path on this machine (A5 Entry A used Google as default engine; split
  adoption human-leg verification searched via Google). A DDG workaround
  under flags (W1 Recommendation) is a workaround, not normal search.
  Route 1 therefore fails the bar as written.
- Two further Route 1 costs, both measured. First, pre-existing tabs: the
  shim does not reach already-loaded documents; script.evaluate install
  fixes the live value but cannot unsee an early read (early=true already
  recorded); only preload plus reload gives early=false (W1 Headline 3,
  Test 3). An always-on flagged owner session would need evaluate-install
  on every attach, accepting the early-read limit, or reloads of open tabs.
  Second, panel outcomes stay probabilistic: fresh v3 passed P1 and
  challenged P2 at n=1 per cell (W1 Headline 4, Test 4). The honest claim
  is "passes most of the time," not a guarantee (W1 Test 4 reading).
- Stage 1 explains why Route 1 exists at all: each launcher flag alone
  forces navigator.webdriver=true, and dom.webdriver.enabled=false changes
  nothing (Stage 1 Headline 1-2, test matrix T2-T6). The shim was the only
  JS-layer answer. W1 proves the JS layer is not where the Google block
  lives.

Verdict on Route 1: cheapest to keep, already built, and disqualified as
end state by W1 Test 2. Retain v3 only as interim residue inside the agent
profile (Stage 2 Step 1 already does this) and as fallback if the build is
killed.

### Route 2 fails on attach latency, heap loss, and flagged-during-session

- W3 corrected the Stage 1 pricing honestly: window return is about 1
  second per restart, not minutes (W3 Verdict, Timing table, Answer to the
  Stage 2 question). Council A accepts the correction. The rejection no
  longer rests on "minutes."
- The real costs are measured and sufficient. BiDi session.new takes 46.5
  seconds after flagged relaunch, consistent across five launches (46.47,
  46.51, 46.51, 46.56, 46.57), while the port listens at about 1 second;
  Marionette attaches in 5.6 to 5.9 seconds on the same launches (W3
  Timing table and notes). Every agent call pays that attach wait plus two
  restarts (about 2 seconds of window absence total, W3 Verdict).
- Restore fidelity is high but lossy where it matters: 19 of 20 tabs, form
  text, and scroll survive exactly; JS heap state is lost by construction
  (counter 7 to 0); the active tab is not re-activated (New Tab active);
  tab 0 is replaced by about:blank in the ad-hoc throwaway profile (W3
  Fidelity table and evidence layers). Registered-profile behavior for
  tab 0 is untested (W3 caveat), which is itself a risk, not a comfort.
- Restored tabs are lazy and unreachable to the agent through BiDi or
  Marionette alone: BiDi getTree lists 1 context not 20; Ctrl+Tab via
  input.performActions does not switch; Marionette lists 20 handles but
  evaluate reads about:blank; only an OS-level sidebar click loads the tab
  with restore data (W3 Agent-attach reality). A seamless route whose
  agent cannot reach the owner's restored tabs without OS clicks has not
  solved the seamless problem.
- During the entire agent session the owner's browsing in that session is
  flagged (W3 Verdict; Stage 2 leg-1 failure). That is the original
  problem, relocated in time rather than removed.
- Stage 2 rejected boundary-restart unanimously as dominated (Stage 2
  Decision, Step 2 note). W3 confirms the rejection stands on new numbers
  (W3 Answer to the Stage 2 question).

Verdict on Route 2: rejected. It is the only route that charges the owner
a visible disruption (two restarts, heap loss, active-tab reset) on every
single agent call, and still leaves him flagged while the agent works.

### RDP is the only measured flag-free control channel with a clean signal

- W2 Headline 1: with only --start-debugger-server plus four devtools
  prefs, pages read webdriver=false with the native getter, verified two
  ways (beacon page and RDP evaluate). W2 calls it "the only measured
  channel with agent control and a clean webdriver signal at the same
  time." Council A finds no contradiction in any other report.
- W2 Latency table: RDP evaluate 0.4 ms median, ahead of BiDi (1.6 ms
  trivial, 0.7 ms DOM read) and Marionette content execute (3.5 ms). RDP
  connect 18.2 ms, listTabs 22.3 ms, getTarget 19 to 27 ms. Port open 0.40
  to 0.56 s after launch. RDP also does DOM write and navigate, verified
  with a minimal stdlib client, no geckodriver in the loop (W2 Headline 2,
  Per-route detail 3).
- W2 Capability matrix, RDP column: DOM read yes, DOM write yes, tab
  list plus navigate verified. Trusted input not available via console
  actor (untested beyond evaluate). Screenshot not measured. Zen
  internals untested (parent-process targets not probed). These gaps are
  real and are priced below; they do not erase the one fact no other lane
  offers, which is control without the webdriver tell.
- W2 risks, adopted: RDP is the DevTools internal protocol, less stable as
  an API contract than BiDi or WebDriver; actor shapes changed across
  versions (descriptor vs target split observed in this spike); it needs
  devtools prefs in the profile, a wider config change than a launch flag
  (W2 Per-route detail 3, Risks).
- Launch requirements matter for blast radius: --start-debugger-server
  alone does not open the port; four prefs are required
  (devtools.debugger.remote-enabled, devtools.chrome.enabled,
  devtools.debugger.prompt-connection=false, devtools.debugger.remote-host
  and port) (W2 Per-route detail 3). Whether those prefs, always on in the
  owner profile, themselves move Google or Cloudflare scoring is
  unmeasured. That is the top unknown, ranked below.

### Marionette chrome reaches Zen internals but cannot be flag-free

- W2 Headline 3 and Per-route detail 2: chrome context reaches
  gZenWorkspaces, gZenFolders, gBrowser, and 29 Zen globals at 1.4 ms
  median eval, but only with MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 in the
  launch env; without it, chrome context is refused.
- W2 Capability matrix, Marionette chrome column: webdriver side-effect
  true (same launch flag). Marionette needs --marionette, which Stage 1
  proved forces webdriver=true alone (Stage 1 T3). Any lane that requires
  Marionette in the owner session reintroduces the flagged state Route 1
  already failed on.
- The chrome-observer shim route failed in two variants (Xray isolation;
  per-call sandbox windows) (W2 Per-route detail 2). Marionette chrome is
  not a shim delivery mechanism.
- Consequence for the hybrid: Marionette chrome is valuable exactly once,
  for workspace, folder, and tab-strip control that no flag-free lane
  offers today (W2 matrix: workspace/folder control yes only here). It
  must live outside the owner session (separate instance or profile,
  maintenance lane), or the hybrid silently becomes Route 1 with extra
  steps. Council A insists on that placement in writing.

### Extension bridge is a proven evaluate lane with two open gates

- W2 Headline 4 and Per-route detail 5: a temporary MV3 extension installed
  via geckodriver moz/addon/install in 85 ms runs a MAIN-world content
  script at document_start that flips page-visible webdriver from true to
  false. In-extension executeScript measured about 4 ms; the 50.4 ms
  bridge round-trip is dominated by the spike harness 50 ms poll interval,
  and a WebSocket bridge would close most of the gap (W2 Latency table
  notes).
- W2 Capability matrix, Extension column: DOM read and write yes, trusted
  input no (JS click measured isTrusted=false), screenshot no, Zen
  internals no, tab control partial via tabs API.
- Two gates are unproven. First, persistence: temporary install needs no
  signing, but temporary installs do not survive restart. Permanent
  install in a release Zen build (signing policy, profile extension
  placement, update survival) was not tested in any spike. Second, the
  toString tell remains in the extension shim as measured (getter reads
  get() { return false; } vs native form, W2 Per-route detail 5). Under
  flags that tell plus the W1 Google finding means 3b-as-shim fails the
  same way Route 1 fails. As a flag-free control lane (native false, no
  shim needed), the tell is irrelevant, but then the extension is purely
  an evaluate lane competing with RDP at 0.4 ms, and it loses on latency
  unless the bridge is rebuilt.
- Council A reading: the extension is a viable fallback evaluate lane and
  the proven shim vehicle if a shim is ever needed again. It is not the
  primary lane. Building it first would spend the signing and persistence
  risk before proving RDP cannot carry the load.

### SessionStore is read-only inventory at best

- W2 Headline 5 and Per-route detail 4: zen-sessions.jsonlz4 decodes
  trivially (mozLz40 magic, python-lz4, 0.0 ms median on a synthetic
  20-tab file, byte-identical round-trip), but the file stayed empty (0
  tabs, 0 spaces) after 21 BiDi-created tabs and after 10 WebDriver-created
  tabs, live and after shutdown. Agent-created tabs are not collected on
  any timescale tested (up to 20 s live plus shutdown). Offline
  write-and-relaunch verification is blocked, honestly.
- W3 shows the other half: owner and UI-created tabs do collect (19 tabs
  in zen-sessions.jsonlz4 across cycles, scroll stored as "0,2500",
  formdata stored with real key-event typing) (W3 Fidelity evidence
  layers). Collection works for human tabs and fails for agent tabs, for
  reasons unknown (timer, UI tab-strip events, workspace gating, W2
  Per-route detail 4).
- gZenSessionStore exposes only init, promiseInitialized, and
  restoreInitialTabData; no save or collect hook (W2 Per-route detail 2).
- Consequence: sessionstore reads can inventory the owner's tabs (useful
  for record-before-attach discipline). Any design that writes session
  state or controls tabs through this file is building on a blocked
  mechanism. Council A excludes it from the control path.

### Cross-cutting facts that shape any hybrid

- One WebDriver session at a time across BiDi and Marionette (Stage 1 T8;
  W2 Cross-cutting notes). RDP and extension lanes are independent of that
  limit. A hybrid built on RDP plus OS-input avoids the sequencing tax in
  the hot path; any BiDi or Marionette fallback must be sequenced.
- First-attach costs argue for held sessions: BiDi and Marionette first
  attach about 1 s, warm re-attach 20 to 26 ms; a held session pays
  neither (W2 Latency table notes). W3's 46.5 s BiDi attach is a different
  condition (restored profile with 20 lazy tabs after relaunch, W3 Timing
  notes) and must not be conflated with W2 warm numbers. Both are cited
  with their conditions in the cost table.
- Port discipline: parallel lanes collided on default spare ports during
  W2; any multi-lane toolset needs a port registry (W2 Cross-cutting
  notes). W1 hit the same class (port 9333 held by a parallel lane, W1
  Failure chains).
- Continuity demand: Stage 1 counted 0 of 55 frozen tasks needing
  owner-session continuity, with the stated caveat that the frozen list
  was designed around fresh pages (Stage 1 (d)). Stage 2 refused to use
  that count to downgrade the bar (Stage 2 fork ruling, redteam S2). The
  owner has now ruled same-session seamless is the bar (27/11 12:08).
  Council A treats the 0/55 count as workload history, not as permission
  to keep the split.

## Cost table

Build cost uses Stage 1 Alternative 3 framing (research plus build plus
test 2-5 days for a dedicated layer, Stage 1 (d)) split by lane, plus W2
evidence of what already exists. Maintenance is per major Zen update until
automated (Stage 2 Step 4 estimate 0.5-1 day re-verification, adopted as
the planning number).

| Route | Build cost | Per-update maintenance | Latency (measured) | Blast radius on daily browsing | What breaks on Zen update |
|---|---|---|---|---|---|
| 1. Flagged + v3 shim always on | Near zero. v3 exists (682 B, W1 Test 1). Holder preload discipline exists (Stage 1 T7). | Low. Re-run probe, re-verify shim descriptor shape. | BiDi eval 1.6 ms trivial / 0.7 ms DOM, navigate 37.6 ms, screenshot 11.7 ms (W2 table). Attach 26.4 ms warm, 974 ms first (W2). | HIGH. Owner browses flagged every day. Google search blocked (W1 Test 2, 6/6). Pre-existing tabs leak early reads without reload (W1 Test 3). Pristine-realm tell remains (W1 Test 1). | Shim descriptor or preload API change; Google or Cloudflare adds a flag-correlated signal the shim cannot reach (already true for Google). |
| 2. Attach-on-demand flagged relaunch | Low-medium. Launcher and record/restore wiring exist in split adoption machinery. Collection-before-SIGTERM guarantee still needed (W3 Timing notes). | Low. Launcher and probe re-verification. | Window return about 1 s per restart (W3). BiDi attach 46.5 s, Marionette about 6 s per call (W3). Per-action same as Route 1 once attached. | HIGH per call. Two restarts, JS heap lost, active tab reset, tab-0 risk on ad-hoc profile (W3 Fidelity). Flagged browsing during whole agent session. Restored tabs need OS clicks (W3 Agent-attach reality). | Session file shape (already Zen-specific, W2 Per-route 4); restore fidelity regressions; BiDi attach latency shifts. |
| 3a. RDP-based control (no flags) | Medium. Minimal stdlib client proven (W2 Per-route 3). Production lane still needs target management, navigate/error handling, pref and port management, port registry. | Medium-high. Internal protocol; actor shapes already observed changing (descriptor vs target split, W2 Risks). Fail-loud probe required. | BEST measured. Eval 0.4 ms, DOM read 0.4 ms, connect 18.2 ms, listTabs 22.3 ms, getTarget 19-27 ms (W2 table). Navigate accepted, not timed. | LOW if Google-clean (unproven, top unknown). Four devtools prefs always in profile (W2 Per-route 3). No webdriver tell (native false, W2 Headline 1). | Actor names/shapes, pref names, debugger-server auth or prompt behavior. Any one breaks the lane until client updated. |
| 3b. Extension-bridge control (no flags) | Medium. Extension plus bridge proven as spike (W2 Per-route 5). Production needs WebSocket transport (poll is 50 ms, W2 notes) plus permanent-install solution (signing/persistence untested). | Medium. MV3 API drift, MAIN-world support, signing renewal if required. | In-extension about 4 ms; bridge round-trip 50.4 ms poll-bound as spiked (W2 table). WebSocket expected single-digit ms (ASSUMED, W2 Evidence labels). | LOW-MEDIUM. Extension resident in owner profile, MAIN-world script on every page (perf and attack surface). No trusted input, no screenshot (W2 matrix). | MV3 APIs, document_start MAIN-world semantics, signing policy, geckodriver install path. |
| 3c/3d. Phased hybrid (RDP + OS-input, Marionette chrome as external maintenance lane, sessionstore read-only) | High in total, phased. Phase 1 = 3a plus existing OS-input lane (already built, pill-proven in W1/W3 runs). Phase 2 (extension) and internals lane added only on measured demand. | High in total (sum of lanes), phased the same way. Each lane fails independently; hot path depends only on RDP plus OS-input. | Hot path = RDP numbers above. Trusted/screenshot path = OS-input wall time (seconds class, not measured in W2 table; must be budgeted, see unknowns). Held RDP session pays no re-attach (W2 notes). | LOW on browsing (flag-free, native false). Complexity risk instead: lane sequencing, port registry, focus assertions before OS input (W1 method note). Marionette chrome never in owner session. | Any single lane can break per update; design must degrade to remaining lanes plus split fallback, not to flagged owner browsing. |

Reading the table honestly: Route 1 wins every cost column and loses the
only column that matters, which is whether the owner can search normally.
Route 2 wins on build cost and loses on per-call owner disruption. The
hybrid loses on build and maintenance cost and is the only route whose
measured lanes can satisfy all three legs of the criterion at once:
flag-free browsing (RDP, W2 Headline 1), agent callable at any time in the
same session (held RDP session, no relaunch, W2 notes), AI-optimized speed
(0.4 ms eval, W2 table). That trade is exactly what the owner authorized
when he weighted the dedicated build as primary candidate.

## Kill criteria

Adopted from Stage 2 Step 4, tightened per lane. Any one trigger retires
the affected lane to the interim split automatically; no silent degraded
flagged browsing of the owner profile, ever.

1. RDP Google-entry spike fails (flagged-style wall under RDP launch
   config): RDP-primary is dead before build. Fall back to split as end
   state candidate and renegotiate the criterion with the owner on that
   evidence (Stage 2 Step 3 pattern).
2. ONE Zen update breaks the landed toolset (probe not CLEAN on native
   signals, or human-path block on the acceptance panel), or 7 days
   broken: retire to split (Stage 2 Step 4 kill criteria, verbatim).
3. RDP actor breakage on two consecutive Zen updates requiring client
   rewrites (not version bumps): RDP lane retired; evaluate extension
   lane as primary or return to split.
4. Extension permanent install proves impossible without signing the owner
   cannot maintain, or does not survive a Zen update: 3b dropped, hybrid
   continues RDP plus OS-input only.
5. No named maintenance owner staffed (Stage 2 Step 4 requires Muse as
   owner of per-update verification, automated probe plus spot check):
   build does not start, or stops.
6. OS-input lane cannot meet focus-safety (focus-pid assertion failures,
   wrong-window input) at acceptable rate in acceptance: trusted actions
   restricted to BiDi fallback in agent profile; seamless claim narrowed
   in writing, not silently.

## Acceptance test Council A would require

Probe-clean is necessary, not sufficient (Stage 2 Step 4). All of the
following, on a throwaway profile first, real profile only at a task
boundary with the pill visible. Normal-user path throughout: entry via
homepage or search, click through visible UI, no deep links, no internal
setters as proof. Evidence shows entry, path, action, resulting state.

1. Human leg, flag-free: owner-profile launcher (no
   --remote-debugging-port, no --marionette; RDP prefs only). Probe read:
   webdriver false, boolean, native getter form, no documentElement
   attribute, no automation globals (unified probe signals, Stage 1 (c)).
2. Google entry: google.com homepage, type query, Enter, 3 queries
   (reuse W1 set: weather hanoi, timeanddate weekday calculator,
   codeforces). Pass = SERP loads 3/3, no unusual-traffic wall. This is
   the test Route 1 failed 6/6 (W1 Test 2); the build must pass it.
3. Cloudflare panel, cold trials, control arm interleaved same day: P1
   timeanddate, P2 coolors, P5 codeforces, C1 example.com (A5 panel).
   Pass = build arm passes P1/P2/P5/C1 while flagged-raw control
   challenges on at least P1 or P2 same day (void rule, A5 and W1 Test 4).
   Block outcomes recorded per arm. Owner-browsing arm reported
   separately from agent-driven visits (Stage 2 Step 2 rigor).
4. Agent leg, same session - held RDP session evaluates DOM read and write
   (median under 2 ms, budget vs W2 0.4 ms), navigates, and OS-input lane
   performs a trusted click (isTrusted=true verified at page level, the
   check W2 used for BiDi) plus a screenshot, pill visible throughout.
   Attach from cold under 1 s warm-path budget (W2 connect plus list plus
   target components); full task wall time recorded.
5. Pre-existing tab leg: tab loaded before agent attach reads
   early=false without reload (the W1 Test 3 failure mode). Under
   flag-free RDP this should hold natively; prove it, do not assume it.
6. Zen internals leg (only if hybrid claims it): workspace list read via
   the designated lane (RDP parent target if proven, else external
   Marionette chrome lane) without flagging the owner session. If the
   lane flags the owner session, the claim fails and the lane stays
   external.
7. Update drill: after the next Zen update, cold-call the agent lane with
   no human touching the profile; probe plus human-path spot check must
   pass before agent use resumes (split adoption S8 pattern).

## Open unknowns, ranked

Decision-blocking means: do not land the route until spiked. Acceptable
risk means: proceed with mitigation and fail-loud checks.

1. **RDP Google-entry behavior. DECISION-BLOCKING for 3a and 3c.** Does
   --start-debugger-server plus the four devtools prefs trigger the same
   flag-correlated Google wall W1 isolated (W1 Test 2), or does Google
   pass like flag-free? Spike: RDP launch config on throwaway profile,
   real-keyboard Google entry, 3 queries, W1 isolation method. Half a day.
   Everything else in the hybrid depends on this answer.
2. **RDP screenshot and trusted input. DECISION-BLOCKING for 3a
   standalone; acceptable for hybrid if OS-input covers.** Console actor
   has neither (W2 matrix, Per-route 3). Spike: probe other RDP actors for
   screenshot/input; if none, hybrid budgets OS-input for both and 3a
   standalone is not claimed complete.
3. **Extension permanent install: signing and persistence.
   DECISION-BLOCKING for 3b.** Temporary install proven (85 ms, W2
   Per-route 5); permanent install surviving restart and Zen update in a
   release build is untested everywhere. Spike before any 3b commitment.
4. **Devtools prefs blast radius. DECISION-BLOCKING-ish.** The four prefs
   (W2 Per-route 3) sit in the owner profile permanently under 3a/3c. Do
   they move Cloudflare scoring (panel test under RDP config) or change
   owner DevTools UX? Panel half is covered by unknown 1's spike plus a
   P1/P2 run; UX half is a config review. Do not land prefs always-on
   until the panel half passes.
5. **RDP chrome/parent targets for Zen internals. Not blocking for Phase
   1.** Untested (W2 matrix, ASSUMED label). If proven, Marionette chrome
   may be unnecessary; if not, internals stay on the external maintenance
   lane. Spike after Phase 1, on demand.
6. **OS-input lane latency and reliability budget. Not blocking, needed
   for honest speed claims.** W2 table has no OS-input row. Hybrid wall
   time for trusted tasks will be dominated by this lane. Measure
   per-action latency and focus-assertion failure rate during acceptance;
   report alongside RDP numbers, never blended.
7. **W3 BiDi 46.5 s attach cause. Not blocking for RDP-primary.** Cause
   not isolated (W3 Timing notes). Matters only if BiDi remains a
   fallback lane; price fallback calls at 46.5 s on restored profiles
   until explained.
8. **SessionStore collection triggers. Not blocking for read-only use.**
   Why agent tabs never collect (W2 Per-route 4) blocks any write-control
   design, which Council A already excludes. Read-only owner-tab
   inventory is proven by W3 fidelity evidence.
9. **Extension toString tell closure (v3-style byte-exact patch inside
   extension). Not blocking.** Matters only for shim-under-flags designs,
   which W1 Google evidence already rejects. Flag-free control needs no
   shim.
10. **Registered-profile tab-0 loss (W3 caveat). Not blocking.** Route 2
    is rejected; the question is moot unless relaunch returns.

Acceptable risks carried knowingly: RDP actor drift across updates
(mitigated by version-pinned client, automated startup probe, kill
criterion 3); probabilistic Cloudflare panel outcomes (mitigated by
control-arm void rule and per-arm outcome recording, A5/W1 method);
hybrid complexity (mitigated by phasing, port registry per W2
Cross-cutting notes, and lane-independent degradation to split).

## Bottom line for the coordinator

Evidence kills the cheap routes and leaves one buildable path. Route 1
fails Google 6/6 with the best shim ever measured here (W1 Test 2). Route
2 charges 46.5 s BiDi attach, heap loss, and flagged browsing on every
call (W3). RDP is the only channel measured with control and a clean
native signal together, at the fastest latency measured (W2 Headlines
1-2). Build the phased hybrid around it, spike unknown 1 before writing
production code, keep Marionette chrome out of the owner session, and
hold the whole thing to the acceptance test above. If unknown 1 fails,
say so plainly and renegotiate; do not drift back to flagged owner
browsing by default.

Council A, evidence and cost lens. English only. No commits made.
