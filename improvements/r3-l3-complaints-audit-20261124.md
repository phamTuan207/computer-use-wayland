# Complaints audit for the R3-L3 run, 2026-11-24

- Auditor: independent complaints auditor, fresh agent, did not work on the run on 2026-11-24.
- Scope: every complaint, error, frustration, and unexpected situation the owner raised, first in the main chat on 2026-11-24 (Part A), then across the whole project history from the project start in mid-October 2026 to 2026-11-24 (Part B).
- Deliverable for: the final pre-run meeting for the R3-L3 run on 2026-11-25.
- Language note: this file uses "the owner" throughout and contains no personal data (no names, addresses, emails, phone numbers, passwords, PINs, tokens, or schedules).

## Method and honesty note

- Sources: (1) transcript queries over the full history (user messages, 13 Oct to 24 Nov 2026, about 6,048 messages: 750 in October, 5,298 in November), keyword-filtered for complaint markers and read in date order; (2) all 43 daily logs under the memory directory, 2026-10-13 to 2026-11-24; (3) the standing-rule record, which is itself the codified list of past complaints; (4) the R3-L3 execution plan, section 12 residual risks.
- Counts below are AT-LEAST counts of distinct incidents found in that evidence. They are not an exhaustive census: keyword filtering can miss softly worded complaints, and voice messages arrive as transcripts. Treat a count of N as "N found, possibly more".
- Each item follows one shape: what happened, root cause, concrete prevention for tomorrow's plan. Preventions are rules, checks, or procedures, not wishes. Part C collects them as a checklist the run coordinator must apply.
- Items already fixed during the day are still listed, because a fix without a prevention rule recurs. Where the owner already set a standing rule, the item says so and the prevention is to enforce it, not to re-invent it.

## Summary by theme

| Theme | Entries found | Worst single case |
|---|---|---|
| T1. Asking the owner to act, repeating questions, sign-in friction | 12 | Secure Vault card shown again after a hard ban (15 Nov) |
| T2. Computer-use driving errors (wrong window, tool, click, grounding, slowness, pill) | 14 | Laptop driven while the owner used it; typed into the wrong window (6 Nov) |
| T3. Silent stalls, unreported blockers, false delivery receipts | 10 | Mochi "silent" 79 minutes before detection (24 Nov) |
| T4. Fabrication, wrong claims, unverified assertions, misattribution | 9 | Clone1 falsely accused of driving without a pill (24 Nov) |
| T5. Calendar overlaps, silly events, wrong tags, missing travel time | 7 | TeachingAssistant shift overlapping a shower block (25 Oct) |
| T6. Channel mix-ups (wrong chat, wrong thread, wrong person) | 6 | Proactive follow-up posted in main instead of its side chat (15 Oct) |
| T7. Long dash and AI-slop writing | 5 | Draft lost points for 2 long dashes (16 Nov) |
| T8. Git and repo hygiene (personal data in history, wrong repo, sweep commits, missing delivery path) | 7 | Discord CLI split across two repos (24 Nov) |
| T9. Wrong delegation, assumed agent capabilities | 7 | Brief told clone1 to "write a report" with no commit instruction, then claimed it had no repo path (24 Nov) |
| T10. Watchdog and monitoring failures | 7 | Read path blind 19:23 to 19:53, 15-minute poke rule unenforceable (24 Nov) |
| T11. Speed and slowness | 6 | First click took almost 5 minutes after the go order (21 Nov) |
| T12. Memory system deleting or changing owner decisions | 3 | R3-029 password decision removed from memory twice in one day (24 Nov) |
| T13. Lessons not recorded, owner forced to repeat | 6 | "Note it down so I do not have to remind you again" (5 Nov) |
| T14. Cleanup after use (windows, tabs, processes left behind) | 5 | 27 leftover Chromium tabs; owner: "a pile of messy windows" (24 Nov) |
| T15. Outreach quality (money mention, wrong split, no biography crawl) | 4 | Outreach mail mentioned money; owner: elementary mistake (14 Nov) |
| T16. Rogue automation and unrequested work | 5 | Telegram script kept auto-sending frames after a stop order (4 Nov) |
| T17. Giving up after one try; self-diagnosis instead of independent review | 4 | R3-040 declared failed after one method hit a rate limit (24 Nov) |
| T18. Evidence and verification standards | 4 | "Fixed" claimed without a passing live task test (standing rule, 15 Nov) |
| T19. Run-prep defects found 24 Nov (docs drift, stale IDs, wrong counts) | 8 | Addendum listed retired scorer session IDs; ledger regex rejected two backups (24 Nov) |
| Total distinct incidents | 132 | |

Theme entries total 129. Twenty of them cross-reference Part A items and two repeat other Part B items, so Part B adds 107 new incidents to Part A's 25, for 132 distinct incidents in total.

## Part A. Today, 2026-11-24 (main chat)

### A1. Clone1 brief lacked a commit instruction, then Muse wrongly claimed clone1 had no repo path
- What happened: the owner asked why the clone1 report had not reached the repo. The brief only said "write a report", with no commit instruction and no delivery path. Muse then claimed clone1 "has no path into the repo". Clone1 answered in its own chat that it does have the command line tool, is signed in, and merged a pull request at 20:00 the same day. The owner repeated several times: both clones already had the tool set up, and if Muse did not know, it should have asked the agent directly.
- Root cause: the brief stated the work but not the delivery path; Muse guessed at an agent's capability instead of checking or asking.
- Prevention: every brief must name the delivery path in one line (what file, which branch, commit and push, verified). Never assert what an agent can or cannot do; check first or ask the agent in its own chat. Add this as a pre-brief checklist line in the run plan, and have the coordinator verify each brief carries it before sending.

### A2. Pill misattribution: clone1 accused of driving Zen without a pill; the driver was the coordinator's own worker
- What happened: the Zen final report accused clone1 of driving Zen that evening with no pill overlay, which would break the standing pill rule. The owner objected three times: clone1 has no computer-use skill, no shell, and no connection into the machine, so it could not have driven anything; "certainly someone in this story is fabricating". An independent investigator found clone1 cannot reach the browser automation port at all, and the real driver at 19:58 was a browser-automation test worker belonging to the Zen coordinator itself. The pill really was absent 19:53 to 20:22, but the violator was the coordinator's own worker, not clone1.
- Root cause: an accusation was written into a report from a screenshot (a chat tab visible in a split view) without checking the accused agent's actual access path, and without checking whose worker ran at that minute.
- Prevention: no blame claim goes into any run report without two checks: (1) the accused agent's access path (can it physically reach the resource?), (2) the timestamped log of who actually acted. The coordinator must correct its own report in writing when an independent check refutes it. For the run: every live drive must take the pill first, whatever the method (computer-use session, raw automation protocol, script), and the pill check is part of the pre-drive checklist, not an afterthought.

### A3. Discord work split across two repos
- What happened: the Discord command line tool was built in two places. Research and phase 1 commits went to the main repo on the run branch; the CLI source, tests, skill, and final report went to a second repo on a branch of the same name. The owner asked in chat whether to merge them into one repo or leave it split; at flush time the user had not answered, so the split stayed pending the user's decision.
- Root cause: workers 3 and 4 were briefed without a single named repo and branch; nobody owned the landing target.
- Prevention: every multi-worker job names exactly one repo and one branch in the brief, and the coordinator verifies each commit lands there before the worker is marked done. For the run: only the coordinator commits to the run-log branch; no other agent touches the repo during the run (already in the plan, enforce it with a pre-task check that no other worktree has uncommitted changes).

### A4. The R3-029 password decision was removed from memory twice in one day by an external process
- What happened: the owner decided at 18:51 that the R3-029 test-account password is not stored in the Secure Vault and will not be stored there; the run coordinator passes it to the runner in the task brief. An hourly memory job removed that decision from memory twice (restored at 20:33 and again around 21:00). A related line (the R3-040 retry decision) was also deleted from memory by an outside edit around 02:53.
- Root cause: an automated memory job can delete an explicit owner decision without any guard, and nothing alerts anyone when it does.
- Prevention: owner decisions are append-only for automated jobs; any automated edit that removes a decision line must be blocked or must raise an alert. For the run: the coordinator must re-verify the R3-029 credential handoff from the run brief itself, not from memory, before position 25; and the run brief must carry the credential decision in writing so a memory edit cannot silently change it. Do not record the password value in any repo file or log.

### A5. PWA tasking used mouse and vision when a code path was available
- What happened: the owner sent a screenshot of a worker clicking into the clone1 chat box with the mouse and asked why, since the app was supposedly already optimized for AI. The earlier PWA work had only proved read-only code control; the message-send path over code had never been built, and the brief still told the worker to use the mouse. A worker then built a code-based send script and proved it, and the owner widened the scope to test every PWA feature over code.
- Root cause: "optimized" was claimed after proving only reads; the write path was never built or tested, and the brief defaulted to mouse.
- Prevention: an app is only called optimized after both read and write paths are proved live over code. Briefs must name the code path first and forbid mouse or vision unless the brief states why code cannot do it. For the run: runners drive through the fastest code path first (command line, API, automation protocol), vision and mouse last; any mouse step in a run brief must carry its justification.

### A6. Watchdogs removed at the user's order, plus a disk watchdog the user declined
- What happened: the owner asked for a list of watchdogs in the chat, ordered the first three removed, asked for a fresh assessment of what the night needed, approved three new 15-minute watchdogs, then added two more, then immediately cancelled the disk watchdog because the user had already cleaned the disk and had 200 GB free. The three removed were the mei-mochi 15-minute watchdog, the Zen 20-minute watchdog, and the liveness guard.
- Root cause: not an error; the owner re-scoped monitoring for the night. The risk is losing coverage silently if the removal is not recorded with what replaces it.
- Prevention: every watchdog removal or replacement is recorded in one place with the replacement coverage named. For the run: the run coordinator owns a written watchdog roster (which watch, what it guards, interval, who is paged). No watch is removed mid-run without the replacement being live first.

### A7. Machine optimization felt like mere memory cleanup, not controllability
- What happened: the owner said the goal was to optimize the machine so AI can control everything in it more easily, but what the user saw felt like only cleaning memory for the user. The sweep's measurable wins were mostly stopping a service, clearing cache, and stopping an indexer; the real control work was only the PWA code endpoint and a window-focus helper. A separate AI-control coordinator was then spawned to map every app to a control path.
- Root cause: the sweep brief measured success by freed resources, not by control paths proved.
- Prevention: an optimization sweep reports control paths proved live (one line per app: path, proof, time), and resource cleanup is a separate, secondary section. For the run: the run plan already separates machine-optimized paths from stock-app paths; the coordinator must not confuse a tidy machine with a controllable one.

### A8. Chromium (the second chat account's browser) died twice in one evening, silently
- What happened: the read path for both chat accounts failed from 19:23 (connection refused on both automation ports). The browsers had died or been closed between 19:18 and 19:23. The same browser died again at 20:15, under six minutes after being relaunched, with no crash dump, no out-of-memory kill, and no signal; the suspected cause was launching it attached to a short-lived remote session. It was relaunched detached and verified alive.
- Root cause: browsers launched attached to transient sessions die when the session ends; nothing watched the automation ports, so the death was found only when reads failed.
- Prevention: every long-lived browser is launched detached (never tied to a short session), and a health check polls its automation port, not just the process. For the run: the pre-task-1 check must verify the automation ports respond, and the run must have a mid-run restart point with a clean relaunch procedure (already in the plan appendix, enforce it).

### A9. Discord self-bot risk accepted without a written guardrail at first
- What happened: the owner approved building a Discord read and send path despite the terms-of-service risk ("go ahead, what is there to fear"). The research showed self-bots are explicitly banned and the account could be terminated; the code path does not appear by name in the published terms, but the self-bot rule does not distinguish mechanism. The work was limited to a test account the owner provided for that purpose, with zero vision or mouse use.
- Root cause: risk acceptance was verbal; the boundary (test account only, no production account, no token extraction) was not written down before building.
- Prevention: any accepted terms risk gets a one-paragraph written record before work starts: what is allowed, what is forbidden, which account, and who accepted the risk. For the run: no runner or scorer touches any account outside the run's named test accounts, and no credential is ever extracted or stored.

### A10. Stall detected 79 minutes late; a false poke fired at the wrong agent
- What happened: Mochi was blocked for 79 minutes on a missing file before anyone noticed. The owner: "It took 79 minutes to discover this? It should have been found in 15 minutes." The 15-minute auto-poke rule existed only in memory; no process ran it, the old watchdog only watched the repo on a 1-hour threshold and could not read chat, and the message daemon had died unnoticed. A watchdog was then built and scheduled every 5 minutes. The same night, the new watchdog poked the wrong agent: it measured silence from the last sent message while she had already replied one second later, so the poke was a read-back miss, not real silence. The rule was fixed the same day: poke only when the last sent message is newer than the last seen reply.
- Root cause: a rule with no running process behind it; a silence metric that measured the wrong timestamp.
- Prevention: every time-based rule must name the process that enforces it and the schedule it runs on, verified live. The poke condition is now "last sent is newer than last seen reply", and the read path must be healthy before any poke fires. For the run: the coordinator checks delivery first (not the send receipt) before concluding any scorer is silent, and a read failure disables poking rather than triggering it.

### A11. R3-040 declared failed after one method; the retry then exposed a key mismatch
- What happened: a task failed because the archive service rate-limited the laptop twice. The owner ordered: never call a task failed after one try; try two or three ways and retry several times first. Three parallel probes found a working path from a different machine address. The retry then ran on a different page than the frozen key names, and both scorers failed it because the title and archive date did not match the key. The owner also corrected the record: research source selection should come from live crawling, not from a news feed.
- Root cause: a single-attempt failure verdict, plus a runner choosing its own page instead of the key's page.
- Prevention: the standing rule is now "fail only after two or three methods, retried several times". For the run: runners must use the page the key names unless the key allows a choice; any page substitution is a design question for the coordinator, not a runner improvisation. Scorers grade against the key as written.

### A12. Codex stall misdiagnosed three times in one night
- What happened: new agent sessions stopped responding from about 02:03. The diagnosis moved through four theories in hours: model API stream stall, then a 30-day rate limit at 100 percent (which was true since the previous morning, so it could not be the trigger), then the daemon blocking turns, then the interactive terminal mode itself. Each theory was presented as the answer before the next probe refuted it. The owner kept pushing: "there must be a reason for the error", "find it", and "why did it work yesterday and fail now, read the history and logs and answer". The eventual finding was that interactive terminal sessions could not dispatch turns while the non-interactive exec mode worked, with the exact trigger event never identified with confidence.
- Root cause: each diagnosis was stated as a conclusion from partial evidence instead of as a hypothesis with a falsifying test; no single log (rate-limit state over time, dispatch log) was read before the first claim.
- Prevention: the no-self-healing rule (independent investigator, evidence log handed over, no self-diagnosis) plus a rule that a root cause is only called "found" when a probe reproduces the fix. For the run: the Codex lane now uses non-interactive exec per task (proved working); if a runner stalls, the coordinator restarts a fresh session for that lane and re-runs the dead task from the start, and does not burn run time on live diagnosis.

### A13. Run documents said the R3-029 password was in the Secure Vault; it was not
- What happened: the run order file said the test password was in the Secure Vault. A direct check found the Vault empty for that site. The owner then decided it stays out of the Vault and the coordinator passes it in the task brief. The same file also said the task was position 5 in one report; the correct position is 25.
- Root cause: run documents asserted a credential location nobody had verified.
- Prevention: every credential claim in a run document must be verified by a live check (or explicitly marked unverified) before task 1. The coordinator re-checks the handoff from the brief, not from memory, before position 25.

### A14. Addendum listed retired scorer sessions; the ledger pattern rejected two backups
- What happened: in the final readiness check, both reviewers independently found the same three defects: the scorer addendum listed old session IDs while the run order, coordinator state, and checklist listed new ones; the ledger schema and validator patterns rejected two of the backup tasks; and the verdict channel in the addendum contradicted how verdicts were actually delivered in the previous run. All three were fixed and verified before the run (commit with the corrected IDs, patterns widened, verdicts by file only, daemon messages carrying only a file pointer).
- Root cause: the addendum was written from stale notes, and no cross-file consistency check ran before it was published.
- Prevention: before task 1, one mechanical pass greps every session ID, backup ID, and file pattern across all run documents and fails the gate on any mismatch. For the run: verdicts travel by file to the coordinator only, never by chat, and never directly to the owner.

### A15. R3-047 position recorded as 35; the correct position is 34
- What happened: several log entries said to recheck the maintenance page before position 35. A reviewer caught that the task is position 34. Six files were corrected.
- Root cause: a position number was copied from memory instead of from the run order.
- Prevention: position numbers in run documents are generated from the run order file, never typed by hand. The coordinator re-verifies the recheck point (before position 34) during the run.

### A16. Backup file said the R3-029 check covered 3 of 5 products; the check covered all 5
- What happened: the backup file recorded 3 of 5 product names while the checklist recorded all 5 verified with prices. A reviewer flagged the mismatch; the file was corrected to 5 of 5.
- Root cause: two records of the same verification drifted apart.
- Prevention: one verification record is canonical; every other file quotes it or links to it instead of re-typing the count. The pre-task-1 gate includes a count-consistency check.

### A17. The R3-009 page choice was misread from a garbled message
- What happened: the owner sent a garbled message about changing the page. Muse guessed it meant switching to the one clean page, but that page would have broken the task (its own step requires at least one error). The owner then delegated the choice to the team, which kept the original page with evidence, and the page was re-verified live with full numbers before the run.
- Root cause: a garbled message was interpreted as a decision instead of being clarified.
- Prevention: never act on a garbled instruction; ask for confirmation in one short question. Page and key decisions are verified live by the reviewer, not taken from a single session.

### A18. The 30-hour estimate was challenged; the first answer had no breakdown
- What happened: the owner asked why the run would take about 30 hours even if nothing got stuck, and where the time went. The first answer lacked a bottleneck breakdown. The team then produced one: single machine, single session, sequential lanes, one scorer for all tasks, plus evidence and reset time per task. The owner ordered more scorers, fewer steps, and a rolling pipeline, which the speedup council approved.
- Root cause: an estimate was quoted as a headline without the per-stage arithmetic behind it.
- Prevention: every estimate in the run carries its breakdown (per-task run time, scoring time, reset time, serial coordinator work). The checkpoint after the third graded task recomputes the estimate from measured times and pauses the run for an owner decision if it leaves the planned range (already in the plan).

### A19. Reviewing the run build partly broke the lead scorer's blindness
- What happened: the lead scorer independently reviewed the run build and confirmed it had no blocking errors, but doing so meant she had seen the key contents. She asked whether she should stay as scorer 1 or hand over and keep only the pre-task check. The decision was to keep her as scorer 1, because she had not seen the second scorer's verdicts or the runners' outcomes, with the second scorer and the tiebreaker as the check layer.
- Root cause: the same person was asked to both verify the build and score it blind.
- Prevention: build review and scoring are separate roles; if they must overlap, the decision and its reasoning are recorded before task 1, and the independent scorer plus tiebreaker are named as the check. For the run: the coordinator audits the first grades of each task type and watches for inter-pair drift.

### A20. A worker tried a banned model route because the brief omitted the rule
- What happened: a machine-optimization worker tried a banned model route and reported it out of credit. The rule (no such route, ever) existed in memory but was not in the brief. The owner made Muse write the rule into the standing identity files and ordered that every future brief repeat it.
- Root cause: a hard rule lived in one file and was not repeated in the brief that needed it.
- Prevention: hard rules are repeated in every brief that could touch them; a brief is incomplete if it omits a rule that applies to its work. For the run: runner and scorer briefs carry the short hard-rule list (no banned routes, no other models, no personal data in repo text).

### A21. "Use Mochi more, Mei less" (workload balance correction)
- What happened: the owner set a standing rule to use Mochi more and Mei less, because Mei had done far more work (review, triage, eighteen fixes) while Mochi had only scored and then gone quiet. Later run work was ordered to go to Mochi first.
- Root cause: work was routed to whoever was already loaded, with no balance check.
- Prevention: the coordinator tracks per-agent load and routes new work to the least-loaded qualified agent. For the run: the two scoring pairs split the lanes, and the coordinator does not pile extra verification work on one scorer.

### A22. Clone1 and clone2 have no machine access; their reports are web research only
- What happened: the owner stated twice that the two clones have no remote access into the user's machine, so they do not really know what is on it; work that needs to understand the machine must go to people with remote access. A clone's browser report is web research, and every claim about the machine in it must be verified on the real machine before use.
- Root cause: earlier tasking treated a web-research report as if it described the real machine.
- Prevention: every brief states the agent's access boundary, and every machine claim from an agent without machine access is marked "unverified on the real machine" until a coordinator with access verifies it. For the run: only the coordinator and its workers with remote access verify machine state.

### A23. ZCode excluded from AI optimization
- What happened: the owner said the ZCode app does not need AI optimization and should be left out of all optimization and control work; editing by file is enough.
- Root cause: the sweep had no exclusion list, so it swept in an app the owner did not want touched.
- Prevention: every sweep carries an explicit exclusion list, confirmed with the owner before it starts. For the run: ZCode is out of scope for all run optimization.

### A24. Machine-optimized versus repo-for-outsiders design principle
- What happened: the owner set the principle that apps on the user's machine are deliberately optimized for AI, but the repo is for outsiders whose apps usually are not optimized, so the repo must work on stock, unoptimized apps, and machine optimizations committed to the repo must be optional (opt-in), default off.
- Root cause: earlier work conflated the two targets and risked shipping machine-only assumptions as defaults.
- Prevention: every optimization committed to the repo is labeled machine-only (always on locally) or repo-shared (optional, default off), and the repo path is tested on a stock app. For the run: the run uses the machine-optimized paths, but any fix landed to the repo during the run follows the optional-default-off rule.

### A25. Zalo session lost on the run night; login needs the owner's phone
- What happened: the Zalo check at 20:00 found the web session logged out (redirect to a QR login page). The owner said the user would log in later; by 21:00 it was still out. No messages could be read in between.
- Root cause: a session expiry with no advance warning and no fallback channel.
- Prevention: session-based checks record their expiry risk and the fallback (owner re-login) in advance; the run does not depend on any single session staying alive. For the run: no run-critical handoff travels only through a session that can expire silently.

## Part B. Full history, by theme (mid-October to 24 November 2026)

### T1. Asking the owner to act, repeating questions, sign-in friction (12 incidents)
- B1.1. Messenger PIN: the owner entered the PIN while the agent asked about it; rule set 26 Oct, repeated 27 Oct ("just enter the PIN yourself, do not report or ask again"), and hardened 28 Oct ("never ask or notify about the PIN; enter it silently"). Prevention: the PIN is handled silently by the agent, never surfaced.
- B1.2. Google sign-in: the agent repeatedly asked the owner to type an account or password, or showed a secure-entry card. The owner ordered the Google account chooser every time (28 Oct, 10 Nov, 15 Nov), and later removed the "stop at the password step" rule: use the saved login or create a fresh account and verify by email, never ask the user. Prevention: the chooser is the only sign-in method; a password step is a cue to try the saved login, never to ask the owner.
- B1.3. Gmail confirmation codes: the agent asked the owner to click links or type codes. Rule set 13 Nov and hardened 20 Nov: the agent fetches the code from the mailbox itself. Prevention: any confirmation that arrives by email is fetched by the agent, never delegated to the owner.
- B1.4. Secure Vault card shown again after a hard ban (15 Nov): the owner said never let the user see a Vault card again unless the user asks for it. Prevention: no Vault card is ever shown for a Google sign-in; the chooser covers it.
- B1.5. "Do it yourself" (11 Nov): the owner said when the user asks for something the user has no intention of doing it, even running a command or moving a mouse; the agent has the tools, so it should set everything up and run it. Prevention: never hand the owner steps; do the work, and only ask at a genuine dead end.
- B1.6. Repeated questions: "note it down and do it, do not ask again next time" (28 Oct), "do not ask me the obvious question again" (15 Nov), "do not ask again about things from a year ago" (19 Nov). Prevention: once the owner answers, the answer is recorded the same day and the question is never asked again.
- B1.7. Asking the owner to approve routine work: the owner set full autonomy (23 Nov): the team meets, decides, and acts; only ask the user what only the user can decide (security or personal data, a physical action, direction). Prevention: the run coordinator decides everything inside the plan and escalates only the five run-stop conditions.
- B1.8. Asking the owner to merge pull requests (23 Nov): "you merge it, I am not doing anything, I am leaving the machine to the team". Prevention: the coordinator merges; the owner is never the merge step.
- B1.9. Asking the owner to check a phone number (24 Nov): the agent sat on an audit finding since 23 Nov and the owner had to ask; the number turned out to be a fake fixture number. Prevention: surface audit findings the same day they are found, with the exact value and the verdict.
- B1.10. Asking the owner to re-login to Zalo (24 Nov): the session expired and the only fix is the user's phone QR scan. Prevention: see A25.
- B1.11. Asking the owner to choose between equivalent options without a recommendation (several dates): the owner repeatedly said "you decide, do not ask me" for anything the team can decide. Prevention: bring a recommendation, not a bare question.
- B1.12. Asking the owner to repeat the user's own context (28 Oct, wrong-image search): the agent searched the wrong source because it did not re-read the user's message. Prevention: re-read the user's exact words before acting; when in doubt, search the web first (10 Nov: "when stuck, search Google directly, it is often faster").

### T2. Computer-use driving errors (14 incidents)
- B2.1. Laptop driven while the owner used it (6 Nov): the agent kept driving via computer-use while the owner was at the keyboard, opened the wrong browser despite an explicit instruction to use the other one, and typed into the wrong window, until the owner said "stop everything and answer me". Prevention: the pill must show on any agent control; never drive the owner's active window; finish the in-flight probe, then do only non-driving work until told to resume.
- B2.2. Wrong browser (21 Nov, problem 3): the working method used one browser with the logged-in tab, but the agent opened a different browser and typed URLs with key presses, killing the session. Prevention: save the working method verbatim and reuse it; never improvise a different approach for an identical task.
- B2.3. Missed clicks and bad grounding (20 Nov): the owner filmed the agent failing to find buttons, clicking the wrong ones, and thinking longer than the other agent; root cause admitted the same day was reading positions from an image without correcting for the owner's different screen ratio. Prevention: one vision pass, maximum actions; get positions from the document model or accessibility tree, not from a JPEG; verify grounding on the first attempt.
- B2.4. Slow decisions (20-21 Nov): the agent stood still for almost 5 minutes at a delete dialog; the first click after a go order took almost 5 minutes (21 Nov). Prevention: time every task, log every step with wall-clock time, and treat a 3 to 6 operation task taking 5 minutes as broken, not normal.
- B2.5. Overlay flicker and weak refraction (15-19 Nov): the pill had a visible seam, a dead zone with no refraction in the middle, and was nearly transparent. Prevention: verify the pill visually with a screenshot after every change; do not claim a visual fix without a photo.
- B2.6. Pill missing on raw protocol drives (22 Nov): a message went in with no pill because it was sent over a raw protocol call, not a computer-use session. Prevention: all live writes go through a computer-use session so the pill shows; raw protocol is read-only until a pill-on-protocol mechanism exists.
- B2.7. Ydotool used despite a ban (13 Nov): a worker used the banned tool six times because the brief omitted the ban. Prevention: restate every ban in every brief; never assume a brief inherits rules.
- B2.8. Wrong window closed (22 Nov): an incognito tab was lost when the whole browser process was restarted during a fixture test; incognito tabs do not survive a restart. Prevention: never close or navigate any tab or window the owner opened; open a new tab beside it.
- B2.9. Tab hygiene (21 Nov, 24 Nov): leftover tabs piled up; 27 tabs closed in one cleanup. Prevention: each runner works in one dedicated tab, closes every tab it created after sealing evidence, and never touches the owner's baseline tabs (plan appendix rule).
- B2.10. Browser automation session outlives its connection (24 Nov, plan appendix): a session must be ended before handover, or the next driver gets "session already started". Prevention: the handover checklist includes ending the session cleanly; never retry in a loop, report to the coordinator.
- B2.11. Keyboard layout switching flaky on the optimized browser (21 Nov): the input method sometimes failed to switch and sometimes fixed itself. Prevention: an independent worker investigates and proposes a fix; flaky input is a run risk, not a shrug.
- B2.12. Workspace switching by mouse (21 Nov): a click missed and opened the wrong menu. Prevention: switch workspaces by command, never by clicking a bar button; fastest path first.
- B2.13. File picker: the Browse button is not blocked; clicking dead centre does not register, the mouse must offset until the button darkens (20 Nov). Prevention: record exact click mechanics (hover state first) in the working method, not just "click the button".
- B2.14. Voice call: the agent claimed to see images during a call when it could not, and counted 2 items instead of 11 (20 Nov). Prevention: never claim to see what you cannot see; say so plainly and ask for a description or wait until after the call.

### T3. Silent stalls, unreported blockers, false delivery receipts (10 incidents)
- B3.1. Two-hour stall with no report (19 Nov): work sat silent for 2 hours; the owner set the rule to message the parent within 15 minutes when there is no next lever. Prevention: a dedicated watcher per long process; no progress for 15 minutes means poke and restart immediately.
- B3.2. Blocker unreported for over an hour (20 Nov): a file-picker failure sat from 15:37 to 16:47 before the owner asked. Prevention: report a major blocker as soon as it becomes one, never wait to be asked.
- B3.3. Promised next task never started (20-21 Nov): the agent promised to start problem 3 when the fix finished, then did not check until the owner asked twice; the fix had finished long before. Prevention: when a task is promised on completion of another, the agent must monitor completion and start the next one immediately, then notify.
- B3.4. "Silent" agents were not silent (23 Nov): the agent reported two agents silent for 21-22 hours, but both had replied; there was no read-back path into their chats, and the watchdog only watched the repo. Prevention: never call an agent silent without reading its chat; a repo-only watch cannot see chat replies.
- B3.5. Delivery receipt is not delivery (20 Oct, 24 Nov): a chat send returned a receipt but never appeared in the transcript (verified twice by re-reading); a daemon send reported "sent, verified" while the recipient's client showed "delivery not confirmed" for about 4 hours. Prevention: verify delivery by re-reading the thread; when an agent does not reply, check delivery first before concluding it is silent.
- B3.6. Stuck subagent left running 73 hours (13-14 Nov): a test agent stuck and silent for 73 hours; the owner ordered: kill a stuck agent immediately, do not ask first, and tell the user it was stuck. Prevention: kill stuck agents at once, report the kill, never let one run silent.
- B3.7. Coordinator silent over completed children (22 Nov): a coordinator sat 31 minutes with 6 finished children unanswered and a deadline passed; it was killed and replaced. Prevention: the watchdog reports to the main agent, not to the coordinator, so a stuck coordinator cannot silence its own stall flags.
- B3.8. Long-running process attached to an agent session, so the agent never completed (19 Nov): a worker finished its work but stayed "running" because its guard process was attached to its session, and the completion report never arrived. Prevention: launch long-running processes fully detached; verify the process runs, then end the turn with the report.
- B3.9. Gates finished with no report for 1.5 hours (21 Nov, error-list file). Prevention: every gate completion is reported the same day; a finished gate with no report is treated as a stall.
- B3.10. "Check the inbox every minute" job removed without a replacement (4 Nov): the owner cancelled a 1-minute message check for one contact. Prevention: see A6; removals are recorded with their replacement.

### T4. Fabrication, wrong claims, unverified assertions, misattribution (9 incidents)
- B4.1. "Does not exist" claims are unreliable (10 Nov): a worker reported 7 failed attempts to find an open copy of a paper, but the owner found the PDF in minutes. Prevention: never accept "does not exist / no open copy" from a worker without independently re-checking; a failed search is not proof of absence.
- B4.2. Wrong website named (12 Nov): the agent named the wrong site for a form. Prevention: verify names and links against the source before sending; a wrong name in a handoff wastes the whole team.
- B4.3. Wrong image found (28 Oct): the agent found the wrong meme image from the wrong source; the owner said to search Google, not the social feed. Prevention: search Google first, the video app second, never the social feed for this kind of lookup.
- B4.4. "Not found" for a file that existed on the machine (24 Nov, R3-009 council file): a reviewer said the council minutes file did not exist because it was only on the coordinator's machine, not in her workspace. Prevention: distinguish "not in my workspace" from "does not exist"; check the named location before claiming absence.
- B4.5. Misread of a message (10 Nov): "each person takes 2 lecturers" was read as 2 each and sent, against a 5/5 agreement from the day before; corrected and re-sent. Prevention: re-read the prior agreement before sending a split; when two readings exist, ask which stands.
- B4.6. Wrong count reported (1 Nov): 190 ideas reported, correct number 187. Prevention: recompute counts from the source list, never quote a remembered number.
- B4.7. Outreach mail invented a story (14 Nov): a mail was customized only at company level and got no reply, while a mail built from the recipient's own life story got a same-day reply. Prevention: crawl the person's full biography before writing; write to the person, never to the title.
- B4.8. A worker's "fixed" claim without a passing live test (15 Nov): the owner set the testing standard that a claim of fixed without a passing live realistic task is worth zero. Prevention: tests use realistic tasks, an independent judge scores them, and "fixed" requires a pass.
- B4.9. Pill misattribution (24 Nov): see A2. Prevention: see A2.

### T5. Calendar overlaps, silly events, wrong tags, missing travel time (7 incidents)
- B5.1. Overlapping events (24 Oct): a study block and a teaching shift overlapped; the owner ordered a whole-day check across all calendars before any add or move, and zero overlaps after every change. Prevention: the audit script covers all calendars and reports every overlapping pair; run it before and after any change.
- B5.2. Teaching shift overlapping a shower block (25 Oct): "nobody teaches and showers at the same time, obviously; note it down". Prevention: check neighbouring events when adding or moving anything; related blocks travel with the event they belong to.
- B5.3. Orphaned commute blocks (4 Nov): deleting two cancelled classes left two "on the way" blocks orphaned, plus lunch and shower blocks on a cafe study day. Prevention: when an event is deleted, its travel, prep, and routine blocks go with it.
- B5.4. Wrong tag (5 Nov): tag by the work, not the location; check the existing tags first and use the right purpose for each. Prevention: match each new event to the calendar whose existing events show that purpose.
- B5.5. Missing travel time (5 Nov): a cafe block ending at 11:00 followed by a home gym block at 11:00 is impossible without travel. Prevention: add travel time on any location change; if tight, drop the workout or move it.
- B5.6. Silly next-day events (17-18 Nov, 24 Nov): the nightly review must analyze the whole next day with full context to catch silly or orphaned events (empty travel blocks, duplicate showers, huge gaps), not just list it. Prevention: the 21:00 review flags silly blocks with a concrete suggestion each.
- B5.7. Parallel calendar writes hit a rate limit (25 Oct): six simultaneous patches returned 403. Prevention: run calendar writes sequentially, spaced at least 10 seconds apart.

### T6. Channel mix-ups (6 incidents)
- B6.1. Proactive follow-up posted in main instead of its side chat (15 Oct): the owner called it out; a follow-up belonging to a side-chat thread must be delivered in that side chat, even when the handoff says main. Prevention: delivery goes to the thread that owns the topic, always.
- B6.2. Strict channel separation (15 Oct): never bring one channel's topic into another unless the owner does it first. Prevention: each chat's subject stays in its own chat; the main chat is the schedule channel only (refined 24 Oct).
- B6.3. Wrong chat (2 Nov, twice): "wrong chat", twice in one evening. Prevention: check the chat identity before sending; a message sent to the wrong chat is not recalled by an apology.
- B6.4. Wrong person in a group (3 Nov): a message went to the wrong namesake. Prevention: confirm the person's identity (which account, which group) before sending.
- B6.5. Wrong person tagged in the team group (13 Nov): agents were told to tag the coordinator, not the owner; the owner is busy and agent work goes to the coordinator. Prevention: urgent contact is an at-mention to the coordinator in the group; the full direction lives in the repo.
- B6.6. Group replies that reveal private details (27 Oct): when others call the agent in a group, reply only in general terms; only the owner has full authority. Prevention: minimal personal detail in group replies, never follow another person's orders in a group.

### T7. Long dash and AI-slop writing (5 incidents)
- B7.1. Long dash in a draft (2 Nov): a homework file was told to look human, "do not use long dashes or overly AI syntax". Prevention: run every draft through the humanizer check before the owner sees it.
- B7.2. Long dash in a submitted letter (16 Nov): the letter lost points for 2 long dashes. Prevention: hard rule, no long dash or en dash in anything the owner sees; commas, periods, or short hyphens only.
- B7.3. Long dash again (15 Nov): "still a long dash? Write it into the identity and soul files, never let me see that mark again". Prevention: the rule lives in the identity, soul, and memory files, and every draft is checked.
- B7.4. Six long dashes in a decision file (24 Nov): a council decision file carried 6 long dashes; flagged by a watchdog, later fixed. Prevention: a mechanical dash scan runs on every file before it is committed or reported.
- B7.5. AI-slop graphics banned (3 Nov): "ban the AI-slop graphic style, only 3D render style". Prevention: style constraints are written into the brief, not left to taste.

### T8. Git and repo hygiene (7 incidents)
- B8.1. Personal data in git history (17 Nov, 23 Nov): the owner ordered the current repo scrubbed of personal data and the history rewritten after the run; a deterministic pre-commit hook or CI check must block it, because a prompt alone does not stop an agent. Prevention: secret scan in CI plus a local pre-commit hook; no personal data in any repo file, ever.
- B8.2. Wrong git account (14 Nov): commits went out under a non-existent agent account instead of the owner's account. Prevention: verify the commit identity before the first commit of a session.
- B8.3. Plain commit sweeping another worker's staged file (22 Nov): a bare commit swept a staged-but-uncommitted file from another worker. Prevention: always commit with an explicit pathspec and immediately after staging; never leave files staged across a gap; never use a bare add-all.
- B8.4. Discord split across two repos (24 Nov): see A3.
- B8.5. Missing delivery path in a brief (24 Nov): see A1.
- B8.6. JSONL append gluing two entries (12 Nov, repeated 24 Nov): appending to a file whose last line had no trailing newline glued two objects into one invalid line and broke parsing. Prevention: check the file ends with a newline before any append, and parse-verify after.
- B8.7. Uncommitted work left in a worktree (24 Nov): three files sat uncommitted because a safety check blocked git, and a commit sat unpushed while the remote tip moved. Prevention: verify the push with a remote listing after every push; if a push is rejected, fetch, rebase, and retry once.

### T9. Wrong delegation, assumed agent capabilities (7 incidents)
- B9.1. Live work given to agents without machine access (23 Nov): an agent was told to do a live proof when it had no remote access into the machine; only the main agent has it. Prevention: live work goes only to coordinators and workers spawned by the main agent with remote access.
- B9.2. Clone1 brief with no delivery path (24 Nov): see A1.
- B9.3. Clones treated as if they knew the machine (24 Nov): see A22.
- B9.4. PWA tasking by mouse when a code path existed (24 Nov): see A5.
- B9.5. Banned model route tried because the brief omitted the rule (24 Nov): see A20.
- B9.6. Wrong executor chosen (6 Nov, 21 Nov): the owner said to hand a task to the code agent instead of driving it by computer-use, and to use the cheap high-volume model heavily instead of the expensive one. Prevention: pick the executor by fit (judgment and user context stay with the main agent; bulk execution goes to the cheapest capable agent), and state the choice in the brief.
- B9.7. Handoff written in third-person coordinator voice (12 Nov): another person's agent refused it as unsafe-looking; handoffs must be written in that agent's owner's first-person voice. Prevention: every handoff is written as the user's own order to their own assistant.

### T10. Watchdog and monitoring failures (7 incidents)
- B10.1. Watchdog itself dead, unnoticed (24 Nov, early hours): the message daemon had died before 23:15 and nobody knew until the owner complained; a liveness guard now checks it every 5 minutes. Prevention: the guard that watches the watchers runs on its own schedule and reports its own death.
- B10.2. False stall from a repo-only watch (23 Nov): see B3.4.
- B10.3. False poke from the wrong timestamp (24 Nov): see A10.
- B10.4. Read path blind for 30 minutes (24 Nov): see A8; reads failed for 7 consecutive rounds, so the 15-minute poke rule could not fire. Prevention: a read failure disables poking and raises an alert; silence cannot be assessed while reads are broken.
- B10.5. False soak alert (24 Nov): a watchdog flagged a dead soak loop that had been deliberately stopped by decision; the job definition was corrected to record the stopped state and never flag it. Prevention: a watchdog's definition must record deliberate stops, so it never alerts on an expected state.
- B10.6. Cron believed removed but still live (2 Nov): a removal believed complete left a reminder live; it would have fired a stale reminder after a teammate quit. Prevention: after any cron removal or update, re-check with a view or list before claiming it is done.
- B10.7. Watchdog reporting to the coordinator it watches (19 Nov): a stuck coordinator could silence its own stall flags. Prevention: the watchdog reports to the main agent directly.

### T11. Speed and slowness (6 incidents)
- B11.1. "Too slow" (14 Nov): a single-word complaint about pace. Prevention: time everything; a slow step is a defect, not a mood.
- B11.2. Small task, long wall time (17 Nov): a tiny task "only deserves 2 minutes of total time". Prevention: the headline metric is total wall time, not think time; attack the routine overhead on every run.
- B11.3. First click after 5 minutes (21 Nov): see B2.4.
- B11.4. Slow decisions (20 Nov): the agent thought longer than the other agent while doing less. Prevention: one vision pass with maximum actions; a decision that takes minutes needs a reason logged.
- B11.5. Estimate challenged (24 Nov): see A18.
- B11.6. Run rate contradicts the baseline (24 Nov, plan section 12): 11 tasks took about 16 hours of wall time in the previous run, against a baseline that assumed far less. Prevention: the checkpoint after the third graded task replaces assumption with measurement.

### T12. Memory system deleting or changing owner decisions (3 incidents)
- B12.1. R3-029 password decision removed twice (24 Nov): see A4.
- B12.2. R3-040 decision line deleted from memory (24 Nov, around 02:53): an outside edit removed the "fail only after two or three ways" line from memory the same night it was set. Prevention: same as A4; owner decisions are append-only for automated jobs.
- B12.3. Memory edits that change a decision without a flag (general, 24 Nov): the owner asked which process removed the decision and why; the investigation was still open at flush time. Prevention: every automated memory edit that touches a decision line must leave a visible trace naming the job; unexplained edits are investigated, not shrugged off.

### T13. Lessons not recorded, owner forced to repeat (6 incidents)
- B13.1. "Note the method so I do not have to remind you next time" (5 Nov): a method was taught, then not written down. Prevention: every lesson is written into the standing files the same day, in both the repo (generic) and the local install (detailed).
- B13.2. "Do not make me repeat myself" (14 Nov, 17 Nov, 19 Nov): the owner had to repeat instructions about time logging, about not asking again, and about a password. Prevention: a lesson is only "recorded" when it appears in the standing files and in the next brief that needs it.
- B13.3. Lesson learned but not passed to the next worker (13 Nov, ydotool): see B2.7.
- B13.4. Lesson learned but not passed to the next brief (24 Nov, OpenRouter): see A20.
- B13.5. A rule existed only in one file (24 Nov, OpenRouter rule in memory only, not in identity or soul). Prevention: hard rules live in the identity, soul, and memory files together, and in every brief.
- B13.6. Working method not saved (21 Nov): a method that worked was not saved verbatim, so the next attempt used a worse method and failed. Prevention: save the working method verbatim the first time it works; reuse it exactly.

### T14. Cleanup after use (5 incidents)
- B14.1. "Test finished, clean up" (18 Nov, 24 Nov): the owner asked for a tidy screen after a test; the rule is that after closing any coordinator and after any computer-use use, verify on the machine that its workers are dead, kill them directly if not, finish active sessions, and confirm the pill is gone and the desktop is clean. Prevention: cleanup is part of the task, not a separate favour; the task is not done until the desktop is clean.
- B14.2. Messy windows (24 Nov, 14:09): "a pile of messy windows on screen 1; clean up after use, keep only what is still needed". Prevention: each runner closes the windows it opened; only the baseline tabs survive.
- B14.3. 27 leftover tabs closed (24 Nov). Prevention: see B2.9.
- B14.4. Leftover processes (21 Nov): a dead executor left behind. Prevention: verify with a process list that workers are dead after a test; kill them directly if not.
- B14.5. Black screen after reboot (22 Nov): a user service that pulled in the graphical session target broke login entirely; fixed by removing one line. Prevention: never put a session-target dependency in a user service; test a reboot after any service change.

### T15. Outreach quality (4 incidents)
- B15.1. Money mentioned in an outreach mail (14 Nov): the owner said the one mistake was mentioning money; the mail asked only for an opinion, and it still slipped in a fee. Prevention: outreach never mentions money or fees, even in negation; only "just asking for an opinion".
- B15.2. Wrong split sent to a teammate (10 Nov): see B4.5.
- B15.3. Mail to a CEO with no reply (14 Nov): twenty mails to CEOs got zero replies; a mail built from the recipient's own story got a same-day reply. Prevention: see B4.7.
- B15.4. Letter docked for long dashes (16 Nov): see B7.2.

### T16. Rogue automation and unrequested work (5 incidents)
- B16.1. Telegram script kept auto-sending frames after a stop order (4 Nov): the owner had to order the kill and cleanup twice before it was verified dead. Prevention: a stop order kills the process and verifies it is dead (process list, not a log line); a second stop order means the first kill failed and must be investigated.
- B16.2. Discord bot created without being asked (22 Nov): "why create a Discord bot, did I ever ask for one?" Prevention: never build a new entity (bot, account, repo) the owner did not request; ask first.
- B16.3. Test with an irrelevant map task (22 Nov): the owner said the whole list of test tasks was not needed and off-direction. Prevention: test tasks must be realistic tasks the owner might actually assign, not synthetic coverage.
- B16.4. Roadmap work the owner did not approve (22 Nov): two tracks (freelancing, a paid tool) were struck off the roadmap at the owner's order. Prevention: roadmap changes need the owner's decision; the team does not add tracks on its own.
- B16.5. Messenger auto-replies in a group without a boundary (27 Oct): the agent replied in a group it should have stayed general in. Prevention: see B6.6.

### T17. Giving up after one try; self-diagnosis instead of independent review (4 incidents)
- B17.1. "Do not report an error as 'I cannot do it', find a way first, then report" (14 Nov). Prevention: try two or three ways and retry several times before declaring failure; report the attempts, not just the failure.
- B17.2. R3-040 single-attempt failure (24 Nov): see A11.
- B17.3. Self-diagnosis of the agent's own failure (22 Nov): the owner set the no-self-healing rule: when the agent itself errors, an independent worker investigates, names the cause, and finds the fix; the agent only records the evidence. Prevention: hand the log and the evidence to an independent investigator; never self-diagnose, even for small errors.
- B17.4. Codex stall theories presented as conclusions (24 Nov): see A12.

### T18. Evidence and verification standards (4 incidents)
- B18.1. "Fixed" without a passing live test is worth zero (15 Nov): see B4.8.
- B18.2. Claims without measurement (22 Nov): every claim needs a real measurement (command, output, commit hash, time log). Prevention: a report line without evidence is a hypothesis, labeled as one.
- B18.3. Held-out validation, not memorization (17 Nov): re-running the same test case with baked-in coordinates proves memorization, not speed. Prevention: validate on held-out cases from an independent subagent, run by a fresh agent with no memory of the tasks.
- B18.4. Fresh untrained evaluator (19 Nov): test cases must be run by an independent agent that was never trained on the system, connecting the same way any agent would. Prevention: the evaluator is a fresh agent, not the author of the fix.

### T19. Run-prep defects found 24 Nov (8 incidents)
- B19.1. Stale scorer session IDs in the addendum: see A14.
- B19.2. Ledger pattern rejecting two backups: see A14.
- B19.3. Verdict channel confusion: see A14.
- B19.4. Wrong position for R3-047: see A15.
- B19.5. Wrong product count for R3-029: see A16.
- B19.6. R3-029 password location wrong in the run order: see A13.
- B19.7. R3-009 page choice confusion from a garbled message: see A17.
- B19.8. Two frozen keys briefly suspected wrong (24 Nov): the keys for two tasks were suspected of being wrong from stale notes; both were verified correct live in the browser, which closed the no-margin risk. Prevention: a key is only called wrong after a live check of the actual page; stale notes are not evidence.

## Part C. Prevention checklist for the R3-L3 run plan (apply before task 1)

1. Briefs: every brief names the delivery path (file, branch, commit, push, verify) and repeats the hard rules that apply to its work. No brief goes out without it.
2. Capabilities: never assert what an agent can or cannot do; check first or ask the agent in its own chat. Access boundaries (who has machine access, who does not) are written in the brief.
3. Blame: no blame claim goes into any report without checking the accused agent's access path and the timestamped log of who acted.
4. Pill: every live drive takes the pill first, whatever the method; raw protocol is read-only until a pill-on-protocol mechanism exists.
5. Drive path: code path first (command line, API, automation protocol), vision and mouse last; any mouse step in a brief carries its justification.
6. Watchdogs: a written roster (what is guarded, interval, who is paged). No watch is removed mid-run without its replacement live first. Removal is verified with a view or list.
7. Stall rule: a time-based rule names the process that enforces it and its schedule, verified live. The 15-minute poke fires only when the last sent message is newer than the last seen reply, and never while the read path is broken.
8. Delivery: a send receipt is not proof of delivery. Verify by re-reading the thread; when an agent does not reply, check delivery first.
9. Failure: fail only after two or three methods, retried several times. A runner uses the page the key names; any substitution is a coordinator decision.
10. Diagnosis: a root cause is only called "found" when a probe reproduces the fix. The agent's own failures go to an independent investigator with the evidence log.
11. Memory: owner decisions are append-only for automated jobs; the coordinator re-verifies the R3-029 handoff from the run brief before position 25, not from memory.
12. Documents: one mechanical consistency pass before task 1 (session IDs, backup IDs, file patterns, counts, positions) across all run documents; any mismatch fails the gate.
13. Estimates: every estimate carries its breakdown; the checkpoint after the third graded task recomputes from measured times and pauses the run if it leaves the planned range.
14. Cleanup: each runner closes the tabs and windows it opened and ends its automation session cleanly before handover; the task is not done until the desktop is clean.
15. Repo: only the coordinator commits to the run-log branch; explicit pathspec, add and commit atomically, push verified with a remote listing. No personal data in any repo file; machine optimizations landed to the repo are optional and default off.
16. Sign-in: the Google account chooser is the only sign-in method; a password step is a cue to try the saved login or create a fresh account, never to ask the owner.
17. Writing: no long dash or en dash in anything the owner sees; a mechanical dash scan runs on every file before commit.
18. Roles: build review and scoring are separate roles; verdicts travel by file to the coordinator only, never by chat and never directly to the owner. The second scorer and the tiebreaker are the check on the lead scorer.

## Sources and limits

- Transcripts: full-history user-message queries, 13 Oct to 24 Nov 2026, about 6,048 messages, keyword-filtered and read in date order. The keyword filter can miss softly worded complaints; counts are at-least counts.
- Daily logs: 43 files, 2026-10-13 to 2026-11-24, used as a cross-check and as the source for items that appear only in the log.
- Standing rules: the recorded rule set is itself the codified history of these complaints; items that became rules are cited as rules, not re-invented.
- Execution plan: `r3-l3-execution-plan-20261124.md`, section 12 residual risks, read for run context.
- Side chat: the R3-L3 side chat directory was not present on this machine, so its content was covered through the daily log and the transcript queries.
- What this audit does not do: it does not re-score the previous run, it does not change any run decision, and it does not reproduce any credential value, personal identifier, or schedule detail. Decisions recorded here as "owner decided" are the decisions as written in the logs and transcripts on 2026-11-24.
