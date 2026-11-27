# P2a ambiguity refusal: independent review (clone2)

Date: 2026-11-27. Review only, no code changed. Reviewed branch
adopt-p2a at commit 809085ca, against the adoption decision
(improvements/zen-mcp-adoption-decision-20261127.md) and the
commit's own claims. Three independent lanes; lane files kept
locally in ~/workspace/p2a-review-out/ (lane-a-counting.md,
lane-b-envelope-guards.md, lane-c-provenance-tests.md).

## Verdict: FAIL (fixes required before landing)

The design decisions are the right ones and the provenance is
clean: the count is genuinely uncapped, verify-and-act really
is a single evaluate, the guarded route is intact, and nothing
was copied from zen-mcp's capped count or its actor path. But
the headline guarantee, "acts only when count == 1", has a
proven hole at the scan cap, the "never replayed" claim is
false in the transport retry corner, and the acceptance
evidence for the true count of 100 is not on the branch. Five
MAJOR findings, no BLOCKING. Fix list at the end.

## What passes

- Provenance: CLEAN (lane C, checked mechanically and
  semantically). Counting runs over a fresh full-document
  querySelectorAll with count = matches.length; CANDIDATE_CAP
  (10) truncates only refusal summaries, never the count; the
  only zen-mcp-shaped cap is SCAN_CAP (10,000) on examined pool
  elements, with candidatesTruncated demoting the count to a
  lower bound. No bridge, no JSWindowActor, no
  MarionetteCommands, no WebDriver clickElement or
  sendKeysToElement anywhere (grep: zero occurrences); actions
  are in-page el.click() and the native prototype value setter
  with input and change events, through our own evaluateJSAsync
  path. Identifier overlap with zen-mcp's targeting code is
  generic DOM and ARIA vocabulary only. The concept was adopted
  by assignment; the code was not copied.
- Guarded route: PASS (lanes A and B agree). act() sends
  exactly one evaluate(); evaluate() runs the scope and
  denylist guard before any packet is sent, and attach is
  guarded too, so on a credential tab the refusal fires in
  Python before the counting JS, or any page JS, can run. No
  pre-check evaluate, no load wait, no side path.
- Descriptor handling: PASS (lane B, probe-verified). The
  descriptor is embedded with json.dumps into a single
  placeholder; hostile values (quotes, backslash escapes, a
  literal __SPEC__, template markers, U+2028) round-trip
  byte-identically. No injection beyond what raw eval already
  grants the same caller.
- Classification: PASS (lane B, probe-verified). The
  evaluate-exception prefix is checked before refusal needles
  for act too; needle-laden page exception text classifies as
  evaluate_failed / delivery_uncertain / unsafe, and refusal
  codes come only from the typed ActRefusal, never from message
  text. Page content can spoof neither a safe refusal nor
  target_ambiguous.
- Counting logic at fixture scale: VERIFIED by execution (lane
  A). The exact _ACT_JS, extracted and run in Node against a
  fixture-shaped stub pool (100 "Action" buttons plus 200
  inputs), returned count:100, candidatesTruncated:false, zero
  clicks. SCAN_CAP is about 33x the fixture pool, so the cap
  cannot bite there.
- Tests as counted: CONFIRMED (lane C). test_act.py 22 of 22
  OK; full suite 93 of 93 OK (wall 1.80 s). The total reconciles
  exactly: 71 base tests on this branch (P1's snapshot tests
  are absent, as expected, since P2a branched earlier) plus 22.

## MAJOR findings

### M1. The gate acts on a truncated scan: count == 1 with candidatesTruncated=true still clicks (lane A A1; lane C boundary gap)

The counting itself is honest, but the gate is
"if (count !== 1) refuse" (rdp_client.py:453) with no check of
the truncated flag. Lane A proved it by executing the real
script: a pool of 10,001 buttons with one "Unique" inside the
examined window and a second at index 10,000 (beyond SCAN_CAP)
returned {"acted":true, "count":1, "candidatesTruncated":true}
and clicked the element, while the true count was 2. The
documentation frames candidatesTruncated as a property of
refusal verdicts and never discloses that an acted verdict can
carry it. The corner needs a pool over 10,000 elements, so it is rare,
but it is a direct counterexample to the item's headline
guarantee, and neither the code nor any test treats an acted
verdict with candidatesTruncated=true as suspect. Fix: refuse
whenever truncated is true (the count is then a lower bound and
cannot prove uniqueness), or at minimum have act() reject an
acted verdict carrying the flag; add the boundary test at pool
== SCAN_CAP and above.

### M2. The transport retry can fire the act twice; "act commands are never replayed" is false in that corner (lane A A3, lane B B4)

Verify-and-act is genuinely single-eval, and malformed verdicts
(non-string, invalid JSON, missing acted) all raise RDPError
and can never fire an act from Python. But evaluate()
(rdp_client.py:1268-1281) auto-retries the identical script
once after a pinned re-attach on any noSuchActor error. If the
actor died after the script executed (click-triggered
navigation is the canonical cause) but before the result was
read, the retry re-runs verify-and-act on the re-attached tab
and can click a second time. The pinned re-attach verification
(canonical tab id plus URL) catches the case where the click
navigated elsewhere; a same-URL swap (reload, actor churn)
passes both checks, since neither id nor URL changes. This is the
known F1 double-execution class arriving at the first
non-idempotent command to inherit the retry, and the commit
message's "never replayed" claim does not survive it. Fix: opt
the act evaluate out of the noSuchActor retry (or make the
retry refuse when the command is an act), and correct the
claim to name the corner until then.

### M3. The refusal disposition bends the envelope vocabulary (lane B B1)

An arrived refusal emits its own code (target_ambiguous,
target_not_found, target_not_editable, bad_selector), exit 1,
the verdict dict as result, delivery=delivered_verified, and
retry=unsafe (rdp_client.py:1907-1913, test-pinned). The pair
is deliberate and documented, but it conflicts with the
channel's own definitions: the README defines unsafe as "input
may have landed", while an arrived refusal verdict proves the
input did NOT land (count != 1, nothing actuated). The stated
rationale, that a lost response cannot distinguish refusal
from a landed click, describes the transport path, which
already classifies correctly as delivery_uncertain/unsafe; the
ActRefusal branch is only reachable when the response was NOT
lost. It also inverts the success path, where a completed act
is delivered_unverified while a refusal is delivered_verified.
Distinct error codes limit the consumer harm, which is why
this is MAJOR and not BLOCKING. The success path itself is
consistent with the A2 fix (delivered_unverified; in-page
effect verification is nil for click and read-back-only for
type). Fix: classify an arrived refusal as not_delivered (or
delivered_verified with retry=safe), keeping
delivery_uncertain/unsafe for the lost-response path where it
belongs, and align the README wording.

### M4. "Exhaustive" is top-document only, and that is nowhere disclosed (lane A A2)

The pool is built from the top document only; the script never
enters iframes or shadow DOM, and grep for "iframe|shadow"
over rdp_client.py and README.md returns zero hits, while the
code header claims an "EXHAUSTIVE match count". A descriptor
matching one element in the top document and one inside an
iframe counts 1 and acts. Fix: disclose the pool boundary in the header, the
README, and the verdict (a pool-scope field), or extend the
scan; the disclosure is the minimum.

### M5. The acceptance evidence for the true count is not on the branch, and the counting JS is never executed by the suite (lane A A5, lane C)

The decision doc's acceptance test (true count 100 on the
fixture) cannot be re-run from 809085ca: the count-100 tests in
test_act.py feed canned fake-transport verdicts (they verify
Python passthrough, not counting), ScriptContractTests assert
script substrings and one textual ordering, the fixture HTML is
not in the repo, and test_act.py's docstring cites a "P2a
report" that does not exist on this branch (the commit touches
only README, rdp_client.py, test_act.py). Lane A's Node probe
shows the logic does produce exactly 100, so this is an
evidence defect, not a counting defect; but a regression that
capped the count at the candidate cap, exactly zen-mcp's
blemish, would pass all 93 tests today. Fix: commit the fixture
and a JS-executing test (Node or a live throwaway-browser test
in the rdp_smoke style), and either land the cited P2a report
or correct the docstring.

## MINOR findings

- A4: Python never re-verifies the success verdict; probes
  showed {"acted":true,"count":5,...}, {"acted":true} with no
  count, and {"acted":"false"} (a truthy string, count 0) all
  accepted as success. Page JS cannot forge the evaluate
  result, so this is defence in depth, and it is also the
  cheapest place to close M1 from the Python side.
- A6 / B10: candidate summaries (page-controlled name and text,
  capped at 120 chars) are emitted in the live envelope with no
  I22 redaction walk, unlike P1 snapshot output. The drive
  report omits candidates and is fully redacted.
- A7 / B7: refusal fields pass through untyped (a stubbed
  count:"many" is recorded verbatim), and the fallback code
  act_refused is not in the README's documented closed set.
- B8: ActRefusal's message embeds caller descriptor text; if it
  ever reached the generic _classify_error path it would
  misclassify as a safe refusal. Currently unreachable; the
  safety is positional, not structural.
- B9: library-level act() raises RDPError with only the
  message, dropping the usage code the CLI path preserves.
- B2: the success verdict's "acted": true wording and the
  echoed typed value in the type verdict are looser than the
  envelope's delivered_unverified label; noted for the record.
- Lane C: the retry=unsafe envelope test calls _fail directly
  with the expected literals instead of driving main()'s
  ActRefusal handler; the handler is correct by inspection but
  its wiring is untested end to end.

## Fix list (in order)

1. M1: refuse on truncated scans (JS gate and/or Python-side
   rejection of an acted verdict carrying
   candidatesTruncated=true); add the SCAN_CAP boundary test.
2. M2: exclude act from the noSuchActor evaluate retry, or
   make the retry refuse for act commands; correct the "never
   replayed" wording until then.
3. M5: commit the 100-button fixture and a test that executes
   the counting JS; land the cited P2a report or fix the
   docstring.
4. M3: reclassify the arrived-refusal disposition
   (not_delivered/safe for the refusal itself;
   delivery_uncertain/unsafe stays for lost responses) and
   align the README.
5. M4: disclose the top-document-only pool in the header, the
   README, and the verdict.
6. MINORs worth one pass: A4 (verify the success verdict's
   shape in Python), A6/B10 (redact candidate summaries in the
   envelope), A7/B7 (type the refusal fields; document
   act_refused).

## Bottom line

Do not land adopt-p2a as-is. The parts the owner asked about
most, provenance and the guarded route, are clean, and the
counting logic itself is right; but the gate acts on truncated
scans, the inherited transport retry can double-fire the act,
the refusal's envelope labels contradict the channel's own
vocabulary, "exhaustive" silently means top-document only, and
the acceptance proof for the headline count is not in the
repo. All five fixes are small.
