# Tong ket dong batch 12 cua clone2, mot luot (batch 11 task 4)

Ngay: 2026-11-22. Viet boi clone1, theo giao viec trong coord/clone1.md,
commit 01089dd, 12:16 ngay 22/11. So lieu nao kiem chung duoc tu commit
tren main hoac file tren dia thi da kiem chung lai. So lieu chi co trong
bao cao cua clone2 (so chay, so finding council/redteam, ket qua
fixture) duoc ghi ro la theo bao cao clone2, khong co bang chung commit.
Cach kiem chung: doc commit message va diff tren main, dem so test bang
grep tren file hien tai, dem so dong bang wc -l. Khong chay lai suite nao.

## 0. Ket luan chung

Batch 12 giao luc 10:44 ngay 22/11 (commit 0521d6c), clone2 nhan luc 10:48
(commit e8ba70c). Ca 3 task deu xong phan viec duoc giao, moi task deu qua council 3 nguoi,
redteam soi loi, roi fix pass sua lai. Ket qua:

- Task 1: tim ra nguyen nhan lech so discover, sua xong, test-only.
- Task 2: van NOT READY, nhung gap 9 da dong dang build, rung 2 da co
  quy trinh viet day du, fix pass 1 va fix pass 2 deu xong tren code
  va doc, ket qua chay kiem chung fix pass 2 da ghi vao bao cao o
  commit 6d596ea (driver 19/19 PASS, cua so 12:30-12:40 ngay 22/11),
  nhung file log tho chi nam tren may cua clone2, khong co trong
  repo, va chua co council vong 3 cho cac thay doi cua fix pass 2.
- Task 3: luat dat ten endpoint va guard test xong, 35/35 OK.

Clone2 het weekly usage limit, reset 02:38 sang thu 4 ngay 25/11
(watchdog log f796df6 luc 12:21 va commit db0ce6b luc 12:20, clone2 da
nhan thong bao). Tu gio khong giao viec gi cho clone2 nua, cho toi khi
limit reset.

Dinh chinh mot thong tin trong brief giao viec: brief noi commit cuoi
cua clone2 la watchdog log 12:09 (f07da6b). Tren main, clone2 con commit
sau do: dfea01b luc 12:28, 6d26abe luc 12:29 (watchdog log), 93e8f48 luc
12:31, c58037e luc 12:32, 00ce862 luc 12:35, b4e08ed luc 12:39
(watchdog log), 32dd8f7 luc 12:49 (watchdog log), b72ec65 luc 12:50
(fix pass 2: sua runbook, workflow doc, design doc), 6d596ea luc 12:55
(fix pass 2: bao cao va closeout). Commit cuoi cung cua clone2 tren
main tinh toi 13:00 ngay 22/11 la 6d596ea, 12:55, mot commit doc.
Commit cong viec batch 12 cuoi cung cua clone2 tren code van la
00ce862, 12:35; b72ec65 va 6d596ea chi sua doc, khong doi code.

## 1. Task 1: dieu tra lech so discover 1974/1/5/17 so voi 0/4

Giao viec: batch 11 task 3 cua clone2 bao discover 1974 test, 1 failure,
5 errors, 17 skipped o commit 65a2df6, trong khi step-1 close-out do
o 36364b1 la 0 failure, 4 errors. Tim ra 1 failure do la test nao va
error thu 5 la gi, chay lai o tip hien tai, neu la loi that thi sua.

### Ket qua

1 failure va error thu 5 la cap test tc02 tesseract trong
tests/test_tc02_controller.py, lop Tc02MenuBarTests:

- Failure: test_typed_text_check_fails_when_fragment_is_absent.
- Error thu 5: test_typed_text_check_passes_when_fragment_is_visible.

Nguyen nhan: ca hai test chi mock subprocess.run ma quen mock
shutil.which('tesseract') dung truoc no trong scripts/tc02_controller.py.
Tren may khong co tesseract, cua gate kich hoat truoc khi code mock
duoc chay toi, nen test passes thi error, test fails thi fail assert.
Loi that, khong phai flake: chay rieng 3 lan deu FAILED (failures=1,
errors=1), theo bao cao clone2. Bang chung quyet dinh: code giong het nhau giua hai tip
(git diff 36364b1 65a2df6 tren hai file tren la rong, ca cay chi khac
mot file log), va thi nghiem stub tesseract tren PATH lam ca hai test
pass, theo bao cao clone2. Suy luan co ly nhat, chua xac minh: may cua
step-1 close-out co tesseract tren PATH, may nay thi khong.

### Chay lai va sua

- Chay lai o tip todolist-push 3724f52 (fetched 10:52, khong phai tip
  hien tai luc viet, luc do tip la efbb666; tip todolist-push luc
  viet vong 2 la 030c227, 12:53 ngay 22/11, fetched 13:00), theo bao
  cao clone2: Ran
  2024 tests, 1 failure, 5 errors, skipped 17. So test tang 1974 len
  2024 la do co them dung 50 test method giua hai tip, khong phai do
  runner khac.
- Sua test-only, khong doi production code: ca hai test gio mock them
  shutil.which bang helper _which_with_tesseract (tra ve duong dan
  chi khi ten la 'tesseract', con lai uy thac cho ham that), them mot
  test moi test_typed_text_check_escalates_when_tesseract_is_absent
  bao phu truc tiep cua gate.
- Sau sua, full discover o tip 3724f52: Ran 2025 tests, 0 failures,
  4 errors, skipped 17, trong 176.354 giay (thoi gian chay theo bao
  cao clone2; so 2025/0/4/17 co trong message commit 4dd05b0). 4 errors con lai la cac
  loi moi truong co san (a11y skeleton import, cursor_file g++ khong
  nhan -std=c++26, perf_evidence x2 thieu file json), khong thuoc
  pham vi task nay.

### Council, redteam, fix pass

Bao cao 067745d. Council 1 ISSUES, council 2 ISSUES, council 3 ISSUES,
redteam ISSUES (chi minor, 4 finding), tat ca theo bao cao clone2.
Tat ca sua da ap dung, tru 3
cho da kiem tra va BAC BO co bang chung (ve commit 58704a2, ve so dong
838/864). Thay doi test o commit c7bc697 va 06a7b08: c7bc697 chi them
6 dong mock don gian, 06a7b08 them 29 dong, gom helper
_which_with_tesseract va test gate moi. Fix pass o commit 4dd05b0,
message ghi 2025/0/4/17. Merge 9178403.

Kiem chung lai tren dia: helper _which_with_tesseract co o dong 632,
hai cho mock them o dong 663-666 va 680-683, test gate moi o dong 688
trong tests/test_tc02_controller.py. File bao cao
docs/clone2-batch12-discover-discrepancy-20261122.md dai 337 dong.

Lu y thanh that trong bao cao: redteam chay lai doc lap duoi tai nang
cho 2 failure o test_cursor_session (deadline wait_for 8 giay), khong
lien quan tc02, theo bao cao clone2. So 0 failure la ket qua do duoc cua cac lan chay trong
bao cao, khong phai bao dam duoi tai.

### Viec con lai cua task 1

Fix chi co tren main. Port sang todolist-push la quyet dinh cua dieu
phoi. May cua close-out van CHUA XAC MINH (khong ghi hostname, khong
ghi which tesseract). 4 errors moi truong con lai van mo.

## 2. Task 2: dong not 5 gap live-run readiness, chuan bi rung 2

Giao viec: closeout batch 11 task 2 de lai 2 closed, 3 partial, 5 open,
2 standing. Dong not 5 gap open toi muc lam duoc ma khong can gui tin
live. Chuan bi quy trinh chay rung 2 (live 0-vision tren chat clone
that o ws2) voi option A fallback. Gap nao bat buoc phai gui tin live
moi dong duoc thi ghi ro, khong tu gui tin live.

### Ket qua build (truoc fix pass)

- Script: commit f49851f. Build xong 6 tinh nang cua gap 9: textNew
  trong V12 gate (chi pass khi dung mot bubble moi xuat hien sau
  gate_baseline truoc Enter), pre-send reservation (ghi "sending"
  truoc Enter, doi chieu thanh "sent" hoac "failed-unverified" sau
  gate), V11 MutationObserver flag (dem mutation record theo thread),
  D3 ref stability (kiem tra lai ref truoc khi nhap, fail nhanh
  ref-stale), frames census, strict input name, them cross-window
  check (ham cross_window_check o dong 787). Run registry (run_id
  dung lai trong workdir moi bi REFUSED truoc khi mo browser) khong
  thuoc build nay, ma la them moi o fix pass 1, commit c1b623b.
- Runbook: commit e704d44, them section 14 quy trinh rung 2 day du.
- Workflow doc: commit 8eeafbe.
- Bao cao va closeout dated note: commit 981a0b1, verdict van NOT READY,
  so dem luc do 3 closed, 4 partial, 3 open, 2 standing.

### Fix pass 1

Council 1 ISSUES (1 critical, 1 major, 1 minor, 2 note), council 2
ISSUES (minor only, 5 finding), redteam BROKEN (13 finding F1-F13,
3 HIGH), redteam 4/4 ISSUES (9 sua), tat ca theo bao cao clone2. Sua o commit c1b623b (script) va
45315d5 (driver fix pass 11/11, them fixture double-append va CE
no-send). Sua doc o commit b892918 (runbook, workflow doc, design doc)
va 6ab0c04 (bao cao va closeout, so dem cuoi 3/5/2/2).

So dem cuoi sau fix pass 1, 3 closed, 5 partial, 2 open, 2 standing:

- Closed (3): AMEND4 item 12 runbook section 9, VISION 2 monitor va
  run log, tinh nang script (gap 9).
- Partial (5): checklist 10 contradictions, 10.3 definition (dry probe
  mo), live-shape procedures, cross-origin frames (census da build,
  check live con no), input name (quy trinh da co gioi hoa, gia tri
  live con no).
- Open (2): gap 7 a11y dry probe (CHUA CHAY, can operator tren laptop
  truoc lan live dau), gap 8 method approval va thread URLs/selectors
  (can dieu phoi, decision packet 10 muc o section 3 cua bao cao).
- Standing (2): live lane free, do live muc 90% (do chinh bang lan
  chay).

Kiem chung lai tren dia: runbook 1928 dong, workflow doc 1121 dong,
design doc 792 dong (ca ba dem lai tu commit 6d596ea, khong phai so
trong message commit), script tests/two_vision_bench.py 1939 dong
(1637 dong o commit c1b623b, dung nhu bao cao ghi; tang len 1939 sau
fix pass 2, dem lai tu commit 00ce862). File bao cao
docs/clone2-batch12-readiness-closeout-20261122.md dai 866 dong sau
commit 6d596ea (569 dong o ban fix pass 1), file closeout dated note
docs/clone2-live-run-readiness-closeout-20261122.md dai 451 dong.

Chay kiem chung bang fixture (khong co lan chay live nao, khong gui
tin live nao), theo bao cao clone2: happy path PASS, stale bubble PASS, no-send FAIL nhu
thiet ke, strict input name FAIL nhu thiet ke, iframe harvest
HARVEST-ONLY, exactly-once driver PASS, fix-pass driver 11/11 PASS
trong 54.0356 giay (so 11/11 va 54.0356 giay co trong message commit
45315d5). Tat ca tren headless Firefox 160.0.1.

### Fix pass 2 (sau bao cao 6ab0c04)

Vong 2 council va redteam chay tren ban fix pass 1, verdict ghi trong
commit message dfea01b: council 1 ISSUES (10), council 2 ISSUES (16),
council 3 redteam BROKEN (15, 4 HIGH), redteam 4/4 ISSUES (11).
Sua o commit dfea01b, them commit 93e8f48 (chay T15 tren shared browser
truoc, quit truoc khi chay CLI tests) va 00ce862 (ghi gate_settle_s
tren moi loi ra cua gate, khong chi duong PASS), merge c58037e.

Noi dung sua chinh trong fix pass 2: harvest mode khong bind run
registry nua; ledger record gan intent (message, URL, thread, bubble
selectors), doi plan thi tu choi retry-blocked-intent-changed; intent
"sent" ma khong thay bubble thi tu choi
retry-blocked-sent-bubble-absent thay vi gui lai; V12 gate cho on
dinh 1.0 giay sau khi dat baseline+1 de bat double append tre;
ledger state machine chat hon ("sent" la terminal, reserve atomic
duoi mot lock, file hong bi tu choi exit 2); driver mo rong len 19
test. Kiem chung lai tren dia: file tests/two_vision_fixpass_driver.py
co dung 19 key ket qua rieng biet (T1-T20 trong docstring, T19 nam
trong T1).

### Cap nhat doc sau fix pass 2 (commit b72ec65 va 6d596ea)

Ghi chu o ban truoc noi sau fix pass 2 khong co commit cap nhat doc
nao la SAI o thoi diem viet vong 2. Hai commit doc da co tren main:

- b72ec65, 12:50: sua 3 doc, 474 dong them, 184 dong xoa. Runbook
  1783 len 1928 dong, workflow doc 1004 len 1121 dong, design doc
  764 len 792 dong (so dong dem lai tu commit, khong phai chi tu
  message). Noi dung: harvest mode khong bind run registry nua,
  intent binding va sent-bubble-absent refusal, 1.0 giay gate
  settle, decision packet len 11 muc (them resume authorization),
  0-vision scoping ghi ro can dieu phoi duyet, sua cac claim ve
  cua so chay fix pass 1 va housekeeping, ghi ket qua chay kiem
  chung fix pass 2 (driver 19/19 PASS, baselines kem thoi gian).
- 6d596ea, 12:55: bao cao va closeout dated note, 436 dong them,
  58 dong xoa. Bao cao 569 len 866 dong, closeout 370 len 451 dong
  (so dong dem lai tu commit). Noi dung: them ket qua chay kiem
  chung fix pass 2 vao section 2 (cua so 12:30-12:40 ngay 22/11,
  driver re-run 05:33-05:36Z, baselines 05:37-05:39Z, driver 19/19
  PASS trong 157.1595 giay, happy/stale/nosend/strict/iframe/once/
  b12t2 kem wall time tung case), them section 8 phu luc vong 2
  (council 1 ISSUES 10 finding, council 2 ISSUES 16, council 3
  redteam BROKEN 15 voi 4 HIGH, redteam 4/4 ISSUES 11), sua
  decision packet len 11 muc, sua section 0: so dem 3/5/2/2 chi
  dung tu fix pass 2 (ban truoc ghi sai la tu fix pass 1), sua
  wording F4 tu "recorded causal ties" thanh "recorded
  evidence", tiet lo lan chay fp-iframe-strict dau tien that
  (TypeError log() got multiple values for argument 'name',
  wall 5.5436 giay) va viec cac lan chay fix pass 1 kiem chung
  cay working tree truoc commit chu khong phai commit, xoa cac
  claim khong co bang chung (profile bi xoa, /tmp 5 phan tram
  va 52 phan tram, khong con Firefox chay o fix pass 1) va ghi
  lai dung: profile duoc giu, /tmp o fix pass 2 la 90 phan tram
  (55M free, do bang df), khong con Firefox (0 marionette
  match, 0 listener tren 2828/9223).

Ket qua sau 6d596ea: so dem KHONG DOI, van 3 closed, 5 partial,
2 open, 2 standing (3/5/2/2), verdict van NOT READY. Chua co
council vong 3 nao chay cho cac thay doi cua fix pass 2 (het limit,
quyet dinh cua dieu phoi 01089dd); bao cao ghi ro day la muc mo
cho dieu phoi.

Luu y ve bang chung chay: ket qua chay fix pass 2 gio DA DUOC GHI
VAO BAO CAO (so lieu tren, kem wall time), nhung file log tho
van khong co trong repo. Bao cao ghi log nam o
~/workspace/tools/batch12-t2-fixpass2/ tren may cua clone2. Tu
repo nay chi kiem chung duoc so lieu trong doc va commit message,
khong kiem chung duoc file log goc.

### NOT READY nghia la gi

Khong co lan chay live nao duoc phep cho toi khi dieu phoi cung cap
decision packet 10 muc (method approval, live shape option B hay A,
thread URLs, thread selector va bubble selector theo tung thread, voi
luu y selector mac dinh co dang fixture va live plan bat buoc phai
override, input_name, v12_gate_s, xac nhan --confirm-live, run_id
owner va gia tri, duong dan binary option A, debug port moi browser,
xac nhan live lane free) va operator dong gap 6 va gap 7 o thoi diem
chay bang harvest-first DOM read va a11y dry probe tren laptop.
Fixture proof khong phai live proof. Rung 2 acceptance bat buoc chay
tren chat clone that, khong phai fixture.

## 3. Task 3: luat dat ten endpoint (P3 port-split follow-up)

Giao viec: vu P3 da ro, 127.0.0.1:9223 la Chromium cua clone2, Brave
khi debug o [::1]:9223, hai cai 9223 la hai trinh duyet khac nhau.
Viet luat dat ten endpoint theo tung trinh duyet, lam mot guard test
phai FAIL neu harness resolve endpoint mo ho. Doc harness S2 hien tai
tren todolist-push de xem da fix chua. Deliverable la test va tai lieu
tren main, san sang de port; viec port de dieu phoi quyet.

### Ket qua

Commit e248a7a: luat, resolver scripts/endpoint_names.py, guard test
tests/test_endpoint_naming_guard.py, 29/29 OK. Fix pass commit
9993e25: sua theo council va redteam, 35/35 OK.

Luat: moi endpoint phai neu ro browser (brave hoac chromium), host la
IP literal 127.0.0.1 hoac ::1 (cam localhost), port luon ghi ro (cam
bo trong), owner la chat hoac muc dich (clone1 cho Brave, clone2 cho
Chromium). Dang chuan: Brave http://[::1]:9223, Chromium
http://127.0.0.1:9223. Endpoint nao thieu truong nao cung bi tu choi
bang EndpointAmbiguityError, khong doan mo.

Co so bang chung, theo bao cao clone2: /etc/hosts map localhost sang ca hai family;
getaddrinfo('localhost', 9223) tra ve ca ::1 va 127.0.0.1; thi nghiem
live cho thay ca Python urllib va Node fetch deu fallback sang family
con lai khi family dau tat, nen localhost:9223 nghia la "browser nao
dang chay", khong phai mot browser cu the. S2 flip runs 1-5 cung cu
the hoa su tach biet: brave tren [::1]:9223 outcome sent, chromium
tren 127.0.0.1:9223 outcome failed-unverified (CDP timeout khoang
5000 ms o ca 5 run).

Kiem chung lai tren dia: tests/test_endpoint_naming_guard.py co dung
35 test method (grep dem duoc 35). File bao cao
docs/clone2-endpoint-naming-rule-20261122.md dai 354 dong.

### Council, redteam, fix pass

Fix pass 11:05-11:20 ngay 22/11, council 1/2/3 ISSUES cong redteam
BROKEN, tat ca sua da ap dung va kiem chung lai, theo bao cao clone2.
Mot sua cua council 1 da kiem tra va BAC BO, theo bao cao clone2
(dong save previous_endpoint o dong 3081, nam trong range trich dan
3081-3092; trich dan nay dung o trang thai cu cua todolist-push, vi
du commit d2da482, tren main scripts/cu.py chi dai 2633 dong va khong
co chuoi previous_endpoint, tu commit 108fd45 dong save da doi sang
3136, can xac minh lai khi port). Failing-first, theo bao cao clone2:
chay guard test voi behavior cu thi 31 test, FAILED (failures=25),
chung minh guard co tac dung voi module moi.

### Gioi han thanh that

Guard test chi co tac dung voi module moi scripts/endpoint_names.py,
module nay chua duoc production goi. Cac duong production (cu.py,
cdp.mjs, warm_browser.py, chromium_cli.py, session_remote.py) van
chap nhan localhost va port mac dinh nhu cu. Khong co automated
browser-identity check nao (doc /json/version roi so sanh truoc khi
gui). V12, P9, seed helpers la file /tmp tren laptop, khong co trong
repo, khong kiem chung duoc tu day. Port sang todolist-push la quyet
dinh cua dieu phoi, chua port trong batch nay.

## 4. Bang commit tong hop

Task 1: 067745d (bao cao), c7bc697 (sua test, 6 dong), 06a7b08 (sua
test, 29 dong, helper va test gate moi), 4dd05b0 (fix pass,
2025/0/4/17), 9178403 (merge fix pass).

Task 2: f49851f (script), e704d44 (runbook rung 2, 3/4/3/2), 8eeafbe
(workflow doc), 981a0b1 (bao cao, 3/4/3/2), b892918 (fix pass doc),
6ab0c04 (fix pass bao cao, 3/5/2/2), c1b623b (script fix pass),
45315d5 (driver 11/11), dfea01b (fix pass 2), 93e8f48 (fix pass 2
driver), c58037e (merge), 00ce862 (fix pass 2 gate_settle_s, sau merge),
b72ec65 (fix pass 2 doc: runbook 1928, workflow 1121, design 792),
6d596ea (fix pass 2 bao cao 866 dong va closeout 451 dong, so dem
khong doi 3/5/2/2, verdict van NOT READY).

Task 3: e248a7a (luat va guard test, 29/29), 9993e25 (fix pass,
35/35).

Giao va nhan: 0521d6c (giao batch 12, 10:44), e8ba70c (clone2 nhan,
10:48), 4be15a7 (dieu phoi, log COORD-CLICK-5, xac nhan clone2 het
limit va giao close-out cho clone1, khong phai ket qua cua clone2),
db0ce6b (clone2 nhan thong bao het limit, 12:20), f796df6
(watchdog 12:21, het limit toi 02:38 25/11), 6d26abe (watchdog 12:29),
b4e08ed (watchdog 12:39), 32dd8f7 (watchdog 12:49), a47a15b
(watchdog 12:38, batch 11 task 4 da giao). Luu y: trong luc viet vong
2 nay, main tien them commit e623663 (watchdog 12:59, 12:59); commit
nay nam ngoai pham vi vong 2, chua gap vao ban nay.

## 5. Viec con lai, khong thuoc clone2 nua

- Clone2 het limit toi 02:38 sang thu 4 ngay 25/11. Khong giao viec
  gi cho clone2 cho toi luc do.
- Task 2 fix pass 2 xong tren code va doc da cap nhat o b72ec65 va
  6d596ea (so dem khong doi 3/5/2/2, verdict van NOT READY). Con
  thieu: chua co council vong 3 nao chay cho cac thay doi cua fix
  pass 2, bao cao 6d596ea ghi ro la muc mo cho dieu phoi; file log
  tho cua cac lan chay fix pass 2 nam tren may cua clone2
  (~/workspace/tools/batch12-t2-fixpass2/), khong co trong repo,
  nen tu repo chi kiem chung duoc so lieu trong doc, khong kiem
  chung duoc log goc.
- Porting sang todolist-push (fix test tc02 cua task 1, resolver va
  guard test cua task 3) la quyet dinh cua dieu phoi, chua lam.
- Live run (rung 2 hoac 2-vision) can decision packet 10 muc cua dieu
  phoi va gap 6, gap 7 dong o thoi diem chay tren laptop. Chua co
  lich chay nao duoc xep trong batch 12.
