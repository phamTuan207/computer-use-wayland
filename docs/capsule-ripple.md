# Capsule rim and ripple candidate

Reference: https://github.com/dashersw/liquid-glass-js/blob/main/container.js

The reference separates exponential rim refraction from a tangential sinusoidal
ripple. Lower rim decay widens the effect; rim intensity is displacement, not
Fresnel brightness. This implementation independently adapts those concepts to
pixel-space sampling, rather than copying page-texture UV amplitudes.

Capsule-only shader constants: added radial intensity 2.4 px, inverse-distance
decay 0.24 per pixel, ripple amplitude 1.2 px. The ripple phase uses distance to
the edge divided by pill height, multiplied by 25. It has no time animation or
random noise. Both additions fade with the surface normal at the cylinder axis.
These are compile-time candidate values, not new runtime configuration options.
The existing interior dome, transparent tint and blur settings are unchanged.

Validation: native plugin build passed; 195 Python tests passed in 20.786 s,
with one optional skip. A separate real nested compositor compiled the shader
and rendered static ruler and moving-background fixtures. The moving interior
changed with the background; after hiding the indicator, the expanded pill and
shadow crop was pixel-identical to the clean baseline in both fixtures.
Hide/show presentation acknowledgments ranged from 9.6 to 14.0 ms in those runs.
These are acknowledgment timings, not GPU execution timings or FPS measurements.

The running host plugin was not replaced, unloaded, or reloaded. This candidate
still needs visual acceptance and a fresh-session activation before it becomes
the host desktop effect. The appearance is not claimed to match the reference.
