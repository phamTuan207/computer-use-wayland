# R10 Stage 2 decision - Cloudflare / navigator.webdriver (27/11/2026)

Stage 2 of Item 3 in team-decisions-20261127.md, decided on the
Stage 1 report (r10-stage1-report-20261127.md). Council A (evidence
and cost), Council B (owner intent and real usage), and an
independent redteam deliberated in parallel. Working files in this
directory: r10-stage2-councilA-20261127.md,
r10-stage2-councilB-20261127.md, r10-stage2-redteam-20261127.md.

Owner delegation 06:19 27/11: the team meets and decides on its own.
This document is that decision.

## Stage 1 facts carried into Stage 2 (all VERIFIED)

- Each launcher flag alone forces navigator.webdriver = true
  (BiDi-only true, Marionette-only true, no flags false). Removing
  a flag loses that agent attach lane. No runtime toggle exists.
- The pref route is dead: dom.webdriver.enabled=false changes
  nothing page-visible under either flag or both.
- The probe disagreement is explained: the shim is a BiDi preload
  script that applies only to documents loaded inside the holder
  session. A unified probe exists (r10-webdriver-probe.mjs) and
  certifies only its listed signals, not TLS/IP/behaviour.
- Continuity count: 0 of 55 frozen R3-L3 tasks needed owner-session
  continuity, with the stated caveat that the frozen list was
  designed around fresh pages.
- ASSUMED, still unproven: Cloudflare blocks in this environment
  are driven mainly by the webdriver signal.

## The fork and how the team reads it

The decision turns on "the same Zen" in the owner criterion (human
browses normally with no Cloudflare block; agents callable to
computer-use Zen at any time; Zen stays AI-optimized; owner
addendum: build a dedicated tool if needed).

Council A read it as same install: the criterion as written does
not say "in my tabs/logins", the measured workload shows zero
same-session demand, and Ponytail (smallest complete change first)
favours the split. Council B read it as same live session: the
standing acceptance test says "agent drive on the same Zen
session", the owner's lived pattern is agents driving his live
tabs and logins (R3-056 tab restore, Gmail confirmations by the
agent as a standing rule, Codeforces under his manager nick), and
the "build a dedicated tool if needed" addendum only makes sense
if the bar includes something the split cannot deliver. The
redteam attacked "same install" as a lawyerly redefinition (S1)
and the 0/55 count as selection bias (S2): the frozen list never
looked for "do X in my account" tasks, so it cannot price their
absence.

Team ruling: "the same Zen" means the same live session. That is
the natural reading of the owner's words given how this machine is
actually used, and the team will not silently downgrade the
criterion to "same install" by reinterpretation. Council A's cost
arguments are adopted as sequencing discipline (cheap and
reversible first, expensive and unproven gated on evidence), not
as a redefinition of the bar. R10 therefore stays OPEN until the
same-session end state passes acceptance, or until the build is
proven impossible and the criterion is renegotiated with the owner
with that evidence in hand.

## Decision

Staged, with evidence gates. Boundary-restart is rejected as
dominated (unanimous).

### Step 1 (immediate): adopt the two-profile split as INTERIM

The split unblocks the human browsing leg today. It is labelled
interim in every report; it is not criterion satisfaction.

- Human profile: the owner's existing Zen profile, launched
  flag-free (plain zen, not the zen-ai launcher). Verified clean:
  no flags reads webdriver false.
- Agent profile: dedicated profile via the existing zen_cli.py
  dedicated-session machinery, launched flagged (BiDi 9222,
  Marionette 2828). Agents attach to the agent profile by default
  and never to the human profile in normal operation.
- Interim residue stays in the agent profile until the build lands
  or is killed: pinned shim hash, probe result in every drive
  report, dirty probe = stop. The shim's getter toString tell
  (function () { [native code] } vs native function webdriver()
  { [native code] }) is known-imperfect interim, not a solution.
- Redteam amendments adopted as requirements, not options:
  (a) launch-path audit: every entry point (desktop entry,
  terminal zen, file association, PWA, update restart, session
  restore) resolves flag-free for the human profile, plus a
  startup probe on the human profile that fails loud if
  webdriver=true (S6).
  (b) headed concurrency gate: both profiles open at once, agent
  drives while the human browses, pill routing and RAM recorded,
  no profile-lock errors across a restart cycle (S3).
  (c) continuity escape hatch, explicit and logged, never silent:
  owner-account tasks either run as a deliberate flagged session
  on the human profile (tabs recorded before, probe in the drive
  report, restore after) or as a logged-in agent-profile task.
  The silent flagged-drive of the human profile (redteam S2
  option c) is forbidden.
  (d) credential policy for the agent profile: task-scoped
  accounts by default (R3-029 pattern); any login as the owner
  requires explicit per-task approval and is logged; the owner
  never daily-drives the agent profile (S5).
  (e) parity mechanism with a named owner: what syncs between
  profiles (prefs, extensions, filter lists), what never syncs
  (cookies, logins, session), and a drift check in the drive
  report (S4).
  (f) update drill: after a Zen update, cold-call the agent lane
  with no human touching the agent profile and record whether it
  attaches clean (S8).
- Human-leg verification (normal-user path): owner opens Zen
  normally, searches and browses his real Cloudflare-fronted sites
  via search/homepage click-through; pass = no interstitial and
  webdriver false on probe read. Repeat after every Zen update.

### Step 2 (gate, hours): run the A5 controlled A/B experiment

Before any build commitment, test the ASSUMED cause with existing
throwaway-profile machinery. Same machine/IP/day, cold profile
per trial, human entry path, pre-registered site panel including
sites that demonstrably block in this environment (the 06:33
live-Zen interstitial context) and high-protection Cloudflare
sites:

- Arm 1: flagged, no shim.
- Arm 2: flagged + holder shim.
- Arm 3: flag-free.

Outcomes decide honestly:
- Arm 3 also blocks: webdriver is not the main driver; both
  branches fail leg 1; stop and rethink (IP/TLS), report honestly,
  no scope expansion.
- Arm 2 passes like Arm 3: the build is unnecessary; keep the
  shim, and the split (adopted for safety) becomes the end-state
  candidate with the criterion renegotiated on that evidence.
- Only Arm 3 passes: proceed to the spike (Step 3).

Acceptance rigor for this and all later tests (redteam A2/A6/A7):
fixed panel frozen before testing, cold trials (no cf_clearance
carryover), flagged control arm interleaved same-day, owner-
browsing arm reported separately from agent-driven visits, block
outcomes recorded per arm. If the control arm never blocks, the
test is void, not passed.

### Step 3 (gate, 1 day): spike the hiding layer

Only if A5 says only flag-free passes. Time-boxed spike: prove a
JS layer (extension content script at document_start preferred
over autoconfig for fail-safe behaviour, redteam B5) makes the
unified probe CLEAN including cross-realm/iframe reads (B3) and
wins the race test (earliest inline script, dynamic iframe,
worker all read false with native-form getter, B4). Spike failure
= build dead; fall back to the split as end state and renegotiate
the criterion with the owner on that evidence.

### Step 4 (conditional commission): build the hiding layer

Commissioned only if Steps 2 and 3 both pass. Required elements,
named now per the Stage 1 decision:

- Scope: normalize page-visible automation signals so pages see a
  normal browser. Explicitly out of scope: solving CAPTCHAs,
  rotating or spoofing IP addresses, spoofing TLS or network
  fingerprints, imitating human behaviour, promising Cloudflare
  passes any given visit.
- Frozen coverage (frozen today; any new signal class needs a new
  decision): navigator.webdriver false with correct type;
  getter toString in native form (function webdriver()
  { [native code] }); descriptor location and configurability
  matching native; no documentElement automation attribute;
  automation-globals list (as enumerated in the unified probe)
  clean; plugins length plausible per probe expectation; parity
  across documents inside and outside a BiDi holder session.
- Maintenance owner: Muse (main agent) is the named owner of
  per-update verification; verification is automated (startup
  probe with fail-loud banner plus human-path spot check), so
  ownership is supervision of an automated gate, not manual
  labour. Backup: coordinator on duty. If this ownership cannot
  be staffed, the build does not start.
- Cost estimate: A5 half a day; spike 1 day; full build 2-5 days
  research + build + test; per major Zen update 0.5-1 day
  re-verification until automated, then spot checks.
- Kill criteria (tightened per redteam B6): ONE Zen update
  breaking the layer (probe not CLEAN, or human-path block), or
  7 days broken, retires the layer to the split automatically.
  A5 or spike failure kills the build before it starts. No named
  owner kills the build.
- Placement: active configuration on the laptop machine layer;
  repo carries it only as OPTIONAL opt-in, default off, with the
  probe test included. Never repo default (B9).
- Acceptance: probe-clean is necessary, not sufficient. Repeated
  human-path visits (open Zen normally, search, click through to
  multiple Cloudflare-protected sites, no deep links or internal
  setters) with no block, plus an agent computer-use drive on the
  same Zen session with the pill visible; evidence shows entry,
  path, action, resulting state; block outcomes keep being
  recorded separately in drive reports. Test rigor per Step 2
  (panel, cold trials, control arm, separate owner-browsing arm).
  Throwaway profile first; real profile only at a task boundary
  with the pill visible.

## Redteam attacks and how this decision answers them

- S1 (lawyerly same-install): answered by the fork ruling above -
  same live session is the bar; the split is interim, not closure.
- S2 (0/55 selection bias, continuity trilemma): answered by the
  explicit logged escape hatch (Step 1c) and by keeping R10 open;
  the 0/55 count is not used to claim zero loss.
- S3 (headed concurrency unproven): Step 1b gate.
- S4 (parity rot): Step 1e.
- S5 (credential blast-radius inversion): Step 1d.
- S6 (launch-path leakage): Step 1a.
- S7 (benchmark vs real help): the same-session end state is
  retained precisely for interactive help; the split interim
  accepts the loss temporarily and visibly.
- S8 (update split-brain): Step 1f.
- B1 (frozen coverage theatre): A5 measures whether the covered
  signals are the ones that matter before money is spent.
- B2 (2-5 days on ASSUMED cause): ordering fixed - A5 first.
- B3 (toString unclosable from JS): 1-day spike gate; failure
  kills the build on its own terms.
- B4 (document_start races): race test inside the spike gate.
- B5 (autoconfig dead browser / silent exposure): extension
  route preferred; automated startup probe fails loud.
- B6 (maintenance-owner fiction, slow kill criteria): named
  owner + automation + tightened kill criteria (one update /
  7 days).
- B7 (arms-race asymmetry): accepted as a real cost; the build
  is only commissioned if A5 + spike prove the covered signals
  are sufficient today, and kill criteria cap the treadmill.
- B8 (24-tab blast radius, one-session limit): structural, not
  fixed by the build; tab-safety discipline (record before
  attach, never close owner tabs) stays mandatory in the end
  state; the interim split removes the blast radius meanwhile.
- B9 (stock-app principle): placement fixed as machine-layer
  opt-in, default off.
- A1-A7 (acceptance rigor, ASSUMED claim): Step 2 is the A5
  experiment itself, with A2/A6/A7 rigor written into every
  acceptance test in this decision.

## Council positions in brief

- Council A: adopt the split as final under a same-install
  reading; do not build unless the owner rules same-session
  mandatory or measured continuity demand appears. Its adoption
  plan and cost analysis are adopted here as the interim plan
  and sequencing discipline; its fork reading is not adopted.
- Council B: staged hybrid - split now as interim, commission
  the build in parallel (spike first), same-live-session reading,
  R10 not closed on the split. Adopted in structure; the build
  commission is gated on A5 + spike per redteam B2/B3 rather
  than started unconditionally in parallel.
- Redteam: split survives better; neither branch should be chosen
  until A5 runs and the fork is confirmed. A5 adopted as Step 2;
  the fork is decided by the team under the owner's delegation
  (same live session) instead of bounced back, with the split
  adopted immediately as interim so the human leg is unblocked
  while evidence is gathered.

## Concrete next actions (parent executes, in order)

1. SSH-capable worker adopts the interim split: profile setup,
   launch-path audit + human-profile startup probe, headed
   concurrency gate, credential policy and parity mechanism
   written down, human-leg verification. Throwaway profile first;
   real profile only at a task boundary with the pill visible.
   Never close or navigate owner-opened tabs/windows.
2. SSH-capable worker runs A5 (half day): three arms, cold
   profiles, frozen panel, control arm, per-arm outcomes logged
   to the master event log and reported to the parent. A5 outcome
   is reported to the owner plainly, whichever way it lands.
3. Only if A5 says only flag-free passes: SSH-capable worker runs
   the 1-day spike (probe CLEAN incl. cross-realm reads + race
   test). Spike result decides the build commission.
4. Only if the spike passes: build commissioned with the frozen
   coverage, named owner, cost, and kill criteria above;
   acceptance per Step 4. Until then, no build starts.
5. R10 stays open in every status report until Step 4 acceptance
   passes, or A5/spike kills the build and the criterion is
   renegotiated with the owner on that evidence.
6. Every step logged to the master event log via
   ~/workspace/agent-event-log/log-event.sh with the full chain.

## Evidence labels

- VERIFIED: Stage 1 matrix (each flag forces true; pref dead;
  shim lifetime = holder session; probe coverage limits; shim
  toString tell; one WebDriver session limit); 0/55 continuity
  count and its fresh-page caveat; 24-tab incident 26/11;
  live-Zen Cloudflare interstitial 06:33 27/11; dedicated-profile
  machinery exists (zen_cli.py); owner criterion and addendum as
  fixed 06:20-06:21 27/11.
- ASSUMED: blocks driven mainly by webdriver (tested by Step 2);
  JS layer can close the toString tell (tested by Step 3);
  future real asks include same-session tasks at meaningful
  frequency (Council B inference from the owner's lived pattern);
  per-update verification effort 0.5-1 day until automated.
