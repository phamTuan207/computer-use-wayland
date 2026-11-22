# Batch 10 redteam: tan cong review task 2 step 5 (commit 76d0a56)

Ngay: 22/11/2026. Nguoi redteam: batch 10 redteam task 2, doc lap, chi bao cao, khong sua code, khong sua coord/clone1.md, khong sua coord/clone2.md, khong commit, khong push. File test-w.txt 0-byte duoc de nguyen.

## 1. Pham vi va phuong phap

Doi tuong bi tan cong: `docs/batch10-task2-step5-review-20261122.md`, 13 bug va 1 van de nho (B1-B14), tat ca duoc bao la tai hien 14/14. Code step 5 la commit 76d0a56 tren nhanh todolist-push, chi fetch read-only, khong sua nhanh do. Cay commit giai nen tai `~/workspace/step5review-scratch/tree/scripts`, reproducer goc tai `~/workspace/step5review-scratch/repro/repro_step5.py`.

Phuong phap: chay lai reproducer goc, doc code that cua commit, roi viet cac tan cong rieng de pha tung bug. Moi tan cong deu chay tren code that hoac doc lai duong goi that (caller) trong cay commit. Tan cong rieng nam o `/tmp/redteam_attacks.py`, chay bang `python3 /tmp/redteam_attacks.py`.

Ket qua chay lai reproducer goc:

```
cd ~/workspace/step5review-scratch/repro && python3 repro_step5.py
REPRODUCED 14 of 14 checks
```

Ket qua tan cong rieng (`/tmp/redteam_attacks.py`): A1 chung minh B7 nua dau qua wrapper that, A2 chung minh hinh dang B7 nua sau xuat phat tu code that, A3 chung minh B11 qua ca duong doc `[]`, A4 chung minh B4 qua ca validation that cua code_exec, A5 chung minh B3 mat gate hoan toan, A6 chung minh B8 chay qua duong bubble khi ledger rong.

## 2. Tom tat ket qua

Trong 14 bug, 12 bug SONG SOT (SURVIVES), 2 bug BI PHA (BROKEN).

| Ma | Verdict | Ghi chu |
|----|---------|---------|
| B1 | SURVIVES | Vi pham docstring "never raises", nhung latent, chua co caller production |
| B2 | SURVIVES | Vi pham docstring "never raises", nhung latent, chua co caller production |
| B3 | SURVIVES | Mat gate hoan toan, ca hai Enter deu bi xep sai |
| B4 | SURVIVES | Assert dau chuong trinh van thoa gate, ca validation that cung chap nhan |
| B5 | SURVIVES | Latent, muc thap, docstring hua tra ve nhung code raise |
| B6 | BROKEN | Input tu mau thuan, khong producer nao tao ra, xem muc 4.6 |
| B7 | SURVIVES | Ca hai nua deu co duong that dan toi, xem muc 4.7 |
| B8 | SURVIVES | Duong bubble khi ledger rong khong co test nao bao ve, xem muc 4.8 |
| B9 | SURVIVES | Loi typo ro rang, muc thap, khong consumer doc truong nay |
| B10 | SURVIVES | Truong tu mau thuan, nhung ok van False nen chi anh huong chan doan |
| B11 | SURVIVES | Nua "element bien mat" duoc `[]` cuu, nhung nua unique thi khong, xem muc 4.11 |
| B12 | SURVIVES | Comment "one moment" la sai, strict yeu hon fallback, nhung cua race hep |
| B13 | BROKEN | Khong producer nao tao ok=1, `is True` la kieu chung ca codebase, xem muc 4.13 |
| B14 | SURVIVES | Duong production that khong bao gio ep P5, xem muc 4.14 |

## 3. Luu y chung truoc khi doc chi tiet

Ba phat hien ve caller lam thay doi muc do, khong lam thay doi verdict cua nhieu bug:

- `route_perception` chi co caller la test (`tests/test_step5_p1p5.py`), khong co caller production nao trong cay commit. B1 va B2 vi vay la latent.
- `focus_type` khong co caller production nao trong cay commit, chi co test goi no (`tests/test_click2_redteam.py`, `tests/test_dom_act.py`). Duong send production that chay qua `first_action` fallback va `cu` CLI act, ca hai deu goi truc tiep `cu.desktop_act` voi hooks best-effort (`scripts/first_action.py:830`, `scripts/cu.py:3157`). Dieu nay lam B14 manh hon, va lam B8, B9, B10 thanh bug latent trong ham chua duoc noi vao production.
- `ground_many` chi co caller la test (`tests/test_click2_redteam.py:354`, `tests/test_dom_act.py:338`, `tests/test_dom_act.py:593`). B11 vi vay la latent trong ham chua duoc noi vao production.
- B7 nua dau va B14 la cung mot lo hong goc nhin tu hai lop: B14 la producer, B7 nua dau la hop dong.

## 4. Chi tiet tung bug

### 4.1. B1. Router raise voi target kind khong hash duoc. SURVIVES

Tan cong 1: kiem tra caller that co truyen kind dang list khong. Ket qua: khong co caller production nao trong cay commit, chi co test truyen kind dang str (`tests/test_step5_p1p5.py:39-110`). Tan cong nay khong pha duoc bug, no chi ha muc do xuong latent.

Tan cong 2: doc ky docstring (`scripts/perception_router.py:88-90`): "The router never raises: any unexpected input fails closed to the screenshot fallback with the reason recorded." Code da co y dinh cung co input (`kind = target.get('kind') if isinstance(target, dict) else None`, dong 97) nhung quen mat truong hop kind khong hash duoc, dong 98 `if kind not in _PRIORITY:` raise `TypeError: unhashable type: 'list'`. Reproducer chay lai cho dung output nay. Khong co cach doc nao bien dong nay thanh hanh vi co y dinh.

Verdict: SURVIVES. Muc do trung binh la rong, thuc te la latent vi chua co caller nao truyen kind lac.

### 4.2. B2. Router raise khi emit raise, va khi probes khong phai dict. SURVIVES

Tan cong 1: cho rang probes la tham so co kieu da ghi ro (dict), caller truyen list la loi cua caller. Ket qua: docstring cung hua "any unexpected input fails closed", va code da tu xu ly probe raise trong try (`scripts/perception_router.py:117-124`) nhung lai de `probes.get` (dong 120) va `emit(record)` (dong 149) ngoai moi bao ve. Cung mot ham, mot nua duoc bao ve, mot nua khong, day la cung co do dang, khong phai thiet ke co y.

Tan cong 2: cho rang emit mac dinh chi in ra stderr nen khong the raise. Ket qua: emit la tham so caller truyen vao, bat ky emit nao cung co the raise, va ca emit mac dinh `_default_emit` cung co the raise khi stderr hong. Reproducer chay lai cho dung hai output: `emit-raises: raised RuntimeError: stderr broke` va `probes-list: raised AttributeError: 'list' object has no attribute 'get'`.

Verdict: SURVIVES. Latent nhu B1, chua co caller production nao kich hoat.

### 4.3. B3. Hai Enter giong nhau: Enter gui thu hai bi xep loai sai. SURVIVES

Tan cong 1: kiem tra `_validate_dom_actions` (`scripts/code_exec.py:199-260`) co loai bo action trung lap khong. Ket qua: khong co buoc dedup nao, hai dict Enter giong het nhau deu vuot qua validation (toi da 32 action). Chuong trinh `[Enter, type, Enter]` la hop le o lop validation.

Tan cong 2: chay tan cong rieng A5 tren code that. Ket qua: `assert_for(enter_a)` va `assert_for(enter_b)` deu tra ve exception "a non-send key has no generic DOM postcondition", nghia la ca hai Enter deu bi xep la khong phai send, gate bien mat hoan toan chu khong chi lech mot Enter. Enter thu nhat dung la khong phai send (khong co type dung truoc), nhung Enter thu hai la send that su va cung bi mat gate.

Tan cong 3: kiem tra `focus_type` co bi anh huong khong. Ket qua: `focus_type` tu xay chain chi co mot Enter (`scripts/dom_act.py:595-601`) nen khong bi B3, nhung duong code_exec (`scripts/code_exec.py:887`) thi bi, dung nhu review noi.

Verdict: SURVIVES. Tan cong 2 con cho thay bug nang hon mo ta goc: khong phai mot Enter bi xep sai, ma ca hai Enter deu khong duoc cong nhan la send.

### 4.4. B4. Assert o bat ky vi tri nao cung thoa sent_bubble. SURVIVES

Tan cong 1: kiem tra code_exec co kiem tra rieng vi tri assert o dau khong. Ket qua: chi co truong hop `no_after=True` moi kiem tra assert cuoi (`scripts/code_exec.py:897-909`). Duong thuong (`_api_dom_act`, dong 887) chi goi `require_asserts` va khong kiem tra them gi.

Tan cong 2: chay tan cong rieng A4 tren code that. Ket qua: `_validate_dom_actions` CHAP NHAN `[assert(title), fill, Enter]`, va `require_asserts` cung CHAP NHAN voi `sent_bubble: False`. Bien trong code ten la `has_trailing_assert` nhung dung `any(...)` (`scripts/dom_asserts.py:201-215`), ten bien noi mot dang, code lam mot neo.

Tan cong 3: doc docstring cua module (`scripts/dom_asserts.py:24-30`): "a send program (fill/set_value followed by key Enter) must end with an assert action". Chuong trinh trong reproducer khong ket thuc bang assert ma van pass, trai truc tiep voi cau nay. Assert o dau chuong trinh kiem tra title, chay truoc khi gui, khong the xac minh bubble.

Verdict: SURVIVES. Khong co tan cong nao pha duoc, ca ba lop (docstring, ten bien, validation) deu ung ho review.

### 4.5. B5. assert_for raise ValueError khi key khong co trong danh sach. SURVIVES

Tan cong 1: kiem tra caller that co goi off-list khong. Ket qua: chi co `assert_coverage` va `require_asserts` goi `assert_for`, ca hai deu truyen danh sach co chua action do (`scripts/dom_asserts.py:159-170`, `scripts/dom_asserts.py:193-215`). Khong co caller trong cay commit kich hoat duong nay.

Tan cong 2: doc docstring cua `assert_for` (`scripts/dom_asserts.py:127-135`): "Returns {'action': type, 'assert': name...} for a covered action, or {'action': type, 'exception': reason} for an exception-list action, or None". Docstring hua tra ve, khong he noi raise. Mot ham truy van (query) ma raise `ValueError` khi hoi ve mot action rieng le la trai voi hop dong cua chinh no. Khong co bang chung nao cho thay raise la hanh vi co y dinh.

Verdict: SURVIVES. Latent, muc thap la dung, nhung khong phai false positive.

### 4.6. B6. verified True at ca target_received False, ok van True. BROKEN

Tan cong 1: liet ke moi diem goi `build_contract` trong cay commit va kiem tra to hop nao co the tao ra verified True kem target_received False. Ket qua:

- `scripts/cu.py:1799` (wrapper): verified True chi khi `type_verified is True` va basis la `dom-value`, va cung luc do `target_received` duoc gan True (`scripts/cu.py:1791-1792`).
- `scripts/dom_act.py:620` (already-sent): target_received True.
- `scripts/dom_act.py:713` (click+type): verified True (dom-value) chi khi `type_verified is True`, va khi do `target_received = bool(type_verified)` la True.
- `scripts/dom_act.py:744` (sent-bubble): verified True voi `target_received` lay tu type, chi co the la True hoac None, khong bao gio False khi type pass.
- `scripts/dom_act.py:727` va `:753`: verified la None hoac False.
- `scripts/action_result.py:101-107` (migrate): verified luon None.
- `contract_ok` chi co mot caller duy nhat la `scripts/first_action.py:790`, an session result tu desktop_act da qua wrapper, nen cung khong the tao ra to hop nay.

Khong co producer nao trong cay commit tao ra duoc dict co verified True kem target_received False. Review tu thua nhan dieu nay ("Hien tai chua co producer nao trong step 5 tao ra to hop nay").

Tan cong 2: doc docstring cua `build_contract` (`scripts/action_result.py:51-58`): "ok is True exactly when the intended end state holds: verified is True (the postcondition passed...)". Neu postcondition (sent-bubble) da pass thi bubble ton tai, nghia la target da nhan, nen target_received False trong input la mot khang dinh sai tu caller, khong phai trang thai that. Ham xu ly dung theo dinh nghia da ghi cua chinh no, mau thuan nam o input do reproducer tu tay xay, khong phai o code.

Verdict: BROKEN. Reproducer mock bug vao ton tai bang mot dict tu mau thuan ma khong producer nao tao ra. Cung lam chi con la mot ghi chu cung co phong thu cho caller tuong lai, khong phai bug song.

### 4.7. B7. verified None van pass send; nhanh completed-capture ghi de postcondition da fail. SURVIVES

Tan cong 1 (nua dau): cho rang reproducer dung dict tu xay nen khong chung minh duoc gi. Ket qua: tan cong nay that bai, vi toi chay duoc cung hinh dang do qua wrapper that. Tan cong rieng A1 dung `cu._with_result_contract` voi mot stub tra ve dung nhung gi desktop_act that tra khi band pass (`type_verified` True, basis `input-line-band`, `completed` 3, `ok` True, theo `scripts/cu.py:2393-2394`): output la `ok=True verified=None basis='no-dom-postcondition: pixel band is diagnostic only' input_sent=True` cho mot batch `[click, type, Enter]`, tuc la mot send that khong chay bat ky DOM postcondition nao van bao ok True. Day la producer that, khong phai dict tu xay.

Tan cong 2 (nua sau): kiem tra hinh dang trong reproducer co that su xuat phat tu desktop_act that khong, bang cach doc trace: batch chay het (`completed` bang so action); type_check hook fail sau khi chay xong thi `error_code_override` thanh `type_unverified` (`scripts/cu.py:2180-2190`); after-capture van chay sau do va neu raise thi gan `capture_error`, `ok` False (`scripts/cu.py:2332-2337`) ma khong xoa `error_code`; khoi xac minh type bi bo qua vi khong co `after` (`scripts/cu.py:2349`, dieu kien `if has_type and error is None and 'after' in result`); wrapper anh xa `error_code` type_unverified thanh verified False (`scripts/cu.py:1779-1780`). Tan cong rieng A2 xac nhan `_is_completed_capture` chap nhan dung hinh dang nay, va nhanh o `scripts/first_action.py:774-790` khong nhin `verified` chut nao truoc khi gan envelope ok True. Review da dung o cho nay.

Tan cong 3: doc comment trong nhanh completed-capture (`scripts/first_action.py:784-788`): "The full batch ran but the after-capture failed, so no postcondition ran". Cau nay la sai khi type_check hook da chay va fail truoc after-capture. Comment tu thua nhan nhanh nay dung truoc vi "contract_ok would also pass this shape", nhung no khong xu ly truong hop verified False.

Verdict: SURVIVES ca hai nua. Nua dau co producer that (desktop_act band-only), nua sau co duong trace that dan toi hinh dang do.

### 4.8. B8. Bubble giong het tu truoc lam mat lenh gui moi. SURVIVES

Tan cong 1: cho rang day la hanh vi co y dinh (exactly-once), duoc test R6 ban phuc (`tests/test_click2_redteam.py:397-418`, `test_retry_after_partial_send_must_not_double_send`) va duoc benchmark `send_one` mo ta (`tests/two_vision_bench.py:414-428`, pre-check chay "regardless of ledger status"). Ket qua: tan cong nay chi dung mot nua. Test R6 goi `focus_type` hai lan tren cung session: lan thu hai di qua LEDGER (lan thu nhat da ghi intent sau khi gui thanh cong), nen test do khong bao gio chay qua duong bubble khi ledger rong. `send_one` co `intent_id` de phan biet retry cung intent voi send moi, con `focus_type` khong co intent nao, no ap dung logic retry cung intent cho moi lan gui co cung text. Khong co test nao bao ve duong bubble khi ledger rong nhu mot hanh vi co y dinh.

Tan cong 2: chay tan cong rieng A6. Ket qua: session moi, ledger rong, bubble "hello" co san tu truoc, `focus_type` tra ve `ok=True already_sent=True` ma `act_fn` duoc goi 0 lan. Gui "hello" lan thu hai la hop le trong chat that, nhung tin nhan khong bao gio duoc gui ma van bao thanh cong.

Tan cong 3: kiem tra tac dung phu. Ket qua: duong pre-send bubble con tu ghi intent vao ledger (`scripts/dom_act.py:629-631`, `intents.add((selector, text))`), nen sau mot lan bo lang sai, ledger cung bi nhiem va moi lan thu lai sau do cung se bo qua qua duong ledger.

Verdict: SURVIVES. Co che retry la co y dinh, nhung ap dung no khi ledger rong, khong co intent id, la qua rong va lam mat send moi trung text.

### 4.9. B9. act_observes giu gia tri cu sau batch Enter. SURVIVES

Tan cong 1: kiem tra bien `observes` co duoc gan lai giua hai batch khong. Ket qua: khong. `observes` duoc gan mot lan tu batch click+type (`scripts/dom_act.py:690`), roi dong 722-723 viet `if sent.get('observes') is not None: out['act_observes'] = observes`, dieu kien doc batch Enter nhung phep gan dung bien cu. Day la loi copy ro rang, khong co cach doc nao bien no thanh co y dinh.

Tan cong 2: kiem tra consumer cua truong nay de danh gia muc do. Ket qua: khong co consumer nao ngoai `scripts/dom_act.py`, chi co mot test assert `act_observes` bang 0 o duong already-sent (`tests/test_dom_act.py:434`). Anh huong chi la chan doan sai so observes.

Verdict: SURVIVES. Muc thap la dung, loi typo la that.

### 4.10. B10. Batch Enter fail xoa mat xac minh type da pass. SURVIVES

Tan cong 1: cho rang viet lai la dung vi "send khong chay". Ket qua: code viet lai ca hop dong (`scripts/dom_act.py:724-733`): `input_sent` False, `verified` None, basis "send did not execute", trong khi `completed` van 2 va `target_received` van True tu click+type. Mot dict co `target_received` True di kem `input_sent` False la tu mau thuan theo dinh nghia cua chinh module (`input_sent` la input da duoc gui, `target_received` la target da nhan). Mot postcondition da chay va pass (type_check dom-value) lai bi bao la chua chay (verified None).

Tan cong 2: kiem tra ok cuoi cung co sai khong. Ket qua: ok van False vi `input_sent` False, nen khong co wrong pass. Anh huong that la chan doan: mot vong retry doc `input_sent` False se tuong chua co gi duoc gui, trong khi field da co text.

Verdict: SURVIVES. Muc trung binh la rong, anh huong that o muc thap vi ok van fail-closed, nhung truong tu mau thuan la that.

### 4.11. B11. Duong harvest cua ground_many bo qua CB-5. SURVIVES

Tan cong 1: cho rang `GroundPoints.__getitem__` cuu duoc, vi no re-ground khi rect doi (`scripts/dom_act.py:352-365`). Ket qua: tan cong nay chi cuu duoc mot nua. Nua "element bien mat" trong reproducer goc dung la se bi `__getitem__` chan (locate tra None thi raise DomActError). Nhung tan cong rieng A3 cua toi dung mot session ma locate tra ve cung mot rect khong doi va `locate_confirmed` se tu choi vi unique_count 2: `ground_many` tra ve diem `[110.0, 35.0]` qua ca duong doc `[]` ma `locate_confirmed` duoc goi 0 lan. Guard chi re-ground khi rect doi, no khong bao gio kiem tra unique, stable, interactive khi rect dung yen.

Tan cong 2: kiem tra `harvest` that tra ve nhung gi (`scripts/zen_dom.py:1155-1213`). Ket qua: moi item chi co rect, hit, focused. Khong co visible, interactive, stable, unique. Duong per-element (`ground_input`) chay `confirm_locate` du nam xac nhan, duong one-shot khong chay bat ky xac nhan nao trong bon cai do, hit trong harvest chi bao uncovered tai thoi diem harvest.

Tan cong 3: kiem tra docstring cua `ground_many_one_shot` (`scripts/dom_act.py:366-374`) co hua CB-5 khong. Ket qua: docstring chi hua raise khi selector missing, uncovered, hoac map ngoai image. Nhung `ground_many` (`scripts/dom_act.py:461-476`) gioi thieu hai duong nhu the thay the nhau cho cung mot cong viec, va caller khong co cach nao biet duong one-shot yeu hon. Su khac biet thuc thi la that du docstring cua ham con co viet hep hon.

Verdict: SURVIVES. Phan chung minh manh nhat khong phai "element bien mat" nhu review viet, ma la truong hop unique_count 2 vuot qua ca duong doc `[]` da ghi trong tai lieu.

### 4.12. B12. Strict path khong doc lai rect sau hit_check, diem co the stale. SURVIVES

Tan cong 1: kiem tra comment ma review trich dan. Ket qua: comment ton tai that (`scripts/zen_dom.py:870-873`): "visible, interactive, and uncovered are read in the same evaluate as the rect, so the report describes one moment, not three." Nhung code that noi khac: visible va interactive lay tu evaluate dau tien, uncovered lay tu mot lan goi `hit_check` rieng biet (`scripts/zen_dom.py:943`), va `hit_check` tu doc lai rect bang `getBoundingClientRect` trong evaluate cua rieng no (`scripts/zen_dom.py:827-875`). Comment la sai su that.

Tan cong 2: kiem tra stable co bat duoc chuyen dong khong. Ket qua: khong. Stable so rect lan mot voi rect lan hai (`locate`, `scripts/zen_dom.py:932-939`), ca hai deu doc truoc khi `hit_check` chay. Neu element doi ngay trong luc `hit_check` thi report van tra rect cu voi stable True va uncovered True. Reproducer chay lai cho dung output nay, va duong fallback cua `confirm_locate` thi doc lai locate sau hit_check va re-ground (`scripts/dom_act.py:100-113`), nen strict path yeu hon fallback path dung o cung cho nay.

Tan cong 3: danh gia muc do. Cua race chi la khoang giua hai evaluate lien nhau, element phai doi dung luc do, va duong `ground_many` con co guard `[]` doc lai o thoi diem click. Rieng duong `ground_input` (ma `first_action` fallback goi truc tiep o `scripts/first_action.py:835`) thi khong co guard sau do, nen lo hong van song o duong do. Muc cao la rong, muc trung binh la dung hon.

Verdict: SURVIVES. Comment sai va thieu re-read la that, chi co muc do la noi qua.

### 4.13. B13. Legacy ok=1 bi dich sai thanh input_sent False. BROKEN

Tan cong 1: tim producer nao tao ra ok=1. Ket qua: grep `'ok': 1`, `"ok": 1`, `ok=1` tren toan cay commit khong co ket qua nao lien quan (chi co mot dong dem trong `check-perf-evidence.py:90` voi khoa `ok` la so luong, khong phai result ok). Khong co producer nao tao ra gia tri nay.

Tan cong 2: kiem tra nguon input that cua `migrate_legacy_result`. Ket qua: diem goi duy nhat la `scripts/first_action.py:742`, an `session_result` tu stdout cua session subprocess duoc parse bang JSON (`scripts/first_action.py:691`, `_parse_stdout_envelope`, `json.loads` o dong 238). JSON `true` parse thanh Python `True`, khong bao gio thanh `1`. Ket qua cua desktop_act trong tien trinh cung dung bool that.

Tan cong 3: kiem tra `is True` co phai la khong nhat quan lac long khong. Ket qua: khong. Ca codebase dung `result.get('ok') is True` mot cach nhat quan (10 cho trong `scripts/cu.py`, 1 cho trong `scripts/first_action.py`). Day la kieu strict co y dinh de chi nhan bool that, khong phai loi danh may.

Tan cong 4: xet ca truong hop xau nhat gia su co producer lac tao ok=1. Ket qua: no bi dich thanh ok False, tuc la fail-closed (bao loi thay vi bao pass), khong phai wrong pass. Mot van de chi co the gay bao loi thua thi khong phai bug song.

Verdict: BROKEN. Input gia dinh, khong co producer, kieu strict la co y dinh, va huong sai neu co cung la fail-closed.

### 4.14. B14. desktop_act khong bao gio thuc thi P5, type chi bang pixel van ok True. SURVIVES

Tan cong 1: cho rang pixel band fallback la thiet ke co y dinh, duoc ghi trong docstring cua `open_dom_hooks` ("the caller then falls back to the pixel band instead of failing the batch", `scripts/dom_act.py:541-547`) va lap lai o ca hai caller production (`scripts/cu.py:3157-3162`, `scripts/first_action.py:824-829`). Ket qua: tan cong nay that bai ve mat ket luan, vi thiet ke do mau thuan truc tiep voi P5 ("type_check, mandatory", `scripts/dom_asserts.py:32-36`) va voi CB-1 ("pixel band stays a diagnostic, never a postcondition", `scripts/dom_asserts.py:14-18`). Hai tai lieu thiet ke trong cung commit noi nguoc nhau, va hanh vi that (ok True cho type khong co DOM check) la dung cai P5 duoc tao ra de ngan. Mot fallback duoc ghi ro van co the la bug khi no pha vo quy tac mandatory.

Tan cong 2: chay tan cong rieng A1 qua wrapper that. Ket qua: mot send `[click, type, Enter]` chi bang pixel band cho `ok=True verified=None basis='no-dom-postcondition: pixel band is diagnostic only'`. Reproducer cua review dung fake desktop_act, nhung stub cua toi tra ve dung nhung gi desktop_act that tra khi band pass (`scripts/cu.py:2393-2394`), nen ket qua dung cho code that.

Tan cong 3: kiem tra xem co lop ep nao khac tren duong Zen khong. Ket qua: khong. Khong co caller production nao goi `focus_type` (lop ep duy nhat tren duong Zen), va `require_asserts` chi duoc goi o `focus_type` va `code_exec` (duong Chromium). Duong Zen production (session desktop_act va fallback desktop_act) khong bao gio ep P5.

Verdict: SURVIVES. Day la bug manh nhat cung voi B7, vi no la producer that cua lo hong B7 nua dau.

## 5. Tan cong manh nhat da thu

Tan cong manh nhat la A3 chong lai B11: thay vi dung lai o reproducer goc (fake locate tra None, von duoc guard `[]` cuu mot phan), toi xay mot session ma locate tra ve cung mot rect khong doi va `locate_confirmed` se tu choi vi unique_count 2, roi doc diem qua duong `[]` da ghi trong tai lieu. Ket qua: diem `[110.0, 35.0]` duoc tra ve, `locate_confirmed` duoc goi 0 lan. Tan cong nay that bai trong viec pha B11, nguoc lai no chung minh B11 manh hon ca mo ta goc: duong one-shot khong chi thieu CB-5 o luc ground, ma ca guard doc lai cung khong bao gio kiem tra unique khi rect dung yen.

Tan cong manh thu hai la A1 chong lai B7 nua dau: thay vi dung dict tu xay, toi dua mot ket qua co dung hinh dang desktop_act that tra khi band pass qua wrapper that `cu._with_result_contract` va nhan duoc `ok=True verified=None` cho mot send. No bien mot phan bi nghi la mock thanh mot producer that.

## 6. Ket luan

Review task 2 dung o 12/14 bug. Hai bug bi pha (B6, B13) deu co cung mau: reproducer tu xay mot input ma khong producer nao trong cay commit tao ra, va code xu ly dung theo dinh nghia hoac kieu chung da ghi. Muoi hai bug con lai song sot sau moi tan cong, ke ca khi toi thu dung chinh caller that, validation that, wrapper that, va duong doc da ghi trong tai lieu de pha chung. Nam bug muc cao van dung: B4, B7, B8, B11, B12, voi hai dieu chinh ve muc do: B12 nen ha xuong trung binh vi cua race hep, B11 nen manh hon o phan unique chu khong phai phan element bien mat. Nen sua 5 bug muc cao truoc, roi sua B3, B14 cung goc voi B7, va xem B1, B2, B5 nhu cung co phong thu.
