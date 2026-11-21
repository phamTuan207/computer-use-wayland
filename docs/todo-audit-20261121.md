# TODO AUDIT, 21/11/2026, INDEPENDENT VERIFICATION OF 111 TICKED ITEMS

Source list: docs/zen-error-fix-todolist-20261121.md, 111 ticked items,
4 unticked items excluded from this audit (2.1.7, 2.1.10, 2.2.3, 3.4.1).
Audit base: repo HEAD 1c7d252, checked 2026-11-21.
Method: for each ticked item I checked whether real evidence exists on
disk or in git history: a commit, a file, a passing test run, or a
measured log. I did not untick anything and did not edit the todolist.

## Summary

- Ticked items checked: 111.
- With evidence: 95.
- Weak evidence: 16.
- No evidence found: 0.
- Unticked items (not audited): 4.

Correction note, batch 4: the first version of this audit reported
92 E, 15 W, 4 N. Council review found evidence the auditor missed
for all 4 N items, so the verdicts were corrected below. The new
totals 95 E, 16 W, 0 N come from a full recount of the 111-row
table after the corrections, done 2026-11-21.

## Runs done by the auditor on this machine, 2026-11-21

- Phase 3 plus overlay test files, executed function by function:
  test_phase3_c1, c2, c3, brief, cleanup, polygon (35 tests) plus
  test_overlay (11 tests). Total 46, passed 46, failed 0. This matches
  the 46/46 claim in item 5.4.
- tests/test_indicator_watchdog, test_step_watchdog, test_timing,
  test_hit_rate via unittest: 23 tests, all pass.
- Hit rate recount from tests/calibration-e2-hits.jsonl: 87
  click_attempt rows, 51 hits, 51/87 = 58.6 percent. This matches the
  17/29 = 58.6 percent quoted in the list.
- tests/test_glass_shayxo_contract: 17 tests, 11 pass, 6 fail. See
  item 2.7.10. The 6 failures are caused by the blur 0.15 change.
- scripts/polygon_checks.py: CLI runs, help prints, checks B1 to B14
  are implemented except B5 and B14, which the file itself notes as
  not decidable offline.

## Items first marked no evidence, corrected after council review

The first version of this audit marked 4 items N. Council review
found evidence the auditor missed, so all 4 verdicts were corrected.
No item in this audit is N anymore.

### 2.4.5 I23, corrected to E

Tick says the fix is to follow the named person's instructions
exactly and never invent an Add to Contest method, a Share button, a
Package condition, or an account link. The auditor first found no
rule stating this. Council pointed to docs/phase23-24-25-fixes.md
lines 47-48, rule I23: "follow the tutorial exactly. No invented
step, no cut step, no reordered step. A step with no source in the
tutorial is not a step." That is the rule the tick asks for, written
in the canonical fixes file.

### 2.4.6 I24, corrected to E

Tick says the fix is to read the tooltip and verify before claiming a
warning is harmless. The auditor first found no tooltip-check rule.
Council pointed to docs/phase23-24-25-fixes.md lines 49-51, rule
I24: "read the tooltip before characterising an error.
'Enumerated incorrectly' says 'Package can not be built': a blocker,
not a warning. Guessing severity is fabrication." That is the
tooltip-check rule the tick asks for.

### 2.4.7 I25, corrected to E

Tick says the fix is to not claim to see images during a phone call,
and the count error (2 vs 11) is part of it. The auditor first found
no rule on phone-call visibility or the count. Council pointed to
docs/phase23-24-25-fixes.md lines 52-56, rule I25: "never claim to
see an image the current channel cannot show. During a voice call
there is no new image; only images already received exist, named
explicitly. Counts are re-counted from the image actually in front
of you." That is the rule the tick asks for.

### 2.7.7 G7, corrected to W

Tick says the fix is to use a laptop SSH helper script,
~/workspace/ssh-laptop.sh. The auditor first found the name nowhere
except the todolist and the file absent. Council pointed out the name
appears in 6 repo files, and improvements/live-test-log.md line 341
documents the script contract from the file itself (the full ssh
command with BatchMode, ConnectTimeout 25, StrictHostKeyChecking
accept-new, IdentitiesOnly, and ProxyCommand) together with a
recorded live measurement: all laptop checks about 4 s each, well
inside the about 30 s SSH limit. Verdict is W, not E, because the
file itself is absent from the repo and from this machine, so the
contract cannot be re-checked against the file here. The laptop path
remains UNVERIFIED for live re-testing.

## Weak evidence, 15 items

### 1.1.4 zen-mcp / zenpilot

The comparison doc (docs/zen-dom-control-comparison.md sections 1
and 2, line 28) records zen-mcp 1.2.3 at 2-20 ms and zenpilot 0.7.0
at 439-478 ms, tested by Worker B, and the final report repeats the
table. No raw Worker B log was found on disk, so the numbers rest on
the summary doc only.

### 1.3.2 real task re-test

The only source is docs/final-report-20261121.md section 5.1: 0.64 s
total, 0 misses, 0 slow steps, 15 steps, run 1 failed then run 2
passed. No raw run log for this task was found on disk. The same
applies to item 5.1, which points at the same section.

### 2.1.3, 2.1.4, 2.1.5, 2.1.6 (I2, I3, I4, I5)

Commit 1cfac75 and tests/heldout_dom_cases.mjs plus
tests/heldout-dom-protocol.md exist, so the offline fixture work is
real. But each tick admits live proof is pending, so the fix is only
proven offline, not on the live site.

### 2.2.1 H1/I9 and 2.2.2 I10 (overlay flicker)

The cited file overlay-flicker-work-log-20261121.md does not exist
anywhere in the repo. The measurement itself is recorded elsewhere:
docs/final-report-20261121.md line 82 (122 one-second windows, 0 idle
paint callbacks), docs/overlay.md, and docs/pending-user-decisions.md
line 18. The tick also admits the trigger for the 20/11 liquid-mode
incident is still unidentified, and the about 10 Hz rate was a user
estimate, never measured. So the no-repaint result is evidenced, the
cited log file and the root cause are not.

### 2.2.4 I12 (overlay watchdog respawn)

The Daemon class exists in scripts/overlay.py, and restart behavior
is covered by differently named tests in
tests/test_indicator_watchdog.py (two-confirmed-missing restart,
exited child restart), which pass. But the exact names in the tick do
not exist: no Daemon._ensure_native method and no tests named
test_daemon_respawns_dead_native or
test_daemon_keeps_live_native were found. The tick also admits live
respawn proof is still owed.

### 2.2.5 I20 (screenshot-volume claim retracted)

docs/redteam-council-20261121/worker4-overlay-flicker-redteam.md
exists and supports the retraction, but the doc itself states it
does not prove the live flicker cause and does not exclude an
unobserved capture loop. The tick overstates the finding as proven by
code and live measurement.

### 2.7.10 G10 (pill shape)

The Shayxo contract test file tests/test_glass_shayxo_contract.py
exists, and docs/pending-user-decisions.md records candidate 2 as
the temporary default. But 6 of 17 contract tests fail on this
machine, and the failures are caused by the blur change in items
2.7.11 and 4.1: the tests assert blur_strength 0.0 and pad 12.6,
while the repo now has blur_strength 0.15 and pad 12.75. The
contract was not updated when blur was raised, so the copy-exact
claim is currently contradicted by its own tests.

### 3.2.5 B5 (new package per revision)

docs/polygon-upload-runbook.md section 8 documents the procedure, but
the tick itself admits no offline check exists for it. It is a
written procedure only.

### 3.2.11 B12 (input-only test zip)

The runbook section 4 and the B12 check in scripts/polygon_checks.py
exist. But the tick's own note says the validator flags the original
3 zips as all containing .a files, so the fix is a rule plus a
checker, not verified clean zips.

### 4.3 Speed loop

The PAUSED state is documented in docs/final-report-20261121.md line
145. But the goal file named in the tick was not found anywhere in
the repo, so the "last updated 18/11 00:48" detail is unverifiable
here.

### 5.1 Test on a real task

Same single source as 1.3.2: docs/final-report-20261121.md section
5.1 only, no raw run log on disk.

## Full per-item verdicts

Verdict codes: E = evidence found, W = weak evidence, N = no evidence.
Evidence refs are short; details for W and N are in the sections above.

### Phase 1

| Item | Verdict | Evidence |
|---|---|---|
| 1.1.1 BiDi click retest | E | improvements/worker-j-post-reboot-log.md lines 13-14, numbers match tick exactly; tests/bidi_click_retest.mjs exists |
| 1.1.2 firefox-mcp live | E | worker J log lines 20-23: 3.37 s install, 2828 listening, 1594 ms, 417 ms total, click 33 ms verified |
| 1.1.3 Selenium live | E | worker J log line 27: 11/11, 0.278 s, 1863x1176, type 21 ms, click 63 ms verified |
| 1.1.4 zen-mcp / zenpilot | W | comparison doc sections 1-2 only, no raw Worker B log |
| 1.1.5 Playwright moz-firefox | E | comparison doc section 5, BROKEN with specifics |
| 1.2.1 Tool comparison | E | comparison doc section 7, session leak; commit f1797e3 |
| 1.2.2 DOM vs screenshot | E | comparison doc lines 117, 122: DOM 3-14 ms, vision 58.6 percent |
| 1.2.3 Breakthrough direction | E | commit 352b943 multi-action DOM batches; comparison doc |
| 1.2.4 Choose primary tool | E | scripts/zen_dom.py, commit f1797e3; comparison doc conclusion |
| 1.3.1 Integrate code | E | scripts/zen_dom.py exists, file lock plus finally delete, commit f1797e3 |
| 1.3.2 Re-test real task | W | final report section 5.1 only, no raw log |
| 1.3.3 Desktop files | E | worker J log lines 6-8: PID 11292, flags present, desktop verified |

### Phase 2.1

| Item | Verdict | Evidence |
|---|---|---|
| 2.1.1 G12/I6 calibration | E | commit b876ee1: docs/calibration-e2-report.md plus hits jsonl |
| 2.1.2 H3/I1 DOM rects | E | same E2 report; DOM exact, vision 58.6 percent |
| 2.1.3 I2 Discard vs Continue | W | commit 1cfac75 held-out cases exist; live proof pending per tick |
| 2.1.4 I3 Add to Contest | W | same as 2.1.3 |
| 2.1.5 I4 General info link | W | same as 2.1.3 |
| 2.1.6 I5 commit button | W | same as 2.1.3 |
| 2.1.8 I8 hit rate | E | hits jsonl recount 51/87 = 58.6 percent; E2 report 17/29 |
| 2.1.9 G13 batch observation | E | commit 352b943 |
| 2.1.11 B9/I21 hover click | E | hover_click in scripts/cdp.mjs; runbook section 4 mentions B9 |

### Phase 2.2

| Item | Verdict | Evidence |
|---|---|---|
| 2.2.1 H1/I9 flicker cause | W | cited log file missing; measurement in final report line 82 and docs/overlay.md; cause unidentified |
| 2.2.2 I10 10 Hz flicker | W | same measurement source; 10 Hz rate never measured, replaced by 0 Hz reading |
| 2.2.4 I12 watchdog respawn | W | Daemon class exists; cited method and test names do not; equivalent watchdog tests pass; live proof owed |
| 2.2.5 I20 retracted claim | W | redteam worker4 doc exists but limits its own conclusion |
| 2.2.6 overlay for any agent | E | worker J log lines 31-35: 314 files, check exit 0, 50320 bytes, blur 0.15, acquire/release verified |

### Phase 2.3

| Item | Verdict | Evidence |
|---|---|---|
| 2.3.1 H2/I13 think time | E | scripts/timing.py docstring fixes H2/I13, per-step think time, slow_think flag |
| 2.3.2 I14 3.5 min timeout | E | docs/brief-template.md line 43; scripts/step_watchdog.py STEP_TIMEOUT_S 210 |
| 2.3.3 I15 5 min progress | E | brief-template line 46; step_watchdog HEARTBEAT_S 300 |
| 2.3.4 G22 timing always on | E | scripts/timing.py ALWAYS ON; scripts/drive_log.py exists |
| 2.3.5 I16 slow worker | E | scripts/timing.py docstring fixes I16 too |

### Phase 2.4

| Item | Verdict | Evidence |
|---|---|---|
| 2.4.1 A7/I17 invented rule | E | brief-template section 6: say "I don't know" instead of inventing |
| 2.4.2 I18 wrong attribution | E | brief-template section 6: every claim needs source plus access date |
| 2.4.3 I19 invented dialogs | E | brief-template section 6: verify before asserting |
| 2.4.4 I22 relayed diagnosis | E | brief-template section 6: never relay a subagent diagnosis as fact |
| 2.4.5 I23 invented method | E | phase23-24-25-fixes.md lines 47-48, rule I23: follow the tutorial exactly, no invented step |
| 2.4.6 I24 warning guess | E | phase23-24-25-fixes.md lines 49-51, rule I24: read the tooltip before characterising an error |
| 2.4.7 I25 phone call claim | E | phase23-24-25-fixes.md lines 52-56, rule I25: never claim to see an image the channel cannot show, recount from the image in front of you |
| 2.4.8 I26 Playwright tip | E | brief-template section 6: research first, Google first when stuck |
| 2.4.9 A8 unverified claims | E | brief-template section 6 line 1: source plus access date |

### Phase 2.5

| Item | Verdict | Evidence |
|---|---|---|
| 2.5.1 A4 no follow-up | E | scripts/task_chain.py TaskChainMonitor polls and notifies; docs/phase23-24-25-fixes.md line 66 |
| 2.5.2 A5/I27 70 min stuck | E | step_watchdog WORKER_STALL_S 900, STEP_TIMEOUT_S 210 |
| 2.5.3 A6 kill stuck agent | E | brief-template line 45; docs/worker-brief-checklist.md line 68 |
| 2.5.4 G16 watchdog direct | E | step_watchdog.py lines 13-25: DirectReporter reports to Muse, bypasses coordinator |
| 2.5.5 G17 late report | E | step_watchdog WATCH_INTERVAL_S 300; docstring cites G17 |
| 2.5.6 G15 detached launch | E | brief-template lines 49-50: setsid nohup disown |
| 2.5.7 G18 Track 2 pause | E | docs/track2-gate.json; phase23-24-25-fixes.md lines 90, 111 |
| 2.5.8 I28-I30 | E | phase23-24-25-fixes.md lines 94-99 with code refs |

### Phase 2.6

| Item | Verdict | Evidence |
|---|---|---|
| 2.6.1 A1 skipped steps | E | brief-template section 2, research first |
| 2.6.2 A2 lost method | E | brief-template section 3, saved working method |
| 2.6.3 A3 missing lessons | E | brief-template section 4, all lessons |
| 2.6.4 A9 silent solution | E | worker-brief-checklist lines 40-41: tell user BEFORE writing |
| 2.6.5 I31 no driving log | E | scripts/drive_log.py, step_watchdog.py, overlay.py exist; brief-template line 61 |
| 2.6.6 I32-I40 bad instructions | E | worker-brief-checklist section 5 covers I32-I40 |

### Phase 2.7

| Item | Verdict | Evidence |
|---|---|---|
| 2.7.1 G1 stale relay code | E | scripts/sync-installed.py _relay_restart_needed and _restart_relay, stale-code refusal |
| 2.7.2 G2 geometry 901x1176 | E | scripts/tc02_controller.py lines 107-108, 164 enforce 901x1176 |
| 2.7.3 G3 lease in /tmp | E | scripts/tc02_controller.py lines 559-563: lease root under home cache, mode 0700; commit 871f2e1 |
| 2.7.4 G4 Lua dispatch | E | worker-brief-checklist line 108 hl.dsp object form; improvements/live-test-log.md line 760 |
| 2.7.5 G5 image viewer | E | scripts/image_viewer.py kills with pkill -x imv-wayland |
| 2.7.6 G6 SSH dies 30 s | E | worker-brief-checklist line 93: long jobs run detached |
| 2.7.7 G7 SSH helper script | W | name in 6 repo files; live-test-log.md:341 documents the contract and a live measurement (about 4 s per check); file itself absent from repo and this machine |
| 2.7.8 G8 agy non-interactive | E | worker-brief-checklist line 98: use fcc-claude |
| 2.7.9 G9 live-site proxy | E | scripts/vm_proxy.py docstring, local forward proxy plus ignore-certificate-errors |
| 2.7.10 G10 pill shape | W | contract test file exists but 6 of 17 fail on blur 0.15; see weak section |
| 2.7.11 G11 pill blur | E | native/hyprglass-local-optics.lua line 14: blur_strength 0.15 |
| 2.7.12 G19 workers not found | E | brief-template section 6: re-check yourself, Google first |
| 2.7.13 G20 Google sign-in | E | docs/cookie-session-summary.md lines 11, 28, 35; checklist line 102 |
| 2.7.14 G21 Browse hover | E | same as 2.1.11 |
| 2.7.15 G23 model routing | E | brief-template line 110 never route to gpt-reserve; scripts/brief_check.py line 24 |
| 2.7.16 G24 JSONL newline | E | scripts/hit_rate.py lines 49-50, det_finish.py line 247, cursor_theme.py line 146 |
| 2.7.17 G27 group reply | E | worker-brief-checklist line 104: reply in group immediately |

### Phase 2.8

| Item | Verdict | Evidence |
|---|---|---|
| 2.8.1 observation expiry | E | scripts/cu.py line 48 OBSERVATION_MAX_AGE 120, line 746 refusal; commit ceff51c |
| 2.8.2 driver session rot | E | commit e3d75c4; scripts/session_driver.py lines 84, 118 (I43 PNG path) |

### Phase 3.1

| Item | Verdict | Evidence |
|---|---|---|
| 3.1.1 C1 120 s expiry | E | commit ceff51c; tests/test_phase3_c1.py, 4 tests in 46/46 run |
| 3.1.2 C2 settle recapture | E | commit 6be6784; tests/test_phase3_c2.py, 5 tests |
| 3.1.3 C3 Ctrl+T refusal | E | commit 92944da; tests/test_phase3_c3.py, 6 tests |
| 3.1.4 C4 Commit link | E | docs/polygon-upload-runbook.md section 6 |
| 3.1.5 C5 404 navigation | E | runbook section "Navigation that fails" |
| 3.1.6 C6 ydotool ban | E | commit aa114b2; docs/brief-template.md line 108; tests/test_phase3_brief.py |
| 3.1.7 C7 narrate | E | brief-template section 5; scripts/timing.py, drive_log.py, step_watchdog.py, overlay.py |
| 3.1.8 C8 cleanup | E | commit 8636f21; scripts/session_cleanup.py --check and --clean; tests/test_phase3_cleanup.py |

### Phase 3.2

| Item | Verdict | Evidence |
|---|---|---|
| 3.2.1 B1 .cpp solution | E | commit 2f0510d; runbook section 5; polygon_checks B1 |
| 3.2.2 B2 short name | E | runbook section 11; polygon_checks B2 |
| 3.2.3 B3 duplicate tests | E | runbook section 7; polygon_checks B3; validator found duplicate [21,28] |
| 3.2.4 B4 renumber | E | runbook section 7; polygon_checks B4 |
| 3.2.5 B5 new package | W | runbook section 8 only; tick admits no offline check exists |
| 3.2.6 B6 hash link | E | runbook section 11; polygon_checks B6 |
| 3.2.7 B7 English statement | E | runbook section 2; polygon_checks B7 |
| 3.2.8 B8 dollar signs | E | runbook section 2; polygon_checks B8 |
| 3.2.9 B10 Zen only | E | runbook section 0; brief-template section 7 |
| 3.2.10 B11 no keyed URL | E | runbook section 0; brief-template section 7 |
| 3.2.11 B12 input-only zip | W | runbook section 4 and B12 check exist; tick notes original 3 zips still contain .a files |
| 3.2.12 B13 test count | E | runbook section 4; polygon_checks B13, expected count 30 |
| 3.2.13 B14 verification rule | E | runbook section "Verification failed is NOT a stop rule"; scripts/claim_check.py tripwire |

### Phase 3.3

| Item | Verdict | Evidence |
|---|---|---|
| 3.3.1 D1 thread channels | E | commit aa114b2; brief-template section 8 |
| 3.3.2 D2 Messenger connector | E | brief-template section 8; scripts/brief_check.py |
| 3.3.3 D3 push at once | E | brief-template section 8; brief_check.py |
| 3.3.4 D4 lessons both places | E | brief-template section 8; brief_check.py |
| 3.3.5 D5 full-day calendar | E | brief-template section 8; brief_check.py |

### Phase 3.4

| Item | Verdict | Evidence |
|---|---|---|
| 3.4.2 E2 Firefox automation | E | comparison doc and final report; same evidence as Phase 1 |
| 3.4.3 E3 10x speed | E | final-report line 145: PAUSED documented with baseline numbers |

### Phase 4

| Item | Verdict | Evidence |
|---|---|---|
| 4.1 pill blur up | E | native/hyprglass-local-optics.lua line 14 blur 0.15; note: this change breaks 6 Shayxo contract tests, see 2.7.10 |
| 4.2 cookie research | E | docs/cookie-session-summary.md: named profile per account, connector as main path, heartbeat every 3-4 days |
| 4.3 speed loop | W | PAUSED documented in final report line 145; named goal file not found in repo |
| 4.4 Track 2 paused | E | phase23-24-25-fixes.md lines 90, 111; docs/track2-gate.json |
| 4.5 pill candidate 2 | E | docs/pending-user-decisions.md line 25: candidate 2 temporary default, candidate 1 kept |
| 4.6 user decisions list | E | docs/pending-user-decisions.md sections: H1-BASE, Step 3, save-dialog Part B, backups, Omarchy restore, Calibration Grid tabs |

### Phase 5

| Item | Verdict | Evidence |
|---|---|---|
| 5.1 real task test | W | final-report section 5.1 only, no raw log; same source as 1.3.2 |
| 5.2 before/after table | E | final-report section 5.2 table with measured numbers; honest note that no equal-task ratio is claimed |
| 5.3 final report | E | docs/final-report-20261121.md exists as FINAL |
| 5.4 merge todolist-push | E | merge commit 96438bb exists; 46/46 re-run by auditor, 46 passed, 0 failed |

## Notes on evidence classes

- About 30 ticked items are process or behavior rules (sections 2.3
  to 2.6 and parts of 2.7). For those, the repo evidence is the rule
  written into the canonical brief template plus machine checks in
  scripts/brief_check.py and enforcement code such as
  scripts/step_watchdog.py, scripts/task_chain.py, and
  scripts/timing.py. That is real evidence that the rule exists and is
  enforced in new briefs, not a measurement that past behavior changed.
- Live Zen timings in items 1.1.1 to 1.1.3, 1.3.3, and 2.2.6 rest on
  improvements/worker-j-post-reboot-log.md, a log file on disk. The
  numbers in the log match the numbers in the todolist exactly. They
  were not re-measured by this auditor, because this machine has no
  Zen or Firefox binary.

## UNVERIFIED

- Item 2.7.7: the laptop SSH helper script file itself is absent
  from the repo and from this machine, so the contract documented
  in live-test-log.md:341 cannot be re-checked against the file
  here, and live re-testing on the laptop path remains UNVERIFIED.
- Items 2.1.3 to 2.1.6: live proof on the real site is still pending,
  as the ticks themselves state.
- Items 1.1.4, 1.3.2, and 5.1: single-source numbers with no raw log
  on disk.
- The 20/11 liquid-mode flicker trigger (items 2.2.1, 2.2.2) remains
  unidentified.
- The 6 failing Shayxo contract tests (item 2.7.10) were found by
  this audit but not fixed here; fixing them is out of scope for an
  audit. The fix is either to update the contract to the 0.15 blur
  profile or to revert blur to 0.0, a decision for the coordinator.
