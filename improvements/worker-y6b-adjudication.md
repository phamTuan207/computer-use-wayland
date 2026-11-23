# Worker Y6b adjudication: council + redteam verdicts on the Wayland-nested probe run

- Date: 2026-11-21, 19:05-19:10 +07
- Adjudicator: Y6b (Muse subagent). Branch: todolist-push.
- Papers: worker-y6b-council-1-feasibility.md (C1), worker-y6b-council-2-evidence.md (C2), worker-y6b-council-3-safety.md (C3), worker-y6b-redteam.md (redteam).
- Subject: /tmp/y6-nested/run-nested-wayland.sh (Y6 design, commit 482e4ba) plus run-nested-pill.py and conf files.

## Verdict: DO NOT RUN AS WRITTEN

All four papers agree the run as written cannot produce a verdict. Two independent fatal bugs are proven by two independent agents with live commands:

1. The pill geometry parser crashes on real Hyprland 0.57.2 layers JSON (the extra "levels" wrapper). Proven by C1 and C2 with the exact snippet and traceback.
2. capture() fails on every call, twice over: grim -g takes "X,Y WxH" (space form) but the script passes comma form, and -g and -o are mutually exclusive. Proven by redteam and C2 with live grim commands.

The run would pass its positive control, start the nest and the pill, tile the nest window over the live screen, then abort at armA frame 01 with zero arm data, and teardown would destroy the nested log on the abort path. That is not a weak run. It is a run that cannot measure.

## Reconciliations (where the papers disagree)

1. grim invalid geometry, cause: C1 attributed it to monitor offsets (eDP-2 at 2464,902). Redteam and C2 proved it is the FORMAT: grim -g "0,0,200,200" returns "invalid geometry" regardless of position, and grim -g "2464,902 200x200" succeeds. Redteam is right. C1's determinism evidence (byte-identical repeat frames) still stands and is adopted.
2. run_agyq2.py flock references: C1 claims grep empty. My own grep on todolist-push shows the preflight at lines 1334/1458/1492 (added by Y4d, commit 1e3901c). Redteam found the preflight in /tmp/worker-y4-server/run_agyq2.py (lines 1458-1496) and zero references in run_live.py, run_agyq.py, run_fcck.py and the y5-tests copy. Resolution: the CURRENT repo run_agyq2.py HAS the preflight, but the laptop checkout (4500a18, 28 behind origin) does NOT, and the y5-tests copy does NOT. Flock coverage is per launch wrapper, not per file. The C1 change 6 spirit (process check, do not rely on flock alone) stands; its premise is corrected.
3. Laptop repo state: my brief said detached HEAD with uncommitted changes. C1, C2 and redteam all correct this: the laptop repo is on branch todolist-push at 4500a18, tracked tree clean, 28 commits behind origin, and scripts/indicator.py is identical to origin. The pill therefore imports exactly the origin indicator.py. I must NOT pull the laptop repo before the run, or the imported code changes under the frozen design.
4. Timeout 300: C1 computes worst case about 219s (margin about 80s) and recommends 420. C2 measures grim at 0.028s per capture, sees about 100s of slack, and recommends 600 anyway. C3 also says 600. Adopted: 600. The timeout is a safety net only; the script's own gates bound the time.
5. Arm B verdict: C1 says downgrade the arm B only verdict to SUGGESTIVE (testsrc2 spatial non-uniformity plus refraction). C2 says keep it as REPRODUCED in the animated arm but only at >= 3 with validity gates. Adopted: C2's rule (>= 3, with B_BG_DIFF >= 15/31 gate and the two-frame motion re-validation), because the gates answer C1's objection: if the backdrop sample is genuinely moving and the pill changes while the sample does not, that is flicker evidence, not refraction, since refraction follows the backdrop. If the gates cannot be met, arm B is VOID, not SUGGESTIVE.
6. Log-pattern arm: C2 says drop it (calibration: 6 matches in 4959 live-log lines, zero repaint events, 0 growth over 32s idle). Redteam agrees it is not a callback counter. Adopted: drop log_delta entirely, including its echo bug (C1 change 10 becomes moot).

## Unified fix list (applied by Y6b, in order)

U1. Layers parser: iterate mdata.get("levels", {}) (C1-1, C2-1). Emit geometry in grim form "X,Y WxH".
U2. capture(): drop -o, geometry in "X,Y WxH" form (C1, C2-2, redteam F1). BACKDROP_GEOM becomes "0,0 200x200" / "760,0 200x200".
U3. Remove hl.exec_cmd mpv/foot autostart from conf/hyprland-wayland.lua. Launch mpv from the launcher with explicit nest env after the plugin and liquid checks pass, record its PID, kill by PID. Remove foot entirely (no measurement uses it; C2 notes it is never closed and could overlap the sample corner or blink). Replace pgrep -x mpv / pgrep -x foot checks with PID checks (kill -0 $MPV_PID). (C1-2, C2-4, redteam F9.)
U4. Arm A static backdrop: show a controlled static image fullscreen (a frozen frame of backdrop.mp4, extracted with ffmpeg to backdrop-static.png, displayed by mpv paused) instead of a dead terminal, and capture a backdrop sample during arm A at the same cadence. Require 0 backdrop diffs or arm A is VOID. (Redteam F2, C2-6.)
U5. Gate the Wayland backend check: grep -a -q "Wayland backend" "$LOG" || fail. Keep a display-only grep. (C1-3, redteam F5.)
U6. Parse hyprglass status JSON explicitly before the liquid gate: fail fast with the observed version recorded if version is not 1.1.1-cu.1 or versionCheck is not match. Grep the nested log for the "Y6-NEST-HOOK: hyprglass not ready" marker after the plugin check and fail fast with that diagnosis instead of burning the 60s gate. (C1-5, redteam F6.)
U7. Teardown, all of: (a) copy $RUN_DIR/hypr/$SIG/hyprland.log to $NEST/hypr-saved-<timestamp>-$SIG before rm -rf; (b) guard pkill/rm -rf so they run only if the nest was actually started; (c) kill the nest process group (kill -- -$NESTED_PID, then delayed SIGKILL to the group), record the real nested Hyprland PID; (d) close fd 9 in every background launch (9>&-); (e) fix the live version check (no pipe through head); (f) verify no Hyprland besides the live PID remains and the lock is free after teardown; (g) trap TERM/INT/HUP as well as EXIT; (h) raise timeout 300 to 600. (C1-4, C1-8, C2-3, C2-4, C3-2, C3-3, C3-6, redteam F9.)
U8. Runner-quiet gate: before acquiring the lock, check for live runner processes (pgrep for run_agyq2.py, run_live.py, run_agyq.py, run_agy_y2.py, run_fcck.py, geckodriver, Codex sessions driving browsers) and abort if any are present. The flock is a tripwire, not a guarantee. (C1-6, C3-1, C3-6, redteam F10.)
U9. Pill: call native.command("show") BEFORE printing ready, print ready only after show succeeds, so the launcher ready signal means visible. Launcher still waits for "ready". (C1-7, equivalent to C2-8.)
U10. Verdict thresholds: A_DIFF >= 3 is REPRODUCED, 1-2 is INCONCLUSIVE (rerun arm A once, same rule decides; if still 1-2, report INCONCLUSIVE with the counts), 0 is negative. Same rule for B_PILL_ONLY. Report the counts in every case. (C2-5.)
U11. Validity gates: arm A backdrop sample must be 0 diffs or arm A is VOID; arm B requires B_BG_DIFF >= 15/31 or VOID; after restarting mpv for arm B, wait until two consecutive full-output frames differ (bounded 10s) before starting arm B captures. Add explicit VOID verdict lines; a VOID arm prints VOID, never NOT reproduced. (C2-6, redteam F3, redteam H10.)
U12. Backdrop corner from the full pill rect: compute intersection with each candidate corner, pick a corner with zero intersection, fail if none exists. Re-read pill geometry from nested layers immediately before arm B and abort or re-baseline if it changed. Add a bounds check that the pill rect lies inside the 960x540 output before capturing. (C1-11, C2-7, C2-2.)
U13. Sampling: randomize inter-frame delays (0.6-1.4s) so a periodic about 10 Hz flicker cannot hide by phase lock with a 1s cadence. (Redteam F4.)
U14. Drop the log-pattern arm entirely (remove log_delta and the counts from the arm echo lines). Label B_PILL_DIFF honestly in the SUMMARY: only B_PILL_ONLY is flicker evidence, the pill-surface region differs under pure expected motion. (C2-9.)
U15. Resolve LIVE_SIG and live PID at runtime (ls -t /run/user/1000/hypr/ | head -1, pgrep -x Hyprland), fail if ambiguous, use those values in live() and teardown. Keep the currently verified values only as a comment. (C1-12, C3-7, redteam H11.)
U16. Pre-launch cleanup: also remove stale /tmp/y6-nested/run/wayland-1 and wayland-1.lock. Record the actual nest output name with nest hyprctl -j monitors after signature discovery and use it in the grim -o calls for the positive control. (C1-13, C1-14.)
U17. Record the nest renderer lines from the nested log in the report. (Redteam F5, H8.)
U18. Classify plugin-load failures from the nested log (version/API vs renderer) before declaring option C dead. On load failure, grep the nested log for the load error and record the classification. (Redteam F5, H5.)
U19. Overall script deadline (25 minutes from start, checked before each arm) and owner-return detection. CORRECTION (Y6b, proven live 19:09): loginctl IdleHint is UNUSABLE on this machine. All 8 user sessions report IdleHint=no while the owner is away, including session 2 (seat0, tty1, the graphical Hyprland session). Hyprland/UWSM never sets IdleHint to yes. An abort gate on IdleHint would false-abort every run. So check_idle is WARN-ONLY: it logs the IdleHint value and never aborts. The owner-return protection is the explicit Muse go at run time (the parent confirms the owner is still away immediately before the run) plus the 25-minute deadline plus the run's short duration (about 4-6 minutes). Residual risk recorded. (Redteam F9, H9, C3-7.)
U20. Runner output: tee the runner's own stdout to a timestamped file inside the script, and put frames in a timestamped per-run directory. The detached invocation also redirects stdout to a timestamped file. (C2-3.)
U21. Post-teardown stray process check: record any surviving nested Hyprland, native indicator child, mpv, or foot. (C1-15.)

## What the adjudication does NOT do

- It does not change the design: two frame-diff arms, positive control, verdict asymmetry (a nest negative never exonerates live). The arms are repaired, not redesigned.
- It does not authorize running before the re-verification checklist (C2) is complete: bash -n, py_compile, fixed parser against live layers JSON (clean exit 1, no traceback) and synthetic JSON (prints geometry), one grim -g "X,Y WxH" call with the exact string the fixed script will pass, teardown dry harness with a fake nested log, confirm tee + timestamped frames, confirm no pkill -x on a shared process name remains.
- It does not resolve the A1 coordination question: the A1 pilot arms do not respect zen_dom.lock, and Y8 E1 / Y9 agy-y2 runner files were not found, so their lock behavior is unverified. Before my window, Muse must confirm in writing that no A1 arm is scheduled in my window and name the exact launch wrapper every queued runner uses. The process check (U8) is the real gate; the flock is secondary.
- It does not order a second council: C1 says no second council is needed for mechanical edits if changes 1-9 are applied as written. The measurement repairs (U4, U10, U11, U13) are applied exactly as C2 and redteam specified them, so no re-review is required. If re-verification forces a deviation from the specified repairs, that part goes back for review before running.

## Slot status

My live run still waits for the queue: Y8 E1 arms (running now, worker Y8b), then Y9 agy-y2 live, then Y11 proof, then Y6b. The fixes do not change the queue. I apply the fixes and re-verify while waiting.
