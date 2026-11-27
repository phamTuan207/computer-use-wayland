# Final pre-landing review of zen-mcp-adopt-20261127 at 2adb4c5a (clone2)

Date: 2026-11-27. Review only, no code changed. Scope, as
assigned: (1) re-review of the P1 fixes against clone2's earlier
FAIL review of adopt-p1 (improvements/p1-snapshot-review-
20261127.md), and (2) the pending P2a act path against clone2's
earlier FAIL review of adopt-p2a (improvements/p2a-act-review-
20261127.md). Three independent lanes; lane files kept locally
in ~/workspace/adopt-final-out/ (lane-1-p1-fixes.md,
lane-2-p2a-fixes.md, lane-3-regression.md). Lane 3 also ran a
regression and smoke pass over the rest of the merged branch
(P4 wrappers, P2b settling tests, P3 probe); that part is a
smoke check, not a deep review of those items.

## Bottom line: 2 BLOCKING findings. Do not land as-is.

Both blocking findings are small to fix, and everything else
from the two earlier reviews is either closed or non-blocking.
The blocking items are stated first, each with its exact
location.

## BLOCKING 1. P1: typed content still leaks into snapshot names through ancestor elements

Location: scripts/zen-rdp/rdp_client.py:134-136, the non-field
name branch of SNAPSHOT_JS.

The gate fix closed the direct channels, and lane 1 verified
that by executing the shipped script against a stub DOM with
planted secrets: the field or editable element itself emits no
innerText-derived name (a contenteditable role="textbox"
emitted no name; a textarea and a password input emitted only
their name attributes; a SELECT's name no longer comes from
option text), and the text preview now walks text nodes while
skipping form and contenteditable subtrees, so planted secrets
inside those subtrees never reach textPreview.

The residual: the non-field name branch still reads e.innerText
unconditionally, and innerText aggregates the whole subtree.
Lane 1's probe: a div with role="group" wrapping a
contenteditable emitted the name "label PLANTEDSECRET". Any
walked ancestor (a, button, h1 to h6, [role]) that wraps an
editable subtree leaks up to 60 chars of typed content into its
name. The gate-fix live fixture planted secrets in the fields
themselves, so it never covered this shape. This is the same
leak class as the original C-M1 finding, narrowed but not
closed, and it meets the landing criterion directly: user-typed
values still reach the snapshot output. Fix shape: in the
non-field branch, derive the name from the element's own text
nodes with the same form/editable subtree skipping the preview
walk already uses, or drop innerText from the name chain for
any element that contains an editable or form descendant; add
the ancestor-wrapping case to the fixture.

## BLOCKING 2. P2a: act still fires on a target that is not unique in the tab, and the pool scope is still undisclosed

Location: scripts/zen-rdp/rdp_client.py:537-540 (pool built
from document.querySelectorAll on the top document only),
header claim at line 431, README claim at line 230.

The act pool never enters iframes or shadow DOM. Grep for
iframe, shadow, contentDocument, shadowRoot over rdp_client.py
and README.md returns zero hits. The header still claims an
"EXHAUSTIVE match count", the README still says the script
"counts ALL visible matches", and the verdict carries no
pool-scope field. So a descriptor matching one element in the
top document and one inside an iframe counts 1 and acts, while
a second matching element exists in the tab. Clone2's earlier
review rated this MAJOR and named disclosure (header, README,
verdict) as the minimum fix; the gate-fix addendum (55ce675e)
itself records that clone2's P2a findings still needed a
follow-up pass, and this fix was not made. It is raised to
BLOCKING for this landing decision because it meets the stated
criterion, actuation on a non-unique target, silently, under a
written claim of counting all matches. The fix is the small
one already named: disclose the top-document pool scope in the
header, the README, and the verdict (or extend the scan). One
condition from lane 2 belongs on the record: if the owner
accepts the top-document pool as a deliberate design scope,
this finding reverts to MAJOR, but the false "counts ALL"
wording should not land on main either way.

## P1 fix verdicts (lane 1)

- C-M1 innerText leak: PARTIAL (see BLOCKING 1). Direct
  channels closed and probe-verified; ancestor channel open.
  A narrower residual is MINOR: the preview walk stops its
  ancestor check at document.body, so a contenteditable body
  is not excluded.
- C-M2 delivered_verified: CLOSED. _validate_snapshot requires
  all ten accounting keys, recomputes returnedElements from
  the elements array, and checks both truncation flags against
  the totals; the missing-keys probe case now refuses. The
  delivered_verified label is earned by that validation, as
  the earlier review required. BUT the fix introduced a new
  MAJOR (below).
- C-M3 byte cap: CLOSED. SNAPSHOT_BYTE_CAP = 25919 is now
  enforced in snapshot() by popping elements from the end with
  a bytesTruncated flag rolled into complete; role, title, url,
  and href are capped in the JS, so the unbounded worst case is
  gone. One MINOR: the cap is measured on the bare result dict,
  while envelope-mode _emit output measured 26,295 B for a
  25,723 B capped result (376 B over), so the "exact
  serialization consumers see" comment holds only for legacy
  mode.
- C-M4 longString: CLOSED. _fetch_long_string is hardened
  (advances by the actual chunk length, rejects actor error
  packets before the from-match, an empty chunk fails loud,
  the assembled length is verified against the declared
  length), and test_snapshot.py now serves the payload as a
  chunked longString grip with reassembly, short-chunk, and
  chunk-error tests, all passing.
- Earlier MINORs: A-6 (list-branch redaction discarding its
  return) CLOSED; B6 (cap pinning) CLOSED (all caps are Python
  constants interpolated into the JS and pinned by test; the
  HREF_CAP interpolation is not asserted, a nit); A-1
  (fail-fast on guard refusal) CLOSED (wait_for, wait_load, and
  snapshot re-raise guard refusals; test_snapshot.py now runs
  in 0.542 s total, against the old 10.032 s denylist test
  alone).

New MAJOR from the C-M2 fix: the textPreview consistency check
in _validate_snapshot compares Python code-point lengths
against JavaScript UTF-16 lengths, so a payload built exactly
as Firefox emits it for a page whose preview window contains
an astral character (an emoji) is refused ("textPreview length
13 inconsistent with textLength=14", probe-confirmed). Snapshot
fails loud on such pages. Fail-safe (no leak, no false claim),
so MAJOR, not blocking; fix by comparing in UTF-16 units or by
having the JS report the preview length in the same unit the
client checks.

## P2a fix verdicts (lane 2)

- M1 act on truncated scan: CLOSED. The JS gate refuses on
  truncated before the count gate (rdp_client.py:566-570, ahead
  of count !== 1 at 571), and act() converts any acted verdict
  carrying candidatesTruncated=true into the scan_truncated
  refusal (1562-1571), code target_scan_truncated, which is in
  the README closed set. Lane 2 re-ran the earlier
  counterexample (pool 10,001, second match beyond SCAN_CAP):
  refused, zero clicks. A boundary pool of exactly 10,000 with
  a unique match acts exactly once.
- M2 retry double-fire: CLOSED. evaluate() gained a replay
  parameter (default True) with the noSuchActor retry gated on
  it (1495-1513); act() passes replay=False (1545-1546), so a
  post-click actor loss propagates after exactly one execution
  while read paths keep the RT-06 retry. Unit proof on the fake
  transport (one send, zero retries), plus the live
  fault-injection settling tests in test_p2b_settling.py
  (env-gated here; the addendum records 8 of 8 with a session).
  A lost act response now surfaces as delivery_uncertain/unsafe
  through _classify_error, which is the honest label.
- M3 refusal disposition: STILL OPEN, MAJOR, not blocking. The
  ActRefusal CLI branch still emits delivered_verified plus
  retry=unsafe for an arrived refusal (2342-2347), the header
  comment keeps the lost-response rationale (439-441), and the
  README still defines unsafe as "input may have landed"
  (207-208) while documenting the same pair for arrived
  refusals (261-265) against a delivered_unverified success
  path. Neither fix option from the earlier review was adopted.
  It does not block landing: distinct error codes limit
  consumer harm and nothing actuates on a refusal. It belongs
  in the follow-up pass the addendum already owes.
- M4 top-document pool: STILL OPEN, raised to BLOCKING 2
  above.
- M5 acceptance evidence: PARTIAL, MAJOR remainder, not
  blocking. Improved: the shipped _ACT_JS is now executed live
  by test_p2b_settling.py, but only for delivery settling on a
  unique target, never for a count. Still open: test_act.py
  still stubs evaluate() with canned verdicts, so the count-100
  acceptance still rests on passthrough; the gate-fix JS test
  is textual ordering only; no act fixture HTML is committed
  (no file matching *p2a* exists on the branch); and
  test_act.py's docstring (lines 11-12) still cites a "P2a
  report" that does not exist on this branch. Lane 2 executed
  the current script on the fixture shape directly: exactly
  count:100, ambiguous refusal, zero clicks, so the logic is
  right and this remains an evidence defect.
- Earlier MINORs: A4 PARTIAL (act() now rejects non-string,
  invalid-JSON, and acted-less verdicts and pops "value", but
  probes still show {acted:true, count:5}, {acted:true} with no
  count, and {acted:"false"} accepted as success); A6/B10 STILL
  OPEN (the refusal result is printed unredacted; _redact_
  report_urls is called only on the snapshot path); A7/B7 STILL
  OPEN (the act_refused fallback is still absent from the
  README closed set; refusal fields still pass through
  untyped); B2 (type verdict echoing el.value) CLOSED by the
  gate fix (hasValue and valueLength only).

## Regression and integration (lane 3)

- Full suite at 2adb4c5a: 159 tests, OK, 0 failures, 0 errors,
  3 skipped (unittest clock 3.153 s, wall about 3.5 s). The 3
  skips are the test_p2b_settling live tests, env-gated on
  RDP_TEST_PORT with explicit reasons. Per-module arithmetic
  reconciles exactly against both earlier branches: base 71,
  plus redaction growth of 7 (10 to 17), snapshot 22, act 30,
  zen_spaces 17, p2b_settling 8, p3_probe 4, totalling 159; no
  test was lost in the merges.
- Coexistence: PASS. Both subcommands are CLI-wired and both
  go through the guarded evaluate route; _READ_COMMANDS
  contains snapshot and not act, so transport-error
  dispositions match each command's semantics; no shared-state
  interference found.
- pii-scan: the added-lines delta (4,570 lines) gives exactly
  one hit, the decision doc's own sentence describing the scan;
  the doc's "zero new hits" record is confirmed. Whole-file
  scanning shows 18 hits, all pre-existing (planted redaction
  fixtures and prose not in this diff).
- Personal information in the branch diff since 431a8d1e:
  CLEAN (zero matches for name, personal email domains, +84
  phone numbers, credential assignments).
- Smoke check of the other merged items: zen_spaces.py
  compiles, is stdlib-only, writes nothing, and routes through
  the gated parent_evaluate; the p2b and p3 test modules are
  properly env-gated or subprocess-local. Nothing breaks
  collection or import.
- MINORs from this lane: the README test command lists only 7
  modules and runs 147 of the 159 tests, silently omitting
  test_p2b_settling and test_p3_probe; the 3 live settling
  tests never run in a plain unit run, so their evidence rests
  on the spike lane's dedicated session.

## What would unblock landing

1. BLOCKING 1: close the ancestor innerText channel in the
   snapshot name derivation and add the wrapping-ancestor case
   to the fixture.
2. BLOCKING 2: disclose the act pool's top-document scope in
   the header, the README, and the verdict (or extend the
   scan).

The remaining items (the emoji UTF-16 validation MAJOR, P2a M3
and the M5 remainder, and the MINORs) can land and be handled
in the follow-up pass the gate-fix addendum already
acknowledges, as long as they stay tracked there.
