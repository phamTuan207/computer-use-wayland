# W-Y6REVIEW log, re-review doc lap bang chung re-trial A8 (COORD-CLICK-6)
# Worker: W-Y6REVIEW. Chu: Pham Tuan. Nhanh: todolist-push.
# Chuan Lauren Tan: moi claim co lenh + output + commit hash + thoi gian (Asia/Ho_Chi_Minh, elapsed).
# Khong dau gach ngang dai. Khong ydotool. Khong tu cham pass. Chi DOC, khong chay trial, khong mo Zen.

## Pham vi va thoi gian
- Bat dau: 18:10 22/11/2026. Ket thuc: 18:15 22/11/2026 (elapsed ~5 phut).
- HEAD luc bat dau: efa206a (nhanh todolist-push, da fetch truoc do, ls-remote todolist-push = e1b62b4a).
- Nhiem vu: re-review doc lap bang chung re-trial A8 cua W-TODO (18:01:49-18:02:58 22/11), ket luan GO/NO-GO cho viec tick 4.13 va 2.2.3.
- Khong chay lai trial, khong mo Zen, khong chuyen focus, khong sua code hay todolist. Chi chay lenh doc (md5sum, wc, grep, git show, git diff) va 1 lan chay bo test unit tren VM (tests/test_y6c5_positive_gate.py, khong dung Zen).

## 1. Verify md5 evidence (lenh 18:10)
- Lenh: `md5sum improvements/y6c5-evidence/*` + `wc -l improvements/y6c5-evidence/*`.
- Output:
  - a8-rerun-20261122-180149.log: b112292d5cde51d3f85c808c9c9526ff, 86 dong. KHOP md5 W-TODO ghi (b112292d).
  - y6-profile-applied-20261122-180149.txt: d2702bacf07072816cd35c0bb179149d, 2 dong. KHOP md5 W-TODO ghi (d2702bac).
  - a8-trial-run-20261122-161803.log: d71a9a0bff17984d1ec846ff406e2edf, 84 dong. KHOP md5 W-TODO ghi (d71a9a0b).
  - ldd-y6e-conf.txt: d6d8512775ea99754c79d3280a2dd992, 99 dong. W-TODO khong ghi md5 file nay trong log, chi ghi ldd rc=0.
- Ket luan muc 1: 3/3 md5 W-TODO ghi deu KHOP file tren repo. Khong co file evidence nao bi doi sau khi W-TODO ghi log.

## 2. Metadata correction: 84 dong vs 77 dong, md5 d71a9a0b vs 721cb67c
- Lenh: `tail -n +8 improvements/y6c5-evidence/a8-trial-run-20261122-161803.log | md5sum` + `| wc -l`.
- Output: md5 721cb67c5b2947639236b89a706fad36, 77 dong. KHOP dung so invest log ghi.
- Lenh: `git show 5fdc527:improvements/y6c5-evidence/a8-trial-run-20261122-161803.log | md5sum` + `| wc -l`.
- Output: md5 d71a9a0bff17984d1ec846ff406e2edf, 84 dong. File KHONG doi tu commit trial 5fdc527 (chi 1 commit cham vao file, git log xac nhan).
- Giai thich dung (kham pha cua re-review, chinh xac hon mo ta cua W-TODO): file repo co 84 dong vi gom 7 dong header comment (dong 1-7, tu ghi md5 721cb67c va 77 dong cua ban log goc) + 77 dong log chay that (dong 8-84). Invest log ghi "77 dong, md5 721cb67c" la DUNG cho ban log goc chua co header; W-TODO ghi "84 dong, md5 d71a9a0b" la DUNG cho file repo co header. Ca hai so deu dung, cho hai doi tuong khac nhau. Loi duy nhat cua invest log la khong noi ro pham vi dem (log goc, khong header). Khong co bang chung nao bi sua hay lam gia. Ket luan: metadata correction DUOC XAC NHAN, voi co che ro rang la 7 dong header.
- He qua: dong FAIL, gate lines, teardown ma invest log trich dan van khop verbatim (W-TODO da kiem tra o 18:00, re-review nay khong can lap lai vi file khong doi tu 5fdc527).

## 3. Fix o commit 44b9a80 (lenh 18:10-18:11)
- Lenh: `git show --stat 44b9a80` + `git show 44b9a80` theo tung file. Output: 5 file, 187 insertions, 72 deletions.
- Runner improvements/worker-y6b-run-nested-wayland-v2.sh:
  - G4 configerrors gate DOI LEN TRUOC A2 (khoi code chuyen vi tri, than khoi khong doi ngoai 4 dong comment A8-INVEST them vao; diff than khoi sau khi loai comment: IDENTICAL, kiem tra bang sed trich khoi G4 o 44b9a80^ va 44b9a80).
  - Gate A2 doi tu grep log sang poll marker file $RUN_DIR/y6-profile-applied.txt + doc layers.enabled truoc (IPC), log grep chi corroboration, fail string doi thanh "marker file ... absent".
  - Teardown them copy-out marker file truoc rm -rf RUN_DIR (dong cp moi, missing chi warn).
  - Comment cap nhat: reload hypothesis bi bac bo, log delivery lag.
  - Liquid gate: KHONG DOI code. `git show 44b9a80 -- runner | grep liquid` chi thay 1 comment bi xoa (NOTE ve early layers.enabled read) + dong comment liquid gate cu. Khoi liquid gate dong 499-516 o HEAD van la ban cu.
- Hook improvements/y6-nested-conf/nested-visuals-hook.lua: them viet marker file (io.open "w", 2 dong, close) SAU print applied, path tu XDG_RUNTIME_DIR, fallback /tmp/y6-nested/run. Thu tu dofile -> print -> viet file khong doi, khong pcall moi. Chi them, khong sua logic cu.
- Tests tests/test_y6c5_positive_gate.py: them assert marker file, cam log-grep quyet dinh gate, doi 2 test healthy dang log sang dang file (marker file present + log chi parse-1 = PASS), them assert hook viet/close file + XDG. Khong giam do bao phu: so test van 16.
- Trial doc improvements/worker-y6c5-a8-load-only-trial.md: dinh nghia do doi sang marker file, log chi corroboration. Khong doi pill, arms, backdrop, liquid gate (invest log dong 673 khop).
- Log improvements/w-todo-remaining-log.md: chi them log, khong phai code.
- Kiem chung doc lap bo test (lenh 18:11, VM, khong Zen): `python3 tests/test_y6c5_positive_gate.py`, 2.6s, output "RESULT: all 16 checks PASS". KHOP claim 16/16 cua W-TODO.
- Ket luan muc 3: fix DUNG nhu mo ta, khong co sua len nao ngoai 5 file da liet ke. Khong co file optics.lua, conf, hay liquid gate nao bi cham o 44b9a80.

## 4. Code path liquid_available va loi "liquid never ready in 60s"
- Code: scripts/indicator.py, ham _valid_liquid dong 210-240, liquid_available dong 242-253.
  - Dong 222: shaders phai thuoc ('ready', 'pending').
  - Dong 224: `if status['shaders'] == 'pending' and ready: return False`. Voi ready=True, shaders bat buoc phai "ready".
  - Dong 232-239: them dieu kien layers enabled true + active true + reason null, windows/subsurface enabled false.
- Runner liquid gate (HEAD, dong 499-516): poll indicator.liquid_available(env, ready=True), deadline 60s, in "liquid ready=False" moi lan, het 60s in "liquid never ready in 60s" roi fail. Code nay khong doi o 44b9a80 (muc 3), nen fix KHONG THE gay ra loi liquid.
- Lich su shaders pending o nest (truoc fix, cung code gate):
  - Trial 16:18: status JSON shaders "pending" (a8-trial-run log, dong 26-27 trong file repo).
  - Y6e 21:57: shaders "pending" o 7s (worker-y6r-rereview-log.md:107, 182; worker-y6r-council-2-evidence.md:106).
  - Vay pending la hanh vi nest co tu truoc, khong phai hoi quy do fix.
- O3 (cau hoi mo tu truoc: nest shaders co dat ready trong 60s khong): truoc re-trial nay, O3 ghi ro UNVERIFIED o nhieu cho (worker-y6r-rereview-log.md:107, 182; opt-council-m2-evidence.md:61; opt-council-m2-verdict.md:74). Re-trial nay la lan DAU TIEN cho doi het 60s o nest, va tra loi: KHONG, 31 lan poll False lien tuc (rerun log dong 36-66, dem bang `grep -c 'liquid ready=False'` = 31), dong 67 "liquid never ready in 60s". Day la dap an moi cho O3 trong cua so 60s, khong phai loi cua fix.
- Live shaders READY co nguon: paper log 16:15 doc read-only live status (improvements/worker-click5-y6-paper-log.md:332-335): version 1.1.1-cu.1, versionCheck match, active true, shaders READY, layers enabled true active true. Live co client dang chay, nest rong khong co client. Tuong thich voi giai thich "nest rong khong kich hoat bien dich shader", nhung co che kich hoat cu the (client nao, surface nao) CHUA co bang chung truc tiep trong repo, chi la giai thich hop ly nhat. Re-review nay khong khang dinh co che, chi khang dinh: loi la do dieu kien moi truong nest rong, khong do fix.
- Mau thuan trong trial doc can ghi nhan: dong 13 noi trial "does NOT prove the liquid readiness window (O3)", nhung dong 110-113 liet "liquid 60 s timeout" vao abort/FAIL, dong 137-138 noi "Do not proceed to the pill measurement on a failed trial". Theo van ban goc, run nay la FAIL va pill retry bi chan. Quyet dinh WAIVE cua COORD-CLICK-6 (chi cho lan re-trial nest nay) la thu go nut that nay bang quyet dinh, khong phai bang sua code. De xuat: ghi waiver + dap an O3 vao trial doc o lan cap nhat sau, de lan sau khong tranh cai lai.
- Pham vi waiver: chi cho re-trial nest nay. Pill retry chay tren live (live doc shaders ready o 16:15), nen liquid gate o pill retry van phai PASS; neu no FAIL o live thi do la loi that, khong duoc ap dung waiver nay.

## 5. Bang 7/7 measured items, moi item co dong bang chung (rerun log = improvements/y6c5-evidence/a8-rerun-20261122-180149.log, marker = y6-profile-applied-20261122-180149.txt)
- (1) Marker file 2 dong: marker dong 1 "Y6-NEST-OPTICS: applied blur=0.15 refraction=0.55 mask=contour namespace=computer-use-indicator", dong 2 "Y6-NEST-HOOK: profile applied". Rerun log dong 32-33 in lai 2 dong nay tu marker file, dong 35 gate OK, dong 71 "profile marker file saved to /tmp/y6-nested/y6-profile-applied-20261122-180149.txt". PASS.
- (2) Hook corroboration trong file: marker dong 2 (tren). Khong yeu cau trong log nua theo trial doc moi. PASS.
- (3) layers.enabled true: rerun log dong 21-22 (status JSON layers enabled true, active true, reason null), dong 31 "profile gate: features.layers.enabled=True", dong 35 gate OK. PASS.
- (4) Version match: rerun log dong 19 (JSON version 1.1.1-cu.1, versionCheck match), dong 26 "hyprglass version=1.1.1-cu.1 versionCheck=match", dong 34 re-check giong vay. PASS.
- (5) G4 empty, chay TRUOC gate: rerun log dong 28 "configerrors empty after profile application (G4 OK)", dung truoc dong 35 gate OK. PASS.
- (6) AMEND4 OK + AMEND5-BEFORE OK + live list truoc ghi day du: rerun log dong 2 AMEND4 OK, dong 4 AMEND5-BEFORE OK, dong 5-8 live plugin list truoc (hyprbars, hyprglass, computer-use-cursor). PASS.
- (7) Live untouched: rerun log dong 73-78 live PID 3638 alive (STARTED Sun Nov 22 17:19:41 2026), dong 79-81 plugin list sau giong truoc, dong 82 "live plugin list unchanged (before == after)", dong 83-84 stray check PID 3638, dong 85 lock free, dong 86 teardown done 18:02:58. PASS.
- Khong co item nao NO EVIDENCE. 7/7 co dong bang chung cu the. Thoi gian chay nhat quan: start dong 1 18:01:49, teardown dong 69 18:02:56, done dong 86 18:02:58 (69s = gate + 60s liquid wait). So poll liquid False = 31, khop 60s.
- Bang chung phu: staging md5 repo-side khop claim cua W-TODO: runner 42ac63d4d101f8ccb5e842eae9ef97c4, hook 0b1c5b2aa1e0a1bd2b9d5d56752e58d4, optics 85298d2035697710d95117355c9830ca; conf 9ccb2701... khop header ldd file. Runner/hook/optics khong doi tu 44b9a80 (git log 44b9a80..HEAD tren 3 file rong).

## 6. Nit nho (khong anh huong verdict)
- PII grep tren trial log cu co 2 hit: do chuoi "339" xuat hien trong day so cua nested sig (dong 20 va 69, "..._1795339084_327326060"), khong phai thong tin ca nhan. Hai file evidence MOI (rerun log + marker) co 0 hit. Khong co van de PII.
- `grep -c 'not found'` tren ldd file = 1: do dong header 8 tu ghi '"not found" count: 0'. Cac dong ldd that co 0 lib missing, libaquamarine.so.15 + libhyprgraphics.so.5 resolve (dong 11, 13). Claim "ldd rc=0, 0 not found" cua W-TODO dung.

## 7. Ket luan GO / NO-GO
- VE BANG CHUNG RE-TRIAL A8: GO. Fix dung nhu mo ta, 7/7 items co bang chung dong cu the, 16/16 tests PASS do re-review tu chay lai, metadata correction duoc xac nhan voi co che header 7 dong, loi liquid la do moi truong nest rong (O3 tra loi lan dau: khong dat ready trong 60s), khong do fix. Waiver liquid gate cua COORD-CLICK-6 cho dung lan re-trial nest nay la co co so.
- VE VIEC TICK 4.13 NGAY BAY GIO: NO-GO. Ly do cu the: noi dung muc 4.13 ghi "Y6 A1-A10 + fresh re-review, roi pill measurement retry (2.2.3...). Gate G-PILL", va trial doc dong 13 ghi A8 "does NOT prove the pill measurement (no arms ever ran)". Pill measurement retry CHUA chay. Tick 4.13 bay gio se tuyen bo mot viec chua xay ra. Phan da xong (fix + re-review + re-trial A8 7/7) duoc ghi nhan o tren, nhung muc chi duoc tick sau khi pill retry chay va PASS gate G-PILL.
- VE VIEC TICK 2.2.3 NGAY BAY GIO: NO-GO. Ly do cu the: noi dung muc 2.2.3 ghi "pill measurement van CHUA chung minh. Xem 4.13." Muc tieu cua 2.2.3 la chung minh do pill (indicator co repaint o idle khong), ma trial load-only khong co arm nao chay nen khong chung minh duoc. Tick bay gio se tuyen bo muc tieu da dat trong khi no chua dat.
- Dieu GO nay MO KHOA: chay pill measurement retry (tren live, co handover, gate G-PILL). Neu pill retry PASS, ca 4.13 va 2.2.3 du dieu kien tick. Neu pill retry FAIL o liquid gate tren live (noi shaders da doc ready o 16:15), do la loi that, khong ap dung waiver nest nay.
- Can bo sung sau (khong chan pill retry): ghi waiver + dap an O3 vao trial doc (giai quyet mau thuan dong 13 doi voi dong 110-113/137-138); cap nhat 4.13/2.2.3 ghi "A8 DONE 22/11 (re-review W-Y6REVIEW), pill retry pending" thay vi tick.

## Lennh da chay (tom tat Lauren Tan)
- 18:10: `md5sum improvements/y6c5-evidence/*`, `wc -l improvements/y6c5-evidence/*`, `grep -c 'liquid ready=False'` (= 31), `git show --stat 44b9a80`, `git log --oneline -8`, `git branch --show-current` (todolist-push), `git status --short` (dirty chi file cua worker khac, khong dung toi).
- 18:10-18:11: `tail -n +8 ... | md5sum` (= 721cb67c) + `| wc -l` (= 77); `git show 5fdc527:... | md5sum` (= d71a9a0b) + `| wc -l` (= 84); `git show 44b9a80` tung file; trich khoi G4 o 44b9a80^ va 44b9a80 roi diff (chi khac 4 dong comment); `grep -rn liquid_available` + doc scripts/indicator.py dong 180-290; `grep -n liquid` tren runner HEAD (dong 499-516); `grep -rn 'shaders.*ready'` (chi 1 hit la file diff source hyprglass, khong phai quan sat live); doc paper log dong 325-345 (live shaders READY 16:15).
- 18:11: `python3 tests/test_y6c5_positive_gate.py` (2.6s, 16/16 PASS, tu chay lai); `md5sum` runner/hook/optics (42ac63d4 / 0b1c5b2a / 85298d20, khop claim staging); `git log --oneline 44b9a80..HEAD` tren 3 file (rong); `git merge-base --is-ancestor 44b9a80 HEAD` (IN_HEAD); `git ls-remote origin todolist-push` (= e1b62b4a).
- Commit log nay: pathspec ro rang, khong amend, khong add -A (xem muc duoi).
