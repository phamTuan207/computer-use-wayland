# COORD-A1-RESUME log: A1 pilot resume, relay re-verification + preconditions + preflight

- Coordinator: COORD-A1-RESUME. Task received: 01:58 +07, 23/11/2026.
  ZT-B run 6 PASS (F4 fix verified live, ZT-B done), so A1 resume unlocked.
  Machine quiet (owner confirmed 23:58 22/11 not touching machine, all
  machine-use alarms are false, keep doing live). Single lane: A1 only,
  no extra ZT-B.
- Rules: 18:23 (never close or navigate any tab or window the owner
  opened); 18:30 (pill must show on any agent control; the preflight
  probes run inside real computer-use sessions whose guardian creates
  the pill and fails the session outright when the pill cannot appear,
  so all probe writes happen under a visible pill; no raw CDP writes);
  no em dash (U+2014) or en dash (U+2013) anywhere in this file; no
  ydotool; no personal info on GitHub; explicit pathspec commits only
  (`git add -- <path>` then `git commit -m` with no pathspec argument,
  never `git commit -- <paths>`, never `git add -A`, never amend);
  no self-grading, Muse tong verifies independently.
- Evidence standard (Lauren Tan): every claim carries command, output,
  commit hash, and wall-clock time (Asia/Ho_Chi_Minh) with elapsed time.
- Sources read: improvements/w-a1prep2-log.md (prep round 2, commit
  f64ba70), section 4 draft resume order; tests/realistic/a1-pilot/
  runbook.md (253 lines). Sealed manifest contents NOT read (only hash
  and size verified, section 1). The 12 pilot runs are NOT run in this
  task: they need a Codex executor session on the laptop and Muse tong
  reading the sealed manifest to issue run-ids one at a time, per the
  runbook. This task is the resume infrastructure only.

## 1. H2 (fresh HEAD at resume time) and manifest F1

- VM, 01:58 +07 23/11/2026: `git fetch origin && git checkout
  todolist-push && git pull --ff-only origin todolist-push &&
  git rev-parse HEAD`.
- H2 = 3f7059190971b21506dce228f002bbb14694828c.
  Log line: "ZT-B run 6 PASS: F4 fix verified live, ZT-B done
  (COORD-CLICK-14)".
- Manifest: ~/workspace/a1fix-sealed/a1-manifest.jsonl. sha256
  470df41818c2ad5637c9429f32cace50cad18568eb6d2a1069ca1a1107d21bc7.
  Size 1599 bytes. Lines 12. Expected sha256 (from W-A1PREP2 log F1):
  470df41818c2ad5637c9429f32cace50cad18568eb6d2a1069ca1a1107d21bc7.
- Verdict: MATCH. Hash matches exactly, size 1599 bytes, 12 lines.
  Contents NOT read, NOT reproduced here. The mapping stays sealed.

## 2. Laptop state before sync (read-only SSH)

- Laptop HEAD before sync: 0031449ef0ee241a8af605cecbcd0119943cfe1e.
  Log line: "F4 review evidence: council + redteam, first round and
  re-review". NOT equal to H2 (3f70591). Laptop behind.
- `git status --short` (laptop): only untracked files
  (improvements/cf26-polygon-upload-lessons-20261120.md,
  improvements/latency-probe-20261120-results.csv,
  improvements/latency-probe2-20261120-results.csv,
  improvements/live-a2t-20261120/, improvements/live-a4r-20261120/).
  Tree clean apart from untracked files, fast-forward safe.
- Relay before restart: ActiveState=active, MainPID=70985 (same PID
  as the F3 restart at 18:32:03 +07 22/11; not restarted since).
- Broker before restart: {"ok":true,"broker":"running",
  "broker_generation":"8624ae4023d6dc0d1ea2b6a45b64ef93",
  "loaded_code_sha256":
  "d490f369f6b754d200518055025ef956284a759cc49e3ee70ed6b2a4483e3da4",
  "started_git_head":"4eb591764c7ac5741c7ef34c5102ab387c54c284",
  "state":"finished","owner":"s2-flip-run6","generation":
  "2c69261582def25ba8936413d09f2f8d","driver":"stopped","guardian":
  "clean","cancelled":false,"cancellation_state":"clear",
  "recovery":"none","next_sequence":3,"active_sequence":null,
  "last_start_error":"cleanup_failed","last_status_error":null,
  "error":"cleanup_failed","stop_reason":"explicit_finish"}.
  Idle in effect (state finished, driver stopped, active_sequence
  null, no active session), but started_git_head 4eb5917 STALE and
  the cleanup_failed marker still present. Restart required.
- Fixture server before restart: python3 http.server port 8768,
  PID 45976, listening on 127.0.0.1:8768, etime 07:57:53. Alive.

## 3. Laptop sync to H2

- Command (laptop, over SSH): `cd ~/computer-use-wayland
  && git fetch origin && git pull --ff-only origin todolist-push &&
  git rev-parse HEAD`.
- Output: fast-forward, new files created including
  improvements/c5-zenproof-runs/run-6.json and
  improvements/coord-click-14-log.md.
- HEAD after sync: 3f7059190971b21506dce228f002bbb14694828c.
  Log line: "ZT-B run 6 PASS: F4 fix verified live, ZT-B done
  (COORD-CLICK-14)".
- Verdict: laptop HEAD equals H2. MATCH.

## 4. Relay restart and F3 re-verification

- Idle check immediately before restart: broker idle in effect
  (section 2: state finished, driver stopped, active_sequence null,
  no active session). No live session to kill. Safe to restart.
- Command (laptop, over SSH): `systemctl --user restart
  computer-use-relay.service`, sleep 3, then verify.
- Relay after restart: ActiveState=active, MainPID=377403 (new PID).
- Live process env (/proc/377403/environ): CU_CODE_EXEC=1,
  CU_PICK4_FASTPATH=1. Both present.
- Drop-in flags.conf: [Service], Environment=CU_CODE_EXEC=1,
  Environment=CU_PICK4_FASTPATH=1. Persists.
- Broker after restart: {"ok":true,"broker":"running",
  "broker_generation":"d363d8c89940ecdd06f749013868f389",
  "loaded_code_sha256":
  "d490f369f6b754d200518055025ef956284a759cc49e3ee70ed6b2a4483e3da4",
  "started_git_head":"3f7059190971b21506dce228f002bbb14694828c",
  "state":"idle","owner":null,"generation":null,"driver":"idle",
  "guardian":"idle","cancelled":false,"cancellation_state":"clear",
  "recovery":"none","next_sequence":1,"active_sequence":null,
  "last_start_error":null,"last_status_error":null}.
- Verdict: F3 re-verification PASS. started_git_head equals H2
  (3f70591). Both flags =1 in live process env. Broker truly idle
  (state idle, driver idle, guardian idle, active_sequence null,
  owner null). cleanup_failed marker CLEARED (last_start_error null,
  last_status_error null, no error field). New broker generation
  d363d8c8. Next sequence 1.

## 5. Desktop check (read-only hyprctl)

- Active workspace: 1 (ws1), 1 window, last window 0x56307e2771d0
  "Chat - Muse - Zen Browser". Zen on ws1, untouched.
- Clients: herdrdrop terminal (special:herdrdrop); Chromium
  "Chat - mochi - Chromium" (ws2); Brave "Muse - Brave Origin"
  (ws2, mei); Zen "Chat - Muse - Zen Browser" (ws1).
- Chromium /json/list: ONLY A67A718D "Chat - mochi"
  (https://muse.ai/). The 6 fixture tabs were closed at the 22:05
  screen cleanup and are NOT reopened. No fixture tab open.
- Verdict: desktop clean. Zen untouched on ws1. Chromium only
  mochi's chat. Brave mei live. No owner tab closed or navigated.
  The Chat - Muse tab was NOT reopened by me (it was already open
  on ws1; the owner reopened it before run 5).

## 6. Fixture md5s (all three copies)

- VM repo, laptop repo, served dir /tmp/a1fix-20261122/fixtures/:
  - pick4-fixture.html: 91b2f92945c167306a13ae32977a9bf3.
  - test-01-spreadsheet.html (f01):
    2b6eda97036af51510b7eefe6d36dd93.
  - test-06-file-converter.html:
    b989fe26ed497b24301467fd3ca38663.
  - test-07-weather-dashboard.html:
    be0eeafe893680f4ca47abfbfb9d5888.
  - test-08-quiz-app.html:
    7688f92ddad686fab9b0f456d13a51c6.
  - test-09-pomodoro-timer.html:
    f8d286e522f11c0da4a7c27c2676946d.
  - test-10-markdown-editor.html:
    6a819e3947b4beca6d334c78d9473b39.
- All 7 md5s identical across VM repo, laptop repo, served dir, and
  match the frozen values in FREEZE.md and the W-A1PREP2 log.
- Note: the first md5 attempt used short names (test-06.html etc.)
  and failed "No such file or directory"; the real filenames carry
  full suffixes (test-06-file-converter.html etc.). Re-checked with
  correct names, all MATCH. No file missing.
- Verdict: MATCH on all three copies.

## 7. Preflight probes under the resumed relay (RUN, 5/5 PASS)

- Helper pre-check (required): /tmp helpers on the laptop PRESENT,
  sha256 match prep round 2 (mtime 21:42 +07 22/11):
  /tmp/c5-activate.mjs 74af25d2..., /tmp/c5-count.mjs d0f4e254...,
  /tmp/s2-v12.mjs dd588e84..., /tmp/s2-p9.mjs b39829e1.... No restore
  needed.
- Driver md5: 6e764940641b5c338e17654bf2ba3a34 on BOTH VM repo and
  laptop repo (tests/realistic/a1-pilot/run_preflight_probes.py).
- Command (VM), start 18:59:23 UTC (01:59:23 +07 23/11): `python3
  tests/realistic/a1-pilot/run_preflight_probes.py --out
  /tmp/a1fix-preflight`. Finished 19:00:10 UTC (02:00:10 +07).
  Wall 46.5s. Exit 0. Summary all_ok true.
- Results (times +07 23/11, driver ts labels are VM clock UTC
  mislabeled +07:00, true wall 01:59-02:00 from exec timing):
  - click, probe_ms 8758.9: P1 ok false, error "ref is not present
    in the bound snapshot; observe again" (expected bad-ref),
    navigate act ok True, new tab 78373C53A233EB76F2EC8D1FEDF5AD2A;
    P2 ok true, "#result still not clicked yet", same tab true,
    verify image ef201946ff89.jpg. PASS.
  - fill, probe_ms 8745.0: P1 ok false, same bad-ref error,
    navigate act ok True, new tab EA365EF1A9407FEA336571A91B2D42ED;
    P2 ok true, "#a2 still -", same tab true, verify image
    ae26c1aa8f5d.jpg. PASS.
  - set_value, probe_ms 8773.9: P1 ok false, same bad-ref error,
    navigate act ok True, new tab 4551D959396D62FFA5E2D5EBD346A515;
    P2 ok true, "#a2 still -", same tab true, verify image
    cde526c36a11.jpg. PASS.
  - assert, probe_ms 8741.0: P1 ok false, same bad-ref error,
    navigate act ok True, new tab 63FFC91F7A8838B7C0C4D051B8ED75D5;
    P2 ok true, "#result still not clicked yet", same tab true,
    verify image d0c93052feb1.jpg. PASS.
  - retry-logging, probe_ms 10689.9: P1 ok true, retry_logged true:
    "first dom_act ok False completed 0", "retry dom_act ok True
    completed 1", "retry confirmed pick4-ok", new tab
    2D76CCA14D96B3B83D698B3BEBDB6FC4; P2 ok true, "#result contains
    pick4-ok", same tab true, verify image 3f2dcefd4d98.jpg. PASS.
- Verdict: 5/5 PASS, all_ok true, driver exit 0. The resumed relay
  (PID 377403, H2 3f70591) works live. Probe 5 retry works live.
- Probe dirs on the laptop: /tmp/a1-pilot-20261121/runs/preflight/
  probe-1-click, probe-2-fill, probe-3-set-value, probe-4-assert,
  probe-5-retry-logging, each with end-state.json, run-log.jsonl,
  verify.png. preflight-log.jsonl now 30 lines (10 F4FIX run +
  10 prep round 2 re-probe + 10 this run).
- Pill: every probe runs inside a real computer-use session (cu.py
  session plus session-driver relay); the session guardian creates
  the indicator pill before the driver starts and fails the session
  outright when the pill cannot appear, so all probe writes happen
  under a visible pill. No raw CDP writes in this session.

## 8. Post-preflight state

- Broker after preflight: state idle, owner null, driver idle,
  guardian idle, active_sequence null, started_git_head 3f70591
  (= H2), last_start_error null, last_status_error null, broker
  generation d363d8c8 (unchanged from the restart). All probe
  sessions ended cleanly. No active session.
- Chromium tabs after preflight: 5 new probe tabs (2D76CCA1,
  63FFC91F, 4551D959, EA365EF1, 78373C53, all fixture URLs on
  127.0.0.1:8768) plus mochi's chat A67A718D. No owner tab was
  navigated or closed. The 5 probe tabs are left open: the driver
  does not close tabs, and closing via /json/close is banned since
  the 18:11:22 +07 Chromium scope end. Same behavior as prep round 2.
  These are NEW tabs from this preflight run, not a reopen of the
  22:05-closed fixture tabs.
- CB-2 amendment (runbook template navigate act stamped with scope
  and observation_id): DONE, commit a51cf9c, verified by grep in
  prep round 1. Not re-checked here; no runbook change since.

## 9. Verdict: A1 pilot resume PASS

- (1) Relay F3 re-verification: PASS. H2 3f70591 on VM and laptop,
  relay restarted (PID 377403), flags CU_CODE_EXEC=1 and
  CU_PICK4_FASTPATH=1 in live process env and drop-in,
  started_git_head equals H2, broker truly idle, cleanup_failed
  marker cleared.
- (2) Broker SOLO and idle: PASS. State idle, driver idle, guardian
  idle, active_sequence null, owner null, no active session, before
  and after the preflight probes.
- (3) Desktop clean: PASS. Zen untouched on ws1, Chromium only
  mochi's chat plus the 5 new preflight probe tabs, Brave mei live,
  no owner tab closed or navigated, Chat - Muse tab NOT reopened
  by me.
- (4) Fixture md5s: PASS. All 7 match on VM repo, laptop repo,
  served dir, and the frozen values.
- (5) Preflight probes under resumed relay: PASS. 5/5, all_ok true,
  exit 0, wall 46.5s. Probe 5 retry works live.
- (6) CB-2 amendment: DONE (commit a51cf9c).
- Manifest F1: MATCH (sha256 470df418..., 1599 bytes, 12 lines,
  contents not read).
- The A1 pilot resume is complete and PASS. The pilot is ready for
  Muse tong to read the sealed manifest and issue the 12 run-ids
  one at a time to a Codex executor session on the laptop, per the
  runbook. The 12 pilot runs themselves are NOT run in this task.
- No H3 record written by COORD-A1-RESUME (only Muse tong writes
  it). No resume order issued by COORD-A1-RESUME beyond this log.
  No tab or window of the owner was closed or navigated. No live
  pilot arm was run.
