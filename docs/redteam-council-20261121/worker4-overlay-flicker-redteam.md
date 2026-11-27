# Worker 4 Redteam: overlay (pill) flicker at ~10x/sec

- Worker: Redteam Worker 4.
- Date: 2026-11-21. Start 03:32:51 +07, report written about 03:41 +07, elapsed about 8 minutes.
- Scope: H1, I9-I12 of `~/workspace/cf26-upload/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md`. Repo: `~/workspace/computer-use-wayland`.
- Rule compliance: no em dashes or en dashes in this file, only commas, periods, and short hyphens.

## 0. Bottom line

The repo audit did not identify a normal 10 Hz pill command source. This is a static finding, not proof of the live cause. The capture path sends hide/show around an observation, so it can create visibility transitions during a capture. At the reported cadence of one observation per 10-30 seconds, that path alone does not account for a continuing 10 Hz flicker during the reported idle interval with no captures. The user report and cadence were not independently measured in this audit. Other client requests, GTK/frame activity, the compositor, the plugin, or multiple instances remain to be checked with runtime evidence. The after-paint behavior was a code-level candidate, not a verified cause. The experiments in sections 5 and 6 are proposed tests, not proof already obtained.

Two corrections to the record, already noted by the fix run, confirmed here. First, Part H (H1) says the flicker happened while Codex drove, but I9 says the opposite, Codex was normal and direct Muse driving flickered. I9 is the primary source and H1 is wrong. Second, the screenshot-volume explanation in I20 was retracted. The code cadence is consistent with that retraction for the reported idle interval, but it does not prove the live flicker cause or exclude an unobserved capture/request loop.

## 1. What was read and verified

### 1.1 The incident, from H1 and I9-I12

- I9 (18:53-19:02 20/11): pill "Computer use active" flickers continuously while Muse drives directly. User asks why Codex driving is normal but Muse driving flickers. Muse first blames screenshots, then retracts that explanation at 19:02 and acknowledges the true cause is unverified. The source report gives an observe cadence of 10-30 seconds, but this audit has no live request or frame trace.
- I10 (18:56-18:58 20/11): user reports the flicker continues while Muse visibly does nothing, about 10 times per second. This is the most important constraint. The source report says no mouse moves or screenshots occurred during the flicker window. If accurate, that makes ordinary capture activity insufficient to explain that interval; this was not independently measured here.
- I11 (19:13 20/11): user orders computer-use off because the flicker hurts the user's eyes. Muse turns it off.
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

## 2. What the capture cadence does and does not explain

The earlier claim blaming too many screenshots was unsupported and was retracted. Static code inspection provides a limited cadence check:

- The normal capture path hides before a clean screenshot and shows afterward. That can cause a transition around each capture. Nested captures are now coalesced into one outer hide/show pair.
- At the reported rate of one observe every 10-30 seconds, normal captures do not produce 10 transitions per second. The report also says no screenshot was taken during the idle flicker interval. Those are source-reported conditions, not measurements from this audit.
- This does not rule out an unobserved retry loop, another caller, or behavior outside this repo. The capture explanation is not supported as the cause of the reported continuous idle flicker, but the live cause remains unknown.


## 3. What could cause ~10x/sec flicker

### 3.1 The inventory of everything that touches the pill, and its rate

| Path | Trigger | Rate | Can it do 10 Hz idle? |
|---|---|---|---|
| hide/show via socket | capture fence, normally one per observe | 2 transitions per 10-30 s if report cadence holds | Does not explain reported 10 Hz idle flicker by itself |
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

### 3.2 H-A. Compositor/plugin repaint loop, pill re-presented continuously (UNVERIFIED CANDIDATE)

Hypothetical mechanism, not verified: if GTK continues painting, the old `painted()` handler could issue damage and commit work on each paint. Whether that makes the compositor re-render the liquid effect, and whether any resulting rendering difference is visible as flicker, has not been measured. Candidate render differences include contour-mask or backdrop changes, but there is no frame trace to support those examples.

What keeps the frame clock ticking during an idle driver? Candidates, all outside the repo: an animation in the page behind the pill (loading spinner, GIF, progress bar, blinking caret), the browser tab strip repainting, the cursor sitting over the pill region, or a Hyprland damage bug that re-damages the layer on every frame. The pill sits at top-left (16,16), directly over Zen's tab strip, where a loading tab spinner animates during page loads. During 18:53-19:02 Muse was stuck on Polygon commit/save flows, pages loading and reloading, which fits.

Why Muse and not Codex, under this hypothesis: not the driver at all, but what was on screen at the time. Different page state, different backdrop animation, different cursor position. The 18/11 single-frame dropouts under Luna support this: same mechanism, lower rate, different backdrop.

Consistency only: the source report describes idle flicker, and the earlier video report describes isolated dropouts. Neither shows that this mechanism caused them. No live frame or command trace supports H-A, and the trigger for continued GTK painting is unidentified. Lack of a disproving observation is not evidence for this hypothesis.

### 3.3 H-B. Two pill instances fighting (PLAUSIBLE, cheap to check)

Mechanism: two `native/indicator` processes, or two layer surfaces with namespace `computer-use-indicator`, drawn at the same place. The compositor alternates them, or the two processes alternately own the socket and hide/show each other. How could two exist? The 18:32 handover: Muse took over from Codex. If Codex's session was not cleanly finished first, or if a login warmup indicator from `visuals.py` was still alive, a second pill could linger. Counter-evidence: `owner_lock()` refuses a second session while one is active, the indicator dies on parent death (PR_SET_PDEATHSIG) and on stdin EOF, and the guardian tears the session down if the indicator dies. So a lingering second instance requires a guardian that died abnormally without its child dying, or a session started outside the guardian path. Not ruled out, and trivially checkable live.

### 3.4 H-C. Hide/show storm from a client retry loop (POSSIBLE, but the code argues against it)

Mechanism: some client calls observe (or another capture path) in a tight retry loop on failure, for example observation expired, window moved, or stale snapshot causing an immediate retry with no backoff, each iteration doing hide plus show. At 10 Hz this needs a roughly 100 ms retry cycle. Counter-evidence: no retry loop of that shape exists in the repo's `cu.py` or `session_driver.py`, and `redraw()` refuses overlapping commands by quitting the process, while the 2 s ack timeout would kill the indicator under a sustained storm rather than sustain 10 Hz. The storm would have to live in the client outside this repo (Muse's own harness or MCP bridge behavior while waiting), which I cannot inspect. If H-C were true, the session would likely have died quickly, yet the flicker ran for minutes (18:53-19:02, still going at 19:13 when the user ordered it off). That duration argues against H-C.

### 3.5 H-D. Indicator crash/restart oscillation via the broker (UNLIKELY)

Mechanism: the indicator dies (discarded feedback, ack timeout, monitor change), and the broker, described as "Reconnectable, single-owner", restarts the session, which spawns a fresh indicator, which dies again. Each cycle re-shows the pill, producing blinking. Counter-evidence: a restart cycle involves guardian startup, indicator spawn, GTK init, and liquid ready checks, plausibly 0.5-2 s per cycle, far slower than 10 Hz. Also the user would see other symptoms (cursor theme flipping, session errors, driver complaints). I12 (overlay gone while the worker lived) is better explained as the session having ended on indicator death while the worker kept issuing standalone observe commands, since `capture_clean` silently proceeds without hiding when no session exists. H-D is not the flicker, but I12 shows the indicator death path is real and worth hardening.

### 3.6 H-E. Animated backdrop behind the pill (UNVERIFIED CANDIDATE)

Hypothesis only: an animation behind the pill could coincide with repaint activity. No backdrop frames or matched static-versus-animated comparison were captured, so this does not yet explain the reported flicker or client difference. Experiment E2 could test for a relationship.

### 3.7 H-F. Shader recompilation loop (UNLIKELY)

Mechanism: hyprglass recompiles its shaders on every frame because the shader cache fails or the "first overlay triggers shader compilation" path re-triggers. Counter-evidence: this would more likely freeze or stutter the whole compositor, not blink just the pill at 10 Hz, and the plugin reported ready (the pill rendered, just flickering). Checkable via CPU sampling during flicker.

### 3.8 H-G. Refresh-rate beat frequency (SPECULATIVE, lowest)

Mechanism: 10 Hz as a beat between two rates, for example a 60 Hz repaint against a 50 Hz present rate. No evidence for any 50 Hz element in this stack. Only testable by changing refresh rate or VRR, and only worth trying after H-A through H-F are excluded.

## 4. Why Muse and not Codex? The honest answer

I could not find any code difference in the driver path. Both clients drive through the same session, guardian, indicator, broker, and relay code, byte-identical on the laptop for every flicker-relevant file. The session contract in `skill/references/session.md` is client-agnostic. Possible explanations include:

1. What was on screen. Different page state, different backdrop animation behind the pill, different cursor position. This could interact with H-A/H-E, but no matching-screen comparison was made.
2. Session overlap at the 18:32 handover. Whether Codex's session was cleanly finished before Muse started is not recorded in the files I read. This is one possible explanation under H-B, not an established cause.
3. Client request pattern outside this repo. Different clients may poll status, re-issue observes, or hold the session differently. I cannot verify this from the repo, and no runtime command trace was collected.
4. Coincidence. The 18/11 source report of isolated dropouts is suggestive but not a controlled comparison. The reported difference between clients does not by itself prove a driver difference.

## 5. Is the flicker a symptom of a deeper bug?

Possibly. The three reports are consistent with presentation-path failures but do not prove one shared cause. The code-level candidates in or around `native/indicator.c` included:

- At report time, `painted` unconditionally damaged and committed on every paint. Phase 2.2.3 has since made commits conditional on a pending presentation; no live comparison verifies whether this affected flicker.
- The presentation-feedback handshake is fail-deadly: a discarded feedback or a 2 s ack timeout quits the whole indicator process, which tears down the session. A transient compositor hiccup becomes a dead session. I12 is consistent with this having fired.
- At report time, the indicator had no redraw-rate counters. Phase 2.2.2 has since added timestamped paint, commit, visibility, and capture counters. They have not been collected during a live flicker reproduction, so the rate and cause remain unknown.
- The contour mask uses the pill's rendered pixels. This is a possible feedback path, but there is no evidence it oscillated during the reported incident.

None of these is proven as the root cause. The after-paint commit change is in place, but its effect is unverified. The plugin internals and the live presentation path still need measurement.

## 6. Experiments to find the true cause (ordered by value)

E1. Collect the timestamped counters added in Phase 2.2.2, together with presentation acknowledgements and visible-frame measurements. A high hide/show rate would support a command-path investigation; repeated paints without commands would narrow attention to the render path; multiple indicator PIDs would establish duplication. None alone proves the visible flicker cause. Compare clients only with the same page and conditions.

E2. During a no-input interval, measure visible pill frames without using capture activity as the assumed cause. Compare a static backdrop, an animated backdrop, and cursor positions under otherwise matched conditions. Flicker without driver traffic would make the capture path insufficient as the sole explanation, but would not prove H-A. A correlation with backdrop or cursor changes would support further tests, not establish causation.

E3. Glass comparison. In a later authorized live test, compare the same indicator with glass enabled and disabled. A change in measured flicker would support plugin involvement, but repeated matched runs are needed to rule out timing or backdrop differences.

E4. During a measured flicker, inspect indicator PIDs and layer namespaces. Multiple instances would establish duplication, but a controlled stop of one instance is still needed to show whether duplication causes the visible effect.

E5. Measure visible on/off transitions and sample indicator/Hyprland CPU. A stable 10 Hz rate is consistent with a periodic source but does not identify one. Irregular timing or high CPU may guide follow-up tests but does not prove repaint or shader causation.

E6. Capture indicator stderr during a measured flicker. A discarded-frame or acknowledgement-timeout message proves that presentation failure occurred, but does not by itself show that it caused the visible flicker.

E7. Compare clients with matched page, cursor, and capture cadence while collecting the same counters and visible-frame measurements. A difference would motivate tracing the client path; it would not alone establish why that path differs.

E8. The conditional after-paint commit change is already implemented and built. Its effect on flicker still needs a matched live before/after measurement; code change and offline build alone do not prove a fix.

## 7. Hypotheses (not findings)

The available evidence does not justify ranking a root cause. H-A through H-G are candidates only. The static audit and source report do not distinguish among GTK/frame activity, compositor/plugin behavior, multiple instances, or external client requests.

The highest-value next evidence is E1 plus E2: record indicator command and frame counters while measuring the visible flicker during a no-input interval. A high hide/show rate would locate traffic at the indicator boundary and require tracing its caller. Paint activity without commands would narrow the search to the render/presentation path, but would not by itself identify whether GTK, Hyprland, or the plugin is responsible.


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
