# Integration phase: Clone2 research findings into computer-use-wayland (2026-11-27)

Owner approval (2026-11-27 18:29): integrate Clone2's research
findings, test on the real laptop, keep researching and
improving until the best level is reached. The Polygon final
test stays LAST and is not part of this phase.

Sources (all on todolist-push):
- improvements/bottleneck-study-20261127.md (26b1133d):
  register M1-M34, proof-law tiers, rejected list.
- improvements/agent-desktop-comparison-20261127.md
  (6b67e286): ideas I1-I23, do-first 10, open privacy finding
  (section 6).
- improvements/zen-r17-continuation-20261127.md (df2bbd0a):
  four stacked defects in zen_live.py, RDP vs Marionette.

Branch facts at start (2026-11-27):
- Work branch: integration-20261127, based on todolist-push
  tip 87242b01. Items push to todolist-push as they land;
  landing to main is by cherry-pick after the council +
  redteam gate (main and todolist-push diverged 981/1221
  commits since merge-base 7007efa68f7a).
- scripts/zen-rdp/ lives on fix-review-20261127, not on
  todolist-push. Zen-lane items bring it in explicitly.
- The tc02 tesseract fix (c7bc697e) is on main, NOT on
  todolist-push: the M16 lineage defect is live.
- Privacy finding: the personal name in
  skill/cli-anything/chromium.md and zen.md is already
  scrubbed on todolist-push (8b9f5da4, 9fd84006) but still
  present on main. pii-scan.py does not check personal
  names; that blind spot is what I13 must close.

## Queue

Status legend: QUEUED, IN PROGRESS, IMPLEMENTED (unit tests
green), LIVE-TESTED (real laptop), LANDED (todolist-push),
ON MAIN (cherry-picked after gate), REJECTED (with reason),
PILOT (running, unproven).

### First batch: PROVEN + do-first

| # | Item | Source | Status | Notes |
|---|---|---|---|---|
| 0 | Privacy census + scrub (skill/ + user-facing docs; main's two files) | agent-desktop s.6 | ON MAIN | PR #1140 merged d69ef7c9; see record below |
| 1 | zen_live.py four defects + test fixes + run_op smoke | R17 s.4 | LIVE-TESTED | e3d81539; live proof on laptop 2026-11-27 18:35-18:38; see record below |
| 2 | M16 hermetic-suite gate + lineage check (incl. cherry-pick c7bc697e) | bottleneck M16 | IMPLEMENTED | 26662dea + 03f177b0 + db91f346 (CI); detector proven pre/post fix |
| 3 | M17 sharded discover (serial stays gate of record) | bottleneck M17 | IMPLEMENTED + MEASURED | Full SHARD MATCH 2340 tests; 175.7s vs 292.0s (1.66x, 1.5-CPU VM); laptop re-measure pending |
| 4 | I13 architecture guard (import map first; docs + name denylist) | agent-desktop I13 | IMPLEMENTED | 4b2cf7cf; found+fixed 7 hardcoded home paths |
| 5 | I21 blocked key-combo list (conservative subset; full after Hyprland check) | agent-desktop I21 | IMPLEMENTED | 2e4369ac; full list from live Hyprland binds |
| 6 | I3 snapshot-qualified refs (additive, id in file, grandfather legacy) | agent-desktop I3 | IMPLEMENTED + LIVE-TESTED | ec7e60b7; live on laptop AT-SPI app: id in file, qualified ground ok, bare warns, foreign refused |
| 7 | M2 one-pass seal wrapper (gate stays separately runnable) | bottleneck M2 | QUEUED | PROVEN manifest identity |
| 8 | I8 probes/ + probe ledger | agent-desktop I8 | QUEUED | Measurement layer for later pilots |
| 9 | I1 envelope + disposition, Zen lane first (rdp_client.py) | agent-desktop I1+I7 | QUEUED | Needs scripts/zen-rdp/ brought in; compat shim |
| 10 | I17 post-action wait flags (after I1, no default timeout) | agent-desktop I17 | QUEUED | |
| 11 | I22 secure-field redaction, DOM/RDP only | agent-desktop I22 | QUEUED | |
| 12 | I5 accounting half (per-node completeness, skeleton, drill-down) | agent-desktop I5 | QUEUED | |
| 13 | I10 auto-wait half (a11y lane, short cap) | agent-desktop I10 | QUEUED | |
| 14 | I16 DOM-rect debug artifact (machine-layer only) | agent-desktop I16 | QUEUED | |
| 15 | I9 capability matrix in doctor (read-only) | agent-desktop I9 | QUEUED | |
| 16 | I15 root-level incomplete marking | agent-desktop I15 | QUEUED | |
| 17 | I19-substitute: MCP drift test | agent-desktop I19 | QUEUED | |
| 18 | I20-substitute: RDP lock hardening + lock map doc | agent-desktop I20 | QUEUED | |
| 19 | M14 adversarial probe gate (Y1b suite) | bottleneck M14 | QUEUED | PROVEN cost 15.478 s |
| 20 | M7 stall detector parts a+b (backtests required) | bottleneck M7 | QUEUED | Flag-only, never auto-takeover |
| 21 | M11c Marionette pre-flight session check | bottleneck M11c | QUEUED | Detection + cheap recovery |
| 22 | M11d pre-freeze triage (process + verify-list gate) | bottleneck M11d | QUEUED | |
| 23 | M28a watchdog rolling branch (append-only) | bottleneck M28a | QUEUED | Needs coordinator approval recorded |
| 24 | M18-reduced, M20, M23, M28d, M29, M34f (guidance/rules) | bottleneck | QUEUED | Docs/rules, low risk |
| 25 | M10-reduced pre-calibrated spare scorer (process) | bottleneck M10 | QUEUED | |

### Pilots (UNPROVEN until they report)

M1 (audit-share instrumentation first), M12 (429 rule,
coord/mei.md s.9), M26 (verdict template), M4, M5, M6, M9,
M11a, M11b, M13, M15, M19, M21, M27, M28b (fallback only),
M30, M31 (snippet library), M32, M33 (after M28a), M34a-e;
I2 (a11y identity probe, refusal budget named first), I4
stale-ref preflight, I6 (click verification, gated on
measured silent-failure rate), I12 (event-line convention),
I14 (bench re-run, query() ungate separately), I18 (drift
check, after item 0), I23 (browser-lane conformance).
M25 is a recommendation to the owner only, not built.

### Rejected (not revived without new evidence)

M3, M8, M22 (standalone; drive-by only), M24, M28c, M28a
force-updated form, M31 generator, M18 automatic selection,
M34f 15x constant; I11, I19 generation, I20 lease as written,
I4 executor, I5 walk-by-default, I6 uniform duty, I8
mandatory gate, I9 big-bang, I10 battery as written, I12
subsystem, I15 per-element, I18 serving, I22 full contract,
I23 AT-SPI half, I2 full RefStore, I14 single-flip, I7
standalone, I1 all-lane big-bang, I13 without import map.

## Per-item records

### Item 0: privacy census + scrub (2026-11-27)

Census (skill/, docs/, README.md, skills/):
- todolist-push: personal name already absent (scrub commits
  8b9f5da4, 9fd84006). Real profile dir found in
  skill/cli-anything/zen.md:83 (example command) and
  scripts/zen_cli.py docstring; both genericized (7caff5b9).
  The same profile hash remains in 10 historical
  improvements/ log files; left as historical record (same
  class as the deferred git-history rewrite).
- main: name present in 5 files. User-facing four scrubbed
  via PR #1140 (merged d69ef7c9, gitleaks check passed,
  independent reviewer PASS with 2 cosmetic nits, both fixed
  before merge). docs/clone2-watchdog-log.md keeps 5
  historical log entries with the name (frozen audit log,
  last updated 2026-11-23; left untouched, noted here).
  pii-scan.py does not check personal names; that blind spot
  is item 4's (I13) job to close.
- pii-scan.py on scripts/zen_cli.py flags the word "session"
  as credential assignments; pre-existing false positives
  (scanner targets snapshot dirs), unchanged by this item.

### Item 1: zen_live.py four defects (2026-11-27)

Implementation (e3d81539): greeting read as length-prefixed
frame (D1); namespaced command names WebDriver:NewSession /
Marionette:SetContext / WebDriver:ExecuteAsyncScript /
WebDriver:DeleteSession (D2); lazy ops table in run_op (D3);
async completion via the appended callback
arguments[arguments.length - 1] (D4); WebDriver {"value":...}
unwrap in execute_async; launch-gate documented in the module
docstring. Tests: fake server now sends the greeting
length-prefixed and asserts namespaced names; run_op smoke
test added. Suite: 21 tests OK in 0.231 s.

Live test on the real laptop (throwaway profile, Marionette
port 2829, MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1; owner Zen PID
807599 untouched, verified before/after):
- Attempt 1 failed before starting: script upload raced with
  launch in one ssh command, file landed 0 bytes. Fixed by
  separate upload (sha256-verified) and launch steps.
- Run 1 (18:35:42-18:35:52): introspect PASS (Zen internals
  visible), list PASS, pin example.com PASS (verified in the
  second list), create-folder FAILED because the example.org
  tab never loaded (about:blank; pickTab matched 0, error
  path correct, rc=1). Test-setup issue, not a client defect.
  Pill gap: `cu.py session` without a driver command errored,
  so no pill showed during run 1. The test window was visible
  on the desktop; recorded honestly here.
- Run 2 (18:38, as cu.py session driver, pill up): folder
  "R17Test" created live, tabCount 2 (example.org plus the
  fresh tab createFolder opens; members report pinned: true,
  both matching Zen semantics in the R17 report). Test
  instance killed by recorded pid after cmdline check;
  session ended; desktop verified clean (only owner windows).
Verdict: the four-defect fix is live-proven on Zen 1.24.3b on
the real laptop for introspect/list/pin/create-folder.
Remaining subcommands share the fixed transport and prelude;
their payloads were not run live (same boundary as R17).

### Items 2-3: M16 hermetic gate + lineage, M17 sharding (2026-11-27)

Implementation: rung3-ci/test-discover.py (per-test runner,
hermetic diff gate, sharded runner with --compare-serial),
rung3-ci/lineage-check.py + lineage-manifest.txt (content
markers, since cherry-picks rewrite hashes), unit tests in
rung3-ci/test-test-discover.py (5 tests OK). The tc02 fix was
cherry-picked from main (26662dea); lineage check passes.

Detector proof (this VM has tesseract installed): with the
pre-fix test file, the hermetic gate FAILs naming exactly the
2 tc02 typed-text tests; post-fix it PASSes. Exit codes
verified (0 post-fix).

Sharding identity: first full run mismatched (1808 vs 2337
tests) because loadTestsFromName does not reproduce discover
identity for import-failing modules, plus a module-name
normalization bug in the shard filter. Fixed by filtering a
discovered suite (identity-exact by construction), attributing
_FailedTest entries to the failing module, and an @@RESULT@@
marker (a test's own stdout had polluted parsing). Second full
run: 2337 vs 2338, 2 mismatches, both test_ime_cleanup
real-signal timing tests flaking under 4-way parallel load on
a 1.5-CPU VM (serial 3/3 OK; different tests flake each shard
run). Resolution: --serial-only list (default test_ime_cleanup)
run in the parent; serial stays gate of record. Third full
run: 2338 = 2338, 1 mismatch: test_cli_exit_codes exists as a
bare function test in TWO modules (test_phase3_brief,
test_phase3_cleanup), colliding in the outcome map. Fixed by
qualifying bare FunctionTestCase ids with their module and
parsing the RESULT status from the right (some ids contain
spaces). Subset re-test incl. the colliding modules: SHARD
MATCH. Fourth full run: 2340 = 2340, 1 mismatch:
test_phase3_cleanup.test_cli_exit_codes serial=ok shard=fail.
Root cause (explained in writing per M17): the test runs
session_cleanup.py --check, which scans the ambient /proc for
a cmdline containing both 'cursor_session' and 'guard'; the
shard runner's own cmdline contains both substrings (module
names test_cursor_session + test_cursor_guard_build), so the
check flips under sharding. Fixed at the source: a
--procs-file test-support flag on session_cleanup.py and the
test passes an empty procs file (3e699cec). Subset with the
cursor modules: SHARD MATCH. Fifth full run: SHARD MATCH,
2340 tests, sharded 175.7s vs serial 292.0s (1.66x on this
1.5-CPU VM). Measured walls across runs: serial 292.0-313.0s,
sharded 162.7-200.9s (1.54-1.82x). Pre-existing suite state on
this VM: 2233 ok, 81 error, 9 fail, 17 skip (missing build
artifacts/binaries; identical in serial and sharded).
M17 measurement complete; laptop re-measure pending (more
cores, expect better).

### Item 4: I13 architecture guard (2026-11-27)

rung3-ci/arch-guard.py + import-map.txt (generated from the
current 71-module graph; new edges must be added deliberately)
+ test-arch-guard.py (2 tests OK). Machine-value denylist:
personal name forms, profile-dir hash pattern, home paths,
Tailscale IPs; scanned over scripts/, skill/, docs/, README.
First run found 7 pre-existing hardcoded /home/<vm-user> paths
(bench_manifest.py, ssh_mux.py, ssh-laptop-mux.sh); all fixed
to Path.home()/$HOME. Guard now PASSes.

### Item 5: I21 blocked key combos (2026-11-27)

Blocklist at the key_names() choke point in scripts/cu.py;
refusals raise ValueError (surface in action results, logged).
Verified against live Hyprland binds on the laptop:
Ctrl+Alt+Delete = close all windows, Super+Q = close window,
Super+Ctrl+P + XF86PowerOff = power menu; plus kernel-level
VT-switch (Ctrl+Alt+F1..F12) and SysRq combos. Neighbours
verified still allowed (Ctrl+Alt+Left/Right Zen workspace
switch, plain F5, plain PrintScreen). Tests in
tests/test_core.py (test_blocked_key_combos_refused). One
pre-existing error in test_core on this VM (missing
native/wtype build artifact), identical with and without the
change.

### Item 6: I3 snapshot-qualified refs (2026-11-27)

scripts/a11y.py: observe() now records snapshot_id inside the
snapshot file (was filename-only); parse_ref() accepts
'<snapshot_id>:<ref>', refuses a foreign id, warns on stderr
for bare refs against id-carrying snapshots, and grandfathers
legacy snapshots without an in-file id. Wired into ground,
drill, act (actions normalized once before validation and
execution). ground() returns qref. Tests: 6 new in
tests/test_a11y.py (26 total OK); the 4 act-exec harness sites
updated to include parse_ref. 22 pre-existing errors in
test_p2_element_ref on this VM, identical with/without.

Live test (laptop, under cu.py session pill, read-only):
Zen is not AT-SPI-registered, so the target was a listed
AT-SPI app (pid 1072896 'Unnamed'). observe -> snapshot_id in
result and in file; ground with qualified ref ok (qref
b73818eabcf2:e1); bare ref ok with deprecation warning;
foreign id refused. Owner Zen PID 807599 untouched. Test
files removed. Pre-existing stale indicator socket from
2026-11-21 left in place (not from this work).

## Sources cited during this phase

- The three source reports above (repo paths + commits).
- External sources are cited per item with URL + access date
  as they are used.
