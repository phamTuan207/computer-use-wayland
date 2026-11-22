# Council 1: kiem tra so lieu bao cao xac minh step 7, P2 element-ref

Nguoi kiem tra: batch 11 council 1 (chi kiem so lieu task 1). Khong sua coord/clone1.md, khong sua coord/clone2.md, khong commit, khong push. Khong dung toi file test-w.txt 0-byte.
Uy quyen: coordinator Muse, coord/clone1.md, batch 11 task 1, commit d9b0c05 tren origin/main.
Thoi gian kiem tra: 2026-11-22 12:13 den 12:18 +07 (05:13 den 05:18 UTC).
Commit duoc kiem tra: 292753f0914bd4a67808233e287ed2812dbd5cd3, "P2 element-ref rewrite: protocol, A9 screen point, Zen backend, verified-origin validator", 2026-11-22 04:56:34 +0000.
Trang thai commit: da xac nhan la ancestor cua origin/todolist-push truoc khi kiem tra (lenh `git merge-base --is-ancestor 292753f origin/todolist-push`, ket qua ANCESTOR-YES). Diff: 17 file, 2227 them, 266 xoa.

## Phuong phap va gioi han quan trong

Phuong phap: suy luan lai truoc tien tu repo, bang cac lenh chi doc (`git show`, `git grep`, `git diff` hien thi text) tai commit 292753f, khong sua code, khong checkout worktree.
Gioi han: KHONG chay lai test nao, KHONG build wtype, KHONG tao worktree. Ly do: sau lenh `git fetch origin todolist-push main` dau tien, he thong gan co kiem tra rui ro thuc thi cho ket qua lenh do va cam chay, checkout, build, test noi dung lay ve. Vi vay moi con so "OK" (pass/fail) trong bao cao xac minh chi duoc kiem chung o muc dem test va doc code, khong duoc chay lai de tai hien. Council can mot lan chay thuc thi o noi duoc phep de chot hai con so "Ran 86, OK" va "Ran 294, OK".
Luu y ve nhanh: code P2 khong co tren nhanh main hien tai (HEAD ed9b469). Tren main, `scripts/element_ref.py` va `tests/test_p2_element_ref.py` deu khong ton tai, `grep -rn 'dom_rect_to_image_point' scripts/ tests/` tra ve rong. Moi kiem tra duoi day deu doc truc tiep tai commit 292753f tren todolist-push.

## Ket luan

PASS voi 2 hieu chinh nho va 1 cau hoi mo. Tat ca con so dem deu dung khi dem ca test thua ke, khong chi dem dong `def test`. Phan hanh vi validator va no_pointer_delegate dung theo code doc truc tiep. Phan chay test (86 OK, 294 OK, loi 21 truoc khi build wtype, 6 truong hop validator chay truc tiep, kiem tra no_pointer chay truc tiep) chua duoc chay lai o vong council nay vi ly do neu o tren, chi duoc ho tro bang suy luan tinh.

## 1. Bo test P2: 86 test, DUNG ve so luong, chua chay lai

Bao cao xac minh noi: Ran 86 tests, OK (sau khi build wtype).
Kiem tra dem tinh tai 292753f:
- Lenh: `git grep -c 'def test' 292753f -- tests/test_p2_element_ref.py`, ket qua: 70.
- Dem thu cong theo lop: ElementRefTests 21, ValidatorFixTests 11, ScreenPointFormTests 11, CodeExecPlanValidationTests 9, ZenBackendTests 14, BackendRangeTests 2, ScreenScopeLegalityTests 2. Tong 70. Khong co tao test dong (`setattr`, `load_tests`, `addTest`, `subTest`, `globals()[` deu 0 ket qua).
- Diem quyet dinh: `class ScreenScopeLegalityTests(__import__('test_keyboard_preflight').DesktopPreflight)` (dong 1083-1085). Lop nay thua ke 16 test method tu DesktopPreflight.
- Lenh: `git show 292753f:tests/test_keyboard_preflight.py | sed -n '30,520p' | grep -c 'def test'`, ket qua: 16.
- Tong: 70 tu dinh nghia + 16 thua ke = 86. Khop con so 86 cua bao cao xac minh.
- Khong co TestCase nao khac rot vao namespace module nay: cac import o dau file chi lay `cu`, `FakeBackend`, `FakeDomBackend`, `FakeDomSession`, `FakeWdSession`, khong lay DesktopPreflight truc tiep. `__import__` nam trong khai bao lop co so, khong gan ten vao module. Nen unittest chi load 86 test nay, khong hon.
- Ket luan: so 86 DUNG. Trang thai OK thi chua chay lai o vong council nay (xem muc gioi han). Dem thu cong 70 dong `def test` neu khong cong 16 test thua ke se sai, day la cho de hieu lam nhat cua con so nay.

Hieu chinh nho: bao cao xac minh noi bo test "them 1 test verified-origin so voi 85 luc commit failing-first". Ve so rong thi dung: commit cha 4ae8cccb co 69 dong `def test` (69 + 16 = 85), commit 292753f co 70 dong (70 + 16 = 86). Nhung thay doi thuc te la 4 test them va 3 test xoa, khong phai chi them 1 test. Lenh `git diff 292753f^ 292753f -- tests/test_p2_element_ref.py | grep '^\+.*def test'` tra ve 4 dong: test_live_zen_state_refuses_unverified_moz, test_live_zen_state_accepts_verified_moz, test_live_zen_state_logs_the_verified_override, test_viewport_origin_live_state_records_the_override. Lenh grep `^\-.*def test` tra ve 3 dong bi xoa: test_live_zen_state_returns_the_computed_origin, test_live_zen_state_logs_the_closure_overflow, test_viewport_origin_live_state_records_the_warning. So rong +1, so gop 4 them 3 xoa.

Ghi chu ve wtype, DUNG: `.gitignore` dong 13 tai 292753f ghi `native/wtype`. Lenh `git ls-tree -r --name-only 292753f -- native/wtype` tra ve rong, tuc khong co binary nao duoc commit. Tren checkout main, `ls native/wtype` bao khong co file, trong khi `git ls-files native/` chi co `native/vendor/wtype/` (LICENSE, README.md, keyboard-correction.patch, main.c). Vay helper la build artifact bi gitignore, may khong co san binary se gap loi thieu helper nhu bao cao xac minh mo ta. Con so "errors=21" truoc khi build thi chua suy luan lai duoc bang tinh: lop ScreenScopeLegalityTests chi co 18 test (16 thua ke + 2 tu dinh nghia), nho hon 21. Dieu nay van co the dung vi mot test co the ghi 2 muc loi (loi o than test cong loi o tearDown), nhung council khong the khang dinh neu khong chay. De lai lam cau hoi mo cho lan chay thuc thi.

## 2. Bo test lien quan: 294 test, DUNG ve so luong, chua chay lai

Bao cao xac minh noi: Ran 294 tests, OK, gom 7 suite test_zen_dom, test_click3_redteam2, test_code_exec, test_a1_preflight, test_core, test_first_action, test_s0_bundle.
Kiem tra dem tinh tai 292753f, lenh `git grep -c 'def test' 292753f -- <file>` cho tung file:
- tests/test_zen_dom.py: 42
- tests/test_click3_redteam2.py: 19
- tests/test_code_exec.py: 55
- tests/test_a1_preflight.py: 7
- tests/test_core.py: 39
- tests/test_first_action.py: 71
- tests/test_s0_bundle.py: 29
- Tong so dong `def test`: 261, thieu 33 so voi 294.
- Phan thieu nam o test_click3_redteam2.py, co 2 nguon cong them:
  - Lop `R3aUnwiredPathTests(DesktopPreflight)` (dong 132) thua ke 16 test tu DesktopPreflight, ban than lop nay chi dinh nghia 2 test (dong 133 va 227). Cong 16.
  - File nay import truc tiep o muc module: `from test_keyboard_preflight import DesktopPreflight, cu` (dong 27). unittest loadTestsFromModule duyet `dir(module)` va load ca lop TestCase duoc import, nen DesktopPreflight duoc chay them mot lan nhu mot suite rieng. Cong 16.
- Tong: 261 + 16 + 16 = 294. Khop con so cua bao cao xac minh.
- Cac file khac khong co cong them: test_core co `Coordinates(IsolatedCuState)` va `SecureObservationFiles(IsolatedCuState)` nhung IsolatedCuState chi co setUp, khong co test method nao de thua ke. test_zen_dom chi import test_click3_redteam2 ben trong than test (dong 720, 750, 897, 920), khong gan ten o muc module. test_code_exec, test_a1_preflight, test_first_action, test_s0_bundle deu chi ke thua unittest.TestCase truc tiep, khong import lop TestCase nao tu module khac.
- Ket luan: so 294 DUNG. Trang thai OK thi chua chay lai o vong council nay (xem muc gioi han). Dem tho 261 dong `def test` se hieu sai con so nay neu bo qua 32 test cong them tu DesktopPreflight.

## 3. Khong con production caller cua dom_rect_to_image_point: DUNG, 0 caller

Lenh: `git grep -n 'dom_rect_to_image_point' 292753f -- scripts/ tests/`, ket qua 13 dong:
- Dinh nghia duy nhat trong scripts: scripts/fastpath.py:229.
- Test: tests/test_click2_redteam.py 3 vi tri (160, 166, 174), tests/test_click3_redteam2.py 2 vi tri (345, 346), tests/test_p2_element_ref.py 1 test (dong 471, test_dom_rect_to_image_point_kept_for_tests_and_legacy) cong 1 dong docstring (dong 22), tests/test_pick4_fastpath.py 4 vi tri (489, 584, 588, 592).
- Khop dung danh sach bao cao xac minh neu. So production caller ngoai dinh nghia: 0. DUNG.

## 4. Duong live dung dom_rect_to_screen_point: DUNG, 4 vi tri

Lenh: `git grep -n 'dom_rect_to_screen_point' 292753f -- scripts/ tests/`, ket qua trong scripts:
- scripts/dom_act.py:295 (ground_input), scripts/dom_act.py:543 (ground_many_one_shot), scripts/zen_backend.py:324 (_screen_point), scripts/zen_dom.py:940 (locate_screen_point). Dung 4 vi tri live-path nhu bao cao xac minh neu. DUNG.
- Ghi chu them: scripts/fastpath.py:261 goi ham nay ben trong chinh dom_rect_to_image_point (ham cu suy ra image point tu screen point), day la loi goi noi bo cua ham legacy, khong phai mot caller live-path thu 5. Cac dong con lai la docstring hoac comment (fastpath.py:200, 234; zen_dom.py:913, 920) va test (test_p2_element_ref.py:22; test_pick4_fastpath.py:568, 570, 575).

## 5. Validator verified-origin, 6 truong hop: DUNG theo code doc truc tiep, chua chay truc tiep

Doc `check_viewport_geometry` tai scripts/zen_dom.py, dong 107 tro di, tai 292753f. So live dung trong bao cao xac minh: moz [274, 66], absolute [2783, 980], window [2509, 914], size [925, 1176], inner [677, 1160], monitor [2464, 902, 1920, 1200], true origin [2749, 922] (ung voi verified moz [240, 8] o factor 1).
- Truong hop 1, khong verified: right_gap = 925 - 677 - 274 = -26, bottom_gap = 1176 - 1160 - 66 = -50, am nen vao nhanh tu choi. Code nem ZenDomError voi message co chu 'dimension closure fails' va ghi gap. DUNG.
- Truong hop 2, verified moz [240, 8]: v_right_gap = 925 - 677 - 240 = 8, v_bottom_gap = 1176 - 1160 - 8 = 8, deu khong am; verified nam trong window; verified_absolute = [2509 + 240 x 1, 914 + 8 x 1] = [2749, 922]. Moz-computed [2509 + 274, 914 + 66] = [2783, 980], khac ket qua tra ve. DUNG. Kiem tra them: [2749, 922] nam trong monitor [2464, 902, 1920, 1200] (2464 <= 2749 < 4384, 902 <= 922 < 2102), nen qua ca buoc containment.
- Truong hop 3, verified path bo qua absolute_origin: nhanh verified chi dung window + verified x factor, bien absolute chi duoc parse ma khong duoc dung tren nhanh nay. Truyen absolute rac [9999, 9999] van tra [2749, 922] theo code. DUNG.
- Truong hop 4, verified moz sai [900, 8]: v_right_gap = 925 - 677 - 900 = -652, am nen tu choi voi message verified khong dong. DUNG.
- Truong hop 5, F9 factor 2: bao cao xac minh mo ta chua du dau vao (khong noi moz nao duoc truyen). Ket qua tu choi van dung theo ca 2 cach doc: neu truyen moz bao cao [274, 66] thi closure that bai truoc; neu truyen moz dung [240, 8] thi buoc exactness that bai vi expected = [2509 + 480, 914 + 16] = [2989, 930], khac absolute [2783, 980]. DUNG ve ket qua, mo ta truong hop can ghi ro moz dau vao.
- Truong hop 6, F10 thieu factor: code kiem tra factor ngay dau ham, factor None hoac khong hop le thi nem ZenDomError voi message 'viewport factor is required' va nhac F10. DUNG.
- Log override: offset ghi trong code la verified - moz = [240 - 274, 8 - 66] = [-34, -58], khop so bao cao xac minh neu, va origin tra ve [2749, 922]. DUNG.
- Ket luan: ca 6 ket qua hanh vi deu suy ra duoc tu code. Council khong chay script kiem tra truc tiep nao (xem muc gioi han), nen phan "chay truc tiep" cua bao cao xac minh duoc xac nhan o muc doc code, khong phai o muc thuc thi.

## 6. Zen backend tu choi khi khong co pointer delegate: DUNG o duong chinh, GAP o duong re-ground DUNG

Doc scripts/zen_backend.py tai 292753f, khong chay truc tiep.
- Duong chinh: khoang dong 584-604, khi self._pointer is None va action thuoc click, double_click, confirm_click, hover_click, fill, set_value, key, scroll thi ket qua ghi input_sent False, target_received False, verified False, error code no_pointer_delegate, roi break. Ham _dispatch (dong 380-387) tra (False, False) khi pointer None, la lop phong thu thu hai. DUNG.
- Mac dinh: constructor co tham so pointer=None (dong 54-56). scripts/cu.py tao backend khi CU_DOM_BACKEND=zen ma khong truyen pointer (khoang dong 3150), kem comment ghi ro delegate chua duoc noi day va backend se tu choi input. DUNG.
- Action wait chay local (dong 490-500, time.sleep, ok True), assert doc state, khong can pointer. DUNG.
- GAP duong re-ground, DUNG: nhanh re-ground (khoang dong 531) goi thang self._dispatch ma khong qua kiem tra pointer o dong 584. Khi pointer None, _dispatch tra (False, False) nen ok False, roi code gan `error = {'code': 'action_failed', 'reason': basis}` (dong 556-558). Vay loi ghi nhan la action_failed, khong phai no_pointer_delegate, dung nhu bao cao xac minh neu. Khong co input nao duoc gui (fail-closed), nhung ma loi gay hieu lam ve nguyen nhan that.
- Khong co test truc tiep cho pointer=None: lenh `git grep -n 'no_pointer_delegate' 292753f -- scripts/ tests/` chi tra ve scripts/zen_backend.py:596 va 602, 0 ket qua trong tests/. DUNG. Tat ca ZenBackendTests dung FakeZenPointer.

## 7. Hieu chinh mo hinh 1, CLI act binding-when-present: DUNG, co 2 hieu chinh so dong

Doc code tai 292753f.
- scripts/cu.py, desktop_act (khoang dong 1864): vong lap chi goi element_ref.validate_action_binding khi action co 'scope' hoac 'observation_id'. Action khong co 2 truong nay di duong pixel cu. DUNG.
- scripts/cu.py, nhanh CLI act (khoang dong 3244-3267): comment ghi "CB-2 on this interface is binding-when-present, not mandatory", va code bo qua action khong co ca 2 truong (`if 'scope' not in action and 'observation_id' not in action: continue`). DUNG.
- Chieu bat buoc: scripts/code_exec.py co comment "CB-2: scope + observation_id are mandatory in action data" va vong lap validate moi action trong api_act. Hieu chinh so dong: comment nay o dong 772, khong phai dong 780 nhu bao cao xac minh ghi (dong 780 nam trong vong lap validate). Ham _validate_dom_actions dinh nghia o dong 205, khong phai dong 280 nhu bao cao xac minh ghi; khoi binding check nam o khoang dong 272-280, tuc so 280 chi dung cho khoi binding, khong phai cho dinh nghia ham. Noi dung thi dung, so dong trich dan lech nho.
- Xoa refusal screen-scope: diff 292753f^ sang 292753f cho thay scripts/first_action.py doi 47 dong, scripts/cu.py doi 162 dong. Trong first_action.py, doan refusal cu bi xoa va thay bang comment ghi refusal screen-scope da bi xoa, thay bang snapshot binding ma desktop_act thuc thi. Trong cu.py, nhanh `if screen_scope and any(a['type'] in ('key','type')...)` co o commit cha (dong 1845) va khong con tai 292753f. G28 giu nguyen theo code. DUNG.

## 8. Cac tuyen bo phu da doi chieu

- scripts/element_ref.py: RECT_TOLERANCE_PX = 0.5 (dong 26), SNAPSHOT_MAX_AGE_SECONDS = 120 (dong 29), STALE_REASON_CODES dinh nghia (dong 32). Khop bao cao xac minh. DUNG.
- scripts/zen_backend.py: DOM_WINDOW_CLASS = 'zen' (dong 51), SESSION_TIMEOUT_SECONDS = 30 (dong 52), SNAPSHOT_MAX_AGE_SECONDS lay tu element_ref (dong 45), message snapshot het han 120s (dong 305). DUNG.
- Worker log: `git show 292753f:improvements/worker-click5-p2-impl-log.md | wc -l` tra ve 504. Khop bao cao xac minh. DUNG.
- Commit cha cua 292753f la 4ae8cccb, co 69 dong `def test` trong file P2 (85 test tinh ca thua ke). So 85 cua bao cao xac minh dung o commit cha nay, nhung bao cao khong ghi ro commit failing-first co phai commit cha nay hay khong. De lai lam ghi chu, khong phai loi so lieu.

## Danh sach lenh va bang chung

- `git fetch origin todolist-push main`, `git show -s --format='%H %ci %s' 292753f`, `git merge-base --is-ancestor 292753f origin/todolist-push` (xac nhan commit va nhanh; chay truoc khi co gioi han thuc thi).
- `git grep -n 'dom_rect_to_image_point' 292753f -- scripts/ tests/` (0 production caller).
- `git grep -n 'dom_rect_to_screen_point' 292753f -- scripts/ tests/` (4 vi tri live-path).
- `git grep -n 'no_pointer_delegate' 292753f -- scripts/ tests/` (chi 2 dong trong zen_backend.py, 0 trong tests/).
- `git grep -c 'def test' 292753f -- tests/test_p2_element_ref.py` (70) va cho 7 file lien quan (42, 19, 55, 7, 39, 71, 29; tong 261).
- `git show 292753f:tests/test_keyboard_preflight.py | sed -n '30,520p' | grep -c 'def test'` (16 test thua ke cua DesktopPreflight).
- `git show 292753f:tests/test_p2_element_ref.py | grep -n '^class \|def test'` (dem theo lop, tong 70, khong co tao test dong).
- `git show 292753f:scripts/zen_dom.py | sed -n '90,280p'` (doc check_viewport_geometry va suy luan 6 truong hop bang so hoc).
- `git show 292753f:scripts/zen_backend.py | sed -n '50,60p;375,395p;490,500p;520,545p;545,580p;580,610p'` (pointer None, _dispatch, wait, re-ground, kiem tra pointer).
- `git show 292753f:scripts/cu.py | sed -n '1855,1875p;3140,3160p;3240,3275p'` (binding-when-present, tao backend khong pointer).
- `git show 292753f:scripts/code_exec.py | sed -n '205,280p;770,800p'` (mandatory, _validate_dom_actions).
- `git diff 292753f^ 292753f -- scripts/first_action.py scripts/cu.py` (xoa refusal screen-scope).
- `git diff 292753f^ 292753f -- tests/test_p2_element_ref.py | grep 'def test'` (4 them, 3 xoa, rong +1).
- `git show 292753f:.gitignore | grep -n 'wtype'` (dong 13), `git ls-tree -r --name-only 292753f -- native/wtype` (rong), `ls native/wtype` tren checkout main (khong co file).
- Khong co lenh chay test, build, hay tao worktree nao trong vong council nay.

## Verdict

PASS voi 2 hieu chinh nho va 1 cau hoi mo. Moi con so dem trong bao cao xac minh deu dung khi dem day du ca test thua ke: P2 86 (70 + 16), suite lien quan 294 (261 + 16 + 16), 0 production caller cua dom_rect_to_image_point, 4 vi tri live-path cua dom_rect_to_screen_point, 6 truong hop validator deu suy ra dung tu code, no_pointer_delegate dung o duong chinh va thieu o duong re-ground, khong co test pointer=None.
Hieu chinh 1: code_exec.py trich dan dong lech nho, comment mandatory o dong 772 khong phai 780, _validate_dom_actions dinh nghia o dong 205, khoi binding o khoang 272-280.
Hieu chinh 2: "+1 test verified-origin" la so rong, thay doi gop la 4 test them va 3 test xoa.
Cau hoi mo: con so "errors=21" truoc khi build wtype chua suy luan lai duoc bang tinh (lop ScreenScopeLegalityTests chi co 18 test), va trang thai OK cua ca 2 bo test chua duoc chay lai o vong council nay vi he thong cam thuc thi code lay ve. Can mot lan chay thuc thi o noi duoc phep de chot "Ran 86, OK", "Ran 294, OK", va "errors=21".
De nghi sua o step sau (khong chan step 7): them test pointer=None cho duong chinh va duong re-ground, sua nhanh re-ground de tra no_pointer_delegate thay vi action_failed, ghi ro mo ta truong hop F9 (moz dau vao), ghi chu phu thuoc build native/wtype vao huong dan chay test.
