# 30-day sweep: verifying a click without a second vision pass

Batch 9 task 4. Topic: how agents verify a click landed on its target WITHOUT a second screenshot or vision pass (reading DOM state, checking caret and focus, reading session results, and similar).

## How this sweep ran

- Skill: last30days v4.5.0, clone at ~/workspace/tools/last30days-skill, HEAD ef01dab, used from the clone only.
- Engine run: wall 2026-11-21T21:41:31Z to 2026-11-21T21:43:21Z, 110 s elapsed (108.5 s research time per the engine). Date range 2026-10-22 to 2026-11-21.
- Flags: --no-browser-cookies, keyless, no API keys configured on this machine.
- Plan: 4 subqueries submitted (primary, verify-action, a11y-verify, focus-caret). The engine ran 2 of them (primary and verify-action) and dropped the other two; see the recall limits below.
- Targeting: subreddits LocalLLaMA, AI_Agents, ClaudeAI, automation, selenium; TikTok hashtags aicoding, aiagent, computeruse; dev.to tags ai, automation.
- Results: 57 items. Reddit 15, Hacker News 24, dev.to 12, Web 3 (partial), GitHub 3. Follow-up cache ID a5b6ea7091754d1488aca3dd102970a1.
- Raw engine output: ~/workspace/tools/ground-verify-sweep/how-ai-agents-verify-a-click-landed-on-its-target-without-a-second-screenshot-or-vision-pass-raw-v3.md (908 lines plus the WebSearch Supplemental Results appendix). Run log: ~/workspace/tools/ground-verify-sweep/run-log.md.
- Host web searches (2 pre-engine for resolution, 1 post-engine supplement) are appended to the raw file. Every claim below carries its source and date.

## Headline findings

### 1. NEW and usable: the three-facts verification model (dev.to, 2026-11-14)

The single most on-topic piece in the window is "The screen is not the state: verifying that a browser action actually happened, and recovering when it did not", by maptosite, DEV Community, published 2026-11-14T21:35:28Z (https://dev.to/maptosite/the-screen-is-not-the-state-verifying-that-a-browser-action-actually-happened-and-recovering-when-326k). It was found by host web search, not by the engine (see recall limits).

Its model: every web action produces three separate facts, almost never established by the same observation.

1. The input reached the element. The click or keystrokes arrived at the intended control, not an overlay, not a different element with the same label, not a field that re-rendered and dropped it.
2. The page changed in response. Something in the DOM moved: a URL, a status line, a disabled button, a row in a list.
3. The effect persisted somewhere the page does not control. A confirmation number, a record in an account, a message in a recipient's inbox, a charge in a ledger.

Fact 1 is the easiest and least interesting. Fact 2 is what most automation treats as success. Fact 3 is the only one that survives closing the tab, and it is usually checked last, or not at all. The article's tool contract: "act, then read what changed, then read the record. If you cannot read the record, say so instead of inferring it."

The failure modes it names, all verified without a screenshot:

- Optimistic UI. A framework updates state before the server answers. Reading the DOM right after the click tells you what the app hoped would happen.
- Element handles expire. Between the click and the follow-up read, the page re-rendered and every reference points at nothing or at a different node. Recovery is a fresh read of the page before touching it again, not a retry with the old references.
- Same name, different item. Two "Cancel" buttons, one per booking. The defence is to read each control in relation to the surrounding record (whose name, which date, which amount) before acting.
- Overlay interception. A cookie banner or modal covers the target. If the tool reports the element was intercepted by another element, that is the page telling the truth: dismiss the blocker, then re-read.
- Masked screens. When a password, card number or one-time code is on the page, a well-built harness refuses to screenshot. The article says to verify through signals that are not secret: the field's own state after entry (masked length, a "valid" tick, the last four digits where the site shows them), an error region that stayed empty, a button that became enabled, the network-level artefact of the fill itself, and, once submitted, a confirmation page that names the item and amount. If none of those exist, the honest output is "filled, not verified", not "done".
- Retry from the record, not from the log. External actions persist after the response is lost, so the retry rule is: read the current state before acting again; if the state is ambiguous, do not guess in the direction of action; never treat "already done" as an invitation to do it again. The effect key must be derived from the fact (action plus target plus consequential inputs), not from the run that carries it.
- Instrument the delta, not the intention. Log what was expected to change, what actually changed, and where the record can be re-read later when the screenshot is gone.

Usable for this project: the three-facts split maps directly onto the V12 sent-bubble gate (fact 2, the page changed) and the record read (fact 3, the message in the thread). The "filled, not verified" wording and the fresh-read-before-retry rule are directly adoptable. The masked-screen section is the closest published statement to verifying without any screenshot at all.

### 2. NEW and usable: observe-act-observe through the accessibility tree, with machine-readable errors (November 2026)

Vercel Labs' agent-desktop (open source, Apache 2.0, Rust CLI and C library) shipped v1.0.0 on 2026-10-28 and v1.0.2 on 2026-10-30, with v1.3.1 released 2026-11-13. It was covered by several independent pieces in the window, all found by host web search:

- itxtayab, DEV Community, November 2026 (https://dev.to/itxtayab/agent-desktop-let-ai-agents-use-your-computers-apps-without-screenshots-20h): the core loop is three commands, observe, act, observe again. "agent-desktop snapshot --app Finder -i", "agent-desktop click @s8f3k2p9:e8", "agent-desktop snapshot --app Finder -i". Refs belong to their snapshot; when the UI changes an action returns STALE_REF or AMBIGUOUS_TARGET. Checked 2026-11-03: 11,728 stars, 796 forks, about 3,800 stars gained in a single day.
- piekwerk, DEV Community, November 2026 (https://dev.to/piekwerk/vercel-agent-desktop-computer-use-for-coding-agents-through-the-accessibility-tree-5fap): v1.0.2, observe-act-observe loop, STALE_REF and AMBIGUOUS_TARGET errors, retry only when the error disposition says safe.
- gabrielanhaia, DEV Community, November 2026 (https://dev.to/gabrielanhaia/vercels-agent-desktop-lets-coding-agents-click-native-apps-without-moving-your-mouse-38p1): v1.0.2 released 2026-10-30, about 6,900 stars on 2026-11-02. "A successful action does not prove the UI changed", so verify with a follow-up read such as "wait --element ... --predicate value".
- Zhang Xian, November 2026 (https://lxsabrina.github.io/en/agent-desktop-fail-closed-computer-use/): ref resolution re-identifies the element from evidence, evidence has three states (known, absent, unknown), and every result says whether input was sent and whether repeating is safe. Only "not delivered" is safe to retry.
- Abhinav Dobhal, Medium, November 2026 (https://medium.com/@abhinav.dobhal/vercels-agent-desktop-gives-ai-agents-computer-use-without-screenshots-and-it-s-written-in-rust-0270c6bee53b): v1.3.1, about 24.6k stars, 51 releases, snapshot, click, snapshot loop, STALE_REF, AMBIGUOUS_TARGET, INVALID_ARGS.

Usable for this project: the delivery semantics (every result says whether input was sent and whether a retry is safe) are the same property the 2-vision benchmark's exactly-once ledger needs, and the "successful action does not prove the UI changed" line is the published form of the V12 gate. The STALE_REF pattern (a ref belongs to one snapshot, re-identify from evidence before acting) is a concrete design for the re-read fix in the DOM bench. Caveat: agent-desktop is desktop-only (macOS AX, Windows UI Automation, Linux AT-SPI); web pages belong to its sibling agent-browser. The Linux AT-SPI path is the one that matters for this project, and none of these pieces ran it on a Linux desktop with no session bus.

### 3. CORROBORATION: DOM assertions and failure classification in production browser agents (undated)

"Computer-Use Agent Browser Automation in Production: Action Replay, DOM Assertions, and Human Handoff for Stable Web Tasks", oh-bug.com (https://www.oh-bug.com/posts/computer-use-agent-browser-automation-production/), returned by the engine's web lane with date unknown (date confidence low). It corroborates the same shape from a production angle: the model proposes a target, the executor maps it to a DOM or accessibility node, checks the element is visible, stable, can receive events, and is enabled, then acts; every action carries an envelope with preconditions and expected_after_action (for example "result table is visible", "network idle or loading spinner disappears"); failures are classified as observation, location, action, assertion, permission, or uncertain side effects, and uncertain side effects get "query result state; do not blindly retry submission". Its Playwright example asserts toBeVisible and toBeEnabled before clicking. Because the date is unknown, this is corroboration only, not in-window evidence.

A second engine web item, "Computer Use agent: how it works and how to control it", lite.ego.app (https://lite.ego.app/article/computer-use-agent), also undated, compares pixel, DOM, protocol, and API control and argues for state, approvals, evaluation, and evidence. Same status: corroboration only.

### 4. ADJACENT: deterministic verification gates, not click verification

These in-window items are about verification discipline in general, not about verifying a click without vision:

- "AI agents open 17 million pull requests a month. I built a gate that rejects the ones that lie.", dev.to, 2026-11-17 (https://dev.to/aws-builders/ai-agents-open-17-million-pull-requests-a-month-i-built-a-gate-that-rejects-the-ones-that-lie-46n7): a deterministic Python gate that rejects a fix when it cannot prove it. "No model grades the model." The comment thread agrees a hidden suite should block merges and be versioned and probed with known-bad changes. Adjacent: the gate pattern, not click grounding.
- r/AI_Agents, 2026-11-20, "How Do You Make AI Agents Reliable When They Use Multiple Tools?" (https://www.reddit.com/r/AI_Agents/comments/1y136s0/how_do_you_make_ai_agents_reliable_when_they_use/): build a small replay set of real tool-call inputs and outputs, pin the model version. Top comment by u/IrfanZahoor_950: "If the calendar confirms an appointment and the CRM update fails, I'd keep the booking ID and retry just the CRM update. If the calendar times out, I'd check whether the booking went through first." That last line is the retry-from-record rule in miniature.
- r/AI_Agents, 2026-11-14, "If you're building AI apps/agents for companies, where do you test them?" (https://www.reddit.com/r/AI_Agents/comments/1xvo3ku/if_youre_building_ai_appsagents_for_companies/): "Claude grading its own homework is the real bug here." Adjacent: independent checking, not click verification.
- GitHub, 2026-11-16, cogine-ai/CogineBot PR #196, "Stop repeated tool results and show actual completion outcomes" (https://github.com/cogine-ai/CogineBot/pull/196): thin, adjacent. GitHub, 2026-11-07, browseros-ai/BrowserOS PR #3191, "feat(neo): Serve pressSequentially" (https://github.com/browseros-ai/BrowserOS/pull/3191): thin, adjacent. GitHub, 2026-10-29, Paige-Agent-AI PR #3082 (https://github.com/Paige-Agent-AI/Paige-Agent-AI/pull/3082): thin, adjacent.
- Hacker News, 2026-11-17, "Advancing computer-use agents for healthcare teams" (https://openai.com/index/advancing-computer-use-for-healthcare-teams/): on-topic by domain (computer-use agents) but no verification method in the evidence. Adjacent.

### 5. NOISE: what the engine ranked highest is mostly not about this topic

Of the engine's 8 ranked clusters, only cluster 8 (the r/AI_Agents reliability thread, 2026-11-20) is adjacent to the topic. Clusters 1 to 7 are generic AI-agent news: Signal privacy (Hacker News, 2026-11-20, 569 points), coding cost (dev.to, 2026-11-18), Harvard code-review bottleneck (Hacker News, 2026-11-17), the PR gate (dev.to, 2026-11-17), KPMG audit trial (Hacker News, 2026-11-18), an unmapped Maya site (Hacker News, 2026-11-11), and United Airlines banning AI booking agents (Hacker News, 2026-11-11). None of them says anything about verifying a click. The engine's relevance ranking for this niche topic is weak: high-engagement generic AI-agent stories outranked the on-topic pieces, and the two most on-topic dev.to articles in the window never entered the engine's results at all.

### 6. ADJACENT but outside the window: the read-act-read loop (2026-10-20)

"Coordinate Clicks Are a Trap: Driving a GUI Agent Without Pixel Guessing", dev.to, published 2026-10-20T22:03:56Z (https://dev.to/galagent/coordinate-clicks-are-a-trap-driving-a-gui-agent-without-pixel-guessing-452i), is 2 days older than the window start (2026-10-22) and is NOT counted as in-window evidence. It is worth one line because it states the loop plainly: read the accessibility tree before you click, move focus with TAB or arrow keys and confirm the focused field by reading the tree again, verify after every action ("did the screen change at all, did the expected text appear, did the node count change"), treat "nothing happened" as an error, and wait for a specific predicate with a timeout. "Your AI Agent Can't See What It Clicks", dev.to, about 42 days before 2026-11-22, is also outside the window and argues for a second screenshot pass, the opposite approach; it is listed only to mark the contrast.

## What is new and usable versus the rest

- NEW and usable: the three-facts model with its failure taxonomy and retry-from-record rule (maptosite, 2026-11-14); the agent-desktop observe-act-observe loop with STALE_REF, AMBIGUOUS_TARGET, delivery semantics, and retry-only-when-safe (November 2026, five independent pieces).
- CORROBORATION: DOM assertions, action envelopes with expected_after_action, and failure classification (oh-bug.com, undated); pixel vs DOM vs protocol comparison (lite.ego.app, undated).
- ADJACENT only: deterministic gates and hidden test suites (dev.to, 2026-11-17), replay sets and check-before-retry (Reddit, 2026-11-20 and 2026-11-14), the three thin GitHub PRs (2026-10-29 to 2026-11-16), OpenAI healthcare computer-use (Hacker News, 2026-11-17).
- NOISE: the 7 generic AI-agent news clusters the engine ranked above the on-topic items, plus the 12 generic dev.to tag-feed items.
- NOTHING NEW on two specific sub-questions: no in-window source measured how cheap a DOM re-read verify is against a screenshot verify in wall-clock time, and no in-window source described a caret or focus check as the primary click confirmation for a web input (the focus check appears only as one step inside the tree re-read, in the out-of-window 2026-10-20 piece). Both remain open questions for this project, not findings from this sweep.

## Recall limits, stated honestly

- Sources reachable keyless: Reddit, Hacker News, dev.to, GitHub, keyless web (grounding). Sources NOT reachable: X (no bearer token, no browser cookies, and the task forbids cookies), YouTube (yt-dlp is not installed on this machine), TikTok and Instagram (need a ScrapeCreators key), Polymarket (not applicable to this topic), Bluesky, Threads, Pinterest, Digg, LinkedIn.
- The engine ran 2 of the 4 planned subqueries. The a11y-verify and focus-caret subqueries were dropped by the planner, so the accessibility-tree and focus-check angles were covered only by the host web searches, not by the engine.
- Reddit's primary path failed on all 5 targeted subreddits (IncompleteRead connection errors on every page 1 fetch) and on the global search. The 15 Reddit threads came from the ArcticShift listing supplement (105 posts recovered, 75 dropped by the relevance floor, 30 kept, 20 then pruned). Reddit coverage is supplement-only and thinner than the count suggests.
- Web (grounding) was partial: "Keyless web search unavailable", 3 items only, 2 of them undated (oh-bug.com and lite.ego.app). The third, appscale.blog (https://appscale.blog/en/blog/computer-use-agent-production-architecture-vm-sandbox-action-audit-2026), was not ranked and its date was not established; it is not cited above.
- The engine's dev.to lane returned 12 items from the generic "ai" and "automation" tag feeds, none of them about click verification. The two most on-topic dev.to articles in the window ("The screen is not the state", 2026-11-14, and the agent-desktop pieces) came from host web search, not from the engine. A sweep that trusts the engine's dev.to lane alone would have missed the best evidence.
- What a keyed sweep could change: an X bearer token would add X threads from agent builders (the launch posts for agent-desktop went up on X first); yt-dlp would add YouTube transcripts, where tool walkthroughs usually demonstrate the verify loop; a ScrapeCreators key would add TikTok and Instagram demos. None of those sources is likely to overturn the two headline findings, which already agree with each other, but they could add a measured timing comparison for DOM re-read versus screenshot verify, which this sweep did not find.
- No old datasets were used. Every dated claim above is inside 2026-10-22 to 2026-11-21 unless it is explicitly labelled undated, adjacent, or outside the window.
