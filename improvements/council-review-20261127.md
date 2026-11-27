# Council review: R10 seamless-control (route 3c, RDP-primary) landing readiness (27/11/2026)

Reviewer: council (independent, not the builder). Scope: paper + code review only.
No laptop access, no owner-Zen contact. Evidence judged, not effort.

Sources read in full: decision doc
(`r3l3-run-wt/improvements/r10-seamless-decision-20261127.md`), L1-L6 reports
(`r10-landing-l1/` .. `r10-landing-l6/`), landed code
(`r3l3-run-wt/scripts/zen-rdp/rdp_client.py`, `rdp_smoke.py`, `README.md`).
Spot-checked load-bearing evidence files: L6 `smoke-real.json` (overall PASS),
`step2-panel.json`, `control.json`, `speed.json`, `steps.json`, `restore.json`;
L4 `logs/smoke-pass.json` + `rdp-port-registry.json`; L5
`logs/eval-loop-summary.json`; L2 eval-loop JSONL line counts (339 lines).
Unit tests re-run by this reviewer: `python3 -m unittest test_scope_unittest
test_rdp_smoke` in `scripts/zen-rdp/` = **17/17 PASS** (matches L5 claim).

## Verdict

**LANDING-READY WITH CONDITIONS** (8 conditions in Q5). The evidence supports
switching the operating configuration to the RDP lane on the owner's flag-free
session, provided the conditions below are applied at switch time. It does not
support an unconditional switch, and it does not require P2 to pass cleanly first.

---

## Q1. Does RT-21 PARTIAL PASS satisfy the decision doc's acceptance bar?

**Yes, on the bar as written. PARTIAL is enough to land; a clean P2 is not required.**

The decision doc's step 2 requires: at least 3 queries (target 5), SERPs load,
click-through to P1/P2/P5/C1, no unusual-traffic wall, **panel outcomes recorded
per arm**, cold repeats across different hours. It never requires a 100% panel
pass. It explicitly frames the panel as probabilistic (W4 throwaway: "P1 1/2";
redteam: no "never blocked" claim), and step 5 defines the honest-label rule
(partial is recorded, not silently passed). Kill criterion 6 is **Google-entry
failure**, not any single landing challenge.

L6 (real profile, `report-l6-rt21.md`, `step2-panel.json`, `control.json`):
Google entry **5/5 SERPs PASS** under the exact RDP pref set with the agent
attached; landings P1/P5/C1/Q5 PASS, **P2 coolors CHALLENGE-CF** (Cloudflare
"Just a moment..."). Flagged-raw control arm challenged on **both** P1 and P2,
so the void rule is satisfied and the panel stands. Outcomes are recorded per
arm, no "never blocked" claim is made anywhere in L6. Kill criterion 6 did
**not** fire. On this panel the RDP lane (1 challenge in 5) is strictly better
than the flagged baseline (2 in 2), and the speed leg (step 9, `speed.json`)
shows the flagged baseline failing Google outright (`google.com/sorry`) while
the RDP lane completed.

Two honest caveats, neither blocking:
- **Cold repeats across different hours were not done.** L6 ran in one window
  (14:36-15:11 +07). The doc asks for them; W4 + L6 together give two sessions
  on the same day, not different hours. This is a monitoring debt, not a
  landing blocker, because the kill criterion (Google entry) passed 5/5 cold
  in the real-profile run. Condition C6 below closes it post-landing.
- **Step 8 is PROCEDURE-READY, not DONE.** By construction it cannot be done
  before the next Zen update. The doc's step 8 is a post-update drill; landing
  with a proven-ready procedure (smoke PASS on the real-profile instance,
  step 7) is the only possible pre-landing state. Condition C5 makes the first
  real update a supervised drill.

Requiring P2 to pass cleanly first would impose a stricter bar than the doc
sets, on a site (coolors) that also challenged in W4 throwaway evidence and
challenges the flagged control. The correct landing posture is: land, keep the
probabilistic-panel language, and keep the OS lane / split fallback for
Cloudflare-gated sites. Steps 1, 3, 4, 5, 6, 7 PASS on the real profile and
step 9 DONE (8x/13x on DOM tasks, `speed.json`) complete the picture.

## Q2. Are the residual risks acceptable for landing?

**Yes, with the operational fences in Q5. None is a silent-corruption risk;
each fails loud or is fenced by procedure.**

1. **Positional tab-id scope (exact only within a held session).** L6 found
   descriptor ids are positional and shift on tab insertion, contradicting
   L3's "stable across connections" observation; L6's harness attached to the
   wrong tab twice (read-only probe only; the scoped client correctly
   REFUSED once; no owner tab was written). The landed client mitigates:
   canonical-id strip (`rdp_client.py:91-101`), pinned re-attach by canonical
   id with exact-URL fallback and **refusal** of selected-tab fallback
   (`rdp_client.py:431-454`), URL-pattern scope as the robust form
   (`Scope.matches`, `rdp_client.py:119-126`). Residual risk is real but
   bounded: within a held session with a fresh `listTabs`, ids are exact;
   across sessions they are not. **Fence: URL-pattern scope is mandatory for
   owner-session drives; tab-id scope only inside a held session (C3).**
2. **DevTools-close re-attach retry: unit-proven, live-unfired.** The retry
   (catch `noSuchActor`, re-attach pinned, retry once) is in
   `rdp_client.py:480-488` (evaluate) and `:547-555` (navigate), with the
   retry counter in the drive report (`:661`). Four unit tests cover it
   (re-verified 17/17 PASS by this reviewer). Live: L2 observed exactly one
   `noSuchActor` in 321 evaluates (on a close+tab-switch transition); L5's
   single permitted DevTools cycle fired zero swaps (60 evals, retries 0);
   L6 step 6 fired zero (31/31). So the live firing remains UNTESTED. The
   failure mode is safe: worst case is a raised `RDPError` after one retry,
   never a wrong-tab write (pinned, refuses fallback). Acceptable to land;
   first live firing must be logged and reported (C6).
3. **RT-02 isTrusted suite still open (only one trusted click proven).**
   L6 step 3 proves one OS-lane click with `isTrusted=true` at page level;
   upload picker, clipboard, drag, Turnstile-gated forms are unproven. But
   the OS lane is the pre-existing computer-use lane, not new code, and the
   landing claim does not include those actions. **Fence: seamless claim
   covers DOM read/write/navigate + single trusted click + screenshot;
   anything needing richer trusted input stays on the split/OS lane until
   the RT-02 suite passes (C7).** Kill criterion 5 (focus-safety) is not
   triggered: L2 test 2 and L6 step 6 both show zero keystroke loss and no
   focus theft.
4. **RT-23 multi-agent session locking undesigned.** Two scoped clients can
   attach concurrently; the registry's single `selected=true` channel does
   not prevent two drivers. This is an operational risk, not a code defect.
   **Fence: single-driver rule for the owner session until RT-23 is
   designed; concurrent drives go to the split profile (C4).**
5. **Step 8 unproven until a real Zen update.** Covered in Q1. The smoke
   exists, passes on the real-profile instance, and fails loud with distinct
   exit codes (`rdp_smoke.py:44-45`). Landing is probationary until the
   first update drill passes (C5).

## Q3. Is the security posture complete?

**Substantially yes. No gap blocks landing, provided C2/C3 are applied.
Two defaults must be flipped at switch time; they are safe as-shipped for
throwaway use but not for the owner session.**

- **RT-04 silent attach:** owner-accepted 14:00 (recorded in L6 step 7:
  unrelated local process attach+evaluate succeeded silently, recorded as
  owner-accepted behavior). The decision doc required this in writing before
  landing; the task brief confirms it. The acceptance must exist in the
  machine layer alongside the registry (C1). Loopback leg verified x3
  (W4, L4 smoke check f, L6 non-loopback Tailscale connect refused).
- **RT-20 scoping enforced in-tool:** `_guard` (`rdp_client.py:253-279`)
  gates `getTarget`/`evaluate`/`navigate` on scope then denylist;
  navigate-destination denylist check at `:527-545`; approvals require
  `--allow-credential-tab` + `--approval-note` together (`:744-752`) and are
  logged; drive report carries probe, tab diff, refusals, approvals, retries
  (`:624-662`). Live-proven in L3 (21/21) and L6 step 3 (scoped session,
  denylist ON, zero owner tabs touched, `drive-step3.json`). **Gap: the
  denylist is OFF by default** (`--use-default-denylist` opt-in or config).
  For the owner session it must be ON (C2).
- **Fail-closed registry:** rule verbatim in `rdp-port-registry.json`
  ("No channel selected = no drive... refuse to drive"); all channels
  currently `selected=false`; `zen-rdp-owner` `profile_marker` is null and
  the smoke refuses while null. Correct default.
- **Loopback-only bind:** smoke check (f) parses `ss` and fails on any
  non-`127.0.0.1:` local address (`rdp_smoke.py:56-68`); unit-tested (5 bind
  cases). L6 verified from a non-loopback interface (refused).
- **Fail-closed marker:** `check_port_owner` refuses an empty marker
  (`rdp_client.py:156-164`); CLI exits 2 before any connection when the
  marker is missing; the only escape is `--allow-unmarked-test-attach`,
  which warns loudly and is test-only. **Gap: unscoped mode still exists**
  (legacy, loud `UNSCOPED` warning, `rdp_client.py:47-52`). For the owner
  channel, unscoped must be procedurally forbidden (C3); the warning alone
  is not a fence.
- **Inherent limit (accepted with RT-04):** enforcement is client-side; it
  constrains this tool, not other local processes. That is the RT-04
  acceptance itself, not a new gap.

## Q4. Kill criteria status; maintenance ownership

| # | Criterion | Status |
|---|---|---|
| 1 | One update breaks toolset / 7 days broken | Not triggered (no update since build). Armed via smoke (C5). |
| 2 | Actor breakage on 2 consecutive updates | Not triggered. |
| 3 | Extension install impossible | N/A (3b not built; hybrid continues RDP+OS). |
| 4 | No named maintenance owner staffed | **Owner named (Muse parent, backup coordinator on duty) in decision doc + registry. Automation NOT yet applied:** L4's watch snippet is propose-only; the registry `smoke.script` path is "recorded at landing". Staffed on paper, not yet in the cron. C5 closes this at switch. |
| 5 | OS lane focus-safety failure | Not triggered (L2/L6 PASS). |
| 6 | RDP Google-entry failure | **Not triggered** (L6: 5/5 SERPs PASS, agent attached). |

Maintenance ownership is therefore **staffed by name, pending automation**.
Landing without applying the watch snippet would leave criterion 4 half-met;
the switch must include it (C5).

## Q5. Verdict, conditions, and what the switch concretely changes

**Verdict: LANDING-READY WITH CONDITIONS.**

### Conditions (all applied at switch time, before the first owner-session drive)

- **C1 (RT-04 record):** the 14:00 silent-attach acceptance is written into
  the machine layer with the registry, before `prompt-connection=false` is
  applied to the owner profile.
- **C2 (denylist ON):** owner-session drives run with the credential-tab
  denylist enabled (machine-layer scope config; generic defaults as floor).
  Default-off stays for throwaway use only.
- **C3 (scoped + URL-pattern, never unscoped):** owner-session drives are
  always scoped, URL-pattern scope preferred; tab-id scope only within a
  held session after a fresh `listTabs`. Unscoped mode and
  `--allow-unmarked-test-attach` are forbidden on the owner channel.
- **C4 (single driver, RT-23 fence):** one agent drives the owner session at
  a time, by coordinator assignment, until RT-23 locking is designed.
  Concurrent work uses the split profile.
- **C5 (step-8 automation + probation):** apply L4's watch snippet to
  `r3l3-zen-laptop-health` (cron.update + cron.view verify), record the
  laptop `rdp_smoke.py` path in the registry, and treat the first real Zen
  update as a supervised drill: smoke must PASS (probe CLEAN + Google spot
  check) before agent use resumes; any FAIL retires to the split per kill
  criterion 1, no retry-drive.
- **C6 (monitoring debts):** post-landing, (a) cold panel repeats across
  different hours within the first week, outcomes recorded per arm, no
  "never blocked" language; (b) first live `noSuchActor` retry firing is
  logged with its drive report and reported to the coordinator.
- **C7 (narrowed seamless claim, RT-02):** landed claim = DOM
  read/write/navigate + Zen-internals read/write via parent target (L1) +
  single trusted OS click + OS screenshot. Upload picker / clipboard /
  drag / Turnstile-gated forms remain on the split/OS lane until the RT-02
  suite passes on real tasks.
- **C8 (smoke before first drive):** `rdp_smoke.py` PASS (exit 0) on the
  owner channel (port 6021 + real profile marker) is recorded in the
  registry `last_smoke` before the first agent drive. L6's real-profile
  smoke (`smoke-real.json`, PASS) was on a test launch; the landed launch
  config gets its own run.

### What the switch concretely changes

1. **Launch config (machine layer):** owner `user.js` gains the generic RDP
   pref set (remote-enabled, chrome.enabled, prompt-connection=false,
   remote-host 127.0.0.1, remote-port 6021) and the owner launch path adds
   `--start-debugger-server 6021`. Still flag-free: no
   `--remote-debugging-port`, no `--marionette`.
2. **Registry:** `zen-rdp-owner.profile_marker` set to a substring of the
   owner Zen cmdline (profile dir); `selected=true` for exactly that one
   channel; `last_smoke` updated by C8. All other channels stay unselected.
3. **Tooling:** laptop copy of `scripts/zen-rdp/` (client + smoke) placed
   and path-recorded; watch cron updated per C5.
4. **Operating configuration:** agent DOM work moves from the split
   (flagged agent profile, BiDi) to the RDP lane on the owner's live
   session, scoped per task, with drive reports.

### What stays interim / unchanged

- The **two-profile split remains the fallback** and the home for concurrent
  drives (C4), RT-02-unproven trusted actions (C7), and any Cloudflare-gated
  site the RDP lane cannot pass.
- The **flagged escape hatch** (Route 2 mechanics) stays rare, explicit,
  logged; Marionette chrome stays out of the owner session.
- **3b extension bridge stays unbuilt** (fallback only if RDP breaks across
  an update; kill criterion 2 path).
- **R10 stays OPEN** until the first post-update drill passes (C5) and the
  C6 monitoring debts close; status reports keep saying so.
- Owner tabs/workspaces, Zen internals writes beyond L1-proven operations,
  and screenshots stay exactly as today (OS lane, pill visible).

### Blockers

None. Every residual risk above fails loud, is fenced by a named condition,
or is explicitly accepted (RT-04). The one item that would have blocked
landing, Google-entry failure (kill criterion 6), was tested on the real
profile and did not fire.

---

Council reviewer, 27/11/2026. English only. No GitHub commits. No laptop access.
