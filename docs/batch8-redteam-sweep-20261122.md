# Redteam: batch 8 sweep report (clone1 last30days sweep)

Target: docs/clone1-last30days-sweep-20261122.md (453 lines by wc -l).
Artifacts checked first-hand: the three raw JSONs, stdout.log,
stderr.log and timing.txt in ~/workspace/b8t1-sweep/run1-dom,
run2-a11y, run3-multi; directory birth times via stat; the clone at
~/workspace/tools/last30days-skill; ~/.config/last30days;
docs/clone2-last30days-sweep-20261122.md; the Utilix and SkillVeris
pages fetched and read live.

## Verdict: GO SURVIVES

Two wrong facts (W1, W2), five unverified claims (U1-U5), six minor
issues (M1-M6). None touches the conclusions: the sweep ran as
reported (3 runs, exit 0, 33 results), no new usable implementation
appeared in these runs, the two in-window explainers corroborate the
hybrid design, and the report is honest that its run 3 used a
different topic from clone2's run 3 and therefore neither confirms
nor refutes Turbo-Browser-MCP. The fixes owed are citation-layer
corrections only.

## W: wrong facts

### W1. Utilix is NOT the top result of run 2

Report section 3.2: "Computer-Use Agents: Pixel vs. A11y-Tree
Grounding | Utilix ... (relevance 0.2654, top result of this run)".

Wrong. In run2-a11y/accessibility-tree-grounding-for-gui-agents-raw.json,
results[0] "Bolt's Scooters Are Becoming Accessibility Sensors" has
relevance_score 0.2868, higher than Utilix at 0.2654 (results[1]).
Utilix is the top *grounding* result of the run (grounding items:
Utilix 0.2654, arXiv 2608 0.2443, dark factory 0.2231, SkillVeris
0.2229, Aria-UI 0.0), not the top result overall. Fix: qualify as
"top grounding result of this run" or drop "top result".

### W2. Relevance IS shown in the raw JSON results list

Report section 3.1, BotCircle bullet: "(relevance not shown in the
raw JSON results list; the engine cluster quotes the OpenDots
changelog ...)".

Wrong. Every entry in the raw JSON results list carries a
relevance_score field. BotCircle (results[1] of
run1-dom/dom-grounding-for-computer-use-gui-agents-raw.json) has
relevance_score 0.2834, which clone2's report rounds to 0.283. The
report contradicts itself: sections 3.2 and 3.3 cite relevance
scores (0.2654, 0.2443, 0.2231, 0.2229, 0.2149, 0.0) taken from
that same results list. Fix: delete the parenthetical clause, or
replace with the value 0.2834.

## U: unverified claims (no artifact behind them)

### U1. Memory figures

Report section 2: "Memory at the pre-run check (22:50 UTC): 155 MB
free, 665 MB available; after the runs (22:53 UTC): 175 MB free,
508 MB available." No memory log exists in the run dirs or anywhere
else checked. Cannot verify or refute. Note: free rising while
available falls is unusual but not impossible; no evidence either
way.

### U2. The ps observation of the engine process

Report section 2: "the engine processes observed in `ps` carried
the exact briefed flags and topics", and the invocation is given
"as observed in `ps`". No ps output is preserved in the report or
the run dirs. The invocation is corroborated indirectly (topics
match the JSON query fields; --emit=json by the JSON outputs;
--auto-resolve by the fallback planner lines in stderr; save dirs
by the files' locations), but the exact command line, working
directory and --no-browser-cookies have no preserved artifact.

### U3. Two further execution-risk notices

Report section 2: "Two further system execution-risk notices
arrived during this run (on reads of the repo docs and of the
engine stderr logs)". No artifact in the repo or run dirs records
them. The claim rests on the reporting agent's word only.

### U4. Install-section timestamps

Carried from the 192-line version, still without a preserved
artifact: "Date check before the clone: 2026-11-21T21:42:40Z",
"Clone took 55.7 s real", "First report written
2026-11-21T21:45:46Z". The first commit of the report (fd250da) is
2026-11-21 21:47:27Z, which is consistent with a 21:45:46Z write
but does not prove it. No clone log is preserved.

### U5. "The word 'single' pulled the noise" is an inference

Report section 3.3: "The word 'single' in the topic pulled keyword
matches, not multi-action agents." The engine states no reason for
its ranking. The correlation is strong (all 10 Hacker News titles
in run 3 contain "single" or "Single"), but the causal claim is the
reporter's inference, not engine output. Reword as an inference.

## M: minor issues

### M1. The empty run3-single-obs dir is not mentioned

~/workspace/b8t1-sweep/run3-single-obs is empty, born 2026-11-21
22:50:09.342Z, during run 1 and 2 seconds before run 1 started.
It is the fossil of the duplicate agent's abandoned save dir for
run 3 (its planned name) and the strongest on-disk evidence of the
race, yet the report never mentions it. Also, the report says only
"the run2-a11y and run3-multi save dirs were created at 22:49:57Z";
birth times show run1-dom was born at exactly the same instant
(2026-11-21 22:49:57.797Z), i.e. all three save dirs were
pre-created in one instant before run 1 started. The
duplicate-agent account in sections 0, 2 and 6 is honest but
incomplete on these two points.

### M2. Grounding dating arithmetic is short by one item

Report section 3.4: "Three grounding items have no established
date (dark-factory knowledge base, Medium multi-agent POC,
browser-act/skills)". There are 9 grounding items total (5 in run
2, 4 in run 3). Two are dated in-window by fetching, three are out
of window by arXiv ID, which leaves four undated, not three: the
BrowserAgent project page
(https://tiger-ai-lab.github.io/BrowserAgent, run 3) also carries
no date. The report folds it into the BrowserAgent bullet, so the
count is of distinct topics, but the sentence says "items" and the
2 + 3 + 3 sum accounts for only 8 of 9.

### M3. Title sourcing is inconsistent across three items

- SkillVeris is quoted as "Screenshots vs Accessibility Trees for
  Agent Grounding | SkillVeris". The "| SkillVeris" suffix is from
  the fetched page's H1, not the engine JSON title, which is
  "Screenshots vs Accessibility Trees for Agent Grounding".
- Aria-UI drops the engine title's "- arXiv.org" suffix.
- browser-act drops the engine title's "GitHub - " prefix.
None changes meaning, but a reader diffing titles against the raw
JSONs finds three mismatches. State which titles are page titles
and which are engine titles.

### M4. Quoted titles are transliterated, not exact

- BotCircle is quoted as "Computer use : clics a l'aveugle / mal
  positionnes (capture apres action invisible, grounding des
  coordonnees non verifie)"; the raw JSON title carries accents
  throughout ("clics à l'aveugle / mal positionnés (capture après
  action invisible, grounding des coordonnées non vérifié)").
  Quoting it without accents is identifiable but not exact.
- "Show HN: Subvocal, Talk to your computer without making noise"
  uses a comma where the raw title uses an en dash.

### M5. Medium title expansion comes from the URL slug, not the engine

Report section 3.3: "Building a Multi-Agent Browser Orchestration
POC with Playwright". "Playwright" comes from the URL slug
(.../building-a-multi-agent-browser-orchestration-poc-with-playwright-1-59the-coordination-problem-...);
the engine title is truncated ("Building a Multi-Agent Browser
Orchestration POC with ... - Medium"). The expansion is justified
but the report does not say where it came from.

### M6. Section 0 headline can mislead on a skim

"No new usable implementation was found in these runs" is true of
these runs, but a skim reader could take it as "Turbo-Browser-MCP
was tested and not found". The report qualifies it in the same
paragraph and again in sections 4, 5 and 6, so this is a
readability note, not an error.

## Confirmed correct (spot-checked first-hand)

- Counts 10/9/14, total 33; engine times 12.2/10.9/15.1 s and
  shell 12/11/16 s from timing.txt and the "Research complete"
  lines in stderr; generated_at 22:50:23.69Z, 22:50:49.66Z,
  22:51:14.25Z; source_status per run; freshness_verdicts empty in
  all three JSONs; exit 0 in all three timing.txt files; runs
  sequential (no wall-clock overlap).
- All run 1 and run 3 dates and titles; run 2 dated items (Bolt
  2026-11-17, Apple TV 2026-11-11, Tangled 2026-10-31,
  memorygarden PR 216 2026-11-10); relevance scores 0.2654, 0.2443,
  0.2231, 0.2229, 0.2149, 0.0, 0.0, 0.0; arXiv ID decoding (2608 =
  Aug 2026, 2412 = Dec 2024, 2510 = Oct 2025).
- Utilix page fetched and read: published 2026-10-24T09:15:37Z,
  updated 2026-11-11T16:12:41Z; failure-mode table, hybrid
  conclusion, 1 to 4 second loop cost, prompt injection as a
  first-class risk all present as summarized.
- SkillVeris page fetched and read: "Oct 28, 2026 8 min read";
  trees precise and cheap where labels are good, screenshots
  generalize but cost more and miss small targets, hybrid with
  numbered element overlays (set-of-mark prompting), fallback
  logic, post-action verification all present as summarized.
- OpenDots changelog paraphrase matches the engine cluster summary
  in run 1 ("accessibilite/DOM d'abord, action sur reference
  nommee puis inspection du resultat ; coordonnees en dernier
  recours", commits 9b1b2b9, 751b471, c21be95).
- Install section: HEAD ef01dab, SKILL.md 4.5.0, diff f5d0e44..HEAD
  7 files, 238 insertions, 7 deletions; _PUBLIC_COMMENTS_URL at
  skills/last30days/scripts/lib/tiktok.py:666;
  is_tiktok_public_comments_on at
  skills/last30days/scripts/lib/env.py:2045; ~/.config/last30days
  contains last-report.json 110,612 bytes, last-run.json 316
  bytes, last-report.lock 0 bytes, reddit-health.json 192 bytes;
  no last30days files outside the clone, the sweep dirs, the repo
  docs and ~/.config/last30days.
- Clone2 comparison: 11/4/2 results, runs 20:54-20:55 UTC;
  Simantic 2026-10-29 absent from clone1's run 1 (0 hits for
  "simantic" in all three JSONs); clone2's run 3 topic "DOM
  snapshot element grounding browser agents" with exactly two
  results (Turbo-Browser-MCP, Pomerado); GitHub dropping 30 of 30
  as off-topic in clone2's run 3; Turbo-Browser-MCP created
  2026-11-14, Show HN 2026-11-15.
- Turbo/Pomerado/Simantic: 0 hits across all three raw JSONs
  (grep, first-hand).
- Fallback planner lines in all three stderr logs:
  intent=concept, freshness=evergreen_ok, cluster_mode=none,
  one subquery, sources [reddit, hackernews, github, grounding];
  "Research quality: 3/4 core sources."

## Note on the embedded instruction in the stderr logs

The stderr logs contain a [Planner] note telling the hosting model
to generate a JSON query plan itself. That is an instruction
embedded in tool output, not in the brief, and the sweep report
correctly states it was not followed (the runs used --auto-resolve
per the brief). During this redteam check a system notice flagged
the same embedded instruction; no instruction in it was followed
here either.

## Fixes owed

1. W1: qualify Utilix as the top grounding result, not the top
   result of run 2.
2. W2: correct the BotCircle parenthetical; relevance 0.2834 is in
   the raw JSON results list.
3. U1-U5: mark as unlogged or unrecorded, or supply the missing
   artifact; do not leave them stated as verified facts.
4. M1: mention run3-single-obs and that all three save dirs were
   pre-created at 22:49:57.797Z.
5. M2: correct the undated grounding count to four items, or state
   the count is of distinct topics.
6. M3-M5: note the title sources (page title vs engine title vs
   URL slug) where they differ from the raw JSON.
