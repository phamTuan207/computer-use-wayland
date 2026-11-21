# Batch 8 sweep council 2: findings (section 3) verified first-hand

Date of work: 2026-11-22, local time Asia/Saigon. Council 2 checked
section 3 of docs/clone1-last30days-sweep-20261122.md (453 lines)
against the raw engine JSONs in ~/workspace/b8t1-sweep/run1-dom,
run2-a11y and run3-multi, and fetched the two explainer pages
itself. Method: parsed all three raw JSONs with python3
(results published_at, relevance_score, source, url, summary,
clusters, freshness_verdicts), and read both pages with
browser.open. No coord edits, no commit, no push.

## 1. BotCircle issue 8: CONFIRMED, with one correction

- Present in the run 1 raw JSON: title "Computer use : clics a
  l'aveugle / mal positionnes (capture apres action invisible,
  grounding des coordonnees non verifie)", source github, url
  https://github.com/Sr-0w/BotCircle/issues/8, published_at
  2026-10-22. The date the report claims is exact.
- The cluster summary and the result summary both contain the
  fix description the report paraphrases, in French: "System
  prompt et description des outils : accessibilite/DOM d'abord,
  action sur reference nommee puis inspection du resultat ;
  coordonnees en dernier recours", with commits 9b1b2b9,
  751b471 and c21be95 cited. The report's English paraphrase
  (accessibility and DOM first, act on a named reference then
  inspect the result, coordinates only as a last resort) is
  accurate in substance.
- W1, WRONG FACT: the report says, at lines 181-183,
  "(relevance not shown in the raw JSON results list; the
  engine cluster quotes the OpenDots changelog: ...". The
  relevance IS in the raw JSON results list: the BotCircle
  result item carries relevance_score 0.2834. Correction:
  delete "relevance not shown in the raw JSON results list"
  and, if the score is wanted, cite 0.2834.
- M1, MINOR: "the OpenDots changelog" is a loose label. The
  quoted text is the GitHub issue's own summary of fixes
  published in OpenDots commits, not a changelog file or
  changelog page. The substance is right; the label should
  read "the issue's summary of the OpenDots fixes". Section
  6 line 442 uses the same label and should be corrected
  with it.

## 2. Two in-window explainers: CONFIRMED, with one correction and one minor note

Utilix, fetched and read at
https://www.utilix.tech/blog/computer-use-agents-screenshots-accessibility-trees-grounding:

- Dates confirmed on the page itself: Published
  2026-10-24T09:15:37Z, Updated 2026-11-11T16:12:41Z. Both
  inside the window. The report's dates are exact.
- Content summary confirmed: hybrid conclusion ("use the
  accessibility tree when it is populated and trustworthy,
  fall back to pixel grounding when it is not, let the model
  see both signals where possible so it can cross-check"),
  loop cost "on the order of 1 to 4 seconds" per model
  round-trip, screen as untrusted input with prompt
  injection as a first-class risk, and the failure-mode
  table (dense/small UI, canvas apps, layout shifts, legacy
  software, cross-platform coverage, CAPTCHA). The report's
  summary matches.
- Relevance 0.2654 confirmed in the run 2 raw JSON.
- W2, WRONG FACT: the report says at line 221 "(relevance
  0.2654, top result of this run)". Utilix is NOT the top
  result of run 2. "Bolt's Scooters Are Becoming
  Accessibility Sensors" has relevance_score 0.2868, higher
  than 0.2654. Utilix is the top grounding-source result of
  the run (0.2654, above the MCP item at 0.2443). Correction:
  "top grounding result of this run", not "top result of
  this run".

SkillVeris, fetched and read at
https://www.skillveris.com/blog/screenshots-vs-accessibility-trees-for-agent-grounding:

- Date confirmed on the page itself: "Oct 28, 2026 8 min
  read". Inside the window. The report's date is exact.
- Content summary confirmed: trees precise and cheap where
  labels are good, screenshots generalize but cost more per
  step and miss small targets, hybrid with numbered element
  overlays (set-of-mark prompting), fallback logic (tree
  when it contains a confident match, visual grounding when
  it does not), and post-action verification (re-capture
  and verify the expected change after each action). The
  report's summary matches.
- Relevance 0.2229 confirmed in the run 2 raw JSON.
- M2, MINOR: the report quotes the title at line 237 as
  "Screenshots vs Accessibility Trees for Agent Grounding |
  SkillVeris". The raw JSON title has NO "| SkillVeris"
  suffix; it is exactly "Screenshots vs Accessibility
  Trees for Agent Grounding". The suffix comes from the
  fetched page's own title, which does carry it. The
  attribution to SkillVeris is correct (the URL is on
  skillveris.com), but the quoted title should be noted as
  the page title, not the engine JSON title.

## 3. Out-of-window arXiv claims: CONFIRMED

All three URLs are present in the raw JSONs with source
grounding and published_at None:

- https://arxiv.org/html/2608.24898 in run 2, relevance
  0.2443. arXiv ID 2608 means August 2026, outside the
  2026-10-22 to 2026-11-21 window. The report's reading
  is correct. Its engine summary matches the report's
  paraphrase: "accessibility-tree extraction is often slow
  and platform-inconsistent, which has pushed some agent
  designs toward pure pixel-level perception".
- https://arxiv.org/html/2412.16256 in run 2, relevance
  0.0. arXiv ID 2412 means December 2024, outside the
  window. The report's reading is correct. Its engine
  summary describes Aria-UI as a large multimodal model
  for GUI grounding, as the report says.
- https://arxiv.org/html/2510.10666v1 in run 3, relevance
  0.0, plus its project page
  https://tiger-ai-lab.github.io/BrowserAgent (relevance
  0.0). arXiv ID 2510 means October 2025, outside the
  window. The report's reading is correct. The engine
  summary describes a browser agent with human-inspired
  browsing actions, as the report says.

The YYMM reading of arXiv IDs is correct in all three
cases. None of the three is counted as an in-window
finding, as the report states.

## 4. Three undated grounding items: CONFIRMED

All three are present in the raw JSONs with source
grounding and published_at None, and the report claims no
date for any of them:

- "Accessibility-tree grounding, the dark factory
  knowledge base",
  https://raghunathnair1-rgb.github.io/kb/accessibility-tree-grounding/
  in run 2, relevance 0.2231. Engine summary describes a
  personal knowledge-base page, as the report says. Not
  fetched, no date claimed. Correct.
- "Building a Multi-Agent Browser Orchestration POC with
  Playwright" (Medium) in run 3, relevance 0.2149. Engine
  summary is about multi-user browser flows, not
  single-observation multi-action, as the report says. No
  date claimed. Correct.
- "browser-act/skills: Browser automation CLI built for
  AI agents" (GitHub repo via the grounding lane) in run
  3, relevance 0.0. Engine summary lists anti-bot walls,
  parallel multi-task execution and multi-session
  operation, as the report says. No date claimed. Correct.

## 5. Grounding dating caveat (section 3.4): CONFIRMED

- freshness_verdicts is [] in all three raw JSONs,
  verified by parsing each file.
- Every grounding-source item in all three runs has
  published_at None: 5 in run 2, 4 in run 3, 0 in run 1.
  No grounding item carries an engine date. The report's
  statement is exact.
- The report's scope limit follows from this: the "in the
  last 30 days" claim applies strictly to the Hacker News
  and GitHub items (which carry engine published_at dates)
  and to the two fetched pages. That framing is honest
  and correct.

## 6. Full date sweep of sections 3.1 to 3.3: CONFIRMED

Every Hacker News and GitHub date the report states in
sections 3.1, 3.2 and 3.3 was checked against published_at
in the raw JSONs. All match exactly: run 1 Subvocal
2026-11-02, BotCircle 2026-10-22, Ask HN 2026-11-06,
Zeus 2026-11-20, Botel 2026-11-06, Transitive Policies
2026-11-14, Aisync 2026-11-10, Airlock 2026-11-09, Beolis
2026-10-30, Don't Yell at Your Agents 2026-10-22; run 2
Bolt scooters 2026-11-17, Apple TV 2026-11-11, Tangled
2026-10-31, memorygarden PR 216 2026-11-10; run 3 zine
folding 2026-11-19, Voyager 1 2026-11-18, single router
WSJ and MSN both 2026-11-15, Fable52 2026-11-12,
accessible color palette 2026-11-21, GPU from a single
NAND gate 2026-11-19, Strand 2026-11-19, single
technology killing oil demand 2026-11-19, Danbooru
2026-11-11. The memorygarden PR 216 "plant placement
game" characterization matches its title. The "Don't Yell
at Your Agents" YouTube link is a Hacker News item with
a youtube.com URL, as the report says.

Relevance scores quoted in section 3.2 and 3.3 all match
the raw JSONs: Utilix 0.2654, MCP item 0.2443, dark-factory
0.2231, SkillVeris 0.2229, Aria-UI 0.0, Medium POC 0.2149,
browser-act/skills 0.0, BrowserAgent items 0.0.

## Verdict

Section 3 stands. All findings are confirmed first-hand:
BotCircle issue 8, both in-window explainers with exact
dates and matching content, all three out-of-window arXiv
readings, all three undated grounding items reported
without a date, and the grounding dating caveat. No
finding is overturned.

Corrections owed, all citation-level, none changing any
conclusion:

- W1: BotCircle relevance IS in the raw JSON results list
  (0.2834). Delete "relevance not shown in the raw JSON
  results list" at lines 181-183.
- W2: Utilix is the top grounding result of run 2, not
  the top result of the run (Bolt's Scooters is higher at
  0.2868). Correct line 221.
- M1: "the OpenDots changelog" is a loose label for the
  issue's own summary of OpenDots fixes; correct at lines
  181-183 and 398 and 442.
- M2: the "| SkillVeris" suffix on the SkillVeris title
  is from the fetched page title, not the raw JSON title;
  note that at line 237.
