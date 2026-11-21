# Y13 codex-y5 live ship (frozen)

Runner: tests/realistic/run_codex_y5.py (Worker Y13, 21/11/2026).
Base: run_live.py from commit 1e3901c ONLY, md5 84fa106c253d5e7f16daccf2ce3f14a5
(Y4d live-proven base; ONE 10/10 live run on these bytes, run 2; run 1 was 8/10).
NOT HEAD: HEAD's run_live.py changed in 91d3cd2 (Y11 live-metrics, +415/-66),
unit-verified only. live_metrics.py must be ABSENT from the ship dir.

Launcher: tests/realistic/launch_y13.py (council A F4 + redteam H5,
Y13f H3 re-review fix). It performs the launch-time checks (go order
asserted, Y6c marker check with --repo REQUIRED, ship manifest md5
vs the committed manifest, handover token fresh, runner-quiet
process check, predecessor + own ports free, no live geckodriver
with a live parent) and then execs the runner under flock -w 60.
Launch ONLY via the launcher, never directly. The marker check
matches subjects only (never --grep), rejects "harness" subjects,
and requires the newest completion to be newer than the newest
abort. The ship is re-staged from the committed bytes with:
  python3 tests/realistic/regen_codex_y5_manifest.py --stage /tmp/worker-y13-server
(Regenerate the manifest LAST, after every runner edit; the
launcher refuses a ship whose manifest md5 differs from the
committed manifest.)

Ship dir (laptop): /tmp/worker-y13-server
Ports: server 8771, WD 4452, Marionette 2828 (shared, connect-existing).
Handover token: /tmp/worker-y13-handover.json (written by the launcher at run start).
JSONL: /tmp/worker-y13-live.jsonl. Shots: /tmp/worker-y13-shots/.
Gecko log: /tmp/geckodriver-4452.log (copied per test).

Launch (on the laptop, from /tmp/worker-y13-server, ONLY after the
Y6c completion marker + Muse's go order + the launch-time checks pass):
  cd /tmp/worker-y13-server && Y13_GO=1 python3 launch_y13.py \
    --repo /home/james/workspace/computer-use-wayland all \
  > /tmp/worker-y13-stdout.log 2>&1

Manifest: codex-y5-manifest.json, md5 f27c03020c9866cfa0dcd637df6f8647, 27 files.
Files (path, md5):

- run_codex_y5.py 3cc5fa11a4be533c1bb49941008bfa75
- launch_y13.py 2b02c5ec85ef474bfcddf4b59dcacc0f
- run_live.py 84fa106c253d5e7f16daccf2ce3f14a5
- codex-y5/test-01-git-workflow.md 0f347247c21b2f1375596c1ee51449b4
- codex-y5/test-02-music-player.md 15925f6709c62908dfd5cd88f1fc8c91
- codex-y5/test-03-password-vault.md e931e09bee8d28ca64768f5bc2053f40
- codex-y5/test-04-maps-directions.md 0d59678a646493d17fc8b2efdf518cc3
- codex-y5/test-05-calendar-recurring.md 71cbaa55642161c97d7fc98e9221e72b
- codex-y5/test-06-video-editor.md 842783b7278cf8bb5bc7b1b40d1516cb
- codex-y5/test-07-chat-search.md 3b0c37be71f023d8be148a1c99805971
- codex-y5/test-08-spreadsheet-pivot.md d50ffaee6f2261108551279416c5cd1b
- codex-y5/test-09-file-search-tag.md cae2f8e3afb0c476590e7d6ba5ecfe68
- codex-y5/test-10-extension-settings.md ed5f2b35862784b6b02eafbb185691c7
- codex-y5/simulate.mjs b6c7c9c9c09a0da452c1996a8c43504d
- codex-y5/check.mjs 56312f93fcf8f13eae9b4fabe85d172d
- codex-y5/README.md 217c3edceb42a040f2f601fdddbcdf6a
- codex-y5/check-dashes.py d4e7659f4e6b77dc351c6e7319ed4e61
- codex-y5/fixtures/test-01-git-workflow.html ac0f3f5f6510bbd9c5ccf32e2b2f8301
- codex-y5/fixtures/test-02-music-player.html 0b988fde53e221f6522b6d8965f92113
- codex-y5/fixtures/test-03-password-vault.html 21ecdc2bb9b2ae34fdd1b7ca48e60a80
- codex-y5/fixtures/test-04-maps-directions.html ea6f1365c4d57f030d58e6913f39ac28
- codex-y5/fixtures/test-05-calendar-recurring.html caf9d8acd2440028b135d005ed42a4f2
- codex-y5/fixtures/test-06-video-editor.html 6cd220edc51a1c69c97ae6fcb87d5bb4
- codex-y5/fixtures/test-07-chat-search.html 45a8077d703ee5481092ec316ce26d83
- codex-y5/fixtures/test-08-spreadsheet-pivot.html af10ca0627a72dc8eb8890c0ea3d635d
- codex-y5/fixtures/test-09-file-search-tag.html 16507889dd0cb236339cc11fe6b80f7e
- codex-y5/fixtures/test-10-extension-settings.html 21b2aacee36e9bc3dd7a61dbaba25123

Queue: Y13 runs AFTER Y6c (Wayland-nested) reports completion AND Muse says go.
Y6c ended NO VERDICT (commit 5a2b69d, BLOCKED at launch); Y6d rebuilt the
plugin + launcher (commit 72eb8ad) and Y6e is risk-checking it. The H3 gate
as written matches ^Y6c subjects only, so a Y6d/Y6e commit does NOT satisfy
it; the gate refuses until a fresh Y6c-pattern marker lands or Muse directs
otherwise. Do NOT weaken the gate. Y14 (batch-3 live) queues AFTER Y13.
Y13 completion marker for Y14:
a todolist-push commit matching ^Y13 codex-y5: .*live complete, plus the
log line 'Y13 codex-y5 live complete: <clean>/<flagged>/<total>'.
