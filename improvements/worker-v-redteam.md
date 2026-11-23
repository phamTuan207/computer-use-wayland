# Redteam attack report: Vietnamese typing fixes (Worker T proposal)
# Worker V (redteam), 21/11/2026. All times wall-clock Asia/Ho_Chi_Minh.
# Target: improvements/worker-t-vietnamese-typing-diagnosis.md, commit 029cb9b.
# Method: read the live code, re-ran read-only checks on the laptop, attacked
# each proposal (Fix 1 retroactively, Fix 2, 3, 4, 5). No edits, no restarts,
# no kills. Live checks ran 17:25-17:28 on 21/11/2026.
# Rule: no em dash or en dash anywhere in this file.

## Verdict up front

- Fix 1 (lotus-autostart.sh): SURVIVES as harmless, but the applied fix is
  NOT what was proposed, and its verification is vacuous. Correct the record,
  do not claim it fixes anything at login.
- Fix 2a (retry SetCurrentIM in indicator.py): DOES NOT SURVIVE as specified.
  The 2s retry budget is an order of magnitude shorter than the observed
  21s stall, and retrying inside the single-threaded loop lengthens the
  exact block that causes presses to pile up. Redesign (retain pending with
  a TTL, cover all three clearing sites, cap the per-tick dbus budget) or drop.
- Fix 2b (wrapper polls fcitx5-remote -n, falls back to fcitx5-remote -t):
  DOES NOT SURVIVE as specified. The fallback races the stalled switch and
  can land the user on the opposite method. Redesign (explicit target with
  -s, flock serialization, timeout on every call, bind from user config) or drop.
- Fix 3 (30s watchdog probe, restart indicator.py then fcitx5): DOES NOT
  SURVIVE as specified. The probe itself toggles the user's live input
  method twice every 30s, has no backoff or circuit breaker, and has a
  missing-env false-positive path that would restart fcitx5 every 30s
  forever. Reject as specified.
- Fix 4 (ActiveByDefault=True experiment): DOES NOT SURVIVE as specified.
  It treats a symptom Worker T did not reproduce, its password-field safety
  claim is unverified, and its harm cases (code typing, passwords, URL bar)
  are untested. Reject until H2 is reproduced and the harm cases pass.
- Fix 5 (logging-only stall monitor): DOES NOT SURVIVE as specified. The
  proposed probe is not logging-only: it cycles the input method. Redesign
  as a truly read-only latency monitor with per-component timings, or drop.
- Scope gap across all five: NOTHING proposes a fix for the wtype
  (agent typing) stall, which was 5 consecutive hangs over about 3 minutes
  in the observed window. All five fixes target Super I bookkeeping. The
  shared-path stall that froze both wtype and dbus has no fix proposed.

## Corrections to Worker T's diagnosis (the record, before the attacks)

C1. Misattribution of the pending-clearing site. T writes that "in
indicator.py refresh(), if the fcitx5 dbus call fails or times out ... the
code catches GLib.Error and CLEARS pending silently". Indicator.refresh()
(lines 108-119) does not catch anything. The clearing happens in THREE
places, and a patch that touches only refresh() misses two of them:
- watch.refresh() wrapper, lines 225-232: on GLib.Error it sets
  indicator.pending = "" AND indicator.last = "".
- Indicator.refresh(), line 112: if self.pending is not in the methods
  returned by snapshot(), pending is cleared. A transient snapshot that
  returns a partial method list eats the press the same way.
- command(), lines 289-302: on any exception from select_next() (GLib.Error,
  OSError, ValueError, subprocess.CalledProcessError) it sets
  indicator.pending = "".
The mechanism T describes is real, but the patch target is wrong. Any Fix 2a
patch must cover all three sites, or better, centralize pending clearing.

C2. The 5s restart claim is confirmed. /usr/share/omarchy/shell/Commons/
InputMethodState.qml: Process onExited sets root.state = ({}) and starts a
Timer with interval 5000 that sets watcher.running = true. So killing
indicator.py blanks the bar widget for 5s and loses pending and last.

C3. The "cycle returns ok in 7ms" claim is confirmed and is worse than T
states. InputMethodState.qml cycle(back) returns false if the watcher is
not running, else writes "cycle\n" to stdin and returns true.
omarchy-input-method only checks that the reply is "ok". "ok" means the
bytes entered the pipe, not that any switch happened or will happen.

C4. T's acceptance test 3 is wrong on its face. It says: kill indicator.py,
press Super I within the 5s restart window, confirm the switch still lands
"via the Fix 2 retry". During that window cycle() returns false, nothing is
queued, and there is no indicator.py process for Fix 2a to retry inside.
The press is gone. Only a path that bypasses the dead reader (Fix 2b's
direct fcitx5-remote call) can cover that window, and Fix 2a cannot.

C5. The applied Fix 1 deviates from the proposal. See attack F1-2 below.

## Evidence base (live, read-only, 21/11/2026 17:25-17:28)

- indicator.py: /usr/share/omarchy/default/input-methods/indicator.py,
  owned by omarchy-settings 4.5.0-3 (pacman -Qo). Bind file
  /usr/share/omarchy/default/hypr/bindings/input-method.lua, same package.
- call(), lines 17-20: bus.call_sync(..., Gio.DBusCallFlags.NO_AUTO_START,
  1000, ...). Every dbus call has a 1000ms timeout and never autostarts fcitx5.
- schedule(), lines 251-261: 50ms timer while pending, 500ms while polling,
  2000ms while failed.
- select_next(), line 87: runs `hyprctl -j devices` via subprocess.run with
  check=True and NO timeout, before any dbus call. layout_switches() also
  runs `hyprctl switchxkblayout` with no timeout.
- command(), lines 289-302: reads up to 4096 bytes per event and processes
  EVERY buffered "cycle" line in a while loop, calling select_next() for each.
- InputMethodState.qml: cycle() writes to stdin, returns true; onExited
  blanks state and restarts after 5000ms.
- fcitx5-remote -n healthy latency: 0.002s (measured 17:27). fcitx5-remote -h:
  "-t,-T switch Active/Inactive", "-s <imname> switch to the input method
  uniquely identified by <imname>". Note: -t is active/inactive, NOT
  "switch to the other method".
- Existing precedent that fcitx5-remote can block: the CTRL+SPACE terminal
  bind in input-method.lua wraps its call as
  `timeout 0.3 fcitx5-remote --check -c`. A 2ms healthy call gets a 300ms
  timeout guard in production code. Whoever wrote that bind has seen
  fcitx5-remote hang.
- fcitx5 PID 1828 alive, service omarchy-fcitx5.service active since
  15:17:30. indicator.py PID 3444 alive at 17:27. Both same PIDs as T saw.
- journalctl --user -u omarchy-fcitx5.service 16:40-16:50 on 21/11: only an
  autosave at 16:47:30. No error, no restart in the stall window. Confirms
  T: fcitx5 logged nothing during the stall.
- lotus-autostart.sh: ~/.local/bin/lotus-autostart.sh, mtime
  16:52 21/11. Backup .bak-20261121, 258 bytes vs 259 current. diff shows
  exactly one line changed: `-s lotus` to `-s ngosen`. 2>/dev/null still
  present on both lines. Comment still says "switch to Lotus".
- autostart.lua line 13 launches the lotus script at login. It also launches
  `fcitx5 -d` while omarchy-fcitx5.service already runs fcitx5: dual
  launcher, the -d is redundant but harmless.
- No pacman hook re-applies local patches. Hooks present include
  00-omarchy-update-guard.hook (PreTransaction, checks the update entry
  point, AbortOnFail) and 10-omarchy-hyprland-reload-pause.hook. Neither
  preserves edits under /usr/share/omarchy.
- hyprctl binds could not be verified from SSH: HYPRLAND_INSTANCE_SIGNATURE
  not set. The bind file is the evidence for the live bind, not a live query.
- fcitx5 config ~/.config/fcitx5/config: [Behavior] ActiveByDefault=False.
  Profile: group Default, keyboard-us + ngosen, DefaultIM=ngosen.

## Fix 1, retroactive attack (lotus-autostart.sh, already applied)

F1-1. The applied fix is half the proposal. T proposed two changes: the
word lotus to ngosen, AND removing 2>/dev/null so a future failure is
visible. Only the word changed. diff of backup vs current is exactly one
line; both `fcitx5-remote -s ngosen 2>/dev/null` and
`fcitx5-remote -o 2>/dev/null` still discard stderr. A future failure is
still silent. Severity: MITIGABLE. Finish the second half, or admit the
fix was word-only.

F1-2. The "remove 2>/dev/null makes failure visible" claim is unproven
even if done. The script runs via o.launch_on_start in autostart.lua. Where
does launch_on_start send stdout and stderr? Nobody checked. If it goes to
the Hyprland log, to the journal, or to /dev/null is unknown. Removing the
redirect without knowing the destination does not make anything visible, it
moves the output to an unknown sink. Severity: MITIGABLE. Find the sink
first (run the script once with a forced failure and see where the output
lands), then decide on the redirect.

F1-3. The verification step is vacuous. T: "reboot or run the script, then
fcitx5-remote -n must print ngosen". DefaultIM=ngosen already guarantees
-n prints ngosen at login whether the script runs or not. The check cannot
distinguish "script worked" from "script never ran" from "script failed".
A real verification needs a distinguishing test, for example temporarily
setting DefaultIM to keyboard-us in a test profile, or logging a marker
from the script itself (timestamped line to a file) and checking the marker
after login. Severity: BLOCKING for any claim that Fix 1 works at login.
The fix may be fine; the proof is void.

F1-4. The untested assumption: does `-s ngosen` do anything at login with
no focused window and no input context? T's own log (16:38) shows a cycle
with no focused window left -n unchanged. -s calls SetCurrentIM, which
applies to the current input context. At login there is none. It is
plausible the -s is still a no-op, now for a different reason than the
lotus name, and the only reason -n shows ngosen is DefaultIM. The script
does have a good wait loop (up to 20s for `fcitx5-remote --check`), so the
startup race is handled, but the no-context question is not answered.
Severity: MITIGABLE. Test at a real login: check -n and a marker file
before any window gains focus.

F1-5. Side effect the no-op did not have. The old line could never change
anything. The new line forces ngosen at every login. If the user ever
changes DefaultIM away from ngosen, the script will override that choice
on every login, silently. Also the stale comment ("switch to Lotus") and
the stale autostart.lua comment ("Auto-switch to Lotus") now mislead the
next reader: the file says Lotus and does ngosen. Severity: ACCEPTED RISK,
fix the comments when touching the file next.

F1-6. Backup correctness: the backup is correct. .bak-20261121 differs by
exactly one byte (lotus 5 chars vs ngosen 6 chars), content otherwise
identical. Rollback by restoring the backup works. Note the backup sits
next to the live script with no README; a future agent could mistake it
for the current file. Minor, ACCEPTED RISK.

## Fix 2a attack (retry SetCurrentIM up to 2s in indicator.py)

F2a-1. BLOCKING. The retry budget is an order of magnitude shorter than
the observed stall. Healthy cycle lag is about 200ms. Observed stall lag
was about 21s for the cycle and about 3 minutes for wtype. A 2s retry
expires long before a 21s stall clears, and the press is still dropped,
just 2s later. The fix does not survive the failure it is meant to
survive. The correct design is to retain pending until the next successful
snapshot confirms the switch landed, with a TTL measured in minutes (or
until superseded by a newer press), not a 2s retry window.

F2a-2. BLOCKING. Retrying inside refresh() lengthens the single-threaded
main-loop block that causes the pile-up. One refresh() tick during a full
dbus stall can block for up to about 7s: snapshot is 3 calls
(CurrentInputMethodGroup, InputMethodGroupInfo, CurrentInputMethodInfo),
plus SetCurrentIM, plus a second snapshot of 3 calls, each with a 1000ms
timeout, all synchronous on the GLib main loop. While refresh() is blocked,
the stdin watch cannot run, so Super I presses accumulate in the pipe.
command() then processes every buffered line in a while loop, calling
select_next() for each, so N frustrated presses flip the method N times
and the final method depends on the parity of the press count. The user
cannot predict the outcome. Adding retries to refresh() makes each tick
block longer and the pile-up worse. The retry treats the symptom (dropped
pending) by worsening the mechanism (main-loop block). The real fix is
async dbus calls or a hard per-tick call budget, not more synchronous calls.

F2a-3. BLOCKING (patch target). See correction C1: pending is cleared in
three places (watch.refresh() line 231, Indicator.refresh() line 112,
command() line 302). A patch that only edits refresh() misses two of them.
Also select_next() clears nothing itself but its caller does. The patch
must cover all three sites or centralize pending clearing in one place,
or the first transient error in an unpatched path still eats the press.

F2a-4. MITIGABLE. The 50ms pending poll hammers a stalled bus. While
pending is set, schedule() re-arms a 50ms timer, and each tick issues up
to 7 synchronous dbus calls. During a stall the loop is blocked nearly
100 percent of the time in timeouts. Cheaper than retry: exponential
backoff on the pending poll (50ms, 200ms, 500ms, 2s) so the stalled bus
is not hammered, plus retaining pending across errors. Backoff costs one
small change and no new component.

F2a-5. MITIGABLE. Logging the failure "to stderr so it is visible in the
journal" is unproven. indicator.py is spawned by Quickshell Process, which
captures stdout via SplitParser and does not capture stderr anywhere in
InputMethodState.qml. stderr goes to Quickshell's own stderr, and where
that lands (journal, Hyprland log, nowhere) was not checked. Also logging
every failed retry at 50ms cadence during a 3-minute stall is thousands
of lines: log spam that can flood the journal. Needs rate limiting (log
once per stall, not once per tick) and a verified sink.

F2a-6. MITIGABLE. select_next() runs `hyprctl -j devices` synchronously
with NO timeout before any dbus call. If the stalled component is
Hyprland's socket rather than fcitx5's dbus, the indicator wedges on
hyprctl indefinitely and no dbus retry helps at all. Fix 2a does not
touch this call. Mitigation: cache the device list (it changes rarely) or
add a timeout with a fallback to the last-known layout. Note the layout
path is dead code on this machine anyway: T verified all keyboards report
layout "us", so cycle_choice takes the simple method path and
layout_switches never runs. The hyprctl call buys nothing here and risks
everything.

F2a-7. ACCEPTED RISK. A retained pending has a staleness hazard of its
own. Press Super I, stall, forget about it, open a password field 5
minutes later: a retained pending applies to that new context and flips
the method inside the password field. Any retention needs a TTL and a rule
that a newer press supersedes an older pending. A TTL of minutes, not
seconds and not forever.

## Fix 2b attack (wrapper: poll fcitx5-remote -n up to 1s, fall back to -t)

F2b-1. BLOCKING. The fallback races the stalled switch, and the race is
unwinnable. Concrete scenario, using T's own numbers: user presses Super I
at t0. indicator.py queues pending=keyboard-us. dbus stalls. The wrapper
polls -n for 1s, sees no change, fires `fcitx5-remote -t`, toggling to
keyboard-us. At t0+21s the stalled SetCurrentIM finally lands, toggling
back to ngosen. Net result: the user ends on ngosen, the opposite of what
they asked, with no indication anything went wrong. Two writers (indicator
pending, wrapper -t) share one state with no sequence number, no lock, and
no way to know whether the stalled call is dead or merely late. The 1s
poll window is 5x the healthy lag (200ms) but 21x shorter than the
observed stall lag, so the fallback false-triggers in exactly the case it
is meant to fix: every stall longer than 1s.

F2b-2. BLOCKING. `-t` is the wrong tool. fcitx5-remote -h says "-t,-T
switch Active/Inactive". It toggles active/inactive, not "switch to the
other method". It works on this machine only because the group has exactly
2 methods and keyboard-us is the inactive one (state 1) while ngosen is
the active one (state 2). If a third method is ever added, -t no longer
cycles to it. Worse, -t's result depends on the state at the instant it
runs: if the state changed between the poll and the -t (user pressed
Super I again, the app changed context, Fix 4 auto-activated), -t toggles
the wrong way. It is not idempotent and not target-directed. A correct
fallback names its target explicitly: `fcitx5-remote -s <target>`.

F2b-3. BLOCKING. Nothing serializes presses. The user mashes Super I 3
times during a stall: 3 wrappers run concurrently, each polls -n, each
fires -t. Toggles multiply and the final method is parity luck. The
wrapper needs flock -n (and a defined policy for the locked case: drop the
duplicate press, do not queue it), plus `timeout` on every fcitx5-remote
call.

F2b-4. MITIGABLE. The wrapper's own poll depends on the stalled path.
`fcitx5-remote -n` is a dbus call to fcitx5. During the exact stall the
fix is meant to survive, -n can hang: fcitx5-remote's dbus timeout is
unknown, and the CTRL+SPACE bind's `timeout 0.3` wrapper is evidence the
authors expect it to block. Without `timeout` on every call, the wrapper
hangs past its 1s budget and the fallback fires late, after the stall
cleared, toggling a healthy state. Every call in the wrapper must be
wrapped in `timeout` with a budget shorter than the poll window.

F2b-5. MITIGABLE. T proposes editing the package-owned bind file to call
the wrapper. That edit is unnecessary. The user's own
~/.config/hypr/bindings.lua already overrides defaults with hl.unbind()
(lines 36, 68, 74 show the pattern). The wrapper can be bound from user
config, which survives Omarchy updates. Editing the package file is the
fragile option, not the only option. If the wrapper is bound from user
config, the only package-owned dependency left is indicator.py itself.

F2b-6. ACCEPTED RISK. The wrapper adds a second switch path the user must
reason about, and when it misfires the failure is at least visible quickly:
the bar widget follows fcitx5 state via its 500ms poll, so a wrong-method
toggle shows within 500ms and one more press fixes it. But "one more
press" during a stall re-enters the same race, so this is small comfort.

## Fix 3 attack (30s watchdog probe, restart indicator.py then fcitx5)

F3-1. BLOCKING. The probe is not a measurement, it is a treatment. Every
30s it does a cycle round trip (cycle + cycle back), flipping the user's
live input method twice: 4 flips a minute, about 240 an hour, about 3,800
over a 16-hour day. Concrete interleaving: probe cycle flips to
keyboard-us, the user presses Super I (flips to ngosen), probe cycle-back
flips to keyboard-us. The probe ate the user's toggle and left them on
keyboard-us mid-sentence, typing plain ASCII until they notice. If the
cycle-back is lost (stall, or the 5s reader-restart window), the user is
left on keyboard-us indefinitely. A detection probe must be read-only
(fcitx5-remote -n latency only). A cycle round trip as a probe is a design
error, not a detail.

F3-2. BLOCKING. No backoff, no circuit breaker, no max restarts. During
a 3-minute stall the probe fires every 30s: restart indicator (useless,
PID 3444 was alive through the whole observed stall), re-probe, restart
fcitx5, re-probe, restart fcitx5 again, up to 6 restarts in one stall.
Each fcitx5 restart destroys every input context, kills any in-progress
Telex preedit (half-composed word gone), and resets the current method to
DefaultIM ngosen. After the stall clears, the user is left on ngosen even
if they had keyboard-us for code. And if the stall is in Hyprland rather
than fcitx5, every restart is pure disruption with zero benefit, while the
new fcitx5 must re-handshake the input-method protocol with a stalled
compositor. The proposal needs: restart only after N consecutive stalled
probes, at most one fcitx5 restart per stall episode, and a cooldown after
a restart before the next probe counts as a stall.

F3-3. BLOCKING. Missing-env false positive. `omarchy-input-method cycle`
exits 1 with "OMARCHY_PATH is not set" outside the Hyprland session env
(T's own log, 16:37:56). A cron job has neither OMARCHY_PATH nor the
session dbus address. A systemd user timer may have the dbus address but
OMARCHY_PATH is set by the Hyprland session, not by the user manager. If
the probe treats a cycle failure as "stall", it restarts fcitx5 every 30s
forever, on a healthy system, because of an env var. The runner must be a
systemd user timer (not cron), must export OMARCHY_PATH=/usr/share/omarchy,
must have the session bus, and must distinguish "cycle infra broken"
(fast exit 1) from "fcitx5 stalled" (slow). None of this is in the proposal.

F3-4. BLOCKING. The 2s threshold has no margin. T's own healthy
measurement of cycle-back was 1s (16:49). Under load (load average 1.78,
Chromium scopes starting 16:44:22) a healthy cycle can exceed 2s. The
threshold rests on one healthy sample, with no latency distribution under
load. False positives restart fcitx5 while the user is typing, at the
cost described in F3-2.

F3-5. MITIGABLE. Restarting indicator.py first treats a component proven
healthy. It also destroys state: killing it drops any "cycle\n" lines
queued in its stdin pipe, blanks the bar widget (InputMethodState.qml
onExited sets root.state = ({})), and the new instance starts with
pending="" and last="", losing the only record of what the user asked
for. If a restart is ever needed, pending must be drained or preserved
first, which the current design cannot do.

F3-6. MITIGABLE. The proposal says step 2 "briefly interrupts typing" and
needs user approval. The real cost is larger: lost preedit, lost
per-window method state (every window reverts to DefaultIM), and a silent
method flip to ngosen for a user who was on keyboard-us for code. Their
next code is Telex-mangled until they notice. Approval must be informed
by that cost, not by "briefly interrupts typing".

F3-7. ACCEPTED RISK, but it undercuts the value case. The watchdog would
not even have fired for the observed stall's cycle component: the cycle
landed 21s late, so the cycle path self-cleared before a 30s probe plus
restart sequence could act. The watchdog only helps stalls longer than
about 60-90s (detect 30s, restart, re-probe 30s), while the observed
stall self-cleared in about 3 minutes for wtype. Marginal gain, high
disruption.

F3-8. MITIGABLE. Probe pile-up, the same disease as the indicator stdin
queue in a second component. Without `timeout` on every call and `flock`
on the script, a stalled probe (fcitx5-remote hanging for its full dbus
timeout, qs ipc hanging for its own timeout) overlaps the next 30s probe.
After recovery, N queued probes each do a cycle round trip: 2N flips in a
burst.

## Fix 4 attack (ActiveByDefault=True experiment)

F4-1. BLOCKING. It treats a symptom that was not reproduced. T's H2
(per-context activation: new tab starts with IM inactive) was REFUTED for
reported state: a new Zen tab kept ngosen (16:44:08-16:44:35). The stall
is in the shared path, not in activation. Fix 4 changes global behavior
to fix a hypothesis that failed its own test. The experiment should only
run after H2 is actually reproduced (demonstrate a fresh context starting
inactive and requiring a toggle).

F4-2. BLOCKING. The password-field safety claim is unverified. T writes
"fcitx5 already steps aside in password fields, so that specific risk is
low". The only evidence is a comment in indicator.py switchable() ("A
lone composition engine still toggles, and steps aside in password
fields"), which is about the widget's polling decision, not a test of
fcitx5 in a password field. No live password-field test was done. If the
claim is wrong, the cost is a mistyped password the user cannot see:
Telex transforms keystrokes invisibly behind dots, so a sudo password
fails repeatedly and the user cannot tell why. This must be tested in a
real password field (sudo prompt, a login form) before the experiment, not
assumed from a code comment.

F4-3. BLOCKING. The harm cases are untested and the harm surface is
larger than the benefit surface. With ActiveByDefault=True every new input
context starts with Telex armed: new terminal tab, new editor buffer, new
VS Code file, Zen address bar. The user is a CS student who types code
far more often than Vietnamese prose in new contexts. Concrete mangling:
typing `sudo` in a fresh terminal, the s after u applies an acute accent
and the shell receives "súdo"; typing `users` gives "úers"; variable and
function names containing s, f, r, x, j, w, d sequences get diacritics.
T's verification (5 fresh Zen tabs compose 5/5) measures only the benefit
and never the harm. The experiment needs harm tests first: type code in 5
fresh terminals and 5 fresh editor buffers with no toggle, and confirm
zero mangling, plus the password-field test in F4-2, plus the URL bar.

F4-4. MITIGABLE. Interaction with Fix 2a retention: if pending is retained
across stalls AND new contexts auto-activate ngosen, a stale pending from
an old press can flip a fresh context, including a password field. Any
retention TTL must be shorter than the time between the press and the next
new context, which is unknowable. Interaction with Fix 3: every fcitx5
restart resets contexts, so after a watchdog restart the user's next
terminal starts Telex-armed even mid-coding-session.

F4-5. MITIGABLE. Rollback is not free. Reverting needs a config edit plus
a fcitx5 restart, which itself interrupts typing and resets all contexts.
Also the config file is user-owned (~/.config/fcitx5/config), which is the
one point in Fix 4's favor: it survives Omarchy updates, unlike Fix 2's
files.

F4-6. ACCEPTED RISK. The experiment as designed has no decision rule: no
stated number of days, no metric for "better", no owner to call it off.
An experiment without a stop rule becomes a permanent behavior change by
default.

## Fix 5 attack (logging-only stall monitor for days)

F5-1. BLOCKING. It is not logging-only. The proposed monitor reuses Fix
3's probe, which does a cycle round trip. That toggles the user's live
input method twice every 30s, with all the interleaving hazards of F3-1,
for days, while calling itself logging-only. A truly read-only monitor
polls `timeout 2 fcitx5-remote -n` latency plus load average plus journal
timestamps, and never cycles. As specified, the monitor perturbs the
system it measures, and any stall it "catches" may have been lengthened
or caused by its own cycles.

F5-2. BLOCKING. The instrument cannot localize the trigger. It measures
one number (cycle round-trip time) for three different failure domains:
fcitx5 dbus stalled, Hyprland socket stalled, indicator stdin queue backed
up. A slow cycle does not say which one. The discriminating instrument
needs per-component timings at the same moment: (a) fcitx5-remote -n
latency (dbus to fcitx5), (b) hyprctl devices latency (compositor socket),
(c) wtype latency (virtual keyboard path), (d) time from writing "cycle\n"
to the indicator's state JSON line (reader responsiveness). Only then can
the 16:42-16:45 stall be attributed. Also 30s cadence is too coarse: the
stall window's key events (Chromium scopes 16:44:22, opencode-telegram
watchdog 16:44:26) happened seconds apart, and a 30s probe cannot order
them. Cadence should be 5s for a read-only latency poll.

F5-3. MITIGABLE. The correlation plan is weak because the channels were
already checked and showed nothing. fcitx5's journal was clean through
the stall (only an autosave at 16:47:30, verified live), and the xkbcomp
warnings are routine noise (80 that day). Logging the same channels again
for days will likely reproduce "no signal". The monitor needs new
channels (per-component latencies above), not more of the same logs.

F5-4. MITIGABLE. No owner, no review cadence, no stop rule, no alert.
"Run for a few days" with nobody assigned to read the log means it runs
indefinitely, toggling the IM twice a minute the whole time. Define: who
reads it, when, what decision it feeds, and when it stops.

## Cross-cutting attack: Omarchy updates silently revert Fix 2

X1. BLOCKING. Both files Fix 2 touches are owned by omarchy-settings
4.5.0-3 (verified live with pacman -Qo). Files under /usr/share are not
pacman backup files: on the next omarchy-settings upgrade they are
overwritten silently, with no .pacnew and no warning. There is no hook
that re-applies local patches (checked /usr/share/libalpm/hooks: the
update guard only checks the update entry point). T's plan ("keep the
patch in the repo and re-apply after Omarchy updates") has no trigger:
nothing tells anyone an update happened. The user discovers the revert
only when typing breaks again, weeks later, and the failure looks like a
new bug.

X2. BLOCKING. Half-applied state is worse than either pure state. If the
re-apply step is interrupted, or only one file is re-applied, the system
runs the new wrapper (which fires -t on a 1s timeout) against the OLD
indicator.py (which clears pending on the first dbus error). Both fire,
double toggle, and the user cannot tell which component moved the method.
The re-apply procedure needs an atomic check (verify both files' hashes
after re-applying) and a way to detect the revert (a version stamp checked
at login, or a pacman hook that warns).

X3. MITIGABLE. The bind half of Fix 2 does not need the package file at
all. The user's ~/.config/hypr/bindings.lua already overrides defaults
with hl.unbind() (lines 36, 68, 74). Bind the wrapper from user config.
That leaves only indicator.py as package-owned, which halves the revert
surface and removes the bind from the update problem entirely.

## Interaction matrix (fixes combined)

- Fix 2a retry + Fix 3 watchdog restart: the watchdog kills indicator.py
  while Fix 2a's retry is mid-flight. The SetCurrentIM goes to a dying
  fcitx5 (NO_AUTO_START means it fails, pending cleared or retried against
  a fresh daemon whose state is DefaultIM). The retry dies with the
  process it lives in.
- Fix 2b wrapper + Fix 3 probe: the probe's cycle round trip and the
  wrapper's -t fallback are two more writers to the same state. During a
  stall, three writers (indicator pending, wrapper -t, probe cycle) can
  fire within seconds of each other. Final method is whichever fired last.
- Fix 2b wrapper + Fix 2a retry: the wrapper fires -t at 1s while the
  retry is still trying SetCurrentIM for up to 2s. The retry then applies
  the original pending on top of the -t result, toggling twice.
- Fix 4 + Fix 2a retention: a stale pending plus auto-activated new
  contexts means an old press can flip a fresh context, including a
  password field (see F4-4).
- Fix 4 + Fix 3 restart: every fcitx5 restart resets contexts, so the
  user's next terminal after a restart starts Telex-armed mid-coding.
- Fix 3 probe + Fix 5 monitor: if Fix 5 ships first and Fix 3 is
  rejected, the monitor still toggles the IM twice a minute, because it
  reuses the same probe code. The monitor's side effects survive the
  watchdog's rejection.
- Fix 1 + everything: none. Fix 1 is a login-time no-op that interacts
  with nothing, which is its only safety property.

## Cheapest alternatives nobody proposed

A1. Direct bind, no Quickshell in the path. In ~/.config/hypr/bindings.lua
(user file, survives updates, precedent hl.unbind exists): unbind SUPER+I
and bind it to a tiny script that runs `flock -n` plus
`timeout 2 fcitx5-remote -s <target>` where target is computed from the
current method (read -n first, also under timeout). This bypasses the
stdin queue, the pending mechanism, the hyprctl -j devices call, and the
50ms poll. The bar widget still follows state via its 500ms poll, so the
display stays correct. Cost: loses cycle_choice multi-layout logic, which
is dead code on this machine (single "us" layout, verified by T), and
loses the retain-pending-until-focus behavior. What it gains: one dbus
call, no queue, failure is loud (nonzero exit) instead of silent. This is
the cheapest real fix and should be tested before any indicator.py patch.

A2. Backoff, not retry. Change the pending poll from a fixed 50ms to
exponential backoff (50ms, 200ms, 500ms, 2s) and retain pending across
dbus errors with a TTL. One small change, no new component, no new
writer, and it stops hammering the stalled bus.

A3. Visibility instead of machinery. After Super I, show the current
method on screen (a brief OSD or notify-send with the method name). The
core UX bug is silent lag: the user types before the switch lands because
nothing tells them it has not landed yet. A visible method indicator
kills the "typed through the wrong method" symptom without touching dbus
at all. It does not fix the stall, but it fixes half the complaint for
near-zero risk.

A4. Longer dbus timeout only: REJECTED, and worth naming so nobody
proposes it next. Raising call() from 1000ms to 5000ms means each poll
tick can block 5x longer on the single-threaded loop, and the stdin
pile-up gets worse. Longer timeouts help a slow call succeed; they hurt
everything else waiting on the loop.

A5. Disable the 50ms poll: WEAK, and worth naming so nobody proposes it
as a fix. During a stall each tick already blocks for up to about 7s in
synchronous timeouts, so the 50ms cadence number is meaningless under
stall. The problem is synchronous calls, not the cadence. Disabling the
poll changes nothing while stalled and only slows healthy switching.

A6. The proper fix, stated plainly so the council does not mistake the
cheap fixes for it: make indicator.py's dbus calls async (Gio async
calls with callbacks) so the main loop never blocks, stdin stays
responsive during a stall, and presses are processed in order with a
sequence number. That is a bigger change to a package-owned file and needs
a re-apply procedure with a hash check. A1-A3 are what ship now; A6 is
what actually fixes the mechanism.

## Top 3 BLOCKING attacks

1. Fix 2b races the stalled switch (F2b-1 + F2b-2). The 1s poll window
   false-triggers in every stall longer than 1s, and the -t fallback then
   toggles against a SetCurrentIM that may still land 20s later, leaving
   the user on the opposite method. Two writers, one state, no
   coordination, and -t is active/inactive rather than target-directed.
   Must be answered before implementing: use an explicit -s target, add
   flock and timeout, and prove the fallback cannot fire while a switch
   is still in flight.
2. Fix 3 as specified can loop-restart a healthy fcitx5 (F3-1 + F3-2 +
   F3-3). The probe toggles the user's live method twice every 30s, has
   no backoff or circuit breaker, and a missing OMARCHY_PATH makes every
   cycle call fail, which the probe would read as "stall" and answer with
   a restart every 30s forever. Must be answered before implementing:
   read-only probe, restart only after N consecutive stalled probes, one
   restart per episode, env pinned, and infra-failure distinguished from
   stall.
3. Fix 2a does not survive the observed stall (F2a-1 + F2a-2). A 2s retry
   expires an order of magnitude before a 21s stall clears, and retrying
   synchronously inside the single-threaded loop lengthens the block that
   makes Super I presses pile up and execute as a parity-dependent burst.
   Must be answered before implementing: retain pending with a TTL until
   a successful snapshot confirms the landing, cover all three clearing
   sites, and cap the per-tick dbus budget or go async.

## Overall judgment

Ship nothing as specified. The diagnosis of the mechanism is mostly right
(the async lag, the silent pending clear, the shared-path stall), but
every fix as specified either does not survive the failure it targets
(Fix 2a, Fix 2b), treats a component proven healthy (Fix 3 step 1),
measures with a probe that changes what it measures (Fix 3, Fix 5),
changes global behavior for an unreproduced symptom (Fix 4), or proves
nothing (Fix 1). What survives is a redesigned set: A1 direct bind from
user config, A2 backoff plus TTL retention, A3 visible method feedback,
and a redesigned Fix 5 as a truly read-only per-component latency monitor
at 5s cadence with a stop rule. Fix 3 and Fix 4 do not survive in any form
close to the proposal. Fix 2 survives only after the redesign in the top 3
attacks above. No proposal addresses the wtype stall; the council should
say that plainly instead of implying Super I fixes cover it.

## What was checked live (read-only, no edits, no restarts, no kills)

- indicator.py, input-method.lua, InputMethodState.qml, lotus-autostart.sh
  and its backup (diff: one line, lotus to ngosen), fcitx5 config and
  profile, pacman -Qo ownership, libalpm hooks, fcitx5-remote -n timing
  (0.002s) and -h output, service and process state (fcitx5 PID 1828,
  indicator.py PID 3444, both alive), journalctl for the 16:40-16:50 stall
  window (only an autosave at 16:47:30).
- Live check wall time: 17:25-17:28, 21/11/2026. Report written 17:30.
