# Diagnosis: intermittent Vietnamese typing failure in AI-optimized Zen
# Worker T, 21/11/2026. All times wall-clock Asia/Ho_Chi_Minh.
# Evidence: live commands on the laptop, reproduction scripts, logs.
# Repo: computer-use-wayland, branch todolist-push.

## User symptoms (verbatim gist)
- When Zen runs AI-optimized, Vietnamese typing breaks often, sometimes works sometimes not.
- Pressing Super I to switch input language does not register.
- After a while it fixes itself. User does not know why.

## The stack (verified live)
- Input method: fcitx5 (PID 1828, omarchy-fcitx5.service, running since 15:17:30 after reboot). No ibus daemon.
- Engine: ngosen (Telex, VietnameseOn=True). Group: keyboard-us + ngosen, DefaultIM=ngosen.
- fcitx5 config: ActiveByDefault=False. TriggerKeys default.
- Zen env: XMODIFIERS=@im=fcitx, QT_IM_MODULE=fcitx, SDL_IM_MODULE=fcitx, GTK_IM_MODULE unset on purpose (hyprland.lua comment: unsetting it avoids a double IM context for Gtk3 Wayland apps; Chromium uses text-input-v3 directly).
- Super I chain (all files read): Hyprland bind in /usr/share/omarchy/default/hypr/bindings/input-method.lua -> `omarchy-input-method cycle` -> `omarchy-shell shell cycleInput` (qs ipc, has a timeout) -> Quickshell Commons.InputMethodState.cycle() -> writes "cycle\n" to stdin of long-running indicator.py (PID 3444, spawned by Quickshell, auto-restarts 5s after exit) -> indicator.py select_next() sets pending -> refresh() calls SetCurrentIM(pending) on fcitx5 via dbus.
- indicator.py polls fcitx5 every 500ms while the group has >1 method, and every 50ms while a switch is pending.

## What I reproduced live (the core finding)
A stall window 16:42:27-16:45:19 on 21/11/2026 in which BOTH the virtual-keyboard path AND the fcitx5 dbus path were stuck at the same time, then both recovered together:
- wtype (the agent typing path, Wayland virtual-keyboard protocol) hung: private helper timed out after 30s (run 2, 16:42:27), then 12s (run 3, 16:44:08, 16:44:47, 16:45:12), system wtype timed out 12s twice (16:44:20, 16:45:00). 5 consecutive hangs, textarea stayed empty.
- Super I (cycle) at 16:45:00 returned in 7ms with rc 0 but fcitx5-remote still showed ngosen; the switch to keyboard-us only became visible at 16:45:21, about 21 seconds later.
- Recovery: system wtype worked at 16:45:21 (7.4s, still slow), private wtype worked at 16:45:23 (567ms, normal), probe2 at 16:48:06 worked in 129ms with a clean WAYLAND_DEBUG trace (virtual keyboard created, keymap sent, keys delivered, destroy).
- Garbled composition after recovery: the textarea ended up "chaof banjhào bạn xin chaoào", consistent with keystrokes sent during the stall being queued and delivered late + interleaved, corrupting Telex composition. Keys are not only lost, they can arrive late and garbled.

Healthy-state baselines measured the same day:
- Super I switch lands in about 200ms (measured 16:49:38: cycle returned in 12ms, fcitx5-remote showed keyboard-us at +209ms; cycle back restored ngosen in 1s).
- wtype types in 129ms when healthy.
- fcitx5 journal 15:17-16:47: clean start, no errors, no restarts, only autosaves. Daemon is NOT crashing.

## Root cause (stated with confidence levels)
1. HIGH CONFIDENCE: Super I is asynchronous and can silently lag or be lost. The cycle command returns "ok" in ~7-12ms but only QUEUES the switch in indicator.py; the real SetCurrentIM happens on indicator.py's event loop. Healthy lag is ~200ms. During a stall it was ~21s. Worse, in indicator.py refresh(), if the fcitx5 dbus call fails or times out (1000ms timeout in call()), the code catches GLib.Error and CLEARS pending silently, so the switch is lost entirely with no error shown to the user. Pressing Super I and typing immediately therefore often types through the OLD input method. This is the direct mechanism behind "an Super I no nhan".
2. HIGH CONFIDENCE: there is a real intermittent stall in the shared input path (compositor + fcitx5 event handling) that freezes both virtual-keyboard input and fcitx5 dbus switching for minutes, then self-clears. Reproduced 5x in one window. It is NOT Zen, NOT Marionette/BiDi (no BiDi session was active during the hangs; Marionette calls worked fine throughout), NOT a fcitx5 crash, NOT the indicator.py process dying (PID 3444 alive the whole time).
3. MEDIUM CONFIDENCE: the "AI-optimized Zen" correlation is real but indirect. AI-optimized Zen means the agent is driving Zen: tab switches, new tabs, focus changes, agent typing via wtype. That churn creates new input contexts and competes with the user's own typing, so the user hits the stall/lag far more often than when typing alone in a quiet browser. The flags --remote-debugging-port / --marionette do not touch the input method path.
4. NOT PROVEN (open item): the exact trigger of the 16:42-16:45 stall. Candidates: (a) a stuck fcitx5 input context left by the SIGKILLed wtype in run 2, though the stall predates that kill (first hang was 1s after focusing the textarea, before any wtype ran); (b) system load spike (Chromium scopes started 16:44:22, opencode-telegram watchdog 16:44:26, load average 1.78 at 16:49); (c) a Hyprland event-loop stall. The xkbcomp warnings at 16:45:19 are routine noise (80 occurrences that day), not a cause. The discriminating test is in the proposal below.
5. REFUTED: opening a new Zen tab does NOT reset fcitx5's reported input method (ngosen stayed ngosen across tab A to tab B, 16:44:08-16:44:35). The simple "new tab resets IM" story is wrong for the reported state. ActiveByDefault=False remains a real footgun for per-context activation, but it was not the thing observed here.
6. SIDE BUG (proven, minor): lotus-autostart.sh runs `fcitx5-remote -s lotus`, but "lotus" is not a valid input method name here; tested 16:37, current IM stays ngosen. The step is a silent no-op (stderr discarded). Harmless because DefaultIM=ngosen plus `-o` activates it, but misleading.

## Proposed fix (in order, propose only, nothing applied yet)
### Fix 1 (trivial, safe, do first): lotus-autostart.sh
- Change `fcitx5-remote -s lotus` to `fcitx5-remote -s ngosen`, remove the 2>/dev/null on that line so a future failure is visible.
- Verify: reboot or run the script, then `fcitx5-remote -n` must print ngosen.
- Rollback: change the word back to lotus. One word, no behavior change today (it is already a no-op).

### Fix 2 (the real Super I fix): make the switch synchronous-confirming
Two layers, both small:
- (a) In indicator.py refresh(): do NOT clear pending on a transient dbus error. Retry the SetCurrentIM for up to 2s before dropping the pending choice, and log the failure to stderr so it is visible in the journal. Today a single >1000ms dbus hiccup silently eats the user's Super I press.
- (b) In the Super I bind path: after `omarchy-input-method cycle`, verify the switch landed by polling `fcitx5-remote -n` for up to 1s; if it did not change, fall back to `fcitx5-remote -t` (direct toggle) once. Implement as a wrapper script the bind calls, so the behavior is: press Super I, switch is confirmed within ~200ms or retried, never silently lost.
- Files touched: /usr/share/omarchy/default/input-methods/indicator.py and the bind in /usr/share/omarchy/default/hypr/bindings/input-method.lua. NOTE: both are owned by the Omarchy package and can be overwritten by an Omarchy update. Keep the patch in the repo (computer-use-wayland) with the exact diff, and re-apply after Omarchy updates, or move the logic into ~/.config so it survives updates.
- Verify: press Super I 20 times with a focused Zen textarea, each time fcitx5-remote -n must flip within 1s, 20/20. Type "tieengs vieetj" after each press and check the composed result matches the shown method.
- Rollback: restore the two files from backup (copy them first), or `git checkout` the repo patch. No other component depends on the new behavior.

### Fix 3 (stall detection + recovery): watchdog for the input path
- A small background probe every 30s: time `fcitx5-remote -n` and one `omarchy-input-method cycle` round trip (cycle + cycle back). If fcitx5-remote takes >2s or the cycle does not land within 2s, log a STALL event with timestamp and restart the input stack in this order: (1) kill indicator.py (Quickshell restarts it in 5s), (2) if still stalled, `systemctl --user restart omarchy-fcitx5.service` (fcitx5 restarts in ~1s, profile preserved, typing interrupted briefly).
- This needs the user's approval because step 2 briefly interrupts typing. Propose it as a cron/systemd user timer, not applied yet.
- Verify: the probe log shows stall events with timestamps; after a restart, the next probe is healthy.

### Fix 4 (experiment, needs a decision): ActiveByDefault
- Try fcitx5 ActiveByDefault=True (in ~/.config/fcitx5/config, [Behavior] ActiveByDefault=True) so new input contexts start with the IM active instead of inactive. This is the standard fix for "must toggle in every new field" behavior. Trade-off: it changes activation behavior everywhere, including apps where the user wants plain US first. fcitx5 already steps aside in password fields, so that specific risk is low.
- Verify: open 5 new Zen tabs, focus a textarea in each, type Telex immediately with no toggle, 5/5 must compose.
- Rollback: set it back to False and restart fcitx5.

### Fix 5 (catch the stall trigger): stall-catching monitor
- Run the probe from Fix 3 in logging-only mode for a few days (no restarts). When the next stall happens, the log gives the exact start/end time; correlate with journalctl (fcitx5, Hyprland, Chromium launches, CPU spikes) to identify the trigger. The 16:42-16:45 window is the reference: stall started before any wtype ran, ended around the 16:45:19 keymap recompile.
- This is the only way to close open item 4 with evidence instead of guessing.

## How to verify the whole fix works (acceptance test)
1. Super I 20/20 flips within 1s (Fix 2).
2. Type Telex in 5 fresh Zen tabs with no toggle: if Fix 4 is on, 5/5 compose; if off, the user toggles once per tab and it stays.
3. One forced stall drill: kill indicator.py, press Super I within the 5s restart window, confirm the switch still lands (via the Fix 2 retry) or is retried after the reader restarts.
4. No regression: normal typing, password fields, terminal Ctrl+Space prefix still work.

## Cleanup verified
- All my test tabs closed: 0 leftover worker-t tabs in Zen (22 tabs open, all the user's), Marionette sessions deleted, IM restored to ngosen state 2.
- Never touched: user tabs, Zalo, Teams, Jarvis, music, indicator.py process (only read its code), pill shader.
- Scripts used: ~/workspace/worker-t-typing-test.py, ~/workspace/worker-t-probe2.py, ~/workspace/worker-t-tabcheck.py (on the laptop at ~/workspace/), run logs /tmp/worker-t-typing-run*.jsonl and ~/workspace/worker-t-typing-run*.log.
