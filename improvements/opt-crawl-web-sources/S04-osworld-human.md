# S4. OSWorld-Human: Benchmarking the Efficiency of Computer-Use Agents (Abhyankar et al.)

- Class: (b) slow first action and think-observe loop costs
- URL: https://arxiv.org/html/2506.16042v1
- Accessed: 2026-11-21
- Crawler: OPT-WEB, 2026-11-21 22:50 +07

## What they did

First systematic latency study of computer-use agents on OSWorld (369 tasks). Broke down Agent S2 and GTA1 trajectories on 37 tasks into retrieval, planning, grounding, action, screenshot, reflection. Built OSWorld-Human, human gold trajectories for all 369 tasks, plus a Weighted Efficiency Score.

## Evidence shown

Planning and reflection LLM calls are 75% to 94% of total latency across tasks; judging/reflection alone is 22.5% (GTA1) to 33.6% (S2); each successive step can take 3x longer than early steps as prompt history grows; best agents take 1.4-2.7x more steps than necessary (16 agents evaluated); best agent 42.5% success but only 17.4% on the strictest efficiency metric. Concrete example: changing line spacing of two paragraphs takes an agent 12 minutes, a human under 30 seconds.

## Applicability verdict: APPLIES

This is the core diagnosis for our think-observe loop. Two fixes follow from their numbers, and both match our standing direction: (1) cut LLM calls per step (group actions into one call, drop per-step reflection/judging, which is up to a third of time); (2) cut steps per task (their 1.4-2.7x over human is our batching lever). Their "later steps 3x slower" also justifies our observation expiry: stale context is not just stale, it is expensive. Caveat: their numbers are GPT-4.1 planner plus UI-TARS grounding on Ubuntu VMs, not our Luna/Codex loop, so the percentages transfer as direction, not as our exact budget.
