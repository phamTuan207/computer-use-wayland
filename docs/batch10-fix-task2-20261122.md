# Batch 10 fix task 2: sua review step 5 theo ket luan cua council va redteam

Ngay: 22/11/2026. Nguoi sua: batch 10 fix agent task 2. Chi sua file review `docs/batch10-task2-step5-review-20261122.md`, khong sua code chung, khong sua coord/clone1.md, khong sua coord/clone2.md, khong commit, khong push. File `test-w.txt` 0-byte duoc de nguyen.

## 1. Phuong phap kiem chung

Step 5 la commit `76d0a56` tren nhanh `todolist-push`. Da xac minh commit ton tai:

```
git fetch origin todolist-push
git cat-file -t 76d0a56
```

Ket qua: `commit`, hash day du `76d0a5600154aa8c822a3f00434abbc1a51441e2`.

Luu y ve cach kiem chung o lan sua nay: sau lenh fetch dau tien, he thong bao mot canh bao rui ro thuc thi doi voi noi dung cua repo, nen lan sua nay khong chay lai reproducer (`repro_step5.py`) va khong chay lai bat ky test suite nao (khong chay code cua repo). Moi diem sua doi deu duoc kiem chung truc tiep bang cach doc file trong cay giai nen tai `~/workspace/step5review-scratch/tree` va bang grep tim kiem van ban (chi doc, khong thuc thi code). Cac con so chay test (37 test step 5 OK, 19 test dom_act OK, R5 pass 2/2, 64 loi wtype) lay tu lan chay cua council 1, 2, 3 va redteam, va da duoc doi chieu lai bang cach doc code lien quan. Cac lenh grep va output that nam o tung muc duoi day.

## 2. Cac sua doi da ap dung (10/10 muc trong brief)

### 2.1. B6 rut (redteam BROKEN)

Ly do rut: khong co producer nao trong cay commit tao ra duoc dict co verified True kem target_received False. Reproducer goc tu tay xay mot dict tu mau thuan.

Bang chung tu kiem chung truc tiep, grep `build_contract` tren `scripts/` va `tests/`:

```
scripts/action_result.py:36: def build_contract(...)
scripts/action_result.py:82: return build_contract(  (contract_ok)
scripts/action_result.py:98,100: build_contract(...)  (migrate, verified luon None)
scripts/cu.py:1799: contract = action_result.build_contract(  (wrapper)
scripts/dom_act.py:620: build_contract(...)  (already-sent)
scripts/dom_act.py:713: build_contract(...)  (click+type)
scripts/dom_act.py:727: build_contract(...)  (Enter fail, verified None)
scripts/dom_act.py:744: build_contract(...)  (sent-bubble)
scripts/dom_act.py:753: build_contract(...)  (send unverified, verified False)
scripts/first_action.py:790: action_result.contract_ok(session_result)
```

Doc tung diem goi trong cay giai nen:

- `scripts/cu.py:1799`: verified True chi khi `type_verified is True` va basis la `dom-value`, va cung luc do `target_received` duoc gan True o dong 1791-1792.
- `scripts/dom_act.py:620` (already-sent): `target_received=True`.
- `scripts/dom_act.py:713` (click+type): verified True chi khi `type_verified is True`, va khi do `target_received = bool(type_verified)` la True.
- `scripts/dom_act.py:727`: verified None. `scripts/dom_act.py:753`: verified False.
- `scripts/dom_act.py:744` (sent-bubble): verified True voi `target_received` lay tu type, chi co the la True hoac None, khong bao gio False khi type pass.
- `scripts/action_result.py:98-107` (migrate): verified luon None.
- `contract_ok` chi co mot caller duy nhat la `scripts/first_action.py:790`, an session result tu desktop_act da qua wrapper, nen cung khong the tao ra to hop nay.
- Test (`tests/test_step5_p1p5.py:214-246`) chi dung to hop nhat quan (verified True chi di kem target_received True).

Docstring cua `build_contract` (`scripts/action_result.py:51-58`) noi verified True nghia la postcondition da pass, ma postcondition pass (sent-bubble ton tai) thi target da nhan, nen target_received False trong input la mot khang dinh sai tu caller, khong phai trang thai that. Da sua muc B6 trong review thanh "Rut, khong phai bug", giu lai nhu mot ghi chu cung co phong thu, khong dem la bug.

### 2.2. B13 rut (redteam BROKEN)

Ly do rut: khong co producer nao tao ra ok=1, `is True` la kieu chung co y dinh cua ca codebase, va huong sai neu co cung la fail-closed.

Bang chung:

1. Grep `'ok': 1`, `"ok": 1`, `ok=1` tren toan cay commit (scripts va tests) cho 0 ket qua lien quan. Ket qua duy nhat gan giong la `scripts/check-perf-evidence.py:90`, mot dong dem voi khoa `ok` la so luong, khong phai result ok.
2. Diem goi duy nhat cua `migrate_legacy_result` la `scripts/first_action.py:742`, an `session_result` tu `_parse_stdout_envelope` (`scripts/first_action.py:224-243`, `json.loads` o dong 238). JSON `true` parse thanh Python `True`, khong bao gio thanh `1`. Ket qua cua desktop_act trong tien trinh cung dung bool that.
3. `is True` la kieu chung: grep dem 23 cho dung `is True` chi rieng trong `scripts/cu.py`, 25 cho trong `cu.py` va `first_action.py` cong lai, cong them `scripts/code_exec.py:912`, `scripts/session_remote.py`, va nhieu cho khac.
4. Truong hop xau nhat gia su co producer lac tao ok=1: no bi dich thanh ok False, tuc la fail-closed, khong phai wrong pass.

Da sua muc B13 trong review thanh "Rut, khong phai bug". Da sua bang tom tat o muc 3 va ket luan o muc 7 cho khop.

### 2.3. G4: B3 va B5 gop lai thanh mot root cause

Bang chung: ca hai deu o `scripts/dom_asserts.py:111`, dong `index = actions.index(action)` trong `_is_send_key`. Da doc truc tiep dong nay trong cay giai nen. B3 (Enter thu hai bi xep loai sai) va B5 (assert_for raise ValueError khi key khong co trong danh sach) la hai trieu chung cua cung mot loi, cung mot cach sua (truyen index tuong minh thay vi goi `actions.index`). Council 3 xac nhan cac cap khac khong trung (B1/B2 o dong khac nhau, B6/B7 o nhanh khac nhau, B9/B10 o dong khac nhau).

Da sua: muc B3 trong review nay gop ca trieu chung B5, muc B5 doi thanh "Da gop vao B3, khong dem rieng" nhung van giu lai reproducer cu de truy vet. So root cause rieng biet giam tu 14 check xuong 13 truoc khi rut B6/B13, va xuong 11 sau khi rut.

### 2.4. G3: B11 ngoai diff, nhung van la bug that, khong bo

Bang chung ve pham vi, kiem chung truc tiep:

```
git diff 76d0a56^ 76d0a56 -- scripts/dom_act.py | grep -c "ground_many_one_shot"
0
git show 76d0a56^:scripts/dom_act.py | grep -n "def ground_many_one_shot"
311:def ground_many_one_shot(session, meta, selectors):
git show 76d0a56:scripts/dom_act.py | grep -n "def ground_many_one_shot"
366:def ground_many_one_shot(session, meta, selectors):
```

Ham nay khong co trong diff cua commit 76d0a56, chi doi so dong tu 311 sang 366. Day la code co san truoc step 5, khong phai loi step 5 dua vao.

Khong bo bug: redteam tan cong A3 manh hon ca mo ta goc, da chung minh B11 that. `GroundPoints.__getitem__` chi re-ground khi rect doi, khong bao gio kiem tra unique, stable, interactive khi rect dung yen. Voi mot session ma `locate()` tra ve cung mot rect khong doi va `locate_confirmed` se tu choi vi unique_count 2, `ground_many` van tra ve diem `[110.0, 35.0]` qua ca duong doc `[]`, `locate_confirmed` duoc goi 0 lan. Da doc truc tiep `ground_many_one_shot` (`scripts/dom_act.py:366-460`) trong cay giai nen: ham chi kiem tra `item.get('hit')`, khong goi `confirm_locate` hay `locate_confirmed`.

Da sua: muc B11 ghi ro "ngoai diff, pre-existing, nhung that", muc 6 sua tuyen bo pham vi cho khop (chu yeu review code commit 76d0a56, ngoai le duy nhat la B11), muc 3 va muc 7 ghi ro trong 11 root cause co 10 trong diff va 1 ngoai diff.

### 2.5. G5: muc do nhat quan, cong dieu chinh cua redteam

Da ap dung day du:

- B3 nang tu Trung binh len Cao. Ly do: redteam tan cong A5 cho thay ca hai Enter deu bi xep la khong phai send, gate sent_bubble bien mat hoan toan, khong chi lech mot Enter. `_validate_dom_actions` (`scripts/code_exec.py:199-260`) khong co buoc dedup nao, chuong trinh `[Enter, type, Enter]` la hop le o lop validation. Cung loai hau qua nhu B4 (gate sent_bubble bat buoc bi bo qua, send khong duoc xac minh van pass), nen cung muc Cao nhu B4.
- B14 nang tu Trung binh len Cao. Ly do: B14 la producer that cua lo hong B7 nua dau, tren duong production that. Khong co caller production nao goi `focus_type`, `require_asserts` chi duoc goi o `focus_type` va `code_exec`, duong Zen production (session desktop_act va fallback desktop_act) khong bao gio ep P5. Cung loai hau qua nhu B4 va B7, nen cung muc Cao.
- B12 ha tu Cao xuong Trung binh. Ly do theo redteam: cua race chi la khoang giua hai evaluate lien nhau, element phai doi dung luc `hit_check` chay, va duong `ground_many` con co guard `[]` doc lai o thoi diem click. Rieng duong `ground_input` (ma `first_action` fallback goi truc tiep o `scripts/first_action.py:835`) thi khong co guard sau do, nen lo hong van song o duong do.
- B10 ha tu Trung binh xuong Thap. Ly do: ok cuoi cung van False vi `input_sent` False, nen khong co wrong pass. Anh huong that chi o muc chan doan.
- B1, B2, B5 danh dau latent. Bang chung ve caller, grep tren cay commit: `route_perception` chi co caller la test (`tests/test_step5_p1p5.py:39-110`), khong co caller production nao trong `scripts/`. `focus_type` khong co caller production nao trong `scripts/`, chi co test goi no (`tests/test_step5_p1p5.py:375,404,410`, `tests/test_dom_act.py:452`). `ground_many` chi co caller la test (`tests/test_click2_redteam.py:354`, `tests/test_dom_act.py:338`, `tests/test_dom_act.py:593`). Da ghi latent vao muc B1, B2, va muc B3 (cho trieu chung B5), dong thoi ghi chu o muc B7 rang B8, B9, B10 cung nam trong `focus_type` nen cung latent mot phan, nhung khong ha muc cua B8 vi no la bug that tren duong send da ghi trong tai lieu.

Muc do sau hieu chinh: Cao 6 (B3, B4, B7, B8, B11, B14), Trung binh 3 (B1, B2, B12), Thap 2 (B9, B10).

### 2.6. G6: mau is True o cu.py:1806, khong phai bug rieng

Bang chung: da doc truc tiep `scripts/cu.py:1799-1806` trong cay giai nen. Dong 1806 la `result['ok'] = (result.get('ok') is True) and contract['ok']` trong wrapper `_with_result_contract`. Input cua wrapper la ket qua cua `desktop_act` trong tien trinh, `ok` o do la bool that, khong co producer nao tao ok=1 (cung bang chung grep o muc 2.2, 0 ket qua lien quan). Neu co mot ket qua lac voi ok=1 thi dong nay cho ok False, tuc la fail-closed nhu B13. Ket luan: chet vi cung ly do nhu B13, khong phai mot bug rieng, khong them bug moi. Da ghi ket luan nay vao muc B13 trong review.

### 2.7. G1: file tests/test_click2_redteam.py, them ghi chu

Bang chung doc truc tiep, khong chay test:

- Lop `R5EnterOrderingTests` o dong 366, co dung 2 test: `test_successful_send_must_not_fail_verification` (dong 367) va `test_retry_after_partial_send_must_not_double_send` (dong 395). Pass 2/2 theo lan chay cua council 3.
- Dong gay loi: `scripts/cu.py:103-106`, ham `_wtype_executable` raise `RuntimeError('private wtype helper is missing: ' + str(helper))` khi file `native/wtype` khong ton tai.
- Kiem tra su ton tai cua binary: `ls` thu muc `scripts/native/` cho "No such file or directory" o ca cay giai nen lan checkout main. Vay 64 loi la loi moi truong, khong phai hoi quy do step 5.
- Con so toan file (Ran 71, errors=64) lay tu lan chay cua council 3, khong chay lai o lan sua nay (ly do o muc 1). Da ghi ro nguon cua con so trong review de khong gia vo nhu da chay lai.

Da them ghi chu G1 vao muc 6 cua review.

### 2.8. G2: improvements log, danh dau unverified

Bang chung doc truc tiep: file `improvements/worker-click4-step5-p1p5-log.md` dai 230 dong (dem bang `wc -l`). Dong 195-217 tuyen bo full discover Ran 2022 tests trong 214.513s, FAILED (errors=1, skipped=17), failures 0, loi duy nhat la loi g++ -std=c++26 setUpClass pre-existing o test_cursor_file, va delta +41 phan tich thanh +37 test step 5 va +4 test bench-manifest.

Ket luan: tuyen bo nay CHUA DUOC KIEM CHUNG LAI bang mot lan chay full suite doc lap trong review nay, vi lan sua nay khong chay test suite. Da ghi vao muc 6 cua review la unverified, chi ghi lai dung nhung gi log noi, khong xac nhan them.

### 2.9. G7: nhanh fallback cua first_action.py, an toan, them ghi chu

Bang chung doc truc tiep trong cay giai nen:

- Nhanh fallback o `scripts/first_action.py:879`: `envelope['ok'] = result.get('ok') is True`, doc thang ok ma khong qua `contract_ok`.
- `result` o day la ket qua cua `cu.desktop_act` goi truc tiep o dong 862-865 trong cung nhanh fallback.
- `desktop_act` da duoc decorator `_with_result_contract` (`scripts/cu.py:1741`), gan `ok` bang `(ok cu is True) and contract ok` o dong 1806, nen `ok` o day da qua contract.

Ket luan: an toan, khong phai bug, chi la diem bao phu bo sot truoc day. Da them ghi chu nay vao muc 5 cua review.

### 2.10. G8: confirm_locate fallback visible check va hasattr o focus_type

Bang chung doc truc tiep trong cay giai nen:

- Duong fallback cua `confirm_locate` (`scripts/dom_act.py`): visible chi la `bool(rect.get('width')) and bool(rect.get('height'))`, khong kiem tra display hay visibility nhu duong strict. Duong strict (`scripts/zen_dom.py`, `locate_confirmed`): visible la `width and height and display !== 'none' and visibility !== 'hidden'`.
- Ket luan: khong phai lo hong song. Fallback chay `hit_check` (elementFromPoint) ngay sau visible check, va mot element `visibility:hidden` khong the pass hit_check. Muc do thap, va fallback da ghi ro yeu hon (interactive va unique de None voi basis 'unprobed').
- Diem nho o `focus_type`: `has_gate = hasattr(session, 'sent_bubble_contains')` o `scripts/dom_act.py:607`, roi goi thang o dong 629 va 741 ma khong kiem tra callable. Neu thuoc tinh ton tai nhung khong goi duoc thi loi goi se raise TypeError. Khong phai bug thuc te vi ZenSession co method that, va `confirm_locate` cung cho lam dung mau (`getattr` roi kiem tra `callable`). Ghi lai nhu ghi chu phong thu, khong dem la bug moi.

Da them ca hai ghi chu nay vao muc 5 cua review.

## 3. So lieu cuoi cung (tu tinh lai)

- Check reproducer: 14 check, 12 song sot, 2 rut (B6, B13).
- Root cause rieng biet: 11 (14 check tru 1 do B3/B5 gop lai, tru 2 do B6/B13 rut).
- Trong 11 root cause: 10 nam trong diff cua commit 76d0a56, 1 (B11) la code co san truoc step 5, ngoai diff nhung van that.
- Muc do: Cao 6 (B3, B4, B7, B8, B11, B14), Trung binh 3 (B1, B2, B12), Thap 2 (B9, B10). Tong 6 + 3 + 2 = 11, khop.
- File review sau sua: 549 dong (truoc sua 536 dong, tang 13 dong rong).
- File bao cao sua doi nay: xem so dong o ban giao.

## 4. Nhung gi khong thay doi va ly do

- 12 bug song sot (B1, B2, B3, B4, B7, B8, B9, B10, B11, B12, B14, cong trieu chung B5 trong B3) khong thay doi noi dung, chi thay doi muc do o B3, B10, B12, B14 nhu muc 2.5 va them ghi chu latent, pham vi. Ly do: council 1 xac nhan 5/5 bug muc cao, council 2 xac nhan 9/9 bug con lai, redteam xac nhan 12/14 song sot, khong co bang chung moi de thay doi noi dung cua chung.
- B11 khong bo. Ly do: redteam tan cong A3 chung minh manh hon ca mo ta goc (unique_count 2 vuot qua ca guard doc lai), chi sua pham vi thanh ngoai diff.
- Khong them bug moi. Ly do: G6 chet vi cung ly do nhu B13, G8 visible check duoc hit_check cuu nen khong phai lo hong song, diem hasattr chi la ghi chu phong thu. Khong co reproducer cho bat ky bug moi nao.
- Khong sua coord/clone1.md, coord/clone2.md, khong commit, khong push, khong sua code chung. File `test-w.txt` 0-byte duoc de nguyen.
- Ghi chu ve test `test_verified_none_ok_follows_input_sent` (khoa chat hanh vi verified None cho ok True) duoc them vao muc B7 cua review theo ghi chu nho cua council 3, vi cach sua B7 se phai doi ca test do. Day la ghi chu, khong phai bug moi.

## 5. Han che con lai

- Lan sua nay khong chay lai reproducer va khong chay lai test suite (ly do o muc 1). Cac con so chay test trong review van lay tu lan chay cua council va redteam, da doi chieu bang cach doc code.
- Tuyen bo full suite Ran 2022 trong improvements log van chua duoc kiem chung lai, da danh dau unverified trong review.
