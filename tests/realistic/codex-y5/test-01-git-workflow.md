# test-01-git-workflow.md

## Test ID
test-01-git-workflow

## Topic
Git terminal workflow with branch creation, commits, a merge conflict, recovery, resolution, and log verification.

## Context
A developer is preparing a configuration change in the local Git Workbench fixture. They must enter Git commands in its terminal, branch from main, commit a config change, make a conflicting change on main, merge main into the feature branch, recover from choosing the wrong side of the conflict, resolve the file, and verify status and history. The fixture is tests/realistic/codex-y5/fixtures/test-01-git-workflow.html.

## Timing
- Baseline start time: 2026-11-21 18:21:00 Asia/Ho_Chi_Minh
- Expected duration: 240 seconds elapsed
- Maximum allowable latency: 360 seconds elapsed

## Goal
Finish on feature/cleanup with a clean worktree, four commits, no unresolved conflicts, and config.txt containing mode=preview and log=compact.

## Exact steps
1. Open tests/realistic/codex-y5/fixtures/test-01-git-workflow.html in the browser.
2. Verify #current-branch text is "main", #worktree-status text is "Clean", #commit-count text is "1", #conflict-count text is "0", and #terminal-output text is "Ready on branch main".
3. Type "git switch -c feature/cleanup" into #terminal-command-input and click #btn-run-git-command; #current-branch must become "feature/cleanup".
4. Verify #terminal-output text is "Switched to a new branch 'feature/cleanup'" and #branch-list text is exactly "main\nfeature/cleanup".
5. Replace #file-config-editor value with "mode=preview\nlog=verbose"; its value must match exactly.
6. Verify #worktree-status text is "Modified: config.txt" and #file-config-editor value is "mode=preview\nlog=verbose".
7. Type "git add config.txt" into #terminal-command-input and click #btn-run-git-command; #staged-count must become "1".
8. Verify #terminal-output text is "staged config.txt" and #staged-count text is "1".
9. Type "git commit -m \"Add preview mode\"" into #terminal-command-input and click #btn-run-git-command; #latest-commit must become "Add preview mode".
10. Verify #terminal-output text is "committed: Add preview mode", #commit-count text is "2", and #worktree-status text is "Clean".
11. Type "git switch main" into #terminal-command-input and click #btn-run-git-command; #current-branch must become "main".
12. Verify #terminal-output text is "Switched to branch main" and #file-config-editor value is "mode=stable\nlog=verbose".
13. Replace #file-config-editor value with "mode=stable\nlog=compact"; its value must match exactly.
14. Verify #worktree-status text is "Modified: config.txt".
15. Type "git add config.txt" into #terminal-command-input and click #btn-run-git-command; #staged-count must become "1".
16. Verify #terminal-output text is "staged config.txt" and #staged-count text is "1".
17. Type "git commit -m \"Use compact logs\"" into #terminal-command-input and click #btn-run-git-command; #latest-commit must become "Use compact logs".
18. Verify #terminal-output text is "committed: Use compact logs", #commit-count text is "3", and #worktree-status text is "Clean".
19. Type "git switch feature/cleanup" into #terminal-command-input and click #btn-run-git-command; #current-branch must become "feature/cleanup".
20. Verify #terminal-output text is "Switched to branch feature/cleanup" and #file-config-editor value is "mode=preview\nlog=verbose".
21. Type "git merge main" into #terminal-command-input and click #btn-run-git-command; #merge-status must become "Conflict in config.txt".
22. Verify #terminal-output text is exactly "Auto-merging config.txt\nCONFLICT in config.txt", #conflict-count text is "1", and #merge-status text is "Conflict in config.txt".
23. Mistake: click button #btn-use-incoming and accept main's conflicting version; #file-config-editor value must become "mode=stable\nlog=compact".
24. Verify #merge-status text is "Resolved with incoming version" and #conflict-count text is "0".
25. Recovery: click button #btn-undo-conflict-resolution; #merge-status must return to "Conflict in config.txt".
26. Verify #conflict-count text is "1" and #conflict-markers text is exactly "<<<<<<< feature/cleanup\nmode=preview\n=======\nmode=stable\n>>>>>>> main".
27. Click button #btn-use-ours to keep the feature mode and main log setting; #file-config-editor value must become "mode=preview\nlog=compact".
28. Verify #merge-status text is "Conflict resolved", #conflict-count text is "0", and #staged-count text is "1".
29. Type "git commit -m \"Merge main after resolving config\"" into #terminal-command-input and click #btn-run-git-command; #latest-commit must become "Merge main after resolving config".
30. Verify #terminal-output text is "committed: Merge main after resolving config", #commit-count text is "4", #worktree-status text is "Clean", and #file-config-editor value is "mode=preview\nlog=compact".
31. Type "git status --short" into #terminal-command-input and click #btn-run-git-command; #terminal-output must become "working tree clean on feature/cleanup".
32. Verify #terminal-output text is exactly "working tree clean on feature/cleanup".
33. Type "git log --oneline" into #terminal-command-input and click #btn-run-git-command; #terminal-output must become exactly "4 Merge main after resolving config\n3 Use compact logs\n2 Add preview mode\n1 Initial commit".
34. Verify #terminal-output text is exactly "4 Merge main after resolving config\n3 Use compact logs\n2 Add preview mode\n1 Initial commit", #git-log-list text is exactly "Merge main after resolving config\nUse compact logs\nAdd preview mode\nInitial commit", #current-branch text is "feature/cleanup", and #conflict-count text is "0".

## Pass/fail criteria
- Pass: The final branch is feature/cleanup, config.txt contains mode=preview and log=compact, the worktree is clean, four commits are recorded, the conflict is resolved, and terminal status and history match exactly.
- Fail: The feature branch is missing, the wrong config survives, recovery does not restore the conflict, the worktree is dirty, or any expected commit is missing.

## Errors designed to expose
- click miss: The terminal command field, run control, branch controls, and conflict buttons are close together.
- slow think: The workflow alternates branches and requires a commit on each side before merging.
- stale observation: Conflict count changes after both resolution and undo.
- wrong diagnosis: Accepting the incoming version appears successful but loses the intended feature mode.
- fabrication: The final status, config value, and four-line terminal log are exact DOM checks.

## Checker / expected end state
```bash
node tests/realistic/codex-y5/check.mjs --fixture tests/realistic/codex-y5/fixtures/test-01-git-workflow.html --test 01
```
