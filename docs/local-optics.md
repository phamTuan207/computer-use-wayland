# Accepted local optical profile

Build the pinned Hyprglass source with `scripts/build-glass.py --local-optics SOURCE`.
This selects `native/hyprglass-local-optics.patch`; do not combine it with the
alternative capsule patch. The BSD-3-Clause notice is in native/hyprglass-LICENSE.

The upstream refraction formula is retained. Geometry, direction and bezel scale
use the indicator's glass region instead of its transparent shadow padding.
The region is rounded integer scanlines: its modeled bounding box is 286 by 38,
slightly narrower than the drawn 288 by 38 pill. Pixel-perfect alignment is not
claimed. All other layers keep their upstream full-box sentinel behavior.

The separate `native/hyprglass-local-optics.lua` profile removes tint, noise and
adaptive dimming. It uses stronger edge refraction with a weak interior lens.
Build and 199 Python tests passed (20.848 seconds, one optional skip). A real
nested compositor rendered moving lake content through the candidate; cache
misses advanced from 19 to 38 and the interior changed. After hiding the pill,
its expanded shadow crop matched the clean baseline pixel-for-pixel. Presentation
acknowledgments were 9.0–14.0 ms; these are not GPU timings or FPS measurements.
Appearance is the user-accepted local profile; it is not claimed identical to a
browser reference with different dimensions and background sampling. The numbers
above are nested-compositor measurements, not GPU timings or FPS.

## Final accepted build and activation

This overlay is **Hyprland-specific**, not generic Wayland: it needs Hyprland
0.56.2, the Hyprglass plugin built against that exact ABI, `wp_presentation`, the
layer-shell protocol and `ext-background-effect-v1`. Generic Wayland compositors
do not provide the plugin host or these staging protocols.

1. Choose empty source and existing install directories (`SOURCE` and `DEST`).
   Check out the **Hyprglass source pinned for Hyprland 0.56.2**:
   `git clone https://github.com/hyprnux/hyprglass.git "$SOURCE"` and
   `git -C "$SOURCE" checkout 84c1a5ab217101a317d4edaab7fba2efcc1bf346`.
2. Build the accepted profile: `scripts/build-glass.py --local-optics "$SOURCE"`.
   (Do not combine it with the alternative capsule patch; that stays experimental.)
3. Publish immutably: `scripts/install-glass.py "$SOURCE/hyprglass.so" "$DEST"` writes a
   hash-named `.so` and never loads it or overwrites a running module.
   Copy `native/hyprglass-local-optics.lua` into `$DEST/native/` separately;
   the installer publishes the library only, not the profile or CLI.
4. Activate only in a **fresh login** (never hot-swap a loaded plugin), then load
   the matching profile generically: `hl.plugin.load("<DEST>/hyprglass-<sha>.so")`
   followed by `dofile("<DEST>/native/hyprglass-local-optics.lua")`.
5. Keep the previous immutable module as rollback.

This document is the accepted overlay profile. The alternative capsule/ink paths
and the older experimental material notes remain as experiments, not defaults.
