# P1 snapshot command: independent review (clone2)

Date: 2026-11-27. Review only, no code changed. Reviewed branch
adopt-p1 at commit 26c16c07, against the implementation report
improvements/zen-mcp-p1-snapshot-20261127.md. Three independent
lanes; lane files kept locally in ~/workspace/p1-review-out/
(lane-a-guard-redaction-values.md, lane-b-completeness-size.md,
lane-c-tests.md).

## Verdict: FAIL (fixes required before landing)

The design is right and much of the implementation is sound:
the guarded route, the completeness arithmetic, and the test
counts all check out. But the branch makes three headline
claims that the code does not back: that field values are never
read into the output, that the result is delivered_verified,
and that output stays under a 25,919 B budget. Each is the same
class of overstatement this project has flagged before (A2 in
the integration review), and one of them is a real value leak.
Four MAJOR findings, no BLOCKING. Fix list at the end.

## What passes

- Guarded evaluate route: PASS. The CLI refuses unscoped and
  unmarked sessions before constructing the client; attach runs
  the scope and denylist guard before any getTarget request;
  snapshot() polls through wait_for on the guarded evaluate()
  and reads through evaluate(SNAPSHOT_JS). It sends no packet of
  its own and neither uses nor circumvents the raw-packet guard.
  Probed classifications: denylist refusal (denylist_refused,
  not_delivered, safe), scope refusal (scope_refused,
  not_delivered, safe).
- Completeness arithmetic: SOUND. totalElements is
  all.length from a fully materialised querySelectorAll before
  capping (rdp_client.py:105); elementsTruncated and
  textTruncated use strict greater-than, so exactly 200
  elements and exactly 1,500 chars are correctly not truncated,
  201 and 1,501 are; a page still loading at budget expiry gets
  loadComplete=false (any error from the wait poll forces it,
  conservatively) and complete=false, while the read still
  returns. Malformed results (non-string, invalid JSON,
  non-object) raise RDPError.
- snapshotId: SOUND as a label. uuid4 hex minted Python-side per
  call; two reads of the same page get different ids, which is
  what P2 needs. It is bound to nothing (no tab, URL, or content
  binding), so P2 must keep the id-to-(client, tab) mapping
  itself (MINOR).
- Cap contract: SNAPSHOT_ELEMENT_CAP = 200 and the JS CAP = 200
  match, and the contract test genuinely pins them together.
- Test counts: CONFIRMED by re-running. Full suite 80 tests OK
  (11.9 s run, wall 12.1 s); the five pre-existing modules alone give 71 OK;
  test_snapshot.py alone gives 9 OK. The pii-scan gate claim was
  reconstructed from the commit diff and is clean, exit 0. The
  README snapshot section matches the code on caps, flags, the
  10 s default, hasValue, and redaction scope.
- Redaction walk coverage: the _redact_report_urls walk does
  reach every emitted string field, and the controls pass:
  query parameters, fragment pairs containing = or &, userinfo
  passwords, ;jsessionid path parameters, nested next= tokens,
  URL-shaped parameter names. The planted-token test asserts
  the token is absent from the whole output blob, the strongest
  test in the file.

## MAJOR findings

### M1. Field values reach the output for contenteditable, and may for textarea (lane A A-7, lane C C-2)

The direct channel is clean: SNAPSHOT_JS never emits e.value
(only !!e.value for hasValue, line 118), never touches
getAttribute('value'), defaultValue, or option values, and the
Python side adds only snapshotId, loadComplete, and complete.
But the name fallback reads e.innerText for every element
(rdp_client.py:110-112), and the text preview is
document.body.innerText (line 124). For a contenteditable
element (the walk includes [role] elements, so a
contenteditable role="textbox" is in scope) innerText is the
user's typed content, emitted as name up to 60 chars and inside
the 1,500-char preview. For a textarea the same applies if
Firefox's innerText returns the field's current value; that
specific behaviour is UNVERIFIED, and the settling check is one
live fixture with planted secrets in a contenteditable, a
textarea, and a select. Either way, the report's headline
"Field values are never read into the output" is not true as
written: it was live-verified only on password and text inputs,
the two cases that cannot leak this way, and the contract test
only greps the JS for a value passthrough pattern. Fix: exclude
form-field and editable content from the name fallback and the
preview (or mask it), narrow the report claim to what is
proven, and add the planted-secret fixture for contenteditable
and textarea.

### M2. Snapshot success is labelled delivered_verified; by the A2 precedent it is delivered_unverified (lane A A-9; lane B B1, lane C C-4)

snapshot sits in _READ_COMMANDS, so its refusals are honestly
not_delivered/safe. But _success_disposition (rdp_client.py:
346-353) labels a snapshot success delivered_verified, while
eval, peval, and navigate were downgraded to
delivered_unverified by the A2 fix precisely because the tool
does not verify what it reports. The snapshot payload is
entirely page-authored, checked only for being a JSON object;
its completeness accounting is self-reported, and a payload
with totalElements, elementsTruncated, and textTruncated
deleted still returns complete=true (lane B B1 and lane C C-4
record this independently; no schema validation runs before
the roll-up). Claiming verified for self-reported
accounting repeats the A2 overstatement. Fix: either label
snapshot delivered_unverified, or earn the label by validating
client-side (required accounting keys present, returnedElements
recomputed from the elements array) before the roll-up.

### M3. The 25,919 B "budget" is not a budget and not a cap; the real worst case is about 64,437 B and formally unbounded (lane B B4, lane C)

25,919 B is traced to improvements/zen-mcp-test-20261127.md:112
(commit 351f8020): the measured output of a different,
agent-written hand-walk script on that study's fixture. Nothing
in rdp_client.py enforces a byte size; output size follows only
from the field caps. href IS capped (slice(0, 200), line 122),
but lane B's independently computed worst case from the caps,
measured with the same serialisation as the budget test, is
64,437 B for 200 anchors with names and hrefs at cap plus a
full preview (49,437 B from hrefs at cap alone; 124,437 B with
CJK names under JSON escaping). Role, title, and the page url
are uncapped in the JS, so the true worst case is formally
unbounded. The unit budget test passes because its synthetic
payload uses roughly 25-char hrefs and 10-char names; lane B
reproduced that fixture at 17,111 B and lane C at 17,116 B,
right next to the live 17,347 B, which confirms the live figure
is a truthful measurement of that fixture and nothing more.
The report's "under by 8,572 B" line invites reading headroom
as a safety property (B5). Fix: enforce a real byte cap in
snapshot() (truncate with a flag, in the command's own
accounting style), or rename the figure to a fixture reference
size everywhere it appears (report, the code comment at line
100, the test and its "worst case" comment); cap role and title
while there.

### M4. The big-page transport path has no unit coverage: longString reassembly is untested and still carries the F2 defects (lane C C-1)

The fake transport returns the snapshot payload as a primitive
string grip even at 14,010 chars. A real session delivers a
result that size as a longString grip reassembled by
_fetch_long_string, which still advances position by the
requested chunk size regardless of the actual substring length,
never verifies the assembled length against the declared
length, and can consume an actor error packet as content (the
earlier RDP review's F2, still open). The 300-control case is
the case this command exists for; its transport path is covered
only by the one-off live run. Fix: a fake-transport mode that
serves the payload as a longString grip in chunks, with a test
that the reassembled snapshot parses and accounts correctly,
including a chunk-error case; or fix F2 first and test through
it.

## MINOR findings

- A-1 / C-3: wait_for swallows guard refusals as not-yet, so a
  snapshot on a denylisted tab burns the full load budget
  (default 10 s) before the read-stage evaluate refuses. Safety
  holds (the guard is pre-send); the denylist unit test's
  measured 10.032 s is exactly this wait, and neither the
  report nor the test mentions it. This is the known F11
  behaviour arriving in a new command.
- A-2: the known C1 residual is now on first-class output: a
  bare-token fragment (https://ex.com/cb#SECRETJWT, href
  "#access_token") passes redaction verbatim.
- A-3: tokens in URL path segments (/reset/SECRET/confirm) are
  never redacted; I22 only handles parameter-shaped secrets.
- A-4: bare secrets in textPreview and element names pass; only
  URL substrings are rewritten.
- A-5: non-http(s) hrefs pass verbatim (a data: base64 href
  leaked its payload in probing); file:// page URLs likewise
  skip _redact_text.
- A-6: latent: _redact_report_urls discards the recursive
  return value in its list branch, so bare strings inside lists
  are never redacted. No current snapshot field has that shape;
  the first list-of-strings field will inherit the hole.
- A-8: a SELECT's snapshot name is its concatenated option
  text. Option values are never read; noted for the record.
- B2: no test executes SNAPSHOT_JS; the JS boundary behaviour
  (200/201/0 elements, 1,500/1,501 chars) rests on code reading
  and one live run. The canned-payload tests would not catch a
  JS-side accounting change.
- B3: snapshotId unbound (see What passes).
- B6: TEXT_CAP and NAME_CAP exist only inside the JS; there is
  no Python constant and no contract pin for them, unlike the
  element cap.
- C-5, C-6, C-7: snapshot-level redaction is tested for one
  planted shape only (fragment tokens, element names, userinfo
  hrefs untested); snapshotId is asserted present, never
  unique across two calls; zero-element pages, cap extremes,
  the CLI success envelope, and hasValue on select and textarea
  are untested.

## Test sufficiency, per report claim (lane C)

Result shape and no value key: PARTIAL (the no-value assertion
sits on a hand-written canned record; it proves pass-through,
not the JS). Completeness under the cap: ADEQUATE for the
roll-up arithmetic. Load-wait timeout accounting: ADEQUATE and
real. Redaction of the planted token across url, href, and
preview with blob-wide absence: ADEQUATE for the planted shape.
Denylist refusal proving the guarded route: ADEQUATE. Script
contract: WEAK, grep-level; it would not catch a value
passthrough written differently, or SELECT and TEXTAREA
dropping out of the JS branch. Fixture budget: PARTIAL (a real
serialised size of a tame fixture, not the worst case its
comment claims). CLI refusals (unscoped exit 2, --load-timeout
0): ADEQUATE, real subprocess tests asserting envelope codes.

## Fix list (in order)

1. M1: keep form-field and editable content out of name and
   textPreview; add the planted-secret live or JS-level fixture
   for contenteditable and textarea; narrow the report's value
   claim to what is proven.
2. M2: relabel snapshot success delivered_unverified, or add
   client-side payload validation (required keys,
   returnedElements recomputed) and keep verified.
3. M3: enforce a byte cap in snapshot() with a truncation flag,
   or rename 25,919 B to a fixture reference size in the
   report, the code comment, and the test; cap role and title.
4. M4: unit-cover the longString path for snapshot-sized
   payloads, including a chunk-error case.
5. MINORs worth one pass: A-6 (the list-branch redaction bug,
   one line, protects every future field), A-1 (fail fast when
   the load-wait poll is refused), B6 (pin TEXT_CAP and
   NAME_CAP in the contract test).

## Bottom line

Do not land adopt-p1 as-is. The command's skeleton is good and
its accounting arithmetic is honest, but it ships with a value
leak through innerText, a verified label it has not earned, a
budget figure that is not a bound, and no unit coverage of the
transport path its main use case depends on. All four fixes are
small and inside the command's own scope.
