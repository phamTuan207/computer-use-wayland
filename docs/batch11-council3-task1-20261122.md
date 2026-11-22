# Hoi dong 3, batch 11 task 1: gioi han va luu y cua bao cao kiem tra step 7

Nguoi viet: council 3, batch 11 task 1. Chi doc va viet bao cao, khong sua coord/clone1.md hay coord/clone2.md, khong commit, khong push.
Uy quyen: coordinator Muse, coord/clone1.md, batch 11 task 1, commit d9b0c05 tren origin/main.
Doi tuong: docs/batch11-task1-step7-verify-20261122.md, bao cao kiem tra doc lap step 7 tai commit 292753f0914bd4a67808233e287ed2812dbd5cd3.
Ngay viet: 2026-11-22 (+07). File test-w.txt 0-byte khong dung toi, de nguyen.
Phuong phap: fetch read-only origin todolist-push va main, git grep va git show tai dung 292753f, doc truc tiep 3 script tam trong /tmp cua verifier, doc lai bao cao verifier. Khong chay lai bo test, khong build gi them.

## Ket luan ngan

Verdict PASS cua verifier dung trong pham vi no tu dat ra, nhung pham vi do hep hon nhieu so voi nhung gi tieu de bao cao co the gay hieu. Cac cho sau day la gioi han bang chung that, khong phai loi cua verifier: bo P2 khong co test nao cho pointer=None, duong re-ground tra sai ma loi, bo test day du 2110 test cua worker khong duoc chay lai, hieu chinh mo hinh 1 chi duoc doc code chu khong chay, kiem tra validator va no-pointer dung fake va so lieu nhap tay, toan bo bang chung chay lai phu thuoc vao mot worktree tam da bi xoa. Step 7 chua duoc chung minh tren Zen that, tren may sach, hay o quy mo day du.

## 1. Nhung gi verifier khong test

1.1. Khong co test P2 nao bao truc tiep truong hop pointer=None. Kiem chung lai bang lenh `git grep -n 'no_pointer_delegate' 292753f -- tests/`, ket qua 0 dong, exit 1. Trong khi do `git grep -n 'no_pointer_delegate' 292753f -- scripts/` chi co 2 dong, deu trong scripts/zen_backend.py:596 va 602. Tat ca ZenBackendTests trong bo P2 dung FakeZenPointer, khong co truong hop nao truyen pointer=None.

1.2. Duong re-ground voi pointer=None khong co test, va lai tra sai ma loi. Verifier tu phat hien GAP nay bang script tam: ket qua ok False, input_sent False, nhung error la `{'code': 'action_failed', 'reason': 'focus_check'}`, khong phai no_pointer_delegate. Nguyen nhan theo bao cao: nhanh re-ground o scripts/zen_backend.py:531 goi thang _dispatch ma khong qua kiem tra pointer o dong 584. Khong co input nao duoc gui, nen fail-closed, nhung ma loi gay hieu lam ve nguyen nhan that. Chua ai kiem tra co caller nao re nhanh theo ma loi nay hay khong, nen muc do anh huong that chua biet.

1.3. Verifier chi test truc tiep dom_act click voi pointer=None. Cac action khac cung nam trong danh sach kiem tra pointer o zen_backend.py:596-604 (double_click, confirm_click, hover_click, fill, set_value, key, scroll) khong duoc test truc tiep. dom_start va dom_observe voi pointer=None cung khong duoc test.

1.4. Full discover 2110 test khong duoc chay lai. Commit message cua 292753f tu bao "Full discover: Ran 2110, 0 failures, 4 pre-existing errors, 17 skipped", nhung verifier chi chay lai 86 test P2 va 294 test o 7 suite lien quan, tong 380 test. 4 loi co san va 17 test bi skip trong tuyen bo cua worker khong duoc dinh danh, khong duoc doi chieu. Tuyen bo full discover van chi la loi worker, chua co kiem chung doc lap.

1.5. Mot file test bi sua trong commit nhung khong duoc chay lai: tests/test_keyboard_preflight.py doi 1 dong trong diff 17 file, nhung khong co trong danh sach 7 suite verifier chay (test_zen_dom, test_click3_redteam2, test_code_exec, test_a1_preflight, test_core, test_first_action, test_s0_bundle). Hai file test goi ham dom_rect_to_image_point duoc giu lai (tests/test_click2_redteam.py, tests/test_pick4_fastpath.py) cung khong duoc chay, chi duoc grep de dem caller.

1.6. Khong co test live tren Zen that. Khong co lan chay nao mo Zen browser that, khong co cua so that, khong co pointer delegate that. Mọi ket qua Zen backend deu qua FakeZenSession va FakeZenPointer lay tu chinh file test P2.

## 2. Phu thuoc may nay

2.1. Bo P2 khong chay duoc ngay tren may sach vi thieu helper native/wtype. Lan chay dau cua verifier: Ran 86 tests, FAILED (errors=21), tat ca o ScreenScopeLegalityTests, loi `RuntimeError: private wtype helper is missing`. Nguyen nhan da kiem chung lai: .gitignore:13 ghi `native/wtype`, `git ls-files 292753f native/` chi co vendor/wtype (LICENSE, README.md, keyboard-correction.patch, main.c), va `ls native/wtype` tren repo chinh bao khong co file. Ket qua OK 86/86 chi dat duoc sau khi verifier build thu cong phan wtype tu source vendored.

2.2. Cach build wtype khong tai hien duoc tu bao cao. Bao cao chi mo ta bang loi: wayland-scanner tao keyboard-protocol, patch main.c bang keyboard-correction.patch, cc bien dich. Khong co lenh day du, khong co log build, khong co hash cua binary. May khac muon chay lai bo P2 phai tu dung lai cac buoc nay. Them nua, chay tron scripts/build.py that bai tren may nay vi thieu gtk4-layer-shell-0 o buoc indicator, nen verifier chi build rieng phan wtype. Day la phu thuoc moi truong, khong phai loi code, nhung no co nghia la ket qua OK gan voi may nay va voi mot binary khong co trong repo.

2.3. Tuyen bo "may cua worker co san binary" la suy doan, khong kiem chung. Verifier khong co quyen truy cap may worker, khong co log nao tu may worker chung minh binary ton tai o do. Chi biet chac mot dieu: binary khong co trong commit 292753f.

2.4. Thoi gian chay (86 test trong 0.140s, 294 test trong 17.114s) la so do tren may nay, luc 05:08 den 05:12 UTC ngay 2026-11-22, khong co gia tri doi chieu tren may khac.

## 3. Chi doc code, khong chay

3.1. Hieu chinh mo hinh 1 (CLI act chi binding-when-present) chi duoc kiem tra bang cach doc code: scripts/cu.py desktop_act khoang dong 1864, nhanh CLI act khoang dong 3267, scripts/code_exec.py:780 va 280, diff scripts/first_action.py va scripts/cu.py. Khong co lan chay that nao cua `cu.py act` voi action co scope/observation_id va voi action khong co 2 truong nay de doi chieu hanh vi luc chay. Ket luan "dung code" la dung o muc doc, chua co bang chung luc chay.

3.2. G28 giu nguyen, cac hang so o scripts/element_ref.py (RECT_TOLERANCE_PX 0.5 dong 26, SNAPSHOT_MAX_AGE_SECONDS 120 dong 29, STALE_REASON_CODES dong 32), va cac tuyen bo phu o muc 7 cua bao cao verifier (DOM_WINDOW_CLASS 'zen', session timeout 30s, snapshot expiry 120s) deu chi duoc doc code, khong co test hanh vi nao kem theo.

3.3. Duong live mac dinh khong co pointer delegate (scripts/cu.py:3150 tao backend khi CU_DOM_BACKEND=zen ma khong truyen pointer) chi duoc doc code. Khong co lan chay that nao voi CU_DOM_BACKEND=zen de xem duong live that su roi vao trang thai nao.

3.4. Kiem chung lai cua council o muc nay co gioi han rieng: council kiem chung lai bang git grep phia scripts (dom_rect_to_image_point chi con 1 dong dinh nghia tai scripts/fastpath.py:229, no_pointer_delegate 0 hit trong tests/), bang git show --stat (17 file, 2227 them, 266 xoa), va bang merge-base (292753f la ancestor cua origin/todolist-push). Danh sach caller phia tests trong muc 3 cua bao cao verifier (test_pick4_fastpath.py, test_click2_redteam.py, test_click3_redteam2.py, test_p2_element_ref.py) council khong grep lai, chi ghi nhan theo bao cao.

## 4. Kiem tra truc tiep bang script tam: gioi han

4.1. Ca 3 lan kiem tra truc tiep (validator 6 truong hop, no-pointer duong chinh, no-pointer duong re-ground) deu chay bang script tam trong /tmp, khong commit, khong nam trong repo. Council doc lai ca 3 file va thay: /tmp/validator-check.py, /tmp/no-pointer-check.py, /tmp/no-pointer-reground-check.py deu con ton tai, nhung ca 3 deu co dong `sys.path.insert(0, '/tmp/p2-verify-292753f/scripts')`, trong khi worktree /tmp/p2-verify-292753f da bi xoa (doc thu bao loi No such file or directory). Ke tu luc worktree bi xoa, khong script nao chay lai duoc nguyen trang. Bang chung chay lai cua verifier chi con ton tai duoi dang loi ke trong bao cao.

4.2. Worktree tam da bi xoa theo dung loi verifier ghi ("se do sau khi bao cao xong"), va binary wtype build thu cong nam trong worktree do cung mat theo. Ngay tren may nay, muon chay lai bo 86 test cung phai build lai wtype tu dau.

4.3. File bao cao verifier hien la untracked trong repo (git status hien `?? docs/batch11-task1-step7-verify-20261122.md`). No chua duoc commit, nen bang chung kiem tra chua nam trong lich su git.

4.4. Kiem tra validator dung so lieu nhap tay, khong phai capture moi. Cac so moz [274, 66], absolute [2783, 980], window [2509, 914], size [925, 1176], inner [677, 1160], monitor [2464, 902, 1920, 1200] duoc verifier go tay vao script tu "live items56" va pixel proof a42ef12 cu. Day la kiem tra ham check_viewport_geometry don le, khong phai chay tren Zen dang mo. Neu go sai mot so, ket qua van hien PASS ma khong ai phat hien. 6 truong hop chi bao phu ham validator, khong bao phu duong goi no tu Zen backend hay tu dom_act.

4.5. Kiem tra no-pointer dung fake lay tu chinh file test dang duoc kiem tra (FakeZenSession, FakeZenPointer, _zen_fields, _zen_windows tu tests/test_p2_element_ref.py). Fake co the khong giong hanh vi session Zen that, nhat la o duong re-ground khi rect doi. Ket qua chi chung minh logic trong zen_backend.py, khong chung minh hanh vi tren Zen that.

## 5. Nhung gi con chua biet ve step 7 tai commit 292753f

- Full discover 2110 test co that su xanh tren may sach hay khong, va 4 loi co san voi 17 test skip la nhung gi.
- test_keyboard_preflight.py sau khi doi 1 dong co pass hay khong.
- test_click2_redteam.py va test_pick4_fastpath.py co pass hay khong sau khi ham dom_rect_to_image_point chi con duoc giu cho test va legacy.
- CLI act binding-when-present co hanh vi luc chay dung nhu doc code hay khong.
- Zen backend voi pointer=None co hanh vi nhu the nao tren Zen that, khong chi tren fake.
- Ma loi sai o duong re-ground (action_failed/focus_check thay vi no_pointer_delegate) co anh huong den caller nao khong.
- Build wtype tu source vendored co tai hien duoc tren may khac hay khong, vi lenh build day du khong duoc ghi lai.
- Cac action khac ngoai click (double_click, fill, set_value, key, scroll) co bi chan dung bang no_pointer_delegate hay khong.

## 6. Lenh va bang chung council da chay

- `git fetch origin todolist-push main` (read-only), `git show -s --format='%H %ci %s' 292753f` (xac nhan commit, 2026-11-22 04:56:34 +0000), `git merge-base --is-ancestor 292753f origin/todolist-push` (tra ve ANCESTOR-YES).
- `git show 292753f --stat` (17 file, 2227 them, 266 xoa, khop bao cao verifier).
- `git grep -n 'no_pointer_delegate' 292753f -- tests/` (0 ket qua, exit 1).
- `git grep -n 'no_pointer_delegate' 292753f -- scripts/` (2 dong: scripts/zen_backend.py:596 va 602).
- `git grep -n 'dom_rect_to_image_point' 292753f -- scripts/` (1 dong: scripts/fastpath.py:229, dinh nghia ham).
- `git ls-files 292753f native/` (chi co vendor/wtype voi 4 file, khong co binary wtype).
- `git show 292753f:.gitignore` (dong 13: native/wtype).
- `ls native/wtype` tren repo chinh (khong co file). `ls -la test-w.txt` (0 byte, 21/11 12:59, de nguyen).
- Doc /tmp/p2-verify-292753f (khong ton tai, da xoa). Doc /tmp/validator-check.py, /tmp/no-pointer-check.py, /tmp/no-pointer-reground-check.py (con ton tai, deu tro den worktree da xoa).
- Doc docs/batch11-task1-step7-verify-20261122.md (ban day du, la doi tuong cua bao cao nay).
- Council khong chay lai bo test nao, khong build wtype, khong tao worktree moi.

## 7. De nghi cho step sau

- Them test pointer=None vao bo P2 cho ca duong chinh va duong re-ground, bao ca click va it nhat mot action khac (vi du key hoac fill), de 0 hit cho no_pointer_delegate trong tests/ khong con lap lai.
- Sua nhanh re-ground o scripts/zen_backend.py:531 de tra no_pointer_delegate thay vi action_failed/focus_check khi pointer la None.
- Ghi buoc build native/wtype vao huong dan chay test (lenh day du, co log), hoac de test bao loi ro rang hon khi helper thieu.
- Chay lai full discover va ghi ro 4 loi co san cung 17 test skip; chay them test_keyboard_preflight.py, test_click2_redteam.py, test_pick4_fastpath.py.
- Chay that mot lan CLI act co va khong co scope/observation_id, va mot lan tren Zen that voi CU_DOM_BACKEND=zen, truoc khi tuyen bo step 7 hoan tat o muc live.
