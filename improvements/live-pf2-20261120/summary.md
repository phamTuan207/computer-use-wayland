# Task 4: H6 page prefetch discriminating test

Verdict: BLOCKED-by-mechanism. The page prefetch never ran, so no
prefetch benefit could be measured. The open load_ms comparison is
fresh-load vs fresh-load, not a prefetch benefit.

Branch: harness-prefetch 56f5af4 (suite gate CITED, HEAD matches the
triple A/B gate, 1355 tests, 7F/0E/2S).
Relay env: CU_PRECAPTURE=0 in both arms (desktop pre-capture OFF;
only the page prefetch differs).
Task: B1, open https://example.com in managed Chromium, report the
heading "Example Domain".

## Baseline arm (56f5af4, CU_PRECAPTURE=0, no prefetch call): SUCCESS
- Open: prefetched false, load_ms 232.996, tab
  856E9ED5075BE774B7380BFB88F4F851 (fresh tab, full navigation cost).
- DOM observe: title "Example Domain", url https://example.com/,
  snapshot 30048a0b-970. Heading verified.
- Time-to-first-interaction (open submit 01:51:40.142 to first
  successful browser observe 01:51:58.835): 18.693s. Dominated by
  the executor's think gap, not the 232.996ms load.
- Task wall (session start submit 01:51:22.808 to DOM observe result
  01:51:58.835): 36.027s.
- Desktop observe (Chromium window): prefetched False, capture_ms
  41.256 (live capture, CU_PRECAPTURE=0).
- Requests: browser 2, observe 1, windows 1, start 1, finish 1;
  status polls 3; service total 1.130s; image bytes 101,776.
  Analyze.py span 353.560s, gap share 99.6 percent (includes a 236s
  finish deliberation: the executor deliberated about 4 min after
  the desktop observe before sending finish at 01:57:16; the
  coordinator killed the codex at about 01:57:22 while it composed
  the summary, after the finish; no measurement lost).
- Baseline summary: live-pf2-20261120/baseline-summary.md (also on
  the laptop at /tmp/live-pf2-20261120/pf2-baseline/summary.md).

## Method arm (56f5af4, CU_PRECAPTURE=0, prefetch call): PREFETCH FAILED
- Prefetch call result:
  `{"ok": false, "command": "prefetch", "error": "prefetch requires an active computer-use task"}`
- Open result:
  `{"ok": true, "command": "open", "endpoint": "http://127.0.0.1:9222", "tab": {"id": "CF3379C90E6F160AC8C0D03449A71922", "title": "Example Domain", "url": "https://example.com/"}, "prefetched": false, "load_ms": 175.874}`
- The open fell back to a fresh tab load (prefetched false,
  load_ms 175.874). The 57ms difference from the baseline's
  232.996ms is run-to-run noise (and the page may have been
  cached), NOT a prefetch benefit: no prefetched tab existed to
  adopt.
- DOM observe: title "Example Domain", url https://example.com/,
  snapshot ddff8e26-26a. Heading verified.
- Task wall (session start submit 02:02:32.039 to DOM observe result
  02:03:43.091): 71.052s. The open submit epoch was not recorded by
  the executor, so the exact open-to-observe interval is not
  available; the open itself took 175.874ms.
- Desktop observe (Chromium window): prefetched False, capture_ms
  59.872. Same range as the baseline's 41.256ms, as expected (only
  the page prefetch differs, not the desktop pre-capture).
- Requests: browser 7, observe 1, windows 1, start 2, status 1;
  status polls 6; service total 1.638s; image bytes 147,677.
  Analyze.py span 344.312s, gap share 99.4 percent.
- Method summary: live-pf2-20261120/method-summary.md (also on the
  laptop at /tmp/live-pf2-20261120/pf2-method/summary.md).

## Root cause of the prefetch failure (machine-checked)
- The chromium_cli prefetch wrapper reads the session token from
  `~/.local/share/agent-computer-use/session.json` (or the
  CU_SESSION_TOKEN env). That file does NOT exist on the laptop:
  the executor got a FileNotFoundError reading it, and a find over
  `~/.local/share/agent-computer-use` and
  `~/.cache/agent-computer-use` finds no session.json anywhere.
- The broker (scripts/session_remote.py) defines
  SNAPSHOT = STATE / 'session.json' (STATE is
  ~/.cache/agent-computer-use) and only READS it (lines 549, 634,
  695, 897, 933). Nothing in the current broker path WRITES it.
  So the token file never exists, and the prefetch wrapper cannot
  associate a prefetch with the active task.
- The baseline arm hit the same missing file (its broker open
  succeeded anyway, because the broker handles its own token). The
  method arm's prefetch path depends on the file and has no
  fallback.
- The prefetch was attempted in the required single shell burst
  (prefetch, sleep 3, open), so TTL expiry (30s) is not the cause.
- Corroboration: ~/.local/share/agent-computer-use/chromium-cli-state.json
  records only the opened tab (CF3379..., "Example Domain",
  updated_unix 1795114997). No prefetched tab was ever registered.
- The fix must be harness-side (the broker writes session.json
  with the token on session start, or chromium_cli gets the token
  another way). This is the same class of gap as Task 2's
  change-only delivery gap. Do not re-run the method arm until that
  lands.

## Session failures in the method arm (executor-side, NOT prefetch)
- Two driver_command_failed session failures, both caused by the
  executor's extra H1 check (a verification step it added beyond
  the brief, using a snapshot/selector on the page). Neither is
  related to the prefetch mechanism.
- H1 check 1 (02:06:36): "Uncaught: Error: stale snapshot" (the
  snapshot from the DOM observe was stale by the time the check
  ran, 117.6s of deliberation later). Session failed.
- The executor restarted (b1-restart1, generation
  4781a4144d6f94848a662f6a729f5595, start 02:07:46), re-verified
  the heading (restart1 observe 02:08:05, title "Example Domain",
  snapshot 525fa6e5-358), then ran the H1 check again.
- H1 check 2: "Uncaught: Error: selector must match exactly one
  element". Session failed again.
- The coordinator killed the method codex (PID 1108435) at about
  02:09:15 to stop a third restart loop. The executor never wrote
  a summary; the method summary was written by the coordinator
  from the codex.log and records.jsonl. No measurement was lost.

## Wall verdict
- No wall verdict can be drawn. The wall in both arms is dominated
  by think gaps (gap share 99.4-99.6 percent, service 0.3-0.5
  percent). The load_ms difference (175.874 vs 232.996) is 57ms on
  a 36-71s task, far below the run-to-run think variance (the
  method arm's own H1 deliberation alone was 117.6s). As the brief
  framed it, the wall effect of a page prefetch is expected to be
  below noise (like the H6 desktop prefetch, where capture is
  about 50ms of a 50s task); the mechanism is what was to be
  judged, and the mechanism could not run.
- Do not claim a wall WIN from the 57ms load_ms drop. The two
  opens were both fresh loads.

## Other notes
- The desktop observe OCR was noisy in both arms (French text and
  garbled characters in the transcript). Verification relied on the
  DOM observe (title/url), not the desktop OCR.
- The brief's session.json path is the one that does not exist;
  the broker's own STATE path (~/.cache/agent-computer-use) also
  has no session.json. The file is missing from both locations.
- Cleanup (coordinator, both arms): closed the Chromium window
  and the executor terminal kitty via hl.dsp.window.close after
  each session. Desktop verified clean (herdrdrop, Zen Pill
  fixture only).

## Files
- live-pf2-20261120/summary.md (this file)
- live-pf2-20261120/baseline-summary.md, live-pf2-20261120/method-summary.md
- live-pf2-20261120/brief-pf2-baseline.md, live-pf2-20261120/brief-pf2-method.md
- Laptop run dirs: /tmp/live-pf2-20261120/pf2-baseline/ and
  /tmp/live-pf2-20261120/pf2-method/ (records.jsonl, decisions.log,
  analyze.py output, summary.md, codex.log).
