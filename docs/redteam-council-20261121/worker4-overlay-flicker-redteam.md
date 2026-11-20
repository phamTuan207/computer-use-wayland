# Worker 4 Redteam: overlay (pill) flicker at ~10x/sec

- Worker: Redteam Worker 4.
- Date: 2026-11-21. Start 03:32:51 +07, report written about 03:41 +07, elapsed about 8 minutes.
- Scope: H1, I9-I12 of `~/workspace/cf26-upload/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md`. Repo: `~/workspace/computer-use-wayland`.
- Rule compliance: no em dashes or en dashes in this file, only commas, periods, and short hyphens.

## 0. Bottom line

No code in the repo can produce a 10 Hz pill flicker during idle driving. That is the main finding, and it is a strong negative result, not a gap in the search. Every in-repo path that touches the pill was traced. The only visibility toggles are hide/show around screenshots (1 observe per 10-30 s, so 2 toggles per 10-30 s). Every in-repo timer near 100 ms is I/O polling that sends no pill traffic. The entrance animation (16 ms timer) is disabled in the final liquid mode that was running. Therefore the 10 Hz driver is either inside the compositor or the hyprglass plugin, or in a second pill instance, or in client behavior outside this repo (the Muse harness request pattern, which I cannot inspect from here). The most likely cause is a compositor/plugin level repaint loop, with the pill's own after-paint handler as an accomplice. Ranked verdicts and the experiments that would prove each one are in sections 5 and 6.

Two corrections to the record, already noted by the fix run, confirmed here. First, Part H (H1) says the flicker happened while Codex drove, but I9 says the opposite, Codex was normal and direct Muse driving flickered. I9 is the primary source (chat transcript 18:53-19:02 20/11) and H1 is wrong. Second, Muse's screenshot explanation (I20) is not just admitted wrong, it is provably wrong from the code, see section 2.

## 1. What was read and verified

### 1.1 The incident, from H1 and I9-I12

- I9 (18:53-19:02 20/11): pill "Computer use active" flickers continuously while Muse drives directly. User asks why Codex driving is normal but Muse driving flickers. Muse first blames screenshots, then retracts at 19:02, admitting screenshots at 1 per 10-30 s cannot cause 10x/sec flicker, and admits the true cause is unverified.
- I10 (18:56-18:58 20/11): user reports the flicker continues while Muse visibly does nothing, about 10 times per second. This is the most important constraint. During the flicker window Muse made no mouse moves and took no screenshots, so the cause must be active during an idle driver.
- I11 (19:13 20/11): user orders computer-use off because the flicker hurts his eyes. Muse turns it off.
- I12 (15:28 20/11): overlay vanished entirely while the worker was still alive and screenshotting. A second, distinct failure mode of the same pill, disappearance rather than flicker.
- True cause unverified as of 02:30 21/11.

### 1.2 The pill implementation, as read

- `native/indicator.c`: a GTK 4 + gtk-layer-shell process. One layer surface per monitor, layer OVERLAY, top anchored, exclusive zone -1. Surface 320x66, pill 288x38 at local (16,16). Click-through (empty input region). Owned by the session guardian (`scripts/cursor_session.py`), stdin EOF or parent death ends it. Dies (quits its main loop) on: presentation feedback discarded, frame ack timeout (2 s), monitor layout change, backdrop blur capability lost, rendering backend global removed, overlapping command, bad stdin line.
- `native/hyprglass-local-optics.lua`: hyprglass plugin config for namespace `computer-use-indicator`, mask_mode "contour", refraction_strength 0.55, blur_strength 0.0, chromatic_aberration 0.07. The contour mask traces the pill outline from the rendered content, because GTK 4.24 already requests the background effect itself and a second request is a protocol error that kills the client. That comment is in indicator.c, and it means the plugin's mask depends on the pill's own rendered pixels.
- `native/require-liquid` exists on the laptop, so final liquid mode was active on 20/11: `CU_INDICATOR_MATERIAL=liquid`, and the entrance animation is explicitly popped in that mode (`scripts/indicator.py` lines 34-40). No entrance animation was running during the flicker.
- `scripts/indicator.py`: the only pill commands are hide, show, and legacy move, served over a Unix socket by the guardian. `SessionVisuals.command` also forwards hide/show to the cursor guard, so each capture fence toggles both the pill and the software cursor together.
- `scripts/cu.py` lines 914 and 951: `capture_clean` (hide, grim, show) is used only by `observe` and `observe_screen`. No other caller exists in the repo.

### 1.3 The laptop install matches the code I read

Verified by SSH to the laptop (short read-only commands, 03:37-03:38 +07):

- No `native/indicator` process is running now. The only matching process is Omarchy's input-method indicator (`/usr/share/omarchy/default/input-methods/indicator.py`), a different program with a similar name. This is a grep trap for future investigators.
- md5 identical between laptop and VM for `native/indicator.c`, `native/hyprglass-local-optics.lua`, `scripts/indicator.py`, `scripts/cursor_session.py`, `scripts/session_remote.py`. Only `scripts/cu.py` differs (VM HEAD is newer).
- The pill-relevant mechanisms (capture_clean, after-paint presentation fence) come from commits d0f7dd6 and e25756f (2026-10-10), both ancestors of the laptop HEAD 56f5af4 (2026-11-19 21:50). So the code quoted in this report is the code that ran on 20/11 evening.
- Laptop indicator binary dated Nov 19 17:59, after the last indicator.c change (Nov 17 09:00), consistent with a matching build, though I did not verify the binary hash against a fresh build.
- A `journalctl --user` query for 18:50-19:05 on 20/11 grepping hyprglass, indicator, layer, present, discard, and background effect returned zero lines. Inconclusive: it may mean no errors were logged, or Hyprland logs elsewhere. I did not find where Hyprland logs on this machine.

### 1.4 Prior evidence: the pill already drops single frames

`improvements/live-test-log.md` (18/11 pill video test, Luna-driven scroll): the pill VANISHES for isolated single frames (frames 54, 1000, 1005) while the page is static across neighbouring frames, and Luna's verdict independently notes flicker/dropout frames 48-58. So intermittent presentation dropouts of the same pill existed two days earlier, under Codex/Luna driving, at a low rate. A 10 Hz visible flicker could be the same dropout mechanism firing much more often, not a new mechanism. This weakens any theory that the cause is exclusive to Muse driving.

### 1.5 Web grounding

A web search for Hyprland layer-shell flicker returns documented compositor-side layer-surface render quirks, not driver-side causes: Hyprland issue 875 (blur breaks layer surface fadeOut animation, surface flickers out on close), and Hyprland issue 15738 (gtk-layer-shell overlay surfaces not rendered for the first several invocation cycles, described as compositor-side, Hyprland 0.56.1). These do not prove our cause, but they establish that layer surfaces in Hyprland can fail to present intermittently for compositor-side reasons, which is the category my top hypothesis falls in.

## 2. Why screenshots cannot be the cause (code proof, not just rate arithmetic)

Muse's retraction in I20 rests on rate arithmetic (1 per 10-30 s vs 10 per s). The code makes it airtight:

- The pill has exactly two visibility transitions per observe (hide before grim, show after), gated by presentation-feedback acknowledgements (`redraw()` waits for `wp_presentation_feedback` presented events, 2 s timeout in C, 3 s in Python).
- No other code path sends hide or show. I grepped all of `scripts/*.py`, `skill/`, and `native/`. The `move` command only replies "ok" and never redraws, and nothing calls it.
- During I10 Muse was idle (no observes), so even the 2-toggles-per-observe path was silent. A cause that fires while the driver is idle cannot be the capture fence.

## 3. What could cause ~10x/sec flicker

### 3.1 The inventory of everything that touches the pill, and its rate

| Path | Trigger | Rate | Can it do 10 Hz idle? |
|---|---|---|---|
| hide/show via socket | observe/observe_screen only | 2 per 10-30 s | No |
| `enter_frame` 16 ms timer | entrance animation, first 1 s only, disabled in liquid mode | 60 Hz for 1 s | No, not running on 20/11 |
| `painted` after-paint handler | every GTK paint of the indicator window | paints only when something queues a draw | Only if something keeps painting, see H-A |
| `redraw()` ack timeout | presentation feedback missing for 2 s | one-shot, then process exits | No, it kills the pill |
| `discarded` feedback handler | compositor discards a presented buffer | one-shot, then process exits | No, it kills the pill |
| guardian loop `select(..., 0.05)` | 20 Hz poll, checks indicator liveness, serves socket | 20 Hz wakeups | No pill traffic unless a request arrives |
| broker `readline` select 0.1 | 10 Hz poll while awaiting a driver response | 10 Hz waits | Sends nothing to the pill |
| `activation_checks` sleep 0.1 | startup `wait_for_profile` only | 10 Hz for seconds at startup | No, startup only |
| mcp_bridge_transport POLL 0.04 | I/O polling | 25 Hz | Sends nothing to the pill |
| session_remote cleanup wait sleep 0.1 | during stop only | 10 Hz while stopping | No, stop only |
| cursor guard hide/show | bundled with pill hide/show | same as capture fence | No |

Note the trap: there ARE 10 Hz (0.1 s) and 20 Hz (0.05 s) and 25 Hz (0.04 s) timers in the repo, but all of them are local I/O waits. None of them emits a pill command. A careless reading could blame the 0.1 s select in `session_remote.py` line 397 or the 0.1 s sleep in `activation_checks.py` line 27. Both are innocent by construction: one waits for bytes that never arrive while idle, the other runs only at startup.

### 3.2 H-A. Compositor/plugin repaint loop, pill re-presented continuously (MOST LIKELY)

Mechanism: `painted()` in indicator.c is connected to the GTK frame clock `after-paint` signal, and on EVERY paint it calls `wl_surface_damage(full surface)` plus `wl_surface_commit` plus flush, even when no redraw is pending. In steady state GTK should go idle (no paints, no commits), but if anything keeps the frame clock ticking, every paint forces the compositor to re-render the layer surface, and re-rendering the liquid glass means re-sampling the backdrop and re-tracing the contour mask. The visible blink is then the glass alternating between two render states from frame to frame: for example, the contour mask traced from the previous frame's content flips between "pill outline found" and "no outline", toggling blur on and off, or the backdrop sample alternates between pre- and post-damage frames, or the manual double commit (GTK's own commit during paint, then the manual commit in `painted`) presents alternating buffers, one of them stale or transparent.

What keeps the frame clock ticking during an idle driver? Candidates, all outside the repo: an animation in the page behind the pill (loading spinner, GIF, progress bar, blinking caret), the browser tab strip repainting, the cursor sitting over the pill region, or a Hyprland damage bug that re-damages the layer on every frame. The pill sits at top-left (16,16), directly over Zen's tab strip, where a loading tab spinner animates during page loads. During 18:53-19:02 Muse was stuck on Polygon commit/save flows, pages loading and reloading, which fits.

Why Muse and not Codex, under this hypothesis: not the driver at all, but what was on screen at the time. Different page state, different backdrop animation, different cursor position. The 18/11 single-frame dropouts under Luna support this: same mechanism, lower rate, different backdrop.

Evidence for: 18/11 dropouts; known Hyprland layer-surface quirks; no in-repo 10 Hz driver found; flicker persists while the driver is idle (I10), which is exactly what a compositor-side loop predicts. Evidence against: none found, but the loop's trigger (what keeps GTK painting) is unidentified, which is why this is ranked first and not proven.

### 3.3 H-B. Two pill instances fighting (PLAUSIBLE, cheap to check)

Mechanism: two `native/indicator` processes, or two layer surfaces with namespace `computer-use-indicator`, drawn at the same place. The compositor alternates them, or the two processes alternately own the socket and hide/show each other. How could two exist? The 18:32 handover: Muse took over from Codex. If Codex's session was not cleanly finished first, or if a login warmup indicator from `visuals.py` was still alive, a second pill could linger. Counter-evidence: `owner_lock()` refuses a second session while one is active, the indicator dies on parent death (PR_SET_PDEATHSIG) and on stdin EOF, and the guardian tears the session down if the indicator dies. So a lingering second instance requires a guardian that died abnormally without its child dying, or a session started outside the guardian path. Not ruled out, and trivially checkable live.

### 3.4 H-C. Hide/show storm from a client retry loop (POSSIBLE, but the code argues against it)

Mechanism: some client calls observe (or another capture path) in a tight retry loop on failure, for example observation expired, window moved, or stale snapshot causing an immediate retry with no backoff, each iteration doing hide plus show. At 10 Hz this needs a roughly 100 ms retry cycle. Counter-evidence: no retry loop of that shape exists in the repo's `cu.py` or `session_driver.py`, and `redraw()` refuses overlapping commands by quitting the process, while the 2 s ack timeout would kill the indicator under a sustained storm rather than sustain 10 Hz. The storm would have to live in the client outside this repo (Muse's own harness or MCP bridge behavior while waiting), which I cannot inspect. If H-C were true, the session would likely have died quickly, yet the flicker ran for minutes (18:53-19:02, still going at 19:13 when the user ordered it off). That duration argues against H-C.

### 3.5 H-D. Indicator crash/restart oscillation via the broker (UNLIKELY)

Mechanism: the indicator dies (discarded feedback, ack timeout, monitor change), and the broker, described as "Reconnectable, single-owner", restarts the session, which spawns a fresh indicator, which dies again. Each cycle re-shows the pill, producing blinking. Counter-evidence: a restart cycle involves guardian startup, indicator spawn, GTK init, and liquid ready checks, plausibly 0.5-2 s per cycle, far slower than 10 Hz. Also the user would see other symptoms (cursor theme flipping, session errors, driver complaints). I12 (overlay gone while the worker lived) is better explained as the session having ended on indicator death while the worker kept issuing standalone observe commands, since `capture_clean` silently proceeds without hiding when no session exists. H-D is not the flicker, but I12 shows the indicator death path is real and worth hardening.

### 3.6 H-E. Animated backdrop behind the pill (TRIGGER for H-A, not a separate cause)

Mechanism: the page behind the pill animates at about 10 Hz (a spinner, a GIF, a progress bar), forcing the compositor to re-render the glass at that rate, and each re-render briefly shows the pill without glass or with a stale mask. This is the most concrete trigger candidate for H-A, and it neatly explains Muse vs Codex as different page states. Testable by freezing the backdrop (experiment E2). I list it separately because its experiment differs from H-A's.

### 3.7 H-F. Shader recompilation loop (UNLIKELY)

Mechanism: hyprglass recompiles its shaders on every frame because the shader cache fails or the "first overlay triggers shader compilation" path re-triggers. Counter-evidence: this would more likely freeze or stutter the whole compositor, not blink just the pill at 10 Hz, and the plugin reported ready (the pill rendered, just flickering). Checkable via CPU sampling during flicker.

### 3.8 H-G. Refresh-rate beat frequency (SPECULATIVE, lowest)

Mechanism: 10 Hz as a beat between two rates, for example a 60 Hz repaint against a 50 Hz present rate. No evidence for any 50 Hz element in this stack. Only testable by changing refresh rate or VRR, and only worth trying after H-A through H-F are excluded.

## 4. Why Muse and not Codex? The honest answer

I could not find any code difference in the driver path. Both clients drive through the same session, guardian, indicator, broker, and relay code, byte-identical on the laptop for every flicker-relevant file. The session contract in `skill/references/session.md` is client-agnostic. So the difference must be one of these, in order of likelihood:

1. What was on screen. Different page state, different backdrop animation behind the pill, different cursor position. Muse was stuck on Polygon commit and delete-dialog flows with pages loading; Codex had been on different pages. Under H-A/H-E this alone explains the difference.
2. Session overlap at the 18:32 handover. Whether Codex's session was cleanly finished before Muse started is not recorded in the files I read. Under H-B this explains it.
3. Client request pattern outside this repo. Muse's harness (VM, over SSH, via the broker) and Codex's client (on the laptop, via fcc-claude) may poll status, re-issue observes, or hold the session differently. I cannot verify this from the repo, and no in-repo path turns a client pattern into 10 Hz pill traffic.
4. Coincidence. The flicker mechanism is intermittent (18/11 dropouts under Luna prove it fires under Codex driving too, at a low rate), and it happened to manifest at high rate during Muse's window. The user's "Codex normal, Muse flickers" observation is real, but a rate difference is not proof of a driver difference.

## 5. Is the flicker a symptom of a deeper bug?

Yes, plausibly, and the pattern across three incidents points the same way: 18/11 single-frame dropouts, 20/11 15:28 total disappearance (I12), 20/11 18:53-19:13 continuous 10 Hz flicker (I9-I11). Three failure modes of one presentation path. The deeper bug candidates, all in or around `native/indicator.c`:

- The `painted` after-paint handler unconditionally damages the full surface and commits on every paint. This defeats damage tracking and forces a full liquid-glass re-render per paint. It should only commit when a redraw is actually pending.
- The presentation-feedback handshake is fail-deadly: a discarded feedback or a 2 s ack timeout quits the whole indicator process, which tears down the session. A transient compositor hiccup becomes a dead session. I12 is consistent with this having fired.
- The indicator logs nothing about its own redraw rate. There is no counter, no timestamped log of hide/show/painted/framed/discarded. A 10 Hz repaint loop is therefore invisible to every existing log, which is why the cause stayed unverified for a day. This observability gap is itself a bug worth fixing first, because it blocks every other diagnosis.
- The contour mask depends on the pill's own rendered pixels, a feedback loop by construction: rendered content determines the mask, the mask determines the next render. Any per-frame variation in the rendered content can oscillate the mask.

None of these is proven as the root cause. The flicker could still be entirely inside the closed-source hyprglass plugin (Hyprnux), which I cannot inspect. But the indicator side has three concrete fragilities that should be fixed regardless, after the cause is proven by experiment.

## 6. Experiments to find the true cause (ordered by value)

E1. Instrument the pill, then A/B the drivers. Add timestamped logging to indicator.c (or a socket tap): every stdin command, every `redraw()`, every `framed`, every `discarded`, every `painted`, every ack timeout, with monotonic timestamps. Run a 5 minute Muse drive and a 5 minute Codex drive on the SAME Polygon page, same cursor position. Decides: H-C if hide/show arrive at 10 Hz (storm proven), H-A if `painted` fires at 10 Hz with no commands (compositor-side repaint proven), H-B if two indicator PIDs appear. This is the single highest-value experiment and should be done first.

E2. Idle isolation. Start a session, then send no observes and no input for 60 s. Record the screen with wf-recorder at 60 fps, or grim in a loop, and count pill-present vs pill-absent frames. Repeat with (a) a static desktop and no browser window under the pill, (b) a loading or animating page under the pill, (c) cursor parked far from the pill vs resting on the pill. If flicker continues with zero driver traffic, the driver is exonerated and H-A is proven. If it follows the animated backdrop, H-E is proven. If it follows cursor position, the cursor or software-cursor path is implicated.

E3. Glass kill-switch. With the user's go-ahead, unload the hyprglass plugin (`hyprctl plugin unload`) or disable the layer glass while the indicator keeps running. If the flicker stops, the plugin is in the loop. If it continues with a plain (non-glass) pill, the cause is the indicator, GTK, or the compositor alone, and the plugin is exonerated.

E4. Duplicate-instance check during flicker. While it is flickering, run `pgrep -af 'native/indicator'`, `hyprctl -j layers`, and `hyprctl -j clients`. Two indicator PIDs, or two layer surfaces with namespace `computer-use-indicator`, proves H-B on the spot. Also reconstruct the 18:32 handover from the chat log: was Codex's session finished before Muse started?

E5. Measure the rate precisely and sample CPU. Film the flicker (wf-recorder at 60 fps) and count on/off transitions per second, rather than trusting "about 10". Simultaneously sample indicator CPU and Hyprland CPU (`pidstat` or `top -p`). An exact 10.0 Hz points to a 100 ms timer somewhere (H-C or a client poll). An irregular rate points to damage-driven repaints (H-A). High Hyprland or indicator CPU points to shader cost (H-F).

E6. Capture indicator stderr during a drive. Look for "indicator buffer was not presented" (discarded feedback) or "indicator frame acknowledgement timed out". Any occurrence proves the presentation handshake is failing under load, which supports H-A/H-D and justifies hardening the fail-deadly paths.

E7. A/B the driver properly. Same page, same time of day, Muse drives 5 minutes, then Codex drives 5 minutes, with E1 instrumentation and screen recording running throughout. If flicker follows the driver, it is client behavior. If it follows the page or cursor, it is H-A/H-E. This controls for the coincidence possibility in section 4 point 4.

E8. Patch test, only after diagnosis. Remove the unconditional damage plus commit from `painted` when no redraw is pending (commit only when pending), rebuild the indicator, re-run E2. If dropouts and flicker vanish, H-A is proven and fixed at the root. Do not ship this blind: without E1/E2 it would be guessing at the fix the same way the screenshot explanation guessed at the cause.

## 7. Verdict (ranked)

1. H-A, compositor/plugin repaint loop, with the pill's after-paint handler re-committing full-surface damage on every paint. Most likely. Explains idle flicker (I10), the 18/11 dropouts, and why no driver code runs at 10 Hz.
2. H-E, animated backdrop behind the pill as the trigger for H-A. Most likely trigger. Explains Muse vs Codex as different page states.
3. H-B, two pill instances from the 18:32 handover. Plausible, cheapest to check, would be decisive if true.
4. H-C, client retry storm. Possible in principle, but no such loop exists in the repo, and a storm should have killed the indicator quickly rather than running for 20 minutes.
5. H-D, crash/restart oscillation. Unlikely, cycle time too slow for 10 Hz.
6. H-F, shader recompilation loop. Unlikely, wrong symptom shape.
7. H-G, refresh-rate beat. Speculative, last resort.

The experiment that matters most is E1 plus E2 together: instrument the pill, then watch it while doing nothing. If the pill repaints at 10 Hz with zero driver traffic, the driver is innocent and the bug lives in indicator.c, GTK, Hyprland, or hyprglass. If hide/show commands arrive at 10 Hz, the client is guilty. Either outcome is decisive, and neither requires guessing.

## 8. What I could not verify (limits)

- The hyprglass plugin is closed-source (Hyprnux). Its internal render loop cannot be inspected from this repo. H-A's plugin half is therefore inference, not code proof.
- The Muse harness request pattern (what Muse's client sends to the broker while thinking) is outside this repo and was not observed. H-C's client half is unverifiable here.
- The journalctl probe for the flicker window returned no lines, which is inconclusive about Hyprland errors.
- The 18/11 dropouts were observed in a screen recording (wf-recorder), which could itself drop frames. The dropout evidence is therefore suggestive, not conclusive, about the live display.
- No live flicker was reproduced during this redteam. All rate claims rest on the user's "about 10 per second" estimate in I10, not a measurement. E5 exists to replace that estimate with a number.

## 9. Files and sources

- `~/workspace/cf26-upload/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md`, sections H1, I9-I12.
- `~/workspace/computer-use-wayland/native/indicator.c` (all of it, 400+ lines).
- `~/workspace/computer-use-wayland/native/hyprglass-local-optics.lua`.
- `~/workspace/computer-use-wayland/scripts/indicator.py`, `scripts/cursor_session.py`, `scripts/cu.py` (observe/observe_screen), `scripts/session_remote.py`, `scripts/session_driver.py`, `scripts/mcp_bridge.py`, `scripts/mcp_bridge_transport.py`, `scripts/activation_checks.py`, `scripts/step_watchdog.py`, `scripts/visuals.py`.
- `~/workspace/computer-use-wayland/skill/references/session.md`, `skill/references/usage.md`.
- `~/workspace/computer-use-wayland/improvements/live-test-log.md` (18/11 dropout frames 54, 1000, 1005; Luna verdict frames 48-58).
- `~/workspace/computer-use-wayland/docs/zen-error-fix-todolist-20261121.md` section 2.2.
- `~/workspace/computer-use-wayland/improvements/fix-run-20261121.md` (Phase 2 pending; H1 correction already recorded there).
- Web: Hyprland issue 875 (blurls break layerSurface fadeOut animation), Hyprland issue 15738 (gtk-layer-shell overlay not rendered on first cycles, compositor-side).
- Laptop SSH probes 03:37-03:38 +07: no indicator running now; md5 match on five flicker-relevant files; laptop HEAD 56f5af4 (2026-11-19 21:50) contains the capture_clean and after-paint commits (2026-10-10).
