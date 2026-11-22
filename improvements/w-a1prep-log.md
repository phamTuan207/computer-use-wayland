# W-A1PREP log: prepare A1 pilot resume order (prep only, no issue)

- Owner: Pham Tuan. Worker: W-A1PREP, for COORD-CLICK-7 (campaign COORD-CLICK-7).
- Task received: 18:59:46 +07, 22/11/2026. Task: PREPARE the resume order only.
  W-A1PREP does NOT issue the resume order (only Muse tong issues it).
  W-A1PREP does NOT write any H3 record (only Muse tong writes it).
  No live arm run in this session: no pilot run, no probe run, no browser
  driving. Owner is using the machine. All laptop checks are read-only SSH.
- Rules acknowledged: 18:23 (never close or navigate any tab or window
  Pham Tuan opened; open a new tab or window beside it if a browser is
  needed); 18:30 (pill must show when any agent drives the machine; this
  session is read-only, no live browser work, so no pill question arises;
  if browser touch were needed I would stop and report first); no em dash
  (U+2014) or en dash (U+2013) anywhere in this file; no ydotool; no
  personal info on GitHub; explicit pathspec commits only
  (`git add -- <path>` then `git commit -m` with no pathspec argument,
  never `git commit -- <paths>`, never plain commit, never `git add -A`,
  never amend); no self-grading, COORD-CLICK-7 verifies independently.
- Evidence standard (Lauren Tan): every claim carries command, output,
  commit hash, and wall-clock time (Asia/Ho_Chi_Minh).
- Sources read before work: improvements/w-a1fix-f1f6-log.md (F1, F2, F3,
  F4, F5, F6), improvements/coord-click-6-log.md (W-A1FIX done, F4
  decision, W-F4FIX done, W-F4LAND done, A1 resume unblocked pending
  relay re-verify).

## 0. Session start and HEAD movement observed

- 18:59:50 +07 (11:59:50 UTC), VM: `git rev-parse HEAD` returned
  c97d61735907b995850f273803eb6869634ff703. Log line: "docs:
  COORD-CLICK-6 log, W-F4LAND done (F4 landed 658c432, 7/7 suites
  green), 14/14 lanes complete, campaign status".
- 19:00:55 +07, VM: `git rev-parse HEAD` returned
  d59c2b8b007d16de743ca1abbf89290fe7bd3131. Log line: "docs:
  COORD-CLICK-7 log, resume tu CLICK-6, pill answer 279a8c3, spawn
  W-SOAKRESTART + W-A1PREP".
- Fact: HEAD moved c97d617 to d59c2b8 DURING this prep session (one
  docs-only log commit). This proves again that HEAD moves with every
  log commit, so the relay re-verification at resume time is mandatory
  and must use the HEAD current at that moment (H2), not any HEAD
  recorded in this log.
- VM tree at 19:00:55 +07 (`git status --short`): modified
  tests/realistic/clone1-batch3/results.json (NOT mine, never added or
  committed) plus untracked improvements files from other workers (NOT
  mine). Only this log file is added and committed by W-A1PREP.

## 1. Manifest F1 verification (hash and size only, contents NOT read)

- File: ~/workspace/a1fix-sealed/a1-manifest.jsonl (VM path
  /home/hatch/workspace/a1fix-sealed/a1-manifest.jsonl).
- Command (VM), 18:59:50 +07: `sha256sum
  ~/workspace/a1fix-sealed/a1-manifest.jsonl; stat -c '%s bytes, %n'
  ...; wc -l ...`.
- Output: sha256
  470df41818c2ad5637c9429f32cace50cad18568eb6d2a1069ca1a1107d21bc7.
  Size 1599 bytes. Lines 12 (12 run-ids). Meta file
  a1-manifest.jsonl.meta.json exists, 153 bytes.
- Expected sha256 (from W-A1FIX log F1 and the task brief):
  470df41818c2ad5637c9429f32cace50cad18568eb6d2a1069ca1a1107d21bc7.
- Verdict: MATCH. Hash matches exactly, size 1599 bytes matches the
  sealed value, 12 lines match. The file contents were NOT read and
  are NOT reproduced here. The mapping stays sealed.
- Pool (from W-A1FIX log F1, not re-derived here): test-06, test-07,
  test-08, test-09, test-10, live-validated 5/5 in F2. Order: Case A
  pairs 1-3 then Case B pairs 1-3, stratified.

## 2. Relay verification at current HEAD, F3 procedure (read-only SSH)

- SSH route: ~/workspace/ssh-laptop.sh (read-only commands only, no
  restart, no sync, no write on the laptop).
- Relay unit: computer-use-relay.service (user service). Drop-in:
  /home/james/.config/systemd/user/computer-use-relay.service.d/flags.conf.
- Command (laptop, over SSH), about 19:00 +07:
  `cd /home/james/computer-use-wayland && git rev-parse HEAD &&
  git log --oneline -1 && git status --short | head -20`,
  then `systemctl --user show computer-use-relay.service -p MainPID
  -p ActiveState -p Environment`, then `tr '\0' '\n' <
  /proc/$PID/environ | grep -E 'CU_CODE_EXEC|CU_PICK4_FASTPATH'`,
  then `cat` the drop-in, then `python3
  /home/james/computer-use-wayland/scripts/session_remote.py status`.
- Output, laptop checkout:
  - HEAD 331523f83834596e44af5046e880b717eb58f1e1. Log line: "test:
    W-F4FIX probe driver opens a NEW tab per probe (rule 18:23)".
  - `git status --short` (laptop): `M scripts/cdp.mjs` plus untracked
    improvements files (cf26-polygon-upload-lessons-20261120.md,
    latency-probe-20261120-results.csv,
    latency-probe2-20261120-results.csv, live-a2t-20261120/,
    live-a4r-20261120/). The `M scripts/cdp.mjs` is the F4 worker-loop
    patch W-F4FIX applied directly on the laptop before it landed in
    the repo as 658c432; it is NOT mine and I did not touch it.
- Output, relay:
  - ActiveState=active, MainPID=70985 (same PID as the F3 restart at
    18:32:03 +07; the relay has NOT restarted since F3).
  - Environment=PYTHONDONTWRITEBYTECODE=1
    XDG_CACHE_HOME=/home/james/.cache CU_CODE_EXEC=1
    CU_PICK4_FASTPATH=1. Both flags present.
  - /proc/70985/environ: CU_CODE_EXEC=1, CU_PICK4_FASTPATH=1. Both
    flags present in the live relay process env.
  - Drop-in flags.conf (69 bytes, verified by cat): [Service],
    Environment=CU_CODE_EXEC=1, Environment=CU_PICK4_FASTPATH=1.
    The drop-in persists across restarts.
- Output, broker status (same SSH call):
  {"ok":true,"broker":"running","broker_generation":
  "8624ae4023d6dc0d1ea2b6a45b64ef93","loaded_code_sha256":
  "d490f369f6b754d200518055025ef956284a759cc49e3ee70ed6b2a4483e3da4",
  "started_git_head":"4eb591764c7ac5741c7ef34c5102ab387c54c284",
  "state":"idle","owner":null,"generation":null,"driver":"idle",
  "guardian":"idle","cancelled":false,"cancellation_state":"clear",
  "recovery":"none","next_sequence":1,"active_sequence":null,
  "last_start_error":null,"last_status_error":null}.
- Comparison:
  - started_git_head of relay: 4eb591764c7ac5741c7ef34c5102ab387c54c284
    (short 4eb5917, the F3 verification HEAD).
  - VM HEAD at check time: c97d617 (18:59:50), then d59c2b8 (19:00:55).
  - Laptop checkout HEAD: 331523f.
  - MATCH: NO. The relay head 4eb5917 equals NEITHER the VM HEAD NOR
    the laptop checkout HEAD. It is stale by every commit since F3.
  - Flags: YES, both present (unit env and live process env and
    drop-in).
  - Broker state: idle, owner null, active_sequence null, driver idle,
    guardian idle, both error fields null. SOLO and idle at check time.
- Verdict: relay flags OK, broker SOLO and idle, BUT started_git_head
  is STALE. Resume is BLOCKED on the F3 re-verification step until the
  laptop is synced to the resume-time HEAD (H2) and the relay is
  restarted and re-verified. I did NOT restart the relay, did NOT sync
  the laptop tree, and did NOT run any live arm, per the brief.

## 3. What the resume order must include to fix the relay (exact commands)

- Because the relay head does not match, the resume order MUST include
  the F3 re-verification sequence from the W-A1FIX log (section F3,
  resume-time re-verification), run at resume time with the HEAD
  current then (H2). Exact commands, copied from that log:
  - (VM) cd ~/workspace/computer-use-wayland && git fetch origin &&
    git pull --ff-only origin todolist-push && git rev-parse HEAD
    (call it H2).
  - (laptop) git fetch origin && git pull --ff-only origin
    todolist-push && git rev-parse HEAD (must equal H2).
  - systemctl --user restart computer-use-relay.service (the flags
    persist via the drop-in, no re-passing needed).
  - Then: tr '\0' '\n' < /proc/$(systemctl --user show
    computer-use-relay.service -p MainPID | cut -d= -f2)/environ |
    grep -E 'CU_CODE_EXEC|CU_PICK4_FASTPATH' (both must print =1)
    and python3
    /home/james/computer-use-wayland/scripts/session_remote.py status
    (started_git_head must equal H2, state idle, active_sequence
    null). Only then issue run 1.
- Extra flag for the resume order (observation, not an order from me):
  the laptop tree is dirty (`M scripts/cdp.mjs` plus untracked files,
  see section 2). The sync step must check `git status --short` on the
  laptop before the pull, because a dirty tree can block a fast-forward
  pull. How to clear it is for Muse tong (or the W-SYNC lane) to
  decide; W-A1PREP does not prescribe a destructive command and did
  not touch the laptop tree. Note: the dirty cdp.mjs diff is the F4
  worker-loop patch that has since landed in the repo as 658c432, so
  the sync step should compare that diff against the landed hunk
  before deciding.
- Broker idle check immediately before the restart is part of the F3
  procedure (state idle, no active sequence, so the restart kills no
  live session). At check time the broker IS idle (section 2), but the
  check must be repeated immediately before the restart at resume time.

## 4. Draft resume order, filled with current HEAD and relay status (DRAFT ONLY)

- This is a DRAFT prepared by W-A1PREP 19:01 +07 22/11/2026 for Muse
  tong to issue. W-A1PREP does NOT issue it. Only Muse tong issues
  the resume order, with a timestamp, after the relay re-verification
  in section 3 is done and passes.
- ---
- RESUME ORDER (draft, prepared by W-A1PREP 19:01 +07 22/11/2026,
  for Muse tong to issue)
- Manifest: ~/workspace/a1fix-sealed/a1-manifest.jsonl, sha256
  470df41818c2ad5637c9429f32cace50cad18568eb6d2a1069ca1a1107d21bc7,
  1599 bytes, 12 lines. Verified MATCH by W-A1PREP 18:59:50 +07
  (hash and size only, contents not read). Muse reads the sealed
  file and issues the 12 run-ids one at a time, in file order
  (Case A pairs 1-3, then Case B pairs 1-3).
- Relay status at prep time (19:00 +07): flags CU_CODE_EXEC=1 and
  CU_PICK4_FASTPATH=1 present (unit env, live process env PID 70985,
  drop-in). Broker idle, owner null, active_sequence null.
  started_git_head 4eb5917 is STALE: VM HEAD was c97d617 at 18:59:50
  and d59c2b8 at 19:00:55, laptop checkout HEAD 331523f. The resume
  MUST run the F3 re-verification sequence in section 3 of the
  W-A1PREP log first (sync laptop to H2, restart relay, verify both
  flags =1 in the live process env, verify started_git_head equals
  H2, state idle, active_sequence null). Only then issue run 1.
  Do NOT reuse the HEAD values in this draft: HEAD moves with every
  log commit, so H2 is whatever `git rev-parse HEAD` returns at
  resume time.
- Preconditions before run 1: (1) relay restarted with
  CU_CODE_EXEC=1 and CU_PICK4_FASTPATH=1 and started_git_head
  equal to the repo HEAD at that time (F3, re-verified at resume,
  see above); (2) broker SOLO and idle per session_remote.py status,
  saved per run (was idle at prep check 19:00 +07, re-check at
  resume); (3) desktop verified clean (hyprctl activeworkspace
  plus clients), Zen untouched, Chromium only, workspace 2 (NOT
  clean at prep check, see section 5; owner is using the machine,
  handover and clean check owed at resume); (4) fixture md5s
  re-verified per run and recorded in setup.json (pick4
  91b2f92945c167306a13ae32977a9bf3, f01
  2b6eda97036af51510b7eefe6d36dd93; all matched at prep check, see
  section 5); (5) preflight probes re-run under the new-tab-only
  procedure (driver run_preflight_probes.py, commit 331523f; F4
  CLOSED, probe 5 PASS live 18:44-18:45 +07, landed 658c432; the
  re-probe itself is still owed at resume, it was NOT run in this
  prep session); (6) runbook template navigate act stamped with
  scope and observation_id (done, commit a51cf9c, verified by grep,
  see section 5).
- Between runs: fresh browser session, storage cleared, fixture
  reloaded, desktop verified clean, each reset logged in
  setup-log.jsonl.
- After run 12: broker-status and desktop checks again (F6
  procedure), then unblinding from the run_start timestamps.
- ---

## 5. Preconditions before run 1, current status (read-only checks only)

- (1) Relay flags + head: flags OK, head STALE. BLOCKS run 1 until
  section 3 is done at resume time. Evidence in section 2.
- (2) Broker SOLO and idle: YES at check time, about 19:00 +07.
  session_remote.py status: state idle, owner null, generation null,
  driver idle, guardian idle, active_sequence null, next_sequence 1,
  broker_generation 8624ae40 (same as the F3 restart), both error
  fields null. No active session. Re-check and save per run at
  resume (a snapshot now does not prove idle at run 1).
- (3) Desktop clean: NO, not clean at check time. Read-only hyprctl
  over SSH (HYPRLAND_INSTANCE_SIGNATURE set from
  /run/user/1000/hypr/, the known non-interactive SSH quirk),
  about 19:00 +07:
  - Active workspace: 2 (ws2), 3 windows, last window
    0x56307e202df0 "Pick 4 DOM fixture - Chromium".
  - Clients: Zen "(5) Chat - Muse - Zen Browser" (ws1, untouched);
    Chromium "Pick 4 DOM fixture - Chromium" (0x56307e202df0, the
    leftover W-A1FIX probe tab window); Chromium "Chat - mochi -
    Chromium" (mochi's chat, live); Brave "Muse - Brave Origin"
    (mei, live). Plus a terminal window (omarchy herdrdrop).
  - So: the owner is active on ws2, mei is live in Brave, mochi's
    Chromium is live, and a leftover Pick 4 fixture window from the
    W-A1FIX probes is still open. Run 1 needs a handover plus a
    clean-desktop check at resume time. I made no focus or workspace
    change, closed nothing, navigated nothing.
- (4) Fixture md5s per run: MATCH at prep check on all three copies
  (VM repo, laptop repo, /tmp served dir). Read-only md5sum, about
  19:00 +07:
  - VM repo: pick4-fixture.html
    91b2f92945c167306a13ae32977a9bf3; test-01-spreadsheet.html (f01)
    2b6eda97036af51510b7eefe6d36dd93; test-06
    b989fe26ed497b24301467fd3ca38663; test-07
    be0eeafe893680f4ca47abfbfb9d5888; test-08
    7688f92ddad686fab9b0f456d13a51c6; test-09
    f8d286e522f11c0da4a7c27c2676946d; test-10
    6a819e3947b4beca6d334c78d9473b39.
  - Laptop repo: identical md5s for the same 7 files (f01 path
    tests/realistic/fcc-k/fixtures/test-01-spreadsheet.html; agy-q2
    fixtures under tests/realistic/agy-q2/fixtures/).
  - Laptop served dir /tmp/a1fix-20261122/fixtures/: identical md5s
    for the same 7 files.
  - All match the frozen values in FREEZE.md and the F5 log. The
    per-run re-verification (setup.json per run) is still owed at
    resume; this check does not replace it.
- (5) Re-probe under new-tab-only procedure: procedure READY, re-probe
  NOT RUN in this session. Evidence (read-only grep on the VM):
  - Driver tests/realistic/a1-pilot/run_preflight_probes.py, commit
    331523f: lines 71-76 and 157-162 record Ctrl+T as the first
    action of the navigate act, tab picked by id-diff (URL matches,
    id not in the before list), no second Ctrl+T on retry, operator
    closes ONLY the tabs it opened by tab id.
  - F4 CLOSED (coord log, W-F4FIX done 18:46 +07): probe 5 PASS live
    18:44:14-18:44:55 +07 (retry-logging 8591.8ms, all 5 probes PASS,
    driver exit 0, all_ok true), check_run cross-check PASS, adapter
    fix landed 658c432 (W-F4LAND, 7/7 suites green), runbook CB-2
    stamped (see below). The re-probe at resume is still owed
    because the probe dirs were wiped and the pilot needs a fresh
    pre-run re-probe; it was not run now because this session is
    prep-only and the owner is using the machine.
- (6) CB-2 amendment for template navigate act: DONE, verified by
  grep (read-only). Runbook tests/realistic/a1-pilot/runbook.md
  section 5 step 2, lines 114-123: bullet requires scope plus
  observation_id on EVERY act and dom_act, desktop act uses
  "scope": obs["scope"] and "observation_id": obs["id"], dom_act
  uses "scope": tab["id"] and "observation_id": snap["snapshot"],
  with a stamped literal navigate example; retry re-observes first
  and stamps from the fresh observe or snapshot. Commit a51cf9c.
  Preflight-probe.md P1 literals stamped too (commit 9aa7c85, 20/20
  actions stamped; grep shows scope plus observation_id on the P1
  navigate acts and dom_act calls).

## 6. Other read-only observations (no action taken)

- Chromium 9223 alive: /json/version returns Chrome/157.0.8103.38,
  Protocol 1.3. /json/list (read-only, about 19:00 +07): page "Pick
  4 DOM fixture" (http://127.0.0.1:8768/pick4-fixture.html), page
  "Chat - mochi" (https://muse.ai/) plus its Stripe iframes and
  service worker, plus Omnibox popups. No scratch tabs. Mochi's tab
  is intact. Nothing was closed or navigated.
- Fixture server still running on the laptop: python3 http.server
  port 8768, PID 45976, listening on 127.0.0.1:8768 (left running by
  W-A1FIX for a resume-time re-probe).
- F4 status (from the coord log, not re-derived): CLOSED. Probe 5
  PASS live, adapter fix landed 658c432, 7/7 node suites green,
  test_browser_worker.py 14 tests OK. A1 resume was unblocked for
  the relay verification step after W-F4LAND; that step is what
  this prep does.
- No live arm was run, no relay restart, no laptop sync, no file
  changed on the laptop, no tab or window touched, no focus or
  workspace change. All laptop commands were read-only (git
  rev-parse, git log, git status, systemctl show, cat drop-in,
  /proc environ read, session_remote.py status, hyprctl
  activeworkspace and clients, md5sum, curl /json/list and
  /json/version, ss listen check).

## 7. Verdict summary for COORD-CLICK-7

- Manifest F1: sha256 MATCHES (470df418...), 1599 bytes, 12 lines.
  Sealed, contents not read.
- Relay: flags BOTH PRESENT (CU_CODE_EXEC=1, CU_PICK4_FASTPATH=1),
  drop-in intact, broker SOLO and idle at check time. BUT
  started_git_head 4eb5917 is STALE against VM HEAD (c97d617 then
  d59c2b8 during this session) and laptop checkout HEAD 331523f.
  This BLOCKS run 1 until the F3 re-verification in section 3 runs
  at resume time (sync laptop to H2, restart relay, re-verify flags
  and head and idle state).
- Draft resume order: WRITTEN in section 4, filled with the current
  HEAD and relay status, marked DRAFT ONLY for Muse tong. W-A1PREP
  did NOT issue it.
- Preconditions before run 1: (1) relay: BLOCKED, head stale;
  (2) broker SOLO/idle: YES at check time, re-check at resume;
  (3) desktop: NOT clean (owner active on ws2, mei Brave live,
  mochi Chromium live, leftover Pick 4 fixture window), handover
  and clean check owed at resume; (4) fixture md5s: MATCH on all
  three copies, per-run re-verify still owed; (5) re-probe
  new-tab-only: procedure ready, F4 CLOSED, re-probe itself still
  owed at resume; (6) CB-2 amendment: DONE (runbook lines 114-123,
  commit a51cf9c).
- Other flags for the resume order: laptop tree is dirty
  (`M scripts/cdp.mjs` plus untracked files), so the sync step must
  check `git status --short` first; the dirty cdp.mjs diff is the
  F4 patch since landed as 658c432. HEAD moved during this prep
  (c97d617 to d59c2b8), so H2 must be read fresh at resume time.
- No H3 record written by W-A1PREP. No resume order issued by
  W-A1PREP. Awaiting COORD-CLICK-7 independent verification.
