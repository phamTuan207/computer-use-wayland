# BLOCKING fix verification on zen-mcp-adopt-20261127 at ace79018 (clone2)

Date: 2026-11-27. Review only, no code changed. Scope, as
assigned: verify the two BLOCKING fixes from clone2's final
pre-landing review (improvements/adopt-final-review-20261127.md)
as landed in commit cf5d8790, at branch tip ace79018. Three
independent lanes; lane files kept locally in
~/workspace/adopt-fix2-out/ (lane-1-blocking1.md,
lane-2-blocking2.md, lane-3-regression.md).

## Bottom line: both BLOCKINGs are CLOSED. No BLOCKING remains.

On the criteria of the earlier review, the branch is clear to
land. The still-open non-blocking items (the emoji UTF-16
validation MAJOR, P2a M3 refusal disposition, the P2a M5
evidence remainder, and the MINORs) are unchanged by this fix
round and stay tracked for the follow-up pass, exactly as the
fix commit itself records.

## BLOCKING 1 (snapshot ancestor innerText leak): CLOSED

The fix (rdp_client.py:141-148) computes
wrapsField = !isField && !!e.querySelector('input, textarea,
select, [contenteditable]'), and any element with isField or
wrapsField now derives its name only from aria-label,
placeholder, or name attributes, never innerText.

Lane 1 executed the shipped SNAPSHOT_JS verbatim in Node with
a subtree-aggregating innerText stub:

- The original probe shape (div role="group" wrapping a
  contenteditable with a planted secret): the ancestor emits
  NO name, and the secret reaches no name, no preview, and
  nowhere in the serialized payload.
- Variants all leak-free: button wrapping an input, h2
  wrapping a textarea, a wrapping a select, a nested
  div > span > contenteditable="" chain, and a walked element
  inside a contenteditable root.
- No regression: ordinary elements (button, h1, a plain
  role="group" div) keep their innerText names.

Guard coverage: the attribute-presence selector catches
contenteditable in every form ("", "true", "plaintext-only")
at any subtree depth; inherited editability on the walked
element itself is caught earlier by isField via
isContentEditable. An editable descendant with no
contenteditable attribute anywhere is not constructible in the
DOM model. One UNVERIFIED note, not a finding: querySelector
does not pierce shadow roots, and live-browser innerText
behaviour across shadow boundaries was not verified in this
lane.

The new test is genuine: test_cm1_ancestor_wrapping_editable_
no_leak embeds rc.SNAPSHOT_JS verbatim via json.dumps, evals
it in Node on the exact probe shape, and asserts the secret is
absent from every name, the preview, and the whole payload,
with positive controls. test_snapshot.py: 23 tests OK.

Two MINORs:
- MINOR 1: a wrapping ancestor loses its own label text too,
  because the fix drops innerText wholesale for wrapping
  ancestors instead of filtering it (also triggered by a
  contenteditable="false" descendant). This is the safe
  direction, and it was one of the two fix shapes the original
  BLOCKING 1 review explicitly offered; recorded as a
  name-completeness tradeoff, not a reopening.
- MINOR 2: the textPreview contenteditable-body residual from
  the previous round is still present and unchanged,
  probe-confirmed: text nodes that are direct children of a
  contenteditable body reach the preview, because the preview
  walk's ancestor check stops before document.body; text
  nested in a child div of the same body is correctly
  excluded. Same narrow shape and severity as last round.

## BLOCKING 2 (act top-document pool undisclosed): CLOSED

Disclosure is complete and accurate everywhere a consumer
would look. Grep for exhaustive, counts all, all visible, all
matches, and whole-tab over rdp_client.py and README.md
returns only qualified or negating uses. The module docstring
(line 38), the _ACT_JS header comment (441-448), and the act()
docstring (1557-1560) all state the count is exhaustive over
the TOP DOCUMENT only, that iframes and shadow DOM are not
scanned, and that every verdict carries
poolScope: "top-document". The README act section (230-240)
qualifies "counts all visible matches ... in the TOP
DOCUMENT", adds the explicit pool paragraph (a second match
inside a frame or shadow root is invisible to the count and
does not block the act), and lists poolScope among the refusal
verdict fields. The old unqualified EXHAUSTIVE header and
counts ALL README wording are gone.

poolScope verified by execution: the shipped _ACT_JS has
exactly 8 verdict returns and all 8 carry poolScope:
POOL_SCOPE. Lane 2 executed the script as shipped in Node
against stub DOMs for the acted click, ambiguous, not_found,
scan_truncated, not_editable, bad_selector, and acted type
shapes; every one returned poolScope "top-document" with the
correct acted, reason, and count values. Python side: the
setdefault runs before branching, so a field-less verdict
leaves act() with "top-document"; the scan_truncated
conversion keeps the field in both the converted refusal and
the drive-report record; refusal records include poolScope
from the verdict.

Tests: test_act.py is now 32 tests, all OK. A script-contract
test pins that every verdict return in the generated script
carries poolScope, and a verdict test pins the refusal path
and the Python-side defaulting. Two MINORs: no test pins the
docstring, header, or README wording itself, so the prose is
correct as landed but unguarded against a future edit; and the
redteam's whole-tree grep found the unqualified wording
surviving in test_act.py's own prose (the module docstring's
"exhaustive count" at line 5 and the test name
test_script_embeds_spec_and_counts_exhaustively at line 92).
Those are test-file descriptions, not consumer surfaces, and
they do not reopen this finding; qualifying them belongs in
the follow-up pass.

No regression in the act path: the _ACT_JS diff touches only
the POOL_SCOPE constant, its comment, and verdict literals;
pool construction, SCAN_CAP, and gating are byte-identical.
M1 stays closed (the truncated-scan probe re-refused with zero
clicks on the current script) and M2 stays closed (act() still
passes replay=False). The scan behaviour itself is unchanged
(top-document only), which is the disclosed design scope.

## Regression at the new tip (lane 3)

- Full suite: 162 tests OK, 0 failures, 0 errors, 3 skipped
  (the same env-gated test_p2b_settling live tests), unittest
  clock 3.458 s. The fix commit's claim is confirmed, and the
  growth reconciles exactly: snapshot 23 (was 22, +1, the new
  Node-executed ancestor test), act 32 (was 30, +2, the two new
  poolScope tests), all other modules unchanged from the
  previous tip. No test lost.
- pii-scan on the added-lines delta since 2adb4c5a (249 added
  lines): clean, exit 0, zero hits.
- The diff 2adb4c5a..ace79018 touches exactly the five claimed
  files (the decision doc, README.md, rdp_client.py,
  test_act.py, test_snapshot.py) and contains no personal
  information.
- The previously open non-blocking items are unchanged, none
  silently altered: P2a M3 (the ActRefusal branch still emits
  delivered_verified plus retry=unsafe), the emoji UTF-16
  validation MAJOR (_validate_snapshot untouched), and the P2a
  M5 remainder (the new act tests are disclosure tests; the
  counting JS is still never executed for a count, and no act
  fixture was added).

## Conclusion

BLOCKING 1 CLOSED, BLOCKING 2 CLOSED, no BLOCKING remaining.
Nothing in this fix round opened a new MAJOR. Landing is clear
on the criteria of the final pre-landing review; the tracked
follow-up pass still owes the emoji UTF-16 fix, the P2a M3
disposition correction, and the M5 acceptance evidence.
