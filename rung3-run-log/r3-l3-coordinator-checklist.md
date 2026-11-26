# R3-L3 coordinator checklist (run phase, epoch 12)

Owner: run coordinator (epoch 12, 0ef54a8e). Created 2026-11-26 for redteam checks 11-12.
Standing rules for every brief: ponytail (code work), graphify for codebase context, ydotool BANNED, pill "Computer use active" on any agent control, user-path test rule (entry point + forbidden shortcuts filled; end-state-only evidence returned unread), event-log duty via ~/workspace/agent-event-log/log-event.sh, never assume an agent capability, explicit delivery path in every brief, git explicit pathspec add+commit, no personal info on GitHub, English for agent work.

## Check 11 - Re-proof trigger (ARMED)

Any bot-wall invalid on a shimmed drive triggers council + redteam gate re-check before further releases on that site class.
- Site classes: timeanddate class first (R3-036, R3-046 remaining; R3-028 passed 2026-11-26 with probe webdriver false, no block). Then: namechk class (R3-027 invalid event 5, no remaining exposure), coolors class (known cold limit, zero remaining exposure), Google sorry class (not shim-covered, INVALID path).
- Stop behavior: on a bot-wall invalid on a shimmed drive, the coordinator stops further releases on that site class, records the invalid per section 1 (stop, Ray ID, 60-second wait), notifies the parent, and convenes council + redteam for a gate re-check before any further release on that class. Other site classes continue.
- Invalid budget state at arming: events 5/5 EXHAUSTED (R3-027 namechk = event 5). A 6th event needs a new recorded team decision via the parent BEFORE further releases. R3-036/R3-046 shared-cause (timeanddate) drops add 0 events only with browser evidence + scorer-2 confirmation.
- Probe rule (check 5, standing): every drive starts the holder, probe fail-loud (webdriver false, own_on_proto true, own_on_navigator false, get_name "get webdriver", toString verbatim), result in snapshot manifest chain AND recorded in every per-task drive report (webdriver value + holder/probe/shim hashes verified). Mismatch stops the drive; never drive unshimmed.
- Warm-profile rule (check 6, standing): no cookie clears on run hosts mid-run without coordinator approval recorded in advance.

## Check 12 - Watch-item guards (F12 verbatim in briefs)

- R3-079 runner brief: rung3-run-log/briefs/R3-079-runner-brief.md (F12 coupled reset pre-check verbatim). Position ~43. Verify by grep before release.
- R3-089 runner brief: rung3-run-log/briefs/R3-089-runner-brief.md (F12 fixture guard verbatim). Position ~49. Coordinator owns refresh: day before R3-089 runs, and 2026-11-30 12:00 guard refresh EVEN IF not reached (fixture expiry 2026-12-01 08:59). Refresh record: rung3-run-log/r3-l3-r3-089-refresh.md (date, time, who, count, new expiry). Confirmation after reset, before runner: find -mtime -7 on live ~/rung3/nd09-logs/ = exactly 6.
- R3-100 runner brief: rung3-run-log/briefs/R3-100-runner-brief.md (F12 port guard verbatim). Position ~55. Graded from saved files only.

## Per-drive standing steps

1. Holder hash verify before every drive (holder 70bfe8ab...213, probe 5329a574...c1f9, shim bb49ff3f...630b8). /tmp ephemeral: re-transfer by base64 pipe + re-verify if wiped. No drive on hash mismatch.
2. State-write discipline (fix-review R1): at every task start write task_start + runner identity atomically (temp file + rename, G-48): runner_pid for OS-process lanes, claude_runner_session for the Muse lane (no OS PID by design; never invent one). During long drives refresh last_updated/heartbeat at least every 10 min so the liveness watch sees a live coordinator. At drive end clear task_start + runner identity. Timeout watch kills by exact PID at 30 min (Muse lane: coordinator closes the subagent). FCC pane PID 22399 is PERSISTENT, never killed, never left as recorded runner PID. Verdict logic lives in rung3-ci/signal-hygiene.py (completed-task guard, deadline suppression); test: rung3-ci/test-signal-hygiene.py.
3. One driver at a time on shared Zen (ws2). Backpressure max 2 unscored per runner. Class L: score before reset.
4. Snapshot: delete evidence-dir manifest.json BEFORE snapshot.py (self-hash lesson). pii-scan.py before every snapshot push. Explicit pathspec git add + commit, ls-remote verify.
5. Verdicts filed in ~/workspace/rung3-verdicts (VM-local, never committed) as R3-xxx-A1/A2/B1/B2.json before ledger row. validate-ledger.py + ledger-cross-check.py exit 0 before push.
6. Tab hygiene: close finished task tabs; NEVER owner tabs, pinned, essentials, ws3. Cleanup after use.

7. Clean ledger validation (R19, team decision 27/11/2026): never execute validate-ledger.py / ledger-cross-check.py or git from inside this worktree (execution-risk guard: hooks/filters can run code). At each ledger push and at run close: copy rung3-ci/clean-validate-ledger.py to /tmp and run the copy (python3 /tmp/clean-validate-ledger.py --repo-root <worktree>). It copies the validators + inputs (verdict dir first, order file, ledger last) read-only to a scratch dir outside the tree, records the todolist-push head SHA, and prints both exit codes + row count. Log the result (exit codes, SHA, rows) to the master event log. Test: rung3-ci/test-clean-validate.py.

## Notification points (via parent, do not stop unless stated)

Ledger repair completion/blocker; any 6th invalid event or threat; each further drop; task 56 tab ambiguity; valid-50 reconvene; bar unreachable (rule-A fails reach 3); DP-05 use; R3-089 guard refresh done; closure.
