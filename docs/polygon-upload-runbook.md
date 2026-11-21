# Polygon / Codeforces upload runbook

Source: the full workflow file (QUY-TRINH-UP-DE-POLYGON-CODEFORCES-2026-11-20.md,
written 20/11/2026 after reading all of Hieu's messages and video) plus the
errors actually hit on 20-21/11/2026 (LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md,
parts B and C). Rule: only what Hieu said or did in the video. Where Hieu
said nothing, it says CHUA RO. Never invent a step.

Run `scripts/polygon_checks.py` on the problem directory before every
commit and before adding to Codeforces. It catches B1, B2, B3, B4, B6,
B7, B8, B12, B13 offline.

## 0. Browser and session (B10, B11)

- Use ZEN BROWSER ONLY, in the already-logged-in Polygon tab. Never
  open Chromium (a fresh browser with no login) and never open a new
  tab for the task.
- NEVER type a URL with per-character key events (B11). The `:` and
  `/` keys do not survive key-event typing and the session dies. Use
  the already-open tab, or navigate by clicking links.
- NEVER press Ctrl+T in Zen: it opens a new window (Ctrl+N is the new
  tab). The driver refuses Ctrl+T into a Zen window (C3).

## 1. Create the problem, set limits

- polygon.codeforces.com, create a new problem.
- General Info tab: Input file = stdin, Output file = stdout, limits
  per the problem (Bubble Sort / Easy Problem: 1000 ms, 256 MB;
  Keo Con: 5 s, 256 MB). Save.
- NEVER click the "Add to Contest" link in General Info. Hieu never
  clicked it in the video. It is NOT the way into Codeforces.

## 2. Statement: language ENGLISH, content Vietnamese (B7)

- Statement language MUST be english. Hieu, DM 20/11 20:51: "de
  statement la english giup toi nha. Dung de la vietnamese, luc hien
  thi tren codeforces cthe bi loi a."
- Content stays Vietnamese (from De bai.docx, converted to LaTeX).
  Preview, check rendering, Save.
- If BOTH an english and a vietnamese statement exist, DELETE the
  vietnamese one and keep only english.
- LaTeX math must be closed (B8): every `$` needs its closing `$`.
  `"$5 + 9 + 10 = 24."` (missing the closing `$`) fails Preview with
  "Unclosed math text". The validator checks `$` balance.

## 3. Checker: std::lcmp.cpp

- Checker tab: pick the standard checker std::lcmp.cpp.

## 4. Tests: import the input-only zip (B3, B4, B9, B12, B13)

- Open the test zip in Drive first and check its contents.
- The zip must contain INPUTS ONLY (B12). A zip with inputs AND
  answers imports double the tests (56 instead of 30): Polygon
  generates answers itself by running the Main solution.
- The Browse button (B9): clicking its exact centre does NOT open
  the file picker. Move the mouse OFF-CENTER (left/right a little)
  until the button darkens (hover state), then click at the same
  off-center point. Use the `hover_click` DOM action; it moves off
  the control, waits for `:hover` plus a visual-style change, then
  clicks. Applies to every Browse/file picker on Polygon.
- "Set test example": mark the sample tests as Example,
  "Use in statements: Yes". Samples are tests 01 and 02.
- Tick "Enable points". Points go on HIDDEN tests ONLY (B2 points
  scheme, Hieu 20/11 10:01-10:02): recognition 15/test, comprehension
  10/test, application 5/test, VDC 5/test. Samples get 0 points.
- After import, CHECK THE COUNT AT ONCE (B13): it must be exactly
  the expected number (30 for these problems). If one is missing
  (problem 2 imported 29, file 03 missing), add it by hand with the
  exact original bytes.

## 5. Solution: upload a .cpp file, code still C (B1)

- Solution files tab: upload a file with the `.cpp` extension.
  The code inside stays C. Language MUST be
  cpp.gcc14-64-msys2-g++23. Type MUST be "Main correct solution".
- Typing code directly into Polygon's editor does NOT work. Use Add
  Files to upload the file.

## 6. Commit, first time (C4)

- The Commit Changes link is at the END OF THE RIGHT COLUMN, under
  the panel listing ADDED changes (C4). Press End on any problem page
  to get there.
- Read the warnings, press "Commit". The message may be empty.
  Revision becomes 1/1.
- Common warnings: "No tags", "use hyphen '-' instead of dash '--'",
  "No validator", "Manual tests with indices ... are equal" (that
  last one means duplicate tests, step 7).

## 7. Delete duplicate tests, RENUMBER 1..N, commit again (B3, B4)

- Delete the tests the commit warnings flagged as equal. Confirm
  the "Are you sure you want to delete N test(s)?" dialog.
- AFTER DELETING, RENUMBER THE TESTS TO 1..N CONTINUOUSLY (B4).
  Leftover gaps make Polygon report "Testset 'tests' has invalid
  tests numeration" and "Package can not be built". That BLOCKS
  packaging; it is not a warning to ignore.
- Commit again. Revision becomes 2/2 (or 3/3).

## 8. Create a NEW package for the NEWEST revision (B5)

- Packages tab: "Create package: Standard / Full", tick "Verify".
- A NEW package is REQUIRED for each new revision. Codeforces reads
  the package, not the revision. Committing to Rev 2 while keeping
  the Rev 1 package leaves Codeforces seeing the old version.

## 9. If tests still fail: fix, commit again

- Check the statement Preview: the Example block must render from
  the sample tests.
- Fix the tests, commit again (Revision 3/3 in the video).

## 10. Access (Hieu WRITE, codeforces READ)

- Manage Access, Add user `hieutrancong`, change Read to Write.
- Manage Access, Add user `codeforces`, keep Read. Codeforces needs
  at least READ or it cannot read the problem.

## 11. To Codeforces: Add Problems with the HASH link (B6, B2)

- Open the contest, open Add Problems
  (`/group/<group>/contest/<id>/problems/new`).
- Paste the Polygon link and press "Add problems".
- The link MUST be the HASH format from Polygon's copy button (the
  copy icon at the end of the link box in the right panel, under
  "View changes"): `https://polygon.codeforces.com/<hash>/<owner>/<slug>`
  (example: `https://polygon.codeforces.com/p3eEZsM/hieutrancong/ptgk-p7`).
- NEVER use the `/p/<id>/<slug>` link (B6):
  `https://polygon.codeforces.com/p/634823/in-search-of-an-easy-problem`
  is rejected by Codeforces with "Can not find problems by query".
- The contest code (B2) must be set explicitly, NOT left for
  Codeforces to auto-assign A/B/C: NB1 = Bubble Sort, NB2 = Di tim
  bai de nhat, NB3 = Keo Con; TH1-TH4, VD1-VD3, VDC1-VDC3 for the
  other problems.

## 12. Cross-check each other's problems

- Each person checks someone else's problems, not their own.

## Navigation that fails (C5)

- Opening `https://polygon.codeforces.com/problem/<id>` directly
  returns 404. Go via Dashboard > View Problems > "Continue" (the
  link on the LEFT).
- Never press OK on a "delete working copy?" dialog. Cancel out of
  it; OK deletes the working copy.

## Verification failed is NOT a stop rule (B14)

- In the video, verification FAILED after creating the package and
  was still failed at Revision 3, and Hieu still went to Codeforces.
- There is NO rule from Hieu saying "verification failed means stop".
  That rule was Muse's own invention (I18) and is a fabrication
  tripwire in `scripts/claim_check.py`.
- Only an invalid tests numeration (B4) blocks packaging. Fix the
  numeration, commit again, and continue.

## Error checklist (run before every commit)

1. Solution file ends `.cpp`, language msys2-g++23, Main correct (B1).
2. Statement language is english; no vietnamese statement file (B7).
3. `$` balanced in every statement field (B8).
4. Tests contiguous 1..N, no duplicates, count exact (B3, B4, B13).
5. Zip has inputs only (B12).
6. Contest link is hash format, never `/p/` (B6).
7. Short name matches NB/TH/VD/VDC + number (B2).
8. New package for the newest revision, Verify ticked (B5).
