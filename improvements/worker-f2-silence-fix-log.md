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
- 22:16:07: owner: waited 3+ minutes, nothing seen on the user's computer.
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
`~/.local/share/agent-computer-use/scripts/`):

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
- Cause KNOWN (solved 22:57, per MEMORY.md + VMFIX c16dd4e): a
  self-deleting shim from Redteam Y13r2 (A6e) deleted the file by
  accident (globals().update overwrote __file__ before os.remove),
  NOT a foreign process. VMFIX restored it durably. The earlier
  "cause UNKNOWN" note is superseded; the record above is what was
  known at 22:30. The owner noted at 22:25 that the workspace "has many
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
  `~/.local/share/agent-computer-use/scripts/`. Verified
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
- a576e69 F2: first_action.py (overlay-first fast path, session watchdog
  + Pointer fallback)
- afed06e F2: tests for first_action (21 tests, VM-only)
- 8d1f775 F2: wire act-now subcommand into cu.py
- 8979b30 F2: first-visible-action rule doc
- 2495382 F2: silence-fix log (root causes R1-R6 + crawl + design +
  deploy). Remote HEAD verified 2495382 via ls-remote 22:44.
- Push race note: the first push was rejected (remote had moved to
  08014a07, Y13r2 council 1); a later fetch showed a576e69 already in
  the remote history (branch -r --contains) and the push then went
  019bdf3..2495382. The remote moves fast (Y13r2, F1, PRIO all
  committing); always fetch before push.

### Event log (owner rule 22:47: log EVERY event with time, nothing
omitted; append as it happens, never batch at the end)
- T0 = 22:40:00 +07 (owner target steer, start of this work block).
  T_order (rehearsal) = 22:45:15.749 +07 (fresh observe start).
  Elapsed below is since T0 unless marked T_order.
- 22:40:00 (T+0s) owner target: team to 240 commits before 24:00
  (189 now, ~51 more). Commit small and often, quality first,
  council + redteam complete.
- 22:41-22:42 (T+60-120s) appended deployment note to this log
  (implementation section 5).
- 22:42 (T+120s) git fetch + ff: HEAD d5239ab, already up to date.
- 22:43 (T+180s) commit a576e69 (scripts/first_action.py) created;
  push REJECTED: remote at 08014a07 (Y13r2 council 1), expected
  d5239ab. Rebase failed: unstaged changes in the shared tree.
- 22:44 (T+240s) diagnostics: remote HEAD 5033c9d (F1); a576e69
  confirmed in remote history (git branch -r --contains).
- 22:44 (T+240s) committed 4 more: afed06e (tests), 8d1f775 (cu.py),
  8979b30 (rule doc), 2495382 (this log).
- 22:44 (T+240s) push OK: 019bdf3..2495382, ls-remote verified
  remote HEAD 2495382. All 5 F2 commits on todolist-push.
- 22:44 (T+240s) ZT-00 gate step 0: zen_dom.py list (via
  /tmp/zen_tab_cleanup/zen_dom.py) returned 67 tabs, saved to
  /tmp/zt00-baseline.json (8974 B). Outcome: PASS. Note: the restart
  restored ALL 67 tabs, undoing the 22:03 cleanup (39 fixture tabs
  back). Example Domain tab at index 10 (F3 likely opened it during
  verification). ZT doc path ~/computer-use-wayland/scripts/
  zen_dom.py does NOT exist; the file is at
  ~/workspace/computer-use-wayland/scripts/zen_dom.py.
- 22:44 (T+240s) ZT-00 gate step 1: ps zen-bin PID 426338 alive
  (etime 07:00). PASS.
- 22:44 (T+240s) ZT-00 gate step 2: curl 127.0.0.1:9222/ -> 200. PASS.
- 22:44 (T+240s) ZT-00 gate step 3: Marionette session created without
  error (the list worked, no browserElement null). PASS. Gate 0-3 all
  PASS; the slot is healthy after F3's restart.
- 22:44:54 (T+294s) eval document.title -> null (active tab is
  blank/unloaded). No concurrent driver processes (no zen_dom,
  run_live, run_agy, computer-use session, act-now). Coast clear.
- 22:45:15.749 (T+315s, T_order+0s) fresh observe: id 20a5e52da440,
  capture 39 ms, 1920x1200, image 568,754 B, monitor eDP-2
  [2464,902,1920,1200], scale 1.0. Image
  ~/.cache/agent-computer-use/20a5e52da440.jpg.
- 22:45 (T+300s) owner correction: open Omarchy menu and switch
  workspaces by COMMAND, never click the bar (hyprctl dispatch in
  hl.dsp form for workspace; find the exact launcher command from the
  Hyprland/Omarchy config for the menu). Fastest-path-first: CLI
  first, mouse last. Applies to the rehearsal: if a workspace switch
  or menu open is needed, use the command, not a bar click. ZT-00
  does not need either (Zen is on the current workspace).
- 22:47 (T+420s) owner rule: log EVERY event with time, nothing
  omitted; append as it happens. This section is that log.
- 22:48 (T+480s) viewed observe 20a5e52da440 (22:45:15): the screen
  shows TWO Muse chat windows tiled side by side (clone1 left,
  clone2 right), NOT Zen. Zen is not visible on the current
  workspace; it is on another workspace or behind. No Omarchy menu
  open in this shot. Owner's 22:44 missed-click note (MEMORY.md):
  a click missed workspace 1 and opened the Omarchy menu ~22:44;
  F2 made NO pointer click at 22:44 (only DOM list + ps + curl +
  eval, all CLI/connector), so the click was not F2's. F3's
  verification is the likely source (unproven; F3 has no log yet).
- 22:48 (T+480s) owner updates (MEMORY.md): (a) 22:45 menu/workspace
  by COMMAND, CLI first (already recorded above); (b) 22:46-22:47
  OPTIMAL METHOD: convene ALL agents, each spawns many crawlers +
  council + redteam, find ONE optimal fix method for the whole error
  pile; log time + events continuously; Worker OPT (coordinator)
  spawned; (c) 22:48 LAUREN TAN, NO CUTTING STEPS: follow the Lauren
  Tan structure tightly, do not cut steps or the code will be garbage;
  owner asleep, work overnight, do not disturb, report results in
  the morning. F2 continues its brief as written (rehearsal ->
  council/redteam -> error file -> commit -> report); that IS the
  Lauren Tan structure (evidence contract, council + redteam, small
  commits, generator never runs its own tests, kill rules, continuous
  logging). No shortcuts.
- 22:48 (T+480s) next: find Zen's workspace via hyprctl clients,
  switch by COMMAND (hl.dsp.workspace), never a bar click, then
  re-observe before any pointer action.
- 22:49 (T+540s) hyprctl clients (4 clients): Zen 0x557052b62dd0 on
  workspace 1, at [2509,914], size [1863,1176], not floating, PID
  426338. Two Muse windows (chrome-... and brave-... classes, both
  titled 'Muse') on workspace 2, at [2533,914] and [3448,914], each
  901x1176 (tiled halves). A herdrdrop special window also present.
  Active workspace NOW is 1 (Zen's). So the 22:45:15 observe showed
  workspace 2 (Muse), and the workspace switched to 1 between
  22:45:15 and 22:49 (switcher unknown: F3's verification or the
  owner; NOT F2, F2 issued no workspace command). No workspace
  switch needed now; Zen is on the active workspace.
- 22:50:27.772 (T+627s) fresh observe 7650ae3be6e7: capture 24 ms,
  1920x1200, image 569,185 B, monitor eDP-2 [2464,902,1920,1200],
  scale 1.0. This is the observation for the act-now batch.
- 22:50:45 (T+645s) viewed observe 7650ae3be6e7: it STILL shows the
  two Muse chat windows (clone1 left, clone2 right), NOT Zen. So
  eDP-2 is still on workspace 2 despite activeworkspace saying 1.
- 22:51:32.440 (T+692s) workspace switch attempt (CLI, owner 22:45
  rule): `hyprctl dispatch "hl.dsp.workspace(1)"` FAILED: error
  "[string ...]:1: attempt to call a table value (field
  'workspace')", rc=7, activeWs stayed 2. So hl.dsp.workspace is a
  TABLE, not a function; the workspace sub-function name is unknown
  (candidates: goto/switch/change). SUPERSEDED (J23, 22:58): the
  methods are swap_monitors, rename, move, change_id, toggle_special,
  no goto or switch; hl.dispatch("workspace", "1") also fails.
  Workspace switching by command is still unsolved except via the
  focus side effect. UPDATE 23:19 (AGENTS.md): `hl.dsp.focus({
  workspace = 2 })` switches workspaces in ~1 s (verified both
  directions); `hl.dsp.workspace.goto` FAILS (goto is a Lua reserved
  word, rc 7). Workspace switching by command is SOLVED via the
  focus form. Did NOT fall back to the plain
  string form `hyprctl dispatch workspace 1` (broken in Hyprland
  0.57.2 Lua per AGENTS.md).
- 22:51:56.149 (T+716s) focus Zen by address instead (repo pattern,
  cu.py:541): `hyprctl dispatch "hl.dsp.focus({ window =
  \"address:0x557052b62dd0\" })"` -> "ok", rc=0. eDP-2 activeWs is
  now 1 (Zen's workspace). Focusing the window switches to its
  workspace; this is the working CLI-first route. The exact
  hl.dsp.workspace sub-function is still unknown (follow-up: find it
  in the Hyprland Lua docs, do not guess).
- 22:53:39 (T+819s) F3 cleanup check: NO F3 process running (no
  cleanup2.py, zen_dom.py, run_live, computer-use session). Only
  kernel i915_cleanup workers. /tmp/zen_tab_cleanup/ files all from
  22:03-22:19 (my earlier cleanup). Coast clear; F3 has not started
  its re-run yet. Proceeding with the rehearsal now (fast, one
  batch), and will re-baseline before the close check.
- 22:53:57.380 (T+837s) act-now run 1 (ZT-00 step 4): batch [Ctrl+N,
  click address bar (165,72), type "example.com", Enter],
  observation ce2bf0b9a594 (given, fresh). RESULT: REFUSED, ok false,
  completed 0, total 638 ms. Overlay acquire FAST:
  order_to_overlay_ms 356 ms, daemon spawned PID 446144 (overlay
  mechanism works). Session error (clear, F1's improved message):
  "session guardian startup failed: cursor guard reply is not valid
  JSON (got: unknown request); the cursor backend may not be loaded,
  load it with scripts/activate-glass.py and scripts/activate-cursor-guard.py
  or re-run the fresh-login loader scripts/visuals.py". Fallback
  attempted, but desktop_act REFUSED the batch: "screen observations
  support pointer actions only; use a window or accessibility target
  for typing". NEW FINDING: a screen observation cannot do type/key
  actions; typing needs a window or accessibility target. The batch
  as designed (mouse + keyboard in one desktop batch) cannot run on
  a screen observation. Investigating the window-observe option.

### Rehearsal (in progress)
- ZT-00 health gate via act-now. Gate 0-3 PASS (above). Step 4 next:
  fresh observe viewed, then ONE act-now batch [Ctrl+N, click address
  bar, type example.com, Enter]. Deviation from ZT-00 as written
  (recorded): ZT-00 navigates the active tab, but the count/identity
  cleanup rule (title set AND count must match after close) means the
  closed tab must be run-opened, so a new tab is opened first. The
  active tab is a blank baseline tab; navigating and closing it would
  drop the count 67 -> 66.

- 22:55:31.641 (T+931s) act-now run 2 (ZT-00 step 4, window obs
  cdd81db8e871): batch [Ctrl+N, click urlbar (120,60), type
  "example.com", Enter]. RESULT: OK, path fallback, completed 4/4,
  total 1477 ms. order_to_overlay_ms 333 ms, order_to_action_start_ms
  333 ms. Session guardian failed as expected (same clear error,
  logged as fallback_reason). After-capture 594806e130f1. Pill
  "Muse via act-now" VISIBLE in the after-capture (top center).
  THE CORE PROOF: overlay in 333 ms, first action in 333 ms, whole
  batch in 1.48 s, vs tonight's ~5.5 min of silent diagnosis.
- 22:56:33 (T+993s) verification: hyprctl cursorpos = (2629, 974)
  GLOBAL, which is exactly window (120,60) = screen (165,72). The
  CLICK LANDED exactly on target (0 px error). BUT the navigation
  did NOT happen: the active tab was still "New Tab" (after-capture
  + obs4 22:57:10 both show the blank new-tab wallpaper, urlbar
  shows "Search..." empty). The click landed but did not focus the
  urlbar for typing (or the typing went elsewhere). DOM check
  BLOCKED: zen_dom.py list FAILED, Marionette slot broken AGAIN
  (see below). DOM evals right after run 2 returned null for
  document.title and location.href (the eval ran but the document
  was null/blank, or the slot was already failing).
- 22:56:33 (T+993s) MARIONETTE SLOT BROKE AGAIN (F3 owns it):
  zen_dom.py list raises ZenDomError "could not create a remote
  session ... HTTP 500 on POST /session: TypeError: can't access
  property \"namespaceURI\", browserElement is null" (same as
  22:06-22:19, #registerBrowser/#registerWindow/newSession). The slot
  worked at 22:44 (gate) and 22:55 (evals), broke between 22:55 and
  22:56:33. Suspect: the act-now Ctrl+N / new-tab navigation, or the
  eval session DELETE while focused on a new/blank tab (the 22:10
  lesson: DELETE /session when current is a closed/discarded tab
  leaves Zen in a dead-tab state). CORRECTED (council 2, Finding 5;
  F3 log; MEMORY.md 23:14): the timing exonerates act-now. The slot
  worked at 22:55:34 (F3 verify listed 17 tabs, AFTER run 2 at
  22:55:31), close3 ended about 22:56:05, and the slot failed at
  22:56:12. So the break window is 22:56:05-22:56:12, after F3's
  close3, not after F2's run 2. The act-now Ctrl+N suspicion above
  is withdrawn. F3's hypothesis (close3 DELETE of a BiDi-navigated
  Example Domain tab leaves a zombie with null linkedBrowser) fits
  the window but is still UNPROVEN (needs BiDi diagnosis; MEMORY.md
  23:14: zombie CHUA chung minh). This is a timing correction, not
  a root-cause verdict. F3 must fix it (likely another
  Zen restart or a live-tab click). This BLOCKS Y13/Y14 live runs
  (they need Marionette). FLAG TO PARENT as a blocker (owner 23:01
  rule: report blockers immediately).
- 22:58:05 (T+1085s) fresh window observe e76537a263e6 (capture
  37 ms, 1863x1176) for the diagnostic.
- 22:58:17.762 (T+1097s) act-now run 3 (diagnostic, keyboard only):
  batch [Ctrl+L, type "example.com", Enter], window obs e76537a263e6.
  RESULT: OK, path fallback, completed 3/3, total 1592 ms,
  order_to_overlay_ms 314 ms. After-capture de010258f1fd.
- 22:58:53 (T+1133s) obs5 (screen ad4c19f94946) VERIFIES the
  diagnostic: urlbar shows "example.com", active tab is "Example
  Domain", main area shows the Example Domain page ("This domain is
  for use in documentation examples..."). So Ctrl+L DOES focus the
  urlbar and typing + Enter navigates. The keyboard path works; the
  MOUSE CLICK on the urlbar does not focus it. The navigation
  happened on a run-opened tab (run 2's Ctrl+N tab), not a baseline
  tab. CORRECTION (council 2, Finding 1): the 'Tab count now 68'
  claim is RETRACTED. F3's cleanup_full launched 22:54:22 and closed
  52 tabs (68 to 16 at 22:54:50); F3's live verify at 22:55:34 listed
  17 tabs. The sessionstore (68 tabs, dated 22:55, not updated since)
  was stale and must not have been used as a counter at all.
- 22:59:31 (T+1171s) fresh window observe 70cd5cc023ea (capture
  33 ms) for the mouse-click retest.
- 22:59:40.680 (T+1180s) act-now run 4 (mouse-click retest): batch
  [Ctrl+N, wait 500 ms, click urlbar (120,60), type "example.org",
  Enter], window obs 70cd5cc023ea. RESULT: OK, path fallback,
  completed 5/5, total 1998 ms, order_to_overlay_ms 346 ms.
  After-capture c35ef9025e45.
- 23:00:08 (T+1208s) obs6 (screen 0f0efdb160bd) VERIFIES run 4
  FAILED to navigate: urlbar still shows "example.com", active tab
  still "Example Domain", main area still the Example Domain page.
  No example.org tab. So the mouse click on the urlbar does NOT
  focus it, 2/2 attempts (run 2 without wait, run 4 with 500 ms
  wait after Ctrl+N). HYPOTHESIS (redteam A7, downgraded from
  CONFIRMED FINDING): in this Zen layout, a mouse click on the
  sidebar-top urlbar/search field lands (cursorpos exact on run 2)
  but may not focus it for URL entry; Ctrl+L is required for now.
  NOT proven: the 2 attempts used an identical target, identical
  coords, and an identical sequence shape, with zero hover dwell
  before the click, no control click, no double-click, no click
  without the preceding Ctrl+N, and the field identity read off a
  screenshot, not DOM/a11y. Discriminating probes before calling
  it proven: hover 100 ms then click; click a control text field;
  click the urlbar without a preceding Ctrl+N; double-click.
  ZT-00 step 4 as written (mouse click the address bar) stays
  blocked (the mouse path did not navigate 2/2). Act-now delivery
  itself is exonerated (coordinate conversion and press/release
  are correct). Record in the error file as a new finding (G29),
  scoped as a hypothesis, cross-referenced to H3.
- 23:00:55 (T+1255s) sessionstore read: recovery.jsonlz4 still
  dated 22:55 (NOT updated since), 68 tabs, Example Domain at index
  50. The sessionstore is stale and NOT a reliable live tab counter
  right now. Do not use it to verify the close; use a visual
  observe instead.
- 23:01:21.625 (T+1281s) act-now run 5 (ZT-00 step 7, close):
  batch [Ctrl+W], window obs e656ed429720 (fresh, 1863x1176).
  Pre-close check: active tab was "Example Domain" (obs6). RESULT:
  OK, path fallback, completed 1/1, total 865 ms,
  order_to_overlay_ms 330 ms. After-capture 2155674040fa.
- 23:01:36 (T+1296s) obs7 (screen 8bf0f6b1ade5) VERIFIES the close:
  active tab is now "Welcome!" (zen-browser.app, "Welcome to Zen!"
  page). CORRECTION (council 2, Finding 1): the '67 or 68' final
  count and the 'at most 1 extra blank tab' bound are RETRACTED. The
  67 baseline no longer existed after F3's cleanup (22:54:22-22:54:50,
  68 to 16 tabs; F3 verify 22:55:34 listed 17; close3 22:56:01 closed
  3 more to 15; final 14 real tabs, 0 fixture). The sidebar 'Example
  Domain' row in obs7 is the zombie F3 proved at 23:01:10 (clicking
  the row selects 'New Tab' instead; no browsing context), NOT F3's
  baseline tab (index 10), which close3 had already closed at
  22:56:01. Run 5's Ctrl+W closed whatever tab was active at
  23:01:21 (after F3's 23:01:10 click had selected New Tab, so it may
  have closed the sacrificial New Tab, not an Example Domain tab).
  The close is verified only as 'active tab became Welcome!'. Tab
  identities are confounded, not merely unverifiable. The ZT-00
  step-7 set check therefore cannot be verified tonight; recorded
  honestly.
- 23:01 (T+1260s) owner (MEMORY.md): going to sleep, but if there
  is an error or something that really needs the user, report it (do not
  wait until morning). Big errors, blockers, things needing the user's
  decision: report immediately. Routine work: do quietly, report
  results in the morning. The Marionette slot re-break is a
  blocker; flag it to the parent in the final report.
- 22:57 (MEMORY.md): Y13r2 DONE, verdict BLOCK (4 new blockers B1-B4
  + 5 amend); Y13g spawned to fix per the redteam paper, then a new
  re-review. R6 ROOT CAUSE SOLVED: the re/__init__.py deletion was
  a self-deleting shim from Redteam Y13r2 (A6e) that deleted the
  file by accident (globals().update overwrote __file__ before
  os.remove), NOT a foreign process; VMFIX restored durably
  (c16dd4e). Update R6 in this log (cause now KNOWN, not unknown).
  H3 gate: accept Y13r2's proposal (5a2b69d NO VERDICT + a
  runner-quiet/ports check counts as a done-marker for this run,
  keep the gate text, Y6 retry after Y13). So the live queue is Y13
  next, then Y14, then Y6 retry. My rehearsal is the F2 proof; Y13
  runs after the H3 gate is satisfied.
- 22:49-22:51 (MEMORY.md): owner correction on the graph: it shows
  136 contributions (UTC day), not 190 (+07 day; recount 22:51 is
  201 commits + 1 PR). The graph only counts the default branch
  (main); todolist-push has 290 commits on UTC 21/11 but they do
  NOT count. Worker MERGE spawned to merge todolist-push into main
  to push the graph past 240. My commits stay on todolist-push (the
  merge carries them); I keep committing small there.
- 22:55 (MEMORY.md): clone2-watch cron (15 min) set up: Muse
  switches to workspace 2 (clone2's tab) to check it; if silent
  >15 min, look at what it needs approval for and approve it, or
  prompt it to keep working; switch back to workspace 1 after.
  This explains some workspace switching. Not my task; noted.

### Rehearsal verdict (ZT-00 via act-now)
- Gate steps 0-3: PASS (67 tabs, zen-bin alive, curl 200,
  Marionette session created at 22:44).
- Step 4 (mouse click urlbar + type + Enter): NOT SATISFIED as
  written. The click landed exactly (cursorpos 2629,974 = target),
  the overlay showed, the batch completed, but the navigation did
  NOT happen via mouse click (2/2 attempts). Navigation WAS
  achieved via keyboard (Ctrl+L + type + Enter, run 3). So the
  composite step-4 action did not achieve its end via the specified
  mouse path. Root cause: Zen urlbar click does not focus (finding
  above). ZT-A must fix the scenario.
- Step 5 (title "Example Domain" within 10 s): CONDITION MET, but
  via the keyboard diagnostic (run 3), not via the step-4 mouse
  click. The title was "Example Domain" (obs5).
- Step 6 (hyprctl activewindow diagnostic): done in equivalent form
  (hyprctl clients/monitors used throughout; activeWs tracked).
- Step 7 (pre-close check + Ctrl+W + set check): pre-close check
  PASSED (active tab was Example Domain). Ctrl+W ran (active tab now
  Welcome!). Set check: CANNOT VERIFY (Marionette broken,
  sessionstore stale, and F3's concurrent cleanup confounded the tab
  identities; live count 14-17, not 67-68). The close is verified
  only as 'active tab became Welcome!', not as 'my Example Domain
  tab closed'.
- Overall: ZT-00 as a scenario is INCONCLUSIVE (step 4 mouse path
  blocked by the Zen urlbar behavior; step-7 set check unverifiable
  tonight). The F2 FIX (act-now) is PROVEN on its own claims, scoped
  to the FALLBACK path: all 4 OK runs took the fallback (the session
  guardian failed every time), so the session path was never
  exercised in this rehearsal and is untested here. Overlay in
  314-346 ms (4 runs), fallback works (4/4 runs, session guardian
  fails -> desktop_act completes), full batches in 0.87-2.0 s. The
  ~5.5 min baseline is end to end (agent thinking + diagnosis before
  any command ran); the act-now numbers start at command start and
  exclude agent decision and observation time, so the under-30 s rule
  from a user order is NOT yet demonstrated end to end. The 333 ms
  figure is the session-attempt start (order_to_session_attempt_ms),
  not the first pointer move; the first pointer move is bounded by
  the total batch time (0.87-2.0 s). The click landed exactly on run
  2 (cursorpos 2629,974 = target, 0 px error), read 22:56:33 about
  60 s after run 2 finished, with no pointer move recorded in
  between; run 4 has no cursorpos check. The pill is visually
  confirmed in runs 2, 3, 4, 5 via their after-captures (fetched
  from the laptop and viewed; run 1 has no after-capture, it
  refused). Keyboard navigation works. The urlbar-click finding is
  a Zen UI issue for ZT-A / the error file, not an act-now defect.

### R6 update (root cause SOLVED, 22:57)
- The re/__init__.py deletion cause is now KNOWN: a self-deleting
  shim from Redteam Y13r2 (A6e) accidentally deleted the file
  (globals().update overwrote __file__ before os.remove). NOT a
  foreign process. VMFIX restored it durably (commit c16dd4e,
  dpkg -V clean). This log's R6 "cause UNKNOWN" is superseded.

- 23:03 (T+1380s) rule doc updated (CLI-first, log-everything,
  commit-small-and-many, Lauren Tan no-cutting-steps, typing needs a
  window observation, Zen urlbar-click finding, rehearsal measured
  numbers). Committed 82539bf, pushed, ls-remote verified. 9th F2
  commit.
- 23:03 (T+1380s) owner (MEMORY.md): DEFERRED, LOW: Zen keybinds.
  Sometime go into Settings, Shortcuts of Zen on the user's machine, record
  the Zen keybinds into the computer-use copy ON THE MACHINE
  (machine-specific layer, local-only), do NOT push to the repo. Not
  important, do later. Not done; saved for later. Noted as a
  follow-up: knowing the keybinds (e.g., Ctrl+L) helps diagnose the
  urlbar-click finding, but it is a separate deferred task, not part
  of F2.
- 23:04 (T+1440s) council + redteam spawned (4 subagents, parallel):
  council 1 (code correctness), council 2 (evidence + measurement),
  council 3 (rule + error-file plan), redteam (attack the fix).
  Each writes its verdict to improvements/worker-f2-council-1/2/3.md
  or improvements/worker-f2-redteam.md and returns GO/AMEND/BLOCK
  to F2. F2 commits the verdict files. No code changes by reviewers,
  no live driving, no commits by reviewers.
- 23:04 (T+1440s) error-file prep (not yet written, waits for the
  council verdicts): located the exact lines in
  ~/workspace/cf26-upload/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md.
  H2 fix line is line 307 ("Cách sửa: CHƯA XÁC ĐỊNH. Cần đo think
  time từng bước..."). G27 ends line 292, Part H starts line 294,
  so G28 goes after G27. Part J exists (J10 at line 694). The update
  will be: H2 fix line -> the act-now path with the measured numbers,
  new G28 (screen observation cannot type), the urlbar-click finding,
  R6 root cause solved. The error file is NOT in the repo, so it is
  NOT committed.

### Council verdicts + fixes (23:05-23:17)
- 23:06 council 3 verdict (AMEND, R1-R6 + M1-M4), file committed
  f9f3184. Required: narrow the determinism claim (R1), H2 PARTIALLY
  fixed with the exact wording (R2), fix the 30 s / 60 s enforcement
  wording and the D2 ordering sentence (R3), correct the
  typing-refusal exit code (exit 1, not exit 2) and state the
  window-obs precondition (R4), add `omarchy-menu toggle root` and
  the J23 unsolved-workspace-switch note (R5), add G28 + G29 with the
  exact texts (R6). The doc fixes R1/R3/R4/R5 and the log
  supersessions M2/M3/R5 were applied to the rule doc and this log
  and are committed separately (see below). R2/R6 go in the error
  file, which waits for the redteam verdict.
- 23:07 council 1 verdict (BLOCK, B1-B3 + A1-A5), file committed
  2b5e6cb. The fallback safety predicate had two false-positive
  replay paths plus a fail-open liveness check. Fix applied to
  scripts/first_action.py (commit bb8f4e3): B1 timeout NEVER falls
  back (the driver may have acted and been torn down); B2 substring
  matching replaced by a positive start-failure signal (parsed
  stdout JSON error starts with 'session guardian startup failed'
  or 'driver registration failed', both emitted by supervise before
  the driver can act, cursor_session.py:275, :290); B3 the
  post-kill session_live probe removed entirely (it measured
  liveness after the kill, which cannot prove "never started");
  A1 acquire failure removes the holder again (no leak); A2 run()
  never lets an exception escape (single JSON envelope, deadline
  validated positive and finite); A3 session success requires the
  stdout envelope to say ok (or the completed-capture-error shape);
  A4 bad actions file goes through the envelope + log; A5 the
  overlay is re-checked (status) immediately before the fallback
  acts, and a release failure is recorded in the envelope; M1 the
  stderr tail is used only when it names a failure; M2 the STATE
  dir is created and a log failure is recorded; M3 the overlay
  module is threaded through run() instead of re-imported in the
  fallback branch. Field rename (council 2, Finding 2):
  order_to_action_start_ms is now order_to_session_attempt_ms
  (it measures the session-attempt start, not the first pointer
  move). The 5 rehearsal envelopes below still carry the old field
  name; that is the historical record, not an error.
- 23:07 council 2 verdict (AMEND, findings 1-7), file committed
  8bfc8c8. Corrections applied in this log and the rule doc:
  Finding 1 tab accounting (F3 ran cleanup_full 22:54:22,
  68 to 16 tabs, during the rehearsal; '67 or 68' and the run-5
  close attribution retracted; tab identities confounded);
  Finding 2 the baseline comparison scoped (act-now timings start
  at command start; the under-30 s rule from a user order is not
  yet demonstrated end to end; the 333 ms figure is the
  session-attempt start); Finding 3 raw envelopes pasted below;
  Finding 4 pill scope RESOLVED BY VIEWING: the after-captures for
  runs 3, 4, 5 were fetched from the laptop and viewed, and the
  pill 'Muse via act-now' is visible in all three, so the pill is
  visually confirmed in runs 2, 3, 4, 5 (run 1 has no
  after-capture, it refused); Finding 5 Marionette attribution
  corrected to the 22:56:05-22:56:12 window after F3 close3 (timing
  correction, root cause still unproven); Finding 6 the verdict
  scoped to 'fallback path proven; session path untested in this
  rehearsal' plus the default-use gap as a follow-up; Finding 7
  the click exactness scoped to run 2 with the 60 s caveat.
- 23:08 tests: 41 tests, ALL PASS, 0.575 s (21 original + 20 new
  counter-examples). Test file committed fca30c1.
- 23:09 the fixed first_action.py deployed to the laptop
  (~/.local/share/agent-computer-use/scripts/),
  md5 dc6b5cfd01bf152f038e36ac8f1c38c0 on both sides,
  `computer-use act-now --help` works, import OK with the new
  START_FAILURE_PREFIXES. cu.py on the laptop unchanged (it already
  carries the act-now wiring).
- 23:14 (MEMORY.md): F3 DONE + SLOT RE-WEDGED. F3 proved the
  Marionette root cause from source (driver.sys.mjs #registerWindow
  4639 passes null to #registerBrowser 4616); restart 22:36 fixed
  it (session 0.1 s); cleanup redo 22:54-22:56 closed 55 tabs, 14
  real tabs left, 0 fixture (verify 22:55:34); J21 = F3's click
  (the app-launcher button, not workspace 1). BUT the slot wedged
  again 22:56:12 (4 retries failed), zombie NOT proven, council 3x
  AMEND + redteam BLOCK (B7: 4 close methods untested). Muse
  approved a 2nd restart (F3b, baseline first, try right-click
  Close Tab first, then test distinguishing Arms A/B/C). Live
  Y13/Y14 blocked tonight. This confirms the council 2 Finding 1
  tab counts (14-17, not 67-68) and the Finding 5 qualification
  (the zombie hypothesis is unproven).
- 23:05 (MEMORY.md): MERGE DONE + GRAPH 456. main HEAD 5c94e6c
  (merge 0ac4311 todolist-push 313 commits + 0c473f9), 3 conflicts
  kept both sides, suite 1618 tests: 3 fail + 5 error (all
  pre-existing in baseline, 0 regression, +124 tests). Graph UTC
  21/11 recount: 455 commits + 1 PR = 456, EXCEEDS the 240 target.
  My F2 commits are on main via that merge.
- Redteam verdict LANDED 23:19 (improvements/worker-f2-redteam.md,
  commit bbbbf73): BLOCK, A1-A9. Fixes applied, tested, committed,
  deployed (see the "Redteam BLOCK fixes" section below). A council
  1 re-review of the BLOCK fix + a redteam re-check are owed before
  this lands. The error-file update (H2 partial wording, G28, G29,
  R6 solved) waits for the re-reviews.

## Redteam BLOCK fixes (applied 23:20-23:25)

- A1 (phase-aware replay classifier): the start-failure prefixes ARE
  the phase evidence. supervise raises 'session guardian startup
  failed' only BEFORE the driver is spawned (cursor_session.py:275)
  and 'driver registration failed' only when 'registered' is NOT
  received within 2 s, before the 'go' gate byte is written
  (cursor_session.py:290). The error can only be raised in the
  pre-driver phase, so a matching prefix proves the driver never
  started. A post-start 'Expecting value' or 'cursor guard' can
  never carry these prefixes. No further change needed beyond the
  council 1 fix (bb8f4e3).
- A2 (session deadline): the deadline clamp is implemented as an
  upper bound of 120 s (the observation freshness window), with
  REFUSAL (not silent clamping) for out-of-range values (0,
  negative, non-finite, >120 s). The lock-timeout point is based
  on a FALSE premise: cu.locked() is a NON-BLOCKING flock
  (cu.py:1988-1993, LOCK_EX|LOCK_NB, raises RuntimeError on
  contention), so the fallback already fails fast instead of
  hanging forever; no lock timeout is needed. The SIGTERM-grandchild
  test was NOT implemented: the timeout fallback was removed (B1),
  so there is no replay risk from a surviving process, and orphan
  cleanup is the supervisor's finally (terminate_driver +
  guard.wait), which is the session machinery's domain (F1), not
  act-now's. The whole-run time budget is recorded in the envelope
  as target_breached (total_ms > 30000).
- A3 (overlay show ack): _show_label returns bool (True only on
  ack; daemon path retries once after _ensure_native; session path
  returns session_label(label) and session_live()); apply_holders
  returns visible False with error 'pill show failed' when the
  show ack fails. The fallback re-check now uses a 'sync' round
  trip (not 'status'): apply_holders (called by 'sync') returns
  visible False on a show failure, while 'status' only reports
  whether holders exist.
- A4 (per-run holders + prune): holders are keyed by (agent, pid)
  via _holder_key() (key f"{agent}:{pid}" for a positive int pid,
  bare agent name for backward compat); remove_holder(agent,
  pid=None) removes only that run's entry when a pid is given, or
  all of the agent's entries when pid is None; the daemon serve()
  'release' handler passes req pid to remove_holder; cmd_release
  gained a --pid argument. prune_dead_holders is called by
  _ensure_daemon and by apply_holders (start of reconcile). A
  killed run leaves no live holder.
- A5 (fallback preflight refusals): the fallback desktop_act call
  is wrapped in an inner try/except (ValueError, RuntimeError)
  that writes the error into the envelope, keeps path 'fallback',
  returns 1 cleanly with no traceback, and still attempts the
  after-capture.
- A6 (stale observation): _fresh_observation takes deadline_s
  (default 20.0) and requires age + deadline < 120 s
  (OBSERVATION_MAX_AGE_S) for a given observation to count as
  fresh. Up-front scope/backend/window validation was NOT
  implemented: desktop_act already enforces it, and the refusal
  is now clean (A5), so the age+deadline budget is the concrete
  fix and the scope check is covered by the clean-refusal path.
- A7 (urlbar claim): downgraded from CONFIRMED FINDING to
  HYPOTHESIS in the rule doc and in this log (run 4 entry). The
  discriminating probes are queued for the next live run (hover
  100 ms then click; click a control text field; click the urlbar
  without a preceding Ctrl+N; double-click). Do NOT drive Zen
  live now (Marionette slot broken, F3b restart pending, owner
  asleep).
- A8 (session-path completion): fixed by the council 1 fix (A3):
  session success requires the stdout envelope to say ok (or the
  completed-capture-error shape, cu.py:1341).
- A9 (tests): 46 tests in test_first_action.py (41 + 5 new:
  huge deadline refused, target_breached recorded, age+deadline
  must stay under 120, age+deadline within 120 is used, fallback
  desktop_act raises ValueError), 11 tests in test_overlay.py
  (7 + 4 new: two same-agent pids independent, show-label bool,
  apply-holders visible False on show failure, apply-holders
  prunes dead holders). All pass on the VM (0.592 s + 0.097 s).
  Overlay-adjacent suites also pass with no regression:
  test_indicator.py 42 OK, test_phase3_cleanup.py exit 0,
  test_activate_glass.py 12 OK, test_visuals.py 34 OK.
- Rule doc: A7 downgrade (f584a20) + CLI-first workspace command
  (hl.dsp.focus({ workspace = 2 }) switches in ~1 s, verified
  23:19; hl.dsp.workspace.goto FAILS, goto is a Lua reserved
  word). Log: A7 downgrade + workspace update (8767d9b).
- Commits (all pushed, verified via ls-remote, remote HEAD
  8767d9b): 91895b3 (overlay.py A3+A4), 268fcbf
  (first_action.py A2+A5+A6), dcabc4c (test_first_action 46
  tests), 3eb53b1 (test_overlay rekey/show-ack/prune tests),
  f584a20 (rule doc A7 + workspace), 8767d9b (log A7 +
  workspace).
- DEPLOY 23:25: overlay.py + first_action.py scp'd to the
  installed scripts dir. First scp attempt failed ("Connection
  closed"): the scp call lacked -i/IdentitiesOnly, so it tried
  the default keys and fell back to password (the known AGENTS.md
  lesson: a bare ssh/scp without -i/IdentitiesOnly reports
  Permission denied with the same key). Retried with
  -i /home/hatch/.ssh/id_ed25519 -o IdentitiesOnly=yes and it
  worked. md5s match on both sides: overlay.py
  6df09642a9ef931d61d533d9c37de386, first_action.py
  8caff3651bc2d11d2101f05d5f030e9f. No overlay daemon was
  running (holders {}), so the next acquire spawns a fresh
  daemon with the new code; no restart was needed.
  Verified on the laptop: `computer-use act-now --help` works;
  rekey smoke test passes on the deployed copy (two same-agent
  pids independent, releases isolated); overlay status is
  holders {}, owner none, visible false (clean).
- MEMORY.md 23:22: owner ordered keybind integration (find all
  keybinds, integrate into computer-use). Worker KB is collecting
  them (Omarchy + Hyprland + Zen) into the computer-use copy ON
  THE MACHINE (local-only, not pushed to the repo). The deferred
  Zen-keybinds item (23:03) now has an owner (KB); F2 does not
  duplicate it.
- NEXT: re-review (council 1 + redteam re-check) of the BLOCK
  fixes, then the error-file update (H2 partial wording, G28,
  G29, R6 solved), then the final report to the parent. The
  final test (independent Codeforces contest, 5 problems) runs
  LAST, after all other work; not started.

## Re-review verdict (BLOCK on D1, fixed 23:35)

- Re-review LANDED 23:33 (improvements/worker-f2-rereview.md,
  commit 1a45f8d): BLOCK on ONE remaining defect, D1.
  Everything else verified FIXED against source (council B1/B2/
  B3, A1-A5, M1-M3; redteam A1, A3, A5, A7, A8; A2 lock-timeout
  premise confirmed false; A6 scope-skip reasoning sound).
  Test counts confirmed: 46 + 11, all green on the VM.
- D1: `overlay.cmd_acquire` (overlay.py:494-503) called
  add_holder first with no cleanup, so a daemon-start or socket
  failure left a holder with pid None that prune_dead_holders
  (int pids only) can never drop. The pill stays up after the
  run ends. Same defect class as redteam A4, in the same file,
  but F2 applied the remove-on-failure only to
  first_action.acquire_overlay. The re-review ran both repros
  from /tmp (isolated BASE): daemon failure and socket failure
  each left {'Muse': {..., 'pid': None}} and prune removed [].
- FIX (commit 1c6344e): cmd_acquire now wraps the post-add_holder
  steps in try/except and calls remove_holder(args.agent,
  args.pid) on failure, then re-raises; mirrors
  first_action.acquire_overlay (first_action.py:116-131).
  TEST (commit 526919d): test_cmd_acquire_failure_leaks_nothing
  (daemon failure + socket failure, each asserts holders == {}
  and prune == []). First run of the test failed on a test bug:
  the socket-fault half used the REAL _ensure_daemon, which
  exits during startup on the VM (no Wayland); fixed by
  monkeypatching _ensure_daemon to a no-op for that half.
  Suites now: test_overlay.py 12 tests pass, test_first_action.py
  46 tests OK.
- DEPLOY 23:35: overlay.py scp'd to the installed scripts dir
  (md5 9d2473ce3aa78404f32b69add0b27a01 on both sides);
  first_action.py unchanged since the 23:25 deploy. Overlay
  status clean (holders {}, owner none, visible false).
- MEMORY.md 23:33: KB DONE (commit 9e9b811): no Omarchy skill
  (independent search 0 results); the fumbling cause was
  fastest-paths.md on the machine writing the WRONG workspace
  command (string dispatcher, proven broken live 23:32 rc=7);
  the correct hl.dsp.focus command was proven 23:19. KB
  integrated 250 Omarchy/Hyprland binds + 85 Zen binds into the
  computer-use copy ON THE MACHINE (local-only); fastest-paths
  fixed 6 broken lines; repo added scripts/hypr_cmd.py + tests
  13/13 OK. Still unsolved: move-to-workspace, absolute resize,
  {omarchy/panel/ipc/menu} table forms (keypress-only), Zen has
  no CLI.
- NEXT: narrow D1 re-check (spawned 23:35) verifies the fix +
  the test and checks hold() for the same leak class; then the
  error-file update (H2 partial wording, G28, G29, R6 solved),
  then the final report to the parent. Re-review amends NOT
  implemented in this pass (A-M2 status reports holders not
  pill-rendered, A2 grandchild test, A6 up-front scope
  validation, whole-run budget recorded not enforced): recorded
  as follow-ups, none blocks the fix.

## D1 re-check GO + error-file update (23:38-23:40)

- D1 RE-CHECK LANDED 23:38 (improvements/worker-f2-rereview-d1.md,
  commit 44baabf): GO, D1 fixed. Tests measured: test_overlay.py
  12 tests pass, test_first_action.py 46 tests OK (0.580 s).
  Both D1 repros re-run against the fixed code (isolated BASE,
  /tmp/d1_rereview_repro.py): daemon failure and socket failure
  each leave holders {} and prune []. Success path intact
  (returns 0, visible true, label 'Muse via act-now', holder
  present). hold() (overlay.py:572-585) shells out to
  `overlay.py acquire`, i.e. the fixed cmd_acquire, so it is
  covered. cmd_release no-daemon branch verified by run (removes
  the holder, returns 0, holders {}). Daemon 'acquire' handler
  has no try around add_holder + apply_holders, but a raise
  there kills the daemon reply, the client sees EOF, and
  cmd_acquire's except path removes the holder from the same
  holders.json: no leak left by that path.
- HARDENING NOTE (not a BLOCK, applied anyway): if _send_socket
  returned a non-dict JSON value, `reply['label'] = label`
  (outside the try) raises TypeError and the holder leaks
  (demonstrated with a mocked socket; prune removes []). It is
  unreachable through the real daemon (every reply is a dict
  literal). Applied the re-checker's one-line follow-up:
  moved the label assignment INSIDE the try (commit 4c32fc4)
  + test (non-dict reply leaks nothing, commit 1c08f8a).
  Suites: test_overlay.py 12 pass, test_first_action.py 46 OK.
  Deployed: overlay.py md5 c7e815b544f07350effbd2d84e75c185 on
  both sides; overlay status clean. Two observations recorded
  as follow-ups, not fixed: pid-None remove_holder in the fix
  over-removes a concurrent same-agent holder (pre-existing
  remove_holder behavior on the pid-None CLI path); cmd_acquire
  returns 0 on a visible False daemon reply (pre-existing).
- ERROR FILE UPDATED 23:40 (~/workspace/cf26-upload/LOI-VA-GIAI-
  PHAP-TOAN-BO-20261121.md, NOT in the repo, NOT committed):
  H2 fix line replaced with council 3's exact wording (SỬA MỘT
  PHẦN: the visible-silence slice fixed by act-now, think time
  still open, cites J10; the old CHƯA XÁC ĐỊNH line kept marked
  as replaced, H1 convention); G28 added (screen observation
  cannot type, cu.py:1475, council 3 exact text); G29 added
  (urlbar click, ZT-A owns the scenario fix, cross-referenced
  to H3) WITH the redteam A7 downgrade (GIẢ THUYẾT, CHƯA CHỨNG
  MINH, with the caveats and the 4 discriminating probes),
  not council 3's original "hành vi UI của Zen" wording.
  R6/J7 needed NO edit: the file already records the root
  cause as solved (Y13r2 self-deleting shim, VMFIX c16dd4e).
  Verified: 0 em dashes, 0 en dashes in the file, 756 lines.
- FINAL STATE: council 1 BLOCK fixed + re-reviewed, council 2
  AMEND fixed, council 3 AMEND fixed, redteam BLOCK fixed +
  re-reviewed (BLOCK on D1 only, D1 fixed + re-checked GO +
  hardening applied). act-now is the proven fallback path
  (overlay 314-346 ms, batches 0.87-2.0 s, pill visually
  confirmed runs 2-5); the session path is still untested live
  (guardian fails every time, F1 owns it). ZT-00 as a scenario
  is INCONCLUSIVE (urlbar-click hypothesis, step-7 set check
  unverifiable, tab identities confounded by F3's concurrent
  cleanup). The final test (independent Codeforces contest, 5
  problems) runs LAST, after all other work; not started.
  The deferred Zen-keybinds item is owned by Worker KB (done,
  9e9b811).

### Raw rehearsal envelopes (council 2, Finding 3)
Fetched from the laptop STATE/first-action-20261121.jsonl
(~/.cache/agent-computer-use/first-action-20261121.jsonl,
5 lines, 5041 bytes) and pasted verbatim. The numbers match this
log exactly. After-capture images are on the laptop at
~/.cache/agent-computer-use/<id>.jpg; the pill is visible
in runs 2 (594806e130f1), 3 (de010258f1fd), 4 (c35ef9025e45), 5
(2155674040fa); run 1 has no after-capture (refused).

{"after": null, "after_error": null, "agent": "Muse", "completed": 0, "fallback_reason": "session guardian startup failed: cursor guard reply is not valid JSON (got: unknown request); the cursor backend may not be loaded, load it with scripts/activate-glass.py and scripts/activate-cursor-guard.py or re-run the fresh-login loader scripts/visuals.py", "method": "act-now", "observation": {"id": "ce2bf0b9a594", "source": "given"}, "ok": false, "order_to_action_start_ms": 356.079, "order_to_overlay_ms": 356.003, "overlay_owner": "daemon", "path": "refused", "session_error": "session guardian startup failed: cursor guard reply is not valid JSON (got: unknown request); the cursor backend may not be loaded, load it with scripts/activate-glass.py and scripts/activate-cursor-guard.py or re-run the fresh-login loader scripts/visuals.py", "session_timed_out": false, "total_ms": 638.216, "wall_time": "2026-11-21T22:53:57.440+07:00"}
{"after": {"id": "594806e130f1", "observation": "~/.cache/agent-computer-use/594806e130f1.json"}, "after_error": null, "agent": "Muse", "completed": 4, "fallback_reason": "session guardian startup failed: cursor guard reply is not valid JSON (got: unknown request); the cursor backend may not be loaded, load it with scripts/activate-glass.py and scripts/activate-cursor-guard.py or re-run the fresh-login loader scripts/visuals.py", "method": "act-now", "observation": {"id": "cdd81db8e871", "source": "given"}, "ok": true, "order_to_action_start_ms": 333.438, "order_to_overlay_ms": 333.388, "overlay_owner": "daemon", "path": "fallback", "session_error": "session guardian startup failed: cursor guard reply is not valid JSON (got: unknown request); the cursor backend may not be loaded, load it with scripts/activate-glass.py and scripts/activate-cursor-guard.py or re-run the fresh-login loader scripts/visuals.py", "session_timed_out": false, "total_ms": 1477.763, "wall_time": "2026-11-21T22:55:31.694+07:00"}
{"after": {"id": "de010258f1fd", "observation": "~/.cache/agent-computer-use/de010258f1fd.json"}, "after_error": null, "agent": "Muse", "completed": 3, "fallback_reason": "session guardian startup failed: cursor guard reply is not valid JSON (got: unknown request); the cursor backend may not be loaded, load it with scripts/activate-glass.py and scripts/activate-cursor-guard.py or re-run the fresh-login loader scripts/visuals.py", "method": "act-now", "observation": {"id": "e76537a263e6", "source": "given"}, "ok": true, "order_to_action_start_ms": 314.537, "order_to_overlay_ms": 314.463, "overlay_owner": "daemon", "path": "fallback", "session_error": "session guardian startup failed: cursor guard reply is not valid JSON (got: unknown request); the cursor backend may not be loaded, load it with scripts/activate-glass.py and scripts/activate-cursor-guard.py or re-run the fresh-login loader scripts/visuals.py", "session_timed_out": false, "total_ms": 1591.814, "wall_time": "2026-11-21T22:58:17.815+07:00"}
{"after": {"id": "c35ef9025e45", "observation": "~/.cache/agent-computer-use/c35ef9025e45.json"}, "after_error": null, "agent": "Muse", "completed": 5, "fallback_reason": "session guardian startup failed: cursor guard reply is not valid JSON (got: unknown request); the cursor backend may not be loaded, load it with scripts/activate-glass.py and scripts/activate-cursor-guard.py or re-run the fresh-login loader scripts/visuals.py", "method": "act-now", "observation": {"id": "70cd5cc023ea", "source": "given"}, "ok": true, "order_to_action_start_ms": 345.817, "order_to_overlay_ms": 345.766, "overlay_owner": "daemon", "path": "fallback", "session_error": "session guardian startup failed: cursor guard reply is not valid JSON (got: unknown request); the cursor backend may not be loaded, load it with scripts/activate-glass.py and scripts/activate-cursor-guard.py or re-run the fresh-login loader scripts/visuals.py", "session_timed_out": false, "total_ms": 1998.431, "wall_time": "2026-11-21T22:59:40.741+07:00"}
{"after": {"id": "2155674040fa", "observation": "~/.cache/agent-computer-use/2155674040fa.json"}, "after_error": null, "agent": "Muse", "completed": 1, "fallback_reason": "session guardian startup failed: cursor guard reply is not valid JSON (got: unknown request); the cursor backend may not be loaded, load it with scripts/activate-glass.py and scripts/activate-cursor-guard.py or re-run the fresh-login loader scripts/visuals.py", "method": "act-now", "observation": {"id": "e656ed429720", "source": "given"}, "ok": true, "order_to_action_start_ms": 330.067, "order_to_overlay_ms": 329.967, "overlay_owner": "daemon", "path": "fallback", "session_error": "session guardian startup failed: cursor guard reply is not valid JSON (got: unknown request); the cursor backend may not be loaded, load it with scripts/activate-glass.py and scripts/activate-cursor-guard.py or re-run the fresh-login loader scripts/visuals.py", "session_timed_out": false, "total_ms": 865.078, "wall_time": "2026-11-21T23:01:21.680+07:00"}
