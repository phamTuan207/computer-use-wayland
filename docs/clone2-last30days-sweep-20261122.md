# last30days sweep: DOM grounding, batch 8 new task 4

Date of work: 2026-11-22, local time Asia/Saigon. All run times below
are UTC wall clock as printed by the engine, with elapsed seconds.

This report is generic. It contains no personal information, no real
names, no email addresses, no accounts, no tokens.

## 0. What was done

The cancelled review task was replaced by this task: install the
last30days skill on this machine, then run a 30-day sweep with it for
the DOM grounding topic (the topic of batch 8 task 2: DOM and a11y
fast grounding for Firefox and Zen, one observation for many actions,
cheap verify). The coordinator verdict on the skill source is CLEAN
and clone2's independent review agreed (verdict PROCEED,
docs/clone2-last30days-review-20261122.md). The user confirmed the
task change directly.

## 1. Install

Method: git clone, no installer run, no npx.

- Command: git clone --depth 1
  https://github.com/mvanhorn/last30days-skill into
  ~/workspace/tools/last30days-skill, then git fetch --unshallow so
  the reviewed commit could be diffed.
- Installed HEAD: ef01dab, SKILL.md version 4.5.0.
- The reviewed commit was f5d0e44. The installed clone is exactly one
  commit past it: ef01dab, "feat(tiktok): free top comments for every
  kept TikTok from the public comment endpoint (#1555)". Diff
  f5d0e44..ef01dab: 7 files, 238 insertions, 7 deletions
  (CONFIGURATION.md, one changelog.d entry,
  skills/last30days/scripts/lib/env.py +9 lines,
  skills/last30days/scripts/lib/pipeline.py,
  skills/last30days/scripts/lib/tiktok.py, and two test files). It is
  a TikTok comments feature inside the already reviewed source
  surface, with one transport change stated plainly below. No
  installer change. The sweep ran from this clone.
- The transport change: the diff adds a direct call to
  https://www.tiktok.com/api/comment/list/ (literal constant
  _PUBLIC_COMMENTS_URL in skills/last30days/scripts/lib/tiktok.py),
  fetched with a browser User-Agent and a tiktok.com Referer, and it
  is ON by default (is_tiktok_public_comments_on in
  skills/last30days/scripts/lib/env.py defaults to 'on' unless
  LAST30DAYS_TIKTOK_PUBLIC_COMMENTS is off, 0, false or no). At
  f5d0e44 TikTok comments went only through ScrapeCreators with a
  key, and the string "tiktok.com" appeared in the reviewed code
  only in domain lists and in a constructed post URL, never as a
  fetched endpoint. The provider is the same as the existing TikTok
  source and no host outside the reviewed source surface is added,
  but a direct call to www.tiktok.com is new, and the earlier
  "no new outbound host class" wording hid that. The URL is a
  literal in the added code, verified in the diff itself.
- The skill is used from the clone only. No skill files were
  installed or copied into home, config, PATH or tools directories
  beyond the clone itself, and no file from the repo was executed
  except the research engine entry point
  skills/last30days/scripts/last30days.py. One qualification: the
  engine writes its own run state to ~/.config/last30days during a
  run (last-report.json 43 KB, last-run.json, last-report.lock).
  That is engine runtime state, not a skill install.

## 2. Sweep runs

Three engine runs, window 30 days, --auto-resolve,
--no-browser-cookies, --emit json, one save dir per run under
~/workspace/tools/last30days-sweep, sweep2 and sweep3. Raw engine
output is preserved in those save dirs as the *-raw.json files.

| Run | Topic | Wall (UTC) | Elapsed | Results |
|---|---|---|---|---|
| 1 | DOM grounding for computer use GUI agents | 2026-11-21T20:54:47Z to 20:55:05Z, agent-reported, end anchored at generated_at 20:55:04.96Z | 17.1 s, agent-reported (no stdout log preserved for run 1; the stated window spans 18 s, not 17.1 s) | 11 |
| 2 | accessibility tree grounding for GUI agents | 2026-11-21T20:55:15Z to 20:55:29Z, start agent-reported | 12.8 s, engine-reported ("Research complete (12.8s)" in the stdout log) | 4 |
| 3 | DOM snapshot element grounding browser agents | 2026-11-21T20:55:15Z to 20:55:29Z, start agent-reported | 12.8 s, engine-reported ("Research complete (12.8s)" in the stdout log) | 2 |

Runs 2 and 3 ran in parallel: their generated_at values are 0.02 s
apart (run 2 20:55:29.18Z, run 3 20:55:29.16Z), and both printed
"Research complete (12.8s)". The elapsed column above uses the
engine-reported figure where the stdout log preserves it; run 1 has
no stdout log in its save dir (only the raw JSON and the library
database), so its start time and elapsed are agent-reported only,
with only the end anchored by generated_at.

Source status: runs 1 and 2, github ok, hackernews ok, reddit
unreachable, grounding (the web search backend) unreachable. Run 3
differs: github "no-results", hackernews ok, reddit unreachable,
grounding unreachable. In run 3 GitHub found 30 issues/PRs and
dropped 30 of 30 as off-topic (twice, per the stdout log), and the
"Research complete" line records Github: 0 results. Both run-3
items (Turbo-Browser-MCP and Pomerado) came from Hacker News only.
No API keys are configured on this machine, so the keyed sources (X,
YouTube, TikTok, ScrapeCreators-backed sources) returned nothing,
and browser cookies stayed off. Effective recall is Hacker News
plus GitHub for runs 1 and 2, and Hacker News only for run 3. This
matters for the Turbo-Browser-MCP finding: it rests on Hacker News
alone. Every date below is the item's own published date as
recorded by the engine, inside the window 2026-10-22 to
2026-11-21.

## 3. Findings

### 3.1 NEW AND USABLE: Turbo-Browser-MCP, a shipped implementation of the combined design shape

- Source: Show HN, Hacker News, 2026-11-15, "Show HN:
  Turbo-Browser-MCP, Batch forms, DOM deltas and submit guards for
  MCP", pointing at https://github.com/Tthanh2k6/turbo-browser-mcp
  (run 3, relevance 0.361, the top result of that run).
- Checked directly on the repo page, crawled 2026-11-21 20:55 UTC:
  the repository was created 2026-11-14, has 136 stars and 74
  commits, MIT license. Its README describes a Playwright MCP server
  with 11 tools built to cut agent turns and tokens:
  - inspect_compact returns a size-capped snapshot of elements, and
    with onlyChanged true returns only the elements that changed
    since the last snapshot, with new refs marked and removed refs
    listed. This is the diff-only re-observation from the team's
    crawls, shipped.
  - batch_actions runs an ordered list of clicks, key presses, form
    steps and page reads as one call, with an expect check
    (urlMatches, textMatches, textNew, selector) evaluated after the
    steps. This is plan-once batched execution with an outcome
    check, shipped.
  - batch_actions takes a submissionKey, and the README example is
    "Allow the final click, check for a receipt, refuse a repeat".
    This is an exactly-once send mechanism with a named key, which
    is the benchmark design's open gap D4 (exactly-once asserted but
    not mechanized), shipped with a concrete mechanism. Qualified:
    exactly-once only when the call returns. The README's Safety
    section states: "The ledger is written only when the call
    returns. If the call throws after the page already sent the
    submission (for example a navigation timeout), nothing is
    recorded. Check the site before re-running." A throw after send
    leaves the ledger empty and a re-run double-sends, which is
    exactly the failure mode the team's own task 1 redteam proved
    in the 2-vision benchmark (a retry after a failed gate
    double-sends). The ledger is also a per-machine file
    (~/.turbo-browser-mcp/submissions.jsonl by default), so it does
    not cover two clones on two machines or a wiped home directory.
    The actionable conclusion survives: read the implementation,
    port the mechanism, not the driver.
  - A submit guard is on by default: buttons that look like a final
    commit (Submit, Send, Publish, Pay, Confirm, and equivalents in
    several languages) are blocked unless allowSubmit is passed.
  - Click aftermath reporting: after a click the server waits for
    the DOM to go quiet and reports what changed, a cheap
    non-vision verify step.
- Limit: it is Chromium only (Playwright, CDP). Per the team's
  proven rule, CDP is dead on Firefox and Zen, so the driver does
  not transfer. The design and the mechanism names do transfer, and
  they map one to one onto the 2-vision benchmark's open items: the
  V12 sent-bubble gate (expect plus receipt check), gap D4
  (submissionKey), and the step-6 loop hygiene item (onlyChanged
  delta snapshots).
- UNVERIFIED here: the README's benchmark numbers were not re-run.
  Only the tool surface and mechanisms were read.

### 3.2 NEW, independent corroboration: BotCircle issue 8 and the OpenDots fix direction

- Source: GitHub, 2026-10-22, Sr-0w/BotCircle issue 8, "Computer
  use: clics a l'aveugle / mal positionnes (capture apres action
  invisible, grounding des coordonnees non verifie)", at
  https://github.com/Sr-0w/BotCircle/issues/8 (run 1, relevance
  0.283). The title itself names the team's incident shape: blind
  and mispositioned clicks, a post-action capture that shows
  nothing, coordinate grounding never verified.
- The engine's cluster for this item (GitHub source) quotes the
  related OpenDots changelog: the system prompt and tool
  descriptions were changed to accessibility and DOM first, act on
  a named reference then inspect the result, coordinates only as a
  last resort, with fixes called out for cursor, focus and native
  typing precision (commits 9b1b2b9, 751b471, c21be95 in
  Sr-0w/OpenDots, as quoted by the engine cluster).
- Value: an independent practitioner hit the same failure in the
  window and converged on the same fix direction the team's amend
  already takes (DOM and a11y first, named references, inspect the
  result, coordinates last). It is corroboration from the field,
  not a new method.

### 3.3 ADJACENT, not a grounding method: Pomerado

- Source: Launch HN, Hacker News, 2026-11-11, "Launch HN: Pomerado
  (YC F26), Turn any website into an MCP for agents",
  https://news.ycombinator.com/item?id=50455811 (run 3, relevance
  0.337). Turning a website into a structured MCP surface would
  bypass visual grounding for covered sites, but it is a hosted
  product announcement with no method detail in the sweep data.
  Noted only; not counted as a grounding result.

### 3.4 Noise, stated honestly

Most of the sweep's recall was keyword noise, and this report does
not dress it up as findings:

- Run 1's top cluster was "Show HN: Subvocal, Talk to your computer
  without making noise" (Hacker News, 2026-11-02, relevance 0.341),
  a voice input product, not grounding. The rest of run 1 was agent
  infrastructure news (Simantic 2026-10-29, Zeus 2026-11-20,
  Aisync 2026-11-10, Airlock 2026-11-09, Beolis 2026-10-30, a
  transitive-policies essay 2026-11-14, "Ask HN: Is anyone running
  multi/always-on agents that don't cost a fortune?" 2026-11-06,
  "Show HN: Botel" 2026-11-06, and "Don't Yell at Your Agents"
  2026-10-22, a YouTube link), none of it about grounding
  methods.
- Run 2 (accessibility tree) returned only general accessibility
  news: Bolt scooters as accessibility sensors (2026-11-17), Apple
  TV sign language (2026-11-11), a front-end accessibility hiring
  post (2026-10-31), and one unrelated GitHub pull request. No
  a11y-tree grounding method appeared.
- No new Firefox or Zen specific grounding method appeared in the
  reachable sources in this window.

## 4. New versus already known

Already known to the team before this sweep (from the batch 7 and
click2 crawls): HCU batched actions with a live guard and a diff,
Mantis numbered compact text with diff-only updates, DOM value
readback as the cheap verify, plan-once execute-all, and the
exactly-once concern recorded as combined-design gap D4 with no
mechanism.

New in this 30-day window:

1. A shipped open-source implementation combining the whole shape
   (Turbo-Browser-MCP, created 2026-11-14, Show HN 2026-11-15),
   with three concrete mechanisms the team's design does not yet
   have: onlyChanged delta snapshots as a tool parameter,
   submissionKey as the exactly-once mechanism for a send
   (exactly-once only when the call returns; a throw after send
   leaves the ledger empty and a re-run double-sends, per the
   README Safety section quoted in 3.1), and an expect outcome
   check plus a default-on submit guard. Each maps
   onto a named open item in the benchmark design (D4, the V12
   gate, step-6 loop hygiene).
2. Independent field evidence (BotCircle issue 8, 2026-10-22, and
   the OpenDots changelog it quotes) that the blind-click failure
   is being hit and fixed the same way elsewhere: DOM and a11y
   first, named references, inspect the result, coordinates last.

Nothing in the reachable window contradicts the combined design,
and nothing in it offers a vision-only method that meets the 90
percent bar. The one directly usable next step is to read
Turbo-Browser-MCP's submissionKey, expect and onlyChanged
implementations before the benchmark's D4 and loop-hygiene items
are built, and to port the mechanisms, not the Chromium driver.

## 5. Limits

- Recall is Hacker News plus GitHub only for runs 1 and 2, and
  Hacker News only for run 3 (GitHub returned no results there):
  reddit and the web grounding backend were unreachable from this
  machine in all three runs, and no API keys are configured, so X,
  YouTube and TikTok contributed nothing. A sweep with keys set
  would widen recall and could change section 3. This limit is the
  engine's own source status output, not an inference.
- The skill ran keyless with browser cookies off, matching the
  review's conditions (cookies off by default, official APIs
  preferred).
- Turbo-Browser-MCP's performance claims are UNVERIFIED here; only
  its tool surface was read.
- The OpenDots changelog text is quoted from the engine's cluster
  summary of GitHub data, not re-read commit by commit here.
