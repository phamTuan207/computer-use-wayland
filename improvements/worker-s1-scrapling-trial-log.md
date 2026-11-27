# Worker S1: Scrapling trial log

Sat 2026-11-21 ~21:06-21:20 +07, VM. Owner sent a TikTok clip (@beeknoeeai) about
Scrapling and ordered us to use it to crawl real data more powerfully and learn
from people who went before. Small bounded trial only: install, verify, one tiny
public crawl, report. No big crawl, no protection bypass, no live Zen slot touched.

## 0. What Scrapling is (verified by web search, Nov 2026)

- Repo D4Vinci/Scrapling, author Karim Shoair, BSD-3-Clause, free, no paid tier.
- ~100k stars, latest v0.5 / v0.5.1, Python 3.10+.
- HTTP fetchers (curl_cffi TLS impersonation), stealth browser fetcher (Playwright
  based), parser with adaptive selectors, spider crawlers, CLI, MCP server.
- README: learning/research only, misuse is the user's responsibility. The clip
  framed it as an ethics question (public data readable vs permission to take it);
  it named NO crawl sources.

## 1. Install (VM, Python 3.12.3, pip 24.0)

- `pip3 install --user scrapling` FAILED: PEP 668 externally-managed environment.
  System pip refuses; venv required.
- First venv in /tmp FAILED at the fetchers extra: /tmp is a 512M tmpfs, 399M used,
  `pip install scrapling[fetchers]` died with Errno 28 No space left on device.
  Lesson: never put a venv on /tmp here; /home has 101G free.
- Final venv: `python3 -m venv ~/workspace/scrapling-trial-venv`
  - `pip install scrapling` : 17.1s, scrapling 0.5.1 (cssselect, frostwork, lxml,
    orjson, tld, typing_extensions, w3lib).
  - `pip install "scrapling[fetchers]"` : 19.7s, adds curl_cffi 0.17.0, playwright
    1.65.2, patchright 1.64.4, browserforge 1.2.4, apify-fingerprint-datapoints.
  - `pip install "scrapling[ai]"` (for the MCP server): 48.1s, adds mcp 2.3.0,
    pydantic 2.14.4, markdownify 1.2.4, starlette/uvicorn, beautifulsoup4.
- Gotcha 1: base install does NOT include curl_cffi, so `from scrapling.fetchers
  import Fetcher` raises ModuleNotFoundError until the fetchers extra is added.
- Gotcha 2: `scrapling mcp` does NOT start without the ai extra: it crashes at
  import with `ModuleNotFoundError: No module named 'pydantic'`.
- Gotcha 3: names changed from older docs. In 0.5.1 there is NO `DynamicFetcher`
  and NO top-level `Spider`. Real names: `Fetcher`, `AsyncFetcher`,
  `StealthyFetcher` (from scrapling.fetchers), `Adaptor` (= `Selector`, from
  scrapling.parser), `Spider` (from scrapling.spiders). CLI binaries: `scrapling`
  and `scrapling-mcp`; `python -m scrapling` does not work.
- Import check (0.71s): Fetcher, AsyncFetcher, StealthyFetcher, Adaptor, Spider
  all import clean. CLI `scrapling --help` lists: extract, install, mcp, shell.

## 2. Tiny trial crawl (robots.txt checked first)

- example.com/robots.txt: 404 (no file). Page itself says doc examples need no
  permission. One fetch only.
- httpbin.org/robots.txt: 200, `User-agent: * / Disallow: /deny`. /html allowed.
- Script: /tmp/s1-trial.py, venv python, total wall 3.4s.
  - A: example.com, Fetcher.get, 0.71s, status 200, body 577 bytes, title
    "Example Domain", p extracted. h1 is None: the page has no h1 (correct).
  - B: httpbin.org/html, Fetcher.get, 1.59s, status 200, body 3741 bytes, h1
    "Herman Melville - Moby-Dick", first p extracted.
- Gotcha 4: `Selector.text` is the element's DIRECT text only (`root.text`), so
  `page.text` on the root is empty. Raw body is `Response.body` (bytes).
  `get_all_text()` gives the full visible text. My first script measured
  len(page.text) = 0 and crashed on the missing h1; both were my errors, not
  Scrapling's.
- No page blocked the fetch. Nothing was evaded.

## 3. Adaptive selector (the headline feature)

- `find_similar()` (AutoScraper-inspired): from one element, finds siblings at
  the same depth/tag/parent. Offline test on local HTML, 3 product cards:
  first card found by selector, find_similar returned the other 2 (Beta, Gamma).
  Same after renaming classes (card -> item-box). Works.
- Real adaptive relocation: `Adaptor(html, url=..., adaptive=True,
  storage_args={"storage_file": ...})` + `css(selector, adaptive=True,
  identifier=..., auto_save=True)` stores the element signature in SQLite.
  Test (/tmp/s1-adaptive.py): learned `.card` on v1; on redesigned v2 (classes
  renamed to .item-box) plain `find(".card")` returns None (control), while
  adaptive `css(".card", adaptive=True, identifier="product-card")` relocated
  to the `.item-box` div with "Alpha Widget". PROVEN.
- Gotcha 5: adaptive params live on `css()`/`xpath()`, NOT on `find()`/`find_all()`.
  Passing adaptive=True to find() raises TypeError (only string values accepted
  for kwargs). This is the single sharpest API footgun in the trial.

## 4. MCP server

- `scrapling mcp --help`: stdio default; --http on 127.0.0.1:8000 needs a token
  (SCRAPLING_MCP_AUTH_TOKEN or --auth-token), --no-auth refuses without token.
- Smoke test (/tmp/s1-mcp.py): stdio initialize answered in 1.8s, tools/list
  returned 16 tools: browser_open, browser_save_state, browser_load_state,
  open_request_session, close_session, list_sessions, make_request,
  browser_fetch_once, browser_fetch, session_make_request, browser_extract,
  browser_actions, browser_evaluate, browser_network_requests,
  browser_network_request, browser_screenshot, browser_observe.
- Tool call test (/tmp/s1-mcp-tool.py): make_request to example.com, 0.7-1.0s,
  status 200, css_selector "p" returned the paragraph text correctly.
  Quirk: css_selector "title" returned empty content (head element, no visible
  text in the tool's extraction), not a failure.
- Server was NOT wired into anything; stdio smoke test only. Exit -15 in the
  test is my own terminate() (SIGTERM), expected.

## 5. StealthyFetcher (browser path) - NOT PROVEN on this VM

- `playwright install chromium` FAILED TWICE (3m44s, then 6m56s): "Failed to
  download Chrome for Testing 159.0.8154.6 (playwright chromium v1255),
  Download failure, code=1". The CDN itself is reachable (curl to
  storage.googleapis.com returns 200 in 2.6s), so the download failure is
  specific to Playwright's download path, not general network. Stopped after
  2 attempts; no more retries.
- Workaround found: ~/.cache/ms-playwright/ already holds chromium-1187 +
  chromium_headless_shell-1187 (919M, from an older Playwright). StealthyFetcher
  accepts `executable_path`, so I pointed it at that binary.
- Attempt 1 (/tmp/s1-stealth.py): `Page.goto: Timeout 45ms exceeded` - MY bug,
  Playwright timeouts are in ms; I passed timeout=45 meaning 45ms.
- Attempt 2 (timeout=45000): `Page.goto: net::ERR_TUNNEL_CONNECTION_FAILED`.
  Chromium launched fine and navigated, but could not reach the network.
- Attempt 3 (/tmp/s1-stealth2.py): passed the VM egress proxy from env
  (server + username + password, never printed) + extra_flags
  ["--ignore-certificate-errors"]. SAME error: ERR_TUNNEL_CONNECTION_FAILED.
  This matches the known VM lesson (AGENTS.md 2026-11-10 W-MOTION): Chromium
  rejects credentials in --proxy-server, the egress proxy drops unauthenticated
  CONNECTs instead of answering 407, so Playwright proxy auth never engages.
  The documented working route is a local forward proxy on 127.0.0.1 that adds
  preemptive Proxy-Authorization + --ignore-certificate-errors; building that
  is beyond this bounded trial.
- Conclusion: StealthyFetcher LAUNCHES and drives Chromium on this VM, but
  cannot fetch anything until the proxy route is built. The plain Fetcher
  (curl_cffi) works because curl sends Proxy-Authorization preemptively.
  JS-heavy sources stay out of reach until the forward-proxy route is set up.

## 6. Crawl-source proposal (proposal only, NOT crawled)

Goal: learn from predecessors (people who went before) about computer-use /
agent tooling, scraping, and the topics the owner tracks. Sources are ranked by
what Scrapling can actually fetch:

- Hacker News (news.ycombinator.com): static HTML, no login, robots allow.
  Scrapling Fetcher handles it fully. Best first target: front-page + Ask HN /
  Show HN threads about agents, computer use, scraping.
- GitHub trending / search (github.com/trending, api.github.com): static HTML
  for trending pages; API needs no auth for public read at low rate (60/h
  unauthenticated). Fetcher handles trending pages; use the API, not scraping,
  for repo metadata. Good for finding what tools predecessors built.
- Reddit (old.reddit.com / www.reddit.com .json): old Reddit is static HTML,
  Fetcher handles it; the .json endpoints work without login for public subs.
  New Reddit and login-walled subs need a session; do NOT log in, stick to
  public .json + old Reddit. Good for r/Automate, r/webscraping, r/LocalLLaMA.
- YouTube (youtube.com): JS-heavy, anti-bot, consent walls; Fetcher alone will
  mostly fail or return a skeleton. Needs StealthyFetcher or the yt-dlp /
  YouTube Data API route. Do NOT hammer it; use the API or RSS feeds first.
- X / Twitter (x.com): login-walled, aggressive anti-bot. Fetcher cannot do it,
  StealthyFetcher will likely be challenged. Do NOT attempt; use Nitter mirrors
  only if they exist and allow it, or the X API with the user's key if the user ever
  provides one. Lowest priority.
- The last30days skill (github.com/mvanhorn/last30days-skill, 68k stars) already
  covers Reddit + X + YouTube + Hacker News + Polymarket ranking by upvotes and
  real money; the owner saved it 21/11 as "chi luu, khong lam". Scrapling would
  be the FETCH layer under a similar ranking, not a replacement for the skill.

Proposed next step (for Muse + owner to decide): a small pilot spider (Fetcher
only, 1 request per 2-3s, respect robots.txt) over Hacker News front page + top
10 threads and GitHub trending (Python), storing title/url/score/comments to a
JSONL file, max ~50 pages, then a short digest of what predecessors actually
built. StealthyFetcher only if the pilot proves the static layer insufficient.

## 7. Ethics boundary (kept)

Public data only, robots.txt checked before every host, no Cloudflare/login
bypass attempted, no personal data collected, learning/research only, tiny
volume (a handful of requests). No test page blocked us, so no stop was needed.

## 8. Verdict

USEFUL WITH LIMITS.
- Useful: free (BSD-3-Clause), installs in ~90s total, Fetcher + adaptive
  relocation + MCP server all proven working on this VM with real output.
  The MCP server is the most immediately usable piece: 16 tools, stdio, works.
- Limits: base install is a trap (fetchers + ai extras needed, ~90s extra);
  API names drifted from older docs; adaptive params only on css()/xpath();
  .text is direct-text only; the StealthyFetcher browser path is BLOCKED on
  this VM by the proxy (Playwright download fails 2x, existing Chromium gets
  ERR_TUNNEL_CONNECTION_FAILED even with proxy + ignore-cert-errors passed;
  needs the local forward-proxy route from the W-MOTION lesson). JS-heavy and
  login-walled sources are therefore out of reach for now; the static Fetcher
  covers HN, GitHub trending, old Reddit, and public .json endpoints, which is
  where the pilot should start.
