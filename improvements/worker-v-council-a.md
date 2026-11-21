# Council Member A verdict: Fix 2 (Super I fix), Worker T diagnosis
# Date: 21/11/2026. Verification window 17:24-17:26 Asia/Ho_Chi_Minh.
# All laptop reads read-only. No file edited on the laptop. No ydotool used.
# Repo: computer-use-wayland, branch todolist-push.

## Verdict: IMPLEMENT LATER (conditional)

Split verdict:
- (a) indicator.py retry: IMPLEMENT NOW, in the corrected form in section 3 below.
  T's direction is right, the mechanism needs two corrections (no new sync
  retry loop, and a deadline longer than 2s).
- (b) bind-path wrapper with `fcitx5-remote -t` fallback: REJECT AS SPECIFIED.
  The `-t` fallback is the wrong primitive and can undo a landed switch.
  Implement the corrected variant instead: fall back to `fcitx5-remote -s <target>`.
  That one-word change turns (b) from unsafe to safe, and then it is IMPLEMENT NOW.

Do not ship (b) with `-t`. Everything else in Fix 2 is sound.

## 1. Verification of T's description of the code (all confirmed, with two additions)

Files read live on the laptop, 17:24 +07, 21/11/2026:
- `/usr/share/omarchy/default/input-methods/indicator.py`, 322 lines, confirmed.
- `/usr/share/omarchy/default/hypr/bindings/input-method.lua`, 29 lines, confirmed.
  Line 22: `o.bind("SUPER + I", "Switch input language", "omarchy-input-method cycle")`.
  Line 23: Super+Shift+I binds `cycle back`.
- Chain confirmed end to end: `omarchy-input-method cycle` calls
  `omarchy-shell shell cycleInput` (returns "ok" only if the reader runs),
  `shell.qml` line 1792-1793 returns `Commons.InputMethodState.cycle(...)`,
  `InputMethodState.qml` lines 9-19 write `"cycle\n"` to indicator.py stdin,
  lines 33-38 restart the reader 5s after exit. The "ok in 7ms, switch lands
  later" async behavior T reported is exactly what this code does.

Confirmed claims, with exact lines in indicator.py:
- 1000ms dbus timeout in `call()`: lines 17-20. `call_sync(..., 1000, None)`
  with `Gio.DBusCallFlags.NO_AUTO_START`. Confirmed.
- Pending cleared on GLib.Error: `watch.refresh()`, lines 229-232. On any
  `GLib.Error` from `indicator.refresh()` it sets `indicator.pending = ""`
  AND `indicator.last = ""`, then returns an empty state. Confirmed. Note it
  clears `last` too, which also loses the display fallback.
- 50ms / 500ms polling: `schedule()`, lines 256-259. Pending means a 50ms
  timer, else polling means a 500ms timer. Confirmed.
- `Indicator.refresh()`, lines 108-129: line 116 calls
  `SetCurrentIM(pending)`, line 117 re-snapshots, lines 118-119 clear pending
  only when the snapshot confirms current == pending. So a `GLib.Error` from
  the snapshot at line 109 (before SetCurrentIM is even attempted) or from the
  re-snapshot at line 117 (after SetCurrentIM already succeeded) also loses
  the switch. The clear is broader than "SetCurrentIM failed".

Two things T did not mention, both material:
- (i) There is a SECOND clear site: `command()`, lines 301-302. If
  `select_next()` raises (`GLib.Error`, `OSError`, `ValueError`,
  `CalledProcessError`), `indicator.pending = ""`. A fix that only touches
  `watch.refresh()` leaves this hole open.
- (ii) A failed-read retry ALREADY EXISTS: `schedule()`, lines 260-261.
  If `failed` is set and fcitx5 is present, refresh is retried every 2000ms.
  But it is neutered by the clear: with pending already wiped, the retry only
  re-reads state, it never re-applies the lost switch. The real bug is the
  clear, not the absence of a retry. The minimal fix is therefore smaller
  than T described: stop clearing pending (and last) on transient error, and
  the existing machinery re-attempts.

## 2. Live test: what `fcitx5-remote -t` actually does (17:25:20 +07)

`fcitx5-remote` help text: `-t,-T  switch Active/Inactive`. It is an
activation toggle, NOT a method switch.

Empirical test, 17:25:20 +07, 21/11/2026 (state restored afterwards):
- Before: `ngosen`, state 2 (active).
- After one `-t`: `keyboard-us`, state 1 (inactive).
- After a second `-t`: `ngosen`, state 2 (active). Restored exactly.

So in THIS group (exactly two methods, keyboard-us + ngosen, DefaultIM ngosen)
`-t` happens to look like a method toggle, because fcitx5 reports the plain
keyboard-us method when the engine is inactive. A proper cycle to keyboard-us
also reports keyboard-us/1 (T measured this at 16:49), so the two are
indistinguishable by `fcitx5-remote -n` alone. That resemblance is a trap:
- With 3 methods in the group, `-t` toggles activation, it does not walk the
  group, so it cannot reach the intended method at all.
- If the current method is ngosen but INACTIVE (state 1, e.g. after Ctrl+Space
  direct input, or a per-context inactive state under ActiveByDefault=False),
  `-t` ACTIVATES ngosen instead of switching to keyboard-us. The wrapper
  would read `-n` before as ngosen and after as ngosen, conclude the fallback
  failed, while the activation state silently flipped underneath it.
- `-t` touches activation state, which is the same state the Ctrl+Space
  direct-input bind and the password-field step-aside behavior depend on.
  A method switch (`-s` / SetCurrentIM) does not.

## 3. Judgement on (a): retry in indicator.py refresh()

Direction correct, mechanism needs correction.

Why it is correct in direction: the pending value is an explicit method name,
not a toggle. Re-applying SetCurrentIM with the same pending value is
idempotent. A second Super I press recomputes pending from the existing
pending (`select_next`, line 98: `current = self.pending or state["current"]`),
so presses are not lost or duplicated by a retry, they supersede. There is no
double-switch hazard and no wrong-method hazard from (a) alone.

Why T's mechanism needs two corrections:
- (a1) Do NOT write a synchronous retry loop inside `refresh()`. `call()` is
  `call_sync` with a 1000ms timeout, and `refresh()` runs on the single GLib
  main loop. A "retry up to 2s" loop would block the loop for up to 2 extra
  seconds: stdin cycle commands queue unprocessed, the bar widget freezes.
  The better design is already in the file: preserve pending across the
  error, and let the existing 50ms pending poll (`schedule()`, line 257)
  re-attempt `refresh()`. No new blocking beyond what one call already does.
  (Caveat: during a stall each re-attempt still blocks up to 1000ms, so the
  effective cadence is about 1s, not 50ms. Acceptable, and no worse than the
  current 500ms poll under the same stall.)
- (a2) A 2s deadline is too short for the failure T actually reproduced.
  The observed stall delayed the switch by about 21s (16:45:00 press,
  visible 16:45:21). A 2s retry budget drops pending at 2s and the switch is
  still lost in exactly the reproduced case. A 2s fix only covers a 1-2s
  dbus hiccup, not the 3-minute stall. Recommendation: retain pending until
  it lands, the user presses again (which supersedes it), or a 30s deadline
  expires, then log the drop to stderr. 30s covers the observed 21s stall
  with margin. Trade-off stated honestly: a switch landing 21s late can land
  mid-word and split a Telex composition. But the user typed in the wrong
  method for those 21s either way, so late application is closer to intent
  than silent loss, and the late landing is at least visible in the bar.
  If the council wants the conservative end, 10s is the floor, not 2s.
- (a3) Cover both clear sites: `watch.refresh()` lines 229-232 and
  `command()` lines 301-302. Keep the legitimate clear at lines 111-112
  (pending not in methods means the method left the group).
- (a4) Log to stderr, never stdout: Quickshell parses indicator.py stdout
  as JSON (`InputMethodState.qml`, SplitParser). A stderr line
  (`print(..., file=sys.stderr, flush=True)`) is safe and lands in the
  journal. Log every failed attempt with timestamp and the pending value,
  and log the drop when the deadline expires. That log is what makes the
  next stall diagnosable instead of silent.

Confidence on (a) as corrected: high. It is a small, local, idempotent change
with the failure mode (silent loss) proven by the code, not inferred.

## 4. Judgement on (b): wrapper with `-t` fallback

REJECT as specified. The design has one correct idea (verify the switch
landed, retry if not) and one wrong primitive (`-t`).

Failure modes of `-t` as the fallback:
- False-negative poll undoes a landed switch. The wrapper polls
  `fcitx5-remote -n`, which is itself a dbus call to the same stalled fcitx5.
  During the stall the poll can read stale state or time out, so "not
  changed" does not prove "switch lost". If the switch DID land and the
  wrapper fires `-t`, it toggles the method straight back. The fallback
  then causes the exact symptom it was built to fix, with no trace except a
  method flip the user did not ask for.
- Late delivery. T proved a cycle can land 21s late. A `-t` issued into the
  same stalled path can also be delivered late, after recovery, toggling the
  method after the user has already re-pressed or after indicator.py has
  applied pending. The result is the wrong method with no user action.
- Double application with (a). If (a) retries and applies pending keyboard-us
  at 1.5s, and the wrapper already fired `-t` at 1.0s, the two layers fight:
  indicator.py sets keyboard-us, the late `-t` flips back to ngosen, and
  indicator.py sees current != pending on its next poll and re-applies,
  or the pending was already cleared on the earlier confirm. The final state
  depends on arrival order, which is nondeterministic under a stall.

The fix is one word: replace `-t` with `-s <target>`. The wrapper knows the
intended target (read current before the cycle, take the other method from
the group; the group is exactly [keyboard-us, ngosen] per
`~/.config/fcitx5/profile`, confirmed live). `fcitx5-remote -s <imname>`
switches to the method uniquely identified by that name (help text, verified
live). With `-s`:
- A redundant fallback is a no-op: re-applying the same target changes nothing.
- A false-negative poll is harmless for the same reason.
- Wrapper and (a) converge: both apply the same explicit target, so a
  double application is idempotent instead of a fight.
- It works with any group size and from any activation state.

Wrapper details that must be in the implementation, not left open:
- Capture the before-value BEFORE calling cycle, poll for a change from it.
- Put a timeout on every `fcitx5-remote` call in the wrapper (e.g.
  `timeout 0.2 fcitx5-remote -n`), otherwise a stalled dbus call blocks the
  wrapper indefinitely. The same applies to the fallback `-s` call.
- Poll interval about 100ms, budget 1s, then one `-s <target>`, then stop.
  Do not loop the fallback: one shot only, then log to stderr and leave the
  state visible in the bar.
- Direction matters: Super+Shift+I (cycle back) has the opposite target.
  The wrapper must take the direction argument through.

Confidence on the `-t` flaw: high. It is proven by the help text and by the
live test in section 2, plus the false-negative argument which follows from
T's own stall evidence.

## 5. Interaction summary: wrapper plus indicator.py retry

- (a) corrected plus (b) corrected (`-s`): safe together. Both layers apply
  the same explicit method name. Worst case is a redundant idempotent call.
- (a) plus (b) as specified (`-t`): unsafe together. The toggle can undo the
  retry's application, and the outcome depends on arrival order during a
  stall. This is the strongest reason (b) must not ship with `-t`.
- (a) alone already fixes the 1-2s hiccup case and, with a 30s deadline, the
  reproduced 21s stall. (b) alone fixes the case where indicator.py itself
  is dead (Quickshell restarts it after 5s) or the "cycle" write never
  arrived, because `-s` talks to fcitx5 directly. They cover different
  failure modes, so both are worth having, in corrected form.

## 6. Omarchy update survival (how the patch lives)

Verified live with `pacman -Qo`, 17:24 +07:
- indicator.py and input-method.lua are both owned by `omarchy-settings
  4.5.0-3`. Any upgrade of that package overwrites both files. T's note is
  correct, and there is no user-override path for (a): `InputMethodState.qml`
  line 19 hardcodes `OMARCHY_PATH + "/default/input-methods/indicator.py"`.
  So (a) MUST be re-applied after updates. Survival plan, all verified to
  exist: keep the exact diff in this repo, add a re-apply hook in
  `~/.config/omarchy/hooks/post-update.d/` (a real working hook dir, three
  executable `.hook` scripts already present there, read 17:26 +07), and add
  a version check (e.g. a weekly check that the patched lines are still
  present, else re-apply and notify). Do not rely on memory.
- (b) does NOT need to touch /usr/share at all. `~/.config/hypr/bindings.lua`
  is the documented personal-overrides file (header: "Keep only your personal
  keybinding overrides here"), and it already uses `hl.unbind` plus `o.bind`
  (lines 36, 68, 74). So (b) can be installed as: `hl.unbind("SUPER + I")`
  and `hl.unbind("SUPER + SHIFT + I")` in bindings.lua, rebind both to a
  wrapper script in `~/.local/bin/`, and the default bind file stays
  pristine. That survives Omarchy updates untouched. This is strictly better
  than T's proposal to edit input-method.lua, and it removes half the
  update-survival problem.

## 7. Verification test (what would prove it works)

T's proposed test (Super I 20/20 flips within 1s in a focused Zen textarea)
is necessary but not sufficient: it only exercises the healthy path, where
the current code already passes (T measured about 200ms healthy). Add:
- (1) Healthy path: 20/20 flips within 1s, typing "tieengs vieetj" after
  each press composes correctly for the shown method. Same as T proposed.
- (2) Dead-reader drill: kill indicator.py (PID 3444 at verification time),
  press Super I inside the 5s Quickshell restart window. With (a) corrected,
  the switch must land after the reader restarts (pending retained), or the
  wrapper (b) must land it directly via `-s`. Either way the flip must be
  visible within 6s. This is the drill that separates the fix from luck.
- (3) Double-press drill: press Super I twice within 300ms. Final method
  must be the original method, never stuck on the intermediate one, and the
  bar must agree with `fcitx5-remote -n`.
- (4) Failure visibility: after an induced failure, `journalctl` must show
  the stderr log line with timestamp and pending value. Silent loss must be
  impossible to miss in the log.
- (5) Regression: normal typing, password fields (engine steps aside),
  terminal Ctrl+Space direct input still works, bar widget agrees with
  `fcitx5-remote -n` after every flip.
- Deliberately NOT proposed: a forced 21s stall drill, because no safe way
  to induce the real stall on demand is known. The 30s deadline is justified
  by the observed 21s case, not by a new reproduction.

## 8. Strongest three reasons (summary for the coordinator)

- (1) The silent-loss bug is proven in the code, not inferred: indicator.py
  lines 229-232 clear pending AND last on ANY GLib.Error, including a
  snapshot failure before SetCurrentIM runs and a re-snapshot failure after
  it already succeeded, and a second clear site exists at lines 301-302.
  Preserving pending is a small, idempotent, high-confidence fix.
- (2) The `-t` fallback is the wrong primitive and can undo a landed switch:
  `-t` toggles Active/Inactive (help text and live test 17:25:20 +07), it
  only resembles a method switch in this exact 2-method group, and a
  false-negative poll during the same stall it is meant to fix would flip
  the method back. One word, `-s <target>`, removes the whole hazard class.
- (3) The 2s retry budget does not cover the failure it is meant to fix:
  the reproduced stall delayed the switch by about 21s, so a 2s deadline
  still drops it. Retain pending for 30s (or until superseded), log every
  failure to stderr, and let the existing 50ms pending poll do the retrying
  instead of adding a blocking sync loop.

## Evidence log (wall-clock Asia/Ho_Chi_Minh, 21/11/2026)

- 17:24:11 +07: SSH via ~/workspace/ssh-laptop.sh. indicator.py 322 lines,
  input-method.lua 29 lines, both root-owned, dated Nov 5 10:12.
- 17:24:17 +07: read input-method.lua in full (binds at lines 22-23).
- 17:24-17:25 +07: read indicator.py in full (cat -n, lines 1-180 then 180-322).
- 17:25 +07: `omarchy-input-method` read; group Default, methods
  keyboard-us + ngosen, DefaultIM ngosen, confirmed from
  ~/.config/fcitx5/profile. `pacman -Qo`: both files owned by
  omarchy-settings 4.5.0-3; `omarchy-input-method` owned by omarchy 4.5.0-3.
- 17:25:20 +07: `-t` live test. ngosen/2, then `-t` gives keyboard-us/1,
  then `-t` gives ngosen/2. Restored exactly.
- 17:26:14 +07: fcitx5 PID 1828, indicator.py PID 3444, both alive since
  boot (etime about 02:08). `fcitx5-remote -n` answers in 2ms healthy.
- 17:26:36 +07: `~/.config/omarchy/hooks/post-update.d/` exists with three
  executable hooks; `~/.config/hypr/bindings.lua` has hl.unbind precedent.
- Total verification elapsed: about 3 minutes. Nothing edited on the laptop.
  Final IM state left as found: ngosen, state 2.
