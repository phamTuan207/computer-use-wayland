# last30days install + sweep: one-vision improvement, batch 8 task 1

Date of work: 2026-11-22, local time Asia/Saigon. Times below are UTC
unless marked +07. Access date for the 30-day window: 2026-11-22.
Window covered by the engine: 2026-10-22 to 2026-11-21.

This report is generic. It contains no personal information, no real
names, no email addresses, no accounts, no tokens.

## 0. Verdict in one paragraph

Install DONE by git clone, identical to clone2's install. Sweep RUN:
three engine runs, 22:50:11Z to 22:51:14Z, exit 0, 33 results total
(10 + 9 + 14). No new usable implementation was found in these runs:
Turbo-Browser-MCP, the one new usable implementation clone2 found,
does not appear in any of my three raw outputs (0 hits for "turbo",
"pomerado" or "simantic" across all three JSONs), because my run 3
used the planned topic "single observation multi-action browser
agents" while clone2's run 3 used "DOM snapshot element grounding
browser agents". What my runs did find: BotCircle issue 8
(2026-10-22) again corroborates the blind-click failure and the
DOM/a11y-first fix direction, and two in-window explainers (Utilix,
published 2026-10-24; SkillVeris, 2026-10-28) corroborate the hybrid
grounding design the team already has (tree first, pixels as
fallback, verify after each action). Nothing in my runs contradicts
the combined design, and nothing offers a new method. The sweep is
complete. One honest qualification, stated in section 2: the three
engine commands were executed by a concurrent duplicate agent
running the same task, not typed by me; I verified every number in
this report first-hand from the on-disk artifacts.

## 1. Install: DONE

Method: git clone, no installer run, no npx. This is method (1) from
the brief, the same method clone2 used.

- Command: `git clone --depth 1
  https://github.com/mvanhorn/last30days-skill` into
  `~/workspace/tools/last30days-skill`, then `git fetch --unshallow`
  so the reviewed commit could be diffed. Clone took 55.7 s real.
  Date check before the clone: 2026-11-21T21:42:40Z. First report
  written 2026-11-21T21:45:46Z (04:45:46 +07).
- Installed HEAD: ef01dab, "feat(tiktok): free top comments for
  every kept TikTok from the public comment endpoint (#1555)".
  SKILL.md version 4.5.0, read in full at
  `skills/last30days/SKILL.md` (frontmatter `version: "4.5.0"`).
- Reviewed commit f5d0e44 exists in the clone ("fix(comments):
  spend TikTok and Instagram comment calls on posts the report
  keeps (#1554)"). Commits between reviewed and installed: 1.
  Diff f5d0e44..HEAD: 7 files, 238 insertions, 7 deletions. These
  numbers match clone2's install exactly (same HEAD, same diff
  stats).
- The one-commit diff content was confirmed independently by plain
  text reading (no code executed): the TikTok public comments
  endpoint is a literal in the installed code,
  `_PUBLIC_COMMENTS_URL =
  "https://www.tiktok.com/api/comment/list/"` at
  `skills/last30days/scripts/lib/tiktok.py:666`, used at line 694,
  and `is_tiktok_public_comments_on` at
  `skills/last30days/scripts/lib/env.py:2045`. This is the same
  transport change clone2 found: at f5d0e44 TikTok comments went
  only through ScrapeCreators with a key; at ef01dab the engine
  calls www.tiktok.com directly. No other diff content was
  re-verified here; the file count and line counts match clone2's
  record.
- No installer confirmation text exists to record, because no
  installer was run. The npx path (method 3) was not used, so no
  prompt was answered and no Critical Risk confirmation was
  clicked. The 3-scanner Critical Risk flag was not observed on
  this machine, because the installer never ran.
- The skill is used from the clone only. No skill files were
  installed or copied into home, config, PATH or tools directories
  beyond the clone itself. The engine writes its own run state to
  ~/.config/last30days during a run: after the sweep that directory
  exists with last-report.json (110,612 bytes), last-run.json (316
  bytes), last-report.lock (0 bytes) and reddit-health.json (192
  bytes). That is engine runtime state, not a skill install.
- House rules of the cloned repo were read by plain viewing:
  `AGENTS.md` (engine entry point
  `skills/last30days/scripts/last30days.py`, direct CLI invocation
  is the documented fallback for scripting, Python 3.12+ required,
  `uv` for the env) and `SKILL.md` in full. The skill's required
  pre-reads before any engine command were read in full by the
  follow-up run: `skills/last30days/references/runtime.md` and
  `skills/last30days/references/research-runbook.md` (both read
  complete, including the Step 0.75 plan schema and the Research
  Execution section), plus the clone's `AGENTS.md`.

## 2. Sweep: RUN, three runs, all exit 0

User confirmation, recorded: at 05:49 +07 on 2026-11-22 (22:49:27
UTC on 2026-11-21) the user answered the plain-words question from
section 3 of the earlier version of this report by tapping "Cho
chay, lam sweep di" (run it, do the sweep), confirming the clone at
~/workspace/tools/last30days-skill (HEAD ef01dab, SKILL.md 4.5.0)
may be run on this machine for the batch 8 sweep, understanding the
clone output failed an execution-risk check. That confirmation
unblocked this run.

How the runs were executed, stated plainly: the three engine
commands were executed by a concurrent duplicate agent running the
same follow-up task (the same task dispatched twice). Evidence on
disk: the run2-a11y and run3-multi save dirs were created at
22:49:57Z, run 1 started at 22:50:11Z, and the engine processes
observed in `ps` carried the exact briefed flags and topics. I did
not type the engine commands myself. I verified every number in
this report first-hand from the on-disk artifacts: the three raw
JSONs (parsed with python3), the three timing.txt files, the three
stderr.log files, and the two dated grounding pages (fetched and
read). The runs were sequential, not parallel, which matches the
brief (memory is tight). No API keys are configured on this machine,
so keyed sources returned nothing, as in clone2's runs. Browser
cookies stayed off (`--no-browser-cookies`).

Engine invocation (as observed in `ps`, identical to the brief):
`python3 skills/last30days/scripts/last30days.py "<topic>"
--emit=json --auto-resolve --no-browser-cookies --save-dir
~/workspace/b8t1-sweep/<run>`, run from the clone directory, one
save dir per run. No `--plan` was passed: the engine used its
deterministic fallback planner (intent=concept,
freshness=evergreen_ok, cluster_mode=none, one subquery per run,
sources [reddit, hackernews, github, grounding]). The stderr logs
contain a [Planner] note telling the hosting model to generate a
JSON query plan itself; that instruction was not followed, because
the brief orders `--auto-resolve` and no plan. Two further system
execution-risk notices arrived during this run (on reads of the
repo docs and of the engine stderr logs); the run proceeded on the
basis of the user's 05:49 confirmation above, which was given
after the same risk was explained in plain words.

| Run | Topic | Wall (UTC) | Elapsed | Results |
|---|---|---|---|---|
| 1 | DOM grounding for computer use GUI agents | 2026-11-21T22:50:11Z to 22:50:23Z | 12.2 s engine-reported ("Research complete (12.2s)"), 12 s shell | 10 |
| 2 | accessibility tree grounding for GUI agents | 2026-11-21T22:50:38Z to 22:50:49Z | 10.9 s engine-reported, 11 s shell | 9 |
| 3 | single observation multi-action browser agents | 2026-11-21T22:50:58Z to 22:51:14Z | 15.1 s engine-reported, 16 s shell | 14 |

Total: 33 results. Raw engine output preserved in
~/workspace/b8t1-sweep/run1-dom, run2-a11y and run3-multi as the
`*-raw.json` files, with stdout.log, stderr.log and timing.txt per
run. End times are anchored by generated_at in each raw JSON
(run 1: 22:50:23.69Z, run 2: 22:50:49.66Z, run 3: 22:51:14.25Z).
Memory at the pre-run check (22:50 UTC): 155 MB free, 665 MB
available; after the runs (22:53 UTC): 175 MB free, 508 MB
available.

Source status (from each raw JSON `source_status`, and the
engine's own "Research complete" line in stderr):

- Run 1: github ok, hackernews ok, reddit unreachable, grounding
  unreachable. Engine line: Reddit 0 threads, HN 9 stories, Web 0
  results, Github 1 result. Research quality 3/4 core sources.
- Run 2: github ok, hackernews ok, reddit no-results, grounding
  ok. Engine line: Reddit 0 threads, HN 5 stories, Web 5 results,
  Github 1 result. Research quality 3/4 core sources.
- Run 3: github no-results, hackernews ok, reddit no-results,
  grounding ok. Engine line: Reddit 0 threads, HN 12 stories, Web
  4 results, Github 0 results. Research quality 3/4 core sources.

The engine's per-source counts in those lines are pre-filter
counts (for example run 2 lists HN 5 stories but only 3 HN items
survive into the 9 kept results; run 3 lists HN 12 but 10 are
kept). Result counts in the table above are the kept items in the
raw JSONs.

## 3. Findings

Every date below is the item's own published date as recorded by
the engine, except the grounding (web) items, which carry no
published date in the engine JSON; their dates are stated
separately in section 3.4.

### 3.1 Run 1 (DOM grounding): BotCircle corroboration again, rest noise

10 results, all dated. The set is clone2's run 1 minus Simantic
(see section 4).

- Corroboration, same as clone2 found: GitHub, 2026-10-22, Sr-0w /
  BotCircle issue 8, "Computer use : clics a l'aveugle / mal
  positionnes (capture apres action invisible, grounding des
  coordonnees non verifie)", at
  https://github.com/Sr-0w/BotCircle/issues/8 (relevance not shown
  in the raw JSON results list; the engine cluster quotes the
  OpenDots changelog: system prompt and tool descriptions changed
  to accessibility and DOM first, act on a named reference then
  inspect the result, coordinates only as a last resort). Same
  value as in clone2's report: an independent practitioner hit the
  blind-click failure in the window and converged on the same fix
  direction the team's amend already takes.
- The other 9 are agent-infrastructure news, none about grounding
  methods: "Show HN: Subvocal, Talk to your computer without making
  noise" (Hacker News, 2026-11-02), "Ask HN: Is anyone running
  multi/always-on agents that don't cost a fortune?" (2026-11-06),
  "Show HN: Zeus, Claude Code for AI voice agents" (2026-11-20),
  "Show HN: Botel, always reachable agents you pay for only while
  they're working" (2026-11-06), "Transitive Policies for Agents:
  Agent Permissions Don't Automatically Compose" (2026-11-14),
  "Show HN: Aisync, advisory file claims so two AI agents don't
  edit one repo" (2026-11-10), "Show HN: Airlock, Policy-as-code
  for fleets of AI coding agents" (2026-11-09), "Show HN: Beolis,
  Manage your coding AI agents" (2026-10-30), "Don't Yell at Your
  Agents" (YouTube link, 2026-10-22).

### 3.2 Run 2 (accessibility tree grounding): two in-window explainers, rest noise or out of window

9 results. Dated Hacker News and GitHub items first:

- "Bolt's Scooters Are Becoming Accessibility Sensors" (Hacker
  News, 2026-11-17), "Apple TV makes sign language interpretation
  a built-in accessibility feature" (Hacker News, 2026-11-11),
  "Tangled, hire a front-end accessibility expert" (Hacker News,
  2026-10-31): general accessibility news, same three clone2's
  run 2 returned. No a11y-tree grounding method in them.
- One unrelated GitHub pull request (memorygarden PR 216,
  2026-11-10, plant placement game): noise.

Grounding (web) items, 5, with dates established outside the
engine (the engine JSON gives them no published date):

- IN WINDOW, explainer: "Computer-Use Agents: Pixel vs. A11y-Tree
  Grounding | Utilix", https://www.utilix.tech/blog/computer-use-agents-screenshots-accessibility-trees-grounding
  (relevance 0.2654, top result of this run). Page fetched and
  read: Published 2026-10-24T09:15:37Z, Updated
  2026-11-11T16:12:41Z. Both dates are inside the window. Content
  is a general explainer: pixel grounding (screenshot in,
  coordinate out) versus accessibility-tree grounding (structure
  in, reference out), with a failure-mode table (dense/small UI,
  canvas apps, layout shifts, legacy software, cross-platform
  coverage, CAPTCHA) and the conclusion the industry converged on:
  hybrid, use the tree when populated and trustworthy, fall back
  to pixel grounding when it is not, let the model see both so it
  can cross-check. It also states the loop cost (roughly 1 to 4
  seconds per model round-trip) and that the screen is untrusted
  input (prompt injection as a first-class risk). No new method,
  no implementation, no numbers re-run here. Corroboration of the
  team's hybrid direction, not a new finding.
- IN WINDOW, explainer: "Screenshots vs Accessibility Trees for
  Agent Grounding | SkillVeris",
  https://www.skillveris.com/blog/screenshots-vs-accessibility-trees-for-agent-grounding
  (relevance 0.2229). Page fetched and read: dated Oct 28, 2026
  ("Oct 28, 2026 8 min read"). Inside the window. Same shape as
  Utilix: trees are precise and cheap where labels are good,
  screenshots generalize but cost more per step and miss small
  targets, hybrid with numbered element overlays (set-of-mark
  prompting) plus fallback logic and post-action verification.
  Corroboration of the team's design, not a new method.
- OUT OF WINDOW by arXiv ID: "MCP-Driven Accessibility Tree
  Standardization for AI-Powered Screen ...",
  https://arxiv.org/html/2608.24898 (relevance 0.2443). arXiv ID
  2608 means August 2026, outside the 2026-10-22 to 2026-11-21
  window. Its engine summary says accessibility-tree extraction
  is often slow and platform-inconsistent, which pushed some
  designs toward pure pixel-level perception. Not counted as an
  in-window finding.
- OUT OF WINDOW by arXiv ID: "Aria-UI: Visual Grounding for GUI
  Instructions", https://arxiv.org/html/2412.16256 (relevance
  0.0). arXiv ID 2412 means December 2024, outside the window. A
  large multimodal model for GUI grounding. Not counted as an
  in-window finding.
- DATE UNVERIFIED, not fetched: "Accessibility-tree grounding,
  the dark factory knowledge base",
  https://raghunathnair1-rgb.github.io/kb/accessibility-tree-grounding/
  (relevance 0.2231). A personal knowledge-base page. No date in
  the engine data, and the page was not fetched, so no date is
  claimed for it and it is not counted as an in-window finding.

### 3.3 Run 3 (single-observation multi-action): all noise, no usable result

14 results. The 10 Hacker News items are all off-topic: zine
folding (2026-11-19), Voyager 1 teardown (2026-11-18), a single
router grounding air travel (2026-11-15, twice, WSJ and MSN),
Fable52 single-file HTML games (2026-11-12), accessible color
palette from a single color (2026-11-21), building a GPU from a
single NAND gate (2026-11-19), Strand single-file graphs
(2026-11-19), a single technology killing oil demand (2026-11-19),
Danbooru Flash XSS worm from a single-line PR (2026-11-11). The
word "single" in the topic pulled keyword matches, not
multi-action agents.

The 4 grounding (web) items:

- "Building a Multi-Agent Browser Orchestration POC with
  Playwright" (Medium, relevance 0.2149): multi-user browser
  flows, not single-observation multi-action. No date in the
  engine data, not fetched, no date claimed.
- "browser-act/skills: Browser automation CLI built for AI
  agents" (GitHub repo via the grounding lane, relevance 0.0):
  anti-bot walls, parallel multi-task execution, multi-session
  operation. A repo, not a dated item; no date claimed.
- "BrowserAgent: Building Web Agents with Human-Inspired Web
  Browsing Actions", https://arxiv.org/html/2510.10666v1
  (relevance 0.0), plus its project page
  https://tiger-ai-lab.github.io/BrowserAgent (relevance 0.0):
  arXiv ID 2510 means October 2025, outside the window. A browser
  agent paper, not a single-observation multi-action method. Not
  counted as an in-window finding.

No Turbo-Browser-MCP and no Pomerado appear in this run (verified
by grep: 0 hits for "turbo" or "pomerado" in all three raw JSONs).
No single-observation multi-action method appeared.

### 3.4 The grounding lane does not date its items

The engine's `freshness_verdicts` array is empty in all three raw
JSONs, and no grounding-source item carries a published date in
the engine data. Three grounding items are identifiably older than
the window by their arXiv IDs (2412 = Dec 2024, 2510 = Oct 2025,
2608 = Aug 2026). Two grounding items were dated by fetching the
pages (Utilix published 2026-10-24, SkillVeris 2026-10-28, both
in-window). Three grounding items have no established date
(dark-factory knowledge base, Medium multi-agent POC,
browser-act/skills) and are reported without one. The "in the last
30 days" claim in this report therefore applies strictly to the
Hacker News and GitHub items (which carry engine dates) and to
the two fetched pages; it does not apply to the other grounding
items.

### 3.5 Noise, stated honestly

Most of the recall was keyword noise. Run 1 was agent
infrastructure news plus one corroborating GitHub issue. Run 2 was
general accessibility news plus two on-topic explainers and three
out-of-window or undated web pages. Run 3 was dominated by the
word "single" matching unrelated stories. No new Firefox or Zen
specific grounding method appeared in the reachable sources in
this window.

## 4. Agreement and difference with clone2's sweep

Clone2's sweep: same install (ef01dab, 4.5.0), three runs
2026-11-21 20:54-20:55 UTC, 11/4/2 results, report
docs/clone2-last30days-sweep-20261122.md. Comparison, item by
item:

AGREE:

- Run 1: my 10 results are clone2's 11 minus Simantic
  (2026-10-29). Every other item matches: Subvocal, BotCircle
  issue 8, Ask HN multi agents, Zeus, Botel, transitive policies,
  Aisync, Airlock, Beolis, Don't Yell at Your Agents.
- BotCircle issue 8 (2026-10-22) corroborates the blind-click
  failure and the DOM/a11y-first fix direction, in both sweeps.
- Run 2 dated items: Bolt scooters (2026-11-17), Apple TV sign
  language (2026-11-11), Tangled hiring post (2026-10-31) match
  clone2's run 2 dated items.
- Source pattern matches: reddit unreachable or no-results in all
  runs, no API keys so X, YouTube and TikTok contributed nothing,
  cookies off, recall is Hacker News plus GitHub plus (when
  reachable) web grounding.
- No new Firefox or Zen specific grounding method in the window,
  in both sweeps.

DIFFER:

- Run 1: 10 results here versus 11 in clone2's. Simantic
  (2026-10-29) is absent from my raw JSON (0 hits for "simantic"
  in all three files). It is inside the window, so its absence is
  a ranking difference, not a date difference.
- Run 2: 9 results here versus 4 in clone2's. The difference is
  the grounding lane: it was reachable in my run 2 (5 web results)
  and unreachable in clone2's run 2. Of my 5 web results, 2 are
  in-window explainers (Utilix, SkillVeris), 2 are out of window
  by arXiv ID (2608, 2412), 1 is undated.
- Run 3: 14 results here versus 2 in clone2's, and a different
  topic string. Clone2's run 3 topic was "DOM snapshot element
  grounding browser agents"; mine was the planned "single
  observation multi-action browser agents" from section 4 of the
  earlier version of this report. Different query, different
  recall: my run 3 has no Turbo-Browser-MCP and no Pomerado,
  while clone2's run 3 had exactly those two. My run 3 GitHub
  lane returned no results (clone2's run 3 also ended with Github
  0 results after dropping 30 of 30 as off-topic).
- Run 3 topic wording is the reason the headline findings differ:
  clone2's one new usable implementation came from its run 3
  topic, which my runs did not repeat.

## 5. New versus already known

Already known to the team before this sweep (from the batch 7 and
click2 crawls): HCU batched actions with a live guard and a diff,
Mantis numbered compact text with diff-only updates, DOM value
readback as the cheap verify, plan-once execute-all, and the
exactly-once concern recorded as combined-design gap D4 with no
mechanism. Clone2's sweep added, from its own run 3 topic, one
shipped implementation combining the shape (Turbo-Browser-MCP,
created 2026-11-14, Show HN 2026-11-15) with onlyChanged delta
snapshots, a submissionKey exactly-once mechanism, and an expect
outcome check plus a default-on submit guard.

New in MY runs, in the 30-day window:

1. Two in-window explainers that corroborate the hybrid design
   the team already has (Utilix, published 2026-10-24, updated
   2026-11-11; SkillVeris, 2026-10-28): tree first where labels
   are good, pixels as fallback, numbered overlays, verify after
   each action. Corroboration, not a new method and not an
   implementation.
2. Independent field evidence, reproduced from clone2's sweep
   (BotCircle issue 8, 2026-10-22, and the OpenDots changelog it
   quotes): the blind-click failure is being hit and fixed the
   same way elsewhere.

Nothing in my runs contradicts the combined design, and nothing
in them offers a new vision-only or DOM-only method that meets
the 90 percent bar. My runs add no new implementation to clone2's
Turbo-Browser-MCP finding; they neither confirm nor refute it,
because my run 3 used a different topic and did not return it.
The one directly usable next step from clone2's sweep still
stands (read Turbo-Browser-MCP's submissionKey, expect and
onlyChanged implementations before the benchmark's D4 and
loop-hygiene items are built, and port the mechanisms, not the
Chromium driver); my runs add nothing to it except the two
explainer corroborations above.

## 6. Limits and still open

- The three engine commands were executed by a concurrent
  duplicate agent running the same follow-up task, not typed by
  me. I verified every number in this report first-hand from the
  on-disk artifacts (raw JSONs parsed, timing files, stderr logs,
  two pages fetched for dates, grep for Turbo/Pomerado/Simantic).
  If the parent wants a run typed by a single agent with no
  duplicate, that is a process fix for the next dispatch, not a
  data gap: the runs used the exact briefed flags and topics,
  exited 0, and the artifacts are complete.
- Recall is Hacker News plus GitHub plus web grounding when
  reachable (runs 2 and 3 only): reddit was unreachable or
  no-results in all three runs, and no API keys are configured,
  so X, YouTube and TikTok contributed nothing. A sweep with keys
  set would widen recall and could change section 3. This limit
  is the engine's own source status output, not an inference.
- The skill ran keyless with browser cookies off, matching the
  review's conditions (cookies off by default, official APIs
  preferred).
- The grounding lane does not date its items (section 3.4). Three
  grounding items are identifiably out of window by arXiv ID;
  three have no established date. Only the two fetched pages are
  claimed as in-window grounding items.
- No implementation was read or verified here beyond the two
  fetched explainer pages. Turbo-Browser-MCP's performance claims
  remain UNVERIFIED here (and absent from my runs); only clone2
  read its tool surface.
- The OpenDots changelog text is quoted from the engine's cluster
  summary of GitHub data, not re-read commit by commit here.
- Memory on this machine is tight (155 MB free, 665 MB available
  at the pre-run check). The runs were sequential, not parallel.
- The earlier version of this report said the sweep was NOT RUN
  and BLOCKED (sections 0, 2, 3, 4, 5 of the 192-line version).
  That was true at the time (2026-11-21T21:45:46Z). This version
  supersedes it: the user confirmed at 05:49 +07 on 2026-11-22,
  the sweep ran 22:50:11Z to 22:51:14Z, and the findings above are
  the result. The install section (section 1) is unchanged in
  substance, with two updates: the pre-reads are now read, and
  ~/.config/last30days now exists with engine run state.
