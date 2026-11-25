# Lauren Tan workflow: user-behavior testing, researched again (2026-11-26)

Owner order (26/11 05:01): when testing anything involving users, test the way a NORMAL USER behaves, not the way an AI does. Example: an AI opens GPT by direct command; a normal user searches GPT on the web and clicks. Users do not open or use things the way AIs do. Hard rule for every user-facing case. The owner says this principle is part of Lauren Tan's workflow and wants it researched again, then integrated and hardcoded into the team's hard-rule process.

Access date for all web sources below: 2026-11-26.

## 1. Who she is, and her workflow in one paragraph

Lauren Tan, handle @poteto. Finance/accounting background, moved into code. 4 years Netflix, 6 years Meta (React Core team, React Compiler, staff engineer/EM), then Cursor (Member of Technical Staff), now Principal Engineer at SpaceX (formerly xAI) on the Grok Bot team. Source: team synthesis `improvements/lauren-tan-workflow-20261122.md` (22/11, from her talk, the TikTok recap, and independent analyses); talk page https://ai.engineer/talks/O_zcc6Xl12g-all-code-is-slop-except-mine.

Her talk "All Code Is Slop (Except Mine)" (AI Engineer Code Summit, video posted 14/11/2026, https://www.youtube.com/watch?v=O_zcc6Xl12g) and the TikTok recap the team crawled on 21/11 (https://www.tiktok.com/@anythingai39/video/7710239842663288071, @anythingai39, 20/11/2026) describe one system:

- Trust pyramid, widest first: (1) codebase design so the wrong choice cannot be written, (2) deterministic checks (lint, types, tests), (3) runtime/formal verification, (4) text rules (AGENTS.md, skills) only for what cannot be encoded. Human review is the expensive tip, kept last.
- Build the environment before scaling: about 6 months tuning the agent environment before high speed. Install pstack (her open-source Cursor plugin, MIT, https://github.com/cursor/plugins/tree/main/pstack), start with zero skills, add skills only where agents measurably fail.
- Coordinator pattern: bots are managers, not coders. A lead agent breaks work down, delegates to subagents, and reviews diffs itself instead of repeating subagent claims.
- Evidence contract: "done" means nothing without runnable proof. State the finish condition first; match the check to the change; verify on the same surface where the problem appears; the agent that wrote a change never grades it.
- Every correction becomes a rule: architecture change first, then a lint/test, then a skill/rule, human review last ("ngmi").

The team's own record of the clip says the same in one line: "The agent must really run the program, simulate user actions, check the feature actually works, and submit evidence: test results, screenshots, video." (`improvements/worker-w-crawl-clip-20261121.md`, section "What it teaches", point 3.)

## 2. The user-behavior testing component, concretely

This is the part the owner is pointing at. In her workflow it lives in the verification skill, generated per app by `/create-verification-skill`. Sources: pstack upstream (https://github.com/cursor/plugins/tree/main/pstack); a faithful copy of the skill text at https://github.com/smolpaws/smolpaws/blob/HEAD/.agents/skills/create-verification-skill/SKILL.md; independent walkthroughs at https://desty.github.io/en/blog/81-pstack-merge-without-review/ and https://logos52.github.io/wiki/Working-with-Agents/Let-an-agent-check-its-own-work/ and https://thoughtfulbits.ai/how-to-be-like-poteto.

The generated `verify-<app>` skill has five sections plus a feature map:

1. **Launch**: the exact command that starts the app for verification, and how to tell it is ready (a log line, a port answering, a prompt). "Ready" means actually usable, not just "the process answers".
2. **Doctor**: one read-only check that the running instance is worth driving (process up, right build, port owned by us, auth valid).
3. **Drive**: the harness recipe with real selectors/commands from the repo. "Exercise a feature the way a user would." Prefer stable handles (ARIA labels, data attributes, prompt strings, route paths) over screen coordinates and tab order.
4. **Evidence**: proof standards, stated verbatim in the skill: "exercise the real user path, not internal setters or test-only endpoints; capture the action and the resulting state, not just the final screen; verify side effects (files written, rows inserted, messages sent) alongside what's visible; mocks only where a production boundary already isolates the external system."
5. **Cleanup**: tear down only what the run created, never by process name; evidence survives cleanup.

Feature map: one file per user-facing feature, written from the user's point of view. Each answers: what the feature is, **how to get to it (user POV)**, how to drive it with the harness, and what observable end state proves it works. "A proof that drives one convenient entry point is incomplete when the map lists others." The talk page says the same: "A feature map shows an agent how users reach each feature and what to check." (https://ai.engineer/talks/O_zcc6Xl12g-all-code-is-slop-except-mine)

Independent summaries phrase the Drive step exactly as the owner did: "it reaches each feature through the screens as a user would" and "verifier agents that click through the app like a user" (https://logos52.github.io/wiki/Working-with-Agents/Let-an-agent-check-its-own-work/).

Before handover, the generated skill must prove itself end to end once: launch, doctor, drive ONE mapped feature, capture evidence, clean up, and confirm the evidence still exists after cleanup. "A generated skill that was never executed is a draft, not a deliverable."

What this means for the owner's GPT example: the user path to GPT is search-the-web-and-click, or open the homepage and navigate. Opening it by direct command or deep link exercises a different path than any user takes, so it proves nothing about the user's experience. Her Evidence standard says the same thing in general form: real user path, not internal setters or test-only endpoints; the action AND the resulting state, not just the final screen.

Note on scope honesty: her Drive step is about exercising features through the real UI surface once inside the app. The owner's rule adds the entry point: how the user arrives at the app in the first place (web search, homepage, in-app navigation). The two compose: arrive like a user, then drive like a user. The team already has the entry half as the limio rule (2026-11-09: enter via Google search or the homepage, click through sequentially, never jump to a deep URL). This brief proposes promoting that half from a browser-task habit to a hard rule for every user-facing test.

## 3. Proposed hard-rule text (English, for AGENTS.md and briefs)

> TEST LIKE A NORMAL USER (owner hard rule, 2026-11-26): every test that involves a user-facing surface must follow normal user behavior, never the AI way. Enter the way a user enters: search on the web and click, or open the homepage and navigate through the visible UI step by step. Users do not open or use things the way AIs do: a normal user does not open GPT by direct command, they search for it and click. Never prove a user-facing behavior by deep link, direct command, internal setter, or test-only endpoint. Evidence must show the whole path (entry, navigation, action, resulting state), not only the final screen. A test that skipped the user path is not evidence, even if the end state looks right. Restate this rule in every test brief. (Source: Lauren Tan's verification-skill Drive/Evidence standards, pstack; team limio rule 2026-11-09.)

Short form for brief templates (one line):

> User-path test: enter via search/homepage and click through like a normal user; no deep links, no direct commands, no internal setters; evidence shows entry, path, action, and resulting state.

## 4. Integration points

1. **AGENTS.md (standing rules)**: add the full text from section 3 as a dated entry. Change: the rule becomes part of the file every agent reads; the limio entry (2026-11-09) gets a cross-reference so the two are read as one rule (entry + drive).
2. **Worker brief templates**: every brief that involves testing a user-facing surface must carry the one-line short form plus two filled fields: (a) user entry point for this test (search query, homepage, in-app start screen), (b) forbidden shortcuts for this test. Change: a brief without those fields is incomplete and gets sent back, same as a brief without a delivery path.
3. **Test checklists / evidence review**: the coordinator's fast-reject check (working-structure-redesign 5.3) gains one line: does the evidence show the user path, or only the end state? Change: end-state-only evidence for a user-facing claim is returned unread, like a bare "done".
4. **Rung3 test protocol**: runner briefs already navigate the human way under the limio rule. Formalize: the drive starts from a user entry (search engine or homepage), the per-task evidence must include the path taken (search, clicks, landing), and scorers treat a drive that deep-linked past the user path as incomplete evidence. Change: scoring rubric line, not a freeze change; applies to remaining tasks only, recorded in the re-plan.
5. **Cloudflare fix test plan**: see the worked example in section 5. Change: the fix is not "proven live" until the user-way test passes on at least coolors.co and chatgpt.com, with path evidence.
6. **Skill-equipping tests** (owner rule 04:57: a skill counts as equipped only after live use): the live-use test for any user-facing skill must itself follow the user path. Change: equipping evidence records the entry point used.

## 5. Worked example: testing the Zen Cloudflare fix

The bug: Zen launched via the zen-ai wrapper (`--remote-debugging-port=9222 --marionette`) sets navigator.webdriver=true; Cloudflare answers with "Verify you are human" and the page never becomes usable. Seen on chatgpt.com and on coolors.co mid-drive (owner photo, 26/11 04:35). Research record: `improvements/zen-cloudflare-chatgpt-fix-research-20261125.md` in the run worktree.

**The AI way (not evidence):** open chatgpt.com by typing the URL or by a direct navigation command, load coolors.co by deep link, check the DOM renders. This can pass while a real user still hits the challenge, because it skips the path the user actually takes and may skip the exact navigation sequence that triggers the interstitial.

**The user way (the test):**
1. Start from a blank tab or the browser start page, the way a user starts.
2. Type the query into the address bar or a search engine ("coolors", then separately "chatgpt"), press Enter, click the top result.
3. Wait for the landing page. Observe: does the Cloudflare "Verify you are human" interstitial appear? Does it clear on its own?
4. Interact like a user: on coolors.co, scroll and open a palette; on chatgpt.com, click into the prompt box and type a short prompt.
5. Record the whole path as evidence: timed log (wall-clock + elapsed), screenshot or video at each step (search results, click, landing state, interaction result), plus the final state. If the interstitial appears, that is a FAIL with the screenshot as proof; if the page is usable end to end, that is a PASS.
6. Repeat once from a fresh browser start (new session) so the result is not an artifact of a warm profile.

**What counts as proof:** the path evidence above, produced by an agent that did not implement the fix, showing a normal user can search, click, land, and use both sites without the challenge. A DOM dump from a deep-linked page does not count.

## 6. Sources

- Team synthesis (22/11): `improvements/lauren-tan-workflow-20261122.md` (local repo file).
- Team clip crawl (21/11): `improvements/worker-w-crawl-clip-20261121.md` (local repo file).
- Team redesign (21/11): `improvements/working-structure-redesign-20261121.md` (local repo file).
- Talk: https://www.youtube.com/watch?v=O_zcc6Xl12g (posted 14/11/2026); talk page https://ai.engineer/talks/O_zcc6Xl12g-all-code-is-slop-except-mine.
- TikTok recap crawled by the team: https://www.tiktok.com/@anythingai39/video/7710239842663288071 (@anythingai39, 20/11/2026).
- pstack upstream: https://github.com/cursor/plugins/tree/main/pstack (MIT).
- create-verification-skill skill text (faithful adaptation): https://github.com/smolpaws/smolpaws/blob/HEAD/.agents/skills/create-verification-skill/SKILL.md.
- Independent analyses: https://desty.github.io/en/blog/81-pstack-merge-without-review/ ; https://logos52.github.io/wiki/Working-with-Agents/Let-an-agent-check-its-own-work/ ; https://thoughtfulbits.ai/how-to-be-like-poteto ; https://agentspoon.com/en/verification-skills-pstack/.

Caveat carried over from the 22/11 synthesis: her PR counts and revert rates are self-reported and not independently verified; the method transfers, the numbers do not. Nothing in this brief depends on those numbers.
