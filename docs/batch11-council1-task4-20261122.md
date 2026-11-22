# Council 1, batch 11 task 4: kiem chung so lieu tong ket batch 12 cua clone2

Ngay: 2026-11-22. Council 1 (kiem so), doc kiem tra la
docs/batch11-task4-batch12-closeout-20261122.md, 280 dong, ban nhap
chua commit. Nhiem vu: kiem chung MOI so lieu va commit hash trong
ban tong ket, truc tiep tu repo bang git log, git show, dem tren dia,
va chay lai hai bo test nho. Khong sua ban nhap, khong commit, khong
push.

## Ket luan: STANDS WITH CORRECTIONS

Ban tong ket dung o hau het so lieu. Co 3 cho can sua, liet ke o muc 1.
Khong co so lieu nao bi bop meo, khong co commit nao khong ton tai,
khong co so dem test nao sai. Hai cho sua la ve thoi diem va quy tac
thuoc ve, mot cho la so dong da loi thoi sau mot commit moi. Sau khi
sua 3 cho nay, ban tong ket dung de dong batch 12.

## 1. Danh sach sua (3 muc)

### Sua 1. Commit cuoi cua clone2 khong phai 00ce862 luc 12:35

Ban tong ket viet: "Commit cuoi cung cua clone2 tren main tinh toi
luc viet tong ket nay la 00ce862, 12:35 ngay 22/11. Sau 12:35 khong
con commit nao cua clone2 nua."

SAI o thoi diem kiem chung. Sau khi chay git fetch origin main,
dau main la b4e08ed, tac gia clone2, 05:39:50 UTC, tuc 12:39:50 +07,
message "clone2 watchdog 12:38: no stall, clone1 batch 11 done, task
4 dispatched". Day la mot commit watchdog log, khong phai commit
cong viec batch 12, nhung no la commit cua clone2 va no den sau
00ce862.

Sua thanh: commit cuoi cung cua clone2 tren main la b4e08ed, 12:39
ngay 22/11, mot watchdog log. Commit cong viec batch 12 cuoi cung
cua clone2 van la 00ce862, 12:35. Phan dinh chinh ve brief van dung
huong: brief noi commit cuoi la f07da6b luc 12:09, thuc te clone2 con
dfea01b 12:28, 93e8f48 12:31, c58037e 12:32, 00ce862 12:35, roi them
6d26abe 12:29 va b4e08ed 12:39 (hai watchdog log). Tat ca cac moc gio
nay deu khop voi git log, chi thieu b4e08ed.

Bang chung: git log origin/main --format='%h %ci %an %s'
--since='2026-11-22 05:35:16 +0000' liet ke b4e08ed o dau, tac gia
clone2. Bang commit tong hop o muc 4 cua ban tong ket cung thieu
b4e08ed, can them mot dong.

### Sua 2. Run registry thuoc fix pass 1, khong thuoc build f49851f

Ban tong ket, muc 2, phan "Ket qua build (truoc fix pass)", viet
script o commit f49851f da build xong "them cross-window check va
run registry (run_id dung lai trong workdir moi bi REFUSED truoc
khi mo browser)".

SAI ve quy tac. Kiem tra truc tiep: git grep -i registry f49851f
-- 'tests/*' chi tra ve cac ket qua khong lien quan (pyatspi
Registry trong tests/atspi_probe.py), khong co run registry nao
trong tests/two_vision_bench.py o commit f49851f. Bao cao closeout
cua chinh task 2, muc 6, cung ghi ro: f49851f gom textNew,
reservation, V11, D3, frames census, strict input name; con
"registry" nam trong danh sach thay doi cua c1b623b, cung voi
--visions-used, --allow-resume, disk guard. Hanh vi REFUSED la
finding F3 cua redteam, sua o fix pass 1, commit c1b623b.

Sua thanh: f49851f build xong textNew, reservation, V11, D3, frames
census, strict input name, va cross-window check (ham
cross_window_check co o dong 787 cua file o commit f49851f). Run
registry (shared run registry, run_id dung lai bi REFUSED) la them
moi o fix pass 1, commit c1b623b. Cung can sua cau "Build xong 4
tinh nang cua gap 9": ban tong ket liet ke 6 muc ma bo sot frames
census va strict input name, hai muc nay co trong message cua
f49851f va trong muc 6 cua bao cao closeout.

### Sua 3. So dong 3081 cua dong save previous_endpoint da loi thoi

Ban tong ket, muc 3, viet dong save previous_endpoint o dong 3081,
nam trong range trich dan 3081-3092.

DUNG o thoi diem bao cao task 3 viet, SAI o tip todolist-push hien
tai. Kiem tra truc tiep: git show 350934a:scripts/cu.py cho
previous_endpoint=BROWSER_ENDPOINT o dung dong 3081. Day la commit
cu.py dang co hieu luc trong cua fix pass (11:05-11:20). Nhung sau
do commit 292753f, 04:56:34 UTC tuc 11:56:34 +07, da viet lai cu.py,
nen tren tip todolist-push hien tai dong save o dong 3136 (git show
origin/todolist-push:scripts/cu.py, grep -n). So dong 3081 trong
ban tong ket can ghi chu: dung o commit 350934a, da doi thanh 3136
sau commit 292753f. Day la loi thoi do file doi, khong phai so lieu
bi bop meo.

## 2. Task 1: tat ca so lieu CONFIRMED

- 1974 test, 1 failure, 5 errors, 17 skipped o 65a2df6: CONFIRMED.
  Bao cao docs/clone2-batch12-discover-discrepancy-20261122.md,
  dong 40-41: "measured at tip 65a2df6: Ran 1974 tests in 180.748 s,
  FAILED (failures=1, errors=5, skipped=17)". Commit 65a2df6 ton
  tai, 01:49:16 UTC.
- 0 failure, 4 errors o 36364b1 (step-1 close-out): CONFIRMED.
  Bao cao, muc 3, dong 127-134: "0 failures, 4 errors at 36364b1",
  "248.397 s, FAILED (errors=4, skipped=17), 0 failures". Commit
  36364b1 ton tai, 01:39:18 UTC.
- Chay lai o tip todolist-push 3724f52: Ran 2024, 1 failure,
  5 errors, skipped 17: CONFIRMED. Bao cao dong 42-43: "Ran 2024
  tests in 176.606 s, FAILED (failures=1, errors=5, skipped=17)".
  Commit 3724f52 ton tai, 03:51:05 UTC, tren todolist-push.
- Tang 1974 len 2024 la dung 50 test method them: CONFIRMED,
  dem doc lap. Lenh git diff -U0 65a2df6 3724f52 -- 'tests/test_*.py'
  roi dem dong them dang def test_ cho dung 50.
- Code giong het nhau giua hai tip, ca cay chi khac mot file log:
  CONFIRMED. git diff 36364b1 65a2df6 -- tests/test_tc02_controller.py
  scripts/tc02_controller.py cho 0 dong. git diff --stat
  36364b1 65a2df6 chi co improvements/worker-click4-coord-log.md,
  90 insertions.
- Chay rieng 3 lan deu FAILED (failures=1, errors=1): CONFIRMED.
  Bao cao dong 110: "gives FAILED (failures=1, errors=1) all 3
  times."
- Sau sua, full discover o tip 3724f52: Ran 2025, 0 failure,
  4 errors, skipped 17, trong 176.354 giay: CONFIRMED. Bao cao
  dong 227: "Ran 2025 tests in 176.354 s, FAILED (errors=4,
  skipped=17), 0 failures". Message commit fix pass 4dd05b0 ghi
  dung "2025/0/4/17". Commit 4dd05b0 ton tai, 04:27:47 UTC.
- Helper _which_with_tesseract o dong 632: CONFIRMED, grep cho
  dong 632. Hai cho mock them o dong 663-666 va 680-683: CONFIRMED,
  grep cho side_effect=_which_with_tesseract o dong 666 va 683,
  khoi with bat dau o dong 663 va 680. Test gate moi o dong 688:
  CONFIRMED, test_typed_text_check_escalates_when_tesseract_is_absent
  o dong 688. Ca ba test tc02 chay lai truc tiep tren may nay:
  Ran 3 tests, OK.
- Council 1 ISSUES, council 2 ISSUES, council 3 ISSUES, redteam
  ISSUES chi minor, 4 finding: CONFIRMED. Bao cao muc 7, dong
  289-291: "Council 1 ISSUES (1 factual, 4 minor), council 2
  ISSUES (3 corrections, 4 minor nits), council 3 ISSUES
  (7 corrections, 6 minor nits), redteam ISSUES (minor only,
  4 findings)."
- Tru 3 cho da kiem tra va BAC BO (ve commit 58704a2, ve so dong
  838/864): CONFIRMED. Bao cao muc 7: "except three that were
  checked and REJECTED with evidence", gom council 1 correction 2
  va council 2 nit 4 (ve 58704a2) va council 3 correction 4 (ve
  dong 838 va 864). Commit 58704a2 ton tai.
- Redteam chay lai doc lap duoi tai nang cho 2 failure o
  test_cursor_session, deadline wait_for 8 giay: CONFIRMED. Bao
  cao dong 32-33 va 254-256: redteam re-run cho 2024/2/4/17, 8 s
  wait_for deadline.
- Bao cao task 1 dai 337 dong: CONFIRMED, wc -l cho 337.
- Commit 067745d (bao cao), c7bc697 (sua test), 9178403 (merge):
  CONFIRMED, ca ba ton tai voi message khop.

## 3. Task 2: tat ca so lieu CONFIRMED

- So dem luc bao cao 981a0b1: 3/4/3/2: CONFIRMED. Message commit
  981a0b1 ghi "3/4/3/2". Ban dau cua bao cao o commit 981a0b1 ghi
  "3 fully closed, 4 partial, 3 open, 2 standing". Commit e704d44
  cung ghi "section 12 recount 3/4/3/2".
- So dem cuoi sau fix pass 1: 3/5/2/2: CONFIRMED. Message commit
  6ab0c04 ghi "counts 3/5/2/2". Ban dau bao cao hien tai ghi "3
  fully closed, 5 partial, 2 open, 2 standing". Message commit
  b892918 cung ghi "counts 3/5/2/2".
- Danh sach Closed (3), Partial (5), Open (2), Standing (2):
  CONFIRMED, khop tung muc voi muc 5 cua bao cao closeout: Closed
  la AMEND4 item 12, VISION 2, script features gap 9; Partial la
  checklist 10 contradictions, 10.3 definition, live-shape
  procedures, cross-origin frames, input name; Open la gap 7 va
  gap 8; Standing la live lane free va do 90%.
- Driver fix pass 11/11 trong 54.0356 giay: CONFIRMED. Message
  commit 45315d5 ghi "Run: 11/11 PASS, wall 54.0356 s". Commit
  45315d5 ton tai.
- Fix pass 1 council va redteam: CONFIRMED. Bao cao muc 7:
  Council 1 ISSUES, 1 critical, 1 major, 1 minor, plus 2 notes;
  Council 2 ISSUES, minor only, 5 findings; Redteam BROKEN,
  13 findings F1-F13, F1 HIGH, F2 HIGH, F3 HIGH (dung 3 HIGH);
  Redteam 4/4 ISSUES, 9 corrections, all applied. Khop tung so
  voi ban tong ket.
- Fix pass 2 vong 2: council 1 ISSUES (10), council 2 ISSUES
  (16), council 3 redteam BROKEN (15, 4 HIGH), redteam 4/4 ISSUES
  (11): CONFIRMED. Message commit dfea01b ghi dung tung so nay.
  Commit dfea01b ton tai, 05:28:51 UTC.
- Driver mo rong len 19 test: CONFIRMED. Message commit dfea01b
  ghi "driver now 19 tests". Dem truc tiep trong file
  tests/two_vision_fixpass_driver.py: docstring liet ke T1-T20,
  dong 58 ghi "T19 (fix pass 2 state machine, unit, inside T1)",
  va results["tests"] co dung 19 key rieng biet (f1_guard_sent,
  f2_zero_send_no_pass, f3_fresh_workdir_refused,
  f5_duplicate_bubble, f6_tag_swap, f7_moved_input,
  f11_identical_messages, c12_thread_missing, f8_placeholder_rename,
  f10_prefixed_foreign, f9_ce_typing_no_mutation,
  r2f4_delayed_double, r2f1_harvest_then_run,
  r2f2_sent_bubble_absent, r2f3_intent_changed,
  r2f5_registry_recorded, r2f15_substring_messages,
  r2f18_outcome_note, r2f20_corrupt_files).
- Commit 93e8f48 (chay T15 tren shared browser truoc, quit truoc
  khi chay CLI tests) va 00ce862 (ghi gate_settle_s tren moi loi
  ra cua gate): CONFIRMED, message khop tung chu. Merge c58037e:
  CONFIRMED.
- V12 gate on dinh 1.0 giay sau khi dat baseline+1: CONFIRMED.
  Message dfea01b: "V12 gate settles 1.0 s after first reaching
  baseline+1".
- Runbook 1783 dong, workflow doc 1004 dong, script 1939 dong
  hien tai va 1637 dong o commit c1b623b: CONFIRMED. wc -l cho
  docs/two-vision-live-runbook-20261122.md 1783,
  docs/two-vision-benchmark-workflow-20261122.md 1004,
  tests/two_vision_bench.py 1939; git show
  c1b623b:tests/two_vision_bench.py cho 1637.
- Bao cao closeout dai 569 dong: CONFIRMED, wc -l cho 569.
- Quy trinh rung 2 o section 14 cua runbook: CONFIRMED. Runbook
  co "## 14. Rung 2: live 0-vision benchmark" o dong 1356.
- Decision packet 10 muc: CONFIRMED. Bao cao dong 400-401:
  "decision packet in section 3, now 10 items".
- Sau fix pass 2 khong co commit cap nhat doc nao tren main:
  CONFIRMED. git log cua ca hai file bao cao va closeout dated
  note deu dung o 6ab0c04. Vi vay nhan dinh "so dem 3/5/2/2 van
  dung cho fix pass 1; chua co so dem moi sau fix pass 2" la dung
  voi trang thai doc hien tai.
- Commit f49851f, e704d44, 8eeafbe, 981a0b1, b892918, 6ab0c04,
  c1b623b: CONFIRMED, tat ca ton tai voi message khop.

## 4. Task 3: tat ca so lieu CONFIRMED

- Commit e248a7a, 29/29 OK: CONFIRMED. Message ghi "29/29 OK".
  Dem truc tiep: git show e248a7a:tests/test_endpoint_naming_guard.py
  cho dung 29 test method. Commit gom dung 3 file: bao cao,
  scripts/endpoint_names.py, tests/test_endpoint_naming_guard.py.
- Fix pass commit 9993e25, 35/35 OK: CONFIRMED. Message ghi
  "35/35 OK". Dem tren dia: grep -c 'def test_' trong
  tests/test_endpoint_naming_guard.py cho 35. Chay lai truc tiep
  tren may nay: Ran 35 tests in 0.007s, OK.
- Failing-first: 31 test, FAILED (failures=25): CONFIRMED. Bao
  cao dong 314-318: "Ran 31 tests, FAILED (failures=25)".
- Fix pass 11:05-11:20, council 1/2/3 ISSUES cong redteam BROKEN:
  CONFIRMED. Bao cao dong 4: "2026-11-22 11:05-11:20 +07: council
  1/2/3 ISSUES plus redteam BROKEN". Commit 9993e25 luc 11:11 +07,
  nam trong khoang.
- Mot sua cua council 1 da BAC BO (dong save previous_endpoint):
  CONFIRMED ve noi dung, voi luu y loi thoi o Sua 3 tren. Bao cao
  dong 331-336 ghi ro viec kiem tra va ket luan dong save o 3081,
  trong range 3081-3092.
- /etc/hosts map localhost sang ca hai family, getaddrinfo tra ve
  ca ::1 va 127.0.0.1: CONFIRMED. Bao cao dong 70-84 ghi dung ca
  hai dong /etc/hosts va ket qua getaddrinfo do luc 10:54 +07.
- Thi nghiem fallback (Python urllib va Node fetch deu fallback):
  CONFIRMED nhu ghi trong bao cao, muc 3, thi nghiem 11:05 +07.
- S2 flip runs 1-5: brave tren [::1]:9223 outcome sent, chromium
  tren 127.0.0.1:9223 outcome failed-unverified, timeout khoang
  5000 ms o ca 5 run: CONFIRMED. Bao cao dong 119-122: "every run
  records brave on http://[::1]:9223 outcome sent" va "chromium
  failure is a dom_act timeout of about 5000 ms in all five runs
  (5002-5003 ms in the program log, elapsed 5102-5106 ms)".
- Bao cao task 3 dai 354 dong: CONFIRMED, wc -l cho 354.

## 5. Giao nhan va gioi han: CONFIRMED, tru Sua 1

- Giao batch 12 luc 10:44, commit 0521d6c: CONFIRMED, commit luc
  03:44:30 UTC, tuc 10:44:30 +07.
- Clone2 nhan luc 10:48, commit e8ba70c: CONFIRMED theo message
  commit (message ghi "10:48 22/11"). Luu y nho: timestamp cua
  commit la 10:49:46 +07, lech 1 phut 46 giay so voi gio ghi trong
  message, do clone2 viet message truoc roi commit sau. Khong phai
  loi so lieu.
- Clone2 het limit, reset 02:38 sang thu 4 ngay 25/11: CONFIRMED.
  Message commit db0ce6b va f796df6 deu ghi "02:38 25/11". Lenh
  date cho 25/11/2026 la Wednesday, tuc thu 4. Commit db0ce6b luc
  12:20:44 +07, f796df6 luc 12:21:12 +07 (message ghi 12:20, lech
  1 phut 12 giay, cung kieu lech nhu tren).
- Brief giao viec 01089dd luc 12:16: CONFIRMED, commit luc
  05:16:55 UTC, tuc 12:16:55 +07.
- Watchdog 6d26abe luc 12:29 va a47a15b luc 12:38: CONFIRMED,
  timestamp khop.
- Brief noi commit cuoi cua clone2 la f07da6b luc 12:09: dung la
  brief noi vay, va f07da6b ton tai, message ghi 12:09, timestamp
  12:10:49 +07. Phan dinh chinh cua ban tong ket la can thiet,
  chi sai o moc cuoi, xem Sua 1.
- Ban tong ket dai 280 dong: CONFIRMED, wc -l cho 280.

## 6. Phuong phap kiem chung

- git fetch origin main truoc khi ket luan, de moc main moi nhat
  la b4e08ed.
- Doc message day du cua cac commit 4dd05b0, dfea01b, 45315d5,
  c1b623b, b892918, 6ab0c04, e704d44, f49851f, 981a0b1, va kiem tra
  thoi gian UTC doi sang +07 cho moi commit trong muc 4 cua ban
  tong ket.
- Dem doc lap: 50 test method them giua 65a2df6 va 3724f52; 35
  test method trong guard test; 29 test method o commit e248a7a;
  19 key ket qua trong driver fix pass 2; so dong cac file bang
  wc -l.
- Doc truc tiep ba bao cao goc (337, 569, 354 dong) va doi chieu
  tung so dem voi ban tong ket.
- Chay lai truc tiep: guard test 35/35 OK trong 0.007 giay; ba
  test tc02 3/3 OK trong 0.117 giay. Khong chay lai full discover
  (176 giay) hay driver fixture (can Firefox), vi so lieu do da
  co log va message commit khop nhau.
- Khong sua ban nhap, khong commit, khong push. File test-w.txt
  0-byte khong dung toi.
