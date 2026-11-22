# Batch 10 council 1: kiem tra 5 bug muc cao cua task 2 (step 5)

Ngay: 22/11/2026. Council 1, chi kiem tra, khong sua code, khong commit, khong push, khong sua coord.

## 1. Pham vi

Kiem tra doc lap 5 bug muc cao trong `docs/batch10-task2-step5-review-20261122.md`: B4, B7, B8, B11, B12. Step 5 la commit `76d0a56` tren nhanh `todolist-push`.

## 2. Phuong phap va xac minh commit

Chay reproducer tren dung code cua commit, khong chay tren code cua main. Cay commit duoc giai nen san o `~/workspace/step5review-scratch/tree/scripts`, reproducer day du o `~/workspace/step5review-scratch/repro/repro_step5.py`.

Xac minh commit va cay trich xuat:

```
git fetch origin todolist-push
git cat-file -t 76d0a56
```

Ket qua: `cat-file` tra ve `commit`, hash day du `76d0a5600154aa8c822a3f00434abbc1a51441e2`, tieu de "C4 step 5: P1 perception router, P5 DOM asserts, CB-1 contract, CB-5 locate confirmations".

Kiem tra toan ven cay trich xuat bang sha256 cua 5 file lien quan so voi `git show 76d0a56:scripts/<file>`: `dom_asserts.py`, `action_result.py`, `dom_act.py`, `first_action.py`, `zen_dom.py` deu MATCH.

Chay rieng 5 reproducer:

```
cd ~/workspace/step5review-scratch/repro
python3 -c "import repro_step5 as r; r.check('B4 ...', r.b4); r.check('B7 ...', r.b7); r.check('B8 ...', r.b8); r.check('B11 ...', r.b11); r.check('B12 ...', r.b12)"
```

Chay them toan bo script de doi chieu:

```
python3 repro_step5.py
```

Ket qua doi chieu: toan bo script cho `REPRODUCED 14 of 14 checks`, khop voi con so trong doc review.

## 3. Ket qua tom tat

| Ma | Ket luan |
|----|----------|
| B4 | CONFIRMED |
| B7 | CONFIRMED |
| B8 | CONFIRMED |
| B11 | CONFIRMED |
| B12 | CONFIRMED |

Ket qua: 5/5 bug muc cao duoc xac nhan. Khong co bug nao NOT REPRODUCED.

## 4. Chi tiet tung bug

### B4. Assert o bat ky vi tri nao cung thoa sent_bubble. CONFIRMED

Co che doc trong code: `scripts/dom_asserts.py:201`, dong `has_trailing_assert = any(...)`. Comment o tren noi "trailing assert", nhung code dung `any`, nghia la mot assert o bat ky dau trong batch cung thoa, ke ca assert chay truoc khi gui va kiem tra thu khac.

Lenh:

```
python3 -c "import repro_step5 as r; r.check('B4 any-position assert satisfies send', r.b4)"
```

Output:

```
REPRODUCED B4 any-position assert satisfies send
    require_asserts returned True for [assert, fill, Enter] with sent_bubble unavailable; the assert ran BEFORE the send, so it cannot verify the bubble (code_exec surface)
```

Nhan xet: batch `[assert title, fill, key Enter]` pass `require_asserts` du `sent_bubble` khong co san. Mo ta trong doc review la dung.

### B7. verified None van pass send chua chay postcondition; nhanh completed-capture ghi de ca postcondition da fail. CONFIRMED

Co che doc trong code, hai mat:

- `scripts/action_result.py:63`, nhanh verified None: `ok = input_sent and target_received is not False`. Mot send co `input_sent` True, `verified` None, `target_received` None cho ok True, du khong co postcondition nao chay.
- `scripts/first_action.py:254`, ham `_is_completed_capture` chi kiem tra `ok` False, co `capture_error` dang str, va `completed` bang so action. Ham khong nhin `verified` chut nao. Nhanh dung ham nay o `first_action.py:774-790` dat `envelope['ok'] = True` truoc nhanh `contract_ok`.

Lenh:

```
python3 -c "import repro_step5 as r; r.check('B7 verified None passes unverified send', r.b7)"
```

Output:

```
REPRODUCED B7 verified None passes unverified send
    contract_ok(send, verified=None) = True; _is_completed_capture(verified=False, type_unverified) = True, so the first_action completed-capture branch sets envelope ok True over a FAILED postcondition
```

Nhan xet: ca hai mat deu tai hien dung nhu doc review mo ta. Mat thu hai chi chung minh o muc dieu kien nhanh dung ham that `_is_completed_capture`, khong chay toan bo `first_action.run()`, giong gioi han ma doc review da ghi.

### B8. Bubble giong het tu truoc lam mat lenh gui moi. CONFIRMED

Co che doc trong code: `scripts/dom_act.py:625-631` trong `focus_type`. Dong 625 kiem tra ledger `(selector, text)` truoc, dong 629 kiem tra `session.sent_bubble_contains(text)`. Neu bubble da co san thi tra ve `_already_sent_result()` ma khong goi `act_fn` lan nao. Khong co nonce hay id nao phan biet mot lan gui moi trung text voi mot retry that su.

Lenh:

```
python3 -c "import repro_step5 as r; r.check('B8 identical bubble skips fresh send', r.b8)"
```

Output:

```
REPRODUCED B8 identical bubble skips fresh send
    result ok=True already_sent=True, act_fn called 0 times (fresh session, empty intent ledger; the second "hello" was never sent)
```

Nhan xet: session moi, ledger rong, bubble "hello" da co san tu truoc, gui "hello" lan nua bi bo lang nhung bao ok True, already_sent True. Mo ta trong doc review la dung.

### B11. Duong harvest cua ground_many bo qua CB-5. CONFIRMED

Co che doc trong code: `scripts/dom_act.py:366-460`, ham `ground_many_one_shot`. Ham chi kiem tra `item` co rect va `item.get('hit')` o dong 445, khong goi `confirm_locate`, khong goi `locate_confirmed`, khong kiem tra visible, interactive, stable, hay unique. `ground_many` o dong 461 re sang duong one-shot nay khi session co `harvest`. Trong khi do duong per-element `ground_input` co chay `confirm_locate` day du.

Lenh:

```
python3 -c "import repro_step5 as r; r.check('B11 harvest path skips CB-5', r.b11)"
```

Output:

```
REPRODUCED B11 harvest path skips CB-5
    ground_many returned points for #msg-input; harvest called 1 time(s), locate_confirmed called 0 time(s) though it would refuse (unique_count 2), and locate() returns None
```

Nhan xet: `ground_many` tra diem cho mot element ma `locate()` tra ve None (da bien mat khoi DOM that) va `locate_confirmed` se tu choi vi unique_count 2. Mo ta trong doc review la dung.

### B12. Strict path khong doc lai rect sau hit_check, diem co the stale. CONFIRMED

Co che doc trong code: `scripts/zen_dom.py:876-945`, ham `locate_confirmed`. Thu tu that su la: evaluate 1 lay rect, dong 929 `second = self.locate(selector)` lay rect thu hai de tinh stable, dong 943 `'uncovered': bool(self.hit_check(selector))` moi chay hit_check. Rect tra ve la rect cua evaluate 1. Khong co lan doc rect nao sau hit_check. Neu element di chuyen trong luc hit_check chay thi report van tra rect cu voi stable True va uncovered True. Duong fallback cua `confirm_locate` o `scripts/dom_act.py:111` manh hon o dung cho nay: no doc lai `locate()` sau hit_check va re-ground khi rect doi.

Lenh:

```
python3 -c "import repro_step5 as r; r.check('B12 strict path stale after hit_check', r.b12)"
```

Output:

```
REPRODUCED B12 strict path stale after hit_check
    locate_confirmed returned rect x=10 stable=True uncovered=True, but a fresh locate() right after returns x=400; the point from the report is stale and no post-hit re-read caught it; fallback path on the same movement returned rect x=400 (re-grounded)
```

Nhan xet: chuyen dong gia lap trong luc hit_check chay (rect tu x 10 sang x 400) khong bi strict path phat hien, trong khi duong fallback tren cung chuyen dong tra ve rect x 400 da re-ground. Mo ta trong doc review la dung.

## 5. Ket luan

Ca 5 bug muc cao B4, B7, B8, B11, B12 deu CONFIRMED bang reproducer chay duoc tren dung code commit 76d0a56, kem co che doc truc tiep trong code. Khong co bug nao trong 5 bug nay la NOT REPRODUCED. Khuyen nghi sua ca 5 bug truoc khi coi step 5 la xong, roi chay lai toan bo reproducer de xac nhan.
