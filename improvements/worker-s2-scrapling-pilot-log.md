# Worker S2: Scrapling pilot log

Sat 2026-11-21 ~21:24-21:30 +07, VM. Pilot crawl only: Fetcher-only Scrapling
over Hacker News front page + top threads + GitHub trending, max 50 pages,
public data only, no login, no evasion. No live Zen slot touched.

## 0. Setup

- Venv from S1: ~/workspace/scrapling-trial-venv, scrapling 0.5.1, Python 3.12.3.
  Verified at start: `python -c "import scrapling; print(scrapling.__version__)"`
  printed 0.5.1. Repo on branch todolist-push at e700c97 (S1).
- Script: improvements/s2-pilot.py (written 21:25). Output:
  improvements/s2-pilot-data.jsonl. Digest:
  improvements/worker-s2-pilot-digest.md. This log:
  improvements/worker-s2-scrapling-pilot-log.md.

## 1. robots.txt (checked first, 2 requests)

- news.ycombinator.com/robots.txt: 200, 243 bytes. `User-agent: *`,
  `Crawl-delay: 30`. Disallows /collapse?, /context?, /fave?, /flag?, /hide?,
  /login, /logout, /r?, /reply?, /submitlink?, /vote?, /x?. Item pages
  (/item?id=) are NOT disallowed. Compliance: only ONE request to the HN
  website itself (the front page); all thread data came from the official
  public HN JSON API (hacker-news.firebaseio.com), which is a separate
  service built for programmatic access.
- github.com/robots.txt: 200, 30190 bytes. Generic `User-agent: *` section
  disallows /search, /gist/, /raw/, /tree/, /blame/, /commits/ and similar.
  /trending is not mentioned anywhere in the file and is not disallowed.
  GitHub's own note in the file points crawlers at its API for metadata.

## 2. Pilot run (43 requests, wall 153.6s)

Command: `~/workspace/scrapling-trial-venv/bin/python improvements/s2-pilot.py`
Run 14:25:45-14:28:19 UTC, exit 0. 1 request per 2.5s sleep between calls.
Request count: 43 total (2 robots.txt + 1 HN front + 10 HN items + 20 HN
comments + 2 GitHub trending pages + 10 GitHub API repo calls). Under the
50-page cap.

Results by source:
- HN front page: 200, 30 stories parsed (titles, scores, comment counts,
  item ids all aligned; n_titles 30, n_scores 30, n_comment_links 30).
- HN items (top 10 by score): 10/10 200. Comment counts 23-260.
- HN comments (top 2 per thread): 20/20 200, text truncated to 500 chars
  in the JSONL.
- GitHub trending overall: 200, 16 repos. Python: 200, 22 repos.
- GitHub API repo metadata: 5/10 200, 5/10 403 (Claude-BugHunter,
  superpowers, CLI-Anything, minimind, firecrawl). The 403 records hold
  all-None fields: the error JSON has no repo fields, and my script did not
  store the error message. Limitation recorded, not hidden.

## 3. Bug found and fixed during the run (my error, not Scrapling's)

- First run crashed at once: `AttributeError: 'Selector' object has no
  attribute 'attributes'`. In Scrapling 0.5.1, `css()` returns parsel-style
  `Selector` objects; attributes live on `.attrib`, not `.attributes`.
  Probed live: `a.attrib` returns `{'href': 'item?id=1'}`,
  `get_all_text()` and `css()` on elements work. Fixed with one sed:
  `sed -i 's/\.attributes\.get/.attrib.get/g'` (4 sites). Second run
  completed clean. Lesson for the next worker: never trust attribute names
  from older docs; probe the object first.

## 4. The 403s: cause proven, not guessed

- Follow-up call (1 extra request, total 44): GET
  https://api.github.com/rate_limit returned 200 with core
  `limit 60, used 60, remaining 0, reset 2026-11-21T14:32:19Z`. The shared
  egress IP had exhausted the unauthenticated 60/hour core quota, so the
  403s were genuine rate-limit exhaustion, not blocking or a script bug.
  The quota reset ~4 minutes after the check. Consequence for future runs:
  trending HTML is the reliable layer (10/10); API enrichment needs a
  GitHub token or a wait for reset. No retry was attempted; the pilot
  stayed inside its budget.

## 5. Verification of the output

- `python3 -c` parse check: 43 lines, all valid JSON, statuses {200: 38,
  403: 5}, file ends with newline.
- Cross-checks: HN front top story (2746 pts, GRH proof) matches the API
  item record for the same id (2746 pts, 1922 descendants). GitHub trending
  repo names match the API full_name fields where the API answered (5/5).
- No page blocked the Fetcher. Nothing was evaded. No personal data
  collected (only public titles, scores, repo metadata, public comments).

## 6. Files and commit

- improvements/s2-pilot.py (pilot script, 8.1 KB)
- improvements/s2-pilot-data.jsonl (43 records)
- improvements/worker-s2-pilot-digest.md (findings, under 800 words)
- improvements/worker-s2-scrapling-pilot-log.md (this file)
- Commit on todolist-push, verified via ls-remote (hash reported to Muse).

## 7. Verdict

USEFUL WITH LIMITS, same as S1. The static Fetcher layer covers HN and
GitHub trending fully and the data is immediately usable: the digest names
5 concrete patterns predecessors use (skills bundles, methodology-as-product,
agent-native CLIs, tiny/local models, scraping as infrastructure). The
limits are the API quota on a shared IP and the still-blocked stealth path
for X/YouTube. Next step if the owner wants more: a token for the GitHub
API, a daily repeat of this pilot (same script, new snapshot), and the
forward-proxy route from the W-MOTION lesson to unblock StealthyFetcher.
