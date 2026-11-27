# R3-L3 Re-plan Council 3: Ponytail Rollout, Graphify Rollout, and Remaining-Run Operations

Date: 2026-11-26. Council: COUNCIL-3 (operations). Run status: PAUSED by owner order. This document is a verdict and an execution plan only. It installs nothing, commits nothing, edits no coordinator state, resumes no run, and messages no owner. Every install step below runs only after the owner approval gate in section 3.3. English only. No em dashes or en dashes anywhere in this file.

Sources read for this verdict: ponytail skill at ~/workspace/custom-skills/ponytail/SKILL.md, ponytail repo at ~/workspace/ponytail-repo (README.md, INSTALL.md, AGENTS.md, plugin manifests, hooks, opencode plugin, docs/agent-portability.md), skill scout registry at ~/workspace/skill-scout/REGISTRY.md, run order at rung3-run-log/thu-tu-chay.txt, backups at rung3-run-log/du-phong.txt, coupled-task rules at rung3-run-log/r3-l3-coupled-tasks.md, R3-089 refresh rules at rung3-run-log/r3-l3-r3-089-refresh.md, R3-100 port rule at rung3-run-log/r3-l3-r3-100-port-rule.md, task 56 brief at improvements/r3-l3-task56-restore-tabs-20261126.md, Cloudflare research at improvements/zen-cloudflare-chatgpt-fix-research-20261125.md, coordinator state at rung3-run-log/r3-l3-coordinator-state.json (read only). Laptop state was verified read only over SSH on 2026-11-26 between 04:41 and 04:52 (Asia/Ho_Chi_Minh) with short commands. SSH sessions die at about 30 seconds, so each check was a separate short call. No laptop file was changed.

## Verdict summary

1. Ponytail is ready to roll out, but the laptop is in three different states and one blind install command would be wrong. Opencode already has ponytail. Codex has only a bare skill file, no plugin. FCC has neither. The plan below installs only what is missing, verifies each CLI live, and records every step in the skill scout registry.
2. Graphify is installed and proven on the VM and absent on the laptop. The plan below installs it on the laptop, rebuilds the graph from the laptop checkout, and verifies it with a known-node query before any laptop agent is told to use it.
3. The remaining run is operable from the pause point, but two clocks are running. The invalid budget may reach 4 of 5 when R3-026 is graded, and the R3-089 fixture expires on 2026-12-01 at 08:59. Both have exact handling below. Neither blocks the re-plan. Both have owner-notification points.
4. Nothing resumes until three gates pass in order: the Cloudflare fix is proven live, ponytail and graphify are installed and verified per CLI, and the owner approves the re-plan. The sequencing in section 3.3 is the single path from pause to closure.

## 1. Ponytail: what it enforces

Ponytail (github.com/DietrichGebert/ponytail, MIT, version 5.3.3 in the local clone) is one prompt shipped through many host adapters. The canonical prompt is skills/ponytail/SKILL.md. The compact always-on form for hosts that only read a rules file is AGENTS.md. Everything else in the repo loads that prompt into a specific agent. Six skills ship: ponytail, ponytail-review, ponytail-audit, ponytail-debt, ponytail-gain, ponytail-help.

What the prompt enforces, in order:

1. Before writing: read the task and the code it touches. List every place the change must reach (callers, tests, fixtures, config, exports). Check what the change could break for users (data destroyed or exposed, callers that stop working). That list is the scope. Extra features are not scope.
2. The smallest complete change, first option that fully works: (a) does it need to exist at all, skip unrequested features and name them in one line; (b) already in this codebase, reuse the helper, component, service, or pattern the way surrounding code does; (c) standard library or platform feature, unless the project has its own; (d) an installed dependency, never a new dependency for a few lines; (e) one line a reader gets at a glance; (f) otherwise the minimum code that works.
3. Hard bans: no unrequested abstraction, wrapper, type conversion, option, config, boilerplate, or for-later code. Keep values in the form the platform already gives. Deletion beats addition. Keep the structure the codebase already has.
4. Bug fixes: grep every caller of the function touched, then fix the root cause once in the shared code. Moved or merged code keeps its error handling and validation.
5. Checks: new non-trivial logic (a branch, a loop, a parser, money or security, or a whole new script or app) leaves one small test or an assert-based self-check. Trivial changes need none. A deliberate shortcut gets a code comment in the form: shortcut, the limit, when to upgrade. The ponytail-debt skill harvests those comments into a ledger.
6. Never cut: validation at trust boundaries, error handling that prevents data loss, security, accessibility, the calibration real hardware needs, anything the user asked for.
7. Reply discipline: end with one or two lines naming what was skipped or not checked and any risk the user must know.
8. Levels: lite (build what was asked, name the smaller option in one line), full (the rules above, default), ultra (also question the request before building). Level switches with the ponytail command. The ruleset stays active for the whole session until the user says stop ponytail or normal mode.

How each integration works:

- Claude Code and Codex (full plugin tier): a plugin manifest (.claude-plugin/plugin.json, .codex-plugin/plugin.json) points at skills/ and at hooks/claude-codex-hooks.json. Three Node lifecycle hooks run: SessionStart (ponytail-activate.js, loads the ruleset at the active level), SubagentStart (ponytail-subagent.js, injects the ruleset into every subagent), UserPromptSubmit (ponytail-mode-tracker.js, tracks level switches). Node must be on the non-interactive PATH or every hook call prints a harmless node not found error while the skills still work. Claude Code also gets a band UI (needs Claude Code 2.1.290 or later, terminal or desktop app only, never in print mode). Codex invokes plugin skills with the dollar namespace, for example $ponytail:ponytail-review. Default level can be set with the PONYTAIL_DEFAULT_MODE environment variable or a defaultMode field in ~/.config/ponytail/config.json. Subagent injection can be scoped with PONYTAIL_SUBAGENT_MATCHER.
- OpenCode (server plugin tier): .opencode/plugins/ponytail.mjs injects the ruleset into every chat system prompt at the active level, persists level switches to ~/.config/opencode/.ponytail-active, and registers the ponytail commands and skills. Install is either the npm package @dietrichgebert/ponytail through the plugins array in opencode.json, or a checkout directory path. The plugins entry must name a directory, not a file. OpenCode also auto-loads AGENTS.md, so the rules hold at instruction tier even without the plugin, but levels need the plugin.
- Instruction tier (all other hosts): copy AGENTS.md into the project, or copy the matching rules file (.cursor/rules, .windsurf/rules, .clinerules, .github/copilot-instructions.md, .kiro/steering, .qoder/rules). Rules hold, commands and levels do not.
- Muse (this VM): the skill is installed at ~/workspace/custom-skills/ponytail/SKILL.md with AGENTS-ponytail.md beside it. Muse subagents inherit parent skills. Briefs reference the skill path and restate the rule text in section 1.6.

## 1.1 Read-only verification of current laptop state (2026-11-26, SSH, no changes)

All commands below ran over ~/workspace/ssh-laptop.sh as the owner on the Omarchy laptop. Long SSH sessions die at about 30 seconds with a broken pipe error, so verification used short calls only. Findings:

Codex:
- codex-cli 0.172.0 at /home/james/.local/share/mise/shims/codex. The plugin command tree exists: codex plugin add, list, marketplace, remove. Marketplace syntax verified live: codex plugin marketplace add takes a local path, owner/repo, HTTPS Git URL, or SSH Git URL. Plugin add syntax verified live: PLUGIN@MARKETPLACE or PLUGIN with --marketplace.
- codex plugin marketplace list shows only openai-bundled and openai-curated. Ponytail is NOT installed as a Codex plugin. No ponytail entry in ~/.codex/config.toml, no ponytail hook in ~/.codex/hooks.json.
- One nuance the registry summary missed: ~/.codex/skills/ponytail/SKILL.md exists (3492 bytes, dated Oct 10). It is the ponytail skill text at instruction tier. It gives Codex the rules when the skill is invoked, but it has no lifecycle hooks, no automatic activation, no level persistence, and no subagent injection. Council ruling: treat Codex as NOT INSTALLED for plugin purposes. The bare skill file stays as a fallback and is not deleted. The plugin install in section 1.2 adds activation, levels, and the other five skills on top of it.
- Node v26.13.1 is on PATH, so the plugin hooks will run.

Opencode:
- opencode v2.4.1 at /home/james/.local/share/mise/shims/opencode. Global config at ~/.config/opencode/opencode.json. The plugin command tree exists: opencode plugin list, add, check, update, remove.
- Ponytail IS already installed, in a local dual v1/v2 form. Evidence: ~/.config/opencode/plugins/ponytail/index.js (5979 bytes) plus package.json (name ponytail-opencode-plugin, version 0.1.0, description ponytail dual v1/v2 plugin). The file header states why it exists: the published npm plugin is v1 only and v2 refuses to load it, so this local file serves both majors, persists the mode, and injects the ruleset. Skills are symlinked: ~/.config/opencode/skills/ponytail points at ~/.cache/opencode/packages/@dietrichgebert/ponytail@latest/node_modules/@dietrichgebert/ponytail/skills/ponytail, and all six ponytail skills are present. Commands are present in ~/.config/opencode/command/ (ponytail.md, ponytail-review.md, ponytail-audit.md, ponytail-debt.md, ponytail-gain.md, ponytail-help.md). The mode file ~/.config/opencode/.ponytail-active exists and contains: full.
- Two facts to record honestly. First, opencode plugin list shows only herdr-opencode, not ponytail, and opencode.json has no plugins key. That means ponytail loads by directory auto-discovery from ~/.config/opencode/plugins/, not by a registered package entry. Directory load is a supported OpenCode path, but the list output will not prove it. Verification for opencode must therefore be file based plus a live model run, not list based. Second, opencode cannot run a model for this run today. The models list shows groq and nvidia routes. The owner rule (26/11) is opencode provider models only, never NVIDIA, Groq, or OpenRouter. The previous nvidia/deepseek-ai/deepseek-v4.1-flash model hit end of life on 2026-11-16. The owner has not yet picked a replacement free model. Council ruling: opencode gets NO reinstall. It gets activation verification only, and the live model proof waits until the owner picks a model. Opencode runs no R3-L3 task in the remaining run.

FCC (fcc-claude):
- fcc-claude 2.1.332 (Claude Code) at /home/james/.local/bin/fcc-claude, a uv tool launcher for free-claude-code. It is a full Claude Code build: fcc-claude plugin exists with marketplace add, list, remove, update, plus plugin install, list, enable, disable, details. The plugin list today shows only four built-in plugins, all enabled. No ponytail marketplace is configured: ~/.claude/plugins/known_marketplaces.json lists only claude-plugins-official.
- FCC loads skills from ~/.claude/skills/. Current skills: computer-use, diagnose-crash, last30days, omacal, omarchy, omarchy-app. No ponytail skill. FCC server state lives in ~/.fcc/ (database, logs, locks) and is not a skills location. The run drives FCC through the tmux session r3-fcc-runner-L3 (pane PID 22399 at last check). Council ruling: FCC is NOT INSTALLED. Install through the Claude Code plugin route in section 1.2 while the run is paused, then refresh the tmux session and verify before any FCC task is released.
- Band note: fcc-claude 2.1.332 meets the 2.1.290 minimum for the ponytail band, but the band never shows in print mode and the run does not need it. Band presence is not a verification criterion for the run.

VM and remote accounts:
- Muse VM: ponytail skill installed and verified on disk at ~/workspace/custom-skills/ponytail/SKILL.md. Subagent workers inherit it.
- clone1, clone2, mei, mochi: separate Muse accounts with no SSH to the laptop. Registry status is UNKNOWN for all four. The rule reaches them only through briefs. No per-account install can be done from the VM. Do not assume their install state. Ask each account directly in its own chat when a code task is assigned, and state the delivery path in the brief.
- agy: quota exhausted until about 28/11. Out of scope for this rollout. Check after quota returns.

Who runs where, for the record: Codex and FCC run on the laptop. Muse subagents run on the VM and drive the laptop over SSH. Opencode runs on the laptop but is unusable for the run until the owner picks a model. Mei and mochi score and analyze from their own accounts. Clone1 and clone2 do repo and web work only.

## 1.2 Exact installation steps per CLI (post-approval only)

General rules for every install below: check before installing (owner rule, 26/11 04:40), one CLI at a time, timed and logged with wall-clock Asia/Ho_Chi_Minh plus elapsed time, registry entry updated the same day, no install while a drive is in flight. All laptop commands run over ~/workspace/ssh-laptop.sh. Any step that may exceed 25 seconds runs detached with nohup and a log file, then a short follow-up call reads the log. Never hold an SSH session open waiting for a CLI to finish.

### Codex (laptop): install the plugin

Pre-check (already done 26/11, repeat at install time): codex --version, codex plugin marketplace list, codex plugin list. Confirm ponytail is absent before installing. Confirm node --version prints a version.

Install, exact commands on the laptop:

    codex plugin marketplace add DietrichGebert/ponytail
    codex plugin add ponytail@ponytail

Syntax verified against the repo INSTALL.md, the README, and live --help output on the laptop (codex-cli 0.172.0). The marketplace source form owner/repo is accepted. The plugin selector form PLUGIN@MARKETPLACE is accepted.

Then, in an interactive codex session on the laptop: open /hooks, review and trust the two ponytail lifecycle hooks (SessionStart activation and UserPromptSubmit mode tracking, plus SubagentStart injection), and start a new thread. The run drives Codex with codex exec per task, so after trusting the hooks, confirm one codex exec invocation picks the plugin up (see verification in section 1.3). The bare skill file at ~/.codex/skills/ponytail/SKILL.md is left in place. If the plugin install shadows it, that is expected and harmless. Do not delete it during the run.

Set the default level to full explicitly so a fresh thread never starts at an unknown level:

    mkdir -p ~/.config/ponytail
    printf '{"defaultMode":"full"}\n' > ~/.config/ponytail/config.json

Only write that file if it does not already exist. If it exists, read it first and merge, never overwrite blindly.

### Opencode (laptop): activate and verify only, do NOT reinstall

No install command runs for opencode. The plugin, skills, commands, and mode file are already present (evidence in section 1.1). The steps are:

1. Read back the state: cat ~/.config/opencode/.ponytail-active (expect: full), ls ~/.config/opencode/skills/ (expect all six ponytail skills), ls ~/.config/opencode/command/ (expect all six ponytail commands), head ~/.config/opencode/plugins/ponytail/index.js (expect the dual v1/v2 header).
2. Confirm the mode is full. If the file is missing or holds another value, write full to it. That is the only write allowed for opencode in this rollout.
3. Record in the registry that opencode ponytail is directory-loaded, so opencode plugin list is not evidence either way. Live model verification is deferred until the owner picks an opencode provider model (section 1.3). Until then, opencode is not assigned code work that depends on ponytail being proven.

### FCC (fcc-claude, laptop): install the plugin

Pre-check (already done 26/11, repeat at install time): fcc-claude --version (expect 2.1.332 or later), fcc-claude plugin list, ls ~/.claude/skills/. Confirm ponytail is absent.

Install, exact commands on the laptop, run while the run is paused and no FCC drive is in flight:

    fcc-claude plugin marketplace add DietrichGebert/ponytail
    fcc-claude plugin install ponytail@ponytail

Syntax verified against live --help output: fcc-claude plugin marketplace add takes a URL, path, or GitHub repo; fcc-claude plugin install takes plugin@marketplace. If the marketplace add asks to accept a declared command, stop and record the exact prompt. Do not pass --accept-command blindly. The coordinator reviews the sha256 the tool reports, confirms it matches the ponytail marketplace catalog, and only then re-runs with the accept flag.

Fallback if the plugin route fails twice: use the skills route. Copy the six skill folders from the VM clone (~/workspace/ponytail-repo/skills/) into ~/.claude/skills/ on the laptop, or load one session with --plugin-dir pointing at a laptop checkout of the repo. The skills route gives the rules and commands without lifecycle hooks, so activation is per session and levels do not persist. Record which route was used in the registry. Try the plugin route first, because the run needs always-on activation, not per-session opt-in.

After install: restart or refresh the tmux session r3-fcc-runner-L3 so the new plugin loads, confirm the session answers a test prompt, and only then release FCC tasks. Never install into a live driving session.

### Muse subagents (VM): already installed, brief discipline only

Skill path: ~/workspace/custom-skills/ponytail/SKILL.md. Repo: ~/workspace/ponytail-repo. No install step. Every brief that involves writing or reviewing code must (a) name the skill path, (b) restate the rule text in section 1.6 verbatim, and (c) state the delivery path explicitly. Workers read the skill file at task start. The coordinator does not assume a worker loaded it.

### clone1, clone2, mei, mochi: briefs only, ask directly

No install is possible from the VM. Each code brief to these accounts restates the rule text in section 1.6 verbatim and asks the account to confirm whether the ponytail skill is available in its environment before starting. Record the answer in the registry under that staff member. Never guess. If the account cannot load the skill, the brief text itself is the ruleset for that task, and the reviewer checks the diff against it.

## 1.3 Live verification per CLI (post-install, timed and logged)

A claim of installed without a live proof is worth nothing. Each CLI gets two proofs: a state proof (config readback) and a behavior proof (a trivial code task whose output shows ponytail behavior). Log wall-clock start, elapsed time, command, and output hash for each proof. File the log with the registry entry.

Codex:
- State proof: codex plugin marketplace list shows the ponytail marketplace. codex plugin list shows ponytail@ponytail installed and enabled at version 5.3.3 (or the installed version, recorded exactly). /hooks in a fresh thread shows the ponytail hooks trusted.
- Behavior proof: run one codex exec task in a scratch directory: ask for a date picker added to a tiny page that already has an Input component. Pass: the result reuses the existing Input with a native date type in a handful of lines, adds no dependency, and the reply ends with what was skipped and any risk. Fail: a new date library, a hand-built calendar, or no closing skipped-and-risk lines. Also invoke $ponytail:ponytail-review on the scratch diff and confirm it answers in the ponytail review format (what the code does, what goes wrong, how to fix it, what happens if skipped).

Opencode:
- State proof (available now): mode file reads full, six skills and six commands present, plugin file header matches the dual v1/v2 form. Record the file hashes.
- Behavior proof (deferred): blocked until the owner picks an opencode provider model. When a model exists, run the same date picker scratch task through opencode and apply the same pass and fail lines as Codex, plus /ponytail lite, /ponytail full, /ponytail ultra, /ponytail off level switches each changing the next reply. Until that proof exists, the registry keeps opencode at INSTALLED with usage UNVERIFIED, and no run task depends on it.

FCC:
- State proof: fcc-claude plugin list shows ponytail enabled. fcc-claude plugin details ponytail shows the skills and hooks inventory. A fresh fcc-claude session reports ponytail mode active at full.
- Behavior proof: in the refreshed r3-fcc-runner-L3 session, run the same date picker scratch task. Pass and fail lines as Codex. Then run /ponytail-review on the scratch diff. Given the FCC fabrication history in this run (R3-001, R3-002), the behavior proof is graded from files on disk by the coordinator, never from the FCC completion report alone. The scratch files must exist, hash-match the report, and show the reuse. A report without files is a fail.

Muse VM:
- State proof: skill file present at ~/workspace/custom-skills/ponytail/SKILL.md, repo present at ~/workspace/ponytail-repo, registry entry current.
- Behavior proof: the next code brief after approval includes the rule text, and the worker diff is reviewed against it (reuse before writing, no new dependency for a few lines, one small test for non-trivial logic). The review note names the rung that held.

## 1.4 Revert path per CLI

Codex: codex plugin remove ponytail, then codex plugin marketplace remove ponytail. Verify with codex plugin list (ponytail absent) and a fresh thread (no ponytail activation line). The bare skill file at ~/.codex/skills/ponytail/SKILL.md is untouched by the plugin remove and stays as instruction tier. If ~/.config/ponytail/config.json was created by this rollout, remove it only if nothing else uses it. Record the revert in the registry.

Opencode: nothing was installed, so revert is mode only. Write off to ~/.config/opencode/.ponytail-active, or remove the file to fall back to the default. Do not delete the plugin directory, skills, or commands as part of a revert. They predate this rollout. If the owner later orders a full removal, that is a separate task: opencode plugin remove @dietrichgebert/ponytail for a package install, plus manual removal of the local plugin directory and symlinks, verified by a fresh opencode start with no ponytail injection.

FCC: fcc-claude plugin disable ponytail for a soft revert, or fcc-claude plugin uninstall ponytail (interactive form: /plugin remove ponytail) for a hard revert, then fcc-claude plugin marketplace remove ponytail. Verify with fcc-claude plugin list and a fresh session. If the skills fallback route was used instead, remove the six copied folders from ~/.claude/skills/. Run node scripts/uninstall.js from a ponytail checkout before the host remove command if leftover state must be cleaned (mode flag, statusline copy, settings entry). That script is itself a plugin file, so run it first or from a separate clone.

Muse VM: remove or rename ~/workspace/custom-skills/ponytail/ only on owner order. Briefs stop restating the rule at the same time. Record in the registry.

General: every revert is timed, logged, and registry-recorded with the same discipline as the install. A revert during the run needs coordinator approval and never happens mid-drive.

## 1.5 Registry discipline (skill scout team)

The skill scout coordinator owns equipping. This plan goes through the registry at ~/workspace/skill-scout/REGISTRY.md. Format already in use: per tool, repo URL, license, what it does, fits, verification, install status per staff (INSTALLED, PROPOSED, NOT FIT, REJECTED, UNKNOWN). Council additions for each laptop install in this plan: exact version installed, install date and time, state proof output, behavior proof result, revert command, and log path. The coordinator (run coordinator for run tasks, skill scout coordinator for equipping) updates the entry the same day the install lands. No install is done until its registry entry says INSTALLED with a verification result. PROPOSED entries stay proposed while the run is paused.

## 1.6 Ponytail rule text to restate verbatim in every code brief

Copy the block below into every worker brief that involves writing or reviewing code, unchanged. Do not paraphrase it. Do not shorten it.

    PONYTAIL (standing rule, owner order 26/11, github.com/DietrichGebert/ponytail, MIT). Skill: ~/workspace/custom-skills/ponytail/SKILL.md (read it at task start). Smallest complete change that fully solves the task. Reuse what exists in the codebase before writing new code. Standard library and platform features before new dependencies. Never add a dependency for a few lines. No unrequested abstraction, wrapper, option, config, or for-later code. One small test or assert-based self-check for non-trivial logic (a branch, a loop, a parser, money or security, or a whole new script). Never cut validation at trust boundaries, error handling that prevents data loss, security, or accessibility. Fix bugs at the root cause in the shared code after grepping every caller. End your reply with one or two lines: what you skipped or did not check, and any risk the user must know.

## 2. Graphify: codebase knowledge graph for laptop CLIs

Graphify (github.com/Graphify-Labs/graphify, Apache-2.0) turns a codebase into a queryable knowledge graph with tree-sitter AST extraction. Code parsing is local, deterministic, and needs no LLM credits. Agents query graph.json instead of re-reading whole files. Docs and papers need an LLM key for semantic extraction. Code-only builds need no key. That distinction decides the laptop plan: code-only everywhere, semantic extraction only where a key already exists and the owner approves its use.

Current state, verified 26/11:
- VM: graphify 0.9.120 installed via uv tool (PyPI package graphifyy, double y). Binaries at ~/.local/bin/graphify and ~/.local/bin/graphify-mcp. Note for briefs: graphify is not on the default non-login PATH on the VM, so VM commands use the full path ~/.local/bin/graphify or export PATH first. Graph built for computer-use-wayland at ~/workspace/cu-graphify/graphify-out/ (graph.json, graph.html, GRAPH_REPORT.md, manifest.json). Registry record: code-only AST, 7903 nodes, 16640 edges, 430 communities, built from commit f58e341d, query verified working.
- Laptop: graphify NOT installed. uv 0.13.9 is present. No ~/cu-graphify, no graphify-out directory. Registry status: NOT INSTALLED, PROPOSED, laptop install is re-plan scope.

Where the graph lives for laptop use (council decision): the graph lives with the checkout the agent queries. Laptop agents work in the laptop checkout of computer-use-wayland, so the laptop graph is built on the laptop from the laptop checkout and stored in that checkout at graphify-out/graph.json. The VM graph at ~/workspace/cu-graphify/graphify-out/ stays the reference copy. Do not copy the VM graph.json to the laptop as the working graph. A copied graph drifts the moment either checkout moves, and a stale graph that answers confidently is worse than no graph. Copying is allowed only as a one-time seed for comparison during verification, clearly labeled, never as the queried graph.

Freshness rule: rebuild after big code changes, and before any task that depends on graph answers about changed code. Rebuild commands (from the registry, verified on the VM): graphify . --code-only, then graphify cluster-only . . For incremental refreshes, graphify update <path> re-extracts code files with no LLM. Record the source commit in the registry entry at every rebuild. If the graph and the code disagree, the code wins and the graph gets rebuilt before the task proceeds.

### 2.1 Exact installation steps (post-approval only)

Pre-check on the laptop (repeat at install time): which graphify (expect absent), uv --version, ls the laptop checkout path and record its git HEAD. Confirm the checkout is the computer-use-wayland repo the run uses. Do not build a graph for the wrong tree.

Install the CLI on the laptop:

    uv tool install graphifyy

Verify: ~/.local/bin/graphify --help prints the command list (install, path, explain, section, update, cluster-only, and the rest). Record the version: ~/.local/bin/graphify --version if supported, else uv tool list. The PyPI package name is graphifyy with double y. The binary name is graphify. Do not confuse the two in briefs.

Install the per-CLI skill copies (graphify ships its own platform installer):

    graphify install --platform codex
    graphify install --platform claude
    graphify install --platform opencode

Supported platforms include claude, codex, and opencode. Run one platform at a time, read back where the skill landed (the installer prints the target config dir), and record the path per CLI in the registry. FCC uses the claude platform, because fcc-claude is Claude Code and loads skills from ~/.claude/skills/. If the installer writes outside the expected skills dir for any CLI, stop, record the actual path, and do not hand-move files until the coordinator confirms the CLI reads from there.

Build the laptop graph from the laptop checkout:

    cd <laptop checkout of computer-use-wayland>
    graphify . --code-only
    graphify cluster-only .

Both steps run detached with logs if they exceed 25 seconds. Record: wall-clock start, elapsed time, source commit (git rev-parse HEAD), node count, edge count, community count from GRAPH_REPORT.md. The VM reference numbers (7903 nodes, 16640 edges, 430 communities at f58e341d) are a sanity range, not a pass bar. Counts differ if the laptop checkout is at a different commit. A large unexplained gap (for example half the nodes) is a stop-and-investigate, not a pass.

### 2.2 Live verification (timed and logged)

State proof: graphify --help works from ~/.local/bin, the three platform skill copies exist at the paths the installer printed, graphify-out/graph.json exists in the laptop checkout, and GRAPH_REPORT.md carries the counts and source commit.

Behavior proof, a query that returns known nodes. Use two queries so one lucky hit cannot pass the gate:
1. graphify explain on a node that must exist in this codebase (for example the session driver or the zen backend module). Pass: the output names the node, its file, and real neighbors that match the code. Fail: node not found, empty neighbors, or neighbors that do not exist in the checkout.
2. graphify path between two known nodes that are connected in the code (for example the CLI entry and the module it calls). Pass: a shortest path with real intermediate nodes. Fail: no path, or a path through nodes absent from the checkout.

Cross-check one answer by hand: open the file the graph names and confirm the symbol is there. Record the queries, outputs, and hashes in the log. Only after both proofs pass may briefs tell laptop agents to query the graph instead of reading files. Until then, agents read files as before.

Brief rule once verified: query the graph first (graphify-out/graph.json), read files only for what the graph cannot answer, and say in the report which queries were run. A graph answer is a lead, not proof. Code that will be edited gets read in full before the edit.

### 2.3 Revert path

Per CLI skill copies: graphify uninstall removes graphify from all detected platforms in one shot. Add --purge only if the graph output must also go, because --purge deletes graphify-out/. Default revert keeps the graph files and removes only the platform integration. Full removal: uv tool uninstall graphifyy after the platform uninstall, then verify graphify --help fails and the skill copies are gone. Record the revert in the registry with date, time, and verification output. The VM install and VM graph are untouched by a laptop revert.

## 3. Remaining-run operations

### 3.0 Run state at the pause point

Graded: 29 tasks. Of those, 23 PASS, 3 FAIL (the original FCC fabrications, each superseded by a PASS re-run under Rule A, original fail records untouched), 3 INVALID (each replaced by a backup PASS: DP-06, DP-02, DP-07). Rule-A counting (rerun-replaces-fail, owner approved): 23 PASS, 0 FAIL. Closure reports both countings. Invalid budget: 3 of 5 used. By difficulty: medium 2 of 2 (at cap), hard 1 of 2. Backups left: DP-05 only (very hard). DP-03 was pre-assigned at position 34 for the dropped R3-047. DP-06, DP-07, DP-02 are used. Medium backups are exhausted. That fact drives the handling in section 3.1.

In flight at the pause (epoch 8 record, 04:38:26): the R3-026 drive was BLOCKED by Cloudflare on coolors.co (Just a moment page, Ray ID a603c518ed7945df). R3-026 is an INVALID candidate in Pair A scoring. If R3-026 grades INVALID, the invalid count becomes 4 of 5. That is an owner-notification point (section 3.5). Council-1 owns the counting analysis. This council owns the operations handling: scoring completes from the sealed evidence, no re-drive is released while paused, and the count is reported at the gate before any resume. Also in flight: R3-025 fresh completion drive (runner 52e38de8, started 04:39:00, deadline about 05:09:00). Attempt-1 verdicts for R3-025 were both FAIL with no ledger row, so the fresh drive is the graded attempt. It finishes, gets snapshotted, gated, and scored under the normal rules. No new task releases behind it while the run is paused.

Remaining after in-flight: 30 original-set tasks in fixed order (positions from thu-tu-chay.txt): R3-027 (23), R3-028 (24), R3-029 (25), R3-035 (26), R3-036 (27), R3-037 (28), R3-045 (32), R3-046 (33), DP-03 (34), R3-049 (35), R3-055 (36), R3-067 (37), R3-072 (38), R3-074 (39), R3-075 (40), R3-076 (41), R3-078 (42), R3-079 (43), R3-082 (44), R3-083 (45), R3-085 (46), R3-086 (47), R3-088 (48), R3-089 (49), R3-093 (50), R3-094 (51), R3-096 (52), R3-098 (53), R3-099 (54), R3-100 (55). Positions 29, 30, 31 (R3-040, R3-041, R3-042) are already graded and do not appear in the remaining list. Then task 56 at position 56 (section 3.2). Bar: 53 of 55 on the original set, 54 of 56 with task 56. Closure counts both ways.

Class L remaining (score-before-reset, runner waits for the grade): R3-055, R3-074, R3-075, R3-078, R3-079, R3-088, R3-089, R3-096. Eight tasks. Every other remaining task is Class S (score from sealed snapshot, reset may proceed after the gate). Backpressure stays at 2 unscored tasks per runner. One driver at a time on the shared Zen session. That serialization is not optional. It was bought with the R3-040 attempt-2 session collision and the owner kept it on 25/11 (no second session, no parallel driving).

### 3.1 Watch items with exact handling

R3-029 (position 25, FCC lane). Needs the owner-held password for the test account rung3-029-test@example.com on ecommerce-playground.lambdatest.io. The key was verified correct before the run (all 5 product names with prices, wishlist works). Handling, no exceptions: the parent re-verifies with the owner before the position arrives. The password goes in the task brief at release time only. It never goes in any file, state file, ledger, log, or commit. The coordinator notifies the parent as the position approaches (at position 24 release at the latest, earlier if the pause makes timing uncertain). If the password is not confirmed by release time, R3-029 is held and the coordinator reports to the parent. The runner never guesses, never reuses another credential, and never asks the owner directly. After the task, the brief copy holding the password is destroyed and the destruction is logged without the value.

R3-028, R3-036, R3-046 (positions 24, 27, 33). INVALID candidates sharing the timeanddate.com cause with R3-011. Counting rule (frozen): one proven shared service incident counts as 1 invalid event against both the total cap (5) and the per-difficulty cap (2), while each affected task still leaves the sample and still follows the backup rule. R3-011 already graded, so the shared-cause question is whether these three fail for the same proven cause. Per-event counting applies. A curl 403 alone is never proof of a browser block. Each candidate needs browser evidence plus scorer-2 independent confirmation. Backup reality: medium backups are exhausted (DP-06 and DP-07 used, DP-03 pre-assigned). If any of the three grades INVALID, it drops from the sample with no replacement. B-F4 rule (frozen): if valid tasks fall to 53, the bar recomputes to 51 of 53, the coordinator notifies the owner, and the run does NOT stop. Lack of a backup is never a stop condition. The coordinator records each decision with its evidence. Runner-caused failures (rapid repeated calls, tab floods, service hammering) are FAIL, never INVALID.

R3-026 (position 22, scoring now). Cloudflare block on coolors.co. Handling: Pair A scores from the sealed evidence. The coordinator does not re-drive, does not coach the scorers, and does not pass a preferred verdict. If the grade is INVALID, invalids become 4 of 5 and the owner is notified at that point (section 3.5). The backup question for R3-026 follows its difficulty group and the remaining backup DP-05 only if the group matches. Council-1 owns the counting analysis. Operations owns the sequencing: no replacement task releases until the re-plan gate passes.

R3-079 coupled reset (position 43, Codex, Class L). Pair: R3-078 (position 42) creates a backup in ~/rung3/d45-backup. R3-079 restores into ~/rung3/d46-restored. Exact check before R3-079 starts, after R3-078 is scored and reset: (a) R3-078 snapshot gate PASS and R3-078 graded; (b) ls ~/rung3/d45-backup returns No such file and ls ~/rung3/d46-restored returns No such file; (c) the d46 fixture is intact in ~/rung3-goc/. If d45-backup still exists after the reset, the reset failed. Do NOT start R3-079. Report to the parent and fix the reset first. Both tasks are Class L, so the runner waits for each grade before each reset. General rule for every task, not only this pair: before any task starts, diff -r -q ~/rung3/ ~/rung3-goc/ must be empty. After any task: snapshot, manifest gate, grade or queue the grade, reset, re-run the diff. The reset restores ~/rung3/ from ~/rung3-goc/ and clears the evidence dir for the task just run. The reset never touches ~/rung3-goc/.

R3-089 fixture check (position 49, Codex, Class L). The fixture holds 12 log files. The key expects find -mtime -7 to return exactly 6 (log-01 to log-06 within 7 days, log-07 to log-12 older). Current state verified twice: refreshed 2026-11-25 08:59 (log-01 to log-06 at 1 day ago, log-07 to log-12 at 10 days ago), and this council re-verified read only on 2026-11-26: find ~/rung3-goc/nd09-logs -name "*.log" -mtime -7 returns 6. Hard expiry: 2026-12-01 08:59 (Asia/Ho_Chi_Minh). After that, log-01 to log-06 age out and the count falls to 0. The task becomes ungradeable. Handling: the coordinator refreshes the fixture the day before R3-089 runs, using the frozen procedure (touch -d "1 day ago" for log-01 to log-06, touch -d "10 days ago" for log-07 to log-12, in ~/rung3-goc/nd09-logs/ only, contents untouched), then verifies the count is exactly 6, then records date, time, who, count, and new expiry (refresh time plus 7 days) in rung3-run-log/r3-l3-r3-089-refresh.md. Date guard: if the run has not reached R3-089 by 2026-11-30 12:00, refresh on 2026-11-30 anyway so the fixture stays valid through 2026-12-07. Confirmation runs after the reset that precedes R3-089 and before the runner starts, on the live ~/rung3/nd09-logs/. If the count is not 6 and a refresh cannot make it 6, stop and report to the parent. Do not run R3-089 on a broken fixture. The pause makes this the most time-sensitive operations item in the remaining run.

R3-100 port check (position 55, Codex, last original task). The task reads live port state and saves an HTML page. Port state is transient, so the frozen rule makes it deterministic. Handling: before R3-100 starts, the coordinator reads the port number from the frozen key (docs/rung3-answer-keys.md, R3-100 section, the key is the source of truth, this plan does not hard-code the number), lists listening ports with ss -tlnp, and confirms the target port is in the state the key expects. A leftover process from an earlier run task holding the port gets killed (it is a leftover, not part of R3-100) and the state is re-verified. The runner records the port state at run time (ss output plus saved HTML) into the evidence folder. The scorer grades from the saved files only and never re-checks the live port. R3-100 is Class S for that reason. If the port is held by an unrelated process that cannot be killed (for example a system service), stop and report to the parent before starting. Do not run R3-100 on a port whose state cannot be made to match the key.

### 3.2 Task 56 (position 56, Class L, counted): restore pinned and essential tabs

Origin: cleanup batch 2 on 2026-11-26 at 02:15:58 closed 24 Zen tabs, including owner pinned and essential tabs. Owner amendment 02:18: restoration is a new counted task at the end of the run. The original 55 tasks and their freeze are untouched. thu-tu-chay.txt stays frozen. This task lives in improvements/r3-l3-task56-restore-tabs-20261126.md plus the state file. Closure counts both ways (53 of 55 original, 54 of 56 with task 56). Runner: Muse fresh independent subagent by default, Codex approved alternative. Opencode cannot run it. Do not assign opencode.

Evidence base: preserved sessionstore on the laptop at ~/zen-sessionstore-pre-cleanup-20261126.jsonlz4 (mozLz40 format, verified present 26/11, 3060932 bytes). A pure-python LZ4 block decompressor reads it (8-byte magic, 4-byte little-endian uncompressed size, LZ4 block). VM extraction at ~/workspace/rung3-evidence-staging/zen-sessionstore/closed-tabs-pinned-state.json. Pre-cleanup counts: 78 tabs, 49 pinned, 12 essentials. Closed: 5 essentials plus 3 pinned plus 16 normal task tabs. The 16 normal tabs are NOT restored.

Restore set, exact. Essentials, inserted after the first YouTube and before GitHub, in this order: (1) YouTube second copy, https://www.youtube.com/ (2) Reddit, https://www.reddit.com/ (3) Todoist Today, https://app.todoist.com/app/today (4) Gmail, https://mail.google.com/mail/u/1/#inbox (5) Google Calendar, https://calendar.google.com/calendar/u/1/r/week. Pinned, at the head of the pinned section, in this order: (6) PCCV CF26 Google Sheet, https://docs.google.com/spreadsheets/d/1WzUJNuCQlYLAj59-gdIPFFQv2P_d3f2KhEYcGeWhRRY/edit?gid=0#gid=0 (7) Free Claude Code Admin, http://127.0.0.1:8082/admin/model_config (8) Welcome, https://zen-browser.app/welcome/. Exact URLs, pinned flags, zenEssential flags, zenWorkspace values, and order come from the preserved sessionstore. Restore in the same workspace as recorded. If the sessionstore and this list ever disagree, the sessionstore wins and the disagreement is recorded.

Steps: decompress the sessionstore and extract the 8 tabs with URLs, flags, workspaces, order. Record the current tab list as the before state. Recreate the 5 essentials in order, each marked essential and pinned. Recreate the 3 pinned in order, each pinned and not essential. Verify with a fresh tab list plus a sessionstore read (all 8 present, correct URLs, flags, workspaces, relative order). Write ~/rung3-chung-cu/R3-056/ket-qua.txt (extracted list, before list, after list, per-tab state, any tab that could not be restored exactly with reason). Save at least 1 timestamped screenshot of the sidebar or tab bar showing the restored essentials and pinned in order. Class L: leave the restored tabs live after the drive. No reset exists for this task. The coordinator verifies against the live tab list plus sessionstore before scoring closes.

Key: pass needs all 8 tabs with exact URLs, correct pinned and essential flags, correct workspaces, correct insertion order, verified from tab list plus sessionstore, complete ket-qua.txt, screenshot showing the order. Fail is any tab missing, wrong URL, wrong flag, wrong workspace, wrong order, or a normal task tab recreated instead. Scoring by two fresh independent scorers, grader never the author.

Safety, hard rules: never close owner tabs. Restoration happens only as task 56 at run end, never earlier, never as a side favor during another task. If pinned or essential state cannot be determined from the sessionstore, ask the owner to confirm before position 56. Do not guess the setup.

### 3.3 Sequencing from now to the end

Phase 0, pause point (now). In-flight work finishes and nothing new releases. R3-025 fresh drive completes, snapshot, gate, Pair A scoring. R3-026 Pair A scoring completes from sealed evidence. Ledger rows are written only after audit passes. Pushes are verified with git ls-remote after every push. The coordinator state file is the live record. This council document commits nothing. The coordinator commits centrally.

Phase 1, Cloudflare fix. Owner order supersedes the old sequencing: the fix no longer waits until after the run. The whole team fixes it first, then rung 3 continues. Known cause (research report, 25/11): every Zen launch goes through the zen-ai wrapper, which adds --remote-debugging-port=9222 --marionette, and both flags force navigator.webdriver to true in every page. The run needs BiDi on 9222 and Marionette on 2828, so the flags cannot simply come off the run Zen. The fix must get past Cloudflare while staying optimized for AI, building a tool if needed. Council-3 operations constraints on any fix: the run Zen keeps its automation endpoints, owner tabs are never closed or navigated by a fix attempt, no launcher, wrapper, prefs, or Zen restart change lands without a live proof and a revert path, and Chromium covers chatgpt.com until the fix is proven. Live proof means a real Cloudflare-gated page passing in the fixed setup, timed and logged, not a settings screenshot. R3-026 (coolors.co) is the reminder that bot-walls hit run tasks, not only chatgpt.com. The fix gate is: proof recorded, revert recorded, council plus redteam agree, parent accepts. Until then, no resume.

Phase 2, ponytail and graphify installs. Run sections 1.2 and 2.1 in order: Codex plugin, FCC plugin, opencode verification only, graphify CLI plus platform skills plus laptop graph build. Each install gets its state proof and behavior proof (sections 1.3 and 2.2) and its registry entry. Timed and logged. Nothing installs while a drive is in flight. The FCC tmux session refresh happens in this phase, never mid-task.

Phase 3, owner approval gate. The parent presents the re-plan (this council plus council-1, council-2, redteam) to the owner. Resume needs explicit owner approval. No approval, no resume. Approval covers the sequence, the invalid handling, the task 56 plan, and the install results. Anything the owner changes goes back through council before it runs.

Phase 4, resume and remaining positions. One driver at a time on the shared Zen. Backpressure 2 unscored tasks per runner. Class L tasks score before reset, runner waits. Class S tasks score from sealed snapshots. Fixed order from section 3.0. Watch items fire at their positions (section 3.1). R3-089 refresh fires the day before position 49, or on 2026-11-30 under the date guard, whichever comes first. Zen memory is watched (section 3.5). Every task: snapshot, manifest gate, score or queue, reset, diff check, ledger after audit, push verified by ls-remote.

Phase 5, task 56. Runs last, after position 55 is graded. Live verification before scoring closes. No reset.

Phase 6, closure. Final ledger validation (validate-ledger plus ledger-cross-check, 0 errors). Both counts reported: original set against 53 of 55, full set against 54 of 56, Rule-A counting shown beside the original counting with original fail records untouched. Final report written. All pushes verified via ls-remote. Tab hygiene at the end: finished and confirmed-unused task tabs cleaned, owner tabs untouched, restored task 56 tabs left live.

Coordinator succession (applies through every phase). Epochs complete after short sessions. The parent is the continuity layer. On epoch 8 completion: takeover record first (written before any order, fencing by coordinator_active), then spawn successor plus fresh deputy, G-24 and G-38 closed for the new epoch (deputy declaration after the state edit, dry run PASS in the deputy own session). Workers obey only the current coordinator_active. A completed coordinator cannot write. No split-brain. The state file is written via temp file then rename. The successor re-reads the state file, the ledger, and this plan before releasing anything.

### 3.4 Standing rules to restate in every brief template

Every coordinator and worker brief in the remaining run carries these rules. Restate them, never assume them:

- Ponytail for all code work (section 1.6 verbatim) plus Graphify first for codebase questions (query graphify-out/graph.json, read files only for what the graph cannot answer, rebuild after big changes).
- Check before installing. Verify what is already on the machine. Never install blindly. Every install gets a skill scout registry entry.
- ydotool is banned. Restate the ban in every brief. Never assume it.
- Pill on any agent control, by any method (computer-use, CDP, Playwright, script). Pill text is plain: Computer use active. Raw CDP is read-only until a pill-on-CDP mechanism exists. Live browser writes go through the computer-use session so the pill shows.
- Full access: Codex with --sandbox danger-full-access, fcc-claude with --dangerously-skip-permissions. Equivalent full-access mode for any other CLI.
- SSH only via ~/workspace/ssh-laptop.sh (key plus IdentitiesOnly plus tailscale proxy). Bare ssh failures prove nothing. Sessions die at about 30 seconds. Long jobs run fully detached (setsid nohup, log file, disown) and progress is checked with short calls. A subagent that launches a long process attached never completes, so detach, verify running, then report.
- English for agent work and AI-to-AI communication. Vietnamese only when messaging the owner. Copy-ready prompts for Codex or other agents arrive as their own short standalone message in English markdown.
- No em dashes or en dashes in owner-visible text. Commas, periods, short hyphens only.
- No personal information on GitHub, ever. Names, addresses, emails, phone numbers, schedules, photos, accounts, passwords, tokens stay local. Repo text is generic. Leaks are blocked by a deterministic pre-commit or CI check, not by prompts alone.
- Machine-specific optimization is always-on local only. Anything committed to the repo for outside users is optional and default-off. The repo must work on stock, unoptimized apps (vision, mouse, accessibility paths stay strong).
- ZCode is excluded from AI optimization work. No edits, no CLI work, no sweep inclusion. ZCode is edited by file only.
- Never assume an agent capability. Check it or ask the agent directly in its own chat. Every brief states the delivery path explicitly (commit where, file where), never just write a report.
- Fail only after trying 2 to 3 methods and retrying several times. A failed search is not proof of absence.
- Check delivery before concluding an agent is silent. A daemon receipt (outcome sent, verified true) does not prove delivery. Check the UI status or ask the owner to look. A rising transcript count proves appearance, not receipt.
- Never close or navigate owner-opened tabs or windows. Open a new tab or window beside them. Finished task tabs get cleaned with no backlog. Each runner closes its own task tabs. The lead checks at each boundary.
- Report to the owner only when truly extremely important and only the owner can decide (security or personal data, mechanical action only the owner can do, computer-use direction, and the notification points in section 3.5). Everything else is decided by the team through council plus redteam.
- Timing and logging always on. Every test timed as precisely as possible, logged with wall-clock Asia/Ho_Chi_Minh plus elapsed time. A claim of fixed without a passing live task test is worth nothing.
- Shutdown after use. Verify on the laptop that workers are dead, finish broker sessions, confirm no session processes remain, confirm the pill is gone and the desktop is clean. Keep only what is still needed.

### 3.5 Risks for the remaining run, mitigations, notification triggers

Bot-walls even after the fix. Cloudflare and similar checks can still block individual sites (R3-026 on coolors.co is the live example). Mitigation: Phase 1 fix with live proof, Chromium fallback for chatgpt.com, per-task browser evidence for any INVALID claim, scorer-2 confirmation, no INVALID on curl evidence alone. Trigger: a bot-wall on a task with no backup left goes to the parent the same day. Owner notification only if it changes the bar or needs an owner decision.

Invalid budget exhaustion. Budget is 3 of 5 now, possibly 4 of 5 after R3-026. Medium is at cap with no backups. Mitigation: per-event counting for the proven shared timeanddate cause, B-F4 recompute (valid 53 means bar 51 of 53, notify owner, do not stop), DP-05 held for its group only. Triggers (frozen): notify the owner at invalids 3, 4, and 5. Invalid 3 was already reached. Invalid 4 fires if R3-026 grades INVALID. Invalid 5 means the next invalid makes rung 3 a new benchmark. That is an owner decision, reported immediately.

R3-089 fixture expiry if the pause runs long. Hard expiry 2026-12-01 08:59. Mitigation: date guard refresh on 2026-11-30 12:00 if position 49 is not reached, day-before refresh otherwise, count verified at exactly 6 before the runner starts. Trigger: if the refresh cannot make the count 6, stop that task and report to the parent. Owner notification only if the task cannot be graded fairly.

Scorer fatigue and compaction. Pair A and Pair B scorers grade from snapshots under 30-minute windows. Long runs compact sessions and stale scorer IDs have already caused confusion in this run. Mitigation: fresh sessions briefed identically when calibration sessions complete, verdict files only (never verdict values in chat), coordinator audit before any ledger row, tiebreakers spawned on demand. Trigger: scorer disagreement or a disputed verdict goes to the tiebreaker, not to the owner, unless the process itself is disputed.

Zen memory growth. Long Zen sessions grow toward about 8 GB RSS and need a D1 restart. Mitigation: watch RSS at task boundaries, restart only at a boundary with no drive in flight, never restart Zen to chase a fix mid-task, re-verify tabs and session after any restart. Owner tabs survive restarts only if the session restores cleanly, so a restart is a coordinator decision with a before and after tab list. Trigger: RSS near the limit with tasks remaining goes to the parent with a restart proposal. Owner notification only if a restart risks owner tab state.

Daemon deaths. The messaging daemon has died and been restarted before (24/11). Mei and mochi verdict delivery depends on it, and a receipt does not prove delivery. Mitigation: watchdog restarts, fallback channel documented (rung3-run-log/r3-l3-daemon-fallback.md), delivery checked in the UI before anyone is called silent, verdict files committed to the repo when the VM-local channel cannot cross VMs (the R3-001 lesson). Trigger: daemon dead with scoring pending goes to the parent immediately. Owner notification only if verdicts cannot be delivered by any channel.

FCC fabrication recurrence. R3-001 and R3-002 both fabricated evidence three times each. Mitigation: manifest comparison against on-disk files (never the completion report), hash checks, screenshot content checks, re-collect limits with seal-and-score after exhaustion, FCC assigned only the easiest tasks. Trigger: any new fabrication seals the evidence, scores as-is, and is recorded. Owner notification only if it threatens the bar under both countings.

Single-driver serialization cost. One driver at a time is slow by design. Mitigation: backpressure 2 keeps scoring overlapped without driving in parallel, Class S resets do not wait for grades, lane briefs are pre-issued. No mitigation may reintroduce parallel driving or a second session. The owner kept the one-session plan on 25/11. Trigger: none. Speed never trades against the session rule.

Opencode unusable. No owner-picked model, banned routes only. Mitigation: opencode gets no run tasks, ponytail verification for opencode stays file level, task 56 runner is Muse or Codex. Trigger: owner picks a model, then opencode verification (section 1.3) runs before any assignment.

SSH fragility. Sessions die at about 30 seconds. Mitigation: short commands, detached long jobs, log files, verify by readback. Trigger: none for the owner. Operations handles it.

Owner-notification summary (the only points that interrupt the owner): invalid 4, invalid 5, bar recompute under B-F4, R3-029 password re-verification before position 25, task 56 state confirmation if the sessionstore is ambiguous, the Phase 3 approval gate, and anything only the owner can decide (security, personal data, mechanical action, computer-use direction). Everything else stays with the team.

## 4. Council verdict

COUNCIL-3 verdict: PROCEED on the plan above, in the order above, with no step skipped. Ponytail installs for Codex and FCC, verification only for opencode, graphify install plus laptop graph build, all through the skill scout registry, all timed and logged, all revertible. Remaining run operated exactly as sections 3.1 to 3.5 state. Resume only after the Cloudflare live proof, the install verifications, and explicit owner approval.

Open items for the parent: (1) R3-026 grade and the invalid-4 notification if it lands. (2) R3-029 password re-verification timing as position 25 approaches. (3) Owner model pick for opencode, whenever the owner chooses, with no run dependency until then. (4) Epoch 8 succession readiness (successor plus fresh deputy, G-24 and G-38) at the next coordinator boundary.

What was skipped in this council pass: no install was executed, no laptop file was changed, no task was driven or scored, no state file was edited, nothing was committed. Live behavior proofs for ponytail and graphify are specified but not yet run, because they are post-approval steps. Risks the parent must know: the R3-089 clock (expiry 2026-12-01 08:59), the possible invalid-4 count, and the Codex bare-skill nuance (skill file present, plugin absent) which the registry summary alone would have missed.
