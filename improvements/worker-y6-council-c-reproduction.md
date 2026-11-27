# Council C (reproduction design): position paper on Worker Y6 Wayland-nested reproduction

- Date: 2026-11-21, 18:45 to 19:05 +07
- Council member: C (reproduction design). Worker: Y6 (Muse subagent). Branch: todolist-push.
- Sources read in full: improvements/worker-y6-hyprglass-nested-probe.md (Y6 draft), docs/decision-2-2-3-hyprglass-test-20261121.md (Worker X decision doc), improvements/worker-y6-council-a-feasibility.md (Council A), docs/pending-user-decisions.md section 2, docs/redteam-council-20261121/worker4-overlay-flicker-redteam.md (the 20/11 incident record, H-E), scripts/indicator.py (liquid_available, LIQUID_READY_TIMEOUT), scripts/setup.py (optics hook, _hook_body), tests/realistic/run_agyq2.py preflight (flock check).
- Read-only verification via ssh-laptop.sh, no launch, no write, live session untouched. Details in the evidence section at the end.
- Owner order in force: best quality, not speed.

## Verdict: APPROVE-WITH-CHANGES

The design is runnable in shape and asks the right question, but it is NOT runnable as written and NOT decisive as written. Approve the Wayland-nested run only after all seven changes below are applied to the design. None of the seven needs the owner. If any one is skipped, the run risks failing loudly at launch (changes 1 and 2) or, worse, succeeding vacuously and reporting a false negative (changes 3 and 4).

### Exact changes required before the run

1. Fix the parent connection env in run-nested-wayland.sh. Set WAYLAND_DISPLAY to the absolute socket path /run/user/1000/wayland-1 (verified to exist, single live socket), and keep XDG_RUNTIME_DIR=/tmp/y6-nested/run for the nested server only. As written the script pairs XDG_RUNTIME_DIR=/tmp/y6-nested/run with WAYLAND_DISPLAY=wayland-1, which makes the Wayland backend look for /tmp/y6-nested/run/wayland-1, a socket that does not exist. This repeats the exact mistake Council A diagnosed in attempt 3. Pre-launch check: test -S /run/user/1000/wayland-1. Post-launch check: the nested log must show the Wayland backend started, not only that a window appeared.
2. Create the missing files before the window. /tmp/y6-nested/run-nested-wayland.sh and /tmp/y6-nested/conf/hyprland-wayland.conf do not exist on the laptop. Only run-nested.sh (headless version, sets WAYLAND_DISPLAY=wayland-y6 plus WLR_BACKENDS/AQ_BACKENDS=headless) and conf/hyprland.conf (monitor=HEADLESS-1, exec-once foot --title y6-nested-probe) exist. Write the Wayland versions, then clean /tmp/y6-nested/run/hypr/ of its 5 stale signature dirs from the crashed attempts, so the nested HYPRLAND_INSTANCE_SIGNATURE lookup is unambiguous.
3. Name the animated backdrop and add a positive control. The design says "LIQUID animated backdrop" but never says what moves. Inside the nest the only client is foot, which is static. A static backdrop makes 32/32 identical frames the expected outcome even if the bug is real. Required: name the animation source (one concrete moving client behind the pill), verify it moves before the pill starts (grim diff of the backdrop region without the pill must show pixel change), and run the E2 two-arm comparison from the redteam doc: static backdrop arm, then animated backdrop arm, matched conditions. Without the animated arm the design tests the control, not the incident.
4. Name the measurement exactly. Step 5 says "count paint callbacks/commits (the live measurement method)" but gives no command, log path, or counter field for the nest, and no diff tool, pixel region, or threshold for the 32 frames. Required: write down the exact E1 counter source (log path and fields) or the exact grim frame-diff procedure (region, tool, threshold) before the run. The 32 frames at 1 s apart is a sound frame arm; the callback arm currently has no executable form. I searched scripts/indicator.py for a paint or callback counter and found none by those names, so the counter source is UNVERIFIED until the design names it.
5. Replace `source=optics.lua` with the known-working mechanism. The live setup applies the optics profile through the setup.py Lua hook: a managed block that runs dofile(profile) when exactly one hyprglass of version 1.1.1-cu.1 is loaded. The design instead adds `source=/tmp/y6-nested/conf/optics.lua` to the nested config. Hyprland `source` loads Hyprland-syntax config files, and whether 0.57.2 executes a .lua file through `source` is UNVERIFIED. No evidence in the repo supports the `source=` form, and the repo's only proven path is the dofile hook. Apply the hook to the nested config verbatim (or prove `source=` executes Lua first). Apply it by restarting the nest with the hook included. Drop the "reload the nested compositor" branch: reload behavior for a newly added plugin line in the nest is UNVERIFIED, and restart is the safe branch the design already lists.
6. Close the check-then-launch race. Precondition checks are a snapshot. Nothing in the design holds the quiet window between the check and the launch, so a runner can start in between. Required: hold zen_dom.lock (flock) for the whole nested run, or have Muse sequence the nested run as a job in the runner queue, so the one-runner-at-a-time rule covers it. Give the exact flock check command: the /proc/locks inode method from the run_agyq2.py preflight, not a bare "check the flock is free". Extend the 30 minute window to cover launch through teardown; the design gives no duration estimate for the full run.
7. Add teardown and sharpen GO/NO-GO (see section 3). The design has no teardown step. Required: kill the nested Hyprland, remove its runtime dir, then re-verify the live session (PID 1515 alive, hyprctl responsive), the same verification Y6 did at 18:23.

## 1. Preconditions: checkable, but not sufficient as written

| Precondition | Checkable? | Sufficient? | Finding |
|---|---|---|---|
| No Zen runner active: flock on zen_dom.lock free, no run_agyq2/run_live/E1 process, Muse confirms none scheduled in next 30 min | Partly. The flock check is checkable via the /proc/locks inode method in run_agyq2.py preflight, but the design gives no command. The process check is checkable via ps (verified just now: no run_agyq2, run_live, or E1 process running; Zen itself, PID 27958, is the owner's browser, not a runner). The "Muse confirms" leg is not a check at all: no schedule artifact is named, and the live queue (Y4d rerun, Y8 E1, Y9 agy-y2, one runner at a time) lives only with Muse. | No. Snapshot only, see change 6. Also 30 minutes is ungrounded: no duration estimate for launch plus plugin plus optics plus 32 frames plus teardown. | Require change 6 and a duration estimate. |
| Owner away (handover 18:24 still in force) | Yes as a standing fact, and the 18:30 note says the owner is busy and unavailable and the work runs fully automatic. | Yes, with a note: the nested window appears on the live screen, so if the owner returns mid-run it is visible but harmless. The "do not click it" instruction is correct and sufficient. | Keep. |
| seatd NOT required (Wayland backend needs no seat) | Yes. A Wayland client needs no seat. | Yes for the Wayland path. | Keep. This is the Wayland path's main structural advantage over headless, and it is correctly stated. |

One more precondition gap: the design never checks that the nested config and launcher script exist (change 2) or that the parent socket exists (change 1) before dispatching. Both checks are one line each and belong in the preconditions, not discovered at launch time.

## 2. Does the design reproduce the 20/11 incident? Not as written

What the incident was, from the redteam record: on 20/11, 18:53 to 19:02, the pill flickered continuously at about 10 times per second while idle, while Muse drove directly, with no mouse moves and no screenshots during the interval (I9, I10). The user ordered computer-use off at 19:13 because the flicker hurt the user's eyes (I11). The animated backdrop is hypothesis H-E, and the redteam doc states it explicitly as an UNVERIFIED CANDIDATE: "an animation behind the pill could coincide with repaint activity. No backdrop frames or matched static-versus-animated comparison were captured." The proposed test, E2, is a static-versus-animated comparison under matched conditions. Nobody recorded what was actually behind the pill on 20/11, so the animation source is unknown, not merely unspecified in the design.

Against that bar, the design as written tests something else:

- The backdrop is never named. Inside the nest the only client is foot, a static terminal. "Capture the foot window over the backdrop" describes a static scene. A run of this design can return 32/32 identical frames and 0 callbacks while the real incident cause is untouched, because no moving backdrop was ever presented.
- The pill setup is right: indicator.py against the nested env, namespace computer-use-indicator, LIQUID mode. That part faithfully mirrors the live session.
- The frame count is right: 32 grim frames 1 s apart matches the live measurement (32/32 identical frames in the live indicator proof). The frame arm is sound once the backdrop moves.
- The callback arm is not executable as written (change 4). The live numbers it cites (122 one-second windows with 0 callbacks, 3 minutes with 0 commits) are real measurements, but the design does not say how to obtain the equivalent numbers inside the nest.

Fix: change 3 (named animation source, positive control, E2 two-arm comparison) plus change 4 (exact measurement). With those, the design does reproduce the incident's testable core: an idle LIQUID pill over a moving backdrop, with frame diffs and paint counts as the readout. Without those, a negative result means nothing and a positive result would be uninterpretable, because the backdrop state was never established.

## 3. GO/NO-GO: mostly sharp, with three soft edges

What is sharp, and I endorse it:

- Version is not 1.1.1-cu.1 is NO-GO. This matches indicator.py's own gate: _valid_liquid requires version exactly 1.1.1-cu.1 and versionCheck exactly 'match', plus schema 1, active true, layers enabled and active with reason null, windows and subsurfaces disabled. The design's GO paraphrase ("version 1.1.1-cu.1 and layers.active=true") is looser than the code. Apply liquid_available(ready=True) semantics exactly instead of the paraphrase.
- The 30 second shader wait is grounded: LIQUID_READY_TIMEOUT is 30.0 in indicator.py, and the live first-use compile took about 8 s. Keep 30 s as the first bound.

Three soft edges, fixed by change 7 and the branches below:

- Version mismatch branch is missing. NO-GO must also say what happens next: record the observed version and return to council. Do not silently substitute the backup 2 .so (different build, sha256 ddfff1c2, not used) or proceed with a mismatched profile. A newer version such as 1.1.1-cu.2 might be benign, but that is a council decision, not a runner improvisation.
- Shaders pending versus failed is not distinguished. If shaders is still 'pending' at 30 s, allow one further 30 s extension: nested shader compile under the Wayland backend may run slower than the live 8 s, and 'pending' means still compiling, not failed. If shaders reports error or failed, or is still pending after the extension, that is NO-GO. The shader state vocabulary beyond 'ready' and 'pending' is UNVERIFIED, so the design must record the exact string observed.
- The nested window itself changes the rendering, and the design does not say so. The nest renders at 960x540 at 60 Hz through the Wayland backend and the parent compositor's presentation timing, possibly with software GL, versus the live session's direct output. Consequence, and this must be written into the verdict clause: a POSITIVE result (frames differ in the backdrop region while the pill is idle, or paint callbacks fire repeatedly with no input) is decisive, it reproduces the incident. A NEGATIVE result (32/32 identical, 0 callbacks) is only "not reproduced in the nest". It does NOT exonerate the live backdrop, because the flicker may depend on live timing the nest does not replicate. The design as written states the negative as "NOT reproduced" without that qualification, which overclaims.
- Missing branches: plugin loads but `hyprctl hyprglass status` errors or returns non-JSON is NO-GO; nested window appears but hyprctl inside the nest never responds is NO-GO with cleanup; nested crash is NO-GO, and the crash must be attributed correctly (live PID 1515 check first, then the nested crash report), the same attribution Y6 did at 18:23.

## 4. Single weakest step and its fix

Weakest step: the parent-connection environment pair in run-nested-wayland.sh, XDG_RUNTIME_DIR=/tmp/y6-nested/run plus WAYLAND_DISPLAY=wayland-1.

Why it is the weakest: it decides whether anything runs at all, and as written it is deterministically wrong. libwayland resolves a relative WAYLAND_DISPLAY against XDG_RUNTIME_DIR, so the nested Wayland backend would look for /tmp/y6-nested/run/wayland-1, which does not exist, and fail with wl_display_connect failed, exactly like all five headless attempts. It repeats the precise error Council A diagnosed in attempt 3, inside the very design written to avoid it. Every later step (plugin load, optics, 32 frames) depends on this one pair, and no later check can rescue it.

Fix (change 1): in run-nested-wayland.sh, set WAYLAND_DISPLAY=/run/user/1000/wayland-1, the absolute socket path, verified present on the laptop, while keeping XDG_RUNTIME_DIR=/tmp/y6-nested/run for the nested server's own socket. Add the pre-launch check test -S /run/user/1000/wayland-1 and the post-launch check that the nested log shows the Wayland backend started. The in-nest client env (XDG_RUNTIME_DIR=/tmp/y6-nested/run, WAYLAND_DISPLAY=wayland-y6) is already a consistent pair and needs no change.

Note on the runner-up: the unnamed animated backdrop (change 3) is the most dangerous validity gap, because a run can succeed end to end and still test the wrong thing. I rank the env pair first only because it fails before any evidence exists at all, and its failure mode is identical to the five crashes already logged.

## 5. Headless versus Wayland if seatd-launch works

Call: Wayland-nested first, even if seatd-launch works. Do not reorder on the strength of a seatd fix alone.

Reasons:

- Wayland-nested is the highest probability path (Council A Path C, agreed) and the only one whose allocator source is already known to exist: the parent supplies a DRM fd via dmabuf. Headless via seatd-launch still carries two UNVERIFIED unknowns from Council A: seatd versus logind coexistence on one VT, and Aquamarine DRM backend acceptance of a render-only node (AQ_DRM_DEVICES plus AQ_NO_KMS_REQUIREMENT). A seat fix answers only the first wall.
- Fidelity decides this question, not scheduling. The incident is a timing-sensitive flicker at about 10 Hz. Wayland-nested keeps a real presentation path through the live compositor. Headless on a render node or vkms, with likely software GL and no KMS page-flip timing, is further from the live rendering path, so a headless negative would be weaker evidence than a Wayland negative (see section 3 asymmetry). The owner ordered best quality, not speed, and the Wayland path's cost (one quiet window, one brief focus steal) is already handled by the preconditions.
- Headless's advantage is scheduling: no window on the live screen, no focus steal, no runner-quiet requirement. That advantage matters for speed and convenience. It does not matter for correctness, and it does not outweigh the two unknowns plus weaker timing fidelity.

What changes in the design if seatd-launch works and headless runs instead:

- Preconditions 1 and 2 (no runner active, owner away) drop to a seatd-lifecycle rule only, and only after coexistence is proven benign. Until then, still run in a runner-quiet window, because a seatd versus logind fight could disturb the live session. Kill seatd immediately after the attempt and re-verify live PID 1515 and hyprctl, as Council A specifies.
- Config: monitor becomes HEADLESS-1, and AQ_DRM_DEVICES points at a render node (/dev/dri/renderD128 or renderD129, both verified world accessible) with AQ_NO_KMS_REQUIREMENT=1, or at a vkms card if Path B is used. The plugin line, optics hook (change 5, dofile form), indicator launch, 32 frames, and callback counting are unchanged.
- grim changes back to the form the design already notes: grim -o HEADLESS-1 against the nested display.
- The verdict asymmetry widens: a headless positive still reproduces the incident, but a headless negative is weaker than a Wayland negative, because the rendering path differs more from live. Record that in the verdict clause.
- Ordering stands: run Wayland-nested first. If it fails, run Council A Path A (seatd-launch plus render node, plugin line removed as control). If A fails at the DRM step only, run Path B (vkms). If C, A, and B all fail, option C is dead by exhaustion and the choice is A versus D from the decision doc, exactly as Y6 concluded.

## What I verified, and what stays UNVERIFIED

Verified read-only via ssh-laptop.sh on 2026-11-21 about 18:50 +07:

- /tmp/y6-nested/run-nested-wayland.sh does not exist; /tmp/y6-nested/conf/hyprland-wayland.conf does not exist. Present: run-nested.sh (headless env), conf/hyprland.conf (HEADLESS-1, plugin line, foot exec-once), 5 attempt logs, seatd.log. /tmp/y6-nested/run/hypr/ holds 5 stale signature dirs from the crashed attempts.
- Live socket /run/user/1000/wayland-1 exists (single socket), live hypr sig dir is a single entry. No run_agyq2, run_live, or E1 process running at check time. zen_dom.lock exists, 0 bytes, no flock holder shown. Zen PID 27958 is the owner's browser, not a runner. Live Hyprland PID 1515 alive (per Y6 18:23 check, not re-polled by me beyond the process list, which showed Hyprland PID 1515 running).
- seatd-launch present at /usr/bin/seatd-launch; grim, foot, kitty present; /dev/dri/renderD128 and renderD129 present (per Council A verification, not re-checked by me).
- indicator.py: LIQUID_VERSION '1.1.1-cu.1', LIQUID_READY_TIMEOUT 30.0, _valid_liquid requires schema 1, version match, active true, shaders ready or pending (pending rejected when ready=True), layers enabled and active with reason null, windows and subsurfaces disabled. setup.py _hook_body applies the optics profile via dofile when exactly one hyprglass of the right version is loaded.
- The 20/11 incident record (redteam worker4): 10 Hz idle flicker, 18:53 to 19:02, no input, no screenshots; animated backdrop is H-E, UNVERIFIED CANDIDATE, with E2 defined as a static-versus-animated comparison.

UNVERIFIED, stated as such:

- Whether Hyprland 0.57.2 executes a .lua file through `source=` in hyprland.conf.
- Reload behavior for a newly added plugin line in a nested compositor.
- Which command, log path, or counter field yields paint callback and commit counts inside the nest (no paint or callback counter found in scripts/indicator.py by those names).
- The full shader state vocabulary beyond 'ready' and 'pending'.
- seatd versus logind coexistence on one VT, Aquamarine DRM acceptance of a render-only node, Aquamarine on vkms plus GBM and EGL behavior there (all per Council A, not re-proven by me).
- What, if anything, was actually animating behind the pill on 20/11. No backdrop frames exist.

No launch was performed, no file was modified on the laptop, the live session was not touched. No personal info is in this paper.

## Timed run log

- 18:45 to 18:50: read Y6 draft, decision doc, Council A paper, pending decisions section 2, redteam worker4 incident record.
- 18:50 to 18:58: read-only SSH checks (nested files, live socket, runner processes, flock state) and repo reads (indicator.py liquid gate, setup.py hook, run_agyq2.py flock preflight).
- 18:58 to 19:05: wrote this paper, committed and pushed on todolist-push.
