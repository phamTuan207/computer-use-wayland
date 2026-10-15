# Public benchmark evidence

Sanitized, portable aggregates. Each row is a measured task execution, not a
model-billing record. Raw run files stay private; their SHA-256 hashes are
embedded in the aggregates so the files stay identifiable without publishing
contents.

- `muse2_assertion_poll_aggregate.json` — 1,440 measured browser tasks
  (24 blocks x 60) plus 48 warmups, across 6 delay/control workloads and
  2 task routes. Blocks ran B,A,A,B, so the 1,440 rows are repeats under
  that order, not 1,440 distinct scenarios. Local owned live Chromium
  fixture, reviewed measurements, not a third-party independence claim.
- `muse1_historical_aggregate.json` — historical MUSE1 evidence: 180
  live-fixture task executions (120 Chromium + 30 GTK full + 30 GTK crop)
  plus 4 warmups, and 11 installed unit-test module executions totalling
  98 run / 98 pass. Historical source basis predates Round4; not Round4
  HEAD validation. Execution counts, not distinct test IDs; live fixtures,
  not unit mocks, for the 180.
- `r4_isolation_aggregate.json` — R4 FINAL measured isolation experiment:
  66 blocks, 870 measured rows plus 54 warmups. Desktop 36 blocks x 10
  (360 measured + 0 warmup, 3 cells); CDP normal 24 blocks x 20
  (480 measured + 48 warmup, 4 cells); CDP image 6 blocks x 5
  (30 measured + 6 warmup, exploratory, no gate). Per-row timings, JSON
  bytes, PNG bytes with dimensions (image) or null-absent (normal),
  runtime hashes, raw-file hash manifest, pooled/per-round summaries,
  seeded paired-block CI and fixed gate outcomes. Local owned fixtures,
  root local verification — not an external third-party claim.

Verify everything with the stdlib-only checker (no dependencies):

```sh
python3 scripts/check-perf-evidence.py
```

It recomputes all 24 pooled medians/p95 values, the 1440/48 counts with
correctness/cleanup flags, the embedded summary, the numbers quoted in
`docs/optimization-experiments.md`, the 180 + 98 historical counts, and the
full R4 aggregate (66 blocks, per-cell and per-round medians/p95, paired CI,
fixed gates). Root separately tests the actual checker against corrupted
artifacts; the checker does not maintain a second validation implementation.
