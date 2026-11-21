# Worker Y1 log: Code Mode snippets registry + Part C verification (Codex Luna 6 Max)

Date: 2026-11-21. Worker: Y1 (Muse subagent, driving Codex on the owner's laptop).
Parent: Muse. Owner order: burn every worker's tokens to the limit, work super
thoroughly, council + redteam on decisions.

## 17:47 +07 | 00:00 | Start
- Task: (1) implement the Code Mode snippets registry (Worker N adopt item 2,
  report docs/research/2026-11-21-code-mode-integration.md); (2) fix any Part C
  errors not already fixed by O/O2.
- Read N's report, scripts/codemode.py (prototype, 6 ops, 21/21 tests), the
  Pick 1 template (P1-P4, improvements/pick1-program-template.md), Part C
  (lines 108-142 of LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md).
- Spawned council (3 members) + redteam to debate the snippets design BEFORE
  any implementation. Key tension flagged to them: Pick 1 programs call
  observe/act/dom_* (code_exec.py API) but codemode.execute_op only exposes
  repo.* ops, so a snippet must run in an executor that has its API.

## 17:48 +07 | 00:01 | Baseline (verified by Y1 directly, not by Codex)
- python3 -m unittest tests.test_codemode: 21 tests, OK, 0.151s.
- Full suite baseline: python3 -m unittest discover -s tests -p 'test_*.py',
  running in background, log /tmp/worker-y1-baseline.log. O2's last result
  was 1,523 tests, 0 failures, 2 skipped, 119.885s.

## 17:48 +07 | 00:01 | Part C triage (repo evidence, before any fix)
- Todolist docs/zen-error-fix-todolist-20261121.md items 3.1.1-3.1.8 already
  ticked DONE with evidence commits. Y1 verified each claim in source:
  - C1 observation expiry: OBSERVATION_MAX_AGE=120 enforced in
    scripts/code_exec.py:99,417-426,549,602 and scripts/cu.py:48,745.
    Test: tests/test_phase3_c1.py.
  - C2 stale screenshot after navigation: cu.py _settle_after_capture;
    tests/realistic/run_live.py has post-navigation settle.
    Test: tests/test_phase3_c2.py.
  - C3 Ctrl+T: scripts/cu.py:1408-1438 _refuse_zen_ctrl_t preflight.
    Test: tests/test_phase3_c3.py.
  - C4 Commit Changes location: docs/polygon-upload-runbook.md:82.
  - C5 /problem/<id> 404: docs/polygon-upload-runbook.md:143-144.
  - C6 ydotool ban: scripts/brief_check.py:22 + tests/test_phase3_brief.py.
  - C7 static screen reads as idle: brief_check.py:32 "narrate before acting"
    + docs/brief-template.md sections 5 and 9.
  - C8 cleanup: scripts/session_cleanup.py + tests/test_phase3_cleanup.py.
- Provisional verdict: Part C is fully covered already. Remaining Part 2 work
  is INDEPENDENT VERIFICATION (run the Phase 3 tests myself, confirm each fix
  would fail if regressed) plus fixing any genuine gap the verification finds.
  No Part C fix will be claimed without a failing-before/passing-after test.

## 17:50 +07 | 00:03 | Baseline full suite FAILED on the VM (before wtype)
- python3 -m unittest discover -s tests -p 'test_*.py': Ran 1460 tests in
  174.083s, FAILED (failures=2, errors=69, skipped=16). Log
  /tmp/worker-y1-baseline.log. O2 reported 1523 tests, 0 failures on the
  laptop. Discrepancy investigated, NOT assumed to be a regression:
  - 60+ errors trace to ONE cause: RuntimeError "private wtype helper is
    missing: <repo>/native/wtype" (scripts/cu.py:76-81). The VM never built
    the native helper; the laptop has it (36KB, built 21/11 06:46).
  - 2 failures (test_session_driver FullRestoreEnvelope) are the same cause:
    expected typing error replaced by the missing-helper error.
  - test_cursor_session fails to IMPORT: SyntaxError "too many statically
    nested blocks" at line 566 (33 tests in that file never run). The file is
    unmodified from HEAD; its last change is 0ba9584. The SAME file parses OK
    on the laptop (checked via SSH). Likely a Python-version compiler limit
    difference (VM 3.12.3). This is a REAL defect: a whole module silently
    never runs on the VM. Needs a fix (split the nested with-blocks) or a
    documented VM exclusion. Do NOT silently exclude it.
  - O2's commits 7387b17/4500a18 ARE ancestors of VM HEAD. Laptop HEAD is
    4500a18 (O2's final commit); VM todolist-push HEAD is c1cc7d8 (newer: W
    crawls + Worker X ticks). Test-count delta (1460 vs 1523) is explained by
    the unimportable module (33 tests) plus VM skips (16 vs 2).
- scripts/build.py fails on the VM (needs gtk4-layer-shell-0 + gtk4 dev libs,
  absent here; known VM limitation, Worker J noted it). Built wtype ONLY from
  the build.py recipe: patch main.c, wayland-scanner keyboard.xml, cc with
  wayland-client + xkbcommon. BUILD_OK, binary 35,984 bytes, executes.
  native/wtype is gitignored; generated keyboard-protocol.h/c leave git
  status clean.
- Baseline re-run with wtype present: running in background, log
  /tmp/worker-y1-baseline2.log.

## 17:51 +07 | 00:04 | Council verdicts: UNANIMOUS GO (3/3)
- Council 1 (improvements/worker-y1-council-1.md), Council 2
  (improvements/worker-y1-council-2.md), Council 3
  (improvements/worker-y1-council-3.md). All GO with conditions. Unanimous:
  - Storage: snippets/*.py (one file per snippet) + snippets/manifest.json
    (metadata only, never code strings). JSON code strings REJECTED on the P4
    escaping evidence; data inside code_exec.py REJECTED (880-line sandbox
    file must not mix with data).
  - Executor: scripts/code_exec.py ONLY. codemode.execute_op exposes only 6
    repo.* ops; zero of P1-P4 can run there (windows/observe/act unbound).
    Do NOT extend codemode, do NOT keep two registries.
  - Safety: full AST scan + wall/API/trace budgets + CU_CODE_EXEC gate on
    EVERY run, no trust exemption for promoted snippets. sha256 check on
    load; API-name pre-check (every Name node in allowlist/builtins/params).
  - Schema: name, file, sha256, description, params, source, last_verified,
    verified_against (git commit), expected_result, tags.
  - Verification: tests/test_snippets.py against the existing fake backends
    (tests/test_code_exec.py FakeBackend/FakeShellBackend/FakeTerminalBackend);
    live laptop run required before any last_verified bump. P1-P4 migrate
    first, byte-for-byte; tests stop extracting programs from markdown.
  - run_snippet: top-level code_exec entry through the cu.py gate (CLI
    --snippet flag) AND an allowlisted name inside programs, depth cap 1
    (a snippet may not call run_snippet). Params bound as values, never
    string-substituted. Unknown name returns error + closest matches.
    Search shows one-liners with a stale flag, never full code.
  - Staleness (synthesis): API-stale or hash mismatch = hard refuse.
    Age-stale (>90 days) = refuse by default, allow_stale=True diagnostic
    override only, logged (majority C1+C3; C2's run-with-warning rejected
    as it lets a stale snippet run silently forever).
  - Location: top-level snippets/ (C1+C2 majority; C3's scripts/snippets/
    noted and overruled: registry data belongs at the root, visible).
  - Naming: kebab-case (C2), e.g. p1-disk-free.
- Redteam verdict still pending (no file yet at 17:53).

## 17:56 +07 | 00:09 | Baseline 2 (with wtype built): 1483 tests, 0 failures, 2 errors
- Ran 1483 tests in 147.250s, FAILED (errors=2, skipped=16). Log
  /tmp/worker-y1-baseline2.log. The 69 keyboard errors and 2 failures are
  GONE: all were the missing wtype helper.
- Remaining 2 errors are BOTH VM toolchain gaps, not repo regressions:
  1. test_cursor_file setUpClass: g++ -std=c++26 fails. VM g++ is 13.3.0
     (no C++26 support); laptop g++ is 16.2.1. Environmental.
  2. test_cursor_session import: SyntaxError "too many statically nested
     blocks" line 566. VM Python is 3.12.3; laptop Python is 3.14.10 and
     parses the same file fine. The file is unmodified from HEAD. This is a
     real portability defect (a whole module, 33 tests, never runs on the VM)
     and goes to Codex as a fix task: refactor test_cleanup_exceptions_
     cannot_skip_restore (giant with-chain + nested with) to reduce static
     nesting, behavior identical, verified by Y1 on the VM (import + 33 tests).
- Y1 verified code_exec.py citations directly: allowlist lines 271-275,
  validate_program 331-341, _resolve_read_path /tmp-only. Council citations
  check out.

## 17:57 +07 | 00:10 | Laptop pre-flight for Codex
- Laptop repo at 4500a18 (O2's final commit), untracked files from sibling
  workers only. No Codex process running: Codex is FREE. fcc-server daemon
  and agy Y2 (sibling, generating agy-y2 tests) are running; Codex must work
  on its own branch to avoid git collisions.
- Redteam still running (last activity <1 min ago at check). Codex brief is
  NOT launched until the redteam verdict lands.

## 17:58 +07 | 00:11 | Redteam verdict: BLOCK (all 4 children done)
- Report improvements/worker-y1-redteam.md (774 lines). No full RCE found,
  but 7 attacks, 6 HIGH, all PROVEN with probe runs on the VM:
  1. str.format defeats the dunder ban: "{0.__self__.session_token}".format
     (windows) returned the LIVE session token verbatim in code_exec.
     Fix: remove "format" from SAFE_ATTRIBUTE_NAMES in both files.
  2. Wall-clock/trace budgets do not bind C-level work: sum(range(3*10**8))
     took 7.40s (codemode) / 9.06s with ok=True (code_exec) vs 2s wall.
     50MB string returned in envelope, no result cap.
  3. codemode __codemode_main__ reachable/callable: conditional self-call
     double-executed the body; a yield program returns completed with the
     body never run.
  4. codemode does not pin __builtins__ (latent full escape, one gap away).
  5. Snippet trust: no content hash, name collision, param shadowing,
     exfil via act(), param as format string.
  6. Stale guard dead on laptop: verified_against is a git commit hash but
     the installed copy has no .git; CI never executes live_only snippets;
     P3/P4 asserts pass on leftover /tmp state from a prior run.
  7. Replay/divergence: retried Polygon create/submit duplicates; act()
     without fresh observe acts on another snippet's observation.
  8. Registry poisoning: no manifest size cap, duplicate-name shadowing,
     path traversal, .py files importable (import bypasses the scan),
     cross-snippet variable poisoning (proven).
- Unblock checklist: 12 must-fix (4 executor, 8 snippet-design) + 3
  should-fix-soon (real preemption + memory cap; template assert hygiene;
  search ranking). Council synthesis AMENDED:
  - sha256 in manifest is REQUIRED (council 2 had it; council 3 lacked it).
  - Stale check keyed on runtime-computed hash of the code_exec API
    surface/file bytes, NEVER on a git commit (dead on laptop).
    verified_against stays as audit metadata only.
  - Expiry: 30 days live_only (redteam), 90 days VM-verifiable (council).
  - run_snippet INLINE with shared api_calls/deadline/trace counters
    (nested run() gives 32x32 = 1024 calls, up to 16 min wall).
  - Params: reject allowlist collisions, frame locals, snapshot/restore
    persistent variables. Observation/DOM bindings scoped per snippet run.
  - Manifest: size cap, duplicate-name rejection, per-entry fail-closed
    loading, code_path containment, text-only loading, no __init__.py.
  - Non-idempotent snippets: requires_approval + per-session applied
    ledger so a retry does not blindly re-execute.
  - Registry location stays top-level snippets/ (council majority);
    redteam's scripts/snippets/ paths map to it.
- Codex brief: Phase A executor fixes (redteam 1-4), Phase B registry
  (council synthesis + redteam 5-12), Phase C test_cursor_session.py
  nesting fix, Phase D Part C verification (run Phase 3 tests on laptop),
  Phase E live P1-P4 runs. Codex works in a git worktree from
  origin/todolist-push on branch y1-snippets, pushes there; Y1 verifies
  on the VM, then merges to todolist-push. No direct todolist-push pushes
  until verified.
