# Worker F1a log: F1 live activation + council-3 5-step positive proof
# Owner order: F1 phase of the F1+F2 end-to-end proof. F3b healed the slot
# (Zen PID 496121, restart #3 23:44:11, probes OK 23:51:12) and signed off.
# All times wall-clock Asia/Ho_Chi_Minh + elapsed from task start 23:51.
# Rule: log EVERY event as it happens, never batched. No em/en dashes.

## 23:51 task start
- Spawned as F1a. Brief: run python3 scripts/activate-session-backend.py
  from the installed tree, then the council-3 5-step positive proof.
- Read improvements/worker-f1-guardian-fix-log.md in full (F1 root cause
  4 layers, drift repair, round 1 + round 2 fixes, wrapper, council-3
  5-step proof, preconditions 1-8).
- Read F3b final report (commit 7cde3d2, log improvements/worker-f3b-restart-log.md):
  slot HEALED by restart #3 (PID 496121), probe_r3 PASS, final probe
  23:51:12 PROBE1 OK 3d32d968 + PROBE2 OK b79465cd, 14 real tabs, 0 fixtures,
  Marionette 17 = 14 real + 3 pre-existing blanks. F1 SIGN-OFF given.
  Trigger: Arm E combination (sac + multiple DELETE /window + DELETE with
  sac current); A/B/C/D alone PASS. Rule: never Marionette-close tabs in
  bulk, never Marionette-close about:blank; BiDi close or UI right-click
  Close Tab only. Owner was active on ws2 at 23:43:43 (clone2 confirming
  todo): do NOT yank his screen; observe first, wait if he is active.
- VM repo todolist-push HEAD 7cde3d2 (F3b handover). 2 untracked files
  (multi-agent-deliberation-idea, muse-coordinate-accuracy) are not mine.

## 23:52 pre-flight (council-2 precondition 2, same-minute)
- Pinned values (installed native/visuals.json): abi
  11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_aq_0.16_hu_0.14_hg_0.6_hc_0.1_hlg_0.6;
  glass hyprglass-199153aea84a833d86f3eee21708e186c5a722c52259397735898b52f86df07f.so;
  guard cursor-guard-06712eafb74c15297f7c63cdd2ebdb752c1026e988660bb0c319ee1bb7f2c800.so;
  profile_sha256 9a15163491b543dde09c8388a8faf01f9b491c831647320ce2949d5737d8993c.
- Plugin list: hyprbars 1.0 ONLY. configerrors: empty. cu-cursor status:
  "unknown request" (guard not loaded, expected). Socket dir
  /run/user/1000/agent-computer-use/: does not exist (no session).
- Glass sha 199153ae... = filename + manifest. Guard sha 06712eaf... =
  filename + manifest. ldd: 0 not found on both.
- Live abiHash 11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_aq_0.16_hu_0.14_hg_0.6_hc_0.1_hlg_0.6
  = manifest abi exactly. Zen PID 496121 (stable, matches F3b handover).
- Wrapper --help: --manifest (default native/visuals.json), --glass-library,
  --guard-library, --abi, --profile-sha256. Holds owner_lock across glass +
  guard. Pre-flight ALL PASS. Next: fresh observe (owner-activity check)
  before any driving.
