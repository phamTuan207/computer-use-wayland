# P1 snapshot command: implementation report

Date: 2026-11-27. Item P1 of the zen-mcp adoption plan
(improvements/zen-mcp-adoption-decision-20261127.md, sequenced
plan step 4). Branch: adopt-p1. Status: implemented, unit +
live tested, ready for independent review (Clone2).

## What shipped

One `snapshot` subcommand in scripts/zen-rdp/rdp_client.py:

- One fixed, client-owned read script (SNAPSHOT_JS, ~35 lines,
  our shape; zen-mcp's 3,561-line script was not ported).
  Compact walk over a/button/input/select/textarea/headings/
  [role], element cap 200 (the historical cap-200 walk size),
  name cap 60 chars, text preview cap 1500 chars.
- Routed through the existing guarded evaluate(): tab scope
  and credential denylist apply exactly as for `eval`.
- I17 load wait before reading (readyState complete, budget
  `--load-timeout`, default 10 s). On expiry the read still
  happens and `loadComplete` is false: accounting, not silent
  truncation, and a still-loading page is never mistaken for a
  complete read.
- Completeness accounting: totalElements, returnedElements,
  elementsTruncated, textTruncated, textLength, loadComplete,
  rolled-up `complete`, plus a client-issued `snapshotId`.
- Value-presence metadata only: inputs report `hasValue`
  (boolean). Field values are never read into the output.
- I22 redaction over the full output (url, hrefs, text
  preview) via the existing _redact_report_urls walk.
- Envelope: `snapshot` is a read command (delivered_verified
  on success; refusals not_delivered/safe). Usage error
  `load_timeout_invalid` for a non-positive budget.
- README section "Page snapshot (P1)".

Files: scripts/zen-rdp/rdp_client.py, scripts/zen-rdp/README.md,
scripts/zen-rdp/test_snapshot.py (new, 9 tests).

Implementation lane note: the decision doc assigns P1 to Codex
with Clone2 review. This implementation was written directly
in the VM worktree (the laptop Codex cannot reach the VM
worktree), so the author/grader split rests on the Clone2
independent review of this branch, which is still required
before landing to todolist-push.

## Unit tests

Baseline before: 71 tests OK. After: 80 tests OK (9 new in
test_snapshot.py, fake transport, no browser):

- result shape: snapshotId present, flags correct, no `value`
  key on input records.
- completeness under cap: total 300 / returned 200 /
  elementsTruncated true / complete false.
- load-wait timeout: loadComplete false, complete false, read
  still returned.
- redaction: planted token in url + href + text preview all
  redacted, token absent from output bytes.
- denylist refusal: snapshot raises CREDENTIAL TAB REFUSED
  when the denylist is armed after attach (proves the guarded
  evaluate() route).
- script contract: hasValue present, no value passthrough,
  JS cap constant matches SNAPSHOT_ELEMENT_CAP.
- fixture budget: synthetic 200-record payload at the cap
  stays under 25,919 B.
- CLI: unscoped snapshot refused (exit 2, unscoped_refused);
  --load-timeout 0 refused (load_timeout_invalid).

## Live test (dedicated session, owner Zen untouched)

Throwaway profile under /tmp, RDP port 9232, devtools user.js
prefs per the test-report recipe; fixtures on 127.0.0.1
(page1 form, big 300-control page, login page). Owner Zen
(PID 807599, port 6021) verified alive before and after;
test session killed by recorded PID with cmdline profile
check; ports 9232/8931 clear after cleanup.

- page1 snapshot: result 786 B, complete=true, 5/5 elements.
  Planted token in a link href redacted (token parameter
  replaced with REDACTED);
  password and text input values absent from output;
  hasValue=true on both inputs. CLI wall 88 ms.
- big snapshot (300 controls + h1): result 17,347 B,
  envelope 18,533 B. Budget 25,919 B: under by 8,572 B.
  totalElements 301, returnedElements 200,
  elementsTruncated=true, textTruncated=true (textLength
  1901, preview 1500), complete=false, loadComplete=true.
  No `value` key on any record. CLI wall 87 ms.
- denylist smoke: navigated to login.html with --no-denylist,
  then `snapshot` with the default denylist refused:
  exit 1, code denylist_refused, delivery not_delivered,
  retry safe (refusal fired at getTarget during attach,
  before any read; the evaluate-stage refusal is covered by
  the unit test).

## Before/after (honest)

| Read | Think-steps | Bytes (big page) | Wall |
| --- | --- | ---: | ---: |
| agent-JS walk via eval (representative hand walk, same caps) | author JS per call site | 11,684 B result string | 3.6 ms in-process; ~98 ms CLI |
| snapshot subcommand | 0 (fixed script) | 17,347 B result | 4.7 ms in-process; 87 ms CLI |

Notes: the representative hand walk is terser than the one
measured in the zen-mcp test report (25,919 B); either way,
snapshot is not a byte saving and wall-clock saving is ~0 ms
(process floor dominates CLI calls; in-process snapshot pays
one extra readyState poll evaluate). That matches the
decision doc's expectation. The value is accounting and
safety: the hand walk truncates silently, leaks input values
(verified: fixture values present in its output), and has no
redaction; snapshot reports truncation, never emits values,
redacts URLs, and issues a snapshotId for later refs work
(P2). One JS-authoring think-step per read is removed.

## Gates

- unittests: 80 OK (before 71 OK).
- pii-scan: clean (exit 0) on the changed-file delta
  (test_snapshot.py, README.md, this report, added lines of
  rdp_client.py). Note: a whole-tree scan of scripts/zen-rdp +
  improvements reports 544 pre-existing hits in already-landed
  files (e.g. test_redaction.py fake credentials); that debt
  predates P1 and is out of scope here.
- Explicit pathspec commit on adopt-p1; push verified via
  git ls-remote. No git add -A.
- Pending: Clone2 independent review; council+redteam gate
  before landing to todolist-push per the sequenced plan.
