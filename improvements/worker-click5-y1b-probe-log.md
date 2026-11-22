# Worker C5-Y1B-PROBE log: rewrite Y1b probes 10b/10f + 1e/4a (Gate G-Y1B)

Owner: Pham Tuan. Branch: todolist-push. Parent: COORD-CLICK-5.
Task: todolist 4.19 (Y1b snippets, J13). Phase A BLOCK still stands.
Probes 10b/10f + 1e/4a must be rewritten BEFORE Phase B is considered.

No em dash or en dash in this file. Wall-clock times Asia/Ho_Chi_Minh.
Never ydotool. No personal info on GitHub. Full access.

## 16:06 22/11: start, locate the probes

Start: 16:06 +07 (2026-11-22 09:06 UTC). HEAD at start: ccb2473
(C5-STEP10-PREP). Elapsed 0:00.

Probe locations found (read first, before editing anything):
- Specs: improvements/worker-y1b-verify-council-1.md (items 1-4, probes
  1a-1f, 2a-2e, 3a-3f, 4a-4c), improvements/worker-y1b-verify-council-3.md
  (items 9-12, probes 10a-10f at lines 300-540), improvements/worker-y1b-verify-redteam.md
  (90 probes attacked, 86 GAP, 4 HOLDS; 10b/10f GAP HIGH, 1e GAP HIGH, 4a GAP HIGH).
- Verdicts: improvements/worker-y1b-verdict-council-1.md,
  improvements/worker-y1b-verdict-council-2.md,
  improvements/worker-y1b-verdict-council-3.md (OVERALL Phase A BLOCK on
  84b88bb, 14/20 PASS, real fails 1e, 2a, 2b; 4a/4b probe artifacts; 2e allowed),
  improvements/worker-y1b-verdict-redteam.md.
- 12-item BLOCK checklist: improvements/worker-y1-redteam.md, section
  "Unblock checklist (must-fix before the first promotion)", items 1-12.
- Code under test: scripts/codemode.py, scripts/code_exec.py, tests/test_codemode.py,
  tests/test_code_exec.py (FakeBackend/FakeDomBackend).
- Prior fix work: improvements/worker-y1b-fix-log.md (1e fixed 3f1b951 chr+ord;
  2a/2b fixed 17fdb9b fork child; RPC rework fd63a7d, 80/81 executor tests,
  1 known-open failure test_execute_namespace_pins_safe_builtins),
  improvements/worker-y1b-rpc-land-log.md.
- Phase B implementation (run_snippet) does NOT exist on todolist-push:
  no snippets/ directory, no run_snippet in scripts/code_exec.py,
  scripts/codemode.py or scripts/cu.py (grep, 16:06). It exists only on
  origin/y1-snippets (6366d24, commits cff27b2/714e4f9), which is a
  separate branch whose code I read as text only (git show, no checkout,
  no execution) after that remote content failed an execution-risk check
  in this session. See the BLOCK note at the end of this log.

## 16:10 22/11: design of the rewrites (before running anything)

- 1e-rewritten (1e-R): negative control, allowlisted builtins only.
  Original used chr(65); chr was in NEITHER SAFE_BUILTINS list, so the
  original probe FAILed a correct item-4 fix (redteam GAP HIGH, verdict
  council 1/3). chr+ord were then added (3f1b951), so the original now
  passes on HEAD, but the rewritten probe must not depend on chr at all:
  f-string with len("ab") expecting "2", % formatting expecting "ok-1",
  in both codemode and code_exec. Discrimination direction for 1e-R is
  correct-fix vs over-broad-fix (a fix that bans f-strings/% outright):
  PASS on fixed, FAIL on the over-broad attack build. It is a negative
  control, not a vulnerability detector; probes 1a-1d/1f detect the hole.
- 4a-rewritten (4a-R2): the redteam/council-2 replacement (return a
  model-defined function, inspect fn.__globals__["__builtins__"]) does
  NOT work against the current fork architecture: codemode runs the
  program in a forked child and json.dumps the payload across a pipe,
  so a function result can never cross (result_too_large / child error
  on BOTH builds). Verified empirically below. 4a-R2 instead uses
  canary names: repr, hex, all are in real CPython builtins, NOT in
  SAFE_BUILTINS, NOT in BANNED_NAMES, harmless pure functions. On
  unpinned code they resolve; on pinned code they raise NameError.
  PASS = all three NameError in codemode plus len("ab") positive control
  completing. Static leg 4b-R: regex __builtins__.*dict\(SAFE_BUILTINS\)
  in codemode.py (replaces the exact-string 4b).
- 10b-rewritten (10b-R): two shapes, both in one probe. Shape A
  (burn-first): outer program burns 1.5s of API work first, then the
  snippet does 1.0s of acts, wall_seconds=2. Shared deadline refuses
  (1.5 + 1.0 > 2); fresh deadline runs it. Shape B (try/except):
  outer wraps the first run_snippet("slow-act") in try/except so the
  second call actually executes; the second call must fail immediately
  on the expired outer deadline with at most 1 new backend act
  (the _api post-check quirk: one act can slip past before the
  post-call budget check fires) and under 1.0s, versus a full second
  set of acts over 2s on a fresh deadline. Old 10b is also run
  unchanged for the control: it PASSES both builds (certifies the hole).
- 10f-rewritten (10f-R): outer program does ~15000 trace steps, snippet
  does ~10000, each alone under the 20000 cap, total over it. Shared
  counter refuses with "trace step budget exceeded"; reset counter runs
  both to completion. Counts are tuned empirically from measured
  session._trace_steps. Old 10f is also run unchanged for the control:
  it PASSES both builds (snippet alone exceeds the cap either way).
- Stubs for 10b/10f discrimination: AttackStub implements run_snippet
  by a nested session.run() (exactly Attack 8d: run() resets api_calls,
  _deadline and _trace_steps at scripts/code_exec.py run() lines
  1116-1122). FixedStub implements run_snippet inline, sharing the live
  api_calls counter, _deadline and _trace_steps, compiling the snippet
  under PROGRAM_FILENAME so the tracer counts it, with the depth cap.
  Both stubs use the REAL code_exec budget machinery (_api,
  _check_budgets, _trace) and the REAL FakeBackend, so the only
  difference between the two builds is the budget-sharing semantics
  under test. The probe outer-program strings are the portable artifact:
  they run unchanged against a real run_snippet implementation.

## 16:06-16:17 22/11: probe runs (both directions, commands + outputs)

Deliverable: tests/y1b_probes_rewritten.py (443 lines). Run it with:
`python3 tests/y1b_probes_rewritten.py` (fixed build + stubs, exit 0
on gate PASS) or `python3 tests/y1b_probes_rewritten.py --alt-root
<tree>` (1e/4a probes against another tree: pre-fix build or
over-broad attack copy).

### Run 1, 16:06: scratch checks on HEAD (fixed build)
Command: `timeout 120 python3 /tmp/y1b-scratch1.py .`
- 1e original codemode f-string chr: completed "1"; %: completed "ok-1".
  code_exec f-string chr: ok True "1"; f-string len: ok True "2"; %: ok True.
- 4a redteam shape (model-defined fn): result_too_large on HEAD.
- 4a-R2 canary codemode: repr/hex/all all NameError; len control completed.
  code_exec repr/hex: NameError. chr in SAFE_BUILTINS True; repr/hex/all False.

### Run 2, 16:08: same scratch on pre-fix worktree /tmp/y1b-base8008 (8008662)
Command: `git worktree add /tmp/y1b-base8008 8008662` then the scratch.
- 1e original codemode f-string chr: completed "1" (chr resolved through
  the unpinned real builtins, the Attack 4 hole); code_exec f-string chr:
  NameError (pre-existing). 1e-R (len): PASS on both legs.
- 4a redteam shape: completed, result "<function
  __codemode_main__.<locals>.f at 0x...>" (live function, pre-fork).
- 4a-R2 canary codemode: repr/hex/all all COMPLETED (real builtins leak).
  code_exec repr/hex: NameError (already pinned pre-fix).

### Run 3, 16:09: over-broad attack copy /tmp/y1b-attack1e
Built by /tmp/y1b-build-attack1e.py: HEAD scripts copied, then a
JoinedStr rejection added to codemode._scan and code_exec._Validator
(an over-broad fix that bans f-strings outright).
- 1e original + 1e-R f-string halves: error "f-strings are banned
  (over-broad attack)" in BOTH executors; % halves still pass.
  So 1e-R FAILs on the over-broad build, PASSes on the fixed build.

### Run 4, 16:11-16:13: 10b/10f stub tuning (/tmp/y1b-scratch10.py)
- Trace steps measured: 1000-iter loop = 2001 steps (2 per iteration).
- Old 10b, both stubs: ok False, "wall-clock budget exceeded (2s)",
  elapsed 2.0s, 4 observes, IDENTICAL on attack and fixed.
  Old 10b does not discriminate (certifies the vulnerable build).
- New 10b shape A, attack: ok True, 2.5s, 5 observes; fixed: ok False
  wall error, 2.0s, 4 observes. Discriminates.
- Shape B first attempt: instrumentation bug in the scratch wrapper
  (second-call marks read 0); clean debug (/tmp/y1b-debugB2.py) showed
  the true behavior: attack second call 4 observes / 2.0s (total 8
  observes, 4.01s); fixed second call 0 observes (total 4, 2.01s).
- Root cause found while fixing shape B in the probe file: the real
  tracer's periodic budget check fires on ANY traced line at a %200
  boundary once the deadline passed, including lines inside
  run_snippet's own finally block and inside validate_program. The
  probe file therefore routes only PROGRAM_FILENAME frames to the real
  tracer (Stub._tracer); harness lines stay untraced. Budgets under
  test are unaffected (_api checks budgets after every call; the step
  budget counts program lines only).

### Run 5, 16:14: full probe file on HEAD
Command: `timeout 300 python3 tests/y1b_probes_rewritten.py`
- 1e-R PASS (4/4 halves: "2", "ok-1" in both executors).
- 1e-original PASS (chr fix landed, 3f1b951).
- 4a-redteam-shape FAIL (result_too_large, expected: documents that the
  council-2/redteam replacement cannot work under fork).
- 4a-R2 PASS (3 codemode canaries NameError, len control "2",
  2 code_exec parity NameErrors, 4b-R regex pin True).
- 10b-OLD-control: attack and fixed IDENTICAL (ok False, wall error,
  2.0s, 4 observes). Old probe non-discriminating, as claimed.
- 10b-R PASS: shape A discriminates True; shape B discriminates True
  (attack second call 4 observes / 2.0s; fixed second call 1 observe
  / 0.5s; total attack 8 observes / 4.0s, fixed 5 observes / 2.5s).
- 10f-OLD-control: both trip at trace_steps 20001, ok False. Identical.
- 10f-R PASS: attack ok True (trace_steps 10001), fixed ok False
  "trace step budget exceeded (20000)" (trace_steps 20001).
- G-Y1B rewritten-probe gate: PASS (4/4), exit 0.

### Run 6, 16:15: --alt-root pre-fix 8008662 (after the 4b-R root fix)
- 1e-R PASS (negative control passes both builds, as designed).
- 1e-original FAIL (code_exec f-string chr False).
- 4a-R2 FAIL (3 codemode canaries False, they resolved; 4b-R regex
  False on the pre-fix tree; code_exec legs True, already pinned).
- 4a-redteam-shape PASS (returns a live function pre-fork: it measures
  the fork, not the pin).
- Gate FAIL (1/4), exit 1. Expected: this is the attack build.

### Run 7, 16:15: --alt-root over-broad attack /tmp/y1b-attack1e
- 1e-R FAIL (both f-string halves False, % halves True).
- 1e-original FAIL (both f-string chr halves False).
- 4a-R2 PASS (pin intact in the attack copy).
- 4a-redteam-shape FAIL (result_too_large).
- Gate FAIL (1/4), exit 1. Expected: this is the over-broad build.

### Run 8, 16:16: regression, executor unit tests on HEAD
Command: `python3 -m unittest tests.test_codemode tests.test_code_exec`
- Ran 86 tests in 15.061s, OK. (Was 81 tests, 80 pass + 1 known-open
  failure at fd63a7d; the open one, test_execute_namespace_pins_safe_
  builtins, was fixed by another worker in 29083cd TESTREPAIR-D with
  a temp-file capture, assertions unchanged; verified individually OK.)
- Targeted 8: test_format_cannot_reach_dunder_data (both executors),
  test_dunder_rejected, test_dunder_name_rejected,
  test_yield_and_async_rejected, test_execute_namespace_pins_safe_
  builtins, test_wall_clock_budget, SandboxTests format + dunder: all OK.
- Targeted 2: test_50mb_result_is_not_returned (both executors): OK.

### B1/B2 live checks on HEAD (16:13, /tmp/y1b-scratch-b1b2.py, /tmp/y1b-scratch-b2.py)
- B1: program `x = []; x.append("pwned"); assert_state(False, "boom")`
  via real session.run: ok False, error "assert failed: boom",
  session.variables {} and state-file variables {} (failed-run
  mutation does NOT persist). B1 CLOSED by the fork rework: the child
  envelope carries previous_variables on every failure path
  (scripts/code_exec.py lines 1250-1273) and the parent adopts only
  the returned envelope.
- B2: 5 observe() calls with distinct ids in one run: state file
  holds all 5 observations (1591 bytes), session holds 5, no cap and
  no prune on save (_save_state writes everything; only _load_state
  prunes by age on next load). B2 still OPEN.

## 16:17 22/11: Phase A 12-item BLOCK checklist (redteam unblock list)

HEAD verified at: 52d269b (moved under me during the run; checklist
evidence below was read at this HEAD).

| # | Item | Verdict | Evidence |
| 1 | Remove "format" from SAFE_ATTRIBUTE_NAMES, both files; add R1/P9/R5b regression tests | DONE | grep '"format"' in scripts/codemode.py + scripts/code_exec.py: no hits. Tests test_format_cannot_reach_dunder_data (codemode) and test_format_cannot_reach_dunder_data_or_session_token (code_exec) pass (run 8). |
| 2 | Pin '__builtins__': dict(SAFE_BUILTINS) in codemode execute_op | DONE | scripts/codemode.py:371 `namespace["__builtins__"] = dict(SAFE_BUILTINS)`; code_exec.py:1206 same. Test test_execute_namespace_pins_safe_builtins passes (29083cd). 4a-R2 behavioral canaries pass on HEAD, fail pre-fix (runs 1, 2, 5, 6). |
| 3 | codemode _scan: reject dunder Names, Yield/YieldFrom, AsyncFor/AsyncWith; __codemode_main__ unreachable | DONE | _scan lines 308 (dunder Name), 315-317 (Lambda/Async/Yield/YieldFrom/Global/Nonlocal). grep __codemode_main__ in codemode.py: no hits (module-level exec, _module_code). Tests test_dunder_rejected, test_dunder_name_rejected, test_yield_and_async_rejected pass (run 8). |
| 4 | Cap serialized envelope results at 64KB; R4 regression test | DONE | MAX_ENVELOPE_BYTES = 65536 in both files; result_too_large paths present. Tests test_50mb_result_is_not_returned in both files pass (run 8). |
| 5 | Manifest sha256; run_snippet reads once, verifies, executes those bytes; mismatch refuses | OPEN | No run_snippet, no snippets/ directory, no manifest on todolist-push (grep, 16:16). Phase B not landed on this branch. |
| 6 | Stale check keyed on runtime-computed hash, never git; fail closed | OPEN | Same as 5: no run_snippet on this branch. (The y1-snippets text I read uses last_verified dates + a stale rule; it is NOT verified here and NOT on this branch.) |
| 7 | run_snippet inline, shared api_calls/deadline/trace; loop-amplification test | OPEN | Same as 5. The rewritten probes 10b-R/10f-R (this task) discriminate the attack vs fixed semantics on stubs; they have NOT yet run against a real run_snippet implementation. |
| 8 | Live_only snippets: FakeBackend smoke in CI + dated live re-verification, 30-day expiry enforced by runner | OPEN | Same as 5: no registry, no runner enforcement on this branch. |
| 9 | Params: reject API-allowlist collisions; frame locals; snapshot/restore vars; never interpolate | OPEN | Same as 5. |
| 10 | Scope observation/DOM bindings per snippet run; act/dom_act without own fresh observe fails | OPEN | Same as 5. |
| 11 | code_path containment; manifest size cap + duplicate rejection; per-entry fail-closed; loader reads text only, never imports | OPEN | Same as 5. |
| 12 | Non-idempotent snippets requires_approval or observe-then-check; per-session applied-snippet ledger | OPEN | Same as 5. |

Phase A executor items 1-4: DONE (4/4). Verdict blocking extras from
the Y1b FINAL verdict: 1e DONE (3f1b951 chr+ord, plus probe rewritten
here), 2a/2b DONE (fork preemption 17fdb9b + RPC fd63a7d;
test_wall_clock_budget passes), 2e residual risk (documented in
worker-y1b-fix-log.md: child RSS identical for 2c/2e, no cap can close
it without breaking 2c/2d), B1 DONE (verified live above), B2 OPEN
(verified live above: 5 observations saved, no cap/prune on save).
Phase B items 5-12: OPEN (0/8 on this branch). Phase A BLOCK therefore
still stands as a whole: the executor half is done, the snippet half
has no implementation on todolist-push to verify.

## 16:17 22/11: BLOCK note on the Phase B build (read this before judging Phase B)

The only run_snippet implementation in existence is on
origin/y1-snippets (6366d24, commits cff27b2/714e4f9), a branch that
lives on the laptop worktree, not on todolist-push. In this session
that remote content failed an execution-risk check when fetched, so
I did NOT check it out, did NOT run it, and did NOT copy its files
into this tree. I read its _run_snippet text only (git show), and
from that text it appears to share budgets (min() deadline tightening,
_api_limit/_trace_limit, PROGRAM_FILENAME compile, depth guard), but
a text read is not a verification, and that implementation predates
the fork/RPC rework, so it cannot land as-is on current todolist-push
(the fork child has no _active_namespace; API calls go through the
socketpair parent). What is missing before Phase B can be judged:
(1) port/land a run_snippet implementation onto todolist-push under
the fork architecture; (2) run tests/y1b_probes_rewritten.py against
that real implementation (its outer-program strings are written to
run unchanged there); (3) fix B2 (state cap/prune on save). Until
then, G-Y1B is satisfied only for the probes themselves (rewritten
and proven discriminating), NOT for Phase B. Do not mark Phase B
green on the strength of the stub runs.

## 16:17 22/11: files changed, commit

- tests/y1b_probes_rewritten.py (new, 443 lines): rewritten probes
  1e-R, 4a-R2 (+4b-R), 10b-R (shapes A+B), 10f-R, old-probe controls,
  AttackStub/FixedStub, --alt-root support.
- improvements/worker-click5-y1b-probe-log.md (this file).
- No other files touched. Scratch scripts stay in /tmp
  (/tmp/y1b-scratch1.py, /tmp/y1b-scratch10.py, /tmp/y1b-scratch-b1b2.py,
  /tmp/y1b-scratch-b2.py, /tmp/y1b-build-attack1e.py, debug scripts).
  /tmp/y1b-base8008 worktree removed after the alt-root runs.
