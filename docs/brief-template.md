# Worker brief template (canonical header for EVERY brief)

Every worker brief starts with this header, filled in for the task. A
brief that omits any section below is incomplete: run
`scripts/brief_check.py <brief-file>` before sending it. The checklist
it points to is `docs/worker-brief-checklist.md`; the rules here are
the ones workers kept repeating because a brief omitted them.

## 1. Task

- What to do, in one paragraph. The exact outcome, not the method.
- Which repo, which branch, which files. Where results go.

## 2. Source workflow (research first, A1)

- The worker's FIRST step is RESEARCH: re-read the whole workflow,
  tutorial, or instruction source in full before acting.
- Write the plan as steps taken from the source, in the source's order.
  Never skip, cut, or reorder steps. If a step looks wrong, stop and
  ask instead of silently dropping it.
- Name the source files/URLs and their dates here. A step with no
  source does not exist.

## 3. Saved working method (reuse verbatim, A2)

- If a method already worked for this exact task, write it here in
  full (which browser, which tab/session, which driver, which
  commands) and the worker MUST reuse it verbatim. Never let the
  worker invent a different approach for a task with a saved method.
- The proven browser method: the user's chosen browser only, the
  already-logged-in tab, the session driver. Never a different
  browser, never a fresh login, never typing a URL key by key (B10,
  B11).

## 4. All lessons for this task (A3)

- List EVERY known error and fix for this task, not a summary. Attach
  the task's lessons file. A worker cannot avoid a mistake it was
  never told about.

## 5. Progress, blockers, stalls (A4, A5, A6, C7)

- Stuck more than 3.5 minutes on one step: report it immediately.
- Stuck more than 15 minutes: report to the coordinator immediately.
- A stuck worker gets killed at once, not asked about first.
- Progress is reported every 5 minutes at most. Silence is not
  progress. When a task finishes, say so at once and start the next
  one; never wait to be asked.
- Long-running processes launch FULLY DETACHED
  (`setsid nohup ... > log 2>&1 < /dev/null & disown`).
- Holder/session lifecycle: never timeout-kill or SIGTERM the holder;
  stop via the stop file. After an abrupt holder death, wait ~10 min
  and poll session creation instead of relaunching blind. Record the
  runner identity (PID, or subagent session id for lanes with no OS
  PID) and task_start in the state file at every task start, and
  clear both at drive end; a stale task_start can make a watchdog
  kill a live idle process.
- NARRATE BEFORE ACTING (C7): when driving computer-use live while
  the user watches, say each step out loud BEFORE doing it (which
  button/link, what action, in plain short words). A static screen
  reads as doing nothing. When a phase is all code/terminal work
  with nothing visible, say so upfront and show concrete log
  evidence of progress. Acquire the overlay first
  (`scripts/overlay.py acquire --agent <name> --method <method>`)
  so the user sees who is driving, and release it when done.
- Timing/logging is ALWAYS ON: every test timed precisely (wall-clock
  Asia/Ho_Chi_Minh + elapsed) and logged fully (`scripts/timing.py`,
  `scripts/drive_log.py` for direct driving).

## 6. Verify, do not invent (A7, A8)

- Every claim needs a source and an access date. Say "I don't know"
  instead of inventing. Use `scripts/claim_check.py` tripwires before
  asserting anything a previous session fabricated.
- A worker's "not found / doesn't exist" is not proof of absence.
  Re-check yourself; search the web first (Google first when stuck).
- Never relay a subagent's diagnosis as fact without checking it.
- If the same approach fails the same way 2-3 times, stop, rethink,
  and change approach.
- Fixture and answer-key freshness preflight: before a task runs,
  confirm fixtures are in-window and answer keys match the live
  versions they grade against (a stale key version once graded a
  correct live answer wrong). Record the check in the brief.

## 7. Browser rules (Zen)

- KEYBIND/COMMAND FIRST (hard rule, owner 27/11): whatever can be
  done with a keybind or command, use the keybind/command. Limit
  vision/screenshot use to cross-checks only, to save time. Verify
  every keybind against the live config, never against docs defaults
  alone (docs defaults have been wrong on this machine before).
- NEVER press Ctrl+T in Zen: it opens a new window (Ctrl+N is the new
  tab). The driver refuses Ctrl+T into a Zen window (C3).
- Workspace switching and the Omarchy menu are done by COMMAND, never
  by clicking the bar (J21, 4.28): workspace via
  `hyprctl dispatch "hl.dsp.focus({ workspace = N })"`; Omarchy menu
  via `omarchy-menu toggle root` (bound to SUPER+SPACE in
  ~/.config/hypr/bindings.lua). The far-left rail top icon (15,30) is
  the app launcher, not workspace 1. Log every click (what, where,
  result) so a mis-click is attributable.
- NEVER type a URL with per-character key events (B11). Use the
  already-open tab, or the DOM goto/fill action.
- NEVER Ctrl+L in a file picker: it opens the URL bar. Click the
  picker to focus, then type the path directly.
- Buttons that need hover feedback (for example Polygon Browse) use
  `hover_click`: move off-center until the button darkens, then click
  at the same off-center point (B9).
- Never start work before the user says GO. "Ready" is not GO.
- Never report "ready" without a live check (login state, session
  state, file presence).
- BROWSER RESTART (R16, decided 2026-11-27; full procedure in
  `docs/browser-restart-procedure.md`): no watch ever kills or
  restarts a live browser. Revive-dead only: the health watch may
  relaunch only when no browser process exists AND the automation
  ports are down on two consecutive checks, logged. A live restart
  is coordinator/human-initiated at a task boundary, never mid-drive:
  record open tabs (including pinned and essential) via BiDi list
  dump to a file first, restart through the wrapper, then verify
  ports up, pill visible, session restore, owner essentials present.
  Memory threshold is 8 GB RSS (uncalibrated placeholder); record
  RSS + headroom at every boundary to calibrate. The same
  record-before / verify-after checklist and the R6 guardrail govern
  agent-initiated tooling restarts (e.g. sessionstore surgery),
  whoever initiates. The procedure is not "ready" until a
  throwaway-profile drill passes on the real mechanism.

## 8. Channels and process (D1-D5)

- Channel separation (D1): a follow-up belongs to its own thread.
  Never raise one thread's task in another channel. The main chat is
  the schedule channel.
- Messenger (D2): check the user's messages through Muse's own
  connectors only. Never open Messenger in the laptop browser.
- Push to GitHub as you go (D3): every small piece of work is its own
  commit, pushed immediately. Never hold a push to batch it later.
- Record lessons in both places (D4): a generic version in the repo,
  a detailed version on the laptop. Never put personal information
  in the repo.
- Calendar edits (D5): before ANY add/edit/delete/move, read the
  WHOLE day on ALL calendars plus adjacent days, account for travel
  time on location changes; after the change, run the overlap audit
  and confirm 0 overlaps. Never run parallel calendar writes.

## 9. Ban list (in EVERY brief, no exceptions)

- NEVER use ydotool.
- NEVER use OpenRouter.
- NEVER route to gpt-reserve. Use the designated executor model for
  everything.
- NEVER ask the user to enter an account or password, and never show
  a secure-entry card for a sign-in unless the user explicitly asks
  for it. A password step means stop that provider.
- NEVER put personal information (real names, addresses, emails,
  phone numbers, schedules, photos, accounts, passwords, tokens) on
  GitHub or any public place. Personal information stays local.

## 10. Polygon tasks (only when the task is a Polygon upload)

- Statement language is english (content stays Vietnamese). If both
  an english and a vietnamese statement exist, delete the vietnamese
  one. See `docs/polygon-upload-runbook.md`.
- Contest links use the hash format from the Polygon copy button
  (`https://polygon.codeforces.com/<hash>/<owner>/<slug>`). Never
  use the `/p/<id>/<slug>` link: Codeforces rejects it.
- Verification failed is not a stop rule. Only an invalid tests
  numeration blocks packaging. Never invent a stop rule the tutorial
  did not state.
- Run `scripts/polygon_checks.py` on the problem directory before
  every commit and before adding to Codeforces.
