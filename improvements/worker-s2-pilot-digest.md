# S2 pilot digest: what predecessors built

Snapshot: Sat 2026-11-21 ~21:26 +07 (14:25-14:28 UTC). 43 requests in 153.6s,
1 request per 2.5s, via Scrapling 0.5.1 Fetcher on the VM. Raw data:
[improvements/s2-pilot-data.jsonl](s2-pilot-data.jsonl) (43 records, 38 x 200,
5 x 403). Sources: Hacker News front page (30 stories) + top 10 threads with
top 2 comments each + GitHub trending overall (16 repos) and Python (22) +
GitHub API metadata for the top 10 (5 of 10 failed, see Limits).

## Hacker News front page

- The day belongs to math. Two claimed proofs of the Generalized Riemann
  Hypothesis top the page: Levent Alpoge (2746 pts, 1922 comments,
  https://news.ycombinator.com/item?id=50574968) and Alessandro Masullo
  (2240 pts, 1058 comments, https://news.ycombinator.com/item?id=50579568).
  Terry Tao blogged on the Navier-Stokes/GRH connection (481 pts). Comments
  already carry a claimed counterexample to one proof. A proof claim is news;
  verification is the real event.
- AI models: Inkling 2 Mini from Thinking Machines (1136 pts,
  https://news.ycombinator.com/item?id=50581260), a looped transformer
  matching Qwen3-8-27B quality; commenters ran it locally on a Ryzen at
  27 tokens/s. "Language Models Can Rewrite Their Own Weights"
  (440 pts, https://arxiv.org/abs/2611.21885). Nasdaq erased all 2026 gains
  on an AI sell-off (388 pts, 696 comments).
- Craft and careers: "We promoted developers into architects without
  informing them" (498 pts). Ask HN from a developer unemployed 2 years with
  15 years of experience (318 pts, 324 comments): the job market is the other
  side of the AI story. Slopstrap, a CSS kit that makes a site look hastily
  vibecoded (368 pts): the joke lands because the look is now recognizable.
  DreamCoder, a coding harness and IDE from the Mastering Emacs author.
  NINLIVE, a Nine Inch Nails live archive. Brazil's tax authority
  open-sourced its tax calculator under MIT.

## GitHub trending

- Agent skills are the format of the moment: Claude-BugHunter (+1794 stars
  today, https://github.com/elementalsouls/Claude-BugHunter, 82 skills and
  15 slash commands for bug hunting and red-team work), superpowers (+884,
  https://github.com/obra/superpowers, an agentic skills framework and dev
  methodology), diagram-design (+582, 69.6k stars total,
  https://github.com/cathrynlavery/diagram-design, diagram skills for Claude
  Code, Codex, Copilot and Cursor), last30days-skill (+566, 71.7k stars,
  https://github.com/mvanhorn/last30days-skill, the exact skill the owner
  saved on 21/11).
- CLI-Anything (+767, https://github.com/HKUDS/CLI-Anything): "making ALL
  software agent-native". The owner already cleared its license; it is
  trending today, so the idea is in the air, not a secret.
- Firecrawl (+999, https://github.com/firecrawl/firecrawl): scraping and
  search infrastructure for agents, the paid counterpart to Scrapling. Worth
  studying as the productized version of what Scrapling does free.
- minimind (+488, https://github.com/jingyaogong/minimind): train a 64M LLM
  from scratch in 2 hours. Tiny-model training as learnable content.
- Also trending: cursor/plugins (+261, 18k stars), opensre (CI/CD
  reliability agent), google-labs-code/stitch-skills.

## Patterns worth learning

1. Ship skills, not apps. The highest-velocity format is a bundle of markdown
   skills plus slash commands that plug into Claude Code, Codex or Cursor.
   Distribution is a GitHub repo, not a store.
2. Methodology sells. superpowers and Claude-BugHunter sell a way of working
   (red-team, bug hunting), not a tool. The owner's computer-use error file
   is the same shape: a methodology others could run.
3. Make existing software agent-native. CLI-Anything's whole thesis is
   wrapping CLIs so agents can drive them. The user's own work (zen-mcp,
   overlay CLI) is this pattern.
4. Tiny and local wins attention. minimind (64M model in 2h) and Inkling 2
   Mini running on a Ryzen prove small and local is a story, not a compromise.
5. Scraping is infrastructure, not a side quest. Firecrawl at +999 stars a
   day shows the market pays for agent data access. Scrapling is the free
   layer under it.

## Not worth copying

- Unverified proof claims. The GRH threads are spectacular and already
  contested; chasing the headline without the verification is slop.
- Launch-day star spikes. +1794 stars in a day is a launch, not durability.
  Check back in a month before treating a trending repo as proven.
- The vibe-coded look. Slopstrap is a joke about a real aesthetic problem;
  shipping slop on purpose is still slop.
- Hype job-market takes. The Ask HN thread is 324 comments of pain; it is
  data about the market, not a business idea.

## Pilot limits (honest)

- Snapshot only: one front page at one time, top 2 comments per thread.
- GitHub API metadata failed for 5 of 10 repos (403). Cause proven by a
  follow-up call to /rate_limit: the shared egress IP had used 60/60
  unauthenticated core requests per hour (0 remaining, reset 14:32:19 UTC).
  Trending HTML worked 10/10 and is the reliable layer; API enrichment needs
  a token or a wait for reset.
- No X or YouTube: the stealth browser path is blocked on this VM (S1).
- Nothing here was verified beyond the crawl: star counts, claims and
  benchmarks are as the sources state them.
