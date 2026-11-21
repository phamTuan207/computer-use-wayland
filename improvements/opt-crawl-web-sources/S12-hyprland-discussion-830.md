# S12. Hyprland discussion 830: get open windows list

- Class: (e) Hyprland workspace switching and app-launcher opening by command vs mouse click
- URL: https://github.com/hyprwm/Hyprland/discussions/830?sort=new
- Accessed: 2026-11-21
- Crawler: OPT-WEB, 2026-11-21 22:51 +07

## What they did

Community pattern for listing and switching windows without a mouse: read `hyprctl -j clients`, pick a window, then `hyprctl dispatch focuswindow address:<addr>`; close with `closewindow address:<addr>`; move with `hyprctl --batch "dispatch focuswindow address:<addr>; dispatch movetoworkspace <ws>"`. Launcher side: pipe the list through wofi/rofi dmenu and exec the dispatch for the chosen line. Maintainer answer: xlsclients is X11-only, use `hyprctl clients`, and `hyprctl dispatch focuswindow <window>`.

## Evidence shown

Working scripts (perl and shell), no timing numbers. The pattern is the community standard, not a benchmark.

## Applicability verdict: APPLIES

This is the command-side answer to our class (e): workspace and window switching by hyprctl is the supported path, and the address-based focus (not title or index) is the robust identifier because titles change and indices shift. For our driver, window switching should be `hyprctl -j clients` to resolve the address, then `focuswindow address:...`, never a mouse click on a workspace pill, and never a title match. The launcher side (rofi/wofi dmenu) is the human path; our agent path should skip the launcher UI entirely and dispatch directly.
