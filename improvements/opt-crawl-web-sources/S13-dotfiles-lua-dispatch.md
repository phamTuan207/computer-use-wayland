# S13. Dotfiles history, July 2026: Hyprland 0.55 Lua dispatch breakage

- Class: (e) Hyprland workspace switching and app-launcher opening by command vs mouse click
- URL: https://dotfiles.v1cferr.dev/history/2026/07-july/
- Accessed: 2026-11-21
- Crawler: OPT-WEB, 2026-11-21 22:52 +07

## What they did

Documented, with live debugging, that Hyprland 0.55 changed `dispatch` into a shortcut for `hl.dispatch(...)`, so the old string form `dispatch workspace 3` builds `hl.dispatch(workspace 3)` and dies in the Lua parser. The click died silently because Quickshell execDetached hides stderr. Correct form: `hl.dsp.focus({ workspace = N })`. Also notes `hl.dsp.workspace(N)` fails ("attempt to call a table value") because it is a table of sub-dispatchers, not a function. Separately: `hyprctl -i 0` finds the Hyprland instance from any shell, fixing SSH reloads that silently never applied because HYPRLAND_INSTANCE_SIGNATURE was missing.

## Evidence shown

Dated log entries, exact error strings, the working form verified by the author. No timing numbers.

## Applicability verdict: APPLIES

This independently confirms our local Hyprland 0.57.2 Lua lesson (hl.dsp object form, never the string form) and adds two things we should adopt: (1) any dispatch path must surface stderr, because a silent failure is the failure mode (our driver should capture hyprctl stderr on every call and log it); (2) `hyprctl -i 0` is the correct invocation from SSH or any shell without the instance signature in the environment, which matters for our VM-to-laptop SSH path. The workspace-switch-by-click path (clicking a bar pill) is exactly what broke here, which supports preferring hyprctl dispatch over mouse clicks for workspace moves.
