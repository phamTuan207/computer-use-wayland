# R3-L3 Phase 0 prepare: documentation and consistency gates

- Date: 2026-11-25, about 09:05 +07 (Asia/Ho_Chi_Minh)
- Worker: Phase 0 prepare worker (docs gates only). Did not start the run. Did not run any run task.
- Sources read in full or grepped: `~/workspace/r3-l3-replan-final-20261124.md` (re-plan, FINAL),
  `~/workspace/r3-l3-execution-plan-20261124.md` (execution plan, 576 lines),
  `~/workspace/r3l3-run-wt/rung3-run-log/r3-l3-coordinator-state.json` (state file, last_updated 2026-11-24T20:02:00+07:00),
  `~/workspace/r3l3-run-wt/rung3-run-log/thu-tu-chay.txt` (run order, canonical),
  `~/workspace/r3l3-run-wt/rung3-run-log/r3-l3-exception-list.txt` (Class L/S, canonical),
  `~/workspace/r3l3-run-wt/rung3-run-log/du-phong.txt` (backups, canonical),
  `~/workspace/r3l3-run-wt/rung3-ci/ledger-schema.json` and `rung3-ci/validate-ledger.py`,
  `~/workspace/r3l3-run-wt/rung3-run-log/r3-l3-phase0-checklist-status.md`,
  `~/workspace/r3-l3-deputy-declaration.md` (17:24:46 +07, 24/11),
  `~/workspace/r3l3-run-wt/rung3-run-log/r3-l3-zen-1.24.3b-optimizations-20261124.md`,
  `~/workspace/r3l3-run-wt/rung3-run-log/zen-opencode-council-decision-20261124.md` (P1-H),
  `~/workspace/r3l3-run-wt/improvements/r3-l3-clone1-meeting-input-20261124.md` (clone1 risk 1.7),
  `~/workspace/r3l3-run-wt/rung3-run-log/r3-l3-ledger-push.md`, `r3-l3-timeout-watch.md`,
  `~/workspace/r3l3-run-wt/rung3-ci/audit-scan.py`.
- Live checks done by this worker via SSH to the laptop (short commands only, no windows touched,
  nothing closed or navigated): 2026-11-25 09:01-09:03 +07.

## Per-gate verdicts

| Gate | Verdict |
|---|---|
| G-32 mechanical consistency pass | FAIL (10 mismatches listed below) |
| Updates-off check procedure | DEFINED in writing below; live re-verified PASS 09:01-09:03 +07 |
| G-24 deputy re-confirmation | NOT DONE (declaration stale, no newer confirmation) |
| G-38 deputy dry-run | NOT DONE / BLOCKED (no record; no channel to the deputy session from this worker) |
| G-27 run-tab protection | PARTIAL (RSS headroom recorded live; pinned tab and about:unloads baseline NOT verified) |
| G-40 correlated-outage wait | DONE (60 minutes, recorded) |
| G-41 per-task report file | DONE (file created by this worker, zero rows) |
| G-48 state file atomic write | NOT VERIFIED (no procedure existed; procedure defined below, adoption still needed) |
| G-49 ledger cross-check | PARTIAL (schema validation works; no ledger-vs-verdict diff script exists) |
| P1-H definition | DONE (definition recorded) |

Task 1 must not start until G-32, G-24, G-38, G-27, G-48, G-49 are green or recorded as
accepted limitations with an owner decision. G-40, G-41, P1-H and the updates-off procedure are done.

## G-32: mechanical consistency pass - FAIL, 10 mismatches

Canonical source per the re-plan: the state file plus thu-tu-chay.txt. The execution plan is
declared superseded on ids, but no superseded stamp exists in the execution plan file itself (M8).

Verified consistent (no mismatch):
- Run order: 55 tasks, 55 unique ids. Positions: R3-001=1, R3-029=25, R3-037=28, R3-040=29,
  R3-047=34, R3-055=36, R3-074=39, R3-075=40, R3-078=42, R3-079=43, R3-088=48, R3-089=49,
  R3-093=50, R3-096=52, R3-100=55. Lane split FCC 1-28, Codex 29-55.
- Counts: 55 tasks, 35 browser, 20 desktop; 37 medium, 11 hard, 7 very hard (execution plan line 20,
  thu-tu-chay.txt line 6). Pass bar 53/55 everywhere. Invalid cap max 5 total, max 2 per group.
- Freeze hashes: H1 9b9d900, H2 5fac0eb, key JSON sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8,
  keys md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60,
  list sha256 c1d9a220fa9a5fe57f509cd386c2b28ad466aaecdfb053ad35b5723c697d29ec (state freeze block,
  thu-tu-chay.txt, execution plan line 19).
- Class L 9 plus Class S 46 equals 55, zero overlap, zero gaps (exception list, checked programmatically).
  Class L: R3-001, R3-055, R3-074, R3-075, R3-089, R3-096, R3-078, R3-079, R3-088 (state file, exception list,
  thu-tu-chay.txt agree).
- Backups: medium DP-03, DP-06, DP-07 in that order; hard DP-02 only (Class L); very hard DP-05 only;
  DP-01 RETIRED (state file, du-phong.txt, thu-tu-chay.txt, exception list agree).
  Ledger schema task pattern DP-0[123567] admits exactly the live backups DP-02/03/05/06/07 and
  correctly excludes DP-01. DP-04 does not exist and is excluded by the pattern.
- Rejected tiebreaker B 9d613f19 is marked NOT APPROVED (3/4) everywhere it appears (state file,
  thu-tu-chay.txt, re-plan). R3-L2 tiebreaker 3f3aca86 is marked retired in the canonical files.
- Verdict file pattern R3-xxx-A1/A2/B1/B2/TB.json agrees between the re-plan (section 9) and the
  execution plan (line 241, dir ~/workspace/rung3-verdicts/, which exists and is empty).

Mismatches (every one must be fixed or explicitly accepted before task 1):

- M1. State file recorded thu-tu-chay.txt sha256 is stale.
  State file line 67 (note 2026-11-24T18:48:27+07:00) records thu-tu-chay.txt sha256
  9f47a3a20ae5a957f4f921b9dafa5261baf6366a7e62466866dfbd813b891d13. Actual sha256 of the current file,
  computed 2026-11-25: eaffee95e281efa1b9611efe09f0b60ee1f1424dc5747b275530763e5234bdba.
  Cause: the 20:02 verifier fix changed the tip stamp in thu-tu-chay.txt (7aeaf0f to ccd83e5) without
  recording a new hash.
- M2. State file recorded du-phong.txt sha256 is stale.
  State file line 66 (note 18:20) records du-phong.txt sha256 3648a7d504e7b8dd450c7f4ce2fe1dff3cc9e21de8c2f07524b31f872d063ae0.
  Actual sha256 of the current file, computed 2026-11-25: a57b488f15850413b02918df31db6c985f19e67f7a50fd5899ef121a531a5779.
  Cause: same 20:02 tip-stamp update (d58d3da to ccd83e5), no new hash recorded. The tip stamps themselves
  (ccd83e5 in both files) do match the canonical tip.
- M3. Phase 0 checklist status item 14 is stale.
  File r3-l3-phase0-checklist-status.md line 33 claims thu-tu-chay.txt tip 7aeaf0f and sha256
  b2b8c985fbb392b830d34d2b71af37317eb92c6b5292c6e27752bf1d38b9960b. Actual: tip ccd83e5,
  sha256 eaffee95e281efa1b9611efe09f0b60ee1f1424dc5747b275530763e5234bdba.
- M4. Phase 0 checklist status item 9 is stale.
  File r3-l3-phase0-checklist-status.md line 23 claims the state file is "currently 2026-11-24T17:45:00+07:00".
  Actual state file last_updated: 2026-11-24T20:02:00+07:00.
- M5. Phase 0 checklist status item 1 repeats the stale du-phong hash (same as M2):
  line 11 records sha256 3648a7d5, actual a57b488f.
- M6. Execution plan carries stale scorer ids (4 ids, 13 occurrences).
  Pair B scorer 1B 2890a5de (line 181) vs canonical 4e2f52d4-f3f7-41ad-a302-78f0aee91895.
  Pair B scorer 2B b8c9b7b8 (line 182) vs canonical 2e3ae678-2a82-496e-b301-7ac090356fb3.
  Pair A tiebreaker 6e844611 (lines 183, 196, 220, 383, 477) vs canonical 97290681-d2ce-4230-9869-13c1c68df5d1.
  Pair B tiebreaker 3f3aca86 (lines 184, 383, 477) vs canonical df4defcc-050b-47c0-8609-cb2932e36207.
  Lines 383 and 477 also name 6e844611 and 3f3aca86 as the fallback scorer 1 designations; the re-plan
  names TB-A (97290681) and TB-B2 (df4defcc) instead.
- M7. Execution plan carries stale counts and tip.
  Class L 5, Class S 50 (lines 23 and 152, including the lane arithmetic "5 Class L, 50 Class S")
  vs canonical 9 and 46. Branch tip 175cfd7 (line 19) vs canonical ccd83e5.
  Note: line 222 of the execution plan itself flags that the exception list must be republished before
  task 1; the republication happened (17:12) but the plan text was never updated.
- M8. The "superseded on ids" stamp does not exist.
  The re-plan G-32 says the execution plan is stamped as superseded on ids. Grep for "superseded"
  in the execution plan returns zero hits. The stamp was never applied to the file.
- M9. State file live PIDs are stale after the laptop reboot (see the reboot note below).
  State file records FCC pane PID 203375 (runners.fcc.pane_pid). The laptop rebooted about 08:44 on
  25/11; the FCC tmux session r3-fcc-runner-L3 was recreated 09:00:18 with new PIDs (tmux 20571,
  fcc-claude 22399). PID 203375 no longer exists. The execution plan Z6 Zen PID 404548 is likewise
  superseded (live Zen PID is now 6444, started 08:45:30).
- M10. State file records the Mochi session only as an 8-hex prefix.
  State file scorers.pair_a_1: "mochi (session 70cd99d1)". Thu-tu-chay.txt and the execution plan
  (line 27) carry the full UUID 70cd99d1-ecef-4d02-9f42-714d7e86ab85. The prefix matches; the full id
  is absent from the state file.

Fix for G-32 green: (a) recompute and record the current sha256 of thu-tu-chay.txt (eaffee95...) and
du-phong.txt (a57b488f...) in the state file; (b) update phase0-checklist-status items 1, 9, 14, or mark
that file superseded by the state file; (c) add the SUPERSEDED-on-ids stamp to the execution plan, or
correct its stale ids, counts and tip in place; (d) update the state file live PIDs after the reboot
(FCC pane PID, Zen PID) or record them as re-verified at T+0.

## Updates-off check procedure (clone1 open item 1.7) - DEFINED

Clone1 risk 1.7: "The update lock is not verified." The council disposition (clone1 meeting input
line 59) left the verification method as an open item for the run lead to define before launch.
This section defines it. It is the procedure, not a one-off result.

Checklist (all must pass; run it after every Zen restart or reboot, and at T+0):
1. user.js in the run profile holds both pins. Path on the laptop:
   ~/.config/zen/ae59l0ak.Default (release)/user.js. Required lines:
   user_pref("app.update.enabled", false);
   user_pref("remote.prefs.recommended", false);
   The second pin matters because pinning remote.prefs.recommended=false re-enables the auto-update
   that recommended prefs normally block, so the explicit app.update.enabled=false guard is required
   in the same file.
2. prefs.js in the same profile holds both pins as effective prefs (live, flushed after the last Zen
   start): app.update.enabled=false and remote.prefs.recommended=false. A pin present in user.js but
   absent from prefs.js is not yet proven effective; the check fails until Zen has started and flushed.
3. No staged update exists. All four must be absent: the install dir /opt/zen-browser-bin/updates/,
   the profile updates/ dir, updates.xml in the profile, active-update.xml in the profile.
4. The running Zen is still 1.24.3b, BuildID 20261118023529 (application.ini plus the live process),
   with ports 9222 (BiDi) and 2828 (Marionette) listening on 127.0.0.1.
5. Caveats that do not fail the check but must be recorded: the install ships an updater binary and
   update-settings.ini (ACCEPTED_MAR_CHANNEL_IDS=release), so the pref is the operative guard, not the
   absence of an updater. Firefox 161.0 was released 2026-11-24, so a Zen rebase is coming; the freeze
   holds only while the pins are effective and nothing is staged.
6. A live about:config read is NOT part of this procedure. It needs a BiDi or Marionette session, the
   single-session rule forbids opening one for this check, and Firefox forbids WebDriver navigation to
   about:config. File evidence (user.js plus prefs.js) is the verification. If a session is already open
   for other work, a spot-check may be added, but it is optional.

Live re-verification by this worker, 2026-11-25 09:01-09:03 +07 via SSH (read-only):
- Both pins present in user.js AND in prefs.js (two occurrences each in the grep output).
- No updates dirs or files: /opt/zen-browser-bin/updates/ absent, profile updates/ absent,
  updates.xml absent, active-update.xml absent.
- Running Zen: Version 1.24.3b, BuildID 20261118023529 (application.ini). Ports 9222, 2828, 9223, 9224
  all listening on 127.0.0.1.
- Result: PASS as of 09:03 +07. This re-verification was required because the last recorded check was
  about 20:10 on 24/11 (Zen doc lines 125-130), before the 20:44 council restart and before the
  25/11 reboot. The next re-check is at T+0.

## G-24: deputy re-confirmation - NOT DONE

- Deputy declaration: ~/workspace/r3-l3-deputy-declaration.md, read 2026-11-24 17:24:46 +07.
- State file last_updated: 2026-11-24T20:02:00+07:00. The declaration predates the last state-file update
  by 2 hours 37 minutes.
- The re-plan G-24 explicitly says the old declaration (17:24, listing the rejected tiebreaker B
  9d613f19) is stale and does not count, and that a confirmation older than the last material state
  change does not satisfy G-24.
- Material state changes after 17:24 include: the 18:48 blocker fix (scorer id corrections, ledger
  pattern change, verdict channel decision), the TB-B2 approval (17:31), the R3-047 invalid candidacy
  (18:02), the 20:02 TB-B2 verification-gap correction and tip update to ccd83e5.
- No newer deputy confirmation exists in any file searched (scoped grep over the run-log docs, the
  re-plan, the execution plan, and the state file; no re-confirmation line in the state file).
- Needed: the deputy re-reads the CURRENT state file (last_updated 20:02:00+07:00) and re-confirms in
  writing with a new timestamp after 20:02, either as an appended declaration or as a confirmation
  line in the state file. The deputy session is 028399b1-634c-4b37-84d1-6c8689c87ab8.
- This worker cannot reach the deputy session: there is no channel from this subagent to message an
  arbitrary session id, so the re-confirmation could not be prompted from here. The parent must prompt
  the deputy directly.

## G-38: deputy dry-run - NOT DONE / BLOCKED

- No dry-run record exists in any run file. Grep for dry-run and dry run across the run-log docs and
  the re-plan finds only the gate definition itself (re-plan G-38, section 7, section 9).
- Needed: the deputy lists every live worker from the state file and confirms the contact path
  (SSH/tmux/session) for each, and the result is recorded in the run log. Live workers from the state
  file: coordinator 68a84d25-2e88-48b1-b2ee-9911e2a4191c; FCC session r3-fcc-runner-L3; Codex via codex
  exec (no interactive session); Mochi (session 70cd99d1); scorer 2 Pair A dc7e0d0d-24b2-4d94-9729-f106d21eff16;
  1B 4e2f52d4-f3f7-41ad-a302-78f0aee91895; 2B 2e3ae678-2a82-496e-b301-7ac090356fb3;
  TB-A 97290681-d2ce-4230-9869-13c1c68df5d1; TB-B2 df4defcc-050b-47c0-8609-cb2932e36207.
- This worker cannot reach the deputy session 028399b1 to prompt the dry-run (no channel from this
  subagent to an arbitrary session id). The parent must prompt the deputy directly.
- Live complication found by this worker: the laptop rebooted about 08:44 on 25/11 (see below), and the
  FCC tmux session was recreated 09:00:18 with new PIDs, so every contact path recorded last night is
  stale. The dry-run must use post-reboot PIDs and sessions, not the state file values as written.

## G-27: run-tab protection - PARTIAL

Recorded live numbers (SSH to the laptop, 2026-11-25 09:02 +07, read-only):
- Total RAM: 31702 MB (about 31 GB). Used 9135 MB, free 13222 MB, available 22567 MB (about 22.1 GB).
  Swap 36821 MB total, 0 used.
- Zen total RSS: 1835 MB across 12 zen-exe processes (main PID 6444, RSS about 606 MB, started
  08:45:30). Method: summed RSS of every /proc pid whose exe links to a zen binary.
- Headroom to the 8 GB RSS threshold: 8192 minus 1835 equals 6357 MB (about 6.2 GB). The 8 GB threshold
  is armed for the Z3 restart.
- Last night baselines are superseded by the reboot: probe about 19:51 (30 GB RAM, 17 GB available,
  Zen RSS about 2.5 GB) and the 20:44 council restart (PID 788926, main RSS 663052 KB, 72 tabs,
  49 pinned). The live numbers above replace them.

Not verified (G-27 cannot go green until these are recorded at T+0):
- Run tab PINNED: no file records which tab is "the run tab" or its pinned state as a checkable fact.
  The closest recorded facts are 72 tabs and 49 pinned at the 20:44 restart, superseded by the reboot.
  Pinned-state verification needs a live BiDi or sessionstore read at T+0 (G-35 final pass).
- about:unloads baseline: not recorded anywhere. The Zen doc (line 79) recommends opening about:unloads
  once and recording the unload priority order; no record exists. Needs a live browser read at T+0.
- The unload pref is DROPPED as a verification per the re-plan: browser.tabs.unloadOnLowMemory does not
  exist in this build and is a no-op (council decision: confirmed directly in the shipped firefox.js
  defaults).

Marionette PARTIAL, recorded as an accepted risk (re-plan section 4 risk 8, G-27):
- BiDi is primary; Marionette fallback is unproven (newSession returns zero bytes, cause unproven;
  protocol v3 array framing is required; chrome-context pref reads are blocked without
  MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1; no second restart was done to add it). Response to a zombie BiDi
  session is the Z3 restart, not Marionette. Do NOT restart Zen to fix it. Date: 2026-11-24.
  Owner: not named in the re-plan; recorded owner is the run coordinator (to confirm).

## G-40: correlated-outage wait - DONE

- Maximum wait: 60 minutes, then escalate to the owner. Recorded here, per re-plan G-40, F-23, and
  section 9 run-stop conditions.
- Backup-exhaustion rule: a correlated event that invalidates more tasks than the remaining backups of
  that difficulty leaves the run short, and the coordinator escalates to the owner rather than
  improvising. The coordinator does not improvise a re-split.
- The coordinator may change the 60-minute value only with a reason recorded in the run log. Task 1
  must not start with the value blank; it is now recorded.

## G-41: per-task report file - DONE (created by this worker)

- File: ~/workspace/r3l3-run-wt/rung3-run-log/r3-l3-per-task-reports.log (974 bytes, created 2026-11-25).
- No such file existed before this worker created it (searched the run-log dir and the worktree; the
  reporting-chain watch had no file to grep).
- Format (header in the file): one pipe-delimited line per graded task, append-only:
  TIMESTAMP | TASK_ID | VERDICT | PAIR | TIEBREAKER | INVALID_OR_BACKUP | ELAPSED.
  TIMESTAMP is ISO 8601 with timezone. VERDICT is PASS, FAIL, or INVALID. PAIR is A or B.
  TIEBREAKER is the tiebreaker session short id if one was invoked, else "-".
  INVALID_OR_BACKUP is "INVALID:<reason> -> <backup>" when invalid, "BACKUP:<backup>" when a backup
  ran, else "-". ELAPSED is task wall time, e.g. 14m22s.
- Zero rows so far. The run has not started.
- Note: the reporting-chain watch cron that greps this file is G-34, not this gate, and is not created here.
  The heartbeat log file (re-plan section 8) is a separate file and is not created by this gate.

## G-48: state file atomic write - NOT VERIFIED (procedure defined below)

- Findings: no script or doc describes how the state file is written. Grep for "coordinator-state"
  across the worktree finds only .md references (council/redteam docs, timeout-watch.md, checklist
  status); no .py or .sh writer exists. Past state writes were manual file writes; their atomicity is
  unproven.
- What was verified: the current state file parses as JSON (json.load OK, 23 top-level keys) and its
  mtime is sane (file mtime 2026-11-24 20:01:22 +07 vs last_updated 2026-11-24T20:02:00+07:00).
  Parse plus sane mtime is necessary but not sufficient for G-48.
- Procedure defined here, to be adopted by the coordinator before task 1 (no past write is claimed
  atomic):
  1. Write the new state JSON to r3-l3-coordinator-state.json.tmp in the same directory (never write
     the live path directly).
  2. Read the temp file back and JSON-parse it. If it fails to parse, stop and fix it; do not rename.
  3. Rename the temp file over the live file (os.rename, atomic on the same filesystem).
  4. Read the live file back, JSON-parse it, and confirm its mtime advanced past the previous value.
  5. The deputy verifies the file parses and its mtime is sane before trusting it, and falls back to
     the ledger tip plus the run log if it does not parse.
- Verdict: procedure defined; adoption plus the first atomic write are still needed before task 1.

## G-49: ledger cross-check - PARTIAL

- What exists and works: rung3-ci/validate-ledger.py. Run by this worker on 2026-11-25 against
  rung3-run-log/R3-L3-grades.jsonl: "PASS: ledger valid: 1 row(s), 0 errors", exit 0.
  The ledger holds 1 trial row only (test_row true, task_id R3-TEST), ends with a newline (verified
  with od), and parses. Schema task pattern DP-0[123567] matches the live backup set.
- What does NOT exist: no script diffs each ledger row against its verdict files (task ID, verdict,
  pair). validate-ledger.py validates schema, verdict enums, grade consistency, and duplicates only;
  it never reads a verdict file. rung3-ci/audit-scan.py checks one verdict file's forbidden-read list
  only; it never reads the ledger. No file in rung3-ci reads both the ledger and the verdict files.
- The G-49 alternative (rows generated from the verdict files instead of typed) also does not hold:
  rows are built by the coordinator per r3-l3-ledger-push.md.
- Gap: a ledger-vs-verdict cross-check script is still needed before the first push, or the gate must
  be recorded as an accepted limitation with the coordinator manually diffing each row against its
  verdict files before every push (and recording that diff in the run log).

## P1-H definition - DONE

- Prefs: network.captive-portal-service.enabled=false and network.connectivity-service.enabled=false.
- Council decision: zen-opencode-council-decision-20261124.md, P1-H APPLY (2 APPLY, 1 REJECT).
  Redteam REJECT reason: the connectivity service detects link down/up, and disabling it can delay
  reconnect detection; no portal incident was cited; if a task needs a portal login it fails with no
  diagnosis. Mitigation accepted: reconnection is OS-level; the portal tab stealing the task window is
  a real disruption on flaky campus WiFi; for an unattended run a portal login cannot happen anyway,
  so the portal tab only harms.
- Condition: REVERT both prefs after the run (they persist into daily use otherwise). The revert is a
  post-run step, recorded in the re-plan sections 9 and 10.
- Evidence: both prefs are in the RecommendedPreferences set (verified); shipped defaults are true;
  both appear in prefs.js with exactly the council values (verified in the council decision's
  "All 13 effective" list).
- Note: P1-H is defined in the re-plan and the council decision, NOT in the execution plan (grep for
  P1-H, captive-portal, connectivity-service in the execution plan returns zero hits).

## Material finding outside these gates: the laptop rebooted this morning

- Laptop uptime at 09:02 on 25/11 was 18 minutes, so it booted about 08:44. Zen started 08:45:30
  (PID 6444). Swap use is 0 (was 5.3 GB used at the 24/11 probe), consistent with a reboot.
- Post-reboot live state (SSH, 09:00-09:03 +07): tmux sessions legacy-link, main, and r3-fcc-runner-L3
  all created 09:00:18 today (the FCC session was recreated, not resumed; fcc-claude PID 22399 under
  tmux PID 20571). A codex resume session 01a20bc6-8a12-7691-abdc-aee717c0b37b is running (PID 4232);
  the state file cites session 01a20d16 for the codex exec proof, a different id, which the coordinator
  should confirm. The Messenger daemon runs on the VM (daemon.py PID 12541, watchdog PID 12133, both
  alive), not on the laptop, so no daemon outage is implied by the reboot.
- Consequence: several Phase 0 DONE marks rest on last-night live state (FCC pane PID 203375, Zen PID
  788926, 72 tabs, 49 pinned, 20:44 restart baseline) and need T+0 re-verification (G-35, owned by the
  parent). The deputy dry-run (G-38) must use post-reboot sessions and PIDs.

## What the parent must do before task 1

1. Prompt the deputy (028399b1-634c-4b37-84d1-6c8689c87ab8) directly for two things: (a) re-read the
   CURRENT state file and re-confirm in writing with a timestamp after 2026-11-24T20:02:00+07:00 (G-24);
   (b) run the dry-run listing every live worker and confirming the contact path for each, post-reboot,
   and record the result in the run log (G-38).
2. Fix the G-32 mismatches M1-M10 (recompute and record the two file hashes in the state file; update
   or supersede the phase0 checklist status; stamp or correct the execution plan; update live PIDs).
3. Adopt the G-48 atomic-write procedure and make the first state write after adoption use it.
4. Close the G-49 gap: either a ledger-vs-verdict cross-check script, or a recorded accepted limitation
   with manual per-push diffing by the coordinator.
5. At T+0 (G-35 final pass): verify the pinned run tab and record the about:unloads baseline (G-27),
   and re-verify the post-reboot live state (FCC session, Zen tabs, daemon, codex exec proof session).

## Files created by this worker

- ~/workspace/r3l3-run-wt/rung3-run-log/r3-l3-per-task-reports.log (G-41, new, zero rows)
- ~/workspace/r3l3-run-wt/improvements/r3-l3-prepare-docs-20261125.md (this report)
- No other files were created or modified. No files were committed (per the delivery path, the parent commits).
- No personal info in any file written by this worker. No OpenRouter used or proposed.
