# Worker N work log: Cloudflare Code Mode research

All times Asia/Ho_Chi_Minh (UTC+7), wall-clock + elapsed per step.

## 2026-11-21 15:35 +07 (start)
- Spawned as Worker N. Task: research Cloudflare Code Mode, assess fit for computer-use-wayland, build a minimal prototype, write a report.
- Note: the TikTok video itself could not be watched from the VM (no live browser for subagents); the work uses the video description plus the Cloudflare blog post and SDK sources the parent already identified.

## 15:36 +07 (2 min): blog post read
- Read https://blog.cloudflare.com/code-mode-mcp/ (published 2026-02-20, updated 2026-07-15, crawled 2026-11-21 08:35 UTC).
- Confirmed: 2,500+ endpoints, 1.17M tokens as native MCP tools, ~1,000 tokens with two tools search() and execute(), 99.9% reduction. Dynamic Worker isolate, no filesystem, no env vars, external fetch off by default. MCP Server Portals compose multiple servers behind one gateway.

## 15:37 +07 (3 min): SDK docs read
- Read https://developers.cloudflare.com/agents/tools/codemode/how-it-works/ (crawled 2026-11-21 08:35 UTC).
- Key model: one outer tool `codemode` taking {code}; platform SDK inside the sandbox (search, describe, step, run); connectors as sandbox globals (github.list_pull_requests); executor runs one block once, no state; durable runtime records execution, approvals, replay, rollback, snippets in SQLite; approval pauses execution, replay replays recorded results; step() captures nondeterminism; fetch/connect blocked by default (globalOutbound null).
- Changelog 2026-07-22: runtime now has direct execute(), search(), describe() for non-AI-SDK hosts; requiresApproval on methods; approve()/reject() resolve paused runs.

## 15:38 +07 (2 min): Anthropic + Goose variants read
- Anthropic Programmatic Tool Calling: Claude writes Python in a code execution sandbox that calls tools as functions; intermediate results stay in the sandbox and never re-enter context. Requires beta header advanced-tool-use-2025-11-20, code_execution_20250825, models Opus 4.5/4.6 and Sonnet 4.5/4.6, via Claude API and Microsoft Foundry. Public beta. Not covered by Zero Data Retention.
- Goose Code Mode (Block, v1.17.0, Dec 2025): three meta-tools list_functions, get_function_details, execute_javascript; runs JS in a Boa context; text-only results; no filesystem, shell, network, env, or package access; tool calls keep extension lease, permission flow, cancellation. One team member measured 30% fewer tokens on one bug-fix task (informal, not a benchmark).
- Goose docs: https://goose-docs.ai/docs/guides/managing-tools/code-mode/ (crawled 2026-11-21 08:35 UTC).

## 15:40 +07 (5 min): SDK source cloned and read
- Cloned cloudflare/agents sparse (packages/codemode only), read README.md in full.
- Confirmed API: createCodeTool({tools, executor}), DynamicWorkerExecutor (WorkerLoader), createCodemodeRuntime, McpConnector, OpenApiConnector, CodemodeConnector base class, snippets (saveSnippet, codemode.run), ToolProvider interface, Executor interface (execute(code, providers) -> {result, error, logs}), normalizeCode, generateTypesFromJsonSchema, sanitizeToolName. NodeVMExecutor example in README shows the pattern is executor-agnostic. Limitations: experimental, JS only, DynamicWorkerExecutor needs Workers env, iframe executor cannot preempt tight sync loops.

## 15:45 +07 (4 min): repo fit investigation
- Repo scripts/: 60 files, 56 .py/.mjs/.sh. tests/: 150 files.
- Found scripts/code_exec.py (880 lines): the repo ALREADY implements the client-side Code Mode pattern. One short program per model call, allowlisted API (windows, observe, act, dom_start, dom_tabs, dom_observe, dom_act, dom_assert, read_file, assert_state, assert_file_contains, assert_file_exists), AST scan rejects imports/dunders/eval/exec/open, restricted builtins, wall budget 30s default/60s max, API budget 32, trace budget 20000, state persists in mode 0600 file, observation bindings expire after 120s, opt-in flag CU_CODE_EXEC=1 default OFF. Track 2 Pick 1, won 4/4, merged at commit 453adc4.
- Baseline anchor (improvements/speed-proto-pick1.md): clean-task mean wall 36.4s, mean model think 34.2s (94%), broker service 1.4s (4%). Pick 1 replaces 4-5 think calls with 1 program-writing call + finish. Measurement paused mid-run by user order, NO before/after wall-time numbers exist yet.
- Measured token-relevant sizes (chars/4 estimate, stated as estimate): code_exec.py API docstring 4910 chars, ~1227 tokens. All 56 scripts first-3-lines total 5764 chars, ~1441 tokens. Prototype search(all) output 804 chars, ~201 tokens. Prototype describe(all 6 ops) 1423 chars, ~355 tokens.

## 15:52 +07 (6 min): prototype built
- Wrote scripts/codemode.py: registry of 6 typed ops (repo.list_scripts, repo.script_info, repo.py_compile, repo.read_file, zen.locate laptop-only, overlay.status laptop-only), search_ops, describe_op, execute_op with AST scan, restricted builtins, trace step budget (model frames only), wall-clock budget, envelope results incl. requires_laptop.
- Wrote tests/test_codemode.py: 21 tests (search, describe, execute, chained ops, loop/filter, read_file guards, laptop-only envelope, import/open/eval/dunder rejection, syntax/unknown-name envelopes, wall-clock budget, size cap, timing).

## 15:58 +07 (4 min): prototype test failures fixed, all green
- Failure 1: trace step budget exceeded on py_compile. Root cause: my tracer counted lines inside op implementations. Fix: count only frames with co_filename == "<codemode>", same rule as code_exec.py.
- Failure 2: py_compile refused cfile=/dev/null ("non-regular file"). Fix: compile to a NamedTemporaryFile in /tmp.
- Result: 21/21 tests pass in 0.056s. CLI demo verified: search "dom locate" returns zen.locate, describe returns full signature, execute list_scripts('zen') completes in 7.9ms, 6 steps.

## 16:00 +07 (5 min): report written
- Wrote docs/research/2026-11-21-code-mode-integration.md: what Code Mode is (3 variants), how each works, per-agent applicability, fit assessment with verdict, prototype results with measured numbers, risks, concrete next steps.
- Verdict: do NOT build a full Cloudflare-style Code Mode server (no MCP server with thousands of tools exists here, and code_exec.py already is the client-side equivalent). DO adopt the two missing pieces: search/describe progressive discovery over the 56-script catalog, and a snippets registry for reusable programs. Test further: measure wall time code_exec vs baseline on the realistic test set.

## 16:05 +07: commit and push
- Commits on todolist-push (owner's mail). Report back to Muse.
