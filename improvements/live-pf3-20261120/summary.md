# TASK 1 RE-MEASURE: H6 prefetch URL normalization (harness-prefetch 7c840d7) - VERDICT: WIN

Branch: `harness-prefetch`, HEAD `7c840d7a295be62d9faff2628f3337e92f3323b3`
("fix: normalize root paths for prefetch adoption").
Relay env: `CU_PRECAPTURE=0` (same as the pf2r run, so the adopted load_ms is
comparable). Suite gate CITED, not rerun: post-fix full suite 1362 tests,
7 failures, 0 errors, 2 skipped, failset identical to the 1358-test baseline
(from improvements/h6-prefetch-url-normalization.md in the fix commit).
Run dir: /tmp/live-pf3-20261120/pf3-probe (run-probe.sh, probe-driver.log,
records.jsonl). Scripted probe, zero model calls, one live broker session
(pf3-probe, generation 1d88592de78bd744de7a5ca7681a8a6b).

## Success bar (from the assignment)

Prefetch `https://example.com` then open `https://example.com/` in one active
live task and the same shell burst: open reports prefetched:true, reuses the
prefetch tab id, and load_ms is near the adopted ~13ms figure rather than the
fresh-load ~50ms figure. Baseline arm: no prefetch call, fresh load.

## Baseline arm (no prefetch, fresh load)

- Open submit 06:42:31.055: ok:true, prefetched:false, load_ms=177.439,
  tab A7DF905F15A689FD74C32896E3FBE23E (fresh tab, full navigation cost).
- First browser observe after open: result 06:42:31.675, service 0.287s,
  title "Example Domain", url https://example.com/, snapshot 72f414f6-965,
  image 73,212 bytes. TTFI (open submit to observe result) 0.620s.
- Note: 177.439ms is higher than the earlier fresh-load ~55ms (pf2r probe
  tests A/C: 55.363 / 52.591) because this was the first navigation in a
  fresh browser profile (cold start). The in-session comparison still holds:
  adopted 14.422ms vs fresh 177.439ms.

## Method arm (prefetch no-slash, open trailing-slash)

- Prefetch submit 06:42:32.745: ok:true, prefetched:true,
  tab 1B720CC0CA24915B230B123CCDFD7075. Tabs right after prefetch show that
  tab with url "https://example.com/" and title "Example Domain" (page
  already loaded), plus the about:blank tab.
- Open submit 06:42:35.899 (3.154s later, inside the 30s TTL): ok:true,
  prefetched:TRUE, SAME tab id 1B720CC0CA24915B230B123CCDFD7075,
  load_ms=14.422.
- First browser observe after open: result 06:42:36.319, service 0.289s,
  title "Example Domain", url https://example.com/, snapshot 722f45cf-018,
  image 73,212 bytes. TTFI 0.420s.
- load_ms 14.422 sits next to the prior adopted figure 13.512 (trailing-slash
  probe on ac3882b) and far from every fresh-load figure (49.464-177.439).

## Probe wall and broker service

- Probe wall 06:42:29.794 to 06:42:38.772: 8.978s.
- Browser start ok, endpoint http://127.0.0.1:9222, reused false,
  pid 1332668, start_call 0.166s, ready 0.872s, 3 status polls.
- Broker requests: browser start 1, browser observe 2, finish 1.
  chromium_cli: open 2, prefetch 1, tabs 2, close 2.
  Broker service: browser start 0.300s, observes 0.287s + 0.289s,
  finish 0.272s. 0 model calls, 0 refusals, 0 misclicks, 0 session deaths.
- Teardown: both test tabs closed, the leftover about:blank tab closed,
  finish ok, driver stopped, guardian clean, broker finished owner
  pf3-probe, desktop clean (omarchy terminal + Zen Pill fixture only,
  no Chromium, no kitty).

## Verdict: WIN

The 7c840d7 fix works live. A prefetch of the no-slash URL is now adopted
by an open of the trailing-slash URL: prefetched:true, same tab id,
load_ms 14.422 (adopted range, not fresh-load range). The ac3882b LOSS is
reversed on exactly the failing case. TTFI here is pure service time
(0.420s method vs 0.620s baseline, no Luna think gap in a scripted probe),
so it is not comparable to the executor-arm TTFI figures (14.6s / 16.0s,
dominated by think); the adoption + load_ms evidence is the decisive part
and it is unambiguous.
