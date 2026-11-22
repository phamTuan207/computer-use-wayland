# W-A1PREP2 log: prepare A1 pilot resume order, round 2 (prep only, no issue)

- Owner: the owner. Worker: W-A1PREP2, for COORD-CLICK-11 (live sequence step 3).
- Task received: 21:47:10 +07, 22/11/2026. Task: PREPARE the resume order only.
  W-A1PREP2 does NOT issue the resume order (only Muse tong issues it).
  W-A1PREP2 does NOT write any H3 record (only Muse tong writes it).
  W-A1PREP2 does NOT restart the relay, does NOT sync the laptop.
  Machine handed over (owner treo may 19:10, not at machine), machine quiet,
  single lane. Idle signals ignored throughout.
- Rules acknowledged: 18:23 (never close or navigate any tab or window
  the owner opened; open a new tab beside it if a browser is needed);
  18:30 (pill must show when any agent drives the machine; the re-probe
  runs inside real computer-use sessions whose guardian creates the pill
  and fails the session outright when the pill cannot appear, so all
  probe writes happen under a visible pill; no raw CDP writes in this
  session); no em dash (U+2014) or en dash (U+2013) anywhere in this file;
  no ydotool; no personal info on GitHub; explicit pathspec commits only
  (`git add -- <path>` then `git commit -m` with no pathspec argument,
  never `git commit -- <paths>`, never plain commit, never `git add -A`,
  never amend); no self-grading, COORD-CLICK-11 verifies independently.
- Evidence standard (Lauren Tan): every claim carries command, output,
  commit hash, and wall-clock time (Asia/Ho_Chi_Minh) with elapsed time.
- Sources read before work: improvements/w-a1prep-log.md (prep round 1,
  19:00 +07: manifest F1 sha 470df418..., relay head 4eb5917 STALE,
  broker idle, desktop not clean then, fixture md5s match, re-probe
  not run, draft resume order section 4);
  improvements/w-a1fix-f1f6-log.md (F1-F6).

## 0. Session start and HEAD movement observed

- 21:47:18 +07 (14:47:18 UTC), VM: `git rev-parse HEAD` returned
  9ee2289d5c67f3feb4af3eb399d9ddd7423015a7. Log line: "W-GPILL-RETRY:
  G-PILL retry PASS (run 6, sent, pill sight-verified live in 2 grims)".
- 21:49:18 +07, VM: `git rev-parse HEAD` returned
  f76c3035973fe11890d9e5362dbe24515683e5be.
- Fact: HEAD moved 9ee2289 to f76c303 DURING this prep session (another
  worker's commit). This proves again that HEAD moves with every log
  commit, so the relay re-verification at resume time is mandatory
  and must use the HEAD current at that moment (H2), not any HEAD
  recorded in this log.
- VM tree at 21:47:18 +07 (`git status --short`): modified
  improvements/c5-zenproof-runs/zen-tab.py, scripts/zen_dom.py,
  tests/realistic/clone1-batch3/results.json, tests/test_zen_dom.py,
  tests/test_zenproof2_fix.py (NOT mine, never added or committed)
  plus untracked improvements files from other workers (NOT mine).
  Only this log file is added and committed by W-A1PREP2.

## 1. Manifest F1 verification (hash and size only, contents NOT read)

- File: ~/workspace/a1fix-sealed/a1-manifest.jsonl (VM path
  /home/hatch/workspace/a1fix-sealed/a1-manifest.jsonl).
- Command (VM), 21:47:18 +07: `sha256sum
  ~/workspace/a1fix-sealed/a1-manifest.jsonl; stat -c '%s bytes' ...;
  wc -l ...`.
- Output: sha256
  470df41818c2ad5637c9429f32cace50cad18568eb6d2a1069ca1a1107d21bc7.
  Size 1599 bytes. Lines 12 (12 run-ids). Meta file
  a1-manifest.jsonl.meta.json exists, 153 bytes.
- Expected sha256 (from W-A1FIX log F1, W-A1PREP log section 1, and
  the task brief):
  470df41818c2ad5637c9429f32cace50cad18568eb6d2a1069ca1a1107d21bc7.
- Verdict: MATCH. Hash matches exactly, size 1599 bytes matches the
  sealed value, 12 lines match. The file contents were NOT read and
  are NOT reproduced here. The mapping stays sealed.
- Pool (from W-A1FIX log F1, not re-derived here): test-06, test-07,
  test-08, test-09, test-10, live-validated 5/5 in F2. Order: Case A
  pairs 1-3 then Case B pairs 1-3, stratified.

## 2. Relay re-verification at current HEAD, F3 procedure (read-only SSH)

- SSH route: ~/workspace/ssh-laptop.sh (read-only commands only, no
  restart, no sync, no write on the laptop).
- Relay unit: computer-use-relay.service (user service). Drop-in:
  /home/james/.config/systemd/user/computer-use-relay.service.d/flags.conf.
- Command (laptop, over SSH), about 21:47 +07:
  `cd /home/james/computer-use-wayland && git rev-parse HEAD &&
  git log --oneline -1 && git status --short | head -20`,
  then `systemctl --user show computer-use-relay.service -p MainPID
  -p ActiveState -p Environment`, then `tr '\0' '\n' <
  /proc/$PID/environ | grep -E 'CU_CODE_EXEC|CU_PICK4_FASTPATH'`,
  then `cat` the drop-in, then `python3
  /home/james/computer-use-wayland/scripts/session_remote.py status`.
- Output, laptop checkout:
  - HEAD 8b0b32d56da168b165dc9fa20b307b5d55319df7. Log line:
    "COORD-CLICK-10: ZT-B run 3 FAIL verified, sequence STOPPED at step 1".
  - `git status --short` (laptop): only untracked files
    (cf26-polygon-upload-lessons-20261120.md,
    latency-probe-20261120-results.csv,
    latency-probe2-20261120-results.csv, live-a2t-20261120/,
    live-a4r-20261120/). The `M scripts/cdp.mjs` dirty entry from
    prep round 1 is GONE: the laptop tree is clean apart from
    untracked files, so the sync step at resume should fast-forward
    without a dirty-tree block. I did not touch the laptop tree.
- Output, relay:
  - ActiveState=active, MainPID=70985 (same PID as the F3 restart at
    18:32:03 +07; the relay has NOT restarted since F3).
  - Environment=PYTHONDONTWRITEBYTECODE=1
    XDG_CACHE_HOME=/home/james/.cache CU_CODE_EXEC=1
    CU_PICK4_FASTPATH=1. Both flags present.
  - /proc/70985/environ: CU_CODE_EXEC=1, CU_PICK4_FASTPATH=1. Both
    flags present in the live relay process env.
  - Drop-in flags.conf (verified by cat): [Service],
    Environment=CU_CODE_EXEC=1, Environment=CU_PICK4_FASTPATH=1.
    The drop-in persists across restarts.
- Output, broker status (same SSH call, about 21:47 +07):
  {"ok":true,"broker":"running","broker_generation":
  "8624ae4023d6dc0d1ea2b6a45b64ef93","loaded_code_sha256":
  "d490f369f6b754d200518055025ef956284a759cc49e3ee70ed6b2a4483e3da4",
  "started_git_head":"4eb591764c7ac5741c7ef34c5102ab387c54c284",
  "state":"finished","owner":"s2-flip-run6","generation":
  "2c69261582def25ba8936413d09f2f8d","driver":"stopped","guardian":
  "clean","cancelled":false,"cancellation_state":"clear",
  "recovery":"none","next_sequence":3,"active_sequence":null,
  "last_start_error":"cleanup_failed","last_status_error":null,
  "error":"cleanup_failed","stop_reason":"explicit_finish"}.
- Comparison:
  - started_git_head of relay: 4eb591764c7ac5741c7ef34c5102ab387c54c284
    (short 4eb5917, the F3 verification HEAD).
  - VM HEAD at check time: 9ee2289 (21:47:18), then f76c303 (21:49:18).
  - Laptop checkout HEAD: 8b0b32d.
  - MATCH: NO. The relay head 4eb5917 equals NEITHER the VM HEAD NOR
    the laptop checkout HEAD. It is stale by every commit since F3.
  - Flags: YES, both present (unit env and live process env and
    drop-in).
  - Broker state: state "finished" (not "idle"), owner "s2-flip-run6"
    (stale owner from the last finished session), driver stopped,
    guardian clean, active_sequence null, next_sequence 3. No active
    session: SOLO and idle in effect. The error field reads
    cleanup_failed (last_start_error): a stale marker from the last
    session end, the same marker W-A1FIX noted at 18:27, not a live
    session. The broker generation 8624ae40 is unchanged since the
    F3 restart.
- Verdict: relay flags OK, broker SOLO with no active session, BUT
  started_git_head is STALE. Resume is BLOCKED on the F3
  re-verification step until the laptop is synced to the resume-time
  HEAD (H2) and the relay is restarted and re-verified. I did NOT
  restart the relay, did NOT sync the laptop tree, and did NOT run
  any live pilot arm, per the brief.

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
- Change since prep round 1: the laptop tree is now clean apart from
  untracked files (the `M scripts/cdp.mjs` dirty entry is gone), so
  the sync step should fast-forward without a dirty-tree block. The
  sync step must still check `git status --short` on the laptop
  before the pull, because a tree can go dirty again between prep
  and resume.
- Broker idle check immediately before the restart is part of the F3
  procedure (no active sequence, so the restart kills no live
  session). At check time the broker has NO active session (section
  2), but the check must be repeated immediately before the restart
  at resume time. Note: the broker state reads "finished" with a
  stale owner and a stale cleanup_failed marker, not "idle"; the
  resume check should accept state finished with driver stopped and
  active_sequence null as idle in effect, and should confirm the
  cleanup_failed marker is gone after the restart (both error fields
  null, as after the F3 restart at 18:32:06 +07).

## 4. Draft resume order, filled with current HEAD and relay status (DRAFT ONLY)

- This is a DRAFT prepared by W-A1PREP2 21:50 +07 22/11/2026 for Muse
  tong to issue. W-A1PREP2 does NOT issue it. Only Muse tong issues
  the resume order, with a timestamp, after the relay re-verification
  in section 3 is done and passes.
- ---
- RESUME ORDER (draft, prepared by W-A1PREP2 21:50 +07 22/11/2026,
  for Muse tong to issue)
- Manifest: ~/workspace/a1fix-sealed/a1-manifest.jsonl, sha256
  470df41818c2ad5637c9429f32cace50cad18568eb6d2a1069ca1a1107d21bc7,
  1599 bytes, 12 lines. Verified MATCH by W-A1PREP2 21:47:18 +07
  (hash and size only, contents not read). Muse reads the sealed
  file and issues the 12 run-ids one at a time, in file order
  (Case A pairs 1-3, then Case B pairs 1-3).
- Relay status at prep time (21:47 +07): flags CU_CODE_EXEC=1 and
  CU_PICK4_FASTPATH=1 present (unit env, live process env PID 70985,
  drop-in). Broker has no active session (state finished, owner
  s2-flip-run6 stale, driver stopped, active_sequence null).
  started_git_head 4eb5917 is STALE: VM HEAD was 9ee2289 at 21:47:18
  and f76c303 at 21:49:18, laptop checkout HEAD 8b0b32d. The resume
  MUST run the F3 re-verification sequence in section 3 of the
  W-A1PREP2 log first (sync laptop to H2, restart relay, verify both
  flags =1 in the live process env, verify started_git_head equals
  H2, no active session). Only then issue run 1.
  Do NOT reuse the HEAD values in this draft: HEAD moves with every
  log commit, so H2 is whatever `git rev-parse HEAD` returns at
  resume time.
- Preconditions before run 1: (1) relay restarted with
  CU_CODE_EXEC=1 and CU_PICK4_FASTPATH=1 and started_git_head
  equal to the repo HEAD at that time (F3, re-verified at resume,
  see above); (2) broker SOLO and idle per session_remote.py status,
  saved per run (no active session at prep check 21:47 +07,
  re-check at resume); (3) desktop verified clean (hyprctl
  activeworkspace plus clients), Zen untouched, Chromium only,
  workspace 2 (NOT clean at prep check, see section 5; the
  re-probe left 5 new probe tabs open plus the older W-A1FIX probe
  tab, and mei Brave plus mochi Chromium are live; a clean-desktop
  decision is owed at resume); (4) fixture md5s re-verified per run
  and recorded in setup.json (pick4
  91b2f92945c167306a13ae32977a9bf3, f01
  2b6eda97036af51510b7eefe6d36dd93; all matched at prep check, see
  section 5); (5) preflight probes re-run under the new-tab-only
  procedure (driver run_preflight_probes.py; F4 CLOSED, probe 5 PASS
  live in the re-probe 21:48 +07, see section 6; the re-probe is
  DONE in this prep session, 5/5 PASS, exit 0); (6) runbook template
  navigate act stamped with scope and observation_id (done, commit
  a51cf9c, verified by grep in prep round 1, see section 5 of the
  W-A1PREP log).
- Between runs: fresh browser session, storage cleared, fixture
  reloaded, desktop verified clean, each reset logged in
  setup-log.jsonl.
- After run 12: broker-status and desktop checks again (F6
  procedure), then unblinding from the run_start timestamps.
- ---

## 5. Preconditions before run 1, current status

- (1) Relay flags + head: flags OK, head STALE. BLOCKS run 1 until
  section 3 is done at resume time. Evidence in section 2.
- (2) Broker SOLO and idle in effect: YES at check time, about
  21:47 +07. session_remote.py status: state finished, owner
  s2-flip-run6 (stale), generation 2c692615, driver stopped,
  guardian clean, active_sequence null, next_sequence 3, broker
  generation 8624ae40 (same as the F3 restart), last_status_error
  null. The error field reads cleanup_failed (last_start_error):
  a stale marker from the last session end, not a live session.
  No active session. Re-check and save per run at resume (a
  snapshot now does not prove idle at run 1). Same reading after
  the re-probe (21:49 +07, section 6).
- (3) Desktop clean: NO, not clean at check time. Read-only hyprctl
  over SSH (HYPRLAND_INSTANCE_SIGNATURE set from
  /run/user/1000/hypr/, the known non-interactive SSH quirk),
  about 21:47 +07:
  - Active workspace: 1 (ws1), 2 windows, last window
    0x56307e2771d0 "Lich Google - Tuan 16 thang 11, 2026 - Zen Browser".
  - Clients: Zen "Lich Google - Tuan 16 thang 11, 2026 - Zen Browser"
    (ws1, untouched); Chromium "Pick 4 DOM fixture - Chromium"
    (0x56307e202df0, ws2, the leftover W-A1FIX probe tab window,
    same address as in prep round 1); Chromium "Chat - mochi -
    Chromium" (0x56307e7d9bb0, ws2, mochi's chat, live); Brave
    "Muse - Brave Origin" (0x56307e4c2f90, ws2, mei, live); OmaCal
    (ws1); plus a terminal window (omarchy herdrdrop, special
    workspace).
  - So: the owner handed the machine over and is not at it, but mei
    is live in Brave, mochi's Chromium is live, and a leftover Pick
    4 fixture window from the W-A1FIX probes is still open. Run 1
    needs a clean-desktop decision at resume time. I made no focus
    or workspace change, closed nothing, navigated nothing during
    the checks. The re-probe later focused the Chromium window as
    harness setup (driver focus step) and left the active workspace
    on ws2; see section 6.
- (4) Fixture md5s per run: MATCH at prep check on all three copies
  (VM repo, laptop repo, /tmp served dir). Read-only md5sum, about
  21:47 +07:
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
  - Fixture server still running on the laptop: python3 http.server
    port 8768, PID 45976, listening on 127.0.0.1:8768 (left running
    by W-A1FIX for a resume-time re-probe).
- (5) Re-probe under new-tab-only procedure: DONE in this session,
  5/5 PASS. Evidence in section 6.
- (6) CB-2 amendment for template navigate act: DONE, verified by
  grep in prep round 1 (runbook tests/realistic/a1-pilot/runbook.md
  section 5 step 2, lines 114-123, commit a51cf9c). Not re-checked
  here; no runbook change was made since.

## 6. Re-probe, new-tab-only procedure (RUN, 5/5 PASS)

- Helper pre-check (REQUIRED by the brief, before running): the
  /tmp helpers on the laptop were PRESENT, so no restore was needed.
  Command (laptop, over SSH), about 21:47 +07: `ls -l` plus
  `sha256sum` of /tmp/c5-activate.mjs, /tmp/c5-count.mjs,
  /tmp/s2-v12.mjs, /tmp/s2-p9.mjs.
  - /tmp/c5-activate.mjs, 2473 bytes, mtime 21:42 +07, sha256
    74af25d2f9b8bae1f7f5154ac9d974e1bc5316247a564768cd44d6571dff1d70.
  - /tmp/c5-count.mjs, 1983 bytes, mtime 21:42 +07, sha256
    d0f4e25464395544504200bff9d0edf79c73e221f7fdbc4297c61c168606d80d.
  - /tmp/s2-v12.mjs, 2658 bytes, mtime 21:42 +07, sha256
    dd588e8417a35a6a33dda01cd315eaf83f395fdb61a9f8fc5ebdebb278b1a473.
  - /tmp/s2-p9.mjs, 1229 bytes, mtime 21:42 +07, sha256
    b39829e12b139d6fe4c2f803a356f6789bf90b4515e92c0f69184aa586580f4b.
  - All four present with a 21:42 mtime (freshly present, after the
    W-GPILL-RETRY finding that they went missing between runs).
    Persistent copies also exist under /home/james/c5-step8-run/,
    /home/james/c5-step9-run/ and /home/james/c5-rung2-run/ (found
    by find, not restored from, not compared by hash: the /tmp
    copies were present, so no restore was needed).
  - Note: the preflight probe driver itself does not call these
    four helpers; the check was done as ordered because
    W-GPILL-RETRY found them missing between runs, and a missing
    helper would have stopped the run. They were present, so the
    run proceeded.
- Driver: tests/realistic/a1-pilot/run_preflight_probes.py, md5
  6e764940641b5c338e17654bf2ba3a34 on BOTH the VM repo and the laptop
  repo (verified before the run). F4 CLOSED procedure: new-tab-only
  (Ctrl+T first action of the navigate act, tab picked by id-diff,
  no second Ctrl+T on retry, operator closes ONLY tabs it opened
  by tab id). Pill: every probe runs inside a real computer-use
  session (cu.py session plus session-driver relay); the session
  guardian creates the indicator pill before the driver starts and
  fails the session outright when the pill cannot appear, so all
  browser writes inside a probe happen under a visible pill. No
  raw CDP writes in this session.
- Command (VM), 21:48:07 +07: `python3
  tests/realistic/a1-pilot/run_preflight_probes.py --out
  /tmp/a1fix-preflight`. Finished 21:48:54 +07. Wall time 46.9s.
  Exit 0. Summary all_ok true.
- Results, all times +07 22/11/2026 (per-probe wall from the driver
  summary; the submit `ts` fields in the log read 14:48:xx+07:00,
  which is the VM clock, UTC, mislabeled +07:00 by the driver:
  true wall is 21:48, from the exec timing, not the ts label):
  - click, probe_ms 8797.0: P1 ok false, error "ref is not present
    in the bound snapshot; observe again" (expected bad-ref),
    navigate act ok True, new tab 8C2B463CBE7BE67680140CAF8E20A07D;
    P2 ok true, "#result still not clicked yet", same tab true,
    verify image
    /home/james/.cache/agent-computer-use/4299a4741de8.jpg. PASS.
  - fill, probe_ms 8878.1: P1 ok false, same bad-ref error,
    navigate act ok True, new tab 2BD0A28B3368EA445064D7EDC5AC147F;
    P2 ok true, "#a2 still -", same tab true, verify image
    /home/james/.cache/agent-computer-use/cc519ab55118.jpg. PASS.
  - set_value, probe_ms 8856.8: P1 ok false, same bad-ref error,
    navigate act ok True, new tab 970FC935D479B0A94F6FF1812D0CA028;
    P2 ok true, "#a2 still -", same tab true, verify image
    /home/james/.cache/agent-computer-use/6e56c3716dc8.jpg. PASS.
  - assert, probe_ms 8822.8: P1 ok false, same bad-ref error,
    navigate act ok True, new tab 07DA26A3E50478EE1EFA413FE528032F;
    P2 ok true, "#result still not clicked yet", same tab true,
    verify image
    /home/james/.cache/agent-computer-use/1b9e09a3f4be.jpg. PASS.
  - retry-logging, probe_ms 10781.8: P1 ok true, retry_logged true:
    "first dom_act ok False completed 0", "retry dom_act ok True
    completed 1", "retry confirmed pick4-ok", new tab
    DF2C789E5A81598D528014A1C647A246; P2 ok true, "#result contains
    pick4-ok", same tab true, verify image
    /home/james/.cache/agent-computer-use/ea107ed1327a.jpg. PASS.
- Verdict: 5/5 PASS, all_ok true, driver exit 0. Probe 5 now PASSES
  live: the in-program retry after a failed dom_act works, which
  proves the F4 adapter fix (landed 658c432, W-F4LAND, 7/7 suites
  green) live. This is the first clean full re-probe since the
  F4 fix: the 18:44 +07 F4FIX run was the fix verification, this
  21:48 +07 run is the fresh pre-run re-probe for the resume.
- Probe dirs written on the laptop (verified 21:49 +07):
  /tmp/a1-pilot-20261121/runs/preflight/probe-1-click,
  probe-2-fill, probe-3-set-value, probe-4-assert,
  probe-5-retry-logging, each with end-state.json, run-log.jsonl
  and verify.png, all rewritten 21:48 +07. preflight-log.jsonl
  has 20 lines (10 from the 18:44 +07 F4FIX run, 10 from this run).
  End states read back: probe-1 {"result_text": "not clicked yet"},
  probe-2 {"a2": "-"}, probe-3 {"a2": "-"}, probe-4
  {"result_text": "not clicked yet"}, probe-5 {"result_text":
  "pick4-ok hello stranger"}. Every probe dir run-log.jsonl ends
  with verdict pass.
- Post re-probe tab check (read-only /json/list, 21:49 +07): 7 page
  tabs. The 5 new probe tabs (8C2B463C, 2BD0A28B, 970FC935, 07DA26A3,
  DF2C789E) plus the older W-A1FIX probe tab 025266AE (Pick 4
  fixture) plus mochi's chat tab A67A718D (https://muse.ai/).
  NO pre-existing tab was navigated or closed: mochi's chat tab is
  intact, the older probe tab is intact. The 5 new probe tabs were
  left open (the driver does not close tabs; closing via
  /json/close is banned since the 18:11:22 +07 Chromium scope end).
  The resume order must decide what to do with these 6 fixture
  tabs before run 1; W-A1PREP2 did not close any of them.
- Post re-probe desktop check (read-only hyprctl, 21:49 +07):
  active workspace is now 2 (the driver focused the Chromium
  window 0x56307e202df0 as harness setup before each probe).
  Clients unchanged otherwise: Zen ws1, Chromium ws2 (Pick 4
  fixture + mochi chat), Brave ws2 (mei), OmaCal ws1, terminal
  herdrdrop. I did not switch the workspace back; the resume
  clean-desktop check will set the workspace it needs.
- Post re-probe broker check (21:49 +07): same as section 2
  (generation 8624ae40, state finished, owner s2-flip-run6 stale,
  driver stopped, active_sequence null, cleanup_failed stale
  marker). No active session. The re-probe sessions all ended
  cleanly.
- Chromium 9223 alive throughout: Chrome/157.0.8103.38, Protocol
  1.3, still answering after the run. No Chromium restart.

## 7. Other read-only observations (no action taken)

- VM HEAD moved twice during this session: 9ee2289 at 21:47:18 to
  f76c303 at 21:49:18 (another worker's commit). Laptop checkout
  HEAD 8b0b32d is neither. The relay head 4eb5917 is stale against
  all three.
- No live pilot arm was run, no relay restart, no laptop sync, no
  file changed on the laptop, no tab or window of the owner was
  closed or navigated, no workspace change made by me except the
  driver focus step (harness setup, Chromium window only).
  All laptop commands except the re-probe driver were read-only
  (git rev-parse, git log, git status, systemctl show, cat
  drop-in, /proc environ read, session_remote.py status, hyprctl
  activeworkspace and clients, md5sum, sha256sum, curl /json/list
  and /json/version, ss listen check).

## 8. Verdict summary for COORD-CLICK-11

- Manifest F1: sha256 MATCHES (470df418...), 1599 bytes, 12 lines.
  Sealed, contents not read.
- Relay: flags BOTH PRESENT (CU_CODE_EXEC=1, CU_PICK4_FASTPATH=1),
  drop-in intact, broker has NO active session at check time. BUT
  started_git_head 4eb5917 is STALE against VM HEAD (9ee2289 then
  f76c303 during this session) and laptop checkout HEAD 8b0b32d.
  This BLOCKS run 1 until the F3 re-verification in section 3 runs
  at resume time (sync laptop to H2, restart relay, re-verify flags
  and head and idle state).
- Draft resume order: WRITTEN in section 4, filled with the current
  HEAD and relay status, marked DRAFT ONLY for Muse tong. W-A1PREP2
  did NOT issue it.
- Preconditions before run 1: (1) relay: BLOCKED, head stale;
  (2) broker SOLO/no active session: YES at check time, re-check at
  resume; (3) desktop: NOT clean (mei Brave live, mochi Chromium
  live, leftover W-A1FIX probe tab, plus 5 new re-probe tabs left
  open), clean-desktop decision owed at resume; (4) fixture md5s:
  MATCH on all three copies, per-run re-verify still owed;
  (5) re-probe new-tab-only: DONE, 5/5 PASS, exit 0, wall 46.9s,
  probe 5 retry now works live (F4 fix proven); (6) CB-2 amendment:
  DONE (runbook lines 114-123, commit a51cf9c, per prep round 1).
- New flags for the resume order: laptop tree is now clean apart
  from untracked files (the `M scripts/cdp.mjs` dirty entry from
  prep round 1 is gone), so the sync step should fast-forward
  cleanly; HEAD moved during this prep (9ee2289 to f76c303), so H2
  must be read fresh at resume time; the broker state reads
  "finished" with a stale owner and cleanup_failed marker, not
  "idle", so the resume idle check must accept finished plus driver
  stopped plus active_sequence null, and must confirm the marker
  clears after the restart; the 6 fixture tabs now open in
  Chromium need a disposition before run 1.
- No H3 record written by W-A1PREP2. No resume order issued by
  W-A1PREP2. Awaiting COORD-CLICK-11 independent verification.
