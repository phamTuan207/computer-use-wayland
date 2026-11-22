# Worker C5-Y1B-PHASEB log: port run_snippet onto todolist-push (fork architecture) + B2 fix

Owner: Pham Tuan. Branch: todolist-push. Parent: COORD-CLICK-5.
Task: Phase B items 5-12 (run_snippet), rewritten-probe gate on the real
implementation, B2 cap/prune on observation save, regression suite.

No em dash or en dash in this file. Wall-clock times Asia/Ho_Chi_Minh.
Never ydotool. No personal info on GitHub. Full access.

## 16:19 22/11: start

Start: 16:19 +07 (2026-11-22 09:19 UTC). HEAD at start: 561da54
(C5-Y1B probe rewrite, G-Y1B gate PASS 4/4 on stubs). Elapsed 0:00.

Read first, before writing anything:
- improvements/worker-click5-y1b-probe-log.md (full): probe rewrites,
  stub semantics, B1 DONE / B2 OPEN live evidence, Phase A 1-4 DONE,
  Phase B 5-12 OPEN (0/8), BLOCK note on origin/y1-snippets.
- tests/y1b_probes_rewritten.py (443 lines): OUTER_10B_A/B/OLD,
  OUTER_10F/OLD, SNIPPET_SLOW2/SLOW6/MANY/MANY_OLD, AttackStub/FixedStub.
- scripts/code_exec.py (1335 lines, HEAD): fork/RPC rework, run() forks
  a child per program, API calls marshal to the parent over a socketpair,
  parent holds variables/observations/dom_snapshots/api_calls/_deadline.
- scripts/codemode.py (453 lines): separate executor, no snippet API.
- improvements/worker-y1-redteam.md items 5-12 (the Phase B spec) and
  improvements/worker-y1b-verify-council-3.md probes 10a-10f, 11a-11h,
  12a-12b (the contract the port must satisfy).

## 16:25 22/11: risk assessment (recorded BEFORE writing any port code)

The only existing run_snippet implementation lives on origin/y1-snippets
(6366d24). That remote content FAILED an execution-risk check when fetched
in the probe session, so the probe worker did not check it out, run it, or
copy it. My handling, and my own assessment:

1. I read that branch as TEXT ONLY, via `git show origin/y1-snippets:path`
   piped through sed/grep (read-only plumbing, no execution, no checkout,
   no file copies). I read its code_exec.py _run_snippet and registry
   loader text, its manifest.json, one snippet file (p1-disk-free.py), and
   its test names. Nothing from that branch was executed, checked out, or
   copied into this tree. Its snippet programs (which type commands into a
   live terminal) were NOT copied: the shipped registry starts with one
   fresh trivial snippet I write myself, and all probe fixtures are built
   by my own harness.
2. The old text is UNTRUSTED design reference only, not a base to patch.
   It predates the fork/RPC rework and cannot land as-is: it executed
   snippets in-process against self._active_namespace with self._deadline
   / self._api_limit / self._trace_limit mutated in place, but on current
   todolist-push there is no _active_namespace in the parent (the program
   runs in a forked child; API calls go through the socketpair parent).
   I port by writing FRESH code under the fork architecture, informed by
   the text read. The authority for behavior is the in-repo checklist
   (redteam items 5-12) plus the rewritten probes, not the old text.
3. Design flaws in the old text that I will NOT carry over (each is a
   deliberate, documented deviation):
   a. verified_against (a git commit hash) as the staleness key. Item 6
      forbids git-keyed staleness. My port requires api_sha256 per entry:
      sha256 of the code_exec.py file bytes, computed at runtime at
      verification time and recomputed at run time. Mismatch means stale.
      Fail closed when the hash cannot be computed.
   b. _check_snippet_api_names rejecting any snippet name outside
      SAFE_BUILTINS plus API plus params plus snippet locals. That rejects
      a snippet reading an outer-program variable, which probe 10e
      REQUIRES (snippet sees outer variables). Dropped as a rejection; the
      AST scan plus restricted builtins plus manifest param-collision
      rejection already bound the name space, and the snippet executes
      with the live namespace as globals, so reads work and writes land
      in frame locals.
   c. Ledger recording FAILED applications. That blocks retry after a
      transient failure and changes probe 10b-R shape B (the second call
      must re-attempt and fail on the wall, not on the ledger). My port
      records only successful applications, matching the CDP intent ledger
      precedent in this same file (record only verified sends).
   d. Per-entry budget tightening (wall_seconds / max_api_calls /
      max_trace_steps in the manifest). Not in checklist items 5-12; the
      fork port enforces the SHARED outer budgets (item 7) as the binding
      constraint. Manifest entries declaring those fields are rejected at
      load (unknown field, entry skipped, fail-closed).
   e. Registry location: the old branch used repo-root snippets/. Item 11
      says containment under scripts/snippets/. My port uses
      scripts/snippets/ (SNIPPET_ROOT next to code_exec.py).
4. Execution risk of MY port, and how it is bounded:
   - Parent side (trusted): manifest loader reads files with O_NOFOLLOW,
     regular-file check, 1MB manifest cap, 128-entry cap, duplicate-name
     rejection, per-entry fail-closed validation, path containment
     (resolve plus prefix check, .py only, no .., no absolute). The loader
     reads TEXT ONLY and never imports snippet files. Hash verification
     (sha256 of file bytes) happens in the parent before any source is
     handed to the child.
   - Child side (model code): the snippet is AST-validated again in the
     child, compiled under PROGRAM_FILENAME so the tracer counts its
     lines, executed with restricted builtins, the live namespace as
     globals (deep-copied variables, so in-place mutation cannot leak),
     and params as frame locals. API calls marshal to the parent, so the
     shared api_calls counter, the shared deadline, and the shared trace
     counter all apply. The child is killed at the outer wall by the
     parent. Depth cap 1, enforced by a child-side counter.
   - Per-run binding scoping (item 10) is enforced in the PARENT via a
     snippet-run tag carried on every API request: observations and DOM
     snapshots record the run id that created them, and act/dom_act refuse
     an id from another run.
5. Residual risk, stated plainly: the AST scan plus restricted builtins is
   NOT a true isolate (redteam residual-risk note). A future allowlist
   addition could reopen a hole the scan cannot see. The port does not
   widen any allowlist: run_snippet is the only new program-visible name,
   and it resolves to a stub that can only fetch hash-verified registry
   bytes. No new builtin, attribute, or import path is opened.

## 16:26 22/11: port design (fork-native, fresh code)

Registry (items 5, 6, 11):
- scripts/snippets/manifest.json plus scripts/snippets/*.py. Loader:
  load_snippet_manifest(root=None), _validate_snippet_entry,
  _resolve_snippet_path, _read_snippet_once (read once, sha256-verify,
  execute those bytes; mismatch refuses). Duplicate JSON keys rejected,
  duplicate snippet names fail the whole load, invalid entries skipped
  with a warning log. Entry required fields: name, file, sha256,
  description, params, source, last_verified, api_sha256,
  expected_result, tags. Optional: requires_approval, live_only, output.
  Param names colliding with the API allowlist are rejected at load
  (item 9/11a). Snippet names colliding with API names or codemode op
  paths are rejected at load (op paths read from codemode.py by AST text
  read, never imported).
- Stale (items 6, 12): age from last_verified (live_only 30 days, else
  90 days) AND api_sha256 mismatch against the runtime-computed hash of
  code_exec.py bytes. Either stale means refuse, unless allow_stale=True
  (diagnostic only, logged). search_snippets() excludes stale entries;
  describe_snippet(name) returns metadata without code.

Execution (item 7):
- Outer program calls run_snippet(name, allow_stale=False, **params).
  The child namespace carries a dedicated stub (not a plain API stub):
  it checks the depth cap, fetches the verified source from the parent
  over the existing API channel (one api call, through _api, so it costs
  budget), then execs the source INLINE in the child under the live
  tracer (PROGRAM_FILENAME compile, shared _trace_steps in the child
  copy, shared _deadline copy, shared api_calls in the parent).
  No nested run(), no nested session (probe 10d tripwire covers this).
- Params (item 9): validated in the parent against the manifest entry
  (unknown params rejected, required params enforced, types checked,
  JSON-only). Bound as frame locals in the child; never interpolated
  into source (item 11h). The snippet globals are a deep copy of the
  live namespace, so snippet rebindings and in-place mutations cannot
  leak; only the declared output (if any) is copied back into the live
  namespace (item 11d). Params never persist (item 11c).
- Ledger (item 12): parent-side applied_snippets dict, keyed by
  name plus params hash. Checked at fetch time. Recorded only on
  success: the child reports back over the channel after a successful
  snippet exec (a dedicated record message, no budget charge). A failed
  snippet is not recorded, so a retry is allowed.
- Scoping (item 10): every API request carries the child-side snippet
  run id (0 for the outer program, fresh id per snippet call). The
  parent records the run id on each observation and DOM snapshot and
  refuses act/dom_act against an id from another run (including the
  outer program's ids and a previous snippet's ids).
- Top-level entry: run_snippet_program(name, ...) runs one registry
  snippet as a program (via run() with a generated run_snippet call),
  with an approved flag for requires_approval snippets.

B2 fix (separate change, same landing):
- Cap observations kept in the state file: MAX_OBSERVATIONS = 32 (equals
  MAX_API_CALLS, the most one run can add). _save_state prunes to the
  32 newest by created, in memory and on disk. Same cap applied to DOM
  snapshots (MAX_DOM_SNAPSHOTS = 32), the identical hazard in the same
  function. Probe evidence to beat: 5 observations, 1591 bytes, no cap.

Tests (fresh files, no copies from the untrusted branch):
- tests/test_snippets.py: manifest loader, hash mismatch, path
  containment, param collisions, stale boundaries, ledger, depth cap,
  shared budgets (10a), inline namespace (10e), snapshot/restore
  (11c/11d), binding scoping (11e/11g), param injection (11h),
  no-nested-run tripwire (10d), search/describe, B2 cap.
- tests/y1b_phaseb_real_run.py: runs the probe file's OUTER strings
  unchanged (OUTER_10B_A/B/OLD, OUTER_10F/OLD) against the REAL
  run_snippet with fixture manifests built at runtime (api_sha256
  computed from the current code_exec.py bytes), SleepingBackend for
  wall timing. Asserts FixedStub-like outcomes. Exit 0 on gate PASS.

## 16:26-16:34 22/11: implementation record (deviations from the old text)

Deviations, all deliberate, all recorded here (see the risk assessment
for the reasons):
- (a) verified_against (git commit) replaced by api_sha256 (runtime
  hash of code_exec.py bytes) as a required manifest field, per item 6.
- (b) _check_snippet_api_names unknown-name rejection dropped: it
  contradicts probe 10e (snippet reads outer variables). AST scan plus
  restricted builtins plus manifest param-collision rejection bound the
  name space instead.
- (c) Ledger records successful applications only, never failures, so a
  failed snippet can be retried (CDP ledger precedent in the same file;
  probe 10b-R shape B re-attempts after a wall failure).
- (d) Per-entry budget caps (wall_seconds / max_api_calls /
  max_trace_steps) not supported in the fork port: the shared outer
  budgets are the binding constraint (item 7). Entries declaring those
  fields are rejected at load (unknown field, entry skipped).
- (e) Registry at scripts/snippets/ per item 11, not repo-root snippets/
  as on the untrusted branch.
- (f) Ledger scoped to requires_approval (non-idempotent) snippets
  only. A blanket ledger blocks deliberate repetition of an idempotent
  snippet and breaks probe 10a (the same snippet called 5 times in a
  loop must trip the API budget, not the ledger). Found live at 16:30:
  the first smoke run showed the second run_snippet("two-windows") call
  refused by the ledger; after scoping, 10a passes with exact
  accounting (5 fetches + 10 windows would be 15, budget trips at 6,
  backend served 4 windows calls, session api_calls 6).
- (g) The shipped registry holds one fresh snippet I wrote
  (two-windows, two lines) plus its manifest entry. No snippet file was
  copied from the untrusted branch.

## 16:30-16:33 22/11: failures found by the tests (evidence, cause, fix)

Failure 1 (16:31, tests/test_snippets.py first run, 34/35):
test_observation_bindings_scoped_per_snippet FAIL at line 410:
"'not bound to this snippet run' not found in 'action 0 is missing
scope: scope is mandatory in action data (CB-2)'". Cause, two gaps in
my port: (i) _bound_observation(None) returned the newest observation
without any run-id check, so a snippet calling act() with no argument
reached CB-2 validation on the outer program's observation; (ii) the
child-side snippet run id was a 0/1 toggle (increment then decrement),
so sequential snippets shared id 1 and the second could act on the
first's observation (probe 11g). Fix: (i) the None fallback now binds
to the newest observation from THIS run only, and refuses with the
per-run binding error when none exists; (ii) run ids now come from a
monotonic counter that never reuses an id. Re-run: 35/35 OK.
This failure, its cause, and its fix are recorded here in full so an
independent reviewer can re-check the two changed hunks; the fix was
verified by the same tests that caught it, not by assertion alone.

Failure 2 (16:31, same run): test_shipped_registry_loads_and_smoke_runs
FAIL with "snippet is stale: two-windows ... age=0 days". Cause: the
manifest api_sha256 was computed before my code_exec.py edits, and the
fail-closed hash check refused the shipped entry. This is the item-6
mechanism working as designed, not a bug. Fix: recompute api_sha256
after code_exec.py is final (done at 16:34, hash f85ee4a7...).

## 16:33 22/11: verification runs (commands + outputs)

Run 1, 16:33: `timeout 300 python3 -m unittest tests.test_snippets`
- Ran 35 tests in 2.076s, OK. (After the two fixes above.)

Run 2, 16:33: `timeout 300 python3 tests/y1b_probes_rewritten.py`
- G-Y1B rewritten-probe gate: PASS (4/4), exit 0. Old 10b/10f controls
  still non-discriminating as documented (attack and fixed identical).

Run 3, 16:33: `timeout 300 python3 tests/y1b_phaseb_real_run.py`
- G-Y1B real-implementation gate: PASS (4/4), exit 0.
- 1e-R PASS, 4a-R2 PASS (directly against the real modules).
- 10b-R shape A: real refuses (ok False, wall-clock error, 2031ms,
  api_calls 5) vs attack ok True (2.5s, 5 observes). Shape B: real
  4 observes in 2.03s vs attack 8 observes in 4.0s.
- 10f-R: real refuses (trace step budget exceeded, api_calls 1) vs
  attack ok True.
- Old controls on the real impl: old 10b wall error on the first call,
  second never runs (4 observes, 2.03s); old 10f snippet alone trips
  the trace cap.

Run 4, 16:34: `timeout 300 python3 -m unittest tests.test_codemode tests.test_code_exec`
- Ran 86 tests in 14.183s, OK. (Same count as the probe session baseline.)

B2 live proof (test_observation_cap_on_save, in run 1):
- 40 observes across two runs (DistinctIdBackend), state file holds 32
  observations (obs-0009 through obs-0040), oldest 8 pruned, in memory
  and on disk. DOM snapshots capped the same way (40 injected, 32 kept).
- Probe baseline beaten: 5 observations, 1591 bytes, no cap (probe log).

Hash verification (16:34):
- code_exec.py sha256 f85ee4a779241cc68f9abf3d65189f1bbfb167363caaffa8b791ae7cce852f19
  equals the manifest api_sha256. two-windows.py sha256
  316c66eb2709940ceaa0ca23875d5f62cad63a4362892cb50b0f575d7947cdb3 equals
  the manifest sha256.

## 16:34 22/11: Phase B checklist (redteam items 5-12)

| # | Item | Verdict | Evidence |
| 5 | Manifest sha256; run_snippet reads once, verifies, executes those bytes; mismatch refuses | DONE | _read_snippet_once + hash test (refuses before any backend call) |
| 6 | Stale check keyed on runtime-computed hash, never git; fail closed | DONE | api_sha256 (sha256 of code_exec.py bytes); mismatch refuses; hash-uncomputable refuses; live proof: manifest went stale on my own edit at 16:31 |
| 7 | run_snippet inline, shared api_calls/deadline/trace; loop-amplification test | DONE | Real-run gate 10b-R/10f-R PASS; 10a PASS (budget trips at 6, backend 4 windows) |
| 8 | Live_only: FakeBackend smoke in CI + dated live re-verification, 30-day expiry enforced by runner | DONE (mechanism) | 30-day expiry enforced (12a test: 29d runs, 31d refuses + leaves search); FakeBackend smoke is tests/test_snippets.py; no live_only snippet shipped, so no live re-verification exists yet |
| 9 | Params: reject API-allowlist collisions; frame locals; snapshot/restore vars; never interpolate | DONE | Load-time collision rejection; frame locals (11c); snapshot/restore + declared output (11d); injection stays data (11h) |
| 10 | Scope observation/DOM bindings per snippet run; act/dom_act without own fresh observe fails | DONE | 11e/11f/11g tests pass, including the two gaps found live (None fallback + unique run ids) |
| 11 | code_path containment; manifest size cap + duplicate rejection; per-entry fail-closed; loader reads text only, never imports | DONE | scripts/snippets/ containment; 1MB + 128-entry caps; duplicate names fail all; bad entries skipped; traversal rejected |
| 12 | Non-idempotent snippets requires_approval or observe-then-check; per-session applied-snippet ledger | DONE | Approval gate + ledger scoped to requires_approval; retry after failure allowed (recorded on success only); 30/90-day boundaries (12a/12b) |

Phase B items 5-12: DONE (8/8) on todolist-push, verified against the
real implementation, not stubs. B2 DONE (cap 32, proved live).
Regression 86/86 OK. Known gaps, stated plainly: per-entry budget
tightening is not enforced (deviation d); the AST scan is not a true
isolate (redteam residual risk, unchanged); no live_only snippet is
shipped, so item 8's live re-verification path has no live entry yet.

## 16:34 22/11: files changed, commit

- scripts/code_exec.py (modified): registry loader, api_run_snippet
  (parent fetch), child run_snippet stub, per-run binding scoping,
  ledger, search/describe, run_snippet_program, B2 cap.
- scripts/snippets/manifest.json (new): one entry, two-windows.
- scripts/snippets/two-windows.py (new): fresh two-line snippet.
- tests/test_snippets.py (new): 35 tests.
- tests/y1b_phaseb_real_run.py (new): real-implementation gate runner.
- improvements/worker-click5-y1b-phaseb-log.md (this file).
- No other files touched. The tree holds unrelated modified files from
  other workers; the commit below uses an explicit pathspec with only
  the six files above.
