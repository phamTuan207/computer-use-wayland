# Worker F2 - silence weakness fix log

Worker: F2 (Muse fixer). Task: fix the top-priority weakness FIRST and optimally.
Owner order 22:18 on 2026-11-21: fix the big errors at full team capacity.
Owner correction 22:21: narration before each step is NOT needed. Requirements, in
priority order: (1) FAST, (2) CONTINUOUS operations with no idle gaps, (3) the
OVERLAY MUST BE VISIBLE, because the overlay itself is what reports to the user
what is happening.
Owner method 22:22 (applies to F1/F2/F3): read the source code and crawl to find
the root cause, the origin, the reason it fails, and only then fix it. Record the
exact root cause with file/line and source evidence, then fix at that root.
Do not fix by guessing.
Owner test rule 22:23 (standing): future tests must be COMBINED (one test uses
DOM + CLI + mouse + keyboard at the same time), set by an independent agent
(the test-taker must not know the test in advance). Applies to every future
test run (Y13/Y14 live, A1, final test, any new test).
Owner status 22:27: the owner went to sleep. Work overnight, do not disturb.

## 1. Tonight, measured (2026-11-21, Asia/Ho_Chi_Minh)

- 22:11:30: owner orders a tab click via computer-use (as a test, "Do dac di").
- 22:16:07: owner: waited 3+ minutes, nothing seen on his computer.
- 22:16:13: owner: computer-use not seen turning on.
- 22:16:18: owner: the weakness shows immediately.
- 22:17: direct Pointer click SUCCEEDS in 0.31 s, cursor 2598,1174, no miss,
  Welcome tab selected. BUT NO overlay/pill appeared, because the direct
  path bypasses the session.
- Owner measurement (22:21): order (22:11:30) to first click (22:17) was
  nearly 5 minutes, while the click itself was only 0.31 s. The rest was
  silent diagnosis.

Timeline evidence (file mtimes on the laptop, +07):

- /tmp/zen_tab_cleanup/out5.log 22:12:09 (cleanup2 retry 3, Marionette fail)
- observation a730a9b92410.json 22:13:53 (fresh observe, 28.6 ms capture)
- observation b890e3c807c3.json 22:15:00 (observe inside the session attempt)
- session attempt ~22:15:00, guardian failed in 0.46 s
- direct Pointer click 22:17, 0.31 s
- /tmp/zen_tab_cleanup/out6.log 22:19:52 (cleanup2 retry 4, still failing)

Breakdown of the ~5.5 min: ~40 s Marionette retry, ~2 min cu.py/session
research + observe + view, ~1 min session attempt + diagnostics, ~1.5 min
guardian/desktop_act source reads, ~0.5 min Pointer read + click.
The click itself was 0.31 s. The diagnosis phases were ~4.5 min of the
5.5 min, all silent, no visible action.

## 2. Root causes (proven, file/line + live evidence)

### R1. No structural fast path. The agent's default loop is research-first.
The code offers no single command that does overlay-on + move first and
diagnoses after. The agent must remember to be fast, and tonight it did not.
Fix (this worker): make the fast path the DEFAULT command (act-now), so
speed is structural, not a decision. Lauren Tan rule: a repeated mistake
becomes a deterministic rule, never a reminder.

### R2. Session guardian startup fails fast, with a swallowed error. (F1 owns the fix.)
Chain, proven live 22:25-22:33:

- `scripts/cursor_session.py`, guardian(): after `cursor_theme.snapshot(env)`
  it calls `cursor_theme.check_guard(env)`, before writing SNAPSHOT and
  before printing 'ready'. Any exception there kills the guardian.
- `scripts/cursor_theme.py:107-108`, check_guard():
  `guard_reply(command(env,'hyprctl','cu-cursor','status'),active=False,token='')`.
- `scripts/cursor_theme.py:99`, guard_reply(): `reply = json.loads(raw)`.
- `scripts/cursor_theme.py:52-53`, command(): subprocess.check_output,
  stderr merged to stdout, timeout 5 s.
- Live 22:33: `hyprctl cu-cursor status` returns the string
  `unknown request` with exit code 0 (the `cu-cursor` dispatcher is not
  registered in the live Hyprland). `json.loads("unknown request")` raises
  `json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)`.
  This is byte-identical to the stderr string seen in tonight's failed
  session attempt.
- `scripts/cursor_session.py:230`, supervise(): the guardian's stdout EOF
  (no 'ready') raises `RuntimeError('session guardian startup failed')`.
- `scripts/cu.py`, main(): the session branch prints
  `{"ok": false, "error": "session guardian startup failed"}` and exits 1.

Why the dispatcher is unknown (live evidence 22:33):

- `hyprctl plugin list` shows ONLY hyprbars (version 1.0). The cursor-guard
  plugin is not loaded.
- `hyprland.conf` has no `cu-cursor` or `cursor-guard` reference (grep, no hits).
- The guard socket dir `/run/user/1000/agent-computer-use/` does not exist.
  (`cursor_theme.py` Guard requires it, 0700, with `cursor-guard.sock`.)
- The guard source exists in the install
  (`native/cursor-guard.cpp`, `scripts/activate-cursor-guard.py`,
  `scripts/build-cursor-guard.py`) but was never loaded into the live
  compositor.
- Handoff to F1: load/register the cursor-guard in the live Hyprland (or
  make check_guard degrade instead of killing the guardian). F2 does NOT
  fix the guard itself; F2's watchdog detects the failure and falls back.

Probe results that cleared the other guardian steps (22:25, installed copy
`/home/james/.local/share/agent-computer-use/scripts/`):

- owner_lock OK.
- cursor_theme.snapshot OK (keys gtk/hypr/agent theme+size).
- cursor_theme.check_guard FAIL (the JSONDecodeError above).
- indicator.listen OK with a valid 32-hex token. (An earlier probe FAIL was
  my own artifact: I passed the invalid token 'diagtoken123'; endpoint()
  rightly rejects it. Not a bug.)
- indicator.Native OK (spawned, poll None, closed cleanly, no pill shown
  on construction; a benign mesa Vulkan warning only).

### R3. The overlay is not tied to any action. (This worker's core fix.)
- `scripts/cu.py:2595`, act(): `require_session()` demands a live session
  (CU_SESSION_TOKEN). No session, no act.
- The pill exists only inside a live session: the guardian creates
  `indicator.Native` and the session driver shows it. No session, no pill.
- The direct Pointer path (what tonight's 22:17 click used) never touches
  the overlay at all. Result: any session failure means an invisible run.
  Tonight's click had no overlay for exactly this reason.
- `scripts/overlay.py` (central overlay control, in the installed copy):
  `acquire --agent <name> --method <method>` / `release` / `status` /
  `stop` / `daemon`. Reference-counted: the pill hides only when ALL
  holders release. Session-aware: if a live session exists it forwards
  show/label to the session indicator instead of spawning a second pill;
  if the session dies while holders remain, the daemon spawns its own
  indicator and takes over. State in
  `~/.cache/agent-computer-use/overlay/` (0700). On the laptop 22:25:
  holders.json was `{}` (no stale holders), daemon.log last entry 15:36:59
  (clean stop), no overlay daemon running, no pill.
- Fix: overlay acquire is a PRECONDITION of any pointer action, on BOTH
  paths, enforced in code. If the overlay cannot be shown, the action is
  REFUSED with a clear error, never executed invisibly.

### R4. The act chain is three serial failure points before any visible action.
`observe` (max age 120 s, OBSERVATION_MAX_AGE in cu.py) -> `session`
(guardian, up to 15 s wait in supervise) -> `act` (requires session +
fresh observation, session_policy.require_observation). Each step must
succeed before anything moves. There is no fast path in the code.
Fix: act-now acquires the overlay and moves the pointer FIRST (overlay is
the visible action; the move follows within the same second), then does
session/observe for the rest. Diagnosis happens after or in parallel,
never as a long silent phase first.

### R5. Marionette slot still wedged after the Welcome click. (F3 owns it.)
`/tmp/zen_tab_cleanup/out6.log` 22:19:52 still contains
`browserElement is null` (grep count 2). The 22:17 click did NOT fix the
slot. F3's scope expanded 22:25: full Zen restore (Zen cannot click/open
any web, sidebar collapsed, new-tab page open, PID 27958 alive). F2's
rehearsal is gated on F3's Zen restore.

### R6. VM integrity incident: stdlib `re/__init__.py` deleted 22:25:39 +07.
- Symptom: all laptop SSH failed 22:26-22:30 (tailscale-proxy.py imports
  urllib.parse, which imports re; `AttributeError: module 're' has no
  attribute 'compile'`).
- Diagnosis: `/usr/lib/python3.12/re/` is a package dir (CPython 3.12);
  its `__init__.py` was missing, so `import re` resolved to an empty
  namespace package. Dir mtime 2026-11-21 15:25:39 UTC = 22:25:39 +07.
  `find /usr/lib/python3.12 -newermt '2026-11-21 15:20:00'` showed ONLY
  the `re` dir changed: damage limited to that one file.
  `__pycache__/__init__.cpython-312.pyc` (17,938 B) survived but cannot
  load without its source (header check fails).
- Fix applied 22:30: downloaded CPython v3.12.3 `Lib/re/__init__.py`
  (16,315 B) from raw.githubusercontent.com, verified
  `re.compile('x').search('xyz')` works and `urllib.parse` imports.
  SSH works again.
- Cause UNKNOWN. No F2 command touches /usr/lib. Needs investigation by
  the parent (which agent/cron deleted it at 22:25:39). Recorded here so
  it is not lost. The owner noted at 22:25 that the workspace "has many
  strange errors" (doi workspace nhieu loi ki); this may be one of them.

## 3. Crawl findings (how other harnesses guarantee fast first action + always-on overlay)

Sources (web search 22:22-22:25):

- dsh-computer-use-win (github.com/datuloar/dsh-computer-use-win):
  overlay-first as a TOOL-ENFORCED gate. "Input is refused while the
  indicator is down. move, click, drag, wheel, type, key, keys, clipboard
  and run answer with a refusal until `dsh-cu overlay` has put the frame
  on screen. That gate lives in the tool, not in the prompt." Loop:
  `dsh-cu overlay` (human warned 5 s, ESC cancels) BEFORE the first
  input, then actions, then `overlay --stop`. ESC stops everything;
  injected ESC is ignored, so an agent cannot switch off its own
  indicator. This is the direct precedent for R3's fix.
- @agent-sh/computer-use-linux (pi.dev, Rust MCP server + CLI for Linux):
  server-driven indicator with per-action feedback (per-agent cursor
  glide, click ripple, keycaps/typing banner, screen-edge glow, status
  pill). "Visible to humans, invisible to screenshots": the overlay
  hides automatically under a shared capture lock before any screenshot
  is read. Pointer actions wait 350 ms so the cursor lands before the
  real input. `doctor` returns a readiness report with explicit blockers
  and a recommended next step. Precedent for: overlay driven by the
  tool server (not the session wrapper), and a readiness report that
  names blockers instead of failing silently.
- Anthropic computer use (reference implementation, 2024-10): the loop
  is screenshot -> reason -> act, every step a full vision-model
  inference call; latency and token budget are the dominant constraints;
  the model cannot batch multiple actions atomically. Our repo already
  beats this with batched actions (Pick 1, code-exec). Lesson: the first
  action must not wait for the full loop; batching + fast paths are the
  right direction, and they must be the DEFAULT path, not an option.
- Codex parity research (claude-computer-use docs, 2026-09-02): guarded
  input (if the user touched the window, the next action fails and forces
  a re-read); per-window indices; revision counters so waits can be
  skipped when nothing changed. Precedent for fail-closed guards.

Design conclusions for the fix:

- D1. Overlay acquire is a precondition of any pointer action, enforced
  in the tool (dsh precedent). No overlay, no action, loud refusal.
- D2. Overlay + first move happen BEFORE session/observe diagnosis
  (Anthropic loop lesson: never let the first action wait for the loop).
- D3. Session start has a hard deadline; on failure, fall back to the
  direct Pointer path WITH the overlay already on, and log the bypass
  with the guardian's real error (computer-use-linux doctor precedent:
  name the blocker).
- D4. Measure order-to-first-visible-action on every live run; target
  under 30 s; a run with no visible action for more than 60 s while the
  user watches is a failure.

## 4. Fix design (to implement)

- `scripts/first_action.py` (new): the fast path. One call does, in order:
  (1) acquire the overlay (overlay.py, agent=f2, method=act-now) and
  record the acquire time; (2) attempt the session with a hard deadline
  (default 20 s); if the session reaches ready, run the actions through
  it; (3) if the session fails or times out, fall back to the direct
  Pointer path for the same actions, with the overlay already on, and
  log the bypass (guardian error, deadline, path taken); (4) verify the
  pointer position after each click (within 3 px, same rule as
  desktop_act); (5) release the overlay; (6) return a JSON envelope with
  path taken, timings (order -> overlay-on, order -> first move,
  order -> first click), pill_shown flag, and any bypass reason.
  Never silent, never invisible: if the overlay cannot be acquired, the
  run refuses loudly instead of acting invisibly.
- `scripts/cu.py`: new `act-now` subcommand wiring first_action.py
  (observation + actions file, same shapes as `act`).
- `tests/test_first_action.py` (new, VM): unit tests with fakes for the
  session attempt (ready / fast-fail / timeout), the overlay gate
  (acquire fail refuses), the fallback path, and the timing envelope.
- `improvements/first-visible-action-rule-20261121.md` (new): the rule
  doc. FAST + CONTINUOUS + OVERLAY VISIBLE. First visible action under
  30 s. No idle gap over 60 s while the user watches. Overlay on from
  the first visible action until the task ends, on both paths.
- Error file update: new G28 (silence weakness, root causes R1-R4, fix)
  + H2 fix line updated from CHUA XAC DINH to the act-now path.
- Live rehearsal: COMBINED test (DOM + CLI + mouse + keyboard in one
  task), set by an independent agent (ZT-A scenarios, or a fresh setter
  if none is ready), run via the new act-now path after F3 restores Zen.
  Measure order-to-first-visible-action, verify overlay visible in the
  after-capture, verify the click landed, verify continuity (no gap
  over 60 s). Record the numbers here.
- Council (3 voices) + redteam over the diff + rehearsal evidence.
- Commit only F2's files by exact path on todolist-push, verify via
  ls-remote, report fix + measured numbers to the parent.

## 5. Implementation log

### 22:35-22:39 (VM, no SSH needed)
- Wrote `scripts/first_action.py` (new, ~300 lines): overlay acquire
  FIRST (gate: refuse loudly when the pill cannot be shown), fresh
  observation when none is given or the given one is stale (over 120 s),
  session attempt with a hard 20 s deadline (process-group kill on
  timeout), fallback to the same `desktop_act` the session path uses
  only on a session-START failure (guardian error, cursor-guard error,
  or a timeout with no live session), never replay an act failure,
  after-capture, overlay release, JSON envelope + JSONL timing log
  (`STATE/first-action-YYYYMMDD.jsonl`).
- Wired `act-now` into `scripts/cu.py` (subparser + dispatch, 2
  insertions only; `git diff` clean).
- Wrote `tests/test_first_action.py` (21 tests, VM-only, fakes for cu
  and overlay). First run 20/21: one real bug found (the refusal
  envelope was printed twice, once in the except branch and once in the
  finally); fixed by printing only in the finally. Second run 21/21 OK.
  `cu.py` + `first_action.py` parse OK, `act-now --help` works.
- Wrote the rule doc `improvements/first-visible-action-rule-20261121.md`.
- Crawl extra (latency benchmarks, for the rule doc target): mean
  observation-to-action gap 6.51 s on real OSWorld workloads (arXiv
  2604.18860); cua-speedrun: Fast I/O (2-28 ms screenshots) made the
  agent SLOWER (99.02 s vs 89.54 s) because screenshots arrived before
  the redraw, so the fix keeps desktop_act's settle/verify steps;
  naive loop 4-8 s/step, production target 600 ms (datarekha).

### 22:40-22:42 (deployment, laptop)
- Installed `cu.py` was BEHIND the VM HEAD (2 diffs: an em dash in a
  comment, fixed in HEAD; a `run` vs `cli_run_parser` variable rename).
  No local-only changes in the installed copy, so overwriting it with
  the VM working tree (HEAD + act-now wiring) is a safe forward sync.
- Deployed by exact-path scp: `first_action.py` (new) + `cu.py`
  (HEAD + act-now) to
  `/home/james/.local/share/agent-computer-use/scripts/`. Verified
  md5s after copy: first_action.py 68d8e84d..., cu.py 2d208d36...
  (matches the VM working tree). `computer-use act-now --help` works
  on the laptop; `import first_action` OK. No `computer-use session`
  or `act` process was running during the copy.
- Zen was restarted by F3 at 22:36 (new PID 426338, flags
  --remote-debugging-port=9222 --marionette); `curl 127.0.0.1:9222/`
  returns 200. Old PID 27958 is gone. Session-restore state unknown;
  the ZT-00 gate (step 3, Marionette session must create) decides it.
- F1's log read: F1 independently proved the same guardian root cause
  (Layer 1 check_guard JSONDecodeError, Layer 2 plugins not loaded)
  and went deeper (Layer 3 login loader failed at manifest_validation,
  Layer 4 laptop-repo optics/manifest drift vs the installed tree).
  F1's fix plan: repair the drift (laptop-local), live restoration
  AFTER F3, code fixes in cursor_theme.py (validate reply) and
  cursor_session.py (pipe guardian stderr), then proof. F2 does not
  duplicate F1: F2's watchdog detects the failure and falls back.
  F1 also verified the VM `re` restore (md5 14c5eb10... matches dpkg).
- Owner target 22:40: the whole team pushes to 240 commits before
  24:00 (189 now, ~51 more). Commit small and often, quality first,
  council + redteam complete. F2 commits below follow that order.

### Commits (todolist-push, each verified via ls-remote)
- (to fill as they land)

### Rehearsal (pending)
- ZT-00 health gate via act-now, then ZT-01, after the gate passes.
