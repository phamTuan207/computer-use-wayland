# R3-055 scorer 2 grade (Pair B, R3-L3, Class L)

scorer session ID: clone2-main-ad85548c-ced4-4f31-afdb-d1043dcabbd7
task ID: R3-055
verdict: PASS
timestamp: 2026-11-26 19:06 +07 (Asia/Ho_Chi_Minh)
key file hash: docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8; docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both verified against the brief's frozen hashes before scoring)
reason: tree-listing.txt and the in-window terminal screenshot show exactly the 8 required folders with exact names in the right places under ~/rung3/d06-du-an-moi, README.md holds all 3 required items, .gitignore matches the template content exactly, and the permissions listings show Tai-lieu read-only (dr-xr-xr-x) with every other folder read-write (drwxr-xr-x).

## Key section used

docs/rung3-answer-keys.md, "## R3-055 (Tier B)", lines 453-460: template ~/rung3/d06-template.txt (sha256 fe957ba1d6000a272177c12a0e11dd6750cf954021ea23502ec975dfa8cd711b); root ~/rung3/d06-du-an-moi with 5 level-1 folders (Tai-lieu, Ma-nguon, Kiem-thu, Du-lieu, Cong-cu) and 3 level-2 folders (Ma-nguon/thu-vien, Ma-nguon/ung-dung, Kiem-thu/kiem-thu-don-vi); README.md at the root with project name, creation date and folder list; .gitignore exactly __pycache__/, *.pyc, .venv/; Tai-lieu read-only, all other folders read-write. Rubric per the brief: 8 folders exact names and places, README 3 items, .gitignore exact, Tai-lieu read-only, others not read-only, screenshot in window.

## Snapshot verification

- Snapshot: rung3-run-log/rung3-snapshots/R3-055-L3/
- Manifest hash (manifest_sha256 field in manifest.json): c679ba432cf3370184f276ead9b48ee87904efba8901abec81d4ebf79f79736c (matches the dispatch notice)
- Per-file sha256 verification against manifest.json (recomputed, hash and size): all 11 evidence files OK
  - .gitignore 4cad133d4f0a6cf4bba15f1b8bbae48d6a55f20b94f75487c51a93cc6a5af59f OK
  - README.md 3a66200783a8fc31a21326b587f93d32323ed4516b86332a58a2c51b71b4686c OK
  - bao-cao.txt 4aca5edbbc71cf36d5b0cb5a4103b8303ca8a2985582846f938bb6c5c182a26d OK
  - drive-log.txt a1578dc6322f46d52db7a2a622ab72041a21a7cedd5b0dee8f5e40305c5f4ba0 OK
  - end_time.txt 55e0da9070aabcc40d6a5f915fb15d80fc5babd25ef44111cee538b122a72db6 OK
  - folder-permissions.txt 3fe45cda4820599fbbabde336cd104a50d3ad5da76f9435228799b263e64fcc0 OK
  - pill-gone.png ed906a70f64386aff38ee1856b33663d7479ed2f85899efb7232885555993593 OK
  - pill-visible.png ae88e57244fea8916d866a30126a5d2c5327e8c296f7797b4124d82a78af3b35 OK
  - screenshot-20261126-190021.png 02672a73bb2457d82045f156f64172de2cc559a6bfda6813a97e4547b4bbdf73 OK
  - start_time.txt ef45086c716264c3c3a9d9acf663f6e70ed2984bbabcca498d309403053c7498 OK
  - tree-listing.txt 8fe1d0d3c6b3ae3769433dad22ca5546b68e909196c13f29a7872e95386f65be OK
- No files in the snapshot dir beyond the manifest list plus manifest.json itself.
- Run window: start_time.txt 2026-11-26T18:55:43+07:00, end_time.txt 2026-11-26T19:02:23+07:00, inside the 30 minute task limit. The screenshot filename timestamp 20261126-190021 (19:00:21) falls inside the window.

## Files read

- rung3-run-log/briefs/R3-055-scorer-clone2-brief.md
- docs/rung3-answer-keys.md (sha256 verification; key section lines 453-460 only)
- docs/rung3-answer-keys.json (sha256 verification only)
- rung3-run-log/rung3-snapshots/R3-055-L3/manifest.json
- rung3-run-log/rung3-snapshots/R3-055-L3/tree-listing.txt
- rung3-run-log/rung3-snapshots/R3-055-L3/folder-permissions.txt
- rung3-run-log/rung3-snapshots/R3-055-L3/README.md
- rung3-run-log/rung3-snapshots/R3-055-L3/.gitignore
- rung3-run-log/rung3-snapshots/R3-055-L3/screenshot-20261126-190021.png
- rung3-run-log/rung3-snapshots/R3-055-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-055-L3/end_time.txt

The remaining snapshot files (bao-cao.txt, drive-log.txt, pill-visible.png, pill-gone.png) were hash-verified against the manifest but not read for grading: the brief directs grading from the tree listing, the permissions listing, the README and .gitignore copies, and the screenshot.

## Independence declaration

I graded independently from the snapshot and key section only; I did not read scorer 1's verdict or contact the runner.

## Reasons

- Folder structure (tree-listing.txt): under /home/james/rung3/d06-du-an-moi the listing shows exactly the 5 level-1 folders Tai-lieu, Ma-nguon, Kiem-thu, Du-lieu, Cong-cu and the 3 level-2 folders Ma-nguon/thu-vien, Ma-nguon/ung-dung, Kiem-thu/kiem-thu-don-vi, all with the key's exact names in the right places, plus README.md and .gitignore at the root. No extra folders appear.
- Permissions (folder-permissions.txt, agreeing with the permission strings in tree-listing.txt): Tai-lieu is dr-xr-xr-x, no write bit for owner, group or others, so read-only as required. The root and every other folder (Cong-cu, Du-lieu, Kiem-thu, Kiem-thu/kiem-thu-don-vi, Ma-nguon, Ma-nguon/thu-vien, Ma-nguon/ung-dung) are drwxr-xr-x, owner read-write, so not read-only as required.
- README.md: holds all 3 required items: project name (title "# d06-du-an-moi"), creation date ("Creation date: 2026-11-26", the run date), and a folder list naming all 8 folders including the level-2 paths.
- .gitignore: content is exactly the 3 template lines __pycache__/, *.pyc, .venv/, nothing added and nothing missing.
- Screenshot (screenshot-20261126-190021.png, 19:00:21, inside the run window): the terminal shows the find tree output with the same 8 folder paths and the ls -ldn permissions output identical to folder-permissions.txt, including Tai-lieu at dr-xr-xr-x, corroborating both saved listings.
- Rubric check: 8 folders exact names and places, README 3 items, .gitignore exact, Tai-lieu read-only, others not read-only, screenshot in window. Every rubric item is met, and the evidence was complete and judgeable, so the invalid case does not arise.
