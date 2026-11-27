# E1 experiment report: deliberation vs direct (Worker X-E1)

Status: INCOMPLETE. Deliberation done and measured. Both executor runs ON HOLD. No comparison is possible yet, and this report does not pretend otherwise.

## Question

Does splitting deliberation (many agents) from execution (one agent) increase SPEED or ACCURACY versus the current way (one agent decides and executes)? The idea is from the user, 21/11 01:12 (improvements/multi-agent-deliberation-idea-20261121.md).

## Design

- Task: test-05-contact-book, 28 spec steps (add Frank Sinatra, edit Bob phone to +1-555-9999, star David Kim, delete Spam Bot, search and group filter, save directory). Same task for both conditions.
- Condition A (DIRECT): 1 fresh executor reads the spec and fixture, decides each step itself, drives live Zen hand-driven through the step driver.
- Condition B (DELIBERATED): 3 deliberators in parallel read the spec and fixture and write plan drafts; the coordinator merges them into ONE plan file; 1 fresh executor executes ONLY that plan (it never sees the spec or fixture).
- Runs are sequential on the shared Zen, never concurrent. Each executor opens only its own new tab, clears localStorage first, closes only its own tab, deletes its session.
- PASS/FAIL is decided from DOM reads plus the fixture __agyVerify() result, never from an agent claim.
- Wall times are wall-clock Asia/Ho_Chi_Minh. Deliberation wall time is the parallel max member time. B total is deliberation + merge + execution, each stated separately.
- Agent mechanism: this coordinator is a depth-2 subagent with no subagent-spawn tool, so the fresh agents are fresh codex CLI invocations on the laptop (codex 0.169.0, -m gpt-6-luna -c model_reasoning_effort=max -s danger-full-access --json), one process per agent, launched detached, briefed self-contained from files. A fresh codex exec process has no memory of the task or of other agents. Tool calls are counted from the --json event stream (completed command_execution items; agent_message items are not tool calls).

## Why test-05

Mid-size (28 steps) with a varied decision surface: modal add, edit, favorite star, delete, search filter, group filter, save. More distinct decision points than test-09 (25 steps, mostly linear timer flow), so more room for deliberation to matter. Fixture verified before the experiment: every spec id exists (static ids plus JS-rendered ids); __agyVerify reads real state (contacts model plus DOM banner), no self-simulation; fixture uses no localStorage (state is in-memory, a fresh tab is fresh state). Spec, fixture, and hand_drive.py md5-identical between the VM repo and the laptop repo.

## Deliberation results (measured)

Launched 17:54:45, three deliberators in parallel, identical brief.

| Deliberator | Finished | Wall time | Tool calls | Plan | Steps | UNVERIFIED | Tokens in / out (reasoning) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| delib-1 | 18:03:25 | 8m 40s | 5 | draft-1.md, 22,842 bytes | 68 | none | 198,978 / 28,305 (15,159) |
| delib-2 | 18:02:25 | 7m 40s | 5 | draft-2.md, 17,921 bytes | 62 | none | 177,601 / 24,994 (14,486) |
| delib-3 | 17:59:17 | 4m 32s | 2 | draft-3.md, 18,548 bytes | 58 | none | 86,545 / 14,696 (9,637) |

- Deliberation wall time (parallel max): 8m 40s (520 s).
- Total deliberation tokens: about 463,124 in, 67,995 out. (Delib-1 input is high because codex loads large cached context per run; the number is reported as observed, not as a cost claim.)
- All three drafts agreed on every load-bearing fact (star is a span, use click_js; delete has no confirmation; select by JS value plus change; search live on input, group on change, all resets; banner exact text; final __agyVerify check). All three reported zero UNVERIFIED selectors.
- Delib-2 note: its first plan write failed on a string-interpolation error in a dynamic-id template; it rewrote the file with the template kept literal. That is why it took longer than delib-3 despite the same brief.
- Delib-1 and delib-2 wrote in Vietnamese; delib-3 in English.

## Merge (measured)

Coordinator merged the three drafts into improvements/worker-x-e1-plan-test-05.md (58 steps, 22,145 bytes), copied to /tmp/e1/plan-test-05.md on the laptop (md5 a7b5646b2bf081386bb7bcea0563ad5a). Merge rule: base skeleton draft-3, contested points resolved by majority or by the more robust option, every point checked against the fixture HTML. Decisions are recorded in the plan file merge note. Validation after merge: 58 numbered steps sequential, 64 JSON commands all parse (0 bad), all 15 element-id references point at the 14 find steps, every find is consumed. Merge wall time: about 2 minutes, bounded by file mtimes (drafts fetched 18:03:48, plan written 18:05:50).

## Numbers table

| Condition | Wall time | Tool calls | Driver commands | Errors / misclicks | Result |
| --- | --- | --- | --- | --- | --- |
| A (DIRECT) | UNMEASURED (on hold) | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED |
| B deliberation | 8m 40s (parallel max) | 5 + 5 + 2 = 12 | n/a (no driving) | 1 (delib-2 first write failed, rewrote) | 3 drafts, 0 UNVERIFIED |
| B merge | about 2 min | n/a | n/a | 0 | 1 plan, validated |
| B execution | UNMEASURED (on hold) | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED |
| B total | UNMEASURED (deliberation 8m 40s + merge about 2 min + execution UNMEASURED) | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED |

## Hold status (why there is no verdict yet)

- Worker Y4 was running agy-q2 10 tests live on the same Zen. Its scripted run aborted 0/2 at 17:52 (q01/q02 failed on the first type step: body visible=False, the hidden-body incident Worker R saw 16:36-16:44). No Y4 report on origin/todolist-push as of the last check.
- 17:59 AGENTS.md standing rule: Y4 probes navigated fixture tabs while the user was at the keyboard and the user's physical keyboard + mouse stopped responding for about 1 min (self-recovered 18:00). A live runner must NEVER open/navigate/switch tabs in the user's Zen while the user is at the keyboard; do only non-driving work until told to resume.
- 18:04 parent order: E1 executor runs are ON HOLD until the user hands the machine over again and Muse tells E1 to resume.
- E1 compliance: E1 has never opened, navigated, or switched any Zen tab, and has never started a Marionette session. No executor was mid-run, so there was nothing to stop cleanly. The infra scripts (driver port 4451, HTTP server port 8767, chosen to avoid Y4 ports 4448/8768) are written and transferred but NEVER started. No geckodriver was launched by E1.

## Verdict

NONE YET. The research question (is deliberation faster? more accurate?) is UNANSWERED because neither executor has run. Any verdict now would be fabrication.

What can be said honestly from the measured half: deliberation plus merge costs 8m 40s + about 2 min before execution even starts. For condition B to win on total wall time, its execution must beat condition A execution by more than about 10m 40s. That is a hypothesis to test on resume, not a conclusion. Deliberation produced a plan with zero unverified selectors and three-way agreement on every load-bearing fact, which is a real input to the accuracy question, but accuracy is decided by the executor runs, not by the plan looking good.

## Ready for resume

- Merged plan: /tmp/e1/plan-test-05.md on the laptop, improvements/worker-x-e1-plan-test-05.md in the repo.
- Executor briefs: /tmp/e1/worker-x-e1-executor-a-brief.md and worker-x-e1-executor-b-brief.md on the laptop.
- Infra scripts: /tmp/e1/worker-x-e1-step.sh, worker-x-e1-start-infra.sh (driver port 4451, HTTP 8767), worker-x-e1-stop-infra.sh on the laptop. Start them only after the resume order.
- Resume conditions: (1) parent confirms Y4 done (its report on origin/todolist-push); (2) parent confirms the user handed the machine over again. Run A first, then B, sequentially.
- Pre-flight before each executor run (added after Y4 incident): check no geckodriver from Y4 is active, check ports 4451/8767 are free, start infra, then verify a fresh tab renders with body visible before the executor starts (Y4 q01/q02 failed exactly here). If body is hidden, do not start the executor; report it.

## Files

- improvements/worker-x-e1-experiment-log.md (full timestamped log)
- improvements/worker-x-e1-experiment-report.md (this file)
- improvements/worker-x-e1-plan-test-05.md (merged plan)
- improvements/worker-x-e1-deliberator-brief.md, worker-x-e1-executor-a-brief.md, worker-x-e1-executor-b-brief.md (briefs)
- improvements/worker-x-e1-step.sh, worker-x-e1-start-infra.sh, worker-x-e1-stop-infra.sh (infra scripts)
- Laptop scratch (not committed): /tmp/e1/ (briefs, drafts, plans, events JSONL, probe logs)
