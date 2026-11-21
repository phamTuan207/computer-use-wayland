# Council Member 2 verdict: Code Mode snippets registry design (Worker Y1)

Date: 2026-11-21. Role: Council Member 2, Worker Y1 council.
Scope: DESIGN ONLY. No implementation.
Sources read: docs/research/2026-11-21-code-mode-integration.md,
scripts/codemode.py, scripts/code_exec.py,
improvements/pick1-program-template.md.
Branch: todolist-push (verified by git branch check at verdict time).

## Bottom line

GO, with conditions. The snippets registry is worth building, but only in
one shape: real .py files plus a manifest, executed only by
scripts/code_exec.py, always under its AST scan and budgets, verified by a
dedicated test file. The two NO-GO shapes are a JSON file holding code as
strings, and extending scripts/codemode.py into a second executor. A
snippet that cannot run in its executor is dead code, and today not one
Pick 1 template program can run in codemode.execute_op.

## 1. Where the registry lives

Recommendation: (b) a snippets/ directory of .py files plus a manifest.

Concrete shape: snippets/<name>.py for the code, one file per snippet,
plus snippets/manifest.json for the metadata. The manifest is the index,
not the code store. The .py file is the code store.

Reasons, with evidence:

- Editability. Snippet code is real Python. An editor, py_compile, and
  git diff all work on it directly. The prototype already shows this
  pattern works: scripts/codemode.py lines 89-101 compile-check a script
  file with py_compile, and tests/test_codemode.py runs that check.
- Versioning. A diff of a .py file shows exactly what changed. A diff of
  code embedded in a JSON string shows escaped text, and a one character
  escaping change is easy to miss in review.
- Testability. Tests can load the .py file and run it directly through
  code_exec.run_program, the same way tests/test_code_exec.py lines
  131-142 load the P1-P4 programs today (by extracting them from
  markdown, which is itself fragile and should stop once snippets/ exists).

Reject (a) JSON file with code as strings, for a concrete reason, not a
taste reason. The P4 program already proves the escaping hazard:
improvements/pick1-program-template.md lines 59-63 use literal backslash-n
inside a single-quoted printf argument, and lines 78-79 document that
getting the escaping wrong broke P4 (wtype pressed Return inside the
shell command, producing bash: command not found). JSON string encoding
would add a second escaping layer on top of the Python string escaping
and the shell quoting. Byte-for-byte fidelity, which P4 depends on, would
rest on three nested encodings instead of one. Worker N suggested
improvements/code-snippets.json as an example at
docs/research/2026-11-21-code-mode-integration.md lines 303-304. I
overrule that example on this evidence: the example was illustrative,
and the P4 escaping history shows JSON strings are the wrong container
for these programs.

Reject (c) inside scripts/code_exec.py as data, for two reasons.
First, size and focus: scripts/code_exec.py is already 880 lines, and its
safety-critical parts are the validator at lines 270-329, validate_program
at lines 331-341, and the session runner at lines 799-870. Every snippet
addition or edit would touch that file, so every content change would
re-open review of the sandbox file. Second, merge risk: snippet edits
and sandbox edits would conflict in the same file for no benefit.

Known risk of (b), and its mitigation: the manifest can drift from the
.py files (a rename, a stale hash, a wrong last-verified date). Mitigate
by making drift a test failure, not a convention. The test file in
section 4 asserts, for every manifest entry, that the file exists, that
its sha256 matches the manifest, that validate_program passes, and that
the snippet runs against a fake backend. Drift then fails CI instead of
silently shipping.

## 2. Which executor runs snippets

Recommendation: merge the registry into code_exec.py. Do NOT extend
codemode.py with the code_exec API. Do NOT keep two registries.

The key tension, stated with file evidence:

- The Pick 1 template programs call windows, observe, act, and file
  asserts. P1 is at improvements/pick1-program-template.md lines 18-22,
  P3 at lines 42-46, P4 at lines 59-63. All four follow the shape at
  lines 9-11: windows, observe, act, observe, assert.
- Those names exist only in code_exec.py. The allowlist is at
  scripts/code_exec.py lines 271-275: windows, observe, act, read_file,
  assert_state, assert_file_contains, assert_file_exists, print,
  dom_start, dom_tabs, dom_observe, dom_act, dom_assert.
- They do not exist in codemode.py. Its namespace is built at
  scripts/codemode.py lines 241-244 from the OPS list only, mapping each
  op path to its function (repo.list_scripts becomes repo_list_scripts).
  The OPS list at lines 130-166 holds exactly 6 ops: repo.list_scripts,
  repo.script_info, repo.py_compile, repo.read_file, zen.locate,
  overlay.status. A P1 program run through codemode.execute_op would
  fail on the first name (windows is not in the namespace). Zero of the
  four template programs can run there today.
- codemode.py has no desktop backend at all. Its two laptop ops are
  stubs that raise requires_laptop: scripts/codemode.py lines 120-126
  (_op_zen_dom_locate and _op_overlay_status). It has no act path, no
  observation bindings, no cancel latch, no API call budget. code_exec.py
  has all of these: observation bindings with 120 second expiry at lines
  99 and 538-551, API budget 32 at lines 95 and 487-495, wall budget
  30 seconds default and 60 seconds max at lines 92-94, cancel checks
  before every API call at lines 487-495, and brokered act through
  desktop_act with the pointer miss check preserved per the module
  docstring at lines 26-30.
- There is also a read scope mismatch that would change verification
  semantics if snippets ran under codemode: codemode._op_read_file at
  scripts/codemode.py lines 103-118 allows the repo root and /tmp, while
  code_exec._resolve_read_path at scripts/code_exec.py lines 345-353
  allows /tmp only. Running the same snippet under the two executors
  would not mean the same thing.

The honest resolution is therefore: one executor, code_exec.py.
Snippets are code_exec programs, loaded from disk, validated through
validate_program (scripts/code_exec.py lines 331-341), and run through
CodeExecSession.run (lines 799-870). codemode.py keeps only its discovery
role (search_ops and describe_op, scripts/codemode.py lines 173-198),
or its search/describe functions merge into code_exec.py in a later
step. Either way, execution never forks. Extending codemode with a
second copy of the windows/observe/act/dom API would duplicate the
safety invariants (cancel latch, observation bindings, budgets, brokered
act) and create two sandboxes to audit, with guaranteed divergence over
time. Two registries are rejected for the same reason: one will go stale,
and the model will not know which to trust.

Consequences:

- run_snippet lives in scripts/code_exec.py, not in codemode.py.
- Snippets inherit the CU_CODE_EXEC opt-in gate. code_exec.is_enabled at
  scripts/code_exec.py lines 132-134 requires CU_CODE_EXEC=1 (or true /
  yes), and scripts/cu.py lines 2381-2382 refuse the code-exec command
  while the flag is off. No separate snippet flag. A snippet path must
  not bypass the flag that gates the executor it runs on.
- run_snippet is a top-level entry, not a callable inside a snippet
  program. The model invokes it as its own program call (see section 5),
  so there is no nested execution, no double budget accounting, and no
  observation binding confusion between an outer and an inner program.

## 3. Safety: scan, budgets, and staleness

Recommendation: snippets ALWAYS go through the AST scan and the budgets
at run time. Promotion is review, not exemption.

Reasons:

- Promotion is a human judgment at one point in time about intent and
  correctness. It is not a proof that the code is safe for all future
  runs, and it does not survive the file being edited after promotion.
  The AST scan is cheap (validate_program runs before execution at
  scripts/code_exec.py lines 331-341, and run calls it at line 812
  before any API call). There is no performance case for skipping it.
- Worker N states the sandbox weakness plainly at
  docs/research/2026-11-21-code-mode-integration.md section 4.4: an AST
  scan plus restricted builtins is NOT a true isolate, and the allowlist
  must not be widened casually. Removing the scan for snippets would
  widen the one gap that already exists, for code that by definition
  performs real desktop actions. The mitigation stack (small allowlist,
  flag default OFF, brokered act with pointer miss check and
  screen-changed refusal, per the code_exec.py docstring at lines
  26-30) only holds if every program, promoted or not, passes through it.
- A snippet file can change after promotion through a bad merge, a
  careless edit, or a malicious edit. The manifest therefore carries a
  sha256 of the .py file, and run_snippet refuses to run when the on-disk
  hash does not match the manifest. Hash mismatch means the file changed
  since promotion, and the promotion no longer covers it.

Stale definition. A snippet is stale if any of these holds:

- (a) API stale: it references a name that is no longer in the current
  code_exec allowlist (scripts/code_exec.py lines 271-275) plus safe
  builtins, or it uses a call signature the current API rejects. Note
  that validate_program alone does not catch this: the validator at
  lines 310-315 rejects banned and dunder names, but an unknown name
  only fails at run time as a NameError. run_snippet must therefore do
  an explicit pre-check: every Name node in the snippet AST must be in
  the allowlist, the safe builtins, or the declared params. Unknown name
  means stale, and the run is refused with a stale error, not attempted.
- (b) Age stale: last_verified is more than 90 days old. Ninety days is
  a judgment call, not a measured threshold; it is long enough to avoid
  churn and short enough that a desktop API drift is caught. If the
  council prefers a different number, change this one constant, not the
  mechanism.
- (c) Test stale: its verification test fails (section 4). This is the
  strongest signal and overrides the other two.

Runtime behavior, split by kind, so freshness and safety are not
confused:

- API stale: hard refuse. The snippet cannot run correctly anyway, so
  attempting it wastes a run and risks a partial side effect.
- Hash mismatch: hard refuse, for the reason above.
- Age stale only (API check passes, hash matches, tests pass): run, but
  the envelope carries a stale warning (stale: true, last_verified:
  <date>), and search results mark it stale (section 5). Age alone does
  not block a run, because the code still validates, but it must never
  run silently as if freshly verified.
- Tests failing on age stale: CI fails. A snippet that is age stale with
  a green test suite is a re-verification job (bump last_verified after
  a passing run), not a deletion. Nothing is auto-deleted for age alone.

## 4. Schema and verification

Required fields per snippet, in snippets/manifest.json. No field is
optional except tags:

- name: stable kebab-case identifier, for example p1-disk-free. The
  first four entries keep their P1-P4 identity in the source field, but
  the runnable name is kebab-case, not P1, so names stay unique and
  searchable as the registry grows.
- file: relative path, for example snippets/p1-disk-free.py.
- sha256: hex digest of the .py file at promotion time. Verified on load.
- description: one line, what the snippet does, in plain words. This is
  what search returns (never the full code).
- params: list of {name, type, required, default, description}. Empty
  list for P1-P4, which take no params. Params are bound as namespace
  variables at run time (section 5), never substituted into the code
  text.
- source: where it came from, for example
  improvements/pick1-program-template.md P1, with the template lines if
  useful. This is the audit trail for promotion.
- last_verified: ISO date (YYYY-MM-DD) of the last passing verification.
- verified_against: git commit (full or short hash) of the repo state the
  snippet was last verified against, so an API change can be traced to
  the exact code_exec.py it was checked with.
- expected_result: what a passing run proves, in checkable terms, for
  example ok is true and /tmp/hoc-ky-2/dsa exists (P3), or the file at
  /tmp/y-tuong.txt contains all three idea lines (P4). This is not a
  free-text hope; the verification test asserts it.
- tags: optional list of keywords for search ranking, for example
  terminal, disk, file, dom.

Verification, in two layers:

- Layer 1, VM tests (tests/test_snippets.py, new file). For every
  manifest entry: the file exists; sha256 matches; py_compile passes;
  validate_program passes (scripts/code_exec.py lines 331-341); the
  snippet runs to ok true against a fake backend and its expected_result
  holds. Follow the existing pattern: tests/test_code_exec.py lines
  18-48 define FakeBackend, lines 155-242 define FakeShellBackend and
  FakeTerminalBackend which simulate typed shell text, and lines 698-774
  verify the P3 race and the P4 byte-exact text. The snippets test
  reuses those fakes instead of inventing new ones. This layer runs on
  the VM with no laptop, no Zen, no network, like tests/test_codemode.py
  (21 tests, 21 pass, per docs/research/2026-11-21-code-mode-integration.md
  section 5).
- Layer 2, laptop live re-verification. A desktop snippet is only
  last_verified after a live run on the laptop through the real backend,
  because the VM fakes cannot prove a real act lands or a real window
  settles. The fake-backend pass is necessary, not sufficient. Bumping
  last_verified requires the live run, and the commit that bumps it
  records verified_against.

Migration order: P1-P4 first, byte-for-byte from
improvements/pick1-program-template.md (P1 lines 18-22, P2 lines 30-34,
P3 lines 42-46, P4 lines 59-63). The template file stays as the human
source document, but tests stop extracting programs from markdown
(the template_program helper at tests/test_code_exec.py lines 136-142)
and load from snippets/ instead, so the registry is the single source
for runnable code. No new snippet is added until P1-P4 migrate and
their tests pass under the new loader.

## 5. Run by name, and search

Invocation. The model invokes a snippet as its own program call, not
from inside another program:

- Entry point: run_snippet(name, params) as a module-level function in
  scripts/code_exec.py, exposed through scripts/cu.py as a code-exec
  mode, for example a --snippet flag on the existing code-exec command
  (scripts/cu.py lines 2322 and 2381-2382 already gate that command on
  CU_CODE_EXEC). The exact CLI spelling is an implementation detail;
  the design constraint is that it goes through the same gate and the
  same session runner as a hand-written program.
- Semantics: run_snippet loads the manifest entry, checks the sha256,
  runs the API pre-check from section 3, binds declared params as
  namespace variables (validated JSON-serializable values only, same
  _is_jsonable rule as scripts/code_exec.py lines 137-145), then calls
  CodeExecSession.run with the file contents. Params are never string
  substituted into the code. String substitution would re-open
  injection through a param value, and would break the P4 byte-exactness
  that section 1 protects.
- Envelope: the same envelope CodeExecSession.run returns
  (scripts/code_exec.py lines 799-870), plus snippet name, the
  last_verified date, and a stale flag when age stale. A refused run
  (unknown name, hash mismatch, API stale) returns an error envelope,
  never a partial run.
- Unknown name is an error, not a search fallback. If the model asks
  for a name that does not exist, run_snippet returns the error plus
  the closest matching names, and the model searches again. Silent
  fuzzy matching would run code the model did not ask for.

Search. Snippets appear in search results on the same terms as ops,
following the Cloudflare pattern Worker N describes: search returns
ranked paths plus one-liners, never full schemas
(docs/research/2026-11-21-code-mode-integration.md section 2.2, and
scripts/codemode.py lines 173-186, where search_ops returns path,
description, laptop_only, and score only):

- search_ops returns snippet entries alongside op entries, marked
  kind snippet, with name, one-line description, score, and a stale
  flag. The full code is never in a search result.
- describe_snippet(name) returns the manifest entry (description,
  params, source, last_verified, verified_against, expected_result),
  still without the code body. The model reads the code only by running
  it, or by describe returning the file path for the supervisor to read.
  Either way, the code body does not enter the model context through
  search.
- Stale snippets are listed, not hidden, with stale true and the reason
  (age stale, with last_verified date). Hiding them would make the
  registry look smaller than it is and would hide re-verification work.
  API-stale snippets are listed as unrunnable until re-verified, so the
  model does not waste a run on them.

## Overall verdict

GO, with these conditions, all of which must hold before the registry
is announced as usable:

1. Storage is (b): snippets/*.py plus snippets/manifest.json. No code
   as JSON strings, no snippet data inside scripts/code_exec.py.
2. Single executor: scripts/code_exec.py only. codemode.py stays
   discovery-only and gains no desktop API. No second registry.
3. Safety is not relaxed for promoted code: AST scan, wall budget,
   API budget, trace budget, CU_CODE_EXEC gate, sha256 check, and API
   pre-check all apply at every run.
4. Schema is as in section 4, with sha256, last_verified, and
   verified_against required, and params bound as variables, never
   substituted as text.
5. Verification is tests/test_snippets.py against the existing fake
   backends, plus a live laptop run before any last_verified bump.
   P1-P4 migrate first, byte-for-byte, and tests load from snippets/,
   not from markdown.
6. run_snippet is a top-level code_exec entry through the existing
   cu.py gate, and snippets appear in search as one-liners with a stale
   flag, never with full code.

If any condition is dropped, the verdict for that part becomes NO-GO:
a JSON code store is NO-GO on the P4 escaping evidence; a second
executor is NO-GO because it would duplicate the safety invariants;
exempting promoted snippets from the scan is NO-GO because promotion
does not survive later edits to the file.
