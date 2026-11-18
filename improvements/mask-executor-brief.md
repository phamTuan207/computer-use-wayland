# Mask executor brief: observation masking, baseline arm vs masked arm (Pick 5)

- Owner: Pham Tuan. Repo worktree: /home/james/computer-use-wayland-masking,
  branch speed-swarm-masking (origin/speed-swarm-masking). NEVER work in
  /home/james/computer-use-wayland (the live checkout; other pick workers
  are running there). NEVER restart the relay. NEVER touch the broker.
- Implementer of the prototype: Luna 6 Max. Date: Thu 2026-11-19, early.
- Prototype: scripts/mask_history.py, tests in tests/test_mask_history.py.
  Flag: CU_MASK_HISTORY=1, default off. Masking is a deterministic local
  RULE, not an LLM summarization: no extra model call, no summarizer.
- You are Luna 6 Max, a measurement executor. You run ON this laptop
  (james). NEVER use ydotool. NEVER touch his Jarvis Codex, his Zen tabs,
  his Zalo, Teams, music, or the cancel latch. Never use `pkill -x codex`
  for any reason. No code changes, no repo edits, no reboot, no logout.
- No em dash or en dash in anything you write, per standing rule.

## What masking does (read first)

Prior art 3.1 (The Complexity Trap, Lindenbauer, arXiv 2508.21433):
observation tokens are about 84 percent of an average turn. Masking
halves cost and matches LLM summarization on solve rate, with ZERO
extra model calls. Prior art 3.4 (OSWorld-Human): screenshot-only
history does NOT improve performance, only text history helps; each
successive step can take 3x longer than steps at the beginning, because
history accumulates. Prior art 2.12: long context raises per-token cost
3.6x to 7x even with caching.

The prototype keeps only the latest 2 screenshots in full; older
observation images become one text line each,
"[screenshot N masked: <one-line description of what it showed>]";
reasoning and action history stay in full. The current observation is
ALWAYS fresh pixels; masking applies only to HISTORY, never to the
observation you are acting on now. Never mask the latest screenshot.

## Arms

- BASELINE arm (run first): flag OFF, normal loop, exactly the v3
  optimized discipline. Kitty title `mask-base-term`. Run dir
  /tmp/speed-mask/mask-base. Session owners `mask-base-p1` and so on,
  lease dirs `~/.cache/agent-computer-use/leases/mask-base-p1/` and so on.
- MASKED arm (run second): flag ON in YOUR shell only:
  `export CU_MASK_HISTORY=1`. Nothing else changes. Kitty title
  `mask-pick-term`. Run dir /tmp/speed-mask/mask-pick. Session owners
  `mask-pick-p1` and so on, lease dirs
  `~/.cache/agent-computer-use/leases/mask-pick-p1/` and so on.
- The flag lives in the executor shell only. Masking runs in your own
  shell through the mask CLI; the relay never sees it. NO relay restart
  is needed for either arm, and NO repo restore is needed after the run:
  the flag defaults off, so the tree is baseline by default.
- In both arms, `__ARM__` below means `mask-base` or `mask-pick`,
  and `__RUN_DIR__` means /tmp/speed-mask/mask-base or
  /tmp/speed-mask/mask-pick. `__TERM__` means mask-base-term or
  mask-pick-term.

## Masked arm protocol (masked arm ONLY; baseline arm skips this section)

After EVERY observe, append one turn to `__RUN_DIR__/history-<task>.jsonl`
(one JSON turn per line) with the one-line description of what the
screenshot showed, written by YOU in the same think call that already
read the image. No extra call writes it. Turn shape:

{"n": 1, "label": "obs1", "observation": {"image": "<image path>",
"description": "<one line, what the screenshot showed>",
"window": "<window address>"}, "reasoning": "<your reasoning, short>",
"action": "<the action you then took, short>"}

Before EVERY think call that follows an observe, build the masked
prompt with the CLI (from the masking worktree):

CU_MASK_HISTORY=1 python3 /home/james/computer-use-wayland-masking/scripts/mask_history.py prompt --history __RUN_DIR__/history-<task>.jsonl --current __RUN_DIR__/current-<task>.json --out __RUN_DIR__/prompt-<task>-<n>.json

Write `current-<task>.json` first: one observation dict
{"image": "<latest image path>", "description": "<one line>",
"window": "<address>"}. The CLI output gives image_paths (at most 2)
and masked_count. VIEW ONLY the images in image_paths. NEVER re-open
a masked observation image. When you verify, read only the latest
observation image (tesseract OCR). If the CLI ever lists more than 2
images, STOP, record BLOCKED-mask-cap in the summary, and report.
Log the CLI call first:
`echo "$(date '+%H:%M:%S.%3N') MASK <label> images=<n> masked=<n>" >> __RUN_DIR__/mask.log`

## Baseline arm

Follow the v3 optimized discipline exactly (one observation, ground all
controls, batch actions in one act request, re-observe only to verify).
Do NOT apply any masking rule. Do NOT write history files. Log DECIDE
lines exactly as below. This arm is the control.

## Tasks (both arms, same order, same end states)

Do the tasks in order P1 to P4. Fresh broker session per task. Same kitty
terminal window reused across tasks in the same arm (title `__TERM__`).

- P1 C-03: "O dia con trong bao nhieu?" Run `df -h /` in the terminal and
  report the free space of `/` from what you OBSERVE on screen. End state:
  correct free-space answer, read from the terminal output via broker
  observe. Session owner `__ARM__-p1`, lease
  `~/.cache/agent-computer-use/leases/__ARM__-p1/p1.lease`.
- P2 E-04: "144 tren 150 la bao nhieu phan tram?" Run
  `python3 -c "print(144/150*100)"` and report the answer from the observed
  terminal output. End state: correct answer (96.0). Owner `__ARM__-p2`,
  lease dir `__ARM__-p2`.
- P3 B-01: "Tao trong /tmp thu muc hoc-ky-2, trong do co 3 thu muc con: dsa,
  ktvm, oop." Run `mkdir -p /tmp/hoc-ky-2/dsa /tmp/hoc-ky-2/ktvm /tmp/hoc-ky-2/oop`
  then `find /tmp/hoc-ky-2 -type d` and verify all 4 dirs from the observed
  output. End state: the 4 directories exist. Owner `__ARM__-p3`, lease dir
  `__ARM__-p3`.
- P4 A-01: "Tao file y-tuong.txt trong /tmp, ghi 3 dong." The 3 lines, exact
  Vietnamese with diacritics, must be byte-exact: line 1 "Ý tưởng 1: app
  nhắc uống nước.", line 2 "Ý tưởng 2: bot tóm tắt bài giảng.", line 3
  "Ý tưởng 3: web bán đồ secondhand." Write the file with one printf
  command, then `cat /tmp/y-tuong.txt` and verify the exact 3 lines from
  the observed output. End state: /tmp/y-tuong.txt with exactly those 3
  lines. Owner `__ARM__-p4`, lease dir `__ARM__-p4`.

DIRT CHECK (before P3, P4): if /tmp/hoc-ky-2 or /tmp/y-tuong.txt already
exists before its task starts, the run is dirty (a previous arm left it).
STOP, record BLOCKED-dirty in the summary, and report. Do NOT delete them
yourself; the coordinator cleans between arms. Verify dirt only by
OBSERVING the terminal (`ls` in the terminal through the broker), never
by reading files in your own shell.

## Optimized discipline (both arms)

- One observation, then ground ALL needed controls from it, then send as
  many actions as possible in ONE batched act request (up to 32 actions).
  Re-observe only to verify the end state or on surprise. Never do one
  action then one observation as a habit.
- Selective observation: observe requests use image_policy "always". Act
  requests use image_policy "auto" (the broker then only delivers the
  after-image when the frame actually changed). Never request an
  observation that proves nothing new.
- Local execution: you run on this laptop; there is no VM SSH hop inside
  the loop. Do not add any remote hop.

## Broker access (the ONLY way you touch the desktop)

- Wrapper: `python3 __RUN_DIR__/timed.py --log __RUN_DIR__/records.jsonl <command>`
  (timed.py is copied into the run dir by the coordinator; it is the fixed
  v3 wrapper that preserves the full broker result payload and chmods
  request files to mode 600).
- Start: `timed.py start --owner __ARM__-p1 --lease-file ~/.cache/agent-computer-use/leases/__ARM__-p1/p1.lease --label p1-start`
  (lease dir per task, mkdir -p first, chmod 700 the dir).
- Request: write the envelope JSON to a file first, e.g.
  `__RUN_DIR__/p1-req1.json`, chmod 600 the file, then `timed.py req
  --lease-file <lease> --seq 1 --request <file> --label p1-windows`.
  Sequence numbers start at 1 and increase by 1 per request in the same
  session. Never reuse a sequence number. Never call session_remote.py
  directly (except the one idle check in SETUP below).
- Status: `timed.py status --lease-file <lease> --label <label>`.
- Finish: `timed.py finish --lease-file <lease> --label <label>`.
- Envelope shapes (args are the cu.py driver commands):
  - windows: `{"args": ["windows"]}`
  - observe screen: `{"args": ["observe", "--screen", "eDP-2", "--max-width", "960"], "image_policy": "always"}`
  - observe window: `{"args": ["observe", "--window", "0x...", "--max-width", "960"], "image_policy": "always"}`
  - act: `{"args": ["act", "--observation", "<observation JSON path from the observe result>", "--actions", "<actions JSON path>"], "image_policy": "auto"}`
  - The observe result gives you the observation JSON path
    (record["observation_path"] or result["observation"]) and the image
    path (record["image_path"] or result["image"]). The act --observation
    argument needs that JSON file path, not an id. Write actions JSON to a
    file, chmod 600 it, e.g. `[{"type": "type", "text": "df -h /\n"}]`.
    One "type" action with trailing newline runs a terminal command. If a
    type action fails, retry with a key Return action instead and note it.
  - IMPORTANT: screen observations support pointer actions only, never
    typing. To type into the terminal you MUST observe its window
    (address from the windows list) and act on that window observation.
  - Keep --settle-ms at its default 0 unless the observed text looks torn
    mid-render; if you use it, log it as a settle with the ms value.
- First request within seconds of the session reaching ready. Keep every
  gap between requests under 240 seconds or the session dies on
  idle_timeout (300 s). If an observation is older than 90 s when you act,
  the act is refused as stale: re-observe and retry, and log the stale
  refusal.
- If a request returns accepted:false, report request_error verbatim,
  retry ONCE after a fresh observe, and if it fails twice record the task
  BLOCKED with the error and move to the next task. Do NOT spend more than
  5 minutes investigating harness source code; your job is measuring, not
  debugging the harness.
- If a session dies, note the wall time and the cause, delete the old lease
  file, start a FRESH session with a fresh lease dir, and continue. Never
  reuse a lease file after a restart (a reused lease replays the old start
  outcome).
- BROKER IS SINGLE-OWNER. If a session start is refused because another
  worker owns the lease, DO NOT fight it: sleep 60 to 120 seconds and
  retry, up to 10 retries, then record BLOCKED-lease and stop. Keep live
  sessions short: finish each task session before starting the next.
- BROKER-FREE CHECK (before each arm, and before P1): run
  `python3 /home/james/computer-use-wayland/scripts/session_remote.py status`
  (one plain call is fine for this check). If a session is actually
  running, do NOT start yours; wait 2 minutes and re-check, up to 30
  minutes, then report blocked. A state of finished or idle with driver
  stopped is free to start. If your start call itself returns a cancelled
  error, report BLOCKED and stop; do not touch the latch.

## Reading terminal output (verification)

The observation PNG is the only source of truth for what is on screen.
Read the text out of it with tesseract OCR: `tesseract <image path>
stdout` (tesseract is installed at /usr/bin/tesseract). The image path is
record["image_path"]. Use the OCR text to verify the end state. Never
verify by reading files or running commands in your own shell (that
bypasses the loop being measured).

## Decision logging (this is how the gap gets split; do it every time, except inside the scripted floor probe)

- Before EVERY timed.py call, run: `echo "$(date '+%H:%M:%S.%3N') DECIDE <label>" >> __RUN_DIR__/decisions.log`
- The label must match the timed.py --label for that call.
- Any sleep you insert must be logged first: `echo "$(date '+%H:%M:%S.%3N') SLEEP <seconds> <reason>" >> __RUN_DIR__/sleeps.log`. Prefer no sleeps at all.

## Setup (plain shell, not broker input; do this once before each arm)

- Work in the masking worktree for the prototype files only:
  `cd /home/james/computer-use-wayland-masking && git rev-parse --show-toplevel`
  must print /home/james/computer-use-wayland-masking. If it prints the
  live checkout, STOP and report. The tree may have uncommitted files from
  other workers: LEAVE THEM UNTOUCHED, never stash, never commit, never
  ask about them. NEVER stop before P1 for a git reason, and NEVER end
  your turn with a question: there is no one to answer it. If you are
  blocked, record BLOCKED with the cause in the summary and move to the
  next task.
- Run dir: `mkdir -p /tmp/speed-mask/__ARM__`. Copy timed.py and
  analyze.py from /tmp/speed-profile-20261118/ into `__RUN_DIR__`.
  Records file: `__RUN_DIR__/records.jsonl`. Decision log:
  `__RUN_DIR__/decisions.log`. Sleep log: `__RUN_DIR__/sleeps.log`.
  Mask log (masked arm only): `__RUN_DIR__/mask.log`.
- Export the mask flag for your own shell only on the masked arm:
  `export CU_MASK_HISTORY=1`. Baseline arm: make sure it is unset
  (`unset CU_MASK_HISTORY`). The flag never reaches the relay and no
  relay restart is needed for either arm.
- Source the env file: `source /home/james/backups/cu-final-0.57.2-20261114-225131/env.sh`
- Hyprland signature: the live instance dir is the one under
  `/run/user/1000/hypr/` that contains hyprland.lock (there are stale
  dirs; refresh_gui fails because of them). Export
  HYPRLAND_INSTANCE_SIGNATURE to that dir name before any hyprctl call.
  Re-detect it, do not assume a value.
- Launch one kitty terminal: `nohup kitty --title __TERM__ >__RUN_DIR__/kitty.log 2>&1 &`
  (with the GUI env exported). Then drive it only through the broker.
  Find its window address from the broker windows list (title __TERM__).
- Before every act, verify from your latest observation that the focused
  target is the __TERM__ window. If focus ever lands on any other
  window, STOP driving, finish the session, and report what happened.

## Floor probe (scripted, zero model calls; run AFTER P4 in EACH arm, BEFORE teardown)

Same shape as the v3 floor probe, labels `floor-*`, owner `__ARM__-floor`,
lease `~/.cache/agent-computer-use/leases/__ARM__-floor/floor.lease`:
start, windows, observe screen, observe window (address of __TERM__
parsed from the floor-windows record), act with one harmless type action
`[{"type": "type", "text": "\n"}]`, observe window again, finish.
Sequence numbers 1..6 in that session. All envelope/action files chmod
600. Record the probe wall start/finish in the summary.

## Verification and reporting

- Verify each end state ONLY from a broker observe of the terminal output
  (OCR of the observation image). Never verify by reading the files or
  running commands in your own shell.
- Per task, record wall start (session start submit) and wall finish
  (verified end state) times in `__RUN_DIR__/summary.md` as you go.
- If a task exceeds 30 minutes wall, finish its session, record it as
  BLOCKED with the cause, and move to the next task.
- Teardown after P4 and the floor probe, in EACH arm: close the test
  terminal gracefully with hyprctl dispatch `hl.dsp.window.close()` on
  its window (the object form; string dispatcher names are broken in
  Hyprland 0.57.2). Confirm no test window remains. Finish session P4
  cleanly (and the floor session, if not already finished).
- When all 4 tasks are done in an arm, write `__RUN_DIR__/summary.md`
  FRESH with: repo HEAD (masking worktree), per-task wall start/finish,
  total seconds, request counts by type (windows/observe/act/status),
  observations count, act requests, actions, SUCCESS/FAIL with the
  observed evidence (quote the OCR text you verified), any refusals or
  session deaths with cause, the floor-probe totals, and (masked arm
  only) mask stats per task (images kept vs masked from mask.log,
  prompt image counts), and any blocker. Also run:
  `python3 __RUN_DIR__/analyze.py __RUN_DIR__/records.jsonl __RUN_DIR__/decisions.log __RUN_DIR__/sleeps.log`
  and paste its output at the end of summary.md. Then stop. Do not start
  any other task.
- After BOTH arms, write the before/after table (one table, both arms)
  into /tmp/speed-mask/mask-before-after.md:

| Step | Baseline think (s) | Masked think (s) | Delta |
| --- | --- | --- | --- |
| think before windows |  |  |  |
| think before first observe |  |  |  |
| think before act |  |  |  |
| think before verify observe |  |  |  |
| think total (clean-task mean) |  |  |  |
| wall (clean-task mean) |  |  |  |
| broker service (clean-task mean) |  |  |  |
| SUCCESS (tasks / 4) |  |  |  |

Baseline anchor from the profile run (clean-task mean, P2-P4):
wall 36.4s, think 34.2s (94 percent), broker service 1.4s (4 percent);
think before act 14.9s, think before first observe 7.7s, think before
verify observe 6.7s, think before windows 4.9s. The question the table
answers: does masking cut think time, and does it cut the LATER steps
most (the steps where history is longest)? Report per-step think by
step index too, so the growth curve is visible. A masked arm that is
slower or loses a task is a real result: report it plainly, do not
hide it. Verdict is PROVISIONAL (non-Astra): Astra 6 is out of credit.
