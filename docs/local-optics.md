# Upstream local optical candidate

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
Appearance still needs user acceptance; it is not claimed identical to a browser
reference with different dimensions and background sampling.

Publish a tested binary with `scripts/install-glass.py SOURCE DIRECTORY`.
The installer uses an immutable hash-named path and never loads the plugin.
Never overwrite, unload or hot-swap a running compositor plugin. Activate the
new path only in a fresh login, followed by the matching Lua profile. Preserve
the previous immutable module as a rollback option.
