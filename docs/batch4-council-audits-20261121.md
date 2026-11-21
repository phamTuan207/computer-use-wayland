# BATCH 4 COUNCIL, MEMBER 2, INDEPENDENT VERIFICATION OF BATCH 2 AND 3 AUDITS

Date: 2026-11-21. Repo base: local HEAD beffa19, origin/main beffa19.
Role: council member 2, batch 4. I did NOT trust the batch 2 and 3
report (coord/clone1.md) or any agent's claimed numbers. Every number
below comes from a check I ran in this session. I did not edit the
todolist, did not untick anything, did not modify any file under
review. No personal info in this file. 0 em dash, 0 en dash.

## Summary

- Todo audit re-check: I sampled 38 of the 111 ticked items, spread
  across every section (Phase 1, 2.1 to 2.8, 3.1 to 3.4, 4, 5).
  The sample includes all 4 items the audit called no-evidence and
  13 of the 15 items it called weak-evidence.
- Agree with the audit on 34 of 38 sampled items. DISAGREE on 4:
  2.4.5, 2.4.6, 2.4.7, 2.7.7. All 4 are items the audit called
  no-evidence. Three of them (2.4.5, 2.4.6, 2.4.7) have direct
  evidence in docs/phase23-24-25-fixes.md, a file the audit
  apparently never searched for those items. The fourth (2.7.7)
  has weaker evidence than the audit claimed was absent, but the
  file itself is still unverifiable from this machine.
- Revised verdicts for the 4 disputed items: 2.4.5 E, 2.4.6 E,
  2.4.7 E, 2.7.7 W. If the same corrections applied to the full
  audit, its counts would move from 92 E, 15 W, 4 N to 95 E, 16 W,
  0 N. I did NOT re-check the other 73 items, so that is an
  extrapolation from my sample, not a recount of all 111.
- Todolist counts verified by me: 111 ticked lines, 4 unticked
  lines in docs/zen-error-fix-todolist-20261121.md, matching the
  audit. I spot-checked 2.1.10 is unticked.
- Shayxo contract, run by me: 17 tests, 11 pass, 6 fail. Matches
  the audit exactly.
- Phase 3 plus overlay suites, re-run by me with my own harness
  (the test files use plain functions, not unittest TestCase, so
  plain unittest finds 0 tests): 46 passed, 0 failed. Matches the
  audit's 46/46 claim and item 5.4.
- Watchdog, timing, hit-rate suites, re-run by me: 23 tests, all
  pass. Matches the audit.
- Hit-rate recount by me from tests/calibration-e2-hits.jsonl:
  87 rows, 51 hits, 51/87 = 58.6 percent. Matches the audit and
  the 17/29 quoted in the todolist.
- All 13 commits cited by the audit exist (1cfac75, b876ee1,
  352b943, ceff51c, 6be6784, 92944da, 2f0510d, aa114b2, 8636f21,
  96438bb, f1797e3, 871f2e1, e3d75c4). Checked with git cat-file.
- PR #1: head is now c936fcd, trial merge into current main
  CONFLICTS in coord/clone2.md only. Issues 1 and 2 from the
  batch 2 review are STILL PRESENT at c936fcd, no fix commit.
  GitHub: OPEN, mergeable UNKNOWN, 0 reviews.
- Code Mode: all batch 2 numbers hold exactly. Unittest 40 tests
  pass. CLI numbers reproduce to the decimal. Token estimates
  recomputed from disk, with the definition made explicit below.
- Minor audit error, not a verdict error: the audit's weak-evidence
  section labels the input-only zip item "3.2.12 B12". The
  todolist has B12 at 3.2.11 and B13 at 3.2.12. The audit's own
  table lists it correctly as 3.2.11 B12, only the section heading
  is wrong.

## Per-item table, 38 sampled todo items

Verdict codes: E = evidence found, W = weak evidence, N = no
evidence. "Audit" is the batch 3 audit verdict, "Mine" is my
independent verdict.

| Item | Audit | Mine | Agree | Evidence I checked myself |
|---|---|---|---|---|
| 1.1.1 BiDi click retest | E | E | yes | worker J log lines 13-14: v1 page.click FAIL counter 0, v2 evaluate counter 1; tests/bidi_click_retest.mjs exists |
| 1.1.2 firefox-mcp live | E | E | yes | worker J log lines 20-23: install 3.37 s, port 2828 listening, list_pages 1594 ms, click 33 ms, total 417 ms |
| 1.1.3 Selenium live | E | E | yes | worker J log line 27: 11/11, 0.278 s, 1863x1176, type 21 ms, click 63 ms |
| 1.1.4 zen-mcp / zenpilot | W | W | yes | comparison doc sections 1-2 only; no Worker B raw log in improvements/ (logs present are A2, C, D, E, F, G, H, I, J, K, N) |
| 1.1.5 Playwright moz-firefox | E | E | yes | comparison doc table line 15 and section 5: BROKEN |
| 1.2.1 Tool comparison | E | E | yes | commit f1797e3 exists; comparison doc section 7, session leak |
| 1.2.2 DOM vs screenshot | E | E | yes | comparison doc lines 117, 122: DOM 3-14 ms, vision 17/29 = 58.6 percent |
| 1.2.3 Breakthrough direction | E | E | yes | commit 352b943 exists, message "test: cover multi-action DOM batches" |
| 1.3.1 Integrate code | E | E | yes | scripts/zen_dom.py exists; fcntl.flock lock and finally delete |
| 1.3.2 Re-test real task | W | W | yes | final report section 5.1 only (0.64 s, 15 steps, run 1 failed, run 2 passed); no raw run log found |
| 2.1.1 G12/I6 calibration | E | E | yes | commit b876ee1 exists; docs/calibration-e2-report.md and hits jsonl exist |
| 2.1.3 I2 Discard vs Continue | W | W | yes | commit 1cfac75 exists; heldout files exist; tick line 31 says live proof pending |
| 2.1.5 I4 General info link | W | W | yes | same commit and files; tick line 33 says live proof pending |
| 2.1.8 I8 hit rate | E | E | yes | recount by me: 51/87 = 58.6 percent from hits jsonl |
| 2.2.1 H1/I9 flicker cause | W | W | yes | cited log file overlay-flicker-work-log-20261121.md missing (checked, absent); measurement in final report line 82 (122 windows, 0 idle paints); trigger unidentified per tick |
| 2.2.2 I10 10 Hz flicker | W | W | yes | same measurement source; 10 Hz never measured, tick admits |
| 2.2.4 I12 watchdog respawn | W | W | yes | Daemon class exists (overlay.py line 205); _ensure_native and the two named tests absent (grep empty); equivalent tests test_two_confirmed_missing_layer_probes_restart_indicator and test_exited_child_is_restarted exist and pass in my 23-test run; live proof owed per tick |
| 2.2.5 I20 retracted claim | W | W | yes | redteam worker4 doc exists; lines 12 and 56 state it does not prove the live cause |
| 2.2.6 overlay for any agent | E | E | yes | worker J log lines 31-35: 314 files, check exit 0, 50320 bytes, blur 0.15 |
| 2.3.2 I14 3.5 min timeout | E | E | yes | brief-template line 43 (3.5 min); step_watchdog STEP_TIMEOUT_S 210 |
| 2.4.1 A7/I17 invented rule | E | E | yes | brief-template section 6 line 65: say "I don't know" |
| 2.4.5 I23 invented method | N | E | NO | phase23-24-25-fixes.md lines 47-49 state the rule: "follow the tutorial exactly. No invented step, no cut step, no reordered step." See dispute section |
| 2.4.6 I24 warning guess | N | E | NO | same doc lines 50-52: "read the tooltip before characterising an error", with the exact "Enumerated incorrectly" example from the tick. See dispute section |
| 2.4.7 I25 phone call claim | N | E | NO | same doc lines 53-56: "never claim to see an image the current channel cannot show. During a voice call there is no new image", counts re-counted from the image in front of you. See dispute section |
| 2.5.4 G16 watchdog direct | E | E | yes | DirectReporter class at step_watchdog.py line 50; docstring lines 13-25: reports directly, bypasses coordinator |
| 2.7.7 G7 SSH helper script | N | W | NO | script name appears in 4+ repo files, not only the todolist; contract documented from the file in live-test-log.md line 341; file itself absent from this machine (full-disk find, zero copies). See dispute section |
| 2.7.10 G10 pill shape | W | W | yes | 17 tests, 6 fail, run by me; test asserts blur 0.0 (lines 193, 204, 257) and pad 12.6 (line 267); lua has blur 0.15, depth 9 dp gives pad 12.75 |
| 2.7.11 G11 pill blur | E | E | yes | native/hyprglass-local-optics.lua line 14: blur_strength 0.15 |
| 2.8.1 observation expiry | E | E | yes | commit ceff51c exists; cu.py line 48 OBSERVATION_MAX_AGE 120, refusal near line 746 |
| 3.1.1 C1 120 s expiry | E | E | yes | commit ceff51c exists; 4 c1 tests pass in my 46-test run |
| 3.1.6 C6 ydotool ban | E | E | yes | commit aa114b2 exists; brief-template line 108 ydotool ban; brief tests pass in my 46-test run |
| 3.2.1 B1 .cpp solution | E | E | yes | commit 2f0510d exists; runbook section 5; check_solution_file implements B1 |
| 3.2.5 B5 new package | W | W | yes | runbook section 8 only; tick admits no offline check exists |
| 3.2.11 B12 input-only zip | W | W | yes | runbook section 4 and check_test_zip implement B12; tick notes original 3 zips still contain .a files |
| 4.1 pill blur up | E | E | yes | lua line 14 blur 0.15; note: this change breaks 6 Shayxo contract tests, see 2.7.10 |
| 4.3 Speed loop | W | W | yes | PAUSED in final report line 145; goal name test-case-nhanh-g-p-5-10-l-n appears only in the todolist |
| 5.1 real task test | W | W | yes | same single source as 1.3.2, final report section 5.1 only |
| 5.4 merge todolist-push | E | E | yes | merge commit 96438bb exists; my own 46-test harness run: 46 passed, 0 failed |

## Disputed items, detail

### 2.4.5, 2.4.6, 2.4.7: the audit missed docs/phase23-24-25-fixes.md

The audit's no-evidence section says no rule, checklist line, code,
or test in the repo states these fixes. That is wrong. The file
docs/phase23-24-25-fixes.md has one numbered entry per todolist item
in section 2.4, and the three entries state the fixes directly:

- 2.4.5 (lines 47-49): "follow the tutorial exactly. No invented
  step, no cut step, no reordered step. A step with no source in the
  tutorial is not a step." The tick says follow the named person
  exactly, no cutting, no inventing. The doc phrases the source as
  "the tutorial" where the tick says the person's name; the doc's
  line 40 links the two ("Muse wrote is never attributed to Hieu or
  to a tutorial"). This is the same fix, written as a rule.
- 2.4.6 (lines 50-52): "read the tooltip before characterising an
  error. 'Enumerated incorrectly' says 'Package can not be built':
  a blocker, not a warning. Guessing severity is fabrication."
  This is word for word the tick's fix, including its example.
- 2.4.7 (lines 53-56): "never claim to see an image the current
  channel cannot show. During a voice call there is no new image;
  only images already received exist, named explicitly. Counts are
  re-counted from the image actually in front of you." This is the
  tick's fix, including the phone-call case and the count correction.

The audit cited the same file for other items (2.5.1, 2.5.7, 2.5.8,
2.6.x, 4.4), so the file was known to the auditor; the 2.4.x entries
were apparently never checked. My verdict for all three is E. One
caveat for 2.4.5 only: the doc says "tutorial" while the tick says
the person's name, so a strict reader could call that W instead of
E. I call it E because the doc's numbered entries map 1:1 to the
todolist items and line 40 ties the name to the tutorial.

### 2.7.7: the audit's premise is false, but the file is still unverified here

The audit says the script name appears nowhere in the repo except
in the todolist itself. I found it in at least 4 other files:

- docs/redteam-council-20261121/worker3-coordinate-redteam.md line 6:
  live measurement via ssh-laptop.sh at 03:36, 21/11/2026.
- improvements/speed-checks-cache-structured.md line 4: laptop reads
  via ~/workspace/ssh-laptop.sh.
- improvements/speed-swarm-rerun-plan.md line 102: SSH only via
  ~/workspace/ssh-laptop.sh.
- improvements/live-test-log.md line 341: "ssh-laptop.sh contract
  verified from the file", quoting the full ssh command with
  BatchMode, ConnectTimeout 25, IdentitiesOnly, ProxyCommand, and
  the key path.

So the script's existence on the laptop side and its exact contract
are documented in the repo, and it was used for a recorded live
measurement. What the audit got right: the file itself is absent
from this machine. I checked ~/workspace/ssh-laptop.sh (not there)
and ran a full-disk find (zero copies anywhere on this machine).
The file is a laptop-side path and was never in the repo. My verdict
is W, not N: references plus contract plus recorded live use exist,
but the file itself cannot be verified from this machine.
UNVERIFIED: whether the file still exists on the laptop today.

## Shayxo contract test, run by me

- Command: python3 -m unittest tests.test_glass_shayxo_contract
- Result: Ran 17 tests, FAILED (failures=6). 11 pass, 6 fail.
  Matches the audit exactly.
- Cause confirmed by reading the code: the test asserts
  blur_strength 0.0 (lines 193, 204, 257) and pad 12.6 (line 267,
  computed as depth 9 dp times 1.4 plus blur). The repo now has
  blur_strength 0.15 (lua line 14), which makes the real pad 12.75.
  The contract was not updated when blur was raised in item 4.1.
  This is the same finding as item 2.7.10. Fixing it is out of
  scope for this council check; the user has since directed that
  the contract be updated to the new values (batch 5 task 1).

## PR #1 re-review

- Branch: origin/coord-clone2-setup, current head c936fcd
  ("clone2: batch 3 status report, zero progress stated openly,
  work starting now"). This is past the batch 2 review head
  6ce5a75. New commits since then: 4bb010d (merge main into
  branch), c043ad1 (task 4, 10 realistic tests), 7f254c1 (task 5,
  Selenium live package), 32b09fb (task 6, speed comparison),
  e3f2d06 (batch 2 completion report), c936fcd (batch 3 status).
- Trial merge, done by me in a scratch worktree (removed after):
  merging origin/main (beffa19) into c936fcd CONFLICTS in exactly
  one file, coord/clone2.md. All other files merge cleanly. This
  is a change from the batch 2 review, which found a clean merge
  at 6ce5a75: main has since advanced (including Muse's beffa19
  commit touching coord/clone2.md) while the branch also rewrote
  coord/clone2.md. The conflict is in a coord status file only,
  trivially resolvable, but the PR is no longer clean-mergeable.
- GitHub state, checked via gh only: PR #1 OPEN, mergeable
  UNKNOWN, mergeStateStatus UNKNOWN, 0 reviews, updated
  2026-11-21T11:24:13Z. Title is now "clone2: DOM control
  research, AT-SPI, realistic tests, Selenium Zen package, speed
  benchmark". I did not merge, did not push to the PR branch, did
  not modify the PR.
- Issue 1 from the batch 2 review, STILL PRESENT at c936fcd:
  I read tests/atspi_prototype.py main(). Live success sets
  summary["ok"] = True, and the selftest failure branch only sets
  summary["selftest"], never resetting summary["ok"]. The final
  return is 0 if summary["ok"] else 1. So in auto mode, live pass
  plus selftest fail still exits 0, contradicting the docstring.
  No fix commit on the branch.
- Issue 2 from the batch 2 review, STILL PRESENT at c936fcd:
  press_button() (lines 115-125) still returns {"ok": bool(ok)}
  without raising when do_action() returns False. A failed press
  is still recorded as a passed step. No fix commit on the branch.
- The branch has grown past the batch 2 review scope: it now also
  contains tests/realistic_clone2/ (10 tests), a Selenium live
  procedure doc, and a speed comparison doc. I did not re-review
  those new files in depth; they are out of the scope I was given.
  The HOLD recommendation from the batch 2 review still stands,
  and now has one more reason: the merge conflict in
  coord/clone2.md must be resolved first.
- UNVERIFIED: all live Selenium and Firefox numbers on the branch,
  same as the batch 2 review. No browser or driver was used here
  for the PR check.

## Code Mode verification

- Unittest, run by me: python3 -m unittest
  tests.test_codemode_search tests.test_codemode, Ran 40 tests,
  OK (0.119 s). Matches the batch 2 claim of 40 tests (19 new
  plus 21 existing), all pass.
- CLI search, run by me: python3 scripts/codemode_search.py
  search "dom locate" returns total 2, zen_dom first with
  description "Single-session Zen DOM control manager." Matches.
- CLI describe, run by me: describe zen_dom returns short info
  with entry points (ZenDomError, ZenSession, main, and others),
  683 chars total, under the 2000 char cap. Matches.
- CLI tokens, run by me (note: the subcommand needs a query
  argument; bare "tokens" errors with usage, which is correct
  behavior, not a bug):
  - "dom locate": before 1823.0, after 90.2, saved 1732.8.
  - "session": before 1823.0, after 251.0, saved 1572.0.
  - "polygon": before 1823.0, after 59.5, saved 1763.5.
  All three match the batch 2 numbers exactly.
- Token estimates recomputed from disk by me: the code's
  catalog_before_text() builds the before-text as each file name,
  a newline, then the first 3 lines of that script, joined with
  newlines, over 60 ops. That text is 7292 chars, 7292 / 4 =
  1823.0 tokens estimate. My first naive recompute (first 3 lines
  only, no file names) gave 6333 chars / 1583.25, which differs by
  959 chars, exactly the 60 file names plus separators. The
  batch 2 number 1823.0 is correct under the code's own
  definition (file name plus first 3 lines per script). The
  definition should have been stated in the batch 2 report; the
  number itself holds.
- Snippets registry, checked by me: snippets/registry.json has 4
  entries. Each program matches its .py file on disk byte for
  byte (p1-terminal-df, p2-terminal-calc, p3-terminal-mkdir,
  p4-terminal-write-file). Descriptions are 104 to 182 chars,
  under the 200 cap. Each entry has input and sample output. All
  4 programs pass scripts/code_exec.py validate_program.
- Search descriptions are at most 62 chars in my run, under the
  200 cap.
- UNVERIFIED: no snippet was executed end to end here, same as
  batch 2. Sample outputs are shell commands run directly, not
  full program runs through code_exec.py.

## Runs done by me in this session, 2026-11-21

- python3 -m unittest tests.test_glass_shayxo_contract: 17 tests,
  11 pass, 6 fail.
- python3 -m unittest tests.test_codemode_search
  tests.test_codemode: 40 tests, OK.
- python3 -m unittest tests.test_indicator_watchdog
  tests.test_step_watchdog tests.test_timing tests.test_hit_rate:
  23 tests, OK.
- Own harness running every test_ function in
  test_phase3_c1, c2, c3, brief, cleanup, polygon, and
  test_overlay: 46 passed, 0 failed. (Plain unittest finds 0
  tests in these files because they define plain functions, not
  TestCase classes. The audit's 46/46 was reproduced with the
  function-by-function harness.)
- Hit-rate recount from tests/calibration-e2-hits.jsonl: 51/87 =
  58.6 percent.
- CLI: search "dom locate", describe zen_dom, tokens for three
  queries, all as reported above.
- git cat-file -t for all 13 cited commits: all exist.
- Trial merge of origin/coord-clone2-setup (c936fcd) into
  origin/main (beffa19) in a scratch worktree: conflict in
  coord/clone2.md only, worktree removed after.
- gh pr view 1: OPEN, mergeable UNKNOWN, 0 reviews.

## UNVERIFIED

- The other 73 ticked items I did not sample. My 38-item sample
  cannot certify the full 111.
- Live Zen timings in items 1.1.1 to 1.1.3, 1.3.3, and 2.2.6 rest
  on improvements/worker-j-post-reboot-log.md, a log file on disk.
  I verified the numbers in the log match the todolist exactly,
  but I did not re-measure them. This machine has no Zen.
- Item 2.7.7: whether the laptop script still exists today.
- The 20/11 liquid-mode flicker trigger (items 2.2.1, 2.2.2)
  remains unidentified, as the ticks themselves state.
- Live proof for items 2.1.3 to 2.1.6 on the real site is still
  pending, as the ticks themselves state.
- All live numbers on PR #1 (Selenium, Firefox, AT-SPI) and all
  Zen-specific claims.
- No snippet was executed end to end (Code Mode).
