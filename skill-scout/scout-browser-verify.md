# Skill Scout: Browser Automation + Verification Tools

Scout date: 2026-11-26 (Asia/Ho_Chi_Minh). Worker: skill-scout subagent (browser/verify lane).
Scope: browser-agent frameworks, Wayland/accessibility helpers for computer-use-wayland, and independent verification/scoring tools.
Method: VM `which`/pip/npm checks + one read-only SSH check on the laptop; every repo page below was opened and read (license, install, limits recorded from the page itself, not from memory).

Already equipped (not re-scouted): Ponytail, Graphify. Rejected already: Scrapling for Zen (Patchright is Chromium-only, Zen is Firefox-based). Already in repo: cli-anything-zen, CDP/BiDi driving, manifest-gate.py + audit-scan.py + snapshot.py in rung3-ci/.

VM state at scout time: none of the candidates below are installed on the VM (`which` empty for all; pip list clean; npm global empty). Already present on VM and relevant: `gitleaks`, `trufflehog`, `pre-commit`, `actionlint` in ~/.local/bin.
Laptop state (verified read-only via ssh-laptop.sh, 2026-11-26): none of the candidates installed; `cli-anything-zen`, `codex`, `computer-use` present as expected. Nothing was changed on the laptop.

---

## 1. agent-browser (vercel-labs)

- Repo URL: https://github.com/vercel-labs/agent-browser
- License: Apache-2.0 (repo page, opened 2026-11-26)
- What it does: Native Rust CLI that drives a browser one shell command at a time over CDP. `snapshot` returns the page as compact accessibility-tree text with short refs (`@e1`); the agent clicks/fills by ref, re-snapshots, repeats. Ships version-matched agent skills (`agent-browser skills get core`), an MCP server mode, and session persistence. 53,966 stars, 124 releases, created 2026-01-11, actively maintained.
- Fits: Codex (R3-L3 runner), FCC, Muse parent/subagent workers. This is the closest match to the team priority ladder (CLI first, then code-exec, vision last) and to the token-efficiency goal: one observation yields many cheap shell actions instead of screenshot loops. Skills bound to the binary version means instructions never drift from the installed CLI. Also fits clone1/clone2/mei/mochi for web research tasks (no laptop needed, runs anywhere).
- Install/check status: VM checked, NOT installed. Laptop verified, NOT installed. Install: `npm install -g agent-browser` then `agent-browser install` (downloads Chrome for Testing); or `npx agent-browser open example.com` with no install.
- Evidence: Opened repo page and README 2026-11-26. README states CDP control via background daemon, Chrome for Testing default, `--cdp`/`--auto-connect` attach mode, Lightpanda/Obscura engines, cloud providers (Browserbase, Browserless, Browser Use, Kernel, AgentCore), and a "Firefox engine guide" link. Clicks fail loudly when the target is hidden/disabled/covered (good anti-fabrication property: no silent fake success).
- Hard limitation: Default engine is Chrome/Chromium via CDP. Zen is Firefox-based; the Firefox engine path exists in docs but is unverified by us, and third-party reviews note weak results against Cloudflare-protected sites (relevant: chatgpt.com on Zen already hits Cloudflare). Security controls (allowlist, action policy) are opt-in, off by default.
- Next step: INSTALL TEST on VM first (npx, no global install): drive a held-out page, measure tokens/actions vs current BiDi path. Do not touch Zen/launcher until the Firefox-engine question is answered in a sandbox.

## 2. Stagehand (browserbase)

- Repo URL: https://github.com/browserbase/stagehand
- License: MIT (README badge + search result, opened 2026-11-26)
- What it does: SDK for browser agents in TypeScript, Python, and Go. Three natural-language primitives on top of Playwright-style APIs: `act` (self-healing actions), `observe` (returns real selectors so credentials never reach the model), `extract` (schema-validated data via zod/pydantic). Runs locally or on Browserbase cloud; also ships a `browse` CLI + skill for coding agents and a hosted MCP server. 26.1k stars, latest release 4.3.0 (Oct 2026).
- Fits: Codex and FCC (the `browse` CLI path needs no LLM key or Browserbase account for local use, per README), Muse workers doing structured extraction. The `observe` pattern (model finds the selector, code types the secret) is a clean fit for the team rule of never sending credentials through the model.
- Install/check status: VM checked, NOT installed. Laptop verified, NOT installed. Install: `pnpm add @browserbasehq/stagehand` / `pip install stagehand` / `go get .../sdk-go/v4`; CLI: `npm install -g browse`.
- Evidence: Opened full README (raw.githubusercontent.com/browserbase/stagehand/main/README.md) 2026-11-26. README: "Local runs need Chrome installed." SDK path needs an LLM provider API key; Browserbase cloud path needs a Browserbase API key. Hybrid accessibility-tree trimming claimed for token efficiency.
- Hard limitation: Chrome/Chromium-centric (CDP engine, "optimized, low level interface to the browser"). Same Zen/Firefox question as agent-browser, with no Firefox path visible in the README. Cloud features (Model Gateway, caching, proxies) are paid Browserbase.
- Next step: PROPOSE as second browser candidate. Test the `browse` CLI locally on the VM against agent-browser on the same held-out tasks; pick one, do not equip both (Ponytail: smallest complete change).

## 3. browser-use

- Repo URL: https://github.com/browser-use/browser-use
- License: MIT (repo page, opened 2026-11-26)
- What it does: Python library where the model writes Python against raw CDP in a persistent REPL ("The model, a REPL and CDP. That's the whole agent."). Three paths: fully hosted cloud, CLI (`browser-use skill install`), Python library. Built-in post-run Judge that grades the run from the trace and screenshots. 122,063 stars, 11,075 commits, 157 releases, created 2024-10-31.
- Fits: Muse workers and clone1/clone2 for autonomous web tasks where a full agent loop (not just driving) is wanted. The Judge feature is interesting for verification, but note it uses the same model that ran the task, so it is NOT an independent scorer (see promptfoo/Inspect below for independence).
- Install/check status: VM checked, NOT installed. Laptop verified, NOT installed. Install: `uv tool install browser-use==1.0.8` or `pip install 'browser-use==1.0.8'`. README insists on exact pinning (`==`, never `>=`): "releases move fast and can break APIs."
- Evidence: Opened repo page 2026-11-26. Local mode drives Chrome/Chromium/Edge via CDP (`Browser('chromium')`, `Browser('chrome')`); default mode is Browser Use Cloud ($0.06/browser-hour, needs API key/login). Telemetry on by default (can disable). "Ultrafast" mode acts on accessibility-tree ids.
- Hard limitation: Chromium/CDP only in local mode; no Firefox/Zen path seen. Heavy dependency surface (Pydantic AI stack), fast-moving API with breaking releases, cloud upsell throughout. Overlaps heavily with agent-browser/Stagehand for our driving use case.
- Next step: REJECT for now as a driving tool (agent-browser covers the CLI-driving need with a smaller surface). Keep on the list only if a task needs a self-contained autonomous web agent loop; re-scout then. Note: task brief said browser-use "may already be known" — it is not installed anywhere we checked, so treat as unevaluated, not equipped.

## 4. Steel Browser (steel-dev)

- Repo URL: https://github.com/steel-dev/steel-browser
- License: Apache-2.0 (search result + review, 2026-11-26)
- What it does: Self-hostable browser sandbox/API. Runs Chrome behind a REST API + CDP WebSocket with session management, stealth/fingerprinting, text-to-markdown, and a debug UI. Connect with Puppeteer, Playwright, or Selenium. One-command Docker deploy: `docker run -p 3000:3000 -p 9223:9223 ghcr.io/steel-dev/steel-browser`.
- Fits: Muse parent/workers if the team ever needs parallel isolated browser sessions off the laptop (e.g. clone1/clone2 web research at scale, or a clean-room browser for held-out tests). Not a fit for driving Zen on the laptop.
- Install/check status: VM checked, NOT installed. Laptop verified, NOT installed. Install: Docker image from GHCR, or Steel Cloud account.
- Evidence: Search results 2026-11-26 (repo page summary, devtoolwatch review, dev.to comparison). Latest release v0.5.4-beta (Aug 2026), repo updated Oct 2026. "Steel is in public beta and evolving every day."
- Hard limitation: Chrome/Chromium only (Puppeteer/CDP). Ports 3000/9223 have NO authentication — README warns never to expose them; on a shared VM this needs a firewall/loopback plan before any test. Beta status.
- Next step: PARK. Only propose if a concrete parallel-session need appears; then install test in Docker on the VM bound to loopback only.

## 5. Anchor Browser (anchorbrowser)

- Repo URL: https://github.com/anchorbrowser/AnchorBrowser-SDK-Typescript (SDKs; platform is hosted)
- License: SDKs Apache-2.0; platform itself is a paid hosted service (review, 2026-11-26)
- What it does: Cloud fleet of humanized Chromium sessions for computer-use agents: REST API, CDP WebSocket, TS/Python SDKs, hosted MCP servers, CAPTCHA solving, proxy rotation, cached deterministic action replay ("Web Action Cache").
- Fits: Nobody on the current roster. Our computer-use work must drive the user's real Zen on the user's laptop (logged-in sessions, visible pill, Wayland). A cloud Chromium fleet cannot do that, and sending tasks/credentials to a third-party fleet conflicts with the team's local-first setup.
- Install/check status: VM checked, NOT installed. Laptop verified, NOT installed. Install: `npm i anchorbrowser` / `pip install anchorbrowser` + API key; pricing ~$0.05/browser-hour + proxy fees (review).
- Evidence: Search results 2026-11-26 (anchorterminal review verified 2026-10-08; agent-native index). Review flags: no published SLA, CDP connection puts the API key in the URL, "keyless onboarding" answered disabled.
- Hard limitation: Cloud-only, Chromium-only, paid, credentials leave the machine. API key in CDP URL is a red flag for our security posture.
- Next step: REJECT. Revisit only if a future task explicitly needs cloud stealth browsing and the owner approves sending data out.

## 6. promptfoo

- Repo URL: https://github.com/promptfoo/promptfoo
- License: MIT (README badge, search result 2026-11-26)
- What it does: Local-first LLM evaluation and red-teaming CLI. YAML test configs with deterministic assertions (is-json, javascript, regex) stacked under LLM-as-judge rubrics (`llm-rubric`, `g-eval`, multi-judge voting). Matrix views across prompts/models, caching, CI integration (GitHub Action), JSON/CSV/HTML outputs. Runs completely locally; talks directly to the model APIs you configure.
- Fits: mochi (scorer) and mei (analysis/review) first, Muse parent second. This is the strongest candidate for catching FCC-style evidence fabrication: deterministic checks verify structure/claims that must be exact, and an independent judge model (different from the runner's model) grades the rest against a rubric. Scorers stay independent of runners because the judge provider is configured separately from whatever produced the output. Also fits clone1/clone2 for regression-testing prompts/briefs.
- Install/check status: VM checked, NOT installed. Laptop verified, NOT installed. Install: `npx promptfoo@latest init` (no global install needed) or `npm install -g promptfoo`.
- Evidence: Search results 2026-11-26 (README, LLM-as-judge guide). Guide shows the exact pattern we need: Layer 1 deterministic assertions, Layer 2 `llm-rubric` judge returning `{pass, score, reason}`, plus multi-judge voting and injection-safe judge prompts.
- Hard limitation: Node ecosystem (team is Python-heavy in rung3-ci; a Node tool in the scoring path is a new runtime to maintain). Judge quality depends on the grader model chosen; needs API keys for hosted graders or a local model. It evaluates text outputs, not live browser state — pair it with snapshot.py artifacts, not as a replacement.
- Next step: INSTALL TEST on VM (npx, zero-commit): encode 3-5 past R3-L3 scoring rubrics (including one fabricated-evidence case) as promptfoo configs, run against stored snapshots, compare verdicts with mochi's. Propose to coordinator if agreement is high.

## 7. Inspect AI (UK AISI)

- Repo URL: https://github.com/UKGovernmentBEIS/inspect_ai
- License: MIT (docs/search result 2026-11-26)
- What it does: Python framework for frontier AI evaluations from the UK AI Security Institute + Meridian Labs. Every eval is a Task = Dataset (labeled samples) + Solver (model/agent under test) + Scorer (grader). Built-in tool use, multi-turn agents, sandboxed code execution (Docker/K8s), model-graded scoring, transcript replay in Inspect View, 200+ pre-built evals (inspect_evals).
- Fits: mochi/mei for rigorous independent scoring; Muse parent for building held-out test suites (the team's anti-"hoc tu" rule: validate on held-out cases from an independent agent). The Task/Solver/Scorer split enforces scorer independence structurally, not by convention. Python-native, matches rung3-ci.
- Install/check status: VM checked, NOT installed. Laptop verified, NOT installed. Install: `pip install inspect-ai`.
- Evidence: Search results 2026-11-26 (inspect.aisi.org.uk docs, PyPI). Docs confirm Task/Solver/Scorer APIs, 20+ model providers, sandboxing toolkit, VS Code extension.
- Hard limitation: Heavier framework than promptfoo (more concepts, more setup); designed for benchmark-style evals, so encoding ad-hoc R3-L3 snapshot scoring takes more upfront work. Overkill if promptfoo covers the need.
- Next step: PROPOSE as the long-term scoring harness if promptfoo's test shows rubric scoring works but we outgrow YAML configs. Do not install both at once (Ponytail).

## 8. Semgrep (Community Edition)

- Repo URL: https://github.com/semgrep/semgrep
- License: Engine LGPL-2.1; registry rules under Semgrep Rules License v1.0 (internal use OK, no repackaging into competing products); cross-file Pro engine is commercial (search results 2026-11-26)
- What it does: Fast static analysis with rules written as code-shaped patterns (YAML). 30+ languages, runs as CLI/CI/editor, custom rules in minutes. CE analyzes within single files/functions; paid tiers add cross-file taint analysis and proprietary rule packs.
- Fits: Muse workers + mei (review) + rung3-ci gates. Deterministic, no LLM in the loop: ideal for hard rules the team already has, e.g. ban ydotool usage, ban raw CDP writes without the pill path, flag PII patterns before commit (complements gitleaks/trufflehog already on the VM), enforce Ponytail-style constraints (no new deps without approval). Catches mechanical violations that LLM reviewers miss or rationalize.
- Install/check status: VM checked, NOT installed. Laptop verified, NOT installed. Install: `pip install semgrep` or Docker `semgrep/semgrep`.
- Evidence: Search results 2026-11-26 (repo page: LGPL-2.1; comparison vs CodeQL: CE found 2/3 planted injections with community rules, a 12-line custom rule caught the third in 1.7s; latest 1.186, Nov 2026, actively maintained).
- Hard limitation: CE is single-file analysis (cross-file dataflow is paid). Rules license restricts redistribution of the official rule packs (our own rules are ours). Not a substitute for CodeQL's deep queries on public repos, but CodeQL's CLI is free only for open-source/research use and needs paid GitHub Code Security for private code, so Semgrep CE is the better fit for private team repos.
- Next step: INSTALL TEST on VM: `pip install semgrep`, write 3 starter rules (ydotool ban, PII pattern, banned-import), run against computer-use-wayland, measure false positives. Propose for rung3-ci if clean.

## 9. reviewdog

- Repo URL: https://github.com/reviewdog/reviewdog
- License: MIT (repo page, search result 2026-11-26)
- What it does: Takes any linter/analyzer output (errorformat, checkstyle, RDFormat, SARIF) and posts findings as PR review comments or checks, filtered to the diff. Local mode filters lint output by diff without posting. Single Go binary, GitHub Action available.
- Fits: Muse parent (landing path) + mei (review). Turns Semgrep/ruff/etc. output into visible PR annotations so silent issues stop being silent (matches the team's "no silent work" reporting rule). Low effort, high visibility.
- Install/check status: VM checked, NOT installed. Laptop verified, NOT installed. Install: install.sh one-liner, `go install github.com/reviewdog/reviewdog/cmd/reviewdog@latest`, or the `reviewdog/action-setup` GitHub Action.
- Evidence: Search results 2026-11-26 (repo page: MIT, 47 releases, created 2016, SARIF 2.1.0 support, reporters for GitHub PR check/review, GitLab).
- Hard limitation: It is a reporting layer, not an analyzer: value depends on having good analyzers feeding it (Semgrep, ruff, shellcheck). Posting to GitHub needs a token with PR permissions; keep tokens in the existing gh setup, never in repo files.
- Next step: PROPOSE after Semgrep test. If Semgrep lands in CI, add reviewdog in the same change (smallest complete change: analyzer + reporter together).

## 10. dogtail + AT-SPI (Wayland accessibility-tree automation)

- Repo URL: https://gitlab.com/dogtail/dogtail (PyPI: dogtail)
- License: GPL (dogtail COPYING; AT-SPI stack is LGPL/GPL GNOME project) — verify exact terms before any redistribution; internal use only is fine
- What it does: Python GUI automation over the AT-SPI accessibility tree (the same tree screen readers use). Walk any GTK/Qt/Electron app's UI tree by role+name, act on elements without screenshots. On Wayland, input injection goes through gnome-ponytail-daemon (Remote Desktop + Screen Cast portals). Accerciser inspects the live tree.
- Fits: computer-use-wayland repo research lane (Muse workers). Relevant because the team's priority ladder wants accessibility-tree grounding before vision+mouse, and AT-SPI is the only OS-native tree for non-browser Linux apps (Zen internals, file dialogs, native apps). Read-only tree walking could ground actions in native dialogs that BiDi cannot see.
- Install/check status: VM checked, NOT installed (no dogtail, no accerciser). Laptop verified, NOT installed. Install: `pip install dogtail` + distro AT-SPI stack; Wayland input needs gnome-ponytail-daemon (C code, distro package or source build).
- Evidence: Search results 2026-11-26 (PyPI dogtail 1.0.8/2.0.dev, Fedora Magazine "Automation through Accessibility"). Dogtail 1.0 is explicitly Wayland-enabled via gnome-ponytail-daemon, which uses `org.gnome.Shell.Introspect` for the window list.
- Hard limitation: gnome-ponytail-daemon is GNOME Shell-specific (Introspect API). The laptop runs Hyprland, not GNOME Shell, so the input bridge likely does not work there as-is; the AT-SPI tree itself (read side) should still work for GTK/Qt apps with accessibility enabled. Firefox/Zen expose AT-SPI too, but the team already has BiDi for Zen. This is a research spike, not a drop-in.
- Next step: RESEARCH ONLY. Propose a timeboxed spike: check whether AT-SPI tree walking works read-only under Hyprland for one native app (e.g. file picker) before any install decision. Do not install on the laptop during the paused R3-L3 run.

---

## Ranked shortlist (top 3)

1. **agent-browser** — biggest speed/token win for every runner (Codex, FCC, Muse workers). CLI-first matches the team ladder, version-matched skills prevent instruction drift, loud click failures fight fabrication. Test on VM via npx; answer the Zen/Firefox-engine question in a sandbox before any laptop use.
2. **promptfoo** — fastest path to independent, reproducible scoring for mochi/mei. Deterministic assertions + independent judge model directly target the FCC fabrication failure mode. Zero-install test (npx) against stored snapshots and past rubrics.
3. **Semgrep CE** — deterministic gates with no LLM in the loop (ydotool ban, PII, banned patterns), complements gitleaks/trufflehog already on the VM, and pairs with reviewdog for visible PR reporting. Python-installable, fits rung3-ci.

Close fourth: Inspect AI (adopt if scoring outgrows promptfoo). Parked: Steel (needs a parallel-session use case). Rejected: Anchor (cloud-only, paid, key-in-URL), browser-use as a driver (heavier duplicate of agent-browser; keep only for autonomous-loop tasks). Research spike only: dogtail/AT-SPI (Hyprland input bridge uncertain).

No installs were performed. No repo was touched. No personal information is included in this file.
