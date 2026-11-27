# Working Structure Redesign Proposal

- Date: 2026-11-21
- Team: Worker W (coordinator), crawlers W-Crawl-1/2/3, council A/B/C, redteam
- Repo: computer-use-wayland, branch todolist-push
- Status: PROPOSAL ONLY. No structural change is implemented here. Muse decides what to apply.
- Owner priority: PERFORMANCE WHEN MUSES CONTROL THE USER'S MACHINE comes first. The single most valuable first step is a concrete performance lever, not an org-chart change. Super I input work is NOT important and is left out of this proposal.
- Standing rules applied: no fabrication, every claim carries a source plus access date, unknown is UNVERIFIED. No em dash or en dash anywhere in this file. Never ydotool. Never push personal info to GitHub.

## 1. What the clip teaches

The clip is a Vietnamese recap of Lauren Tan's talk "All Code Is Slop (Except Mine)" at the AI Engineer Code Summit, 14 Nov 2026. Video 7710239842663288071 by @anythingai39, posted 2026-11-20, 3 min 43 sec, 61,792 plays. Resolved via short-link, tikwm mirror API, local Whisper transcription of all 222.98 seconds, cross-checked against independent write-ups of the original talk (AGI Hunt, The AI Record, Korean summary). Full evidence: improvements/worker-w-crawl-clip-20261121.md, commit c1cc7d8, accessed 2026-11-21.

Lauren Tan ("Sister Potato"), Grok Bot engineer at SpaceX/xAI, ex Netflix/Meta, finance background, once barely coded. She alone shipped 3,000+ PRs in a month; her team 11,000 PRs at about 0.5% revert rate. Those headline numbers are SpaceX self-reported claims, not audited, and depended on free Grok tokens at SpaceX plus a very strong orchestrator model. The method transfers; the headline output does not.

The five teachings, verified against the transcript and the write-ups:

1. Delegate code writing to agents. The human's job moves up to directing, not typing.
2. An agent's "done" means nothing without runnable verification evidence: test results, screenshots, video, formal verification. Human review shifts to checking those artifacts.
3. A repeated agent mistake becomes a deterministic rule (lint rule, type, test, architecture), never a reminder. Example: the Electron main/renderer split enforced by dependency analysis plus lint rules.
4. The codebase is a garden. AI copies whatever it sees, including temporary hacks, so prune constantly and fix recurring problems in code and tooling, not in prompts or docs.
5. Repeated operations become tools; effective repeated approaches become skills. Every time the AI errs or succeeds, ask "can this later run without me?" and compound the system.

## 2. What the crawl found

28 primary sources across two crawl files, all accessed 2026-11-21: improvements/worker-w-crawl-structures-20261121.md (13 sources, commit 4b715b8) and improvements/worker-w-crawl-bottlenecks-20261121.md (15 sources, commits 5c22bd4, 539a405). Last30days engine coverage was partial in this run (X, YouTube, Reddit search unreachable; Hacker News heavy). Each source is labeled MEASURED or OPINION in the crawl files; secondhand and UNVERIFIED items are flagged there and kept flagged here.

Performance findings, strongest first:

- Planning dominates latency, not execution. OSWorld-Human (arXiv 2506.16042v2, MLSys 2026, MEASURED): planning over 50%, sometimes near 75%, of task latency; reflection/judging next at 22.5-33.6%; best agents take 2.7-4.3x more steps than necessary.
- Batching works. Hybrid Computer Use (arXiv 2610.41432, Oct 2026, MEASURED): batches actions per call, returns AX diffs instead of full screenshots, top OSWorld 2.0 scores (72.37% Partial with GPT-6 Astra). Qwen-UI-Agent (2026-07-31): over 40% of action outputs batched, 58.4% and 21.7% fewer steps per task than baselines. LLMCompiler-style DAG scheduling (ICML 2024, via Zylos 2026-04-26): 1.8x latency reduction on HotpotQA, up to 3.7x on parallelizable workflows, up to 6x cost reduction from fewer LLM calls.
- The harness can cost 3x on identical weights. PureTensor live bake-off (2026-09-26, MEASURED, 39 live tasks): same Qwen3.8-27B at 12.7s median in a lean loop vs 38.2s in browser-use with vision. Olliebot head-to-head (secondhand): DOM-based agent 15s vs Gemini Computer Use 75s, about 0.8s per screenshot for encoding alone.
- Observe with the tree, verify with the screenshot. MobiBench (2026-10-21, MEASURED, 508 tasks, Android mobile): GPT-4.1 task success 27.17% on accessibility tree, 4.72% on raw screenshot, 31.50% hybrid. Transfer to desktop Zen is assumed, not shown. SyndiPath (2026-11-08, vendor blog, multipliers UNVERIFIED): pruned ARIA snapshot about 320 tokens vs 2,400+ for full-HD vision, 0.4-0.9s vs 2.8-5.5s per action.
- Reliability collapses with step count. Mittal (about 2026-09, MEASURED, n=10,664 trajectories): every model tested falls from near-perfect to near zero within 16 steps. Context rot (Xia et al., 2026-10-27): models give up long before the window fills, and bounding context steepens decay rather than easing it. A 12-call loop is already in the degradation zone.
- Code execution is the biggest single latency win. OpenBot research notes (updated 2026-09-16): one code call replacing N screenshot-to-click round trips.

Structure findings:

- Keep the coordinator. Anthropic "Worse Together" (2026-11-11, MEASURED, 77 scenarios, simulated environments): one coordinator beat peer-to-peer agent teams in 4 of 4 environments by 10-45 points; peer teams reached only 47%/38% of coordinator performance in the shared-budget environment, and agents stalled as teams grew.
- Parallelism yields little. Stackness (2026-11-11, MEASURED, 364 runs, single repo and developer): effective parallelism 1.21 overall, 1.46 busiest window, 1.82 best case. A 2,124-run benchmark (circa 2026-11-20, read via news summary only): sub-agents dropped Claude Code solve rate from 83% to 59% while tokens rose 1.41-3.31x. Nosov (2026-11-07, 288 runs): sub-agents cost 74-221% extra for read/search work with no recall gain.
- Give every worker the original brief, never a summary. Swarm-tax controlled trial (2026-10-26, 144 runs, coding tasks): planner-coder-reviewer team passed 25.7% of hidden tests vs 56.8% for one agent, recovering to 54.1% only when every agent read the task file. Reviewer approvals were wrong 24 of 24 times.
- Handoffs lose state through repeated compression. Handoff-loss paper (about 2026-11-17, read via summary only): rewriting handoff notes from full history instead of the previous summary recovers 70-82% of lost learning. Madani field study (14 production deployments, small self-selected sample): 12 of 14 rolled back or abandoned (86%, a warning flag not a base rate); adding handoff structure added 1.4x-2.8x tokens.
- Verification is the hidden cost, and people misjudge speed. METR RCT (16 devs, 246 issues, July 2025): tasks took 19% longer with AI while devs felt 20% faster (CI plus 2% to plus 39%). AWS VCR framing (2026-05-29, anecdotal, three deployments): when verification time exceeds production time, human review is theater. A 50-turn Claude Code session burns about 1M input vs 40K output tokens (25:1), input about 85% of cost, re-sent context about 62% of the bill (tokenade, secondhand, UNVERIFIED for the 62% figure).

Gaps the crawl could not close (stated plainly):

- No crawled source gives a measured think-vs-observe-vs-act split of wall time for a computer-use loop. Our 87.8% loop figure stands as INTERNAL only.
- No published A/B wall-time number exists for "one observation yields many actions" as a standalone intervention on a desktop GUI task. HCU and Qwen-UI-Agent are the closest evidence, via batching and step counts.
- No crawled source measures the batching experiment Council C designed at 44-run scale; the pilot in section 5 is how we close that gap on our own test cases.

## 3. Our current structure and its measured weak points

Current structure: Muse (coordinator/PM) on a VM directs Muse subagents (Workers, spawned per task), laptop agents via SSH (Codex Luna 6 Max, fcc-claude, agy via agy-hypr helper, opencode), and two Muse clones on their own machines contacted ONLY via GitHub repo coord/<name>.md, PR comments, issues. Generators never run their own tests; independent runners verify. Watchdog checks liveness every 15 min. Zen todolist 111/115 done and merged to main. Standing rules: quality over speed, no fabrication, small commits push as you go, full access, never push personal info to GitHub, no em/en dashes, never ydotool, kill stuck agents on first stall flag, realistic complex tests, time everything.

Measured weak points, all internal, all 2026-11-21 unless noted:

1. The loop is the cost. Hand-driven test t01 took about 7 min over 12 tool calls vs 2,678 ms machine time for the same scripted test (Worker P report). Ratio about 157x, n=1, hand-driven by an unnamed driver, variance unknown: a directional fact, not a precise ratio. The 10x review found the think-observe-think loop is 87.8% of task time, with no time-motion split ever measured. Every performance ranking in this proposal rests on these two numbers, and both are the most important unmeasured quantities we have.
2. Verification is bought twice. Clone1 finished batch 2+3 in about 20 min; quality was questioned; a full batch 4 council plus redteam re-verification was ordered. Accepting a weak first report cost a second full verification cycle. Worker P caught a false tick the same way: Worker A2 claimed 9 Phase 2.1 checkboxes ticked, commit b876ee1 never touched the todo file.
3. Generators ship broken fixtures. Worker P ran fcc-k tests: 0/10 PASS as specced, all fixture/spec defects, not Zen control. Worker S then fixed all 10; Worker U re-ran them live: 10/10 PASS in 28,613 ms. The fix-then-rerun cycle is the system working, but the first 0/10 shows generators are not checked before their output is believed.
4. Silent deaths waste the most time. fcc K2 died twice with zero output and an empty directory; the retry log only says it is drafting. agy Q2 timed out at the 10-min helper limit at 4/10 tests. Clone2 stalled 70+ min with no commits after a new batch. Coordinator #2 was flagged STALL at 04:14 and killed at 04:36, 50 min after silence. The watchdog works; the kill was late because the first flag was not acted on. (Standing rule now: kill on the FIRST stall flag.)
5. Speed claims outrun evidence. Pick 1 measured wall minus 53% (37.54s to 17.59s), think minus 56%, calls 5 to 2, 4/4 SUCCESS (a1-code-exec-dom-design.md, 2026-11-19). The same design file warns for its sibling measurement D1: "n=1 per arm, do not quote a precise speedup factor." Pick 1 is the best number available, not a solid number. DOM read 3-5ms vs screenshot seconds is a 100x read gap, not a wall-time win: reading state is the smallest slice of a loop where think is 87.8%.
6. Parallelism bought questioned quality. Clone1 batch 2+3 in about 20 min is real speed, but the fault may be the missing acceptance gate between batches, not the parallelism itself. The two batches were combined and the next work started before verification.
7. Handoff loss is real but unmeasured here. No resume-without-re-asking rate is tracked. The 70-82% recovery figure and the 28.5-point swarm-tax gain come from coding tasks and summary-read papers; transfer to our GUI tasks and clone coord files is assumed, not shown.

## 4. The debate: what the council proposed, what the redteam killed

Council A (performance, improvements/worker-w-council-a-performance-20261121.md, commit 5b25b2f): batch actions per observation inside code-exec programs; DOM/ARIA-first observation; code-exec/CLI replacing deterministic GUI steps; faster coordinate grounding; cut tool calls per task; plus a do-NOT list.
Council B (structure, improvements/worker-w-council-b-structure-20261121.md, commit 1c11606): P1 original-brief-only spawning; P2 full-history handoffs; P3 verification evidence contract; P4 generator-runner separation; P5 two-lane spawn cap; P6 progress-based kill rules; P7 clone management; P8 coordinator guards; P9 register plus tools plus skills.
Council C (measurement, improvements/worker-w-council-c-measurement-20261121.md, commit 5bff650): Exp1 batching (44 runs, 30% bar, four go conditions); Exp2 tree-first (20% bar); Exp3 code-exec substitution (25% bar, four conditions); six metrics plus run-log JSONL schema; pre-registration and anti-self-deception rules; fixtures first, then sequential experiments.
Redteam (improvements/worker-w-redteam-20261121.md, commit f09fb8e): attacked every proposal, cross-checked load-bearing numbers against primary sources, listed 10 contradictions between councils and standing rules.

Redteam verdicts (KILL means do not adopt as specified, not proven false by experiment):

- KILLED: A4 coordinate cache (circular invalidation, undefined desktop element identity, 90s expiry on minutes-long tasks); B P9 register, weekly review, four tools and three skills (restates P1-P8, no owner or budget, contradicts the Madani finding it cites); C Exp3 as designed (four simultaneous go conditions, wrong qualifying cases, unenforceable fabrication boundary).
- WEAKENED (narrowed scope): A1 (Pick 1 pattern only, deterministic short tasks, fixture frozen into repo first); A2 (opt-in per task type, after single-session ownership is built, read-time win is not a wall-time win); A3 (guideline not gate, increment over A1 small and unmeasured); A5 (cheap parts only, token claims UNVERIFIED); B P1 (template hygiene, 28.5-point gain does not transfer); B P2 (full-history rewrites only at real boundaries); B P4 (landed changes only, runner counts against the lane cap); B P6 (progress markers yes, invented 60/30/20 timeouts no, measure p95 first); B P7 (keep the acceptance gate, drop the one-batch ban); B P8 (checklist lines, not blocking gates); C Exp1 (pilot first, not 44 runs; it tests model-turn batching while A1 is code-exec batching); C Exp2 (smaller set, fresh runner, only if Exp1 goes GO); C order of work (fixtures-first yes, strict sequential gating no).
- SURVIVED: B P3 verification evidence contract (strongest structural proposal); B P5 two-lane spawn cap (strongest multi-source case); C six metrics plus schema (tokens downgraded to best-effort, VCR as a flag); C pre-registration and anti-self-deception rules; A6 negatives except the handoff-structure line, which contradicts B P2/P3/P9.

The 10 contradictions, resolved in section 5 (not left for the implementer to guess):

1. Two "single first experiments" (A: Pick 4 fixture, code-exec batching; C: 44 fcc-k runs, model-turn batching). Resolved: ONE first experiment, the A1 narrow pilot (section 5.1). Exp1's model-turn batching becomes a separate named experiment run after the pilot, only if the pilot goes GO.
2. Handoff structure yes or no (A6 bans it, B P2/P3/P9 add it). Resolved: plain-text templates are allowed; JSON-schema validations are not. Madani warns against schema validation overhead, not against a plain-text template.
3. Runner consumes the lane cap (P4 adds a runner, P5 caps at two lanes). Resolved: the runner counts against the cap explicitly; separation applies to landed changes only, so most tasks still have one free lane.
4. Verification cost vs theater threshold (P3 plus P4 can push VCR above 1.0 on small tasks). Resolved: small tasks are exempt from the separate-runner leg; VCR is a flag ("verification cost exceeded production cost, explain why"), not an automatic theater verdict.
5. Context: cut it or read it all (A5 cuts, B P2 and C read the full record). Resolved: cut WORKER context (diffs, file references, short reports); keep COORDINATOR handoffs full. The line is drawn here, in writing.
6. Kill on first flag vs quality over speed (P6 invented timeouts can kill a productive agent on a legitimate 40-min step). Resolved: progress markers with a tightened definition; no invented timeout numbers; measure p95 first; watchdog flags about the coordinator go to Muse directly, never to the coordinator being flagged.
7. Who owns the observation rule (B P9a states it, A owns the technical form). Resolved: Council A owns it. B drops it from the register, which is killed anyway.
8. Selection bias (C Exp1 excludes 6 of 10 fcc-k cases; A Exp1 uses one synthetic fixture). Resolved: the pilot uses f01, a hard case with 70 scripted steps, plus the Pick 4 fixture; excluded cases are reported plainly, not hidden.
9. Summary ban vs coordinator-authored handoffs (P1 bans coordinator summaries; P2 requires the coordinator to write clone handoffs). Resolved: the ban applies to SPAWN briefs (workers get the original brief file); clone handoffs are coordinator-written from the full record in plain text, because the coord file IS the clone's only source.
10. Sequential experiments vs the owner priority (C: no experiment starts until the previous go/no-go). Resolved: fixtures-first for the cases in the experiment, but the fixture fix and the pilot run in parallel on disjoint cases; Exp2 design work may happen during Exp1 runs. No experiment's RUNS start until the previous experiment's cases and thresholds are frozen.

## 5. The proposed new structure

### 5.1 Roles (what changes: almost nothing about who, everything about how each role proves its work)

- Muse, coordinator/PM: unchanged as the single coordinator. Keeps the repo-mediated shape (workers never talk directly; Anthropic coordinator beat peer teams 4 of 4). New duties: name the original brief file in every spawn; check for the evidence attachment BEFORE reading any report (fast reject); count the runner against the lane cap; write clone handoffs from the full record in plain text.
- Muse subagents (Workers): unchanged shape, spawned per task. New duties: read the original brief file in full, never a coordinator summary; attach verification evidence to every done report; log progress markers (a step, artifact, test run, or decision that names the next concrete step and its evidence).
- Laptop agents (Codex, fcc, agy, opencode): unchanged channels. New duty: same evidence contract on every done report; same progress markers so the watchdog can kill on stall, not on silence.
- Clones (clone1, clone2): unchanged channel (repo only, coord/<name>.md, PR comments, issues). New rules: acceptance gate between batches on the same workstream; parallel batches allowed on disjoint workstreams with separate runners; one stall clock (15-min progress marker); no second nudge (kill/stop note, wait for ack or timeout, reassign).
- Independent runner: NEW as a formal role, not a new person. Any worker can be the runner for another worker's change, but never for its own. The runner's evidence is the only evidence that counts for a landed change.

### 5.2 Handoff rules

- Every spawn names ONE original brief file the worker must read in full. If the task has no written original brief, the coordinator writes one first, except ad-hoc tasks under a size threshold (coordinator judgment, stated in the spawn).
- Handoffs use a fixed six-part plain-text template (task, original brief, what was done, evidence, what is still open, exact error text). No JSON-schema validation on handoffs.
- Full-history rewrites (rewritten from the brief, logs, test outputs, exact error text, never compressed from the previous note) happen ONLY at real boundaries: day boundary, clone batch boundary, agent replacement after a kill. Every other transfer uses the template filled from the last note.
- Clone handoffs are coordinator-written from the full record. The P1 summary ban does not apply here because the coord file is the clone's only source.

### 5.3 Verification rules (the evidence contract, B P3, the strongest surviving proposal)

- No report counts as done without runnable evidence: exact test command plus output/log, commit hash; timed run log plus end-state screenshot or video for machine tasks; source plus access date per research claim.
- A bare "done" is returned unread. Fast reject: the coordinator checks for the evidence attachment first, before reading the report.
- The generator never runs its own tests. Only a different agent's runner evidence counts, for landed changes (code merged, machine state changed, contest-affecting work). Small tasks are exempt from the separate-runner leg, but still attach their own evidence.
- An agent reviewer's approval is explicitly NOT evidence. Independent acceptance tests and the owner's check are the gates.
- VCR is a flag, not a rule: if verification cost exceeded production cost, the report says why. Safety-critical verification (contest upload with a deadline, a package error that blocks a contest) may cost as much as production.
- Lauren Tan rule, adopted verbatim as the standard: done means nothing without runnable verification evidence.

### 5.4 Spawn and kill rules

- Default spawn cap: TWO concurrent lanes, disjoint files only, sequential as the default. The runner counts as a lane. A third lane needs all three, checkable: disjoint files, its own test slot, and a NAMED DELIVERABLE FILE (not a sentence) that neither other lane delivers.
- Kill on no progress marker for 15 min. Progress means a step, artifact, test run, or decision logged; a decision counts only if it names the next concrete step and its evidence; a heartbeat alone does not count. Kill on the FIRST stall flag, per standing rule.
- Watchdog polls every 5 min as a separate process and reports to Muse directly, never to a sub-coordinator. A flag about the coordinator goes to Muse directly, not to the coordinator being flagged.
- No invented hard timeouts. Measure p95 completion time per task type on the next 10 tasks first, then set timeouts from those numbers with margin. Until then, timeouts are a coordinator judgment call, not a number in the brief.
- One kill record line per kill (worker, last progress marker, wall time, cause). If the same cause kills twice, the task is re-scoped, not the worker re-blamed.

### 5.5 Performance rules (the loop is the product)

- Batch actions per observation inside code-exec programs, on deterministic short tasks first (A1 narrow form, section 5.1 experiment). One model call writes one program that observes, acts, branches, retries, and asserts locally with zero model round trips in between. Cap program length in the brief; test the preflight guarantee deliberately with a bad ref mid-list across every action type used; publish which types are preflight-safe.
- DOM/ARIA-first observation is OPT-IN per task type (form fill, navigation, state reads), after single-session ownership is built and tested. Screenshot stays the default for hover-dependent, canvas, and animated-glass tasks. Final verification screenshot is mandatory. Real mouse for clicks (BiDi click reported ok but fired nothing). One Zen session owned by scripts/zen_dom.py.
- Code-exec and CLI replace GUI steps as a GUIDELINE, not a gate: prefer code/CLI, note the GUI steps kept and why, in one line. The runner checks the program does not touch fixture internals to set the end state directly; reaching into fixture internals is fabrication of a pass.
- Coordinate grounding: use DOM rects where they exist, folded into the DOM-first rule. NO coordinate cache until the invalidation circularity is solved and element identity is defined. Do not chase grounding accuracy past about 92%.
- Cut tool calls with the cheap parts only: diff-only observations, short structured reports, file-referenced plans. No blind context compaction (bounding context steepens reliability decay), no token-multiplier claims until measured on our own sessions.
- What NOT to do: do not add more parallel workers to go faster (measured 1.21-1.82x effective parallelism, solve rate 83% to 59%); do not let workers talk peer-to-peer (coordinator beat peer teams 4 of 4); do not trust an agent reviewer's approval as a quality gate (24 of 24 approvals failed hidden tests); do not add JSON-schema validations to handoffs.

### 5.6 Deterministic rules, tools, skills (Lauren Tan, applied narrowly)

- One-line principle, kept as a sentence inside the spawn-brief template: "twice means a rule, and the rule lives in a lint, a test, or a template." No register, no weekly review, no program of tools and skills. The register apparatus is KILLED.
- At most one tool may be proposed later (the evidence packager, which directly serves the evidence contract), with a named builder and a time budget. Nothing else is built until the evidence contract has run for two weeks.
- Repeated operations become tools and repeated approaches become skills only when the item has repeated at least twice AND the conversion has a named owner and a time budget.

### 5.7 Metrics on every run (Council C, with redteam downgrades)

Six metrics, computed by script from a run-log JSONL schema, on every run from now on:

1. Wall time per task, the headline, timed by the runner, never self-reported.
2. Tool calls per task, counted from the transcript.
3. Tokens per task, input and output separately, BEST-EFFORT: if the session does not expose a per-task token count, report UNMEASURED, never estimated.
4. Observation cost per observation by type, once the harness logs it. Until the logger is built, this metric is aspirational, not required.
5. Verification cost, shown as a VCR flag (verification cost divided by production cost, with an explanation when it exceeds 1.0), not an automatic theater verdict.
6. Stall minutes, defined as wall time minus time covered by progress markers, with a worked example so two runners compute the same number.

Plus per run: pass/fail by DOM checker, recovery steps, refusals, misclicks, session deaths, retries. A win on wall with a rise in refusals or deaths is not a win.

Anti-self-deception rules: pre-register thresholds before runs; allow a pilot phase with movable thresholds, then the bar freezes for confirmatory runs; freeze cases before the first run; report ALL runs including failures, timeouts, and kills; independent runner verifies; handoffs written from the full run log, not the previous summary; record one secondary metric per experiment (coordinator review minutes) so wall-time-only claims do not discard the coordinator cost.

## 6. What to try first (the single most valuable first step)

FIRST STEP: the A1 narrow pilot. Batch actions per observation inside code-exec programs, on deterministic short tasks only, with the Pick 4 fixture frozen into the repo first.

- Why this first: it is the only proposal with our own measured win (Pick 1: wall minus 53%, 37.54s to 17.59s, think minus 56%, calls 5 to 2, 4/4 SUCCESS), zero new infrastructure, zero new workers, and it directly attacks the loop that is 87.8% of task time. The evidence contract (section 5.3) is applied to the pilot itself, so the pilot cannot produce another questioned fast result.
- Exact pilot: freeze the Pick 4 fixture into the repo (not /tmp); code-exec program vs step-by-step loop, n=3 per arm, alternating arms, checker blinded to method; then one held-out realistic task by an independent runner. Cap program length in the brief; test the preflight guarantee with a bad ref mid-list across every action type used.
- GO only if: median wall time down at least 30% per case AND pass rate equal or better AND recovery steps not higher. The actions-per-observation figure is reported as a diagnostic, not a gate. Any one failing is NO-GO.
- If the pilot goes GO: run Council C Exp1 as the confirmatory run (model-turn batching as its own named experiment, pilot-sized set first, not 44 runs), then Exp2 (tree-first, smaller set, fresh runner, only if Exp1 goes GO). If the pilot goes NO-GO: stop, report plainly, and do not proceed to Exp1/Exp2 on the same lever.
- What runs in parallel with the pilot: the fixture fix for the experiment cases (f01, f03, f04, f09) on disjoint cases, time-boxed with a named budget; Exp2 design work may happen during pilot runs. No experiment's RUNS start until the previous experiment's cases and thresholds are frozen.

SECOND (same week, no build): adopt the evidence contract (section 5.3) and the two-lane cap (section 5.4) immediately. Both cost nothing to implement; the contract attacks the documented clone1 re-verification failure, and the cap costs only a refusal to spawn.

THIRD (after the pilot): DOM-first as opt-in per task type, once single-session ownership is built and tested. Not before.

## 7. What NOT to change

- The coordinator model. One coordinator, repo-mediated workers, no peer-to-peer agent chat. Anthropic coordinator beat peer teams 4 of 4 by 10-45 points.
- The clone channel. Repo only (coord files, PR comments, issues). The user never messages clones again after the startup prompt.
- Generators never run their own tests. Strengthened by the evidence contract, not changed.
- The watchdog. 15-min check cadence stays; refined to a 5-min poll as a separate process reporting to Muse directly.
- Quality over speed. The standing rule stands; the kill-on-first-flag rule stands with it, reconciled by tightened progress markers instead of invented timeouts.
- Realistic complex tests (15-40 steps), timed and logged. The test loop is the measurement instrument for the whole redesign.
- No personal info on GitHub, no em/en dashes, never ydotool, small commits push as you go, full access.
- The final test plan (independent Codeforces contest, 5 problems, run LAST) is untouched by this proposal.

## 8. What was killed, and why (so nobody revives it quietly)

- A4 coordinate cache. Circular invalidation, undefined desktop element identity, 90s expiry on minutes-long tasks.
- B P9 register, weekly review, four tools, three skills. Restates P1-P8, no owner or budget, contradicts the Madani finding it cites.
- C Exp3 as designed. Four simultaneous go conditions, wrong qualifying cases, unenforceable fabrication boundary. Fold the question into Exp1/Exp2 reporting (substitutable-step share and wall time vs the scripted floor).
- Hard timeouts at 60/30/20 min. Invented numbers with no p95 data. Measure first.
- B P4 on every task. One extra spawn per task contradicts the P5 cap. Landed changes only.
- C Exp1 at full 44-run scale before a pilot. Run the pilot first.
- Blanket one-batch ban on clones. The gate fixes the documented failure; the ban throws away working parallelism.
- JSON-schema validations on handoffs. Plain-text templates only.

## 9. Honest gaps (what this proposal does not know)

- The 87.8% loop share has no time-motion confirmation. No crawled source gives a think-vs-observe-vs-act split. The pilot plus the six metrics are designed to measure it, but until then every ranking here assumes the split is correct. If the true split is, say, 50% think and 30% observe, the ranking of levers changes.
- The 157x ratio (t01, 7 min vs 2,678 ms) is n=1, single test, variance unknown. It is a directional fact, not a precise ratio.
- Pick 1 minus 53% is real but small-n, one task shape, one rerun set. The design file itself warns not to quote a precise speedup factor for the sibling measurement.
- No published A/B exists for one-observation-many-actions as a standalone intervention on a desktop GUI task. The pilot is the way to close that gap on our own test cases.
- The transfer audit (redteam section 5) applies to every crawled number used here: swarm-tax, Anthropic, Stackness, the 2,124-run benchmark, Mittal, MobiBench, SyndiPath, tokenade, handoff 70-82%, Madani, METR, Lauren Tan. Each is labeled with its scope limit in the crawl files; none is quoted here beyond what its scope supports.

## Sources

Internal (repo, accessed 2026-11-21):

- improvements/worker-w-crawl-clip-20261121.md (commit c1cc7d8): Lauren Tan talk identification, transcript, cross-checks.
- improvements/worker-w-crawl-structures-20261121.md (commit 4b715b8): 13 sources.
- improvements/worker-w-crawl-bottlenecks-20261121.md (commits 5c22bd4, 539a405): 15 sources.
- improvements/worker-w-council-a-performance-20261121.md (commit 5b25b2f).
- improvements/worker-w-council-b-structure-20261121.md (commit 1c11606).
- improvements/worker-w-council-c-measurement-20261121.md (commit 5bff650).
- improvements/worker-w-redteam-20261121.md (commit f09fb8e).
- improvements/a1-code-exec-dom-design.md (2026-11-19): Pick 1 numbers, D1, program budgets, preflight design.
- docs/zen-dom-control-comparison.md (21/11/2026): zen-mcp DOM read 3-5ms, vision grounding 17/29 = 58.6%, BiDi false-ok click, single session per Zen.
- tests/realistic/RUN-REPORT-20261121.md (2026-11-21): fcc-k fixture defects, f01 spec bug, self-simulating checkers.
- Task briefs and run reports, 2026-11-21: t01 7 min vs 2,678 ms; 87.8% loop share; clone1 10/10 in 59.1s; agy-q 4/5 in 20.5s; fcc-k fixed 10/10 in 28.6s; full suite 1,523 tests 0 failures in 119.9s; fcc K2 died twice; agy Q2 timed out at 10 min at 4/10; clone2 stalled 70+ min; coordinator #2 flagged 04:14 killed 04:36; clone1 batch 2+3 in about 20 min, quality questioned.

Crawled (primary links in the crawl files, all accessed 2026-11-21):

- OSWorld-Human, arXiv 2506.16042v2. Hybrid Computer Use, arXiv 2610.41432. Qwen-UI-Agent technical report, 2026-07-31. PureTensor PT-R-2026-028, 2026-09-26. MobiBench, arXiv:2512.12634, 2026-10-21. Mittal, "How Fast Do Agents Rot?", about 2026-09. Xia et al., "Diagnosing and Mitigating Context Rot", 2026-10-27. Anthropic "Worse Together", 2026-11-11. Swarm-tax experiment, 2026-10-26. Stackness, 2026-11-11. Nosov, 2026-11-07. 2,124-run sub-agent benchmark, circa 2026-11-20 (news summary). METR RCT, July 2025, re-analysis Oct 2026. Madani Agency field study, Jan 2025-Apr 2026. AWS Builder VCR, 2026-05-29. Handoff-loss paper via zicq.com summary, about 2026-11-17. Anchan and Sen, arXiv:2610.06069, Oct 2026. SyndiPath, 2026-11-08 (vendor blog, UNVERIFIED multipliers). tokenade.net, about 2026-10-16 (secondhand, UNVERIFIED). Zylos / LLMCompiler, 2026-04-26. OpenBot research notes, updated 2026-09-16. Lauren Tan talk, AI Engineer Code Summit, 14 Nov 2026 (via clip crawl).
