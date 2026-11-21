# Cloudflare Code Mode: integration assessment for computer-use-wayland

Date: 2026-11-21. Author: Worker N. Sources accessed 2026-11-21.
Repo: phamTuan207/computer-use-wayland, branch todolist-push.

## 1. What Code Mode is

Code Mode is a pattern for giving an agent access to a large API without
loading every tool definition into its context window. Instead of exposing
one tool per operation, the host exposes a tiny fixed surface (two tools in
Cloudflare's server, one tool in the SDK, three meta-tools in Goose) and the
model writes code against a typed API. The code runs in a sandbox and
returns only the final result. The full API catalog never enters the model
context.

Cloudflare's numbers, from the blog post (published 2026-02-20, updated
2026-07-15, https://blog.cloudflare.com/code-mode-mcp/): the Cloudflare API
has over 2,500 endpoints. Exposing each as a native MCP tool would cost
about 1.17 million tokens. The Code Mode MCP server exposes `search()` and
`execute()` for about 1,000 tokens, a 99.9% reduction, fixed no matter how
many endpoints exist. The whole operation in the blog example (search the
spec, inspect a schema, list rulesets, fetch DDoS and WAF configs) took
four tool calls.

## 2. The three variants

### 2.1 Cloudflare server-side (the blog post)

The MCP server exports two tools. `search()` runs model-written JavaScript
against the full OpenAPI spec (all `$refs` pre-resolved) inside a Dynamic
Worker isolate. `execute()` runs model-written JavaScript against a
`cloudflare.request()` client that makes authenticated API calls. Both run
in a lightweight V8 sandbox with no file system, no environment variables
to leak through prompt injection, and external fetches disabled by default.
Outbound requests can be explicitly controlled with outbound fetch handlers.
The server is OAuth 2.1 compliant and downscopes the token to the
permissions the user granted. MCP Server Portals compose multiple MCP
servers behind one gateway with unified auth, and Cloudflare is building
first-class Code Mode integration for all of them.

### 2.2 Cloudflare Code Mode SDK (open source)

Package `@cloudflare/codemode` in the cloudflare/agents repo
(https://github.com/cloudflare/agents/tree/main/packages/codemode).
Marked experimental, may have breaking changes.

Architecture, from the SDK README and
https://developers.cloudflare.com/agents/tools/codemode/how-it-works/:

- One outer tool named `codemode` taking `{code: string}`. Its
  description lists connector namespace names (e.g. `github`, `stripe`)
  but not every method and schema.
- Inside the sandbox, the `codemode` global provides `search(query)`,
  `describe(target)`, `step(name, fn)`, and `run(name)`. `search` returns
  ranked paths, not complete schemas. `describe` returns focused
  TypeScript documentation for one path.
- Each connector becomes another sandbox global (`github.list_pull_requests`).
  Connector calls cross the sandbox boundary through Workers RPC. The
  runtime intercepts each call before it executes, applying approval,
  logging, replay, and rollback policy.
- The executor runs one block of code once and stores no state.
  `DynamicWorkerExecutor` creates an isolated Worker per execution pass.
  External `fetch()` and `connect()` are blocked by default
  (`globalOutbound: null`).
- The durable runtime stores execution records, connector-call logs,
  pending approvals, and snippets in isolated SQLite storage. A connector
  method can require approval: the run pauses, the user approves or
  rejects, and approval starts another pass with the same code and
  execution ID. Calls already applied return recorded results instead of
  executing again. `codemode.step()` captures nondeterministic work
  (Date.now, Math.random) so replay stays stable. Rollback walks applied
  calls in reverse and invokes each method's `revert` implementation.
- Connectors: `McpConnector` (wraps an MCP server, one method per MCP
  tool), `OpenApiConnector` (derives one typed tool per OpenAPI operation
  host-side, zero prompt tokens), and a `CodemodeConnector` base class
  (name, instructions, tools with description, schema, approval flag,
  execute, revert).
- Snippets: durable saved scripts. The model writes and runs scripts, the
  developer promotes the good ones (`runtime.saveSnippet`), the model
  reuses them (`codemode.run`). They appear in search results.
- The Executor interface is minimal and executor-agnostic: `execute(code,
  providers) -> {result, error, logs}`. The README shows a Node VM
  executor in a few lines. A changelog entry (2026-07-22) adds direct
  `execute()`, `search()`, and `describe()` on the durable runtime handle
  for hosts that do not use the AI SDK.
- Limitations stated in the README: experimental; JS only;
  `DynamicWorkerExecutor` requires a Cloudflare Workers environment; the
  browser iframe executor cannot preempt tight synchronous loops.

### 2.3 Anthropic Programmatic Tool Calling

Anthropic's version of the same pattern (docs at
https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling,
public beta, accessed 2026-11-21 via archived copies). Claude writes
Python code inside the code execution sandbox that calls the host's tools
as functions. Intermediate results stay in the sandbox and never re-enter
the model context. When a tool function is called, code execution pauses
and the API returns a `tool_use` block; the host provides the result and
execution continues. Requirements: the `advanced-tool-use-2025-11-20`
beta header, the `code_execution_20250825` tool enabled, and tools marked
with `allowed_callers: ["code_execution_20250825"]`. Available on Claude
Opus 4.5/4.6 and Sonnet 4.5/4.6, via the Claude API and Microsoft
Foundry. Not covered by Zero Data Retention arrangements.

### 2.4 Block Goose client-side Code Mode

Goose (Block, open source, now under the Agentic AI Foundation) shipped a
Code Mode extension in v1.17.0 (Dec 2025). Docs:
https://goose-docs.ai/docs/guides/managing-tools/code-mode/. It exposes
three meta-tools: `list_functions`, `get_function_details`, and
`execute_javascript`. The model writes JavaScript that Goose executes in a
fresh Boa JS context. Multiple tool calls batch in one execution,
intermediate results chain locally, tools are discovered on demand. The
sandbox has no direct filesystem, shell, network, environment, or package
access. Tool calls keep the extension lease, permission flow,
cancellation, and mutation handling. Only text results are supported;
images and binary content are ignored. Console output, JSON depth, item
counts, instructions, loop iterations, and recursion are bounded. One
Goose team member measured 30% fewer tokens on a single bug-fix task with
Code Mode on; that is an informal experiment, not a benchmark.

## 3. Which of our agents could use each variant

- fcc-claude (free Claude Code): Anthropic's programmatic tool calling is
  an API-level beta feature. Whether the free Claude Code build exposes
  it is UNVERIFIED. Claude Code is a different product surface from the
  Claude API, and the feature requires the beta header plus specific
  models. Do not assume it works until tested in fcc directly.
- Codex (OpenAI, Luna 6 Max): OpenAI has no equivalent native feature.
  Client-side only, which is what scripts/code_exec.py already does.
- opencode (DeepSeek): no equivalent native feature. Client-side only.
- Muse (this platform): the tool surface is fixed by the platform, not by
  an MCP server, so Code Mode cannot shrink Muse's own tool definitions.
  It applies to the repo's own operations, through code_exec.py and the
  prototype below.
- Clones (Muse accounts): same as Muse.

## 4. Fit assessment for this repo

### 4.1 The honest headline: we already have this pattern

The repo already implements the client-side Code Mode pattern in
scripts/code_exec.py (880 lines, Track 2 Pick 1, merged at commit
453adc4 after winning the council vote 4/4). One short program per model
call, written by the model at runtime, run in a persistent local Python
interpreter. Allowlisted API: windows, observe, act, dom_start, dom_tabs,
dom_observe, dom_act, dom_assert, read_file, assert_state,
assert_file_contains, assert_file_exists. AST scan rejects imports, dunder
access, eval, exec, open, __import__, getattr/setattr, lambdas, and async.
Restricted builtins, program cap 8192 chars, wall budget 30s default and
60s max, API budget 32, trace budget 20000 lines. State persists in a
mode 0600 file, observation bindings expire after 120s. Opt-in flag
CU_CODE_EXEC=1, default OFF. The model template is
windows -> observe -> act -> observe -> assert
(improvements/pick1-program-template.md). One program replaces the 4 to 5
think calls of the baseline loop with one program-writing think call plus
a finish confirmation.

So the question is not "should we adopt Code Mode" but "what does
Cloudflare's version add that code_exec.py does not already have".

### 4.2 Does the 99.9% saving apply to us?

No, not in the Cloudflare sense. The 99.9% figure is about tool
definitions for a 2,500-endpoint API. We have no MCP server with thousands
of tools. Measured sizes in this repo (chars/4 token estimate, stated as
an estimate):

- code_exec.py API docstring (the whole API the model must know): 4,910
  chars, about 1,227 tokens. That is already the same order of magnitude
  as Cloudflare's ~1,000 tokens for 2,500 endpoints, for an API of about
  12 functions.
- All 56 repo scripts, first 3 lines each (a proxy for a full catalog):
  5,764 chars, about 1,441 tokens.
- Prototype search over all ops: 804 chars, about 201 tokens.
  Prototype describe of all 6 ops: 1,423 chars, about 355 tokens.

The absolute saving from search/describe over loading the whole catalog
is on the order of 1,000 tokens. That is real but small. The large saving
in our repo is not tool-definition tokens but model calls: the baseline
profile run measured clean-task mean wall 36.4s with mean model think
34.2s (94%) and broker service 1.4s (4%). Code execution attacks the
94%, not the tool definitions. But there are NO before/after wall-time
numbers yet: the Pick 1 measurement run was paused mid-run by user order
on 2026-11-18, and the summary file states plainly that no wall time, no
think total, and no model-call count exist yet. Do not claim a saving
until that measurement finishes.

### 4.3 What a Code Mode interface for our repo looks like

The prototype in scripts/codemode.py is the shape: a registry of typed
ops, search_ops(query) returning ranked paths plus one-liners (never full
schemas), describe_op(path) returning the full typed signature of one op,
and execute_op(code) running model-written Python against the registry
under the same safety shape as code_exec.py (AST scan, restricted
builtins, wall-clock and trace budgets, envelope results). Ops that need
the laptop are registered with laptop_only=True and return a
requires_laptop envelope on the VM instead of touching the laptop.

The two pieces Cloudflare's design has that code_exec.py does NOT have,
and that are worth adopting:

1. search/describe progressive discovery over the full 56-script catalog.
   Today the model knows only the ~12 code_exec API functions. The other
   ~50 scripts (overlay, zen_dom, polygon_checks, session_cleanup, timing,
   and the rest) are only reachable by the supervisor writing shell
   commands, with no typed registry and no discovery. A search/describe
   layer over all of them would let the model find the right operation
   without the supervisor hand-picking it.
2. A snippets registry. Cloudflare's saved, reusable, named scripts
   (codemode.run) match a real need here: the Pick 1 template programs
   (P1-P4) are already reused verbatim, and the repo has no registry for
   them. A snippets file plus a run-by-name op would make reuse explicit
   instead of copy-paste from a markdown file.

The two pieces NOT worth copying: the durable runtime with approval
pause/resume/replay/rollback (heavy infrastructure, Durable Objects and
SQLite; our sessions are short-lived and the cancel latch plus
observation expiry already cover the safety cases), and the V8 isolate
executor (our AST-scan plus restricted builtins is weaker isolation, but
it runs locally with no Cloudflare account, no Worker Loader, and no
network dependency; a true isolate would be a separate project).

### 4.4 Risks, stated plainly

- Sandbox escape: an AST scan plus restricted builtins is NOT a true
  isolate. code_exec.py and this prototype share that weakness. A model
  that finds a gap (for example through an allowlisted attribute or a
  string formatting hole) runs code in the agent process. Cloudflare's V8
  isolate and Goose's Boa context are stronger. Mitigation in this repo:
  the allowlist is small, the flag defaults OFF, and act() still goes
  through the brokered desktop_act with the pointer miss check and the
  screen-changed refusal. Do not widen the allowlist casually.
- Prompt injection via generated code: model-written code can read files
  the model can see and exfiltrate them through act() typing or through
  return values. code_exec.py limits read_file to /tmp; the prototype
  limits it to the repo root and /tmp. Any Code Mode interface must keep
  those bounds.
- Loss of fine-grained control: one program doing many actions is harder
  to interrupt mid-way than one action per model call. The cancel latch
  (check_cancel before every API call) is the mitigation; it must stay.
- Silent divergence: code that branches on values it read can behave
  differently on replay. Cloudflare solves this with step() and recorded
  results. Our code_exec.py has no replay; a retried program re-runs from
  scratch. For short programs this is acceptable, but it is a real gap
  for long ones.
- Token cost moves, it does not vanish: the model still writes the
  program, and a long program costs output tokens. The saving is in
  round trips, not in total tokens, and only when the program is shorter
  than the conversation it replaces.

## 5. Prototype results (measured on the VM, 2026-11-21)

- scripts/codemode.py: 6 registered ops (repo.list_scripts,
  repo.script_info, repo.py_compile, repo.read_file, zen.locate
  laptop-only, overlay.status laptop-only), search_ops, describe_op,
  execute_op with AST scan, restricted builtins, trace step budget
  (model frames only), wall-clock budget, envelope results.
- tests/test_codemode.py: 21 tests, 21 pass in 0.056s. Covers search
  ranking, describe, chained ops in one program, loops and filters,
  read_file guards, laptop-only envelope, import/open/eval/dunder
  rejection, syntax and unknown-name envelopes, wall-clock budget (2s
  infinite loop stopped), program size cap, and timing bounds.
- Two bugs found and fixed during testing: (1) the tracer counted lines
  inside op implementations, so py_compile exhausted the step budget; fix
  counts only frames from the model code, same rule as code_exec.py.
  (2) py_compile refused cfile=/dev/null; fix compiles to a temp file.
- CLI demo (measured): search "dom locate" returns zen.locate in one
  result; describe returns the full signature; execute
  repo_list_scripts('zen') completes in 7.9 ms, 6 steps.
- Measured sizes: search over all ops 804 chars (~201 tokens); describe
  of all 6 ops 1,423 chars (~355 tokens).
- The prototype never touched the laptop or the user's Zen. Laptop-only
  ops return a requires_laptop envelope on the VM.

## 6. Verdict

Do NOT build a full Cloudflare-style Code Mode server for this repo.
There is no MCP server with thousands of tools here, the client-side
equivalent already exists and is merged (code_exec.py), and the durable
runtime plus V8 isolate would be a separate infrastructure project for
little gain.

DO adopt the two missing pieces, as a small extension of code_exec.py:

1. A search/describe registry over all 56 repo scripts, so the model can
   discover operations on demand instead of the supervisor hand-picking
   shell commands.
2. A snippets registry for reusable programs (the Pick 1 template
   programs are the first entries), callable by name.

Test further before claiming anything: finish the paused Pick 1
measurement (wall time, think total, model-call count, code_exec vs the
baseline loop) on the realistic test set, then compare the prototype's
search/describe path against loading the full catalog in the prompt.

## 7. Next steps (if pursued)

1. Extend scripts/codemode.py registry to cover all 56 scripts with typed
   signatures, or merge the registry into scripts/code_exec.py as a
   search/describe API. Keep the AST scan, budgets, and laptop-only
   envelope.
2. Add a snippets file (for example improvements/code-snippets.json) with
   the Pick 1 template programs, plus a run_snippet op.
3. Run the paused Pick 1 measurement to completion on the realistic test
   set and record before/after wall time, think time, and model calls.
4. Test whether fcc-claude exposes Anthropic programmatic tool calling;
   if it does, compare it against code_exec.py on the same tasks.
5. Do not widen the allowlist, do not relax the budgets, and do not copy
   the durable runtime unless a concrete task needs approval pause and
   replay.

## 8. Sources (accessed 2026-11-21)

- Cloudflare blog, Code Mode: give agents an entire API in 1,000 tokens,
  published 2026-02-20, updated 2026-07-15,
  https://blog.cloudflare.com/code-mode-mcp/
- Cloudflare Agents SDK, @cloudflare/codemode README,
  https://github.com/cloudflare/agents/tree/main/packages/codemode
- Cloudflare Agents docs, How Code Mode works,
  https://developers.cloudflare.com/agents/tools/codemode/how-it-works/
- Cloudflare changelog 2026-07-22, Agents SDK Code Mode updates,
  https://developers.cloudflare.com/changelog/post/2026-07-22-mcp-codemode-updates/
- Anthropic docs, Programmatic tool calling,
  https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling
  (read via archived copies, access date 2026-02-20 in the archive)
- Goose docs, Code Mode,
  https://goose-docs.ai/docs/guides/managing-tools/code-mode/
- Repo sources: scripts/code_exec.py, improvements/speed-proto-pick1.md,
  improvements/speed-proto-pick1-summary.md,
  improvements/pick1-program-template.md, scripts/zen_dom.py,
  scripts/overlay.py.
