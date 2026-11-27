# Idea queue 2026-11-27: new ideas and refinements with evidence

Date: 2026-11-27. Prepared by clone2 from four expert-source research
lanes (R1 error contracts, R2 element identity, R3 AT-SPI performance,
R4 protocol evolution), building on the agent-desktop comparison study
of the same date (ideas I1 to I23, open items U1 to U5).

Purpose: a queue of new ideas and refinements, with evidence, for the
integration team. The owner approved integration and testing of the
study's proposals on the real machine on 2026-11-27, and directed that
research continue and new ideas enter this queue with evidence
attached. The final test comes last, after the best level is reached;
nothing in this queue changes that order.

Evidence rule: every entry cites a real source that the lane opened and
read (URL, access date 2026-11-27), or is marked "read via search text"
in the entry itself, or cites a local proof already on record.
Anything a lane could not open or verify is marked UNVERIFIED and is
quarantined in section 4; no queue entry rests on quarantined material.

Measurement rule (owner directive, 2026-11-27 18:34): every proof run
measures and logs every event in full detail, nothing skipped, with
wall clock and elapsed timing recorded. Every "proof to promote" line
below is to be executed under that rule.

## 1. Answers to open questions from the study

### U3. I2 refusal-rate budget: no source supports a number

Lane R2's answer, stated plainly: no source supports a numeric
refusal-rate budget. No specification (WebDriver, AT-SPI, accName)
names an acceptable refusal percentage. Playwright's documentation sets
strictness as a binary rule (throw on multiple matches), not a rate.
Falkowski's measured study reports refusal behaviour of specific
engines on specific tasks (missing-target refusal 90 to 100 percent,
look-alike refusal 49 to 79 percent), but those are observed
behaviours, not recommended budgets, and his only numeric thresholds
(confidence cuts at 0.5 and 0.9) come with his own warning that they
were fitted on the evaluation data and should not be reused as-is.

Any number the I2 pilot adopts is therefore our own design choice, and
the pilot plan must label it that way. The defensible route is the one
the converged I2 form already specifies: measure the mis-click baseline
first, then set the refusal ceiling per app as a self-imposed target.
One form the sources do support qualitatively: every source treats a
wrong-element act as categorically worse than a refusal, so a
zero-tolerance wrong-act target paired with a per-app refusal ceiling
is consistent with the evidence, while any specific ceiling percentage
is not source-backed.

Evidence: Bryan Falkowski, "Can a Browser Test Agent Tell When It Can't
Tell?" (https://bfalkowski.github.io/writing/cant-tell.html, accessed
2026-11-27); Playwright Locators and Auto-waiting documentation
(https://playwright.dev/docs/locators and
https://playwright.dev/python/docs/actionability, accessed 2026-11-27).

### U4. Python-side AT-SPI walk speedup: plausible, by cache and bulk calls, not threads

Lane R3's answer: a Python-side speedup is plausible, but not by the
mechanism the I5 walk pilot first assumed. No opened source supports
bounded-concurrency GetAll under threads as the win: pyatspi calls are
synchronous, libatspi's own history shows main-loop starvation
pathologies (BGO#701145, read via search text), and no source demonstrates threaded pyatspi
walks scaling. The GIL question stays genuinely open, and it is the
smaller question. The sources support four mechanisms, in evidence
order:

- (a) Fewer round trips per node, via the cache. Name, parent,
  children, state, role, description and interfaces are cacheable and,
  once populated, are served locally. Precondition: the cache is only
  maintained while events are processed, so the walk needs a running
  main loop or the cache may be stale or never populated.
- (b) One bulk snapshot per application, via Cache.GetItems. A single
  call returns parent, index, child count, interfaces, name, role,
  description and states for every object. Caveat: Qt's bridge
  GetItems is a stub returning empty in the examined source and Qt
  still uses the old signature, so this path is per-toolkit and must
  be probed.
- (c) Keep uncached fields out of the hot walk. Extents and attributes
  are never cached and cost a round trip each; Chromium's profiling
  independently shows geometry dominating serialization cost.
- (d) Server-side filtering for find-style queries, via
  Collection.GetMatches: one call, filtering in the application, one
  reply.

The measurement that settles U4, tied to the I8 probe ledger: run five
walk variants on our own stack against three application classes (one
GTK, one Qt, one Electron or Chromium), recording per variant the wall
time, nodes visited, and D-Bus call count. Variants: (i) the current
synchronous per-property walk; (ii) the same walk with a main-loop pump
running and cache-served fields only; (iii) a GetItems bulk snapshot
per application plus local tree assembly; (iv) a threaded walk over
disjoint subtrees at 2 and 4 threads, testing GIL scaling directly;
(v) GetMatches for the find case. The success factor is stated
before running, as a pre-registered choice of this queue (not
sourced): the pilot continues only if a variant beats (i) by at least
2x on the dense application without losing nodes. If none
does, U4 closes as "no win available" and the walk pilot dies there.

Evidence: org.a11y.atspi.Cache interface documentation
(https://gnome.pages.gitlab.gnome.org/at-spi2-core/devel-docs/doc-org.a11y.atspi.Cache.html,
accessed 2026-11-27); Mike Gorse, "AT-SPI caching and D-Bus usage",
2013 (https://www.mail-archive.com/gnome-accessibility-devel@gnome.org/msg02272.html,
accessed 2026-11-27); hyprsay verification block, section V2
(https://github.com/ilyaskhallouki/hyprsay/blob/HEAD/docs/research/vision/verification_block.md,
accessed 2026-11-27); Atspi.set_timeout documentation
(https://gnome.pages.gitlab.gnome.org/at-spi2-core/libatspi/func.set_timeout.html,
accessed 2026-11-27).

U1, U2 and U5 were not in these four lanes' scope and remain open
exactly as recorded in the study.

## 2. The queue

Ordering basis: proven live defects and safety hazards first, then
mechanisms that unblock approved pilots, then contract and design
refinements, then new capability and process items, then confirmations
of already-approved design (no new work beyond proceeding as approved).
Entry numbers (Q1 to Q47) are stable identities and never change;
tier placement is the priority order, and an entry can move between
tiers without renumbering.

### Tier A. Proven defects and safety hazards

### Q1. Pass --allow-system-access to geckodriver itself

- Kind: REFINES (lane plumbing under the approved Marionette and
  zen_dom routes)
- Touches: zen_dom.py geckodriver lane (no I-number; supports I1's Zen
  lane family)
- Proposal: There are three distinct system-access mechanisms and they
  are not interchangeable: the environment variable for direct browser
  launch, --remote-allow-system-access as a browser argument, and
  geckodriver's own --allow-system-access flag. Any zen_dom.py launch
  path that sets system access through moz:firefoxOptions args is
  silently broken on current geckodriver and must use the flag.
- Evidence: geckodriver CHANGES.md
  (https://github.com/mozilla-firefox/firefox/blob/HEAD/testing/geckodriver/CHANGES.md,
  accessed 2026-11-27): 0.36.0 introduced --allow-system-access;
  0.37.1 (2026-07-20, the version on clone2's VM) states "Browser UI
  testing for Firefox now requires the geckodriver
  --allow-system-access command-line argument. Setting the Firefox
  --remote-allow-system-access command-line argument via
  moz:firefoxOptions is no longer supported."
- Proof to promote: one live geckodriver session on a throwaway Zen
  profile with the flag set, reaching chrome context; and one without,
  recording the failure. Success criterion: chrome context reachable
  only via the flag, both runs fully logged.
- Status: QUEUED

### Q2. Client-supplied action keys with stored-outcome replay

- Kind: NEW IDEA
- Touches: I1 (envelope and disposition), I7
- Proposal: The caller attaches a UUID action key to each
  state-changing command (click, type, key, folder op). The executor
  records key to outcome (envelope included) once execution begins; a
  retry presenting the same key returns the recorded envelope instead
  of executing again, and key reuse with different parameters is an
  error. No stored outcome for pre-execution validation failures. A
  second call presenting a key whose attempt is still in flight
  receives an error (Stripe's behaviour), never a fresh execution.
  Keys are scoped to the session and lane that created them, and are
  prunable after a retention window of at least 24 hours, adopting
  Stripe's pruning floor. This converts delivery_uncertain from a
  terminal guess into a resolvable lookup in the cases where an
  outcome was recorded; if the executor dies during execution before
  recording an outcome, the uncertainty remains and the caller must
  treat it as before.
- Evidence: Stripe API, Idempotent requests
  (https://docs.stripe.com/api/idempotent_requests, accessed
  2026-11-27): client-generated keys, stored status and body replayed
  on retry including saved 500s, parameter mismatch on key reuse is an
  error, keys prunable after at least 24 hours, no stored result for
  validation failures or in-flight same-key requests. Local relevance:
  the RDP toolkit review (Task 3) proved a live double execution of
  evaluate() through an error path, the failure family this removes.
- Proof to promote: fault-injection pilot on the Zen lane: kill the
  response path after execution on a state-changing command, retry
  with the same key, and verify the recorded envelope returns and the
  action executed exactly once, counted on the page side. Success
  criterion: exactly one execution across the retry, in every injected
  run.
- Status: QUEUED

### Q3. A separate result kind for page and script exceptions

- Kind: NEW IDEA
- Touches: I1
- Proposal: I1 should return evaluate-style script exceptions as a
  success-shaped exception result (exception text, value, line, column,
  stack trace), not as a protocol error. Protocol errors say the
  automation failed; an exception result says the automation worked and
  the page code threw. Keeping them in different envelope kinds makes
  the error-text-matching bug class structurally impossible.
- Evidence: W3C WebDriver BiDi specification
  (https://w3c.github.io/webdriver-bidi/, accessed 2026-11-27):
  script.callFunction and script.evaluate return
  script.EvaluationResultException carrying exceptionDetails, not a
  protocol error. Local relevance: the RDP toolkit review proved that
  matching the string "noSuchActor" in error text caused a live double
  execution.
- Proof to promote: test on the Zen lane with a page script that throws
  a crafted exception whose text contains a protocol error name;
  success criterion: the result is classified as a script exception,
  no retry or re-execution occurs, and the envelope kind differs from
  protocol errors in the log.
- Status: QUEUED

### Q4. Fix zen_live.py wire handling and rebuild its test fake

- Kind: CONFIRMS (the R17 findings and fix direction)
- Touches: Marionette lane (folder tool); supports the study's
  evidence base for I23
- Proposal: Fix the four stacked client defects proven in R17
  (length-prefixed greeting parse, namespaced command names only,
  lazy ops dispatch, last-argument async callback), and rebuild the
  unit-test fake server from the documented wire framing, since the
  current fake encodes the same wrong assumptions and kept 20 tests
  green while the client was dead live.
- Evidence: Marionette reference client transport.py
  (https://dev.phabricator.nonprod.webservices.mozgcp.net/source/mozilla-esr52/browse/default/testing/marionette/client/marionette_driver/transport.py;7fc6eedd33484ae8679bde3ae600563d2b457f4e,
  accessed 2026-11-27): messages "are always preceded by the message
  length and a colon". Bugzilla 1452490
  (https://bugzilla.mozilla.org/show_bug.cgi?id=1452490, accessed
  2026-11-27): marionetteScriptFinished removed in Firefox 63, "The
  callback is always the last argument". Local proof: R17 report
  (improvements/zen-r17-continuation-20261127.md), fixed copy runs
  live at 68 to 131 ms on Zen 1.24.3b.
- Proof to promote: already proven on clone2's VM for four
  subcommands; promotion to the repo copy needs the laptop live test
  still owed from the folder-tool research, now including the pinned
  dump through the RDP route. Success criterion: the same ops pass
  against the owner's Zen build, fully logged.
- Status: QUEUED

### Q5. ChildCount-gated enumeration in the AT-SPI walk

- Kind: NEW IDEA
- Touches: I5 (accounting half, adopted)
- Proposal: Never call GetChildren on a node whose cached child count
  exceeds the per-node cap without a stated sampling or drill-down
  decision. The cap must be checked against ChildCount before the
  call, because a cap applied to the reply after it arrives does not
  bound the cost of producing the reply.
- Evidence: LibreOffice accessibility thread, 2024-06
  (https://www.mail-archive.com/search?l=libreoffice%40lists.freedesktop.org&q=subject%3A%22%5C%5Ba11y%5C%5D+LibreOffice+Calc+exposes+2%5C%5E31+children%2C+freezes+on+%60GetChildren%60%22&o=newest&f=1,
  accessed 2026-11-27): a container exposing 2^31 children freezes on
  GetChildren. Child count is available without enumeration via the
  Cache interface (source in Q7).
- Proof to promote: synthetic pathological container in the walk
  pilot (a fixture exposing a very large child count); success
  criterion: the walk records the node as cut-by-child-count in the
  accounting and completes inside budget, with no GetChildren call
  issued against it, verified in the D-Bus call count.
- Status: QUEUED

### Q6. Explicit short per-call timeout in the AT-SPI walk

- Kind: NEW IDEA
- Touches: I5, I15
- Proposal: Set atspi_set_timeout to a short value (order 100 to
  200 ms) instead of inheriting the 800 ms default, budget timeouts
  explicitly, and record timed-out nodes as unknown. This converts the
  worst case from "a few dead nodes eat the whole 2 s budget" to a
  bounded, accounted cost.
- Evidence: Atspi.set_timeout documentation
  (https://gnome.pages.gitlab.gnome.org/at-spi2-core/libatspi/func.set_timeout.html,
  accessed 2026-11-27): the libatspi default method-call timeout is
  800 ms, with a 15 s application startup timeout.
- Proof to promote: walk variant in the U4 measurement (section 1)
  with the short timeout set, against an app with unresponsive nodes;
  success criterion: total walk time stays inside the 2 s budget and
  every timed-out node is recorded as unknown in the accounting, none
  silently absent.
- Status: QUEUED

### Q47. MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 on the launch checklist

- Kind: CONFIRMS (the R17 launch gate)
- Touches: Marionette and BiDi chrome work on direct launches
- Placement note: sits in Tier A because it gates direct
  chrome-context launches.
- Proposal: Put the environment variable on the launch checklist for
  any direct Firefox or Zen launch that needs chrome context, for
  both Marionette and BiDi. Whether the laptop launcher (zen-human)
  sets it remains UNVERIFIED and needs the laptop probe owed from R17;
  see section 4.
- Evidence: Security aspects of the Remote Agent, Firefox Source Docs
  (https://firefox-source-docs.mozilla.org/remote/Security.html,
  accessed 2026-11-27): "you must explicitly enable system access by
  starting Firefox with the MOZ_REMOTE_ALLOW_SYSTEM_ACCESS environment
  variable set to 1", granting Gecko API access "for both the
  Marionette and WebDriver BiDi protocols".
- Proof to promote: the owed laptop probe; success criterion: the
  launcher's environment is inspected and the variable's presence or
  absence is recorded, not assumed.
- Status: QUEUED

### Tier B. Mechanisms that unblock approved pilots

### Q7. Retarget the I5 walk pilot: cache-served walk, then GetItems

- Kind: REFINES
- Touches: I5 walk pilot, U4
- Proposal: Replace the pilot's "bounded-concurrency GetAll rewrite"
  target with, in order: a cache-served walk with a main-loop pump, a
  per-app GetItems bulk snapshot where the toolkit serves it, and
  threads only as a measured variant. The concurrency-first framing
  priced a Rust async result onto a synchronous Python client; the
  sources price round-trip elimination instead.
- Evidence: org.a11y.atspi.Cache interface documentation
  (https://gnome.pages.gitlab.gnome.org/at-spi2-core/devel-docs/doc-org.a11y.atspi.Cache.html,
  accessed 2026-11-27): GetItems returns one record per object with
  parent, index, child count, interfaces, name, role, description and
  states, because per-object queries "produce a lot of traffic in the
  accessibility bus". Mike Gorse, 2013 (URL in section 1, U4):
  name, parent, children and state fetches dominate AT-SPI traffic,
  and the cacheable field set is exactly those fields.
- Proof to promote: the five-variant measurement specified in the U4
  answer (section 1), with the success factor stated before running.
  Success criterion: a variant beats the current walk by at least 2x
  (the pre-registered factor from the U4 answer, this queue's own
  choice, not sourced) on the dense application without losing nodes,
  per toolkit, recorded in the I8 probe ledger.
- Status: QUEUED

### Q8. Main-loop pump as part of the observe contract

- Kind: NEW IDEA
- Touches: I5, I15 (a11y lane infrastructure; no current design item
  names who owns the pump)
- Proposal: Run a GLib main loop (or pump thread) for the lifetime of
  the a11y lane, and state cache freshness in the snapshot itself.
  Without event processing the cache desynchronises or is never
  populated, so every cache-based speedup (Q7) silently rests on this.
- Evidence: Mike Gorse, 2011
  (https://www.mail-archive.com/gnome-accessibility-devel@gnome.org/msg01943.html,
  accessed 2026-11-27): "if a pyatspi script does not call
  registry.start() but instead calls sleep() or similar while waiting
  for user interaction, then it will not see any events and the cache
  will get out of synch". Lane R3 also records that at-spi2-core 2.1.2
  disabled caching if the event main loop has not been called
  (read via search text).
- Proof to promote: in the U4 measurement, variant (ii) runs with and
  without the pump; success criterion: the pumped run's cache-served
  fields match a fresh per-property read on the same tree, and the
  unpumped run's divergence (if any) is measured and logged, not
  assumed.
- Status: QUEUED

### Q9. GetItems snapshot as the I2 completeness proof on dense apps

- Kind: REFINES
- Touches: I2 pilot, I5
- Proposal: On dense applications, a GetItems snapshot may satisfy
  I2's complete-read proof more cheaply and more honestly than a live
  walk, because it returns child counts for nodes never expanded.
  Probe per toolkit before relying on it.
- Evidence: org.a11y.atspi.Cache documentation (URL in Q7, accessed
  2026-11-27): GetItems returns child count per object in the bulk
  record. Counter-evidence handled in the same entry: Qt's QSpiDBusCache
  source notes its GetItems returns an empty array
  (https://code.qt.io/cgit/qt/qtbase.git/tree/src/gui/accessible/linux/qspidbuscache.cpp?id=fc0e66eefe3a08428ca4a6e92c66f37ac126d3c4,
  read via search text 2026-11-27), so support is per-toolkit.
- Proof to promote: on one GTK and one Qt application, compare a
  GetItems-derived tree against the capped live walk; success
  criterion: the snapshot reports child counts for 100 percent of
  nodes the walk visited, or the toolkit is recorded in the probe
  ledger as not serving GetItems and the walk stays the proof there.
- Status: QUEUED

### Q11. Split the stale taxonomy, and make eviction a first-class outcome

- Kind: REFINES (plus one NEW IDEA element, the eviction outcome)
- Touches: I2 pilot, I3
- Proposal: Split STALE_REF into GONE versus REPLACED, and add a third
  outcome, UNKNOWN (or EVICTED), for refs that never existed or were
  evicted from the store. Our current two-way split cannot express
  eviction, which our own persisted RefMap pruning creates, so pilot
  metrics would mix store capacity with application behaviour.
- Evidence: Appium stale-element write-up, checked 2026-10-28 against
  UiAutomator2 driver 8.7.3 and XCUITest driver 12.22.2
  (https://www.rinsaitech.com/articles/appium-staleelementreferenceexception,
  accessed 2026-11-27): three distinct stale messages (list-origin,
  rebuilt, gone); bounded LRU element caches of 500 (UiAutomator2) and
  1024 (WebDriverAgent); eviction reported inconsistently across
  platforms (no such element on Android, stale on iOS). W3C WebDriver
  (https://w3c.github.io/webdriver/#errors, accessed 2026-11-27)
  likewise separates no such element from stale element reference.
- Proof to promote: I2 pilot scenarios covering each outcome (target
  deleted, target replaced, ref pruned from the store); success
  criterion: each scenario reports its own outcome class in the pilot
  log, with zero cases forced into a class that does not describe
  them.
- Status: QUEUED

### Q12. Check AT-SPI native death signals before re-resolving

- Kind: REFINES
- Touches: I2 pilot
- Proposal: Read the captured object's state first: ATSPI_STATE_DEFUNCT
  means the backing widget is destroyed; ATSPI_STATE_STALE means its
  data may be desynchronized. This cheap first gate can short-circuit
  the full window re-read in the common dead case, and it splits
  refusal causes measurably for the pilot's reporting. Where the
  object is still held for this check, that hold is a probe, not an
  identity claim.
- Evidence: AT-SPI2 Accessible interface reference
  (https://gnome.pages.gitlab.gnome.org/at-spi2-core/devel-docs/doc-org.a11y.atspi.Accessible.html,
  accessed 2026-11-27): ATSPI_STATE_DEFUNCT marks an object that "no
  longer has a valid backing widget"; ATSPI_STATE_STALE marks
  information that "may no longer be synchronized with the application
  state".
- Proof to promote: in the I2 pilot, log the pre-check result for
  every act and the short-circuit rate separately; success criterion:
  the defunct pre-check agrees with the full re-resolution outcome on
  the pilot's dead-target scenarios, and the per-act cost report shows
  the short-circuit share.
- Status: QUEUED

### Q13. Shuffled-order control in the I2 pilot harness

- Kind: NEW IDEA
- Touches: I2 pilot (harness validity)
- Proposal: Where the harness can permute sibling order, or replay a
  capture against a re-sorted tree, re-run re-identification and
  require the same verdict; a verdict that flips under permutation is
  position leakage, not identity. At minimum, position and child index
  must never act as a silent tie-breaker; if used at all, log the act
  as a separate, weaker verdict class.
- Evidence: Falkowski (URL in section 1, U3; accessed 2026-11-27): in
  page order, engines guessed on 25 to 29 percent of unanswerable
  points and were nearly always right by ordinal matching; with the
  list shuffled, both engines refused every time. The author warns
  page order "is fragile" and recommends a shuffled control.
- Proof to promote: run the I2 pilot's repeated-row scenarios twice,
  once in capture order and once shuffled; success criterion: verdicts
  identical across both orders on every answerable case, and any flip
  is reported as a harness finding, not averaged away.
- Status: QUEUED

### Q14. Evidence-strength score with a separately calibrated threshold

- Kind: NEW IDEA
- Touches: I2 pilot
- Proposal: Score which evidence classes matched (AccessibleId, name
  plus role, container slice, structural path), fix the acceptance
  threshold on a calibration set of scenarios, then freeze it before
  the measured pilot runs.
- Evidence: Falkowski (accessed 2026-11-27): a confidence threshold
  separated right from wrong picks in his data (a 0.5 cut blocked all
  of one engine's wrong picks while keeping every correct pick), with
  his explicit warning: "These thresholds were chosen on the same data
  they are evaluated on" and the exact cut points should not be reused
  as-is. The transferable form is the calibration discipline, not the
  numbers.
- Proof to promote: build the calibration set from scenarios disjoint
  from the pilot set, fix the threshold, freeze it in the pilot plan;
  success criterion: the pilot report states the threshold and its
  calibration provenance, and no threshold change occurs after the
  first measured pilot run.
- Status: QUEUED

### Q15. Record the capture context slice and capture cardinality on the ref

- Kind: REFINES
- Touches: I2 pilot
- Proposal: For refs captured inside repeated containers (rows, list
  items, cards), store the immediate container's identifying text, one
  container up, and require it to match at re-identification time. Do
  not store the whole table or list. Also record capture cardinality
  on the ref itself, so the act-time path does not trust caller memory
  that the ref was born unique.
- Evidence: Falkowski (accessed 2026-11-27): engines given surrounding
  row context picked the correct element 99.5 to 100 percent of the
  time; given names only, accuracy fell to 65 to 67 percent, and on
  repeated rows to 13 to 18 percent; whole-table context destroyed
  separability again. Appium write-up (URL in Q11): UiAutomator2
  restores only refs from a single-match find, never refs born from a
  multi-match find.
- Proof to promote: I2 pilot repeated-row scenarios run with and
  without the container slice recorded; success criterion: the
  with-slice run's wrong-act count on repeated rows is zero, and the
  comparison is reported per app, not pooled.
- Status: QUEUED

### Q16. Name the I2 pilot apps by failure property, not just density

- Kind: REFINES
- Touches: I2 pilot (specification)
- Proposal: The pilot's app set must include at least one app with
  view recycling or heavy row reuse (a mail client or file manager
  list with many near-identical rows, including a scrolling-list
  scenario) and one with repeated same-name controls, because those
  are the two measured failure shapes in the sources. A dense app
  alone exercises neither unless it has repeated rows.
- Evidence: Appium write-up (URL in Q11, accessed 2026-11-27):
  Android RecyclerView reuses row views, and because the element id
  identifies the view rather than its data, "a stored row reference
  can point at a view that now shows a different item", with no
  staleness signal. Falkowski (accessed 2026-11-27): repeated rows are
  where name-only identity collapses.
- Proof to promote: this is a pilot-specification change; promotion is
  the pilot plan naming, per app, which failure property it covers
  (recycling, repeated rows, repeated same-name controls), checked
  before the pilot runs.
- Status: QUEUED

### Q17. Per-act cost framing and refusal-cause split in I2 reporting

- Kind: REFINES
- Touches: I2 pilot (measurement), I8 (probe ledger)
- Proposal: Measure re-identification cost per act type (click-type
  versus type-type) rather than as one pooled figure, since the check
  set differs by action; report the defunct-check short-circuit rate
  (Q12) separately. Also separate context-destroyed refusals (window
  or application gone) from target-moved refusals in pilot reporting,
  because the remedies differ.
- Evidence: Playwright Auto-waiting
  (https://playwright.dev/python/docs/actionability, accessed
  2026-11-27): per-action actionability check sets differ (click
  requires exactly one element, Visible, Stable, Receives Events,
  Enabled; fill does not require Stable or Receives Events). Selenium
  error documentation
  (https://www.selenium.dev/documentation/webdriver/troubleshooting/errors/,
  accessed 2026-11-27): distinguishes a context change (reference
  still valid but temporarily inaccessible) from a page change
  (context destroyed).
- Proof to promote: the I2 pilot report carries per-act-type cost
  rows and the two refusal classes as separate counts; success
  criterion: no pooled cost figure appears without its per-type
  breakdown in the same report.
- Status: QUEUED

### Q37. Treat AccessibleId as bonus evidence, never required evidence

- Kind: REFINES
- Touches: I2 pilot
- Proposal: When an application sets AccessibleId, treat it as the
  AT-SPI analogue of a test id, the most resilient evidence class, and
  use it to confirm a candidate found by other means. Never require
  it: it is application-specific, often absent, and resolving by it
  requires a recursive walk because there is no find-by-id.
- Evidence: AT-SPI2 Accessible interface reference (URL in Q12,
  accessed 2026-11-27): AccessibleId is an "application-specific
  identifier for the current object" meant "for reliable
  identification by ATs or for use in tests", with the caveat that
  "there is no way to directly find an object by its id". Playwright
  Locators (URL in section 1, U3) calls dedicated test ids "the most
  resilient way of testing".
- Proof to promote: I2 pilot includes one app that sets AccessibleId;
  success criterion: refs there re-identify with the id as confirming
  evidence, and removing the id from the evidence set degrades the
  verdict to the standard path, never to a failure of the pilot.
- Status: QUEUED

### Tier C. Contract and design refinements

### Q18. Give every error code a documented caller-next-action

- Kind: REFINES
- Touches: I1, I7
- Proposal: For each code, the contract documents one of three next
  actions: retry the same call, retry at a higher level after
  re-observation, or do not retry until state is explicitly fixed.
  Retry guidance becomes a function of code plus disposition,
  documented per code. A not_delivered outcome caused by invalid
  argument must not be retried unchanged, while some delivered-state
  failures warrant a higher-level retry; disposition.retry alone
  carries neither fact.
- Evidence: gRPC status codes guide
  (https://grpc.io/docs/guides/status-codes/, accessed 2026-11-27):
  for FAILED_PRECONDITION, "Use UNAVAILABLE if the client can retry
  just the failing call", use ABORTED if the client should retry at a
  higher level, and FAILED_PRECONDITION if the client should not retry
  until the system state has been explicitly fixed.
- Proof to promote: contract review test: for every code in the I1
  set, a table row exists with its next action, and two worked cases
  (invalid-argument not_delivered, delivered-state check failure)
  produce different guidance. Success criterion: no code ships without
  a documented next action.
- Status: QUEUED

### Q19. Specify the unknown-code fallback and reserve a namespaced extension range

- Kind: REFINES
- Touches: I1
- Proposal: Two clauses in the contract. First, an unrecognized code
  degrades to a generic failure class while preserving the disposition
  fields, and never raises a parse error in the consumer. Second,
  reserve a colon prefix (for example zen: for the Zen lane, atspi:
  later) for lane-specific codes outside the closed core set, with
  consumers applying the fallback to any extension code they do not
  know. The core set stays closed because the fallback is defined.
- Evidence: gRPC status codes guide (URL in Q18, accessed 2026-11-27):
  codes outside the known range convert to UNKNOWN rather than
  failing. W3C WebDriver
  (https://www.w3.org/TR/2025/WD-webdriver2-20251028/#errors,
  accessed 2026-11-27): extension commands and capabilities live under
  a vendor prefix containing ":". WebDriver BiDi (URL in Q3): BiDi
  extends the classic set with about 17 additional codes, and
  extension modules must contain a single colon in the name.
- Proof to promote: consumer test feeding the envelope an unknown core
  code and an unknown extension code; success criterion: both degrade
  to the generic class with disposition intact, and no consumer raises.
- Status: QUEUED

### Q20. Adopt the RFC 9457 field split, with per-occurrence instance ids

- Kind: REFINES (field split) plus NEW IDEA (instance id as audit
  join key)
- Touches: I1, I12
- Proposal: Map the envelope's error object to: code (stable type id),
  a fixed title per code that never varies between occurrences,
  message as occurrence detail that consumers are forbidden to parse,
  and an instance or correlation id per occurrence that joins the
  envelope to logs and audit records. Mint the occurrence id on every
  envelope, success or failure, and require the executor's log and
  audit trail to record the same id. Add the documentation rule: no
  code enters the set without its id, fixed title, and exit-code
  mapping written in the contract.
- Evidence: RFC 9457 (https://www.rfc-editor.org/info/rfc9457, read
  via mirror https://test.nic.funet.fi/pub/mirrors/ftp.ietf.org/rfc/rfc9457.html,
  accessed 2026-11-27): title "SHOULD NOT change from occurrence to
  occurrence"; "Consumers SHOULD NOT parse the detail member";
  section 4.1, new problem types MUST document a type URI, a title,
  and the status code. Local relevance: the RDP toolkit review found
  parent-evaluate audit records do not persist without a drive report;
  an occurrence id is the join key that fixes correlation.
- Proof to promote: one end-to-end Zen lane action, forced to fail,
  traced from envelope to executor log to audit record by the single
  occurrence id; success criterion: all three records carry the same
  id, with no message-text matching used anywhere in the trace.
- Status: QUEUED

### Q21. Allow a typed data payload per error code

- Kind: REFINES
- Touches: I1
- Proposal: Define, per code, an optional typed payload object (for
  example the blocking element's ref for an intercepted-click code,
  the actual text for an unexpected-dialog code) instead of letting
  callers scrape the message.
- Evidence: W3C WebDriver errors section (URL in Q19, accessed
  2026-11-27): the error object bears error, message, stacktrace, and
  sometimes a fourth field, data. MDN WebDriver Errors
  (https://developer.mozilla.org/en-US/docs/Web/WebDriver/Reference/Errors,
  accessed 2026-11-27): the worked example shows unexpected alert open
  carrying data: {"text": ...}.
- Proof to promote: one code with a payload (unexpected-dialog with
  its text) consumed by a caller that reads only the payload;
  success criterion: the caller's behaviour is fully determined by
  code plus payload in the test log, with the message field unused.
- Status: QUEUED

### Q22. State the atomicity guarantee for validation-class codes

- Kind: REFINES
- Touches: I1 (and the already-built whole-batch validation in I4)
- Proposal: The contract guarantees that invalid-argument class
  failures are side-effect-free and multi-target operations are
  all-or-nothing, but only for operations the executor can actually
  make transactional. The proof must enumerate which operations
  qualify, and operations that cannot provide atomicity must say so
  in the contract instead of claiming it. That scoped guarantee is
  what licenses unconditional retry of that class after the input is
  fixed.
- Evidence: Appium WebDriver BiDi reference
  (http://appium.io/docs/en/latest/reference/api/bidi/, accessed
  2026-11-27): a subscribe request exceeding a limit "fails with an
  invalid argument error without changing the subscriptions", and an
  unknown subscription ID "causes an invalid argument error without
  removing any subscriptions".
- Proof to promote: enumerate which operations qualify as
  transactional, then run a multi-target operation with one invalid
  target against the Zen lane; success criterion: zero targets
  changed, verified by before and after state reads in the log, and
  every operation that cannot provide atomicity is marked non-atomic
  in the contract.
- Status: QUEUED

### Q23. Add an optional server-supplied retry delay

- Kind: REFINES
- Touches: I1, I17
- Proposal: Add an optional retry_after_ms member the executor may set
  when it knows the condition's duration (browser busy, rate
  limited), so callers stop guessing backoff for the codes where the
  executor knows better.
- Evidence: RFC 9457 (URLs in Q20, accessed 2026-11-27): "Problem type
  definitions MAY specify the use of the Retry-After response header
  in appropriate circumstances."
- Proof to promote: one busy-condition error on the Zen lane carrying
  retry_after_ms, with the caller honouring it; success criterion:
  the retry timestamp in the log is at or after the supplied delay,
  and no retry occurs before it.
- Status: QUEUED

### Q24. Attach a structured diagnostic log to timeout-class outcomes

- Kind: REFINES
- Touches: I1, I17, I10
- Proposal: For wait and timeout codes, attach the per-check results
  (which actionability or wait condition failed, last observed state)
  as structured data. Diagnosability grows without growing the code
  set.
- Evidence: Playwright Auto-waiting (URL in Q17, accessed 2026-11-27):
  up to six actionability checks run per action, yet failures collapse
  into a single TimeoutError type with the diagnostics carried in the
  call log rather than in distinct codes. This is the standing
  counterexample to taxonomy maximalism.
- Proof to promote: one wait-timeout on the a11y lane carrying the
  per-check results; success criterion: the failing check is
  identifiable from the structured attachment alone, without reading
  message text.
- Status: QUEUED

### Q33. Enforce strict Marionette sequencing; route parallel work to BiDi

- Kind: REFINES
- Touches: Marionette lane clients (zen_live.py, geckodriver usage)
- Proposal: Every Marionette client sends commands strictly one at a
  time and waits for each response; any pipelining or fire-and-forget
  is a protocol violation, not a style issue. Parallel work belongs on
  BiDi, which supports it by design.
- Evidence: Marionette Protocol, Firefox Source Docs
  (https://firefox-source-docs.mozilla.org/remote/marionette/Protocol.html,
  accessed 2026-11-27): "Clients must send commands one at a time.
  After sending a command, wait for its response before sending the
  next one"; "If you need to run commands in parallel, use WebDriver
  BiDi instead. Its protocol supports this by design."
- Proof to promote: code audit of the fixed zen_live.py plus a stress
  run interleaving two command streams; success criterion: the client
  serializes them (one in flight at any time, verified in the log),
  and no response is attributed to the wrong command.
- Status: QUEUED

### Q35. Branch on standard WebDriver error codes in Marionette clients

- Kind: REFINES
- Touches: Marionette lane; same rule as Q3 and Q20 for the Zen lane
- Proposal: Marionette clients branch on the error field's standard
  WebDriver JSON error code, never on message text, which is not
  guaranteed.
- Evidence: Marionette Protocol (URL in Q33, accessed 2026-11-27):
  the error field is "guaranteed to be one of the JSON error codes as
  laid out by the WebDriver standard".
- Proof to promote: client test with a server response whose message
  text is deliberately misleading while the code is unambiguous;
  success criterion: the client takes the code's branch.
- Status: QUEUED

### Q36. Name the invalidating events for snapshot-qualified refs

- Kind: REFINES
- Touches: I3 (ADOPT, additive form)
- Proposal: I3 should state which events invalidate a snapshot's refs,
  not just qualify refs by snapshot. The AT-SPI analogues of document
  change are window close, application exit and tree rebuild.
- Evidence: MDN, Stale element reference
  (https://developer.mozilla.org/en-US/docs/Web/WebDriver/Reference/Errors/StaleElementReference,
  accessed 2026-11-27): on navigation, "all web element references to
  the previous document will be discarded along with the document."
- Proof to promote: I3 implementation test closing a window and
  exiting an app, then using a prior snapshot's ref; success
  criterion: the ref resolves to the invalidation outcome, not to a
  live look-alike.
- Status: QUEUED

### Tier D. New capability and process items

### Q25. Collection.GetMatches as the find engine

- Kind: NEW IDEA
- Touches: locator layer (supports I14 find-style locator)
- Proposal: Where the toolkit implements Collection, the find-style
  locator becomes one call with application-side filtering (match by
  states, attributes, interfaces, roles), falling back to the walk
  where it does not. Probe per toolkit, as with GetItems.
- Evidence: LibreOffice accessibility thread (URL in Q5, accessed
  2026-11-27): with Collection "the bus overhead would be lower as
  it's just one call to the interface method, then the filtering
  happens on the application side and the result is returned in a
  single D-Bus reply", versus a round trip per navigation call.
  Atspi.MatchRule documentation
  (https://gnome.pages.gitlab.gnome.org/at-spi2-core/libatspi/class.MatchRule.html,
  read via search text 2026-11-27) defines the matching surface.
- Proof to promote: variant (v) of the U4 measurement; success
  criterion: on a toolkit that implements Collection, a find query
  completes in one D-Bus call with results matching the walk's find
  on the same tree, recorded per toolkit in the probe ledger.
- Status: QUEUED

### Q26. Event-maintained delta snapshots

- Kind: NEW IDEA
- Touches: I5, I15
- Proposal: After a first GetItems snapshot of a window, maintain it
  from AddAccessible and RemoveAccessible signals and
  property-carrying events, so repeat observations of the same window
  cost deltas, not full re-walks. This is the protocol's designed
  lifecycle; our current model re-walks from zero every time. The
  GetItems starting point is gated per toolkit, as in Q9: where
  GetItems is unavailable or returns empty, the fallback is
  event-maintained deltas maintained over a live walk instead of a
  bulk snapshot.
- Evidence: org.a11y.atspi.Cache documentation (URL in Q7, accessed
  2026-11-27): "Assistive tech should try to do a bulk query of all
  the objects in a new window with the GetItems method, and then
  update them dynamically from the AddAccessible and RemoveAccessible
  signals." Lane R3 also records the 2013 at-spi2-core change (bug
  708387) making events carry a list of properties to avoid follow-up
  calls (read via search text).
- Proof to promote: observe the same window twice across a known UI
  change; success criterion: the second observation's D-Bus call
  count is at most 10 percent of the first (a pre-registered
  threshold set by this queue as its own choice, not sourced), and
  the delta-maintained tree matches a fresh full walk on the same
  state.
- Status: QUEUED

### Q27. Fetch extents late, only for the final candidate set

- Kind: REFINES
- Touches: I10, I14
- Proposal: Budget extents as the known-expensive field: fetch them
  late, only for the final candidate set after filtering, never per
  visited node in the walk's inner loop.
- Evidence: Mike Gorse, 2013 (URL in section 1, U4; accessed
  2026-11-27): "extents are not cached, so a significant number of
  round-trip calls are needed in order to fetch extents for many
  different objects". Chrome for Developers, "Improving the
  performance of Chromium accessibility"
  (https://developer.chrome.com/blog/chromium-accessibility-performance?hl=en,
  accessed 2026-11-27): bounding-box serialization dominated cost,
  with a focus-links test improving about 1618 percent when bounding
  boxes were removed.
- Proof to promote: walk variant in the U4 measurement with extents
  deferred; success criterion: D-Bus call count drops by at least 30
  percent against variant (i) on the bench application (a
  pre-registered threshold set by this queue), wall time does not
  regress, and no candidate that needed extents for the final
  decision lacks them.
- Status: QUEUED

### Q28. Known-position child indexing as a locator fast path

- Kind: REFINES
- Touches: locator layer (I14 family)
- Proposal: A recorded index path is a legitimate fast-path hint under
  a verified fallback walk: try the known child position first, verify
  the result against the recorded predicate, and fall back to the full
  search on any mismatch.
- Evidence: Pitivi dogtail commit message
  (https://mail.gnome.org/archives/commits-list/2014-April/msg00628.html,
  read via search text 2026-11-27): known-position child indexing used
  as "a performance hack to very quickly get the widgets we want, by
  using their known position instead of searching" (dogtail material
  collected in lane R3, source 15).
- Proof to promote: locator bench on a stable fixture app; success
  criterion: the fast path resolves in fewer D-Bus calls than the
  search path, and a deliberately shifted tree produces a predicate
  mismatch and a fallback, never a silent wrong target.
- Status: QUEUED

### Q29. Add MOZ_LOG RDP packet tracing to the RDP toolkit debug mode

- Kind: NEW IDEA
- Touches: scripts/zen-rdp (Task 3 review follow-up)
- Proposal: Add MOZ_LOG="devtools_rdp:3" packet tracing to the RDP
  toolkit's debug mode. It would have shortened the Task 3 review's
  double-execute investigation by showing the actual packet flow.
- Evidence: Remote Debugging Protocol, Firefox Source Docs
  (https://firefox-source-docs.mozilla.org/devtools/backend/protocol.html,
  accessed 2026-11-27): packet tracing is available via
  MOZ_LOG="devtools_rdp:3"; the same page confirms noSuchActor is a
  real protocol error name ("If a packet is directed to an actor that
  no longer exists, the server sends a packet... "error":"noSuchActor""),
  which is exactly why matching it inside page exception text is
  unsafe.
- Proof to promote: reproduce the double-execute scenario with
  tracing on, pinned to a preserved pre-fix revision of the RDP
  toolkit or a synthetic fault-injection fixture reproducing the
  double-execute path, so the proof stays executable after the defect
  is fixed; success criterion: the trace shows the duplicate
  execution's packet sequence, and the trace file is attached to the
  debug log.
- Status: QUEUED

### Q30. Track the Firefox base version in Zen release notes

- Kind: NEW IDEA (process)
- Touches: all browser lanes
- Proposal: A one-line check per Zen update: "Firefox base changed
  from X to Y; check Marionette and BiDi changelogs for Y." The Zen
  release notes carry no automation notes, so the Firefox base
  version is the only reliable predictor of protocol behaviour; every breaking change
  found in lane R4 (Fx63 callback removal, Fx138 system-access gating,
  Fx141 CDP removal, Fx148 chrome scope) arrived via a Firefox version
  bump.
- Evidence: Zen Browser release notes
  (https://zen-browser.app/release-notes/, accessed 2026-11-27): Zen
  1.24.3b entry states "Updated to Firefox 160.0.1"; a search of the
  opened page found no mention of Marionette, RDP, or automation or
  debug flags at all.
- Proof to promote: process adoption, verified by the next Zen update
  producing a changelog-check note in the lane log before any client
  is run against the new build; success criterion: the note exists
  and names the Firefox base delta.
- Status: QUEUED

### Q31. Adopt the BiDi network module for agent observability

- Kind: NEW IDEA
- Touches: BiDi lane (zen_cli.py, dedicated agent profile)
- Proposal: Use the BiDi network module (header injection plus data
  collectors that now include request post data) for request capture
  on the agent profile, with a documented, versioned API, instead of
  RDP network actors. Captured post data must pass through the I22
  secure-field redaction before anything is written to a log, and
  capture on the agent profile is scoped to fixture traffic unless
  that redaction is in place.
- Evidence: Firefox WebDriver Newsletter 146
  (https://fxdx.dev/firefox-webdriver-newsletter-146/, accessed
  2026-11-27): network.setExtraHeaders implemented, and network data
  collectors extended to the request data type (request post data).
- Proof to promote: on the agent profile, capture one request with
  its post data through BiDi collectors during a fixture task;
  success criterion: the captured record matches the request the
  fixture sent, headers and post data, in the log.
- Status: QUEUED

### Q32. Use BiDi emulation commands for deterministic agent-profile testing

- Kind: NEW IDEA
- Touches: BiDi lane (test setup)
- Proposal: Use emulation.setNetworkConditions (offline) and
  emulation.setLocaleOverride for deterministic agent-profile testing,
  replacing any ad-hoc profile prefs for offline or locale simulation.
- Evidence: Firefox WebDriver Newsletter 150
  (https://fxdx.dev/firefox-webdriver-newsletter-150/, accessed
  2026-11-27): emulation.setNetworkConditions adds offline emulation.
  Newsletter 146 (URL in Q31): emulation.setLocaleOverride also
  overrides navigator.language(s).
- Proof to promote: one fixture task run offline via the emulation
  command and one under a locale override; success criterion: the
  page observes offline state and the overridden locale, both
  recorded, with no profile pref edits involved.
- Status: QUEUED

### Q34. Design the BiDi lane around exactly one session per Firefox instance

- Kind: REFINES
- Touches: BiDi lane (multi-agent design)
- Proposal: Firefox rejects a second session.new while a session is
  active, so multi-agent designs need one browser instance (or user
  context) per agent, not session multiplexing.
- Evidence: MDN, session.new
  (https://developer.mozilla.org/en-US/docs/Web/WebDriver/Reference/BiDi/Modules/session/new,
  accessed 2026-11-27): "In browsers that don't support multiple
  sessions (e.g., Firefox), sending session.new when a session is
  already active results in an error response."
- Proof to promote: design rule recorded in the BiDi lane's
  documentation, plus one test: a second session.new against a live
  instance returns the documented error and the first session is
  unaffected; success criterion: the error is the documented one and
  no state is lost.
- Status: QUEUED

### Q10. BiDi chrome-scope spike as the RDP exit ramp

- Kind: NEW IDEA
- Touches: RDP lane succession; relates to I23 (lane conformance)
- Proposal: On a throwaway Zen profile, launch with
  --remote-allow-system-access and test browsingContext.getTree with
  moz:scope "chrome" plus script.evaluate in a chrome context against
  a read-only Zen internals query (the pinned and folder dump is the
  natural candidate). If it works, Zen internals reads move from an
  internal protocol to the standards-track one, incrementally,
  read-only first.
- Evidence: Firefox WebDriver Newsletter 148
  (https://fxdx.dev/firefox-webdriver-newsletter-148/, accessed
  2026-11-27): "Added initial support for interacting with the
  browser's chrome scope... browsingContext.getTree now accepts the
  vendor specific moz:scope parameter... These contexts can be used
  with script.evaluate and script.callFunction to execute privileged
  JavaScript with access to Gecko APIs." Zen 1.24.3b is built on
  Firefox 160.0.1 (Zen release notes,
  https://zen-browser.app/release-notes/, accessed 2026-11-27), so
  the feature is version-wise present. Status of the capability on
  Zen itself: UNPROVEN until the spike runs.
- Proof to promote: the spike itself, on clone2's VM under the
  measurement rule; success criterion: a chrome context is returned
  and a read-only pinned and folder dump completes through BiDi with
  results matching the Marionette fixed-client dump on the same
  throwaway profile.
- Status: QUEUED

### Tier E. Confirmations of approved design (proceed as approved)

### Q38. Closed code set, branching on code only

- Kind: CONFIRMS
- Touches: I1
- Proposal: Keep the I1 set closed and keep message text out of all
  branching logic, with Q19's fallback and extension range as the
  growth mechanism.
- Evidence: gRPC's 17 codes and WebDriver's single normative table
  (URLs in Q18 and Q19, accessed 2026-11-27) show a small closed set
  is workable at scale; RFC 9457 (URLs in Q20) states consumers must
  not parse the detail member.
- Proof to promote: not applicable, already approved (I1, in the
  study's do-first list); the confirmation is recorded so the rollout
  does not relitigate it.
- Status: QUEUED

### Q39. The five-state delivery disposition

- Kind: CONFIRMS
- Touches: I1, I7
- Proposal: Keep the five-state disposition axis (unknown,
  not_delivered, delivery_uncertain, delivered_unverified,
  delivered_verified) separate from the error code, with Q2 as the
  mechanism that resolves the uncertain state and Q18 as the retry
  guidance layer.
- Evidence: gRPC status codes guide (URL in Q18, accessed 2026-11-27):
  DEADLINE_EXCEEDED "may be returned even if the operation has
  completed successfully", proving delivery_uncertain is a state real
  systems must name.
- Proof to promote: not applicable, already approved (I1 and I7,
  adopted in the study).
- Status: QUEUED

### Q40. Zen lane first, with a compat shim for major breaks only

- Kind: CONFIRMS (with the versioning clause from lane R1)
- Touches: I1
- Proposal: Ship the envelope on the Zen lane first and shim the rest,
  and state the additive-evolution rule in the contract: minor
  versions are purely additive, consumers ignore unknown members and
  degrade unknown codes (Q19), and the shim is reserved for genuine
  major-version breaks.
- Evidence: RFC 9457 (URLs in Q20, accessed 2026-11-27): "Clients
  consuming problem details MUST ignore any such extensions that they
  don't recognize." WebDriver BiDi (URL in Q3): every message type
  ends with an Extensible map. WebDriver's own history is the
  precedent: a stable classic core, then BiDi layering beside it.
- Proof to promote: consumer test on an envelope carrying an unknown
  extension member; success criterion: the consumer processes the
  envelope normally and ignores the member.
- Status: QUEUED

### Q41. Strict exactly-one-match semantics and the unique-at-capture precondition

- Kind: CONFIRMS
- Touches: I2 pilot
- Proposal: Keep the converged I2 form: ambiguity at act time is a
  refusal, never a silent pick, and refs are captured only from unique
  matches. No design change; the evidence supports the converged form.
- Evidence: Playwright Locators (URL in section 1, U3; accessed
  2026-11-27): strict locators throw if more than one element matches,
  and first() or nth() escapes are documented as not recommended.
  Falkowski (accessed 2026-11-27): without a refusal path, engines
  guess, including a 100 percent first-match bias on repeated rows.
- Proof to promote: not applicable, already approved (the I2 pilot
  as specified in the study); the pilot itself is the measurement.
- Status: QUEUED

### Q42. Snapshot-qualified refs match the platform model

- Kind: CONFIRMS
- Touches: I3
- Proposal: Keep I3's additive form (accept qualified refs, warn on
  bare refs, reject only after a deprecation window, legacy snapshots
  grandfathered). Scoping refs to a snapshot and a window is the
  WebDriver invalidation boundary made explicit.
- Evidence: W3C WebDriver (URL in Q11, accessed 2026-11-27): element
  references live in a per-session map; MDN (URL in Q36): references
  to a document are discarded wholesale on navigation.
- Proof to promote: not applicable, already approved (I3, in the
  study's do-first list); Q36 names the invalidating events to state
  alongside it.
- Status: QUEUED

### Q43. I5 accounting and the tri-state outcome model

- Kind: CONFIRMS
- Touches: I5 (accounting half, adopted), I15
- Proposal: Proceed with per-node cut accounting and outcomes that
  distinguish unknown from absent. "Not observed" is genuinely
  ambiguous between absent, stale and timed out, and the accounting
  is the correct response. Boundary from the study: the confirmed I15
  half is the root-level incomplete flag; per-node unknown recording
  lives in the I5 accounting (Q6), and per-element tri-state output
  was rejected by the study and is not confirmed here.
- Evidence: lane R3, sources 8 and 9 (Gorse 2011, URL in Q8; the
  2013 caching thread, read via search text): cache staleness is a
  documented failure mode.
  Atspi.set_timeout documentation (URL in section 1, U4): a single
  call can burn 800 ms before timing out.
- Proof to promote: not applicable, already approved (the I5
  accounting half, adopted in the study); Q5 and Q6 harden its worst
  cases.
- Status: QUEUED

### Q44. I14 bench-gating: extents and query ungate separately

- Kind: CONFIRMS
- Touches: I14 pilot
- Proposal: Keep extents and query as separately bench-gated ungates.
  Extents are the one field both ecosystems independently identify as
  the expensive one.
- Evidence: Gorse 2013 (extents uncached, URL in section 1, U4) and
  Chromium accessibility performance post (bounding-box cost
  dominance, URL in Q27), both accessed 2026-11-27.
- Proof to promote: the I14 bench re-run under the study's bench
  criterion, reproduced here in full: re-run the observation timing
  benches first; ungate query() only; extents stays opt-in until its
  per-element cost is measured; the bench must measure coverage too,
  not only cost (which widget classes silently report no extents);
  query() and the extents-default ungate separately.
- Status: QUEUED

### Q45. Probe-before-pilot sequencing, with per-toolkit ledger rows

- Kind: CONFIRMS
- Touches: I8 (probes and ledger, adopted)
- Proposal: Keep probing per application class before committing
  engineering, and record each variant's per-toolkit result in the
  probe ledger. Toolkit variance is real, and published walk numbers
  have already been corrected once on re-measurement, so a number
  measured on one toolkit or one machine does not transfer.
- Evidence: hyprsay verification block (URL in section 1, U4;
  accessed 2026-11-27): an independent re-measurement corrected a
  claimed 0.22 to 0.24 ms per element to 0.322 to 0.334 ms per
  element, and top-level enumeration from a claimed 2.3 ms to a
  measured 18.76 ms. Qt GetItems stub: Q9.
- Proof to promote: not applicable, already approved (I8 probes and
  ledger, in the study's do-first list); the U4 measurement
  (section 1) is its first full exercise.
- Status: QUEUED

### Q46. Keep RDP primary for live-profile Zen internals, for now

- Kind: CONFIRMS (the post-switch position)
- Touches: RDP lane; Q10 is its named successor path
- Proposal: No opened source shows any other current route to
  parent-process browser objects on a running profile; BiDi chrome
  scope is explicitly initial support. RDP stays primary until Q10's
  spike proves an alternative, and every RDP dependency is recorded
  as replaceable (see correction W20).
- Evidence: Firefox WebDriver Newsletter 148 (URL in Q10, accessed
  2026-11-27): chrome-scope support is initial, and "Other commands
  do not yet support chrome contexts, but support will be added
  incrementally."
- Proof to promote: not applicable, already approved (the
  post-switch position recorded in the study); this is the standing
  position the Q10 spike is designed to retire.
- Status: QUEUED

## 3. Corrections: what our current direction gets wrong

For the integration team's attention. Each item names the evidence;
items already fixed by a queue entry name that entry.

- W1. A closed set with no extension path and no unknown fallback
  contradicts how both WebDriver generations evolved. The classic
  table grew new codes over time, and BiDi then added about 17 more
  in a namespaced layer. If I1 ships frozen with neither, the first
  new lane (AT-SPI) or the first genuinely new failure mode breaks
  the contract instead of extending it. Fixed by Q19. Evidence: lane
  R1, sources 1 and 3 (URLs in Q19 and Q3).
- W2. disposition.retry as "safe only when not_delivered" is too
  coarse in both directions. Retry guidance has at least three values
  (retry the call, retry higher up, never until fixed), and safety
  depends on the operation's idempotency, not only on delivery state:
  not_delivered via invalid argument is not safe to retry unchanged,
  and some delivered-state failures are safe to retry at a higher
  level after re-observation. Fixed by Q18. Evidence: gRPC status
  codes guide (URL in Q18), including UNAVAILABLE being "not always
  safe to retry non-idempotent operations".
- W3. Five disposition states name the uncertainty but provide no way
  to resolve it. Nothing in the sources supports adding more states
  as the remedy; Stripe resolves the same uncertainty mechanically,
  with keys and stored outcomes. Without Q2, callers are left guessing
  with a fancier vocabulary, and our own pin-race evidence shows the
  executor itself can be unsure which of two racing operations
  landed. Fixed by implementing Q2's stored-outcome lookup in I1
  and I7. Evidence: lane R1, section 3, item 3.
- W4. Versioning by contract number with a strict-equality shim
  fights the additive-evolution rule. RFC 9457's MUST-ignore rule,
  BiDi's Extensible maps and gRPC's unknown-code conversion all point
  the same way: minor versions must be purely additive. Fixed by Q40.
- W5. Any consumer that branches on message text is wrong by the
  sources and by our own incident record. RFC 9457 forbids parsing
  the detail member; our RDP toolkit review proved a live double
  execution caused by matching the string "noSuchActor" in error
  text. Any I1 consumer or shim still pattern-matching message text
  is a defect to remove, not a style issue. Fixed structurally by Q3,
  Q20 and Q35.
- W6. Predicate re-identification accepts look-alikes; the field's
  restore rule rejects them. UiAutomator2 accepts a re-found element
  only if it is "the same view, not a new one that looks the same".
  I2 deliberately accepts a recreated look-alike when the predicate
  matches uniquely. This is a real semantic difference: our "same
  element" means same description, theirs means same node. The pilot
  must state this explicitly and include the case where it bites: a
  destroyed control replaced by a different control with the same
  name and role in the same container. Evidence: Appium write-up (URL
  in Q11).
- W7. View recycling defeats node and path identity silently. A
  stored reference can point at a view that now shows different data,
  with no error raised, because the view never detached. The AT-SPI
  analogue is toolkit list and grid view reuse. Q16 puts a
  scrolling-list scenario in the pilot to probe it. Evidence: Appium
  write-up (URL in Q11).
- W8. Holding references at all is the anti-pattern in the Playwright
  model; the fix is storing the query. This supports the DOM lane's
  no-refs design and pressures I2 toward storing the full capture
  predicate as a re-runnable query rather than as comparison evidence
  against a held object. Where I2 still holds the accessible object
  (Q12's defunct check), that hold is a probe, not an identity claim,
  and the pilot text must say so. Evidence: Playwright Locators and
  Selenium error documentation (URLs in section 1 and Q17).
- W9. Position is not identity. Falkowski's shuffle result: ordinal
  alignment produced nearly-always-right guesses on unanswerable
  items until the list was shuffled, at which point the engines
  refused every time. Any use of child index or sibling order in
  re-identification, even as a tie-breaker, imports this leak. Fixed
  by Q13's control. Note the boundary with Q28: an index path is a
  locator fast-path hint under predicate verification, never identity
  evidence.
- W10. The accessible name is mutable, and sometimes empty by
  construction. accName is computed from live markup; name-from-content
  changes when content changes; roles whose nameFrom property is
  prohibited have no name at all. Name evidence therefore needs three
  states (match, mismatch, not computable), and a not-computable name
  must count as neither a match nor a mismatch. Evidence: W3C
  Accessible Name and Description Computation 1.2
  (https://www.w3.org/TR/2026/WD-accname-1.2-20260311/, accessed
  2026-11-27).
- W11. A unique match can still be the wrong element. Strictness
  bounds but does not eliminate the risk: when the original is gone
  and exactly one look-alike remains, a unique predicate match is a
  wrong act with no ambiguity signal. The pilot's scenario list must
  include target-deleted-with-one-look-alike-present. Evidence:
  Selenium's warning that re-finding by a stored description "can
  cause problems if the locator you're using references a different
  element (and not the one you want) after the page has changed"
  (URL in Q17); Falkowski's missing-target cases are exactly this
  shape.
- W12. The 500-node cap silently amputates the trees the walk pilot
  targets. Real browser and Electron pages measure 1,554 to 1,826
  nodes, so on dense applications the cap cuts most of the tree before
  depth or time become the binding constraint. The cap is defensible
  as a budget; it is wrong as a silent default, which is what the
  adopted I5 accounting half fixes by recording the cut. Evidence:
  hyprsay verification block (URL in section 1, U4).
- W13. The 100-children-per-node cap only protects if checked before
  the call. A single container can expose 2^31 children and
  GetChildren can freeze; a cap applied to the reply does not bound
  the cost of producing it. Fixed by Q5. Evidence: LibreOffice thread
  (URL in Q5).
- W14. The 2 s budget ignores the 800 ms default per-call timeout.
  Two or three slow or defunct nodes consume the entire budget in
  timeouts, and the walk then reports a truncated tree whose
  truncation cause is timeouts, not size. Per-call timeout and budget
  must be designed together. Fixed by Q6. Evidence: Atspi.set_timeout
  documentation (URL in section 1, U4).
- W15. Depth accounting spends budget on transparent containers.
  Chromium trees interleave anonymous wrapper nodes (the study's own
  Lane B found wrapper skipping changed ref-able nodes from 4 to 54
  to 83 at depth 10), so depth consumed by wrappers is depth not
  reaching controls. Depth accounting should distinguish structural
  from semantic depth. The walk pilot's measurement must record
  structural and semantic depth separately, and Q7 owns this fix.
  Evidence: lane R3, section 4, citing the study and the hyprsay
  measurements.
- W16. The 80-element return cap conflates visited with returned.
  Combined with the node cap, a snapshot can be simultaneously
  complete-as-visited and misleading-as-returned. The sources do not
  set our numbers, but the completeness hazards all point the same
  way: the numbers matter less than stating, per node, where and why
  the snapshot stopped, which is the adopted I5 accounting half.
  Evidence: lane R3, section 4.
- W17. Any lingering CDP assumption is wrong. CDP was removed in
  Firefox 141; on current Firefox and Zen, --remote-debugging-port
  serves WebDriver BiDi only. Tooling, docs, or fallback plans that
  mention CDP against current Zen describe a protocol that no longer
  exists in the binary. Instruction: audit tooling, docs and
  fallback plans, remove CDP paths, and replace any still-needed
  function with the BiDi equivalent. Evidence: MDN Firefox 141
  release notes
  (https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/141,
  accessed 2026-11-27).
- W18. Setting system access via moz:firefoxOptions is wrong on
  current geckodriver, and the remote.system-access-check.enabled
  preference is gone. The preference was temporary (Firefox 138) and
  removed in Firefox 141; any profile template or doc that sets it is
  inert at best. Fixed by Q1 (flag) and Q47 (env var). Evidence:
  geckodriver CHANGES.md (URL in Q1); Remote protocol preferences,
  Firefox Source Docs
  (https://firefox-source-docs.mozilla.org/remote/Prefs.html,
  accessed 2026-11-27).
- W19. Treating Marionette as parallelizable is wrong. The protocol
  doc forbids it in terms and names the failure modes (response never
  arrives, error reported for the wrong command). Concurrency belongs
  on BiDi. Fixed by Q33. Evidence: Marionette Protocol (URL in Q33).
- W20. Treating RDP as a stable public API is wrong. It is Mozilla's
  internal DevTools protocol; actors have limited lifetimes tied to
  the connection, and nothing opened gives it a versioning or
  stability commitment. It is the right tool today for live-profile
  Zen internals, but every RDP dependency should be recorded as
  replaceable, with BiDi chrome scope (Q10) as the named successor.
  Evidence: Remote Debugging Protocol, Firefox Source Docs (URL in
  Q29).
- W21. Trusting the zen_live.py unit tests as wire-format evidence is
  wrong. R17 showed the fake server encodes an unprefixed greeting
  and short command names; the sources show the real server does the
  opposite on both counts. Green tests against a wrong fake are how
  four stacked defects survived. Fixed by Q4.
- W22. Eviction masquerades as staleness. Platforms disagree on the
  error reported for an evicted reference (no such element on
  Android, stale on iOS), and our own RefMap pruning would mix
  eviction with genuine staleness in the I2 pilot's metrics,
  corrupting the refusal and staleness rates the pilot exists to
  measure. Fixed by Q11's eviction outcome. Evidence: Appium
  write-up (URL in Q11).

## 4. UNVERIFIED quarantine

The following items appeared in the lanes but could not be opened or
verified. They are listed here so they are visible, and explicitly not
relied on: no queue entry, answer, or correction above rests on any of
them.

- gRPC retry service config details (retryPolicy,
  retryableStatusCodes, backoff parameters) and the RetryInfo detail:
  the official retry guide was not opened in lane R1. Q23 rests on RFC
  9457 only.
- Engineering write-ups on exactly-once delivery being impossible (Two
  Generals) and the at-least-once plus idempotent-processing pattern:
  seen in search results in lane R1, none opened. The delivery claims
  in this queue rest on the opened gRPC and Stripe sources.
- Appium's internal error-mapping layer (proxy error unwrapping,
  conversion of unknown thrown values to unknown error): seen only in
  a secondary code summary in lane R1 search results. Only Appium's
  published BiDi documentation is cited (Q22).
- BiDi module-specific error codes beyond the core list: the core
  ErrorCode production and the specification's section 3.5 list were
  read in lane R1; a full sweep of every module fragment was not
  performed.
- Healenium empirical paper (International Journal of Applied
  Mathematics 38(12s), 2025), claiming self-healing reduced
  locator-related failures by 40 to 60 percent and maintenance effort
  by 30 to 50 percent: seen only as a search-result snippet in lane
  R2, never opened. UNVERIFIED.
- TestNav-Agent paper, claiming a flaky failure rate reduction from
  13.5 to 4.1 percent across 100 runs and element-location failures
  down 62.4 percent in dynamic pages: seen only as a search-result
  snippet in lane R2, never opened. UNVERIFIED.
- ScrollTest's 68 percent figure (self-healing test selectors): read
  via search-result text in lane R2, not opened in full; the author
  states the figure is not from a peer-reviewed study (an audit of 34
  setups). Only the false-pass concept is used in this queue, not the
  figure.
- A 2003 gnome-accessibility-devel mailing-list post on Accessible
  pointer reuse after unref: historical context only in lane R2, not
  current AT-SPI2 D-Bus semantics. Not used as evidence.
- at-spi2-core GitLab issue 142 (referenced by the LibreOffice thread
  cited in Q5): returned an access-denied page on
  open in lane R3. Nothing rests on it beyond the thread's reference.
- The org.a11y.atspi.Collection D-Bus specification page itself was
  not separately opened in lane R3, and claims about Orca internals
  beyond its sources 3, 8 and 9 are not relied on. Q25 rests on the
  LibreOffice thread and the Atspi.MatchRule class documentation.
- Whether the laptop launcher (zen-human) sets
  MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1: no web source can answer this; it
  needs the laptop probe already owed from R17. See Q47.
- Whether Zen 1.24.3b's build actually exposes BiDi moz:scope chrome
  contexts: version-wise it should (Firefox 160 base, feature landed
  in the Firefox 148 cycle), but this is UNPROVEN until the Q10 spike
  is run on a throwaway profile.
- Zen documentation beyond the release-notes page (docs site, GitHub
  wiki) was not opened in lane R4; the "no automation contract"
  finding in Q30 covers the release notes only.

No personal information in this document.
