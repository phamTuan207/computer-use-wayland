# Re-review log: B2-6 step-1 close-out, fix round (independent)

Reviewer: re-review, independent. Worker graded: MOCHI-B2-6 fix round.
Worktree: ~/workspace/mochi-b2-6-work. HEAD at review start:
56118131e7fb67db81d527d4a3e10256e78b6004 (detached).
Base for the fix round diff: 82d2f9a.
Fix commits under review: 8ee4de1 (node ws token and TAB/FF),
afce25e (Python FakeInput url branch plus url case), adc7ae3
(Python ws token and TAB/FF cases), 25c4253 (manifest reporting
and coordinates in final log), 5611813 (P1 eight inputs, P2
sketch, soften 3.3, R-2/R-3 notes).
Start: 2026-11-23 00:46 +07 (Asia/Ho_Chi_Minh). All times below
are wall-clock +07 unless noted. Standing rules: no em dash
(U+2014) or en dash (U+2013) anywhere in this file, no personal
info, never ydotool, no live browser run, no push, no file
deleted, no worker file edited. Only this file is created by
this reviewer. Commit method: git add -- file then git commit -m,
never git commit -- paths.

Scope: the 5 fix commits on base 82d2f9a, fixing 9 items from
4 prior reviews (redteam 342f1ba KHONG PHA DUOC, council 1
5923497 PASS with 7 findings, council 2 82d2f9a CHUA PASS,
council 3 7ea8190 CHUA PASS). Docs read in full before work:
improvements/mochi-b2-6-redteam-log.md,
improvements/mochi-b2-6-council-1-log.md,
improvements/mochi-b2-6-council-2-log.md,
improvements/mochi-b2-6-council-3-log.md,
improvements/lauren-tan-workflow-20261122.md, and
git diff 82d2f9a HEAD. This reviewer grades the fix round,
not its own fix, so there is no self-review conflict.

Head note: HEAD moved during this review, from 5611813 to
f68d494, because a concurrent redteam round 2 committed its
log (2b25cad, then f68d494 to fill the hash). git diff 5611813
HEAD shows only that one added log file, no code or test
change, so all evidence gathered at 5611813 stands at f68d494
for the fix round. This reviewer formed its own verdict from
its own checks first, then read the redteam round 2 log
(improvements/mochi-b2-6-redteam-2-log.md, 2b25cad) as a
cross-check; where the two agree it is noted as independent
corroboration, not as proof.

## 0. Finish conditions (evidence contract, Lauren Tan)

Written BEFORE any check below was run. A confident reply
without evidence is a red flag. "Inconclusive" is honest, not
a pass.

| # | Check (command, from the worktree root unless noted) | Finish condition (expected output) |
| --- | --- | --- |
| RR-C1 | node tests/cdp_snapshot.mjs | exit 0, "all cdp snapshot, redaction, fill, payload, no_after and scope regressions pass" |
| RR-C2 | cd tests, PYTHONPATH=../scripts:. python3 -m unittest test_click3_redteam2 | Ran 52 tests, OK |
| RR-C3 | cd tests, PYTHONPATH=../scripts:. python3 -m unittest test_click3_redteam2.CdpSetValueTests.test_set_value_email_multiple_trims_each_token -v | Ran 1 test, OK |
| RR-C4 | python3 -m unittest tests.test_first_action.TestRun.test_session_after_is_scope_matching_not_screen tests.test_first_action.TestRun.test_fallback_after_is_scope_matching_not_screen tests.test_first_action.TestRun.test_after_without_result_after_captures_fresh_window tests.test_first_action.TestRun.test_screen_observation_key_batch_proceeds_to_session -v | Ran 4 tests, OK |
| RR-C5 | python3 -m unittest tests.test_cdp_snapshot | Ran 2 tests, OK |
| RR-C6 | cd tests, PYTHONPATH=../scripts:. python3 -m unittest test_first_action test_zen_dom test_dom_act test_type_verification test_click2_redteam test_codemode test_session_continuation test_session_policy | Ran 348 tests, OK |
| RR-C7 | python3 scripts/bench_manifest.py verify --manifest deploy-manifest.json --repo . on the clean tree at HEAD 5611813 | exit 1, git_status_clean ok, exactly 5 FAILs: source_commit, source_content_sha256, artifact firefox, artifact firefox_bin, artifact geckodriver; bench_script ok, fixture ok, log names run bench-20261122T020225Z-3d9270 |
| RR-C8 | Discrimination in a scratch copy (never touching the worktree): swap in the 0400e86 scripts/cdp.mjs template, run the new Python named test and the node suite, then restore the HEAD template and run again | Old template: new test FAILS, node exit 1. HEAD template: new test passes, node exit 0. Worktree git status clean except this untracked review log after |
| RR-C9 | Coordinate spot check at HEAD 5611813 by grep -n: node multiWsToken and multiTabFf lines and block range; Python FakeInput url branch lines, url_trim, multi_ws_token, multi_tab_ff lines, test end and module guard lines; final-log claims for R4 F2/F4, header :579-593, email branch :597-610, url else-if :611, node block :240-261 at d88a472 and :240-274 at adc7ae3, Python test :870-973 at d88a472 and end :998 guard :1001 at adc7ae3 | Every claimed coordinate matches, or the mismatch is listed as a finding with the true coordinate |
| RR-C10 | Full discover re-run (detached, log in /tmp, not in the worktree): cd tests, PYTHONPATH=../scripts:. python3 -m unittest discover -s . -p "test_*.py" | Tally recorded; FAIL/ERROR lines naming cdp, cdp_snapshot, redteam2, first_action, zen_dom, dom_act, type_verification are zero; every other FAIL/ERROR identified by cause and matched to R12/R13/R14 or listed as new |
| RR-C11 | No-dash scan: python3 scan for U+2014 and U+2013 in tests/cdp_snapshot.mjs, tests/test_click3_redteam2.py, improvements/mochi-b2-6-final-log.md, improvements/mochi-b2-6-rereview-log.md; file counts after clearing __pycache__ | 0 dash counts in each file; tracked (git ls-files) and on-disk counts reported separately |
| RR-C12 | P1 text check: read final-log section 4 P1 and confirm it names 8 inputs m0-m7 with exact set values and expected read-backs, the .value assignment step with the setAttribute warning, the m2 explicit gate with the Blink Multiple() branch, m5 I-1 with verbatim record and both decider outcomes, m6 NBSP kept, m7 VT kept; P2 labeled sketch with the four checks enumerated; section 4 heading honest; section 3.3 softened with the shared-misreading correction and the Blink risk | Each item present as written, or the gap is listed as a finding |

Verdict rule: PASS only if RR-C1 to RR-C6 pass exactly on
the committed tree, RR-C7 matches the final-log correction
claim (clean tree, git_status_clean ok, 5 FAILs), RR-C8
discriminates both ways, RR-C9 finds no material coordinate
error, RR-C10 shows zero in-scope failures, and every one
of the 9 fix items is verified present and correct in the
code and the log, with no new breakage. Any fix item wrong,
missing, or breaking another suite blocks PASS. A live
verdict is out of scope: no live browser run is allowed for
this reviewer, so P1 stays owed and the fix stays
harness-proven only.

## 1. Checks run (results, each run by this reviewer)

HEAD for all runs: 56118131e7fb67db81d527d4a3e10256e78b6004.
Base 82d2f9a. All times +07, Asia/Ho_Chi_Minh.

- RR-C1, node, 00:47:54 +07, about 1.2s: node
  tests/cdp_snapshot.mjs, exit 0, "all cdp snapshot, redaction,
  fill, payload, no_after and scope regressions pass". PASS.
- RR-C2, RT2, 00:47:59 +07, 2.631s: cd tests,
  PYTHONPATH=../scripts:. python3 -m unittest
  test_click3_redteam2. "Ran 52 tests in 2.631s, OK". PASS.
- RR-C3, named test, 00:47:59 +07, 0.195s: the same run with
  test_click3_redteam2.CdpSetValueTests.test_set_value_email_
  multiple_trims_each_token -v. "Ran 1 test in 0.195s, OK".
  PASS.
- RR-C4, item-12, about 00:48 +07, 0.007s: python3 -m unittest
  tests.test_first_action.TestRun.(4 tests) -v. "Ran 4 tests in
  0.007s, OK". PASS.
- RR-C5, test_cdp_snapshot, about 00:48 +07, 4.958s: python3
  -m unittest tests.test_cdp_snapshot. "Ran 2 tests in 4.958s,
  OK". PASS.
- RR-C6, neighbors, 00:48:07 +07, 9.913s: cd tests,
  PYTHONPATH=../scripts:. python3 -m unittest test_first_action
  test_zen_dom test_dom_act test_type_verification
  test_click2_redteam test_codemode test_session_continuation
  test_session_policy. "Ran 348 tests in 9.913s, OK". PASS.
- RR-C7, manifest verify, two runs:
  - In the real worktree at HEAD 5611813, about 00:48 +07,
    exit 1, 6 FAILs: source_commit (manifest d7d569b, repo
    5611813), source_content_sha256 (manifest 92891523..., repo
    7324498d...), git_status_clean (status lists only this
    untracked review log file), artifact firefox, artifact
    firefox_bin, artifact geckodriver. bench_script ok (blob
    80b00469...), fixture ok (blob bac2702e...), log names run
    bench-20261122T020225Z-3d9270. The 6th FAIL is only my own
    untracked log, as expected.
  - On a fully clean tree at HEAD 5611813 (linked worktree
    ~/mochi-b2-6-rr-clean, created by git worktree add because
    /tmp is 98 percent full and a git clone there failed with
    "No space left on device"; removed afterwards with git
    worktree remove --force), 00:48:46 +07, exit 1,
    git_status_clean ok (status=''), exactly 5 FAILs:
    source_commit (manifest d7d569b, repo 5611813),
    source_content_sha256 (manifest 92891523..., repo
    21a7eaf5...), artifact firefox, firefox_bin, geckodriver.
    bench_script ok, fixture ok, log names run
    bench-20261122T020225Z-3d9270. The FAIL categories match the
    final-log correction claim exactly. The repo digest differs
    from the 7324498d... quoted in the log (see note RR-N1):
    the digest is disk-state sensitive through ignored
    generated files, and the fresh checkout lacked the 6 native
    build artifacts. PASS on the categories; note RR-N1 records
    the digest precondition.
- RR-C8, discrimination, in the linked scratch worktree
  ~/mochi-b2-6-rr-clean at HEAD 5611813 (same worktree as
  RR-C7, removed afterwards; real worktree untouched):
  - Old template (scripts/cdp.mjs replaced by git show
    0400e86:scripts/cdp.mjs; git diff showed 37 lines, 10
    insertions, 27 deletions, the exact reverse of the fix),
    00:48:55 +07: Python named test "Ran 1 test in 0.102s,
    FAILED (failures=1)"; node tests/cdp_snapshot.mjs exit 1,
    first failure at tests/cdp_snapshot.mjs:247:8, error "value
    verification failed", mutation_may_have_occurred true.
  - HEAD template restored (byte-identical copy, git status
    clean, git diff HEAD empty), 00:49:01 +07: Python named
    test "Ran 1 test in 0.094s, OK"; node exit 0. PASS both
    ways, both harnesses.
  - Broken-fake leg (separate linked worktree
    ~/mochi-b2-6-rr-discrim at HEAD 5611813, removed
    afterwards): the 4 Python FakeInput url-branch lines
    (tests/test_click3_redteam2.py:910-913) deleted, 00:53:19
    +07: named test "Ran 1 test in 0.289s, FAILED
    (failures=1)", failure at the url_trim assert ("url
    whole-value trim failed", value
    '  https://example.com/a,b  '). File restored with git
    checkout, named test "Ran 1 test in 0.104s, OK". The new
    url pin is not fake: removing the branch fails the suite.
    PASS.
- RR-C9, coordinates, all verified by grep -n and direct
  reads at HEAD 5611813 (and at d88a472 via git show where
  the log cites that state):
  - scripts/cdp.mjs: header comment :579-593, email branch if
    at :597 with body through join at :610, url else-if at
    :611. Final log claims exact.
  - tests/cdp_snapshot.mjs: comment :240, multiEmail :245,
    multiMaxField :258, last assert :261 at d88a472, so block
    :240-261 exact for the d88a472 state; multiWsToken :265,
    multiTabFf :271, last assert :274, textField :275 at HEAD,
    so block :240-274 exact for the adc7ae3 state. Final log
    claims exact.
  - tests/test_click3_redteam2.py: FakeInput url branch
    :910-913 (else-if :910, while loops :911-912, slice :913),
    url_trim :957-958, multi_ws_token :959-960, multi_tab_ff
    :961-962, last assert :997-998, module guard at :1001.
    Named test has seven cases: multi_spaces, single_comma,
    multi_maxlen, multi_over, url_trim, multi_ws_token,
    multi_tab_ff. At d88a472: def at :870, last assert
    :971-973, module guard at :976, file 977 lines. Final log
    claims exact.
  - R4: F2 assertRaises DomActError at :366 (and :396), F4
    y_range comment at :90 and code at :101. Final log
    corrected claims exact.
  - R10 note: cu.py numbers are TESTREPAIR-tree coordinates,
    stated as such in the final log. Verified present.
  - Node fake url branch (tests/cdp_snapshot.mjs:20-21)
    trims TAB LF FF CR SPACE by regex; Python fake url branch
    (:910-913) trims char codes 9, 10, 12, 13, 32. Same set;
    the 10/13 entries are dead code after the global CR/LF
    strip in both harnesses, and no observable difference.
  - Tooling note, not a finding: the git diff 82d2f9a HEAD
    output as rendered to this reviewer showed one line as
    `" multi_ws_token: <redacted>`; a direct read of
    tests/test_click3_redteam2.py:959-960 shows the full line,
    `runCase('INPUT', 'email', '',` followed by
    `'a@b.com, ,c@d.com', -1, true),`. The file is correct;
    only the diff rendering redacted it.
- RR-C10, full discover, launched 00:46:xx +07 detached,
  log /tmp/mochi-b2-6-rereview-discover.log, finished
  00:50:28 +07 (log mtime 17:50:41Z): "Ran 2381 tests in
  203.193s, FAILED (failures=2, errors=41, skipped=17)".
  Tally 2381 matches all three council re-runs (worker 2380,
  difference still unattributed, same as council F7/F5/F3).
  The 2 FAILs are the known ones: test_label_format (R13)
  and test_typed_text_check_fails_when_fragment_is_absent
  (R12). The 41 errors split exactly into 8 known
  (test_a11y_skeleton x1, test_bench_manifest x3,
  test_cursor_file setUpClass x1, test_perf_evidence x2,
  test_typed_text_check_passes_when_fragment_is_visible x1,
  none caused by disk space) plus 33 caused by OSError
  Errno 28 "No space left on device" (59 occurrences in the
  log; /tmp is a 512M tmpfs at 98 percent, filled by other
  agents scratch copies, which this reviewer did not delete).
  Zero FAIL/ERROR lines name cdp, cdp_snapshot, redteam2,
  first_action, zen_dom, dom_act, or type_verification. No
  new in-scope failure. The fix round broke nothing.
- RR-C11, hygiene: python scan for U+2014 and U+2013 returns
  0 in tests/cdp_snapshot.mjs, tests/test_click3_redteam2.py,
  improvements/mochi-b2-6-final-log.md, and this log. File
  counts after clearing __pycache__: tracked 1547 (git
  ls-files), on-disk 1554 files (find -type f, excluding
  .git). Reconciled exactly: 1542 tracked at 5ee043d plus 5
  committed review logs since then (council-1, redteam round
  1, council-2, council-3, redteam round 2) equals 1547;
  1547 tracked plus 1 untracked (this log) plus 6 ignored
  native build artifacts (native/pointer, native/wtype,
  native/keyboard-protocol.c/.h, native/pointer-protocol.c/.h)
  equals 1554.
- RR-C12, P1 and procedure text, read first-hand in the
  final log (section 4 lines 432-555, section 3.3 lines
  346-368):
  - P1 names eight inputs m0-m7 with exact set values and
    expected read-backs (:452-493). LOAD-BEARING STEP states
    values are set by assigning el.value, never setAttribute,
    with the reason (:453-457). m2 is an EXPLICIT GATE with
    the Blink Multiple() branch (:461-468). m5 is the I-1
    decider with the spec-text expected value (line feed
    kept), both outcomes named, verbatim record required
    (:473-482). m6 NBSP kept (:483-486), m7 VT kept (:487-490).
    Step 3 stop condition is m0-m4, m6, m7 match, m5 recorded
    verbatim with its decider outcome (:498-503).
  - Finding RR-F1: step 4 verdict line (:506-508) says "PASS
    with all eight matched", which contradicts step 3. See
    section 2.
  - P2 is labeled SKETCH with the four checks enumerated
    (arm-false, arm-true, F9, F10) (:517-528). Section 4
    heading is honest ("P1 is a procedure, P2 is a sketch, P3
    is a deferral") (:432). P3 is labeled deferral (:555).
  - Section 3.3 is softened: the two checks are NOT
    independent in the sense that matters, a shared misreading
    passes both silently, only P1 catches common-mode error,
    with the Blink divergence as the concrete instance and m2
    as the case most likely to FAIL live (:356-364). No
    sentence still claims the wrong outcome is unexpressible.
  - R-2/R-3 notes are present (:192-208): multiple never read
    (correct per spec, unconditional rule), maxLength refusal
    as pre-existing C8 policy, re-grading belongs to the
    council.

## 2. Findings

- RR-F1 (BLOCKING, log-only, commit 5611813): P1 verdict
  line contradicts the m5 decider.
  Coordinates: improvements/mochi-b2-6-final-log.md lines
  498-508 (step 3 at :498-503, step 4 verdict line at
  :506-508).
  Reproduction (read-only, no live run): read lines 498-508
  of the final log at HEAD 5611813. Step 3 defines the stop
  condition as m0-m4, m6, m7 matching, with m5 recorded
  verbatim as a decider with no match condition. Step 4
  defines the verdict line as "PASS with all eight matched".
  The two cannot both hold, under EITHER live outcome for
  m5:
  - Live strips the line feed: step 3 says I-1 closes as
    engine-confirmed (a good outcome for the probe), but m5
    does not match its spec-text expected value (line feed
    kept), so step 4 says FAIL.
  - Live keeps the line feed: all eight match, so step 4
    says PASS, but step 3 says the template and both fakes
    must be corrected, which is not a PASS outcome for the
    fix.
  A runner following the procedure as written must choose
  between step 3 and step 4; there is no verdict line that
  is correct under both steps. This is in commit 5611813,
  the commit whose stated purpose is to fix P1, so the
  close-out round does not leave P1 executable as written.
  Fix: rewrite the step 4 verdict line to match step 3, for
  example "PASS with m0-m4, m6, m7 matched and m5 recorded
  with its decider outcome (stripped: I-1 closed; kept:
  template and fakes must be corrected), or FAIL naming the
  mismatched id and its actual value". No code change is
  needed. Independent corroboration: redteam round 2 found
  the same contradiction independently and broke on it
  (improvements/mochi-b2-6-redteam-2-log.md, commit 2b25cad,
  finding F1, same coordinates and same both-outcomes
  analysis). This reviewer reached the finding from its own
  first-hand read before reading that log.
- RR-N1 (residual note, not a break, not blocking): the
  manifest source_content_sha256 repo digest depends on
  ignored generated files on disk.
  Coordinates: scripts/sync-installed.py _source_bundle
  (lines 166-200, GENERATED_FILES added when present on
  disk); final log section 5 correction bullet ("at HEAD
  adc7ae3, on a fully clean tree (git status empty) ...
  repo 7324498d...").
  Evidence: this reviewer measured repo digest 7324498d...
  in the real worktree at 5611813 (generated files present)
  and 21a7eaf5... in a fresh linked worktree at the same
  HEAD 5611813 (generated files absent). The final log claim
  is TRUE in the worker tree state, but "fully clean tree
  (git status empty)" does not state the precondition (the 6
  ignored native build artifacts present on disk), and git
  status does not show ignored files. A verifier on a fresh
  checkout measures a different digest and may wrongly
  conclude the log is false. Suggested one-line note in the
  section 5 correction: the digest was measured with the
  generated native files present. No fix to the manifest or
  the code is needed. Independent corroboration: redteam
  round 2 residual R-1 (commit 2b25cad) reproduces the same
  two digests at adc7ae3.
- What was checked and found correct, item by item (9 items):
  1. Manifest reporting: 6 FAILs listed with causes in row
     11, section 2 R9, and section 5; the git_status_clean
     pass expectation withdrawn as a verify-pass claim;
     "verifies only at a d7d569b checkout" stated. Verified
     by RR-C7 in both trees.
  2. Coordinates: R4 F2 :366, F4 comment :90 code :101,
     header :579-593, email branch :597-610, url else-if
     :611, node block :240-261 at d88a472 and :240-274 at
     adc7ae3, Python test :870-973 at d88a472 and end :998
     guard :1001 at adc7ae3, cu.py as TESTREPAIR-tree
     coordinates. All verified exact by RR-C9.
  3. P1: eight inputs m0-m7, .value step, m2 gate, m5 I-1,
     m6 NBSP, m7 VT. All present and correct, except the
     step 4 verdict line, finding RR-F1.
  4. P2 labeled sketch with the four checks enumerated,
     section 4 heading honest. Verified by RR-C12.
  5. Section 3.3 softened, shared-misreading correction,
     Blink risk recorded. Verified by RR-C12.
  6. R-2 note: multiple never read, correct per spec.
     Verified present by RR-C12.
  7. R-3 note: maxLength refusal as pre-existing C8 policy.
     Verified present by RR-C12.
  8. Whitespace-only token and TAB/FF token-end cases in
     both harnesses (node multiWsToken :265, multiTabFf
     :271; Python multi_ws_token :959-960, multi_tab_ff
     :961-962). Verified present and passing by RR-C1 to
     RR-C3 and RR-C8.
  9. Python FakeInput url whole-trim branch (:910-913) plus
     url_trim case (:957-958). Verified present, correct
     against the node fake, and discriminating by RR-C8
     broken-fake leg.
  No other fix item is wrong or missing. The code in the 5
  fix commits needs no change. The only blocking defect is
  the one-line P1 verdict line in the final log (RR-F1).

## 3. Verdict

CHUA PASS. The code in the 5 fix commits is verified: all
targeted suites pass on the committed tree (node exit 0, RT2
52 tests OK, named test 1 test OK, item-12 4 tests OK,
test_cdp_snapshot 2 tests OK, neighbors 348 tests OK), the
discrimination round-trip holds both ways in both harnesses,
the new pins fail when the fakes are broken, every close-out
coordinate is exact, the manifest correction reproduces
(git_status_clean ok, 5 FAILs on a clean tree), and the full
discover shows zero in-scope failures. But the close-out
round does not pass as written, because finding RR-F1 is a
self-contradiction in the live procedure the round exists
to fix: P1 step 3 makes m5 a decider with no match
condition, step 4 demands "PASS with all eight matched",
and no live outcome for m5 satisfies both steps. A
procedure whose verdict condition cannot be executed as
written is broken as written, and P1 is the gate for live
closure of I-1. The required correction is one line in the
final log (rewrite the step 4 verdict line to match step 3),
plus the optional RR-N1 note on the digest precondition.
After those log corrections are committed, a re-review needs
only to check the corrected lines against this log, not to
re-run the suites, because the code evidence in section 1
already stands. Owner for the corrections: the B2-6 worker
(or the coordinator, as a log-only correction commit, no push
by this reviewer). Live confirmation (P1) remains owed
before the fix is quoted as live-proven, exactly as the
final log already states.

## 4. Evidence table (command, output, hash, Vietnam time, elapsed)

- RR-C1: node tests/cdp_snapshot.mjs, HEAD 5611813,
  00:47:54 +07, about 1.2s, exit 0, "all cdp snapshot,
  redaction, fill, payload, no_after and scope regressions
  pass".
- RR-C2: cd tests, PYTHONPATH=../scripts:. python3 -m
  unittest test_click3_redteam2, 00:47:59 +07, 2.631s, "Ran
  52 tests in 2.631s, OK".
- RR-C3: named test alone, 00:47:59 +07, 0.195s, "Ran 1
  test in 0.195s, OK".
- RR-C4: item-12 4 tests, about 00:48 +07, 0.007s, "Ran 4
  tests in 0.007s, OK".
- RR-C5: python3 -m unittest tests.test_cdp_snapshot,
  about 00:48 +07, 4.958s, "Ran 2 tests in 4.958s, OK".
- RR-C6: neighbors 8 modules, 00:48:07 +07, 9.913s, "Ran
  348 tests in 9.913s, OK".
- RR-C7: manifest verify at HEAD 5611813, about 00:48
  +07, exit 1, 6 FAILs in the real worktree (git_status_clean
  only on this untracked log); clean linked worktree
  00:48:46 +07, exit 1, git_status_clean ok, 5 FAILs
  (source_commit, source_content_sha256, 3 tool artifacts),
  bench_script ok, fixture ok, log names run
  bench-20261122T020225Z-3d9270. Repo digest 7324498d... in
  the real worktree, 21a7eaf5... in the fresh checkout
  (see RR-N1).
- RR-C8: discrimination in linked scratch worktrees at HEAD
  5611813. Old template 0400e86, 00:48:55 +07: Python named
  test FAILED (failures=1, 0.102s), node exit 1, first
  failure tests/cdp_snapshot.mjs:247:8, "value verification
  failed". Restored HEAD template, 00:49:01 +07: Python named
  test OK (0.094s), node exit 0. Broken-fake leg (Python url
  branch lines 910-913 deleted), 00:53:19 +07: named test
  FAILED (failures=1, 0.289s) at the url_trim assert, value
  '  https://example.com/a,b  '; restored file OK (0.104s).
  Real worktree untouched; scratch worktrees removed after.
- RR-C9: coordinate spot checks by grep -n and direct reads
  at HEAD 5611813 and d88a472 (git show). All claims exact;
  see section 1.
- RR-C10: full discover, launched 00:46 +07 detached, log
  /tmp/mochi-b2-6-rereview-discover.log, finished 00:50:28
  +07: "Ran 2381 tests in 203.193s, FAILED (failures=2,
  errors=41, skipped=17)". FAILs: test_label_format (R13),
  test_typed_text_check_fails_when_fragment_is_absent (R12).
  Errors: 8 known plus 33 Errno 28 No space left on device
  (/tmp 98 percent full). Zero in-scope FAIL/ERROR lines.
- RR-C11: dash scan 0 U+2014 and 0 U+2013 in all 4 files.
  Counts after clearing __pycache__: tracked 1547 (git
  ls-files), on-disk 1554 files; reconciled exactly (1547
  plus 1 untracked log plus 6 ignored native artifacts).
- RR-C12: P1/P2/P3/3.3 text audit, final log lines 346-368
  and 432-555. All items present except RR-F1 (step 4
  verdict line, lines 506-508).
- HEAD moved during this review (5611813 to f68d494) by
  concurrent redteam round 2 commits 2b25cad and f68d494,
  touching only improvements/mochi-b2-6-redteam-2-log.md.
  All evidence above is at 5611813 and stands at f68d494.
- Real worktree git status clean apart from this untracked
  review log at every check. No worker file modified, no
  push, no live run, no file deleted except gitignored
  __pycache__ dirs cleared before counting, per the brief.

Elapsed: task received 00:46:26 +07; finish conditions
written by 00:47 +07; RR-C1 to RR-C7 00:47-00:49 +07; RR-C8
00:48-00:49 +07 plus broken-fake leg 00:53 +07; RR-C10
discover 00:46-00:50 +07 (203.193s run); fact checks and log
write 00:50-00:56 +07.

## 5. Commit record (this reviewer's own commit, no push)

- This log file: improvements/mochi-b2-6-rereview-log.md, commit
  dd322652d05a28eda6f7bca87d4af5e52ddef281 (dd32265). The hash
  line was filled by a follow-up commit on this same file. No
  push was made (per the brief).
