# H5 executor brief: drop old screenshots from history, baseline arm vs H5 arm (plus optional drop-text arm)

- Owner: Pham Tuan. Branch harness-drop-old-shots, HEAD 375df9e. H5 prototype
  worktree: /home/james/computer-use-wayland-dropshots (use it ONLY for
  scripts/h5_history.py). The live checkout /home/james/computer-use-wayland
  is detached at 375df9e by the coordinator; the relay was restarted by the
  coordinator (MainPID 1372783, started_git_head 375df9e verified, clean env,
  broker idle at arm start). Verify HEAD is 375df9e with
  `git -C /home/james/computer-use-wayland rev-parse --short HEAD` and record
  it; if it is not 375df9e, record BLOCKED and stop. Do NOT checkout, pull,
  stash, or otherwise touch git state anywhere. Do NOT restart the relay
  yourself. NEVER touch the broker except through the timed.py wrapper below.
- Implementer of the prototype: Luna 6 Max (continuation worker). Date: Thu
  2026-11-19, evening.
- Prototype: scripts/h5_history.py, tests in tests/test_h5_history.py
  (39/39 pass). Flags: CU_H5_DROP_OLD_SHOTS=1 (on, default off),
  CU_H5_KEEP_FULL (default 1), CU_H5_DROP_TEXT=1 (drop-entirely variant).
  H5 is a deterministic local RULE, not an LLM summarization: no extra
  model call, no summarizer.
- You are Luna 6 Max, a measurement executor. You run ON this laptop
  (james). NEVER use ydotool. NEVER touch his Jarvis Codex, his Zen tabs,
  his Zalo, Teams, music, or the cancel latch. Never use `pkill -x codex`
  for any reason. No code changes, no repo edits, no reboot, no logout.
- No em dash or en dash in anything you write, per standing rule.


STANDING RULES (no exceptions): NEVER use ydotool. No em dash (U+2014) or en
dash (U+2013) in any file, message, or summary you write; use commas, periods,
or a hyphen (-) only. Timing ALWAYS ON: log wall-clock Asia/Ho_Chi_Minh
times. Fastest path first: CLI/API, then DOM/a11y, screenshot/vision last. ONE
observation yields AS MANY actions as possible. Realistic tasks only; a "fixed"
claim without a passing live test is 0 points. Judge on WHOLE task wall time,
not think time alone. Work in small steps, a tool call every 2-3 minutes,
heartbeat lines to the progress log if a step runs long. Effort is
SESSION-LEVEL only (no per-call override exists in Codex CLI 0.169.0); do NOT
attempt a per-step in-session effort dial. M4 model routing is CLOSED (do not
route to gpt-reserve, use Luna for everything). Do NOT use Jedi-3B as a
grounder under any circumstance. Cleanup after every task (desktop clean, never
touch his Zen tabs, Jarvis, music). Push small commits to GitHub as work lands
(docs/log files only on speed-swarm; main stays FROZEN except approved
landings). Do NOT decide open items needing him (Step 3 design, save-dialog
Part B, H1-BASE recovery); note them instead.

## What H5 does (read first)

Harness-speed research section 2 H5, refining algorithm research A7/R7
with the FSP finding: screenshot-only history does not improve
performance; only text-based action history helps. Screenshot tokens are
typically 80 percent or more of total context. The executor's conversation
history accumulates a full screenshot per step; over a 5-step task that is
5 images in context. H5 keeps only the LATEST screenshot in the model's
context and replaces older screenshots with one short text line each:
"[shot N: <one-line description> | did: <action> | got: <result>]".
Reasoning and action text stay in full on every turn, always. The current
observation is ALWAYS fresh pixels and always occupies the one image slot;
pruning applies only to HISTORY, never to the observation you are acting
on now.

GATE ANSWER (checked 19/11, verified by the implementer): the Codex
executor does NOT support pruning old images from history, and there is
no harness history builder anywhere in the repo (scripts/cu.py holds zero
occurrences of "prompt" or "history"; the history lives in the Codex
executor's own transcript). Pruning is therefore executor-side discipline
via scripts/h5_history.py plus this brief, NOT a harness change, and the
relay never sees it, so NO relay restart is needed for any arm. This was
already proven by the masking prototype (scripts/mask_history.py on
branch speed-swarm-masking, 31/31 tests, live discipline verified: every
prompt carried exactly 2 images). H5 differs from masking in three ways,
which is why it is a separate measurement and not a re-run of masking:

- Keep ONE image, not two: the latest screenshot only (the current
  observation occupies the single slot; history keeps zero full images).
- The text line per old step carries the ACTION TAKEN and the RESULT,
  not just what the screenshot showed. FSP says only text action
  history helps, so the action plus result is the load-bearing text.
- A drop-entirely variant (CU_H5_DROP_TEXT=1) drops old turns with no
  text line at all, to test whether even the text lines cost think.
  This is a THIRD arm, optional, only if the coordinator asks for it.

Prior live result this measurement must beat or explain (Phase C masking,
04:19-05:18 19/11, verdict NO WIN provisional): masked (keep 2) slower
on every task, baseline mean wall 105.4s to masked 179.6s (+74.2s);
clean P2-P3 41.8s to 72.7s (+30.9s); broker service identical (2.3s
both arms), whole delta is think; before-act think 22.6s to 47.5s
(+24.9s). Per-step think growth FLAT in both arms; no history-growth
curve existed to cut at this task length (2-6 observations per task).
Confounders: P1 masked unusable (kitty incident), P4 masked session
death plus restart, n=1. H5 tests keep 1 (not 2) and adds a genuinely
multi-step task (M1, about 10 observations) where a growth curve can
actually exist. If H5 also shows no win, the history-pruning line is
closed with two independent negative measurements. A slower H5 arm or a
lost task is a real result: report it plainly, do not hide it.

## Arms

- BASELINE arm (run first): flag OFF, normal loop, exactly the v3
  optimized discipline. Run dir /tmp/speed-h5/h5-base. Session owners
  `h5-base-p1` and so on, lease dirs
  `~/.cache/agent-computer-use/leases/h5-base-p1/` and so on.
- H5 arm (run second): flag ON in YOUR shell only:
  `export CU_H5_DROP_OLD_SHOTS=1`. Nothing else changes. Run dir
  /tmp/speed-h5/h5-pick. Session owners `h5-pick-p1` and so on, lease
  dirs `~/.cache/agent-computer-use/leases/h5-pick-p1/` and so on.
- DROP-TEXT arm (optional third, only if the coordinator asks):
  `export CU_H5_DROP_OLD_SHOTS=1 CU_H5_DROP_TEXT=1`. Run dir
  /tmp/speed-h5/h5-droptext. Owners `h5-droptext-p1` and so on.
- The flags live in the executor shell only. H5 runs in your own shell
  through the h5 CLI; the relay never sees it. NO relay restart is
  needed for any arm, and NO repo restore is needed after the run: the
  flag defaults off, so the tree is baseline by default.
- In all arms, `h5-pick` below means `h5-base`, `h5-pick`, or
  `h5-droptext`, and `/tmp/speed-h5/h5-pick` means /tmp/speed-h5/h5-base,
  /tmp/speed-h5/h5-pick, or /tmp/speed-h5/h5-droptext.

## H5 arm protocol (H5 and drop-text arms ONLY; baseline arm skips this section)

After EVERY observe, append one turn to `/tmp/speed-h5/h5-pick/history-<task>.jsonl`
(one JSON turn per line) with the one-line description of what the
screenshot showed, the action you then took, and the result you observed,
written by YOU in the same think call that already read the image. No
extra call writes it. Turn shape:

{"n": 1, "label": "obs1", "observation": {"image": "<image path>",
"description": "<one line, what the screenshot showed>",
"window": "<window address>"}, "reasoning": "<your reasoning, short>",
"action": "<the action you then took, short>",
"result": "<what the result was, short>"}

If you have not recorded a field yet (for example no action taken after
an observe), write the field as an empty string; the CLI will mark it
"(no action recorded)" and never invents content. Never write a
description, action, or result you did not actually see or do.

Before EVERY think call that follows an observe, build the pruned prompt
with the CLI (from the H5 worktree):

CU_H5_DROP_OLD_SHOTS=1 python3 /home/james/computer-use-wayland-dropshots/scripts/h5_history.py prompt --history /tmp/speed-h5/h5-pick/history-<task>.jsonl --current /tmp/speed-h5/h5-pick/current-<task>.json --out /tmp/speed-h5/h5-pick/prompt-<task>-<n>.json

Write `current-<task>.json` first: one observation dict
{"image": "<latest image path>", "description": "<one line>",
"window": "<address>"}. The CLI output gives image_paths (at most 1
in the H5 arm), pruned_count, and kept_count. VIEW ONLY the images in
image_paths. NEVER re-open a pruned observation image. When you verify,
read only the latest observation image (tesseract OCR). If the CLI ever
lists more than 1 image, STOP, record BLOCKED-h5-cap in the summary,
and report. Log the CLI call first:
`echo "$(date '+%H:%M:%S.%3N') H5 <label> images=<n> pruned=<n>" >> /tmp/speed-h5/h5-pick/h5.log`

In the drop-text arm, add `--drop-text` to the CLI call. The prompt
then carries no text line for old turns; the H5 log line is the same.

## Baseline arm

Follow the v3 optimized discipline exactly (one observation, ground all
controls, batch actions in one act request, re-observe only to verify).
Do NOT apply any H5 rule. Do NOT write history files. Log DECIDE
lines exactly as below. This arm is the control.

## Tasks (all arms, same order, same end states)

Do the tasks in order P1, P2, P3, P4, then M1. Fresh broker session per
task. Same kitty terminal window reused across tasks in the same arm
(title `h5-pick-term`, see Setup).

- P1 C-03: "O dia con trong bao nhieu?" Run `df -h /` in the terminal and
  report the free space of `/` from what you OBSERVE on screen. End state:
  correct free-space answer, read from the terminal output via broker
  observe. Session owner `h5-pick-p1`, lease
  `~/.cache/agent-computer-use/leases/h5-pick-p1/p1.lease`.
- P2 E-04: "144 tren 150 la bao nhieu phan tram?" Run
  `python3 -c "print(144/150*100)"` and report the answer from the observed
  terminal output. End state: correct answer (96.0). Owner `h5-pick-p2`,
  lease dir `h5-pick-p2`.
- P3 B-01: "Tao trong /tmp thu muc hoc-ky-2, trong do co 3 thu muc con: dsa,
  ktvm, oop." Run `mkdir -p /tmp/hoc-ky-2/dsa /tmp/hoc-ky-2/ktvm /tmp/hoc-ky-2/oop`
  then `find /tmp/hoc-ky-2 -type d` and verify all 4 dirs from the observed
  output. End state: the 4 directories exist. Owner `h5-pick-p3`, lease dir
  `h5-pick-p3`.
- P4 A-01: "Tao file y-tuong.txt trong /tmp, ghi 3 dong." The 3 lines, exact
  Vietnamese with diacritics, must be byte-exact: line 1 "Ý tưởng 1: app
  nhắc uống nước.", line 2 "Ý tưởng 2: bot tóm tắt bài giảng.", line 3
  "Ý tưởng 3: web bán đồ secondhand." Write the file with one printf
  command, then `cat /tmp/y-tuong.txt` and verify the exact 3 lines from
  the observed output. End state: /tmp/y-tuong.txt with exactly those 3
  lines. Owner `h5-pick-p4`, lease dir `h5-pick-p4`.
- M1 M-01 (multi-step, about 10 observations; the task where a
  history-growth curve can actually exist): "Tao trong /tmp du an nho
  h5-m1." All file contents are ASCII only (no diacritics in typed text).
  Steps, each verified from the observed terminal output before moving on:
  (1) `mkdir -p /tmp/h5-m1/src /tmp/h5-m1/docs /tmp/h5-m1/tests`, then
  `find /tmp/h5-m1 -type d` and verify the 4 dirs.
  (2) Write /tmp/h5-m1/README.md with exactly 2 lines: "h5-m1 test project"
  and "step 2 done", then `cat` it and verify both lines.
  (3) Write /tmp/h5-m1/src/main.py with one line:
  `print("hello h5")`, then run `python3 /tmp/h5-m1/src/main.py` and verify
  the output is exactly `hello h5`.
  (4) Write /tmp/h5-m1/tests/test_main.py with one line:
  `# test placeholder`, then `cat` it and verify.
  (5) Append one line to the README: `echo "step 5 done" >> /tmp/h5-m1/README.md`,
  then `cat` the README and verify it now has exactly 3 lines.
  (6) `find /tmp/h5-m1 -type f | sort` and verify exactly these 3 files:
  README.md, src/main.py, tests/test_main.py.
  (7) `find /tmp/h5-m1 -type f | wc -l` and report the count (expect 3)
  from the observed output.
  End state: the /tmp/h5-m1 tree with exactly those 3 files and contents,
  program output `hello h5` observed, file count 3 reported. Owner
  `h5-pick-m1`, lease dir `h5-pick-m1`.

DIRT CHECK (before P3, P4, M1): if /tmp/hoc-ky-2, /tmp/y-tuong.txt, or
/tmp/h5-m1 already exists before its task starts, the run is dirty (a
previous arm left it). STOP, record BLOCKED-dirty in the summary, and
report. Do NOT delete them yourself; the coordinator cleans between arms.
Verify dirt only by OBSERVING the terminal (`ls` in the terminal through
the broker), never by reading files in your own shell.

## Optimized discipline (all arms)

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

- Wrapper: `python3 /tmp/speed-h5/h5-pick/timed.py --log /tmp/speed-h5/h5-pick/records.jsonl <command>`
  (timed.py is copied into the run dir in Setup; it is the fixed v3 wrapper
  that preserves the full broker result payload and chmods request files
  to mode 600).
- Start: `timed.py start --owner h5-pick-p1 --lease-file ~/.cache/agent-computer-use/leases/h5-pick-p1/p1.lease --label p1-start`
  (lease dir per task, mkdir -p first, chmod 700 the dir).
- Request: write the envelope JSON to a file first, e.g.
  `/tmp/speed-h5/h5-pick/p1-req1.json`, chmod 600 the file, then `timed.py req
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

- Before EVERY timed.py call, run: `echo "$(date '+%H:%M:%S.%3N') DECIDE <label>" >> /tmp/speed-h5/h5-pick/decisions.log`
- The label must match the timed.py --label for that call.
- Any sleep you insert must be logged first: `echo "$(date '+%H:%M:%S.%3N') SLEEP <seconds> <reason>" >> /tmp/speed-h5/h5-pick/sleeps.log`. Prefer no sleeps at all.

## Setup (plain shell, not broker input; do this once before each arm)

- Work in the H5 worktree for the prototype files only:
  `cd /home/james/computer-use-wayland-dropshots && git rev-parse --show-toplevel`
  must print /home/james/computer-use-wayland-dropshots. If it prints the
  live checkout, STOP and report. The tree may have uncommitted files from
  other workers: LEAVE THEM UNTOUCHED, never stash, never commit, never
  ask about them. NEVER stop before P1 for a git reason, and NEVER end
  your turn with a question: there is no one to answer it. If you are
  blocked, record BLOCKED with the cause in the summary and move to the
  next task.
- Run dir: `/tmp/speed-h5/h5-pick` (already created by the coordinator). timed.py and
  analyze.py are already copied there by the coordinator; verify their md5
  (timed.py 82176e2a4b84691a1584ed68ce82953f, analyze.py
  39170ad8dcfd90016806f87ab50ee9df, same as the triple A/B wrapper) and record
  them. If either file is missing, STOP and report BLOCKED-no-timedpy, do not
  hunt for another copy in a live worker's run dir.
  Records file: `/tmp/speed-h5/h5-pick/records.jsonl`. Decision log:
  `/tmp/speed-h5/h5-pick/decisions.log`. Sleep log: `/tmp/speed-h5/h5-pick/sleeps.log`.
  H5 log (H5 and drop-text arms only): `/tmp/speed-h5/h5-pick/h5.log`.
- Export the H5 flag for your own shell only on the H5 arm:
  `export CU_H5_DROP_OLD_SHOTS=1`. Drop-text arm: also
  `export CU_H5_DROP_TEXT=1`. Baseline arm: make sure both are unset
  (`unset CU_H5_DROP_OLD_SHOTS CU_H5_DROP_TEXT`). The flags never reach
  the relay and no relay restart is needed for any arm.
- Source the env file: `source /home/james/backups/cu-final-0.57.2-20261114-225131/env.sh`
- Hyprland signature: the live instance dir is the one under
  `/run/user/1000/hypr/` that contains hyprland.lock (there are stale
  dirs; refresh_gui fails because of them). Export
  HYPRLAND_INSTANCE_SIGNATURE to that dir name before any hyprctl call.
  Re-detect it, do not assume a value.
- Launch one kitty terminal: `setsid -f kitty --single-instance=no --title h5-pick-term`
  (with the GUI env exported). Then drive it only through the broker.
  Find its window address from the broker windows list (title h5-pick-term).
- Before every act, verify from your latest observation that the focused
  target is the h5-pick-term window. If focus ever lands on any other
  window, STOP driving, finish the session, and report what happened.

## Floor probe (scripted, zero model calls; run AFTER M1 in EACH arm, BEFORE teardown)

Same shape as the v3 floor probe, labels `floor-*`, owner `h5-pick-floor`,
lease `~/.cache/agent-computer-use/leases/h5-pick-floor/floor.lease`:
start, windows, observe screen, observe window (address of h5-pick-term
parsed from the floor-windows record), act with one harmless type action
`[{"type": "type", "text": "\n"}]`, observe window again, finish.
Sequence numbers 1..6 in that session. All envelope/action files chmod
600. Record the probe wall start/finish in the summary.

## Verification and reporting

- Verify each end state ONLY from a broker observe of the terminal output
  (OCR of the observation image). Never verify by reading the files or
  running commands in your own shell.
- Per task, record wall start (session start submit) and wall finish
  (verified end state) times in `/tmp/speed-h5/h5-pick/summary.md` as you go.
  Also record, per task: think total (from analyze.py), input tokens per
  call if the Codex usage record shows them (otherwise record the prompt
  image count per think call from h5.log / prompt JSONs as the token
  proxy), model calls (count of think calls), observations count, and
  SUCCESS/FAIL with the observed evidence (quote the OCR text). Also record MISCLICKS and MISREAD incidents per task (count 0 explicitly
when none, with what would have counted).
- If a task exceeds 30 minutes wall, finish its session, record it as
  BLOCKED with the cause, and move to the next task.
- Teardown after M1 and the floor probe, in EACH arm: close the test
  terminal gracefully with hyprctl dispatch `hl.dsp.window.close()` on
  its window (the object form; string dispatcher names are broken in
  Hyprland 0.57.2). Confirm no test window remains. Finish session M1
  cleanly (and the floor session, if not already finished).
- When all 5 tasks are done in an arm, write `/tmp/speed-h5/h5-pick/summary.md`
  FRESH with: repo HEAD (H5 worktree), per-task wall start/finish,
  total seconds, request counts by type (windows/observe/act/status),
  observations count, act requests, actions, SUCCESS/FAIL with the
  observed evidence (quote the OCR text you verified), any refusals or
  session deaths with cause, the floor-probe totals, and (H5 and
  drop-text arms only) H5 stats per task (images kept vs pruned from
  h5.log, prompt image counts), and any blocker. Also run:
  `python3 /tmp/speed-h5/h5-pick/analyze.py /tmp/speed-h5/h5-pick/records.jsonl /tmp/speed-h5/h5-pick/decisions.log /tmp/speed-h5/h5-pick/sleeps.log`
  and paste its output at the end of summary.md. Then stop. Do not start
  any other task.
- After BOTH arms (or all three, if the drop-text arm ran), write the
  before/after table (one table, all arms) into
  /tmp/speed-h5/h5-before-after.md:

| Step | Baseline think (s) | H5 think (s) | Delta |
| --- | --- | --- | --- |
| think before windows |  |  |  |
| think before first observe |  |  |  |
| think before act |  |  |  |
| think before verify observe |  |  |  |
| think total (clean-task mean) |  |  |  |
| wall (clean-task mean) |  |  |  |
| broker service (clean-task mean) |  |  |  |
| input tokens per call (mean) |  |  |  |
| model calls per task (mean) |  |  |  |
| SUCCESS (tasks / 5) |  |  |  |

Baseline anchor from the profile run (clean-task mean, P2-P4):
wall 36.4s, think 34.2s (94 percent), broker service 1.4s (4 percent);
think before act 14.9s, think before first observe 7.7s, think before
verify observe 6.7s, think before windows 4.9s. The question the table
answers: does H5 cut think time, and does it cut the LATER steps most
(the steps where history is longest)? Report per-step think by step
index too, so the growth curve is visible, and report M1 separately
from P1-P4 (M1 is the long-history task; P1-P4 are the short-history
control). Success bar (pre-committed, from harness-speed research H5):
wall lower with no drop in task success. Verdict is PROVISIONAL
(non-Astra): Astra 6 is out of credit.
