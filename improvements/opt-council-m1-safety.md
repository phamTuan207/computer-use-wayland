# Council OPT-M1, Voice 3: SAFETY
# Classes (A) session/guardian startup failure, (B) silence / slow first action,
# (C) overlay never shows / flicker. What each method risks on the live machine
# while the owner sleeps, what must never happen. No em/en dashes in this file.

## Method of this voice
Assume the owner is asleep and cannot intervene. Assume any live step can fail
in the worst way it can fail. A method is safe only if its worst failure is
bounded, recoverable without the owner, and logged with timestamps. "It worked
before" is not a safety argument. Every veto below names the exact failure it
prevents and the source that proves the failure is real.

## Hard vetoes (never, under any circumstances, tonight)

### V1. Never load hyprglass live while the F-team works
- Failure prevented: a plugin load crash kills the whole compositor with the
  owner asleep. Source: F1 council 2 F1, LOG improvements/worker-f1-council-2.md
  (plugin load dlopens in-process; a segfault kills Hyprland PID 1515 outright
  with every window and unsaved work; no sandbox, no snapshot, no auto
  recovery). Todolist gate G-PILL states it directly: never load hyprglass
  live when the F-team is fixing the machine.
- Applies to: class C2 flicker measurement (todolist 2.2.3 BLOCKED for exactly
  this reason), any Y6 retry, any "just try loading it" shortcut. The nested
  Hyprland (owner choice C, 18:24) is the only approved measurement route.
- The residual risk after the veto is zero for this failure mode, because the
  live compositor is never touched by a load. The cost is delay: C2 measurement
  waits for the nested path. That cost is acceptable; a dead compositor at 03:00
  with the owner asleep is not.

### V2. Never blind-retry a plugin load
- Failure prevented: double load, half-loaded state, misleading errors.
  Sources: F1 council 2 F2 (activate-glass.py takes no owner_lock and no
  session/token check; concurrent runs can both pass the pre-load check; a
  retry after partial success fails closed at setup_baseline with a misleading
  message), F4 (glass ok but reload refused or wait_for_profile timeout leaves
  glass loaded with no rollback and no documented recovery), F5 (hyprctl
  timeouts of 5s glass and 10s guard leave load state unknown; a blind retry
  could double load), F3 (TOCTOU on the .so files: digest computed, then loaded
  by path with no re-hash; post-load asserts check only name/author/version,
  not the loaded sha).
- Rule: re-query the plugin list before ANY retry. Never re-run activate-glass
  after a partial success; guard-only retry. Wait longer for slow shaders
  (F9: shader warm-up can exceed the 8s wait; a first guard refusal may mean
  slow shaders only). Hold owner_lock across the whole glass plus guard
  sequence; no concurrent writers to the plugins dir; no sync-installed during
  it. The lock-holding wrapper must be built BEFORE the activation (F1 council
  2 precondition 4), because activate-glass.py takes no lock today.
- Applies to: class A live activation (F1 plan B) and any future load.

### V3. Never drive while the owner is at the keyboard
- Failure prevented: focus steal, input freeze, lost work. Source: todolist
  4.25 and MEMORY.md (2026-11-21 17:59 live-runner focus steal: worker Y4
  probes navigated fixture tabs in the owner Zen while the user was using the machine;
  the user's physical keyboard + mouse stopped responding for about 1 minute). Owner
  rule 17:59: a live runner must NEVER open/navigate/switch tabs in the user's Zen
  while the user is at the keyboard.
- Tonight the owner is asleep, so this veto binds differently: no live driving
  at all until the morning handover, except the single-operator, F3-signed-off
  activation and rehearsal windows defined in the verdict, and even then only
  if no human input is observed. If the owner wakes and touches the machine,
  stop driving at once and log the stop with time.

### V4. Never click workspace, menu, or bar buttons
- Failure prevented: stray menu opens, workspace switches, lost context.
  Source: owner correction 22:45 (open the Omarchy menu and switch workspaces
  by COMMAND, hyprctl dispatch in hl.dsp form, never by clicking workspace/menu
  buttons on the bar; CLI first, mouse last). Evidence it already happened:
  a click missed workspace 1 and opened the Omarchy menu around 22:44; F3 log
  records a second menu-opening miss at 22:45:38 (wtype Logo+1 bound to the
  system menu, not workspace 1). Attribution of the 22:44 click is still open.
- Rule: workspace and menu moves use commands only. The exact launcher command
  must be read from the Hyprland/Omarchy config, never guessed (F3 open item 1).
  The rehearsal and the activation proof contain at most one planned pointer
  click, on the already-active tab only, never on the bar.

### V5. Never act invisibly
- Failure prevented: a run that moves the machine with no visible sign, which
  is exactly the class B complaint. Source: owner 22:21 (overlay MUST BE
  VISIBLE). F2 R3: overlay acquire is a precondition of any pointer action; if
  the overlay cannot be shown, the action is REFUSED with a clear error, never
  executed invisibly. First_action.py lines 68-90 enforce this in code.
- Applies to: every live run, both paths (session and direct Pointer fallback).
  A fallback that acts without the pill is not a fallback, it is a repeat of
  the 22:17 invisible click.

### V6. Never replay an action that may have partially run
- Failure prevented: double commit, double delete, double add-to-contest.
  Source: first_action.py is_session_start_failure, lines 153-176, and the
  error file I1/I2 (clicks that landed on Remove and Discard nearly deleted
  real work). The fallback is allowed ONLY when no action can have run. Any
  other failure (act refusal, screen-change refusal, timeout with a live
  session) returns False and the actions must never be replayed blind.
- Rule: the fallback predicate is a safety gate, not an optimization. If its
  verdict is ever uncertain, do not fall back; stop and log.

### V7. Never touch the owner data, tabs, or sessions outside the task
- Failure prevented: lost tabs, lost logins, lost work. Sources: todolist
  4.7-4.10 (Zen restore must count 28 real tabs; F3 log 22:48: 67 contexts,
  all 13 real tabs present, one LMS login tab lost because it was never
  flushed to sessionstore); G-TAB (open a sacrificial tab BEFORE closing a
  tab; end the session on a live tab); MEMORY.md shutdown rule (never touch
  the user's Jarvis Codex, Zen tabs, music, cancel latch, or the Omarchy
  input-method indicator.py).
- Rule: the rehearsal opens its own tab and closes only its own tab. The
  activation proof clicks only the already-active tab, and skips the click if
  the active tab is the whiteboard or has unsaved state (F1 council 2
  precondition 6). No other tab is opened, closed, or navigated.

### V8. Never push personal information to GitHub
- Failure prevented: exposure of the owner real name, email, address, schedule.
  Source: MEMORY.md standing rule NO PII ON GITHUB (2026-11-21) and todolist
  4.20 (scrub email + real name from history; 71 lines / 45 files still contain
  the real name; gate G-SCRUB). The council papers contain no PII; the redteam
  must check this before any push, as this council did with grep before each
  commit (0 em/en dashes, no PII in the four papers).

## Risk assessment per class method

### Class A live activation (F1 plan B under preconditions 1-8)
- Worst failure: the glass or guard .so segfaults on load and Hyprland PID 1515
  dies, taking every window and all unsaved work with it, while the owner
  sleeps. Probability: low (exact ABI match, clean ldd on both pinned builds,
  these exact binaries loaded successfully on instance 1795086072), but nonzero
  and uninsurable: there is no snapshot and no auto recovery. Mitigations that
  lower it: preconditions 1-8 in order, single operator, F3 sign-off first,
  same-minute pre-flight, installed-tree scripts only, owner_lock across the
  sequence, no sync-installed during it. Mitigations that do NOT lower it:
  code review, VM tests, and the negative test, none of which exercise a live
  dlopen. Residual risk accepted only because the alternative (sessions dead
  indefinitely) blocks all other work, and because the crash contingency exists.
- Crash contingency (F1 council 2 precondition 7): if the compositor dies or
  the desktop freezes, STOP, report to the parent at once, relaunch NOTHING
  blindly. No automatic restart, no retry loop, no "try loading again". The
  machine waits for a human decision in the morning. This must be written into
  the activation brief verbatim, not paraphrased.
- Second risk: half-loaded state (glass up, guard refused). Recovery is
  guard-only retry after re-querying the plugin list, never a glass re-run.
  If the guard refuses twice, stop and log; do not escalate to a reload.
- Third risk: the activation runs while another worker drives. Mitigation:
  single live runner (G-SINGLE-LIVE), sequence after F3 sign-off, Zen PID
  stable, no parallel driving. The 22:44 unattributed menu click proves two
  workers can touch the same controls within minutes; the activation brief must
  name the single operator and the time window, and every other worker must be
  told the window in advance.

### Class B act-now rehearsal
- Worst failure: the fallback replays an action that already ran (double click
  on Add to Contest, double commit). Probability: low if the predicate holds,
  but the predicate is unit-tested only, never live-proven (evidence paper).
  Mitigation: the rehearsal task must be harmless by design (open a new tab,
  navigate to example.com, close only that tab), so even a double run is
  harmless. Never rehearse on a real Polygon page, a real contest, or any page
  with unsaved state. The rehearsal uses the ZT composite blind test after F3
  sign-off, not a worker-invented task.
- Second risk: the rehearsal runs while the owner is awake and at the keyboard.
  Mitigation: V3. If human input is observed, stop at once.
- Third risk: the overlay acquire succeeds but the pill is not actually visible
  (daemon running, indicator dead). Mitigation: verify the pill in a fresh
  observe before the first click, not just by the acquire reply. The F2 log
  22:25 shows holders.json can be empty with no daemon running; an acquire
  reply alone does not prove a visible pill.

### Class C1 watchdog + hyprglass gate
- Worst failure: the watchdog respawns an indicator in a loop, or respawns the
  wrong indicator, and the pill flickers or duplicates. Probability: low (unit
  tests pass, daemon is reference-counted), but the live respawn proof is still
  owed. Mitigation: the live proof kills the indicator ONCE during a hold and
  watches a single respawn in a fresh observe. If it respawns more than once or
  spawns a duplicate pill, stop and log; do not let a respawn loop run overnight.
- Second risk: the R3 gate, once implemented, refuses sessions that would
  otherwise have worked (glass briefly down during shader warm-up, F9). A gate
  that is too strict converts a working session into a refusal. Mitigation: the
  gate must distinguish "glass not loaded" from "glass loading" (warm-up
  window), and the refusal message must name the state and the remedy.

### Class C2 nested measurement
- Worst failure: the nested Hyprland escapes onto the live desktop (nested
  compositor misconfiguration) or consumes enough resources to disturb the live
  session. Probability: low (Y6d launcher v3 + C2 ALL PASS, Y6e nested LOAD
  TEST PASS 21:57 with live 1515 untouched), but the nested path must be
  verified isolated before the flicker measurement starts: live 1515 untouched,
  no windows moved, no input grabbed. Mitigation: check `hyprctl clients`
  before and after, and abort the measurement if any live window changes.
- Second risk: measuring the wrong thing. The nested compositor has no owner
  windows, no real backdrop, and no real workload. A 0-repaint result there may
  not transfer to the live desktop. Mitigation: the measurement must reproduce
  the live conditions as closely as possible (animated backdrop on, LIQUID mode,
  same optics profile 9a151634) and the verdict must state the transfer gap
  plainly. A nested 0 does not prove the live desktop is clean; it only
  falsifies the compositor-loop hypothesis under those conditions.

## What must never happen, collected
1. Never load hyprglass live while the F-team works (V1, G-PILL).
2. Never blind-retry a plugin load (V2).
3. Never drive while the owner is at the keyboard (V3).
4. Never click workspace, menu, or bar buttons; commands only (V4).
5. Never act invisibly; no overlay, no action (V5).
6. Never replay an action that may have partially run (V6).
7. Never touch owner data, tabs, or sessions outside the task (V7).
8. Never push personal information to GitHub (V8).
9. Never run two live drivers at once (G-SINGLE-LIVE, one runner, one session).
10. Never relaunch anything blindly after a compositor crash; stop and report (V7 of F1 council 2).
11. Never use ydotool (standing ban, in every brief).
12. Never let a respawn or retry loop run unattended overnight; one retry, then stop and log.

## Safety verdict on the three methods
- Class A method is APPROVED TO PROCEED only under preconditions 1-8, single
  operator, F3 sign-off first, crash contingency in the brief verbatim. Without
  any one precondition, it is NOT approved.
- Class B method is APPROVED TO PROCEED for the harmless rehearsal task only,
  after F3 sign-off, with the pill verified in a fresh observe before the first
  click, and the fallback predicate treated as a safety gate. It is NOT approved
  for any real page until the rehearsal passes.
- Class C1 method (watchdog proof + R3 gate) is APPROVED TO PROCEED for the
  single-kill respawn proof only. The R3 gate implementation needs its own
  council + redteam before it lands, because a too-strict gate breaks working
  sessions.
- Class C2 method (nested measurement only) is APPROVED TO PROCEED, because it
  never touches the live compositor. Any live load to chase the flicker is
  VETOED.
