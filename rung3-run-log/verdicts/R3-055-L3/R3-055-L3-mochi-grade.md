# R3-055 (Tier B) grade, scorer 1 mochi, Pair B, R3-L3

- Task: R3-055
- Scorer: mochi, scorer 1, Pair B
- Session ID: 70cd99d1-ecef-4d02-9f42-714d7e86ab85
- Timestamp: 2026-11-26T19:08:00+07:00
- Verdict: PASS
- Snapshot commit: 93ceeb8e4d8a2c50f7fb1015227fb1c85873de43
- Snapshot branch base: todolist-push tip 5d7fcdb0 at verdict time
- Verdict branch: mochi/verdict-R3-055-L3

## Independence declaration

I scored from the frozen key and the snapshot evidence only. I read only the
section "## R3-055 (Tier B)" of docs/rung3-answer-keys.md and the brief
rung3-run-log/briefs/R3-055-scorer-mochi-brief.md. I did not read any other
task key section, did not read scorer 2's verdict, did not read the ledger row
for R3-055, and did not contact the runner. I did not run the task, did not
visit any website, and did not delete or modify the created tree. This is a
Class L score-before-reset task.

## Key hash verification (before scoring)

- docs/rung3-answer-keys.md sha256:
  21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60, match.
- docs/rung3-answer-keys.json sha256:
  5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, match.
- Template sha256 from the key: fe957ba1d6000a272177c12a0e11dd6750cf954021ea23502ec975dfa8cd711b.
  The snapshot report bao-cao.txt reproduces the template text verbatim, and
  the created .gitignore matches that template content exactly.

## Snapshot verification

- Manifest sha256: c679ba432cf3370184f276ead9b48ee87904efba8901abec81d4ebf79f79736c,
  matches the sealed snapshot commit message.
- All 11 snapshot files verified: every per-file sha256 and size in
  manifest.json matches the file in the snapshot. Files: .gitignore, README.md,
  bao-cao.txt, drive-log.txt, end_time.txt, folder-permissions.txt,
  pill-gone.png, pill-visible.png, screenshot-20261126-190021.png,
  start_time.txt, tree-listing.txt.
- Run window: start 2026-11-26T18:55:43+07:00, end 2026-11-26T19:02:23+07:00.

## Rubric checks

1. Folder structure, 8 folders, exact names and places: PASS.
   Root /home/james/rung3/d06-du-an-moi (runner home, so ~/rung3/d06-du-an-moi)
   holds level 1 Tai-lieu, Ma-nguon, Kiem-thu, Du-lieu, Cong-cu, and level 2
   Ma-nguon/thu-vien, Ma-nguon/ung-dung, Kiem-thu/kiem-thu-don-vi. The tree
   listing shows all 8 folders, no extra folder, no missing folder.
2. README.md, 3 items: PASS. Project name "# d06-du-an-moi", creation date
   2026-11-26, folder list with all 8 folders.
3. .gitignore, exact template content: PASS. Exactly three lines:
   __pycache__/, *.pyc, .venv/, 26 bytes.
4. Permissions: PASS. Tai-lieu is dr-xr-xr-x (mode 555, read-only). Root and
   all other 7 folders are drwxr-xr-x (mode 755, read-write). Shown both in
   folder-permissions.txt (ls -ldn) and in the screenshot.
5. Screenshot in window: PASS. screenshot-20261126-190021.png, taken 19:00:21,
   inside the run window, shows the terminal with the full project tree and
   the permission listing. pill-visible.png shows the active control pill
   during the session, pill-gone.png shows no pill after the session ended.

## INVALID consideration

The evidence is complete and judgeable on every rubric item, so no INVALID
condition applies. The infrastructure re-run path was considered, as required
from epoch 23, and was not needed: nothing in the evidence is missing,
unreadable, or ambiguous.

## Verdict

PASS. Every rubric item is met by the snapshot evidence, with hashes verified
before scoring.
