# Skill Scout Registry

Owner order 2026-11-26 04:39: a dedicated team finds repos, skills, and tools,
evaluates fit per staff member, and equips each staff member with what suits them.
Coordinator: skill-scout subagent (reports to parent Muse only).
Hard rule (owner, 26/11 04:40): CHECK BEFORE INSTALLING. Always verify what is
already installed on the target machine first. Never install blindly.

Status legend: INSTALLED (verified on that machine) / PROPOSED (awaiting parent
approval) / NOT FIT / REJECTED (with reason) / UNKNOWN (not yet checked).

Scout lane files (full evidence, same directory):
- scout-skills-ecosystem.md (agent skills/plugins ecosystem)
- scout-mcp-tokens.md (MCP servers + token-saving tools)
- scout-browser-verify.md (browser/computer-use + verification tools)

## Staff roster (short)

- Muse (parent, VM): coordinator; skills in ~/workspace/custom-skills/ + /opt/muse/skills.
- Subagent workers (VM): coding, review, research; inherit parent skills.
- clone1, clone2 (separate Muse accounts, NO SSH): repo + web research only.
  clone1 token-capped (weekly reset Nov 30), use sparingly.
- mei, mochi (separate Muse accounts, NO SSH): repo work, research (last30days),
  scoring (mochi Pair A), analysis (mei).
- Codex (laptop CLI, gpt-6-luna): R3-L3 runner positions 32-55. Plugins via
  `codex plugin marketplace`. Verified 26/11: 70 skills in ~/.codex/skills/
  (incl. caveman family, ponytail, code-review, tdd, computer-use); plugins
  installed: browser, unified-computer-use, codex-app-tools, visualize;
  Playwright MCP enabled; no last30days.
- FCC / fcc-claude (laptop, Claude Code via FCC server): easy tasks only.
  Verified 26/11: only 6 skills in ~/.claude/skills (computer-use,
  diagnose-crash, last30days, omacal, omarchy, omarchy-app); only marketplace
  claude-plugins-official; own computer-use MCP connected.
- opencode (laptop CLI): cannot run yet (model pick pending; ONLY opencode/
  provider models allowed, never NVIDIA/Groq/OpenRouter). Verified 26/11:
  81 skills in ~/.config/opencode/skills/ (incl. caveman family, ponytail
  family); plugins dir has caveman/ + ponytail/.
- agy (laptop, herdr only): quota exhausted until ~28/11; skill state UNKNOWN.

---

## Equipped (installed and verified)

### 1. Ponytail

- Repo: https://github.com/DietrichGebert/ponytail
- License: MIT
- What: clean-code discipline skill for coding agents: smallest complete change,
  reuse before writing, stdlib/platform before dependencies, no unrequested
  abstraction, one small test for non-trivial logic, never cut validation,
  security, or error handling.
- Fits: ALL staff who write or review code (team-wide standing rule, owner
  order 26/11 04:36).
- Install status per staff:
  - Muse (VM): INSTALLED as skill at ~/workspace/custom-skills/ponytail/SKILL.md
    (+ AGENTS-ponytail.md). Verified on disk 26/11.
  - Subagent workers (VM): INSTALLED (inherit parent skills).
  - clone1, clone2: UNKNOWN (parent messaged the rule 26/11 via pwa-send;
    install state on their accounts not verified).
  - mei, mochi: UNKNOWN (asked directly 26/11 via daemon runs mei 34 /
    mochi 235; awaiting replies).
  - Codex (laptop): INSTALLED as skill folder in ~/.codex/skills/ (verified
    read-only 26/11 by ecosystem scout; 70 skills incl. ponytail). The Codex
    PLUGIN route is not installed; the skill folder covers the discipline.
    Correction to the earlier "Codex NO" note: that referred to the plugin,
    not the skill.
  - FCC (laptop): NOT INSTALLED (verified 26/11; 6 skills, no ponytail).
    PROPOSED: copy skill folder to ~/.claude/skills (low risk, but laptop
    change, parent approval required).
  - opencode (laptop): INSTALLED (ponytail family skills + plugin dir,
    verified 26/11). Activation effectiveness to check once opencode runs.
  - agy: UNKNOWN (quota exhausted; check after ~28/11).

### 2. Graphify

- Repo: https://github.com/Graphify-Labs/graphify
- License: Apache-2.0
- What: turns a codebase into a queryable knowledge graph (tree-sitter AST,
  local, deterministic, 0 LLM credits for code parsing). Agents query
  graph.json instead of re-reading the whole codebase; saves tokens.
- Fits: all staff who touch the computer-use-wayland codebase.
- Verification: CLI graphify 0.9.120 on VM via uv tool (PyPI graphifyy;
  binaries graphify + graphify-mcp in ~/.local/bin). Graph built at
  ~/workspace/cu-graphify/graphify-out/ (code-only AST: 7903 nodes, 16640
  edges, 430 communities; built from commit f58e341d). Query re-tested by
  skill-scout 26/11: pill/overlay subgraph returned correctly (253 nodes,
  BFS depth 2). Rebuild: `graphify . --code-only` then
  `graphify cluster-only .` after big code changes.
- Install status per staff:
  - Muse (VM) + subagent workers: INSTALLED (verified 26/11).
  - clone1, clone2, mei, mochi: UNKNOWN (remote repo work; check-first
    required before proposing).
  - Codex, FCC, opencode, agy (laptop): NOT INSTALLED. Laptop install is
    re-plan scope; PROPOSED only.

### 3. promptfoo (equipped by skill-scout 26/11, VM)

- Repo: https://github.com/promptfoo/promptfoo
- License: MIT
- What: local-first LLM evaluation CLI. YAML configs with deterministic
  assertions (contains, is-json, regex, javascript) stacked under
  LLM-as-judge rubrics (llm-rubric, g-eval, multi-judge voting). Runs
  locally; judge provider configured separately from the producer, so
  scorers stay independent of runners.
- Fits: mochi (scorer) + mei (analysis) conceptually; VM Muse + workers
  practically (installed here). Directly targets the FCC evidence-
  fabrication failure mode: deterministic checks verify exact claims,
  an independent judge grades the rest. NOT a replacement for snapshot.py
  evidence; pair with stored snapshots.
- Test result (skill-scout, VM, 26/11): `npm install -g promptfoo` ->
  0.126.0. Minimal eval with echo provider: `contains` assertion PASS
  (1 passed), `is-json` assertion correctly FAILED on non-JSON output.
  Assertion machinery proven both ways. (First npx attempt timed out at
  180s through the VM proxy; global install succeeded.)
- Install status:
  - Muse (VM) + subagent workers: INSTALLED (global npm, 0.126.0).
  - mei, mochi: UNKNOWN MCP/CLI capability; asked 26/11, awaiting reply.
    PROPOSED: encode 3-5 past R3-L3 rubrics (incl. one fabricated case),
    run against stored snapshots, compare with mochi verdicts.
  - Codex, FCC, opencode, agy: NOT INSTALLED; not needed there now.

### 4. agent-browser (equipped by skill-scout 26/11, VM)

- Repo: https://github.com/vercel-labs/agent-browser
- License: Apache-2.0
- What: native Rust CLI driving a browser one shell command at a time over
  CDP. `snapshot` returns compact accessibility-tree text with short refs
  (@e1); agent acts by ref. Version-matched skills, MCP mode, session
  persistence. Clicks fail loudly when target hidden/disabled/covered
  (anti-fabrication property).
- Fits: Muse VM workers (local fixtures), Codex, FCC. Matches the team
  ladder (CLI first, code-exec second, vision last) and token-efficiency
  goal. clone1/clone2/mei/mochi could use it for web research (runs
  anywhere, no laptop needed).
- Test result (skill-scout, VM, 26/11): `npm install -g agent-browser` ->
  0.45.0. Local page test: opened file:///tmp/scout-test.html, snapshot
  returned heading/button/textbox with refs e1-e3, clean close. External
  site (example.com) FAILED with ERR_TUNNEL_CONNECTION_FAILED: known VM
  egress-proxy limitation (AGENTS.md 2026-11-10 W-MOTION), not a tool
  defect. VM use is therefore local-pages/fixtures only unless the
  forward-proxy workaround is used.
- Hard limitation: Chrome/Chromium default. Zen is Firefox-based; the
  Firefox-engine path exists in docs but is UNVERIFIED for Zen. Weak vs
  Cloudflare per third-party reviews. Does NOT solve the Zen Cloudflare
  problem.
- Install status:
  - Muse (VM) + subagent workers: INSTALLED (global npm, 0.45.0).
  - Codex, FCC (laptop): NOT INSTALLED (verified 26/11). PROPOSED: laptop
    install test (direct internet there) vs current BiDi path on held-out
    tasks; answer the Zen/Firefox question in a sandbox first. Parent
    approval required (laptop change).
  - clone1, clone2, mei, mochi: UNKNOWN; PROPOSED for web research tasks.

### 5. last30days (already equipped; update pending)

- Repo: https://github.com/mvanhorn/last30days-skill
- License: MIT
- What: research skill; searches Reddit, X, YouTube, TikTok, HN,
  Polymarket, GitHub, arXiv and ~20 sources in parallel, scores by
  engagement, synthesizes a cited brief. Team research standard.
- Install status:
  - Muse (VM): INSTALLED v4.5.0 at ~/workspace/custom-skills/last30days.
    Upstream is v4.6.0 (SKILL.md read 26/11). UPDATE BLOCKED: the cloned
    upstream content failed a runtime execution-risk check; per security
    policy it must not be copied/installed without owner approval. PROPOSED:
    parent decides the update path (e.g. npx skills add, or approve the
    clone copy).
  - FCC (laptop): INSTALLED (one of its 6 skills; version not read).
  - Codex, opencode (laptop): NOT INSTALLED (verified 26/11). PROPOSED:
    Codex install via `npx skills add mvanhorn/last30days-skill -g` so
    Codex research tasks get the same brief quality.
  - mei, mochi: asked 26/11 (daemon runs 34/235), awaiting replies.
  - Warning from upstream README: marketplace + npx copies do not dedupe;
    pick one install method per machine.

### 6. Playwright MCP (already equipped for Codex)

- Repo: https://github.com/microsoft/playwright-mcp
- License: Apache-2.0
- Status: INSTALLED + enabled for Codex on the laptop (verified 26/11:
  isolated/headless Chromium at /usr/bin/chromium; playwright CLI 1.65.1
  via mise). Vendor's own README says Playwright CLI + SKILLS is more
  token-efficient than MCP for coding agents. PROPOSED: usage shift to
  CLI + SKILLS for Codex coding-agent work, measured against the MCP path
  on held-out tasks. No new install needed. Not for VM/FCC without a
  named task.

---

## Proposed (needs parent approval; laptop or account changes)

### 7. openai/codex-plugin-cc (for FCC) - highest leverage

- Repo: https://github.com/openai/codex-plugin-cc
- License: OpenAI official plugin (confirm LICENSE before vendoring).
- What: runs the local Codex CLI from inside Claude Code: /codex:review
  (read-only), /codex:adversarial-review, /codex:rescue, background jobs,
  optional Stop-hook review gate.
- Fits: FCC exclusively. FCC has 6 skills and no independent reviewer;
  Codex is already installed + authenticated on the laptop, so one
  marketplace add gives FCC independent Codex reviews, serving the
  no-self-review rule and R3-L3 scoring discipline.
- Status: NOT INSTALLED (verified 26/11: FCC marketplaces = only
  claude-plugins-official). Install: `/plugin marketplace add
  openai/codex-plugin-cc`, `/plugin install codex@openai-codex`,
  `/codex:setup`. Keep the review gate OFF until measured (loop + quota
  risk). PROPOSED install test: /codex:review --background on one real
  computer-use-wayland diff vs independent_review skill output.

### 8. anthropics/skills: webapp-testing + skill-creator (single folders)

- Repo: https://github.com/anthropics/skills
- License: per-skill Apache-2.0 (18 of 19 folders; doc-coauthoring none).
- What: webapp-testing = Playwright reconnaissance-then-action testing of
  local web apps (with_server.py helper). skill-creator = author/test/
  optimize new skills with an A/B eval harness. (mcp-builder also exists;
  relevant if computer-use-wayland tools are exposed as an MCP server.)
- Fits: webapp-testing for VM workers + Codex + FCC (frontend-kit and
  web-fixture verification without vision-token burn). skill-creator for
  the skill-scout team itself: future adoptions measured, not vibes.
- Status: NOT INSTALLED anywhere (verified 26/11: VM, FCC, Codex,
  opencode all lack both). PROPOSED: copy single folders only (not the
  12-skill bundle); webapp-testing needs `pip install playwright` +
  `playwright install`. Test on a frontend-kit fixture; run skill-creator
  eval on one existing custom skill before trusting it.

### 9. Caveman skill-only (for FCC + VM)

- Repo: https://github.com/JuliusBrussee/caveman
- License: Apache-2.0
- What: terse-output skill family (cuts filler, keeps code/commands
  exact) + a local proxy half (input compression, Auto routing). Honest
  README numbers: /caveman ~3% shorter than "Answer concisely",
  ultracave ~35%; proxy measured 33.2% fewer input tokens on 6 synthetic
  tasks (vendor numbers, treat as claims).
- Status: laptop Codex + opencode ALREADY HAVE the skill family
  (verified 26/11). VM: NOT INSTALLED. FCC: NOT INSTALLED. PROPOSED:
  skill-only install for FCC + VM (`npx skills add JuliusBrussee/caveman
  -g`), cheap and reversible. DEFER the proxy/Auto router (sits between
  agent and provider; needs its own measured A/B). clone1 is
  token-capped; if its account can install skills, caveman is a fit
  (UNKNOWN until asked).

### 10. Context7 (for Codex first, then FCC)

- Repo: https://github.com/upstash/context7
- License: MIT (MCP server source only; API backend/index is private
  Upstash infrastructure).
- What: fetches current, version-specific library docs into context.
  Two MCP tools (resolve-library-id, query-docs) or CLI + Skills mode
  (`npx ctx7 setup`). Attacks hallucinated-API retries on fast-moving
  APIs (Wayland, Hyprland, Playwright, Rust crates).
- Status: NOT INSTALLED anywhere (verified 26/11). Needs one free API
  key from context7.com/dashboard (parent to create; scout does not
  create accounts). PROPOSED: Codex first in CLI + Skills mode (fits
  CLI-first ladder, no MCP schema bloat), measure retries + tokens on
  held-out tasks; then FCC. VM workers can use CLI mode via exec if
  needed. NOT for mochi scoring (scoring judges submitted evidence).

### 11. obra/superpowers (one-harness A/B on Codex)

- Repo: https://github.com/obra/superpowers
- License: MIT
- What: 15 composable SKILL.md workflows (brainstorming, writing-plans,
  subagent-driven-development, TDD, code review, systematic debugging,
  etc.) with a SessionStart bootstrap hook. Emphasizes red/green TDD,
  YAGNI, DRY.
- Status: NOT INSTALLED anywhere (verified 26/11; Codex lists
  superpowers@openai-curated-remote v7.0.1 as not installed). Overlap
  risk: ponytail + existing tdd/code-review skills already cover parts;
  superpowers mandates worktrees + TDD deletions that may friction with
  ponytail's smallest-change rule. PROPOSED: install test on Codex only,
  one held-out task with/without, compare tokens + review quality. Do
  not roll to FCC/VM until that passes.

### 12. Serena (bounded Codex test)

- Repo: https://github.com/oraios/serena
- License: SPLIT - SolidLSP MIT; Serena app GPL-3.0-or-later. Tool use is
  fine; NEVER vendor/link its code into computer-use-wayland (copyleft).
- What: IDE-like semantic tools over MCP (find symbol, references,
  rename, replace symbol body, diagnostics) via language servers (40+
  languages). Complements Graphify (read path) with a write path.
- Status: NOT INSTALLED (verified 26/11; uv present on both machines).
  PROPOSED: bounded Codex test only (one language server, one held-out
  refactor: rename + reference update) vs Graphify + grep + edit
  baseline, tokens/time/errors. Council + redteam gate before wider
  rollout. Reject the paid JetBrains backend.

### 13. Chrome DevTools MCP (Codex only, slim + telemetry off)

- Repo: https://github.com/ChromeDevTools/chrome-devtools-mcp
- License: Apache-2.0 per secondary summary (confirm LICENSE before
  install).
- What: drives live Chrome via Puppeteer/CDP: console, network,
  performance traces, Lighthouse, memory. ~29 tools; --slim mode exists.
  Telemetry ON by default.
- Status: NOT INSTALLED (verified 26/11). PROPOSED: Codex-only trial
  with `--slim --no-usage-statistics --no-performance-crux` on one real
  frontend debug task vs the vision path. Chrome-only support: does NOT
  fix the Zen Cloudflare problem.

### 14. wshobson/agents (2 plugins for FCC)

- Repo: https://github.com/wshobson/agents
- License: MIT (free catalog; ignore the paid "Verified" layer).
- What: multi-harness plugin marketplace (93 plugins, 199 agents, 185
  skills). Relevant: developer-essentials, security-scanning,
  python-development, plugin-eval.
- Status: NOT INSTALLED anywhere (verified 26/11). PROPOSED: install
  developer-essentials + security-scanning for FCC only, run one PR
  review through each vs current FCC output. REJECT bulk install
  (context bloat, duplicates existing code-review/tdd skills).

### 15. agnix (from agent-sh/agentsys) - trial only

- Repo: https://github.com/agent-sh/agentsys (agnix is the standalone
  linter sibling)
- License: MIT
- What: deterministic linter for agent configs (SKILL.md, CLAUDE.md,
  AGENTS.md, hooks, MCP) against 455-757 rules with autofixes, CLI + LSP.
- Status: NOT INSTALLED (verified 26/11). PROPOSED: read-only trial over
  ~/workspace/custom-skills/ + laptop skill dirs; adopt as a
  pre-commit-style check only if it catches real breakage. REJECT full
  agentsys (/foreman duplicates our governance skills).

### 16. Semgrep CE + reviewdog (install test blocked, retry later)

- Repos: https://github.com/semgrep/semgrep (engine LGPL-2.1; rules
  license restricts redistribution of official packs; own rules are ours)
  + https://github.com/reviewdog/reviewdog (MIT).
- What: deterministic static gates (ydotool ban, PII patterns, banned
  imports) with no LLM in the loop; reviewdog posts findings as PR
  annotations. Complements gitleaks/trufflehog already on the VM.
- Test result (skill-scout, VM, 26/11): `uv tool install semgrep`
  FAILED 3 attempts - VM proxy HTTP timeouts on PyPI dependency downloads
  (semantic-version, requests, attrs). Not a tool defect; install test
  to retry when the proxy cooperates, or on the laptop (parent approval).
- Status: NOT INSTALLED (verified 26/11). PROPOSED: retry install, write
  3 starter rules, measure false positives on computer-use-wayland;
  add reviewdog in the same change if Semgrep lands in CI.

### 17. Inspect AI (long-term scoring harness, later)

- Repo: https://github.com/UKGovernmentBEIS/inspect_ai
- License: MIT
- What: Python eval framework (UK AISI): Task = Dataset + Solver +
  Scorer; sandboxed execution; transcript replay; 200+ pre-built evals.
  Structural scorer independence; matches the anti-"hoc tu" held-out
  rule. Heavier than promptfoo.
- Status: NOT INSTALLED (verified 26/11). PROPOSED LATER: adopt only if
  promptfoo's rubric test works but scoring outgrows YAML configs. Do
  not install both at once (Ponytail).

### 18. Stagehand browse CLI (second browser candidate, test vs agent-browser)

- Repo: https://github.com/browserbase/stagehand
- License: MIT
- What: SDK + `browse` CLI for browser agents (act/observe/extract);
  observe returns real selectors so credentials never reach the model.
  Chrome/Chromium-centric; cloud features paid.
- Status: NOT INSTALLED (verified 26/11). PROPOSED: test the browse CLI
  on the VM against agent-browser on the same held-out tasks; pick one,
  do not equip both.

---

## Rejected (deliberate, with reasons)

- **Anchor Browser** (anchorbrowser): cloud-only paid Chromium fleet,
  API key in CDP URL, credentials leave the machine. Cannot drive the
  owner's real Zen. Rejected.
- **browser-use as a driver** (browser-use/browser-use, MIT): heavier
  duplicate of agent-browser (Pydantic AI stack, fast-breaking API,
  cloud upsell, Chromium-only). Not installed anywhere (brief's "may
  already be known" is false; treat as unevaluated). Rejected as driver;
  revisit only for a self-contained autonomous-loop task. Its built-in
  Judge uses the same model that ran the task, so it is NOT an
  independent scorer.
- **MCP reference-server bundle** (modelcontextprotocol/servers):
  Filesystem/Git/Fetch/Memory duplicate VM built-ins and connectors;
  reference implementations, not production. Rejected as installs; keep
  as code reference only.
- **LLMLingua** (microsoft/LLMLingua, MIT): lossy prompt compression;
  heavy deps (torch + model download); weak maintenance signal (last
  news Dec 2024); README's own example shows garbled output at high
  ratios. Graphify already solves code context deterministically.
  Rejected for code and scoring evidence (auditability). Revisit only
  for a measured prose bottleneck.
- **computer-use-linux MCP as a runtime** (agent-sh/computer-use-linux):
  uses ydotool/ydotoold as deterministic fallback (team ydotool BAN) and
  does not satisfy the pill-on-any-control rule. Rejected as runtime.
  PROPOSED instead: read-only design study (doctor report, semantic
  selectors, tool annotations, context scoping) for the
  computer-use-wayland backlog; verify license first.
- **NikiforovAll/opencode-marketplace**: 15-star bespoke installer;
  standardize on `npx skills add` / `gh skill` instead. Rejected.
- **GitHub MCP for VM**: duplicates the connected Hatch GitHub connector
  + gh CLI; ~90-tool schema cost. Rejected for VM. Conditional Codex
  trial (remote, read-only, minimal toolsets) only if laptop `gh` auth
  turns out missing (not yet checked).
- **Scrapling for Zen**: already rejected 25/11 (Patchright is
  Chromium-only, Zen is Firefox-based). Not re-proposed.

## Deferred / parked

- **Steel Browser** (steel-dev/steel-browser, Apache-2.0): self-hostable
  browser sandbox (Docker). Parked: needs a concrete parallel-session
  use case; unauthenticated ports need a loopback plan. Beta.
- **Exa MCP** (exa-labs/exa-mcp-server, MIT): hosted search/fetch.
  Deferred pending one fact: can mei/mochi/clone accounts run MCP
  servers? Asked mei + mochi 26/11, awaiting replies. If yes, propose a
  research bake-off vs current search.
- **Firecrawl MCP** (firecrawl/firecrawl-mcp-server, license NOT
  verified): hosted scraping, credit cost, token-blowup risk, feedback-
  tool telemetry pattern. Deferred until a concrete JS-heavy research
  failure. Rejected for evidence capture (third-party transformation).
- **dogtail / AT-SPI**: Wayland accessibility-tree automation research
  spike only. gnome-ponytail-daemon is GNOME Shell-specific; laptop runs
  Hyprland, so the input bridge likely fails there. Read-only tree
  walking may still work. Timeboxed spike proposed; no laptop install
  during the paused run.

## Reference only

- **hesreallyhim/awesome-claude-code**: curated discovery index (not an
  install). Next scout lane should mine its Testing + Observability
  sections. Never bulk-install from it; audit entries individually.

---

## Open unknowns (check-first, do not guess)

1. Can clone1, clone2, mei, mochi run MCP servers? Asked mei (run 34) +
   mochi (run 235) on 26/11; awaiting replies. clone1/clone2 not asked
   yet (clone1 token-capped; ask when a concrete need appears).
2. Can the VM Muse lane attach arbitrary MCP servers, or only Hatch
   connectors? Affects Context7/Exa fit for VM workers (CLI modes
   sidestep this).
3. Does laptop Codex have working `gh` auth? Decides GitHub MCP.
4. License files not yet opened: chrome-devtools-mcp, firecrawl-mcp-
   server, computer-use-linux, codex-plugin-cc. Confirm before install.
5. FCC last30days version (not read); bun presence on laptop (not
   confirmed); agy skill state (quota until ~28/11).
6. Mei/mochi ponytail + caveman install state (asked 26/11).

## First-pass summary (2026-11-26)

- Equipped by skill-scout on the VM: promptfoo 0.126.0 (tested both
  ways), agent-browser 0.45.0 (tested; VM external browsing proxy-
  blocked, local fixtures fine).
- Already equipped (verified): Ponytail (VM, Codex skill, opencode;
  FCC missing), Graphify (VM), last30days (VM 4.5.0, FCC; Codex +
  opencode missing), Playwright MCP (Codex), caveman skills (Codex +
  opencode).
- Blocked: last30days 4.6.0 update (execution-risk check on cloned
  content; needs owner approval path). Semgrep install (VM proxy
  timeouts, 3 attempts).
- Top proposals for parent: codex-plugin-cc for FCC; webapp-testing +
  skill-creator single-folder installs; caveman skill-only for FCC+VM;
  Context7 for Codex; ponytail skill folder for FCC.
