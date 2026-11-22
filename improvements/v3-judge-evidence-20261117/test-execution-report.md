# Test execution report — tc02 then tc01 (overnight rerun, 16-17/11/2026)

- Worker J (test executor), reported 01:35 17/11/2026 (+07). T0 = 22:30:38 16/11.
- Executor: Codex Luna 6 max (`gpt-6-luna`, reasoning max, `--sandbox danger-full-access`), launched detached from the repo dir on the laptop via `~/workspace/ssh-laptop.sh`.
- Run dir (laptop): `/tmp/opencode/overnight-fix-20261116-0105` (tc02/ + tc01/ each with input/, output/, evidence/).
- Evidence manifest (laptop, frozen 01:30:36): `/tmp/opencode/overnight-fix-20261116-0105/evidence-manifest.md` — 113 artifacts hashed (SHA-256). VM mirror of the key evidence: `improvements/tc02-evidence/` (notes, manifest, executor log, before-state, preconditions, on-tap.txt, byte-exact read-back, request timeline, finish record, final state, 7 key screenshots).
- No scores are assigned in this report. The independent judge scores from the frozen evidence.
- No writes were made to the repo or the installed tree. No user apps, documents, or tabs were closed.

## Execution build (verified live)

- Repo HEAD: `a2ddfe14f5819805bf49a2c0f6d96622cf04072f`, tree clean.
- Repo == installed hashes: `cu.py` 0e89a258, `session_remote.py` 20167457, `mcp_bridge.py` 25ea900e.
- Relay: `computer-use-relay.service`, MainPID 106001, broker generation `7bcc844bd0a1ad67957b4a27e06fef4e`.
- Before start: retained finished record (mimeo smoke B1, `stop_reason: explicit_finish`); public status also carried a stale `error: cleanup_failed` string (known shared-state artifact from the B2 direct session; does not block a new start — a fresh tc02 start was accepted on the same broker generation). No `session.json`, cancelled false, recovery none.

## Incident during the run: executor v1 stopped on a stale sync log

- V1 (Codex PID 122828, launched 00:50) read `/tmp/opencode/sync-codex.log` / `sync-codex-report.md` ("STEP 2 BLOCKED; release rolled back") and concluded at 00:53:40 that no session/app launch was authorized. It created run dir `/tmp/opencode/overnight-fix-20261116-0050` (empty case dirs + one log line) and stalled; no session started, no input sent.
- That verdict is stale: a later re-sync published 23:13 with `--check` exit 0, the relay was restarted 00:19, and live hash comparison showed repo == installed, confirmed by Worker I's two passing smokes (00:40-00:48).
- Worker J killed ONLY PID 122828 (plain `kill`, not `pkill -x codex`; PIDs 3194/3704/3879 are other sessions and were untouched) and relaunched as v2 (PID 126149) at ~00:58 with a corrected prompt: verify preconditions LIVE and never let a stale log override live state; GUI env from `systemctl --user show-environment` (no `env.sh` exists in the repo); no broad filesystem searches. V2's live preflight (00:59:10) confirmed hashes match, broker clean, relay 106001, and proceeded. The aborted v1 run dir is left in place, unused.

## tc02 — brokered VS Code note: APPLICATION GATE FAILED, suite stopped

Task: open VS Code, type `Tối nay ôn cấu trúc dữ liệu lúc 20:30.` + one newline, save as `on-tap.txt`.

### What ran, step by step (all +07, 17/11)

1. 01:00:13 — fixture ready: `tc02/input/blank.txt` 0 bytes, mode 0600; `on-tap.txt` absent. Before-state recorded.
2. 01:01:14 — request-file skeletons + driver plan prepared; no coordinates chosen.
3. 01:01:59 — VS Code launched exactly once: `code --ozone-platform=wayland --new-window <blank.txt>` with the systemd user GUI environment. Launch PID 129611, returncode 0; one window (PID 129628, title `blank.txt - Visual Studio Code`).
4. 01:04:31.759 — broker `start` submitted (fresh owner `tc02-overnight-fix-20261116-0105`, fresh lease `~/.cache/agent-computer-use/overnight-tc02-qwazkoku/tc02.lease`). 01:04:33.388 — authenticated status `running / ready / active`, task generation `b601278a0177e70a536d6ea9af17d14b`, same broker generation. Start-to-readiness 1.628 s.
5. 01:04:33.387 — first request (`windows`, seq 1) submitted 0.185 ms after readiness; completed; exactly one test-owned VS Code editing window (`blank.txt - Visual Studio Code`, address 0x55abc9eed380).
6. 01:05:21 — fresh observation (seq 2), 91,714 image bytes received and hash-verified.
7. 01:06:53 — fresh cropped observation (seq 3): Restricted Mode banner visible, NO modal trust dialog. Banner close control clicked through the broker at 01:08:01.701 (seq 4, image point 1832,27); fresh observation 01:08:37 confirmed the banner gone. No folder trust was granted; work stayed in Restricted Mode.
8. 01:09:20.379 — pointer-clicked the blank editor (seq 6, image point 120,85); fresh observation showed caret at line 1, column 1.
9. 01:10:34.762 — brokered keyboard type submitted the exact sentence + one newline (seq 8); completed; after-image 86,665 bytes. 01:11:43 — explicit text observation (seq 9, 87,958 bytes): one sentence visible on line 1, caret on empty line 2, no dialog/banner. A tight line crop (seq 10) showed Vietnamese glyphs rendering box-like at that scale, so exact text was not asserted from pixels.
10. 01:13:29.731 — Ctrl+Shift+S (seq 11) completed but did NOT open Save As (verified by fresh observe seq 13 + windows seq 12, not assumed). Recovered human-like: pointer-clicked the observed File menu (seq 14, 47,14), selected File > Save As (seq 16, 80,316). A separate GTK Save As dialog appeared; observed before input (seq 18). Name field held selected `blank` + `.txt`, current folder was the tc02 input dir.
11. 01:18:15.497 — clicked Name, selected all, typed the absolute path `/tmp/opencode/overnight-fix-20261116-0105/tc02/output/on-tap.txt` (seq 19). 01:19:31.111 — pointer-clicked the observed Save button (825,22; seq 21, `--no-after` because the dialog closes). 01:19:54 — windows (seq 22) showed title `on-tap.txt - Visual Studio Code`; post-save observation seq 23 (86,931 bytes) confirmed the tab.
12. 01:20:48 — independent read-only UTF-8 byte comparison FAILED: expected 50 bytes (`Tối nay ôn cấu trúc dữ liệu lúc 20:30.\n`, sha256 `8da1f562…`), actual 45 bytes (`Tối nay ôn cấu tc   ữ liệu c 20:30.\n`, sha256 `8bb4c179…`), `exact_byte_match: false`. Evidence: `tc02/evidence/byte-exact-read-back.json`.
13. 01:22:46.449 — ONE evidence-driven corrective attempt (seq 25): Ctrl+A then the exact sentence + newline at 25 ms per character. The after-image (92,707 bytes) showed the old malformed line remained and a second line was appended; Ctrl+A did not replace the document. No further input was sent.
14. 01:24:27 — broker `finish` completed: `finished / stopped / clean`, `error: null`, cancellation clear, recovery none, no `session.json`. No apps/documents/tabs closed. VS Code left open with the test window as-is.

### Final file state (verified read-only, VM copy hash matches laptop)

`/tmp/opencode/overnight-fix-20261116-0105/tc02/output/on-tap.txt`, 91 bytes, sha256 `b10ffde1f54106f160461c967aa6c73f96f06cd8be279a30f57d8d797817d48c`:

```text
Tối nay ôn cấu tc   ữ liệu c 20:30.
Tối nay ôn cấu  c dữ liệu l c 20:30.
```

### Total task time (tc02)

- Session start submission (01:04:31.759) to finish completion (01:24:27.064): **1195.417 s (19 min 55 s)**. Ready-to-finish: 1193.789 s.
- Breakdown: start to readiness 1.628 s; readiness to first request 0.185 ms; windows + first observe ~2 min (01:04:33-01:05:21, includes banner-crop observation at 01:06:53); banner dismissal 01:08:02-01:08:37; editor click + focus observation 01:09:20-01:09:55; type 01:10:35 + text verification 01:11:43-01:12:20; Save As flow 01:13:30-01:19:54 (includes the failed Ctrl+Shift+S and the File-menu recovery); post-save verification + byte check 01:20:25-01:20:48; corrective attempt 01:21:59-01:22:48; finish 01:24:27.
- 25 broker requests, 0 refusals. Largest gap between request submissions: 93.671 s (all gaps under the 240 s limit; no keep-alive was needed, no idle expiry). 20 observation images received and hash-verified, totaling 1,399,300 bytes. Full per-request monotonic timestamps, byte counts, and image hashes: `tc02/evidence/request-timeline.json`.
- Prep before the session (run-dir creation 00:56:13 through VS Code launch 01:01:59 and driver-plan prep) took ~8 min with no session held open, which is exactly the intended pattern.

### Why it failed (exact reason)

The brokered keyboard input dropped Vietnamese characters on BOTH typing attempts, differently each time:

- Attempt 1 (no per-character delay): `trúc` lost `rú`, `dữ` lost `d`, `lúc` lost `lú` — `Tối nay ôn cấu tc   ữ liệu c 20:30.`
- Attempt 2 (25 ms/char, after Ctrl+A): `trúc` lost `trú`, `lúc` lost `lú` — `Tối nay ôn cấu  c dữ liệu l c 20:30.`

The typed text reached the editor (a line appeared after each type, and the file saved through the UI), but the delivered keystrokes lost composed/diacritic characters. The per-character delay did not fix it, and the Ctrl+A selection did not take effect (old line remained, new line appended). The second line reached the file because VS Code Auto Save was checked (seen in the File-menu screenshot), so the appended line was persisted without a second explicit save.

This is a broker/driver keyboard-input defect for Vietnamese text, not a session-start, window-targeting, or Save-As failure: start/readiness, windows identification, banner handling, editor click, Save As dialog, and broker finish all completed through the real session path. The meaningful-result zero gate fails because the saved file does not contain the exact requested sentence.

### tc02 outcome for the judge

- Broker session: started, ready, finished clean (generation `b601278a…`, 25 requests, finish `finished/stopped/clean`).
- Application result: file saved through the UI, but its bytes do not match the requested sentence (two malformed lines, 91 bytes). No exact task text appears in the file.
- Failure-gate consequence: the suite STOPPED here per the binding contract.

## tc01 — NOT RUN (tc02 gate)

Pinta was never launched and no drawing input was sent. Reason: tc02 application gate failed (see above).

## tc03-tc13 — NOT RUN (tc02 gate)

All 11 cases not run. Reason: tc02 application gate failed.

## Stress suite — NOT RUN (tc02 gate)

Repeated sessions, rapid inputs, long sessions, expiry/recovery, broker load, many observations: not run. Reason: tc02 application gate failed; the hard stop (06:00) was not reached.

## Totals for the judge

- Attempted: tc02 only. tc01, tc03-tc13, stress suite: NOT RUN (tc02 gate).
- No score is stated here; the judge scores tc02 from the frozen evidence and lists all 13 cases (0 for every NOT RUN case).

## Evidence manifest

- Laptop (frozen 01:30:36, 113 artifacts): `/tmp/opencode/overnight-fix-20261116-0105/evidence-manifest.md`
- Run dir: `/tmp/opencode/overnight-fix-20261116-0105` (executor log, before-state, live-preconditions, test-execution-notes, tc02/evidence with 107 files incl. 25 per-request records, tc02/output/on-tap.txt)
- VM mirror (key evidence only): `improvements/tc02-evidence/` — `test-execution-notes.md`, `evidence-manifest.md`, `executor-log.md`, `before-state.txt`, `live-preconditions.json`, `tc02/output/on-tap.txt` (sha256 `b10ffde1…`, matches laptop), `tc02/evidence/byte-exact-read-back.json`, `request-timeline.json`, `finish-record.json`, `final-state.json`, `start-readiness.json`, `windows-result.json`, screenshots `after-type-sentence.png` (sha256 `c93c632c…`, matches manifest), `editor-sentence.png`, `after-corrective-type.png`, `tab-on-tap.png`, `trust-banner-observation.png`, `observation-01.png`, `save-as-dialog.png`.
- Full evidence lives on the laptop run dir; the VM mirror is a subset for the judge/parent. The aborted v1 run dir `/tmp/opencode/overnight-fix-20261116-0050` holds only empty case dirs + one log line and is not evidence for any case.

## Notes / caveats for the parent

- The executor's `test-execution-notes.md` leaves two timing placeholders unfilled as literal `{start['start_submission_wall']}` / `{timeline['total_session_seconds']:.3f}` template text. The real values are in this report and in `request-timeline.json` (start 01:04:31.759, readiness 01:04:33.388, total 1195.417 s). Minor report defect, evidence itself is complete.
- VS Code Auto Save was ON in the test window (visible in the File-menu screenshot). That is how the second malformed line reached disk without a second Save As. It does not change the outcome but the judge should know the second line was auto-saved, not UI-saved.
- The `recovery: active` value seen in public broker status while the tc02 session was running returned to `none` after finish; finish record shows `error: null`. No action needed.
- Recommended follow-up (not done by this worker): the Vietnamese keyboard-input character loss is the concrete defect to hand to the fix loop — two attempts, different dropped characters each time, delay did not help. A retest with ASCII-only text would separate "typing is broken" from "Vietnamese composition is broken", but that would be a new test case, not part of this suite.
