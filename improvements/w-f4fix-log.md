# W-F4FIX log: close F4 of the A1 pilot (adapter fix + CB-2 template + re-probe)

- Owner: Pham Tuan. Worker: W-F4FIX, for COORD-CLICK-6.
- Branch: todolist-push. Repo: ~/workspace/computer-use-wayland.
- Task received: 18:36:16 +07, 22/11/2026. Decision of COORD-CLICK-6: FIX
  THE ADAPTER, do not amend the runbook retry model. Frozen design
  f31abcf unchanged.
- Rules: no em dash (U+2014) or en dash (U+2013) anywhere in this file.
  No personal info. No ydotool. Explicit pathspec commits only, never
  plain git commit, never git add -A, never git commit --amend on a
  pushed commit. Every commit pushed at once, verified by git ls-remote.
- Evidence standard (Lauren Tan): every claim carries command, output,
  commit hash, and wall-clock time (Asia/Ho_Chi_Minh) with elapsed time.
  No self-grading pass; independent verification owed.
- Hard rules acknowledged in this session, 18:36 +07 22/11/2026:
  (a) 18:23: NEVER close or navigate any tab/window Pham Tuan opened.
  Re-probe opens ONLY a NEW tab beside, never navigates an existing
  tab; at the end close ONLY the tab I opened, by its exact tab id;
  NEVER restart Chromium; never touch Zen/Brave/mochi tab/any tab of
  Pham Tuan. No reckless /json/close.
  (b) 18:30: the pill MUST show on any live control. Before any live
  re-probe, verify the probe path (one-shot session of the driver)
  shows the pill; if it does not, do NOT run live, finish parts 1
  and 2 plus unit tests, then STOP and report the live re-probe as
  waiting on a pill path.
  (c) No live pilot arm, only preflight probes. Do not read the sealed
  manifest (~/workspace/a1fix-sealed/a1-manifest.jsonl, only Muse
  reads it).

## 0. Session start

- 18:36:28 +07 (11:36:28 UTC): git log HEAD a803d7a, branch
  todolist-push, tree clean except tests/realistic/clone1-batch3/
  results.json (modified, NOT mine, never staged) plus untracked
  improvements files from other workers (never staged).
- Starting state from W-A1FIX (log improvements/w-a1fix-f1f6-log.md,
  commits 4eb5917 + 5e13215): probes 1-4 PASS live, probe 5 FAIL at
  18:20:48 +07 with "browser worker ended; stop this task" after a
  first dom_act ok:false (failed assert, completed 0). Preflight dir
  on the laptop wiped 18:24, empty since, no probe dirs, no
  preflight-log.jsonl.

## 1. Adapter fix

### 1a. Defect, verified by code read before any edit

- scripts/browser_worker.py line 53 (HEAD a803d7a):
  `if isinstance(result,dict) and result.get('ok') is False:self.close()`.
  Any ok:false response closes the worker, and request() raises
  'browser worker ended; stop this task' once closed. An assert fail
  is a RESULT, not a dead session, so in-program retry after a failed
  dom_act is impossible on this adapter.
- Second half of the same defect, found by reading the worker child:
  scripts/cdp.mjs worker loop, near the end of the file:
  `if(result?.ok===false){process.exitCode=1;break;}`. The Node
  worker process itself EXITS on the first ok:false response. Fixing
  only browser_worker.py would leave the next request writing to a
  dead child stdin (BrokenPipeError, then close and raise), so the
  live probe 5 would fail again at the next layer. Both halves must
  change for the gate (probe 5 PASS live) to be reachable. The
  one-shot (non-worker) cdp.mjs path keeps exitCode 1 on error; that
  path exits anyway, so it is left alone.
- Fatal behavior kept, per brief: process exit, timeout, bad framing,
  non-dict/list response, oversized request/response, cancellation
  all still close the worker with no replay. Only a well-formed
  dict/list response with ok:false stops closing the worker.

### 1b. (to fill: edit, unit test, node-level test, commit hash)

- Edit 1, scripts/browser_worker.py (18:39 +07): removed the
  `if result.get('ok') is False: self.close()` line; a well-formed
  dict/list response with ok:false is now returned to the caller and
  the worker stays alive. Comment records the rule and the fatal
  paths that still close via the except.
- Edit 2, scripts/cdp.mjs worker loop (18:39 +07): removed the
  `if(result?.ok===false){process.exitCode=1;break;}` exit, with a
  comment recording why; added `process.exitCode = 0` on clean
  stdin EOF (handle() sets exitCode 1 per failed request, so a
  worker that served results and then closed cleanly must not look
  like a crash; a stream error still exits 1 via the catch). The
  one-shot path is untouched. First attempt at edit 2 broke a brace
  (node --check SyntaxError 18:39:30 +07); fixed the same minute,
  node --check OK 18:39:41 +07. No em dash or en dash in either file
  from my edits (the one em dash in browser_worker.py line 27 is
  pre-existing, not mine).
- Node-level survival test (/tmp/node-worker-survival.py, no browser):
  spawn `node scripts/cdp.mjs --worker`, send unknown operation,
  then tabs to a dead port, then unknown operation again. Result
  18:39:41 +07 (VM) and 18:43:27 +07 (laptop, patched file): all
  three replies ok:false, worker alive after each, exit code 0 on
  stdin close. NODE WORKER SURVIVAL: PASS.
- Unit test, tests/test_browser_worker.py: replaced
  test_error_json_closes_child_without_replay with
  test_error_json_survives_for_in_program_retry. The fixture child
  answers the first request with {ok:false, completed:0, error:
  'assertion failed'}, then echoes. The test asserts the first
  reply, worker not closed, child process alive, second request in
  the SAME session returns its echo, spawn called once, then close
  is clean. Run 18:39:55 +07: 14/14 OK (3.5s). Neighbour suites
  18:40:13 +07: test_code_exec, test_dom_act, test_p2_element_ref,
  test_session_driver, test_endpoint_retention,
  test_session_continuation, 229 tests OK (15.3s). Fatal paths
  (malformed, child death, timeout, oversized) still close with no
  replay, covered by the unchanged tests.
- Commit 5745e3e, pushed 18:41 +07, ls-remote 5745e3e5f8542619468c
  80fc0eeadbdc1bee42a (2 files, pathspec add and commit).
- cdp.mjs commit BLOCKED by a shared-tree collision, recorded here
  for COORD: W-PILLCDP is working concurrently in the same VM tree
  and has uncommitted pill-gate work in scripts/cdp.mjs (about 100
  lines: CDP pill gate in handle() for act, plus chromium_cli.py,
  s2_flip_live.py, test_chromium_cli.py, docs/overlay.md, new
  tests/cdp_pill.mjs and test_s2_flip_pill.py, log
  improvements/w-pillcdp-log.md, design written 18:40 +07).
  Committing scripts/cdp.mjs now would sweep their work into an F4
  commit, so the VM cdp.mjs fix stays UNCOMMITTED until W-PILLCDP
  lands theirs; then the diff will be only my hunks and it can be
  committed normally. The laptop received the same two hunks by
  direct patch instead (see section 4), so the live probe is not
  blocked by this.

## 2. CB-2 template fix

- Template located: runbook.md section 5 step 2, template rules,
  first bullet (navigate with one desktop act, Ctrl+L, type the URL,
  Enter). The probe doc (preflight-probe.md) P1 programs show the
  same unstamped literal shape; the driver stamps them at runtime.
- Reproduction, 18:39:01 +07, /tmp/cb2-repro.py (VM, no browser):
  element_ref.validate_action on the literal navigate act raises
  "action 0 is missing scope: scope is mandatory in action data
  (CB-2)"; code_exec._validate_dom_actions on the literal dom_act
  with snapshot_id + target raises the same. Stamped versions pass
  both checks. Code path: code_exec.api_act validates every desktop
  act action with validate_action_binding against the bound
  observation (scripts/code_exec.py about line 1242), and
  _validate_dom_actions does the same for dom_act (about line 317).
  The executor copying the template verbatim would be refused
  before any input, at run 1.
- Fix, runbook.md section 5 step 2 (commit a51cf9c, pushed 18:41
  +07, ls-remote a51cf9c9fc362ce1809bfb230c2b0ed3dbc29009): new bullet
  requiring scope + observation_id on EVERY act and dom_act action,
  with the desktop (obs scope/id) and DOM (tab id/snapshot) forms,
  the stamped navigate act written out literally, and the retry rule
  (re-observe first, stamp from the fresh observe or snapshot).
  0 em dash, 0 en dash. The frozen design is untouched: this is a
  template correction, not a retry-model or cost-model change.
- Note for COORD: preflight-probe.md literal P1 programs still show
  the unstamped shape; the driver (run_preflight_probes.py) stamps
  them at runtime, and the runbook rule now tells the executor to
  stamp when composing. Whether to also stamp the probe doc literals
  before resume is COORD's call, not taken here.

## 3. Pill check (rule 18:30), code path, before any live run

- Verdict: PILL YES. The probe driver runs every probe inside a
  real computer-use session, not raw CDP.
- Path, verified by code read: run_preflight_probes.py Session()
  opens SSH to `CU_CODE_EXEC=1 python3 cu.py session -- python3
  cu.py session-driver`. cu.py main routes 'session' to
  cursor_session.supervise(env, driver). supervise spawns the
  guardian; guardian() (scripts/cursor_session.py) gates on
  indicator.liquid_available (fails fast when hyprglass is not
  active or shaders are warming up), then creates indicator.Native
  (the pill) and prints 'ready'; supervise waits for 'ready' and
  'registered' before starting the driver. The guardian loop raises
  'session indicator lost' if the pill process dies, and serves the
  indicator socket. So the pill is up for the whole probe session,
  and every browser write inside it (code-exec act/dom_act through
  BrowserWorker to cdp.mjs) happens under a visible pill. A session
  that cannot show the pill fails before any browser write, and the
  driver raises.
- This matches the 18:30 interim rule exactly ("live browser writes
  go through act-now/computer-use session so the pill shows").
  W-A1FIX's raw-CDP F2 runner is NOT used here. W-PILLCDP's
  additional per-act pill gate in cdp.mjs (uncommitted, VM only at
  18:40 +07) is a second layer, not needed for this verdict and not
  on the laptop.
- Live confirmation for the verdict: the probe session must start
  (guardian 'ready') and finish its browser writes without a
  'session indicator lost' failure; a successful probe run is that
  proof. Recorded with the probe results in section 5.

## 4. Laptop sync and live pre-checks (read-only unless noted)

- Baseline tabs on 9223, 18:42:54 +07 (8 targets, read-only
  /json/list): page A67A718D5E236F894F9863F48834743C "Chat - mochi"
  https://muse.ai/ (mochi's tab, NEVER navigate or close); page
  025266AE11C86425817A3AF6E0FB7B26 "Pick 4 DOM fixture"
  http://127.0.0.1:8768/pick4-fixture.html (W-A1FIX leftover probe
  tab, pre-existing, never navigate); muse.ai stripe iframes,
  omnibox popups, one service worker. These two page ids are the
  baseline: both must still be listed after the run.
- Broker status, 18:42:49 +07: running, generation 8624ae40, state
  idle, owner null, driver idle, active_sequence null, error null.
  SOLO and idle. started_git_head 4eb5917 (before the pull below).
- Laptop uptime 1:28 at 18:42:49 +07 (no reboot since the 18:13
  relaunch). Fixture server alive, PID 45976 since 18:00, both
  fixtures HTTP 200 (pick4, f01) at 18:43:02 +07.
- Laptop pull, 18:43:11 +07: git fetch + pull --ff-only origin
  todolist-push, HEAD 4eb5917 to 331523f83834596e44af5046e880b717eb
  58f1e1 (equals VM HEAD). 7 files changed. Tree otherwise clean
  except pre-existing untracked files.
- Laptop cdp.mjs direct patch, 18:43:23 +07: /tmp/f4-cdp-patch.py
  applied ONLY the two F4 hunks (asserts the file is the HEAD
  version with no pill gate, asserts each anchor once, node
  --check OK after). Diff: 12 insertions, 1 deletion. Laptop node
  worker survival test 18:43:27 +07: PASS (three ok:false replies,
  worker alive after each, exit 0). The laptop cdp.mjs fix is
  uncommitted by design (see section 1b); the VM commit follows
  once W-PILLCDP lands.

## 5. Live re-probe

### 5a. Probe 5 trial (single probe, before the full run)

- Run 18:43:53-18:44:02 +07, driver exit 0. P1 ok true,
  retry_logged true, wall 2244.6ms, api_calls 11, log:
  "navigate act ok True", "tab id 1F1017679AE2254F32991D7EF1C0E043"
  (a NEW tab, not any baseline id), "first dom_act ok False
  completed 0" (the expected failed assert), "retry dom_act ok True
  completed 1", "retry confirmed pick4-ok". P2 ok true,
  dom_effect true, wall 470.3ms, api_calls 5, "#result contains
  pick4-ok", same tab. probe_ms 8619.7. PROBE 5 PASS on the first
  try with the fixed adapter. The in-program retry genuinely
  happened: the failed assert no longer kills the session.

### 5b. Full run, all 5 probes, clean directory

- Remote preflight dir wiped 18:44 (my own probe output only) and
  recreated; full driver run 18:44:14-18:44:55 +07, exit 0,
  all_ok true. Every probe opened its own NEW tab (Ctrl+T first
  action, id-diff lookup); no existing tab was navigated.
  - click, 7420.0ms: P1 ok false, error "ref is not present in the
    bound snapshot; observe again", P2 ok true, "#result still not
    clicked yet", same tab 873AEAA6420600A4B69FE06EA1FC0382.
  - fill, 8836.2ms: P1 ok false, same bad-ref error, P2 ok true,
    "#a2 still -", same tab 558290DF569CB47E20E94E57357BA815.
  - set_value, 7585.6ms: P1 ok false, same bad-ref error, P2 ok
    true, "#a2 still -", same tab
    A22652F8F1962CB3A65AB3F84FF14758.
  - assert, 7552.2ms: P1 ok false, same bad-ref error, P2 ok true,
    "#result still not clicked yet", same tab
    910A8C75D2FF02EAB386F037D37EAEC8.
  - retry-logging, 8591.8ms: P1 ok true, retry_logged true, "first
    dom_act ok False completed 0", "retry dom_act ok True
    completed 1", "retry confirmed pick4-ok", P2 ok true,
    "#result contains pick4-ok", same tab
    1DD2366BF1C4186652DCFA301CEA7A41.
- Probe dirs on the laptop: all 5 present, each with end-state.json,
  run-log.jsonl, verify.png. preflight-log.jsonl has 10 lines (5
  probes x P1+P2), matching the full run. No navigate act failed in
  either run (navigate act ok True first try every time, with the
  focus step).
- Pill, live confirmation: all 6 probe sessions (trial + full run)
  started through cu.py session (guardian 'ready', focus on
  Chromium window 0x56307e202df0 verified before each session) and
  completed their browser writes with no 'session indicator lost'
  failure and no guardian startup failure. The pill was up under
  every probe write, per the code path in section 3. No raw CDP
  write was made in this session: the only CDP calls were reads
  (/json/list, /json/version) and the /json/close calls on my own
  tabs below.

### 5c. check_run.py cross-check (Stage 1, laptop, 18:45:05 +07)

- probe-1-click: FAIL exit 1, result_text "not clicked yet" does
  not contain "pick4-ok". EXPECTED: zero-effect proof.
- probe-2-fill: FAIL exit 1, end state {"a2": "-"} matches neither
  pick4 nor f01 shape. EXPECTED: zero-effect proof (the checker
  only knows the full f01 shape; a probe end state with only a2 is
  not a full case).
- probe-3-set-value: FAIL exit 1, same as probe-2. EXPECTED.
- probe-4-assert: FAIL exit 1, result_text "not clicked yet".
  EXPECTED.
- probe-5-retry-logging: PASS exit 0, result_text "pick4-ok hello
  stranger", no problems.
- Cross-check verdict: the set matches the design exactly (probes
  1-4 prove zero effect, probe 5 proves the retry landed). No
  Stage 2 metrics run: the probe dirs are not pilot runs (no
  setup.json, no commands.txt), Stage 1 is the cross-check here.

### 5d. Tab close-out and final state

- Tabs I opened (6): trial probe 5
  1F1017679AE2254F32991D7EF1C0E043; full run click
  873AEAA6420600A4B69FE06EA1FC0382, fill
  558290DF569CB47E20E94E57357BA815, set_value
  A22652F8F1962CB3A65AB3F84FF14758, assert
  910A8C75D2FF02EAB386F037D37EAEC8, retry
  1DD2366BF1C4186652DCFA301CEA7A41. Closed one at a time via
  /json/close/<id>, 18:45:12-18:45:25 +07, each returning "Target
  is closing" and verified after: 9223 still answers, mochi tab
  still listed, the target gone. All 6 closed, Chromium never
  faltered, no restart.
- Final state 18:45:31 +07: /json/list shows the baseline exactly
  (mochi A67A718D..., W-A1FIX fixture 025266AE..., stripe iframes,
  omnibox popups, service worker). Broker idle, SOLO, generation
  8624ae40 unchanged, error null. Chromium windows
  0x56307e202df0 (Pick 4 fixture) and 0x56307e7d9bb0 (mochi chat),
  the same addresses as W-A1FIX recorded: Chromium was NOT
  restarted. Zen never touched. No live pilot arm run.

## 6. Verdict and open items

- F4 CLOSED. Gate met: probe 5 PASS live with a genuine in-program
  retry (first dom_act ok False completed 0, retry dom_act ok True
  completed 1, P2 confirms pick4-ok) + probes 1-4 still PASS +
  check_run cross-check matches design (probe 5 PASS, probes 1-4
  FAIL as zero-effect proof) + CB-2 template fixed in the runbook.
- Commits (all pushed, ls-remote verified): 5745e3e (adapter
  browser_worker.py + unit test), a51cf9c (runbook CB-2), 331523f
  (driver new-tab-only), 9c9fea9 (this log, parts 1-4). This final
  log update is a further commit below.
- OPEN ITEM 1 (for COORD): scripts/cdp.mjs on the VM is still
  UNCOMMITTED, holding my two F4 hunks mixed with W-PILLCDP's
  uncommitted pill-gate work (diff 102 lines at 18:45:31 +07,
  W-PILLCDP had not committed). The laptop carries ONLY my hunks
  as a direct patch (12 insertions, 1 deletion, node --check OK,
  node survival PASS, live probe 5 PASS on it). Once W-PILLCDP
  commits, the VM diff will be only my hunks: commit them with
  pathspec, push, pull to the laptop, and the laptop tree will be
  clean. Until then, do NOT commit scripts/cdp.mjs from the VM
  tree, or it sweeps W-PILLCDP's work.
- OPEN ITEM 2 (resume-time, already known from F3): relay
  started_git_head reads 4eb5917 while repo HEAD has moved past it
  (my commits). At resume, re-verify the relay at the then-current
  HEAD per the F3 procedure in the W-A1FIX log before run 1.
  Probes do not go through the relay, so this did not gate F4.
- OPEN ITEM 3 (note, not mine): preflight-probe.md literal P1
  programs still show the unstamped shape; the driver stamps them
  at runtime and the runbook now states the rule. COORD decides
  whether to stamp the probe doc literals too before resume.
