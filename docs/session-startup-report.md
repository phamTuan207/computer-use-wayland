# Session startup report — superseded 2026-10-09

The previous startup report described a now-removed screen magnifier and a gate
requiring consecutive identical captures. It incorrectly treated screen zoom as
an enlarged cursor. Its approximately 25-capture settlement cost was caused by
rescaling the desktop and is not a requirement of automation sessions.

Both the magnifier and the gate are deleted. Startup now only establishes the
session token, best-effort Escape cancellation and driver process-group handshake.
Each action still runs the original focus, geometry and image preflight checks.

Current evidence, numbers and limitations are in
[indicator-removal-report.md](indicator-removal-report.md); current lifecycle and
crash recovery are in [automation-cursor-design.md](automation-cursor-design.md).
Do not use the old settlement measurements to describe current startup behavior.
