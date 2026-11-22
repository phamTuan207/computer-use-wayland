# Batch 10 council 3: kiem tra phuong phap va bao phu cua review task 2 (step 5)

Ngay: 22/11/2026. Doi tuong: docs/batch10-task2-step5-review-20261122.md (536 dong), review commit 76d0a56 tren nhanh todolist-push. Council 3 chi kiem tra phuong phap va bao phu, khong sua code, khong commit, khong push, khong sua coord, file test-w.txt 0-byte duoc de nguyen.

## 1. Ket luan

METHOD GAPS. Phuong phap nen cua review la tot (so lieu nen dung, 14 reproducer deu chay duoc, trich dan dong dung), nhung co 8 khoang trong bao phu va van de phuong phap liet ke o muc 4. Khong co khoang trong nao lam sai lech ket qua nen, nhung 3 van de (G3, G4, G5) lam sai lech cach dem va muc do cua review, va 2 file trong diff khong co bang chung duoc xet.

## 2. Phuong phap cua council 3

- Fetch read-only origin/todolist-push, xac minh commit 76d0a56 ton tai, hash day du 76d0a5600154aa8c822a3f00434abbc1a51441e2.
- So sanh cay giai nen tai ~/workspace/step5review-scratch/tree voi commit bang diff tung file, ca 12 file deu khop.
- Chay lai hai suite nen tren cay commit: python3 -m unittest tests.test_step5_p1p5, python3 -m unittest tests.test_dom_act.
- Chay lai toan bo ~/workspace/step5review-scratch/repro/repro_step5.py.
- Chay them tests.test_click2_redteam tren cay commit (file test thu ba cua diff ma review khong chay).
- Doc het diff (git show 76d0a56, 2151 dong), doc het 3 file moi (perception_router.py, dom_asserts.py, action_result.py) va cac hunk sua o dom_act.py, zen_dom.py, cu.py, first_action.py, code_exec.py, doi chieu tung trich dan dong, ten test va mo ta fake cua review voi code that.
- Kiem tra them cdp.mjs (ngoai diff) vi chu thich o code_exec.py dua vao no.

## 3. So lieu nen: da xac minh, dung

- Diff commit 76d0a56: 12 file, 1752 dong them, 98 dong xoa. git show 76d0a56 cho 2151 dong, khop con so 2151 cua review. (git diff rieng cho 2111 dong, chenh lech la header commit, khong phai loi cua review.)
- Cay giai nen khop commit o ca 12 file, gom ca improvements/worker-click4-step5-p1p5-log.md.
- tests.test_step5_p1p5: Ran 37 tests, OK. Dung nhu review noi.
- tests.test_dom_act: Ran 19 tests, OK. Dung nhu review noi.
- repro_step5.py: REPRODUCED 14 of 14 checks. Ca 14 bug B1-B14 deu tai hien duoc tren cay commit, khong co bug nao chi la ly thuyet.
- File moi: perception_router.py 150 dong, dom_asserts.py 227 dong, action_result.py 103 dong, tests/test_step5_p1p5.py 561 dong. Khop muc 1 cua review.

## 4. Nhung diem review lam dung (da xac minh tung diem)

- Trich dan dong deu dung: perception_router.py:98 (if kind not in _PRIORITY), :120 (probes.get), :149 (emit); dom_asserts.py:111 (actions.index), :201-215 (has_trailing_assert); action_result.py:58 (if verified is True), :87 va :101 (is True); dom_act.py:722-723 (act_observes), :724-733 (nhanh Enter fail), :366-460 (ground_many_one_shot); zen_dom.py:876 (locate_confirmed); cu.py:1741 (_with_result_contract), :1812 (desktop_act); code_exec.py:887 (require_asserts); first_action.py:774 (_is_completed_capture).
- Ten test trich dan deu ton tai va noi dung khop mo ta: test_code_exec_send_without_trailing_assert_is_missing (dong 190), test_exception_list_is_shared_with_cb1 (dong 205, dung assertIs), test_send_without_bubble_gate_refuses_before_typing (dong 392).
- FakeSendSession va META o muc 4.0 cua review giong het fake trong tests/test_step5_p1p5.py (sent_bubble_contains dung phep ==, META giong het), nen cac reproducer khong bi lech do fake tu che.
- B11 dung ve mat ky thuat: ground_many_one_shot chi kiem tra item.get('hit'), khong goi confirm_locate hay locate_confirmed; duong per-element qua ground_input thi co CB-5 vi ground_many goi ground_input khi session khong co harvest.
- B7 dung ve thu tu nhanh: nhanh completed-capture dung truoc contract_ok trong first_action.py, va _is_completed_capture chi kiem tra ok False, capture_error la str, completed du so action, khong nhin verified.
- B4 doi chung dung: test_code_exec_send_without_trailing_assert_is_missing chi cover truong hop khong co assert nao.
- Dem 5 bug muc cao (B4, B7, B8, B11, B12) khop bang o muc 3 cua review.

## 5. Khoang trong bao phu va van de phuong phap

### G1. File tests/test_click2_redteam.py khong co bang chung duoc xet

Vi tri: diff 10 dong them o tests/test_click2_redteam.py, hai ham _enter trong lop R5EnterOrderingTests. Review chi liet ke ten file o muc 1, khong noi gi ve noi dung diff, khong chay file test nay. Council chay tren cay commit: lop R5EnterOrderingTests pass 2/2. Toan file: Ran 71 tests, FAILED (errors=64), tat ca 64 loi deu la RuntimeError: private wtype helper is missing: .../native/wtype, la loi moi truong (binary native khong co trong cay giai nen, cung thieu o checkout main), khong phai hoi quy do step 5. Ket luan: khong co bug an o file nay theo bang chung hien co, nhung tuyen bo "doc het diff" cua review khong co bang chung cho file nay.

### G2. File improvements/worker-click4-step5-p1p5-log.md khong duoc xet

Vi tri: diff 230 dong them o improvements/worker-click4-step5-p1p5-log.md. Review khong thao luan noi dung log. Tuyen bo full suite trong log va commit message (Ran 2022, failures 0, errors 1, skipped 17) khong duoc review kiem chung lai. Review co noi dung o muc 5 khi chi khang dinh so lieu "o pham vi hai file test do", dieu do trung thuc, nhung log van la 1 trong 12 file cua diff ma review bo qua.

### G3. B11 nam ngoai pham vi tuyen bo cua review

Vi tri: scripts/dom_act.py:366-460, ham ground_many_one_shot. Ham nay khong co trong diff cua commit 76d0a56: o commit cha no o dong 311, o commit moi o dong 366, khong hunk nao cham toi no. Muc 6 cua review noi "Chi review code cua commit 76d0a56", mau thuan voi B11. Bug la that (da tai hien, council xac nhan bang code va reproducer), va no dung la lo hong cua khung CB-5 ma step 5 tuyen bo, nhung review phai ghi ro day la code co san truoc step 5, khong phai loi step 5 dua vao. Cach dem "14 bug cua step 5" vi vay noi qua so loi step 5 dua vao. Can sua: ghi B11 la pre-existing, ngoai diff.

### G4. B3 va B5 trung goc, khong phai hai bug rieng biet

Vi tri: scripts/dom_asserts.py:111, dong index = actions.index(action). B3 (Enter thu hai bi xep loai sai) va B5 (assert_for raise ValueError khi key khong co trong danh sach) la hai trieu chung cua cung mot loi, cung mot cach sua (truyen index tuong minh thay vi goi actions.index). So loi rieng biet theo goc la 13, khong phai 14, cu the la 12 bug + 1 van de nho (B13). Cac cap khac khong trung: B1/B2 o dong khac nhau va cach sua khac nhau, B6/B7 o nhanh khac nhau trong build_contract, B9/B10 o dong khac nhau trong focus_type.

### G5. Muc do khong nhat quan giua cac bug cung loai hau qua

- B3 xep Trung binh trong khi B4 xep Cao, trong khi ca hai deu la cua gui sent_bubble bi bo qua: require_asserts tra True trong khi sent_bubble khong co san, send khong duoc xac minh van pass. Cung loai hau qua, muc do khac nhau, review khong dua ly do phan biet.
- B14 xep Trung binh trong khi B4 va B7 xep Cao, trong khi ca ba deu la gate P5 bat buoc vang mat ma ok van True. Review khong dua ly do phan biet. Co mot ly do co the bien minh cho B14 (wrapper ghi verified None trung thuc voi basis ro rang, trong khi B7 ghi de ca postcondition da fail), nhung review khong viet ly do nay.
- Cac muc do con lai nhat quan: B1, B2, B6, B10 Trung binh la hop ly, B5, B9 Thap la hop ly, B13 Nho la hop ly, B4, B7, B8, B11, B12 Cao la hop ly theo hau qua.

### G6. B13 bo sot cung mau is True o cu.py:1806

Vi tri: scripts/cu.py:1806, dong result['ok'] = (result.get('ok') is True) and contract['ok'] trong _with_result_contract. Dong nay dung cung mau is True nhu B13, nhung B13 chi neu action_result.py:87 va :101. Mot ket qua desktop_act co ok la 1 (int) cung bi doc sai o wrapper nay (ok thanh False). Goi y sua cua B13 (dung bool) khong bao cu.py. Day la diem thuc thi cung chu de ma review bo sot.

### G7. Nhanh fallback cua first_action.py khong duoc xet

Vi tri: scripts/first_action.py, khoang dong 880 tren cay commit, dong envelope['ok'] = result.get('ok') is True trong nhanh fallback. Nhanh nay doc thang ok ma khong qua contract_ok, trong khi B7 chi xet nhanh completed-capture va contract_ok. Council kiem chung nhanh nay an toan vi result luon tu cu.desktop_act, da duoc decorator _with_result_contract gan ok voi contract, nen ok o day da qua contract. Day la ket luan cua council, khong phai cua review. Khong phai bug, nhung la diem bao phu thieu.

### G8. Duong fallback cua confirm_locate va mot diem nho o focus_type khong duoc xet

Vi tri: scripts/dom_act.py, ham confirm_locate, duong fallback. Kiem tra visible o fallback chi la width va height khac 0, khong kiem tra display hay visibility nhu duong strict, nen mot element visibility:hidden se pass visible o fallback. Review chi xet duong strict o muc 5. Muc do thap vi fallback da ghi ro yeu hon (interactive va unique de None voi basis 'unprobed'). Diem nho cung cho: focus_type dung hasattr(session, 'sent_bubble_contains') ma khong kiem tra callable, neu thuoc tinh ton tai nhung khong goi duoc thi loi goi se raise TypeError; khong phai bug thuc te vi ZenSession co method that.

## 6. Ghi chu nho (khong tinh la khoang trong)

- Review tin loi chu thich o code_exec.py rang cdp.mjs tu thuc thi focus_check va type_check, khong kiem chung. Council kiem chung: set_value luon lam native-setter write va read-back verification o scripts/cdp.mjs:503-521, kiem tra document.activeElement o :536-537. Khong co bug an o day.
- Hanh vi raise voi action type khong biet trong require_asserts khong duoc review neu, council doc code thay dung (raise DomAssertError).
- Test test_verified_none_ok_follows_input_sent khoa chat hanh vi verified None cho ok True, nen cach sua B7 (them truong verified_required) se phai doi ca test nay; review khong neu diem nay.
- Review noi "doc het diff (2151 dong)": git show 76d0a56 cho 2151 dong, khop, khong phai loi dem.

## 7. Khuyen nghi

- Sua B11 thanh pre-existing, ngoai diff cua step 5, hoac ghi ro pham vi review rong hon muc 6.
- Ghi chu B3 va B5 chung mot goc (dom_asserts.py:111), so loi rieng biet la 13, hoac dua ly do giu cach dem 14 theo trieu chung.
- Xep lai B3 len Cao, hoac dua ly do giu Trung binh so voi B4; tuong tu cho B14 so voi B4 va B7.
- Mo rong B13 sang cu.py:1806.
- Ghi them ket qua kiem tra cho tests/test_click2_redteam.py (R5 pass 2/2, 64 loi moi truong do thieu native/wtype), improvements log, nhanh fallback cua first_action.py, va duong fallback cua confirm_locate, de tuyen bo "doc het diff" co du bang chung.
