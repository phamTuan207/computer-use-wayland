# Worker T log: Vietnamese typing in AI-optimized Zen
# All times wall-clock Asia/Ho_Chi_Minh, 21/11/2026. Started 16:34.

## 16:34:21 - Input method stack identified
- Daemon: fcitx5 PID 1828, service omarchy-fcitx5.service, active running since 15:17:30 (after reboot). No ibus daemon.
- Current IM: ngosen, state 2 (active). Zen env: XMODIFIERS=@im=fcitx, QT_IM_MODULE=fcitx, SDL_IM_MODULE=fcitx, GTK_IM_MODULE empty (unset on purpose), GLFW_IM_MODULE=ibus.
- fcitx5 log 15:17-16:17: clean start, no errors, no restart. Wayland native input method protocol: 1. Autosaves 15:47, 16:17.
- fcitx5 config: [Behavior] ActiveByDefault=False. TriggerKeys default (Zenkaku_Hankaku, Hangul). Profile group Default: keyboard-us + ngosen, DefaultIM=ngosen.
- ngosen.conf: VietnameseOn=True, Telex (default).

## 16:35-16:37 - Super+I chain traced (read-only)
- Hyprland bind: /usr/share/omarchy/default/hypr/bindings/input-method.lua: `o.bind("SUPER + I", "Switch input language", "omarchy-input-method cycle")`. Super+Shift+I cycles back.
- `omarchy-input-method cycle` -> `omarchy-shell shell cycleInput` (qs ipc, has a timeout) -> Quickshell Commons.InputMethodState.cycle() -> writes "cycle\n" to stdin of long-running indicator.py (spawned by Quickshell Process, stdinEnabled, restarts 5s after exit).
- indicator.py (322 lines, /usr/share/omarchy/default/input-methods/indicator.py, READ ONLY, not touched):
  - select_next(): snapshot fcitx5 via dbus, cycle_choice over methods [keyboard-us, ngosen], sets self.pending, then refresh().
  - refresh(): if pending set and fcitx5 reports a current method, calls SetCurrentIM(pending). If fcitx5 reports NO current method (no input context / nothing focused), pending is RETAINED and polled every 50ms until a context appears.
  - Polls fcitx5 state every 500ms while the group has >1 method (follows per-app input contexts and trigger keys pressed inside apps).
- NOTE: cycle only changes the *pending* choice when nothing has focus; it applies when a text field gains focus.

## 16:37-16:38 - Live cycle tests (SSH, no focused window)
- 16:37:56 `omarchy-shell shell cycleInput next` WITHOUT OMARCHY_PATH: exit 1, stderr "OMARCHY_PATH is not set". (SSH env gap only, not a user-facing bug: Hyprland session sets it.)
- 16:38:14 with OMARCHY_PATH=/usr/share/omarchy: `omarchy-input-method cycle` took 0.007s, no error, but fcitx5-remote -n stayed "ngosen", state 2. Same after `cycle back`.
- Unresolved: did cycle apply and switch back, or did it only set pending (no focused window, so nothing to apply to)? Needs a focused-window test.
- NOTE: lotus-autostart.sh runs `fcitx5-remote -s lotus` then `-o`. Tested 16:37: `-s lotus` left current IM at "ngosen" (16:37, before/after identical). "lotus" is not a valid IM name here; that step is a silent no-op. The `-o` (activate) still works. Profile DefaultIM=ngosen is what actually loads.

## 16:41-16:45 - Live reproduction (run 2 + run 3)
- Run 2, 16:42:26: session ok, tab A focused (ngosen/2). wtype private helper HUNG, killed by 30s timeout. Textarea empty. Session deleted cleanly.
- Run 3, 16:44:07-16:45:23: baseline ngosen/2, indicator.py PID 3444 alive, quickshell PID 1646 alive.
  - 16:44:08 tabA focused ngosen/2. Private wtype TIMEOUT 12s, system wtype TIMEOUT 12s, value "".
  - 16:44:35 tabB focused ngosen/2. New tab did NOT reset the reported IM (H2 simple form REFUTED).
  - 16:44:47 tabB private wtype TIMEOUT 12s, system wtype TIMEOUT 12s, value "".
  - 16:45:00 cycle_next: 7ms rc 0, but im stayed ngosen/2. Switch NOT visible.
  - 16:45:12 private wtype "chaof banj" TIMEOUT 12s.
  - 16:45:21 system wtype "chaof banj" SUCCEEDED in 7398ms, im now keyboard-us/1, value "chaof banj" (literal, correct for keyboard-us). So the cycle_next switch landed ~21s late.
  - 16:45:21 cycle_back: 7ms rc 0, im stayed keyboard-us/2.
  - 16:45:23 private wtype " xin chaof" SUCCEEDED in 567ms, im ngosen/2, value "chaof banjhào bạn xin chaoào" (GARBLED: late/duplicate keystrokes delivered after the stall, corrupting Telex composition).
  - 5 wtype hangs total in the window 16:42:27-16:45:12, then recovery 16:45:21-23.
- 16:45:19 journal: xkbcomp "Virtual modifier multiply defined" warnings. Checked: 80 such warnings today, routine (every keymap compile), NOT a cause.

## 16:48 - Probe 2 (WAYLAND_DEBUG wtype, healthy state)
- wtype private helper: 129ms, rc 0, typed "ab", value "ab". Clean protocol trace: create virtual keyboard, keymap, key events with sync roundtrips, destroy. No hang.
- Conclusion: wtype works fine when healthy; the 16:42-16:45 hangs were a real transient stall, not a broken binary.

## 16:49 - Cycle latency measurement (healthy state)
- Start ngosen/2. Cycle returned in 12ms. At +209ms fcitx5-remote showed keyboard-us/1. Cycle back restored ngosen/2 in 1s.
- Healthy Super I lag is ~200ms. During the stall it was ~21s. Same command, 100x difference.

## 16:49 - Keyboard layouts + system state
- hyprctl devices: ALL keyboards layout "us" (single). So cycle_choice takes the simple fcitx5-method path; layout_switches / switchxkblayout never runs. Super I does not recompile keymaps.
- Notable devices: keyd-virtual-keyboard, ydotoold-virtual-device, hl-virtual-keyboard-fcitx5.
- No leftover wtype processes. Load average 1.78. Zen 13.7% CPU.
- Final state: IM ngosen/2, 22 Zen tabs open, 0 leftover worker-t tabs, Marionette sessions deleted.

## Open hypotheses (to test)
- H1: indicator.py reader dies / stalls -> Super+I dead until Quickshell restarts it (5s). Matches "Super I khong nhan" + "1 luc tu het".
- H2: ActiveByDefault=False + per-context state: new Zen tab / new text field starts with IM inactive (keyboard-us), user must toggle again. Matches "luc duoc luc ko".
- H3: Pending choice race: Super+I with no focus sets pending; typing before the 50ms poll applies it goes through as plain US.
- H4: Agent-driven Zen (Marionette/BiDi tab switches, new tabs) creates new input contexts -> IM off. This would explain the correlation with "AI-optimized Zen" without Marionette itself breaking the IM.
- H5: fcitx5-remote / dbus call timeouts (1000ms in indicator.py call()) under load.

## Status at 16:50 - DIAGNOSIS DONE
- H1 REFINED: reader was alive the whole stall (PID 3444); the failure is not the reader dying but the switch path stalling + pending silently cleared on dbus timeout. See diagnosis file.
- H2 REFUTED for reported state (new tab keeps ngosen); per-context activation still unproven, kept as Fix 4 experiment.
- H3 PROVEN in mechanism (cycle is async, ~200ms healthy, ~21s stalled); typing before it lands goes through the old method.
- H4 REFINED: Marionette/BiDi do not break the IM; the correlation is agent-driven context churn + typing competition, not the flags.
- H5 SUPPORTED: indicator.py clears pending on any GLib.Error from a 1000ms dbus call, silently losing the switch.
- Full diagnosis + fix proposal: improvements/worker-t-vietnamese-typing-diagnosis.md
