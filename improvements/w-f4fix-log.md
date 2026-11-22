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

## 5. Live re-probe (to fill: probe 5 trial, full run, close-out, check_run)
