# Council Member 1 verdict: Code Mode snippets registry design

Date: 2026-11-21. Council: Worker Y1 council, Member 1.
Scope: DESIGN ONLY. No implementation.
Branch: todolist-push, repo ~/workspace/computer-use-wayland.
Sources read: docs/research/2026-11-21-code-mode-integration.md (Worker N),
scripts/codemode.py, scripts/code_exec.py, improvements/pick1-program-template.md.

## The deciding fact

The Pick 1 template programs P1-P4 call the code_exec API only:
`windows()`, `observe()`, `act()`, `assert_state()`,
`assert_file_exists()`, `assert_file_contains()`
(improvements/pick1-program-template.md lines 15-25 for P1, 27-37 for P2,
39-54 for P3, 56-71 for P4; shape rule lines 7-13).
That API is allowlisted in scripts/code_exec.py lines 271-275 and
implemented as CodeExecSession methods lines 511-800.

scripts/codemode.py exposes none of it. Its OPS registry
(lines 130-167) has exactly 6 ops: repo.list_scripts, repo.script_info,
repo.py_compile, repo.read_file, zen.locate, overlay.status. Its
execute_op namespace (lines 241-244) binds only those repo_* names.
A P1-P4 snippet executed by codemode.execute_op would fail with an
unbound name. Any design that puts snippets in codemode makes the first
entries dead code on arrival. That single fact decides question 2, and
it constrains questions 1, 4 and 5.

## 1. WHERE does the snippets registry live

Recommendation: (b) a snippets/ directory of .py files plus a manifest.
Concrete shape: top-level `snippets/` at the repo root, one file per
snippet (for example `snippets/p1_disk_check.py`), plus
`snippets/manifest.json` holding metadata only, never code strings.

Reasons:

- Editability. Snippets are real Python files: syntax highlighting,
  `py_compile`, editor support, and normal review diffs. Option (a),
  JSON with code as strings, fails exactly where this repo already
  hurts: P4's program needs literal backslash-n inside a single-quoted
  printf argument, and the template spends lines 73-82 explaining the
  escaping (two backslashes then n in the file, one at the end). JSON
  would add another escaping layer on top of that, and a one-character
  escaping slip changes shell behavior silently. Option (c), data inside
  scripts/code_exec.py, mixes registry data with safety-critical
  sandbox code in a file that is already 880 lines; every snippet edit
  would touch the file whose AST validator and budget guards must stay
  stable, and review of a snippet change could not be separated from
  review of the runner.
- Versioning. One file per snippet gives clean git history per snippet
  (added, fixed, retired) and clean blame. The manifest diff shows only
  metadata changes. A JSON blob with code strings would show whole
  programs as changed lines on any reformat.
- Testability. A .py file can be loaded and run by the test harness
  directly, and compiled by the same py_compile path codemode already
  uses (scripts/codemode.py lines 105-114). A JSON string first has to
  be extracted before any of that works.
- The manifest stays JSON because it holds metadata only: name, file,
  description, params, source, last_verified, expected_result,
  api_version. No code in the manifest means no escaping problem there.

Condition: the manifest is the single index. No snippet is runnable
unless it is listed in the manifest, and no manifest entry may point at
a file outside snippets/. The loader enforces both.

## 2. WHICH executor runs snippets

Recommendation: scripts/code_exec.py. Merge the registry into
code_exec; do NOT run snippets in codemode.execute_op, do NOT extend
codemode with the code_exec API, and do NOT keep two registries.

Reasons:

- Merge into code_exec is the only option under which the first
  entries run. code_exec already has the backend, the cancel latch
  (check_cancel before every API call, scripts/code_exec.py lines
  13-16 and 460), the 120s observation and DOM snapshot bindings
  (lines 99, 417, 426, 549), the dom_start Chromium window wait
  (lines 608-646), and the pointer miss check and screen-changed
  refusal inherited through desktop_act (docstring lines 24-32).
  Rebuilding any of that in codemode would duplicate the live runner.
- Extend codemode with the code_exec API is rejected. It would create
  a second sandbox with a second validator (codemode _scan lines
  200-222 vs code_exec _Validator lines 260-328), a second budget
  set, and a second backend binding. The two would drift, and a safety
  fix applied to one would silently not apply to the other. Worker N
  already records that codemode.py is a prototype for evaluation, not
  production code (scripts/codemode.py lines 18-22).
- Two registries (one per executor) is rejected. The model would have
  to know which registry a snippet belongs to, the same snippet could
  exist in both with different behavior, and staleness would double.
- codemode keeps its own job: search/describe over the repo scripts
  (Worker N verdict section 6, docs/research/2026-11-21-code-mode-integration.md
  lines 281-304). That is a discovery layer, not an executor. If the
  registries ever merge, the merge direction is codemode search/describe
  into code_exec, never code_exec execution into codemode.

Implementation shape for Worker Y1 to specify (design only, no code
here): `run_snippet` becomes a new allowlisted name in code_exec,
alongside the names at scripts/code_exec.py lines 271-275. It loads the
snippet file named by the manifest, substitutes declared params only,
and executes the snippet body inside the running program's session and
namespace, sharing the session wall budget (default 30s, max 60s,
lines 92-94), the API call budget (32, line 95), the trace step budget
(20000, line 96), the observation bindings, and the cancel latch. It
must NOT reset budgets: a snippet that resets the wall clock would be
a budget bypass. The top-level entry point (cu.py code-exec command,
scripts/cu.py lines 2322-2380) also accepts a snippet by name, loading
it and running it through the existing CodeExecSession.run path
(scripts/code_exec.py lines 799-870), so a snippet is runnable without
a wrapping program.

## 3. SAFETY: promoted snippets still go through the scan and budgets

Recommendation: YES, every snippet goes through the full AST scan and
all budgets at run time, every time. Promotion grants reuse, never
trust. No exemption path.

Reasons:

- Promotion is a review at one point in time; the file on disk is
  what runs. A snippet edited after review, a bad merge, or a manifest
  pointing at a different file would all bypass a trust-once rule.
  The runtime scan is the only check that sees the code that actually
  executes. The scan is cheap: validate_program
  (scripts/code_exec.py lines 330-345) already runs on every program,
  and snippets are programs.
- Budgets are session safety, not code quality checks. A correct
  snippet on a hung desktop still needs the wall budget and the cancel
  latch; a snippet in a retry loop still needs the 32 API call budget.
  Exempting snippets from budgets would let a stale snippet loop
  act() calls indefinitely.
- The GUI safety invariants do not change: act() still goes through
  desktop_act with the pointer miss check and screen-changed refusal
  (scripts/code_exec.py docstring lines 24-32), and verification still
  comes from an exact source plus a final observation image, never
  from the snippet asserting its own success (docstring lines 18-22).

Stale snippets:

- Each snippet carries `api_version` (the code_exec API version it was
  verified against) and `last_verified` (date). The loader checks
  `api_version` against the current code_exec API before running.
  A mismatch fails closed with an envelope naming the snippet, the
  recorded version, and the current version. This is in addition to,
  not instead of, the AST scan: an unknown name would fail validation
  anyway, but the version check gives a clear stale error instead of
  a confusing NameError.
- A snippet is stale when `api_version` does not match the current
  code_exec API, or when `last_verified` is older than the staleness
  window the council sets (recommend 90 days; Worker Y1 to confirm).
  Search results must flag stale snippets as stale, never silently
  list them as current.
- `run_snippet` refuses a stale snippet by default. The refusal
  envelope names the snippet, the last_verified date, and the reason.
  An explicit opt-in (`allow_stale=True` at the call site, logged)
  may override for diagnosis only, never as the normal path. The
  model must replan from the refusal, not retry the same snippet.

## 4. SCHEMA and verification

Required fields per snippet (all in the manifest except `code`, which
lives in the .py file):

- `name`: stable identifier, lowercase with underscores, for example
  `p1_disk_check`. This is the run-by-name key. Never renamed without
  a manifest alias entry for the old name.
- `file`: path under snippets/, for example `p1_disk_check.py`.
- `description`: one line, what the snippet does and when to use it.
  This is what search returns.
- `params`: declared parameters with names, types, defaults, and
  required flags. Only declared params may be substituted; undeclared
  values are rejected, never interpolated into code.
- `source`: where the snippet came from, for example
  `improvements/pick1-program-template.md P1`. P1-P4 cite the template
  file and program number, so a future reader can check the original.
- `last_verified`: ISO date of the last passing verification run.
- `api_version`: code_exec API version verified against.
- `expected_result`: the observable postcondition, for example
  "terminal shows df output and verify image is captured" or, for P3,
  "directories /tmp/hoc-ky-2/dsa, ktvm, oop exist". This must be
  checkable, not prose about intent.
- `tags`: keywords for search, for example `terminal`, `disk`, `verify`.

Verification:

- A test file `tests/test_snippets.py` runs every manifest-listed
  snippet against a fake backend, following the existing
  tests/test_code_exec.py pattern (FakeBackend at lines 18-48,
  FakeDomBackend at lines 49-112, run_program helper at lines
  132-133). Snippets that need a live terminal or browser run against
  the fake backend with canned windows/observations; the test asserts
  the snippet's expected_result postcondition, not just that it did
  not crash.
- The test runs on every commit touching snippets/ or
  scripts/code_exec.py, and it fails if: a manifest entry has no file,
  a file has no manifest entry, a snippet fails the AST scan, a
  snippet exceeds MAX_PROGRAM_CHARS (8192, scripts/code_exec.py
  line 92), a snippet's api_version does not match, or a snippet's
  expected_result does not hold.
- `last_verified` is updated only by a passing verification run, never
  by hand editing the date. A snippet whose verification fails is
  marked stale in the manifest by the test run, not left looking
  current.
- Live re-verification: the four Pick 1 snippets are re-run live on
  the laptop whenever the code_exec API changes (new name added,
  signature changed, budget changed), before the change merges.

## 5. RUN-BY-NAME and search

Recommendation:

- Invocation: `run_snippet(name, **params)` is an allowlisted name
  inside code_exec programs (see question 2), and `--snippet name`
  is the top-level entry point on the cu.py code-exec command. Params
  are passed as named arguments matching the manifest `params` block;
  a snippet that needs a window title takes it as a param instead of
  hardcoding `speed-pick1-term`. P1-P4 as written hardcode that title
  (improvements/pick1-program-template.md lines 19, 31, 43, 60), so
  the first registry entries must parameterize the title before they
  are promoted, or they only work for that one terminal.
- Search: snippets appear in search results through the same
  search/describe shape codemode already provides
  (scripts/codemode.py search_ops lines 173-186, describe_op lines
  188-198), extended to cover snippet names, descriptions, and tags.
  Search returns name, description, params summary, last_verified,
  and a stale flag, never the full code. Describe returns the full
  manifest entry plus the snippet source for one named snippet, so
  the model can inspect before running. The model flow is:
  search snippets, describe one, run_snippet by name.
- Snippets and repo ops share one search surface but are marked by
  kind (`snippet` vs `op`), so the model can tell a runnable program
  from a single operation. A search hit on a stale snippet shows the
  stale flag and the last_verified date in the same line as the name,
  so the model does not have to describe it to learn it is stale.

## Overall verdict

GO, with conditions.

- GO on: snippets registry as a snippets/ directory of .py files plus
  a JSON manifest with metadata only; executor is scripts/code_exec.py
  only; run_snippet as a code_exec allowlisted name sharing session
  budgets and bindings; full AST scan plus budgets on every run with
  no trust exemption; schema and fake-backend verification as in
  question 4; search/describe/run-by-name as in question 5.
- NO-GO on: running snippets in codemode.execute_op; extending
  codemode with the code_exec API; two registries; JSON files holding
  code as strings; data inside scripts/code_exec.py; any trust
  exemption for promoted snippets; running stale snippets by default.
- Conditions before the first entries merge:
  1. P1-P4 are parameterized (window title as a param, not hardcoded
     `speed-pick1-term`) before promotion.
  2. tests/test_snippets.py exists and passes, covering all four
     entries against the fake backend.
  3. The manifest loader enforces manifest-only, snippets/-only, and
     api_version checks, failing closed.
  4. No change to the code_exec sandbox, budgets, or allowlist other
     than adding the run_snippet name. The safety invariants in the
     scripts/code_exec.py docstring (lines 11-32) stay unchanged.
- Open item for Worker Y1 to settle: the staleness window (recommended
  90 days) and the code_exec API versioning scheme that api_version
  refers to (a version constant in code_exec.py is the cleanest
  option; a git commit hash of code_exec.py is acceptable if no
  version constant exists yet).

## Claims and sources

- Worker N verdict (do not build full Code Mode server; adopt
  search/describe plus snippets registry):
  docs/research/2026-11-21-code-mode-integration.md lines 281-304.
- code_exec is the live runner, Pick 1 merged at 453adc4, API list:
  docs/research/2026-11-21-code-mode-integration.md lines 124-141;
  scripts/code_exec.py lines 271-275.
- codemode prototype, 6 ops, not production:
  scripts/codemode.py lines 18-22, 130-167, 241-244.
- P1-P4 programs and shape rule:
  improvements/pick1-program-template.md lines 7-13, 15-71.
- code_exec budgets and opt-in flag: scripts/code_exec.py lines
  92-96, 132-134.
- Fake backend test pattern: tests/test_code_exec.py lines 18-48,
  49-112, 132-133.
- No existing snippets file or run_snippet op was found by grep over
  scripts/, improvements/, docs/, tests/ on 2026-11-21; this design
  creates both from scratch.
