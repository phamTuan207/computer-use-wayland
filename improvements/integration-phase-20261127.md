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
| 2 | M16 hermetic-suite gate + lineage check (incl. cherry-pick c7bc697e) | bottleneck M16 | QUEUED | PROVEN detector |
| 3 | M17 sharded discover (serial stays gate of record) | bottleneck M17 | QUEUED | PROVEN 1.57x on VM; re-measure on laptop |
| 4 | I13 architecture guard (import map first; docs + name denylist) | agent-desktop I13 | QUEUED | Closes the privacy blind spot |
| 5 | I21 blocked key-combo list (conservative subset; full after Hyprland check) | agent-desktop I21 | QUEUED | |
| 6 | I3 snapshot-qualified refs (additive, id in file, grandfather legacy) | agent-desktop I3 | QUEUED | |
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

## Sources cited during this phase

- The three source reports above (repo paths + commits).
- External sources are cited per item with URL + access date
  as they are used.
