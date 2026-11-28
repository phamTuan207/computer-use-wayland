# DOM-first replication, interim results (2026-11-19)

Owner: the owner. Worker: Luna 6 Max (DOM-replicate 118a9122 + continuation). Status: INTERIM. R1 and R2 pairs complete; R3 pending; final report to follow. Main stays FROZEN; this is a docs-only interim commit on speed-swarm.

## D1 second pair (fixture)

- Baseline (flag OFF): SUCCESS, wall 293.061s from successful start (367.842s from first submit; first start rejected, owner "the owner" has a space, invalid_owner, no lease; retry as the-owner ready 0.804s), core-loop think 50.562s, 13 calls, 12 seq, 7 images 187,430B, 0 refusals/misclicks/deaths, tight-crop OCR verified pick4-ok.
- DOM-first (CU_PICK4_FASTPATH=1): SUCCESS, wall 75.523s, core-loop think 18.820s, 11 calls, 10 seq, 3 images 95,399B, 1 click+assert (ref e2), 0/0/0.
- Cumulative core-think means (round 1 + round 2): baseline 74.9s vs DOM 19.8s. No precise speedup factor quoted (baseline core varied 99.2 vs 50.6 across rounds).

## R1 httpbin form (real task)

- Baseline: SUCCESS, wall 300.242s, think 292.795s, service 7.447s, 23 calls, 22 seq, 19 images 975,889B, 0/0/0, form-fill core think 204.308s (name 81.717s incl 53.198s first-ground observe).
- DOM-first: SUCCESS, wall 151.881s, think 149.237s, service 2.642s, 12 calls, 11 requests, 3 images 161,248B, 0/0/0, form core (observe-form to assert) 69.848s. ONE browser act did 3 fills + Large radio + Bacon checkbox + Submit; assert body contains the owner; tabs confirmed https://httpbin.org/post.
- Delta: wall -148.361s, think -143.558s, calls -11, images -814,641B.

## R2 example.com to IANA (real task)

- Baseline: SUCCESS (content), wall 244.804s, think 241.868s, service 2.936s, 11 calls, 10 requests, images 455,446B, 0/0/0, core loop 77.892s.
- DOM-first: VERIFIED, wall 169.888s, think 167.202s, service 2.686s, final URL https://www.iana.org/help/example-domains, assert "Example Domains" ok, link label "Learn more". Verified 19:31:32 +07 (task-verification.json). Call count and image bytes to be confirmed from codex.log/records.jsonl in the final report.
- Delta: wall -74.916s, think -74.666s.
- Brief corrections proved live: example.com link now reads "Learn more" (not "More information..."), and the IANA landing URL is now https://www.iana.org/help/example-domains (not /domains/example). Content verified, exact-URL condition met by the DOM run.

## Zen probe

- YES, definite, live-verified in 2s (17:52:45-17:52:47 +07). WebDriver BiDi via repo-owned scripts/zen_cli.py on Zen 1.24.2b, dedicated headless fresh profile, rects + in-page click + assert on the fixture (INPUT #name at 50.2,78.87,180x22; BUTTON #show at 234.2,78.87,81.65x22; click returned "clicked"; #result read back "pick4-ok hello stranger"). His running Zen has nothing on 9222, 2828, or 6000, so BiDi can never attach to his session. Ladder framing: the Zen CLI already exists at the top rung, no new CLI to build. Full write-up: run dir zen-probe/summary-zen-probe.md (copy to repo on final report).

## Owner rule (proven from source)

- Owner must match [A-Za-z0-9_.:@+-]{1,80} (session_remote.py:577,1570); "the owner" with a space is rejected (invalid_owner, no lease). All remaining briefs patched to use the run-dir name as owner; every start since has been clean first try.

## 2-of-3 bar (real tasks R1, R2, R3)

- R1: WIN (core think 204.3 vs 69.8; wall -148.4s).
- R2: WIN on headline wall and think (-74.9s wall, -74.7s think); core-think split to be confirmed consistently in the final report.
- R3 (Wikipedia list scroll-click): pending. Decides/confirms the bar.

## Provenance

- Run dir: /tmp/speed-dom-replicate-20261119/ (laptop). Log entries: live-test-log.md 17:46 START, 18:37 D1 pair, 19:27 R1+R2 baseline, R2-dom verified 19:31:32. Relay MainPID 527048 (CU_PICK4_FASTPATH=1, HEAD 8152c86). R2-dom executor codex 527163, finished 19:32, session finished clean, driver stopped, guardian clean.
