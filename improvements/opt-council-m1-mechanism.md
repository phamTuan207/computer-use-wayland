# Council OPT-M1, Voice 1: MECHANISM
# Classes (A) session/guardian startup failure, (B) silence / slow first action,
# (C) overlay never shows / flicker. Repo ~/workspace/computer-use-wayland,
# branch todolist-push. Evidence contract: every claim carries file:line or a
# runnable-evidence citation. No em/en dashes in this file.

## Method of this voice
Read the code, not the summaries. Each failing point below was read in the VM
repo at the cited lines. Where a claim comes from a log rather than code read
here, it is marked LOG and the log file is cited. OPT-SRC crawl file
(improvements/opt-crawl-src-20261121.md) did not exist when this council started
(checked 22:50 +07), so there is no OPT-SRC position to agree or disagree with
yet. That gap is recorded in the council log.

## Class A: session/guardian startup failure

### A0. User-visible symptom
`computer-use session` dies in 0.46s with
`{"ok": false, "error": "session guardian startup failed"}`, no pill ever
appears. LOG: improvements/worker-f1-guardian-fix-log.md, 22:19 test start;
improvements/worker-f2-silence-fix-log.md section 1, session attempt ~22:15:00.

### A1. First failing point: check_guard throws on a non-JSON reply
File: scripts/cursor_theme.py, function guard_reply, lines 99-113 (after F1 fix).
Function check_guard, lines 115-117, runs `hyprctl cu-cursor status` and passes
raw stdout to guard_reply, which does json.loads(raw). Before the F1 fix this
was lines 99-108 with an unconditional json.loads.
Mechanism: when the cursor-guard plugin is not loaded, Hyprland answers the
custom dispatcher with the plain string `unknown request` and exit code 0.
command() (cursor_theme.py lines 52-53) uses subprocess.check_output, which
raises only on a non-zero exit, so no subprocess exception fires. Instead
json.loads("unknown request") throws json.decoder.JSONDecodeError.
Live proof, LOG: F1 step probe 22:19, check_guard THROW in 0.004s with
traceback; live `hyprctl cu-cursor status` returns `unknown request`, rc 0;
`hyprctl -j plugin list` shows hyprbars only.
Upstream corroboration, LOG (F1 crawl): hyprglass docs state a paused hyprglass
has no `hyprctl hyprglass` command and answers `unknown request`; cjennings
dotfiles note that under a Lua config `hyprctl keyword` answers `unknown
request` and exits 0. Same bug class.
What must change: already changed by F1 (guard_reply catches JSONDecodeError
and raises a named RuntimeError with the remedy). Remaining gaps, LOG:
council 1 A3 says guard_reply misses UnicodeDecodeError on the socket path
(verified live on the VM); redteam R4 says a truncated JSON reply is
misdiagnosed as a missing backend. Both are real code gaps at the same lines.

### A2. Second failing point: supervise swallows the cause
File: scripts/cursor_session.py, function supervise, lines 210-260 (after F1 fix).
The guardian is spawned with stdout piped and stderr piped. supervise waits
15s with select.select for the string `ready` on the guardian stdout
(lines 245-248). If the guardian dies early, the old code raised the bare
RuntimeError('session guardian startup failed') and the CLI printed only that
(cu.py session branch). The guardian real cause was never in the envelope.
What must change: already changed by F1 (drain thread into a deque, tee to
stderr, tail appended to the error). Remaining gaps, LOG: council 1 A1 says a
drain race remains (guard_errors is read the instant select reports, with no
wait for guardian exit and no join of the drain thread); council 1 A2 says the
driver registration failure at line 260 carries no detail; redteam R5 says the
drain thread dies silently on non-UTF8 stderr; redteam R6 says no drain settle
before composing the detail; redteam R7 says deque maxlen 32 plus detail[-1200:]
can drop the root cause. All five are real code gaps at the same function.

### A3. Third failing point: Guard.__init__ would throw next
File: scripts/cursor_theme.py, class Guard, __init__. Even if check_guard
passed, Guard.__init__ requires the socket directory
/run/user/1000/agent-computer-use/ with cursor-guard.sock. LOG: that directory
does not exist at all on the live machine, because the plugin owns the socket
and the plugin is not loaded. So the failure has two successive throws behind
the same opaque error, and fixing only A1 would surface A3 next. Any fix that
only patches the JSON parse without loading the plugin still leaves sessions dead.

### A4. Runtime state: neither plugin is loaded, and nothing reloads them
LOG: live plugin list is hyprbars only; no `cu-cursor` or `cursor-guard` lines
in hyprland.conf or conf.d; live Hyprland PID 1515 alive since 03:05:59 on
2026-11-21; broker sessions worked before 03:05 and none proven after. Plugin
loads are first-load manual steps only. Hyprland wiki (LOG, F1 crawl): plugins
are NOT persistent across restarts unless the config reloads them
(`hyprpm reload` in autostart). Our repo loads plugins only via first-load
scripts, so every compositor restart silently unloads both plugins.

### A5. Login loader failed: manifest_validation
File: scripts/visuals.py, function _login, lines 258-274. The check is
`if manifest['profile_sha256'] != hashlib.sha256(OPTICS.read_bytes()).hexdigest():
raise ValueError('profile does not match the pinned optics source')`,
with OPTICS = native/hyprglass-local-optics.lua and manifest =
native/visuals.json, both read from the LAPTOP repo copy because
native/visuals-login.lua runs that copy.
LOG: the loader DID run at this compositor login (spawn 15:17:29 +07, 4s after
compositor start 15:17:25, inside the 30s fresh-login window) but failed at
stage manifest_validation, instance 11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947,
record time 1795249050, in ~/.cache/agent-computer-use/logs/visuals.jsonl,
corroborated by visuals-stderr.log. The previous instance failed the same way;
the one before (1795086072) SUCCEEDED (glass 199153ae, guard 06712eaf).
The loader failure is silent because visuals-login.lua fires visuals.py via
hl.exec_cmd with stdout/stderr to /dev/null and the exit code never recorded
(LOG, F1 citing live-test-log.md:464 and :2601).

### A6. Root drift: laptop repo stale vs setup-published state
LOG (F1, verified on disk and in loader logs): laptop repo at detached HEAD
56f5af4 (predates blur-0.15 commit b2afcd1, Nov 20 20:40). Laptop optics sha256
545455d3 = commit 09a8df7 (blur 0.0). Laptop manifest profile_sha256 674441ea.
Installed tree optics sha256 9a151634 = commit b2afcd1 (blur 0.15), manifest
pins profile_sha256 9a151634 + library hyprglass-199153ae. The b2afcd1 commit
message admits no visuals.json manifest existed in that checkout, so no pin
was refreshed there; the sync re-pinned only the INSTALLED manifest, never the
laptop-repo manifest (a gitignored local file), and never updated the
laptop-repo optics file.
Correction pending, LOG (council 1 A5, UNVERIFIED by this council): the old pin
674441ea is claimed to match commit d27ad0a (blur 0.10), which would make the
drift two different stale commits (optics from 09a8df7 vs manifest pin from
d27ad0a), not one unknown pin. This council did not verify that sha; F1 must
verify `git show d27ad0a:native/hyprglass-local-optics.lua | sha256sum` on the
laptop repo before the log is corrected. The repair is correct either way.
What must change: repair the drift on the laptop-local files (F1 plan A, done
22:37, proven by the loader now failing at fresh_login_gate instead of
manifest_validation), then make the repair durable: a re-pin check in
sync-installed/setup (redteam R1/R2, council 1 A6), because the next optics
change repeats the exact incident otherwise.

### A7. Activation gate in activate-cursor-guard.py
LOG: activate-cursor-guard.py is the first-load path but REFUSES unless
indicator.liquid_available(env) is true, i.e. hyprglass loaded + active +
version 1.1.1-cu.1 + versionCheck match. File: scripts/indicator.py,
liquid_available, line 242. So the guard cannot load until glass loads first,
and glass loads via activate-glass.py. Order is forced: glass, then guard.
Both pinned .so files are loadable NOW, LOG: pinned glass 199153ae ldd
resolves libaquamarine.so.15 + libhyprgraphics.so.5 (0 not found);
cursor-guard 06712eaf full ldd 0 not found; live abiHash matches the manifest
abi. The Y6c "dead ABI" finding was about vendor-dir/backup binaries, not
these pinned builds.

### A8. What the A fix must contain, in code terms
1. scripts/cursor_theme.py guard_reply: already names the missing backend; add
   the A3 UnicodeDecodeError catch and the R4 truncated-JSON distinction.
2. scripts/cursor_session.py supervise: already pipes and tees guardian stderr;
   add the A1 drain settle (wait for guardian exit + join drain thread), the A2
   detail on driver registration failure, the R5 errors='replace' drain, and
   the R7 larger deque/tail.
3. Laptop-local drift repair (done) plus a durable re-pin check in
   sync-installed/setup (not done, tracked follow-up).
4. Live activation: activate-glass.py then activate-cursor-guard.py with the
   manifest abi and profile-sha256 9a151634, under F1 council 2 preconditions 1-8.
5. Session gate on hyprglass active (redteam R3): check_guard only checks
   cu-cursor today; a paused or crashed glass with a loaded guard starts a
   session with no pill, which is class C1 returning silently.

## Class B: silence / slow first action

### B0. Measured timeline, LOG
F2 log section 1: owner order 22:11:30, owner reports nothing seen 22:16:07,
direct Pointer click succeeds 22:17 in 0.31s at cursor 2598,1174, no miss,
Welcome tab selected, NO overlay. Order to first click nearly 5 minutes; the
click itself 0.31s. Breakdown: ~40s Marionette retry, ~2 min cu.py/session
research + observe + view, ~1 min session attempt + diagnostics, ~1.5 min
guardian/desktop_act source reads, ~0.5 min Pointer read + click. Diagnosis
phases were ~4.5 min of the 5.5 min, all silent, no visible action.

### B1. Failing point 1: no structural fast path, research-first default loop
There is no single command that does overlay-on + move first and diagnoses
after. The agent must remember to be fast, and on 2026-11-21 22:11 it did not.
File evidence: scripts/cu.py act() at line 2595 calls require_session() at
line 2599, which raises unless CU_SESSION_TOKEN is set. The session branch
(line 2368) runs cursor_session.supervise, which waits up to 15s for `ready`.
The act chain is three serial failure points before any visible action:
observe (max age 120s, OBSERVATION_MAX_AGE line 48) -> session (guardian, up
to 15s) -> act (requires session + fresh observation). No fast path exists in
the code. Fix direction: make the fast path the DEFAULT command, so speed is
structural, not a decision (F2 R1, Lauren Tan rule: a repeated mistake becomes
a deterministic rule, never a reminder).

### B2. Failing point 2: the overlay exists only inside a live session
The pill exists only inside a live session: the guardian creates
indicator.Native and the session driver shows it. No session, no pill. The
direct Pointer path never touches the overlay at all. File evidence:
scripts/cu.py require_session lines 2599-2602; scripts/overlay.py is the
central overlay control (reference-counted holders, session-aware forwarding,
daemon takeover if the session dies while holders remain), but nothing in the
Pointer path calls it. Consequence, proven 22:17: any session failure means an
invisible run. The 22:17 click had no overlay for exactly this reason.
What must change: overlay acquire is a PRECONDITION of any pointer action, on
BOTH paths, enforced in code. If the overlay cannot be shown, the action is
REFUSED with a clear error, never executed invisibly (F2 R3, precedent:
dsh-computer-use-win tool-enforced overlay gate, F2 crawl).

### B3. Failing point 3: session start has no deadline and no fallback
supervise waits 15s for `ready` and then fails the whole run. There is no
bounded attempt and no degraded path. What must change: scripts/first_action.py
(F2, new file, ~300 lines): acquire_overlay first (lines 68-90, refuses loudly
when the pill cannot be shown), session attempt with a hard 20s deadline
(attempt_session lines 112-124, process-group kill on timeout), fallback to
the same desktop_act the session path uses ONLY on a session-START failure
(is_session_start_failure lines 153-176: true only when no action can have
run, so a fallback is safe; false on any act failure, timeout with a live
session, or partial run, so actions are never replayed blind), verify pointer
position after each click within 3px, release the overlay, return a JSON
envelope with path taken and timings (order -> overlay-on, order -> first
move, order -> first click) plus a JSONL timing log. Wired as `act-now` in
scripts/cu.py (subparser + dispatch). Tests: tests/test_first_action.py, 21
tests, 21/21 on the VM.

### B4. Failing point 4: the agent loop itself is the bottleneck, not the tools
LOG (F2 crawl): mean observation-to-action gap 6.51s on real OSWorld workloads;
cua-speedrun found Fast I/O (2-28ms screenshots) made the agent SLOWER because
screenshots arrived before the redraw, so desktop_act settle/verify steps must
stay. The tools are already fast (DOM read 3-28ms, click 100% in the 1.2.2
comparison); the cost sits in the think-observe loop (G13: 87.8% of task time).
What must change: nothing in the tools for class B; the fix is the act-now
default path plus the <30s order-to-first-visible-action target plus the
no-gap-over-60s rule, measured on every live run. Owner correction 22:21:
narration before each step is NOT needed; the requirements are FAST,
CONTINUOUS, OVERLAY VISIBLE, in that order.

### B5. Dependency: B cannot be proven until A is green
LOG (todolist gate G-F1-BEFORE-F2): measure F2 only when F1 is green, because
F2 cannot be measured while the session dies in 0.46s. The F2 rehearsal is
gated on F3 Zen restore (F3 log 22:48: Marionette slot FIXED, 67 tabs listed,
click tab PASS 29ms 1.0px) and on the ZT-00 gate. The rehearsal design is a
COMBINED test (DOM + CLI + mouse + keyboard in one task) set by an independent
agent (owner test rule 22:23). Until the rehearsal runs, act-now is code-proven
(21/21 VM tests) but not live-proven.

## Class C: overlay never shows / flicker

### C0. Two distinct phenomena, one label
The error file conflates two things under "overlay". They have different
mechanisms and different fixes, and treating them as one problem is itself an
error. C1: overlay never shows (I12, 15:28 20/11). C2: overlay flickers
continuously (H1/I9/I10, evening 20/11). Voice 1 splits them.

### C1. Overlay never shows: two mechanisms
Mechanism C1a: the session is dead, so the pill is never created. This is
class A. LOG (I12): worker alive, broker and relay running, overlay gone;
"the session may have dropped or the pill was turned off without the worker
knowing". Fix is the class A fix.
Mechanism C1b: the session is alive but the glass is paused or crashed.
LOG (redteam R3): the session never gates on hyprglass. check_guard only
checks cu-cursor. liquid_available is consulted only by activation, and
Native fails closed on missing glass only when the require-liquid marker
exists, which is gitignored and absent from the installed tree (verified).
So a paused or crashed glass plus a loaded guard starts a session with no
pill, and the original symptom returns silently with a successful session.
What must change: gate the session on hyprglass active (or publish the
require-liquid marker), and keep the watchdog respawn from todolist 2.2.4:
Daemon._ensure_native() respawns a dead native indicator while holders remain
+ retries label/show once; unit tests test_daemon_respawns_dead_native and
test_daemon_keeps_live_native pass. Live respawn proof is still owed (needs a
killed indicator during a hold).
Overlay control file: scripts/overlay.py, reference-counted holders in
~/.cache/agent-computer-use/overlay/ (0700), daemon takeover when the session
dies while holders remain. LOG (F2 22:25): holders.json was empty, daemon.log
last entry 15:36:59 clean stop, no overlay daemon running, no pill.

### C2. Flicker: what is proven, what is not
Proven facts, LOG (todolist 2.2.1, Worker G E2 live): the fixed indicator does
NOT repaint at idle (0 idle paints in 122 one-second windows, 32/32 frames
pill pixel-identical, 60s idle with no events). No in-repo 10Hz driver exists
(redteam worker4 proved: exactly 2 visibility toggles per observe, 0 while
idle). The flicker work log file itself was NOT found in this VM repo, so the
numbers above are cited as todolist-recorded, not re-verified by this council.
Proven false, LOG (todolist 2.2.5): the "screenshots cause flicker" claim is
false by code and by live measurement; Muse observed only every 10-30s, which
cannot cause ~10Hz flicker (I20 retraction, I9 19:02 admission).
Most likely remaining cause, LOG (todolist 2.2.1): a compositor/plugin repaint
loop triggered by an animated backdrop (H-E) in LIQUID mode, which could not be
tested live because hyprglass is not loaded now. E1 per-event logging was added
so any recurrence is captured.
What is NOT proven: the flicker rate (~10Hz) was only a user estimate (I10),
never measured; the trigger was never observed directly; the animated-backdrop
hypothesis was never tested live. Todolist 2.2.3 is BLOCKED: the test needs
loading a backup plugin into the live compositor, which risks crashing
Hyprland while the owner works. Owner decision 18:24: option C, nested Hyprland
(isolated), try C first, then A or D, never B (add to hyprland.conf + reboot).
Y6c NO VERDICT, Y6d launcher v3 + C2 ALL PASS, Y6e rebuild + nested LOAD TEST
PASS 21:57 (hyprglass active true, versionCheck match, live 1515 untouched);
pill measurement still UNPROVEN (Y6e).
What must change: do NOT chase C2 on the live compositor. Measure it only in
the nested Hyprland (option C) with E1 per-event logging, animated backdrop on,
LIQUID mode, and count repaints per second. If the nested test shows 0 repaints
under animated LIQUID backdrop, the compositor-loop hypothesis is falsified
and the investigation restarts from the E1 logs. The pill blur increase (0.0 to
0.15, todolist 4.1, owner order after reboot 21/11 02:15) is a separate taste
change, not a flicker fix, and must not be cited as one.

## Cross-class mechanism summary
- A is a load-order failure: plugins unload at compositor restart, the login
  loader fails silently on a stale pin, the session gate throws an opaque error.
- B is a path failure: no fast path exists, the overlay lives only inside the
  session, the session has no deadline and no fallback.
- C1 is A returning through a second door (glass down, guard up) plus a missing
  watchdog proof. C2 is an unmeasured compositor-side repaint loop, not an
  indicator bug, and the indicator is already proven innocent at idle.
- The three classes share one spine (session health + overlay visibility) but
  need three different proofs: A needs a live session start with pill in a
  fresh observe; B needs a timed rehearsal under 30s; C2 needs a nested
  compositor measurement. No single live run proves all three.
