# Batch 8 sweep, council 3: sections 4, 5, 6 of docs/clone1-last30days-sweep-20261122.md

Date of work: 2026-11-22. Verifier: council 3 (independent of the
sweep report author). Method: first-hand checks only. I read
clone2's sweep report docs/clone2-last30days-sweep-20261122.md in
full, parsed the three raw JSONs in ~/workspace/b8t1-sweep/run1-dom,
run2-a11y, run3-multi with python3, grepped all three JSONs for
"simantic", "turbo" and "pomerado", fetched the Utilix and SkillVeris
pages and read them, checked birth times of the save dirs, and
checked the user-confirmation record in coord/clone1.md.

Verdict: the conclusions of sections 4, 5 and 6 SURVIVE. Two wrong
facts were found, both citation-level, neither changes any
conclusion. Two minor corrections are owed. No fabricated item, no
wrong finding.

## 1. Section 4 AGREE items

- A1 Run 1 is clone2's run 1 minus Simantic: CONFIRMED. All 10
  titles and published_at dates in my run1-dom JSON match clone2's
  run 1 list item for item (Subvocal 2026-11-02, BotCircle
  2026-10-22, Ask HN 2026-11-06, Zeus 2026-11-20, Botel 2026-11-06,
  transitive policies 2026-11-14, Aisync 2026-11-10, Airlock
  2026-11-09, Beolis 2026-10-30, Don't Yell at Your Agents
  2026-10-22). Simantic (2026-10-29) is the only item missing.
- A2 BotCircle issue 8 corroborates the blind-click failure and
  the DOM/a11y-first fix direction, in both sweeps: CONFIRMED. My
  run 1 JSON has candidate_id
  https://github.com/Sr-0w/BotCircle/issues/8, published_at
  2026-10-22, relevance_score 0.2834, and its summary quotes the
  OpenDots commits 9b1b2b9, 751b471, c21be95 and
  "accessibilite/DOM d'abord", matching clone2's report section
  3.2 (relevance 0.283 there).
- A3 Run 2 dated items match clone2's: CONFIRMED. Bolt's Scooters
  2026-11-17, Apple TV sign language 2026-11-11, Tangled hiring
  post 2026-10-31, all present with those published_at dates in
  my run2-a11y JSON, matching clone2's run 2. The unrelated GitHub
  PR is memorygarden pull 216, published_at 2026-11-10, title
  "Plant placement and quality", exactly as the report names it.
- A4 Source pattern matches: CONFIRMED. Reddit unreachable or
  no-results in all runs on both sides (mine: run 1 unreachable,
  runs 2 and 3 no-results; clone2: unreachable in all three). No
  API keys, so X, YouTube and TikTok contributed nothing on both
  sides. Cookies off on both sides.
- A5 No new Firefox or Zen specific grounding method in the
  window, in both sweeps: CONFIRMED. Nothing in my three JSONs is
  Firefox or Zen specific; clone2's report says the same.

## 2. Section 4 DIFFER items

- D1 Run 1, 10 results here versus 11 in clone2's, Simantic
  absent: CONFIRMED. Grep over all three raw JSONs returns 0 hits
  for "simantic". Simantic (2026-10-29) is inside the window, so
  its absence is a ranking difference, not a date exclusion, as
  the report states.
- D2 Run 2, 9 results here versus 4 in clone2's, grounding lane
  reachable here and unreachable in clone2's: CONFIRMED. My run 2
  JSON has 5 grounding items (Utilix, arXiv 2608.24898, dark
  factory knowledge base, SkillVeris, Aria-UI arXiv 2412.16256).
  Clone2's run 2 had 4 results total with grounding unreachable.
  The breakdown is right: 2 in-window explainers (Utilix,
  SkillVeris), 2 out of window by arXiv ID (2608 is Aug 2026,
  2412 is Dec 2024), 1 undated (dark factory).
- D3 Run 3, 14 results here versus 2 in clone2's, different topic
  string: CONFIRMED. Clone2's run 3 topic was "DOM snapshot
  element grounding browser agents" (its section 2 table); mine
  was "single observation multi-action browser agents". Grep over
  all three of my JSONs returns 0 hits for "turbo" and 0 hits for
  "pomerado", while clone2's run 3 returned exactly those two
  (Turbo-Browser-MCP, Show HN 2026-11-15, relevance 0.361;
  Pomerado, Launch HN 2026-11-11, relevance 0.337). My run 3
  GitHub lane returned no results (source_status no-results);
  clone2's run 3 also ended with Github 0 results after dropping
  30 of 30 as off-topic.
- D4 Run 3 topic wording is the reason the headline findings
  differ: CONFIRMED as a supported inference. Clone2's one new
  usable implementation came from its run 3 topic, which my runs
  did not repeat, and no other run of mine returned it.

## 3. Section 5, new versus already known

- S1 The "already known" list (HCU batched actions with a live
  guard and a diff, Mantis numbered compact text with diff-only
  updates, DOM value readback as the cheap verify, plan-once
  execute-all, exactly-once concern as combined-design gap D4
  with no mechanism): CONFIRMED as a faithful restatement of
  clone2's report section 4, which lists the same five items in
  the same words. The underlying batch 7 and click2 crawls were
  not re-verified here; that is outside this check's scope, which
  is only as far as the report documents it.
- S2 Two in-window explainers corroborate the hybrid design:
  CONFIRMED first-hand by fetching both pages. Utilix,
  https://www.utilix.tech/blog/computer-use-agents-screenshots-accessibility-trees-grounding,
  shows Published 2026-10-24T09:15:37Z and Updated
  2026-11-11T16:12:41Z, and its content matches the report's
  summary (hybrid conclusion, loop cost roughly 1 to 4 seconds
  per model round-trip, the screen as untrusted input with prompt
  injection as a first-class risk). SkillVeris,
  https://www.skillveris.com/blog/screenshots-vs-accessibility-trees-for-agent-grounding,
  shows "Oct 28, 2026 8 min read", and its content matches the
  report's summary (trees precise and cheap where labels are
  good, screenshots generalize but cost more and miss small
  targets, hybrid with numbered element overlays, fallback logic,
  post-action verification). Both are corroboration, not a new
  method, as the report states.
- S3 BotCircle issue 8 reproduced as independent field evidence:
  CONFIRMED (see A2).
- S4 Nothing in my runs contradicts the combined design, and my
  runs neither confirm nor refute Turbo-Browser-MCP: CONFIRMED.
  No item in my three JSONs contradicts the hybrid design; the
  explainers support it and the rest is noise. Turbo is absent
  from my runs, not contradicted by them.
- S5 The directly usable next step from clone2's sweep still
  stands (read Turbo-Browser-MCP's submissionKey, expect and
  onlyChanged implementations, port the mechanisms not the
  Chromium driver): CONFIRMED as a faithful restatement of
  clone2's report section 4. My runs add nothing to it except
  the two explainer corroborations, as the report states.

## 4. Section 6 limits and the duplicate-agent qualification

- L1 The duplicate-agent qualification is stated honestly:
  CONFIRMED. The report discloses the duplicate execution in
  sections 0, 2 and 6. Birth times on disk support it: all three
  save dirs (run1-dom, run2-a11y, run3-multi) were created at
  2026-11-21 22:49:57.797Z, 30 seconds after the user's 05:49
  confirmation (22:49:27Z), and the timing files show the runs
  sequential (run 1 22:50:11Z to 22:50:23Z, run 2 22:50:38Z to
  22:50:49Z, run 3 22:50:58Z to 22:51:14Z). The report's claim
  that every number was verified first-hand from the artifacts
  is consistent with the artifacts being complete on disk.
- L2 Empty directory ~/workspace/b8t1-sweep/run3-single-obs:
  FOUND, 0 bytes, created 2026-11-21 22:50:09.342Z. No reference
  to it exists in any log, timing file or JSON under
  ~/workspace/b8t1-sweep. It is an unused leftover save dir,
  almost certainly created by one of the two duplicate agents for
  run 3 (its name matches the run 3 topic, "single observation")
  while the actual run 3 used run3-multi (started 22:50:58Z). It
  contains nothing and changes no finding. Minor correction M2
  below: one line in section 6 would close the record.

## 5. Section 2 user-confirmation record

- C1 The user confirmed at 05:49 +07 on 2026-11-22 by tapping
  "Cho chay, lam sweep di": CONFIRMED against coord/clone1.md
  lines 3497 to 3499, heading "DOT 8, VIEC 1, 05:49 ngay 22/11 -
  CHU DA XAC NHAN, SWEEP DANG CHAY" and text "Chu xac nhan trong
  chat luc 05:49 +07 ngay 22/11: cho chay clone o
  ~/workspace/tools/last30days-skill".

## 6. Wrong facts (citation level, conclusions unaffected)

- W1 Section 3.2 calls the Utilix page "(relevance 0.2654, top
  result of this run)". WRONG. In the run2-a11y JSON, Bolt's
  Scooters has relevance_score 0.2868, higher than Utilix 0.2654,
  and the results list order is Bolt first, Utilix second. Utilix
  is the top grounding result, second overall. Correction: "top
  grounding result of this run (relevance 0.2654), second
  overall". The relevance value itself (0.2654) is correct, as
  are the other grounding relevance values I checked (SkillVeris
  0.2229, 2608 0.2443, dark factory 0.2231, Aria-UI 0.0, Medium
  0.2149, browser-act 0.0, BrowserAgent 0.0).
- W2 Section 3.1 says of BotCircle issue 8 "(relevance not shown
  in the raw JSON results list; ...)". WRONG. The raw JSON item
  carries "relevance_score": 0.2834, which matches clone2's
  0.283. Correction: state the relevance as 0.2834.

## 7. Minor issues

- M1 Section 2 says "the run2-a11y and run3-multi save dirs were
  created at 22:49:57Z". INCOMPLETE. Birth times show run1-dom
  was also created at 2026-11-21 22:49:57.797Z; all three save
  dirs share the same birth second. Correction: "all three save
  dirs were created at 22:49:57Z".
- M2 The empty run3-single-obs dir (see L2) is not mentioned in
  the report. One line in section 6 closes the record; its
  absence is not a factual error in any claim.
- M3 Section 4 AGREE bullet "recall is Hacker News plus GitHub
  plus (when reachable) web grounding" could be misread as
  applying to clone2 too, whose grounding was unreachable in all
  runs. The DIFFER bullet immediately clarifies the difference,
  so no correction is needed; noted only as a reading risk.

## 8. Overall

Sections 4, 5 and 6 survive council 3. Every AGREE and DIFFER
item checked out against clone2's report and the raw JSONs, the
two explainer dates were confirmed by fetching the pages, the
user-confirmation record matches coord, and the duplicate-agent
qualification is honest and supported by the on-disk birth
times. The two wrong facts (W1, W2) and two minor corrections
(M1, M2) are citation-level and change no conclusion. Apply W1,
W2, M1, M2 to the sweep report and the task 1 record is clean.
