# Batch 10 task 2: review doc lap step 5 (commit 76d0a56)

Ngay: 22/11/2026. Nguoi review: batch 10 task 2, doc lap, chi bao cao, khong sua code chung, khong commit, khong push.

Sua doi ngay 22/11/2026 theo ket luan cua 3 council va redteam task 2 (docs/batch10-council1-task2-20261122.md, docs/batch10-council2-task2-20261122.md, docs/batch10-council3-task2-20261122.md, docs/batch10-redteam-task2-20261122.md). Moi sua doi deu duoc kiem chung lai truc tiep tu code cua commit 76d0a56 trong cay giai nen tai ~/workspace/step5review-scratch/tree. Ket qua sau sua doi: 14 check reproducer doi chieu thanh 11 root cause rieng biet, trong do 12 check song sot va 2 check bi rut (B6, B13). Chi tiet sua doi nam o docs/batch10-fix-task2-20261122.md.

## 1. Pham vi va xac minh commit

Step 5 duoc review la commit `76d0a56` tren nhanh `todolist-push`, tieu de "C4 step 5: P1 perception router, P5 DOM asserts, CB-1 contract, CB-5 locate confirmations". Commit ton tai, da xac minh bang lenh sau:

```
git fetch origin todolist-push
git cat-file -t 76d0a56
git show --stat 76d0a56
```

Ket qua: `cat-file` tra ve `commit`, hash day du `76d0a5600154aa8c822a3f00434abbc1a51441e2`. Diff co 12 file, 1752 dong them, 98 dong xoa. Cac file moi: `scripts/perception_router.py` (150 dong), `scripts/dom_asserts.py` (227 dong), `scripts/action_result.py` (103 dong), `tests/test_step5_p1p5.py` (561 dong). Cac file sua: `scripts/dom_act.py`, `scripts/zen_dom.py`, `scripts/cu.py`, `scripts/first_action.py`, `scripts/code_exec.py`, `tests/test_dom_act.py`, `tests/test_click2_redteam.py`.

Cach review: giai nen toan bo cay commit ra thu muc tam rieng bang `git archive 76d0a56`, doc het diff (2151 dong), roi chay reproducer tren dung code cua commit do, khong chay tren code cua main. Khong sua nhanh `todolist-push`, khong push.

## 2. Phuong phap va so lieu nen

Linh vuc kiem tra: logic sai, duong nao chua fail-closed, cho nao hop dong CB-1 ba phan chua duoc thuc thi dung, cho nao router dinh tuyen sai coverage.

Lenh kiem tra nen, chay tren cay commit:

```
cd <cay commit>/tree
python3 -m unittest tests.test_step5_p1p5
python3 -m unittest tests.test_dom_act
python3 repro_step5.py
```

Ket qua:

- `tests.test_step5_p1p5`: Ran 37 tests, OK.
- `tests.test_dom_act`: Ran 19 tests, OK.
- `repro_step5.py`: 14/14 check tai hien duoc bug.

Nhu vay 37 test cua step 5 deu pass, nhung cac lo hong duoi day nam ngoai vung phu cua chung. Moi bug duoi day deu co reproducer chay duoc, kem lenh va output that. Ban day du cua tat ca reproducer nam o `~/workspace/step5review-scratch/repro/repro_step5.py`, import tu cay commit o `~/workspace/step5review-scratch/tree/scripts`. Phan 4 trich lai tung reproducer o dang rut gon, du de chay lai khi co them phan fake chung o muc 4.0.

Hieu chinh sau review cua council va redteam (22/11/2026): 14 check reproducer van chay duoc 14/14, nhung chi 12 check song sot thanh bug that. B6 va B13 bi rut vi input cua reproducer khong co producer nao tao ra (xem muc B6 va B13). B3 va B5 la hai trieu chung cua cung mot root cause o `dom_asserts.py:111`, nen gop lai thanh 1 root cause. Vay so root cause rieng biet con lai la 11, trong do 10 nam trong diff cua commit 76d0a56 va 1 (B11) la code co san truoc step 5, ngoai diff nhung van la bug that.

## 3. Tom tat ket qua

Tim thay 11 root cause rieng biet (12 check reproducer song sot, 2 check bi rut), tat ca deu tai hien duoc. Khong tim thay bug nao o phan dinh tuyen co ban (zen-chrome ve screenshot, empty harvest va truncated tree deu fall-through dung), xem muc 5. B11 la code co san truoc step 5, ngoai diff cua commit 76d0a56, nhung van la bug that cua khung CB-5 ma step 5 tuyen bo, nen van dem trong 11 root cause va ghi ro la ngoai pham vi diff. B3 gop ca trieu chung B5 (cung root cause o `dom_asserts.py:111`). B6 va B13 da bi rut, khong dem nua, ly do o muc 4.

| Ma | Ten ngan | Muc do | Trang thai |
|----|----------|--------|------------|
| B1 | Router raise voi target kind khong hash duoc | Trung binh (latent, chua co caller production) | Song sot |
| B2 | Router raise khi emit raise, khi probes khong phai dict | Trung binh (latent, chua co caller production) | Song sot |
| B3 | Hai Enter giong nhau: Enter gui thu hai bi xep loai sai; assert_for raise khi key khong co trong danh sach (gop B5) | Cao | Song sot, gop B5 |
| B4 | Assert o bat ky vi tri nao cung thoa sent_bubble | Cao | Song sot |
| B7 | verified None van pass send chua chay postcondition; nhanh completed-capture ghi de ca postcondition da fail | Cao | Song sot |
| B8 | Bubble giong het tu truoc lam mat lenh gui moi | Cao | Song sot |
| B9 | act_observes giu gia tri cu sau batch Enter | Thap | Song sot |
| B10 | Batch Enter fail xoa mat xac minh type da pass | Thap (chi anh huong chan doan, ok van False) | Song sot |
| B11 | Duong harvest cua ground_many bo qua CB-5 | Cao (ngoai diff, pre-existing, nhung that) | Song sot |
| B12 | Strict path khong doc lai rect sau hit_check, diem co the stale | Trung binh (cua race hep) | Song sot |
| B14 | desktop_act khong bao gio thuc thi P5, type chi bang pixel van ok True | Cao | Song sot |
| B6 | verified True at target_received False, ok van True | Rut | Rut, khong co producer nao tao ra to hop nay |
| B13 | Legacy ok=1 bi dich sai thanh input_sent False | Rut | Rut, khong co producer nao tao ra ok=1 |

Muc do sau hieu chinh: Cao 6 (B3, B4, B7, B8, B11, B14), Trung binh 3 (B1, B2, B12), Thap 2 (B9, B10).

## 4. Chi tiet tung bug

### 4.0. Fake chung dung cho cac reproducer

META va fake session duoi day phong theo dung fake cua chinh test step 5 (`tests/test_step5_p1p5.py`, `FakeSendSession`, `META`).

```python
import sys
sys.path.insert(0, '<cay commit>/tree/scripts')
import dom_act, dom_asserts, action_result
from perception_router import route_perception

META = {'window_bounds': [0, 0, 800, 600], 'monitor_box': [0, 0, 800, 600],
        'image_size': [800, 600], 'region': [0, 0, 800, 600]}

class FakeSendSession:
    def __init__(self, value='', bubble_text=None):
        self.fields = {'#msg-input': {
            'rect': {'x': 10, 'y': 20, 'width': 200, 'height': 30},
            'focused': False, 'value': value, 'covered': False}}
        self.sent_intents = set()
        self.bubble = bubble_text
        self._typed = {}
    def live_window_origin(self, address=None): return None
    def locate(self, selector):
        f = self.fields.get(selector)
        return None if f is None else dict(f['rect'])
    def viewport_origin(self, window_origin=None, window_size=None,
                        monitor_box=None):
        return list(window_origin or [0, 0])
    def hit_check(self, selector):
        f = self.fields.get(selector)
        return bool(f) and not f.get('covered', False)
    def focus_check(self, selector):
        f = self.fields.get(selector)
        return bool(f) and bool(f.get('focused', False))
    def field_value(self, selector):
        f = self.fields.get(selector)
        return None if f is None else f.get('value')
    def arm_typed_flag(self, selector):
        self._typed[selector] = False
        return True
    def note_typed(self, selector): self._typed[selector] = True
    def typed_flag(self, selector): return bool(self._typed.get(selector))
    def verify_typed(self, selector, expected, before=None):
        f = self.fields.get(selector)
        if f is None or f.get('value') != expected: return False
        if before is not None and not self.typed_flag(selector): return False
        return True
    def sent_bubble_contains(self, text):
        return self.bubble is not None and self.bubble == text
```

Ham `act_fn` gia lap `cu.desktop_act`: click thi focus, type thi gan value va ghi trusted event roi chay type_check, Enter thi hien bubble. Batch click+type tra `observes` 2, batch Enter tra `observes` 7, kem `type_verified` True va basis `dom-value` khi check pass.

### B1. Router raise voi target kind khong hash duoc. Muc do: trung binh (latent)

Latent: `route_perception` chi co caller la test (`tests/test_step5_p1p5.py:39-110`), khong co caller production nao trong cay commit, nen chua co duong production nao kich hoat bug nay. Muc do trung binh giu nguyen vi docstring hua router khong bao gio raise.

Vi tri: `scripts/perception_router.py:98`, dong `if kind not in _PRIORITY:`.

Docstring cua `route_perception` noi router khong bao gio raise, moi input bat thuong deu fail-closed ve screenshot. Nhung neu `kind` la mot list thi `kind not in _PRIORITY` raise `TypeError: unhashable type`. Mot target dict lac tu caller co the mang kind dang list.

Reproducer:

```python
out = route_perception({'kind': ['zen-content']}, emit=lambda r: None)
```

Output:

```
TypeError: unhashable type: 'list'
```

Goi y sua: ep kieu hoac kiem tra `kind` co hash duoc va co dang str truoc khi tra trong bang, neu khong thi dat `kind = 'unknown'`.

### B2. Router raise khi emit raise, va khi probes khong phai dict. Muc do: trung binh (latent)

Latent: nhu B1, `route_perception` chi co caller la test trong cay commit, khong co caller production nao kich hoat hai duong raise nay. Muc do trung binh giu nguyen vi docstring hua router khong bao gio raise.

Vi tri: `scripts/perception_router.py:120` (`probes.get(candidate)`) va dong 149 (`emit(record)`).

Cung hop dong "router never raises" nhu B1, nhung co hai duong raise khac. Thu nhat, `emit(record)` nam ngoai moi try, nen mot emit bi hong (stderr gay, emit do caller truyen vao bi loi) se lan ra ngoai. Thu hai, neu caller truyen `probes` dang list thi `probes.get` raise AttributeError.

Reproducer:

```python
def boom(record): raise RuntimeError('stderr broke')
route_perception({'kind': 'zen-content'},
                 probes={'dom-zen': lambda t: {'elements': 3, 'truncated': False}},
                 emit=boom)
route_perception({'kind': 'zen-content'}, probes=[('dom-zen', None)],
                 emit=lambda r: None)
```

Output:

```
emit-raises: raised RuntimeError: stderr broke
probes-list: raised AttributeError: 'list' object has no attribute 'get'
```

Goi y sua: boc `emit(record)` trong try, ghi log loi roi van tra decision; kiem tra `probes` co phai dict khong, neu khong thi coi nhu rong.

### B3. Hai Enter giong nhau: Enter gui thu hai bi xep loai sai, va assert_for raise khi key khong co trong danh sach (gop B5). Muc do: cao

Root cause duy nhat: `scripts/dom_asserts.py:111`, dong `index = actions.index(action)`. B3 va B5 cu la hai trieu chung cua cung mot loi, cung mot cach sua (truyen index tuong minh thay vi goi `actions.index`), nen gop lai thanh mot root cause, dem la 1 thay vi 2. Trieu chung B5 cu: `assert_for` raise ValueError thay vi tra ve ket qua khi key Enter khong nam trong danh sach `actions` truyen vao, trai voi docstring cua no (chi hua tra ve spec, exception, hoac None). Trieu chung nay cung la latent vi chi co `assert_coverage` va `require_asserts` goi `assert_for`, ca hai deu truyen danh sach co chua action do.

Muc do nang len Cao (tu Trung binh): redteam tan cong A5 cho thay khong phai chi Enter thu hai bi xep sai, ma ca hai Enter deu bi xep la khong phai send (`assert_for` tra exception cho ca hai), nen gate sent_bubble bien mat hoan toan, khong chi lech mot Enter. `_validate_dom_actions` (`scripts/code_exec.py:199-260`) khong co buoc dedup nao, chuong trinh `[Enter, type, Enter]` la hop le o lop validation. Cung loai hau qua nhu B4 (gate sent_bubble bat buoc bi bo qua, send khong duoc xac minh van pass), nen cung muc Cao nhu B4.

Vi tri: `scripts/dom_asserts.py:111`, dong `index = actions.index(action)`.

`_is_send_key` dung `actions.index(action)` de tim vi tri cua phim Enter. `list.index` so sanh bang gia tri, nen khi batch co hai dict Enter giong het nhau (hai object khac nhau, cung noi dung) thi Enter thu hai cung tra ve index 0, phan truoc no la danh sach rong, nen no bi xep la key khong phai send. Ket qua: `require_asserts` khong doi sent_bubble cho lan gui that su.

Reproducer:

```python
enter_a = {'type': 'key', 'keys': ['Enter']}
enter_b = {'type': 'key', 'keys': ['Enter']}
actions = [enter_a, {'type': 'type', 'text': 'hi'}, enter_b]
print(dom_asserts.assert_for(enter_b, actions))
dom_asserts.require_asserts(
    actions, available={'focus_check': True, 'type_check': True,
                        'sent_bubble': False})
```

Output:

```
assert_for second Enter: {'action': 'key', 'exception': 'a non-send key has no generic DOM postcondition: ...'}
require_asserts returned: True (sent_bubble NOT demanded for the real send)
```

Doi chung: cung batch nhung chi mot Enter sau type thi `require_asserts` raise dung, noi `key needs mandatory assert sent_bubble`.

Goi y sua: truyen index vao `_is_send_key` thay vi goi `actions.index`, hoac duyet bang `enumerate` trong `assert_coverage` va `require_asserts`.

### B4. Assert o bat ky vi tri nao cung thoa sent_bubble, phai la assert cuoi. Muc do: cao

Vi tri: `scripts/dom_asserts.py:201-215`, `has_trailing_assert = any(...)`.

Docstring noi "a trailing assert action in the program satisfies the sent_bubble requirement". Nhung code dung `any`, nghia la mot assert o bat ky dau trong batch cung thoa. Mot chuong trinh `[assert, fill, key Enter]` se pass `require_asserts` du sent_bubble khong co san, trong khi assert do chay TRUOC khi gui nen khong the xac minh bubble. Day la mat phia code_exec (`scripts/code_exec.py:887` goi dung ham nay voi `sent_bubble: False`): mot chuong trinh gui khong co gate van duoc chap nhan chi vi co mot assert lac dau chuong trinh, ke ca assert do kiem tra thu khac (vi du title).

Reproducer:

```python
actions = [{'type': 'assert', 'check': 'title'},
           {'type': 'fill', 'text': 'hi'},
           {'type': 'key', 'keys': ['Enter']}]
dom_asserts.require_asserts(
    actions, available={'focus_check': True, 'type_check': True,
                        'sent_bubble': False})
```

Output:

```
require_asserts returned True for [assert, fill, Enter] with sent_bubble unavailable
```

Doi chung: cung batch nhung bo assert dau tien thi `require_asserts` raise, noi thieu sent_bubble (test `test_code_exec_send_without_trailing_assert_is_missing` cua step 5 chi cover truong hop khong co assert nao).

Goi y sua: chi chap nhan assert o vi tri cuoi batch, va chi khi assert do kiem tra bubble (kiem tra noi dung cua action assert, khong phai bat ky assert nao).

### B5. (Da gop vao B3, khong dem rieng)

B5 cu (`assert_for` raise ValueError khi key khong co trong danh sach, `scripts/dom_asserts.py:111`) la trieu chung thu hai cua cung root cause voi B3, cung mot dong code, cung mot cach sua. Xem muc B3. Khong dem B5 nhu mot bug rieng nua. Reproducer cu van nam trong `repro_step5.py` (check B5) va van chay duoc:

```python
key = {'type': 'key', 'keys': ['Enter']}
dom_asserts.assert_for(key, [{'type': 'type', 'text': 'hi'}])
```

Output cu:

```
ValueError: {'type': 'key', 'keys': ['Enter']} is not in list
```

### B6. (Rut, khong phai bug) verified True at ca target_received False, ok van True. Muc do cu: trung binh

Rut theo redteam muc 4.6, da kiem chung lai truc tiep tu code. Khong co producer nao trong cay commit tao ra duoc dict co verified True kem target_received False. Danh sach day du cac diem goi `build_contract` trong cay commit (grep `build_contract` tren `scripts/` va `tests/`):

- `scripts/cu.py:1799` (wrapper): verified True chi khi `type_verified is True` va basis la `dom-value`, va cung luc do `target_received` duoc gan True (`scripts/cu.py:1791-1792`).
- `scripts/dom_act.py:620` (already-sent): `target_received=True`.
- `scripts/dom_act.py:713` (click+type): verified True chi khi `type_verified is True`, va khi do `target_received = bool(type_verified)` la True.
- `scripts/dom_act.py:727` (Enter fail): verified None.
- `scripts/dom_act.py:744` (sent-bubble): verified True voi `target_received` lay tu type, chi co the la True hoac None, khong bao gio False khi type pass.
- `scripts/dom_act.py:753` (send unverified): verified False.
- `scripts/action_result.py:98-107` (migrate): verified luon None.
- `scripts/action_result.py:82` (`contract_ok`): tinh lai tu dict truyen vao, nhung caller duy nhat la `scripts/first_action.py:790`, an session result tu desktop_act da qua wrapper, nen cung khong the tao ra to hop nay.
- Test (`tests/test_step5_p1p5.py:214-246`) chi dung to hop nhat quan (verified True chi di kem target_received True).

Docstring cua `build_contract` (`scripts/action_result.py:51-58`) noi verified True nghia la postcondition da pass, ma postcondition pass (sent-bubble ton tai) thi target da nhan, nen target_received False trong input la mot khang dinh sai tu caller, khong phai trang thai that. Reproducer goc tu tay xay mot dict tu mau thuan ma khong producer nao tao ra. Nhanh `if verified is True: ok = True` xu ly dung theo dinh nghia da ghi. Giu lai nhu mot ghi chu cung co phong thu cho caller tuong lai, khong dem la bug.

### B7. verified None van pass send chua chay postcondition; nhanh completed-capture ghi de ca postcondition da fail. Muc do: cao

Vi tri: `scripts/action_result.py`, ham `build_contract` va `contract_ok`; `scripts/first_action.py:774-790`, nhanh completed-capture.

Hai mat cua cung mot lo hong: `verified=None` mang hai nghia chong len nhau, vua la "khong co postcondition nao ap dung" (dung cho scroll, hover) vua la "postcondition bat buoc chua bao gio chay" (send khong co gate). `build_contract` xu ly ca hai giong nhau, cho ok True khi input_sent True. He qua:

- Mot ket qua send co `input_sent` True, `verified` None (khong co DOM check nao chay) duoc `contract_ok` chap nhan la ok True.
- Nhanh completed-capture trong `first_action.run` chay TRUOC nhanh `contract_ok` va khong nhin `verified` chut nao. No chi kiem tra `ok` False, co `capture_error`, va `completed` du so action. Nen mot batch ma type check da FAIL (`verified` False, `error_code` `type_unverified`) nhung tat ca action da chay va after-capture bi loi van duoc bao envelope ok True, verified None.

Reproducer (phan nhanh completed-capture chung minh o muc dieu kien nhanh, khong chay toan bo `run()` vi no can subprocess):

```python
import first_action
send_result = {'ok': True, 'input_sent': True, 'target_received': None,
               'verified': None, 'verified_basis': None, 'completed': 3}
print(action_result.contract_ok(send_result))
cap = {'ok': False, 'capture_error': 'after-capture failed',
       'completed': 3, 'input_sent': True, 'verified': False,
       'type_verified': False, 'error_code': 'type_unverified'}
print(first_action._is_completed_capture(cap, 3))
```

Output:

```
contract_ok(send, verified=None) = True
_is_completed_capture(verified=False, type_unverified) = True
```

Goi y sua: them mot truong vao hop dong phan biet "khong co postcondition" voi "postcondition bat buoc chua chay", vi du `verified_required`; `contract_ok` chi pass verified None khi khong co postcondition bat buoc; nhanh completed-capture phai tu choi khi `verified` la False. Luu y: test `test_verified_none_ok_follows_input_sent` (`tests/test_step5_p1p5.py`) dang khoa chat hanh vi verified None cho ok True, nen cach sua nay se phai doi ca test do.

Ghi chu them: `focus_type` (chu cua B8, B9, B10) khong co caller production nao trong cay commit, chi co test goi no; duong send production that chay qua `first_action` fallback va `cu` CLI act, ca hai deu goi truc tiep `cu.desktop_act`. B7 nua dau va B14 la cung mot lo hong goc nhin tu hai lop: B14 la producer, B7 nua dau la hop dong.

### B8. Bubble giong het tu truoc lam mat lenh gui moi. Muc do: cao

Vi tri: `scripts/dom_act.py:625-635`, phan pre-send V12 read trong `focus_type`.

`focus_type` kiem tra bubble TRUOC khi gui: neu thread DOM da co mot bubble co text giong het thi no tra ve already-sent thanh cong ma khong goi `act_fn` lan nao. Dieu nay dung cho retry sau khi mat ket qua, nhung sai cho lan gui moi co cung noi dung. Gui "hello" hai lan lien tiep la hop le, nhung lan thu hai bi bo lang, bao ok True, `already_sent` True, trong khi thread chi co mot bubble. Ledger `(selector, text)` o dong 625 chi xu ly dung retry that su, con phan pre-send bubble check thi qua rong vi no khong co nonce hay id nao phan biet hai lan gui.

Reproducer: session moi, ledger rong, bubble da co san "hello" tu mot tin truoc, goi `focus_type` gui "hello" lan nua:

```python
session = FakeSendSession(bubble_text='hello')
calls = []
out = dom_act.focus_type(session, _recording_act(session, calls), META,
                         '#msg-input', 'hello', enter=True)
print(out.get('ok'), out.get('already_sent'), len(calls))
```

Output:

```
result ok=True already_sent=True, act_fn called 0 times
```

Goi y sua: chi dung pre-send bubble check khi ledger da ghi intent do (retry that), hoac dem so bubble trung text truoc va sau khi gui thay vi chi kiem tra ton tai.

Latent mot phan: B8 nam trong `focus_type`, ham nay chi co caller la test trong cay commit (xem ghi chu o B7). Khong co test nao bao ve duong bubble khi ledger rong nhu mot hanh vi co y dinh.

### B9. act_observes giu gia tri cu sau batch Enter. Muc do: thap

Latent mot phan: B9 nam trong `focus_type`, ham nay chi co caller la test trong cay commit (xem ghi chu o B7). Khong co consumer nao doc truong `act_observes` ngoai `scripts/dom_act.py`, chi co mot test assert `act_observes` bang 0 o duong already-sent.

Vi tri: `scripts/dom_act.py:722-723`.

Sau batch Enter, code kiem tra `sent.get('observes') is not None` roi gan `out['act_observes'] = observes`, trong do `observes` la bien cua batch click+type truoc do, khong phai cua batch Enter. Day la loi copy, gia tri observes cua batch Enter bi bo qua hoan toan.

Reproducer: batch click+type tra observes 2, batch Enter tra observes 7:

```python
session = FakeSendSession()
calls = []
out = dom_act.focus_type(session, _recording_act(session, calls), META,
                         '#msg-input', 'hello', enter=True)
print(out.get('act_observes'), out.get('ok'))
```

Output:

```
act_observes=2 (click+type batch reported 2, Enter batch reported 7), ok=True
```

Goi y sua: gan `sent.get('observes')` hoac cong don ca hai batch, tuy theo dinh nghia cua truong nay.

### B10. Batch Enter fail xoa mat xac minh type da pass. Muc do: thap (ha tu trung binh)

Muc do ha xuong Thap theo redteam muc 4.10: ok cuoi cung van False vi `input_sent` False, nen khong co wrong pass. Anh huong that chi o muc chan doan: mot vong retry doc `input_sent` False se tuong chua co gi duoc gui, trong khi field da co text. Truong tu mau thuan (`target_received` True di kem `input_sent` False va `verified` None, `completed` 2) la that, nhung chi anh huong chan doan.

Latent mot phan: B10 nam trong `focus_type`, ham nay chi co caller la test trong cay commit (xem ghi chu o B7).

Vi tri: `scripts/dom_act.py:724-733`, nhanh `if sent.get('ok') is not True`.

Khi batch Enter that bai, code viet lai toan bo hop dong thanh `input_sent` False, `verified` None, basis "send did not execute". Nhung click+type da chay xong (`completed` 2) va type check da pass (`target_received` True). Ket qua cuoi cung tu mau thuan noi bo: `completed` 2 va `target_received` True di kem `input_sent` False va `verified` None, trong khi mot postcondition da chay va pass lai bi bao la chua chay.

Reproducer: batch click+type pass, batch Enter tra ok False:

```python
session = FakeSendSession()
calls = []
out = dom_act.focus_type(
    session, _recording_act(session, calls, enter_ok=False), META,
    '#msg-input', 'hello', enter=True)
print(out.get('input_sent'), out.get('target_received'), out.get('verified'),
      out.get('verified_basis'), out.get('completed'))
```

Output:

```
input_sent=False target_received=True verified=None
verified_basis='send did not execute: the Enter batch failed' completed=2
```

Goi y sua: giu nguyen phan hop dong cua click+type (input_sent True, verified True, basis dom-value) va them truong rieng ghi nhan send that bai, thay vi viet de len hop dong.

### B11. Duong harvest cua ground_many bo qua CB-5. Muc do: cao (ngoai diff, pre-existing, nhung that)

Pham vi: NGOAI DIFF cua commit 76d0a56. Ham `ground_many_one_shot` khong co trong diff cua commit 76d0a56: o commit cha no o dong 311, o commit moi o dong 366, khong hunk nao cham toi no (kiem chung: `git diff 76d0a56^ 76d0a56 -- scripts/dom_act.py` cho 0 dong chua chuoi `ground_many_one_shot`). Day la code co san truoc step 5, khong phai loi step 5 dua vao. Bug van dem trong 11 root cause vi no la lo hong that cua khung CB-5 ma step 5 tuyen bo, nhung phai ghi ro la ngoai pham vi diff, khong phai loi step 5 dua vao. Tuyen bo cu o muc 6 ("Chi review code cua commit 76d0a56") da duoc sua lai cho khop o muc 6.

Bo sung tu redteam tan cong A3: phan chung minh manh nhat khong phai "element bien mat" nhu mo ta goc, ma la truong hop unique_count 2 vuot qua ca duong doc `[]` da ghi trong tai lieu. `GroundPoints.__getitem__` chi re-ground khi rect doi, no khong bao gio kiem tra unique, stable, interactive khi rect dung yen. Voi mot session ma `locate()` tra ve cung mot rect khong doi va `locate_confirmed` se tu choi vi unique_count 2, `ground_many` van tra ve diem `[110.0, 35.0]` qua ca duong doc `[]`, `locate_confirmed` duoc goi 0 lan.

Latent: `ground_many` chi co caller la test trong cay commit (`tests/test_click2_redteam.py:354`, `tests/test_dom_act.py:338`, `tests/test_dom_act.py:593`), khong co caller production nao.

Vi tri: `scripts/dom_act.py:366-460`, ham `ground_many_one_shot`.

`ground_input` chay qua `confirm_locate` nen co du nam xac nhan CB-5. Nhung `ground_many_one_shot`, duong harvest mot lan ma docstring goi la dang VISION 1, khong goi `confirm_locate`, khong goi `locate_confirmed`, khong kiem tra visible, interactive, stable, hay unique. No chi kiem tra `hit` trong item harvest. Cung mot ham `ground_many` co hai duong voi muc thuc thi khac nhau: duong per-element thi co CB-5, duong one-shot thi khong.

Reproducer: session co harvest tra rect va hit True, nhung `locate()` tra None (element da bien mat khoi DOM that) va `locate_confirmed` se tu choi vi unique_count 2:

```python
class HarvestSession:
    def __init__(self):
        self.harvest_calls = 0
        self.confirm_calls = []
    def harvest(self, selectors):
        self.harvest_calls += 1
        return {'moz_inner': [0, 0], 'device_pixel_ratio': 1,
                'screen_pixels_per_css_pixel': 1, 'zoom': 1,
                'inner_size': [800, 600], 'outer_size': [800, 600],
                'items': {s: {'rect': {'x': 10, 'y': 20, 'width': 200,
                                       'height': 30, 'center_x': 110,
                                       'center_y': 35},
                            'hit': True, 'focused': False}
                          for s in selectors}}
    def locate(self, selector): return None
    def locate_confirmed(self, selector):
        self.confirm_calls.append(selector)
        return {'rect': {'x': 10, 'y': 20, 'width': 200, 'height': 30,
                         'center_x': 110, 'center_y': 35},
                'visible': True, 'interactive': True, 'uncovered': True,
                'stable': True, 'unique': False, 'unique_count': 2}

session = HarvestSession()
points = dom_act.ground_many(session, META, ['#msg-input'])
print(session.harvest_calls, len(session.confirm_calls), '#msg-input' in points)
```

Output:

```
ground_many returned points for #msg-input; harvest called 1 time(s),
locate_confirmed called 0 time(s) though it would refuse (unique_count 2),
and locate() returns None
```

Luu y: `GroundPoints.__getitem__` co tu kiem tra lai khi doc bang `[]`, nhung ban than `ground_many` tra ve thanh cong cho mot element khong con ton tai, trai voi docstring cua no ("Raises DomActError when any selector is missing, uncovered, or maps outside the image"), va moi caller dung `.get()` se nhan diem stale ma khong co bao ve nao.

Goi y sua: chay `confirm_locate` cho moi selector trong duong one-shot, hoac it nhat kiem tra lai bang `locate()` va so sanh rect truoc khi tra ve.

### B12. Strict path khong doc lai rect sau hit_check, diem co the stale. Muc do: trung binh (ha tu cao)

Muc do ha xuong Trung binh theo redteam muc 4.12: cua race chi la khoang giua hai evaluate lien nhau, element phai doi dung luc `hit_check` chay, va duong `ground_many` con co guard `[]` doc lai o thoi diem click. Rieng duong `ground_input` (ma `first_action` fallback goi truc tiep o `scripts/first_action.py:835`) thi khong co guard sau do, nen lo hong van song o duong do. Comment "one moment" la sai va thieu re-read la that, chi co muc do la noi qua.

Vi tri: `scripts/zen_dom.py:876-945`, ham `locate_confirmed`; `scripts/dom_act.py:55-100`, ham `confirm_locate`.

Comment trong code noi visible, interactive, va uncovered duoc doc trong cung mot evaluate voi rect, "so the report describes one moment, not three". Dieu nay khong dung: uncovered den tu mot lan goi `hit_check` rieng biet, sau lan doc rect thu hai dung cho stable. Thu tu that su la: evaluate 1 lay rect, `locate()` lay rect thu hai de tinh stable, `hit_check()` doc rect thu ba o ben trong. Neu element di chuyen giua lan doc thu hai va hit_check thi hit_check pass o vi tri moi, trong khi report van tra rect cu voi stable True. Diem click tinh tu rect cu la stale. Dang chu y la duong fallback trong `confirm_locate` lai manh hon o dung cho nay: no doc lai `locate()` sau hit_check va re-ground khi rect doi. Nhu vay strict path yeu hon fallback path dung o cuoc dua R7 ma step 5 noi la da chuyen vao `confirm_locate`.

Reproducer: fake ZenSession co rect that A (x 10), lap sang B (x 400) ngay trong luc chay hit_check:

```python
class MovingSession(ZenSession):
    def __init__(self):
        super().__init__(timeout_s=5)
        self.session = 'test-session-id'
        self.live = {'x': 10, 'y': 20, 'width': 200, 'height': 30}
    def _wd(self, method, path, body=None):
        raise AssertionError('transport must not be used in this fake')
    def _rect(self):
        r = dict(self.live)
        r['center_x'] = r['x'] + r['width'] / 2
        r['center_y'] = r['y'] + r['height'] / 2
        return r
    def evaluate(self, script, args=None):
        if 'zen_locate_confirmed' in script:
            return {'rect': self._rect(), 'visible': True, 'enabled': True,
                    'count': 1}
        if 'elementFromPoint' in script:
            self.live = {'x': 400, 'y': 500, 'width': 200, 'height': 30}
            return True
        if 'getBoundingClientRect' in script:
            return self._rect()
        raise AssertionError('unexpected script ' + script[:80])

session = MovingSession()
report = session.locate_confirmed('#msg-input')
after = session.locate('#msg-input')
print(report['rect']['x'], report['stable'], report['uncovered'], after['x'])
```

Output:

```
locate_confirmed returned rect x=10 stable=True uncovered=True,
but a fresh locate() right after returns x=400
```

Doi chung: cung chuyen dong do, duong fallback cua `confirm_locate` tra ve rect x=400 (da re-ground), vi no doc lai locate sau hit_check.

Goi y sua: doc lai rect mot lan nua sau hit_check trong `locate_confirmed` va so sanh voi rect da tra, hoac chuyen hit_check vao cung evaluate voi rect nhu comment da noi.

### B13. (Rut, khong phai bug) Legacy ok=1 bi dich sai thanh input_sent False. Muc do cu: nho

Rut theo redteam muc 4.13, da kiem chung lai truc tiep tu code. Ba diem, moi diem deu co bang chung:

1. Khong co producer nao tao ra ok=1. Grep `'ok': 1`, `"ok": 1`, `ok=1` tren toan cay commit (scripts va tests) cho 0 ket qua lien quan. Ket qua duy nhat gan giong la `scripts/check-perf-evidence.py:90`, mot dong dem voi khoa `ok` la so luong, khong phai result ok.
2. Nguon input that cua `migrate_legacy_result` la stdout JSON. Diem goi duy nhat la `scripts/first_action.py:742`, an `session_result` tu `_parse_stdout_envelope` (`scripts/first_action.py:224-243`, `json.loads` o dong 238). JSON `true` parse thanh Python `True`, khong bao gio thanh `1`. Ket qua cua desktop_act trong tien trinh cung dung bool that.
3. `is True` la kieu chung co y dinh cua ca codebase, khong phai loi danh may. Grep cho 23 cho dung `is True` chi rieng trong `scripts/cu.py` (25 cho trong `cu.py` va `first_action.py` cong lai), cong them `scripts/code_exec.py:912`, `scripts/session_remote.py`, va nhieu cho khac. Day la kieu strict chi nhan bool that.
4. Ngay ca truong hop xau nhat gia su co producer lac tao ok=1, no bi dich thanh ok False, tuc la fail-closed (bao loi thay vi bao pass), khong phai wrong pass. Mot van de chi co the gay bao loi thua thi khong phai bug song.

Ghi chu G6 lien quan: cung mau `is True` o `scripts/cu.py:1806` (`result['ok'] = (result.get('ok') is True) and contract['ok']`) cung chet vi cung ly do. Input cua wrapper la ket qua cua `desktop_act` trong tien trinh, `ok` o do la bool that, khong co producer nao tao ok=1. Neu co thi cung fail-closed nhu tren. Khong phai mot bug rieng, khong them bug moi.

### B14. desktop_act khong bao gio thuc thi P5, type chi bang pixel van ok True. Muc do: cao (nang tu trung binh)

Muc do nang len Cao: B14 la producer that cua lo hong B7 nua dau, tren duong production that. Khong co caller production nao goi `focus_type` (lop ep duy nhat tren duong Zen), va `require_asserts` chi duoc goi o `focus_type` va `code_exec` (duong Chromium). Duong Zen production (session desktop_act va fallback desktop_act, `scripts/cu.py:3157`, `scripts/first_action.py:830`) khong bao gio ep P5. Cung loai hau qua nhu B4 va B7 (gate P5 bat buoc vang mat ma ok van True cho mot send chua chay postcondition), nen cung muc Cao. Ly do co the bien minh cho muc Trung binh cu (wrapper ghi verified None trung thuc voi basis ro rang) khong du, vi ok cuoi cung van True cho mot send khong co DOM check nao.

Vi tri: `scripts/cu.py:1741-1811`, ham `_with_result_contract`, va `scripts/cu.py:1812`, ham `desktop_act`.

`require_asserts` chi duoc goi o hai cho: `focus_type` (`dom_act.py:638`) va code_exec (`code_exec.py:887`). `desktop_act` khong goi no bao gio. Duong CLI act (`cu.py`) va fallback cua first_action chi gan DOM hooks khi co `--dom-selector`, va neu hooks khong mo duoc thi batch van chay voi pixel band nhu cu, ghi ly do roi bao ok. Wrapper `_with_result_contract` danh verified None cho truong hop band-only, nhung hop dong cho ok True vi input_sent True va target khong phai False, roi AND voi ok cu van ra True. Ket qua: mot type action khong co bat ky DOM assert nao van bao thanh cong, dung cai ma P5 noi la mandatory.

Reproducer:

```python
import cu
def fake_desktop_act(env, meta, actions, **kw):
    return {'ok': True, 'completed': 2, 'type_verified': True,
            'type_verified_basis': 'input-line-band', 'focus_verified': True}
wrapped = cu._with_result_contract(fake_desktop_act)
out = wrapped({}, {}, [{'type': 'click', 'x': 1, 'y': 1},
                       {'type': 'type', 'text': 'hi'}])
print(out['ok'], out['verified'], out['verified_basis'])
import inspect
print('require_asserts' in inspect.getsource(cu.desktop_act))
```

Output:

```
ok = True verified = None basis = no-dom-postcondition: pixel band is diagnostic only
require_asserts in desktop_act: False
```

Goi y sua: goi `require_asserts` trong `desktop_act` khi batch co type hoac click va khong co hooks, hoac it nhat de wrapper ha ok xuong False khi mot action thuoc S2 class chay ma khong co DOM check nao.

## 5. Nhung diem da kiem tra va dung

- Router: zen-chrome chi ve screenshot, khong probe nao chuyen duoc no sang DOM. Empty harvest (0 element) va truncated tree deu fall-through. Probe raise duoc coi la backend khong co san, khong raise. Unknown kind ve screenshot. Cac test router cua step 5 cover dung cac truong hop nay.
- Exception list dung chung mot object giua `dom_asserts` va `action_result`, test `test_exception_list_is_shared_with_cb1` xac nhan bang phep `is`.
- Strict path cua `confirm_locate` tu choi dung khi visible, interactive, uncovered, stable, unique fail. Test `LocateConfirmedTests` cover du ca nam.
- `focus_type` tu choi truoc bat ky keystroke nao khi session khong co gate, test `test_send_without_bubble_gate_refuses_before_typing` xac nhan field van rong.
- Duong enter-accepted cu da bien mat, send khong co bubble bao ok False voi error_code `send_unverified`.
- `migrate_legacy_result` khong tu nhan postcondition, verified None, chi chuyen ok cu thanh input_sent.
- Commit message noi delta test +41 (37 test moi + 4 tu commit khac), chay lai tren cay commit cho 37 test step 5 OK va 19 test dom_act OK, khop voi con so nay o pham vi hai file test do.
- Nhanh fallback cua `first_action.py` (G7): nhanh fallback o `scripts/first_action.py:879` doc thang `envelope['ok'] = result.get('ok') is True` ma khong qua `contract_ok`. Da kiem chung la an toan: `result` o day la ket qua cua `cu.desktop_act` goi truc tiep o dong 862-865, ham nay da duoc decorator `_with_result_contract` (`scripts/cu.py:1741`) gan `ok` bang `(ok cu is True) and contract ok`, nen `ok` o day da qua contract. Khong phai bug, chi la diem bao phu bo sot truoc day.
- Duong fallback cua `confirm_locate` va diem nho o `focus_type` (G8): duong fallback kiem tra visible chi bang width va height khac 0 (`scripts/dom_act.py`, ham `confirm_locate`), khong kiem tra display hay visibility nhu duong strict (`scripts/zen_dom.py`, `locate_confirmed` kiem tra `display !== 'none'` va `visibility !== 'hidden'`). Da kiem chung: day khong phai mot lo hong song, vi fallback chay `hit_check` (elementFromPoint) ngay sau do, va mot element `visibility:hidden` khong the pass hit_check. Muc do thap, va fallback da ghi ro yeu hon (interactive va unique de None voi basis 'unprobed'). Diem nho cung cho: `focus_type` dung `hasattr(session, 'sent_bubble_contains')` (`scripts/dom_act.py:607`) ma khong kiem tra callable, neu thuoc tinh ton tai nhung khong goi duoc thi loi goi o dong 629 va 741 se raise TypeError. Khong phai bug thuc te vi ZenSession co method that, va `confirm_locate` cung cho lam dung mau (`getattr` roi kiem tra `callable`). Ghi lai nhu ghi chu phong thu, khong dem la bug moi.

## 6. Gioi han cua review

- Khong co live browser (khong co Zen, Chromium, Marionette o day), nen cac reproducer dung fake session phong theo fake cua chinh test step 5. Cac bug ve JS trong `locate_confirmed` (B12) duoc chung minh o muc thu tu goi evaluate, khong phai bang click that tren trinh duyet.
- B7 nua sau (nhanh completed-capture) duoc chung minh o muc dieu kien nhanh dung ham that `_is_completed_capture`, khong chay toan bo `first_action.run()` vi no can subprocess va session that.
- Pham vi: chu yeu review code cua commit 76d0a56. Ngoai le duy nhat la B11 (`ground_many_one_shot`), code co san truoc step 5, ngoai diff, duoc review vi no la lo hong cua khung CB-5 ma step 5 tuyen bo, va da ghi ro la ngoai diff o muc B11. Khong review cac commit truoc hoac sau no tren todolist-push, tru viec doc diff de hieu ngu canh.
- File `tests/test_click2_redteam.py` (G1): diff chi them 10 dong, hai ham `_enter` trong lop R5EnterOrderingTests. Lop R5 co dung 2 test (`test_successful_send_must_not_fail_verification`, `test_retry_after_partial_send_must_not_double_send`, dong 367 va 395), pass 2/2 theo lan chay cua council 3. Toan file Ran 71 tests, FAILED (errors=64), tat ca 64 loi deu la RuntimeError `private wtype helper is missing` tu `scripts/cu.py:106`, vi binary `scripts/native/wtype` khong co trong cay giai nen, va cung khong co trong checkout main (kiem chung: thu muc `scripts/native/` khong ton tai o ca hai noi). Day la loi moi truong, khong phai hoi quy do step 5. Lan sua nay khong chay lai file test do (khong chay code cua repo), chi kiem chung bang cach doc file test, doc dong gay loi o `cu.py:103-106`, va kiem tra su ton tai cua binary; con so pass va loi lay tu lan chay cua council 3.
- File `improvements/worker-click4-step5-p1p5-log.md` (G2): log dai 230 dong, tuyen bo full suite Ran 2022, failures 0, errors 1, skipped 17, trong 214.513s, loi duy nhat la loi g++ -std=c++26 setUpClass pre-existing o test_cursor_file, va delta +41 phan tich thanh +37 test step 5 va +4 test bench-manifest (log dong 195-217). Tuyen bo nay CHUA DUOC KIEM CHUNG LAI bang mot lan chay full suite doc lap trong review nay; chi doc log va ghi lai dung nhung gi log noi. Danh dau la unverified cho den khi co lan chay lai.
- Khong sua bat ky file code chung nao, khong commit, khong push, khong sua coord, file `test-w.txt` 0-byte duoc de nguyen.

## 7. Ket luan

Step 5 xay dung dung khung P1, P5, CB-1, CB-5 va 37 test cua no deu pass, nhung khung do co 11 root cause rieng biet con song sot sau kiem tra cua 3 council va redteam (12 check reproducer song sot tren 14 check, B6 va B13 bi rut, B3 va B5 gop lai thanh 1). Trong 11 root cause, 10 nam trong diff cua commit 76d0a56 va 1 (B11) la code co san truoc step 5, ngoai diff nhung van that. Muc do sau hieu chinh: Cao 6 (B3, B4, B7, B8, B11, B14), Trung binh 3 (B1, B2, B12), Thap 2 (B9, B10). Dang chu y nhat: mot assert lac dau chuong trinh van thoa gate gui (B4), mot send chua tung chay postcondition van duoc bao ok (B7, voi producer that la B14), mot lan gui moi trung text cu bi bo lang (B8), duong harvest bo qua toan bo xac nhan CB-5 (B11, manh nhat o phan unique_count 2 vuot qua ca guard doc lai), va hai Enter giong nhau lam mat hoan toan gate gui (B3). Khuyen nghi sua 6 bug muc cao truoc khi coi step 5 la xong, roi chay lai toan bo reproducer o muc 4 de xac nhan.
