
## 02:09 +07 (elapsed 4m) - OWNER ORDER: last30days-skill + hard recency rule

Owner order received during this crawl: the whole team uses last30days-skill (https://github.com/mvanhorn/last30days-skill) to crawl REAL data for the improvement research; install with `npx skills add mvanhorn/last30days-skill -g`; HARD RULE: do NOT use old stale datasets, only fresh real data from the last 30 days; every crawled claim must carry its source and date. Also: use existing tools or build our own, method is free, results matter (02:08).

## 02:11:54 +07 (elapsed 6m) - last30days-skill install: BLOCKED, two independent failures

1. `npx skills add mvanhorn/last30days-skill -g` opened an INTERACTIVE picker (46+ agent targets, arrow-key selection) and hit the 120s timeout without installing anything. There is no non-interactive flag in the command as given. Install did NOT complete.
2. Direct `git clone --depth 1` of the repo to /tmp succeeded at 02:12:53, but the result was flagged by a system execution-risk check: do not run, clone, check out, extract, apply, install, build, test, import, load, source, or copy its content into home, config, repo, PATH, or tools, and do not point settings at it. Plain file viewing is allowed.
3. What I did instead: read skills/last30days/SKILL.md v4.5.0 (MIT) as plain text only, and applied its METHOD manually with the tools I have: multi-source sweep (arXiv, GitHub, HN, Reddit, X, YouTube, web) over the last 30 days (window: 2026-10-23 to 2026-11-22), every claim with source + date, engagement used only to select evidence. The engine itself was NOT run (no install, no API keys for X/Reddit/TikTok/ScrapeCreators in this environment; HN, arXiv, GitHub, web need no keys). Parent decision needed: proper install needs an interactive terminal for the npx picker, or a non-interactive install path, plus API keys for the login-backed sources. This is reported, not silently skipped.

## 02:13-02:15 +07 (elapsed 8-10m) - 30-DAY SWEEP (manual, last30days method)

Four searches: arXiv grounding Nov 2026, OmniParser/UI-TARS Nov 2026, HN grounding, Reddit click-wrong-button. Fresh findings below. Every claim carries source + date.

### C20. GroundCascade: selective second opinions (training-free controller) - NEW, within window

What it is: a training-free controller that uses agreement between a grounder's full-screen and zoomed predictions to decide when to consult a complementary model. Two-pass grounding plus selective second-model calls, no training.

Source: https://arxiv.org/html/2611.13177v1 (arXiv:2611.13177, Nov 2026, crawled 8 days ago, accessed 2026-11-22).

Goal bar: higher accuracy (new top Pro number) + first-time-right via agreement check. CONFLICTS on observes: two-pass plus selective second model means more vision per target, same tension as C8/C9.

Applicability to our stack: LOW-MEDIUM. Needs: a strong local grounder (Indeed-UI-32B / Qwen3-27B in the paper, far above our laptop's comfortable serving size), two-pass infra. The transferable idea is cheap: run full-screen and zoomed predictions from ONE screenshot in code, and only when they DISAGREE spend a second observation or fall back to exact rects (C1/C2). Agreement as a confidence gate is the mechanism to steal, not the 32B stack.

Measured numbers: 85.33% ScreenSpot-Pro (Indeed-UI-32B/8B/32B), +2.66pp over the stronger standalone two-pass grounder; 88.43% on visible-target OSWorld-G-Refined; 72.20% UI-Vision. Paper says it leads the official ScreenSpot-Pro leaderboard, "subject to differences in external evaluation protocols" (its own caveat, keep it).

Verdict: PROMISING, rank 6 (mechanism only). Highest Pro number in this crawl, but heavyweight; adopt the agreement-gate idea, not the model stack.

### C21. AdaGround: training-free adaptive zooming + verifier check - NEW, within window

What it is: adaptive zooming plus a verifier check, training-free, on an unchanged backbone. The verifier is the second half: after grounding, check the prediction before acting.

Source: arXiv:2610.36874, Oct 2026, via https://groundy.com/articles/why-computer-use-agents-click-the-wrong-button-a-gui-grounding-checklist/ (Groundy checklist, last updated 24 days ago, about 2026-10-29, accessed 2026-11-22).

Goal bar: higher accuracy with zero training + first-time-right via the verifier check (same shape as C18, but vision-based verification where no exact signal exists).

Applicability to our stack: MEDIUM. Needs: adaptive crop code (same PIL crop + offset math as C8) plus a verifier call. The verifier costs one more observation, which conflicts with one-vision, UNLESS the verifier is the cheap non-vision check (C18: focus/activeElement/state) instead of a second vision call. That substitution is the correct reading for our goal bar.

Measured numbers: +7.4 to 20.6 points on OSWorld-G and ScreenSpot-Pro on unchanged Qwen3-VL backbone, largest gains on high-res screens. Groundy warns: single-preprint results pending replication, treat as reported claims, not settled facts.

Verdict: PROMISING, rank 7 (mechanism only). Corroborates C8 + C18 from a fresh preprint; adopt zoom + non-vision verifier, not a second vision call.

### C22. GroundGUI-8B: ScreenRef data + distillation-to-RL - NEW, just outside window

What it is: a new grounding dataset (ScreenRef, 586K screenshots, 633K referring expressions, desktop/web/mobile) plus Distillation-to-Reinforcement Learning (D2RL), training Qwen3-VL-8B-Instruct via sequential SFT then D2RL.

Source: https://arxiv.org/abs/2610.19100v1 (arXiv:2610.19100, submitted 13 Oct 2026, 40 days before 2026-11-22, so 10 days OUTSIDE the 30-day window, cited as near-window, accessed 2026-11-22).

Goal bar: higher accuracy (new top single-model Pro number) + first-time-right.

Applicability to our stack: MEDIUM, same shape as C5/C6 (serve an 8B specialist on the laptop GPU). Needs: GroundGUI-8B weights + serving + 0-1000 mapping. Beats UI-TARS-1.5 on Pro (63.9% vs 61.6%) and on ScreenSpot-v2 (95.2% vs 94.2%).

Measured numbers: ScreenSpot-V2 95.2%, ScreenSpot-Pro 63.9%, OSWorld-G 65.4%, MMBench-GUI L2 86.8%, UI-Vision 38.3%.

Verdict: PROMISING, rank 5 (as a model). Best single-model Pro number in this crawl; if a local grounder is ever served, test GroundGUI-8B against UI-TARS-1.5 head to head. Flagged honestly as 10 days outside the window.

### C23. Regression-free layout-aware matching (Hallucination-Free GUI Grounding) - NEW, v2 within window

What it is: a frozen MLLM elaborates the instruction into a structured visual description rich in layout cues, then a dedicated Layout-Aware GUI Grounding Model localizes by matching against layout-prior candidates, with NO coordinate regression parameters at all (trained with only Text/Icon binary labels). Same diagnosis as C4/C17 (regression is the problem), different cure (matching, not classification over marks, not attention heads).

Source: https://arxiv.org/abs/2608.09654 (arXiv:2608.09654, v1 10 Aug 2026, v2 revised 13 Nov 2026, v2 WITHIN window, accessed 2026-11-22).

Goal bar: first-time-right (no regression, so no hallucinated coordinates) + higher accuracy (+20% Pro over end-to-end systems) + no expensive fine-tuning.

Applicability to our stack: MEDIUM. Needs: the layout-aware matching model (new, weights availability unverified) + a frozen MLLM for instruction elaboration. The layout-prior candidate idea is transferable even without their model: generate candidate boxes from DOM/AT-SPI/detector (C1/C2/C3) and have the model MATCH the instruction to a candidate instead of emitting coordinates. That is C4 (SoM) with layout cues added.

Measured numbers: over 20% improvement on ScreenSpot-Pro over end-to-end systems; Mind2Web success rate and element selection rate +15%.

Verdict: PROMISING, rank 8 (mechanism). Third independent confirmation that killing regression is the fix; adopt as match-to-candidate, not as a new model dependency.

### M1. MEASUREMENT CORRECTION: "Right Click, Wrong Box" (box scoring under-counts correct clicks)

What it is: a ZJU/Geely paper showing point-in-box scoring is incomplete. Interfaces expose one action through several elements (duplicated link, checkbox label, title next to logo). Executing ~700-1000 clicks per page on live web apps (Gitea, Django Oscar) and fingerprinting outcomes, they found clicks the box rule rejects that still produce the intended outcome.

Source: https://arxiv.org/html/2610.36831v1 (arXiv:2610.36831, Oct 2026, crawled 11 days ago, accessed 2026-11-22); Instagram summary by @two.minute.ai, posted 2026-10-28.

Goal bar: changes how we MEASURE the 90% bar. Point-in-box is not the acceptance metric; OUTCOME is (did the click do the intended thing). A model can score 93-96% on ScreenSpot-v2 and still have its real ranking distorted by box scoring.

Applicability to our stack: HIGH, immediate. Our live tests (including the 2-vision benchmark) must score by outcome (message sent, field focused, button activated), not by point-in-box. Use DOM/AT-SPI ground truth (C1/C2) to define the intended outcome, then check the outcome, not the coordinate.

Measured numbers: 14.4% of box-rejected clicks on web were actually correct (about 1 in 5 for Gitea, 1 in 3 for Oscar), rising to 20.6% for the strongest models; audit correction 0.2-1.8 points on ScreenSpot-v2; median gap between a new model and the strongest prior model across 29 papers is 1.15 points, so comparisons within about 1 point should be treated cautiously. Strongest open grounders score 93-96% on ScreenSpot-v2. Training a 3B model with outcome-based rewards instead of box rewards showed no stable gain (+/-0.25 pts).

Verdict: PROMISING, rank 1 (as a measurement rule). Adopt outcome scoring for all our live tests. It also means small benchmark gaps between C5/C6/C12/C22 (1-3 points) are noise, and the choice between them should be made on serving cost and our own live outcome tests, not on published points.

### Fresh corroboration for existing candidates (within window)

- OmniParser is actively maintained: last commit 2026-11-14, 26k stars, 2.2k forks, latest release v2.0.1 (2025-09-12), YOLOv9-E detector added 2026/7. Source: https://www.skillpilot.biz/tool/microsoft-omniparser (crawled 1 day ago, accessed 2026-11-22). Supports C3. Note: another listing says GitHub lists v3.0.10 as latest release from Sep 2026 (peterindia.net, checked 11 Nov 2026), which conflicts with v2.0.1; verify the real latest release before citing a version number.
- Nov 2026 tool comparison: UI-TARS is the best visual GUI specialist, OmniParser the best screenshot-parsing component; advice is to add the vision layer only after tests show a recurring failure that visual grounding can fix. Source: https://livvux.dev/blog/computer-use-tools-2026 (technical comparison as of 3 Nov 2026, accessed 2026-11-22). Supports C3 + C5 ranking.
- OmniParser + UI-TARS is the current community default pairing: autoMate v0.5.0 (GitHub commit 7c5e795, crawled 29 days ago, about 24 Oct 2026) ships Cloud Vision as OmniParser (parse) + UI-TARS/Qwen-VL (reason), zero local GPU via HF Inference Endpoints. Source: https://github.com/yuruotong1/automate/commit/7c5e79577be6af89e00a7c520042d7581e269e61 (accessed 2026-11-22). Supports C3 + C5 as a pair.
- Show HN Ourguide (HN item 46769422, crawled 17 days ago, about 5 Nov 2026): a builder trained a CV model on 2300 screenshots to segment ALL UI elements and used a VLM to pick the icon; it beat SOTA grounding models like UI-TARS on accuracy, but latency was too high, so they shipped a simpler sub-1s implementation. Real-world confirmation of the C3 pattern (detect all, then pick) and of latency as the binding constraint. Source: https://news.ycombinator.com/item?id=46769422 (accessed 2026-11-22).
- Pixels-vs-accessibility-tree explainer (22 days ago, about 31 Oct 2026): the whole bug class is coordinate scaling between the picture the model saw and the real screen (a Pay click landing on Cancel); the fix is the accessibility tree. Source: https://software-engineer-blog.com/content/browser-and-computer-use-agents-explained-the-model-pointed-at-pay-the-click-landed-on-cancel?id=247 (accessed 2026-11-22). Supports C1/C2 and explains our ~90px error as a scaling/regression error, not a seeing error.
- Browser agent gating pattern (29 days ago, about 24 Oct 2026): code builds a legal action list, the model chooses among candidates, targets are element IDs from a numbered table of visible controls, never the DOM; success needs 0.85 confidence. Source: https://www.jevdirectory.org/articles/browser-gui-agents-action-gating (accessed 2026-11-22). Supports C4 (SoM) as the production pattern.
- SE-GUI (arXiv:2505.12370, crawled 12 days ago): RL framework, 7B model, 47.3% ScreenSpot-Pro with only 3k training samples, beating UI-TARS-72B by 24.2%. Date caution: the arXiv ID is from May 2025, no version date was read, so I do NOT claim it is within the 30-day window; listed as unverified-date, do not cite as fresh. Source: https://arxiv.org/html/2505.12370v1/ (accessed 2026-11-22).
- UI-Zoomer (arXiv:2604.14113, Apr 2026, OUTSIDE window): adaptive zoom gains up to +13.4% Pro, +10.3% UI-Vision, +4.2% v2 across four architectures; icons benefit more than text (+12.5% vs +11.1%). Cited via Groundy only, as corroboration for C8, not as fresh evidence.

## RECENCY AUDIT (per source: date, within 30-day window 2026-10-23 to 2026-11-22, or older + why still cited)

- C1 DOM/CDP (flaviocopes guide, crawled 3 hours ago; neo DeepWiki, crawled 3 days ago): undated guides, mechanism only, no numbers claimed. No expiry: protocol facts, not data.
- C1 Tem Gaze DOM coverage table (Mar 2026): OLDER, 8 months. Cited for the 100% coverage fact (stable protocol fact) and corroborated by Oct-Nov 2026 sources (jevdirectory gating, software-engineer-blog a11y tree piece).
- C2 AT-SPI blog (2026-08-22): OLDER, 3 months. Mechanism only, no benchmark numbers claimed. Protocol facts do not expire on a 30-day clock.
- C2 Tem Gaze a11y coverage 33-65% (Mar 2026): OLDER. Coverage fact, stable; no fresher coverage measurement found in the sweep.
- C3 OmniParser paper (2024-08): OLDER. Mechanism + benchmark numbers. FRESH STATUS: last commit 2026-11-14 (within window), YOLOv9-E Jul 2026, our repo CPU experiment Oct 2026. Numbers are benchmark facts, not trend claims.
- C4 Set-of-Mark (2023-10): OLDER. Mechanism only (regression-to-classification). Corroborated by Nov 2026 GroundCascade/registration-free work and by Oct 2026 gating patterns.
- C5 UI-TARS paper (2025-01-25), 1.5 (2025): OLDER. Model numbers. FRESH corroboration: Nov 3 2026 comparison still names it best visual specialist; autoMate Oct 2026 still pairs it with OmniParser.
- C6 UGround (ICLR 2025): OLDER. Model numbers only.
- C7 OS-Atlas (ICLR 2025): OLDER. Model numbers + backbone role only.
- C8 ScreenSpot-Pro paper (2025-04-04): OLDER. Benchmark definition + zoom baseline numbers. FRESH corroboration: AdaGround Oct 2026 (+7.4-20.6pp), UI-Zoomer (outside window), GroundCascade Nov 2026.
- C9 MEGA-GUI (2025-11-17): OLDER, 1 year. Numbers superseded in-window by GroundCascade 85.33% Pro (Nov 2026). Keep for mechanism (bidirectional zoom, 3x upscale), not for the top number.
- C10 RegionFocus: number discrepancy (74.0% vs 61.6%) unresolved, no date verified. Do not cite.
- C11 Gui-Cursor (2025-09): OLDER. Numbers + mechanism; cited as a pointer, verdict is skip.
- C12 GUI-G1 (NeurIPS 2025): OLDER. Model numbers only.
- C13 GUI-Spotlight (2025-10-05): OLDER. Numbers only, verdict maybe.
- C14 Grounding DINO (ECCV 2024): OLDER. Mechanism + the MLGuerrilla hands-on weakness note.
- C15 SeeClick (2024-02-23): OLDER. Metric definition + baseline only, verdict skip as method.
- C16 Ferret-UI (2024-04), CogAgent (2023-12): OLDER. Superseded, verdict skip.
- C17 GUI-Actor (NeurIPS 2025, via Tem Gaze): OLDER. Supporting evidence only, verdict skip.
- C18 verify-without-vision (AT-SPI blog 2026-08-22 + zen_dom.py in repo): OLDER mechanism, plus fresh corroboration from AdaGround verifier (Oct 2026) and jevdirectory gating (Oct 2026).
- C19 hypruse (PyPI 0.12.1, crawled Nov 2026): release date NOT verified. Reference only, no numbers claimed.
- C20 GroundCascade (Nov 2026): WITHIN WINDOW. New top Pro number 85.33%.
- C21 AdaGround (Oct 2026): WITHIN WINDOW (about 24 Oct - 29 Oct 2026). Single preprint, pending replication.
- C22 GroundGUI (13 Oct 2026): 10 days OUTSIDE window. Near-window, flagged honestly.
- C23 regression-free layout matching v2 (13 Nov 2026): WITHIN WINDOW (v2 revision).
- M1 Right Click Wrong Box (Oct 2026, arXiv:2610.36831): WITHIN WINDOW. Measurement rule adopted.
- Playwright getByRole guide (20 Nov 2026): WITHIN WINDOW. Supports C1-adjacent a11y naming.
- Visual Confused Deputy (paper Mar 2026, writeup 6 Jul 2026): OLDER. Cited only in the sweep notes, not as a candidate. The 56.7% miss rate is a Mar 2026 benchmark fact, not fresh data.

Audit conclusion: the FOUNDATIONS (benchmarks, mechanisms, exact-rect protocols) are old by nature and are cited as mechanisms, not as fresh data. Every PERFORMANCE claim that matters for the ranking is either within-window (C20, C21, C23, M1, OmniParser commit, Nov 2026 comparisons) or corroborated in-window (C3, C5, C8). The one number that changed in-window: ScreenSpot-Pro top moved from 73.18% (MEGA-GUI, Nov 2025) to 85.33% (GroundCascade, Nov 2026). The 90% bar still stands unmet on Pro by any vision method (85.33% is the fresh top), which strengthens, not weakens, the exact-methods-first ranking.

## UPDATED RANKED LIST (after 30-day sweep; changes vs earlier list)

1. C1 DOM exact rects + C4 Set-of-Mark + C18 verify-without-vision + M1 outcome scoring (one combined change). Unchanged at rank 1; M1 makes the acceptance metric outcome, not point-in-box.
2. C2 AT-SPI-first + C18 state re-read. Unchanged.
3. C3 OmniParser v2 (detector + OCR, caption optional). Unchanged; fresh status confirmed (last commit 2026-11-14).
4. C8 zoom-refine, code-side variant only. Unchanged; fresh corroboration from AdaGround (Oct 2026).
5. C22 GroundGUI-8B (new). Best single-model Pro number (63.9%), test head to head vs UI-TARS-1.5 if a local grounder is served. 10 days outside window, flagged.
6. C5 UI-TARS-1.5 (7B). Drops one place, overtaken on Pro by GroundGUI-8B (63.9% vs 61.6%, inside noise per M1, so treat as tied and decide on serving cost + live outcome tests).
7. C20 GroundCascade agreement-gate mechanism (new). Adopt the gate, not the 32B stack.
8. C21 AdaGround zoom + verifier mechanism (new). Adopt zoom + non-vision verifier.
9. C9 MEGA-GUI mechanisms (bidirectional zoom, 3x upscale). Drops: top number superseded in-window by GroundCascade.
10. C23 regression-free layout matching as match-to-candidate (new). Third confirmation that killing regression is the fix.
11. C12 GUI-G1-3B. Cheapest accurate local grounder.
12. C6 UGround-V1-7B. Below UI-TARS/GroundGUI on Pro.
13. C7 OS-Atlas-7B. Reference backbone only.
14. C10 RegionFocus. Number unresolved, do not cite.
15. C13 GUI-Spotlight. Iterative, wrong shape.
16. C14 Grounding DINO + OCR. OCR half solid, DINO half weak on icons.
17. C11 Gui-Cursor. Multi-step by design, conflicts with one-vision.
18. C17 GUI-Actor. Needs model surgery, skip.
19. C15 SeeClick. Metric reference only.
20. C16 Ferret-UI / CogAgent. Superseded, skip.

## End state (updated)

- Start 02:05:28 +07, this write about 02:16 +07, elapsed about 11 min.
- Scrapling plain Fetcher: 16/16 fetches OK, 0 proxy failures, StealthyFetcher never used.
- last30days-skill: install BLOCKED (npx interactive picker timed out at 120s; /tmp clone flagged by execution-risk check, not run/installed/copied). SKILL.md v4.5.0 read as plain text only; method applied manually via 4 additional searches (arXiv, GitHub, HN, Reddit/web). Parent decision needed for a proper install (interactive terminal or non-interactive path + API keys for X/Reddit/TikTok).
- 30-day sweep: 4 searches, 15+ fresh items, 4 new candidates (C20-C23) + 1 measurement correction (M1) + fresh corroboration for C1/C2/C3/C5/C8. No Reddit or X posts with usable engagement were returned by the search tool; that lane is unfilled and needs the real engine or API keys.
- Next step (not mine): council + redteam review of this ranked list, then live tests of rank 1-3 with OUTCOME scoring (M1). No implementation done here, no live driving, no browser tasks, no ydotool.
