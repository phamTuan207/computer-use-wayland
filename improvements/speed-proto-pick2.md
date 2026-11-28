# Pick 2 prototype report: subgoal-only verification plus the reasoning dial (M2 plus M12)

- Owner: the repository owner. Date: 2026-11-18, 22:58 to 23:52 Asia/Ho_Chi_Minh.
- Repo: phamTuan207/computer-use-wayland, branch speed-swarm.
- Status: BUILT, TESTED, PUSHED. MEASUREMENT PAUSED by user order 23:50 (disk cleanup on the laptop). The pick2 arm never ran; the baseline arm produced one partial P1 only. Before/after tables below are therefore marked PENDING except for the gate probe and the partial baseline numbers, which are reported as-is.
- No em dash or en dash in this file.

## Gate-check verdict: per-call reasoning-effort override is POSSIBLE

Two granularities, both verified live on the laptop (Codex CLI 0.169.0, model gpt-6-luna):

- Per invocation: `codex exec -c model_reasoning_effort="low"` and `"max"` both work. Same multi-step arithmetic question at each effort: low answered in 6.0s with 0 reasoning tokens and 6 output tokens; max answered in 7.6s with 118 reasoning tokens and 126 output tokens. Same correct answer (210000). A trivial one-line prompt at either effort used 0 reasoning tokens, so the dial only shows on prompts that need reasoning, as expected.
- Per resumed turn: `codex exec resume <session> -c model_reasoning_effort="max"` works on a session started at low. The resumed turn answered a fresh question correctly (136000) with 116 reasoning tokens. Resume does NOT accept `-s`, `-C`, or `-o` (those flags error); it does accept `-c`, `-m`, `--json`, `--skip-git-repo-check`.
- Usage records carry token fields: `turn.completed` usage events report `input_tokens`, `cached_input_tokens`, `cache_write_input_tokens`, `output_tokens`, `reasoning_output_tokens`. Prompt caching is real on the Codex route: `cached_input_tokens` was 10752 on a repeat invocation and on the resumed turn, 0 on first turns. So the dial is real and measurable, and the M6 cache open check is answered YES as a side effect.
- Strict JSON schema: `codex exec --output-schema <file>` is accepted. The L2 schema file is `scripts/pick2-l2-schema.json`.
- Consequence: the dial is built as separate invocations (and resumed turns) with different `-c` flags, exactly the fallback the plan specified. No fake dial: level 2 runs as its own low-effort invocation, level 3 as max.

## What was built

All Pick 2 behavior sits behind the opt-in env flag `CU_PICK2_SUBGOAL_ONLY` (default OFF). With the flag unset the loop is byte-identical to baseline. Measurement enables exactly this flag and no other pick.

- `scripts/subgoal_policy.py` (new, 259 lines): the whole pick as pure policy.
  - Levels: L1 deterministic procedure, no model call; L2 bounded routine decision, Luna low plus strict JSON, max 512 output tokens, with a deterministic postcondition check behind it; L3 genuine ambiguity, recovery, or new procedure, Luna max. `classify_decision` routes; `codex_args_for_level` builds the per-invocation `-c` args (plus `--output-schema` for L2).
  - `validate_l2_decision`: fail closed. Exact keys action/target/confidence, confidence in [0, 1], and irreversible actions (delete, send, shutdown, push, submit, and others) are never level 2.
  - `judge_allowed`: per-step judge/reflect is allowed only at a subgoal boundary, never inside one. `validate_plan_has_no_mid_step_judge` fails a plan that hides a judge/reflect call inside a subgoal.
  - `mask_history`: only the last 2 screenshots stay in full; older observations become one compact text line each. Screenshot-only history does not help (OSWorld-Human); only text action history does.
  - `verify_subgoal`: deterministic postcondition checks only (file bytes and SHA, window/dialog class, AT-SPI validation). `should_escalate` sends any failed postcondition, ambiguity, or new procedure to level 3.
  - `QuarantineTracker`: a procedure whose checkpoint fails twice in a row is quarantined; the next run re-derives layout from a fresh full-frame observation. `DetectionLagTracker` counts actions run before a bad action is detected at subgoal verification.
- `scripts/pick2-l2-schema.json` (new): the strict JSON schema for level 2 decisions (action, target, confidence), written mode 600 by `write_l2_schema`.
- `scripts/tc02_controller.py` (hook only, 43 lines): reads the flag, validates the plan has no mid-step judge/reflect call, logs a `pick2-mode` event at preflight, counts subgoal verifications, exposes `pick2_subgoal_verification`, and records `pick2_mode` in the run summary. No behavior change when the flag is unset.
- `improvements/pick2-executor-brief.md` (new): the standalone measurement brief for the laptop executor. Same 4 held-out tasks as the profile run (P1 C-03, P2 E-04, P3 B-01, P4 A-01) plus one cold task P5 (largest entry in /tmp, no procedure exists, so the dial has something to act on), the Pick 2 rules, the exact level 2 sub-invocation form with schema and validation, supervisor logging, the scripted floor probe, and the focus-safety rule. The baseline arm uses the same brief with the Pick 2 section stripped.
- Safety invariants kept: ownership, lease, generation, cancellation, explicit finish, verification from exact sources plus a final observation image, brokered keyboard input only, pointer miss check and screen-changed refusal untouched, low effort never decides an irreversible action.

## Commits pushed (origin speed-swarm, HEAD 8f0e002, verified by ls-remote)

- 2c5d5a0 pick2: subgoal-only verification policy plus reasoning dial (M2 plus M12), `scripts/subgoal_policy.py` plus `scripts/pick2-l2-schema.json`.
- 1d781b6 pick2: tests for subgoal-only verification and the reasoning dial, `tests/test_subgoal_policy.py` (40 tests).
- 96fb092 pick2: controller hook for subgoal-only mode (opt-in, default OFF), `scripts/tc02_controller.py`.
- c1b7034 pick2: executor brief for the baseline vs pick2 measurement arms, `improvements/pick2-executor-brief.md`.
- 8f0e002 pick2: brief setup must never stop for a dirty tree or ask a question (fix found by live attempt 2, see Incidents).

Rebased cleanly onto origin twice (9183568, then ec6912a) before pushing. Never committed to main. No commits on the laptop; the laptop pulled speed-swarm to c1b7034 (the brief fix 8f0e002 was applied directly to the laptop brief copies, same text).

## Offline test suite: zero new failures

Worktree `~/workspace/pick2-wt` (isolated, branch pick2-wip at origin/speed-swarm) so the shared checkout churn could not contaminate the numbers:

- Baseline (origin/speed-swarm 9183568, no Pick 2 files): 1093 tests, 9 failures, 68 errors, 15 skipped. The 9 failures are the 5 allowed DoctorCliTests failures plus 2 TypedRefusalRecovery and 2 FullRestoreEnvelope failures, all pre-existing. The 68 errors are pre-existing environment errors (fast-observe, keyboard preflight, pointer safety, cursor file, wtype native; the VM has no desktop or wtype).
- After (same base plus Pick 2 files): 1131 tests, 9 failures, 68 errors on the confirmation run, identical failure and error lists, zero new. One first-run extra error (`test_menu_bar_ocr_requires_file_and_edit_on_fixture_images`, a tesseract subprocess timeout at 10s under full-suite load) was investigated: my diff touches no OCR path, and the test passes twice in isolation with the change applied, so it is a load flake, not a regression.
- New tests: 40 in `tests/test_subgoal_policy.py`, all passing (flag values, effort mapping, per-invocation args, schema file mode 600, L2 validation fail-closed cases, level classification, judge rule, history masking, subgoal checks, quarantine, detection lag).

## Live measurement: PAUSED, incomplete

Baseline reference (speed-swarm-profile.md, 2026-11-18 evening, 4 held-out tasks): clean-task mean wall 36.4s, mean model think 34.2s (94 percent), broker service 1.4s (4 percent). Think-before-act mean 14.9s (41 percent), think before first observe 7.7s, think before verify observe 6.7s, think before windows 4.9s. Scripted zero-thinking floor 2.116s.

My measurement runs (run dirs on the laptop, records kept):

- Baseline attempt 1, 23:17 to 23:27, dir `/tmp/speed-profile-20261118-pick2-base/`, summary written. P1 BLOCKED-focus-stop, 0 acts, no answer verified. The terminal window disappeared (`window no longer exists`), two `task_stopped` errors, session failed; after a fresh-lease restart the screen observe showed browser text, so the executor stopped under the focus rule. Span 479.055s, service total 1.449s, gap total 477.105s (99.6 percent think), 12 records excluding status polls. Think gaps: windows 6.7s, windows-retry 84.1s, observe-terminal 71.2s, windows-recovery 57.9s, fresh-screen-observe 17.2s, status 18.8s, restart windows 35.7s, restart observe-terminal 42.4s, restart observe-screen 54.7s, finish 44.3s. P2 to P5 and the floor probe never started. This attempt is NOT a baseline measurement; it is a partial P1 failure log.
- Baseline attempt 2, 23:45 to 23:47, dir `/tmp/speed-profile-20261118-pick2-base2/`, summary preserved as `summary-attempt2-gitstop.md`. The executor stopped before P1: `git pull --ff-only` was blocked by other workers' uncommitted files and it ended its turn with a question. Zero tasks, zero records. This found the brief bug fixed in commit 8f0e002 (pull with `git -c pull.rebase=false pull --ff-only`, leave dirty files untouched, never stop for git, never end with a question).
- Baseline attempt 3: waiter launched 23:47, killed by the 23:50 user pause before the broker freed. Never launched. No tasks.
- Pick 2 arm: never launched. Dir `/tmp/speed-profile-20261118-pick2-2/` is ready (brief patched, timed.py and analyze.py in place).

Before/after tables: PENDING. The columns the resume run must fill per task are wall time, think total, think-before-act, think-before-observe, think-before-verify, broker service total, request and image counts, refusals, misclicks, session deaths, plus reasoning tokens and cached tokens per call from the `--json` usage events, plus supervisor calls (L2 count, L3 escalations, L2 validation failures, detection lags) on the pick2 arm.

## Incidents (for the resume run)

- Shared-checkout stash sweep: another worker ran `git stash -u` on the shared VM checkout and swept my untracked files (plus Pick 1 and Pick 3 files) into their stash `stash@{0}` (WIP on 59a2b37), and a reset reverted my controller edit. Recovered byte-identical from the stash commits (`git show 65011c7:` for new files, `git show 3e6c745:` for the controller, diff verified to be exactly my 43 lines). The stash was left untouched for its owner. All further work ran in the isolated worktree `~/workspace/pick2-wt` (branch pick2-wip).
- Baseline brief contamination: attempt 1's executor followed the Pick 2 rules section even though it was the baseline arm (it ran 2 L2 calls and exported the flag). The section is now stripped from the baseline brief copy, with the remaining L2/L3 mentions verified to be negations or `(pick2 arm only)` labels only.
- Focus recovery addendum: after attempt 1 stopped on a screen observe showing browser text, both briefs now say to re-observe the terminal window itself first and stop only if the terminal itself is gone or shows non-terminal content.
- Broker contention all evening (single-owner): speed-smoke, speed-smoke2, pick3d, pick3x, pick3-ab, and speed-base (Pick 1 executor, PID 613054, session speed-base-p1) all ran measurements. My waiter polled for `finished stopped` and launched on the free window; a race at 23:45 let the Pick 1 executor take the broker first. At pause time the broker was owned by speed-base-p1 (running).
- Laptop pull blocked by a dirty tree twice (2 files, then 4, other workers' uncommitted work). The working pull form is `git -c pull.rebase=false pull --ff-only origin speed-swarm`; never stash another worker's files.
- Origin moved three times during the task (221f061, 9183568, 2ef80dd, ec6912a); each push was preceded by fetch plus rebase.

## Cleanup verification at pause (23:51, hyprctl clients)

- My waiter killed (`pkill -f pick2-wait-launch-base2.sh`), no Pick 2 codex processes remain, no broker session of mine is live (broker owner at 23:51 was speed-base-p1, Pick 1's executor, left alone for its owner and the parent to pause).
- Desktop: only his own windows (Jarvis herdrdrop, foot terminal, kitty ncdu running his disk cleanup, Zen Muse chat). My pick2-term terminal was closed at 23:32 and verified gone. Zero Pick 2 test windows. Zen tabs, Zalo, Teams, Jarvis, music untouched.
- Note: the old v3 `speed-profile-term` kitty seen at 23:32 was gone by 23:51 (closed by someone else, not by me). The VS Code tc09 window seen at 23:32 was also gone by 23:51.

## Resume plan (for the parent)

1. Wait for the resume order. Do not launch anything before it.
2. On the laptop: `rm -rf /tmp/hoc-ky-2 /tmp/y-tuong.txt /tmp/lon-nhat.txt` (already absent at pause), check the broker is `finished stopped`, then relaunch the waiter for baseline attempt 3: `/tmp/pick2-wait-launch-base2.sh` (already on the laptop, patched brief in `/tmp/speed-profile-20261118-pick2-base2/`). It launches the executor when the broker frees.
3. When the baseline summary lands, verify desktop clean (close pick2-term, hyprctl clients check), clean /tmp artifacts, then launch the pick2 arm the same way from `/tmp/speed-profile-20261118-pick2-2/` (waiter script needs the same one-line dir change; the brief there is already patched and the flag is set by the brief).
4. Fill the before/after tables in this report from both summaries plus `analyze.py` output and the `--json` usage events (reasoning and cached tokens per call), then give the ship verdict per the plan decision rule (lower wall time with no rise in refusals, misclicks, or session deaths).
5. Known risk: the desktop is shared with other workers measuring at the same time, so focus steals and broker races can recur; the focus-recovery addendum and the waiter mitigate both.
