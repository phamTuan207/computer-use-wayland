# R10 Stage 2 - Council A Position (Evidence and Cost)

Date: 2026-11-27
Seat: Council Member A - evidence and cost lens
Decision: Cloudflare / navigator.webdriver in Zen

## 1. Recommendation

**Adopt the two-profile split in one Zen install. Do not commission the dedicated hiding-layer build now.**

Reading of the fork: "the same Zen" is satisfied by the same install with two profiles, not by the same live session. The same-live-session reading is not supported by the measured task evidence and it is the only reading that forces the expensive build. If the owner later rules that same-live-session control is mandatory, that ruling, not new technical evidence, is what reopens the build. See Section 3.

Boundary-restart (Alternative 2) is rejected as dominated. See Section 2.5.

## 2. Reasoning tied to the evidence

### 2.1 The root cause is structural, and the cheap exits are already closed

- VERIFIED: Each flag alone forces `navigator.webdriver = true` in throwaway headless profiles: BiDi-only true, Marionette-only true, no flags false. Removing a flag loses that agent attach lane. No runtime toggle exists; conditioning means relaunch.
- VERIFIED: The pref route is dead. `dom.webdriver.enabled=false` changes nothing page-visible under either flag or both.
- VERIFIED: The probe disagreement is explained. The shim is a BiDi preload script that only applies to documents loaded inside the holder session; a Marionette read outside a holder session reads native true. A unified probe exists at `improvements/r10-webdriver-probe.mjs`.
- Consequence: There is no flag combination that gives one live session both a clean human leg and both agent lanes. The choice is genuinely between separation (split), restart boundaries, or a hiding layer. This is a fork in architecture, not a tuning problem.

### 2.2 Continuity evidence does not justify same-live-session control

- VERIFIED: 0 of 55 frozen R3-L3 tasks needed owner-session continuity (his logged-in accounts as himself, his existing tabs/session). The only continuity-dependent task was R3-056, an owner-added incident-repair task to restore his own tabs. R3-029 used a task-scoped test account.
- VERIFIED caveat: The frozen list was designed around fresh pages; tasks of the form "do X in my account / my tabs" are not represented.
- ASSUMED: Future owner requests will include some account-bound work (for example, act in a logged-in service as the owner). The caveat means 0/55 cannot be read as "continuity will never be needed." It can be read as "continuity was not needed for the measured workload, and no measured workload currently requires paying the build cost."
- Cost reading: A requirement with zero observed instances in the only measured workload does not justify a 2-5 day build plus per-update verification. Ponytail principle applies: smallest complete change first, reuse before writing, no unrequested abstraction. The build is an abstraction for a hypothetical task class. The split serves the observed task class today and leaves the build available if the hypothetical becomes real.

### 2.3 The split reuses proven components; the build creates new ones

- VERIFIED: The human profile flag-free case is verified clean (no flags: false). The agent profile flagged case uses existing dedicated-session machinery; `zen_cli.py` already implements dedicated-profile sessions.
- VERIFIED: Stage 1 priced the split as low cost with components proven, satisfying legs 1-3 if "the same Zen" means same install.
- VERIFIED: Stage 1 priced the build as highest cost: 2-5 days research plus build plus test, verification after every Zen update, named maintenance owner required. Proposed frozen coverage is webdriver value plus native-form getter toString only.
- ASSUMED: Zen updates will continue at a cadence that makes per-update verification a recurring tax, not a one-time cost. The owner runs Zen 1.24.3b on an AI-optimized laptop; update cadence is outside team control.
- Ponytail reading: The split is the smallest complete change that meets the criterion under the same-install reading. It reuses the dedicated-session machinery instead of writing a new hiding layer, adds no new dependency, and keeps the repo working on stock apps with machine optimization as opt-in only, per the standing design principle.

### 2.4 The build does not guarantee the outcome it is bought for

- VERIFIED: The unified probe certifies only its listed signals (webdriver value/type, descriptor location, getter name, getter toString native vs Proxy form, configurability, documentElement attribute, plugins length, fixed automation-globals list). It does not certify TLS, IP, or behaviour.
- VERIFIED: The current shim has a detectable tell: getter toString is `function () { [native code] }` vs native `function webdriver() { [native code] }`.
- ASSUMED: Cloudflare may use signals outside the frozen coverage, including TLS fingerprint and behavioural signals that a document_start content script or autoconfig JS cannot fix. This is stated in the Stage 1 brief as out of scope and unfixable here.
- Consequence: Paying 2-5 days plus maintenance buys a clean probe on frozen coverage, not a guaranteed clean Cloudflare outcome. If blocks persist with a clean probe, the honest report is "frozen coverage passed, block persists, no scope expansion." That is a real possible end state: cost paid, criterion still unmet on the human leg if the human leg shares the flagged session. The split does not have this failure mode on the human leg, because the human profile is flag-free by construction and verified clean on the webdriver signal.

### 2.5 Boundary-restart is dominated and should not be adopted

- VERIFIED: Stage 1 priced boundary-restart as dominated: leg 1 fails during agent sessions, two restarts per call, restore risk.
- Reasoning: It pays restart cost and restore risk on every agent call, breaks the human leg precisely while agents work, and still requires session restore to be perfect. The split gives the human leg continuous cleanliness with zero restarts. There is no cost or evidence argument for boundary-restart over the split.

### 2.6 Safety blast radius favours the split

- VERIFIED: Under the split, agents attach to the agent profile; owner credentials in the human profile are outside the automation blast radius. Stage 1 lists this as a safety win.
- VERIFIED: R3-056 exists because owner tabs were lost in an incident-repair context. Tab/session incidents in the owner session have already occurred in this project.
- ASSUMED: An agent error in the agent profile (wrong tab closed, wrong page navigated, profile state corrupted) has lower blast radius than the same error in the owner profile, because the owner session, logins, and tabs are not in scope.
- Cost reading: The build keeps agents inside the owner session, so every agent incident is an owner-session incident. The split converts a class of owner-session incidents into agent-profile incidents, which are cheaper to recover from (recreate profile, re-login task account) than restoring owner tabs and logins.

### 2.7 "Build if needed" - need is not proven

- VERIFIED: The owner addendum is "build a dedicated tool if needed."
- Reading: "If needed" is conditional. Need would be proven by either (a) an owner ruling that same-live-session control is mandatory, or (b) observed tasks that cannot be served by the split. Neither is in evidence today. The measured workload (0/55) points the other way.
- ASSUMED: If the owner intended same-live-session as mandatory, he would have said so when fixing the criterion at 06:20-06:21 on 27/11. The criterion as fixed says "agents callable to computer-use Zen at any time; Zen stays AI-optimized." It does not say "in my tabs" or "in my logins." The same-install reading satisfies the criterion as written.

### 2.8 Losses of the split, stated plainly

- VERIFIED: Agents cannot act inside the owner's live tabs/logins without a separate login in the agent profile.
- VERIFIED: Two profiles must be maintained.
- Mitigation, not denial: Account-bound tasks use a task-scoped login in the agent profile (as R3-029 already did). Owner-tab tasks remain human-only or are handled by explicit owner handoff (owner opens the page in the agent profile, or owner performs the step). If such tasks become frequent, that frequency is the evidence that reopens the build. See Section 3.

## 3. What would change my mind

I would switch from split to build if any one of these becomes true:

1. **Owner ruling on the fork.** The owner rules that "the same Zen" means same live session (agents act in his own tabs/logins at any time while his browsing stays clean). This is a criterion ruling, not a technical finding. Under that ruling the split fails by definition and the build is the only route that satisfies all three legs literally.
2. **Observed continuity demand.** A measured run of real owner tasks shows recurring tasks that require owner-session continuity and cannot be served by a task-scoped login in the agent profile. Threshold I would use: 3 or more such tasks in a single measured batch, or any single task where a separate login is impossible (for example, hardware-bound or session-bound state that cannot be recreated). One anecdote is not enough; a pattern is.
3. **Split fails its own verification.** The human-leg verification in Section 4.3 fails: the flag-free human profile still hits Cloudflare interstitials on normal browsing, or the agent profile cannot be driven reliably through existing dedicated-session machinery. A split that does not deliver a clean human leg has no cost advantage to defend.
4. **Build cost collapses.** A proven, maintained, upstream or community hiding layer appears that covers the frozen signals with per-update verification already handled by its maintainer, reducing team cost from 2-5 days plus ownership to adoption plus verification only. Ponytail favours reuse; a reusable component changes the cost equation.
5. **Maintenance owner volunteers and is named.** Even under items 1-2, the build should not start without a named maintenance owner who accepts per-update verification. Without an owner, the build decays silently after the next Zen update and the team is back to dirty-probe stops with no one accountable.

What would NOT change my mind: a single blocked page in the agent profile (expected under flags; the agent leg is not required to be Cloudflare-clean for the owner), or a clean probe in the flagged session (probe cleanliness does not prove Cloudflare cleanliness, per Section 2.4).

## 4. Adoption plan for the two-profile split

### 4.1 Profile setup

- VERIFIED basis: One Zen install, two profiles. Human profile launched flag-free (no `--remote-debugging-port`, no `--marionette`). Agent profile launched flagged via existing dedicated-session machinery (`zen_cli.py` dedicated-profile sessions).
- ASSUMED implementation detail: The current launcher `~/.local/bin/zen-ai` execs `zen-bin --remote-debugging-port=9222 --marionette` against the default profile. Under the split, the human entry point must not use that launcher. Concretely:
  - Human entry: a flag-free launch (desktop entry / plain `zen-bin` with the human profile) for all owner browsing. No debugging port, no Marionette.
  - Agent entry: the existing `zen-ai` path retargeted to the agent profile via the dedicated-session machinery, keeping BiDi on 9222 and Marionette on 2828 for that profile only.
  - The two profiles must not share a profile directory. Separate profile directories, separate session restore state.
- Repo principle: The split is a machine-local opt-in configuration. The repo must keep working on stock apps; nothing in the split becomes a default-on repo requirement.

### 4.2 Which profile agents attach to

- Agents attach only to the agent profile, via BiDi (9222) and Marionette (2828) on the flagged launch.
- Agents never attach to the human profile. There is no attach lane to the human profile by design; that is the point of the split.
- Account-bound agent tasks log in inside the agent profile with task-scoped accounts (precedent: R3-029). Owner credentials are not copied into the agent profile as a standing practice; any exception is per-task, explicit, and logged.
- Owner-tab tasks (the R3-056 class) are not agent tasks under the split. They are owner-performed or owner-assisted handoffs. If the owner wants an agent to act on content currently in a human tab, the owner opens that content in the agent profile or the agent opens a fresh copy; the agent does not reach into the human session.

### 4.3 Human-leg verification

Verification follows the normal-user rule: enter the way a user enters, evidence shows entry, path, action, and resulting state.

- Step 1 - Signal check: In the human profile, run the unified probe (`improvements/r10-webdriver-probe.mjs` signals) and confirm `navigator.webdriver` is false with native-form getter. VERIFIED expectation from Stage 1: no flags yields false.
- Step 2 - User-path check: From the human profile, browse and search normally (homepage entry, visible UI navigation, no deep-link shortcuts) across a small set of Cloudflare-fronted sites including at least one that previously showed the "Just a moment..." interstitial in the owner's live Zen. Evidence must show entry, navigation, action, and resulting state (page loaded without interstitial), not only the final screen.
- Step 3 - Agent-leg check: Confirm agents can still attach to the agent profile via both lanes (BiDi 9222, Marionette 2828) and complete a representative drive task with a probe result in the report.
- Step 4 - Update check: After the next Zen update, repeat Step 1 and a shortened Step 2. The split has no hiding layer to re-verify, so this is a confirmation, not a rebuild. ASSUMED: flag-free behaviour is stable across updates because it is the stock behaviour; the check exists to catch a regression, not because one is expected.
- Failure handling: If Step 1 or Step 2 fails, the split has failed its own criterion. Report honestly, do not expand scope silently, and reopen Stage 2 with the failure as new evidence (see Section 3, item 3).

### 4.4 Interim residue handling

- VERIFIED current residue: pinned shim hash, probe result in every drive report, dirty probe = stop. The shim's getter toString tell is known.
- Under the split:
  - Human profile: shim not needed and not installed. No preload script, no pinned hash to maintain on the human leg. The human leg is clean by construction, not by masking.
  - Agent profile: keep the interim residue as-is for now (pinned shim hash, probe result in every drive report, dirty probe = stop). The agent leg remains flagged and may still hit Cloudflare blocks on some sites; that is acceptable for agent tasks that do not require Cloudflare-fronted pages, and for tasks that do, the dirty-probe stop rule prevents silent false success. Do not invest in improving the shim's toString tell under the split; that work only pays off under the build, which is not commissioned.
  - Drive reports continue to carry the probe result so that any future build decision has a continuous evidence trail.

### 4.5 Maintenance and ownership under the split

- Maintenance burden: keep two profile directories, keep the human entry point flag-free, keep the agent entry point on the dedicated-session machinery. No per-update hiding-layer verification.
- Owner of the split configuration: the coordinator (machine-local config), not a new named build owner. This is deliberately lighter than the build's required named maintenance owner.
- Kill criteria for the split itself: if the human leg cannot be kept flag-free in practice (for example, the owner must use the flagged launcher for daily browsing), or if agent attach to the dedicated profile proves unreliable in the Step 3 check, the split is not delivering and Stage 2 reopens.

## 5. Summary of the evidence/cost balance

| Factor | Split | Build |
|---|---|---|
| Human leg clean | VERIFIED by construction (no flags: false) | ASSUMED via masking; probe-clean does not guarantee Cloudflare-clean |
| Agent lanes | VERIFIED via existing dedicated-session machinery | VERIFIED flags retained, plus new layer to maintain |
| Same-live-session control | No (by design) | Yes (only route) |
| Measured demand for same-session | 0/55 VERIFIED, with stated caveat | Same evidence; build pays for unmeasured demand |
| Build cost | Low, components proven VERIFIED | 2-5 days plus per-update verification VERIFIED |
| Maintenance owner | Coordinator, light | Named owner required VERIFIED |
| Blast radius | Owner credentials outside automation scope VERIFIED | Owner session inside automation scope |
| Success guarantee | Human leg does not depend on masking | Not guaranteed; TLS/behaviour out of scope |

On evidence and cost, the split wins unless the owner rules same-live-session mandatory or measured continuity demand appears. That is the position of Council A.
