# Pick 4 D1 baseline browser task (PROVISIONAL, non-Astra)

- Owner: the repository owner. Worker: Luna 6 Max (Codex gpt-6-luna, max reasoning).
- Run dir: /tmp/speed-pick4-20261118/baseline-browser/. Executor summary: summary-baseline-browser.md. Records: records-baseline-browser.jsonl. Log: baseline-browser-codex.log.
- Relay: restarted 07:52 to clean env before launch (new generation dcf39ccf, HEAD c8595f3, no CU_ vars in relay env, no drop-in on disk). Executor shell: CU_PICK4_FASTPATH=unset, CU_CODE_EXEC=unset, 0 pick flags. Broker SOLO, no waiter scripts, direct codex launch.
- Task: the same D1 Chromium task as Pick 4 arm 2. Managed Chromium, open file:///tmp/speed-pick4-20261118/pick4-fixture.html, click "Show result", verify #result contains "pick4-ok". Baseline method: screenshot-based grounding only. Browser observe WITH --image, button grounded by looking at the screenshot, desktop pointer click, verification by desktop screenshot plus tesseract OCR. No DOM ref click, no browser act, no DOM assert.

## Baseline result: SUCCESS

- Wall start (start submit): 2026-11-19 07:55:28.037 +07. Verified: 07:59:55.415 +07. Wall to verified: 267.378s.
- Analyzer task span (first submit to last result): 397.814s. Gap total 394.480s, service total 3.151s, image bytes total 205,348.
- Requests, 13 sequences, all accepted: windows 3, browser 3 (start, tabs, observe WITH --image), desktop observe 4, desktop act 3, status 1 (post-finish), start 1, finish 1. Records 19 lines (16 excluding 3 status polls).
- Browser observes with image: 1 (16,833 bytes, 924x494). Browser observes without image: 0. Browser acts: 0. Asserts: 0.
- Desktop images: 6 (4 observes plus 2 after-act images). Screenshots taken, all for grounding or verification, none forced by failure.
- Evidence: tight-crop OCR of the verify screenshot reads exactly "pick4-ok hello stranger" (full-image OCR misread 4 as d). Name field left empty. Click landed on the button, result text changed.
- Refusals 0, misclicks 0, stale refusals 0, fallbacks 0, session deaths 0, sleeps 0.
- Incidents: first start attempt failed pre-session (timed.py call missing --log, syntax error, no session opened; retried correctly). Alt+F4 act returned ok:false, "window no longer exists" (Chromium already closed before the after-image; the following windows request confirmed the Chromium address gone).
- Teardown: finish ok, driver stopped, guardian clean. Chromium gone from the windows list.

## Think splits (baseline, DECIDE lines)

- windows 17.7, browser-start 9.0, windows-after-start 8.8, browser-tabs 10.1, desktop-observe-focus 8.9, navigate-act 28.1, browser-observe-image 9.7, desktop-observe-ground 17.6, desktop-act-click 63.5, desktop-observe-verify 8.4, desktop-observe-close 96.3, desktop-act-close 11.3, windows-after-close 8.4, finish 44.6 (+4.3 prep), post-finish-status 42.3 (+4.3 prep).
- Core loop think (browser-observe-image + ground-observe + click + verify-observe): 9.7 + 17.6 + 63.5 + 8.4 = 99.2s.
- Post-observe verification work: verify observe result arrived 07:58:33, verified timestamp 07:59:55, about 82s of executor-side OCR work in between (full-image OCR misread, tight crop, re-OCR, visual check). That work is part of the baseline verification cost; the DOM assert needs none of it.

## D1 arm 2 (DOM-first, flag ON) numbers for comparison

- SUCCESS, wall 293.401s (02:24:50.943 to 02:29:44.342, start to assert plus cleanup check). Analyzer span 293.658s, gap 291.334s, service 2.139s, image bytes 39,930.
- Requests 10: windows 2, observe 2, act 2, browser 4 (start, tabs, DOM observe, DOM act), status 0. Browser observes with image 0, without image 1. Browser acts 1. Asserts 1 (passed, ok true, completed 2). Desktop images 2.
- Think splits: browser-start 5.9, windows 16.4, tabs 6.9, desktop-observe 7.8, navigate-act 21.5, browser-observe 7.5, browser-act 13.2, close-observe 45.8, close-act 14.7, windows-after-close 11.2, finish 139.2.
- Core DOM loop think (browser-observe + browser-act): 7.5 + 13.2 = 20.7s.
- Time to assert, DERIVED (not directly reported): analyzer gaps before the browser-act result sum to 80.268s, plus about 1.7s service, so about 82s after start. The reported 293.401s wall includes the 139.2s finish think, which is executor overhead, not task time.

## Delta (baseline minus DOM-first)

| Measure | Baseline | DOM-first | Delta |
|---|---:|---:|---:|
| Time to verified end state | 267.378s | about 82s (derived) | +185s (+226 percent) |
| Analyzer span (first submit to last result) | 397.814s | 293.658s | +104.2s (+35 percent) |
| Core loop think | 99.2s | 20.7s | +78.5s (+379 percent) |
| Click think | 63.5s | 13.2s (click plus assert) | +50.3s |
| Browser screenshots | 1 | 0 | +1 |
| Desktop images | 6 | 2 | +4 |
| Image bytes | 205,348 | 39,930 | +165,418 (+414 percent) |
| Requests (sequences) | 13 | 10 | +3 |
| Broker service | 3.151s | 2.139s | +1.0s |
| Refusals / misclicks / deaths | 0 / 0 / 0 | 0 / 0 / 0 | none |

- The saving is in think, not service: service differs by 1.0s while think differs by 100s or more on every comparable cut.
- The single biggest item is grounding the click from the screenshot: 63.5s of think before the baseline click, against 13.2s for the DOM click plus assert. The second is verification: about 82s of executor-side OCR work after the baseline verify observe, against a DOM assert result that arrives with the act.
- Wall-definition note: the two reported walls are not the same cut. Baseline wall runs start to verified (267.378s). Arm 2 wall runs start to assert plus cleanup check (293.401s). The like-for-like cuts are the rows above: time-to-verified (267.378s vs about 82s derived) and analyzer span (397.814s vs 293.658s). Both cuts point the same way.

## Coordinate-frame note (verified from the records, flagging to the coordinator)

- The executor summary states the click point as global (3762, 1721), window origin (3448, 1509) plus image point (314, 212). The actions file actually sent {"type": "click", "x": 314, "y": 212}, the image point.
- The click still succeeded (result text changed to "pick4-ok hello stranger"), and global (314, 212) is off-monitor (eDP-2 sits at global (2464, 902)), so the driver resolves click coordinates against the passed --observation (window-relative), not as raw global desktop coordinates.
- The grounding itself was correct and screenshot-based; only the frame stated in the executor summary is imprecise. Future briefs should state explicitly that act click coordinates are observation-relative for window observations.

## Verdict: PROVISIONAL

- DOM-first is a real think-time win on the D1 browser task, not just a capability demo. Baseline core loop 99.2s vs DOM-first 20.7s; baseline 267.378s vs about 82s to verified. The mechanism is consistent: vision grounding of the click plus OCR verification costs far more think than a DOM snapshot plus assert.
- Caveats: n=1 per arm; executor think variance is large (both arms carry 100s or more of overhead think in close and finish steps: baseline close-observe 96.3s plus finish 44.6s plus post-finish 42.3s; arm 2 finish 139.2s). The arm 2 time-to-verify (about 82s) is derived from analyzer gaps, not a directly reported timestamp. A second baseline/DOM pair would firm up the factor, but the direction and the mechanism are consistent across every cut.
- Recommendation to the coordinator: DOM-first may land as a capability with a measured think-time win on browser tasks. Do not quote a precise speedup factor from n=1.
