# B2-1 review log: A8-AST test fix per R9 (compiled artifact)

- Item: B2-1, batch 2, assigned in coord/mochi.md commit f9a1a9f, 18:32 22/11/2026.
- Fix commit: 64c2ade21667c7daa14924266a5fb72f71e22f48, on todolist-push, base ef964a6 (B2-3).
- Fix: 1 file, improvements/y13g-verify/attack_a8_ast.py, 7 insertions, 5 deletions. No code changed.
  - None case expect True -> False (R9 key presence, C2-11), header Amend 5 is-not-None -> R9 wording, tokenizer count 12 -> 14.
  - File md5 after fix: a911977a83bd70df96494c3fe7671c87. sha256: 4ca60adab31219398b030e0e97fa19ed10a54069d683558f2318986146dfffaa.
- Worker: completed 18:39 22/11/2026, worktree /tmp/mochi-b2-1, detached HEAD 9ae216b.
  - Baseline before fix: A8-AST 26/27, rc 1. After fix: A8-AST 27/27, rc 0, three runs.
  - A5 9/10 inside the detached worktree is a proven environment artifact, not a regression: A5-R fails because a worktree .git is a file and launcher_check_driver refuses "is not a git checkout"; run from the real repo the same check gives "no Y6c completion marker" and A5 is 10/10.

## Council 1: PASS

- Caveat: a full clean_ship and A5 rerun inside its fixed-origin clone could not be completed because a runtime safety check stopped it. clean_ship 6/6 had already passed in the worktree.

## Council 2: PASS

- Noted A2 flaked once 10/11 then 11/11 on immediate rerun, unrelated to B2-1.

## Council 3: PASS

## Redteam: KHONG PHA DUOC

- Reverting code to is-not-None reopens C2-11 on both the round-3 and round-2 tests.
- Truth table shows R9 differs from Amend 5 only on None.
- Tokenizer count 14 confirmed from extract_lib.TOKENIZER_FUNCS.

## Independent verifier: PASS, completed 18:47:05 22/11/2026

- Re-ran A8-AST on the fixed bytes: 27/27, rc 0.
- A4-live 5/6 in its run was cross-lane noise: the offender PIDs belonged to a B2-5 council shell whose heredoc contained the runner name.
- The A5 9/10 worktree artifact was independently confirmed by the verifier via a driver run directly on the real repo (10/10).

## Re-measurement on committed bytes (by mochi, 23:12 22/11/2026)

- Applied the worktree diff onto todolist-push HEAD ef964a6, md5 matched a911977a83bd70df96494c3fe7671c87.
- `python3 improvements/y13g-verify/attack_a8_ast.py`: A8-AST DONE 27/27 pass in 1.2s, rc 0. Re-run after push, 23:12:45, still 27/27, 1.3s.
- Push verified by `git ls-remote origin todolist-push`: 64c2ade21667c7daa14924266a5fb72f71e22f48.
- Coord report: commit 0bac4a5 on main, push verified.

## Note on this artifact

- This log compiles the review handoffs received on 2026-11-22 (worker, council 1, council 2, council 3, redteam, independent verifier). The original review subagent sessions did not commit their own artifacts; that gap is what the new rule fixes (see coord/mochi.md, rule from 23:57 22/11/2026: every council/redteam/verifier review must commit an artifact with a hash). This committed log is the verifiable artifact for B2-1; its commit hash is the proof.
- Remaining for B2-1: prepare the full Y13G live run procedure only, no live run without a written GO from Muse tong.
