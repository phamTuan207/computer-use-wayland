# Task 4 B1 method (harness-prefetch 56f5af4, CU_PRECAPTURE=0, prefetch call)

Status: PREFETCH FAILED (blocked by a missing session token file).
The open fell back to a fresh load. Heading "Example Domain" verified
twice by DOM observe. No prefetch benefit could be measured because
the prefetch never ran.

Repo HEAD: 56f5af4
Relay env: CU_PRECAPTURE=0 (prefetch.conf drop-in), no CU_CODE_EXEC.
Broker: session pf2-method-b1, start 02:02:32.039.

## Prefetch (FAILED)
- Prefetch call result:
  `{"ok": false, "command": "prefetch", "error": "prefetch requires an active computer-use task"}`
- Cause: the session token file
  `~/.local/share/agent-computer-use/session.json` does NOT exist on
  the laptop (the executor got a FileNotFoundError reading it). The
  chromium_cli prefetch wrapper reads the token from that file; with
  no token it cannot register a prefetch for the active task, so the
  call is rejected before any navigation happens.
- This is the same missing file the baseline arm hit (its broker open
  succeeded anyway, because the broker handles its own token). The
  method arm's prefetch path depends on the file and has no fallback.
- The prefetch was attempted in the required single shell burst
  (prefetch, sleep 3, open), so TTL expiry is not the cause.

## Open (fresh tab, no prefetched tab to adopt)
- Open result (broker, via chromium_cli wrapper):
  `{"ok": true, "command": "open", "endpoint": "http://127.0.0.1:9222", "tab": {"id": "CF3379C90E6F160AC8C0D03449A71922", "title": "Example Domain", "url": "https://example.com/"}, "prefetched": false, "load_ms": 175.874}`
- prefetched false, load_ms 175.874. This is a fresh-tab load, the
  same kind of load as the baseline (232.996ms). The 57ms difference
  is run-to-run noise (and the page may have been cached), NOT a
  prefetch benefit: no prefetched tab existed to adopt.

## Verification
- Browser DOM observe: title "Example Domain", url
  https://example.com/, snapshot ddff8e26-26a. Heading verified.
- Task wall (session start submit 02:02:32.039 to DOM observe result
  02:03:43.091): 71.052s.
- The open submit epoch was not recorded by the executor (its burst
  did not log OPEN_SUBMIT_EPOCH), so the exact open-to-observe
  interval is not available. The open itself took 175.874ms; the
  DOM observe result came at 02:03:43, after the burst reported at
  about 02:03:40.
- Desktop observe (Chromium window): prefetched False, capture_ms
  59.872. With CU_PRECAPTURE=0 the desktop observe captures live;
  the method arm's desktop capture (59.872ms) is in the same range
  as the baseline's (41.256ms), as expected (only the page prefetch
  differs, not the desktop pre-capture).

## Requests and service
- Requests: browser 7, observe 1, windows 1, start 2, status 1.
  Status polls 6. Service total 1.638s. Image bytes total 147,677.
- Analyze.py: span 344.312s (first submit to last result), gap share
  99.4 percent, service share 0.5 percent. Think gaps: browser-start
  8.9s, browser-observe-dom 60.6s, windows 40.0s,
  desktop-observe-chromium 15.5s, h1-check 117.6s, refresh 20.1s,
  status 15.8s, restart1-browser-start 8.2s,
  restart1-browser-observe 9.0s, restart1-h1-check 10.7s.

## Session failures (executor's extra H1 check, NOT prefetch)
- Two driver_command_failed session failures, both caused by the
  executor's extra H1 check (a verification step it added beyond the
  brief, using a snapshot/selector on the page). Neither failure is
  related to the prefetch mechanism.
- H1 check 1 (02:06:36): "Uncaught: Error: stale snapshot" (the
  snapshot from the DOM observe was stale by the time the check ran,
  117.6s of deliberation later). Session failed, stop_reason
  driver_command_failed. The executor's refresh observe was rejected
  (task_stopped).
- The executor restarted the session (b1-restart1, generation
  4781a4144d6f94848a662f6a729f5595, start 02:07:46), re-ran the
  browser start and observe, and re-verified the heading
  (restart1 observe 02:08:05, title "Example Domain", snapshot
  525fa6e5-358). It then ran the H1 check again.
- H1 check 2 (02:08:2x): "Uncaught: Error: selector must match
  exactly one element" (the H1 selector did not match exactly one
  element). Session failed again, same stop_reason.
- The coordinator killed the codex (PID 1108435) at about 02:09:15
  to stop a third restart loop. The executor never wrote a summary.
  This summary was written by the coordinator from the codex.log
  and records.jsonl. No measurement was lost.
- Cleanup (coordinator): closed the Chromium window ("Example
  Domain - Chromium") and the pf2-method-term kitty via
  hl.dsp.window.close. Desktop verified clean (herdrdrop, Zen Pill
  fixture only).
