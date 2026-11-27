# zen-mcp idea adoption: council + redteam decision and sequenced plan

Date: 2026-11-27. Decision meeting on which zen-mcp ideas to port into
our RDP lane (scripts/zen-rdp) to build the combined version, in what
order, and what to reject. Inputs: improvements/zen-mcp-test-20261127.md
(measurements, commit 351f8020) and improvements/zen-mcp-study-20261127.md
(Clone2 audit). Method: three council agents (performance, reliability,
architecture lenses) and two redteam agents (cost/duplication, risk/security)
argued Round 1 from the measurement numbers only; Round 2 rebuttals
resolved four live tensions. This document is the converged decision.
No integration code was written in this task.

## The evidence base in one paragraph

Same fixtures, same machine, single runs (not medians), localhost pages.
zen-mcp rides one persistent connection; our RDP lane is one-shot CLI
invocations with a ~50 ms process-start floor per call, and roughly
50 ms of every "their lane is faster" delta is that floor, not their
scripts (status 2-6 ms vs probe 58-85 ms; tabs 2.2-6.1 ms vs 52 ms).
Where execution paths differ we are faster outright: type 52 ms vs
154.6 ms, click 51 ms vs 138.8 ms, space create 73 ms vs 127.3 ms,
folder create 99 ms vs 171.3 ms. Their snapshot payloads are larger
than ours (page1: 4,323 B vs 1,238 B; 300-control page: 51,082 B vs
25,919 B; raw HTML 13,378 chars), so a snapshot is structure plus
accounting, not a byte saving. Their context claim is real: research
surface 35,235 B for 17 tools vs full 83,261 B for 55 (-56.9%
same-version; -62.0% by chars vs their 0.5.0 baseline). Their event
read is 0.7 ms (backlog over a persistent connection) vs our 157 ms
end-to-end poll detection from a one-shot CLI; those are not the same
measurement. Their ambiguity refusal fired in 5.4 ms with a typed
error, but miscounted candidates ("6 elements" on a 100-button page).
zen_ask's server-side pending flow is proven (5,006 ms block, pending
plus questionId); the card render was never screenshot-verified and
the answering path never exercised.

## Per-item decisions

### D2 machine-layer copy drift: ADOPT NOW, first

The deployed machine-layer rdp_client.py lags the landed code (no I17
--wait-for/--wait-timeout), so every measured RDP number describes the
landed tree, not the deployed lane, and deployed callers poll (157 ms
class) instead of waiting (3.5 ms class). Unanimous. Fix: refresh the
deployed copy from the landed tree, add a hash assertion to the smoke
run so drift fails loud. Cheapest high-value fix in the whole set.
Expected saving: every wait on the deployed lane drops from poll-class
to wait-class. Cost: small.

### D1 bench wait_load timeout: ADOPT NOW

`rdp_client.py bench` failed on a healthy dedicated session with
`wait_load timeout for 'slice'` after 30 s, a 30,000 ms zero-output
burn against a 104 ms working navigate. Unanimous: root-cause first,
no timeout raise, keep fail-loud, add a bench self-test to the smoke
run. This is the measurement instrument every other item is judged
with. Cost: small to medium (diagnosis unknown until root-caused).

### D3 fresh-profile prefs footgun: ADOPT NOW

A fresh-profile RDP session needs the devtools user.js prefs
(remote-enabled, chrome.enabled, prompt-connection=false,
remote-host/port) or --start-debugger-server never listens (one headed
launch without prefs died; with prefs, two launches worked; ready
within ~3.5 s). Fix: one launch helper for dedicated RDP sessions.
Guardrail (redteam): chrome.enabled plus prompt-connection=false is a
loaded gun; the helper must verify the target profile root by marker
and fail closed, never the owner's profile. Cost: small.

### P1 snapshot command: ADOPT NOW, scoped

One format, one fixed server-authored read script, one subcommand,
routed through guarded evaluate() (credential denylist + tab scope),
I22 redaction over the full output including the text preview,
value-presence metadata only (never values), completeness flags plus
snapshotId, I17 load wait before reading (their tabs_open returns
before load with the URL lagging at about:blank, so an immediate read
can mistake blank for complete). Redteam guardrail accepted: fixture
acceptance test at or below 25,919 B on the 300-control page (our
current cap-200 walk size), tighter than their 51,082 B; denylist-
refusal smoke check; their 3,561-line read script is not ported as a
blob. Form resolved: subcommand beats a snippet library because the
subcommand is the contract that issues snapshotId and routes through
the guard; a snippet through eval is still caller-supplied JS, and
per-callsite drift is the current state, not a future risk. Expected
saving: one JS-authoring think-step per read and bounded token spend;
wall-clock saving is ~0 ms as another CLI subcommand (the 52-54 ms vs
13.5-20.3 ms delta is the process floor), and that is stated honestly.
The value is accounting: today our cap-200 walk truncates silently
with no completeness flag. Cost: medium. Foundation for P2.

### P2 refs + digest + ambiguity refusal: SPLIT

Ambiguity refusal: ADOPT NOW, in single-eval verify-and-act form.
Exhaustive match count inside the act script, act only on count==1,
report the true count or candidatesTruncated=true (their capped count
must not be copied), retry=unsafe, merged into the landed I3 contract
(one ref system, two resolvers), not a second scheme. Their refusal
fired in 5.4 ms; a wrong first match costs ~153 ms plus a think-step
and is our known failure class. Their actor execution (click
138.8 ms, type 154.6 ms) is explicitly NOT copied; we keep our
51-52 ms JS path.

Persistent ref registry + cross-call digest re-verification: ADOPT
LATER, gated on F1. Round 2 resolved the tension: single-eval
atomicity closes the TOCTOU/stale-target half and removes the
retry-on-mismatch loop, but it does NOT close transport-level retry
of a delivery_uncertain act eval; atomicity in-page is not
idempotency across the socket. Two settling tests are specified and
must pass before the registry ships: (a) fault-injection delivery
test, drop the RDP response after the click fires in-page, submit
counter must stay 1 with retry=unsafe; (b) two identical "Confirm"
buttons swap/mutation test, proving digest shows descriptor
stability, not element identity. Frequency of wrong matches is
unmeasured; the registry's benefit is therefore unproven until those
tests and a wrong-match rate exist. Cost: medium to large.

### P3 browser event feed: SPIKE FIRST, library-mode only

Council-performance's ADOPT NOW did not survive Round 2. The 0.7 ms
figure is a backlog read over a persistent connection; 157 ms is
end-to-end detection from a one-shot CLI. In one-shot CLI mode an
in-process log dies per invocation, so cross-call value is zero; the
win shrinks to within-invocation navigate+wait flows. Their rich
event classes (navigation phases, document replacement, dialogs) come
from in-browser chrome observers (browser-events.ts), not from
discarded RDP packets; which event classes arrive unsolicited on our
socket is unproven. Demuxing unsolicited packets inside request() is
the riskiest client change on the table (tabListChanged storms
mid-request; 25 s long-poll fights the wrapper-set flock). Spike
scope: packet-class inventory plus demux proof under a tab-restore
storm shape, bounded 200-entry log with dropped-count flag, cursor
read only, I22 redaction before any URL is logged. No long-poll, no
reader thread, no server-side watches. If the spike proves coarse
lifecycle events (tab changes, navigation, target destruction) arrive
reliably, the library-mode feed shrinks F11 wait burn; if not, F11 is
finished by other means and P3 closes. Cost: spike small, build
medium if proven.

### P4 typed Spaces/Folders surface: SPLIT

List + create: ADOPT NOW as 3-5 thin library wrappers owning the
gZenWorkspaces/gZenFolders JS strings, behind the existing
parent-context gate plus audit, pinned method set asserted in the
smoke run. Honest basis: our raw peval is already faster on creates
(73 vs 127.3 ms; 99 vs 171.3 ms); the value is one audited
implementation instead of hand-written chrome JS plus 55 ms
introspection per callsite. Port zen_live.py's call knowledge, not its
Marionette transport (it cannot attach to the owner's live Zen).

Move/switch: ADOPT LATER, separate decision, owner-active guard.
They mutate visible owner state (the 21/11 focus-steal and 27/11
incident class). Delete: REJECT by charter, permanently. The ratchet
is documented, not speculative: create/move/switch/delete are single
method calls, and their catalog is the end state (PolicyLayer: 24 of
50 tools modify or destroy without limits, 3 rated critical risk).
Cost: small for list+create.

### P5 progressive disclosure: REJECT as build, pattern recorded

The numbers are real (35,235 B vs 83,261 B, -56.9%) but solve a
55-tool problem we do not have (7 subcommands, no MCP surface over
zen-rdp). Record the pattern plus a trigger condition (~35 KB
tools/list payload) in the I9 capability matrix; building a
search/use gateway now is for-later code. Note their trap: the
research surface omits zen_wait_for while tabs_open returns before
load. Cost: zero now.

### P6 zen_ask interaction contract: SPIKE FIRST, throwaway profile only

REJECT for the owner's live Zen. The card render was never
screenshot-verified, the answering path never exercised, the only
live run disabled their own consent card (requireConsent:false), and
their 120 s default block would hold the flock plus socket on the
live session. The only measured number is a cost: 5,006 ms blocked
with nobody answering, against our handed-over unattended model.
Spike scope: throwaway profile, screenshot-verified render, focus
measurement, answering path exercised end to end. The transferable
part is the contract (card, blocking wait with pending fallback, late
answers via companion call), not their chrome code. Cost: spike
medium, build large and uncommitted.

### P7 launch-nonce ownership proof: ADOPT LATER, inside D3 helper

Dedicated self-launched sessions only; never gates attaching to the
owner's live Zen (we do not launch it; a no-nonce-expected vs
mismatch bug there means lockout or false pass). Complements, never
replaces, the profile-marker gate. Point-in-time and same-user
readable, so defence-in-depth only. Cheapest acceptable form also on
record: PID + profile + port session file verified at attach. Cost:
small.

## Not-adopt list (final, 13 items)

Original four, confirmed by all agents: (1) owned-browser-only model
(conflicts with driving the owner's live Zen; they refuse attach
entirely), (2) npm distribution for our channel (98-package supply
chain that already moved at 0.6.3 with a postinstall skill offer),
(3) update-check phone-home (egress with zero benefit), (4) history
access without allowlist filtering (their Places SQL at
ops.ts:3966-4011 bypasses their own allowlist).

Nine additions from redteam-risk, all accepted in Round 2:
(5) Places SQL history/bookmarks at all (their allowlist is advisory,
proven by the bypass; would hole our denylist + I22),
(6) clipboard write, (7) the destructive set (space/session/template
delete, essentials), (8) session save/restore into the live Zen,
(9) the consent-card pattern as a credited control (banned as a
control, allowed as a spike subject), (10) the Marionette lockdown
(rejected for the owner's Zen and shared infra outright; not adopted
for dedicated sessions either, because the RDP re-attach path needs
the listener), (11) tabs_open returns-before-load semantics,
(12) server-side polling watches, (13) acting on inactive-space tabs
without selection.

## Sequenced implementation plan

Order respects dependencies and the "fix the instrument first" rule.
Owner lanes use the standing fleet: Codex (gpt-6-luna under herdr)
for implementation, FCC (fcc-claude) for small fix batches, opencode
(opencode/ models only) for test batches, Clone2 for independent
review (grader is never the author). Every item: unit tests green,
live test on the laptop against a dedicated test session (never the
owner's Zen except where the item is explicitly about the deployed
lane), before/after measurement recorded, council+redteam gate before
landing, pii-scan clean (exit 1 = no push), explicit pathspec commits,
push verified via ls-remote.

1. D2 deployed-copy refresh + hash assertion. Lane: FCC (small fix).
   Test: smoke run fails loud on a deliberately drifted copy; deployed
   navigate/eval accept I17 flags; before/after: deployed wait drops
   from poll-class to wait-class.
2. D1 bench root-cause + self-test. Lane: Codex. Test: bench completes
   on a dedicated session with a timed result; self-test in smoke;
   before/after: 30,000 ms timeout burn vs measured bench time.
3. D3 launch helper. Lane: Codex. Test: fresh dedicated profile
   launches, debugger port listens, probe CLEAN; helper refuses a
   non-marker profile (fail closed); owner profile path refused.
4. P1 snapshot command (scoped). Lane: Codex, Clone2 review. Test:
   fixture acceptance at or below 25,919 B on the 300-control page;
   completeness flags correct under cap; denylist refusal on a
   credential URL; I22 over output verified with a planted token;
   before/after: read think-steps and payload bytes vs agent-JS eval.
5. P2a ambiguity refusal (single-eval). Lane: Codex, Clone2 review.
   Can run parallel to 4 (act path vs read path). Test: ambiguous
   "Action" target on the 300-control fixture refused with true count
   100; unique target acts; retry=unsafe asserted in envelope;
   before/after: wrong-element rate on a duplicate-label fixture.
6. P4 list+create wrappers. Lane: FCC or Codex. Parallel to 4/5
   (parent-context path). Test: list/create against dedicated
   session, gate+audit entries present, pinned method set asserted in
   smoke, delete absent by construction.
7. P3 spike (library-mode packet inventory + demux proof). Lane:
   Codex. Deliverable is evidence, not a feature: which event classes
   arrive unsolicited, demux correctness under a tab-restore storm
   shape, dropped-count behaviour. Decision point after the spike.
8. P6 spike (throwaway profile). Lane: Codex. Deliverable: screenshot-
   verified card render, focus measurement, answering path end to end.
   No live-Zen commitment regardless of spike outcome without a new
   decision.
9. P2b refs registry + digest. Lane: Codex, Clone2 review. Gated on
   F1 closure, both settling tests passing, and P1 landed. Test: the
   two settling tests become regression tests.
10. P4 move/switch. Separate decision with owner-active guard; not
    scheduled.
11. P5: record pattern + ~35 KB trigger in the I9 matrix. Lane: any,
    documentation only.

Explicitly not scheduled: P7 ships only as part of the D3 helper if
the helper's author includes it cheaply; otherwise it waits for the
next dedicated-session hardening pass. F1 double-execution and F11
completion remain competing priorities ahead of P2b and any P3 build;
the redteam opportunity-cost ranking (D2, D1, D3, then F1/F11, then
P2-lite, P4-lite, P1-lite) is noted and the sequence above is
consistent with it.

## What we are NOT buying

Recorded so the decision is auditable: their WebDriver actor execution
path (click 138.8 ms, type 154.6 ms vs our 51-52 ms), their nine
read formats (we take one), their 3,561-line read script as a blob,
their MCP surface itself, and every item on the 13-item not-adopt
list. The combined version keeps our channel's core: driving the
owner's real live session, delivery/retry semantics, attach-time
defence in depth, stdlib-only zero supply chain. The ported ideas are
patterns reimplemented in our shape, measured on our fixtures, gated
by our tests.

## Sources

All accessed 2026-11-27.

- improvements/zen-mcp-test-20261127.md (commit 351f8020, this repo):
  all measurements cited.
- improvements/zen-mcp-study-20261127.md and
  improvements/zen-mcp-study-lanes/ (this repo): architecture,
  security audit, comparison, the 55-tool catalog.
- scripts/zen-rdp (landed integration tree): our channel as measured.

## Execution status (2026-11-27, adoption branch zen-mcp-adopt-20261127)

Owner approved execution 22:48 +07. Five parallel workers, one branch
each, merged into zen-mcp-adopt-20261127. Merged-tree suite: 125
tests OK (2 P2b session tests skip cleanly), smoke/bench/launch
script tests PASS.

- D2 DONE (adopt-dfix a50bfc93): deployed copy refreshed (md5
  7145e620 -> landed), smoke hash gate exit 17 fails loud on drift
  (0.2 ms, before attach). Deployed wait: poll-class 212.6 ms ->
  wait-class (in-process wait_for 1.8 ms; one CLI call instead of N).
- D1 DONE: root cause was hardcoded wait substrings ("slice",
  "example") in bench(); fixed by deriving the substring from the
  URL, no timeout raise. Bench runs=3 total 0.743 s vs 30.273 s
  timeout burn. Smoke bench self-test (exit 18) added.
- D3 DONE: launch_dedicated.py (marker + nonce session file, the
  cheap P7 form included). Fresh launch 0.465 s, probe CLEAN,
  refusals exit 2 (non-marker dir, owner profile, outside temp).
- P1 DONE (adopt-p1 26c16c07): snapshot subcommand via guarded
  evaluate(), I22 over output, value-presence only, completeness
  flags + snapshotId. 300-control fixture 17,347 B vs 25,919 B cap.
  Clone2 independent review requested.
- P2a DONE (adopt-p2a 809085ca): act subcommand, single-eval
  verify-and-act, true count 100 refusal proven live, wrong-element
  rate 1/1 -> 0/1, latency parity (73.8 vs 72.4 ms). Clone2
  independent review requested.
- P4 DONE (adopt-p4 d68501ce): zen_spaces.py list+create wrappers
  behind parent gate + audit (44/44), pinned methods in smoke,
  delete absent by construction (grep-verified).
- P3 SPIKE DONE (adopt-spike c8b1b54f): coarse lifecycle events DO
  arrive unsolicited (tabListChanged, descriptor-destroyed,
  tabNavigated); demux proof passed under 12-tab storm (36/36
  paired). Library-mode feed is viable; build decision pending.
- P6 SPIKE BLOCKED: pinned install completed, then a runtime
  execution-risk check stopped execution before the server ever
  ran. Card render, focus, and answering path remain unverified.
  Needs a fresh explicit owner go-ahead to execute the pinned
  package in the isolated test environment.
- P2b settling tests DONE as code only (test_p2b_settling.py):
  fault-injection drop keeps submit counter at 1 with retry=unsafe;
  identical-Confirm swap shows digest = descriptor stability, not
  identity. Live 7/7 PASS. P2b itself NOT landed (F1 gate stands).

Merge notes: smoke exit codes renumbered after a collision
(drift 17, bench 18, pinned methods 19); check letter (j) for bench.
pii-scan: adoption delta adds zero new hits; the single hit on the
changed-file scan (rdp_client.py token= comment) is pre-existing at
431a8d1e. Machine-layer copies must be refreshed from the final
merged tree after landing (the D2 hash gate will flag the drift
until then, by design).

## Gate-fix addendum (2026-11-27, branch adopt-gatefix)

Council verdict LAND-WITH-FIXES and redteam verdict BLOCK on the
adoption branch, plus Clone2's independent P1 review FAIL
(improvements/p1-snapshot-review-20261127.md, ce5287c3, 4 MAJOR).
All findings fixed on adopt-gatefix (bf43b542 + c8902d7f); every
finding was verified against the code first, all were real.

- B1: act refuses on a truncated scan even at examined count 1
  (JS scan_truncated return before any click, plus a python-side
  conversion if a script ever acts truncated). Live: 10001-button
  page refused target_scan_truncated with count=1.
- B2: evaluate(replay=False) for act; exactly one execution, read
  paths keep the RT-06 retry. Live via the P2b noSuchActor variant.
- B3: P3 probe requires a verified launch_dedicated profile and
  closes only tabs it tagged. Live: 4 opened, 4 tagged closed,
  pre-storm tabs intact, demux paired.
- B4: launch_dedicated stop() runs full session validation
  (marker+nonce, profile/port agreement, exact profile cmdline
  token, pid start-time pin) before signaling. Forged-session
  unit tests refuse; live stop of the test session worked.
- M1 + Clone2 A-2/A-3/A-5/A-6: bare-secret redaction in text
  (sensitive key=value pairs, Bearer, sk-/ghp_/AKIA prefixes,
  32+ char token-like strings), bare-token fragments, token path
  segments, data:/javascript: payloads, list-of-strings walk.
  Residual limit documented in README (pattern-based).
- M2/C-M1: field and contenteditable content excluded from
  snapshot names, the text preview (text-node walk skipping form
  subtrees), and act summaries. Settled live: Firefox textarea
  innerText returns '' (not the value); the exclusion holds
  regardless. Planted-secret live fixture: all absent.
- M3: act visibility via computed style (display/visibility/
  opacity); disabled excluded for click, typed refusals for type
  (target_disabled/target_readonly). Live-verified.
- M4: type verdicts carry hasValue/valueLength only. Live: typed
  password absent from verdict bytes.
- M5: wait_for/wait_load re-raise guard refusals. Live: denylist
  snapshot refusal 0.00 s (was the full 10 s budget).
- M6/C3: smoke bench leg requires dedicated-session proof
  (--bench-profile-dir or explicit any-session flag), refused
  before attach otherwise; i_bench renamed j_bench. Live smoke
  PASS all checks including j_bench.
- M7: create_space captures activeWorkspace before/after and
  fails loud on change; slot cleanup in finally (m3). Live:
  space created, active workspace unchanged.
- M8: P2b settling test (a) drives shipped RDPClient.act()
  through the dropping proxy (dropped response + noSuchActor
  variants), submit counter stays 1, retry=unsafe; descriptor
  vs SNAPSHOT_JS field mapping documented in the test file.
- C-M2: snapshot payload validated client-side (required keys,
  returnedElements recomputed, flag consistency) - the
  delivered_verified label is earned, not relabelled.
- C-M3: 25,919 B is now an enforced byte cap (bytesTruncated);
  role/title/url capped in JS; all caps are Python constants
  interpolated into the JS (m6/B6).
- C-M4/F2: longString reassembly advances by actual chunk
  length, verifies total length, rejects error packets;
  fake-transport longString tests incl. chunk-error case.
- C1: launch kills the launched process on port timeout or
  port-owner failure; the temp dir itself refused as a profile.

Suite: 159 tests OK (3 live skip without a session; 8/8 with the
dedicated session incl. both P2b fault-injection tests), smoke /
bench / launch script tests PASS. pii-scan delta zero (17
pre-existing hits at base 2729de6a, unchanged count). Live session
was a dedicated throwaway on port 9236 via launch_dedicated,
stopped through the tool afterwards; the owner's Zen was never
touched. Clone2's P2a review was still pending at gate-fix time;
if it lands, its findings need a follow-up pass.

## Final-review BLOCKING fixes (2026-11-27, cf5d8790)

Clone2's final pre-landing review of 2adb4c5a
(improvements/adopt-final-review-20261127.md, 2389a4be on
todolist-push) raised 2 BLOCKING findings. Both fixed in
cf5d8790 on zen-mcp-adopt-20261127:

- BLOCKING 1 (P1 snapshot ancestor innerText leak): FIXED.
  SNAPSHOT_JS drops innerText from the name chain for any
  element wrapping a form/editable descendant (wrapsField
  guard); aria-label and attribute fallbacks still apply.
  New stub-DOM node test runs the shipped script on the
  review probe shape (div role=group wrapping a
  contenteditable with a planted secret) and asserts the
  secret reaches no emitted name and no text preview.
- BLOCKING 2 (P2a act pool scope undisclosed): FIXED by
  disclosure (the review's named minimum; scan still does
  not enter iframes/shadow DOM). Header comment, module
  docstring, act() docstring, and README now state the
  top-document scope; every act verdict carries
  poolScope: "top-document" (JS-emitted, defaulted
  python-side in act(), recorded in drive-report refusals).

Suite after fix: 162 tests OK (3 live skip). pii-scan delta
zero (17 pre-existing benign hits, identical set). Still
tracked for the follow-up pass, per the review: emoji UTF-16
validation MAJOR, P2a M3 disposition, M5 evidence remainder,
and the MINORs.
