# Worker V implementation log: Vietnamese typing council + fixes
# All times wall-clock Asia/Ho_Chi_Minh, 21/11/2026. Started ~17:24 (council
# convened), implementation 17:31-17:40. Repo: computer-use-wayland, todolist-push.

## Council phase
- 17:24: read T's diagnosis + log fully (commit 029cb9b).
- 17:24: spawned 4 subagents in parallel: Council A (Fix 2), Council B
  (Fix 3 + Fix 5), Council C (Fix 4 + diagnosis audit), Redteam (all).
- 17:27: Council B done (Fix 5 IMPLEMENT NOW, Fix 3 IMPLEMENT LATER).
- 17:27: Council A done (Fix 2 split: 2a IMPLEMENT NOW corrected, 2b REJECT
  as specified, IMPLEMENT NOW with -s target).
- 17:28: Council C done (Fix 4 REJECT, diagnosis SOUND WITH GAPS).
- 17:29: Redteam done (ship nothing as specified; redesigned set proposed).
- 17:31: read all 4 verdict files in full, synthesized the decision.

## Implementation phase
- 17:31: read indicator.py live (322 lines). Verified all three clear sites,
  1000ms timeout, 50/500/2000ms polling.
- 17:32: wrote patched indicator.py in repo (retain pending, 30s TTL,
  backoff, rate-limited file+stderr log, re-snapshot failure handling).
  py_compile OK. Diff reviewed (134-line patch file).
- 17:32: installed on laptop with sudo (backup original + patched copy at
  ~/.config/agent-computer-use/patches/). Killed reader PID 3444, new PID
  159243 up. Old-path cycle test: ngosen to keyboard-us to ngosen, pass.
- 17:33: wrote wrapper omarchy-input-method-switch (explicit -s target,
  flock, timeouts, notify-send, marker file). Installed, syntax OK.
- 17:33: direct wrapper test: 20/20 flips, landed=1, 8-10ms each.
- 17:33: rebound Super I + Super+Shift+I in ~/.config/hypr/bindings.lua
  (user config). hyprctl reload ok. hyprctl binds shows exactly one bind
  per description, no duplicates.
- 17:34: wtype Super I test INCONCLUSIVE (wtype presses do not trigger
  Hyprland binds, proven with a registered SUPER+F9 marker bind that never
  fired). One unexplained single flip ngosen to keyboard-us during wtype
  testing, not reproduced in 3 later presses. Live physical press test
  still owed by the owner. F9 test bind removed after the test.
- 17:34: restored IM to ngosen.
- 17:36: monitor service enabled and started. Read probes 3-4ms rc 0.
- 17:38: first cycle probe 17:38:29, flip_ms 117, landed 1, restored ngosen.
- 17:38: Fix 1 completion: lotus comments fixed (script + autostart.lua),
  marker line added. Script run live, marker written, IM=ngosen.
- 17:38: re-apply hook installed at
  ~/.config/omarchy/hooks/post-update.d/reapply-indicator-patch.hook.
  Syntax OK, dry run exit 0, no re-apply needed (patch present).
- 17:39: dead-reader drill: reader killed (PID 165470), wrapper flipped
  ngosen to keyboard-us in 8ms during the dead window, reader restarted
  (PID 165692), state consistent. PASS.
- 17:39: double-press drill: sequential double returns to original;
  concurrent double gives exactly one flip (flock works, log proves it). PASS.
- 17:39: IM left at ngosen. Monitor active, logging every 30s.

## Known open items (not hidden)
- Live physical Super I press test: owed by the owner (wtype cannot test binds).
- Unexplained single IM flip during wtype testing (17:34, ngosen to
  keyboard-us, once, never reproduced). Recorded, not attributed.
- Fix 3: IMPLEMENT LATER, gated on Fix 5 capturing a stall + a manual restart
  proving it clears faster than self-clear.
- Fix 4: REJECTED. Revisit only on a distinct symptom.
- A6 (async dbus in indicator.py): IMPLEMENT LATER, the proper fix.
- wtype stall itself: no fix proposed; Fix 5 monitor is the path to one.
- Fix 1 F1-4: whether -s ngosen does anything at login with no focused
  window is still untested; the marker proves the script ran, not that -s
  changed state (DefaultIM is the real guarantee).
