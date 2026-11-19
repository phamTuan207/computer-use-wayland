# TASK 2 RE-MEASURE: H6 page prefetch (harness-prefetch ac3882b) - VERDICT: LOSS (adoption gate bug, root cause proven)

Branch: `harness-prefetch`, HEAD `ac3882b2b3daeb4a7166346064e9b8036218a61b`.
Relay env: `CU_PRECAPTURE=0` (desktop pre-capture OFF in both arms, so only page prefetch differs).
Suite gate on this exact HEAD: Ran 1358 tests in 102.909s, FAILED (failures=7, skipped=2), 0 errors.
Failset identical to the h6 fix gate (same 7 pre-existing failures). Log: /tmp/live-pf2r-20261120/suite-prefetch.log.
Run dirs: /tmp/live-pf2r-20261120/pf2r-baseline, pf2r-method, pf2r-adopt-probe.

## Success bar (from the assignment)
prefetch ok:true AND open reports prefetched:true with the SAME target ID AND
time-to-first-interaction no worse than baseline.

## Baseline arm B1 (no prefetch, fresh load) - MISMATCH on heading, load metrics valid
Executor kitty pf2r-base-exec, gpt-6-luna max, exited naturally. Records 9 lines.
- Wall 64.613s (start submit 05:02:27.537 to mismatch evidence 05:03:32.150).
- Browser start ok, endpoint http://127.0.0.1:9222.
- Open submit 05:02:49.170: ok=true, prefetched=false, load_ms=169.492,
  tab 805F0B2F4E4800604388F44F7D70DFC7 (fresh tab, full navigation cost).
- First successful browser observe 05:03:03.798, TTFI 14.628s.
- Desktop observe capture_ms 60.734, prefetched=false, window 0x5564a6346fd0 (458x581).
- Outcome MISMATCH (per brief step 6, executor stopped, did not guess): the DOM observe
  returned title "Example Domain", url https://example.com/, snapshot d0a3b1ef-55c, but the
  only element was the "Learn more" link (offscreen:true); NO H1 text in the result (the
  broker snapshot lists interactive elements, not headings). The desktop image
  (2998f21771bd.png, viewed by the coordinator) shows the page scrolled below the H1:
  body paragraph text in English/Arabic/Chinese/French/Russian, no heading in the viewport;
  OCR read the body text only. The browser-observe image (a701aac1a22b.png) shows the same
  scrolled viewport. The PAGE is correct (title, URL, body text); the heading is on the page
  but was not captured by either verification channel in this run. The pf2 baseline "verified"
  the heading from title+URL, which is weaker than this executor's H1-text requirement.
- Requests: browser 2, windows 1, observe 1, act 0, status 0, start polls 3.
  Refusals none, session deaths none. Analyzer: service 1.208s, gap 286.609s.
  b1-finish think 223.1s (long close deliberation).
- Floor probe NOT run (executor stopped on the mismatch).

## Method arm B1 (prefetch + open, one shell burst) - PREFETCH ok:true, ADOPTION FAILED
Executor kitty pf2r-method-exec, gpt-6-luna max, exited naturally. Records 9 lines.
- Wall start 05:13:19.072, verification outcome 05:14:52.400, wall 93.328s.
- Browser start ok, endpoint http://127.0.0.1:9222.
- Prefetch submit 05:14:03.782: ok=true, prefetched=true,
  tab 6691BF08CAD1B81BF83B14101915EC59. The Task 4 blocker is GONE: the wrapper read the
  broker session snapshot itself, no token, no "prefetch requires an active computer-use task".
- Open submit 05:14:06.987 (3.205s later, inside TTL 30s): ok=true, prefetched=FALSE,
  load_ms=49.464, tab 86350AA5696A9E99E27D2D24C796E349 (DIFFERENT tab, fresh load).
  Tab IDs do NOT match. Open gave no explicit reason for prefetched=false. No retry.
- First browser observe after open: TTFI 16.010s (baseline 14.628s, +1.382s, within think noise).
- Desktop observe capture_ms 54.406, prefetched=false. OCR read tab text "Example Domz" + body text, no H1.
- Outcome MISMATCH (same heading-verification limitation as baseline).
- Requests: browser 2, windows 1, observe 1 desktop, act 0, status 0, start polls 3.
  Refusals none, session deaths none. Analyzer: service 2.568s, gap 223.825s.
  Floor probe ran (broker finished owner pf2r-method-floor).

## Root cause (code) - URL normalization mismatch in the adoption gate
scripts/chromium_cli.py, ac3882b:
- `validate_url` (line 132) returns the raw string unchanged, so the prefetch record URL is
  "https://example.com" (no trailing slash).
- `_prefetched_target` (line 714) requires `target.get("url") == record["url"]` AND
  `state["url"] == record["url"]` AND `ready == "complete"`. Chromium reports the loaded tab
  URL and `location.href` as "https://example.com/" (WITH trailing slash). The string
  comparison therefore fails DETERMINISTICALLY before the ready check is ever reached.
- `cmd_open` then closes the prefetched target and falls back to a fresh tab
  (PUT /json/new + navigate), exactly as observed.

## Adoption probe (coordinator-run, zero model calls) - root cause PROVEN live
Session pf2r-probe-adopt, generation 921ef558fb30dfd51bd0bddccc015762, wall 05:28:55-05:29:17.
Driver: run-adopt-probe.sh, log probe-driver.log.
- Test A (replication, no slash, 3s): prefetch ok:true tab 9884E6155426FBFA70B8FB611E382985.
  Tabs right after prefetch show that tab with url "https://example.com/" and title
  "Example Domain" (page already loaded). Open: prefetched:false, fresh tab
  FE7D4D3E93CF22BFB67ED6E05AADDB2C, load_ms 55.363. Replicates the method arm exactly.
- Test B (trailing slash, 3s): prefetch https://example.com/ ok:true tab
  7BA0263640DED4A190CFAFCFB4CD5D09. Open https://example.com/: prefetched:TRUE,
  tab 7BA0263640DED4A190CFAFCFB4CD5D09, THE SAME TAB ID, load_ms 13.512.
  ADOPTION CONFIRMED. The only difference from test A is the trailing slash.
- Test C (control, no slash, 12s): prefetch ok:true tab 481DE5E10E3D417A0614FADD1BE260E7.
  Open after 12s: prefetched:false, fresh tab B2D31797E25A2892918FFC246AFF0387,
  load_ms 52.591. Still no adoption after 12 seconds: the readyState hypothesis is RULED OUT.
- Adoption load_ms 13.512 vs fresh-load 55.363 (A) / 52.591 (C): adoption saves ~40ms of
  navigation time on this tiny page (the load is already done in the background tab).
- Teardown: all opened tabs closed (the two already-closed prefetched tabs returned 404 as
  expected, cmd_open closes a failed-adoption target itself), finish ok, driver stopped,
  guardian clean, chromium windows remaining 0. Desktop clean.

## Verdict: LOSS
- Prefetch ok:true: YES (both arms, and all three probe tests).
- Adoption confirmed in the method arm: NO (prefetched:false, different tab).
  The probe proves adoption works ONLY when the URL string matches exactly what Chromium
  reports. The natural URL form a user or model writes ("https://example.com", no trailing
  slash) fails deterministically, for every URL Chromium normalizes.
- TTFI no worse than baseline: YES (16.010s vs 14.628s).
- The fix (2aab1ad + ac3882b) solved the Task 4 blocker (snapshot-based auth) but the
  adoption gate is broken as shipped for normalized URLs. The fix needed: normalize URLs
  before comparing in `_prefetched_target` (and in the record lookup in `cmd_open`), e.g.
  default an empty path to "/" (or compare urlparse components with path normalized).
  Workaround until fixed: pass the URL in its normalized form (trailing slash for a bare
  domain), as test B proves.
- Heading-verification caveat (both arms): the B1 heading check cannot be satisfied by the
  current verification channels (DOM snapshot carries no headings; desktop viewport can be
  scrolled below the H1). This is independent of prefetch and affects both arms equally;
  it does not change the adoption verdict.

## Numbers table
| metric | baseline B1 | method B1 | probe A | probe B | probe C |
|---|---|---|---|---|---|
| prefetch ok | n/a | true | true | true | true |
| open prefetched | false | false | false | TRUE | false |
| open tab == prefetch tab | n/a | NO | NO | YES | NO |
| open load_ms | 169.492 | 49.464 | 55.363 | 13.512 | 52.591 |
| TTFI (open submit to first browser observe) | 14.628s | 16.010s | n/a | n/a | n/a |
| task wall | 64.613s | 93.328s | n/a | n/a | n/a |
| heading verified | MISMATCH | MISMATCH | n/a | n/a | n/a |
