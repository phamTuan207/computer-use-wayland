# Batch 10 council 2: kiem tra 9 bug muc trung binh, thap va nho cua task 2

Ngay: 22/11/2026. Pham vi: chi kiem tra 9 bug B1, B2, B3, B5, B6, B9, B10, B13, B14 trong `docs/batch10-task2-step5-review-20261122.md`. Khong sua code, khong sua coord, khong commit, khong push. File `test-w.txt` 0-byte duoc de nguyen.

## 1. Phuong phap

Step 5 la commit `76d0a56` tren nhanh `todolist-push`. Cay commit giai nen tai `~/workspace/step5review-scratch/tree`, reproducer day du tai `~/workspace/step5review-scratch/repro/repro_step5.py`. Da doi chieu hash sha256 cua 5 file trong cay giai nen voi `git show 76d0a56:<file>`, ket qua MATCH cho ca 5 file: `scripts/perception_router.py`, `scripts/dom_asserts.py`, `scripts/action_result.py`, `scripts/dom_act.py`, `scripts/cu.py`. Vay reproducer chay dung code cua commit 76d0a56.

Lenh chay toan bo:

```
cd ~/workspace/step5review-scratch/repro && python3 repro_step5.py
```

Ket qua: `REPRODUCED 14 of 14 checks`. Sau do chay rieng tung ham reproducer cho 9 bug duoc giao, bang lenh:

```
cd ~/workspace/step5review-scratch/repro && python3 -c "import repro_step5 as r; print(r.b1())"
```

(tuong tu cho b2, b3, b5, b6, b9, b10, b13, b14). Ca 9 deu tra ve True, nghia la tai hien duoc. Ngoai reproducer, council doc truc tiep code trong cay commit de xac nhan co che tung bug.

## 2. Ket qua tong hop

| Ma | Ten ngan | Muc do | Ket luan |
|----|----------|--------|----------|
| B1 | Router TypeError voi target kind dang list | Trung binh | CONFIRMED |
| B2 | Router raise khi emit raise va probes khong phai dict | Trung binh | CONFIRMED |
| B3 | Enter thu hai giong het bi xep loai sai | Trung binh | CONFIRMED |
| B5 | assert_for ValueError khi key khong co trong danh sach | Thap | CONFIRMED |
| B6 | verified True at target_received False, ok van True | Trung binh | CONFIRMED |
| B9 | act_observes giu gia tri cu sau batch Enter | Thap | CONFIRMED |
| B10 | Batch Enter fail xoa mat xac minh type da pass | Trung binh | CONFIRMED |
| B13 | Legacy ok=1 bi dich sai thanh input_sent False | Nho | CONFIRMED |
| B14 | desktop_act khong bao gio goi require_asserts | Trung binh | CONFIRMED |

Ket luan chung: 9/9 bug duoc xac nhan, khong co bug nao khong tai hien, khong co reproducer nao loi.

## 3. Chi tiet tung bug

### B1. Router TypeError voi target kind dang list. CONFIRMED.

Co che trong code: `scripts/perception_router.py:98`, dong `if kind not in _PRIORITY:`. Docstring cua `route_perception` noi router khong bao gio raise, moi input bat thuong deu fail-closed ve screenshot. Nhung `kind` la list thi phep `in` tren dict can hash, nen raise TypeError truoc khi den duoc nhanh fail-closed.

Lenh:

```
python3 -c "import repro_step5 as r; print(r.b1())"
```

Output:

```
(True, "route_perception raised TypeError: unhashable type: 'list' (docstring: router never raises)")
```

Reproducer goc: `route_perception({'kind': ['zen-content']}, emit=lambda r: None)`.

### B2. Router raise khi emit raise va khi probes khong phai dict. CONFIRMED.

Co che trong code: hai duong raise nam ngoai moi try. Thu nhat, `scripts/perception_router.py:120`, dong `probe = probes.get(candidate)`, neu `probes` la list thi raise AttributeError. Thu hai, dong 149, `emit(record)` nam ngoai try, nen emit bi hong se lan ra ngoai. Ca hai deu vi pham hop dong "router never raises" trong docstring.

Lenh:

```
python3 -c "import repro_step5 as r; print(r.b2())"
```

Output:

```
(True, "emit-raises: raised RuntimeError: stderr broke; probes-list: raised AttributeError: 'list' object has no attribute 'get' (docstring: router never raises)")
```

Reproducer goc goi `route_perception` voi emit raise RuntimeError, roi voi `probes=[('dom-zen', None)]`. Ca hai truong hop deu raise.

### B3. Hai Enter giong nhau: Enter gui thu hai bi xep loai sai. CONFIRMED.

Co che trong code: `scripts/dom_asserts.py:111`, dong `index = actions.index(action)` trong `_is_send_key`. `list.index` so sanh bang gia tri, nen Enter thu hai co cung noi dung voi Enter thu nhat cung tra ve index 0, phan truoc no la danh sach rong, khong co type nao, nen no bi xep la key khong phai send. `require_asserts` vi vay khong doi sent_bubble cho lan gui that su.

Lenh:

```
python3 -c "import repro_step5 as r; print(r.b3())"
```

Output:

```
(True, "assert_for(second Enter) = {'action': 'key', 'exception': 'a non-send key has no generic DOM postcondition: a shortcut may legitimately change nothing observable'}; require_asserts returned True (sent_bubble NOT demanded)")
```

Reproducer goc: batch `[Enter, type 'hi', Enter]` voi hai dict Enter giong het nhau, `assert_for` cho Enter thu hai tra exception thay vi spec send, `require_asserts` tra True trong khi `sent_bubble` khong co san.

### B5. assert_for raise ValueError khi key khong co trong danh sach. CONFIRMED.

Co che trong code: cung dong `scripts/dom_asserts.py:111`, `actions.index(action)` nhu B3. `assert_for` duoc ghi la tra ve spec, exception, hoac None, nhung neu action khong nam trong danh sach thi `index` raise ValueError thay vi tra ve ket qua.

Lenh:

```
python3 -c "import repro_step5 as r; print(r.b5())"
```

Output:

```
(True, "assert_for raised ValueError: {'type': 'key', 'keys': ['Enter']} is not in list (actions.index, no membership check)")
```

Reproducer goc: `assert_for({'type': 'key', 'keys': ['Enter']}, [{'type': 'type', 'text': 'hi'}])`.

### B6. verified True at ca target_received False, ok van True. CONFIRMED.

Co che trong code: `scripts/action_result.py:58`, nhanh `if verified is True: ok = True`. Nhanh nay bo qua hoan toan `target_received`, nen mot hop dong tu mau thuan van cho ok True.

Lenh:

```
python3 -c "import repro_step5 as r; print(r.b6())"
```

Output:

```
(True, "build_contract(...) = {'input_sent': True, 'target_received': False, 'verified': True, 'verified_basis': 'sent-bubble', 'ok': True}")
```

Reproducer goc: `build_contract(input_sent=True, target_received=False, verified=True, verified_basis='sent-bubble')`.

### B9. act_observes giu gia tri cu sau batch Enter. CONFIRMED.

Co che trong code: `scripts/dom_act.py:670`, dong `observes = result.get('observes')` lay observes cua batch click+type. Sau batch Enter, dong 722-723 viet:

```
if sent.get('observes') is not None:
    out['act_observes'] = observes
```

Dieu kien kiem tra `sent.get('observes')` cua batch Enter, nhung gia tri gan lai la bien `observes` cu cua batch click+type. Day la loi copy, gia tri observes cua batch Enter bi bo qua.

Lenh:

```
python3 -c "import repro_step5 as r; print(r.b9())"
```

Output:

```
(True, 'act_observes=2 (click+type batch reported 2, Enter batch reported 7; line assigns the old value) ok=True')
```

Reproducer goc: batch click+type tra observes 2, batch Enter tra observes 7, ket qua cuoi `act_observes=2` thay vi 7.

### B10. Batch Enter fail xoa mat xac minh type da pass. CONFIRMED.

Co che trong code: `scripts/dom_act.py:724-733`, nhanh `if sent.get('ok') is not True:`. Khi batch Enter that bai, code viet lai toan bo hop dong thanh `input_sent` False, `verified` None, basis `'send did not execute: the Enter batch failed'`, trong khi `target_received` True tu batch click+type van giu nguyen va `completed` van la 2. Ket qua cuoi tu mau thuan: type check da pass nhung hop dong lai bao postcondition chua chay.

Lenh:

```
python3 -c "import repro_step5 as r; print(r.b10())"
```

Output:

```
(True, "input_sent=False target_received=True verified=None verified_basis='send did not execute: the Enter batch failed' completed=2 (type postcondition passed, then the contract was rewritten)")
```

Reproducer goc: batch click+type pass, batch Enter tra ok False, ket qua cuoi co `input_sent` False di kem `target_received` True va `completed` 2.

### B13. Legacy ok=1 bi dich sai thanh input_sent False. CONFIRMED.

Co che trong code: `scripts/action_result.py:87` trong `contract_ok` (`return result.get('ok') is True`) va dong 101 trong `migrate_legacy_result` (`input_sent=result.get('ok') is True`). Ca hai dung `is True` thay vi truthiness, trong khi `build_contract` dung `bool()`. Mot result cu co `ok` la 1 (int) bi dich thanh input_sent False va ok False, mac du 1 la gia tri true hop le.

Lenh:

```
python3 -c "import repro_step5 as r; print(r.b13())"
```

Output:

```
(True, 'migrate_legacy_result({ok: 1}) input_sent=False; contract_ok({ok: 1}) = False (is True, not truthiness)')
```

Reproducer goc: `migrate_legacy_result({'ok': 1})` va `contract_ok({'ok': 1})`. Anh huong thuc te thap vi JSON parse ra bool that, nhung day la khong nhat quan trong cung mot module.

### B14. desktop_act khong bao gio thuc thi P5, type chi bang pixel van ok True. CONFIRMED.

Co che trong code: grep `require_asserts` tren cay commit cho thay chi hai noi goi: `scripts/dom_act.py:638` (trong `focus_type`) va `scripts/code_exec.py:887`. `scripts/cu.py` khong co lan goi nao, ham `desktop_act` tai `scripts/cu.py:1812` khong goi `require_asserts`. Wrapper `_with_result_contract` tai `scripts/cu.py:1741` danh verified None cho truong hop band-only voi basis `'no-dom-postcondition: pixel band is diagnostic only'`, nhung `build_contract` cho ok True khi input_sent True va target_received khong phai False, roi AND voi ok cu van ra True. Ket qua: mot type action khong co bat ky DOM assert nao van bao thanh cong.

Lenh:

```
python3 -c "import repro_step5 as r; print(r.b14())"
```

Output:

```
(True, "pixel-only type: ok=True verified=None basis='no-dom-postcondition: pixel band is diagnostic only'; require_asserts in desktop_act source: False (only focus_type and code_exec call it)")
```

Reproducer goc: fake desktop_act tra `type_verified` True voi basis `'input-line-band'`, batch click+type qua wrapper cho `ok=True`, `verified=None`, va `inspect.getsource(cu.desktop_act)` khong chua chuoi `require_asserts`.

## 4. Gioi han

Khong co live browser, cac reproducer dung fake session phong theo fake cua chinh test step 5. Chi kiem tra 9 bug duoc giao, khong kiem tra lai B4, B7, B8, B11, B12. Khong sua code, khong commit, khong push.
