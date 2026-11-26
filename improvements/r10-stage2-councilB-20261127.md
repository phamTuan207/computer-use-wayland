# R10 Stage 2 - Council Member B Position (owner intent and real usage)

Date: 27/11/2026
Lens: Council B - interpret the owner criterion as the owner most plausibly meant it, given how he actually uses this machine.
AI-to-AI communication in English. Independent position, not coordinated with any other agent.

## Recommendation in one paragraph

Adopt a staged hybrid. Adopt the two-profile split immediately as an interim unblock for the human browsing leg, and in parallel commission the dedicated hiding layer build (spike first, then full build if the spike passes), because only the build satisfies the criterion as the owner most plausibly meant it. Do not close R10 on the split alone. Presenting the split as final satisfaction would be a silent downgrade of the criterion from "same live session" to "same install" without the owner agreeing to that downgrade.

## 1. Reading of "the same Zen" and recommendation

### 1.1 Reading: "the same Zen" means the same live session

My reading is (ii) same live session: agents act in the owner's own tabs and logins at any time while his browsing stays clean. Reasoning summary, expanded in section 2:

- VERIFIED (per brief): the standing acceptance test says "agent drive on the same Zen session with the pill visible". The word "session" is already in the team's own acceptance language. Reading the criterion as "same install" contradicts that test.
- VERIFIED (per brief): in the owner's lived experience agents drive his Zen, his tabs, his logged-in session. Examples in the record include restoring his tabs, checking his screenshots, and task 56. The machine's whole purpose is agents driving his real desktop.
- VERIFIED (per brief): the owner said "agents callable to computer-use Zen at any time". "Callable at any time" most naturally means callable into the Zen he is actually using, not callable into a second profile he must separately log into and maintain.
- VERIFIED (per brief): the owner addendum is "build a dedicated tool if needed". An owner who meant "same install is fine" would not need that addendum, because the split needs no dedicated tool. The addendum only makes sense if the bar includes something the split cannot deliver.

### 1.2 Recommendation: hybrid with explicit triggers

1. Interim (now): two-profile split. Human profile flag-free, agent profile flagged. This restores clean human browsing today and keeps agents callable in an isolated profile. Label it interim in every report. Do not mark the criterion satisfied.
2. End state (commissioned): dedicated hiding layer in the flagged browser, normalizing page-visible automation signals in every document, so one live session serves both the human and the agents. Start with a time-boxed spike against the frozen coverage, then proceed to full build only if the spike passes probe plus live Cloudflare human-path tests.
3. Cancellation triggers for the build (any one cancels or pauses it, see section 4.3): the owner explicitly accepts the same-install reading; the spike shows Cloudflare still blocks despite a clean probe; logged real-world asks over a defined window show zero same-session need; or maintenance capacity cannot be staffed with a named owner.

This hybrid satisfies the criterion only as a staged path to the same-session end state. It violates the criterion if the split is declared final. The distinction must be visible to the owner: interim status, not closure.

## 2. Reasoning tied to the evidence

### 2.1 What the 0/55 count does and does not prove

- VERIFIED: 0 of 55 frozen R3-L3 tasks needed owner-session continuity. The only continuity-dependent task was R3-056, an owner-added incident-repair task (restore his own tabs). R3-029 used a task-scoped test account.
- VERIFIED caveat (per brief): the frozen list was designed around fresh pages. Tasks of the form "do X in my account / my tabs" are not represented.
- ASSUMED: the owner's real future asks include same-account tasks at meaningful frequency. His life includes Gmail confirmations, Codeforces under his manager nick, his calendar, and his Drive. These are exactly the "do X in my account" shape the frozen list excludes.
- Conclusion: 0/55 measures the test list design, not the owner's real demand. Using it to justify a split-only end state would be a measurement error: concluding no need exists because the instrument never looked for it.

### 2.2 The cost of being wrong, each way

If we adopt split-only and the owner meant same session (wrong in the split direction):
- ASSUMED: the owner discovers the loss at the worst moment, mid-task, when an agent cannot act in his logged-in tabs. The failure reads as "you changed what I asked for", not as a technical limit.
- VERIFIED pattern: agents have historically been asked to work in his live session. Removing that capability removes a proven use, not a hypothetical one.
- The rework cost is not just the build later. It is trust cost plus re-login friction in the agent profile for every account task in the meantime, plus credential spread into a second profile if agents log in as him there.

If we build and the owner meant same install (wrong in the build direction):
- VERIFIED estimate (Stage 1): 2-5 days research plus build plus test, verification after every Zen update, named maintenance owner required.
- VERIFIED limit: the unified probe certifies only its listed signals, not TLS, IP, or behaviour. Cloudflare may still defeat the layer via out-of-scope signals.
- ASSUMED: per-update verification burden is real and recurring. Without a named owner it decays silently, which is worse than not building, because a silently broken hiding layer gives false confidence.

Asymmetry judgment: the split-direction error breaks a capability the owner demonstrably uses and contradicts his own acceptance test wording. The build-direction error wastes bounded engineering time and can be stopped by kill criteria. Bounded waste is recoverable. A silently downgraded criterion is not, because nobody re-opens a "closed" item until it fails in use. This asymmetry favours building, with kill criteria to cap the waste.

### 2.3 The safety win of the split is real but does not decide the fork

- VERIFIED: agent automation once closed 24 of the owner's tabs including 5 essentials and 3 pinned (26/11), creating a repair task. The owner is a heavy Zen user (essentials, folders, pinned tabs, workspaces).
- VERIFIED (Stage 1 pricing): the split keeps owner credentials out of the automation blast radius. That is a genuine safety win.
- Counterweight: the safety win argues for isolation as a default operating mode, not for abandoning same-session capability entirely. The hybrid keeps isolation as the interim default while building the layer that makes same-session work safe enough to offer. Tab-safety discipline (snapshot before any owner-session attach, never close owner tabs) remains required in both end states, because incident-repair tasks like R3-056 will still exist.

### 2.4 Fit with the standing design principle

- VERIFIED principle: his machine is AI-optimized but the repo must work on stock apps; machine optimizations go in the repo only as optional (opt-in, default off).
- The split fits the principle trivially (profiles are stock). The hiding layer also fits if delivered as a machine-local optional layer with repo presence opt-in and default off. The principle therefore does not rule out the build. It only constrains how the build is packaged.

### 2.5 Why not boundary-restart

- VERIFIED (Stage 1 pricing): boundary-restart is dominated. Leg 1 fails during agent sessions, two restarts per call, restore risk. I concur: recommend against. It satisfies neither reading well and adds restore risk to a heavy tab user's session.

## 3. What would change my mind

Any one of these would move me to split-only as the end state:

1. The owner, asked plainly with both readings stated, confirms "same install" suffices and same-session agent work is not required. His word settles intent; my inference yields to it.
2. Logged evidence over a defined window (propose 30 days of real asks, logged in the master event log) shows zero same-session tasks and zero re-login friction in the agent profile. Real demand data would replace the frozen-list proxy.
3. The build spike fails: the probe is clean on frozen coverage but Cloudflare still blocks on the owner's real sites via out-of-scope signals. Then the build cannot deliver its promise and should be killed, with the split promoted to end state and the criterion renegotiated with the owner.
4. No named maintenance owner can be staffed for per-update verification. An unmaintained hiding layer is worse than an honest split.
5. A security review finds the hiding layer cannot be packaged as opt-in default-off without breaking stock-app behaviour. That would violate the standing principle.

What would not change my mind: another recount of the frozen 55 tasks. The list design caveat means recounting it adds no information about real demand.

## 4. Plan specifics

### 4.1 Interim split adoption (immediate)

Profile setup:
- Human profile: the owner's existing Zen profile, launched flag-free (plain zen, not the zen-ai launcher). VERIFIED: flag-free profile reads webdriver false and browses clean.
- Agent profile: dedicated profile via the existing dedicated-session machinery in zen_cli.py. VERIFIED: that machinery already implements dedicated-profile sessions. Launched flagged (BiDi 9222 plus Marionette 2828) so both attach lanes survive.

Which profile agents attach to:
- Default: agent profile only. Agents do not attach to the owner's live session in normal operation during the interim.
- Exception: explicit owner order for incident repair in his own session (R3-056 shape). Requires a tab and session snapshot before attach, and the standing rule that agents never close owner-opened tabs or windows.

Human-leg verification:
- Owner opens Zen normally (flag-free human profile), searches and browses the Cloudflare-fronted sites he actually uses, via the normal human path (search or homepage, click through). Pass means no "Just a moment..." interstitial and webdriver false on probe read.
- Repeat after every Zen update. The human profile should stay clean flag-free; any regression is a stop-and-report event.

Interim residue handling:
- Keep the current residue in the agent profile until the build lands: pinned shim hash, probe result in every drive report, dirty probe equals stop. VERIFIED: the shim getter toString (`function () { [native code] }`) differs from native (`function webdriver() { [native code] }`) and is a detectable tell, so the residue is a known-imperfect interim, not a solution. Do not remove it early; a flagged profile with no shim is strictly worse.
- Agent profile holds no owner credentials. Task-scoped accounts only (R3-029 pattern). Any login as the owner in the agent profile requires explicit owner approval per task.

Reporting discipline:
- Every status report labels the split "interim, criterion not yet satisfied". R10 stays open until the build passes acceptance or the owner accepts the same-install reading.

### 4.2 Build commission (parallel track)

Form: extension content script at document_start or chrome-privileged autoconfig JS, normalizing page-visible automation signals in every document of the flagged browser. Machine-local layer; repo presence opt-in, default off.

Frozen coverage (minimum, from Stage 1 proposal plus probe parity):
- navigator.webdriver value false, correct type.
- Getter toString in native form: `function webdriver() { [native code] }`.
- Descriptor location and configurability matching native.
- No documentElement automation attribute.
- Automation-globals list (as enumerated in the unified probe) clean.
- Plugins length plausible per probe expectation.
- Coverage must hold for documents inside and outside a BiDi holder session (the Stage 1 probe disagreement root cause), so Marionette reads and page reads agree.

Maintenance owner:
- One named owner, not "the team". Owns re-verification after every Zen update (probe run plus live Cloudflare human-path check) and owns breakage response. If the named owner cannot be staffed, do not start the full build (see kill criteria).

Cost estimate:
- VERIFIED (Stage 1): 2-5 days research plus build plus test.
- ASSUMED: 0.5-1 day per major Zen update for re-verification until automated, then spot checks. Budget this explicitly or the layer decays.

Acceptance (all in one live flagged session, no relaunch):
- Human browses and searches normally in the flagged session with no Cloudflare block on his real sites.
- Agent drive on the same Zen session with the pill visible (standing acceptance test), acting in the owner's tabs.
- Unified probe clean in every tested document.

### 4.3 Triggers and kill criteria

Proceed from spike to full build only if: spike passes frozen-coverage probe in holder and non-holder reads AND passes live Cloudflare human-path tests on the owner's real sites in the flagged profile.

Kill or pause the build if any of these fire:
- Spike probe-clean but Cloudflare still blocks (out-of-scope signals dominate). Kill, promote split, renegotiate criterion with owner.
- Per-update breakage exceeds the named owner's capacity twice in a row. Pause and re-decide.
- Owner accepts same-install reading at any point. Kill immediately; split becomes end state.
- 30-day real-ask log shows zero same-session need. Pause; re-decide with data.
- Packaging cannot stay opt-in default-off on stock apps. Kill or re-scope.

## 5. Residual risks of my recommendation

- ASSUMED risk: the build may pass the probe yet fail against Cloudflare behaviour or TLS signals in ways the probe cannot certify. The spike gate exists to surface this before full investment.
- ASSUMED risk: running split interim plus build in parallel splits team attention. Mitigation: the split is low cost with proven components (VERIFIED, Stage 1), so parallel cost is mostly the build itself.
- VERIFIED risk carried from history: any return to same-session agent work re-opens the tab-destruction blast radius seen on 26/11. The snapshot-before-attach and never-close-owner-tabs rules are mandatory in the end state, not optional.

## Claim labels index

VERIFIED claims above rest on the Stage 1 investigation facts, the owner criterion as fixed 06:20-06:21 27/11, the standing acceptance test wording, and the recorded 26/11 tab incident, all as supplied in the Stage 2 brief. ASSUMED claims are my inferences about future real-world demand frequency, owner reaction to a downgraded criterion, and recurring maintenance effort. Each is labelled inline where it appears.
