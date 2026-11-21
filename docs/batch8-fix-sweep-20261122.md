# Batch 8 sweep report fixes (council 1/2/3 + redteam)

Date: 2026-11-22. Target: docs/clone1-last30days-sweep-20261122.md,
453 lines before fixes, 491 lines after. 0 em/en dashes in both
docs (verified by grep). No correction below changes any
conclusion of the sweep report: the sweep ran (3 runs, exit 0, 33
results), no new usable implementation appeared in these runs,
the two in-window explainers corroborate the hybrid design, and
the report is honest that its run 3 used a different topic from
clone2's run 3 and therefore neither confirms nor refutes
Turbo-Browser-MCP.

Every correction was verified first-hand against the raw JSONs in
~/workspace/b8t1-sweep/run1-dom, run2-a11y, run3-multi, the
timing.txt and stderr.log files, and stat birth times of the save
dirs, before being applied. Line numbers below are post-fix lines
in the sweep report unless marked pre-fix.

## W: wrong facts, applied

- W1 (council 2, council 3, redteam). Section 3.2 called Utilix
  "(relevance 0.2654, top result of this run)". Wrong: the run 2
  raw JSON has Bolt's Scooters at 0.2868, higher than Utilix at
  0.2654. Fixed at line 235 to "top grounding result of this run,
  second overall".
- W2 (council 2, council 3, redteam). Section 3.1 said of
  BotCircle "(relevance not shown in the raw JSON results list...)".
  Wrong: the run 1 raw JSON item carries relevance_score 0.2834.
  Fixed at line 194 to "(relevance 0.2834 in the raw JSON results
  list; ...".

## Counts and dirs, applied

- M-count (redteam). Section 3.4 and section 6 said three
  grounding items have no established date. Wrong: there are FOUR
  undated grounding items (dark-factory knowledge base, Medium
  multi-agent POC, browser-act/skills, BrowserAgent project page).
  The true split is 2 in-window + 3 out of window by arXiv ID + 4
  undated = 9 grounding items, verified by counting the grounding
  source items in the run 2 (5) and run 3 (4) raw JSONs. Fixed at
  lines 337-340 (section 3.4, with the 2 + 3 + 4 = 9 total now
  stated) and line 467 (section 6).
- M-dirs (council 1, council 3, redteam). Section 2 said only the
  run2-a11y and run3-multi save dirs were created at 22:49:57Z.
  Wrong: stat shows ALL THREE save dirs were created at
  22:49:57.797Z, the same instant. Fixed at line 107. One line
  added in section 6 (lines 479-484) about the empty leftover
  ~/workspace/b8t1-sweep/run3-single-obs (0 bytes, born
  22:50:09.342Z, verified by stat and ls), almost certainly the
  duplicate agent's abandoned run 3 save dir while the actual run
  3 used run3-multi.

## Citation accuracy, applied

- OpenDots label (council 2). "OpenDots changelog" was a loose
  label: the quoted text is the BotCircle issue's own summary of
  the OpenDots fixes (in the result summary field of the run 1
  raw JSON, citing commits 9b1b2b9, 751b471, c21be95), not a
  changelog. Corrected at lines 196 (section 3.1), 429-430
  (section 5), 473-474 (section 6).
- Title sourcing (council 2 M2, redteam M3). Added a "Title
  quoting note" at lines 281-288 stating the rule used: titles
  are quoted from the engine JSON, except the "| SkillVeris"
  suffix comes from the fetched page heading (the run 2 raw JSON
  title is "Screenshots vs Accessibility Trees for Agent
  Grounding" with no suffix), the Aria-UI title drops the
  engine's "- arXiv.org" suffix, and the browser-act title drops
  the engine's "GitHub - " prefix.
- BotCircle title accents (redteam M4). The raw JSON title carries
  French accents; the report had stripped them. Accents restored
  in the quoted title at lines 191-193, which now reads exactly
  as in the raw JSON: "Computer use : clics à l'aveugle / mal
  positionnés (capture après action invisible, grounding des
  coordonnées non vérifié)".
- Long-dash replacement (redteam M4). The raw Subvocal title uses
  an en dash and the raw dark-factory title uses an em dash; the
  report replaces both with commas. The commas are KEPT, per the
  no-long-dash rule, and the replacement is now disclosed in the
  title quoting note (lines 281-288).
- Medium title (redteam M5). The "with Playwright" part of the
  quoted Medium title comes from the URL slug
  (.../building-a-multi-agent-browser-orchestration-poc-with-playwright-...);
  the engine title is truncated with "...". Noted at lines
  308-310.
- BrowserAgent project page (redteam M2, follow-on). Section 3.3
  listed the project page alongside the arXiv paper as out of
  window; the page itself has no date in the engine data. A
  clarifying sentence was added at lines 321-323, and the page is
  now counted among the four undated items in section 3.4.

## Unverified claims, marked (numbers kept, proof not invented)

- U1 (council 1, redteam). Memory figures (155 MB free / 665 MB
  available pre-run; 175/508 after): no memory log exists.
  Marked "(Unlogged: no memory log survives.)" at line 157, and
  the section 6 repeat now points back to section 2 (line 477).
- U2 (council 1, redteam). "ps showed an engine process with the
  exact briefed flags": no ps output is preserved. Marked at
  lines 117 and 130-136: the exact command line,
  --no-browser-cookies, and keyless operation are not verified by
  surviving artifacts; the indirect corroboration is stated
  (topics match the JSON query fields, stderr shows the fallback
  planner with no --plan, JSON outputs exist in the named save
  dirs, source status is consistent with keyless, cookies-off
  runs).
- U3 (redteam). "Two further system execution-risk notices
  arrived during this run": no artifact records them. Marked
  "(unlogged: no artifact records the notices)" at line 139.
- U4 (council 1, redteam). Install timestamps carried from the
  192-line version (clone date check 21:42:40Z, clone took 55.7 s,
  first report written 21:45:46Z): first commit fd250da is
  2026-11-21 21:47:27Z (verified by git log), consistent with the
  write time but not proof. Marked at lines 42-46.
- U5 (redteam). "The word 'single' pulled keyword matches" is an
  inference, not engine output. Labelled as an inference at lines
  300-302 (with the verified correlation, 10 of 10 HN titles in
  run 3 contain the word) and cross-referenced at lines 353-354.

## No correction needed, recorded

- The engine's "Research quality 3/4 core sources" figure is
  quoted faithfully from the stderr logs (council 1 M3); no
  change.
- Council 3 M3 (the section 4 AGREE bullet on recall could be
  misread, but the DIFFER bullet immediately clarifies); no
  change.
- Redteam M6 (the section 0 headline "No new usable
  implementation was found in these runs" can mislead on a skim):
  it is qualified in the same paragraph and in sections 4-6, so
  readability only; no change.

## Nothing refuted

No council or redteam finding was refuted. Every W, U, and M item
above was verified first-hand and applied as stated, except the
three no-change items listed in the previous section.
