# CLI-Anything end-to-end proof: held-out case G-01 (Obsidian)

- Date: 2026-11-19, work 12:05 to 12:20 Asia/Ho_Chi_Minh. Worker: Luna 6 Max.
- Laptop: user@192.0.2.1 (Omarchy/Hyprland). Repo ~/computer-use-wayland,
  branch speed-swarm, HEAD 0db0a43 at proof time.
- Task (held-out case G-01, verbatim): "Tao ghi chu moi trong Obsidian ten
  'Y tuong khoi nghiep', ghi 2 dong: 'Ban khoa hoc online.' va 'Lam app cho
  sinh vien.'" Expected result: file `Y tuong khoi nghiep.md` in the vault
  with exactly those 2 lines.
- No broker session, no computer-use session, 0 model calls, 0 observations.
  Every step went through the repo's `computer-use cli run` (HEAD 0db0a43).

## Commands and timing (wall-clock Asia/Ho_Chi_Minh)

All four through `python3 scripts/cu.py cli run obsidian -- ...` from the repo dir:

| Step | Command | rc | Wall |
|---|---|---|---|
| server status | `cli run obsidian -- server status` | 0 | 0.308s |
| vault create | `cli run obsidian -- vault create "Y tuong khoi nghiep.md" --content "Ban khoa hoc online.\nLam app cho sinh vien."` | 0 | 0.311s |
| vault read | `cli run obsidian -- vault read "Y tuong khoi nghiep.md"` | 0 | 0.316s |
| vault delete | `cli run obsidian -- vault delete "Y tuong khoi nghiep.md"` | 0 | 0.319s |

- Task wall (status plus create plus read): 0.943s (12:07:50.201 to 12:07:51.142).
- Whole proof script (incl. delete and disk verify): 1.28s (12:07:50.197 to 12:07:51.477).
- All four envelopes: ok true, returncode 0, empty stderr.

## Verification (byte for byte)

- After create, the file existed at vault root: 49 bytes.
- sha256: 3a674f1d92df3b05d26d61cb474ab2ba04f0e80ac015b07cf02a02009f0e86fa,
  exactly the expected hash for the 2 lines with NO trailing newline
  (the trailing-newline variant hashes to 8fca62a6... and did NOT match).
- `vault read` through the CLI returned exactly the same 2 lines.
- After `vault delete` through the CLI, the file was gone; the vault is
  restored to its before state (the note did not exist before the run).
- Server: Obsidian 1.15.1, Local REST API plugin 5.5.2, authenticated true.

## Baseline

- No measured GUI baseline exists for this exact task, so no speedup factor
  is claimed. The held-out case estimates 5 to 10 minutes by GUI against
  about 2 seconds by CLI; the measured CLI path took 0.943s for status plus
  create plus read.

## Setup notes (two real obstacles, both fixed live)

1. The harness binary was gone: the 18/11 verification used /tmp venvs and
   the exam-morning reboot wiped /tmp. Reinstalled persistently with
   `uv tool install cli-anything-obsidian` (1.58s, PyPI 1.1.1, binary now
   in ~/.local/bin on PATH). Plain `pip` does not exist on the laptop.
2. Obsidian was not running, and a bare `obsidian` launch exited silently
   (rc 1, only "Loaded updated app" in the log). With logging on, the cause
   was `Missing X server or $DISPLAY`: Electron defaulted to X11.
   Fixed by launching with `--ozone-platform=wayland` (command-line flag
   only, no config change); port 27124 was listening about 16s after launch.
   The API key was read from the plugin's own data.json into the
   OBSIDIAN_API_KEY env var at runtime; it was never printed or stored.
   Obsidian was stopped with SIGTERM after the run; port 27124 verified
   closed and the desktop shows Jarvis only.

## Attribution (license flag cleared 19/11 08:35)

- Credit added for CLI-Anything by HKUDS (Data Intelligence Lab, University
  of Hong Kong, led by Prof. Chao Huang), https://github.com/HKUDS/CLI-Anything,
  Apache License 2.0, vendored from upstream HEAD 34f5195 on 2026-11-18,
  used with the owner's permission (granted 2026-11-19).
- Files: scripts/cli-anything.py docstring, skill/cli-anything/registry.json
  header credit key, skill/cli-anything/obsidian.md, libreoffice.md, gimp.md
  header comments (repo-added comment block only, vendored bodies untouched),
  docs/cli-anything.md (credit line plus the MIT vs Apache 2.0 open flag
  marked resolved). The Obsidian header also names the harness PyPI package
  author Doruk Ozgen (from the installed package METADATA).
- Verification: registry.json still parses (15 apps), `cli list` works,
  all 8 tests/cli_anything_docs tests pass.
- Commits on origin speed-swarm, ls-remote verified: 2fa4f65 (credit headers,
  5 files), fcbd8b6 (license flag resolution, docs/cli-anything.md).

## Cleanup and state after the run

- Obsidian stopped (SIGTERM to PID 101904), port 27124 closed, desktop clean
  (Jarvis only, verified via hyprctl clients; Zen tabs, Jarvis, music untouched).
- Broker never used, still free. Relay untouched (MainPID 97108 at last check).
- Vault: no .md file changed except the proof note (created then deleted).
- Run dir on the laptop: /tmp/cli-proof-20261119 (run-proof.sh, results.txt,
  step outputs, obsidian logs, attribution.py).
- Log merge: VM live-test-log.md merged into the repo log chronologically
  (merge script improvements/merge-logs-cli-proof.py, backups in /tmp):
  repo 4174 lines, VM 4149 lines, merged 4184 lines (4135 equal, 24 repo-only,
  6 VM-only, 4 replace regions, 4 surplus duplicate lines dropped, 0 lines
  lost, 0 conflict markers, multiset-union verified). Caveat: the merged tail
  keeps 2 pre-existing timestamp inversions from the VM log (08:15 poll 65
  after the 08:20 merge line; 11:31 poll 1 after the 11:32 G1 START line);
  both files kept, order preserved as in the VM source.
- Main stays FROZEN at 21684e7. No merge to main.

## Verdict (PROVISIONAL, non-Astra)

- PROVEN: a real held-out task runs end to end through `computer-use cli run`
  with 0 model calls and byte-exact verification, in under 1 second for the
  task itself. The CLI-Anything path is real, not just wired up.
- Open: no measured GUI baseline for G-01, so the speedup is an estimate
  only; the other 58 held-out cases still have no CLI coverage (plain shell
  meets 5-10x for most); the installed `computer-use` binary is a stale copy
  of the repo (different sha256), so the proof ran the repo checkout directly.
