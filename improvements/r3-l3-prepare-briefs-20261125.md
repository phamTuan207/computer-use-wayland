# R3-L3 Prepare: lane briefs re-issued (G-26) and acknowledged (G-30)

- Date: 2026-11-25, 09:04-09:11 +07. Worker: Phase 0 prepare worker (briefs only). The run has NOT started. No run task was run.
- Gates addressed: G-26 (lane briefs re-issued carrying the re-plan rules) and G-30 (FCC and Codex acknowledge their lane briefs in writing before task 1). A tmux READY prompt alone does not satisfy G-30; both acks below are written replies to the NEW L3 briefs.

## Brief files (VM, run worktree)

- FCC lane brief: ~/workspace/r3l3-run-wt/improvements/r3-l3-lane-brief-fcc-L3-20261125.md (10,656 bytes)
- Codex lane brief: ~/workspace/r3l3-run-wt/improvements/r3-l3-lane-brief-codex-L3-20261125.md (12,707 bytes)
- Synced to the laptop: /home/james/r3-l3-lane-brief-fcc-L3-20261125.md (sha256 f5ee0a48b0f9f724d8887a3317c0ade2aaae8e5e58669e5eb9b82906e529a5fa) and /home/james/r3-l3-lane-brief-codex-L3-20261125.md (sha256 0b63d992fc4fb3990d97a8bab9f2249bd6a70395de7a417c6a6402a2fe2c21ba).

## What was wrong with the old briefs (verified first-hand)

- Laptop files /home/james/rung3-runner-brief.md, /home/james/rung3-runner-brief-fcc.md, /home/james/rung3-fcc-runner-brief.md are R3-L1 era (23/11, one dated 24/11 05:43). They list R3-082 expected values as 55, 75, 70, 68, 30 (frozen key: 71, 78, 120, 89, 25) and the batch brief names R3-002 as the first task instead of R3-001. Both errors are corrected in the new briefs. The three old files are declared VOID in the new FCC brief; the R3-L1 Codex brief is declared VOID in the new Codex brief.
- FCC had already acknowledged the stale briefs this morning (pane showed its reply at 09:01). That ack does NOT count for G-30. The new ack below supersedes it.

## New briefs: rules carried (from the re-plan)

- Both: first task R3-001 (FCC) / R3-040 (Codex); one task at a time, sequential; 10-minute heartbeat into the shared append-only JSONL log file (file-based fallback, not the daemon); stop at the task boundary; pill-before-drive (pill MUST show on any live drive); explicit-pathspec git rule (runners never commit; only the coordinator commits); no banned model routes (NO OpenRouter); no personal data in repo text; worker self-stop F-01 (cannot reach the coordinator: finish the current task, preserve evidence, do NOT start the next); evidence plus snapshot per task (-L3 suffix mandatory); 30-minute timeout is FAIL, stop, log; single driver, session free only by /proc fd scan for cursor.lock; run does NOT start until the coordinator releases task 1; do NOT start any task until assigned.
- Codex only: durable trace per codex exec invocation (task ID, session ID, launch command before launch; PID immediately after spawn, verified by ps); retry ONLY after checking the evidence dir and runner state; if a partial drive is recorded, re-run from the start on a clean fixture, never resume.
- No credential value in either brief. No R3-029 password in any brief or file. No em dash or en dash in either brief (verified: 0 occurrences).

## FCC written acknowledgement (verbatim, tmux r3-fcc-runner-L3, 09:06 +07)

Delivered by pasting the brief path into the FCC tmux session and asking FCC to read it. FCC read the file ("Read 1 file") and replied:

> ACK, FCC R3-L3 lane brief read, positions 1-28, first task R3-001, R3-082 values 71/78/120/89/25, waiting for task 1 from the coordinator. I will not start any task until assigned.

- Gate G-30 for FCC: SATISFIED (written ack of the NEW L3 brief).

## Codex written acknowledgement (verbatim, live codex exec, session 01a21076-155a-76e0-8035-ec559e3cf6af)

- Launch trace (recorded before launch): task ID ACK-CODEX-L3-20261125 (acknowledgement only, not a run task); launch command `codex --no-daemon -m gpt-6-luna --sandbox danger-full-access -C /home/james exec --skip-git-repo-check "<prompt>"`; launched 2026-11-25 09:08:23 +07 from /home/james; PID 38470, verified by ps immediately after spawn; process exited after replying; full log /home/james/r3-l3-codex-ack.log (14,276 bytes, 18,399 tokens).
- Codex read the brief and replied (verbatim, twice in the log, once as its final message):

> ACK, Codex R3-L3 lane brief read, positions 29-55, first task R3-040, R3-082 values 71/78/120/89/25, durable trace and retry rules understood, waiting for task 1 from the coordinator. I will not start any task until assigned.

- Codex also said before reading: "Toi se chi doc brief duoc chi dinh va trich nguyen dong ACK o muc 14, khong chay hay bat dau task nao." (It would only read the named brief and quote the ACK line from section 14, and run or start no task.)
- Gate G-30 for Codex: SATISFIED (written ack of the NEW L3 brief). This closes the gap Codex stated in live codex exec session 01a2106e ("I don't have the Codex lane brief for R3-L3 positions 29-55, so I'm not ready to run it today").

## Blockers and notes for the coordinator

- No blockers. Both acks obtained on the FIRST attempt each. No retry was needed.
- Discrepancy to resolve (not blocking this task): re-plan section 6 says "The runner (Codex, position 25)" for R3-029, but the canonical run order (thu-tu-chay.txt, tip ccd83e5) and the FCC batch list both put R3-029 at position 25 in the FCC lane (positions 1-28, R3-001 to R3-037). The new briefs follow the canonical run order: R3-029 is FCC lane, position 25, and its credential comes in the FCC task brief only. The coordinator should confirm or correct the re-plan line before position 25.
- The run has NOT started. Neither runner has been assigned any task. Both are waiting for task 1 from the coordinator.
- No file was committed by this worker. Paths above are ready for the parent to commit.
