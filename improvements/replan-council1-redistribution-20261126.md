# R3-L3 Re-plan Council 1 Verdict: Redistribution and Scoring Design

Date: 2026-11-26. Council role: COUNCIL-1, redistribution and scoring design.
Run state: PAUSED by owner order 04:31-04:36. Epoch 8 coordinator e2bc09c6 holds the run.
This document is a design verdict only. It does not resume the run, does not edit the coordinator state file, and is not committed by this council. The coordinator commits centrally.

## 1. Decision

The council adopts the owner ratios inside the movable work pool only, counted in work units, not in raw task count. Driving stays non-movable and unchanged in structure. Scoring independence, Pair A and Pair B structure, and tiebreakers stay. Mei scores zero. Mochi keeps Pair A scorer 1 seat and takes Pair B overflow as whole tasks. Clone1 and clone2 become named scorers only after calibration. Fresh sessions fill the remainder for speed and parallelism. Nothing resumes until the Zen-AI Cloudflare fix is proven live and the owner approves resume. Task 56 runs last. Closure counts both ways.

Pinned ratio reading (owner to confirm, see section 10): clone1 gets half of a full share, where a full share is the clone2 share and the mei share. Mochi gets 85 percent of a full share. Weights are clone2 100, mei 100, mochi 85, clone1 50. Total weight 335. Shares are clone2 29.85 percent, mei 29.85 percent, mochi 25.37 percent, clone1 14.93 percent. The alternative reading, half of the average of the other three, gives clone1 47.5 against a full share of 100. The difference is small but it changes integer quotas, so the council pins half of a full share and asks the owner to confirm.

## 2. Run state used for this design

Verified from the coordinator state file, heartbeat log, ledgers, du-phong.txt, and the frozen order file thu-tu-chay.txt.

- Heartbeat at pause: graded 29, pass 23, fail 3, invalid 3. The 3 fails are the original FCC fabrications R3-001, R3-002, R3-003. All 3 were superseded by PASS re-runs under counting rule A. The 3 invalids are R3-011, R3-022, R3-024. They were replaced by DP-06, DP-02, DP-07, all PASS and inside the 23. Rule-A count is 23 PASS and 0 FAIL.
- In-flight at pause, to be finished by epoch 8 and then held:
  - R3-026 drive finished blocked. Runner e6f9a5a5, start 04:31:44, end 04:36:27. coolors.co showed Cloudflare Just a moment, Ray ID a603c518ed7945df, waited 60 seconds, still blocked. Runner stopped per bot-check rule, nothing fabricated. Snapshot sealed, manifest 59c32ec9, gate PASS, published at todolist-push 2ae0500e. Pair A scoring in progress: Mochi scorer 1 (daemon run 231, verdict via branch mochi/verdict-R3-026-L3) and fresh scorer 2 session 582ecc45. R3-026 is INVALID candidate number 4. See section 7.
  - R3-025 fresh completion drive. Runner 52e38de8, started 04:39:00, deadline about 05:09. Attempt 1 runner 140b69dc died at 04:07:05 with model truncation. Attempt-1 verdicts A1 Mochi FAIL and A2 FAIL were collected and audited, with no ledger row. The fresh drive, seal, and score produce ONE ledger row for R3-025 from the completed attempt. Attempt-1 snapshot 13d5004b and verdicts stay preserved. The council endorses this plan and adds a hard rule: the re-plan must not retroactively change any scoring outcome already filed, including R3-025 attempt 1 and the original R3-001, R3-002, R3-003 FAIL rows. Rule A supersede at closure is the only counting change, and it was already owner approved.
- Remaining after in-flight: 30 original-set tasks plus task 56. In frozen order after R3-026: R3-027, R3-028, R3-029, R3-035, R3-036, R3-037, R3-045, R3-046, DP-03, R3-049, R3-055, R3-067, R3-072, R3-074, R3-075, R3-076, R3-078, R3-079, R3-082, R3-083, R3-085, R3-086, R3-088, R3-089, R3-093, R3-094, R3-096, R3-098, R3-099, R3-100. R3-040, R3-041, R3-042 already graded PASS and are not in the remaining list.
- Pair A remaining after in-flight: 6 tasks (R3-027, R3-028, R3-029, R3-035, R3-036, R3-037). Pair B remaining: 24 tasks plus task 56, total 25 scoring tasks in Pair B mechanics. Task 56 uses Pair B mechanics per its task file unless the coordinator assigns Pair A. This design assigns Pair B.
- Class L remaining, score before reset, runner waits: R3-055, R3-074, R3-075, R3-078, R3-079, R3-088, R3-089, R3-096, plus task 56. Total 9 Class L tasks in the remaining pool, all in Pair B. All other remaining tasks are Class S, decoupled scoring from the sealed snapshot.
- Bar math at pause: need 30 of 32 remaining original-set positions counting in-flight R3-025 and R3-026, slack 2 fails. With task 56, need 31 of 33, slack 2 fails. Closure counts both 53 of 55 original and 54 of 56 with task 56. Section 7 updates this math for the R3-026 invalid candidate.
- Invalid budget at pause: 3 of 5 used. Medium 2 of 2 at cap. Hard 1 of 2. Backups used: DP-03 at position 34 pre-assigned for dropped R3-047, DP-06, DP-07, DP-02. Remaining backup: DP-05 only, very hard tier, sqlite3 on the laptop. R3-028, R3-036, R3-046 are pre-run INVALID candidates sharing the timeanddate cause with R3-011.

## 3. Movable work pool: unit definitions and totals

Clone1, clone2, mei, and mochi have no Tailscale and no SSH. They cannot drive Zen live. Movable work only is scoring from repo snapshots, INVALID analysis, review, prep research, and repo work. Driving, live fixture checks on the laptop, reset, timeout enforcement, and ledger writing stay with the coordinator and the driving lanes.

Unit definition: 1 work unit (WU) equals one scoring assignment, target 30 minutes, hard limit 60 minutes, from sealed snapshot plus frozen key section for one task, producing one verdict json file and one grade markdown file with independence declaration and key hashes.

Derived units:

- Scoring assignment: 1 WU. Two per task.
- Tiebreaker: 2 WU. The tiebreaker re-reads the snapshot, the key, and both verdicts, then grades from scratch. Counting a tiebreaker as 2 WU follows clone2 input that tiebreaker effort is about double. Tiebreakers are drawn from a planning reserve and charged to the standby pool, not to the four Muses, unless a named Muse who did not score, prep, or analyze that task is calibrated and assigned. The default stays standby.
- INVALID analysis: 2 WU per analysis. One analysis covers browser evidence review, cause proof, difficulty group check, backup mapping, and cap accounting. Cause proof standard is browser evidence (screenshot, Ray ID where present, wait log). Curl 403 alone is not proof, per du-phong.txt.
- Prep research: 1 WU per task. One pre-run check covers liveness in a browser (not curl alone), fixture freshness, key hash check, and snapshot path readiness. Prep splits into browser research, which is movable, and live laptop fixture checks, which need SSH and stay non-movable. The pool counts 31 prep units and marks 6 as live-only.
- Review: 1 WU per verdict-pair audit, plus closure package units. One audit covers verdict json parse, session match, key hashes, manifest match, allowlist check (snapshot plus key only), independence declaration, and ledger cross-check preparation. The coordinator keeps the ledger write itself. Independent audit is movable.

Pool for the 31 tasks after in-flight (30 original plus task 56):

| Work type | Count basis | Units | WU |
| --- | --- | --- | --- |
| Scoring assignments | 31 tasks x 2 | 62 assignments | 62 |
| Tiebreaker reserve | 3 tiebreakers x 2 WU | 3 tiebreakers | 6 |
| INVALID analyses | 6 analyses x 2 WU | 6 analyses | 12 |
| Prep research | 31 tasks x 1 WU | 31 checks | 31 |
| Review | 31 audits x 1 WU plus 4 closure units | 35 units | 35 |
| Total movable pool |  |  | 146 |

INVALID analyses expected, 6 total: R3-026 cause and cap ruling (in-flight scoring, analysis still open), R3-028, R3-036, R3-046 (known timeanddate candidates), plus 2 unplanned bot-wall analyses. The unplanned count follows the observed bot-wall rate: 3 invalids in 29 graded, 4 candidates in 31 counting R3-026, about 10 to 13 percent, all Cloudflare or Google blocks in Zen. The Cloudflare fix should lower the rate, but the plan does not assume zero. If more than 2 unplanned analyses arise, each extra analysis is 2 WU charged to mei lead plus clone2 second, and quotas rebalance at the next milestone.

Tiebreaker reserve, 3 tiebreakers: no tiebreaker has been needed in the 29 graded tasks to date. The reserve assumes about 10 percent disagreement on 31 tasks. If the reserve is exhausted, fresh tiebreaker sessions absorb overflow and the coordinator records the overrun. Ratios are not re-litigated per tiebreaker.

Prep live-only units, 6 of 31: R3-055 directory permissions, R3-074 script inputs, R3-075 venv, R3-089 fixture refresh (expiry 2026-12-01 08:59, refresh the day before R3-089 runs), R3-096 live diff files, task 56 sessionstore extraction. These need SSH to the laptop and stay with the coordinator or a Muse driving subagent. The other 25 prep units are browser research and repo checks, movable to the four Muses.

Review coordinator-retained units, 19 of 35: verdict-pair audits that need VM-local verdict files before the repo pull completes, plus the ledger write and push. The four Muses take independent audits after the pull, tally work, and closure drafting. The split is stated in section 4 so epoch 8 does not have to guess.

## 4. Owner ratios applied inside the movable pool

Ratios apply to the Four-Muse pool, meaning work assigned to clone1, clone2, mei, and mochi. Fresh sessions and the coordinator take the remainder. The council states both pools so the owner can see the full picture.

Four-Muse pool size: 90 WU. Fresh plus coordinator plus standby pool: 56 WU. Total 146 WU.

Ideal Four-Muse quotas at weights clone2 100, mei 100, mochi 85, clone1 50, total 335, applied to 90 WU:

| Person | Weight | Ideal WU | Assigned WU | Check |
| --- | --- | --- | --- | --- |
| Clone2 | 100 | 26.87 | 27 | Full share |
| Mei | 100 | 26.87 | 27 | Full share, scoring zero |
| Mochi | 85 | 22.84 | 23 | 23 / 27 = 85.2 percent |
| Clone1 | 50 | 13.43 | 13 | 13 / 27 = 48.1 percent, rounding to whole units |
| Total | 335 | 90.00 | 90 |  |

Clone1 at 13 WU is 48.1 percent of a full share, not exactly 50 percent, because units are whole. The next tiebreaker or extra INVALID analysis charged to clone1 brings the share to 50 percent. The coordinator tracks actual WU and rebalances at each milestone (after every 8 graded tasks) by moving the next prep or review unit to the person furthest below target. No person is assigned a half task to hit a decimal.

Per work type allocation, honoring mei scoring zero and mochi Pair A seat:

| Work type | Total WU | Mei | Clone2 | Mochi | Clone1 | Fresh / Coord / Standby |
| --- | --- | --- | --- | --- | --- | --- |
| Scoring | 62 | 0 | 15 | 15 | 7 | 25 fresh |
| Tiebreaker reserve | 6 | 0 | 0 | 0 | 0 | 6 standby TB-A / TB-B2 |
| INVALID analyses | 12 | 6 | 4 | 0 | 2 | 0 |
| Prep research | 31 | 12 | 6 | 4 | 3 | 6 live-only |
| Review | 35 | 9 | 2 | 4 | 1 | 19 coordinator |
| Total | 146 | 27 | 27 | 23 | 13 | 56 |

How the mei scoring deficit redistributes: mei ideal scoring share at full-pool ratios would be about 18 WU of the 62 scoring assignments. She takes 0 by disqualification. The deficit moves in two steps. First, clone2, mochi, and clone1 absorb scoring up to their calibrated capacity (15, 15, 7). Second, fresh sessions absorb the rest (25). Mei reaches her full share of 27 WU entirely from non-scoring work: 6 INVALID, 12 prep, 9 review. The non-scoring pool is 78 WU (12 plus 31 plus 35), large enough for mei to reach 27 without scoring. No rule change is needed. Lifting mei disqualification would need an explicit owner decision and is not recommended. See section 10.

Mochi existing seat counts toward her share: her 15 scoring WU include 6 pre-committed Pair A scorer 1 assignments (R3-027, R3-028, R3-029, R3-035, R3-036, R3-037) plus 9 Pair B overflow assignments as scorer 1 on whole tasks. In-flight R3-025 fresh scoring and R3-026 scoring already assigned to mochi are not in the 31-task pool and do not change the quotas above. The coordinator counts them as load for scheduling, not as quota credit, so mochi is not double charged for pause close-out work.

Clone1 watchdog duty continues through the re-plan and is not counted in WU. Clone1 quota of 13 WU assumes the 10-minute watchdog stays. If watchdog load spikes, clone1 prep units move to fresh first, scoring units move last.

Mei tranches, per clone2 input: mei work releases in two tranches. Tranche 1, during the pause: R3-026 INVALID analysis lead (2 WU), prep for the next 6 tasks in order (R3-027 through R3-037, 6 WU), scorer-2 supervision for session dc7e0d0d, run tally. Tranche 2, released when the task-56 coord entry closes and the Cloudflare fix is proven live: remaining prep (6 WU), remaining INVALID analyses (4 WU), review and closure drafting (9 WU). Mei replied at 04:36 and is responsive. The tranche split protects the run if she stalls again without penalizing her share. If tranche 2 is late by more than one milestone, prep units move to clone2 and review units move to the coordinator, and mei quota rebalances at closure with a written note. No silent reassignment.

Why fresh sessions keep 25 scoring assignments, 6 tiebreaker WU, 6 live prep units, and 19 review units:

- Parallelism and backpressure. Driving is serialized, one driver at a time, with max 2 unscored per runner. Class L tasks need both verdicts before reset while the runner waits. Four single-threaded chats cannot cover 62 scorings inside 30-minute targets without stalling drivers. Fresh sessions spawn per task in parallel with driving, the pattern already proven for 29 graded tasks.
- Context and compaction limits. Mochi reports 350k context, 39 percent used, 212k free, compacted once, verdicts on disk. Clone1 and clone2 report fresh weekly budgets but no exact figure. Mei works via bounded subagent lanes with file handoffs. Fresh sessions start clean per task and carry no cross-task key exposure, which protects blindness.
- Independence. Fresh scorer 2 sessions have no prep or analysis history on the task. Named Muses accumulate history. Keeping about 40 percent of scoring with fresh sessions limits correlated error and gives the tiebreaker a clean pool.
- Live access. The four Muses have no SSH. Live prep and VM-local audit steps cannot move to them.

Fresh scoring assignments are not unsupervised. Each fresh session gets the scorer brief plus R3-L3 addendum, files a written independence declaration (no list authorship, no key authorship, no task run, no preflight trial, no runner code), reads only the sealed snapshot plus the frozen key section for the assigned task, and returns one verdict json plus one grade markdown file. The coordinator audits every verdict before the ledger write. The calibration sessions dc7e0d0d, 4e2f52d4, 2e3ae678 completed and cannot resume. Run sessions are fresh spawns briefed identically, the pattern recorded in the state file at run start. TB-A 97290681 and TB-B2 df4defcc stay on standby and are spawned on demand with updated IDs recorded then.

## 5. Scorer pairing design

Fixed pairings per task. Nobody scores a task they prepped or analyzed. Nobody reviews key or list content for a task they still have to score. The coordinator enforces an allowlist per assignment: sealed snapshot files for the assigned task plus the frozen key section for that task only. Key hashes json 5059f6c4 and md 21f8b61a are verified and recorded in every grade file.

Pair A, 6 tasks. Scorer 1 is mochi session 70cd99d1 for all 6. Scorer 2 rotates:

| Task | Scorer 1 (1A) | Scorer 2 (2A) | Note |
| --- | --- | --- | --- |
| R3-027 | Mochi | Clone2 | FCC drive |
| R3-028 | Mochi | Fresh A2 | INVALID candidate. Clone2 analyzes cause, does not score. |
| R3-029 | Mochi | Clone2 | Password in brief only, never in snapshot or file. |
| R3-035 | Mochi | Clone2 |  |
| R3-036 | Mochi | Fresh A2 | INVALID candidate. Clone2 analyzes cause, does not score. |
| R3-037 | Mochi | Clone1 | FCC drive. Clone1 first real grade after calibration. |

Pair B, 25 tasks including task 56. Pairings are fixed in advance. Class L tasks always include at least one named fast scorer (mochi or clone2) so score-before-reset does not wait on two fresh spawns.

| Task | Class | Scorer 1 (1B) | Scorer 2 (2B) |
| --- | --- | --- | --- |
| R3-045 | S | Clone2 | Fresh |
| R3-046 | S | Fresh | Fresh | INVALID candidate. Mei leads analysis, clone2 second. Neither scores. |
| DP-03 | S | Clone2 | Fresh |
| R3-049 | S | Mochi | Fresh |
| R3-055 | L | Mochi | Clone2 |
| R3-067 | S | Mochi | Fresh |
| R3-072 | S | Fresh | Clone1 |
| R3-074 | L | Clone2 | Fresh |
| R3-075 | L | Mochi | Clone2 |
| R3-076 | S | Fresh | Clone1 |
| R3-078 | L | Clone2 | Fresh |
| R3-079 | L | Fresh | Clone2 |
| R3-082 | S | Clone1 | Fresh |
| R3-083 | S | Fresh | Clone1 |
| R3-085 | S | Mochi | Fresh |
| R3-086 | S | Fresh | Fresh |
| R3-088 | L | Clone2 | Fresh |
| R3-089 | L | Mochi | Clone2 |
| R3-093 | S | Fresh | Clone1 |
| R3-094 | S | Clone1 | Fresh |
| R3-096 | L | Mochi | Fresh |
| R3-098 | S | Fresh | Clone2 |
| R3-099 | S | Clone2 | Fresh |
| R3-100 | S | Mochi | Fresh |
| Task 56 | L | Mochi | Clone2 |

Counts check: Pair B mochi 9, clone2 12, clone1 6, fresh 23. Pair A mochi 6, clone2 3, clone1 1, fresh 2. Totals mochi 15, clone2 15, clone1 7, fresh 25. Matches section 4.

Calibration gate for clone1 and clone2. Neither grades a real task until calibrated 4 of 4 with independent verification. Calibration set: R3-041 PASS, R3-002 FAIL, R3-003 FAIL, R3-067 PASS, graded blind from sealed snapshots plus frozen keys, the same set used for TB-B2. The verifier is a fresh independent session, not mei, not mochi, not the coordinator alone, and not the candidate. The verifier re-grades all 4 cases from scratch and signs off in a file. If a candidate scores 3 of 4 or less, the candidate does not grade real tasks. One re-calibration with a held-out set is allowed during the pause. If the second calibration fails, fresh sessions fill that candidate quota, ratios rebalance at the next milestone, and the owner is notified. Calibration work is a gate, not quota credit. Mochi needs no new calibration. She is the established scorer 1 with 29 tasks graded. Fresh per-task sessions follow the existing brief plus declaration pattern and are audited per verdict. Any fresh session that fails audit twice is retired and replaced.

Blindness rules, hard:

- No prep-then-score on the same task. Prep assignments in section 4 are disjoint from scoring assignments per task. The coordinator checks the prep log before releasing a scoring assignment.
- No analysis-then-score on the same task. INVALID analysts for a task do not score that task. This is why R3-028, R3-036, and R3-046 scorers exclude their analysts in the tables above.
- Mochi key and list review ban for unscored tasks. Mochi may review key or list content only for tasks she has already scored or tasks she will never score. She must never score a task she prepped or analyzed, never run tasks or runner code, and never do preflight trials. The same ban applies to clone1 and clone2 for tasks in their scoring blocks.
- Mei blindness in reverse. Mei authored the 100-task list and keys and is disqualified as scorer. She does not read ledgers or snapshots. Her INVALID analysis uses commit messages, the frozen key and list, and coordinator reports only. She supervises scorer-2 session dc7e0d0d only. Changing either mei rule needs an explicit owner decision.
- Verdict independence. Scorers work blind to each other. Neither scorer reads the other verdict, the Tier A output beyond what the coordinator hands identically to both, the live evidence dir, or the runner log beyond the sealed snapshot. Disagreement goes to the tiebreaker. The coordinator does not pass fabrication judgments or cause judgments to scorers.

Snapshot delivery path, PII-safe, defined so epoch 8 can execute without questions:

1. Coordinator seals the snapshot locally at ~/workspace/rung3-snapshots/R3-xxx-L3/ and runs the manifest gate.
2. Coordinator runs a PII scan before any push: gitleaks on the snapshot dir plus manual check for passwords, tokens, personal emails, and owner tab URLs beyond what the task requires. R3-029 test account password never enters the snapshot, the evidence dir, or any file. Task 56 tab URLs are owner data. Task 56 snapshot stays VM-local plus coordinator live verification note. It is not pushed with full URLs unless the owner approves. Scorers for task 56 grade from the VM-local snapshot plus the live verification note, with URLs redacted to host plus path pattern where the key allows. If redaction would break grading, the coordinator asks the owner before pushing. Default is no push of task 56 URLs.
3. Coordinator pushes the snapshot to todolist-push under rung3-run-log/rung3-snapshots/R3-xxx-L3/ and verifies with ls-remote. The gitleaks gate on main must pass. A failed gate stops the push. The snapshot does not move by chat.
4. Scorer pulls the snapshot, grades, and returns verdicts on a per-scorer branch named <name>/verdict-R3-xxx-L3 with exactly two files: verdict json and grade markdown. Verdict values stay in files, not in chat. The scorer notifies the coordinator with task ID plus branch plus file paths only.
5. Coordinator pulls, audits, copies verdicts to ~/workspace/rung3-verdicts/, cross-checks, and writes the ledger row. The ledger row records both scorer sessions, both verdicts, key hashes, manifest hash, and timestamps.

Tiebreaker counting: each tiebreaker is 2 WU to the standby pool. TB-A 97290681 covers Pair A. TB-B2 df4defcc covers Pair B. The tiebreaker must not have scored, prepped, or analyzed the task. The tiebreaker grade is the final grade. The ledger records all three verdicts. If TB-A or TB-B2 is unavailable, the coordinator spawns a fresh tiebreaker under the same calibration gate (4 of 4, independent verification) before grading.

Scorer-1 rotation contingency: mochi flagged that if load grows a lot, plan scorer-1 rotation. Trigger: mochi unscored queue at 2 for more than 60 minutes, or mochi context above 80 percent, or two consecutive 60-minute hard-limit breaches. Action: clone2, once calibrated, takes Pair A scorer 1 for the next 2 tasks as whole tasks, mochi rests, fresh A2 continues. Rotation is recorded in the state file with session IDs. Mochi never scores a task she prepped during rotation cover. Rotation does not change quotas unless it lasts beyond 2 tasks, in which case quotas rebalance at the next milestone.

## 6. Driving split confirmation

Driving is non-movable. The four Muses do not drive. One driver at a time on shared Zen on ws2. Backpressure max 2 unscored per runner lane. Class L runner waits for both verdicts. Class S runner proceeds after the snapshot gate.

| Lane | Tasks (remaining after in-flight) | Count | Method |
| --- | --- | --- | --- |
| FCC | R3-027, R3-037 | 2 | tmux r3-fcc-runner-L3 pane PID 22399, easiest tasks only, no coaching |
| Muse subagents | R3-028, R3-029, R3-035, R3-036, plus task 56 default | 4 plus 1 | Fresh independent Muse subagent per task, SSH via ~/workspace/ssh-laptop.sh, Zen via computer-use with pill visible, lane brief plus task only |
| Codex | R3-045, R3-046, DP-03, R3-049, R3-055, R3-067, R3-072, R3-074, R3-075, R3-076, R3-078, R3-079, R3-082, R3-083, R3-085, R3-086, R3-088, R3-089, R3-093, R3-094, R3-096, R3-098, R3-099, R3-100 | 24 | codex exec per task from /home/james, -m gpt-6-luna --sandbox danger-full-access --skip-git-repo-check, Hyprland env exported |

Task 56 runner: Muse fresh independent subagent by default. Codex is the approved alternative if the Muse runner fails twice on task 56. Opencode cannot run task 56 or any remaining task. The opencode DeepSeek route reached end of life on 2026-11-16 and the owner rule allows opencode only via the opencode provider (opencode/ prefix), never NVIDIA, Groq, or OpenRouter. Do not assign opencode. Do not retry opencode routes.

Order: frozen order R3-027 onward, no reordering mid-run. Task 56 last, after R3-100. R3-029 password is held by the parent and passed in the R3-029 task brief at release, never in a file. The parent re-verifies with the owner before position 25 (R3-029). R3-089 fixture refresh is owned by the run coordinator, refreshed the day before R3-089 runs. The 21:31 tab-close standing rule and the M2 end-of-drive self-check stay in every runner brief. Never close or navigate owner-opened tabs. Open a new tab beside owner tabs when a browser is needed.

Ponytail rule for all code work, restated in every runner and scorer brief that involves code: smallest complete change, reuse what exists before writing, standard library and platform before new dependencies, no unrequested abstraction or for-later code, one small test for non-trivial logic, never cut validation, security, or error handling. Skill at ~/workspace/custom-skills/ponytail/SKILL.md. This applies to R3-074, R3-075, R3-076, R3-086, R3-094, R3-098, R3-099, R3-100, DP-05 if used, and the task 56 sessionstore extraction script. Ponytail does not change task keys or pass criteria. It governs how runner code is written, not what counts as PASS.

## 7. Invalid handling under the new split, including R3-026

Who analyzes, who decides:

1. Scorers decide PASS, FAIL, or INVALID from the sealed snapshot plus frozen key, blind and independent. Both scorers must agree, or the tiebreaker decides. INVALID means the task cannot be graded because the service or environment blocked the runner, proven by browser evidence in the snapshot. Runner failure, fabrication, missing evidence, and wrong answers are FAIL, not INVALID.
2. Mei leads INVALID analysis and triage from commit messages, the frozen key and list, and coordinator reports. She does not read ledgers or snapshots and does not override scorers. Her analysis covers cause grouping, difficulty group, backup mapping, and cap accounting.
3. Clone2 is second analyst for tasks he does not score. Clone1 takes one analysis. Mochi analyzes only tasks she does not score. Analyst assignments: R3-026 mei lead plus clone2 second (mochi scores R3-026, so mochi does not analyze it). R3-028 mei lead plus clone2 second. R3-036 mei lead plus clone2 second. R3-046 mei lead plus clone2 second. Unplanned analyses rotate mei lead, clone2 or clone1 second, excluding scorers of that task. Totals match section 4: mei 3 analyses (6 WU), clone2 2 analyses (4 WU), clone1 1 analysis (2 WU). The 6th analysis in the pool is the second unplanned slot. If R3-028, R3-036, and R3-046 share one proven cause, the cause proof is written once and confirmed twice. WU still counts per task for cap accounting, but the coordinator records the shared proof file so the work is not triple written.
4. Coordinator countersigns the INVALID decision, records the backup mapping or drop in du-phong.txt and the state file, updates invalid counters by group, and notifies the owner at the points below. The coordinator does not grade and does not pass cause judgments to scorers before they grade.

R3-026 ruling required by the 04:40 update:

- Difficulty group: medium (trung binh), browser group, Tier B. Source: docs/rung3-list-100-tasks.md line 452, R3-026 coolors.co palette task, do kho trung binh. Class S.
- Evidence: Cloudflare Just a moment on coolors.co homepage, Ray ID a603c518ed7945df, 60-second wait, still blocked, 1 timestamped block screenshot, ket-qua.txt records palettes NOT OBTAINED. This meets the browser evidence standard if both scorers agree from the snapshot. Curl alone would not suffice. The snapshot has browser evidence.
- Shared-incident counting: R3-026 does NOT share the single-incident counting with R3-011 or R3-024 under the du-phong.txt ruling as written. The ruling covers 1 proven shared service incident, written for the timeanddate group R3-011, R3-028, R3-036, R3-046 (same site, same cause). R3-011 is timeanddate.com Cloudflare. R3-024 is Openverse search Cloudflare. R3-026 is coolors.co Cloudflare. Same vendor, different services, different Ray IDs, different times. That is a shared browser environment pattern, not one service incident. The council counts R3-026 as a separate invalid event. Merging cross-site Cloudflare blocks into one event would need an explicit owner decision to extend the ruling. The council does not recommend merging without owner approval, because merging would hide the Zen-AI root cause the Cloudflare fix workstream must prove. See section 10.
- Cap impact if graded INVALID: total invalids 4 of 5. Medium invalids 3, over the per-group cap of 2. Hard stays 1 of 2. Epoch 8 recorded the same warning at 04:38:26. The run is already paused. The over-cap consequence is an owner decision point, not an automatic stop. Council recommendation: drop R3-026 from the sample, recompute the bar, notify the owner, do not stop. Alternative owner options are waive the per-group cap for this run or stop the run. The council recommends drop and recompute because the pre-declared B-F4 pattern already handles sample shrinkage by recomputing the bar to N minus 2 and continuing.
- Backup availability: no medium backup remains. DP-06 and DP-07 are used. DP-03 is position 34 in the frozen 55 and is not available as a spare. DP-05 is very hard tier and cannot replace a medium task without breaking tier balance. DP-02 is hard tier and already used. A medium invalid now drops from the sample. DP-05 stays reserved for a very hard invalid only. Using DP-05 for a medium task needs an explicit owner decision and is not recommended.
- Bar-math impact if R3-026 drops: valid original set 55 minus 1 equals 54. Bar recomputes to 52 of 54 (N minus 2 pattern, matching epoch 8 note). Passes already banked under rule A: 23. Remaining valid positions to grade: R3-025 fresh plus 30 remaining equals 31. Need 52 minus 23 equals 29 more PASS. Slack 2 fails. With task 56: valid 55, bar 53 of 55, need 30 more PASS from 32 positions (31 plus task 56), slack 2 fails. Closure still counts both ways with the recomputed bars stated plainly. The original 53 of 55 bar is reported as superseded by the drop, not hidden.

Backup exhaustion path for remaining tasks:

- R3-028, R3-036, R3-046: if they go INVALID with the proven timeanddate shared cause, they count as the same 1 event already counted for R3-011 for both caps. They add 0 new cap events. Each task still needs a same-difficulty backup to stay in the sample. No medium backup remains, so each drops. Valid falls by 1 per drop. Bar recomputes to N minus 2 each time. If all 3 drop after R3-026 drops: valid original 51, bar 49 of 51, need 26 more PASS from 28 remaining valid positions, slack 2. With task 56: valid 52, bar 50 of 52, need 27 from 29, slack 2. B-F4 trigger at valid 53 is crossed on the way down. The coordinator notifies the owner at valid 53 and at each further drop, and does not stop, per B-F4.
- Unplanned invalids: hard tasks can use no backup (DP-02 used). Very hard tasks can use DP-05 once. Medium tasks drop. Easy tasks drop (no easy backup in the table). Each drop recomputes the bar to N minus 2. Slack stays 2 fails as long as drops are the only shrinkage. Each FAIL consumes slack. Two fails plus any drops still leaves the bar reachable. Three fails makes the bar unreachable under any drop scenario. At 3 fails under rule A, the coordinator notifies the owner and asks whether to continue for data, as the owner directed earlier in the run. The council does not pre-authorize continuing past an unreachable bar.
- Stop-and-ask floor: if valid falls below 50, the sample is too small to claim a 53-bar equivalent with a straight face. The coordinator pauses releases and asks the owner. This floor is a council recommendation for owner confirmation. It does not override B-F4 do-not-stop at valid 53. It adds a lower bound where continuing without owner input would mislead closure.

Owner notification points for invalids, via parent, with ledger evidence:

- Invalid 3: already passed (R3-024). Recorded.
- Invalid 4: R3-026 if graded INVALID. Notify immediately with difficulty group, cap counts (total 4 of 5, medium 3 over cap 2), backup result (drop), and recomputed bars (52 of 54 and 53 of 55 with task 56).
- Invalid 5: cap reached. Notify immediately. Any 6th invalid event needs owner approval to continue.
- Per-group cap breach: notify at the breach (R3-026 medium breach is the first).
- Valid falls to 53: B-F4 recompute to 51 of 53 (or the equivalent with task 56 stated both ways), notify, do not stop.
- Each further drop below 53: notify with new N and new bar.
- DP-05 use or exhaustion: notify before DP-05 drives, not after.
- Shared-cause proof for R3-028, R3-036, R3-046: notify when the proof is filed, with the proof file path.

## 8. Sequencing with the Cloudflare fix, to the very end

Another council member owns the Zen-AI Cloudflare fix workstream. This council owns only sequencing impact. The fix is not designed here.

Phase 0, pause close-out, epoch 8: finish R3-026 scoring and ledger row (PASS, FAIL, or INVALID as graded), finish R3-025 fresh drive, seal, score, and ONE ledger row, push ledgers, record the pause point in the state file, then hold. No new releases, no new runners, no new scorers beyond in-flight. R3-027 does not release in Phase 0.

Phase 1, Cloudflare fix, whole team, proven live: nothing in the run resumes during Phase 1. Proven live means, at minimum, chatgpt.com, coolors.co, timeanddate.com, and Openverse search load in Zen on ws2 without Just a moment or Verify you are human blocks, with the pill visible during driving, navigator.webdriver false, on 3 consecutive loads each, with screenshots and Ray ID absence recorded. The fix workstream defines the exact proof. This council requires only that the proof covers the 4 sites that produced invalids or blocks in this run, because resuming on a chatgpt.com-only proof would leave R3-028, R3-036, and R3-046 exposed to the same timeanddate block. If the fix changes the Zen launcher, wrapper, prefs, or session, the fix workstream must also prove owner tabs, pinned tabs, and essentials survive, and that no owner tab is closed. Task 56 restoration does not happen in Phase 1.

Phase 2, calibration and readiness, during the pause, after or parallel with Phase 1 but before resume: clone1 and clone2 calibration (4 of 4, independent verification), PII-safe snapshot path test on one already-scored snapshot (push, pull, verdict branch, audit, no PII leak, gitleaks pass), mei tranche 1 (R3-026 analysis, prep for R3-027 through R3-037, tally), R3-029 password re-verification with the owner via parent, R3-089 fixture refresh scheduling. No task drives in Phase 2.

Phase 3, owner approval to resume: the parent sends the owner-approved new plan (this design as amended by council plus redteam plus owner decisions in section 10) to epoch 8. Epoch 8 records the approval, the recomputed bars if R3-026 dropped, and the calibrated scorer list in the state file before releasing R3-027. Resume without owner approval is prohibited.

Phase 4, remaining positions in frozen order: R3-027 through R3-100 in thu-tu-chay.txt order, one driver at a time, backpressure 2, Class L score-before-reset, milestone rebalancing after every 8 graded tasks (WU actuals vs targets, invalid counters, bar reachability). Task 56 last, after R3-100, Class L, leave restored tabs live, coordinator verifies against live tab list plus sessionstore before scoring closes. No reset exists for task 56.

Phase 5, closure: ledger validation, cross-check, both-ways count (original set bar as recomputed for drops, and with task 56), original FAIL rows plus rule-A supersede stated plainly, invalid list with cause proofs and backup mapping, per-task cycle times, final report draft by mei (review units), independent closure audit by clone2 or fresh auditor who did not draft the report. Council plus redteam review the closure package before it goes to the owner, per the owner rule that the team reconvenes until all agree. Cleanup after use: close leftover task tabs, kill dead executors, verify pill gone, desktop clean. Never touch owner tabs, music, or the cancel latch.

Time note: the pre-run estimate was 19 to 31 hours staffed for 55 tasks. At pause, 29 graded tasks are done. Remaining 31 tasks plus task 56 close-out, calibration, and the Cloudflare fix will take longer than a simple pro-rata slice because Class L tasks cluster in Pair B and invalid handling adds analysis time. The coordinator tracks Class L and Class S cycle times separately and reports a revised run-complete estimate at each milestone. The council does not promise a wall-clock finish time.

## 9. Risks in this design and mitigations

- Risk: clone1 or clone2 fails calibration. Mitigation: calibration during pause, one re-calibration allowed, fresh fills quota on second failure, owner notified, ratios rebalance. No uncalibrated grading.
- Risk: mochi overload as Pair A scorer 1 plus Pair B overflow. Mitigation: 30-minute target, 60-minute hard limit, backpressure 2, rotation trigger in section 5, verdicts on disk so compaction does not lose grades. Mochi share is 15 scoring assignments over 31 tasks, about 1 per 2 tasks, not every task.
- Risk: mei stall on tranche 2. Mitigation: tranche split, milestone check, prep moves to clone2 and review to coordinator if late, written rebalance note. Mei already replied at 04:36. Clone2 stall flag from 02:32 is stale and is not held against her share.
- Risk: blindness break by prep or analysis history. Mitigation: disjoint assignments per task in fixed tables, allowlist per assignment, coordinator prep-log check before scoring release, key review ban for unscored tasks. Any break voids that verdict and the task is re-scored by a clean scorer. The void is recorded, not hidden.
- Risk: PII leak via snapshot push, especially R3-029 credentials and task 56 owner tab URLs. Mitigation: PII scan plus gitleaks gate before push, password never in files, task 56 snapshot VM-local by default, owner approval before any task 56 URL push. A failed gate stops the push.
- Risk: Cloudflare fix proven on chatgpt.com only, then timeanddate blocks again at R3-028. Mitigation: Phase 1 proof must cover coolors.co, timeanddate.com, and Openverse as well as chatgpt.com. Resume gate checks all 4.
- Risk: invalid cascade exhausts backups and shrinks the sample below a credible bar. Mitigation: drop-and-recompute to N minus 2, owner notification at valid 53 and each drop, stop-and-ask floor at valid below 50, DP-05 reserved for very hard only. Slack stays 2 fails under drops alone, so the bar stays reachable unless fails accumulate.
- Risk: FCC fabrication repeats on R3-027 or R3-037. Mitigation: FCC gets only 2 easiest remaining tasks, manifest gate plus Tier A checker where applicable, seal as-is and score after 3 gate failures per precedent, no coaching of key values. FCC fabrication history (R3-001, R3-002, R3-003) is the reason FCC share stays at 2.
- Risk: Codex lane stalls on Class L live checks. Mitigation: codex exec per task with Hyprland env exported, one invocation per task, 30-minute timeout enforced by coordinator, Class L prep live units assigned to coordinator so the runner brief includes the live capture plan. Codex already graded R3-040, R3-041, R3-042 PASS early, so the lane is proven.
- Risk: ratio drift as tiebreakers and extra invalids accumulate. Mitigation: milestone rebalancing after every 8 graded tasks, WU actuals tracked in the state file, next prep or review unit goes to the person furthest below target. Ratios are targets with whole-unit rounding, not per-task quotas.
- Risk: snapshot delivery delay stalls Class L scoring while the runner waits. Mitigation: Class L snapshots seal locally first, coordinator live verification note travels with the assignment, repo push follows for the record. Scorers grade from the sealed snapshot. The runner does not wait for the push, only for both verdicts.

## 10. Decisions only the owner can make

The council recommends a default for each. Epoch 8 executes the default unless the owner decides otherwise. Items marked BLOCKING must be decided before resume. Others can be decided at the milestone where they arise, with the default holding until then.

1. BLOCKING. Ratio pinning: clone1 equals half of a full share (clone2 and mei share). Default: yes, weights 100, 100, 85, 50 as in section 4. Alternative is half of the average of the other three (47.5). Owner confirms.
2. BLOCKING. Resume after Cloudflare fix: owner approves resume only after the fix is proven live per Phase 1. Default: no resume without explicit owner approval. Owner confirms the proof standard or amends it.
3. BLOCKING if R3-026 grades INVALID. Per-group cap breach (medium 3 over cap 2): drop R3-026 and recompute bars to 52 of 54 and 53 of 55 with task 56, notify, do not stop. Default: drop and recompute. Alternatives: waive the per-group cap for this run, or stop the run. Owner decides.
4. Cross-site Cloudflare shared-incident merge: count R3-011, R3-024, R3-026 as separate events. Default: separate. Merging needs owner approval to extend du-phong.txt beyond the timeanddate group. Owner decides if a merge is ever proposed.
5. DP-05 tier mismatch: DP-05 (very hard) does not replace medium or hard invalids. Default: no mismatch use. Owner decides if a mismatch is ever proposed.
6. Mei disqualification and ledger ban: mei scores zero and does not read ledgers or snapshots. Default: both rules stand. Lifting either needs explicit owner decision. Council recommends no lift. Owner decides.
7. Task 56 runner fallback: Muse default, Codex if Muse fails twice. Default: as stated. Owner confirms. Opencode is excluded in all cases.
8. Task 56 snapshot push: VM-local by default, no owner tab URLs pushed without approval. Default: no push. Owner decides if a push is needed for grading.
9. Valid floor: pause and ask if valid falls below 50. Default: floor at 50. Owner confirms or sets a different floor. B-F4 do-not-stop at valid 53 stands regardless.
10. Calibration failure fallback: fresh fills quota, ratios rebalance, owner notified. Default: as stated. Owner confirms.

## 11. Execution checklist for epoch 8

Epoch 8 executes in this order. No step needs a question to the council. Owner decisions in section 10 are the only gates.

1. Finish Phase 0 close-out. Record R3-026 grade and R3-025 fresh grade. Push ledgers. Record pause point. Hold.
2. File mei tranche 1 assignments: R3-026 INVALID analysis lead, prep R3-027 through R3-037, tally. Record WU actuals starting at 0 for the 31-task pool.
3. Run clone1 and clone2 calibration. File verifier sign-offs. Record calibrated list or fallback.
4. Test PII-safe snapshot path on one scored snapshot. Record gitleaks result.
5. Wait for Cloudflare fix proof (Phase 1) and owner resume approval (Phase 3). Do not release R3-027 before both.
6. On resume approval, record recomputed bars, calibrated scorers, pairing tables from section 5, and driving split from section 6 in the state file. Release R3-027 to FCC.
7. Drive in frozen order. One driver at a time. Backpressure 2. Class L score-before-reset. Ponytail in every code brief. Tab-close rule in every runner brief.
8. Score per fixed pairings. Audit every verdict pair. Ledger write only after audit pass. Tiebreakers to TB-A and TB-B2.
9. Invalid handling per section 7. Notify owner via parent at invalid 4, invalid 5, cap breach, valid 53, each drop, DP-05 use.
10. Milestone rebalance after every 8 graded tasks. Move next prep or review unit to the person furthest below WU target. Record actuals.
11. Task 56 last. Muse runner default. Leave tabs live. Coordinator live verification before scoring closes.
12. Closure both ways. Independent audit. Council plus redteam reconvene until all agree. Cleanup after use.

End of verdict.
