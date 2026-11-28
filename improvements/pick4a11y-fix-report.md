# Pick 4 a11y fix report

Owner: the owner. Branch: `speed-swarm-pick4a11y`, based on `0fd2b72`. Verdict: PROVISIONAL, non-Astra.

## Findings

**Layer 1, broker allowlist: NOT REPRODUCED on current code.** `scripts/session_remote.py:41` includes `a11y` in `COMMANDS`, and `_validate_envelope()` checks that set at `scripts/session_remote.py:348-357`. The session driver also allows `a11y` at `scripts/session_driver.py:117-118`. An isolated in-process `Broker.handle()` run with the exact G1 query and observe envelopes, plus a ground envelope, accepted all three through status, start, request, and result using a mock driver. A non-allowlisted `rm` request returned `unsupported_command` and did not consume sequence 4. The regression is in `tests/test_session_remote.py:384-422`. The G1-time rejection remains unexplained: that relay process is gone and the rejected request has no retained log. No allowlist change or speculative cause was added.

**Layer 2, a11y ground coordinate frame: REPRODUCED and fixed.** The prior `scripts/a11y.py:160` returned `_component_extents(root)` directly. An AT-SPI application object without a Component interface therefore returned `root_extents: null`. Then `scripts/cu.py:2310-2311` selected `unknown`, and `scripts/fastpath.py:72-74` raised `cannot tell whether extents are screen or window relative; use vision`. The recorded Nautilus probe has a window at `[3448,1509,924,581]`, window-relative element extents starting at `[0,0]`, and this exact ground error (`/tmp/speed-pick4-20261118/probe/probe.log`).

`scripts/a11y.py:158-173` now prefers app-root extents, then checks at most 100 direct children and uses the first child with Component extents. If none has extents, it raises `no window frame extents; use vision`. The extents coordinate label is not used to choose the frame. The `CU_PICK4_FASTPATH=1` gate, 90 second staleness check, `resolve()` checks, and fail-closed `cu.py` coordinate conversion remain unchanged.

## Tests and dry run

- `test_pick4_fastpath.py`: 23 tests passed. Coverage includes frame-child fallback, no-frame failure, app-root extents, flag-off behavior, and the mocked Nautilus CLI path.
- `test_session_remote.py`: 49 tests passed. The new Broker regression accepts query, observe, and ground, and keeps `rm` rejected.
- Full suite before source changes, 2026-11-19 08:05:54 to 08:07:35 +07: 1287 tests, 9 failures, 66 errors, 2 skipped. Full suite after changes, 2026-11-19 08:17:12 to 08:18:54 +07: 1292 tests, 9 failures, 66 errors, 2 skipped. The added five tests pass. Sorted FAIL diff: `[]`. Sorted ERROR diff: `[]`. The before and after sorted-list signature is identical: `55a97610fc0c6e17a06de8cc32f66df8ab9b000445f8c13a80e2f956864fb70b`. The suite exits 1 because the same existing failures and errors remain.
- Mocked cu.py ground dry run, with no broker and no desktop: `coord_frame: window`, box `[3448,1509,184,535]`, center `[3540,1776]`, crop `[0,67,208,400]`, inside the `[924,581]` window.

## Commits and follow-up

Pushed to `origin/speed-swarm-pick4a11y`:

- `8c683ca` test: reproduce Pick 4 a11y frame fallback
- `70c8a44` fix: fall back to a11y window frame extents
- `4c2118a` test: pin broker a11y command acceptance

A live G1 Nautilus re-probe against this branch remains for the coordinator after the broker is free. No live Nautilus, broker session, relay restart, or desktop window action was used for this fix.

Final read-only `hyprctl --instance ... -j clients` check found Jarvis and Zen only in the active instance. No kitty or Chromium client appeared in that listing. No window was launched, focused, or closed.
