# S14. The Agent Evaluation Crisis (Agentic Frontier)

- Class: (f) blind composite test design for GUI agents
- URL: https://www.agenticfrontier.dev/articles/agent-evaluation-crisis
- Accessed: 2026-11-21
- Crawler: OPT-WEB, 2026-11-21 22:51 +07

## What they did

Synthesized D'Oro et al. 2026 (NeurIPS, arXiv 2605.08261) and the Berkeley RDI BenchJack work into an audit framework. Core result: a 1MB blind replay script (no model, fixed recorded action sequence) beats frontier models on static benchmarks: 71.1% vs 70.6% on OSWorld, 41.5% vs 32.7% on MobileWorld. Rebuilt as DigiWorld (15 sandboxed apps, data, theme, and initial state varied independently across 3.2M verified configurations), the blind script falls to 6.90% while the real model scores 45.7%. Five failure modes: contamination, determinism exploits, single-seed reporting, success-criterion gaming, cost blindness. Cures: report IQM plus confidence intervals (worked example: a mean tie 50.0% vs 53.5% becomes an 8-point IQM gap), hierarchical bootstrap with Wilson intervals, pass^k (chance all k attempts succeed; retail pass^8 under 25% for leading agents), functional correctness (check the world reached the goal state, not the action sequence), and cost as a first-class metric.

## Evidence shown

Replay vs frontier percentages, DigiWorld 6.90% vs 45.7%, GAIA humans 92% vs GPT-4 15%, WebArena GPT-4 14.41% vs humans 78.24%, pass^8 under 25%. Also cites BenchJack: an exploit agent scoring 100% on 8 benchmarks with zero tasks solved (OSWorld 73% via fetching the gold file and abusing eval in the grader).

## Applicability verdict: APPLIES

This is the design authority for our class (f). Direct rules for our blind composite tests: (1) vary the initial state per run (data, theme, starting tab, window layout), or a replay of a recorded run will pass; run a blind replay control and require it to score near zero; (2) executor blind to the test means also blind to the gold answer: the grader must check end state (file exists, text present, setting changed), never the action sequence, and the gold must not be readable from the machine the agent can reach (BenchJack fetched OSWorld gold from a public URL); (3) report IQM plus intervals over multiple seeds, not a single pass rate, and report wall time and cost beside accuracy; (4) use pass^k for reliability, since a single lucky pass hides inconsistency. Our current practice (fresh agent, held-out cases, no baked coordinates) already follows the spirit; this paper supplies the controls that prove it (replay control, state variation, end-state grading).
