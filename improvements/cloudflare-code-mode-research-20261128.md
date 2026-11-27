# Cloudflare Code Mode research and team verdict (2026-11-28)

Owner order 2026-11-28 06:33: research Cloudflare Code Mode, team discusses and proposes, meet if anything is noteworthy.

## What Code Mode is

Code Mode is a technique from Cloudflare (Kenton Varda and Sunil Pai, blog 2025-09-26) for reducing the context-window cost of MCP tool use. Instead of exposing every operation as a separate MCP tool, the MCP tools are converted into a typed TypeScript API and the model is given one tool that executes code. The model writes code against the API, and the code runs in a V8 isolate sandbox (Dynamic Worker Loader). The code acts as a compact plan: the model can explore operations, compose multiple calls, and return only the data it needs, so intermediate results never enter the context window.

Two variants exist:

1. Client-side Code Mode (original, 2025-09-26): the agent framework converts connected MCP servers into a TypeScript API, loads that API into the model context, and gives the model a single execute tool. Sandbox code calls back through RPC bindings to the real MCP servers. Implemented in Goose (Block) and in Anthropic's Claude SDK as Programmatic Tool Calling.
2. Server-side Code Mode (2026-02-20): the MCP server itself exposes only two tools, search() and execute(). The agent writes JavaScript to query the OpenAPI spec (search) and to call the API (execute). Cloudflare's own MCP server covers the entire Cloudflare API (2,500+ endpoints) this way in roughly 1,000 tokens of context, versus about 1.17 million tokens for a native MCP server with full schemas (99.9% reduction, measured with tiktoken). The footprint stays fixed no matter how many endpoints exist.

Anthropic independently explored the same pattern in "Code execution with MCP" (2025-11-04): present MCP servers as code APIs (one file per tool), let the agent write glue code. Their worked example (Google Drive to Salesforce) drops from 150,000 to 2,000 tokens (98.7%). Their later measured numbers are smaller: a Tool Search Tool cut about 77K tokens to about 8.7K, and Programmatic Tool Calling cut research tasks from 43,588 to 27,297 tokens.

## How it works

- The MCP schema is converted into a TypeScript API with doc comments and types.
- The model writes code; the code runs in a Dynamic Worker isolate: a lightweight V8 sandbox with no filesystem, no environment variables, and external fetches disabled by default. Outbound requests can be explicitly controlled with outbound fetch handlers (globalOutbound).
- The sandbox's only access to the outside world is through bindings: live objects in env that proxy to the connected MCP servers. The supervisor holds the access tokens, so generated code cannot leak API keys.
- Isolates start in milliseconds with a few megabytes of memory, so a fresh one is created per snippet and thrown away. No containers, no pooling, no prewarming.
- Server-side: search() gives the model a spec object (full OpenAPI spec, all $refs pre-resolved); execute() gives it an authenticated API client. Results are capped at about 6,000 tokens per call (truncate: false available). OAuth 2.1 with downscoped tokens: the agent only gets permissions the user granted at connect time.

## Maturity, cost, limits

- Dynamic Worker Loader API: open beta since 2026-03-24, available to all paid Workers users (Workers Paid starts at $5/month). Pricing: $0.002 per unique Dynamic Worker per day (charge waived during beta), 1,000 unique Dynamic Workers included per month, plus standard Workers request and CPU pricing. APIs, limits, and pricing may change during beta.
- Code Mode SDK open-sourced in the Cloudflare Agents SDK (@cloudflare/codemode): DynamicWorkerExecutor, codeMcpServer wrapper. Durable runtime handle gained execute(), search(), describe() (Jul 2026).
- MCP Server Portals support Code Mode policies: Off, Opt-in, On by default, Enforced (Jul 2026). Clients can opt out with ?codemode=off to avoid nested code execution.
- Goose (Block) shipped client-side Code Mode in v1.17.0 (Dec 2025) as the "Code Execution" extension, using the boa JS engine in Rust with NativeFunction callbacks to MCP servers. Three tools (search_modules, read_module, execute_code) replace the full tool list.
- Claude Code has an experimental Code Mode (v2.1.325, reported Nov 2026); community reports find it useful for repo audits and chaining MCP tools, but no token-savings measurements were provided.
- Limits: JavaScript/TypeScript only (V8). Server-side results capped at about 6,000 tokens per call. Requires a sandbox with resource limits and monitoring, which Anthropic notes adds operational overhead that direct tool calls avoid. The full API definition is still loaded into context in client-side mode (Cloudflare notes future improvements could allow dynamic search/browse of the API).

## Security model and findings

- Design: sandbox has no internet access (fetch/connect throw), no filesystem, no env vars; only granted bindings are reachable; API keys never enter generated code; OAuth tokens downscoped at connect time.
- Check Point Research ("When Agentic Glue Melts", Hacker News item 49243046) found five memory-corruption bugs in workerd's native C++ glue layer (two rated Critical by Cloudflare), chained into a cross-tenant heap read (another Worker's secrets) and a Code Mode sandbox escape (prompt injection to native code on the host). The V8 cage and memory-protection keys do not cover the tcmalloc native heap where the glue allocates. Both exploits verified on self-hosted workerd, not against Cloudflare production. Cloudflare fixed managed Workers in production; self-hosted deployments should update to workerd v1.20260619.1. No CVEs assigned (Cloudflare policy).
- MCP Inspector RCE (CVE-2025-49596, CVSS 9.4, Oligo Security) is a separate MCP-ecosystem warning: code-execution surfaces in agent tooling are high-value targets. Fixed in MCP Inspector 0.14.1.

## Community reaction

- Mixed. The pattern is widely seen as a real improvement for large tool surfaces; the "MCP is dead" framing on social media is pushed back on (Code Mode still uses MCP underneath; it is a consumption pattern, not a replacement).
- Hacker News discussion centers on the Check Point exploit and on whether the token savings matter at realistic tool counts.
- Anthropic's own later numbers (43,588 to 27,297 tokens on research tasks) are far more modest than the 98.7% headline, which came from one worked example with unnamed model, tool count, and counting method.
- Cloudflare itself lists the alternatives: CLIs (self-documenting, progressive disclosure, but need a shell = broader attack surface) and dynamic tool search (Anthropic's; shrinks context but each matched tool still costs tokens).

## Sources

- Cloudflare blog, "Code Mode: the better way to use MCP" (2025-09-26): https://blog.cloudflare.com/code-mode/
- Cloudflare blog, "Code Mode: give agents an entire API in 1,000 tokens" (2026-02-20): https://blog.cloudflare.com/code-mode-mcp/
- Cloudflare blog, "Sandboxing AI agents, 100x faster" (2026-03-24): https://blog.cloudflare.com/dynamic-workers/
- Cloudflare docs, Dynamic Workers open beta changelog (2026-03-24): https://developers.cloudflare.com/changelog/post/2026-03-24-dynamic-workers-open-beta/
- Cloudflare MCP repo README: https://github.com/cloudflare/mcp/blob/main/README.md
- Cloudflare docs, MCP servers for Cloudflare: https://developers.cloudflare.com/agents/model-context-protocol/cloudflare/servers-for-cloudflare/
- Anthropic, "Code execution with MCP" (2025-11-04), via Simon Willison summary: https://simonwillison.net/2025/Nov/4/code-execution-with-mcp/
- Sulat analysis of Anthropic post (2026-11-23): https://news.sulat.com/2026/11/23/anthropic-code-execution-mcp/
- Check Point Research on Hacker News: https://news.ycombinator.com/item?id=49243046
- Goose Code Mode write-up: https://ghenghis.github.io/Super-Goose/blog/2025/12/15/code-mode-mcp/
- Goose dev.to explainer: https://dev.to/goose_oss/code-mode-doesnt-replace-mcp-heres-what-it-actually-does-3hga

## Team verdict (council + redteam, 2026-11-28)

Three independent workers reviewed the research against our stack (computer-use-wayland, RDP lane, MCP tooling, agent fleet). All three reached the same verdict:

**NO ACTION on adopting Code Mode.** Do not adopt Dynamic Worker Loader, @cloudflare/codemode, MCP Server Portals, or a self-hosted workerd sandbox. The core pattern is already embodied in our stack via CLIs + exec/Python.

### Council seat 1 (architecture / fit): NO ACTION

1. Wrong bottleneck. Code Mode solves MCP tool-definition token bloat (2,500+ endpoints, 1.17M tokens). Our bottleneck is browser driving (wait/see/act over Firefox RDP); our MCP surface is small (hundreds to low thousands of tokens of definitions). Anthropic's own later measurement (43,588 to 27,297 tokens) shows the 98.7% headline only appears at extreme tool counts.
2. Stateful visual work does not batch like API chaining. RDP lane work is sequential and judgment-dependent: P1 snapshot, P2a ambiguity refusal, and P4 wrappers all require seeing intermediate state before the next action. A blind multi-step execute() would violate the P2a refusal design and the normal-user test rule (evidence must show entry, navigation, action, resulting state). Code Mode does not fix the P3 event-feed timing problem either.
3. Sandbox model incompatible with the laptop-local fleet. Isolates have no filesystem, no env vars, no external fetches, bindings only. Our fleet needs filesystem, local binaries, SSH via ~/workspace/ssh-laptop.sh, RDP sockets to Zen, screenshots, long-lived state. Self-hosting workerd brings the Check Point findings (5 memory-corruption bugs in C++ glue, 2 Critical) plus sandbox limits/monitoring overhead.
4. Runtime mismatch. @cloudflare/codemode targets TypeScript on Workers; our RDP lane and tooling are Python/CLI-first. Adopting a JS isolate runtime means rewriting RDP, Spaces/Folders, and snapshot bindings in a second language for no measured gain.
5. We already run the pattern. Cloudflare's own alternatives include CLIs; zen_cli.py plus exec is effectively the "typed API + one execute surface" Code Mode proposes, without the isolate.

Borrowable ideas: (A) progressive disclosure via a search() discovery tool, only if the MCP surface ever exceeds roughly 30-50 tools (trigger not met today); (B) formalize in briefs for non-visual chains: one script that calls the CLI multiple times and returns only the summary; (C) bindings-hide-secrets is already satisfied by Secure Vault and credential flows.

### Council seat 2 (performance / cost / measured value): NO ACTION

1. Where it would save in theory: tool-definition tokens at scale (we do not spend them); intermediate results kept out of context (agents already filter locally with exec/Python; P1 snapshot is already capped at 25,919 B, the same order as Code Mode's 6,000-token result cap); fewer think-steps for deterministic chains (already collapsed into P4 wrappers and zen_cli.py commands).
2. Where it would not save: browser driving is observe-act-observe; the next click depends on visual state and ambiguity checks, so chains cannot be pre-written. Screenshots and DOM state dominate tokens, not tool schemas. Anthropic's realistic measured saving is 37% on API-research tasks; applied to the tool-definition slice of our context it yields under 1% total token saving and 0% wall-time saving.
3. Locality kills the cloud variant: Dynamic Workers run in Cloudflare edge isolates with no route to the laptop's localhost RDP; tunneling owner browser control to Cloudflare would add tens to hundreds of ms per call against a 3.5ms local wait-class and break the local-only data principle. The laptop itself, via exec, is already our sandbox, with full local access and no isolate cost.
4. Adoption cost: $5/month plan plus per-Worker charges for an incompatible service; weeks of engineering to port the RDP surface to a typed TypeScript API and dual-maintain it; new ops burden (sandbox limits, monitoring, workerd patch cadence) the team does not have today; beta infrastructure with no measurement showing better.
5. Proposed instead (zero platform cost, measurable): keep investing in snapshot diffing / incremental snapshot and wait-class coverage; borrow the one useful principle locally: allow the agent to submit a small in-page JS predicate via the existing RDP evaluate to extract only needed DOM nodes before the snapshot returns, landing only if token/wall-time measurement on held-out tasks beats the P1 snapshot baseline. If a future lane ever exposes hundreds of tools, re-evaluate Anthropic Tool Search / dynamic tool search first.

### Redteam: REJECT for the core stack

1. Problem mismatch: tool surface is small and capped; Code Mode removes no wait or see; headline numbers compare a naive load-everything baseline against a best-case run.
2. Security regression: a single execute tool is a single prompt-injection target; Check Point chained workerd glue bugs to a sandbox escape from prompt injection to native code. Self-hosting means owning the patch treadmill with no-CVE opacity; managed Workers means owner browser state leaves the laptop. Exposing RDP control as a binding means reimplementing P2a refusal, tab hygiene, and read-only enforcement in TypeScript inside the binding layer. Under the standing full-access rule, a no-filesystem isolate alongside full-access exec is a fake boundary: the agent can bypass it with one exec call; restricting agents to the sandbox would break Codex/FCC/opencode shell workflows. Intermediates kept out of context are also kept out of the audit transcript unless every snippet and binding call is logged; the URL-leak class that helped kill P3 widens.
3. Reliability: GUI driving is stateful, timing-sensitive, adversarial (modals, challenges, focus steals). Blind 10-step scripts contradict see-act-verify; P2a refusal loses meaning inside a chain; fresh isolates force state serialization; the 6,000-token result cap truncates exactly the debugging output needed when a chain fails halfway, and re-runs may not be idempotent (double submit, double tab close). Two runtimes, two error models, zero wall-time gain.
4. Lock-in and hidden cost: beta-waived pricing is not a price; per-Worker-per-day billing at fleet scale is an open-ended meter; generated TS types must be maintained on every P-command change; exit cost is throwing away the binding layer and isolate harness. No evidence in the research of Code Mode proven for GUI automation, Wayland, or RDP driving.
5. Borrow narrowly: we already do the useful part (Python via exec to crunch snapshots and logs without flooding context). If tool count ever grows, adopt Tool Search first. If offline DOM crunching is needed on dedicated sessions, keep it in logged Python exec, not a JS isolate.

### Decision and next steps

- No adoption, no spike, no repo changes for Code Mode. Evaluation closed: "does not fit; pattern already covered by CLI + exec."
- Keep the CLI-first RDP lane architecture; continue the F11 narrow fix and the P1/P2a/P4 line on main (PR #1187).
- One borrowable principle worth a measured test later: in-page JS predicate via existing RDP evaluate to extract only needed DOM nodes before snapshot return, landed only if it beats the P1 baseline on held-out tasks.
- Revisit triggers only: tool-definition tokens become a measured bottleneck in our runs (roughly over 20k tokens of context per task), or a local Code Mode runtime gains first-class Python + RDP bindings with CVE transparency and per-call audit parity. Neither holds today.

Verdict recorded 2026-11-28. Nothing noteworthy requiring owner action; no owner input needed.
