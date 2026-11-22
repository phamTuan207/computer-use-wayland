# Council 1 review log: B2-6 step-1 close-out (independent)

Reviewer: council 1, independent. Worker graded: MOCHI-B2-6.
Worktree: ~/workspace/mochi-b2-6-work. HEAD at review start:
5ee043d25fd072586dfd9d51d767488c4f2d7c43 (detached).
Base for the diff under review: 0400e86.
Fix commits under review: 3532bfd (scripts/cdp.mjs),
e500923 (tests/cdp_snapshot.mjs), d88a472
(tests/test_click3_redteam2.py). Final log under review:
improvements/mochi-b2-6-final-log.md, commit b0876ca, filled
in by 5ee043d, 607 lines.
Start: 2026-11-23 00:24 +07 (Asia/Ho_Chi_Minh). All times below
are wall-clock +07 unless noted. Standing rules: no em dash
(U+2014) or en dash (U+2013) anywhere in this file, no personal
info, never ydotool, no live browser run, no push, no file
deleted, no worker file edited. Only this file is created by
this reviewer. Commit method: git add -- file then git commit -m,
never git commit -- paths.

Scope: the worker fix (3 commits above) and the final log
(b0876ca, 5ee043d), against the task brief (B2-6 step-1
close-out, coord commit f9a1a9f), the final direction log
(improvements/worker-click3-final-direction-log.md, step 1),
and the Lauren Tan workflow
(improvements/lauren-tan-workflow-20261122.md). This reviewer
grades the worker fix, not its own fix, so there is no
self-review conflict. Every conclusion below rests on checks
this reviewer ran itself, not on the worker conclusions.

## 0. Finish conditions (evidence contract, Lauren Tan)

Written BEFORE any check below was run. A confident reply
without evidence is a red flag. "Inconclusive" is honest, not
a pass.

| # | Check (command, from the worktree root unless noted) | Finish condition (expected output) |
| --- | --- | --- |
| C1 | python3 -m unittest tests.test_first_action.TestRun.(4 item-12 tests) -v, exact names read from tests/test_first_action.py at HEAD | Ran 4 tests, OK |
| C2 | cd tests, PYTHONPATH=../scripts:. python3 -m unittest test_click3_redteam2 | Ran 52 tests, OK |
| C3 | node tests/cdp_snapshot.mjs | exit 0 |
| C4 | python3 -m unittest tests.test_cdp_snapshot | Ran 2 tests, OK |
| C5 | cd tests, PYTHONPATH=../scripts:. python3 -m unittest test_first_action test_zen_dom test_dom_act test_type_verification test_click2_redteam test_codemode test_session_continuation test_session_policy | Ran 348 tests, OK |
| C6 | Spec check, first-hand: read the Email state value sanitization algorithm in HTML Standard 4.10.5.1.5 from https://html.spec.whatwg.org/multipage/input.html, and compare it token by token with scripts/cdp.mjs lines 581-630 at HEAD | Algorithm says split on commas, strip leading and trailing ASCII whitespace from each token, rejoin with a single comma; template implements exactly that, with ASCII whitespace TAB LF FF CR SPACE |
| C7 | Discrimination round-trip, run by this reviewer: restore scripts/cdp.mjs from 0400e86 to a scratch copy, run the new Python test test_set_value_email_multiple_trims_each_token against the old template, then restore the HEAD template and re-run | Old template: new test FAILS. HEAD template: new test passes. Worktree clean after (git status shows only this untracked log file) |
| C8 | Spot-check remnant inventory R1-R14: verify each cited file, line, commit hash and count from the repo at HEAD (wc -l, grep -n, git show --stat, git ls-remote) | Every cited coordinate exists as claimed, or the mismatch is listed as a finding with its coordinate |
| C9 | Full discover: cd tests, PYTHONPATH=../scripts:. python3 -m unittest discover -s . -p "test_*.py", on the final committed HEAD 5ee043d | Tally recorded; FAIL/ERROR lines naming cdp, cdp_snapshot, redteam2, first_action, zen_dom, dom_act, type_verification are zero; every other FAIL/ERROR identified by cause and matched to R12/R13/R14 or listed as new |
| C10 | Manifest verify: python3 scripts/bench_manifest.py verify --manifest deploy-manifest.json --repo . | Source artifacts bench_script and fixture ok, log names the run; any FAIL explained by cause (git_status_clean, tools dir) |
| C11 | File counts: clear __pycache__ first, then git ls-files count (tracked) and on-disk count separately; em dash and en dash scan over the 3 fix files plus both log files | Tracked and on-disk counts reported separately; 0 em dash and 0 en dash in the fix files |
| C12 | Procedure check P1-P3: read section 4 of the final log and judge whether each procedure names setup, exact inputs and expected outputs, stop condition, and evidence artifact, well enough for a live worker to run it without inventing the test | P1 judged runnable as written or its gaps listed; P2 and P3 judged the same way, with P3 judged against its own admission that it is a pointer only |

Verdict rule: PASS only if C1-C5, C7 and C9 show the claimed
test outcomes on the committed tree, C6 confirms the spec
match, C8 finds no material remnant error, and every finding
is either fixed in the fix commits or is a live or out-of-scope
residual with a named owner. Any finding that changes what the
fix proves, or any claim in the final log without evidence,
blocks PASS.

## 1. Checks run (results, each run by this reviewer)

HEAD throughout: 5ee043d25fd072586dfd9d51d767488c4f2d7c43.
Base 0400e86. All times +07, Asia/Ho_Chi_Minh.

- C1, 00:25 +07, 0.2s: python3 -m unittest
  tests.test_first_action.TestRun.test_session_after_is_scope_matching_not_screen
  tests.test_first_action.TestRun.test_fallback_after_is_scope_matching_not_screen
  tests.test_first_action.TestRun.test_after_without_result_after_captures_fresh_window
  tests.test_first_action.TestRun.test_screen_observation_key_batch_proceeds_to_session
  -v. Ran 4 tests in 0.015s, OK. The four names sit at
  tests/test_first_action.py lines 1372, 1398, 1418, 1436, exactly
  as the final log claims. C1 PASS.
- C2, 00:25:33 +07, 2.7s: cd tests,
  PYTHONPATH=../scripts:. python3 -m unittest test_click3_redteam2.
  Ran 52 tests in 2.350s, OK. C2 PASS.
- C3, 00:25 +07, 1.9s: node tests/cdp_snapshot.mjs, exit 0, final
  line "all cdp snapshot, redaction, fill, payload, no_after and
  scope regressions pass". C3 PASS.
- C4, 00:25 +07, 4.9s: python3 -m unittest tests.test_cdp_snapshot.
  Ran 2 tests in 4.730s, OK. C4 PASS.
- C5, 00:25:53 +07, 11.5s: cd tests, PYTHONPATH=../scripts:.
  python3 -m unittest test_first_action test_zen_dom test_dom_act
  test_type_verification test_click2_redteam test_codemode
  test_session_continuation test_session_policy. Ran 348 tests in
  11.251s, OK. C5 PASS.
- C6, spec first-hand: read HTML Standard
  https://html.spec.whatwg.org/multipage/input.html, page crawled
  2026-11-22 17:13 UTC, section 4.10.5.1.5 Email state. Lines
  1355-1368 state the value sanitization algorithm verbatim: split
  on commas, strip leading and trailing ASCII whitespace from each
  resulting token, let the values be the resulting list, set the
  value to the tokens joined with a single U+002C COMMA. Lines
  1339-1349 state the same per-value strip for the multiple change
  steps. The template in scripts/cdp.mjs lines 598-611 implements
  exactly this: split on char code 44, trim each token over char
  codes 9, 12, 32, rejoin with a single comma. ASCII whitespace is
  TAB 9, LF 10, FF 12, CR 13, SPACE 32; CR and LF are stripped from
  the value two lines above (lines 594-596), so only 9, 12, 32 can
  remain at token ends, and the trim set is complete. The rule is
  unconditional for email, with or without multiple, which the
  template, the node fake (tests/cdp_snapshot.mjs lines 14-20) and
  the Python fake (tests/test_click3_redteam2.py lines 870-975)
  all implement the same way. The url branch keeps the whole-value
  trim, unchanged. C6 PASS.
- C7, discrimination, 00:26:25 to 00:26:26 +07: copied HEAD
  scripts/cdp.mjs to /tmp, restored the 0400e86 template, ran the
  new Python test
  test_set_value_email_multiple_trims_each_token: Ran 1 test in
  0.188s, FAILED (failures=1), error "multiple email set failed
  although the engine lands the per-token trimmed value:
  {'ok': False, 'error': 'value verification failed', 'events': [],
  'value': 'a@b.com,c@d.com'}". The failure mechanism is exactly
  as the worker described: the fake lands the per-token trimmed
  value while the old template expects the whole-trim form.
  Restored the HEAD template, verified git status shows only
  untracked review logs and git diff HEAD is empty, re-ran the
  test: Ran 1 test in 0.096s, OK. The new test is not vacuous.
  C7 PASS.
- C8, remnant spot-checks, 00:25 to 00:27 +07:
  - R1: the four test names and lines verified in C1. The old
    refused test exists at 36364b1
    (tests/test_first_action.py:1041) and is absent at 0400e86
    (grep count 0); P2 commit 292753f exists. Supported.
  - R2: git ls-remote origin amend4-codex returns
    06a34e8610a9467c3884f6dd7a567293c747da45, and that hash appears
    in improvements/worker-click4-step1-closeout-log.md (1 hit)
    and improvements/w-step1-closeout-log.md (2 hits). Supported.
  - R3: wc -l gives 598, 783, 657 for r3c1, r3c2, r3c3, exactly
    as claimed; "GO 7", "AMEND 5", "BLOCK 0" each appear in 2 of
    the round-3 logs. Supported.
  - R4: F3 split verified at tests/test_click3_redteam2.py:316
    and :358; F5 def at :133; F6 def at :418. F2 and F4
    coordinates are off, see finding F1.
  - R5: test_set_value_maxlength_uses_sanitized_length at
    tests/test_click3_redteam2.py:777, exact. Supported.
  - R6: test_typed_flag_not_forgeable_via_prelocked_getter at
    tests/test_zen_dom.py:825, exact; the window-property test
    is at :793. Supported.
  - R7: the three scopeless-window tests are at
    tests/test_first_action.py:1455, 1484, 1505, exact.
    Supported.
  - R8: at 0400e86, grep for multiple in tests/cdp_snapshot.mjs
    finds only line 497 (an unrelated scope-selector test), and
    none in scripts/cdp.mjs. The gap was real at the base.
    Supported.
  - R9: grep -c a1a672d deploy-manifest.json returns 0; the
    manifest run_id is bench-20261122T020225Z-3d9270 and its
    source_commit is d7d569b. Supported, except the verify FAIL
    enumeration, see finding F2.
  - R10: the citation exists in
    improvements/worker-click3-testrepair-log.md lines 339-341
    ("F5 DOM-gate finding ... cu.py:2280 / cu.py:2110-2117 /
    cu.py:2279"); scripts/cu.py lines 2278-2282 are the
    type_unverified path, consistent in spirit. This reviewer
    did not independently verify cu.py:2110-2117 as the locus.
    Second-hand, see finding F6.
  - R11: test_arm_typed_flag_misses_iframe_targets is at
    tests/test_click3_redteam2.py:509, exact. Supported.
  - R13: git show 163e90c touches only scripts/overlay.py
    (1 file, 6 insertions, 4 deletions); at 36364b1
    scripts/overlay.py _label_for returns agent + ' via ' +
    method, so the test expectation 'Muse via BiDi' passed
    there; at HEAD the test file still asserts it at
    tests/test_overlay.py:163. Supported.
  - R14: /home/hatch/workspace/tools/ does not exist
    (ls: No such file or directory). Supported.
  - Fix commits: git show --stat confirms 3532bfd 27 insertions
    10 deletions, e500923 29 insertions 1 deletion, d88a472 107
    insertions, each exactly 1 file. The final log is 607 lines
    (wc -l), b0876ca adds 606 lines and 5ee043d adds 1 net line.
    Supported.
- C9, full discover, launched 00:26:15 +07 detached, log
  /tmp/mochi-b2-6-council1-discover.log, finished 00:31:07 +07
  (log mtime 17:31:07Z), 290.389s: Ran 2381 tests in 290.389s,
  FAILED (failures=2, errors=8, skipped=17). FAIL/ERROR lines,
  byte-identical in set to the worker run:
  test_label_format (R13), test_typed_text_check_fails_when_
  fragment_is_absent (R12), test_a11y_skeleton,
  test_bench_manifest x3 (R14), test_cursor_file setUpClass,
  test_perf_evidence x2, test_typed_text_check_passes_when_
  fragment_is_visible (R12). Zero FAIL/ERROR lines name cdp,
  cdp_snapshot, redteam2, first_action, zen_dom, dom_act, or
  type_verification. The worker log
  ~/workspace/mochi-b2-6-discover.log survives and reads Ran 2380
  tests in 210.613s with the same failures=2, errors=8,
  skipped=17. The 1-test tally difference (2380 vs 2381) is
  unexplained: both logs are 356 lines with identical named
  tests, and the extra passing test is one dot early in the
  progress output (7 dots vs 8 before the first IME message).
  Cause not identified; it changes no failure, error, or skip,
  and every reviewed suite matches exactly (C1-C5), so it is
  recorded as inconclusive and non-material, see finding F5.
  C9 PASS on the failure set, with the tally note.
- C10, manifest verify, 00:26:36 +07, 1s: python3
  scripts/bench_manifest.py verify --manifest
  deploy-manifest.json --repo . on HEAD 5ee043d. Result: verify
  FAILED, 6 FAILs: source_commit (manifest d7d569b, repo
  5ee043d), source_content_sha256, git_status_clean (untracked
  council-1, council-2, council-3 review logs), artifact
  firefox, artifact firefox_bin, artifact geckodriver. Passing:
  bench_script ok (blob 80b00469...), fixture ok (blob
  bac2702e...), log exists and names run
  bench-20261122T020225Z-3d9270. The source_commit and
  source_content_sha256 FAILs are expected by construction: the
  manifest pins the bench commit d7d569b, so verifying it at any
  other HEAD fails those two checks. They do not indicate a
  manifest defect, but the final log omits them, see finding F2.
- C11, file counts, 00:33:00 +07, after clearing __pycache__:
  tracked 1542 (git ls-files), on-disk 1552 (find, excluding
  .git). The +10 is 4 untracked review logs (council-1,
  council-2, council-3, redteam, all written by concurrent
  reviewers in this worktree, not by the worker) plus 6
  gitignored native build files (native/keyboard-protocol.c,
  native/keyboard-protocol.h, native/pointer,
  native/pointer-protocol.c, native/pointer-protocol.h,
  native/wtype). Em dash and en dash scan: 0 U+2014 and 0 U+2013
  in scripts/cdp.mjs, tests/cdp_snapshot.mjs,
  tests/test_click3_redteam2.py,
  improvements/mochi-b2-6-final-log.md, and this log. C11 PASS.
- C12, procedures P1-P3: P1 is runnable as written: it names the
  five inputs (m0 url control plus m1-m4 email cases) with exact
  set values and expected read-backs, the headless Chromium
  command, the stop condition (all five read-backs match, any
  mismatch stops and is reported with actuals), and the evidence
  artifact (probe HTML, full JSON, Chromium version, time log,
  verdict line), and it cites the F1 method in the microgap log
  section 3, which exists (chromium --headless --disable-gpu
  --dump-dom, microgap log line 36). One count slip, see finding
  F3. P2 is partial: it names the scripts (arm_typed_flag,
  typed_flag, viewport_origin, ground mapping), the expectations
  (flag False then True, mapped point within 10 px of the live
  getBoundingClientRect center), the stop condition, and the
  evidence, but it gives no scratch-page HTML, no file path, and
  no Marionette session setup or eval command, so a live worker
  must invent the page and the harness. P3 is a pointer only,
  as the worker admits ("No procedure is written here beyond
  this pointer: the rung-2 worker writes it"). P2 and P3 are
  step-11 venue items with named owners (rung-2 live worker),
  not step-1 items, so this is a procedure-completeness finding,
  not a fix finding, see finding F4.

Other checks: the worker claim "no Codex run was launched, and
no laptop SSH was used in this session" and the native-helper
build claims ("pointer built OK", "wtype built OK") have no
artifact in the repo and cannot be verified from the repo;
the built binaries native/pointer and native/wtype do exist on
disk, gitignored, which is consistent with the build claim but
does not prove when they were built. Recorded as unverifiable,
see finding F6.

## 2. Findings

- F1 (minor, log accuracy): R4 coordinates are imprecise for two
  of the five defective proof tests. The final log says F2
  assertRaises DomActError is at tests/test_click3_redteam2.py:370;
  the assertRaises is at line 366 (inside
  test_stale_window_origin_refused_at_ground_time, which starts at
  :358). The final log says F4 y_range=(100, 120) is at :81; the
  comment is at :90 and the use is at :101. F5 at :133 and F6 at
  :418 are exact. The repairs themselves are real and the tests
  pass (C2, C5), so this does not change any R4 conclusion.
- F2 (log accuracy, the main finding): the final log understates
  the manifest verify FAIL set in section 0 rows 8 and 11 and in
  section 5. It lists only git_status_clean plus the 3 tool
  artifacts, and row 11 says "only FAILs are the missing tools
  dir (environmental)". Re-run by this reviewer (C10) shows 6
  FAILs, adding source_commit and source_content_sha256. Those
  two FAILs are expected by construction, because the manifest
  pins the bench commit d7d569b (scripts/bench_manifest.py lines
  271-279 compare manifest source_commit and digest against the
  current HEAD unconditionally), so they must have failed in the
  worker runs at 0400e86 and d88a472 as well, and they do not
  indicate a manifest defect. But the finish condition in row 11
  as written was not met as written, and the evidence table is
  incomplete. The R9 conclusion itself stands: source artifacts
  verify, the log names run bench-20261122T020225Z-3d9270, the
  tool FAILs are environmental, and the a1a672d pass stays
  unquotable as a gate. The worker prediction "after this log is
  committed, git_status_clean is expected to pass" is also not
  yet testable as written: at HEAD 5ee043d git_status_clean still
  FAILs, on the untracked council review logs in this worktree.
- F3 (minor, procedure accuracy): P1 says "write
  /tmp/mochi-b2-6-multi-probe.html with four inputs (ids m1, m2,
  m3, m4)" and then adds control m0 and requires "all five
  read-backs" to match. Four vs five is a count slip; all five
  inputs (m0-m4) are specified with exact values and expectations,
  so the procedure is still runnable.
- F4 (procedure completeness, owned): P2 gives no scratch-page
  HTML, file path, Marionette session setup, or eval command, so
  a live worker must invent the page and the harness. P3 is
  explicitly a pointer only, with no procedure. Both are step-11
  venue items, and the final log names the owner (the rung-2 live
  worker). This does not block the step-1 close-out, but P2 and
  P3 are not runnable as written today.
- F5 (minor, test coverage): no test pins a whitespace-only token
  ('a@b.com, ,c@d.com' must land as 'a@b.com,,c@d.com') or a
  token ending in TAB or FF ('a@b.com\t, c@d.com'). The template
  and both fakes trim TAB and FF, so the behavior should hold,
  but it is unpinned. The covered cases are: multi spaces,
  single comma, empty middle token, maxLength 15 ok, maxLength
  14 refuse, in both the node harness (4 cases) and the Python
  named test (4 cases).
- F6 (minor, evidence limits): three claims rest on sources this
  reviewer could not independently re-verify from the repo. R10
  cites cu.py:2280, cu.py:2110-2117, cu.py:2279 from the
  TESTREPAIR log; the citation exists there (lines 339-341) and
  cu.py:2278-2282 is the type_unverified path, but
  cu.py:2110-2117 was not independently checked as the DOM-gate
  locus. The "no Codex run, no laptop SSH" claim and the native
  helper build claims have no repo artifact. None of these
  affects the fix or any gate.
- F7 (inconclusive, non-material): full discover tally is 2381
  in this review vs 2380 in the worker run, with identical
  failures=2, errors=8, skipped=17 and identical FAIL/ERROR
  sets. Cause not identified. It changes no conclusion.

What was checked and found correct: the fix matches HTML
Standard 4.10.5.1.5 exactly (C6); the new Python test fails on
the old template and passes on the new one (C7); item-12 tests
4/4, RT2 52/52, node snapshot exit 0, test_cdp_snapshot 2/2,
neighbors 348/348 (C1-C5); remnant inventory R1-R14 coordinates
verified except F1 and F2 above; no em dash or en dash in the
fix files; the fix touches exactly 3 files, one per commit, with
the stated insertion and deletion counts.

Trust-pyramid note: the template, the node fake, and the Python
fake were all written by the same worker, so they encode the
same reading of the spec. The independent oracle is the live
probe P1, still owed and owned by Muse tong. The worker states
this itself in section 3.3 ("if live behavior differs from the
spec form, live wins"). This review confirms the harness-level
proof only; the fix is not live-proven, and must not be quoted
as live-proven until P1 passes.

## 3. Verdict

PASS, with findings F1-F7 above. The R8 fix is spec-correct,
discrimination-proven, and all targeted suites pass on the
committed tree. The findings are log-accuracy items (F1, F2),
a procedure count slip (F3), procedure incompleteness for
step-11 items with a named owner (F4), a small unpinned edge
(F5), unverifiable process claims (F6), and an unexplained
1-test tally difference with identical failure sets (F7). None
changes what the fix proves, none changes any remnant status,
and none reopens a step-1 item. Still owed, with owners: P1
live probe (Muse tong), P2/P3 live debts (rung-2 live worker,
step 11), R13 test_label_format (pill-label lane, 163e90c
author), R14 and R9 tool artifacts plus R12 tesseract
(environment owner), R10 F5 DOM-gate note (P5 implementer,
step 5).

Evidence (Lauren Tan standard): commands, outputs, hash, time,
elapsed are in section 1. HEAD 5ee043d25fd072586dfd9d51d767488c4f2d7c43.
Review started 2026-11-23 00:24 +07, finished 2026-11-23 00:33
+07. Longest check: full discover 290.389s (launched 00:26:15,
finished 00:31:07 +07).
