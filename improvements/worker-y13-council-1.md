# Council 1 verdict: Worker Y13 codex-y5 live plan v1

- Reviewer: Council Member 1 (base pin + harness fidelity)
- Date: 2026-11-21 ~19:25 +07
- Plan reviewed: improvements/worker-y13-codex-y5-live-plan.md (v1)
- Files read: tests/realistic/run_agyq2.py (Y4d, commit 1e3901c),
  tests/realistic/run_agy_y2.py (Y9), tests/realistic/run_live.py at HEAD
  and at 1e3901c, improvements/worker-y9-agy-y2-live-plan.md (v2),
  git diff 1e3901c HEAD -- tests/realistic/run_live.py (+415/-66).
- Overall verdict: APPROVE-WITH-CHANGES. The base pin is right and the
  plan is sound in structure, but the harness copy list as written
  reproduces the exact shared-tab-kill bug the Y9 park was invented to
  fix. The runner must be written against run_agy_y2.py for the park,
  bootstrap, recheck, and main, not against run_agyq2.py. No live
  driving until the changes below are in the runner code.

## Q1: Base pin 1e3901c vs HEAD (91d3cd2)

- Verdict: APPROVE. Pin run_live.py to 1e3901c. No change to decision D1.
- The md5 in the plan is correct: git show 1e3901c:tests/realistic/
  run_live.py hashes to 84fa106c253d5e7f16daccf2ce3f14a5, matching the
  plan. The 1e3901c base has diagnose_body and the allow_hidden kwarg
  on goto/refresh/new_tab, which the runner needs.
- What the HEAD diff actually changes (git diff 1e3901c HEAD --
  tests/realistic/run_live.py, one commit, 91d3cd2, Y11 metrics only):
  every hunk is metrics instrumentation, no diagnose or recovery logic
  changes. _classify_snapshot and _diagnose_body_impl are byte-identical
  apart from the rename of diagnose_body to _diagnose_body_impl plus a
  wait-metered wrapper. WD.__exit__ and WD._cleanup are identical in
  both versions (1e3901c lines 329-346, HEAD lines 517-534).
- Behavior changes in the diff that touch the WD/Runner paths the
  runner will use:
  1. WD.click: when self.metrics is not None, one extra pre-click probe
     eval (live_metrics.PROBE_JS, scripts/live_metrics.py line 84) runs
     after scroll/find and before the element click, plus a
     record_click row in a finally block. When metrics is None the
     _metered wrapper passes through untouched.
  2. WD.type_text: when self.metrics is not None, a post-type read-back
     (self.value, one extra find plus property GET per type) runs and
     records input fidelity. When metrics is None, identical to 1e3901c.
  3. WD.eval, find, text, value, visible, click_js, set_file, alert_*,
     scroll_into_view, close_tab, wait_ready, wait_for: wrapped by
     _metered, which returns the unwrapped function immediately when
     self.metrics is None.
  4. WD.switch, goto, refresh, new_tab: same calls as 1e3901c, wrapped
     in try/finally that only emits an action row when metrics is set.
  5. diagnose_body: wrapper increments d._meter_depth during the impl
     when the attribute exists, then notes wait time when metrics is
     set. A 1e3901c-style WD has no _meter_depth attribute, so the
     wrapper is a no-op pass-through.
  6. Runner.__init__ gains an optional metrics=None parameter and
     Runner.step sets and restores the _CURRENT_METRICS global; both
     are inert when metrics is None.
  7. Import-time side effect in HEAD only: it searches for
     live_metrics.py under scripts/ and next to run_live.py, inserts
     that directory into sys.path when found, and prints one stderr
     line when the import fails.
- Why the pin still stands: Y13's runner never constructs a
  LiveMetrics object and never sets d.metrics, so under HEAD every
  change above would be inert too. But HEAD is unit-verified only
  (Y11 log: 22 + 7 tests), never live-proven, and it buys Y13 nothing:
  scripted steps record think null and the click record is a
  selector-delivery rate, not a grounding hit rate. A verdict run must
  not be the first live exercise of an unproven base. The plan's
  revisit clause is sound: revisit only if Y11b's live proof passes
  before this run AND the council agrees the API diff is safe.
  Default stays 1e3901c.
- Required guard (no plan change, runner discipline): the ship dir
  must contain exactly the 1e3901c run_live.py bytes, verified by the
  launch-time manifest check the plan already requires. Never ship
  scripts/live_metrics.py next to it, and never set LIVE_METRICS in
  the launch environment, so no metrics path can activate by accident
  if the pin is ever flipped.

## Q4: Shared-tab park (Y9) plus Y4d rebootstrap fallback

- Verdict: APPROVE-WITH-CHANGES. The park logic is sound in outline
  but the plan as written does not actually contain it, and three
  holes remain.
- How DELETE /session behaves (the fact the park relies on):
  base WD._cleanup (1e3901c run_live.py lines 333-346, identical at
  HEAD) first DELETEs /window for every handle in opened_tabs, then
  DELETEs /session. Y4d proved DELETE /session closes the session's
  current tab: the shared test tab died 20/20 at session exit. So
  DELETE /session really closes only the throwaway IF AND ONLY IF the
  current window is the throwaway at delete time. The park's whole
  job is to make that true.
- Finding Q4-F1 (sharpest hole, BLOCKER in effect): the plan's copy
  list names only run_agyq2.py functions, and run_agyq2.py contains
  NO park implementation at all. The park lives only in
  run_agy_y2.py: class Y9WD (line 358), _park_before_exit (lines
  372-408), __exit__ (lines 410-415). A runner built from the plan's
  list as written has no park. Exact change: port Y9WD verbatim from
  run_agy_y2.py (renamed, ports and paths adapted) and use it for
  EVERY session: bootstrap_tab, each per-test session, _recheck, and
  the suite-end cleanup session. Y4d uses plain WD() in all four
  places (bootstrap_tab line 1296, per-test main line 1537,
  _recheck_shared_tab line 478, suite-end cleanup line 1622), and
  plain-WD exit is what kills the shared tab.
- Finding Q4-F2: Y4d bootstrap_tab (run_agyq2.py lines 1282-1321)
  kills the shared tab it just created. It uses plain WD(), and its
  finally calls wd.__exit__() while the current window is the new
  shared tab (removed from opened_tabs, so _cleanup skips the
  /window DELETE and goes straight to DELETE /session on the shared
  tab). That is the Y4d 20/20 finding, not a hypothetical. Exact
  change: bootstrap must run under the parked WD subclass (Y9
  bootstrap_tab, run_agy_y2.py lines 2191-2270, uses Y9WD at line
  2216 and 3 fresh-tab attempts). Copying Y4d bootstrap_tab verbatim
  means test 01 starts with "shared tab gone, rebootstrap" at best,
  or a dead shared tab at worst.
- Finding Q4-F3: Y4d _recheck_shared_tab (run_agyq2.py lines 472-491)
  also kills the shared tab. It opens a plain WD(), switches to the
  shared tab to diagnose it, then __exit__ DELETEs /session with the
  shared tab current. Every INFRA recheck would destroy the evidence
  tab and force a rebootstrap on the next test. Exact change: use
  Y9's _recheck_shared_tab (run_agy_y2.py lines 756-782, with Y9WD
  at line 761) instead.
- Finding Q4-F4: can the park tab itself be the shared tab? Not by
  handle: window/new always creates a fresh handle, so new_tab can
  never return the shared tab. But the park can still kill the shared
  tab in effect, two ways. (a) _park_before_exit first closes every
  handle in opened_tabs (run_agy_y2.py lines 387-393). The design
  invariant is that the shared tab is never in opened_tabs, but
  nothing in Y9's code asserts it; if any path re-adds the shared
  handle to opened_tabs, the park closes it before creating the
  throwaway. Exact change: assert the shared handle is not in
  opened_tabs at the top of _park_before_exit, and log loudly if it
  is. (b) The final switch to the throwaway (lines 404-407) sits in
  try/except pass with no verification that the current window
  actually changed. If that switch fails silently, DELETE /session
  closes whatever is current, which may be a test tab. Exact change:
  after the switch, read GET /window and confirm it equals the
  throwaway handle; on mismatch, log PARK-FAILED and do not rely on
  the park for that exit.
- Finding Q4-F5: the park is best-effort with silent fallback to the
  old behavior. If new_tab raises inside _park_before_exit (lines
  397-400 return silently), base _cleanup runs with the current
  window uncontrolled, which is exactly the state after an INFRA
  failure or a rebootstrap exhaustion. Y9's per-test finally
  mitigates the common case by switching to a known test tab or a
  sacrificial tab before wd.__exit__() (run_agy_y2.py lines
  2729-2740), but any path that exits without that pre-switch
  (session-creation failure, bootstrap failure, _recheck) still
  exposes the shared tab. Exact change: log PARK-FAILED explicitly
  whenever the park cannot be established, and treat the following
  session delete as shared-tab-risky: the next test must recheck the
  shared tab handle before driving, never assume it survived.
- Finding Q4-F6: the park has never run live. Y9's re-review B2 fix
  is code-reviewed only; Y9's live run (queued before Y13) is the
  first live exercise of the park. The plan treats the park as proven
  ("Y9 park pattern"). Exact change: make Y13's reliance on the park
  conditional on Y9's live result. If Y9 still prints "shared tab
  gone, rebootstrap" on every test, the park failed live and Y13
  must run with the rebootstrap fallback as the primary mechanism,
  with the park kept only as defense in depth, and must say so in
  its run log.

## Q8: Harness functions copied from run_agyq2.py

- Verdict: APPROVE-WITH-CHANGES. Most helpers copy cleanly; four
  functions need a different source (run_agy_y2.py, not run_agyq2.py)
  and the copy list itself is incomplete. Per-function verdicts:
- _ppid_of (run_agyq2.py lines 76-87): MISSING from the plan's list
  but REQUIRED. preflight calls it for every PID-file entry. Copying
  preflight without it is a NameError on the first live PID file.
  Exact change: add _ppid_of to the copy list, verbatim.
- _check_handover (lines 139-164): OK with a path adaptation only.
  HANDOVER_FILE must change from /tmp/worker-y4d-handover.json
  (line 68) to the Y13 token path. HANDOVER_MAX_AGE_S (4h) unchanged.
- _hyprland_signature (lines 89-137): OK unchanged. No paths or
  ports. The two-source version (environ, then socket-dir with
  AF_UNIX verify) is the live-proven one; do not simplify it.
- start_server (lines 166-191): OK with adaptations the plan already
  names. Probe URL must change from the agy-q2 fixture to the
  codex-y5 fixture (test-01-git-workflow.html), and SERVER_PORT
  8768 becomes 8770 via the launch environment (1e3901c run_live.py
  reads LIVE_SERVER_PORT at import). Note the import list in the plan
  is wrong here: run_agyq2.py imports SERVER_PORT and
  start_server as _rl_start_server from run_live (lines 53-56).
  The plan's stated import list (WD, Runner, diagnose_body,
  log_step, start_server) omits SERVER_PORT and the alias. Exact
  change: import SERVER_PORT and _rl_start_server as in run_agyq2.py.
- select_option (lines 193-200): OK unchanged. Pure eval JS, no
  paths or ports.
- select_by_text (lines 202-210): OK unchanged. Unused unless needed,
  as the plan says.
- clear_input (lines 212-218): OK unchanged, but note Y9 removed it
  as dead code in re-review (N9); run_agyq2.py itself uses it once
  (line 905). Keep it only if a codex-y5 driver needs the input
  event; otherwise drop it rather than carrying dead code.
- set_date (lines 220-227): OK unchanged as a fallback only. The
  plan already guards it correctly: no fixture input is type=date
  (test-05 is a plain text input), so set_date must never be called
  on this suite unless a live check proves otherwise.
- txt (lines 229-233), count (235-238), has_class (240-245),
  is_checked (247-251), norm (253-256): OK unchanged. Pure eval or
  string helpers, no paths or ports.
- _log_diag (lines 258-291): OK unchanged. Uses log_step and
  r.details only.
- rebootstrap_tab (lines 293-349): ADAPT. Two deltas. (a) The
  exhaustion raise at line 348 is a bare RuntimeError with no INFRA:
  prefix; Y9's version raises "INFRA: rebootstrap: no visible test
  tab after 3 attempts" (run_agy_y2.py lines 596-597). Take Y9's
  prefix, so a direct rebootstrap failure classifies as INFRA
  instead of a bare runner error. (b) It references the _TEST_TABS
  global and r.base; both must exist in the Y13 module. Otherwise
  the registered-handles-only discipline copies unchanged.
- ensure_visible (lines 351-470): OK unchanged. The 8.0s enforced
  deadline, poll, tz-hidden removal with verified-removal flagging,
  and rebootstrap swap all carry over; it depends only on d, r.tab,
  r.base, and r.details, all of which the Y13 Runner must carry the
  same way Y4d does (r.tab set dynamically; base Runner has no .tab
  attribute, which is fine in Python).
- _recheck_shared_tab (lines 472-491): ADAPT, do not copy from
  run_agyq2.py. See Q4-F3: Y4d's version uses plain WD() and kills
  the shared tab on exit. Take Y9's version (run_agy_y2.py lines
  756-782), which uses Y9WD and guards empty snapshots.
- open_fixture (lines 494-560): ADAPT. Fixture path changes from
  agy-q2/fixtures/ to codex-y5/fixtures/. And drop the no-op step at
  line 555: r.step("check body visible", "check", lambda:
  d.visible("body")) logs ok True even when the body is hidden,
  because Runner.step only fails on exception and ignores a False
  return. Y9 already removed it for exactly this reason (Redteam
  re-review N14; run_agy_y2.py lines 1124-1127 keep only the
  r.check gate). Keep the r.check gate.
- bootstrap_tab (lines 1282-1321): ADAPT, do not copy from run_agyq2.py.
  See Q4-F2: Y4d's version uses plain WD() and a single attempt with
  allow_swap=True, and its exit kills the shared tab. Take Y9's
  bootstrap_tab (run_agy_y2.py lines 2191-2270): parked WD, 3
  fresh-tab attempts, allow_swap=False, fixture path adapted.
- preflight (lines 1323-1500): OK with adaptations. Fixture probe URL
  and handover file path change; the rest (BiDi 9222, Marionette
  2828, Hyprland SAFETY gate with 10s timeout, orphan sweep with
  parent check, ppid-None refuse, cmdline re-verify before SIGKILL,
  lock check accepting POSIX/FLOCK/OFDLCK with the ancestor set
  including os.getpid()) copies unchanged. See the preflight gaps
  section below for what is missing relative to Y9.
- main (lines 1501-1639): ADAPT, do not copy from run_agyq2.py. Y4d
  main has no re-run logic at all, no manifest verification, no
  --verify-manifest flag, no per-test screenshots, no gecko-log
  copy, no attempt fields, and uses plain WD() per test (line 1537).
  The plan requires a one-time infra re-run per test, a launch-time
  manifest check, and per-test screenshots, none of which exist in
  Y4d main. Take Y9's main structure (run_agy_y2.py lines 2507-2864)
  as the base and adapt ports, paths, and the suite name.
- Missing from the plan's copy list entirely, all required for what
  the plan promises: the Y9WD class itself (_park_before_exit,
  __exit__, screenshot, _wd call counter); the _TEST_TABS global
  (run_agyq2.py line 63); HANDOVER_FILE / HANDOVER_MAX_AGE_S
  constants (lines 68-69); TRACKED_ITEM (line 74); _md5_of,
  _verify_manifest, and _copy_gecko_log (run_agy_y2.py lines 266,
  273, 2479); and the Runner.check JSONL override plus attempt and
  gaps handling (Y9Runner, run_agy_y2.py lines 458-540), without
  which intermediate checks leave no JSONL record. Exact change:
  extend the copy list to name each of these with its source file.

## Preflight gaps: plan vs Y4d preflight vs Y9 preflight

- Against Y4d's preflight, the plan misses nothing. Its list
  (handover token, BiDi 9222, Marionette 2828, Hyprland IPC SAFETY
  gate, fixture server, orphan sweep by PID with parent check,
  zen_dom.lock flock held by an ancestor) matches run_agyq2.py lines
  1323-1500 in full, including the ppid-None refuse and the cmdline
  re-verify before SIGKILL.
- Against Y9's preflight (run_agy_y2.py lines 2271-2505), the plan
  misses four things:
  1. Launch-time slot-port checks. Y9 checks the predecessor's ports
     are FREE at launch (Y8 server 8767 and driver 4451,
     run_agy_y2.py lines 2337-2344): if either answers, the
     predecessor is still alive and the launch refuses. Y13 names
     only its own ports (8770/4450). Exact change: add free-port
     checks for the immediate predecessors in the queue (at minimum
     Y9 8769/4449 and Y8b 8767/4451; Y11b and Y6c ports once known)
     as a preflight step, not a manual check. Partial mitigation
     already exists: Y4d's orphan sweep globs /tmp/geckodriver-*.pid
     across all ports and refuses when a live driver has a live
     parent, but that only catches drivers with PID files, not a
     live fixture server holding a port.
  2. The runner-quiet process check is procedural only. The plan's
     Slot section says "before driving I ALSO do a runner-quiet
     process check", but it is not listed as a preflight step and
     not in the copy list. Exact change: wire it into preflight code
     (no other run_*.py process on the laptop, same check Y6b v2
     uses), so a manual step cannot be skipped under time pressure.
  3. JSONL rotation at launch. Y9 rotates the existing JSONL to
     .prev-<timestamp> so a new run never appends to a stale log.
     Y4d appends. Exact change: rotate LIVE_LOG at launch and log
     the rotation, or refuse when the log already exists.
  4. Handover token fingerprint binding (Y9 N5), preflight-failure
     suite JSON (Y9 N6), and the --verify-manifest dry-run flag
     (run_agy_y2.py lines 2509-2510). Exact change: add all three;
     the manifest check must run BEFORE preflight and the server
     start, so a bad ship fails before any driving.
- The gecko-log copy per test (run_agy_y2.py line 2479, defense in
  depth after each WD exit) is also absent from the plan. Add it;
  it costs one file copy per test and preserves the only evidence
  when a session dies.

## Notes (no action required)

- The plan's test-10 reload handling (click, wait_ready, 1s settle,
  diagnose, no d.refresh()) is consistent with the base: refresh
  would re-run the document and re-trigger the extension content
  script, which is a second reload, not a settle.
- The plan's ports (server 8770, WD 4450, Marionette 2828 shared)
  do not collide with Y4d (8768/4448) or Y9 (8769/4449). Marionette
  2828 is shared by design (connect-existing).
- The queue order in the plan (Y8b, Y9, Y11b, Y6c, then Y13) is
  unchanged by the MEMORY.md note added 19:20 that Y14 (batch-3
  live) queues after Y13.

## Summary of required changes

1. Keep the 1e3901c pin (md5 verified). No change to D1.
2. Port Y9WD (_park_before_exit + __exit__ + screenshot) from
   run_agy_y2.py and use it for bootstrap, per-test, recheck, and
   suite-end sessions. Do not build the runner from run_agyq2.py's
   copy list as written.
3. Take bootstrap_tab, _recheck_shared_tab, open_fixture (minus the
   no-op check step), rebootstrap_tab (INFRA prefix), and main from
   run_agy_y2.py, adapted to codex-y5 paths and ports.
4. Add _ppid_of, _TEST_TABS, HANDOVER_FILE, TRACKED_ITEM,
   SERVER_PORT / _rl_start_server import, _md5_of,
   _verify_manifest, _copy_gecko_log, and the Runner.check JSONL
   override to the copy list.
5. In _park_before_exit, assert the shared tab is not in opened_tabs
   and verify the current handle equals the throwaway after the
   switch; log PARK-FAILED loudly on any park failure.
6. Condition park reliance on Y9's live result; if Y9 still prints
   "shared tab gone, rebootstrap" every test, the park failed live.
7. Preflight: add predecessor free-port checks, wire the
   runner-quiet check into code, rotate the JSONL at launch, add the
   --verify-manifest flag, run the manifest check before preflight.
