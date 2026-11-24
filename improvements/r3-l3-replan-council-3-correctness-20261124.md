# Council 3 (correctness lens) vote on the R3-L3 re-planned roadmap draft

- Date: 2026-11-24, written 21:36 to 21:44 +07 (Asia/Ho_Chi_Minh). Elapsed about 8 minutes for reading and writing; commit steps follow.
- Member: Council 3, correctness lens.
- Vote: AMEND. The draft is sound in structure and adopts the right sources, but it has 28 correctness defects below, each with a concrete fix. None requires rejecting the plan. All blocking items (A1 to A14) must be fixed before task 1; the rest are wording or measurement fixes to fold in before task 1.
- Decision rule applied: majority decides; this vote is AMEND, not APPLY and not REJECT.
- Most serious objection: A1. The draft prints the R3-029 test credential value in its own section 6, contradicting its own rule that the credential lives only in the run coordinator brief and is never written to a repo file. If this draft is committed as-is, the credential leaks into shared repo history, which cannot be undone by a later delete. Delete the value before any commit.
- No credential value, no email address, and no personal info is written in this file.

## Sources read in full before voting

- Draft: ~/workspace/r3-l3-replan-draft-20261124.md (11 sections).
- Base plan: ~/workspace/r3-l3-execution-plan-20261124.md (565 lines, 22 preconditions, 46 redteam objections answered).
- Crawler research: improvements/r3-l3-multiagent-coordination-research-20261124.md (commit f9e20bd).
- Complaints audit: improvements/r3-l3-complaints-audit-20261124.md (commit 5a1d705, 132 incidents).
- Readiness check: improvements/r3-l3-readiness-check-20261124.md (commit 73b49a5, 21 PASS / 3 FAIL / 3 PARTIAL).
- Codex runner input: ~/workspace/codex-meeting-input-20261124.md (10 risks + 10 preventions).
- Cross-checks run live: deputy declaration ~/workspace/r3-l3-deputy-declaration.md; run log thu-tu-chay.txt, coordinator state r3-l3-coordinator-state.json, exception list r3-l3-exception-list.txt (commit 28e2ce03), Phase 0 checklist status, Zen council decision zen-opencode-council-decision-20261124.md.

## Verified correct (the check was real, not assumed)

- Roster IDs in the draft (TB-A 97290681, TB-B2 df4defcc, 1B 4e2f52d4, 2B 2e3ae678, deputy 028399b1) match the current thu-tu-chay.txt and coordinator state. The execution plan IDs (6e844611, 3f3aca86, 2890a5de, b8c9b7b8) are stale R3-L2 IDs with retirement notes in thu-tu-chay.txt. The draft is right to use the new IDs. The stale file is the deputy declaration (17:24), which still lists TB-B 9d613f19, rejected 3/4. See A4.
- Codex 10 preventions are all adopted in the draft (section 4 items 1-10, reflected in sections 7, 8, 9).
- R3-029 and R3-075 keys verified CORRECT (Mochi 17:11-17:19 +07, all 5 product names confirmed with prices; R3-075 fixture sha256s). Key hashes match the readiness check (JSON 5059f6c4, md 21f8b61a).
- Class L count is 9 in the republished exception list (adds R3-096, R3-078, R3-079, R3-088; R3-093 stays Class S with named evidence). See A25.
- Checkpoint rule, 30-minute timeout, invalid caps (max 5 total, max 2 per group), tiebreaker blind packet, Class L score-before-reset, and the per-graded-task report cadence are all consistent with the base plan.
- The draft correctly warns against the readiness check wrong fix (pointing mei at clone1 tab F0857EB317D3027975B6F70658AB666A). See A3 for why the gate itself does not enforce that warning.

## Blocking objections (fix before task 1)

### A1. The draft prints the R3-029 test credential value in section 6
- Defect: section 6 writes the password value and the test-account address in the draft file, while the same section states the credential is never written to a file in the repo and lives only in the run coordinator brief. A file that states a rule and breaks it in the same section cannot be committed.
- Fix: strip the password value and the test-account address from the draft before any commit. Keep only: the credential is in the run coordinator brief, verified by reading the brief (G-28), and never in the repo. Apply the same redaction to the email address in the agy roster row (section 1): remove it from any repo-bound version.

### A2. TB-B2 (df4defcc) has no independent verification, so base-plan precondition 10 is not green
- Defect: the base plan requires Pair B declarations and calibration to be verified by someone other than the coordinator before task 1. The coordinator state file records a correction at 20:02 +07: TB-B2 4/4 rests on the coordinator own check only. The independent verification report (17:27 +07) predates the TB-B2 calibration (17:31 +07) and never mentions df4defcc. The draft roster presents TB-B2 as approved with no flag.
- Fix: add a gate (G-31, or fold into Phase 0 item 10): an independent verifier signs the TB-B2 calibration grade file before task 1. Until then, precondition 10 is NOT green and task 1 does not release. If verification cannot be done in time, record it as an accepted limitation with owner and date (the objection-43 pattern), but do not present it as verified.

### A3. G-23 can pass while reading the wrong chat, and it does not prove sending works
- Defect 1: G-23 requires read.py for mei to return ok=true. The live tab that returns ok for that check today is clone1 chat (F0857EB317D3027975B6F70658AB666A, per the readiness check). Ok=true on the wrong tab satisfies the gate as written.
- Defect 2: G-23 claims the messaging chain is proven working, but it verifies only daemon alive plus read path. The readiness check states a real send is still unproven until the coordinator next real message goes through.
- Fix: G-23 must verify the tab TITLE and CONTENT belong to the intended recipient (mei chat, mochi chat) by direct read, and must explicitly forbid target F0857EB317D3027975B6F70658AB666A as mei target. Either require one real test send plus re-read confirmation per scorer before task 1, or downgrade the claim to read path proven, send proven on the first real message, and name that first message as the proof point.

### A4. G-24 deputy confirmation is stale
- Defect: the deputy declaration is timed 17:24 +07. TB-B2 was approved 17:31, and the codex-exec adaptation and roster changes came after 17:24. A 17:24 declaration cannot confirm the current state file and roster.
- Fix: G-24 requires a fresh, timestamped deputy re-confirmation against the current state file and current roster (TB-B2 df4defcc, codex exec per task) before task 1.

### A5. G-25 and F-01(a): recording a PID BEFORE launching is unimplementable
- Defect: a PID exists only after the process spawns. Codex exec spawns one process per task, so its PID cannot be recorded before launch. The same holds for a fresh tmux session.
- Fix: record task ID, session ID, and launch command BEFORE launch, and record the PID immediately after spawn and before the task starts driving. Keep the deputy check (PID, session, evidence dir before relaunch) from Codex prevention 3.

### A6. F-21 and G-27 (Z8): the unload protection is unverifiable as specified, and the mechanism is unproven
- Defect 1: F-21 offers verification by unload protection from the council prefs being effective. The readiness check found browser.tabs.unloadOnLowMemory absent from prefs.js because the pref does not exist in this build, so it is a no-op. That claim cannot be the verification.
- Defect 2: the base plan Z1 states Linux Firefox does not auto-unload tabs by default and Zen removed its unload timer, so the default is tabs stay loaded. That cuts against F-21 premise that the run tab can be unloaded under memory pressure. No unload mechanism is established in the sources.
- Fix: reframe F-21 as precautionary. Make G-27 concrete: verify the run tab is pinned (state how and where checked), record Zen RSS plus headroom as a number, and confirm the Z3 restart trigger (RSS 8 GB) is armed. Drop the prefs-effectiveness claim, or replace it with the about:unloads baseline check from Z4.

### A7. Section 9 mixes position numbers with task numbers
- Defect: section 9 says before positions 34, 49, 79, 100. Only 55 positions exist. 79 and 100 are task numbers, not positions (R3-079 is position 43 per the exception list; R3-100 is the last Codex-lane task). The todolist in section 10 correctly says Before R3-079 and Before R3-100.
- Fix: rewrite as before position 34 (R3-047 Gutenberg), before position 49 (R3-089 fixture), before R3-079 (position 43, coupled-task reset), before R3-100 (position 55, port check).

### A8. The reporting-chain watch false-positives on normal operation
- Defect: section 5 and section 8 trigger the watch on no per-task report for 30 minutes while tasks are running. One task may run up to 30 minutes, plus Class L serial scoring, so gaps over 30 minutes between ledger rows are expected. The watch will page the parent during normal running.
- Fix: trigger on no coordinator heartbeat AND no report for 30 minutes (heartbeat every 10 minutes per section 8), or set the threshold to cover the maximum expected gap (task timeout 30 minutes plus scoring lag). Name the heartbeat as the liveness signal, not the ledger row.

### A9. Standby-as-fallback-scorer leaves the pair without a tiebreaker
- Defect: section 1 makes TB-A and TB-B2 the fallback scorer 1 for their pairs, following base-plan objection 28, but names no replacement tiebreaker if a disagreement then arises in that pair. The pair would have no one to call.
- Fix: name the tiebreaker of last resort for a pair whose standby is acting as scorer 1 (for example the other pair standby, or escalation of the disagreement to the council or owner) and record it in the roster.

### A10. Research-commit contradiction
- Defect: F-07 and section 5 state only the coordinator commits to the run-log branch during the run and no other agent touches the repo. Section 5 also requires Clone1 and Clone2 to commit research to todolist-push. Both cannot hold.
- Fix: reconcile explicitly. Either research commits go through the coordinator, or they go to a named non-run-log path or branch approved by the coordinator. State which rule yields.

### A11. Codex retry rule contradicts the no-blind-retry rule
- Defect: section 1 says if a codex exec invocation fails, the coordinator retries it once, with no state check. Codex prevention 5 and F-11 forbid blind retry because a partial run could drive the same action twice.
- Fix: retry only after checking the evidence dir and runner state (no partial drive already recorded), per F-11.

### A12. F-23 maximum wait is promised, not set
- Defect: the draft and the base plan both defer the correlated-outage maximum wait to Phase 0 with no value and no gate checking that a numeric value exists. The outage stays unbounded until someone writes the number.
- Fix: add a gate requiring the numeric maximum wait (value plus escalation path) written in the run log before task 1.

### A13. G-29 scrub scope is incomplete
- Defect: the readiness check says the private address is in WORKLOG.md line 89 AND in two other head-tree files (unnamed). G-29 allows scrubbing in a new commit without naming all files, so a one-file scrub can claim the gate while the finding stays live.
- Fix: require a repo-wide grep proving zero occurrences of the address in the head tree before claiming scrubbed, or written acceptance naming all files plus a scrub date.

### A14. New watchdogs lack verify-after-write
- Defect: section 5 creates coordinator-liveness-watch, reporting-chain-watch, and daemon-liveness-watch as new crons to create before task 1. The todolist says created and enabled with no verification step. Complaints audit B10.6 shows a cron believed removed stayed live.
- Fix: require cron list verification before task 1 (each job listed, enabled, first run succeeded or next run scheduled).

## Must-fix wording and measurement objections (fold in before task 1)

### A15. Backpressure wording drift
- Defect: section 9 says if the lag exceeds 30 minutes, pause that runner. That reads as lag alone triggering a pause. The base plan pauses when the runner has 2 unscored tasks AND the oldest lag exceeds 30 minutes.
- Fix: restore the conjunction verbatim.

### A16. Pass-bar recomputation narrowed
- Defect: section 9 Phase 3 says the bar is recomputed only by an owner decision before task 1 if the valid count shrank. The base plan Phase 3 step 4 recomputes per table (54 valid needs 52, 53 needs 51) and records it in the ledger, with an owner decision required only if the shrink was not pre-declared.
- Fix: restore the table plus the pre-declared-shrink distinction.

### A17. Inter-pair drift trigger is unmeasurable
- Defect: F-20 and risk R13 trigger a council review if agreement differs by more than 1 task, but agreement between pairs is undefined (each pair internal agreement, or pass counts).
- Fix: define the metric. For example, each pair pass count among its first 3 graded tasks; if the two pass counts differ by more than 1, call a council review before the next task in the affected pair.

### A18. F-03(b) is unenforceable as a run prevention
- Defect: the memory job must not remove a line that records an explicit owner decision. No enforcing process, owner, or check is named, and the run cannot enforce another job behavior. The real protections are (a) brief-only and (c) re-verify.
- Fix: downgrade (b) to a follow-up request to the parent, recorded but not counted as a run prevention.

### A19. F-04(b) assumes a BiDi pill procedure that is not established
- Defect: F-04(b) says the BiDi procedure must acquire the pill before every live drive, without naming that procedure. Complaints A2 and B2.6 record that a pill-on-raw-protocol mechanism does not exist yet and live writes go through computer-use sessions so the pill shows.
- Fix: name the pill-acquisition procedure for BiDi drives, or state the fallback (live drives go through a computer-use session; raw BiDi is read-only until the pill mechanism exists) and verify it before task 1.

### A20. F-12 manual ID update repeats the wrong-fix trap
- Defect: F-12 says until the daemon resolves targets dynamically, the coordinator updates the IDs after every browser restart. The manual update is exactly what produced the wrong mei fix (pointing mei at clone1 tab).
- Fix: every manual ID update must verify tab TITLE and CONTENT match the intended recipient before use (same check as A3).

### A21. Roster count is wrong
- Defect: section 0 says the full 9-person team. The roster table has 14 rows.
- Fix: say 9 core sessions plus 5 support roles (or count 14 members).

### A22. Mei INVALID channel is new versus the base plan and underspecified
- Defect: the base-plan invalid procedure is scorer 1 proposes, scorer 2 confirms blind. The draft gives Mei, a non-scorer and key author, an INVALID-proposal channel feeding scorer-2 blind confirmation, without naming which scorer 2 (Pair A or B, per lane) and without stating it does not replace scorer 1 proposal right.
- Fix: name the confirming scorer per lane, and state Mei proposal is an additional input, not a replacement. Scorer 1 keeps its proposal right.

### A23. F-14(c) re-enables a watchdog the owner disabled, without citing approval
- Defect: the owner ordered the mei-mochi 15-minute watchdog disabled tonight. The draft asserts it is re-enabled for the run without citing owner approval for the re-enable.
- Fix: record owner confirmation for the re-enable (or note that run-start approval covers it) before task 1.

### A24. P1-H todolist item is undefined in the draft
- Defect: section 10 cites P1-H pref reverted after the run (council condition) with no pref names. The definition exists in zen-opencode-council-decision-20261124.md line 112: network.captive-portal-service.enabled false and network.connectivity-service.enabled false, revert condition at line 169.
- Fix: add the two pref names plus the source pointer to the draft.

### A25. F-16 does not state the per-task dispositions
- Defect: F-16 says the four are resolved without stating how. The resolution exists in the republished exception list (commit 28e2ce03): Class L is 9 (adds R3-096, R3-078, R3-079, R3-088; R3-093 stays Class S with named evidence). The Class L count drives the time estimate, so the draft should state it.
- Fix: cite the exception list commit 28e2ce03, state Class L is 9, and state R3-093 stays Class S.

### A26. F-19 Tier A checkers are not verified
- Defect: the readiness check verifies manifest-gate, audit-scan, and snapshot scripts but names no Tier A checker script. F-19 says if the checker script cannot be located, Decision D cannot be executed. No gate verifies the checkers exist.
- Fix: add a Phase 0 verification that each Tier A checker script is located and runnable before task 1, naming the scripts.

### A27. Section 11 decision rule is ambiguous
- Defect: majority (2 of 3) APPLY equals council APPLY, but a REJECT blocks only if its objection is not concretely mitigated. If 2 vote APPLY and 1 votes REJECT with an unmitigated blocking objection, the outcome is unclear.
- Fix: clarify. Majority APPLY adopts the draft subject to every blocking objection being mitigated before task 1; an unmitigated blocking objection blocks task 1, not the adoption.

### A28. F-07 git wording contradicts itself
- Defect: F-07 says always commit with an explicit pathspec AND immediately after staging, then says never use a pathspec on the commit. The pathspec belongs on git add, not on git commit, but the sentence as written says both.
- Fix: reword to: use git add with an explicit pathspec, then git commit with no pathspec, immediately after staging, never leaving files staged across a gap.

## What this vote does not object to

- The two new failure modes (F-01 orphaned workers, F-02 silent reporting chain) are real and correctly added. The heartbeat plus ack design is the right shape; A8 fixes its trigger, A5 fixes its PID wording.
- The watchdog roster (section 5) is the right set of watches. A14 adds the missing verification step.
- G-23 as a concept (gate the run on the messaging chain) is correct. A3 fixes what it verifies.
- G-30 (FCC input optional, noted in the log) is correctly scoped.
- The draft correctly keeps the 22 base preconditions in force and correctly keeps the 19-31 hour honest range instead of promising 20 hours.
