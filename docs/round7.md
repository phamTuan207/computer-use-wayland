# Round 7

Four review items, checked with mocked input/capture and temporary Git fixtures.
No live compositor or plugin build/load validation was performed in this round.

1. **Paint `failure_string` keeps its hash refresh.** The `failure_string`
   corruption in `tests/test_perf_evidence.py` refreshes the block hash before
   asserting rejection, so the exact `'R5 paint failure retained'` checker
   error (normal and `-O`) is what rejects — not a stale hash. The earlier
   missing-refresh claim against HEAD was wrong; HEAD already refreshed.
2. **H5: glass build dirt gate.** `scripts/build-glass.py` refuses dirty sources
   by default with `--allow-dirty` as the explicit bypass, checking
   `--untracked-files=all` on both status calls so
   `status.showUntrackedFiles=no` cannot hide untracked files. Own-patch dirt
   in the same run is permitted; reruns over it need the flag. Stamps
   `commit`/`initial_dirty`/`allow_dirty`/`build_dirty` trace every decision.
   Covered by mocked plus one real-git temp-fixture test; no real builds.
3. **N4: IME restore flag.** Desktop results may carry `ime_restore_failed: true`
   only when IME restoration actually failed. Stop, report the restoration failure, and
   never replay automatically. The flag also voids transient-refusal
   classification. Covered through the real `desktop_act` envelope for
   grouped and standalone (leading-dash) forms, plus compose/no-remote/cancel
   paths.
4. **H2: re-observe whitelist.** Exactly two refusals preserve a session when no capture, cleanup or IME error accompanies them —
   `screen changed`/`screen_changed` and `focus changed`/`focus_changed`.
   After either, run an explicit `observe` and use only its fresh path; stale
   paths stay blocked and everything else (including cancel) ends the task.
   Markers persist per token across CLI processes; no auto retry, resume, or
   focus restore.
