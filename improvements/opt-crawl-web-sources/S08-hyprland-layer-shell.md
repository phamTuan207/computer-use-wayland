# S8. Hyprland issue 15738: layer-shell overlay not rendered on first invocation cycles

- Class: (c) overlay and pill flicker or visibility failures on Wayland and Hyprland
- URL: https://github.com/hyprwm/hyprland/issues/15738
- Accessed: 2026-11-21
- Crawler: OPT-WEB, 2026-11-21 22:51 +07

## What they did

Reported, not fixed. A gtk-layer-shell overlay (Handy speech-to-text app, Tauri/GTK) is not rendered by Hyprland during the first several invocation cycles, then appears after about 5 triggers and works persistently until restart. The surface exists and receives events (mic-level events in logs), it is simply not painted. Same class of bug existed on KDE Plasma and was fixed in the app repo, not the compositor.

## Evidence shown

Reproduction steps, Hyprland 0.56.1, gtk-layer-shell 0.10.1, about 5 cycles to first paint, reset on restart. No fix, no workaround except HANDY_NO_GTK_LAYER_SHELL=1, which falls back to a regular always-on-top window and loses layer-shell anchoring (overlay centers instead of bottom edge).

## Applicability verdict: NO PUBLISHED FIX

This is the closest public report to our pill visibility failures, and it is an open issue with no compositor fix. What it gives us is a diagnosis pattern and a fallback shape: (1) "surface exists, events flow, compositor does not paint" is a known Hyprland layer-shell failure mode, so our pill going invisible is plausibly compositor-side, not a bug in our overlay code; (2) the working fallback is a regular always-on-top window instead of a layer-shell surface, at the cost of anchoring, which is a fallback we can implement if the pill stays invisible; (3) the "works after about 5 triggers" detail suggests a warm-up or first-commit race, so a fix attempt is to force an early commit or a dummy show/hide cycle at startup. No published numbers on flicker rate or a verified fix exist for this class in the sources found.
