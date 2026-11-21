# Worker W crawl: multi-agent structures and computer-control performance

Worker: W-Crawl-2 (structures researcher)
Crawl date: 2026-11-21
Access date for every source below: 2026-11-21
Window targeted: last 30 days (since 2026-10-22). Sources found outside that window are marked OUTSIDE WINDOW and kept only when their numbers bear directly on the performance question.
Method: last30days skill (queries: "multi-agent workflow", "agent team structure", "parallel AI agents", "agent orchestration") plus browser.search on performance angles, plus direct reads of the two most load-bearing primary pages (swarm-tax experiment, Stackness parallel-agents measurement).
Coverage limits: in the skill runs, Reddit, web search and X were unreachable (Reddit search down, keyless web search unavailable, X not enabled). Findings below therefore lean on Hacker News, GitHub and browser.search results. A failed source is not evidence of no discussion.

## Work log (Asia/Ho_Chi_Minh)

- 17:42, T+0min: start. Read last30days README and AGENTS.md. Repo computer-use-wayland on branch todolist-push confirmed.
- 17:42-17:44, T+0-2min: skill query "multi-agent workflow", 24 items (13 HN, 11 GitHub).
- 17:44-17:45, T+2-3min: skill query "agent team structure", 7 items.
- 17:45-17:48, T+3-6min: browser.search, three queries (computer-use speed DOM vs vision, Worse Together, sub-agent swarm tax). Strong haul.
- 17:48-17:50, T+6-8min: browser.search, two more queries (Anthropic multi-agent research system, batching actions per observation). Read swarm-tax experiment page in full.
- 17:50-17:52, T+8-10min: skill queries "parallel AI agents" and "agent orchestration". Read Stackness parallel-agents measurement in full.
- 17:52-18:05, T+10-23min: wrote this file, committed, pushed.

## Our own baseline (internal measurements, for comparison)

- A hand-driven computer-use test took about 7 min over 12 tool calls, while the same scripted test took 2,678 ms of machine time. The gap is almost entirely think-observe-think overhead, not machine execution.
- Our 10x review found the think-observe-think loop is 87.8% of task time.
- Read the findings below against that baseline: anything that cuts model round trips or observations per action attacks the 87.8% directly.

## PART A. PERFORMANCE: cutting the observe-think-act loop (weighted first, per owner priority)

### A1. OSWorld-Human: planning dominates latency, agents take 2.7-4.3x too many steps

- Title: OSWorld-Human: Benchmarking the Efficiency of Computer-Use Agents
- Date: arXiv 2506.16042v2, MLSys 2026 proceedings. Surfaced in crawl 2026-11-21. OUTSIDE WINDOW (June 2026 arXiv version), kept because it is the only latency-breakdown study found.
- Link: https://arxiv.org/html/2506.16042v2
- Claim: large model calls for planning, reflection and judging account for most of overall latency. Planning alone is more than half, sometimes close to 75%, of total task latency for both Agent S2 and GTA1. Judging (GTA1) and reflection (S2) are the second biggest sink, 22.5% and 33.6% of total task time. As an agent uses more steps, each successive step can take 3x longer than steps at the beginning. Even the best agents take 2.7-4.3x more steps than necessary (measured against human trajectories in OSWorld-Human). 23% of errors are due to poor visual grounding, causing up to 30 extra steps on a single task.
- Evidence: MEASURED. Step breakdown of 39 representative OSWorld tasks across two frameworks, 16 agents evaluated on OSWorld-Human.
- Relevance to us: our 87.8% think-observe-think share matches this paper's shape (planning plus reflection/judging dominate, execution is small). The levers it points to: fewer steps, less planning per step, no per-step judging/reflection round trips.

### A2. Hybrid Computer Use (HCU): batch actions per call, compact observations, AX diffs

- Title: Hybrid Computer Use: A Unified Programmatic, Semantic, and Visual Interface for General Agents
- Date: October 2026 (arXiv 2610.41432v1). Inside window.
- Link: https://arxiv.org/html/2610.41432v1
- Claim: combine three channels (programmatic code/CLI, semantic accessibility tree, visual GUI) in one interface. The accessibility (AX) tools return compact observations, execute actions in batches, and report their effects as AX diffs, so the model needs fewer round trips. On OSWorld 2.0, HCU achieves the highest Partial and Binary scores among compared systems. With GPT-6 Astra it reaches 72.37% Partial, outperforming CUA Driver by 3.55 points. All evaluated models improve with HCU and consistently outperform baselines on both efficiency and task success.
- Evidence: MEASURED. Benchmark scores on OSWorld 2.0, OSWorld 1.0, WeaveBench, MacAgentBench, Windows Agent Arena.
- Relevance to us: this is the closest published match to our own priority ladder (CLI first, then code-exec, then vision). Batching plus diff-based observation (only what changed, not a fresh full screenshot) is exactly the "one observation yields many actions" direction.

### A3. Qwen-UI-Agent: more than 40% of actions batched, far fewer steps per task

- Title: Qwen-UI-Agent technical report (via Minjae's Paper Blog summary)
- Date: blog post 2026-07-31. OUTSIDE WINDOW, kept for the batching numbers only.
- Link: https://sgtcho.com/en/paper/2026-07-31-qwen-ui-agent-technical-report-toward-next-generation-real.html
- Claim: GUI and CLI in a single action space, batch actions that emit multiple actions in a single model turn, reducing unnecessary observation and reasoning steps. More than 40% of action outputs were executed in batches. It required 58.4% and 21.7% fewer steps per task than MiniMax M3 and Qwen 3.7 Plus respectively. OSWorld-Verified 79.5% (2nd overall), ScreenSpot-Pro zoom-in 81.5%.
- Evidence: MEASURED. Benchmark scores and step counts from the paper's evaluation.
- Relevance to us: independent confirmation that batching is common in the best systems (40%+ of outputs batched) and that it shows up directly as fewer steps per task.

### A4. OpenBot research notes: code execution is the single biggest latency win

- Title: How ChatGPT's Computer Use Works (research notes)
- Date: last updated 2026-09-16. OUTSIDE WINDOW, kept because it states the mechanism clearly.
- Link: https://github.com/jccrump/openbot/blob/HEAD/docs/research/computer-use.md
- Claim: "Speed comes from collapsing the loop. The biggest lever is not a faster model, it is replacing N screenshot-to-click round trips with one code call that performs many actions. OpenAI's own API docs now recommend a code-execution harness over the step-by-step computer tool." Seven levers in order of impact, starting with code execution collapsing the loop, then batched actions per turn (the legacy computer tool returns an ordered actions array, click followed by type in one call), then observation budget discipline (current screenshot plus short action history, not full image history). Generations table: Operator Jan 2025 (screenshots only) OSWorld 38.1%; ChatGPT agent Jul 2025 (visual plus text browser plus terminal) BrowseComp 68.9%; 2026 GPT-6 Astra / ChatGPT Work (screenshots plus ARIA/DOM plus headless Chrome, Playwright/PyAutoGUI code execution) OSWorld 2.0 72.6% in about 40 min/task.
- Evidence: MIXED. The benchmark numbers are measured (OSWorld, BrowseComp); the "biggest lever" ranking is the author's synthesis of OpenAI docs and observed failures, not a controlled experiment.
- Relevance to us: matches our CLI/code-exec-first ladder and the "one observation, many actions" rule. Note the 40 min/task figure: even the best 2026 system is slow in wall time, so the win is relative, not absolute.

### A5. PureTensor bake-off: the same model runs 3x slower in a heavy harness

- Title: Click Accuracy Picks the Wrong Browser Agent (PT-R-2026-028 v1.0)
- Date: 2026-09-26. OUTSIDE WINDOW (about 8 weeks), kept for the harness-speed measurement.
- Link: https://puretensor.ai/papers/PT-R-2026-028_Click_Accuracy_Picks_the_Wrong_Browser_Agent_v1.0.pdf
- Claim: five setups compared on 39 live tasks, scored only by verified end state, no LLM judge. The same Qwen3.8-27B weights scored 37/39 at a median of 38.2 s inside browser-use with vision on, versus 38/39 at a median of 12.7 s in a lean screenshot loop, 3.0x slower at the median. The DOM-only incumbent (DeepSeek-V4.1-Flash inside browser-use) scored 39/39 but needs four GPUs across two nodes. Every screenshot-only agent failed the one multi-field form with autocomplete; both setups that could read the DOM passed it. A viewport trap moved clicks about 12% too low (headless Chrome 1280x800 window reports a 1280x713 page). Click accuracy mis-ranked models: UI-Venus-2-9B hit 95.8% on clicks but the ranking did not predict live-task results.
- Evidence: MEASURED. 72-target click corpus plus 39 live tasks, one run each, authors state the top four setups cannot be separated on this sample.
- Relevance to us: the harness matters as much as the model. A heavy loop can cost 3x on identical weights. Also a warning for our own grounding: verify viewport geometry, a wrong constant silently shifts every click.

### A6. DOM vs vision head-to-head: DOM 15 s vs vision 75 s on the same task

- Title: Specialized Computer Use Models Research (olliebot docs)
- Date: UNVERIFIED. No date in the document; surfaced by browser.search with last crawl 30 days ago. Treat date as unknown.
- Link: https://github.com/joechiu-uipath/olliebot/blob/HEAD/docs/research/computer-use-models-research.md
- Claim: specialized vision computer-use models are NOT faster than DOM-based approaches in real-world use. Head-to-head: DOM-based agents (Browser Use) complete a task in 15 seconds while Gemini Computer Use takes 1 minute 15 seconds for the same task, 5x slower. Average step time 3 s (DOM) vs 11-15 s (vision). Full task trajectory 68 s vs 225-330 s. Every screenshot adds about 0.8 s of latency for image encoding alone. Benchmark table: OSWorld Claude Computer Use 66.3% (Opus 4.5) vs human 72.4%; WebVoyager OpenAI CUA 87%, Gemini 83.5%, Claude 56%. The 225 ms latency claim for Gemini 2.5 Computer Use is model inference only, excluding screenshot capture, encoding, network round trip, action execution and UI settling.
- Evidence: MEASURED, but secondhand. The timing table is attributed to "Browser Use benchmarks" without a link in the snippet; the OSWorld/WebVoyager numbers match published benchmarks. Verify before quoting the 15 s vs 75 s pair externally.
- Relevance to us: supports DOM/accessibility-first control for browser work and explains why screenshot-per-action is expensive. The "0.8 s per screenshot for encoding alone" is a useful floor: even a perfect vision model pays it on every observation.
- Companion source, same conclusion, OPINION with illustrative numbers: "How AI Agents Actually See Your Screen: DOM Control vs Screenshots Explained", dev.to, https://dev.to/m13v/how-ai-agents-actually-see-your-screen-dom-control-vs-screenshots-explained-41 (about 249 days old, OUTSIDE WINDOW). Claims screenshot approach 1,500-7,000 ms per action vs DOM 20-100 ms per action; a 5-field form takes 22-77 s screenshot-based vs 0.2-1.1 s DOM-based. No experiment behind the table, it is an illustrative estimate, not a measurement.

### A7. Claude Code re-sends background agent transcripts: context cost of parallel agents

- Title: Claude Code regularly sends each background agent's transcript to its model (HN discussion of a gist)
- Date: 2026-10-29. Inside window. HN score 591 points, 236 comments.
- Link: https://gist.github.com/flamerix-ai/c3905705cc4205e5de3011fa2e74efce (via https://news.ycombinator.com, item discussed 2026-10-29)
- Claim: Claude Code regularly sends each background agent's transcript back to its model, so parallel subagents multiply context traffic, not just token spend.
- Evidence: MEASURED (transcript inspection, per the gist), but I did not open the gist itself; the HN engagement (591 pts) is the signal I verified. Mark the mechanism as reported, not independently verified by me.
- Companion, MEASURED from session transcripts: claude-code issue 106025 (2026-10-29), https://github.com/anthropics/claude-code/issues/106025 : "98% of a 2.4B-token multi-agent run was re-sent context". One week (Opus 5.5, two machines, one web-app build) reached about 80% of a weekly Max 20x limit, measured from session transcripts with usage deduplicated.
- Relevance to us: parallel workers are not free even when they succeed; the coordinator pays re-sent context for every worker transcript. Keep worker reports short and structured, and prefer file references over pasting full transcripts into the coordinator context.

## PART B. STRUCTURES: coordinator/worker patterns, what works and what fails

### B1. Anthropic "Worse Together": one coordinator beats a team of peer agents in all four environments

- Title: Worse Together: How Performance Breaks Down in Multi-User Multi-Agent Teams
- Date: 2026-11-11. Inside window.
- Link: https://alignment.anthropic.com/2026/worse-together/
- Claim: in four simulated environments (shared API-token budget, clinic calendar, group food order/travel booking, merge queue with release cutoff), a single coordinator agent serving everyone beat a peer-to-peer team of per-user agents in all four environments, for both Claude Opus 5 and Claude Sonnet 5, by about 10 to 45 percentage points. In the API-key environment, peer teams reached 47% (Opus 5) and 38% (Sonnet 5) of coordinator performance, 30% and 12% of the optimal outcome against 64% and 32% for the coordinator. Failure modes: stalling as teams grow (many agents never act at all, more sit out from 4 to 16 agents), overriding other users' requests, unsupported claims about other people, checkout race conditions. A guard (do not commit until unread messages are read) recovered failed team episodes to 73% (Opus 5) and 62% (Sonnet 5) on reruns. Three environments released as MAMUBench.
- Evidence: MEASURED. Controlled simulation, 77 scenarios in the paper, frontier models from Anthropic, OpenAI and Alibaba. Caveat, stated by Anthropic and by secondary coverage: simulated environments, not live deployments; and these were per-user peer agents with competing goals, not one manager directing specialist subagents. Do not overgeneralize to our setup.
- Relevance to us: the strongest recent evidence FOR our shape (one coordinator, workers that do not negotiate with each other) and AGAINST peer-to-peer agent teams. The stalling finding matches our own stuck-agent history. The unread-message guard is a concrete pattern worth stealing: a worker must not commit/land until it has read all incoming messages.

### B2. Swarm-tax experiment: a planner-coder-reviewer team lost to one agent, 144 runs

- Title: Does a team of coding agents beat one agent?
- Date: 2026-10-26. Inside window. Controlled trial, pre-registered hypotheses, full data published.
- Link: https://programmingtheloop.com/experiments/swarm-tax/
- Claim: Codex CLI 0.157 (gpt-5.6-luna, medium effort), six features, 144 runs, hidden acceptance tests. One agent passed 56.8% of hidden tests; planner-coder-reviewer team passed 25.7% (difference minus 31.2 points, 95% interval minus 40.8 to minus 21.9). Bigger team (two coders, three review rounds) reached 48.1% at 3.7x the cost. Giving every team member the task file (not just the planner's summary) raised the team from 25.7% to 54.1% (plus 28.5 points), level with one agent at about 1.6x the cost. Every time an agent reviewer approved a change, the change failed hidden tests: 24 of 24 approvals. Median time per run: one agent 2.3 min, team 3.9 min, bigger team 6.9 min. A first attempt stalled: a wrong messaging tool name left the planner waiting an hour for a reply that never came, with no error.
- Evidence: MEASURED. 144 runs, bootstrap confidence intervals, Holm-corrected p values, all runs graded, reproduction data on GitHub.
- Relevance to us: the single most applicable finding in this crawl. Two rules map directly onto our setup: (1) every worker must read the ORIGINAL task/brief, never a coordinator's summary, because hand-offs lose field names, status codes and edge cases (one agent's code contained 84% of stated field names/status codes, the team's 63%); (2) an agent reviewer's approval is not evidence, 24/24 approvals went to code that failed hidden tests, so keep independent acceptance tests and a human-visible check. Our repo-based briefs (coord files, BOARD.md) already implement rule 1; this experiment is the evidence for keeping them.

### B3. Sub-agent concurrency benchmark: solve rate fell 83% to 59%, cost up 1.41-3.31x

- Title: Empirical Benchmark Unmasks Sub-Agent Concurrency: SWE-bench Success Drops 24% as Token Costs Surge up to 3.3x
- Date: circa 2026-11-20/21 (surfaced 2026-11-21 as updated 10 hours ago). Inside window.
- Link: https://aicoder.com/news/news-1792472743870-ib8id
- Claim: 2,124 runs across Claude Code, Codex and Kimi Code, 354 tasks, about $20.8K API cost. On 100 SWE-bench Verified tasks, enabling sub-agents dropped Claude Code's solve rate from 83% to 59% and latency rose from 17.5 to 27.8 minutes; Kimi Code fell 77% to 59%; Codex stayed at 71%. Token consumption inflated 1.41x to 3.31x. Three failure modes: unbounded fan-out and budget exhaustion, orphaned child processes (parent submits before workers return), delivery race conditions (concurrent edits overwrite each other). Gains only on massive multi-file projects (LoopsBench 7.1% to 21.4%). Authors recommend sequential execution as the default.
- Evidence: MEASURED, large sample, but I read the news summary, not the underlying study. Treat the numbers as reported by the study author (@zhou_xiaoma) via this summary.
- Relevance to us: fan-out is the default failure mode. Cap the number of concurrent workers, join every worker before the coordinator concludes, and keep workers on disjoint files/areas to avoid delivery races. Sequential is the recommended default; parallelize only when the parts are truly independent.

### B4. Nosov 288-run test: sub-agents added cost only, same recall

- Title: Stop telling Claude Code to use sub-agents: 288 runs, same recall, up to 221% more cost
- Date: 2026-11-07 (Qiita, via nosov.ai summary). Inside window.
- Link: https://nosov.ai/library/lib-2026-11-07-stop-telling-claude-code-to-use-sub-agents-288/
- Claim: 288 runs, six repos, 151 target items, pre-registered rubric, full data public. No instruction: Haiku 98% recall at $0.0056 per run, Opus 100% at $0.16. With sub-agents: Haiku $0.0098-0.012 (plus 74% to plus 116%), Opus $0.39-0.51 (plus 143% to plus 221%), recall 97-99%. Raising sub-agent effort did not improve search. Without an instruction, Claude Code never called a sub-agent on its own: 0 of 72 runs here, 0 of 504 in an earlier test. Sub-agents inherit the main agent's model (an Opus session spawns Opus sub-agents). 210 of 216 sub-agent runs had no answer in the first result event; four Haiku runs did not exit for 20 minutes after answering.
- Evidence: MEASURED. Pre-registered, public data, both scorings published after a scoring fix.
- Relevance to us: for read/search work, sub-agents cost 2-3x for no recall gain. Use workers for genuinely parallel independent work, not as a default. Also a practical warning: workers that do not exit cleanly waste wall time; our watchdog pattern exists for exactly this.

### B5. Stackness: parallel agents give 1.2-1.8x, not Nx

- Title: How much faster are parallel coding agents? About 1.5x, measured on 364 runs
- Date: 2026-11-11. Inside window.
- Link: https://stackness.dev/blog/how-much-faster-are-parallel-coding-agents-measured-on-364-runs
- Claim: 364 timed Claude Code task runs, July to November 2026. Effective parallelism (agent-hours divided by busy hours) averaged 1.21 overall, 1.46 in the busiest window, 1.82 in a six-agent 106-task run. Rule of thumb: effective parallelism about 0.3x the agent cap. The merge is where parallel lanes pay back time: one worktree merged 24 days later needed 92 files resolved by hand and 56 minutes plus four full check runs. A second agent on the same machine made `make check` 37-54% longer. Recommendation: two lanes, a third only with its own database and test slot per lane, merge into main at least once a day. Human review is the bottleneck: 60% of the busiest 94-hour window had no agent running, lanes waiting on the human.
- Evidence: MEASURED. Timing reports joined with the git log, evidence folder published, single repo/developer/harness caveat stated by the author.
- Relevance to us: plan for 1.5x, not Nx, when adding workers. Merge daily (we already push as we go). Two lanes is the honest default; more lanes need separate test slots. The human (owner) review queue, not agent count, is usually the bottleneck.

### B6. CooperBench: coordinating agents do much worse than a single agent

- Title: CooperBench: Why Coding Agents Cannot be Your Teammates Yet
- Date: arXiv 2601.13295, PyPI 0.0.1 listed Jan 27, 2026. Date as shown; outside the 30-day window if the January date is right, surfaced in this crawl. Flagged, not relied on.
- Link: https://pypi.org/project/cooperbench/0.0.1/
- Claim: coordinating agents perform much worse than a single agent given the same total workload. GPT-5 and Claude Sonnet 4.5 achieve only 25% success with two-agent cooperation, roughly 50% lower than when a single agent handles both tasks. Agents spend up to 20% of their budget on communication, reducing merge conflicts but not improving overall success.
- Evidence: MEASURED (benchmark), as reported on the PyPI page. I did not read the paper itself.
- Relevance to us: communication between workers costs up to 20% of budget and does not fix the success drop. Another vote for coordinator-mediated communication (workers talk through the coordinator/repo) rather than worker-to-worker chat.

### B7. Anthropic multi-agent research system: the one big success, at 15x token cost

- Title: How we built our multi-agent research system (Anthropic Engineering)
- Date: June 2025. OUTSIDE WINDOW, canonical background, included because every other source references it.
- Link: https://www.anthropic.com/engineering/multi-agent-research-system
- Claim: lead agent plans, spawns 3-5 parallel subagents with isolated contexts, synthesizes. Beat a single-agent Claude Opus 4 by 90.2% on Anthropic's internal research eval; research time cut by up to 90% on complex queries. Cost: agents use about 4x more tokens than chat, multi-agent about 15x. Token usage alone explained about 80% of performance variance. Mixed tiers help: Opus lead plus Sonnet workers beat single Opus while containing cost. Subagents write outputs to a shared filesystem and return lightweight references instead of piping large results through conversation history. Plan persisted to external memory because the 200K context window gets truncated.
- Evidence: MEASURED, but on Anthropic's own internal eval, not an independent benchmark. The 90.2% figure is vendor-reported.
- Relevance to us: the success case is read-heavy, loosely coupled research with isolated contexts, not tightly coupled coding or GUI control. The transferable patterns: workers return condensed summaries plus file references (not full transcripts), the coordinator persists the plan outside context, cheap models filter while the expensive model synthesizes. Note the 15x cost: multi-agent only pays for high-value tasks.

### B8. Minor signals (not load-bearing)

- Thrum (Show HN 2026-11-09, https://thrum.team/): run Claude Code, Codex and other coding agents as one team. HN thread: top questions were overhead (CPU/RAM per agent) and "how does it handle 100+ agents when most multi-agent tools struggle to keep them productive". No measurements published. OPINION/HYPE level.
- Muxlio (HN 2026-11-20, https://muxlio.github.io/muxlio/): workflow coordinator for multi-step work across agents and tools. Announcement only, no measurements.
- KradleBench (Show HN 2026-11-18, https://www.kradle.ai): multi-agent AI evals in Minecraft. Astra 6.2 scored unexpectedly high. Benchmark announcement, numbers are the benchmark's own leaderboard.
- Multi Agent Coordination Benchmark (Bespoke Labs, 2026-11-18, https://benchmarks.bespokelabs.ai/multi-agent-coordination-bench/): new benchmark, no results quoted in the crawl.
- "Building a Multi-Agent System from Scratch: Architecture Patterns" (kadhar.dev, HN 2026-11-05, 106 pts, 45 comments, https://kadhar.dev/blog/multi-agent-systems-from-scratch): top HN comment (bob1029) argues sub-agents (nested prompt wrapped in a tool call) beat multi-agent frameworks. OPINION, highly upvoted, no measurements.
- "Embracing Multi-Agent Development" (tombedor.dev, HN 2026-11-13, https://tombedor.dev/multi-agent-orchestration/): practitioner post, no numbers surfaced.

## Synthesis: what this means for our setup

Our setup: one coordinator directing many workers, plus outside agents contacted only through a shared repo (coord files, BOARD.md, PR comments). The crawl supports this shape and warns about its failure modes.

1. Keep the coordinator. Anthropic's Worse Together (B1) is the freshest controlled evidence: a single coordinator beat peer-to-peer agent teams in 4 of 4 environments by 10-45 points. Peer-to-peer worker chat is the thing that fails, not coordination itself. Our repo-mediated contact (workers never talk directly) matches the winning formation.
2. Every worker reads the original brief, never a summary. The swarm-tax experiment (B2) quantifies the cost of summaries: 25.7% vs 56.8% pass rate, recovered to 54.1% only when every agent read the task file. Our coord-file and BOARD.md practice already does this; do not regress to summary-only briefs.
3. Attack the 87.8% loop share first, before adding workers. OSWorld-Human (A1) says planning plus reflection/judging dominate latency and best agents take 2.7-4.3x too many steps. HCU (A2) and Qwen-UI-Agent (A3) show the concrete fix: batch several actions per model turn, return compact diff observations instead of full screenshots, prefer code/CLI/AX over vision. OpenBot (A4) and PureTensor (A5) agree the harness can cost 3x on identical weights, and DOM beats vision 5x on the same task (A6).
4. Expect 1.5x from parallelism, not Nx, and budget for it. Stackness (B5) measured 1.21-1.82 effective parallelism; Nosov (B4) and the 2,124-run benchmark (B3) show sub-agents cost 1.4-3.3x tokens and can cut solve rates (83% to 59%). Two lanes is the honest default; merge daily; cap fan-out; join every worker before concluding (orphaned workers are a named failure mode in B3).
5. Do not trust agent review as a quality gate. Swarm-tax (B2): 24 of 24 reviewer approvals went to code that failed hidden tests. Keep independent acceptance tests and the owner's check.
6. Watch the context tax. Claude Code re-sends background agent transcripts (A7) and one measured run was 98% re-sent context out of 2.4B tokens. Workers should return short structured reports plus file paths, not full transcripts.
7. Steal the unread-message guard. Worse Together (B1): requiring agents to read incoming messages before committing recovered failed episodes to 73% (Opus 5). Our watchdog plus "read the repo state before landing" is the same idea.

## Gaps and UNVERIFIED items

- Reddit, X and keyless web search were unreachable during the skill runs, so community discussion on Reddit and X is missing from this crawl.
- The olliebot DOM-vs-vision timing table (A6) is attributed to "Browser Use benchmarks" without a direct link in what I read; verify before quoting externally.
- The 2,124-run sub-agent benchmark (B3) was read via a news summary, not the underlying study; the numbers are the study author's as reported there.
- The gist behind A7 was not opened; the transcript re-send mechanism is reported, not independently verified by me.
- The CooperBench date (B6) is ambiguous in the sources surfaced; its January 2026 listing would put it outside the window.
- No source found in this crawl that measures "one observation yields many actions" as a standalone intervention with an A/B wall-time number on a desktop GUI task. HCU (A2) and Qwen-UI-Agent (A3) are the closest published evidence, via batching and step counts. This is a gap worth a direct experiment on our own test cases.
