# Independent review: integration-20261127 branch (2026-11-27)

Reviewer: clone2. Independent review only; no code was changed by
this review. Branch reviewed: integration-20261127 at tip 97d22c70,
read in the scratch worktree ~/workspace/integration-review-wt.

Scope: items I1, I3, I5, I8, I9, I10, I16, I17, I22, M2, M17, as
landed on the branch and recorded in
improvements/integration-phase-20261127.md on that branch.

Method: three review lanes read the landed code against the
approved designs in improvements/agent-desktop-comparison-20261127.md
(the study), the refinements in improvements/idea-queue-20261127.md,
and the do-first definitions in
improvements/bottleneck-study-20261127.md. Tests were run on
clone2's VM where runnable (lanes A and B, plus a direct rung3-ci
run by clone2). Lane C operated under an execution restriction on
the fetched branch content and was limited to plain file reading;
its test log says so plainly, and branch-recorded figures it cites
are labelled as branch claims, not reproduced facts. Ponytail was
the judging standard throughout: smallest complete change, no
unrequested abstraction, no cut validation.

Headline: every scoped item landed in its approved form, and the
rejected or pilot halves correctly stayed out. No BLOCKING
findings. Seven MAJOR findings: two places where the I1 envelope
still lets message text or an unchecked claim decide what a
consumer believes (A1, A2), one redaction hole on the exact path
OAuth tokens travel (C1), two approved behaviours that the landed
code does not actually perform (F7, F11), and two holes in the
M17 test tooling and its CI coverage (C-4, C-8). Thirty-three
MINOR findings are listed in section 3.

## 1. Summary verdicts

| Item | Form verdict | BLOCKING | MAJOR | MINOR |
|------|--------------|----------|-------|-------|
| I1 error envelope, Zen lane | Landed as approved (envelope v1, exit-code split, compat shim) | 0 | 2 (A1, A2) | 4 (A3 to A6) |
| I3 snapshot-qualified refs | Landed exactly as approved (additive form) | 0 | 0 | 4 (B1 to B4) |
| I5 accounting half | Landed as approved; walk half correctly absent | 0 | 0 | 3 (F1 to F3) |
| I8 probes and probe ledger | Split landed as approved; mandatory A/B gate correctly refused | 0 | 0 | 2 (F4, F5) |
| I9 capability matrix in doctor | Adopted half landed; unified interface correctly absent | 0 | 0 | 1 (F6) |
| I10 auto-wait half | Shape landed as approved; one approved condition (enabled) not actually polled | 0 | 1 (F7) | 2 (F8, F9) |
| I16 DOM-rect debug artifact | Adopted half landed exactly; a11y overlay correctly absent | 0 | 0 | 1 (F10) |
| I17 post-action wait flags | Landed after I1 as approved; one R2 condition (terminal fail-fast) not landed | 0 | 1 (F11) | 2 (F12, F13) |
| I22 secure-field redaction | Landed as the approved narrowed contract | 0 | 1 (C1) | 5 (C2 to C6) |
| M2 one-pass seal wrapper | Conforms to the study definition | 0 | 0 | 3 (C-1 to C-3) |
| M17 sharded discover | Mechanism conforms; one substantive hole in shard mode | 0 | 2 (C-4, C-8) | 6 (C-5, C-6, C-7, C-9, C-10, C-11) |
| Total |  | 0 | 7 | 33 |

C-8 is a cross-cutting CI finding; it is counted on the M17 row
because the tests it leaves unrun are the M2 and M17 covering
tests. C-9 and C-10 are cross-cutting MINORs counted on the same
row for the same reason.

## 2. MAJOR findings

### A1 (I1). The error classifier branches on message text that embeds page-controlled exception text

Location: scripts/zen-rdp/rdp_client.py:150-176 (the _REFUSAL_MAP
needles and _classify_error), 820 and 824 (evaluate failure
raising), 870 and 874 (parent evaluate).

Evidence: the refusal needles are tested first, before the
evaluate branch, and evaluate failures raise RDPError carrying
the first 400 characters of the whole result packet, including
the page's own exception text. Proven on clone2's VM against the
worktree module: an evaluate exception whose text contains the
needle "pinned tab" classifies as (attach_failed, not_delivered,
safe) instead of (evaluate_failed, delivery_uncertain, unsafe).

Why it matters: a page can choose the code and disposition of
its own failure. A consumer that honours retry "safe" can be
talked into replaying a state-changing evaluate that actually
ran. Q38 confirms the design rule "keep message text out of all
branching logic"; the consumer side honours it, the producer
side does not. Not BLOCKING only because no in-repo consumer
auto-retries on disposition today; the envelope's own contract
invites exactly that consumer. The fix direction is typed error
origins instead of message substrings.

### A2 (I1). Navigate success is labelled delivered_verified, but navigate performs no delivery check

Location: scripts/zen-rdp/rdp_client.py:894, 931-938.

Evidence: after navigateTo is ACKed, navigate() sleeps 0.05 s
and attempts list_tabs() and get_target() inside a try/except
that swallows every exception. The re-read re-attaches target
identity; it never compares the resulting URL or tab state with
the requested destination, and its failure is silent. The
study's own evidence correction for I6 already established that
this re-read is identity re-attachment, not page-state
verification. The README repeats the overstatement ("navigate
polls to load").

Why it matters: the disposition axis is the thing I1 exists to
make honest. On that axis, navigate is delivered_unverified at
best until a URL comparison exists. Consumers making retry or
trust decisions from the label are reading a claim the code
does not back.

### C1 (I22). The URL redactor never redacts the fragment, where OAuth implicit-flow tokens live

Location: scripts/zen-rdp/rdp_client.py:345-361 (_redact_url).

Evidence: _redact_url partitions the fragment out of the query
and reattaches it verbatim, and test_redaction.py locks this in
as intended behaviour ("fragment preserved"). Fragment carriage
is the standard OAuth implicit-flow shape: tokens are delivered
after '#', not in the query. Proven on clone2's VM with a
synthetic callback URL: the fragment-carried token value passes
through _redact_url unchanged.

Why it matters: a tab snapshot or drive report can carry a live
token in the fragment while every query parameter is scrubbed.
The redaction looks complete from the query side and leaks on
the fragment side, on exactly the URL shape identity providers
produce.

### F7 (I10). Enabled is gated, not polled

Location: scripts/a11y.py:213 (resolve), 228 (wait_actionable).

Evidence: resolve() raises ValueError('element is disabled')
the moment SENSITIVE is absent, and wait_actionable calls
resolve() uncaught at the top of every iteration, so a
momentarily disabled element fails instantly instead of being
waited on inside the 1 s cap. The approved form says "poll
visible/enabled/stable", the commit message claims
"enabled+visible+stable extents", and the docstring's first
line says "poll until the element is enabled"; only visible
and extents stability are actually polled.

Why it matters: elements that enable asynchronously (buttons
enabling after validation, menu items enabling after a
selection) are a standard auto-wait case, and they get no
benefit from the wait as landed. The landed code does not do
one thing the approved form and its own commit message say it
does.

### F11 (I17). wait_for swallows terminal page states instead of failing fast

Location: scripts/zen-rdp/rdp_client.py:953-956 (wait_for).

Evidence: wait_for catches every exception from evaluate and
treats it as not-yet, with no distinction between a transient
context-destroyed error mid-navigation and a terminal state
(tab gone, session dead, actor gone for good). The behaviour is
tested only in its transient form
(test_envelope.py, test_wait_for_tolerates_transient_errors);
no terminal case exists because the behaviour does not.

Why it matters: on a terminal state the caller burns the entire
named budget and receives wait_timeout instead of the real
failure. That is the slow-failure shape the study's R2
condition on I17 was written to prevent, and the condition did
not land.

### C-4 (M17). Shard mode without --compare-serial can drop tests silently

Location: rung3-ci/test-discover.py, cmd_shard (the communicate
loop).

Evidence: each shard subprocess's stdout is parsed for
@@RESULT@@ lines and its stderr is discarded ("out, _ ="). If
a shard crashes, times out at the interpreter level, or a
module emits no results, the merged outcome map is simply
smaller, and nothing compares the merged total against the
discovered total that module_test_counts already computed in
the same process. The run prints a plausible-looking summary
and exits 0. The study's quarantine rule only bites when the
comparison is run, and the comparison is opt-in.

Why it matters: a test gate that can silently pass with fewer
tests than exist undermines every result it reports. This is
the same defect the items 1-5 gate redteam raised (its major
4); the coordinator's decision was to fix all five majors
before landing items 1-5 to main, and at this branch tip the
hole is still present in the code as read. The fix shape is
small: assert the merged total equals the discovered total,
and that every expected module contributed, failing loudly
otherwise, independent of --compare-serial.

### C-8 (cross-cutting). CI never runs the rung3-ci tools' own unit tests

Location: .github/workflows/rung3-checks.yml.

Evidence: the workflow runs verify-list, check-key-hash,
validate-ledger, lineage-check, arch-guard, and the hermetic
gate, but no step runs test-seal.py, test-test-discover.py,
test-arch-guard.py, or the other rung3-ci test files. The
tests exist and pass when run directly: clone2 ran them on
this VM at 2026-11-27 20:27 at the branch tip (test-seal.py 3
tests OK in 0.794 s, test-test-discover.py 5 tests OK,
test-arch-guard.py 2 tests OK; see the test log).

Why it matters: the covering tests for M2 and M17 rot
invisibly. A future edit can break seal.py or the shard
identity logic with CI green. This is the items 1-5 gate
redteam's major 5; the fix-before-landing decision covers it,
and it is still open at this tip. The fix is one workflow step.

## 3. MINOR findings

Thirty-three in total: lane A 13, lane B 11, lane C 9. Grouped
by item, with locations.

### I1

- A3 (rdp_client.py:140). The fifth delivery state, unknown,
  exists only in the vocabulary comment. No code path emits it,
  and the README delivery vocabulary lists four states. Q39
  confirms a five-state axis; the landed set is four-state in
  practice. Either emit unknown somewhere defensible or stop
  claiming the fifth state.
- A4 (rdp_client.py:1337-1340; argparse in main()). The README
  promises exactly one JSON envelope on stdout; two paths break
  it. Argparse failures exit 2 with usage text on stderr and no
  envelope at all. And tabs with --drive-report emits the
  success envelope, then calls c.write_drive_report()
  unguarded; if that write raises, a second, contradictory
  error envelope follows on stdout and the command exits 1
  after reporting success.
- A5 (rdp_client.py:170-227). Queue refinements still QUEUED
  and not landed: Q18 per-code caller-next-action (the retry
  axis is a single safe/unsafe pair and does not distinguish
  retry-the-same-call from retry-at-a-higher-level), Q19
  unknown-code fallback and namespaced extension range, Q20
  fixed title per code and per-occurrence instance id (an
  envelope still cannot be joined to the executor log and
  audit record by id, the correlation gap the Task 3 review
  found), Q21 typed data payload per code, Q23
  retry_after_ms. Q24 is partly served by I17's wait block.
  Recorded as a queue gap, not a design miss.
- A6 (rdp_client.py:148-149). The _REFUSAL_MAP header comment
  describes the tuples as (message substring, code, delivery,
  retry); they are pairs, with delivery and retry implied by
  membership. A stale comment on the contract's core table; the
  risk is confusion, not silent misbehaviour.

### I3

- B1 (a11y.py:265-266). In act(), validate_actions runs on the
  un-normalized actions before parse_ref strips qualification,
  contrary to the integration report's "normalized once before
  validation and execution". Harmless today because the
  validator only requires a non-empty string ref, but any
  future ref-format check in validate_actions would reject
  qualified refs before parse_ref can strip them.
- B2 (a11y.py:151-176). Q36 is not landed: nothing states
  which events invalidate a snapshot's refs (window close,
  application exit, tree rebuild). The only invalidation is
  the pre-existing 90-second age check. A ref used after its
  application exited fails deep inside resolve() with a generic
  error rather than a named invalidation outcome. A gap
  against the queue, not against the approved I3 form.
- B3 (a11y.py:163-168). Against a legacy snapshot, parse_ref
  accepts any 'prefix:ref' and silently discards the prefix,
  because there is no in-file id to verify against. Documented
  in the docstring and accepted by the approved
  grandfathering rule; recorded so the weakness is on the
  record.
- B4 (a11y.py:170-173). The bare-ref deprecation warning
  prints once per action inside act() batches, up to 32
  near-identical stderr lines for one call. Noise only; stdout
  is untouched.

### I22

- C2 (rdp_client.py:337-343). Parameter matching is exact-name
  against the 19-name set. Common variants pass through
  untouched: client_secret, auth_token, session_id,
  access-token, and camelCase refreshToken. Proven on clone2's
  VM with synthetic values. The Task 3 review already showed a
  name-list net failing open on real identity-provider URLs;
  this is the same shape, failing in the same direction.
- C3 (rdp_client.py:363-375, 388-389). _redact_report_urls
  redacts only dict keys named exactly "url". The report's own
  tab_diff emits from_url and to_url, safe today only because
  both diff inputs are pre-redacted snapshots; any future raw
  URL stored under another key name bypasses the walker
  silently.
- C4 (skill/cli-anything/zen.md:201, 209). Two rules numbered
  10 after this commit's insertion: the new secure-field rule
  and the pre-existing DOM-work rule, in the very file that
  carries the evaluate() out-of-scope rule.
- C5 (zen_dom.py:77; cdp.mjs:356; rdp_client.py:345-361).
  Three different redaction markers across the lanes:
  "[secure field value redacted]", "[redacted]", and
  "REDACTED" as the URL replacement value. No consumer or test
  can match one sentinel reliably.
- C6 (zen_dom.py:1446-1449). field_value's secure test covers
  type=password or a password-naming autocomplete only. A
  credential field rendered as type=text without a password
  autocomplete hint, a shape custom login forms use, returns
  its live value. The limit is inherent to the narrow
  contract, but the contract text does not state it.

### I5

- F1 (scripts/a11y.py:98-100, 110). The new complete flag can
  certify an incomplete walk: when items reaches the 80 cap in
  full mode, the loop breaks without setting truncated, and if
  pending is empty at that moment the snapshot reports
  complete=True even though the current node's children were
  never queued. The blind spot predates I5, but the accounting
  half's own flag now turns it into an explicit false claim.
- F2 (scripts/a11y.py:96). Per-node children_count and cut
  flags only reach the snapshot for elements that survive the
  items filter; in full mode a cut non-actionable container's
  accounting never appears, only the snapshot-level flags show
  the incompleteness. The integration report's "recorded in
  both modes" omits this caveat.
- F3 (scripts/a11y.py:90-91, 102). A failed get_child_count()
  is retried unguarded in the expansion branch; a second
  failure aborts the node's expansion (the item honestly keeps
  children_count=None), but the retry defeats the try/except's
  purpose and costs an extra D-Bus call per failing node.

### I8

- F4 (probes/ledger.jsonl rows 1-5). All five phase rows cite
  the same output, improvements/integration-phase-20261127.md,
  which is the phase report narrating the results, not the
  probe outputs themselves. The study's condition was that
  ledger rows cite probe outputs; the raw outputs are not in
  the repo, so no row in the ledger yet cites a raw output
  artifact and a reader cannot re-check a row without trusting
  the report.
- F5 (probes/validate-ledger.py:34-40). The path-existence
  check is skipped for any value containing a space, any
  spaceless value containing "/" is treated as a repo path,
  and the date format the README fixes as YYYY-MM-DD is not
  checked. Low stakes in an advisory tool, but the validator
  is the ledger's only quality control.

### I9

- F6 (scripts/cu.py:3196-3198). The zen_rdp operations list is
  ['tabs','eval','peval','navigate','probe'], omitting the
  report and bench subcommands rdp_client.py actually exposes.
  The list is a hand-maintained copy and will drift again
  unless it is derived or checked.

### I10

- F8 (scripts/a11y.py:231-235). Visibility requires both
  VISIBLE and SHOWING when both state types exist. SHOWING
  means on-screen, stricter than the approved "visible": an
  off-screen element the pre-I10 act path handled now waits
  1 s and fails with 'element is not visible'. The same
  tightening applies to ground(). No test covers
  VISIBLE-without-SHOWING.
- F9 (scripts/a11y.py:246-248). The deadline is checked only
  after a full resolve plus extents iteration, so on a slow
  bus one iteration can overshoot the 1 s cap. Standard
  polling shape, bounded impact.

### I16

- F10 (scripts/dom-rect-debug.py:35-47). Nit:
  rects_from_snapshot yields from the elements shape and then
  from the items shape with no exclusivity check, so a JSON
  carrying both keys would double-draw every rect. Real inputs
  carry one shape or the other; the cost is a messier debug
  image.

### I17

- F12 (scripts/zen-rdp/rdp_client.py:954). Each poll calls
  evaluate with a hardcoded timeout=5 regardless of the
  remaining budget, and the deadline is checked only after
  evaluate returns, so a single hanging evaluate can overshoot
  a 1 s --wait-timeout by up to about 5 s. The recorded live
  test used a fast false predicate and could not observe this.
- F13 (scripts/zen-rdp/rdp_client.py:179-181). wait_timeout
  classification keys on the message substring "wait_for
  timeout" in the message wait_for itself raises. Internal and
  currently consistent, but it is the message-text branching
  pattern the queue says to remove (Q3, Q35, W5): rewording
  the raise would silently reclassify wait timeouts as
  delivery_uncertain through the generic branch below it.

### M2

- C-1 (rung3-ci/seal.py). seal.py does not anchor the gate's
  requirements path: manifest-gate.py defaults --requirements
  to a relative path resolved against the caller's working
  directory, and seal.py forwards --requirements only when the
  caller supplies it, so a seal run from another directory
  makes the gate resolve a different (or missing) requirements
  file. Fail-closed, but the wrapper's behaviour silently
  depends on CWD. Fix shape: pass the anchored default through,
  as collect-evidence.py does.
- C-2 (rung3-ci/test-seal.py). Coverage stops at two of the
  four exit paths: the happy path, the collect-failure stop,
  and the separate gate re-run are covered; a snapshot-step
  failure, a gate failure over wrapper output, and the
  no-SNAPSHOT:-path branch are not. A coverage nit, not a
  conformance gap, since M2 claims no measured effect.
- C-3 (rung3-ci/seal.py, run_step). run_step pipes stdout but
  inherits stderr, so under captured output the two streams
  can interleave out of order. Cosmetic, no behavioural
  effect.

### M17

- C-5 (rung3-ci/test-discover.py, cmd_shard). Shard stderr is
  discarded even when --compare-serial is used, so when a
  mismatch is reported the crashing shard's traceback is
  unavailable for the written explanation the study requires.
- C-6 (rung3-ci/test-discover.py, cmd_shard).
  communicate(timeout=...) is applied per process sequentially
  after all shards launch, so later shards effectively get a
  longer timeout, and a hung shard raises TimeoutExpired
  uncaught, leaving sibling processes running. Fail-closed,
  but untidy.
- C-7 (rung3-ci/test-discover.py). Cosmetic: the module
  docstring says run mode prints "RESULT <test-id> <status>"
  lines; the actual marker is @@RESULT@@. The stale docstring
  invites a future parser to match the wrong prefix. Also
  run_suite() opens os.devnull without closing the handle.
- C-11 (branch records). The study's headline figures (365 s
  to 232 s, 2,433 tests) are not this branch's result; the
  branch measured 292.0 s serial to 175.7 s sharded on 2,340
  tests, with the laptop re-measure pending. Quote the branch
  figures for the branch.

### Cross-cutting

- C-9 (hermetic gate, cmd_hermetic). The gate treats a
  differing test set between normal and stripped runs as a
  WARNING, not a failure, so a test that vanishes in the
  stripped run does not fail the gate. This is M16's surface
  and overlaps the items 1-5 gate redteam's major 1 (hermetic
  vacuous pass); recorded here so the M17 identity work is not
  mistaken as covering it.
- C-10 (personal information, count and location only).
  Personal-name forms exist in plaintext in exactly one
  deliberate place on this branch: rung3-ci/arch-guard.py,
  one denylist pattern entry (DENY_PATTERNS) holding the name
  forms the guard scans for. That is by design (a denylist
  must contain what it matches, and the file sits outside the
  guard's own scan scope, as its comment says), and it is how
  item 4 closed the pii-scan blind spot. Separately, per the
  branch's own record, a real profile-dir hash remains in 10
  historical improvements/ log files, left as historical
  record; lane C did not independently enumerate them. The 5
  historical watchdog-log lines the owner decided on
  2026-11-27 to keep are on main, not on this branch
  (docs/clone2-watchdog-log.md does not exist here). No other
  personal information was found in any file the lanes read in
  full.

## 4. Form conformance notes

What landed exactly as approved:

- I1: Zen lane first (rdp_client.py only, cu.py untouched),
  version field plus migration notes in the README, the
  --legacy-output compat shim restoring the old behaviour
  exactly, the exit-code split the study's evidence correction
  demanded, per-command disposition definitions written before
  the shape changed, and I7 read-outcome labels riding in the
  disposition field, as the study required.
- I3: an exact match with the approved additive form and with
  Q42's confirmation of it: qualified refs accepted, bare refs
  warned on, only foreign ids rejected during the deprecation
  window, legacy snapshots grandfathered, the id recorded
  inside the snapshot file (reusing the filename stem) rather
  than only in its name.
- I5: the accounting half exactly (per-node children_count and
  cut flags, the snapshot-level complete flag), with skeleton
  and drill-down as they already existed.
- I8: the adopted half (probes/ plus the ledger habit) landed;
  advisory A/B is stated as allowed and non-blocking, per the
  study.
- I9: the adopted half exactly (read-only reporting in
  doctor); availability is entry-point presence plus one hard
  dependency, and no lane is exercised, as approved.
- I10: the auto-wait half with the approved shape (a11y lane,
  short 1 s cap, poll, last failing reason raised on expiry),
  wired into act() and ground(). F7 is the one approved
  condition the shape did not deliver.
- I16: the adopted half exactly (DOM-rect version,
  machine-layer only), with the docstring stating annotated
  outputs are machine-local debug artifacts, never committed.
- I17: ships after I1 and rides its envelope, as approved; no
  default timeout, as approved (the required-flag design
  enforces the R2 condition that a 30 s default turns 2 s
  failures into 30 s failures); the timeout error preserves
  the action outcome as action_result, as approved; the
  one-paragraph wait-for vs I6 vs I10 rule is in the README,
  as approved. F11 is the one R2 condition that did not land.
- I22: an exact match with the narrowed contract the study
  adopted: redact only where the tool controls the bytes, and
  document in the same breath that evaluate() is out of scope.
  Lane A verified field_value is the only general value-read
  path in zen_dom.py.
- M2: wrapper form only. seal.py reimplements nothing, invokes
  collect, snapshot, and gate as subprocesses in sequence,
  stops at the first non-zero exit, and propagates the code.
  The gate remains separately runnable over the wrapper's
  output, and that property is tested, not just claimed. No
  time saving is claimed anywhere (machine delta 0.35 s,
  agent-minute effect UNPROVEN), as the study required.
- M17: the mechanism conforms to the study definition:
  shards are built by filtering one discovered suite, outcomes
  are keyed by qualified per-test identity, --compare-serial
  diffs the full per-test maps, and the reported sharded wall
  includes the serial-only modules' run inside the timed
  window. The branch's five documented runs follow the study's
  quarantine discipline: every mismatch explained in writing.
  The hermetic follow-up (session_cleanup.py --procs-file,
  commit 3e699cec) is sound and fixed at the right layer: the
  production check is unchanged when the flag is absent, and
  the test is hermetic by construction. The companion fix
  (module-qualifying bare FunctionTestCase ids) is also sound.
  Two residual risks on the follow-up, both MINOR (lane C,
  recorded here so they are not lost): a nonexistent
  --procs-file path crashes with a traceback instead of a clean
  error, and passing an empty procs file in real use would make
  the guardian check vacuous; the flag is labelled test support
  and its only caller found is the test.

Rejected or pilot halves that correctly stayed out:

- I5 walk rewrite: the walk loop is byte-for-byte the same
  synchronous pending-stack walk with the 500-node and 2 s
  caps; no threading, no GetItems, no concurrency anywhere in
  a11y.py. Queue refinements Q5 to Q9 and Q25 to Q28 were not
  silently adopted either.
- I8 mandatory A/B gate: explicitly refused in
  probes/README.md ("no mandatory merge-base A/B gate and no
  baseline store until a real CI runner exists"); no gate code
  or baseline store was created.
- I9 unified lane interface: not built, and the docstring of
  cu.capability_matrix() says so.
- I10 actionability battery: no hit-test, no receives-events
  check, nothing beyond states and extents; the integration
  report records the hit-test probe as a ledger precondition
  before any battery work.
- I16 a11y-rect overlay: not built; only the DOM-rect version
  landed.

Ponytail credit, where the lanes gave it: I1 is the smallest
complete change (one data table plus one function, no
exception-class hierarchy, the shim a single flag read in two
small functions). I3 is one 25-line function and one reused
identifier, no new types and no second id to keep in sync. I22
places redaction at the two serialization points (snapshot,
report) instead of threading it through the client's
internals, so gating behaviour is untouched. I5 is 20 lines
changed in one function, no new abstraction. I8 is three small
files, no framework. I9 is one 40-line function with a small
closure, no interface layer, no config. I16 is one file,
stdlib plus PIL, no plugin shape. M2 reimplements nothing.

## 5. Test log

All runs on clone2's VM (headless, no live Zen or AT-SPI
session), in the worktree at the branch tip, unless noted. No
test files were modified by the review.

Lane A runs:

| Suite | Command | Result | Wall clock |
|-------|---------|--------|------------|
| Zen-RDP unit suites (test_envelope, test_redaction, test_scope_unittest) | python3 -m unittest test_envelope test_redaction test_scope_unittest (from scripts/zen-rdp) | 49 tests, OK (0.987 s inside unittest) | 1.09 s |
| A11y suite | python3 -m unittest tests.test_a11y | 29 tests, OK (1.071 s) | 1.23 s |
| Zen DOM suite | python3 -m unittest tests.test_zen_dom | 53 tests, FAILED (errors=4) (5.299 s) | 6.11 s |

The 4 zen_dom errors (test_typed_flag_not_forgeable_via_prelocked_getter,
test_typed_flag_not_forgeable_via_window_property,
test_focus_check_faithful_shadow_shim,
test_hit_check_faithful_shadow_shim) are import and harness
errors, none touching I22 paths. Two of the four were
spot-checked and reproduce identically in the main checkout,
confirming they are pre-existing VM environment errors, not
integration regressions. The I22 test
test_field_value_redacts_password_fields passes, as do both
field_value and verify_typed tests.

Lane A also ran finding probes with synthetic inputs only
(python3 -c against the worktree rdp_client module): the A1
classification spoof, and _redact_url against a
fragment-carried token and client_secret / refreshToken
parameters (C1, C2). Results are recorded with the findings.

Lane B runs (native artifacts native/wtype and
native/keyboard-protocol.c/.h copied from the main checkout
first, as fresh worktrees lack the gitignored files):

| Suite | Command | Result | Wall clock |
|-------|---------|--------|------------|
| Ledger validator (I8) | python3 probes/validate-ledger.py | LEDGER OK: 11 rows | 0.08 s |
| A11y suites | python3 -m unittest tests.test_a11y tests.test_a11y_skeleton | 39 tests, OK (0.863 s) | 1.19 s |
| Envelope suite (I1, I17) | python3 -m unittest test_envelope (from scripts/zen-rdp) | 15 tests, OK (0.808 s) | 1.08 s |
| Scope suite | python3 -m unittest test_scope_unittest (from scripts/zen-rdp) | 29 tests, OK (0.817 s) | 0.99 s |
| DOM-rect tests (I16) | python3 -m unittest scripts.test_dom_rect_debug | 2 tests, OK (0.097 s) | 0.36 s |
| Core suite (I9) | python3 -m unittest tests.test_core | 41 tests, OK (2.413 s) | 2.60 s |

Notes: the integration report recorded 1 pre-existing VM error
for test_core.py; on this VM all 41 tests pass with the native
artifacts copied in, so that error did not reproduce here
(environment difference, not a contradiction). No test in any
suite exercises the F7 disabled-polling case, the F8
VISIBLE-without-SHOWING case, or the F11 terminal-state case;
the suites pass because those behaviours are untested, not
because they are covered.

Lane C runs: none. The fetched branch content failed an
execution-risk check, and the governing instruction for
flagged content prohibits running or testing it without the
user's explicit go-ahead, which a subagent cannot request.
Lane C's work is file reading only.

Clone2 direct run, 2026-11-27 20:27, worktree at branch tip:

| Suite | Result |
|-------|--------|
| rung3-ci/test-seal.py | 3 tests, OK (0.794 s) |
| rung3-ci/test-test-discover.py | 5 tests, OK |
| rung3-ci/test-arch-guard.py | 2 tests, OK |

What was NOT run by this review:

- The live Zen harnesses: scripts/zen-rdp/test_rdp_client.py
  and test_rdp_smoke.py contain no unit tests; both assume a
  throwaway Zen with --start-debugger-server already running.
  Live results quoted in the integration report (laptop runs)
  were not re-run and are not counted here either way.
- The full M17 shard --compare-serial run. The branch-recorded
  figures (2,340 tests, sharded 175.7 s versus serial 292.0 s,
  1.66x; ranges serial 292.0 to 313.0 s, sharded 162.7 to
  200.9 s) are the branch's own records and were NOT re-run by
  this review. Lane C likewise lists the branch-recorded
  rung3-ci results (test-seal.py 3 tests OK, test-test-discover.py
  5 tests OK, the M16 hermetic detector pre-fix FAIL and
  post-fix PASS, the test_phase3_cleanup.py subset SHARD MATCH)
  as branch claims; clone2's direct run above independently
  confirms the two unit suites, but not the timed runs.

## 6. What the integration team should fix first

Ordered by severity and blast radius:

1. C-4 (M17). Assert the merged shard total against the
   discovered total, independent of --compare-serial. Until
   then the test gate can pass with tests silently missing,
   which undermines every other result the gate reports. The
   fix is small and the gate redteam already decided it as a
   fix-before-landing item.
2. A1 (I1). Give the classifier typed error origins instead
   of message substrings. A page currently controls the code
   and disposition of its own failures, and the first consumer
   that auto-retries on "safe" turns that into a replay
   hazard.
3. C1 (I22). Redact the URL fragment, and take C2 (the common
   parameter-name variants) in the same pass, since both are
   the same redaction surface. Live tokens are the blast
   radius.
4. C-8 (CI). Add one workflow step running the rung3-ci unit
   tests. Without it, fixes 1 and every future M2 or M17 edit
   can regress with CI green.
5. A2 (I1). Relabel navigate to delivered_unverified until a
   URL comparison against the requested destination exists,
   and correct the README wording in the same pass.
6. F7 (I10). Catch the disabled case inside the wait loop so
   enabled is actually polled; add the async-enable test case
   that is currently missing.
7. F11 (I17). Distinguish terminal evaluate errors (tab gone,
   session dead, actor gone) from transient ones and fail fast
   with the real failure; add the terminal test case.

After those, the MINOR clusters worth one pass each: the
remaining message-text classification in F13, the I5 complete
flag in F1, the single-envelope breaks in A4, and the
redaction-marker unification in C5.

Bottom line: the integration branch did what was approved, in
the approved shapes, with the rejected halves kept out and a
consistent smallest-change discipline. The seven MAJORs are
concentrated, not structural: three are claims the code does not
back (A2, F7, F11), two are
message-text and redaction holes on security-relevant paths
(A1, C1), and two are test-tooling trust holes (C-4, C-8).
None requires redesign; all seven have small, known fix
shapes.
