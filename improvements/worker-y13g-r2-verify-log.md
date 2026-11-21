# Independent re-verification log: Y13g ROUND-2 fix diff (R2 verifier)

- Verifier: independent Muse subagent (depth 2). Did NOT write the fix.
- Parent: Worker Y13g (session b58d1a36). Report:
  improvements/worker-y13g-r2-verify-report.md (this log's sibling).
- Repo: ~/workspace/computer-use-wayland, branch todolist-push.
- Scope: ONLY the round-2 diff (commits 0639d04, 87eec47, 6ba43f2,
  8bdd5aa, 5a9b9e8). No fix file edited. No live Zen driving. No
  ydotool. No em/en dashes. Never touched /usr/lib or any system
  path.
- Harnesses: improvements/y13g-r2-verify/ (committed). Staged
  ships + result logs: ~/workspace/y13g-r2-verify/ (persistent,
  never /tmp-only).
- All times wall-clock Asia/Ho_Chi_Minh + elapsed per test.

## 2026-11-22 01:00:42 +07 (T+0m): START, pins verified FIRST

- Branch todolist-push, HEAD 334cf69 at start.
- python3: 3.12.3.
- md5 tests/realistic/run_codex_y5.py = d5047ff573820491263a2eb3805105f4
  (pin d5047ff5 holds).
- md5 tests/realistic/launch_y13.py = 8e72a5ce85cbaf8382f998987e8890e5
  (pin 8e72a5ce holds).
- md5 tests/realistic/codex-y5-manifest.json =
  7c76383402e4c50b28adab6b25a22e09 (pin 7c763834 holds, 27 files).
- run_live.py: manifest records 84fa106c253d5e7f16daccf2ce3f14a5
  (the 1e3901c pin); working-tree file md5 is
  d8e2b14d7456b2866790f4a87ec1919e (91d3cd2 changed HEAD). BY DESIGN:
  the regen script stages run_live.py from `git show
  1e3901c:tests/realistic/run_live.py`, never from the working
  tree (commit 9564304). Verified below: all 27 manifest md5s
  match the working tree except run_live.py, which matches the
  pinned commit bytes instead.
- Round-2 commit scope: each of 0639d04, 87eec47, 6ba43f2, 8bdd5aa,
  5a9b9e8 touches only the 6 fix files (runner, launcher, plan,
  manifest, SHIPPED.md, regen). The wider range also shows
  worker-y13g-fix-log.md from the log commit 6cf7166, which is
  not one of the 5 fix commits.
- Raw tokenizer-block text diff (runner vs launcher, # Y13g B3
  through _is_codex_process): exactly 4 lines, the 2 sync notes.
  The CODEX comment block (Keep in sync with <counterpart>)
  differs only in the counterpart filename. Both checked
  mechanically in the A8/AST battery.

## 2026-11-22 01:0x +07: harness build (T+?m)

- Copied the round-1 harnesses (improvements/y13g-verify/) into
  improvements/y13g-r2-verify/ and adapted them for round 2:
  WORK dir ~/workspace/y13g-r2-verify, manifest pin 7c763834,
  14 tokenizer functions, new R2 cases per battery (see the
  report for the full list). New: attack_a5b.py (remote-URL
  normalization), .so plant compilation in attack_a6d.py from
  the council-2 probe plant_so.c.
- Clean ship staged with the regen script: exit 0,
  {"manifest_ok": true, "files_checked": 27, "mismatches": [],
  "manifest_md5": "7c76383402e4c50b28adab6b25a22e09"}. Regen
  rewrote the manifest file; git shows NO diff (bytes
  identical to committed). Staged run_live.py md5 is
  84fa106c253d5e7f16daccf2ce3f14a5 (the 1e3901c pin); staged
  runner d5047ff5, launcher 8e72a5ce. All 14 harness files
  py_compile OK; sleeper built (gcc -O2).
- Commit: harness + this log start (small commit 1).
