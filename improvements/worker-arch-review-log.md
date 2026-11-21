# Worker ARCH-REVIEW: independent first-principles architecture review
# Start: 2026-11-22 06:03 +07. Scope: scripts/cu.py (3063 lines), scripts/first_action.py (719),
# session/overlay model, observe/act split, failure record (todolist + error file).
# Method: read the code, re-derived every claim from file/line or measured logs.
# Goal bar: one vision drives max actions, accuracy >=90%, minimal total wall time.
# Verdict: the architecture is inverted. Pixels are the primary path; structured
# state (DOM/a11y/compositor IPC) is a bolt-on. The evidence proves the inverse
# is correct. Rewrite, do not patch.

## 0. The job, from first principles

An agent driving a desktop needs exactly three things: (1) know the target
state, (2) change it, (3) verify the change. There are exactly three sources
of state: the application's own structured model (DOM, accessibility tree,
API), the compositor's window model (Hyprland IPC), and pixels. Structured
state is exact, cheap (milliseconds), and verifiable. Pixels are lossy, slow
(seconds plus agent vision time), and the agent's reading of them is the
proven error source. Therefore the architecture must be: structured-first,
pixels-last. The current architecture is the inverse: the primary path is
screenshots plus a virtual mouse, with DOM/a11y as optional hooks.

Measured proof of the inversion:
- Vision hit rate 17/29 = 58.6%; pointer error 0.5-0.9px once grounded (E2).
  DOM rects are exact. (todolist 2.1.1, 2.1.2)
- DOM grounding, clone2 batch 7: one-shot harvest got all 66 element
  coordinates (Marionette median 0.030s); one snapshot drove 5 clicks, all
  5 hit; verify by one DOM read 0.005-0.015s. (summary of batch 7)
- Real task DOM-first (Worker J): 0.64s total, 0 misses, 15 steps; upload
  zip 11ms vs a 70-minute blocker. (todolist 1.2.3, 5.1)
- firefox-mcp click 33ms verified; Selenium 11/11 steps in 0.278s;
  zen-mcp 2-20ms. (todolist 1.1.2, 1.1.3, 1.1.4)
- Think-observe-think loop is 87.8% of task time. (todolist 2.1.9, G13)
- G30: 5 attempts, 0 messages sent, clicks 64px and 75px above the real
  input field. G31: 45px eyeball error, caught only by the grounding tool.
- F2b order-to-overlay 12.262s breaks down as: SSH/scp dispatch 11.620s
  (95%), fresh observe 0.233s, Python startup 0.060s, overlay acquire
  0.349s. The mechanism is fast; the transport is the cost.
  (improvements/worker-f2b-live-session-log.md)
- F2b honesty number: spawn-to-overlay 6m56s of agent think/setup time.
  The 30s target measures the mechanism, not the loop. The loop is the
  problem. (same log)

The benchmark script itself concedes the point. tests/two_vision_bench.py
(868 lines, origin/main) states: "VISION 1 here is a DOM harvest, NOT a
screenshot". harvest_window() is one driver.execute_script(HARVEST_JS);
clicks go through Selenium ActionBuilder, typing through send_keys,
verification through a DOM bubble gate (V12). The script that is supposed
to prove "one vision drives many actions" is implemented as DOM-first.
The vision step is vestigial. The honest end state is 0 visions for
structured targets, with vision kept only for genuinely visual checks.

## 1. Findings

### F1. The screenshot is the primary sensor, and it is the worst sensor.
cu.py observe() (line 920) and observe_screen() (line 974) shell out to
grim, decode PPM via PIL, LANCZOS-resize, JPEG-encode at q90 4:4:4,
re-decode the JPEG to hash stored pixels, and write a .jpg plus a .json
to disk. Every observation is a file. The agent then reads coordinates
off the file by eye. That reading is the single largest error source in
the whole failure record (G30, G31, vision 58.6%). No amount of
verification downstream fixes a sensor that misreads 4 times in 10.
The correct sensor for a chat input is the element rect (exact, 0.030s),
not a JPEG.

### F2. The coordinate model has four systems and converts at every step.
Image pixels -> region origin -> monitor coordinates -> normalized
0-1000000 -> virtual pointer (cu.py image_point line 1000, move() line
1770). Each conversion is a bug surface: F2b-1 (act converts with the
observation REGION origin, not monitor_box), C12 (window-relative vs
screen-relative origin, probe cd89597), the 1.10x vision scale error
(todolist 2.1.1), G30/G31. The DOM model has ONE system: element rects
in CSS px, converted once at the driver edge. Four systems exist because
the pixel path needs them; the structured path needs one.

### F3. desktop_act re-queries the world for every action.
desktop_act (cu.py:1619-2199, ~580 lines) calls guard() before every
group and inside every action. guard() (line 1691) fetches the full
clients list, the full monitors list, and the active window over the
Hyprland socket, and parses all three JSON blobs. move() (line 1770)
does two cursorpos round trips per move. A click costs roughly 8-10
socket round trips plus JSON parses of full compositor state. hypr()
(line 520) correctly uses the Unix socket instead of fork/exec, but the
pattern is still poll-the-world-per-action. A driver that holds state
(window bounds, monitor layout) and subscribes to compositor events
(Hyprland socket2) would pay this cost once, not per action.

### F4. The batch does up to five screen captures.
desktop_act takes a pre-batch re-observe plus a settle retry (lines
1733-1749), then an after-capture plus a settle retry (lines 2083-2091).
act-now adds its own after screen capture (first_action.py, end of
run()). That is up to 5 grim captures plus 5 PIL pipelines per batch,
to answer a question a compositor event subscription or a DOM read
answers in milliseconds. The pre-batch re-observe exists because the
observation may be stale (120s window); the staleness exists because
observations are files shipped over SSH. The captures are a tax on the
file-based design, not on the task.

### F5. The session supervisor tree is machinery for a problem the
### fallback path does not have.
cursor_session.py supervise() (line 228) spawns a guard process and a
driver process, connects them with pipes, a gate byte ('go'), a UUID
token, select() timeouts, a drain thread, and snapshot recovery. The
entire F1 failure cluster (4 layers: JSONDecodeError on hyprctl output,
guard plugin not loaded, fresh-login loader failure, stale repo) is
session machinery. Yet the act-now fallback path runs the SAME
desktop_act with a directly opened Pointer and NO session, and it works.
The session's real jobs are: (a) a named, killable scope for one task,
(b) cancel/stop, (c) the session pill label. All three can be done by
the driver plus a state file plus a cancel latch. The supervisor tree
should not exist.

### F6. The overlay daemon is a server for a boolean plus a label.
overlay.py (613 lines) is a Unix-socket server with holder accounting,
a monitor thread, a native indicator subprocess, holder leak pruning,
and a "sync vs status" distinction. The pill's job is to tell the human
an agent is acting. But observe() HIDES the pill by design
(capture_clean, cu.py:947-948, 985-986), so the agent's own screenshots
never contain it: the observation path and the status path fight each
other, and pill verification needs raw grim. A compositor plugin that
shows the indicator whenever the virtual device is active, or a pill
owned by the driver process itself, removes a whole server, its socket
protocol, and the "overlay unavailable" refusal class. The visibility
must stay; the daemon must not.

### F7. The agent loop runs over one-shot SSH, and SSH is 95% of the cost.
F2b proves it: 11.620s of 12.262s is SSH/scp dispatch. Connections die
at ~30s (G6), so long jobs must be detached and polled. A persistent
relay exists (session_remote.py Broker, 1601 lines) but the observed
practice is still one-shot SSH per command. Either the persistent
channel becomes the ONLY transport, or the one-shot path is the tax
forever. Note also that session_remote.py carries git-head-at-start
checks and env-steal test proofs: test scaffolding inside production
transport code. A transport should transport.

### F8. Observations and actions are files shipped over SSH.
Every step is: write JSON, scp to laptop, run, write JPEG+JSON, scp
back, read. The 120s freshness window, the G28 substitution refusal,
the stale-observation class, and the path confusion all exist because
state moves as files. The persistent session-driver (session_driver.py,
180 lines, JSON-lines over stdio, runs cu.main() in-process per
command) already exists, and Codex's demo proved it works: one
persistent driver, one action per call, fresh observation each step,
verify after every step. The one-shot path should be the fallback, not
the default. code_exec.py (880 lines, Pick 1 winner) already provides
the in-process program model with observe/act/dom_observe/dom_act/
dom_assert and an allowlisted API: the shape of the rewrite already
exists inside the repo.

### F9. The act-now after-image is defective by construction.
Independent investigation (5f5a2fd) proved it: first_action.py always
captures the envelope `after` with cu.observe_screen (max_width 1920),
regardless of input scope, overwriting desktop_act's scope-matching
after-capture (cu.py:2083-2091). EVERY act-now after-image is
screen-scoped, so reusing ANY of them for a key/type step ALWAYS fails.
CL2-MSG's after-image was also screen-scoped; the trap just did not
bite. This is not a bug in a feature; it is a feature that cannot work
as documented. Either the after-capture matches the input scope, or the
`after` field stops being offered as an observation and becomes
verification-only evidence.

### F10. Type verification by pixel band is necessary, not sufficient,
### by its own admission.
desktop_act's band check (cu.py, after-capture section) states plainly
that a caret or focus ring alone also changes a band. The sufficient
check is the DOM value read, which already exists as the type_check
hook. For structured targets the pixel band should not exist at all;
for unstructured targets it is the only check and should be labeled
weak, not reported as verification.

## 2. What should not exist at all

1. Screenshots as the primary grounding mechanism for structured
   targets. Replace with DOM/a11y harvest. (Evidence: F1, benchmark
   script.)
2. The session supervisor tree (guard + driver + gate + token +
   snapshot recovery). Replace with driver task scope + cancel file.
   (Evidence: F5, F1 cluster.)
3. The overlay daemon socket server + holder accounting. Replace with
   a driver-owned pill or a compositor-plugin indicator. Keep the
   visibility, delete the server. (Evidence: F6.)
4. The one-shot SSH-per-command agent loop. Replace with the persistent
   Broker channel as the only transport. (Evidence: F7, 95% cost.)
5. File-based observation/action IPC (JSON + JPEG + scp per step).
   Replace with in-process driver calls (session-driver already
   exists). (Evidence: F8.)
6. The act-now `after` image as a chainable observation. Either fix
   its scope or demote it to verification-only evidence. (Evidence: F9.)
7. Pixel-band type verification for structured targets. Replace with
   DOM value assertions. (Evidence: F10.)

## 3. What was wrong from the start

- The observe/act split was designed around the agent's eyes, not the
  application's model. The agent was given a camera when the application
  already had a nervous system (DOM/a11y). Every error in G30/G31 and
  the 58.6% vision rate flows from this one choice.
- The "session" was designed as a process tree instead of a state
  machine. Process trees need supervision; state machines need a file.
- The pill was designed as a separate server instead of a property of
  the acting process. Servers need protocols; properties need a flag.
- The transport was designed as one-shot remote commands instead of a
  persistent driver connection. One-shot commands pay connection setup
  per action; a driver pays it once.
- The coordinate model was designed around the image instead of the
  element. Images have four coordinate systems; elements have one.

## 4. The rewrite (concrete breakthrough direction)

Layer 0, new primary: a persistent driver daemon on the laptop. One
process, holds state (window bounds, monitor layout, DOM/a11y sessions,
compositor event subscription). The agent talks to it over one
persistent channel (the Broker shape, slimmed: no git-head checks, no
env-steal proofs). The driver exposes three calls: snapshot (structured
state: DOM + a11y + window list, one call), execute (a plan: a list of
structured actions with refs, not pixels), verify (structured
assertions). No screenshots in the loop at all for structured targets.
No SSH per command; SSH only establishes the channel.

Layer 1, demoted pixels: the current desktop_act path, kept ONLY for
targets with no structured interface, with the pixel-band verification
honestly labeled weak, and with the after-image scope bug fixed (F9).

Delete: the session supervisor tree, the overlay daemon server, the
one-shot SSH loop, file-based observation/action IPC. Redesign: the
coordinate model to one system (CSS px element rects, converted once at
the driver edge). Split desktop_act (~580 lines doing validation +
guards + captures + verification) into plan validation, structured
execution, and pixel-fallback execution.

What already exists as the prototype of the rewrite: code_exec.py
(in-process program model, Pick 1 winner, merged 453adc4),
session_driver.py (persistent JSON-lines driver, proven by the Codex
demo), dom_act.py / zen_dom.py / a11y.py (structured grounding),
tests/two_vision_bench.py (DOM harvest + WebDriver execution + DOM
gate). The rewrite is mostly assembly and deletion, not invention.

Acceptance test for the rewrite: a 0-vision live benchmark. Same shape
as the 2-vision benchmark but against the REAL clone chats on ws2 (not
the local fixture in headless Firefox): DOM harvest, plan, execute,
DOM verify, zero screenshots in the loop, accuracy >=90%, total wall
time measured end to end including transport. Note the current benchmark
runs against a local fixture, so it is a fixture proof, not a live
proof; the council round-2 note of a benchmark target gap (C3R2 G5)
says the same. Vision is used only for a final visual sanity check if
the user asks for one.

## 5. Honest limits (what stays)

- The pixel path cannot be deleted entirely. Native apps without a11y
  (games, some Electron apps, canvas) still need it. The claim is
  about the DEFAULT, not about deleting the fallback.
- The pill visibility must stay: the user must see when an agent acts.
  The proposal deletes the daemon server, not the visibility.
- The single-runner lock must stay (G-SINGLE-LIVE, 1 live runner,
  1 BiDi/Marionette session total). The driver holds it as a task lock
  instead of the guardian holding it as a process tree.
- The rewrite is large: session supervisor, overlay daemon, transport,
  and the observe/act split all change. That is the point of this
  review: the evidence says patching around these designs has already
  cost a day of councils and redteams on AMEND3's 13 breaking findings.
  A rewrite of the four pieces above is smaller than another round of
  patching them.

## 6. Log

- 06:03 +07 (T+0m): start. Read first_action.py (719 lines, full),
  todolist (215 lines, full), cu.py function map, error file headings.
- 06:05 +07 (T+2m): read desktop_act (cu.py:1619-2199) and observe /
  observe_screen / save_observation (cu.py:834-1000).
- 06:07 +07 (T+4m): read cursor_session.py supervise (line 228), overlay
  model, session_remote.py Broker structure, code_exec.py API,
  session_driver.py shape.
- 06:09 +07 (T+6m): read tests/two_vision_bench.py from origin/main
  (868 lines, harvest/click/send/verify flow); confirmed VISION 1 is a
  DOM harvest, not a screenshot.
- 06:10 +07 (T+7m): re-checked measured numbers against logs: F2b
  12.262s breakdown, DOM grounding 66 rects / 5 clicks, vision 58.6%,
  real-task 0.64s DOM-first.
- 06:12 +07 (T+9m): wrote this log. Next: commit with explicit
  pathspec to todolist-push, verify with git ls-remote, report.
