# Task 4 B1 baseline (harness-prefetch 56f5af4, CU_PRECAPTURE=0)

Status: SUCCESS. Heading "Example Domain" confirmed by DOM observe.

Repo HEAD: 56f5af4
Relay env: CU_PRECAPTURE=0 (prefetch.conf drop-in), no CU_CODE_EXEC.
Broker: session pf2-base-b1, start submit 01:51:22.808, finish 01:57:16.367.

## Open (fresh tab, no prefetch)
- URL: https://example.com
- Open result (broker, via chromium_cli wrapper): ok true,
  prefetched false, load_ms 232.996, tab 856E9ED5075BE774B7380BFB88F4F851.
- This is the baseline load: a fresh tab load with no prefetched tab
  to adopt, so the full navigation cost is paid.

## Verification
- Browser DOM observe: title "Example Domain", url https://example.com/,
  snapshot 30048a0b-970, image
  /home/james/.cache/agent-computer-use/e364953a7e13.png.
- Time-to-first-interaction (open submit 01:51:40.142 to first
  successful browser observe result 01:51:58.835): 18.693s.
  This is dominated by the executor's think gap between the open and
  the observe, not by the page load (load_ms 232.996).
- Task wall (session start submit 01:51:22.808 to DOM observe result
  01:51:58.835): 36.027s.

## Desktop observe (Chromium window)
- Observe result: prefetched False, capture_ms 41.256, image
  /home/james/.cache/agent-computer-use/2e7b7762757a.png.
- With CU_PRECAPTURE=0 the desktop observe captures live (41.256ms),
  no prefetched frame. This is the baseline capture cost to compare
  against the method arm's desktop observes (also CU_PRECAPTURE=0;
  only the page prefetch differs).
- Note: the desktop observe OCR was noisy (French text and garbled
  characters in the transcript). The executor relied on the DOM
  observe (title/url) for verification, not the desktop OCR.

## Requests and service
- Requests: browser 2, observe 1, windows 1, start 1, finish 1.
  Status polls 3. Service total 1.130s. Image bytes total 101,776.
- Analyze.py: span 353.560s (first submit to last result), gap share
  99.6 percent, service share 0.3 percent. Think gaps: browser-start
  8.5s, browser-observe-dom 25.9s, windows 72.6s,
  desktop-observe-chromium 8.4s, finish 236.0s.
- The 236s finish gap is the executor deliberating after the desktop
  observe (about 4 min of silence, repeatedly listing a nonexistent
  summary.md). It sent finish at 01:57:16. The coordinator killed
  the codex (PID 1101334) at about 01:57:22 while it was composing
  the summary, after the finish; no measurement was lost. This
  summary was written by the coordinator from the codex.log and
  records.jsonl. The executor never wrote its own summary.md.

## Setup notes
- The brief's session.json path
  (~/.local/share/agent-computer-use/session.json) does NOT exist on
  the laptop. The executor got a FileNotFoundError reading it, but
  the broker open succeeded anyway (the broker handles the token).
  The method arm must not depend on that file existing.
- Cleanup (coordinator): closed the Chromium window ("Example
  Domain - Chromium") and the pf2-base-term kitty via
  hl.dsp.window.close after the session finished. Desktop verified
  clean (herdrdrop, Zen Pill fixture only).
