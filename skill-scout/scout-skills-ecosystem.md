# Skill Scout: Agent-Skills Ecosystem Findings

Scout date: 2026-11-26 (Asia/Ho_Chi_Minh). Worker: skill-scout (ecosystem lane).
Coordinator: skill-scout subagent. Owner rule applied throughout: CHECK BEFORE
INSTALLING. Nothing was installed. Laptop state was verified read-only via
`~/workspace/ssh-laptop.sh` (short commands, no changes). VM state was checked
on disk. Every candidate below was opened on its repo page via browser.open
(or read via its README blob) for license, activity, and install method.

Already equipped, not re-scouted: Ponytail (DietrichGebert/ponytail, MIT) and
Graphify (Graphify-Labs/graphify, Apache-2.0). See REGISTRY.md.

## Baseline: what is already installed (verified 26/11)

VM (`~/workspace/custom-skills/`, `/opt/muse/skills/`, `~/.local/bin`):
- Custom skills (31): includes ponytail, last30days (v4.5.0), frontend-design,
  frontend-kit, frontend-judge, impeccable, taste-reference, gsap-* (7),
  threeui, ui-ux-pro-max-reference, omarchy, mobile-kit, plus governance and
  safety skills (independent_review, external_claim_verification,
  subagent_campaign_governance, local-subagent-delegation, etc.).
- `/opt/muse/skills` (57 bundled): no caveman, superpowers, webapp-testing,
  skill-creator, or playwright skill.
- `~/.local/bin`: graphify + graphify-mcp present. No caveman binary.

Laptop (read-only SSH, 26/11):
- FCC / fcc-claude `~/.claude/skills/`: computer-use, diagnose-crash,
  last30days, omacal, omarchy, omarchy-app (6 only). Plugin marketplaces:
  only `claude-plugins-official` (anthropics/claude-plugins-official).
  No superpowers, caveman, webapp-testing, skill-creator, wshobson, agentsys,
  or codex-plugin-cc installed for FCC.
- Codex: 70 skills in `~/.codex/skills/`, including the full caveman family
  (caveman, caveman-commit, caveman-compress, caveman-help, caveman-review,
  caveman-stats, cavecrew), ponytail, code-review, tdd, computer-use,
  chromium-cdp, diagnosing-bugs, research, and matt-pocock-style workflow
  skills (grill-me, to-spec, to-tickets, triage, wayfinder, etc.).
  Plugins installed+enabled: browser, unified-computer-use, codex-app-tools,
  visualize (all openai-bundled). Available but NOT installed:
  superpowers@openai-curated-remote v7.0.1, caveman@openai-curated-remote
  v2.7.0 (skills already present via folder copy), browser-use, browser-act.
  No last30days, webapp-testing, or skill-creator skill in Codex.
- opencode: 81 skills in `~/.config/opencode/skills/`, including caveman
  family, ponytail family (ponytail, ponytail-audit, ponytail-debt,
  ponytail-gain, ponytail-help, ponytail-review), code-review, computer-use,
  chromium-cdp, mouse-control, research, tdd. Plugins dir
  `~/.config/opencode/plugins/`: caveman/ and ponytail/ dirs present.
  No `installed.json`, so the opencode-marketplace CLI is not in use.
  No superpowers, last30days, or webapp-testing skill in opencode.
- agy 1.5.7 present; quota exhausted until ~28/11, skill state UNKNOWN.

Implication: the laptop CLIs (Codex, opencode) are already heavily equipped
with caveman + ponytail + matt-pocock workflow skills. The real gaps are
(1) FCC has almost nothing beyond computer-use + last30days, (2) nobody has
superpowers, webapp-testing, or skill-creator, (3) VM last30days is one
minor version behind upstream, (4) Codex lacks last30days.

---

## 1. anthropics/skills (official) - webapp-testing, skill-creator, mcp-builder

- Repo URL: https://github.com/anthropics/skills
- License: No repo-level license file; per-skill Apache-2.0 (18 of 19 folders
  carry Apache-2.0 LICENSE.txt as of 18 Nov 2026; doc-coauthoring has none).
  Document skills (docx, pdf, pptx, xlsx) moved to Apache-2.0 on 6 Nov 2026.
- What it does: Anthropic's public Agent Skills reference repo (19 skill
  folders + spec + template). The three that matter for us: `webapp-testing`
  (Playwright reconnaissance-then-action testing of local web apps, with
  `with_server.py` helper), `skill-creator` (author/test/optimize new skills
  with an A/B eval harness and trigger-description tuning), `mcp-builder`
  (4-phase workflow for building MCP servers). Also frontend-design,
  claude-api, doc-coauthoring, brand-guidelines.
- Fits: webapp-testing fits Muse VM subagents + Codex + FCC for verifying
  frontend-kit output and computer-use-wayland web fixtures without burning
  vision tokens on every click; the reconnaissance-then-action pattern
  (wait networkidle, inspect DOM, then act) matches our own grounding rules.
  skill-creator fits the skill-scout team itself (Muse parent + workers):
  every future skill we adopt or write should pass its eval harness instead
  of shipping on vibes. mcp-builder fits computer-use-wayland if we expose
  the Wayland tools as an MCP server for external agents.
- Install/check status: VM checked - webapp-testing NOT FOUND, skill-creator
  NOT FOUND (not in custom-skills or /opt/muse/skills). Laptop verified -
  neither skill in FCC (6 skills only), Codex (70 skills, no match), or
  opencode (81 skills, no match). Install: Claude Code
  `/plugin marketplace add anthropics/skills` then
  `/plugin install example-skills@anthropic-agent-skills` (bundle of 12), or
  copy single folders to `~/.claude/skills/`; webapp-testing also needs
  `pip install playwright` + `playwright install` (Chromium).
- Evidence: Opened https://github.com/anthropics/skills (200,471 stars,
  23,445 forks, 64 commits, created 2025-09-22, current commit e4bb5d9).
  README confirms Apache-2.0 for most skills including document skills,
  demo/educational disclaimer, and the marketplace install commands. Read
  `skills/webapp-testing/SKILL.md` via search result: decision tree,
  with_server.py, networkidle warning. Secondary check (GitHub API via
  2026-11-19 roundup): 197,294 stars then, last commit 16 Nov 2026.
- Next step: PROPOSE (install test, single skills not the whole bundle).
  Copy `webapp-testing` + `skill-creator` folders only, test webapp-testing
  against a frontend-kit fixture on the VM, and run skill-creator's eval on
  one existing custom skill (e.g. ponytail) before trusting it. Do not
  install document-skills (we already have documents tooling).

## 2. obra/superpowers

- Repo URL: https://github.com/obra/superpowers
- License: MIT
- What it does: A complete software-development methodology as 15 composable
  SKILL.md workflows with a SessionStart bootstrap hook that makes skills
  auto-trigger: brainstorming, using-git-worktrees, writing-plans,
  subagent-driven-development, executing-plans, test-driven-development,
  requesting-code-review, receiving-code-review, systematic-debugging,
  dispatching-parallel-agents, finishing-a-development-branch,
  diagnosing-superpowers, writing-skills, using-superpowers. Emphasizes
  red/green TDD, YAGNI, DRY.
- Fits: Codex (laptop, R3-L3 runner + computer-use-wayland coding) and FCC
  most directly, because both currently rely on ad-hoc prompting for
  plan/test/review discipline; superpowers would enforce plan-before-code
  and review-between-tasks. Muse VM subagents second: our
  local-subagent-delegation skill overlaps subagent-driven-development, so
  superpowers would need a merge decision, not a blind install. opencode
  later (blocked on model pick). agy supports it natively
  (`agy plugin install https://github.com/obra/superpowers`) once quota
  returns.
- Install/check status: VM checked - NOT FOUND. Laptop verified - Codex
  plugin `superpowers@openai-curated-remote` v7.0.1 is listed as
  "not installed"; no superpowers skill folder in Codex or opencode; FCC
  has no superpowers marketplace. Install per harness: Claude Code
  `/plugin install superpowers@claude-plugins-official`; Codex CLI
  `/plugins` then search superpowers; opencode via fetching
  `.opencode/INSTALL.md`; Muse via `muse plugins install ./superpowers`
  + approve (repo ships a native `.muse-plugin`).
- Evidence: Opened https://github.com/obra/superpowers (326,540 stars,
  28,972 forks, MIT, 687 commits, 17 releases, created 2025-10-09).
  README confirms 15 skills, 16 harnesses, per-harness install, and the
  bootstrap-hook design (skills are inert without it). Latest release
  v7.0.2 shipped 2026-11-03 per secondary coverage; last push 2026-11-03.
- Next step: PROPOSE with caution (install test on ONE harness first).
  Overlap risk is real: our ponytail rule + tdd/code-review skills on the
  laptop already cover parts of this. Test on Codex only (one-command
  plugin install, easy uninstall), run one held-out computer-use-wayland
  task with and without it, compare tokens + review quality. Do not roll
  to FCC/VM until that test passes. Note: superpowers mandates worktrees
  and TDD deletions that may conflict with our "smallest complete change"
  ponytail rule; the test must check for friction.

## 3. JuliusBrussee/caveman (token saving)

- Repo URL: https://github.com/JuliusBrussee/caveman
- License: Apache-2.0 (whole repo since 3.0.0; older releases MIT/BSL)
- What it does: Two halves. (1) A terse-output skill family (`/caveman`,
  `/ultracave`, `/megacave`, plus caveman-commit/review/compress/stats)
  that cuts filler from agent replies while keeping code/commands exact.
  (2) A local proxy ("Read less") that compresses logs/JSON/CSV/test
  output before the model reads them, plus Auto model routing and Blocks
  (reusable scripts). Honest numbers in README: `/caveman` is only ~3%
  shorter than "Answer concisely." (ultracave ~35%); the proxy measured
  33.2% fewer input tokens per session on 6 synthetic large-output tasks.
- Fits: Token saving is the fit. Codex and opencode on the laptop ALREADY
  have the skill half (verified: full caveman family in both skill dirs).
  The gap is the proxy half (input compression) which neither has as a
  running proxy, and FCC + VM Muse which have no caveman at all.
  clone1 is token-capped (weekly reset Nov 30) so any input-compression
  win matters there most, but clone accounts cannot be verified from here.
- Install/check status: VM checked - caveman NOT FOUND (no skill, no
  binary). Laptop verified - Codex skills: caveman family PRESENT;
  opencode skills: caveman family PRESENT + `plugins/caveman/` dir
  present; Codex plugin `caveman@openai-curated-remote` v2.7.0 NOT
  installed (folder skills cover it); FCC: no caveman. Skill-only install:
  `npx skills add JuliusBrussee/caveman -g`. Full toolchain:
  `npx @caveman-ai/cli@latest` (needs Node 22.13+, runs a local proxy -
  heavier, changes agent routing).
- Evidence: Read caveman README blob (v4.2.0, 22 Nov 2026): six rocks
  table with measured numbers, install commands, "rules cost ~1,160 input
  tokens" caveat. Search corroboration: ~122k stars, Apache-2.0, last
  commit 24 Nov 2026, JetBrains A/B (86 tasks, 8.5% fewer output tokens,
  no quality loss p=0.82) and Adobe CAVEWOMAN citation as reported in
  README. One fetch in this scout (caveman README) was flagged by the
  runtime safety check; no instructions from it were followed - facts
  above are cross-checked against search results and the laptop's own
  installed skill folders.
- Next step: PROPOSE skill-only for FCC + VM (cheap, reversible); DEFER
  the proxy. The laptop already proves the skill half works in our setup.
  For FCC (easy tasks only, token-sensitive) the terse skill is a clear
  win. The proxy/Auto router is a bigger change (sits between agent and
  provider, Auto needs an account) - needs its own measured A/B on
  computer-use-wayland logs before adoption. Do not install the full CLI
  blind.

## 4. mvanhorn/last30days-skill (research/crawling) - already installed, update pending

- Repo URL: https://github.com/mvanhorn/last30days-skill
- License: MIT
- What it does: Research skill that searches Reddit, X, YouTube, TikTok,
  HN, Polymarket, GitHub, arXiv, Techmeme, and ~20 more sources in
  parallel, scores by engagement (upvotes/likes/odds), and synthesizes a
  cited brief. Python engine (127 lib files) + 17 reference guides.
  Keyless tier: Reddit, HN, Polymarket, GitHub. Needs Python 3.12+.
- Fits: mei + mochi (research duty) and Muse VM workers. Already the
  team's research standard. The question is not adoption but currency:
  VM has v4.5.0, upstream shipped v4.6.0 on 2026-11-22 (finished-brief
  capture + library feed). Codex has NO last30days at all, so Codex
  research tasks currently fall back to plain web search.
- Install/check status: VM INSTALLED at `~/workspace/custom-skills/last30days`
  v4.5.0 (SKILL.md verified, homepage points to upstream repo). Laptop
  verified - FCC HAS last30days (one of its 6 skills, version not read);
  Codex does NOT; opencode does NOT. Install/update: Claude Code
  `/plugin marketplace add mvanhorn/last30days-skill` + `/plugin install
  last30days`, or `npx skills add mvanhorn/last30days-skill -g` for
  Codex/other hosts. Warning from README: marketplace + npx copies do
  not dedupe (two `/last30days` entries) - pick one method per machine.
- Evidence: Opened https://github.com/mvanhorn/last30days-skill (75,031
  stars, 6,612 forks, MIT, 1,637 commits, 86 releases, created
  2026-01-23). README confirms source table, install paths, zero-config
  keyless tier. Independent test (AI Parabellum, v4.3.2): 107 items from
  8 sources keyless, ~2x cost/time vs plain Claude search ($1.14/5m24s
  vs $0.56/2m10s) but far better community signal.
- Next step: PROPOSE update + Codex gap-fill. Update VM copy 4.5.0 ->
  latest via the same method it was installed (folder copy; verify no
  duplicate entry). Install for Codex via `npx skills add ... -g` so
  Codex research tasks get the same brief quality. No action for FCC
  (already has it; check its version on next laptop pass).

## 5. wshobson/agents (multi-harness plugin marketplace)

- Repo URL: https://github.com/wshobson/agents
- License: MIT (free catalog; "Verified" is a separate paid layer by the
  maintainer's company - ignore it)
- What it does: One Markdown source generating plugins/agents/skills for
  Claude Code, Codex CLI, Cursor, OpenCode, Antigravity, Copilot, Pi.
  Catalog: 93 plugins, 199 agents, 185 skills, 103 commands. Relevant
  plugins for us: `developer-essentials` (code review, debugging, Git,
  testing), `security-scanning` (security review, dependency checks),
  `python-development` (Python/testing/packaging - computer-use-wayland
  is Python-heavy), plus a `plugin-eval` static checker for skills.
- Fits: FCC first (it has only 6 skills; developer-essentials +
  security-scanning would give it real review/security capability for
  easy tasks). Codex second (native marketplace route exists). Muse VM
  workers third, skills-only via `gh skill` / `npx skills` for single
  skills without the plugin machinery. Scoring/verification fit:
  plugin-eval + Verified scorecards show the maintainer measures pass
  rates, which matches our evidence standard.
- Install/check status: VM checked - NOT FOUND. Laptop verified - no
  wshobson marketplace in FCC (only claude-plugins-official), no
  wshobson plugins in Codex list output, no wshobson skills in opencode.
  Install: Claude Code `/plugin marketplace add wshobson/agents` then
  `/plugin install <plugin>@claude-code-workflows`; Codex
  `codex plugin marketplace add wshobson/agents`; skills-only
  `gh skill install wshobson/agents <skill>` (needs gh 2.90+) or
  `npx skills add wshobson/agents --skill <skill>`; opencode via clone +
  `make install-opencode`.
- Evidence: Opened https://github.com/wshobson/agents (42,890 stars,
  4,542 forks, MIT, 651 commits, created 2025-07-24). README confirms
  counts, multi-harness adapters, CI validation, and per-plugin install
  (only the installed plugin's files load into context - good for tokens).
- Next step: PROPOSE selective install test (2 plugins max). Install
  `developer-essentials` + `security-scanning` for FCC only, run one
  computer-use-wayland PR review through each, compare against current
  FCC output. Reject bulk install: 93 plugins would bloat context and
  duplicate our existing code-review/tdd skills on Codex/opencode.

## 6. openai/codex-plugin-cc (Codex reviews inside Claude Code)

- Repo URL: https://github.com/openai/codex-plugin-cc
- License: OpenAI official plugin (check repo LICENSE before vendoring;
  distributed via Claude Code marketplace). Requirements: ChatGPT
  subscription (incl. Free) or OpenAI API key, Node 18.18+.
- What it does: Runs the local Codex CLI from inside Claude Code:
  `/codex:review` (read-only review), `/codex:adversarial-review`
  (steerable challenge review), `/codex:rescue` (delegate a task),
  `/codex:transfer`, status/result/cancel for background jobs, and an
  optional Stop-hook review gate.
- Fits: FCC (laptop Claude Code) exclusively - it is the only Claude Code
  harness we run, and it currently has no independent reviewer. Our
  standing rule says Muse failures get independent review; this gives
  FCC-written code a Codex second opinion without window-switching, and
  gives the council/redteam flow a cheap adversarial pass. No fit for
  Codex itself (it IS Codex) or VM Muse (different harness).
- Install/check status: VM checked - NOT FOUND (and not applicable).
  Laptop verified - FCC marketplaces contain only claude-plugins-official;
  no openai-codex marketplace, so codex-plugin-cc is NOT installed for
  FCC. Codex CLI itself IS installed and authenticated on the laptop
  (plugin list worked), so the plugin's prerequisite is met. Install in
  Claude Code: `/plugin marketplace add openai/codex-plugin-cc`,
  `/plugin install codex@openai-codex`, `/reload-plugins`, `/codex:setup`.
- Evidence: Read the full README blob at
  https://github.com/openai/codex-plugin-cc/blob/HEAD/README.md: command
  table, read-only guarantees, background job flow, review-gate warning
  ("may drain usage limits quickly"), and the note that it reuses local
  Codex auth/config/checkout. Shipped 30 Mar 2026 by OpenAI engineers.
- Next step: PROPOSE install test for FCC, review gate OFF. Test:
  `/codex:review --background` on one real computer-use-wayland diff,
  compare findings vs our independent_review skill output. Keep the
  review gate disabled until measured (loop + quota risk). This is the
  highest-leverage single install for FCC.

## 7. agent-sh/agentsys (+ agnix linter)

- Repo URL: https://github.com/agent-sh/agentsys
- License: MIT
- What it does: Orchestration runtime + marketplace: 11 plugins, 5 agents,
  14 skills in the current README (older material says 24/49/44 across
  standalone repos). Commands: `/foreman` (work the GitHub issue queue
  with subagents), `/deslop` (clean AI slop), `/banthis` (durable
  negative memory), `/learn`, `/skill-curator`. Standalone sibling
  `agnix` lints agent configs (SKILL.md, CLAUDE.md, AGENTS.md, hooks,
  MCP) against 455-757 rules with autofixes, as CLI + LSP.
- Fits: agnix fits the skill-scout team + Muse parent: we now maintain
  31 custom skills + laptop fleets of 70-81 skills; a deterministic
  linter catches broken frontmatter/hooks before they silently fail
  (same philosophy as our PII pre-commit rule: deterministic check over
  prompt-only rule). `/deslop` fits code review for computer-use-wayland.
  `/foreman` overlaps our existing subagent governance - low priority.
- Install/check status: VM checked - NOT FOUND (no agentsys, no agnix
  binary in ~/.local/bin). Laptop verified - no agentsys marketplace in
  FCC, no agentsys skills in Codex/opencode lists. Install: Claude Code
  `/plugin marketplace add agent-sh/agentsys` then per-plugin install;
  or `npm install -g agentsys`; agnix also ships as its own CLI/LSP.
- Evidence: Search + repo metadata: 1,021 stars, 117 forks, MIT, 838
  commits, created 2026-01-15, latest release v6.1.1 (6 Oct 2026), last
  push 2026-11-09. README (via search excerpts) confirms command/skill
  tables and multi-platform support (Claude Code, Codex, OpenCode,
  Cursor, Kiro). Smaller and younger than superpowers/wshobson - treat
  as a tool pick (agnix), not a platform bet.
- Next step: PROPOSE agnix-only trial; REJECT full agentsys for now.
  Run agnix read-only over `~/workspace/custom-skills/` and the laptop
  skill dirs, count real findings. If it catches real breakage, adopt
  as a pre-commit-style check. Skip /foreman (duplicates our governance
  skills) and skip the marketplace until agnix proves out.

## 8. hesreallyhim/awesome-claude-code (discovery index, not an install)

- Repo URL: https://github.com/hesreallyhim/awesome-claude-code
- License: Other (NOASSERTION) - it is a curated list, not code to vendor
- What it does: Hand-curated index of Claude Code skills, hooks, slash
  commands, orchestrators, status lines, and tooling, backed by a CSV
  resource table (~226 resources). Sections include Skills, Testing,
  Security, Memory & Context, Observability, Agent Orchestration.
- Fits: The skill-scout team as a discovery source for future lanes
  (hooks, status lines, usage monitors). No staff member "uses" it at
  runtime.
- Install/check status: N/A (nothing to install). VM/laptop checks not
  applicable. Use via browsing the README_ALTERNATIVES views or the CSV.
- Evidence: Opened https://github.com/hesreallyhim/awesome-claude-code
  (58,802 stars, 5,020 forks, 2,483 commits, created 2025-04-19).
  Root files confirm CSV-backed generation (THE_RESOURCES_TABLE_NEW.csv,
  generate_readme.py). Caveat from roundups: no formal vetting process;
  entries must be audited individually (one entry's scripts contact
  Baidu/Yandex - read scripts before installing anything from the list).
- Next step: KEEP as reference. Next scout lane should mine its Testing
  + Observability sections for computer-use verification tooling.
  Never bulk-install from it.

## 9. NikiforovAll/opencode-marketplace (opencode plugin CLI) - defer

- Repo URL: https://github.com/NikiforovAll/opencode-marketplace
- License: MIT
- What it does: `bunx opencode-marketplace` CLI to install/update/list/
  scan opencode plugins (commands/agents/skills) from local dirs or
  GitHub URLs, with namespacing and an installed.json registry.
- Fits: opencode only. opencode currently cannot run (model pick
  pending, opencode/ provider only), and its 81 skills were installed
  by folder copy without this tool (no installed.json exists).
- Install/check status: VM checked - NOT FOUND (not applicable). Laptop
  verified - no installed.json in ~/.config/opencode/plugins/, so the
  tool is NOT in use; plugins dir holds caveman/ + ponytail/ only.
  Install would be `bun install -g opencode-marketplace` (bun presence
  on laptop not confirmed in this pass).
- Evidence: Opened https://github.com/NikiforovAll/opencode-marketplace
  (15 stars, 5 forks, 39 commits, 3 releases, created 2026-01-02).
  README confirms convention-based discovery and registry design.
  Very small adoption vs the `npx skills` / `gh skill` installers that
  every major collection already supports.
- Next step: REJECT for now. Standardize on `npx skills add` / `gh skill`
  (supported by anthropics, superpowers, wshobson, last30days, caveman)
  instead of a 15-star bespoke installer. Revisit only if opencode
  plugin management becomes a real pain after opencode can run.

---

## Ranked shortlist (top 3)

1. **openai/codex-plugin-cc for FCC** (candidate 6). Biggest gap, smallest
   install: FCC has 6 skills and no independent reviewer; Codex is already
   installed+authed on the laptop. One marketplace add gives FCC read-only
   + adversarial Codex reviews, directly serving our independent-review
   rule and R3-L3 scoring discipline. Gate stays off until measured.

2. **anthropics/skills: webapp-testing + skill-creator, single-folder
   installs** (candidate 1). Official, Apache-2.0, zero overlap with what
   we have. webapp-testing cuts vision-token burn on web fixture checks
   (computer-use-wayland + frontend-kit); skill-creator gives the scout
   team an eval harness so future adoptions are measured, not vibes.

3. **Caveman skill-only for FCC + VM, and last30days update + Codex
   install** (candidates 3 + 4, paired as "close the known gaps").
   The laptop already proves caveman skills work; FCC/VM lack them.
   last30days is already our research standard - VM is one version
   behind (4.5.0 vs 4.6.0) and Codex lacks it entirely. Both are
   low-risk, reversible, and token/research-positive. Superpowers
   (candidate 2) is the close runner-up but needs a one-harness A/B
   first because of overlap with ponytail + existing tdd/review skills.

## Method and limits

- VM checks: directory listings of ~/workspace/custom-skills/,
  /opt/muse/skills/, ~/.local/bin (26/11). clone1/clone2/mei/mochi
  account state cannot be verified from the VM (no SSH) - marked
  UNKNOWN wherever relevant; the coordinator should ask those agents
  directly before proposing installs for them (standing rule: never
  guess an agent's capabilities).
- Laptop checks: three short read-only SSH calls via ssh-laptop.sh
  (skill dirs, codex plugin list, marketplace registry). Nothing was
  changed on the laptop. FCC last30days version and bun presence were
  not read - noted as open items, not guessed.
- Web evidence: repo pages opened for anthropics/skills, obra/superpowers,
  mvanhorn/last30days-skill, wshobson/agents, hesreallyhim/awesome-claude-code,
  NikiforovAll/opencode-marketplace; README blobs read for caveman and
  codex-plugin-cc; agentsys verified via search metadata + README excerpts.
  Star counts are as displayed at crawl time (2026-11-25/26) and measure
  popularity, not quality. No skill scripts were executed.
- Security note: skills can bundle executable scripts. Every proposed
  install above still requires reading the SKILL.md + scripts/ before
  first use, per Anthropic's own guidance. One fetched page in this
  scout was flagged by the runtime safety check; its instructions were
  not followed and its facts were cross-checked independently.
