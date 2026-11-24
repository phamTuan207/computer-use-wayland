# Multiagent coordination research for the R3-L3 run

Research date: 2026-11-24. Run date: 2026-11-25.
Run shape: 55 tasks, 2 runners, 4 scorers, 2 tiebreakers, 1 coordinator,
rolling release, estimated 19-31 hours.

Method: last30days engine v4.5.0 (window 2026-10-25 to 2026-11-24) on three
topics, plus web supplements. Engine results were uneven and this report says
so plainly: the Lauren Tan topic returned 0 usable items (thin evidence), the
Anthropic topic returned 23 items (GitHub 11, Hacker News 12), the OpenAI
topic returned 14 items, mostly off-topic news noise. The concrete practices
below therefore come from the engine hits that did land, from first-party
pages fetched in full (Anthropic Projects article, pstack analysis of the
upstream README and skills), and from the team's own internal workflow doc
`improvements/lauren-tan-workflow-20261122.md`, which already encodes the
Lauren Tan standard. Nothing below is copied from a vendor claim without a
caveat where the claim is self-reported.

Caveats up front: Lauren Tan's PR counts (about 1,150 PRs in 4 days, about
3,000 PRs in a month) and Anthropic's multi-agent eval numbers (+90.2% on an
internal research eval, about 15x tokens) are vendor/self-reported with no
independent measurement. The mrlatte.net review of pstack (2026-11-06) states
explicitly that no public measurements of pstack's effectiveness exist yet.
Transfer the methods, not the numbers. Her setup also ran on effectively free
tokens at SpaceX/xAI; this run does not have that, so lane counts and
parallelism are capped by the team's own measured numbers, not hers.

## 1. Trust pyramid: fix at the highest layer that can hold the fix

What it is: when an agent makes a mistake, fix it in this order, top first:
(1) codebase/architecture, so the wrong choice cannot be written; (2)
deterministic checks (lint, types, compiler, tests) that block the error at
write time; (3) runtime validation (the agent runs the code and reads real
output) and formal verification; (4) text rules (AGENTS.md, rules files,
skills) only for what cannot be encoded as a check. Before writing a rule,
ask two questions: can this become a deterministic check that blocks the
error immediately, and better, can the design change so the wrong choice is
impossible to write. Only when both answers are no does it go into a rules
file.

Where it came from: Lauren Tan, "All Code Is Slop (Except Mine)", AI Engineer
Code Summit, talk 11/11/2026, video 14/11/2026; Paul Kuo analysis
"Agent mistakes into checks" (19/11/2026); pstack README. Internal doc
section 2.

How it applies to R3-L3: every scoring disagreement and every runner error
during the run gets classified by layer before it gets a fix. A scorer
misreading a rubric item becomes a rubric wording fix plus a worked example
in the scoring checklist (layer 2/3), not a paragraph added to the brief
(layer 4). A runner submitting evidence in the wrong format becomes a
template with required fields that the coordinator rejects when empty
(layer 2), not a reminder in chat. The coordinator keeps a running count of
fixes per layer; if most fixes land in layer 4, the run is accumulating
text debt and the next pre-run meeting must convert the top three into
checks or templates.

## 2. Coordinator does not code, does not run, does not score

What it is: bots are managers, not coders. The coordinator gathers work,
breaks it down, delegates, supervises, and merges. It never does the work
itself. In pstack's delegation trust boundary, the lead agent does not write
code; it hands work to a background subagent, then reviews the diff itself
and writes its own summary instead of repeating the subagent's claims,
because an agent can believe it is done when it is not. Anthropic's Projects
redesign (14/11/2026) ships the same shape as a product: a coordinator that
scopes the request, delegates to threads, reviews outputs, and assembles the
result, while threads do the work.

Where it came from: Lauren Tan talk and pstack `poteto-mode` / Orchestrate
playbook; Anthropic, "Projects redesigned: from folder to conversation"
(https://claude.com/resources/articles/projects-redesigned, published
2026-09-17, discussed on Hacker News 14/11/2026, 101 points, 99 comments);
internal doc sections 4 and 5.

How it applies to R3-L3: the single coordinator runs zero tasks and scores
zero tasks. Its job is queue, briefs, evidence intake, conflict resolution,
landing, and the decision log. If the coordinator is tempted to "just run
this one task quickly", that is a staffing failure, not a shortcut: it means
a runner lane is blocked and the coordinator's job is to unblock the lane.
Each runner result is accepted only after the coordinator has re-read the
evidence itself (command, output, artifact), never on the runner's word
that it passed.

## 3. One coordinator beats peer-to-peer teams (measured)

What it is: in Anthropic's "Worse Together" study (11/11/2026, 77 scenarios),
a single-coordinator team beat peer-to-peer multi-agent teams in 4 out of 4
environments, by 10-45 points. Agents messaging each other directly
coordinate worse than agents reporting to one coordinator through a shared
medium.

Where it came from: Anthropic, "Worse Together" (11/11/2026); internal doc
section 9.

How it applies to R3-L3: keep the existing rule, no peer-to-peer contact
between runners, scorers, and tiebreakers. All traffic goes through the
coordinator and the shared repo (run log / board). A scorer who needs
clarification asks the coordinator, never the runner. A runner who spots a
problem in another runner's task reports it to the coordinator, never to the
other runner. This is already the design; the study is the reason not to
relax it mid-run when it feels slow.

## 4. Evidence contract: state the finish condition before the work starts

What it is: "done" means nothing without runnable evidence. The finish
condition is a concrete check the agent can run, stated before work begins,
not "make it better". A confident reply with no evidence is a red flag.
"Inconclusive" is an honest answer and it is not a pass. Verification must
happen on the same surface where the problem appeared: a UI bug is
reproduced in the UI, not declared fixed by a unit test. A CLI change is
proven by running the real command; a UI change by driving the running app;
a performance claim by comparing profiles; a storage change by reading the
value back.

Where it came from: Lauren Tan talk; pstack Prove It Works principle and Bug
fix playbook; mrlatte.net pstack analysis (06/11/2026); internal doc
section 6.

How it applies to R3-L3: every task brief carries its finish condition as a
runnable check (exact command or exact UI flow plus the expected observable
outcome). A runner's delivery must attach: the exact command run, its real
output or log, the commit hash, and a screenshot or video for machine tasks.
A scorer marks PASS only when it has re-run or re-read that evidence; a
delivery with no evidence is returned unread. "Inconclusive" is recorded as
such and counts as not passed, never as a soft pass. The 53/55 bar is a
finish condition; it is never loosened silently mid-run (see practice 10).

## 5. The grader is never the author

What it is: the agent that grades a change is never the agent that wrote it.
pstack's swarm reports results as PASS, ISSUES, or BLOCKED with evidence; a
result that omits the commits or measurement methods the brief required is
discarded and the worker is launched once more; if the second attempt also
omits them, that part stays a gap, and a gap does not count as a pass.
pstack's interrogate is adversarial review where only findings demonstrated
through execution survive: a finding without a failing test, a reproduction
script, or incorrect output is discarded, as are opinions about style or
naming that cannot be demonstrated. Only findings the parent confirms by
re-running the same command are kept.

Where it came from: pstack swarm and interrogate skills, as analyzed at
mrlatte.net (06/11/2026); Lauren Tan talk; internal doc section 6.

How it applies to R3-L3: this is the structural reason for 4 scorers and 2
tiebreakers behind 2 runners. Enforce it mechanically: a scorer never scores
a task run by the same model family session that produced it where an
alternative exists, and a tiebreaker never re-scores by reading the first
scorer's verdict; it re-runs the evidence check itself. A scorer finding
must cite the failing command and its output (or the missing evidence);
a finding that is only an opinion about approach is discarded. One re-launch
for missing evidence, then the task is a gap, not a pass.

## 6. Arena: parallel candidates, cross-family judge, convergence as signal

What it is: give several agents the same task with the same prompt, each in
its own worktree. When all finish, a judge model from a different family
than the parent scores the candidates against a rubric; the parent also
scores them independently and compares the two judgments. Use the candidate
that is easiest to refine as the base and graft one or two useful pieces
from the rejected candidates. If candidates converge on similar results,
treat that as strong agreement; if they diverge sharply, redefine the task.

Where it came from: pstack arena skill, as analyzed at mrlatte.net
(06/11/2026); internal doc section 5.

How it applies to R3-L3: use the arena shape only at the tiebreaker layer,
not by re-running tasks. When the two scorers on a task disagree, the
tiebreaker acts as the cross-family judge: it scores the runner's evidence
against the rubric independently, without seeing either scorer's reasoning
first, then compares. Agreement between independent scorers is strong
evidence the verdict is right; sharp divergence is a signal to redefine the
task's finish condition or rubric item, not to pick a winner by vote and
move on. Keep the two runner lanes on different model families (Codex and
FCC) so that a systematic blind spot in one family shows up as divergence
rather than silent agreement.

## 7. Capture-recapture: estimate what the reviewers missed

What it is: two independent reviewers will each catch a different subset of
defects. If reviewer A finds n1 defects, reviewer B finds n2, and m overlap,
the estimated total is roughly n1 x n2 / m. Example from the literature: 10
and 8 found, 4 in common, estimated total about 20, so about 6 remain
undiscovered. The method only works when reviewers come from different
model families, because same-family reviewers miss the same things and the
estimate comes out too low. Stopping rule: stop when a reviewer from a
previously unused model family finds no new blocking defects.

Where it came from: mrlatte.net pstack analysis (06/11/2026), citing Eick et
al., ICSE 1992, and Briand et al., IEEE Transactions on Software
Engineering 26(6), 2000; internal doc not yet covering this.

How it applies to R3-L3: the 4 scorers already work in 2 pairs. After each
batch of about 10 scored tasks, the coordinator computes the overlap between
the two pairs' blocking findings. A low overlap means the true defect count
is higher than either pair found and the batch needs a second pass; a high
overlap with no new blocking defects from the second pair means the batch
can land. This turns "did we score enough" from a feeling into a number,
and it is the quantitative check on the 53/55 bar: if capture-recapture
says several failures likely remain undiscovered, the bar has not really
been met.

## 8. Rolling release as small, ordered, evidenced landings

What it is: small PRs in order, with evidence in the description; 5 narrow
PRs beat 1 fat PR. pstack's babysit-PR playbook handles blockers in order:
conflict first, then review thread, then CI, and stops at merge-ready.
Anthropic's Projects article adds the merge mechanics: each thread works on
its own branch and copy of the repo, and overlap between threads is resolved
as a merge conflict just like any other PR.

Where it came from: Lauren Tan talk; pstack Shipping and Babysit playbooks;
Anthropic Projects article (14/11/2026); internal doc section 6.

How it applies to R3-L3: rolling release means land each scored task's
evidence as soon as its verdict is locked, in task order, one small commit
per task with the evidence (verdict, scorer, key checks) in the commit
message. Do not batch a day's work into one push. Each runner works on its
own branch/worktree; if two runners touch the same file, that is a merge
conflict the coordinator resolves, not a silent overwrite. The coordinator
babysits the landing queue in blocker order: conflicts, then scoring
disputes, then CI, and a task is only "landed" when all three are clear.

## 9. Overnight contract: goal, finish condition, permissions, escape hatch, decision log

What it is: before any long unattended run, write down four things as a
contract: the goal, the finish condition, the permitted actions, and a way
to stop. "Work on this for 4 hours" is not a finish condition; without one
you wake up to four hours of motion instead of a result. Keep a decision
log (pstack `show-me-your-work`); when you return, start with its Attention
section. A plateau means pivot, and the finish condition is never loosened
silently.

Where it came from: pstack Autonomous run playbook and overnight guide, as
analyzed at mrlatte.net (06/11/2026); Lauren Tan talk; internal doc
section 6.

How it applies to R3-L3: the run contract is a one-page file the coordinator
owns before the first task starts: goal (55 tasks scored against the 53/55
bar), finish condition (every task has a locked verdict with evidence, or is
explicitly marked gap), permissions (what runners and scorers may push,
merge, or message without asking), and stop conditions (rate limit, runner
stall beyond the agreed timeout, evidence pipeline broken). The decision log
is append-only with wall-clock timestamps; its Attention section lists every
blocked task and every bar or rubric change. If the run plateaus (same
failure class repeating, no verdicts locking for an hour), the coordinator
pivots the approach and logs it; it does not lower the bar to keep the
line moving.

## 10. Every manual fix becomes a rule, and the rule lives in a check

What it is: every time a human intervenes to fix an agent, think about how
to eliminate that intervention entirely. Order of value: (1) remove the
problem with better architecture or data structure; (2) turn it into a lint
rule or test so CI catches it; (3) turn it into a skill or rule; (4) rely on
human review, which Tan labels "ngmi". The gardener habit: someone quietly
watches the flow of work, notices smells (the third copy of the same helper
in a week, lint suppressions spreading), and turns each weed pulled into a
rule so it cannot grow back. When a lint rule blocks a bad pattern, go back
and clean up old examples so later agents cannot copy them. pstack's
`/correct` skill turns repeated feedback into structural safeguards; its
`/automate-me` and `/reflect` mine old transcripts for corrections that keep
repeating. The team's own version: "Twice means a rule, and the rule lives
in a lint, a test, or a template."

Where it came from: Lauren Tan talk; pstack correct / automate-me / reflect
skills; mrlatte.net (06/11/2026); internal doc sections 8 and 9.

How it applies to R3-L3: the coordinator is the gardener for the run. Every
correction issued during the run (a brief clarification, a scoring fix, a
landing repair) is logged with its count. The second time the same
correction occurs, it becomes a template, checklist, or rubric change the
same day, not after the run. At the end of the run, the coordinator harvests
the decision log into rule changes for the next run; a correction that was
given three times and never became a rule is listed as a run failure, not
as normal coordination. This is the mechanism that makes the next run
cheaper than this one.

## 11. Playbook todo list, copied verbatim, with skipped steps labeled

What it is: the router copies the selected playbook's steps verbatim into
the agent's todo list. A step that is skipped still shows, labeled
`skip: reason`. Nothing disappears silently. The agent's first message
restates the goal and the smallest change that meets it in its own words,
then proceeds. Every claim in a reply must carry evidence or a label in the
same sentence: measured result, inference, or guess.

Where it came from: pstack `poteto-mode` skill, as analyzed at mrlatte.net
(06/11/2026); internal doc section 5.

How it applies to R3-L3: every task brief is a checklist copied from the
task's playbook (run steps, evidence steps, scoring steps), not a prose
paragraph. A runner that skips a verification step writes `skip: <reason>`
in the run log; an empty checkbox with no reason is treated as not done.
Every runner and scorer report opens by restating the task goal and the
finish condition in its own words, which catches brief misreads before
work starts. Every claim in a report is labeled: measured (with command and
output), inferred, or guessed. A guessed claim in a scoring verdict is
rejected.

## 12. Briefs carry five things, and nothing else

What it is: a good request contains the goal, the criteria for "done", the
evidence wanted, what is already known, and the real constraints. The
criteria must distinguish a pass from a failure; "make it better" and "work
on it for an hour" are not checks. Leave out two things: instructions on
how to do the work, and the requester's initial guess about the cause, which
narrows the search to where it was pointed. Let the agent restate the
problem first, then share the hypothesis.

Where it came from: pstack guide 2 (poteto-mode), as analyzed at mrlatte.net
(06/11/2026); internal doc section 5.

How it applies to R3-L3: the runner and scorer brief templates are frozen
to those five fields. No step-by-step instructions, no hint about where the
fault is, no skill names listed in the prompt (selecting skills is the
worker's job). A brief that contains a how-to or a guessed cause is
rewritten before it is sent. This is what keeps the two runners genuinely
independent: same five fields, same finish condition, different paths.

## 13. Shared memory across threads, not per-thread amnesia

What it is: in Anthropic's Projects redesign, every thread adds to and draws
from a shared memory, so decisions accumulate across the project instead of
being re-decided per thread: the release moved, the export was dropped, who
to check before touching billing. A library collects the files added and
the artifacts produced, so new work builds on past efforts. A practitioner
comment on the Hacker News thread put it concretely: the todo list becomes
individual threads with proactive communication.

Where it came from: Anthropic Projects article (14/11/2026); Hacker News
discussion, comment by kami23 (14/11/2026); internal doc section 4 (outer
loop feeds the inner loop).

How it applies to R3-L3: the run log and board are the shared memory. Before
starting a task, each runner reads the log entries for the previous tasks of
the same class (same site, same failure mode) and notes what was already
decided. The coordinator writes every decision into the log the moment it is
made, with timestamp and task number, so a runner starting at hour 20 does
not re-litigate a decision made at hour 3. The log is the outer loop feeding
the inner loop; if a runner's report contradicts an earlier logged decision
without citing it, the coordinator sends it back.

## 14. Cap parallelism deliberately, and tier models by role difficulty

What it is: multi-agent only pays on breadth-first, parallelizable,
high-value work. Anthropic reports a multi-agent system with Opus 4 as lead
and Sonnet 4 subagents outperforming single-agent Opus 4 by 90.2% on an
internal research eval, but using about 15x more tokens; on equal token
budgets a single agent often matches multi-agent, so delegation must earn
its coordination cost. The practitioner rule from the Claude Code subagent
guides: delegate large, independent, parallel work; do everything else in
the main conversation, including checking your own work. Model tiering by
role difficulty is the main cost lever: mechanical work to the cheap model,
standard work to the middle tier, hard reasoning and judgment to the
strongest. OpenAI's Agents API now enforces the same idea as a product
setting: a `multi_agent` flag with `max_concurrent_subagents` (default 6),
a concurrency cap that acts as budget control. OpenAI's guidance adds that
agents editing the same files must coordinate their changes, and short
dependent sequences should stay in the main agent.

Where it came from: Anthropic multi-agent research eval, as summarized in
the Claude Code custom-subagents best-practices reference (verified against
Anthropic docs, July 2026) and the roughworks.ca subagent guides (Nov 2026);
OpenAI Agents API launch (10/09/2026) via The New Stack (25/09/2026) and
the creuto.com coordinator-pattern analysis; internal doc section 9 (team's
own measured parallelism 1.21-1.82x, solve rate 83% down to 59% in a
2,124-run benchmark when subagents were added).

How it applies to R3-L3: do not copy Tan's 10+ parallel projects or
OpenAI's default cap of 6. The run's cap is 2 runners, set deliberately from
the team's own measurements, not inherited. Tier by role: runners do the
mechanical execution, scorers and tiebreakers (the judgment roles) get the
strongest reasoning available per lane, and the coordinator (the synthesis
and decision role) is the highest-tier work in the run. If a lane is idle
while another is overloaded, that is not a reason to raise the cap mid-run;
it is a reason to re-queue tasks to the idle lane. Any proposal to add a
third runner during the run must show it earns its coordination cost in
locked verdicts per hour, not in tasks started.

## 15. Termination, timeouts, and error classification are part of the design

What it is: defense in depth on termination: iteration caps (about 15-25
steps), wall-clock timeouts (about 300 seconds for a single loop), token and
cost budgets, loop detection, and error classification (retry 429/5xx,
terminate on 401/403). pstack's autonomy rules draw a hard line at one-way
doors: proceed without asking on reversible work, but stop and ask before
force-pushing a shared branch, deploying, deleting data, or messaging a
customer. The pstack failure record is instructive here: issue #1160
(03/11/2026) reported a cleanup step running alongside the verification
swarm and changing code after verification had finished; the proposed fix
was to treat missing verification capability as BLOCKED rather than PASS.

Where it came from: OpenAI / Anthropic / Google tool-orchestration guidance
as compiled in code-os (re-verified 06/11/2026); pstack autonomy rules and
issue #1160; mrlatte.net (06/11/2026); internal doc section 5.

How it applies to R3-L3: each task gets a wall-clock timeout in its brief;
a runner that exceeds it is stopped and the task is re-queued, not left to
run. The 15-minute silence rule stays, with the existing correction that a
poke only fires when a sent message is still awaiting a reply. Rate-limit
errors (429/5xx) are retried with backoff; auth errors stop the lane and go
to the coordinator immediately. Verification and cleanup are sequenced, never
parallel: nothing edits code or files after a task's verification has
finished. A task whose verification capability is missing (site down, tool
unavailable) is BLOCKED, never PASS. Force-push, deploy, and any
customer-facing message are one-way doors the coordinator alone decides.

## 16. What not to copy

- Tan's auto-merge. She merges her own agents' PRs and reviews what landed
  while she was away, because she spent 6 months building verification
  first. This run keeps the acceptance gate: no task lands without a locked
  scorer verdict and coordinator re-read. Auto-merge is a later trust
  level, not a starting point.
- Tan's lane count. 10+ parallel Projects assume cloud agents with their
  own machines and effectively free tokens. This run's measured numbers say
  2 lanes.
- Peer-to-peer messaging between agents. Both the Anthropic study and the
  OpenAI handoff guidance say coordination goes through the coordinator or
  through explicit handoffs, never direct agent-to-agent chat.
- Instructions as enforcement. pstack's sequencing is prose, and prose is
  followed differently across environments (issue #1176, 05/11/2026:
  a delegation step ignored in Claude Code and over-applied in Codex).
  Where a rule matters for this run (evidence required, scorer independence,
  BLOCKED not PASS), enforce it in the template or the checklist, not only
  in the brief text.

## Sources

- Internal: `improvements/lauren-tan-workflow-20261122.md` (team synthesis,
  22/11/2026); `improvements/working-structure-redesign-20261121.md`.
- Lauren Tan, "All Code Is Slop (Except Mine)", AI Engineer Code Summit,
  talk 11/11/2026, video 14/11/2026,
  https://www.youtube.com/watch?v=O_zcc6Xl12g
- pstack upstream: https://github.com/cursor/plugins/tree/main/pstack
- mrlatte.net, "pstack, the plugin that teaches coding agents the order of
  work", 06/11/2026,
  https://www.mrlatte.net/en/research/2026/11/06/pstack-agent-workflow/
- Paul Kuo, "Agent mistakes into checks", 19/11/2026,
  https://paulkuo.tw/en/articles/agent-mistakes-into-checks/
- besthub.dev, "Grok's 'Potato Sister' Open-Sources pstack: Agent Harness
  for 1150 PRs in 4 Days", 08/11/2026,
  https://www.besthub.dev/articles/grok-s-potato-sister-open-sources-pstack-agent-harness-for-1150-prs-in-4-days-fcc0f85853f3
- aliirz.com, "The factory comes after the loop", Nov 2026,
  https://aliirz.com/the-factory-comes-after-the-loop
- Anthropic, "Projects redesigned: from folder to conversation",
  https://claude.com/resources/articles/projects-redesigned (published
  2026-09-17; Hacker News discussion 14/11/2026, 101 points, 99 comments,
  https://news.ycombinator.com/item?id=50492893)
- Anthropic, "Worse Together" (multi-agent coordination study, 11/11/2026,
  77 scenarios), via internal doc section 9.
- Anthropic, "Building Effective Agents" (orchestrator-workers,
  evaluator-optimizer patterns); Claude Code subagents documentation, via
  roughworks.ca guides (Nov 2026) and the Claude Code custom-subagents
  best-practices reference (July 2026).
- OpenAI Agents API multi-agent launch, 10/09/2026, via The New Stack
  (25/09/2026) and creuto.com, "Coordinator agent pattern: who should run
  the loop", https://creuto.com/coordinator-agent-pattern-who-runs-loop
- OpenAI Agents SDK / AgentKit guidance (triage, sequential orchestration,
  parallel decomposition, handoffs), via skills-registry
  (frankxai AI Architect Academy, OpenAI AgentKit).
- Eick et al., "Estimating Software Fault Content Before Coding", ICSE 1992;
  Briand et al., IEEE Transactions on Software Engineering 26(6), 2000
  (capture-recapture), via mrlatte.net.
- last30days engine v4.5.0 runs, 2026-11-24, window 2026-10-25 to
  2026-11-24: "Lauren Tan pstack multi-agent coordination workflow" (0
  usable items, thin evidence); "Anthropic Claude Code multi-agent subagent
  orchestration best practices" (23 items: GitHub 11, Hacker News 12);
  "OpenAI Agents SDK multi-agent orchestration coordinator swarm best
  practices" (14 items: GitHub 2, Hacker News 12, mostly off-topic news).
