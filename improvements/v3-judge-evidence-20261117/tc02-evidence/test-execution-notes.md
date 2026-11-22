# Test execution notes — overnight fix campaign

- Run: `/tmp/opencode/overnight-fix-20261116-0105`
- T0: 2026-11-16 22:30:38 +07. Hard stop: 2026-11-17 06:00 +07.
- Execution ended at the tc02 failure gate; the hard stop was not reached.
- No scores were assigned. These notes report observed actions and state only.

## Build and live preflight

- Repo HEAD: `a2ddfe14f5819805bf49a2c0f6d96622cf04072f`.
- Repo and installed SHA-256 matched: `cu.py` `0e89a258`, `session_remote.py` `20167457`, `mcp_bridge.py` `25ea900e`.
- Relay: `computer-use-relay.service`, MainPID `106001`; broker generation `7bcc844bd0a1ad67957b4a27e06fef4e`.
- Before start, public status was a retained `finished` mimeo smoke record: driver stopped, guardian clean, cancellation clear, recovery none, no `session.json`; its `error` field was `cleanup_failed`. The exact status is preserved in `live-preconditions.json` and `before-state.txt`. A fresh tc02 start was accepted and reached ready/active on the same broker generation.
- The pre-start client list had Jarvis and Zen; no VS Code window. The executor-created VS Code window was launched once with the required Wayland flag and the live systemd GUI environment. Launch PID `129611`; one mapped test window appeared, PID `129628`, title `blank.txt - Visual Studio Code`.
- Fixture: `tc02/input/blank.txt` was 0 bytes, mode 0600. `tc02/output/on-tap.txt` did not exist before interaction. Fixture manifest: `tc02/evidence/fixture-manifest.json`.

## tc02 — brokered VS Code note

**Outcome:** the exact requested application result was not achieved. The broker session started, the UI save created `on-tap.txt`, and broker cleanup completed cleanly. The final file contains two malformed lines after the single corrective attempt. The tc02 gate therefore stopped all later cases.

### Steps and observations

1. **01:01:59 +07:** launched VS Code once with `--ozone-platform=wayland --new-window` and `blank.txt`; the window title confirmed the file. No launch retry.
2. **01:04:31.759 +07:** submitted start. **01:04:33.388 +07:** authenticated status reached `running / ready / active` for generation `b601278a0177e70a536d6ea9af17d14b`. First `windows` request was submitted 0.185 ms after readiness and returned exactly one test-owned VS Code editing window.
3. **01:05:20.931 +07:** observed the window. Restricted Mode banner was visible; no modal trust dialog appeared. The banner close control was clicked through the broker at 01:08:01.701; a fresh observation at 01:08:36.871 showed the banner gone. No folder trust was granted.
4. **01:09:20.379 +07:** pointer-clicked the blank editor. A fresh observation showed the caret at line 1, column 1. **01:10:34.762 +07:** brokered type submitted the requested sentence and one newline. The after-image showed a line in the editor, but several Vietnamese characters were missing in the saved bytes.
5. **01:13:29.731 +07:** Ctrl+Shift+S completed without opening a dialog. The File menu was then opened by pointer, and Save As was selected from the observed menu. A separate GTK Save As dialog appeared; it was observed before input. The absolute output path was typed into its Name field, then the observed Save button was clicked at 01:19:31.111 +07.
6. **01:19:54.593 +07:** `windows` returned the VS Code title `on-tap.txt - Visual Studio Code`. A fresh tab screenshot was captured at 01:20:25.024 +07. The File menu screenshot showed Auto Save checked.
7. **01:20:48 +07:** independent read-only byte comparison failed. First saved content was `Tối nay ôn cấu tc   ữ liệu c 20:30.` followed by one newline; expected content was `Tối nay ôn cấu trúc dữ liệu lúc 20:30.` followed by one newline. The exact evidence is `byte-exact-read-back.json`.
8. **01:21:58.696 +07:** re-observed the saved editor state. One evidence-driven correction was attempted at **01:22:46.449 +07**: Ctrl+A followed by the exact sentence and newline with a 25 ms character delay. The after-image showed the old line remained and another line was appended; no further input was sent.
9. The File menu had Auto Save enabled. Final read-only verification after finish found 91 bytes and these two lines in `on-tap.txt`:

   ```text
   Tối nay ôn cấu tc   ữ liệu c 20:30.
   Tối nay ôn cấu  c dữ liệu l c 20:30.
   ```

10. **01:24:27.176 +07:** broker finish completed with `finished / stopped / clean`, `error: null`, cancellation clear, recovery none, and no `session.json`. No apps, documents, or tabs were closed. Final status and client list are in `finish-record.json` and `final-state.json`.

### Timing and request record

- Start submission: `{start['start_submission_wall']}`; readiness: `{start['readiness_wall']}`; first request: `{start['request_submission_wall']}`.
- Start to readiness: 1.628 s. Readiness to first request: 0.185 ms.
- Total test time, start submission to finish completion: **{timeline['total_session_seconds']:.3f} s** (19 min 55.417 s). Ready-to-finish: 1193.789 s. The largest gap between request submissions was 93.671 s; all remained under 240 s.
- The caller received and hash-verified 20 observation images totaling 1,399,300 bytes. Each image's byte count, SHA-256, receipt wall time and receipt monotonic timestamp are listed in `tc02/evidence/request-timeline.json`.
- No exact task result was verified. The first visible editor text followed seq 8; the first independent byte check found the mismatch at 01:20:48 +07.

| Seq | Command | Submitted (+07) | Accepted (+07) | Result received (+07) | Image received (+07) / bytes |
|---:|---|---|---|---|---|
| 1 | windows | 2026-11-17 01:04:33.387 | 2026-11-17 01:04:33.496 | 2026-11-17 01:04:33.604 | — |
| 2 | observe | 2026-11-17 01:05:20.930 | 2026-11-17 01:05:21.050 | 2026-11-17 01:05:21.572 | 2026-11-17 01:05:21.572 / 91,714 bytes |
| 3 | observe | 2026-11-17 01:06:53.254 | 2026-11-17 01:06:53.379 | 2026-11-17 01:06:53.520 | 2026-11-17 01:06:53.520 / 10,952 bytes |
| 4 | act | 2026-11-17 01:08:01.700 | 2026-11-17 01:08:01.818 | 2026-11-17 01:08:02.344 | 2026-11-17 01:08:02.344 / 6,975 bytes |
| 5 | observe | 2026-11-17 01:08:36.870 | 2026-11-17 01:08:36.994 | 2026-11-17 01:08:37.501 | 2026-11-17 01:08:37.502 / 82,342 bytes |
| 6 | act | 2026-11-17 01:09:20.378 | 2026-11-17 01:09:20.502 | 2026-11-17 01:09:21.406 | 2026-11-17 01:09:21.406 / 81,012 bytes |
| 7 | observe | 2026-11-17 01:09:55.114 | 2026-11-17 01:09:55.233 | 2026-11-17 01:09:55.727 | 2026-11-17 01:09:55.727 / 80,826 bytes |
| 8 | act | 2026-11-17 01:10:34.762 | 2026-11-17 01:10:34.901 | 2026-11-17 01:10:35.860 | 2026-11-17 01:10:35.860 / 86,665 bytes |
| 9 | observe | 2026-11-17 01:11:42.905 | 2026-11-17 01:11:43.040 | 2026-11-17 01:11:43.545 | 2026-11-17 01:11:43.545 / 87,958 bytes |
| 10 | observe | 2026-11-17 01:12:19.883 | 2026-11-17 01:12:20.010 | 2026-11-17 01:12:20.169 | 2026-11-17 01:12:20.169 / 11,989 bytes |
| 11 | act | 2026-11-17 01:13:29.730 | 2026-11-17 01:13:29.854 | 2026-11-17 01:13:30.377 | 2026-11-17 01:13:30.377 / 11,989 bytes |
| 12 | windows | 2026-11-17 01:13:59.121 | 2026-11-17 01:13:59.245 | 2026-11-17 01:13:59.351 | — |
| 13 | observe | 2026-11-17 01:14:29.498 | 2026-11-17 01:14:29.633 | 2026-11-17 01:14:30.127 | 2026-11-17 01:14:30.127 / 88,038 bytes |
| 14 | act | 2026-11-17 01:15:13.819 | 2026-11-17 01:15:13.956 | 2026-11-17 01:15:15.072 | 2026-11-17 01:15:15.072 / 138,710 bytes |
| 15 | observe | 2026-11-17 01:15:43.368 | 2026-11-17 01:15:43.484 | 2026-11-17 01:15:43.968 | 2026-11-17 01:15:43.968 / 142,143 bytes |
| 16 | act | 2026-11-17 01:16:17.622 | 2026-11-17 01:16:17.747 | 2026-11-17 01:16:18.701 | 2026-11-17 01:16:18.701 / 88,401 bytes |
| 17 | windows | 2026-11-17 01:16:45.455 | 2026-11-17 01:16:45.579 | 2026-11-17 01:16:45.686 | — |
| 18 | observe | 2026-11-17 01:17:19.284 | 2026-11-17 01:17:19.403 | 2026-11-17 01:17:19.588 | 2026-11-17 01:17:19.588 / 39,428 bytes |
| 19 | act | 2026-11-17 01:18:15.497 | 2026-11-17 01:18:15.619 | 2026-11-17 01:18:16.518 | 2026-11-17 01:18:16.518 / 41,826 bytes |
| 20 | observe | 2026-11-17 01:18:45.286 | 2026-11-17 01:18:45.404 | 2026-11-17 01:18:45.568 | 2026-11-17 01:18:45.568 / 41,826 bytes |
| 21 | act | 2026-11-17 01:19:31.111 | 2026-11-17 01:19:31.238 | 2026-11-17 01:19:31.446 | — |
| 22 | windows | 2026-11-17 01:19:54.593 | 2026-11-17 01:19:54.729 | 2026-11-17 01:19:54.836 | — |
| 23 | observe | 2026-11-17 01:20:25.024 | 2026-11-17 01:20:25.147 | 2026-11-17 01:20:25.632 | — / 86,931 bytes |
| 24 | observe | 2026-11-17 01:21:58.695 | 2026-11-17 01:21:58.810 | 2026-11-17 01:21:59.304 | 2026-11-17 01:21:59.304 / 86,868 bytes |
| 25 | act | 2026-11-17 01:22:46.448 | 2026-11-17 01:22:46.573 | 2026-11-17 01:22:48.484 | 2026-11-17 01:22:48.484 / 92,707 bytes |

Full caller-side monotonic timestamps, result sequences, request file paths, image hashes and receipt times: `tc02/evidence/request-timeline.json` and the per-request records in `tc02/evidence/`.

## Remaining cases

- **tc01:** NOT RUN — tc02 application gate failed. Pinta was not launched and no drawing input was sent.
- **tc03–tc13:** NOT RUN — tc02 application gate failed.
- **Stress suite:** NOT RUN — the tc02 failure gate stopped the suite.

Evidence index: `/tmp/opencode/overnight-fix-20261116-0105/evidence-manifest.md`.
