# Council Member 3 verdict: Code Mode snippets registry design

Role: Council Member 3 of Worker Y1's council. Date: 2026-11-21.
Branch: todolist-push. Repo: ~/workspace/computer-use-wayland.
Scope: DESIGN ONLY. No implementation was done and no other worker's files were touched.

Sources read, with the claims each one grounds:
- docs/research/2026-11-21-code-mode-integration.md (Worker N's verdict: do NOT build a full Code Mode server; DO adopt (1) search/describe registry over all 56 scripts and (2) a snippets registry; Pick 1 template programs are the first entries)
- scripts/codemode.py (320 lines; prototype, 6 ops, search_ops/describe_op/execute_op)
- scripts/code_exec.py (880 lines; the LIVE runner, Pick 1 merged at commit 453adc4)
- improvements/pick1-program-template.md (template programs P1-P4, the first snippets)
- tests/test_code_exec.py (53 test functions; FakeBackend stand-in for the brokered primitives) and tests/test_codemode.py (21 test functions)

## 1. WHERE does the snippets registry live

Recommendation: option (b), a snippets/ directory of .py files plus a manifest, located at scripts/snippets/ with the manifest at scripts/snippets/manifest.json.

Reasoning, option by option:

- (a) JSON file with code as strings (the example in the research doc, docs/research/2026-11-21-code-mode-integration.md lines 303-304, "Add a snippets file (for example improvements/code-snippets.json)"): REJECT. Code in JSON strings cannot be syntax highlighted, cannot be py_compile checked, and forces escaping pain on exactly the construct snippets use most. The P4 lesson proves the cost: improvements/pick1-program-template.md documents at length that the printf argument needs literal backslash-n inside one single-quoted argument, with `\\n` in the Python source and `\n` only at the end, and that getting this wrong produced `bash: command not found` in the live run. Storing that program as a JSON string adds a second escaping layer on top of the Python layer and the shell layer. Every future edit would re-risk the P4 failure mode. JSON is also hostile to review diffs: a one-line logic change shows as a changed string blob.
- (c) Inside scripts/code_exec.py as data: REJECT. scripts/code_exec.py is already 880 lines of safety-critical sandbox code (AST validator at lines 267-329, session and budgets at lines 357-484, run at lines 799-869). Every snippet addition or edit would touch the file that enforces the sandbox, widening review risk and merge conflicts on the live runner. Data and enforcement must not share a file when the data changes often and the enforcement must change rarely.
- (b) snippets/ directory of .py files plus a manifest: ACCEPT. Each snippet is a real .py file, so it gets syntax highlighting, py_compile checks, readable diffs, and direct execution by the test suite. The manifest holds metadata only (see question 4), so the .py file stays pure runnable code with no metadata comments to drift. Editability, versioning, and testability are all best under (b): an edit is a normal code edit, a version is a normal git diff, and a test is a normal test run over the file.

Location note: scripts/snippets/ rather than improvements/snippets/. The snippets are runtime code executed by scripts/code_exec.py, not improvement notes; improvements/ holds design docs and reports. Keeping code beside its executor also makes the import path trivial for the test loader. If the council prefers the manifest to live with the design docs, the manifest path is the one negotiable detail; the .py files must stay as real files either way.

## 2. WHICH executor runs snippets

Recommendation: code_exec.py runs snippets. Merge the registry into code_exec.py as a run_snippet capability. Do NOT run snippets in codemode.execute_op, do NOT extend codemode with the code_exec API, and do NOT maintain two registries.

The key tension, stated with evidence:

- The Pick 1 template programs call the code_exec API. improvements/pick1-program-template.md P1-P4 all call windows(), observe(), act(), assert_state(), and P3-P4 add assert_file_exists() / assert_file_contains(). scripts/code_exec.py lines 31-57 document exactly that API: windows, observe, act, dom_start, dom_tabs, dom_observe, dom_act, dom_assert, read_file, assert_state, assert_file_contains, assert_file_exists.
- codemode.execute_op exposes only repo.* ops. scripts/codemode.py lines 130-168 register 6 ops: repo.list_scripts, repo.script_info, repo.py_compile, repo.read_file, zen.locate (laptop-only), overlay.status (laptop-only). scripts/codemode.py lines 243-245 build the execution namespace from those ops only. A P1 program executed under codemode.execute_op would fail on the first call, because windows is not a name in that namespace.
- Therefore a snippet that cannot run in its executor is dead code, and the only executor in which P1-P4 can run is code_exec.py.

Why not the alternatives:

- Extending codemode with the code_exec API would duplicate the live runner: a second AST scanner (scripts/codemode.py lines 200-221 already duplicates the scan shape), a second set of budgets (scripts/codemode.py lines 31-34 vs scripts/code_exec.py lines 92-96), and a second session/binding model to keep in sync. codemode.py's own docstring says it is "a prototype for evaluation, not production code" and "does not replace scripts/code_exec.py". Duplicating a safety-critical sandbox to serve the prototype is the wrong direction; the prototype should stay small.
- Two registries (one per executor) would diverge within weeks: a snippet fixed in one registry and stale in the other, and the model would have to guess which registry holds the working copy. One registry, one executor, one source of truth.

Design constraint for the implementer: run_snippet(name, **params) must be a code_exec API function, added to the _Validator allowlist (scripts/code_exec.py lines 270-276) and to the run() namespace (scripts/code_exec.py lines 799-869), that loads the snippet .py file, binds params as plain values in the current session namespace (never by string interpolation into the snippet source, see question 3), validates the snippet with validate_program (scripts/code_exec.py lines 331-343), and executes it in the SAME session, against the SAME API-call budget (default 32, scripts/code_exec.py line 95), wall-clock budget (default 30s, max 60s, lines 93-94), and observation/DOM bindings (120s expiry, line 91 in the constants area and _load_state). A nested fresh session would reset budgets and drop bindings, which would break the windows -> observe -> act -> observe -> assert shape the templates rely on. The snippet's own asserts stay in place; run_snippet returns the snippet's envelope fields, not a bare success flag.

What codemode keeps: search/describe over repo scripts stays in scripts/codemode.py (search_ops at lines 173-186, describe_op at lines 188-197). Snippets are a code_exec concern; the op registry is a codemode concern. If the 56-script registry is later merged into code_exec.py, run_snippet rides along unchanged because it already lives there.

## 3. SAFETY: trusted once promoted, or scanned every run

Recommendation: snippets are NEVER trusted once promoted. Every snippet run goes through the full AST scan plus budgets at run time, exactly like model-written code. Promotion is a review gate, not a trust upgrade.

Reasons:

- The sandbox is not a true isolate. docs/research/2026-11-21-code-mode-integration.md section 4.4 states plainly that "an AST scan plus restricted builtins is NOT a true isolate" and that a model finding a gap "runs code in the agent process". Skipping the scan for promoted code would remove the only barrier between a snippet and the agent process. The scan is cheap (it runs before execution in both scripts/code_exec.py lines 331-343 and scripts/codemode.py lines 200-221); there is no performance case for skipping it.
- Promotion is a point-in-time human judgment; the file can change after promotion. A .py file in the repo can be edited by any later commit, by a bad merge, or by a mistaken edit. Runtime scanning makes the safety property independent of file history. Trusting the file because it was once reviewed is trusting git history, not code.
- Params are model-supplied at call time. A snippet with a `terminal_title` or `text` param receives attacker-controllable values from the model on every call. Param binding must be value binding into the namespace, never string interpolation or formatting into the snippet source before scanning, or a param value could smuggle code past the scan. The scan must run on the final source AFTER params are bound as values, which in practice means: scan the snippet source as written, then bind params as namespace values. Any design that builds snippet source by concatenating param strings is rejected.
- The CU_CODE_EXEC opt-in flag still gates everything. scripts/code_exec.py lines 132-134 enable execution only when CU_CODE_EXEC is 1, true, or yes. Snippets do not get their own bypass flag and do not run when the flag is off.

Stale snippets: a snippet goes stale when the code_exec API changes (a renamed function, a changed act schema, a changed binding rule) or when the desktop behavior it assumes changes. Handling, in order:

1. The manifest carries last_verified (date) and verified_against (the code_exec.py git commit hash the snippet was last verified with). See question 4.
2. At load time, run_snippet compares verified_against with the current code_exec.py commit. On mismatch it does NOT silently run. It returns a stale-snippet envelope naming the snippet, its verified commit, and the current commit, and the model falls back to writing a fresh program.
3. The verification test (question 4) is the detection mechanism: it runs every snippet on every change to scripts/code_exec.py and to scripts/snippets/, so staleness is caught by CI, not by a user watching a failure.
4. A snippet that fails its verification test is removed from search results (question 5) until re-verified. A failing snippet must never be offered to the model as usable.

## 4. SCHEMA and verification

Recommendation: manifest entries carry these fields. Required fields first, then optional.

Required fields per snippet:

- name: stable kebab-case id, e.g. p1-terminal-df, p3-make-dirs, p4-write-ideas. The id never changes after first use; renames break callers.
- description: one line, shown in search results. Must say what the snippet does and what it needs, e.g. "Type a command in a named terminal and verify the act succeeded".
- code_path: relative path to the .py file under scripts/snippets/, e.g. snippets/p1_terminal_df.py.
- params: list of {name, type, required, default, description}. Types are JSON types only (string, integer, boolean, string list), matching the JSON-serializable variable rule in scripts/code_exec.py lines 137-155. P1-P4 as written have one param each in practice (the terminal title speed-pick1-term, hardcoded in improvements/pick1-program-template.md); the first manifest entries should promote that title to a param with a default, so the snippet is reusable instead of a verbatim copy.
- source: where the snippet came from, e.g. improvements/pick1-program-template.md P1, plus the commit that introduced it. This is the audit trail for promotion.
- last_verified: ISO date of the last passing verification run.
- verified_against: git commit hash of scripts/code_exec.py at that verification.
- expected_result: what success looks like, stated as the envelope plus the assert, e.g. "ok True, assert_state(result[ok]) passes, no file assertions" for P1, or "ok True plus assert_file_contains passes for all three lines" for P4. This field is what the test asserts; it is not prose for the model.
- tags: keyword list for search, e.g. ["terminal", "type", "verify"].

Optional fields:

- wall_seconds and max_api_calls: per-snippet budget overrides within the global caps (scripts/code_exec.py lines 93-96: wall max 60s, API max 32). Defaults apply when absent. Overrides may only lower the caps, never raise them.
- live_only: boolean. True when the snippet needs a live desktop and cannot run against a fake backend (any snippet calling act on a real terminal). Live-only snippets are verified in the laptop live-test lane, not in VM CI.
- reviewed_by and reviewed_on: promotion record. Nice to have, not load-bearing.

Verification: a new test file tests/test_snippets.py, structured as follows:

- It loads scripts/snippets/manifest.json, and for every entry it checks the manifest schema (required fields present, code_path exists, params well-formed).
- It py_compiles every snippet .py file and runs validate_program on it (scripts/code_exec.py lines 331-343), so a snippet that would fail the AST scan fails the test.
- It executes every non-live_only snippet against the FakeBackend harness already used by tests/test_code_exec.py (FakeBackend at tests/test_code_exec.py lines 18-47, run helper at lines 131-145), and asserts the manifest's expected_result.
- Live-only snippets (P1-P4 as written, since they act on a real terminal) are executed in the laptop live-test lane with the same expected_result assertions, and their last_verified is updated only by a passing live run.
- The test file runs in VM CI for the non-live set, and the manifest's last_verified / verified_against fields are updated by the verification run itself, not by hand, so the fields cannot claim a verification that never happened.

## 5. RUN-BY-NAME and search visibility

Recommendation: the model invokes a snippet with run_snippet(name, **params) as a code_exec API function (see question 2), and snippets appear in search results alongside ops, clearly marked as snippets.

Run-by-name mechanics:

- Inside a code_exec program, the model writes run_snippet("p1-terminal-df", terminal_title="speed-pick1-term"). The name is a string literal; params are keyword arguments bound as values.
- run_snippet loads scripts/snippets/manifest.json, looks up the name, checks the stale rule from question 3, loads the .py file, validates it with validate_program, binds params, and executes it in the current session under the current budgets.
- Unknown name returns an error envelope listing the closest matching names, so the model can correct a typo instead of guessing.
- A snippet may not call run_snippet on itself or form a call cycle. The implementer must enforce a call-depth cap of 1 (a snippet runs flat; nested run_snippet calls are rejected). Snippets compose by the model calling two snippets in sequence in one program, not by snippets calling snippets.

Search visibility:

- Snippets appear in codemode search_ops results with a distinct marker, e.g. entries shaped {kind: "snippet", path: "snippet.p1-terminal-df", description, params} alongside {kind: "op", path: "repo.list_scripts", ...}. The kind field is what keeps the model from confusing a snippet (runnable by name with params) with an op (callable as a function in execute_op code).
- describe_op, or a describe_snippet companion, returns the full manifest entry for one snippet: description, params with types and defaults, expected_result, last_verified, and verified_against. The model describes before it runs, the same progressive-disclosure pattern as ops (scripts/codemode.py lines 173-197).
- Stale or failing snippets are excluded from search results entirely (question 3, rule 4). Search must never advertise a snippet the runner would refuse.
- The code_exec API docstring (scripts/code_exec.py lines 31-57) gains one line documenting run_snippet, so the model knows the capability without loading the whole manifest. The manifest itself is never loaded into the model context wholesale; search returns ranked one-liners, exactly as search_ops does today.

## Overall verdict: GO, with conditions

GO, for the design as specified above: snippets/ directory of .py files plus a manifest at scripts/snippets/manifest.json; execution merged into scripts/code_exec.py as run_snippet; full AST scan plus budgets on every run with no trust-upgrade at promotion; the schema and tests/test_snippets.py verification in question 4; run-by-name plus kind-marked search visibility in question 5.

Conditions, all of which must hold before the first snippet is promoted:

1. No snippet runs outside scripts/code_exec.py. No second executor, no second registry, no codemode extension.
2. No param string interpolation into snippet source. Value binding only, scan on the snippet as written.
3. No snippet is searchable or runnable while stale or failing verification. The stale envelope and search exclusion are part of the first implementation, not a later hardening pass.
4. The first manifest entries are exactly P1-P4 from improvements/pick1-program-template.md, with the terminal title promoted to a param, and tests/test_snippets.py passes for them in the VM lane (non-live assertions) before any live promotion is claimed.
5. No measurement claims. Per docs/research/2026-11-21-code-mode-integration.md section 4.2, there are still no before/after wall-time numbers for Pick 1; the snippets registry must not be presented as a measured speedup until the paused Pick 1 measurement finishes.

Open question for Worker Y1, not a blocker: whether the manifest lives at scripts/snippets/manifest.json (recommended) or under improvements/. The .py files must be real files under scripts/snippets/ either way.
