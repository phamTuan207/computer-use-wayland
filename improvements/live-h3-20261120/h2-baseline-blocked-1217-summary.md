# H2 JPEG q90 BASELINE-arm run report

- Verdict: BLOCKED at setup step 1. No benchmark task was started.
- Run directory: `/tmp/speed-jpegq90-20261120/h2-baseline`. It already contained `brief.md`, `timed.py`, and `codex.log` when checked.
- Required baseline HEAD: `8727135`.
- HEAD observed at initial broker status: `56f5af4e521e1c20b26b56dc31d662e34f1c2668`. No checkout was attempted.

## Setup gate

The required starting broker state was `idle` with `owner: null`. The first status showed `state: finished`, `owner: h3method-r2`, `driver: stopped`, and `guardian: clean`. I rechecked after 10 seconds and after another 30 seconds; both results were unchanged. The broker was not started, restarted, or otherwise modified.

Per the stop-on-failure instruction, setup steps 2 through 7 were not run. No git status or stash was made, no log backup or md5 was made, no relay restart or PNG source check was made, no GUI or terminal was launched, and no benchmark task or T1-T3 observation was made.

## Broker checks

Three `python3 scripts/session_remote.py status` checks returned the same relevant values:

| Check | state | owner | driver | guardian | started_git_head |
|---|---|---|---|---|---|
| Initial | finished | h3method-r2 | stopped | clean | 56f5af4e521e1c20b26b56dc31d662e34f1c2668 |
| Recheck after 10 seconds | finished | h3method-r2 | stopped | clean | 56f5af4e521e1c20b26b56dc31d662e34f1c2668 |
| Recheck after another 30 seconds | finished | h3method-r2 | stopped | clean | 56f5af4e521e1c20b26b56dc31d662e34f1c2668 |

## Task results

| Task | Wall | Think | Service | Calls | Image bytes | encode_ms | Refusals | Misclicks | Deaths | Result |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| P1 | N/A | N/A | N/A | 0 | 0 | N/A | 0 | 0 | 0 | Not run |
| P2 | N/A | N/A | N/A | 0 | 0 | N/A | 0 | 0 | 0 | Not run |
| P3 | N/A | N/A | N/A | 0 | 0 | N/A | 0 | 0 | 0 | Not run |
| P4 | N/A | N/A | N/A | 0 | 0 | N/A | 0 | 0 | 0 | Not run |
| T1-T3 | N/A | N/A | N/A | 0 | 0 | N/A | 0 | 0 | 0 | Not run |

No observation image exists, so there is no first observation filename, image format, file extension, or Tesseract output to report. There are no observed reads or ground-truth comparisons for P1-P4. No T3 target was selected.

## Teardown and restore

No broker session or test terminal was created. No cleanup or restore operation was needed or attempted. The relay was left as found. Stash status and log md5 are not applicable because setup step 2 was not reached. Desktop windows were not inspected.

## Remaining work

The run can proceed after the broker status meets the required gate: `state: idle`, `owner: null`. Then restart from setup step 1 and complete the full baseline run.

This report was written at 2026-11-20 12:17:02 +07 Asia/Ho_Chi_Minh time.
