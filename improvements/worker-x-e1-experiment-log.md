# E1 experiment log, deliberation vs direct (Worker X-E1)

All times Asia/Ho_Chi_Minh. Coordinator: Worker X-E1. Branch: todolist-push.
Repo (VM): ~/workspace/computer-use-wayland. Laptop repo: ~/workspace/computer-use-wayland.
Zen: live on laptop, PID 27958, --remote-debugging-port=9222 --marionette (Marionette 2828).

## Task picked

test-05-contact-book (28 steps). Why this one:
- Mid-size (28 steps) with a varied decision surface: modal add, edit, favorite star, delete, search filter, group filter, save. More distinct decision points than test-09 (25 steps, mostly linear timer flow), so more room for deliberation to matter.
- Fixture verified before the experiment: every spec id exists (static ids plus JS-rendered ids btn-edit-contact-${c.id}, phone-${c.id}, btn-fav-contact-${c.id}, btn-del-contact-${c.id}); __agyVerify reads real state (contacts model + DOM banner), no self-simulation; fixture uses no localStorage (state is in-memory, a fresh tab is fresh state).
- md5 of spec, fixture, and hand_drive.py identical between VM repo and laptop repo.

## Agent mechanism (recorded because it differs from the brief)

This subagent (depth 2) has no subagent-spawn tool, so the fresh agents are fresh codex CLI invocations on the laptop (codex 0.169.0, -m gpt-6-luna -c model_reasoning_effort=max -s danger-full-access --json), one process per agent, each launched detached with setsid nohup, each briefed self-contained from a file. A fresh codex exec process has no memory of the task or of other agents. Executor A never sees the deliberation; executor B sees ONLY the final plan file. Tool calls are counted from the --json event stream (item type command_execution and other tool item types, agent_message excluded).

## Ports (chosen to avoid Y4)

Y4 (Worker Y4, agy-q2 scripted run) uses WD 4448 and HTTP 8768. E1 uses WD 4451 and HTTP 8767. P used 4450/8765, R used 8766.

## Zen contention (Y4)

- 17:50 parent warning: Y4 is running agy-q2 10 tests live on the same Zen. E1 executor runs must wait until Y4 is done. Deliberation may proceed now.
- 17:51 check: no geckodriver on laptop, no codex/fcc processes, no Y4 report on origin/todolist-push.
- 17:56 check: /tmp/worker-y4-live.jsonl exists (2312 bytes, last write 17:52). Y4 q01 and q02 both failed at the first type step: "check body visible" returned false, then "element not interactable: could not be scrolled into view" on the first input. Same hidden-body symptom Worker R saw 16:36-16:44. No run_agyq2 process running at 17:56. Y4 appears to be diagnosing (probe_y4.py present in /tmp/worker-y4-server). No Y4 report on origin yet. E1 executors stay on hold.

## Timeline

- 17:47 E1 task received.
- 17:49 laptop recon: Zen PID 27958 up, Marionette 2828 and 9222 listening, codex 0.169.0, /tmp/geckodriver present, no stale geckodriver.
- 17:50 Y4 contention warning received from parent.
- 17:52 codex mechanism probe: first launch failed (not in a trusted directory, /tmp/e1 is outside a git repo). Relaunched from the laptop repo dir, prompt via stdin. Probe SUCCEEDED: probe-last.txt = CODEX_PROBE_OK, events JSONL shows thread.started, command_execution item, agent_message, turn.completed (input_tokens 36374, cached 17920, output 123).
- 17:54 deliberator brief written (improvements/worker-x-e1-deliberator-brief.md, dash-clean), transferred to laptop, 3 numbered variants created (brief-delib-1/2/3.md).
- 17:54:45 DELIB_LAUNCH: 3 deliberators launched in parallel (PIDs 178065, 178066, 178067).
- 17:55 executor briefs A and B written (dash-clean). Infra scripts written: step.sh, start-infra.sh (driver port 4451, HTTP 8767), stop-infra.sh. All transferred to /tmp/e1/ (step.sh and start-infra.sh chmod +x).
- 17:56 deliberators still running (01:31 elapsed each). delib-1: 6 command executions, delib-2: 6, delib-3: 2. No plan files yet. Y4 still active (see above).

## Deliberation phase (DONE, 17:54:45-18:03:25)

Three deliberators launched in parallel at 17:54:45, identical brief, different output files. All three read only the spec, the fixture, and hand_drive.py. None touched Zen.

| Deliberator | Finished | Wall time | Tool calls | Plan file | Plan steps | UNVERIFIED selectors | Tokens in/out (reasoning) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| delib-1 (PID 178065) | 18:03:25 | 8m 40s | 5 | draft-1.md, 22,842 bytes | 68 | none | 198,978 / 28,305 (15,159) |
| delib-2 (PID 178066) | 18:02:25 | 7m 40s | 5 | draft-2.md, 17,921 bytes | 62 | none | 177,601 / 24,994 (14,486) |
| delib-3 (PID 178067) | 17:59:17 | 4m 32s | 2 | draft-3.md, 18,548 bytes | 58 | none | 86,545 / 14,696 (9,637) |

Deliberation wall time (parallel = max member time): 8m 40s (delib-1).
Tool calls counted from the --json event stream (completed command_execution items only; agent_message items are not tool calls).
Delib-2 note: its first plan write failed on a string-interpolation error in a dynamic-id template; it rewrote the file with the template kept literal. That is why it took longer than delib-3 despite the same brief.
Delib-1 and delib-2 wrote in Vietnamese; delib-3 in English. All three agreed on every load-bearing fact (star is a span, use click_js; delete has no confirmation; select by JS value plus change; search live on input, group on change, all resets; banner exact text; final __agyVerify check).

## Merge (DONE, ~18:05-18:10)

Coordinator merged the three drafts into improvements/worker-x-e1-plan-test-05.md (58 steps, 22,145 bytes), also copied to /tmp/e1/plan-test-05.md on the laptop (md5 a7b5646b2bf081386bb7bcea0563ad5a, matches). Merge rule: base skeleton draft-3, contested points resolved by majority or by the more robust option, every point checked against the fixture HTML. Decisions recorded in the plan file merge note. Validation after merge: 58 numbered steps sequential, 64 JSON commands all parse (0 bad), all 15 element-id references point at the 14 find steps, every find is consumed. Merge wall time: about 2 minutes, bounded by file mtimes (drafts fetched 18:03:48, plan written 18:05:50). CORRECTION: an earlier draft of this log line said "about 25 minutes"; that was an unmeasured guess and is wrong. The mtime-bounded window is about 2 minutes. The merge is coordinator overhead the experiment design did not budget as a separate line; the honest B total must be deliberation + merge + execution, and the report states all three separately so the reader can add them.

## HOLD (from 18:04, parent order; AGENTS.md standing rule 21/11 17:59)

- 17:59 AGENTS.md entry: Y4 probes (probe_y4b 17:57, probe_y4c 17:59) navigated fixture tabs while the user was at the keyboard; his physical keyboard + mouse stopped responding for about 1 min, self-recovered 18:00. Standing rule: a live runner must NEVER open/navigate/switch tabs in his Zen while he is at the keyboard; finish the in-flight probe, then do only non-driving work until told to resume.
- 18:04 parent order: executor runs (conditions A and B) are ON HOLD until the user hands the machine over again and Muse tells E1 to resume. Do only non-driving work until then.
- E1 compliance: E1 has never opened, navigated, or switched any Zen tab, and has never started a Marionette session. No executor is mid-run, so there is nothing to stop cleanly. The infra scripts (driver on port 4451, HTTP server on 8767) are written and transferred but NEVER started. No geckodriver was launched by E1. Deliberation, merge, log, and report are non-driving work and are complete.
- Y4 status at hold time: its scripted run aborted 0/2 (q01/q02 failed 17:52, body visible=False, hidden-body incident). No Y4 report on origin/todolist-push as of the last check (18:04 fetch). Y4 done-signal is still pending, independent of the user-away condition.

## Condition A (DIRECT) run

ON HOLD. Not started. Executor brief A is written and transferred to the laptop (/tmp/e1/worker-x-e1-executor-a-brief.md). Resume condition: parent confirms Y4 done AND user handed the machine over again.

## Condition B (DELIBERATED) execution run

ON HOLD. Not started. Merged plan is ready at /tmp/e1/plan-test-05.md. Executor brief B is written and transferred to the laptop (/tmp/e1/worker-x-e1-executor-b-brief.md). Resume condition: same as A, and B runs only after A finishes (sequential, shared Zen).

## Numbers (final)

Deliberation: max member 8m 40s (520 s). Merge: about 2 minutes, mtime-bounded (drafts fetched 18:03:48, plan written 18:05:50). Conditions A and B: NO NUMBERS YET, executors on hold. No wall times, no accuracy results, no verdict on speed or accuracy. Anything else would be fabrication.
