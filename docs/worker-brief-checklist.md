# Worker brief checklist: every lesson, every brief

Every one of these rules exists because the exact mistake already happened
and cost real time. Before writing ANY worker brief, check every box that
applies. A lesson omitted from the brief will be repeated by the worker.

The brief itself must contain: the full task, the exact source workflow,
this checklist (or the items that apply), and the ban list at the bottom.
Never write a brief from memory when a source exists.

## 1. Research first (A1)

- The worker's FIRST step is RESEARCH: re-read the whole workflow, tutorial,
  or instruction source in full before acting.
- Write the plan as steps taken from the source, in the source's order.
- Never skip, cut, or reorder steps on your own. If a step looks wrong,
  stop and ask instead of silently dropping it.
- If you forgot the workflow, re-read the source before acting. Do not
  reconstruct it from memory.

## 2. Save the working method, reuse it verbatim (A2)

- When a method works on a real task, save it exactly (which browser, which
  tab/session, which driver, which commands) and reuse it VERBATIM for the
  next identical task.
- Never let the worker invent a different approach for a task with a saved
  working method.
- The proven browser method: the user's chosen browser only, the
  already-logged-in tab, the session driver. Never a different browser,
  never a fresh login, never typing a URL key by key.

## 3. Give ALL lessons (A3)

- The brief lists EVERY known error and fix for this task, not a summary.
- Include this checklist plus the task's own lessons file.
- A worker cannot avoid a mistake it was never told about.

## 4. Tell the user first (A9)

- When a required input is missing (a solution file, a credential, a
  decision only the user can make), tell the user BEFORE writing or
  deciding it yourself.
- A self-written artifact buried in a long report does not count as
  telling. A material fact gets its own short message.

## 5. Brief rules from past failures (I32-I40)

- I32: never Ctrl+L in a file picker. In the user's browser it opens the
  URL bar. Click the picker to focus, then type the path directly.
- I33: in the user's browser, Ctrl+N is a new tab and Ctrl+T is a new
  window (swapped). Never use Ctrl+T.
- I34: follow the tutorial's order exactly (for example, checker before
  solution). Never invert steps.
- I35: never start work before the user says GO. "Ready" is not GO.
- I36: never report "ready" without a live check (login state, session
  state, file presence). A guess is not a check.
- I38: never ask the user to click, type, run a command, or drive the
  mouse for you. Do it yourself with the tools you have.
- I39: keep each thread's topic in its own thread. Never raise one
  thread's task in another channel.
- I40: a material fact (for example, a solution you wrote yourself) gets
  its own short message, never one line buried in a long report.

## 6. Stuck, blockers, and reporting

- Stuck more than 3.5 minutes on one step: report it immediately.
- Stuck more than 15 minutes: report to the coordinator immediately.
- A worker that is stuck gets killed at once, not asked about first, and
  the user is told it was stuck.
- Report a blocker as soon as it becomes one. Never let a worker retry
  silently for an hour.
- A long-running process is launched FULLY DETACHED
  (`setsid nohup ... > log 2>&1 < /dev/null & disown`); an attached
  process keeps its parent from ever completing.
- Progress is reported every 5 minutes at most. Silence is not progress.
- When a task finishes, say so at once and start the next one; never wait
  to be asked.

## 7. Verify, do not invent

- Every claim needs a source and an access date. Say "I don't know"
  instead of inventing.
- A worker's "not found / doesn't exist" is not proof of absence.
  Re-check yourself; search the web first (Google first when stuck).
- Never relay a subagent's diagnosis as fact without checking it.
- If the same approach fails the same way 2-3 times, stop, rethink, and
  change approach. Do not keep pushing the same way.
- Never invent extra steps, conditions, or rules for a tutorial workflow.
  Follow the tutorial exactly.

## 8. Operator runbook (technical)

- SSH to the laptop dies after about 30 seconds. Long jobs run detached;
  check progress with short commands.
- Plain SSH without `-i` and `IdentitiesOnly=yes` fails with Permission
  denied. Always use the provided SSH wrapper script.
- The agy CLI cannot run non-interactive over SSH (it needs an
  interactive login). Use fcc-claude for non-interactive agent runs.
- Live-site browsing from the VM's Chromium fails out of the box. Run
  `scripts/vm_proxy.py` and launch Chromium with
  `--proxy-server="http://127.0.0.1:18080" --ignore-certificate-errors`.
- Sign-in goes through the provider's account chooser only. Never ask the
  user for a password. A password step means stop that provider.
- When tagged in a group, reply in the group immediately (confirm or
  answer). Never process silently and leave people asking again.
- The image viewer binary is `imv-wayland`, not `imv`. Kill it after
  every photo: `pkill -x imv-wayland`.
- Hyprland Lua dispatch takes the `hl.dsp` object form only
  (`hl.dsp.window.close(...)`); the string-dispatcher form is broken.
- Editor geometry is floating, exactly 901x1176. Never let the window
  manager tile it.
- Leases live in `~/.cache/agent-computer-use/leases/` (mode 0700),
  never in /tmp.
- After every broker code change, restart the relay when idle (or refuse
  the sync while busy); the broker reports its loaded code hash and the
  sync verifies it. Never let a relay run stale code.
- Desktop observations and DOM snapshots expire after 120 seconds. Take
  a fresh observation before acting.
- JSONL appends go through `scripts/jsonlutil.py`: check the file ends
  with a newline before appending, and parse-verify after a push.
- Bound git output in scripts and briefs: prefer `git log -n <N>` and
  pathspec-limited queries over unbounded `git log --all` or full-history
  dumps, and batch repeated git calls instead of looping one call per item.
  This is scripting hygiene only; it claims no measured saving.
- Direct driving is logged to a file with wall-clock time
  (Asia/Ho_Chi_Minh) and elapsed time (`scripts/drive_log.py`), not only
  in chat history.
- Pill (liquid glass): copy the upstream shader exactly, only reduce the
  blur. Never invent a new displacement law. The user is the taste judge.

## 9. Channels, process, and live driving (D1-D5, C7)

- Channel separation (D1): a follow-up belongs to its own thread.
  Never raise one thread's task in another channel. The main chat is
  the schedule channel. (Already in section 5 as I39; repeated here
  because it is a process rule, not just a brief rule.)
- Messenger (D2): check the user's messages through Muse's own
  connectors only. Never open Messenger in the laptop browser.
- Push to GitHub as you go (D3): every small piece of work is its
  own commit, pushed immediately. Never hold a push to batch it.
  Mechanical log appends (append-only log files with no judgement content)
  are exempt from the small-commit rule and may ride along with the next
  commit instead of forcing a commit of their own.
- Record lessons in both places (D4): a generic version in the repo,
  a detailed version on the laptop. Never put personal information
  in the repo.
- Calendar edits (D5): before ANY add/edit/delete/move, read the
  WHOLE day on ALL calendars plus adjacent days, account for travel
  time on location changes; after the change, run the overlap audit
  and confirm 0 overlaps. Never run parallel calendar writes.
- Narrate before acting (C7): when driving computer-use live while
  the user watches, say each step out loud BEFORE doing it. A static
  screen reads as doing nothing. Acquire the overlay first
  (`scripts/overlay.py acquire --agent <name> --method <method>`)
  so the user sees who is driving, and release it when done.

## Ban list (in EVERY brief, no exceptions)

- NEVER use ydotool.
- NEVER use OpenRouter.
- NEVER route to gpt-reserve. Use the designated executor model for
  everything.
- NEVER ask the user to enter an account or password, and never show a
  secure-entry card for a sign-in unless the user explicitly asks for it.
- NEVER put personal information (real names, addresses, emails, phone
  numbers, schedules, photos, accounts, passwords, tokens) on GitHub or
  any public place. Personal information stays local.
