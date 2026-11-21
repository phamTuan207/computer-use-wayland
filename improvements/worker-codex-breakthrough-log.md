# Worker CODEX-BREAKTHROUGH log

Role: launch Codex (Luna 6 Max) on the laptop as an INDEPENDENT auditor of computer-use, monitor it, deliver its report. I do not do the audit myself.
Log rule: wall-clock Asia/Ho_Chi_Minh + elapsed time for every step.

## Launch

- 06:03:15 (T+0s) Prompt + error file copied to laptop: /tmp/codex-breakthrough-prompt.md (3907 bytes), /tmp/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md (125534 bytes). Verified present on laptop.
- 06:03:xx Pre-launch state: codex-cli 0.169.0 on laptop. A DIFFERENT Codex already running: PID 774258, started 05:58, prompt /tmp/codex-amend4-prompt.md (COORD-CLICK-3 AMEND4 work). My audit is a second, separate Codex run: own prompt file, own output log, report to /tmp only, no repo writes. No conflict.
- 06:03:xx Laptop repo /home/james/workspace/computer-use-wayland on branch todolist-push, HEAD 4500a18.
- 06:04:15 (T+60s) Launched detached via /tmp/codex-breakthrough-launch.sh (proven demo pattern: setsid nohup codex exec -m gpt-6-luna -c model_reasoning_effort=max -s danger-full-access -C /home/james/workspace/computer-use-wayland - < prompt > /tmp/codex-breakthrough-out.log 2>&1 &). Codex PID 781223.
- 06:04:30 (T+75s) Verified running: PID 781223, elapsed 00:08, /tmp/codex-breakthrough-out.log 4333 bytes, hooks SessionStart + UserPromptSubmit completed.

## Monitoring

- (pending) Periodic short SSH checks: process alive, log size, report file /tmp/codex-breakthrough-report.md exists.
- 06:19:50 (T+15m35s) Check 1: PID 781223 alive, elapsed 15:28. /tmp/codex-breakthrough-out.log 1065280 bytes (was 4333 at launch). Report file NOT yet written. Log tail shows Codex synthesizing measurements into the report (Vietnamese: combining results with each measurement's limits). Still working, appears to be in the write-up phase.
- 06:29:59 (T+25m44s) Check 2: PID 781223 GONE (finished). /tmp/codex-breakthrough-report.md exists, 21557 bytes, written 06:20. Out log 1112694 bytes, last modified 06:21. Total wall about 16 min (launch 06:04:15 to report 06:20).
- 06:30:xx Retrieved report to VM, verified verbatim (diff clean, 21557 bytes), saved to improvements/codex-breakthrough-report.md. Checks: 0 em/en dashes, no email addresses in the report.

## Cover note (what Codex did, runtime, caveats)

- What Codex did: read docs/zen-error-fix-todolist-20261121.md, the full error file, scripts/cu.py, browser/accessibility adapters, broker/session driver, and the installed act-now code on the laptop. Only new measurement was a read-only synthesis of the existing act-now JSONL (199 lines). It ran no tests, controlled no windows/tabs, modified nothing in the repo.
- Runtime: launched 06:04:15, report written 06:20, about 16 min wall. Single session, Luna 6 Max, max reasoning, full access.
- Verdict: current direction UNSOUND as the main control loop (one image, model picks as many coordinates as possible). Core flaw: the contract reports success when input was sent, without proving the right element received it or the target state was reached (finding 2.1). Breakthrough proposal: a local semantic transaction executor (semantic targets, preconditions, real mouse/keyboard input, postconditions, retry only when surely unsent), vision kept as fallback, one local broker owning session/overlay/browser, DOM/BiDi + AT-SPI + screenshot-crop backends under one contract. 10 weaknesses total, each with file/line references.
- Caveats: (1) Report is in Vietnamese. (2) Codex could NOT verify the 66-rect/5-click DOM claim from its checkout: laptop checkout is todolist-push HEAD 4500a18, remote-tracking ref behind 622 commits, and it did not fetch origin, so the claim (which lives in clone2's report on main) was unverifiable from its vantage point. Not a refutation, an unverified-from-here. (3) SSH 95% of 12.26s claim also unverified: local logs start after the command reaches the laptop. (4) Finding 2.9: installed first_action.py is not in the repo and not git-tracked; the running laptop behavior depends on a wrapper the checkout cannot reproduce. Deployment drift is itself a finding.
