# R3-049 Snapshot S1 — EMPTY EVIDENCE

Task: R3-049 (Tier B, lookup on calculator.net: 3 loans, monthly payment + total interest, 3 screenshots + ket-qua.txt).
Runner: Codex (codex exec 0.172.0, gpt-6-luna, detached).
Run: attempt 1 started 13:17 +07, ended ~13:20 (81,850 tokens); attempt 2 started ~13:20, ended ~13:25 +07 (119,636 tokens).

## What happened
Attempt 1: Codex opened a new Chromium window, calculator.net reported a process crash, results page did not load. Codex gave up, ended session driver. No evidence.
Attempt 2: calculator.net loaded (retry fixed the transient Chromium crash). Codex entered loan data, but the form input/submit stopped because the driver reported a field not visible and ended the session. No loan results read. Codex reported "R3-049 — chưa hoàn thành" (not completed) and ended the session driver. No evidence.

## Evidence
NONE. The evidence dir /home/james/rung3-chung-cu/R3-049/ was EMPTY at Codex completion (verified 13:26 +07). No loan1.png, loan2.png, loan3.png, no ket-qua.txt. The main Chromium process (PID 56452) stayed alive; the failures were a renderer/GPU subprocess crash (attempt 1) and a driver field-not-visible error (attempt 2).

This snapshot contains only this NOTE file. Scorers must judge R3-049 from this absence of evidence.

Coordinator: coord10 (fb3ec38b), 2026-11-24 13:26 +07.
