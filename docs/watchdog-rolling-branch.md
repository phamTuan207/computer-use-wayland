# Watchdog rolling branch (M28a, append-only form)

Status: mechanism implemented and scratch-tested 2026-11-27.
No live cron or watchdog configuration is changed by this item;
switching a lane over is a separate coordinator decision.

## Why

Before this item, every watchdog tick created its own branch
and its own PR. The bottleneck study (2026-11-27) counted
2,001 watchdog commits of 4,732 total (42 percent), 1,017
watchdog PRs of 1,109 (92 percent), and 706 watchdog branches
on the remote. One lane's 476 watchdog PRs are all still open
and its log file on main has been frozen since 2026-11-23, so
the only complete copy of that record is scattered across
hundreds of unmerged branches.

M28a replaces the per-tick branch and PR with one rolling
branch per lane. Only the append-only form was adopted; the
force-updated variant was rejected because a force-updated
branch is a rewritable audit record. Watchdog auto-merge
(M28c) was also rejected.

## The mechanism

- One branch per lane: `watchdog/<lane>` (for example
  `watchdog/clone2`). The namespace was verified free on the
  remote before this item.
- One file per tick on that branch:
  `entries/<utc-timestamp>-<lane>-<rand>.md`. Unique filenames
  are what make concurrent appends conflict-free.
- Appends are made by `scripts/watchdog_append.py` using git
  plumbing (temp index, `commit-tree`), so the caller's working
  tree and index are never touched.
- Pushes are plain fast-forward pushes. The script has no
  force-push path, and published history is never rewritten:
  every append adds exactly one commit on top of the current
  tip.
- A material flag (stall, dead lane, anything that today would
  get attention) still gets a PR exactly as today. The rolling
  branch only replaces the routine per-tick ceremony.
- A periodic rollup PR lands the log on main: run the `rollup`
  subcommand to concatenate all entries in order, commit the
  result as the lane's log file on a normal branch off main,
  and open a PR. The rolling branch itself is never merged; it
  stays the durable append-only record. Branch cleanup (M33)
  stays sequenced strictly after the record is durable here.

## Concurrency behavior (tested)

Two writers appending at the same time both build on the tip
they fetched. The first push wins; the second is rejected as
non-fast-forward. The script then re-fetches the new tip,
rebuilds its commit on top (the entry filename is unique, so
nothing conflicts), and retries, up to `--retries` attempts
(default 5). The scratch test
`tests/test_watchdog_append.py` runs two clones appending five
entries each in parallel: all ten entries land, the history
stays linear, and every earlier tip remains an ancestor of
every later tip. If all retries are exhausted the append fails
loudly with a non-zero exit and the entry text stays with the
caller; nothing is dropped silently.

## Personal data rule

Watchdog entries are status summaries only. They must never
carry raw personal data: no names of private individuals, no
addresses, emails, phone numbers, credentials, tokens, private
URLs, or machine secrets. The append script enforces what it
can mechanically: before committing, it runs
`rung3-ci/pii-scan.py` over the entry and refuses the append on
any hit. The scanner is a floor, not a guarantee; the writer of
an entry is responsible for keeping personal data out in the
first place.

## Usage

Append one tick (entry text on stdin or via `--entry-file`):

    python3 scripts/watchdog_append.py append --lane clone2 \
        --repo . --entry-file entry.md

Build the rollup file for the periodic PR to main:

    python3 scripts/watchdog_append.py rollup --lane clone2 \
        --repo . --out docs/clone2-watchdog-log.md

## What this item does not change

- No cron, watchdog, or lane configuration is touched.
- Existing per-tick branches and PRs are left as they are.
- M28d (exempting mechanical log appends from the small-commit
  rule) is a separate guidance item, not part of this change.
- Savings are stated in counts only, per the study: about 476
  PR creations per lane per period and about 90 percent of
  watchdog commit ceremony. No minute saving is claimed. A
  one-week count comparison against the 300-430 per day
  baseline is the post-adoption check.

No personal info in this document.
