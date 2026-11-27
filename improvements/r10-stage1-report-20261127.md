# R10 Stage 1 report - Cloudflare / navigator.webdriver investigation (27/11/2026)

Stage 1 of Item 3 in team-decisions-20261127.md. Read-only
investigation in throwaway headless profiles on spare ports. Nothing
built, no launcher changed. Live Zen never restarted, reconfigured,
or signalled by this work (see "Live Zen note" below).

Owner criterion (fixed): human browsing in Zen presents as a normal
browser to Cloudflare (no automation signals such as
navigator.webdriver leaking to pages), while agent computer-use
control of the same Zen stays available at any time and Zen stays
AI-optimized.

## Headline findings

1. **Each launcher flag alone forces navigator.webdriver = true.**
   `--remote-debugging-port` (BiDi Remote Agent) alone: true.
   `--marionette` alone: true. No flags: false (native boolean).
2. **The preference layer cannot fix it.** `dom.webdriver.enabled =
   false` does not change the page-visible value under either flag
   or both. The flag/pref route is dead; the signal is inseparable
   from agent attach at the flag/pref layer.
3. **The R3-100 probe disagreement is explained.** It was not an
   eval-path difference. Both transports read identical values in
   identical browser state. The shim exists only inside the holder's
   BiDi session, on documents loaded after `addPreloadScript`.
   R3-100 read via Marionette in a keyboard-created tab outside any
   holder session, so it read the native `true`.
4. **Continuity count: 0 of the 55 frozen R3-L3 tasks needed
   owner-session continuity.** The only continuity-dependent task
   was R3-056, an owner-added incident-repair task (restore the
   user's own tabs). R3-029 used a task-scoped test account, not
   the owner's session.

## (a) Launcher flag inventory

- Launcher: `~/.local/bin/zen-ai` (machine layer) execs
  `zen-bin --remote-debugging-port=9222 --marionette "$@"`. Every
  non-terminal launch path resolves to it via the desktop entry.
- Live process confirmed: `zen-bin --remote-debugging-port=9222
  --marionette`, BiDi on 9222, Marionette on 2828.
- `zen-bin --help` automation-relevant surface: `--marionette`,
  `--remote-debugging-port`, `--remote-allow-hosts`,
  `--remote-allow-origins`, `--start-debugger-server`,
  `--jsdebugger`. No runtime toggle that enables an endpoint on an
  already-running instance was found in this surface; conditioning
  a flag means relaunching (the boundary-restart alternative).
- Removing `--remote-debugging-port` loses the BiDi lane (holder,
  zen_cli.py). Removing `--marionette` loses the Marionette lane
  (zen_dom.py, geckodriver). Removing both loses all agent attach.

## Test matrix (throwaway headless profiles, spare ports 9333/2838/4445)

Probe: improvements/r10-webdriver-probe.mjs (this commit). Driver:
improvements/r10-stage1-run-tests.sh (this commit). All readings on
a data: page; verdict vocabulary CLEAN / SHIMMED / DIRTY / ABSENT /
ERROR.

| Test | Config | Transport | webdriver | Verdict |
|---|---|---|---|---|
| T9c | no flags (control, screenshot read) | - | false (boolean) | native clean |
| T2 | `--remote-debugging-port` only | BiDi | true | DIRTY |
| T3 | `--marionette` only | Marionette (geckodriver) | true | DIRTY |
| T4 | both flags (live replica) | BiDi | true | DIRTY |
| T4 | both flags (live replica) | Marionette | true | DIRTY |
| T5 | both + `dom.webdriver.enabled=false` | BiDi | true | DIRTY |
| T5 | both + `dom.webdriver.enabled=false` | Marionette | true | DIRTY |
| T6 | BiDi only + `dom.webdriver.enabled=false` | BiDi | true | DIRTY |
| T7 | both, pre-existing tab before shim | BiDi | true | DIRTY |
| T7 | both, new tab after `addPreloadScript` | BiDi | false, Proxy toString | SHIMMED |
| T7 | both, pre-existing tab after reload | BiDi | false, Proxy toString | SHIMMED |
| T7 | both, new tab after `removePreloadScript` | BiDi | true | DIRTY |
| T8 | BiDi session held, Marionette session create | - | - | ERROR: Maximum number of active sessions |
| T8b | BiDi shimleave, then Marionette read | Marionette | true (landed on original about:blank tab) | DIRTY |

Agent attach per config: T2 BiDi attach works, Marionette absent.
T3 Marionette attach works, BiDi absent. T4 both work, sequenced
(one WebDriver session at a time across protocols, T8). T5/T6
attach still works; only the value stays true.

Non-webdriver signals were clean in every config: documentElement
`webdriver` attribute null, no known automation globals,
navigator.plugins.length 5 (headless throwaway; value itself is
profile-dependent, recorded for completeness).

Failed measurement routes, recorded honestly: headless
`--print-to-pdf` hung (60s timeout, no PDF) on both data: and file:
pages; the no-flags control was instead read from a headless
screenshot of a page that writes the value as text (T9c).

## (b) Preference layer

- Live profile prefs.js contains no webdriver-related pref
  (read-only grep; only unrelated "remote" matches).
- `dom.webdriver.enabled=false` in a throwaway profile changes
  nothing page-visible under either flag (T5, T6). The pref route
  is dead for this purpose.

## (c) Why the probe disagreed, and the unified probe

- T4: BiDi `script.evaluate` and Marionette `execute/sync` read
  identical values in the same browser state. Eval path is not the
  variable.
- T7: the pinned shim is a BiDi preload script. It applies to
  documents loaded after `addPreloadScript` in that session,
  including reloads of pre-existing tabs, and stops applying to new
  documents after `removePreloadScript`. Already-loaded documents
  outside the session never get it.
- R3-100's drive report: the probe ran via zen_dom.py (Marionette)
  in a task-created blank tab (keyboard Ctrl+N), i.e. a document
  loaded outside any holder session. Native `true` is the expected
  reading there. The holder's probe-clean readings came from inside
  the holder session. No contradiction remains.
- T8: the Remote Agent allows one WebDriver session at a time
  across BiDi and Marionette ("Maximum number of active sessions").
  Cross-transport reads must be sequenced, never concurrent.
- T8b: after a BiDi session ends, its shimmed tab is not readable
  as the shimmed document by a later Marionette session (read
  landed on the original about:blank tab). Cross-session shim reads
  do not work; the shim's lifetime is the holder session.

Unified probe delivered: `improvements/r10-webdriver-probe.mjs`.
One expression, two transports (BiDi / WebDriver-HTTP via
geckodriver), one verdict vocabulary. It checks: webdriver value
and type, descriptor location (prototype vs navigator), getter name,
getter toString (native `function webdriver() { [native code] }` vs
shim `function () { [native code] }`), configurability,
documentElement `webdriver` attribute, navigator.plugins.length,
and a fixed list of known automation globals. **Coverage stated
plainly: the probe certifies exactly those listed signals. It does
not certify TLS fingerprints, IP reputation, behaviour, or any
signal outside the list.** Run it with:

    node r10-webdriver-probe.mjs --transport bidi --port 9222 --mode probe
    node r10-webdriver-probe.mjs --transport webdriver --port 4444 --mode probe
    node r10-webdriver-probe.mjs --transport bidi --port 9222 --mode shimtest

(`shimtest` reproduces the T7 lifecycle; `shimleave` exists for the
T8b sequence.) One residual: a Marionette read of a document loaded
under a live BiDi preload shim was not directly measured (T8 blocks
concurrency; T8b shows the tab does not survive session end for a
later read). By mechanism (page-realm prototype redefine; T4 proves
both transports read the same realm state) it would read `false`.
Labelled ASSUMED, not load-bearing for the recommendation.

## (d) Alternatives priced

### Continuity count (method + result)

Method: classified all 55 frozen tasks from the frozen answer keys
(docs/rung3-answer-keys.md) plus runner briefs. A task "needed
owner-session continuity" if it operated on the owner's existing
session state: the user's logged-in accounts as the user, the user's existing
tabs or session restore, or the user's profile data. Standing
"never close owner tabs" boilerplate in briefs is tab-safety, not a
continuity requirement.

Result: **0 of 55 frozen tasks needed owner-session continuity.**
They are fresh-page public-site tasks, local-fixture tasks, or
terminal/file tasks. R3-029 used a task-scoped test account on a
demo store (parent-held credential), runnable in any profile.
R3-017 and R3-025 ran in Brave, not Zen. The one
continuity-dependent task in the run was R3-056 (position 56,
owner-added after the tab-cleanup incident): restore the owner's
own tabs/essentials/folders. Caveat, stated plainly: the frozen
list was designed around fresh pages; the count measures this run,
not all future agent work. Tasks of the form "do X in my account /
my tabs" would need continuity and are not represented in the 55.

### Alternative 1: two Zen profiles in one install

Human profile launched flag-free (verified clean, T9c); agent
profile launched flagged via the existing dedicated-session
machinery (zen_cli.py already implements dedicated-profile sessions
and refuses profiles inside ~/.config/zen).

- Build cost: LOW. Launcher split (human default flag-free; agent
  sessions through the dedicated path), brief updates, one
  acceptance pass. Most components exist and are proven.
- Criterion: leg 1 (human clean) YES. Leg 2 (agent computer-use at
  any time) YES, on the agent profile's Zen. Leg 3 (Zen stays
  AI-optimized) YES for the agent profile. Open question for Stage
  2: does "the same Zen" in the criterion mean same install or same
  live session? This alternative satisfies same-install, not
  same-session.
- Losses: agents cannot act inside the owner's live tabs/logins
  (e.g. the user's Gmail as the user) without a separate login in the agent
  profile; two profiles to maintain; agent profile is also a
  safety win (no owner credentials in the automation blast radius).
- Continuity evidence: 0/55 frozen tasks lose anything.

### Alternative 2: boundary-restart model

Launch clean; when an agent is called, restart Zen with flags
(record tabs first, restore after, per the Item 4 boundary restart
procedure); restart clean again when the agent finishes.

- Build cost: MEDIUM. Launcher logic plus record/restore wiring.
  Recording tabs before the flagged restart cannot use BiDi (needs
  the flag); sessionstore-based recording (R17 tooling) is the
  available route.
- Criterion: leg 1 YES only between agent calls; DURING any agent
  session the human's browsing in that same session is flagged
  again. Leg 2 YES with restart latency (observed Zen relaunch to
  usable session: minutes, and Task 56 showed restore fidelity is
  imperfect). Leg 3 YES.
- Losses: two restarts per agent call, owner-visible disruption,
  session-restore risk on every cycle, leg-1 failure while agents
  work. Dominated by Alternative 1 on friction and by the build on
  criterion fidelity. Recommend against.

### Alternative 3: build a dedicated hiding layer

In-browser layer that normalizes page-visible automation signals
for every document in the flagged browser (extension content script
at document_start, or chrome-privileged autoconfig JS), replacing
per-session preload discipline.

- Build cost: HIGHEST. Research + build + test estimated 2-5 days,
  plus verification after every Zen update (probe run), plus a
  named maintenance owner. Per the Stage 2 decision requirements:
  frozen coverage list at build time, cost estimate, kill criteria
  (e.g. two consecutive Zen updates breaking the layer retires it
  to Alternative 1).
- Criterion: the only route satisfying all three legs literally,
  including same-session agent control with human-clean browsing.
- Known tell to engineer against: the current shim's getter
  toString is `function () { [native code] }` vs native
  `function webdriver() { [native code] }` (T7, SHIMMED verdict).
  Any build must close or explicitly accept this tell; the unified
  probe detects it.
- Frozen coverage proposed for the build decision: navigator.
  webdriver value + native-form getter toString. (DocumentElement
  attribute, automation globals, plugins length were already clean
  in every tested config; adding them costs nothing but they are
  not currently dirty.)

## Recommendation for Stage 2

The flag/pref route is proven dead (T2, T3, T5, T6), so Stage 2 is
a genuine fork, and the fork turns on one phrase in the criterion:

- If "the same Zen" means **same install**: adopt Alternative 1
  (two profiles). Cheapest, components proven, human leg verified
  clean, 0/55 continuity loss. Do not build.
- If "the same Zen" means **same live session** (agents must be
  able to act in the user's own tabs/logins at any time while the user's
  browsing stays clean): only Alternative 3 (build) satisfies the
  criterion as written. Commission it with the frozen coverage,
  named owner, cost estimate, and kill criteria the decision
  requires. The unified probe ships as its fail-loud check.
- Alternative 2 (boundary restart) is dominated either way.
  Recommend against.

Either branch keeps the acceptance bar from the decision:
probe-clean is necessary, not sufficient; repeated human-path
visits to multiple Cloudflare-protected sites with no block, plus
an agent drive on the same Zen with the pill visible; block
outcomes recorded separately. Current-problem evidence, same day:
the parallel CF735368 lane hit a Cloudflare interstitial
("Just a moment...") in the owner's live flagged Zen at 06:33
(master event log, cf735368-driver).

## Live Zen note (transparency)

During the Stage 1 window the owner's live Zen changed PID
(4059095 to 37679, started 06:37:47). The master event log shows
the parallel CF735368 driver lane recorded the death at ~06:35
(cause unattributed in their log) and relaunched via the standard
launcher. Stage 1 tests ran only in throwaway profiles with
`--no-remote` on spare ports, and every kill verified the target
cmdline carried a throwaway profile path; Stage 1 never signalled
the live process. Ports 9222/2828 verified listening on the new
process after cleanup.

## Cleanup verification

All test instances stopped (kill verified against throwaway-profile
cmdlines), throwaway profiles removed per test, geckodriver
instances killed, /tmp/r10-stage1 removed from the laptop after
logs were pulled, no test processes remain (verified by ps), live
Zen ports listening.

## Evidence labels

- VERIFIED: launcher identity and flags (zen-ai script read; live
  process cmdline).
- VERIFIED: T2/T3/T4/T5/T6 webdriver values (probe JSON in matrix
  log, this commit's driver script reproduces them).
- VERIFIED: T7 shim lifecycle (four readings, matrix log).
- VERIFIED: T8 one-session limit (geckodriver error text).
- VERIFIED: T9c no-flags false (screenshot read; print-to-pdf
  route failed and is recorded as failed).
- VERIFIED: live prefs.js has no webdriver pref (read-only grep).
- VERIFIED: continuity count method and result (frozen answer keys
  + briefs + grades ledger task list).
- ASSUMED: Marionette read of a BiDi-shimmed document returns false
  (mechanism argument; T4 same-realm evidence; not directly
  measured due to T8/T8b constraints).
- ASSUMED: Cloudflare blocks in this environment are driven mainly
  by the webdriver signal. If blocks persist with a CLEAN probe,
  report that honestly; do not expand evasion scope (per decision).
