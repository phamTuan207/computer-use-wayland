# Vault-move proof: Obsidian backlinks, API move vs plain mv

- Date: 2026-11-19, work 13:07 to 13:22 Asia/Ho_Chi_Minh. Worker: Luna 6 Max.
- Laptop: user@192.0.2.1 (Omarchy/Hyprland). Repo ~/computer-use-wayland,
  branch speed-swarm, HEAD 464df02 at proof time (report correction commit).
- Vault: ~/the owner's second brain (101 .md files, alwaysUpdateLinks true).
- Task: move an Obsidian note to a new location and prove the backlink in the
  linking note is updated; then show plain shell mv leaves the link broken.
- No broker session, 0 model calls, 0 observations in any run. Every CLI step
  went through the repo checkout (python3 scripts/cu.py cli run, HEAD 464df02).

## Finding 1: the briefed `vault move` command does NOT exist

- Installed cli-anything-obsidian 1.1.1 is the PyPI latest (verified 19/11).
  Its vault group offers append, create, delete, list, read, update only.
  No move or rename appears in the skill doc, the registry, or cli-anything.py.
- Attempt: `computer-use cli run obsidian -- vault move "CU-Proof-B.md"
  "998- Unsorted/CU-Proof-B.md"` failed, returncode 2, 0.317s:
  "Error: No such command 'move'."
- Fallback used, and documented as a deviation: the underlying Local REST API
  itself. The installed plugin (Local REST API 5.5.2, main.js) exposes HTTP
  MOVE on /vault/{path} with a Destination header; its moveVaultFile calls
  app.fileManager.renameFile, the link-updating rename. That is the exact API
  the CLI wraps, same server, same auth, same rename path.
- Open follow-up: add a `vault move` subcommand to the harness so the briefed
  CLI command exists.

## Finding 2: the API move DOES update backlinks (when the link needs it)

- Pure rename, test 4: G linked [[CU-Proof-H]] (sha 4b3d3c96). REST MOVE H to
  H2, HTTP 204 in 0.018s. G became [[CU-Proof-H2]] (sha 89cc869f), checked at
  +15s and +45s. H2 exists, H gone, H content byte-exact.
- Pathed folder move, test 5b: F in 998- Unsorted, E linked
  [[998- Unsorted/CU-Proof-F]] (sha 7cddb318). REST MOVE F to root, HTTP 204
  in 0.023s. E became [[CU-Proof-F]] (sha 3e5a95b8). F at root, byte-exact.
- Folder moves with bare links, runs 1-3: A/E/G stayed [[CU-Proof-B/F/H]]
  byte-identical at +3s/+15s/+60s. That is CORRECT, not a failure: bare
  [[name]] links resolve by filename under shortest-path links, so a
  folder-only move needs no rewrite. The discriminating cases are renames
  and pathed links, both proven above.
- Moved-note content was byte-exact in every run (sha256 unchanged).

## Finding 3: plain mv breaks links (shell-only failure mode)

- Rename via mv, test 5a: C linked [[CU-Proof-D]], mv D to D2 in 0.001s.
  C stayed [[CU-Proof-D]] (sha 456864ef unchanged). No file named
  CU-Proof-D.md remains anywhere, so the link is broken.
- Pathed folder move via mv, test 5c: I linked [[998- Unsorted/CU-Proof-J]],
  mv J to root in 0.002s. I stayed [[998- Unsorted/CU-Proof-J]] (sha
  cd464826 unchanged). Nothing remains at the old path, so the link is broken.
- Run 1 folder move via mv showed the same no-rewrite behavior (C stayed
  [[CU-Proof-D]]); its link was a bare one, so it still resolves by name.
  The rename and pathed cases above are the true breakage demonstrations.
- mv changed no file bytes anywhere; the failure is the link, not content.

## Verdict (PROVISIONAL, non-Astra)

- PROVEN: the vault move DOES qualify under the last-resort rule. Only the
  Obsidian API updates backlinks; plain mv leaves them broken; there is no
  file-based approach that preserves links. The G-01 correction stands (note
  creation is shell work, not a CLI win); the move is the case that needs
  the API. Caveat: the move went through the REST API directly because the
  harness has no `vault move` subcommand yet (finding 1).
- Open: no measured GUI baseline for the move, so no speedup factor is
  claimed; add `vault move` to the harness.

## Wall times (WALL TIME is the headline number)

- REST MOVE call: 0.008s, 0.014s, 0.018s, 0.023s across the four moves.
- CLI calls (server status, vault create/read/delete, note open): 0.306s
  to 0.392s each, typically about 0.31s.
- Plain mv: 0.001s (rename), 0.002s (folder move).
- Full create plus move plus verify cycle, run 1: 4.296s.
- Whole run scripts: run 1 9.228s, retry 76.967s, test 3 136.308s,
  test 4 76.354s, test 5 69.926s (tests 2-5 walls are mostly settle sleeps
  of 15s to 60s, not work).
- The API move call itself is effectively instant; the honest headline is
  the 0.008 to 0.023s MOVE call plus about 0.31s per CLI call around it.

## Setup notes

- Obsidian was not running. Launched with --ozone-platform=wayland (bare
  launch exits silently with Missing X server/$DISPLAY, Electron defaults
  to X11). Port 27124 up 2s after launch. Server status OK (Obsidian 1.15.1,
  Local REST API 5.5.2, authenticated true).
- API key read from the plugin data.json into OBSIDIAN_API_KEY at runtime,
  never printed or stored. Run scripts contain no key material.
- Test 3 pure-rename step failed on my own URL-encoding bug (curl rc 3,
  unencoded space in the source URL); fixed in test 4 with 998-%20Unsorted.
- Cleanup: all test notes deleted through the CLI (A/B/C/D/E/F/G/H/H2/I/J),
  0 CU-Proof files remain, vault restored. Obsidian stopped with SIGTERM
  (PID 140303), port 27124 verified closed, no obsidian process left.
  Desktop clean (Jarvis only, verified via hyprctl clients; Zen was not
  running at check time, untouched). Broker free (state finished, driver
  stopped, guardian clean, next_sequence 4). Relay untouched.
- Run dir on the laptop: /tmp/cli-vault-move-20261119/ (run-proof.sh,
  run-proof2.sh, run-proof3.sh, run-proof4.sh, run-proof5.sh, results.txt,
  results2.txt, results3.txt, results4.txt, results5.txt, step outputs,
  obsidian.log, this summary).
- Commits on origin speed-swarm: 464df02 (G-01 correction, 13:06, pushed
  before the proof). This summary plus the report update land as the next
  commit. Main stays FROZEN.
