# last30days scan 2026-11-28: browser-agent improvements, fixes, tricks

Owner order 2026-11-28 06:31: use last30days to scan forums,
social media, and repos for any improvements or fixes for our
stack; then the team meets (council + redteam) on remaining
pain points and decides what to build. This file is Part 1,
the scan. Part 2, the meeting decision, lands in
improvements/pain-point-meeting-20261128.md.

## Method and coverage honesty

Engine: last30days v4.5.0 local engine, run 2026-11-28
06:33-06:36 +07, window 2026-10-28 to 2026-11-27, topic
"AI agents driving Firefox Zen Browser automation MCP
WebDriver BiDi". Available sources per --diagnose: Reddit,
Hacker News, GitHub, Polymarket. X/Twitter was not enabled
(no credentials), YouTube unavailable (yt-dlp not installed),
TikTok/Instagram unavailable (no ScrapeCreators key).

Engine run facts, stated plainly:

- Reddit site search returned HTTP 403 Blocked for this
  network; the engine fell back to the arctic-shift keyless
  lane and still delivered 15 Reddit threads. Reddit
  coverage is therefore partial (listing discovery, not
  search), and the relevance floor dropped most of it.
- Only 2 of the 4 planned subqueries executed (primary,
  bidi). The waits-snapshots and zen-mcp subqueries did not
  run; those angles were covered by host web-search
  supplements below.
- Total engine evidence: 34 items (Reddit 15, HN 12,
  GitHub 7, Polymarket 0). Only 16 of 34 dated items are
  from the last 7 days. Much of the engine output is noise
  for our stack (Firefox memory benchmark, Chrome-power-user
  thread, Google Workspace MCP politics). The genuinely
  applicable findings below come mostly from the supplements
  and from direct verification against primary sources.

Supplements (host web search, then verified by opening the
primary source): Planet Mozilla announcement feed, Mozilla
Discourse release post, Bugzilla, GitHub API reads of three
repos. Every claim below cites a source that was opened.

## Finding 1 (GENUINELY NEW, HIGH RELEVANCE): Mozilla's own Firefox MCP v0.11.1 shipped 2026-11-27

Mozilla's official MCP server (@mozilla/firefox-mcp, 621
GitHub stars, pushed 2026-11-27) released v0.11.1 yesterday.
Verified on Planet Mozilla and the Mozilla Discourse release
post (2026-11-27 10:51, by jdescottes).

What changed that matters to us:

- New `wait_for` tool: waits until a text or an element
  matching a CSS selector is visible, or with `gone` until
  it disappears; searches open shadow roots and same-origin
  iframes; timeout default 5000 ms, max 30000 ms. This is
  exactly the primitive our I17/I10 wait flags approximate,
  and Mozilla shipped it because agents otherwise "take
  snapshots in a loop, or poll with evaluate_script"
  (Bugzilla 2089768, the enhancement request behind it).
- WebDriver sessions can now be restricted to a single
  container (with `--connect-existing`): all events and
  commands limited to that container. A scoping primitive
  we do not have; relevant to our act poolScope disclosure
  work and to any future multi-agent tab sharing.
- Tab management and privileged-context tools moved from
  WebDriver Classic to WebDriver BiDi; the server now uses
  BiDi commands and events only. Direction confirmation:
  the protocol center of gravity is BiDi, not Classic and
  not CDP (CDP was removed from Firefox in 141).
- `take_snapshot` then `click_by_uid` / `fill_by_uid`: the
  same snapshot-then-act-by-reference shape as our P1 + I3.
  Independent convergence on our design.
- Tool presets (slim, basic, developer, mozilla, all)
  control which tools are exposed; the `slim` preset drops
  evaluate_script. This is progressive disclosure (our P5
  pattern) implemented by Mozilla as presets. We rejected
  P5 as a build; Mozilla's version is cheaper (static
  presets, not dynamic disclosure) and worth a second look
  as a pattern, not as a dependency.
- `--idle-timeout` (default 1800s): a connect-existing
  session releases Firefox after inactivity because Firefox
  accepts one client at a time; the next tool call
  reconnects. Directly relevant to our single-session
  constraint and to daemon/agent contention on one browser.
- Fixed: reloading a POST-loaded page no longer blocks on
  the resend prompt (`dom.confirm_repost.testing.
  always_accept=true` by default). A real agent pain point
  with a one-pref fix; check whether our lane hits it.

Sources: Planet Mozilla feed (planet.mozilla.org, crawled
2026-11-27 23:35 UTC); Mozilla Discourse release post
(discourse.mozilla.org/t/firefox-mcp-v0-11-1-released/150479);
Bugzilla 2089768; GitHub mozilla/firefox-mcp (API read
2026-11-28: 621 stars, pushed 2026-11-27T16:08:40Z).

## Finding 2 (GENUINELY NEW): Bugzilla 2081604, page settling after input

The wait_for request (2089768) explicitly separates two
problems: Bug 2081604 covers "letting the page settle after
an input action"; 2089768 covers content that appears a
second or two later. Our P2b settling tests (landed as code,
registry still gated) attack the same settle problem from
our side. Mozilla treating settle as its own bug class
validates the P2b gate structure (settling tests first,
registry after). No new mechanism offered by Mozilla yet;
watch 2081604 for their settle definition.

Source: Bugzilla 2089768 (opened, read 2026-11-28).

## Finding 3 (NEW, PATTERN VALUE): Kitsune, extension-based shared-browser MCP

junyeong-nero/kitsune (48 stars, pushed 2026-11-27, MIT):
MCP server + Firefox add-on for Firefox/Zen/LibreWolf. No
WebDriver; the extension is the bridge. Design points worth
recording even though we will not adopt the extension route
(it requires installing into the owner's profile, which our
R10 decision avoided):

- Agent-created tabs open in the background; selecting a tab
  for the agent does not switch the tab the user sees.
  Directly addresses our focus-steal incident class
  (2026-11-21 live-runner focus steal).
- Handoff model: by default the agent can read user tabs
  but cannot type, navigate, scroll, or close them; it must
  request a handoff, the user approves and can take the tab
  back. This is a consent shape different from zen_ask
  (which the owner rejected): approval is per-tab and
  revocable, not per-action. Recorded as a pattern only;
  the owner rejected being asked back, so any handoff-like
  build needs his explicit word.
- Six tools total (Python for actions plus recovery
  controls): the small-surface end of the spectrum, opposite
  to zen-mcp's 55 and firefox-bidi-mcp's 177.

Sources: GitHub API + README read 2026-11-28
(junyeong-nero/kitsune); r/mcp launch post surfaced via
search (shadowgraph.io mirror, Nov 2).

## Finding 4 (NEW, PATTERN VALUE): claude-for-zen, BiDi with existing profile

ilhamnadhif/claude-for-zen (0 stars, pushed 2026-11-13):
MCP server over WebDriver BiDi (ws://127.0.0.1:9333) for
Zen/Firefox, no extension. Two run modes including
`--existing-profile` (ZEN_PROFILE_MODE=existing), real
trusted input events, isolated page runtime. Glama lists it
with A license / A quality. Small and young, but it is the
closest public analog to our RDP lane's job (drive the
user's real Zen) done over BiDi instead of RDP. Worth a
code read if we ever revisit the BiDi lane; not a candidate
to adopt (0 stars, single maintainer, npm distribution,
which our zen-mcp audit already flagged as a risk class).

Sources: Glama listing (glama.ai/mcp/servers/ilhamnadhif/
claude-for-zen, crawled 2026-11-24); GitHub API read
2026-11-28.

## Finding 5 (CONFIRMS OUR DIRECTION): the field is converging on wait_for + snapshot + scoped sessions

- Playwright MCP has `browser_wait_for`; Chrome DevTools
  MCP has `wait_for`; Mozilla added `wait_for` in v0.11.1
  (Bugzilla 2089768 names both predecessors). Three
  independent implementations of the same primitive.
- agent-browser (Vercel) added a Firefox engine via
  WebDriver BiDi in November 2026 (releases 0.41.1 to
  0.45.0), with full snapshots and element references, plus
  experimental saved flows (record once, replay). Source:
  agentgid.com changelog summary (crawled 2026-11-28).
  Saved flows are a new idea class for us: replayable task
  recordings. Our run logs already capture steps; a replay
  format is a candidate for the pain-point meeting.
- Firefox 155 (2026-09-01) stabilized parallel BiDi +
  DevTools by removing the nested event-loop dependency in
  moz:debugging. Source: en.98ip.com summary of Mozilla MDN
  release notes (secondary source, treat as UNVERIFIED
  until checked against MDN; low stakes either way).

## Finding 6 (RISK CONTEXT, RESOLVED INVALID): Remote Agent network data collection

Bugzilla 2090753 (opened ~2026-11-11, closed RESOLVED
INVALID): an unauthenticated local Remote Agent client can
harvest decrypted request/response bodies via
network.addDataCollector and forge identity headers via
network.setExtraHeaders. Mozilla's ruling: this is how the
protocol is meant to work; the Remote Agent only starts
with --remote-debugging-port, and that mode gives the
connected client full control by design; script evaluation
already gives the same access. For us: no action, but it
confirms the standing rule that our RDP/BiDi ports must stay
loopback-only and that any local process reaching them is
root-equivalent over web content. Our lane already binds
127.0.0.1; keep it that way, and keep the port registry
discipline.

Source: bugzilla.mozilla.org/show_bug.cgi?id=2090753 (read
2026-11-28).

## Finding 7 (NOISE, RECORDED SO NOBODY RE-SCANS IT)

- zen-mcp (spaxe-dev) v0.6.0 Reddit post 2026-11-22
  (r/zen_browser, 35 pts): the same post the owner shared;
  already audited, tested, and adopted-from (PR #1187).
  Community reaction in the engine output is still split
  ("why would anyone want to use an MCP for a browser").
  Nothing new since our audit.
- firefox-bidi-mcp (177 tools, 17 domains): maximal-surface
  design, opposite of our direction; no new mechanism.
- Google Workspace MCP mandate (HN, 420 pts): platform
  politics about Gmail/Drive APIs; the only transferable
  line is the elicitation primitive (server pauses a tool
  call to ask the user), which is the zen_ask class the
  owner already rejected.
- Firefox v10-to-v160 memory benchmark (r/firefox, 382 pts):
  general browser performance, no automation mechanism.
- WebMCP / generate-MCP-servers thread (r/mcp): speculative,
  no shipped mechanism; the one concrete caution (generated
  servers inherit the session's full trust) matches our
  existing security posture.

## What this scan did NOT find

- No new event-feed mechanism that signals load completion.
  Mozilla's own answer to the wait problem is still a
  polling wait_for (text/selector visibility), which
  corroborates our P3 decision (tabNavigated is start-only;
  the feed cannot replace readyState reads).
- No published fix for the stale-actor evaluate hang we
  measured in M1 (5s timeout on the pre-navigation console
  actor). The shipped replay path's recovery number is
  still unmeasured on our side; that gap is ours to close.
- No new snapshot format beating the accessibility-tree /
  structured-DOM consensus; Mozilla, Playwright, and
  agent-browser all ship the same shape we landed in P1.

## Hand-off to Part 2

Candidate inputs for the pain-point meeting, in scan order:
(1) adopt Mozilla's wait_for semantics (gone flag, shadow
roots, same-origin iframes) into our wait primitives;
(2) container-scoped sessions as a scoping primitive;
(3) idle-timeout session release for the one-client lock;
(4) dom.confirm_repost pref check; (5) static tool presets
as the cheap form of progressive disclosure; (6) saved
flows / replay as a new idea class; (7) background-tab
discipline from Kitsune (pattern only). Each needs a
build / not-build decision with evidence; none is adopted
by this scan alone.
