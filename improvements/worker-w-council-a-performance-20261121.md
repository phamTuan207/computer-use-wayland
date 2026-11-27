# Worker W Council A: performance position paper

- Role: Worker W-Council-A, performance councillor, Worker W structure team
- Date: 2026-11-21
- Repo: computer-use-wayland, branch todolist-push
- Sources accessed: 2026-11-21. Every external claim below carries its source and access date. Unknown = UNVERIFIED.
- Owner priority applied: performance when Muses control the user's machine comes first. Super I input work is out of scope and ignored here.

## Work log (Asia/Ho_Chi_Minh, wall clock plus elapsed)

- 17:51, T+0min: task received from Worker W (parent coordinator).
- 17:52-17:58, T+1-7min: read all three crawl files (clip, structures, bottlenecks) and the A1 code-exec design plus the Zen DOM control comparison.
- 17:58-18:10, T+7-19min: wrote this paper, committed, pushed.

## 0. The baseline we are optimizing against (INTERNAL, our own measurements)

These numbers come from the task brief and the crawl files, all dated 2026-11-21:

- Hand-driven test t01: about 7 min over 12 tool calls. The same test scripted: 2,678 ms machine time. Ratio about 157x. The machine work is negligible. The loop is the cost.
- Think-observe-think loop: 87.8% of task time (10x review, internal).
- Pick 1 code-exec rerun 19/11: 4/4 SUCCESS, mean wall 37.54s to 17.59s (minus 53%), think minus 56%, model calls 5 to 2 (improvements/a1-code-exec-dom-design.md).
- DOM-first D1: core think 99.2s to 20.7s, n=1 per arm (same file).
- Full suite: 1,523 tests, 0 failures, in 119.9s (task brief, internal).
- Clone1 tests 10/10 in 59.1s; agy-q 4/5 in 20.5s; fcc-k fixed 10/10 in 28.6s (task brief, internal).
- Failure modes that cost wall time without producing progress: fcc K2 died twice with zero output; agy Q2 first run timed out at 10 min at 4/10 tests; clone2 stalled 70+ min once; coordinator #2 stall flagged 04:14, killed 04:36 (50 min after silence) (task brief, internal).

Implication, stated plainly: a faster model or a faster click moves almost nothing. The 87.8% loop share means the only levers that matter are fewer loop iterations, cheaper observations per iteration, and more actions per iteration. Every proposal below is scored against that baseline, and every expected effect is either our own measured number or a crawled number with its source. Where the crawl gives no number, the proposal says so and the verification experiment supplies it.

## 1. TRY THIS FIRST: batch actions per observation inside code-exec programs

### What changes

Generalize the proven Pick 1 pattern to every multi-step task, using the A1 design that already exists in this repo (improvements/a1-code-exec-dom-design.md, 2026-11-19). One model call writes one program. The program does observe, act, branch, retry, and assert locally, with zero model round trips in between. Concretely:

- The program issues one `act()` call carrying a list of actions (type, click, key, wait) instead of one action per model turn. The interpreter already supports action lists; the A1 design extends this to DOM with `dom_act(snapshot, actions)` taking 1 to 32 action dicts in one call.
- Retries and second looks move inside the program: `if not clicked["ok"]: re-observe and retry once`, exactly as section 4 of the A1 design shows. A retry costs 0 model calls.
- The `after` snapshot returned by `dom_act` is bound automatically, so the program chains without re-observing. No fresh observation between act and assert.

Why this is first: it is the only proposal that is already proven in our own repo, on our own test loop, with zero new infrastructure. Pick 1 measured it. A1 is designed, not speculative. Everything else below needs new measurement before it can be trusted; this one needs only a rerun.

### Expected wall-time effect

- Our own measurement: Pick 1 rerun, wall minus 53% (37.54s to 17.59s), think minus 56%, calls 5 to 2 (A1 design, 2026-11-19, internal). That is the number to beat or match on new tasks, not a promise for every task.
- Crawled support, same direction: Qwen-UI-Agent batched more than 40% of action outputs and needed 58.4% fewer steps per task than MiniMax M3 and 21.7% fewer than Qwen 3.7 Plus (structures crawl A3, source dated 2026-07-31, accessed 2026-11-21). HCU (Hybrid Computer Use, arXiv 2610.41432v1, Oct 2026, accessed 2026-11-21) batches actions per call and reports AX diffs, reaching the highest OSWorld 2.0 scores among compared systems (structures crawl A2). LLMCompiler-style DAG scheduling measured 1.8x latency reduction on HotpotQA and up to 3.7x on parallelizable workflows (bottlenecks crawl A2, Source 6, Zylos 2026-04-26, accessed 2026-11-21; the 1.8x/3.7x figures are from the original ICML 2024 paper, not re-measured in 2026).
- Honest bound: batching helps only where actions are independent or sequenced deterministically inside the program. A task that genuinely needs the model to judge an intermediate screen still pays one observation per judgment. Expect the Pick 1 shape (about half the wall, about half the calls) on deterministic multi-step tasks, and near zero on judgment-heavy tasks. The experiment in the verification section measures which tasks are which.

### How to verify it in one experiment

- Arms, same fixture, same timed wrapper: (a) current step-by-step loop on the Pick 4 fixture (`tests/` fixture used by D1, `file:///tmp/speed-pick4-20261118/pick4-fixture.html`); (b) one code-exec program doing DOM observe plus click-by-ref plus DOM assert with no screenshots, per the A1 design section 3 program. n=3 runs per arm, broker SOLO, relay with `CU_CODE_EXEC=1` and `CU_PICK4_FASTPATH=1`.
- Report per run: wall (headline), think total, think-before-code-exec, in-program elapsed, model calls, refusals, misclicks, session deaths, program retries. Success bar (the Pick 1 re-measure bar): fewer calls AND lower wall than arm (a), with no rise in refusals, misclicks, or deaths.
- Then repeat on one HELD-OUT realistic task from `tests/realistic/` that the program author has never seen, run by an independent runner (generators never run their own tests, per standing rule). If the held-out task does not also improve, the proposal is fixture-specific and the paper says so.

### What breaks if it is wrong

- A bad batch fails as a unit: if the interpreter or adapter validates the whole batch before any effect (A1 design section 7 states the adapter preflight does this), a preflight failure has `completed: 0` and the program re-observes and retries cleanly. If that preflight guarantee is wrong for some action type, a partial batch could leave the app in a half-done state (for example typed text with no Enter, or a clicked toggle with no confirm). Guard: the verification experiment must include one deliberately failing batch (bad ref mid-list) and check the app state after it. If partial effects are observed, batching is restricted to preflight-safe action types only.
- Program-composition think grows with program length. The A1 design already flags this: P3/P4 think-before-code-exec was about 18s vs P2 8.59s. If think-before-code-exec eats the whole saving on longer programs, the net effect is zero or negative, and the experiment must report it rather than hide it behind the wall-time headline.
- A program that loops forever inside one call burns the wall budget silently. Guard already in the design: trace budget, API-call budget (32), wall-clock budget (default 30s, max 60s). Do not raise these budgets to make a slow program pass.

## 2. DOM/ARIA-first observation, screenshot only for verification and recovery

### What changes

Flip the default observation channel. Today the loop observes by screenshot every iteration. Change it to:

- Observe with a structured tree first: DOM/ARIA snapshot on web (zen-mcp for live Zen, `scripts/cdp.mjs` for Chromium), accessibility tree on desktop where available. Text only, no image.
- Take a screenshot only at two moments: final verification (the existing final-observation-image rule stays), and recovery (the tree disagrees with expected state, or a pointer-miss / screen-changed refusal arrives).
- Return diffs, not full snapshots, on repeat observations: only elements that changed since the last snapshot (the HCU AX-diff pattern, structures crawl A2). A repeat observe that returns the same 80 elements is pure waste.

Our repo already has the pieces: zen-mcp 1.2.3 reads DOM in 3-5ms and clicks in 2-3ms on the live Zen (docs/zen-dom-control-comparison.md, measured live 21/11/2026); `dom_observe` with `max_elements=80` and scoped observe exists in the A1 design; `scripts/cdp.mjs` already does snapshot binding and expiry. What is missing is the DEFAULT: the loop still reaches for the screenshot first.

### Expected wall-time effect

- Our own measurement: DOM read 3-14ms (zen-mcp 3-5ms, Selenium read 14ms) vs screenshot plus vision observe measured in seconds, with the observe round trip the dominant cost (docs/zen-dom-control-comparison.md section 8, 21/11/2026). DOM is 100x+ faster for reading state, in our own numbers.
- Crawled support: SyndiPath (2026-11-08, accessed 2026-11-21) claims a pruned ARIA snapshot is about 320 tokens vs a full-HD PNG vision loop at about 2,400+ tokens (7.5x cheaper) and 0.4-0.9s per action vs 2.8-5.5s for vision (about 4x faster end to end). Treat the exact multipliers as UNVERIFIED: vendor blog, no independent replication found in the crawl. The direction matches every other source.
- PureTensor bake-off (2026-09-26, accessed 2026-11-21, MEASURED, 39 live tasks): the same Qwen3.8-27B weights scored 37/39 at median 38.2s in browser-use with vision on vs 38/39 at median 12.7s in a lean screenshot loop, 3.0x slower in the heavier harness (bottlenecks crawl A1, Source 9).
- MobiBench (2026-10-21, accessed 2026-11-21, MEASURED, 508 tasks): GPT-4.1 task success 27.17% reading an accessibility tree as text, 4.72% reading a raw screenshot only, 31.50% hybrid (bottlenecks crawl A3, Source 11). Tree beats screenshot alone by a wide margin; hybrid beats both.
- Honest bound: the tree cannot see everything. The Polygon Browse button needs a real hover-then-click and its behavior depends on hover state (docs/zen-dom-control-comparison.md section 8; MEMORY.md 2026-11-20 correction). Canvas, custom-drawn controls, and animated glass (the pill) have no tree. Those tasks keep the screenshot path. The proposal is a default flip, not a ban.

### How to verify it in one experiment

- One realistic browser task from `tests/realistic/`, two arms, n=3 each: (a) screenshot-every-step loop; (b) DOM-observe loop with screenshot only at final verification. Same timed wrapper, same success criterion (verified end state, not a judge's opinion).
- Report per run: wall, model calls, input tokens per run (tree tokens vs image tokens), steps, and whether the final verification screenshot caught anything the tree missed. If arm (b) is not faster AND not less accurate, the default does not flip.
- Include one task the tree cannot do (hover-dependent control, per the Polygon lesson) as a negative control: arm (b) must fall back to screenshot plus real mouse and still pass, proving the fallback works instead of proving the tree is universal.

### What breaks if it is wrong

- Silent state mismatch: the tree says the button exists and is enabled; the pixels say it is covered by an overlay or off-viewport. The Zen windowed Marionette quirk is the live example: a tab can report correct rects while having a 0x0 viewport and `elementFromPoint` null everywhere (docs/zen-dom-control-comparison.md section 3). A tree-only loop would click into the void and report success. Guard: the final verification screenshot is mandatory, never skipped, and any click whose post-state does not change in the tree triggers an immediate screenshot recovery observe.
- DOM click is not a real mouse click: Puppeteer BiDi click took 971ms, reported ok, and the counter stayed 0 (same doc, section 4). Never trust a DOM/BiDi click to fire a handler. Rule, already in the doc: DOM for LOCATE and READ, real mouse for CLICK, and always verify the DOM changed after the click. If a future change drops that rule, this proposal's numbers stop applying.
- Session leak: live Zen allows ONE remote session total across BiDi and Marionette (same doc, section 7). A tree-first loop that opens a session per observe will hit "Maximum number of active sessions" and block everything. Guard: `scripts/zen_dom.py` owns the single session (file lock, session delete in finally, hung-client watchdog). No parallel remote-control workers on the live Zen, ever.

## 3. Code-exec and CLI replace GUI steps wherever the step is deterministic

### What changes

Extend the standing priority ladder (CLI first, then code-exec, then vision plus mouse) from a guideline into a gate: before any task runs as a vision loop, the brief must name the deterministic steps and say why each one cannot be code or CLI. The mechanisms already exist:

- Shell and file steps go through code-exec programs (`assert_file_contains`, typed shell acts inside one program call), not through typing into a terminal window one keystroke at a time.
- Browser navigation, form fill, and state reads go through zen-mcp or CDP (proposal 2), not through address-bar typing plus screenshots.
- Repeated multi-step operations become tools, per the Lauren Tan clip rule (crawl clip file, 2026-11-21): a repeated operation that stays a prompt is a repeated cost; bake it into a script or a skill the agent can call directly. The clip's own caveat applies: her 3,000 PRs/month depended on free Grok tokens at SpaceX, so do not quote her output as reproducible. The mechanism (repeated ops become tools) is what transfers, not the headline number.

### Expected wall-time effect

- Our own measurement: the same test took 2,678 ms scripted vs about 7 min hand-driven, ratio about 157x (bottlenecks crawl A5, INTERNAL). No crawled source gives a directly comparable scripted-vs-GUI-agent number, so this ratio is OURS, not a literature claim.
- Crawled support, per-step: UI-TARS Desktop writeup (about 2026-10-18, accessed 2026-11-21, secondhand table, numbers not independently verified) puts scripted selectors under 50 ms/step vs 800-2,500 ms/step for vision GUI agents, a 16x-50x per-step gap (bottlenecks crawl A1, Source 10). SyndiPath (same caveat as proposal 2) claims 0.4-0.9s vs 2.8-5.5s per action.
- Honest bound: 157x is the full-test ratio including all 12 think steps; the per-step machine gap is 16x-50x and the rest is loop overhead already counted in proposal 1. Do not add 157x and proposal 1's 53% together. They overlap: most of the 157x IS the loop that proposal 1 attacks. The incremental gain of proposal 3 over proposal 1 is the steps that become zero-model-call code instead of one-program-call code. Measure it as such.

### How to verify it in one experiment

- Take one realistic multi-step task that currently runs as a vision loop (for example a terminal-plus-browser task from `tests/realistic/`). Rewrite its deterministic steps as a code-exec program. Run both arms n=3, same timed wrapper, same verified end state.
- Report: wall, model calls, and a step table marking each step GUI vs code/CLI in each arm. The claim to test is narrow: steps converted to code cost near-zero model time. If the converted task is not faster, the conversion cost (program-composition think) exceeded the saving, and the task stays a vision loop.

### What breaks if it is wrong

- A scripted step that silently does the wrong thing is worse than a slow vision step that the model can see is wrong. A `fill` that sets a value without firing the input event leaves the app state unchanged while the script reports success. Guard: every code-exec step that changes app state ends with a DOM assert or a file assert inside the same program (the A1 design section 3 pattern). No assert, no claim of done.
- The sandbox is the boundary: code-exec runs under the existing allowlist (no imports, no dunders, no eval/exec/open, trace and wall budgets). Any proposal to widen the allowlist to make more steps scriptable needs its own review. This paper does not propose widening it.

## 4. Faster coordinate grounding: stop paying vision to find what the tree already knows

### What changes

Grounding (turning "the Show result button" into x,y) is currently a vision task on every step. Change it to a lookup task with vision as fallback:

- Primary: DOM rect from `getBoundingClientRect` via zen-mcp or CDP (exact, zero vision error). The existing `CU_PICK4_FASTPATH=1` flag already puts `rect`/`center` in snapshot elements; use it everywhere, not only in Pick 4.
- Desktop (non-browser): cache coordinates per window address for the duration of one task, keyed by element identity, and re-ground ONLY on a screen-changed or pointer-miss refusal. Today every step re-grounds from a fresh screenshot.
- Never re-ground what has not moved: if the observation diff (proposal 2) shows no change in the target element's rect, reuse the last coordinates.
- Keep the real mouse for the click itself (docs/zen-dom-control-comparison.md section 8): DOM rect plus real mouse click through the existing driver, verified exact to under 1px.

### Expected wall-time effect

- Our own measurement: vision grounding measured 17/29 = 58.6% on a known-point grid (Phase 2.1 E2, cited in docs/zen-dom-control-comparison.md section 8). DOM locate removes that entire miss class: exact rects, zero vision error. A miss costs a full extra loop iteration (observe, think, re-act), so every miss avoided saves one whole iteration, not just the grounding time.
- Crawled support for NOT chasing accuracy further: PureTensor (2026-09-26, MEASURED) found click accuracy separated the top three vision models by only 3 targets out of 72 (95.8%, 93.1%, 91.7%), yet the most accurate model finished last on live tasks (33/39), because most failures were errors of judgment and recovery, not missed pixels (bottlenecks crawl A3). Chasing grounding accuracy past about 92% buys little; loop design and recovery decide live-task success.
- Per-step floor: every screenshot adds about 0.8s of latency for image encoding alone (structures crawl A6, olliebot docs, secondhand attribution to Browser Use benchmarks, UNVERIFIED as a standalone claim). Removing one screenshot per step removes at least that floor plus the vision tokens.
- Honest bound: caching coordinates helps only when the UI is static between steps. Scrolling, animations (the pill), and layout shifts invalidate the cache. The invalidation rule (re-ground on any refusal or any diff touching the target rect) is what keeps the cache honest. A stale cache that is not invalidated produces confident wrong clicks, which are worse than slow right ones.

### How to verify it in one experiment

- Grid calibration task, same fixture as Phase 2.1 E2: two arms, n=1 run each is enough for accuracy (the grid is deterministic), n=3 for timing. Arm (a): vision grounding per step. Arm (b): DOM rect plus cached coordinates, re-ground only on refusal.
- Report: hit rate (correct first click / total targets), wall per target, and number of re-grounds in arm (b). Success bar: arm (b) hit rate at or above arm (a) with fewer observations. Also run one scrolling task as a negative control: the cache must invalidate and re-ground, not click the old position.

### What breaks if it is wrong

- Stale coordinates after an unobserved layout shift: the diff says nothing changed because the observation itself was skipped, so the cache looks valid while the button moved. Guard: cache lifetime is bounded by one task and by the 90s snapshot expiry already in cdp.mjs; any act that returns a changed layout, any scroll, and any window resize clears the cache for that window.
- The viewport trap: headless Chrome at 1280x800 reports a 1280x713 page, and a harness assuming 800 places every click about 12% too low (PureTensor, bottlenecks crawl A1, Source 9; a single viewport constant moved one setup from 17/26 to 23/26). DOM rects are in page coordinates; the click driver needs the same coordinate frame. Guard: the verification experiment must assert the coordinate frame on the actual window size before trusting any rect, and the 12% failure mode is a named check in the experiment report.

## 5. Cut tool calls per task: compact observations, no full history, short reports

### What changes

Tool-call count is the multiplier on everything: each call re-sends growing context and pays a full think step. Three cuts, all cheap to implement, none needing new models:

- Compact observations: diff-only snapshots (proposal 2) plus a cap on observation size (`max_elements=80` already exists in the A1 design; enforce it, do not let an unscoped observe return the whole page). Never send full image history: current screenshot plus short action history only (OpenBot research notes, structures crawl A4, citing OpenAI docs).
- Short worker reports: workers return a structured summary plus file paths, never a full transcript pasted into the coordinator context. This is the direct response to the re-sent-context finding: Claude Code regularly sends each background agent transcript back to its model (structures crawl A7, HN 2026-10-29, 591 points, reported not independently verified by the crawl author), and one measured run was 98% re-sent context out of 2.4B tokens (same section, claude-code issue 106025, 2026-10-29, MEASURED from session transcripts).
- Persist the plan outside context: the coordinator writes the plan to a repo file (coord files, BOARD.md already do this) and workers read the file instead of receiving the plan re-pasted in every brief. The swarm-tax experiment (structures crawl B2) is the evidence: every worker must read the ORIGINAL task file, never a coordinator summary, because summaries lose field names and edge cases (team pass rate 25.7% vs 56.8% for one agent, recovered to 54.1% only when every agent read the task file).

### Expected wall-time effect

- Crawled numbers, all secondhand or vendor-adjacent, so stated with their caveats: a typical 50-turn session burns about 1,000,000 input tokens and 40,000 output tokens, a 25:1 ratio, with input driving about 85% of session cost because the agent re-reads its whole context on every tool call, and re-sent context about 62% of the bill (tokenade.net, about 2026-10-16, accessed 2026-11-21; the 62% figure and the Uber budget figure in the same source are UNVERIFIED here; the 25:1 ratio and the re-read mechanism are consistent with the parallel-tool-calling sources) (bottlenecks crawl B4, Source 12).
- Our own numbers that bound the effect: 12 tool calls over 7 min in t01. Cutting calls from 12 to 4 (the Pick 1 shape, 5 to 2) removes 8 re-sends of the full context. The wall saving is the Pick 1 saving (proposal 1); this proposal's incremental contribution is the token and context-length saving, which matters for cost and for reliability (next paragraph), not only for wall time.
- Reliability effect, measured: task success falls from near-perfect to near zero within 16 steps on the agentic task (Mittal, about 2026-09, accessed 2026-11-21, MEASURED, n=10,664 trajectories; degradation driven by step count, not context length) (bottlenecks crawl A4, Source 15). A 12-call loop is already in the degradation zone. Shortening the loop is a reliability fix as well as a speed fix. Context rot (Xia et al., 2026-10-27, accessed 2026-11-21, MEASURED, four flagship models) shows models give up or answer wrong long before exhausting the window (same section, Source 13).

### How to verify it in one experiment

- Run one realistic task twice with identical instructions, once with full-history observations and pasted transcripts, once with diff-only observations and file-referenced reports. n=3 per arm. Report: model calls, input tokens per run (from the session transcript, not estimated), wall, and success. The hypothesis is directional (fewer tokens, same or better success), not a precise multiplier. Any precise multiplier quoted from this experiment needs n=3 agreement, not a single fast run.

### What breaks if it is wrong

- Compaction that drops state: bounding the context window steepened the reliability decay in the Mittal study (logit slope minus 0.69 vs minus 0.44), contradicting a lost-in-the-middle explanation (bottlenecks crawl A4). Cutting context aggressively can make the agent dumber, not faster. Guard: cut by STRUCTURE (diffs, file references, short reports), never by blind truncation. Handoff notes are rewritten from the full record, not from the previous summary: rewriting from the complete record recovers 70-82% of lost learning at the same 300-character budget (bottlenecks crawl B3, Source 16, measured experiment read via summary, so the 70-82% figure is reported, not independently verified).
- A short report that omits the one field the coordinator needs (a status code, an edge case) forces a re-read round trip that costs more than the saving. Guard: worker reports follow a fixed schema (task, result, verified end state, file paths, numbers with units, what failed). The swarm-tax finding is the reason the schema is fixed: free-form summaries lose field names.

## 6. What NOT to do (the crawl is clear, and it saves us from spending the budget here)

- Do NOT add more parallel workers to go faster. Measured effective parallelism is 1.21 overall, 1.46 in the busiest window, 1.82 in a six-agent 106-task run, about 0.3x the agent cap (Stackness, 2026-11-11, accessed 2026-11-21, MEASURED, 364 runs; structures crawl B5). Sub-agent concurrency dropped Claude Code solve rate from 83% to 59% and raised latency 17.5 to 27.8 min, with token inflation 1.41x-3.31x (2,124-run benchmark, read via news summary, structures crawl B3). For read/search work, sub-agents cost 2-3x for no recall gain (Nosov, 288 runs, 2026-11-07, structures crawl B4). Two lanes is the honest default; more lanes need separate test slots. This paper proposes zero new workers.
- Do NOT let workers talk peer-to-peer. Anthropic "Worse Together" (2026-11-11, accessed 2026-11-21, MEASURED, 77 scenarios): one coordinator beat peer-to-peer teams in 4 of 4 environments by 10-45 points, and peer teams stalled as they grew (structures crawl B1). Our repo-mediated shape (workers never talk directly) is the winning formation. Keep it.
- Do NOT trust an agent reviewer's approval as a quality gate. Swarm-tax: every time an agent reviewer approved a change, the change failed hidden tests, 24 of 24 approvals (structures crawl B2). Keep independent acceptance tests and the owner's check. Verification is a budgeted stage, not a free check: when verification time meets or exceeds production time, human review is theater (AWS Builder, VCR, bottlenecks crawl B1, anecdotal field observation, not a survey).
- Do NOT chase grounding accuracy past about 92% (proposal 4, PureTensor). Do NOT add handoff structure to fix handoff loss: in one field study, adding JSON schemas and validations to handoffs increased total token spend 1.4x-2.8x over the single-thread baseline, and 12 of 14 multi-agent deployments rolled back or were abandoned (Madani Agency, 14 deployments, bottlenecks crawl B3, Source 18, small self-selected sample, treat 86% as a warning flag, not a base rate).

## 7. Priority order and the single first experiment

Order, by (measured effect on our own loop) times (cost to try):

1. Batch actions per observation inside code-exec programs (proposal 1). FIRST. Already proven in-repo (Pick 1, minus 53% wall, calls 5 to 2), design exists (A1), zero new infrastructure, zero new workers. If it fails on held-out tasks, we learn it in one experiment and stop.
2. DOM/ARIA-first observation (proposal 2). Second. Our own DOM numbers are already 100x+ faster for reading state, and the pieces exist (zen-mcp, cdp.mjs, A1 dom_observe). Needs the fallback discipline (screenshot verification, real-mouse clicks, single-session ownership) built and tested, which is why it is second, not first.
3. Code-exec and CLI replace GUI steps (proposal 3). Third, as the generalization of proposal 1. Same mechanism, wider scope, needs a per-task judgment about which steps are deterministic.
4. Faster coordinate grounding (proposal 4). Fourth. Mostly a consequence of proposal 2 (DOM rects) plus a cache with a strict invalidation rule. Do not build the cache before the DOM default flips; the cache alone without DOM rects is a smaller win with a stale-coordinate risk.
5. Cut tool calls per task (proposal 5). Fifth as a standalone change, but apply its cheap parts immediately inside proposals 1-4: diff observations, short structured reports, file-referenced plans. These cost nothing and the crawl supports all three.

The single first experiment is proposal 1's verification: Pick 4 fixture, code-exec program vs step-by-step loop, n=3 per arm, then one held-out realistic task by an independent runner. One experiment, one decision: does the Pick 1 saving generalize, or was it fixture-specific? Everything else in this paper waits for that answer, because if batching does not generalize, the DOM and grounding proposals inherit the same doubt (they all assume the loop can be collapsed), and if it does generalize, proposals 2-4 are the way to extend it.

## 8. Verification protocol for every proposal (standing rules, restated)

- Wall time is the headline metric (total wall time per task, timed and logged). Never self-reported speed: METR RCT (16 developers, 246 issues, July 2025, re-analysis Oct 2026, accessed 2026-11-21, MEASURED) found tasks took 19% longer with AI while developers believed they were 20% faster, a perception gap of about 40 points (bottlenecks crawl B2, Source 4).
- Same timed wrapper, same fixture, same verified end state for both arms. n=3 minimum per arm for any wall-time claim; n=1 is a smoke test, not a measurement (the A1 design already states this for D1).
- Realistic, complex tests (standing rule): held-out cases from an independent runner, varied app, content, geometry, and sequence. Generators never run their own tests.
- Report per run: wall, think total, model calls, input tokens, refusals, misclicks, session deaths, retries. A win on wall with a rise in refusals or deaths is not a win.
- Stall detection stays as it is (standing rule, matches the crawl): dedicated watcher, poll every 5 min, poke and restart after 15 silent min, watchdog reports to Muse not to the coordinator, watch progress markers (steps, artifacts, beats) not process liveness. The crawl adds one refinement worth adopting: a hard wall-clock timeout per task at p95 completion plus margin (bottlenecks crawl B5, Sources 21-24). Our own stall history (clone2 70+ min, coordinator #2 50 min silence) is what that timeout would have caught earlier.
- No em dash or en dash in any file or message the owner sees. No ydotool. No personal info on GitHub. Small commits, push as you go.

## Sources (all accessed 2026-11-21)

Internal (our repo and task brief, not external claims):

- Task brief from Worker W, 2026-11-21: t01 7 min / 12 calls vs 2,678 ms scripted; 87.8% loop share; clone1 10/10 in 59.1s; agy-q 4/5 in 20.5s; fcc-k 10/10 in 28.6s; full suite 1,523 tests 0 failures in 119.9s; fcc K2 died twice with zero output; agy Q2 timed out at 10 min at 4/10; clone2 stalled 70+ min; coordinator #2 stall flagged 04:14, killed 04:36.
- improvements/a1-code-exec-dom-design.md, 2026-11-19: Pick 1 rerun 4/4, wall 37.54s to 17.59s, think minus 56%, calls 5 to 2; D1 core think 99.2s to 20.7s, n=1 per arm.
- docs/zen-dom-control-comparison.md, 21/11/2026, live measurements: zen-mcp DOM read 3-5ms, click 2-3ms; Selenium read 14ms, click 66ms headless; vision grounding 17/29 = 58.6% (Phase 2.1 E2); BiDi click 971ms reported ok with counter stayed 0; one remote session total per Zen instance; DOM 100x+ faster for reading state.

Crawled (via improvements/worker-w-crawl-structures-20261121.md and improvements/worker-w-crawl-bottlenecks-20261121.md, both 2026-11-21; primary links in those files):

- OSWorld-Human, arXiv 2506.16042v2: planning more than half, sometimes close to 75%, of latency; best agents take 2.7-4.3x too many steps.
- Hybrid Computer Use (HCU), arXiv 2610.41432v1, Oct 2026: batch actions, AX diffs, highest OSWorld 2.0 scores among compared systems.
- Qwen-UI-Agent technical report, blog 2026-07-31: more than 40% of outputs batched, 58.4% and 21.7% fewer steps per task.
- OpenBot research notes, updated 2026-09-16: code execution is the biggest latency lever; OpenAI docs recommend code-execution harness over step-by-step computer tool.
- PureTensor bake-off PT-R-2026-028, 2026-09-26: same model 38.2s vs 12.7s median by harness (3.0x); click accuracy 95.8%/93.1%/91.7%; viewport 12% misplacement.
- Olliebot / Browser Use timing table, date UNVERIFIED: DOM 15s vs vision 75s same task; 0.8s per screenshot for encoding alone (secondhand attribution, verify before quoting externally).
- SyndiPath, 2026-11-08: ARIA about 320 tokens vs vision 2,400+; 0.4-0.9s vs 2.8-5.5s per action (vendor blog, multipliers UNVERIFIED).
- MobiBench, 2026-10-21, arXiv:2512.12634: GPT-4.1 tree 27.17%, screenshot 4.72%, hybrid 31.50%; 508 tasks.
- UI-TARS Desktop writeup, about 2026-10-18: scripted selectors under 50 ms/step vs 800-2,500 ms/step vision GUI (secondhand table, UNVERIFIED).
- Zylos / LLMCompiler, 2026-04-26: 1.8x HotpotQA, up to 3.7x parallelizable workflows, up to 6x cost reduction (original ICML 2024 paper numbers).
- Mittal, "How Fast Do Agents Rot?", about 2026-09: near-perfect to near zero within 16 steps; n=10,664 trajectories.
- Xia et al., "Diagnosing and Mitigating Context Rot", 2026-10-27: parallel sampling gain 2.6%-4.9%.
- tokenade.net, about 2026-10-16: 50-turn session about 1M input / 40K output tokens, 25:1; re-sent context about 62% of bill (secondhand, UNVERIFIED).
- Anthropic "Worse Together", 2026-11-11: coordinator beat peer teams in 4 of 4 environments by 10-45 points.
- Swarm-tax experiment, 2026-10-26, 144 runs: one agent 56.8% vs team 25.7%; team with full task file 54.1%; reviewer approvals 24 of 24 failed hidden tests.
- Stackness, 2026-11-11, 364 runs: effective parallelism 1.21 overall, 1.46 busiest window, 1.82 six-agent run; about 0.3x the agent cap.
- Nosov, 2026-11-07, 288 runs: sub-agents plus 74%-221% cost, same recall.
- Sub-agent concurrency benchmark, circa 2026-11-20/21, 2,124 runs, read via news summary: solve rate 83% to 59%, latency 17.5 to 27.8 min, tokens 1.41x-3.31x.
- METR RCT, July 2025, re-analysis Oct 2026, CACM 2026-11-09: tasks 19% longer with AI (CI plus 2% to plus 39%); felt 20% faster; predicted 24% faster; 246 issues, 16 developers.
- Handoff-loss paper via zicq.com summary, about 2026-11-17: rewrite from full history recovers 70-82% of lost learning (reported, not independently verified).
- Madani Agency field study, Jan 2025-Apr 2026: 12 of 14 deployments rolled back or abandoned; handoff structure added 1.4x-2.8x tokens (small self-selected sample).
- Stall-detection sources, bottlenecks crawl B5: walking-dead detection (68 infinite-loop failures across 47 projects from 6,549 repos scanned, secondhand), heartbeat watchdog pattern, zombie detection (one loop: 274 calls, 91,547 tokens before noticed), neuramesh stall watchdog (5-min pass, 15-min full pass).
- Lauren Tan clip crawl, improvements/worker-w-crawl-clip-20261121.md, 2026-11-21: "All Code Is Slop (Except Mine)", AI Engineer Code Summit, 14 Nov 2026; delegate code to agents, done means nothing without runnable verification evidence, repeated mistakes become deterministic rules, repeated ops become tools, ask "can this later run without me?". Headline numbers (3,000 PRs/month, 0.5% revert) are the team's own self-reported claim, not audited, and depended on free Grok tokens at SpaceX.

## Gaps and UNVERIFIED items

- No crawled source gives a measured think-vs-observe-vs-act split of wall time for a computer-use loop. Our 87.8% figure is INTERNAL and stands alone.
- No crawled source measures "one observation yields many actions" as a standalone A/B wall-time intervention on a desktop GUI task. HCU and Qwen-UI-Agent are the closest published evidence, via batching and step counts. The proposal 1 experiment is designed to fill exactly this gap on our own test cases.
- SyndiPath multipliers (7.5x tokens, 4x latency), the olliebot 15s vs 75s pair, the tokenade 62% re-sent-context figure, and the handoff 70-82% recovery figure are UNVERIFIED secondhand claims. They are used here only as direction, never as the load-bearing number for a proposal. The load-bearing numbers are our own Pick 1, D1, zen-mcp, and E2 measurements.
