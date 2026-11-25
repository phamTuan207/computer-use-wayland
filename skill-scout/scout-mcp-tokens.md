# Skill Scout: MCP Servers and Token-Saving Tools

Scout date: 2026-11-26 (Asia/Ho_Chi_Minh). Worker: skill-scout (MCP/tokens lane).
Scope: MCP servers and token/context tools that could make staff faster, more
accurate, or cheaper in tokens. Ponytail and Graphify are already equipped and
are not re-scouted, except where a candidate overlaps them.

How this file was checked (evidence standard):
- VM state checked 2026-11-26: `~/.local/bin` listing, `which` checks, node
  v24.22.1, npm/npx 10.9.4, python 3.12.3, uv 0.13.10 at `~/.local/bin/uv`,
  graphify 0.9.120 plus `graphify-mcp` present, `pip show llmlingua
  serena-agent` not found, npm global empty, none of serena/playwright/
  chrome-devtools/computer-use-linux/firecrawl-mcp/ctx7 on PATH.
- Existing Hatch connectors on the VM already cover GitHub, Gmail, Google
  Calendar/Drive/Docs/Sheets, Notion, Slack, Places, and many others
  (`/opt/hatch/connectors/`). Any MCP server that only duplicates those is
  NOT FIT for the VM Muse lane.
- Laptop state verified read-only 2026-11-26 via `~/workspace/ssh-laptop.sh`
  (short commands, nothing changed): host `omarchy`; codex, claude, opencode,
  node, npx, uv, playwright present via mise shims; serena not present;
  node v26.13.1, uv 0.13.9, playwright 1.65.1. Codex MCP list shows
  `playwright` enabled (local playwright-mcp, isolated/headless, Chromium at
  `/usr/bin/chromium`), `cua_repl` enabled, `codex_app` disabled. Claude MCP
  list shows `computer-use-session` connected (the team's own
  computer-use MCP at `~/.local/bin/computer-use-mcp` on the laptop). FCC skills
  on laptop: computer-use, diagnose-crash, last30days, omacal, omarchy,
  omarchy-app. No Context7, Serena, GitHub MCP, Chrome DevTools MCP, Exa, or
  Firecrawl MCP found in either list.
- Clone1, clone2, mei, mochi: whether those separate Muse accounts can run
  MCP servers at all is UNKNOWN. This file does not assume they can. Every
  "fits mei/mochi/clone" note below is conditional on confirming that first.
- Muse parent and subagent workers on the VM use Hatch tools and connectors.
  Whether the VM Muse lane can attach arbitrary npx/uvx MCP servers is also
  UNKNOWN from evidence gathered here. Candidates below are therefore rated
  primarily for the verified MCP-capable lanes: Codex (laptop) and FCC /
  fcc-claude (laptop Claude Code). VM Muse fit is marked NOT FIT or UNKNOWN
  honestly rather than assumed.
- Opencode cannot run yet (model pick pending; only `opencode/` provider
  models allowed). Agy quota is exhausted until about 28/11. Both are
  deferred for every candidate.
- No candidate was installed by this scout. Report only, per check-before-
  installing rule (owner, 26/11 04:40).
- Token and speed numbers from vendors and papers are claims, not facts.
  Each candidate notes where the claim is vendor-curated or benchmark-bound.

---

## 1. Model Context Protocol reference servers (Filesystem, Git, Memory, Sequential Thinking, Fetch, Time)

- Name: modelcontextprotocol/servers (reference bundle)
- Repo URL: https://github.com/modelcontextprotocol/servers
- License: Apache License 2.0 for new contributions, existing code under MIT
  (README license section; GitHub license field shows NOASSERTION because of
  the mix). Verified on repo page 2026-11-26.
- What it does: Official reference implementations, not production products.
  Current maintained set: Everything (test server), Fetch (web fetch to
  LLM-friendly text), Filesystem (scoped file ops), Git (repo read/search/
  manipulate), Memory (knowledge-graph persistent memory), Sequential
  Thinking (structured thought sequences), Time. The old GitHub, Google
  Drive, Slack, PostgreSQL, Puppeteer and others are archived. TypeScript
  servers run via `npx -y @modelcontextprotocol/server-*`; Python servers via
  `uvx` (for example `uvx mcp-server-git`, `uvx mcp-server-fetch`).
- Fits (which staff, why):
  - Muse VM + subagents: NOT FIT. Filesystem, Git, Fetch, and Memory all
    duplicate tools the VM lane already has (file read/write/edit, exec with
    git/gh, browser search/open, and the Muse memory system). Sequential
    Thinking adds structured reasoning the models already do natively;
    no evidence it improves accuracy for this team.
  - Codex / FCC (laptop): mostly NOT FIT for the same reason. Both already
    have native file, shell, and git tools. Fetch could help FCC on simple
    tasks, but FCC is restricted to the easiest tasks anyway.
  - Clone1/clone2/mei/mochi: UNKNOWN MCP capability; even if capable, the
    duplication argument applies.
- Install/check status: VM checked 2026-11-26: none installed, none needed.
  Node/npx and uv/uvx are present, so install would be trivial, but trivial
  is not a reason. Laptop verified: none of these in Codex or Claude MCP
  lists.
- Evidence: Repo page opened 2026-11-26 (92,248 stars, 5,280 commits, not
  archived). README warning read directly: servers are reference
  implementations for education, not production-ready solutions, and users
  must evaluate their own security requirements. Archived list confirms the
  old GitHub reference server is gone; do not install
  `@modelcontextprotocol/server-github` (unsupported since April 2025 per
  multiple secondary sources; use candidate 2 instead).
- Next step: REJECT as a bundle for all lanes. Keep only as a code reference
  if the team ever builds its own MCP server (for example, exposing
  computer-use-wayland over MCP). No install test.

## 2. GitHub MCP Server (official)

- Name: github/github-mcp-server
- Repo URL: https://github.com/github/github-mcp-server/blob/main/README.md
- License: MIT (per GitHub docs and multiple independent summaries checked
  2026-11-26; the README blob view opened here does not itself show a
  license field, so confirm the LICENSE file before any install).
- What it does: GitHub's official MCP server (Go). Read repos and code,
  manage issues and PRs, inspect Actions runs and logs, read Dependabot and
  code-scanning alerts. Two forms: remote hosted server at
  `https://api.githubcopilot.com/mcp/` (OAuth or PAT), or local Docker image
  `ghcr.io/github/github-mcp-server` / release binary (stdio). Tools are
  grouped in toolsets; defaults are context, repos, issues, pull_requests,
  users. Read-only mode is available (`--read-only` locally, readonly
  endpoint/headers remotely).
- Fits (which staff, why):
  - Muse VM + subagents: NOT FIT. The VM already has the Hatch GitHub
    connector (connected) plus `gh` CLI 2.102.0 logged in. An MCP duplicate
    adds a second credential path and a large tool schema for zero new
    capability.
  - Codex (laptop): CONDITIONAL FIT. Codex does repo work and PR review;
    structured GitHub tools could beat shelling out to `gh` for issue/PR/
    Actions triage. But Codex also has shell + gh access on the laptop
    (verify gh login there before assuming; not checked in this scout).
    Value is convenience, not new capability.
  - FCC (laptop): WEAK FIT. Easy tasks only; GitHub MCP write tools are
    more power than FCC tasks need.
  - Clone1/clone2/mei/mochi: UNKNOWN MCP capability. They already work on
    the repo through their own paths; do not assume.
- Install/check status: VM checked: not installed, not needed (connector +
  gh present). Laptop verified: not in Codex or Claude MCP lists. Remote
  form needs no local install but needs a PAT or OAuth app per host; local
  form needs Docker or a binary. Token cost warning: independent counts
  put the default surface at roughly 88-92 tools, over half of them write
  tools. That schema loads into context every session. If ever adopted,
  read-only mode plus a minimal toolset allow-list is mandatory.
- Evidence: README opened 2026-11-26 (remote vs local forms, OAuth-in-memory
  for local Docker, PAT handling guidance, toolset configuration). Star and
  release figures from secondary sources (about 33.5k stars, v2.0.2/v2.2.0
  in Oct-Nov 2026) indicate active maintenance; treat exact numbers as
  secondary-source claims.
- Next step: PROPOSE only as a scoped Codex trial (remote, read-only,
  repos+issues+pull_requests toolsets only), and only after confirming
  whether laptop Codex already has working `gh` access. If `gh` works,
  reject: Ponytail says reuse what exists. Never install for the VM lane.

## 3. Playwright MCP (and Playwright CLI + SKILLS)

- Name: microsoft/playwright-mcp (`@playwright/mcp`)
- Repo URL: https://github.com/microsoft/playwright-mcp
- License: Apache License 2.0. Verified on repo page 2026-11-26.
- What it does: Browser automation for agents via Playwright accessibility
  snapshots (structured tree with element refs) instead of screenshots or
  vision. Supports persistent or isolated profiles, CDP endpoint attach,
  allowed/blocked origins, headless mode, Docker image
  `mcr.microsoft.com/playwright/mcp`. Requires Node 20+. The same project
  now also ships Playwright CLI + SKILLS (`@playwright/cli`) aimed at
  coding agents.
- Fits (which staff, why):
  - Codex (laptop): ALREADY FIT AND INSTALLED. Verified 2026-11-26: Codex
    MCP list shows `playwright` enabled with isolated, headless, sandbox
    flags and Chromium at `/usr/bin/chromium`. Directly useful for
    frontend-kit checks and any browser verification in R3-L3 style tasks.
  - FCC (laptop): POSSIBLE FIT for simple browser checks, but FCC gets only
    the easiest tasks; add only if a concrete easy task needs it.
  - Muse VM + subagents: NOT FIT as an MCP install. VM subagents cannot
    operate a live browser; the parent lane already has browser tools.
    Playwright the library could still be used inside exec scripts, but
    that is a library choice, not this MCP server.
  - Clone1/clone2/mei/mochi: UNKNOWN MCP capability; browser work is not
    their lane (no SSH, repo + web research only).
- Install/check status: VM checked: `playwright` not on PATH, no global npm
  packages; not needed. Laptop verified: INSTALLED for Codex (see above);
  playwright CLI 1.65.1 present via mise. Not in Claude MCP list.
- Evidence: Repo page opened 2026-11-26 (40,143 stars, 637 commits, 76
  releases, created 2025-03-21, not archived). Critical token evidence from
  the vendor's own README: for coding agents, CLI + SKILLS is more
  token-efficient than MCP because MCP loads large tool schemas and verbose
  accessibility trees into context; MCP remains better only for persistent,
  exploratory, self-healing loops. That is the vendor arguing against its
  own MCP for our main use case. Believe it.
- Next step: KEEP the existing Codex MCP install for exploratory loops, but
  PROPOSE adding Playwright CLI + SKILLS for Codex coding-agent work and
  measuring tokens per task against the MCP path on the same held-out
  tasks. Do not add Playwright MCP to FCC or the VM without a named task.

## 4. Chrome DevTools MCP (Chrome DevTools for agents)

- Name: ChromeDevTools/chrome-devtools-mcp (`chrome-devtools-mcp`)
- Repo URL: https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/README.md
- License: Apache License 2.0 per secondary summary (dev.to, Apr 2026);
  LICENSE file was not opened in this scout, confirm before install.
- What it does: Google Chrome DevTools team's MCP server plus CLI. Drives a
  live Chrome via Puppeteer/CDP: navigate, click, type, fill forms, read
  console messages with source-mapped stacks, inspect network requests,
  record performance traces with actionable insights, Lighthouse/CrUX,
  memory snapshots, emulation. About 29 tools across input, navigation,
  performance, network, debugging, emulation, memory (secondary count).
  `--slim` mode exposes a reduced tool set for basic tasks. `--autoConnect`
  (Chrome M144+) attaches to an already-running Chrome, keeping logins and
  cookies. Ships agent skills (chrome-devtools, a11y-debugging,
  cookie-debugging, debug-optimize-lcp, memory-leak-debugging, etc.) and
  plugin installs for Claude Code and Codex.
- Fits (which staff, why):
  - Codex (laptop): FIT for frontend work. The team does frontend-kit and
    UI work where console/network/performance evidence beats screenshots.
    Complements Playwright MCP (deterministic tests) rather than replacing
    it (live debugging). Laptop has Chromium at `/usr/bin/chromium`.
  - FCC (laptop): WEAK FIT, easy tasks only; performance debugging is not
    an easy-task lane.
  - Muse VM: NOT FIT (no live browser for subagents; parent has browser
    tools).
  - Zen/Cloudflare note: this server officially supports Google Chrome and
    Chrome for Testing only; other Chromium browsers may work but are not
    guaranteed (README disclaimer). Zen is Firefox-based, so this does NOT
    fix the Zen Cloudflare problem. Do not sell it as that fix.
- Install/check status: VM checked: not installed (`chrome-devtools` not on
  PATH). Laptop verified: not in Codex or Claude MCP lists. Install is
  `npx -y chrome-devtools-mcp@latest` in MCP config; Node LTS + Chrome
  stable required. Privacy flags are mandatory for this team:
  `--no-usage-statistics` (telemetry is on by default) and
  `--no-performance-crux` (otherwise trace URLs go to Google CrUX API).
- Evidence: README opened 2026-11-26 (key features, disclaimers, telemetry
  opt-out, requirements, skills table, plugin commands for Claude Code and
  Codex). Secondary sources report weekly-ish releases (v0.21.0 by Apr
  2026, 43 releases in 7 months); treat cadence as a secondary claim, but
  the repo is clearly actively maintained by the Chrome team.
- Next step: PROPOSE a Codex-only trial with `--slim
  --no-usage-statistics --no-performance-crux` on one real frontend debug
  task, scored against the current screenshot/vision path for tokens and
  time. No FCC or VM install.

## 5. Context7 (up-to-date library docs)

- Name: upstash/context7 (`@upstash/context7-mcp`, CLI `ctx7`)
- Repo URL: https://github.com/upstash/context7
- License: MIT. Verified on repo page 2026-11-26. Note: the repo hosts the
  MCP server source only; the API backend, parsing, and crawling engines
  are private (README disclaimer). You are trusting Upstash's index.
- What it does: Fetches current, version-specific documentation and code
  examples for a named library and injects the relevant slice into the
  agent's context. Exactly two MCP tools: `resolve-library-id` (name to
  Context7 ID) and `query-docs` (ID + question to docs). Two modes: MCP
  server (hosted at `https://mcp.context7.com/mcp` or local via npx), or
  CLI + Skills mode (`npx ctx7 setup`, no MCP required). Free API key
  recommended for higher rate limits; OAuth also supported. Requires
  Node 22.13+ for the ctx7 CLI.
- Fits (which staff, why):
  - Codex (laptop): STRONG FIT. Codex writes and reviews code against
    fast-moving APIs (Wayland protocols, Hyprland, Playwright, Rust crates,
    Python libs). Stale training data is a real failure mode; versioned
    docs cut hallucinated-API retries, which is where the token saving
    actually comes from (fewer fix loops), even though each docs call
    itself costs tokens. Two-tool surface is tiny compared with GitHub
    MCP's ~90 tools.
  - FCC (laptop): FIT for the same reason on easy tasks; cheap to add.
  - Muse VM + subagents: UNKNOWN whether the VM lane can attach it. If it
    cannot, the CLI mode (`ctx7 library` / `ctx7 docs` via exec) is still
    usable by subagents as a shell tool, which fits the team's CLI-first
    priority ladder. That path needs no MCP support at all.
  - Clone1/clone2/mei/mochi: UNKNOWN MCP capability. CLI mode via their
    own shell (if any) is also UNKNOWN. Confirm before proposing.
  - Mochi scoring (R3-L3 Pair A): NOT FIT. Scoring must judge submitted
    evidence, not fetch fresh docs mid-score.
- Install/check status: VM checked: `ctx7` not on PATH, not installed.
  Laptop verified: not in Codex or Claude MCP lists. No API key exists yet;
  setup needs one free key from context7.com/dashboard (owner or parent to
  create; scout does not create accounts).
- Evidence: Repo page opened 2026-11-26 (65,461 stars, 1,283 commits, 192
  releases, created 2025-03-26, not archived). README read directly,
  including the private-backend disclaimer and the two-tool MCP surface.
  No token-saving percentage is claimed by the vendor; the claim is
  accuracy (no hallucinated APIs). That honesty raises credibility.
- Next step: PROPOSE as the first install test. Codex first, CLI + Skills
  mode preferred (avoids MCP schema load, matches CLI-first rule), MCP mode
  as fallback. Measure on held-out coding tasks: hallucinated-API retries
  and total tokens with vs without. Then FCC if Codex results hold.

## 6. Serena (semantic code navigation and editing)

- Name: oraios/serena (package `serena-agent`)
- Repo URL: https://github.com/oraios/serena/blob/HEAD/README.md
- License: SPLIT. SolidLSP component under MIT; Serena application under
  GPL-3.0-or-later; combined distributions are subject to the GPL (README
  license section, verified 2026-11-26). Contributions require a CLA. The
  GPL matters: using Serena as a tool is fine, but vendoring or linking its
  code into computer-use-wayland would trigger copyleft obligations. Keep
  it as an external tool only, never embed.
- What it does: IDE-like semantic tools over MCP: find symbol, symbol
  overview, find referencing symbols, rename, replace symbol body, insert
  before/after symbol, safe delete, diagnostics, plus basic file/search/
  shell utilities and a markdown memory system. Backed by open-source
  language servers (40+ languages, default) or a paid JetBrains plugin.
  Installed via uv (`uv tool install -p 3.13 serena-agent`, then `serena
  init`). Warns explicitly: do not install via MCP/plugin marketplaces
  (outdated commands).
- Fits (which staff, why):
  - Codex (laptop): CONDITIONAL FIT, highest potential and highest setup
    cost. computer-use-wayland is a large multi-language codebase where
    cross-file renames and reference lookups via grep are slow and
    error-prone. Serena's symbol tools target exactly that. Overlap with
    Graphify is partial: Graphify answers "what connects to what" from a
    prebuilt graph (read path, already installed); Serena performs precise
    edits and live LSP diagnostics (write path, not covered by Graphify).
    They complement; Serena does not replace Graphify.
  - FCC (laptop): NOT FIT. LSP indexing and symbolic refactoring exceed
    the easy-task lane.
  - Muse VM + subagents: UNKNOWN MCP capability. VM subagents already use
    Graphify for code context; Serena would need per-project LSP setup for
    each language in the repo (Rust, Python, shell, etc.), which is real
    work. Do not propose for VM until Codex proves value.
  - Clone1/clone2/mei/mochi: UNKNOWN MCP capability and UNKNOWN LSP
    availability in their environments. Do not propose.
- Install/check status: VM checked: `serena` not on PATH, `pip show
  serena-agent` not found. Laptop verified: `which serena` not found; not
  in Codex or Claude MCP lists. uv is present on both machines (VM 0.13.10,
  laptop 0.13.9), so the documented install path is available. Language
  servers for the repo's languages may need separate installs; not checked.
- Evidence: README opened 2026-11-26 (feature tables for retrieval,
  refactoring, symbolic editing; language list; uv install commands; GPL
  license split). Agent testimonials in the README ("single most impactful
  addition", "8-12 steps collapse into one call") are vendor-curated
  evaluations on vendor-chosen tasks. Treat as marketing, not measurement.
  No independent token benchmark was found in this scout.
- Next step: PROPOSE a bounded, measured Codex test only: one language
  server (the repo's main language), one held-out refactor task (rename +
  reference update), tokens/time/errors vs the current Graphify + grep +
  edit baseline. Council + redteam review before any wider rollout, per
  team rules. Reject the JetBrains paid backend (cost, no need).

## 7. LLMLingua / LLMLingua-2 (prompt compression)

- Name: microsoft/LLMLingua
- Repo URL: https://github.com/microsoft/LLMLingua
- License: MIT. Verified on repo page 2026-11-26.
- What it does: Python library (`pip install llmlingua`) that uses a small
  model (GPT2-small, LLaMA-7B, phi-2, or BERT/XLM-RoBERTa for LLMLingua-2)
  to score and drop non-essential tokens from a prompt before it reaches
  the main LLM. Variants: LLMLingua (general), LongLLMLingua (long context
  / RAG, reorder + dynamic ratio), LLMLingua-2 (task-agnostic, distilled
  from GPT-4, 3-6x faster than v1 per vendor), SecurityLingua (jailbreak
  guardrail). It is a preprocessing library, not an MCP server; using it
  means building and maintaining a compression step in our own pipeline.
- Fits (which staff, why):
  - Muse VM research workers: WEAK/DEFER. The plausible use is compressing
    long web/RAG dumps before summarization. But Graphify already solves
    the code-context version of this problem deterministically with zero
    LLM credits and no quality loss. For prose, the team's current path
    (search snippets + targeted page opens) already bounds input size.
  - Codex / FCC: NOT FIT. Neither lane has a place to insert a Python
    compression preprocessor without custom harness work, which violates
    Ponytail (smallest change, reuse first).
  - Mei/mochi research: UNKNOWN environment; heavy deps make it a poor fit
    for accounts we cannot inspect.
  - Scoring/verification: REJECT. Lossy compression of evidence before
    scoring destroys auditability. Mochi Pair A must see full evidence.
- Install/check status: VM checked: `llmlingua` not found (`pip show`
  empty, not on PATH). Install pulls torch + transformers and downloads a
  compressor model (hundreds of MB) on first run; CPU works, GPU faster.
  That is a heavy dependency for an unproven gain. Laptop: not checked for
  pip packages (only MCP lists and binaries were verified); mark UNKNOWN,
  but the fit argument already fails.
- Evidence: Repo page opened 2026-11-26 (6,860 stars, 91 commits, 8
  releases, created 2023-07-07; last news item Dec 2024, maintenance signal
  is weak for a 2026 adoption). Vendor/paper claims: up to 20x compression
  with minimal loss; LongLLMLingua RAG +21.4% using 1/4 tokens. Skepticism
  required: the README's own worked example shows visibly garbled output
  (merged words, broken numbers) at 11.2x. For code, numbers, and evidence
  text, that failure mode is disqualifying without task-specific testing.
  Typical prose compression in third-party skill writeups is 2-5x, not 20x.
- Next step: REJECT for now. Revisit only if a measured bottleneck appears
  (for example, repeated multi-page research dumps overflowing context)
  and only as an isolated experiment on prose, never on code or scoring
  evidence. Graphify remains the token-saving answer for code.

## 8. Exa MCP Server (web search and research)

- Name: exa-labs/exa-mcp-server
- Repo URL: https://github.com/exa-labs/exa-mcp-server
- License: MIT. Verified on repo page 2026-11-26.
- What it does: Hosted MCP server at `https://mcp.exa.ai/mcp` (also local
  npm package and Claude/Codex plugins). Default tools: `web_search_exa`
  (search with clean content) and `web_fetch_exa` (URL to markdown).
  Optional: `web_search_advanced_exa` (filters, domains, dates, subpage
  crawl) and `agent_run` (multi-step research/enrichment, needs auth).
  Anonymous use works with rate limits; OAuth or API key raises limits.
  Beta `dynamicHighlights` claims to return less text per result under a
  shared budget.
- Fits (which staff, why):
  - Mei / mochi / clone1 / clone2 (research lane): CONDITIONAL FIT, blocked
    on one unknown: whether those accounts can use MCP servers at all. If
    they can, Exa's code search and clean-fetch could complement
    last30days (which covers social/community signals Exa does not). If
    they cannot, this is moot. Ask them directly; do not assume (team rule
    from 24/11).
  - Codex (laptop): WEAK FIT. Codex already has web access paths; Exa adds
    a paid-credit dependency. Context7 (candidate 5) covers the docs need
    better.
  - Muse VM: NOT FIT. VM lane already has browser.search/open with source
    grounding rules. A second search vendor adds cost and a new trust
    boundary for no proven gain.
- Install/check status: VM checked: not installed, no Exa key. Laptop
  verified: not in Codex or Claude MCP lists. Hosted form needs no local
  install (URL config only), which is its main advantage. Cost: Exa API
  credits beyond anonymous limits; exact pricing not verified in this
  scout, check live before any adoption.
- Evidence: Repo page opened 2026-11-26 (5,269 stars, 452 commits, created
  2024-11-27, not archived, no releases/tags - distribution is via npm and
  the hosted endpoint). README tool table and auth section read directly.
  Dynamic Highlights token claim is vendor beta language ("less text
  reaches your agent's context"), not a measured benchmark.
- Next step: DEFER pending one fact: ask mei/mochi/clone accounts directly
  whether they can add MCP servers. If yes, propose a small research
  bake-off (Exa vs current search) on held-out queries with token counts.
  If no, reject without further work.

## 9. Firecrawl MCP Server (scrape, crawl, extract)

- Name: firecrawl/firecrawl-mcp-server (`firecrawl-mcp` on npm)
- Repo URL: https://github.com/firecrawl/firecrawl-mcp-server
- License: NOT VERIFIED on pages opened in this scout (DocSearch index page
  shows no license field). Confirm the LICENSE file before any install.
  Do not assume MIT.
- What it does: MCP bridge to Firecrawl's hosted scraping API. Tools
  include scrape (URL to clean markdown or schema-JSON), batch scrape,
  map (URL discovery), search, crawl (site-wide async), extract
  (structured JSON), interact (click/type in a real browser), parse (PDFs/
  docs), monitor (change diffs), and research indexes (papers, GitHub).
  Full profile lists roughly 27-34 tools (counts vary by version/profile).
  Hosted keyless tier at `https://mcp.firecrawl.dev/v2/mcp` exposes only
  scrape/search/parse with rate limits; full use needs an API key and
  credits. Local form: `npx -y firecrawl-mcp` with `FIRECRAWL_API_KEY`.
  Self-hosting Firecrawl itself is possible but heavy.
- Fits (which staff, why):
  - Research workers (VM subagents, mei/mochi if MCP-capable): NARROW FIT
    for JS-heavy pages where browser.open returns thin text, and for
    schema-JSON extraction that keeps responses small. The vendor's own
    guidance says prefer JSON schema mode; markdown mode only when full
    text is required, precisely because crawl/markdown responses blow up
    token budgets.
  - Codex / FCC: WEAK FIT. Browser automation is already covered by
    Playwright MCP (Codex, installed) and Chrome DevTools MCP (candidate
    4). Firecrawl's interact tool duplicates those with a credit meter
    attached.
  - Scoring/verification: REJECT for evidence capture. Hosted scraping
    adds a third-party transformation between source and scorer; R3-L3
    evidence must stay directly auditable.
- Install/check status: VM checked: `firecrawl-mcp` not on PATH, no key.
  Laptop verified: not in Codex or Claude MCP lists. Credit cost is the
  real install cost; keyless tier is rate-limited and tool-poor. Note from
  an independent Oct 2026 review: the server's docs instruct agents to
  call a search-feedback tool after searches (sends feedback to Firecrawl
  for a credit refund). That default telemetry-for-credits pattern must be
  disabled or explicitly approved before any use.
- Evidence: DocSearch index of the official repo opened 2026-11-26 (tool
  selection guide, JSON-vs-markdown guidance, keyless vs keyed endpoints,
  V1/V2 versioning). Search-result evidence confirms official status
  (firecrawl org, docs.firecrawl.dev, about 7,600 stars, active pushes in
  Oct-Nov 2026, npm 3.41.0). Multiple fork repos with identical READMEs
  pollute search results; only the firecrawl-org repo is official.
- Next step: DEFER. Propose only if a concrete research task fails on
  JS-heavy pages with current tools. If proposed, keyless tier first,
  JSON-schema mode only, feedback tool disabled, credit budget capped.
  Otherwise reject in favor of existing browser tools.

## 10. Computer-use MCP servers for Linux/Wayland (reference study only)

- Name: agent-sh/computer-use-linux (primary); also noted in search:
  kurojs/wayland-mcp, vadgr-computer-use, kwin-mcp
- Repo URL: https://github.com/agent-sh/computer-use-linux
- License: NOT VERIFIED on the DocSearch page opened in this scout.
  Third-party skill/package listings describe MIT, but the LICENSE file
  itself was not opened. Confirm before any use or code reuse. (The other
  Wayland MCPs found were not opened in depth; licenses unverified.)
- What it does: Rust MCP server + CLI for full Linux desktop control.
  Wayland-first via XDG portals (`org.freedesktop.portal.RemoteDesktop`),
  AT-SPI accessibility trees with semantic selectors (role/name/text),
  compositor-aware window registry (GNOME, KWin, Hyprland via hyprctl, i3,
  COSMIC), screenshots, click/drag/scroll/type/press-key, semantic actions,
  a `doctor` JSON readiness report, and an opt-in `run_shell` tool
  (`COMPUTER_USE_LINUX_ENABLE_SHELL=1`). Input fallbacks include `wtype`
  and ydotool 1.0.3+. No network listeners or telemetry per its security
  notes. This is a direct peer/competitor to our own computer-use-wayland.
- Fits (which staff, why):
  - As a runtime replacement for computer-use-wayland: REJECT. Two hard
    blockers. First, the team's standing ydotool ban: this server uses
    ydotool/ydotoold as its deterministic fallback and its setup docs tell
    users to enable ydotoold. Adopting it would require disabling that
    path and council approval; the ban exists because ydotool caused real
    harm in this project. Second, the team already has a working
    computer-use MCP on the laptop (FCC `computer-use-session` connected,
    verified 2026-11-26) plus the pill/overlay rules (pill must show on any
    agent control; raw CDP is read-only until pill-on-CDP exists). A
    third-party desktop controller does not satisfy those rules by default.
  - As a reference study for computer-use-wayland design: FIT. Its
    `doctor` readiness report, semantic-selector-first targeting,
    per-tool safety annotations (read-only vs destructive hints), scoped
    `get_app_state` to avoid context flooding, and portal-first input are
    exactly the problems our repo is solving. Reading its design (not
    copying code without a license check) is cheap and valuable.
  - Codex / FCC as an additional desktop tool: NOT FIT. Codex already has
    Playwright MCP for browsers; desktop control must go through our own
    stack so the pill, logging, and shutdown rules apply.
- Install/check status: VM checked: `computer-use-linux` not on PATH.
  Laptop verified: not in Codex or Claude MCP lists (Claude instead runs
  our own computer-use-session). Install paths documented (npm global,
  cargo, install script) were NOT run by this scout.
- Evidence: DocSearch index of the repo opened 2026-11-26 (tool catalog,
  architecture layers, Wayland input-focus guidance, safety annotations
  table, security considerations including ydotoold socket permissions).
  Search evidence also surfaced three sibling projects (wayland-mcp-kurojs
  with portal-first input and no privileged setup; vadgr-computer-use with
  tiered DOM/AT-SPI/pixel control; kwin-mcp with isolated virtual KWin
  sessions). Those siblings were not opened; treat their claims as
  unverified search snippets. One search result in this lane failed a
  safety check and was discarded without acting on it; this section rests
  only on the DocSearch page and the earlier unflagged search.
- Next step: PROPOSE a read-only design study (no install on the laptop,
  no ydotool anywhere): one worker extracts transferable ideas (doctor
  report shape, semantic selectors, tool annotations, context scoping)
  into a short memo for the computer-use-wayland backlog, with license
  verification as step one. Any live test would need council + redteam
  approval and a pill-compliant harness. Default verdict stays reject as
  a runtime.

---

## Ranked shortlist (top 3)

1. **Context7 for Codex (CLI + Skills mode first, MCP fallback), then FCC.**
   Smallest tool surface, directly attacks hallucinated-API retries on
   fast-moving Wayland/browser/Rust APIs, free tier exists, and CLI mode
   fits the team's CLI-first ladder without MCP schema bloat. Next step:
   parent creates one free API key, install test on Codex, measure retries
   and tokens on held-out tasks.
2. **Serena for Codex as a bounded measured test (one language server, one
   held-out refactor), complementing Graphify.** Highest ceiling for
   cross-file refactors in computer-use-wayland, but GPL-3.0 (tool use
   only, never embed), LSP setup cost, and vendor-curated evidence mean it
   must earn adoption with numbers, not testimonials. Council + redteam
   gate before wider rollout.
3. **Chrome DevTools MCP for Codex only, slim + telemetry off**
   (`--slim --no-usage-statistics --no-performance-crux`). Fills the live
   debugging gap (console, network, performance traces) that Playwright
   MCP does not cover, for frontend-kit work. Explicitly not a Zen
   Cloudflare fix (Chrome-only support). Trial on one real debug task vs
   the current vision path.

Honorable mentions, in order: Playwright CLI + SKILLS for Codex (vendor's
own token-efficiency guidance; MCP already installed, so this is a usage
shift, not a new install). Exa for mei/mochi/clone research, blocked until
their MCP capability is confirmed by asking them directly. GitHub MCP
(read-only, scoped) for Codex only if laptop `gh` access turns out to be
missing.

Rejected or deferred: reference-server bundle (duplicates built-ins),
LLMLingua (heavy, lossy, weak maintenance signal, Graphify already covers
code context), Firecrawl (credit cost, token blowup risk, feedback-tool
telemetry; defer until a concrete JS-heavy research failure), Wayland
computer-use MCPs as runtimes (ydotool ban + pill rules; design study
only).

Open unknowns for the coordinator:
- Can clone1, clone2, mei, mochi run MCP servers? Ask each directly.
- Can the VM Muse lane attach arbitrary MCP servers, or only Hatch
  connectors? Affects Context7/Exa fit for VM workers (CLI mode sidesteps
  this for Context7).
- Does laptop Codex already have working `gh` auth? Decides GitHub MCP.
- License files not yet opened: chrome-devtools-mcp, firecrawl-mcp-server,
  computer-use-linux. Confirm each before any install.
