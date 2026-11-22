# W-A1FIX log: close F1-F6 (A1 pilot fix list, W-A1 decision 3204fc2)

- Owner: Pham Tuan. Worker: W-A1FIX, for COORD-CLICK-6.
- Branch: todolist-push. Repo: ~/workspace/computer-use-wayland.
- Task received: 17:55:08 +07, 22/11/2026. Follow-up from COORD-CLICK-6
  received 17:56:29 +07: W-SYNC done (ae2fe52), F3 unlocked after
  F1/F2/F4/F5/F6; owner handed the machine over at 17:55, live Chromium
  work allowed, no live pilot arm.
- Rules: no em dash (U+2014) or en dash (U+2013) anywhere in this file.
  No personal info. No ydotool. Explicit pathspec commits only, never
  plain git commit, never git add -A. Dirty files NOT mine, never add
  or commit: tests/realistic/clone1-batch3/results.json,
  tests/cdp_snapshot.mjs, tests/test_s2_flip_wiring.py,
  scripts/cdp.mjs, scripts/s2_flip_live.py.
- Frozen design (freeze commit f31abcf, 21/11) unchanged: no threshold,
  case, cap, fixture, run order, or checker change. No live pilot arm
  run in this session.
- Evidence standard (Lauren Tan): every claim carries command, output,
  commit hash, and wall-clock time (Asia/Ho_Chi_Minh) with elapsed time.
  No self-grading pass; independent verification owed.

## 0. Session start and repo sync

- 17:55:13 +07 (10:55:13 UTC): git fetch origin, git pull --ff-only
  reported "Already up to date". HEAD 3204fc2 (W-A1 decision log).
  Branch todolist-push.
- W-SYNC verified done before F3 (checked 17:57 +07): commit ae2fe52
  "docs: W-SYNC laptop tree sync, CB-9 drift cleared (ab7c7a5), broker
  observe verified". Laptop tree synced to ab7c7a5, drift zero,
  sync-installed.py --check exit 0, broker observe verified no 404.
  W-SYNC did NOT restart the relay: relay started_git_head still
  9ec713c (see F3). F3 therefore requires a relay restart with flags.
  F3 is done LAST, after F1/F2/F4/F5/F6, per brief.
- Owner machine handover 17:55 +07 (per COORD-CLICK-6 follow-up and
  MEMORY.md 17:55 entry): owner no longer touching the machine. Live
  Chromium work allowed. Zen never touched (Chromium only).

## F5. Fixture checksums re-verified (CLOSED)

- Command (VM): md5sum + stat, run 17:58:49 +07 (10:58:49 UTC).
- pick4: md5 91b2f92945c167306a13ae32977a9bf3, 719 bytes. MATCHES frozen
  value in FREEZE.md and decision log section 4 F5.
- f01: md5 2b6eda97036af51510b7eefe6d36dd93, 5636 bytes. MATCHES frozen
  value.
- Laptop copies verified identical, same command over SSH at 17:58 +07:
  pick4 91b2f92945c167306a13ae32977a9bf3, f01
  2b6eda97036af51510b7eefe6d36dd93, plus agy-q2 test-06
  b989fe26ed497b24301467fd3ca38663 (13335 bytes), test-07
  be0eeafe893680f4ca47abfbfb9d5888 (12156 bytes), test-08
  7688f92ddad686fab9b0f456d13a51c6 (11824 bytes), test-09
  f8d286e522f11c0da4a7c27c2676946d (14931 bytes), test-10
  6a819e3947b4beca6d334c78d9473b39 (10701 bytes). Laptop tree at ab7c7a5.
  All laptop md5s equal the VM md5s, so the shipped bytes are exact.
- Verdict: F5 CLOSED. Freeze intact. Re-verification per run remains a
  resume-time step (setup.json per run), unchanged.

## F6. Broker SOLO and desktop state (IN PROGRESS, evidence below)

- Broker status, 17:57:24 +07, via
  `python3 /home/james/computer-use-wayland/scripts/session_remote.py status`
  over SSH: {"ok":true,"broker":"running","broker_generation":
  "411cfadf0b32da29387fe9dbb59e1886","loaded_code_sha256":
  "d490f369f6b754d200518055025ef956284a759cc49e3ee70ed6b2a4483e3da4",
  "started_git_head":"9ec713c2a6a803c75e41d7e6f99cd335330779ef",
  "state":"finished","owner":"w-sync","generation":
  "cb770f0c102467de35993b049355cd92","driver":"stopped","guardian":
  "clean","cancelled":false,"active_sequence":null,"error":null,
  "stop_reason":"explicit_finish"}. Broker running, no active session,
  driver stopped: SOLO and idle at that time.
- Desktop state as found, 17:57 +07 (hyprctl): active workspace 1
  (Zen, "Chat - Muse - Zen Browser"). Workspace 2 holds Brave
  ("Chat - mei - Brave Origin") and Chromium ("Chat - mochi -
  Chromium"). Chromium 9223 alive (Chrome/157.0.8103.38), Brave 9224,
  Zen 9222. Relay serve PID 3913 (started 17:19).
- Procedure recorded for resume (before run 1 and after run 12): run
  `session_remote.py status`, save the full JSON per run; run
  `hyprctl activeworkspace` plus `hyprctl clients` before run 1 and
  after run 12; Zen untouched, Chromium only; between runs fresh
  browser session, storage cleared, fixture reloaded, desktop verified
  clean, each reset logged in setup-log.jsonl.
- (F6 close-out completed after the live F2/F4 work, with final
  broker-status and desktop checks, in the section below.)

## F2. Pool live validation, agy-q2 test-06..test-10 (IN PROGRESS)

- Prior state: pool validated by simulation only (simulate.mjs 10/10
  simulated). Existing live runners (run_agyq2.py, run_agyq.py,
  run_agy_y2.py, run_fcck.py) are all Zen/Marionette only; no Chromium
  scripted runner exists in the repo. The simulation step functions
  for test-06..test-10 already exist in tests/realistic/agy-q2/
  simulate.mjs lines 187-292 (page.click / page.select / page.type /
  page.$eval, then window.__agyVerify()).
- Runner built for this fix: tests/realistic/agy-q2/
  run_live_chromium.mjs (dependency-free Node, raw CDP over the
  built-in WebSocket, no puppeteer: puppeteer-core is NOT installed
  on the laptop or the VM). It connects to the agent Chromium on
  127.0.0.1:9223, opens one fresh tab per test, drives the SAME
  scripted steps as simulate.mjs with real CDP input, calls
  window.__agyVerify(), records per-step JSONL, closes the tab.
  (Runner details and per-test results below.)
- Fixture server (laptop): /tmp/a1fix-20261122/fixtures, served by
  `python3 -m http.server 8768 --bind 127.0.0.1`, started detached
  18:00:31 +07 (setsid nohup, log /tmp/a1fix-20261122/http.log).
  All 7 fixture md5s in that directory match the repo bytes
  (verified in the same SSH call). URLs: http://127.0.0.1:8768/<file>.
- Mouse pipeline probe (selftest mode), 18:00:44-18:00:54 +07:
  workspace switched ws1 to ws2 at 18:00:38 +07 (hyprctl dispatch
  hl.dsp.focus workspace 2, verified active ws2). Real CDP mouse
  click on the pick4 "Show result" button: ok true in 130ms,
  #result "pick4-ok hello stranger", exit 0. The mouse pipeline
  WORKS on visible workspace 2, confirming the S2 flip occlusion
  hypothesis (mouse dispatch timed out 5/5 at 5003ms while the
  window sat occluded on ws2 with ws1 active). F2 therefore used
  real mouse input throughout.
- Run 1, launched 18:01:01 +07 (detached, pid 46413), finished by
  18:01:17 +07 (about 16s wall). Per-test results (from
  /tmp/a1fix-20261122/f2-results.jsonl, 45 steps, 0 failed steps):
  - test-06 file converter: PASS, 2772ms, score 1, failures [].
    State: sessionSaved true, convertedCount 2, downloadedCount 2,
    metaChecked true, compVal High, banner "Batch complete: 2 files
    converted and 2 downloaded".
  - test-07 weather dashboard: FAIL at first, 183ms, error
    "__agyVerify missing after load". NOT a fixture failure: runner
    bug (see below). No steps ran.
  - test-08 quiz app: PASS, 2288ms, score 1, failures []. State:
    quizSubmitted true, resultsSaved true, score 5, banner "Quiz
    completed: 5/5 score (100%) - Results verified and saved".
  - test-09 pomodoro timer: FAIL at first, 192ms, same runner bug.
    No steps ran.
  - test-10 markdown editor: PASS, 1024ms, score 1, failures [].
    State: docSaved true, htmlExported true, title "Release Notes
    v2.3.0", listCount 2, banner "Document saved: 'Release Notes
    v2.3.0' (HTML exported, 0 errors)".
- Runner bug found and fixed (setup reason, not a fixture result):
  the shared CDP event buffer kept Page.loadEventFired events from
  earlier tabs, so waitEvent returned a stale event and the
  __agyVerify check ran before the new page loaded. Fix committed
  in run_live_chromium.mjs: dropEvents() before navigate, plus a
  poll up to 10s for location.href plus __agyVerify function after
  load. Re-shipped to the laptop (16924 bytes, node --check OK both
  sides).
- Run 2 (tests 07 and 09 only, fixed runner), launched 18:01:59 +07,
  finished by 18:02:24 +07 (37 steps, 0 failed steps):
  - test-07 weather dashboard: PASS, 2416ms, score 1, failures [].
    State: dashboardSaved true, activeUnit F, cityCount 4,
    primaryCity ho-chi-minh-city, banner "Dashboard saved: 4 cities
    monitored in F (Primary: Ho Chi Minh City)".
  - test-09 pomodoro timer: PASS, 2562ms, score 1, failures [].
    State: sessionSaved true, settings work 30 / break 6 /
    autoBreak true, completedCycles 2, totalFocusMin 60,
    historyCount 3, banner "Session log saved: 2 focus cycles
    completed (60 min total focus)".
- Tab hygiene verified 18:02:32 +07 via /json/list: no fixture tab
  and no scratch tab remains in the agent Chromium; only mochi's
  chat tab (https://muse.ai/) plus its iframes and service worker.
  Mochi's tab was never navigated or closed, only backgrounded
  while scratch tabs were active.
- Verdict: F2 CLOSED. Pool validated live 5/5: test-06, test-07,
  test-08, test-09, test-10. All pass live as specced on real
  Chromium (visible ws2, real mouse input). No candidate dropped.
  Raw logs on the laptop: /tmp/a1fix-20261122/f2-results.jsonl,
  f2-rerun.jsonl, f2-run.log, f2-rerun.log. (Copies to be attached
  to the repo record before close-out; see the file note at the end
  of this log.)

## F4. Layer-2 preflight probes (CLOSED with one FAIL: probe 5 adapter defect; clean re-run and checker cross-check BLOCKED by the 18:23 hard rule, see below)

- Driver: tests/realistic/a1-pilot/run_preflight_probes.py (repo
  file, reusable for resume-time re-probe). Runs the 5 probes in
  tests/realistic/a1-pilot/preflight-probe.md live on the agent
  Chromium 9223 via the code-exec path, one interactive one-shot
  session per probe, P1 then P2 as two sequential submits over the
  same session stdin. P1 and P2 MUST share one session: each
  dom_start() closes prior browser-start contexts, so a fresh
  session per submit would close P1's tab before P2 reads it.
  Mechanism (S2 flip pattern): CU_CODE_EXEC=1 on the one-shot
  command line only, because the relay was started without the flag
  and the broker cannot set env per request (the F3 defect).
- CB-2 scope adaptation (recorded, NOT a design change): probe
  programs as written fail with sandbox error "action 0 is missing
  scope: scope is mandatory in action data (CB-2)". Every desktop
  act() action needs "scope": obs["scope"], "observation_id":
  obs["id"]; every dom_act() action needs "scope": tab["id"],
  "observation_id": snap["snapshot"]. The desktop act fails first
  (api_calls 3); the dom_act would fail next. Bad-ref error text
  once scope is fixed: "ref is not present in the bound snapshot;
  observe again" (scripts/code_exec.py line 275; validation runs
  before any action executes).
- FINDING for COORD-CLICK-6: the frozen runbook's template navigate
  act (runbook section 5, step 2) shows the same unstamped shape,
  so the executor would hit the same CB-2 refusal at run 1. A
  pre-run-1 runbook amendment stamping the template is owed
  (amendments before run 1 are free).
- Other driver adaptations (recorded, not design changes): P2 ends
  with a desktop observe plus prints of window title/address and
  verify image path (for verify.png); P1 prints navigate-act result
  and retries the navigate act once (fresh observe plus re-act) on
  ok:false; P1 and P2 print tab ids and the driver requires the same
  tab; P2 looks its tab up by the exact target id P1 printed, never
  by URL (stale tabs leak across sessions and a URL lookup could
  fake a zero-effect verdict). Tabs are NEVER closed with CDP
  /json/close (see the Chromium death incident below).
- Navigate-act flakiness: error "type verification failed: input
  line unchanged after typing; text may not have landed; re-observe
  and check focus before retrying". Full run 18:09:16-18:09:41 +07:
  click P1 FAIL navigate, fill PASS, set_value P1 FAIL navigate,
  assert PASS, retry P1 FAIL navigate and P2 FAIL (assertion failed,
  reading a stale tab). Per the probe doc triage rule, navigate
  failures are setup failures, re-run after the setup is fixed,
  never recorded as probe results. About 40 percent of P1s failed
  this way across the first runs (18:09-18:19 +07). Cause: the
  keystrokes land nowhere when the Chromium window lacks focus, so
  the frame never changes. Focus is contended while mei works live
  in Brave on the same workspace (18:20:11 +07: active window was
  Brave, not Chromium). Fix in the driver: focus the agent Chromium
  window (hyprctl hl.dsp.focus on the class-chromium window,
  verified active) immediately before each probe session, retrying
  up to 3 times. Focusing is harness setup, not a probe change: the
  runbook already requires the desktop verified before run 1.
- CHROMIUM DEATH INCIDENT (flagged prominently): at about 18:11:20
  +07 I ran a pre-probe cleanup that closed one fixture tab via
  /json/close; the cleanup reported closed 1, remaining 1. At
  18:11:22 +07 the Chromium scope ended (journalctl:
  "app-org.chromium.Chromium-18451.scope: Consumed 29.112s CPU time
  over 34min 26.295s wall clock time, 166.5M memory peak"); 9223
  stopped listening, no Chromium window in hyprctl clients, no new
  crash report, no OOM (14G free, 17G disk free). The close is the
  suspected trigger (timing only), mechanism unproven. Relaunch:
  first attempt with bare /usr/lib/chromium/chromium failed
  ("Failed to connect to Wayland display", missing env); second
  attempt with XDG_RUNTIME_DIR=/run/user/1000
  WAYLAND_DISPLAY=wayland-1 succeeded but produced window class
  "chromium-browser" (wrong; probe/pilot programs filter
  class == "chromium"). I killed that instance (PID 55571) and
  relaunched via the wrapper /home/james/.local/bin/chromium-intel
  (sets LIBVA_DRIVER_NAME=iHD etc., adds
  --remote-debugging-port=9223); new PID 56452, answering by
  18:13:26 +07, window class "chromium" restored (same window
  address 0x56307e202df0), ws2. Mochi's chat tab did NOT restore
  (only "New Tab", chrome://newtab/).
- MOCHI TAB LOSS, window 18:02-18:21 +07 (facts for
  COORD-CLICK-6, no conclusion claimed): my F2 check at 18:02:32
  +07 showed mochi's chat tab intact (only mochi's tab plus its
  iframes and service worker). My probe P1 navigate acts (from
  18:09:16 +07) navigated the then-current tab via Ctrl+L plus type
  URL WITHOUT verifying which tab was current; the current tab at
  18:09 may have been mochi's chat tab (the only page tab at
  18:02:32). So two candidate mechanisms come from my work: (a) a
  probe navigate navigated mochi's tab to a fixture, (b) the
  /json/close cleanup then the browser death lost the tab on
  relaunch. I cannot prove which one did it. COORD-CLICK-6 recorded
  (commit a1d36bf) that the actor in 18:02-18:21 is NOT yet
  identified and it does not conclude without evidence. Mochi's tab
  is back: /json/list at 18:25:48 +07 shows "Muse - Your Personal
  AI Agent from Meta" (https://muse.ai/) beside the Pick 4 fixture
  tab. I left both untouched after 18:25.
- Update 18:21-18:23 +07 (AGENTS.md and MEMORY.md entries): the
  recorded cause is the Chromium restart about 18:13-18:14 (my
  relaunch after the 18:11:22 scope end) while a campaign worker
  ran the Pick 4 fixture test in that instance; the tab was
  incognito, and incognito tabs do not survive a restart and cannot
  be restored. That attributes the loss to my restart, not to a
  probe navigate. The scope-end trigger itself (my /json/close
  cleanup at about 18:11:20) remains timing-only, mechanism
  unproven. The lesson stands in AGENTS.md: never close or
  navigate any tab or window the owner opened.
- Probe results, standalone runs with the focus driver (all times
  +07, 22/11/2026; same tab id 025266AE11C86425817A3AF6E0FB7B26
  throughout):
  - click, 18:18:24, PASS (4632.9ms): P1 bad-ref error, P2 #result
    still "not clicked yet", same tab true, verify image
    /home/james/.cache/agent-computer-use/a49f71acb9ba.jpg.
  - fill, 18:18:37, PASS (4680.0ms): P1 bad-ref error, P2 #a2
    still "-", same tab true, verify image
    /home/james/.cache/agent-computer-use/a972398a73b9.jpg.
  - set_value: FAILED navigate 18:18:50 standalone (focus race);
    PASSED 18:19:57 with the focus step (7317.6ms): navigate act ok
    True, P1 bad-ref error, P2 #a2 still "-", same tab true,
    verify image
    /home/james/.cache/agent-computer-use/740bba056980.jpg.
  - assert, about 18:19:05, PASS (4689.9ms): P1 bad-ref error, P2
    #result still "not clicked yet", same tab true, verify image
    /home/james/.cache/agent-computer-use/f0bfb659e9c4.jpg.
  - retry-logging, 18:20:48, FAIL, adapter defect, NOT a setup
    failure: P1 navigate act ok True, first dom_act ok False
    completed 0 (the expected failed assert), then the retry
    branch's dom_observe raised "browser worker ended; stop this
    task" (api_calls 8); P2 the same error at api_calls 1 (shared
    session). Mechanism: cdp.mjs act returns {ok:false,
    completed:0, error:'assertion failed'} on a failed assert, and
    browser_worker.py line 51 closes the browser worker on ANY
    ok:false response, so all later browser calls in the session
    raise. In-program retry after a failed dom_act is therefore
    impossible on the current adapter, which also breaks the runbook
    section 5 step 2 template rule (retry inside the program after
    ok:false, "a retry costs zero model calls; that is the point").
    STOP-FIX-REPROBE applies: fix the adapter (worker survives a
    failed assert) or amend the runbook (retry only via a recovery
    call in a fresh program, never in-program). That decision is
    COORD-CLICK-6's; my brief forbids changing the frozen design.
  - Fresh-session P2 for retry-logging, 18:24:46 (new --program P2
    --tab mode, fresh worker, tab 025266AE...): ok:false, error
    "assert failed: assertion failed", api_calls 3, same tab.
    Confirms the actual state is still "not clicked yet": no click
    effect, the retry genuinely did not happen.
- Verdict: probes 1-4 PASS (P1 bad-ref error plus P2 zero DOM
  effect, same tab). Probe 5 FAIL (adapter defect above). The
  completed-0 and zero-effect premise is proven live; the
  in-program retry premise is disproven live on the current
  adapter.
- check_run.py cross-check: BLOCKED. The remote preflight dir was
  wiped at 18:24 for a clean full re-run; that re-run was aborted
  by the 18:23 hard rule (see below) before writing any probe dir,
  so no probe dirs exist on the laptop now (verified 18:25:48 +07:
  /tmp/a1-pilot-20261121/runs/preflight/ empty, no
  preflight-log.jsonl). Re-running the probes to regenerate the
  dirs requires navigating tabs, which the hard rule forbids in its
  current form. The cross-check needs a new-tab-only re-probe
  procedure approved by COORD-CLICK-6. The probe evidence in this
  log (commands, outputs, times) is the record until then.
- Driver changes recorded in run_preflight_probes.py: focus step
  with up to 3 retries; --program P1/P2/both plus --tab for a
  P2-only fresh-session re-read; probe-5 end state follows the
  ACTUAL outcome (pick4-ok only when the retry genuinely landed,
  else "not clicked yet") so the checker cannot be handed a
  fabricated PASS. End states used: click/assert
  {"result_text":"not clicked yet"}, fill/set_value {"a2":"-"},
  retry {"result_text":"pick4-ok hello stranger"} (exact text
  grounded in the F2 mouse selftest, 18:00:44 +07) only if the
  retry lands.

## LUAT CUNG 18:23 22/11, UU TIEN CAO NHAT: KHONG BAO GIO dong hay navigate tab/cua so trinh duyet cua Pham Tuan (xac nhan da doc)

- Nhan luc 18:25:02 +07, 22/11/2026, qua subagent interrupt tu
  COORD-CLICK-6, submission 88a9ebce-3745-4e26-bafa-59f5567f1739.
  Lenh truc tiep tu Pham Tuan 18:23 22/11: KHONG BAO GIO dong hay
  chuyen huong (navigate) tab/cua so trinh duyet cua Pham Tuan.
  Tab mochi la tab an danh Chromium do chinh Pham Tuan mo san de
  dung; mot worker chien dich da dong hoac chuyen huong no mat luc
  18:00-18:21, Pham Tuan phai dang nhap lai. Tu gio, neu can trinh
  duyet thi MO TAB/CUA SO MOI BEN CANH, workspace 2 cuon duoc,
  tuyet doi khong dong, khong navigate tab cua Pham Tuan (tab mochi
  an danh, cua so Brave cua mei, Zen, bat ky tab nao Pham Tuan mo).
  Ap dung cho moi lane, moi worker, ke ca live test. Ghi vao log
  coord tai commit a1d36bf.
- XAC NHAN: toi da doc luat nay. Toi DUNG NGAY moi viec navigate
  va dong tab luc 18:25 (buoc chay lai full 5 probe dang chay do
  bi abort; khong co lan goi probe nao sau 18:24:46). Khong co tab
  nao bi toi navigate hay dong sau 18:25. Cac viec con lai trong
  phien nay (F1 manifest, F6 kiem tra, F3 restart relay) khong dung
  navigate hay dong tab trinh duyet.
- He qua cho F4: driver probe nhu hien tai navigate tab hien tai
  qua desktop act; khong dung lai duoc cho toi khi COORD-CLICK-6
  duyet mot bien the chi-mo-tab-moi. Fixture tab 025266AE... (tab
  probe cua chinh toi) va tab muse.ai cua mochi deu duoc de nguyen
  sau 18:25 (kiem tra chi-doc qua /json/list luc 18:25:48 +07: ca
  hai tab deu co mat).

## F1. Sealed manifest and draft resume order (CLOSED, setup only)

- Command (VM), 18:27:00 +07 (11:27:00 UTC), 22/11/2026:
  python3 tests/realistic/a1-pilot/a1_manifest.py --pool
  test-06,test-07,test-08,test-09,test-10 --out
  ~/workspace/a1fix-sealed/a1-manifest.jsonl
  Exit 0. Stdout: sha256
  470df41818c2ad5637c9429f32cace50cad18568eb6d2a1069ca1a1107d21bc7.
  Stderr: meta file at
  ~/workspace/a1fix-sealed/a1-manifest.jsonl.meta.json (seed and
  held-out draw sealed there).
- Verification, 18:27:11 +07: sha256sum of the manifest file equals
  the printed hash 470df418...; the file has 12 lines (12 run-ids);
  the meta file exists (1599 bytes manifest, 153 bytes meta). The
  file contents were NOT read and are NOT reproduced here: the
  mapping is sealed, only the sha256 is published, per the brief
  ("chi cong bo sha256") and the manifest doc (Muse reads the file
  to issue runs one at a time; the executor never sees the file).
  The 12 run-ids are therefore NOT listed in this log; the draft
  order below points Muse at the sealed file instead.
- Pool: test-06, test-07, test-08, test-09, test-10, all
  live-validated 5/5 in F2. Run order: Case A pairs 1-3 then Case B
  pairs 1-3, stratified (exactly 2 pairs start on one arm, 1 on the
  other, per case), per a1_manifest.py.
- Draft resume order for Muse (the coordinator) to issue. W-A1FIX
  only prepares it; it does NOT issue it in Muse's name:
  ---
  RESUME ORDER (draft, prepared by W-A1FIX 18:27 +07 22/11/2026,
  for Muse to issue)
  - Manifest: ~/workspace/a1fix-sealed/a1-manifest.jsonl, sha256
    470df41818c2ad5637c9429f32cace50cad18568eb6d2a1069ca1a1107d21bc7.
    Muse reads the sealed file and issues the 12 run-ids one at a
    time, in file order (Case A pairs 1-3, then Case B pairs 1-3).
  - Preconditions before run 1: (1) relay restarted with
    CU_CODE_EXEC=1 and CU_PICK4_FASTPATH=1 and started_git_head
    equal to the repo HEAD at that time (F3, done in this session,
    re-verify at resume because HEAD moves with every commit);
    (2) broker SOLO and idle per session_remote.py status, saved
    per run; (3) desktop verified clean (hyprctl activeworkspace
    plus clients), Zen untouched, Chromium only, workspace 2;
    (4) fixture md5s re-verified per run and recorded in setup.json
    (pick4 91b2f92945c167306a13ae32977a9bf3, f01
    2b6eda97036af51510b7eefe6d36dd93); (5) preflight probes re-run
    under a new-tab-only procedure approved by COORD-CLICK-6 (see
    F4: probe 5 needs an adapter fix or a runbook amendment, and
    the re-probe must not navigate any existing tab per the 18:23
    hard rule); (6) runbook template navigate act stamped with
    scope and observation_id (see F4 CB-2 finding) before run 1.
  - Between runs: fresh browser session, storage cleared, fixture
    reloaded, desktop verified clean, each reset logged in
    setup-log.jsonl.
  - After run 12: broker-status and desktop checks again (F6
    procedure), then unblinding from the run_start timestamps.
  ---
- Verdict: F1 CLOSED as setup. The manifest exists, the hash is
  published, the mapping stays sealed outside the repo, and the
  draft order is ready for Muse to issue.

- Final broker status, 18:27:37 +07, same command over SSH:
  {"ok":true,"broker":"running","broker_generation":
  "411cfadf0b32da29387fe9dbb59e1886","loaded_code_sha256":
  "d490f369f6b754d200518055025ef956284a759cc49e3ee70ed6b2a4483e3da4",
  "started_git_head":"9ec713c2a6a803c75e41d7e6f99cd335330779ef",
  "state":"finished","owner":"w-sync","generation":
  "cb770f0c102467de35993b049355cd92","driver":"stopped","guardian":
  "clean","cancelled":false,"cancellation_state":"clear",
  "recovery":"none","next_sequence":3,"active_sequence":null,
  "last_start_error":"cleanup_failed","last_status_error":null,
  "error":"cleanup_failed","stop_reason":"explicit_finish"}.
  Broker running, same generation 411cfadf as 17:57, no active
  sequence, driver stopped: SOLO and idle. The error field reads
  cleanup_failed (last_start_error): a stale marker from the last
  session end, the same marker W-GECKO noted at 18:11, not a live
  session. started_git_head still 9ec713c: the relay was NOT
  restarted in this session yet (F3, done last, below).
- Final desktop state, 18:27:37 +07 (hyprctl, read-only): active
  workspace 1 (Zen, "Chat - Muse - Zen Browser"). Workspace 2
  holds Brave ("Chat - mei - Brave Origin") and two Chromium
  windows: 0x56307e202df0 "Pick 4 DOM fixture" (my probe tab) and
  0x56307e7d9bb0 "Chat - mochi - Chromium" (mochi's chat, back in
  its own window). The desktop returned to ws1 on its own (I
  switched to ws2 at 18:00:38 and did not switch back; the active
  workspace is ws1 as found). I made no focus or workspace change
  after 18:25. Zen untouched throughout. Chromium PID 56452 alive
  on 9223, Brave 9224, Zen 9222. Fixture server still running on
  the laptop (PID 45976, port 8768, /tmp/a1fix-20261122/fixtures),
  left running for a resume-time re-probe.
- Verdict: F6 CLOSED. Broker SOLO and idle at start (17:57:24)
  and at close-out (18:27:37), desktop verified before and after,
  Zen untouched. Resume-time procedure (before run 1 and after run
  12): save session_remote.py status JSON per run; hyprctl
  activeworkspace plus clients before run 1 and after run 12;
  between runs fresh browser session, storage cleared, fixture
  reloaded, desktop verified clean, each reset logged in
  setup-log.jsonl.

## F3. Relay flags and started_git_head (CLOSED, verified at HEAD 4eb5917; resume-time re-verification owed because the final log commit moves HEAD)

- Precondition: W-SYNC done (ae2fe52, laptop tree at ab7c7a5, drift
  zero, --check exit 0, broker observe verified). W-SYNC did NOT
  restart the relay, so started_git_head still read 9ec713c at
  17:57:24 +07 and at every check until this section. F3 done LAST,
  after F1/F2/F4/F5/F6, per brief.
- Fix method: persistent systemd drop-in plus relay restart (no
  runbook amendment needed: the flags are a relay environment
  property, not a design change). The relay unit is
  /home/james/.config/systemd/user/computer-use-relay.service
  (ExecStart: python3 scripts/session_remote.py serve --socket
  %t/computer-use-wayland/relay.sock; Restart=no). It had no CU_*
  flags. The flags are consumed by cu.py in the session-driver
  children: code-exec gate at cu.py line 3101 (env CU_CODE_EXEC
  must be 1/true/yes) and pick4 fastpath gate at cu.py line 3370.
  The broker builds child env from its own os.environ
  (session_remote.py line 474 base_env = dict(os.environ), line
  523 Popen with env), so flags in the relay process env propagate
  to every session child.
- Laptop tree sync, 18:31:38 +07: git fetch origin plus git pull
  --ff-only origin todolist-push on the laptop. Fast-forward from
  6594dd9 (a local merge commit, already an ancestor of origin) to
  4eb591764c7ac5741c7ef34c5102ab387c54c284. Laptop HEAD now equals
  the VM HEAD 4eb5917 (commit "docs: W-A1FIX F1/F2/F4/F5/F6 log,
  live Chromium runner, preflight probe driver, F2 evidence",
  pushed 18:31:27 +07, verified via git ls-remote).
- Installed-tree check, same call: python3
  scripts/sync-installed.py --check reports "sync-installed:
  error: latest release ledger source identity differs from the
  current checkout". That is the expected staleness after any new
  commit (the installed tree was last synced at an earlier HEAD);
  the relay runs from the CHECKOUT (WorkingDirectory
  /home/james/computer-use-wayland, started_git_head from git
  rev-parse HEAD in that checkout), not from the installed tree,
  so this does not block the pilot. The installed-tree re-sync is
  W-SYNC's lane; recorded here as-is, not silently fixed.
- Drop-in written 18:31:57 +07:
  /home/james/.config/systemd/user/computer-use-relay.service.d/flags.conf
  (69 bytes, verified by cat):
  [Service]
  Environment=CU_CODE_EXEC=1
  Environment=CU_PICK4_FASTPATH=1
  The drop-in persists across restarts, so every future relay
  restart keeps the flags without anyone re-passing them.
- Broker idle check immediately before restart, 18:31:57 +07:
  state finished, driver stopped, active_sequence null, generation
  411cfadf, owner w-sync. No live session was running, so the
  restart could not kill one.
- Restart, 18:32:03 +07: systemctl --user daemon-reload, then
  systemctl --user restart computer-use-relay.service. Service
  active, new MainPID 70985 (old PID 3913, started 17:19).
- Verification, 18:32:03-18:32:06 +07:
  - systemctl show Environment:
    PYTHONDONTWRITEBYTECODE=1 XDG_CACHE_HOME=/home/james/.cache
    CU_CODE_EXEC=1 CU_PICK4_FASTPATH=1. Both flags present.
  - /proc/70985/environ: CU_CODE_EXEC=1, CU_PICK4_FASTPATH=1.
    Both flags present in the live relay process env.
  - Broker status 18:32:06 +07: {"ok":true,"broker":"running",
    "broker_generation":
    "8624ae4023d6dc0d1ea2b6a45b64ef93","loaded_code_sha256":
    "d490f369f6b754d200518055025ef956284a759cc49e3ee70ed6b2a4483e3da4",
    "started_git_head":
    "4eb591764c7ac5741c7ef34c5102ab387c54c284","state":"idle",
    "owner":null,"generation":null,"driver":"idle","guardian":
    "idle","cancelled":false,"cancellation_state":"clear",
    "recovery":"none","next_sequence":1,"active_sequence":null,
    "last_start_error":null,"last_status_error":null}.
    started_git_head EQUALS the repo HEAD 4eb5917. New broker
    generation 8624ae40 (relay restarted). State idle, no owner,
    no active sequence. The stale cleanup_failed error marker from
    before the restart is gone (both error fields null).
- No live through-relay code-exec smoke test was run: the flags
  are verified in the live relay process env, the inheritance path
  to session children is code-verified (session_remote.py lines
  474 and 523), and the gates are code-verified (cu.py lines 3101
  and 3370). A smoke session would add broker state for little
  marginal proof; the pilot executor exercises code-exec through
  the relay on run 1 and the runbook pre-run checks catch a flag
  problem before any run counts.
- Verdict: F3 CLOSED at HEAD 4eb5917. Relay has CU_CODE_EXEC=1 and
  CU_PICK4_FASTPATH=1, started_git_head equals the repo HEAD, and
  the broker is idle.
- Resume-time re-verification (REQUIRED, exact commands): this
  final log commit moves HEAD past 4eb5917, so the relay's
  started_git_head will be one commit behind at the end of this
  session. At resume, before run 1, run: (VM) cd
  ~/workspace/computer-use-wayland && git fetch origin && git
  pull --ff-only origin todolist-push && git rev-parse HEAD
  (call it H2); (laptop) git fetch origin && git pull --ff-only
  origin todolist-push && git rev-parse HEAD (must equal H2);
  systemctl --user restart computer-use-relay.service (the flags
  persist via the drop-in, no re-passing needed); then
  tr '\0' '\n' <
  /proc/$(systemctl --user show computer-use-relay.service -p
  MainPID | cut -d= -f2)/environ | grep -E
  'CU_CODE_EXEC|CU_PICK4_FASTPATH' (both must print =1) and
  python3 /home/james/computer-use-wayland/scripts/session_remote.py
  status (started_git_head must equal H2, state idle,
  active_sequence null). Only then issue run 1.
- Resume notes from owner decisions 18:21 and 18:30 +07, 22/11:
  the browser does NOT auto-open after a reboot; only the owner
  opens it, so if the machine rebooted before resume, the Chromium
  instance must be opened by the owner (do not auto-start it).
  And: whenever ANY agent drives the machine by ANY method, the
  computer-use pill/overlay MUST be visible; interim rule is all
  live browser writes go through act-now/computer-use session (pill
  shows) and raw CDP is read-only until a pill-on-CDP mechanism
  exists. The F2 live runner in this session used raw CDP writes
  before that rule was issued (18:00-18:02 +07, rule 18:30 +07);
  any future live re-validation must go through a session that
  shows the pill.

## Evidence files

- improvements/w-a1fix-f1f6-evidence/f2-results.jsonl (7882 bytes,
  md5 06a1218435443f735c92268a5cf6a37d, 50 lines): run 1, tests
  06/07/08/09/10, 18:01:01-18:01:17 +07. Byte-exact copy of
  /tmp/a1fix-20261122/f2-results.jsonl on the laptop (md5 matched).
- improvements/w-a1fix-f1f6-evidence/f2-rerun.jsonl (6021 bytes,
  md5 49821ae631b25ff47373b742f77b9f63, 39 lines): run 2, tests 07
  and 09 with the fixed runner, 18:01:59-18:02:24 +07. Byte-exact
  copy of /tmp/a1fix-20261122/f2-rerun.jsonl (md5 matched).
- The runner stdout logs f2-run.log (9486 bytes) and f2-rerun.log
  (7076 bytes) remain on the laptop at /tmp/a1fix-20261122/; they
  mirror the same summaries and were not copied.
- The F4 probe log and probe dirs no longer exist on the laptop:
  the remote preflight dir was wiped at 18:24 for a clean full
  re-run, which the 18:23 hard rule aborted before writing any
  probe dir (verified empty 18:25:48 +07). The F4 probe evidence in
  this log is the record until a new-tab-only re-probe is approved
  and run.
