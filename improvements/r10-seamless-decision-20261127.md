# R10 seamless-control decision (27/11/2026)

Coordinator decision on the owner ruling of 27/11 12:08: seamless
same-session agent control of Zen is the end state; the two-profile
split does not fit as end state; the team chooses the method. Owner
addendums folded in: full control surface beyond BiDi (Marionette
privileged chrome JS, Zen internal APIs, sessionstore, extension
bridge, combinations); speed as headline criterion; dedicated build
weighted as serious primary candidate; machine-specific layer on the
laptop only, repo generic.

Process: three spike workers (W1 shim, W2 control surface + speed,
W3 relaunch) ran in parallel on throwaway profiles; Council A
(evidence and cost), Council B (owner intent and real usage), and an
independent redteam deliberated on the evidence; W4 then ran the
decision-blocking spike (RT-01) as the first real slice of the
chosen tool. All reports in this directory:
r10-seamless-w1-shim-spike-20261127.md,
r10-seamless-w2-control-surface-20261127.md,
r10-seamless-w3-relaunch-20261127.md,
r10-seamless-w4-rdp-slice-20261127.md,
r10-seamless-councilA-20261127.md, r10-seamless-councilB-20261127.md,
r10-seamless-redteam-20261127.md. Background: Stage 1 report,
Stage 2 decision, A5 gate, split adoption (same directory).

## Decision

**Chosen route: 3c phased hybrid, RDP-primary, on the flag-free
owner session.** A dedicated Zen control toolset:

- **Phase 1 (build now):** RDP fast DOM lane (attach, evaluate
  read/write, navigate, tab list) on the owner's normal flag-free
  Zen (no --remote-debugging-port, no --marionette; debugger server
  via --start-debugger-server plus devtools prefs, machine layer),
  plus the existing OS-input computer-use lane for trusted input
  and screenshots (pill visible). Held RDP session; no relaunch on
  an agent call; no second window.
- **Zen internals:** first choice is the RDP parent-process target
  (W4 proved typeof reach to gZenWorkspaces/gBrowser/gZenFolders;
  deeper control untested). Until proven, internals asks go through
  the rare, explicit, logged flagged escape hatch (Route 2
  mechanics). Marionette chrome stays OUT of the owner session.
- **Fallback evaluate lane:** extension bridge (3b), built only if
  RDP breaks across a Zen update. Runner-up end state.
- **SessionStore:** read-only owner-tab inventory at most; excluded
  from the control path (W2: agent tabs never collect).
- **Interim split** remains the operating configuration until
  acceptance passes. R10 stays OPEN until then.

**Rejected on measured evidence:**
- Route 1 (flagged + improved shim always on): W1 Test 2 - Google
  entry blocks 6/6 under flags even with a probe-CLEAN v3 shim;
  input method and session isolated out. The flags drive the block;
  no shim fixes it. The owner's main search path breaks daily.
- Route 2 (attach-on-demand flagged relaunch): W3 - ~1 s window
  return but 46.5 s BiDi attach (Marionette ~6 s), JS heap lost,
  active tab reset, restored tabs unreachable via agent lanes
  without OS clicks, and flagged browsing during every agent
  session. Kept only as the logged escape hatch.

## Evidence per route (summary)

| Route | Decisive evidence | Verdict |
|---|---|---|
| 1. Flagged + shim | W1: Google 6/6 blocked flagged (BiDi + real keyboard), 2/2 pass flag-free; v3 shim probe-CLEAN, pristine-realm name leak; pre-existing tabs early=true; panel probabilistic (fresh v3 P1 PASS, P2 CHALLENGE once) | REJECTED as end state |
| 2. Relaunch | W3: window ~1 s, BiDi session.new 46.5 s x5 launches, form/scroll survive, heap 7->0, 19/20 tabs, lazy tabs need OS click | REJECTED as end state; escape hatch only |
| 3a. RDP build | W2: webdriver natively false, evaluate 0.4 ms; W4: Google 3/3 PASS with server running + attached, panel P2/P5/C1 PASS, P1 1/2, control CHALLENGE x2 (void rule satisfied); attach-to-first-evaluate 3.0 ms, evaluate 0.5 ms, DOM read 0.3 ms; screenshot actor ABSENT; parent target reaches Zen internals (typeof) | PRIMARY LANE (Phase 1) |
| 3b. Extension bridge | W2: temp install 85 ms, MAIN-world document_start shim flips true->false, ~4 ms in-extension, 50.4 ms poll-bound round-trip, JS click isTrusted=false; permanent install/signing UNTESTED | FALLBACK lane; runner-up |
| 3c. Hybrid (chosen) | Composition of 3a + OS lane (W4: OS click isTrusted=true, ~2.2 s/batch) + internals path + 3b fallback | CHOSEN |
| Marionette chrome | W2: gZenWorkspaces/gZenFolders/gBrowser at 1.4 ms, needs MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1; --marionette forces webdriver=true (Stage 1 T3); chrome-observer shim failed | External maintenance lane only |
| SessionStore | W2: zen-sessions.jsonlz4 decodes trivially but stays empty for agent tabs (21 BiDi + 10 WebDriver); W3: human tabs collect (19 tabs, form/scroll stored) | Read-only inventory at most |

Speed note (redteam RT-07, adopted): eval micro-benchmarks are
reported, never scored alone. Acceptance measures end-to-end task
wall time vs the split baseline.

## Council and redteam verdicts

- **Council A:** phased hybrid RDP-primary (3c/3d); runner-up 3a.
  Routes 1/2 rejected on W1/W3. RT-01 named decision-blocking;
  spike before production code. Kill criteria and acceptance test
  in its position file.
- **Council B:** 3c hybrid; runner-up 3b + OS lane. Judged against
  the owner's actual day (Google entry, logged-in tabs, mid-task
  agent call, Zen-internals asks). Route 1 fails his search path;
  Route 2 breaks mid-flow (46 s + heap loss).
- **Redteam:** 23 attacks (RT-01..RT-23). Bottom line: R3a-primary
  (RDP evaluate lane + OS-input fallback, Marionette-chrome out of
  the human browser) is the only candidate worth the blocking
  spikes, RT-01 first. W4 has since answered RT-01/RT-08 (Google
  3/3 PASS under RDP; panel probabilistic with one P1 challenge -
  no "never blocked" claim), RT-03 partially (internals typeof
  reach proven, control unproven; screenshot absent, OS lane
  covers), RT-04 loopback leg (127.0.0.1 only, verified x2).
  RT-04's silent-attach acceptance remains an owner-level decision
  (see below). Remaining blocking items are listed under "What
  remains before landing".

## First slice (proven, W4)

Production-shaped stdlib RDP client (improvements/r10-seamless-w4/
rdp_client.py + test_rdp_client.py, self-test PASS): attach
(connect/listTabs/getTarget with selected-tab picking and
tabListChanged filtering), evaluate read/write, navigate with
re-attach on window-global swap, port-owner guard (refuses foreign
listener), fail-loud webdriver probe. Measured medians (headed
throwaway, Zen 1.24.3b): attach-to-first-evaluate 3.0 ms (n=12),
evaluate 0.5 ms (n=20), DOM read 0.3 ms, navigate-to-load ~54 ms
poll-bound (local + example.com). DOM write verified; JS click
isTrusted=false (OS lane required and proven isTrusted=true).
RDP screenshot: no actor on this build (4 methods refused) - OS
grim/computer-use observe stays the screenshot lane. Parent target:
gZenWorkspaces/gBrowser/gZenFolders all typeof object.

## Acceptance test (required before landing)

Normal-user path only: enter via search/homepage, click through
visible UI; no deep links, no internal setters as proof; evidence
shows entry, path, action, resulting state. Throwaway profile
first; owner profile only at a task boundary with the pill visible
and tabs recorded before. Pre-registered panel, cold trials,
flagged-raw control arm interleaved same day (control never blocks
= void, not passed). Owner-browsing arm reported separately from
agent-driven visits.

1. **Owner opens Zen normally** (normal launch path, 3c config):
   window up, tabs/workspaces present, startup probe CLEAN
   (webdriver false, native getter, no doc attribute, no
   automation globals), no connection prompts, no DevTools side
   effects.
2. **Google search works under the exact RDP pref set:** at least
   3 queries (acceptance target 5, varied, per redteam), SERP
   loads, click through to P1 timeanddate, P2 coolors, P5
   codeforces, C1 example.com; no unusual-traffic wall; panel
   outcomes recorded per arm; cold repeats across different hours.
   (W4 throwaway result: Google 3/3, P2/P5/C1 PASS, P1 1/2.)
3. **Agent acts in the same session:** same PID, no relaunch.
   Held RDP session: DOM read + write (median under 2 ms budget),
   navigate; OS lane: one trusted click (isTrusted=true verified
   at page level) + screenshot, pill visible. Owner tabs diffed
   before/after; zero owner tabs closed or navigated except the
   tasked tab.
4. **Pre-existing tab leg:** a tab loaded before agent attach
   reads early=false without reload (the W1 Test 3 failure mode;
   under flag-free RDP this should hold natively - prove it).
5. **Zen-internals leg:** one internals read (active workspace +
   pinned count) via RDP parent target; if write is claimed, one
   internals write (workspace switch) without flagged relaunch.
   If the escape hatch is needed, record it as escape-hatch use
   with W3 costs; acceptance marked partial, not silently passed.
6. **Concurrency arm:** owner DevTools open while agent evaluates;
   owner typing while agent navigates another tab; no errors, no
   focus theft beyond the pill contract. (RT-06)
7. **Security checks:** ports loopback-only verified from a
   non-loopback interface; attach attempt from an unrelated local
   process recorded; startup probe fails loud if webdriver=true or
   RDP port missing/misbound. (RT-04)
8. **Update drill:** after the next Zen update, cold-call the
   agent lane with no human touching the config; probe + Google
   spot check must pass before agent use resumes. (S8 pattern)
9. **Speed, honestly:** end-to-end wall time for 3 fixed real
   tasks vs the split baseline, same sites, same day.

## Kill criteria

1. One Zen update breaks the landed toolset (probe not CLEAN, or
   human-path block on the acceptance panel), or 7 days broken:
   retire to the interim split automatically. (Stage 2 Step 4,
   verbatim.)
2. RDP actor breakage on two consecutive Zen updates requiring
   client rewrites (not version bumps): RDP lane retired; evaluate
   extension lane as primary or return to split.
3. Extension permanent install impossible without unmaintainable
   signing, or does not survive a Zen update: 3b dropped; hybrid
   continues RDP + OS lane.
4. No named maintenance owner staffed (Muse owns per-update
   verification: automated startup probe + spot check; backup:
   coordinator on duty): build does not start, or stops.
5. OS-input lane cannot meet focus-safety at acceptable rate in
   acceptance: trusted actions restricted to the agent profile;
   seamless claim narrowed in writing, not silently.
6. (Already discharged) RDP Google-entry failure would have
   killed RDP-primary before build; W4 passed it (3/3). The
   criterion stands for the real-profile acceptance run.

## What remains before landing

Decision-blocking (redteam list, minus what W4 answered):
- **RT-04 owner decision:** prompt-connection=false means any
  local process can silently attach and evaluate JS in the owner's
  logged-in tabs. Loopback-only bind is verified; the silent-attach
  acceptance itself is an owner-level security decision, NOT yet
  recorded. Landing requires it in writing.
- **RT-20 credential policy:** same-session work needs a written
  policy + tool-enforced tab scoping (per-task tab scope,
  credential-tab denylist, drive-report probe + tab-list diff) or
  explicit owner acceptance of the risk. The S2 escape-hatch
  discipline was designed for rare exceptions; seamless makes it
  the main road.
- **RT-21 real-profile acceptance:** all spike evidence is
  throwaway-profile. Acceptance steps 1-9 must run on the owner's
  real profile at a task boundary before the criterion is declared
  met.
- **RT-03 depth:** Zen-internals CONTROL via RDP parent target
  (only typeof proven); screenshot stays OS lane (proven absent
  in RDP).
- **RT-02 depth:** isTrusted task suite on real tasks (upload
  picker, clipboard, drag, Turnstile-gated form) via the OS lane.
- **RT-06:** DevTools concurrency spike.
- **RT-05/RT-18:** per-update RDP smoke test + port registry with
  named owner + fail-closed channel selection (no channel selected
  = no drive, never guess).
- **RT-22 placement:** per component - RDP prefs + client config +
  port registry = machine layer (laptop only); generic RDP client
  = repo, OPTIONAL opt-in, default off; never repo default.
- **RT-14:** only if the 3b fallback is built - persistent
  extension install on Zen release without flags, surviving
  restart + update, failing loud.
- **RT-23:** session locking for multi-agent drives of one live
  session (undesigned).

Not changed by this task: owner's launch paths and live Zen
(flag-free, probe CLEAN since the 27/11 restart) are untouched.
The interim split remains the operating configuration until
acceptance passes. R10 stays open in every status report until
then, or until a kill criterion fires and the criterion is
renegotiated with the owner on that evidence.

## Evidence labels

- VERIFIED: Stage 1 flag/pref matrix; A5 panel + Google outcomes;
  W1 shim variants + Google isolation + pre-existing-tab limits;
  W2 latency/capability matrix (RDP native-false, Marionette chrome
  internals, extension mechanism, sessionstore block); W3 relaunch
  timings + fidelity; W4 RT-01 (Google 3/3, panel + control arm,
  void rule satisfied), slice latencies, parent-target typeof,
  screenshot absence, loopback bind.
- ASSUMED: deeper Zen-internals control via RDP parent target;
  panel pass rate generalizes beyond 27/11 (n small, warmth
  possible); WebSocket bridge closes extension latency gap.
- UNTESTED (blocking list above): real-profile behavior,
  DevTools concurrency, isTrusted task suite, persistent
  extension install, multi-agent session locking.

Coordinator, 27/11/2026. English only. No personal information in
this document; machine-specific configuration details live only on
the laptop machine layer.
