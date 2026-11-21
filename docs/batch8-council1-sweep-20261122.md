# Batch 8 sweep, council 1: counts, timings, flags, install section

Date of check: 2026-11-22. Method: first-hand parsing of the three raw
JSONs with python3, reading the three timing.txt and stderr.log files,
stat birth times of the save dirs, and reading the clone on disk.
Report checked: docs/clone1-last30days-sweep-20261122.md, 453 lines
by wc -l, 0 em/en dashes. Every number below was re-read from an
artifact, not trusted from the report.

## 1. Run counts, timings, exit codes, sequence: all CONFIRMED

Kept results parsed from the raw JSONs:

- run1-dom/dom-grounding-for-computer-use-gui-agents-raw.json: 10
  results, generated_at 2026-11-21T22:50:23.692157Z,
  freshness_verdicts [], source_status github ok, grounding
  unreachable, hackernews ok, reddit unreachable.
- run2-a11y/accessibility-tree-grounding-for-gui-agents-raw.json: 9
  results, generated_at 2026-11-21T22:50:49.663767Z,
  freshness_verdicts [], source_status github ok, grounding ok,
  hackernews ok, reddit no-results.
- run3-multi/single-observation-multi-action-browser-agents-raw.json:
  14 results, generated_at 2026-11-21T22:51:14.251695Z,
  freshness_verdicts [], source_status github no-results, grounding
  ok, hackernews ok, reddit no-results.

Total 33, matching the report. All three JSONs carry window_days 30
and schema_version 1.4, and their query fields match the three
planned topics exactly.

Timing.txt files:

- Run 1: START 2026-11-21T22:50:11Z, EXIT:0, END 22:50:23Z,
  elapsed_shell_s=12.
- Run 2: START 22:50:38Z, EXIT:0, END 22:50:49Z, elapsed_shell_s=11.
- Run 3: START 22:50:58Z, EXIT:0, END 22:51:14Z, elapsed_shell_s=16.

Engine-reported times in the stderr.log "Research complete" lines:
12.2 s, 10.9 s, 15.1 s, matching the report table. Per-source
pre-filter counts in those lines also match: run 1 (Reddit 0, HN 9,
Web 0, Github 1), run 2 (Reddit 0, HN 5, Web 5, Github 1), run 3
(Reddit 0, HN 12, Web 4, Github 0). Kept per-source counts parsed
from the JSONs confirm the report's pre-filter note: run 2 keeps 3
of 5 HN stories (9 kept = 3 HN + 5 grounding + 1 GH), run 3 keeps
10 of 12 HN stories (14 kept = 10 HN + 4 grounding), run 1 keeps
all 9 HN + 1 GH.

Sequential, not parallel: the three wall windows (22:50:11-22:50:23,
22:50:38-22:50:49, 22:50:58-22:51:14) do not overlap, and the
timing.txt birth times (22:50:11.115Z, 22:50:38.358Z, 22:50:58.809Z)
confirm the same order. All three runs exit 0.

Save-dir birth times (stat): run1-dom, run2-a11y and run3-multi
were all created at 22:49:57.797Z. The report section 2 says the
run2 and run3 dirs were created at 22:49:57Z and run 1 started at
22:50:11Z. CONFIRMED, with the small precision note in M2 below
that run1-dom shares the same 22:49:57Z birth time.

"Research quality: 3/4 core sources." appears in all three
stderr.log files, so the report quotes the engine faithfully. Note
(M3): run 1 source_status shows only 2 sources "ok" (github,
hackernews) while the engine still prints 3/4, so the 3/4 is the
engine's own figure, not a plain count of ok statuses. No
correction needed; the report does not derive it independently.

## 2. Flags used: PARTIALLY VERIFIED

- --emit=json: CONFIRMED. All three runs produced JSON output
  files (*-raw.json) plus stdout.log copies of the same JSON.
- --auto-resolve (no --plan): CONFIRMED. All three stderr.log
  files contain the [Planner] "No --plan passed" note and then the
  deterministic fallback plan: intent=concept,
  freshness=evergreen_ok, cluster_mode=none, subqueries=1,
  sources [reddit, hackernews, github, grounding], one subquery
  per run with the exact planned topics. The note in the logs was
  not acted on here; this check only records that no --plan was
  passed and the fallback planner ran.
- --no-browser-cookies: NOT VERIFIED by surviving artifacts. No
  log or JSON field records the cookie setting either way. The
  report attributes the invocation to a live `ps` observation,
  which cannot be re-observed now that the processes are gone.
- Keyless (no API keys): NOT VERIFIED by surviving artifacts. The
  raw JSONs carry usage None and no keyed source returned data,
  which is consistent with keyless, but no artifact records the
  run environment's key configuration.

Conclusion on flags: the two flags provable from artifacts are
confirmed; the other two rest on the report's `ps` observation
and cannot be independently re-verified now. This does not change
any finding, since the source_status outputs are consistent with
keyless, cookies-off runs.

## 3. Install section (section 1): all CONFIRMED

Checked in ~/workspace/tools/last30days-skill:

- HEAD ef01dab92d8ef0da673b18e7f90d69fde77c495b, message
  "feat(tiktok): free top comments for every kept TikTok from the
  public comment endpoint (#1555)". CONFIRMED.
- SKILL.md version "4.5.0" at skills/last30days/SKILL.md line 3.
  CONFIRMED.
- Commit f5d0e44 exists as the parent ("fix(comments): spend
  TikTok and Instagram comment calls on posts the report keeps
  (#1554)"). Diff f5d0e44..HEAD: 7 files changed, 238 insertions,
  7 deletions. CONFIRMED by git diff --stat.
- TikTok public comments endpoint literal
  `_PUBLIC_COMMENTS_URL = "https://www.tiktok.com/api/comment/list/"`
  at skills/last30days/scripts/lib/tiktok.py line 666. CONFIRMED
  by direct read. `is_tiktok_public_comments_on` defined at
  skills/last30days/scripts/lib/env.py line 2045. CONFIRMED.

~/.config/last30days exists with exactly the files the report
names: last-report.json 110,612 bytes, last-run.json 316 bytes,
last-report.lock 0 bytes, reddit-health.json 192 bytes. CONFIRMED.

User confirmation record: coord/clone1.md line 3497 records the
05:49 +07 on 2026-11-22 confirmation, matching section 2 of the
report. CONFIRMED as a record; the chat tap itself is outside
what disk artifacts can show.

## 4. Numbers in sections 0-2 with no surviving artifact

- "Clone took 55.7 s real", "Date check before the clone:
  2026-11-21T21:42:40Z", "First report written
  2026-11-21T21:45:46Z": NOT VERIFIED by any surviving artifact.
  They appear verbatim in the earlier committed version of the
  report (commit fd250da, lines 31-33), and that version was
  committed at 2026-11-21T21:47:27Z, which is consistent with a
  21:45:46Z write time, but no log or timestamp file proves the
  three numbers themselves.
- "Memory at the pre-run check (22:50 UTC): 155 MB free, 665 MB
  available; after the runs (22:53 UTC): 175 MB free, 508 MB
  available": NOT VERIFIED. No memory log exists on disk.

## Minor observations

- M1: an empty fourth save dir exists at
  ~/workspace/b8t1-sweep/run3-single-obs, birth 2026-11-21
  22:50:09.342Z, 0 bytes, created 2 seconds before run 1 started
  and after the three run dirs (22:49:57Z). The report does not
  mention it. It holds no data, so it changes nothing, but one
  line acknowledging it would close the gap.
- M2: section 2 says the run2 and run3 save dirs were created at
  22:49:57Z. All three dirs share birth 22:49:57.797Z, including
  run1-dom. The statement is true for the two named dirs but
  omits that run1-dom was created at the same instant.
- M3: see section 1. The engine's "3/4 core sources" figure is
  quoted faithfully but is the engine's own counting, not a plain
  count of ok statuses in source_status (run 1 has only 2 ok).
  No correction needed.

## Verdict

Sections 0-2: CONFIRMED on every number that has an artifact
behind it (result counts 10/9/14, wall times, engine times
12.2/10.9/15.1 s, shell times 12/11/16 s, exit 0, sequential
order, generated_at values, freshness_verdicts empty,
source_status per run, pre-filter versus kept counts, HEAD
ef01dab, SKILL.md 4.5.0, diff 7 files 238+/7-, TikTok literal at
tiktok.py:666, env.py:2045, ~/.config/last30days file sizes).
PARTIALLY VERIFIED on the flags (--emit=json and --auto-resolve
proven from artifacts; --no-browser-cookies and keyless rest on
the unrepeatable `ps` observation). NOT VERIFIED on four
historical numbers with no surviving artifact (55.7 s clone,
21:42:40Z date check, 21:45:46Z first report, memory figures).
No wrong fact found in sections 0-2 that changes any conclusion.
M1-M3 are minor gaps, not corrections to findings.
