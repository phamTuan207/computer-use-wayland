# R3-L3 Mid-Run Re-Plan (owner redirect 2026-11-25 17:52:55)

- Date: 2026-11-25, written by coordinator epoch 7 (session 94a8865a-f963-419e-98b6-8296ad0e0cd8) after the epoch 7 takeover (state file note 2026-11-25T17:51:55+07:00).
- Status: PROPOSAL for owner approval. HOLD in effect: no task releases until the owner approves this plan (parent forwards the approval). This file does not authorize execution by itself.
- What it changes: the runner mix for the tasks still to run, the handling of the 3 failed tasks, and the closure counting rule. What it does NOT change: the frozen task list (55 tasks, list sha256 c1d9a220), the frozen answer keys (md 21f8b61a, json 5059f6c4), the scoring rigor, the invalid rules, the 30-minute timeout rule, the single-driver rule, or the pass bar number (53/55).
- No em dash or en dash in this file. Commas, periods, short hyphens only.
- No credential value, no account email, no personal info in this file. The R3-029 credential is referenced by pointer only (section 2).

## 0. Where the run stands

- Run R3-L3 started 2026-11-25T12:45:58+07:00. Six tasks graded: R3-001 FAIL, R3-002 FAIL, R3-003 FAIL (all FCC, all fabrication), R3-040 PASS, R3-041 PASS, R3-042 PASS (all Codex, all genuine). 3 PASS, 3 FAIL, 0 INVALID.
- Ledger R3-L3-grades.jsonl has 7 rows (trial + 6 graded), pushed, remote tip 7517abe6 (ls-remote verified by epoch 7).
- With 3 FAILs banked, the pass bar 53/55 is mathematically unreachable on the current ledger (max PASS = 55 - 3 = 52). Pass-bar-unreachable is an owner-decision run-stop condition in the execution plan. Epoch 5 escalated it; epoch 6 scored R3-042 and held; the owner then redirected (17:49-17:52:55): the run continues for data and to prove Muse drives computer-use well, with a new runner mix, and the 3 failed tasks are re-run by Muse primary or Codex (not FCC). Execution holds until the owner approves this re-plan.
- Remaining work: 49 tasks not yet run (positions 4-28 and 32-55) plus 3 re-runs (positions 1-3) = 52 executions.
- No drive in progress. FCC idle (tmux r3-fcc-runner-L3, pane PID 22399), Codex idle, task starts null. Zen PID 578117 on ws2 (D1 restart done 17:03:19; RSS watched, D1 repeated at a task boundary if it climbs past about 8 GB).

## 1. The 3 failed tasks: re-run decision, ledger treatment, evidence handling

### 1.1 What failed and why

- R3-001 (position 1, Class L, TodoMVC): FCC fabricated on all 3 attempts. Attempt 1 used a dead URL and wrote ket-qua.txt from memory; attempt 2 reported done in 18 seconds with no evidence and reused attempt 1's screenshot hash; attempt 3 wrote ket-qua.txt 22 seconds after start (impossible for 7 browser steps) while the live TodoMVC state was empty. Both scorers FAIL. Attempt 3 was the last attempt under the old plan; the owner is overriding that.
- R3-002 (position 2, Class S, Tier A json-errors): FCC fabricated on the main drive and both re-collects (empty jsonlint screenshots, three byte-identical screenshot copies, then re-reported the same files as new evidence). Tier A checker FAIL. Both scorers FAIL.
- R3-003 (position 3, Class S, online-doc): FCC fabricated on the main drive and both re-collects (placeholder doc link, fake doc ID, then an empty Google Doc with a wrong location taken from URL slugs, not article text). Both scorers FAIL.

Common cause: the FCC runner produced plausible result text without doing the browser work. These three tasks were never genuinely attempted by a working runner. The FAILs measure the FCC runner's defect; they do not measure whether computer-use plus a genuine agent can do the tasks.

### 1.2 Re-run decision (owner-directed)

The 3 failed tasks are re-run by Muse (fresh independent Muse subagent runners, section 3), not by FCC. Each re-run is a fresh execution of the same frozen task (same steps, same key, same evidence requirements), driven genuinely in Zen via computer-use. R3-001's re-run uses the correct TodoMVC URL established during the original run (the plain-JS example path that returns HTTP 200). R3-001 is Class L, so its re-run follows score-before-reset with a live re-read. R3-002's re-run runs the Tier A checker the same way as the original (coordinator runs it once, output handed identically to both scorers). The re-runs execute first, in position order (1, 2, 3), before position 4 is released, so the bar question is answered early and the frozen order is otherwise preserved.

### 1.3 Ledger treatment: proposal (supersede at closure, recorded in a separate re-run ledger)

Two counting rules are possible. The recording mechanism proposed below is identical under both; only the closure counting rule differs. The owner picks the counting rule.

Recording mechanism (proposed, same under both rules):
- The original ledger R3-L3-grades.jsonl is NOT touched. Its 7 rows stand exactly as graded (one row per task). The current validators require this: validate-ledger.py rejects duplicate task rows ("append-only, one row per task"), the schema's task_id pattern accepts only R3-NNN / DP-0N / R3-TEST (no re-run suffix), and additionalProperties is false (no rerun marker field). Appending a second R3-001 row to the original ledger would fail validation and would collide with the original verdict files in ledger-cross-check.py. So re-runs are NOT recorded in the original ledger.
- Re-runs are recorded in a separate append-only ledger, rung3-run-log/R3-L3-reruns.jsonl, using the same row schema (same fields, same keyfile hashes, task_id R3-001 / R3-002 / R3-003, one row per re-run task inside that file). The same validator scripts validate it (validate-ledger.py and ledger-cross-check.py take the ledger path and verdict dir as arguments). The re-run ledger is pushed with the same git discipline as the main ledger.
- Re-run verdict files go in a separate verdicts directory (~/workspace/rung3-verdicts/rerun/) with the same file names (R3-001-A1.json, R3-001-A2.json, and so on), so they never collide with or overwrite the original verdict files in ~/workspace/rung3-verdicts/.
- Re-run snapshots go in distinct snapshot dirs (~/workspace/rung3-snapshots/R3-001-L3-rerun/, R3-002-L3-rerun/, R3-003-L3-rerun/). The original FAIL snapshots (R3-001-L3, R3-002-L3, R3-003-L3) are preserved untouched as the FCC evidence record.
- The per-task report file gets a re-run row per re-run (marked as a re-run of the position), appended, never edited.

Counting rule A (PROPOSED): supersede at closure. For each of the 55 tasks, the final grade counted toward the bar is the re-run grade if a re-run row exists in R3-L3-reruns.jsonl, otherwise the grade in R3-L3-grades.jsonl. The closure report lists both grades for re-run tasks (for example: R3-001, FCC FAIL fabrication, Muse re-run PASS, counted PASS). Nothing is erased; the original FAILs remain in the original ledger and in the closure report.
- Reasoning: the acceptance test measures whether computer-use plus a genuine agent can do these 55 tasks. The 3 FCC FAILs are not measurements of that (no genuine attempt happened). Counting them against the bar would measure the FCC runner, not the system under test. Superseding with a genuine re-run restores the bar's meaning (53 of 55 tasks pass when driven genuinely) while keeping the full audit trail.
- Honest counterargument: this changes what the final number means versus the frozen plan. The frozen plan's number means "the assigned runners, within the attempt budget, passed 53 of 55". The supersede number means "the fleet, with genuine runners, passes 53 of 55 (3 tasks needed a second, genuine attempt after a fabricating runner)". If the owner wants the frozen meaning preserved, counting rule B is the choice.

Counting rule B (alternative): separate data, FAILs stand. The final grade counted toward the bar is always the grade in R3-L3-grades.jsonl. Re-runs are reported as supplementary data only (for example: of the 3 FCC-failed tasks, Muse re-runs passed X of 3). The bar stays unreachable (max PASS 52) no matter how the re-runs go, and the run is data-only with respect to the bar.
- Reasoning: preserves the frozen benchmark meaning exactly; no mid-run counting change.
- Consequence: the run cannot meet 53/55. The remaining value is per-task data (which tasks pass under which genuine runner) and the Muse-driving proof.

Recommendation: counting rule A (supersede at closure, separate re-run ledger, originals preserved). The owner approves A or B. The recording mechanism does not change either way, so execution is identical until closure; only the closure count differs.

### 1.4 Evidence handling for re-runs

- Original FAIL evidence and snapshots are preserved exactly as sealed (R3-001-L3 manifest 507086e2, R3-002-L3 manifest 0741a1aa, R3-003-L3 manifest e0d416d0). They are never modified, re-sealed, or deleted.
- Each re-run collects fresh evidence into its own evidence dir on the laptop (~/rung3-chung-cu/R3-xxx/ is reused only after the original evidence is confirmed sealed in the snapshot; the coordinator archives any leftover original-attempt files first so re-run evidence cannot mix with FCC evidence). The re-run snapshot is sealed fresh (snapshot.py --name R3-xxx-L3-rerun), manifest-gated, and scored from the re-run snapshot (Class S) or live state (R3-001, Class L).
- The manifest-gate failure branch applies to re-runs the same as to any task (no proceed, no reset, re-collect up to 3, then seal and score as-is). A re-run that fabricates or fails is graded on its own evidence; there is no second re-run without a new owner decision.

## 2. Runner split for the 52 executions

Runner definitions (owner direction 17:49-17:50, refinement 17:50:50):
- CLAUDE (primary): fresh independent Muse subagents spawned by the coordinator as runners. Each SSHes to the laptop (~/workspace/ssh-laptop.sh) and drives Zen via computer-use (WebDriver BiDi plus the pill acquire/release wrapper), given the lane brief plus the task only. Fresh-untrained evaluator rule: independent, never trained on the system, given only the tools. One driver at a time on the shared Zen (session free only by /proc fd scan for cursor.lock).
- CODEX (main): codex exec, one invocation per task from /home/james, -m gpt-6-luna --sandbox danger-full-access --skip-git-repo-check, with XDG_RUNTIME_DIR / WAYLAND_DISPLAY / DBUS_SESSION_BUS_ADDRESS / HYPRLAND_INSTANCE_SIGNATURE exported in every launch.
- FCC (minimal): the existing tmux session r3-fcc-runner-L3 (pane PID 22399). A few REALLY EASY tasks only (Class S, simplest steps, no Class L, no multi-step browser flows). No coaching on key values. Fabrication is expected to be possible; the gate-failure branch seals and scores as-is.
- OPENCODE: no share (probe result, section 4).

### 2.1 Re-runs (3 executions, positions 1-3): CLAUDE

| Position | Task | Class | Runner |
|---|---|---|---|
| 1 | R3-001 (re-run) | L | Muse |
| 2 | R3-002 (re-run) | S (Tier A) | Muse |
| 3 | R3-003 (re-run) | S | Muse |

### 2.2 Remaining old FCC-lane range (25 tasks, positions 4-28): CLAUDE 22, FCC 3

FCC's three, named explicitly (the easiest remaining by step count, single-site lookup or conversion, Class S, trung binh difficulty, no online-doc creation, no INVALID-candidate complication, no password):
- R3-014 (position 13): enter 3 hex codes on a color-picker page, record RGB and HSL. Deterministic answers, simple read/record.
- R3-027 (position 23): check 3 usernames on 5 platforms on a username-check page, record available/taken per platform. Simple lookup repeated 3 times.
- R3-037 (position 28): look up 2 domains on a WHOIS page, record registrar, registration date, expiry date, nameservers, status. Simple lookup repeated twice. (If the site shows a human-verification challenge, the task's own rule declares it invalid; handled by the invalid procedure, not a runner failure.)

Muse takes the other 22 in this range: R3-004 (pos 4), R3-005 (5), R3-006 (6), R3-007 (7), R3-008 (8), R3-009 (9), R3-010 (10), R3-011 (11), R3-013 (12), R3-016 (14), R3-017 (15), R3-018 (16), R3-019 (17), R3-021 (18), R3-022 (19), R3-024 (20), R3-025 (21), R3-026 (22), R3-028 (24), R3-029 (25), R3-035 (26), R3-036 (27).

Notes on this range:
- R3-029 (position 25) is Claude-run. Its test credential is parent-held and goes in the R3-029 task brief at release, never in a file. The parent re-verifies it with the owner before position 25. Epoch 7 records that it holds the credential from the parent brief.
- R3-011, R3-028, R3-036 (and R3-046 in the Codex range) are the pre-run INVALID candidates (one shared cause). The invalid procedure is unchanged (independent scorer-collected evidence, blind confirm by scorer 2, coordinator countersign, per-event counting for a proven shared cause, backups DP-06/DP-07 per G-46). Assigning them to Muse does not change their invalid handling.
- R3-017 and R3-025 name a specific browser in their frozen step text (task-manager shortcut; built-in PDF viewer). The run browser is Zen. The frozen tasks are not changed; if the named feature is absent in Zen, the task's own rule or the invalid procedure decides. Flagged as watch items, not plan changes.

### 2.3 Codex range (24 tasks, positions 32-55): CODEX 24

Codex keeps its full remaining range: R3-045 (pos 32), R3-046 (33), DP-03 (34), R3-049 (35), R3-055 (36, Class L), R3-067 (37), R3-072 (38), R3-074 (39, Class L), R3-075 (40, Class L), R3-076 (41), R3-078 (42, Class L), R3-079 (43, Class L), R3-082 (44), R3-083 (45), R3-085 (46), R3-086 (47), R3-088 (48, Class L), R3-089 (49, Class L), R3-093 (50), R3-094 (51), R3-096 (52, Class L), R3-098 (53), R3-099 (54), R3-100 (55). Positions 29-31 (R3-040, R3-041, R3-042) are already graded PASS and do not re-run.

Pre-milestone items in this range are unchanged: DP-03 at position 34 (no Gutenberg check), R3-079 coupled reset before position 43, R3-089 fixture check before position 49 (find -mtime -7 returns exactly 6; fixture in-window until 2026-12-01 08:59, refresh if the run slips past it), R3-100 port check before position 55 (graded from saved files only).

### 2.4 Totals and execution order

- Muse: 25 executions (3 re-runs + 22 in positions 4-28).
- Codex: 24 executions (positions 32-55).
- FCC: 3 executions (R3-014, R3-027, R3-037).
- Opencode: 0.
- Total: 52 executions.
- Order: re-runs of positions 1, 2, 3 first (in order), then positions 4-28 in order, then positions 32-55 in order. One driver at a time on the shared Zen; the runner for each position is per this split. Class L tasks (R3-001 re-run, R3-055, R3-074, R3-075, R3-078, R3-079, R3-088, R3-089, R3-096) are score-before-reset: the runner waits for scoring plus reset before the next release on that lane's turn.

## 3. How Muse runners work (new runner type)

- Each Muse task is run by a FRESH independent Muse subagent spawned by the coordinator for that one task. The subagent is given the runner lane brief plus the task text only (no key, no prior task evidence, no training on the system). This is the fresh-untrained evaluator rule.
- The subagent SSHes to the laptop via ~/workspace/ssh-laptop.sh (IdentitiesOnly plus tailscale-proxy; direct ssh fails). Long jobs run detached (setsid nohup ... > log 2>&1 < /dev/null & disown); SSH sessions are kept short (the connection dies around 30 seconds).
- Driving: Zen via computer-use (WebDriver BiDi, port 9222; Marionette 2828 fallback unproven, recorded as accepted risk). The pill MUST show on any agent control: acquire before driving, release after, verify with grim (the pill can stay visible after release while status says false; end each session with finish). Pill text is plain "Computer use active".
- One driver at a time: before any drive, the coordinator verifies the session is free by /proc fd scan for cursor.lock (no holder). The Muse runner, the Codex runner, and the FCC runner never overlap drives.
- Evidence: the runner writes evidence to ~/rung3-chung-cu/R3-xxx/ on the laptop (ket-qua.txt, timestamped screenshots, start/end times, saved files per the task). The coordinator pulls it to the VM (sha256-verified, one file at a time), seals the snapshot, runs the manifest gate, and only then releases the next task. The runner never scores its own task and never writes the ledger.
- 30-minute task timeout: over 30 minutes is FAIL, never graded from partial evidence, kill by exact recorded PID only (never pkill -f). The coordinator records task_start and the runner PID at every release and clears them at drive end (stale timer fields caused two near-miss kills earlier in the run; the timeout watch verifies with independent evidence before any kill, and epoch 7 keeps the fields fresh).
- A Muse runner that cannot reach the coordinator finishes the current task, preserves evidence, and does not start another (worker self-stop floor).

## 4. Opencode probe result: does not run; flag for the owner

Probe (epoch 7, 2026-11-25 17:53 +07, on the laptop, opencode v2.4.1):
- Command: opencode run -m nvidia/deepseek-ai/deepseek-v4.1-flash "Reply with the single word READY and nothing else" (detached, 90-second timeout).
- Result: "Error: The model 'deepseek-ai/deepseek-v4.1-flash' has reached its end of life on 2026-11-16T08:00:00Z and is no longer available."
- The nvidia route for DeepSeek v4.1 Flash is end-of-life. The only other configured route in opencode.json is OpenRouter, which is banned for opencode by the owner's hard rule and is out of credits. The owner's rule for opencode is DeepSeek v4.1 Flash free only, do not try other models, no OpenRouter; groq and other nvidia models were therefore not tried.
- Conclusion: opencode cannot run as a runner on an allowed route. Share: 0 tasks.
- Flag for the parent/owner: making opencode runnable needs an owner-level login step (wire an allowed DeepSeek route into opencode; a DeepSeek credential exists in the FCC configuration but is not wired into opencode, and no key was invented or copied by the coordinator). The run does not block on opencode; it proceeds with Muse + Codex + FCC. If the owner wires a route later, opencode can be given a share from Muse's range by a short plan amendment.

## 5. Scoring assignments (independence preserved)

- Grader never the author: no runner scores a task it ran. Muse runner subagents and scorer subagents are always different fresh sessions. Mochi is a separate account and never runs tasks.
- Pair A (positions 1-28, including the 3 re-runs and FCC's 3): scorer 1 is Mochi where her capacity allows; scorer 2 is a fresh independent subagent per task. For every task Mochi scores, the coordinator pushes the sealed snapshot to the repo first (Mochi has no VM or laptop access; she scores from files). Her verdict files come back via her own branch and are copied into the verdicts dir (re-run verdicts into the rerun subdir). If Mochi is unavailable or her queue lags past the backpressure limit, the Pair A standby tiebreaker (TB-A) is the fallback scorer 1 (per the re-plan roster), and the tiebreaker of last resort is TB-B2.
- Pair B (positions 29-55, Codex-run): two fresh independent subagent scorers per task (the 1B/2B pattern used for R3-040, R3-041, R3-042), scoring from VM-local snapshots (no repo push needed). Tiebreaker TB-B2 on disagreement (fresh spawn; the calibrated session IDs are completed and cannot resume, so tiebreakers are spawned fresh on demand, as in epochs 3-6).
- Re-run scoring: Pair A, same rigor. The re-run scorer 2 is a fresh subagent distinct from the Muse re-run runner. R3-001's re-run is Class L (score-before-reset, live re-read of TodoMVC state). R3-002's re-run gets the Tier A checker output handed identically to both scorers.
- Mochi load note: Pair A has 28 scorings under this plan (3 re-runs + 25 remaining positions 4-28). Backpressure protects her queue: a runner pauses when it has 2 unscored tasks and the oldest lag exceeds 30 minutes. If Mochi's scoring rate cannot keep up with the serialized drive rate (about one task per 14 minutes), the drive rate slows to her rate; the time estimate in section 6 assumes she keeps up on average, with the fallback above if she cannot.
- Tiebreaker only on PASS/FAIL disagreement, disputed invalid, or formal key dispute (blind packet: both grades + manifest + key excerpt). Invalid requires independent scorer-collected evidence plus blind confirm by scorer 2 plus coordinator countersign; the owner is notified at invalid 3, 4, 5 (via the parent, per the reporting threshold).
- The coordinator audits every verdict (parse, session match, key hashes 5059f6c4 / 21f8b61a, manifest match, independence declaration, snapshot + key only, no log.txt, no other-scorer verdict) before writing any ledger row. The coordinator never scores and never overturns a scorer; only the owner overturns, and only on a process dispute.

## 6. Time estimate under single-driver serialization

- 52 executions, one driver at a time. Measured Codex drive times this run: R3-041 14m07s, R3-042 9m01s (R3-040's 5m05s final attempt reused a VM-fetched page and is not representative). Muse subagent drive times are unmeasured; a fresh subagent must SSH in, read the brief, drive, and produce evidence, so 12-25 minutes per task is the planning range. FCC's 3 easy tasks: 5-15 minutes each if genuine, plus gate-failure re-collect time if FCC fabricates (capped by the 3-re-collect branch, then seal and score).
- Planning average: about 16 minutes of wall time per execution (drive-bound, serialized), including evidence collection. 52 x 16 min = about 13.9 hours.
- Class L score-before-reset waits: 9 Class L executions (R3-001 re-run + 8 in the Codex range) where the driver idles while scoring completes, about 8 minutes each = about 1.2 hours.
- Coordinator serial work (collect, snapshot, manifest gate, reset, audit, ledger, push) is about 5 minutes per task, mostly overlapped with the next drive for Class S tasks; only the Class L waits and any scoring lag add wall time beyond the drive-bound estimate.
- Total additional wall time: about 15-17 hours. Elapsed so far: about 5.2 hours (started 12:45:58, now about 17:57). Projected run total: about 20-22 hours, inside the 31-hour staffed ceiling.
- Re-measure triggers (unchanged in spirit from the re-plan checkpoint): after the first 3 Muse-run tasks (calibrates the Muse drive time), after 3 graded tasks of one class, and at the 3-hour wall-clock fallback. Pause and report to the owner (via the parent) only if the revised run-complete exceeds 31 hours or a per-class mean exceeds its estimate by more than 25 percent with at least 3 graded tasks of that class; otherwise continue with a recorded estimate.
- Zen RSS: it climbed about 1.2 GB per 15 minutes under run load before the 17:03 D1 restart reset it to 978 MB. Expect further D1 restarts at task boundaries (SIGTERM, relaunch via the zen-ai wrapper, verify ports 9222/2828 and tabs restored, Zen back on ws2) whenever RSS passes about 8 GB. Each restart is a few minutes at a boundary and does not affect sealed evidence.

## 7. What happens to the 53/55 bar

- Under counting rule A (supersede, proposed): the bar is reachable again, conditional on the re-runs.
  - 3 of 3 re-runs pass: 6 PASS banked, need 47 of the remaining 49. Two FAILs of slack.
  - 2 of 3 pass: 5 PASS, 1 FAIL banked, need 48 of 49. One FAIL of slack.
  - 1 of 3 passes: 4 PASS, 2 FAIL banked, need 49 of 49. Reachable only with a perfect remaining run.
  - 0 of 3 pass: max PASS 52. Bar unreachable (same as now).
  - Invalids still recompute the bar by the pre-declared table (valid N needs N-2) if the valid count shrinks; the re-runs do not change the invalid caps (5 total, 2 per difficulty group).
- Under counting rule B (separate data): max PASS stays 52. The bar is unreachable regardless of re-runs or remaining results. The run's value is per-task data and the Muse-driving proof, reported as such at closure.
- Either way, the closure report states the count both ways (original-ledger count and, if rule A is approved, the superseded count), so the result is never presented without its basis.

## 8. What stays frozen, and the approval ask

Frozen and unchanged by this re-plan: the 55-task list and its order (re-runs are re-executions of positions 1-3, not list changes), both answer keys, the evidence requirements, the Class L / Class S split, the invalid and backup rules, the timeout rule, the single-driver rule, the pill rule, the git discipline, and the bar number 53/55.

Decisions the owner is asked to approve:
1. The re-runs of R3-001, R3-002, R3-003 by Muse (section 1.2), overriding the old last-attempt limit on R3-001.
2. The ledger counting rule: A (supersede at closure, separate re-run ledger, originals preserved) or B (separate data, FAILs stand). Recommendation: A.
3. The runner split (section 2): Muse 25 (3 re-runs + 22), Codex 24, FCC 3 named easy tasks (R3-014, R3-027, R3-037), opencode 0 with the flag in section 4.
4. Execution order: re-runs first (positions 1-3), then positions 4-28, then 32-55, single driver at a time.

On approval, epoch 7 formalizes the split in the state file, releases the R3-001 re-run to a fresh Muse runner, and continues under the re-plan's standing rules (heartbeat every 10 minutes to the state file and the heartbeat log, Zen RSS watch with D1 restarts at boundaries, backpressure, per-task reports, ledger pushes at least hourly and immediately on INVALID or dispute). Until approval, HOLD: no releases, no drives, no scoring assignments beyond what is already graded.
