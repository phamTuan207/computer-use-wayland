# Independent judge report — overnight computer-use-wayland L3 run, multi-page fix (Worker N)

- Judge: independent judge run (separate Luna 6 max run, READ-ONLY). No code changes, no sessions started, no repo/installed-tree changes, no commits, no live tests, no broker use by the judge. No executor self-score received or used as proof; Worker N's report was used ONLY to locate evidence, and every claim below was re-verified by the judge against the evidence itself.
- Judged: 08:46-08:55, 17/11/2026 (+07). T0 = 22:30:38 16/11 (user start order). Judging elapsed from T0: +10h16m to +10h25m.
- Sources read in full by the judge: `test-cases.md` (CASES, 13 cases, rubric R=4/F=3/E=2/S=1, PASS=10/10, PARTIAL=1-9, FAIL/BLOCKED/NOT RUN=0), `test-scores.md` (prior baseline 0/130, tc02 0/10 FAIL), `typing-fix-multipage-report.md` (Worker N, 306 lines), `test-execution-report.md` (prior tc02 failure evidence).
- Build under test: repo HEAD `c9b96a7c73b3f2e2f4864b0d7ddbfefae1cd1efb` (multi-page fix), helper `83b8b9b25ff9adaab85b59ba047544a3317d1ea23c45e40b702e6119daa8f65b`. Every case `state.json` records `repo_head: c9b96a7c73b3f2e2f4864b0d7ddbfefae1cd1efb` (judge-checked all 14 trial dirs).
- Run dir (laptop): `/tmp/opencode/multipage-l3/` — `tc02-t1`, `tc02-t2`, `tc02-t3`, `tc01`, `tc03` through `tc13`, `stress/`. Evidence verified read-only via SSH (`~/workspace/ssh-laptop.sh`, short commands only). Key screenshots (20) fetched to the VM via scp and VIEWED directly by the judge (`/tmp/judge/`). All output files re-hashed by the judge on the laptop; hashes below are the judge's own.
- Prior baseline for comparison: tc02 0/10 FAIL (45-byte loss, SHA `8bb4c179...`, then 91-byte two-line file SHA `b10ffde1...`), total 0/130.

## Verdict

- **Total: 130 / 130. Full passes: 13 of 13.**
- tc02: **10/10, PASS** (3/3 trials byte-exact 50/50). tc01, tc03-tc13: **10/10 each, PASS**.
- Stress suite (separate, does NOT add to the 130): **S1 5/5 PASS, S2 PASS, S3 15/15 PASS, S4 PASS (rerun), S5 PASS (S5d, third attempt)**. S4 and S5 each needed reruns; each rerun failure was a driver/environment cause, confirmed from the stress log (see Stress section).

## Gates applied first (all cases)

1. **Meaningful-result zero gate: does NOT fire on any case.** Every case produced its exact task-specific application result, verified by the judge from files and/or viewed screenshots (per-case citations below).
2. **Prohibited-shortcut zero gate: does NOT fire on any case.** All scored input went through the real broker session (`session_remote.py` request files, broker generations recorded per case). Judge grepped all executor logs for `ydotool|set_text|browser fill|cu.py act|direct write` — zero hits. No direct file write, AT-SPI setter, `cu.py act`, ydotool, or API bypass is in the evidence. Keyboard navigation of open GTK menus (tc04, tc06) is brokered keyboard input through the session, a method a human can use; the menu-opening clicks were pointer clicks. a11y was used in tc01 only to IDENTIFY the Ellipse tooltip; the click itself was a pointer click. Copy/paste in tc09 was in-app Ctrl+C / Ctrl+V through the broker, not an external clipboard injection.
3. **Session-generation consistency: CONFIRMED for every case.** Each case's `state.json` generation matches its `evidence/finish-record.json` generation and its `evidence/start-readiness.json` ready-status generation (running / ready / active, broker generation `7bcc844bd0a1ad67957b4a27e06fef4e` throughout). All finish records: `ok: true, status: finished, driver: stopped, guardian: clean, error: null`.
4. **Timing: all in-session request gaps under 240 s.** Judge-parsed executor logs: max in-session gaps tc02-t1 102 s, tc02-t2 ~40 s, tc02-t3 ~25 s, tc01 223 s, tc03 26 s, tc04 63 s, tc05 102 s, tc06 51 s, tc07 30 s, tc08 89 s, tc09 50 s, tc10 27 s, tc11 54 s, tc12 47 s, tc13 171 s. The 960 s / 1151 s gaps in the tc02-t2/t3 logs are a shared prep line (05:43:28) to trial launch, i.e. inter-trial idle with no session held, not in-session gaps. First request after readiness: 25 s (tc02-t1), 29 s (tc02-t2), 25 s (tc02-t3) — tens of seconds, not a few; recorded as a timing observation, no rubric point depends on it.

## Per-case scores with evidence verified by the judge

### tc01 — Pinta yellow circle: 10/10 PASS (R4/F3/E2/S1)

- R (4): painted ellipse exists on canvas (2) — judge viewed `tc01/evidence/draw-ellipse.png`: yellow circle with selection handles, History `New Image / Ellipse Added`, Ellipse tool selected, brush width 7. Saved PNG reopens with that ellipse (2) — judge viewed `tc01/evidence/observe-reopened-2.png`: `hinh-tron-vang.png` tab, clean yellow circle, History `Open Image`, 640x480 at 90%, no selection, no dialog.
- F (3): yellow stroke (1); circular proportions and size/stroke (1) — judge decoded the PNG independently on the laptop: 640x480 RGBA, yellow pixels 4330, bbox 205x206 (w/h 0.995, diff 0.5% < 10%), diameter ~205 px (in 160-240), mid-row stroke runs 6 px and 7 px (in 4-8); one outline, white background, no extra marks (1) — judge viewed the PNG directly: one yellow circular outline on white, nothing else; the 615 non-white/non-yellow pixels by the judge's count are pale anti-aliasing blends at the stroke edge, inside the circle bbox.
- E (2): PNG decodes as 640x480 with nonblank yellow shape pixels (1) — file `/tmp/opencode/multipage-l3/tc01/output/hinh-tron-vang.png`, 9481 bytes, judge re-hash SHA-256 `0b2f8a7d1dd5156a9a21e7f370296eb3be343010dc8868b25e4bcdfa743aaea6`; pre-save History and selected-tool evidence support Ellipse rather than Rectangle Select (1) — `draw-ellipse.png` shows `Ellipse Added`, not Rectangle Select.
- S (1): saved result left visible without an active selection or dialog, broker finish completes (1) — reopen screenshot + finish record gen `52898492c9e4f42e504bab6201a7df05` (session 5 of 5; sessions 1-2 died on benign dialog-close capture failures, actions themselves succeeded; all 5 generations appear in `tc01/executor-log.md`).
- Caveat, no deduction: the reopen screenshot shows a background tab `hinh-tron-vang.png*` (asterisk) alongside the active clean tab; the active tab is the verified reopen and the file on disk is the verified PNG.

### tc02 — VS Code note `on-tap.txt`: 10/10 PASS (R4/F3/E2/S1), 3/3 trials

- R (4): task text appears in the editor following the brokered click/type sequence (2) — judge viewed `tc02-t1/evidence/type-sentence.png`: line 1 `Tối nay ôn cấu trúc dữ liệu lúc 20:30.`, caret on empty line 2; a nonempty `on-tap.txt` saved through the UI (2) — Save As via observed File menu + portal dialog, tab `on-tap.txt`, in all 3 trials.
- F (3): exact sentence and accents (1); exact filename/path (1); one sentence, one trailing newline, no duplicate insertion (1) — all 3 trials byte-exact, judge re-hashed each on the laptop: t1/t2/t3 all SHA-256 `8da1f5624c1b482bcdfae9d7c6883fdc52313dbe4120c2d1df2623ec5bcb9772`, 50 bytes each (the tc02 oracle). Independent `byte-exact-read-back.json` per trial: `exact: true, actual_bytes: 50, expected_bytes: 50`.
- E (2): independent file read-back matches the visible text (1); trace connects successful start/readiness, click/type, application result and finish under the same generation with caller-side image receipt (1) — t1 gen `320f5b16f36b47368a8ca87e1bc3290c` (36 requests, ready in 1.8 s), t2 gen `7b514cc48cee513fdaf01c7c6519f670` (15 requests, ready in 2.1 s), t3 gen `85adf101babd366b9dcf319745b2862a` (14 requests, ready in 2.0 s); executor logs record per-request image bytes (e.g. t1 type-sentence 51819 bytes).
- S (1): file saved, no dialog remains, broker finish completes with no recovery required (1) — all 3 finish records `finished / stopped / clean`, `error: null`.
- Baseline comparison: prior build lost Vietnamese characters on both attempts (45-byte file); this build is exact 50/50 on all 3 trials through the same real broker path.

### tc03 — Student-budget calculation (Omacalc, 180000): 10/10 PASS (R4/F3/E2/S1)

- R (4): budget expression visible (2) + evaluated result visible (2) — judge viewed `tc03/evidence/observe-result.png`: top line `125000 + 35000 + 20000`, large result `180000`.
- F (3): all three operands correct (1); addition used twice (1); result numerically 180000 (1) — judge checked the arithmetic independently: 125000 + 35000 + 20000 = 180000.
- E (2): readable result screenshot delivered (1); retained expression/history corroborates (1) — `observe-expr.png` + `observe-result.png` in evidence; session gen `ee40a3ed3bbf470319b5ba6f1f91de13`, finish clean.
- S (1): result stays visible without a stray menu/dialog, broker finish completes (1).

### tc04 — Reveal `.env.example` in Files: 10/10 PASS (R4/F3/E2/S1)

- R (4): `.env.example` revealed in the file list (2) — judge viewed `tc04/evidence/observe-on.png` (both files visible) and `tc04/evidence/observe-selected.png`: `.env.example` row highlighted, status bar `".env.example" selected (15 bytes)`; visibly selected in the correct folder (2), path bar `.../tc04/input/bai-tap`.
- F (3): exact fixture folder (1); exact hidden filename (1); README remains present and file contents unchanged (1) — judge re-hashed on the laptop: README.txt SHA `22a43f72e730bdfd908cdd869946fc5dce274a7492f18b963010d0004617a543` (25 bytes), `.env.example` SHA `daa81feca0eb71500a1aaad5e912ba3832e86d4411d2d53b4f1bfcd1e63bff21` (15 bytes = `APP_MODE=study` + newline).
- E (2): before/after images demonstrate the visibility change (1) — true before-state was established live, not from gsettings: the first observation showed BOTH files visible even though gsettings `show-hidden-files` was false (per-window toggle persisted in the running Nautilus process); the executor toggled OFF first, then the scored ON toggle. Menu-toggle evidence corroborates Show Hidden Files (1) — judge viewed both menu states: `observe-menu-on.png` (menu open, `Show Hidden Files` UNCHECKED, only README.txt visible) and `observe-off.png` (menu open, `Show Hidden Files` CHECKED, `.env.example` visible). The two opposite check states with matching list visibility prove the toggle, not a different folder/search. (Evidence filenames are confusingly named; the images themselves settle it.)
- S (1): original hidden-files preference restored after evidence and broker finish completes (1) — judge viewed `tc04/evidence/observe-restored.png`: only README.txt visible; session gen `d6c4e2c49ba6e7cdf4ca54f3c86daf8a`, finish clean.
- Note: the hamburger main menu has no Show Hidden Files in this Nautilus version; the toggle lives in the view-options dropdown, which the executor opened with a pointer click. Pointer clicks on the GTK popup menu items themselves do not land (grab blocks synthetic pointer events); keyboard navigation (Down + Enter) of the open menu was used instead — brokered keyboard input, a method a human can use. No deduction.

### tc05 — Save Vietnamese notes (`viec-ngay-mai.md`): 10/10 PASS (R4/F3/E2/S1)

- R (4): requested note content appears in the document (2); a nonempty Markdown file is saved and can be reopened (2) — judge viewed `tc05/evidence/observe-reopened2.png`: status bar `Opened viec-ngay-mai.md`, all 4 lines shown.
- F (3): Vietnamese spelling/accents and punctuation match (1); all four lines, leading markers and final newline match (1); exact output filename and directory (1) — judge re-hashed on the laptop: `/tmp/opencode/multipage-l3/tc05/output/viec-ngay-mai.md`, 137 bytes, SHA `6fee512ff5a659cd201f9ffa4f8320febed4ce5d195881548c98dbaeac10a7a1`; judge read the content: exactly the 4 specified lines + trailing newline.
- E (2): independent UTF-8 read-back verifies content (1); reopening shows the saved note rather than a different untitled buffer (1).
- S (1): no unsaved changes/dialog remain and broker finish completes (1) — final session gen `1f112702de50375fe89f132049f58fd6` (3 sessions; first Save As failed because Omawrite's own Save dialog treats a full path typed into the Name field as a filename, recovered via Ctrl+L + bare name; an Omawrite-inserted blank line after the heading was removed with Backspace; file then byte-exact 137/137), finish clean.

### tc06 — Rename `bai-tap-nhap.txt` to `CTDL-buoi-3.txt`: 10/10 PASS (R4/F3/E2/S1)

- R (4): a fixture rename is visible in the file list (2); the intended source now exists under the requested new name with its original bytes (2) — judge viewed `tc06/evidence/observe-after-rename.png`: `CTDL-buoi-3.txt` 31 bytes SELECTED (status bar confirms), decoy `bai-tap-nhap-cu.txt` 29 bytes intact, old name gone.
- F (3): exact new basename (1); exactly one `.txt` extension (1); decoy name and bytes remain unchanged (1) — judge re-hashed: `CTDL-buoi-3.txt` SHA `98f06e733eaace896709160dfba9c481e776df8698abb60bab27d1d72ce7d80a` (matches the recorded original), decoy SHA `042ece38ca416b3342e41822cba6aff78cde02bbdde8a9ca961b2b07a6278df0` (unchanged).
- E (2): filesystem listing corroborates the intended old/new names (1); original/result hash comparison establishes content preservation (1).
- S (1): the correct new file is selected, no rename dialog remains, and broker finish completes (1) — gen `f056f6d7e963b60e0bfa22103e8493ec`, finish clean. (One pointer click on `Rename...` landed ~35 px low and opened Compress; dismissed with Escape, no harm; recovered by keyboard navigation — the single allowed corrective attempt.)

### tc07 — Drag note into `CTDL` folder: 10/10 PASS (R4/F3/E2/S1)

- R (4): `ghi-chu.txt` appears inside `CTDL` following the recorded drag (2); the source disappears from the parent, establishing a move (2) — judge viewed `tc07/evidence/observe-ctdl.png`: CTDL open, `ghi-chu.txt` 26 bytes visible, path bar `.../sap-xep/CTDL`.
- F (3): destination is CTDL, not OOP (1); exact filename retained (1); bytes match the original (1) — judge re-hashed: `CTDL/ghi-chu.txt` SHA `bee64efd784d0fba1857f6611b21a6527a57f0610c83d2bd5f409e9a605df6a7` (matches original); `OOP/` still empty; parent no longer lists the file.
- E (2): before-parent and after-destination screenshots corroborate the transfer (1); independent source/destination/hash checks agree (1).
- S (1): destination folder is left open with no pending drag/dialog, and broker finish completes (1) — gen `acc76c70fd25eb249c95a1b799676fd6`, finish clean. Drag `{"type":"drag","from":[285,260],"to":[265,155],"ms":500}` worked first try.

### tc08 — Read timetable, save answer (`lich-thu-ba.txt`): 10/10 PASS (R4/F3/E2/S1)

- R (4): a timetable answer appears in the note editor (2); it is saved in a nonempty `lich-thu-ba.txt` (2) — judge viewed `tc08/evidence/observe-final.png`: tab `lich-thu-ba.txt`, breadcrumb `tmp > opencode > multipage-l3 > tc08 > output`, line 1 the answer, line 2 empty (trailing newline), no dialog.
- F (3): correct day/course pairing (1); time is 09:00-10:30 (1); room is A2-407 (1) — judge read the fixture `/tmp/opencode/multipage-l3/tc08/input/thoi-khoa-bieu.html` (verified against the spec: 4 rows; the Thứ Ba + Cấu trúc dữ liệu row is 09:00-10:30, A2-407; decoys are OOP/B1-305, Mon A2-203, Wed A2-203) and the output file: `Thứ Ba: Cấu trúc dữ liệu, 09:00–10:30, phòng A2-407.` + newline, 65 bytes, judge re-hash SHA `b12982656e1fcb145f0503377ed5e6968a9c946c1c63fe812287f2b99d20c186`.
- E (2): retained source screenshot shows the matching row and headings (1) — judge viewed `tc08/evidence/observe-tkb.png`: rendered table, all 4 rows with headings Ngày/Giờ/Môn học/Phòng; independent result read-back matches the visible note (1).
- S (1): saved note remains visible without unsaved changes/dialogs and broker finish completes (1) — gen `b6d9213ba2bb0edd5eb7460b2b0a1f31`, finish clean. (Two earlier tc08 sessions died on `window is not visible on its monitor` because Zen lives on workspace 1; the executor focused Zen via the Lua-wrapped hyprctl dispatch and proceeded. Those were setup failures, not scored attempts.)
- Note: VS Code/Zen screenshots render some Vietnamese diacritics as tofu boxes (font artifact); the file bytes are exact, which is what the rubric scores.

### tc09 — Copy Vietnamese text into an unsent local draft: 10/10 PASS (R4/F3/E2/S1)

- R (4): first source line appears in the draft (2); second source line appears beneath it (2) — judge viewed `tc09/evidence/observe-pasted.png`: textarea contains both lines exactly once, with the line break, accents correct.
- F (3): accents and punctuation match (1); line break and single occurrence of each line preserved (1); content is in the intended local draft field, with no send action (1) — the disabled `Gửi — đã khóa trong thử nghiệm` button is visible; no send action was taken; the draft tab was left open.
- E (2): source/destination screenshots allow a direct content comparison (1) — source `nhac-lich.txt` (105 bytes, SHA `07476d68...` per report; judge read the two lines and confirmed the fixture) vs pasted draft; trace shows actual in-app copy and paste, and final UI shows the disabled Send control (1) — evidence includes `select-copy.png`, `observe-copied.png`, `click-paste.png` (Ctrl+A + Ctrl+C in VS Code, Ctrl+V in Zen, all brokered).
- S (1): unsent draft remains visible and broker finish completes (1) — gen `644106003ccb615431d64c3456ace581`, finish clean.

### tc10 — Replace `linked list` in one note: 10/10 PASS (R4/F3/E2/S1)

- R (4): first occurrence replaced (2); second occurrence replaced (2) — judge viewed `tc10/evidence/observe-replaced.png`: both lines show `danh sách liên kết`, Find `linked list` shows `No results`.
- F (3): replacement text and accents exact (1); stack line and other target-file text unchanged (1); sibling file unchanged (1) — judge read `/tmp/opencode/multipage-l3/tc10/input/ghi-chu-ctdl.txt` (both replacements, `stack dùng nguyên tắc LIFO.` intact) and re-hashed the sibling `khong-sua.txt` SHA `d4e7e97c82a4501e17beb96d364bf2288df2a8a4df341a33ec341cf03db2305b` (unchanged).
- E (2): saved-file read-back contains two replacements and no old term (1); before/after editor evidence shows single-file scope (1) — editor Find/Replace (Ctrl+H, single-file, match count `2 of 2`), Replace All via Ctrl+Alt+Enter.
- S (1): edited file is saved, Find/Replace is dismissed, and broker finish completes (1) — judge viewed `tc10/evidence/observe-final10.png`: Find bar gone, edited note visible; gen `0c596be779d444e09c1f77ad1df06d41`, finish clean.

### tc11 — Scroll to last assignment question (Câu 30): 10/10 PASS (R4/F3/E2/S1)

- R (4): the page visibly reaches the final question after wheel input (2); a nonempty final-question note is saved (2) — judge viewed `tc11/evidence/observe-scroll2.png`: Câu 28, Câu 29 and Câu 30 fully visible with the full final text `Cài đặt hàng đợi bằng hai ngăn xếp; phân tích độ phức tạp của enqueue và dequeue.`, no further question follows.
- F (3): correct question number 30 (1); queue-with-two-stacks requirement preserved (1); both `enqueue` and `dequeue` complexity requirements preserved (1) — output file `/tmp/opencode/multipage-l3/tc11/output/cau-cuoi.txt`, 116 bytes, judge re-hash SHA `b7414877a475f8b470ca4250060af78ec77b724b9865504e5397b4f3b80de6da` (matches the report's oracle); judge verified the fixture `de-bai.html` has 30 sections, final section heading `Câu 30` with that exact text.
- E (2): top/bottom screenshots and wheel trace demonstrate actual navigation (1) — `observe-top.png` (Câu 1-3) → `observe-scroll2.png` (Câu 28-30) via broker scroll action dy=+800 (positive-down); saved-file read-back agrees with the final-section screenshot (1).
- S (1): note is saved without a dialog, source tab remains available, and broker finish completes (1) — judge viewed `tc11/evidence/observe-final11.png`: tab `cau-cuoi.txt`, breadcrumb `tc11/output`; gen `05646f8f1a2cc4f2f6fe767959d434ca`, finish clean.

### tc12 — Open timetable, deliver readable screenshot: 10/10 PASS (R4/F3/E2/S1)

- R (4): Zen visibly renders the fixture timetable (2); a nonempty valid PNG of it is produced (2) — judge viewed `tc12/output/lich-tuan.png` directly: title `Lịch học tuần này` + all three schedule lines readable.
- F (3): title and all three schedule lines included (1); text is legible and not clipped (1); capture is limited to the test browser window, without unrelated desktop content (1) — the PNG is the Zen window observation (925x581), title + 3 lines fully legible; the Zen sidebar (other tab titles) is part of the browser window chrome, and the blurred surround is Zen's own glass rendering, not another application window or desktop content. The judge awards this point and records the sidebar as an observation, not a deduction.
- E (2): independent PNG decode succeeds (1) — judge decoded on the laptop: PNG 925x581 RGB; caller receipt record includes actual PNG bytes/byte count matching the preserved image (1) — file 540693 bytes, judge re-hash SHA `ccc2d94bfe9b184ba0985be998d0dd3abcf6667b0d4e58c93068cd937de3d291`, identical to the evidence copy.
- S (1): timetable remains visible without menus/dialogs and broker finish completes (1) — gen `02d682739496f3a04f8459e46b5adcd7`, finish clean. Fixture `lich-tuan.html` verified against the spec (title + the 3 specified lines).

### tc13 — Create `CTDL buoi 3` + `README.txt` in terminal: 10/10 PASS (R4/F3/E2/S1)

- R (4): the requested directory is created by the terminal command (2); its nonempty README file is created (2) — judge viewed `tc13/evidence/observe-cat.png`: terminal shows `pwd` → `/tmp/opencode/multipage-l3/tc13/output`, the typed `mkdir -- 'CTDL buoi 3' && printf ...` command, `cat -- 'CTDL buoi 3/README.txt'` output `Bài tập danh sách liên kết`, idle prompt.
- F (3): directory name preserves spaces and capitalization (1); filename exactly `README.txt` (1); file text and trailing newline exact (1) — judge verified on the laptop: directory `CTDL buoi 3` exists, `README.txt` 34 bytes, SHA `76e6da66ce3a6dc52b4c654ca20f9db8ad3e453b315b864571dd433cca1888c2` (matches the report's oracle).
- E (2): terminal screenshot shows execution and matching `cat` output (1); independent filesystem read-back verifies path and bytes (1).
- S (1): terminal returns to an idle prompt, result remains visible, and broker finish completes (1) — gen `b5090269aac36a0bb1f16f32e750f8b2`, finish clean.

## Full 13-case table

| # | Case | Status | R /4 | F /3 | E /2 | S /1 | Total /10 | Reason / key artifact |
|---|---|---|---|---|---|---|---|---|
| 1 | Pinta yellow circle | PASS | 4 | 3 | 2 | 1 | **10** | PNG 9481 B, SHA `0b2f8a7d...`, 640x480, yellow 4330 px, bbox 205x206; `draw-ellipse.png` History `Ellipse Added` |
| 2 | VS Code note `on-tap.txt` | PASS | 4 | 3 | 2 | 1 | **10** | 3/3 trials byte-exact 50/50, SHA `8da1f562...`; gens `320f5b16...`, `7b514cc4...`, `85adf101...` |
| 3 | Student-budget calculation (Omacalc, 180000) | PASS | 4 | 3 | 2 | 1 | **10** | `observe-result.png`: expression + `180000` visible |
| 4 | Reveal `.env.example` in Files | PASS | 4 | 3 | 2 | 1 | **10** | Toggle OFF/ON both menu-evidenced; selected, 15 B; restored; hashes verified |
| 5 | Save Vietnamese notes (`viec-ngay-mai.md`) | PASS | 4 | 3 | 2 | 1 | **10** | 137 B, SHA `6fee512f...`, exact 4 lines; reopen verified |
| 6 | Rename `bai-tap-nhap.txt` to `CTDL-buoi-3.txt` | PASS | 4 | 3 | 2 | 1 | **10** | Renamed file SHA `98f06e73...` = original; decoy `042ece38...` unchanged |
| 7 | Drag note into `CTDL` folder | PASS | 4 | 3 | 2 | 1 | **10** | `CTDL/ghi-chu.txt` SHA `bee64efd...` = original; OOP empty; drag first try |
| 8 | Read timetable, save answer (`lich-thu-ba.txt`) | PASS | 4 | 3 | 2 | 1 | **10** | 65 B, SHA `b1298265...`; correct row 09:00-10:30, A2-407 |
| 9 | Copy Vietnamese text into unsent local draft | PASS | 4 | 3 | 2 | 1 | **10** | Both lines pasted once; disabled Send visible; no send |
| 10 | Replace `linked list` in one note | PASS | 4 | 3 | 2 | 1 | **10** | 2 replacements, 0 old terms; sibling SHA `d4e7e97c...` unchanged |
| 11 | Scroll to last assignment question (Câu 30) | PASS | 4 | 3 | 2 | 1 | **10** | `cau-cuoi.txt` 116 B, SHA `b7414877...`; Câu 30 visible after wheel scroll |
| 12 | Open timetable, deliver readable screenshot | PASS | 4 | 3 | 2 | 1 | **10** | PNG 540693 B, SHA `ccc2d94b...`, 925x581 RGB; title + 3 lines legible |
| 13 | Create `CTDL buoi 3` + `README.txt` in terminal | PASS | 4 | 3 | 2 | 1 | **10** | README 34 B, SHA `76e6da66...`; terminal `cat` output matches |
| **Total** | **13 cases** | **13 PASS** | | | | | **130 / 130** | 13 attempted, 13 full passes. Prior baseline 0/130. |

## Stress suite (separate; does NOT add to the 130)

No detailed stress spec exists in the repo or the brief; Worker N defined S1-S5 from the program shape. The judge verified the stress evidence from `/tmp/opencode/multipage-l3/stress/stress.log` (judge-read) and re-hashed the stress output files.

| Stress | Result | Judge-verified evidence |
|---|---|---|
| S1 — 5 back-to-back sessions (start, type, save, verify, finish each) | **5/5 PASS** | `s1-1.txt` … `s1-5.txt`, each 50 B, SHA `8da1f562...` (judge re-hash); log 07:48:19-07:50:34, each `saved=True exact=True finish_clean=True` |
| S2 — rapid sequential inputs (5 types in one act) | **PASS** | `s2.txt` 250 B, 5 lines, SHA `38ec42cb...` (judge re-hash); log `saved=True exact=True bytes=250 lines=5 finish_clean=True` |
| S3 — 15 consecutive observations on one window | **PASS** | Log: `15/15 observations ok, finish_clean=True` |
| S4 — observation expiry + recovery (sleep 100 s) | **PASS (rerun)** | Rerun log 07:57:58-08:00:06: stale act explicitly refused (`session_continues: true`, no input sent), recovery fresh observe + type + save exact 50 B (`s4.txt` SHA `8da1f562...`, judge re-hash), finish clean. First run FAILED at 07:53:20 because the stale act never had a last observation (`no last observation in state; observe first`) — 9 accumulated test VS Code windows had tiled new windows into tiny slivers (0x-5), so the observes failed; the expiry part was never exercised. Cause is environment/driver, not the fix or broker; the rerun on a clean screen exercised it properly. |
| S5 — long session (~10 min, 5 type+observe cycles 2 min apart) | **PASS (S5d, third attempt)** | `s5d.txt` 250 B, 5 lines, SHA `38ec42cb...` (judge re-hash); log 08:33:36-08:42:25 `cycles_ok=5/5 saved=True exact=True finish_clean=True`. First rerun (08:00-08:08) FAILED exact=False, 50 B/1 line: driver slept 120 s then acted on the pre-sleep observation, so cycles 2-5 were refused as stale — the 90 s expiry worked as designed; driver bug. S5b (08:11-08:20) same failure, 50 B/1 line. S5c (08:22-08:31) all 5 types landed (250 B, 5 lines) but exact=False: fixed-position click put the caret mid-document, later types inserted mid-text — driver bug, typing fine. S5d fixed it with Ctrl+End before every type. All three failures are documented driver/environment causes; the broker and the typing fix behaved correctly throughout. |

## Human-likeness assessment (all cases)

- **Real session path: YES, all 13 cases.** Broker start → authenticated `running / ready / active` → windows/observe/act requests → finish, under one generation per case, via `session_remote.py`. 875 JSON evidence records across the run dirs (judge-counted).
- **Pill visible: NOT EVIDENCED in the delivered images.** The screenshots are window-scope observations (VS Code/Pinta/Files/Zen window crops) plus dialog crops; the desktop overlay pill is not visible in any image the judge viewed. Window-scope crops cannot show the pill either way, and per test-cases §8 a normal clean capture may hide the overlay, so this is withheld as unverified, not scored as absent. Same withholding as the prior judge's tc02 report. Pill F1 stays deferred per the plan.
- **Cursor actually moving / clicks landing where a human would click: VERIFIED BY EFFECT.** Each pointer click's effect is verified by a fresh after-observation (banner gone, caret at line 1 col 1, File menu open, Save As dialog, tab renamed, ellipse painted, file selected, drag toast, menu toggles). The cursor glyph itself is not discernible in the delivered crops, so cursor visibility is withheld as unverified.
- **Typing into the focused app: YES, all typing cases.** Editor/terminal/textarea clicks verified focus before typing; typed text appeared in the focused app via the brokered keyboard path (tc02 3/3 exact, tc05/tc08/tc10/tc11 exact, tc13 terminal command executed).
- **Human-like recovery: YES.** tc01 tooltip consumed the first Ellipse click → moved pointer away, re-clicked, verified tool state; tc02 Save As via File menu after Ctrl+Shift+S failed; tc05 Save As failure → Ctrl+L + bare name; tc06 Compress mis-click → Escape + keyboard nav; tc04 pointer can't click GTK popup items → keyboard nav of the open menu; tc08 workspace focus via hyprctl dispatch. All verified by fresh observations, not blind retries.
- **Overall:** the operations looked and behaved like a human doing them through the real UI, and this time the results are exactly what a human would produce.

## Execution context (for the coordinator)

- Run dir (laptop): `/tmp/opencode/multipage-l3/`. Prior run `/tmp/opencode/overnight-fix-20261116-0105/` is the superseded 0/130 baseline and is not evidence for this verdict.
- Repo HEAD at execution: `c9b96a7c73b3f2e2f4864b0d7ddbfefae1cd1efb`; repo_head recorded identically in all 14 trial `state.json` files (judge-checked). Broker generation `7bcc844bd0a1ad67957b4a27e06fef4e` throughout.
- L3 wall times (from Worker N's report, cross-checked against executor-log timestamps by the judge): tc02 05:43-06:05, tc01 06:06-06:32, tc03 06:34-06:35, tc04 06:35-06:45, tc05 06:46-07:00, tc06 07:01-07:06, tc07 07:06-07:08, tc08 07:09-07:18, tc09 07:18-07:22, tc10 07:22-07:25, tc11 07:27-07:33, tc12 07:33-07:37, tc13 07:37-07:42; stress 07:44-08:42.
- Judge's own verification footprint: re-hashed all 13 output/result files on the laptop; viewed 20 screenshots fetched to the VM (`/tmp/judge/`); read all 14 `state.json` + `finish-record.json` + `start-readiness.json` (tc02 trials) files; parsed all executor logs for request counts, gaps, refusals, and prohibited-shortcut terms; read the stress log and re-hashed all stress output files; independently decoded the tc01 PNG and the tc12 PNG on the laptop.

## What the judge could NOT verify

- Pill visibility and cursor-glyph appearance during any case: no desktop-scope image in the evidence shows them; window-scope crops cannot settle it. Withheld, not inferred. Does not affect any score (no rubric point requires the pill).
- The offline verification claims in Worker N's report (native tests 23/23, full suite 1030 tests, live GUI verification 21/21 trials): not re-verified by this judge; they are outside the L3 live-suite judging scope. The L3 verdict above rests only on the live brokered evidence.
- Every per-request record file on the laptop was not individually re-read (875 JSON records exist); the judge verified state/finish/readiness records, executor logs, byte-exact read-backs, and the key screenshots, and re-hashed every result file.
- First request after readiness took 25-29 s in the tc02 trials (SSH round-trip + driver processing), not "within seconds" in the strict sense; no rubric point depends on it, and all in-session gaps stayed under 240 s.
- Whether the tc01 reopen tab's `hinh-tron-vang.png*` asterisk denotes an unsaved change in a background tab: the active reopened tab is clean and the file on disk is the verified PNG; no deduction.
- tc12's delivered PNG includes the Zen sidebar (other tab titles) as part of the browser window chrome; the judge awards the framing point with this noted, since no unrelated application window or desktop content appears.
