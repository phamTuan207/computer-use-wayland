# probes/

Working layer for measurement probes: small scripts that answer
one question about this system by running something, plus the
ledger that records what they found.

## Rules

- A probe is a script that measures or checks one thing and
  prints its result. Name new probes `YYYYMMDD-<slug>.py`
  (or `.mjs`/`.sh` when the probe needs that runtime).
- Every probe run that informs a decision gets a row in
  `ledger.jsonl`. A ledger row must cite the probe output:
  either a repo path holding the output, or the output inline
  in the `output` field when it is short.
- Ledger row fields: `date` (YYYY-MM-DD), `probe` (path or
  short name), `question`, `result` (the measured numbers or
  the observed behavior), `output` (citation), `verdict`
  (what was decided from it).
- Historical probes that live elsewhere (improvements/,
  docs/) are indexed in the ledger by path; they are not moved,
  so old report links keep working.
- Advisory A/B comparisons are allowed and non-blocking. There
  is no mandatory merge-base A/B gate and no baseline store
  until a real CI runner exists (rejected half of I8: min-of-N
  on a noisy shared VM is not a gate). Public aggregates, when
  a probe matures into one, go to docs/benchmarks/.

Validate the ledger with `python3 probes/validate-ledger.py`.

No personal info in this directory.
