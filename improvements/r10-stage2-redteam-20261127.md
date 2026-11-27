# R10 Stage 2 REDTEAM - Cloudflare / navigator.webdriver (27/11/2026)

Independent redteam. AI-to-AI communication in English. I attack
every proposal. I do not coordinate with any other agent.

Basis: Stage 1 investigation facts as briefed (verified matrix,
probe, continuity count). Where I rely on them I label VERIFIED
(per Stage 1) or ASSUMED. I did not touch any browser, laptop,
or other files.

Owner criterion (fixed 06:20-06:21 27/11, verbatim sense):
human opens Zen and browses/searches normally without Cloudflare
blocking; agents callable to computer-use Zen at any time; Zen
stays AI-optimized. Owner addendum: "build a dedicated tool if
needed". Standing principle: repo must work on stock apps;
machine optimizations only as OPTIONAL (opt-in, default off).

The fork: "the same Zen" = (i) same install, or (ii) same live
session.

---

## 1. Attacks on the SPLIT branch (two profiles, one install)

### S1. "Same install" is a lawyerly redefinition of the owner's words
- Severity: CRITICAL
- Attack: In ordinary language, "Zen" for the owner is the
  browser the user lives in: the user's window, the user's tabs, the user's logins. Stage 1
  redefines it to "same install" and then declares legs 1-3
  satisfied. That is semantic drift by the team, not a decision
  by the owner. If the owner meant same live session (the natural
  reading of "agents callable to computer-use Zen at any time"
  while the user browses in it), the split fails leg 2 by definition:
  agents can never act in the session the user is looking at.
  VERIFIED: Stage 1 itself flags this as the open question.
  ASSUMED: that the owner would accept the install reading.
- Evidence that would answer it: the owner's explicit, recorded
  confirmation that same-install (separate agent profile, no
  access to the user's live tabs/logins) satisfies the user's criterion. Not a
  team inference, not silence. Without that sentence, the split
  is built on an unapproved reinterpretation.

### S2. The 0/55 continuity count proves nothing about future work
- Severity: CRITICAL
- Attack: VERIFIED: 0 of 55 frozen R3-L3 tasks needed owner-
  session continuity; the only continuity task was R3-056
  (owner-added tab restore). But the frozen list was designed
  around fresh pages (Stage 1 caveat, VERIFIED). Using it to
  price future loss is selection bias. Real standing work needs
  the user's session: Gmail confirmation by the agent itself (standing
  hard rule), Codeforces under the user's nick (the CF735368 lane hit a
  Cloudflare interstitial in the user's live Zen at 06:33 on 27/11,
  VERIFIED per Stage 1), Drive, Notion, GitHub as the user.
  The first such task forces a trilemma, all bad:
  (a) refuse / ask the owner to do it manually - violates
      "agents callable at any time" and the DO IT YOURSELF rule;
  (b) log in separately in the agent profile - duplicate logins,
      2FA friction, session divergence (agent sees a different
      account state than the owner);
  (c) quietly drive the human profile flagged - leg 1 fails
      exactly where it matters (the user's real accounts).
  Option (c) is what will actually happen under time pressure,
  silently reintroducing the flagged profile and defeating the
  split where it counts.
- Evidence that would answer it: an inventory of non-R3 agent
  tasks from the last 30 days that needed the user's logged-in session,
  counted honestly. If that count is non-trivial, the split needs
  an explicit continuity escape hatch (see Verdict), not a claim
  of "0 loss".

### S3. Two simultaneous headed Zen instances are unproven here
- Severity: HIGH
- Attack: VERIFIED: Stage 1 ran throwaway profiles headless with
  --no-remote on spare ports. That proves isolated headless
  instances work. It does NOT prove two headed instances running
  concurrently on Hyprland/Wayland, both usable, with correct
  window focus, pill routing to the right window, and no profile
  lock ("Firefox is already running") errors. Firefox-family
  profile locking, --no-remote / -P semantics, update prompts,
  and crash recovery across two instances are all untested in
  the headed concurrent case. RAM: two Zen instances roughly
  double browser memory on a laptop also running agent CLIs.
  VERIFIED: Remote Agent allows only ONE WebDriver session at a
  time (T8) - the split needs distinct ports per profile and a
  routing discipline so an agent never attaches to the human
  profile by mistake.
- Evidence that would answer it: a live headed concurrency test
  on the real machine: human profile flag-free + agent profile
  flagged, both open, agent drives while human browses, RAM/CPU
  recorded, pill verified on the agent window only, no lock
  errors across a restart cycle.

### S4. Profile parity will rot, and nobody owns the sync
- Severity: HIGH
- Attack: The human profile evolves daily (extensions, prefs,
  search engines, filter lists, AI-optimization prefs). The
  agent profile freezes at creation. Within weeks the agent is
  driving a different browser than the owner uses: missing
  extension, different cookie-banner behaviour, different
  rendering. Tasks then fail in the agent profile that would
  pass in the human profile, and debugging wastes time on
  profile drift instead of the task. VERIFIED: zen_cli.py
  refuses profiles inside ~/.config/zen, so "just copy the
  profile" is not the existing machinery's model. No sync
  mechanism, drift detector, or owner is named in the split
  proposal.
- Evidence that would answer it: a named parity mechanism
  (what syncs, what never syncs - cookies/logins must not),
  a drift check in the drive report, and a named owner.

### S5. The "safety win" inverts once the agent profile gets logins
- Severity: HIGH
- Attack: Split claims a safety win: no owner credentials in
  the automation blast radius. True only while the agent profile
  stays login-free. To be useful it will accumulate logins:
  task test accounts, then real ones (standing login rule uses
  the user's Gmail account; GitHub as the user for repo work). Result:
  credentials in TWO profiles, one of them less watched and
  driven by full-access agents. Worse, history VERIFIED: agent
  automation once closed 24 owner tabs including 5 essentials
  and 3 pinned (26/11). In the split that blast radius moves to
  the agent profile - good - until the owner, finding the user's
  accounts already logged in there, starts using the agent
  profile as the user's daily browser. Then the user is back on a flagged
  browser and leg 1 is dead by migration, not by decision.
- Evidence that would answer it: a credential policy for the
  agent profile (which logins allowed, enforced how, audited
  how) plus a guard that the owner never daily-drives it
  (e.g. distinct theme/name, launcher discipline).

### S6. The human profile is clean only if every launch path is clean
- Severity: MEDIUM-HIGH
- Attack: VERIFIED: flag-free profile reads webdriver=false
  (T9c). But today every non-terminal launch resolves to the
  flagged zen-ai launcher. The split requires a launcher split;
  any missed path (terminal `zen`, file association, PWA,
  update-triggered restart, session restore) silently launches
  the human profile flagged. The owner then gets blocked and
  nobody knows why, because the probe gate (dirty = stop) runs
  in drive reports, not on human launches.
- Evidence that would answer it: an enumerated launch-path
  audit (every entry point resolves flag-free for the human
  profile) plus a startup probe on the human profile that
  fails loud if webdriver=true.

### S7. Split optimizes for the benchmark, pessimizes for real help
- Severity: MEDIUM
- Attack: The core computer-use value is "agent helps with what
  I am looking at". Split destroys that: the agent cannot see
  the owner's tab, scroll position, half-filled form, or
  logged-in view. The owner must copy a URL across profiles and
  lose page state. R3 tasks never needed this (fresh pages);
  interactive daily help needs it constantly. ASSUMED: future
  value is mostly benchmark-style tasks. That assumption is
  unstated and unpriced.
- Evidence that would answer it: a sample of real interactive
  requests ("do X on this page") and whether cross-profile
  URL-copy preserves enough state to complete them.

### S8. Update split-brain blocks the agent lane silently
- Severity: MEDIUM
- Attack: One install updates; both profiles migrate. An agent
  profile left unused for weeks may hit a profile-version
  migration prompt or downgrade guard on next agent call,
  blocking the lane until a human clicks through - on the
  profile nobody watches. "Callable at any time" fails at the
  exact moment of an urgent call after an update.
- Evidence that would answer it: an update drill: update Zen,
  then cold-call the agent lane with no human touching the
  agent profile, and record whether it attaches clean.

---

## 2. Attacks on the BUILD branch (dedicated hiding layer)

### B1. Frozen coverage (webdriver + getter toString) is theatre vs Cloudflare
- Severity: CRITICAL
- Attack: VERIFIED: the unified probe certifies only its listed
  signals; it does not certify TLS fingerprints, IP reputation,
  behaviour, or any signal outside the list. Cloudflare
  interstitials / Bot Management / Turnstile can draw on TLS
  JA3/JA4, HTTP/2 fingerprint, IP reputation, cf_clearance
  history, JS challenge execution, canvas/WebGL, many navigator
  properties beyond webdriver, and behavioural signals. The
  build fixes exactly one signal family. Its success probability
  is the joint probability that (blocks here are webdriver-
  driven) AND (no other signal triggers). Neither factor is
  measured. Shipping a "hiding layer" that hides one signal
  while the blocker uses twenty is security theatre with a
  maintenance bill.
- Evidence that would answer it: the controlled A/B in section 3
  (A5) showing flagged+hidden passes where flagged-raw blocks,
  on sites that actually block in this environment, cold.

### B2. 2-5 days + forever maintenance spent on an ASSUMED cause
- Severity: CRITICAL
- Attack: VERIFIED: Stage 1 labels "Cloudflare blocks here are
  driven mainly by webdriver" as ASSUMED, not verified. The
  build branch commits the highest cost (2-5 days research+
  build+test, verification after every Zen update, named owner)
  BEFORE testing that assumption, when a hours-long experiment
  using existing throwaway-profile machinery can test it (A5).
  That ordering is indefensible: measure the cause first, then
  price the cure.
- Evidence that would answer it: A5 results. If flag-free also
  blocks, the build is pointless. If flagged+shim already
  passes, the build is unnecessary. Only one A5 outcome
  (flag-free passes, flagged+shim blocks, flagged-raw blocks)
  even begins to justify a build.

### B3. The getter toString tell may be unclosable from any JS layer
- Severity: CRITICAL
- Attack: VERIFIED: current shim getter toString is
  `function () { [native code] }` vs native
  `function webdriver() { [native code] }`; the probe detects
  it (SHIMMED verdict). Frozen coverage demands closing this.
  But a JS-level redefinition (content script, preload, even
  chrome-privileged autoconfig JS) replaces a native getter
  with a JS/Proxy function. A page can detect that without
  toString: cross-realm comparison (a fresh iframe realm has
  the native getter; the patched realm differs), descriptor
  shape, Function.prototype.toString applied via a pristine
  realm, error-stack shapes, Proxy traps observable via
  timing/inspection. Truly native-form requires an engine-level
  change (patching Firefox/Zen source), which is a fork, not a
  2-5 day layer. ASSUMED (by the build proposal): JS can make
  the getter indistinguishable. No spike evidence is offered.
- Evidence that would answer it: a time-boxed spike (1 day)
  proving a JS layer makes the probe CLEAN including a
  cross-iframe/cross-realm read. If the spike cannot beat the
  probe, the build's own frozen coverage is unachievable and
  the branch dies on its own terms.

### B4. document_start still loses races (iframes, workers, early scripts)
- Severity: HIGH
- Attack: VERIFIED: the BiDi preload shim already misses
  documents loaded outside the holder session and pre-existing
  tabs until reload (T7). An extension content script at
  document_start improves coverage but does not guarantee
  first-read wins: a page's earliest inline script, an iframe
  created before injection, or a worker context can read
  webdriver before or outside the patch. Cloudflare's challenge
  script only needs one early read. "Every document" in the
  proposal is an aspiration, not a mechanism guarantee.
- Evidence that would answer it: a race test page that reads
  webdriver in the earliest inline script, in a dynamically
  created iframe, and in a worker, all under the built layer,
  all reading false with native-form getter.

### B5. Autoconfig blast radius: dead browser or silent exposure
- Severity: HIGH
- Attack: Chrome-privileged autoconfig JS runs at startup
  with full privileges. Failure modes after a Zen update:
  (a) startup breakage - browser will not start, owner loses
      the user's browser entirely, recovery needs manual file surgery;
  (b) silent disable - layer stops applying, webdriver=true,
      owner blocked again, and nothing alarms unless someone
      runs the probe (probe runs in drive reports, not on
      human browsing).
  The extension route fails safer but faces release-channel
  signing/sideload constraints in Firefox-family browsers;
  an update can disable an unsigned/policy-loaded extension
  silently (same fail-open). Either way the layer's failure
  mode is worse than the split's failure mode (split fails
  loud: agent cannot attach; human profile unaffected).
- Evidence that would answer it: failure-injection tests:
  break the layer deliberately (syntax error, disabled
  extension) and record startup behaviour + whether a loud
  alarm fires before the owner browses.

### B6. The maintenance owner is a fiction; kill criteria = weeks broken
- Severity: HIGH
- Attack: "Named maintenance owner required" - named whom?
  The team is rotating agents with token limits plus one
  student owner with exams from 30/11. Per-update verification
  forever means a human/agent must run the probe + human-path
  visits after every Zen/Firefox-cadence update and fix
  breakage. When that owner is busy, the layer rots and the
  owner is blocked again - the original problem returns with
  extra complexity on top. Kill criteria "two consecutive
  updates break it" at monthly cadence is potentially 4-8
  weeks of broken browsing before retirement triggers, and
  only if someone is even checking. Without an automated
  startup probe, the kill criteria is unenforceable.
- Evidence that would answer it: a named human owner + named
  backup + automated probe-on-startup with fail-loud banner +
  a per-update checklist that has actually been run once.

### B7. Arms-race asymmetry: frozen defender vs funded adversary
- Severity: HIGH
- Attack: Cloudflare updates detection continuously; frozen
  coverage freezes the defence at build time. Every new tell
  (and B3/B4 show tells are plentiful) demands a new build
  cycle. The build branch commits the team to a permanent
  evasion treadmill. The split branch has no treadmill: a
  flag-free profile is genuinely clean, nothing to evade,
  nothing for Cloudflare to newly detect. Paying forever to
  stay one step behind an adversary, when a no-evasion option
  exists, needs extraordinary justification. None is given.
- Evidence that would answer it: a costed treadmill estimate
  (expected fix cycles per year) accepted explicitly by the
  owner, or proof that webdriver is a stable, sufficient
  signal (A5 + time).

### B8. Build preserves the 24-tab blast radius and the one-session limit
- Severity: HIGH
- Attack: VERIFIED: agent automation once closed 24 owner tabs
  (26/11); VERIFIED: Remote Agent allows ONE WebDriver session
  at a time (T8). The build changes neither. Agents still drive
  the user's live session, still can close the user's tabs, still
  serialize behind one session. The build spends the most
  money to preserve the exact configuration that caused the
  worst incident, while the split removes that blast radius
  for free.
- Evidence that would answer it: none available - this is
  structural. Mitigation would require tab-safety machinery
  priced separately, which the build estimate does not include.

### B9. Stock-app principle: an n=1 fragile layer in a generic repo
- Severity: MEDIUM
- Attack: Standing principle VERIFIED (briefed): repo must work
  on stock apps; machine optimizations only OPTIONAL opt-in
  default off. A Zen-version-fragile hiding layer is the
  opposite of stock-generic. If it lands default-on, stock
  users break. If opt-in, its only user is this one machine -
  full maintenance cost for n=1, and every repo consumer must
  still reason about it. The owner's "build a dedicated tool
  if needed" addendum does not by itself reconcile this; the
  decision must state explicitly that the layer is machine-
  layer opt-in, never repo default.
- Evidence that would answer it: a written placement decision
  (machine layer vs repo, default off) accepted in Stage 2.

---

## 3. Attacks on the acceptance test and the ASSUMED claim

### A1. Probe-clean certifies a list, not Cloudflare-clean
- Severity: HIGH
- Attack: VERIFIED: probe coverage is exactly its listed
  signals (webdriver value/type, descriptor, getter name/
  toString, configurability, documentElement attribute, plugins
  length, fixed globals list). A CLEAN verdict means "these
  signals present as normal", nothing about TLS/IP/behaviour.
  The acceptance bar says probe-clean is necessary not
  sufficient - correct - but then sufficiency rests entirely
  on A2's visit test, which is weak. There is a real risk the
  team treats CLEAN as victory in practice (it is the only
  automated, repeatable signal available).
- Evidence that would answer it: acceptance wording that
  forbids declaring success on probe alone, plus A2/A5 rigor.

### A2. "No block on N visits" cannot distinguish fix from luck
- Severity: CRITICAL
- Attack: Cloudflare challenge rates vary by IP reputation
  decay, time, site config, and cf_clearance cookies. If the
  true block rate is 20%, five clean visits occur ~33% of the
  time by chance. The decision specifies no N, no period, no
  site panel, no cold/warm cookie discipline, and - fatally -
  no flagged control arm run the same day on the same IP to
  prove the test can detect a block at all. Without a control
  arm, a passing test is consistent with "nothing was going to
  block today anyway".
- Evidence that would answer it: a pre-registered test: fixed
  site panel (A6), fixed N per arm, cold profiles per trial
  (A7), flagged-raw control arm interleaved same-day, block
  outcomes recorded separately per arm. Meaningful N: enough
  trials that the control arm blocks at least sometimes while
  the treated arm does not (if control never blocks, the test
  is void, not passed).

### A3. Agent-driven "human-path" visits are not human
- Severity: HIGH
- Attack: The standing user-path rule requires entry via
  search/homepage and clicking through like a normal user.
  But an agent driving via BiDi/Marionette still produces
  robotic timing, no mouse entropy, instant navigation.
  Cloudflare behavioural signals may therefore block agent
  visits a human would pass, or pass agent visits (holder
  shim active) that the user's own later browsing would fail
  (no holder session, VERIFIED shim lifetime = holder session).
  The test confounds driver, shim state, and browser config.
- Evidence that would answer it: separated arms: owner
  browsing (true human, no agent) vs agent-driven, reported
  separately. Only the owner-browsing arm proves leg 1.

### A4. Existing shim evidence undermines BOTH branches' stories
- Severity: HIGH
- Attack: Per the fix review (briefed): "shim proven live and
  probe-clean repeatedly, no bot block" in holder sessions.
  Take it at face value and it implies the webdriver VALUE
  alone (even with the SHIMMED toString tell, VERIFIED) may
  already pass real Cloudflare sites - which makes the build's
  extra toString engineering unnecessary and suggests split +
  existing shim in the agent profile may already suffice for
  agent tasks. Discount it as anecdote (no control arm, warm
  cookies, low-challenge sites) and it proves nothing for
  either branch. Either way it does not support spending
  2-5 days before measuring. Note also: "probe-clean" for a
  shimmed document is loose language - the unified probe calls
  that state SHIMMED, not CLEAN (VERIFIED in probe code).
  Precision matters when the probe is the fail-loud gate.
- Evidence that would answer it: A5, which converts this
  anecdote into a measurement.

### A5. The cheap experiment that tests the ASSUMED claim has not been run
- Severity: CRITICAL
- Attack: ASSUMED (Stage 1): blocks here are driven mainly by
  webdriver. Everything in both branches prices cures for that
  cause. The direct test costs hours with existing machinery
  (throwaway profiles, spare ports, unified probe - all
  VERIFIED working in Stage 1):
  Arms, same machine/IP/day, cold profile per trial:
    (1) flagged, no shim (expect blocks if assumption holds)
    (2) flagged + holder shim (tests shim sufficiency)
    (3) flag-free (tests split leg 1 / build target state)
  Panel: sites with observed blocks in this environment
  (including the 06:33 live-Zen interstitial context) plus
  high-protection Cloudflare sites; human entry path
  (search/homepage, click through); interstitial outcome
  recorded per trial.
  Outcomes decide the fork honestly:
  - (3) also blocks -> webdriver is NOT the main driver;
    both branches fail leg 1; stop and rethink (IP/TLS).
  - (2) passes like (3) -> build unnecessary; keep shim,
    split optional for safety.
  - Only (3) passes -> split justified; build still needs
    B3 spike before any commitment.
  Committing to either branch before this experiment is
  buying the cure before diagnosing the disease.
- Evidence that would answer it: the experiment itself. It is
  the single highest-value next step in this entire decision.

### A6. Site-panel bias can make any test pass vacuously
- Severity: MEDIUM-HIGH
- Attack: "Multiple Cloudflare-protected sites" is unspecified.
  A panel of low-protection sites (Bot Fight Mode off, no
  managed challenge) passes under every config including
  flagged-raw, proving nothing. The panel must include sites
  that demonstrably block in this environment and sites with
  managed challenge / Turnstile, or the acceptance test is a
  rubber stamp.
- Evidence that would answer it: a named panel with per-site
  protection level and observed block history here, frozen
  before testing.

### A7. cf_clearance carryover makes repeated visits non-independent
- Severity: MEDIUM-HIGH
- Attack: A passed challenge sets a cf_clearance cookie
  (typically tens of minutes to hours, bound to IP/UA).
  Repeated visits in the same profile after one pass are one
  trial repeated, not N trials. An acceptance run of "10
  visits, no block" in one warm profile may be a single lucky
  pass echoing. ASSUMED in current acceptance wording:
  visits are independent. They are not, unless cookies are
  cleared / fresh profiles used per trial.
- Evidence that would answer it: cold-profile-per-trial
  discipline, or explicit separate reporting of cold vs warm
  outcomes.

---

## 4. Verdict

### Which branch survives better: the SPLIT branch, conditionally

The build branch fails on physics and economics: its frozen
coverage may be unachievable from any JS layer (B3), it races
early reads (B4), its failure mode is a dead browser or silent
exposure (B5), it preserves the worst blast radius (B8), and it
commits to a permanent arms race (B7) - all to cure a cause
that is still ASSUMED (B2/A5). Its core defects are not fixable
by policy; they are properties of the mechanism.

The split branch's core defects are decision and policy
defects: an unapproved reinterpretation (S1), an unpriced
continuity loss (S2), unproven concurrency (S3), rot and
credential policy (S4/S5). Those are fixable by explicit owner
decision, a live test, and written policy - cheap, reversible,
and honest. A flag-free human profile is genuinely clean with
no evasion treadmill. That asymmetry decides it.

Boundary-restart (Alternative 2) remains dominated: it inherits
the build's flagged-during-agent-work failure plus restart/
restore risk on every call. Agree with Stage 1: recommend
against. No further attack needed.

### Amendments that make the SPLIT branch viable (required, not optional)

1. Owner decision on the fork, recorded verbatim: same-install
   accepted, with the continuity loss stated plainly (agents
   cannot act in the user's live tabs/logins by default). If the user says
   same-session, the split is dead and Stage 2 must say so.
2. Run A5 BEFORE migration. If flag-free still blocks, stop:
   neither branch delivers leg 1.
3. Headed concurrency live test (S3) as a gate: both profiles
   open, agent drives, human browses, pill/routing/RAM verified.
4. Continuity escape hatch, explicit and logged, never silent:
   for owner-account tasks, a deliberate flagged session on the
   human profile with tabs recorded before, probe in the drive
   report, restore after - or a separately logged-in agent
   profile task. Pick one, write it down, forbid silent (c).
5. Parity mechanism + drift check (S4) and credential policy
   for the agent profile (S5), each with a named owner.
6. Launch-path audit + startup probe gate on the human profile
   (S6): every entry point flag-free, webdriver=true fails loud.
7. Acceptance per A2/A6/A7: pre-registered panel, cold trials,
   flagged control arm, owner-browsing arm reported separately.

### Amendments that would make the BUILD branch viable (losing branch)

Only consider building if ALL of these hold, in order:
1. A5 proves: flag-free passes, flagged-raw blocks, flagged+shim
   blocks (i.e. the toString tell or shim gaps actually matter
   on real blocking sites). Any other A5 outcome kills the build.
2. A 1-day spike proves the getter can be made probe-CLEAN
   including cross-realm/iframe reads (B3) and wins the race
   test (B4). Spike failure = build dead, fall back to split.
3. Extension route preferred over autoconfig (fail-safe over
   fail-dead, B5), with signing/sideload proven across a Zen
   update before commitment.
4. Automated startup probe with fail-loud banner; named human
   owner + backup; per-update checklist run once for real (B6).
5. Kill criteria tightened: ONE broken update or 7 days broken
   retires the layer to the split automatically. "Two
   consecutive updates" is weeks of owner pain (B6).
6. Placement written down: machine-layer opt-in, default off,
   never repo default (B9); tab-safety priced separately (B8).

If those gates cannot be met, the build branch is not viable
and should not be commissioned on hope.

### Bottom line

Do not choose between split and build today. Run A5 (hours),
get the user's fork decision in the user's own words (S1), and run
the S3 concurrency gate. Those three cheap facts collapse most
of this uncertainty. On current evidence the split survives;
the build is an expensive bet on an unmeasured assumption with
an possibly unclosable tell.

---

Evidence labels summary:
- VERIFIED (per Stage 1 / briefed facts): each flag alone forces
  webdriver=true; pref route dead; shim lifetime = holder
  session; probe coverage limits; shim toString tell; one
  WebDriver session limit; 0/55 continuity count and its
  fresh-page caveat; 24-tab incident 26/11; live-Zen
  Cloudflare interstitial 06:33 27/11; dedicated-profile
  machinery exists (zen_cli.py).
- ASSUMED (flagged wherever load-bearing above): blocks driven
  mainly by webdriver; owner accepts same-install reading;
  JS layer can close the toString tell; repeated visits are
  independent trials; future work resembles the frozen 55.
