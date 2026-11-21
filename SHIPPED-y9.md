# Y9 ship manifest (frozen at ship time, 2026-11-21)

- Ship commit (todolist-push): a82bb4188a133c5c3507c8647393b42f4b48dd24
- Shipped from: /home/hatch/workspace/computer-use-wayland
- Note: run_live.py is shipped from the WORKING TREE at ship time
  (uncommitted Y4d revisions, HEAD a82bb41). This frozen copy is
  what runs; later VM edits do not affect the run. run_agyq2.py is
  NOT shipped: run_agy_y2.py is self-contained except for the
  run_live import.

## Files (path in /tmp/worker-y9-server, md5, source)

- run_live.py, 84fa106c253d5e7f16daccf2ce3f14a5, working tree (dirty)
- run_agy_y2.py, 1defa4ebf184c7e52df9604e75cd7f4b, commit
- agy-y2/README.md, 6e6677e80acf4185b9fc4edc00075958, commit 30a72e5
- agy-y2/check-dashes.py, a70faed01522b9be5070f4cc543b98a7, commit 30a72e5
- agy-y2/check.mjs, abb75b01807758933becd999871f2fbb, commit 30a72e5
- agy-y2/fixtures/test-01-tmux-session.html, d7a7b296b236057227df891a3262bc87, commit 30a72e5
- agy-y2/fixtures/test-02-network-settings.html, c167f6523ecfc31eb9278943468b9f89, commit 30a72e5
- agy-y2/fixtures/test-03-photo-editor.html, e9ac042c657cf66eb37a857a43f9fb7f, commit 30a72e5
- agy-y2/fixtures/test-04-email-compose.html, 7dbee8181518b9747f38cb8008aae53c, commit 30a72e5
- agy-y2/fixtures/test-05-spreadsheet-chart.html, 486508fd359f2d47079c7722a703043d, commit 30a72e5
- agy-y2/fixtures/test-06-video-call.html, 1f02764f86e8c8545d38c0e8387759d6, commit 30a72e5
- agy-y2/fixtures/test-07-file-manager.html, 8fb5b686e27050e36d79bdf7a4493cf0, commit 30a72e5
- agy-y2/fixtures/test-08-devtools.html, 991d85aa560524b5d927567d23ba14d4, commit 30a72e5
- agy-y2/fixtures/test-09-notes-sync.html, c96f2c308252736990e60803367e6343, commit 30a72e5
- agy-y2/fixtures/test-10-ide-debug.html, 08d9cabcad50853d04e026b4f42468a1, commit 30a72e5
- agy-y2/simulate.mjs, 0643d9a5babcc5b2e3d284bb16e10b33, commit 30a72e5
- agy-y2/test-01-tmux-session.md, 1ffef261c0b126ac36c50f2c782756f3, commit 30a72e5
- agy-y2/test-02-network-settings.md, 55d669ef8e6eebbeddba3634c350b36b, commit 30a72e5
- agy-y2/test-03-photo-editor.md, 8f901137e49ee3887277aba8b9919f42, commit 30a72e5
- agy-y2/test-04-email-compose.md, aae817fc492693cf6ffb3bdd3f669d7a, commit 30a72e5
- agy-y2/test-05-spreadsheet-chart.md, e366d4f601a2e01b145877c6076f41c7, commit 30a72e5
- agy-y2/test-06-video-call.md, c2e5b1f3735a148bf604de682b8e6c0e, commit 30a72e5
- agy-y2/test-07-file-manager.md, 9f63ac6cd289fabb279b411ab1896faf, commit 30a72e5
- agy-y2/test-08-devtools.md, bdf0bf8f08cf0f8e43005a2ec68fa3c7, commit 30a72e5
- agy-y2/test-09-notes-sync.md, ec2faabd507e612646bfff551f68143c, commit 30a72e5
- agy-y2/test-10-ide-debug.md, f9b3be84606468007862f2c19d72d23b, commit 30a72e5

## Launch (from the shipped dir, detached, one SSH call)

cd /tmp/worker-y9-server && LIVE_SERVER_ROOT=/tmp/worker-y9-server LIVE_SERVER_PORT=8769 LIVE_LOG=/tmp/worker-y9-live.jsonl WD_PORT=4449 LIVE_OWNER_AWAY=1 flock -w 60 ~/.cache/agent-computer-use/zen_dom.lock -c "python3 run_agy_y2.py all > /tmp/worker-y9-stdout.log 2>&1"

## Notes

- The handover token /tmp/worker-y9-handover.json is written by the
  launcher at launch time, NOT shipped.
- Fixture URLs are http://127.0.0.1:8769/agy-y2/fixtures/test-XX-....html
- Geckodriver logs per test: /tmp/worker-y9-gecko-{test}-a{attempt}.log
- Screenshots: /tmp/worker-y9-shots/{test}-a{attempt}.png
