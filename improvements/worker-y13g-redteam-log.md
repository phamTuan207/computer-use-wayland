# Y13g redteam log: attack the Y13g FIX DIFF (431b2a9..b815590)

Worker Y13g redteam (independent Muse attacker). T0 (task received):
2026-11-22 00:05:34 +07. Scope: ONLY the Y13g fix diff (6 files).
No code modification to the fix files. No live Zen driving. No
ydotool. No em/en dashes. Work only in the repo worktree and
~/workspace/y13g-redteam/ (persistent; /tmp harnesses vanished
overnight). Never touch /usr/lib or any system path (the re.py
incident). Attack shims print a marker ONLY: no deletion, no
os.remove/unlink, no globals().update delegation, no file writes
outside the staged ship copies.

## 1. Live event log

- 00:05:34 +07 (T+0m00s): task received. Redteam the Y13g fix diff.
  Read Y13r2 redteam paper + rereview log + Y13g fix log in full.
  Fix commits: caa4a7c, 0cf43f8, 03303f4, 6cd0f7a, b815590.
  Manifest md5 0ca16ddd743acc9e28294fecd07a9c70, 27 files.
  Runner md5 db3e357f, launcher eec63492, run_live 84fa106c (pin holds).
- 00:10:30 +07 (T+4m56s): diff saved to
  ~/workspace/y13g-redteam/diff-431b2a9-b815590.txt (2015 lines),
  read in full (plan + SHIPPED.md + launcher + regen + runner
  top/verify/proven_no_body/tokenizer). Remote URL verified:
  `git remote get-url origin` returns exactly
  https://github.com/phamTuan207/computer-use-wayland.git, the
  KNOWN_REMOTE_URL in the launcher. Staging the fresh ship next.
