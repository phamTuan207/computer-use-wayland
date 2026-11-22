# C5-VISIBILITY: Chromium CDP Input stall, visibility hypothesis test

Worker: C5-VISIBILITY (independent of the S2 flip worker). Coordinator: COORD-CLICK-5.
Task: prove or kill the visibility hypothesis for the Chromium CDP Input stall.
Branch: todolist-push. Log started 10:42 Asia/Ho_Chi_Minh, 2026-11-22.

## 0. Starting point (verified facts, not re-derived)

- S2 flip verdict DO NOT EXPAND: median wall 33166.9ms over 5 runs, Brave 5/5
  verified, Chromium 0/5, 0 model calls, per-send 5/10, per-run 0/5. Chromium
  error runs 2-5: "CDP timeout: Input.dispatchMouseEvent".
  Full log: improvements/worker-click4-s2-flip-log.md. Run JSONs:
  improvements/s2-flip-runs/run-1..5.json.
- Isolated reproduction (flip worker, run 2, /tmp/s2-diag2.mjs on the live
  Chromium tab): Runtime.evaluate answers in 1-3ms, scrollIntoView is a no-op
  (rect top stays 1091), bare Input.dispatchMouseEvent mouseMoved TIMES OUT at
  5000ms. The Input domain specifically is stuck on that tab; the renderer
  answers Runtime.evaluate in 1ms.
- Leading explanation, NOT proven: Chromium sits on workspace 2 while workspace
  1 is active; the occluded window's input pipeline may not dispatch synthetic
  mouse events. The flip worker did NOT switch workspaces to test it.

## 1. Pre-state (10:42:45 +07)

Test command (SSH only via ~/workspace/ssh-laptop.sh):

```
~/workspace/ssh-laptop.sh 'export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-1 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus; SIG=$(ls /run/user/1000/hypr/ | head -n1); export HYPRLAND_INSTANCE_SIGNATURE=$SIG; date "+%H:%M:%S %Z %F"; hyprctl activeworkspace; hyprctl clients; pgrep -a chromium | head; pgrep -a zen | head; pgrep -a brave | head; ss -ltnp | grep -E "9222|9223"; ls -la /tmp/s2-diag2.mjs'
```

Output (abridged, full output in this worker's report to the coordinator):

- Active workspace: 1, lastwindow 0x55705383d420 (Brave, title Muse).
- Chromium window 0x5570538ed160, PID 8059, workspace 2, class
  chrome-hichoggbhebpgpgcbcgfpkjmohpcflhh-Default, title Muse, at 2514,914
  size 1853,1176, visible flag 1 (mapped, on inactive workspace).
- Zen window 0x557052b62dd0, PID 496121, workspace 1, port 9222.
- Brave window 0x55705383d420, PID 1003210, workspace 1, no debug flag.
- Ports: 127.0.0.1:9223 LISTEN (chromium PID 8059), 127.0.0.1:9222 LISTEN
  (zen-bin PID 496121). [::1]:9223 closed (Brave rolled back, as briefed).
- /tmp/s2-diag2.mjs still exists (2505 bytes, Nov 22 10:18), reused verbatim.
  It does Runtime.evaluate baseline, scrollIntoView of
  textarea[aria-label="Message"], 5 post Runtime.evaluate probes at 500ms
  intervals, then ONE bare Input.dispatchMouseEvent mouseMoved at (763,574)
  with a 5000ms timeout. No click, no typing, no text sent anywhere.
- Chromium /json/list shows exactly 1 page target:
  id D1374C7C994D3DA72678E20C7FD099A0, title "Chat - clone2",
  url https://muse.ai/?__pwa=1. (Other entries are Stripe iframes of that page.)
  This is the SAME tab the flip worker diagnosed. All runs below use it.

Pre-state matches the brief exactly. No browser restarted, nothing else touched.

## 2. Run A1, occluded, ws1 active (10:43:10-10:43:12)

```
node /tmp/s2-diag2.mjs http://127.0.0.1:9223 D1374C7C994D3DA72678E20C7FD099A0
```

Result:

```
{"baseline":{"ms":2,"value":2},"scroll":{"ms":1,"value":[1091,24]},"post":[{"ms":0},{"ms":1},{"ms":1},{"ms":0},{"ms":1}],"mouseMoved":{"ms":3,"ok":true}}
```

mouseMoved answered in 3ms while occluded. Stall NOT reproduced. scrollIntoView
still a no-op (rect top 1091, same as the flip worker saw).

## 3. Run A2, occluded, repeat (10:43:25-10:43:27)

Same command. Result: baseline 2ms, scroll [1091,24], post all 0-1ms,
mouseMoved {"ms":2,"ok":true}. Second occluded success in a row.

## 4. Switch to workspace 2 (10:43:34-10:43:36)

```
hyprctl dispatch "hl.dsp.focus({ workspace = 2 })"
```

Output: ok. Active workspace 2, lastwindow 0x5570538ed160 (Chromium, title Muse),
mapped 1, hidden 0, visible 1, acceptsInput 1. Chromium is now the visible,
focused window.

## 5. Run B1, visible, ws2 active (10:43:43-10:43:46)

Same diag command. Result: baseline 2ms, scroll [1091,24], post all 0-1ms,
mouseMoved {"ms":2,"ok":true}. Visible answers in 2ms, as expected, and no
different from the occluded A1/A2 (3ms, 2ms).

## 6. Switch back to workspace 1 (10:43:53-10:43:55)

```
hyprctl dispatch "hl.dsp.focus({ workspace = 1 })"
```

Output: ok. Active workspace 1, lastwindow 0x55705383d420 (Brave). Chromium back
on the inactive workspace 2.

## 7. Run A3, occluded again (10:44:01-10:44:09)

Same diag command. Result:

```
{"baseline":{"ms":2,"value":2},"scroll":{"ms":1,"value":[1091,24]},"post":[{"ms":0},{"ms":1},{"ms":0},{"ms":1},{"ms":0}],"mouseMoved":{"ok":false,"error":"Error: CDP timeout: Input.dispatchMouseEvent"}}
```

The stall REPRODUCED, 8 seconds after switching away from ws2. Runtime.evaluate
still 0-2ms throughout. Only Input.dispatchMouseEvent times out at 5000ms.

## 8. Runs A4-A6, occluded, stall persistence (10:44:30-10:44:59)

Three back-to-back runs, same command, 2s gaps:

- A4 10:44:30: baseline 6ms, post 0-1ms, mouseMoved TIMEOUT.
- A5 10:44:40: baseline 2ms, post 0-1ms, mouseMoved TIMEOUT.
- A6 10:44:49: baseline 2ms, post 0-6ms, mouseMoved TIMEOUT.

Once stalled, the stall STICKS: 4 consecutive timeouts (A3-A6) while occluded,
Runtime.evaluate never above 6ms.

## 9. Switch to workspace 2 again, runs B2-B4 visible (10:45:07-10:45:22)

```
hyprctl dispatch "hl.dsp.focus({ workspace = 2 })"
```

Output: ok. Active window 0x5570538ed160 (Chromium), visible 1. Three runs:

- B2 10:45:09: mouseMoved {"ms":2,"ok":true}.
- B3 10:45:13: mouseMoved {"ms":2,"ok":true}.
- B4 10:45:18: mouseMoved {"ms":2,"ok":true}.

Visibility UNSTUCK the tab immediately: 3/3 answers in 2ms right after 4
consecutive occluded timeouts. Runtime.evaluate 0-3ms throughout.

## 10. Switch back to workspace 1, runs A7-A8 occluded (10:45:32-10:45:53)

```
hyprctl dispatch "hl.dsp.focus({ workspace = 1 })"
```

Output: ok. Active workspace 1, lastwindow Brave. Two runs:

- A7 10:45:34 (2s after switching away): mouseMoved TIMEOUT.
- A8 10:45:43: mouseMoved TIMEOUT.

Re-occlusion re-stalls IMMEDIATELY in this cycle, unlike the first cycle
where A1/A2 answered while occluded.

## 11. Run A9, occluded after 240s steady occlusion (PENDING)

Note: the first attempt at this step used a single foreground SSH call with
`sleep 240` inside it; the SSH session broke at ~33s ("client_loop: send
disconnect: Broken pipe", 10:46:26), the documented ~30s SSH limit for long
sessions. No diag ran in that attempt. Relaunched correctly as a detached job:

```
setsid nohup bash -c 'date "+%H:%M:%S %Z %F"; sleep 240; date "+%H:%M:%S"; node /tmp/s2-diag2.mjs http://127.0.0.1:9223 D1374C7C994D3DA72678E20C7FD099A0; echo run-A9 EXIT=$?; date "+%H:%M:%S %Z %F"' > /tmp/c5-a9.log 2>&1 < /dev/null & disown
```

Launched 10:47:03. Diag due ~10:51:03. Purpose: test whether the stall clears
on its own after minutes of steady occlusion (A1/A2 suggest long-occluded can
answer; A7/A8 show freshly-occluded stalls). Result:

```
10:47:03 +07 2026-11-22
10:51:03
{"baseline":{"ms":2,"value":2},"scroll":{"ms":1,"value":[1091,24]},"post":[{"ms":1,"value":2},{"ms":1,"value":2},{"ms":1,"value":2},{"ms":1,"value":2},{"ms":1,"value":2}],"mouseMoved":{"ok":false,"error":"Error: CDP timeout: Input.dispatchMouseEvent"}}
run-A9 EXIT=0
10:51:11 +07 2026-11-22
```

Run A9 (10:51:03, occluded, 240s+ steady occlusion after A8): mouseMoved
TIMEOUT. The stall does NOT clear on its own after 4 minutes of steady
occlusion. The "time-since-focus-loss settles" refinement is also dead.
Stuck state persisted across 7 consecutive timeouts (A3-A9, 10:44:01 to
10:51:03) while Runtime.evaluate stayed 0-6ms the whole time.

## 12. Results table (all runs, same tab D1374C7C994D3DA72678E20C7FD099A0, same script)

| Run | Time (+07) | Workspace active | Chromium state | Runtime.evaluate | mouseMoved |
|-----|-----------|------------------|----------------|------------------|------------|
| A1 | 10:43:10 | 1 | occluded, long steady | 0-2ms | 3ms ok |
| A2 | 10:43:25 | 1 | occluded | 0-1ms | 2ms ok |
| B1 | 10:43:43 | 2 | visible, focused | 0-1ms | 2ms ok |
| A3 | 10:44:01 | 1 | occluded, 8s after switch away | 0-2ms | TIMEOUT 5000ms |
| A4 | 10:44:30 | 1 | occluded | 0-6ms | TIMEOUT |
| A5 | 10:44:40 | 1 | occluded | 0-2ms | TIMEOUT |
| A6 | 10:44:49 | 1 | occluded | 0-6ms | TIMEOUT |
| B2 | 10:45:09 | 2 | visible, focused | 0-2ms | 2ms ok |
| B3 | 10:45:13 | 2 | visible, focused | 0-1ms | 2ms ok |
| B4 | 10:45:18 | 2 | visible, focused | 0-1ms | 2ms ok |
| A7 | 10:45:34 | 1 | occluded, 2s after switch away | 0-1ms | TIMEOUT |
| A8 | 10:45:43 | 1 | occluded | 0-1ms | TIMEOUT |
| A9 | 10:51:03 | 1 | occluded, 240s+ steady | 1ms | TIMEOUT |

Totals: visible 4/4 ok (all 2ms). Occluded 2/9 ok (A1, A2), 7/9 timeout.

## 13. Post-state (10:51:44 +07)

Workspace 1 active, same 4 windows as pre-state, same PIDs: Chromium 8059 on
ws2, Zen 496121 on ws1, Brave 1003210 on ws1, herdrdrop 1645 on special.
Machine restored to pre-state. No browser restarted, no clicks, no typing, no
text sent into any chat. The tab is left in the stuck Input state (A9 timeout),
same as the flip runs left it; nothing else was changed.

## 14. VERDICT: VISIBILITY KILLED (as the cause)

The hypothesis as stated, that the occluded window's input pipeline may not
dispatch synthetic mouse events, is KILLED: the SAME tab, occluded on ws2
while ws1 was active, answered bare Input.dispatchMouseEvent mouseMoved in
3ms (A1) and 2ms (A2). Occlusion does not by itself block Input dispatch.

What the data DOES show, and what the coordinator should not lose:

1. The stall is real, intermittent, and STICKY. Onset fell between A2
   (10:43:27, ok) and A3 (10:44:01, timeout). Once on, 7 consecutive
   dispatches timed out (A3-A9, 10:44:01 to 10:51:03) while Runtime.evaluate
   stayed 0-6ms throughout. Only the Input domain is wedged; the renderer
   is fully alive. This matches the flip pattern (Chromium 0/5 runs after
   onset, per-send 5/10).
2. Visibility is a reliable RECOVERY, not the cause. Switching to ws2 unstuck
   the tab immediately: B2-B4 all answered in 2ms right after 4 consecutive
   occluded timeouts. 3/3, zero delay.
3. Re-occlusion re-stalls fast in the second cycle (A7/A8 timeout within
   seconds of switching away), but the first cycle answered fine while
   occluded (A1/A2). So the trigger is NOT steady occlusion. Leading
   candidate for the onset trigger, NOT proven: the workspace-switch /
   focus-loss transition itself (the only events between A2 ok and A3
   timeout were ws1->ws2, one visible diag, ws2->ws1). Alternative: a
   random or time-based onset that happened to fall in that window.
4. The stuck state does NOT self-clear with time: A9 still timed out after
   240s+ of steady occlusion.

Fix implication: a visibility precondition in the send path is NOT the fix.
Occluded sends CAN work (A1/A2), so gating every send on visibility would
not have prevented the flip failures and would add a workspace switch to
every send for no causal benefit. What visibility IS good for: a RETRY /
UNBLOCK step. When a send times out with "CDP timeout:
Input.dispatchMouseEvent", focusing the target window (workspace switch to
ws2, verified 3/3 instant recovery) unsticks the Input domain. The real fix
still needs the onset trigger, which is now the open question.

Suggested next levers (for the coordinator, not done here):
- L1: what wedges Input between A2 and A3: repeat A/B/A with a dispatch
  after EVERY single workspace switch, and try switching workspaces WITHOUT
  any diag in between, to isolate the switch as the trigger.
- L2: does Page.bringToFront (CDP-only, no workspace switch) unstick a
  stuck tab? If yes, the unblock needs no visible switch at all.
- L3: does a fresh CDP session, or Input.enable re-issue, unstick it? (Each
  diag run here already opened a fresh WebSocket session, and the stall
  persisted across sessions, so a fresh session alone does NOT unstick it.)
- L4: capture whether the stall correlates with a pending/unacked dispatch
  from the broker send path (mousePressed without release, or an Input
  dispatch issued while the tab was mid-switch).

