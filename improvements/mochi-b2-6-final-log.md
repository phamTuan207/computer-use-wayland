# Worker MOCHI-B2-6 final log: step-1 close-out, AMEND4 remnants at 36364b1

Owner: the owner. Worker: MOCHI-B2-6, for batch 2 item B2-6.
Branch: todolist-push. Worktree: ~/workspace/mochi-b2-6-work.
Base HEAD at start: 0400e86 (0400e869d4275fe58286412f8acde1824b1e3623).
Fix HEAD at log write: d88a472 (three fix commits, section 6).
Start: 2026-11-23 00:09 +07 (Asia/Ho_Chi_Minh). All times below are
wall-clock +07 unless noted. Standing rules: no em dash (U+2014) or
en dash (U+2013) anywhere in this file, no personal info, never
ydotool, no live browser run by this worker, no file deleted, no
push. Commits by this worker use git add -- file then git commit -m,
never git commit -- paths.

Task (B2-6, coord commit f9a1a9f): step-1 close-out. Read all step-1
remnants at HEAD 36364b1, fix what can be fixed from the repo, write
what needs a live browser as procedures for Muse tong, do not run
live. Re-coordinate every item at the HEAD in force while working
(0400e86, then d88a472 after the fix commits).

Restart note: the previous B2-6 attempt (worktree in /tmp, now gone)
never reported a final result. Its partial report (a tests/
cdp_snapshot.mjs edit at 18:41 22/11, council 1 PASS for fix R2,
council 2 PASS for R4a and R4b, redteam could not break it, full
discover still running, final log not written) could NOT be verified:
no commit, no log file, no worktree survives, and the labels R2/R4a/
R4b match no artifact in the repo (R2 in scripts/cdp.mjs:621 is the
amend3 step-1 setter-write rule; R4a/R4b in tests/
test_click2_redteam.py:286,299 are the unverified-ok tests, not
cdp_snapshot items). Nothing from that partial report is trusted
here. Every item below was rediscovered from scratch.

## 0. Finish conditions (evidence contract, Lauren Tan)

Each check below names its command and its expected output BEFORE
the check counts. The targets in rows 1-8 were fixed before this
session ran: they are the targets set by the prior close-out logs
(C4 4ac9320, W-S1CLOSE 3e64547, TESTREPAIR 77c72be) and by the task
brief, recorded here verbatim. Rows 9-11 ran after this section was
written. A confident reply without evidence is a red flag.
"Inconclusive" is honest, not a pass. This worker does NOT grade its
own fix: outputs below are facts (commands, outputs, hashes, times);
the verifier grades the fix. No self-review.

| # | Check (command) | Finish condition (expected output) |
| --- | --- | --- |
| 1 | python3 -m unittest tests.test_first_action.TestRun.(4 item-12 tests) -v | Ran 4 tests, OK (3 surviving item-12 tests plus the P2 replacement test, see R1) |
| 2 | cd tests, PYTHONPATH=../scripts:. python3 -m unittest test_click3_redteam2 | Ran 51 tests OK before the fix, Ran 52 tests OK after (one new named test) |
| 3 | node tests/cdp_snapshot.mjs | exit 0, all regressions pass |
| 4 | python3 -m unittest tests.test_cdp_snapshot | Ran 2 tests, OK |
| 5 | cd tests, PYTHONPATH=../scripts:. python3 -m unittest test_first_action test_zen_dom test_dom_act test_type_verification test_click2_redteam test_codemode test_session_continuation test_session_policy | Ran 348 tests, OK |
| 6 | cd tests, PYTHONPATH=../scripts:. python3 -m unittest discover -s . -p "test_*.py" (detached, log ~/workspace/mochi-b2-6-discover.log) | Full tally recorded; zero FAIL/ERROR lines naming cdp, cdp_snapshot, redteam2, first_action, zen_dom, dom_act, type_verification; every other FAIL/ERROR identified by cause |
| 7 | git ls-remote origin amend4-codex | 06a34e8610a9467c3884f6dd7a567293c747da45 (V-Z2 still landed) |
| 8 | python3 scripts/bench_manifest.py verify --manifest deploy-manifest.json --repo . | Source artifacts (bench_script, fixture) ok, log names the run; any FAIL explained by cause |
| 9 | Committed-tree re-run (after fix commits): rows 1-4 again on HEAD d88a472 | Same outputs as rows 1-4 |
| 10 | Discrimination round-trip: old template from 0400e86 restored to scripts/cdp.mjs, run new Python test, then restore HEAD version | Old template: new test FAILS. Restored template: new test passes. Worktree clean after |
| 11 | Manifest re-verify on the clean committed tree (row 8 again after the log commit) | git_status_clean ok; only FAILs are the missing tools dir (environmental) |

## 1. What step 1 is

Step 1 is the AMEND4 close-out, final direction
(improvements/worker-click3-final-direction-log.md) section 3 step 1
and section 6 worker 3: (a) run the four item-12 regression tests
and record PASS on the new code (cbab398); (b) confirm the Codex-lane
item-12 delivery or re-commission it (V-Z2); (c) round-3 council:
patch-vs-rewrite judgment per AMEND4 item under the 06:07 criterion,
and repair or re-verify the defective proof tests for items 3, 4,
5-6 (B5 lift limb ii). The kill rule at reconciliation applies at
the round-3 judgment, not here.

Docs read in full before work: docs/zen-error-fix-todolist-20261121.md
(sections 4.1-4.29, Phase 5), improvements/
worker-click3-final-direction-log.md (sections 0, 1, 3, 6, 7),
improvements/worker-click4-step1-closeout-log.md (4ac9320),
improvements/w-step1-closeout-log.md (3e64547), improvements/
worker-click3-item8-microgap-log.md (36364b1 itself), improvements/
worker-click3-amend4-log.md, improvements/
worker-amend4-closeout-log.md, improvements/
worker-click3-testrepair-log.md (77c72be), improvements/
worker-click3-r3c1-review-log.md, improvements/
worker-click3-r3c2-review-log.md, improvements/
worker-click3-r3c3-review-log.md, improvements/
worker-click3-r3rt-review-log.md, improvements/
lauren-tan-workflow-20261122.md (311eacd).

## 2. Remnant inventory at 36364b1, re-coordinated at 0400e86

Coordinates are file and line at HEAD 0400e86 unless the row says
d88a472 (after the fix commits). Status DONE-BEFORE means landed
before 36364b1 and re-verified in this session.

### R1. Step 1 (a): item-12 regression tests, DONE-BEFORE, re-verified

- The four tests landed in cbab398, tests/test_first_action.py at
  0400e86: test_session_after_is_scope_matching_not_screen (:1372),
  test_fallback_after_is_scope_matching_not_screen (:1398),
  test_after_without_result_after_captures_fresh_window (:1418).
  The fourth name changed after 36364b1: P2 (292753f) DELETED the
  pre-overlay screen-scope key/type refusal and replaced
  test_screen_observation_key_batch_refused_before_overlay with
  test_screen_observation_key_batch_proceeds_to_session (:1436),
  per the final direction section 2 item (f): the refusal changed
  form into snapshot binding, enforced by desktop_act. This is a
  deliberate protocol change, not a breakage.
- Re-run 2026-11-23 00:14:41 +07, 0s: Ran 4 tests in 0.007s, OK
  (the 3 surviving tests plus the P2 replacement). Finish
  condition row 1 met.

### R2. Step 1 (b): Codex-lane item-12 confirmation (V-Z2), DONE-BEFORE, re-verified

- git ls-remote origin amend4-codex, 2026-11-23 00:16:47 +07:
  06a34e8610a9467c3884f6dd7a567293c747da45, matching the resume log
  (2de4c31), the C4 record, and the W-S1CLOSE record. The Codex
  lane is LANDED. No re-commission needed. The VM-vs-Codex shape
  difference (VM captures a fresh window when no scope-matching
  after exists; Codex leaves after None; Codex pre-overlay refusal
  stricter) stays as recorded in the reconcile log (e1a4e77,
  verdict KEEP VM); judging it belongs to the round-3 council,
  not this worker. No Codex run was launched, and no laptop SSH
  was used in this session (the ls-remote hash match plus the two
  prior independent verifications is the evidence).
- Finish condition row 7 met.

### R3. Step 1 (c): round-3 council patch-vs-rewrite judgment, DONE-BEFORE

- Council C1/C2/C3 and redteam all landed before 36364b1:
  improvements/worker-click3-r3c1-review-log.md (598 lines),
  worker-click3-r3c2-review-log.md (783 lines),
  worker-click3-r3c3-review-log.md (657 lines),
  worker-click3-r3rt-review-log.md. Verdicts agree: GO 7 (items 1,
  2, 8, 9, 10, 11, 12), AMEND 5 (items 3, 4, 5, 6, 7), BLOCK 0.
  Patch-vs-rewrite summary (amend4 log, section "Patch vs remove
  vs redesign"): patch items 1, 2, 3, 4, 8; patch with a removal
  items 5-6 and 11; redesign items 7 and 12; tests only items 9,
  10. No item needs a rewrite instead of its patch or redesign.
  Nothing left to judge here.

### R4. Defective proof tests F2, F3, F4, F5-behavior, F6, DONE-BEFORE, re-verified

- Repaired by TESTREPAIR-B (43b27a1, ancestor of 36364b1) exactly
  as the council specified: F2 assertRaises DomActError
  (tests/test_click3_redteam2.py:370), F3 split into a stale-value
  documentation test (:316) plus a ground-time refusal test
  (:358), F4 y_range=(100, 120) (:81), F5 wired-path rewrite
  (:133), F6 guarded forge plus F7-shaped value assertion (:418).
- Re-run 2026-11-23 00:14:43 +07, 2s: the RT2 set Ran 51 tests in
  1.384s, OK (before the fix). After the fix the set is Ran 52
  (row 9). The 5 adjudicated defectives are gone as failures.
  Finish condition row 2 met (pre-fix half; post-fix half in
  section 5).

### R5. Redteam residual C8: maxLength pre-check measures sanitized length, DONE-BEFORE, re-verified

- Fixed by TESTREPAIR-C8 (7372ddd, ancestor of 36364b1):
  scripts/cdp.mjs pre-check compares sanitized.length; named test
  test_set_value_maxlength_uses_sanitized_length in tests/
  test_click3_redteam2.py:777. Re-run in the CdpSetValueTests
  batch, 2026-11-23 00:16:40 +07: ok, with the F1 test and the new
  multiple test (Ran 3 tests in 0.492s, OK).

### R6. Redteam residual C7: typed-flag pre-locked getter hardening, DONE-BEFORE, re-verified

- Fixed by TESTREPAIR-C7 (ee883bc, ancestor of 36364b1): per-arm
  unpredictable property name, re-arm trust branch deleted; named
  test test_typed_flag_not_forgeable_via_prelocked_getter in
  tests/test_zen_dom.py:825 (plus the window-property test :793).
  Both are inside the neighbor batch (row 5, Ran 348, OK).

### R7. Redteam residuals C12: scope-less window meta, DONE-BEFORE, re-verified

- Fixed by TESTREPAIR-C12 (2ec3d67, ancestor of 36364b1):
  _scope_after restored with the scopeless-window fix, plus 3
  named tests in tests/test_first_action.py:1455, 1484, 1505.
  All three are inside the neighbor batch (row 5, Ran 348, OK).

### R8. ITEM8 microgap known limitation: email multiple per-token trim, OPEN at 36364b1, FIXED in this session

- The 36364b1 commit IS the microgap log. Its section 6 records
  the limitation as out of scope there: for email with multiple,
  the spec strips each comma-separated token, but the fix trims
  only the whole value ends, matching Codex. At 0400e86 the gap
  was still present: grep for multiple in scripts/cdp.mjs and
  tests/cdp_snapshot.mjs found only an unrelated scope-selector
  test line (tests/cdp_snapshot.mjs:497). No multiple handling
  existed in the template or in either fake.
- Fix in this session (section 3): scripts/cdp.mjs per-token
  trim for email, tests/cdp_snapshot.mjs fake plus 4 cases,
  tests/test_click3_redteam2.py named test. Commits 3532bfd,
  e500923, d88a472. Live confirmation of the per-token behavior
  in a real browser is still owed (procedure P1, section 4).
  This is the only step-1 remnant that was still open and
  repo-fixable.

### R9. CB-9 manifest for the bench build a1a672d, NOT LOCKED (step 3, not step 1), superseded by a re-run manifest

- C4 proved the a1a672d manifest cannot be locked retroactively:
  the mechanism landed after the bench ran, and the installed
  tree at bench time is gone. That stands: deploy-manifest.json
  contains no reference to a1a672d (grep count 0).
- What changed after 36364b1: a bench RE-RUN at d7d569b got its
  manifest locked in 5f86046 (not an ancestor of 36364b1, ancestor
  of HEAD 0400e86): run_id bench-20261122T020225Z-3d9270, wall
  12.6852s, PASS, visions_used 2, log improvements/
  worker-click4-bench-manifest-log.md. The direction step-3 gate
  ("lock the manifest before the pass is quoted as a gate") is
  therefore satisfied by the d7d569b re-run, not by a1a672d. Quote
  the re-run, never a1a672d, as the gate.
- Verify at HEAD (row 8), 2026-11-23 00:17:17 +07, 2s:
  artifact bench_script ok (blob
  80b00469c4676d7a9a8934626b6bf66ed2a5aeee), artifact fixture ok
  (blob bac2702efa375ad330cce8130df40d8025d86261), log exists and
  names the run. FAILs: git_status_clean (my 3 uncommitted fix
  files at that time; re-verify in row 11 on the clean committed
  tree) and 3 tool artifacts (firefox, firefox-bin, geckodriver)
  whose paths under /home/hatch/workspace/tools/ no longer exist
  (ls: No such file or directory; the tools dir is gone after the
  VM restart). The 3 tool FAILs are environmental, not a manifest
  defect: the source-pinned artifacts still verify.

### R10. TESTREPAIR note 1: F5 DOM-gate finding, RECORDED, not a step-1 fix

- The pixel band is never the decider through the full wired
  path; the DOM type_check decides either way (cu.py:2280,
  cu.py:2110-2117, cu.py:2279 in the TESTREPAIR log). This is a
  design note for P5/CB-1 (step 5), not a step-1 defect. No code
  changed here. Left for the P5 implementer.

### R11. Live debts recorded in the AMEND4 log, venue step 11, procedures in section 4

- "The 2-vision benchmark as a whole, and the F1/F8/F9 live-DOM
  runs: owed from the redteam round." F1 live is done twice
  (fcc-f1-live-confirm f4dcfa3, W-S1CLOSE section 4). Items 5-6
  live hyprctl re-read is done (W-S1CLOSE section 6). Still owed:
  F8 live-DOM run (test_arm_typed_flag_misses_iframe_targets,
  tests/test_click3_redteam2.py:509) and F9/F10 live-DOM runs
  (geometry, item 1, cc964b2), and the 2-vision benchmark as a
  whole (step 11 rung 2). Procedures P2 and P3, section 4.

### R12. Environmental: tesseract failures in the full discover, PRE-EXISTING, out of scope

- test_tc02_controller: 1 failure
  (test_typed_text_check_fails_when_fragment_is_absent) plus 1
  error (test_typed_text_check_passes_when_fragment_is_visible),
  both "tesseract is unavailable; refusing to assume text
  presence". Same as the AMEND4 log's 2 environmental tesseract
  failures. Installing a system package is out of this pass.

### R13. NEW failure at HEAD, not step-1: test_label_format, owned by the pill-label lane

- tests/test_overlay.py:163 asserts overlay._label_for('Muse',
  'BiDi') == 'Muse via BiDi'. Commit 163e90c (HEAD~1, 2026-11-23
  00:04:52 +07, "overlay: pill label always plain 'Computer use
  active', no agent jargon") changed only scripts/overlay.py and
  did NOT touch tests/test_overlay.py. At 36364b1 the test passed
  (same expectation in the 36364b1 file, line 25); at HEAD the
  production function changed and the test was not updated, so
  the discover FAILs it. Not a step-1 remnant, not caused by this
  fix. Left for the pill-label lane (163e90c author) to update
  the test expectation or restore the label. This worker did not
  touch it: out of scope, and editing another lane's fresh change
  without its context risks scope creep.

### R14. NEW errors at HEAD, not step-1: test_bench_manifest x3, environmental

- test_verify_passes_with_log_then_fails_on_tamper,
  test_write_pins_commit_and_artifacts,
  test_write_refuses_dirty_checkout all ERROR at
  scripts/bench_manifest.py:177 _sha256(FIREFOX): the tools dir
  /home/hatch/workspace/tools/ no longer exists. Same cause as
  the R9 tool artifact FAILs. They fail identically on a clean
  tree at this HEAD; the missing tools dir is the cause, not any
  code change. Left for the environment owner (reinstall the
  tools or point FIREFOX at an existing binary).

## 3. The fix: email multiple per-token trim (R8)

### 3.1 Spec, verified first-hand

HTML Standard, Email state (4.10.5.1.5), value sanitization
algorithm, read from https://html.spec.whatwg.org/multipage/
input.html (crawled 2026-11-22 17:13 UTC) by this worker:

1. Split on commas the element's value, strip leading and trailing
   ASCII whitespace from each resulting token, if any, and let the
   element's values be the resulting list of tokens, maintaining
   the original order.
2. Set the element's value to the result of concatenating the
   element's values, separating each value from the next by a
   single U+002C COMMA character, maintaining the list's order.

ASCII whitespace per the Infra Standard: TAB U+0009, LF U+000A,
FF U+000C, CR U+000D, SPACE U+0020. The algorithm is the email
state's sanitization algorithm: it does not branch on the multiple
attribute, so it holds for a plain email field too. The multiple
change steps (same section) strip each value the same way and
rejoin with a single comma, consistent.

### 3.2 The gap, proven failing-first

Before the fix, scripts/cdp.mjs trimmed only the whole value ends
for url/email. For a multiple email value '  a@b.com , c@d.com  ',
the old sanitized form kept the inner space ('a@b.com, c@d.com')
while the engine (per the algorithm above) lands 'a@b.com,c@d.com',
so set_value reported ok:false 'value verification failed' on a set
the engine accepted: a false refusal, same class as the C8
maxLength residual.

Failing-first proof, 2026-11-23 00:15:50 +07, 0s, before touching
scripts/cdp.mjs (fake plus cases edited first, production
untouched): node tests/cdp_snapshot.mjs exited 1, first failure at
tests/cdp_snapshot.mjs:247 (the multiEmail ok assert), result
{"ok":false,"completed":0,"error":"value verification failed",
"mutation_may_have_occurred":true}.

### 3.3 Design (trust pyramid)

This fix is level 2, a deterministic check, not a text rule. The
behavior is pinned by two independent checks (node harness plus
Python named test), both running the REAL template against a
spec-faithful fake. No new text rule was added anywhere (no AGENTS.md
change). The design choice that makes the wrong outcome
unexpressible: the template computes sanitized from the same
per-token rule the fake models, and the read-back compares e.value
against sanitized, so any future drift between the two fails loudly
in the harness instead of silently in production. The live probe
(procedure P1) is level-3 validation, still owed: if live behavior
differs from the spec form, live wins and the template plus fake
must be corrected to the live behavior.

### 3.4 Edits (coordinates at d88a472)

Commit 3532bfd, scripts/cdp.mjs (27 insertions, 10 deletions):
- Lines 581-592: header comment now states the email per-token
  rule with the spec cite (4.10.5.1.5) and that the maxLength
  pre-check measures the sanitized length.
- Lines 598-611: the email branch splits on comma (char code 44),
  trims each token ends over char codes 9, 12, 32, rejoins with a
  single comma; the url branch keeps the whole-value trim
  (unchanged behavior). Char-code form throughout, no regex
  escapes, so the template needs no backslash doubling when it is
  re-evaluated. CR/LF are already stripped above, so only TAB, FF
  and SPACE can remain at token ends.
- The maxLength pre-check (sanitized.length) and both read-back
  checks need no change: they already operate on sanitized.

Commit e500923, tests/cdp_snapshot.mjs (29 insertions, 1 deletion):
- Lines 14-20: FakeInput setter models the engine rule (email:
  split on commas, trim each token, rejoin; url: whole trim).
- Lines 235-261: four new cases after the emailField case:
  multiEmail (multiple, '  a@b.com , c@d.com\t' lands as
  'a@b.com,c@d.com', events input then change), singleEmailComma
  (plain email, 'a@b.com, b@c.com' lands as 'a@b.com,b@c.com'),
  multiEmptyToken ('a@b.com,,c@d.com' preserved, empty middle
  token kept), multiMaxField (multiple, maxLength 15, raw 21 chars
  lands as 'a@b.com,c@d.com', proving the pre-check measures the
  per-token-trimmed length).

Commit d88a472, tests/test_click3_redteam2.py (107 insertions):
- Lines 870-975: new named test
  test_set_value_email_multiple_trims_each_token in
  CdpSetValueTests, same driver shape as the C8 maxlength test,
  plus a multiple flag per case. Its FakeInput models the email
  per-token rule. Four cases: multi_spaces (ok true, value
  'a@b.com,c@d.com', events input then change), single_comma (ok
  true, 'a@b.com,b@c.com'), multi_maxlen (maxLength 15, ok true,
  'a@b.com,c@d.com'), multi_over (maxLength 14, ok false,
  'value exceeds maxlength').

No other file changed. No em dash or en dash in any changed file
(python scan, 0 counts for U+2014 and U+2013 in all three files).

## 4. Live procedures for Muse tong (this worker ran no live browser)

Every procedure ends with a checkable artifact (probe output plus a
verdict line), not prose alone. Run each in a quiet window, never
touching the owner's tabs: new scratch tab or headless Chromium
only. Stop conditions are stated per procedure.

### P1. Email-multiple live probe (for the R8 fix; MUST pass before the fix is quoted as live-proven)

Goal: prove in a real browser that a multiple email input set to
'  a@b.com , c@d.com  ' reads back 'a@b.com,c@d.com', and that a
plain email input set to 'a@b.com, b@c.com' reads back
'a@b.com,b@c.com'. If live behavior differs, LIVE WINS: correct
the template and the fake to the live behavior, re-run rows 2-4,
and do not quote the fix as proven until the probe passes.

Setup (same F1 method as the microgap log section 3 and W-S1CLOSE
sections 4-5; headless Chromium only, no user tab):

1. On the laptop, write /tmp/mochi-b2-6-multi-probe.html with four
   inputs (ids m1, m2, m3, m4) and a script that sets values and
   records JSON in pre#result:
   - m1: type email, multiple, set '  a@b.com , c@d.com\t',
     expect 'a@b.com,c@d.com'.
   - m2: type email (no multiple), set 'a@b.com, b@c.com',
     expect 'a@b.com,b@c.com'.
   - m3: type email, multiple, set 'a@b.com,,c@d.com',
     expect 'a@b.com,,c@d.com'.
   - m4: type email, multiple, maxlength 15, set
     '  a@b.com , c@d.com  ', expect 'a@b.com,c@d.com'.
   - Control m0: type url, set '  https://example.com  ',
     expect 'https://example.com' (regression control for the
     existing trim).
2. Run: chromium --headless --disable-gpu --dump-dom
   file:///tmp/mochi-b2-6-multi-probe.html (record the Chromium
   version from the run).
3. Read pre#result JSON. Stop condition: all five read-backs match
   the expected values above. Any mismatch stops the procedure:
   record the actual read-back per id, do not adjust the expected
   values to fit, and send the mismatch back to the B2-6 lane.
4. Evidence to collect: the probe HTML file, the full JSON output,
   the Chromium version, the time log (+07), and one verdict line
   (PASS with all five matched, or FAIL naming the mismatched id
   and its actual value).
5. Optional second leg (same quiet window, only if a live Zen
   scratch tab is already open for other work): run the same five
   sets through the live Zen DOM on a NEW scratch tab beside the
   owner's tabs, using the shipped set_value path, and record the
   same JSON. Never navigate or type into any of the owner's tabs.
   If no scratch tab is open, skip this leg; the headless Chromium
   leg is the gate.

### P2. F8/F9 live-DOM runs (AMEND4 live debt, venue step 11)

Goal: run the same checks the node tests prove, against a real
browser DOM: F8 (typed-flag arm in an iframe target), F9/F10
(geometry: factor handling, one unit system, CSS px closure).

1. Build a scratch page with an iframe target plus a message
   input (same shape as the node fakes in tests/
   test_click3_redteam2.py:509 and tests/test_zen_dom.py).
2. Through the live Zen Marionette session (or headless Chromium
   if Zen is busy), evaluate the REAL arm_typed_flag and
   typed_flag scripts from scripts/zen_dom.py on the scratch page:
   arm the iframe field, set its value by page script with zero
   trusted input events, read the flag (expect False), then set
   it with a trusted input event and read the flag (expect True).
3. For F9/F10: evaluate the REAL viewport_origin and ground
   mapping from scripts/zen_dom.py and scripts/dom_act.py on the
   scratch page geometry, and compare the mapped point against
   the element's live getBoundingClientRect center (expect within
   10 px, same bar as the node tests).
4. Stop condition: all four outcomes match the node-test
   expectations. Any mismatch stops the procedure and is reported
   with the actual numbers, not adjusted.
5. Evidence to collect: the scratch page, the evaluated scripts
   (commit hash of the zen_dom.py they came from), the JSON
   outputs, the time log, and a verdict line per check.

### P3. 2-vision benchmark as a whole (step 11 rung 2; pointer, not a step-1 procedure)

- The benchmark runs under the step-11 acceptance ladder
  (final direction section 4), not as a step-1 live session.
  The quotable bench evidence is the d7d569b re-run manifest
  (R9): run_id bench-20261122T020225Z-3d9270, wall 12.6852s, PASS,
  visions_used 2. A fresh live run needs a quiet window, owner
  approval per run, and the runbook (clone2), and it must use
  the CB-9 manifest habit (deploy-manifest.json locked for the
  run) so the pass is quotable as a gate. No procedure is
  written here beyond this pointer: the rung-2 worker writes it.

## 5. Evidence table (Lauren Tan standard: command, output, hash, Vietnam time, elapsed)

Native helpers (gitignored build artifacts, built in-worktree
because the full scripts/build.py needs gtk4-layer-shell and
wayland-protocols, both missing on this VM; pointer and wtype need
only wayland-client and xkbcommon, both present):
- pointer: wayland-scanner pointer.xml plus cc -O2, 00:14:17 +07,
  elapsed 442ms, HEAD 0400e86, output "pointer built OK".
- wtype: wayland-scanner keyboard.xml plus patch vendor/wtype
  main.c with keyboard-correction.patch plus cc -O2, 00:14:20
  +07, elapsed 551ms, HEAD 0400e86, output "wtype built OK".
  Warnings only (unused parameters in vendored main.c).
  git status after the build: clean (binaries gitignored).

Pre-fix verification (HEAD 0400e86, uncommitted tree clean):
- Item-12 tests: python3 -m unittest tests.test_first_action.
  TestRun.(4 tests) -v, 00:14:41 +07, 0s, "Ran 4 tests in 0.007s,
  OK".
- RT2 set: cd tests, PYTHONPATH=../scripts:. python3 -m unittest
  test_click3_redteam2, 00:14:43 +07, 2s, "Ran 51 tests in
  1.384s, OK".
- node tests/cdp_snapshot.mjs, 00:14:27 +07, 1s, exit 0.
- python3 -m unittest tests.test_cdp_snapshot, 00:14:30 +07, 3s,
  "Ran 2 tests in 3.019s, OK".
- Neighbors: cd tests, PYTHONPATH=../scripts:. python3 -m
  unittest test_first_action test_zen_dom test_dom_act
  test_type_verification test_click2_redteam test_codemode
  test_session_continuation test_session_policy, 00:14:47 to
  00:14:57 +07, 10s, "Ran 348 tests in 9.249s, OK".
- Full discover: launched 00:15:17 +07 detached (setsid nohup),
  log ~/workspace/mochi-b2-6-discover.log, finished 00:18:37 +07
  (log mtime 17:18:37Z), "Ran 2380 tests in 210.613s, FAILED
  (failures=2, errors=8, skipped=17)". The run covered HEAD
  0400e86 plus the uncommitted fix (same bytes as d88a472 for
  the 3 files). FAIL/ERROR lines: 0 naming cdp, cdp_snapshot,
  redteam2, first_action, zen_dom, dom_act, type_verification.
  The 2 failures: test_label_format (R13) and
  test_typed_text_check_fails_when_fragment_is_absent (R12).
  The 8 errors: test_a11y_skeleton, test_bench_manifest x3
  (R14), test_cursor_file setUpClass, test_perf_evidence x2,
  test_typed_text_check_passes_when_fragment_is_visible (R12).
  The 4 baseline errors (a11y, cursor_file, perf_evidence x2)
  are identical to the C4 baseline at 36364b1.
- V-Z2: git ls-remote origin amend4-codex, 00:16:47 +07,
  06a34e8610a9467c3884f6dd7a567293c747da45.
- Spec: https://html.spec.whatwg.org/multipage/input.html,
  crawled 2026-11-22 17:13 UTC, Email state 4.10.5.1.5
  sanitization algorithm quoted in section 3.1.

Fix verification (same commands, before and after the fix):
- Failing-first: node tests/cdp_snapshot.mjs, 00:15:50 +07, 0s,
  exit 1, first failure at tests/cdp_snapshot.mjs:247, error
  'value verification failed', mutation_may_have_occurred true.
- Post-fix node: 00:16:06 +07, 2s, exit 0.
- Post-fix test_cdp_snapshot: 00:16:10 +07, 4s, "Ran 2 tests in
  3.904s, OK".
- CdpSetValueTests (new multiple test plus maxlength plus F1):
  00:16:40 +07, 1s, "Ran 3 tests in 0.492s, OK".

Committed-tree re-run (row 9, HEAD d88a472, tree clean except
this untracked log file):
- Item-12 tests, 00:22:01 +07, 0s, "Ran 4 tests in 0.009s, OK".
- RT2 set, 00:22:03 +07, 2s, "Ran 52 tests in 1.580s, OK".
- node tests/cdp_snapshot.mjs, 00:22:08 +07, exit 0 (5s for the
  node plus python batch together).
- python3 -m unittest tests.test_cdp_snapshot, 00:22:08 +07,
  "Ran 2 tests in 3.081s, OK".

Discrimination round-trip (row 10, HEAD d88a472):
- Old template restored from 0400e86: new Python test, 00:22:12
  +07, 1s, "Ran 1 test in 0.114s, FAILED (failures=1)". The new
  test is not vacuous: it fails on the old template.
- Fixed template restored (copy from /tmp, verified with git
  status clean and git diff HEAD empty): new Python test,
  00:22:16 +07, 0s, "Ran 1 test in 0.089s, OK".

Manifest verify (rows 8 and 11):
- Dirty tree (uncommitted fix): 00:17:17 +07, 2s, exit 1.
  bench_script ok, fixture ok, log names the run;
  git_status_clean FAIL (my 3 files); 3 tool artifacts FAIL
  (tools dir gone).
- Committed fix tree (only this log file untracked): 00:22:21
  +07, 2s, exit 1. bench_script ok, fixture ok, log names the
  run; git_status_clean FAIL only on '?? improvements/
  mochi-b2-6-final-log.md' (this file, pending its own commit);
  3 tool artifacts FAIL (tools dir gone, environmental). After
  this log is committed, git_status_clean is expected to pass;
  the verifier may re-run the verify on the fully clean tree.

## 6. Residuals and commit record

### Residuals (what is still open)

1. P1 live probe owed (section 4, procedure P1). The email
   multiple fix is proven in the harness only; the live browser
   behavior is the gate before the fix is quoted as live-proven.
   Owner: Muse tong (live run).
2. P2/P3 live debts (F8/F9 live-DOM runs, 2-vision benchmark as
   a whole). Venue step 11. Owner: the rung-2 live worker.
3. Independent review owed for this fix: council 3 plus redteam
   plus verifier, each committing its own review log file itself
   (Lauren Tan workflow, coordinator never codes, grader never
   the writer). This worker does NOT self-review and does not
   conclude the fix is PASS; the outputs in section 5 are facts
   for the verifier to grade. Owner: the coordinator to arrange.
4. R13 test_label_format (tests/test_overlay.py:163): owned by
   the pill-label lane (163e90c author).
5. R14 test_bench_manifest x3 plus R9 tool artifact FAILs:
   the tools dir /home/hatch/workspace/tools/ is gone. Owned by
   the environment owner.
6. R12 tesseract (2 failures): owned by the environment owner.
7. R10 F5 DOM-gate finding: owned by the P5 implementer (step 5).
8. R9: the a1a672d bench pass stays unquotable as a gate; quote
   the d7d569b re-run manifest (5f86046) instead.
9. A full discover re-run on the final committed state (d88a472
   plus this log commit) was not run end to end (210s). The
   discover in section 5 ran on identical bytes (uncommitted
   fix), and the targeted suites were re-run on the committed
   tree (row 9). The verifier may run the full discover on the
   final state to close this gap.

### Commit record (this worker's own commits, no push)

- 3532bfd: B2-6: set_value email trims each comma-separated
  token per HTML Standard 4.10.5.1.5 (scripts/cdp.mjs, 1 file,
  27 insertions, 10 deletions).
- e500923: B2-6: fake models email per-token trim, add
  multiple-email set_value cases (tests/cdp_snapshot.mjs, 1
  file, 29 insertions, 1 deletion).
- d88a472: B2-6: named test
  test_set_value_email_multiple_trims_each_token (tests/
  test_click3_redteam2.py, 1 file, 107 insertions).
- This log file: improvements/mochi-b2-6-final-log.md, commit
  b0876ca18a88b4cefda5109dd6f3f0abca2cc34e (b0876ca). The commit
  record line itself was filled in by a follow-up commit (see
  below). No push was made for any of these commits (per the
  brief: coordinator commits nothing for this worker, and no push
  from this worker).

Elapsed: task received 00:09 +07; docs read by 00:14 +07;
natives built 00:14:20 +07; pre-fix verification 00:14:41 to
00:14:57 +07; discover launched 00:15:17 +07, finished 00:18:37
+07; failing-first 00:15:50 +07; fix applied 00:16:04 to 00:16:40
+07; fix commits 00:20:20 to 00:22:00 +07 (3532bfd, e500923,
d88a472); committed-tree re-run and discrimination round-trip
00:22:01 to 00:22:21 +07.
