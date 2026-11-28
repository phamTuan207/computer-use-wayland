# Arch-guard cleanup + CI wiring outcome (2026-11-28)

Owner approved 2026-11-28 10:26 and 10:28 (including running code from a
repo checkout despite the execution-risk flag). Landed as PR #1244,
merge commit 53e61e50 on main. Branch deleted after merge.

## Violations before/after

Pristine main (fae59654): `arch-guard FAIL: 131 violation(s)`

- import-map edges: 21 (all in scripts/zen-rdp/, new code from
  PR #1187/#1225/#1227), plus 2 more the guard could not see
  (scripts/zen-rdp/probes/p3_unsolicited_probe.py imports rdp_client
  and launch_dedicated via a sys.path parent insert; found by the
  independent review). Total real edges added: 23.
- machine-value: 110 (65 home-path, 44 personal-name, 1 split-form
  personal-name in scripts/chromium_cli.py).

After cleanup (merged main 53e61e50, verified): `arch-guard PASS`,
0 violations. DENY_PATTERNS unchanged (diff touches only
ALLOW_PREFIXES and the resolver).

## How each category was cleaned

Import map: 23 edges added to rung3-ci/import-map.txt. Resolver fix in
arch-guard.py: `resolve_static` now tries ancestor dirs of the
importer (only scripts/zen-rdp and scripts/zen-rdp/probes exist as
subdirs, so the change affects exactly the one probe file).

Machine values fixed in live code (no behavior change):

- scripts/sync-installed.py: fallback Path('/home/james/...') ->
  Path.home() / 'computer-use-wayland' (identical on the laptop,
  strictly better on the VM).
- native/computer-use-relay.service: systemd %h specifiers.
- scripts/chromium_cli.py: docstring name reworded to "the user's".
- skill/cli-anything/vscode.md: example paths to ~/Work/...
- tests/ bench + driver files (7 .py, 5 .mjs): fixture/tool paths
  repo-relative or home-relative (os.path / new URL / homedir).
- docs/cookie-session-summary.md: account names redacted.

Machine values allowlisted in ALLOW_PREFIXES, each with a stated
reason per the guard's convention: frozen 2026-11-21/22 run records
(docs/batch, docs/clone2-, docs/two-vision-, 3 dated docs; the
watchdog log keeps its 5 historical name entries per owner decision
2026-11-27), generated realistic-test fixtures (agy-q, agy-q2, fcc-k),
frozen realistic run records, realistic drivers (fixture persona
name), 3 unit-test files (fake parser-input paths).

## CI wiring

.github/workflows/rung3-checks.yml adapted from the integration-wt
candidate to main (push + PR to main):

- Kept: lineage-check, arch-guard, guard unit tests
  (test-arch-guard, test-test-discover, test-stall-detector),
  15 zen-rdp unit tests (candidate had 4; expanded to all pure-unit
  ones), hermetic gate.
- Dropped: steps whose scripts exist only on todolist-push
  (verify-list, check-key-hash, validate-ledger, test-clean-validate,
  test-collect-evidence, test-signal-hygiene, test_tier_a_check,
  probe-gate) and test-seal / test-check-spare-scorer /
  test-pre-freeze-gate, which fail pre-existing on main (missing
  todolist-push deps; verified on pristine main).
- Hermetic gate wired non-blocking (continue-on-error): 35
  pre-existing tests depend on optional tools (git, node, wayland,
  built binaries) and fail stripped. Verified identical before/after
  this cleanup (targeted test_sync_installed pristine-vs-cleaned
  comparison). Flip to blocking once those tests mock/guard their
  tool deps.

First CI run on PR #1244: checks pass (5m19s), gitleaks pass.

## Verification numbers

- Full shard identical to baseline: 1785 tests, ok=1708 error=54
  fail=5 skip=18 (188.3s, 4 shards).
- test-arch-guard 22 tests OK; lineage-check OK.
- Independent review (non-author worker): MAY LAND, no BLOCKING.
  Its one MAJOR (probe edges invisible to the guard) fixed in the
  same PR (resolver + map line). MINORs accepted as-is: series-prefix
  allowlists stay safe while those doc series stay frozen; whole-file
  exemptions verified fixture-only; pre-existing import-map rot
  (13 stale keys, 5 allowed-but-not-actual edges) untouched.
- pii-scan delta clean. Two pre-existing false positives in touched
  files (sync-installed.py session assignment, hcu_batch.mjs example
  email) are on untouched lines and present on main.

## Follow-ups left open

- Fix the 35 tool-dependent tests (mock/guard git, node, wayland,
  binaries), then flip the hermetic CI step to blocking.
- test-seal / test-check-spare-scorer / test-pre-freeze-gate fail on
  main for missing todolist-push deps; port or retire them.
- Import-map rot: 13 keys for deleted modules, 5 allowed-but-not-
  actual edges, 4 import-free modules without keys (pre-existing).
