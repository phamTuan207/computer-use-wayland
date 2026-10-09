# Performance report — current scope, 2026-10-09

The synthetic startup-settlement benchmarks were removed with the magnifier and
its quiescence gate. Historical timings for that gate do not describe current
startup. `tests/performance.py` still measures Python startup/import, CLI help and
status, and image comparison on synthetic images; it does not touch the desktop.

The global image check remains necessary: the synthetic case changing a large
region outside a target's 49x49 patch is rejected by the full guard and missed by
a patch-only guard. No image thresholds were loosened to improve timings.

See [indicator-removal-report.md](indicator-removal-report.md) for the five suite
results and real-desktop before/after observe and session timings. The magnifier
removal affects session startup; observe still performs the same actual capture.
